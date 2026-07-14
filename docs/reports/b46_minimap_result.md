# b46 - Uber Dungeon minimap + area-label fix (ROUND 2, authoritative result)

> Fix for Will's 2026-07-13 report: in the Uber Dungeon (1) the drawn minimap does not line up
> with the level ("black void" under the player), and (2) the top-right area label reads
> "Village of Helos". Branch `feat/b46-minimap`. **This round-2 doc supersedes the round-1 result**
> and reconciles the RCA (`b46_minimap_rca.md`) imprecision the vet flagged. No heavy build;
> all proofs are dry-runs on COPIES of the DEPLOYED DEV map (`SoulvizierClassicDEV/Resources/
> Levels.arc`, MD5 `841c56cd` = what Will plays). Regenerable probes in the session scratchpad
> (`p_label1..6.py`, `p_sd_inject.py`, `p_neighbors.py`, `p_verify.py`).

---

## 0. TL;DR - both symptoms fixed; ONE reported bug, TWO distinct mechanisms

The Uber Dungeon report has two symptoms with **two independent mechanisms** that merely share a
theme ("the relocated SV interior lacked world-map identity"). The RCA framed them as "one root
cause"; that was imprecise. The truth, now proven byte-level:

| symptom | mechanism (structure) | fix | round | confidence |
|---|---|---|---|---|
| **1. minimap "black void"** | the level's **LEVELS-entry teleport-zone `dbr`** was empty -> its minimap TGA is never composited onto a world-map page | assign a `mapIndex`-correct zone `dbr` (its TGA then composites on the continent page at the level's own grid corner) | 1 (retained) + r2 refine | mechanism INFERRED; needs in-game composite check |
| **2. "Village of Helos" label** | the level's **`0x17` region[] GUID** (`59c096c3...`) had **no world-SD (0x18) record**, so the area-name banner never resolves and retains the last region (Helos, the teleport origin) | append the missing SD REGION record for that exact GUID (+ its Text tag) | **2 (this round)** | mechanism **PROVEN on 489/489 levels**; needs only a visual confirm |

Both are additive, map-tooling-only, and respect every b46 LAW (QUESTS 256-window byte-identical;
every `0x0b` navmesh byte-identical; no blob/raster/`0x17` edit). **18/18 verification gates PASS**
(Section 5).

**Residual (honest): neither symptom is in-game-confirmed** - static analysis cannot observe
rendering and this agent (like the vet) is barred from launching TQ. The label mechanism is now
*statically proven* (see Section 2), so its residual is small; the minimap composite still wants
Will's eyes. See Section 6.

---

## 1. Symptom 1 - the minimap (round 1, retained; one r2 refinement)

Mechanism + fix are unchanged from round 1 and the vet RETAINED them as "clean and safe":
the world map composites each level's minimap TGA (`DATA2`/`0x1a`, a bare positionless 24-bit
TGA) onto its **continent page**, selected by the level's teleport-zone `dbr`'s `mapIndex`, at the
level's **own grid corner**. A zoneless level's TGA is never composited -> the map keeps the
teleport-origin page (Helos = Greece) while the player marker sits at the dungeon's real corner,
off the drawn content = "black void". Fix: `apply_zone_dbr_overrides()` assigns each relocated
zoneless interior a `mapIndex`-correct existing zone (14 levels; zero new DB records).

**Evidence the page is per-continent (auto-sizing), so any same-continent zone works:** the 38
base levels sharing `greece/delphi.dbr` composite across grid X[-9399,-3130] Z[-3268,-320] - a
huge span - proving the page auto-sizes to include each member at its own corner (probe
`p_neighbors.py`). `delphi/knossos/sparta/megara` are all `mapIndex 0` (byte-verified from
`database.arz`); `olympus` is `mapIndex 4`.

**Round-2 refinement (vet LOW):** crypt_floor1's zone changed **knossos -> delphi**. The Uber
Dungeon's grid corner `(-2578,-2682)` sits inside Delphi map-space - its physically nearest
already-composited neighbor is the Delphi-underground `entrance03` at **721u** (vs Knossos content
>1100u west). Both are `mapIndex 0`, so identical under the proven per-continent paging, but
`delphi` is the correct nearest-content anchor and is robust to any per-zone paging component.

