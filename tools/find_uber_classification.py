"""Find uber boss monster classifications in the mod database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find Toxeus specifically
    print('=== Toxeus records ===')
    for name in db.record_names():
        if 'toxeus' in name.lower():
            fields = db.get_fields(name)
            if not fields:
                continue
            cls_val = ''
            classification = ''
            tmpl = ''
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if rk == 'Class' and tf.values:
                    cls_val = str(tf.values[0])
                if rk == 'monsterClassification' and tf.values:
                    classification = str(tf.values[0])
                if rk == 'templateName' and tf.values:
                    tmpl = str(tf.values[0])
            if cls_val:
                print(f'  {name}')
                print(f'    Class={cls_val}  monsterClassification={classification}  template={tmpl}')

    # Find all unique monsterClassification values used in the mod
    print('\n=== All monsterClassification values ===')
    class_counts = {}
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        classification = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
        if classification:
            class_counts[classification] = class_counts.get(classification, 0) + 1
    for cls, count in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f'  {cls:20s} {count:5d} monsters')

    # Find monsters with 'um_' prefix (uber monsters) and their classifications
    print('\n=== um_ prefix monsters (uber) - classification distribution ===')
    um_class_counts = {}
    um_samples = {}
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
        classification = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
        if not classification:
            classification = '(none)'
        um_class_counts[classification] = um_class_counts.get(classification, 0) + 1
        if classification not in um_samples or len(um_samples[classification]) < 3:
            um_samples.setdefault(classification, []).append(fn)
    for cls, count in sorted(um_class_counts.items(), key=lambda x: -x[1]):
        samples = ', '.join(um_samples.get(cls, [])[:3])
        print(f'  {cls:20s} {count:5d}  e.g. {samples}')


if __name__ == '__main__':
    main()
