# tqit_soulvizier_classic

## Purpose

Create and publish a Titan Quest Anniversary Edition Custom Quest mod called **SoulvizierClassic**.

This project ports and completes the **original Soulvizier 0.98i (Immortal Throne era)** design philosophy, while running on **Titan Quest Anniversary Edition (AE)** for stable multiplayer via Steam.

The mod must preserve the classic scope and feel.

* Campaign scope: Acts I through IV only, ending at Hades, plus original Soulvizier extras like Blood Cave and other classic secret content.
* Gameplay feel: Souls broadly usable, high drop frequency similar to original Soulvizier 0.98i.
* Avoid the Steam fork behavior the user dislikes, meaning no aggressive nerfs, no extreme stat requirements, no low soul drop rates, no removal of Blood Cave.
* Multiplayer: must work as a Custom Quest mod in AE so friends can join if they have the same mod version.

This repository is developed using Cursor Agent natively on Windows 11 with PowerShell scripts.

## Current system state

On this Windows 11 PC:

* Steam is installed.
* Titan Quest Anniversary Edition is installed.
* The user can already see at least one installed Custom Quest mod: `SVAERA_customquest` and a map `world01.map` is present.
* Development is done natively on Windows using Cursor and PowerShell.
* A GitHub repo already exists, named `tqit_soulvizier_classic`.

## Non negotiable constraints

* Do not modify Titan Quest base game install files under `steamapps/common/...`.
* Do not rely on manual GUI editing by the user.
* Edits are done as text edits on extracted records and assets using Cursor.
* Build and deployment must be triggered by scripts.
* Always back up anything before overwriting it, especially anything under Documents and CustomMaps.
* Treat Steam Workshop downloaded mods as read only reference sources. Copy them into repo reference folders instead of editing them in place.

Important note about compilation:
* ArchiveTool handles .arc files only (list/extract). It does NOT handle .arz.
* We built custom Python tools for .arz manipulation: `tools/arz_extract.py`, `tools/arz_build_delta.py`, `tools/arz_converter.py`, `tools/arz_patcher.py`, `tools/build_svc_database.py`.
* The current build pipeline loads SV 0.98i, patches it with SoulvizierClassic changes, and writes a fully patched .arz.
* No GUI interaction (ArtManager) is required for the current workflow.

## Definitions

