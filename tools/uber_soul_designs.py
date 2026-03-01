"""Hand-crafted uber soul designs for SoulvizierClassic.

Each soul is individually designed with thematic skills, stats, and tradeoffs
that reflect the monster it came from. 32 souls for genuinely new uber monsters.

Field naming follows TQ Anniversary Edition DBR conventions:
- Flat damage values: float (offensiveFireMin, offensiveColdMax, etc.)
- DoT fields: offensiveSlow* prefix (offensiveSlowFireMin = burn, etc.)
- Percentage modifiers/resistances: int (defensiveFire=15 means 15%)
- Character stats: int (characterLife, characterStrength, etc.)
- Speed modifiers: int percentage (characterAttackSpeedModifier=5 means +5%)
- Skill levels: int
- Paths: str with double backslashes
"""

# =============================================================================
# Augment Skill Paths
# =============================================================================

# Fire
_FIRE_ENCHANT = 'records\\skills\\earth\\drxfireenchantment.dbr'
_RING_OF_FLAME = 'records\\skills\\earth\\drxringofflame.dbr'
_VOLCANIC_ORB = 'records\\skills\\earth\\drxvolcanicorb.dbr'
_ERUPTION = 'records\\skills\\earth\\drxeruption.dbr'
_SPONTANEOUS_COMBUSTION = 'records\\skills\\earth\\drxspontaneouscombustion.dbr'
_FIRE_ENCHANT_BRIMSTONE = 'records\\skills\\earth\\drxfireenchantment_brimstone.dbr'
_FIRE_ENCHANT_STONESKIN = 'records\\skills\\earth\\drxfireenchantment_stoneskin.dbr'
_CORE_DWELLER_WILDFIRE = 'records\\skills\\earth\\drxcoredweller_petmodifier_wildfire.dbr'

# Cold
_COLD_AURA = 'records\\skills\\storm\\drxcoldaura.dbr'
_FREEZING_BLAST = 'records\\skills\\storm\\drxfreezingblast.dbr'
_ICE_SHARD = 'records\\skills\\storm\\drxiceshard.dbr'
_SQUALL = 'records\\skills\\storm\\drxsquall.dbr'
_COLD_AURA_SYNERGY = 'records\\skills\\storm\\drxcoldaura_synergy.dbr'
_FREEZING_BLAST_HYPOTHERMIA = 'records\\skills\\storm\\drxfreezingblast_hypothermia.dbr'
_ICE_SHARD_VELOCITY = 'records\\skills\\storm\\drxiceshard_velocity.dbr'

# Lightning
_STORM_NIMBUS = 'records\\skills\\storm\\drxstormnimbus.dbr'
_THUNDERBALL = 'records\\skills\\storm\\drxthunderball.dbr'
_LIGHTNING_BOLT = 'records\\skills\\storm\\drxlightningbolt.dbr'
_STORM_SURGE = 'records\\skills\\storm\\drxstormsurge.dbr'
_STORM_NIMBUS_STATIC = 'records\\skills\\storm\\drxstormnimbus_staticcharge.dbr'
_LIGHTNING_BOLT_CHAIN = 'records\\skills\\storm\\drxlightningbolt_chainlightning.dbr'
_THUNDERBALL_CONCUSSIVE = 'records\\skills\\storm\\drxthunderball_concussiveblast.dbr'
_ENERGY_SHIELD = 'records\\skills\\storm\\drxenergyshield.dbr'
_SPELLBREAKER = 'records\\skills\\storm\\drxspellbreaker.dbr'

# Poison
_ENVENOM_WEAPON = 'records\\skills\\stealth\\drxenvenomweapon.dbr'
_POISON_GAS_BOMB = 'records\\skills\\stealth\\drxpoisongasbomb.dbr'
_PLAGUE = 'records\\skills\\nature\\drxplague.dbr'
_TOXIN_DISTILLATION = 'records\\skills\\stealth\\drxtoxindistillation.dbr'
_ENVENOM_NEUROTOXIN = 'records\\skills\\stealth\\drxenvenomweapon_neurotoxin.dbr'
_ENVENOM_DELIRIUM = 'records\\skills\\stealth\\drxenvenomweapon_delirium.dbr'
_PLAGUE_FATIGUE = 'records\\skills\\nature\\drxplague_fatigue.dbr'

# Life / Spirit
_DEATH_CHILL = 'records\\skills\\spirit\\drxdeathchillaura.dbr'
_ENSLAVE_SPIRIT = 'records\\skills\\spirit\\drxenslavespirit.dbr'
_VISION_OF_DEATH = 'records\\skills\\spirit\\drxvisionofdeath.dbr'
_DEATH_WARD = 'records\\skills\\spirit\\drxdeathward.dbr'
_TERNION = 'records\\skills\\spirit\\drxternion.dbr'
_DEATH_CHILL_NECROSIS = 'records\\skills\\spirit\\drxdeathchillaura_necrosis.dbr'
_DEATH_CHILL_RAVAGES = 'records\\skills\\spirit\\drxdeathchillaura_ravagesoftime.dbr'
_DARK_COVENANT = 'records\\skills\\spirit\\drxdarkcovenant.dbr'

