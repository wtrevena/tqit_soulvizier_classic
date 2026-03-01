"""Extract reference data for hand-crafting uber souls:

1. Full stat profiles of the best existing SV souls at each level tier
2. All augmentable player skills (drx* prefix skills referenced by augmentSkillName)
3. All grantable skills (referenced by itemSkillName)
4. All auto-cast controllers (referenced by itemSkillAutoController)
5. All pet bonus records
6. All racial profiles available

This gives us the complete palette for designing souls.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

SOUL_FIELDS = [
    'augmentSkillName1', 'augmentSkillLevel1',
    'augmentSkillName2', 'augmentSkillLevel2',
    'itemSkillName', 'itemSkillLevel', 'itemSkillAutoController',
    'skillName1', 'skillLevel1',
    'characterStrength', 'characterIntelligence', 'characterDexterity',
    'characterLife', 'characterMana',
    'characterLifeRegen', 'characterManaRegen',
    'characterLifeModifier', 'characterManaModifier',
    'characterManaRegenModifier',
    'characterStrengthModifier', 'characterIntelligenceModifier', 'characterDexterityModifier',
    'characterAttackSpeedModifier', 'characterSpellCastSpeedModifier',
    'characterRunSpeedModifier', 'characterTotalSpeedModifier',
    'characterDodgePercent', 'characterDeflectProjectile',
    'characterOffensiveAbility', 'characterDefensiveAbility',
    'characterOffensiveAbilityModifier', 'characterDefensiveAbilityModifier',
    'offensivePhysicalMin', 'offensivePhysicalMax', 'offensivePhysicalModifier',
    'offensiveFireMin', 'offensiveFireMax', 'offensiveFireModifier',
    'offensiveColdMin', 'offensiveColdMax', 'offensiveColdModifier',
    'offensiveLightningMin', 'offensiveLightningMax', 'offensiveLightningModifier',
    'offensiveSlowPoisonMin', 'offensiveSlowPoisonMax', 'offensiveSlowPoisonModifier',
    'offensiveSlowPoisonDurationMin',
    'offensiveLifeMin', 'offensiveLifeMax', 'offensiveLifeModifier',
    'offensivePierceMin', 'offensivePierceMax', 'offensivePierceModifier',
    'offensivePierceRatioModifier',
    'offensiveSlowPhysicalMin', 'offensiveSlowPhysicalMax', 'offensiveSlowPhysicalDurationMin',
    'offensiveSlowFireMin', 'offensiveSlowFireMax', 'offensiveSlowFireDurationMin',
    'offensiveSlowColdMin', 'offensiveSlowColdMax', 'offensiveSlowColdDurationMin',
    'offensiveSlowLightningMin', 'offensiveSlowLightningMax', 'offensiveSlowLightningDurationMin',
    'offensiveSlowBleedingMin', 'offensiveSlowBleedingMax', 'offensiveSlowBleedingDurationMin',
    'offensiveSlowBleedingModifier',
    'offensiveSlowLifeLeechMin', 'offensiveSlowLifeLeechMax',
    'offensiveSlowLifeLeachModifier',
    'offensiveLifeLeechMin', 'offensiveLifeLeechMax',
    'offensiveTotalDamageModifier', 'offensiveBaseDamageModifier',
    'offensivePercentCurrentLifeMin', 'offensivePercentCurrentLifeMax',
    'offensiveStunMin', 'offensiveFreezeMin',
    'offensiveFumbleMin', 'offensiveProjectileFumbleMin',
    'offensiveGlobalChance',
    'offensiveManaBurnMin', 'offensiveManaBurnMax',
    'defensiveFire', 'defensiveCold', 'defensiveLightning',
    'defensivePoison', 'defensiveLife',
    'defensivePhysical', 'defensivePierce',
    'defensiveProtection', 'defensiveProtectionModifier',
    'defensiveElementalResistance',
    'defensiveStun', 'defensiveFreeze', 'defensivePetrify',
    'defensiveBleeding', 'defensiveDisruption',
    'defensiveAbsorption', 'defensiveAbsorptionModifier',
    'defensiveTotalSpeedResistance',
    'defensiveSlowLifeLeach', 'defensiveSlowManaLeach',
    'retaliationPhysicalMin', 'retaliationPhysicalMax',
    'retaliationFireMin', 'retaliationFireMax',
    'retaliationColdMin', 'retaliationColdMax',
    'retaliationLightningMin', 'retaliationLightningMax',
    'retaliationPoisonMin', 'retaliationPoisonMax',
    'retaliationLifeMin', 'retaliationLifeMax',
    'petBonusName',
    'racialBonusRace', 'racialBonusPercentDamage',
    'racialBonusAbsoluteDamage', 'racialBonusPercentDefense',
    'skillCooldownReduction',
    'itemLevel', 'levelRequirement',
    'itemNameTag', 'FileDescription',
]


def fn(path):
    return path.replace('\\', '/').split('/')[-1].replace('.dbr', '')


def extract_soul(db, path):
    fields = db.get_fields(path)
    if not fields:
        return None
    stats = {}
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk in SOUL_FIELDS and tf.values and tf.values[0] is not None:
            v = tf.values[0]
            if isinstance(v, (int, float)) and v == 0:
                continue
            if isinstance(v, str) and not v:
                continue
            stats[rk] = v
    return stats


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # 1. Catalog all augmentable skills
    print("=" * 80)
    print("SECTION 1: ALL AUGMENT SKILLS USED BY EXISTING SOULS")
    print("=" * 80)
    augment_skills = defaultdict(int)
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if '\\test\\' in nl:
                continue
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if rk in ('augmentSkillName1', 'augmentSkillName2') and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            augment_skills[fn(v)] += 1

    for skill in sorted(augment_skills, key=augment_skills.get, reverse=True):
        print(f"  {skill:<55s} used {augment_skills[skill]:3d} times")

    # 2. Catalog all granted skills
    print("\n" + "=" * 80)
    print("SECTION 2: ALL GRANTED SKILLS (itemSkillName) USED BY EXISTING SOULS")
    print("=" * 80)
    granted_skills = defaultdict(int)
    granted_controllers = defaultdict(int)
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if '\\test\\' in nl:
                continue
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if rk == 'itemSkillName' and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            granted_skills[fn(v)] += 1
                if rk == 'itemSkillAutoController' and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            granted_controllers[fn(v)] += 1

    for skill in sorted(granted_skills, key=granted_skills.get, reverse=True):
        print(f"  {skill:<55s} used {granted_skills[skill]:3d} times")

    print("\n  --- Auto-cast controllers ---")
    for ctrl in sorted(granted_controllers, key=granted_controllers.get, reverse=True):
        print(f"  {ctrl:<55s} used {granted_controllers[ctrl]:3d} times")

    # 3. Catalog all racial profiles used
    print("\n" + "=" * 80)
    print("SECTION 3: RACIAL BONUS TARGETS")
    print("=" * 80)
    racial_targets = defaultdict(int)
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if '\\test\\' in nl:
                continue
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                if key.split('###')[0] == 'racialBonusRace' and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            racial_targets[v] += 1
    for race in sorted(racial_targets, key=racial_targets.get, reverse=True):
        print(f"  {race:<30s} {racial_targets[race]:3d} souls")

    # 4. Show 20 best souls at each level tier as reference
    print("\n" + "=" * 80)
    print("SECTION 4: BEST EXISTING SOULS BY LEVEL (reference for stat values)")
    print("=" * 80)

    all_sv = []
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if '\\test\\' in nl or 'svc_uber' in nl:
                continue
            if '_n.' not in nl and '_n.dbr' not in nl:
                continue
            stats = extract_soul(db, name)
            if not stats:
                continue
            level = stats.get('itemLevel', 0)
            if not isinstance(level, (int, float)) or level < 5:
                continue
            interesting = sum(1 for k in stats if k not in (
                'itemLevel', 'levelRequirement', 'itemNameTag', 'FileDescription',
                'characterStrength', 'characterIntelligence', 'characterDexterity',
                'characterLife', 'characterMana', 'characterLifeRegen',
                'offensivePhysicalMin', 'offensivePhysicalMax',
            ))
            all_sv.append((name, stats, int(level), interesting))

    all_sv.sort(key=lambda x: (-x[3], x[2]))

    tiers = [(5, 15), (16, 25), (26, 35), (36, 45), (46, 55), (56, 70)]
    for lo, hi in tiers:
        tier_souls = [s for s in all_sv if lo <= s[2] <= hi]
        tier_souls.sort(key=lambda x: -x[3])
        print(f"\n--- Level {lo}-{hi} ({len(tier_souls)} souls) ---")
        for name, stats, lvl, iq in tier_souls[:5]:
            desc = stats.get('FileDescription', fn(name))
            print(f"\n  {desc} (lvl {lvl}, {iq} interesting fields)")
            for k in sorted(stats):
                if k in ('itemNameTag',):
                    continue
                v = stats[k]
                if isinstance(v, str) and len(v) > 60:
                    v = fn(v)
                elif isinstance(v, float):
                    v = f'{v:.1f}'
                print(f"    {k} = {v}")

    # 5. List all pet bonus records
    print("\n" + "=" * 80)
    print("SECTION 5: PET BONUS RECORDS")
    print("=" * 80)
    for name in db.record_names():
        nl = name.lower()
        if 'petbonus' in nl and 'soul' in nl:
            print(f"  {name}")


if __name__ == '__main__':
    main()
