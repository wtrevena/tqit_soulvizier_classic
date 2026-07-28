# CLAUDE.md - Soulvizier Classic (TQAE mod) - Status Board & Working Notes

> Durable status/notes for Claude Code sessions, committed to git so state survives across
> sessions and machines. **Read this first.** Newest status at the top of each section.
> Last updated: 2026-07-08 (orientation + read-order below are current; the "Current status" and
> later sections are HISTORICAL - the live state lives in `docs/HANDOFF_LIVE_STATE.md`).

> 📘 **For HOW-TO knowledge** (add new caves/areas/quests/portals, how the engine's world
> model works, navmesh pipeline, recipes, failure graveyard, engine internals):
> **`docs/MODDING_PLAYBOOK.md`** - the durable playbook distilled from everything learned
> fixing the map. This file (CLAUDE.md) is the STATUS board; the playbook is the MANUAL.

> ⚖️ **`docs/WILL_RULINGS.md` = THE DESIGN LAW OF RECORD (2026-07-16).** Four standing process
> laws, born from the 07-16 regression day:
> 1. **RULINGS LEDGER:** every implementer brief checks the ledger for its domain; every vet
>    checks the change against it; rulings are never silently dropped (IMPLEMENTED/PENDING/
>    SUPERSEDED only). New Will decisions get appended VERBATIM the turn they are made.
> 2. **RETIREMENT PROTOCOL:** deleting/retiring any record requires checking the ledger + wave
>    reports for design intent naming it. "Unreferenced in code" is NOT sufficient (the
>    q_bloodtoxeus_lone_50 lesson - it WAS the 100% chest spawn). Deletions default to WILL-VETO.
> 3. **PLAYER-SURFACE CHECKLIST:** every content lane enumerates and verifies every player-visible
>    surface of what it builds (name, icon, portrait, race, sounds, tooltip, drop, unlock,
>    in-game color) - never silently deferred (the b40 deferred-portraits lesson). Colors may
>    only be claimed from in-game-CONFIRMED assets (the 343_dark_smoke renders-green lesson).
> 4. **NO NEW SURFACE WITHOUT A GATE + DEBT REGISTER:** a lane creating a new content CLASS ships
>    its invariant gate with it (the boss-placement spacing/clearance lesson). Every
>    "deferred/unproven/launch-gated/needs-Will-check" item in any report is registered in the
>    BACKLOG DEBT section at commit time; integration gate records print the open debt list.

---

## What this mod is

**Soulvizier Classic** is a total-conversion mod for **Titan Quest Anniversary Edition (TQAE)**.
It back-ports the classic TQ:Immortal-Throne-era **Soulvizier 0.98i** ("SV") and merges it with
**Soulvizier AERA** ("SVAERA", the modern TQAE port), plus the **DRX** ("Diablo Re-eXtinction")
visual overhaul, into one playable **Custom Quest** mod.

Centerpiece feature: hundreds of **"souls"** that drop from monsters and summon pets; masteries,
legacy-skill restoration, Super Caravan storage, and epic/legendary enchanting (baked into the DB).

Upstream authors (for credits + permissions): **amgoz1** (SV 0.98i, on Munderbunny's Underlord),
**soa** (SVAERA), **Dragonlord** (DRX).

---

## ⚡ SUCCESSOR AGENTS - READ ORDER: **docs/HANDOFF_MASTER_2026-07-12.md FIRST** (throttle handoff: live P0s, in-flight workflow resume command, full plan) → this file (CLAUDE.md) → **`docs/README.md`** (the doc index +
trust levels) → **`docs/HANDOFF_LIVE_STATE.md`** (the current-state board: build27 sizes/MD5s, the
TESTHUB-vs-canonical deploy asymmetry, standing rules). Then `docs/BACKLOG.md` (the single open
bug/queue board) and `docs/PLAYBOOK.md` (how to add/change anything) as needed. This repo is
self-sufficient; no conversation context is required.

> ⚠️ **STATUS BELOW IS HISTORICAL - see `docs/HANDOFF_LIVE_STATE.md` for the LIVE state** (build27,
> Workshop wrapper fix, exact sizes/MD5s; open bugs in `docs/BACKLOG.md`). The "Current status" and
> every section below were written build25-era and earlier; they are preserved as the map/RE decision
> record (how the invisible-wall bug was solved, entrance history, content-gap origins), NOT as
> current fact.

## Current status (2026-07-07: PUBLIC ON STEAM WORKSHOP - item 3759792705)

