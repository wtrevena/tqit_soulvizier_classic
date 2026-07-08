# HANDOFF — LIVE PROJECT STATE (written 2026-07-07 night, for a ZERO-CONTEXT successor agent)

> READ THIS FIRST, then CLAUDE.md, then docs/AREA_WIRING_RECIPE.md (the map how-to) and the
> per-topic docs referenced below. Everything here is repo-derivable; no conversation context needed.

## 1. WHAT IS DEPLOYED RIGHT NOW (critical asymmetry!)

- DEPLOYED NOW: Workshop CANONICAL = build27 (map a1ba5db2 born-open portals + arz w/ toxeus-spawn + born-open invariants). Will LOCAL = TESTHUB map 96a9eb14 (+hub portals +toxeus spawn) over the SAME coupled arz. (superseded line:) map build26
  (`local/Levels_merged.arc`, md5 3f1b2e4d..., commit 0f9ceef tag build26-doors-hub) +
  Quests.arc (it-cap-complete, md5 74603c0d) + arz (masteries-supra-audit, md5 4e1acb48...) + Text.arc.
- **Will's LOCAL install** (`...My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassic/`)
  = the **TESTHUB variant** (`local/Levels_merged_TESTHUB.arc`) — canonical + 20 hub portal
  entities in the Silk Road cave + a Blood Toxeus test spawn outside the cave mouth.
  **NO CO-OP while TESTHUB is deployed** (byte-identity). REVERT = copy `local/Levels_merged.arc`
  over the deployed Levels.arc + cmp. Rolling backups: `local/Levels_deployed_prev.arc`,
  `local/Quests_deployed_prev.arc`, `local/db_backups/`, `local/save_backups/` (character zips).
- Workshop updates: `powershell -ExecutionPolicy Bypass -File scripts/package_workshop.ps1` then
  `scripts/upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0` (steamcmd session cached,
  no prompts). NEVER upload a TESTHUB artifact.

## 2. OPEN BUGS from Will's LIVE test session (2026-07-07 night, on TESTHUB) — the work queue

| # | Bug | Diagnosis state | Where |
|---|-----|-----------------|-------|
| A | ✅ FIXED+SHIPPED (build27-portals-born-open): the portals were GridEntranceDynamic = born-closed/invisible, quest never opened them. Swapped to base GridEntrance = born-open + always-visible, no quest dependency (DLL-proven). COUPLED deploy done: arz e8064cf9-successor + canonical map a1ba5db2 + TESTHUB 96a9eb14; Workshop pushed canonical; TESTHUB local. — was: Hub/door portals INVISIBLE | DynGridEntrance closed-state renders nothing; the quest open-action never reached them. Fix loop RUNNING (see §3): goal = portals open from raw data, no quest dependency. | workflow wf_c0012e88-64a |
| B | ✅ FIXED+SHIPPED (commit tag toxeus-spawn-fix; champion crowd-out was the cause - championChance=100 with 1 slot REPLACED the boss with a demon; now 1 boss + 2 demons guaranteed N/E/L at authored level, both placements, 5th invariant added; arz e8064cf9 deployed + Workshop pushed) — was: Blood Toxeus main monster doesn't spawn (his blood-demon adds DO) | Prime suspect: proxy difficultyLimitsFile=limit_area002 level bracket filters charLevel-40 main on Normal. Affects BOTH the hub test spawn AND the canonical secret-area spawn (build21 - likely never spawned for anyone). Fix loop RUNNING. | workflow wf_30460e48-ca1 |
| C | Sprite pit near occultist does NOT respawn sprites continuously | Compare our t1_pitspawner cluster config vs the LIVE Greece occultist pit (interval/max-alive/controller). Will is testing leave-and-return (per-level-load vs dead). | task #37A |
| D | Smoke density still far below SV (starts-at-entry region fog missing) | The C4 restore covered ENTITY emitters only; the REGION-ENV half (SD/0x18 or 0x09 env params) was never restored (vet hedge on record). Deep-parse SV SD/0x09 for HV01 region + Delphi occultist region, diff, restore. | task #37B |
| E | 'Temple Entrance - Locked ~ Sealed By Guardian' door in Blood Cave does NOT unseal after killing its guardian | Trace SV's unlock chain: quest Condition_MonsterDeath -> UnlockFixedItem? Candidates: controlling quest NEVER PORTED (re-audit the ~86 unported upstream .qst; the '4 questlines = complete' conclusion may be wrong), watched-monster record mismatch, or broken door binding. | task #37C |
| F | **NEW: summon souls spawn BROKEN pets** — "Soul of the Blood High Priest" grants "Call the Blood Blade-Dancer"; the summon appears as a FLOATING SCYTHE only, cannot move | Pet record wiring: floating-weapon-only = missing/mismatched mesh + animation table on the cloned pet. The souls wave created 6 pets (bwpriest/lillued x3 tiers) via the Boneash-clone pattern with "animation fields" as the deliberate difference — audit ALL wave-created pets + BOTH summon souls: mesh field, charAnimationTable, all visual refs must resolve AND match each other. Likely systemic across our created summons (Will's explicit concern). Compare field-by-field vs the WORKING Boneash/Lyia pets AND vs the source monster (bwpriest = the Blood Cult High Priest monster's mesh/anims). | NEW - fold into #37 wave or own loop |
| G | Esfri's chest (hidden blood-cave supra chest): Will opened it; whether a supra FORMULA dropped = UNANSWERED (ask him). Static chain verified. | pending Will |

