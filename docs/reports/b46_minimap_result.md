# b46 - Uber Dungeon minimap fix (round 1 implementation + verification)

> Fix for Will's 2026-07-13 report: in the Uber Dungeon the drawn minimap does not line up
> with the level ("black void" under the player), and the top-right area label reads
> "Village of Helos". Branch `feat/b46-minimap`. Implementer round 1. NO heavy build.
> Builds on `docs/reports/b46_minimap_rca.md`; corrects two RCA imprecisions (below).

---

## 0. TL;DR

**Fixed (this round): the minimap "black void" for every reachable relocated SV interior.**
The SV-only interiors reached via the Helos traveler hub carry an **empty (or dangling)
teleport-map-zone pointer** in their `LEVELS`-index `dbr`. The world map composites each
level's minimap TGA (`DATA2`) onto its continent **page** keyed by that zone's `mapIndex`; a
zoneless level's TGA is **never composited**, so the map keeps showing the teleport-ORIGIN page
(Helos = Greece) while the player marker sits at the dungeon's real grid corner off the drawn
content = "black void". The fix assigns each interior a `dbr` pointing at an **existing,
mapIndex-correct** zone, so its TGA composites on the right page at its own grid corner.

**Deferred (round 2): the top-right area LABEL** ("Village of Helos"). It is driven by a
**region GUID embedded in the level's `0x17` section** (an un-RE'd, format-variant section) -
NOT by the zone name. crypt_floor1 has no such region ref. Injecting one is not doable via the
proven round-trip tooling, so per the b46 crash-safety LAW it is scoped as a follow-up with a
precise mechanism spec (Section 5), rather than a blind edit.

Change is **one map-tooling file** (`tools/svaera_plus_portals.py`), **map-side only**: a
`LEVELS`-entry `dbr` override table + a `apply_zone_dbr_overrides()` pass before
`build_level_index`. No DB/Text/quest/navmesh/`0x17` edits.

---

## 1. Mechanism (evidence-verified; two RCA corrections)

The world map is per-continent **pages** selected by a zone's `mapIndex` (base DB: Greece=0,
Egypt=1, Olympus=4, Orient=7). A level's minimap TGA composites onto its zone's page **at the
level's own grid corner** (`ints_raw[6],[8]`). Proven: 38 base levels share `greece/delphi.dbr`
yet their TGAs span grid X[-9399,-3130] Z[-3268,-320] -> the zone assigns the *page*, the grid
corner assigns the *position*, and the page auto-sizes to include its members. A level with
**no zone** is never added to any page -> its TGA is not composited -> "black void". Helos is
itself `mapIndex 0`, so the player teleporting in from Helos is already viewing the Greece page;
assigning the dungeon any Greece (`mapIndex 0`) zone composites its TGA onto that same page.

Two RCA claims were checked and **corrected**:
- **"crypt_floor1's TGA is present but never composited"** - the RCA's read of a 960x960 TGA was
  right (960x960, type 2, 2,764,818 B at abs offset 740132206, byte-identical to SV 0.98i). My
  first probe misread a DATA2-relative offset; bitmap offsets are **absolute** file offsets. So
  the TGA is valid; only its *page membership* (zone) is missing. Fix stands.
- **"empty `dbr` = the defect; only Border/Edge filler tiles are empty in base"** - not quite:
  base interiors `Crypt01.lvl` (idx92) and `MiscCaveA.lvl` (idx104) also ship with empty `dbr`.
  They get away with it because they are entered by a walk-in `GridEntrance` from a zoned parent;
  the Uber Dungeon is entered by a **boat-dialog teleport** and is otherwise isolated, so it has
  no zone to inherit. The fix (give it an explicit zone) is correct either way.

**The label is region-driven, not zone-driven** (RCA got this right, mechanism now located):
each named base dungeon embeds its region GUID in its `0x17` section (e.g. Delphi Underground
`Entrance03` -> "Parnassus Caves" `tagRegionName37`; `StartingCave01` -> "Natural Cave"
`tagPOI01`). crypt_floor1's `0x17` has **no** region GUID -> the label retains the last region
("Village of Helos"). So the zone fix does not, by itself, relabel the top-right (Section 5).

---

## 2. What changed (implementation)

`tools/svaera_plus_portals.py`:
- `LEVEL_ZONE_DBR_OVERRIDES` - `{level-path -> existing zone dbr}` for 14 reachable interiors.
- `apply_zone_dbr_overrides(merged_levels)` - sets `dbr`/`dbr_raw` on the matched entries; fails
  loud if any target path is missing (fname drift guard). Called once on the final
  `merged_levels` immediately before `build_level_index`.

Assignments (all REUSE existing, proven-good, mapIndex-correct zones - zero new DB/Text records):

