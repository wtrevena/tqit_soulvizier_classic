export const meta = {
  name: 'proven-mechanism-travel',
  description: "R-248 (Will 2026-08-14, in-game refutation of the R-246 devices): the new portals 'dont work and they lag the game out and break everything'. REVERT all device placements; KEEP the row-rip + budget gates (the real bug fix); rebuild travel using ONLY the two mechanisms proven working in OUR mod in-game: the Garden-of-Merchants boat-traveler design (Almyros pattern) and the post-Typhon fixed-portal-to-Rhodes design. Base-game-faithful one-shot arming, no churn.",
  phases: [
    { title: 'Design' },
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/proven-travel'
const BR = 'feat/proven-mechanism-travel'

const LAW = [
  'Repo: ' + REPO + '. main = 057a605 (R-246 device wave MERGED - you are UNDOING its device half). Work ONLY in worktree',
  WT + ' on ' + BR + ' from 057a605. py launcher, PYTHONIOENCODING=utf-8; builds PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 into',
  'scratch SVC_OUT_DIR. NO deploy/CustomMaps/TQ/Steam; do NOT touch main-checkout work//local/; other lanes own',
  '.claude/worktrees/akremon + device-travel + uber-laby - do not enter them. COMMIT EVERY STEP. Couplings honored.',
  'NAVMESH b89 law. TESTHUB local-only. Shared-record law. Retirement protocol (esp. when reverting R-246 pieces - ledger',
  'every retirement).',
  '',
  'WILL RULING R-248 (2026-08-14, verbatim - append to WILL_RULINGS; supersedes R-246\'s DEVICE half; the RIP survives):',
  '"why cant we just get the npc traveler to work as intended or the portals like the one that you use to travel after you',
  'kill typhon to get to rhodes. also the traveler to take you to the garden of merchants works why cant we just use that',
  'design. also the new portals you made dont work and they lag the game out and break everything. those new portals you',
  'made never worked in the first place thats why we switched to the npc traveler design."',
  '',
  'WHAT THIS MEANS (design law):',
  '- The R-246 doors + rift shrines are IN-GAME REFUTED (lag + breakage + non-function) AND this device class failed once',
  '  before (pre-2026-07-12, why travelers exist). TWICE-BITTEN => permanent failure-graveyard entry in MODDING_PLAYBOOK',
  '  with the best-supported mechanism (leading hypothesis to INVESTIGATE, not assume: born-open GridEntrance bindings',
  '  pre-stream their target levels; 14 court doors + 2 canonical = massive streaming/memory pressure in a 32-bit process',
  '  = the lag/crash class; check the playbook/crash docs + the 0x14 GUID-binding model for corroboration).',
  '- ONLY two travel mechanisms are allowed, both proven IN OUR MOD IN-GAME:',
  '  (A) THE BOAT-TRAVELER DESIGN (Almyros/Garden pattern - Will: "the traveler to take you to the garden of merchants',
  '      works"). Corruption context: the forensic proved the 39-rows-armed-on-ONE-blanket-refire-step table statefully',
  '      corrupts; base game arms max 2/step, ONE-SHOT (isResettable=0), never re-fires, and its boatmen work forever',
  '      including remote ones. The R-246 RIP (51->16 armed rows) SURVIVES as the bug fix.',
  '  (B) THE FIXED-PORTAL DESIGN (post-Typhon -> Rhodes pattern - a placed portal entity + quest Action_UnlockFixedItem,',
  '      proven working in OUR mod via the Q1/Q3 wiring). Zero armed rows. Decode that exact working chain as the template.',
  '',
  'KEEP from R-246 (do NOT revert): the rip + gate_boatdialog_budget, the Y-vs-terrain fixes/gate, placement hygiene,',
  'the stale-gate rewrites where still coherent. REVERT: all 45 device instances + their GROUPS additions + aura/marker',
  'entities on BOTH map variants; gate_device_resolution retires or narrows to whatever survives (ledgered).',
].join('\n')

phase('Design')
const design = await agent(
  'PROVEN-MECHANISM TRAVEL - DESIGN. READ-ONLY (no commits).\n' + LAW + '\n\n'
  + 'Settle these from bytes before anyone implements:\n'
  + '1. THE ARMING MODEL: decode how base-game quest 7/8 arm their boatmen (one-shot isResettable=0, arms-once-persists,\n'
  + '   max 2/step, remote boatman works) vs our corrupt blanket-refire step. Design the traveler wiring to be BASE-GAME-\n'
  + '   FAITHFUL: one-shot arming, spread across steps (<=2-3 rows/step, Almyros grandfathered at 3), NO row on any\n'
  + '   re-firing step. Project the global armed count for canonical and TESTHUB rosters; state the residual risk honestly\n'
  + '   (the corruption was churn+scale; one-shot removes churn; if the count still worries you, say where the line is and\n'
  + '   what the Frida probe would settle).\n'
  + '2. THE FIXED-PORTAL TEMPLATE: decode the WORKING post-Typhon->Rhodes chain end-to-end (portal entity record, placement,\n'
  + '   0x14/0x05 shape, the quest unlock action, born-open vs unlocked variants) - THE template for one-way links. Confirm\n'
  + '   whether a fixed portal pre-streams its destination (the lag question) or teleports like a boat dest - if it also\n'
  + '   pre-streams, portals get the same scrutiny as doors and the roster leans traveler-heavy; PROVE which from the\n'
  + '   engine model/playbook, do not guess.\n'
  + '3. THE ROUTE MAP: every connection (canonical: laby->uber entrance [R4 wording], catacomb->sparta descend [the warden\n'
  + '   NPC gets his row back - under the fixed small-table world his dialog plausibly binds; flag as the key in-game test],\n'
  + '   area returns per R5 [return-to-entrance dests], Almyros untouched; TESTHUB: the 14 travelers restored at the R-245\n'
  + '   spaced positions + returns) -> assign mechanism (A) or (B) per connection with justification; prefer (B) where a\n'
  + '   one-way link suffices AND (2) proves portals safe.\n'
  + '4. THE REVERT PLAN: exact device instances/GROUPS/markers to remove per map, what survives, gate dispositions.\n'
  + '5. THE LAG INVESTIGATION: best-supported mechanism for the device lag/breakage from available evidence (playbook,\n'
  + '   crash docs, streaming model, 32-bit ceiling, count of GridEntrance bindings added) - for the failure graveyard.\n'
  + 'Return: arming_model, portal_template (+ the pre-stream verdict), route_map, revert_plan, lag_finding, risks.',
  { label: 'design', phase: 'Design', schema: {
    type: 'object',
    properties: { arming_model: { type: 'string' }, portal_template: { type: 'string' }, route_map: { type: 'string' },
      revert_plan: { type: 'string' }, lag_finding: { type: 'string' }, risks: { type: 'string' } },
    required: ['arming_model', 'portal_template', 'route_map', 'revert_plan', 'lag_finding', 'risks'],
  } })

if (!design) { return { status: 'no-go', error: 'design agent died - relaunch' } }

let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  phase('Implement')
  impl = await agent(
    'PROVEN-MECHANISM TRAVEL - IMPLEMENT (round ' + round + ').\n' + LAW + '\n\nTHE DESIGN (execute; deviate only with stated reason):\n'
    + 'ARMING: ' + design.arming_model + '\nPORTAL TEMPLATE: ' + design.portal_template + '\nROUTES: ' + design.route_map
    + '\nREVERT: ' + design.revert_plan + '\nLAG FINDING: ' + design.lag_finding + '\nRISKS: ' + design.risks + '\n'
    + (round > 1 && verdict ? '\nVET RETURNED ' + verdict.verdict + '. CLEAR EVERY ISSUE, re-measure:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\n' : '')
    + '\nDELIVER, committing every step:\n'
    + '1. THE REVERT: all R-246 device instances/GROUPS/markers off BOTH maps per the plan; b89 proof per touched blob;\n'
    + '   ledgered retirements.\n'
    + '2. THE TRAVELERS: restore/build the roster per the route map with BASE-GAME-FAITHFUL one-shot arming spread across\n'
    + '   steps; the warden gets his descend row back; laby entrance NPC gets his single R4 row; returns per R5; TESTHUB 14\n'
    + '   at the spaced positions. QUESTS-window law (256) respected.\n'
    + '3. THE PORTALS (if the design cleared them): per the decoded template, exact working-chain shape.\n'
    + '4. GATES: budget gate extended with the NO-CHURN law (no travel row on a re-firing step; one-shot flags asserted) +\n'
    + '   per-step/global counts updated; device gates retired/narrowed; negatives planted (a churn-step row must RED).\n'
    + '5. BUILDS+PROOFS: canonical + TESTHUB Levels + Quests det-2x, full diffs vs 057a605 (only intended), gates +\n'
    + '   contracts 0 P0/0 P1, armed counts before/after.\n'
    + '6. DOCS: R-248 VERBATIM + R-246 supersession in WILL_RULINGS; failure-graveyard entry in MODDING_PLAYBOOK (device\n'
    + '   class, twice-bitten, the lag finding); WILL_TEST_GUIDE rewritten (traveler walk list; the WARDEN CLICK is the\n'
    + '   headline test - the small-table world is the mute fix); BACKLOG lane record + debts.\n'
    + 'Return: status, commit_sha, armed_counts, artifact_md5s, roster (mechanism per connection), done, not_done, proofs.',
    { label: 'impl:r' + round, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, armed_counts: { type: 'string' },
        artifact_md5s: { type: 'string' }, roster: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'armed_counts', 'artifact_md5s', 'roster', 'done', 'not_done', 'proofs'],
    } })

  if (!impl) { log('round ' + round + ': impl died (transient), retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL VET (round ' + round + ') of ' + BR + ' @ ' + impl.commit_sha + '.\n' + LAW + '\n\n'
    + 'THEY CLAIM:\nARMED: ' + impl.armed_counts + '\nARTIFACTS: ' + impl.artifact_md5s + '\nROSTER: ' + impl.roster
    + '\nDONE: ' + impl.done + '\nNOT DONE: ' + impl.not_done + '\nPROOFS: ' + impl.proofs + '\n\n'
    + 'Rebuild everything yourself from the branch + 057a605 baselines. Verify: (1) ZERO R-246 device entities remain on\n'
    + 'either map (sweep for GridEntrance/shrine/marker records yourself); reverted blobs navmesh-identical. (2) THE ARMING\n'
    + 'LAW: decode every travel trigger - one-shot flags, <=3 rows/step, NO row on a re-firing step (find the refire steps\n'
    + 'yourself and prove no travel row sits on one), global counts match claims. (3) Every roster connection resolves:\n'
    + 'label -> dest -> level containment -> on-mesh, R4/R5 honored, warden row present + Almyros byte-untouched. (4) If\n'
    + 'portals shipped: byte-shape matches the decoded working template exactly. (5) Gates real (churn negative REDs; budget\n'
    + 'gate REDs on the R-246-era AND the 39-row-era Quests). (6) Diffs intended-only; couplings; contracts 0 P0/0 P1;\n'
    + '(7) docs: ruling verbatim, graveyard entry, honest not_done. GO only if a player can reach + leave every area via\n'
    + 'proven-mechanism travel with no churn-armed rows anywhere. Return verdict GO/NO-GO, issues (severity+command), summary.',
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
  commit: impl && impl.commit_sha, armed_counts: impl && impl.armed_counts, artifact_md5s: impl && impl.artifact_md5s,
  roster: impl && impl.roster, done: impl && impl.done, not_done: impl && impl.not_done,
  vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
