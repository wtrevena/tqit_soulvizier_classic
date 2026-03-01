"""Diagnose mastery skill tree layouts and identify missing skills/icons."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    if len(sys.argv) < 2:
        print("Usage: diagnose_masteries.py <database.arz>")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Find all mastery tree records
    for m in range(1, 12):
        prefix = f'records\\ingameui\\player skills\\mastery {m}\\'
        records = [n for n in db.record_names() if n.lower().startswith(prefix.lower())]

        if not records:
            continue

        # Get mastery skill reference
        mastery_dbr = prefix + 'mastery.dbr'
        mastery_skill = ''
        mfields = db.get_fields(mastery_dbr)
        if mfields:
            for key, tf in mfields.items():
                rk = key.split('###')[0]
                if rk == 'skillName' and tf.values:
                    mastery_skill = str(tf.values[0])

        print(f'\n=== Mastery {m} ({len(records)} layout records) ===')
        print(f'  Mastery skill: {mastery_skill}')

        # Check if mastery skill exists
        if mastery_skill:
            exists = db.has_record(mastery_skill)
            print(f'  Mastery skill exists: {exists}')

            if exists:
                msf = db.get_fields(mastery_skill)
                if msf:
                    for key, tf in msf.items():
                        rk = key.split('###')[0]
                        if rk == 'skillDisplayName' and tf.values:
                            print(f'  Display name tag: {tf.values[0]}')

        # Check each skill slot
        missing = []
        present = []
        for i in range(1, 30):
            slot_name = f'{prefix}skill{i:02d}.dbr'
            fields = db.get_fields(slot_name)
            if fields is None:
                continue

            skill_ref = ''
            bitmap = ''
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if rk == 'skillName' and tf.values:
                    skill_ref = str(tf.values[0])
                elif rk == 'bitmapName' and tf.values:
                    bitmap = str(tf.values[0])

            if skill_ref:
                exists = db.has_record(skill_ref)
                short = skill_ref.split('\\')[-1]
                if exists:
                    present.append(f'skill{i:02d}: {short}')
                else:
                    missing.append(f'skill{i:02d}: {short} (MISSING)')

        print(f'  Skills present: {len(present)}')
        for s in present:
            print(f'    {s}')
        if missing:
            print(f'  Skills MISSING: {len(missing)}')
            for s in missing:
                print(f'    {s}')

    # Also check AE base game mastery order
    print('\n=== Mastery Class Records (skill_mastery*.dbr) ===')
    mastery_skills = []
    for name in db.record_names():
        nl = name.lower()
        if 'skill_mastery' in nl and nl.endswith('.dbr'):
            fields = db.get_fields(name)
            display = ''
            if fields:
                for key, tf in fields.items():
                    rk = key.split('###')[0]
                    if rk == 'skillDisplayName' and tf.values:
                        display = str(tf.values[0])
            print(f'  {name} -> {display}')

    # Check xpack mastery layouts too
    print('\n=== XPack UI Skill Layouts ===')
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'xpack' in nl and 'ui' in nl and 'skills' in nl and 'mastery' in nl:
            print(f'  {name}')


if __name__ == '__main__':
    main()
