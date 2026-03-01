# Changelog

## 2026-02-20

### First Playable Deployment

After extensive debugging, the mod is now playable as a Custom Quest in TQAE.

**Working configuration:**
- `SoulvizierClassic.arz`: 26.3 MB delta containing only the 17,351 records unique to Soulvizier (no base game overrides)
- `Levels.arc`: Sourced from SVAERA reference mod (631 MB, AE-compatible world01.map)
- All other .arc files: From upstream Soulvizier 0.98i (textures, meshes, sounds, UI)
- Total deployed size: 1,171.5 MB (44 files)

### Debugging Timeline

1. **Full .arz deployment** -- Deployed the complete 51.9 MB upstream database.arz (renamed). Game loaded but player could not move.
2. **Excluded game engine records** -- Built delta .arz removing gameengine.dbr, CombatEquations, and related DRX records. Still no movement.
3. **SV-only records** -- Built delta .arz with zero base game overrides (17,351 records). Still no movement.
4. **Identified root cause** -- The upstream Soulvizier `Levels.arc` (282 MB) contains a TQIT-era `world01.map`. AE can render it but cannot use its pathfinding data.
5. **Swapped Levels.arc** -- Replaced with SVAERA's AE-compatible `Levels.arc` (631 MB). **Movement works.**

### Python Tooling

- Created `tools/arz_extract.py` -- extracts .dbr records from .arz to text files
- Created `tools/arz_build_delta.py` -- builds a delta .arz containing only records that differ from AE base game
- Created `tools/arz_converter.py` -- reads/converts .arz format (TQIT vs TQAE)
- Fixed zlib decompression in arz_extract.py to handle multiple wbits strategies

### Key Findings

- The original Soulvizier 0.98i `database.arz` is already in TQAE format (magic=4, version=3)
- It contains 51,186 records total; 33,835 overlap with AE base; 17,351 are SV-unique
- AE base game has 74,013 records (includes DLC content SV doesn't have)
- SVAERA's .arz is actually an empty .arc file (2 KB) -- all content delivered via .arc resources
- The movement bug was caused by incompatible pathfinding in the old TQIT-era Levels.arc
- DRX* and SV* .arc files are byte-identical between upstream SV 0.98i and SVAERA

### Project Setup (Windows Native)

- Migrated development from WSL2 to native Windows with PowerShell scripts
- Created `scripts/doctor.ps1` — detects system paths, writes `local/config.env`
- Created `scripts/_common.ps1` — shared config loader for all scripts
- Created `scripts/sync_reference_mods.ps1` — copies Workshop mods for reference
- Created `scripts/import_upstream_soulvizier.ps1` — extracts upstream archive
- Created `scripts/bootstrap_working_mod.ps1` — creates working mod tree
- Created `scripts/deploy_to_custommaps.ps1` — deploys mod for testing
- Ran doctor: all critical checks pass, TQAE and tools located
- Synced SVAERA_customquest reference mod (1.7 GB, 34 files)
- Updated README.md for Windows-native workflow