**The mod is LIVE and PUBLIC** (subscribe to download; updates push via
`scripts/upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0` after
`package_workshop.ps1`; steamcmd session cached). Deployed = build25 map +
augments-fix arz + current Text. Highlights since 07-06: blood cave fully
walkable (Y-align build17 + rocks-carve build20); quest load-window fixed
(build22 - QUESTS section = 256 vanilla-parity entries, THE letter/widow root
cause); fountain/caravan/letter/smoke/sprites restored; Knossos->UberDungeon
door (build24) + invented Sparta Crypt door (build25); all 15 SV-area interiors
have real navmeshes (build23, config-driven CLUSTERS generator w/ blood-cave
byte-identity proof); ~60 boss souls implemented + Ainex fixed + release drop
rates 66/25 + zero dead augments; Hemorrheus superboss = "Toxeus the Murderer,
Devourer of Blood" (Athens mesh, crimson skin) beyond the secret waterfall
chamber. THREE fail-loud DB build invariants (soul leaks / soul augments /
text tags) + per-wave map gates; a unified map contract suite is queued.
**LIVE session state + run-books: the memory board (tq-soulvizier-2026-07-resume.md).**
⚠️ STANDING: Occult + Hunting masteries contain Will's HAND-TUNING - never
revert them to SV. Will's build-script soul edits = law; SV originals = the
design bible for generated souls. TESTHUB map variants are LOCAL-ONLY, never
uploaded. Deploy couplings: Levels+Quests together; arz+Text together.

## Prior status: Current status (2026-07-07: build22 - QUESTS load-window fix)

**WIDOW-LETTER + CARAVAN REPEAT-REPORT ROOT CAUSE FIXED (map-side QUESTS registry).** Will
re-reported "widow letter STILL missing" and "caravan STILL missing" on build21. The letter
half was a REAL, newly-diagnosed map defect (the caravan half was addressed in the prior wave
by placing a functional NpcCaravan at the cave mouth). Root cause of the letter: the world
QUESTS(0x1b) section appended the 4 SV area questlines (widowletter/urder/bossarena/
open_bloodcave_portal) PAST index 254 (widowletter at 256), and the engine NEVER loads a
QUESTS entry past the original ~254-256 window (empirically proven across 5 custom-quest chars
+ vanilla saves; docs/QUEST_STATE_INJECT.md sec 2). So the quest never tracked for ANY
character (fresh OR existing) -> the letter's OnLevelLoad spawn never fired. build19b's slot
tweak and quest_state_inject.py were both NO-OPs for this (the engine rebuilds Quest.myw from
live objects on save).

FIX (build22, `tools/svaera_plus_portals.py` `build_ordered_quest_list`, map-tooling only, no
DLL/navmesh/donor change): rebuild the QUESTS section so the 4 SV quests sit INSIDE the load
window - insert their primary `Quests/<name>.qst` forms right after `Quests/sv_commonmechanics.qst`
(idx 96 -> they land at idx 97-100), drop the 2 redundant `x2quest_controlsdoors.qst` native
re-registrations (identity kept via the first copy), and drop the entire ~46-entry appended
`XPack/Quests/*` dup+dead tail (every identity preserved by a native twin or the relocated
primary). Result: EXACTLY 256 entries (vanilla's proven-loading count), widowletter at idx 99,
and idx 254-255 = `x4_other_002_hcdungeon_control.qst` + `x2_StartQuest.qst` = the SAME 2 quests
at the SAME indices as VANILLA (byte parity at the boundary -> provably load; 0 native
regression). Now Will's EXISTING `_Toxeus` auto-adopts widowletter on next load (the engine
auto-adopts newly-loadable quests for existing chars), the STATIC finalletter (placed at the
letterdrop spot in the prior wave via INJECT_SPECS) is picked up -> SQWL_PickedUpLetter granted
-> the chest + widow + reward chain completes. Reward reachable for BOTH fresh and existing
chars, no save surgery. Verified: gates C1-C5 PASS + verify_merged_bc_navmeshes 24/24 +
entrance_landing --check-merged PASS; only 2 level blobs differ vs build21 (hiddenvalley01
0x05+0x14 caravan, drxfirstxistion_connection 0x05 letter), all navmeshes byte-identical.
`local/Levels_merged.arc` rebuilt (685,652,028 B). NOT yet deployed/committed.

> ⚠️ DEPLOY COUPLING (must ship together): the single-letter guarantee needs BOTH artifacts -
> the STATIC letter in `Levels_merged.arc` AND the widowletter.qst spawn-neutralization in
> `Quests.arc` (`tools/build_quest_files.py` removes the quest's own `Action_SpawnEntityAtLocation`
> so it cannot spawn a second letter). Deploying the new map WITHOUT rebuilding + staging the new
> `Quests.arc` would, once the quest tracks, yield static + quest-spawned = 2 letters. Always run
> `tools/build_quest_files.py` (or bootstrap) in the SAME deploy as the map.

