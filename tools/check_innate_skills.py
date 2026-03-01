"""Check how innate skills (Taunt, Basic Attack, Pet Attack) are granted
to the player, so we can grant Rest the same way."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Check player character records
    player_records = []
    for name in db.record_names():
        nl = name.lower()
        if ('malepc' in nl or 'femalepc' in nl) and 'creature' in nl:
            player_records.append(name)

    for name in sorted(player_records):
        fields = db.get_fields(name)
        if not fields:
            continue
        print(f'\n=== {name} ===')
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split("###")[0]):
            rk = key.split('###')[0]
            if any(kw in rk.lower() for kw in ['skill', 'default', 'innate', 'autocast']):
                vals = [str(v) for v in tf.values if v is not None]
                if vals and any(v != '0' and v != '0.0' and v != '' for v in vals):
                    vstr = ', '.join(vals)
                    if len(vstr) > 120:
                        vstr = vstr[:120] + '...'
                    print(f'  {rk} = {vstr}')

    # Also check the AE base game for comparison
    ae_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\database\database.arz')
    ae = ArzDatabase.from_arz(ae_path)

    print('\n\n=== AE Base Player Records ===')
    for name in ae.record_names():
        nl = name.lower()
        if ('malepc' in nl or 'femalepc' in nl) and 'creature' in nl and 'old' not in nl:
            fields = ae.get_fields(name)
            if not fields:
                continue
            print(f'\n--- {name} ---')
            for key, tf in sorted(fields.items(), key=lambda x: x[0].split("###")[0]):
                rk = key.split('###')[0]
                if any(kw in rk.lower() for kw in ['skill', 'default']):
                    vals = [str(v) for v in tf.values if v is not None]
                    if vals and any(v != '0' and v != '0.0' and v != '' for v in vals):
                        vstr = ', '.join(vals)
                        if len(vstr) > 120:
                            vstr = vstr[:120] + '...'
                        print(f'  {rk} = {vstr}')


if __name__ == '__main__':
    main()
