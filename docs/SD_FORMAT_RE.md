# SD (0x18) Section Format - Reverse Engineering (M13b)

> **Trust level: RECIPE** - durable reverse-engineering reference for the world-map SD
> section. Written for M13b (the deferred SD half of the merge-drop restoration; the GROUPS
> half M13a shipped build31e). Companion parser: **`tools/sd_format.py`** (byte-identical
> round-trip proven on 4 maps). Sibling RE refs: `CROSS_LEVEL_STITCH_RE.md`,
> `QUEST_STATE_INJECT.md`. Last updated 2026-07-10.

TL;DR: the SD section is the world's **environment / zone table** (named regions + their
fog/light colors + display-name text tags + audio & miniboss zone bindings). It is **not
pathfinding**; editing it cannot affect walkability. The format was fully RE'd; a
parser/writer round-trips **byte-identical** on SV 0.98i (v6), our shipped map (v6),
SVAERA base (v7), and vanilla TQAE base (v7). **M13b verdict: NO-GO** for any SD swap - the
merge dropped **zero reachable content**; see section 6.

---

## 1. Where SD lives, how it was extracted

`Levels.arc` -> `world/world01.map` -> section id `0x18`. Section framing is the standard
map-section header used by every section (`tools/merge_levels_binary.py parse_sections`):
`[u32 type][u32 size][size bytes]`. The four SD sections compared:

| Map | file | SD ver | SD size |
|---|---|---|---|
| SV 0.98i (classic) | `upstream/soulvizier_098i/Resources/Levels.arc` | 6 | 116,299 B |
| Our shipped canonical | `work/SoulvizierClassic/Resources/Levels.arc` | 6 | 116,299 B (byte-identical to SV) |
| SVAERA base | `reference_mods/SVAERA_customquest/Resources/Levels.arc` | 7 | 227,893 B |
| Vanilla TQAE base | `<Steam>/.../Titan Quest Anniversary Edition/Resources/Levels.arc` | 7 | 227,893 B (byte-identical to SVAERA) |

Two hard facts fell out immediately: **our SD == SV 0.98i SD** (the merge took SV's SD
verbatim; `svaera_plus_portals.py` step 3 `Using SV SD`), and **SVAERA SD == vanilla TQAE
SD** (SVAERA did not touch it). So the whole M13b question reduces to **SV v6 vs base v7**.

---

## 2. Top-level layout (all little-endian)

```
u32  magic     = 2          # constant; the value 2 is also reused as a per-list "format tag"
u32  version                # 6 = classic TQIT/SV ; 7 = TQAE base / SVAERA
<a POSITION-ORDERED sequence of typed lists, each:>
    u32  listTag            # NOT a reliable schema key (reused - see below)
    u32  count
    count records           # record schema is fixed by LIST POSITION, not by listTag
```

The list sequence, in order, is the same in every base/SV/SVAERA map:

| # | list | v6 listTag | v7 listTag | record schema | v6 count | v7 count |
|---|---|---|---|---|---|---|
| 0 | Environment / fog | 1 | 3 | ENV (sec 3) | 213 | 387 |
| 1 | Region / zone-label | 2 | 2 | REGION (sec 4) | 293 | 538 |
| 2 | Audio zones | 2 | 2 | AUDIO (sec 5) | 203 | 376 |
| 3 | Miniboss zones | 1 | ... | MINIBOSS (sec 5) | 29 | ... |
| .. | further zone-binding lists | | | (region-family) | | |

**`listTag` is reused** (1 = env AND miniboss; 2 = region AND audio), so the tag cannot key
the schema - **list order does**. This is the single most important structural finding: a
naive "parse by tag" desyncs. `tools/sd_format.py` therefore fully decodes only the two
lists M13b needs (ENV[0] + REGION[1]) and preserves everything from list 2 onward as an
opaque **tail** blob (still byte-exact for round-trip; see sec 7).

---

## 3. ENV record (list 0) - environment / fog presets

```
u32   a                 # = 1 in every record (enable/type flag)
u32   nameLen; char name[nameLen]        # e.g. "MarshlandLightandFog", "BloodCave"
u8    guid[16]                            # environment id
u8    block[BLOCK]                        # fog/light colors, fog distances, flags
                                          #   BLOCK = 120 (v6)  |  148 (v7)
--- v7 ONLY (version 7) ---
u32   effectPathLen; char effectPath[]    # weather-effect .dbr, len 0 = none, e.g.
                                          #   records\xpack2\effects\blizzard01.dbr
```

