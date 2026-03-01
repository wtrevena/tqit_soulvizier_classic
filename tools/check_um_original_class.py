"""Check um_ monsters in the ORIGINAL SV 0.98i database (before our patches)
to see what their intended classifications were."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    monsters = []
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fn = nl.replace('\\', '/').split('/')[-1]
        if not fn.startswith('um_'):
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        cls_val = ''
        classification = ''
        level = 0
        hp = 0
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'Class' and tf.values:
                cls_val = str(tf.values[0])
            if rk == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
            if rk == 'charLevel' and tf.values:
                level = int(tf.values[0]) if isinstance(tf.values[0], (int, float)) else 0
            if rk == 'characterLife' and tf.values:
                hp = float(tf.values[0]) if isinstance(tf.values[0], (int, float)) else 0
        if 'Monster' not in cls_val and 'monster' not in cls_val:
            continue

        has_soul = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'lootFinger2Item1' and tf.values:
                for v in tf.values:
                    if v and 'soul' in str(v).lower():
                        has_soul = True
        monsters.append({
            'name': name,
            'fn': fn.replace('.dbr', ''),
            'classification': classification or '(none)',
            'level': level,
            'hp': hp,
            'has_soul': has_soul,
        })

    # Show the non-Hero/Boss ones
    print(f'Total um_ monsters: {len(monsters)}\n')

    print('=== um_ monsters that were NOT Hero/Boss in the original SV mod ===')
    for m in sorted(monsters, key=lambda x: (x['classification'], -x['level'])):
        if m['classification'] in ('Hero', 'Boss'):
            continue
        soul_tag = 'HAS SOUL' if m['has_soul'] else 'no soul'
        print(f"  {m['fn']:<50s} class={m['classification']:10s} lvl={m['level']:<4d} hp={m['hp']:<12.0f} {soul_tag}")

    print(f'\n=== Summary ===')
    for cls in ['Hero', 'Boss', 'Champion', 'Common', '(none)']:
        group = [m for m in monsters if m['classification'] == cls]
        with_soul = sum(1 for m in group if m['has_soul'])
        print(f"  {cls:12s}: {len(group):3d} total, {with_soul:3d} had souls in original SV")


if __name__ == '__main__':
    main()
