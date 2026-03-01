"""Dump player character records and quest reward skill tree fields."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def dump_record(db, name, label):
    fields = db.get_fields(name)
    if not fields:
        print(f'\n=== {label}: NOT FOUND or EMPTY ===')
        return

    print(f'\n=== {label}: {name} ===')
    for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
        rk = key.split('###')[0]
        vals = [str(v) for v in tf.values if v is not None]
        if vals:
            print(f'  {rk} = {", ".join(vals)[:200]}')


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find player character records
    targets = []
    for name in db.record_names():
        nl = name.lower()
        if 'malepc01' in nl or 'femalepc01' in nl:
            targets.append(name)

    for t in sorted(targets):
        dump_record(db, t, 'Player Character')

    # Find quest reward skill tree
    for name in db.record_names():
        nl = name.lower()
        if 'questreward' in nl and 'skilltree' in nl:
            dump_record(db, name, 'Quest Reward Skill Tree')

    # Find all DRX mastery skill trees (just list them)
    print('\n=== All skill tree records ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'skilltree' in nl and nl.endswith('.dbr'):
            fields = db.get_fields(name)
            skill_count = 0
            if fields:
                for key in fields:
                    if key.split('###')[0].startswith('skillName'):
                        skill_count += 1
            print(f'  {name} ({skill_count} skills)')

    # Dump the rest skill buff to verify its fields
    for name in db.record_names():
        if 'drxrest_skillbuff' in name.lower():
            dump_record(db, name, 'Rest Skill Buff')
        if 'drxrest_skill.dbr' in name.lower():
            dump_record(db, name, 'Rest Skill Caster')


if __name__ == '__main__':
    main()
