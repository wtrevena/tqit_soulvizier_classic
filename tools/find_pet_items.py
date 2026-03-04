"""
Find specific fixed equipment items for Rakanizeus and Boneash pet summons.
Searches the SoulvizierClassic database for unique/legendary/epic items in:
  - Swords (1H) for Rakanizeus
  - Staves for Boneash
  - Armbands/bracers for both
  - Rings for both
"""
import sys
sys.path.insert(0, 'tools')
from arz_patcher import ArzDatabase
from pathlib import Path
from collections import defaultdict

DB_PATH = Path('work/SoulvizierClassic/Database/SoulvizierClassic.arz')

# Fields to extract for display
INTERESTING_FIELDS = [
    'Class', 'itemClassification', 'itemNameTag', 'description', 'FileDescription',
    'itemText', 'itemQualityTag', 'levelRequirement',
    # Physical damage
    'offensivePhysMin', 'offensivePhysMax',
    # Fire damage
    'offensiveFireMin', 'offensiveFireMax',
    # Cold
    'offensiveColdMin', 'offensiveColdMax',
    # Lightning
    'offensiveLightningMin', 'offensiveLightningMax',
    # Poison
    'offensivePoisonMin', 'offensivePoisonMax',
    # Vitality
    'offensiveVitalityMin', 'offensiveVitalityMax',
    # Life leech
    'offensiveLifeLeechMin', 'offensiveLifeLeechMax',
    # Mana leech
    'offensiveManaLeechMin', 'offensiveManaLeechMax',
    # Percentage damage bonuses
    'offensivePhysicalModifier', 'offensiveFireModifier',
    'offensiveTotalDamageModifier',
    # Character bonuses
    'characterStrength', 'characterDexterity', 'characterIntelligence',
    'characterLife', 'characterLifeRegen', 'characterMana', 'characterManaRegen',
    'characterAttackSpeed', 'characterSpellCastSpeed',
    'characterOffensiveAbility', 'characterDefensiveAbility',
    'characterRunSpeed',
    'characterStrengthModifier', 'characterDexterityModifier', 'characterIntelligenceModifier',
    'characterLifeModifier', 'characterManaModifier',
    # Attack speed / cast speed (item-level)
    'offensiveSlowAttackSpeed', 'offensiveSlowRunSpeed',
    # Resistances
    'defensiveProtection',
    # Requirements
    'intelligenceRequirement', 'strengthRequirement', 'dexterityRequirement',
    # Weapon speed
    'characterBaseAttackSpeedTag',
    # Skill bonuses
    'augmentAllLevel', 'augmentMasteryLevel1', 'augmentMasteryName1',
    # Retaliation
    'retaliationPhysMin', 'retaliationPhysMax',
    'retaliationFireMin', 'retaliationFireMax',
    # Granted skills
    'itemSkillAutoController', 'itemSkillName',
]

def get_all_fields_with_pattern(fields, patterns):
    """Get all fields whose name contains any of the given patterns."""
    results = {}
    for key, tf in fields.items():
        name = key.split('###')[0]
        for pat in patterns:
            if pat in name.lower():
                # Only include if value is non-zero/non-empty
                val = tf.values
                if val and val != [0] and val != [0.0] and val != [''] and val != ['0']:
                    results[name] = tf.values
                break
    return results


def extract_item_info(db, record_name):
    """Extract all interesting fields from an item record."""
    fields = db.get_fields(record_name)
    if not fields:
        return None

    info = {'record': record_name}

    # Extract named fields
    for field_name in INTERESTING_FIELDS:
        for key, tf in fields.items():
            k = key.split('###')[0]
            if k == field_name:
                val = tf.values
                if val and val != [0] and val != [0.0] and val != [''] and val != ['0']:
                    info[field_name] = val[0] if len(val) == 1 else val
                break

    # Also grab all 'offensive*', 'defensive*', 'retaliat*', 'augment*', 'skill*' fields with nonzero values
    pattern_fields = get_all_fields_with_pattern(fields,
        ['offensive', 'defensive', 'retaliat', 'augment', 'skill', 'character', 'racial'])
    info['_extra'] = pattern_fields

    return info


