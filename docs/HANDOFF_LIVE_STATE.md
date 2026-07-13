# HANDOFF LIVE STATE

> ## BUILD37-dev DEPLOYED TO DEV (2026-07-13) - TESTHUB traveler hub + coupled arz/Text/Quests; STEAM UNTOUCHED
> **The DEV entry `SoulvizierClassicDEV` now runs build37-dev** (local TESTHUB build for Will's
> Helos-traveler-hub tour before anything more ships to Steam). All 4 coupled artifacts were copied to
> `CustomMaps/SoulvizierClassicDEV` and md5-verified on disk (source + destination both hashed):
> - `Resources/Levels.arc` = **`841c56cd2b6b8a87209327cb02529d23`** (688,688,154 B): TESTHUB map
>   (`SVC_TEST_HUB=1`), 17 hub-gated traveler/return NPCs. Canonical `local/Levels_merged.arc` UNCHANGED
>   (`60a62880`) - never rebuilt.
> - `Database/SoulvizierClassicDEV.arz` = **`56d6db221466eb991804f001aa1a83a5`** (55,334,381 B): first
>   full-registry DB build (9 modules, order hash `7ed29402a38d`) - registry bosses
>   (neferkha/toxeus_suite/polis_vault/diadochi/four_generals) + skill_quality de-filler + H/O
>   improvements + lane-A (BL-ENSLAVER-SPAWNS / smoke-FX / bloodhound). Record-diff vs build36 arz =
>   124 ADDED / 0 REMOVED / 1394 CHANGED, 0 unexplained, 0 clobbers.
> - `Resources/Text.arc` = **`8c7229db978fd5ecc24a94053c30306e`** (377,150 B): golden A7 guard PASS
>   (41 waived / 0 other); validate_tags PASS.
> - `Resources/Quests.arc` = **`838bdc3a3716b5e9028c076317e99608`** (194,581 B): exactly 17 Helos-hub
>   travel triggers appended to `sv_commonmechanics.qst`; entry-diff vs build36a = ONLY that file.
>   (Levels+Quests couple: the hub NPCs ride the map, their dialog triggers ride Quests; the 256-slot
>   QUESTS window parity is preserved.)
> - **STEAM = build36a canonical, UNTOUCHED** (Workshop item 3759792705: arz `63ca7cf8` /
>   Levels `60a62880` / Text `2af4ce38` / Quests `56acee66`). TESTHUB is LOCAL-ONLY; never uploaded.
> - **To see it, Will only needs to fully quit + restart TQ** (Steam was already restarted today;
>   TQ was closed at deploy time). Tour: `docs/WILL_TEST_GUIDE.md` HELOS TRAVELER HUB section.
> - **Rollback to build36a on DEV:** copy `local/Levels_merged.arc` (`60a62880`) -> DEV
>   `Resources/Levels.arc`; rebuild the arz from git tag `build36` (or restore from `local/db_backups/`);
>   `local/Text_deployed_prev.arc` (`2af4ce38`) + `local/Quests_deployed_prev.arc` (`56acee66`) -> DEV
>   Text/Quests. Tag `build37-dev`; gate record at `efc1933` (`docs/BACKLOG.md`).
> - **Two non-blocking tuning-lane notes** (not gate failures, for a human glance): (1) pcsafe
>   `earthfury_ring` `skillCooldownTime` is 16.0 in this build vs 5.0 in build36a (opposite the A4
>   "16->5" build-log narrative); (2) stale "x60" comment in
>   `toxeus_suite._sweep_inject_legendary_stalker` (the Enslaver monolith sweep is now x300).

