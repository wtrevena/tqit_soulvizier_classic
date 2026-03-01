"""Find which quests give inventory sacks and what the first quest is."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    sack_path = 'inventorysack'

    # Find ALL references to inventorysack
    print('=== All references to inventorysack ===')
    for name in sorted(db.record_names()):
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and sack_path in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Find quest reward records that use "Give Player Item"
    print('\n=== Quest rewards with givePlayerItem ===')
    for name in sorted(db.record_names()):
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if 'giveplayeritem' in rk or 'playeritem' in rk:
                if tf.values and any(v for v in tf.values if v):
                    print(f'  {name} -> {key.split("###")[0]} = {tf.values}')

    # Find the first quest (Helos area)
    print('\n=== Early quests (Greece/Helos) ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'quest' in nl and ('helos' in nl or 'q01' in nl or 'jg01' in nl or 'first' in nl):
            if nl.endswith('.dbr'):
                print(f'  {name}')

    # Find quest volume/trigger records
    print('\n=== Quest trigger/volume records (first area) ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'quest' in nl and ('reward' in nl or 'complete' in nl) and 'greece' in nl:
            if nl.endswith('.dbr'):
                print(f'  {name}')

    # Check for "talk to" or first NPC quest actions
    print('\n=== Quest location/action records for early game ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'questlocations' in nl and 'greece' in nl and ('q01' in nl or 'jg01' in nl or 'guard' in nl or 'satyr' in nl or 'start' in nl):
            print(f'  {name}')
            fields = db.get_fields(name)
            if fields:
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                        vstr = str(tf.values)
                        if len(vstr) > 200:
                            vstr = vstr[:200] + '...'
                        print(f'    {rk} = {vstr}')


if __name__ == '__main__':
    main()
