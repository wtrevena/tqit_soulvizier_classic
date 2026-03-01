"""Look at the 5 AE monsters that use chanceToEquipFinger2 to see the full pattern.
Also check the full equip pattern for Finger1 as a reference."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    ae_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(ae_path)

    print('=== AE monsters with chanceToEquipFinger2 ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        has_f2 = False
        for key, tf in fields.items():
            if key.split('###')[0] == 'chanceToEquipFinger2' and tf.values:
                ch = float(tf.values[0]) if tf.values[0] else 0
                if ch > 0:
                    has_f2 = True
        if not has_f2:
            continue
        print(f'\n  {name}:')
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rk = key.split('###')[0]
            rl = rk.lower()
            if any(kw in rl for kw in ['finger', 'equip', 'drop', 'loot', 'class']):
                if tf.values and any(v is not None and str(v).strip() and str(v) != '0' and str(v) != '0.0' for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 120:
                        vstr = vstr[:120] + '...'
                    print(f'    {rk} = {vstr}')

    # Also show 2 sample heroes that use chanceToEquipFinger1 (the common pattern)
    print('\n\n=== AE sample heroes with chanceToEquipFinger1 (common pattern) ===')
    shown = 0
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        classification = ''
        has_f1 = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
            if rk == 'chanceToEquipFinger1' and tf.values:
                ch = float(tf.values[0]) if tf.values[0] else 0
                if ch > 0:
                    has_f1 = True
        if classification != 'Hero' or not has_f1:
            continue
        print(f'\n  {name}:')
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rk = key.split('###')[0]
            rl = rk.lower()
            if any(kw in rl for kw in ['finger', 'equip', 'drop', 'classification']):
                if tf.values and any(v is not None and str(v).strip() and str(v) != '0' and str(v) != '0.0' for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 150:
                        vstr = vstr[:150] + '...'
                    print(f'    {rk} = {vstr}')
        shown += 1
        if shown >= 3:
            break


if __name__ == '__main__':
    main()
