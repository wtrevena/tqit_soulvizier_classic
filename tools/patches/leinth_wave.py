r"""leinth_wave - b94 PART B: Leinth, the Blood Witch, becomes a real wall, gains
an HONOUR GUARD mirroring the one amgoz1/DRX gave Hades, and has the two poison
rigs DRX staged for her finally wired in - every donor a PROVEN, already-shipping
record from her OWN cult family (records\drxcreatures\bloodwitch\...).

WILL'S ASK (paraphrase; the verbatim ruling is ledgered as R-73 in
docs/WILL_RULINGS.md): Leinth is too easy and her fight is one long attrition
sludge with nothing to react to. Make her stronger and give her more to do.

⭐ ROUND 3 - WILL'S ANSWERS 2026-07-27 SUPERSEDE PARTS OF R-73 (ledgered R-76)
------------------------------------------------------------------------------
Round 1 asked Will four design questions and proposed answers. He answered, and on
three of them he went AGAINST the recommendation. His answers are law; this round
implements them, including where they reverse round 1.

  Q4 "how much stronger?"  -> "lets give her some guardians like amgoz1 gave hades"
     So the PRIMARY strengthening is an HONOUR GUARD, not stat inflation. Round 1's
     modest stat work is KEPT (it is not inflation and it still makes sense beside
     guardians); she is deliberately NOT pushed to uber charLevel 100 - he did not
     ask for that, and R-73's reasoning against it stands.

  Q6 "the two staged poison rigs?" -> "Use them AND remove her poison weakness"
     Round 1 REJECTED them as off-identity (poison rigs on the one poison-weak
     boss). Will's answer removes the contradiction from the other end. Both rigs
     are now wired AND defensivePoison goes -15 -> +15. She becomes a coherent
     poison/blood witch instead of a poison-weak one.

  Q7 "cut the ugly swarm?"  -> "Keep the swarm as-is"
     Round 1 cut leinth_summon_uglies from petBurstSpawn 4;6;8 / petLimit 16 to
     2;3;4 / petLimit 6 + a 45s TTL, on the b76 density law. That cut is REVERTED
     IN FULL: this module now writes NOTHING to that skill, so it keeps its shipped
     values by construction, and verify() PINS them so no later writer can cut them.
     The b76 density risk is real and is MEASURED + FLAGGED rather than silently
     mitigated - see THE ENTITY BUDGET below and the wave report.

  Q9 "no-kill exit fallback?" -> "yes" (PART C, tools/build_quest_files.py)

HOW AMGOZ1/DRX BUILT HADES' GUARDIANS (studied in the shipped bytes, then mirrored)
----------------------------------------------------------------------------------
Traced end to end in the deployed arz:
  records\xpack\quests\proxies\main\xq06_boss_hades_champions.dbr   (FileDescription
  "DRX") is a SEPARATE proxy from the boss proxy xq06_boss_hades.dbr. It carries the
  GUARD's own mesh (gigantes01_quest.msh @ scale 2.8), shares the boss's
  hadesdifficulty_01 / bosslimit_all, quest=1, and points at
  records\xpack\quests\proxies\pools\xq06_boss_hades_champion_pool.dbr (also "DRX"):
  spawnMin=spawnMax=1, championMax=1, limit1=1, name1 = the DRX dishonor-guard
  gigantes records\drxcreatures\drxdishonorguard\anapaest_45.dbr, weight1=100.
  A placement census over all 2,282 levels finds that champion proxy placed exactly
  TWICE, both in XPack\Levels\Area08_HadesPalace\HadesPalace_Floor05_04.lvl.
  So the pattern is: ONE dedicated elite guard record, spawned from its OWN pool,
  standing beside the boss, TWO of them, and INVISIBLE to the boss's own quest proxy.

MIRRORED FOR LEINTH - AND DELIBERATELY WITHOUT A MAP CHANGE
-----------------------------------------------------------
The literal Hades route needs two new PLACEMENTS in bossfight.lvl, i.e. a Levels.arc
rebuild. This repo already ships a DB-only equivalent whose donor is LITERALLY
LEINTH'S OWN POOL: apply_svc_patches._svc_boss_pool, "the 1-boss + 2-guaranteed-
champion recipe (spawnMax=3 / championChance=100 / championMin=Max=2 -> 3-2=1
guaranteed boss; the LAW)", used in shipping content by neferkha (2 frozen tomb
guardians), diadochi (2 strider guards) and the Hades Marshal (2 machae escorts),
and paired with _svc_neutralize_pool_equation so the literal counts survive the
inherited proxyPoolEquation. Applying that LAW to q_leinth_lone itself yields
EXACTLY 1 Leinth (still randomly one of her three variants, weights and limits
untouched) + 2 guaranteed honour guards, with Levels.arc BYTE-UNCHANGED.

  THE TWO GUARDS (her own cult, amgoz1 bar: zero new art/FX/sound):
    svc_leinth_guard_reaver   <- d_reaver_42   (tagBWreaver, Champion, God, scale
        1.75, melinoe_bloodburst + bloodboil + sux2buwave + zap; NO summons at all)
    svc_leinth_guard_disciple <- c_disciple_42 (tagBWdisciple, Champion, God, the
        bloodstare + blood-rain caster, disciple_aura)
  Both raised to HER level band [47,62,74], given honour-guard life, a small scale
  bump so they read as elite, and real names. The Disciple's inherited
  disciple_summon_bloodbeast has petLimit 4 and NO TTL - the exact b76 defect - so
  the guard gets a CLONED copy capped with a finite TTL (the four_generals
  "finite TTL (quest-safe)" precedent); the shared original is never touched.

  EXIT-TRIGGER INTERACTION (deliberate, not incidental): the guards ride in
  q_leinth_lone, which is exactly the pool PART C's primary
  Condition_KillAllCreaturesFromProxy watches. So the primary now needs the whole
  honour guard dead, which is the RIGHT reading ("kill the guard and the mistress,
  the sanctuary opens") AND is precisely why PART C's three per-variant
  Condition_KillCreature fallbacks plus the new no-kill fallback are load-bearing.

THE TWO STAGED POISON RIGS - AND THE FREE WIN INSIDE THEM
---------------------------------------------------------
DRX left THREE records staged in her own folder, all with ZERO referrers anywhere
in the 51,098-record db (verified by exact-path scan, not substring):
    leinth_skills\cerberus_acidpuddle_summon.dbr   Skill_AttackProjectileSpawnPet,
        ground-targeted, petBurstSpawn 1, petLimit 10, TTL 6s, skillMaxLevel 3
    leinth_skills\cerberus_acidpuddle_monster.dbr  the puddle entity
    leinth_skills\cerberus_acidpuddle_attack.dbr   Skill_BuffAttackRadiusDuration,
        offensiveSlowPoisonMin 825/1122/900 + 5% current-life from index 3
The free win: the "attack" rig is NOT a boss self-buff needing its own scarce cast
slot - it is the PUDDLE's own aura (the xpack twin is wired at the puddle monster's
initialSkillName + skillName1). So wiring the SUMMON alone brings BOTH of Will's
rigs live through ONE specialAttack slot. This module therefore also repoints her
staged summon at HER staged monster (DRX left it aimed at the xpack copy) and that
monster at HER staged attack, so the whole chain is self-contained in her folder and
the xpack Cerberus chain (boss_cerberus_40/42/44, specialAttack3) stays byte-clean.

THE ONE FREE ATTACK SLOT, AND WHO WINS IT
-----------------------------------------
Monster records expose five castable specialAttack slots (census over the deployed
arz: 3169/1607/899/300/170 users; the only three specialAttack6 users in the whole
db are Pet.tpl records from our own prior wave, so slot 6 is NOT a Monster
precedent). Leinth's four bespoke DRX specials (bloodboil, summon_uglies,
bloodall_02, heatseeker) hold slots 1-4, and the retirement protocol forbids
displacing them. That leaves exactly ONE free attack slot, and round 1 spent it on
CRIMSON TITHE - an invention of mine. Will's explicit instruction outranks my
invention, so:
    specialAttack5 -> cerberus_acidpuddle_summon   (WILL'S ASK)
    CRIMSON TITHE  -> dyingSkillName               (re-homed, not dropped)
dyingSkillName is a well-precedented home for its class: 79 shipping records carry a
Skill_AttackProjectileAreaEffect there. As her death-throe it still lands the
telegraphed moment R-73 wanted, at the instant the exit opens.

NOTE numAttackSlots stays 4, and ROUND 2 CORRECTS ROUND 1'S CENSUS. Round 1 claimed
"46 shipping records run numAttackSlots=4 with five wired specials (and 3 with
six)"; the vet could not reproduce 46 and neither can I. The re-measured truth,
straight from the deployed arz: 170 records carry a non-empty specialAttack5, split
numAttackSlots 4 -> 76 and numAttackSlots 6 -> 94. Of the 76 at numAttackSlots=4:
62 Pet.tpl, 12 Monster.tpl, 1 Hades.tpl, 1 Megalesios.tpl. The 12 Monster.tpl
include the base-game em_monolith_45 (five wired), the mod's boss_coldworm50 and
boss_dagon_66 (five wired each) and - decisively - HER OWN CULT'S
b_seductress_39/41/43. So a numAttackSlots=4 Monster with a wired slot 5 is shipped
precedent inside her own family. The structural proof is stronger than the census
either way: numAttackSlots is defined in Templates/character.tpl beside
numDefenseSlots and combatManagerRecord (defaultValue 4) - a combat positional-slot
count, NOT a special-attack cap - while specialAttack5SkillName and dyingSkillName
are both defined in templates/templatebase/monsterskillmanager.tpl, so the engine
reads slot 5 and the dying slot regardless.

ROUND 2: THE CAST-ABORT SWEEP (why round 1 was a NO-GO, and what it cost)
-------------------------------------------------------------------------
An independent vet proved that round 1's headline addition never fires: the staged
acid summon carries skillSpecialAnimationName='AcidPuddle', a token absent from
every row of her animation table, and hard-law #2 (SkillManager::StartSkill aborts a
cast whose special anim the caster's table cannot start - the law that killed
Meteor/Thunderball/Bonespire) aborts it. It also proved the Voice's TTL-capped
bloodbeast was a LEVEL-0 summon (cast-wired, but in no skillName slot anywhere in
the db). Neither round-1 gate asserted either law, so both shipped.
Round 2 therefore does not just fix those two: it adds BOTH laws as roster-wide
invariants (_cast_abort_violations + _level_zero_violations over all five records
this wave writes, following charAnimationTableName), and running them turned up
THREE MORE dead abilities nobody had noticed:
    q_leinth_*           specialAttack1 melinoe_bloodboil 'BloodBoil'  UNBOUND
    svc_leinth_guard_reaver specialAttack1 melinoe_bloodboil 'BloodBoil' UNBOUND
    svc_leinth_guard_reaver specialAttack3 reaver_zap      'Zappity'    UNBOUND
Blood Boil is HER SIGNATURE AoE life-leech - the skill her own soul is built around
- and it has never fired in this mod. That is a direct, measurable cause of Will's
"she is too easy, the fight is one long attrition sludge" (R-73), and fixing it is
worth more to the encounter than any stat on the list below. All five are now
castable; both shared donors (melinoe_bloodboil: 20 records; reaver_zap: 3) are
CLONED, never written, so no other creature's behaviour moves by one byte.

TWO ROUND-1 SKILLS ARE RETIRED (retirement protocol, stated not silent)
-----------------------------------------------------------------------
R-73 names CHOIR OF THE BLOODBORN and SANGUINE MIRE, so retiring them requires an
explicit ledger entry - this is it (R-76 supersedes that half of R-73). Both were
MY OWN round-1 inventions, authored on this unmerged branch and never shipped to
Will or seen in game, so no player-facing content is being taken away:
  * CHOIR summoned discipleboss_bladedancer pets to give her cult bodies. The
    HONOUR GUARD is Will's own answer to that exact need and does it better (named,
    elite, guaranteed, standing with her from the first second).
  * SANGUINE MIRE existed solely because she had no zone control. The acid puddle
    is the authentic DRX-staged rig for that job.
Retiring them is also the ONLY density lever available that touches NOTHING Will
told me to keep. Their records are simply never authored this round.

THE ENTITY BUDGET (Will asked for this number; it is a FLAGGED RISK)
--------------------------------------------------------------------
RE-MEASURED IN ROUND 2 against the deployed arz, per the vet's instruction that
Will must not rule on a phantom. Every line below is read from the record, and
every summon is confirmed CAST-WIRED (a rig in a skillName slot that nothing casts
contributes zero - hero_flesheater, petLimit 4, sits in skillName4 on Leinth AND on
the Reaver and is cast by neither, so it is correctly excluded).
Worst case, at petLimit saturation:
    1  Leinth
    2  honour guards
   16  summoned_ugly            PERMANENT (no TTL) - Will: keep as-is
   10  leinth_heatseeker_pet    PERMANENT (no TTL) - her shipped DRX kit
   10  acid puddles             transient, 6s TTL   <- REAL only after the r2 fix
    2  guard bloodbeasts        transient, 20s TTL  <- REAL only after the r2 fix
   = 41 concurrent, of which 26 are PERMANENT summons (+ the 3 bodies).
HONEST DELTA: the figure is numerically the same as round 1's, but round 1's was a
phantom - the 10 puddles could not spawn (cast abort) and the 2 bloodbeasts were
level-0, so what round 1 would ACTUALLY have shipped is 29 concurrent / 26
permanent. Round 2 makes the 41 real, and the permanent half is unchanged at 26
either way, because both of the newly-live rigs are the TTL-capped ones.
The b76 chumbi-freeze RCA measures the standalone offender (um_voranthys_99) at 25
PERMANENT summons (petLimit 9 + 8 + 8) and states that even standing alone that
"degrades over a long fight". Leinth's 26 permanent EXCEEDS it, and she now also
peaks 12 transient bodies on top. Nothing Will told me to keep has been reduced;
this is reported, not silently fixed. See the wave report.

STATS (all three variants; the deliberate no-touch list is below)

GROUND TRUTH (deployed arz, all three variants)
-----------------------------------------------
q_leinth_47 (charLevel 47;62;74), q_leinth_49 (49;64;76), q_leinth_50 (50;65;75);
all monsterClassification=Boss. Her passives ALREADY cap her where it does not
matter: skill14 zpassive_resists_bleedvitleechconvert_x10plvl @10 gives +100
bleed / +100 life / +100 convert / +100 life-leech / +100 mana-leech, and skill15
elementalresistance_10xlevel @3 gives +30 elemental. Net effective: bleed 100,
life 160, convert 100, elemental 50, stun 100 - and PHYSICAL 10, PIERCE 20,
POISON -15. Physical and pierce are the ONLY things that touch her, which is
exactly why a weapon build melts her while a caster respects her.

WHAT THIS MODULE CHANGES
------------------------
STATS (all three variants; the deliberate no-touch list is below)
  characterLife         32,481 -> 52,000 | 35,703 -> 57,000 | 38,924 -> 62,000 (+60%)
  defensivePhysical     10 -> 35    <- THE REAL LEVER
  defensivePierce       20 -> 45    <- THE REAL LEVER
  defensivePoison      -15 -> +15   <- WILL Q6: "remove her poison weakness"
  characterAttackSpeed  0.8 -> 1.0  (her casts actually land; still under the
                                     champions' 1.1)
  characterRunSpeed     1.0 -> 1.15 (she can reposition; far under the Enslaver's 1.5)
  characterLifeRegen    2 -> 10     (a life-leech witch should visibly heal)

  KIT (round 2 - these, not the stats, are what the fight will feel):
  specialAttack1        melinoe_bloodboil -> svc_leinth_bloodboil (a castable copy).
                        Her signature AoE life-leech FIRES FOR THE FIRST TIME.
  specialAttack5        cerberus_acidpuddle_summon, anim 'AcidPuddle' -> 'SpitSummon'
                        (WILL Q6; round 1 wired it but it aborted on cast)
  dyingSkillName        Crimson Tithe (unchanged from round 1)
  skillLevel13          NOT TOUCHED, deliberately. Round 1 raised cerberus_crackfire
                        1;4;7 -> 4;7;9 and reported "poison 800/850/950 and the 5%
                        current-life component ON at every difficulty" as delivered.
                        It is not: the skill has NO cast mechanism (skillName13
                        only) and demands the token 'Roar', which anm_leinth does
                        not bind. It is dormant twice over, there is no free
                        Monster-precedented cast slot left to give it, and the raise
                        changed nothing in play. The slot now keeps its shipped
                        value and verify() PINS it. Registered as debt.

  WHY +15 AND NOT 0 OR 100 (Will said "remove the weakness", not "make her immune").
  +15 is not invented: it is EXACTLY the value her own cult's heavy carries
  (d_reaver_42 defensivePoison = 15), so she is anchored to her family's norm rather
  than to a number I chose. It removes the weakness decisively (she no longer takes
  bonus poison damage) and makes her coherent now that she wields BOTH the geysers
  and the acid puddles. It is deliberately NOT immunity: at +15 poison remains by
  far her SOFTEST resist (bleed 100 / life 160 / convert 100 / elemental 50 /
  stun 100), so the counter-play R-73 valued survives in relative terms while the
  weakness itself is gone. It also stays far below the Enslaver's 100, so the
  mid-boss-must-not-out-stat-the-uber ordering invariant still holds.

  DELIBERATELY NOT TOUCHED: charLevel stays 47-76. She is the blood cave's
  main-path terminal boss, NOT an uber; pushing her to the champions' 100 would
  break the cave's curve and step on their role, and Will did not ask for it.

  DELIBERATELY NOT TOUCHED: leinth_summon_uglies. Will: "Keep the swarm as-is".
  This module writes NOTHING to that record; verify() pins petBurstSpawn [4,6,8],
  petLimit 16 and the absence of a TTL so no later writer can quietly cut it.

WHAT THIS MODULE DOES NOT TOUCH
-------------------------------
No loot field of any kind: chanceToEquipHead (her guaranteed lenithsveil),
chanceToEquipFinger2 (her 66% soul, the R-42 PLACED rate), every loot*Item* field
and treasureProxyName are snapshotted before and after and apply() fails loud if
any of them moved. No pool, no proxy, no placement, no map, no quest.

GATE
----
verify() runs in registry step 4 over the FINAL merged db and fails the build loud
unless: every stat target holds on all three variants; defensivePoison is the NEW
non-negative value and is NOT immunity; the ugly swarm is untouched at its shipped
[4,6,8]/16/no-TTL (Will's "as-is"); both staged acid rigs are live and chained to
HER copies; the xpack Cerberus acid chain is unmoved; Crimson Tithe is wired at
dyingSkillName; the two honour guards exist at her level band and the pool spawns
EXACTLY 1 main + 2 guaranteed champions under the _svc_boss_pool LAW; every summon
this module authors carries a finite TTL; her drop wiring is untouched; and she
still ranks BELOW the Enslaver on resists/speed.

ROUND 2 ADDS THE FOUR ASSERTIONS WHOSE ABSENCE MADE ROUND 1 A NO-GO:
  * the acid summon's skillSpecialAnimationName is the BOUND token, not DRX's
    unbound 'AcidPuddle' (HIGH-1);
  * the Voice's capped bloodbeast occupies skillName4 at level >= 1, not just a
    cast field (HIGH-2, the b39 "level-0 summon never fires" law);
  * Blood Boil is the castable clone in BOTH halves on all four casters, and both
    SHARED donors still carry their original tokens (nothing upstream moved);
  * ROSTER-WIDE: 0 cast-aborting and 0 level-0 slots across all five records this
    wave writes, evaluated by following charAnimationTableName.
Planted negative tests: tools/debug/negtest_leinth_wave.py (27 subtests).
See docs/reports/b94_leinth_wave.md.
"""
import apply_svc_patches as asp

