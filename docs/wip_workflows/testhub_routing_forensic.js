export const meta = {
  name: 'testhub-routing-forensic',
  description: "READ-ONLY forensic: Will hit scrambled travel routing on DEV TESTHUB (Helos 'Sparta' traveler landed him behind the Minotaur; the uber return sent him to the Athens catacombs; the Sparta Warden is fully mute). Decode every route in shipped Quests 736cd50a, test the stale-TESTHUB-map hypothesis, explain all three symptoms mechanically, and rule the STEAM build in or out.",
  phases: [
    { title: 'Forensic' },
    { title: 'Verify' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const DEV = 'C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV'

const LAW = [
  'Repo: ' + REPO + ' (main checkout, HEAD 34b014e = build90-ship = LIVE on Steam). READ-ONLY LANE: no commits, no deploys,',
  'no CustomMaps writes, no TQ/Steam launches, do NOT touch work/ or local/ live artifacts - build anything you need into a',
  'scratch dir (SVC_OUT_DIR) under the session scratchpad. Python: py launcher, PYTHONIOENCODING=utf-8; deterministic env',
  'PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1. NOTE: a parallel implement lane (fix/uber-labyrinth-entrance, worktree',
  REPO + '/.claude/worktrees/uber-laby) is running - do not enter its worktree.',
  '',
  'KNOWN GROUND TRUTH (recon a38b8146, byte-proven): canonical Levels from main = 6784cf0f (last map change b63/build75,',
  'warden relocated (25,1,38)->(25,1,32)); shipped Quests = 736cd50a (build89: ALL 31 SVC boat triggers got the awakening',
  'prepend [ShowNpc, UpdateNPCDialog(Dialog Needed), BoatDialog]); shipped arz = a86afc15. DEV deployed pair right now:',
  'Levels = 7a7ca9ac (a PREBUILT TESTHUB artifact of uncertain vintage, NOT rebuilt through builds 84-90), Quests = 736cd50a,',
  'arz = a86afc15 (renamed SoulvizierClassicDEV.arz). DEV files at: ' + DEV,
  'KNOWN RESIDUAL (pr5 lane, honest disclosure at the time): on TESTHUB the dev traveler svc_helos_trav_sparta teleports to',
  'the catacomb door coord where the Warden stands (0.00u overlap - two NPCs on the same spot).',
].join('\n')

const SYMPTOMS = [
  "WILL'S LIVE REPORT (DEV TESTHUB, 2026-08-13, verbatim): \"I was in helos and i clicked on the guy to teleport me to the",
  'spartan crypt, but when I clicked on him he telported me to behind the minotaur, then when i clicked on the guy behind the',
  'minotaur door (who was extremely hard to click on) it said click her to return to helos, then when i clicked return to',
  'helos it teleported me to athens catacombs level 3 where the guy is that should teleport you to the spartan crypt, and now',
  'in the testhub when i click on the warden of the spartan crypt in athens catacombs level 3 literally no dialogue or',
  'nothing comes up and i cant travel anywhere."',
  'SYMPTOM 1: Helos "Sparta" traveler -> landed BEHIND THE MINOTAUR (the maze03/uber landing), not the Sparta staging point.',
  'SYMPTOM 2: the maze03 NPC (svc_area_return_uber; hard to click = door occlusion, ALREADY being fixed in a parallel lane)',
  '           offered "return to helos" but landed him at ATHENS CATACOMBS L3 (CataCube02_FloorLast, the Warden spot).',
  'SYMPTOM 3: the Warden of the Spartan Crypt there now gives NO DIALOG AT ALL - no menu, no travel.',
  'POSITIVE SIGNAL: the maze03 NPC DID respond when finally clicked => the b89 awakening works on at least one remote NPC.',
].join('\n')

phase('Forensic')
let fx = null, check = null
for (let round = 1; round <= 2; round++) {
  fx = await agent(
    'TESTHUB ROUTING FORENSIC (round ' + round + ').\n' + LAW + '\n\n' + SYMPTOMS + '\n'
    + (round > 1 && check ? '\nTHE VERIFIER REJECTED YOUR EXPLANATION. Fix every hole, re-measure:\n'
        + JSON.stringify(check.issues, null, 1) + '\n' + check.summary + '\n' : '')
    + '\nANSWER THESE, everything from bytes you decode yourself:\n\n'
    + 'A. ROUTE TABLE OF THE SHIPPED QUESTS: decode EVERY travel trigger in the DEV/Steam Quests.arc 736cd50a (read it from\n'
    + '   ' + DEV + '/Resources/Quests.arc after md5-confirming 736cd50a) - for each trigger: host quest, trigger index, keyed\n'
    + '   NPC record, action list (awakening present?), menu/offer tag + its resolved English text (from the arz/Text), and the\n'
    + '   BoatDialog destination coord + WHICH LEVEL contains that coord on (i) canonical 6784cf0f and (ii) TESTHUB 7a7ca9ac\n'
    + '   (read the DEV Levels.arc for the latter; build canonical into scratch from 34b014e or reuse a verified existing one\n'
    + '   ONLY if its md5 matches 6784cf0f). Flag every route whose destination level/coord does not match its label text.\n\n'
    + 'B. THE STALE-MAP HYPOTHESIS: rebuild the TESTHUB map from main 34b014e (SVC_TEST_HUB=1, deterministic env, scratch out).\n'
    + '   Is its md5 7a7ca9ac? If NOT: diff DEV\'s 7a7ca9ac against your fresh TESTHUB - which levels/placements differ, and\n'
    + '   WHICH RECORD PATHS does 7a7ca9ac place in (i) the Helos plaza, (ii) maze03, (iii) CataCube02_FloorLast, (iv) the\n'
    + '   sparta staging areas, vs your fresh build? Date the vintage of 7a7ca9ac if you can (match its differing blobs against\n'
    + '   git history states / gate records in docs/BACKLOG.md). The couplings law says Levels+Quests ship together - state\n'
    + '   plainly whether DEV is running a mismatched pair.\n\n'
    + 'C. EXPLAIN EACH SYMPTOM MECHANICALLY from A+B: (1) why did the Helos "Sparta" click land behind the Minotaur - wrong\n'
    + '   destination in the quest bytes, wrong NPC record placed at the "Sparta" plaza spot on the STALE map, overlapping/\n'
    + '   crowded plaza NPCs, or something else? (2) why did the uber return labeled "return to helos" land at the catacombs -\n'
    + '   note the pr5 residual says svc_helos_trav_sparta\'s dest IS the catacomb door; did Will actually fire a DIFFERENT\n'
    + '   trigger than the label suggested, or is the return route\'s dest wrong in the bytes? (3) why is the Warden fully mute\n'
    + '   THERE - the known 0.00u NPC overlap at that coord on TESTHUB (clicks hitting svc_helos_trav_sparta instead), a stale-\n'
    + '   map warden at the OLD (25,1,38) coord, quest-state saturation, or a real awakening failure? For each symptom name the\n'
    + '   mechanism, the evidence, and your confidence.\n\n'
    + 'D. STEAM BLAST RADIUS - THE MONEY QUESTION: the Steam build = canonical 6784cf0f + the SAME Quests 736cd50a + arz\n'
    + '   a86afc15. For the 6 NPCs actually PLACED on canonical (Almyros, the Warden, the 4 in-area returns): walk each of\n'
    + '   their routes end-to-end in the bytes (label text -> dest coord -> containing level -> is the landing on-mesh and\n'
    + '   sensible). Is ANY Steam-reachable route misrouted or mislabeled? VERDICT: Steam clean / Steam broken (which routes).\n\n'
    + 'E. REMEDY: precise, minimal. If DEV is a mismatched pair: the exact coupled redeploy (fresh TESTHUB Levels + which\n'
    + '   Quests/arz). If quest bytes carry real route bugs: name the generator lines. If the Warden overlap is the mute cause:\n'
    + '   the placement change needed (and whether the parallel uber-labyrinth lane\'s scope should absorb it). Order the fixes.\n\n'
    + 'Return: symptoms_explained (1/2/3 each w/ mechanism+evidence+confidence), steam_verdict (CLEAN or BROKEN + routes),\n'
    + 'dev_pair_verdict (matched/mismatched + vintage), route_table_summary (the flagged rows only), remedy (ordered), proofs\n'
    + '(commands+md5s), unknowns (exhaustive).',
    { label: 'forensic:r' + round, phase: 'Forensic', schema: {
      type: 'object',
      properties: { symptoms_explained: { type: 'string' }, steam_verdict: { type: 'string' },
        dev_pair_verdict: { type: 'string' }, route_table_summary: { type: 'string' },
        remedy: { type: 'string' }, proofs: { type: 'string' }, unknowns: { type: 'string' } },
      required: ['symptoms_explained', 'steam_verdict', 'dev_pair_verdict', 'route_table_summary', 'remedy', 'proofs', 'unknowns'],
    } })

  if (!fx) { log('round ' + round + ': forensic died (transient), retry'); continue }

  phase('Verify')
  check = await agent(
    'ADVERSARIAL VERIFY (round ' + round + ') of a routing-forensic explanation. Try to BREAK it.\n' + LAW + '\n\n' + SYMPTOMS + '\n\n'
    + 'THE FORENSIC CLAIMS:\nSYMPTOMS: ' + fx.symptoms_explained + '\nSTEAM: ' + fx.steam_verdict
    + '\nDEV PAIR: ' + fx.dev_pair_verdict + '\nFLAGGED ROUTES: ' + fx.route_table_summary
    + '\nREMEDY: ' + fx.remedy + '\nPROOFS: ' + fx.proofs + '\nUNKNOWNS: ' + fx.unknowns + '\n\n'
    + 'Re-derive the load-bearing claims yourself from bytes (do NOT trust the forensic\'s intermediate artifacts): (1) does\n'
    + 'each symptom explanation actually account for what Will saw, or is there an unexplained hole? (2) is the STEAM verdict\n'
    + 'sound - spot-check at least Almyros\'s 3 routes + the Warden route end-to-end on canonical yourself; a wrong CLEAN here\n'
    + 'ships a broken route to the public, a wrong BROKEN triggers a pointless emergency. (3) is the DEV pair verdict proven\n'
    + '(md5s, diff evidence)? (4) is the remedy minimal + correctly ordered + coupling-respecting? Default to REJECTED when a\n'
    + 'claim is unproven. Return verdict ACCEPTED/REJECTED, issues (each w/ the command that shows it), summary.',
    { label: 'verify:r' + round, phase: 'Verify', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['ACCEPTED', 'REJECTED'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } })

  if (!check) { check = { verdict: 'REJECTED', issues: ['verifier died (transient) - re-run'], summary: 'verifier did not return' } }
  log('round ' + round + ': ' + check.verdict)
  if (check.verdict === 'ACCEPTED') break
}

return { status: (check && check.verdict) === 'ACCEPTED' ? 'accepted' : 'unverified',
  symptoms_explained: fx && fx.symptoms_explained, steam_verdict: fx && fx.steam_verdict,
  dev_pair_verdict: fx && fx.dev_pair_verdict, route_table_summary: fx && fx.route_table_summary,
  remedy: fx && fx.remedy, unknowns: fx && fx.unknowns,
  verify: check && check.summary, open_issues: (check && check.issues) || [] }
