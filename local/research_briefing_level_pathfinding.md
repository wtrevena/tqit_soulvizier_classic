# Research Briefing: TQAE Level Pathfinding Requirements (Update 6)

## Context

We are modding Titan Quest Anniversary Edition (TQAE). We have two mods:
- **SVAERA**: A TQAE-native mod compiled with the TQAE MapCompiler. 2235 levels. Works perfectly.
- **Soulvizier (SV) 0.98i**: A TQIT-era mod compiled with the original TQ:IT editor. 1004 levels. Works perfectly as standalone.

We are merging them: SVAERA as the base map + 46 SV-only levels (levels that exist in SV but not in SVAERA) appended. The merged map runs in TQAE's "Custom Quest" mode.

## The Problem

After teleporting to SV-only levels via BoatDialog (a quest action that warps the player to world coordinates), the player and pets **cannot move**. The level geometry loads and renders correctly, the player character appears at the destination, but WASD movement and click-to-move both fail. Pets also cannot move.

## What Works

1. **BoatDialog teleportation to SVAERA levels works perfectly** — including v0x0e format levels. We confirmed this by teleporting to ArcadiaDungeonPassage.lvl (a SVAERA v0x0e level, index 973). Pets could move freely. Player was stuck in rocks (bad coordinates), but pathfinding itself was active.

2. **BoatDialog teleportation to SVAERA v0x11 levels works** — confirmed with HiddenValley01.

3. **SV 0.98i standalone runs on TQAE with full movement** — all SV levels are v0x0e, none have 0x0b sections, and pathfinding works. This proves TQAE CAN handle v0x0e levels with only 0x0a (PTH\x04) pathfinding.

4. **Level geometry streaming works for SV-only levels** — the cave/dungeon renders, player is visible.

5. **NPC injection works** — injected NPCs appear as rendered meshes.

## What Doesn't Work

- Player movement at ANY SV-only level destination (WASD and mouse click)
- Pet movement at SV-only level destinations
- Both pathfinding (AI navigation) and collision (player physics) appear affected

## Map File Format (world01.map)

The .map file inside Levels.arc contains these sections:

| Section | Type ID | Purpose |
|---------|---------|---------|
| QUESTS | 0x1b | Quest name strings |
| GROUPS | 0x11 | Level group definitions (uses GUID hashes, NOT level indices) |
| SD | 0x18 | Scene data — zone definitions with string names and float parameters (lighting/atmosphere) |
| LEVELS | 0x01 | Level index: per-level fname, ints_raw (52 bytes), data_offset, data_length |
| BITMAPS | 0x19 | Maps level_index -> {offset, length} into DATA2 section. Format: unknown(4) + count(4) + count * (offset(4), length(4)) |
| 0x10 | 0x10 | 164 bytes. Structure: uint32(count=10) + count * (uint32 id, float, float, float). See analysis below. |
| DATA2 | 0x1a | Minimap bitmap data (TGA format, NOT pathfinding). Header: uint32(0) + uint32(level_count). |
| DATA | 0x02 | Concatenated level blobs (LVL magic + sections) |

### ints_raw (52 bytes = 13 int32 per level)
- [0..5]: Tile dimensions — half-widths and heights
- [6,7,8]: Grid position (signed int32 x, y, z) — world-space corner of the level
- [9..12]: GUID (used in GROUPS references). All 2281 GUIDs are globally unique across the merged world — zero collisions.

### Section 0x10 Analysis (NOW DECODED)

164 bytes. Structure: `uint32(count=10)` + `count * (uint32_id, float, float, float)`.

SVAERA and SV versions are nearly byte-identical (single float rounding diff: 1.000000 vs 0.999998 at offset +124).

Entries (identical in both maps):
```
Entry 0: id=  312  (    50.346,      1.234,     25.301)
Entry 1: id=   31  (    45.989,    -10.416,     66.036)
Entry 2: id=   92  (    99.143,      1.000,    130.003)
Entry 3: id=  162  (    32.357,     -4.505,    172.929)
Entry 4: id=  264  (   171.738,      7.899,     75.400)
Entry 5: id=  269  (    85.776,      1.000,     51.864)
Entry 6: id=  271  (    75.579,      1.000,     44.468)
Entry 7: id=  274  (    91.854,      1.000,    122.947)
Entry 8: id=  282  (    35.512,      1.000,     68.837)
Entry 9: id=  528  (    59.000,      1.000,     69.000)
```

The IDs (312, 31, 92, etc.) are small numbers, possibly level indices or zone identifiers. The floats could be camera/lighting parameters. **This section does NOT contain a level count gate** — it has only 10 fixed entries regardless of how many levels exist in the map.

### DATA2/BITMAPS Correction

Based on your earlier research, we now agree DATA2/BITMAPS are likely **minimap bitmap data** (TGA format, 24bpp), NOT pathfinding grids. The stride=24 matches 24-bit RGB, and the `width * height * 3` data size matches TGA pixel data. This means we were wrong about DATA2 being pathfinding data.

