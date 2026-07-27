# b89 - ocean_extension05 blood-cave crash: RCA + hotfix (2026-07-27)

> **Status:** fix implemented pipeline-side, gated, built, deployed to DEV (`build49-dev`).
> Will's walk test is the confirmation.
> **Will (verbatim, 2026-07-27):** *"this area is literally right in the beginning of this
> section of the blood cave, we have to fix this bug to make the blood cave even playable"*.
> P0, not avoidable.

---

## 1. The runtime evidence

Two independent Frida sessions (`local/crash_probe/probe_20260727_155800.log`,
`probe_20260727_155845.log`) against the deployed DEV map (build48 TESTHUB,
md5 `c1e814e499fafcf02725549f918fa89b`) both died the same way:

| | session A | session B |
|---|---|---|
| navmesh loads before death | 5 in 6 s | 11 over 4 min |
| co-resident chambers at death | 10 | 9 |
| **ENTER with no LEAVE** | **ocean_extension05** | **ocean_extension05** |
| chamber GUID | `e11908536840dc7e50d5a88221b17b22` (LEVELS idx 2266) | same |
| reported `deps` | `[ocean_extension05, ocean_extension05, ocean_extension05]` | same |

Different pace, different residency, same chamber. 20+ other chamber loads across both
sessions completed cleanly (LEAVE, `al=1`), including every blood-cave neighbour and
`new_secretdoor_transitionhallway`. So this is **not** memory/co-residency pressure - it is
that one section.

`navOK=0` at ENTER is the NORMAL in-progress state (every ENTER shows it; LEAVE flips it to
1). The refuted "navOK=0 = rejected" theory plays no part in this RCA.

---

## 2. Root defect

`ocean_extension05`'s `0x0b` section is the **dead Approach-22 "148-byte stub"** emitted by
`tools/build_section_surgery.build_minimal_rec02` and injected by `svaera_plus_portals`
step 7b **tier 3** (the "no donor" fallback).

That stub was written against a **wrong model of the REC\x02 format**. Its own docstring read
field `+12` as `diff_count = 3 (Normal/Epic/Legendary)` followed by "3 x 16-byte GUID blocks".
The real, RE-proven layout (`tools/rec02_format.py`, byte-identical round-trips over 670 real
sections) is:

```
+12  uint32 guid_count           <- a GUID LIST length, not a difficulty count
+16  guid_count * 16B GUIDs
+..  int32 center[3] / uint32 dims[3]
+..  3 x tileset, each = 52B dtTileCacheParams + int32 numTiles ( + numTiles tile records )
```

So the stub produced two defects at once:

1. **A DEGENERATE GUID list** - `guid_count = 3`, all three entries the level's OWN GUID.
   That is the `[own, own, own]` signature the probe printed. Stock TQAE ships **zero** such
   lists in 2235 levels.
2. **A TRUNCATED body** - one **44-byte** parameter block (missing `maxTiles` + `maxObstacles`,
   which make `dtTileCacheParams` 52 bytes) plus four stray zero `uint32`s, instead of three
   complete 56-byte tilesets. Total 148 bytes.

**The crash mechanism.** `ProcessRLTD` parses tilesets from the body until the section ends.
Reading the stub it consumes set 1 out of the 44-byte block + the first 8 stray bytes
(`maxTiles = 0`, `maxObstacles = 0`, `numTiles = 0`), leaving the cursor **4 bytes from the end
of a 148-byte section** - and it still needs sets 2 and 3. It reads them out of whatever
follows in the heap: garbage `maxTiles`/`numTiles`, then a tile loop walking arbitrary
`dataSize` values. That is the ENTER-with-no-LEAVE, and the process is gone seconds later.

**Why the level is loaded at all.** `ocean_extension05` occupies grid corner
`(4426,-37,3109)`, a 240x240 box that abuts `drxBC3`, `ocean_extension02` and
`ocean_extension03` - i.e. it sits *inside* the walkable block Will crosses at the start of
that section. The engine streams by grid proximity, so "declared cut" buys nothing: the probe
shows `ocean_extension01`, `02`, `03` streaming in cleanly immediately before `05` detonates.

