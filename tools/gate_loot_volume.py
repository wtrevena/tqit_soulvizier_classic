r"""gate_loot_volume.py - AUDIT: how MUCH every mod loot surface pays (R-230).

WILL, VERBATIM (2026-08-11):
  "we probably need to trip the loot-volume trim, especially on the steam version
   where maybe from the two chests, you get guaranteed 1 legendary item. on the
   testhub version we can spawn more that is fine."

`gate_chest_loot_breadth` (R-180) answers WHAT a chest can pay. `gate_loot_distribution`
(R-181) answers in WHAT PROPORTIONS. Neither can see HOW MUCH: every distribution check
is a ratio, and a ratio is invariant under the one lever Will just pulled. On the shipped
b83 arz both were GREEN while the two canonical cage chests paid 36.4 Legendary-grade
gear pieces per run. This is the third, orthogonal question.

WHAT IT ASSERTS
  V1  no CANONICAL surface pays more than CANON_MAX_GEAR_PER_OPEN per open
  V2  the TESTHUB cage twin pays at least HUB_MIN_CAGE_RUN - a FLOOR, so the DEV farm
      cannot be trimmed away by a later lane
  V3  no in-scope table spawns fewer than MIN_SPAWN_MIN_SOLO iterations at one player
      (the build28/29/30 "chest opens, drops nothing" P0)
  V4  every numSpawn equation kept its `numberOfPlayers` term and its readable shape
  V5  every TESTHUB cage table is STRICTLY richer than its canonical twin
  V6  the canonical two-chest cage RUN stays under CANON_MAX_CAGE_RUN, per difficulty
  V7  ... and still pays at least one item at the tier's target grade >= 95% of runs,
      because Will's word was "guaranteed"

All thresholds and their derivations live in `tools/svc_loot_volume.py`; the in-build
gate `tools/patches/loot_volume_trim.verify` and the negative battery
`tools/debug/negtest_loot_volume.py` share this one implementation, so the standalone
audit and the build gate cannot disagree (the gate_relic_difficulty_tiers precedent).

Usage:
  py tools/gate_loot_volume.py <arz>              # audit, exit 1 on any finding
  py tools/gate_loot_volume.py <arz> --calibrate  # worst observed value per check
  py tools/gate_loot_volume.py <arz> --apply      # apply R-230 in memory first, so a
                                                  # PRE-wave arz measures against the
                                                  # same contract (idempotent)
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_loot_volume as SLV


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_loot_volume.py <arz> [--calibrate] [--apply]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    if '--apply' in argv[2:]:
        print("  --apply: R-230 wave applied in memory (idempotent; safe on a built arz)")
        SLV.apply_wave(db, verbose=True)
    lk = SLB.Lookup(db)
    if '--calibrate' in argv[2:]:
        SLV.calibrate(db, lk)
        return 0
    print("\n=== loot-volume audit (R-230) ===")
    report = {}
    problems = SLV.problems(db, lk, report=report)
    print("loot surfaces in scope: %d canonical + %d TESTHUB twin record(s)"
          % (report.get('canonical', 0), report.get('hub', 0)))
    if problems:
        print("\nVOLUME FINDINGS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: a loot surface pays outside its committed volume band.")
        return 1
    worst, who = report.get('worst_surface', (0.0, '-'))
    print("\nGATE PASS: every CANONICAL loot surface pays at most %.2f target-grade gear "
          "piece(s) per open (worst %.2f on %s); the two-chest cage run stays under "
          "%s and still pays at least one at >= %.0f%% of runs; the TESTHUB twin keeps "
          "its shipped volume (floor %s); every in-scope numSpawn equation still carries "
          "`numberOfPlayers` and still spawns >= %.2f iteration(s) solo."
          % (SLV.CANON_MAX_GEAR_PER_OPEN, worst, who, SLV.CANON_MAX_CAGE_RUN,
             100.0 * SLV.MIN_P_AT_LEAST_ONE, SLV.HUB_MIN_CAGE_RUN,
             SLV.MIN_SPAWN_MIN_SOLO))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
