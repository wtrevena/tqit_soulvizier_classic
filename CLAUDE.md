# CLAUDE.md — Soulvizier Classic (TQAE mod) — Status Board & Working Notes

> Durable status/notes for Claude Code sessions, committed to git so state survives across
> sessions and machines. **Read this first.** Newest status at the top of each section.
> Last updated: 2026-07-04.

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

## Current status (2026-07-04)

The database / souls / pets / enchanting side is largely working. The blocker is **map integration**:
the Soulvizier-only areas (blood cave, uber dungeon, secret place, etc.) are **not physically
walkable** — the player hits an "invisible wall." Root cause is now fully understood (below), and a
Steam-clean fix path is chosen. Several independent content bugs and an un-started quest-integration
workstream also stand between here and a shippable release.

**Active goal:** get the game to a state where everything *should* work, so a single in-game test
(walk to the blood cave, confirm entry) is a clean final verification. Then ship to Steam Workshop.

---

## 🗺️ THE MAP BUG — invisible walls in Soulvizier-only areas

### True root cause (disassembly-verified, 2026-07-03)
TQAE has two pathfinding formats inside each level blob (`.lvl` in `world01.map` in `Levels.arc`):
- `0x0a` = **PTH** (old TQIT PathEngine navmesh). The 46 SV-only levels shipped with these.
- `0x0b` = **REC\x02 / RLTD** (modern TQAE Recast navmesh). This is the ONLY format the stock
  TQAE engine loads. **The TQAE LVL parser has no handler for `0x0a`** — it silently skips it.

No navmesh loaded → the click-to-move pathfinder refuses to enter the area → invisible wall.

The last deployed attempt (**Approach 22**) injected a minimal **148-byte empty `0x0b` "stub"** into
each of the 46 levels, betting the engine's built-in runtime Recast generator (`ProcessRLTD_flow`,
VA `0x101F6210`) would rebuild the navmesh from level geometry at load. **This is proven dead:** that
generator is gated by `cmp byte[0x10374441],0 / je (skip)`, and gate byte `0x10374441` lives in
zero-initialized memory that **nothing in the 3.78 MB Engine.dll ever sets non-zero**. So it always
early-returns without building anything. It is Editor/tool-only dead code in the shipping build.

### Decision (locked): ship **Steam-clean, NO DLL patch**
The shipped mod MUST run on a **stock/unpatched** engine. Therefore:
- We do **not** ship the Engine.dll patch (Approach 21 `0x0a→0x0b` redirect) or the one-byte gate
  flip (a personal-play-only option — Steam "Verify integrity" reverts base-game DLLs anyway).
- The fix is to give all 46 SV-only levels **real, valid `0x0b` navmeshes**, baked by the **TQAE
  Editor's "Rebuild Pathing"** (the only known generator of valid RLTD sections), then harvest and
  inject them via the existing `inject_rec02_into_blob(use_stub=False, donor_data=<editor 0x0b>)`
  path in `tools/build_section_surgery.py`.

### Critical-path blocker being cracked
Prior Editor attempt (git `6710428`) failed: the Editor's **terrain viewport rendered black**, and
per-level navmesh baking requires terrain to render. Under investigation: the black-viewport root
cause (most likely missing terrain assets in the Editor source tree, or a Tools.ini/toolsdir
misconfig) **and** whether a **headless/command-line** pathing bake (MapCompiler/Editor flags) exists
that skips the GUI entirely. Fallback if the Editor is unusable on this hardware: offline Recast
generation from the `0x0a` geometry (high effort — RLTD container format RE).

### Why not just restore the original terrain doorway?
SV originally connected the blood cave via terrain edges in the **shared** level `Random09A`. The
merge deliberately keeps SVAERA's version of all shared levels (replacing them caused crashes/walls),
so that doorway is gone — which is why the author added a quest-portal teleport instead (see below).

---

## 🚪 Entrance bugs (block the blood cave even with a good navmesh)