MODULE_NAME = ("Leinth the Blood Witch - honour guard + staged poison rigs + buff "
               "(R-73, R-76)")

_BW = 'records\\drxcreatures\\bloodwitch\\'
_LS = _BW + 'skills\\leinth_skills\\'
_BWS = _BW + 'skills\\'

VARIANTS = (
    _BW + 'q_leinth_47.dbr',
    _BW + 'q_leinth_49.dbr',
    _BW + 'q_leinth_50.dbr',
)

# The Enslaver: the uber Leinth must never out-stat (ordering invariant).
_ENSLAVER = asp._EN_BOSS

# ── STAT TARGETS ─────────────────────────────────────────────────────────────
LIFE = {
    VARIANTS[0]: 52000.0,   # was 32,481.26
    VARIANTS[1]: 57000.0,   # was 35,702.52
    VARIANTS[2]: 62000.0,   # was 38,923.78
}
PHYS = 35.0          # was 10  <- the real lever
PIERCE = 45.0        # was 20  <- the real lever
ATTACK_SPEED = 1.0   # was 0.8 (champions sit at 1.1)
RUN_SPEED = 1.15     # was 1.0 (Enslaver sits at 1.5)
LIFE_REGEN = 10.0    # was 2

# WILL Q6 2026-07-27: "Use them AND remove her poison weakness".
# +15 == her own cult heavy d_reaver_42's defensivePoison (family norm, not an
# invented number). Removes the weakness without granting immunity: poison stays
# her SOFTEST resist by a wide margin, so the counter-play survives.
POISON = 15.0        # was -15 (R-73 kept it; R-76 supersedes)
POISON_WAS = -15.0
POISON_IMMUNE_FLOOR = 100.0   # verify(): must stay strictly below immunity

