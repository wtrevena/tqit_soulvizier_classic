"""SoulvizierClassic extended patches.

Patch 13: Overhaul weak uber/boss souls with skills, summons, procs
Patch 14: Cascade mercenary scrolls across all difficulties/acts
Patch 15: Add Blood Mistress formula to boss loot tables
"""
import sys
from pathlib import Path
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import (
    ArzDatabase, TypedField,
    DATA_TYPE_INT, DATA_TYPE_FLOAT, DATA_TYPE_STRING, DATA_TYPE_BOOL,
)


def _ensure_record(db, path, template):
    """Create a new empty record in the database if it doesn't exist."""
    if not db.has_record(path):
        db.ensure_string(path)
        db._raw_records[path] = (db.ensure_string(path), b'')
        db._record_types[path] = template
        db._record_timestamps[path] = 0
        db._decoded_cache[path] = OrderedDict()
        db._modified.add(path)

# ── Skill / controller path constants ──────────────────────────────────────

_AC_ON_ATTACK = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atenemy_onattack.dbr'
_AC_ON_HIT = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onanyhit.dbr'
_AC_ON_EQUIP = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onequip.dbr'
_AC_THUNDER_REACT = r'records\xpack\ai controllers\autocast_items\basetemplates\thunderballnova_onattacked.dbr'
_AC_SELF_ATTACK = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onattack.dbr'
_AC_LOW_HEALTH = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_lowhealth.dbr'
_AC_FIRE_REACT = r'records\xpack\ai controllers\autocast_items\basetemplates\flamefragmentnova_onattacked.dbr'

SUMMON_CHIMERA_SKILL = r'records\skills\soulskills\summon_chimera.dbr'
SUMMON_HYDRA_SKILL = r'records\skills\soulskills\summon_hydra.dbr'
CHIMERA_PET_1 = r'records\skills\soulskills\pets\chimaera_1.dbr'

SOUL_TEMPLATE = 'database\\Templates\\Jewelry_Ring.tpl'

SUMMON_RAKANIZEUS_SKILL = r'records\skills\soulskills\summon_rakanizeus.dbr'
SUMMON_BONEASH_SKILL = r'records\skills\soulskills\summon_boneash.dbr'

# ── All mercenary scroll item paths ────────────────────────────────────────

NORMAL_SCROLLS = [
    'records/item/artifacts/n_mercscroll_euanthe.dbr',
    'records/item/artifacts/n_mercscroll_scyrna.dbr',
    'records/item/artifacts/n_mercscroll_iaera.dbr',
    'records/item/artifacts/n_mercscroll_kemzir.dbr',
    'records/item/artifacts/n_mercscroll_skoneros.dbr',
    'records/item/artifacts/n_mercscroll_apollinia.dbr',
]

EPIC_SCROLLS = [
    'records/item/artifacts/n_mercscroll_tykos.dbr',
    'records/item/artifacts/n_mercscroll_mivania.dbr',
    'records/item/artifacts/n_mercscroll_ixion.dbr',
]

LEGENDARY_SCROLLS = [
    'records/item/artifacts/n_mercscroll_vanati.dbr',
]

BLOOD_MISTRESS_FORMULA = r'records\item\formulas\n_mercupgrade_bloodmistress_formula.dbr'

# ── Merc scroll loot tables ────────────────────────────────────────────────

MERC_LOOT_TABLES = {
    'records\\item\\loottables\\mercscrolls\\01_n_mercscrolls.dbr': 'n1',
    'records\\item\\loottables\\mercscrolls\\02_n_mercscrolls.dbr': 'n2',
    'records\\item\\loottables\\mercscrolls\\03_n_mercscrolls.dbr': 'n3',
    'records\\item\\loottables\\mercscrolls\\04_n_mercscrolls.dbr': 'n4',
    'records\\item\\loottables\\mercscrolls\\01_e_mercscrolls.dbr': 'e1',
    'records\\item\\loottables\\mercscrolls\\02_e_mercscrolls.dbr': 'e2',
    'records\\item\\loottables\\mercscrolls\\03_e_mercscrolls.dbr': 'e3',
    'records\\item\\loottables\\mercscrolls\\04_e_mercscrolls.dbr': 'e4',
    'records\\item\\loottables\\mercscrolls\\01_l_mercscrolls.dbr': 'l1',
    'records\\item\\loottables\\mercscrolls\\02_l_mercscrolls.dbr': 'l2',
    'records\\item\\loottables\\mercscrolls\\03_l_mercscrolls.dbr': 'l3',
    'records\\item\\loottables\\mercscrolls\\04_l_mercscrolls.dbr': 'l4',
}

# ── Individual soul enhancement specs ──────────────────────────────────────
# For existing SV souls that need overhauls.
# Key = partial path match, Value = dict of fields to set/override.

