"""Comprehensive Soul Balance Audit for SoulvizierClassic.

Catalogs ALL soul rings, scores them, groups by monster tier,
identifies summon souls, flags outliers, and makes recommendations.

Usage: py tools/audit_soul_balance.py work/SoulvizierClassic/Database/SoulvizierClassic.arz
"""
import sys
import re
import statistics
from pathlib import Path
from collections import defaultdict, OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


# ---------------------------------------------------------------------------
# Field groups for scoring
# ---------------------------------------------------------------------------

# Flat offensive damage fields -> (field_min, field_max, weight_per_avg_point)
FLAT_DAMAGE_FIELDS = {
    'offensivePhysical': 1.0,
    'offensivePierce': 1.0,
    'offensiveFire': 1.0,
    'offensiveCold': 1.0,
    'offensiveLightning': 1.0,
    'offensiveLife': 1.2,  # vitality slightly more valuable
    'offensivePoison': 0.8,
    'offensiveElectricalBurn': 0.9,  # DoT
    'offensiveSlowFire': 0.7,  # burn DoT per sec
    'offensiveSlowCold': 0.7,
    'offensiveSlowLightning': 0.7,
    'offensiveSlowPoison': 0.7,
    'offensiveSlowPhysical': 0.7,  # bleed
    'offensiveSlowLife': 0.7,
    'offensiveSlowBleeding': 0.7,
}

# Percentage damage modifiers -> weight per 1%
PCT_DAMAGE_FIELDS = {
    'offensivePhysicalModifier': 0.5,
    'offensiveFireModifier': 0.5,
    'offensiveColdModifier': 0.5,
    'offensiveLightningModifier': 0.5,
    'offensiveLifeModifier': 0.5,
    'offensivePoisonModifier': 0.4,
    'offensiveSlowPoisonModifier': 0.4,
    'offensivePierceModifier': 0.5,
    'offensivePierceRatioModifier': 0.4,
    'offensiveTotalDamageModifier': 0.8,  # very strong
    'offensiveBaseDamageModifier': 0.6,
}

# Character stats -> weight per point
CHAR_STAT_FIELDS = {
    'characterStrength': 0.15,
    'characterIntelligence': 0.15,
    'characterDexterity': 0.15,
    'characterLife': 0.08,
    'characterMana': 0.05,
    'characterOffensiveAbility': 0.2,
    'characterDefensiveAbility': 0.2,
}

# Percentage character modifiers -> weight per 1%
CHAR_MOD_FIELDS = {
    'characterAttackSpeedModifier': 0.8,
    'characterSpellCastSpeedModifier': 0.7,
    'characterRunSpeedModifier': 0.5,
    'characterTotalSpeedModifier': 1.0,
    'characterLifeRegen': 0.3,
    'characterLifeRegenModifier': 0.3,
    'characterManaRegenModifier': 0.2,
    'characterLifeModifier': 0.6,
    'characterManaModifier': 0.3,
    'characterOffensiveAbilityModifier': 0.5,
    'characterDefensiveAbilityModifier': 0.5,
    'characterStrengthModifier': 0.4,
    'characterIntelligenceModifier': 0.4,
    'characterDexterityModifier': 0.4,
    'characterDodgePercent': 0.6,
    'characterDeflectProjectile': 0.6,
}

# Defensive/resistance fields -> weight per point of %resist
DEFENSE_FIELDS = {
    'defensiveFire': 0.4,
    'defensiveCold': 0.4,
    'defensiveLightning': 0.4,
    'defensivePoison': 0.4,
    'defensiveLife': 0.5,
    'defensivePhysical': 0.5,
    'defensivePierce': 0.5,
    'defensiveProtection': 0.03,  # flat armor, less weight
    'defensiveProtectionModifier': 0.3,
    'defensiveAbsorption': 0.5,
    'defensiveAbsorptionModifier': 0.4,
    'defensiveStun': 0.6,
    'defensiveFreeze': 0.5,
    'defensiveBleeding': 0.4,
    'defensiveElementalResistance': 0.6,
    'defensiveSlowLifeLeach': 0.4,
    'defensiveSlowManaLeach': 0.3,
    'defensiveDisruption': 0.3,
    'defensiveTotalSpeedResistance': 0.4,
}

# Retaliation fields (minor score contribution)
RETALIATION_FIELDS = {
    'retaliationPhysical': 0.05,
    'retaliationFire': 0.05,
    'retaliationCold': 0.05,
    'retaliationLightning': 0.05,
    'retaliationLife': 0.05,
    'retaliationPoison': 0.05,
    'retaliationPierce': 0.05,
}

# Leech fields
LEECH_FIELDS = {
    'offensiveSlowLifeLeachMin': 3.0,
    'offensiveSlowLifeLeachMax': 1.5,
    'offensiveSlowManaLeachMin': 2.0,
    'offensiveSlowManaLeachMax': 1.0,
    'offensiveLifeLeechMin': 4.0,
    'offensiveLifeLeechMax': 2.0,
    'offensiveManaLeechMin': 3.0,
    'offensiveManaLeechMax': 1.5,
}

# Special/utility fields
SPECIAL_FIELDS = {
    'offensiveStunMin': 5.0,
    'offensiveFreezeMin': 5.0,
    'offensivePercentCurrentLifeMin': 5.0,
    'offensiveManaBurnMin': 3.0,
    'offensiveFumbleMin': 3.0,
    'offensiveProjectileFumbleMin': 3.0,
    'skillCooldownReduction': 1.0,
    'skillCooldownReductionModifier': 0.5,
    'racialBonusPercentDamage': 0.3,
}