# ── cerberus_crackfire, her poison geysers - ROUND 2: DORMANT, NOT DELIVERED ──
# Round 1 raised skillLevel13 from the shipped [1,4,7] to [4,7,9] and R-73/R-76 +
# the module docstring stated "poison 800/850/950 and the 5% current-life
# component ON at every difficulty" as a delivered buff. The vet proved that is
# false, and re-measuring against the deployed arz confirms it TWICE OVER:
#   1. NO CAST MECHANISM. cerberus_crackfire sits ONLY in skillName13 on the three
#      variants - no specialAttackN, no buffSelf, no dying, no initial. The
#      original boss_cerberus_40/42/44 wire it at BOTH skillName4 AND
#      specialAttack4SkillName (chance 25, delay 12, AnyRange); tools/patches/
#      boss_skill_fix.py classifies exactly this shape as a "dormant kit slot".
#   2. ITS ANIM TOKEN IS UNBOUND. skillSpecialAnimationName='Roar' is bound by 72
#      records DB-wide - anm_leinth is not one of them - so even wired it would
#      abort under hard-law #2.
# It cannot be delivered inside this wave's budget either: all five castable
# specialAttack slots are now spoken for (1 bloodboil, 2 uglies, 3 bloodall_02,
# 4 heatseeker, 5 Will's acid rig) and the retirement protocol forbids displacing
# her four bespoke DRX specials; slot 6 has NO Monster precedent (its only three
# users DB-wide are Pet.tpl records from our own prior wave).
# So this module now writes NOTHING to skillLevel13 - it keeps its shipped value
# by construction - and verify() PINS it, so nobody can raise an inert number
# again and believe they shipped a buff. Registered as debt for a future wave.
GEYSER_SLOT = 13
GEYSER_LEVELS_SHIPPED = [1, 4, 7]   # PINNED: dormant, must not be "raised"
GEYSER_SKILL = _LS + 'cerberus_crackfire.dbr'
GEYSER_ANIM = 'Roar'                # unbound in anm_leinth (part of why it is dead)

# ── THE UGLY SWARM - WILL SAID KEEP AS-IS, SO THIS MODULE NEVER WRITES IT ────
# Values read from the pre-wave baseline arz (1c27d5fa). verify() PINS them.
UGLIES = _LS + 'leinth_summon_uglies.dbr'
UGLIES_BURST = [4, 6, 8]       # shipped; round 1 cut this to [2,3,4] - REVERTED
UGLIES_LIMIT = 16              # shipped; round 1 cut this to 6 - REVERTED
UGLIES_TTL_MUST_BE_ABSENT = True   # round 1 added 45s - REVERTED (Will: "as-is")

# ── WILL Q6: the two staged poison rigs DRX left unwired in HER folder ───────
# All three have ZERO referrers in the whole db (exact-path scan), so wiring them
# cannot disturb anything. The xpack twins stay untouched (Cerberus uses those).
ACID_SUMMON = _LS + 'cerberus_acidpuddle_summon.dbr'   # Skill_AttackProjectileSpawnPet
ACID_MONSTER = _LS + 'cerberus_acidpuddle_monster.dbr'  # the puddle entity
ACID_ATTACK = _LS + 'cerberus_acidpuddle_attack.dbr'    # the puddle's poison aura
ACID_SLOT = 9                  # skillName slot (was Crimson Tithe's in round 1)
ACID_LEVELS = [1, 2, 3]        # donor skillMaxLevel is 3
ACID_SPECIAL = '5'             # THE one free attack slot - Will's ask wins it
ACID_CHANCE = 100.0            # matches her four existing specials
ACID_LEVEL1 = [1, 2, 3]        # the puddle monster's own skillLevel1 on the aura
# ROUND 2 FIX (the vet's HIGH-1). DRX left her staged copy carrying
# skillSpecialAnimationName='AcidPuddle', a token owned ONLY by the xpack Cerberus
# chain + the DRX Bastien records. It is absent from EVERY row of her own table
# anm_leinth (unarmed row: SpitSummon, 2, BloodBall01, SummonTormentedSouls,
# TelekinesisLoop, TelekinesisEnd, ThunderClap), and her three variants carry no
# own *SpecialAnimRef. By this repo's disasm-derived hard-law #2 (SkillManager::
# StartSkill aborts a cast whose skillSpecialAnimationName the caster's table
# cannot start - the law that killed Meteor/Thunderball/Bonespire) the cast
# ABORTED, so round 1's "acid rig LIVE" was false and BOTH of Will's staged rigs
# died with it (the aura only exists on the spawned puddle).
# The token is repointed at 'SpitSummon', which is NOT an invention: DRX bound it
# themselves at anm_leinth unarmedSpecialAnimRef1 ->
# XPack\Creatures\monster\empusa\anm\empusa_staff_skill_frostspit.anm and then
# left it referenced by NO skill of hers - staged in the same breath as the acid
# rig they also left unwired. It is semantically a spit-summon, and unlike ''
# (the Meteor/Thunderball remedy, which falls back to the default attack anim) it
# gives the fight the visible telegraph R-73 asked for.
ACID_ANIM = 'SpitSummon'
ACID_ANIM_WAS = 'AcidPuddle'
# The xpack originals: proven byte-unchanged by verify() (Cerberus depends on them).
ACID_XPACK_SUMMON = r'records\xpack\skills\bossskills\cerberus_acidpuddle_summon.dbr'
ACID_XPACK_MONSTER = r'records\xpack\skills\bossskills\cerberus_acidpuddle_monster.dbr'
ACID_XPACK_ATTACK = r'records\xpack\skills\bossskills\cerberus_acidpuddle_attack.dbr'

# ── ROUND 2: THE CAST-ABORT SWEEP over everything this wave owns ─────────────
# Running the repo's own anim-binding invariant (the one coldworm_buffs shipped)
# across all five records this wave writes found THREE MORE dead active slots
# beyond the vet's HIGH-1, every one of them a skill the wave advertises:
#   q_leinth_*        specialAttack1 melinoe_bloodboil  'BloodBoil' UNBOUND
#   svc_leinth_guard_reaver specialAttack1 melinoe_bloodboil 'BloodBoil' UNBOUND
#   svc_leinth_guard_reaver specialAttack3 reaver_zap    'Zappity'   UNBOUND
# 'BloodBoil' is bound by exactly 2 records DB-wide (anm_maenad bowSpecialAnimRef7,
# anm_acolyte unarmedSpecialAnimRef1) and 'Zappity' by exactly 1 (little_lued
# unarmedSpecialAnimRef2) - none of them is anm_leinth / anm_seductress_armed.
# So Blood Boil, her SIGNATURE AoE life-leech and the thing that makes her read as
# a blood witch at all, has never fired in this mod. That is a direct cause of
# Will's "she is too easy / one long attrition sludge" (R-73).
# BOTH donors are SHARED (melinoe_bloodboil: 20 records incl. every bloodwitch,
# leucothea and d_reaver; reaver_zap: d_reaver_40/41/42), so they are CLONED and
# only THIS WAVE'S records are repointed - zero blast radius, upstream untouched.
# The replacement token is 'ThunderClap', chosen because it is bound in ALL SIX
# weapon rows (bow/dHanded/sHanded/spear/staff/unarmed) of anm_leinth AND
# anm_seductress_armed AND anm_seductress, so it is castable whatever stance the
# engine picks - the strongest binding available, and stronger than '' because it
# still animates the burst.
GUARD_ANIM_TOKEN = 'ThunderClap'
BLOODBOIL_DONOR = r'records\xpack\skills\monsterskills\activeattackradius\melinoe_bloodboil.dbr'
BLOODBOIL = _BWS + 'svc_leinth_bloodboil.dbr'
BLOODBOIL_WAS_ANIM = 'BloodBoil'
BLOODBOIL_SLOT = 2             # skillName2 on BOTH Leinth and the reaver (donor's own slot)
BLOODBOIL_SPECIAL = ''         # specialAttack1 on both
ZAP_DONOR = _BWS + 'reaver_zap.dbr'
ZAP = _BWS + 'svc_leinth_guard_zap.dbr'
ZAP_WAS_ANIM = 'Zappity'
ZAP_SLOT = 6                   # skillName6 on the reaver (donor's own slot)
ZAP_SPECIAL = '3'              # specialAttack3 on the reaver

# ── CRIMSON TITHE - kept, but re-homed to make room for Will's acid rig ──────
TITHE = _LS + 'svc_leinth_crimson_tithe.dbr'
TITHE_DONOR = _BWS + 'disciple_bloodrain_bleedx50_vitx10.dbr'
TITHE_SLOT = 16                # moved off slot 9 (the acid rig takes it)
TITHE_LEVELS = [8, 14, 20]
TITHE_FIELD = 'dyingSkillName'  # 79 shipping records carry this CLASS here
# RETIRED this round (R-76, stated not silent): svc_leinth_choir_bloodborn and
# svc_leinth_sanguine_mire. Both were round-1 inventions on this unmerged branch,
# never shipped to Will; the honour guard and the acid puddle are Will's own
# answers to the exact needs those two were invented for. They are simply never
# authored, so no record is deleted from any shipped db.

NEW_SKILLS = (TITHE, BLOODBOIL, ZAP)

# ── WILL Q4: THE HONOUR GUARD (the amgoz1/DRX Hades mirror) ──────────────────
GUARD_REAVER = _BW + 'svc_leinth_guard_reaver.dbr'
GUARD_REAVER_DONOR = _BW + 'd_reaver_42.dbr'      # her cult's heavy; NO summons
GUARD_DISCIPLE = _BW + 'svc_leinth_guard_disciple.dbr'
GUARD_DISCIPLE_DONOR = _BW + 'c_disciple_42.dbr'  # her cult's caster
GUARDS = (GUARD_REAVER, GUARD_DISCIPLE)
GUARD_LEVEL = [47, 62, 74]          # HER band (q_leinth_47's charLevel)
GUARD_LIFE = {GUARD_REAVER: 7800.0, GUARD_DISCIPLE: 5200.0}  # ~2x their donors
GUARD_SCALE = {GUARD_REAVER: 1.9, GUARD_DISCIPLE: 1.9}       # donors sit at 1.75
GUARD_RANK = 'Champion'             # the anapaest/Hades-guard rank
# The Disciple donor's inherited bloodbeast summon is petLimit 4 with NO TTL - the
# exact b76 defect. The guard gets a CLONED, capped copy; the shared original is
# never touched (four_generals "finite TTL (quest-safe)" precedent).
GUARD_BEAST_SKILL = _BWS + 'svc_leinth_guard_bloodbeast.dbr'
GUARD_BEAST_DONOR = _BWS + 'disciple_summon_bloodbeast.dbr'
GUARD_BEAST_LIMIT = 2
GUARD_BEAST_TTL = 20.0
GUARD_BEAST_SPECIAL = ''            # specialAttack1 on c_disciple_42
# ROUND 2 FIX (the vet's HIGH-2). Round 1 wrote the capped CLONE into
# specialAttackSkillName but left skillName4 holding the SHARED, uncapped donor -
# so the clone had exactly ONE referrer in the whole 51,103-record db (that
# specialAttack field) and NO skillName slot, i.e. NO skillLevel, i.e. it was a
# LEVEL-0 SUMMON. tools/patches/boss_skill_fix.py states the b39 RCA law
# verbatim: "a level-0 summon NEVER fires ... an unambiguous boss never summons
# defect". The Voice of the Bloodborn therefore lost her whole summon kit and the
# advertised petLimit 2 / TTL 20s cap was moot. The fix is to repoint the DONOR'S
# OWN SLOT (skillName4) at the clone, keeping the donor's own level ladder
# [5,10,15] - one field, no new slot, and the shared donor is still never written.
GUARD_BEAST_SLOT = 4
GUARD_BEAST_LEVELS = [5, 10, 15]    # c_disciple_42's own skillLevel4

