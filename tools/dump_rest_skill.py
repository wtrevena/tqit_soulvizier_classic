"""Dump complete rest skill records from v0.4 database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def dump_record(db, name):
    fields = db.get_fields(name)
    if not fields:
        print(f'{name}: NOT FOUND')
        return
    print(f'\n=== {name} ===')
    rec_type = db._record_types.get(name, 'unknown')
    print(f'  templateName/record_type: {rec_type}')
    for key, tf in sorted(fields.items(), key=lambda x: x[0].split("###")[0]):
        rk = key.split('###')[0]
        vals = [str(v) for v in tf.values if v is not None]
        if vals:
            vstr = ', '.join(vals)
            print(f'  {rk} (dtype={tf.dtype}): {vstr}')


def main():
    db_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(db_path)

    rest_records = [
        'records\\quests\\rewards\\drxrest_skill.dbr',
        'records\\quests\\rewards\\drxrest_skillbuff.dbr',
    ]

    for name in rest_records:
        dump_record(db, name)

    # Also check for related effects/FX
    related = [
        'records\\drxeffects\\other\\rest_running_fx.dbr',
        'records\\drxeffects\\other\\rest_running_fxpak.dbr',
    ]
    for name in related:
        dump_record(db, name)

    # Check how it's granted to players - search for references to drxrest
    print('\n\n=== Records referencing drxrest ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'drxrest' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Check if it exists in 0.98i too
    sv098_path = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz')
    if sv098_path.exists():
        print('\n\n=== Checking 0.98i for rest skill ===')
        db98 = ArzDatabase.from_arz(sv098_path)
        for name in rest_records:
            fields = db98.get_fields(name)
            if fields:
                print(f'  {name}: EXISTS in 0.98i')
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split("###")[0]):
                    rk = key.split('###')[0]
                    vals = [str(v) for v in tf.values if v is not None]
                    if vals:
                        print(f'    {rk} (dtype={tf.dtype}): {", ".join(vals)}')
            else:
                print(f'  {name}: NOT in 0.98i')


if __name__ == '__main__':
    main()
