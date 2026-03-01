"""Find all stash/storage/caravan/inventory records in the database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(db_path)

    keywords = ['stash', 'caravan', 'transfer', 'sack', 'vault',
                'inventory', 'storage', 'chest']

    print('=== Records matching stash/storage keywords ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if any(kw in nl for kw in keywords):
            print(f'  {name}')

    # Also search for specific fields
    print('\n=== Records with numberOfSacks field ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'sack' in rk.lower() or 'stash' in rk.lower():
                vals = [str(v) for v in tf.values if v is not None]
                if vals:
                    print(f'  {name} -> {rk} = {vals}')

    # Check playerlevels for inventory settings
    print('\n=== Player levels / game engine inventory settings ===')
    for name in db.record_names():
        nl = name.lower()
        if 'playerlevels' in nl or 'gameengine' in nl:
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if any(kw in rk.lower() for kw in
                       ['sack', 'stash', 'inventory', 'transfer', 'caravan',
                        'storage', 'bag', 'slot']):
                    vals = [str(v) for v in tf.values if v is not None]
                    if vals:
                        print(f'  {name} -> {rk} = {vals}')

    # Check AE base game too
    print('\n=== AE Base Game stash records ===')
    ae_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\database\database.arz')
    ae_db = ArzDatabase.from_arz(ae_path)

    for name in sorted(ae_db.record_names()):
        nl = name.lower()
        if 'stash' in nl or ('caravan' in nl and 'record' not in nl):
            print(f'  {name}')

    print('\n=== AE numberOfSacks fields ===')
    for name in ae_db.record_names():
        fields = ae_db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'numberofsack' in rk.lower() or 'sackwidth' in rk.lower() or 'sackheight' in rk.lower():
                vals = [str(v) for v in tf.values if v is not None]
                if vals:
                    print(f'  {name} -> {rk} = {vals}')


if __name__ == '__main__':
    main()
