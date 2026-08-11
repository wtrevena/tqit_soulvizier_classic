r"""gate_loot_distribution.py - AUDIT: the drop DISTRIBUTION of every mod loot surface
(Will 2026-08-10, R-181).

WHY THIS EXISTS
---------------
Will, verbatim (2026-08-10), twice in one sitting:
  "also what about the armor? i am not really seeing armor drops like shields, chest
   plates, helmets, etc."
  "you overcorrected, that run 4 scorpions tail spears dropped"

`gate_chest_loot_breadth` (R-180) answers REACHABILITY - can this chest pay a legendary
spear at all. Neither of those reports is a reachability report. Measured on the shipped
build76 arz, every mod chest already reached all five worn slots and R-180's own gate was
GREEN while the Gaoler cage paid 58.5 legendary weapons against 12.4 armour pieces per
six-chest run, with SPEAR alone at 25.8% of the legendary mass. A gate that cannot see
that is the gate that let both reports happen.

WHAT IT ASSERTS, per SURFACE (a surface = what the player experiences as one loot event:
the cage's chest_01 with its three themed variants at the pool's 50/25/25, each boss
hoard, the blood-cave mega chest):

  D1  no equipment class holds more than MAX_CLASS_SHARE_TABLE of one TABLE's mass
  D2  no equipment class holds more than MAX_CLASS_SHARE_AGGREGATE of the SURFACE's mass
  D3  no class the surface claims to pay is below MIN_CLASS_SHARE_TABLE (starving)
  D4  no single ITEM exceeds its class's near-uniform bound (the "4 copies of the same
      spear" guard; the bound is relative to the class's pool size, because a 7-item
      class cannot be held to a share smaller than uniform)
  D5  no single ITEM exceeds MAX_ITEM_SHARE_TOTAL of the surface's whole mass
  D6  weapon:armour mass stays within MAX_WEAPON_ARMOUR_RATIO
  D7  every worn slot pays at least ARMOR_SLOT_FLOOR pieces per open

All thresholds and their derivations live in `tools/svc_loot_distribution.py`; the
in-build gate `tools/patches/armor_loot_breadth.verify` and the negative tests
`tools/debug/negtest_armor_breadth.py` share this one implementation, so the standalone
audit and the build gate cannot disagree (the gate_relic_difficulty_tiers precedent).

Usage:
  py tools/gate_loot_distribution.py <arz>              # audit, exit 1 on any skew
  py tools/gate_loot_distribution.py <arz> --verbose    # per-surface slot table
  py tools/gate_loot_distribution.py <arz> --calibrate  # print the worst OBSERVED
                                                        # value per check and exit 0
  py tools/gate_loot_distribution.py <arz> --apply ...  # apply the R-181 wave in memory
                                                        # first, so a PRE-wave arz can be
                                                        # measured against the same
                                                        # contract (idempotent; this is
                                                        # how the before/after arithmetic
                                                        # in the R-181 record is
                                                        # reproduced from one command)
"""
import sys
from collections import defaultdict
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase
import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD


