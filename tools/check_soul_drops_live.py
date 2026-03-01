"""Check soul drop rates on the deployed database, focusing on hero monsters."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    hero_keywords = ['hero', 'champion']
    boss_keywords = ['boss', 'quest', 'typhon', 'hades', 'hydra', 'medusa',
                     'minotaurlord', 'talos', 'cerberus', 'cyclops']

    # Categorize all monsters with souls
    has_soul = 0
    no_soul = 0
    zero_chance = 0
    low_chance = 0  # < 1.0 (old scale)
    correct_chance = 0
    hero_samples = []
    boss_samples = []
    chance_histogram = {}

    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        cls_val = ''
        tmpl_val = ''
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'Class' and tf.values:
                cls_val = str(tf.values[0]).lower()
            elif rk == 'templateName' and tf.values:
                tmpl_val = str(tf.values[0]).lower()

        if 'monster' not in cls_val and 'monster' not in tmpl_val:
            continue

        soul = db.get_field_value(name, 'lootFinger2Item1')
        chance = db.get_field_value(name, 'lootFinger2Chance')

        if not soul or soul == '' or soul == 0:
            no_soul += 1
            continue

        has_soul += 1
        ch = float(chance) if chance else 0.0

        if ch == 0.0:
            zero_chance += 1
        elif ch < 1.0:
            low_chance += 1
        else:
            correct_chance += 1

        # Histogram
        bucket = int(ch)
        chance_histogram[bucket] = chance_histogram.get(bucket, 0) + 1

        is_hero = any(kw in nl for kw in hero_keywords)
        is_boss = any(kw in nl for kw in boss_keywords)

        fn = nl.split('\\')[-1].split('/')[-1]
        if is_hero and len(hero_samples) < 15:
            hero_samples.append((fn, ch, str(soul)[:60]))
        elif is_boss and len(boss_samples) < 15:
            boss_samples.append((fn, ch, str(soul)[:60]))

    print(f'=== Soul Drop Rate Summary ===')
    print(f'  Monsters with souls: {has_soul}')
    print(f'  Monsters without souls: {no_soul}')
    print(f'  Zero chance (0.0): {zero_chance}')
    print(f'  Low chance (<1.0, old scale bug): {low_chance}')
    print(f'  Correct chance (>=1.0): {correct_chance}')

    print(f'\n=== Chance Histogram ===')
    for bucket in sorted(chance_histogram.keys()):
        count = chance_histogram[bucket]
        print(f'  {bucket:6d}%: {count} monsters')

    print(f'\n=== Hero Monster Samples ===')
    for fn, ch, soul in hero_samples:
        print(f'  {fn:50s} chance={ch:6.1f}  soul={soul}')

    print(f'\n=== Boss Monster Samples ===')
    for fn, ch, soul in boss_samples:
        print(f'  {fn:50s} chance={ch:6.1f}  soul={soul}')

    # Check specific early-game heroes
    print(f'\n=== Early-game hero monsters (Greece) ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        if 'greece' not in nl and 'helos' not in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        cls_val = ''
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'Class' and tf.values:
                cls_val = str(tf.values[0]).lower()

        if 'monster' not in cls_val:
            continue

        soul = db.get_field_value(name, 'lootFinger2Item1')
        chance = db.get_field_value(name, 'lootFinger2Chance')
        char_level = db.get_field_value(name, 'charLevel')
        mon_class = db.get_field_value(name, 'monsterClassification')

        if soul and soul != '' and soul != 0:
            fn = nl.split('\\')[-1].split('/')[-1]
            ch = float(chance) if chance else 0.0
            print(f'  {fn:50s} lvl={char_level} class={mon_class} chance={ch:6.1f}')


if __name__ == '__main__':
    main()
