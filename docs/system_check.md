# System Check Report

Generated: 2026-02-20

## Windows System

| Item | Status | Path |
|------|--------|------|
| Windows user | OK | `willi` |
| Documents folder | OK | `/mnt/c/Users/willi/OneDrive/Documents` (OneDrive redirect) |
| TQ IT docs base | OK | `.../OneDrive/Documents/My Games/Titan Quest - Immortal Throne` |
| CustomMaps folder | MISSING | Will create on first deploy |
| Working folder | MISSING | Will create if ArtManager needs it |
| TQAE install | OK | `/mnt/c/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition` |
| ArchiveTool.exe | OK | In TQAE root (handles .arc only; must use PowerShell with Windows paths) |
| ArtManager.exe | OK | In TQAE root (GUI only) |
| Workshop (475150) | OK | 1 mod installed (SVAERA_customquest, ID 2076433374) |
| SteamCMD | MISSING | Not installed yet (needed for Workshop upload later) |

## TQAE Install Contents

- `TQ.exe` - game executable
- `Database/database.arz` - base game database
- `Resources/` - 21 .arc resource archives (Creatures, Effects, Items, Levels, etc.)
- Full modding toolset: ArtManager, Editor, QuestEditor, MapCompiler, etc.
- `WorkshopTool/TQITWorkshopTool.exe` - GUI workshop uploader
- `Toolset/` - Modders guide, templates, tutorials

## SVAERA_customquest Reference Mod (Workshop ID 2076433374)

Structure:
```
SVAERA_customquest/
  Database/
    SVAERA_customquest.arz
  Resources/
    A Few Bug Fixes.arc
    Creatures.arc
    DRXeffects.arc, DRXsounds.arc, DRXtextures.arc
    Items.arc
    Levels.arc
    N66_Mods.arc
    Quests.arc
    SVEffects.arc, SVItems.arc, SVMesh.arc, SVSounds.arc, SVTextures.arc
    SV_NewSkins.arc
    Text.arc
    XPack2.arc, XPack3.arc, XPack4.arc
    Xpack/Items.arc
    _DRX_Effects.arc, _DRX_Meshes.arc, _DRX_Textures.arc
    drx.arc
  Optional/
    4gb_patch.exe
    Language packs (German, French, Russian, Chinese)
  changelog_v_1_14a.pdf, changelog_v_1_14b.pdf
  Installation v1.13_Custom_quest_version_manual - same for 1.14.pdf
```

Key observations:
- No .map files (Custom Quest with database + resource overrides only)
- Uses XPack2/3/4 resource archives (Ragnarok, Atlantis, Eternal Embers content)
- Includes DRX effects/textures (visual overhaul)
- Has Text.arc for custom strings

## WSL2 Tools

| Tool | Status |
|------|--------|
| unzip | OK |
| 7z (p7zip-full) | MISSING |
| rsync | OK |
| python3 (3.12) | OK |
| pip3 | OK |
| dos2unix | MISSING |

## Critical Findings

1. **ArchiveTool path limitation**: WSL paths (`/mnt/c/...`) do not work with ArchiveTool.exe. Must invoke via PowerShell with native Windows paths.
2. **No .arz CLI tool**: ArchiveTool handles .arc only. For .arz extraction/building, we need either ArtManager (GUI) or a community tool.
3. **OneDrive Documents**: Documents folder is synced via OneDrive. This is fine but the path differs from default.
4. **No CustomMaps folder yet**: First deploy will need to create it.

## Action Items

- [ ] User: `sudo apt install p7zip-full dos2unix`
- [ ] Find or build a .arz extraction tool (Python community tools exist)
- [ ] Install SteamCMD when ready for Workshop upload
- [ ] Create helper scripts that invoke Windows .exe tools via PowerShell
