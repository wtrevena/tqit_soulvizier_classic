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
SUMMON_PHARAOH_GUARD_SKILL = r'records\skills\soulskills\summon_pharaohguard.dbr'

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
    # ── RAKANIZEUS: Lightning god-satyr. Summons Rakanizeus + speed + chain lightning skills
    'rakanizeus_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_RAKANIZEUS_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxstormsurge.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxlightningbolt_chainlightning.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 4),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, 45.0),
        'characterAttackSpeedModifier': (DATA_TYPE_INT, 35),
        'characterTotalSpeedModifier': (DATA_TYPE_INT, 25),
        'defensivePierce': (DATA_TYPE_FLOAT, 15.0),
        'characterLife': (DATA_TYPE_INT, 200),
        'characterMana': (DATA_TYPE_INT, 100),
        'characterStrength': (DATA_TYPE_INT, 40),
        'characterDexterity': (DATA_TYPE_INT, 40),
        'characterOffensiveAbility': (DATA_TYPE_INT, 50),
    },

    # ── BONEASH: Fire skeleton caster. Summons Boneash + cast speed + fire skills
    'boneash_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_BONEASH_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\earth\drxvolcanicorb.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\earth\drxfireenchantment.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 35),
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

    # ── PHARAOH'S HONOR GUARD: Tanky construct. Summon + movement penalty only
    'pharaohshonorguard_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_PHARAOH_GUARD_SKILL),
        'characterTotalSpeedModifier': (DATA_TYPE_INT, 0),     # remove total speed penalty
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, -9.0),  # movement-only penalty
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


_SKILL_PREFIXES = (
    'skillname', 'skilllevel', 'attackskillname',
    'specialattack', 'buffself', 'initialskillname',
)


def _update_existing_fields(db, monster_path, pet_path, prefixes):
    """Update VALUES of existing pet fields from monster — never add new fields.

    Uses set_field() which preserves the pet's original dtype (important!).
    Direct dtype overwrite from monster records can corrupt the encoding.
    """
    monster_fields = db.get_fields(monster_path)
    if not monster_fields:
        return 0

    # Build lookup: field_name_lower -> TypedField for monster
    monster_by_name = {}
    for key, tf in monster_fields.items():
        fn = key.split('###')[0].lower()
        if any(fn.startswith(p) for p in prefixes):
            monster_by_name[fn] = tf

    # Only update pet fields that already exist AND have a monster counterpart
    # Use set_field() to preserve pet's dtype — do NOT overwrite dtype.
    pet_fields = db.get_fields(pet_path)
    if not pet_fields:
        return 0
    updated = 0
    for pk in list(pet_fields.keys()):
        fn = pk.split('###')[0].lower()
        if fn in monster_by_name:
            mtf = monster_by_name[fn]
            db.set_field(pet_path, pk.split('###')[0], list(mtf.values))
            updated += 1

    return updated


def _set_pet_equipment(db, pet_path, equip_spec):
    """Set pet equipment from a spec dict using set_field() (dtype-safe).

    equip_spec is a dict of {field_name: value}.  All values are set via
    set_field() which preserves the existing field's dtype if the field
    already exists, or infers dtype from the Python value type for new fields.

    This is the SAFE way to assign equipment — hardcoded values, no monster
    record copying, no dtype overwriting.
    """
    sf = db.set_field
    for field_name, value in equip_spec.items():
        sf(pet_path, field_name, value)
    db._modified.add(pet_path)
    return len(equip_spec)


