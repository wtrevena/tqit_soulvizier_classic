export const meta = {
  name: 'r100-batch-implementation-wave',
  description: "BUILD Will's 19-item play batch (R-100) plus R-101/102/103/105/106/107 and the new tombstone-XP coupling. Implementation, not more analysis.",
  phases: [
    { title: 'Build' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'

const LAW = `
Repo: ${REPO}. main is at 7efd107 and ALREADY carries b93/b94/b95/b96/b97/b98, blade-mastery and R-99.
Python: the "py" launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1.

READ FIRST, and obey - law, not suggestion:
  ${REPO}/CLAUDE.md                 (4 process laws)
  ${REPO}/docs/WILL_RULINGS.md      -> **R-100 through R-107 are the spec for this whole wave.** Every item
                                     below is already MEASURED there with record paths and numbers. Do not
                                     re-derive what is already measured; go and BUILD it.
  ${REPO}/docs/BACKLOG.md           (gate records + DEBT REGISTER)
  ${REPO}/docs/amgoz1_design_voice.md if present; if ABSENT say so and reconstruct the bar from shipped SV content.

WHY THIS WAVE EXISTS: Will gave a 19-item list from a play session and, a day later, none of it was built -
the session produced rulings and probes instead of code. **This wave is implementation. A report that
re-measures what R-100..R-107 already measured is a FAILED lane.**

HARD CONSTRAINTS
- Work ONLY in your own worktree on your own branch, both named in your task.
- DO NOT DEPLOY, do not write to CustomMaps, do not launch or kill TQ/Steam. The orchestrator owns deploys.
- arz+Text are COUPLED; Levels+Quests are COUPLED.
- COMMIT EVERY STEP. Small, frequent, described commits.
- Never mutate shared git config from a linked worktree.
- NO ESTIMATES: measured values with the command that produced them, or "not measured".
- Every new player-visible surface needs a GATE with PLANTED NEGATIVES that actually fire.
- RETIREMENT PROTOCOL: never delete/blank/rename a record to "fix" something.
- SHARED-RECORD LAW (learned the hard way twice): before editing ANY shared record, enumerate its carriers.
  If a non-target carrier exists, CLONE and repoint instead of editing in place. This already bit us on
  genericbossorb_04 (21 consumers) and on toxeus_passiveproperties (18 carriers, 9 of them Will's own PETS).
`

const LANES = [
  {
    key: 'p0-quest-leaks',
    branch: 'fix/quest-item-leaks',
    title: 'P0: farmable quest items + frozen thrown-weapon monsters',
    body: `TWO P0 DEFECTS. Both are shipped bugs in Will's live game.

**(1) R-101 - quest items are farmable off our uber clones.** Already swept to a CLOSED SET of 3:
  - \`um_charonform2_ferryman_99\` -> \`xsq12_charonsoar.dbr\` (Charon's Oar)
  - \`um_polisgaoler_99\` -> \`z_wardenofsoulskey.dbr\` (Key of the Warden of Souls)
  - \`um_polisgaoler_unbound_99\` -> \`z_wardenofsoulskey.dbr\`
Clear \`perPartyMemberDropItemName\` (and any matching chance field) on those 3. **The DONORS
(\`boss_charonform2_39/41/43\`, \`testcharon01\`, \`xsecrethero_wardenofsouls_48\`) MUST stay byte-identical or
the real quests break - that is the whole risk, prove it.** GATE: no \`um_*\` record may carry a per-party drop
resolving to \`itemClassification == Quest\`; state it as a roster invariant, not 3 named exceptions. Negatives
both ways (re-add each -> red; a NON-quest per-party drop -> still green, the field itself is legitimate).

**(2) R-100 #15 - every restored thrown-object monster is FROZEN.** Will: they "spawn and they cant move or
attack or anything they are broken". Owner is \`tools/patches/thrown_wielders.py\`. Multiple past tasks claimed
this rig was proven on 3 families (maenad / duneraider / tigerman) and re-verified; it ships broken anyway, so
**treat those claims as worthless and re-derive from the engine.** Find why a thrown wielder cannot act: the
likeliest class is an animation/rig mismatch (the same class as b98's spear anims and b94's uncastable acid
rig - a skill or attack naming an anm the creature's table does not bind). Enumerate EVERY monster the module
touches, prove for each that its attack/move animations resolve on its actual mesh, and fix the rig rather
than the symptom. If a family cannot be made to work, say so and disable that family rather than shipping a
statue. GATE: every thrown wielder's referenced anms resolve; planted negative on a broken binding.`,
  },
  {
    key: 'devourer-kit',
    branch: 'feat/devourer-kit',
    title: 'Devourer + Hunt: reflect/pierce retune, Bloodbath, Blood Frenzy, summons',
    body: `Will is HARD-BLOCKED: he cannot kill the Devourer at all, and one-shots himself hitting him.

**(a) R-103/R-107 the retune. \`toxeus_passiveproperties\` has 18 carriers and NINE ARE WILL'S OWN PETS**
(\`pets\\toxeus_enslaver_{1,2,3}\`, \`pets\\bloodtoxeus_{1,2,3}\`, \`pets\\toxeus_eoat_{1,2,3}\`), plus
\`drxcreatures\\crowheroes\\less.dbr\` which is not ours. **So you MUST clone a monster-only passive** and
repoint only the 6 Toxeus MONSTERS; pets and \`less.dbr\` keep the original 100/33. Editing in place would nerf
the very pets he is fighting with.
  - \`defensiveReflect\` 100.0 -> **30.0** (keep \`defensiveReflectChance\` at 33.0)
  - \`um_bloodtoxeus_99.defensivePierce\` 70 -> **40** (he plays a SPEAR build; 70% is a near-immunity and it is
    why his pets cannot finish it either)
  Both behind NAMED CONSTANTS with a comment citing R-103/R-107 so Will can retune in one line. Leave
  \`characterLife\` ALONE - it is the reserve lever.
**(b) R-100 #1 Bloodbath** from the Erebenea the Bloodletter soul onto the Devourer, cooldown 45s -> **15s**.
**(c) R-100 #12 Blood Frenzy** (low-health trigger) onto the Devourer - pattern is the Chief Bullfrog Quak soul
(\`quak_bloodfrenzy\`, which the Devourer already carries a variant of - check before adding a duplicate).
**(d) R-100 #13 summonable minions** for the Devourer AND the Endless Hunt, patterned on the Enslaver's
\`svc_enslaver_summonmarauders\`. Held to the amgoz1 bar: each champion's minions must suit HIM, not be a
recolour of the marauders. Respect the b76 chumbi-freeze density precedent and state worst-case simultaneous
entity count.
Will ruled: "harder is the point, keep all three" and "the answer is not cutting skills but cutting elsewhere" -
so (b),(c),(d) are ADDITIVE and must not be trimmed for balance.
GATE: monster passive carries 30/33 and NO pet record is on it; the 3 new abilities are castable (bind and
prove every anm, the b94 lesson); planted negatives.`,
  },
  {
    key: 'green-mesh',
    branch: 'fix/green-mesh-swap',
    title: 'R-102: kill the green by replacing RevenantPoison.msh',
    body: `**ROOT CAUSE IS ALREADY PROVEN BY ELIMINATION - do not re-investigate, implement.** The marauder demons
carry the IDENTICAL smoke FX pak and show no green; the green tracks the MESH:
\`Creatures\\Monster\\Skeleton\\RevenantPoison.msh\`. Will confirmed the Devourer (same mesh, DIFFERENT crimson
texture) glowed too, so the texture is exonerated and a texture-only fix will NOT work.

SCOPE: the Enslaver MONSTER + all three \`pets\\toxeus_enslaver_{1,2,3}\` tiers + \`um_bloodtoxeus_99\` + the
Devourer's pet tiers. \`ShadowStalker.msh\` is proven green-free in the exact scene Will screenshotted and is
what his own demons wear. **BUT R-93 requires the Enslaver and Devourer to STOP sharing a mesh** - so pick a
DISTINCT clean mesh per champion, or you fix the green and break R-93 in the same commit.

⚠️ **THE RISK IS ANIMATION, NOT COLOUR.** A mesh swap re-rigs everything: every skill that names an anm must
still resolve or the champion T-poses or goes uncastable. Prove every referenced anm resolves on the NEW mesh
BEFORE claiming the fix, using the marauder's own rig as the reference implementation. If a chosen mesh cannot
carry his kit, choose another and say why.

ALSO IN SCOPE (R-102 second amendment): b98 wired \`svc_enslaver_shroud\` to the MONSTER ONLY - all three pet
tiers never got it, which is why Will says the shroud "is still not implemented". Wire it to the pets too, and
gate it roster-derived over {monster} + {every pet tier} so a future tier cannot be skipped.
GATE: no Toxeus champion or pet on RevenantPoison.msh; every anm resolves; planted negatives.`,
  },
  {
    key: 'map-placement',
    branch: 'fix/uber-placement',
    title: 'R-100 #8/#9/#10/#14/#16/#16b: placement, chests, and the walking-path law',
    body: `MAP + LOOT lane. All measured in R-100.

**(1) #8 Tantalus is OUTSIDE the Den of Tantalus**, in front of it. A past task claims to have placed him
inside and is marked completed, so **find out why it did not hold** before re-placing - a fix that regresses
the same way is not a fix.
**(2) #9 Tantalus has 3 chests, all "Tantalus Hoard", should have 1. (3) #10 Soul of the Unferried also has 3.**
Likely both root in the earlier "3 majestic chests per boss" decision - scope it rather than special-casing.
**(4) #14 the Lower City of Lost Souls uber guards NO chest and his orb is trash** - give him a chest and
consider the R-99 apex tier.
**(5) #16 the machine uber "Destroyer of Cities" drops no chest AND stands in the main walking path.**
**(6) #16b NEW STANDING RULE: the main walking path is NEVER an appropriate place for an uber monster we
place. AUDIT EVERY EXISTING PLACEMENT**, not just this one, and report the full list even where you change
nothing.
⚠️ NAVMESH SAFETY IS THE DANGER HERE: the b89 blood-cave crash was a malformed navmesh container that made the
game unplayable. If you touch a .lvl, PROVE the navmesh container is well-formed or byte-identical. Dry-run
every injection into COPIES and blob-diff before touching anything real.
GATE: every placed uber inside its intended area and off the main path; chest counts per boss ruled; negatives.`,
  },
  {
    key: 'soul-economy',
    branch: 'feat/soul-economy',
    title: 'R-105/R-106 soul rates + R-100 #11 forge classification + #17 Gaoler',
    body: `**(1) R-105/R-106 RATE SWEEP, all ratified.** Derive every target from \`monsterClassification\`, NEVER from
the record name or folder (the mummy priests classify Common despite a boss-ish filename - that is exactly why).
  - all **66%** (373) and **50%** (361) carriers -> **33%**  [734 creatures]
  - the **15 Common** carriers with any chance (6 swift archers @0.5, 4 carrion crows + 5 mummy priests @0.3) -> **0%**
  - fixed-location bosses stay **25%**; the 12 \`boss_pharaohshonorguard*\` @10% -> **25%**
  - the four Toxeus champions stay **100%** (R-48) - do not touch
  - \`um_polisgaoler_unbound_99\` 66% -> 25%; \`um_polisgaoler_99\` STAYS AT 0 (Will: only the unbound final
    version drops)
  - \`um_charon_ferryman_99\` and \`um_tantalus_99\` are Boss-class at 0% -> **25%** (they carry souls that can
    never drop)
  - **HELD, do NOT touch: the 172 Champion-tier carriers at 0%.** Will has not answered whether the star tier
    qualifies. Leave them and say so.
  Use the ONE shared classifier - a past vet caught drifted duplicate logic in this exact area.
**(2) R-100 #11 - forge formulas for XP potions require souls from a specific ACT, and our minted souls lack
the act classification**, so they cannot be used. Find the field the base game's formulas key on, and set it
correctly for every soul we minted. This is a real player-facing block on a whole crafting path.
**(3) R-100 #17 Soul Gaoler:** halve his chest count (round down), and fix his EPIC chests dropping Normal-tier
"essence of..." instead of Epic-tier "embodiment of..." - a difficulty-tier mis-wire in his loot chain.
GATE: every cohort on its ruled rate, no Common above 0, champions still 100, planted negatives both ways.`,
  },
  {
    key: 'visibility',
    branch: 'feat/uber-visibility',
    title: 'R-100 #7 exclamation marks + #18 Guardians of the General + tombstone XP',
    body: `**(1) #7 - exclamation mark over the head of EVERY uber boss we made, EXCEPT the Devourer** (he sits on a
hidden chest and must stay hard to find). The Endless Hunt already has one - copy that mechanism. The existing
rig is \`tools/patches/uber_quest_markers.py\`; extend it roster-derived rather than hand-listing, so a future
uber gets a marker automatically.
**(2) #18 - the Guardians of the General are indistinguishable from trash.** Will: "super weak and they dont
have any chests and dont drop any orbs or anything... they are small and they look just like the other guys
and i killed them so fast... not big with no special skills or anything to make them even noticeable besides
their red names". They must READ as uber: size, a kit worth noticing, chests, orbs. Held to the amgoz1 bar -
monster-identity-driven, not a stat multiplier. Mind the b76 density precedent if you add summons.
**(3) NEW - TOMBSTONE XP COUPLING (Will, 2026-07-30, verbatim):**
> "one thing we need to check is when you go find your tombstone after you die, you should only get 10% of the
> original xp that is awarded since we cut the death penalty"
b93 cut \`deathPenaltyEquation\` by 90% (and \`deathPenaltyMax\` 500000 -> 50000). **If the death-marker recovery
still returns the ORIGINAL amount, recovering it now GRANTS MORE XP THAN THE DEATH COST - a free-XP exploit we
introduced.** Find the field/equation that governs what the tombstone returns, measure what it currently pays
against what b93 now takes, and **SUPERSEDED BY R-109 - build the EQUALITY, not the 10%:** Will refined it to *"lets make the tombstone xp
recovery match the xp lost upon dying"*. So \`recovered == lost\`, EXACTLY, on every difficulty. Express the
recovery in terms of the penalty so the two cannot drift when the penalty is retuned again; if the engine
will not take a derived expression, mirror the penalty equation verbatim and gate on them being equal.
**Report the measured before/after BOTH ways (XP lost vs XP recoverable) at several levels on all three
difficulties.** GATE: equality - plant negatives on BOTH sides, recovery above the penalty must red the
build and recovery below it must red the build too (paying back less would punish the player twice).`,
  },
]

phase('Build')
const results = await pipeline(
  LANES,
  (lane) => agent(`${lane.title.toUpperCase()}
${LAW}

Worktree: ${REPO}/.claude/worktrees/${lane.key}   Branch: ${lane.branch}
(create: git worktree add ${REPO}/.claude/worktrees/${lane.key} -b ${lane.branch} main)

${lane.body}

Append any ruling you rely on or amend to docs/WILL_RULINGS.md VERBATIM in a decade you prove free with
git grep against main AND every in-flight branch. Add a BACKLOG gate record. Build, run the gates, and
record-diff against a baseline YOU build from main in the same environment: ZERO unattributed changes and
0 REMOVED records.

Return: status, commit_sha, done (PROVEN, with the proof), not_done (EXHAUSTIVE - anything unfinished,
unproven, launch-gated or Will's call; a triaged item is NOT a done item), proofs (commands + outputs + md5s).`,
    { label: `build:${lane.key}`, phase: 'Build', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs'],
    } }),
  (built, lane) => agent(`INDEPENDENT ADVERSARIAL VET of ${lane.branch} (${lane.title}).
${LAW}

Worktree ${REPO}/.claude/worktrees/${lane.key}, branch ${lane.branch}.

THE IMPLEMENTER CLAIMS:
STATUS: ${built && built.status} | COMMIT: ${built && built.commit_sha}
DONE: ${built && built.done}
NOT DONE: ${built && built.not_done}
PROOFS: ${built && built.proofs}

You are NOT the implementer and you do not trust them. Build the artifacts yourself; accept no hash from any
document. Check, in priority order:
1. **Does it actually do what Will asked?** Judge from the built bytes, not the report. Quote his words.
2. **SHARED-RECORD DAMAGE.** Did an edit to a shared record hit a non-target carrier? This has bitten twice
   (genericbossorb_04's 21 consumers; toxeus_passiveproperties' 9 pet carriers). Enumerate carriers yourself.
3. **ANIMATION/RIG.** For any mesh, weapon or new-skill work: does every referenced anm actually resolve? An
   unbindable anm ships a T-posing or uncastable monster and has slipped through twice.
4. **NAVMESH.** For any .lvl change: well-formed or byte-identical. The b89 crash made the game unplayable.
5. **COLLATERAL.** Record-diff vs your own baseline; 0 REMOVED; Levels/Quests untouched unless the lane owns them.
6. **GATES.** Plant the negatives yourself and confirm they fire. A gate that cannot fail is not a gate.
7. **HONESTY.** Compare DONE against what you can prove. Anything asserted-but-unproven, or done-but-undisclosed,
   is a finding. Is every deferred item in the DEBT REGISTER?

Return verdict GO or NO-GO, issues (HIGH/MEDIUM/LOW, each with the command that shows it), and a summary
separating what you reproduced from what you took on trust.`,
    { label: `vet:${lane.key}`, phase: 'Vet', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } }),
)

const out = LANES.map((lane, i) => ({
  lane: lane.key,
  branch: lane.branch,
  title: lane.title,
  verdict: (results[i] && results[i].verdict) || 'DIED',
  issues: (results[i] && results[i].issues) || [],
  summary: (results[i] && results[i].summary) || 'lane produced no result',
}))
log('wave complete: ' + out.map(o => `${o.lane}=${o.verdict}`).join(' '))
return { lanes: out }