### Level Blob Format
- Magic: `LVL` + version byte (0x0d=original TQ, 0x0e=TQIT/TQAE-recompiled, 0x11=TQAE native)
- Internal sections (type byte + size + data):

| Section | Description | Notes |
|---------|-------------|-------|
| 0x05 | Entities (objects/NPCs) | v0x0e: 56-byte records, v0x11: 72-byte records. Differs in 80% of shared levels. |
| 0x06 | Unknown | SVAERA v0x0e: 3-5 KB. SV v0x0e: 463 bytes to 330 KB. Differs in 7% of shared levels. |
| 0x09 | Grid section | v0x0e only (removed in v0x11). Small (24-88K bytes). |
| 0x0a | PTH\x04 — TQIT pathfinding | ALL SV levels have this. SVAERA v0x0e levels mostly do NOT (446/449 lack it). |
| 0x0b | REC\x02 — TQAE pathfinding | 2214/2235 SVAERA levels have this. NO SV levels originally have it. |
| 0x14 | Metadata | Needed for entity interactivity. Small or empty. |
| 0x17 | Unknown | SVAERA v0x0e: 144-230 KB. SV v0x0e: 4-390 KB. Differs in 56% of shared levels. |

**CORRECTION from Update 2:** Earlier claim "0x06 and 0x17 identical between SV/SVAERA for shared levels" was WRONG. Cross-level comparison across 336 shared levels shows significant differences in 0x05 (80%), 0x17 (56%), 0x06 (7%). Also, 186/336 SV shared levels are v0x0d (not v0x0e as assumed).

## Merge Strategy

Our merge script (`svaera_plus_portals.py`) does:

1. **LEVELS**: All 2235 SVAERA levels (indices 0-2234) + 46 SV-only levels (indices 2235-2280)
2. **GROUPS**: SV's GROUPS + SVAERA-only GROUPS (merged by name). Uses GUID hashes, not level indices.
3. **SD**: SV's SD section verbatim (zone definitions with string names)
4. **QUESTS**: SVAERA + SV-unique + custom quest names
5. **BITMAPS**: SVAERA bitmaps (offset-shifted) + new entries for SV-only levels pointing to appended DATA2
6. **DATA2**: SVAERA's DATA2 + SV's per-level DATA2 data appended at the end. Header level count updated to 2281.
7. **DATA**: SVAERA blobs (with NPC injection patches) + SV-only blobs appended
8. **Section 0x10**: Preserved from SVAERA (164 bytes)

### Blood Cave Grid Shift
The xBloodCave levels are shifted by (+1663, 0, +922) to be grid-adjacent to SVAERA's HighAltituedBorder01 level. Other SV-only levels (UberDungeon, Secret_Place, BossArena) keep their original SV grid positions.

## Verified Correct

We have verified in the merged output:
- All 46 SV-only level blobs have valid LVL magic and correct data offsets
- All SV-only levels (except 1) have valid BITMAPS entries pointing to valid DATA2 data (0x20000 preamble verified)
- DATA2 level count updated to 2281
- All data offsets are under 2 GB (int32 max), no overflow
- Blood cave grid positions are correctly shifted
- BoatDialog target coordinates fall within bc_initialpathway's grid area
- **Zero GUID collisions** across all 2281 levels (2235 SVAERA + 46 SV-only all have unique ints_raw[9..12])

## Complete Experiment Log

### Approaches 1-8 (Earlier — ALL FAILED)
1. **v0x0e blobs, no DATA2 bitmap entries** → geometry loads, can't move
2. **v0x0e blobs + SV DATA2 (wrong header count)** → can't move
3. **v0x0e blobs + SV DATA2 (correct count, correct bitmaps)** → can't move
4. **v0x0e->v0x11 conversion + SV DATA2** → can't move
5. **v0x11 + 0x0a->0x0b section rename** → can't move (formats are completely different)
6. **v0x0e + SV DATA2 + grid shift** → can't move
7. **v0x0e + SV DATA2 + grid shift + 256-byte REC\x02 stubs** → can't move
8. **v0x0e + SV DATA2 + grid shift + real SVAERA donor 0x0b transplant** → can't move (matched dimensions, patched coordinates)

### Approach 9: SVAERA v0x0e BoatDialog Test — SUCCESS
- Teleported via BoatDialog to ArcadiaDungeonPassage.lvl (SVAERA v0x0e, index 973)
- Player spawned in rocks (bad coords), BUT **pets could move freely**
- **Confirms: v0x0e format works with BoatDialog in the merged map**
- **Confirms: Pathfinding is active for SVAERA v0x0e levels even though they lack 0x0b in standalone SV**

### Approach 10: Strip 0x0a from SV-only blobs — FAILED
- Removed 0x0a (PTH\x04) sections from all SV-only blobs
- Kept transplanted 0x0b from SVAERA donors
- Result: still can't move