def _create_rakanizeus_pet_skill(db):
    """Create Rakanizeus pet records by cloning from Lyia Leafsong.

    Lyia is the ideal clone source: she's already a permanent pet with full
    equipment, skills, and all required Pet.tpl fields.  After cloning, we
    clear her animations/equipment/skills and replace them with Rakanizeus's.
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    # Clone from Lyia (permanent pet with working equipment + skills)
    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    pet_paths = [
        r'records\skills\soulskills\pets\rakanizeus_1.dbr',
        r'records\skills\soulskills\pets\rakanizeus_2.dbr',
        r'records\skills\soulskills\pets\rakanizeus_3.dbr',
    ]

    # Per-level scaling: [level 1, level 2, level 3]
    life =       [4500, 6500, 8500]
    life_regen = [25.0, 45.0, 65.0]
    dmg_min =    [60, 90, 120]
    dmg_max =    [90, 130, 170]

    # Find the real Rakanizeus monster record
    rakan_monster = _find_record(
        db, r'records\creature\monster\satyr\um_rakanizeus_17.dbr')
    if not rakan_monster:
        print("  WARNING: Rakanizeus monster record not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Replace Lyia's animations and skills with Rakanizeus's.
        if rakan_monster:
            na = _copy_animation_fields(db, rakan_monster, path)
            ns = _update_existing_fields(db, rakan_monster, path, _SKILL_PREFIXES)
            if i == 0:
                print(f"  Copied from Rakanizeus monster: {na} anim, {ns} skill fields")

        sf = db.set_field

        # ── Equipment: fixed items per difficulty (warrior satyr loadout) ──
        # [Normal, Epic, Legendary] — game picks by current difficulty.
        _EQ = r'records\xpack\item\equipmentweapons\sword'
        _AB = r'records\item\equipmentarmband'
        _RG = r'records\item\equipmentring'
        _set_pet_equipment(db, path, {
            # Swords: Om'ehns (N) → Plissken (E) → Eternal Darkness (L)
            'chanceToEquipLeftHand': 100.0,
            'chanceToEquipLeftHandItem1': 5000,
            'lootLeftHandItem1': [
                _EQ + r'\u_n_002.dbr',
                _EQ + r'\u_e_001.dbr',
                _EQ + r'\u_l_002.dbr',
            ],
            # Armbands: Obsidian (N) → Warrior's (E) → Conqueror's (L)
            'chanceToEquipForearm': 100.0,
            'chanceToEquipForearmItem1': 5000,
            'lootForearmItem1': [
                _AB + r'\us_n_obsidianarmor.dbr',
                _AB + "\\us_e_warrior'spanoply.dbr",
                _AB + "\\us_l_conqueror'spanoply.dbr",
            ],
            # Rings: Zakalwe (N) → Adroit Loop (E) → Mark of Ares (L)
            'chanceToEquipFinger1': 100.0,
            'chanceToEquipFinger1Item1': 5000,
            'lootFinger1Item1': [
                _RG + r'\u_n_ringofzakalwe.dbr',
                _RG + r'\u_e_adroitloop.dbr',
                _RG + r'\u_l_markofares.dbr',
            ],
        })
        if i == 0:
            print("  Rakanizeus equipment: sword/armband/ring (N/E/L tiered)")

        # Override identity (replace Lyia's nymph identity with Rakanizeus)
        sf(path, 'charLevel', i + 1)
        sf(path, 'mesh', r'SVMesh\meshes\rakanizeus.msh')
        sf(path, 'baseTexture', '')  # use mesh default
        sf(path, 'bumpTexture', '')
        sf(path, 'scale', 1.4)
        sf(path, 'description', 'tagNewHero87')
        sf(path, 'characterRacialProfile', 'Beastman')
        sf(path, 'controller', CONTROLLER)
        sf(path, 'charAnimationTableName', '')  # clear Lyia's; mesh has defaults

        # Override stats (dtype=None preserves clone's FLOAT types)
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 500.0)
        sf(path, 'characterManaRegen', 20.0)
        sf(path, 'characterStrength', 350.0)
        sf(path, 'characterDexterity', 300.0)
        sf(path, 'characterIntelligence', 200.0)
        sf(path, 'characterAttackSpeed', 0.85)
        sf(path, 'characterRunSpeed', 1.3)
        sf(path, 'characterSpellCastSpeed', 1.4)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))

        # Pet behavior — dropItems=0 prevents equipped gear from dropping as
        # loot when the pet dies (the lootItem fields still control what the
        # pet visually equips, but nothing is dropped on death).
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)

        # Party UI icons
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # ── Clone summon skill from Lyia (already permanent, no TTL) ─────────
    summon_path = SUMMON_RAKANIZEUS_SKILL
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Lyia summon {lyia_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonRakanizeus')
    sf(summon_path, 'skillManaCost', [300.0, 350.0, 400.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'rakanizeus_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3)

    print("  Rakanizeus summon: cloned 3 pet records from Lyia + summon skill")
    return True


def _create_boneash_pet_skill(db):
    """Create Boneash pet records by cloning from Lyia Leafsong.

    Boneash is a fire skeleton caster — slow movement, high INT, devastating
    fire spells (Fireball, Pillar of Flame, Flamestrike, Ternion).
    Clones from Lyia for a clean Pet.tpl baseline, then replaces animations,
    equipment, and skills with the real Boneash monster's.
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    pet_paths = [
        r'records\skills\soulskills\pets\boneash_1.dbr',
        r'records\skills\soulskills\pets\boneash_2.dbr',
        r'records\skills\soulskills\pets\boneash_3.dbr',
    ]

    # Per-level scaling
    life =       [3500, 5000, 6500]
    life_regen = [20.0, 35.0, 50.0]
    dmg_min =    [40, 60, 80]
    dmg_max =    [60, 90, 120]

    # Find the real Boneash monster record
    boneash_monster = _find_record(
        db, r'records\creature\monster\skeleton\um_boneash_30.dbr')
    if not boneash_monster:
        print("  WARNING: Boneash monster record not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Replace Lyia's animations and skills with Boneash's.
        if boneash_monster:
            na = _copy_animation_fields(db, boneash_monster, path)
            ns = _update_existing_fields(db, boneash_monster, path, _SKILL_PREFIXES)
            if i == 0:
                print(f"  Copied from Boneash monster: {na} anim, {ns} skill fields")

        sf = db.set_field

        # ── Equipment: fixed items per difficulty (skeleton caster loadout) ─
        # [Normal, Epic, Legendary] — game picks by current difficulty.
        _ST = r'records\item\equipmentweapon\staff'
        _AB = r'records\item\equipmentarmband'
        _RG = r'records\item\equipmentring'
        _set_pet_equipment(db, path, {
            # Staves: Solaris (N) → Blastos Fotia (E) → Staff of Elysium (L)
            'chanceToEquipLeftHand': 100.0,
            'chanceToEquipLeftHandItem1': 5000,
            'lootLeftHandItem1': [
                _ST + r'\u_n_solaris.dbr',
                _ST + r'\u_e_blastosfotia.dbr',
                _ST + r'\u_l_staffofelysium.dbr',
            ],
            # Arms: Oracle's Winding (N) → Adept's Clasp (E) → Archmage's (L)
            'chanceToEquipForearm': 100.0,
            'chanceToEquipForearmItem1': 5000,
            'lootForearmItem1': [
                _AB + "\\usm_n_oracle'sgarments.dbr",
                _AB + "\\usm_e_adept'sregalia.dbr",
                _AB + "\\usm_l_archmage'sregalia.dbr",
            ],
            # Rings: Cartouche (N) → Star Stone (E) → Seal of Hephaestus (L)
            'chanceToEquipFinger1': 100.0,
            'chanceToEquipFinger1Item1': 5000,
            'lootFinger1Item1': [
                _RG + r'\u_n_cartouchering.dbr',
                _RG + r'\u_e_starstone.dbr',
                _RG + r'\u_l_sealofhephaestus.dbr',
            ],
        })
        if i == 0:
            print("  Boneash equipment: staff/armband/ring (N/E/L tiered)")

        # Override identity (scale/height/texture match the real Boneash boss)
        sf(path, 'charLevel', i + 1)
        sf(path, 'mesh', r'Creatures\Monster\Skeleton\RevenantFire.msh')
        sf(path, 'scale', 1.5)
        sf(path, 'actorHeight', 2.0)
        sf(path, 'baseTexture',
           r'Creatures\Monster\Skeleton\NewSkeleton_Charcoal.tex')
        sf(path, 'charAnimationTableName',
           r'records\creature\monster\skeleton\anm\anm_skeleton01.dbr')
        sf(path, 'description', 'tagNewHero48')
        sf(path, 'characterRacialProfile', 'Undead')
        sf(path, 'controller', CONTROLLER)

        # Override stats (dtype=None preserves clone's FLOAT types)
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 1200.0)
        sf(path, 'characterManaRegen', 30.0)
        sf(path, 'characterStrength', 150.0)
        sf(path, 'characterDexterity', 150.0)
        sf(path, 'characterIntelligence', 400.0)
        sf(path, 'characterAttackSpeed', 1.2)
        sf(path, 'characterRunSpeed', 0.75)
        sf(path, 'characterSpellCastSpeed', 1.5)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))

        # Pet behavior — dropItems=0 prevents equipped gear from dropping as
        # loot when the pet dies (the lootItem fields still control what the
        # pet visually equips, but nothing is dropped on death).
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)

        # Party UI icons
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\spirit\bonefiendup.tex')
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\spirit\bonefienddown.tex')

    # ── Clone summon skill from Lyia (already permanent, no TTL) ─────────
    summon_path = SUMMON_BONEASH_SKILL
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Lyia summon {lyia_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonBoneash')
    sf(summon_path, 'skillManaCost', [250.0, 300.0, 350.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\spirit\bonefiendup.tex')
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\spirit\bonefienddown.tex')

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boneash_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3)

    print("  Boneash summon: cloned 3 pet records from Lyia + summon skill")
    return True


def _create_pharaoh_guard_pet_skill(db):
    """Create Pharaoh's Honor Guard pet records by cloning from Lyia.

    The Honor Guard is a tanky construct (stone guardian statue) — slow movement,
    high life, high physical damage, no mana/magic.  Fights barehanded (no equipment).
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    pet_paths = [
        r'records\skills\soulskills\pets\pharaohguard_1.dbr',
        r'records\skills\soulskills\pets\pharaohguard_2.dbr',
        r'records\skills\soulskills\pets\pharaohguard_3.dbr',
    ]

    # Per-level scaling: tanky slow construct
    life =       [5000, 7500, 10000]
    life_regen = [30.0, 50.0, 70.0]
    dmg_min =    [55, 80, 110]
    dmg_max =    [85, 120, 160]

    # Find the real Honor Guard monster record
    guard_monster = _find_record(
        db, r'records\creature\monster\questbosses\boss_pharaohshonorguard1_31.dbr')
    if not guard_monster:
        print("  WARNING: Pharaoh's Honor Guard monster record not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Replace Lyia's animations and skills with Honor Guard's.
        if guard_monster:
            na = _copy_animation_fields(db, guard_monster, path)
            ns = _update_existing_fields(db, guard_monster, path, _SKILL_PREFIXES)
            if i == 0:
                print(f"  Copied from Honor Guard monster: {na} anim, {ns} skill fields")

        sf = db.set_field

        # No equipment — construct fights barehanded (like the real monster)
        # Disable all equipment slots inherited from Lyia
        for slot in ('LeftHand', 'RightHand', 'Forearm', 'Finger1',
                     'Finger2', 'Head', 'Torso', 'LowerBody',
                     'Misc1', 'Misc2', 'Misc3'):
            sf(path, f'chanceToEquip{slot}', 0.0)
        if i == 0:
            print("  Honor Guard equipment: none (barehanded construct)")

        # Override identity
        sf(path, 'charLevel', i + 1)
        sf(path, 'mesh', r'Creatures\Monster\GuardianStatue\StatuePossesed.msh')
        sf(path, 'baseTexture', '')  # use mesh default
        sf(path, 'bumpTexture', '')
        sf(path, 'scale', 1.1)
        sf(path, 'actorHeight', 1.7)
        sf(path, 'description', 'tagMonsterName1180')
        sf(path, 'characterRacialProfile', 'Construct')
        sf(path, 'controller', CONTROLLER)
        sf(path, 'charAnimationTableName', '')

        # Override stats — tanky slow melee (dtype=None preserves FLOAT)
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 0.0)
        sf(path, 'characterManaRegen', 0.0)
        sf(path, 'characterStrength', 350.0)
        sf(path, 'characterDexterity', 150.0)
        sf(path, 'characterIntelligence', 0.0)
        sf(path, 'characterAttackSpeed', 1.0)
        sf(path, 'characterRunSpeed', 0.7)
        sf(path, 'characterSpellCastSpeed', 1.0)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))

        # Pet behavior — dropItems=0 prevents any loot from dropping when
        # the pet dies (consistent with all other soul pets).
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)

        # Party UI icons (use generic summon icons)
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # ── Clone summon skill from Lyia (already permanent, no TTL) ─────────
    summon_path = SUMMON_PHARAOH_GUARD_SKILL
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Lyia summon {lyia_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonPharaohGuard')
    sf(summon_path, 'skillManaCost', [350.0, 400.0, 450.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'pharaohshonorguard_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3)

    print("  Pharaoh Guard summon: cloned 3 pet records from Lyia + summon skill")
    return True


def _update_pharaoh_guard_drop_rate(db):
    """Change Pharaoh's Honor Guard soul drop rate from 2.25% to 10%."""
    updated = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'pharaohshonorguard' in nl and 'creature' in nl:
            fields = db.get_fields(name)
            if not fields:
                continue
            # Check if this record has a soul drop (chanceToEquipFinger2 > 0)
            for key, tf in fields.items():
                fn = key.split('###')[0]
                if fn == 'chanceToEquipFinger2' and tf.values and float(tf.values[0]) > 0:
                    db.set_field(name, 'chanceToEquipFinger2', 10.0)
                    db._modified.add(name)
                    updated += 1
                    break
    print(f"  Pharaoh's Honor Guard drop rate: 2.25% -> 10% ({updated} monster records)")
    return updated


def _fix_low_boss_soul_drop_rates(db):
    """Raise soul drop rates to 25% for major bosses that have very low rates."""
    bosses = [
        ('boss_titan_typhon', 'Typhon', 25.0),
        ('boss_hadesform3', 'Hades Form 3', 25.0),
        ('boss_greektelkine_megalesios', 'Megalesios', 25.0),
        ('boss_chinatelkine_ormenos', 'Ormenos', 25.0),
        ('boss_cerberus', 'Cerberus', 25.0),
    ]
    total = 0
    for tag, label, target_rate in bosses:
        updated = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if tag in nl:
                fields = db.get_fields(name)
                if not fields:
                    continue
                # Check if this record has a soul drop (chanceToEquipFinger2 > 0)
                for key, tf in fields.items():
                    fn = key.split('###')[0]
                    if fn == 'chanceToEquipFinger2' and tf.values and float(tf.values[0]) > 0:
                        db.set_field(name, 'chanceToEquipFinger2', target_rate, DATA_TYPE_FLOAT)
                        db._modified.add(name)
                        updated += 1
                        break
        print(f"  {label} drop rate -> {target_rate}% ({updated} monster records)")
        total += updated
    return total


def _wire_missing_boss_souls(db):
    """Wire soul drops onto boss variants that are missing them."""
    total = 0

    # ── Helper: find lootFinger2Item1 values from a donor record ────────
    def _get_soul_paths(tag):
        """Find lootFinger2Item1 [N, E, L] from any record matching tag."""
        for name in db.record_names():
            nl = name.lower()
            if tag in nl:
                fields = db.get_fields(name)
                if not fields:
                    continue
                for key, tf in fields.items():
                    fn = key.split('###')[0]
                    if fn == 'lootFinger2Item1' and tf.values and len(tf.values) >= 3:
                        return list(tf.values)
        return None

    def _wire_soul(name, soul_paths, chance):
        """Set lootFinger2Item1 and chanceToEquipFinger2 on a record."""
        db.set_field(name, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
        db.set_field(name, 'chanceToEquipFinger2', chance, DATA_TYPE_FLOAT)
        db.set_field(name, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
        db._modified.add(name)

    # ── xpack Ormenos: wire soul from regular Ormenos variants ──────────
    ormenos_souls = _get_soul_paths('boss_chinatelkine_ormenos')
    if ormenos_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if 'boss_chinatelkine_ormenos' in nl and 'xpack' in nl:
                # Check it doesn't already have a soul wired
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, ormenos_souls, 25.0)
                    wired += 1
        print(f"  Ormenos xpack soul wired: {wired} records (soul: {ormenos_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Ormenos soul paths to wire xpack variants")

    # ── xpack Yaoguai: wire soul from regular Yaoguai variants ──────────
    yaoguai_souls = _get_soul_paths('boss_daemonbull_yaoguai')
    if yaoguai_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if 'boss_daemonbull_yaoguai' in nl and 'xpack' in nl:
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, yaoguai_souls, 25.0)
                    wired += 1
        print(f"  Yaoguai xpack soul wired: {wired} records (soul: {yaoguai_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Yaoguai soul paths to wire xpack variants")

    # ── Charon Form 1: wire uber soul from boss_charon_39 ───────────────
    charon_souls = _get_soul_paths('boss_charon_39')
    if charon_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if ('boss_charon_41' in nl or 'boss_charon_43' in nl):
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, charon_souls, 66.0)
                    wired += 1
        print(f"  Charon Form 1 (41/43) soul wired: {wired} records (soul: {charon_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Charon_39 soul paths to wire Charon 41/43")

    # ── Hydra: wire soul from boss_hydra_66 ─────────────────────────────
    hydra_souls = _get_soul_paths('boss_hydra_66')
    if hydra_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if ('boss_hydra_60' in nl or 'boss_hydra_63' in nl):
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, hydra_souls, 25.0)
                    wired += 1
        print(f"  Hydra (60/63) soul wired: {wired} records (soul: {hydra_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Hydra_66 soul paths to wire Hydra 60/63")

    return total