**INVISIBLE-WALL TRUE ROOT CAUSE FOUND (runtime-proven) + FIX DEPLOYED (build13).** After 9
navmesh-content fixes all walled identically, Frida runtime probes (hook ProcessRLTD; walk the
region-manager table at Engine+0x3743f0; portal dumps) proved: navmeshes LOAD fine (ret=1), portals
exist only for declared cave mouths (entrance pair healthy, open=1), and room-to-room walking is
navmesh TILE STITCHING. The stitch requires both levels' 12.8u tile lattices to coincide: every
working AE seam measures offset 0.000 mod 12.8 (AE batch rooms sit exactly 64u = 5 tiles apart);
every generated seam of ours was misaligned (6.4u at Will's wall = worst case). Fix:
`gen_rec02.generate()` snaps each raster origin down (and extent up) to a shared 64u lattice;
donor-freshness + verifier gates rewritten for the snapped invariant; new merged-map LATTICE GATE
(scratchpad seam_lattice_check.py `<map> --gate`). Build13: 24/24 donors one shared phase, verify
24/24, **24 aligned seams / 0 misaligned**, deployed byte-identical (684,860,698 B). Awaiting Will's
walk test (full TQ restart required).

**Yeti soul-drop bug FIXED + DB deployed:** normal (Common) yetis dropped souls because
`_force_100_pct_soul_drops` keyed off the soul-loot field alone, re-enabling Common/Champion that
`wire_souls_to_monsters` deliberately gates off (design: only Hero/Boss/Quest drop souls). Fix both
sides: wire_souls now zeroes `chanceToEquipFinger2` on non-Hero/Boss/Quest with inherited soul loot
(419 records); the 100% forcer only boosts monsters already at chance>0 (894 boosted, 415 left
gated). Verified in the rebuilt .arz: am_yeti_*/hulking_yeti_35/am_yetichampion_* = 0.0;
boss_gargantuanyeti + um_ heroes = 100. validate_tags PASS. Deployed byte-identical (54,437,387 B).
NOTE: Champion-rank ALSO stops dropping (matches documented design) - if Will wants champions to
drop souls, add 'Champion' to the gate in both files.

## Prior status (2026-07-04)

The database / souls / pets / enchanting side is working. The map-integration blocker is **SOLVED**:
the 23 walkable Soulvizier blood-cave levels now carry **real, valid `0x0b` (RLTD) navmeshes**,
generated **offline in pure Python** after the RLTD / Detour `dtTileCache` format was fully
reverse-engineered (see the map section) - NO TQAE Editor bake and NO DLL patch needed (Steam-clean).
The 23 navmeshes are generated, injected into the merged map, byte-verified present (0x0b size ==
donor size, 0x0a stripped, via `tools/verify_merged_bc_navmeshes.py`), and **deployed to CustomMaps**.
The one remaining unknown is the **in-game walk test** - the only thing a launch can confirm.

**Progress (2026-07-04), build-verified + committed:**
- **MAP BUG SOLVED (headline):** the RLTD / Detour `dtTileCache` navmesh format was fully
  reverse-engineered, so the 23 walkable blood-cave navmeshes are generated **offline in pure Python**
  (`tools/gen_bc_navmeshes.py`) from the pristine upstream `0x0a` geometry, GUID-remapped to resolve
  in the merged world, injected pre-positioned into the merge (`svaera_plus_portals.py` tier-1 +
  `build_section_surgery.py` `pre_positioned=True`), byte-verified in the merged map (23/23 size-exact,
  `0x0a` stripped, `tools/verify_merged_bc_navmeshes.py`), merged, and **deployed to CustomMaps**. This
  bypasses the (unusable-on-this-hardware) TQAE Editor bake entirely and stays Steam-clean.
- Content P0s fixed: soul drops stay 100% for testing (`SVC_RELEASE_DROPS=1` for tuned release
  rates); orphaned soul name-tags fixed + a `tools/validate_tags.py` build-gate added (build passes:
  every referenced + authoritative tag resolves).
- SV area questlines integrated: `urder`, `widowletter`, `bossarena`, `open_bloodcave_portal` ported
  into `Quests.arc` (names were already registered in the map, so no map rebuild). One lost entrance
  NPC (`starting_storyteller`) surgically neutralized.
- Blood-cave entrance-portal bugs fixed (correct NPC + grid-shifted teleport target `(-418,23,2227)`).
- Map-clobber hazards disarmed: deploy Levels sync is now opt-in (`-SyncLevels`); bootstrap Step 3
  keeps an existing `work/Levels.arc` instead of overwriting it with the SVAERA base.
- Verified by a real DB+Text+Quests build (drops 100%, `validate_tags` PASS, `Quests.arc` arc-verify
  105 OK / 0 FAIL). `Levels.arc` deliberately untouched.

**UPDATE (2026-07-04 night): AUTHENTIC WALK-IN ENTRANCE SHIPPED (portal hack removed).** Will's live
test found the quest-portal teleport broken (dialog then no-op; then no dialog at all) - the whole
boat-dialog hack was abandoned in favor of the classic-SV mechanism he remembered: the base-game
Silk Road cave with SV's extra west tunnel. Implementation (design agent -> implementer -> adversarial
vet GO, commits d40518b/bc187c2/57fa322/442352c): SVAERA's `Random09A` level blob is swapped for SV's
version (both LVL v0x0e; SV's adds the west tunnel + blood-cave dressing), relocated by the xBloodCave
GRID_SHIFT to corner `(-198,18,2135)` so its west edge abuts `xPassageTransitionStart`, with the AE
GUID KEPT in the LEVELS index - so HiddenValley01's existing native `GridEntrance` cave mouth (whose
`0x14` metadata references that GUID) streams the player in unchanged, quest-free. Its `0x0b` navmesh
is generated by the same offline pipeline (donor 78,918 B; own-GUID overridden to AE's; neighbor =
xPTS); the vet proved the two navmeshes' walkable areas OVERLAP ~31 world-units across the x=-198
seam. The portal NPC injections + boat-dialog quest are removed (Quests.arc = clean SVAERA original +
the 4 ported SV questlines). Rebuilt map verified 24/24 navmeshes byte-exact + deployed to CustomMaps
(Levels.arc 683,966,024 B).

