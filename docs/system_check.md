# System Check Report

Generated: 2026-02-20 (updated after first working deployment)

## Windows System

| Item | Status | Path |
|------|--------|------|
| Windows user | OK | `willi` |
| Documents folder | OK | `C:\Users\willi\OneDrive\Documents` (OneDrive redirect) |
| TQ IT docs base | OK | `...\OneDrive\Documents\My Games\Titan Quest - Immortal Throne` |
| CustomMaps folder | OK | `...\Titan Quest - Immortal Throne\CustomMaps` |
| TQAE install | OK | `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition` |
| ArchiveTool.exe | OK | In TQAE root (handles .arc files, supports -list) |
| ArtManager.exe | OK | In TQAE root (GUI tool) |
| Workshop (475150) | OK | 1 mod (SVAERA_customquest, ID 2076433374) |
| Python 3.12 | OK | `C:\Users\willi\AppData\Local\Programs\Python\Python312\python.exe` |
| Git | OK | `C:\Program Files\Git\cmd\git.exe` |
| SteamCMD | MISSING | Needed later for Workshop upload |
| 7-Zip | MISSING | Optional |

## Current Working Deployment

**Status: PLAYABLE** -- character can move, world renders, game is functional.

| Component | Source | Size | Notes |
|-----------|--------|------|-------|
| SoulvizierClassic.arz | Built by `arz_build_delta.py` | 26.3 MB | 17,351 SV-only records (no base game overrides) |
| Levels.arc | **SVAERA** reference mod | 631.3 MB | Contains AE-compatible world01.map |
| 42 other .arc files | Upstream Soulvizier 0.98i | ~540 MB | Textures, meshes, sounds, UI, etc. |
| **Total** | | **1,171.5 MB** | 44 files in CustomMaps |

## Key Technical Findings

### .arz Format
1. The original Soulvizier 0.98i `database.arz` is **already in TQAE format** (magic=4, version=3). Not TQIT format as initially assumed.
2. It contains **51,186 records** -- a full database replacement, not an overlay.
3. Of those, **33,835 records** share names with AE base game records (overrides), and **17,351** are SV-unique additions.
4. The AE base game has **74,013 records** (22,827 more than SV, including all DLC content and AE-specific additions).

### .arz Compatibility Issue
5. Deploying the full 51K-record .arz as a Custom Quest overlay **did not crash** (after the initial incident), but **broke player movement**. The player could see the world and open UI, but clicking to move did nothing.
6. Removing game engine records (gameengine.dbr, CombatEquations, etc.) did **not** fix movement.
7. Using only SV-unique records (zero base game overrides) did **not** fix movement.
8. **Conclusion**: The movement issue was NOT caused by .arz database records.

### Levels.arc / world01.map Compatibility
9. **ROOT CAUSE FOUND**: The upstream Soulvizier `Levels.arc` (282 MB) contains a `world01.map` built for the original TQIT engine. AE can render the map but **cannot use its pathfinding/navigation data**, resulting in a character that appears in the world but cannot move.
10. Replacing the upstream `Levels.arc` with SVAERA's version (631 MB, built for AE) **fixed movement completely**.
11. Both Levels.arc files contain exactly one entry: `world/world01.map` (verified via ArchiveTool -list).

### SVAERA Reference Mod Structure
12. SVAERA's `.arz` file is actually an **empty .arc file** (starts with "ARC\0" magic bytes, 2,048 bytes). It contains zero database records.
13. SVAERA delivers ALL content through `.arc` resource files. This means .arc archives can contain .dbr records that the game loads at runtime.
14. SVAERA's approach completely avoids .arz compatibility issues.

### .arc File Compatibility
15. The DRX* and SV* .arc files are **byte-identical** between upstream Soulvizier 0.98i and SVAERA. These are safe on AE.
16. Upstream-only .arc files (UI overrides like menu.arc, InGameUI.arc, etc.) do **not** crash AE when loaded.
17. The only problematic .arc file was `Levels.arc` due to the old map format.

### First Deployment Crash (Resolved)
18. The very first deployment attempt (full .arz + all .arc files) crashed TQAE on startup with a C++ Runtime Error. After reinstalling TQAE, the same combination loaded without crashing. The initial crash may have been caused by a corrupted game state or OneDrive sync interference.

## Python Tooling Built

| Tool | Purpose |
|------|---------|
| `tools/arz_converter.py` | Read/convert .arz between TQIT and TQAE formats |
| `tools/arz_extract.py` | Extract .dbr records from .arz to text files for diffing |
| `tools/arz_build_delta.py` | Build a delta .arz containing only changed/new records |

## Action Items

- [x] Obtain Soulvizier 0.98i original archive
- [x] Extract upstream into `upstream/soulvizier_098i/`
- [x] Install Python 3.12
- [x] Build .arz toolchain (extract, compare, delta build)
- [x] Identify and fix movement issue (Levels.arc from SVAERA)
- [x] Achieve first playable deployment
- [ ] Determine optimal .arz strategy (SV-only vs carefully curated overrides)
- [ ] Test gameplay: masteries, skills, monsters, souls, drop rates
- [ ] Implement Super Caravan features
- [ ] Audit missing souls content
- [ ] Ensure Blood Cave accessibility
- [ ] Multiplayer testing
- [ ] Package for Workshop upload
