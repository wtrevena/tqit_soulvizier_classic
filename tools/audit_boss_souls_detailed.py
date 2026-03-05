"""
Comprehensive audit of all Boss-classified monsters in Soulvizier Classic.
Categorizes by spawn type, evaluates soul skills, and computes power scores.
"""
import sys
import os
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from pathlib import Path
from arz_patcher import ArzDatabase

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fv(fields, name):
    """Get field value (first element) or None."""
    if fields is None:
        return None
    if name in fields:
        v = fields[name].values
        return v[0] if len(v) == 1 else v
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            v = tf.values
            return v[0] if len(v) == 1 else v
    return None

def fvl(fields, name):
    """Get field value as list."""
    if fields is None:
        return []
    if name in fields:
        return fields[name].values
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values
    return []

def is_nonzero(v):
    """Check if a value is meaningfully nonzero."""
    if v is None:
        return False
    if isinstance(v, (int, float)):
        return abs(v) > 0.001
    if isinstance(v, str):
        return v != '' and v != '0'
    if isinstance(v, list):
        return any(is_nonzero(x) for x in v)
    return False

# ---------------------------------------------------------------------------
# Stat extraction
# ---------------------------------------------------------------------------

# Key fields on soul rings
OFFENSIVE_FIELDS = [
    'offensivePhysicalMin', 'offensivePhysicalMax', 'offensivePhysicalModifier',
    'offensiveFireMin', 'offensiveFireMax', 'offensiveFireModifier',
    'offensiveColdMin', 'offensiveColdMax', 'offensiveColdModifier',
    'offensiveLightningMin', 'offensiveLightningMax', 'offensiveLightningModifier',
    'offensivePoisonMin', 'offensivePoisonMax', 'offensivePoisonModifier',
    'offensiveLifeMin', 'offensiveLifeMax', 'offensiveLifeModifier',
    'offensivePierceMin', 'offensivePierceMax', 'offensivePierceModifier',
    'offensivePierceRatioMin', 'offensivePierceRatioMax', 'offensivePierceRatioModifier',
    'offensiveElementalModifier',
    'offensiveStunMin', 'offensiveStunMax', 'offensiveStunModifier',
    'offensiveSlowBleedingMin', 'offensiveSlowBleedingMax', 'offensiveSlowBleedingModifier',
    'offensiveSlowBleedingDurationMin', 'offensiveSlowBleedingDurationMax',
    'offensiveSlowFireMin', 'offensiveSlowFireMax', 'offensiveSlowFireModifier',
    'offensiveSlowFireDurationMin', 'offensiveSlowFireDurationMax',
    'offensiveSlowColdMin', 'offensiveSlowColdMax', 'offensiveSlowColdModifier',
    'offensiveSlowColdDurationMin', 'offensiveSlowColdDurationMax',
    'offensiveSlowPoisonMin', 'offensiveSlowPoisonMax', 'offensiveSlowPoisonModifier',
    'offensiveSlowPoisonDurationMin', 'offensiveSlowPoisonDurationMax',
    'offensiveSlowLightningMin', 'offensiveSlowLightningMax', 'offensiveSlowLightningModifier',
    'offensiveSlowLightningDurationMin', 'offensiveSlowLightningDurationMax',
    'offensiveSlowLifeLeachModifier', 'offensiveSlowManaLeachModifier',
    'offensiveSlowLifeLeachMin', 'offensiveSlowLifeLeachMax',
    'offensiveSlowManaLeachMin', 'offensiveSlowManaLeachMax',
    'offensiveSlowAttackSpeedMin', 'offensiveSlowAttackSpeedMax', 'offensiveSlowAttackSpeedModifier',
    'offensiveSlowRunSpeedMin', 'offensiveSlowRunSpeedMax', 'offensiveSlowRunSpeedModifier',
    'offensiveSlowDefensiveAbilityMin', 'offensiveSlowDefensiveAbilityMax',
    'offensiveSlowOffensiveAbilityMin', 'offensiveSlowOffensiveAbilityMax',
    'offensiveSlowDefensiveReductionMin', 'offensiveSlowDefensiveReductionMax',
    'offensiveSlowOffensiveReductionMin', 'offensiveSlowOffensiveReductionMax',
    'offensiveTotalDamageModifier',
]

DEFENSIVE_FIELDS = [
    'defensivePhysical', 'defensivePhysicalModifier',
    'defensivePierce', 'defensivePierceModifier',
    'defensiveFire', 'defensiveFireModifier',
    'defensiveCold', 'defensiveColdModifier',
    'defensiveLightning', 'defensiveLightningModifier',
    'defensivePoison', 'defensivePoisonModifier',
    'defensiveLife', 'defensiveLifeModifier',
    'defensiveElementalResistance',
    'defensiveProtection', 'defensiveProtectionModifier',
    'defensiveAbsorption', 'defensiveAbsorptionModifier',
    'defensiveStun', 'defensiveStunModifier',
    'defensiveReflect',
    'defensiveSlowLifeLeach', 'defensiveSlowLifeLeachModifier',
    'defensiveSlowManaLeach', 'defensiveSlowManaLeachModifier',
]