**Secret Place cluster (vet MEDIUM):** the 11 secret_place levels sit at Z~-5800..-6200, ~2000u
from any composited content **either way** (Greek `megara` to the north, Orient `silkroad` to the
south). That isolation is an inherent property of their SV-original grid position - the **same
pattern every base-game cave uses** (interiors park ~1700u from their surface region) - NOT a
zone-choice artifact, and no `mapIndex-0` zone de-isolates them. They keep `knossos` (Greek
arrival page). Grid-relocating them to sit adjacent to Greek content is out of scope and high-risk
(it would move navmeshes). This is strictly better than the current black-void and cannot crash.

## 2. Symptom 2 - the area label (round 2, the deferred half; now PROVEN)

### 2a. Mechanism (byte-proven; corrects the RCA)

The top-right area-name banner is **NOT** the teleport-zone name and **NOT** an SD-spatial
lookup (the RCA's guess). It is a **region GUID carried in each level's `0x17` section**, in a
`region[]` slot, resolved against the world **SD (0x18) REGION list** to a display tag.

The `0x17` section begins `magic(=1), version, [layer-GUID table], [region-GUID table]` then a
per-cell detail/lighting raster. **Proof of slot semantics** (`p_label6.py`, deployed map): across
**every one of the 489 cleanly-parseable levels**, the `region[]`-slot GUIDs that resolve in SD
are **EXACTLY** the region GUIDs found by an independent whole-`0x17` SD scan (0 mismatches), and
`layer[]`-slot GUIDs are **never** SD regions (0 exceptions). So `region[]` is definitively where
the displayed area name is bound. Cross-checks: `boss_arena.region[0]` = "Olympian Arena"
(`tagNewMZone1`), `startingcave01` = "Natural Cave", `entrance03` = "Parnassus Caves", GoM =
"Duister" - all match what the game shows.

`crypt_floor1`'s `0x17` `region[0]` GUID = `59c096c3efda75824a40d4f6483fb8bf`, which is **absent
from the SD** (probe1: 0 SD-region GUIDs anywhere in its `0x17`). So no name resolves and the
banner retains the last region entered - "Village of Helos", from the Helos plaza where the
traveler stands. This is an **SV-original gap**: SV 0.98i's `crypt_floor1` `0x17` is byte-identical
(same `region[0]` = `59c096c3...`, no SD record either - `p_label5.py`). It became player-visible
only because our mod made the dungeon reachable via the Helos traveler hub.

### 2b. Fix (additive; proven-round-trip; zero `0x17`/raster edit)

`add_sv_region_labels(sv_sd)` (in `tools/svaera_plus_portals.py`) **appends** one SD REGION
record whose `guid` == the level's existing `0x17` `region[0]` GUID, so the banner resolves. No
`0x17`/blob edit is needed - the level already references the GUID; only its SD definition was
missing (exactly analogous to the empty-`dbr` minimap case). `tools/sd_format.py` round-trips the
SD byte-identically, and regions are looked up by **GUID** (not index), so an append leaves every
existing region, every index, the ENV list, and the opaque audio/miniboss **tail** byte-identical
(+111 B; `p_sd_inject.py` proves the exact surgical splice). Donor colors are copied from the
SV-authored "Olympian Arena" region so the minimap-legend tint is dungeon-appropriate.

**Name = "The Obsidian Halls"** (tag `tagSVCRegionObsidianHalls`, added to
`tools/build_text_arc.py` `TEXT_FIX_TAGS`): crypt_floor1's build36 content **is** the Obsidian
Halls treasure roulette (4 wardens + Kravmoloch, "Keeper of the Wheel of the Obsidian Halls"), and
the hub NPC the player clicks is **"Traveler: The Obsidian Halls"** - so the banner matches both
the traveler and the room. (The classic SV name "The Uber Dungeon" is the one-line alternative:
change the label in `SV_REGION_LABELS` + the `TEXT_FIX_TAGS` value.)

**Only crypt_floor1 needs a minted region.** Sweep of the reachable relocated interiors
(`p_label6.py`): `spartacryptlevel2` already resolves to "Ancient Tomb", GoM to "Duister",
`darkforestenter` to "Dark Forest", `rogueencampment` + `tfinale` ("JoLandia") are named; the
secret_place SUB-rooms carry no region and inherit "Dark Forest" from the landing - thematically
correct for a forest cluster, so no per-room label is minted (naming "woodscorner" etc. would be
worse). `coldtombs` is vestigial (no navmesh, not reached) and skipped.

## 3. What changed (implementation)

- `tools/svaera_plus_portals.py`:
  - `add_sv_region_labels(sv_sd)` + `SV_REGION_LABELS` table - appends the SD area-label region.
    Wired in step 3 right after the SV SD is loaded. Idempotent; fails loud on SD schema drift or
    a duplicate display tag.
  - `apply_zone_dbr_overrides` (round 1, retained): crypt_floor1 `dbr` changed knossos -> delphi;
    comments corrected (label mechanism is now solved, not a "follow-up"; secret_place isolation
    explained).
- `tools/build_text_arc.py`: `TEXT_FIX_TAGS['tagSVCRegionObsidianHalls'] = 'The Obsidian Halls'`
  (emitted once to `modstrings.txt`; folded into the mod-authored tag manifest so `validate_tags`
  and `contract_sd_tags` see it present).

**Deploy coupling: Levels + Text ship together** (the map's new SD region references the Text tag;
`contract_sd_tags` fails loud if the map deploys without the Text tag). This is in addition to the
existing Levels+Quests and arz+Text couplings.

## 4. Georeference proof - crypt_floor1 (numeric)

- Grid corner `(-2578, 0, -2682)`, tile dims `(160,160,160)` -> footprint **X[-2578,-2258]
  Z[-2682,-2362]**, which CONTAINS the boat-dialog teleport target `(-2438,-2450)` (the player
  lands on the drawn tile). The 960x960 minimap TGA is present and unchanged; the level is NOT
  grid-shifted (SV-original corner), so the TGA is internally correct.
- Minimap: `dbr` now `greece/delphi.dbr`, `mapIndex 0` -> TGA composites on the Greece page at the
  grid corner (before: empty `dbr` -> never composited = black void).
- Label: `0x17` `region[0]` GUID `59c096c3...` -> new SD region "The Obsidian Halls" ->
  `tagSVCRegionObsidianHalls` -> Text.arc "The Obsidian Halls" (before: GUID absent from SD ->
  banner retained "Village of Helos").

## 5. Verification - 18/18 gates PASS (dry-run on copies; `p_verify.py`)

| gate | result |
|---|---|
| G1 LEVELS `build(parse(x))==x` | PASS (384,499 B byte-identical serializer) |
| G2 dbr diff: exactly 14 entries, ONLY `dbr` field changed | PASS (0 non-dbr field changes on any entry) |
| G2 crypt_floor1 `dbr` -> `greece/delphi.dbr` | PASS |
| G3 SD round-trip byte-identical | PASS (116,299 B, v6) |
| G3 SD region count +1 (293 -> 294); ENV + tail + all prior regions byte-identical | PASS |
| G3 appended region = "The Obsidian Halls" @ GUID `59c096c3...` | PASS |
| G4 QUESTS byte-identical (256-window untouched) | PASS (sha `7ad0f054`, 11,460 B - matches round-1 vet) |
| G5 every level blob (navmesh `0x0b`, `0x17`, ...) untouched | PASS (blob offsets/lengths unchanged; passes never write blobs) |
| G6 crypt georeference (minimap page + label GUID chain) | PASS |
| G7 `contract_sd_tags`: all 295 SD display tags resolve in Text (mod+base) | PASS (0 unresolved; new tag resolves) |
| py_compile both files | PASS |

**Blob-diff summary:** the only changed map sections are **LEVELS** (14 `dbr` strings) and **SD**
(+1 region record). No level blob is written at all - crypt's `0x17` is READ to locate the region
GUID but never modified. QUESTS, GROUPS, BITMAPS, DATA2, and every `0x0b`/`0x17`/`0x05`/`0x06`
level section are byte-identical.

## 6. Confidence + the one remaining step (in-game)

- **Label (symptom 2): HIGH static confidence.** The `region[] -> SD -> tag` mechanism is proven
  on 489/489 levels with zero exceptions, and the fix makes crypt's already-referenced GUID
  resolvable. The only thing static analysis cannot do is render the banner. Residual: small.
- **Minimap (symptom 1): MEDIUM-HIGH.** The compositing mechanism is inferred (well-supported: the
  Helos-hub natural experiment shows every *zoneless* destination is reported-broken and every
  *zoned* one is not; delphi/knossos both `mapIndex 0`). The composite still wants a visual check.
- **Remaining step (not doable by any agent here):** a DEV launch by Will - enter the Uber Dungeon
  via "Traveler: The Obsidian Halls" and confirm (a) the drawn map appears under the player (no
  black void) and (b) the banner reads "The Obsidian Halls", not "Village of Helos". Restart Steam
  first (standing rule). This is the same in-game gate the vet named; it is Will's to run.

Deploy: rebuild the map (`py tools/svaera_plus_portals.py`, canonical + TESTHUB) AND Text.arc
together, then deploy both to `SoulvizierClassicDEV`.
