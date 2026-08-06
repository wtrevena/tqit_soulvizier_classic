export const meta = {
  name: 'pr-decisions-wave',
  description: "Act on Will's decisions: Sparta catacomb traveler (map), Gorgon full vanilla names (text), dye skins find-or-remove (asset). Implement + adversarial vet each.",
  phases: [
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'

const LAW = [
  'Repo: ' + REPO + '. main is the current tip; it contains the whole R-108 wave that is LIVE on Steam',
  '(item 3759792705) plus the two just-merged player-report fixes (maenad already-fixed note; PC dissolveTexture',
  'restore). Shipped DB build = arz md5 adc7ee4afbae54dfd883a3c52ddbcf51.',
  'Python: py launcher, PYTHONIOENCODING=utf-8; builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1.',
  '',
  'READ FIRST and obey: ' + REPO + '/CLAUDE.md (4 process laws), ' + REPO + '/docs/WILL_RULINGS.md (append rulings',
  'VERBATIM in a free decade, prove it free with git grep), ' + REPO + '/docs/BACKLOG.md (PR-2/PR-4/PR-5 are',
  'captured there with the prior lanes\' proven findings), ' + REPO + '/docs/MODDING_PLAYBOOK.md.',
  '',
  'Build the arz/map yourself and read the bytes - every hash in every doc has been stale at least once.',
  '',
  'HARD CONSTRAINTS',
  '- Work ONLY in your own worktree on your own branch. DO NOT DEPLOY, do not write to CustomMaps, do not launch/kill',
  '  TQ or Steam. The orchestrator owns deploys.',
  '- arz+Text are COUPLED; Levels+Quests are COUPLED - if you change one of a pair, build both.',
  '- COMMIT EVERY STEP. Never mutate shared git config from a linked worktree. NO ESTIMATES.',
  '- RETIREMENT PROTOCOL + SHARED-RECORD LAW: enumerate carriers before editing a shared record; CLONE and repoint',
  '  if a non-target carrier exists; never delete/blank/rename to fix without checking design intent.',
  '- NAVMESH is the top danger for the map lane: the b89 blood-cave crash was a malformed navmesh container that made',
  '  the game unplayable. Any .lvl you touch must be proven well-formed (parse_rec02 OK) or byte-identical; dry-run',
  '  every injection into COPIES and blob-diff before touching anything real.',
  '- Full build with gates, record the md5s you produce, record-diff vs a baseline you build from main in the same',
  '  environment (ZERO unattributed changes, 0 REMOVED records). Update the PR item in BACKLOG.',
].join('\n')

const LANES = [
  {
    key: 'sparta-catacomb',
    branch: 'fix/pr5-catacomb-traveler',
    title: 'PR-5: add the Sparta Crypt traveler to the Athens CATACOMBS (not Helos)',
    body: [
      'WILL\'S DECISION (verbatim intent): the Sparta Crypt should be entered from the Athens CATACOMBS, not from',
      'Helos. Ground truth already PROVEN by the prior lane (fix/pr5-sparta-portal @ 044dc1c, read its BACKLOG entry',
      'and WILL_TEST_GUIDE callout): on the shipped/canonical map, "Almyros the Wayfarer" (portal_master_helos) is',
      'placed x1 in the Helos plaza and routes to the crypt; the catacomb traveler records (svc_helos_trav_sparta,',
      'svc_area_return_sparta) exist in the arz but are placed 0x (TESTHUB-only, never shipped). The crypt itself',
      '(spartacryptlevel2) is present + walkable; a proven on-mesh placement spot exists in the deepest catacomb.',
      '',
      'DO:',
      '1. PLACE a Sparta-Crypt entrance traveler NPC in the Athens catacombs at the PROVEN turnkey spot the prior',
      '   lane found: CataCube02_FloorLast local (25,1,38) = world (-6587,1,-3180), by stairsdown01, 3.69u clearance.',
      '   Re-verify that spot on-mesh yourself before using it (do not trust the number blind). Use the existing',
      '   traveler record that already ships in the arz (svc_helos_trav_sparta / svc_area_return_sparta - pick the',
      '   correct one and say why) with the boat-dialog travel that lands the player ON-MESH inside spartacryptlevel2',
      '   (mirror Almyros\'s proven destination world (-5602,-2,-1409), local (42,42), which the prior lane proved',
      '   on-mesh). The return-out NPC (svc_testhub_return_sparta) is ALREADY placed inside the crypt - confirm it,',
      '   do not duplicate it.',
      '2. REMOVE the "The Sparta Crypt" destination from Almyros\'s Helos menu ONLY (the tagSVCHelosToSparta boat-dialog',
      '   option on portal_master_helos in sv_commonmechanics.qst). KEEP Almyros himself and his OTHER destinations',
      '   (Garden, Secret Place, Uber) - do NOT remove the Helos hub or its other routes. Prove those other routes are',
      '   untouched.',
      '3. This is a MAP + QUESTS change (coupled). Prove the navmesh container of every .lvl you touch stays',
      '   well-formed or byte-identical; dry-run into COPIES and blob-diff; only the intended blobs may change. Build',
      '   the canonical map (NOT the TESTHUB variant - TESTHUB is local-only and never ships) and record its md5.',
      '4. This CANNOT be verified in-game by you (deploys are the orchestrator\'s). Deliver a precise WILL_TEST_GUIDE',
      '   step so Will can walk to the catacomb spot and confirm the traveler is there and the route lands correctly.',
      '   State plainly that in-game confirmation is the remaining gate.',
    ].join('\n'),
  },
  {
    key: 'gorgon-vanilla',
    branch: 'fix/pr4-gorgon-vanilla',
    title: 'PR-4: restore the full vanilla Gorgon caster names (un-swap)',
    body: [
      'WILL\'S DECISION: restore the FULL VANILLA names. The prior lane (fix/pr4-gorgon-names @ 468b3e1) proved the',
      'two gorgon spellcasters carry Soulvizier\'s words ("Profaner" / "Geomancer") SWAPPED relative to base Titan',
      'Quest, whose canonical names are "Impious" and "Geomancy Adept". The fire-caster and the poison/earth-caster',
      'have each other\'s title.',
      '',
      'DO:',
      '1. From base TQAE data, establish the CORRECT vanilla mapping: which gorgon-caster archetype (fire vs',
      '   poison/geomancy) carries "Impious" and which carries "Geomancy Adept" in stock Titan Quest. Derive it from',
      '   the base records + each creature\'s own kit; do not guess.',
      '2. Set each of our two gorgon-caster records to the base-game-correct name TAG so they show the full vanilla',
      '   names, correctly un-swapped. Prefer the smallest correct change (repoint the descriptionTag on the record,',
      '   or correct the text the two tags resolve to) - state which mechanism and why. SHARED-RECORD LAW: confirm no',
      '   non-target creature shares the tag you touch.',
      '3. arz+Text are COUPLED - rebuild both. validate_tags must pass; read BOTH names back OUT of the rebuilt',
      '   Text.arc and confirm each resolves to the correct vanilla string on the correct creature.',
      '4. Record-diff vs a baseline from main: only the intended records/tags change, 0 REMOVED.',
    ].join('\n'),
  },
  {
    key: 'dye-skins',
    branch: 'fix/pr2-dye-skins',
    title: 'PR-2: dyes - find the missing costume skins, wire found ones, remove the rest',
    body: [
      'WILL\'S DECISION: try to FIND the missing costume-dye skin assets; wire in the ones found; for the ones that',
      'cannot be found, REMOVE them. The prior lane (fix/pr2-dyes-grey @ 8b8e7be, read its BACKLOG PR-2 entry) proved',
      'the Garden-of-Merchants "special/costume dyes" (OneShot_Dye records) reference character-skin textures that do',
      'not resolve in our shipped arcs -> the engine paints the PC flat grey. The plain color dyes work.',
      '',
      'DO:',
      '1. Enumerate every BROKEN special-dye record (missing gender-matching skin texture). The prior lane found ~300',
      '   OneShot_Dye records with a missing texture, 242 sold by the 6 Garden vendors and 58 NOT sold by them.',
      '   Re-derive this yourself and, for the 58, check whether any OTHER placed vendor/container/drop makes them',
      '   reachable (a grey dye anywhere is in scope).',
      '2. For EACH broken dye, HUNT its referenced skin texture across every asset source we ship or can extract:',
      '   base TQAE arcs, SV 0.98i / 0.9 / 0.41, SVAERA, DRX. If the exact texture EXISTS somewhere shippable, add it',
      '   to the correct mod .arc so the reference resolves (or repoint the dye to the correct existing path if it is',
      '   a path typo). Prove the reference resolves after rebuild.',
      '3. For dyes whose skin genuinely exists in NO source we can ship, REMOVE that dye: neutralize it from the',
      '   vendor stock / loot so a player can no longer buy or receive it (RETIREMENT PROTOCOL - do not delete the',
      '   record; make it unobtainable and record why). ',
      '4. Deliver a table: each broken dye -> FOUND+wired (with the asset+arc) or NOT-FOUND+removed (with where you',
      '   searched). After the change, PROVE zero obtainable dye references a missing skin (a gate is ideal). arz+Text',
      '   coupled if any tag changes; validate_tags must pass.',
    ].join('\n'),
  },
]

phase('Implement')
let round = 0
const results = await pipeline(
  LANES,
  (lane) => agent(
    lane.title.toUpperCase() + '\n' + LAW + '\n\n'
    + 'Worktree: ' + REPO + '/.claude/worktrees/' + lane.key + '   Branch: ' + lane.branch + '\n'
    + '(create: git worktree add ' + REPO + '/.claude/worktrees/' + lane.key + ' -b ' + lane.branch + ' main)\n\n'
    + lane.body + '\n\n'
    + 'Append any ruling VERBATIM to docs/WILL_RULINGS.md in a free decade. Update the PR item in BACKLOG. '
    + 'Return: status, commit_sha, done (PROVEN, with the command + output that proves it), not_done (exhaustive - '
    + 'anything unproven, launch-gated, or Will\'s call), proofs (commands + outputs + md5s), player_answer (2-3 '
    + 'plain sentences a non-technical player could be told).',
    { label: 'impl:' + lane.key, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' }, player_answer: { type: 'string' } },
      required: ['status', 'commit_sha', 'done', 'not_done', 'proofs', 'player_answer'],
    } }),
  (impl, lane) => agent(
    'INDEPENDENT ADVERSARIAL VET of ' + lane.branch + ' (' + lane.title + ').\n' + LAW + '\n\n'
    + 'Worktree ' + REPO + '/.claude/worktrees/' + lane.key + ', branch ' + lane.branch + '.\n\n'
    + 'THE IMPLEMENTER CLAIMS:\nSTATUS: ' + (impl && impl.status) + ' | COMMIT: ' + (impl && impl.commit_sha) + '\n'
    + 'DONE: ' + (impl && impl.done) + '\nNOT DONE: ' + (impl && impl.not_done) + '\nPROOFS: ' + (impl && impl.proofs) + '\n\n'
    + 'You are NOT the implementer and do not trust them. Build the artifacts yourself; accept no hash from any doc. '
    + 'Check: (1) does it do what Will decided (catacomb traveler present + reachable + Helos Sparta-route removed but '
    + 'other Helos routes intact; OR full vanilla gorgon names correctly un-swapped and resolving; OR every obtainable '
    + 'dye now resolves its skin, found-ones wired and not-found-ones unobtainable)? (2) NAVMESH: any touched .lvl '
    + 'well-formed or byte-identical - prove it, the b89 crash is the precedent. (3) SHARED-RECORD damage - enumerate '
    + 'carriers yourself. (4) COLLATERAL: record-diff/blob-diff vs your own baseline; 0 REMOVED; only intended blobs '
    + 'change; Levels/Quests untouched unless the lane owns them. (5) HONESTY: is DONE proven and player_answer TRUE? '
    + 'For an asset add, does the referenced texture ACTUALLY resolve now? Plant the check yourself.\n\n'
    + 'Return verdict GO or NO-GO, issues (HIGH/MEDIUM/LOW each with the command that shows it), and a summary '
    + 'separating what you reproduced from what you took on trust.',
    { label: 'vet:' + lane.key, phase: 'Vet', schema: {
      type: 'object',
      properties: { verdict: { type: 'string', enum: ['GO', 'NO-GO'] },
        issues: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } },
      required: ['verdict', 'issues', 'summary'],
    } }),
)

log('decisions wave complete')
return { lanes: LANES.map((l) => l.key), results }
