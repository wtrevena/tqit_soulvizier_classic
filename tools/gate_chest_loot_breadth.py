r"""gate_chest_loot_breadth.py - AUDIT: every mod chest can pay every weapon class at
its own difficulty tier, SPEAR included (Will 2026-08-10).

WHY THIS EXISTS
---------------
Will, verbatim (2026-08-10): "there are never any legendary spears dropped it is
basically the same items dropped over and over by all chests."

Measured cause: every mod chest's weapon row is a clone of the DRX donor
`loottable_hidden_bloodcave_0N`, whose loot1 names `unique_1h_*01` (a LootMasterTable
with exactly three children: axe, club, sword) plus `bow_*01` and `staff_*01` - the two
classes that master excludes. It forgot the THIRD excluded class, spear. The only spear
path left was the static randomizer table, which has 0 Legendary leaves, so a legendary
spear was structurally impossible in all 40 mod chest tables while 24 legendary spears
sat in the DB unreachable.

WHAT IT ASSERTS (per mod-owned FixedItemLoot chest table, tier read from the tables it
NAMES - never from its own file name, since polisvault_0N is a chest index, not a tier):

  B1  the chest reaches at least one item of EVERY weapon class at its own tier:
      Axe, Mace, Sword, SPEAR, Bow, Staff. Fails loud naming the table + the missing
      class(es).
  B2  the distinct target-classification pool is at least the per-tier floor (a
      collapse back to a 3-class row reds here even if one stray spear survives).
  B3  Normal reaches no legendary GEAR (the R-100 #17 / Will 2026-08-08 tier law -
      breadth must never be bought by leaking legendaries down a difficulty).

Scope = every mod-owned chest loot table (\svc\ folder or svc_ prefix) except the
documented exemptions in svc_loot_breadth.EXEMPT, so a NEW chest is in scope by default
and can never quietly ship collapsed.

Usage:
  py tools/gate_chest_loot_breadth.py <arz>             # audit, exit 1 on any collapse
  py tools/gate_chest_loot_breadth.py <arz> --verbose   # per-table pool + class table

Shares ONE implementation with the in-build gate
(tools/patches/chest_loot_breadth.verify) and with polis_vault.verify's T7, via
tools/svc_loot_breadth.py, so the standalone audit and the build gate cannot disagree
(the gate_relic_difficulty_tiers precedent).
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_chest_loot_breadth.py <arz> [--verbose] [--apply]")
        return 2
    verbose = '--verbose' in argv[2:]
    db = ArzDatabase.from_arz(Path(argv[1]))
    if '--apply' in argv[2:]:
        # Apply the R-180 + R-181 wave in memory first, so REACHABILITY can be checked
        # on the post-wave state from a pre-wave arz. R-181 only raises weights/chances
        # and adds members, so this must never lose a pool - and that is a claim worth
        # being able to re-run rather than assert.
        import svc_armor_breadth as SAB
        print("  --apply: R-180 + R-181 wave applied in memory")
        SAB.apply_wave(db)
    print("\n=== chest loot-breadth audit ===")
    problems, stats = SLB.audit_db(db, verbose=verbose)
    print("mod-owned chest loot tables audited: %d" % len(stats))
    for tier in SLB.TIERS:
        pools = [v[1] for v in stats.values() if v[0] == tier]
        if pools:
            print("  %s tier: %d table(s), %s pool %d..%d (floor %d)"
                  % (tier, len(pools), SLB.TARGET_IC[tier], min(pools), max(pools),
                     SLB.POOL_FLOOR[tier]))
    for k, why in sorted(SLB.EXEMPT.items()):
        print("  EXEMPT %s - %s" % (k, why))
    if problems:
        print("\nCOLLAPSED CHESTS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: a mod chest cannot pay every weapon class at its own tier.")
        return 1
    print("\nGATE PASS: every mod-owned chest pays all %d weapon classes at its own "
          "tier (SPEAR included), clears its pool floor, and Normal stays free of "
          "legendary gear." % len(SLB.REQUIRED_WEAPON_CLASSES))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