> ## BUILD36a P0 HOTFIX (2026-07-12) - walk-through travel portals REMOVED; NPC-dialog travel only
> **LIVE STEAM breakage fixed** (item 3759792705): "cant walk south in Helos - teleported to Garden of Merchants with no way back." Per Will's TRAVEL LAW every walk-through/proximity teleport we authored is stripped from the canonical map; ALL cross-area travel now routes through the NPC boat-dialog (Helos portal-master out; each area's `svc_testhub_return` NPC or an SV rift shrine back). Map tooling only (`tools/build_section_surgery.py`) - **arz/Text/Quests UNCHANGED from build36** (the return-NPC record + its dialog already shipped in the build36 arz/Quests, inert until the canonical map now places the NPC).
> - **Fix commit `0f08297`; tag `build36a`.** Canonical `Levels_merged.arc` md5 **`60a628807c1746e7bbde14946de62107`** (was `b42be44f`; 688,682,781 B). arz **63ca7cf8** / Text **2af4ce38** / Quests **56acee66** = build36, reused byte-identical (no DB/Quests rebuild).
> - **Blob-diff vs build36 canonical = EXACTLY 9 changed level blobs, 0 added/removed:** the 7 portal levels (startingfarmland06d, hiddenvalley01, gardenofmerchants, rhodes_secretvista_01, darkforestenter, maze03, catacube02_floorlast) + crypt_floor1 + spartacryptlevel2. Gates GREEN: navmeshes 24/24, seam-lattice 24 aligned/0 misaligned, entrance-landing PASS, map contracts 0 P0 / 0 P1 (3 pre-existing native/DLC P2).
> - **Removal inventory (20 authored teleports):** 16 walk-through GridEntrance/GridExitOneWay/map_portal_aura REMOVED from INJECT_SPECS (Helos H1/R2 + swirl; HV01 G1/G4 + swirl; Garden G2/G3/H2/R1 + swirl; vista S1/S4; Secret S2/S3; maze03->Uber; catacube->Sparta) + 4 native 0x06/0x05 return doors DISABLED (SC2 REWRITE_0X06, crypt APPEND_0X06, crypt REMOVE_0X05 - SV-original left untouched). KEPT: Helos + Olympus portal-master NPCs (dialog travel); rift shrines teleportshrine_gom + teleportshrineorient01. PROMOTED TESTHUB->canonical: 4 `svc_testhub_return` NPCs (Garden/Secret/Uber/Sparta). TESTHUB variants unchanged, local-only.
> - **STEAM: SHIPPED 2026-07-12** - SteamCMD "Upload complete", item 3759792705, Visibility 0 (public), cached login (no re-auth). Push-gate PASSED (F9 dist==work + F7 contract suite 0 P0/0 P1) after ONE justified whitelist entry (see below). **DEV (SoulvizierClassicDEV): map STAGED to work/ (`60a62880`); the CustomMaps DEV `Resources/Levels.arc` copy is DEFERRED** while TQ.exe is running (Will actively playing / crash-loop recovery) - copy `local/Levels_merged.arc` over the DEV `Resources/Levels.arc` when TQ exits; NEVER kill TQ.exe.
> - **PUSH-GATE WHITELIST (ship operator):** `tools/contracts/whitelist_quests.txt` +1 justified line `QST-DOOR-UNLOCK bossarena.qst :: records/quests/portal_olympianarena1.dbr` - removing the portal left bossarena.qst's unlock action naming an unplaced door (engine name-lookup no-ops; harmless; intended P0 consequence). Follow-up: a future Quests.arc rebuild should drop the dead action, then remove the whitelist line.

> **BUILD36 SHIPPED 2026-07-12** to Steam Workshop (item 3759792705, "Upload complete") AND the DEV entry (SoulvizierClassicDEV, hash-verified). Tag `build36` @ 9f96340. arz md5 63ca7cf8, canonical Levels_merged md5 b42be44f, Text 2af4ce38, Quests 56acee66 (reused, unchanged). CANONICAL map both targets (TESTHUB rebuild skipped - quota; canonical carries all content). What shipped: 5 uber bosses (Dorus/Tantalus/Charon/Mnemophage/Ephialtes) + Ereban relic + Enslaver rework (skeleton + 4 demon-strength marauders + orbs) + pet overhaul (4 summon-bug fixes) + 18 mastery grafts + Rune Golem + 6 soul RCA fixes + Shadow Stalker + Bloodcrow/Makaria/Anapaest CDs + Flash Powder rework + 21 handcrafted souls + Obsidian balance + Act-5->Epic fix + Vort red + crash mitigation. See docs/WILL_TEST_GUIDE.md (test menu + boss locations + SV areas) and docs/NEXT_STEPS_BUILD37.md (everything unfinished). MP TESTED+works.

---

# HANDOFF - LIVE PROJECT STATE (Soulvizier Classic)

> **Trust level: LIVE - keep this current.** This is the single current-state board. A brand-new
> agent reads `CLAUDE.md` → `docs/README.md` → this file, in that order.
> Open bugs/queue live in `docs/BACKLOG.md`; how-to recipes live in `docs/PLAYBOOK.md`.
> Long history was moved to `docs/ARCHIVE_2026-07.md` (do not trust it for current state).
> Last updated: 2026-07-08 (post workshop-wrapper-fix + doc consolidation).

---

## 1. WHAT THE MOD IS (2 lines)