# Physical / Melee
_ONSLAUGHT = 'records\\skills\\warfare\\drxonslaught.dbr'
_BATTLE_RAGE = 'records\\skills\\warfare\\drxbattlerage.dbr'
_LETHAL_STRIKE = 'records\\skills\\stealth\\drxlethalstrike.dbr'
_TAKE_DOWN = 'records\\skills\\hunting\\drxtakedown.dbr'
_CALCULATED_STRIKE = 'records\\skills\\stealth\\drxcalculatedstrike.dbr'
_DUAL_WIELD = 'records\\skills\\warfare\\drxdualweapontraining.dbr'
_CRUSHING_BLOW = 'records\\skills\\warfare\\drxbattlerage_crushingblow.dbr'
_IGNORE_PAIN = 'records\\skills\\warfare\\drxonslaught_ignorepain.dbr'

# Physical / Tank
_ARMOR_HANDLING = 'records\\skills\\defensive\\drxarmorhandling.dbr'
_BATTLE_AWARENESS = 'records\\skills\\defensive\\drxbattleawareness.dbr'
_RALLY = 'records\\skills\\defensive\\drxrally.dbr'
_COLOSSUS_FORM = 'records\\skills\\defensive\\drxcolossusform.dbr'
_BATTER = 'records\\skills\\defensive\\drxbatter.dbr'
_CONCUSSIVE_BLOW = 'records\\skills\\defensive\\drxconcussiveblow.dbr'
_ADRENALINE = 'records\\skills\\defensive\\drxadrenaline.dbr'

# Ranged / Hunting
_MARKSMANSHIP = 'records\\skills\\hunting\\drxmarksmanship.dbr'
_STUDY_PREY = 'records\\skills\\hunting\\drxstudyprey.dbr'
_CALL_OF_HUNT = 'records\\skills\\hunting\\drxcallofthehunt.dbr'
_ART_OF_HUNT = 'records\\skills\\hunting\\drxartofthehunt.dbr'
_ENSNARE = 'records\\skills\\hunting\\drxensnare.dbr'

# Nature
_HEART_OF_OAK = 'records\\skills\\nature\\drxheartofoak.dbr'
_REGROWTH = 'records\\skills\\nature\\drxregrowth.dbr'
_BRIAR_WARD = 'records\\skills\\nature\\drxbriarward.dbr'
_WOLF_SUMMONS = 'records\\skills\\nature\\drxwolfsummons.dbr'

# Dream
_DISTORT_REALITY = 'records\\xpack\\skills\\dream\\drxdistortreality.dbr'
_PHANTOM_STRIKE = 'records\\xpack\\skills\\dream\\drxphantomstrike.dbr'
_TRANCE_OF_WRATH = 'records\\xpack\\skills\\dream\\drxtranceofwrath.dbr'
_DISTORTION_WAVE = 'records\\xpack\\skills\\dream\\drxdistortionwave.dbr'
_SANDS_OF_SLEEP = 'records\\xpack\\skills\\dream\\drxsandsofsleep.dbr'

# Weapon training
_SWORD_TRAINING = 'records\\skills\\soulskills\\swordtraining.dbr'
_AXE_TRAINING = 'records\\skills\\soulskills\\axetraining.dbr'
_BLUNT_TRAINING = 'records\\skills\\soulskills\\blunttraining.dbr'
_BOW_TRAINING = 'records\\skills\\soulskills\\bowtraining.dbr'
_SPEAR_TRAINING = 'records\\skills\\soulskills\\speartraining.dbr'
_STAFF_TRAINING = 'records\\skills\\soulskills\\stafftraining.dbr'

# =============================================================================
# Granted Skill Paths (itemSkillName)
# =============================================================================

# Fire procs
_GR_BLAZING_WEAPONS = 'records\\skills\\soulskills\\blazingweapons.dbr'
_GR_TOMBGUARD_FLAME = 'records\\skills\\soulskills\\tombguardian_flamering.dbr'
_GR_YAOGUAI_FLAME = 'records\\skills\\soulskills\\yaoguai_flamering.dbr'
_GR_TALOS_FLAME = 'records\\skills\\soulskills\\talos_flamethrower.dbr'
_GR_EPHIALTES_WAVE = 'records\\skills\\soulskills\\ephialtes_flamewave.dbr'
_GR_FIRE_NOVA = 'records\\skills\\soulskills\\firefragmentnova.dbr'
_GR_SCIRTUS_AURA = 'records\\skills\\soulskills\\scirtus_fireaura.dbr'
_GR_SANDWRAITH_BOLT = 'records\\skills\\soulskills\\sandwraith_fierybolt.dbr'

