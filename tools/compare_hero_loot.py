"""Compare hero monster records between AE base game and our mod.
Check if loot fields are set correctly and look for any issues."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def dump_loot_fields(db, name, label):
    fields = db.get_fields(name)
    if not fields:
        print(f'  {label}: record NOT FOUND')
        return False

    print(f'  {label}:')
    loot_found = False
    for key, tf in sorted(fields.items(), key=lambda x: x[0]):
        rk = key.split('###')[0]
        if 'loot' in rk.lower() or 'drop' in rk.lower():
            vals = [str(v) for v in tf.values]
            print(f'    {rk} (dtype={tf.dtype}): {vals}')
            loot_found = True
    if not loot_found:
        print(f'    (no loot fields found)')
    return True


def main():
    mod_path = Path(sys.argv[1])
    ae_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\database\database.arz')

    print('Loading mod database...')
    mod = ArzDatabase.from_arz(mod_path)
    print('Loading AE base database...')
    ae = ArzDatabase.from_arz(ae_path)

    # Pick specific early-game hero monsters to compare
    test_heroes = [
        'records\\creature\\monster\\satyr\\um_rassus_15.dbr',
        'records\\creature\\monster\\satyr\\um_petraeus_07.dbr',
        'records\\creature\\monster\\skeleton\\um_hekos_13.dbr',
        'records\\creature\\monster\\harpy\\um_aello_14.dbr',
        'records\\creature\\monster\\boarmonstrous\\um_boarmonstrous_14.dbr',
        'records\\creature\\monster\\maenad\\um_liniashieldbreaker_15.dbr',
        'records\\creature\\monster\\bat\\um_goatsucker_08.dbr',
        'records\\creature\\monster\\eurynomus\\um_nyx_10.dbr',
        'records\\creature\\monster\\arachnos\\um_ishtilnintheye_10.dbr',
        'records\\creature\\monster\\centaur\\um_sergoslongstride_14.dbr',
    ]

    for hero in test_heroes:
        print(f'\n--- {hero.split(chr(92))[-1]} ---')
        dump_loot_fields(ae, hero, 'AE Base')
        dump_loot_fields(mod, hero, 'SV Mod')

    # Check the FULL loot mechanism - what other loot slots exist?
    print(f'\n\n=== Full loot slot analysis (mod) ===')
    loot_slot_usage = {}
    for name in mod.record_names():
        fields = mod.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk.startswith('lootFinger') and 'Item' in rk:
                if tf.values and any(v and str(v).strip() for v in tf.values):
                    loot_slot_usage[rk] = loot_slot_usage.get(rk, 0) + 1

    for slot, count in sorted(loot_slot_usage.items()):
        print(f'  {slot}: used by {count} records')

    # Check if lootFinger2 has any special handling in AE
    print(f'\n=== AE base game lootFinger2 usage ===')
    ae_finger2_usage = 0
    ae_finger2_samples = []
    for name in ae.record_names():
        fields = ae.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'lootFinger2Item1' and tf.values and tf.values[0]:
                ae_finger2_usage += 1
                if len(ae_finger2_samples) < 5:
                    ae_finger2_samples.append((name, str(tf.values[0])))
    print(f'  Records using lootFinger2Item1: {ae_finger2_usage}')
    for name, item in ae_finger2_samples:
        print(f'    {name} -> {item}')


if __name__ == '__main__':
    main()