Soulvizier Classic is a total-conversion Custom Quest mod for **Titan Quest Anniversary Edition
(TQAE)** - SV 0.98i back-ported and merged with SVAERA + the DRX visual overhaul, headlined by
hundreds of collectible monster "souls", a restored/walkable Soulvizier blood cave and its SV area
questlines, ~60 boss souls, 10 masteries, and a new blood superboss (Toxeus the Murderer).
It ships as content-only data (`.arz` database + `.arc` resources); no DLL/exe patch - Steam-clean.

---

## 2. ARTIFACT MODEL (where everything lives)

| Location | Role |
|---|---|
| `work/SoulvizierClassic/` | **Shipped staging.** The exact tree that gets packaged: `Database/SoulvizierClassic.arz` + `Resources/*.arc` (Levels/Text/Quests/DRX/SV/XPack). Regenerated by the build; gitignored. |
| `local/` | **Build outputs + backups.** Canonical map build `Levels_merged.arc`, hub variant `Levels_merged_TESTHUB.arc`, per-build baselines (`Levels_merged.buildNN-baseline.arc`), rolling `*_deployed_prev.arc`, `db_backups/`, `save_backups/`, navmesh donors in `editor_normalized/`. gitignored. |
| `dist/workshop/content/SoulvizierClassic/` | **Workshop staging.** What `package_workshop.ps1` writes: a SINGLE `SoulvizierClassic/` wrapper with `database/` + `resources/` inside. SteamCMD uploads the CONTENTS of `dist/workshop/content` (one child). |
| `dist/SoulvizierClassic_CustomMaps.zip` | **Manual/ModDB share artifact** (no-Steam co-op path - see `SHARE_AND_PLAY.md`). |
| `<TQ docs>/CustomMaps/SoulvizierClassic/` | **Local deploy target** (the running game reads here). Full path: `C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassic`. |
| Steam Workshop item **3759792705** | **The public listing** (appid 475150). Subscribers download here. `local/workshop_item_id.txt` holds the id. |

`tools/` (Python build pipeline), `scripts/` (PowerShell deploy/package/upload), and `docs/` are the
COMMITTED source of truth. `upstream/` and `reference_mods/` are gitignored source inputs.

---

## 3. CURRENT STATE (build27 + workshop-wrapper-fix, all verified on disk 2026-07-08)

> **DB-lane UPDATE 2026-07-09 (build30.2):** the shipped arz is now the STARTER-CHEST-FIXED
> build30.2 (`work/.../SoulvizierClassic.arz`, 54,658,764 B, md5 `3f60574155d18f24a28658725093d699`;
> record-diff vs build30 `45be22b8` = exactly `tutorialpotionchest.dbr`). Root cause + lesson in
> `BACKLOG.md` -> RESOLVED -> B-STARTER-CHEST. The table below is otherwise build27-era history
> (builds 28/29/30 shipped 07-08/07-09 without this file being refreshed; map lane is at build31b
> in git, not yet uploaded at the time of this note).

**Published Workshop content = build27 canonical.** Verified via fresh steamcmd download; sizes/MD5s
below re-verified against `work/` and the deployed CustomMaps copy on 2026-07-08.

| Artifact | Size (bytes) | MD5 | Notes |
|---|---|---|---|
| `Levels.arc` (canonical) | 688,691,849 | `A1BA5DB2F00FFA067A808753A2E1EAC5` | born-open portals + Toxeus spawn map. `work/.../Levels.arc` == `local/Levels_merged.arc` byte-identical. |
| `SoulvizierClassic.arz` | 54,529,030 | `7C6E209988F0CE815BAF35F058B6A0A8` | sha256 `5014f1903aa4163adaeb8c35fd71ca8fe36db2a7293aa874932660619b600c8f`. Toxeus-spawn fix + born-open invariants + mastery/supra repairs. |
| Workshop package | - | - | exactly **53 files** under one `SoulvizierClassic/` wrapper. |

- **Workshop packaging bug is RESOLVED (2026-07-08, commit `1851203`, tag `workshop-wrapper-fix`).**
  The item root is now a single `SoulvizierClassic/` wrapper (was two broken mods "database" +
  "resources"). `package_workshop.ps1` stages to `dist/workshop/content/SoulvizierClassic/{database,
  resources}`, wipes the stale wrapperless `dist/workshop/SoulvizierClassic` every run, asserts the
  content root has exactly one child, has a **fail-loud TESTHUB MD5 guard** (aborts if the packaged
  `Levels.arc` MD5 == `local/Levels_merged_TESTHUB.arc`), and prints the packaged size + MD5.
  `upload_workshop.ps1` points the vdf `contentfolder` at `dist/workshop/content` and re-asserts the
  single wrapper before uploading. Full recipe: `docs/PLAYBOOK.md` §3.
