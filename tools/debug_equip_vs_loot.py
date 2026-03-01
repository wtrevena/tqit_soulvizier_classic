"""Check whether souls use equipment fields or loot fields on monsters."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    equip_finger2_soul = 0
    loot_finger2_soul = 0
    both = 0
    equip_samples = []
    loot_samples = []

    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        # Check equipment fields
        has_equip_soul = False
        equip_chance = 0
        equip_items = []
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'chanceToEquipFinger2' and tf.values:
                equip_chance = float(tf.values[0]) if tf.values[0] else 0
            if rk.startswith('equipFinger2Item') and tf.values:
                for v in tf.values:
                    if v and 'soul' in str(v).lower():
                        has_equip_soul = True
                        equip_items.append(str(v)[:80])

        # Check loot fields  
        has_loot_soul = False
        loot_chance = 0
        loot_items = []
        loot_val = db.get_field_value(name, 'lootFinger2Item1')
        if loot_val and 'soul' in str(loot_val).lower():
            has_loot_soul = True
            loot_items.append(str(loot_val)[:80])
        lc = db.get_field_value(name, 'lootFinger2Chance')
        if lc:
            loot_chance = float(lc)

        fn = nl.split('\\')[-1]
        if has_equip_soul:
            equip_finger2_soul += 1
            if len(equip_samples) < 5:
                equip_samples.append((fn, equip_chance, equip_items[0] if equip_items else ''))
        if has_loot_soul:
            loot_finger2_soul += 1
            if len(loot_samples) < 5:
                loot_samples.append((fn, loot_chance, loot_items[0] if loot_items else ''))
        if has_equip_soul and has_loot_soul:
            both += 1

    print('=== Soul Assignment Method ===')
    print(f'  Using equipFinger2 (equipment): {equip_finger2_soul}')
    print(f'  Using lootFinger2 (loot drops): {loot_finger2_soul}')
    print(f'  Using both: {both}')

    print(f'\n=== Equipment Soul Samples ===')
    for fn, ch, item in equip_samples:
        print(f'  {fn:50s} equipChance={ch:6.1f} item={item}')

    print(f'\n=== Loot Soul Samples ===')
    for fn, ch, item in loot_samples:
        print(f'  {fn:50s} lootChance={ch:6.1f} item={item}')

    # Dump full equip fields for one monster that has a soul
    print(f'\n=== Full equip fields for a monster with soul ===')
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        has_soul = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk.startswith('equipFinger2') and tf.values:
                for v in tf.values:
                    if v and 'soul' in str(v).lower():
                        has_soul = True
        if has_soul:
            print(f'  {name}:')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                if 'finger2' in rk.lower() or 'finger1' in rk.lower():
                    if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                        print(f'    {rk} = {tf.values}')
            break


if __name__ == '__main__':
    main()
