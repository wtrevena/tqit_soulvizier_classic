"""Check AE base game mastery definitions and compare with SV mod."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def get_skilltree_fields(db, record_name):
    fields = db.get_fields(record_name)
    if not fields:
        return {}
    result = {}
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if tf.values:
            result[rk] = tf.values if len(tf.values) > 1 else tf.values[0]
    return result


def main():
    ae_path = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\database\database.arz')
    sv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None

    print("Loading AE base game...")
    ae_db = ArzDatabase.from_arz(ae_path)

    # Find skilltree definitions in playerlevels
    print('\n=== AE Skill Trees (from playerlevels or game engine) ===')
    for name in ae_db.record_names():
        nl = name.lower()
        if 'playerlevels' in nl and nl.endswith('.dbr'):
            fields = ae_db.get_fields(name)
            if fields:
                for key, tf in fields.items():
                    rk = key.split('###')[0]
                    if 'skilltree' in rk.lower() or 'mastery' in rk.lower():
                        vals = [str(v) for v in tf.values if v]
                        if vals:
                            print(f'  {rk} = {vals}')

    # Check AE base game mastery skill tree layouts
    print('\n=== AE Base Mastery Layouts ===')
    for m in range(1, 12):
        mastery_rec = f'records\\ingameui\\player skills\\mastery {m}\\mastery.dbr'
        fields = ae_db.get_fields(mastery_rec)
        if fields:
            skill_ref = ''
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if rk == 'skillName' and tf.values:
                    skill_ref = str(tf.values[0])
            print(f'  AE Mastery {m}: {skill_ref}')

        # Also check xpack layout
        xpack_rec = f'records\\xpack\\ui\\skills\\mastery {m}\\mastery.dbr'
        fields2 = ae_db.get_fields(xpack_rec)
        if fields2:
            for key, tf in fields2.items():
                rk = key.split('###')[0]
                if rk == 'skillName' and tf.values:
                    print(f'  AE XPack Mastery {m}: {tf.values[0]}')

    # Compare with SV if provided
    if sv_path:
        print(f'\n=== SV Mod Mastery Layouts ===')
        sv_db = ArzDatabase.from_arz(sv_path)
        for m in range(1, 12):
            mastery_rec = f'records\\ingameui\\player skills\\mastery {m}\\mastery.dbr'
            fields = sv_db.get_fields(mastery_rec)
            if fields:
                skill_ref = ''
                for key, tf in fields.items():
                    rk = key.split('###')[0]
                    if rk == 'skillName' and tf.values:
                        skill_ref = str(tf.values[0])
                print(f'  SV Mastery {m}: {skill_ref}')

        # Check if AE mastery order matches SV
        print('\n=== Mastery Order Comparison ===')
        for m in range(1, 12):
            ae_rec = f'records\\ingameui\\player skills\\mastery {m}\\mastery.dbr'
            ae_fields = ae_db.get_fields(ae_rec)
            sv_fields = sv_db.get_fields(ae_rec)

            ae_skill = ''
            sv_skill = ''
            if ae_fields:
                for key, tf in ae_fields.items():
                    if key.split('###')[0] == 'skillName' and tf.values:
                        ae_skill = str(tf.values[0]).split('\\')[-1]
            if sv_fields:
                for key, tf in sv_fields.items():
                    if key.split('###')[0] == 'skillName' and tf.values:
                        sv_skill = str(tf.values[0]).split('\\')[-1]

            if ae_skill or sv_skill:
                match = 'MATCH' if ae_skill.lower() == sv_skill.lower() else 'MISMATCH'
                print(f'  Mastery {m}: AE={ae_skill or "N/A"} SV={sv_skill or "N/A"} [{match}]')


if __name__ == '__main__':
    main()