# The pool + the LAW (apply_svc_patches._svc_boss_pool): spawnMin=spawnMax=3,
# championChance=100, championMin=championMax=2 -> 3-2 = 1 guaranteed main.
LEINTH_POOL = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
POOL_SPAWN = 3
POOL_CHAMPION_CHANCE = 100.0
POOL_CHAMPION_MIN = 2
POOL_CHAMPION_MAX = 2

# ── Text (player-surface checklist: every new surface gets a real name + flavour) ─
TAGS = {
    'tagSVCLeinthCrimsonTithe': 'Crimson Tithe',
    'tagSVCLeinthCrimsonTitheDESC':
        'The Blood Witch calls in the cave\'s debt. Her sanctuary weeps red, and '
        'everything beneath the rain is opened, slowed and made to bleed.',
    'tagSVCLeinthAcidMire': 'Sanguine Mire',
    'tagSVCLeinthAcidMireDESC':
        'She spits the cave\'s own bile across the floor. What it touches keeps '
        'rotting long after she has turned away.',
    'tagSVCLeinthGuardReaver': 'Blood Reaver of the Sanctuary',
    'tagSVCLeinthGuardDisciple': 'Voice of the Bloodborn',
}

# ── the drop fields that MUST NOT move (scope proof) ────────────────────────
_DROP_PREFIXES = ('chanceToEquip', 'loot', 'treasureProxyName', 'dropItems')

# ── ROUND 2: the CAST-ABORT / LEVEL-0 gate surface ──────────────────────────
# Every field on a Monster record that makes the engine actually START a skill.
# (attack/initial/dying/buffSelf + the five castable specialAttack slots; slot 6
# is included defensively so a future writer cannot smuggle a skill past the gate,
# even though no Monster in the db uses it.)
_CAST_FIELDS = (['attackSkillName', 'initialSkillName', 'dyingSkillName',
                 'buffSelfSkillName'] +
                ['specialAttack%sSkillName' % s for s in ('', '2', '3', '4', '5', '6')])


def _v1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _fields(db, rec):
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], list(tf.values))
    return out


def _drop_snapshot(db, recs):
    snap = {}
    for r in recs:
        ff = _fields(db, r)
        snap[r] = {k: v for k, v in ff.items()
                   if any(k.startswith(p) for p in _DROP_PREFIXES)}
    return snap


def _require(db, rec, what):
    if not db.has_record(rec):
        raise SystemExit(
            "[leinth_wave] %s MISSING from the db: %s. Refusing to ship a build "
            "that silently drops this wave." % (what, rec))


def _clone_new(db, donor, dest, label):
    _require(db, donor, 'donor rig (%s)' % label)
    if db.has_record(dest):
        raise SystemExit(
            "[leinth_wave] %s already exists (%s) - another writer claimed this "
            "path. Refusing to overwrite." % (dest, label))
    db.clone_record(donor, dest)


def _free_slot(db, rec, slot, label):
    cur = _v1(db, rec, 'skillName%d' % slot)
    if isinstance(cur, str) and cur.strip():
        raise SystemExit(
            "[leinth_wave] %s: skillName%d is NOT free (holds %r) - %s would "
            "silently displace an existing skill." % (rec, slot, cur, label))


# ═════════════════════════════════════════════════════════════════════════════
# ROUND 2: the two invariants the round-1 gates did not assert, which is exactly
# why two dead headline abilities shipped past them.
# ═════════════════════════════════════════════════════════════════════════════
def _bound_anim_tokens(db, rec):
    r"""Every special-anim token `rec` can actually START -> its .anm file.

    A monster may declare `unarmedSpecialAnimRef<i>` on ITSELF, but Leinth and
    both guards declare none and instead point `charAnimationTableName` at a
    shared table (anm_leinth / anm_seductress / anm_seductress_armed). The engine
    resolves the caster's playable animations through that table, so the gate
    MUST follow it - checking the monster record alone (which is all the coldworm
    gate needed) finds nothing and passes everything.
    """
    import re as _re
    out = {}
    for src in (rec, _v1(db, rec, 'charAnimationTableName')):
        if not isinstance(src, str) or not src.strip() or not db.has_record(src):
            continue
        for key, tf in (db.get_fields(src) or {}).items():
            m = _re.match(r'(\w+?)SpecialAnimRef(\d+)$', key.split('###')[0])
            if not m or not tf.values:
                continue
            name = str(tf.values[0] or '').strip()
            if not name:
                continue
            anim = str(_v1(db, src, '%sSpecialAnim%s' % (m.group(1), m.group(2))) or '')
            if not out.get(name):
                out[name] = anim
    return out


def _cast_abort_violations(db, rec):
    r"""HARD-LAW #2, monster side: SkillManager::StartSkill ABORTS a cast whose
    `skillSpecialAnimationName` the caster's animation table cannot start.

    This is the law that killed Meteor ('MeteorShower'), Thunderball ('Ensnare')
    and Bonespire ('BoneSpire') on the player side, and it is the law round 1
    walked straight into on the monster side with 'AcidPuddle'.
    """
    problems = []
    bound = _bound_anim_tokens(db, rec)
    label = rec.rsplit('\\', 1)[-1]
    for field in _CAST_FIELDS:
        path = _v1(db, rec, field)
        path = str(path).strip() if isinstance(path, str) else ''
        if not path or path == '0':
            continue
        if not db.has_record(path):
            problems.append("%s: %s -> %s does NOT resolve (dead slot)"
                            % (label, field, path))
            continue
        tok = _v1(db, path, 'skillSpecialAnimationName')
        tok = str(tok).strip() if isinstance(tok, str) else ''
        if not tok:
            continue                      # empty = the always-castable default anim
        if tok not in bound:
            problems.append(
                "%s: %s -> %s demands special animation %r, which the caster's "
                "table (%s) does NOT bind (bound: %s). Hard-law #2: the cast "
                "ABORTS, so this ability never fires."
                % (label, field, path.rsplit('\\', 1)[-1], tok,
                   str(_v1(db, rec, 'charAnimationTableName') or rec).rsplit('\\', 1)[-1],
                   sorted(bound)))
        elif not bound[tok].strip():
            problems.append(
                "%s: %s -> %s demands special animation %r whose bound "
                "*SpecialAnim slot is EMPTY - no playable animation"
                % (label, field, path.rsplit('\\', 1)[-1], tok))
    return problems


def _level_zero_violations(db, rec):
    r"""THE b39 RCA LAW (tools/patches/boss_skill_fix.py, verbatim): "a level-0
    summon NEVER fires ... an unambiguous boss never summons defect".

    Every skill a record is wired to CAST must also occupy a `skillName<i>` slot
    with `skillLevel<i>` >= 1, or it has no level at all. Round 1 wrote the
    capped guard bloodbeast into `specialAttackSkillName` and left `skillName4`
    on the shared donor, so the clone had no skillName slot anywhere in the db.
    """
    problems = []
    label = rec.rsplit('\\', 1)[-1]
    ff = db.get_fields(rec) or {}
    kit = {}
    for key, tf in ff.items():
        b = key.split('###')[0]
        if not (b.startswith('skillName') and b[9:].isdigit()) or not tf.values:
            continue
        p = str(tf.values[0] or '').replace('/', '\\').lower()
        if not p:
            continue
        lv = db.get_field_value(rec, 'skillLevel%s' % b[9:])
        lv = lv if isinstance(lv, list) else ([lv] if lv is not None else [])
        try:
            top = max(int(x) for x in lv) if lv else 0
        except (TypeError, ValueError):
            top = 0
        kit[p] = max(kit.get(p, 0), top)
    for field in _CAST_FIELDS:
        path = _v1(db, rec, field)
        path = str(path).strip() if isinstance(path, str) else ''
        if not path or path == '0':
            continue
        key = path.replace('/', '\\').lower()
        if key not in kit:
            problems.append(
                "%s: %s -> %s is CAST but occupies NO skillName slot, so it has "
                "no skillLevel. b39 RCA law: a level-0 skill never fires."
                % (label, field, path.rsplit('\\', 1)[-1]))
        elif kit[key] < 1:
            problems.append(
                "%s: %s -> %s sits in a skillName slot at level 0 - it never fires"
                % (label, field, path.rsplit('\\', 1)[-1]))
    return problems


def _build_castable_clone(db, donor, dest, token, label):
    r"""Clone a SHARED skill and give it an animation token the casters can start.

    The donors here are used by 20 records (melinoe_bloodboil) and 3 (reaver_zap),
    so they are NEVER written; only this wave's own records are repointed at the
    clone. This is the repo's documented Meteor/Thunderball remedy, taken one step
    further: instead of blanking the token (default attack anim, no telegraph) it
    is repointed at a token PROVEN bound in every weapon row of all three tables
    this wave casts from.
    """
    _clone_new(db, donor, dest, label)
    was = _v1(db, donor, 'skillSpecialAnimationName')
    db.set_field(dest, 'skillSpecialAnimationName', token)
    db.set_field(dest, 'FileDescription',
                 'Leinth wave: %s, castable copy - anim %r -> %r so '
                 'SkillManager::StartSkill no longer aborts (b94 r2)'
                 % (label, str(was or ''), token))
    db._modified.add(dest)
    print("    %-28s anim %r -> %r  (shared donor %s left untouched)"
          % (dest.rsplit('\\', 1)[-1], str(was or ''), token,
             donor.rsplit('\\', 1)[-1]))


