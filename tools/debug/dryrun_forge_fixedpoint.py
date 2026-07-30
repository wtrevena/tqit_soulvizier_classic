"""dryrun_forge_fixedpoint.py - prove the XP-forge wiring reaches a FIXED POINT
in memory (no 25-minute build round trip needed to test it).

Wires the formulas on an in-memory copy of a built arz, then runs the gate. The
gate independently re-derives the assignment, so a non-fixed-point classifier
reds with I5 - which is exactly how the first real build caught it.

Usage: py tools/debug/dryrun_forge_fixedpoint.py <built.arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import soul_act_classifier as sac


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    added, unresolved, stats = sac.wire_souls_into_xp_formulas(db)
    problems = sac.verify_xp_formula_membership(db)
    print("\nadded=%d unresolved=%d" % (added, len(unresolved)))
    if problems:
        print("GATE RED (%d):" % len(problems))
        for p in problems[:10]:
            print("   ", p)
        return 1
    print("GATE GREEN: the wiring is a fixed point and every invariant holds.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