def format_item(info, indent=2):
    """Pretty-print an item's info."""
    prefix = ' ' * indent
    lines = []
    lines.append(f"{prefix}Record: {info['record']}")

    # Basic identity
    for f in ['Class', 'itemClassification', 'FileDescription', 'itemNameTag', 'itemQualityTag', 'itemText']:
        if f in info:
            lines.append(f"{prefix}  {f}: {info[f]}")

    # Level/requirements
    for f in ['levelRequirement', 'strengthRequirement', 'dexterityRequirement', 'intelligenceRequirement']:
        if f in info:
            lines.append(f"{prefix}  {f}: {info[f]}")

    # Speed
    if 'characterBaseAttackSpeedTag' in info:
        lines.append(f"{prefix}  Speed: {info['characterBaseAttackSpeedTag']}")

    # Damage
    phys_min = info.get('offensivePhysMin', 0)
    phys_max = info.get('offensivePhysMax', 0)
    if phys_min or phys_max:
        lines.append(f"{prefix}  Physical Damage: {phys_min}-{phys_max}")

    fire_min = info.get('offensiveFireMin', 0)
    fire_max = info.get('offensiveFireMax', 0)
    if fire_min or fire_max:
        lines.append(f"{prefix}  Fire Damage: {fire_min}-{fire_max}")

    cold_min = info.get('offensiveColdMin', 0)
    cold_max = info.get('offensiveColdMax', 0)
    if cold_min or cold_max:
        lines.append(f"{prefix}  Cold Damage: {cold_min}-{cold_max}")

    light_min = info.get('offensiveLightningMin', 0)
    light_max = info.get('offensiveLightningMax', 0)
    if light_min or light_max:
        lines.append(f"{prefix}  Lightning Damage: {light_min}-{light_max}")

    # Character stats
    for f in ['characterStrength', 'characterDexterity', 'characterIntelligence',
              'characterLife', 'characterLifeRegen', 'characterMana', 'characterManaRegen',
              'characterAttackSpeed', 'characterSpellCastSpeed',
              'characterOffensiveAbility', 'characterDefensiveAbility',
              'characterRunSpeed']:
        if f in info:
            lines.append(f"{prefix}  {f}: {info[f]}")

    # Granted skills
    for f in ['itemSkillAutoController', 'itemSkillName', 'augmentAllLevel']:
        if f in info:
            lines.append(f"{prefix}  {f}: {info[f]}")

    # Extra fields (offensive/defensive/retaliation with non-zero values)
    extra = info.get('_extra', {})
    # Filter out fields we already displayed
    already_shown = set(INTERESTING_FIELDS)
    extra_filtered = {k: v for k, v in extra.items() if k not in already_shown}
    if extra_filtered:
        lines.append(f"{prefix}  --- Additional non-zero stats ---")
        for k, v in sorted(extra_filtered.items()):
            lines.append(f"{prefix}    {k}: {v}")

    return '\n'.join(lines)


def find_items(db, category_filter, classification_filter=None):
    """Find items matching category filter function and optional classification."""
    items = []
    for name in db.record_names():
        if not category_filter(name.lower()):
            continue
        info = extract_item_info(db, name)
        if info is None:
            continue
        if 'Class' not in info:
            continue
        # Filter by classification
        cls = info.get('itemClassification', '')
        if classification_filter and cls not in classification_filter:
            continue
        items.append(info)

    # Sort by levelRequirement
    items.sort(key=lambda x: (x.get('levelRequirement', 0) or 0))
    return items


