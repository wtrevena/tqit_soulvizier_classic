"""Check what scale lootFinger2Chance and other loot chances use in AE base game."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    ae_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\database\database.arz')
    print('Loading AE base...')
    ae = ArzDatabase.from_arz(ae_path)

    # Check the 4 AE records that use lootFinger2
    print('\n=== AE lootFinger2 records (full loot fields) ===')
    for name in ae.record_names():
        fields = ae.get_fields(name)
        if not fields:
            continue
        has_f2 = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'lootFinger2Item1' and tf.values and tf.values[0]:
                has_f2 = True
                break
        if has_f2:
            print(f'\n  {name}:')
            for key, tf in sorted(fields.items(), key=lambda x: x[0]):
                rk = key.split('###')[0]
                if 'loot' in rk.lower() and 'chance' in rk.lower():
                    print(f'    {rk} (dtype={tf.dtype}): {tf.values}')
                elif 'lootfinger2' in rk.lower():
                    vals = [str(v)[:60] for v in tf.values]
                    print(f'    {rk} (dtype={tf.dtype}): {vals}')

    # Also check ALL loot chance fields in AE to see what scale they use
    print('\n=== ALL loot chance values in AE base ===')
    chance_fields = {}
    for name in ae.record_names():
        fields = ae.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'chance' in rk.lower() and 'loot' in rk.lower():
                if tf.values and tf.values[0] is not None:
                    try:
                        val = float(tf.values[0])
                    except (ValueError, TypeError):
                        continue
                    if rk not in chance_fields:
                        chance_fields[rk] = {'min': val, 'max': val, 'count': 0, 'samples': []}
                    chance_fields[rk]['min'] = min(chance_fields[rk]['min'], val)
                    chance_fields[rk]['max'] = max(chance_fields[rk]['max'], val)
                    chance_fields[rk]['count'] += 1
                    if len(chance_fields[rk]['samples']) < 5:
                        chance_fields[rk]['samples'].append(val)

    for field, info in sorted(chance_fields.items()):
        print(f'  {field}: count={info["count"]}, min={info["min"]}, max={info["max"]}, samples={info["samples"]}')

    # Also check SV mod's loot chance fields
    print('\n=== SV mod loot chance values ===')
    sv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if sv_path:
        sv = ArzDatabase.from_arz(sv_path)
        sv_chance_fields = {}
        for name in sv.record_names():
            fields = sv.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if 'chance' in rk.lower() and 'loot' in rk.lower():
                    if tf.values and tf.values[0] is not None:
                        try:
                            val = float(tf.values[0])
                        except (ValueError, TypeError):
                            continue
                        if rk not in sv_chance_fields:
                            sv_chance_fields[rk] = {'min': val, 'max': val, 'count': 0, 'samples': []}
                        sv_chance_fields[rk]['min'] = min(sv_chance_fields[rk]['min'], val)
                        sv_chance_fields[rk]['max'] = max(sv_chance_fields[rk]['max'], val)
                        sv_chance_fields[rk]['count'] += 1
                        if len(sv_chance_fields[rk]['samples']) < 10:
                            sv_chance_fields[rk]['samples'].append(val)

        for field, info in sorted(sv_chance_fields.items()):
            print(f'  {field}: count={info["count"]}, min={info["min"]:.4f}, max={info["max"]:.4f}, samples={[round(s,4) for s in info["samples"]]}')


if __name__ == '__main__':
    main()