### Approach 11: High-Index SVAERA Level — SUCCESS
- Teleported via BoatDialog to SVAERA level at index 2234 (last SVAERA level, Greece_HelosShrineInterior03)
- Player under map (bad coords), but **pets could walk around**
- **Confirms: High level indices (up to 2234) work fine — index magnitude is not the issue**
- NOTE: Index 2234 is the last SVAERA level. Indices 2235+ are SV-only. This test does NOT prove 2235+ work.

### Approach 12: Raw Unmodified SV Blobs — FAILED
- Disabled ALL blob modifications: no 0x0b transplant, no 0x0a stripping, no version conversion
- Only NPC injection (adding entities to 0x05 section) applied
- SV-only blobs used exactly as they exist in standalone SV (which works fine as standalone)
- Result: still can't move, pets also can't move

### Approach 13: Replace SVAERA Slot with SV-Only Blob — FAILED
- Replaced SVAERA level blob at index 973 with bc_initialpathway's blob (an SV-ONLY level)
- This tests whether the issue is slot registration vs blob content
- BoatDialog teleport to that index: geometry loads, but can't move
- **This proves: even at a "known good" SVAERA slot, an SV blob still fails**
- **Conclusion: The issue is in the blob content itself, not just append-time registration**

### Approach 14: Replace Shared Level with SV Version — GAME CRASH
- Took RuinedCity02.LVL (a level that exists in BOTH maps, same geometry)
- SVAERA version: sections [0x05, 0x14, 0x06, 0x09, 0x0b, 0x17] (270 KB)
- SV version: sections [0x05, 0x14, 0x06, 0x09, 0x0a, 0x17] (209 KB)
- Replaced SVAERA blob at index 30 with SV's version of the same level
- BoatDialog target was set to this level's coordinates
- Result: **GAME CRASH as soon as the player enters the region** (before BoatDialog activation)
- The crash occurred during normal world streaming — the engine tried to load the SV blob as part of adjacency-based level streaming when the player walked near Delphi
- **This is different from the "can't move" symptom** — world streaming is stricter than BoatDialog loading
- **This means: SV blobs placed at SVAERA slots cause CRASHES during world streaming, even when they describe the same geometry**

### Approach 15: Task 1 — SVAERA Append-Clone at Index 2281 — SUCCESS
- Cloned ArcadiaDungeonPassage (SVAERA idx 973) as a new appended level at index 2281
- Byte-for-byte identical blob (0x0b present, all sections intact)
- New unique GUID [0x7F000001..0x7F000004]
- **Attempt 1**: Grid shift (+10500, 0, +10500) → black void, no geometry. Too far from existing levels for engine streaming.
- **Attempt 2**: Grid shift (+80, 0, 0) — adjacent to donor → **GEOMETRY LOADED, PETS COULD MOVE**
- Player stuck in rocks (walkable center calc was off), but pathfinding itself was active
- **CONCLUSION: NO append-registration gate.** Appended SVAERA levels at indices beyond 2234 work correctly.
- **This definitively proves the issue is SV blob content, not indexing or registration.**

### Approach 16: MapCompiler Recompilation of SV Source — FAILED
- Created `tools/recompile_single_level.py` — builds minimal WRL + source dir, runs MapCompiler
- Test with SV's RuinedCity02.lvl source (v0x0d, has 0x0a):
  - MapCompiler warning: "using non-optimized version... please re-save this level"
  - Output kept 0x0a — did NOT generate 0x0b
  - Version stayed v0x0d (MapCompiler bumps to v0x0e only on .lvl files it re-saves)
  - Only change: 0x06 section grew from 116KB to 431KB
- Test with SVAERA's RuinedCity02.LVL source (v0x0e, has 0x0b):
  - Same "non-optimized" warning
  - Output has 0x0b — because it was already in the source .lvl
  - **CONCLUSION: MapCompiler passes through pathfinding sections from source .lvl files. It does NOT convert 0x0a→0x0b.**
  - The .lvl source files ARE level blobs — they contain all sections including pathfinding
  - Only the TQAE **Editor** generates 0x0b (the "rebuild pathing" / "re-save" operation)

### Approach 17: Deep Format Analysis of 0x0a vs 0x0b — CONVERSION INFEASIBLE
- Created `tools/analyze_pathfinding_sections.py` — detailed binary format analysis
- **0x0a (PTH\x04)** structure:
  - Header: `PTH\x04` + uint32(1) + uint32(payload_size) + uint32(difficulty_count=6)
  - GUIDs packed with 4-byte zero padding between each (N * 20 bytes)
  - Body: **Serialized object graph** with named string fields: `mesh`, `verts`, `tris`, `edges`, `obstacles`, `connection`, `sectionID`, etc.
  - Type+size sub-record framing (types 0x01, 0x02, 0x03)
  - Almost entirely integer data (97.8%)
  - Compact: ~3.5 KB for RuinedCity02
- **0x0b (REC\x02)** structure:
  - Header: `REC\x02` + uint32(1) + uint32(payload_size) + uint32(difficulty_count=6)
  - GUIDs packed densely (N * 16 bytes, no padding)
  - Body: **Compiled binary nav mesh** with `RLTD` sub-records
  - Dense float vertex arrays (18.8% float-like values)
  - Pre-computed spatial lookup structures
  - Much larger: ~31 KB for RuinedCity02