Both verified in source; the quest-portal that teleports the player into the cave is broken two ways:
1. **Coordinate desync** — `tools/build_quest_files.py:33` hard-codes the teleport target to
   `(-2060,18,1322)` (the SV-original position), but `tools/svaera_plus_portals.py:347` grid-shifts
   the whole xBloodCave cluster by `(1663,0,922)`. The teleport lands ~1900 units into empty void.
2. **Wrong NPC** — `build_quest_files.py:29` drives NPC `silkroad_villager1.dbr`, which does **not
   exist** in the entrance level `HiddenValley01` (only native `silkroad_villager4` + the injected
   `portal_bloodcave_entrance.dbr` are there). The dialog/teleport never fires.

Fix: retarget the teleport to a real walkable point inside the shifted `BC_initialpathway`, and drive
the injected portal entity (or a real native NPC). Keep the quest-portal model (restoring the terrain
doorway via shared-level replacement is what caused the original crashes).

---

## 📜 Quest integration (NEW workstream — largely not done)

The prior work built only the *portal teleport* to get INTO the blood cave (and it's buggy). The
actual **Soulvizier content quests** (the questlines inside the blood cave and other SV areas) have
**not been integrated/verified**. Known signals: `open_bloodcave_portal.qst` is a dangling reference
(file absent), `bossarena.qst` is claimed in the README but doesn't exist, and the QUESTS-section
merge only carries names. This needs: an audit of which SV quests exist upstream vs. shipped, and a
plan + implementation to wire the SV area questlines. `tools/qst_format.py` is a fully-RE'd `.qst`
reader/writer (89/89 round-trip) available for this.

---

## 🧟 Content gaps (independent of the map fix — can run in parallel)

**P0 (release-blocking):**
- **Soul drops forced to 100%** — `tools/apply_svc_patches.py` `_force_100_pct_soul_drops` (called
  unconditionally by the build) overrides the tuned 66%/25% rates to 100% ("TESTING", never
  reverted). Gate it behind an explicit testing flag (default OFF).
- **Orphaned soul name-tags** — `tagSoulSVC9005` (Crowboar) & `9006` (Uber) exist in the `.arz` but
  not in shipped `Text.arc` → raw tag text shows in-game. Structural: `build_text_arc.py` isn't
  coupled to `build_svc_database.py`, so this recurs on any soul-roster change. Fix + add a build
  validator that fails loud if any `.arz` name/desc tag is missing from `Text.arc`.
- **Multiplayer never tested** (an explicit non-negotiable). Also SV's `RunEquation` MP spawn-scaling
  formulas fail to parse in AE → silently fewer spawns in MP.

**P1/P2:** Super Caravan "respec items" never implemented; Lite (DRX-free, −339 MB) build coded
(`bootstrap_working_mod.ps1 -LiteMode`) but never packaged/validated (mitigates the 32-bit
address-space D3D crash class); dead orphan `tools/apply_sv_classic_patches.py`; stale docs
(`SOUL_AUDIT.md`, `CHANGELOG.md`, `system_check.md`); `dist/` artifact stale vs HEAD; a few
code-hygiene items (shadowed `_find_record`, unchecked pet-skill return values).

---

## ⚠️ Deploy hazard — neutralize before any deploy

`local/Levels_merged.arc` (May 24, 662 MB, a stale build from a stray test run — ~zero SV content) is
**newer** than the good deployed map (`work/.../Levels.arc`, Mar 13, 683 MB, correct). `scripts/
deploy_to_custommaps.ps1:89` auto-copies `local → work` when local is newer, so **running deploy now
would clobber the good map**. Regenerate a correct `local/Levels_merged.arc` via
`tools/svaera_plus_portals.py` (which also drops the leftover diagnostic append-clone at idx 2281)
before deploying.

---

## 🚀 Steam release plan & hard blockers

Payload ~1.11 GB; Workshop can host it (SVAERA AERA is 1.86 GB live on appid 475150). Repo has working
`scripts/package_workshop.ps1` + `scripts/upload_workshop.ps1` (steamcmd, appid 475150). SteamCMD is
installed at `C:\steamcmd\steamcmd.exe`; never run to completion yet.

Hard blockers: (1) map fix must be stock-engine (this decision handles it); (2) 32-bit
address-space crashes → ship a Lite build + document the community 4GB LAA patch; (3) **legal** — the
mod bundles three upstreams wholesale; get written permission from amgoz1, soa, Dragonlord (dropping
DRX via the Lite build removes the largest permission dependency). Recommend dual distribution:
Workshop (auto-update) + moddb/Nexus zip (GOG/non-Steam, CustomMaps install).

---

## 🛠️ Build & deploy commands

- **Python:** use the `py` launcher (not `python`/`python3`); set `PYTHONIOENCODING=utf-8`.
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
**create a dedicated Custom Quest character** — never load a normal character into it, and never
"bounce" it (breaks characters).

---

## 📌 Key technical lessons (hard-won; don't relearn)

- **dtype preservation:** never pass explicit dtype to `set_field()` on cloned records — INT/FLOAT
  corruption silently zeroes values (pet spawn failure).
- **Permanent pets:** remove `spawnObjectsTimeToLive` (set to `[]`). Reference soul: Lyia Leafsong.
- **Pet.tpl vs Monster.tpl:** copying ANY equipment/loot field from Monster.tpl → Pet.tpl crashes the
  game (even changing values of existing fields). Only animation/skill fields are safe. Pet equipment
  must use `_set_pet_equipment()` with hardcoded item paths, not monster field copying.
- **Never `clone_record` for souls:** brings stat values that corrupt saved items; use bare
  `_ensure_record()`.
- **Soul icon paths:** `SVItems\jewelry\soul_{n,e,l}_icon.tex` (first path component = archive name).
- **`{^F}` prefix** required on soul name tags for pink/magenta text.
- **Enchanting** (epic/legendary) is baked into the `.arz` via `make_enchantable()` — the shippable
  mod has **no Game.dll dependency**. (An old Game.dll hex-patch exists as a local backup only.)
- **TQ saves bake item properties** at pickup — pre-patch items won't reflect DB changes; test with
  freshly dropped items.
- **Map format:** `world01.map` sections QUESTS(0x1b) GROUPS(0x11) SD(0x18) LEVELS(0x01) BITMAPS(0x19)
  0x10 DATA2(0x1a) DATA(0x02). `DATA2`/`BITMAPS` = minimap TGA, NOT pathfinding. `ints_raw` = 13×int32:
  [0..5] tile dims, [6,7,8] grid corner (world x,y,z), [9..12] GUID.

---

## 📂 Repo layout (orientation)

- `tools/` — the build pipeline: `build_svc_database.py`, `apply_svc_patches.py` (souls/patches),
  `svaera_plus_portals.py` (map merge), `build_section_surgery.py` (level-blob surgery + navmesh
  inject), `build_quest_files.py`, `qst_format.py`, plus `.arz`/`.arc` I/O and a pile of pathfinding
  RE scripts. NOTE: `apply_sv_classic_patches.py` (with underscore) is DEAD/orphaned — the live one
  is `apply_svc_patches.py`.
- `scripts/` — PowerShell deploy/package/upload/bootstrap.
- `upstream/` — extracted SV 0.98i / 0.9 / 0.41 sources (gitignored). `reference_mods/SVAERA_customquest`
  — the SVAERA base (gitignored). `local/` — big working scratch incl. decompiled world source
  (`decompiled_sv/`, `merged_source/`) and candidate maps (gitignored).
- `work/SoulvizierClassic/` — staged deploy source (the real, good map lives here). `backups/game_dll/`
  — Engine.dll/Game.dll backups. `docs/` — CHANGELOG, crash analysis, inventories.
