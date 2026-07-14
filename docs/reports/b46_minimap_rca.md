# b46 - Uber Dungeon minimap + area-label RCA (READ-ONLY)

> Root-cause analysis for Will's 2026-07-13 report: in the **Uber Dungeon** the minimap
> does not line up with the level (he walks in "black void" relative to the drawn map),
> and the top-right area label reads **"Village of Helos"** while he is inside the dungeon.
> Read-only investigation; NO map/DB edits made. Evidence = byte-parse of the deployed DEV
> map (`SoulvizierClassicDEV/Resources/Levels.arc` == `local/Levels_merged_TESTHUB.arc`,
> 688,688,154 B, header-identical to the deployed copy), the base-game `database.arz`,
> `Text_EN.arc`, and the pristine upstream SV 0.98i map. Probes are regenerable (session
> scratchpad `probe1..10_*.py`).

> **⚠️ CORRECTION (b46 round 3, 2026-07-13) - read `b46_minimap_result.md` for the authoritative
> mechanism.** This RCA framed both symptoms as "one root cause (missing map/region identity)" and
> guessed the label was an SD-*spatial* lookup. They are **two distinct mechanisms** sharing only a
> theme: (1) the minimap "black void" = the empty LEVELS-entry teleport-zone `dbr` (this RCA got
> that right); (2) the "Village of Helos" label = crypt_floor1's **`0x17` REGION list being EMPTY**
> so no region name resolves and the banner retains the prior region. The 0x17 header is three GUID
> lists `[ENV][REGION][AUDIO]`; round 2 mistook the AUDIO-list GUID `59c096c3` for a region and
> appended an SD region for it (a **no-op** - the banner reads the REGION list, which is empty).
> Round 3 fixes it correctly: inject a minted region GUID into crypt's **0x17 REGION list** (making
> it structurally identical to the shipped, working startingcave01 dungeon) + the matching SD region
> record. Byte-exact-round-trip 0x17 tooling proven on all 2282 levels; navmesh/QUESTS untouched.

---

## 0. Verdict (TL;DR)

**The brief's grid-shift hypothesis is DISPROVEN.** The Uber Dungeon (`crypt_floor1.lvl`)
is **NOT** grid-shifted - it sits at its SV-original grid corner `(-2578,0,-2682)`, and its
navmesh (`0x0b`), its minimap TGA (`BITMAPS`/`DATA2`), and its grid corner are all mutually
consistent at those coordinates. Nothing about its imagery or registration is "stale from a
shift."

**The real root cause: `crypt_floor1` has no world-map / region IDENTITY.** Its `LEVELS`
(0x01) index entry carries an **empty teleport-map-zone pointer** (`dbr = ''`), and it has
**no SD region** covering its coordinates. Both symptoms follow from that single gap:

- **Misaligned minimap (symptom 1):** with no zone, the level's minimap TGA is never
  composited onto any world-map page, so the in-game map keeps showing the **previous zone**
  (Helos, the teleport origin) while the player marker is drawn at the Uber Dungeon's real
  world coordinates far off that page -> "walks in black void relative to the drawn map."
- **"Village of Helos" label (symptom 2):** with no region covering the dungeon, no
  region-enter event fires, so the top-right label **retains the last region** the player was
  in - the "Village of Helos" region (`tagRegionName01`), where the Helos-hub traveler stands.

This is an **SV-ORIGINAL gap** (identical empty pointer in Soulvizier 0.98i), newly *exposed*
because our mod made the Uber Dungeon reachable via the Helos traveler hub
(`svc_helos_trav_uber.dbr` -> `(-2438,10,-2450)`, tag `tagSVCHelosToUber`). It is **not** a
merge or grid-shift regression.

Scope: the same gap affects **14 of the 16 reachable SV interiors** (see the sweep table in
Section 6). One more (Garden of Merchants) has a *dangling* zone pointer to a record that does
not exist. Only **Boss Arena** has a valid existing zone.

---

## 1. How TQAE derives the minimap and the area name (the mechanism)

Three independent systems, each fed by a different map/DB structure. This is the map-format
knowledge the fix must respect.

### 1a. The drawn minimap terrain = `BITMAPS` (0x19) + `DATA2` (0x1a), positioned by `LEVELS`