CHARACTER_FIELDS = [
    'characterLife', 'characterLifeModifier',
    'characterMana', 'characterManaModifier',
    'characterLifeRegen', 'characterLifeRegenModifier',
    'characterManaRegen', 'characterManaRegenModifier',
    'characterStrength', 'characterStrengthModifier',
    'characterIntelligence', 'characterIntelligenceModifier',
    'characterDexterity', 'characterDexterityModifier',
    'characterOffensiveAbility', 'characterOffensiveAbilityModifier',
    'characterDefensiveAbility', 'characterDefensiveAbilityModifier',
    'characterAttackSpeed', 'characterAttackSpeedModifier',
    'characterSpellCastSpeed', 'characterSpellCastSpeedModifier',
    'characterRunSpeed', 'characterRunSpeedModifier',
    'characterTotalSpeedModifier',
    'characterDodgePercent',
    'skillCooldownReduction', 'skillCooldownReductionModifier',
    'skillManaCostReduction', 'skillManaCostReductionModifier',
]

RETALIATION_FIELDS = [
    'retaliationPhysicalMin', 'retaliationPhysicalMax', 'retaliationPhysicalModifier',
    'retaliationFireMin', 'retaliationFireMax', 'retaliationFireModifier',
    'retaliationColdMin', 'retaliationColdMax', 'retaliationColdModifier',
    'retaliationLightningMin', 'retaliationLightningMax', 'retaliationLightningModifier',
    'retaliationPoisonMin', 'retaliationPoisonMax', 'retaliationPoisonModifier',
    'retaliationPierceMin', 'retaliationPierceMax', 'retaliationPierceModifier',
    'retaliationLifeMin', 'retaliationLifeMax', 'retaliationLifeModifier',
    'retaliationStunMin', 'retaliationStunMax', 'retaliationStunModifier',
]


def extract_nonzero_stats(fields, field_list):
    """Return dict of {field_name: value} for nonzero fields."""
    result = {}
    for fname in field_list:
        v = fv(fields, fname)
        if is_nonzero(v):
            result[fname] = v
    return result


def compute_ring_stat_score(fields):
    """Compute a numeric score from ring stats."""
    score = 0.0
    if fields is None:
        return 0.0

    # HP/Mana
    hp = fv(fields, 'characterLife') or 0
    if isinstance(hp, list): hp = max(hp)
    mana = fv(fields, 'characterMana') or 0
    if isinstance(mana, list): mana = max(mana)
    score += float(hp) * 0.3
    score += float(mana) * 0.15

    # Stats (STR/INT/DEX)
    for attr in ['characterStrength', 'characterIntelligence', 'characterDexterity']:
        v = fv(fields, attr) or 0
        if isinstance(v, list): v = max(v)
        score += float(v) * 2.0

    # OA/DA
    oa = fv(fields, 'characterOffensiveAbility') or 0
    if isinstance(oa, list): oa = max(oa)
    da = fv(fields, 'characterDefensiveAbility') or 0
    if isinstance(da, list): da = max(da)
    score += float(oa) * 0.5
    score += float(da) * 0.5

    # Resistances (flat %)
    for res in ['defensivePhysical', 'defensivePierce', 'defensiveFire', 'defensiveCold',
                'defensiveLightning', 'defensivePoison', 'defensiveLife',
                'defensiveElementalResistance']:
        v = fv(fields, res) or 0
        if isinstance(v, list): v = max(v)
        score += float(v) * 3.0

    # Absorption
    absorb = fv(fields, 'defensiveAbsorption') or 0
    if isinstance(absorb, list): absorb = max(absorb)
    score += float(absorb) * 2.0

    # Protection (armor)
    prot = fv(fields, 'defensiveProtection') or 0
    if isinstance(prot, list): prot = max(prot)
    score += float(prot) * 0.1

    # Damage modifiers (% increase)
    for mod in ['offensivePhysicalModifier', 'offensiveFireModifier', 'offensiveColdModifier',
                'offensiveLightningModifier', 'offensivePoisonModifier', 'offensiveLifeModifier',
                'offensiveElementalModifier', 'offensivePierceModifier', 'offensivePierceRatioModifier']:
        v = fv(fields, mod) or 0
        if isinstance(v, list): v = max(v)
        score += float(v) * 2.0

    # Flat damage
    for dmg_pair in [('offensivePhysicalMin', 'offensivePhysicalMax'),
                     ('offensiveFireMin', 'offensiveFireMax'),
                     ('offensiveColdMin', 'offensiveColdMax'),
                     ('offensiveLightningMin', 'offensiveLightningMax'),
                     ('offensivePierceMin', 'offensivePierceMax')]:
        lo = fv(fields, dmg_pair[0]) or 0
        hi = fv(fields, dmg_pair[1]) or 0
        if isinstance(lo, list): lo = max(lo)
        if isinstance(hi, list): hi = max(hi)
        score += (float(lo) + float(hi)) * 0.5

    # Life/mana leech modifiers
    for leech in ['offensiveSlowLifeLeachModifier', 'offensiveSlowManaLeachModifier']:
        v = fv(fields, leech) or 0
        if isinstance(v, list): v = max(v)
        score += float(v) * 1.5

    # Speed bonuses
    speed_mod = fv(fields, 'characterTotalSpeedModifier') or 0
    if isinstance(speed_mod, list): speed_mod = min(speed_mod)  # penalties are negative
    score += float(speed_mod) * 3.0  # negative = penalty

    # Reflect
    refl = fv(fields, 'defensiveReflect') or 0
    if isinstance(refl, list): refl = max(refl)
    score += float(refl) * 1.0

    # Stun resist
    stun_res = fv(fields, 'defensiveStun') or 0
    if isinstance(stun_res, list): stun_res = max(stun_res)
    score += float(stun_res) * 1.0

    # Regen
    hp_regen = fv(fields, 'characterLifeRegen') or 0
    if isinstance(hp_regen, list): hp_regen = max(hp_regen)
    score += float(hp_regen) * 3.0

    # Retaliation
    for rf in RETALIATION_FIELDS:
        v = fv(fields, rf) or 0
        if isinstance(v, list): v = max(v)
        score += abs(float(v)) * 0.3

    # Augment all level
    aug_all = fv(fields, 'augmentAllLevel') or 0
    if isinstance(aug_all, list): aug_all = max(aug_all)
    score += float(aug_all) * 20.0

    # Dodge
    dodge = fv(fields, 'characterDodgePercent') or 0
    if isinstance(dodge, list): dodge = max(dodge)
    score += float(dodge) * 3.0

    # CDR
    cdr = fv(fields, 'skillCooldownReduction') or 0
    if isinstance(cdr, list): cdr = max(cdr)
    score += float(cdr) * 2.0

    return score


