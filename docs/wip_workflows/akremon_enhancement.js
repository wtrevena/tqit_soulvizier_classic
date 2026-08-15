export const meta = {
  name: 'akremon-enhancement',
  description: "R-247 (Will 2026-08-13): Akremon (Golden Bough uber) 'got way smaller and turned into a different character completely who was much much weaker, he should be enhanced significantly' + 'he still drops an orb named Charon's Essence'. Size + power + amgoz1-style signature kit (the backlogged innovation pass, now ACTIVATED) + orb rename. arz+Text couple. Runs parallel to the device-travel wave.",
  phases: [
    { title: 'Implement' },
    { title: 'Vet' },
  ],
}

const REPO = 'C:/Users/willi/repos/tqit_soulvizier_classic'
const WT = REPO + '/.claude/worktrees/akremon'
const BR = 'feat/akremon-enhancement'

const LAW = [
  'Repo: ' + REPO + '. main = 34b014e (build90-ship, LIVE). Work ONLY in worktree ' + WT + ' on ' + BR + ' from 34b014e',
  '(git worktree add ' + WT + ' -b ' + BR + ' 34b014e). NOTE: two other lanes run in parallel in their own worktrees',
  '(device-travel, uber-laby) - do not enter them; your changes are arz+Text-side (patches modules), theirs are quest/map;',
  'keep any apply_svc_patches.py edits minimal and additive to reduce merge friction.',
  'py launcher, PYTHONIOENCODING=utf-8; builds PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 into scratch. NO deploy/CustomMaps/',
  'TQ/Steam/main-checkout-work-local. COMMIT EVERY STEP. Couplings: arz+Text together. Shared-record law: clone before',
  'modifying any record with other carriers; enumerate carriers FIRST. Retirement protocol on any removal.',
  '',
  'WILL RULINGS (2026-08-13, append VERBATIM to docs/WILL_RULINGS.md as R-247):',
  '1. "akremon the heartwood ablaze got way smaller and turned into a different character completely who was much much',
  '   weaker, he should be enhanced significantly. also he still drops an orb named Charon\'s Essence"',
  '2. STANDING DIRECTION from 2026-08-12 (the backlogged kit pass, NOW ACTIVATED by ruling 1): make the kit MORE innovative',
  '   by MERGING distinctive skills from multiple sources (some of Telkine Ormenos\'s moves + Charon + other monsters),',
  '   amgoz1-style, for a truly signature kit. Cite amgoz1_design_voice.md in the content brief (standing creative bar).',
  '3. LETHAEUS (Will 2026-08-13, verbatim): "lethaeus the unremembered has the same problem, the second form of the boss is',
  '   much smaller and much weaker than the original form." In this mod the design law is: the second/final form is the',
  '   ESCALATION (cf. the Soul Gaoler -> unbound final version pattern). A form-2 smaller AND weaker than form-1 = defect.',
  '4. THE CLASS-WIDE AUDIT (implied by two hits; curious-QA law - find them ALL offline, do not let Will discover them one',
  '   fight at a time): enumerate EVERY multi-form boss (actorToSpawnOnDeath chains + any other form mechanism) and every',
  '   uber-tier boss in the shipped arz; measure form-vs-form (scale/HP/damage/defense) and boss-vs-uber-band. Produce the',
  '   full audit table. FIX in this lane: Akremon + Lethaeus (fully, per rulings) + any BLATANT same-class offender (form 2',
  '   strictly smaller AND weaker than form 1 - the D5 blatant-error-sweep precedent; each fix individually justified and',
  '   listed). Borderline/judgment cases: FLAG in the table for Will, do not retune.',
  '5. ENDLESS HUNT IDENTITY (Will 2026-08-13, verbatim): "also toxeus the murderer the endless hunt is still a demon not a',
  '   skeleton and he summons blood hounds which makes no sense." TWO FIXES on um_toxeus_hunt_99 (+ his _l/zzdev siblings if',
  '   they share the defect - enumerate): (a) MESH/RACE: he must be a SKELETON like every Toxeus variant - follow the',
  '   green-mesh lane precedent (Enslaver=SkeletonGrayBlack01New.msh, Devourer=GoldenSkeleton01.msh; pick a distinct clean',
  '   skeleton mesh for the Hunt, in-game-confirmed asset only, no green-glow-class mesh); fix race fields to match the',
  '   family. Note Will said "STILL a demon" - git-archaeology what b98 intended vs shipped. (b) SUMMONS: replace the blood',
  '   hounds (blood = the DEVOURER\'s theme, not the Hunt\'s) with summons fitting the Endless Hunt\'s identity (skeletal',
  '   spear-hunter, endless pursuit) in amgoz1 voice - design your best recommendation (e.g. skeletal huntsmen/spectral',
  '   pursuers in the family\'s black-shroud style), castability+summon-chain gated (A9 render-chain law), flag the choice',
  '   in not_done for Will\'s veto. Keep his 4 b98 skills + endless-pursuit mechanics + spear intact.',
  '6. ENDLESS HUNT KILL-CHAIN + TIERED SOULS (Will 2026-08-13 after killing the LEGENDARY Hunt, verbatim): "So I was able to',
  '   kill the demon version of legendary toxeus the murderer, the endless hunt and i got his soul and the mystical orb but',
  '   it didnt drop the forge formula that should allow you make craft the uber toxeus the murderer soul which should allow',
  '   you to summon the toxeus the murderer guy who you cant even fight in the game, toxeus the murderer end of all things.',
  '   the formula to craft his soul should have dropped when i killed the endless hunt. also the endless hunt wasnt using a',
  '   spear, and his soul should let you summon him and it doesnt. also when you pick up toxeus the murder enslaver of souls',
  '   soul, you can summon toxeus the murderer enslaver of souls. the legendary and epic versions of the soul should allow',
  '   you to summon much stronger versions of him instead of all the normal epic and legendary versions letting you summon',
  '   the same version." FOUR items:',
  '   (a) EOAT FORMULA DROP: trace the full chain in the shipped arz - Hunt death -> End-of-All-Things forge-formula drop ->',
  '       forge recipe -> EoAT soul -> EoAT summon. Find WHY a Legendary Hunt kill dropped soul+orb but NO formula (wrong',
  '       record/chance/difficulty row/missing wiring - b98 claimed "EoAT formula" shipped; archaeology what broke). FIX so',
  '       the formula reliably drops from the Hunt (state the chosen chance + justify; Will expected it from HIS kill, so',
  '       default 100% like the soul unless a ruling says otherwise) and the ENTIRE craft->summon chain resolves (every link',
  '       gated: formula item exists, recipe consumes real ingredients, produces the EoAT soul, soul summon castable + A9).',
  '   (b) SPEAR - VERIFY FIRST, FIX ONLY IF BROKEN: Will initially reported "the endless hunt wasnt using a spear" but then',
  '       SOFTENED it (verbatim): "maybe he was using a spear and i couldnt see it, there was a lot going on." So this is an',
  '       UNCERTAIN observation, not a confirmed bug. Byte-verify the whole spear chain: weapon record resolves, equip',
  '       chance/slot correct, anim table carries the spear stances (the thrown-wielder lesson class). If the bytes prove it',
  '       correct: change NOTHING, report it PROVEN with the evidence. Only fix if a real defect shows in the bytes.',
  '   (c) HUNT SOUL SUMMONS HIM: his soul item must grant a working summon of the Endless Hunt (like the other Toxeus souls).',
  '       Trace why it currently does not (missing skill grant, dead pet record, dtype trap) + fix; pet lessons apply',
  '       (Pet.tpl restrictions, permanent-pet spawnObjectsTimeToLive=[], NEVER clone_record for souls - use _ensure_record;',
  '       CLAUDE.md key lessons section).',
  '   (d) TIERED SOUL SUMMONS: measure how the n/e/l tiers of the TOXEUS-FAMILY souls are configured today (one record or',
  '       three, per-difficulty pet rows, identical-or-not - full table in the report; a parallel recon answers Will quickly',
  '       but YOUR measurement is the implementation truth). IMPLEMENT for the Toxeus-family souls (Enslaver + Devourer +',
  '       Hunt + EoAT as applicable): Normal < Epic < Legendary summon strength, Epic/Legendary "much stronger" (justify the',
  '       scaling from the uber band; per-difficulty rows or tier records - pick the mechanism the pet system supports safely',
  '       per the Pet.tpl lessons). The MOD-WIDE extension (every soul in the game tiered) = FLAG as a Will decision with a',
  '       measured landscape table, do NOT implement mod-wide in this lane.',
  '   (e) SOUL +ALL-SKILLS BONUS (Will 2026-08-13 follow-up, verbatim): "also the epic and legendary versions of these',
  '       toxeus the murderer souls should give you +2 and +3 to all skills respectively and +1 to all skills for the normal',
  '       difficulty soul." EXACT LAW for the Toxeus-family soul ITEMS (the wearer bonus, on the soul-as-equipment):',
  '       Normal tier = +1 to all skills, Epic = +2, Legendary = +3. Use the base-game +all-skills item mechanism',
  '       (augmentAllLevel or whichever field base items provably use - verify from a base +all-skills item), correct dtype',
  '       (the INT/FLOAT corruption trap), stacking sanely with whatever the souls already grant. Applies to "these toxeus',
  '       the murderer souls" = the family rosters in (d).',
  '   RECON GROUND TRUTH (a parallel read-only agent already decoded the shipped arz - VERIFY, then build on it, do not',
  '   rediscover from scratch): (i) Enslaver + Devourer tiers ALREADY ladder correctly (3 item records n/e/l -> same skill',
  '   @ itemSkillLevel 1/2/3 -> DISTINCT pets toxeus_enslaver_1/2/3: L40/13k HP/110-160 dmg -> L68/18k/170-250 ->',
  '   L100/24k/240-350; bloodtoxeus same shape) BUT the tier pets share ONE display name/model/attributes = tiering is',
  '   INVISIBLE in-game (why Will read them as identical). So (d) means: RAISE the scaling to "much stronger" AND make each',
  '   tier VISIBLY distinct (per-tier pet display name at minimum, e.g. tier suffix; player-surface checklist).',
  '   (ii) The Hunt soul grants svc_hunt_quarrysmark (attack buff) and NO summon exists - no summon_toxeus_hunt skill, no',
  '   hunt pet records AT ALL; (c) is a BUILD not a fix: mint pets _1/_2/_3 + Skill_SpawnPet ladder + itemSkillName swap on',
  '   the 3 souls per the family pattern (decide whether Quarry\'s Mark stays as a secondary grant - flag the choice).',
  '   (iii) THE EOAT FORMULA IS ALREADY A GUARANTEED DROP on both hunt records (Misc4@100 via svc_rite_guaranteed, wired',
  '   correctly, 3 difficulty entries) - the REAL defect is VISIBILITY: svc_toxeus_eoat_formula is itemClassification=',
  '   Common with the generic "Blank Arcane Formula" mesh/bitmap = a plain white drop lost in the boss-orb explosion (and',
  '   hidden by loot filters). FIX (a) = rarity/visual: proper classification + distinct name surface so an uber-soul',
  '   formula reads as one; keep the guaranteed drop. ALSO: svc_rite_guaranteed has NO difficulty gate (drops on Normal/',
  '   Epic too) - decide with justification whether that is intended (formula needs 3 LEGENDARY souls as reagents anyway)',
  '   or gate it; flag either way.',
  '7. CHESTS + DEVOURER SPAWNS (Will 2026-08-13, ANGRY, verbatim): "wtf did you do to all the chests like toxeus the',
  '   murderer devourer of blood\'s stash? Revert it back to what it was dropping in the original sv you nerfed the fuck',
  '   out of it. also on normal difficulty toxeus the murderer devourer of blood wasnt even there guarding his stash, he',
  '   should spawn there 100% of the time on every difficulty. also something else got messed up where toxeus the',
  '   murderer, enslaver of souls is spawning in the entrance to the blood cave next to the tattered parchment where',
  '   toxeus the murderer, devourer of blood should be spawning at a 33% rate." THREE items:',
  '   (a) CHEST REVERT: measure the Devourer\'s stash chest (the blood-cave chest-room Majestic chest guarded by',
  '       um_bloodtoxeus_99) + the family of uber stash chests: CURRENT loot vs ORIGINAL SV 0.98i (the upstream arz =',
  '       the design bible; decode the SV originals). Identify WHICH wave nerfed them (prime suspects: R-240 loot-volume',
  '       trim [build84] and R-242 orb-chance rework [build86]) and REVERT these stash chests to the original-SV drop',
  '       richness. LEDGER DISCIPLINE: R-240/R-242 were Will-ratified - this ruling SUPERSEDES them FOR THESE CHESTS;',
  '       amend the ledger entries with the scope carve-out, do not silently contradict them. Enumerate exactly which',
  '       chests you revert (the "chests like ... stash" class = the uber/boss stash chests; general world loot stays',
  '       under R-240) and show before/current/after tables.',
  '   (b) DEVOURER STASH SPAWN 100% ALL DIFFICULTIES: on Normal he was ABSENT from his stash. The M15 mechanism put',
  '       um_bloodtoxeus_99 at 100% into the chest-area pack proxy (egg_blooddragon_pack). Decode the pool per-difficulty:',
  '       find why Normal has no Devourer (difficulty-gated row / champion-cap equation / pool weights) and fix to 100%',
  '       spawn on Normal+Epic+Legendary.',
  '   (c) PARCHMENT SPOT = DEVOURER at 33%, NOT ENSLAVER: at the blood-cave entrance beside the tattered parchment, the',
  '       ENSLAVER is spawning where the DEVOURER should spawn at 33%. Decode the parchment-area pool (the old BACKLOG',
  '       queued items "PARCHMENT REPOINT" + "33% CHANCE retune championChance 50->33 via toxeus_suite" - check whether a',
  '       half-landed change caused the wrong variant); fix: Devourer at 33% there, Enslaver removed from that spot',
  '       (verify where the Enslaver SHOULD spawn per the ledger and that his correct spawns remain intact).',
  '8. ENSLAVER EPIC DIFFICULTY - NOTE ONLY, DO NOT TUNE (Will 2026-08-13, verbatim, append to ledger as an OPEN TUNING',
  '   QUESTION): "I am level 70 running through legendary difficulty easily and I still cant kill toxeus the murderer,',
  '   enslaver of souls on epic difficulty since I just kill myself when i hit him. I have like all the best legendary',
  '   gear, all of it enchanged, and two normal difficulty toxeus the murderer, enslaver of souls pets both of whom i',
  '   have summoned and I still cant kill him... I hit him like 4 or 5 times and then i have to hit one of his demon guys',
  '   to restore health since I have like 50% attack damage converted to health which doesn\'t work on skeletons but which',
  '   works on his demons... maybe i need to get to like level 90 and come back idk. i can now kill the normal difficulty',
  '   variant with both my pets but he is like level 41 or something. Maybe this difficulty setting is right, idk but',
  '   make note of it." Record with the mechanics observation: melee-leech builds are DOUBLE-countered (reflect self-',
  '   damage + undead leech-immunity blocks sustain on the boss), pets cannot outpace his heal. Measure + report his Epic',
  '   reflect%/heal-rate/HP as data for the future tuning decision. NO stat changes to the Enslaver in this lane.',
  '',
  'CONTEXT: Akremon = the Golden Bough uber (R-231/build85, branch feat/charon-rework lineage - he REPLACED a Charon-derived',
  'encounter; the b85 kit was purpose-built from PLANT donors: Ascacophus02 strongbark + DRX emberoak + Skill_DefensiveWall',
  'quillvine wall [the mod\'s ONLY terrain-builder] + drx_earthbind + razorquill fan phase1 -> ring-of-flame + volcanic orb',
  'phase2; vet-proven 0 Charon signature skills). Will has now MET him in-game and ruled him too small + much too weak.',
  'His arena = the old Charon-dock spot (Styx RiverEdge). R-242 orb rules: uber orbs 0/50/75 leg by difficulty; Toxeus+Leinth',
  'excluded/better. Check WILL_RULINGS for every Akremon/charon/orb ruling before changing anything.',
].join('\n')

