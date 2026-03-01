"""Check what classification Carrion Crow and other common monsters have,
and whether they already had souls in the original SV 0.98i."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find all monsters that already have lootFinger2Item1 with soul references
    # and check their classification
    class_counts = {}
    common_with_souls = []

    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue

        classification = ''
        has_soul = False
        soul_ref = ''
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
            if rk == 'lootFinger2Item1' and tf.values:
                for v in tf.values:
                    if v and 'soul' in str(v).lower():
                        has_soul = True
                        soul_ref = str(v)[:80]

        if not has_soul:
            continue

        cls = classification or '(none)'
        class_counts[cls] = class_counts.get(cls, 0) + 1

        if cls not in ('Hero', 'Boss'):
            fn = nl.replace('\\', '/').split('/')[-1].replace('.dbr', '')
            common_with_souls.append((fn, cls, soul_ref))

    print('=== Monsters with souls by classification (original SV) ===')
    for cls, cnt in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f'  {cls:15s} {cnt:5d}')

    print(f'\n=== Non-Hero/Boss monsters with souls ({len(common_with_souls)}) ===')
    for fn, cls, soul in sorted(common_with_souls)[:50]:
        print(f'  {fn:<50s} class={cls:12s} soul={soul}')
    if len(common_with_souls) > 50:
        print(f'  ... and {len(common_with_souls) - 50} more')


if __name__ == '__main__':
    main()