- The `block` is kept opaque by the parser (it is a fixed run of RGBA colors + fog
  scalars + small int flags; decoded far enough to know its length is fixed per version).
- **v6->v7 delta = +28 bytes** of fixed block (120 -> 148) plus the trailing length-prefixed
  weather-effect path field that v6 lacks entirely. The +28 bytes are new v7 env fields
  (extra color/scalar slots); their individual semantics were not needed and not pinned.
- Length proof (v7): `X2_BarrowsFog` = `8 + nameLen(13) + guid(16) + 148 + effectLen(4) +
  effectPath(37)` = **226 B** exactly; clean record `MarshlandLightandFog` = `8+20+16+152` =
  **196 B** (effectPathLen 0 -> the trailing 4 bytes complete the 152-byte payload). The
  387-record env list tiles exactly onto the region-list preamble - proof the formula is
  complete (no record carries a second embedded path).

---

## 4. REGION record (list 1) - zone labels (**the M13b target**)

Identical schema on v6 and v7:

```
u32   a                 # = 1
u32   nameLen; char name[nameLen]        # internal name, e.g. "Village of Helos"
u8    guid[16]                            # world-unique region id
f32   color1[4]                           # RGBA (fog/tint A)
f32   color2[4]                           # RGBA (B)
u32   tagLen; char tag[tagLen]            # display-name TEXT tag, e.g. "tagRegionName01"
                                          #   (resolves in Text.arc; may be empty)
u32   t1                                  # trailer, = 1 in all observed
u32   t2                                  # trailer, = 1 in all observed
```

Fixed overhead = **68 B + nameLen + tagLen**. Proven by exact record-length arithmetic
across consecutive records (e.g. `Village of Helos` nameLen 16, tagLen 15 -> 99 B, lands
exactly on `Helos Farmlands`; `Laconia` nameLen 7 tag 15 -> 90 B, lands on `Laconia
Woods`; etc.), and by the whole 293/538-record list tiling exactly onto the audio-list
preamble. The `tag` values (`tagRegionName01`..`185`, plus SV's own zone tags) are the
on-screen zone-banner labels; the two colors drive the zone tint/fog on the minimap legend.

---

## 5. AUDIO + MINIBOSS records (list 2+) - decoded, kept in the opaque tail

Decoded on paper (not needed for M13b, so `sd_format.py` keeps them verbatim):

- **AUDIO** (`a, nameLen+name, guid[16], color1[4], color2[4]` then a fixed set of
  length-prefixed **.dbr sound-path slots** - music / ambient / event, empty slots = len 0,
  e.g. `Records/Sounds/MusicPak/GreekRandom/GrasslandAltMPakGrk.dbr`). All 203 v6 audio
  records tile cleanly under this schema.
- **MINIBOSS** (`a, name, guid[16]`, then a region-family color/param tail; names like
  `Greece Miniboss - Nessus`, `Orient Miniboss - ...`, `Egypt Miniboss - ...`). These bind
  per-zone miniboss spawn tables.

These are documented for completeness; the parser does not split them (see sec 7 rationale).

---

## 6. M13b go / no-go - what the merge dropped, cost, risk

Diff of **our SD (SV v6)** vs **SVAERA base (v7)**, region list (`sd_format.py --diff`):

**REGION records only in SVAERA base (252) - ALL unreachable DLC/HC content:**

| category | count |
|---|---|
| X4 (Eternal Embers DLC) | 130 |
| X2 (Ragnarok DLC) | 96 |
| X3 (Atlantis DLC) | 23 |
| base/other | 3 (`XS_HCDun{Egypt,Greece,Hades}` = the Hardcore endless-dungeon zones) |

The mod's campaign **ends at Hades (Immortal Throne) for all DLC combos** (standing rule;
DLC integration CANCELLED). Every one of the 252 is in a DLC/HC act the player never enters.

**REGION records only in SV/ours (9) - exactly the restored-SV-area labels the mod NEEDS:**

