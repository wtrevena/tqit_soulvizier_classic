# MASTER HANDOFF - 2026-07-12 night (written under imminent throttle; READ THIS FIRST)

> Successor agent: this supersedes-and-consolidates NEXT_STEPS_BUILD37.md (still valid for
> detail) + the BACKLOG records. Read order: this file -> memory board
> (tq-soulvizier-2026-07-resume.md) -> docs/BACKLOG.md -> docs/NEXT_STEPS_BUILD37.md.
> Model law: Will's main-loop tokens are precious (Fable = ~100x Opus). Delegate ALL work to
> Opus 4.8 max-effort subagents via Workflow (implement -> independent vet -> loop until GO);
> Sonnet 5 for log/QA checks. Orchestrator only coordinates.

## 1. LIVE STATE
- **Steam Workshop item 3759792705 = build36** (public). Files: canonical Levels.arc
  b42be44f891775f110262da74d714b32, arz 63ca7cf858e4f60f2f9bec8f9eb4ef8f, Text
  2af4ce386578ea144177a3227e07e048, Quests 56acee660e0c3dc7408f7d985231338c. Tag `build36`.
- **DEV entry (SoulvizierClassicDEV) = the same build36 set** (Will's active play surface;
  his char _Toxeus's progress lives HERE - the Steam entry has a separate quest namespace).
- main @ HEAD: build36 + docs/BACKLOG records + ⚠️ **tools/occult_hunting_golden.json is
  BROKEN on main** (merge e686130 committed partial conflict markers ~line 174395; repair =
  union of both waiver sides; lane A of the running workflow owns this fix).
- GO-vetted branches waiting: feat/patches-registry (in ho-ui), feat/b37-hunting-occult
  (1815faf), feat/b37-ho-ui (2824a7b), feat/b37-{skill_quality 0f43e33, toxeus_suite cbe5c7c,
  diadochi 7184c9a, polis_vault e076e46, neferkha 5fe4a4c, visuals cc26574}.
  **feat/b37-four_generals (91b71d9) = UNVETTED, excluded until vetted.**

## 2. THE THREE P0s (status)
- **P0-A OPEN, LIVE ON STEAM: Helos-south walk-through teleport -> Garden of Merchants, no
  way back.** Fix = remove ALL authored walk-through/proximity teleports from canonical
  (keep NPC-dialog travelers; ensure an NPC-dialog return path from Garden/Secret Place),
  rebuild canonical ALONE, ship build36a. **TRAVEL LAW (standing): NO walk-through
  teleports ever - only talk-to-NPC confirm-dialog travel** (exemplars: Helos portal-master
  build32, first-cave Garden traveler).
- **P0-B RESOLVED (no shipped bug): Will's "quests blocked/doors closed"** = save-side
  crash-loop damage (byte-proof: both deploy targets pure build36; QUESTS registry perfect,
  255 entries, 0 delta vs b33/34/35). Recovery for Will: clean reload reopens doors (tokens
  re-evaluated on load); if progress truly lost, restore backups/characters/20260709_155432
  with TQ closed, guard Steam Cloud. NEVER ship a map "fix" for this.
- **P0-C PINNED: the blood-cave crash = heap corruption in the NAVMESH-LOAD path**
  (ProcessRLTD streaming deeper chambers; 5/5 dumps identical ancestor chain; map-side -
  the petLimit arz mitigation was provably a no-op). Full dossiers:
  docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md + WER_FINDINGS_2026-07-12.md.
  FIX WAVE (heavy, run after build37-dev + Will's tour): (1) CONFIRM first - Frida
  live-probe while Will reproduces (exact hooks in the dossier; no system changes) or
  Page-Heap (NEEDS Will's approval: registry IFEO + 32-bit OOM risk); (2) then EITHER
  Fix B cluster relocation (GRID_SHIFT in svaera_plus_portals.py + donor regen; PRESERVE
  the Random09A/HiddenValley01 entrance abutment) OR interior GridEntrance transitions
  between deep chambers (native streaming doors = allowed; caps co-resident navmeshes).
  Meanwhile Will: save/town-portal often between deep chambers.
  Hygiene (separate, next DB build): 6 summoned-bloodhound dyingFxPak dangling refs.

## 3. IN-FLIGHT WORKFLOW (dies on throttle - RESUME IT FIRST)
`wf_6f65899d` (task wltudc6en), script:
`C:\Users\willi\.claude\projects\C--Users-willi-repos\fc31fa12-e2e4-44ef-998c-7fe110587b8c\workflows\scripts\p0-hotfix-then-b37-wf_78640c9e-5cf.js`
Resume: `Workflow({scriptPath: <above>, resumeFromRunId: 'wf_6f65899d-edc'})` - completed
agents replay from cache; read the journal.jsonl in its transcript dir first.
Phases: [P0-A hotfix impl->vet->canonical build->ship build36a Steam+DEV] ->
[lane A: golden repair + merge the 6 GO branches + registry-only H/O wiring + SHAPE LAW] ∥
[lane B: HELOS TRAVELER HUB in worktree feat/b37-helos-portals - one talk-to-travel NPC per
target (Obsidian Halls, Sparta Crypt L2, Garden, Secret Place, Boss arena, Dorus/Medea,
Tantalus, Charon/Golden Bough, Mnemophage, Ephialtes, warband), TESTHUB-flagged, return
travelers, doc section w/ Knossos + Sparta door locations] -> [build DB->Text->TESTHUB,
record-diff audit vs baseline arz 63ca7cf8, zero unexplained] -> [DEV-only deploy, tag
build37-dev]. ⚠️ TQ-SESSION GUARD baked into briefs: NEVER kill TQ.exe / restart Steam
while TQ runs - wait for a window or return blocked with staged state.
**WILL'S SHAPE LAW**: cast abilities = SQUARE (Tempest, Poison Gas Bomb); passives/procs/
enhancements = CIRCLE (luckyhit, multishotbolttrap, takedown_eviscerate, dual_blade,
herbalism, corneredrage - the last 3 are a law-driven reversion; FLAG to Will in the report).

## 4. THE DEVELOPMENT PLAN (ordered)
1. Finish wf_6f65899d: build36a (P0-A) to Steam; build37-dev to DEV.
2. **Will's traveler-hub tour** on DEV (docs/WILL_TEST_GUIDE.md has the boss list + menu).
   Fix anything he reports. THEN promote build37 to Steam (canonical map = build36a's;
   arz+Text = build37; Quests unchanged) - full gate battery + push-gate.
3. **b37 MAP PASS** (one wave, all accumulated placements): Polis vault cage interior
   (Guardian + horde + 5 majestic chests - DB module polis_vault is merged; Will asked
   about this explicitly), Helepolis placement (Elysian_Fields_03 idx 776, surveyed),
   Menoetes hall + general guards, Neferkha tomb injection, Toxeus ambush proxy
   (drxFirstRoom), visuals-wave co-locations, Garden-portal-NPC removal from the first
   cave (Will's standing order), add Polis vault to the Helos traveler hub, Vashkarr-scale
   clipping checks. QUESTS-section parity is sacred (build22 law: 255-entry layout,
   identity+order; P0-B's RCA verified current parity - keep a parity check in the wave).
4. **P0-C crash fix wave** (section 2; confirm-first, then map surgery; implement->vet).
5. four_generals salvage (worktree has commits; vet before anything ships).
6. Build-speed infra (scratchpad/specs/build_speed_infra_spec.md; O(n^2) serializer 3-liner
   = byte-identical proven; snapshot cache; monolith decomposition - registry now exists).
7. Quest design wave (Cold Tombs Neferkha questline + new-boss quests; QUESTS registry at
   the 256 window - slot analysis FIRST).
8. BL-AURA-RADIUS (BACKLOG: widen ALL aura radii - pets at range + MP allies on screen).
9. Standing backlog: SV-areas entrances campaign, orbs breadth audit, frostmandible wire,
   sprite-pit retest, orphan tags, moddb/Nexus, permissions (amgoz1/soa/Dragonlord).

## 5. LAWS (all standing; do not relearn)
ONE heavy build at a time (OOM proven) | detached builds + done-markers | A9 needs
Resources beside arz | PYTHONHASHSEED=0 + SVC_RELEASE_DROPS=1 | quest identity = md5 of
FULL registry path | QUESTS 256-window parity (build22) | TESTHUB never uploads | TRAVEL
LAW no walk-throughs | SHAPE LAW squares=cast/circles=passive | arz+Text couple, Levels+
Quests couple | never kill Will's live TQ session | commit checkpoints every step | update
the memory board continuously | Pet.tpl equipment-copy crash law | no clone_record for
souls | permanent pets TTL=[] | evocative names for hand-designed souls, SV originals
untouchable | Opus agents for work, vet independently, loop until GO | no em dashes.

## 6. WILL'S CURRENT CONTEXT
Playing DEV (char _Toxeus). Told to: clean reload to fix doors, save in town, save often in
deep blood cave (crash), restore 7/9 backup only if progress truly lost (TQ closed).
Awaiting from us: build36a on Steam, build37-dev + traveler hub on DEV, then his tour.
Quota: ~5% weekly remaining; Opus agents preferred for all work.
