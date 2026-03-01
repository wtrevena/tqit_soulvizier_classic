"""Dump a specific merchant NPC record to understand the inventory system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Check the alchemist merchant
    print('=== Greece Alchemist Merchant ===')
    for name in db.record_names():
        nl = name.lower()
        if '01_greece_alchemist' in nl:
            fields = db.get_fields(name)
            if fields:
                print(f'  {name}:')
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                        vstr = str(tf.values)
                        if len(vstr) > 200:
                            vstr = vstr[:200] + '...'
                        print(f'    {rk} = {vstr}')

    # Find ANY record with "merchantItem" or "stockedItem" type fields
    print('\n=== Records with merchant stocking fields ===')
    stock_fields = set()
    count = 0
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if 'merchant' in rk or 'stock' in rk:
                if tf.values and any(v and str(v).strip() for v in tf.values):
                    stock_fields.add(key.split('###')[0])
                    if count < 30:
                        print(f'  {name} -> {key.split("###")[0]} = {str(tf.values)[:150]}')
                    count += 1

    print(f'\n  Unique merchant/stock field names:')
    for f in sorted(stock_fields):
        print(f'    {f}')

    # Find merchant dialog records and dump them
    print('\n=== Merchant dialog/NPC records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'merchant' in nl and 'dialog' in nl and 'greece' in nl and nl.endswith('.dbr'):
            fields = db.get_fields(name)
            if not fields:
                continue
            cls = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'Class' and tf.values:
                    cls = str(tf.values[0])
            print(f'  {name} (Class={cls}):')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 150:
                        vstr = vstr[:150] + '...'
                    print(f'    {rk} = {vstr}')
            break


if __name__ == '__main__':
    main()