SOUL_OVERHAULS = {
    # ── RAKANIZEUS: Lightning god-satyr. Summons Rakanizeus + massive speed + chain lightning
    'rakanizeus_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_RAKANIZEUS_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxstormsurge.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxlightningbolt_chainlightning.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 4),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, 45.0),
        'characterAttackSpeedModifier': (DATA_TYPE_INT, 35),
        'characterTotalSpeedModifier': (DATA_TYPE_INT, 25),
        'offensiveLightningMin': (DATA_TYPE_FLOAT, 25.0),
        'offensiveLightningMax': (DATA_TYPE_FLOAT, 80.0),
        'offensiveLightningModifier': (DATA_TYPE_INT, 30),
        'offensiveElectricalBurnMin': (DATA_TYPE_FLOAT, 40.0),
        'offensiveElectricalBurnMax': (DATA_TYPE_FLOAT, 75.0),
        'offensiveElectricalBurnDurationMin': (DATA_TYPE_FLOAT, 3.0),
        'defensiveLightning': (DATA_TYPE_FLOAT, 60.0),
        'defensivePierce': (DATA_TYPE_FLOAT, 15.0),
        'characterLife': (DATA_TYPE_INT, 200),
        'characterMana': (DATA_TYPE_INT, 100),
        'characterStrength': (DATA_TYPE_INT, 40),
        'characterDexterity': (DATA_TYPE_INT, 40),
        'characterOffensiveAbility': (DATA_TYPE_INT, 50),
    },

    # ── BONEASH: Fire skeleton caster. Summons Boneash + fire damage + cast speed
    'boneash_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_BONEASH_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\earth\drxvolcanicorb.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\earth\drxfireenchantment.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 35),
        'offensiveFireModifier': (DATA_TYPE_INT, 40),
        'offensiveFireMin': (DATA_TYPE_FLOAT, 15.0),
        'offensiveFireMax': (DATA_TYPE_FLOAT, 50.0),
        'offensiveBurnMin': (DATA_TYPE_FLOAT, 30.0),
        'offensiveBurnMax': (DATA_TYPE_FLOAT, 60.0),
        'offensiveBurnDurationMin': (DATA_TYPE_FLOAT, 3.0),
        'defensiveFire': (DATA_TYPE_FLOAT, 55.0),
        'characterMana': (DATA_TYPE_INT, 150),
        'characterIntelligence': (DATA_TYPE_INT, 50),
        'characterLifeModifier': (DATA_TYPE_FLOAT, -4.0),
    },

    # ── CALYBE THE WARDANCER: Dual-wield berserker. Eclipse blood drain on-hit
    'calybe_soul': {
        'itemSkillName': (DATA_TYPE_STRING, r'records\skills\soulskills\calybe_eclipse.dbr'),
        'itemSkillLevel': (DATA_TYPE_INT, 6),
        'itemSkillAutoController': (DATA_TYPE_STRING, _AC_ON_HIT),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\warfare\drxdualwieldtechnique_wardance.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 4),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\warfare\drxdualwieldtechnique_crosscut.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterAttackSpeedModifier': (DATA_TYPE_FLOAT, 18.0),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, 8.0),
        'characterOffensiveAbility': (DATA_TYPE_FLOAT, 50.0),
        'characterDexterity': (DATA_TYPE_INT, 30),
        'characterDodgePercent': (DATA_TYPE_FLOAT, 10.0),
        'offensivePhysicalModifier': (DATA_TYPE_INT, 20),
        'offensiveSlowBleedingModifier': (DATA_TYPE_INT, 35),
        'offensivePierceRatioModifier': (DATA_TYPE_INT, 15),
        'characterLife': (DATA_TYPE_INT, -60),
    },

    # ── XERKOS THE BETRAYER: Slow heavy-hitter. Stun + lethal strike, -move speed
    'xerkosthebetrayer_soul': {
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\warfare\drxdualweapontraining.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 3),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\stealth\drxlethalstrike.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterAttackSpeedModifier': (DATA_TYPE_FLOAT, 15.0),
        'characterOffensiveAbility': (DATA_TYPE_FLOAT, 50.0),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, -8.0),
        'offensivePhysicalMin': (DATA_TYPE_FLOAT, 20.0),
        'offensivePhysicalMax': (DATA_TYPE_FLOAT, 45.0),
        'offensiveStunMin': (DATA_TYPE_FLOAT, 0.5),
        'offensiveStunMax': (DATA_TYPE_FLOAT, 1.5),
        'offensiveStunChance': (DATA_TYPE_FLOAT, 20.0),
        'characterLife': (DATA_TYPE_INT, 100),
        'characterStrength': (DATA_TYPE_INT, 30),
        'characterDexterity': (DATA_TYPE_INT, 30),
        'offensivePierceRatioModifier': (DATA_TYPE_INT, 15),
    },
}

