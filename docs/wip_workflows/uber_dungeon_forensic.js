export const meta = {
  name: 'uber-dungeon-forensic',
  description: 'READ-ONLY forensic: is crypt_floor1 (the Uber Dungeon interior) an unfinished stub or merge-dropped? Characterize 3 Will-reported symptoms (minimap misalign, no chests/bosses, invisible walls).',
  phases: [
    { title: 'Forensic', detail: 'contents / navmesh-walls / minimap-zone, in parallel' },
    { title: 'Synthesize', detail: 'never-finished vs merge-dropped verdict + fix scope' },
    { title: 'Verify', detail: 'adversarially challenge the verdict' },
  ],
}

// ============================================================================
// R-250 UBER DUNGEON FORENSIC (Will 2026-08-14). READ-ONLY. No file mutations.
// Backdrop: the labyrinth->Uber entrance is now CONFIRMED WORKING in-game, so
// Will is INSIDE crypt_floor1 for the first time and reports it looks unfinished:
//   (a) minimap misaligned with the map          (b46/b46r3 minimap lane REGRESSION)
//   (b) no chests / no loot / no star|boss mobs
//   (c) invisible walls in some passageways ("seems like this area never got finished")
// GROUND TRUTH breadcrumbs (verified by orchestrator via grep):
//   * Level = levels/world/uberdungeon/crypt_floor1.lvl ; entrance chamber (-2438,10,-2457)
//   * b46 minimap fix set crypt_floor1 LEVELS zone dbr -> _ZONE_GREECE_DELPHI
//     (tools/svaera_plus_portals.py ~line 291) to fix "drawn minimap does not line up".
//   * b46r3 set crypt_floor1 region GUID -> _OBSIDIAN_HALLS_REGION_GUID (~line 401) for the
//     top-right area label ("Village of Helos" bug).
//   * crypt_floor1 described in build_quest_files.py as "single-component" navmesh.
//   * el_boss_audit.md documents a MERGE-DROPPED failure mode (content present in source SV
//     but lost in our Levels.arc merge). THAT is the central fork here.
// THE FORK (drives everything): was crypt_floor1 ALWAYS an empty/unfinished stub in the
// reference source, or was it populated in source and DROPPED in our merge? The answer
// decides polish-pass vs content-rebuild vs map-restore.
// ============================================================================

const REPO = String.raw`C:\Users\willi\repos\tqit_soulvizier_classic`

const COMMON = `
REPO: ${REPO}
TARGET LEVEL: levels/world/uberdungeon/crypt_floor1.lvl  (this IS "the Uber Dungeon" interior; entrance lands at chamber (-2438,10,-2457)).
CONSTRAINTS: STRICTLY READ-ONLY. Do NOT modify, build-into, or commit anything. You may build into a SCRATCH/throwaway dir or read existing built arcs, but never mutate tracked files.
TOOLING ALREADY IN REPO (reuse, do not reinvent): tools/ has a reusable arz loader + level-blob (.lvl) reader (see tasks around "level-blob reader for audit"), parse_rec02 navmesh helpers, tools/check_connectivity.py (greps levels for bossarena/uberdungeon/coldtombs/spartacrypt and dumps level string content), tools/svaera_plus_portals.py (the map builder + the zone/region override tables), tools/build_quest_files.py (landing coords). Run python as: PYTHONIOENCODING=utf-8 the repo's Python (Python312). AWS not needed.
HOW TO GET THE SHIPPED CANONICAL crypt_floor1.lvl: prefer an existing built canonical Levels arc (look under local/, work/, and any baseline_build* snapshots) OR build the canonical map fresh with the documented command (svaera_plus_portals.py WITHOUT SVC_TEST_HUB, into a scratch out dir) then extract the world01.map -> crypt_floor1.lvl blob. State exactly which artifact you analyzed + its md5.
HOW TO GET THE REFERENCE SOURCE crypt_floor1.lvl: locate the SV/AERA source under reference_mods/ (e.g. reference_mods/SVAERA_customquest/Resources/Levels.arc or the base game Levels.arc). Extract the SAME-named level blob. If the level does not exist in a given source, SAY SO explicitly (that itself is evidence).
OUTPUT DISCIPLINE: every claim backed by a byte/record/coordinate observation. No speculation dressed as fact. If you cannot determine something, say UNKNOWN + why. Your returned text IS structured data for the orchestrator, not a human chat message.
`

