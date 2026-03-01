"""Deep debug: check if lootFinger2 actually works in AE.
Compare our mod's hero monsters with AE base game's loot system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def dump_loot_fields(db, name, label):
    """Dump ALL loot-related fields for a monster."""
    fields = db.get_fields(name)
    if not fields:
        return
    print(f'  {label}: {name.split(chr(92))[-1]}')
    for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
        rk = key.split('###')[0]
        rl = rk.lower()
        if any(kw in rl for kw in ['loot', 'drop', 'chest', 'finger', 'misc']):
            if tf.values and any(v is not None and str(v).strip() and str(v) != '0' and str(v) != '0.0' for v in tf.values):
                print(f'    {rk} = {tf.values}')


def main():
    mod_path = Path(sys.argv[1])
    ae_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    mod_db = ArzDatabase.from_arz(mod_path)

    # Check a few specific hero monsters from the mod
    print('=== Mod: Hero monster loot fields ===')
    targets = []
    for name in mod_db.record_names():
        nl = name.lower()
        fn = nl.split('\\')[-1]
        if fn.startswith('hero_') and '\\creature' in nl and fn.endswith('.dbr'):
            targets.append(name)
        if fn.startswith('champion_') and '\\creature' in nl and fn.endswith('.dbr'):
            targets.append(name)
    for t in sorted(targets)[:8]:
        dump_loot_fields(mod_db, t, 'MOD')

    # Check if ANY field references the soul item paths
    print('\n=== Mod: How are souls referenced on monsters? ===')
    soul_fields = set()
    for name in mod_db.record_names():
        nl = name.lower()
        if '\\creature' not in nl:
            continue
        fields = mod_db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'soul' in str(v).lower() and 'equipmentring' in str(v).lower():
                    rk = key.split('###')[0]
                    soul_fields.add(rk)
    print(f'  Fields that reference soul items: {sorted(soul_fields)}')

    # Check what the AE base game uses for monster drops
    if ae_path:
        ae_db = ArzDatabase.from_arz(ae_path)

        print('\n=== AE base: lootFinger2 usage ===')
        finger2_count = 0
        for name in ae_db.record_names():
            nl = name.lower()
            if '\\creature' not in nl:
                continue
            val = ae_db.get_field_value(name, 'lootFinger2Item1')
            if val and val != '' and val != 0:
                finger2_count += 1
                if finger2_count <= 5:
                    dump_loot_fields(ae_db, name, 'AE')
        print(f'  Total monsters with lootFinger2Item1: {finger2_count}')

        # Check what loot fields AE hero monsters use
        print('\n=== AE base: Hero monster loot fields ===')
        count = 0
        for name in ae_db.record_names():
            nl = name.lower()
            if '\\creature' not in nl:
                continue
            fields = ae_db.get_fields(name)
            if not fields:
                continue
            classification = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'monsterClassification' and tf.values:
                    classification = str(tf.values[0])
            if classification == 'Hero':
                dump_loot_fields(ae_db, name, 'AE Hero')
                count += 1
                if count >= 5:
                    break

        # Check what chanceToEquipFinger2 looks like
        print('\n=== AE base: chanceToEquipFinger2 on heroes ===')
        count = 0
        for name in ae_db.record_names():
            nl = name.lower()
            if '\\creature' not in nl:
                continue
            fields = ae_db.get_fields(name)
            if not fields:
                continue
            has_equip_finger2 = False
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if 'chanceToEquipFinger2' == rk and tf.values:
                    ch = float(tf.values[0]) if tf.values[0] else 0
                    if ch > 0:
                        has_equip_finger2 = True
            if has_equip_finger2:
                print(f'  {name.split(chr(92))[-1]}:')
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    if 'finger2' in rk.lower():
                        if tf.values and any(v is not None and str(v).strip() and str(v) != '0' for v in tf.values):
                            print(f'    {rk} = {tf.values}')
                count += 1
                if count >= 5:
                    break


if __name__ == '__main__':
    main()