# ── Scan-and-enhance: find ALL boss/hero souls that lack itemSkillName ─────

_BOSS_SOUL_ENHANCEMENTS = {
    'typhon': None,
    'hydra': None,
    'hades': None,
    'medusa': None,
    'cerberus': None,
    'manticore': None,
    'talos': None,
    'arachne': None,
    'charon': None,
    'chimaera': None,
    'chimera': None,
    'cyclops': None,
    'scorpos': None,
    'dragon': None,
}


def _set_soul_fields(db, record_path, field_dict):
    """Apply a dict of {field_name: (dtype, value)} to a soul record."""
    for fname, (dtype, val) in field_dict.items():
        db.set_field(record_path, fname, val, dtype)
    db._modified.add(record_path)


def _find_record(db, path):
    """Find a record by path, trying both slash conventions."""
    if db.has_record(path):
        return path
    alt = path.replace('\\', '/')
    if db.has_record(alt):
        return alt
    alt = path.replace('/', '\\')
    if db.has_record(alt):
        return alt
    # Try case-insensitive search
    lower = path.replace('\\', '/').lower()
    for name in db.record_names():
        if name.replace('\\', '/').lower() == lower:
            return name
    return None


def _copy_animation_fields(db, monster_path, pet_path):
    """Copy all animation fields from a monster record to a pet record.

    After cloning a pet from Hydra, the pet inherits Hydra-specific animation
    file paths that are incompatible with the target mesh.  This function
    copies the correct animation fields from the real monster record (which
    uses the same mesh) into the cloned pet record.
    """
    monster_fields = db.get_fields(monster_path)
    pet_fields = db.get_fields(pet_path)
    if not monster_fields or not pet_fields:
        return 0

    copied = 0
    for key, tf in monster_fields.items():
        field_name = key.split('###')[0]
        # Copy any field with "Anim" or "anim" in name (animation files,
        # weights, speeds, etc.)
        if 'Anim' in field_name or 'anim' in field_name:
            # Find matching key in pet record (may have different ### suffix)
            target_key = None
            for pk in pet_fields:
                if pk.split('###')[0] == field_name:
                    target_key = pk
                    break
            if target_key:
                pet_fields[target_key].dtype = tf.dtype
                pet_fields[target_key].values = list(tf.values)
            else:
                pet_fields[field_name] = TypedField(tf.dtype, list(tf.values))
            copied += 1

    # Blank out any leftover Hydra-specific animation fields that weren't
    # replaced (e.g. unarmedSpecialAnim1-4, unarmedLongIdleAnim which the
    # real monster doesn't have but the Hydra pet does)
    for pk in list(pet_fields.keys()):
        fn = pk.split('###')[0]
        if ('Anim' in fn or 'anim' in fn) and pet_fields[pk].dtype == 2:
            vals = pet_fields[pk].values
            if vals and isinstance(vals[0], str) and 'Hydra' in vals[0]:
                pet_fields[pk].values = ['']
                copied += 1

    db._modified.add(pet_path)
    return copied


