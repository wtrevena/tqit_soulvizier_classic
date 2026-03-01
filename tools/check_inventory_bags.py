"""Find inventory bag/sack related records and fields in the AE base game."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Search for sack/bag/inventory related records
    print('=== Records with sack/bag in name ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'sack' in nl or ('bag' in nl and 'inventory' in nl):
            print(f'  {name}')

    # Search for player inventory records
    print('\n=== Player inventory records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'inventory' in nl and ('player' in nl or 'character' in nl or 'pc' in nl):
            print(f'  {name}')

    # Search for inventory window / private stash records
    print('\n=== Inventory window records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'inventory' in nl and ('window' in nl or 'private' in nl):
            print(f'  {name}')

    # Look at player character records for inventory-related fields
    print('\n=== Player char inventory fields ===')
    for name in db.record_names():
        nl = name.lower()
        if ('malepc01' in nl or 'femalepc01' in nl) and 'xpack' in nl and nl.endswith('.dbr'):
            if 'old_' in nl or 'anm_' in nl:
                continue
            fields = db.get_fields(name)
            if not fields:
                continue
            print(f'\n  {name}:')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0].lower()
                if any(kw in rk for kw in ['inventory', 'sack', 'bag', 'equip', 'numtab',
                                             'height', 'width', 'cost', 'gold']):
                    print(f'    {key.split("###")[0]} = {tf.values}')

    # Look for records with numSacks, numberOfSacks, etc.
    print('\n=== Records with numberOfSacks/numSacks fields ===')
    count = 0
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if 'numsack' in rk or 'numberofsack' in rk or 'sackcount' in rk:
                print(f'  {name} -> {key.split("###")[0]} = {tf.values}')
                count += 1
                if count > 30:
                    break
        if count > 30:
            break

    # Look for caravan/stash private inventory
    print('\n=== Private stash / caravan records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'caravan' in nl or 'privatestash' in nl or 'private_stash' in nl:
            print(f'  {name}')


if __name__ == '__main__':
    main()
