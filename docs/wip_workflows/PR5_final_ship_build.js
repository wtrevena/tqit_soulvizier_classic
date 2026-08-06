export const meta = {
  name: 'pr5-final-ship-build',
  description: 'Final coupled ship build (arz+Text+Levels+Quests+dye Creatures.arc) from merged main @0449b1b, verified against the lane-vet anchor hashes, then an independent artifact vet. Runs in the MAIN checkout (caches present). NO deploy, NO Steam - orchestrator does those.',
  phases: [
    { title: 'Build' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const SCRATCH = 'C:/Users/willi/AppData/Local/Temp/claude/C--Users-willi-repos/98075e9c-011f-4120-9b92-ce6ca35146b2/scratchpad/ship_finalbuild'

// Anchors proven by the pr5-sparta-polish lane vet (independent rebuild, byte-for-byte):
const ARZ_TARGET = 'd447f095'           // Warden arz (post-polish). record-diff vs baseline = +1 record only.
const MAP_TARGET = '78a3e263'           // canonical Warden map (navmesh byte-identical to R-170 map).
const BASE_ARZ = SCRATCH + '/baseline_prewarden_ab02f16e.arz'   // main@48f47f4 arz (ab02f16e), pre-Warden
const LIVE_QUESTS = SCRATCH + '/baseline_quests_aug5.arc'       // live deployed Quests.arc (bd0fb5f9)
const LIVE_TEXT = SCRATCH + '/baseline_text.arc'                // prior staged Text_EN.arc

const LAW = [
  'Repo: ' + REPO + '. YOU RUN IN THE MAIN CHECKOUT (cwd = repo root). Do NOT create or cd into a git worktree -',
  'worktrees get EMPTY caches and the Quests base will be missing. Main HEAD MUST be 0449b1b (the merged Sparta polish).',
  'All build inputs are already resolvable on main (I verified check_build_inputs.py --all = RESULT: PASS, 10 inputs;',
  'reference_mods/SVAERA_customquest/Resources/Quests.arc + upstream/soulvizier_098i/Resources/XPack/Quests.arc are populated).',
  'Python: py launcher; PYTHONIOENCODING=utf-8. DETERMINISTIC BUILD ENV for every build command:',
  '  PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 PYTHONIOENCODING=utf-8   (SVC_REQUIRE_GATES is optional and does NOT change',
  '  artifact CONTENT - the lane vet proved the arz is byte-identical with it unset; a gated build may exit 1 for an',
  '  environmental asset-gate reason while 0 RESULT:FAIL and the arz is correct. Judge by hashes+diffs+RESULT lines, NOT exit code.)',
  'DO NOT DEPLOY, do NOT write CustomMaps, do NOT launch TQ or Steam, do NOT git commit (work/ is gitignored scratch).',
  'READ FIRST: ' + REPO + '/CLAUDE.md (Build & deploy commands + deploy couplings) and scripts/bootstrap_working_mod.ps1',
  '(canonical per-tool invocations). Deploy couplings: arz+Text together, Levels+Quests together.',
  '',
  'ANCHOR HASHES proven by the pr5-sparta-polish lane vet (independent rebuild):',
  '  arz (work/SoulvizierClassic/Database/SoulvizierClassic.arz) MUST start with ' + ARZ_TARGET,
  '  canonical map (work/SoulvizierClassic/Resources/Levels.arc) MUST start with ' + MAP_TARGET,
  'If EITHER mismatches, STOP and report NO-GO (non-determinism or wrong input) - do not hand-wave.',
].join('\n')

phase('Build')
let build = null, verdict = null
for (let round = 1; round <= 2; round++) {
  build = await agent(
    'FINAL SHIP BUILD (round ' + round + ') - build all 5 coupled artifacts into work/SoulvizierClassic/ from MERGED main.\n' + LAW + '\n'
    + (round > 1 && verdict ? '\nTHE VET RETURNED ' + verdict.verdict + '. FIX EVERY ISSUE, re-measure:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\n' : '')
    + '\nDO, in order, and PROVE each with the command + its output:\n\n'
    + '0. Confirm `git rev-parse --short HEAD` == 0449b1b. Snapshot nothing (baselines already exist at ' + SCRATCH + ').\n\n'
    + '1. DB (arz): build with the deterministic env into work/SoulvizierClassic/Database/SoulvizierClassic.arz using the\n'
    + '   canonical build_svc_database.py invocation from CLAUDE.md (SV 098i/0.9/0.41 arz + out + base-game arz).\n'
    + '   HARD: md5 MUST start ' + ARZ_TARGET + '. Then record-diff vs the pre-Warden baseline:\n'
    + '     py tools/diff_arz_records.py ' + BASE_ARZ + ' work/SoulvizierClassic/Database/SoulvizierClassic.arz   (or the repo\'s diff tool)\n'
    + '   EXPECT exactly ADDED 1 (records\\quests\\svc_warden_sparta_crypt.dbr), REMOVED 0, MODIFIED 0. Any other delta = NO-GO.\n\n'
    + '2. Text.arc: build with de-clobber into work/SoulvizierClassic/Text/Text_EN.arc (canonical build_text_arc.py invocation).\n'
    + '   HARD: `py tools/validate_tags.py` (or the build gate) PASS. Prove tagSVCNpcWardenSpartaCrypt resolves to exactly\n'
    + '   "Warden of the Spartan Crypt" and the greeting tag resolves. Delta of the resolved tag set vs the prior Text\n'
    + '   (' + LIVE_TEXT + ') = +2 lines (the 2 Warden tags), nothing removed.\n\n'
    + '3. CANONICAL map: run svaera_plus_portals.py WITHOUT SVC_TEST_HUB (canonical, not testhub) with PYTHONHASHSEED=0.\n'
    + '   It writes local/Levels_merged.arc. HARD: md5 MUST start ' + MAP_TARGET + '. Copy it to\n'
    + '   work/SoulvizierClassic/Resources/Levels.arc and confirm they are byte-identical. Then map-diff vs a canonical map\n'
    + '   you build from a clean baseline (or vs the live Levels if available): prove the 0x0b navmesh of EVERY changed blob\n'
    + '   is byte-identical (b89 safety) and only intended blobs (the Athens catacomb CataCube02_FloorLast + any R-170\n'
    + '   catacomb blob) differ. Use tools/diff_merged_maps.py.\n\n'
    + '4. Quests.arc: run the DEFAULT `py tools/build_quest_files.py` (reference_mods base is present, so it restores clean +\n'
    + '   applies all wiring incl. the Warden enter-offer). It writes work/SoulvizierClassic/Resources/Quests.arc.\n'
    + '   THEN THE LEINTH-EXIT SAFETY NET: per-ENTRY diff the fresh Quests.arc against the LIVE deployed Quests.arc\n'
    + '   (' + LIVE_QUESTS + ' = bd0fb5f9). Decompress both arcs, compare every entry by name+bytes. The ONLY entry\n'
    + '   allowed to DIFFER is sv_commonmechanics.qst (the Warden/R-170 wiring). If open_bloodcave_portal.qst (Leinth\'s\n'
    + '   exit portal lives there) OR ANY other entry differs, is missing, or is added unexpectedly -> STOP, that is a\n'
    + '   regression; investigate (likely a missing --promote-leinth-exit post-step) and fix so the ONLY delta is\n'
    + '   sv_commonmechanics.qst. Also PROVE inside sv_commonmechanics: the Warden enter-offer tag tagSVCEnterSpartaCrypt\n'
    + '   is present and the sparta Helos-return (tagSVCAreaReturnToHelos on svc_area_return_sparta) is ABSENT. Confirm\n'
    + '   _assert_quest_records_loadable passed (the build prints it).\n\n'
    + '5. Dye Creatures.arc: run tools/build_creatures_dye_skins_arc.py into work/SoulvizierClassic/Resources/Creatures.arc.\n'
    + '   HARD: `py tools/gate_dye_skins.py` PASS. Prove it is ADDITIVE (a costume-dye skin layer) and every skin path it\n'
    + '   references resolves in our shipped arcs.\n\n'
    + '6. CONTRACT BATTERY: run the repo contract suite (souls/summons/resources + map contracts + gate_travel_npc_invariants\n'
    + '   + gate_dye_skins + validate_tags). Require 0 P0 / 0 P1 / 0 RESULT:FAIL. Paste the summary lines.\n\n'
    + 'Return: status, head_sha, arz_md5, map_md5, text_ok(+the 2 tags), quests_delta (the exact per-entry diff result vs live),\n'
    + 'creatures_md5, gates (each + pass/fail), all_artifact_md5s (5 files), not_done (exhaustive), proofs (commands+outputs).',
    { label: 'build:r' + round, phase: 'Build', schema: {
      type: 'object',
      properties: {
        status: { type: 'string' }, head_sha: { type: 'string' }, arz_md5: { type: 'string' }, map_md5: { type: 'string' },
        text_ok: { type: 'string' }, quests_delta: { type: 'string' }, creatures_md5: { type: 'string' },
        gates: { type: 'string' }, all_artifact_md5s: { type: 'string' }, not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'head_sha', 'arz_md5', 'map_md5', 'text_ok', 'quests_delta', 'creatures_md5', 'gates', 'all_artifact_md5s', 'not_done', 'proofs'],
    } })

  if (!build) { log('round ' + round + ': build agent died (transient), retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL ARTIFACT VET (round ' + round + ') of the final ship build in work/SoulvizierClassic/.\n' + LAW + '\n\n'
    + 'THE BUILD CLAIMS:\nSTATUS ' + build.status + ' | HEAD ' + build.head_sha + ' | arz ' + build.arz_md5 + ' | map ' + build.map_md5
    + '\nTEXT: ' + build.text_ok + '\nQUESTS DELTA: ' + build.quests_delta + '\nCREATURES: ' + build.creatures_md5
    + '\nGATES: ' + build.gates + '\nMD5s: ' + build.all_artifact_md5s + '\nNOT DONE: ' + build.not_done + '\n\n'
    + 'You run in the MAIN checkout (read the artifacts in work/; rebuild into a SCRATCH dir to cross-check, never clobber work/).\n'
    + 'VERIFY INDEPENDENTLY:\n'
    + '(1) arz in work/ md5 starts ' + ARZ_TARGET + '; record-diff vs ' + BASE_ARZ + ' = ADDED 1 (svc_warden_sparta_crypt), 0 REMOVED, 0 MODIFIED.\n'
    + '(2) map in work/ md5 starts ' + MAP_TARGET + '; every changed level blob 0x0b navmesh BYTE-IDENTICAL (b89); only intended blobs differ.\n'
    + '(3) Text: tagSVCNpcWardenSpartaCrypt resolves to "Warden of the Spartan Crypt" in work/ Text.arc; validate_tags PASS; +2 tags only.\n'
    + '(4) Quests LEINTH-EXIT SAFETY: per-entry diff work/ Quests.arc vs LIVE ' + LIVE_QUESTS + ' - the ONLY differing entry is\n'
    + '    sv_commonmechanics.qst; open_bloodcave_portal.qst (Leinth exit portal) is byte-IDENTICAL to live; no entry added/removed.\n'
    + '    In sv_commonmechanics: Warden enter-offer present, sparta Helos-return absent.\n'
    + '(5) dye Creatures.arc additive; gate_dye_skins PASS; referenced skins resolve.\n'
    + '(6) Contract battery 0 P0 / 0 P1 / 0 RESULT:FAIL, run by you.\n'
    + '(7) COUPLING sanity: arz+Text coherent (Warden tags in both), Levels+Quests coherent (map places Warden; Quests wires its descend).\n'
    + '(8) HONESTY: are all claimed hashes real (recompute them yourself)?\n'
    + 'Return verdict GO/NO-GO, issues (each HIGH/MEDIUM/LOW + the command that shows it), summary.',
    { label: 'vet:r' + round, phase: 'Vet', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } })

  if (!verdict) { verdict = { verdict: 'NO-GO', issues: ['vet died (transient) - re-run'], summary: 'vet did not return' } }
  log('round ' + round + ': ' + verdict.verdict)
  if (verdict.verdict === 'GO') break
}

return { status: (verdict && verdict.verdict) === 'GO' ? 'go' : 'no-go',
  arz_md5: build && build.arz_md5, map_md5: build && build.map_md5, creatures_md5: build && build.creatures_md5,
  quests_delta: build && build.quests_delta, gates: build && build.gates, all_artifact_md5s: build && build.all_artifact_md5s,
  not_done: build && build.not_done, vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