def _create_rakanizeus_pet_skill(db):
    """Create Rakanizeus pet records by cloning from Hydra and overriding.

    Clones the complete, working Hydra Pet.tpl records (which have all required
    fields for pathing, pet behavior, etc.) then copies animation fields from
    the real Rakanizeus monster record (which uses the same Satyr mesh) and
    overrides stats, skills, and identity.
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    # Source records to clone from (working Hydra pets)
    hydra_sources = [
        r'records/skills/soulskills/pets/hydra_1.dbr',
        r'records/skills/soulskills/pets/hydra_2.dbr',
        r'records/skills/soulskills/pets/hydra_3.dbr',
    ]
    hydra_summon = r'records/skills/soulskills/summon_hydra.dbr'

    pet_paths = [
        r'records/skills/soulskills/pets/rakanizeus_1.dbr',
        r'records/skills/soulskills/pets/rakanizeus_2.dbr',
        r'records/skills/soulskills/pets/rakanizeus_3.dbr',
    ]

    # Per-level scaling: [level 1, level 2, level 3]
    life =       [4500, 6500, 8500]
    life_regen = [25.0, 45.0, 65.0]
    dmg_min =    [60, 90, 120]
    dmg_max =    [90, 130, 170]
    armor_lvl =  [56, 184, 408]

    # Find the real Rakanizeus monster record for animation fields
    rakan_monster = _find_record(
        db, r'records\creature\monster\satyr\um_rakanizeus_17.dbr')
    if not rakan_monster:
        print("  WARNING: Rakanizeus monster record not found!")

    # Clone pet records from Hydra
    for i, path in enumerate(pet_paths):
        src = _find_record(db, hydra_sources[i])
        if not src:
            print(f"  WARNING: Hydra source {hydra_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Copy animation fields from the real Rakanizeus monster (Satyr mesh
        # needs Satyr animations, not Hydra animations)
        if rakan_monster:
            n = _copy_animation_fields(db, rakan_monster, path)
            if i == 0:
                print(f"  Copied {n} animation fields from Rakanizeus monster")

        sf = db.set_field

        # Override identity
        sf(path, 'charLevel', i + 1, DATA_TYPE_INT)
        sf(path, 'mesh', r'SVMesh\meshes\rakanizeus.msh', DATA_TYPE_STRING)
        sf(path, 'scale', 1.4, DATA_TYPE_FLOAT)
        sf(path, 'description', 'tagNewHero87', DATA_TYPE_STRING)
        sf(path, 'characterRacialProfile', 'Beastman', DATA_TYPE_STRING)
        sf(path, 'controller', CONTROLLER, DATA_TYPE_STRING)

        # Override stats — fast melee bruiser with lightning
        sf(path, 'characterLife', life[i], DATA_TYPE_INT)
        sf(path, 'characterLifeRegen', life_regen[i], DATA_TYPE_FLOAT)
        sf(path, 'characterMana', 500, DATA_TYPE_INT)
        sf(path, 'characterManaRegen', 20.0, DATA_TYPE_FLOAT)
        sf(path, 'characterStrength', 350, DATA_TYPE_INT)
        sf(path, 'characterDexterity', 300, DATA_TYPE_INT)
        sf(path, 'characterIntelligence', 200, DATA_TYPE_INT)
        sf(path, 'characterAttackSpeed', 0.85, DATA_TYPE_FLOAT)
        sf(path, 'characterRunSpeed', 1.3, DATA_TYPE_FLOAT)
        sf(path, 'characterSpellCastSpeed', 1.4, DATA_TYPE_FLOAT)

        # Override combat damage
        sf(path, 'handHitDamageMin', dmg_min[i], DATA_TYPE_INT)
        sf(path, 'handHitDamageMax', dmg_max[i], DATA_TYPE_INT)

        # Override combat skills (from Rakanizeus monster)
        sf(path, 'skillName1',
           r'records/skills/monster skills/buff_self/drxstormnimbus.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel1', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName2',
           r'records/skills/monster skills/attack_projectile/reptillian_lightningprojectile_burst.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel2', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName3',
           r'records/skills/monster skills/attack_melee/blitz.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel3', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName4',
           r'records/skills/monster skills/buff_self/rakanizeus_stormsurge.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel4', i + 1, DATA_TYPE_INT)

        # Override armor passive level
        sf(path, 'skillLevel13', armor_lvl[i], DATA_TYPE_INT)

        # Override special attacks (AI combat behavior)
        sf(path, 'attackSkillName',
           r'records/skills/monster skills/attack_melee/blitz.dbr',
           DATA_TYPE_STRING)
        sf(path, 'specialAttackSkillName',
           r'records/skills/monster skills/attack_projectile/reptillian_lightningprojectile_burst.dbr',
           DATA_TYPE_STRING)
        sf(path, 'specialAttackChance', 30, DATA_TYPE_INT)
        sf(path, 'specialAttackDelay', 8.0, DATA_TYPE_FLOAT)
        sf(path, 'specialAttackTimeout', 3.0, DATA_TYPE_FLOAT)
        sf(path, 'buffSelfSkillName',
           r'records/skills/monster skills/buff_self/drxstormnimbus.dbr',
           DATA_TYPE_STRING)
        sf(path, 'buffSelf2SkillName',
           r'records/skills/monster skills/buff_self/rakanizeus_stormsurge.dbr',
           DATA_TYPE_STRING)

        # Override pet behavior (ensure no loot drop)
        sf(path, 'dropItems', 0, DATA_TYPE_INT)
        sf(path, 'giveXP', 0, DATA_TYPE_INT)
        sf(path, 'experiencePoints', 0, DATA_TYPE_INT)

        # Override party UI icons
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex',
           DATA_TYPE_STRING)
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex',
           DATA_TYPE_STRING)

    # ── Clone and configure summon skill from Hydra ──────────────────────
    summon_path = SUMMON_RAKANIZEUS_SKILL
    summon_src = _find_record(db, hydra_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Hydra summon {hydra_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1, DATA_TYPE_INT)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonRakanizeus',
       DATA_TYPE_STRING)
    sf(summon_path, 'skillManaCost', [300, 350, 400], DATA_TYPE_INT)
    sf(summon_path, 'spawnObjects', pet_paths, DATA_TYPE_STRING)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex',
       DATA_TYPE_STRING)
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex',
       DATA_TYPE_STRING)

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'rakanizeus_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1, DATA_TYPE_INT)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2, DATA_TYPE_INT)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3, DATA_TYPE_INT)

    print("  Rakanizeus summon: cloned 3 pet records from Hydra + summon skill")
    return True


def _create_boneash_pet_skill(db):
    """Create Boneash pet records by cloning from Hydra and overriding.

    Boneash is a fire skeleton caster — slow movement, high INT, devastating
    fire spells (Fireball, Pillar of Flame, Flamestrike, Ternion).
    Clones from Hydra to inherit all required Pet.tpl fields, then copies
    animation fields from the real Boneash monster record.
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    # Source records to clone from (working Hydra pets)
    hydra_sources = [
        r'records/skills/soulskills/pets/hydra_1.dbr',
        r'records/skills/soulskills/pets/hydra_2.dbr',
        r'records/skills/soulskills/pets/hydra_3.dbr',
    ]
    hydra_summon = r'records/skills/soulskills/summon_hydra.dbr'

    pet_paths = [
        r'records/skills/soulskills/pets/boneash_1.dbr',
        r'records/skills/soulskills/pets/boneash_2.dbr',
        r'records/skills/soulskills/pets/boneash_3.dbr',
    ]

    # Per-level scaling
    life =       [3500, 5000, 6500]
    life_regen = [20.0, 35.0, 50.0]
    dmg_min =    [40, 60, 80]
    dmg_max =    [60, 90, 120]
    armor_lvl =  [40, 150, 350]

    # Find the real Boneash monster record for animation fields
    boneash_monster = _find_record(
        db, r'records\creature\monster\skeleton\um_boneash_30.dbr')
    if not boneash_monster:
        print("  WARNING: Boneash monster record not found!")

    # Clone pet records from Hydra
    for i, path in enumerate(pet_paths):
        src = _find_record(db, hydra_sources[i])
        if not src:
            print(f"  WARNING: Hydra source {hydra_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Copy animation fields from the real Boneash monster (Skeleton mesh
        # needs Skeleton animations, not Hydra animations)
        if boneash_monster:
            n = _copy_animation_fields(db, boneash_monster, path)
            if i == 0:
                print(f"  Copied {n} animation fields from Boneash monster")

        sf = db.set_field

        # Override identity
        sf(path, 'charLevel', i + 1, DATA_TYPE_INT)
        sf(path, 'mesh',
           r'Creatures\Monster\Skeleton\RevenantFire.msh', DATA_TYPE_STRING)
        sf(path, 'charAnimationTableName',
           r'records\creature\monster\skeleton\anm\anm_skeleton01.dbr',
           DATA_TYPE_STRING)
        sf(path, 'description', 'tagNewHero48', DATA_TYPE_STRING)
        sf(path, 'characterRacialProfile', 'Undead', DATA_TYPE_STRING)
        sf(path, 'controller', CONTROLLER, DATA_TYPE_STRING)

        # Override stats — slow fire caster, big mana pool
        sf(path, 'characterLife', life[i], DATA_TYPE_INT)
        sf(path, 'characterLifeRegen', life_regen[i], DATA_TYPE_FLOAT)
        sf(path, 'characterMana', 1200, DATA_TYPE_INT)
        sf(path, 'characterManaRegen', 30.0, DATA_TYPE_FLOAT)
        sf(path, 'characterStrength', 150, DATA_TYPE_INT)
        sf(path, 'characterDexterity', 150, DATA_TYPE_INT)
        sf(path, 'characterIntelligence', 400, DATA_TYPE_INT)
        sf(path, 'characterAttackSpeed', 1.2, DATA_TYPE_FLOAT)
        sf(path, 'characterRunSpeed', 0.75, DATA_TYPE_FLOAT)
        sf(path, 'characterSpellCastSpeed', 1.5, DATA_TYPE_FLOAT)

        # Override combat damage
        sf(path, 'handHitDamageMin', dmg_min[i], DATA_TYPE_INT)
        sf(path, 'handHitDamageMax', dmg_max[i], DATA_TYPE_INT)

        # Override combat skills (from Boneash monster)
        sf(path, 'skillName1',
           r'Records/Skills/Monster Skills/Monster_Fireball.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel1', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName2',
           r'Records/Skills/Monster Skills/Auras/Damage_FireBonus.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel2', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName3',
           r'Records/Skills/Monster Skills/Attack_Radius/PillarofFlame.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel3', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName4',
           r'records/skills/spirit/ternion.dbr', DATA_TYPE_STRING)
        sf(path, 'skillLevel4', i + 1, DATA_TYPE_INT)
        sf(path, 'skillName5',
           r'Records/Skills/Monster Skills/Attack_Radius/DuneRaider_Flamestrike.dbr',
           DATA_TYPE_STRING)
        sf(path, 'skillLevel5', i + 1, DATA_TYPE_INT)

        # Override armor passive level
        sf(path, 'skillLevel13', armor_lvl[i], DATA_TYPE_INT)

        # Override special attacks (AI combat behavior)
        sf(path, 'attackSkillName',
           r'records/skills/spirit/ternion.dbr', DATA_TYPE_STRING)
        sf(path, 'specialAttackSkillName',
           r'Records/Skills/Monster Skills/Monster_Fireball.dbr',
           DATA_TYPE_STRING)
        sf(path, 'specialAttackChance', 40, DATA_TYPE_INT)
        sf(path, 'specialAttackDelay', 6.0, DATA_TYPE_FLOAT)
        sf(path, 'specialAttackTimeout', 3.0, DATA_TYPE_FLOAT)
        sf(path, 'specialAttack2SkillName',
           r'Records/Skills/Monster Skills/Attack_Radius/PillarofFlame.dbr',
           DATA_TYPE_STRING)
        sf(path, 'specialAttack2Chance', 25, DATA_TYPE_INT)
        sf(path, 'specialAttack2Delay', 10.0, DATA_TYPE_FLOAT)
        sf(path, 'specialAttack2Timeout', 4.0, DATA_TYPE_FLOAT)
        sf(path, 'specialAttack3SkillName',
           r'Records/Skills/Monster Skills/Attack_Radius/DuneRaider_Flamestrike.dbr',
           DATA_TYPE_STRING)
        sf(path, 'specialAttack3Chance', 20, DATA_TYPE_INT)
        sf(path, 'specialAttack3Delay', 12.0, DATA_TYPE_FLOAT)
        sf(path, 'specialAttack3Timeout', 5.0, DATA_TYPE_FLOAT)
        sf(path, 'initialSkillName',
           r'Records/Skills/Monster Skills/Auras/Damage_FireBonus.dbr',
           DATA_TYPE_STRING)
        sf(path, 'buffSelfSkillName',
           r'Records/Skills/Monster Skills/Auras/Damage_FireBonus.dbr',
           DATA_TYPE_STRING)

        # Override pet behavior (ensure no loot drop)
        sf(path, 'dropItems', 0, DATA_TYPE_INT)
        sf(path, 'giveXP', 0, DATA_TYPE_INT)
        sf(path, 'experiencePoints', 0, DATA_TYPE_INT)

        # Override party UI icons
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\spirit\bonefiendup.tex',
           DATA_TYPE_STRING)
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\spirit\bonefienddown.tex',
           DATA_TYPE_STRING)

    # ── Clone and configure summon skill from Hydra ──────────────────────
    summon_path = SUMMON_BONEASH_SKILL
    summon_src = _find_record(db, hydra_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Hydra summon {hydra_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1, DATA_TYPE_INT)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonBoneash',
       DATA_TYPE_STRING)
    sf(summon_path, 'skillManaCost', [250, 300, 350], DATA_TYPE_INT)
    sf(summon_path, 'spawnObjects', pet_paths, DATA_TYPE_STRING)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\spirit\bonefiendup.tex', DATA_TYPE_STRING)
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\spirit\bonefienddown.tex', DATA_TYPE_STRING)

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boneash_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1, DATA_TYPE_INT)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2, DATA_TYPE_INT)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3, DATA_TYPE_INT)

    print("  Boneash summon: cloned 3 pet records from Hydra + summon skill")
    return True