**Remaining to "everything should work":** the **in-game walk test**: TQAE -> Play Custom Quest ->
`SoulvizierClassic` -> in HiddenValley01 (Silk Road, where the old portal NPC stood - it is gone now)
enter the native cave mouth -> inside the cave take the WEST (left) tunnel -> it walks into the blood
cave. Return = walk back out. Only in-game uncertainty: tunnel walkability end-to-end + seam
streaming. Fallbacks if imperfect are in the map section. Then Steam prep (permissions; LAA
instructions; DRX stays - no Lite build).

**Active goal:** get the game to a state where everything *should* work, so a single in-game test
(walk to the blood cave, confirm entry) is a clean final verification. Then ship to Steam Workshop.

---

## 🗺️ THE MAP BUG - invisible walls in Soulvizier-only areas

### True root cause (disassembly-verified, 2026-07-03)
TQAE has two pathfinding formats inside each level blob (`.lvl` in `world01.map` in `Levels.arc`):
- `0x0a` = **PTH** (old TQIT PathEngine navmesh). The 46 SV-only levels shipped with these.
- `0x0b` = **REC\x02 / RLTD** (modern TQAE Recast navmesh). This is the ONLY format the stock
  TQAE engine loads. **The TQAE LVL parser has no handler for `0x0a`** - it silently skips it.

No navmesh loaded → the click-to-move pathfinder refuses to enter the area → invisible wall.

The last deployed attempt (**Approach 22**) injected a minimal **148-byte empty `0x0b` "stub"** into
each of the 46 levels, betting the engine's built-in runtime Recast generator (`ProcessRLTD_flow`,
VA `0x101F6210`) would rebuild the navmesh from level geometry at load. **This is proven dead:** that
generator is gated by `cmp byte[0x10374441],0 / je (skip)`, and gate byte `0x10374441` lives in
zero-initialized memory that **nothing in the 3.78 MB Engine.dll ever sets non-zero**. So it always
early-returns without building anything. It is Editor/tool-only dead code in the shipping build.

### ✅ SOLVED (2026-07-04): real navmeshes generated OFFLINE (no Editor, no DLL patch)
The Editor bake proved unusable on this hardware (black grid viewport + "Error creating path mesh" on
the custom GridSystem levels). Instead the `0x0b` payload was fully reverse-engineered: it is a
serialized Detour **`dtTileCache`** layer set (rasterized walkable cells, NOT prebuilt polys; the
engine builds polys at load via `dtTileCache::buildNavMeshTile`), FastLZ-0.1.0-level-1 compressed,
wrapped in a `REC\x02` container (version + payload size + GUID list [own + neighbor level GUIDs] +
center + dims + exactly 3 `dtTileCacheParams` tilesets, each record = a 56-byte `dtTileCacheLayerHeader`
[magic `DTLR` == bytes `RLTD`] + FastLZ(heights+areas+cons)). Round-trip identity was proven on 670
real base-game sections + confirmed against the Engine.dll disassembly.

Generation pipeline (all pure Python, committed): `tools/tok_parse.py` (parse the `0x0a` PTH "tok"
walkable mesh) -> `tools/gen_rec02.py` (rasterize -> erode -> 64x64 tiles) -> `tools/fastlz.py`
(byte-exact FastLZ port) -> `tools/rec02_format.py` (byte-accurate container). Driver
`tools/gen_bc_navmeshes.py` reads the pristine upstream `0x0a`, shifts the container center by the
xBloodCave `GRID_SHIFT (1663,0,922)`, and remaps GUIDs so every own + neighbor GUID resolves in the
merged world (critical: `xPassageTransitionStart` referenced the SV-original `Random09A` that the
merge replaced with SVAERA's - the raw GUID would fail the engine's GUID gate `ProcessRLTD`
`0x101f4ba0`, which rejects the whole `0x0b` section unless EVERY GUID resolves). Output: 23
`local/editor_normalized/*.0b.bin` (regenerable, `py tools/gen_bc_navmeshes.py`, ~213s, deterministic).

Injected via `svaera_plus_portals.py` step 7b tier-1 (`find_pre_positioned_donor` ->
`inject_rec02_into_blob(pre_positioned=True)`: insert VERBATIM, skip transplant, strip `0x0a`).
Verified in the final merged map by `tools/verify_merged_bc_navmeshes.py` (23/23 `0x0b` size == donor
size, `0x0a` gone) and deployed. **Walk test is the only remaining confirmation.**

Fallbacks if the walk test shows imperfection (ranked): (1) flip the 1-byte area flag in the header
(currently area id=2); (2) C++ Recast for exact erosion parity; (3) pull terrain heights from the
`0x06`/`0x09` sections (BC_initialpathway's tok mesh is height-flat at z=-56 - click-projection there
is the least-certain spot).