const CONTENTS_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['artifact_analyzed','artifact_md5','reference_source','reference_has_level',
             'ours_monster_proxy_count','ours_chest_loot_count','ours_boss_or_champion_count',
             'ref_monster_proxy_count','ref_chest_loot_count','ref_boss_or_champion_count',
             'content_dropped_in_merge','symptom_b_verdict','evidence','confidence'],
  properties: {
    artifact_analyzed: { type: 'string', description: 'path of OUR crypt_floor1 source (which arc/build)' },
    artifact_md5: { type: 'string' },
    reference_source: { type: 'string', description: 'path of the reference SV/base Levels arc used' },
    reference_has_level: { type: 'boolean', description: 'does crypt_floor1.lvl exist in the reference source at all?' },
    ours_monster_proxy_count: { type: 'integer' },
    ours_chest_loot_count: { type: 'integer' },
    ours_boss_or_champion_count: { type: 'integer' },
    ref_monster_proxy_count: { type: 'integer', description: '-1 if reference lacks the level' },
    ref_chest_loot_count: { type: 'integer', description: '-1 if reference lacks the level' },
    ref_boss_or_champion_count: { type: 'integer', description: '-1 if reference lacks the level' },
    content_dropped_in_merge: { type: 'string', enum: ['YES','NO','PARTIAL','UNKNOWN'], description: 'was content present in source but lost in our merge?' },
    symptom_b_verdict: { type: 'string', description: 'plain verdict on "no chests / no star|boss monsters"' },
    evidence: { type: 'array', items: { type: 'string' }, description: 'concrete observations: entity types, dbr names, coords, counts' },
    confidence: { type: 'string', enum: ['HIGH','MEDIUM','LOW'] },
  },
}

const NAVMESH_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['artifact_analyzed','navmesh_component_count','passage_coverage_finding',
             'ref_navmesh_component_count','invisible_wall_root_cause','symptom_c_verdict','evidence','confidence'],
  properties: {
    artifact_analyzed: { type: 'string' },
    navmesh_component_count: { type: 'integer', description: 'walkable navmesh components in OUR crypt_floor1' },
    ref_navmesh_component_count: { type: 'integer', description: '-1 if reference lacks the level' },
    passage_coverage_finding: { type: 'string', description: 'do passageways have walkable mesh, or gaps where the invisible walls are?' },
    invisible_wall_root_cause: { type: 'string', description: 'best byte-grounded explanation (missing mesh / collision prop / unbuilt region / etc.)' },
    symptom_c_verdict: { type: 'string' },
    evidence: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['HIGH','MEDIUM','LOW'] },
  },
}

const MINIMAP_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['canonical_zone_binding','b46_fix_present_in_canonical','testhub_only','misalign_root_cause','symptom_a_verdict','fix_recipe','evidence','confidence'],
  properties: {
    canonical_zone_binding: { type: 'string', description: 'the actual zone dbr / region GUID bound to crypt_floor1 in the SHIPPED CANONICAL map + arz' },
    b46_fix_present_in_canonical: { type: 'boolean', description: 'did the b46 _ZONE_GREECE_DELPHI minimap fix actually land in the canonical shipped map?' },
    testhub_only: { type: 'boolean', description: 'is the fix present only in TESTHUB and absent from canonical?' },
    misalign_root_cause: { type: 'string', description: 'why the minimap still does not line up' },
    symptom_a_verdict: { type: 'string' },
    fix_recipe: { type: 'string', description: 'concrete next step to actually fix the misalignment' },
    evidence: { type: 'array', items: { type: 'string' } },
    confidence: { type: 'string', enum: ['HIGH','MEDIUM','LOW'] },
  },
}