| level | idx | grid corner | old dbr | new dbr | page |
|---|---:|---|---|---|---|
| uberdungeon/crypt_floor1 (**reported bug**) | 2280 | (-2578,-2682) | EMPTY | greece/knossos.dbr | Greece (0) |
| greece/minidungeons/spartacryptlevel2 | 2278 | (-5644,-1451) | EMPTY | greece/sparta.dbr | Greece (0) |
| olympus/gardenofmerchants | 2276 | (1043,-4074) | olympus_gom.dbr (**dangling/absent**) | olympus/olympus.dbr | Olympus (4) |
| secret_place/* (11 levels, hub landing = DarkForestEnter) | 2235-2245 | X[-2199,-3623] Z[-5419,-6182] | EMPTY | greece/knossos.dbr | Greece (0) |

Notes:
- **crypt_floor1 -> knossos.dbr**: thematic (the SV entrance was from Knossos `maze03`); any
  `mapIndex 0` zone is mechanically equivalent (composite = grid corner + page).
- **GoM -> olympus.dbr**: its shipped `dbr` points at `olympus_gom.dbr`, which is **absent** from
  the base DB (SV 0.98i had it but at `mapIndex 3` = SV's Olympus index, wrong for the AE world
  which uses `mapIndex 4`). Repointing to the existing AE `olympus.dbr` composites GoM on the
  Olympus page with no new record. GoM already carries its own region label ("Duister").
- **Secret Place**: reachable via the Helos hub; parked in empty map space (no zoned neighbour),
  so its continent is **inferred** = Greece (the arrival page). Confidence: MEDIUM (Section 4).

---

## 3. Verification (no heavy build; on COPIES of the deployed maps)

Harness re-serializes the `LEVELS` section of the **deployed DEV** map
(`local/Levels_merged_TESTHUB.arc`, == what Will plays) and the **canonical**
(`local/Levels_merged.arc`). Both PASS identically:

1. **Round-trip faithfulness** - `build_level_index(parse_level_index(map))` reproduces the
   original `LEVELS` bytes exactly (384,499 B). The serializer is byte-faithful.
2. **Surgical diff** - after `apply_zone_dbr_overrides`, exactly **14 entries change, all are
   targets, and ONLY the `dbr` field** (every entry's `ints_raw`, `fname_raw`, `data_offset`,
   `data_length` identical; no non-target entry changes at all).
3. **QUESTS parity** - QUESTS section byte-identical (sha `7ad0f054`, 11,460 B) and untouched;
   the 256-window is not in the `dbr` code path. GROUPS/SD/BITMAPS/DATA2 likewise untouched.
4. **Navmesh untouched** - level blobs (which hold `0x0b`) live in the DATA section; the override
   never reads/writes any blob. `dbr`/`dbr_raw` has exactly two consumers in the build:
   `apply_zone_dbr_overrides` (write) and `build_level_index` (read -> LEVELS only). So every
   `0x0b` navmesh is byte-identical.
5. **Georeference (crypt_floor1)** - grid corner (-2578,-2682), 960x960 TGA present and
   byte-unchanged, footprint X[-2578,-2258] Z[-2682,-2362] contains the boat-dialog teleport
   target (-2438,-2450); now assigned `knossos.dbr` (mapIndex 0) -> TGA composites on the Greece
   page at its grid corner. Before: empty `dbr` -> never composited -> black void.
6. `py -m py_compile tools/svaera_plus_portals.py` - OK.

Regenerable: session scratchpad `mm_verify.py` (+ `mm_probe1..11.py` for the mechanism evidence).

---

## 4. Confidence + residual risk

- **HIGH** - crypt_floor1 (the reported bug) and SpartaCryptLevel2: Greek origin, Greek grid
  space, both page models agree on `mapIndex 0`. GoM -> Olympus: it *is* Olympus, region label
  already correct, only the page was broken by the dangling pointer.
- **MEDIUM** - Secret Place cluster continent = Greece (inferred: reached from Greece, empty map
  space, no zoned neighbour). If wrong, the worst case is cosmetic (the cluster shows on the Greek
  world map ~2000u south of Athens as a detached island); it cannot crash and is strictly better
  than the current black-void. Swapping continents later is a one-constant edit.
- Not a regression risk: no spatial overlap with existing content at any assigned page (verified
  grid ranges); the change is a self-delimiting string field.

---

## 5. Deferred to round 2 (documented, not blindly attempted)

1. **Top-right area LABEL for crypt_floor1** ("Village of Helos" -> its own name). The label is a
   **region GUID embedded in the level's `0x17` section**. `0x17` is un-RE'd in this repo
   (`blob_diff.py` calls it `Unknown_17`; no parser/injector exists) and is **format-variant**:
   AE dungeons (v0x0f) and TQIT-era crypt_floor1 (v0x0e) lay out the leading GUID table
   differently, and the table is followed by terrain data that references entries **by index**, so
   a naive append shifts indices / is inert. Per the b46 LAW ("map-format edits only via the
   proven parse/serialize round-trip tooling"), this needs a dedicated `0x17` RE pass first.
   Spec for round 2: RE the `0x17` GUID-table + index model, add an SD region record ("The Uber
   Dungeon", `sd_format` fully supports region add), embed its GUID at the level's region slot,
   round-trip-verify. Only crypt_floor1 (and the ref-less secret_place levels) need this; Sparta
   Crypt/DarkForestEnter/GoM already carry region labels.
2. **Dedicated zones** (vs reused) - would give a named fast-travel node, but these dungeons have
   no rebirth fountain so the zone name never surfaces; deferred unless in-game shows otherwise.
3. **coldtombs** (egypt/minidungeons) - SKIPPED: vestigial (no navmesh, `0,0` bitmap = no TGA), so
   nothing to composite; also not on the hub roster.

---

## 6. Deploy coupling

Map-tooling only -> rebuild the map (`py tools/svaera_plus_portals.py`, canonical + TESTHUB) and
deploy `Levels.arc`. No DB/Text/Quests change, so no arz+Text or Levels+Quests coupling this
round. In-game confirmation (map draws under the player; label still stale = expected, round 2)
is the only remaining check and requires a launch (restart Steam per standing rule).