def _add_dagon_to_ichthian_pools(db):
    """Add Dagon as a rare champion spawn in all ichthian spawn pools."""
    DAGON_RECORD = r'records\test\boss_dagon_66.dbr'
    DAGON_WEIGHT = 2  # Very rare spawn

    if not db.has_record(DAGON_RECORD):
        print("  WARNING: Dagon record not found in database")
        return 0

    # Find all ichthian spawn pools (records with nameN fields referencing ichthian)
    ichthian_pools = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        has_ichthian = False
        has_name_field = False
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn.startswith('name') and not fn.startswith('nameChampion'):
                has_name_field = True
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'ichthian' in v.lower():
                        has_ichthian = True
                        break
        if has_ichthian and has_name_field:
            ichthian_pools.append(name)

    total = 0
    for pool in ichthian_pools:
        fields = db.get_fields(pool)
        if not fields:
            continue

        # Check if Dagon is already in this pool
        already_has = False
        for key, tf in fields.items():
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'boss_dagon' in v.lower():
                        already_has = True
                        break
        if already_has:
            continue

        # Find the highest existing nameChampionN index
        max_champ_idx = 0
        for key in fields:
            fn = key.split('###')[0]
            m = __import__('re').match(r'nameChampion(\d+)', fn)
            if m:
                idx = int(m.group(1))
                if idx > max_champ_idx:
                    max_champ_idx = idx

        # Add Dagon at the next champion slot
        next_idx = max_champ_idx + 1
        db.set_field(pool, f'nameChampion{next_idx}', DAGON_RECORD, DATA_TYPE_STRING)
        db.set_field(pool, f'weightChampion{next_idx}', DAGON_WEIGHT, DATA_TYPE_INT)
        db._modified.add(pool)

        # Ensure champion spawning is enabled if it wasn't
        champ_chance = db.get_field_value(pool, 'championChance')
        if champ_chance is not None and float(champ_chance) == 0.0:
            db.set_field(pool, 'championChance', 15.0, DATA_TYPE_FLOAT)
            db.set_field(pool, 'championMax', 1, DATA_TYPE_INT)

        total += 1

    print(f"  Dagon added to {total} ichthian spawn pools as rare champion (weight={DAGON_WEIGHT})")
    return total


def _add_coldworm_to_egypt_pools(db):
    """Add Cold Worm as a rare champion spawn in Act 2 Egypt underground/insect pools."""
    COLDWORM_RECORD = r'records\test\boss_coldworm50.dbr'
    COLDWORM_WEIGHT = 2  # Very rare spawn

    if not db.has_record(COLDWORM_RECORD):
        print("  WARNING: Cold Worm record not found in database")
        return 0

    # Target: all cryptworm pools + scavenger beetle pools + bone scarab pools
    # These are Egypt underground cave/tomb insectoid pools
    target_pools = []
    for name in db.record_names():
        nl = name.lower()
        if 'proxies egypt' not in nl and 'proxies egypt' not in nl.replace('\\', ' '):
            # Also check with backslash
            if r'proxies egypt' not in nl:
                continue
        if 'pools' not in nl:
            continue
        # Match cryptworm, scavenger beetle, bone scarab, scorpion pools
        basename = nl.replace('\\', '/').split('/')[-1]
        if any(tag in basename for tag in ('cryptworm_', 'scavengerbeetle_', 'bonescarab_', 'scorpion_')):
            target_pools.append(name)

    total = 0
    for pool in target_pools:
        fields = db.get_fields(pool)
        if not fields:
            continue

        # Check if Cold Worm is already in this pool
        already_has = False
        for key, tf in fields.items():
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'boss_coldworm' in v.lower():
                        already_has = True
                        break
        if already_has:
            continue

        # Find the highest existing nameChampionN index
        max_champ_idx = 0
        for key in fields:
            fn = key.split('###')[0]
            m = __import__('re').match(r'nameChampion(\d+)', fn)
            if m:
                idx = int(m.group(1))
                if idx > max_champ_idx:
                    max_champ_idx = idx

        # Add Cold Worm at the next champion slot
        next_idx = max_champ_idx + 1
        db.set_field(pool, f'nameChampion{next_idx}', COLDWORM_RECORD, DATA_TYPE_STRING)
        db.set_field(pool, f'weightChampion{next_idx}', COLDWORM_WEIGHT, DATA_TYPE_INT)
        db._modified.add(pool)

        # Ensure champion spawning is enabled if it wasn't
        champ_chance = db.get_field_value(pool, 'championChance')
        if champ_chance is not None and float(champ_chance) == 0.0:
            db.set_field(pool, 'championChance', 15.0, DATA_TYPE_FLOAT)
            db.set_field(pool, 'championMax', 1, DATA_TYPE_INT)

        total += 1

    print(f"  Cold Worm added to {total} Egypt underground/insect spawn pools (weight={COLDWORM_WEIGHT})")
    return total


