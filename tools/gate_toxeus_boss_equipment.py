r"""Standalone twin of the R-251 `toxeus_boss_equipment` in-build gate.

Runs the SAME `_check` / `_check_modwide` the registry module runs in-build, against any
built arz, so the contract can be re-proven on a shipped artifact without a rebuild.

    py tools/gate_toxeus_boss_equipment.py [arz]          # gate the arz (exit 1 on any problem)
    py tools/gate_toxeus_boss_equipment.py [arz] --dryrun  # load, run apply() IN MEMORY, re-gate

`--dryrun` is the RED->GREEN proof: it asserts the arz you point it at FAILS the contract
(the shipped state - Will's three bugs), applies the module's own `apply()` to the
in-memory db, and asserts the same contract then PASSES. Nothing is ever written to disk.

ANTI-INERT: against the shipped build91/92 arz `b888f022` this gate EXITS 1 and names the
Devourer's bow rows and the Hunt's three missing armour slots - it reproduces Will's
reports as artifact facts, so it is not a gate that can only ever be green.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from arz_patcher import ArzDatabase                       # noqa: E402
from patches import toxeus_boss_equipment as TBE          # noqa: E402

DEFAULT_ARZ = HERE.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'


def _run(db):
    problems = TBE._check(db)
    modwide, checked, waived = TBE._check_modwide(db)
    return problems + modwide, checked, waived


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    dryrun = '--dryrun' in argv
    arz = Path(args[0]) if args else DEFAULT_ARZ
    if not arz.exists():
        print("gate_toxeus_boss_equipment: arz not found: %s" % arz)
        return 2
    print("gate_toxeus_boss_equipment: %s" % arz)
    db = ArzDatabase.from_arz(arz)

    problems, checked, waived = _run(db)
    if dryrun:
        print("  BEFORE apply(): %d problem(s), %d 100%%-pinned Finger2 carrier(s) checked, "
              "%d pre-existing waived" % (len(problems), checked, waived))
        for p in problems[:12]:
            print("     RED: %s" % p)
        if not problems:
            print("  DRYRUN FAILED: the input arz already satisfies the contract, so this "
                  "run proves nothing about apply(). Point it at the pre-fix arz.")
            return 1
        TBE.apply(db, {})
        problems, checked, waived = _run(db)
        if problems:
            print("  DRYRUN FAILED: apply() did NOT close the contract - %d problem(s) left"
                  % len(problems))
            for p in problems[:20]:
                print("     STILL RED: %s" % p)
            return 1
        print("  DRYRUN PASS: RED -> GREEN on the real arz (in memory only, nothing written)")
        return 0

    if problems:
        for p in problems[:30]:
            print("  R-251 OFFENDER: %s" % p)
        print("gate_toxeus_boss_equipment: FAIL (%d problem(s))" % len(problems))
        return 1
    print("gate_toxeus_boss_equipment: PASS (%d 100%%-pinned Finger2 carrier(s) all deliver "
          "a ring; %d pre-existing offender(s) waived by name - BL-R251-DEBT-5)"
          % (checked, waived))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