def _build_honour_guard(db, tags):
    r"""WILL Q4 2026-07-27: "lets give her some guardians like amgoz1 gave hades".

    THE HADES PATTERN, traced in the shipped bytes and mirrored here:
    xq06_boss_hades_champions (a SEPARATE proxy from the boss proxy) -> its own
    pool (spawnMin=spawnMax=1, championMax=1) -> ONE dedicated elite guard record
    (the DRX dishonor-guard anapaest_45), placed TWICE beside Hades and invisible
    to his own quest proxy.

    Mirrored WITHOUT a map change by using this repo's own DB-side escort LAW,
    apply_svc_patches._svc_boss_pool, whose donor is literally q_leinth_lone:
    spawnMin=spawnMax=3 + championChance=100 + championMin=championMax=2 gives
    3 - 2 = 1 guaranteed main + 2 guaranteed champions. Her three variant name
    slots, their weights and their limits are ALL left exactly as shipped, so the
    single main is still a random one of q_leinth_47/49/50.

    _svc_neutralize_pool_equation is MANDATORY here, not optional: her pool
    inherits proxypoolequation_02, which at 1 player scales the literal counts by
    1.357 and floors them -> spawnMax 4, championMax 2 -> 4-2 = TWO Leinths side
    by side. That is the exact documented "two bosses side by side" defect Will
    reported on 2026-07-13, and it is deterministic, not probabilistic.
    """
    sf = db.set_field
    for donor in (GUARD_REAVER_DONOR, GUARD_DISCIPLE_DONOR, GUARD_BEAST_DONOR):
        _require(db, donor, 'honour-guard donor')
    _require(db, LEINTH_POOL, 'her spawn pool')

    # 5a. the Disciple donor's bloodbeast summon is petLimit 4 with NO TTL (the
    #     b76 defect). Clone + cap it; the SHARED original is never written.
    _clone_new(db, GUARD_BEAST_DONOR, GUARD_BEAST_SKILL, 'guard bloodbeast summon')
    sf(GUARD_BEAST_SKILL, 'petLimit', GUARD_BEAST_LIMIT)
    sf(GUARD_BEAST_SKILL, 'spawnObjectsTimeToLive', GUARD_BEAST_TTL)
    sf(GUARD_BEAST_SKILL, 'FileDescription',
       'Leinth honour guard: bloodbeast summon, TTL-capped (b76 law) (b94)')
    db._modified.add(GUARD_BEAST_SKILL)

    # 5b. the two named guards, cloned from her OWN cult
    for guard, donor, tag in ((GUARD_REAVER, GUARD_REAVER_DONOR, 'tagSVCLeinthGuardReaver'),
                              (GUARD_DISCIPLE, GUARD_DISCIPLE_DONOR, 'tagSVCLeinthGuardDisciple')):
        _clone_new(db, donor, guard, 'honour guard')
        sf(guard, 'description', tag)
        sf(guard, 'monsterClassification', GUARD_RANK)
        sf(guard, 'charLevel', list(GUARD_LEVEL))
        sf(guard, 'characterLife', GUARD_LIFE[guard])
        sf(guard, 'scale', GUARD_SCALE[guard])
        sf(guard, 'FileDescription',
           'Leinth honour guard (Will Q4: guardians like amgoz1 gave Hades) (b94)')
        # Don't inherit the donor's DANGLING loot refs. d_reaver_42 carries
        # lootMisc1Item1/2 -> drxitem\loottables\weapons\wands\0{1,2,3}_wand.dbr and
        # lootFinger2Item3 -> an x-disabled u_wand, none of which exist in the db
        # (contracts C-RES-DBR-1 + MONSTER-SKILLS-LOOT already flag the donor P2).
        # Cloning them verbatim would ADD two brand-new violations for a slot that
        # rolls nothing anyway, so the clone drops them. The SHARED donor is left
        # exactly as it is - fixing upstream DRX debt is a separate lane.
        for dead in ('lootMisc1Item1', 'lootMisc1Item2', 'lootFinger2Item3'):
            cur = db.get_field_value(guard, dead)
            cur = [cur] if isinstance(cur, str) else (cur or [])
            if any(isinstance(p, str) and p and not db.has_record(p) for p in cur):
                sf(guard, dead, [])
        db._modified.add(guard)
    # 5b-ii. THE VOICE KEEPS HER SUMMON, BUT THE CAPPED COPY - IN BOTH PLACES.
    # ROUND 2 (the vet's HIGH-2): round 1 wrote the clone into the CAST field only
    # and left skillName4 on the shared donor, so the clone had no skillLevel
    # anywhere in the db = a level-0 summon = the b39 "boss never summons" defect,
    # and the whole advertised petLimit-2 / TTL-20s cap was moot. Both halves are
    # now written together, at the donor's own [5,10,15] ladder.
    sf(GUARD_DISCIPLE, 'specialAttack%sSkillName' % GUARD_BEAST_SPECIAL, GUARD_BEAST_SKILL)
    cur_slot = _v1(db, GUARD_DISCIPLE, 'skillName%d' % GUARD_BEAST_SLOT)
    if not isinstance(cur_slot, str) or 'summon_bloodbeast' not in cur_slot.lower():
        raise SystemExit(
            "[leinth_wave] %s: skillName%d holds %r, expected the donor's own "
            "bloodbeast summon - refusing to repoint the wrong slot."
            % (GUARD_DISCIPLE, GUARD_BEAST_SLOT, cur_slot))
    sf(GUARD_DISCIPLE, 'skillName%d' % GUARD_BEAST_SLOT, GUARD_BEAST_SKILL)
    sf(GUARD_DISCIPLE, 'skillLevel%d' % GUARD_BEAST_SLOT, list(GUARD_BEAST_LEVELS))
    db._modified.add(GUARD_DISCIPLE)
    print("    the Voice's bloodbeast: skillName%d %s -> the CAPPED clone @ %s "
          "(round 1 left it level-0: cast-wired but in NO skillName slot)"
          % (GUARD_BEAST_SLOT, cur_slot.rsplit('\\', 1)[-1], GUARD_BEAST_LEVELS))

    # 5b-iii. THE REAVER'S TWO DEAD SLOTS (round 2, same law as HIGH-1).
    # d_reaver_42 shipped specialAttack1 -> melinoe_bloodboil ('BloodBoil') and
    # specialAttack3 -> reaver_zap ('Zappity'), and NEITHER token is bound in
    # anm_seductress_armed. So half of the honour guard's advertised kit could
    # never fire. Both are repointed at castable clones; the shared donors
    # (20 records / 3 records) are never written, so d_reaver_40/41/42 and every
    # bloodwitch keep their exact shipped behaviour.
    sf(GUARD_REAVER, 'skillName%d' % BLOODBOIL_SLOT, BLOODBOIL)
    sf(GUARD_REAVER, 'specialAttack%sSkillName' % BLOODBOIL_SPECIAL, BLOODBOIL)
    sf(GUARD_REAVER, 'skillName%d' % ZAP_SLOT, ZAP)
    sf(GUARD_REAVER, 'specialAttack%sSkillName' % ZAP_SPECIAL, ZAP)
    db._modified.add(GUARD_REAVER)
    print("    the Reaver: Blood Boil (specialAttack1) + reaver_zap "
          "(specialAttack3) repointed at castable clones - both were "
          "cast-aborting on unbound %r / %r" % (BLOODBOIL_WAS_ANIM, ZAP_WAS_ANIM))

    # 5c. the LAW, applied to her own pool IN PLACE (variants/weights/limits kept)
    before = (_v1(db, LEINTH_POOL, 'spawnMin'), _v1(db, LEINTH_POOL, 'spawnMax'),
              _v1(db, LEINTH_POOL, 'nameChampion1'), _v1(db, LEINTH_POOL, 'championMax'))
    sf(LEINTH_POOL, 'nameChampion1', GUARD_REAVER)
    sf(LEINTH_POOL, 'nameChampion2', GUARD_DISCIPLE)
    sf(LEINTH_POOL, 'nameChampion3', '')
    sf(LEINTH_POOL, 'weightChampion1', 50)
    sf(LEINTH_POOL, 'weightChampion2', 50)
    sf(LEINTH_POOL, 'weightChampion3', 0)
    sf(LEINTH_POOL, 'spawnMin', POOL_SPAWN)
    sf(LEINTH_POOL, 'spawnMax', POOL_SPAWN)
    sf(LEINTH_POOL, 'championChance', POOL_CHAMPION_CHANCE)
    sf(LEINTH_POOL, 'championMin', POOL_CHAMPION_MIN)
    sf(LEINTH_POOL, 'championMax', POOL_CHAMPION_MAX)
    sf(LEINTH_POOL, 'FileDescription',
       'Leinth (1 of 3 variants) + her 2-guard honour guard (b94, R-76)')
    asp._svc_neutralize_pool_equation(db, LEINTH_POOL)
    db._modified.add(LEINTH_POOL)
    print("  honour guard: 2 named cult champions at her band %s; pool spawn "
          "%s/%s -> %d/%d, champions %s -> %s+%s @ %d/%d, equation NEUTRALIZED "
          "(without it the engine floors 3*1.357 -> 4 mains-2 = TWO Leinths)"
          % (GUARD_LEVEL, before[0], before[1], POOL_SPAWN, POOL_SPAWN,
             (before[2] or '').rsplit('\\', 1)[-1],
             GUARD_REAVER.rsplit('\\', 1)[-1], GUARD_DISCIPLE.rsplit('\\', 1)[-1],
             POOL_CHAMPION_MIN, POOL_CHAMPION_MAX))


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    for v in VARIANTS:
        _require(db, v, 'Leinth variant')
    _require(db, GEYSER_SKILL, 'her geyser skill')
    _require(db, UGLIES, 'her ugly-summon skill')

    drops_before = _drop_snapshot(db, VARIANTS)

    # ── 1. Crimson Tithe (kept from round 1, re-homed to dyingSkillName) ────
    _clone_new(db, TITHE_DONOR, TITHE, 'Crimson Tithe')
    db.set_field(TITHE, 'skillDisplayName', 'tagSVCLeinthCrimsonTithe')
    db.set_field(TITHE, 'skillBaseDescription', 'tagSVCLeinthCrimsonTitheDESC')
    db.set_field(TITHE, 'FileDescription',
                 'Leinth: the Bloodborn blood-rain, promoted from her cult Disciple (b94)')
    db._modified.add(TITHE)

    for k, v in TAGS.items():
        tags[k] = v
    print("  authored Crimson Tithe + %d Text tags (Choir + Mire RETIRED this "
          "round - the honour guard and the acid puddle are Will's own answers "
          "to what they were invented for)" % len(TAGS))

    # ── 2. WILL Q6: wire DRX's two staged poison rigs, chained to HER copies ─
    _require(db, ACID_SUMMON, 'her staged acid-puddle summon')
    _require(db, ACID_MONSTER, 'her staged acid-puddle monster')
    _require(db, ACID_ATTACK, 'her staged acid-puddle attack')
    # DRX aimed her summon at the XPACK puddle and her puddle at the XPACK aura.
    # Re-chain both onto HER copies so the rig is self-contained and the Cerberus
    # chain (boss_cerberus_40/42/44) keeps its own records byte-clean.
    db.set_field(ACID_SUMMON, 'spawnObjects', [ACID_MONSTER])
    db.set_field(ACID_SUMMON, 'skillDisplayName', 'tagSVCLeinthAcidMire')
    db.set_field(ACID_SUMMON, 'skillBaseDescription', 'tagSVCLeinthAcidMireDESC')
    # ROUND 2, THE FIX THAT MAKES IT ACTUALLY FIRE. See ACID_ANIM above: DRX left
    # this staged copy demanding 'AcidPuddle', a token absent from EVERY row of
    # anm_leinth, so hard-law #2 aborted the cast and round 1's "acid rig LIVE"
    # was false. Her own table binds 'SpitSummon' (unarmedSpecialAnimRef1 ->
    # empusa_staff_skill_frostspit.anm) and NO skill of hers uses it - DRX staged
    # the animation and the rig together and wired neither.
    _acid_was = _v1(db, ACID_SUMMON, 'skillSpecialAnimationName')
    db.set_field(ACID_SUMMON, 'skillSpecialAnimationName', ACID_ANIM)
    db.set_field(ACID_SUMMON, 'FileDescription',
                 'Leinth: the acid rig DRX staged for her, finally wired AND '
                 'castable (Will Q6, b94 r2)')
    db._modified.add(ACID_SUMMON)
    db.set_field(ACID_MONSTER, 'initialSkillName', ACID_ATTACK)
    db.set_field(ACID_MONSTER, 'skillName1', ACID_ATTACK)
    db.set_field(ACID_MONSTER, 'skillLevel1', list(ACID_LEVEL1))
    db._modified.add(ACID_MONSTER)
    print("  acid rig CHAINED: %s -> %s -> %s (all three had ZERO referrers; the "
          "xpack Cerberus copies are untouched)"
          % (ACID_SUMMON.rsplit('\\', 1)[-1], ACID_MONSTER.rsplit('\\', 1)[-1],
             ACID_ATTACK.rsplit('\\', 1)[-1]))
    print("  acid rig CASTABLE: skillSpecialAnimationName %r -> %r (round 1 left "
          "the DRX token, which anm_leinth does not bind -> StartSkill aborted "
          "and BOTH staged rigs were dead)" % (str(_acid_was or ''), ACID_ANIM))

    # ── 2b. ROUND 2: the same law, swept across the rest of the wave's kit ───
    # Blood Boil is her SIGNATURE AoE life-leech and it has never fired in this
    # mod: melinoe_bloodboil demands 'BloodBoil', bound DB-wide by exactly two
    # records (anm_maenad, anm_acolyte) and by neither anm_leinth nor
    # anm_seductress_armed. The donor is shared by 20 records, so it is CLONED.
    _build_castable_clone(db, BLOODBOIL_DONOR, BLOODBOIL, GUARD_ANIM_TOKEN,
                          'Blood Boil')
    _build_castable_clone(db, ZAP_DONOR, ZAP, GUARD_ANIM_TOKEN, 'the Reaver zap')

    # ── 3. WILL Q7: the ugly swarm is NOT touched. Prove it stayed as shipped. ─
    _ugl = (db.get_field_value(UGLIES, 'petBurstSpawn'),
            _v1(db, UGLIES, 'petLimit'), _v1(db, UGLIES, 'spawnObjectsTimeToLive'))
    print("  leinth_summon_uglies UNTOUCHED (Will: \"keep the swarm as-is\"): "
          "petBurstSpawn=%s petLimit=%s TTL=%s - round 1's cut is REVERTED"
          % (_ugl[0], _ugl[1], _ugl[2]))

    # ── 4. per-variant stats + kit wiring ───────────────────────────────────
    for rec in VARIANTS:
        before = (_v1(db, rec, 'characterLife'), _v1(db, rec, 'defensivePhysical'),
                  _v1(db, rec, 'defensivePierce'), _v1(db, rec, 'defensivePoison'))

        db.set_field(rec, 'characterLife', LIFE[rec])
        db.set_field(rec, 'defensivePhysical', PHYS)
        db.set_field(rec, 'defensivePierce', PIERCE)
        db.set_field(rec, 'defensivePoison', POISON)      # WILL Q6
        db.set_field(rec, 'characterAttackSpeed', ATTACK_SPEED)
        db.set_field(rec, 'characterRunSpeed', RUN_SPEED)
        db.set_field(rec, 'characterLifeRegen', LIFE_REGEN)

        # ROUND 2: her geysers are NOT raised. cerberus_crackfire sits in
        # skillName13 with NO cast mechanism AND demands the unbound token 'Roar',
        # so it is DORMANT twice over and round 1's [1,4,7] -> [4,7,9] raise
        # changed nothing in play while being reported as a delivered buff. This
        # module now writes nothing to the slot; verify() PINS it at its shipped
        # value so the inert number cannot be "raised" again.
        cur_geyser = _v1(db, rec, 'skillName%d' % GEYSER_SLOT)
        if not isinstance(cur_geyser, str) or 'cerberus_crackfire' not in cur_geyser.lower():
            raise SystemExit(
                "[leinth_wave] %s: skillName%d is %r, expected cerberus_crackfire "
                "- her geyser slot moved." % (rec, GEYSER_SLOT, cur_geyser))
        prev_g = db.get_field_value(rec, 'skillLevel%d' % GEYSER_SLOT)

        # ROUND 2: her SIGNATURE Blood Boil, made castable. specialAttack1 and
        # skillName2 are repointed TOGETHER (the HIGH-2 lesson: a cast field
        # without its skillName slot is a level-0 skill), keeping the donor's own
        # levels, which the loop below asserts are untouched.
        _bb_lv = db.get_field_value(rec, 'skillLevel%d' % BLOODBOIL_SLOT)
        cur_bb = _v1(db, rec, 'skillName%d' % BLOODBOIL_SLOT)
        if not isinstance(cur_bb, str) or 'melinoe_bloodboil' not in cur_bb.lower():
            raise SystemExit(
                "[leinth_wave] %s: skillName%d is %r, expected melinoe_bloodboil "
                "- refusing to repoint the wrong slot." % (rec, BLOODBOIL_SLOT, cur_bb))
        db.set_field(rec, 'skillName%d' % BLOODBOIL_SLOT, BLOODBOIL)
        db.set_field(rec, 'specialAttack%sSkillName' % BLOODBOIL_SPECIAL, BLOODBOIL)

        # the two additions, each into a PROVEN-FREE kit slot
        for slot, skill, levels, label in (
                (ACID_SLOT, ACID_SUMMON, ACID_LEVELS, 'Sanguine Mire (acid rig)'),
                (TITHE_SLOT, TITHE, TITHE_LEVELS, 'Crimson Tithe')):
            _free_slot(db, rec, slot, label)
            db.set_field(rec, 'skillName%d' % slot, skill)
            db.set_field(rec, 'skillLevel%d' % slot, list(levels))

        # cast wiring: WILL'S acid rig takes THE one free attack slot; Crimson
        # Tithe moves to dyingSkillName (79 shipping records carry its class there).
        if _v1(db, rec, 'specialAttack%sSkillName' % ACID_SPECIAL):
            raise SystemExit(
                "[leinth_wave] %s: specialAttack%s is already taken - the acid "
                "rig would displace it." % (rec, ACID_SPECIAL))
        db.set_field(rec, 'specialAttack%sSkillName' % ACID_SPECIAL, ACID_SUMMON)
        db.set_field(rec, 'specialAttack%sChance' % ACID_SPECIAL, ACID_CHANCE)
        cur = _v1(db, rec, TITHE_FIELD)
        if isinstance(cur, str) and cur.strip():
            raise SystemExit(
                "[leinth_wave] %s: %s already holds %r - Crimson Tithe would "
                "displace it." % (rec, TITHE_FIELD, cur))
        db.set_field(rec, TITHE_FIELD, TITHE)

        db._modified.add(rec)
        print("  %s: life %s -> %g | phys %s -> %g | pierce %s -> %g | poison "
              "%s -> %g | geysers %s UNTOUCHED (dormant: no cast slot + unbound "
              "%r) | Blood Boil -> castable clone @ specialAttack1 + slot %d %s "
              "| acid rig @ specialAttack%s (slot %d) | Crimson Tithe @ %s (slot %d)"
              % (rec.rsplit('\\', 1)[-1], before[0], LIFE[rec], before[1], PHYS,
                 before[2], PIERCE, before[3], POISON, prev_g, GEYSER_ANIM,
                 BLOODBOIL_SLOT, _bb_lv, ACID_SPECIAL, ACID_SLOT,
                 TITHE_FIELD, TITHE_SLOT))

    # ── 5. WILL Q4: THE HONOUR GUARD (the amgoz1/DRX Hades mirror) ──────────
    _build_honour_guard(db, tags)

    # ── SCOPE PROOF: not one loot field moved ───────────────────────────────
    drops_after = _drop_snapshot(db, VARIANTS)
    if drops_after != drops_before:
        moved = []
        for r in VARIANTS:
            for k in sorted(set(drops_before[r]) | set(drops_after[r])):
                if drops_before[r].get(k) != drops_after[r].get(k):
                    moved.append('%s.%s' % (r.rsplit('\\', 1)[-1], k))
        raise SystemExit(
            "[leinth_wave] DROP SCOPE VIOLATION: %s moved. This module must never "
            "touch her 100%% lenithsveil head drop, her 66%% soul (R-42 PLACED "
            "rate) or her chest proxy." % moved)
    print("  scope proof: 0 of %d loot/drop fields moved across the 3 variants "
          "(veil 100%%, soul 66%%, bosschestproxy_leinth all intact)"
          % sum(len(v) for v in drops_before.values()))

    # ── ROUND 2 SCOPE PROOF #2: not one cast-aborting or level-0 slot survives ─
    # (the module-local run; verify() re-runs it over the FINAL merged db)
    live = []
    for rec in list(VARIANTS) + list(GUARDS):
        bad = _cast_abort_violations(db, rec) + _level_zero_violations(db, rec)
        if bad:
            raise SystemExit("[leinth_wave] CAST-ABORT/LEVEL-0 VIOLATION:\n  - "
                             + "\n  - ".join(bad))
        live.append(sum(1 for f in _CAST_FIELDS
                        if isinstance(_v1(db, rec, f), str) and _v1(db, rec, f).strip()))
    print("  castability proof: %d cast-wired slots across the 3 variants + 2 "
          "guards, 0 aborting on an unbound animation, 0 at level 0 "
          "(round 1 shipped 5 dead: acid x3, Reaver bloodboil + zap, and the "
          "Voice's level-0 bloodbeast)" % sum(live))


