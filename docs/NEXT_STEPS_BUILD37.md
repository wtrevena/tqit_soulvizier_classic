# NEXT STEPS - BUILD37 AND BEYOND (written 2026-07-12, quota-preservation checkpoint)

> Context: build36 convergence+deploy was executing when this was written (workflow wf_b8532b64:
> sequential builds -> final vet -> DEV + Steam deploy + tag build36). ~95% of the weekly Claude
> usage quota was consumed producing build36; this file captures EVERYTHING unfinished so any
> successor session can resume cold. Read with docs/HANDOFF_LIVE_STATE.md + docs/BACKLOG.md.
> The memory board (tq-soulvizier-2026-07-resume.md) has the live workflow IDs.

## 0. IF BUILD36 DID NOT FINISH DEPLOYING
- Convergence code is COMMITTED on main @ 00da531 (Vort red skin eb5591f + bloodbeast petLimit
  8->4 mitigation + q_enslaver_warband placement in build_section_surgery.py INJECT_SPECS,
  surveyed 100% at xbloodcave/drxfirstxistion_connection LOCAL(21.1,10.0,-6.5)).
- Remaining: sequential builds (DB -> Text -> Quests -> canonical map -> TESTHUB map; NEVER two
  heavy builds at once - the machine OOMs, proven law), gate battery (contracts_map must show the
  4 ex-MAP-REF-1 P1s cleared + warband resolves), final vet, then deploy per docs/PLAYBOOK.md:
  DEV coupled sets hash-verified -> package_workshop (single-wrapper, CANONICAL only) ->
  upload_workshop -SteamUser trevenaw7 -Update -Visibility 0 -> restart Steam -> tag build36.
