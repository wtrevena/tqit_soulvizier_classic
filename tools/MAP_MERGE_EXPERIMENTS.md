# Map Merge Experiments Log

## Problem Statement
Soulvizier Classic needs a merged Levels.arc for Custom Quest mode that includes:
- SV's custom content (drxmap overlays, SV-only levels like UberDungeon)
- SVAERA's base map structure (Custom Quest compatible, v0x11 format)
- Functional terrain boundaries, cave entrances, pathfinding

## Key Discovery: v0x0e vs v0x11
- **SV original**: ALL levels are v0x0e format (`LVL\x0e`)
- **SVAERA**: Almost all levels are v0x11 format (`LVL\x11`)
- **v0x0e is INCOMPATIBLE with Custom Quest mode** — deploying unmodified SV Levels.arc causes player to be unable to move at all
- Custom Quest requires v0x11 format for all levels

## v0x0e vs v0x11 Format Differences
| Feature | v0x0e | v0x11 |
|---------|-------|-------|
| Magic | `LVL\x0e` | `LVL\x11` |
| 0x05 instance records | 56 bytes each | 72 bytes each (56 + 16 zero bytes) |
| 0x09 section (grid) | Present (in-blob pathfinding) | Absent |
| 0x14 section (metadata) | Absent | Present (28 bytes per instance) |
| Pathfinding | 0x09 in-blob grid | DATA2 external section |

## Shared+drxmap Levels (9 total)
These levels exist in both SV and SVAERA, and SV modified them (contain `drxmap` references):
1. `DelphiLowlands03.lvl` - 2 drxmap refs
2. `DelphiLowlands04.lvl` - 14 drxmap refs (uber dungeon NPC injected here)
3. `DelphiLowlands02.lvl` - 7 drxmap refs
4. `StartingFarmland06D.lvl` - 1 drxmap ref
5. `HiddenValley01.lvl` - 1 drxmap ref (cave entrance, respawn fountain)
6. `HiddenValleyBorder04.lvl` - 5 drxmap refs
7. `RoadToTown03A.lvl` - 3 drxmap refs
8. `ScrabledEggs_Floor06.lvl` - 1 drxmap ref
9. `Random09A.lvl` - 7 drxmap refs (blood cave entrance)

## ints_raw Key Facts
- 13 uint32s per level entry in the LEVELS index
- ints[4]: differs by +20 between SV and SVAERA for outdoor levels (e.g., SV=56, AE=76)
- ints[6-12]: spatial coordinates (same for most shared levels, different for Random09A)
- MapCompiler: ints[0-5] are ALL ZERO for all levels

---

## Experiment Log

### Exp 1: Section Surgery (SVAERA terrain + SV objects)
- **Date**: 2026-03-06
- **Approach**: For 8 shared+drxmap levels where AE=v0x11, use `perform_section_surgery` (SVAERA terrain sections 0x01-0x04, SV objects in 0x05 converted to v0x11). Random09A (AE=v0x0e) converted full SV blob.
- **ints_raw**: SVAERA's (from ae_levels)
- **DATA2**: SVAERA's for surgery levels, SV's for Random09A
- **Result**: Player CAN move. Can approach cave area. BUT:
  - Cave entrance on minimap doesn't align with 3D cave entrance
  - Cannot enter cave
  - Black rectangular holes in terrain near stone path area (level tile boundaries)
- **Diagnosis**: SVAERA modified terrain layout for these levels. SV's objects (cave entrance position) don't match SVAERA's terrain geometry. Black holes at level boundaries where drxmap-modified SV objects reference terrain that doesn't exist in SVAERA's base.

### Exp 2: Full SV Blob Conversion (SV terrain + SV DATA2)
- **Date**: 2026-03-06
- **Approach**: Convert ALL 9 shared+drxmap SV blobs from v0x0e to v0x11. No section surgery. Append SV's DATA2 for all 9.
- **ints_raw**: SVAERA's (unchanged from ae_levels — BUG)
- **DATA2**: SV's (appended, bitmap entries overridden)
- **Result**: Player CAN move. Invisible wall BACK — prevents approaching cave area.
- **Diagnosis**: Two possible causes:
  1. SV's DATA2 may not be valid for v0x11 (SV uses v0x0e which stores pathfinding in 0x09, not DATA2)
  2. ints_raw mismatch (SVAERA ints with SV terrain)
  3. Level boundary mismatch (9 SV terrain tiles surrounded by SVAERA terrain tiles)

### Exp 3: Full SV Blob + SVAERA DATA2 + SV ints_raw
- **Date**: 2026-03-06
- **Approach**: Convert ALL 9 shared+drxmap SV blobs to v0x11. Keep SVAERA's DATA2 (known good for v0x11). Use SV's ints_raw for these levels.
- **ints_raw**: SV's (copied from sv_levels)
- **DATA2**: SVAERA's (MapCompiler bitmap entries, no override)
- **Result**: FAIL — invisible wall persists at same location as Exp 1 black holes (level tile boundary)
- **Conclusion**: The invisible wall is at the BOUNDARY between converted SV terrain tiles and adjacent SVAERA terrain tiles. Neither ints_raw nor DATA2 source is the cause — it's terrain edge mismatch between adjacent level tiles.