def _find_auto_generated_souls(db):
    """Find svc_uber_ souls we auto-generated that could use skill enhancement."""
    results = []
    for name in db.record_names():
        nl = name.lower()
        if 'svc_uber' not in nl:
            continue
        if 'equipmentring' not in nl:
            continue
        if '_soul_n.dbr' not in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        has_skill = False
        has_augment = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'itemSkillName' and tf.values and tf.values[0]:
                has_skill = True
            if rk == 'augmentSkillName1' and tf.values and tf.values[0]:
                has_augment = True

        if has_skill:
            continue

        basename = nl.replace('\\', '/').split('/')[-1].replace('_soul_n.dbr', '')
        monster_level = 0
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'itemLevel' and tf.values:
                monster_level = int(tf.values[0])
                break

        results.append({
            'path_n': name,
            'path_e': name.replace('_soul_n.dbr', '_soul_e.dbr'),
            'path_l': name.replace('_soul_n.dbr', '_soul_l.dbr'),
            'basename': basename,
            'level': monster_level,
            'has_augment': has_augment,
        })
    return results


# Map elements/keywords to good granted skills + augments for auto-enhancement
_ELEMENT_SKILL_MAP = {
    'lightning': {
        'itemSkillName': r'records\skills\soulskills\ringoflightning.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\storm\drxstormnimbus.dbr',
        'augment2': r'records\skills\storm\drxlightningbolt_chainlightning.dbr',
    },
    'fire': {
        'itemSkillName': r'records\skills\soulskills\firefragmentnova.dbr',
        'itemSkillAutoController': _AC_FIRE_REACT,
        'augment1': r'records\skills\earth\drxfireenchantment.dbr',
        'augment2': r'records\skills\earth\drxringofflame.dbr',
    },
    'cold': {
        'itemSkillName': r'records\skills\soulskills\gargantuanyeti_iceblast.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\storm\drxcoldaura.dbr',
        'augment2': r'records\skills\storm\drxfreezingblast.dbr',
    },
    'poison': {
        'itemSkillName': r'records\skills\soulskills\arachne_venomspray.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\stealth\drxenvenomweapon.dbr',
        'augment2': r'records\skills\nature\drxplague.dbr',
    },
    'life': {
        'itemSkillName': r'records\skills\soulskills\melinoe_bloodboil.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\spirit\drxdeathchillaura.dbr',
        'augment2': r'records\skills\spirit\drxdarkcovenant.dbr',
    },
    'physical': {
        'itemSkillName': r'records\skills\soulskills\cyclops_groundsmash.dbr',
        'itemSkillAutoController': _AC_ON_HIT,
        'augment1': r'records\skills\warfare\drxonslaught.dbr',
        'augment2': r'records\skills\warfare\drxbattlerage.dbr',
    },
}

