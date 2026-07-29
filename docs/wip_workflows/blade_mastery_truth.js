export const meta = {
  name: 'blade-mastery-truth',
  description: "Answer Will's Blade Mastery question from ground truth (does the dodge bonus need a sword/dagger/axe, or any weapon?) and make the tooltip tell the truth.",
  phases: [
    { title: 'Answer' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/blade-mastery'
const BR = 'fix/blade-mastery-truth'

const COMMON = `
Repo: ${REPO}. Work ONLY in worktree ${WT} on branch ${BR}
(create if absent: git worktree add ${WT} -b ${BR} main   -- main tip 4f0299c, which contains the b99
content wave AND the b98 endless-hunt lane. There is a STALE branch fix/blade-mastery-gate sitting at the
old a0276ab; ignore it, do not build on it).
Python: the "py" launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1.

READ FIRST and obey: ${REPO}/CLAUDE.md (4 process laws), ${REPO}/docs/WILL_RULINGS.md (design law of record,
append VERBATIM same-turn), ${REPO}/docs/BACKLOG.md (DEBT REGISTER).
Rulings decades already claimed: main up to R-80 and R-90..R-96; feat/leinth-wave R-73..R-76; fix/green-diff
up to R-71; a feat/sanctuary-populate lane is running in parallel and will claim its own - prove your decade
free against main AND every in-flight branch with git grep before writing, and say which you took.

HARD CONSTRAINTS
- DO NOT DEPLOY, do not write to CustomMaps, do not launch or kill TQ/Steam. The orchestrator owns deploys.
- arz+Text are COUPLED - a tag change means building BOTH.
- COMMIT EVERY STEP; Will's machine can be throttled mid-task and uncommitted work is lost work.
- Never mutate shared git config (no core.* / user.* writes) from a linked worktree.
- NO ESTIMATES. Measured values with the command that produced them, or "not measured".
`

phase('Answer')
const ans = await agent(`BLADE MASTERY - ANSWER WILL'S QUESTION FROM GROUND TRUTH, THEN FIX THE LIE.
${COMMON}

WILL ASKED, verbatim: "does the occult skill blade mastery chance to dodge attacks bonus apply if you are
using any weapon or only if you are using a sword dagger or axe as the skill description says?"

This is a QUESTION FIRST. He wants a true answer he can act on in play. The fix is secondary to being right.

WHAT WE ALREADY BELIEVE (verify it, do not assume it): records\\skills\\stealth\\drx_dual_blade.dbr carries
Sword=1, Axe=1, dualWieldOnly=1, with all four bonuses on the single record and no attached records. If that
holds, the honest answer is that the bonus requires DUAL-WIELDING and only sword/axe qualify - which is
narrower than the description says in two separate ways.

ESTABLISH THE TRUTH:
1. Read the ACTUAL record out of a built arz (state its md5). Enumerate every field that gates the bonus:
   the weapon-class flags, dualWieldOnly, and anything else the template says participates.
2. Read the TEMPLATE for that record class out of the engine's own Toolset/Templates.arc and state what each
   gating field means. Do not infer semantics from the field name alone.
3. DAGGER: TQAE's weapon classes are not the same list as the tooltip's prose. Establish whether "dagger" is
   even a distinct equippable class here or whether daggers are Sword-class items. Answer it with data.
4. PROVE IT BY PRECEDENT, not by reading alone: find base-game or SV skills with the SAME gating shape and
   confirm the shape means what you say. A single mis-read field would make this whole answer wrong.
5. Determine whether ALL FOUR bonuses share the gate or whether only some do - Will asked specifically about
   chance-to-dodge, so if the four bonuses differ, that distinction IS the answer.
6. Say explicitly what a player must be holding, in both hands, for the dodge bonus to apply.

THEN FIX THE TOOLTIP so it tells the truth. It is a player surface, so the player-surface checklist applies.
- Change the TEXT to match the mechanics. Do NOT change the mechanics to match the text - that is a balance
  change and therefore Will's call, not yours. If you believe the mechanics are the thing that is wrong,
  say so as a WILL_DECISION with a recommendation, and still ship the honest text.
- Match the game's own tooltip voice and the amgoz1 bar - read neighbouring skill descriptions and mirror
  their phrasing. Do not invent a house style.
- A tag change means arz+Text rebuild TOGETHER. validate_tags must pass and the tag must actually resolve in
  the built Text.arc - read it back out.
- Add a GATE that ties the description to the gating fields, so a future edit to one without the other reds
  the build (process law #4). Plant negative tests that prove the gate fires.
- Append the ruling VERBATIM to docs/WILL_RULINGS.md, same turn. Add a BACKLOG gate record.

SWEEP FOR SIBLINGS while you are here - this is standing practice, and it is cheap now: are there OTHER
skills in this mod whose description promises a weapon class or condition the record does not enforce (or
enforces more narrowly)? Report what you find with the evidence. Fix only what is unambiguous and text-only;
file the rest as debt rather than expanding scope.

Return: answer (the plain-language answer FOR WILL - lead with it, no preamble, no hedging, and state
exactly what he must equip), mechanism (the field-level truth with md5s and template semantics), precedent
(the same-shape skills you checked), fix (what you changed), siblings (the sweep result),
will_decisions (anything that is a balance call), status, commit_sha, not_done, proofs.`,
  { label: 'answer', schema: {
    type: 'object',
    properties: { answer: { type: 'string' }, mechanism: { type: 'string' }, precedent: { type: 'string' },
      fix: { type: 'string' }, siblings: { type: 'string' },
      will_decisions: { type: 'array', items: { type: 'string' } },
      status: { type: 'string' }, commit_sha: { type: 'string' }, not_done: { type: 'string' },
      proofs: { type: 'string' } },
    required: ['answer', 'mechanism', 'precedent', 'fix', 'siblings', 'will_decisions', 'status', 'commit_sha', 'not_done', 'proofs'],
  } })

phase('Vet')
const vet = await agent(`INDEPENDENT ADVERSARIAL VET of ${BR}.
${COMMON}

You are NOT the implementer and you do not trust them. Will is going to ACT on this answer in play, so a
confidently wrong answer is the worst possible outcome here - worse than no answer.

THEY CLAIM:
ANSWER: ${ans.answer}
MECHANISM: ${ans.mechanism}
PRECEDENT: ${ans.precedent}
FIX: ${ans.fix}
SIBLINGS: ${ans.siblings}
NOT DONE: ${ans.not_done}
PROOFS: ${ans.proofs}

INDEPENDENTLY:
1. Re-read the record out of an arz YOU build. Does the mechanism claim survive? Re-read the template
   yourself - a mis-read gating field makes the entire answer wrong and this is the highest-value check.
2. Is the DAGGER conclusion right? Verify against actual shipped dagger-class items, not against prose.
3. Does the new description text ACTUALLY resolve in the built Text.arc, and is it TRUE - not merely truer?
   Read it back out of the built artifact. Check it against the four bonuses individually.
4. Does the gate genuinely fail on a broken invariant? Plant the negative yourself, both directions.
5. COLLATERAL: record-diff against a baseline you build from main 4f0299c. Anything outside scope is a
   finding. Confirm 0 REMOVED records - b98's 15 new records and b99's sargoth set must survive.
6. Did they silently change MECHANICS while claiming a text-only fix? That would be an undisclosed balance
   change and is a HIGH finding.
7. HONESTY: is anything claimed that they cannot prove? Is the sibling sweep real or gestured at?

Return verdict GO or NO-GO, issues (HIGH/MEDIUM/LOW with evidence), and a summary separating what you
reproduced from what you took on trust.`,
  { label: 'vet', schema: {
    type: 'object',
    properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
      issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
    required: ['verdict', 'issues', 'summary'],
  } })

let final = ans
if (vet.verdict !== 'GO') {
  phase('Answer')
  final = await agent(`BLADE MASTERY - ROUND 2. The independent vet returned NO-GO.
${COMMON}

YOUR ROUND-1 OUTPUT:
ANSWER: ${ans.answer}
MECHANISM: ${ans.mechanism}
FIX: ${ans.fix}

THE VET'S ISSUES - clear every one:
${JSON.stringify(vet.issues, null, 1)}
${vet.summary}

Re-measure rather than restate. If a finding is genuinely wrong, prove it with a command and its output and
say so - that is a legitimate outcome, but "I already said so" is not proof. Getting the ANSWER right matters
more than the code: Will will act on it in play.

Return the same fields as before.`,
    { label: 'answer:r2', schema: {
      type: 'object',
      properties: { answer: { type: 'string' }, mechanism: { type: 'string' }, precedent: { type: 'string' },
        fix: { type: 'string' }, siblings: { type: 'string' },
        will_decisions: { type: 'array', items: { type: 'string' } },
        status: { type: 'string' }, commit_sha: { type: 'string' }, not_done: { type: 'string' },
        proofs: { type: 'string' } },
      required: ['answer', 'mechanism', 'precedent', 'fix', 'siblings', 'will_decisions', 'status', 'commit_sha', 'not_done', 'proofs'],
    } })
}

return {
  status: vet.verdict === 'GO' ? 'go' : 'round2-unvetted',
  branch: BR,
  commit: final.commit_sha,
  answer_for_will: final.answer,
  mechanism: final.mechanism,
  fix: final.fix,
  siblings: final.siblings,
  will_decisions: final.will_decisions,
  not_done: final.not_done,
  vet: vet.summary,
  open_issues: vet.issues,
}