# Cold procs
_GR_YETI_ICEBLAST = 'records\\skills\\soulskills\\gargantuanyeti_iceblast.dbr'
_GR_YETI_FREEZE = 'records\\skills\\soulskills\\yeti_freezingblast.dbr'
_GR_BARMANU_BLIZZARD = 'records\\skills\\soulskills\\barmanu_blizzard.dbr'
_GR_EMPUSA_FROST = 'records\\skills\\soulskills\\empusa_cold_frostspit.dbr'
_GR_CHILLING_AIR = 'records\\skills\\soulskills\\chillingair.dbr'
_GR_ICESHARD_FAN = 'records\\skills\\soulskills\\iceshard_fan.dbr'
_GR_RIMEPUCK_FREEZE = 'records\\skills\\soulskills\\rimepuck_freezingblast.dbr'
_GR_DYSNOMION_COLD = 'records\\skills\\soulskills\\dysnomion_coldenergyblast.dbr'

# Lightning procs
_GR_HARPY_AURA = 'records\\skills\\soulskills\\harpy_lightningaura.dbr'
_GR_MUMMY_BALL = 'records\\skills\\soulskills\\mummy_lightningball.dbr'
_GR_DEINO_CLAP = 'records\\skills\\soulskills\\deino_lightningclap.dbr'
_GR_ENYO_STORM = 'records\\skills\\soulskills\\enyo_thunderstorm.dbr'
_GR_PEMPHREDO_SPARK = 'records\\skills\\soulskills\\pemphredo_thunderspark.dbr'
_GR_CENON_BALL = 'records\\skills\\soulskills\\cenon_lightningball.dbr'
_GR_ZHENG_BOLT = 'records\\skills\\soulskills\\zheng_lightningbolt.dbr'
_GR_THUNDERBALL_NOVA = 'records\\skills\\soulskills\\thunderballnova.dbr'
_GR_RING_LIGHTNING = 'records\\skills\\soulskills\\ringoflightning.dbr'
_GR_TATH_THUNDER = 'records\\skills\\soulskills\\tath_thunderball.dbr'

# Poison procs
_GR_ARACHNE_VENOM = 'records\\skills\\soulskills\\arachne_venomspray.dbr'
_GR_SCARAB_POISON = 'records\\skills\\soulskills\\scarabaeus_poisonspray.dbr'
_GR_NEHEBKAU_GAS = 'records\\skills\\soulskills\\nehebkau_poisongasbomb.dbr'
_GR_PUBOS_GAS = 'records\\skills\\soulskills\\pubos_poisongasball.dbr'
_GR_MEGAERA_NOVA = 'records\\skills\\soulskills\\megaera_venomnova.dbr'
_GR_POISON_ORBS = 'records\\skills\\soulskills\\poisonorbs.dbr'
_GR_SAJAKI_AURA = 'records\\skills\\soulskills\\sajaki_poisonaura.dbr'
_GR_VILETHROAT_FAN = 'records\\skills\\soulskills\\vilethroat_poisonfan.dbr'

# Life / Spirit procs
_GR_LIFE_DRAIN = 'records\\skills\\spirit\\lifedrain.dbr'
_GR_ENSLAVE_SCROLL = 'records\\skills\\scroll skills\\enslavespirit.dbr'
_GR_MELINOE_BLOOD = 'records\\skills\\soulskills\\melinoe_bloodboil.dbr'
_GR_PROSEIA_DRAIN = 'records\\skills\\soulskills\\proseia_lifedrainnova.dbr'
_GR_LICHE_STRIKE = 'records\\skills\\soulskills\\lichequeen_soulstrike.dbr'
_GR_NIGHTSTALKER = 'records\\skills\\soulskills\\nightstalker_shadowsurge.dbr'
_GR_VOIDLASH = 'records\\skills\\soulskills\\voidlash_burst.dbr'
_GR_MORTH_BLOOD = 'records\\skills\\soulskills\\morth_bloodaura.dbr'

# Physical procs
_GR_CYCLOPS_SMASH = 'records\\skills\\soulskills\\cyclops_groundsmash.dbr'
_GR_MYRTO_TREMOR = 'records\\skills\\soulskills\\myrto_tremor.dbr'
_GR_DEMASTIA_STRIKE = 'records\\skills\\soulskills\\demastia_strike.dbr'
_GR_FURYCLAW_SLASH = 'records\\skills\\soulskills\\furyclaw_saberslash.dbr'
_GR_CLUBSLAM = 'records\\skills\\soulskills\\clubslam_ring.dbr'
_GR_SONIC_WAVE = 'records\\skills\\soulskills\\hero_sonicwave.dbr'
_GR_EARTHFURY = 'records\\skills\\soulskills\\earthfury_ring.dbr'

# Buff procs
_GR_NESSUS_ENDURANCE = 'records\\skills\\soulskills\\nessus_enduranceaura.dbr'
_GR_SPEED_ALL = 'records\\skills\\soulskills\\character_speedall.dbr'
_GR_SNOWHOOF_SHIELD = 'records\\skills\\soulskills\\snowhoof_energyshield.dbr'
_GR_CHARON_BUFF = 'records\\skills\\soulskills\\charon_buffself.dbr'