# =============================================================================
# GATE (registry step 4 - runs over the FINAL merged db)
# =============================================================================
def _kit_level(db, rec, skill):
    """The skillLevel array of `skill` in a skillName slot on `rec`, or None."""
    ff = db.get_fields(rec) or {}
    low = skill.lower()
    for k, tf in ff.items():
        b = k.split('###')[0]
        if not (b.startswith('skillName') and b[9:].isdigit()):
            continue
        if tf.values and str(tf.values[0]).replace('/', '\\').lower() == low:
            return db.get_field_value(rec, 'skillLevel%s' % b[9:])
    return None


def verify(db, tags=None):
    problems = []

    for rec in VARIANTS:
        if not db.has_record(rec):
            problems.append("Leinth variant MISSING from the final db: %s" % rec)
            continue
        label = rec.rsplit('\\', 1)[-1]

        def _num(field):
            v = _v1(db, rec, field)
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        checks = (('characterLife', LIFE[rec]), ('defensivePhysical', PHYS),
                  ('defensivePierce', PIERCE), ('characterAttackSpeed', ATTACK_SPEED),
                  ('characterRunSpeed', RUN_SPEED), ('characterLifeRegen', LIFE_REGEN))
        for field, want in checks:
            got = _num(field)
            if got is None or abs(got - want) > 0.01:
                problems.append("%s: %s=%r, expected %g (a later writer moved it)"
                                % (label, field, got, want))

        # WILL Q6: the weakness is REMOVED - but she must not become immune.
        poison = _num('defensivePoison')
        if poison is None or abs(poison - POISON) > 0.01:
            problems.append(
                "%s: defensivePoison=%r, expected %g - Will 2026-07-27 asked for "
                "the poison WEAKNESS removed (was %g)"
                % (label, poison, POISON, POISON_WAS))
        elif poison < 0:
            problems.append("%s: defensivePoison=%r is still NEGATIVE - the "
                            "weakness Will asked to remove survived" % (label, poison))
        if poison is not None and poison >= POISON_IMMUNE_FLOOR:
            problems.append(
                "%s: defensivePoison=%r reaches immunity - Will said REMOVE the "
                "weakness, not make her poison-proof; the counter-play must survive"
                % (label, poison))

        # she must NOT have been pushed to uber tier
        lv = db.get_field_value(rec, 'charLevel')
        if isinstance(lv, list) and any(int(x) >= 100 for x in lv):
            problems.append("%s: charLevel %s reaches uber tier - she is the blood "
                            "cave's main-path boss, not a Toxeus champion" % (label, lv))

        # ROUND 2: the geysers are DORMANT and must stay EXACTLY as shipped.
        # Raising an inert level is how round 1 came to report a buff that does
        # nothing; this assertion is the reverse of round 1's and fails loud if
        # anyone raises it again without ALSO giving it a cast slot + a bound anim.
        g = db.get_field_value(rec, 'skillLevel%d' % GEYSER_SLOT)
        g = g if isinstance(g, list) else [g]
        if [int(x) for x in g] != GEYSER_LEVELS_SHIPPED:
            problems.append(
                "%s: geyser skillLevel%d=%r, expected the SHIPPED %s. "
                "cerberus_crackfire has NO cast mechanism (skillName%d only - the "
                "original boss_cerberus_40/42/44 also wire it at "
                "specialAttack4SkillName) AND demands the token %r, which "
                "anm_leinth does not bind. Raising it delivers NOTHING; wire it "
                "first, or leave it as shipped."
                % (label, GEYSER_SLOT, g, GEYSER_LEVELS_SHIPPED, GEYSER_SLOT,
                   GEYSER_ANIM))

        # each addition is in a kit slot at level>=1 AND wired to a cast mechanism
        for skill, want_levels, wiring, lbl in (
                (ACID_SUMMON, ACID_LEVELS,
                 ('specialAttack%sSkillName' % ACID_SPECIAL,), 'the acid rig'),
                (TITHE, TITHE_LEVELS, (TITHE_FIELD,), 'Crimson Tithe')):
            lvls = _kit_level(db, rec, skill)
            lvls = lvls if isinstance(lvls, list) else ([lvls] if lvls is not None else [])
            if not lvls or min(int(x) for x in lvls) < 1:
                problems.append("%s: %s is not in a skillName slot at level>=1 "
                                "(levels=%r) - a level-0 skill never fires"
                                % (label, lbl, lvls))
            elif [int(x) for x in lvls] != want_levels:
                problems.append("%s: %s levels %r, expected %s"
                                % (label, lbl, lvls, want_levels))
            for field in wiring:
                got = _v1(db, rec, field)
                if not isinstance(got, str) or got.replace('/', '\\').lower() != skill.lower():
                    problems.append("%s: %s=%r, expected %s (%s would never be "
                                    "cast)" % (label, field, got, skill, lbl))
        ch = _num('specialAttack%sChance' % ACID_SPECIAL)
        if ch is None or ch <= 0:
            problems.append("%s: specialAttack%sChance=%r (<=0 = never cast)"
                            % (label, ACID_SPECIAL, ch))

        # her four ORIGINAL specials must all still be wired (nothing displaced)
        for suf in ('', '2', '3', '4'):
            if not _v1(db, rec, 'specialAttack%sSkillName' % suf):
                problems.append("%s: specialAttack%s lost its skill - this wave "
                                "must be purely additive" % (label, suf or '1'))

        # ROUND 2: Blood Boil, her signature, must be the CASTABLE copy in BOTH
        # halves (cast field + kit slot). Repointing only one half is the exact
        # level-0 defect that killed the Voice's bloodbeast in round 1.
        for field in ('specialAttack%sSkillName' % BLOODBOIL_SPECIAL,
                      'skillName%d' % BLOODBOIL_SLOT):
            got = _v1(db, rec, field)
            if not isinstance(got, str) or got.replace('/', '\\').lower() != BLOODBOIL.lower():
                problems.append(
                    "%s: %s=%r, expected the castable clone %s - the shared "
                    "melinoe_bloodboil demands %r, which anm_leinth does NOT "
                    "bind, so her signature AoE aborts on cast (hard-law #2)"
                    % (label, field, got, BLOODBOIL, BLOODBOIL_WAS_ANIM))

        # drops untouched
        if abs((_num('chanceToEquipHead') or 0) - 100.0) > 0.01:
            problems.append("%s: chanceToEquipHead=%r, expected 100 (lenithsveil)"
                            % (label, _num('chanceToEquipHead')))
        soul = _num('chanceToEquipFinger2')
        if soul is None or soul <= 0:
            problems.append("%s: chanceToEquipFinger2=%r - her soul drop is gone"
                            % (label, soul))
        tp = _v1(db, rec, 'treasureProxyName')
        if not isinstance(tp, str) or 'bosschestproxy_leinth' not in tp.lower():
            problems.append("%s: treasureProxyName=%r - her bespoke chest moved "
                            "(this wave must NOT nerf or repoint it)" % (label, tp))

    # every new skill record exists, resolves and (if a summon) is TTL-capped
    for skill in NEW_SKILLS:
        if not db.has_record(skill):
            problems.append("new skill record MISSING: %s" % skill)
            continue
        cls = _v1(db, skill, 'Class')
        if not cls:
            problems.append("%s has no Class - the clone did not take" % skill)
        if isinstance(cls, str) and 'SpawnPet' in cls:
            ttl = _v1(db, skill, 'spawnObjectsTimeToLive')
            try:
                ttl = float(ttl or 0)
            except (TypeError, ValueError):
                ttl = 0.0
            if ttl <= 0:
                problems.append("%s: summon with no finite spawnObjectsTimeToLive "
                                "(b76 chumbi-freeze law)" % skill)
            lim = _v1(db, skill, 'petLimit')
            try:
                lim = int(lim or 0)
            except (TypeError, ValueError):
                lim = 0
            if lim <= 0 or lim > 8:
                problems.append("%s: petLimit=%r (must be a small positive cap)"
                                % (skill, lim))
            # get_field_value returns the SCALAR for a single-entry array, so this
            # must be normalised to a list before iterating (iterating a bare str
            # would walk its characters).
            spawns = db.get_field_value(skill, 'spawnObjects') or []
            if isinstance(spawns, str):
                spawns = [spawns]
            for p in spawns:
                if isinstance(p, str) and p and not db.has_record(p):
                    problems.append("%s spawns a MISSING record %s" % (skill, p))
                    break
        for tag_field in ('skillDisplayName', 'skillBaseDescription'):
            t = _v1(db, skill, tag_field)
            if isinstance(t, str) and t.startswith('tagSVCLeinth') and tags is not None:
                if t not in tags:
                    problems.append("%s references Text tag %s which the module "
                                    "never added" % (skill, t))

    # WILL Q7 "keep the swarm as-is": the shipped values must be UNCHANGED. This
    # is the reverse of round 1's assertion - it now FAILS if anything cut them.
    if db.has_record(UGLIES):
        burst = db.get_field_value(UGLIES, 'petBurstSpawn')
        burst = burst if isinstance(burst, list) else [burst]
        lim = _v1(db, UGLIES, 'petLimit')
        ttl = _v1(db, UGLIES, 'spawnObjectsTimeToLive')
        if [int(x) for x in burst] != UGLIES_BURST:
            problems.append(
                "leinth_summon_uglies petBurstSpawn=%r, expected the SHIPPED %s - "
                "Will 2026-07-27: \"Keep the swarm as-is\"" % (burst, UGLIES_BURST))
        if int(lim or 0) != UGLIES_LIMIT:
            problems.append(
                "leinth_summon_uglies petLimit=%r, expected the SHIPPED %d - Will "
                "2026-07-27: \"Keep the swarm as-is\"" % (lim, UGLIES_LIMIT))
        if UGLIES_TTL_MUST_BE_ABSENT and float(ttl or 0) > 0:
            problems.append(
                "leinth_summon_uglies gained spawnObjectsTimeToLive=%r - the swarm "
                "shipped PERMANENT and Will said keep it as-is. The b76 density "
                "risk is REPORTED in the wave report, not silently patched." % ttl)
    else:
        problems.append("leinth_summon_uglies MISSING - her specialAttack2 is dead")

    # ── WILL Q6: both staged acid rigs live, chained to HER copies ───────────
    for r, what in ((ACID_SUMMON, 'acid summon'), (ACID_MONSTER, 'acid puddle'),
                    (ACID_ATTACK, 'acid aura')):
        if not db.has_record(r):
            problems.append("%s MISSING: %s" % (what, r))
    if db.has_record(ACID_SUMMON):
        sp = db.get_field_value(ACID_SUMMON, 'spawnObjects') or []
        sp = [sp] if isinstance(sp, str) else sp
        if not sp or any(str(p).replace('/', '\\').lower() != ACID_MONSTER.lower()
                         for p in sp if p):
            problems.append(
                "the acid summon spawns %r, expected HER staged puddle %s (DRX left "
                "it aimed at the xpack copy)" % (sp, ACID_MONSTER))
    if db.has_record(ACID_SUMMON):
        # ROUND 2, THE HIGH-1 ASSERTION. Round 1 wired the rig and declared it
        # LIVE without ever checking the one field that decides whether the cast
        # starts at all. This is that check, stated as a hard target so it can
        # never regress to the DRX token silently.
        tok = _v1(db, ACID_SUMMON, 'skillSpecialAnimationName')
        tok = str(tok).strip() if isinstance(tok, str) else ''
        if tok != ACID_ANIM:
            problems.append(
                "her acid summon's skillSpecialAnimationName=%r, expected %r. DRX "
                "shipped it as %r, a token owned only by the xpack Cerberus chain "
                "and the DRX Bastien records and absent from EVERY row of "
                "anm_leinth - SkillManager::StartSkill ABORTS the cast (hard-law "
                "#2, the Meteor/Thunderball/Bonespire law), so BOTH of Will's "
                "staged rigs die (the aura lives only on the spawned puddle)."
                % (tok, ACID_ANIM, ACID_ANIM_WAS))
    if db.has_record(ACID_MONSTER):
        for f in ('initialSkillName', 'skillName1'):
            got = _v1(db, ACID_MONSTER, f)
            if not isinstance(got, str) or got.replace('/', '\\').lower() != ACID_ATTACK.lower():
                problems.append(
                    "her acid puddle's %s=%r, expected HER staged aura %s - without "
                    "it Will's second staged rig is still dead" % (f, got, ACID_ATTACK))
    # the xpack Cerberus chain must be untouched (boss_cerberus_40/42/44 use it)
    _xp_summon_spawn = db.get_field_value(ACID_XPACK_SUMMON, 'spawnObjects') or []
    _xp_summon_spawn = ([_xp_summon_spawn] if isinstance(_xp_summon_spawn, str)
                        else _xp_summon_spawn)
    if any(str(p).replace('/', '\\').lower() == ACID_MONSTER.lower()
           for p in _xp_summon_spawn if p):
        problems.append(
            "the XPACK acid summon was repointed at Leinth's puddle - Cerberus "
            "shares that record; this wave must not move it")
    _xp_aura = _v1(db, ACID_XPACK_MONSTER, 'skillName1')
    if isinstance(_xp_aura, str) and _xp_aura.replace('/', '\\').lower() == ACID_ATTACK.lower():
        problems.append(
            "the XPACK acid puddle was repointed at Leinth's aura - Cerberus "
            "shares that record; this wave must not move it")

    # ── WILL Q4: THE HONOUR GUARD ───────────────────────────────────────────
    for guard in GUARDS:
        if not db.has_record(guard):
            problems.append("honour guard MISSING from the final db: %s" % guard)
            continue
        gl = guard.rsplit('\\', 1)[-1]
        lv = db.get_field_value(guard, 'charLevel')
        lv = lv if isinstance(lv, list) else [lv]
        if [int(x) for x in lv if x is not None] != GUARD_LEVEL:
            problems.append("%s: charLevel %r, expected HER band %s (a guard off "
                            "her band is either free XP or a wall)" % (gl, lv, GUARD_LEVEL))
        rank = _v1(db, guard, 'monsterClassification')
        if rank != GUARD_RANK:
            problems.append("%s: monsterClassification=%r, expected %r (the pool's "
                            "champion slots only accept champions)" % (gl, rank, GUARD_RANK))
        desc = _v1(db, guard, 'description')
        if not isinstance(desc, str) or not desc.startswith('tagSVCLeinthGuard'):
            problems.append("%s: description=%r - an unnamed guard shows a raw tag "
                            "or the donor's name (player-surface checklist)" % (gl, desc))
        elif tags is not None and desc not in tags:
            problems.append("%s references Text tag %s which the module never added"
                            % (gl, desc))
        # no uncapped summon may ride in on the clone (b76)
        for suf in ('', '2', '3', '4', '5'):
            sk = _v1(db, guard, 'specialAttack%sSkillName' % suf)
            if not isinstance(sk, str) or not sk.strip() or not db.has_record(sk):
                continue
            if 'SpawnPet' not in str(_v1(db, sk, 'Class') or ''):
                continue
            if not (float(_v1(db, sk, 'spawnObjectsTimeToLive') or 0) > 0):
                problems.append(
                    "%s: specialAttack%s %s is a summon with NO finite TTL (b76 "
                    "chumbi-freeze law) - clone and cap it instead"
                    % (gl, suf or '1', sk.rsplit('\\', 1)[-1]))
    # the SHARED donor summon must be untouched (other cult disciples use it)
    if db.has_record(GUARD_BEAST_DONOR) and float(
            _v1(db, GUARD_BEAST_DONOR, 'spawnObjectsTimeToLive') or 0) > 0:
        problems.append(
            "the SHARED disciple_summon_bloodbeast gained a TTL - this wave must "
            "cap its own CLONE, never the record the cult's disciples share")

    # ── ROUND 2, THE HIGH-2 ASSERTION: the Voice's summon must have a LEVEL ───
    # Round 1 checked the clone's TTL but never its level, so a summon that can
    # never fire passed a gate whose whole subject is that summon.
    if db.has_record(GUARD_DISCIPLE):
        got = _v1(db, GUARD_DISCIPLE, 'skillName%d' % GUARD_BEAST_SLOT)
        if not isinstance(got, str) or got.replace('/', '\\').lower() != GUARD_BEAST_SKILL.lower():
            problems.append(
                "svc_leinth_guard_disciple: skillName%d=%r, expected the CAPPED "
                "clone %s. Without it the clone has no skillLevel anywhere in the "
                "db - the b39 RCA law: \"a level-0 summon NEVER fires ... an "
                "unambiguous boss never summons defect\"."
                % (GUARD_BEAST_SLOT, got, GUARD_BEAST_SKILL))
        gl_lv = db.get_field_value(GUARD_DISCIPLE, 'skillLevel%d' % GUARD_BEAST_SLOT)
        gl_lv = gl_lv if isinstance(gl_lv, list) else ([gl_lv] if gl_lv is not None else [])
        if not gl_lv or min(int(x) for x in gl_lv) < 1:
            problems.append(
                "svc_leinth_guard_disciple: skillLevel%d=%r - the honour guard's "
                "summon is at level 0 and never fires" % (GUARD_BEAST_SLOT, gl_lv))
        # the Reaver's two repointed slots
        for field, want, lbl in (
                ('specialAttack%sSkillName' % BLOODBOIL_SPECIAL, BLOODBOIL, 'Blood Boil'),
                ('skillName%d' % BLOODBOIL_SLOT, BLOODBOIL, 'Blood Boil'),
                ('specialAttack%sSkillName' % ZAP_SPECIAL, ZAP, 'the Reaver zap'),
                ('skillName%d' % ZAP_SLOT, ZAP, 'the Reaver zap')):
            got = _v1(db, GUARD_REAVER, field)
            if not isinstance(got, str) or got.replace('/', '\\').lower() != want.lower():
                problems.append(
                    "svc_leinth_guard_reaver: %s=%r, expected the castable clone "
                    "%s (%s aborted on an unbound animation as the donor shipped it)"
                    % (field, got, want, lbl))

    # ── ROUND 2, THE ROSTER-WIDE SWEEP (the invariant round 1 never had) ─────
    # Hard-law #2 + the b39 level-0 law, applied to EVERY cast-wired slot on
    # every record this wave writes. Round 1 shipped FIVE dead abilities past its
    # own gates because neither law was asserted anywhere.
    for rec in list(VARIANTS) + list(GUARDS):
        if db.has_record(rec):
            problems.extend(_cast_abort_violations(db, rec))
            problems.extend(_level_zero_violations(db, rec))

    # the SHARED donors of the two castable clones must be byte-untouched
    for donor, was in ((BLOODBOIL_DONOR, BLOODBOIL_WAS_ANIM), (ZAP_DONOR, ZAP_WAS_ANIM)):
        if db.has_record(donor):
            tok = _v1(db, donor, 'skillSpecialAnimationName')
            if str(tok or '') != was:
                problems.append(
                    "the SHARED donor %s had its animation token rewritten (%r, "
                    "was %r) - 20 bloodwitch/leucothea/d_reaver records depend on "
                    "it; this wave must only ever repoint its OWN clones"
                    % (donor.rsplit('\\', 1)[-1], tok, was))

    # the pool: EXACTLY 1 main + 2 guaranteed champions, equation neutralized
    if not db.has_record(LEINTH_POOL):
        problems.append("her spawn pool MISSING: %s" % LEINTH_POOL)
    else:
        def _p(f):
            v = _v1(db, LEINTH_POOL, f)
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        smin, smax = _p('spawnMin'), _p('spawnMax')
        cmin, cmax = _p('championMin'), _p('championMax')
        cch = _p('championChance')
        for f, got, want in (('spawnMin', smin, POOL_SPAWN), ('spawnMax', smax, POOL_SPAWN),
                             ('championMin', cmin, POOL_CHAMPION_MIN),
                             ('championMax', cmax, POOL_CHAMPION_MAX),
                             ('championChance', cch, POOL_CHAMPION_CHANCE)):
            if got is None or abs(got - want) > 0.01:
                problems.append("q_leinth_lone pool: %s=%r, expected %g (the "
                                "_svc_boss_pool escort LAW)" % (f, got, want))
        # THE LAW: spawnMax - championMax must be exactly 1 (one Leinth, never two)
        if smax is not None and cmax is not None and abs((smax - cmax) - 1.0) > 0.01:
            problems.append(
                "q_leinth_lone pool: spawnMax(%r) - championMax(%r) = %r, MUST be 1 "
                "- anything else spawns two Leinths side by side" % (smax, cmax, smax - cmax))
        # the equation MUST be neutralized or the engine floors 3*1.357 -> 2 mains
        eq = _v1(db, LEINTH_POOL, 'proxyPoolEquation')
        if isinstance(eq, str) and eq.strip():
            problems.append(
                "q_leinth_lone pool still carries proxyPoolEquation=%r - it scales "
                "the literal counts by 1.357 and floors them, yielding TWO Leinths "
                "(the documented 2026-07-13 \"two bosses side by side\" defect)" % eq)
        # the champion slots hold OUR guards and nothing stale
        for i, guard in enumerate(GUARDS, start=1):
            got = _v1(db, LEINTH_POOL, 'nameChampion%d' % i)
            if not isinstance(got, str) or got.replace('/', '\\').lower() != guard.lower():
                problems.append("q_leinth_lone pool: nameChampion%d=%r, expected %s"
                                % (i, got, guard))
        stale = _v1(db, LEINTH_POOL, 'nameChampion3')
        if isinstance(stale, str) and stale.strip():
            problems.append(
                "q_leinth_lone pool: nameChampion3=%r must be cleared - a third "
                "champion entry breaks the 2-guard shape (the Vashkarr fix)" % stale)
        # her three variants must still be the ONLY mains, with weights untouched
        for i, want in enumerate(VARIANTS, start=1):
            got = _v1(db, LEINTH_POOL, 'name%d' % i)
            if not isinstance(got, str) or got.replace('/', '\\').lower() != want.lower():
                problems.append("q_leinth_lone pool: name%d=%r, expected %s - her "
                                "3-variant roll must survive" % (i, got, want))

    # ORDERING INVARIANT: the mid boss must not out-stat the uber champion.
    if db.has_record(_ENSLAVER):
        def _e(f):
            v = _v1(db, _ENSLAVER, f)
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        for field, mine in (('defensivePhysical', PHYS), ('defensivePierce', PIERCE),
                            ('defensivePoison', POISON),
                            ('characterAttackSpeed', ATTACK_SPEED),
                            ('characterRunSpeed', RUN_SPEED)):
            theirs = _e(field)
            if theirs is not None and mine > theirs + 1e-6:
                problems.append(
                    "ORDERING: Leinth's %s (%g) now EXCEEDS the Enslaver's (%g) - "
                    "a charLevel 74-76 mid boss must never out-stat a charLevel "
                    "100 uber" % (field, mine, theirs))

    if problems:
        raise SystemExit(
            "[leinth_wave] R-73/R-76 VERIFY FAILED (Leinth honour guard + poison "
            "rigs + buff):\n  - " + "\n  - ".join(problems))
    print("  [leinth_wave] verify OK: 3 variants at life %s / phys %g / pierce %g "
          "/ poison %g (weakness REMOVED, not immunity); BOTH staged acid rigs "
          "live @ specialAttack%s chained to her own copies AND CASTABLE (anim "
          "%r, bound in anm_leinth; xpack Cerberus untouched); Blood Boil "
          "castable at last (%r -> %r, shared donor untouched); Crimson Tithe @ "
          "%s; geysers PINNED at the shipped %s (DORMANT: no cast slot + unbound "
          "%r - reported, not faked); ugly swarm AS SHIPPED (%s/%d/no-TTL); "
          "honour guard = 2 named cult champions at %s via the escort LAW "
          "(spawnMax %d - championMax %d = 1 Leinth, equation neutralized), the "
          "Voice's bloodbeast at skillLevel%d %s (round 1 left it level-0) and "
          "the Reaver's 2 cast-aborting slots repointed; 0 cast-aborting and 0 "
          "level-0 slots across all 5 records; drops untouched; still below the "
          "Enslaver"
          % ([int(LIFE[v]) for v in VARIANTS], PHYS, PIERCE, POISON,
             ACID_SPECIAL, ACID_ANIM, BLOODBOIL_WAS_ANIM, GUARD_ANIM_TOKEN,
             TITHE_FIELD, GEYSER_LEVELS_SHIPPED, GEYSER_ANIM,
             UGLIES_BURST, UGLIES_LIMIT, GUARD_LEVEL, POOL_SPAWN,
             POOL_CHAMPION_MAX, GUARD_BEAST_SLOT, GUARD_BEAST_LEVELS))
