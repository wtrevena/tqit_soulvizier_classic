r"""orb_armor_rows - the uber's MYSTICAL ORB pays ARMOUR too (BL-R181-DEBT-7).

WILL, VERBATIM (2026-08-10), the report this closes the last hole in:
  "also what about the armor? i am not really seeing armor drops like shields, chest
   plates, helmets, etc."
and the order R-220 was written to: orbs roll ALL item classes - armour included.

WHAT WAS LEFT UNDONE, quoted from the R-181 ship record rather than re-argued
---------------------------------------------------------------------------
R-181 gave every mod chest armour at weapon-row parity and shipped the per-surface
distribution gate. R-220 then widened FIFTEEN more loot tables - the uber mystical
orbs - and those fifteen live outside the `\svc\` folder R-181's ownership rule keys
on, so R-220 widened only their WEAPON row and their ARMOUR was owned by NOBODY.
MEASURED on the shipped build80 arz (`c5851a1a`), all fifteen starved:

    weapon:armour 3.45:1 .. 8.38:1        (cap 1.85:1)
    thinnest worn slot 0.007 .. 0.044     (D7 floor 0.52 pieces per open)

Both fail-loud gates were GREEN the entire time. That is the finding: a table no
module claims is a table no gate audits, and no THRESHOLD can catch that.

WHAT THIS MODULE WRITES - `svc_armor_breadth.widen_armor_rows`, the R-181 treatment
verbatim, once per in-scope orb table, and nothing else:
  * every ARMOUR row lifted to the weapon row's own 40% (donor shipped 26/31/32/33/30);
  * every unique-armour member raised to ARMOR_UNIQUE_WEIGHT (donor shipped 27/28
    against ~1700 of static junk);
  * the aggregate armour master `svc_unique_armor_{n,e,l}01` - one member paying all
    five worn slots at equal weight - into the first free armour-row member slot
    (always the shield row on these donors, which ship 2 of 6 members used);
  * the weapon row's own R-181 corrections, so lifting armour cannot INVERT a surface:
    `unique_1h`/`1h_all` re-weighted to 3x its single-class siblings (it pays three
    classes from one member slot) and the aggregate weapon master raised until the row
    is WEAPON_ROW_LEGENDARY_SHARE legendary.
Additive or a strict raise throughout: no member removed, no chance or weight lowered,
numSpawn equations untouched. Expected drops per open therefore strictly RISE, and what
changes inside a row is its COMPOSITION.

ORDER IS LOAD-BEARING: immediately AFTER `orb_loot_breadth`. Its weapon-row balance is
computed from the aggregate weapon master that R-220 puts in loot1, so running before
R-220 would find no master and silently skip the half of the treatment that keeps the
surface from inverting to 85% armour (the R-181 amendment's D6b finding, which was a
real shipped defect on the apex tables, not a hypothetical).

SCOPE IS R-220'S OWN DERIVATION, NEVER A LIST. `svc_armor_breadth.orb_scope` asks
`svc_orb_breadth.scope_tables` which tables the uber drop chains reach. A sixteenth orb
table, or a rewired chain, is swept and audited the day R-220 sees it - the alternative,
a typed list of fifteen names, is how this debt existed in the first place.

GATE. There is deliberately no distribution gate here: `armor_loot_breadth.verify` is
the one distribution gate and it now audits these tables like every other surface,
because `all_surfaces` covers them. What `verify()` below asserts is the OWNERSHIP half -
that the derivation and the sweep and the audit set still agree - plus the per-table
ratios, printed so the build log carries the numbers.
Standalone twin: `py tools/gate_loot_distribution.py <arz> --apply --verbose`.
Negative tests:  `py tools/debug/negtest_armor_breadth.py <arz>` (N8/N9 are this lane's).
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD

MODULE_NAME = ("orb armour rows - an uber's mystical orb pays every WORN SLOT at "
               "weapon-row parity (BL-R181-DEBT-7)")

# The fields this module is allowed to move, mirroring R-220's own scope proof: the
# chance + member fields of THIS TABLE'S OWN armour rows (read off `armor_groups`, never
# assumed to be 2/5/6 - the same refusal to assume a layout that `armor_groups` itself
# makes) plus `loot1Weight*`, the weapon row's two R-181 weight corrections. Anything
# else moving on an in-scope record is a bug, and apply() fails the build on it.
_ALLOWED_WEAPON_PREFIX = 'loot1Weight'

_IC = {'n': 'Epic', 'e': 'Legendary', 'l': 'Legendary'}


def _allowed_prefixes(groups):
    return tuple(['loot%d' % g for g in groups] + [_ALLOWED_WEAPON_PREFIX])


def _ratio(d, dist, table, tier):
    """(weapon mass, armour mass, thinnest worn slot) per open, at the table's tier."""
    p = SLD.ChestProfile(d, dist, table, 1, _IC[tier])
    bs = p.by_slot()
    wm = sum(bs.get(s, 0.0) for s in SLD.WEAPON_SLOTS)
    am = sum(bs.get(s, 0.0) for s in SLD.ARMOR_SLOTS)
    thin = min(bs.get(s, 0.0) for s in SLD.ARMOR_SLOTS)
    return wm, am, thin


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    lk = SLB.Lookup(db)

    # ── 1. the armour masters (idempotent; armor_loot_breadth normally wins) ──
    masters = SAB.ensure_armor_masters(db, lk, verbose=False)
    if not masters:
        raise SystemExit(
            "[orb_armor_rows] the aggregate armour masters could not be authored, so "
            "the orbs cannot be given a member that pays all five worn slots. "
            "`armor_loot_breadth` authors the same three records from the same "
            "idempotent builder and runs first, so this means the donor `all_l01` "
            "LootMasterTable is missing - a build-input problem, not something to "
            "skip past.")
    lk.refresh()

    # ── 2. scope, DERIVED from R-220 and printed (the wave report IS the log) ─
    scope = SAB.orb_scope(db, lk)
    if not scope:
        raise SystemExit(
            "[orb_armor_rows] SCOPE EMPTY: svc_orb_breadth derived no uber orb loot "
            "table. Sweeping nothing while reporting success is exactly how "
            "BL-R181-DEBT-7 shipped; R-220's own MIN_TABLES floor guards the same "
            "collapse on its side.")
    targets = []
    for _key, (table, tier) in sorted(scope.items()):
        real = lk.real(table)
        if not real:
            continue
        groups = SAB.armor_groups(db, real)
        if not groups:
            # Loud, never dropped: an orb table with no armour row at all would be a
            # NEW donor shape, and this module would be silently doing nothing to it.
            print("  ORB ARMOUR: NOTE %s carries no armour row and cannot be lifted; "
                  "the distribution gate still audits it." % SLB._n(real))
            continue
        targets.append((real, tier, groups))
    print("  ORB ARMOUR: %d uber orb loot table(s) derived, %d carry armour rows"
          % (len(scope), len(targets)))

    # ── 3. the before-image, for the scope proof and the printed deltas ──────
    d0 = SLD.Db(db)
    dist0 = SLD.Distributor(d0)
    before_num = {t: _ratio(d0, dist0, t, tier) for t, tier, _g in targets}
    before = {t: {k.split('###')[0]: list(tf.values)
                  for k, tf in (db.get_fields(t) or {}).items()}
              for t, _tier, _g in targets}

    # ── 4. the R-181 treatment, unchanged, once per table ────────────────────
    lifted = 0
    for real, tier, _groups in targets:
        ch = SAB.widen_armor_rows(db, real, tier, lk)
        if ch:
            lifted += 1
            print("    %-46s [%s] %s"
                  % (SLB._n(real).rsplit('\\', 1)[-1], tier, '; '.join(ch)))
    print("  ORB ARMOUR: armour rows lifted on %d of %d table(s) (row chance -> %g%%, "
          "unique-armour weight -> %d, armour master at %d)"
          % (lifted, len(targets), SAB.ARMOR_ROW_CHANCE, SAB.ARMOR_UNIQUE_WEIGHT,
             SAB.ARMOR_MASTER_WEIGHT))

    # ── 5. SCOPE PROOF: only armour-row + weapon-weight fields moved, never down
    illegal = []
    for real, _tier, groups in targets:
        after = {k.split('###')[0]: list(tf.values)
                 for k, tf in (db.get_fields(real) or {}).items()}
        base = SLB._n(real).rsplit('\\', 1)[-1]
        allowed = _allowed_prefixes(groups)
        for field in sorted(set(before[real]) | set(after)):
            a, b = before[real].get(field, []), after.get(field, [])
            if a == b:
                continue
            if not field.startswith(allowed):
                illegal.append('%s.%s' % (base, field))
                continue
            try:
                if float(b[0]) < float(a[0]):
                    illegal.append('%s.%s LOWERED %s -> %s' % (base, field, a[0], b[0]))
            except (TypeError, ValueError, IndexError):
                pass          # a name field: additive by construction, checked above
    if illegal:
        raise SystemExit(
            "[orb_armor_rows] SCOPE PROOF FAILED: %d field(s) outside the allowed set "
            "moved, or moved DOWN (allowed: the armour rows loot2/loot5/loot6 and the "
            "weapon row's loot1Weight* corrections, raises only): %s. An orb's identity "
            "- numSpawn equations, the relic row, the potion row, the mesh, the gold "
            "generator and the level equation - must come through this sweep "
            "byte-unchanged." % (len(illegal), sorted(illegal)[:12]))

    # ── 6. the numbers, before -> after, in the build log ────────────────────
    d1 = SLD.Db(db)
    dist1 = SLD.Distributor(d1)
    print("  ORB ARMOUR: per-open legendary mass, before -> after "
          "(weapon:armour, thinnest worn slot; D7 floor %.2f, D6 cap %.2f:1)"
          % (SLD.ARMOR_SLOT_FLOOR, SLD.MAX_WEAPON_ARMOUR_RATIO))
    for real, tier, _groups in targets:
        w0, a0, t0 = before_num[real]
        w1, a1, t1 = _ratio(d1, dist1, real, tier)
        print("      %-46s [%s]  w:a %6.2f -> %5.2f   thin %.3f -> %.3f"
              % (SLB._n(real).rsplit('\\', 1)[-1], tier,
                 (w0 / a0) if a0 else float('inf'), (w1 / a1) if a1 else float('inf'),
                 t0, t1))
    print("  ORB ARMOUR: scope proof PASS - %d record(s) watched, only the armour rows "
          "and the weapon row's two R-181 weight corrections moved, nothing lowered, "
          "no member removed." % len(targets))
    print("=== orb_armor_rows done ===\n")