def get_field_val(fields, field_name):
    """Get numeric value of a field, or 0 if missing/zero."""
    if field_name in fields:
        v = fields[field_name].values[0] if fields[field_name].values else 0
        if isinstance(v, (int, float)):
            return float(v)
    # Also check ### suffixed keys
    for key, tf in fields.items():
        if key.split('###')[0] == field_name and tf.values:
            v = tf.values[0]
            if isinstance(v, (int, float)):
                return float(v)
    return 0.0


def get_field_str(fields, field_name):
    """Get string value of a field, or '' if missing."""
    if field_name in fields:
        v = fields[field_name].values[0] if fields[field_name].values else ''
        return str(v) if v else ''
    for key, tf in fields.items():
        if key.split('###')[0] == field_name and tf.values:
            v = tf.values[0]
            return str(v) if v else ''
    return ''


def get_all_field_strs(fields, field_name):
    """Get all string values for a multi-value field."""
    results = []
    for key, tf in fields.items():
        if key.split('###')[0] == field_name and tf.values:
            for v in tf.values:
                if isinstance(v, str) and v:
                    results.append(v)
    return results


def score_soul(fields):
    """Score a soul ring's power. Returns (offensive, defensive, utility, total, breakdown)."""
    offensive = 0.0
    defensive = 0.0
    utility = 0.0
    breakdown = {}

    # Flat damage
    for base, weight in FLAT_DAMAGE_FIELDS.items():
        mn = get_field_val(fields, base + 'Min')
        mx = get_field_val(fields, base + 'Max')
        avg = (mn + mx) / 2.0
        if avg > 0:
            pts = avg * weight
            offensive += pts
            breakdown[base] = f'{mn:.0f}-{mx:.0f} (avg={avg:.0f}, score={pts:.1f})'

    # Percentage damage modifiers
    for field, weight in PCT_DAMAGE_FIELDS.items():
        val = get_field_val(fields, field)
        if val != 0:
            pts = val * weight
            offensive += pts
            breakdown[field] = f'{val:+.0f}% (score={pts:.1f})'

    # Character stats (split between offensive and defensive)
    for field, weight in CHAR_STAT_FIELDS.items():
        val = get_field_val(fields, field)
        if val != 0:
            pts = val * weight
            if field in ('characterLife', 'characterDefensiveAbility'):
                defensive += pts
                breakdown[field] = f'{val:+.0f} (DEF score={pts:.1f})'
            elif field in ('characterMana',):
                utility += pts
                breakdown[field] = f'{val:+.0f} (UTIL score={pts:.1f})'
            else:
                offensive += pts
                breakdown[field] = f'{val:+.0f} (OFF score={pts:.1f})'

    # Character % modifiers -> utility
    for field, weight in CHAR_MOD_FIELDS.items():
        val = get_field_val(fields, field)
        if val != 0:
            pts = val * weight
            utility += pts
            breakdown[field] = f'{val:+.1f}% (UTIL score={pts:.1f})'

    # Defenses
    for field, weight in DEFENSE_FIELDS.items():
        val = get_field_val(fields, field)
        if val != 0:
            pts = val * weight
            defensive += pts
            breakdown[field] = f'{val:+.1f} (DEF score={pts:.1f})'

    # Retaliation
    for base, weight in RETALIATION_FIELDS.items():
        mn = get_field_val(fields, base + 'Min')
        mx = get_field_val(fields, base + 'Max')
        avg = (mn + mx) / 2.0
        if avg > 0:
            pts = avg * weight
            defensive += pts
            breakdown[base + ' retal'] = f'{mn:.0f}-{mx:.0f} (score={pts:.1f})'

    # Leech
    for field, weight in LEECH_FIELDS.items():
        val = get_field_val(fields, field)
        if val != 0:
            pts = val * weight
            utility += pts
            breakdown[field] = f'{val:.1f} (UTIL score={pts:.1f})'

    # Specials
    for field, weight in SPECIAL_FIELDS.items():
        val = get_field_val(fields, field)
        if val != 0:
            pts = val * weight
            utility += pts
            breakdown[field] = f'{val:.1f} (UTIL score={pts:.1f})'

    total = offensive + defensive + utility
    return offensive, defensive, utility, total, breakdown


