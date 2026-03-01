"""Dump all fields from stash-related records."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def dump_record(db, name, label=''):
    fields = db.get_fields(name)
    if not fields:
        print(f'{label or name}: NOT FOUND')
        return
    print(f'\n=== {label or name} ===')
    for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
        rk = key.split('###')[0]
        vals = tf.values
        if vals and any(v is not None and str(v) for v in vals):
            vstr = ', '.join(str(v) for v in vals)
            if len(vstr) > 120:
                vstr = vstr[:120] + '...'
            print(f'  {rk} = {vstr}')


def main():
    # Check AE base game stash settings
    ae_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\database\database.arz')
    print('Loading AE base game...')
    ae = ArzDatabase.from_arz(ae_path)

    dump_record(ae, 'records\\xpack\\ui\\caravan\\stashinventory.dbr', 'AE Stash Inventory')
    dump_record(ae, 'records\\xpack\\ui\\caravan\\stashwindow.dbr', 'AE Stash Window')

    # Check for transfer stash config in game engine
    for name in ae.record_names():
        nl = name.lower()
        if 'gameengine' in nl and not 'copy' in nl and not 'xxx' in nl and not 'backup' in nl:
            fields = ae.get_fields(name)
            if fields:
                stash_fields = {}
                for key, tf in fields.items():
                    rk = key.split('###')[0].lower()
                    if any(kw in rk for kw in ['transfer', 'stash', 'caravan', 'sack']):
                        stash_fields[key.split('###')[0]] = tf.values
                if stash_fields:
                    print(f'\n=== {name} (stash fields) ===')
                    for k, v in sorted(stash_fields.items()):
                        print(f'  {k} = {v}')

    # Now check our SV mod
    sv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if sv_path:
        print('\n\nLoading SV mod...')
        sv = ArzDatabase.from_arz(sv_path)

        # Check if SV has stash records
        for name in sv.record_names():
            nl = name.lower()
            if 'caravan' in nl and 'stash' in nl:
                dump_record(sv, name, f'SV: {name}')

        # Check SV game engine for stash settings
        for name in sv.record_names():
            nl = name.lower()
            if 'gameengine' in nl and 'copy' not in nl and 'xxx' not in nl and 'backup' not in nl:
                fields = sv.get_fields(name)
                if fields:
                    stash_fields = {}
                    for key, tf in fields.items():
                        rk = key.split('###')[0].lower()
                        if any(kw in rk for kw in ['transfer', 'stash', 'caravan', 'numberofsack']):
                            stash_fields[key.split('###')[0]] = tf.values
                    if stash_fields:
                        print(f'\n=== SV: {name} (stash fields) ===')
                        for k, v in sorted(stash_fields.items()):
                            print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
