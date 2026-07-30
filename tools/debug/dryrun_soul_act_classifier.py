"""dryrun_soul_act_classifier.py - R-100 #11 coverage report before building.

Usage: py tools/debug/dryrun_soul_act_classifier.py <built.arz> [--unresolved]
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import soul_act_classifier as sac


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    act_of, formulas = sac.read_formula_membership(db)
    print("formulas present: %d  already-listed soul paths: %d"
          % (len(formulas), len(act_of)))
    assignments, unresolved, stats = sac.classify_soul_acts(db)
    print("\nSIGNALS:")
    for k, v in sorted(stats.items()):
        print("   %-24s %d" % (k, v))
    print("\nNEWLY ASSIGNED: %d" % len(assignments))
    per = Counter()
    svc = Counter()
    for s, (act, sig) in assignments.items():
        per[(sac.soul_tier(s), act)] += 1
        if 'svc_uber' in s.lower():
            svc[(act, sig)] += 1
    for k in sorted(per):
        print("   tier=%s act=%d : %d" % (k[0], k[1], per[k]))
    print("\n  of which svc_uber (OUR minted uber souls): %d" % sum(svc.values()))
    for k, v in sorted(svc.items()):
        print("     act=%d via %-22s %d" % (k[0], k[1], v))
    print("\nUNRESOLVED: %d" % len(unresolved))
    for r, n in Counter(r for _s, r in unresolved).most_common():
        print("   %-42s %d" % (r, n))
    folders = Counter('\\'.join(s.lower().split('\\')[:5]) for s, _r in unresolved)
    print("\n  unresolved by folder:")
    for k, v in folders.most_common(12):
        print("     %5d  %s" % (v, k))
    if '--unresolved' in argv:
        for s, r in sorted(unresolved):
            print("      %-70s %s" % (s, r))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