- `world01.map` section `BITMAPS` (0x19) is an index **parallel to `LEVELS`** (0x01): entry
  *i* = `(offset, length)` into `DATA2`. Count == level count (2282 in the DEV map).
- `DATA2` (0x1a) is a concatenation of **bare 24-bit uncompressed TGAs** - an 18-byte TGA
  header (`imagetype=2`) then `w*h*3` pixels, **no embedded world coordinates**. Verified:
  `crypt_floor1` = `960x960` (`len=2,764,818 = 18 + 960*960*3`), `StartingCave01` = `640x320`,
  `boss_arena` = `512x512`, all exact. A `(0,0)` bitmap entry = no minimap (e.g. `coldtombs`).
- Because the TGA carries no position, the engine places it from the level's **`LEVELS`
  entry**: `ints_raw[6:9]` grid corner + `ints_raw[0:6]` tile dims (footprint = corner ..
  corner + dims*2). `crypt_floor1`'s corner `(-2578,0,-2682)` matches its navmesh center, so
  the TGA is **not internally misplaced**.
- **Zone paging:** which map *page* a level's TGA composites onto is driven by the level's
  teleport-map zone (Section 1c). A level with **no zone is never composited** onto any page.

`BITMAPS`/`DATA2` are cosmetic (NOT pathfinding), consistent with `MODDING_PLAYBOOK.md`.

### 1b. The area NAME = SD (0x18) REGION list, spatially resolved and retained

- The on-screen top-right label is a **region name** from the SD (0x18) REGION list
  (`tools/sd_format.py`, `docs/SD_FORMAT_RE.md`): each REGION record = `{a, name, guid,
  color1, color2, tag, t1, t2}` where `tag` is the display text tag.
- Will's label **"Village of Helos" = `tagRegionName01`** (a REGION name), **not** the zone
  name (`tagMZone01 = "Helos"`). Proven by resolving both tags in `Text_EN.arc`. So the label
  is region-driven, not zone-driven.
- Region membership is **spatial** (the REGION record itself has no coordinates; base
  dungeons carry no region record in their `0x05` either, yet are named). When the player is
  somewhere no region covers, the label **retains the last region entered**.

### 1c. The world map + fast-travel = teleport-map ZONE = the `LEVELS`-entry `dbr`

- Each `LEVELS` entry has a length-prefixed **`dbr` string = a teleport-map-zone record**
  `records/ingameui/teleportmap/zones/<act>/<zone>.dbr` (template `Zone.tpl`). Fields (e.g.
  `greece/helos.dbr`): `ZoneNameTag` (=`tagMZone01`="Helos"), `mapIndex` (0=Greece / 4=Olympus
  / ...), `ArrowLocationX/Y`, `WindowLocationX/Y`. This is how a level is bound to a world-map
  page + rebirth-fountain travel node, and it is the paging key for 1a.
- **Every standalone base-game area has one** (`StartingCave01`->helos, `SpartaOptCave02`
  ->sparta, Athens/Knossos undergrounds->athens/knossos, orient `Random0*`->silkroad, etc.).
  The **only** base levels with empty `dbr` are **`*Border*` / `*Edge*` / `*Connector*` /
  `*BackGround*` filler tiles** (248 of the 299 empty-`dbr` levels), which legitimately inherit
  the adjacent named area. A standalone destination with an empty `dbr` is an anomaly.

---

## 2. The Uber Dungeon blob (deployed DEV map, idx 2280)

`Levels\World\UberDungeon\crypt_floor1.lvl`, GUID `dbc245c358434e0b...`, `LVL v0x0e`.

| property | value | note |
|---|---|---|
| grid corner (`ints_raw[6:9]`) | `(-2578, 0, -2682)` | **== SV-original** (shift = 0) |
| tile dims (`ints_raw[0:6]`) | `(160,11,160,160,11,160)` | footprint X[-2578,-2258] Z[-2682,-2362] |
| blob sections | `0x05(15901) 0x14(56) 0x06(19733) 0x0b(320324) 0x17(30794)` | real `0x0b` navmesh present (build23) |
| `BITMAPS`/`DATA2` minimap | `off=740132206 len=2764818` | **valid 960x960 TGA present** |
| `LEVELS`-entry zone `dbr` | **`''` (EMPTY)** | THE defect - no world-map zone |
| `0x05` region/zone records | **none** (32 records: lights/scenery/catacomb setdress/proxies/portal_olympianarena2/svc_testhub_return) | no region box, no ZoneMarker |
| SD REGION entry for the dungeon | **none** | SD only has an *audio* zone `"UberDungeon - Floor1"` + env preset `UberDungeonLevel1`; **no region label** |

