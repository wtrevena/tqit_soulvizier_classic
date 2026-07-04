# Editor navmesh bake - exact GUI click-steps (computer-use session)

Goal: bake ONE real `0x0b` (REC\x02 / RLTD) Recast navmesh for **BC_initialpathway**
(blood-cave entrance) using the stock TQAE Editor, with terrain that actually
renders. This is the minimal repro that unblocks the 46 SV-only levels.

Prereqs already done at file level (do NOT redo):
- `Tools.ini` `additionalbuilddirs` = `<game install>;<CustomMaps\SoulvizierClassic>`
  (backup at `<TQ docs>\Tools.ini.bak-preEditorPrep`).
- Source tree created by `py tools/setup_bc_bake_tree.py` at
  `<TQ docs>\Working\CustomMaps\BCBake\source\` (mod name **BCBake**), with the
  full SV `world01.wrl`/`.sd` + every region/XPack dir junctioned, so
  BC_initialpathway's `.lvl`/`.rlv`/`.tga` and its 32 `drxmap\bloodcave` records
  resolve.

Paths:
- Editor:     `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Editor.exe`
- ArtManager: `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\ArtManager.exe`
- Mod:        `BCBake`
- World file: `Levels\World\world01.wrl` (open from the mod source, NOT from a `Maps\` folder)
- Level to bake: **BC_initialpathway** (region `xBloodCave`)

IMPORTANT computer-use note: the TQ tools are native apps -> granted at **full**
tier, so clicks/typing work. Take a `screenshot` before each decision. Do NOT
click any web links (none should appear).

---

## PHASE 1 - ArtManager: register + build the BCBake mod

The Editor needs the mod known to ArtManager and its assets built once so the
world/level compile pipeline is wired.

1. `open_application` Art Manager (`ArtManager.exe`).
2. If a mod is not already selected as BCBake: menu **Mod -> Set Mod...** (or the
   mod dropdown), choose **BCBake**. If BCBake is not listed, **Mod -> New...**,
   name it exactly `BCBake` (it must match the existing `Working\CustomMaps\BCBake`
   dir; ArtManager will adopt the existing `source\` tree).
3. In the asset tree (left), expand **Levels -> World**. You should see
   `world01.wrl` listed (the source tree provides it).
4. Right-click **`world01.wrl`** -> **Auto-Create Asset** (this registers a build
   asset for the world). Accept defaults.
5. Right-click the new `world01` asset -> **Build** (or toolbar **Build Asset**).
   Wait for the build log to finish with no fatal errors. Texture/record warnings
   for base-game assets are OK; a hard failure mentioning a missing `drxmap` /
   `bloodcave` record means `additionalbuilddirs` is not resolving -> STOP and
   re-check Tools.ini + that CustomMaps\SoulvizierClassic is built.
   - This step is what the earlier attempt skipped; it primes the compile paths.

(You can leave ArtManager open; the Editor is a separate exe.)

---

## PHASE 2 - Editor: open world, ENTER EDITOR MODE, confirm terrain (GO/NO-GO)

6. `open_application` Editor (`Editor.exe`). If it opens the last mod/level, fine;
   otherwise **File -> Open Mod** (or it uses `Tools.ini` `defaultMod`) -> select
   **BCBake**.
7. **File -> Open** -> navigate the mod source to **`Levels\World\world01.wrl`** and
   open it. Wait for the world to load (large world; may take 10-60 s).
8. The Editor opens in **Layout Mode** by default (you see a top-down grid of level
   tiles). **This is NOT enough** - per-level terrain (needed to bake a per-level
   navmesh) only loads in **Editor Mode**.
   - Find the mode tabs/buttons (usually bottom or top toolbar): **Layout Mode**
     and **Editor Mode**. Click **EDITOR MODE**.
9. In Editor Mode, find the **level selector dropdown** (lists the level tiles by
   name). Select **`BC_initialpathway`**. The Editor loads that level's terrain,
   entities, and the 3D viewport re-centers on it.

### GO / NO-GO gate - does terrain render?
Take a `screenshot`.

- GOOD (GO): the viewport shows the blood-cave floor as textured 3D terrain - a
  reddish/rocky cave ground with rock clusters, bone piles, cobwebs (the 32
  drxmap objects). You can orbit/zoom and see lit, textured geometry. Proceed to
  Phase 3.
- BAD (NO-GO): the viewport is **solid black** (or terrain is untextured
  flat/void). The per-level `Terrain` did not render, so `CreatePathMesh` will be
  skipped and the bake produces nothing. Do the fallbacks below, in order, and
  re-check the gate after each:

  Fallback A (most likely fix if Phase-1 build was skipped): return to ArtManager,
  ensure the `world01` **Build** actually completed; rebuild if needed; back in the
  Editor **File -> Reload** the world, re-enter Editor Mode, reselect the level.

  Fallback B (texture-resolve): confirm `Tools.ini` `additionalbuilddirs` really
  contains BOTH `...Titan Quest Anniversary Edition` AND
  `...\CustomMaps\SoulvizierClassic` (semicolon separated, no trailing slash), then
  restart the Editor (it reads Tools.ini at launch only).

  Fallback C (known sub-256 tile bug): BC_initialpathway's tile is 39x24 (< 256).
  The Editor has a documented bug where sub-256x256 tiles can render black
  regardless of assets. If A+B don't help, try selecting a LARGER xBloodCave tile
  as a rendering sanity check (e.g. `drxBC_Finale` or `drxFirstRoom`, which are
  multi-MB and larger) - if those render but BC_initialpathway stays black, the
  tile-size bug is implicated; bake the larger tile first to prove the pipeline,
  then handle BC_initialpathway via the shifted-coord path (see coord note) or by
  a My-Games settings reset (Fallback D).

  Fallback D (settings reset): close the Editor; rename
  `<TQ docs>\Settings\` aside (forces default video/editor settings); relaunch.
  Some black-viewport cases are a stale editor video config, not assets.

  If ALL fallbacks fail (BC_initialpathway still black), STOP and report: the
  per-level terrain will not render on this hardware for this tile, and the
  offline-Recast fallback (RLTD container RE) is the remaining route.

---

## PHASE 3 - Bake the navmesh + maps, save

Only after a GO on terrain.

10. Switch back to **Layout Mode** (Rebuild Pathing operates from the Build menu;
    keep the level selected/loaded).
11. Menu **Build -> Rebuild All Pathing**. Accept the confirmation dialog. Wait for
    completion (progress bar / log). This is the step that runs
    `Level::CreatePathMesh` -> `PathMeshCompiler::CreateNavigationMesh` and writes
    the `0x0b` RLTD section for each level whose terrain is loaded.
    - If a "Rebuild Selected Pathing" option exists and only BC_initialpathway is
      selected, that is faster and sufficient; "All" is the safe default.
12. Menu **Build -> Rebuild All Maps**. Accept. This writes the optimized/packed
    level output (the `LevelsOptimized\` / compiled `world01.map`).
13. Menu **File -> Save All**. This re-writes the source `.lvl` (now containing the
    `0x0b`) and the world files.

---

## PHASE 4 - Harvest + verify

14. Back in a shell (Bash tool), run:
    ```
    py tools/verify_editor_output.py
    ```
    It searches the BCBake source `.lvl`, any `LevelsOptimized\` sibling, `assets\`,
    the mod-root recursively, and the built `Resources\Levels.arc` (`world01.map`),
    and reports **PASS** if a `0x0b` (REC\x02) section is now present (with its size)
    vs the pre-bake baseline (which had `0x0a` only, no `0x0b`). On PASS it copies
    the harvested blob to `local\editor_normalized\BC_initialpathway.lvl`.

15. If PASS: the harvested `0x0b` is injected into the merged map via
    `build_section_surgery.inject_rec02_into_blob(blob, ints_raw,
    donor_data=<0x0b>, use_stub=False)`. See the coord note for whether it needs
    repositioning.

---

## Coordinate note (why the harvested mesh lands in the right place)

- BC_initialpathway original SV grid corner = `(-2101, 18, 1293)`.
- Merged/shifted grid corner (svaera_plus_portals `GRID_SHIFT['xbloodcave']` =
  `(1663,0,922)`) = `(-438, 18, 2215)`.
- The RLTD body is stored in LEVEL-LOCAL coordinates (verified: tile bmin/bmax are
  small 0..80 values, not world ~-6000). The world position comes from the `0x0b`
  header **center** + the engine placing the level at its grid corner.

Two supported routes (default is A):
- A. Bake at ORIGINAL coords (this tree, no `--shift-grid`). Then on inject,
  `transplant_rec02` re-patches the header center to the merged shifted grid.
  (The center-repositioning bug for donors with >4 difficulty blocks is now
  FIXED in `build_section_surgery.py`.) Body is untouched; only the header moves.
- B. Bake at SHIFTED coords: re-run `py tools/setup_bc_bake_tree.py --shift-grid`
  BEFORE Phase 1 (patches the WRL's BC_initialpathway grid to `(-438,18,2215)`),
  then the Editor writes the header center already at the final position and no
  repositioning is needed. Use B if A shows any vertical/positional offset in the
  single in-game walk test.
