"""G1 Dream-panel probe (LANE B, read-only): the Dream mastery (slot 10) uses the
xpack UI folder 'mastery 9'; fix_mastery_panel_buttons only handles ingameui 1-8,
so Summon Copy's button must be registered into the Dream panectrl(s) by the
graft. Dump every panectrl that drives Dream + its tabSkillButtons + BasePane.

Usage: py tools/debug/g1_dreampanel_probe.py [our_arz]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def main():
    our = ArzDatabase.from_arz(Path(OUR))
    m = {norm(n): n for n in our.record_names()}
    cands = [
        r'records\xpack\ui\skills\mastery 9\panectrl.dbr',
        r'records\xpack3\ui\skills\mastery 9\panectrl.dbr',
        r'records\ingameui\player skills\mastery 9\panectrl.dbr',
        r'records\xpack\ui\skills\mastery 9\skill01.dbr',
        r'records\xpack3\ui\skills\mastery 9\skill01.dbr',
    ]
    for c in cands:
        n = m.get(norm(c))
        print(f"\n=== {c}  ({'FOUND' if n else 'absent'})")
        if not n:
            continue
        btns = our.get_field_value(n, 'tabSkillButtons')
        bp = our.get_field_value(n, 'BasePane')
        print(f"   BasePane = {bp}")
        if isinstance(btns, list):
            print(f"   tabSkillButtons: {len(btns)} entries")
            for b in btns:
                print(f"      {b}")
        else:
            print(f"   tabSkillButtons = {btns}")
            # non-panectrl: show templateName
            print(f"   templateName = {our.get_field_value(n, 'templateName')}")


if __name__ == '__main__':
    main()
