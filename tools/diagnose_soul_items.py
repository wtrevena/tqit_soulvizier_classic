"""Check if soul item records actually exist in the database,
and cross-reference monster classifications with soul assignments."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def find_icase(db, path):
    pl = path.lower().replace('/', '\\')
    for name in db.record_names():
        if name.lower() == pl:
            return name
    return None


def main():
    db_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(db_path)

    all_names_lower = {n.lower().replace('/', '\\'): n for n in db.record_names()}

    # Collect ALL monster records with soul assignments
    print('=== Cross-reference: Monster Classification vs Soul Assignment ===\n')

    class_with_soul = {}
    class_without_soul = {}
    missing_soul_items = []
    existing_soul_items = set()
    total_hero_records = []

    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue

        classification = None
        soul_item = None
        soul_chance = None

        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'monsterClassification':
                classification = str(tf.values[0]) if tf.values else None
            elif rk == 'lootFinger2Item1':
                if tf.values and tf.values[0] and str(tf.values[0]).strip():
                    soul_item = tf.values  # all variants
            elif rk == 'lootFinger2Chance':
                if tf.values and tf.values[0] is not None:
                    soul_chance = tf.values[0]

        if classification:
            if soul_item:
                class_with_soul[classification] = class_with_soul.get(classification, 0) + 1
            else:
                class_without_soul[classification] = class_without_soul.get(classification, 0) + 1

            if classification == 'Hero':
                total_hero_records.append({
                    'name': name,
                    'soul_item': soul_item,
                    'soul_chance': soul_chance,
                })

            # Check if soul item DBRs exist
            if soul_item:
                for si in soul_item:
                    si_str = str(si).strip()
                    if not si_str:
                        continue
                    si_lower = si_str.lower().replace('/', '\\')
                    if si_lower in all_names_lower:
                        existing_soul_items.add(si_str)
                    else:
                        missing_soul_items.append((name, si_str))

    print('Monsters WITH souls by classification:')
    for cls in sorted(class_with_soul.keys()):
        print(f'  {cls}: {class_with_soul[cls]}')

    print('\nMonsters WITHOUT souls by classification:')
    for cls in sorted(class_without_soul.keys()):
        print(f'  {cls}: {class_without_soul[cls]}')

    print(f'\n=== Soul Item Record Existence ===')
    print(f'Unique soul item paths that EXIST in database: {len(existing_soul_items)}')
    print(f'Soul item references that are MISSING from database: {len(missing_soul_items)}')

    if missing_soul_items:
        print(f'\nFirst 30 MISSING soul item records:')
        seen = set()
        count = 0
        for monster, soul in missing_soul_items:
            if soul not in seen:
                seen.add(soul)
                print(f'  {soul}')
                print(f'    (referenced by: {monster})')
                count += 1
                if count >= 30:
                    break

    # Show Hero-class monsters specifically
    print(f'\n=== Hero-class Monster Details ({len(total_hero_records)} total) ===')
    heroes_with = [h for h in total_hero_records if h['soul_item']]
    heroes_without = [h for h in total_hero_records if not h['soul_item']]

    print(f'  Heroes WITH soul assignment: {len(heroes_with)}')
    print(f'  Heroes WITHOUT soul assignment: {len(heroes_without)}')

    if heroes_without:
        print(f'\n  First 30 Hero monsters WITHOUT souls:')
        for h in heroes_without[:30]:
            print(f'    {h["name"]}')

    # Check early-game hero monsters specifically (level-based naming)
    print(f'\n=== Early Game Hero Monsters (levels 1-15) ===')
    for h in total_hero_records:
        nl = h['name'].lower()
        # Check for low level numbers in the name
        import re
        nums = re.findall(r'_(\d+)\.dbr$', nl)
        if nums:
            level = int(nums[0])
            if level <= 15:
                soul_str = 'YES' if h['soul_item'] else 'NO'
                chance_str = str(h['soul_chance']) if h['soul_chance'] else 'NONE'
                print(f'  {h["name"]} -> soul={soul_str}, chance={chance_str}')

    # Also check Champion class
    print(f'\n=== Champion Classification Details ===')
    champ_with = class_with_soul.get('Champion', 0)
    champ_without = class_without_soul.get('Champion', 0)
    print(f'  Champions WITH soul: {champ_with}')
    print(f'  Champions WITHOUT soul: {champ_without}')


if __name__ == '__main__':
    main()