def main():
    print("Loading database...")
    db = ArzDatabase.from_arz(DB_PATH)
    print()

    # ============================================================
    # SWORDS (1H) - for Rakanizeus
    # ============================================================
    print("=" * 80)
    print("SWORDS (1H) - Epic/Legendary/Rare")
    print("For Rakanizeus: physical melee warrior, STR 350, DEX 300, INT 200")
    print("=" * 80)

    def sword_filter(nl):
        if 'loottable' in nl or 'effect' in nl or 'projectile' in nl:
            return False
        if 'soul' in nl:
            return False
        # Include sword records from equipment paths
        if ('equipmentweapon' in nl) and 'sword' in nl:
            return True
        # Include drxitem swords
        if 'drxitem' in nl and 'sword' in nl:
            return True
        return False

    swords = find_items(db, sword_filter, {'Epic', 'Legendary', 'Rare'})
    print(f"\nFound {len(swords)} swords")
    for info in swords:
        print()
        print(format_item(info))

    # ============================================================
    # STAVES - for Boneash
    # ============================================================
    print("\n" + "=" * 80)
    print("STAVES - Epic/Legendary/Rare")
    print("For Boneash: fire caster, STR 150, DEX 150, INT 400")
    print("=" * 80)

    def staff_filter(nl):
        if 'loottable' in nl or 'effect' in nl or 'projectile' in nl or 'flight' in nl or 'impact' in nl:
            return False
        if 'soul' in nl:
            return False
        if 'sound' in nl or 'snd_' in nl:
            return False
        if ('equipmentweapon' in nl) and 'staff' in nl:
            return True
        if 'drxitem' in nl and 'staff' in nl:
            # Filter out FX/projectile records
            if 'fx' in nl or 'projectile' in nl:
                return False
            return True
        return False

    staves = find_items(db, staff_filter, {'Epic', 'Legendary', 'Rare'})
    print(f"\nFound {len(staves)} staves")
    for info in staves:
        print()
        print(format_item(info))

    # ============================================================
    # ARMBANDS / BRACERS - for both pets
    # ============================================================
    print("\n" + "=" * 80)
    print("ARMBANDS / BRACERS / ARMS - Epic/Legendary/Rare")
    print("=" * 80)

    def arms_filter(nl):
        if 'loottable' in nl or 'effect' in nl or 'projectile' in nl:
            return False
        if 'soul' in nl:
            return False
        # Arms equipment
        if 'equipmentarms' in nl:
            return True
        # Also check for armband/bracer in other paths
        if ('armband' in nl or 'bracer' in nl) and ('equipment' in nl or 'drxitem' in nl):
            return True
        # drxitem arms
        if 'drxitem' in nl and ('arms' in nl or 'forearm' in nl):
            # But not if it's a torso/head/legs record that has 'arms' in its prefix dir
            if 'torso' in nl or 'head' in nl or 'legs' in nl:
                return False
            return True
        return False

    arms = find_items(db, arms_filter, {'Epic', 'Legendary', 'Rare'})
    print(f"\nFound {len(arms)} armbands/bracers")
    for info in arms:
        print()
        print(format_item(info))

    # ============================================================
    # RINGS - for both pets
    # ============================================================
    print("\n" + "=" * 80)
    print("RINGS - Epic/Legendary/Rare")
    print("=" * 80)

    def ring_filter(nl):
        if 'loottable' in nl or 'effect' in nl or 'projectile' in nl:
            return False
        if 'soul' in nl:
            return False
        if 'attachitem' in nl:
            return False
        if 'equipmentring' in nl:
            return True
        return False

    rings = find_items(db, ring_filter, {'Epic', 'Legendary', 'Rare'})
    print(f"\nFound {len(rings)} rings")
    for info in rings:
        print()
        print(format_item(info))

    # ============================================================
    # FIXED EQUIPMENT EXAMPLES
    # ============================================================
    print("\n" + "=" * 80)
    print("FIXED EQUIPMENT EXAMPLES FROM EXISTING MONSTERS")
    print("=" * 80)

    count = 0
    for name in db.record_names():
        nl = name.lower()
        if 'creature' not in nl and 'monster' not in nl and 'drxcreature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        has_direct = False
        direct_fields = []
        for key, tf in fields.items():
            k = key.split('###')[0]
            if k.startswith('loot') and 'Item' in k and tf.dtype == 2:
                for v in tf.values:
                    vl = v.lower()
                    if 'loottable' not in vl and v.strip():
                        has_direct = True
                        direct_fields.append((k, tf.values))
                        break
        if has_direct and count < 5:
            print(f"\n  {name}")
            for field, vals in direct_fields:
                print(f"    {field} = {vals}")
            # Also show the chance fields
            for key, tf in fields.items():
                k = key.split('###')[0]
                if k.startswith('chanceToEquip') and tf.values and tf.values != [0] and tf.values != [0.0]:
                    print(f"    {k} = {tf.values}")
            count += 1


if __name__ == '__main__':
    main()