def _create_coldworm_soul(db):
    """Create a hand-crafted Cold Worm soul and wire it to the monster.

    Cold Worm is a level 30/50/65 boss using CryptWorm mesh.  It uses poison
    gas, shockwave, and summons bugs.  The soul has a cold/poison theme with
    defensive bonuses, an ice-blast on-hit proc, and cold/poison augments.
    Drop rate: 66%.
    """
    COLDWORM_MONSTER = r'records\test\boss_coldworm50.dbr'
    SOUL_BASE = r'records\item\equipmentring\soul\svc_uber'

    if not db.has_record(COLDWORM_MONSTER):
        print("  WARNING: Cold Worm monster record not found")
        return False

    # ── Difficulty-scaled stats (N=Lv30, E=Lv50, L=Lv65) ──────────────
    # Comparable to peers: Arachne (Lv61), Scorpos (Lv63), Boneash (Lv65)
    # Scorpos L: +409 Life, 88-93 poison, +42% poison modifier
    # Arachne L: +23 Dex, +14% AS, 45-49 poison, +46% poison res
    tiers = [
        # (suffix, itemLevel, levelReq, skillLv, augLv1, augLv2,
        #  defCold, defPoison, coldMin, coldMax, poisMin, poisMax, poisDur,
        #  coldMod, poisMod, life, mana, str, int, DA, castSpeed)
        ('n', 30, 25, 2, 2, 2,
         18.0, 15.0, 10.0, 22.0, 18.0, 35.0, 3.0,
         12, 15, 150, 80, 14, 12, 30, 10),
        ('e', 50, 45, 4, 3, 3,
         30.0, 25.0, 22.0, 40.0, 35.0, 60.0, 3.0,
         25, 30, 280, 140, 22, 20, 55, 18),
        ('l', 65, 60, 6, 5, 5,
         42.0, 38.0, 35.0, 58.0, 50.0, 85.0, 4.0,
         40, 48, 380, 200, 30, 28, 85, 25),
    ]

    soul_paths = []
    for (diff, item_lv, lv_req, sk_lv, aug1_lv, aug2_lv,
         def_cold, def_poison, cold_min, cold_max, pois_min, pois_max, pois_dur,
         cold_mod, pois_mod,
         life, mana, strength, intel, da, cast_speed) in tiers:

        path = f'{SOUL_BASE}\\boss_coldworm50_soul_{diff}.dbr'
        soul_paths.append(path)

        _ensure_record(db, path, SOUL_TEMPLATE)

        # Boilerplate fields
        base = {
            'templateName': (DATA_TYPE_STRING, SOUL_TEMPLATE),
            'Class': (DATA_TYPE_STRING, 'ArmorJewelry_Ring'),
            'bitmap': (DATA_TYPE_STRING, r'Items\miscellaneous\n_soul.tex'),
            'mesh': (DATA_TYPE_STRING, r'drx\meshes\n_soulmesh.msh'),
            'itemCostName': (DATA_TYPE_STRING, 'records/game/itemcost_soul.dbr'),
            'dropSound': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDropPak.dbr'),
            'dropSound3D': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDrop3DPak.dbr'),
            'dropSoundWater': (DATA_TYPE_STRING, r'Records\Sounds\SoundPak\Items\WaterSmDropPak.dbr'),
            'itemClassification': (DATA_TYPE_STRING, 'Magical'),
            'characterBaseAttackSpeedTag': (DATA_TYPE_STRING, 'CharacterAttackSpeedAverage'),
            'castsShadows': (DATA_TYPE_INT, 1),
            'maxTransparency': (DATA_TYPE_FLOAT, 0.5),
            'scale': (DATA_TYPE_FLOAT, 1.0),
            'shadowBias': (DATA_TYPE_FLOAT, 0.01),
            'cannotPickUp': (DATA_TYPE_INT, 0),
            'cannotPickUpMultiple': (DATA_TYPE_INT, 0),
            'hidePrefixName': (DATA_TYPE_INT, 0),
            'hideSuffixName': (DATA_TYPE_INT, 0),
            'quest': (DATA_TYPE_INT, 0),
            'itemLevel': (DATA_TYPE_INT, item_lv),
            'levelRequirement': (DATA_TYPE_INT, lv_req),
            'strengthRequirement': (DATA_TYPE_INT, 0),
            'intelligenceRequirement': (DATA_TYPE_INT, 0),
            'dexterityRequirement': (DATA_TYPE_INT, 0),
            'numRelicSlots': (DATA_TYPE_INT, 1),
            'itemNameTag': (DATA_TYPE_STRING, 'tagD2Boss004'),
            'FileDescription': (DATA_TYPE_STRING, f'boss_coldworm50 soul ({diff.upper()})'),
        }
        _set_soul_fields(db, path, base)

        # Cold/poison themed stats — scaled per difficulty
        stats = {
            # On-hit proc: ice blast
            'itemSkillName': (DATA_TYPE_STRING, r'records\skills\soulskills\gargantuanyeti_iceblast.dbr'),
            'itemSkillLevel': (DATA_TYPE_INT, sk_lv),
            'itemSkillAutoController': (DATA_TYPE_STRING, _AC_ON_HIT),
            # Augment 1: Cold aura
            'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxcoldaura.dbr'),
            'augmentSkillLevel1': (DATA_TYPE_INT, aug1_lv),
            # Augment 2: Plague (poison)
            'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\nature\drxplague.dbr'),
            'augmentSkillLevel2': (DATA_TYPE_INT, aug2_lv),
            # Defensive: cold & poison resistance
            'defensiveCold': (DATA_TYPE_FLOAT, def_cold),
            'defensivePoison': (DATA_TYPE_FLOAT, def_poison),
            # Offensive: cold + poison flat damage
            'offensiveColdMin': (DATA_TYPE_FLOAT, cold_min),
            'offensiveColdMax': (DATA_TYPE_FLOAT, cold_max),
            'offensiveSlowPoisonMin': (DATA_TYPE_FLOAT, pois_min),
            'offensiveSlowPoisonMax': (DATA_TYPE_FLOAT, pois_max),
            'offensiveSlowPoisonDurationMin': (DATA_TYPE_FLOAT, pois_dur),
            # Offensive: % damage modifiers
            'offensiveColdModifier': (DATA_TYPE_INT, cold_mod),
            'offensiveSlowPoisonModifier': (DATA_TYPE_INT, pois_mod),
            # Stat bonuses
            'characterLife': (DATA_TYPE_INT, life),
            'characterMana': (DATA_TYPE_INT, mana),
            'characterStrength': (DATA_TYPE_INT, strength),
            'characterIntelligence': (DATA_TYPE_INT, intel),
            'characterDefensiveAbility': (DATA_TYPE_INT, da),
            'characterSpellCastSpeedModifier': (DATA_TYPE_INT, cast_speed),
        }
        _set_soul_fields(db, path, stats)

    # ── Wire soul to monster record with 66% drop rate ──────────────────
    db.set_field(COLDWORM_MONSTER, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
    db.set_field(COLDWORM_MONSTER, 'chanceToEquipFinger2', 66.0, DATA_TYPE_FLOAT)
    db.set_field(COLDWORM_MONSTER, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
    db._modified.add(COLDWORM_MONSTER)

    print("  Cold Worm soul created (cold/poison theme, Lv 50, 66% drop rate)")
    print(f"    Paths: {soul_paths[0].split(chr(92))[-1]} / _e / _l")
    return True


# ── Shared boilerplate for hand-crafted soul creation ─────────────────────

_SOUL_BOILERPLATE = {
    'templateName': (DATA_TYPE_STRING, SOUL_TEMPLATE),
    'Class': (DATA_TYPE_STRING, 'ArmorJewelry_Ring'),
    'bitmap': (DATA_TYPE_STRING, r'Items\miscellaneous\n_soul.tex'),
    'mesh': (DATA_TYPE_STRING, r'drx\meshes\n_soulmesh.msh'),
    'itemCostName': (DATA_TYPE_STRING, 'records/game/itemcost_soul.dbr'),
    'dropSound': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDropPak.dbr'),
    'dropSound3D': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDrop3DPak.dbr'),
    'dropSoundWater': (DATA_TYPE_STRING, r'Records\Sounds\SoundPak\Items\WaterSmDropPak.dbr'),
    'itemClassification': (DATA_TYPE_STRING, 'Magical'),
    'characterBaseAttackSpeedTag': (DATA_TYPE_STRING, 'CharacterAttackSpeedAverage'),
    'castsShadows': (DATA_TYPE_INT, 1),
    'maxTransparency': (DATA_TYPE_FLOAT, 0.5),
    'scale': (DATA_TYPE_FLOAT, 1.0),
    'shadowBias': (DATA_TYPE_FLOAT, 0.01),
    'cannotPickUp': (DATA_TYPE_INT, 0),
    'cannotPickUpMultiple': (DATA_TYPE_INT, 0),
    'hidePrefixName': (DATA_TYPE_INT, 0),
    'hideSuffixName': (DATA_TYPE_INT, 0),
    'quest': (DATA_TYPE_INT, 0),
    'numRelicSlots': (DATA_TYPE_INT, 1),
    'strengthRequirement': (DATA_TYPE_INT, 0),
    'intelligenceRequirement': (DATA_TYPE_INT, 0),
    'dexterityRequirement': (DATA_TYPE_INT, 0),
}

_SOUL_DIR = r'records\item\equipmentring\soul\svc_uber'


def _create_soul(db, base_name, tag, tiers, monster=None, drop_rate=66.0):
    """Create a hand-crafted soul with N/E/L difficulty scaling.

    tiers: list of 3 dicts, each with 'diff', 'itemLevel', and 'stats' keys.
    stats values are (dtype, value) tuples.
    Returns list of [n, e, l] soul paths.
    """
    soul_paths = []
    for tier in tiers:
        diff = tier['diff']
        path = f'{_SOUL_DIR}\\{base_name}_soul_{diff}.dbr'
        soul_paths.append(path)

        _ensure_record(db, path, SOUL_TEMPLATE)
        _set_soul_fields(db, path, _SOUL_BOILERPLATE)
        _set_soul_fields(db, path, {
            'itemLevel': (DATA_TYPE_INT, tier['itemLevel']),
            'levelRequirement': (DATA_TYPE_INT, max(1, tier['itemLevel'] - 5)),
            'itemNameTag': (DATA_TYPE_STRING, tag),
            'FileDescription': (DATA_TYPE_STRING, f'{base_name} soul ({diff.upper()})'),
        })
        _set_soul_fields(db, path, tier['stats'])

    if monster and db.has_record(monster):
        db.set_field(monster, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
        db.set_field(monster, 'chanceToEquipFinger2', drop_rate, DATA_TYPE_FLOAT)
        db.set_field(monster, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
        db._modified.add(monster)

    return soul_paths


# ── Skill path shortcuts for soul designs ─────────────────────────────────

_SK_PHANTOM_STRIKE = r'records\skills\dream\drxphantomstrike.dbr'
_SK_DISTORTION_WAVE = r'records\skills\dream\drxdistortionwave.dbr'
_SK_DISTORTION_FIELD = r'records\skills\dream\drxdistortionfield.dbr'
_SK_LUCID_DREAM = r'records\skills\dream\drxluciddream.dbr'
_SK_LETHAL_STRIKE = r'records\skills\stealth\drxlethalstrike.dbr'
_SK_BATTLE_RAGE = r'records\skills\warfare\drxbattlerage.dbr'
_SK_ONSLAUGHT = r'records\skills\warfare\drxonslaught.dbr'
_SK_DUAL_WEAPON = r'records\skills\warfare\drxdualweapontraining.dbr'
_SK_DARK_COVENANT = r'records\skills\spirit\drxdarkcovenant.dbr'
_SK_DEATH_CHILL = r'records\skills\spirit\drxdeathchillaura.dbr'
_SK_TERNION = r'records\skills\spirit\drxternion.dbr'
_SK_ENVENOM = r'records\skills\stealth\drxenvenomweapon.dbr'
_SK_PLAGUE = r'records\skills\nature\drxplague.dbr'
_SK_COLD_AURA = r'records\skills\storm\drxcoldaura.dbr'

# Soul skill procs
_SS_RING_LIGHTNING = r'records\skills\soulskills\ringoflightning.dbr'
_SS_BLOOD_BOIL = r'records\skills\soulskills\melinoe_bloodboil.dbr'
_SS_GROUND_SMASH = r'records\skills\soulskills\cyclops_groundsmash.dbr'
_SS_VENOM_SPRAY = r'records\skills\soulskills\arachne_venomspray.dbr'
_SS_FLASH_POWDER = r'records\skills\soulskills\toxeus_flashpowder.dbr'


def _create_sp_toxeus_soul(db):
    """SP Toxeus (um_toxeus_99) — Tier 1: THE strongest soul in the game.

    Dream/Rogue assassin hybrid. Phantom Strike teleport, Distortion Wave,
    Distort Reality (phys + life + electrocution), extreme dodge and deflect.
    Level 33/66/99.  Must surpass Canace (current #1 soul).
    """
    MONSTER = r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr'
    TAG = 'tagSVCSoulSPToxeus'

    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = [
        {'diff': 'n', 'itemLevel': 33, 'stats': {
            # Proc: Ring of Lightning on hit (electrocution from Distortion Wave)
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            # Augments: Dream mastery — his signature moves
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 3),
            # Offensive: physical + life + electrocution (Distort Reality profile)
            'offensivePhysicalMin': (F, 50.0), 'offensivePhysicalMax': (F, 80.0),
            'offensiveLifeMin': (F, 35.0), 'offensiveLifeMax': (F, 55.0),
            'offensiveSlowLightningMin': (F, 80.0),
            'offensiveSlowLightningDurationMin': (F, 4.0),
            'offensivePhysicalModifier': (I, 30),
            'offensiveLifeModifier': (I, 25),
            'offensivePierceRatioModifier': (I, 15),
            'offensiveLifeLeechMin': (F, 35.0),
            'offensivePercentCurrentLifeMin': (F, 5.0),
            # Defensive: dodge + deflect (his passive properties)
            'characterDodgePercent': (F, 10.0),
            'characterDeflectProjectile': (F, 10.0),
            'defensiveLife': (F, 15.0),
            'characterEnergyAbsorptionPercent': (F, 15.0),
            # Speed (assassin)
            'characterAttackSpeedModifier': (I, 12),
            'characterTotalSpeedModifier': (I, 8),
            'characterRunSpeedModifier': (F, 10.0),
            # % Stats (favor modifiers over flat)
            'characterLifeModifier': (F, 10.0),
            'characterManaModifier': (F, 8.0),
            'characterStrengthModifier': (F, 6.0),
            'characterDexterityModifier': (F, 8.0),
            'characterIntelligenceModifier': (F, 5.0),
            'characterOffensiveAbilityModifier': (F, 6.0),
            'characterDefensiveAbilityModifier': (F, 5.0),
            # % Reflect, Armor, Life (user-requested)
            'defensiveReflect': (F, 8.0),
            'defensiveProtectionModifier': (F, 10.0),
        }},
        {'diff': 'e', 'itemLevel': 66, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE),
            'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 4),
            'offensivePhysicalMin': (F, 90.0), 'offensivePhysicalMax': (F, 140.0),
            'offensiveLifeMin': (F, 60.0), 'offensiveLifeMax': (F, 100.0),
            'offensiveSlowLightningMin': (F, 150.0),
            'offensiveSlowLightningDurationMin': (F, 4.0),
            'offensivePhysicalModifier': (I, 55),
            'offensiveLifeModifier': (I, 45),
            'offensivePierceRatioModifier': (I, 22),
            'offensiveLifeLeechMin': (F, 60.0),
            'offensivePercentCurrentLifeMin': (F, 8.0),
            'characterDodgePercent': (F, 14.0),
            'characterDeflectProjectile': (F, 15.0),
            'defensiveLife': (F, 22.0),
            'characterEnergyAbsorptionPercent': (F, 25.0),
            'characterAttackSpeedModifier': (I, 16),
            'characterTotalSpeedModifier': (I, 12),
            'characterRunSpeedModifier': (F, 15.0),
            'characterLifeModifier': (F, 18.0),
            'characterManaModifier': (F, 14.0),
            'characterStrengthModifier': (F, 10.0),
            'characterDexterityModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterOffensiveAbilityModifier': (F, 10.0),
            'characterDefensiveAbilityModifier': (F, 8.0),
            'defensiveReflect': (F, 12.0),
            'defensiveProtectionModifier': (F, 16.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE),
            'augmentSkillLevel1': (I, 6),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 5),
            # Massive offensive: phys + life + electrocution
            'offensivePhysicalMin': (F, 140.0), 'offensivePhysicalMax': (F, 210.0),
            'offensiveLifeMin': (F, 95.0), 'offensiveLifeMax': (F, 150.0),
            'offensiveSlowLightningMin': (F, 240.0),
            'offensiveSlowLightningDurationMin': (F, 4.0),
            'offensivePhysicalModifier': (I, 85),
            'offensiveLifeModifier': (I, 70),
            'offensivePierceRatioModifier': (I, 30),
            'offensiveLifeLeechMin': (F, 90.0),
            'offensivePercentCurrentLifeMin': (F, 12.0),
            # Extreme evasion (Toxeus passive: 15% dodge, 33% deflect)
            'characterDodgePercent': (F, 18.0),
            'characterDeflectProjectile': (F, 22.0),
            'defensiveLife': (F, 30.0),
            'characterEnergyAbsorptionPercent': (F, 35.0),
            'defensiveManaBurnRatio': (F, 40.0),
            # Assassin speed
            'characterAttackSpeedModifier': (I, 20),
            'characterTotalSpeedModifier': (I, 16),
            'characterRunSpeedModifier': (F, 20.0),
            # % Stats (Tier 1 — strongest in game)
            'characterLifeModifier': (F, 25.0),
            'characterManaModifier': (F, 20.0),
            'characterStrengthModifier': (F, 15.0),
            'characterDexterityModifier': (F, 18.0),
            'characterIntelligenceModifier': (F, 12.0),
            'characterOffensiveAbilityModifier': (F, 15.0),
            'characterDefensiveAbilityModifier': (F, 12.0),
            # % Reflect + Armor (user-requested)
            'defensiveReflect': (F, 15.0),
            'defensiveProtectionModifier': (F, 22.0),
        }},
    ]

    paths = _create_soul(db, 'sp_toxeus', TAG, tiers, MONSTER, 66.0)
    print(f"  SP Toxeus soul created (Tier 1 — Dream/Rogue assassin, 66% drop)")
    return paths


