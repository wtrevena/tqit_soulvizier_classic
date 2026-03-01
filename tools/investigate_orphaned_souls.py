"""Deep investigation of orphaned soul items and legacy 0.5% champions.

For orphaned souls: Extract every stat field and find unique/interesting
properties that our generated uber souls don't have.

For 0.5% champions: Explain what's happening and whether to act.

Also: Compare existing SV soul stat profiles vs our generated uber soul
profiles to find interesting abilities we could copy.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


BORING_FIELDS = {
    'templateName', 'Class', 'bitmap', 'mesh', 'itemCostName',
    'dropSound', 'dropSound3D', 'dropSoundWater',
    'itemClassification', 'characterBaseAttackSpeedTag',
    'castsShadows', 'maxTransparency', 'scale', 'shadowBias',
    'cannotPickUp', 'cannotPickUpMultiple', 'hidePrefixName',
    'hideSuffixName', 'quest', 'actorHeight', 'actorRadius',
    'physicsFriction', 'physicsMass', 'cameraShake', 'LightIntensity',
    'LightColor', 'LightRadius',
}

GENERIC_STATS = {
    'characterStrength', 'characterIntelligence', 'characterDexterity',
    'characterLife', 'characterMana', 'characterLifeRegen',
    'characterManaRegenModifier', 'characterAttackSpeedModifier',
    'characterSpellCastSpeedModifier',
    'offensivePhysicalMin', 'offensivePhysicalMax', 'offensivePhysicalModifier',
    'offensiveFireMin', 'offensiveFireMax', 'offensiveFireModifier',
    'offensiveColdMin', 'offensiveColdMax', 'offensiveColdModifier',
    'offensiveLightningMin', 'offensiveLightningMax', 'offensiveLightningModifier',
    'offensiveSlowPoisonMin', 'offensiveSlowPoisonMax', 'offensiveSlowPoisonModifier',
    'offensiveLifeMin', 'offensiveLifeMax', 'offensiveLifeModifier',
    'defensiveFire', 'defensiveCold', 'defensiveLightning',
    'defensivePoison', 'defensiveLife', 'defensiveProtection',
    'itemLevel', 'levelRequirement', 'itemNameTag', 'FileDescription',
    'strengthRequirement', 'intelligenceRequirement', 'dexterityRequirement',
    'numRelicSlots',
}


def get_all_stats(db, record_path):
    """Extract all stat fields from a soul record."""
    if not db.has_record(record_path):
        return None
    fields = db.get_fields(record_path)
    if not fields:
        return None
    stats = {}
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk in BORING_FIELDS:
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


def is_interesting(field_name):
    """Check if a field is something beyond generic stats."""
    return field_name not in GENERIC_STATS and field_name not in BORING_FIELDS


def main():
    if len(sys.argv) < 2:
        print("Usage: investigate_orphaned_souls.py <database.arz>")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('soul_investigation.md')

    # Index all soul items
    all_souls = {}
    uber_souls = {}
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if 'svc_uber' in nl:
                uber_souls[nl] = name
            else:
                all_souls[nl] = name

    # Index monsters with soul refs
    monster_soul_refs = set()
    legacy_champions = []
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        soul_ref = ''
        equip_chance = 0
        classification = ''
        cls = ''
        tmpl = ''
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if not tf.values:
                continue
            if rk == 'lootFinger2Item1' and tf.values[0]:
                for v in tf.values:
                    if v and 'soul' in str(v).lower():
                        soul_ref = str(v).lower()
                        monster_soul_refs.add(soul_ref.replace('\\', '/'))
            if rk == 'chanceToEquipFinger2' and isinstance(tf.values[0], (int, float)):
                equip_chance = float(tf.values[0])
            if rk == 'monsterClassification' and tf.values[0]:
                classification = str(tf.values[0])
            if rk == 'Class' and tf.values[0]:
                cls = str(tf.values[0])
            if rk == 'templateName' and tf.values[0]:
                tmpl = str(tf.values[0])
        if 'monster' not in cls.lower() and 'monster' not in tmpl.lower():
            continue
        if equip_chance > 0 and equip_chance < 1.0 and soul_ref:
            fn = name.replace('\\', '/').split('/')[-1].replace('.dbr', '')
            legacy_champions.append({
                'name': fn,
                'full_path': name,
                'classification': classification or '(none)',
                'equip_chance': equip_chance,
                'soul_ref': soul_ref,
            })

    # Find orphaned souls
    orphaned = {}
    for nl, name in all_souls.items():
        normalized = nl.replace('\\', '/')
        if normalized not in monster_soul_refs:
            orphaned[nl] = name

    print(f"Total SV souls: {len(all_souls)}")
    print(f"Orphaned souls (no monster ref): {len(orphaned)}")
    print(f"Legacy low-rate champions: {len(legacy_champions)}")

    # =================================================================
    # Analyze orphaned souls for interesting stats
    # =================================================================
    interesting_orphans = []
    all_interesting_fields = defaultdict(int)
    orphan_stats = {}

    for nl, name in sorted(orphaned.items()):
        stats = get_all_stats(db, name)
        if not stats:
            continue
        orphan_stats[nl] = stats

        interesting = {k: v for k, v in stats.items() if is_interesting(k)}
        if interesting:
            interesting_orphans.append({
                'path': name,
                'display': stats.get('FileDescription', name.split('/')[-1].split('\\')[-1]),
                'interesting_fields': interesting,
                'all_stats': stats,
            })
            for k in interesting:
                all_interesting_fields[k] += 1

    # =================================================================
    # Analyze ALL existing (non-orphaned) SV souls for interesting stats
    # =================================================================
    active_souls_interesting = []
    for nl, name in sorted(all_souls.items()):
        if nl in orphaned:
            continue
        stats = get_all_stats(db, name)
        if not stats:
            continue
        interesting = {k: v for k, v in stats.items() if is_interesting(k)}
        if interesting:
            active_souls_interesting.append({
                'path': name,
                'display': stats.get('FileDescription', name.split('/')[-1].split('\\')[-1]),
                'interesting_fields': interesting,
                'all_stats': stats,
            })
            for k in interesting:
                all_interesting_fields[k] += 1

    # =================================================================
    # Analyze uber souls to see what they have
    # =================================================================
    uber_stats_list = []
    uber_fields_used = set()
    for nl, name in sorted(uber_souls.items()):
        stats = get_all_stats(db, name)
        if stats:
            uber_stats_list.append(stats)
            uber_fields_used.update(stats.keys())

    # =================================================================
    # Write report
    # =================================================================
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# Soul Investigation - Orphans, Legacy Champions, and Interesting Stats\n\n")

        # --- Legacy Champions ---
        f.write("## Part 1: The 26 Legacy Champions at 0.5%\n\n")
        f.write("These monsters already had `chanceToEquipFinger2` set in the original SV database.\n")
        f.write("In TQIT, this field controlled equipment display chances. In AE, it also controls\n")
        f.write("whether equipped items (including souls) drop on death.\n\n")
        f.write("These are NOT our bug -- they're pre-existing SV data. At 0.5%, a soul drops\n")
        f.write("roughly once every 200 kills. Effectively negligible.\n\n")
        f.write("| Monster | Classification | Equip Chance | Soul Reference |\n")
        f.write("|---------|---------------|-------------|----------------|\n")
        for lc in sorted(legacy_champions, key=lambda x: x['name']):
            soul_fn = lc['soul_ref'].replace('\\', '/').split('/')[-1].replace('.dbr', '')
            f.write(f"| {lc['name']} | {lc['classification']} | {lc['equip_chance']}% | {soul_fn} |\n")

        # --- Interesting fields found across all souls ---
        f.write("\n\n## Part 2: Interesting/Unique Fields Found in Existing SV Souls\n\n")
        f.write("These are fields that existing SV souls use but our generated uber souls do NOT.\n")
        f.write("These could make uber souls more interesting and varied.\n\n")

        missing_from_uber = {k: v for k, v in all_interesting_fields.items()
                             if k not in uber_fields_used}
        present_in_uber = {k: v for k, v in all_interesting_fields.items()
                           if k in uber_fields_used}

        f.write("### Fields NOT used by any uber soul (candidates to add)\n\n")
        f.write("| Field | # Souls Using It | What It Does |\n")
        f.write("|-------|-----------------|-------------|\n")
        for k in sorted(missing_from_uber, key=missing_from_uber.get, reverse=True):
            desc = describe_field(k)
            f.write(f"| `{k}` | {missing_from_uber[k]} | {desc} |\n")

        f.write("\n### Fields already used by uber souls\n\n")
        f.write("| Field | # SV Souls Using It |\n")
        f.write("|-------|--------------------|\n")
        for k in sorted(present_in_uber, key=present_in_uber.get, reverse=True):
            f.write(f"| `{k}` | {present_in_uber[k]} |\n")

        # --- Showcase the most interesting existing souls ---
        f.write("\n\n## Part 3: Most Interesting Existing SV Souls\n\n")
        f.write("These active souls have unique abilities beyond basic stat boosts.\n")
        f.write("Sorted by number of interesting fields.\n\n")

        all_interesting = active_souls_interesting + interesting_orphans
        all_interesting.sort(key=lambda x: -len(x['interesting_fields']))

        shown = set()
        count = 0
        for soul in all_interesting:
            display = soul['display']
            if display in shown:
                continue
            shown.add(display)
            if count >= 60:
                break
            count += 1

            f.write(f"### {display}\n\n")
            f.write(f"Path: `{soul['path']}`\n\n")

            f.write("**Unique/interesting stats:**\n")
            for k, v in sorted(soul['interesting_fields'].items()):
                desc = describe_field(k)
                if isinstance(v, float):
                    f.write(f"- `{k}` = {v:.2f} ({desc})\n")
                else:
                    f.write(f"- `{k}` = {v} ({desc})\n")

            basics = soul['all_stats']
            basic_parts = []
            for bk in ['characterStrength', 'characterIntelligence', 'characterLife',
                        'characterMana', 'itemLevel']:
                if bk in basics:
                    basic_parts.append(f"{bk}={basics[bk]}")
            if basic_parts:
                f.write(f"\nBasic stats: {', '.join(basic_parts)}\n")
            f.write("\n")

        # --- Summary of what uber souls could gain ---
        f.write("\n## Part 4: Recommendations for Enhancing Uber Souls\n\n")
        f.write("Our 140 uber souls currently have these types of bonuses:\n")
        f.write("- Flat stat boosts (Str, Int, HP, MP, regen)\n")
        f.write("- Flat elemental damage (fire/cold/lightning/poison/life/physical min+max)\n")
        f.write("- Elemental damage % modifiers\n")
        f.write("- Elemental resistances (with opposing element penalties)\n")
        f.write("- Attack speed / cast speed / mana regen %\n")
        f.write("- Armor (for tanks)\n\n")
        f.write("What existing SV souls have that ours DON'T:\n\n")

        cool_fields = [
            ('skillName1', 'Grants a skill to the player (most impactful!)'),
            ('augmentSkillName1', 'Augments/enhances a player skill'),
            ('augmentSkillLevel1', 'Level of augmented skill'),
            ('offensiveSlowLifeLeechMin', 'Life leech on hit'),
            ('offensiveSlowLifeLeechMax', 'Life leech on hit'),
            ('offensiveSlowManaLeechMin', 'Mana leech on hit'),
            ('offensiveSlowManaLeechMax', 'Mana leech on hit'),
            ('retaliationPhysicalMin', 'Reflects physical damage back to attackers'),
            ('retaliationFireMin', 'Reflects fire damage back'),
            ('retaliationColdMin', 'Reflects cold damage back'),
            ('retaliationLightningMin', 'Reflects lightning damage back'),
            ('retaliationPoisonMin', 'Reflects poison damage back'),
            ('offensiveSlowPhysicalMin', 'Bleeding damage over time'),
            ('offensiveSlowColdMin', 'Frostburn damage over time'),
            ('offensiveSlowFireMin', 'Burn damage over time'),
            ('offensiveSlowLightningMin', 'Electrocute damage over time'),
            ('offensiveTotalDamageModifier', 'Global % damage boost to ALL damage'),
            ('offensivePercentCurrentLifeMin', '% current life as damage'),
            ('characterRunSpeedModifier', 'Movement speed bonus'),
            ('characterTotalSpeedModifier', 'Total speed (move+attack+cast) bonus'),
            ('characterEnergyAbsorptionPercent', 'Energy shield / damage absorb'),
            ('characterDodgePercent', 'Chance to dodge attacks'),
            ('characterDeflectProjectile', 'Chance to deflect projectiles'),
            ('defensiveAbsorption', 'Flat damage absorption'),
            ('offensiveStunMin', 'Stun duration on hit'),
            ('offensiveFreezeMin', 'Freeze duration on hit'),
            ('offensiveFumbleMin', 'Chance to make enemy fumble'),
            ('offensiveProjectileFumbleMin', 'Chance to disrupt enemy spells'),
        ]
        for field, desc in cool_fields:
            count = all_interesting_fields.get(field, 0)
            if count > 0:
                f.write(f"- **{desc}** (`{field}`): used by {count} existing SV souls\n")

    print(f"Report: {out_path}")


def describe_field(field_name):
    """Human-readable description of common TQ DBR fields."""
    descriptions = {
        'skillName1': 'Grants a SKILL to the wearer',
        'skillLevel1': 'Level of granted skill',
        'augmentSkillName1': 'Augments/boosts an existing skill',
        'augmentSkillLevel1': 'Level of skill augment',
        'augmentMasteryName1': 'Augments a mastery tree',
        'augmentMasteryLevel1': 'Level of mastery augment',
        'offensiveSlowLifeLeechMin': 'Life leech per second',
        'offensiveSlowLifeLeechMax': 'Life leech per second (max)',
        'offensiveSlowManaLeechMin': 'Mana leech per second',
        'offensiveSlowManaLeechMax': 'Mana leech per second (max)',
        'offensiveTotalDamageModifier': '% bonus to ALL damage types',
        'offensivePercentCurrentLifeMin': '% of current life as damage',
        'offensivePercentCurrentLifeMax': '% of current life as damage (max)',
        'offensiveStunMin': 'Stun chance/duration',
        'offensiveFreezeMin': 'Freeze chance/duration',
        'offensiveSlowPhysicalMin': 'Bleeding damage over time',
        'offensiveSlowPhysicalMax': 'Bleeding damage over time (max)',
        'offensiveSlowFireMin': 'Burn damage over time',
        'offensiveSlowFireMax': 'Burn damage over time (max)',
        'offensiveSlowColdMin': 'Frostburn damage over time',
        'offensiveSlowColdMax': 'Frostburn damage over time (max)',
        'offensiveSlowLightningMin': 'Electrocute damage over time',
        'offensiveSlowLightningMax': 'Electrocute damage over time (max)',
        'offensiveFumbleMin': 'Fumble attack chance',
        'offensiveProjectileFumbleMin': 'Disrupts enemy projectiles/spells',
        'retaliationPhysicalMin': 'Physical retaliation damage',
        'retaliationPhysicalMax': 'Physical retaliation (max)',
        'retaliationFireMin': 'Fire retaliation damage',
        'retaliationFireMax': 'Fire retaliation (max)',
        'retaliationColdMin': 'Cold retaliation damage',
        'retaliationLightningMin': 'Lightning retaliation damage',
        'retaliationPoisonMin': 'Poison retaliation damage',
        'retaliationLifeMin': 'Life retaliation damage',
        'characterRunSpeedModifier': 'Movement speed %',
        'characterTotalSpeedModifier': 'Total speed % (move+atk+cast)',
        'characterEnergyAbsorptionPercent': 'Energy shield %',
        'characterDodgePercent': 'Dodge chance %',
        'characterDeflectProjectile': 'Deflect projectile %',
        'defensiveAbsorption': 'Flat damage absorption',
        'defensiveAbsorptionModifier': '% damage absorption',
        'defensiveSlowLifeLeech': 'Resist life leech %',
        'defensiveSlowManaLeech': 'Resist mana leech %',
        'defensiveTotalSpeedResistance': 'Resist slow effects',
        'characterOffensiveAbility': 'Offensive Ability (hit chance)',
        'characterDefensiveAbility': 'Defensive Ability (dodge chance)',
        'characterOffensiveAbilityModifier': 'OA % modifier',
        'characterDefensiveAbilityModifier': 'DA % modifier',
        'offensiveManaBurnMin': 'Burns enemy mana',
        'offensiveManaBurnMax': 'Burns enemy mana (max)',
        'offensiveManaBurnRatioMin': 'Mana burn damage ratio',
        'skillCooldownReduction': 'Cooldown reduction %',
        'conversionInPhysical': 'Converts physical to another element',
        'conversionOutFire': 'Output element for conversion',
        'offensiveBaseDamageModifier': 'Weapon damage %',
        'racialBonusPercentDamage': '% damage vs specific race',
        'racialBonusAbsoluteDefense': 'Armor vs specific race',
        'racialBonusRace': 'Target race for racial bonus',
    }
    return descriptions.get(field_name, field_name)


if __name__ == '__main__':
    sys.exit(main())