- Build-env traps: populate <output>/../Resources with hardlinks from work/SoulvizierClassic/
  Resources/*.arc before DB builds (A9 render gate false-fails otherwise); export SVC_TEST_HUB=1
  on its own line for the TESTHUB map; PYTHONHASHSEED=0 + SVC_RELEASE_DROPS=1.

## 1. READY-TO-SHIP SMALL BUILDS (vetted GO, waiting on integration - IN ORDER)
Ship-small law (Will): one small build at a time, each fully gated.
1. **patches-registry merge** (feat/patches-registry @ 6f29c6b, GO): merge into post-deploy main,
   RE-RUN the empty-registry md5-identity proof against the merged HEAD, drop the H/O wave's
   interim 2-line wiring in apply_svc_patches.py. This unlocks everything below.
2. **Hunting/Occult build** = feat/b37-hunting-occult (GO, 1815faf) + feat/b37-ho-ui (GO, 2824a7b).
   MUST-DO pre-merge fixes:
   - **WILL'S SHAPE LAW (2026-07-12, verbatim ruling)**: "Tempest should be a square since it is
     an ability that you have to cast, circles are for passive buffs in the skill tree or passive
     abilities like % chance to activate or an extension / enhancement to a lower level skill."
     -> Re-audit ALL 8 shape changes on feat/b37-ho-ui against THIS law (not base-game precedent):
     CAST actives = SQUARE: drxspear_tempest (revert the wave's circle - Will's explicit call),
     drxpoisongasbomb (already square, correct).
     PASSIVES/PROCS/MODIFIERS = CIRCLE: drxcalculatedstrike_luckyhit, drxlaytrap_petmodifier_
     multishotbolttrap, drxtakedown_eviscerate (already circles, correct); RE-EXAMINE drxherbalism
     (Skill_Passive), drx_dual_blade (Skill_Passive), drxcorneredrage (PassiveOnLifeBuffSelf) -
     the wave squared them per base-game precedent, but under Will's law standalone passives are
     CIRCLES; confirm with Will or default to his law (circle). Adjust waiver keys accordingly.
   - Add text-mode golden waivers for the improvements wave's 3 tag drifts
     (tagDRXlethalstrikeDESC, tagSkillDescription171, tagSkillDescription172) before the
     Text-build gate when both branches deploy together.
   - Fast-follow inside this build: isolate the shared drx_petskill_boom (Darklings uplift edited
     a record also referenced by the inert graeae_eye cosmetic - clone + repoint the 20
     shadowdemons so the uplift is provably Darklings-only; leak currently proven inert).
3. **b37 content fleet, one build each** (all GO on own branches feat/b37-<key>, each = one
   REGISTRY line + merge + full gate): diadochi ("The Helepolis, Taker of Cities"), polis_vault,
   neferkha, toxeus_suite, skill_quality, visuals.
4. **four_generals**: STOPPED mid-run to clear the machine for the deploy (its branch
   feat/b37-four-generals may have partial commits - salvage per the solo-rerun brief in workflow
   script b37-four-generals-solo-wf_d90c88fe-b20.js; the item died once on StructuredOutput size,
   keep returns concise).
5. **b37 MAP PASS** (single wave, applies ALL accumulated map deltas): Helepolis placement
   (Elysian_Fields_03 idx 776, surveyed spot in its module report), Menoetes central hall +
   general guards, Polis vault chest-arc + spawns, Neferkha tomb injection, Toxeus-suite ambush
   proxy (drxFirstRoom), visuals-wave swirl-FX co-locations + Tier-1 set-piece restorations,
   optional cosmetic deltas (Tantalus poison-swirl ring, Ephialtes fog), **Garden-portal-guy
   removal (below)**, Vashkarr 3.0-scale density re-verify, 3x-guardian clipping checks.
6. **build-speed infra** (spec checker-corrected: build_speed_infra_spec.md in the session
   scratchpad - COPY IT INTO docs/ IF LOST): 3-line O(n^2) serializer fix (byte-identical, 88s->
   0.04s) + helper index -> ~4.4 min cold builds; snapshot cache -> ~3 min incremental; module
   decomposition of the monolith (beware the SHADOWED _find_record: :294 exact vs :3289 substring
   - the substring def wins at runtime).

## 2. WILL'S NEW ITEMS (2026-07-12, NOT started - quota)
- **Remove the Garden of Merchants portal NPC from the first cave** (the cave leading into the
  blood cave / Random09A area). NOTE THE IMPLICATION: that portal is currently an access path to
  the Garden of Merchants; removal without a replacement makes the Garden TESTHUB-only. Options:
  plain removal (Will's literal ask) vs relocate the portal elsewhere. Map-side change (0x05
  entity removal) - fold into the b37 map pass.
- **Tempest -> square** (folded into item 1.2 above, Will's shape law).

## 3. OPEN INVESTIGATIONS / VERIFICATIONS
- **P0 blood-cave crash**: recurring ntdll heap-corruption family (dumps 07-05/07-09/07-12; NOT
  the dyingFxPak theory - refuted). Mitigation shipped in build36 (bloodbeast petLimit 8->4).
  Will retests: kill the hound-summoners in the room after the first door repeatedly. IF IT
  RECURS: deep minidump stack/heap walk (python minidump lib / WinDbg on
  C:/Users/willi/AppData/Local/CrashDumps/TQ.exe.*.dmp) + a Frida live-probe session (repo has
  precedent tooling). WER evidence file: session scratchpad crash_probes/WER_FINDINGS.md.
- **In-game confirms on Will's build36 pass** (see docs/WILL_TEST_GUIDE.md for the full menu):
  Epic unlocks via the Victory Portal after Hades (the one engine-runtime unknown of the Act-5
  fix); golem button renders + is levelable; Trophonios archer-muster fires (build37 item);
  Charon summit-vs-forecourt placement compare (optional).
- **frostmandible_soul -> um_frost_32 wire**: checker-suggested REPLACE of the thin frost_soul,
  verify-at-implement (also untangle the triple-defined tagSoulSVC9004).
- **Sprite pit (B-SPRITE-1)**: records proven SV-faithful; Will's "spawns once" report predates
  the current restoration - RETEST before building the ProxyPool respawn driver.

## 4. STANDING BACKLOG (pre-existing, unchanged)
- SV-areas campaign (task: entrances for the not-yet-reachable areas - unlocks the crow-hero /
  Blood-Witch / D2-NPC soul obtainability). Cold Tombs Tier-2 full area (optional, high-risk
  entrance). Quest wave (Will: post-deploy - Cold Tombs + new-boss quests; QUESTS registry is at
  the 256-entry cap: slot analysis FIRST). Toxeus 6-player readiness. Super-Caravan respec items.
  moddb/Nexus dual distribution. Written permissions from amgoz1/soa/Dragonlord (soa verbal OK).
  Orphan dead soul tags cleanup (7). Duplicate cyclops soul records cleanup. Hunting/Occult
  suggestion-doc proposals NOT explicitly approved by Will remain suggestions-only
  (docs/HUNTING_/OCCULT_IMPROVEMENT_SUGGESTIONS.md).
- Element-filler quality follow-ups beyond the shipped GS fix are IN the skill_quality fleet item.

## 5. PROCESS LAWS LEARNED THIS CAMPAIGN (do not relearn)
- ONE heavy build at a time (two 1.3GB builds = OOM/kill, proven twice).
- Detached builds (Start-Process) + log-polling watchers; agent turns are shorter than builds.
- Resources-hardlink beside every DB build output or A9 false-fails (~200 phantom failures).
- Registry modules: gates run LAST over everything; collisions WARN loud; identity proof on any
  build-pipeline restructure.
- Quest resolution = md5 of the FULL registry path (root-basename copies are INERT - the widow-
  letter and IT-cap bugs were the same class).
- Will's shape law (item 1.2). Evocative names for hand-designed souls; "<Monster> Soul" for
  generated; SV originals untouchable. MP: TESTED AND WORKS (Will 2026-07-12) - stale claims
  purged/being purged from docs.