def _overhaul_main_toxeus_soul(db):
    """Main Toxeus (um_toxeus_21) — Tier 3: massively boost existing soul.

    Rogue/Warfare hybrid. Bladestorm, Flash Powder, Lethal Strike, Envenom
    Weapon, Shield Charge.  Keeps Flash Powder proc + Lethal Strike/Battle
    Rage augments from original soul but with much stronger stats.
    Level 25/45/65.
    """
    # Existing souls at records\item\equipmentring\soul\skeleton\toxeus_soul_*.dbr
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = {
        'n': {
            'itemSkillLevel': (I, 6),  # boost Flash Powder proc
            'augmentSkillLevel1': (I, 5),  # Lethal Strike
            'augmentSkillLevel2': (I, 5),  # Battle Rage
            # Massive physical + pierce + bleed (Bladestorm profile)
            'offensivePhysicalMin': (F, 55.0), 'offensivePhysicalMax': (F, 75.0),
            'offensivePierceMin': (F, 30.0),
            'offensivePierceRatioModifier': (I, 40),
            'offensivePhysicalModifier': (I, 30),
            'offensiveSlowBleedingMin': (F, 80.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            # Envenom weapon theme
            'offensiveSlowPoisonMin': (F, 35.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowTotalSpeedMin': (F, 10.0),
            'offensiveSlowTotalSpeedDurationMin': (F, 3.0),
            # Speed & evasion
            'characterAttackSpeedModifier': (F, 12.0),
            'characterTotalSpeedModifier': (I, 10),
            'characterRunSpeedModifier': (F, 8.0),
            'characterDodgePercent': (F, 8.0),
            'characterDeflectProjectile': (F, 8.0),
            # % Stats (favor modifiers)
            'characterOffensiveAbilityModifier': (F, 4.0),
            'characterDefensiveAbilityModifier': (F, 4.0),
            'characterLifeModifier': (F, 6.0),
            'characterStrengthModifier': (F, 5.0), 'characterDexterityModifier': (F, 6.0),
            'defensiveReflect': (F, 40.0),
            'defensiveProtectionModifier': (F, 8.0),
            'defensivePierce': (F, 20.0),
            'characterEnergyAbsorptionPercent': (F, 15.0),
            'racialBonusPercentDamage': (F, 40.0),  # vs Undead
        },
        'e': {
            'itemSkillLevel': (I, 10),
            'augmentSkillLevel1': (I, 6),
            'augmentSkillLevel2': (I, 6),
            'offensivePhysicalMin': (F, 80.0), 'offensivePhysicalMax': (F, 110.0),
            'offensivePierceMin': (F, 45.0),
            'offensivePierceRatioModifier': (I, 60),
            'offensivePhysicalModifier': (I, 50),
            'offensiveSlowBleedingMin': (F, 130.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowPoisonMin': (F, 55.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowTotalSpeedMin': (F, 15.0),
            'offensiveSlowTotalSpeedDurationMin': (F, 3.0),
            'characterAttackSpeedModifier': (F, 16.0),
            'characterTotalSpeedModifier': (I, 14),
            'characterRunSpeedModifier': (F, 11.0),
            'characterDodgePercent': (F, 11.0),
            'characterDeflectProjectile': (F, 12.0),
            'characterOffensiveAbilityModifier': (F, 6.0),
            'characterDefensiveAbilityModifier': (F, 6.0),
            'characterLifeModifier': (F, 10.0),
            'characterStrengthModifier': (F, 8.0), 'characterDexterityModifier': (F, 10.0),
            'defensiveReflect': (F, 55.0),
            'defensiveProtectionModifier': (F, 12.0),
            'defensivePierce': (F, 30.0),
            'characterEnergyAbsorptionPercent': (F, 22.0),
            'racialBonusPercentDamage': (F, 55.0),
        },
        'l': {
            'itemSkillLevel': (I, 14),
            'augmentSkillLevel1': (I, 8),
            'augmentSkillLevel2': (I, 7),
            'offensivePhysicalMin': (F, 120.0), 'offensivePhysicalMax': (F, 160.0),
            'offensivePierceMin': (F, 65.0),
            'offensivePierceRatioModifier': (I, 80),
            'offensivePhysicalModifier': (I, 75),
            'offensiveSlowBleedingMin': (F, 190.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowPoisonMin': (F, 80.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowTotalSpeedMin': (F, 20.0),
            'offensiveSlowTotalSpeedDurationMin': (F, 4.0),
            'characterAttackSpeedModifier': (F, 20.0),
            'characterTotalSpeedModifier': (I, 18),
            'characterRunSpeedModifier': (F, 14.0),
            'characterDodgePercent': (F, 14.0),
            'characterDeflectProjectile': (F, 16.0),
            'characterOffensiveAbilityModifier': (F, 8.0),
            'characterDefensiveAbilityModifier': (F, 8.0),
            'characterLifeModifier': (F, 15.0),
            'characterStrengthModifier': (F, 12.0), 'characterDexterityModifier': (F, 14.0),
            'defensiveReflect': (F, 75.0),
            'defensiveProtectionModifier': (F, 16.0),
            'defensivePierce': (F, 40.0),
            'characterEnergyAbsorptionPercent': (F, 30.0),
            'racialBonusPercentDamage': (F, 70.0),
        },
    }

    total = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'toxeus_soul' not in nl or 'equipmentring' not in nl:
            continue
        if 'sp_toxeus' in nl:
            continue  # skip our new SP soul
        for diff, stats in tiers.items():
            if f'_soul_{diff}.dbr' in nl:
                _set_soul_fields(db, name, stats)
                total += 1
                break

    print(f"  Main Toxeus soul overhauled ({total} records — Tier 3 rogue/warrior)")
    return total


def _create_leinth_soul(db):
    """Leinth the Blood Witch — blood/life/bleed caster boss.

    Blood Boil AoE (life leech), ranged bleed projectiles, summon minions,
    geyser poison, heatseeker pets.  Olympian race.  Poison weakness.
    Level 47-50 / 62-65 / 74-76.
    """
    # Wire to all 3 Leinth variants
    MONSTERS = [
        r'records\drxcreatures\bloodwitch\q_leinth_47.dbr',
        r'records\drxcreatures\bloodwitch\q_leinth_49.dbr',
        r'records\drxcreatures\bloodwitch\q_leinth_50.dbr',
    ]
    TAG = 'tagSVCSoulLeinth'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 47, 'stats': {
            # Proc: Blood Boil on hit (her SIGNATURE attack)
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            # Augments: Dark Covenant + Plague (summoner/caster)
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 2),
            # Life damage + bleed (blood witch theme)
            'offensiveLifeMin': (F, 30.0), 'offensiveLifeMax': (F, 50.0),
            'offensiveLifeModifier': (I, 20),
            'offensiveSlowBleedingMin': (F, 55.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 25),
            'offensiveLifeLeechMin': (F, 25.0),
            # % Stats (caster)
            'characterLifeModifier': (F, 8.0), 'characterManaModifier': (F, 8.0),
            'characterIntelligenceModifier': (F, 5.0),
            'characterSpellCastSpeedModifier': (I, 12),
            'characterManaRegenModifier': (I, 15),
            'defensiveLife': (F, 15.0),
            'defensiveBleeding': (F, 15.0),
            'defensivePoison': (F, -8.0),  # her weakness carried over
        }},
        {'diff': 'e', 'itemLevel': 62, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 5),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 3),
            'offensiveLifeMin': (F, 55.0), 'offensiveLifeMax': (F, 85.0),
            'offensiveLifeModifier': (I, 35),
            'offensiveSlowBleedingMin': (F, 95.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 40),
            'offensiveLifeLeechMin': (F, 40.0),
            'characterLifeModifier': (F, 12.0), 'characterManaModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterSpellCastSpeedModifier': (I, 20),
            'characterManaRegenModifier': (I, 22),
            'defensiveLife': (F, 22.0),
            'defensiveBleeding': (F, 20.0),
            'defensivePoison': (F, -8.0),
        }},
        {'diff': 'l', 'itemLevel': 74, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 7),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 4),
            'offensiveLifeMin': (F, 85.0), 'offensiveLifeMax': (F, 130.0),
            'offensiveLifeModifier': (I, 55),
            'offensiveSlowBleedingMin': (F, 145.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 60),
            'offensiveLifeLeechMin': (F, 60.0),
            'characterLifeModifier': (F, 18.0), 'characterManaModifier': (F, 16.0),
            'characterIntelligenceModifier': (F, 12.0),
            'characterSpellCastSpeedModifier': (I, 28),
            'characterManaRegenModifier': (I, 30),
            'defensiveLife': (F, 30.0),
            'defensiveBleeding': (F, 28.0),
            'defensivePoison': (F, -8.0),
        }},
    ]

    paths = _create_soul(db, 'leinth', TAG, tiers)
    # Wire to all 3 Leinth variants
    for m in MONSTERS:
        if db.has_record(m):
            db.set_field(m, 'lootFinger2Item1', paths, DATA_TYPE_STRING)
            db.set_field(m, 'chanceToEquipFinger2', 66.0, DATA_TYPE_FLOAT)
            db.set_field(m, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
            db._modified.add(m)
    print(f"  Leinth soul created (blood witch — life/bleed, 66% drop, 3 variants)")
    return paths


def _create_murder_bunny_soul(db):
    """Murder Bunny — Tier 2: endgame uber boss.

    275K HP ambush boss.  Egg bomb spawns + larvae, sandblast pierce+slow,
    massive physical damage (+375 at L), fire retaliation, dodge behavior.
    Level 66/79/99.
    """
    MONSTER = r'records\drxcreatures\crowheroes\murderbunny.dbr'
    TAG = 'tagSVCSoulMurderBunny'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 66, 'stats': {
            # Proc: Ground Smash on attack (physical devastation)
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillLevel': (I, 5),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            # Augments: Onslaught + Lethal Strike (raw killing power)
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE),
            'augmentSkillLevel2': (I, 3),
            # Massive physical + pierce (sandblast + melee theme)
            'offensivePhysicalMin': (F, 80.0), 'offensivePhysicalMax': (F, 130.0),
            'offensivePierceMin': (F, 40.0), 'offensivePierceMax': (F, 65.0),
            'offensivePhysicalModifier': (I, 45),
            'offensivePierceRatioModifier': (I, 18),
            'offensiveSlowBleedingMin': (F, 50.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            # Fire retaliation (his fire retaliation passive)
            'retaliationFireMin': (F, 30.0), 'retaliationFireMax': (F, 50.0),
            # Speed + dodge (ambush hunter)
            'characterAttackSpeedModifier': (I, 14),
            'characterRunSpeedModifier': (F, 10.0),
            'characterDodgePercent': (F, 8.0),
            # % Stats
            'characterLifeModifier': (F, 12.0), 'characterManaModifier': (F, 6.0),
            'characterStrengthModifier': (F, 6.0), 'characterDexterityModifier': (F, 8.0),
            'characterOffensiveAbilityModifier': (F, 6.0),
            'defensivePierce': (F, 25.0),
        }},
        {'diff': 'e', 'itemLevel': 79, 'stats': {
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE),
            'augmentSkillLevel2': (I, 4),
            'offensivePhysicalMin': (F, 130.0), 'offensivePhysicalMax': (F, 200.0),
            'offensivePierceMin': (F, 65.0), 'offensivePierceMax': (F, 100.0),
            'offensivePhysicalModifier': (I, 70),
            'offensivePierceRatioModifier': (I, 25),
            'offensiveSlowBleedingMin': (F, 85.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'retaliationFireMin': (F, 50.0), 'retaliationFireMax': (F, 80.0),
            'characterAttackSpeedModifier': (I, 18),
            'characterRunSpeedModifier': (F, 14.0),
            'characterDodgePercent': (F, 12.0),
            'characterLifeModifier': (F, 18.0), 'characterManaModifier': (F, 10.0),
            'characterStrengthModifier': (F, 10.0), 'characterDexterityModifier': (F, 12.0),
            'characterOffensiveAbilityModifier': (F, 8.0),
            'defensivePierce': (F, 35.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 6),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE),
            'augmentSkillLevel2': (I, 5),
            # Devastating physical + pierce
            'offensivePhysicalMin': (F, 190.0), 'offensivePhysicalMax': (F, 280.0),
            'offensivePierceMin': (F, 95.0), 'offensivePierceMax': (F, 145.0),
            'offensivePhysicalModifier': (I, 100),
            'offensivePierceRatioModifier': (I, 32),
            'offensiveSlowBleedingMin': (F, 130.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'retaliationFireMin': (F, 75.0), 'retaliationFireMax': (F, 120.0),
            # Ambush predator
            'characterAttackSpeedModifier': (I, 22),
            'characterRunSpeedModifier': (F, 18.0),
            'characterDodgePercent': (F, 16.0),
            'characterLifeModifier': (F, 25.0), 'characterManaModifier': (F, 14.0),
            'characterStrengthModifier': (F, 14.0), 'characterDexterityModifier': (F, 16.0),
            'characterOffensiveAbilityModifier': (F, 10.0),
            'defensivePierce': (F, 45.0),
        }},
    ]

    paths = _create_soul(db, 'murderbunny', TAG, tiers, MONSTER, 66.0)
    print(f"  Murder Bunny soul created (Tier 2 — physical devastation, 66% drop)")
    return paths