# Boss signature procs
_GR_MEDUSA_PETRIFY = 'records\\skills\\soulskills\\medusa_petrify.dbr'
_GR_TYPHON_METEOR = 'records\\skills\\soulskills\\typhon_meteorstorm.dbr'
_GR_SUMMON_CHIMERA = 'records\\skills\\soulskills\\summon_chimera.dbr'
_GR_SUMMON_HYDRA = 'records\\skills\\soulskills\\summon_hydra.dbr'
_GR_MANTICORE_QUILLS = 'records\\skills\\soulskills\\manticore_quills.dbr'
_GR_SKELETAL_TYPHON = 'records\\skills\\soulskills\\skeletaltyphon_bonespire.dbr'
_GR_CERBERUS_BREATH = 'records\\skills\\soulskills\\cerberus_breathwave.dbr'
_GR_HADES_STAR = 'records\\skills\\soulskills\\hades_star.dbr'
_GR_ORMENOS_BLAST = 'records\\skills\\soulskills\\ormenos_energyblast.dbr'

# Summons
_GR_SKELETON = 'records\\skills\\soulskills\\skeleton_summon.dbr'
_GR_SKEL_ARCHER = 'records\\skills\\soulskills\\skeletonarcher_summon.dbr'
_GR_FORMICID = 'records\\skills\\soulskills\\formicid_summon.dbr'
_GR_CARRION_CROW = 'records\\skills\\soulskills\\carrioncrow_summon.dbr'
_GR_WRAITH = 'records\\skills\\soulskills\\wraith_summon.dbr'
_GR_FIRE_SPRITE = 'records\\skills\\soulskills\\summon_firesprite.dbr'
_GR_FLAMEWING = 'records\\skills\\soulskills\\summon_flamewing.dbr'
_GR_PENG = 'records\\skills\\soulskills\\peng_summon.dbr'

# =============================================================================
# Auto-Cast Controller Paths
# =============================================================================

_AC_ON_ATTACK = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\base_atenemy_onattack.dbr'
_AC_LOW_HEALTH = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\base_atself_lowhealth.dbr'
_AC_UNDEAD_ATTACK = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\awakeneddeadsoul_onattack.dbr'
_AC_ON_EQUIP = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\base_atself_onequip.dbr'
_AC_ON_HIT = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\base_atself_onanyhit.dbr'
_AC_SELF_ATTACK = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\base_atself_onattack.dbr'
_AC_THUNDER_REACT = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\thunderballnova_onattacked.dbr'
_AC_ZOMBIE_LOW = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\zombiesoul_lowhealth.dbr'
_AC_POISON_ATTACK = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\poisonbomb_onattack.dbr'
_AC_ON_MELEE = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\base_atself_onmeleehit.dbr'
_AC_FIRE_REACT = 'records\\xpack\\ai controllers\\autocast_items\\basetemplates\\flamefragmentnova_onattacked.dbr'

# =============================================================================
# Racial Bonus Targets
# =============================================================================

_RACE_UNDEAD = 'Undead'
_RACE_BEAST = 'Beast'
_RACE_INSECTOID = 'Insectoid'
_RACE_DEMON = 'Demon'
_RACE_BEASTMAN = 'Beastman'
_RACE_DEVICE = 'Device'
_RACE_PLANT = 'Plant'
_RACE_MAGICAL = 'Magical'

# =============================================================================
# Soul Designs - 32 hand-crafted souls for genuinely new uber monsters
# =============================================================================

