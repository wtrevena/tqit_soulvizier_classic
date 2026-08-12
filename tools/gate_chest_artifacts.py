r"""gate_chest_artifacts.py - "artifacts should never drop from chests" (Will 2026-08-11).

Standalone twin of the in-build check in `tools/patches/loot_volume_trim.verify()`;
both call `tools/svc_chest_artifacts.problems`, so they cannot disagree.

Usage:
  py tools/gate_chest_artifacts.py <arz>            # audit, exit 1 on any finding
  py tools/gate_chest_artifacts.py <arz> --verbose  # list every reachable artifact
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_chest_artifacts as SCA
import svc_loot_breadth as SLB


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_chest_artifacts.py <arz> [--verbose]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    lk = SLB.Lookup(db)
    print("\n=== chest-artifact audit (Will 2026-08-11) ===")
    if '--verbose' in argv[2:]:
        reach = SCA.reachable_artifacts(db, lk)
        print("equippable artifacts reachable from a mod loot surface: %d" % len(reach))
        for rec in sorted(reach):
            pin = SCA.R185_CRAFT_REAGENT_PIN.get(rec)
            print("  %-64s %d surface(s)%s"
                  % (rec, len(reach[rec]), '  [PINNED: %s]' % pin if pin else ''))
    problems = SCA.problems(db, lk)
    if problems:
        print("\nARTIFACT FINDINGS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        return 1
    print("\nGATE PASS: %s" % SCA.pass_line(db, lk))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