def _create_sp_hades_soul(db):
    """SP Hades — Tier 2: shadow god, stronger than main Hades soul.

    Uses Form 1 mesh/skills.  Sickle Sweep (massive phys + life damage),
    Shadow Bolt, Shadow Star.  Custom enrage regen passive.  Transforms
    on death to Form 2.  Level 57/71/80.
    """
    MONSTER = r'records\drxcreatures\bloodwitch\boss_hades_54.dbr'
    TAG = 'tagSVCSoulSPHades'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 57, 'stats': {
            # Proc: Blood Boil on attack (death god — life drain AoE)
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            # Augments: Death Chill Aura + Ternion Attack (Spirit mastery)
            'augmentSkillName1': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_TERNION),
            'augmentSkillLevel2': (I, 3),
            # Life + physical (sickle sweep profile)
            'offensiveLifeMin': (F, 50.0), 'offensiveLifeMax': (F, 80.0),
            'offensivePhysicalMin': (F, 40.0), 'offensivePhysicalMax': (F, 65.0),
            'offensiveLifeModifier': (I, 30),
            'offensivePercentCurrentLifeMin': (F, 5.0),
            'offensiveLifeLeechMin': (F, 30.0),
            # Resistance reduction (shadow bolt slow)
            'offensiveTotalResistanceReductionAbsoluteMin': (F, 12.0),
            'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, 3.0),
            # Dark god % stats
            'characterLifeModifier': (F, 10.0), 'characterManaModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 6.0),
            'characterSpellCastSpeedModifier': (I, 22),
            'characterDefensiveAbilityModifier': (F, 6.0),
            'defensiveLife': (F, 20.0),
            'defensiveFire': (F, 12.0), 'defensiveLightning': (F, 12.0),
            'defensiveProtectionModifier': (F, 8.0),
        }},
        {'diff': 'e', 'itemLevel': 71, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_TERNION),
            'augmentSkillLevel2': (I, 4),
            'offensiveLifeMin': (F, 85.0), 'offensiveLifeMax': (F, 130.0),
            'offensivePhysicalMin': (F, 65.0), 'offensivePhysicalMax': (F, 100.0),
            'offensiveLifeModifier': (I, 50),
            'offensivePercentCurrentLifeMin': (F, 8.0),
            'offensiveLifeLeechMin': (F, 50.0),
            'offensiveTotalResistanceReductionAbsoluteMin': (F, 20.0),
            'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, 3.0),
            'characterLifeModifier': (F, 16.0), 'characterManaModifier': (F, 18.0),
            'characterIntelligenceModifier': (F, 10.0),
            'characterSpellCastSpeedModifier': (I, 35),
            'characterDefensiveAbilityModifier': (F, 8.0),
            'defensiveLife': (F, 30.0),
            'defensiveFire': (F, 18.0), 'defensiveLightning': (F, 18.0),
            'defensiveProtectionModifier': (F, 14.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _SK_TERNION),
            'augmentSkillLevel2': (I, 5),
            # Massive life + physical (god of death)
            'offensiveLifeMin': (F, 130.0), 'offensiveLifeMax': (F, 195.0),
            'offensivePhysicalMin': (F, 100.0), 'offensivePhysicalMax': (F, 150.0),
            'offensiveLifeModifier': (I, 75),
            'offensivePercentCurrentLifeMin': (F, 12.0),
            'offensiveLifeLeechMin': (F, 75.0),
            # Shadow resistance shred
            'offensiveTotalResistanceReductionAbsoluteMin': (F, 30.0),
            'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, 3.0),
            # Dark overlord % stats
            'characterLifeModifier': (F, 22.0), 'characterManaModifier': (F, 25.0),
            'characterIntelligenceModifier': (F, 14.0),
            'characterSpellCastSpeedModifier': (I, 48),
            'characterDefensiveAbilityModifier': (F, 12.0),
            'defensiveLife': (F, 42.0),
            'defensiveFire': (F, 25.0), 'defensiveLightning': (F, 25.0),
            'defensiveProtectionModifier': (F, 20.0),
        }},
    ]

    paths = _create_soul(db, 'sp_hades', TAG, tiers, MONSTER, 66.0)
    print(f"  SP Hades soul created (Tier 2 — shadow/life, 66% drop)")
    return paths