def extract_soul_data(db, name, fields):
    """Extract all relevant info from a soul ring record."""
    data = {
        'path': name,
        'filename': name.replace('\\', '/').split('/')[-1].replace('.dbr', ''),
        'folder': '/'.join(name.replace('\\', '/').split('/')[:-1]),
        'itemLevel': int(get_field_val(fields, 'itemLevel')),
        'levelRequirement': int(get_field_val(fields, 'levelRequirement')),
        'itemClassification': get_field_str(fields, 'itemClassification'),
        'itemNameTag': get_field_str(fields, 'itemNameTag'),
        'fileDescription': get_field_str(fields, 'FileDescription'),
        'itemSkillName': get_field_str(fields, 'itemSkillName'),
        'itemSkillLevel': int(get_field_val(fields, 'itemSkillLevel')),
        'augmentSkillName1': get_field_str(fields, 'augmentSkillName1'),
        'augmentSkillLevel1': int(get_field_val(fields, 'augmentSkillLevel1')),
        'augmentSkillName2': get_field_str(fields, 'augmentSkillName2'),
        'augmentSkillLevel2': int(get_field_val(fields, 'augmentSkillLevel2')),
        'petBonusName': get_field_str(fields, 'petBonusName'),
        'racialBonusRace': get_field_str(fields, 'racialBonusRace'),
        'racialBonusPercentDamage': get_field_val(fields, 'racialBonusPercentDamage'),
        # Key stats
        'str': get_field_val(fields, 'characterStrength'),
        'int': get_field_val(fields, 'characterIntelligence'),
        'dex': get_field_val(fields, 'characterDexterity'),
        'hp': get_field_val(fields, 'characterLife'),
        'mp': get_field_val(fields, 'characterMana'),
        'oa': get_field_val(fields, 'characterOffensiveAbility'),
        'da': get_field_val(fields, 'characterDefensiveAbility'),
        'hp_regen': get_field_val(fields, 'characterLifeRegen'),
        'atk_spd': get_field_val(fields, 'characterAttackSpeedModifier'),
        'cast_spd': get_field_val(fields, 'characterSpellCastSpeedModifier'),
        'run_spd': get_field_val(fields, 'characterRunSpeedModifier'),
        'total_spd': get_field_val(fields, 'characterTotalSpeedModifier'),
        'hp_mod': get_field_val(fields, 'characterLifeModifier'),
        'mp_mod': get_field_val(fields, 'characterManaModifier'),
        'dodge': get_field_val(fields, 'characterDodgePercent'),
        'deflect': get_field_val(fields, 'characterDeflectProjectile'),
        # Damage
        'phys_min': get_field_val(fields, 'offensivePhysicalMin'),
        'phys_max': get_field_val(fields, 'offensivePhysicalMax'),
        'fire_min': get_field_val(fields, 'offensiveFireMin'),
        'fire_max': get_field_val(fields, 'offensiveFireMax'),
        'cold_min': get_field_val(fields, 'offensiveColdMin'),
        'cold_max': get_field_val(fields, 'offensiveColdMax'),
        'ltng_min': get_field_val(fields, 'offensiveLightningMin'),
        'ltng_max': get_field_val(fields, 'offensiveLightningMax'),
        'life_min': get_field_val(fields, 'offensiveLifeMin'),
        'life_max': get_field_val(fields, 'offensiveLifeMax'),
        'pierce_min': get_field_val(fields, 'offensivePierceMin'),
        'pierce_max': get_field_val(fields, 'offensivePierceMax'),
        'elec_burn_min': get_field_val(fields, 'offensiveElectricalBurnMin'),
        'elec_burn_max': get_field_val(fields, 'offensiveElectricalBurnMax'),
        # % modifiers
        'phys_mod': get_field_val(fields, 'offensivePhysicalModifier'),
        'fire_mod': get_field_val(fields, 'offensiveFireModifier'),
        'cold_mod': get_field_val(fields, 'offensiveColdModifier'),
        'ltng_mod': get_field_val(fields, 'offensiveLightningModifier'),
        'life_mod_off': get_field_val(fields, 'offensiveLifeModifier'),
        'poison_mod': get_field_val(fields, 'offensivePoisonModifier'),
        'total_dmg_mod': get_field_val(fields, 'offensiveTotalDamageModifier'),
        # Resistances
        'res_fire': get_field_val(fields, 'defensiveFire'),
        'res_cold': get_field_val(fields, 'defensiveCold'),
        'res_ltng': get_field_val(fields, 'defensiveLightning'),
        'res_poison': get_field_val(fields, 'defensivePoison'),
        'res_life': get_field_val(fields, 'defensiveLife'),
        'res_phys': get_field_val(fields, 'defensivePhysical'),
        'res_pierce': get_field_val(fields, 'defensivePierce'),
        'armor': get_field_val(fields, 'defensiveProtection'),
        'stun_res': get_field_val(fields, 'defensiveStun'),
        # Leech
        'life_leech_min': get_field_val(fields, 'offensiveSlowLifeLeachMin'),
        'life_leech_max': get_field_val(fields, 'offensiveSlowLifeLeachMax'),
        # Cooldown reduction
        'cdr': get_field_val(fields, 'skillCooldownReduction'),
    }
    return data


def get_soul_tier(path):
    """Determine soul tier from filename: _n=normal, _e=epic, _l=legendary."""
    pl = path.lower()
    if pl.endswith('_l.dbr'):
        return 'legendary'
    elif pl.endswith('_e.dbr'):
        return 'epic'
    elif pl.endswith('_n.dbr'):
        return 'normal'
    else:
        return 'other'


def get_soul_type_key(path):
    """Get soul type key (strip tier suffix for grouping)."""
    fn = path.lower().replace('\\', '/').split('/')[-1].replace('.dbr', '')
    fn = re.sub(r'_[nel]$', '', fn)
    return fn


def find_monster_for_soul(soul_path, monsters_by_soul_key, soul_key):
    """Try to find the monster record that drops this soul."""
    if soul_key in monsters_by_soul_key:
        return monsters_by_soul_key[soul_key]
    # Fuzzy match
    for mk, mlist in monsters_by_soul_key.items():
        if soul_key in mk or mk in soul_key:
            return mlist
    return []


def is_summon_skill(db, skill_path):
    """Check if a skill path is a summon/pet skill."""
    if not skill_path or not db.has_record(skill_path):
        return False, ''
    fields = db.get_fields(skill_path)
    if not fields:
        return False, ''

    # Check Class field
    cls = get_field_str(fields, 'Class')
    if 'pet' in cls.lower() or 'summon' in cls.lower():
        return True, cls

    # Check if skill name contains summon
    if 'summon' in skill_path.lower():
        return True, 'summon (path)'

    # Check for spawnObjects fields
    spawn = get_field_str(fields, 'spawnObjects')
    if spawn:
        return True, f'spawns: {spawn.split("/")[-1].split(chr(92))[-1]}'

    # Check petSkillName
    pet_skill = get_field_str(fields, 'petSkillName')
    if pet_skill:
        return True, f'petSkill: {pet_skill.split("/")[-1].split(chr(92))[-1]}'

    # Check if it references a pet record
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if 'pet' in rk.lower() or 'spawn' in rk.lower():
            if tf.values and tf.values[0]:
                v = tf.values[0]
                if isinstance(v, str) and v:
                    return True, f'{rk}: {v.split("/")[-1].split(chr(92))[-1]}'

    return False, ''


