r"""gate_supra_recipe_laws.py - AUDIT: every supra recipe is Legendary-gated, and no two
supra recipes want the same three things (Will 2026-08-11).

WILL, VERBATIM (LAW A): "ok for the four epic craftable reagent's, we need to change it
so that one of the items needed to craft the formula needs to be found in legendary like
the rest of the craftable supra recipes."

WILL, VERBATIM (LAW B): "each craftable supra should have different requirements (we
should not have two formulas that both require stymphalian, plisskey, and deathweavers
legtip)"

WHAT IT ASSERTS (see tools/svc_supra_recipes.py for the measured causes):
  S1  every supra craftable names at least one reagent whose ONLY obtain paths are
      Legendary-tier. "Legendary-only" is proved, not asserted: the record is
      itemClassification = Legendary (so R-100 #17 confines it to `_l` hosts), a LEGENDARY
      chest pool reaches it (a reagent nothing can pay is uncompletable, not gated), and
      `obtainable_below_legendary` says NO - one recursive walk that covers the Normal and
      Epic chest pools, the upward table closure (which is what catches a MONSTER paying it
      on a lower difficulty) and the CRAFT path, following a formula into its own reagent
      slots rather than trusting the formula's tier. That walk is what separates "found in
      legendary" (Will's words) from "merely classified Legendary": it is why Hati's gate
      is a drop-only bow and not a divine artifact you can craft from an Epic arcane
      formula, and why Thoth's Glory counts as a gate for the reason that is actually true
      (its formula wants Legendary-only pieces) rather than the one round 2 published (an
      Epic chest pays that formula on 15 of 16 Epic surfaces).
  S2  no two supra craftables name an identical reagent multiset. S2b additionally fails
      a craftable whose several formula records disagree about its own reagents.
  S3  every reagent the de-duplication introduced still resolves, is not one of the 13
      dead `records\equipmentweapon\axe\` twins (five replacements have a dead twin at a
      path that differs only by the missing `item\` folder level), and is reachable from
      a Legendary chest pool.
  S4  LAW C ("the last word should not be dropped in epic, only legendary"): no supra
      ITEM is reachable from a Normal- or Epic-tier surface; S4b no craft-only supra is
      named by ANY loot table at any band; S4c the four supra thrown R-186 deliberately
      made droppable are still reachable on Legendary, because "only legendary" is a
      relocation and not a retirement.

Usage:
  py tools/gate_supra_recipe_laws.py <arz>              # audit, exit 1 on any problem
  py tools/gate_supra_recipe_laws.py <arz> --verbose    # per-craftable detail
  py tools/gate_supra_recipe_laws.py <arz> --sets       # print all 42 reagent sets
  py tools/gate_supra_recipe_laws.py <arz> --drops      # every supra item's drop paths

Shares ONE implementation with the in-build gate (tools/patches/supra_recipe_laws.verify)
and with `gate_craft_thrown_breadth`, via tools/svc_supra_recipes.py.
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_supra_recipes as SSR


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_supra_recipe_laws.py <arz> [--verbose] [--sets]")
        return 2
    flags = argv[2:]
    verbose = '--verbose' in flags
    db = ArzDatabase.from_arz(Path(argv[1]))
    lk = SLB.Lookup(db)
    ex = SLB.Expander(db, lk)

    print("\n=== supra recipe laws: Legendary gating + set uniqueness ===")
    problems, stats = SSR.audit_supra_laws(db, lk, ex, verbose=verbose)
    print("craftables: %d (built by %d formula records)"
          % (stats['craftables'], stats['formulas']))
    print("  distinct reagent sets: %d  (duplicate groups: %d)"
          % (stats['distinct_sets'], stats['duplicate_groups']))
    print("  Legendary-only reagents: %d of %d distinct reagents"
          % (stats['legendary_only_reagents'], stats['reagents']))
    print("  thinnest craftable carries %d Legendary-only reagent(s)"
          % stats['min_gated'])
    print("  supra ITEMS reachable from a loot table: %d (below Legendary: %d)"
          % (stats['droppable_supras'], stats['sub_legendary_supras']))

    if '--drops' in flags:
        print("\nsupra item drop paths (LAW C's input):")
        for result, (tiers, tables) in sorted(stats['drops'].items()):
            if not tables:
                continue
            print("  %-34s [%s] <- %s"
                  % (result.rsplit('\\', 1)[-1][:-4],
                     '/'.join(t.upper() for t in tiers) or 'no pool',
                     ', '.join(t.rsplit('\\', 1)[-1][:-4] for t in tables)))
        print("  (%d craftable(s) reachable from no loot table at all)"
              % len([1 for _t, tb in stats['drops'].values() if not tb]))

    if verbose:
        print("\nper craftable - the Legendary-only reagent(s) that gate it:")
        for result, good in sorted(stats['gated'].items()):
            print("  %-34s %s" % (result.rsplit('\\', 1)[-1][:-4],
                                  ', '.join(x.rsplit('\\', 1)[-1][:-4] for x in good)
                                  or '*** NONE ***'))
    if '--sets' in flags:
        print("\nall reagent sets (the S2 uniqueness input):")
        for result, per_formula in sorted(SSR.recipe_sets(db, lk).items()):
            rg = sorted(per_formula.values())[0]
            print("  %-34s %s" % (result.rsplit('\\', 1)[-1][:-4],
                                  ' + '.join(x.rsplit('\\', 1)[-1][:-4] for x in rg)))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems:
            print("  OFFENDER: %s" % p)
        return 1
    print("\nGATE PASS: S1 + S2 + S3 hold on this database.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