const SYNTH_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['headline_verdict','never_finished_vs_merge_dropped','fix_scope','recommended_lanes','open_questions','ship_impact'],
  properties: {
    headline_verdict: { type: 'string', description: 'one-sentence answer to Will: is the Uber Dungeon unfinished, merge-dropped, or fine-but-mislabeled?' },
    never_finished_vs_merge_dropped: { type: 'string', enum: ['NEVER_FINISHED','MERGE_DROPPED','PARTIAL_BOTH','FINE_MISLABELED','UNKNOWN'] },
    fix_scope: { type: 'string', enum: ['POLISH_PASS','MAP_RESTORE_FROM_SOURCE','FULL_CONTENT_REBUILD','NO_FIX_NEEDED','MIXED'] },
    recommended_lanes: { type: 'array', items: { type: 'string' }, description: 'ordered, concrete next lanes (one per symptom or grouped), each with what it would do' },
    open_questions: { type: 'array', items: { type: 'string' }, description: 'decisions that need Will' },
    ship_impact: { type: 'string', description: 'does this block/affect the in-flight build92 (Almyros trim + Warden)? (it should NOT - different files - confirm.)' },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['agrees_with_verdict','strongest_counter_argument','holes','corrected_verdict_if_any','confidence'],
  properties: {
    agrees_with_verdict: { type: 'boolean' },
    strongest_counter_argument: { type: 'string', description: 'the best case AGAINST the synthesis verdict' },
    holes: { type: 'array', items: { type: 'string' }, description: 'unproven assumptions or gaps in the forensic' },
    corrected_verdict_if_any: { type: 'string', description: 'if you would change the verdict, state the corrected one; else "none"' },
    confidence: { type: 'string', enum: ['HIGH','MEDIUM','LOW'] },
  },
}

phase('Forensic')
const [contents, navmesh, minimap] = await parallel([
  () => agent(`${COMMON}

YOUR JOB (CONTENTS): Establish whether crypt_floor1 is populated, and whether any content was DROPPED in our merge.
1. Extract OUR shipped-canonical crypt_floor1.lvl and enumerate EVERY placed entity: monster proxies / spawn points (note star=champion and boss flags), chest & loot placements, interactive props. Give counts + example dbr names/coords.
2. Extract the REFERENCE-SOURCE crypt_floor1.lvl (SV/AERA and/or base) and enumerate the same. If the level is absent from a source, say so.
3. Compare. Is our copy missing monsters/chests/bosses that the source had? That is the MERGE-DROPPED signal. If source was ALSO empty, that is the NEVER-FINISHED signal.
Return ONLY the structured object.`, { label: 'forensic:contents', phase: 'Forensic', schema: CONTENTS_SCHEMA }),

  () => agent(`${COMMON}

YOUR JOB (NAVMESH / INVISIBLE WALLS): Explain Will's "invisible walls in some passageways ... seems like this area never got finished."
1. Parse OUR crypt_floor1 navmesh (0x0b RLTD). Count walkable components. Map whether the passageways/corridors actually have walkable mesh, or whether there are gaps/holes where a player would hit an invisible wall.
2. Do the same for the REFERENCE source crypt_floor1 (component count, coverage). Compare - did our merge lose navmesh coverage, or is the source itself sparse/unfinished?
3. Also check for collision props or boundary geometry that would read as invisible walls.
Ground every claim in bytes/coords. Return ONLY the structured object.`, { label: 'forensic:navmesh', phase: 'Forensic', schema: NAVMESH_SCHEMA }),

  () => agent(`${COMMON}

YOUR JOB (MINIMAP / ZONE LABEL): Will reports "the minimap is misaligned with the map in the uber dungeon." We already SHIPPED a fix for exactly this (b46/b46r2/b46r3, 2026-07-13): svaera_plus_portals.py set crypt_floor1's LEVELS zone dbr -> _ZONE_GREECE_DELPHI (~line 291) and region GUID -> _OBSIDIAN_HALLS_REGION_GUID (~line 401).
1. Determine the ACTUAL zone/region binding on crypt_floor1 in the SHIPPED CANONICAL map (build canonical fresh WITHOUT SVC_TEST_HUB, or read the shipped canonical arc) + any zone record in the arz. Did the b46 minimap fix actually land in CANONICAL, or is it TESTHUB-only / absent?
2. Explain WHY the minimap still doesn't line up. (Zone dbr controls which minimap page/scale is drawn; misalignment usually = wrong zone bounds/origin vs the level's actual grid corner. crypt_floor1 grid corner noted as (-2578,-2682).)
3. Give a concrete fix recipe.
Return ONLY the structured object.`, { label: 'forensic:minimap', phase: 'Forensic', schema: MINIMAP_SCHEMA }),
])