_ELEMENT_KEYWORDS = {
    'lightning': ['lightning', 'storm', 'thunder', 'electric', 'shock'],
    'fire': ['fire', 'flame', 'burn', 'magma', 'lava', 'pyro', 'inferno'],
    'cold': ['cold', 'ice', 'frost', 'freeze', 'blizzard', 'chill', 'yeti'],
    'poison': ['poison', 'venom', 'toxic', 'plague', 'spider', 'arachn', 'scorpo'],
    'life': ['life', 'death', 'undead', 'spirit', 'wraith', 'ghost', 'liche', 'necrotic', 'shadow', 'dark'],
}


def _guess_element(basename, fields):
    """Guess element from soul basename and existing damage fields."""
    text = basename.lower()
    damage_hints = {}
    for key, tf in fields.items():
        rk = key.split('###')[0].lower()
        if 'offensivefire' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['fire'] = damage_hints.get('fire', 0) + float(tf.values[0])
        elif 'offensivecold' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['cold'] = damage_hints.get('cold', 0) + float(tf.values[0])
        elif 'offensivelightning' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['lightning'] = damage_hints.get('lightning', 0) + float(tf.values[0])
        elif ('offensivepoison' in rk or 'offensiveslowpoison' in rk) and tf.values and float(tf.values[0]) > 0:
            damage_hints['poison'] = damage_hints.get('poison', 0) + float(tf.values[0])
        elif 'offensivelife' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['life'] = damage_hints.get('life', 0) + float(tf.values[0])

    if damage_hints:
        return max(damage_hints, key=damage_hints.get)

    for elem, keywords in _ELEMENT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return elem

    return 'physical'