- **Size ratio 0x0b/0x0a ranges 0.04x to 81x** across 906 shared levels
- **4.4% byte similarity** between bodies (= noise)
- **CONCLUSION: Programmatic conversion is NOT feasible.** Would require full reverse-engineering of both formats — essentially reimplementing the TQAE Editor's pathing rebuild.

### Approach 18: BoatDialog to SVAERA 0x0a-Only Level — INCONCLUSIVE
- Tested LechaionHarbor_B (SVAERA idx 1113, v0x0e, has 0x0a, NO 0x0b)
- BoatDialog teleported player to walkable center of the level
- Player spawned in water (harbor/port level — mostly ocean)
- **INCONCLUSIVE:** All 3 SVAERA levels with 0x0a-only are harbor/water tiles (non-walkable decorative). The 18 with neither are borders/backdrops.
- **Every walkable SVAERA level has 0x0b.** Cannot disprove "0x0b required" hypothesis using these levels.

### Approach 19: AE Editor Normalization Proof Test — BLOCKED (Editor Black Screen)

**Goal:** Open SV RuinedCity02.lvl in TQAE Editor, use "Rebuild All Pathing" to generate 0x0b, then test the normalized blob in the SVAERA map.

**Setup scripts created:**
- `tools/setup_editor_proof_test.py` — Creates Art Manager project with minimal WRL + SV source level
- `tools/verify_editor_output.py` — Checks if Editor-saved .lvl has 0x0b section
- `tools/test_editor_blob_in_map.py` — Would replace SVAERA slot 30 with normalized blob (not yet needed)

**What we tried (all showed black viewport in Editor):**