* Repo root: The folder returned by `git rev-parse --show-toplevel`.
* Windows CustomMaps folder: `C:\Users\<USER>\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps`
* Windows Working folder for mod tools: `C:\Users\<USER>\Documents\My Games\Titan Quest - Immortal Throne\Working`
* Steam Workshop folder for TQAE: `<SteamLibrary>\steamapps\workshop\content\475150\`

## High level workflow

1. Discover system paths and write them into a local config file.
2. Import upstream Soulvizier 0.98i source into an upstream folder.
3. Copy reference mods from Workshop into a reference folder for inspection.
4. Maintain our mod working tree in the repo, editable by Cursor.
5. Build into a repo build output directory.
6. Deploy build output into Windows CustomMaps for the user to test.
7. Back up previous deployed version every time.
8. Package for Workshop.
9. Upload to Workshop using SteamCMD.

## Repository layout

Create and maintain these directories.

* `third_party/`
  * Place upstream zips here, including Soulvizier 0.98i original archive.
  * This folder is gitignored.
* `reference_mods/`
  * Copied from Steam Workshop for reference, including SVAERA_customquest.
  * This folder is gitignored.
* `upstream/`
  * Extracted Soulvizier 0.98i original contents, extracted from the archive.
  * This folder is gitignored.
* `work/`
  * Working mod tree that will be edited by Cursor and fed into the build.
  * This folder is tracked except for large generated artifacts.
* `overrides/`
  * Optional overlay folder for changes if we decide to keep upstream pristine.
  * If used, it is tracked.
* `build/`
  * Built CustomMaps output for SoulvizierClassic.
  * This folder is mostly gitignored except small metadata and scripts.
* `dist/`
  * Workshop staging artifacts and release zips.
  * This folder is gitignored.
* `backups/`
  * Timestamped backups of deployed CustomMaps folder before overwriting.
  * This folder is gitignored.
* `scripts/`
  * All automation scripts, tracked.
* `tools/`
  * Helper scripts for audits and generation, tracked.
* `docs/`
  * Design notes, tracked.

## Git ignore requirements

Add to `.gitignore`:

* `third_party/`
* `reference_mods/`
* `upstream/`
* `build/`
* `dist/`
* `backups/`
* `local/`

Keep only scripts, docs, and small deltas in Git. Do not commit copyrighted game data or large mod binaries.

## Required installations on Windows

Cursor Agent must verify these are present and install where missing.

1. SteamCMD, for workshop upload.
   * Expected path: `C:\steamcmd\steamcmd.exe`
   * If missing, install it.
2. Python on Windows, only if we need UI automation for ArtManager build.
   * Recommended: Python 3.11 or higher.
   * Required packages if used: `pywinauto`, `pywin32`.
3. Titan Quest Anniversary Edition is already installed, verify path.
4. 7-Zip for archive extraction (optional, `winget install 7zip.7zip`).

## Scripts to implement

### scripts/doctor.ps1

Goal:
Detect all key paths, validate prerequisites, and write a config file at `local/config.env`.

Responsibilities:

* Determine Windows username and Documents path (handles OneDrive redirect).
* Locate Titan Quest AE install folder via Steam library paths.
* Locate Workshop folder for app id 475150.
* Locate `ArchiveTool.exe` and `ArtManager.exe` inside the TQAE install folder.
* Locate SteamCMD if installed.

Write `local/config.env` with keys like:

* `WIN_USER=...`
* `WIN_DOCS=...`
* `WIN_CUSTOMMAPS=...`
* `WIN_WORKING=...`
* `TQAE_ROOT=...`
* `TQ_ARCHIVETOOL=...`
* `TQ_ARTMANAGER=...`
* `STEAM_WORKSHOP_475150=...`
* `STEAMCMD_EXE=...`
* `REPO_ROOT=...`

Exit nonzero if the game install path cannot be found.

### scripts/sync_reference_mods.ps1

Goal:
Copy installed Workshop mod folders into `reference_mods/` for analysis.

Minimum:
* Copy `SVAERA_customquest` if present.
* Do not modify the workshop folder.

Implementation approach:
* Search under `STEAM_WORKSHOP_475150` for a directory named `SVAERA_customquest`.
* Copy it into `reference_mods/SVAERA_customquest/`.
* Write `docs/reference_mods.md` summarizing what was copied and where it came from.

### scripts/import_upstream_soulvizier.ps1

Goal:
Import the original Soulvizier 0.98i archive from `third_party/` into `upstream/`.

Responsibilities:
* Locate Soulvizier 0.98i archive under `third_party/`.
* Extract it into `upstream/soulvizier_098i/`.
* Identify key artifacts inside the extracted mod:
  * `database/*.arz`
  * `resources/*.arc`
  * `maps/*.map` or similar
* Write `docs/upstream_inventory.md` listing what upstream contains.

### scripts/bootstrap_working_mod.ps1

Goal:
Create our working mod tree for SoulvizierClassic under `work/SoulvizierClassic/`.

Responsibilities:
* Create `work/SoulvizierClassic/Database/`
* Create `work/SoulvizierClassic/Resources/`

Build the mod from known-good sources:
* Build `SoulvizierClassic.arz` as a **delta** (SV-unique records only) using `tools/arz_build_delta.py`.
* Copy upstream `resources/*.arc` into `work/SoulvizierClassic/Resources/`.
* Replace `Levels.arc` with the AE-compatible version from SVAERA reference mod (critical for pathfinding).

Important:
* The `.arz` file name must match the mod folder name.
* The upstream `Levels.arc` (282 MB, TQIT-era) is NOT compatible with AE pathfinding. Must use SVAERA's version (631 MB).

### scripts/extract_working_database.ps1

Goal:
Extract the working `.arz` into editable `.dbr` records using `tools/arz_extract.py`.

Output:
* Editable records in `work/SoulvizierClassic/database/records/...`.
* Each .dbr is a text file with key=value pairs.

### scripts/build_database.ps1

Goal:
Rebuild `SoulvizierClassic.arz` from the delta build pipeline.

Approach:
1. Use `tools/arz_build_delta.py` to compare upstream SV records against AE base game.
2. Output only SV-unique or SV-modified records into the delta .arz.
3. No GUI or ArtManager interaction required.

### scripts/deploy_to_custommaps.ps1

Goal:
Deploy the built mod into the user CustomMaps folder so they can test.

Responsibilities:
* Before copying, back up any existing deployed folder:
  * `C:\Users\<USER>\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic`
  * Copy it to `backups/deployed/SoulvizierClassic/<timestamp>/`
* Deploy the mod folder into CustomMaps:
  * Copy `work/SoulvizierClassic/` or `build/SoulvizierClassic/` depending on build method.
* Confirm that `database/SoulvizierClassic.arz` exists in deployed folder.

### scripts/package_workshop.ps1

Goal:
Create a clean staging folder for Workshop upload at:
* `dist/workshop/SoulvizierClassic/`

Responsibilities:
* Copy exactly what should be shipped.
* Exclude backups, extracted records, and any dev only files.
* Include:
  * `database/SoulvizierClassic.arz`
  * `resources/*.arc`
  * `maps/*.map` if required for custom quest
  * `preview.jpg` and `workshop_description.txt` generated from docs

### scripts/upload_workshop.ps1

Goal:
Upload using SteamCMD with a VDF file.

Responsibilities:
* Create `dist/workshop/workshop.vdf` with:
  * appid 475150
  * contentfolder path
  * previewfile path
  * title, description
  * publishedfileid if updating an existing item
* Call SteamCMD.
* Save the workshop item id into `local/workshop_item_id.txt`.

## Super Caravan requirements

The user wants “Super Caravan” behavior.

Clarification:
* TQVault is an external tool, it cannot be embedded into the in game caravan UI.
* We implement equivalent quality of life inside the mod via database edits:
  * large player inventory
  * large stash and transfer space
  * early unlock from Act I start
  * optionally vendor sold respec items

Implementation tasks:

1. Inventory bags from start
   * Locate the records that gate bag unlocks.
   * Modify so all bags are unlocked at character creation or very early quest token.

2. Caravan stash expansion
   * Identify caravan UI and stash records in upstream Soulvizier.
   * Compare with SVAERA_customquest reference mod to see how it implements stash expansion.
   * Apply a stable approach that works in AE.

3. Transfer stash expansion
   * Expand transfer stash similarly.
   * Ensure multiplayer stability.

4. Respec items
   * Confirm original Soulvizier respec potions are present.
   * If missing, re add:
     * item record
     * vendor inventory record
     * text tags
   * Avoid adding any DLC dependent NPC.

Optional external companion:
* Document optional use of TQVaultAE for infinite offline storage in `docs/optional_tools.md`.
* This is not required for mod functionality.

## Content completion requirements

1. Souls coverage
   * Create souls for monsters that should have them but do not.
   * Do not introduce restrictive stat requirements.
   * Keep drop rates aligned with original Soulvizier feel.

2. Blood Cave and classic secrets
   * Ensure Blood Cave exists and is accessible.
   * Do not remove or nerf it.

3. Drop rates and balance
   * Do not adopt AERA nerfs.
   * Keep soul drops frequent.
   * Keep stat requirements reasonable.

4. End of game
   * No additional acts beyond Immortal Throne end.
   * Do not add Ragnarok, Atlantis, Eternal Embers regions.

## Testing checklist

After every meaningful change:

1. Build database.
2. Deploy to CustomMaps.
3. Launch TQAE, Play Custom Quest, SoulvizierClassic.
4. Smoke tests:
   * Create new character.
   * Verify masteries appear as expected for classic Soulvizier baseline.
   * Kill a hero monster, confirm souls drop behavior.
   * Open caravan, confirm no crash and expanded space.
   * Confirm Blood Cave access if applicable.

Multiplayer test milestones:

* First milestone: baseline port runs for two players.
* Second milestone: super caravan and souls additions still allow multiplayer join.
* Third milestone: release candidate on Workshop, friends subscribe and join.

## Cursor Agent operating rules

* Always read `local/config.env` for paths.
* Never hardcode a Windows username or Steam library path.
* Never modify the base game folder.
* Never edit Workshop download folders in place.
* All edits happen in `work/` and scripts produce deploy and dist output.
* Before overwriting deployed CustomMaps, create a timestamped backup.
* Commit small changes with clear messages.
* Keep a running changelog in `docs/CHANGELOG.md`.

## Progress

### Completed

1. ~~Directory structure and `.gitignore`~~ DONE
2. ~~`scripts/doctor.ps1` -- system detection and config~~ DONE
3. ~~`scripts/sync_reference_mods.ps1` -- copy SVAERA for reference~~ DONE
4. ~~`scripts/import_upstream_soulvizier.ps1` -- extract SV 0.98i~~ DONE
5. ~~`scripts/bootstrap_working_mod.ps1` -- create working mod tree~~ DONE
6. ~~`scripts/deploy_to_custommaps.ps1` -- deploy for testing~~ DONE
7. ~~Python .arz toolchain -- extract, delta build, format convert, patch~~ DONE
8. ~~First playable deployment achieved~~ DONE
9. ~~Full SV 0.98i .arz deployed (all game balance overrides)~~ DONE
10. ~~Mastery label fix: Rogue -> Occult in Text_EN.arc~~ DONE
11. ~~Potion drop rates restored from SV 0.9 (168 loot table weights)~~ DONE
12. ~~1,667 monsters wired to drop their matching soul items~~ DONE
    * 66% drop chance for rare/hero monsters, 25% for farmable bosses
    * Souls already had 0 stat requirements (str/int/dex) -- no change needed
13. ~~9,804 equipment items made enchantable (numRelicSlots=1)~~ DONE

14. ~~Map restoration: drxmap content (occultist merchant, demon sprites, pit sprites) restored~~ DONE
    * Hybrid v0x0e blob approach: SV's full 0x05 section + SVAERA's terrain/pathfinding
    * 9 shared levels surgically merged, 46 SV-only levels appended
    * Confirmed working in-game: merchant interactive, combat functional
15. ~~SkillsPanel.arc stripped (TQIT UI incompatible with AE)~~ DONE
16. ~~Character backup script updated to include Custom Quest saves (SaveData\User)~~ DONE

### Next actions

1. Implement Super Caravan features (expanded stash, bags, respec items)
2. Verify Blood Cave dungeon (xBloodCave) and Garden of Merchants are accessible via quest triggers
3. Multiplayer testing
4. Package and upload to Steam Workshop

17. ~~Uber Dungeon portal at Crisaeos Falls~~ DONE
    * NPC portal (Action_BoatDialog) placed near the demon sprites in DelphiLowlands04
    * Teleports player to crypt_floor1.lvl (Uber Dungeon) with Deathstalkers, Ghosts, Fell Minotaurs, golden chests
    * Return portal inside the Uber Dungeon back to Crisaeos Falls
    * Uber Dungeon connects onward to Boss Arena via existing portal_olympianarena2
    * Boss Arena quest (bossarena.qst) spawns Satyr Shaman boss on entry
    * Quest file builder: `tools/qst_format.py` (fully reverse-engineered .qst format, 89/89 round-trip verified)

### Future ideas

- **Dionyses' Trickster relic drop**: Add a unique relic drop (like the Magneta Shell) to Dionyses' Trickster
- **Pan's Guard relic drop**: Add a unique relic drop to Pan's Guard
- **Rakanizeus Soul overhaul**: Current auto-generated soul is underwhelming for an uber monster (only +20% run speed, some lightning damage, a pierce penalty). Needs a major buff -- add a lightning proc skill, massive speed/attack speed bonuses, and stats befitting an uber boss. Use Typhon/Hades souls as reference for stat density.
- **Mercenary scrolls everywhere**: Make all merc scrolls droppable in any act/difficulty instead of being locked to specific regions. Cascade availability: Normal scrolls also appear in Epic/Legendary tables, Epic scrolls also in Legendary. Currently Act 3 Normal only drops Skoneros, Act 4 Normal only Apollinia, etc.
- **Blood Mistress formula in loot tables**: The Blood Mistress upgrade is currently forge-only. Add the formula to boss loot tables or forge merchant inventory.
- **Blood Cave entrance audit**: The Blood Cave is accessed via the "Duister" NPC at the Garden of Merchants (triggered by quest `open_bloodcave_portal.qst`). Need to verify this quest chain works end-to-end in the AE port.
- **Quest gating**: Optionally gate the Uber Dungeon portal behind a quest condition (kill a boss, reach a certain point) instead of being always visible.
- **Paragon of Violence**: Not found in any SV database (0.4.1, 0.9, 0.98i). May be from a different mod or was never implemented in SV.

## Archive

The original plan assumed we'd need ArtManager or a CLI .arz builder. In practice, we built
custom Python tools that handle .arz reading, record extraction, field-level patching, and
writing fully patched .arz files. The build pipeline (`tools/build_svc_database.py`) loads
SV 0.98i as the base, compares with SV 0.9 to restore potion drop rates, wires 1,667+
soul-to-monster assignments, makes all equipment enchantable, and outputs a single patched .arz.
No GUI interaction is needed.