# ---------------------------------------------------------------------------
# Skill analysis
# ---------------------------------------------------------------------------

SKILL_CLASS_SUMMON = {'Skill_SpawnPet'}
SKILL_CLASS_PROC_ATTACK = {
    'Skill_AttackProjectile', 'Skill_AttackProjectileBurst',
    'Skill_AttackProjectileAreaEffect', 'Skill_AttackProjectileFan',
    'Skill_AttackProjectileRing', 'Skill_AttackProjectileMultiHit',
    'Skill_AttackProjectileSpawnPet', 'Skill_AttackProjectileDebuf',
    'Skill_AttackRadius', 'Skill_AttackRadiusLightning',
    'Skill_AttackWave', 'Skill_AttackWeapon', 'Skill_AttackWeaponBlink',
    'Skill_AttackChain', 'Skill_AttackBuffRadius',
    'Skill_DropProjectileTelekinesis', 'Skill_OnHitAttackRadius',
    'Skill_DispelMagic', 'Skill_DefensiveWall',
    'Skill_WeaponPool_ChargedFinale', 'Skill_AttackInherent',
    'Skill_BuffAttackRadiusDuration',
}
SKILL_CLASS_BUFF = {
    'Skill_BuffOther', 'Skill_BuffRadius', 'Skill_BuffRadiusToggled',
    'Skill_BuffSelfDuration', 'Skill_BuffAttackRadiusToggled',
    'SkillBuff_Passive', 'SkillBuff_PassiveShield', 'Skill_GiveBonus',
    'Skill_Passive', 'SkillBuff_Debuf', 'SkillBuff_DebufFreeze',
    'SkillBuff_DebufTrap', 'Skill_PassiveOnHitBuffSelf',
    'Skill_PassiveOnLifeBuffSelf',
}

TRIGGER_TYPE_MAP = {
    'AttackEnemy': 'on attack',
    'OnEquip': 'on equip',
    'LowHealth': 'low health',
    'AttackedByEnemy': 'when hit',
}