VERIFIED WORKING live: rocks block; fountain visible+functional+safe+respawn-point (fixed via GROUPS
member position); caravan usable; letter drops (static); 66/25 release drop rates (hero no-drop is
correct behavior); chest quest opened; occult purple totems/atmosphere entities visible.

## 3. RUNNING WORKFLOWS - TWO live fix loops (contract suites STOPPED ON HOLD per Will 2026-07-07: resume later via Workflow({scriptPath, resumeFromRunId}) - entity=wf_87586bbf-b63, map=wf_8da16855-efe, scripts in the workflows/scripts dir; their specs stand in 4b + queue item 4):
- wf_87586bbf-b63 (ENTITY contract suite, spec 4b): new-files-only; on clean -> commit the validator + hook installer, run full-DB, then the BUG-F FIX WAVE (fix the broken pets it diagnosed, apply_svc_patches, after wf_30460e48 frees that file), rebuild arz (validator must then PASS), deploy, Workshop.
- wf_8da16855-efe (MAP contract suite, queue item 4): new-files-only; on clean -> commit, run vs both artifacts, wire into svaera_plus_portals (one line, documented), it gates all future map waves.
(original two below)

Both are Opus implement->vet loops; on completion their final report arrives as a task notification
(lost if session dead — instead read their transcript dirs; the last assistant message of the vet
agent = the verdict; artifacts land in the repo/scratch as documented in their briefs):
- `wf_c0012e88-64a` (portals visibility): transcripts at
  `C:\Users\willi\.claude\projects\C--Users-willi-repos\fc31fa12-e2e4-44ef-998c-7fe110587b8c\subagents\workflows\wf_c0012e88-64a`.
  On clean: commit scoped, rebuild BOTH map artifacts, redeploy TESTHUB locally + canonical->Workshop.
- `wf_30460e48-ca1` (Toxeus spawn brackets): same pattern; likely DB-side fix
  (apply_svc_patches proxy/pool records) -> rebuild arz (deterministic; FOUR fail-loud invariants
  must pass), deploy arz, Workshop update.