def _create_dagon_soul(db):
    """Dagon — deep sea lord, ichthian boss.

    Super Bite (462-2214 poison DoT!), Tidal Wave, Mudstorm, Shadow Star,
    Poison Cloud on death.  100% poison immune.  Level 50/65/80.
    """
    MONSTER = r'records\test\boss_dagon_66.dbr'
    TAG = 'tagSVCSoulDagon'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 50, 'stats': {
            # Proc: Venom Spray on attack (ichthian poison theme)
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            # Augments: Envenom Weapon + Plague
            'augmentSkillName1': (S, _SK_ENVENOM),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 2),
            # Massive poison (Super Bite theme)
            'offensiveSlowPoisonMin': (F, 100.0), 'offensiveSlowPoisonMax': (F, 160.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveSlowPoisonModifier': (I, 25),
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 35.0),
            'offensiveColdMin': (F, 10.0), 'offensiveColdMax': (F, 20.0),
            # % Stats
            'characterLifeModifier': (F, 8.0), 'characterManaModifier': (F, 6.0),
            'characterStrengthModifier': (F, 4.0), 'characterDexterityModifier': (F, 4.0),
            'characterAttackSpeedModifier': (I, 8),
            'defensivePoison': (F, 30.0),
            'defensiveCold': (F, 15.0),
        }},
        {'diff': 'e', 'itemLevel': 65, 'stats': {
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ENVENOM),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 3),
            'offensiveSlowPoisonMin': (F, 180.0), 'offensiveSlowPoisonMax': (F, 280.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveSlowPoisonModifier': (I, 40),
            'offensivePhysicalMin': (F, 35.0), 'offensivePhysicalMax': (F, 55.0),
            'offensiveColdMin': (F, 18.0), 'offensiveColdMax': (F, 30.0),
            'characterLifeModifier': (F, 12.0), 'characterManaModifier': (F, 10.0),
            'characterStrengthModifier': (F, 6.0), 'characterDexterityModifier': (F, 5.0),
            'characterAttackSpeedModifier': (I, 12),
            'defensivePoison': (F, 42.0),
            'defensiveCold': (F, 22.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ENVENOM),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 4),
            # Devastating poison (Super Bite = 2214 poison at max)
            'offensiveSlowPoisonMin': (F, 280.0), 'offensiveSlowPoisonMax': (F, 420.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowPoisonModifier': (I, 60),
            'offensivePhysicalMin': (F, 55.0), 'offensivePhysicalMax': (F, 80.0),
            'offensiveColdMin': (F, 28.0), 'offensiveColdMax': (F, 42.0),
            'characterLifeModifier': (F, 18.0), 'characterManaModifier': (F, 14.0),
            'characterStrengthModifier': (F, 8.0), 'characterDexterityModifier': (F, 7.0),
            'characterAttackSpeedModifier': (I, 15),
            'defensivePoison': (F, 55.0),
            'defensiveCold': (F, 30.0),
        }},
    ]

    paths = _create_soul(db, 'dagon', TAG, tiers, MONSTER, 66.0)
    print(f"  Dagon soul created (deep sea poison lord, 66% drop)")
    return paths