def verify(db, tags):
    """OWNERSHIP gate. The distribution numbers are `armor_loot_breadth.verify`'s job -
    it audits these tables now - so what is asserted here is the thing that was missing:
    that every table the orb derivation produces is actually INSIDE that audit set, and
    that no loot table written anywhere in this build escaped it."""
    lk = SLB.Lookup(db)
    surfaces = SAB.all_surfaces(db, lk)
    audited = {SLB._n(t) for (_l, ts, _w, _tr) in surfaces for t in ts}
    scope = SAB.orb_scope(db, lk)
    missing = sorted(k for k, (t, _tier) in scope.items()
                     if SLB._n(lk.real(t) or t) not in audited)
    if missing:
        raise SystemExit(
            "orb_armor_rows gate FAILED: %d uber orb loot table(s) are outside the "
            "distribution gate's surface set: %s. That is BL-R181-DEBT-7 verbatim - "
            "R-220 writes the table, no surface audits it, and both loot gates stay "
            "green while it starves." % (len(missing), missing[:8]))
    problems = SAB.ownership_problems(db, lk, surfaces=surfaces)
    if problems:
        for p in problems[:16]:
            print("  OWNERSHIP OFFENDER: %s" % p)
        raise SystemExit(
            "orb_armor_rows gate FAILED: %d loot table(s) are written by this build and "
            "audited by no distribution surface. Coverage must be DERIVED from the "
            "writes, never from a list of names - a list is how fifteen live surfaces "
            "starved through two green gates." % len(problems))
    print("  orb_armor_rows gate PASS: %d uber orb loot table(s) derived, every one "
          "inside the distribution surface set (%d surfaces); every loot table written "
          "in this build is audited by a surface or EXEMPT with a reason."
          % (len(scope), len(surfaces)))
