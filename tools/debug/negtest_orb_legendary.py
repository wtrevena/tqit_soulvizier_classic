r"""negtest_orb_legendary.py - PLANTED NEGATIVES for the uber-orb legendary contract
(R-231).

Will 2026-08-11: "you made the orbs way too good... those dont need to have guaranteed
legendary drops, they should just have a chance to drop legendary items, but a low
chance."

A RATE RULING HAS TWO WAYS TO BE WRONG, so these plant in BOTH directions - too much
(the defect Will reported) and too little (this lane's own possible over-correction). A
gate that only reds one side would let the next wave quietly delete the reward while
reporting a clean sweep: that is the b80 D6b mirror lesson and R-230's N5.

  M1  the apex guaranteed row restored to chance 100                     -> O1
       (Will's ruling, literally: the three rows this wave demoted)
  M2  a guaranteed-legendary row planted on an ORDINARY orb, a table that never had
      one, to prove O1 is a PROPERTY of the surface and not a memory of three
      apex records                                                       -> O1
  M3  one orb's numSpawn restored to its shipped volume                  -> O2 + O3
       (the guarantee Will actually hit did not live in a 100% row - it lived in
        5.06-10.58 spawn iterations, so the battery has to plant it there)
  M4  THE MIRROR - every row's legendary weight MOVED onto that row's least-legendary
      member, which is what `BL-R231-DEBT-1` option (B) would do badly. Row totals are
      preserved, so items-per-open never moves and O4 fires ALONE      -> O4, alone
  M5  THE TRUNCATION MIRROR - the same shift, tuned to sit ABOVE the floor on the
      continuous reading and BELOW it under integer truncation           -> O4, and
       green on the continuous reading, which is why O4 is measured on the truncated
       one (BL-R230-DEBT-5)
  M6  THE SECOND MIRROR - every group chance scaled down until the orb is an empty
      box, which satisfies O2/O3/O4 the cheap way                        -> O5
  M7  the derived demotion target moved out from under the contract, so a future
      retune of `boss_charon_*01b` cannot silently relocate the demotion -> SystemExit

  Q1/Q2/Q3 positive controls: the wave is green; the apex orb is still the RICHEST orb
      (the b79 precedent survives as far as Will's newer ruling leaves it standing); and
      the coexisting breadth/distribution gates stay green on the same database, which
      is the "variety survives at lower volume" claim proved rather than asserted.

Usage: py tools/debug/negtest_orb_legendary.py <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD
import svc_loot_volume as SLV
import svc_orb_legendary as SOL
import svc_orb_breadth as SOB

# The apex family, whose group 4 is the row this wave demotes. Named here so M1 is a
# verbatim revert of what the wave did, not an invented plant.
APEX = {'n': r'records\item\loottables\svc\svc_uberorb_apex_n01c.dbr',
        'e': r'records\item\loottables\svc\svc_uberorb_apex_e01c.dbr',
        'l': r'records\item\loottables\svc\svc_uberorb_apex_l01c.dbr'}
# An ORDINARY orb that has never had a guaranteed row - M2's target, so O1 is proved
# to be a sweep over the derived surface rather than three remembered records.
ORDINARY_L = r'records\xpack\item\containers\loot tables\uberorb_default_l01c.dbr'
# The shipped (pre-R-230) spawn multipliers of that same table, so M3 is a verbatim
# revert too. MEASURED on b83: `(2+(1.2*numberOfPlayers))*1.58` both sides -> S 5.06.
SHIPPED_BRACKET = None      # read from the record at plant time; see `_shipped_eq`

# ── M4/M5: HOW THE MIRROR HAS TO BE PLANTED, and the first draft that did not work ──
# The obvious plant - "scale every legendary-bearing member's weight down" - is BLIND,
# and it was written, run, and came back GREEN before this comment existed. The reason
# is worth keeping: on an orb row essentially EVERY member is mixed (the level-banded
# `static_all_l01c` pool carries legendary too), so scaling them all by the same factor
# leaves each member's SHARE of the row identical and the legendary rate does not move.
# A rate is a ratio; a plant that scales a ratio's numerator and denominator together
# plants nothing.
#
# What DOES move the rate is what option (B) of `BL-R231-DEBT-1` would actually do:
# move legendary weight onto a LESS legendary member. So the plant redistributes -
# every above-average-legendary member of every live row gives (1-f) of its weight to
# that row's LEAST legendary member. The row's TOTAL weight is unchanged, so drops per
# open stay at 2.056 and O5 stays green: O4 fires ALONE, which is what makes the case
# prove O4 rather than prove O5 twice.
#
# M5's f is SWEPT, not chosen: the usable band is exactly the gap between the two spawn
# models, so the value taken maximises the SMALLER margin, and the whole sweep is
# recorded so the next reader sees the band instead of trusting a number. MEASURED on
# `uberorb_default_l01c` [l], O4 floor 0.25, 14 members moved every time:
#     f      drops   O4 continuous          O4 truncated           findings
#     0.32   2.056   0.2402 RED             0.2166 RED             O4
#     0.33   2.056   0.2466 RED             0.2225 RED             O4
#     0.34   2.056   0.2534 green by 0.0034 0.2287 RED by 0.0213   O4
#     0.35   2.056   0.2601 green by 0.0101 0.2349 RED by 0.0151   O4    <- taken
#     0.36   2.056   0.2667 green by 0.0167 0.2409 RED by 0.0091   O4
#     0.37   2.056   0.2729 green by 0.0229 0.2467 RED by 0.0033   O4
#     0.38   2.056   0.2796 green          0.2528 green            none
# 0.35 maximises min(margin) at 0.0101. Note what the sweep also proves: drops NEVER
# move, so no other check fires anywhere in the band - which is precisely why a floor
# measured on the lenient model would have shipped this. If a future retune moves the
# surface out of the band the case reports BLIND rather than passing quietly.
M5_WEIGHT_SHIFT = 0.35
# M4 keeps nothing back - the full shift, both readings RED (0.0011 / 0.0010), the
# plain mirror with no band required.
M4_WEIGHT_SHIFT = 0.00
# M6 - every group chance scaled until the orb pays under the 1.50 items/open floor.
M6_CHANCE_SCALE = 0.30


def load_fixed(path):
    """The arz with BOTH waves applied, in registry order - which is the database the
    contract is written against. R-230 first: R-231's readings are measured against the
    trimmed spawn volume, so a battery that skipped it would be testing a surface that
    never ships."""
    db = ArzDatabase.from_arz(Path(path))
    if not SLV.already_applied(db):
        SLV.apply_wave(db, verbose=False)
    lk = SLB.Lookup(db)
    SOL.apply_wave(db, lk, verbose=False)
    lk.refresh()
    return db, lk


def _must(lk, path, why):
    """Resolve a record or DIE. Every plant goes through this.

    A plant that silently misses reports the gate as BLIND, which is an accusation
    against working code and the most expensive way for a negative battery to be wrong
    (R-230's own first draft did exactly that, twice)."""
    real = lk.real(path)
    if not real:
        raise SystemExit(
            "negtest plant could not resolve %r (%s). The plant would have written "
            "NOTHING and the case would have reported the gate as blind." % (path, why))
    return real


def codes(problems, prefix):
    return [p for p in problems if p.startswith(prefix + ' ')]


def _row_members(db, d, dist, real, g):
    """[(member_index, weight, legendary_share)] for one live row, DERIVED - so a retune
    that moves the legendary weight into different members moves the plant with it."""
    members = []
    for i in range(1, 7):
        nm = SLB._sc(db.get_field_value(real, 'loot%dName%d' % (g, i)))
        wt = SLB._sc(db.get_field_value(real, 'loot%dWeight%d' % (g, i)))
        if not (isinstance(nm, str) and nm.strip()):
            continue
        try:
            w = float(wt)
        except (TypeError, ValueError):
            continue
        if w <= 0:
            continue
        leg = sum(q for it, q in dist.dist(nm).items()
                  if str(d.gv(it, 'itemClassification') or '') == SOL.LEGENDARY)
        members.append((i, w, leg))
    return members


def _shift_legendary_weight(db, lk, table, f):
    """Move (1-f) of every ABOVE-AVERAGE-legendary member's weight onto its row's LEAST
    legendary member, on every live row of `table`.

    The row's TOTAL weight is preserved, so items-per-open does not move and O5 stays
    green: O4 fires alone, which is what makes the case prove O4. See the block comment
    on M5_WEIGHT_SHIFT for why the obvious "scale the legendary members down" plant is
    blind - a rate is a ratio, and scaling every member of a row leaves it unchanged."""
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    real = _must(lk, table, 'legendary-shift plant target')
    moved = 0
    for (g, _c, _s) in SOL.group_profile(d, dist, real):
        members = _row_members(db, d, dist, real, g)
        if len(members) < 2:
            continue
        sink = min(members, key=lambda m: m[2])
        total_w = sum(w for _i, w, _l in members)
        avg = sum(w * leg for _i, w, leg in members) / total_w
        pot = 0.0
        for (i, w, leg) in members:
            if leg > avg and i != sink[0]:
                keep = max(1.0, round(w * f))
                pot += (w - keep)
                db.set_field(real, 'loot%dWeight%d' % (g, i), keep)
                moved += 1
        if pot > 0:
            db.set_field(real, 'loot%dWeight%d' % (g, sink[0]), round(sink[1] + pot))
    db._modified.add(real)
    if not moved:
        raise SystemExit("negtest M4/M5 plant moved no weight on %s - the plant would "
                         "have written nothing and the case would have reported the "
                         "gate as blind." % table)


def _shipped_eq(db, lk, table):
    """The table's own bracket, read from the record rather than typed, so M3 restores
    a real shipped volume even if the bracket is retuned."""
    real = _must(lk, table, 'numSpawn revert target')
    p = SLV.parse_eq(SLB._sc(db.get_field_value(real, 'numSpawnMinEquation')))
    if p is None:
        raise SystemExit("negtest M3 could not parse %s's numSpawn equation." % table)
    return real, p[0]


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_orb_legendary.py <arz>")
        return 2
    arz = argv[1]
    fails = []

    base, base_lk = load_fixed(arz)

    # ── Q1: the wave is green.
    probs = SOL.problems(base, base_lk)
    ok = not probs
    print("%s Q1 POSITIVE CONTROL: the R-230+R-231 build passes the orb legendary "
          "contract (%d finding(s))" % ('OK ' if ok else 'XX ', len(probs)))
    for p in probs[:6]:
        print("      %s" % p)
    if not ok:
        fails.append('Q1')

    # ── Q2: the apex orb is STILL the richest orb. Will's b79 precedent ("orbs stay
    #    generous") is superseded only where it collides; a gate that flattened the
    #    apex into its siblings would have thrown away a ruling nobody retired.
    d = SLD.Db(base)
    dist = SLD.Distributor(d)
    scope = SOL.orb_tables(base, base_lk)
    apex_l = _must(base_lk, APEX['l'], 'Q2 apex reference')
    apex_drops = SOL.reading(d, dist, apex_l)[0]
    others = [SOL.reading(d, dist, r)[0]
              for _k, (r, t) in scope.items() if t == 'l' and SLB._n(r) != SLB._n(apex_l)]
    ok = bool(others) and apex_drops >= max(others)
    print("%s Q2 POSITIVE CONTROL: the apex Legendary orb still pays the most of any "
          "orb (%.3f vs best sibling %.3f items/open)"
          % ('OK ' if ok else 'XX ', apex_drops, max(others) if others else 0.0))
    if not ok:
        fails.append('Q2')

    # ── Q3: breadth + distribution are GREEN on the same database. This lane's whole
    #    claim is "variety survives at lower volume", and that is a claim about other
    #    people's gates, so it is proved by running them.
    cross = []
    for name, fn in (('R-220 orb breadth',
                      lambda: SOB.audit_db(base, base_lk, None, verbose=False)[0]),
                     ('R-180 chest breadth',
                      lambda: SLB.audit_db(base, verbose=False)[0]),
                     ('R-181 distribution',
                      lambda: SAB.audit_db(base, verbose=False)[0]),
                     ('R-230 volume', lambda: SLV.problems(base, base_lk))):
        try:
            n = len(fn())
        except SystemExit as exc:
            n = -1
            print("      %s raised: %s" % (name, str(exc)[:120]))
        cross.append((name, n))
    ok = all(n == 0 for _n, n in cross)
    print("%s Q3 POSITIVE CONTROL: coexisting gates on the SAME db - %s"
          % ('OK ' if ok else 'XX ',
             ', '.join('%s %d' % (n, c) for n, c in cross)))
    if not ok:
        fails.append('Q3')

    def check(label, mutate, probe, why):
        db, lk = load_fixed(arz)
        mutate(db, lk)
        hit = probe(db, lk)
        if not hit:
            fails.append(label.split()[0])
        print("%s %-62s -> %s" % ('OK ' if hit else 'XX ', label,
                                  ('RED (correct): %s' % hit) if hit
                                  else 'GREEN (BLIND - %s)' % why))

    # ── M1: the three demoted rows put back at 100.
    def _restore_guaranteed(db, lk):
        for tier, path in APEX.items():
            real = _must(lk, path, 'M1 apex revert target')
            db.set_field(real, 'loot4Chance', 100.0)
            db._modified.add(real)

    def _p_m1(db, lk):
        o1 = codes(SOL.problems(db, lk), 'O1')
        return ('%d O1' % len(o1)) if len(o1) == 3 else ''
    check('M1 the apex guaranteed rows restored to chance 100', _restore_guaranteed,
          _p_m1, "Will's literal ruling stops being enforced and the wave can be undone")

    # ── M2: a guaranteed-legendary row on a table that never had one.
    def _plant_guaranteed(db, lk):
        d = SLD.Db(db)
        dist = SLD.Distributor(d)
        real = _must(lk, ORDINARY_L, 'M2 plant target')
        rows = sorted((r for r in SOL.group_profile(d, dist, real) if r[2] > 0),
                      key=lambda r: -(r[1] * r[2]))
        if not rows:
            raise SystemExit('M2 found no legendary row on %s' % ORDINARY_L)
        db.set_field(real, 'loot%dChance' % rows[0][0], 100.0)
        db._modified.add(real)

    def _p_m2(db, lk):
        o1 = [p for p in codes(SOL.problems(db, lk), 'O1')
              if 'uberorb_default_l01c' in p]
        return ('%d O1 on the ordinary orb' % len(o1)) if o1 else ''
    check('M2 a guaranteed-legendary row planted on an ORDINARY orb', _plant_guaranteed,
          _p_m2, 'O1 is remembering three apex records instead of sweeping the surface')

    # ── M3: one orb back at its shipped spawn volume.
    def _reinflate(db, lk):
        real, bracket = _shipped_eq(db, lk, ORDINARY_L)
        db.set_field(real, 'numSpawnMinEquation', SLV.format_eq(bracket, 1.58))
        db.set_field(real, 'numSpawnMaxEquation', SLV.format_eq(bracket, 1.58))
        db._modified.add(real)

    def _p_m3(db, lk):
        p = SOL.problems(db, lk)
        o2, o3 = codes(p, 'O2'), codes(p, 'O3')
        return ('%d O2 + %d O3' % (len(o2), len(o3))) if (o2 and o3) else ''
    check('M3 an orb restored to its shipped spawn volume', _reinflate, _p_m3,
          'the guarantee Will hit lived in the spawn count, and nothing would see it '
          'come back')

    # ── M4: the MIRROR - a legendary becomes near-impossible.
    def _gut(db, lk):
        _shift_legendary_weight(db, lk, ORDINARY_L, M4_WEIGHT_SHIFT)

    def _p_m4(db, lk):
        p = SOL.problems(db, lk)
        o4 = codes(p, 'O4')
        other = [x for x in p if not x.startswith('O4 ')]
        return ('%d O4 and NOTHING else' % len(o4)) if (o4 and not other) else ''
    check('M4 THE MIRROR: the legendary weight shifted away so a legendary cannot roll',
          _gut, _p_m4,
          '"a LOW chance" can be satisfied by deleting the reward while every ceiling '
          'AND the items-per-open floor stay green')

    # ── M5: the TRUNCATION MIRROR - green on continuous, RED under truncation.
    def _gut_band(db, lk):
        _shift_legendary_weight(db, lk, ORDINARY_L, M5_WEIGHT_SHIFT)

    def _p_m5(db, lk):
        o4 = codes(SOL.problems(db, lk), 'O4')
        if not o4:
            return ''
        # and prove it is the TRUNCATED reading that caught it: the continuous number
        # printed in the finding must still be above the floor.
        d2 = SLD.Db(db)
        dist2 = SLD.Distributor(d2)
        real = _must(lk, ORDINARY_L, 'M5 verification target')
        _drops, _e, p1, p1t = SOL.reading(d2, dist2, real)
        floor = SOL.ORB_MIN_P_LEGENDARY['l']
        if not (p1 >= floor > p1t):
            return ''
        return ('%d O4 with continuous %.4f >= floor %.2f > truncated %.4f'
                % (len(o4), p1, floor, p1t))
    check('M5 THE TRUNCATION MIRROR: above the floor continuous, below it truncated',
          _gut_band, _p_m5,
          'the floor is measured under the LENIENT spawn model and a real collapse '
          'ships green (the R-230 V7b defect, mirrored)')

    # ── M6: the SECOND MIRROR - the orb becomes an empty box.
    def _empty(db, lk):
        real = _must(lk, ORDINARY_L, 'M6 empty-box target')
        for g in range(1, 7):
            c = SLB._sc(db.get_field_value(real, 'loot%dChance' % g))
            try:
                v = float(c)
            except (TypeError, ValueError):
                continue
            if v > 0:
                db.set_field(real, 'loot%dChance' % g, v * M6_CHANCE_SCALE)
        db._modified.add(real)

    def _p_m6(db, lk):
        o5 = codes(SOL.problems(db, lk), 'O5')
        return ('%d O5' % len(o5)) if o5 else ''
    check('M6 THE SECOND MIRROR: every group chance scaled to an empty box', _empty,
          _p_m6, 'every ceiling can be satisfied by making the orb not worth opening')

    # ── M7: the derived demotion target relocated.
    def _p_m7():
        db, lk = load_fixed(arz)
        # put the guaranteed rows back so the wave has work to do, then move the
        # family value the derivation reads.
        for path in APEX.values():
            real = _must(lk, path, 'M7 revert target')
            db.set_field(real, 'loot4Chance', 100.0)
            db._modified.add(real)
        for _k, (real, _t) in SOL.orb_tables(db, lk).items():
            c = SLB._sc(db.get_field_value(real, 'loot4Chance'))
            try:
                v = float(c)
            except (TypeError, ValueError):
                continue
            if 0 < v < 100:
                db.set_field(real, 'loot4Chance', 44.0)
                db._modified.add(real)
        try:
            SOL.apply_wave(db, lk, verbose=False)
        except SystemExit as exc:
            return str(exc)
        return ''
    hit = _p_m7()
    ok = bool(hit) and 'FAMILY_CHANCE_EXPECTED' in hit
    print("%s %-62s -> %s"
          % ('OK ' if ok else 'XX ',
             'M7 the derived demotion target moved out from under the contract',
             'RED (correct): SystemExit naming FAMILY_CHANCE_EXPECTED' if ok
             else 'GREEN (BLIND - a retune of the orb family silently relocates the '
                  'demotion and nobody chose the new number)'))
    if not ok:
        fails.append('M7')

    print()
    if fails:
        print("NEGTEST FAIL: %d case(s) did not behave as designed: %s"
              % (len(fails), ', '.join(fails)))
        return 1
    print("NEGTEST PASS: 7 planted defects RED, 3 positive controls GREEN - the orb "
          "legendary contract fires in BOTH directions, the floor holds under the "
          "PESSIMISTIC spawn model, the derived demotion target cannot drift, and the "
          "breadth/distribution gates stay green on the same database.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
