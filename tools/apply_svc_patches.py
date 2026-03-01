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
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxstormsurge.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxlightningbolt_chainlightning.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 4),
        'itemSkillName': (DATA_TYPE_STRING, r'records\skills\item skills\test_summon.dbr'),
        'itemSkillLevel': (DATA_TYPE_INT, 1),
        'itemSkillAutoController': (DATA_TYPE_STRING, _AC_ON_EQUIP),
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


def _create_rakanizeus_pet_skill(db):
    """Repurpose the unused test_summon.dbr to summon Rakanizeus.

    Minimal change only: swap spawnObjects to Rakanizeus, leave all other
    fields at their original values.  Additional field changes (cooldown,
    mana, display name, icons) are added incrementally once we confirm
    this baseline is stable.
    """
    skill_path = r'records\skills\item skills\test_summon.dbr'
    rakan_monster = 'records/creature/monster/satyr/um_rakanizeus_17.dbr'

    if not db.has_record(skill_path):
        print("    WARN: test_summon.dbr not found, cannot create Rakanizeus summon")
        return False

    db.set_field(skill_path, 'spawnObjects', [rakan_monster], DATA_TYPE_STRING)
    db._modified.add(skill_path)
    print("    Repurposed test_summon.dbr -> Rakanizeus summon (minimal)")
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
    if not rakan_ok:
        print("    Falling back: Rakanizeus soul will use chimera summon")
        SOUL_OVERHAULS['rakanizeus_soul']['itemSkillName'] = (
            DATA_TYPE_STRING, SUMMON_CHIMERA_SKILL)
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

    overhaul_souls(db)
    cascade_merc_scrolls(db)
    add_blood_mistress_to_loot(db)

    return tags