**Why every existing gate missed it.** The stub's *header* is impeccable: version 1, correct
`payload_size` (136 == 148-12), `guid_count` 3 (inside the sane 1..16 range), and every GUID
resolves in the LEVELS index (it is the level's own). `MAP-NAV-1` only parsed the header
(`rec02_header`); `verify_merged_bc_navmeshes` only compared SIZES and printed
`ok ocean-stub`; and `contracts_map.is_cut()` exempted `ocean_extension*` from `MAP-NAV-3`
anyway. Nothing in the repo had ever walked a container's body.

---

## 3. Sweep: exactly which chambers carry it

`tools/audit_navmesh_guid_lists.py` decodes every level's `0x0b` in a `Levels.arc` and reports
degenerate / own-only / unresolvable / structurally invalid containers.

| map | levels | struct-invalid | degenerate | own-only | unresolved GUIDs | no 0x0b |
|---|---|---|---|---|---|---|
| **stock TQAE** `Resources/Levels.arc` | 2235 | **0** | **0** | 251 | 0 | 21 |
| deployed DEV (build48 TESTHUB) | 2282 | **8** | **8** | 260 | 0 | 21 |
| `local/Levels_merged.arc` (canonical) | 2282 | **8** | **8** | 259 | 0 | 21 |
| `local/Levels_merged_TESTHUB.arc` | 2282 | **8** | **8** | 259 | 0 | 21 |

The 8 are identical in every variant, and they are exactly the tier-3 (no-donor) levels:

| idx | level | file | grid corner | box |
|---|---|---|---|---|
| 2266 | `ocean_extension05` | `Levels\World\xBloodCave\` | (4426,-37,3109) | 240x240 |
| 2267 | `ocean_extensionx01` | `Levels\World\xBloodCave\` | (4006,-37,2689) | 180x180 |
| 2269 | `ocean_extensionx03` | `Levels\World\xBloodCave\` | (3826,-37,3229) | 180x180 |
| 2270 | `ocean_extensionx05` | `Levels\World\xBloodCave\` | (4006,-37,3229) | 180x180 |
| 2271 | `ocean_extensionx04` | `Levels\World\xBloodCave\` | (3646,-37,3229) | 180x180 |
| 2272 | `ocean_extensionx06` | `Levels\World\xBloodCave\` | (3646,-37,3049) | 180x180 |
| 2273 | `ocean_extensionx07` | `Levels\World\xBloodCave\` | (3646,-37,2689) | 180x180 |
| 2277 | `coldtombs` | `Levels\World\Egypt\MiniDungeons\` | (-4283,-5,3123) | 512x512 |

Will would have hit the next one minutes later; `coldtombs` is the same landmine parked in
Egypt. **All 8 are fixed in this wave.**

### Stock never ships a degenerate list - and own-only is NOT the same defect
- **Degenerate (>1 entry, all identical): 0 occurrences in stock.** Ours only ever came from
  the malformed generator. It is a genuine invariant.
- **Own-only (`guid_count == 1`): 251 occurrences in stock** - `Crypt01`, `UG_Mines01`,
  `SlavePits`, `SerketCaves01`, `DevMaze01..14`, `TempleOfHathor01`, ... It is the normal form
  for a self-contained interior. **Call recorded:** build47/48's fix A (collapsing
  `new_secretdoor_transitionhallway` to own-only) is therefore **NOT** in this defect class and
  is left exactly as it is. Its structure was already valid (157,898 B, 3 complete tilesets),
  and the probe watched it ENTER and LEAVE cleanly (`al=1`) in session B. `MAP-NAV-6` is
  deliberately written to fire on self-duplication only, and the negative test asserts it stays
  silent on own-only.

### What "the true GUID list should read"
For `ocean_extension05` the geometric neighbours are `drxBC3`, `ocean_extension02` and
`ocean_extension03` (grid-box abutment), and **no other mesh in the map lists
`ocean_extension05`'s GUID** - nor any of the other 7. The GUID list is only ever used to
resolve a tile's `areas` id (1-based index into the list) to an owning Region. A mesh with **no
tiles** dereferences the list zero times, so the honest list for these 8 is `[own]`.

---

## 4. Is `ocean_extension*` really cut content? (fix (b) ruled out)

`tools/contracts/contracts_map.py:CUT_LEVEL_MARKERS` lists `ocean_extension`, and
`docs/CUT_CONTENT.md` calls the family "backdrop/scenery only ... never intended to be
entered. Permanently cut." **The map refutes that as a blanket statement:**

- `ocean_extension01/02/03/04` and `ocean_extensionx02/x08` carry **real generated navmeshes**
  (397 KB / 232 KB / 238 KB / 165 KB / 106 KB / 56 KB) built from real `0x0a` geometry.
- `drxBC3`'s navmesh GUID list is `[drxBC3, drxBC_Finale, ocean_extension01, ocean_extension02,
  ocean_extension03, ocean_extension04]` and `drxBC_Finale`'s is `[drxBC_Finale, drxBC3,
  ocean_extension01, ocean_extension03, ocean_extensionx02, ocean_extensionx08]` - meaning
  those meshes rasterize **walkable cells owned by the ocean levels**. They are live, walked-on
  content.
- The probe shows the player streaming `ocean_extension01/02/03` and then `05`.

So the family is a **mix**: 6 live walkable members, 8 geometry-less members. Option (b)
("make it not stream") is impossible regardless - the engine streams by grid proximity, the
level sits in the middle of the walkable block, and Will's report says he is standing there.
Removing its LEVELS entry would tear a hole in the grid. **Ruled out.**

---

## 5. Fix chosen: (c) - make the container what the engine actually parses

`build_minimal_rec02` now emits a **structurally valid, EMPTY** REC\x02 container:

```
224 bytes = 16 header + 1*16 GUID + 24 center/dims + 3 * 56 tileset
  guid_count = 1, the level's own GUID
  3 complete tilesets: 52B dtTileCacheParams + int32 numTiles = 0
  maxTiles = 2 * ceil(2*dims_x / 12.8) * ceil(2*dims_z / 12.8),  maxObstacles = 128
  center / dims UNCHANGED from before (so the positioning gate is untouched)
```

**Every choice is copied from stock, not invented:**

- **Empty is a real stock form.** Stock ships **60** levels whose navmesh has `numTiles == 0`
  in all three sets - borders, vistas, ocean borders: terrain with no walkable floor, exactly
  our case. They are 240..304 bytes = `208 + 16*guid_count`, always **3 complete tilesets**.
- **The `maxTiles` formula is verified against stock.** `Rhodes_OceanBorder_01` has
  `dims=(80,46,80)` and ships `maxTiles = 338`; `2 * ceil(160/12.8)^2 = 2*13*13 = 338`. Exact.
  It is also what `gen_rec02.generate()` computes for a real mesh, so both producers agree.
- **Empty containers are normal streaming citizens.** 166 stock meshes list an empty-navmesh
  level as a neighbour GUID.
- **`guid_count == 1` is stock-normal** (251 base levels) and **runtime-proven** on our own map
  (`new_secretdoor_transitionhallway`, gc=1, ENTER+LEAVE `al=1` in probe session B). It is also
  residency-proof: the only GUID named is the level being loaded, which is by definition
  stream-resident when its own navmesh loads - safe whether or not ProcessRLTD's residency gate
  behaves as the b87 lane theorised.

**Alternative considered and recorded as debt:** stock also ships **21** levels with **no
`0x0b` section at all** (`ConvergenceBossRoomBackdrop`, `TiamatArenaVista`, `WaterEdge05`,
`PineForest04Border02`, ...), and 43 stock meshes list one of those as a neighbour, so absence
is demonstrably survivable too - and `gen_bc_navmeshes.py`'s own docstring says these levels
"legitimately get no 0x0b". The valid-empty container was preferred because it is the smaller
delta (the blob shape and the 0x0a-stripping invariant are unchanged), it keeps every SV level
carrying a navmesh, and it reproduces the healthy runtime signature (ENTER -> LEAVE `al=1` ->
`navOK=1`) instead of leaving 8 regions permanently navmesh-less. If Will's walk test still
dies at an ocean chamber, the next move is dropping the section entirely (BL-b89-DEBT-1).

This is a **pipeline** fix (BL-103): one function, deterministic, regenerated on every build;
no arc was hand-patched.

---

## 6. The gate that would have caught it

`contracts_map.contract_navmesh` gains two P0 checks backed by a new full-container walk,
`contracts_map.rec02_structure` (same traversal as the proven `rec02_format.parse_rec02`, but
it never raises):

- **`MAP-NAV-5`** - the container body must be **exactly 3 complete tilesets** with every tile
  record's `dtTileCacheLayerHeader` magic (`RLTD`) present and the section ending cleanly. Fires
  on truncation, a short/extra tileset, trailing bytes, and a tileset claiming a tile it does
  not carry.
- **`MAP-NAV-6`** - the GUID list must not be **self-duplicated** (`guid_count > 1` with one
  distinct value). Stock ships none.

Both apply to **every** level including declared-cut ones - the engine streams a level by grid
proximity whether or not the design calls it reachable, so a malformed container in a "cut"
level is a live crash. Neither is whitelisted.

`tools/verify_merged_bc_navmeshes.py` now (a) walks the structure of every blood-cave `0x0b`
instead of only comparing sizes, (b) expects the 224-byte empty container, and (c) **fails**
(rather than printing `?`) when an ocean level's section is the wrong size.

**Planted negative tests** (`tools/contracts/_negtest_map.py`, 36/36 PASS): the **real
148-byte stub is reconstructed byte-for-byte** (`make_b89_stub`) and asserted to trip both
`MAP-NAV-5` and `MAP-NAV-6` at P0 - *and* to pass every pre-existing `MAP-NAV-1` header check,
which is the regression-proof that the old gates could not see it. Plus: 2-tileset, 4-tileset,
trailing-junk and lying-numTiles variants; `MAP-NAV-6` silent on distinct multi-GUID and on
own-only; and the shipped 224-byte replacement clearing every navmesh contract.

While wiring these, the harness itself was found dead: `test_doors` pointed at a hard-coded
path inside a long-deleted session scratchpad, so `_negtest_map.py` crashed before finishing
for anyone. It now resolves a live `Quests.arc` (or `SVC_QUESTS_ARC`) and skips loudly.

---

## 7. Build, verification and deploy

See the BUILD49 gate record in `docs/BACKLOG.md` for the full proof list (hashes, blob-diff,
contract battery, deploy verification).

---

## 8. Related pipeline change

`svaera_plus_portals.main` and `gen_bc_navmeshes` had the two merge inputs hard-coded to
`reference_mods/SVAERA_customquest/...` and `upstream/soulvizier_098i/...`. Both caches were
**absent** on this machine, so the map could not be rebuilt at all - the build died deep inside
`ArcArchive.from_file` with a bare `FileNotFoundError`. Both now accept `SVC_SVAERA_ARC` /
`SVC_SV_ARC` (defaults unchanged) and fail loud naming the variable. The SVAERA base was found
in the Steam Workshop content dir (item `2076433374`).
