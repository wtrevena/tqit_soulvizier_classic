export const meta = {
  name: 'native-device-travel-wave',
  description: "R-246 (Will 2026-08-13): replace the corrupt 39-row armed boat-dialog travel table with ENGINE-NATIVE devices (teleport-shrine rifts / GridEntrance doors). Almyros keeps his 3-route talk menu. Fixes every misroute/mute Will hit + the Steam warden. Builds on fix/uber-labyrinth-entrance. Ships to Steam after DEV.",
  phases: [
    { title: 'Design' },
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/device-travel'
const BR = 'feat/native-device-travel'
const BASE = 'f9f213b'   // fix/uber-labyrinth-entrance HEAD - inherit its hygiene + corrected spots
const SCRATCH_EVIDENCE = 'C:/Users/willi/AppData/Local/Temp/claude/C--Users-willi-repos/98075e9c-011f-4120-9b92-ce6ca35146b2/scratchpad'

const LAW = [
  'Repo: ' + REPO + '. main = 34b014e (build90-ship, LIVE on Steam). Work ONLY in a NEW worktree ' + WT + ' on branch ' + BR,
  'created FROM ' + BASE + ' (= fix/uber-labyrinth-entrance HEAD: the vetted R-245 wave - labyrinth entrance at corrected maze03',
  'spot, plaza >=4.1u spacing, landing moves, R5 return retargets. INHERIT all of it; REWORK what the ruling changes).',
  'py launcher, PYTHONIOENCODING=utf-8; builds PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 into scratch SVC_OUT_DIR. DO NOT deploy,',
  'DO NOT touch CustomMaps/TQ/Steam, DO NOT touch main checkout work//local/. COMMIT EVERY STEP. Couplings: arz+Text, Levels+Quests.',
  'NAVMESH b89 LAW: touched blobs keep 0x0b byte-identical or parse_rec02-proven. TESTHUB stays LOCAL-ONLY. Shared-record law:',
  'clone before modifying any shared record. Retirement protocol: ledger-check before deleting/retiring ANY row/record.',
  '',
  'WILL RULINGS 2026-08-13 (append VERBATIM to docs/WILL_RULINGS.md as R-246):',
  '1. ARCHITECTURE (his AskUserQuestion choice "Native devices"): replace most boat-NPC routes with engine-native mechanisms',
  '   that use zero quest rows - teleport-shrine rifts (proven in our Secret Place) and/or GridEntrance doors (proven',
  '   build24/25) for area entrances/returns, INCLUDING the Sparta Warden descend. Almyros keeps his 3-route talk menu',
  '   (matches the base-game envelope). Kills the bug class permanently; fixes the Warden on Steam.',
  '2. EVIDENCE (his answer): during the misroutes "labels were wrong too" - the menus themselves showed cross-bound rows',
  '   (e.g. the Vashkarr traveler offering Helos (Return)) => corruption at LOOKUP time; the whole-row cross-binding is confirmed.',
  '',
  'THE PROVEN MECHANISM (hunt final report; artifacts in ' + SCRATCH_EVIDENCE + ' - h3_h4_out.txt = registration+event tables,',
  'h2_quest_side.json, h2_diff_full.txt; READ THEM): sv_commonmechanics step 1 arms 39 Action_BoatDialog rows on a blanket',
  'OnLevelLoad step re-fired every level load; 15 rows share one tag+dest; 17 NPCs remote. Base-game census: max 2 rows armed',
  'per step EVER, zero tag/dest reuse, one-shot persistent arming. Result: stateful registry corruption - clicks execute other',
  'rows (label included), NPCs with cross-bound rows go fully mute (warden, dorus-return). All shipped bytes internally perfect',
  '=> invisible to offline gates. ALSO: buried-NPC class - return NPCs\' Y was copied from the landing Y, never re-derived from',
  'terrain (svc_area_return_tantalus @ Styx_SwampBorder_01 Y=-12 Will-confirmed buried; warband likely; testhub sparta check).',
].join('\n')

phase('Design')
const design = await agent(
  'NATIVE-DEVICE TRAVEL - DESIGN + MECHANISM RE. READ-ONLY (no commits). \n' + LAW + '\n\n'
  + 'Produce the DEVICE PLAN the implementer executes. Do the reverse-engineering FIRST, from working instances:\n'
  + '1. TELEPORT-SHRINE RIFT MECHANICS: the mod ships working rifts (teleportshrineorient01 in RogueEncampment/Secret Place;\n'
  + '   teleportshrine_gom in the Garden). Decode from the arz records + placements: how does a rift define its DESTINATION\n'
  + '   (record fields? paired instances? 0x14?), is it one-way or two-way, does it need quest state, what makes it clickable,\n'
  + '   what does the player SEE (mesh/fx/label). Establish whether we can mint N independent rift pairs with arbitrary\n'
  + '   endpoints, and every field required. Check SV-upstream usage for precedent (SV shipped these).\n'
  + '2. GRIDENTRANCE DOOR MECHANICS: from build24/25 (Knossos->UberDungeon door, invented Sparta door) + the blood-cave mouth\n'
  + '   + docs/MODDING_PLAYBOOK.md: what a door needs (0x05 + 0x14 GUID binding + landing), constraints (level-to-level only?),\n'
  + '   crash history (b89!), and where doors beat rifts.\n'
  + '3. THE ROUTE MAP: enumerate every travel connection the mod needs (from the R-245 audit table + WILL_TEST_GUIDE):\n'
  + '   canonical = Garden/Secret/Uber via Almyros (KEEP talk menu, 3 rows) + labyrinth->UberDungeon entrance (corrected maze03\n'
  + '   spot) + catacombs->SpartaCrypt (the warden spot) + every in-area return back to its entrance (R5 pattern) + the blood\n'
  + '   cave (already engine-native walk-in, untouched). TESTHUB adds: the 14 plaza launchers + boss-area returns. Assign each\n'
  + '   connection a DEVICE (rift pair vs door) with exact coords (inherit R-245 corrected spots; re-derive Y from navmesh\n'
  + '   heights for EVERY device - the buried-Y class dies here), what the player sees, and the label/name surface (player-\n'
  + '   surface checklist - no unlabeled mystery devices; use existing proven art only, no invented assets).\n'
  + '4. THE RIP PLAN: which quest rows/triggers are REMOVED from build_quest_files.py (the 39-row hub table incl. the warden\n'
  + '   row + enter-offers), which SURVIVE (Almyros 3 rows; SV-native urder 3 + Leinth vortex 5 + base 4 + Olympus-Rhodes 1 =\n'
  + '   ~13 global armed - flag as residual, DO NOT touch the SV-native/upstream-authentic ones), and what happens to the\n'
  + '   warden NPC (he stays PLACED as flavor beside his door/rift per shared-record law, or is retired - ledger check;\n'
  + '   RECOMMEND keep-as-greeter: zero risk, he just no longer owns travel).\n'
  + '5. GATES to ship with the wave (no-new-surface-without-a-gate): MAX_ARMED_BOATDIALOG budget (per-step AND global, from\n'
  + '   the base census; our post-rip counts must fit), Y-vs-terrain for every placed travel device/NPC, device-resolution\n'
  + '   (every rift/door dest on-mesh in the right level, pairs consistent), and the negative battery.\n'
  + 'Return: rift_mechanics (proven fields+constraints), door_mechanics, route_map (every connection: device type, coords,\n'
  + 'Y-derivation, surface), rip_plan (rows removed/kept + warden disposition), gates_plan, risks (exhaustive, incl. what\n'
  + 'CANNOT be proven offline and needs Will\'s walk).',
  { label: 'design', phase: 'Design', schema: {
    type: 'object',
    properties: { rift_mechanics: { type: 'string' }, door_mechanics: { type: 'string' }, route_map: { type: 'string' },
      rip_plan: { type: 'string' }, gates_plan: { type: 'string' }, risks: { type: 'string' } },
    required: ['rift_mechanics', 'door_mechanics', 'route_map', 'rip_plan', 'gates_plan', 'risks'],
  } })

if (!design) { return { status: 'no-go', error: 'design agent died - relaunch' } }

let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  phase('Implement')
  impl = await agent(
    'NATIVE-DEVICE TRAVEL - IMPLEMENT (round ' + round + ').\n' + LAW + '\n\nTHE DESIGN (execute it; deviate only with stated reason):\n'
    + 'RIFT MECHANICS: ' + design.rift_mechanics + '\nDOOR MECHANICS: ' + design.door_mechanics
    + '\nROUTE MAP: ' + design.route_map + '\nRIP PLAN: ' + design.rip_plan + '\nGATES: ' + design.gates_plan
    + '\nRISKS: ' + design.risks + '\n'
    + (round > 1 && verdict ? '\nVET RETURNED ' + verdict.verdict + '. CLEAR EVERY ISSUE, re-measure:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\n' : '')
    + '\nDELIVER, committing every step on ' + BR + ':\n'
    + '1. The RIP: remove the hub row table per the plan (retirement protocol notes in the commit); Almyros\'s 3 rows + all\n'
    + '   SV-native/base rows untouched. Prove post-rip armed counts (per-step + global).\n'
    + '2. The DEVICES: every route-map connection built (rift pairs / doors) at the planned coords with navmesh-derived Y,\n'
    + '   on BOTH map variants where applicable (canonical set on canonical; TESTHUB adds its launchers). b89 proof per\n'
    + '   touched blob. Player surface: each device visibly labeled/identifiable per the plan.\n'
    + '3. The Y-FIXES for the buried roster (tantalus/warband/sparta-check) even where devices replace them - no buried\n'
    + '   anything remains.\n'
    + '4. The GATES: armed-row budget + Y-vs-terrain + device-resolution, wired into the battery, with planted negatives.\n'
    + '5. BUILDS + PROOFS: canonical + TESTHUB Levels, Quests, (arz+Text only if the plan minted tags) - det-2x, full diffs\n'
    + '   vs the ' + BASE + ' baseline (only intended blobs/entries), all gates + contracts 0 P0/0 P1.\n'
    + '6. DOCS: R-246 rulings VERBATIM, WILL_TEST_GUIDE rewritten for device travel (his walk checks), BACKLOG lane record\n'
    + '   + debts (incl. the ~13 residual armed rows + anything unproven offline).\n'
    + 'Return: status, commit_sha, armed_counts (before/after per-step+global), artifact_md5s, devices_built (count+summary),\n'
    + 'done (PROVEN w/ commands), not_done (exhaustive), proofs.',
    { label: 'impl:r' + round, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, armed_counts: { type: 'string' },
        artifact_md5s: { type: 'string' }, devices_built: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'armed_counts', 'artifact_md5s', 'devices_built', 'done', 'not_done', 'proofs'],
    } })

  if (!impl) { log('round ' + round + ': impl died (transient), retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL VET (round ' + round + ') of ' + BR + ' @ ' + impl.commit_sha + '.\n' + LAW + '\n\n'
    + 'THEY CLAIM:\nARMED: ' + impl.armed_counts + '\nARTIFACTS: ' + impl.artifact_md5s + '\nDEVICES: ' + impl.devices_built
    + '\nDONE: ' + impl.done + '\nNOT DONE: ' + impl.not_done + '\nPROOFS: ' + impl.proofs + '\n\n'
    + 'Rebuild everything yourself from the branch + the ' + BASE + ' baseline. Verify: (1) THE RIP - decode the built Quests\n'
    + 'yourself: armed BoatDialog counts per-step and global match the claim; Almyros exactly 3 rows; NO hub row survives;\n'
    + 'SV-native/base rows byte-untouched. (2) DEVICES - decode every rift/door from the built maps: dest resolves on-mesh in\n'
    + 'the right level, pairs consistent, Y = navmesh height (re-derive yourself), b89 navmesh identity per touched blob,\n'
    + 'labels/surfaces present. (3) The warden disposition per plan; no stranding anywhere (every area reachable AND exitable\n'
    + 'walk the full graph). (4) BURIED roster cured; sweep ALL travel surfaces for Y-below-terrain yourself. (5) GATES real:\n'
    + 'planted negatives actually fire; budget gate RED on the pre-rip Quests (anti-inert proof). (6) COLLATERAL: diffs vs\n'
    + BASE + ' = only intended; couplings honored; contracts 0 P0/0 P1. (7) HONESTY of done/not_done. GO only if a Steam\n'
    + 'player and TESTHUB Will can reach + leave every area through devices that cannot cross-bind. Return verdict GO/NO-GO,\n'
    + 'issues (severity + command each), summary.',
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
  devices_built: impl && impl.devices_built, done: impl && impl.done, not_done: impl && impl.not_done,
  vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