log(`Forensic in: contents=${contents?contents.symptom_b_verdict:'NULL'} | navmesh=${navmesh?navmesh.symptom_c_verdict:'NULL'} | minimap=${minimap?minimap.symptom_a_verdict:'NULL'}`)

phase('Synthesize')
const synth = await agent(`${COMMON}

You are the SYNTHESIS. Three read-only forensic agents examined crypt_floor1 (the Uber Dungeon interior). Their structured findings:

CONTENTS: ${JSON.stringify(contents)}
NAVMESH/WALLS: ${JSON.stringify(navmesh)}
MINIMAP/ZONE: ${JSON.stringify(minimap)}

Resolve THE FORK for Will: is the Uber Dungeon (a) NEVER_FINISHED (a stub in source too), (b) MERGE_DROPPED (populated in source, lost in our merge), (c) PARTIAL_BOTH, or (d) FINE_MISLABELED? Then give the fix scope and the concrete ordered lanes that would address the three symptoms (minimap / empty / invisible walls). Confirm this does NOT collide with the in-flight build92 lane (Almyros trim + Warden fix, which touches quests + the Almyros boat rows, NOT crypt_floor1 contents/navmesh). Return ONLY the structured object.`,
  { label: 'synthesize', phase: 'Synthesize', schema: SYNTH_SCHEMA })

phase('Verify')
const verify = await agent(`${COMMON}

ADVERSARIAL CHECK. A synthesis concluded the following about crypt_floor1:
${JSON.stringify(synth)}

Backed by forensic findings:
CONTENTS: ${JSON.stringify(contents)}
NAVMESH: ${JSON.stringify(navmesh)}
MINIMAP: ${JSON.stringify(minimap)}

Try to REFUTE the verdict. Default to skepticism: is "merge-dropped" vs "never-finished" actually PROVEN by the evidence, or assumed? Are the entity/navmesh counts from comparable extractions (same level, same coordinate frame)? Could the "empty" reading be a difficulty-gated or proxy-based spawn the forensic missed (many TQ bosses spawn via proxy/championChance, invisible to a naive count)? Could the invisible walls be intended geometry? Name the strongest counter-argument and any holes. If the evidence does not support the verdict, give the corrected one. Return ONLY the structured object.`,
  { label: 'verify', phase: 'Verify', schema: VERIFY_SCHEMA })

return {
  contents, navmesh, minimap, synth, verify,
  BOTTOM_LINE: {
    verdict: synth?.never_finished_vs_merge_dropped ?? 'UNKNOWN',
    fix_scope: synth?.fix_scope ?? 'UNKNOWN',
    verify_agrees: verify?.agrees_with_verdict ?? null,
    corrected: verify?.corrected_verdict_if_any ?? 'none',
  },
}