SOUL_DESIGNS = {

    # =========================================================================
    # EARLY GAME (levels 9-18)
    # =========================================================================

    # #1 - Crowboar: bleeding boar that summons carrion crows (lvl 9, physical)
    'crowboar': {
        'augmentSkillName1': _ONSLAUGHT,
        'augmentSkillLevel1': 1,
        'augmentSkillName2': _LETHAL_STRIKE,
        'augmentSkillLevel2': 1,
        'itemSkillName': _GR_CARRION_CROW,
        'itemSkillLevel': 1,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 12,
        'characterLife': 30,
        'offensivePhysicalMin': 4.0,
        'offensivePhysicalMax': 7.0,
        'offensiveSlowBleedingMin': 3.0,
        'offensiveSlowBleedingMax': 5.0,
        'offensiveSlowBleedingDurationMin': 3.0,
        'characterOffensiveAbility': 12,
        'characterDefensiveAbility': -10,
    },

    # #2 - Steamcrawler: armored fire turtle, slow but tough (lvl 13, fire)
    'steamcrawler': {
        'augmentSkillName1': _FIRE_ENCHANT,
        'augmentSkillLevel1': 1,
        'augmentSkillName2': _ARMOR_HANDLING,
        'augmentSkillLevel2': 1,
        'itemSkillName': _GR_FIRE_NOVA,
        'itemSkillLevel': 1,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterDefensiveAbility': 15,
        'defensiveFire': 10,
        'characterLife': 40,
        'offensiveFireMin': 4.0,
        'offensiveFireMax': 7.0,
        'defensiveProtection': 20,
        'characterRunSpeedModifier': -8,
    },

    # #3 - Onyxspine: purple lightning arachnos, multi-bolt strikes (lvl 14, lightning)
    'onyxspine': {
        'augmentSkillName1': _ONSLAUGHT,
        'augmentSkillLevel1': 1,
        'augmentSkillName2': _LIGHTNING_BOLT_CHAIN,
        'augmentSkillLevel2': 1,
        'itemSkillName': _GR_RING_LIGHTNING,
        'itemSkillLevel': 1,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterOffensiveAbility': 15,
        'offensiveLightningMin': 6.0,
        'offensiveLightningMax': 10.0,
        'offensivePhysicalMin': 3.0,
        'offensivePhysicalMax': 6.0,
        'characterAttackSpeedModifier': 5,
        'defensiveFire': -10,
        'racialBonusRace': _RACE_INSECTOID,
        'racialBonusPercentDamage': 8,
    },

    # #4 - Legion_28a: eurynomus corpse eater, life-draining horror (lvl 14, life)
    'legion_28a': {
        'augmentSkillName1': _DEATH_CHILL,
        'augmentSkillLevel1': 1,
        'augmentSkillName2': _ONSLAUGHT,
        'augmentSkillLevel2': 1,
        'itemSkillName': _GR_LIFE_DRAIN,
        'itemSkillLevel': 1,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 14,
        'offensiveSlowLifeLeechMin': 3.0,
        'characterLife': 35,
        'offensivePhysicalMin': 4.0,
        'offensivePhysicalMax': 7.0,
        'defensiveLightning': -10,
        'racialBonusRace': _RACE_UNDEAD,
        'racialBonusPercentDamage': 8,
    },

    # #5 - Legion_28b: eurynomus with stunning attacks (lvl 14, life)
    'legion_28b': {
        'augmentSkillName1': _DEATH_CHILL,
        'augmentSkillLevel1': 1,
        'augmentSkillName2': _CONCUSSIVE_BLOW,
        'augmentSkillLevel2': 1,
        'itemSkillName': _GR_LIFE_DRAIN,
        'itemSkillLevel': 1,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 12,
        'offensiveSlowLifeLeechMin': 3.0,
        'characterDefensiveAbility': 14,
        'defensiveStun': 10,
        'offensivePhysicalMin': 3.0,
        'offensivePhysicalMax': 6.0,
        'defensiveLightning': -10,
        'racialBonusRace': _RACE_UNDEAD,
        'racialBonusPercentDamage': 8,
    },

    # #6 - Blinkfang: venomous spider with charge and web (lvl 16, poison)
    'blinkfang': {
        'augmentSkillName1': _ENVENOM_WEAPON,
        'augmentSkillLevel1': 2,
        'augmentSkillName2': _CALCULATED_STRIKE,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_ARACHNE_VENOM,
        'itemSkillLevel': 2,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterDexterity': 22,
        'offensiveSlowPoisonMin': 8.0,
        'offensiveSlowPoisonMax': 14.0,
        'offensiveSlowPoisonDurationMin': 3.0,
        'characterAttackSpeedModifier': 6,
        'characterOffensiveAbility': 18,
        'defensiveLightning': -12,
        'racialBonusRace': _RACE_INSECTOID,
        'racialBonusPercentDamage': 10,
    },

    # #7 - Phlebas: ghostly drowned sailor, cold tidal wraith (lvl 16, cold)
    'phlebas': {
        'augmentSkillName1': _COLD_AURA,
        'augmentSkillLevel1': 2,
        'augmentSkillName2': _DEATH_WARD,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_CHILLING_AIR,
        'itemSkillLevel': 2,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterIntelligence': 22,
        'offensiveColdMin': 9.0,
        'offensiveColdMax': 15.0,
        'offensiveSlowLifeLeechMin': 4.0,
        'characterMana': 40,
        'characterLife': 45,
        'defensiveFire': -12,
        'racialBonusRace': _RACE_UNDEAD,
        'racialBonusPercentDamage': 10,
    },

    # #8 - Possessedboar: storm-charged spirit boar (lvl 17, lightning)
    'possessedboar': {
        'augmentSkillName1': _STORM_SURGE,
        'augmentSkillLevel1': 2,
        'augmentSkillName2': _ADRENALINE,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_THUNDERBALL_NOVA,
        'itemSkillLevel': 2,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 25,
        'characterLife': 50,
        'offensiveLightningMin': 10.0,
        'offensiveLightningMax': 16.0,
        'offensivePhysicalMin': 5.0,
        'offensivePhysicalMax': 9.0,
        'characterAttackSpeedModifier': 6,
        'defensiveCold': -12,
    },

    # #9 - Rebil: ratman shield brawler, tough and relentless (lvl 17, physical)
    'rebil': {
        'augmentSkillName1': _ONSLAUGHT,
        'augmentSkillLevel1': 2,
        'augmentSkillName2': _BATTLE_AWARENESS,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_NESSUS_ENDURANCE,
        'itemSkillLevel': 2,
        'itemSkillAutoController': _AC_ON_EQUIP,
        'characterStrength': 25,
        'characterDefensiveAbility': 22,
        'offensivePhysicalMin': 8.0,
        'offensivePhysicalMax': 14.0,
        'characterLife': 55,
        'characterSpellCastSpeedModifier': -10,
    },

    # #10 - Vileslash: ratman dual-wield poison assassin (lvl 17, poison)
    'vileslash': {
        'augmentSkillName1': _ENVENOM_NEUROTOXIN,
        'augmentSkillLevel1': 2,
        'augmentSkillName2': _DUAL_WIELD,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_POISON_ORBS,
        'itemSkillLevel': 2,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterDexterity': 24,
        'offensiveSlowPoisonMin': 10.0,
        'offensiveSlowPoisonMax': 16.0,
        'offensiveSlowPoisonDurationMin': 4.0,
        'characterAttackSpeedModifier': 7,
        'characterDefensiveAbility': 18,
        'characterLife': -25,
    },

    # #11 - Quest_celtheano: crag harpy, quest-tier lightning caster (lvl 18, lightning)
    'quest_celtheano': {
        'augmentSkillName1': _STORM_NIMBUS,
        'augmentSkillLevel1': 2,
        'augmentSkillName2': _FREEZING_BLAST,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_HARPY_AURA,
        'itemSkillLevel': 2,
        'itemSkillAutoController': _AC_ON_EQUIP,
        'characterIntelligence': 30,
        'offensiveLightningMin': 12.0,
        'offensiveLightningMax': 18.0,
        'characterMana': 55,
        'characterSpellCastSpeedModifier': 8,
        'characterLife': 60,
        'characterDefensiveAbility': -15,
    },

    # =========================================================================
    # MID GAME (levels 27-30)
    # =========================================================================

    # #12 - Ubericeraptor: massive frost raptor mini-boss (lvl 27, cold)
    'ubericeraptor': {
        'augmentSkillName1': _COLD_AURA_SYNERGY,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _ONSLAUGHT,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_YETI_ICEBLAST,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 35,
        'offensiveColdMin': 14.0,
        'offensiveColdMax': 22.0,
        'characterRunSpeedModifier': 8,
        'characterAttackSpeedModifier': 8,
        'characterLife': 80,
        'defensiveFire': -15,
        'racialBonusRace': _RACE_BEAST,
        'racialBonusPercentDamage': 10,
    },

    # #13 - Nekhekh: lightning crocman with reflection and tail whack (lvl 28, lightning)
    'nekhekh': {
        'augmentSkillName1': _LIGHTNING_BOLT_CHAIN,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _BATTER,
        'augmentSkillLevel2': 2,
        'itemSkillName': _GR_CENON_BALL,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 34,
        'offensiveLightningMin': 14.0,
        'offensiveLightningMax': 22.0,
        'characterOffensiveAbility': 28,
        'characterLife': 75,
        'defensivePoison': -14,
    },

    # #14 - Kazept: fire aura jackalman dual wielder (lvl 30, fire)
    'kazept': {
        'augmentSkillName1': _FIRE_ENCHANT_BRIMSTONE,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _DUAL_WIELD,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_SCIRTUS_AURA,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_EQUIP,
        'characterDexterity': 40,
        'offensiveFireMin': 16.0,
        'offensiveFireMax': 24.0,
        'offensiveSlowFireMin': 10.0,
        'offensiveSlowFireMax': 16.0,
        'offensiveSlowFireDurationMin': 3.0,
        'characterAttackSpeedModifier': 10,
        'characterOffensiveAbility': 30,
        'defensiveCold': -15,
    },

    # =========================================================================
    # LATE GAME (levels 35-40)
    # =========================================================================

    # #15 - Bloodrunner: blood-themed sprite, aggressive life drainer (lvl 35, life/fire)
    'bloodrunner': {
        'augmentSkillName1': _DEATH_CHILL_NECROSIS,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _LETHAL_STRIKE,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_MORTH_BLOOD,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'offensiveSlowLifeLeechMin': 8.0,
        'characterLife': 110,
        'characterOffensiveAbility': 38,
        'offensiveTotalDamageModifier': 5,
        'offensiveSlowBleedingMin': 12.0,
        'offensiveSlowBleedingMax': 20.0,
        'offensiveSlowBleedingDurationMin': 3.0,
        'characterDefensiveAbility': -22,
        'defensiveCold': -15,
    },

    # #16 - Xix: lightning peng with chain attacks and deflection (lvl 36, lightning)
    'xix': {
        'augmentSkillName1': _LIGHTNING_BOLT_CHAIN,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _ENERGY_SHIELD,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_RING_LIGHTNING,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterIntelligence': 48,
        'offensiveLightningMin': 22.0,
        'offensiveLightningMax': 35.0,
        'characterMana': 85,
        'characterDodgePercent': 6,
        'characterLife': -25,
        'defensiveLife': -12,
    },

    # #17 - Frost: Ancient Limos soul stealer, cold/life boss (lvl 36, cold/life, BOSS)
    'frost': {
        'augmentSkillName1': _COLD_AURA,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _DEATH_CHILL,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_CHILLING_AIR,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterIntelligence': 58,
        'offensiveColdMin': 30.0,
        'offensiveColdMax': 48.0,
        'offensiveSlowLifeLeechMin': 8.0,
        'characterLife': 150,
        'characterMana': 80,
        'defensiveCold': 20,
        'defensiveFire': -20,
    },

    # #18 - Koroush: shadow assassin ichthian, Lurker of Samarkand (lvl 39, life)
    'koroush': {
        'augmentSkillName1': _CALCULATED_STRIKE,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _DEATH_CHILL,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_WRAITH,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterDexterity': 52,
        'offensiveSlowLifeLeechMin': 8.0,
        'characterOffensiveAbility': 42,
        'characterMana': 70,
        'defensiveFire': -18,
        'racialBonusRace': _RACE_UNDEAD,
        'racialBonusPercentDamage': 12,
    },

    # #19 - Hero_junshan: tigerman warlord, pure melee powerhouse (lvl 39, physical)
    'hero_junshan': {
        'augmentSkillName1': _CRUSHING_BLOW,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _ADRENALINE,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_SONIC_WAVE,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterStrength': 55,
        'offensivePhysicalMin': 22.0,
        'offensivePhysicalMax': 35.0,
        'offensiveTotalDamageModifier': 5,
        'characterOffensiveAbility': 42,
        'characterLife': 130,
        'characterMana': -30,
        'characterSpellCastSpeedModifier': -12,
    },

    # #20 - Nkac: undead spider priest with death touch and aura (lvl 40, life/cold)
    'nkac': {
        'augmentSkillName1': _DEATH_WARD,
        'augmentSkillLevel1': 3,
        'augmentSkillName2': _DEATH_CHILL_RAVAGES,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_SKELETON,
        'itemSkillLevel': 3,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterIntelligence': 50,
        'characterLife': 130,
        'defensiveCold': 18,
        'offensiveSlowLifeLeechMin': 6.0,
        'defensiveFire': -20,
        'racialBonusRace': _RACE_INSECTOID,
        'racialBonusPercentDamage': 12,
    },

    # =========================================================================
    # END GAME (levels 41-46)
    # =========================================================================

    # #21 - Glittertail: diseased ratman king, fire bombs + poison (lvl 41, fire/poison)
    'glittertail': {
        'augmentSkillName1': _FIRE_ENCHANT,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _ENVENOM_WEAPON,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_POISON_ORBS,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterDexterity': 55,
        'offensiveFireMin': 28.0,
        'offensiveFireMax': 42.0,
        'offensiveSlowPoisonMin': 20.0,
        'offensiveSlowPoisonMax': 32.0,
        'offensiveSlowPoisonDurationMin': 3.0,
        'characterDodgePercent': 6,
        'defensiveCold': -15,
        'characterDefensiveAbility': -20,
    },

    # #22 - Boss_charon: THE Ferryman of Hades, iconic fire caster (lvl 42, fire, BOSS)
    'boss_charon': {
        'augmentSkillName1': _VOLCANIC_ORB,
        'augmentSkillLevel1': 5,
        'augmentSkillName2': _RING_OF_FLAME,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_TALOS_FLAME,
        'itemSkillLevel': 5,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterIntelligence': 80,
        'offensiveFireMin': 42.0,
        'offensiveFireMax': 65.0,
        'offensiveSlowFireMin': 28.0,
        'offensiveSlowFireMax': 45.0,
        'offensiveSlowFireDurationMin': 3.0,
        'characterMana': 150,
        'characterSpellCastSpeedModifier': 18,
        'characterLife': 200,
        'offensiveTotalDamageModifier': 8,
        'defensiveCold': -22,
        'characterRunSpeedModifier': -12,
    },

    # #23 - Shockooth: living lightning conductor ratman (lvl 42, lightning)
    'shockooth': {
        'augmentSkillName1': _STORM_NIMBUS_STATIC,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _THUNDERBALL_CONCUSSIVE,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_THUNDERBALL_NOVA,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_THUNDER_REACT,
        'characterStrength': 58,
        'offensiveLightningMin': 30.0,
        'offensiveLightningMax': 48.0,
        'characterAttackSpeedModifier': 14,
        'characterOffensiveAbility': 48,
        'defensivePoison': -16,
    },

    # #24 - Mountainblade: dragonian flame guard with summons and meteors (lvl 43, fire)
    'mountainblade': {
        'augmentSkillName1': _FIRE_ENCHANT_STONESKIN,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _SPONTANEOUS_COMBUSTION,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_EPHIALTES_WAVE,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterStrength': 62,
        'offensiveFireMin': 32.0,
        'offensiveFireMax': 50.0,
        'offensiveSlowFireMin': 22.0,
        'offensiveSlowFireMax': 35.0,
        'offensiveSlowFireDurationMin': 3.0,
        'characterLife': 155,
        'offensiveTotalDamageModifier': 6,
        'defensiveCold': -18,
        'characterDefensiveAbility': -22,
    },

    # #25 - Droolbog: anouran toad with dream/poison fusion (lvl 43, poison)
    'droolbog': {
        'augmentSkillName1': _TRANCE_OF_WRATH,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _PLAGUE_FATIGUE,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_PUBOS_GAS,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterDexterity': 58,
        'offensiveSlowPoisonMin': 28.0,
        'offensiveSlowPoisonMax': 44.0,
        'offensiveSlowPoisonDurationMin': 4.0,
        'characterDefensiveAbility': 48,
        'characterDodgePercent': 6,
        'defensiveFire': -16,
    },

    # #26 - Xhero_myrto: anteok tremor warrior with charge (lvl 43, physical)
    'xhero_myrto': {
        'augmentSkillName1': _BATTER,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _COLOSSUS_FORM,
        'augmentSkillLevel2': 3,
        'itemSkillName': _GR_MYRTO_TREMOR,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterStrength': 65,
        'offensivePhysicalMin': 30.0,
        'offensivePhysicalMax': 48.0,
        'characterDefensiveAbility': 52,
        'defensiveProtection': 40,
        'characterLife': 170,
        'characterAttackSpeedModifier': -12,
    },

    # #27 - Kydoimos: machae shield warrior in Hades' palace (lvl 45, physical)
    'kydoimos': {
        'augmentSkillName1': _BATTER,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _BATTLE_AWARENESS,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_NESSUS_ENDURANCE,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterStrength': 68,
        'characterDefensiveAbility': 60,
        'offensivePhysicalMin': 32.0,
        'offensivePhysicalMax': 50.0,
        'characterLife': 180,
        'defensiveStun': 18,
        'characterSpellCastSpeedModifier': -15,
        'characterMana': -25,
    },

    # #28 - Trachius: titan-tier cyclops brute from Olympus (lvl 45, physical)
    'trachius': {
        'augmentSkillName1': _IGNORE_PAIN,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _CRUSHING_BLOW,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_CYCLOPS_SMASH,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterStrength': 72,
        'offensivePhysicalMin': 35.0,
        'offensivePhysicalMax': 55.0,
        'offensiveTotalDamageModifier': 6,
        'characterOffensiveAbility': 55,
        'characterLife': 190,
        'characterSpellCastSpeedModifier': -15,
        'characterRunSpeedModifier': -8,
    },

    # #29 - Uber (Waeizhi, Scion of Winter): THE cold boss (lvl 45, cold, BOSS)
    # Fast, freezing predator. Blizzard procs when hit (retaliation freeze).
    'uber': {
        'itemSkillName': _GR_BARMANU_BLIZZARD,
        'itemSkillLevel': 6,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterIntelligence': 85,
        'offensiveColdMin': 55.0,
        'offensiveColdMax': 85.0,
        'offensiveSlowColdMin': 38.0,
        'offensiveSlowColdMax': 60.0,
        'offensiveSlowColdDurationMin': 3.0,
        'offensiveFreezeChance': 15.0,
        'offensiveFreezeMin': 1.5,
        'offensiveFreezeMax': 2.5,
        'characterLife': 250,
        'characterMana': 150,
        'offensiveTotalDamageModifier': 12,
        'retaliationColdMin': 30.0,
        'retaliationColdMax': 50.0,
        'characterAttackSpeedModifier': 12,
        'characterRunSpeedModifier': 10,
        'defensiveFire': -25,
    },

    # #30 - Shadowhero: phantom spider with dream powers and summons (lvl 46, life/lightning)
    'shadowhero': {
        'augmentSkillName1': _DISTORTION_WAVE,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _SANDS_OF_SLEEP,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_WRAITH,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterIntelligence': 68,
        'offensiveSlowLifeLeechMin': 10.0,
        'characterMana': 105,
        'characterDefensiveAbility': 52,
        'characterDodgePercent': 7,
        'characterOffensiveAbility': -22,
        'racialBonusRace': _RACE_INSECTOID,
        'racialBonusPercentDamage': 12,
    },

    # #31 - Xhero_karnahk: machae elite marksman from Hades (lvl 46, physical)
    'xhero_karnahk': {
        'augmentSkillName1': _MARKSMANSHIP,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _ART_OF_HUNT,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_SONIC_WAVE,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_HIT,
        'characterDexterity': 68,
        'offensivePhysicalMin': 32.0,
        'offensivePhysicalMax': 50.0,
        'characterOffensiveAbility': 58,
        'offensivePierceRatioModifier': 18,
        'characterAttackSpeedModifier': 14,
        'characterLife': -35,
    },

    # #32 - Xhero_nightsmistress: empusa dark summoner priestess (lvl 46, life)
    'xhero_nightsmistress': {
        'augmentSkillName1': _ENSLAVE_SPIRIT,
        'augmentSkillLevel1': 4,
        'augmentSkillName2': _DARK_COVENANT,
        'augmentSkillLevel2': 4,
        'itemSkillName': _GR_EMPUSA_FROST,
        'itemSkillLevel': 4,
        'itemSkillAutoController': _AC_ON_ATTACK,
        'characterIntelligence': 65,
        'offensiveSlowLifeLeechMin': 10.0,
        'characterLife': 160,
        'characterMana': 115,
        'characterDodgePercent': 7,
        'characterDefensiveAbility': -20,
        'characterOffensiveAbility': -22,
    },
}
