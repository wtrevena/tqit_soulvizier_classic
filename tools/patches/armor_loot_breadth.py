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
    the first free armour-row member slot at 800;
  * per chest table: `unique_1h_*01` re-weighted to 3x its single-class siblings,
    because that ONE member pays THREE classes (axe/mace/sword) and carrying a
    spear's weight made each of them a third of a spear. That, plus the same
    correction inside R-180's weapon master and the softened theme biases in
    `svc_loot_breadth.THEMES`, is the whole of the "you overcorrected" fix.

ORDERING. Registered immediately AFTER `chest_loot_breadth`, for the same reason that
module runs late: it must sweep the FINAL table set, and it must see R-180's weapon
masters and widened rows already in place (it raises weights R-180 wrote, and its
`unique_1h` correction reads the members R-180 added).

SCOPE. In: every mod-owned gear chest + the 3 DRX donors. OUT BY OWNER: the
`svc_uberorb_*` orb tables, owned by the concurrent b79 `fix/orb-loot-breadth` lane -
listed loudly on every run, never silently skipped. OUT BY EVIDENCE: general monster
armour drops, measured and reported for a Will decision, never changed here.

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
    orb_lane = [t for t in SLB.chest_tables(db, lk) if SAB.is_orb_lane_table(t)]

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
    if orb_lane:
        # Never silent: these belong to another lane, and saying so on every build is
        # what keeps the boundary from turning into a hole (the R-200 lesson).
        print("  ARMOUR BREADTH: %d orb table(s) NOT touched - owned by the b79 "
              "fix/orb-loot-breadth lane (BL-R181-DEBT-1):" % len(orb_lane))
        for s in orb_lane:
            print("      %s" % SLB._n(s).rsplit('\\', 1)[-1])
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
    thinnest, thin_label = 1e9, '?'
    for rep in reports:
        wm = sum(rep['slot_mass'].get(s, 0.0) for s in SLD.WEAPON_SLOTS)
        am = sum(rep['slot_mass'].get(s, 0.0) for s in SLD.ARMOR_SLOTS)
        if am > 0 and wm / am > worst_ratio:
            worst_ratio, worst_label = wm / am, rep['label']
        for s in SLD.ARMOR_SLOTS:
            v = rep['slot_mass'].get(s, 0.0)
            if v < thinnest:
                thinnest, thin_label = v, '%s/%s' % (rep['label'], SLD.SLOT_LABEL[s])
    print("  armor_loot_breadth gate PASS: %d loot surface(s) audited; every worn slot "
          "clears %.2f/open (thinnest %s = %.2f), no class over %.0f%% of a surface, no "
          "item over %.1fx its class uniform share, worst weapon:armour %.2f:1 on %s (cap %.2f)."
          % (len(reports), SLD.ARMOR_SLOT_FLOOR, thin_label, thinnest,
             100.0 * SLD.MAX_CLASS_SHARE_AGGREGATE,
             SLD.MAX_ITEM_OVER_UNIFORM, worst_ratio, worst_label,
             SLD.MAX_WEAPON_ARMOUR_RATIO))
