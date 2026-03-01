"""Check merchant inventory structure and find early-game merchants."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find the first merchant (Helos area) and dump structure
    print('=== Early-game merchant records ===')
    merchants = []
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'merchant' in nl and ('helos' in nl or 'sparta' in nl or 'megara' in nl or 'greece' in nl):
            merchants.append(name)
            if len(merchants) <= 5:
                print(f'  {name}')

    # Dump a sample merchant to see inventory fields
    print('\n=== Sample merchant fields ===')
    for name in db.record_names():
        nl = name.lower()
        if 'merchant' in nl and 'helos' in nl and nl.endswith('.dbr'):
            fields = db.get_fields(name)
            if not fields:
                continue
            cls = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'Class' and tf.values:
                    cls = str(tf.values[0])
            if 'merchant' not in cls.lower() and 'npc' not in cls.lower():
                continue
            print(f'  {name} (Class={cls}):')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 150:
                        vstr = vstr[:150] + '...'
                    print(f'    {rk} = {vstr}')
            break

    # Search for ALL merchants with dialogue reference
    print('\n=== Merchant dialog records referencing items ===')
    count = 0
    for name in db.record_names():
        nl = name.lower()
        if 'dialog' not in nl or 'merchant' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if 'merchanttable' in rk or 'merchantinv' in rk or 'merchantitem' in rk:
                print(f'  {name} -> {key.split("###")[0]} = {tf.values}')
                count += 1
        if count > 10:
            break

    # Find general goods merchants
    print('\n=== Records with merchantTable field ===')
    count = 0
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk.lower() == 'merchanttable' and tf.values and tf.values[0]:
                print(f'  {name} -> {rk} = {tf.values[0]}')
                count += 1
        if count > 15:
            break

    # Check if there's a general goods merchant table we can add sacks to
    print('\n=== Merchant table records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'merchanttable' in nl and nl.endswith('.dbr'):
            print(f'  {name}')


if __name__ == '__main__':
    main()