So the Uber Dungeon has: a real navmesh, a valid minimap TGA, correct SV-original coordinates
- but **no teleport zone and no region name**. Everything needed to draw+name it exists
*except* its identity pointers.

### Why both symptoms follow (mechanism)

The player reaches the dungeon by clicking the Helos-plaza traveler
(`svc_helos_trav_uber.dbr`, `build_quest_files.py:1817`), which `Action_BoatDialog`-teleports
to `(-2438,10,-2450)` inside `crypt_floor1`. At that moment the player is standing in the
**"Village of Helos" region** with the **Helos zone** active.

- **Minimap (symptom 1):** `crypt_floor1` has no zone -> its TGA is not attached to any
  world-map page -> the map UI has no "current zone" for the dungeon and keeps the **Helos
  page** (last valid zone). The player marker is projected at the dungeon's real world coords
  `(-2578..-2258, -2682..-2362)`, which is nowhere near the Helos page content -> the marker
  floats in un-composited black space = "walks in black void relative to the drawn map." The
  TGA itself is fine; it is simply never shown because compositing is organised by zone.
- **Label (symptom 2):** `crypt_floor1` is covered by no region -> no region-enter event ->
  the top-right label **retains "Village of Helos"** (`tagRegionName01`) from the plaza.

Both are **one root cause**: the level has no map/region identity.

---

## 3. Why the grid-shift hypothesis is wrong (disproven)

The brief hypothesised the Uber Dungeon was grid-shifted into unused coords with stale
minimap/region data. Evidence against, all byte-verified:

1. **`crypt_floor1` is NOT in `GRID_SHIFT`** (`svaera_plus_portals.py` only shifts the
   `xbloodcave` cluster + relocated Random09A). `shifted_ints_raw()` returns it unchanged.
2. **Deployed corner == SV-original corner** `(-2578,0,-2682)` (probe10: shift = "same"). The
   2026-07-05 `SV_AREAS_AUDIT.md` already established all 16 SV interiors sit at SV-original,
   XZ-disjoint positions - re-confirmed here.
3. **Its navmesh is anchored to that same corner** (`gen_bc_navmeshes.py` `UBER_DUNGEON`,
   `anchor_key=crypt_floor1`, no `GRID_SHIFT`, Y-align asserted 0), so navmesh, TGA, and grid
   corner all agree. There is no shift-induced offset to be stale about.
4. The minimap TGA is a **bare TGA with no embedded position**, so there is nothing in the
   imagery that could carry a pre-shift coordinate.

The bug is missing identity, not stale geometry.

---

## 4. It is an SV-original gap, not a merge regression

The empty zone `dbr` is **identical in Soulvizier 0.98i** (probe3: SV098i `crypt_floor1
dbr=''`). SV never gave the Uber Dungeon, Sparta Crypt L2, Cold Tombs, or the 11 Secret-Place
levels a teleport zone or a region. SV *did* give Boss Arena the base `olympus.dbr` and
authored a dedicated `olympus_gom.dbr` for Garden of Merchants (see Section 6). The gap only
became player-visible once these areas were made reachable (the Helos traveler hub), i.e. it
is *exposed*, not *introduced*, by our work.

---

## 5. What actually drives what (evidence summary)

| symptom | driver structure | evidence | confidence |
|---|---|---|---|
| minimap not composited / misaligned | `LEVELS`-entry teleport-zone `dbr` (empty) + `BITMAPS`/`DATA2` compositing by zone | empty `dbr`; bare TGA present; base standalone areas all have a zone; only filler tiles are empty | PROVEN data / INFERRED engine-behavior |
| "Village of Helos" label | SD (0x18) REGION spatial coverage (none) -> retained last region | label = `tagRegionName01` (region, not zone `tagMZone01`); no region record in blob or SD for the dungeon | PROVEN data / INFERRED engine-behavior |

