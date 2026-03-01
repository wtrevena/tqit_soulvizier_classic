"""Check icon bitmap references for all Hunting mastery skills."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def find_icase(db, ref):
    ref_lower = ref.lower().replace('/', '\\')
    for name in db.record_names():
        if name.lower().replace('/', '\\') == ref_lower:
            return name
    return None


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Check ALL masteries for skills with missing bitmaps
    for m in range(1, 9):
        print(f'\n=== Mastery {m} - Icon Bitmaps ===')
        for i in range(1, 25):
            layout_rec = f'records\\ingameui\\player skills\\mastery {m}\\skill{i:02d}.dbr'
            lf = db.get_fields(layout_rec)
            if not lf:
                continue

            skill_ref = ''
            for key, tf in lf.items():
                if key.split('###')[0] == 'skillName' and tf.values:
                    skill_ref = str(tf.values[0])

            actual = find_icase(db, skill_ref)
            if not actual:
                continue

            sf = db.get_fields(actual)
            if not sf:
                continue

            up_bitmap = ''
            down_bitmap = ''
            for key, tf in sf.items():
                rk = key.split('###')[0]
                if rk == 'skillUpBitmapName' and tf.values:
                    up_bitmap = str(tf.values[0])
                elif rk == 'skillDownBitmapName' and tf.values:
                    down_bitmap = str(tf.values[0])

            short = skill_ref.split('\\')[-1]
            if not up_bitmap and not down_bitmap:
                print(f'  skill{i:02d}: {short:50s} NO ICONS')
            else:
                up_short = up_bitmap.split('\\')[-1] if up_bitmap else 'NONE'
                print(f'  skill{i:02d}: {short:50s} icon={up_short}')

    # Show mastery 6 only, with full details including which textures are in the resource arcs
    print('\n\n=== Mastery 6 (Hunting) - Detailed ===')
    no_icon_skills = []
    has_icon_skills = []
    for i in range(1, 25):
        layout_rec = f'records\\ingameui\\player skills\\mastery {m}\\skill{i:02d}.dbr'
        lf = db.get_fields(layout_rec)
        if not lf:
            continue
        skill_ref = ''
        for key, tf in lf.items():
            if key.split('###')[0] == 'skillName' and tf.values:
                skill_ref = str(tf.values[0])
        actual = find_icase(db, skill_ref)
        if not actual:
            continue
        sf = db.get_fields(actual)
        if not sf:
            continue
        up_bitmap = ''
        for key, tf in sf.items():
            if key.split('###')[0] == 'skillUpBitmapName' and tf.values:
                up_bitmap = str(tf.values[0])
        if not up_bitmap:
            no_icon_skills.append(skill_ref.split('\\')[-1])
        else:
            has_icon_skills.append(skill_ref.split('\\')[-1])

    print(f'  Skills WITH icons: {len(has_icon_skills)}')
    print(f'  Skills WITHOUT icons: {len(no_icon_skills)}')
    for s in no_icon_skills:
        print(f'    NO ICON: {s}')


if __name__ == '__main__':
    main()
