"""Check mastery skill tree format to understand how to add Rest skill."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find DRX mastery skill trees
    trees = [
        'Records\\Skills\\Warfare\\DRXWarfareSkillTree.dbr',
        'Records\\Skills\\Hunting\\DRXHuntingSkillTree.dbr',
    ]

    for tree_path in trees:
        # Case-insensitive search
        found = None
        for name in db.record_names():
            if name.lower() == tree_path.lower():
                found = name
                break

        if not found:
            print(f'NOT FOUND: {tree_path}')
            continue

        fields = db.get_fields(found)
        if not fields:
            print(f'EMPTY: {found}')
            continue

        print(f'\n=== {found} ===')
        # Find all skillName fields and the highest index
        skill_fields = {}
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk.startswith('skillName') and tf.values and tf.values[0]:
                idx = rk.replace('skillName', '')
                skill_fields[int(idx)] = str(tf.values[0])
                print(f'  {rk} = {tf.values[0]}')

        print(f'  Total skills: {len(skill_fields)}')
        if skill_fields:
            print(f'  Max index: {max(skill_fields.keys())}')

        # Also show template
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'templateName' or rk == 'Class':
                print(f'  {rk} = {tf.values[0]}')

    # List all DRX skill trees
    print('\n=== All DRX Mastery Skill Trees ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'drx' in nl and 'skilltree' in nl and '.dbr' in nl:
            if any(m in nl for m in ['warfare', 'defensive', 'earth', 'storm',
                                       'stealth', 'hunting', 'nature', 'spirit',
                                       'dream', 'occult']):
                print(f'  {name}')


if __name__ == '__main__':
    main()