"INFERRED engine-behavior" = the retained-zone / retained-region behavior is standard TQ
UI behavior fully consistent with every byte-level fact here, but was not disassembly-proven
in this session (read-only, game not launched).

---

## 6. Sweep of all 16 SV interiors (deployed DEV map)

All at SV-original coords (**zero shift** for every one). "zone" = `LEVELS`-entry `dbr`
state. "minimap" = `BITMAPS` TGA length.

| level | idx | corner | minimap TGA | zone dbr | map/name verdict |
|---|---:|---|---:|---|---|
| **uberdungeon/crypt_floor1** | 2280 | (-2578,0,-2682) | 960x960 | **EMPTY** | **BROKEN (the reported bug)** |
| bossarena/boss_arena | 2279 | (-561,0,-3642) | 512x512 | `olympus/olympus.dbr` (EXISTS) | zone OK (verify page-centering in-game) |
| olympus/gardenofmerchants | 2276 | (1043,0,-4074) | 512x512 | `olympus/olympus_gom.dbr` (**MISSING record**) | **BROKEN - dangling zone pointer** |
| minidungeons/spartacryptlevel2 | 2278 | (-5644,0,-1451) | 320x320 | **EMPTY** | BROKEN (same class) |
| egypt/minidungeons/coldtombs | 2277 | (-4283,-5,3123) | **NONE (0,0)** | **EMPTY** | BROKEN + no TGA at all (vestigial; no navmesh) |
| secret_place/behindthesp | 2235 | (-2199,0,-6182) | present | **EMPTY** | BROKEN (same class) |
| secret_place/darkforestenter | 2236 | (-2420,0,-5820) | present | **EMPTY** | BROKEN |
| secret_place/woodscorner | 2237 | (-2548,0,-5820) | present | **EMPTY** | BROKEN |
| secret_place/secretforest2 | 2238 | (-2548,0,-5948) | present | **EMPTY** | BROKEN |
| secret_place/pillagedvillage | 2239 | (-2676,0,-5948) | present | **EMPTY** | BROKEN |
| secret_place/forestobsidiantransition | 2240 | (-2839,0,-5928) | present | **EMPTY** | BROKEN |
| secret_place/rogueencampment | 2241 | (-3216,0,-5547) | present | **EMPTY** | BROKEN |
| secret_place/rogue encampment forest entrance | 2242 | (-3088,0,-5547) | present | **EMPTY** | BROKEN |
| secret_place/rogueencampmentforestfiller | 2243 | (-3216,2,-5419) | present | **EMPTY** | BROKEN |
| secret_place/tfinale | 2244 | (-3623,0,-5635) | 960x960 | **EMPTY** | BROKEN |
| secret_place/murderbossroom | 2245 | (-3592,0,-5955) | present | **EMPTY** | BROKEN |

**Tally: 14 EMPTY-zone, 1 dangling-zone (GoM), 1 valid-zone (Boss Arena).** Every empty/
dangling one will reproduce the reported symptoms *if reached*. Priority = whichever are wired
into the live Helos traveler hub (the Uber Dungeon is; audit the hub roster for the rest).

The blood-cave cluster and Random09A are **not** affected: they inherit
`orient/easternsilkroad.dbr` from the KEPT AE HiddenValley01 chain (probe3), so they already
have a valid zone.

---

## 7. Fix recipe

The fix gives each reachable zoneless SV interior a real map/region identity. It touches three
coupled artifacts (deploy together): the **map** (`LEVELS` 0x01 `dbr` pointer), the **DB**
(`.arz` zone record), and **Text** (the zone name tag). It does NOT touch `QUESTS` (0x1b),
does NOT touch any `0x0b` navmesh, and is a `LEVELS`-index-only map edit via the proven
parse/serialize path - so it respects the b46 LAWS (QUESTS 256-window parity + navmesh
byte-identity are untouched).

### PRIMARY - restore the minimap (assign a teleport zone)

