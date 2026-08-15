r"""gate_uber_hoard_generosity.py - AUDIT: does an uber/boss chest pay like one? (R-251)

`gate_chest_loot_breadth` (R-180) answers WHAT a chest can pay. `gate_loot_distribution`
(R-181) answers in WHAT PROPORTIONS. `gate_loot_volume` (R-240) answers HOW MUCH. All
three were GREEN on the shipped b888f022 arz while twenty-one uber chests paid base-game
Cyclops loot, because all three audit the TABLE and none of them audits the WIRE - whether
the chest the player opens actually names the table they measured.

This is the fourth, orthogonal question: IS THE TUNED TABLE THE ONE THAT OPENS?

WHAT IT ASSERTS (full derivations in `tools/svc_uber_hoards.py`)
  H1  every `svc_<fam>hoard_<tier>` chest names its OWN `svc_<fam>hoard_loot_<tier>`
  H2  no hoard loot table is an orphan (referenced by nothing in the whole db)
  H3  every hoard table carries the authored uber volume, exactly
  H4  ... keeps `numberOfPlayers` and clears the never-empty floor (build28/29/30 P0)
  H5  ... keeps its guaranteed 100% unique+relic row
  H6  the Secret Present gift box pays exactly 3x its SV original (BL-W0814-7)
  H7  no two uber chests share a loot record, and none shares the Devourer's stash
      (Will 2026-08-14: "we need to seperate those records")

⚠ THIS GATE REDS ON EVERY PRE-R-251 ARTIFACT, AND THAT IS THE GATE WORKING. On the
shipped build92 arz it reports 21 H1 findings and 21 H2 orphans - that IS the bug Will
filed five times. Do not "fix" a red by relaxing H1; measure a POST-R-251 arz.

Usage:
  py tools/gate_uber_hoard_generosity.py <arz>              # audit, exit 1 on a finding
  py tools/gate_uber_hoard_generosity.py <arz> --calibrate  # the whole family as a table
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_uber_hoards as SUH


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_uber_hoard_generosity.py <arz> [--calibrate]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    lk = SLB.Lookup(db)
    if '--calibrate' in argv[2:]:
        SUH.calibrate(db, lk)
        return 0
    print("\n=== uber/boss chest generosity audit (R-251) ===")
    report = {}
    problems = SUH.problems(db, lk, report=report)
    print("uber/boss hoard chests: %d; hoard loot tables: %d; orphaned tables: %d"
          % (report.get('chests', 0), report.get('tables', 0), report.get('orphans', 0)))
    if problems:
        print("\nGENEROSITY FINDINGS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: an uber/boss chest does not pay like one. On a PRE-R-251 "
              "artifact this is the ANCHOR WORKING, not a regression - see the header.")
        return 1
    print("\nGATE " + SUH.pass_line(report))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
