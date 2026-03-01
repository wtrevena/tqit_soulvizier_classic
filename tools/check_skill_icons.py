"""Check if skill icon bitmaps exist for Hunting mastery skills."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def find_record_icase(db, ref_path):
    """Find a record by case-insensitive path match."""
    ref_lower = ref_path.lower().replace('/', '\\')
    for name in db.record_names():
        if name.lower().replace('/', '\\') == ref_lower:
            return name
    return None


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Check Hunting mastery (slot 6) skill details
    print('=== Hunting Mastery (Slot 6) - Skill Icon Analysis ===\n')

    for i in range(1, 25):
        layout_rec = f'records\\ingameui\\player skills\\mastery 6\\skill{i:02d}.dbr'
        lf = db.get_fields(layout_rec)
        if not lf:
            continue

        skill_ref = ''
        layout_bitmap = ''
        for key, tf in lf.items():
            rk = key.split('###')[0]
            if rk == 'skillName' and tf.values:
                skill_ref = str(tf.values[0])
            elif rk == 'bitmapName' and tf.values:
                layout_bitmap = str(tf.values[0])

        # Find the skill record (case-insensitive)
        actual_rec = find_record_icase(db, skill_ref) if skill_ref else None
        skill_bitmap = ''
        skill_display = ''

        if actual_rec:
            sf = db.get_fields(actual_rec)
            if sf:
                for key, tf in sf.items():
                    rk = key.split('###')[0]
                    if rk == 'skillBaseDescription' and tf.values:
                        skill_bitmap = str(tf.values[0])
                    elif rk == 'bitmapName' and tf.values:
                        skill_bitmap = str(tf.values[0])
                    elif rk == 'skillDisplayName' and tf.values:
                        skill_display = str(tf.values[0])

        short_ref = skill_ref.split('\\')[-1] if skill_ref else 'NONE'
        status = 'EXISTS' if actual_rec else 'MISSING'
        bitmap = layout_bitmap or skill_bitmap or 'NO BITMAP'

        print(f'  skill{i:02d}: {short_ref:50s} [{status}] display={skill_display:30s} bitmap={bitmap}')

    # Also check a few skills from other masteries for comparison
    print('\n=== Sample from Warfare (Slot 1) ===')
    for i in [1, 2, 3, 21]:
        layout_rec = f'records\\ingameui\\player skills\\mastery 1\\skill{i:02d}.dbr'
        lf = db.get_fields(layout_rec)
        if not lf:
            continue
        skill_ref = ''
        for key, tf in lf.items():
            if key.split('###')[0] == 'skillName' and tf.values:
                skill_ref = str(tf.values[0])
        actual_rec = find_record_icase(db, skill_ref) if skill_ref else None
        short = skill_ref.split('\\')[-1] if skill_ref else 'NONE'
        print(f'  skill{i:02d}: {short:50s} [{"EXISTS" if actual_rec else "MISSING"}]')


if __name__ == '__main__':
    main()
