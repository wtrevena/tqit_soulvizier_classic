"""
Diagnose mastery selection UI issues by comparing SV 0.98i records
with base AE records. Identifies which SV records override AE UI.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    sv_path = Path(sys.argv[1])
    db = ArzDatabase.from_arz(sv_path)

    ui_patterns = [
        'select mastery', 'masterypane', 'skilltree',
        'player skills', 'selectmastery',
    ]

    print("=== Mastery-related records in SV 0.98i ===")
    mastery_records = []
    for name in db.record_names():
        nl = name.lower()
        if any(p in nl for p in ui_patterns):
            mastery_records.append(name)

    mastery_records.sort()
    for r in mastery_records:
        fields = db.get_fields(r)
        tmpl = ''
        desc = ''
        if fields:
            for k, tf in fields.items():
                rk = k.split('###')[0]
                if rk == 'templateName' and tf.values:
                    tmpl = str(tf.values[0])
                elif rk == 'FileDescription' and tf.values:
                    desc = str(tf.values[0])
        print(f"  {r}")
        if tmpl:
            print(f"    template: {tmpl}")
        if desc:
            print(f"    desc: {desc}")

    print(f"\nTotal mastery UI records: {len(mastery_records)}")

    print("\n=== Records under ingameui\\player skills\\ ===")
    skill_ui = []
    for name in db.record_names():
        nl = name.lower()
        if 'ingameui\\player skills\\' in nl or 'ingameui/player skills/' in nl:
            skill_ui.append(name)

    skill_ui.sort()
    for r in skill_ui:
        fields = db.get_fields(r)
        tmpl = ''
        if fields:
            for k, tf in fields.items():
                if k.split('###')[0] == 'templateName' and tf.values:
                    tmpl = str(tf.values[0])
        print(f"  {r}  [{tmpl}]")

    print(f"\nTotal player skills UI records: {len(skill_ui)}")

    print("\n=== xpack UI skill records ===")
    xpack_ui = []
    for name in db.record_names():
        nl = name.lower()
        if ('xpack\\ui\\' in nl or 'xpack/ui/' in nl or
            'xpack2\\ui\\' in nl or 'xpack2/ui/' in nl or
            'xpack3\\ui\\' in nl or 'xpack3/ui/' in nl) and 'skill' in nl:
            xpack_ui.append(name)
    xpack_ui.sort()
    for r in xpack_ui:
        fields = db.get_fields(r)
        tmpl = ''
        if fields:
            for k, tf in fields.items():
                if k.split('###')[0] == 'templateName' and tf.values:
                    tmpl = str(tf.values[0])
        print(f"  {r}  [{tmpl}]")

    print(f"\nTotal xpack UI skill records: {len(xpack_ui)}")

    print("\n=== Checking mastery pane panel controls ===")
    for name in db.record_names():
        nl = name.lower()
        if 'masterypane' in nl or ('select mastery' in nl and 'pane' in nl):
            fields = db.get_fields(name)
            if fields:
                print(f"\n  {name}")
                for k, tf in fields.items():
                    rk = k.split('###')[0]
                    print(f"    {rk} = {tf.values}")


if __name__ == '__main__':
    main()