def overhaul_souls(db):
    """Patch 13: Overhaul weak uber/boss souls with skills, summons, procs."""
    print("\n=== Patch 13: Overhaul weak souls with skills/procs ===")
    total = 0

    rakan_ok = _create_rakanizeus_pet_skill(db)
    total += 1

    boneash_ok = _create_boneash_pet_skill(db)
    total += 1

    eclipse_skill = r'records\skills\soulskills\calybe_eclipse.dbr'
    if db.has_record(eclipse_skill):
        db.set_field(eclipse_skill, 'skillCooldownTime', 18.0, DATA_TYPE_FLOAT)
        db.set_field(eclipse_skill, 'skillCooldownReductionModifier', 18.0, DATA_TYPE_FLOAT)
        db._modified.add(eclipse_skill)
        print("  Eclipse cooldown: 90s -> 18s (for on-hit proc)")

    for partial_key, field_dict in SOUL_OVERHAULS.items():
        for name in list(db.record_names()):
            nl = name.lower()
            if partial_key in nl and 'soul' in nl and 'equipmentring' in nl:
                _set_soul_fields(db, name, field_dict)
                total += 1
        print(f"  Enhanced: {partial_key} ({sum(1 for n in db.record_names() if partial_key in n.lower() and 'soul' in n.lower() and 'equipmentring' in n.lower())} variants)")

    auto_souls = _find_auto_generated_souls(db)
    enhanced = 0
    for soul in auto_souls:
        fields = db.get_fields(soul['path_n'])
        if not fields:
            continue

        elem = _guess_element(soul['basename'], fields)
        skill_map = _ELEMENT_SKILL_MAP.get(elem, _ELEMENT_SKILL_MAP['physical'])
        level = soul['level']
        power = max(1.0, level / 10.0)

        enhancements = {
            'itemSkillName': (DATA_TYPE_STRING, skill_map['itemSkillName']),
            'itemSkillLevel': (DATA_TYPE_INT, max(1, min(int(power), 5))),
            'itemSkillAutoController': (DATA_TYPE_STRING, skill_map['itemSkillAutoController']),
        }
        if not soul['has_augment']:
            enhancements['augmentSkillName1'] = (DATA_TYPE_STRING, skill_map['augment1'])
            enhancements['augmentSkillLevel1'] = (DATA_TYPE_INT, max(1, min(int(power * 0.8), 4)))
            enhancements['augmentSkillName2'] = (DATA_TYPE_STRING, skill_map['augment2'])
            enhancements['augmentSkillLevel2'] = (DATA_TYPE_INT, max(1, min(int(power * 0.6), 3)))

        for variant in (soul['path_n'], soul['path_e'], soul['path_l']):
            if db.has_record(variant):
                _set_soul_fields(db, variant, enhancements)

        enhanced += 1

    print(f"  Auto-enhanced {enhanced} auto-generated (svc_uber) souls with element-matched skills")
    total += enhanced

    print(f"  Total soul records modified: {total}")
    return total