def classify_skill(db, skill_path):
    """Classify a skill record and return info dict."""
    if not skill_path or not isinstance(skill_path, str) or not skill_path.strip():
        return None

    fields = db.get_fields(skill_path)
    if fields is None:
        # Try case-insensitive
        skill_lower = skill_path.lower()
        for rn in db.record_names():
            if rn.lower() == skill_lower:
                fields = db.get_fields(rn)
                break
    if fields is None:
        return {'type': 'unknown', 'path': skill_path, 'details': 'record not found'}

    cls = fv(fields, 'Class') or ''
    file_desc = fv(fields, 'FileDescription') or ''
    display_name = fv(fields, 'skillDisplayName') or ''
    max_level = fv(fields, 'skillMaxLevel') or 0
    cooldown = fv(fields, 'skillCooldownTime') or 0
    mana_cost = fv(fields, 'skillManaCost') or 0

    info = {
        'path': skill_path,
        'class': cls,
        'description': file_desc,
        'display_tag': display_name,
        'max_level': max_level,
        'cooldown': cooldown,
        'mana_cost': mana_cost,
    }

    if cls in SKILL_CLASS_SUMMON or cls == 'Skill_AttackProjectileSpawnPet':
        info['type'] = 'summon'
        spawn_objs = fvl(fields, 'spawnObjects')
        ttl = fvl(fields, 'spawnObjectsTimeToLive')
        pet_limit = fv(fields, 'petLimit') or 1
        pet_burst = fv(fields, 'petBurstSpawn') or 1
        info['spawn_objects'] = spawn_objs
        info['pet_limit'] = pet_limit
        info['pet_burst'] = pet_burst

        if not ttl or all(t == 0 for t in ttl):
            info['permanent'] = True
            info['details'] = f'PERMANENT summon, limit={pet_limit}, burst={pet_burst}'
        else:
            info['permanent'] = False
            avg_ttl = sum(float(t) for t in ttl) / len(ttl) if ttl else 0
            info['ttl'] = ttl
            info['details'] = f'Temporary summon ({avg_ttl:.0f}s avg), limit={pet_limit}'

    elif cls in SKILL_CLASS_PROC_ATTACK:
        info['type'] = 'proc'
        # Summarize damage types present
        dmg_types = []
        for dtype in ['Physical', 'Fire', 'Cold', 'Lightning', 'Poison', 'Life', 'Pierce']:
            lo_key = f'offensive{dtype}Min'
            hi_key = f'offensive{dtype}Max'
            lo = fv(fields, lo_key)
            hi = fv(fields, hi_key)
            if is_nonzero(lo) or is_nonzero(hi):
                dmg_types.append(dtype)
        # Check for projectiles
        num_proj = fv(fields, 'numProjectiles') or 0
        info['damage_types'] = dmg_types
        info['num_projectiles'] = num_proj
        info['details'] = f'{cls.replace("Skill_", "")}: {", ".join(dmg_types) if dmg_types else "special"}'
        if is_nonzero(num_proj):
            info['details'] += f' x{num_proj}'
        if is_nonzero(cooldown):
            cd = cooldown
            if isinstance(cd, list):
                cd = cd[0] if cd else 0
            info['details'] += f' (CD {cd}s)'

    elif cls in SKILL_CLASS_BUFF:
        info['type'] = 'buff'
        info['details'] = f'{cls.replace("Skill_", "").replace("SkillBuff_", "Buff_")}'
        # Check for notable buff effects
        buff_effects = []
        for attr in ['characterLife', 'characterMana', 'characterStrength',
                     'characterIntelligence', 'characterDexterity',
                     'defensivePhysical', 'defensiveFire', 'defensiveCold',
                     'defensiveLightning', 'defensivePoison',
                     'characterOffensiveAbility', 'characterDefensiveAbility',
                     'offensivePhysicalModifier', 'offensiveElementalModifier',
                     'characterTotalSpeedModifier',
                     'characterAttackSpeedModifier', 'characterRunSpeedModifier']:
            v = fv(fields, attr)
            if is_nonzero(v):
                short = attr.replace('character', '').replace('offensive', 'off_').replace('defensive', 'def_')
                buff_effects.append(short)
        if buff_effects:
            info['details'] += f': {", ".join(buff_effects[:5])}'

    else:
        info['type'] = 'other'
        info['details'] = f'Class={cls}'

    return info


def compute_skill_value(skill_info):
    """Compute numeric value for a skill."""
    if skill_info is None:
        return 0

    stype = skill_info.get('type', 'unknown')

    if stype == 'summon':
        if skill_info.get('permanent', False):
            pet_limit = skill_info.get('pet_limit', 1)
            if isinstance(pet_limit, list):
                pet_limit = max(pet_limit)
            return 500 + (int(pet_limit) - 1) * 100
        else:
            # Temporary: score based on duration
            ttl = skill_info.get('ttl', [30])
            avg_ttl = sum(float(t) for t in ttl) / len(ttl) if ttl else 30
            if avg_ttl > 60:
                return 200
            elif avg_ttl > 30:
                return 150
            else:
                return 100

    elif stype == 'proc':
        base = 75
        dmg_types = skill_info.get('damage_types', [])
        base += len(dmg_types) * 15
        num_proj = skill_info.get('num_projectiles', 0)
        if isinstance(num_proj, list):
            num_proj = max(num_proj) if num_proj else 0
        if is_nonzero(num_proj):
            base += min(int(num_proj), 10) * 5
        # AoE skills get bonus
        cls = skill_info.get('class', '')
        if 'Radius' in cls or 'Area' in cls or 'Ring' in cls or 'Wave' in cls or 'Fan' in cls:
            base += 25
        if 'Telekinesis' in cls:  # meteor-style
            base += 40
        return min(base, 200)

    elif stype == 'buff':
        cls = skill_info.get('class', '')
        if 'Toggled' in cls or 'Passive' in cls:
            return 80  # persistent buffs are strong
        elif 'Shield' in cls:
            return 70
        else:
            return 50

    return 20  # unknown/other