- **Item is PUBLIC** (`-Visibility 0`). Updates push with:
  `package_workshop.ps1` → `upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0`
  (steamcmd session cached, no prompts). NEVER upload a TESTHUB artifact.
- **Known content gap (queued, not yet fixed): 8 Text.arc tags render raw** (Blood Toxeus / Crimson
  Verdict names + descriptions). See `BACKLOG.md` → `B-TEXT-TAGS-1`. Fix = coupled arz + Text push.

---

## 4. DEPLOY ASYMMETRY - TESTHUB vs canonical (critical; verified on disk)

Will's LOCAL install runs a **different map** than the Workshop:

- **Workshop / canonical map:** `Levels.arc` `A1BA5DB2…` (688,691,849 B). Co-op-safe (byte-identity).
- **Will's LOCAL CustomMaps map:** the **TESTHUB variant** - `local/Levels_merged_TESTHUB.arc`
  `96A9EB14C88E308E9F850515526C23E4` (688,687,885 B), currently deployed to
  `CustomMaps/SoulvizierClassic/Resources/Levels.arc` (confirmed on disk 2026-07-08). It adds ~20 hub
  portal entities in the Silk Road cave + a Blood Toxeus test spawn at the cave mouth.
- Both run over the **same** build27 arz (`7C6E2099…`, 54,529,030 B) - the arz/Quests/Text are the
  shared coupled build, so only the map differs.
