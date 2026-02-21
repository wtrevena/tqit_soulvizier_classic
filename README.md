# tqit_soulvizier_classic

## Purpose

Create and publish a Titan Quest Anniversary Edition Custom Quest mod called **SoulvizierClassic**.

This project ports and completes the **original Soulvizier 0.98i (Immortal Throne era)** design philosophy, while running on **Titan Quest Anniversary Edition (AE)** for stable multiplayer via Steam.

The mod must preserve the classic scope and feel.

* Campaign scope: Acts I through IV only, ending at Hades, plus original Soulvizier extras like Blood Cave and other classic secret content.
* Gameplay feel: Souls broadly usable, high drop frequency similar to original Soulvizier 0.98i.
* Avoid the Steam fork behavior the user dislikes, meaning no aggressive nerfs, no extreme stat requirements, no low soul drop rates, no removal of Blood Cave.
* Multiplayer: must work as a Custom Quest mod in AE so friends can join if they have the same mod version.

This repository is developed using Cursor Agent in WSL2, while deploying and testing on Windows 11.

## Current system state

On this Windows 11 PC:

* Steam is installed.
* Titan Quest Anniversary Edition is installed.
* The user can already see at least one installed Custom Quest mod: `SVAERA_customquest` and a map `world01.map` is present.
* WSL2 is installed and Cursor will operate inside WSL2 while editing files located on the Windows drive via `/mnt/c/...`.
* A GitHub repo already exists, named `tqit_soulvizier_classic`.

## Non negotiable constraints

* Do not modify Titan Quest base game install files under `steamapps/common/...`.
* Do not rely on manual GUI editing by the user.
* Edits are done as text edits on extracted records and assets using Cursor.
* Build and deployment must be triggered by scripts.
* Always back up anything before overwriting it, especially anything under Documents and CustomMaps.
* Treat Steam Workshop downloaded mods as read only reference sources. Copy them into repo reference folders instead of editing them in place.

Important note about compilation:
* ArchiveTool can extract .arz and .arc, but it is not a reliable way to build .arz from CLI.
* If a pure CLI .arz builder cannot be found, use the official mod toolchain for the build step only.
* The user does not want to manually interact with any GUI, so if ArtManager is required, automate it using a Windows side script.

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

## Required installations in WSL2

Install baseline utilities:

* `unzip`, `p7zip-full`, `rsync`, `python3`, `python3-pip`, `dos2unix`

## Scripts to implement

### scripts/doctor.sh

Goal:
Detect all key paths, validate prerequisites, and write a config file at `local/config.env`.

Responsibilities:

* Determine Windows username via `cmd.exe /c echo %USERNAME%` or PowerShell.
* Determine CustomMaps path under Documents.
* Locate Titan Quest AE install folder.
  * Search common locations under `/mnt/c/Program Files (x86)/Steam/steamapps/common/`.
  * Also parse `libraryfolders.vdf` to find alternate Steam libraries if needed.
* Locate Workshop folder for app id 475150.
* Locate `ArchiveTool.exe` inside the TQAE install folder if present.
* Locate `ArtManager.exe` inside the TQAE install folder if present.
* Locate SteamCMD at `C:\steamcmd\steamcmd.exe`.

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

Exit nonzero if the game install path or CustomMaps path cannot be found.

### scripts/sync_reference_mods.sh

Goal:
Copy installed Workshop mod folders into `reference_mods/` for analysis.

Minimum:
* Copy `SVAERA_customquest` if present.
* Do not modify the workshop folder.

Implementation approach:
* Search under `STEAM_WORKSHOP_475150` for a directory named `SVAERA_customquest`.
* Copy it into `reference_mods/SVAERA_customquest/` using `rsync -a`.
* Write `docs/reference_mods.md` summarizing what was copied and where it came from.

### scripts/import_upstream_soulvizier.sh

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

### scripts/bootstrap_working_mod.sh

Goal:
Create our working mod tree for SoulvizierClassic under `work/SoulvizierClassic/`.

Responsibilities:
* Create `work/SoulvizierClassic/database/`
* Create `work/SoulvizierClassic/resources/`
* Create `work/SoulvizierClassic/maps/` if needed.

Then copy upstream compiled artifacts into the working mod as a baseline:

* Copy upstream `database/*.arz` into `work/SoulvizierClassic/database/` and rename to `SoulvizierClassic.arz`.
* Copy upstream `resources/*.arc` into `work/SoulvizierClassic/resources/`.
* Copy upstream map files into `work/SoulvizierClassic/maps/` if present.

Important:
* The `.arz` file name should match the mod folder name to avoid confusion at runtime.

### scripts/extract_working_database.sh

Goal:
Extract the working `.arz` into editable `.dbr` records.

Responsibilities:
* Use `ArchiveTool.exe` if available to extract `.arz` with `-database` into:
  * `work/SoulvizierClassic/database/records/`
* If ArchiveTool cannot extract, fall back to a dedicated ARZ extractor tool, and document it in the repo.

Output:
* Editable records in `work/SoulvizierClassic/database/records/...`.

### scripts/build_database.sh

Goal:
Rebuild `SoulvizierClassic.arz` from edited `.dbr` records.

Important reality:
* If a pure CLI rebuild tool is not available, the build must use the official mod toolchain.

Approach hierarchy:
1. If a reliable CLI `.arz` builder is present, use it.
2. Otherwise, automate ArtManager build on Windows.

If ArtManager build automation is required:
* Create `scripts/win_artmanager_build.ps1` that:
  * Launches ArtManager.
  * Ensures Tools, Working, Build directories are configured.
  * Loads mod `SoulvizierClassic`.
  * Triggers Build.
  * Waits for completion.
  * Exits cleanly.
* If ArtManager cannot be controlled without manual intervention, implement UI automation using a Windows Python script under `scripts/win_artmanager_build.py` using `pywinauto`.

The user must not be required to click anything.

### scripts/deploy_to_custommaps.sh

Goal:
Deploy the built mod into the user CustomMaps folder so they can test.

Responsibilities:
* Before copying, back up any existing deployed folder:
  * `C:\Users\<USER>\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic`
  * Copy it to `backups/deployed/SoulvizierClassic/<timestamp>/`
* Deploy the mod folder into CustomMaps:
  * Copy `work/SoulvizierClassic/` or `build/SoulvizierClassic/` depending on build method.
* Confirm that `database/SoulvizierClassic.arz` exists in deployed folder.

### scripts/package_workshop.sh

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

### scripts/upload_workshop.sh

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

## Immediate next actions for the agent

1. Implement the directory structure and `.gitignore`.
2. Implement `scripts/doctor.sh` and run it.
3. Implement `scripts/sync_reference_mods.sh` and copy `SVAERA_customquest`.
4. Implement `scripts/import_upstream_soulvizier.sh` using the Soulvizier 0.98i archive in `third_party/`.
5. Implement `scripts/bootstrap_working_mod.sh`.
6. Implement `scripts/extract_working_database.sh`.
7. Decide build approach for `.arz`:
   * Attempt to find a reliable CLI builder.
   * If not found, implement ArtManager build automation that does not require user interaction.
8. Implement deploy script and complete first smoke test.
9. Only after baseline works, start “missing souls” audit and super caravan edits.