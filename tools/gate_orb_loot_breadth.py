r"""gate_orb_loot_breadth.py - AUDIT: every uber's MYSTICAL ORB can pay every weapon
class at its own difficulty, SPEAR included (Will 2026-08-10, R-210).

WHY THIS EXISTS
---------------
Will, verbatim (2026-08-10): "for the mystical orbs that the uber monsters drop, the
items should drop with increased breadth as well so all classes of items could be
dropped."

Measured cause, and it is R-180's defect in a second donor family: every uber orb loot
table's weapon row names `1h_all_*01` (a LootMasterTable with exactly three children -
axe, club, sword) plus `bow_*01` and `staff_*01`, the two classes that master excludes,
and forgot the THIRD excluded class, SPEAR. The level-banded statics beside them carry
no unique spears at all. So **0 spears were reachable from 15 of the 18 uber orb tables,
at every tier and every difficulty** - while orb05's three `svc_uberorb_apex_*` tables
were already fine, purely because they sit in an `\svc\` folder and R-180's
mod-ownership sweep therefore reached them.

WHAT IT ASSERTS (per in-scope table, at the tier its DIFFICULTY SLOT gives it - never
guessed from a file name, since `uberorb_default_13-15` is a LEVEL band, not a tier):

  O1   the table reaches at least one item of EVERY weapon class at its own tier:
       Axe, Mace, Sword, SPEAR, Bow, Staff. Fails loud naming table + missing class.
  O2   the distinct target-classification pool clears the per-branch floor.
  O2b  the tier-correct breadth master is still NAMED in the weapon row (structural,
       so a re-collapse reds by name even where a count-only floor could not).
  O3   the normal branch reaches no legendary GEAR (R-100 #17 / Will 2026-08-08).
  O4   every uber orb chain resolves proxy -> accessory pool -> chest -> loot table at
       all three difficulties, and the derived scope never shrinks below its measured
       floor (an orb gate that audits nothing is the failure this gate prevents).
  O5   every uber chain whose proxy exists ONLY in the base game is PINNED in
       `svc_orb_breadth.OUT_OF_REACH` with the reason it is not widened, and no pin is
       stale. MEASURED: exactly one - the Dark Obelisk's Tower-of-Judgement treasure,
       whose chain lands on the shared act-4 GOLDEN CHEST tables.
  O6   no in-scope table is also named by a container outside every uber chain.
       Widening a shared table would change base-game loot from a lane asked about
       mystical orbs, so such a table is excluded from the sweep and the gate stops
       the build until a human decides (pin it in SHARED_TABLES_ACKNOWLEDGED).

SCOPE is DERIVED, never typed (the R-200 lesson): every proxy an UBER names
(`um_*` basename or a `tagSVCMonster*` display tag), over mod UNION base, and every
loot table its three difficulty slots resolve to. Pass `--mod-only` to skip the base
arz load; the scan then cannot see a base-only uber and says so.

Usage:
  py tools/gate_orb_loot_breadth.py <arz>              # audit, exit 1 on any collapse
  py tools/gate_orb_loot_breadth.py <arz> --verbose    # per-table pool + spear count
  py tools/gate_orb_loot_breadth.py <arz> --mod-only   # skip the base-game union

Shares ONE implementation with the in-build gate (tools/patches/orb_loot_breadth.verify)
and with the negatives (tools/debug/negtest_orb_breadth.py) via tools/svc_orb_breadth.py,
so the standalone audit and the build gate cannot disagree (the R-180 precedent).
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'patches'))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_orb_breadth as SOB


def load_base_rows(mod_only):
    if mod_only:
        print("  base-game union SKIPPED (--mod-only): a base-only uber's orb cannot "
              "be seen by this run.")
        return None
    try:
        import red_uber_orbs as RUO
        return RUO.load_base_rows(required=False, who='gate_orb_loot_breadth')
    except ImportError as exc:
        print("  WARNING cannot import red_uber_orbs (%s); running MOD-ONLY." % exc)
        return None


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_orb_loot_breadth.py <arz> [--verbose] [--mod-only]")
        return 2
    verbose = '--verbose' in argv[2:]
    db = ArzDatabase.from_arz(Path(argv[1]))
    print("\n=== uber orb loot-breadth audit (R-210) ===")
    base_rows = load_base_rows('--mod-only' in argv[2:])
    lk = SLB.Lookup(db)

    carriers = SOB.uber_proxies(db, base_rows)
    print("uber carriers: %d, naming %d proxy/proxies"
          % (sum(len(v) for v in carriers.values()), len(carriers)))
    for proxy_l in sorted(carriers):
        print("  %-36s %2d uber carrier(s)%s"
              % (proxy_l.rsplit('\\', 1)[-1], len(carriers[proxy_l]),
                 '' if lk.real(proxy_l)
                 else '   OUT OF REACH (base-only proxy; O5 requires a pin)'))

    problems, stats = SOB.audit_db(db, lk, base_rows, verbose=verbose)
    print("uber orb loot tables audited: %d" % len(stats))
    for tier in SLB.TIERS:
        pools = [v[1] for v in stats.values() if v[0] == tier]
        spears = [v[2].get('WeaponHunting_Spear', 0) for v in stats.values()
                  if v[0] == tier]
        if pools:
            print("  %s branch: %d table(s), %s pool %d..%d (floor %d), spear %d..%d"
                  % (tier, len(pools), SLB.TARGET_IC[tier], min(pools), max(pools),
                     SOB.POOL_FLOOR[tier], min(spears), max(spears)))
    if problems:
        print("\nCOLLAPSED ORB TABLES: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: an uber's mystical orb cannot pay every weapon class at "
              "its own difficulty.")
        return 1
    print("\nGATE PASS: every uber orb loot table pays all %d weapon classes at its "
          "own difficulty (SPEAR included), clears its pool floor, still names the "
          "breadth master, and the normal branch stays free of legendary gear."
          % len(SLB.REQUIRED_WEAPON_CLASSES))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
