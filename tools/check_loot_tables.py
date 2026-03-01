"""Check loot table types and find how to drop multiple items."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find LootMasterTable examples
    print('=== LootMasterTable records (first 10) ===')
    count = 0
    for name in sorted(db.record_names()):
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'Class' and tf.values and 'mastertable' in str(tf.values[0]).lower():
                print(f'  {name} (Class={tf.values[0]})')
                count += 1
                break
        if count >= 10:
            break

    # Dump a sample LootMasterTable to see fields
    print('\n=== Sample LootMasterTable fields ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        cls = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'Class' and tf.values:
                cls = str(tf.values[0])
        if 'LootMasterTable' in cls:
            print(f'  {name} (Class={cls}):')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                if tf.values and any(v is not None for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 120:
                        vstr = vstr[:120] + '...'
                    print(f'    {rk} = {vstr}')
            break

    # Check what references startingloot.dbr
    print('\n=== Records referencing startingloot ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'startingloot' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Check for "give player item" or auto-grant item mechanisms
    print('\n=== Records with give/grant item fields ===')
    count = 0
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if ('giveplayeritem' in rk or 'grantitem' in rk or 'autoitem' in rk or
                'spawnitem' in rk):
                print(f'  {name} -> {key.split("###")[0]} = {tf.values}')
                count += 1
        if count > 20:
            break

    # List loot template types
    print('\n=== Loot table Class types found ===')
    classes = set()
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            if key.split('###')[0] == 'Class' and tf.values:
                cls = str(tf.values[0])
                if 'loot' in cls.lower():
                    classes.add(cls)
    for c in sorted(classes):
        print(f'  {c}')


if __name__ == '__main__':
    main()
