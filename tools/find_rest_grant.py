"""Find exactly how v0.4 granted the Rest skill to players.
Search for quest tokens, auto-grant mechanisms, etc."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find ALL references to drxrest or Rest skill
    print('=== All references to drxrest ===')
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                vs = str(v).lower()
                if 'drxrest' in vs or 'rest_skill' in vs:
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Find quest tokens that grant skills
    print('\n=== Quest tokens / skill grants ===')
    for name in db.record_names():
        nl = name.lower()
        if 'token' not in nl and 'grant' not in nl and 'reward' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0].lower()
            if 'skill' in rk and tf.values:
                for v in tf.values:
                    if v and 'rest' in str(v).lower():
                        print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Check if there's an auto-start quest
    print('\n=== Quests referencing rest ===')
    for name in db.record_names():
        nl = name.lower()
        if 'quest' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if v and 'rest' in str(v).lower() and 'drx' in str(v).lower():
                    print(f'  {name} -> {key.split("###")[0]} = {v}')

    # Check quest reward tokens that use skillName fields
    print('\n=== Quest reward records with skillName ===')
    for name in db.record_names():
        nl = name.lower()
        if 'reward' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        has_skill = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'skillname' in rk.lower() or 'skilltree' in rk.lower():
                if tf.values and tf.values[0]:
                    print(f'  {name} -> {rk} = {tf.values[0]}')
                    has_skill = True

    # Check for any starting/tutorial quests
    print('\n=== Tutorial/starting quests ===')
    for name in db.record_names():
        nl = name.lower()
        if ('tutorial' in nl or 'start' in nl or 'intro' in nl) and 'quest' in nl:
            fields = db.get_fields(name)
            if fields:
                print(f'  {name}')
                for key, tf in fields.items():
                    rk = key.split('###')[0]
                    if tf.values and any(v and str(v).strip() for v in tf.values):
                        if 'skill' in rk.lower() or 'reward' in rk.lower() or 'token' in rk.lower():
                            print(f'    {rk} = {tf.values}')

    # Check for gameengine default skill settings
    print('\n=== Game engine skill settings ===')
    for name in db.record_names():
        nl = name.lower()
        if 'gameengine' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if 'skill' in rk.lower() and tf.values:
                vals = [str(v) for v in tf.values if v is not None and str(v).strip()]
                if vals:
                    print(f'  {name} -> {rk} = {", ".join(vals)[:120]}')


if __name__ == '__main__':
    main()