1. **Minimal WRL (198 KB, 1 level)** — built by `build_minimal_wrl()` for MapCompiler, not compatible with Editor GUI
2. **Full SV world01.wrl (21.6 MB, 1004 levels)** — decompiled from SV map, used directory junctions to `local/decompiled_sv/` for all 752 .lvl source files. Editor opened but showed black screen in both Editor Mode and Layout Mode.
3. **Full SVAERA world01.wrl (43.3 MB, 2235 levels)** — TQAE-native WRL with v7 SD, all 5 expansion directories (Levels, XPack, XPack2-4) via junctions to `local/decompiled_svaera/`. RuinedCity02.lvl swapped with SV version. **Still black screen.**
4. **Fixed Tools.ini `toolsdir`** — was pointing to `C:\WINDOWS\system32\` (wrong), changed to `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\`. **Still black screen but no more crash dump.**
5. **Reset `lastLayoutPos`** from overflow value `(-2976, 2147483620, -1779)` to `(0, 0, 0)`. **Still black.**

**What DID work (partially):**
- The Editor's "Rebuild All Paths" dialog appeared and user clicked Yes
- **world01.sd was upgraded from v6 (TQIT) to v7 (TQAE)** — version field changed from 6→7, acts changed from 1→3
- world01.wrl was re-saved (same size but new timestamp)
- **NO .lvl files were modified** — the per-level pathfinding rebuild did not process any individual levels
- Conclusion: Layout Mode's "Rebuild All Paths" only updates world-level SD pathing, not per-level nav meshes. Per-level 0x0b generation likely requires the Editor to actually load/render the level terrain (which it can't because of the black screen rendering issue).

**Editor crash dump:** `C:\Users\willi\AppData\Local\CrashDumps\Editor.exe.298352.dmp` (6.8 MB, from before toolsdir fix). After fixing toolsdir, Editor no longer crashes but still shows black. The log files (`log.xml`, `log.html`) are empty.

**Current state of PathingTest mod:**
- Path: `C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\Working\CustomMaps\PathingTest\source\Maps\`
- world01.wrl: SVAERA version (43.3 MB, 2235 levels)
- world01.sd: SVAERA version upgraded to v7 by Editor
- Levels/, XPack/, XPack2-4/: junctions to `local/decompiled_svaera/`
- RuinedCity02.LVL: swapped with SV version (524 KB, v0x0d, has 0x0a only)
- Backup of SVAERA RuinedCity02: `RuinedCity02.lvl.svaera_bak` (585 KB)
- Backup of original SV RuinedCity02: `local/sv_originals/RuinedCity02.lvl.bak` (524 KB)

### Approach 19b: pathengine.dll Direct Call Investigation — BLOCKED

**Investigated whether pathengine.dll can be called directly from Python to generate 0x0b data.**

**pathengine.dll exports (8 functions):**
- `_DllExport_GetIPathEngine@4` — root entry point, returns `iPathEngine*`
- 7 reference wrapper functions for iAgent, iCollisionContext, iCollisionInfo, iMesh, iObstacleSet, iPath, iShape

**Blockers (4 total):**
1. **32-bit vs 64-bit:** pathengine.dll is 32-bit, system Python is 64-bit. No 32-bit Python installed.
2. **C++ vtable API:** All methods are pure virtual C++ classes, not flat C functions. Requires manual vtable pointer arithmetic.
3. **iOutputStream callback:** The `save` methods need a C++ abstract class with virtual `put()` method.
4. **TOK format input:** Ground mesh must be in PathEngine's tokenized XML format. Only Engine.dll's `PathMeshCompiler` class knows how to convert TQ region geometry to TOK. This class is buried in Engine.dll's C++ internals.

**PathEngine details:**
- Version: 5.01.01
- Engine.dll loads it via `LoadLibrary`/`GetProcAddress` at runtime
- Relevant Engine.dll classes: `PathFinder` (singleton), `PathMeshCompiler` (converts TQ geometry → TOK)
- PathEngine SDK source may be available at github.com/sigmaco/pathengine

**Viable approaches identified (not yet attempted):**
- **Option A:** Build a 32-bit C++ shim .exe that loads pathengine.dll, reads TOK from stdin, generates nav mesh, writes output. Call from Python via subprocess. Requires MSVC or MinGW-w32 compiler.
- **Option B:** Install 32-bit Python + ctypes vtable hacking. Painful but possible.
- **Option C:** Reverse-engineer the 0x0b binary format and generate it directly. Most complex.
- **Option D:** Use PathEngine SDK source from GitHub to build a 64-bit conversion tool.

## Key Observations (Updated — All Corrections Applied)

1. **v0x0e format is NOT the problem** — SVAERA v0x0e levels work with BoatDialog
2. **0x0b (REC\x02) sections are NOT required for standalone SV** — but may be required in TQAE-compiled maps
3. **GROUPS don't use level indices** — they use GUID hash references (16-byte per member)
4. **SD doesn't use level indices** — it uses zone name strings
5. **DATA2/BITMAPS are minimap bitmaps (TGA)**, NOT pathfinding data
6. **All data offsets are valid** — no int32 overflow
7. **The issue affects ALL SV-only levels**, not just blood cave levels
8. **High level indices work (up to 2281)** — SVAERA level at index 2234 AND appended clone at index 2281 both have working pathfinding via BoatDialog. **No append-registration gate.**
9. ~~**0x06 and 0x17 blob sections are IDENTICAL**~~ **CORRECTION:** 0x05 differs 80%, 0x17 differs 56%, 0x06 differs 7% across 336 shared levels. 186/336 SV levels are v0x0d (not v0x0e).
10. ~~**TQAE MapCompiler's ONLY change**~~ **CORRECTION:** MapCompiler does NOT convert 0x0a→0x0b. It only regrows 0x06 and passes through all other sections unchanged.
11. **38/46 SV-only levels are NOT in any GROUPS record** (but bc_initialpathway IS in GROUPS and still doesn't work)
12. **All 2281 GUIDs are globally unique** — zero cross-map collisions in ints_raw[9..12]
13. **0x10 section** is 10 entries of (id, 3 floats), identical between maps. NOT a level count gate.
14. **All 4 combinations of 0x0a/0x0b tried** — none enable movement for SV-only levels
15. **SV blob at SVAERA slot fails** (approach 13) — not just an append-registration issue
16. **SV blob at SVAERA slot CRASHES during world streaming** (approach 14) — stricter than BoatDialog
17. **Standalone SV works on TQAE** — so "SV blobs are inherently incompatible with TQAE" is FALSE in the standalone context
18. **MapCompiler is a packager, not a converter** — .lvl source files ARE level blobs, MapCompiler just wraps them
19. **0x0a→0x0b programmatic conversion is infeasible** — fundamentally different formats (object graph vs compiled nav mesh)

## Critical Analysis of Failure Modes

We now have TWO distinct failure modes for SV blobs in a TQAE-compiled (SVAERA) map:

### Failure Mode A: "Can't Move" (BoatDialog loading)
- Occurs when BoatDialog teleports player to an SV blob (any index)
- Geometry renders, player visible, but no movement/pathfinding
- Affects both appended SV-only levels AND SV blobs placed at SVAERA slots
- BoatDialog seems to do a "lightweight" level load that streams geometry but doesn't crash

### Failure Mode B: "Game Crash" (World streaming)
- Occurs when the engine loads an SV blob through normal adjacency-based world streaming
- Crashes immediately upon entering the region
- Tested: SV version of RuinedCity02 placed at SVAERA index 30
- World streaming does a "full" level load that hits an incompatibility and crashes

### What This Tells Us
1. **SV blobs ARE format-incompatible** with the TQAE engine when placed inside a TQAE-compiled world — the crash during world streaming proves this definitively
2. **BUT standalone SV works on TQAE** — meaning the engine has two code paths: one for TQIT-compiled maps (handles 0x0a) and one for TQAE-compiled maps (expects 0x0b)
3. **The map-level format (v0x0e vs v0x11, 0x0a vs 0x0b) determines which code path the engine uses** — and in a TQAE-compiled base map (SVAERA), it uses the TQAE code path which doesn't understand 0x0a
4. **BoatDialog's "lightweight" loading partially bypasses this** — enough to render geometry but not enough for pathfinding

## Hypothesis: The "Wrong MapCompiler" Diagnosis is Correct

Your earlier suggestion about the "wrong MapCompiler" bug now has strong experimental confirmation:

- In a TQAE-compiled map: the engine uses TQAE code paths → expects 0x0b → SV's 0x0a causes crash (streaming) or no-movement (BoatDialog)
- In a TQIT-compiled map (standalone SV): the engine uses TQIT code paths → reads 0x0a → works fine
- The difference is NOT in the blobs themselves but in HOW the engine processes them based on the map's compilation context

**The only thing that changes between a working SVAERA blob and a failing SV blob (for the same level geometry) is 0x0a vs 0x0b.** All other sections (0x05, 0x06, 0x09, 0x14, 0x17) are byte-identical.

## What We Need to Solve This

The core problem: **SV levels have 0x0a (PTH\x04, TQIT pathfinding) but the TQAE engine in a TQAE-compiled map requires 0x0b (REC\x02, TQAE pathfinding).**

### Ruled Out Solutions

1. **Programmatic 0x0a→0x0b conversion** — INFEASIBLE. Formats are fundamentally different (serialized object graph vs compiled binary nav mesh). Would require full reverse-engineering of both formats.

2. **MapCompiler recompilation** — DOES NOT WORK. MapCompiler passes through pathfinding sections from the .lvl source file. It does not generate 0x0b; only the TQAE Editor does.

3. **0x0b transplant from donor levels** — DOES NOT WORK (approach 8). Nav mesh must match actual level geometry.

### Remaining Viable Solutions

#### A. TQAE Editor Batch Re-Save (Most Promising)
Open each of the 46 SV-only .lvl files in the TQAE Art Manager/Editor, re-save them to generate 0x0b sections, then use the updated .lvl files in the merge.

**Research needed:**
- Can the TQAE Art Manager be automated (scripted or macro'd) to open and re-save levels?
- What exactly does "re-save" do? Does it require a full project setup?
- Can we use AutoHotkey or similar to script the Editor GUI for 46 levels?

#### B. Force TQIT Engine Code Path for the Entire Map
If the engine decides which code path to use based on a map-level flag, we could force "TQIT mode" for the merged map. Standalone SV works on TQAE, proving the engine CAN read 0x0a.

**Research needed:**
- What flag/header tells the engine this is a "TQAE-compiled map"?
- Is it the MAP file header, the WRL format, the presence of v0x11 blobs, or something else?
- If SVAERA levels need 0x0b code path but SV levels need 0x0a code path, can we have both?

#### C. Per-Level Code Path Selection
If the engine decides per-level based on version byte or section presence, we might force SV levels to use the TQIT code path while SVAERA levels use TQAE.

**Research needed:**
- Does the LVL version byte (0x0d/0x0e/0x11) affect which pathfinding code path is used?
- Would setting SV blobs to a specific version make the engine read 0x0a correctly?

#### D. Reverse-Engineer REC\x02 Format and Build a Converter
Last resort. Would require:
- Full parse of PTH\x04 to extract the navigation mesh topology
- Understanding of REC\x02's RLTD sub-record structure, vertex layout, spatial indices
- Building a converter that transforms the topology into compiled nav mesh
- This is essentially reimplementing part of the TQAE Editor

## Raw Data for Your Analysis

### Known-Good SVAERA Level (RuinedCity02, idx 30)
```
fname: Levels/World/Greece/Area004/RuinedCity02.LVL
ints_raw: [64, -15, 64, 64, 65, 64, -8212, 0, -320, 1302983333, -284865266, -1638047553, 540141701]
GUID[9..12]: [1302983333, -284865266, -1638047553, 540141701]
Grid: (-8212, 0, -320), Dims: (64, 64)
Blob sections (SVAERA): [0x05, 0x14, 0x06, 0x09, 0x0b, 0x17]  (270 KB)
Blob sections (SV):     [0x05, 0x14, 0x06, 0x09, 0x0a, 0x17]  (209 KB)
```

### Known-Good SVAERA Level (ArcadiaDungeonPassage, idx 973)
```
fname: XPack2/Levels/Corinthia/Underground/ArcadiaDungeonPassage.lvl
ints_raw: [80, 4, 120, 80, 4, 120, -6432, 0, -1053, 326550179, -221363848, -1805162794, 2093026269]
GUID[9..12]: [326550179, -221363848, -1805162794, 2093026269]
Grid: (-6432, 0, -1053), Dims: (80, 120)
```

### Known-Good SVAERA Level (last index 2234)
```
fname: XPack4/Levels/Special/Greece_HelosShrineInterior03.lvl
ints_raw: [40, 4, 40, 40, 4, 40, -6743, 0, 1334, -855939112, 330648579, -1697402561, 1555274572]
GUID[9..12]: [-855939112, 330648579, -1697402561, 1555274572]
Grid: (-6743, 0, 1334), Dims: (40, 40)
```

### Failing SV-Only Level (bc_initialpathway)
```
fname: Levels/World/xBloodCave/bc_initialpathway.lvl
Grid (original): (-2101, 18, 1293), shifted to: (-438, 18, 2215)
Dims: (40, 24)
Blob sections: [0x05, 0x14, 0x06, 0x09, 0x0a, 0x17]
```

### Failing SV-Only Levels (sample)
```
sv_only[0]: XPack/Levels/Secret_Place/BehindtheSP.lvl
  GUID[9..12]: [-1738583166, 1813857476, -1650962237, -50257884]
  Grid: (-2199, 0, -6182), Dims: (60, 60)

