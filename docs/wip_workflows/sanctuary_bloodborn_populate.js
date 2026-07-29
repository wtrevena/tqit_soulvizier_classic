export const meta = {
  name: 'sanctuary-bloodborn-populate',
  description: 'Sanctuary of the Bloodborn: large walkable areas have NO enemies placed, and the minimap does not render them. Recon, then populate to amgoz1 standard.',
  phases: [
    { title: 'Recon' },
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/sanctuary-populate'
const BR = 'feat/sanctuary-populate'

const COMMON = `
Repo: ${REPO}. Work ONLY in worktree ${WT} on branch ${BR}
(create if absent: git worktree add ${WT} -b ${BR} main   -- main tip is 4f0299c, which already contains
the b99 content wave AND the b98 endless-hunt lane; DO NOT branch from anything older).
Python: use the "py" launcher. Set PYTHONIOENCODING=utf-8 and PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 for builds.

READ FIRST, in this order, and obey them - they are law, not suggestions:
  ${REPO}/CLAUDE.md  (the 4 process laws: rulings ledger, RETIREMENT PROTOCOL, player-surface checklist,
                      no-new-surface-without-a-gate + debt register)
  ${REPO}/docs/WILL_RULINGS.md      (design law of record - append VERBATIM, same turn, never edit history)
  ${REPO}/docs/amgoz1_design_voice.md (the creative bar ALL content is held to)
  ${REPO}/docs/BACKLOG.md           (gate records + DEBT REGISTER - read before scheduling anything)

RULINGS DECADES ALREADY CLAIMED - do not collide: main holds up to R-80 (b99) and R-90..R-96 (b98);
feat/leinth-wave holds R-73..R-76; fix/green-diff up to R-71. Pick a FREE decade, prove it free against
main AND every in-flight branch with git grep before you write, and say which you took.

HARD CONSTRAINTS
- DO NOT DEPLOY. Write NOTHING to CustomMaps. The orchestrator owns every deploy and every Steam upload.
- DO NOT launch Titan Quest or Steam. DO NOT kill either.
- Levels+Quests are COUPLED (deploy together); arz+Text are COUPLED. If you change one of a pair, build both.
- COMMIT EVERY STEP. Will's machine can be throttled or interrupted at any moment; uncommitted work is lost
  work. Small, frequent, described commits on the branch. Tag the final build build66-dev (verify that tag
  is free first; if taken, take the next free one and say so).
- Never mutate shared git config (no core.* / user.* writes) - a linked worktree writes the SHARED .git/config
  and has corrupted both repos before.
- NO ESTIMATES in reports. Measured numbers with the command that produced them, or say "not measured".
`

phase('Recon')
const recon = await agent(`SANCTUARY OF THE BLOODBORN - RECON + DESIGN.
${COMMON}

WILL'S REPORT, verbatim: the Sanctuary of the Bloodborn has "large walkable areas with no enemies placed",
and "the minimap doesn't render them". He added that the minimap "isnt a huge issue" - so the EMPTY SPACE
is the priority and the minimap is secondary. Do not invert that.

ANSWER THESE FROM GROUND TRUTH (the built artifacts, not documents - every hash in every doc in this repo
has proven stale at least once):

1. WHAT IS THE SANCTUARY, physically? Identify every .lvl that composes it (name them), its walkable extent,
   and how a player enters and leaves. Use the repo's own level/blob readers under tools/ - do not invent a
   new parser if one exists. Read the CANONICAL Levels.arc the build produces, and state its md5.

2. WHERE EXACTLY IS THE EMPTY SPACE? Produce a MEASURED map of occupancy: for each level blob, the walkable
   area versus the placed-spawn coverage. Quantify it - "N square units of navmesh with zero proxy within R"
   beats "the north half is empty". Identify the specific regions Will would have walked through. If the
   emptiness is not reproducible from the data, say so plainly and stop rather than inventing a fix.

3. WHY is it empty? Distinguish these, they need different fixes: (a) nothing was ever placed there;
   (b) proxies are placed but resolve to nothing (empty pool, weight 0, a difficulty gate);
   (c) they resolve but the spawn budget starves them; (d) a merge dropped them. The b98 lane just proved
   that difficultyLimitsFile ONLY scales player level and NEVER filters whether a proxy resolves - do not
   reuse the refuted b91 reasoning.

4. WHAT SHOULD LIVE THERE? This is a content design question and it is held to the amgoz1 bar: the Sanctuary
   is the Bloodborn's own holy place. Monster-identity-driven, flavourful, coherent with what already spawns
   in the blood cave complex. NOT a generic trash sprinkle to fill area. Propose the population - families,
   density, champion policy, and how it escalates toward whatever the Sanctuary leads to. Cite the design
   voice doc. Prefer pools and proxies that already exist in this mod over minting new creatures.

5. DENSITY SAFETY. The b76 chumbi-freeze is the precedent: too many simultaneous entities freezes the game.
   State the worst-case simultaneous entity count your proposal creates in one screen, and compare it to
   both the b76 figure and to a comparable base-game area you actually measured.

6. THE MINIMAP. Diagnose it, but keep it scoped as secondary. This repo has already solved minimap rendering
   twice (b46 rounds 1-3: zone .dbr records + the SD region GUID binding). Read those reports and say whether
   the Sanctuary is the SAME defect or a different one. Do not re-derive what b46 already proved.

DELIVER a design section written into docs/reports/ BEFORE any implementation, and COMMIT it. Return:
- levels: the .lvl set + the Levels.arc md5 you measured against
- emptiness: the measured occupancy map + which of (a)-(d) it is, with the evidence
- population_plan: the amgoz1-grade proposal, concrete enough to implement
- density: worst-case simultaneous entities vs b76 and vs a measured base-game comparator
- minimap: same-as-b46 or different, with the mechanism
- open_questions: anything that is genuinely Will's call (content taste, difficulty), flagged as WILL_DECISION
- risks: what could break, especially navmesh (the b89 crash came from a malformed navmesh container)`,
  { label: 'recon', schema: {
    type: 'object',
    properties: {
      levels: { type: 'string' }, emptiness: { type: 'string' }, population_plan: { type: 'string' },
      density: { type: 'string' }, minimap: { type: 'string' },
      open_questions: { type: 'array', items: { type: 'string' } },
      risks: { type: 'array', items: { type: 'string' } },
      commit_sha: { type: 'string' },
    },
    required: ['levels', 'emptiness', 'population_plan', 'density', 'minimap', 'open_questions', 'risks', 'commit_sha'],
  } })

log('recon done - ' + String(recon && recon.emptiness || '').slice(0, 160))

let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  phase('Implement')
  impl = await agent(`SANCTUARY OF THE BLOODBORN - IMPLEMENT (round ${round}).
${COMMON}

THE DESIGN PASS RETURNED:
LEVELS: ${recon.levels}
EMPTINESS: ${recon.emptiness}
POPULATION PLAN: ${recon.population_plan}
DENSITY: ${recon.density}
MINIMAP: ${recon.minimap}
OPEN QUESTIONS: ${JSON.stringify(recon.open_questions)}
RISKS: ${JSON.stringify(recon.risks)}
${round > 1 ? `\nTHE INDEPENDENT VET RETURNED **${verdict.verdict}** AND YOU MUST CLEAR EVERY ISSUE:\n${JSON.stringify(verdict.issues, null, 1)}\nDo not argue with a finding by restating your earlier claim - re-measure it. If a finding is genuinely WRONG, prove it wrong with a command and its output, and say so; that is a legitimate outcome.` : ''}

Treat the design as a proposal, not as truth. If implementing it exposes the design as wrong, fix the design,
say so explicitly in the report, and implement what is actually correct.

IMPLEMENT:
- The population, via the repo's established mechanism (registry module under tools/patches/ for DB-side work,
  build_section_surgery.py INJECT_SPECS for map-side placement). Registry ORDER IS SEMANTIC - later means
  later writer. Justify where you insert.
- Every new player-visible surface needs a GATE (process law #4) and an entry in the DEBT REGISTER if anything
  is deferred. A new gate needs PLANTED NEGATIVE TESTS that prove it actually fails when the invariant breaks.
- The minimap fix ONLY if it is genuinely the b46 mechanism and cheap. If it is a different and expensive
  defect, file it as debt with the mechanism you found and move on - Will said it is not the priority.
- Append the ruling(s) to docs/WILL_RULINGS.md VERBATIM in your chosen free decade, same turn as the code.
- Update docs/BACKLOG.md with a gate record for the build.

VERIFY BEFORE YOU CLAIM ANYTHING:
- Full build with gates required. Record the arz/Text/Levels/Quests md5s you actually produced.
- Record-diff against a real baseline built from main 4f0299c in the SAME environment - not against a
  document's hash. ZERO unattributed record or field changes; attribute every one to a named change.
- Navmesh identity: if you touched a .lvl, PROVE the navmesh container is unchanged or correctly formed.
  The b89 crash was a 148-byte stub navmesh that made the engine read into adjacent heap. This is the single
  most dangerous thing this lane can break.
- Contracts + validate_tags + registry verifies, all green, with the numbers.
- Dry-run the map injection into COPIES and blob-diff, before touching anything real.

Return: status, commit_sha, done (what is genuinely finished and PROVEN, with the proof),
not_done (everything unfinished, unproven, launch-gated, or Will's call - be exhaustive; a triaged item is
NOT a done item), proofs (commands + measured outputs + every md5).`,
    { label: `impl:r${round}`, schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs'],
    } })

  phase('Vet')
  verdict = await agent(`INDEPENDENT ADVERSARIAL VET (round ${round}) of ${BR}.
${COMMON}

You are NOT the implementer and you do not trust the implementer. Your job is to try to BREAK this work and
to catch anything it got wrong, overstated, or quietly skipped. A clean GO that misses a real defect is a
worse outcome than a NO-GO that is slightly too harsh.

THE IMPLEMENTER CLAIMS:
STATUS: ${impl.status}
COMMIT: ${impl.commit_sha}
DONE: ${impl.done}
NOT DONE: ${impl.not_done}
PROOFS: ${impl.proofs}

VERIFY INDEPENDENTLY - rebuild it yourself, do not replay their commands and do not accept a hash from a
document (every hash in this repo has been stale at some point):
1. Does it actually do what Will asked? The Sanctuary should no longer read as large empty walkable space.
   Judge that from the DATA (occupancy after the change, measured the way the recon measured it before).
2. NAVMESH SAFETY. If any .lvl changed, verify the navmesh container is well-formed and, where it should be
   untouched, byte-identical. The b89 blood-cave crash was exactly this class of bug and it made the game
   unplayable. Be paranoid here.
3. DENSITY. Re-derive the worst-case simultaneous entity count yourself. Does it approach the b76 freeze?
4. COLLATERAL. Record-diff and blob-diff against a baseline you build yourself from main 4f0299c. Anything
   outside the intended scope is a finding. Confirm it does NOT revert b99 or b98 (0 REMOVED records is the
   load-bearing number - check that b98's 15 new records and b99's summon_sargoth + pets survive).
5. GATES. Do the new gates actually fail when the invariant is broken? Plant the negative yourself.
6. AMGOZ1 BAR. Is the content monster-identity-driven and flavourful, or is it generic filler dressed up in
   good prose? Say so bluntly. Quote the design voice doc.
7. HONESTY AUDIT. Compare DONE against what you can actually prove. Anything claimed but unproven, or
   anything done but not disclosed, is a finding. Is every deferred item really in the DEBT REGISTER?
8. RULINGS. Is the decade genuinely free? Are the rulings verbatim? Did it silently overturn an existing one?

Return verdict GO or NO-GO, issues (each tagged HIGH / MEDIUM / LOW with the evidence and the command that
shows it), and a summary that states what you independently reproduced versus what you took on trust.`,
    { label: `vet:r${round}`, schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } })

  log(`round ${round}: ${verdict.verdict} (${verdict.issues.length} issues)`)
  if (verdict.verdict === 'GO') break
}

return {
  status: verdict.verdict === 'GO' ? 'go' : 'no-go',
  branch: BR,
  commit: impl.commit_sha,
  recon: { emptiness: recon.emptiness, plan: recon.population_plan, minimap: recon.minimap },
  done: impl.done,
  not_done: impl.not_done,
  proofs: impl.proofs,
  vet: verdict.summary,
  open_issues: verdict.issues,
  will_decisions: recon.open_questions,
}