def get_autocast_info(db, controller_path):
    """Get trigger info from an autocast controller."""
    if not controller_path or not isinstance(controller_path, str):
        return None
    fields = db.get_fields(controller_path)
    if fields is None:
        controller_lower = controller_path.lower()
        for rn in db.record_names():
            if rn.lower() == controller_lower:
                fields = db.get_fields(rn)
                break
    if fields is None:
        return {'trigger': 'unknown', 'chance': 0}
    trigger = fv(fields, 'triggerType') or 'unknown'
    chance = fv(fields, 'chanceToRun') or 0
    target = fv(fields, 'targetType') or ''
    return {
        'trigger': TRIGGER_TYPE_MAP.get(trigger, trigger),
        'chance': chance,
        'target': target,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    db_path = Path('work/SoulvizierClassic/Database/SoulvizierClassic.arz')
    print(f'Loading database: {db_path}')
    db = ArzDatabase.from_arz(db_path)
    print()

    # -----------------------------------------------------------------------
    # Step 1: Find all Boss-classified monsters
    # -----------------------------------------------------------------------
    print('=' * 100)
    print('SCANNING FOR BOSS-CLASSIFIED MONSTERS...')
    print('=' * 100)

    all_records = db.record_names()
    creature_records = [r for r in all_records if 'creature' in r.lower() and r.endswith('.dbr')]

    boss_monsters = []
    for rec in creature_records:
        fields = db.get_fields(rec)
        if not fields:
            continue
        mc = fv(fields, 'monsterClassification')
        if mc != 'Boss':
            continue

        # Skip backups, copies, test, old versions
        rec_lower = rec.lower()
        if any(skip in rec_lower for skip in ['backup_', 'copy of ', 'old\\', 'test', 'hadesform', 'conflicted copy']):
            continue

        desc = fv(fields, 'description') or ''
        racial = fv(fields, 'characterRacialProfile') or ''
        lvl = fvl(fields, 'charLevel')

        # Get soul drop paths
        soul_paths = []
        for key, tf in fields.items():
            kn = key.split('###')[0]
            if kn.startswith('lootFinger') and 'Item' in kn and tf.values:
                for v in tf.values:
                    if v and 'soul' in str(v).lower() and str(v).endswith('.dbr'):
                        soul_paths.append(str(v))

        boss_monsters.append({
            'record': rec,
            'desc_tag': desc,
            'race': racial,
            'levels': lvl,
            'soul_paths': soul_paths,
        })

    # Deduplicate: group by desc_tag + soul set, keep highest level variant
    boss_groups = {}
    for bm in boss_monsters:
        soul_key = tuple(sorted(set(bm['soul_paths'])))
        group_key = (bm['desc_tag'], soul_key)
        if group_key not in boss_groups:
            boss_groups[group_key] = bm
        else:
            # Keep the one with highest max level
            existing_max = max(boss_groups[group_key]['levels']) if boss_groups[group_key]['levels'] else 0
            new_max = max(bm['levels']) if bm['levels'] else 0
            if new_max > existing_max:
                # Store all level variants
                boss_groups[group_key]['all_records'] = boss_groups[group_key].get('all_records', [boss_groups[group_key]['record']])
                boss_groups[group_key]['all_records'].append(bm['record'])
                boss_groups[group_key]['levels'] = bm['levels']
                boss_groups[group_key]['record'] = bm['record']
            else:
                boss_groups[group_key].setdefault('all_records', [boss_groups[group_key]['record']])
                boss_groups[group_key]['all_records'].append(bm['record'])

    # Collect level ranges across all variants
    for key, bm in boss_groups.items():
        all_levels = set()
        all_recs = bm.get('all_records', [bm['record']])
        for arec in all_recs:
            fields = db.get_fields(arec)
            if fields:
                lvls = fvl(fields, 'charLevel')
                all_levels.update(int(l) for l in lvls)
        bm['level_range'] = sorted(all_levels)
        bm['num_variants'] = len(all_recs)

    unique_bosses = list(boss_groups.values())
    print(f'\nFound {len(boss_monsters)} Boss records total, {len(unique_bosses)} unique bosses (after dedup)')

    # -----------------------------------------------------------------------
    # Step 2: Classify spawn type
    # -----------------------------------------------------------------------
    for bm in unique_bosses:
        rec = bm['record']
        if '\\um_' in rec:
            bm['spawn_type'] = 'RANDOM (UBER)'
        else:
            bm['spawn_type'] = 'FIXED LOCATION'

    fixed_bosses = [b for b in unique_bosses if b['spawn_type'] == 'FIXED LOCATION']
    uber_bosses = [b for b in unique_bosses if b['spawn_type'] == 'RANDOM (UBER)']
    print(f'  Fixed location bosses: {len(fixed_bosses)}')
    print(f'  Random spawn (uber) bosses: {len(uber_bosses)}')

    # -----------------------------------------------------------------------
    # Step 3: Analyze souls for each boss
    # -----------------------------------------------------------------------
    print('\nANALYZING SOUL DETAILS...')

    for bm in unique_bosses:
        soul_paths = list(set(bm['soul_paths']))  # deduplicate
        bm['souls'] = {}
        bm['total_score'] = 0

        if not soul_paths:
            bm['has_souls'] = False
            continue
        bm['has_souls'] = True

        # Determine tiers from path names
        for sp in soul_paths:
            tier = 'Unknown'
            sp_lower = sp.lower()
            if '_soul_n.' in sp_lower or sp_lower.endswith('_n.dbr'):
                tier = 'Normal'
            elif '_soul_e.' in sp_lower or sp_lower.endswith('_e.dbr'):
                tier = 'Epic'
            elif '_soul_l.' in sp_lower or sp_lower.endswith('_l.dbr'):
                tier = 'Legendary'

            fields = db.get_fields(sp)
            if fields is None:
                bm['souls'][tier] = {'path': sp, 'error': 'record not found'}
                continue

            soul_info = {
                'path': sp,
                'item_name_tag': fv(fields, 'itemNameTag') or '',
                'item_level': fv(fields, 'itemLevel') or 0,
                'item_classification': fv(fields, 'itemClassification') or '',
            }

            # --- Ring stats ---
            soul_info['offensive'] = extract_nonzero_stats(fields, OFFENSIVE_FIELDS)
            soul_info['defensive'] = extract_nonzero_stats(fields, DEFENSIVE_FIELDS)
            soul_info['character'] = extract_nonzero_stats(fields, CHARACTER_FIELDS)
            soul_info['retaliation'] = extract_nonzero_stats(fields, RETALIATION_FIELDS)
            soul_info['augment_all'] = fv(fields, 'augmentAllLevel') or 0
            soul_info['ring_stat_score'] = compute_ring_stat_score(fields)

            # --- Granted skill ---
            skill_path = fv(fields, 'itemSkillName')
            skill_level = fv(fields, 'itemSkillLevel') or 0
            if skill_path and isinstance(skill_path, str) and skill_path.strip():
                skill_info = classify_skill(db, skill_path)
                if skill_info:
                    skill_info['granted_level'] = skill_level
                soul_info['granted_skill'] = skill_info
                soul_info['skill_value'] = compute_skill_value(skill_info)
            else:
                soul_info['granted_skill'] = None
                soul_info['skill_value'] = 0

            # --- Autocast controller ---
            autocast_path = fv(fields, 'itemSkillAutoController')
            if autocast_path and isinstance(autocast_path, str) and autocast_path.strip():
                soul_info['autocast'] = get_autocast_info(db, autocast_path)
            else:
                soul_info['autocast'] = None

            # --- Augment skills ---
            augments = []
            for i in range(1, 5):
                aug_name = fv(fields, f'augmentSkillName{i}')
                aug_level = fv(fields, f'augmentSkillLevel{i}') or 0
                if aug_name and isinstance(aug_name, str) and aug_name.strip():
                    augments.append({'skill': aug_name, 'level': aug_level})
            soul_info['augment_skills'] = augments
            soul_info['augment_value'] = sum(20 * (a.get('level', 1) or 1) for a in augments)

            # --- Total score ---
            soul_info['total_score'] = (
                soul_info['ring_stat_score']
                + soul_info['skill_value']
                + soul_info['augment_value']
            )

            bm['souls'][tier] = soul_info

        # Boss total score = Legendary soul score (or best available)
        for tier_pref in ['Legendary', 'Epic', 'Normal']:
            if tier_pref in bm['souls'] and 'total_score' in bm['souls'][tier_pref]:
                bm['total_score'] = bm['souls'][tier_pref]['total_score']
                break

    # -----------------------------------------------------------------------
    # Step 4: Output
    # -----------------------------------------------------------------------

    def format_boss_entry(bm, index):
        lines = []
        lvl_str = ', '.join(str(l) for l in bm['level_range']) if bm['level_range'] else '?'
        lines.append(f'  {index}. [{bm["desc_tag"]}]  Race: {bm["race"]}  Levels: {lvl_str}  Variants: {bm["num_variants"]}')
        lines.append(f'     Record: {bm["record"]}')
        lines.append(f'     Total Power Score: {bm["total_score"]:.1f}')

        if not bm['has_souls']:
            lines.append('     *** NO SOUL DROPS ***')
            return '\n'.join(lines)

        for tier in ['Normal', 'Epic', 'Legendary']:
            soul = bm['souls'].get(tier)
            if not soul:
                continue
            if 'error' in soul:
                lines.append(f'     [{tier}] ERROR: {soul["error"]} ({soul["path"]})')
                continue

            lines.append(f'     --- {tier} Soul (iLvl {soul["item_level"]}) ---  Score: {soul["total_score"]:.1f} (ring={soul["ring_stat_score"]:.1f} + skill={soul["skill_value"]:.0f} + augment={soul["augment_value"]:.0f})')
            lines.append(f'         Path: {soul["path"]}')

            # Ring stats
            if soul['character']:
                char_strs = []
                for k, v in sorted(soul['character'].items()):
                    short = k.replace('character', '')
                    char_strs.append(f'{short}={v}')
                lines.append(f'         Character: {", ".join(char_strs)}')

            if soul['offensive']:
                off_strs = []
                for k, v in sorted(soul['offensive'].items()):
                    short = k.replace('offensive', '')
                    off_strs.append(f'{short}={v}')
                lines.append(f'         Offensive: {", ".join(off_strs)}')

            if soul['defensive']:
                def_strs = []
                for k, v in sorted(soul['defensive'].items()):
                    short = k.replace('defensive', '')
                    def_strs.append(f'{short}={v}')
                lines.append(f'         Defensive: {", ".join(def_strs)}')

            if soul['retaliation']:
                ret_strs = []
                for k, v in sorted(soul['retaliation'].items()):
                    short = k.replace('retaliation', '')
                    ret_strs.append(f'{short}={v}')
                lines.append(f'         Retaliation: {", ".join(ret_strs)}')

            if soul.get('augment_all', 0):
                lines.append(f'         +{soul["augment_all"]} to All Skills')

            # Granted skill
            gs = soul.get('granted_skill')
            if gs:
                skill_lvl = gs.get('granted_level', 0)
                lines.append(f'         Granted Skill (Lv {skill_lvl}): [{gs.get("type", "?")}] {gs.get("details", gs.get("path", ""))}')
                lines.append(f'           Skill Path: {gs.get("path", "")}')
                if gs.get('type') == 'summon' and gs.get('spawn_objects'):
                    objs = gs['spawn_objects']
                    lines.append(f'           Spawns: {objs[0] if objs else "?"}{"..." if len(objs) > 1 else ""} ({len(objs)} level variants)')

            # Autocast
            ac = soul.get('autocast')
            if ac:
                lines.append(f'         Autocast: {ac.get("trigger", "?")} ({ac.get("chance", 0)}% chance, target={ac.get("target", "?")})')

            # Augment skills
            for aug in soul.get('augment_skills', []):
                lines.append(f'         Augment: +{aug.get("level", 1)} to {aug["skill"]}')

        lines.append('')
        return '\n'.join(lines)

    # Sort by total score descending
    fixed_with_souls = [b for b in fixed_bosses if b['has_souls']]
    fixed_without_souls = [b for b in fixed_bosses if not b['has_souls']]
    uber_with_souls = [b for b in uber_bosses if b['has_souls']]
    uber_without_souls = [b for b in uber_bosses if not b['has_souls']]

    fixed_with_souls.sort(key=lambda b: b['total_score'], reverse=True)
    uber_with_souls.sort(key=lambda b: b['total_score'], reverse=True)

    print('\n')
    print('=' * 100)
    print('FIXED LOCATION BOSSES (Story/Area bosses with specific map spawns)')
    print('=' * 100)
    for i, bm in enumerate(fixed_with_souls, 1):
        print(format_boss_entry(bm, i))

    if fixed_without_souls:
        print('\n--- Fixed Location Bosses WITHOUT Souls ---')
        for i, bm in enumerate(fixed_without_souls, 1):
            lvl_str = ', '.join(str(l) for l in bm['level_range']) if bm['level_range'] else '?'
            print(f'  {i}. [{bm["desc_tag"]}]  Race: {bm["race"]}  Levels: {lvl_str}')
            print(f'     Record: {bm["record"]}')

    print('\n\n')
    print('=' * 100)
    print('RANDOM SPAWN (UBER) BOSSES (um_ prefix, spawn randomly in zones)')
    print('=' * 100)
    for i, bm in enumerate(uber_with_souls, 1):
        print(format_boss_entry(bm, i))

    if uber_without_souls:
        print('\n--- Uber Bosses WITHOUT Souls ---')
        for i, bm in enumerate(uber_without_souls, 1):
            lvl_str = ', '.join(str(l) for l in bm['level_range']) if bm['level_range'] else '?'
            print(f'  {i}. [{bm["desc_tag"]}]  Race: {bm["race"]}  Levels: {lvl_str}')
            print(f'     Record: {bm["record"]}')

    # -----------------------------------------------------------------------
    # Step 5: Summary statistics
    # -----------------------------------------------------------------------
    print('\n\n')
    print('=' * 100)
    print('SUMMARY STATISTICS')
    print('=' * 100)

    fixed_scores = [b['total_score'] for b in fixed_with_souls]
    uber_scores = [b['total_score'] for b in uber_with_souls]
    all_scores = fixed_scores + uber_scores

    def print_stats(label, scores):
        if not scores:
            print(f'  {label}: No data')
            return
        print(f'  {label}:')
        print(f'    Count: {len(scores)}')
        print(f'    Mean:  {statistics.mean(scores):.1f}')
        print(f'    Median: {statistics.median(scores):.1f}')
        print(f'    Min:   {min(scores):.1f}')
        print(f'    Max:   {max(scores):.1f}')
        if len(scores) > 1:
            print(f'    StdDev: {statistics.stdev(scores):.1f}')

    print_stats('Fixed Location Bosses', fixed_scores)
    print_stats('Random (Uber) Bosses', uber_scores)
    print_stats('All Bosses Combined', all_scores)

    # Weakest fixed bosses
    print(f'\n  --- WEAKEST FIXED LOCATION BOSS SOULS (bottom 10) ---')
    for bm in fixed_with_souls[-10:]:
        print(f'    Score {bm["total_score"]:6.1f}  [{bm["desc_tag"]}]  Race: {bm["race"]}  Record: {bm["record"]}')

    # Weakest uber bosses
    print(f'\n  --- WEAKEST RANDOM (UBER) BOSS SOULS (bottom 10) ---')
    for bm in uber_with_souls[-10:]:
        print(f'    Score {bm["total_score"]:6.1f}  [{bm["desc_tag"]}]  Race: {bm["race"]}  Record: {bm["record"]}')

    # Strongest bosses
    print(f'\n  --- STRONGEST BOSS SOULS (top 10) ---')
    all_with_souls = sorted(fixed_with_souls + uber_with_souls, key=lambda b: b['total_score'], reverse=True)
    for bm in all_with_souls[:10]:
        tag = 'FIXED' if bm['spawn_type'] == 'FIXED LOCATION' else 'UBER'
        print(f'    Score {bm["total_score"]:6.1f}  [{tag}] [{bm["desc_tag"]}]  Race: {bm["race"]}')

    # Skill type distribution
    print(f'\n  --- SKILL TYPE DISTRIBUTION (across all boss Legendary souls) ---')
    skill_types = {'summon_permanent': 0, 'summon_temporary': 0, 'proc': 0, 'buff': 0,
                   'other': 0, 'no_skill': 0}
    for bm in all_with_souls:
        for tier in ['Legendary', 'Epic', 'Normal']:
            soul = bm['souls'].get(tier)
            if not soul or 'error' in soul:
                continue
            gs = soul.get('granted_skill')
            if not gs:
                skill_types['no_skill'] += 1
            elif gs.get('type') == 'summon':
                if gs.get('permanent', False):
                    skill_types['summon_permanent'] += 1
                else:
                    skill_types['summon_temporary'] += 1
            elif gs.get('type') == 'proc':
                skill_types['proc'] += 1
            elif gs.get('type') == 'buff':
                skill_types['buff'] += 1
            else:
                skill_types['other'] += 1
            break  # Only count once per boss (best tier)

    total_with_skills = sum(skill_types.values())
    for stype, count in sorted(skill_types.items(), key=lambda x: -x[1]):
        pct = (count / total_with_skills * 100) if total_with_skills else 0
        bar = '#' * int(pct / 2)
        print(f'    {stype:25s}: {count:3d} ({pct:5.1f}%) {bar}')

    # Bosses without souls summary
    all_without = fixed_without_souls + uber_without_souls
    print(f'\n  --- BOSSES WITHOUT SOULS ---')
    print(f'    Total: {len(all_without)}')
    for bm in all_without:
        tag = 'FIXED' if bm['spawn_type'] == 'FIXED LOCATION' else 'UBER'
        print(f'      [{tag}] [{bm["desc_tag"]}] Race: {bm["race"]}  Record: {bm["record"]}')

    # Bosses with augment skills
    print(f'\n  --- BOSSES WITH AUGMENT SKILLS ---')
    aug_count = 0
    for bm in all_with_souls:
        for tier in ['Legendary', 'Epic', 'Normal']:
            soul = bm['souls'].get(tier)
            if soul and not isinstance(soul.get('augment_skills'), type(None)) and soul.get('augment_skills'):
                tag = 'FIXED' if bm['spawn_type'] == 'FIXED LOCATION' else 'UBER'
                for aug in soul['augment_skills']:
                    print(f'    [{tag}] [{bm["desc_tag"]}] {tier}: +{aug.get("level",1)} to {aug["skill"]}')
                aug_count += 1
                break
    print(f'    Total bosses with augments: {aug_count}')

    # Bosses with autocast
    print(f'\n  --- BOSSES WITH AUTOCAST CONTROLLERS ---')
    ac_count = 0
    for bm in all_with_souls:
        for tier in ['Legendary', 'Epic', 'Normal']:
            soul = bm['souls'].get(tier)
            if soul and soul.get('autocast'):
                tag = 'FIXED' if bm['spawn_type'] == 'FIXED LOCATION' else 'UBER'
                ac = soul['autocast']
                gs = soul.get('granted_skill', {})
                print(f'    [{tag}] [{bm["desc_tag"]}] {tier}: {ac.get("trigger","?")} {ac.get("chance",0)}% -> {gs.get("type","?")} ({gs.get("details","")})')
                ac_count += 1
                break
    print(f'    Total bosses with autocast: {ac_count}')

    print('\n\nAudit complete.')


if __name__ == '__main__':
    main()
