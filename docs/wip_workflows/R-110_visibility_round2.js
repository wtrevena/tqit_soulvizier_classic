export const meta = {
  name: 'visibility-round2-machae-rig',
  description: "Round 2 of the R-108 visibility lane: 4 of 12 Guardian signature skills can never fire on the machae rig, and one guard gains zero. Fix, re-vet, close.",
  phases: [
    { title: 'Fix' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/uber-visibility'
const BR = 'feat/uber-visibility'

const LAW = `
Repo: ${REPO}. Work ONLY in worktree ${WT} on branch ${BR} (it already exists with 15+ commits of
round-1 work - do NOT start over, do NOT branch afresh).
Python: the "py" launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1
SVC_REQUIRE_GATES=1.

⚠️ TWO BUILD TRAPS THE ROUND-1 VET HIT AND DOCUMENTED - avoid wasting time on them:
  1. a fresh worktree has no upstream cache -> build EXITs 1;
  2. with SVC_REQUIRE_GATES=1 the build needs Resources/ staged BESIDE the output or
     mastery_sv_alignment.verify reds - this happens on MAIN too, it is not lane-caused.
  And: stale .arz artifacts can sit in a worktree whose md5 already matches what you expect. DELETE
  the output before rebuilding, or you will "verify" a file you did not just build.

READ FIRST: ${REPO}/CLAUDE.md (4 process laws), ${REPO}/docs/WILL_RULINGS.md (R-100 #18 and R-109 are
the spec), ${REPO}/docs/BACKLOG.md (DEBT REGISTER).

HARD CONSTRAINTS
- DO NOT DEPLOY, do not write to CustomMaps, do not launch or kill TQ/Steam.
- COMMIT EVERY STEP. NO ESTIMATES.
- RETIREMENT PROTOCOL + SHARED-RECORD LAW: never edit a shared record in place; CLONE and repoint.
`

phase('Fix')
let fix = null, verdict = null
for (let round = 2; round <= 4; round++) {
  fix = await agent(`GUARDIANS OF THE GENERAL - ROUND ${round}: MAKE THE SIGNATURE SKILLS ACTUALLY FIRE.
${LAW}

ROUND 1 WAS NO-GO ON EXACTLY ONE THING. Everything else on this branch (R-100 #7 exclamation markers,
R-109 tombstone XP) was independently reproduced and passed - **do not touch, redo, or "improve" those.**

**THE DEFECT, already fully diagnosed by the vet - implement the fix, do not re-investigate:**
The guards' animation table \`records\\xpack\\creatures\\monster\\machae\\anm\\anm_machae.dbr\` defines exactly
FOUR named special-anim refs: **HeavyShot, Slam, Strike, ThunderClap**. Four of the twelve signature skills
demand a clip outside that set, so the engine's StartSkill aborts silently and they NEVER FIRE:
  - \`hero_vomitbile\`            -> 'Belch'        (guard b1)
  - \`empusavenomancer_venombolt\` -> 'Belch'        (guard b1 - so BOTH of its two)
  - \`hero_flamewave\`            -> 'ShadowScythe' (guard c1)
  - \`gigantes_shieldcharge\`     -> 'Charge'       (guard c2)
**Bhikru the Bilespitter (Machae Venomancer) therefore has ZERO castable signature skills**, and his
inherited \`specialAttackSkillName = shieldcharge\` demands 'ShieldCharge' which the table also lacks - so he
ends with no working special of any kind. That is Will's complaint ("no special skills or anything to make
them even noticeable") left in place for one of the six guards.

This is the SAME mechanism as the b42 Ephialtes Dread Nova fix already in this repo
(\`tools/apply_svc_patches.py\`), which is itself a round-2 vet HIGH fix: the engine aborts silently when the
caster's mesh has no clip for the named special animation.

**THE FIX, precedented and small - pick per skill, whichever reads better in play:**
  (a) CLONE the offending skill and blank \`skillSpecialAnimationName\` so it casts on the default clip
      (the exact b42 recipe), or
  (b) repick the skill to a clip the machae rig HAS. The vet measured that 62 shipped mod skills already
      demand one of the machae's four clips (55 of them on 'ThunderClap'), so precedent is abundant.
**CLONE, NEVER EDIT IN PLACE** - \`hero_vomitbile\`, \`hero_flamewave\` and \`gigantes_shieldcharge\` each have
6+ other carriers (xhero_woodear_40, xhero_longjaw_40, am_armorite_40/42, xhero_polybotes_47,
xhero_ephialtes_47). Editing them would silently change those monsters too.

Also fix Bhikru's \`specialAttackSkillName\` so he has a working special, and make sure every guard ends with
at least one signature skill that CAN fire.

**EXTEND THE GATE so this class cannot recur:** for every guard, assert that each skill's
\`skillSpecialAnimationName\` is either empty or present in that creature's own resolved animation table.
Plant a negative that names a clip the rig lacks and confirm it REDS. The round-1 gate passed 14/14 while
four skills were dead - a gate that passes on the defect it exists to catch is the thing being fixed here.

**CORRECT THE OVERSTATEMENTS the vet found:** the report says "12 DISTINCT signature skills"; make it say
what is true after your fix. Register anything still deferred in the DEBT REGISTER - the vet noted this
defect was NOT in it.

Return: status, commit_sha, done (PROVEN - list each of the 12 skills and whether it can now fire, measured
from the built arz), not_done (exhaustive), proofs (commands + outputs + md5s).`,
    { label: `fix:r${round}`, phase: 'Fix', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs'],
    } })

  if (!fix) { log(`round ${round}: fix agent died (transient), retrying`); continue }

  phase('Vet')
  verdict = await agent(`INDEPENDENT ADVERSARIAL VET (round ${round}) of ${BR}.
${LAW}

You are NOT the implementer. Round 1 of this lane shipped four signature skills that could never fire while
its own gate passed 14/14 - so the standard here is: prove the skills FIRE, from the built bytes.

THEY CLAIM:
STATUS: ${fix.status} | COMMIT: ${fix.commit_sha}
DONE: ${fix.done}
NOT DONE: ${fix.not_done}
PROOFS: ${fix.proofs}

CHECK, in priority order:
1. **For EVERY guard and EVERY signature skill: resolve \`skillSpecialAnimationName\` against that creature's
   OWN animation table.** Empty is fine; a named clip must be present in the table. Report the full 12-row
   table yourself. Confirm Bhikru now has at least one working special INCLUDING \`specialAttackSkillName\`.
2. **CLONE, not in-place.** Verify \`hero_vomitbile\`, \`hero_flamewave\`, \`gigantes_shieldcharge\` are
   BYTE-UNCHANGED and their other carriers (xhero_woodear_40, xhero_longjaw_40, am_armorite_40/42,
   xhero_polybotes_47, xhero_ephialtes_47) still point at the originals.
3. **THE GATE MUST NOW CATCH THIS CLASS.** Plant a clip the rig lacks yourself and confirm it REDS.
4. **NO REGRESSION on what already passed:** R-100 #7 markers and R-109 tombstone equality must still hold;
   re-run their negatives.
5. COLLATERAL: record-diff vs your own baseline build of main; 0 REMOVED; Levels/Quests untouched.
6. HONESTY: does the report still overstate? Is everything deferred actually in the DEBT REGISTER?

Return verdict GO or NO-GO, issues (HIGH/MEDIUM/LOW with the command that shows each), and a summary
separating what you reproduced from what you took on trust.`,
    { label: `vet:r${round}`, phase: 'Vet', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } })

  if (!verdict) {
    verdict = { verdict: 'NO-GO', issues: ['VET AGENT DIED (transient) - re-run unchanged, not a code finding'], summary: 'vet did not return' }
  }
  log(`round ${round}: ${verdict.verdict} (${verdict.issues.length} issues)`)
  if (verdict.verdict === 'GO') break
}

return {
  status: (verdict && verdict.verdict) === 'GO' ? 'go' : 'no-go',
  branch: BR,
  commit: fix && fix.commit_sha,
  done: fix && fix.done,
  not_done: fix && fix.not_done,
  vet: verdict && verdict.summary,
  open_issues: (verdict && verdict.issues) || [],
}
