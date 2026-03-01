"""Search the AE base game database for inventorysack references and tutorial chests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find ALL references to inventorysack in AE base
    print('=== AE base: inventorysack references ===')
    for name in sorted(db.record_names()):
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'inventorysack' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Find tutorial chest / starting area chests
    print('\n=== Tutorial/starting chests ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if ('tutorial' in nl or 'starting' in nl) and ('chest' in nl or 'potion' in nl or 'loot' in nl or 'proxy' in nl):
            print(f'  {name}')
            fields = db.get_fields(name)
            if fields:
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                        print(f'    {rk} = {str(tf.values)[:200]}')

    # Find Q01 reward records (first main quest)
    print('\n=== Q01 quest rewards ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'reward' in nl and ('q01' in nl or 'q_01' in nl):
            print(f'  {name}')
            fields = db.get_fields(name)
            if fields:
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                        print(f'    {rk} = {str(tf.values)[:200]}')

    # Find JG01 (first journal/side quest) reward records
    print('\n=== JG01 shepherd reward records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'jg01' in nl and 'reward' in nl:
            print(f'  {name}')
            fields = db.get_fields(name)
            if fields:
                for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                    rk = key.split('###')[0]
                    if tf.values and any(v is not None and str(v).strip() for v in tf.values):
                        print(f'    {rk} = {str(tf.values)[:200]}')


if __name__ == '__main__':
    main()
