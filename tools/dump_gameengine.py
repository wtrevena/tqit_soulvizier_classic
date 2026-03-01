"""Dump all game engine fields, looking for sack/bag count settings."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Dump ALL fields from xpack gameengine
    target = 'records\\xpack\\game\\gameengine.dbr'
    for name in db.record_names():
        if name.lower() == target.lower():
            fields = db.get_fields(name)
            print(f'=== {name} ({len(fields)} fields) ===')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                rk = key.split('###')[0]
                rl = rk.lower()
                # Only show fields with actual values
                if tf.values and any(v is not None for v in tf.values):
                    vstr = str(tf.values)
                    if len(vstr) > 200:
                        vstr = vstr[:200] + '...'
                    print(f'  {rk} = {vstr}')
            break

    # Also check what the AE base game looks like
    print('\n\n=== Searching for numDefaultSacks / initialSacks / startingSacks ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if any(kw in rk for kw in ['defaultsack', 'initialsack', 'startsack',
                                        'numsack', 'maxsack', 'sacknum',
                                        'numberofdefault', 'beginningsack']):
                print(f'  {name} -> {key.split("###")[0]} = {tf.values}')

    # Also check for how merchants stock sacks
    print('\n=== Merchants that sell sacks ===')
    for name in db.record_names():
        nl = name.lower()
        if 'merchant' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'inventorysack' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')


if __name__ == '__main__':
    main()