def calibrate(db):
    """Print the worst OBSERVED value for every check. Used to derive the committed
    thresholds from measurement instead of taste, and to compare two builds."""
    lk = SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    worst = defaultdict(lambda: (0.0, ''))
    best_min = (1e9, '')
    thin = (1e9, '')
    low_ratio = (1e9, '')
    for label, tables, weights, tier in SAB.all_surfaces(db, lk):
        profs = [SLD.ChestProfile(d, dist, t, 1,
                                  {'n': 'Epic', 'e': 'Legendary',
                                   'l': 'Legendary'}[tier]) for t in tables]
        w = [float(x) for x in (weights or [1] * len(profs))]
        tw = sum(w) or 1.0
        agg, agg_item = defaultdict(float), defaultdict(float)
        for wi, p in zip(w, profs):
            for s, ev in p.by_slot().items():
                agg[s] += wi / tw * ev
            for it, ev in p.per_item.items():
                if SLD.CLASS_TO_SLOT.get(d.cls(it)):
                    agg_item[it] += wi / tw * ev
        tot = sum(agg.values())
        if tot <= 0:
            continue
        for p in profs:
            bs = p.by_slot()
            m = sum(bs.values()) or 1.0
            for s, ev in bs.items():
                if ev / m > worst['D1 class share, table'][0]:
                    worst['D1 class share, table'] = (
                        ev / m, '%s %s' % (SLD._n(p.table).rsplit('\\', 1)[-1], s))
        for s, ev in agg.items():
            if ev / tot > worst['D2 class share, surface'][0]:
                worst['D2 class share, surface'] = (ev / tot, '%s %s' % (label, s))
        for s in SLD.SLOT_ORDER:
            v = agg.get(s, 0.0) / tot
            if v < best_min[0]:
                best_min = (v, '%s %s' % (label, s))
        by_slot = defaultdict(dict)
        for it, ev in agg_item.items():
            by_slot[SLD.CLASS_TO_SLOT[d.cls(it)]][it] = ev
        for s, items in by_slot.items():
            m = sum(items.values())
            if m <= 0:
                continue
            top, tev = max(items.items(), key=lambda kv: kv[1])
            ratio = (tev / m) * len(items)          # x uniform
            if ratio > worst['D4 item share / uniform'][0]:
                worst['D4 item share / uniform'] = (
                    ratio, '%s %s (%d items)' % (label,
                                                 SLD._n(top).rsplit('\\', 1)[-1],
                                                 len(items)))
            if tev / tot > worst['D5 item share, surface'][0]:
                worst['D5 item share, surface'] = (
                    tev / tot, '%s %s' % (label, SLD._n(top).rsplit('\\', 1)[-1]))
        wm = sum(agg.get(s, 0.0) for s in SLD.WEAPON_SLOTS)
        am = sum(agg.get(s, 0.0) for s in SLD.ARMOR_SLOTS)
        if am > 0 and wm / am > worst['D6 weapon:armour'][0]:
            worst['D6 weapon:armour'] = (wm / am, label)
        if am > 0 and wm / am < low_ratio[0]:
            low_ratio = (wm / am, label)                    # D6b, the MIRROR
        for s in SLD.WEAPON_SLOTS:
            if wm > 0 and agg.get(s, 0.0) / wm > worst['D8 class share of weapons'][0]:
                worst['D8 class share of weapons'] = (agg.get(s, 0.0) / wm,
                                                      '%s %s' % (label, s))
        for s in SLD.ARMOR_SLOTS:
            if am > 0 and agg.get(s, 0.0) / am > worst['D9 slot share of armour'][0]:
                worst['D9 slot share of armour'] = (agg.get(s, 0.0) / am,
                                                    '%s %s' % (label, s))
        for s in SLD.ARMOR_SLOTS:
            if agg.get(s, 0.0) < thin[0]:
                thin = (agg.get(s, 0.0), '%s %s' % (label, s))
    print('\n=== CALIBRATION (worst observed value per check) ===')
    for k in sorted(worst):
        v, who = worst[k]
        print('  %-28s %8.4f   %s' % (k, v, who))
    print('  %-28s %8.4f   %s' % ('D3 thinnest class share', best_min[0], best_min[1]))
    print('  %-28s %8.4f   %s' % ('D6b LOWEST weapon:armour', low_ratio[0], low_ratio[1]))
    print('  %-28s %8.4f   %s' % ('D7 thinnest armour slot', thin[0], thin[1]))


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/gate_loot_distribution.py <arz> "
              "[--verbose] [--calibrate]")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    if '--apply' in argv[2:]:
        # Audit the arz AS IF the wave had run - so a PRE-wave arz can be measured
        # against the same contract the build gate enforces, and the before/after
        # arithmetic in the R-181 record is reproducible from one command.
        print("  --apply: R-181 wave applied in memory (idempotent; safe on a built arz)")
        SAB.apply_wave(db)
    if '--calibrate' in argv[2:]:
        calibrate(db)
        return 0
    verbose = '--verbose' in argv[2:]
    print("\n=== loot-distribution audit (R-181) ===")
    problems, reports = SAB.audit_db(db, verbose=verbose)
    print("loot surfaces audited: %d" % len(reports))
    for k, why in sorted(SLB.EXEMPT.items()):
        print("  EXEMPT %s - %s" % (k, why))
    if problems:
        print("\nSKEWED SURFACES: %d finding(s)" % len(problems))
        for p in problems:
            print("  FAIL  %s" % p)
        print("\nGATE FAIL: a loot surface is skewed across classes, dominated by one "
              "item, or starving a worn slot.")
        return 1
    print("\nGATE PASS: every mod loot surface spreads across all %d equipment classes "
          "within its committed bounds, and every worn slot clears %.2f piece(s) per "
          "open." % (len(SLD.GEAR_SLOTS), SLD.ARMOR_SLOT_FLOOR))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