### Exp 4: MapCompiler Output + metadata patches (no format conversion)
- **Date**: 2026-03-06
- **Approach**: Use MapCompiler's compiled output (`merged_recompiled.map`) as the base. MapCompiler compiled from merged source files (SVAERA levels + SV drxmap/SV-only levels overlaid). Patch metadata only: GROUPS (SV+SVAERA-only), SD (SV's), QUESTS (merged+uber), ints_raw (restored from originals). Inject uber dungeon NPCs.
- **Key difference**: MapCompiler handles terrain boundaries, DATA2, and format compilation correctly. No binary format conversion needed.
- **Format**: v0x11=1409, v0x0e=503, other=369 (mixed — MapCompiler preserved source format)
- **Size**: 1947 MB (638 MB ARC), 2281 levels, 540 drxmap refs
- **Result**: Invisible wall persists

### Exp 5: MapCompiler Output + metadata patches + v0x0e→v0x11 conversion
- **Date**: 2026-03-06
- **Approach**: Same as Exp 4 but also convert ALL 503 v0x0e levels to v0x11 using `convert_v0e_blob_to_v11()`. Compact DATA section to eliminate dead v0x0e blobs.
- **Format**: v0x11=1912, v0x0e=0, other=369
- **Size**: 1944 MB (under 2GB)
- **Result**: Invisible wall persists
- **Note**: 369 v0x0f levels still unconverted — never investigated

### Exp 6: Raw MapCompiler Output (zero modifications)
- **Date**: 2026-03-06
- **Approach**: Package `merged_recompiled.map` directly into ARC with ZERO modifications. No GROUPS/SD/QUESTS patching, no ints_raw restore, no format conversion, no NPC injection.
- **Script**: `tools/baseline_mc_test.py`
- **Format**: v0x11=1409, v0x0e=503, v0x0f=369 (unchanged)
- **Size**: 637.5 MB ARC
- **Result**: CRASH — game crashes immediately on Custom Quest start. log.xml is empty (just header). No crash dump generated.
- **Conclusion**: Raw MC output cannot be deployed. Metadata patching (at minimum GROUPS/SD/QUESTS/ints_raw) is required for the game to start. The invisible wall is NOT caused by our metadata patching.

### Exp 7: SVAERA Unmodified Baseline
- **Date**: 2026-03-06
- **Approach**: Deploy SVAERA's original Levels.arc with ZERO modifications. No SV content, no merging, no format conversion.
- **Size**: 631.3 MB ARC
- **Result**: SUCCESS — no invisible wall. Player can walk freely in Chumbi Valley and enter the cave.
- **Conclusion**: The invisible wall is definitively caused by merging SV content into the map. SVAERA's base map works perfectly in Custom Quest mode.

---

## Key Discovery: v0x0f Format
- **369 levels** in MapCompiler output use v0x0f (`LVL\x0f`) — a third format
- Includes: border tiles, transitions, optional caves, underground floors
- Our `convert_v0e_blob_to_v11()` only handles v0x0e→v0x11, SKIPS v0x0f entirely
- v0x0f structure is undocumented — may have different 0x05 record sizes, 0x09/0x14 requirements
- If a v0x0f level sits at the invisible wall boundary, it could be the cause

## What We've Ruled Out
| Factor | Ruled out by | Notes |
|--------|-------------|-------|
| GROUPS patching | Exp 6 (crash without it) | Required for game to start |
| SD patching | Exp 6 | Required |
| QUESTS patching | Exp 6 | Required |
| ints_raw source | Exp 2 vs 3 | Same wall with SV or SVAERA ints |
| DATA2 source | Exp 2 vs 3 | Same wall with SV or SVAERA DATA2 |
| Binary v0x0e→v0x11 conversion | Exp 4 vs 5 | Wall present with and without |
| Adjacent tile terrain mismatch | Exp 4+ (MapCompiler) | MC handles boundaries, wall persists |
| SVAERA base map | Exp 7 | No wall in unmodified SVAERA — wall is from SV merging |

## Active Theories

### v0x0f Levels Theory (NEW)
369 v0x0f levels are completely unhandled. If the invisible wall location corresponds to a v0x0f level, it could be format incompatibility with Custom Quest.

### Shared+drxmap Replacement Theory (NEW)
The 9 shared+drxmap levels are SV's versions overlaid onto SVAERA's source before MapCompiler. Even though MapCompiler handles terrain boundaries, the SV source files may have different geometry/dimensions than SVAERA's, causing compiled output to have mismatched edges.
**Test**: Deploy with SV-only levels added but NO shared+drxmap replacements (use SVAERA's versions for all 9). If wall disappears, the shared level replacements are the cause.

### 0x14 Section Theory
Our `convert_v0e_blob_to_v11` generates default 0x14 entries: `(2, 0, 1, 1, 0)` per instance (28 bytes). Real SVAERA 0x14 sections may have varied values. Wrong 0x14 values could affect instance interactivity or collision.

### Fallback: Section Surgery + Accept Misalignment
If no conversion approach works for cave entrance, go back to section surgery (Exp 1 result) and accept:
- Cave entrance is visually misaligned but might still be enterable at original position
- Black holes are cosmetic only
- Player can move freely through the game
