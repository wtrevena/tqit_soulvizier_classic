export const meta = {
  name: 'uber-labyrinth-entrance',
  description: "R-250 travel-NPC canonical sweep: promote the TESTHUB 'Enter the Uber Dungeon' NPC into the Labyrinth of Knossos on the CANONICAL (Steam) map, AND audit every travel NPC against Will's rule - only the Helos-launch portals stay TESTHUB-only; every NPC that transports players into/out of areas must be on Steam. Promote all violators. Navmesh-safe; ships to Steam.",
  phases: [
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/uber-laby'
const BR = 'fix/uber-labyrinth-entrance'

const LAW = [
  'Repo: ' + REPO + '. main HEAD = 34b014e = build90-ship = LIVE on Steam. Python: py launcher, PYTHONIOENCODING=utf-8;',
  'map/DB builds get PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1. Build into a SCRATCH dir (SVC_OUT_DIR) - NEVER clobber work/ or',
  'local/ (another session is active in the main checkout). Work ONLY in your own worktree ' + WT + ' on ' + BR,
  '(git worktree add ' + WT + ' -b ' + BR + ' 34b014e). DO NOT DEPLOY / write CustomMaps / launch TQ or Steam. COMMIT EVERY STEP.',
  '',
  'GROUND TRUTH (byte-proven by recon a38b8146, verify yourself):',
  '- Live canonical Levels md5 = 6784cf0f (current main produces it; SVC_TEST_HUB UNSET). Shipped Quests = 736cd50a. Shipped arz = a86afc15.',
  '- The Uber Dungeon (crypt_floor1) is reachable on Steam ONLY via Almyros the Helos portal-master (portal_master_helos, x1 in',
  '  startingfarmland06d) menu option "The Uber Dungeon" (tagSVCHelosToUber -> lands world (-2438,10,-2450) in crypt_floor1). KEEP Almyros UNCHANGED.',
  '- The labyrinth Uber entrance is TESTHUB-ONLY today: svc_area_return_uber is placed IN maze03 (Labyrinth of Knossos) under an',
  '  SVC_TEST_HUB gate and offers the enter-offer "Enter the Uber Dungeon" -> crypt_floor1. It is ABSENT on canonical (Steam).',
  '  The old maze03 walk-through GridEntrance (portal_olympianarena1) was REMOVED 2026-07-12 (Will) - DO NOT restore a walk-through/',
  '  proximity teleport; the fix is a TALK-TO-TRAVEL NPC only (Will ruling).',
  '- The b89 warden-awakening shipped [ShowNpc, UpdateNPCDialog(Dialog Needed), BoatDialog] on all 30 SVC boat NPCs in Quests 736cd50a.',
  '',
  'HARD CONSTRAINTS: NAVMESH is the top danger (b89 crash): any .lvl blob you touch must be well-formed (parse_rec02(decompress=True)',
  'OK) or byte-identical; a placement-only 0x05 edit must leave the 0x0b navmesh BYTE-IDENTICAL - prove it. TESTHUB stays LOCAL-ONLY',
  '(never uploaded). Deploy couplings: Levels+Quests together, arz+Text together. SHARED-RECORD LAW: adding a PLACEMENT of a shared',
  'record is fine (does not modify the record); do NOT modify svc_area_return_uber or any record shared with other placements.',
].join('\n')

phase('Implement')
let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  impl = await agent(
    'UBER LABYRINTH ENTRANCE - IMPLEMENT (round ' + round + ').\n' + LAW + '\n'
    + (round > 1 && verdict ? '\nTHE VET RETURNED ' + verdict.verdict + '. CLEAR EVERY ISSUE:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\nRe-measure, do not restate.\n' : '')
    + '\nWILL DECIDED THREE THINGS (2026-08-13, record all VERBATIM in the ruling):\n'
    + '1. Put the Uber Dungeon entrance in the Labyrinth of Knossos on the STEAM build (promote the TESTHUB "Enter the Uber\n'
    + '   Dungeon" NPC to canonical), keeping Almyros in Helos as a second route.\n'
    + '2. THE GENERAL RULE (verbatim): "the only ones that should be testhub only are the portals from Helos, all the other NPCs\n'
    + '   that actually take you to the areas need to be in the steam build." I.e. svc_helos_trav_* (the Helos plaza hub launchers)\n'
    + '   + the TESTHUB portal rig stay TESTHUB-only; EVERY other travel NPC - area ENTRANCES (enter-offers placed in the world)\n'
    + '   and in-area RETURNS (no stranding) - must be placed on CANONICAL.\n'
    + '3. IN-GAME PLACEMENT BUG, Will just hit it live (verbatim): "the guy in the minoan labarynth the traveler there is placed\n'
    + '   literally right behind the door after you kill the minotaur and you cant even see him based on where he is placed and i\n'
    + '   cant click on him. You need to move him farther along the pathway so the user can see him and click on him instead of\n'
    + '   literally right behind the door where the user cant see or click on him."\n'
    + '   => THE CURRENT TESTHUB COORDINATE IS DISQUALIFIED. Do NOT promote it as-is. The corrected placement must be:\n'
    + '   (a) FARTHER ALONG the pathway the player walks after killing the Minotaur (past the door, in the direction of travel),\n'
    + '   (b) in OPEN corridor/room space with real clearance from the door frame and walls (an NPC hugging door/wall geometry is\n'
    + '       occluded from the TQ camera and its click-target is swallowed - measure distance to the door entity + nearby wall\n'
    + '       pieces in the 0x05/0x14 data and keep several units of standoff, comparable to how base-game NPCs stand in rooms),\n'
    + '   (c) visible + clickable: centered in walkable space, not clipped into scenery, comfortable clearance on all sides.\n'
    + '   APPLY THE SAME CORRECTED COORDINATE TO BOTH MAPS - Will hit this on his own (TESTHUB/DEV) build, so fixing canonical\n'
    + '   while leaving TESTHUB at the behind-the-door spot would leave his play surface broken. Move the TESTHUB placement too.\n'
    + '4. THE MAZE03 NPC IS THE ENTRANCE, NOT A WAY BACK (verbatim): "the guy behind the door to the minotaur should take you\n'
    + '   to the uber dungeon, not back to helos and his message should not be \'return to helos\' it should be \'travel to the\n'
    + '   uber dungeon\' or something like that." Will clicked him in-game and his visible offer was "return to helos" (which\n'
    + '   then misrouted him to the catacombs - a separate forensic lane is on the misroute). REQUIRED END-STATE for this NPC:\n'
    + '   - His menu offers EXACTLY ONE route: "Travel to the Uber Dungeon" (or closely similar wording), landing on-mesh in\n'
    + '     crypt_floor1. Use/verify the existing enter-offer wording tag if it already ships (b62 minted an "Enter the Uber\n'
    + '     Dungeon" enter-offer keyed on svc_area_return_uber); if a new tag is minted, that is an arz+Text-coupled change -\n'
    + '     follow the PR-5 warden pattern exactly (dedicated tag, Text build, validate_tags green).\n'
    + '   - REMOVE the Helos-return route from this NPC (strip him from HELOS_HUB_TRAVEL / whatever binds "return to helos" to\n'
    + '     him) so the mislabeled/misrouting offer Will hit cannot appear. The way OUT of the Uber Dungeon stays the in-crypt\n'
    + '     return NPC (svc_testhub_return_uber) - do not touch it.\n'
    + '   - This mirrors the PR-5 Sparta Warden descend-only design; if svc_area_return_uber\'s display name/tag is a SHARED\n'
    + '     generic ("Return Traveler" class), apply the shared-record law: CLONE to a dedicated record before renaming or\n'
    + '     retagging anything shared (a fitting name like the warden got is welcome but optional - the MENU behavior is the\n'
    + '     requirement; put any naming ambiguity in not_done for Will rather than inventing lore).\n'
    + '5. THE RETURN-TRAVELER PATTERN, UNIVERSAL (verbatim): "there should be a return traveler at the end of the uber dungeon\n'
    + '   that takes you back to where the npc is that lets you travel to the uber dungeon in the first place. this is the\n'
    + '   pattern that should be followed everywhere that we have return travelers." I.e. every in-area return traveler lands\n'
    + '   the player AT ITS OWN AREA\'S ENTRANCE NPC (on-mesh, with standoff - do NOT land the player ON TOP of the entrance\n'
    + '   NPC; the pr5 0.00u-overlap lesson), with label text that says where it goes:\n'
    + '   - Uber Dungeon return (svc_testhub_return_uber in crypt_floor1) -> the maze03 labyrinth spot beside the NEW corrected\n'
    + '     entrance-NPC placement, label like "Return to the Labyrinth of Knossos". NOT Helos.\n'
    + '   - Sparta Crypt return (svc_testhub_return_sparta in spartacryptlevel2) -> the Athens catacombs L3 spot beside the\n'
    + '     Warden, label like "Return to the Athens Catacombs". NOT Helos.\n'
    + '   - Garden / Secret Place returns: their entrance NPC is Almyros IN HELOS, so returning to Helos (beside Almyros) IS\n'
    + '     the pattern - verify their dest coords land beside Almyros and their labels say so; retarget only if they do not.\n'
    + '   - Audit EVERY other return traveler in the roster against this pattern (canonical AND TESTHUB routes); retarget the\n'
    + '     violators. Every retarget: dest on-mesh in the correct level, proven (containment + clearance), label text matches\n'
    + '     the destination, awakening intact. New/changed label tags = arz+Text couple, PR-5 pattern.\n'
    + '6. FORENSIC-DRIVEN HYGIENE (wf_46ee9772 verified findings; ALL routes byte-correct, these are the UX traps that caused\n'
    + '   Will\'s scrambled session - fix them in this lane since they live in the same files):\n'
    + '   - PLAZA DE-CROWDING (TESTHUB): the 14 svc_helos_trav_* clones span ~15x5u; sparta + uber stand 1.66u apart as\n'
    + '     byte-identical clones (differ ONLY in hover tooltip) - Will clicked uber meaning sparta. Space ALL plaza travelers\n'
    + '     to >=4u pairwise (build_section_surgery Helos-hub plaza specs). If a cheap visual distinction per traveler exists\n'
    + '     (distinct existing meshes/tints already shipped in our arcs, per the player-surface checklist), apply it; otherwise\n'
    + '     register as debt - do NOT invent unverified art.\n'
    + '   - RETURN-LANDING HYGIENE: the shared Helos-return dest (-5980,1,909) (15 rows: 5 svc_testhub_return_* + 10\n'
    + '     svc_area_return_*) drops the player INSIDE the clickable cluster (1.12u from trav_secret) - the rebound trap that\n'
    + '     bounced Will to the catacombs. Move the shared landing (and any R5 retargets) to >=6u clear of EVERY clickable NPC\n'
    + '     while satisfying R5 (beside the entrance NPC = near, not ON). Literals live in build_quest_files.py\n'
    + '     TESTHUB_RETURN_DESTS, TESTHUB_RETURN_DESTS_BY_NPC, HELOS_HUB_TRAVEL Helos rows + tagSVCAreaReturnToHelos rows.\n'
    + '   - UBER LANDING OFF THE PORTAL PROP: \'The Uber Dungeon\' dest (-2438,10,-2450) is 0.09u from portal_olympianarena2\n'
    + '     (player teleports ON a portal prop; click-shadow risk; present on Steam too). Nudge the landing 3-4u clear\n'
    + '     (HELOS_PORTAL_DESTS + TRAVELER_ENTER_OFFERS literals), keep it on-mesh + 3u-ish from the in-crypt return NPC.\n'
    + '   - These quest-dest literal changes are Quests-side; the spacing changes are Levels-side - keep the couplings honest\n'
    + '     in the report (what changed on each side; TESTHUB Levels rebuild also picks up the R-240 cage split that DEV is\n'
    + '     currently stale on - note it in the report so the orchestrator deploys the fresh TESTHUB to DEV).\n\n'
    + 'DO:\n'
    + '0. FULL TRAVEL-NPC AUDIT FIRST: enumerate EVERY travel NPC record (portal_master_helos, svc_warden_sparta_crypt,\n'
    + '   svc_helos_trav_*, svc_area_return_*, svc_testhub_return_*, portal rig NPCs, any other boat-dialog NPC in the quest\n'
    + '   wiring) and its placements on BOTH maps (build canonical from 34b014e = must reproduce 6784cf0f; TESTHUB from the same\n'
    + '   tree with SVC_TEST_HUB=1). Produce a classification table: record | placed canonical | placed TESTHUB | role\n'
    + '   (Helos-launcher / area-entrance / in-area-return / rig) | verdict under Will\'s rule (OK / VIOLATION). Also cover every\n'
    + '   quest ROUTE that is inert on canonical (wired but no placement): for each, state whether inertness is CORRECT (Helos\n'
    + '   hub) or a VIOLATION (an area entrance/return missing from Steam). Do not assume the uber NPC is the only violator.\n'
    + '1. Establish the TESTHUB placement of svc_area_return_uber: which .lvl (maze03 / Labyrinth of Knossos), exact local coords,\n'
    + '   and the SVC_TEST_HUB-gated code path in tools/build_section_surgery.py that places it. Read docs/WILL_TEST_GUIDE.md too.\n'
    + '2. Determine whether the enter-offer + b89 awakening for svc_area_return_uber ALREADY ships in Quests 736cd50a (inert on\n'
    + '   canonical, activated by a canonical placement) or is itself TESTHUB-gated in build_quest_files. If it already ships, this\n'
    + '   is a LEVELS-ONLY change (Quests byte-unchanged). If not, add the enter-offer + awakening to the canonical Quests build too.\n'
    + '2b. PROMOTE EVERY OTHER VIOLATOR from step 0 the same way: a canonical placement at a spot on the player\'s natural walkable\n'
    + '   path (per-area survey, same rigor as step 3), with its quest wiring active + awakened. If an apparent violator is\n'
    + '   actually unnecessary on canonical (e.g. its area is an ordinary campaign spot players walk to, no transport needed, or\n'
    + '   its entrance exists via another canonical mechanism), do NOT place it - RECORD the reasoning per NPC in the report +\n'
    + '   BACKLOG instead; ambiguous calls go to the not_done list for Will, never silently skipped.\n'
    + '3. REACHABILITY IS THE CRUX: the placement MUST sit on the PLAYER\'S NATURAL WALKABLE PATH through the Labyrinth of Knossos\n'
    + '   - ideally at/near the Minotaur Lord\'s lair or the point Flozer44 expected the portal (after the Minotaur/Telkine) - NOT\n'
    + '   merely on-mesh at the old TESTHUB teleport-landing spot if that spot is isolated/only-reachable-by-teleport. Survey the\n'
    + '   maze navmesh + the Minotaur boss placement; prove the chosen spot is on-mesh (parse_rec02/clearance) AND in the same\n'
    + '   walkable component the player traverses to fight the Minotaur. Justify the exact coord.\n'
    + '4. Place svc_area_return_uber x1 on CANONICAL at that spot (move it out of the SVC_TEST_HUB gate into the canonical\n'
    + '   INJECT_SPECS, or add a canonical placement; ensure TESTHUB still has its placement too / is not broken). Do NOT place\n'
    + '   svc_helos_trav_uber on canonical (that Helos-launch traveler is a testhub-only convenience; the player reaches the\n'
    + '   labyrinth by playing). Almyros + the Sparta warden + every other placement UNCHANGED.\n'
    + '5. Build the CANONICAL map into scratch (SVC_TEST_HUB unset). PROVE: only the ONE touched labyrinth blob changes vs the\n'
    + '   6784cf0f baseline you build from 34b014e; its 0x0b navmesh BYTE-IDENTICAL; svc_area_return_uber now placed x1 canonical\n'
    + '   in the labyrinth + still x1 on TESTHUB; Almyros still x1 in Helos; 0 REMOVED. Run gate_traveler_responds --canonical and\n'
    + '   gate_boat_npc_awakening; confirm the Uber enter-offer resolves + lands on-mesh in crypt_floor1; contracts 0 P0/0 P1.\n'
    + '6. If Quests changed: rebuild it, prove per-entry diff vs shipped 736cd50a = only the intended entry differs. If Levels-only,\n'
    + '   state Quests is byte-unchanged (736cd50a) and the pair still ships together.\n\n'
    + 'Update docs/WILL_TEST_GUIDE.md (walk-to for the labyrinth Uber entrance) + append a ruling to docs/WILL_RULINGS.md VERBATIM\n'
    + '("Will 2026-08-13: put the Uber Dungeon entrance in the Labyrinth of Knossos on Steam, talk-to-travel, keep Almyros in Helos")\n'
    + '+ a BACKLOG lane record. Return: status, commit_sha, levels_md5 (new canonical), quests_md5 (736cd50a if unchanged),\n'
    + 'spot (level+coords+why-reachable), done (PROVEN w/ commands+md5s), not_done (exhaustive), proofs.',
    { label: 'impl:r' + round, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, levels_md5: { type: 'string' },
        quests_md5: { type: 'string' }, spot: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'levels_md5', 'quests_md5', 'spot', 'done', 'not_done', 'proofs'],
    } })

  if (!impl) { log('round ' + round + ': impl died (transient), retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL VET (round ' + round + ') of ' + BR + '.\n' + LAW + '\n\n'
    + 'THEY CLAIM:\nSTATUS ' + impl.status + ' | COMMIT ' + impl.commit_sha + ' | canonical Levels ' + impl.levels_md5
    + ' | Quests ' + impl.quests_md5 + '\nSPOT: ' + impl.spot + '\nDONE: ' + impl.done + '\nNOT DONE: ' + impl.not_done
    + '\nPROOFS: ' + impl.proofs + '\n\n'
    + 'Build the canonical map yourself from BOTH 34b014e (baseline = must be 6784cf0f) and ' + BR + '. Verify:\n'
    + '(0) THE AUDIT TABLE (Will\'s rule): independently enumerate EVERY travel NPC\'s placements on both maps and re-derive the\n'
    + '    OK/VIOLATION classification yourself. The rule: only svc_helos_trav_* + the TESTHUB rig may be TESTHUB-only; every area\n'
    + '    ENTRANCE and in-area RETURN must be canonical. Any violator the implementer missed, mis-classified, or silently skipped\n'
    + '    (without a recorded reasoning or a not_done entry) = NO-GO.\n'
    + '(1) svc_area_return_uber now placed x1 on CANONICAL in the Labyrinth of Knossos; enumerate its placements on both maps.\n'
    + '(2) REACHABILITY + VISIBILITY: every newly promoted spot is on-mesh AND in the walkable component the player naturally\n'
    + '    traverses (for uber: the path AFTER the Minotaur; not an isolated teleport-only nook). Will DISQUALIFIED the old TESTHUB\n'
    + '    spot in-game: "literally right behind the door... you cant even see him... i cant click on him". Verify the new spot is\n'
    + '    NOT the old coordinate, is farther along the pathway past the door, and has measured standoff from the door entity and\n'
    + '    wall pieces (re-derive the distances from the 0x05/0x14 data yourself; an NPC hugging geometry = NO-GO). Verify the SAME\n'
    + '    corrected coordinate landed on BOTH maps (TESTHUB placement moved too - Will plays TESTHUB and hit the bug there).\n'
    + '(3) NAVMESH b89: every touched blob\'s 0x0b navmesh is BYTE-IDENTICAL; every other blob byte-identical; 0 added/removed levels.\n'
    + '(4) Each promoted NPC\'s enter-offer/route + awakening resolves in the shipped Quests (736cd50a) or the rebuilt Quests, lands\n'
    + '    on-mesh in its destination; NO walk-through/proximity teleport introduced anywhere.\n'
    + '(4b) MENU LAW (Will ruling 4): the maze03 entrance NPC offers EXACTLY ONE route, worded "Travel to the Uber Dungeon" (or\n'
    + '    closely similar), landing in crypt_floor1; the "return to helos" offer is GONE from him. Decode his full trigger set\n'
    + '    yourself - any second route or stale Helos-return binding = NO-GO.\n'
    + '(4c) RETURN PATTERN (Will ruling 5): every in-area return traveler lands beside ITS OWN entrance NPC (uber return -> the\n'
    + '    maze03 entrance spot; sparta return -> the catacombs Warden spot; Garden/Secret returns -> beside Almyros in Helos),\n'
    + '    labels match destinations, landings on-mesh with standoff (NOT on top of the entrance NPC - re-measure the distances).\n'
    + '    Walk every return route end-to-end in the bytes; a return still pointing at the wrong place = NO-GO.\n'
    + '(4d) HYGIENE (ruling 6): re-measure yourself on the built maps - all plaza travelers >=4u pairwise; the shared Helos-return\n'
    + '    landing (and every R5-retargeted landing) >=6u from every clickable NPC; the Uber landing >=3u from portal_olympianarena2\n'
    + '    and still on-mesh near its return NPC. Any landing inside a clickable cluster or on a prop = NO-GO.\n'
    + '(5) Almyros untouched (x1 Helos, menu intact), Sparta warden\'s ENTRANCE untouched, TESTHUB not broken (its placements all\n'
    + '    still present).\n'
    + '(6) COLLATERAL: only the intended blobs/records change; contracts 0 P0/0 P1; couplings honored (if Levels-only, Quests==736cd50a).\n'
    + '(7) HONESTY: is DONE proven from bytes? Is the ruling recorded VERBATIM? Return verdict GO/NO-GO, issues (HIGH/MEDIUM/LOW + the\n'
    + '    command each), summary.',
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
  commit: impl && impl.commit_sha, levels_md5: impl && impl.levels_md5, quests_md5: impl && impl.quests_md5,
  spot: impl && impl.spot, done: impl && impl.done, not_done: impl && impl.not_done,
  vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
