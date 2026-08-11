r"""gate_orb_legendary.py - AUDIT: how often an uber orb pays a LEGENDARY (R-241).

WILL, VERBATIM (2026-08-11), superseding the b79 "orbs stay generous" precedent:
  "you made the orbs way too good... those dont need to have guaranteed legendary
   drops, they should just have a chance to drop legendary items, but a low chance."

`gate_orb_loot_breadth` (R-220) answers WHAT an orb can pay. `gate_loot_distribution`
(R-181) answers in WHAT PROPORTIONS. `gate_loot_volume` (R-240) answers HOW MUCH, in
gear pieces. None of them can see how often the thing that falls out is LEGENDARY, and
on the shipped b83 arz all three were GREEN while an apex Legendary orb paid 8.43
legendary items per open with a 99.99% chance of at least one.

WHAT IT ASSERTS
  O1  ZERO guaranteed-legendary rows - no orb loot group may fire on every spawn
      iteration AND be able to pay a legendary (Will's ruling, literally)
  O2  no orb pays more than ORB_MAX_LEG_PER_OPEN legendary items per open (the
      headline: at most ONE on Legendary difficulty, against 8.43 shipped)
  O3  ... and pays at least one no more often than ORB_MAX_P_LEGENDARY of opens
  O4  the MIRROR - a legendary must still be POSSIBLE at a real rate ("just a CHANCE",
      not "no chance"), so the ceiling cannot be met by deleting the reward
  O5  ... and the orb must still pay ORB_MIN_DROPS_PER_OPEN items of any kind, so the
      ceiling cannot be met by turning the orb into an empty box

R-240 left two readings of the spawn count because the engine's rounding mode is unproven
(`BL-R240-DEBT-5`), and its rule is that each check runs under the model hardest on it.
Here that lands ASYMMETRICALLY, and the asymmetry is deliberate: truncated S is always
<= continuous S and both readings rise with S, so the CONTINUOUS one is the pessimistic
side of a CEILING (O2, O3) and the TRUNCATED one is the pessimistic side of a FLOOR (O4).
There is therefore no truncated ceiling twin - it could never fire while its continuous
parent was green, and a check that cannot fail is worse than no check because it still
appears in the PASS line.

All thresholds and their derivations live in `tools/svc_orb_legendary.py`; the in-build
gate `tools/patches/orb_legendary_chance.verify` and the negative battery
`tools/debug/negtest_orb_legendary.py` share this one implementation, so the standalone
audit and the build gate cannot disagree.

Usage:
  py tools/gate_orb_legendary.py <arz>              # audit, exit 1 on any finding
  py tools/gate_orb_legendary.py <arz> --census     # JUST the number Will asked for
  py tools/gate_orb_legendary.py <arz> --calibrate  # every reading behind every constant
  py tools/gate_orb_legendary.py <arz> --apply      # apply R-240 + R-241 in memory first,
                                                    # so a PRE-wave arz measures against
                                                    # the same contract

⚠ `--apply` runs R-240's volume trim first and R-241's demotion second, because that is
the registry order and the two readings are not independent: the demotion's effect on
E[legendary] is measured against the TRIMMED spawn volume. R-240's half is APPLY-ONCE
and says so; R-241's half is naturally idempotent (a second pass finds no row at 100 and
writes nothing) and proves it by measurement rather than claiming it.
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_loot_volume as SLV
import svc_orb_legendary as SOL


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_orb_legendary.py <arz> [--census] [--calibrate] "
              "[--apply]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    flags = argv[2:]
    if '--apply' in flags:
        if SLV.already_applied(db):
            print("  --apply: R-240 volume wave already present, not re-run (APPLY-ONCE)")
        else:
            print("  --apply: R-240 volume trim applied in memory")
            SLV.apply_wave(db, verbose=False)
        lk = SLB.Lookup(db)
        n = len(SOL.already_applied(db, lk))
        print("  --apply: R-241 demotion applied in memory (%d guaranteed-legendary "
              "row(s) found)" % n)
        SOL.apply_wave(db, lk, verbose=True)
    lk = SLB.Lookup(db)
    if '--census' in flags:
        SOL.census(db, lk)
        return 0
    if '--calibrate' in flags:
        SOL.calibrate(db, lk)
        return 0
    print("\n=== uber-orb legendary audit (R-241) ===")
    report = {}
    problems = SOL.problems(db, lk, report=report)
    print("orb loot tables in scope: %d" % report.get('tables', 0))
    if problems:
        print("\nORB LEGENDARY FINDINGS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: an uber orb pays legendary outside its committed band.")
        return 1
    print("\nGATE PASS: %s. No orb loot row is a guaranteed legendary roll; every orb "
          "keeps a real but bounded chance at one (floors %s), and none of them has "
          "become an empty box (floor %.2f items/open)."
          % (SOL.pass_line(report), SOL.ORB_MIN_P_LEGENDARY,
             SOL.ORB_MIN_DROPS_PER_OPEN))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