- **TESTHUB is LOCAL-ONLY. No co-op while it is deployed** (MP requires byte-identical maps). It must
  NEVER be uploaded (the packager's TESTHUB guard enforces this).
- **Two entries in Will's in-game map list:** Will is ALSO subscribed to item 3759792705, so his
  "Custom Quest" list shows two `SoulvizierClassic` entries - the subscription copy (canonical,
  under Steam's `steamapps/workshop/content/475150/3759792705/`) and his local TESTHUB (under
  `CustomMaps/`). This is expected; the local CustomMaps copy is the TESTHUB one.

**REVERT the TESTHUB (restore co-op-safe canonical locally):**
```
cp local/Levels_merged.arc "<DEPLOY>/Resources/Levels.arc"   # canonical map
cmp -s local/Levels_merged.arc "<DEPLOY>/Resources/Levels.arc"   # must be byte-identical
```
The arz/Quests/Text need no change (already the shared build). After this, local == Workshop item
and MP is safe. Rolling backups if needed: `local/Levels_deployed_prev.arc`,
`local/Quests_deployed_prev.arc`, `local/db_backups/`, `local/save_backups/`. Recipe also in
`docs/PLAYBOOK.md` §3 (deploy).

---

## 5. OPEN WORK → see docs/BACKLOG.md

`docs/BACKLOG.md` is THE single bug/queue board. Current live-test findings (build27, Will's
2026-07-07/08 sessions), summarized - read BACKLOG for full detail, cause, and fix lane:

- **P0:** `B-PORTAL-1` portals render as flat blue panels (need real mesh/FX); `B-PORTAL-2` a portal
  blocks the walkway (forced teleport); `B-PORTAL-3` return/one-way + all Duister (Secret Place)
  portals broken; `B-SUMMON-1` summons spawn naked / floating-scythe / immobile; `B-TOXEUS-1` Blood
  Toxeus shroud is GREEN, should be RED.
- **P1:** `B-SPRITE-1` pyre sprites do not respawn; `B-TEMPLE-DOOR-1` sealed temple door never unseals
  after the guardian dies; `B-SMOKE-1` region smoke density far below SV.
- **P2 / pending:** `B-CHEST-1` did an Esfri supra formula actually drop? (ask Will); `B-DUISTER-EXPLORE`
  full walk-test of all 5 hub destinations once portals are fixed; `B-TEXT-TAGS-1` the 8 raw tags.
- **Standing queue (not new bugs):** entity contract suite (owns B-SUMMON-1), map contract suite,
  mastery selection-screen recheck, souls quality pass vs SV originals, Toxeus encounter suite,
  dropped-visuals restoration, Cold Tombs (ON HOLD). Cut-by-design areas: `docs/CUT_CONTENT.md`.
- **Workshop feedback:** players report via Workshop comments on item 3759792705 - triage into
  BACKLOG (see its WORKSHOP FEEDBACK section).

---

## 6. STANDING RULES (Will's law - never violate)

- **Implement→vet loop is MANDATORY** for any non-trivial change: independent implementer (Opus max)
  → independent vet (Opus max) that reproduces every claim from raw bytes → re-run until clean.
  Never ship self-vetted work. (Fable is exhausted - all Opus now.) Detail: `docs/PLAYBOOK.md` §0.
- **Commit + tag BEFORE every build Will tests**; roll a backup before every deploy.
- **Deploy couplings (ship together or not at all):** `Levels.arc` + `Quests.arc` when both changed
  (single-letter guarantee + neutralizations); `arz` + `Text.arc` when tags changed; the born-open
  **portal swap couples arz + BOTH maps** (60-byte 0x14 read must stay aligned).
- **TESTHUB artifacts are LOCAL-ONLY**, never Workshop; no co-op while deployed.
- **Occult + Hunting masteries hold Will's HAND-TUNING** - never revert to SV; only fix objectively
  dead refs, reported separately. Content-level changes = proposals to Will only.
- **Souls taste hierarchy:** (a) Will's explicit build-script edit blocks = LAW; (b) SV ORIGINAL
  souls = the design bible for everything generated; (c) more fun/powers welcome if thematically
  coherent. All soul refs must resolve.
- **The campaign ends at Hades (Immortal Throne) for ALL DLC combos** (proven by 256-controller
  sweep). Do not reopen DLC acts. DLC integration = CANCELLED by Will.
- **Never touch `map.dat`. Steam-clean only** (no DLL patches). 6-player MP max (TQAE native).
- **Build gates are fail-loud** - a build that trips any gate does NOT ship: 5 DB invariants
  (soul-leaks, soul-augments, supra-refs, tags, spawn-eligibility) + per-wave map gates
  (verify_merged_bc_navmeshes, entrance_landing_check, engine_corridor_full, cluster_seam_check,
  overcoverage_check, gate_doors_hub, portal-openness). Gate list: `docs/PLAYBOOK.md` §12.

---

## 7. BUILD & DEPLOY - see docs/PLAYBOOK.md

The full, current build/deploy/Workshop command reference is `docs/PLAYBOOK.md` §2–3. Quick pointers:
- Database: `py tools/build_svc_database.py <098i> <0.9> <041> work/.../SoulvizierClassic.arz <TQAE base arz>`
- Text: `py tools/build_text_arc.py <098i Text_EN.arc> work/.../Text.arc work/.../Database/uber_soul_tags.txt`
- Quests: `py tools/build_quest_files.py`
- Map: `py tools/gen_bc_navmeshes.py` then `py tools/svaera_plus_portals.py`
  (`SVC_TEST_HUB=1` env writes the TESTHUB variant to its own file).
- Python: `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`, `PYTHONIOENCODING=utf-8`.
- Deploy local: `scripts/deploy_to_custommaps.ps1`. Package/upload Workshop: `scripts/package_workshop.ps1`
  then `scripts/upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0`.
- Determinism is your friend: rebuild twice, compare MD5; a vet should reproduce the exact MD5.

---

## 8. WILL'S CHARACTER / SAVE FACTS

Character `_Toxeus` (~lvl 38 Stalker). Save backups: `local/save_backups/*.zip` (+ hash manifests).
The `_ToxeuQ` sandbox copy was DELETED (Steam Cloud quota). Steam Cloud sync errors = quota; never
accept cloud-over-local. Quest adoption on existing characters WORKS (the engine auto-adopts newly
loadable quests; hidden/controller quests never show in the journal - do not misdiagnose from journal
absence). The mod is a total conversion: always use a dedicated Custom-Quest character; never load a
normal character into it or "bounce" a character between mod and base game (corrupts the character).

---

## 9. GOTCHAS / STALE-STATE POINTERS

- The **LIVE** `uber_soul_tags.txt` is `work/SoulvizierClassic/Database/uber_soul_tags.txt`;
  root-level and `local/` copies are STALE DECOYS.
- The game LOCKS `Levels.arc` while running - a `cp` may fail "Device or resource busy"; poll until
  it unlocks to deploy.
- NEVER commit these parked/other-lane strays: `tools/fix_mc_output.py`, `tools/hybrid_merge.py`,
  `tools/create_uber_souls.py`, `tools/populate_svbake_records.py`, `tools/setup_svbake_world.py`,
  `tools/wrl_format.py`, `tools/reconcile_seam_heights.py`, `tools/svaera_plus_portals.py` (has
  uncommitted other-lane changes - coordinate before touching), `tools/debug/gate_doors_hub.py`,
  `docs/blood_cave_walkin_entrance_plan.md`, `docs/BLOOD_TOXEUS_DESIGN.md`, `docs/DOORS_HUB_LOG.md`.
  Stage files explicitly; never `git add -A`.
- The two in-flight contract-suite workflows (entity + map) were STOPPED on hold; their run IDs +
  transcript paths + the full entity-contract-suite spec are preserved in `docs/ARCHIVE_2026-07.md`.