1. **Create a dedicated zone record** `records/ingameui/teleportmap/zones/greece/uberdungeon.dbr`
   (template `database\Templates\Zone.tpl`) with: a new `ZoneNameTag` (e.g. `tagSVCZoneUber`
   = "The Uber Dungeon"), `mapIndex=0` (Greece page - the dungeon's coords live in Greek map
   space), and an `ArrowLocationX/Y` (cosmetic fast-travel arrow; pick any non-overlapping
   spot - the dungeon has no rebirth fountain so the arrow need not be exact). This mirrors the
   **proven SV precedent**: SV authored a dedicated `olympus_gom.dbr` for Garden of Merchants
   rather than reusing `olympus.dbr`, which indicates the map centers per-zone and each
   isolated area needs its own zone. Add the record in the mod build
   (`tools/apply_svc_patches.py` / the DB pipeline) + the tag in `tools/build_text_arc.py`.
2. **Wire `crypt_floor1`'s `LEVELS` `dbr` to it.** In `tools/svaera_plus_portals.py`, when the
   SV-only `crypt_floor1` entry is appended, set `merged_levels[idx]['dbr']`/`['dbr_raw']` to
   `records/ingameui/teleportmap/zones/greece/uberdungeon.dbr` before `build_level_index()`
   (offsets are recomputed by the builder; string-length change is handled). A small
   `LEVELS`-entry `dbr` override table keyed by level path is the clean shape.
3. **Also fix Garden of Merchants:** create the **missing** `olympus_gom.dbr` (it is dangling)
   so GoM's existing pointer resolves. Same record-creation step.

Cheaper interim (verify in-game first): point `crypt_floor1`'s `dbr` at an existing Greek zone
such as `greece/knossos.dbr` (thematic - the SV entrance was from Knossos `maze03`). This gives
a page + a coarse name with **no new DB/Text records**, but only aligns the map if the world
map composites per continent-page rather than per-zone; the SV `olympus_gom` precedent suggests
a dedicated zone is the safe choice.

### SECONDARY - correct the top-right label (region)

Assigning a zone fixes the **map**; whether it also relabels the top-right depends on whether
TQ falls back to the zone name when no region covers the level (needs an in-game check). If the
label still shows a stale region after the zone fix, the dungeon needs **SD (0x18) region
coverage**. Caveat: the REGION *record* carries no coordinates, so a new region label alone
will not self-place - the region->world-space spatial binding lives elsewhere (an
unRE'd binary structure; the SD tail holds the *audio*-zone spatial data, e.g. the existing
`"UberDungeon - Floor1"` audio zone, but the region-volume format was not reverse-engineered in
this read-only pass). **Open item:** RE the region-volume spatial binding before attempting the
label half, or accept the zone name as the displayed area name if TQ uses it as the fallback.

### Verification (must be in-game; static analysis cannot confirm rendering)

- Enter the Uber Dungeon via the Helos traveler; confirm the drawn map now appears under the
  player (no black-void offset) and the label reads the dungeon name, not "Village of Helos".
- Re-run the map gates: `LEVELS`/`0x0b` byte-identity for all *other* levels, blob-diff shows
  only `crypt_floor1`'s `LEVELS` `dbr` changed, `QUESTS` section untouched.

---

## 8. Evidence index (regenerable, session scratchpad)

- `probe1_levels.py` - `LEVELS`+`BITMAPS` for SV interiors + refs (corners, GUIDs, TGA sizes).
- `probe3_zonedbr.py` - `LEVELS`-entry zone `dbr` across DEV / SV098i / SVAERA (the empty-vs-
  present table; SV-original gap proof).
- `probe4_zonerec.py` / `probe5_minimapzones.py` - `Zone.tpl` fields; no uber/crypt zone
  anywhere; `mini map/zones` are empty stubs.
- `probe6_sweep.py` - full 299 empty-`dbr` sweep (control: empties are border/edge fillers;
  every standalone base dungeon has a zone).
- `probe7_text.py` - `tagMZone01`="Helos" vs `tagRegionName01`="Village of Helos" (label is
  the region, not the zone).
- `probe8_sections_sdtail.py` - blob section lists; base caves also have no `0x05` region
  record; SD tail = audio/miniboss (has `"UberDungeon - Floor1"` audio zone).
- `probe9_fixtemplate.py` - `DATA2` blobs are bare positionless TGAs; `olympus_gom` absent.
- `probe10_finalsweep.py` - the Section 6 table; `olympus.dbr` EXISTS, `olympus_gom.dbr`
  MISSING; every interior shift = 0.
