r"""gate_craft_thrown_breadth.py - AUDIT: the uber-craft chain is completable on every
difficulty, and the THROWN class is payable (Will 2026-08-10).

WHY THIS EXISTS
---------------
Will, verbatim (2026-08-10): "i meant do the mythic formulas drop. they can drop in
normal as well, but the legendary items should not drop in normal. All of the reagents
need to be droppable somewhere in the game, ideally from chests since that is where
people will look. if players farm legendary long enough, they should be able to find all
the reagents without having to farm a specific area or a specific character (except for
the monster unique droppable items like the green items that are needed to build some of
the formulas...). Yes we should make the legendary thrown weapons droppable."

WHAT IT ASSERTS (see tools/svc_craft_thrown.py for the measured causes):
  F1  every uber craftable has at least one chest-droppable formula at EVERY tier
      (n / e / l). Before this wave, Normal reached 0 of 42.
  G0  no reagent names a record that does not exist in the database (three RAGNAROK
      `xpack2\...\1hranged\` ghosts made all four thrown craftables uncompletable).
  G1  every NON-MI reagent is reachable from the Legendary-tier chest pools.
  G2  the committed MI ("green") exemption roster still equals the roster the rule
      (`itemClassification == 'Rare'`) derives from the database.
  C1  Epic/Legendary chests reach a Legendary one-hand-ranged item.
  C2  Normal chests reach a one-hand-ranged item and ZERO legendary ones (tier law).

Usage:
  py tools/gate_craft_thrown_breadth.py <arz>              # audit, exit 1 on any problem
  py tools/gate_craft_thrown_breadth.py <arz> --verbose    # per-tier + per-bucket detail
  py tools/gate_craft_thrown_breadth.py <arz> --mi-sources # print the MI exemption list
                                                           # with the monster loot tables
                                                           # that pay each one

Shares ONE implementation with the in-build gate
(tools/patches/craft_thrown_breadth.verify) and with svc_loot_breadth.audit_table's
C1/C2 rule, via tools/svc_craft_thrown.py.
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_craft_thrown as SCT
import svc_loot_breadth as SLB


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_craft_thrown_breadth.py <arz> [--verbose] "
              "[--mi-sources]")
        return 2
    flags = argv[2:]
    verbose = '--verbose' in flags
    db = ArzDatabase.from_arz(Path(argv[1]))
    lk = SLB.Lookup(db)

    print("\n=== uber-craft chain + thrown-class audit ===")
    problems, stats = SCT.audit_db(db, verbose=verbose, lk=lk)
    f = stats['formulas']
    r = stats['reagents']
    print("uber craftables: %d (built by %d formula records)" % (f['l'][1], f['l'][3]))
    for tier in SCT.TIERS:
        cov, tot, fr, ftot = f[tier]
        print("  %s tier: %d/%d craftables have a chest-droppable formula "
              "(%d/%d formula records reachable)" % (tier, cov, tot, fr, ftot))
    print("reagents: %d distinct = %d MI/green (exempt, monster-farmed) + %d ordinary + "
          "%d artifact + %d missing" % (r['total'], r['mi'], r['ordinary'],
                                        r['artifact'], r['missing']))
    print("  reachable from a Legendary-tier chest: %d/%d"
          % (r['reachable_l'], r['total']))
    print("thrown: %d mod chest table(s) audited for the %s class"
          % (stats['chests'], SCT.THROWN_CLASS))

    if '--mi-sources' in flags:
        print("\nMI / green exemption roster (Will: \"except for the monster unique "
              "droppable items like the green items\"), with the monsters that pay each:")
        for reagent in r['buckets'].get('mi', ()):
            monsters, tables = r['mi_sources'].get(reagent) or \
                SCT.monster_sources(db, lk, reagent)
            names = sorted({SLB._n(m).rsplit('\\', 1)[-1][:-4] for m in monsters})
            print("  %-26s %3d monster(s) via %d table(s): %s%s"
                  % (SLB._n(reagent).rsplit('\\', 1)[-1][:-4], len(monsters), len(tables),
                     ', '.join(names[:6]) or '(NONE - unobtainable)',
                     ' ...' if len(names) > 6 else ''))

    if problems:
        print("\nPROBLEMS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: the uber-craft chain is not completable, or the thrown class "
              "is unpayable.")
        return 1
    print("\nGATE PASS: every uber craftable is formula-reachable on every difficulty, "
          "every non-MI reagent is farmable from Legendary chests, the MI exemption "
          "roster is intact, and the thrown class pays at every tier with no legendary "
          "thrown on Normal.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
