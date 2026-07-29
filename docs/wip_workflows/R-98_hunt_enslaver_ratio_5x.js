export const meta = {
  name: 'hunt-enslaver-ratio-5x',
  description: "Will 2026-07-29: the Hunt must be exactly 5x as likely to appear as the Enslaver in the pools they share. Enslaver rates are FROZEN - move the Hunt. Measure, resolve the collision with the 'one sighting per act' gate, implement, adversarially vet.",
  phases: [
    { title: 'Measure' },
    { title: 'Design' },
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/hunt-ratio'
const BR = 'feat/hunt-enslaver-ratio'

const RULING = `WILL'S RULING, 2026-07-29, VERBATIM - this is the requirement, quote it into the ledger exactly:
"Make the hunt be 5 times as likely to appear than the enslaver in the areas that they share. do not adjust
the enslaver spawn rates, adjust the hunt spawn rate accordingly. the enslaver spawn rate is appropriate
currently based on my playthroughs of the game so far"`

const COMMON = `
Repo: ${REPO}. Work ONLY in worktree ${WT} on branch ${BR}
(create if absent: git worktree add ${WT} -b ${BR} main   -- main tip 4f0299c, which contains BOTH the b99
content wave AND the b98 endless-hunt lane. Do NOT branch from anything older; the b98 weights you are
retuning only exist on that tip).
Python: the "py" launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 and
SVC_REQUIRE_GATES=1.

READ FIRST and obey - law, not suggestion:
  ${REPO}/CLAUDE.md                  (4 process laws: rulings ledger, RETIREMENT PROTOCOL, player-surface
                                      checklist, no-new-surface-without-a-gate + debt register)
  ${REPO}/docs/WILL_RULINGS.md       (design law of record; append VERBATIM, same turn, never rewrite history)
  ${REPO}/docs/reports/b98_endless_hunt.md   (the lane that set the weights you are about to change)
  ${REPO}/docs/BACKLOG.md            (gate records + DEBT REGISTER; BL-b98-DEBT-11 IS THIS ITEM)

${RULING}

THE THREE STANDING CONSTRAINTS THIS COLLIDES WITH - you must reconcile, not ignore:
  * R-18 forbids changing the ENSLAVER's spawn rate. Will has now re-affirmed it explicitly and given the
    reason: his own playthroughs. The Enslaver's weights are FROZEN. Not "preferably unchanged" - frozen.
    If your change touches an Enslaver weight anywhere, you have failed.
  * R-96 is a BUILD GATE, not a comment: the Hunt's census must re-derive to "roughly one sighting per act"
    (b98 measured Act IV 0.955 / Act V 1.034 / full pass 1.989 at p_slot 1/1250) and the build goes RED
    outside the band. Lowering the Hunt's rate in the shared pools pushes on that number. You MUST measure
    which way and by how much.
  * BL-b98-DEBT-11 recorded the defect being fixed: the Hunt is currently 48-53x MORE common than the
    roaming Enslaver in every pool they share. Target is 5x. So this is roughly a 10x reduction - but derive
    the real factor, do not assume mine.

HARD CONSTRAINTS
- DO NOT DEPLOY. Write NOTHING to CustomMaps. Do not launch or kill TQ or Steam. The orchestrator owns every
  deploy and every Steam upload.
- arz+Text are COUPLED; Levels+Quests are COUPLED.
- COMMIT EVERY STEP. Will's machine can be throttled mid-task; uncommitted work is lost work.
- Never mutate shared git config (no core.* / user.* writes) from a linked worktree - it writes the SHARED
  .git/config and has corrupted both repos before.
- NO ESTIMATES ANYWHERE. Every number comes with the command that produced it, or you write "not measured".
- Rulings decades in use: main holds up to R-80 and R-90..R-96; feat/leinth-wave R-73..R-76; fix/green-diff
  up to R-71; parallel lanes feat/sanctuary-populate and fix/blade-mastery-truth are claiming their own right
  now. Prove your decade free with git grep against main AND every in-flight branch before you write.
`

phase('Measure')
const [weights, model, confounders] = await parallel([
  () => agent(`HUNT-vs-ENSLAVER RATIO - MEASUREMENT LANE A: THE GROUND-TRUTH WEIGHT TABLE.
${COMMON}

Build the arz yourself from ${BR} (state its md5 and record count) and measure, from the BUILT BYTES, never
from a document - every published hash in this repo has been stale at some point.

PRODUCE THE AUTHORITATIVE TABLE. For every ProxyPool record in the database that contains EITHER
um_toxeus_hunt_99 / um_toxeus_hunt_l_99 (the Hunt and its endless Legendary variant) OR the roaming
Enslaver um_toxeus_enslaver_99:
  - pool path
  - which of those creatures it carries, in which nameN slot
  - that slot's weightN, and the POOL TOTAL WEIGHT (sum of all weightN in the record)
  - the realised per-slot probability weightN / total
  - the slot's limitN, spawnMin/spawnMax, championChance
  - how many distinct PROXIES reference that pool, and which area (area001..area008) those proxies live in

Then answer precisely:
  1. How many pools carry the Hunt? The Enslaver? How many carry BOTH (the "shared" set Will's ruling is
     scoped to)? b98 said 346 / 63 shared - reproduce or refute that, with your own command.
  2. In the shared pools, what is the CURRENT realised ratio p_hunt / p_enslaver? Give the distribution -
     min, median, max, and whether it is uniform. b98 claimed 48-53x; reproduce or refute.
  3. Is the ratio constant across shared pools, or does it vary? If it varies, a single flat weight cannot
     satisfy "5x" everywhere - say so explicitly and quantify the spread.
  4. Do BOTH Hunt variants appear in shared pools, or only the base one? The ruling says "the hunt" - if the
     endless Legendary variant sits in a different pool set, say which, because the fix may need to treat
     them differently.
  5. What EXACT weight per shared pool makes p_hunt = 5.00 x p_enslaver? Note weightN's dtype and whether
     the engine accepts the value you need - if the required weight is fractional or below 1, say so NOW,
     because that is the whole crux of whether this ruling is even expressible in this data model.
     If integer weights cannot hit exactly 5.00x, give the achievable values that bracket it and the
     resulting real ratios.

Return the full table (machine-readable), the counts, the current ratio distribution, the required weights,
and any reason the target may be inexpressible. This lane MEASURES ONLY - change nothing, commit only
measurement scripts and the data.`,
    { label: 'measure:weights', phase: 'Measure', schema: {
      type: 'object',
      properties: { arz_md5: { type: 'string' }, counts: { type: 'string' }, table: { type: 'string' },
        current_ratio: { type: 'string' }, required_weights: { type: 'string' },
        expressibility: { type: 'string' }, commands: { type: 'string' } },
      required: ['arz_md5', 'counts', 'table', 'current_ratio', 'required_weights', 'expressibility', 'commands'],
    } }),

  () => agent(`HUNT-vs-ENSLAVER RATIO - MEASUREMENT LANE B: WHAT THIS DOES TO THE "ONE SIGHTING PER ACT" GATE.
${COMMON}

You are the independent check on the R-96 collision. Another agent is measuring the weight table; do NOT
coordinate with it - derive everything yourself, because agreement between two independent derivations is
the only evidence worth having here.

R-96 gates the build on the Hunt's expected sightings landing near one per act. b98 published Act IV 0.955 /
Act V 1.034 / full pass 1.989 at p_slot 1/1250, re-derived by a gate from a 797-placement census.

DO THIS:
1. Find and READ the census + the R-96 gate (tools/, docs/reports/b98_endless_hunt.md). Re-derive the
   published figures yourself from the census data. Do they reproduce EXACTLY? If not, that is a finding
   that outranks everything else in this workflow - say so loudly.
2. Understand the model's shape: which pools/areas/proxies contribute, and how sensitive the total is to a
   weight change in a SUBSET of pools.
3. MODEL BOTH READINGS of Will's ruling and give the numbers for each:
   (a) SHARED-ONLY: change the Hunt's weight ONLY in the pools he shares with the Enslaver (the literal
       reading of "in the areas that they share"). Non-shared pools keep b98's weight.
   (b) GLOBAL: apply the same reduced per-slot weight to ALL of the Hunt's pools.
   For each: the new expected sightings for Act IV, Act V and a full pass, and whether it stays inside the
   R-96 band or reds the build.
4. State plainly whether reading (a) satisfies BOTH rulings simultaneously. This is the single most decision-
   relevant number in this workflow. If (a) keeps sightings in band, there is no collision and no escalation.
   If it does not, quantify the conflict exactly: Will cannot have both "5x the Enslaver" and "one sighting
   per act" unless X, where X is a real, specific option.
5. If the readings conflict, enumerate the genuine options with their consequences - e.g. accept fewer
   sightings; raise the Hunt in non-shared pools to compensate (does that violate the spirit of his ruling?);
   widen the R-96 band with a new ruling. Do NOT pick for Will where it is a taste call, and do NOT silently
   loosen the gate - a gate that gets relaxed to fit the change it was built to catch is worthless.

Return the reproduced figures, the model, both readings' numbers, the verdict on whether (a) satisfies both,
and the options if it does not. MEASURE ONLY - change nothing.`,
    { label: 'measure:sightings', phase: 'Measure', schema: {
      type: 'object',
      properties: { reproduced: { type: 'string' }, model: { type: 'string' },
        reading_shared_only: { type: 'string' }, reading_global: { type: 'string' },
        collision_verdict: { type: 'string' }, options: { type: 'array', items: { type: 'string' } } },
      required: ['reproduced', 'model', 'reading_shared_only', 'reading_global', 'collision_verdict', 'options'],
    } }),

  () => agent(`HUNT-vs-ENSLAVER RATIO - MEASUREMENT LANE C: CONFOUNDERS AND BLAST RADIUS.
${COMMON}

"5 times as likely to appear" is a statement about what Will EXPERIENCES in play, not about a weight field.
Your job is to find every mechanism between the weight and the encounter that could make a naive
weight-ratio fix fail to deliver the ruling, and every thing a weight sweep could break.

INVESTIGATE, from ground truth:
1. Between weightN and "the player meets him", what else intervenes? limitN, spawnMin/spawnMax, chanceToRun
   on the proxy, championChance, the spawn BUDGET (difficultyEquation / characterDifficultyEquation - note
   the Hunt and the Enslaver may cost different amounts, which changes realised frequency even at equal
   weight), per-difficulty pool slots, and monster-level windows. For each: does it differ between the Hunt
   and the Enslaver? Quantify. If the Hunt costs more budget than the Enslaver, an exact 5x weight ratio
   does NOT produce an exact 5x encounter ratio - and that distinction is the whole point of this lane.
2. NOTE, do not re-derive: b98 proved difficultyLimitsFile only SCALES player level and never filters
   whether a proxy resolves, refuting the earlier b91 reasoning. Confirm that holds here; do not rebuild it.
3. Does the roaming Enslaver appear ANYWHERE outside those shared pools? Does the Hunt appear in pools with
   OTHER Toxeus champions (the Devourer um_bloodtoxeus_99), where a weight sweep might disturb a third
   party's rate? Enumerate every creature whose realised rate moves if the Hunt's weight in a pool changes
   (in a fixed-total pool, lowering one slot RAISES everyone else's share - quantify that spill).
4. What gates, contracts, goldens or verify() hooks currently assert anything about these weights? A sweep
   that reds an unrelated gate is a real risk. List them and what they assert.
5. The RETIREMENT PROTOCOL applies to the b98 code that set these weights: if a constant or comment becomes
   wrong, it must be corrected, not left to mislead. Identify every place in tools/ and docs/ that states or
   implies the current ratio or weight, and that will be a lie after this change.

Return findings, the spill analysis, the gate inventory, the doc/code lie list, and any reason the ruling as
literally worded would NOT produce a 5x felt experience. MEASURE ONLY - change nothing.`,
    { label: 'measure:confounders', phase: 'Measure', schema: {
      type: 'object',
      properties: { intervening: { type: 'string' }, spill: { type: 'string' },
        third_parties: { type: 'string' }, gates: { type: 'string' }, lies: { type: 'string' },
        felt_vs_weight: { type: 'string' } },
      required: ['intervening', 'spill', 'third_parties', 'gates', 'lies', 'felt_vs_weight'],
    } }),
])

log('measurement done; collision verdict: ' + String(model && model.collision_verdict || 'MISSING').slice(0, 200))

phase('Design')
const design = await agent(`HUNT-vs-ENSLAVER RATIO - DESIGN / RECONCILE.
${COMMON}

Three independent measurement lanes reported. Treat them as EVIDENCE, not as truth - where two disagree, go
back to the bytes and settle it yourself, and say which was wrong.

LANE A (weights): arz ${weights && weights.arz_md5}
COUNTS: ${weights && weights.counts}
CURRENT RATIO: ${weights && weights.current_ratio}
REQUIRED WEIGHTS: ${weights && weights.required_weights}
EXPRESSIBILITY: ${weights && weights.expressibility}
TABLE: ${String(weights && weights.table || '').slice(0, 4000)}

LANE B (the R-96 collision):
REPRODUCED: ${model && model.reproduced}
SHARED-ONLY READING: ${model && model.reading_shared_only}
GLOBAL READING: ${model && model.reading_global}
COLLISION VERDICT: ${model && model.collision_verdict}
OPTIONS: ${JSON.stringify(model && model.options)}

LANE C (confounders):
INTERVENING MECHANISMS: ${confounders && confounders.intervening}
SPILL: ${confounders && confounders.spill}
THIRD PARTIES: ${confounders && confounders.third_parties}
GATES: ${confounders && confounders.gates}
DOC/CODE LIES: ${confounders && confounders.lies}
FELT vs WEIGHT: ${confounders && confounders.felt_vs_weight}

DECIDE AND SPECIFY, precisely enough that the implementer has no latitude:
1. THE SCOPE. Shared pools only, or global? Will wrote "in the areas that they share", which is the literal
   scope, and reading (a) is the default UNLESS the numbers show it produces something incoherent (e.g. the
   Hunt 10x rarer in shared areas than 20 metres away in a non-shared one, in a way a player would notice).
   Justify the choice in one paragraph with the numbers, not with taste.
2. THE EXACT WEIGHT, per pool, with the resulting realised ratio per pool. If integer weights cannot hit
   5.00x, state the achievable ratio and how far off it is. Closest-achievable is fine; pretending it is
   exact is not.
3. THE R-96 OUTCOME. State the new expected sightings and whether the gate passes. If the gate would red:
   do NOT loosen it. Present the conflict as a WILL DECISION with the specific options and a recommendation,
   and design the change so it is a one-constant retune once he answers.
4. THE SPILL. Every third party whose share moves, with the before/after numbers, and whether any of it is
   large enough to matter.
5. WHAT MUST BE CORRECTED under the RETIREMENT PROTOCOL: the constants, comments, gate messages, report
   claims and ledger lines that become false.
6. THE GATE. R-96 must keep working, and the new 5x invariant needs its own gate so a future edit cannot
   silently break the ratio Will just specified. Specify both, including the planted negatives that prove
   they fire.

Write the design into docs/reports/ and COMMIT it before returning. Return: scope (with justification),
weights (the exact per-pool spec), r96 (outcome + whether it passes), spill, corrections, gates,
will_decisions (only genuine taste calls), risks.`,
  { label: 'design', schema: {
    type: 'object',
    properties: { scope: { type: 'string' }, weights: { type: 'string' }, r96: { type: 'string' },
      spill: { type: 'string' }, corrections: { type: 'string' }, gates: { type: 'string' },
      will_decisions: { type: 'array', items: { type: 'string' } },
      risks: { type: 'array', items: { type: 'string' } }, commit_sha: { type: 'string' } },
    required: ['scope', 'weights', 'r96', 'spill', 'corrections', 'gates', 'will_decisions', 'risks', 'commit_sha'],
  } })

let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  phase('Implement')
  impl = await agent(`HUNT-vs-ENSLAVER RATIO - IMPLEMENT (round ${round}).
${COMMON}

THE DESIGN:
SCOPE: ${design.scope}
WEIGHTS: ${design.weights}
R-96 OUTCOME: ${design.r96}
SPILL: ${design.spill}
CORRECTIONS REQUIRED: ${design.corrections}
GATES: ${design.gates}
WILL DECISIONS: ${JSON.stringify(design.will_decisions)}
RISKS: ${JSON.stringify(design.risks)}
${round > 1 ? `\nTHE INDEPENDENT VET RETURNED **${verdict.verdict}**. CLEAR EVERY ISSUE:\n${JSON.stringify(verdict.issues, null, 1)}\n${verdict.summary}\nRe-measure rather than restate. If a finding is genuinely wrong, prove it wrong with a command and its output - that is a legitimate outcome, but "I already said so" is not proof.` : ''}

Treat the design as a proposal. If implementing exposes it as wrong, fix it, SAY SO explicitly, and implement
what is correct.

IMPLEMENT:
- The weight change, in the b98 module that owns these weights (registry ORDER IS SEMANTIC - later means
  later writer; justify where it runs). Put the ratio behind a NAMED CONSTANT with a comment citing the
  ruling, so a future retune is one line.
- ZERO writes to any Enslaver weight. This is the one thing Will said twice. Prove it with a diff.
- Append the ruling to docs/WILL_RULINGS.md VERBATIM (quote Will's sentence exactly as given above), same
  turn as the code, in a decade you proved free. Correct BL-b98-DEBT-11 to CLOSED with the real numbers.
- Every correction from the design's RETIREMENT PROTOCOL list - no comment or doc left asserting the old
  ratio.
- The new ratio gate + the preserved R-96 gate, each with PLANTED NEGATIVE TESTS proving they actually fail
  when the invariant breaks. Test both directions (too high AND too low).
- BACKLOG gate record for the build. Tag the build (verify the tag is free; say which you took).

PROVE IT:
- Full build, gates required, exit 0. Record arz + Text md5s.
- Record-diff vs a baseline YOU build from main 4f0299c in the same environment. Every changed record and
  field attributed to a named intent; ZERO unattributed. 0 REMOVED records is load-bearing (b98's 15 new
  records and b99's summon_sargoth + pets must survive).
- Read the realised ratio back OUT of the built arz, per shared pool, and show it is 5x (or the closest
  achievable, named as such).
- Re-derive the R-96 sightings figure from the built artifact and state pass/fail.
- Contracts + validate_tags + registry verifies, with the numbers.

Return: status, commit_sha, done (what is PROVEN, with the proof), not_done (exhaustive - everything
unfinished, unproven, launch-gated or Will's call; a triaged item is NOT a done item), proofs.`,
    { label: `impl:r${round}`, schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs'],
    } })

  phase('Vet')
  const votes = await parallel([
    () => agent(`ADVERSARIAL VET (round ${round}) of ${BR} - LENS 1: DID IT DELIVER WILL'S RULING?
${COMMON}

You are NOT the implementer and you do not trust them. Will gave a precise numeric instruction based on his
own playthroughs. A change that misses the ratio, or that hits it on paper but not in play, is a failure.

THEY CLAIM:
STATUS: ${impl.status} | COMMIT: ${impl.commit_sha}
DONE: ${impl.done}
NOT DONE: ${impl.not_done}
PROOFS: ${impl.proofs}

INDEPENDENTLY (build the arz yourself; accept no hash from any document):
1. Read the realised probabilities back out of the BUILT arz for every shared pool. Is p_hunt / p_enslaver
   actually 5.00x? Give the distribution. If it is "closest achievable", is that honestly disclosed?
2. Is the ENSLAVER genuinely untouched? Diff every Enslaver-bearing record against a baseline you build.
   Any movement at all is a HIGH finding - Will said this twice.
3. Does the change actually mean what it claims about ENCOUNTERS, not just weights? Re-check the confounders
   (limitN, spawn budget cost, chanceToRun, championChance). If the Hunt and Enslaver cost different budget,
   does a 5x weight ratio really deliver a 5x felt rate? Say so plainly either way.
4. R-96: re-derive the sightings figure yourself from the built artifact. Does the gate pass? Was it QUIETLY
   LOOSENED to accommodate this change? A gate relaxed to fit the change it exists to catch is a HIGH finding.
5. Do the new gates actually fire? Plant the negatives yourself, both directions.

Return verdict GO or NO-GO with issues tagged HIGH/MEDIUM/LOW, each with the command that shows it.`,
      { label: `vet:ruling:r${round}`, phase: 'Vet', schema: {
        type: 'object',
        properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
          issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
        required: ['verdict', 'issues', 'summary'],
      } }),

    () => agent(`ADVERSARIAL VET (round ${round}) of ${BR} - LENS 2: COLLATERAL, HONESTY AND THE LEDGER.
${COMMON}

You are NOT the implementer and you do not trust them. Another vet is checking whether the ratio is right;
you are checking whether anything ELSE broke and whether the report tells the truth. Do not duplicate their
lens - if you find a ratio problem, report it, but spend your effort here.

THEY CLAIM:
STATUS: ${impl.status} | COMMIT: ${impl.commit_sha}
DONE: ${impl.done}
NOT DONE: ${impl.not_done}
PROOFS: ${impl.proofs}

INDEPENDENTLY:
1. COLLATERAL. Record-diff against a baseline you build from main 4f0299c. Anything outside the intended
   weight sweep is a finding. Confirm 0 REMOVED records - b98's 15 new records and b99's summon_sargoth +
   pets\\sargoth_{1,2,3} must survive. Confirm Levels.arc and Quests.arc are untouched.
2. SPILL. In a fixed-total pool, lowering the Hunt RAISES every other member's share. Quantify it yourself
   for the third parties. Is any of it big enough that a player notices some other monster got commoner?
   Was it disclosed?
3. RETIREMENT PROTOCOL. Hunt the repo for every comment, constant, gate message, report line and ledger
   entry that still asserts the OLD ratio or the old weight. Each survivor is a finding - this repo has
   already been burned twice by a stale comment ("Hades trash pools ONLY") that sent later lanes wrong.
4. LEDGER. Is Will's sentence quoted VERBATIM? Is the decade genuinely free against main and every in-flight
   branch (feat/leinth-wave, feat/sanctuary-populate, fix/blade-mastery-truth, fix/green-diff)? Did it
   silently overturn an existing ruling? Is BL-b98-DEBT-11 closed with real numbers rather than a claim?
5. HONESTY AUDIT. Compare DONE line by line against what you can prove. Anything asserted but unproven is a
   finding; so is anything done but not disclosed. Is every deferred item really in the DEBT REGISTER?
   Is the R-96 outcome reported honestly, including if it got worse?

Return verdict GO or NO-GO with issues tagged HIGH/MEDIUM/LOW, each with the command that shows it, and a
summary separating what you reproduced from what you took on trust.`,
      { label: `vet:collateral:r${round}`, phase: 'Vet', schema: {
        type: 'object',
        properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
          issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
        required: ['verdict', 'issues', 'summary'],
      } }),
  ])

  const live = votes.filter(Boolean)
  const bad = live.filter(v => v.verdict !== 'GO')
  verdict = {
    verdict: bad.length === 0 && live.length > 0 ? 'GO' : 'NO-GO',
    issues: live.flatMap(v => v.issues || []),
    summary: live.map(v => `[${v.verdict}] ${v.summary}`).join('\n\n'),
  }
  log(`round ${round}: ${verdict.verdict} (${verdict.issues.length} issues from ${live.length} vets)`)
  if (verdict.verdict === 'GO') break
}

return {
  status: verdict.verdict === 'GO' ? 'go' : 'no-go',
  branch: BR,
  commit: impl.commit_sha,
  scope: design.scope,
  weights: design.weights,
  r96: design.r96,
  collision: model && model.collision_verdict,
  spill: design.spill,
  done: impl.done,
  not_done: impl.not_done,
  proofs: impl.proofs,
  vet: verdict.summary,
  open_issues: verdict.issues,
  will_decisions: (design.will_decisions || []).concat(model && model.options || []),
}
