export const meta = {
  name: 'r99-all-toxeus-apex-orb',
  description: 'R-99 RATIFIED: put EVERY Toxeus variant on genericbossorb_05, including the Endless Hunt (who has no orb at all) and the low-level inherited one. Make the gate roster-derived. Implement + adversarially vet.',
  phases: [
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/toxeus-apex-roster'
const BR = 'feat/toxeus-apex-roster'

const COMMON = `
Repo: ${REPO}. Work ONLY in worktree ${WT} on branch ${BR}
(create if absent: git worktree add ${WT} -b ${BR} main).
main already contains the b99 content wave, the b98 endless-hunt lane, the b94 leinth wave, and R-99 itself.
Do NOT branch from anything older - genericbossorb_05 only exists on this tip.
Python: the "py" launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1
SVC_REQUIRE_GATES=1.

READ FIRST and obey - law, not suggestion:
  ${REPO}/CLAUDE.md                 (4 process laws: rulings ledger, RETIREMENT PROTOCOL, player-surface
                                     checklist, no-new-surface-without-a-gate + debt register)
  ${REPO}/docs/WILL_RULINGS.md      -> **R-99 is the whole spec for this lane. Read it before anything else.**
                                     Note R-47 (generic un-named orbs) and R-48 (100% Toxeus souls) which
                                     this must not disturb.
  ${REPO}/tools/patches/uber_apex_orb.py   (the module you are extending - read its full docstring)
  ${REPO}/tools/debug/negtest_uber_apex_orb.py  (the 16-subtest harness you must extend, not weaken)
  ${REPO}/docs/BACKLOG.md           (gate records + DEBT REGISTER)

GROUND TRUTH ALREADY MEASURED (reproduce it, do not trust it - every hash in this repo has been stale once).
Merged-main build arz md5 967b1f97137bf6479c18c08e9dd6ffc4, 51,124 records:
  um_toxeus_enslaver_99   charLevel 40/68/100  -> genericbossorb_05   ALREADY COVERED
  um_bloodtoxeus_99       charLevel 40/68/100  -> genericbossorb_05   ALREADY COVERED
  um_toxeus_hunt_99       charLevel 40/68/100  -> NO treasureProxyName AT ALL   <- ADD (highest value: this
                                                  is the champion Will has actually fought in play)
  um_toxeus_hunt_l_99     charLevel 40/68/100  -> NO treasureProxyName AT ALL   <- ADD
  um_toxeus_99            charLevel 33/66/99   -> NO treasureProxyName          <- ADD
  um_toxeus_21            charLevel 25/45/65   -> genericbossorb_01 (lowest)    <- ADD (Will OVERRULED the
                                                  balance objection with reasons; see R-99. Do NOT scale him
                                                  down "in the spirit of" the ruling.)
  z_toxeus, old_z_toxeus  charLevel 40/56/71   -> NONE (zzdev dev dummies)      <- INCLUDE per "all versions",
                                                  but FIRST verify whether either is placed anywhere in the
                                                  shipped Levels.arc. Inert is a fine outcome; a silent
                                                  exclusion is not. Record the placement finding.
Leinth (q_leinth_47/49/50) stays on her own bespoke chest, upgraded in place - do not repoint her.

HARD CONSTRAINTS
- DO NOT DEPLOY. Write NOTHING to CustomMaps. Do not launch or kill TQ or Steam. The orchestrator owns
  every deploy and every Steam upload.
- genericbossorb_04 and its NINETEEN other consumers must stay BYTE-UNCHANGED. That is the entire reason a
  new tier was minted. Prove it.
- R-48 (Toxeus souls at 100%) must stay intact - souls are Finger2 equipment, orbs are treasureProxyName,
  and they are independent. Prove the independence held.
- COMMIT EVERY STEP; the weekly model budget is nearly exhausted and this may be interrupted at any moment.
  Small, frequent, described commits. Uncommitted work is lost work.
- Never mutate shared git config (no core.* / user.* writes) from a linked worktree.
- NO ESTIMATES. Measured numbers with the command that produced them, or "not measured".
`

phase('Implement')
let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  impl = await agent(`R-99 ALL-TOXEUS APEX ORB - IMPLEMENT (round ${round}).
${COMMON}
${round > 1 ? `\nTHE INDEPENDENT VET RETURNED **${verdict.verdict}**. CLEAR EVERY ISSUE:\n${JSON.stringify(verdict.issues, null, 1)}\n${verdict.summary}\nRe-measure rather than restate. If a finding is genuinely wrong, prove it with a command and its output.` : ''}

THE WORK, which R-99 has fully specified - no design latitude, but plenty of care required:

1. EXTEND THE ROSTER in tools/patches/uber_apex_orb.py so every Toxeus creature record points at
   genericbossorb_05. Derive the roster from the DATABASE (a scan for Toxeus creature records), not from a
   hand-typed list - a hardcoded list is exactly how the Endless Hunt got missed in the first place, by two
   parallel lanes that each owned half the roster. If you must pin an explicit allow-list for safety, derive
   it AND assert the derived set equals it, so a future new variant reds the build instead of being silently
   dropped.

2. THE GATE IS THE HARD PART. uber_apex_orb.verify() hardcodes exactly TWO champions, and
   negtest NEGATIVE 2 currently asserts that a THIRD record on genericbossorb_05 must FAIL as scope creep.
   That test now encodes the wrong invariant. Re-author it so it asserts the WHOLE ROSTER: every Toxeus
   variant present and on orb05, and nothing that is NOT a Toxeus variant on orb05. Weakening or deleting
   the test is a failure; the invariant it protects (no scope creep onto the apex tier) is still real, it
   just has a bigger legitimate roster now. Add new negatives covering the newly-added variants - at minimum
   one per added record, proving the gate fires if that record loses its orb.

3. THE ZZDEV PAIR. Verify placement in the shipped Levels.arc before deciding they are inert. Include them
   per Will's "all versions". Do NOT delete or retire them (RETIREMENT PROTOCOL - code-unreferenced is not
   proof of dead). Record what you found about their placement either way.

4. LEDGER + DOCS. Move R-99 to IMPLEMENTED with the measured result. Update the uber_apex_orb docstring,
   which currently describes a two-champion design and will otherwise become a lie (this repo has been burned
   twice by a stale comment that sent later lanes wrong). BACKLOG gate record. Tag the build (verify the tag
   is free; build62/65/66 are taken - say which you took).

PROVE IT, all against artifacts you build yourself:
- Full build, gates required, exit 0. Record the arz md5 and record count.
- Read every Toxeus record's treasureProxyName back OUT of the built arz and print the table.
- genericbossorb_04 byte-unchanged, and each of its 19 other consumers still pointing at it.
- Record-diff vs a baseline you build from main in the same environment: zero unattributed changes,
  0 REMOVED records (b98's 15 records and b99's summon_sargoth + pets must survive).
- The full negtest harness green, including your new subtests, with the count.
- R-48 still intact (champion souls at 100).

Return: status, commit_sha, done (PROVEN, with the proof), not_done (exhaustive - anything unfinished,
unproven, launch-gated or Will's call; a triaged item is NOT done), proofs (commands + outputs + md5s),
roster_table (the final measured record -> orb table).`,
    { label: `impl:r${round}`, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' }, roster_table: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs', 'roster_table'],
    } })

  if (!impl) {
    // A transient API error killed the implement agent. It commits as it goes, so its work is on
    // the branch - do NOT treat this as a finding, just re-run the round.
    log(`round ${round}: implement agent died (transient), retrying`)
    continue
  }

  phase('Vet')
  verdict = await agent(`INDEPENDENT ADVERSARIAL VET (round ${round}) of ${BR}.
${COMMON}

You are NOT the implementer and you do not trust them. This lane exists BECAUSE a roster was hardcoded and a
champion was silently missed - so your highest-value check is whether the same class of mistake survives.

THEY CLAIM:
STATUS: ${impl.status} | COMMIT: ${impl.commit_sha}
DONE: ${impl.done}
NOT DONE: ${impl.not_done}
ROSTER: ${impl.roster_table}
PROOFS: ${impl.proofs}

INDEPENDENTLY (build the arz yourself; accept no hash from any document):
1. ROSTER COMPLETENESS. Scan the database YOURSELF for every Toxeus creature record - do not use their
   scan. Is every one on genericbossorb_05? Did they miss one the way b94 missed the Endless Hunt? Is the
   roster genuinely DERIVED, or is it a hand-list wearing a derivation's clothes (i.e. would a NEW Toxeus
   variant added tomorrow be caught, or silently dropped)? Test that by adding one and seeing what happens.
2. NO SCOPE CREEP. Is anything that is NOT a Toxeus variant now on orb05? Is genericbossorb_04 byte-identical,
   and do all 19 of its other consumers still resolve to it? Any movement there is a HIGH finding - not
   raising other champions is the thing Will explicitly asked for.
3. THE GATE. Did they WEAKEN the harness to accommodate the bigger roster? Re-authoring NEGATIVE 2 to assert
   the whole roster is correct; deleting it, or replacing it with something that cannot fail, is a HIGH
   finding. Plant your own negatives - remove one variant's orb and confirm the build reds.
4. THE LOW-LEVEL VARIANT. Will explicitly overruled the balance objection. Confirm um_toxeus_21 really is on
   the FULL apex orb and was not quietly given a lesser tier "in the spirit of" the ruling. That would be
   substituting the implementer's judgement for Will's, which R-99 bans by name.
5. COLLATERAL. Record-diff vs your own baseline. 0 REMOVED records. Levels.arc and Quests.arc untouched.
   R-48 intact (champion souls still 100).
6. HONESTY. Compare DONE against what you can prove. Is the zzdev placement finding real or asserted? Is the
   stale two-champion docstring actually fixed everywhere, or only in the obvious place? Is every deferred
   item in the DEBT REGISTER?

Return verdict GO or NO-GO, issues (HIGH/MEDIUM/LOW, each with the command that shows it), and a summary
separating what you reproduced from what you took on trust.`,
    { label: `vet:r${round}`, phase: 'Vet', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } })

  if (!verdict) {
    verdict = { verdict: 'NO-GO', issues: ['VET AGENT DIED (transient API error), not a code finding - re-run the vet unchanged'], summary: 'vet agent failed to return' }
  }
  log(`round ${round}: ${verdict.verdict} (${verdict.issues.length} issues)`)
  if (verdict.verdict === 'GO') break
}

return {
  status: (verdict && verdict.verdict) === 'GO' ? 'go' : 'no-go',
  branch: BR,
  commit: impl && impl.commit_sha,
  roster: impl && impl.roster_table,
  done: impl && impl.done,
  not_done: impl && impl.not_done,
  proofs: impl && impl.proofs,
  vet: verdict && verdict.summary,
  open_issues: (verdict && verdict.issues) || [],
}