def _create_dev_skeleton_souls(db):
    """Create souls for 15 developer-named Secret Passage skeletons.

    Each soul is themed to match the skeleton's creature mesh and skills.
    Quest class, Level 40/56/71.
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # (record_path, soul_base_name, tag, theme_proc, theme_augment1, theme_augment2,
    #  element_stats for L tier — N/E scaled at 0.6x/0.8x)
    DEV_SKELETONS = [
        # z_arthur — Satyr, spawns z_toxeus on death. Basic melee.
        (r'records\xpack\creatures\monster\zzdev\z_arthur.dbr', 'z_arthur',
         'xtagDevName01', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 55.0, 'offensivePhysicalMax': 80.0,
          'characterStrengthModifier': 8.0, 'characterLifeModifier': 10.0, 'characterOffensiveAbilityModifier': 5.0}),
        # z_ben — Anteok with club, barb flurry, groundbreaker, mass heal.
        (r'records\xpack\creatures\monster\zzdev\z_ben.dbr', 'z_ben',
         'xtagDevName02', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 65.0, 'offensivePhysicalMax': 95.0,
          'characterStrengthModifier': 10.0, 'characterLifeModifier': 12.0, 'characterLifeRegen': 5.0}),
        # z_chooch — Skeletal Typhon. Bone shards, bone spire, bone trap, spirit breath.
        (r'records\xpack\creatures\monster\zzdev\z_chooch.dbr', 'z_chooch',
         'xtagDevName14', _SS_GROUND_SMASH, _SK_DEATH_CHILL, _SK_DARK_COVENANT,
         {'offensivePhysicalMin': 50.0, 'offensivePhysicalMax': 75.0,
          'offensiveLifeMin': 30.0, 'offensiveLifeMax': 50.0,
          'characterLifeModifier': 10.0, 'characterIntelligenceModifier': 7.0, 'defensiveLife': 20.0}),
        # z_cory — Siege Walker. Turret attack, fire spit.
        (r'records\xpack\creatures\monster\zzdev\z_cory.dbr', 'z_cory',
         'xtagDevName12', r'records\skills\soulskills\firefragmentnova.dbr',
         r'records\skills\earth\drxfireenchantment.dbr', r'records\skills\earth\drxringofflame.dbr',
         {'offensiveFireMin': 45.0, 'offensiveFireMax': 70.0,
          'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0,
          'characterLifeModifier': 14.0, 'characterStrengthModifier': 7.0, 'defensiveFire': 25.0}),
        # z_dave — Satyr with Heart of Oak. Nature/physical.
        (r'records\xpack\creatures\monster\zzdev\z_dave.dbr', 'z_dave',
         'xtagDevName03', _SS_GROUND_SMASH, r'records\skills\nature\drxheartofoak.dbr',
         _SK_PLAGUE,
         {'offensivePhysicalMin': 50.0, 'offensivePhysicalMax': 72.0,
          'characterLifeModifier': 10.0, 'characterStrengthModifier': 7.0, 'characterLifeRegen': 4.0}),
        # z_david — Skeleton. Study Prey, Ensnare + Barbed Netting. Rogue theme.
        (r'records\xpack\creatures\monster\zzdev\z_david.dbr', 'z_david',
         'xtagDevName15', _SS_FLASH_POWDER, _SK_LETHAL_STRIKE, _SK_ENVENOM,
         {'offensivePierceMin': 40.0, 'offensivePierceMax': 60.0,
          'offensivePhysicalMin': 30.0, 'characterDexterityModifier': 8.0,
          'characterLifeModifier': 8.0, 'characterAttackSpeedModifier': 12.0}),
        # z_frazier — Satyr, basic.
        (r'records\xpack\creatures\monster\zzdev\z_frazier.dbr', 'z_frazier',
         'xtagDevName04', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 48.0, 'offensivePhysicalMax': 70.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'characterOffensiveAbilityModifier': 4.0}),
        # z_josh — Satyr, basic.
        (r'records\xpack\creatures\monster\zzdev\z_josh.dbr', 'z_josh',
         'xtagDevName05', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_DUAL_WEAPON,
         {'offensivePhysicalMin': 48.0, 'offensivePhysicalMax': 70.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'characterDexterityModifier': 6.0}),
        # z_morgan — HYDRA. Fire/cold/poison breath. Most complex dev skeleton.
        (r'records\xpack\creatures\monster\zzdev\z_morgan.dbr', 'z_morgan',
         'xtagDevName10', r'records\skills\soulskills\firefragmentnova.dbr',
         _SK_COLD_AURA, _SK_PLAGUE,
         {'offensiveFireMin': 35.0, 'offensiveFireMax': 55.0,
          'offensiveColdMin': 30.0, 'offensiveColdMax': 48.0,
          'offensiveSlowPoisonMin': 60.0, 'offensiveSlowPoisonDurationMin': 3.0,
          'characterLifeModifier': 14.0, 'characterIntelligenceModifier': 8.0,
          'defensiveFire': 20.0, 'defensiveCold': 20.0, 'defensivePoison': 20.0}),
        # z_nate — Satyr, basic.
        (r'records\xpack\creatures\monster\zzdev\z_nate.dbr', 'z_nate',
         'xtagDevName06', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 48.0, 'offensivePhysicalMax': 70.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'characterDefensiveAbilityModifier': 4.0}),
        # z_parnell — Odontotyrannus. Sonic wave, frenzy buff.
        (r'records\xpack\creatures\monster\zzdev\z_parnell.dbr', 'z_parnell',
         'xtagDevName11', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 60.0, 'offensivePhysicalMax': 90.0,
          'offensiveStunMin': 1.0, 'offensiveStunMax': 2.0, 'offensiveStunChance': 15.0,
          'characterStrengthModifier': 8.0, 'characterLifeModifier': 12.0}),
        # z_scott — Satyr.
        (r'records\xpack\creatures\monster\zzdev\z_scott.dbr', 'z_scott',
         'xtagDevName07', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 48.0, 'offensivePhysicalMax': 70.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'characterRunSpeedModifier': 8.0}),
        # z_shawn — Satyr, lower HP (3000).
        (r'records\xpack\creatures\monster\zzdev\z_shawn.dbr', 'z_shawn',
         'xtagDevName08', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_LETHAL_STRIKE,
         {'offensivePhysicalMin': 42.0, 'offensivePhysicalMax': 62.0,
          'characterDexterityModifier': 8.0, 'characterLifeModifier': 7.0, 'characterAttackSpeedModifier': 10.0}),
        # z_tom — Satyr.
        (r'records\xpack\creatures\monster\zzdev\z_tom.dbr', 'z_tom',
         'xtagDevName09', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 48.0, 'offensivePhysicalMax': 70.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'characterOffensiveAbilityModifier': 4.0}),
        # z_~v~ — Nightmare. Dream/psionic. Psionic Beam, Hypnotic Gaze, Dream Surge.
        (r'records\xpack\creatures\monster\zzdev\z_~v~.dbr', 'z_tildavtilde',
         'xtagDevName13', _SS_RING_LIGHTNING, _SK_PHANTOM_STRIKE, _SK_DISTORTION_WAVE,
         {'offensiveLightningMin': 40.0, 'offensiveLightningMax': 65.0,
          'offensiveLifeMin': 25.0, 'offensiveLifeMax': 40.0,
          'characterIntelligenceModifier': 10.0, 'characterManaModifier': 10.0, 'characterLifeModifier': 10.0,
          'characterSpellCastSpeedModifier': 15.0, 'defensiveLife': 18.0}),
    ]

    total = 0
    for record, base_name, tag, proc, aug1, aug2, l_stats in DEV_SKELETONS:
        if not db.has_record(record):
            continue

        # Build per-tier stats from L stats with 0.6x/0.8x scaling
        def _scale(stats_dict, factor):
            scaled = {}
            for k, v in stats_dict.items():
                if isinstance(v, float):
                    scaled[k] = round(v * factor, 1)
                elif isinstance(v, int):
                    scaled[k] = max(0, int(v * factor)) if v >= 0 else int(v * factor)
            return scaled

        n_stats = _scale(l_stats, 0.6)
        e_stats = _scale(l_stats, 0.8)

        def _typed(stats_dict):
            typed = {}
            for k, v in stats_dict.items():
                if isinstance(v, float):
                    typed[k] = (F, v)
                else:
                    typed[k] = (I, v)
            return typed

        common_skills = {
            'itemSkillName': (S, proc), 'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, aug1), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, aug2), 'augmentSkillLevel2': (I, 2),
        }
        n_skills = dict(common_skills)
        n_skills['itemSkillLevel'] = (I, 2)
        n_skills['augmentSkillLevel1'] = (I, 1)
        n_skills['augmentSkillLevel2'] = (I, 1)
        e_skills = dict(common_skills)
        e_skills['itemSkillLevel'] = (I, 2)

        tiers = [
            {'diff': 'n', 'itemLevel': 40, 'stats': {**n_skills, **_typed(n_stats)}},
            {'diff': 'e', 'itemLevel': 56, 'stats': {**e_skills, **_typed(e_stats)}},
            {'diff': 'l', 'itemLevel': 71, 'stats': {**common_skills, **_typed(l_stats)}},
        ]

        _create_soul(db, base_name, tag, tiers, record, 66.0)
        total += 1

    print(f"  Developer skeleton souls created: {total} (Secret Passage, 66% drop each)")
    return total


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

    pharaoh_ok = _create_pharaoh_guard_pet_skill(db)
    total += 1
    _update_pharaoh_guard_drop_rate(db)
    _fix_low_boss_soul_drop_rates(db)
    _wire_missing_boss_souls(db)

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

    tags['tagSVCSummonPharaohGuard'] = "Summon Pharaoh's Honor Guard"
    tags['tagSVCSummonPharaohGuardDESC'] = (
        'Awaken the ancient stone guardian, eternally bound to protect '
        "the pharaoh's tomb. The construct rises with unyielding resolve, "
        'crushing enemies with devastating physical force while shrugging '
        'off blows that would fell lesser beings.'
    )

    # Soul name tags
    tags['tagSVCSoulSPToxeus'] = 'Soul of Toxeus the Murderer (SP)'
    tags['tagSVCSoulLeinth'] = 'Soul of Leinth the Blood Witch'
    tags['tagSVCSoulMurderBunny'] = 'Soul of the Murder Bunny'
    tags['tagSVCSoulSPHades'] = 'Soul of Hades (SP)'
    tags['tagSVCSoulDagon'] = 'Soul of Dagon'

    overhaul_souls(db)
    _add_dagon_to_ichthian_pools(db)
    _add_coldworm_to_egypt_pools(db)
    _create_coldworm_soul(db)
    _create_sp_toxeus_soul(db)
    _overhaul_main_toxeus_soul(db)
    _create_leinth_soul(db)
    _create_murder_bunny_soul(db)
    _create_sp_hades_soul(db)
    _create_dagon_soul(db)
    _create_dev_skeleton_souls(db)
    cascade_merc_scrolls(db)
    add_blood_mistress_to_loot(db)

    return tags