### Decision (locked): ship **Steam-clean, NO DLL patch**
The shipped mod MUST run on a **stock/unpatched** engine. Therefore:
- We do **not** ship the Engine.dll patch (Approach 21 `0x0a→0x0b` redirect) or the one-byte gate
  flip (a personal-play-only option - Steam "Verify integrity" reverts base-game DLLs anyway).
- The fix is to give all 46 SV-only levels **real, valid `0x0b` navmeshes**, baked by the **TQAE
  Editor's "Rebuild Pathing"** (the only known generator of valid RLTD sections), then harvest and
  inject them via the existing `inject_rec02_into_blob(use_stub=False, donor_data=<editor 0x0b>)`
  path in `tools/build_section_surgery.py`.

### Critical-path blocker - SOLVED on paper (2026-07-04 investigation)
Prior Editor attempt (git `6710428`) failed with a **black terrain viewport**; per-level navmesh
baking requires terrain to render. Root cause is now identified and fixable (not a hardware limit):

1. **`additionalbuilddirs=` in `Tools.ini`** (at `<TQ docs>\Tools.ini`, outside the repo) is now SET
   to `<game install>;<TQ docs>\CustomMaps\SoulvizierClassic` (verified 2026-07-04). This makes the
   Editor resolve terrain **textures/meshes** (the `.tex`/`.msh` art) from the base game + the built
   SV `.arc`. NOTE (corrected below): this covers ART only - it does **not** make the SV custom
   **records** resolve for the pathing build; those must be loose in the mod source tree. That
   records gap (not textures) is the real "Error creating path mesh" cause. See the blood-cave
   subsection just below.
2. **Wrong Editor sub-mode.** The prior run stayed in **Layout Mode**; per-level terrain only loads
   when you enter **Editor Mode** and select the level. Without a loaded `Terrain`, `CreatePathMesh`
   is skipped (only the world SD bumped v6→v7, no `.lvl` changed - exactly what `6710428` reported).
