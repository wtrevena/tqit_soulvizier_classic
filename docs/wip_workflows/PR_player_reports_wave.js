export const meta = {
  name: 'steam-player-reports-wave',
  description: "Investigate + address the 5 Steam player reports (invisible-on-death, maenad ranged frozen, dyes grey, Gorgon names swapped, Sparta Crypt portal). Investigate from shipped bytes, fix or honestly diagnose, adversarial vet each.",
  phases: [
    { title: 'Investigate' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'

const LAW = [
  'Repo: ' + REPO + '. main is the current tip and ALREADY contains the whole R-108 wave that went LIVE on Steam',
  '2026-08-06 (item 3759792705). The shipped DB build is arz md5 adc7ee4afbae54dfd883a3c52ddbcf51.',
  'Python: the py launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1.',
  '',
  'READ FIRST and obey (law, not suggestion):',
  '  ' + REPO + '/CLAUDE.md (4 process laws)',
  '  ' + REPO + '/docs/WILL_RULINGS.md (design law of record; append VERBATIM same-turn, pick a FREE ruling decade and prove it free with git grep)',
  '  ' + REPO + '/docs/BACKLOG.md (the 5 reports are captured there as PR-1..PR-5; gate records + DEBT REGISTER)',
  '  ' + REPO + '/docs/MODDING_PLAYBOOK.md if present (engine/world/navmesh knowledge)',
  '',
  'THESE ARE REAL PLAYER REPORTS from Steam, both dated BEFORE the wave went live, so each must be triaged',
  'against the CURRENT built artifacts, not documents. Every hash in every doc has been stale at least once -',
  'build the arz/map yourself and read the bytes.',
  '',
  'HONEST OUTCOMES (an investigation lane is NOT required to ship a code change):',
  '  - FIXED: you found the cause in our data and fixed it, proven from a rebuild.',
  '  - ALREADY-FIXED: the live build already resolves it; PROVE it from the shipped bytes, change nothing.',
  '  - NEEDS-WILL: it is a genuine design/taste call; state it precisely with a recommendation.',
  '  - DIAGNOSED-NOT-FIXABLE: the cause is outside our data (engine/hardware/base-game); give the precise',
  '    mechanism + a repro hypothesis + recommendation. DO NOT fabricate a fix. A confident wrong fix is worse',
  '    than an honest diagnosis.',
  '',
  'HARD CONSTRAINTS',
  '- Work ONLY in your own worktree on your own branch, both named in your task.',
  '- DO NOT DEPLOY, do not write to CustomMaps, do not launch or kill TQ/Steam. The orchestrator owns deploys.',
  '- arz+Text are COUPLED; Levels+Quests are COUPLED. Touch a .lvl only with extreme care - the b89 blood-cave',
  '  crash was a malformed navmesh container; prove any navmesh you touch is well-formed or byte-identical.',
  '- COMMIT EVERY STEP. Never mutate shared git config from a linked worktree. NO ESTIMATES.',
  '- RETIREMENT PROTOCOL: never delete/blank/rename a record to fix something without checking design intent.',
  '- SHARED-RECORD LAW: before editing ANY shared record, enumerate its carriers; if a non-target carrier',
  '  exists, CLONE and repoint instead of editing in place (this bit us on genericbossorb_04 and toxeus_passiveproperties).',
  '- If you add a player-visible surface or a new invariant, ship a GATE with PLANTED NEGATIVES that fire.',
].join('\n')

const LANES = [
  {
    key: 'invisible-on-death',
    branch: 'fix/pr1-invisible-on-death',
    title: 'PR-1: player character goes INVISIBLE on death/respawn',
    body: [
      'Player fleurydid (French): "quand je meurt tombe invisible" - when I die I become invisible. He was on the',
      'PRE-wave build, so this is a PRE-EXISTING bug, NOT caused by the R-108 wave. Do not assume the wave broke it.',
      '',
      'INVESTIGATE from the engine + our data, in rough priority order:',
      '1. What happens visually on death/respawn in TQAE: the character model, the rebirth-fountain respawn, ragdoll,',
      '   any dissolve/ambush texture. Look for a player-character or PC-mesh/animation record that could fail to',
      '   re-render after respawn. Note: base TQAE does NOT normally do this, so something in the SV/DRX/our merge is',
      '   the suspect.',
      '2. Does anything in the SHIPPED arz touch the player character record(s), PC animation table, or a death/',
      '   revive skill? Enumerate what our build changes vs base for PC-side records.',
      '3. Consider the mundane causes before the exotic: a dissolve/ambushDissolve texture that never restores alpha,',
      '   a mesh swap, an FX that hides the model, or a mastery/skill the player had active. fleurydid did not name',
      '   his class - that is a real gap; if the cause is class-specific, say which class reproduces it.',
      '4. Distinguish OUR-data cause vs engine/LAA/base-game cause. The mod ships LAA instructions; memory pressure',
      '   can cause render glitches. If it is not in our data, say so with evidence rather than inventing a fix.',
      '',
      'If you find an in-data cause, fix it (clone-and-repoint if shared) and prove the fix from a rebuild + a gate',
      'if a new invariant is warranted. If not, deliver a precise DIAGNOSED-NOT-FIXABLE with a repro hypothesis and',
      'the one question to put to Will/fleurydid (e.g. which class, every death or once, does reload restore the model).',
    ].join('\n'),
  },
  {
    key: 'maenad-ranged',
    branch: 'fix/pr3-maenad-ranged',
    title: 'PR-3: maenads with ranged weapons frozen (arms spread, not firing)',
    body: [
      'Player Flozer44 @ Knossos lvl 22: "Maenads equipped with ranged weapons aren\'t firing; they just stand',
      'motionless with their arms spread wide." Arms-spread-motionless is the classic broken-animation pose.',
      '',
      'THE OPEN QUESTION: the R-108 wave fixed the FROZEN THROWN-WEAPON monsters via tools/patches/thrown_anim_rig.py,',
      'and the maenad family IS in that roster. BUT Flozer said "ranged weapons" which could mean BOWS, not thrown.',
      'A bow-wielding maenad frozen would be a DIFFERENT, still-open bug the thrown fix does NOT cover.',
      '',
      'DO, from the SHIPPED build (build the arz yourself):',
      '1. Enumerate every maenad creature the player meets around Knossos/Greece that carries a ranged weapon.',
      '   For each: its charAnimationTableName, its equipped-weapon class (bow / thrown / rangedOneHand), and whether',
      '   its attack/move/ranged animations RESOLVE on its actual rig (the exact class of check thrown_anim_rig and',
      '   the b98/b94 anim work used).',
      '2. Determine which maenads thrown_anim_rig ALREADY covers and prove they now animate (ALREADY-FIXED), and',
      '   whether any BOW-wielding or otherwise-uncovered maenad is STILL frozen (a real gap to FIX).',
      '3. If there is a still-frozen maenad, fix its rig the same proven way (clone the anim table + restore the',
      '   missing stance clips, or blank an unbindable skillSpecialAnimationName - the b42/b94 recipe; CLONE, never',
      '   edit a shared table in place). Extend the castability/anim gate to cover it and plant a negative.',
      '4. If ALL ranged maenads are already covered, deliver ALREADY-FIXED with the per-maenad proof table, so Will',
      '   can tell Flozer it is resolved in the live build.',
    ].join('\n'),
  },
  {
    key: 'dyes-grey',
    branch: 'fix/pr2-dyes-grey',
    title: 'PR-2: Merchants Gardens dyes do not apply, character turns grey',
    body: [
      'Player Flozer44: "I can\'t seem to apply the special dyes purchased from the merchants in the Merchants\'',
      'Gardens (it gives my character a grey look)." The Merchants\' Gardens = the restored SV "Garden of Merchants"',
      'area (portal at the Hidden Valley camp).',
      '',
      'INVESTIGATE from the shipped arz:',
      '1. Find what the Garden-of-Merchants merchant(s) actually SELL that the player calls a "dye". TQAE has no',
      '   native dye system, so this is an SV/mod cosmetic item (a relic/charm/consumable that recolours the PC).',
      '   Identify the exact item record(s) and their merchant loot/sell table.',
      '2. Determine WHY applying it produces a grey character. Prime suspects: the item references a texture/skin',
      '   that does not resolve in our shipped arcs (missing .tex -> engine falls back to a flat grey material), or',
      '   a colour/tint field that is zeroed/null, or a PC-reskin record whose baseTexture path is broken. Resolve',
      '   every asset the dye references against the SHIPPED .arc set and report which one is missing/broken.',
      '3. Fix the broken reference if it is in our data (repoint to the correct shipped texture, or restore the',
      '   missing asset to the correct arc), and prove the reference resolves after rebuild. If the intended asset',
      '   simply is not present in any upstream we ship, say so and recommend (drop the item from the merchant, or',
      '   source the texture) - a NEEDS-WILL with the specific options.',
    ].join('\n'),
  },
  {
    key: 'gorgon-names',
    branch: 'fix/pr4-gorgon-names',
    title: 'PR-4: Gorgon names swapped (Impious and Geomancy Adept)',
    body: [
      'Player Flozer44: "The Gorgon names are swapped (\'Impious\' and \'Geomancy Adept\')." Two Gorgon-family',
      'creatures carry each other\'s display name.',
      '',
      'DO, from the shipped arz + Text.arc:',
      '1. Find the two Gorgon creature records whose descriptionTag / name resolves (via Text.arc) to "Impious" and',
      '   "Geomancy Adept". Confirm the swap: the creature that should be "Impious" shows "Geomancy Adept" and vice',
      '   versa. Establish the CORRECT mapping from upstream SV / base data or from the creatures\' own kit (a',
      '   geomancer casts earth; "Impious" is a different archetype) - do not guess which is which; derive it.',
      '2. Fix the swap. Prefer the smallest correct change: if a creature record points at the wrong name TAG, repoint',
      '   the tag on the record; if the TWO TAGS themselves hold swapped strings in our text build, correct the text.',
      '   State which mechanism it is and why. arz+Text are coupled - if you touch a tag, rebuild both.',
      '3. This is text/data only - a gate is optional, but validate_tags must pass and both names must resolve',
      '   correctly in the rebuilt Text.arc (read them back out).',
    ].join('\n'),
  },
  {
    key: 'sparta-portal',
    branch: 'fix/pr5-sparta-portal',
    title: 'PR-5: Depths of the Spartan Crypt portal unfindable',
    body: [
      'Player Flozer44 searched hours and cannot find the secret portal to the "Depths of the Spartan Crypt" in the',
      'Athens catacombs. Related PRIOR analysis lives on the UNMERGED branch fix/athens-catacomb-traveler (tip',
      '9dc5b09), whose RCA says "Sparta traveler survived the port + responds; Crypt L2 unreachable by design."',
      'CLAUDE.md records this entrance was an INVENTED door (build25): "a brand new entrance; the original never had one."',
      '',
      'DO, from the SHIPPED map (build/read the canonical Levels.arc the pipeline produces, state its md5):',
      '1. Ground-truth whether the Sparta Crypt entrance / portal to the deeper level is actually PRESENT and',
      '   REACHABLE in the shipped map. Read the branch RCA first, then VERIFY it against the shipped bytes - do not',
      '   trust the doc. Is there a portal/door object placed, does it target a real walkable point, and can the',
      '   player physically reach it (navmesh reachability, the b89-class concern)?',
      '2. Classify: (a) present + reachable but genuinely hard to find (then the fix is a WILL_TEST_GUIDE / description',
      '   hint, or a more visible marker, NOT a map change); (b) present but UNREACHABLE (the RCA\'s "Crypt L2',
      '   unreachable by design") - then decide with evidence whether to make it reachable, and if so how, proving the',
      '   navmesh stays valid; (c) absent/regressed - then it is a real content gap.',
      '3. Only change the map if you can PROVE the navmesh container stays well-formed (dry-run into copies, blob-diff,',
      '   navmesh identity/validity). If the safe answer is a documentation/marker fix rather than a map edit, do that',
      '   and say why. If it needs a real map lane with in-game verification, deliver a precise NEEDS-WILL / debt entry',
      '   with the exact placement spec rather than a risky blind edit.',
    ].join('\n'),
  },
]

phase('Investigate')
const results = await pipeline(
  LANES,
  (lane) => agent(
    lane.title.toUpperCase() + '\n' + LAW + '\n\n'
    + 'Worktree: ' + REPO + '/.claude/worktrees/' + lane.key + '   Branch: ' + lane.branch + '\n'
    + '(create: git worktree add ' + REPO + '/.claude/worktrees/' + lane.key + ' -b ' + lane.branch + ' main)\n\n'
    + lane.body + '\n\n'
    + 'If you make a code change: full build with gates, record the arz/Text/map md5s you produced, record-diff vs a '
    + 'baseline you build from main in the same environment (ZERO unattributed changes, 0 REMOVED records), and run '
    + 'the relevant gates. Append any ruling VERBATIM to docs/WILL_RULINGS.md in a free decade; add a BACKLOG note '
    + 'updating the PR item. \n\n'
    + 'Return: outcome (one of FIXED / ALREADY-FIXED / NEEDS-WILL / DIAGNOSED-NOT-FIXABLE), status, commit_sha, '
    + 'done (what is PROVEN, with the command + output that proves it), not_done (exhaustive - anything unproven, '
    + 'launch-gated, or Will\'s call), proofs (commands + outputs + md5s), player_answer (a plain 2-3 sentence '
    + 'summary a non-technical player could be told about their specific report).',
    { label: 'inv:' + lane.key, phase: 'Investigate', schema: {
      type: 'object',
      properties: {
        outcome: { type: 'string', enum: ['FIXED', 'ALREADY-FIXED', 'NEEDS-WILL', 'DIAGNOSED-NOT-FIXABLE'] },
        status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' }, player_answer: { type: 'string' },
      },
      required: ['outcome', 'status', 'commit_sha', 'done', 'not_done', 'proofs', 'player_answer'],
    } }),
  (inv, lane) => agent(
    'INDEPENDENT ADVERSARIAL VET of ' + lane.branch + ' (' + lane.title + ').\n' + LAW + '\n\n'
    + 'Worktree ' + REPO + '/.claude/worktrees/' + lane.key + ', branch ' + lane.branch + '.\n\n'
    + 'THE INVESTIGATOR CLAIMS:\n'
    + 'OUTCOME: ' + (inv && inv.outcome) + '\nSTATUS: ' + (inv && inv.status) + ' | COMMIT: ' + (inv && inv.commit_sha) + '\n'
    + 'DONE: ' + (inv && inv.done) + '\nNOT DONE: ' + (inv && inv.not_done) + '\nPROOFS: ' + (inv && inv.proofs) + '\n'
    + 'PLAYER ANSWER: ' + (inv && inv.player_answer) + '\n\n'
    + 'You are NOT the investigator and you do not trust them. Build the artifacts yourself; accept no hash from any '
    + 'document. Check, in priority order:\n'
    + '1. Is the OUTCOME honest? An ALREADY-FIXED must be PROVEN from the shipped bytes, not asserted. A FIXED must '
    + '   rebuild and actually resolve the reported symptom. A DIAGNOSED-NOT-FIXABLE must genuinely have ruled out '
    + '   our data (do not let a real in-data fix be dodged as "engine").\n'
    + '2. SHARED-RECORD DAMAGE: did an edit to a shared record hit a non-target carrier? Enumerate carriers yourself.\n'
    + '3. ANIMATION/RIG (for maenad/invisible lanes): does every referenced anm/mesh/texture actually RESOLVE in the '
    + '   shipped arcs? An unresolved reference is exactly the class of these bugs.\n'
    + '4. NAVMESH (sparta lane): if any .lvl changed, prove the container is well-formed or byte-identical. The b89 '
    + '   crash made the game unplayable.\n'
    + '5. COLLATERAL: record-diff vs your own baseline; 0 REMOVED; Levels/Quests untouched unless the lane owns them.\n'
    + '6. HONESTY: compare DONE against what you can prove; is the player_answer TRUE and not overstated?\n\n'
    + 'Return verdict GO or NO-GO, issues (HIGH/MEDIUM/LOW each with the command that shows it), and a summary '
    + 'separating what you reproduced from what you took on trust.',
    { label: 'vet:' + lane.key, phase: 'Vet', schema: {
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
  outcome: (results[i] && results[i][0] && results[i][0].outcome) || (results[i] && results[i].outcome) || 'DIED',
  inv: results[i],
}))
log('wave complete')
return { lanes: LANES.map((l) => l.key), results }