def cascade_merc_scrolls(db):
    """Patch 14: Make all mercenary scrolls droppable everywhere.

    Normal scrolls cascade into Epic tables, Normal+Epic into Legendary.
    Every act's table gets ALL scrolls for that difficulty tier.
    """
    print("\n=== Patch 14: Cascade mercenary scrolls across difficulties ===")
    total = 0

    all_scrolls = NORMAL_SCROLLS + EPIC_SCROLLS + LEGENDARY_SCROLLS

    for table_path, tag in MERC_LOOT_TABLES.items():
        if not db.has_record(table_path):
            continue

        difficulty = tag[0]
        if difficulty == 'n':
            scrolls = NORMAL_SCROLLS
        elif difficulty == 'e':
            scrolls = NORMAL_SCROLLS + EPIC_SCROLLS
        else:
            scrolls = all_scrolls

        for i, scroll_path in enumerate(scrolls, 1):
            db.set_field(table_path, f'lootName{i}', scroll_path, DATA_TYPE_STRING)
            db.set_field(table_path, f'lootWeight{i}', 100, DATA_TYPE_INT)
        for i in range(len(scrolls) + 1, 31):
            db.set_field(table_path, f'lootWeight{i}', 0, DATA_TYPE_INT)

        db._modified.add(table_path)
        total += 1
        print(f"  {table_path}: {len(scrolls)} scrolls ({difficulty.upper()} tier)")

    print(f"  Updated {total} loot tables")
    return total


def add_blood_mistress_to_loot(db):
    """Patch 15: Add Blood Mistress upgrade formula to boss loot tables.

    Adds the formula to the forge formula drop tables in each act at each
    difficulty, so it can drop from bosses alongside other forge formulas.
    """
    print("\n=== Patch 15: Add Blood Mistress formula to boss loot tables ===")
    total = 0

    formula_path = BLOOD_MISTRESS_FORMULA
    if not db.has_record(formula_path):
        print(f"  WARN: Blood Mistress formula not found at {formula_path}")
        return 0

    forge_tables = []
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'forgeformulas' in nl and 'drop' in nl and 'loottable' in nl:
            forge_tables.append(name)

    for table in forge_tables:
        fields = db.get_fields(table)
        if not fields:
            continue

        max_slot = 0
        for key in fields:
            rk = key.split('###')[0]
            if rk.startswith('lootName'):
                try:
                    slot_num = int(rk.replace('lootName', ''))
                    if slot_num > max_slot:
                        max_slot = slot_num
                except ValueError:
                    pass

        new_slot = max_slot + 1
        db.set_field(table, f'lootName{new_slot}', formula_path, DATA_TYPE_STRING)
        db.set_field(table, f'lootWeight{new_slot}', 50, DATA_TYPE_INT)
        db._modified.add(table)
        total += 1

    print(f"  Added formula to {total} forge formula drop tables")
    return total


def apply_all_extended_patches(db):
    """Run all extended patches. Call after create_uber_souls."""
    tags = {}

    tags['tagSVCSummonRakanizeus'] = 'Call of the Storm Tyrant'
    tags['tagSVCSummonRakanizeusDESC'] = (
        'The captured soul of Rakanizeus strains against its bonds, '
        'desperate to reform. Release it and the lightning god-satyr '
        'manifests in a crackling storm of chain lightning, '
        'bound to serve until the tempest fades.'
    )

    tags['tagSVCSummonBoneash'] = 'Summon Boneash'
    tags['tagSVCSummonBoneashDESC'] = (
        'Release the imprisoned essence of Boneash, '
        'a skeletal fire mage consumed by arcane flame. '
        'The revenant rises wreathed in fire, hurling bolts of destruction '
        'and igniting the ground beneath its enemies.'
    )

    overhaul_souls(db)
    cascade_merc_scrolls(db)
    add_blood_mistress_to_loot(db)

    return tags
