"""Deep diagnostic of soul drop rates on deployed database.

Checks:
1. Which early-game hero monsters have souls assigned
2. What the actual lootFinger2 field values are
3. Whether data types are correct
4. Sample specific monsters the player would encounter in Act 1
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_FLOAT, DATA_TYPE_INT, DATA_TYPE_STRING

def main():
    db_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(db_path)

    # Find all hero monsters (Act 1 early game area)
    print('=== Hero Monster Soul Assignments ===\n')

    hero_keywords = ['hero', 'champion', 'boss']
    act1_areas = ['greece', 'graeae', 'satyr', 'skeleton', 'boar', 'spider',
                  'harpy', 'centaur', 'gorgon', 'minotaur', 'cyclops',
                  'nymph', 'maenad', 'arachnos', 'eurynomus', 'zombie',
                  'ghost']

    # Check ALL monsters with lootFinger2Item1
    has_soul = 0
    has_chance = 0
    zero_chance = 0
    missing_chance = 0
    monsters_with_souls = []

    for name in db.record_names():
        nl = name.lower()
        if not ('monster' in nl or 'creature' in nl or 'proxy' in nl):
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        soul_item = None
        soul_chance = None
        soul_chance_dtype = None

        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'lootFinger2Item1':
                if tf.values and tf.values[0]:
                    soul_item = str(tf.values[0])
            elif rk == 'lootFinger2Chance':
                if tf.values and tf.values[0] is not None:
                    soul_chance = tf.values[0]
                    soul_chance_dtype = tf.dtype

        if soul_item and soul_item.strip():
            has_soul += 1
            if soul_chance is not None and float(soul_chance) > 0:
                has_chance += 1
            elif soul_chance is not None and float(soul_chance) == 0:
                zero_chance += 1
            else:
                missing_chance += 1

            monsters_with_souls.append({
                'name': name,
                'soul': soul_item,
                'chance': soul_chance,
                'chance_dtype': soul_chance_dtype,
            })

    print(f'Monsters with soul item assigned: {has_soul}')
    print(f'  With non-zero drop chance: {has_chance}')
    print(f'  With zero drop chance: {zero_chance}')
    print(f'  With missing drop chance: {missing_chance}')

    # Show data type distribution
    dtype_counts = {}
    for m in monsters_with_souls:
        if m['chance'] is not None:
            dt = m['chance_dtype']
            dtype_counts[dt] = dtype_counts.get(dt, 0) + 1
    print(f'\n  Drop chance data types: {dtype_counts}')
    print(f'  (Expected: {DATA_TYPE_FLOAT}=float, {DATA_TYPE_INT}=int)')

    # Show sample of monsters with working drops
    print(f'\n=== Sample monsters WITH working drops ===')
    working = [m for m in monsters_with_souls if m['chance'] and float(m['chance']) > 0]
    for m in working[:20]:
        print(f"  {m['name']}")
        print(f"    soul: {m['soul']}")
        print(f"    chance: {m['chance']} (dtype={m['chance_dtype']})")

    # Show monsters with zero/missing chances
    if zero_chance > 0 or missing_chance > 0:
        print(f'\n=== Sample monsters with BROKEN drops ===')
        broken = [m for m in monsters_with_souls
                  if not m['chance'] or float(m['chance']) == 0]
        for m in broken[:20]:
            print(f"  {m['name']}")
            print(f"    soul: {m['soul']}")
            print(f"    chance: {m['chance']} (dtype={m['chance_dtype']})")

    # Check specifically for early game heroes
    print(f'\n=== Early Game Hero Monsters (Act 1) ===')
    for m in monsters_with_souls:
        nl = m['name'].lower()
        is_hero = any(kw in nl for kw in ['hero', 'champion', '_h_', '_h0', 'boss', 'unique'])
        is_early = any(area in nl for area in act1_areas)
        if is_hero or is_early:
            chance_str = f"{m['chance']} (dtype={m['chance_dtype']})" if m['chance'] is not None else 'NONE'
            print(f"  {m['name']}")
            print(f"    soul: {m['soul']}")
            print(f"    chance: {chance_str}")

    # Now check the ACTUAL raw field encoding for a few records
    print(f'\n=== Raw field dump for first 5 soul-bearing monsters ===')
    for m in working[:5]:
        name = m['name']
        fields = db.get_fields(name)
        print(f'\n  Record: {name}')
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'lootFinger2' in rk or 'loot' in rk.lower() and 'finger' in rk.lower():
                print(f'    {rk}: dtype={tf.dtype}, values={tf.values}')

    # Also check: are there monsters classified as "hero" in their charLevel/monsterClassification?
    print(f'\n=== Monster classification check ===')
    classification_count = {}
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'monsterClassification':
                val = str(tf.values[0]) if tf.values else ''
                classification_count[val] = classification_count.get(val, 0) + 1

    print(f'  Monster classifications found:')
    for cls, count in sorted(classification_count.items()):
        print(f'    {cls}: {count}')


if __name__ == '__main__':
    main()
