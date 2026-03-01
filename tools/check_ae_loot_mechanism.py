"""Check how AE base game handles monster loot drops.
Find which loot fields AE actually uses vs what SV uses."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    ae_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(ae_path)

    # Catalog ALL loot-related fields used on creature records
    loot_field_counts = {}
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            rl = rk.lower()
            if ('loot' in rl or 'drop' in rl) and tf.values:
                has_val = any(v is not None and str(v).strip() and str(v) != '0' and str(v) != '0.0' for v in tf.values)
                if has_val:
                    loot_field_counts[rk] = loot_field_counts.get(rk, 0) + 1

    print('=== AE base: Loot fields used on creatures (non-zero) ===')
    for field, count in sorted(loot_field_counts.items(), key=lambda x: -x[1]):
        print(f'  {field:40s} {count:5d} monsters')

    # Check what chanceToEquipFinger fields look like
    print('\n=== AE base: chanceToEquipFinger usage ===')
    finger_counts = {}
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk.startswith('chanceToEquipFinger') and tf.values:
                ch = float(tf.values[0]) if tf.values[0] else 0
                if ch > 0:
                    finger_counts[rk] = finger_counts.get(rk, 0) + 1
    for field, count in sorted(finger_counts.items()):
        print(f'  {field}: {count} monsters')

    # Sample a hero monster to see ALL its loot/drop/equip fields
    print('\n=== AE base: Sample hero monster (all loot/equip fields) ===')
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        classification = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
        if classification != 'Hero':
            continue
        print(f'  {name}:')
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rk = key.split('###')[0]
            rl = rk.lower()
            if any(kw in rl for kw in ['loot', 'drop', 'equip', 'finger', 'misc', 'chest']):
                if tf.values and any(v is not None and str(v).strip() and str(v) != '0' and str(v) != '0.0' for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 120:
                        vstr = vstr[:120] + '...'
                    print(f'    {rk} = {vstr}')
        break

    # Check lootFinger2 specifically
    print('\n=== AE base: lootFinger2Item1 usage ===')
    count = 0
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        val = None
        for key, tf in fields.items():
            if key.split('###')[0] == 'lootFinger2Item1' and tf.values:
                for v in tf.values:
                    if v and str(v).strip():
                        val = v
        if val:
            print(f'  {name} -> {str(val)[:100]}')
            count += 1
    print(f'  Total: {count}')


if __name__ == '__main__':
    main()
