r"""armor_loot_breadth - WILL 2026-08-10 (R-181): armour parity + an even class spread.

WILL, VERBATIM, the two reports:
  1. "also what about the armor? i am not really seeing armor drops like shields,
     chest plates, helmets, etc."
  2. "you overcorrected, that run 4 scorpions tail spears dropped"

WHAT THIS MODULE IS. R-180 made every weapon class REACHABLE. This module makes the
distribution HONEST - it is the rate half, and both of Will's reports are rate reports.
The whole contract lives in `tools/svc_armor_breadth.py` (writes) and
`tools/svc_loot_distribution.py` (the model + audit); this module is the sweep.

WHAT IT WRITES (all additive or a strict raise; nothing removed, nothing lowered):
  * the 3 aggregate armour masters `svc_unique_armor_{n,e,l}01` - one member that pays
    all five worn slots (helm/arms/torso/legs/shield) at equal weight, built from the
    same donor shape as R-180's weapon master;
  * per chest table: EVERY armour row lifted to the weapon row's own 40% (shipped
    torso/head 33, arms/legs 31, shield 30), its unique-armour members raised to 850
    (shipped 100-200 against ~1700 of static junk), and the armour master dropped into
    the first free armour-row member slot at 1700 (= 2 x ARMOR_UNIQUE_WEIGHT);
  * per chest table: the weapon row's aggregate master raised until the row is 50%
    legendary (WEAPON_ROW_LEGENDARY_SHARE), the mirror of what ARMOR_UNIQUE_WEIGHT
    produces on the armour rows - without it the uberorb apex donor family, whose weapon
    statics are 2500 against the DRX family's 1500, inverts to an 85%-armour surface;
  * per chest table: `unique_1h_*01` re-weighted to 3x its single-class siblings,
    because that ONE member pays THREE classes (axe/mace/sword) and carrying a
    spear's weight made each of them a third of a spear. That, plus the same
    correction inside R-180's weapon master and the softened theme biases in
    `svc_loot_breadth.THEMES`, is the whole of the "you overcorrected" fix.

ORDERING. Registered immediately AFTER `chest_loot_breadth`, for the same reason that
module runs late: it must sweep the FINAL table set, and it must see R-180's weapon
masters and widened rows already in place (it raises weights R-180 wrote, and its
`unique_1h` correction reads the members R-180 added).

SCOPE. In: every mod-owned gear chest (including the 3 `svc_uberorb_apex_*` tables that
back the red-uber Mystical Orb chests and Leinth's hoards) + the 3 DRX donors. There is
NO owner-based exclusion: the previous round deferred the apex tables to b79
`fix/orb-loot-breadth`, which provably does not widen armour on them and says so in its
own docstring. `apply()` now asserts WRITE SET == AUDIT SET and fails the build if they
ever diverge again. OUT BY EVIDENCE: general monster armour drops, measured and reported
for a Will decision, never changed here.

GATE (verify, post-finalization): `svc_armor_breadth.audit_db` over the final db -
per SURFACE, no class over its share cap, no starving class, no single item dominating
its class, every worn slot clearing its per-open floor, and the weapon:armour ratio
inside its cap. Standalone twin: `py tools/gate_loot_distribution.py <arz>`.
Negative tests: `py tools/debug/negtest_armor_breadth.py <arz>`.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD

MODULE_NAME = 'armor_loot_breadth'


def apply(db, tags):
    print("\n=== armor_loot_breadth: every worn slot pays at weapon-row parity ===")
    lk = SLB.Lookup(db)
    masters = SAB.ensure_armor_masters(db, lk)
    if not masters:
        print("  ARMOUR BREADTH: no armour masters authored (donors missing); "
              "sweep skipped.")
        return
    lk.refresh()

    donor_tiers = {SLB._n(p): t for t, p in SLB.DRX_DONORS.items()}
    targets = [t for t in SLB.chest_tables(db, lk) if SAB.in_scope(t)]

    widened = 0
    no_armor_row = []
    for table in targets + list(SLB.DRX_DONORS.values()):
        real = lk.real(table)
        if not real:
            continue
        tier = donor_tiers.get(SLB._n(table)) or SLB.infer_tier(db, real, lk)
        if tier is None:
            no_armor_row.append('%s (no tier-identifiable member)' % real)
            continue
        if not SAB.armor_groups(db, real):
            no_armor_row.append('%s (no armour row)' % real)
            continue
        if SAB.widen_armor_rows(db, real, tier, lk):
            widened += 1

    print("  ARMOUR BREADTH: %d chest table(s) in scope + %d DRX donor(s); armour rows "
          "lifted on %d (row chance -> %g%%, unique-armour weight -> %d, armour master "
          "at %d)." % (len(targets), len(SLB.DRX_DONORS), widened,
                       SAB.ARMOR_ROW_CHANCE, SAB.ARMOR_UNIQUE_WEIGHT,
                       SAB.ARMOR_MASTER_WEIGHT))
    if no_armor_row:
        print("  ARMOUR BREADTH: %d table(s) carry no armour row and were NOT lifted:"
              % len(no_armor_row))
        for s in no_armor_row:
            print("      %s" % s)
    # WRITE SET == AUDIT SET, asserted here rather than trusted. Every table this sweep
    # touched must be a table `all_surfaces` will audit; the previous round wrote the 3
    # DRX donors and the gate never looked at them, and it excluded the 3 apex orb
    # tables from BOTH, which is how a starving surface shipped twice.
    audited = {SLB._n(t) for (_l, ts, _w, _tr) in SAB.all_surfaces(db, lk) for t in ts}
    unaudited = sorted(SLB._n(t) for t in (targets + list(SLB.DRX_DONORS.values()))
                       if lk.real(t) and SLB._n(lk.real(t)) not in audited)
    if unaudited:
        for s in unaudited:
            print("  ARMOUR BREADTH: UNAUDITED WRITE %s" % s)
        raise SystemExit(
            "armor_loot_breadth FAILED: %d table(s) are written by this wave but are "
            "not in the distribution gate's surface set - a write the gate cannot see "
            "is exactly how R-180 stayed green through both of Will's reports"
            % len(unaudited))
    print("  ARMOUR BREADTH: write set == audit set (%d table(s) audited)." % len(audited))
    print("=== armor_loot_breadth done ===\n")


def verify(db, tags):
    """Fail-loud build-wide DISTRIBUTION gate over the FINAL assembled db."""
    problems, reports = SAB.audit_db(db)
    if problems:
        for p in problems[:24]:
            print("  DISTRIBUTION OFFENDER: %s" % p)
        raise SystemExit(
            "armor_loot_breadth gate FAILED: %d problem(s); a loot surface is skewed "
            "across classes, dominated by one item, or starving a worn slot (the "
            "\"i am not really seeing armor drops\" / \"4 scorpions tail spears\" "
            "defect class)" % len(problems))
    if not reports:
        raise SystemExit("armor_loot_breadth gate FAILED: no loot surface was audited "
                         "at all (scope rule broken - it must never be empty)")
    worst_ratio, worst_label = 0.0, '?'
    thin_ps, thin_ps_label = 1e9, '?'
    for rep in reports:
        wm = sum(rep['slot_mass'].get(s, 0.0) for s in SLD.WEAPON_SLOTS)
        am = sum(rep['slot_mass'].get(s, 0.0) for s in SLD.ARMOR_SLOTS)
        if am > 0 and wm / am > worst_ratio:
            worst_ratio, worst_label = wm / am, rep['label']
        spawn = rep.get('S_eff') or 1.0
        for s in SLD.ARMOR_SLOTS:
            v = rep['slot_mass'].get(s, 0.0) / spawn
            if v < thin_ps:
                thin_ps, thin_ps_label = v, '%s/%s' % (rep['label'], SLD.SLOT_LABEL[s])
    # Reported per SPAWN ITERATION, not per open, because that is the form asserted on
    # EVERY surface (D7b). The per-open floor D7 is asserted too, on every surface at or
    # above the volume it was derived at - saying "every worn slot clears 0.52/open"
    # while a low-volume orb sits at 0.28 would be a gate lying in its own PASS line.
    # ... and D7's reach is COUNTED, not implied. The round-2 vet found three surfaces
    # silently outside it (a 1.78e-15 float shortfall) while this very line said the floor
    # held "on every surface at or above S=10.58". Printing the number makes a surface
    # leaving D7 visible in the build log instead of invisible.
    n_d7 = sum(1 for r in reports if r and r.get('d7_asserted'))
    print("  armor_loot_breadth gate PASS: %d loot surface(s) audited; every worn slot "
          "clears %.4f piece(s) per SPAWN ITERATION (thinnest %s = %.4f) and %.2f/open "
          "on the %d surface(s) at or above S=%.2f (D7X: incl. the reference surface "
          "%s), no class over %.0f%% of a surface, no "
          "item over %.1fx its class uniform share, worst weapon:armour %.2f:1 on %s "
          "(cap %.2f)."
          % (len(reports), SLD.ARMOR_SLOT_FLOOR_PER_SPAWN, thin_ps_label, thin_ps,
             SLD.ARMOR_SLOT_FLOOR, n_d7, SLD.ARMOR_SLOT_FLOOR_REF_SPAWN,
             SLD.ARMOR_SLOT_FLOOR_REF_SURFACE,
             100.0 * SLD.MAX_CLASS_SHARE_AGGREGATE,
             SLD.MAX_ITEM_OVER_UNIFORM, worst_ratio, worst_label,
             SLD.MAX_WEAPON_ARMOUR_RATIO))