sv_only[1]: XPack/Levels/Secret_Place/DarkForestEnter.lvl
  GUID[9..12]: [-406284525, 1360021844, -1665216068, 789175748]
  Grid: (-2420, 0, -5820), Dims: (64, 64)
```

## Confirmed Conclusions

1. **No append-registration gate** — appended SVAERA levels work at indices beyond 2234 (approach 15).
2. **Direct 0x0a→0x0b conversion is not the near-term path** — formats are fundamentally different (approach 17).
3. **0x0a-only SVAERA levels are all non-walkable** — 3 harbor/water tiles, 18 borders/backdrops (approach 18). Every walkable SVAERA level has 0x0b.
4. **TQAE Editor renders black screen** — cannot display any world (tried SV WRL, SVAERA WRL, minimal WRL). The rendering pipeline fails silently. Per-level pathfinding rebuild requires the Editor to render terrain, which it cannot do (approach 19).
5. **pathengine.dll cannot be called from Python** — 32-bit DLL, C++ vtable API, needs TOK format input that only Engine.dll can generate (approach 19b).
6. **Layout Mode "Rebuild All Paths" only updates world01.sd** — upgraded SD from v6→v7, but did NOT modify any .lvl files. Per-level nav mesh generation is a separate operation that requires the Editor to load terrain.

## Current Priority: Generate 0x0b Pathfinding for SV Levels

### STATUS: Editor GUI approach is BLOCKED. Need alternative path to generate 0x0b.

The Editor-based approach (approach 19) failed because the TQAE Editor shows a black screen and cannot render terrain. Without rendering, it cannot generate per-level nav meshes. We confirmed the Editor CAN update the world-level SD file (v6→v7 upgrade), but individual .lvl files are untouched.

### Next Steps (Ordered by Feasibility)

#### 1. Fix Editor Rendering (Unblock Approach 19)
The Editor black screen may be fixable. Investigate:
- **Missing Visual C++ redistributables or DirectX runtime** — Editor uses Direct3D for rendering
- **GPU/driver compatibility** — Editor.exe is 32-bit, may need specific D3D9 settings
- **Run as administrator** — may need elevated permissions for D3D initialization
- **Windows compatibility mode** — try Windows 7/8 compatibility on Editor.exe
- **Check if other TQAE Editor users have this issue** — search TQ modding forums (titanquest.net, TQ-DB.net, Steam community)
- **Tools.ini `defaultMod=Art_TQX3`** — this mod doesn't exist; might cause issues. Try removing it or changing to PathingTest.

If the Editor can be made to render, the existing setup (SVAERA world + SV RuinedCity02) is ready for the proof test.

#### 2. Build a 32-bit C++ PathEngine Shim (Approach 20)
Write a small 32-bit C++ executable that:
1. Loads pathengine.dll
2. Reads ground mesh geometry (need to figure out TOK format or extract it from .lvl terrain data)
3. Calls `iPathEngine::loadMeshFromBuffer()` + `iMesh::generatePathfindPreprocessFor()` + `iMesh::savePathfindPreprocessFor()`
4. Writes the serialized 0x0b data to stdout/file

**Requirements:**
- 32-bit C++ compiler (MSVC Build Tools or MinGW-w32)
- PathEngine 5.01.01 SDK headers (available at github.com/sigmaco/pathengine)
- Understanding of TOK mesh format (tokenized XML used by PathEngine)
- Understanding of how Engine.dll's `PathMeshCompiler` converts TQ region geometry to TOK

**Key challenge:** Extracting terrain geometry from .lvl files in the TOK format that pathengine.dll expects. Engine.dll's `PathMeshCompiler::GetTokBuffer()` does this conversion, but it's deep in Engine.dll's C++ internals.

#### 3. Reverse-Engineer Engine.dll Code Path Selection (Approach 21)
Instead of generating 0x0b, figure out what makes the engine use TQIT code path (reads 0x0a) vs TQAE code path (reads 0x0b). Standalone SV works on TQAE, proving the TQIT code path exists and works.

**Research targets:**
- What header/flag in the .map file tells the engine which code path to use?
- Is it the MAP version, the SD version, presence of v0x11 blobs, or something else?
- Can we set a flag to force TQIT code path for specific levels or the whole map?
- Key functions to investigate: `GAME::Level::Load` (crashes during world streaming with SV blobs), `PathFinder` singleton

**Tools:** IDA Free / Ghidra for Engine.dll + Game.dll disassembly. The crash at `GAME::Level::Load + 1424 bytes` during approach 14 (world streaming crash) gives a concrete starting point.

#### 4. Use PathEngine SDK Source (Approach 22)
Clone github.com/sigmaco/pathengine, build from source (possibly 64-bit), create a standalone tool that generates nav meshes from terrain data. This avoids the 32-bit constraint and vtable hacking.

### Do NOT Spend More Time On
- DATA2/BITMAPS analysis
- Section 0x10 analysis
- Donor 0x0b transplants
- Direct 0x0a→0x0b binary conversion (without pathengine.dll)
- Append/index theories
- Trying different WRL files in the Editor (we tried 3 variants, all black)

## Questions for Research (Updated — Answered Questions Marked)

1. ~~**PTH\x04 format**~~: **ANSWERED.** Object graph with named string fields. See `tools/analyze_pathfinding_sections.py`.
2. ~~**REC\x02 format**~~: **ANSWERED.** Compiled binary nav mesh with RLTD sub-records. See `tools/analyze_pathfinding_sections.py`.
3. ~~**0x0a -> 0x0b conversion**~~: **ANSWERED. INFEASIBLE** without pathengine.dll. Formats are fundamentally different.
4. ~~**TQAE MapCompiler CLI**~~: **ANSWERED.** Does NOT convert 0x0a→0x0b — just passes through.
5. ~~**21 SVAERA levels without 0x0b**~~: **ANSWERED.** All non-walkable (3 harbor/water, 18 borders/backdrops). Every walkable SVAERA level has 0x0b.
6. **AE Editor normalization**: **BLOCKED.** Editor shows black screen — cannot render terrain to generate per-level nav meshes. Layout Mode "Rebuild All Paths" only updates SD, not .lvl files. Need to fix Editor rendering first.
7. **AE Editor automation**: **BLOCKED** until Editor rendering works.
8. **Engine code path selection**: **NOW HIGH PRIORITY.** How does Game.dll decide TQIT vs TQAE code paths? The crash at `GAME::Level::Load + 1424 bytes` (approach 14, world streaming) is a concrete entry point for reverse engineering.
9. **PathEngine**: TQ uses PathEngine 5.01.01 for navigation. The DLL has 8 exports, all C++ vtable-based. The API flow would be: `GetIPathEngine()` → `loadMeshFromBuffer("tok", ...)` → `generatePathfindPreprocessFor(shape)` → `savePathfindPreprocessFor(shape, stream)`. **Blocker:** Need TOK-format input which only Engine.dll's `PathMeshCompiler` can generate.
10. **Editor black screen root cause**: Why does the TQAE Editor show a black viewport with ANY world file? Is it a D3D9 init issue, missing dependencies, GPU compatibility, or something else? Search TQ modding forums for known issues.
11. **TOK mesh format**: PathEngine's tokenized XML mesh format — can we extract terrain geometry from .lvl files and convert to TOK? This would unblock the pathengine.dll shim approach.

## WRL File Format (Discovered During Approach 19)

Both SV and SVAERA use identical WRL version 7 format:

### Header
- Magic: `WRL\x07` (4 bytes)
- Num world regions: uint32
- Level index end offset: uint32
- Total level count: uint32

### Level Entries (variable-length)
- `name_len` (uint32) + `lvl_name` (N bytes ASCII)
- 13 metadata uint32s (52 bytes) — same `ints_raw` as in compiled MAP format
- `dbr_len` (uint32) + `dbr_path` (M bytes ASCII)

### Post-Entry Sections
1. **Quests** — marker `0x1B` + data_size + count + quest path entries
2. **Groups/Regions** — total_size + unknown=0 + count + group entries
3. **Raw level data** — terrain/grid tile data

### Companion File: world01.sd
| Field | SV | SVAERA |
|-------|-----|--------|
| Format version | 2 | 2 |
| SD version | 6 (TQIT) | 7 (TQAE) |
| Num acts | 1 | 3 |
| Num regions | 213 | 387 |

### Key Differences SV vs SVAERA WRL
- SV: 1004 levels (Levels/ + XPack/ only)
- SVAERA: 2235 levels (Levels/ + XPack/ + XPack2/ + XPack3/ + XPack4/)
- 594/956 common levels have different `meta[4]` values (differ by +20)
- SV has 191 quests, SVAERA has 254
- SV has 548 groups, SVAERA has 889
- Format is structurally identical — problem is content, not version

## Technical Environment
- Game: Titan Quest Anniversary Edition (TQAE), Steam version
- Mode: Custom Quest
- Map file: world01.map inside Levels.arc (ARC archive)
- Map size: ~2 GB (within int32 limits)
- Level count: 2281 (2235 SVAERA + 46 SV-only)
- Key executables: `Editor.exe`, `ArtManager.exe`, `MapCompiler.exe`, `pathengine.dll` (all in TQAE install dir)
