r"""PROBE (read-only): DB-WIDE census of FROZEN thrown wielders.

The R-100 #15 invariant, stated over the whole roster rather than as N named
exceptions:

    Every Class=Monster record that EQUIPS a thrown weapon (a
    WeaponHunting_RangedOneHand, i.e. a `1h_ranged`/`roh_` loot slot at
    chance > 0) must name an animation table that BINDS, for the stance that
    weapon selects (`dualRanged` when both hands are thrown, else
    `rangedOneHand`), at minimum RunAnim + WalkAnim + AttackAnim1.

A record that fails it spawns and can neither move nor attack - Will's exact
report. This probe prints every violator in the given .arz.

Usage:
  py tools/debug/probe_frozen_throwers.py <db.arz> [<db2.arz> ...]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arz_patcher import ArzDatabase  # noqa: E402
from thrown_anim_rig import scan_frozen_throwers  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    bad_total = 0
    for p in sys.argv[1:]:
        db = ArzDatabase.from_arz(Path(p))
        throwers, frozen = scan_frozen_throwers(db)
        print("\n%s" % p)
        print("  thrown-weapon wielders found : %d" % len(throwers))
        print("  FROZEN (stance unbound)      : %d" % len(frozen))
        for rec, stance, tbl, missing in sorted(frozen):
            print("     %s" % rec)
            print("        stance=%-13s table=%s" % (stance, tbl))
            print("        unbound: %s" % ", ".join(missing))
        bad_total += len(frozen)
    raise SystemExit(1 if bad_total else 0)


if __name__ == "__main__":
    main()
