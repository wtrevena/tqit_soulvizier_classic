export const meta = {
  name: 'pr5-sparta-polish',
  description: "Sparta catacomb entrance NPC: name it 'Warden of the Spartan Crypt' (dedicated record, shared-record-law safe) and make its menu descend-only (remove the Helos-return port). Re-verify navmesh + landing.",
  phases: [
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/pr5-polish'
const BR = 'fix/pr5-sparta-polish'

const LAW = [
  'Repo: ' + REPO + '. main is the current tip; it ALREADY contains the merged PR-5 catacomb-traveler change',
  '(fix/pr5-catacomb-traveler): svc_area_return_sparta is placed at the deepest Athens catacomb',
  '(CataCube02_FloorLast local (25,1,38) = world (-6587,1,-3180)) with a "Descend into the Sparta Crypt" boat-dialog',
  'that lands ON-MESH inside spartacryptlevel2 at world (-5596,-2,-1410); Almyros\'s Helos Sparta route was removed',
  '(his Garden/Secret/Uber routes are intact); svc_testhub_return_sparta is the return-out NPC already inside the crypt.',
  'Python: py launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1.',
  'NOTE: a gated DB build can exit 1 for an ENVIRONMENTAL asset-gate reason even when all gates print RESULT: PASS',
  'and "Done." - judge success by "0 RESULT: FAIL + all registry verify hooks OK + the arz built", not the exit code.',
  '',
  'READ FIRST: ' + REPO + '/CLAUDE.md (4 process laws), ' + REPO + '/docs/WILL_RULINGS.md (R-170 is the catacomb',
  'ruling - append your amendment VERBATIM), ' + REPO + '/docs/BACKLOG.md (PR-5), the prior lane\'s',
  'tools/build_section_surgery.py + tools/build_quest_files.py changes.',
  '',
  'HARD CONSTRAINTS: work ONLY in ' + WT + ' on ' + BR + ' (git worktree add ' + WT + ' -b ' + BR + ' main).',
  'DO NOT DEPLOY / write CustomMaps / launch TQ or Steam. Levels+Quests COUPLED; arz+Text COUPLED. COMMIT EVERY STEP.',
  'NO ESTIMATES. NAVMESH is the top danger (b89): any .lvl you touch must be well-formed (parse_rec02 OK) or',
  'byte-identical; dry-run into COPIES + blob-diff. SHARED-RECORD LAW is the crux of this task (see below).',
].join('\n')

phase('Implement')
let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  impl = await agent(
    'PR-5 SPARTA POLISH - IMPLEMENT (round ' + round + ').\n' + LAW + '\n'
    + (round > 1 && verdict ? '\nTHE VET RETURNED ' + verdict.verdict + '. CLEAR EVERY ISSUE:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\nRe-measure, do not restate.\n' : '')
    + '\nWILL DECIDED TWO THINGS:\n'
    + '1. NAME the catacomb entrance NPC "Warden of the Spartan Crypt".\n'
    + '2. Its menu is DESCEND ONLY - remove the "Helos (Return)" travel option it inherited.\n\n'
    + 'THE SHARED-RECORD TRAP (the whole reason this is a lane, not a one-liner): the placed NPC record\n'
    + 'svc_area_return_sparta.dbr shows the GENERIC name "Return Traveler" (descriptionTag=tagSVCNpcAreaReturn)\n'
    + 'and that record is SHARED by other area-return travelers. You MUST NOT rename the shared record. Instead:\n'
    + '- CLONE svc_area_return_sparta into a DEDICATED record (e.g. records\\... \\svc_warden_sparta_crypt.dbr),\n'
    + '  give the CLONE a new descriptionTag whose text is "Warden of the Spartan Crypt" (mint the tag in the text\n'
    + '  build), and PLACE THE CLONE at the exact proven spot instead of svc_area_return_sparta. Confirm the shared\n'
    + '  record is byte-unchanged and every OTHER area-return placement still uses it.\n'
    + '- On the CLONE (or its quest wiring), remove the HELOS_HUB_TRAVEL / tagSVCAreaReturnToHelos boat-dialog port so\n'
    + '  the Warden offers ONLY "Descend into the Sparta Crypt". Keep the descend port landing ON-MESH unchanged.\n\n'
    + 'PROVE, from artifacts you build yourself:\n'
    + '- The catacomb NPC is now the Warden clone, placed x1 at the proven on-mesh spot; svc_area_return_sparta is\n'
    + '  NOT placed there and is byte-unchanged; its other placements are intact.\n'
    + '- The Warden menu resolves to exactly ONE option "Descend into the Sparta Crypt"; the Helos-return option is gone.\n'
    + '- "Warden of the Spartan Crypt" resolves in the rebuilt Text.arc on the Warden record.\n'
    + '- The touched .lvl navmesh is well-formed or byte-identical; only intended blobs change; the crypt return NPC\n'
    + '  is still present inside (no stranding); Almyros\'s Garden/Secret/Uber routes still intact.\n'
    + '- Record-diff + map/quest diff vs a baseline you build from main: only the intended records/blobs change, 0 REMOVED.\n\n'
    + 'Update docs/WILL_TEST_GUIDE.md so the walk-to step names the Warden. Return: status, commit_sha, done (PROVEN '
    + 'with commands+outputs+md5s), not_done (exhaustive), proofs.',
    { label: 'impl:r' + round, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs'],
    } })

  if (!impl) { log('round ' + round + ': impl died (transient), retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL VET (round ' + round + ') of ' + BR + '.\n' + LAW + '\n\n'
    + 'THEY CLAIM:\nSTATUS: ' + impl.status + ' | COMMIT: ' + impl.commit_sha + '\nDONE: ' + impl.done
    + '\nNOT DONE: ' + impl.not_done + '\nPROOFS: ' + impl.proofs + '\n\n'
    + 'Build the map + arz + text yourself. Verify: (1) the catacomb NPC is a DEDICATED Warden record named "Warden '
    + 'of the Spartan Crypt" (resolves in Text.arc), placed x1 on-mesh at the proven spot. (2) SHARED-RECORD LAW: '
    + 'svc_area_return_sparta is byte-UNCHANGED and its other placements are intact - enumerate them yourself. '
    + '(3) The Warden menu is DESCEND-ONLY (no Helos-return port); the descend still lands on-mesh in the crypt. '
    + '(4) NAVMESH: any touched .lvl well-formed or byte-identical (b89). (5) No stranding: the crypt return NPC is '
    + 'still present. (6) Almyros Garden/Secret/Uber routes intact. (7) COLLATERAL: only intended blobs/records change, '
    + '0 REMOVED. (8) HONESTY: is DONE proven? Return verdict GO/NO-GO, issues (HIGH/MEDIUM/LOW + the command each), summary.',
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

return { status: (verdict && verdict.verdict) === 'GO' ? 'go' : 'no-go', branch: BR,
  commit: impl && impl.commit_sha, done: impl && impl.done, not_done: impl && impl.not_done,
  vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
