r"""orb_legendary_chance - the uber orbs stop guaranteeing legendaries (R-241).

WILL, VERBATIM (2026-08-11). This ruling SUPERSEDES the b79 "orbs stay generous
relative to chests" precedent wherever the two collide, and it says so in
`docs/WILL_RULINGS.md` rather than being resolved quietly here:
  "you made the orbs way too good... those dont need to have guaranteed legendary
   drops, they should just have a chance to drop legendary items, but a low chance."

THE NUMBER HE ASKED FOR, MEASURED ON THE SHIPPED b83 ARZ `44499f56`
--------------------------------------------------------------------
THREE guaranteed-legendary rows in the entire orb surface - ONE per difficulty - and
all three are the same row on the same family: group 4 of `svc_uberorb_apex_{n,e,l}01c`
at chance 100%, where its five sibling orb tables run the identical amulet/relic/ring
row at 12.7% or 21.2%. None of the three is a PURE legendary row (0.44% / 5.25% / 6.28%
legendary by weight). Full census: `py tools/gate_orb_legendary.py <arz> --census`.

THE ROW COUNT WAS NOT WHERE THE GUARANTEE LIVED. Per ONE orb open on the shipped b83
arz: Epic 2.58-6.29 legendary items (93.6-99.9% chance of at least one), Legendary
3.74-8.43 (98.4-99.99%). Six independent loot groups over 5.06-10.58 spawn iterations
produce a guarantee with no 100% row involved, which is why R-220's breadth gate,
R-181's distribution gate and R-240's volume gate were all green while Will was looking
at a vending machine.

WHAT THIS MODULE WRITES
------------------------
ONE field per guaranteed row: `loot{g}Chance`, on exactly the rows the census returns,
demoted to the richest NON-guaranteed chance that same row already carries elsewhere in
the orb family (21.2%, `boss_charon_*01b`'s value). The target is DERIVED from the
shipped bytes and cross-checked against the value this contract was measured on, so a
demotion can never silently land somewhere nobody chose. Three records, three fields.

Combined with R-240's volume trim (previous registry slot), one orb open now pays:
  Normal 0.001-0.004 legendary | Epic 0.451-0.622 | Legendary 0.699-0.846
i.e. AT MOST ONE LEGENDARY ITEM PER OPEN on Legendary difficulty, against 8.43 shipped -
a 90% cut, with breadth and distribution untouched so the variety survives WHEN one rolls.

WHAT IT DELIBERATELY DOES NOT DO
---------------------------------
P(at least one legendary) lands at 54-61% on Legendary, and that is not yet "a low
chance". After the trim an orb pays ~2.06 items and ~40% of its Legendary-tier drop mass
IS legendary-classified, because R-180/R-220 weighted `svc_unique_weapons_l01` /
`svc_unique_armor_l01` at ~47-50% of the weapon and shield rows to buy the class breadth
Will asked for in the same fortnight. Moving it further means scaling those rows'
chances, which divides `svc_loot_distribution` D7b (worn-slot armour per SPAWN
ITERATION, asserted on all 63 surfaces) by the same factor and reds armour parity on
every orb - or scaling only the legendary-heavy rows, which moves D3/D4 and D6 instead.
Either way it is a COMPOSITION decision inside R-180/R-181/R-220's scope, priced for
Will as `BL-R241-DEBT-1` rather than taken by a rate lane. The ceilings this module
gates on are set where the AUTHORISED levers actually reach, so the gate is a true
ratchet and not an aspiration nothing enforces.

WHY IT IS REGISTERED HERE - immediately AFTER `loot_volume_trim`, before the no-op
`visuals`:
  1. `armor_loot_breadth` SKIPS the guaranteed row by design (`is_guaranteed_group`,
     the WARDEN-theme lesson). It runs far earlier, sees group 4 still at 100%, and
     leaves it to the theme - exactly as intended. Demoting BEFORE it would hand that
     row to the armour sweep and let a later pass rewrite a theme, which is the defect
     `armor_groups`' docstring exists to prevent.
  2. R-241's readings are measured against R-240's TRIMMED spawn volume, so the volume
     trim must already have landed when this module's verify() reports numbers.

GATE: `verify()` below runs the whole R-241 contract (O1-O5) on the FINAL db, so a later
module that re-inflates an orb row reds here and gets named. Standalone twin:
`py tools/gate_orb_legendary.py <arz>` (`--census` for Will's number, `--calibrate` to
re-derive every threshold, `--apply` on a pre-wave arz).
Negatives: `py tools/debug/negtest_orb_legendary.py <arz>` - planted in BOTH directions,
because a rate ruling has two ways to be wrong.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB
import svc_orb_legendary as SOL

MODULE_NAME = ("uber-orb legendary chance - an orb has a chance at a legendary, not a "
               "guarantee (R-241)")

# The ONLY field this module may move, and only on an orb table. Everything else on a
# loot table is that surface's identity: its members, its weights, its spawn volume,
# its relic tier. Breadth and distribution must survive verbatim, so that WHEN a
# legendary does roll, the variety b75-b83 shipped is still the thing that rolls.
_ALLOWED_PREFIX = 'loot'
_ALLOWED_SUFFIX = 'Chance'


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    lk = SLB.Lookup(db)

    # The orb surface is derived ONCE and reused for the census, the wave and the
    # calibration. Deriving it walks all 51k records looking for Monster templates, and
    # this module needs it three times in a row; the scope is a function of the
    # proxy -> pool -> chest -> table WIRING, which this module cannot touch (it writes
    # one `loot{g}Chance` on a table already in the set), so reuse is sound rather than
    # a shortcut. `verify()` deliberately re-derives on the FINAL db.
    scope0 = SOL.orb_tables(db, lk)
    if not scope0:
        raise SystemExit(
            "[orb_legendary_chance] SCOPE EMPTY: svc_orb_breadth derived no uber-orb "
            "loot table. Demoting nothing while reporting success is exactly how "
            "BL-R181-DEBT-7 shipped fifteen starving surfaces through two green gates.")

    # ── 1. the census FIRST, in the build log, because Will asked for the number ──
    SOL.census(db, lk, scope=scope0)

    before = {real: {k.split('###')[0]: list(tf.values)
                     for k, tf in (db.get_fields(real) or {}).items()}
              for _k, (real, _t) in scope0.items()}

    # ── 2. the wave ──────────────────────────────────────────────────────────
    changed = SOL.apply_wave(db, lk, verbose=True, scope=scope0)
    lk.refresh()

    # ── 3. SCOPE PROOF: only a loot{g}Chance moved, and only on a demoted row ──
    demoted = {(real, 'loot%dChance' % g) for (real, _t, g, _o, _n) in changed}
    illegal = []
    for real, was in before.items():
        now = {k.split('###')[0]: list(tf.values)
               for k, tf in (db.get_fields(real) or {}).items()}
        base = SLB._n(real).rsplit('\\', 1)[-1]
        for field in sorted(set(was) | set(now)):
            if was.get(field, []) == now.get(field, []):
                continue
            ok = (field.startswith(_ALLOWED_PREFIX) and field.endswith(_ALLOWED_SUFFIX)
                  and (real, field) in demoted)
            if not ok:
                illegal.append('%s.%s %r -> %r'
                               % (base, field, was.get(field), now.get(field)))
    if illegal:
        raise SystemExit(
            "[orb_legendary_chance] SCOPE PROOF FAILED: %d field change(s) outside the "
            "demoted guaranteed rows: %s. This module is allowed to change how OFTEN a "
            "guaranteed orb row fires and nothing else - the moment it touches a member, "
            "a weight, a spawn equation or a row the census did not name, it is silently "
            "redoing R-180/R-181/R-220/R-240's work, and the gates that run after it "
            "would be validating a different wave than the one anyone reviewed."
            % (len(illegal), sorted(illegal)[:12]))

    # ── 4. the numbers, in the build log, because the report IS the log ──────
    SOL.calibrate(db, lk, scope=scope0)
    print("  ORB LEGENDARY: scope proof PASS - %d orb table(s) watched, %d guaranteed "
          "row(s) demoted, only their own loot{g}Chance moved."
          % (len(before), len(changed)))
    print("=== orb_legendary_chance done ===\n")


def verify(db, tags):
    """The R-241 contract (O1-O5) on the FINAL db.

    A verify() rather than an apply()-time gate for the R-240 reason: every other loot
    module has already run by then, so what this measures is the legendary rate the
    player actually gets - not the rate this module left behind a moment before
    something else moved it.
    """
    lk = SLB.Lookup(db)
    report = {}
    problems = SOL.problems(db, lk, report=report)
    # Same standing notice the standalone audit prints, from the same function, before
    # the verdict on either path: the build log is where the ship lane looks, so the
    # undischarged half of the ruling has to be legible there too.
    notice = SOL.undischarged_notice(report)
    if notice:
        print("  " + "!" * 74)
        for ln in notice.split("\n"):
            print("  !! " + ln.strip())
        print("  " + "!" * 74)
    if problems:
        for p in problems[:16]:
            print("  ORB LEGENDARY OFFENDER: %s" % p)
        raise SystemExit(
            "orb_legendary_chance gate FAILED: %d uber-orb legendary finding(s). Will "
            "2026-08-11: \"those dont need to have guaranteed legendary drops, they "
            "should just have a chance to drop legendary items, but a low chance.\" The "
            "ruling has two sides and this gate holds both - an orb may not guarantee a "
            "legendary, and it may not stop being able to pay one." % len(problems))
    print("  orb_legendary_chance gate PASS: %s. Both mirrors hold: a legendary is "
          "still possible on every Epic/Legendary orb (floors %s) and no orb has been "
          "reduced to an empty box (floor %.2f items/open). Residual chance-half debt: "
          "BL-R241-DEBT-1."
          % (SOL.pass_line(report), SOL.ORB_MIN_P_LEGENDARY,
             SOL.ORB_MIN_DROPS_PER_OPEN))
