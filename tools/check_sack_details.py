"""Deep dive into sack/bag count and starting loot."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Dump ALL fields from game engine records looking for sack/bag related
    print('=== xpack/game engine ALL sack/bag/inventory fields ===')
    for name in db.record_names():
        nl = name.lower()
        if nl != 'records\\xpack\\game\\gameengine.dbr':
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rk = key.split('###')[0]
            rl = rk.lower()
            if any(kw in rl for kw in ['sack', 'bag', 'inventory', 'char', 'player',
                                        'initial', 'start', 'default', 'extra', 'additional']):
                print(f'  {rk} = {tf.values}')

    # Dump ALL fields from DRX game engine
    print('\n=== DRX game engine sack/bag/inventory fields ===')
    for name in db.record_names():
        nl = name.lower()
        if 'drxgameengine' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rk = key.split('###')[0]
            rl = rk.lower()
            if any(kw in rl for kw in ['sack', 'bag', 'inventory', 'char', 'player',
                                        'initial', 'start', 'default', 'extra', 'additional']):
                print(f'  {rk} = {tf.values}')

    # Check starting loot records
    print('\n=== Starting loot records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'startingloot' in nl or 'starting_loot' in nl or 'initialloot' in nl:
            print(f'  {name}')
            fields = db.get_fields(name)
            if fields:
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    print(f'    {rk} = {tf.values}')

    # Check OneShot_Sack template for useful fields
    print('\n=== OneShot_Sack template fields (inventorysack.dbr) ===')
    for name in db.record_names():
        if 'inventorysack' in name.lower():
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                print(f'  {rk} [{tf.dtype}] = {tf.values}')

    # Check if there are "extra" or "numberOfSacks" fields anywhere
    print('\n=== Exhaustive search for sack count fields ===')
    sack_fields = set()
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key in fields:
            rk = key.split('###')[0].lower()
            if 'sack' in rk:
                sack_fields.add(key.split('###')[0])
    for f in sorted(sack_fields):
        print(f'  {f}')


if __name__ == '__main__':
    main()