phase('Implement')
let impl = null, verdict = null
for (let round = 1; round <= 3; round++) {
  impl = await agent(
    'AKREMON ENHANCEMENT - IMPLEMENT (round ' + round + ').\n' + LAW + '\n'
    + (round > 1 && verdict ? '\nVET RETURNED ' + verdict.verdict + '. CLEAR EVERY ISSUE, re-measure:\n'
        + JSON.stringify(verdict.issues, null, 1) + '\n' + verdict.summary + '\n' : '')
    + '\nDO, with ground truth first:\n'
    + '1. ESTABLISH CURRENT STATE from the shipped arz (a86afc15): Akremon\'s record(s) - exact display name/title (Will says\n'
    + '   "the Heartwood Ablaze"; the board said "the Grasping Root" - the TEXT is truth), scale/actorHeight/actorRadius, mesh,\n'
    + '   level/HP/damage/resists/OA-DA, full skill kit, the orb record + its name tag (the "Charon\'s Essence" leftover), drop\n'
    + '   wiring. Compare against: (a) the PRE-b85 encounter he replaced (git history of feat/charon-rework - what size/power\n'
    + '   was the previous boss), (b) the mod\'s other uber bosses (Toxeus variants, Leinth, Tantalus, Vashkarr, Aithon - the\n'
    + '   power band he must sit in; Will calls him "the ultimate boss" tier company).\n'
    + '2. SIZE: make him physically IMPOSING again - scale him to uber-boss presence (justify the number from the mesh + the\n'
    + '   uber-boss size band; verify the mesh scales cleanly - no clipping through his own arena geometry; keep collision\n'
    + '   sane per actorRadius conventions).\n'
    + '3. POWER: "enhanced significantly" - retune HP/damage/resists/defenses to the uber band (justify each number against\n'
    + '   the measured uber-boss table, not invented; NO-ESTIMATES law). He should be a real wall for a player who farms\n'
    + '   Toxeus-tier content.\n'
    + '4. KIT (the activated innovation pass, amgoz1 creative bar - read docs/amgoz1_design_voice.md and cite it): KEEP his\n'
    + '   plant identity (quillvine wall terrain-builder is his signature - keep) and MERGE IN distinctive moves per Will\'s\n'
    + '   direction: select 2-4 signature skills from Telkine Ormenos + Charon + other fitting monsters, adapted to the\n'
    + '   heartwood/ember identity (e.g. Ormenos\'s eruption-class casts refit as ember/root, a Charon dock-themed move).\n'
    + '   EVERY added skill: castability-proven (the b108 anim-table law - skill anim empty-or-in-his-resolved-rig; run the\n'
    + '   castability gate), donor cloned not modified, phase structure coherent. Player-surface checklist: names, FX that\n'
    + '   are in-game-confirmed assets only, tooltips.\n'
    + '5. ORB RENAME: the orb name tag "Charon\'s Essence" -> an Akremon-fitting name in amgoz1 voice (implement your best\n'
    + '   recommendation, e.g. derived from his actual title; keep it behind its own tag so Will can veto-rename cheaply;\n'
    + '   flag the chosen name in not_done for his approval). Text build + validate_tags green. Keep the orb\'s R-242 drop\n'
    + '   mechanics/loot rules UNTOUCHED unless a ruling says otherwise.\n'
    + '6. LETHAEUS (ruling 3): find Lethaeus the Unremembered\'s form chain in the shipped arz; measure form-1 vs form-2\n'
    + '   (scale/HP/damage/defense/kit). Fix form-2 to be the ESCALATION: at least form-1\'s presence and strictly stronger,\n'
    + '   sitting in the uber band; keep his identity/kit intact (this is a scale+power fix, not a kit rework, unless a kit\n'
    + '   skill is provably dead - then castability-fix it). Justify every number from the measured band.\n'
    + '7. CLASS-WIDE AUDIT (ruling 4): enumerate ALL multi-form bosses + ubers; produce the form-vs-form + band table.\n'
    + '   Fix BLATANT same-class offenders (strictly smaller AND weaker form-2), each individually justified + listed;\n'
    + '   FLAG borderline cases for Will without touching them.\n'
    + '8. BUILD + PROVE: full DB build det-2x, record-diff vs shipped a86afc15 baseline = ONLY intended records; Text delta =\n'
    + '   only intended tags; castability gate green for every kit skill; contracts 0 P0/0 P1; registry selfcheck; negatives.\n'
    + '9. DOCS: R-247 VERBATIM (all 4 parts) in WILL_RULINGS, content brief citing amgoz1_design_voice.md, WILL_TEST_GUIDE\n'
    + '   fight-checks (Akremon + Lethaeus), BACKLOG lane record (close the backlogged kit-pass item as ACTIVATED->DONE) +\n'
    + '   the audit table + debts.\n'
    + 'Return: status, commit_sha, current_state (measured baselines incl. Lethaeus forms), changes (size/power/kit/orb +\n'
    + 'lethaeus + audit-fixes with justifications), audit_table (all multi-form/uber bosses: verdict per boss), arz_md5,\n'
    + 'done (PROVEN), not_done (exhaustive, incl. the orb-name choice for Will + in-game fights unproven), proofs.',
    { label: 'impl:r' + round, phase: 'Implement', schema: {
      type: 'object',
      properties: { status: { type: 'string' }, commit_sha: { type: 'string' }, current_state: { type: 'string' },
        changes: { type: 'string' }, audit_table: { type: 'string' }, arz_md5: { type: 'string' }, done: { type: 'string' },
        not_done: { type: 'string' }, proofs: { type: 'string' } },
      required: ['status', 'commit_sha', 'current_state', 'changes', 'audit_table', 'arz_md5', 'done', 'not_done', 'proofs'],
    } })

  if (!impl) { log('round ' + round + ': impl died (transient), retry'); continue }

  phase('Vet')
  verdict = await agent(
    'INDEPENDENT ADVERSARIAL VET (round ' + round + ') of ' + BR + ' @ ' + impl.commit_sha + '.\n' + LAW + '\n\n'
    + 'THEY CLAIM:\nBASELINE: ' + impl.current_state + '\nCHANGES: ' + impl.changes + '\narz: ' + impl.arz_md5
    + '\nDONE: ' + impl.done + '\nNOT DONE: ' + impl.not_done + '\nPROOFS: ' + impl.proofs + '\n\n'
    + 'Rebuild + decode yourself. Verify: (1) the measured baseline is real (re-measure Akremon + the uber band from the\n'
    + 'shipped arz); (2) size/power numbers land him in the uber band with justifications that hold - challenge "significantly\n'
    + 'enhanced": would a Toxeus-farming player find him a REAL fight, not a pushover and not unkillable (reflect lessons -\n'
    + 'no 100%-reflect traps); (3) EVERY kit skill castable from his actual rig (run the gate + trace each anim), donors\n'
    + 'cloned w/ carriers enumerated, phases coherent, amgoz1 voice cited and plausibly honored, FX from confirmed assets;\n'
    + '(4) orb rename: tag resolves in Text, old "Charon\'s Essence" gone from player surface, drop mechanics untouched;\n'
    + '(4b) LETHAEUS: re-measure both forms yourself from the built arz - form-2 is now strictly the escalation (scale AND\n'
    + 'power) and in the uber band; his identity/kit intact; the form-chain wiring (actorToSpawnOnDeath etc.) unbroken.\n'
    + '(4c) THE AUDIT: re-run the multi-form/uber enumeration yourself - is the table COMPLETE (no multi-form boss missed)?\n'
    + 'Are the blatant-offender fixes each individually justified, and are borderline cases FLAGGED not silently retuned?\n'
    + 'A missed multi-form boss or an unjustified retune = NO-GO.\n'
    + '(4d) ENDLESS HUNT: decode um_toxeus_hunt_99 (+ siblings) from the built arz - skeleton mesh from a confirmed-clean\n'
    + 'asset (NOT the green-glow class), race matches the Toxeus family, blood-hound summons GONE, the replacement summon\n'
    + 'chain passes the A9 render-chain + castability gates end-to-end (walk the spawn chain yourself), his 4 b98 skills +\n'
    + 'endless-pursuit byte-intact.  A dead summon or a green-class mesh = NO-GO.\n'
    + '(4e) KILL-CHAIN (ruling 6): walk EVERY link yourself on the built arz - Hunt loot contains the EoAT formula at the\n'
    + 'stated chance on ALL difficulties; the forge recipe resolves (ingredients exist + obtainable, output = the EoAT soul);\n'
    + 'the EoAT soul grants a castable summon whose pet passes A9; the Hunt WIELDS the spear (equip chance/slot + spear-stance\n'
    + 'clips resolved in his rig - the frozen-thrown lesson class); the Hunt\'s own soul summons the Hunt (pet chain walked,\n'
    + 'permanent-pet + Pet.tpl laws honored). ANY dead link = NO-GO.\n'
    + '(4f) TIERED SOULS: re-measure the Toxeus-family soul tiers on the built arz yourself - n/e/l summon strictly increasing,\n'
    + 'Epic/Legendary meaningfully stronger (challenge the numbers vs the uber band), mechanism safe per the Pet.tpl/dtype\n'
    + 'lessons (no Monster-field-on-Pet.tpl crash class, no clone_record-for-souls, dtypes preserved - decode the actual\n'
    + 'written values for INT/FLOAT corruption); mod-wide extension FLAGGED not implemented. A dtype-corrupted pet stat or a\n'
    + 'tier that summons an identical pet = NO-GO.\n'
    + '(4g) +ALL-SKILLS (ruling 6e): decode each Toxeus-family soul tier item - Normal carries exactly +1 all skills, Epic +2,\n'
    + 'Legendary +3, via the field base-game +all-skills items provably use (compare against a real base item\'s bytes),\n'
    + 'correct dtype (decode the written value), visible on the item tooltip surface (Text if needed). Wrong field, wrong\n'
    + 'dtype, or wrong number on any tier = NO-GO.\n'
    + '(4h) CHESTS (ruling 7a): decode the reverted stash chests\' loot chains on the built arz AND the ORIGINAL SV 0.98i arz\n'
    + 'yourself - the after-state must match original-SV richness (walk the tables, compare drop counts/tiers); the revert\n'
    + 'scope = the uber stash chests ONLY (general R-240 world-loot trim intact - spot-check 2-3 non-stash tables unchanged);\n'
    + 'ledger amendments present on R-240/R-242. A stash still nerfed, or collateral un-trimming of world loot = NO-GO.\n'
    + '(4i) SPAWNS (rulings 7b/7c): decode the chest-area pack proxy per-difficulty - Devourer 100% on ALL THREE difficulties;\n'
    + 'decode the parchment-area pool - Devourer at 33%, Enslaver ABSENT there, and the Enslaver\'s ledger-correct spawns\n'
    + 'elsewhere intact. Wrong variant or wrong difficulty coverage = NO-GO.\n'
    + '(4j) ENSLAVER (ruling 8): verify NO stat/skill change landed on any Enslaver record (record-diff must show zero\n'
    + 'Enslaver deltas beyond the soul-item work of rulings 6d/6e) and the ledger note + measured reflect/heal/HP data is\n'
    + 'recorded. An uncommanded Enslaver nerf = NO-GO.\n'
    + '(5) record-diff = ONLY intended, couplings honored, gates/contracts green, negatives fire; (6) rulings verbatim +\n'
    + 'docs honest; (7) DONE vs claims. Return verdict GO/NO-GO, issues (severity + command), summary.',
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
  commit: impl && impl.commit_sha, arz_md5: impl && impl.arz_md5, changes: impl && impl.changes,
  done: impl && impl.done, not_done: impl && impl.not_done,
  vet: verdict && verdict.summary, open_issues: (verdict && verdict.issues) || [] }
