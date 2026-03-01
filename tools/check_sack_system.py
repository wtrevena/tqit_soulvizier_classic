"""Deep dive into inventory sack/bag system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Dump the inventory sack item
    print('=== inventorysack.dbr ===')
    for name in db.record_names():
        if 'inventorysack' in name.lower() and name.lower().endswith('.dbr'):
            fields = db.get_fields(name)
            if fields:
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    print(f'  {rk} = {tf.values}')

    # Check game engine for inventory/sack settings
    print('\n=== Game engine inventory/sack settings ===')
    for name in db.record_names():
        nl = name.lower()
        if 'gameengine' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if any(kw in rk for kw in ['sack', 'bag', 'inventory', 'stash', 'numtab',
                                        'equipmentctrl', 'playerinv', 'additionalinv']):
                print(f'  {name} -> {key.split("###")[0]} = {tf.values}')

    # Check for any record that has "additionalInventory" or "numberOfSacks"
    print('\n=== Fields with sack/additional inventory keywords ===')
    found = 0
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if any(kw in rk for kw in ['numsack', 'sackprice', 'sackcost', 'maxsack',
                                        'additionalsack', 'inventorysack',
                                        'inventorycost', 'inventoryheight',
                                        'numberofbag', 'maxbag']):
                if tf.values and any(v for v in tf.values if v is not None):
                    print(f'  {name} -> {key.split("###")[0]} = {tf.values}')
                    found += 1
            if found > 50:
                break
        if found > 50:
            break

    # Check the player character for ALL fields (looking for anything inventory-related)
    print('\n=== ALL player char fields with size/count/cost/num ===')
    for name in db.record_names():
        nl = name.lower()
        if 'malepc01' in nl and 'xpack' in nl and nl.endswith('.dbr') and 'old_' not in nl and 'anm_' not in nl:
            fields = db.get_fields(name)
            if not fields:
                continue
            print(f'  {name}:')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                rl = rk.lower()
                if any(kw in rl for kw in ['cost', 'num', 'max', 'count', 'size',
                                             'gold', 'start', 'initial', 'default']):
                    print(f'    {rk} = {tf.values}')
            break

    # Look at AE base game's stash window for comparison
    print('\n=== Stash window record ===')
    for name in db.record_names():
        if 'stashwindow' in name.lower():
            fields = db.get_fields(name)
            if fields:
                print(f'  {name}:')
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    print(f'    {rk} = {tf.values}')


if __name__ == '__main__':
    main()