`BCXcave / BCXpassage / BCXtemple / BCXwalkway` (blood cave zones, tags `tagBCX*`),
`Duister` (`tagMZoneGoM`), `Dark Forest` (`tagSPDarkForest`),
`tagSPRogueEncampment`, `JoLandia` (`tagJoLandia`), `Olympian Arena` (`tagNewMZone1`).

**Shared base-act regions (282 distinct) - byte-identical v6 vs v7:** name, guid, both
colors, and display tag all match on **282/282**. So for every reachable Act 1-4 zone, our
SD already carries the exact base record.

The **env** and **audio/miniboss** lists tell the same story: SV's SD additionally carries
17 SV-only env presets (`BloodCave, Duister, UberDungeonLevel1, RogueEncampment, Sanctuary,
SecretForestLayer, ObsidianTransitionUnderground, MysteriousPassage*, TempleofLove, ...`)
and SV-only audio/miniboss bindings (`Duister`, blood-cave, `UberDungeon`, `Rogue Enc...`) -
all for the restored SV areas. SVAERA's env extras are 195 DLC presets plus ~10 re-authored
**base-act fog** presets (`MarshlandLightandFog, Greece_HelosVistaFog, OT_GreatWallFogNew01-03,
AbydosCrypts1st/2ndFloor, TempleOfHathor1`) that ours lacks - the only reachable delta, and
it is **purely cosmetic fog polish**.

### Verdict: **NO-GO** (the current SV v6 SD is the correct choice)

- A wholesale swap to v7 SD **loses** all 9 SV region labels + 17 SV env presets + SV audio/
  miniboss bindings (the entire reason the restored SV areas have names/fog/music) to **gain**
  only unreachable DLC zones plus ~10 cosmetic base-act fog upgrades.
- The merge dropped **no reachable, functional content**. **No proven defect is
  SD-attributed** (consistent with `BACKLOG.md` B-MERGE-SD-GROUPS-1). The functional half of
  the merge-drop was GROUPS (dead shrines), already fixed by M13a.
- **Only conceivable net-positive**, if ever wanted: a *targeted record-level merge* that
  keeps SV v6 as the base and ports in **just** the ~10 re-authored base-act fog env presets.
  That is a cosmetic nicety, low priority.

### Restoration cost / risk (if a targeted merge is ever pursued)

- **Region records**: trivial and low-risk - `sd_format.py` decodes/rebuilds them fully and
  the schema is identical v6<->v7, so adding/removing a region is a list edit + count bump.
- **Env records**: the blocker. Porting an SV env preset into a v7 SD requires a **v6->v7
  block conversion** (120 -> 148 B): the +28 v7 bytes are new fog/color fields whose exact
  layout/defaults were not pinned. Guessing them risks wrong fog/lighting in the ported zone.
  This is the real "sd_format RE" cost the BACKLOG flagged, and it is **only** worth paying
  for the cosmetic fog-polish upside above - i.e. not now.
- **Version field**: our map ships a **v6** SD on an otherwise-v7 (TQAE) world and the game
  loads it fine (build27+ is live). Bumping to v7 SD is therefore unnecessary and unproven-safe.

---

## 7. Parser design + round-trip proof (`tools/sd_format.py`)

Model: `SDSection = header(magic,version) + envList[EnvRecord] + regionList[RegionRecord] +
tail(bytes)`. Env and region are decoded into objects and **rebuilt from fields**; the tail
(audio + miniboss + any further lists) is preserved verbatim. Rebuilding env+region from
decoded fields (not raw slices) is what *proves* the ENV and REGION schemas: any wrong field
boundary would make the rebuild differ.

Because `listTag` is not a schema key and the audio/miniboss/further lists have their own
variable schemas, decoding them fully would add risk for zero M13b benefit - hence the
opaque tail. `SDSection.parse` assumes the fixed list order `[env][region][...]` that holds
in every base/SV/SVAERA world map.

**Round-trip result (`py tools/sd_format.py --roundtrip <4 maps>`): byte-identical = True on
all four** (SV v6, ours v6, SVAERA v7, vanilla v7). Env/region counts: v6 213/293, v7
387/538; tails 52,762 B (v6) / 97,586 B (v7).

Commands:
```
py tools/sd_format.py --roundtrip <Levels.arc|world01.map> ...   # fidelity check
py tools/sd_format.py --diff <SV_or_ours> <SVAERA_base>          # region-record delta
```