def main():
    if len(sys.argv) < 2:
        print("Usage: py tools/audit_soul_balance.py <database.arz>")
        sys.exit(1)

    db_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(db_path)

    # =====================================================================
    # PHASE 1: Catalog all soul rings
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 1: CATALOGING ALL SOUL RINGS")
    print("=" * 80)

    all_souls = []
    skip_patterns = ['soultemplate', 'anysoul', 'anysatyrherosoul', 'anymaenadherosoul',
                     'anycentaurherosoul', 'anycarrionbirdherosoul', 'anyharpyherosoul',
                     'anyscarabherosoul', 'copy of', 'conflicted copy',
                     'u_l_bandofsouls']

    for name in db.record_names():
        nl = name.lower()
        # Must be a soul ring
        if not (('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl):
            continue
        # Skip templates, generic, conflicted copies
        fn = nl.replace('\\', '/').split('/')[-1]
        if any(skip in fn for skip in skip_patterns):
            continue
        if 'conflicted copy' in nl:
            continue
        # Skip test souls in \testsouls\ folder
        if '\\testsouls\\' in nl or '/testsouls/' in nl:
            continue
        # Skip soulskills (these are skill records, not rings)
        if 'soulskills' in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        # Verify it's actually a ring (has ArmorJewelry_Ring class)
        cls = get_field_str(fields, 'Class')
        if 'ring' not in cls.lower() and 'jewelry' not in cls.lower():
            continue

        data = extract_soul_data(db, name, fields)
        data['tier'] = get_soul_tier(name)
        data['type_key'] = get_soul_type_key(name)

        # Score
        off, defe, util, total, bkdown = score_soul(fields)
        data['score_offensive'] = off
        data['score_defensive'] = defe
        data['score_utility'] = util
        data['score_total'] = total
        data['score_breakdown'] = bkdown

        # Check if itemSkillName is a summon
        if data['itemSkillName']:
            is_summon, summon_info = is_summon_skill(db, data['itemSkillName'])
            data['is_summon'] = is_summon
            data['summon_info'] = summon_info
        else:
            data['is_summon'] = False
            data['summon_info'] = ''

        all_souls.append(data)

    print(f"  Total soul rings cataloged: {len(all_souls)}")

    # Group by tier
    by_tier = defaultdict(list)
    for s in all_souls:
        by_tier[s['tier']].append(s)

    for tier in ['legendary', 'epic', 'normal', 'other']:
        print(f"  {tier}: {len(by_tier[tier])}")

    # =====================================================================
    # PHASE 2: Index monsters and their classifications
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 2: INDEXING MONSTERS WITH SOUL DROPS")
    print("=" * 80)

    # Build map: soul_type_key -> list of monster records
    monsters_by_soul = defaultdict(list)

    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue

        cls = get_field_str(fields, 'Class')
        tmpl = get_field_str(fields, 'templateName')
        if 'monster' not in cls.lower() and 'monster' not in tmpl.lower():
            continue

        classification = get_field_str(fields, 'monsterClassification')
        level = int(get_field_val(fields, 'charLevel'))
        desc = get_field_str(fields, 'FileDescription')

        # Check for soul reference in finger2 slot
        soul_ref = ''
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'lootFinger2Item1' and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and v and 'soul' in str(v).lower():
                        soul_ref = str(v)
                        break

        if soul_ref:
            sk = get_soul_type_key(soul_ref)
            monsters_by_soul[sk].append({
                'name': name,
                'classification': classification,
                'level': level,
                'desc': desc,
            })

    print(f"  Unique soul types referenced by monsters: {len(monsters_by_soul)}")

    # Attach monster classification to each soul
    for soul in all_souls:
        monsters = find_monster_for_soul(soul['path'], monsters_by_soul, soul['type_key'])
        if monsters:
            # Take the highest classification
            class_order = {'Boss': 5, 'Quest': 4, 'Hero': 3, 'Champion': 2, 'Common': 1, '': 0}
            best = max(monsters, key=lambda m: class_order.get(m['classification'], 0))
            soul['monster_classification'] = best['classification']
            soul['monster_level'] = best['level']
            soul['monster_name'] = best['name'].replace('\\', '/').split('/')[-1].replace('.dbr', '')
            soul['monster_count'] = len(monsters)
        else:
            # Try to infer from path
            path_parts = soul['path'].lower().replace('\\', '/').split('/')
            soul['monster_classification'] = '(unknown)'
            soul['monster_level'] = 0
            soul['monster_name'] = soul['type_key']
            soul['monster_count'] = 0

    # Count by classification
    class_counts = defaultdict(int)
    for s in all_souls:
        class_counts[s['monster_classification']] += 1

    print("  Souls by monster classification:")
    for cls, cnt in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f"    {cls or '(none)'}: {cnt}")

    # =====================================================================
    # PHASE 3: LEGENDARY TIER ANALYSIS (Focus of balance audit)
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 3: LEGENDARY TIER BALANCE ANALYSIS")
    print("=" * 80)

    legendary = [s for s in all_souls if s['tier'] == 'legendary']
    legendary.sort(key=lambda s: -s['score_total'])

    print(f"\n  Total legendary souls: {len(legendary)}")

    if legendary:
        scores = [s['score_total'] for s in legendary]
        print(f"  Score range: {min(scores):.1f} - {max(scores):.1f}")
        print(f"  Mean: {statistics.mean(scores):.1f}")
        print(f"  Median: {statistics.median(scores):.1f}")
        print(f"  Std dev: {statistics.stdev(scores):.1f}")

    # Group legendary by monster classification
    leg_by_class = defaultdict(list)
    for s in legendary:
        leg_by_class[s['monster_classification']].append(s)

    print("\n  === LEGENDARY SOUL SCORES BY MONSTER TIER ===")
    for cls in ['Boss', 'Quest', 'Hero', 'Champion', 'Common', '(unknown)']:
        souls_in_cls = leg_by_class.get(cls, [])
        if not souls_in_cls:
            continue
        cls_scores = [s['score_total'] for s in souls_in_cls]
        print(f"\n  --- {cls} ({len(souls_in_cls)} souls) ---")
        print(f"    Min:    {min(cls_scores):.1f}")
        print(f"    Max:    {max(cls_scores):.1f}")
        print(f"    Mean:   {statistics.mean(cls_scores):.1f}")
        if len(cls_scores) > 1:
            print(f"    Median: {statistics.median(cls_scores):.1f}")
            print(f"    StdDev: {statistics.stdev(cls_scores):.1f}")

    # =====================================================================
    # PHASE 4: SUMMON SKILL ANALYSIS
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 4: SUMMON SKILL ANALYSIS")
    print("=" * 80)

    # Find all souls with itemSkillName
    skill_souls = [s for s in all_souls if s['itemSkillName']]
    summon_souls = [s for s in all_souls if s['is_summon']]
    proc_souls = [s for s in skill_souls if not s['is_summon']]

    print(f"\n  Souls with itemSkillName (any): {len(skill_souls)}")
    print(f"  Souls with SUMMON skills: {len(summon_souls)}")
    print(f"  Souls with PROC skills (non-summon): {len(proc_souls)}")

    # Show all summon souls
    print(f"\n  === ALL SUMMON SOULS ===")
    seen_types = set()
    for s in sorted(summon_souls, key=lambda x: x['type_key']):
        if s['type_key'] in seen_types:
            continue
        seen_types.add(s['type_key'])
        skill_fn = s['itemSkillName'].replace('\\', '/').split('/')[-1]
        print(f"    {s['filename']:<45s} tier={s['tier']:<10s} lvl={s['itemLevel']:3d}  "
              f"score={s['score_total']:.1f}  skill={skill_fn}  "
              f"monster={s['monster_classification']}  info={s['summon_info']}")

    # =====================================================================
    # PHASE 5: RAKANIZEUS AND BONEASH SPOTLIGHT
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 5: RAKANIZEUS AND BONEASH SPOTLIGHT")
    print("=" * 80)

    our_souls = ['rakanizeus', 'boneash']
    all_leg_scores = [s['score_total'] for s in legendary]
    boss_leg = [s for s in legendary if s['monster_classification'] == 'Boss']
    boss_scores = [s['score_total'] for s in boss_leg] if boss_leg else [0]

    for target in our_souls:
        matches = [s for s in all_souls if target in s['type_key']]
        if not matches:
            print(f"\n  {target}: NOT FOUND")
            continue

        print(f"\n  === {target.upper()} ===")
        for s in sorted(matches, key=lambda x: x['tier']):
            print(f"\n    Tier: {s['tier']}  |  Path: {s['path']}")
            print(f"    Item Level: {s['itemLevel']}  |  Monster: {s['monster_classification']} (lvl {s['monster_level']})")
            print(f"    Score: OFF={s['score_offensive']:.1f}  DEF={s['score_defensive']:.1f}  "
                  f"UTIL={s['score_utility']:.1f}  TOTAL={s['score_total']:.1f}")

            # Compare to averages
            if s['tier'] == 'legendary' and all_leg_scores:
                pct = sum(1 for x in all_leg_scores if x < s['score_total']) / len(all_leg_scores) * 100
                boss_pct = sum(1 for x in boss_scores if x < s['score_total']) / len(boss_scores) * 100 if boss_scores else 0
                print(f"    Percentile: top {100-pct:.0f}% of ALL legendary | top {100-boss_pct:.0f}% of BOSS legendary")

            # Key stats
            stats_parts = []
            if s['str']: stats_parts.append(f"+{s['str']:.0f} Str")
            if s['int']: stats_parts.append(f"+{s['int']:.0f} Int")
            if s['dex']: stats_parts.append(f"+{s['dex']:.0f} Dex")
            if s['hp']: stats_parts.append(f"+{s['hp']:.0f} HP")
            if s['mp']: stats_parts.append(f"+{s['mp']:.0f} MP")
            if s['oa']: stats_parts.append(f"+{s['oa']:.0f} OA")
            if s['da']: stats_parts.append(f"+{s['da']:.0f} DA")
            if s['atk_spd']: stats_parts.append(f"+{s['atk_spd']:.0f}% atk spd")
            if s['cast_spd']: stats_parts.append(f"+{s['cast_spd']:.0f}% cast spd")
            if s['run_spd']: stats_parts.append(f"+{s['run_spd']:.0f}% run spd")
            if s['total_spd']: stats_parts.append(f"+{s['total_spd']:.0f}% total spd")
            if s['hp_mod']: stats_parts.append(f"{s['hp_mod']:+.0f}% max HP")
            if s['dodge']: stats_parts.append(f"+{s['dodge']:.0f}% dodge")
            print(f"    Stats: {', '.join(stats_parts) if stats_parts else '(none)'}")

            # Damage
            dmg_parts = []
            if s['phys_min'] or s['phys_max']: dmg_parts.append(f"{s['phys_min']:.0f}-{s['phys_max']:.0f} phys")
            if s['fire_min'] or s['fire_max']: dmg_parts.append(f"{s['fire_min']:.0f}-{s['fire_max']:.0f} fire")
            if s['cold_min'] or s['cold_max']: dmg_parts.append(f"{s['cold_min']:.0f}-{s['cold_max']:.0f} cold")
            if s['ltng_min'] or s['ltng_max']: dmg_parts.append(f"{s['ltng_min']:.0f}-{s['ltng_max']:.0f} ltng")
            if s['life_min'] or s['life_max']: dmg_parts.append(f"{s['life_min']:.0f}-{s['life_max']:.0f} life")
            if s['elec_burn_min'] or s['elec_burn_max']: dmg_parts.append(f"{s['elec_burn_min']:.0f}-{s['elec_burn_max']:.0f} elec burn")
            print(f"    Flat Damage: {', '.join(dmg_parts) if dmg_parts else '(none)'}")

            mod_parts = []
            if s['phys_mod']: mod_parts.append(f"+{s['phys_mod']:.0f}% phys")
            if s['fire_mod']: mod_parts.append(f"+{s['fire_mod']:.0f}% fire")
            if s['cold_mod']: mod_parts.append(f"+{s['cold_mod']:.0f}% cold")
            if s['ltng_mod']: mod_parts.append(f"+{s['ltng_mod']:.0f}% ltng")
            if s['life_mod_off']: mod_parts.append(f"+{s['life_mod_off']:.0f}% life")
            if s['total_dmg_mod']: mod_parts.append(f"+{s['total_dmg_mod']:.0f}% total dmg")
            print(f"    Damage Mods: {', '.join(mod_parts) if mod_parts else '(none)'}")

            res_parts = []
            if s['res_fire']: res_parts.append(f"+{s['res_fire']:.0f}% fire")
            if s['res_cold']: res_parts.append(f"+{s['res_cold']:.0f}% cold")
            if s['res_ltng']: res_parts.append(f"+{s['res_ltng']:.0f}% ltng")
            if s['res_poison']: res_parts.append(f"+{s['res_poison']:.0f}% poison")
            if s['res_life']: res_parts.append(f"+{s['res_life']:.0f}% life")
            if s['res_pierce']: res_parts.append(f"+{s['res_pierce']:.0f}% pierce")
            if s['stun_res']: res_parts.append(f"+{s['stun_res']:.0f}% stun")
            print(f"    Resistances: {', '.join(res_parts) if res_parts else '(none)'}")

            if s['itemSkillName']:
                sk_fn = s['itemSkillName'].replace('\\', '/').split('/')[-1]
                print(f"    Item Skill: {sk_fn} (lvl {s['itemSkillLevel']}) "
                      f"{'** SUMMON **' if s['is_summon'] else '(proc)'} {s['summon_info']}")
            if s['augmentSkillName1']:
                sk_fn = s['augmentSkillName1'].replace('\\', '/').split('/')[-1]
                print(f"    Augment Skill 1: {sk_fn} (lvl {s['augmentSkillLevel1']})")
            if s['augmentSkillName2']:
                sk_fn = s['augmentSkillName2'].replace('\\', '/').split('/')[-1]
                print(f"    Augment Skill 2: {sk_fn} (lvl {s['augmentSkillLevel2']})")
            if s['racialBonusRace']:
                print(f"    Racial Bonus: +{s['racialBonusPercentDamage']:.0f}% vs {s['racialBonusRace']}")

    # =====================================================================
    # PHASE 6: TOP 20 AND BOTTOM 20
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 6: TOP 20 AND BOTTOM 20 LEGENDARY SOULS")
    print("=" * 80)

    # Dedupe by type_key for legendary, take highest-scoring variant
    leg_by_type = {}
    for s in legendary:
        tk = s['type_key']
        if tk not in leg_by_type or s['score_total'] > leg_by_type[tk]['score_total']:
            leg_by_type[tk] = s

    leg_unique = sorted(leg_by_type.values(), key=lambda s: -s['score_total'])

    print(f"\n  Unique legendary soul types: {len(leg_unique)}")

    print(f"\n  === TOP 20 STRONGEST LEGENDARY SOULS ===")
    print(f"  {'Rank':<5} {'Soul Name':<40} {'Score':>7} {'OFF':>6} {'DEF':>6} {'UTIL':>6}  {'Mon.Tier':<10} {'LVL':>4}  Notes")
    print(f"  {'-'*4:<5} {'-'*39:<40} {'-'*6:>7} {'-'*5:>6} {'-'*5:>6} {'-'*5:>6}  {'-'*9:<10} {'-'*3:>4}  {'-'*30}")
    for i, s in enumerate(leg_unique[:20], 1):
        notes = []
        if s['is_summon']:
            notes.append('SUMMON')
        if s['itemSkillName'] and not s['is_summon']:
            notes.append('proc')
        if s['racialBonusRace']:
            notes.append(f'racial:{s["racialBonusRace"]}')
        if s['total_spd']:
            notes.append(f'+{s["total_spd"]:.0f}%spd')
        if s['hp_mod'] < 0:
            notes.append(f'{s["hp_mod"]:.0f}%HP')
        note_str = ', '.join(notes) if notes else ''
        print(f"  {i:<5} {s['filename']:<40} {s['score_total']:>7.1f} {s['score_offensive']:>6.1f} "
              f"{s['score_defensive']:>6.1f} {s['score_utility']:>6.1f}  {s['monster_classification']:<10} "
              f"{s['itemLevel']:>4}  {note_str}")

    print(f"\n  === BOTTOM 20 WEAKEST LEGENDARY SOULS ===")
    print(f"  {'Rank':<5} {'Soul Name':<40} {'Score':>7} {'OFF':>6} {'DEF':>6} {'UTIL':>6}  {'Mon.Tier':<10} {'LVL':>4}  Notes")
    print(f"  {'-'*4:<5} {'-'*39:<40} {'-'*6:>7} {'-'*5:>6} {'-'*5:>6} {'-'*5:>6}  {'-'*9:<10} {'-'*3:>4}  {'-'*30}")
    for i, s in enumerate(reversed(leg_unique[-20:]), 1):
        notes = []
        if s['is_summon']:
            notes.append('SUMMON')
        if s['itemSkillName'] and not s['is_summon']:
            notes.append('proc')
        if s['racialBonusRace']:
            notes.append(f'racial:{s["racialBonusRace"]}')
        note_str = ', '.join(notes) if notes else ''
        rank = len(leg_unique) - 20 + i
        print(f"  {rank:<5} {s['filename']:<40} {s['score_total']:>7.1f} {s['score_offensive']:>6.1f} "
              f"{s['score_defensive']:>6.1f} {s['score_utility']:>6.1f}  {s['monster_classification']:<10} "
              f"{s['itemLevel']:>4}  {note_str}")

    # =====================================================================
    # PHASE 7: OUTLIER DETECTION
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 7: OUTLIER DETECTION (LEGENDARY)")
    print("=" * 80)

    # For each monster classification, find outliers (>2 stddev from mean)
    for cls in ['Boss', 'Quest', 'Hero', 'Champion', 'Common']:
        cls_souls = [s for s in leg_unique if s['monster_classification'] == cls]
        if len(cls_souls) < 5:
            continue

        cls_scores = [s['score_total'] for s in cls_souls]
        mean = statistics.mean(cls_scores)
        std = statistics.stdev(cls_scores)

        overpowered = [s for s in cls_souls if s['score_total'] > mean + 2 * std]
        underpowered = [s for s in cls_souls if s['score_total'] < mean - 1.5 * std]

        if overpowered or underpowered:
            print(f"\n  --- {cls} tier (mean={mean:.1f}, std={std:.1f}) ---")
            if overpowered:
                print(f"    OVERPOWERED (>{mean + 2*std:.1f}):")
                for s in sorted(overpowered, key=lambda x: -x['score_total']):
                    notes = []
                    if s['is_summon']: notes.append('SUMMON')
                    if s['itemSkillName'] and not s['is_summon']: notes.append('proc')
                    n = f" [{', '.join(notes)}]" if notes else ''
                    print(f"      {s['filename']:<40s} score={s['score_total']:.1f}  "
                          f"(+{s['score_total'] - mean:.1f} from mean){n}")
            if underpowered:
                print(f"    UNDERPOWERED (<{mean - 1.5*std:.1f}):")
                for s in sorted(underpowered, key=lambda x: x['score_total']):
                    print(f"      {s['filename']:<40s} score={s['score_total']:.1f}  "
                          f"({s['score_total'] - mean:.1f} from mean)")

    # =====================================================================
    # PHASE 8: RECOMMENDATIONS
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 8: BALANCE RECOMMENDATIONS")
    print("=" * 80)

    # Calculate tier score ranges
    print("\n  === CURRENT TIER SCORE DISTRIBUTIONS (Legendary) ===\n")
    tier_stats = {}
    for cls in ['Boss', 'Quest', 'Hero', 'Champion', 'Common', '(unknown)']:
        cls_souls = [s for s in leg_unique if s['monster_classification'] == cls]
        if not cls_souls:
            continue
        cls_scores = [s['score_total'] for s in cls_souls]
        tier_stats[cls] = {
            'count': len(cls_souls),
            'min': min(cls_scores),
            'max': max(cls_scores),
            'mean': statistics.mean(cls_scores),
            'median': statistics.median(cls_scores),
            'p25': sorted(cls_scores)[len(cls_scores)//4] if len(cls_scores) >= 4 else min(cls_scores),
            'p75': sorted(cls_scores)[3*len(cls_scores)//4] if len(cls_scores) >= 4 else max(cls_scores),
        }
        t = tier_stats[cls]
        print(f"  {cls:<12s}  n={t['count']:3d}  "
              f"min={t['min']:6.1f}  p25={t['p25']:6.1f}  "
              f"median={t['median']:6.1f}  p75={t['p75']:6.1f}  "
              f"max={t['max']:6.1f}  mean={t['mean']:6.1f}")

    # Summon analysis
    print("\n  === SUMMON SOUL ANALYSIS ===\n")
    summon_leg = [s for s in leg_unique if s['is_summon']]
    non_summon_leg = [s for s in leg_unique if not s['is_summon']]

    if summon_leg:
        sum_scores = [s['score_total'] for s in summon_leg]
        non_scores = [s['score_total'] for s in non_summon_leg] if non_summon_leg else [0]
        print(f"  Summon souls (legendary): {len(summon_leg)}")
        print(f"    Score range: {min(sum_scores):.1f} - {max(sum_scores):.1f}  (mean: {statistics.mean(sum_scores):.1f})")
        print(f"  Non-summon souls (legendary): {len(non_summon_leg)}")
        print(f"    Score range: {min(non_scores):.1f} - {max(non_scores):.1f}  (mean: {statistics.mean(non_scores):.1f})")
        print(f"\n  NOTE: Summon souls are scored ONLY on their ring stats, not the pet's power.")
        print(f"  A summon soul with score 50 is actually MUCH stronger than a stat soul with score 50")
        print(f"  because the pet adds enormous power that is not captured in this score.")

    # Specific recommendations
    print("\n  === SPECIFIC RECOMMENDATIONS ===\n")

    print("  1. WHICH MONSTERS SHOULD GET SUMMON PETS:")
    print("     - Only the most iconic BOSS monsters should have summon souls")
    print("     - Current summon souls in the database:")
    for s in sorted(summon_leg, key=lambda x: -x['score_total']):
        print(f"       {s['filename']:<40s} {s['monster_classification']:<8s} score={s['score_total']:.1f}")

    print("\n  2. PROPOSED TIER FRAMEWORK (ring stat scores only):")
    print("     These are RING-ONLY scores. Summon pet value is additional.")
    if tier_stats:
        # Calculate proposed ranges based on current data
        all_medians = {cls: t['median'] for cls, t in tier_stats.items()}
        print(f"     Boss souls:      target 40-80  (summon souls should have LOWER ring stats to compensate)")
        print(f"     Quest souls:     target 30-60")
        print(f"     Hero souls:      target 15-45")
        print(f"     Champion souls:  target  8-25")
        print(f"     Common souls:    target  3-15")

    print("\n  3. SOULS CURRENTLY OVERPOWERED FOR THEIR TIER:")
    for cls in ['Hero', 'Champion', 'Common']:
        cls_souls = [s for s in leg_unique if s['monster_classification'] == cls]
        if len(cls_souls) < 3:
            continue
        cls_mean = statistics.mean([s['score_total'] for s in cls_souls])
        # Flag souls more than 2x the mean
        for s in sorted(cls_souls, key=lambda x: -x['score_total']):
            if s['score_total'] > cls_mean * 2 and s['score_total'] > 30:
                notes = []
                if s['is_summon']: notes.append('SUMMON')
                n = f" [{', '.join(notes)}]" if notes else ''
                print(f"     {s['filename']:<40s} {cls:<8s} score={s['score_total']:.1f} "
                      f"(mean for tier: {cls_mean:.1f}){n}")

    print("\n  4. SOULS CURRENTLY UNDERPOWERED FOR THEIR TIER:")
    for cls in ['Boss', 'Quest']:
        cls_souls = [s for s in leg_unique if s['monster_classification'] == cls]
        if len(cls_souls) < 3:
            continue
        cls_mean = statistics.mean([s['score_total'] for s in cls_souls])
        # Flag souls less than half the mean
        for s in sorted(cls_souls, key=lambda x: x['score_total']):
            if s['score_total'] < cls_mean * 0.4:
                print(f"     {s['filename']:<40s} {cls:<8s} score={s['score_total']:.1f} "
                      f"(mean for tier: {cls_mean:.1f})")

    print("\n  5. RAKANIZEUS & BONEASH ASSESSMENT:")
    for target in our_souls:
        leg_match = [s for s in legendary if target in s['type_key']]
        if leg_match:
            s = leg_match[0]
            boss_mean = statistics.mean(boss_scores) if boss_scores else 0
            all_mean = statistics.mean(all_leg_scores) if all_leg_scores else 0
            print(f"\n     {target.upper()}:")
            print(f"       Ring stat score: {s['score_total']:.1f}")
            print(f"       Boss mean: {boss_mean:.1f}  |  All-soul mean: {all_mean:.1f}")
            print(f"       Has summon pet: {'YES' if s['is_summon'] else 'NO'} + augment skills")
            if s['is_summon']:
                print(f"       VERDICT: Ring stats are {'ABOVE' if s['score_total'] > boss_mean else 'BELOW'} boss average,")
                print(f"       PLUS has a permanent summon pet with equipment and skills.")
                print(f"       This makes it significantly more powerful than typical boss souls.")
                if s['score_total'] > boss_mean:
                    print(f"       RECOMMENDATION: Reduce ring stats to compensate for pet power.")
                    print(f"         Suggested ring score target: {boss_mean * 0.6:.0f}-{boss_mean * 0.8:.0f}")

    # =====================================================================
    # PHASE 9: COMPLETE LEGENDARY CATALOG
    # =====================================================================
    print("\n" + "=" * 80)
    print("PHASE 9: COMPLETE LEGENDARY SOUL CATALOG (sorted by score)")
    print("=" * 80)

    print(f"\n  {'#':<4} {'Soul Name':<40} {'Score':>7} {'OFF':>6} {'DEF':>6} {'UTIL':>6}  "
          f"{'Mon.Tier':<10} {'LVL':>4}  {'Summon':>6}  {'Skill'}")
    print(f"  {'-'*3:<4} {'-'*39:<40} {'-'*6:>7} {'-'*5:>6} {'-'*5:>6} {'-'*5:>6}  "
          f"{'-'*9:<10} {'-'*3:>4}  {'-'*5:>6}  {'-'*30}")

    for i, s in enumerate(leg_unique, 1):
        sk = ''
        if s['itemSkillName']:
            sk = s['itemSkillName'].replace('\\', '/').split('/')[-1].replace('.dbr', '')[:30]
        summon_flag = 'YES' if s['is_summon'] else ''
        print(f"  {i:<4} {s['filename']:<40} {s['score_total']:>7.1f} {s['score_offensive']:>6.1f} "
              f"{s['score_defensive']:>6.1f} {s['score_utility']:>6.1f}  {s['monster_classification']:<10} "
              f"{s['itemLevel']:>4}  {summon_flag:>6}  {sk}")

    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
