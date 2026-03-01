"""Check if the rest skill is properly wired in our deployed database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    records_to_check = [
        'records\\quests\\rewards\\drxrest_skill.dbr',
        'records\\quests\\rewards\\drxrest_skillbuff.dbr',
        'records\\quests\\rewards\\questrewardskilltree.dbr',
        'records\\drxeffects\\other\\rest_running_fxpak.dbr',
        'records\\drxeffects\\other\\rest_running_fx.dbr',
    ]

    for name in records_to_check:
        fields = db.get_fields(name)
        if fields:
            print(f'OK: {name}')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split("###")[0]):
                rk = key.split('###')[0]
                vals = [str(v) for v in tf.values if v is not None]
                if vals and any(v != '0' and v != '0.0' and v != '' for v in vals):
                    vstr = ', '.join(vals)
                    if len(vstr) > 100:
                        vstr = vstr[:100] + '...'
                    print(f'  {rk} = {vstr}')
        else:
            print(f'MISSING: {name}')

    # Check how the skill is granted to player
    print('\n=== How rest skill reaches the player ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'drxrest' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')
                if v and 'questrewardskilltree' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Check if there's a player skill page that includes the rest skill
    print('\n=== Player skill pages referencing rest or questreward ===')
    for name in db.record_names():
        nl = name.lower()
        if 'player' not in nl and 'ingameui' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and ('rest' in str(v).lower() or 'questreward' in str(v).lower()):
                    print(f'  {name} -> {key.split("###")[0]} = {v}')


if __name__ == '__main__':
    main()
