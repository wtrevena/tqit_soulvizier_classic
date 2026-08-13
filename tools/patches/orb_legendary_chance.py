r"""orb_legendary_chance - uber-orb legendary/blue chance BY DIFFICULTY (R-242, Will
2026-08-12). SUPERSEDES R-241's flat 21.2% apex demotion and CLOSES BL-R241-DEBT-1.

WILL, VERBATIM (2026-08-12)
  part 1: "all the orbs that uber monsters drop should have a 50% chance of dropping a
   legendary item on epic, a 75% of dropping a legendary item on legendary, a 0% chance
   of dropping a legendary item on normal, but a 75% chance of dropping a blue item on
   normal (this is a sub legendary item, idk what the name of this class of item is but
   they show up blue)"
  part 2: "Note that Leinth and the toxeus variants keep their current higher / better
   orbs / better drop rates / more loot"

WHAT THIS MODULE WRITES
-----------------------
On the 15 GENERAL uber-orb tables (uberorb_default_* + boss_charon_*01b): a UNIFORM
loot1/2/5/6 chance, CALIBRATED per table so P(>=1 target-classification per open) hits
Will's number for that difficulty - Epic(blue) 75% on Normal (with legendary GEAR held
at 0 by the tier law), Legendary 50% on Epic, Legendary 75% on Legendary. Nothing else:
loot3/loot4, every member, every weight and numSpawn are left verbatim, so breadth,
distribution and the relic law survive and the variety still lands WHEN one rolls.

On the 3 EXCLUDED apex tables (svc_uberorb_apex_{n,e,l}01c, the shared Toxeus + Leinth
loot): the guaranteed relic row is demoted 100 -> 21.2 exactly as R-241 did, which is
their build85 state - so they stay byte-identical to build85 (Will part 2). Letting that
row revert to 100 would both change the bytes and re-arm a guaranteed legendary row.

WHY IT IS REGISTERED HERE - immediately AFTER `loot_volume_trim`:
  1. `armor_loot_breadth` SKIPS the guaranteed row by design and runs far earlier, so it
     must still see the apex group 4 at 100 or the armour sweep would rewrite a theme row.
  2. The readings are measured against R-240's TRIMMED spawn volume, so the volume trim
     must already have landed.

HONEST RESIDUE (`BL-R242-DEBT-1`, awaiting Will's A/B call): freezing the excluded apex
at build85 makes it WEAKER than the general orbs on Legendary legendary-chance (apex
60.9% vs general 75%), an inversion of "keep their better orbs". This gate PRINTS it on
every run and does NOT red on it - the apex's edge is now volume + richer loot4, and
lifting it above the general target is a follow-up lane, Will's call.

GATE: `verify()` runs the whole R-242 contract on the FINAL db. Standalone twin:
`py tools/gate_orb_legendary.py <arz>` (`--census`, `--calibrate`, `--apply`).
Negatives: `py tools/debug/negtest_orb_legendary.py <arz>` - planted in BOTH directions,
because a rate-by-difficulty ruling has several ways to be wrong.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB
import svc_orb_legendary as SOL

MODULE_NAME = ("uber-orb legendary/blue chance by difficulty - general orbs 0/50/75, "
               "Toxeus+Leinth excluded (R-242)")


def _base_rows(required, who):
    """The base-game Monster.tpl rows, via red_uber_orbs' cached loader. Never fatal here
    (every record this module writes lives in the mod overlay), so a missing base arz
    downgrades LOUDLY rather than silently narrowing the roster."""
    try:
        import red_uber_orbs as RUO
    except ImportError as exc:                       # pragma: no cover - packaging
        print("  [orb_legendary_chance] WARNING cannot import red_uber_orbs (%s); the "
              "uber roster runs MOD-ONLY this build. No silent pass: this line IS the "
              "downgrade." % exc)
        return None
    rows = RUO.load_base_rows(required=required, who=who)
    if not rows:
        print("  [orb_legendary_chance] WARNING base-game universe unavailable; the uber "
              "roster runs MOD-ONLY this build. No silent pass: this line IS the downgrade.")
    return rows


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    lk = SLB.Lookup(db)
    base_rows = _base_rows(required=False, who='orb_legendary_chance.apply()')

    scope0 = SOL.orb_tables(db, lk, base_rows)
    if not scope0:
        raise SystemExit(
            "[orb_legendary_chance] SCOPE EMPTY: svc_orb_breadth derived no uber-orb loot "
            "table. Rating nothing while reporting success is exactly how BL-R181-DEBT-7 "
            "shipped fifteen starving surfaces through two green gates.")

    # ── 0. the partition cross-check FIRST: a rewired apex consumer must red here, not
    #    silently move scope (ROSTER_PINNED discipline). ──────────────────────────────
    px = SOL.partition_problems(db, lk, base_rows, scope0)
    if px:
        for p in px:
            print("  ORB PARTITION OFFENDER: %s" % p)
        raise SystemExit(
            "[orb_legendary_chance] the derived Toxeus/Leinth exclusion set no longer "
            "matches the pinned apex roster (%d finding(s)). A general orb was rewired "
            "onto excluded loot, or a new apex table exists - decide deliberately." % len(px))

    # ── 1. the partition in the build log ───────────────────────────────────────────
    SOL.census(db, lk, base_rows, scope0)

    before = {real: {k.split('###')[0]: list(tf.values)
                     for k, tf in (db.get_fields(real) or {}).items()}
              for _k, (real, _t) in scope0.items()}

    # ── 2. the wave ─────────────────────────────────────────────────────────────────
    general_changes, apex_changes = SOL.apply_wave(db, lk, base_rows, verbose=True,
                                                   scope=scope0)
    lk.refresh()

    # ── 3. SCOPE PROOF: only a loot{g}Chance moved, and only on the intended rows -
    #    general loot1/2/5/6, apex loot4. A member, weight, spawn eq or a stray row means
    #    this lane is silently redoing R-180/R-181/R-220/R-240's work. ────────────────
    allowed = set()
    for (real, _t, moves) in general_changes:
        for (g, _o, _n) in moves:
            allowed.add((real, 'loot%dChance' % g))
    for (real, _t, g, _o, _n) in apex_changes:
        allowed.add((real, 'loot%dChance' % g))
    illegal = []
    for real, was in before.items():
        now = {k.split('###')[0]: list(tf.values)
               for k, tf in (db.get_fields(real) or {}).items()}
        base = SLB._n(real).rsplit('\\', 1)[-1]
        for field in sorted(set(was) | set(now)):
            if was.get(field, []) == now.get(field, []):
                continue
            ok = (field.startswith('loot') and field.endswith('Chance')
                  and (real, field) in allowed)
            if not ok:
                illegal.append('%s.%s %r -> %r'
                               % (base, field, was.get(field), now.get(field)))
    if illegal:
        raise SystemExit(
            "[orb_legendary_chance] SCOPE PROOF FAILED: %d field change(s) outside the "
            "calibrated general rows / demoted apex row: %s. This module is allowed to "
            "change how OFTEN an orb gear row fires and nothing else."
            % (len(illegal), sorted(illegal)[:12]))

    # ── 4. the numbers, in the build log ────────────────────────────────────────────
    SOL.calibrate(db, lk, base_rows, scope0)
    print("  ORB LEGENDARY: scope proof PASS - %d general table(s) calibrated, %d apex "
          "row(s) frozen at build85, only loot{g}Chance moved."
          % (len(general_changes), len(apex_changes)))
    print("=== orb_legendary_chance done ===\n")


def verify(db, tags):
    """The R-242 contract on the FINAL db (a verify(), not an apply()-time gate, so it
    measures the rate the player actually gets after every other loot module has run)."""
    lk = SLB.Lookup(db)
    base_rows = _base_rows(required=False, who='orb_legendary_chance.verify()')
    report = {}
    problems = SOL.problems(db, lk, base_rows, report=report)
    notice = SOL.inversion_notice(db, lk, base_rows)
    if notice:
        print("  " + "!" * 74)
        for ln in notice.split("\n"):
            print("  !! " + ln.strip())
        print("  " + "!" * 74)
    if problems:
        for p in problems[:16]:
            print("  ORB LEGENDARY OFFENDER: %s" % p)
        raise SystemExit(
            "orb_legendary_chance gate FAILED: %d uber-orb legendary/blue finding(s). "
            "Will 2026-08-12: general orbs 0%% leg + 75%% blue on normal, 50%% leg on "
            "epic, 75%% leg on legendary; Leinth + Toxeus kept byte-identical to build85."
            % len(problems))
    print("  orb_legendary_chance gate PASS: %s. Every general orb sits in its "
          "per-difficulty band and every excluded apex is byte-frozen at build85; "
          "residual inversion debt: BL-R242-DEBT-1." % SOL.pass_line(report))