3. **Harvested from the wrong folder.** The Editor writes optimized output to a **`LevelsOptimized\`**
   directory; the old verify script looked in `source/Maps/`.

### Blood-cave "Error creating path mesh" - RESOLVED on paper (2026-07-04, evidence-verified)
The 30 xBloodCave levels fail the Editor pathing bake with **"Error creating path mesh"** because
they place **custom records** (`records\drxmap\bloodcave\...` etc.) that live ONLY inside the
compiled `SoulvizierClassic.arz`. The **Editor asset-resolution model** (empirically pinned + forum
corroborated):
- A placed record reference is resolved from the Editor's **working database** = the mod's **loose
  source tree** `<mod>\source\database\records\...\*.dbr` merged over the base game's compiled
  `<game>\Database\database.arz`. The Editor does **NOT** read records from a mod's compiled `.arz`
  in `additionalbuilddirs` during the pathing build. **Proof:** swapping the built `BCBakeSV.arz`
  for the full 54 MB `SoulvizierClassic.arz` had **zero effect** (still 0/30) - the compiled mod
  `.arz` is never consulted for records at bake time.
- Record **`.tpl` templates** resolve automatically from **`<game>\Toolset\Templates.arc`** (566
  templates; all 14 the blood-cave records use are present). No templates need placing in the mod.
- **Art (`.msh`/`.tex`)** DOES resolve from the compiled `.arc` reachable via `additionalbuilddirs`.
  Verified: every blood-cave terrain mesh is in `SoulvizierClassic\Resources\drx.arc`, wall textures
  in `DRXtextures.arc`, and base XPack cave/hades meshes in `<game>\Resources\xpack\
  SceneryUnderground.arc` / `SceneryHades.arc` / `Items.arc`. So **no source art extraction is
  needed - only the loose RECORDS were missing.**

**The blood-cave terrain is a `GridSystem`** (`records\drxmap\bloodcave\bloodcave.dbr`, Class
`GridSystem`, template `Engine\GridSystem.tpl`): a dungeon-tile system whose `feature` +
`wallPieceBase*` fields list the floor/wall `.msh` pieces Recast rasterizes. Placed dungeon pieces
are `Decoration` records with a `mesh` + `baseTexture`.

**THE FIX (built 2026-07-04): `tools/populate_svbake_records.py`.** Extracts the region's placed
SV-custom records into `<mod>\source\database\records\...` as loose ArtManager-format `.dbr`
(CRLF, `key,value,`). Idempotent, parameterized by `--region` (xbloodcave|uberdungeon|bossarena|
secret_place). Default `--placed` mode = the region's `.lvl` DIRECT refs that are SV-only + 1 hop of
SV-only children. Ran for xBloodCave: **285 loose records written** to
`<TQ docs>\Working\CustomMaps\BCBakeSV\source\database\records\` (0.5 MB, 0 malformed).
**Verified without the Editor (GO):** for the two test levels drxBC_Finale (20 placed) and
drxFirstRoom (68 placed) every placed record resolves (SOURCE+BASE, **0 MISSING**), every template
resolves in the toolset, and **every referenced mesh/texture resolves in the arcs (0 unresolved).**
Fallback if the Editor still errors on a deeper (Monster-spawn) ref: `--all-sv-custom` (all ~3,185
`drx*`-namespace SV-custom records; Monster spawns are dynamic and not normally needed for the static
navmesh, which is why base-game levels bake without their loot/monster sub-graph loose).

**Re-bake now:** ArtManager -> Set Mod BCBakeSV -> Build the world asset (compiles the new loose
records into the mod DB) -> Editor -> open world -> Editor Mode -> confirm terrain renders -> Layout
Mode -> Build -> Rebuild All Pathing -> Rebuild All Maps -> Save All. Verify with
`py tools/verify_editor_output.py`.

**No headless/CLI bake exists.** MapCompiler.exe is only a packager (imports zero navmesh symbols
from Engine.dll; passes `.lvl` pathing sections through unchanged). `pathengine.dll` is the legacy
`0x0a`/PTH middleware, not the Recast generator. The Recast/Detour navmesh generator
(`PathMeshCompiler::CreateNavigationMesh`, `Level::CreatePathMesh`, `TerrainPathMeshCalculator`)
lives in stock **Engine.dll** and is driven ONLY by the **Editor GUI** ("Build → Rebuild All
Pathing"). This is Steam-clean (stock tooling, no DLL patch). It must be driven via the GUI
(computer-use). Fallback if the Editor proves unusable on this hardware: offline Recast from the
`0x0a` geometry (high effort - RLTD container RE).

**Bake procedure (proven-on-paper; to be run via computer-use):** fix Tools.ini → in Art Manager,
right-click `Levels/World/world01.wrl` → Auto-Create Asset → Build → in Editor.exe, open the world,
enter **Editor Mode**, select the level, **confirm terrain renders (GO/NO-GO)** → Layout Mode →
Build → Rebuild All Pathing → Rebuild All Maps → Save All → harvest the `0x0b` from
`LevelsOptimized\` (and/or the re-saved source `.lvl`; success = a `REC\x02` section now present) →
inject via `inject_rec02_into_blob(..., use_stub=False, donor_data=<editor 0x0b>)`.
**Coordinate pitfall:** xBloodCave is grid-shifted `(1663,0,922)`; either bake at final shifted grid
coords, or rely on `transplant_rec02` repositioning the mesh via the header center (its docstring
says mesh data is local to center, so a correct center patch repositions it - verify in-game).
**Known risk:** TQAE Editor has a documented bug where sub-256×256 tiles render black regardless of
assets; some small SV tiles may need individual handling.

### The original terrain doorway - now RESTORABLE (2026-07-04 investigation, evidence-verified)
SV 0.98i's real blood-cave entry was a WALK-IN tunnel: terrain grid-edge chain
`Random09A -> xPassageTransitionStart -> BC_initialpathway` (GUID-proven from the 0x0a edge records;

---

## 🚪 Entrance bugs - OBSOLETE (2026-07-04: quest-portal mechanism removed entirely)

> The quest-portal teleport described below was fixed (coord re-derived on-mesh) and STILL failed
> in-game a second way (dialog stopped appearing; fragile 200x-repeat OnLevelLoad idiom + saved quest
> state). It is now fully REMOVED in favor of the engine-native walk-in entrance (SV Random09A blob
> swap; see the status section). Kept for history only.

Both verified in source; the quest-portal that teleports the player into the cave is broken two ways:
1. **Coordinate desync** - `tools/build_quest_files.py:33` hard-codes the teleport target to
   `(-2060,18,1322)` (the SV-original position), but `tools/svaera_plus_portals.py:347` grid-shifts
   the whole xBloodCave cluster by `(1663,0,922)`. The teleport lands ~1900 units into empty void.
2. **Wrong NPC** - `build_quest_files.py:29` drives NPC `silkroad_villager1.dbr`, which does **not
   exist** in the entrance level `HiddenValley01` (only native `silkroad_villager4` + the injected
   `portal_bloodcave_entrance.dbr` are there). The dialog/teleport never fires.

Fix: retarget the teleport to a real walkable point inside the shifted `BC_initialpathway`, and drive
the injected portal entity (or a real native NPC). Keep the quest-portal model (restoring the terrain
doorway via shared-level replacement is what caused the original crashes).

---

## 📜 Quest integration (NEW workstream - largely not done)

The prior work built only the *portal teleport* to get INTO the blood cave (and it's buggy). The
actual **Soulvizier content quests** (the questlines inside the blood cave and other SV areas) have
**not been integrated/verified**. Known signals: `open_bloodcave_portal.qst` is a dangling reference
(file absent), `bossarena.qst` is claimed in the README but doesn't exist, and the QUESTS-section
merge only carries names. This needs: an audit of which SV quests exist upstream vs. shipped, and a
plan + implementation to wire the SV area questlines. `tools/qst_format.py` is a fully-RE'd `.qst`
reader/writer (89/89 round-trip) available for this.

---

## 🧟 Content gaps (independent of the map fix - can run in parallel)

**P0 (release-blocking):**
- **Soul drops forced to 100%** - `tools/apply_svc_patches.py` `_force_100_pct_soul_drops` (called
  unconditionally by the build) overrides the tuned 66%/25% rates to 100% ("TESTING", never
  reverted). Gate it behind an explicit testing flag (default OFF).
- **Orphaned soul name-tags** - `tagSoulSVC9005` (Crowboar) & `9006` (Uber) exist in the `.arz` but
  not in shipped `Text.arc` → raw tag text shows in-game. Structural: `build_text_arc.py` isn't
  coupled to `build_svc_database.py`, so this recurs on any soul-roster change. Fix + add a build
  validator that fails loud if any `.arz` name/desc tag is missing from `Text.arc`.
- **Multiplayer: TESTED AND WORKS** (Will confirmed 2026-07-12). Also SV's `RunEquation` MP spawn-scaling
  formulas fail to parse in AE → silently fewer spawns in MP.

**P1/P2:** Super Caravan "respec items" never implemented; Lite build is OFF THE TABLE (Will
2026-07-04: keep DRX; also `-LiteMode` as-coded strips drx.arc/DRXtextures.arc which the blood cave
itself needs - do NOT run it; crash mitigation is the 4GB LAA patch instead); dead orphan
`tools/apply_sv_classic_patches.py`; stale docs
(`SOUL_AUDIT.md`, `CHANGELOG.md`, `system_check.md`); `dist/` artifact stale vs HEAD; a few
code-hygiene items (shadowed `_find_record`, unchecked pet-skill return values).

---

## ⚠️ Deploy hazard - neutralize before any deploy

RESOLVED (2026-07-04). The old foot-gun (deploy auto-copied a stale `local → work`) is fixed: the
Levels sync is now opt-in (`-SyncLevels`). `local/Levels_merged.arc` was rebuilt fresh (652 MB, the
real navmesh map, 0 bad offsets, append-clone at idx 2281 is a harmless diagnostic) and deployed with
`-SyncLevels`; the deployed `work/.../Levels.arc` is now byte-identical to it (684,002,931 bytes).
Always regenerate via `tools/svaera_plus_portals.py` (deterministic) rather than trusting a leftover
`local/` build.

---

## 🚀 Steam release plan & hard blockers

Payload ~1.11 GB; Workshop can host it (SVAERA AERA is 1.86 GB live on appid 475150). Repo has working
`scripts/package_workshop.ps1` + `scripts/upload_workshop.ps1` (steamcmd, appid 475150). SteamCMD is
installed at `C:\steamcmd\steamcmd.exe`; never run to completion yet.

Hard blockers: (1) map fix must be stock-engine (SOLVED: offline navmesh generation, Steam-clean);
(2) 32-bit address-space crashes → mitigation is the community 4GB LAA patch, shipped as
INSTRUCTIONS (README in the mod + Workshop description pointing at the NTCore 4GB Patch tool; a
Workshop mod is content-only and cannot legally/mechanically ship a patched TQ.exe, and Steam
verify/update reverts it anyway). Will's TQ.exe was LAA-patched locally 2026-07-04 (backups beside
the exe + backups/game_dll/). **DECISION (Will, 2026-07-04): KEEP DRX - no Lite build.** Note
LiteMode as-coded is now UNSAFE anyway: it strips drx.arc + DRXtextures.arc, which hold the blood
cave's own terrain meshes/wall textures (the cave is DRX-built: drxBC*, records\drxmap\...).
(3) **legal** - the mod bundles three upstreams wholesale; get written permission from amgoz1, soa,
Dragonlord (keeping DRX keeps Dragonlord's permission on the critical path). Recommend dual
distribution:
Workshop (auto-update) + moddb/Nexus zip (GOG/non-Steam, CustomMaps install).

---

## 🛠️ Build & deploy commands

- **Python:** use the `py` launcher (not `python`/`python3`); set `PYTHONIOENCODING=utf-8`.

### 🔎 Build inputs - check these FIRST (`tools/check_build_inputs.py`)

`upstream/`, `reference_mods/` and `third_party/` are **gitignored**, so `git worktree add` hands
every lane an **EMPTY** cache. Both build entrypoints therefore run one shared preflight before
touching anything. Resolution order per input, **first hit wins**:

1. the input's `$SVC_*` env var
2. the **in-repo** cache (`upstream/...`, `reference_mods/...`)
3. the **MAIN checkout's** cache (found via the worktree's `.git` file - this is what makes a
   worktree build work at all)
4. the installed location: Steam TQAE, or Steam Workshop item `2076433374` (SVAERA)
5. a sibling worktree that already has the cache (e.g. `build36-map` for SV 0.98i `Levels.arc`)
6. a `third_party/` archive - reported as EXTRACTABLE, never silently unpacked

Every **fallback** is md5-pinned, so auto-resolution can never quietly feed the build a different
upstream; a path you pass on the command line is used **as-is** when it exists. A miss fails LOUD,
once, naming the exact env var and every place searched (no more bare `FileNotFoundError` from deep
inside `ArzDatabase`/`ArcArchive`).

| input | env var | needed by |
| --- | --- | --- |
| SV 0.98i `database.arz` | `SVC_SV098I_ARZ` | DB build |
| SV 0.9 `database.arz` | `SVC_SV09_ARZ` | DB build |
| SV 0.4.1 `database.arz` | `SVC_SV041_ARZ` | DB build (optional) |
| base-game TQAE `database.arz` | `SVC_BASE_ARZ` | DB build (optional) |
| SV 0.98i `Text_EN.arc` | `SVC_SV098I_TEXT_ARC` | text build |
| SVAERA `Levels.arc` | `SVC_SVAERA_ARC` | map merge |
| SV 0.98i `Levels.arc` | `SVC_SV_ARC` | map merge |
| `SVAERA_customquest.arz` | `SVC_SVAERA_ARZ` | build36 mastery graft (`SVC_GRAFT_SVAERA=0` to skip) |

```
py tools/check_build_inputs.py --all --verify-hashes   # inventory + integrity
py tools/check_build_inputs.py --all --extract         # populate upstream/ from third_party/ zips
py tools/check_build_inputs.py --selftest              # planted negative tests for the resolver
```

- **Build database (`.arz`):**
  ```
  py tools/build_svc_database.py \
    upstream/soulvizier_098i/Database/database.arz \
    upstream/soulvizier_0.9/Database/database.arz \
    upstream/soulvizier_041/Database/database.arz \
    work/SoulvizierClassic/Database/SoulvizierClassic.arz \
    "/c/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"
  ```
- **Build merged map (`Levels.arc` → `local/Levels_merged.arc`):** `py tools/svaera_plus_portals.py`
- **Bootstrap full working mod (DB + text + resources):** `scripts/bootstrap_working_mod.ps1`
  (`-LiteMode` for the DRX-free variant)
- **Deploy to CustomMaps:** `powershell -ExecutionPolicy Bypass -File scripts/deploy_to_custommaps.ps1`
- **Package/upload Workshop:** `scripts/package_workshop.ps1` then `scripts/upload_workshop.ps1`

The mod loads via TQAE main menu → **Custom Quest → SoulvizierClassic**. It is a total conversion:
**create a dedicated Custom Quest character** - never load a normal character into it, and never
"bounce" it (breaks characters).

---

## 📌 Key technical lessons (hard-won; don't relearn)

- **dtype preservation:** never pass explicit dtype to `set_field()` on cloned records - INT/FLOAT
  corruption silently zeroes values (pet spawn failure).
- **Permanent pets:** remove `spawnObjectsTimeToLive` (set to `[]`). Reference soul: Lyia Leafsong.
- **Pet.tpl vs Monster.tpl:** copying ANY equipment/loot field from Monster.tpl → Pet.tpl crashes the
  game (even changing values of existing fields). Only animation/skill fields are safe. Pet equipment
  must use `_set_pet_equipment()` with hardcoded item paths, not monster field copying.
- **Never `clone_record` for souls:** brings stat values that corrupt saved items; use bare
  `_ensure_record()`.
- **Soul icon paths:** `SVItems\jewelry\soul_{n,e,l}_icon.tex` (first path component = archive name).
- **`{^F}` prefix** required on soul name tags for pink/magenta text.
- **Enchanting** (epic/legendary) is baked into the `.arz` via `make_enchantable()` - the shippable
  mod has **no Game.dll dependency**. (An old Game.dll hex-patch exists as a local backup only.)
- **TQ saves bake item properties** at pickup - pre-patch items won't reflect DB changes; test with
  freshly dropped items.
- **Map format:** `world01.map` sections QUESTS(0x1b) GROUPS(0x11) SD(0x18) LEVELS(0x01) BITMAPS(0x19)
  0x10 DATA2(0x1a) DATA(0x02). `DATA2`/`BITMAPS` = minimap TGA, NOT pathfinding. `ints_raw` = 13×int32:
  [0..5] tile dims, [6,7,8] grid corner (world x,y,z), [9..12] GUID.

---

## 📂 Repo layout (orientation)

- `tools/` - the build pipeline: `build_svc_database.py`, `apply_svc_patches.py` (souls/patches),
  `svaera_plus_portals.py` (map merge), `build_section_surgery.py` (level-blob surgery + navmesh
  inject), `build_quest_files.py`, `qst_format.py`, plus `.arz`/`.arc` I/O and a pile of pathfinding
  RE scripts. NOTE: `apply_sv_classic_patches.py` (with underscore) is DEAD/orphaned - the live one
  is `apply_svc_patches.py`.
- `scripts/` - PowerShell deploy/package/upload/bootstrap.
- `upstream/` - extracted SV 0.98i / 0.9 / 0.41 sources (gitignored). `reference_mods/SVAERA_customquest`
  - the SVAERA base (gitignored). `local/` - big working scratch incl. decompiled world source
  (`decompiled_sv/`, `merged_source/`) and candidate maps (gitignored).
- `work/SoulvizierClassic/` - staged deploy source (the real, good map lives here). `backups/game_dll/`
  - Engine.dll/Game.dll backups. `docs/` - CHANGELOG, crash analysis, inventories.
