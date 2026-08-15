export const meta = {
  name: 'warden-fix-almyros-trim',
  description: "R-249 (Will 2026-08-14): (A) remove Almyros's Helos->Secret Place + Helos->Uber Dungeon boat rows from the CANONICAL/Steam build (keep Garden); (B) fix the Warden of the Spartan Crypt descend (popup fires then auto-dismisses, then mute) WITHOUT switching to fixed-portals or doors - keep the boat-traveler method Will says is 'getting much closer'. Ship-ready canonical build.",
  phases: [
    { title: 'Forensic' },
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/warden-fix'
const BR = 'feat/warden-fix-almyros-trim'
const DEV = 'C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV'

const LAW = [
  'Repo: ' + REPO + '. main HEAD = 40ea6d9 (build91-ship LIVE on Steam: canonical arz b888f022 / Text e1d9592a /',
  'Levels 61aaf3e4 / Quests 176bf545). Work ONLY in worktree ' + WT + ' on ' + BR + ' from 40ea6d9. py launcher,',
  'PYTHONIOENCODING=utf-8; builds PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 into scratch (SVC_OUT_DIR / SVC_QUESTS_OUT).',
  'NO deploy/CustomMaps/TQ/Steam; do NOT touch main-checkout work//local/; other worktrees are other lanes.',
  'COMMIT EVERY STEP. Couplings: Levels+Quests together. NAVMESH b89 law. Retirement protocol on any row removal.',
  '',
  'WILL RULING R-249 (2026-08-14, append VERBATIM to WILL_RULINGS):',
  '"no steam should not have a traveler from helos to the secret place or the uber place. remove those from the steam',
  'build now. no we dont want to do the typhon-style fix, the current method we are using is getting much closer, we',
  'just need to fix the issue with the warden."',
  '=> (A) On CANONICAL only, remove portal_master_helos (Almyros) rows for Secret Place + Uber Dungeon; KEEP Garden of',
  '   Merchants. (B) Fix the Warden descend using the CURRENT boat-traveler method - do NOT switch to fixed-portals',
  '   (Typhon/Rhodes) or GridEntrance doors; Will explicitly rejected the fixed-portal fix and wants the current method fixed.',
  '',
  'WARDEN SYMPTOM (Will in-game, TESTHUB build 37c33fb0/1764c3a2): "i clicked on the warden... a pop up came up that said',
  'something like do you want to descend into the spartan crypt and before i could click on it the question went away and',
  'then when i clicked the warden again nothing happened." So on the R-248 build the descend BoatDialog now FIRES (progress',
  'from the old total mute) but AUTO-DISMISSES before the player can answer, then goes mute on re-click.',
  'KNOWN CONTEXT: on TESTHUB the dev traveler svc_helos_trav_sparta is placed at the SAME catacomb coord as the Warden',
  '(0.00u overlap, prior lanes flagged it). Will arrived at the catacomb VIA svc_helos_trav_sparta (Helos->catacomb), so',
  'BOTH NPCs occupy the spot and BOTH arm on the catacomb OnLevelLoad. svc_helos_trav_sparta is TESTHUB-ONLY (absent on',
  'canonical/Steam). The proven-working responder svc_area_return_uber (maze03) has the byte-identical awakening triple',
  '[ShowNpc, UpdateNPCDialog(Dialog Needed), BoatDialog] and works - so the triple is not the defect.',
].join('\n')

phase('Forensic')
const fx = await agent(
  'WARDEN FORENSIC (read-only; no commits). ' + LAW + '\n\n'
  + 'ANSWER from bytes you decode yourself (build canonical + testhub Quests/Levels from 40ea6d9 as needed; read the DEV\n'
  + 'testhub pair at ' + DEV + '/Resources for what Will actually played):\n'
  + '1. Decode the Warden descend trigger + EVERY other trigger/NPC that arms or fires on the CataCube02_FloorLast\n'
  + '   OnLevelLoad, on BOTH canonical and testhub. On TESTHUB, is svc_helos_trav_sparta co-located at the Warden coord and\n'
  + '   does its arming (return row + awakening) fire on the same level load? Could two overlapping clickable NPCs / two\n'
  + '   dialogs opening cause the "popup opens then auto-dismisses" (one dialog closing the other, or click-picking the\n'
  + '   wrong NPC each click)? \n'
  + '2. DIFFERENTIAL: is the auto-dismiss TESTHUB-ONLY (caused by the co-located svc_helos_trav_sparta) or does it also\n'
  + '   afflict CANONICAL (Warden alone in the level)? Decode canonical CataCube02_FloorLast: is the Warden the SOLE\n'
  + '   clickable NPC there, is his descend trigger on a dedicated one-shot step (isResettable=0), and is there ANY competing\n'
  + '   trigger that would re-fire OnLevelLoad and dismiss an open BoatDialog? Compare his trigger byte-for-byte to the\n'
  + '   proven svc_area_return_uber trigger - report ANY difference beyond coord/tag.\n'
  + '3. THE AWAKENING INTERACTION: the triple is ShowNpc + UpdateNPCDialog(Dialog Needed, delay 2.0) + BoatDialog. When the\n'
  + '   Warden is clicked, does his messageDialogTag conversation ("I am the Warden...") open AND the BoatDialog, and could\n'
  + '   the conversation auto-closing take the boat menu with it? Does the proven svc_area_return_uber have a messageDialogTag\n'
  + '   conversation too or not (i.e., is the Warden DIFFERENT in carrying a real chat that competes)? This is the leading\n'
  + '   canonical-relevant hypothesis - prove or kill it.\n'
  + 'VERDICT: is the Warden auto-dismiss (a) TESTHUB-only (co-located traveler) => canonical Warden already works, fix = move/\n'
  + 'remove the testhub co-location; or (b) a canonical defect too => name the exact mechanism + the minimal boat-method fix\n'
  + '(e.g. drop the messageDialogTag chat so only the boat menu opens; or reorder/adjust the awakening actions). Give the\n'
  + 'precise fix for the implementer. Return: env_decode, differential_verdict, awakening_finding, warden_fix (exact),\n'
  + 'almyros_rows (the exact Secret+Uber row tags to remove + reachability check that Secret[native shrine]+Uber[labyrinth\n'
  + 'entrance] stay reachable without them), unknowns.',
  { label: 'forensic', phase: 'Forensic', schema: {
    type: 'object',
    properties: { env_decode: { type: 'string' }, differential_verdict: { type: 'string' }, awakening_finding: { type: 'string' },
      warden_fix: { type: 'string' }, almyros_rows: { type: 'string' }, unknowns: { type: 'string' } },
    required: ['env_decode', 'differential_verdict', 'awakening_finding', 'warden_fix', 'almyros_rows', 'unknowns'],
  } })

if (!fx) { return { status: 'no-go', error: 'forensic died - relaunch' } }

let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  phase('Implement')
  impl = await agent(
    'WARDEN FIX + ALMYROS TRIM - IMPLEMENT (round ' + round + ').\n' + LAW + '\n\nFORENSIC FINDINGS (execute the fix):\n'
    + 'ENV: ' + fx.env_decode + '\nDIFFERENTIAL: ' + fx.differential_verdict + '\nAWAKENING: ' + fx.awakening_finding
    + '\nWARDEN FIX: ' + fx.warden_fix + '\nALMYROS ROWS: ' + fx.almyros_rows + '\nUNKNOWNS: ' + fx.unknowns + '\n'
    + (round > 1 && verdict ? '\nVET RETURNED ' + verdict.verdict + '. CLEAR EVERY ISSUE:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\n' : '')
    + '\nDELIVER, committing each step:\n'
    + '1. ALMYROS TRIM (canonical): remove his Secret Place + Uber Dungeon boat rows; KEEP Garden. Prove Secret Place\n'
    + '   (native SV shrine) + Uber Dungeon (labyrinth svc_area_return_uber entrance) remain reachable on canonical. Almyros\n'
    + '   TESTHUB behavior unaffected (he is canonical-only anyway). Update the budget-gate roster (canonical 26 -> 24).\n'
    + '2. WARDEN FIX per the forensic - using the BOAT-TRAVELER method (NO door, NO fixed-portal). If the fix is a testhub\n'
    + '   co-location move (svc_helos_trav_sparta off the Warden spot), do that AND note the canonical Warden was already\n'
    + '   correct. If the fix is a canonical quest-action change (e.g. drop the competing chat so only the descend menu\n'
    + '   opens), implement it on the Warden trigger and prove the descend BoatDialog is the sole dialog that opens on click.\n'
    + '3. BUILD both variants (canonical + testhub) Levels+Quests det-2x; diffs vs 40ea6d9 baselines = only intended;\n'
    + '   navmesh byte-identical; budget/awakening/travel gates green; contracts 0 P0/0 P1; armed counts before/after.\n'
    + '4. DOCS: R-249 verbatim in WILL_RULINGS; WILL_TEST_GUIDE Warden check updated; BACKLOG lane record.\n'
    + 'Return: status, commit_sha, artifact_md5s (canonical + testhub Levels/Quests), warden_disposition (what the fix was +\n'
    + 'canonical-vs-testhub), almyros_after (his remaining rows), done (PROVEN), not_done, proofs.',
    { label: 'impl:r' + round, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, artifact_md5s: { type: 'string' },
        warden_disposition: { type: 'string' }, almyros_after: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'artifact_md5s', 'warden_disposition', 'almyros_after', 'done', 'not_done', 'proofs'],
    } })

  if (!impl) { log('round ' + round + ': impl died, retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL VET (round ' + round + ') of ' + BR + ' @ ' + impl.commit_sha + '.\n' + LAW + '\n\n'
    + 'THEY CLAIM:\nARTIFACTS: ' + impl.artifact_md5s + '\nWARDEN: ' + impl.warden_disposition
    + '\nALMYROS AFTER: ' + impl.almyros_after + '\nDONE: ' + impl.done + '\nNOT DONE: ' + impl.not_done
    + '\nPROOFS: ' + impl.proofs + '\n\n'
    + 'Rebuild + decode yourself. Verify: (1) ALMYROS canonical now offers Garden ONLY (no Secret/Uber rows); Secret Place\n'
    + '(native shrine) + Uber Dungeon (labyrinth entrance) still reachable on canonical (walk the graph); TESTHUB launchers\n'
    + 'intact. (2) WARDEN: the fix matches the forensic; on click, the descend BoatDialog is the SOLE dialog that opens and\n'
    + 'nothing re-fires to dismiss it (decode the trigger set + any competing dialog yourself); it is still a BOAT traveler\n'
    + '(NOT a door/portal - Will ruling). If the fix was testhub-co-location, verify canonical Warden was already sole+clean\n'
    + 'AND testhub no longer overlaps. (3) NAVMESH b89 identity on touched blobs; diffs intended-only; couplings; contracts\n'
    + '0 P0/0 P1; budget gate roster updated + still RED on the pre-fix over-armed Quests. (4) HONESTY. Return verdict\n'
    + 'GO/NO-GO, issues (severity + command each), summary.',
    { label: 'vet:r' + round, phase: 'Vet', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } })

  if (!verdict) { verdict = { verdict: 'NO-GO', issues: ['vet died - re-run'], summary: 'vet did not return' } }
  log('round ' + round + ': ' + verdict.verdict)
  if (verdict.verdict === 'GO') break
}

return { status: (verdict && verdict.verdict) === 'GO' ? 'go' : 'no-go', branch: BR,
  commit: impl && impl.commit_sha, artifact_md5s: impl && impl.artifact_md5s,
  warden_disposition: impl && impl.warden_disposition, almyros_after: impl && impl.almyros_after,
  done: impl && impl.done, not_done: impl && impl.not_done,
  vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
