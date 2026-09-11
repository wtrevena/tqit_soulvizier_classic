r"""Standalone twin of the R-258 `devourer_soul_delivery` in-build gate.

Runs the SAME `_check` the registry module runs in-build, against any built arz, so
`BL-W0814-10`'s contract can be re-proven on a shipped artifact without a rebuild.

    py tools/gate_devourer_soul_delivery.py [arz]            # gate the arz (exit 1 on any problem)
    py tools/gate_devourer_soul_delivery.py [arz] --dryrun   # load, run apply() IN MEMORY, re-gate

`--dryrun` is the RED->GREEN proof: it asserts the arz you point it at FAILS the
contract (the shipped state - Will's report), applies the module's own `apply()` to
the in-memory db, and asserts the same contract then PASSES. Nothing is written.

ANTI-INERT: against the shipped build101 arz `9712f58fcc1a73ec1fba2d5a9e811cbc` this
gate EXITS 1 and says the Devourer's soul has no guaranteed drop row at all - Will's
report as an artifact fact - so it is not a gate that can only ever be green.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from arz_patcher import ArzDatabase                        # noqa: E402
from patches import devourer_soul_delivery as DSD          # noqa: E402

DEFAULT_ARZ = HERE.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    dryrun = '--dryrun' in argv
    arz = Path(args[0]) if args else DEFAULT_ARZ
    if not arz.exists():
        print("gate_devourer_soul_delivery: arz not found: %s" % arz)
        return 2
    print("gate_devourer_soul_delivery: %s" % arz)
    db = ArzDatabase.from_arz(arz)

    problems = DSD._check(db)
    if dryrun:
        print("  BEFORE apply(): %d problem(s)" % len(problems))
        for p in problems[:12]:
            print("     RED: %s" % p)
        if not problems:
            print("  DRYRUN FAILED: the input arz already satisfies the contract, so "
                  "this run proves nothing about apply(). Point it at the pre-fix arz.")
            return 1
        DSD.apply(db, {})
        problems = DSD._check(db)
        if problems:
            print("  DRYRUN FAILED: apply() did NOT close the contract - %d problem(s) "
                  "left" % len(problems))
            for p in problems[:20]:
                print("     STILL RED: %s" % p)
            return 1
        share = DSD._row_share(db, DSD._resolve(db, DSD._DEVOURER),
                               DSD._SLOT, DSD._SOUL_ROW)
        print("  DRYRUN PASS: RED -> GREEN on the real arz (in memory only, nothing "
              "written); measured soul share after apply() = %.4f%%" % share)
        return 0

    if problems:
        for p in problems[:30]:
            print("  R-258 OFFENDER: %s" % p)
        print("gate_devourer_soul_delivery: FAIL (%d problem(s))" % len(problems))
        return 1
    share = DSD._row_share(db, DSD._resolve(db, DSD._DEVOURER),
                           DSD._SLOT, DSD._SOUL_ROW)
    print("gate_devourer_soul_delivery: PASS - the Devourer's soul drops at a MEASURED "
          "%.4f%% of kills on all three difficulties via %s row %d; Finger2 still "
          "pinned at 100 (R-243)." % (share, DSD._SLOT, DSD._SOUL_ROW))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
