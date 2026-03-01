"""Compare existing SV soul stats to our generated uber souls.

Focus on gameplay-relevant fields that make souls interesting:
- Granted skills (itemSkillName, skillName1)
- Skill augments (augmentSkillName1)
- Life/mana leech
- DoT (bleed, burn, frostburn, electrocute)
- Retaliation damage
- Movement speed, dodge, deflect
- OA/DA
- % current life damage
- % total damage modifier
- Pierce damage, pierce resistance
- CC (stun, freeze)
- Pet bonuses
- Racial bonuses

Skip test/junk records.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

GAMEPLAY_FIELDS = {
    'augmentSkillName1', 'augmentSkillLevel1',
    'augmentSkillName2', 'augmentSkillLevel2',
    'itemSkillName', 'itemSkillLevel', 'itemSkillAutoController',
    'skillName1', 'skillLevel1',
    'offensiveSlowLifeLeechMin', 'offensiveSlowLifeLeechMax',
    'offensiveSlowManaLeechMin', 'offensiveSlowManaLeechMax',
    'offensiveLifeLeechMin', 'offensiveLifeLeechMax',
    'offensiveManaLeechMin', 'offensiveManaLeechMax',
    'retaliationPhysicalMin', 'retaliationPhysicalMax',
    'retaliationFireMin', 'retaliationFireMax',
    'retaliationColdMin', 'retaliationColdMax',
    'retaliationLightningMin', 'retaliationLightningMax',
    'retaliationPoisonMin', 'retaliationPoisonMax',
    'retaliationLifeMin', 'retaliationLifeMax',
    'offensiveSlowPhysicalMin', 'offensiveSlowPhysicalMax',
    'offensiveSlowPhysicalDurationMin',
    'offensiveSlowFireMin', 'offensiveSlowFireMax',
    'offensiveSlowFireDurationMin',
    'offensiveSlowColdMin', 'offensiveSlowColdMax',
    'offensiveSlowColdDurationMin',
    'offensiveSlowLightningMin', 'offensiveSlowLightningMax',
    'offensiveSlowLightningDurationMin',
    'offensiveSlowBleedingMin', 'offensiveSlowBleedingMax',
    'offensiveSlowBleedingDurationMin',
    'offensiveTotalDamageModifier',
    'offensivePercentCurrentLifeMin', 'offensivePercentCurrentLifeMax',
    'offensiveBaseDamageModifier',
    'offensivePierceMin', 'offensivePierceMax', 'offensivePierceModifier',
    'offensivePierceRatioModifier',
    'offensiveStunMin', 'offensiveFreezeMin',
    'offensiveFumbleMin', 'offensiveProjectileFumbleMin',
    'offensiveManaBurnMin', 'offensiveManaBurnMax',
    'characterRunSpeedModifier', 'characterTotalSpeedModifier',
    'characterDodgePercent', 'characterDeflectProjectile',
    'characterOffensiveAbility', 'characterDefensiveAbility',
    'characterOffensiveAbilityModifier', 'characterDefensiveAbilityModifier',
    'characterLifeModifier', 'characterManaModifier',
    'characterStrengthModifier', 'characterIntelligenceModifier',
    'characterDexterityModifier',
    'defensivePierce', 'defensivePhysical',
    'defensiveStun', 'defensiveFreeze', 'defensivePetrify',
    'defensiveElementalResistance',
    'defensiveAbsorption', 'defensiveAbsorptionModifier',
    'defensiveTotalSpeedResistance',
    'defensiveSlowLifeLeach', 'defensiveSlowManaLeach',
    'defensiveProtectionModifier', 'defensiveBleeding',
    'defensiveDisruption',
    'petBonusName',
    'racialBonusRace', 'racialBonusPercentDamage',
    'racialBonusAbsoluteDamage', 'racialBonusPercentDefense',
    'skillCooldownReduction',
    'offensiveGlobalChance',
}


def extract_gameplay(db, record_path):
    """Extract only gameplay-relevant stats from a soul record."""
    if not db.has_record(record_path):
        return None
    fields = db.get_fields(record_path)
    if not fields:
        return None

    stats = {}
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk not in GAMEPLAY_FIELDS:
            continue
        if not tf.values or tf.values[0] is None:
            continue
        v = tf.values[0]
        if isinstance(v, (int, float)) and v == 0:
            continue
        if isinstance(v, str) and not v:
            continue
        stats[rk] = v
    return stats


def format_val(v):
    if isinstance(v, float):
        return f'{v:.1f}'
    if isinstance(v, str):
        return v.replace('\\', '/').split('/')[-1].replace('.dbr', '')
    return str(v)


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Categorize all soul records
    sv_souls = {}  # path -> stats
    uber_souls = {}

    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if '\\test\\' in nl or '/test/' in nl:
                continue
            stats = extract_gameplay(db, name)
            if stats:
                if 'svc_uber' in nl:
                    uber_souls[name] = stats
                else:
                    sv_souls[name] = stats

    # Group by soul type (strip _n/_e/_l)
    def type_key(path):
        fn = path.lower().replace('\\', '/').split('/')[-1].replace('.dbr', '')
        return re.sub(r'_[nel]$', '', fn)

    # Find unique interesting SV souls
    sv_by_type = defaultdict(list)
    for path, stats in sv_souls.items():
        tk = type_key(path)
        sv_by_type[tk].append((path, stats))

    uber_by_type = defaultdict(list)
    for path, stats in uber_souls.items():
        tk = type_key(path)
        uber_by_type[tk].append((path, stats))

    # Collect all fields used by uber souls
    uber_fields = set()
    for stats in uber_souls.values():
        uber_fields.update(stats.keys())

    # Find SV souls with abilities uber souls don't have
    print("=" * 80)
    print("FIELDS USED BY EXISTING SV SOULS BUT NOT OUR UBER SOULS")
    print("=" * 80)

    field_counts = defaultdict(int)
    field_examples = defaultdict(list)
    for tk, entries in sv_by_type.items():
        path, stats = entries[0]
        for k, v in stats.items():
            if k not in uber_fields:
                field_counts[k] += 1
                if len(field_examples[k]) < 3:
                    field_examples[k].append((tk, format_val(v)))

    for field in sorted(field_counts, key=field_counts.get, reverse=True):
        count = field_counts[field]
        examples = ', '.join(f'{name}={val}' for name, val in field_examples[field])
        print(f'  {field:<45s} {count:4d} souls | e.g. {examples}')

    # Show the most interesting SV souls (by number of unique gameplay fields)
    print("\n" + "=" * 80)
    print("TOP 50 MOST INTERESTING EXISTING SV SOULS")
    print("(by number of unique gameplay fields)")
    print("=" * 80)

    ranked = []
    seen = set()
    for tk, entries in sv_by_type.items():
        if tk in seen:
            continue
        seen.add(tk)
        path, stats = entries[0]
        unique_count = sum(1 for k in stats if k not in uber_fields)
        if unique_count > 0:
            # Get display name
            desc = ''
            fields = db.get_fields(path)
            if fields:
                for key, tf in fields.items():
                    if key.split('###')[0] == 'FileDescription' and tf.values:
                        desc = str(tf.values[0])
                        break
            ranked.append((tk, desc, stats, unique_count))

    ranked.sort(key=lambda x: -x[3])

    for tk, desc, stats, uniq in ranked[:50]:
        print(f'\n--- {desc or tk} ({uniq} unique fields) ---')
        for k in sorted(stats):
            marker = ' ***NEW***' if k not in uber_fields else ''
            print(f'    {k} = {format_val(stats[k])}{marker}')

    # Show what a "good" SV soul looks like at various levels
    print("\n" + "=" * 80)
    print("EXAMPLE SV SOULS WITH GRANTED SKILLS")
    print("=" * 80)

    skill_souls = []
    for tk, entries in sv_by_type.items():
        path, stats = entries[0]
        if 'itemSkillName' in stats or 'skillName1' in stats or 'augmentSkillName1' in stats:
            desc = ''
            level = 0
            fields = db.get_fields(path)
            if fields:
                for key, tf in fields.items():
                    rk = key.split('###')[0]
                    if rk == 'FileDescription' and tf.values:
                        desc = str(tf.values[0])
                    if rk == 'itemLevel' and tf.values and isinstance(tf.values[0], (int, float)):
                        level = int(tf.values[0])
            skill_souls.append((tk, desc, stats, level))

    skill_souls.sort(key=lambda x: x[3])

    for tk, desc, stats, lvl in skill_souls[:80]:
        skill = stats.get('itemSkillName', stats.get('skillName1', stats.get('augmentSkillName1', '?')))
        skill_fn = format_val(skill)
        print(f'  lvl {lvl:3d} | {desc or tk:<50s} | skill: {skill_fn}')
        for k in sorted(stats):
            if k not in ('itemSkillName', 'skillName1', 'augmentSkillName1'):
                print(f'          {k} = {format_val(stats[k])}')

    # Summary of what uber souls are missing
    print("\n" + "=" * 80)
    print("UBER SOUL ENHANCEMENT OPPORTUNITIES")
    print("=" * 80)
    print(f"\nUber souls use {len(uber_fields)} field types: {sorted(uber_fields)}")
    missing = sorted(field_counts, key=field_counts.get, reverse=True)
    print(f"\nSV souls use {len(missing)} additional field types our uber souls don't have.")
    print("\nTop candidates to add (by popularity):")
    for i, field in enumerate(missing[:20], 1):
        print(f'  {i:2d}. {field:<45s} ({field_counts[field]} SV souls use it)')


if __name__ == '__main__':
    main()
