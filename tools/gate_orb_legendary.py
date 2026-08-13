r"""gate_orb_legendary.py - AUDIT: how often an uber orb pays a LEGENDARY or a BLUE, by
difficulty (R-242, Will 2026-08-12). SUPERSEDES R-241; CLOSES BL-R241-DEBT-1.

WILL, VERBATIM (2026-08-12)
  "all the orbs that uber monsters drop should have a 50% chance of dropping a legendary
   item on epic, a 75% of dropping a legendary item on legendary, a 0% chance of dropping
   a legendary item on normal, but a 75% chance of dropping a blue item on normal ..."
  "Note that Leinth and the toxeus variants keep their current higher / better orbs ..."

`gate_orb_loot_breadth` (R-220) answers WHAT an orb can pay, `gate_loot_distribution`
(R-181) in WHAT PROPORTIONS, `gate_loot_volume` (R-240) HOW MUCH. None sees how OFTEN the
thing that falls out is LEGENDARY or BLUE, or holds the Toxeus/Leinth exclusion.

WHAT IT ASSERTS
  X0  the DERIVED Toxeus/Leinth exclusion set equals the pinned apex roster (a rewired
      consumer reds instead of silently changing scope)
  G1  each general orb pays its per-difficulty target within +/-5pp: Epic(blue) 75% on
      Normal, Legendary 50% on Epic, Legendary 75% on Legendary
  G2  a Normal general orb pays 0% legendary GEAR (the tier law; the base-game
      scroll/formula leak on loot4 is exempt and measured apart)
  G3  each excluded apex table is byte-identical to build85 (loot profile + numSpawn)
  G5  every orb still pays at least ORB_MIN_DROPS_PER_OPEN items of any kind (the
      empty-box mirror, so a rate band cannot be met by deleting the reward)

All thresholds live in `tools/svc_orb_legendary.py`; the in-build gate
`tools/patches/orb_legendary_chance.verify` and the negative battery
`tools/debug/negtest_orb_legendary.py` share this one implementation.

Usage:
  py tools/gate_orb_legendary.py <arz>                 # audit, exit 1 on any finding
  py tools/gate_orb_legendary.py <arz> --census        # the partition
  py tools/gate_orb_legendary.py <arz> --calibrate      # every reading behind every band
  py tools/gate_orb_legendary.py <arz> --apply          # apply R-240 + R-242 in memory
  py tools/gate_orb_legendary.py <arz> --baseline <arz> # ALSO byte-diff the 3 apex tables
                                                        # against a build85 baseline arz
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_loot_volume as SLV
import svc_orb_legendary as SOL


def apex_diff_vs_baseline(db, lk, base_db):
    """[str] - full field-by-field differences of the 3 excluded apex records vs a
    build85 baseline arz. Empty == byte-identical. Stronger than the pinned-value check
    because it compares EVERY field, not just the loot profile."""
    base_lk = SLB.Lookup(base_db)
    out = []
    for _tier, path in sorted(SOL.APEX_PINNED.items()):
        real = lk.real(path)
        bref = base_lk.real(path)
        if not real or not bref:
            out.append("APEX %s missing (this=%s baseline=%s)"
                       % (path.rsplit('\\', 1)[-1], bool(real), bool(bref)))
            continue
        now = {k.split('###')[0]: list(tf.values)
               for k, tf in (db.get_fields(real) or {}).items()}
        was = {k.split('###')[0]: list(tf.values)
               for k, tf in (base_db.get_fields(bref) or {}).items()}
        for f in sorted(set(now) | set(was)):
            if now.get(f, []) != was.get(f, []):
                out.append("APEX %s.%s %r -> %r"
                           % (path.rsplit('\\', 1)[-1], f, was.get(f), now.get(f)))
    return out


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_orb_legendary.py <arz> [--census] [--calibrate] "
              "[--apply] [--baseline <arz>]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    flags = argv[2:]
    baseline = None
    if '--baseline' in flags:
        i = flags.index('--baseline')
        baseline = flags[i + 1]
    if '--apply' in flags:
        if SLV.already_applied(db):
            print("  --apply: R-240 volume wave already present, not re-run (APPLY-ONCE)")
        else:
            print("  --apply: R-240 volume trim applied in memory")
            SLV.apply_wave(db, verbose=False)
        lk = SLB.Lookup(db)
        n = len(SOL.already_applied(db, lk))
        print("  --apply: R-242 calibration+demotion applied in memory (%d pending)" % n)
        SOL.apply_wave(db, lk, verbose=True)
    lk = SLB.Lookup(db)
    if '--census' in flags:
        SOL.census(db, lk)
        return 0
    if '--calibrate' in flags:
        SOL.calibrate(db, lk)
        return 0
    print("\n=== uber-orb legendary/blue audit (R-242) ===")
    report = {}
    problems = SOL.problems(db, lk, report=report)
    print("orb loot tables in scope: %d (general %d, excluded %d)"
          % (report.get('tables', 0), report.get('general', 0), report.get('excluded', 0)))
    if baseline:
        base_db = ArzDatabase.from_arz(Path(baseline))
        diffs = apex_diff_vs_baseline(db, lk, base_db)
        if diffs:
            for dline in diffs:
                problems.append("G3b APEX BYTE-DIFF vs baseline: %s" % dline)
        else:
            print("apex byte-diff vs baseline: 0 differences on all 3 excluded tables.")
    notice = SOL.inversion_notice(db, lk)
    if notice:
        print("\n" + "!" * 78)
        print("!! " + notice.replace("\n", "\n!! "))
        print("!" * 78)
    if problems:
        print("\nORB LEGENDARY FINDINGS: %d" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: an uber orb pays outside its per-difficulty band, or an "
              "excluded apex table changed.")
        return 1
    print("\nGATE PASS: %s. Every general orb hits its per-difficulty legendary/blue "
          "band, every Toxeus/Leinth apex is byte-frozen at build85, and no orb is an "
          "empty box.%s"
          % (SOL.pass_line(report),
             "" if not notice else
             "\n  PASS MEANS THE BANDS HOLD, NOT THAT THE INVERSION IS RESOLVED - see the "
             "notice above (`BL-R242-DEBT-1`)."))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