Resume/re-run: `Workflow({scriptPath: <script>, resumeFromRunId: <id>})` — scripts in
`C:\Users\willi\.claude\projects\...\workflows\scripts\`. If dead, just re-run the loop with the same
brief (they are written self-contained).

## 4. QUEUE (in order; tasks tracked in the session task list, restated here)

1. Consume the 2 running loops -> redeploy TESTHUB + Workshop.
2. **#37 live-fix round 2**: bugs C, D, E, F above (one map+DB wave, implement->vet).
3. **#35** Occult/Hunting UI recheck: static audit says trees clean (docs/MASTERY_AUDIT.md) —
   Will re-verifies the mastery SELECTION SCREEN in-game; if still wrong, the defect is in the
   selection-screen UI layer, not the skill trees. Plus Occult/Neidan scaling assessment
   (Occult content changes = PROPOSALS to Will only).
4. **#30** map contract suite (tools/validate_map_contracts.py; spec in the task/board + the failure
   classes are all documented in docs/: portal bindings, area-reachability, map<->arz resolution,
   GROUPS UID rule, quest-window, blob re-parse). Wire into every merge, negative-test each class.
5. **#28** comprehensive dropped-visuals restoration (docs/DROPPED_CONTENT_AUDIT.md driven).
6. **#31** souls quality pass (SEE RULES §5 — SV originals = design bible).
7. **#32** Toxeus encounter suite (10-25% canonical entrance spawn chance, rant scroll w/ MP
   per-player drops, Legendary stalker feasibility, 6-player checklist).
8. **#36** Cold Tombs ON HOLD (Will said hold; investigate-first plan in the task).

## 4b. TOP-PRIORITY NEW BUILD (Will's final directive 2026-07-07): ENTITY CONTRACT SUITE, COMMIT-BLOCKING

Build tools/validate_entity_contracts.py + wire as BOTH a build gate AND a git pre-commit hook
(hook runs when DB build scripts change; blocks the commit on failure). Goal: wiring gaps like
bug F (summon spawns a floating weapon, no body, immobile) become IMPOSSIBLE to commit.

Contract classes (beyond path-resolution - the existing 4 invariants already do that; these check
SEMANTIC COMPLETENESS AND CONSISTENCY):
1. PETS/SUMMONS: for every summonable (every spawnObjects target of every summon skill, transitively
   from every soul/item/skill grant): mesh EXISTS + charAnimationTable EXISTS + the anim table's
   animation set matches the mesh's rig family (derive the rig-compat rule from working exemplars:
   Boneash, Lyia, base-game pets - compare which anim-table/mesh pairings ship together); required
   Pet.tpl field-set completeness vs a working exemplar (no missing movement/controller fields -
   'cannot move' = likely missing controller/anim wiring); sounds/fx resolve.
2. SKILLS: per-class required-field completeness (a Skill_SpawnPet needs spawnObjects+TTL policy;
   an attack skill needs its projectile/fx chain; derive per-class required sets from base-game
   exemplar populations, not hand lists).
3. MONSTERS: mesh+animTable consistency (same rule as pets), skill refs resolve, loot chains
   resolve, classification present.
4. SOULS/ITEMS: full transitive grant-chain terminates in COMPLETE entities (skill -> pet -> mesh/
   anims), icons resolve, tiers n/e/l all present and consistently laddered.
5. NEGATIVE-TEST every contract class (break a copy, prove the gate fires) - the established pattern.
Run modes: fast static (pre-commit, against the last built arz + the diff'd records) and full
(build gate, whole DB). Wire into scripts/bootstrap + build_svc_database like the 4 invariants.
FIRST TARGET: bug F itself - the suite must fail on the current broken blade-dancer pet, then the
fix (correct mesh/animTable per the source monster) makes it pass. Same wave fixes ALL wave-created
pets it flags. Implement->vet loop, Opus max.
## 5. STANDING RULES (Will's law — NEVER violate)

- **Occult + Hunting masteries contain Will's HAND-TUNING.** Never revert to SV. Only objectively
  dead refs may be fixed there, reported separately. Content-level changes = proposals to Will.
- **Souls taste hierarchy**: (a) Will's explicit build-script edit blocks = LAW; (b) SV ORIGINAL
  souls = the design bible for everything we generated; (c) more fun/powers welcome, thematically
  coherent. All soul refs must resolve (validate_soul_augments).
- **Implement->vet loop mandatory** (independent Opus-max implementer -> independent Opus-max vet ->
  re-implement until clean). Never ship self-vetted work. All Opus now (Fable exhausted).
- **Commit + tag BEFORE every build Will tests**; rolling backup before every deploy; deploy
  couplings: Levels+Quests together when both changed; arz+Text together when tags changed.
- **TESTHUB artifacts are LOCAL-ONLY**, never Workshop. No co-op while deployed.
- **The campaign ends at Hades (Immortal Throne) for ALL DLC combos** (it-cap-complete; proven by
  256-controller sweep). Don't reopen DLC acts. DLC integration = CANCELLED by Will.
- Never touch map.dat. Steam-clean only (no DLL patches). 6-player MP max (TQAE native).
- Build gates: FOUR DB invariants (soul-leaks, soul-augments, supra-refs, tags) + per-wave map gates
  (verify_merged_bc_navmeshes, entrance_landing_check --check-merged, area_selfcheck,
  cluster_seam_check, overcoverage_check, corridor/gate_doors_hub) — a build that fails any gate
  DOES NOT SHIP.

## 6. KEY DOCS INDEX (docs/)

AREA_WIRING_RECIPE (the map how-to distilled from 17 wall attempts) · SV_AREAS_CAMPAIGN_PLAN + _LOG ·
DOORS_HUB_LOG (hub/doors/respawn/C4) · SPARTA_CORRECTIONS_LOG · ENTRANCES_POLISH_LOG ·
NAVMESH_OVERCOVERAGE_RCA (rocks/obstacle carving) · BLOODCAVE_QUESTS_RCA (letter/secret-wall) ·
QUEST_STATE_INJECT (quest identity md5 + .que format + save tooling) · LETTER_SPAWN_DIAGNOSIS ·
IT_ENDPOINT_AUDIT (the cap) · MASTERY_AUDIT · UBER_WEAPONS_AUDIT (supra; Blood Whisper + Paragon
verified) · SOULS_COMPLETENESS_AUDIT · BOSS_SOULS_DESIGN (60-soul roster) · BLOOD_TOXEUS_DESIGN
(Hemorrheus -> renamed Toxeus the Murderer, Devourer of Blood) · MULTIPLAYER_COMPAT + SHARE_AND_PLAY
+ STEAM_RELEASE · DROPPED_CONTENT_AUDIT · MODDING_PLAYBOOK (engine internals) · WALL_ATTEMPT_LEDGER.

## 7. BUILD & DEPLOY CHEAT SHEET

- arz: `py tools/build_svc_database.py upstream/soulvizier_098i/Database/database.arz
  upstream/soulvizier_0.9/Database/database.arz upstream/soulvizier_041/Database/database.arz
  work/SoulvizierClassic/Database/SoulvizierClassic.arz "<TQAE install>/Database/database.arz"`
  (deterministic; prints invariant banners; RELEASE drop rates are the default).
- Text: `py tools/build_text_arc.py upstream/soulvizier_098i/Resources/Text_EN.arc
  work/SoulvizierClassic/Resources/Text.arc work/SoulvizierClassic/Database/uber_soul_tags.txt`
  (the Database/ manifest is the LIVE one; root/local copies are stale decoys).
- Quests: `py tools/build_quest_files.py` (ports + neutralizations incl. widowletter spawn removal
  + both IT-cap quests).
- Map: `py tools/gen_bc_navmeshes.py` (donor regen, config-driven CLUSTERS) then
  `py tools/svaera_plus_portals.py` (merge; SVC_TEST_HUB=1 env for the hub variant).
- Python: `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`, PYTHONIOENCODING=utf-8.
- Git: tags mark every tested build (build13..build26, souls-wave-v1, it-cap-complete, etc.).
  Stale working-tree strays to NEVER commit: fix_mc_output.py, hybrid_merge.py, create_uber_souls.py
  (if present), populate_svbake_records.py, setup_svbake_world.py, wrl_format.py,
  reconcile_seam_heights.py, docs/blood_cave_walkin_entrance_plan.md.

## 8. WILL'S CHARACTER / SAVE FACTS

Character `_Toxeus` (lvl ~38 Stalker). Save backups: `local/save_backups/*.zip` (+hash manifests).
`_ToxeuQ` sandbox copy DELETED (was 14MB; Steam Cloud quota). Steam Cloud sync errors = quota;
never accept cloud-over-local. Quest adoption on existing characters WORKS (engine auto-adopts;
hidden/controller quests never show in the journal - do not misdiagnose from journal absence).
