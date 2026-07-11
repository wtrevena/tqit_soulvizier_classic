r"""build36 Lane A round-2 probe: dump the Runemaster (mastery 10) skill-panel
controller(s) + skill-button records across DLC scopes, in the BASE game arz and
optionally the built mod arz. Answers: which panectrl is authoritative, what its
tabSkillButtons list is, and whether skill23 (the Rune Golem button) is in it.

usage: py tools/debug/rg_panel_probe.py <arz> [<arz2> ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase  # noqa: E402


def norm(s):
    return s.replace('/', '\\').lower()


def fval(db, rec, field):
    ff = db.get_fields(rec) or {}
    for k, tf in ff.items():
        if k.split('###')[0] == field:
            return list(tf.values)
    return None


def dump(arz):
    print("=" * 78)
    print("ARZ:", arz)
    db = ArzDatabase.from_arz(Path(arz))
    names = {norm(n): n for n in db.record_names()}

    # 1) every panectrl in a "mastery 10" folder, any scope
    panes = sorted(real for k, real in names.items()
                   if 'mastery 10' in k and k.endswith('panectrl.dbr'))
    print(f"\n[panectrl records in any 'mastery 10' folder] ({len(panes)})")
    for p in panes:
        btns = fval(db, p, 'tabSkillButtons') or []
        base = fval(db, p, 'BasePane')
        print(f"  {p}")
        print(f"     BasePane={base}")
        print(f"     tabSkillButtons ({len(btns)}):")
        for b in btns:
            print(f"        {b}")

    # 2) skill button records present in each mastery-10 scope
    for scope in ('xpack', 'xpack2', 'xpack3', 'ingameui\\player skills'):
        folder = norm(rf'records\{scope}\ui\skills\mastery 10')
        present = sorted(real for k, real in names.items()
                         if k.startswith(folder + '\\') and 'skill' in k.split('\\')[-1])
        if present:
            print(f"\n[skill-button records under {folder}] ({len(present)})")
            for r in present:
                sk = fval(db, r, 'skillName')
                print(f"     {r.split(chr(92))[-1]:16s} skillName={sk}")

    # 3) explicit skill23 check
    for scope in ('xpack2', 'xpack3', 'xpack'):
        cand = rf'records\{scope}\ui\skills\mastery 10\skill23.dbr'
        print(f"\n  skill23 @ {scope}: {'PRESENT' if norm(cand) in names else 'absent'}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    for a in sys.argv[1:]:
        dump(a)
