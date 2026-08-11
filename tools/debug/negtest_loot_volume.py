r"""negtest_loot_volume.py - PLANTED NEGATIVES for the loot-VOLUME contract (R-230)
and for Will's chest-artifact ruling.

Will 2026-08-11: "we probably need to trip the loot-volume trim, especially on the steam
version where maybe from the two chests, you get guaranteed 1 legendary item. on the
testhub version we can spawn more that is fine." and "artifacts should never drop from
chests".

A VOLUME CONTRACT HAS TWO WAYS TO BE WRONG, so these plant in BOTH directions - too much
(the defect Will reported) and too little (this lane's own over-correction). A gate that
only reds one side would let the next wave quietly starve the game while reporting a
clean sweep, which is the same shape as the b80 D6b mirror finding.

  N1  a canonical cage table re-inflated to its SHIPPED numSpawn        -> V1 + V6
  N2  the TESTHUB twin trimmed with canonical                           -> V2 + V5
  N3  a numSpawn equation replaced with a bare literal                  -> V4
       (the build28/29/30 P0 verbatim: the evaluator returned 0 and the chest opened
        and dropped nothing. That is the single most expensive numSpawn bug on record,
        so it is planted rather than trusted to a comment.)
  N4  numSpawnMin dropped below one iteration at one player             -> V3
  N5  the MIRROR - both cage chests over-trimmed to the bare V3 floor, which is legal
      volume and an illegal GUARANTEE                                   -> V7
  N6  a non-pinned equippable artifact wired into a reachable table     -> A1
  N7  the pinned artifacts' loot row removed                            -> A3 (dead pin)
  N8  the scroll discriminator broken                                   -> A4
  N9  D7X2 - the D7 anchor surface's volume moved out from under the committed
      constant, which silently rescales the armour-parity floor         -> D7X2
  N10 THE TRUNCATION MASK - the guarantee degraded for real, then "repaired" by
      raising numSpawnMax INSIDE the truncation band [1,2)              -> V7b, V7 GREEN
  N11 a SECOND apply_wave on the same database                          -> SystemExit
  P1/P2/P3 positive controls: the wave is green, the TESTHUB twin's DELIBERATE richness
      stays green (a gate that reds the ruling's own other half is worthless), and the
      six R-185 pins stay green.

Usage: py tools/debug/negtest_loot_volume.py <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import svc_armor_breadth as SAB
import svc_chest_artifacts as SCA
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD
import svc_loot_volume as SLV

# The shipped (pre-R-230) cage multipliers, so N1 is a verbatim revert and not a guess.
SHIPPED_M = {'01': (2.4, 2.8), '03': (2.8, 3.2)}
BRACKET = '(3+(1.8*numberOfPlayers))'
# A Greater artifact that NOTHING reaches today (MEASURED: 0 of the 33 Greater records
# are chest-reachable) - so N6 proves A1 fires on a record the roster has never heard
# of, which is the leak the ruling is actually about.
PLANT_ARTIFACT = r'records\xpack\item\artifacts\e_ga_crimsonviper.dbr'
# The table R-185's artifact row hangs off. NOT `xpack\...\04_l_misc` - that path does
# not exist, and an earlier draft of this file used it: both artifact plants then wrote
# nothing and reported the GATE as blind. A negtest whose plant silently misses is worse
# than no negtest, because it accuses working code. Hence `_must` below.
PIN_ROW = r'records\item\loottables\svc\svc_craft_reagents_artifact_l01.dbr'

# ── N10's two plant constants, both SCANNED rather than chosen ───────────────
# The mask only works below TWO iterations solo, because `int(1.99) == int(1.05) == 1`:
# that is the entire band in which the continuous model moves and the truncated one
# cannot. 1.99 is the top of it.
N10_MASK_MAX_SOLO = 1.99
# The composition scale is SWEPT, not chosen. The usable band is narrow by nature -
# it is exactly the gap between the two floors - so the value is the one that
# maximises the SMALLER of the two margins, and the whole sweep is recorded so the
# next reader can see the band rather than trust the number. MEASURED, Epic (the
# binding difficulty), with numSpawnMin at the never-empty floor and numSpawnMax
# masked to 1.99 iterations:
#     f      V7 (cont, floor 0.95)     V7b (trunc, floor 0.90)     other findings
#     0.85   0.9656  green by 0.0156   0.8914  RED   by 0.0086     none
#     0.84   0.9637  green by 0.0137   0.8876  RED   by 0.0124     none   <- taken
#     0.82   0.9599  green by 0.0099   0.8798  RED   by 0.0202     none
#     0.80   0.9557  green by 0.0057   0.8716  RED   by 0.0284     none
#     0.75   0.9435  RED               0.8494  RED                 none
# 0.84 maximises min(margin) at 0.0124. Note what the sweep also proves: NO other
# check fires anywhere in the band - the plant is legal under V1, V3, V4, V5 and V6,
# which is precisely why the continuous model alone would have shipped it. If a
# future retune moves the surface far enough, this case goes BLIND rather than wrong,
# and `check` prints BLIND instead of passing quietly.
N10_CHANCE_SCALE = 0.84


def load_fixed(path):
    db = ArzDatabase.from_arz(Path(path))
    SLV.apply_wave(db, verbose=False)
    return db, SLB.Lookup(db)


def _must(lk, path, why):
    """Resolve a record or DIE. Every plant goes through this.

    A plant that silently misses reports the gate as BLIND, which is an accusation
    against working code and the most expensive way for a negative battery to be wrong.
    Two paths in an earlier draft of this file did exactly that."""
    real = lk.real(path)
    if not real:
        raise SystemExit(
            "negtest plant could not resolve %r (%s). The plant would have written "
            "NOTHING and the case would have reported the gate as blind." % (path, why))
    return real


def hosts_of(db, lk, member):
    """Every loot table naming `member`, with the slot index. Derived, because R-185's
    artifact row hangs off THREE hosts and zeroing one leaves the pins reachable."""
    out = []
    for p in db.record_names():
        for k, tf in (db.get_fields(p) or {}).items():
            base = k.split('###')[0]
            if not base.startswith('lootName'):
                continue
            for v in tf.values:
                if isinstance(v, str) and SLB._n(v) == SLB._n(member):
                    out.append((p, int(base[len('lootName'):])))
    return out


def set_eq(db, lk, table, lo, hi, bracket=BRACKET):
    real = _must(lk, table, 'numSpawn plant target')
    db.set_field(real, 'numSpawnMinEquation', SLV.format_eq(bracket, lo))
    db.set_field(real, 'numSpawnMaxEquation', SLV.format_eq(bracket, hi))
    db._modified.add(real)


def codes(problems, prefix):
    return [p for p in problems if p.startswith(prefix + ' ')]


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_loot_volume.py <arz>")
        return 2
    arz = argv[1]
    fails = []

    base, base_lk = load_fixed(arz)

    # ── P1: the wave is green.
    probs = SLV.problems(base, base_lk)
    ok = not probs
    print("%s P1 POSITIVE CONTROL: the R-230 build passes the volume contract "
          "(%d finding(s))" % ('OK ' if ok else 'XX ', len(probs)))
    for p in probs[:6]:
        print("      %s" % p)
    if not ok:
        fails.append('P1')

    # ── P2: the TESTHUB twin's deliberate richness is NOT read as a defect. The whole
    #    ruling has two halves and a gate that reds its own other half is worthless.
    d = SLD.Db(base)
    dist = SLD.Distributor(d)
    hub_l, _p = SLV.cage_run(d, dist, base_lk, 'l', hub=True)
    can_l, _p2 = SLV.cage_run(d, dist, base_lk, 'l', hub=False)
    ok = hub_l > 8 * can_l and not codes(probs, 'V1')
    print("%s P2 POSITIVE CONTROL: the TESTHUB twin pays %.1f vs canonical %.1f "
          "(%.1fx) and is NOT flagged by the canonical ceiling"
          % ('OK ' if ok else 'XX ', hub_l, can_l, hub_l / max(can_l, 1e-9)))
    if not ok:
        fails.append('P2')

    # ── P3: the six R-185 pins are green, each re-proved live and still a reagent.
    art = SCA.problems(base, base_lk)
    ok = not art
    print("%s P3 POSITIVE CONTROL: the artifact ruling passes on the pinned roster "
          "(%d finding(s))" % ('OK ' if ok else 'XX ', len(art)))
    for p in art[:4]:
        print("      %s" % p)
    if not ok:
        fails.append('P3')

    def check(label, mutate, probe, why):
        db, lk = load_fixed(arz)
        mutate(db, lk)
        hit = probe(db, lk)
        if not hit:
            fails.append(label)
        print("%s %-58s -> %s" % ('OK ' if hit else 'XX ', label,
                                  ('RED (correct): %s' % hit) if hit
                                  else 'GREEN (BLIND - %s)' % why))

    # ── N1: a canonical cage table restored to its shipped volume.
    def _reinflate(db, lk):
        for tier in SLV.TIERS:
            for v in SLV.VARIANTS:
                for N in SLV.CAGE_CHESTS:
                    set_eq(db, lk, SLV.canon_cage_table(N, tier, v), *SHIPPED_M[N])

    def _p_n1(db, lk):
        p = SLV.problems(db, lk)
        n1, n6 = codes(p, 'V1'), codes(p, 'V6')
        return ('%d V1 + %d V6' % (len(n1), len(n6))) if (n1 and n6) else ''
    check('N1 canonical cage re-inflated to shipped numSpawn', _reinflate, _p_n1,
          'the ceiling cannot see a surface going back to 36 legendaries a run')

    # ── N2: the TESTHUB twin trimmed with canonical.
    def _trim_hub(db, lk):
        for tier in SLV.TIERS:
            for v in SLV.VARIANTS:
                for N in SLV.CAGE_CHESTS:
                    canon = lk.real(SLV.canon_cage_table(N, tier, v))
                    eq_lo = SLV.parse_eq(lk.gv(canon, 'numSpawnMinEquation'))
                    eq_hi = SLV.parse_eq(lk.gv(canon, 'numSpawnMaxEquation'))
                    set_eq(db, lk, SLV.hub_cage_table(N, tier, v),
                           eq_lo[1], eq_hi[1], eq_lo[0])

    def _p_n2(db, lk):
        p = SLV.problems(db, lk)
        v2, v5 = codes(p, 'V2'), codes(p, 'V5')
        return ('%d V2 + %d V5' % (len(v2), len(v5))) if (v2 and v5) else ''
    check('N2 TESTHUB twin trimmed with canonical', _trim_hub, _p_n2,
          "the DEV farm can be silently killed while every ceiling stays green")

    # ── N3: the bare literal - the build28/29/30 P0, verbatim.
    def _bare_literal(db, lk):
        real = lk.real(SLV.canon_cage_table('01', 'l', 'a'))
        db.set_field(real, 'numSpawnMinEquation', '1')
        db.set_field(real, 'numSpawnMaxEquation', '2')
        db._modified.add(real)

    def _p_v4(db, lk):
        v4 = codes(SLV.problems(db, lk), 'V4')
        return ('%d V4' % len(v4)) if v4 else ''
    check('N3 numSpawn replaced with a bare literal', _bare_literal, _p_v4,
          'the P0 that made a chest open and drop nothing can ship again')

    # ── N4: below one loot iteration solo.
    def _under_one(db, lk):
        set_eq(db, lk, SLV.canon_cage_table('01', 'l', 'a'), 0.1, 0.2)

    def _p_v3(db, lk):
        v3 = codes(SLV.problems(db, lk), 'V3')
        return ('%d V3' % len(v3)) if v3 else ''
    check('N4 numSpawnMin below one iteration at one player', _under_one, _p_v3,
          'a chest that rolls zero items passes as a "trim"')

    # ── N5: THE MIRROR. Over-trimmed to the bare V3 floor - legal volume, and the
    #    guarantee Will actually asked for is gone. This is the defect THIS LANE could
    #    have shipped, which is why it is planted rather than argued about.
    def _over_trim(db, lk):
        m = round(SLV.MIN_SPAWN_MIN_SOLO / 4.8 + 0.0001, 4)
        for tier in SLV.TIERS:
            for v in SLV.VARIANTS:
                for N in SLV.CAGE_CHESTS:
                    set_eq(db, lk, SLV.canon_cage_table(N, tier, v), m, m)

    def _p_v7(db, lk):
        p = SLV.problems(db, lk)
        v7, v3 = codes(p, 'V7'), codes(p, 'V3')
        # V3 must NOT fire: the point is that the plant is inside every OTHER rule.
        return ('%d V7, V3 silent as designed' % len(v7)) if (v7 and not v3) else ''
    check('N5 MIRROR: over-trimmed until the guarantee dies', _over_trim, _p_v7,
          'the trim can be taken past Will\'s "guaranteed 1 legendary item"')

    # ── N6: a non-pinned equippable artifact wired into a reachable table.
    def _plant_artifact(db, lk):
        row = _must(lk, PIN_ROW, 'the R-185 artifact row, host of the N6 plant')
        _must(lk, PLANT_ARTIFACT, 'the Greater artifact N6 wires in')
        for i in range(1, 13):
            if not str(lk.gv(row, 'lootName%d' % i) or '').strip():
                db.set_field(row, 'lootName%d' % i, PLANT_ARTIFACT)
                db.set_field(row, 'lootWeight%d' % i, 100)
                db._modified.add(row)
                return
        raise SystemExit('negtest N6 found no free member slot on %s' % PIN_ROW)

    def _p_a1(db, lk):
        a1 = codes(SCA.problems(db, lk), 'A1')
        return ('%d A1' % len(a1)) if a1 else ''
    check('N6 a non-pinned equippable artifact reaches a chest', _plant_artifact, _p_a1,
          "Will's \"artifacts should never drop from chests\" is unenforced")

    # ── N7: the pinned row removed -> the pins become DEAD CONFIG and must red.
    #    Every host, not one: R-185's artifact row hangs off 04_l_misc AND amulet_l01
    #    AND finger_l01, so zeroing a single host leaves all six pins still reachable
    #    and the plant would prove nothing.
    def _drop_pin_row(db, lk):
        _must(lk, PIN_ROW, 'the R-185 artifact row N7 unhooks')
        hosts = hosts_of(db, lk, PIN_ROW)
        if not hosts:
            raise SystemExit('negtest N7 found no host naming %s' % PIN_ROW)
        for host, i in hosts:
            db.set_field(host, 'lootWeight%d' % i, 0)
            db._modified.add(host)

    def _p_a3(db, lk):
        a3 = codes(SCA.problems(db, lk), 'A3')
        return ('%d A3' % len(a3)) if a3 else ''
    check('N7 the artifact roster outlives its leak (dead config)', _drop_pin_row,
          _p_a3, 'a pin can survive forever after the thing it excused is gone')

    # ── N8: the discriminator stops discriminating.
    def _break_mark(db, lk):
        SCA.SCROLL_SKILL_MARK = '\\skills\\this folder does not exist\\'

    def _p_a4(db, lk):
        try:
            a4 = codes(SCA.problems(db, lk), 'A4')
            return ('%d A4' % len(a4)) if a4 else ''
        finally:
            SCA.SCROLL_SKILL_MARK = '\\skills\\scroll skills\\'
    check('N8 the scroll discriminator stops discriminating', _break_mark, _p_a4,
          'the gate reports a sweep of 141 artifacts it never performed')

    # ── N9: D7X2 - the anchor volume drifts out from under the committed constant.
    def _move_anchor(db, lk):
        for v in SLV.VARIANTS:
            set_eq(db, lk, SLV.canon_cage_table('01', 'l', v), 0.5, 0.7)

    def _p_d7x2(db, lk):
        _p, reports = SAB.audit_db(db, lk)
        x = [q for q in SLD.reference_surface_problems(reports)
             if q.startswith('D7X2 ')]
        return ('%d D7X2' % len(x)) if x else ''
    check('N9 the D7 anchor surface\'s volume drifts', _move_anchor, _p_d7x2,
          'ARMOR_SLOT_FLOOR silently rescales with whatever numSpawn was edited last')

    # ── N10: THE TRUNCATION MASK. This is the defect V7b exists for, and without it
    #    V7b would be decoration: V7's continuous model can be satisfied by moving a
    #    number the player never experiences.
    #    The plant is two real, plausible edits in sequence:
    #      1. the `BL-R230-DEBT-1` follow-up ("Will meant literally one") taken too
    #         far - every cage group chance scaled by N10_CHANCE_SCALE, so the
    #         guarantee genuinely degrades;
    #      2. the MASK - numSpawnMax raised to just under TWO iterations solo. Under
    #         the continuous model that lifts S from ~1.19 to ~1.52 and the guarantee
    #         "recovers"; under truncation `int(1.99) == int(1.05) == 1` and NOTHING
    #         changes, because the engine either rolls one iteration or it does not.
    #    MEASURED at this scale: Epic P(>=1) 0.9637 continuous (V7 floor 0.95, GREEN)
    #    against 0.8876 truncated (V7b floor 0.90, RED). V1/V6/V3/V4/V5 stay silent -
    #    the plant is legal under every other rule in the contract, which is the whole
    #    point. If a future retune moves the base numbers this case goes BLIND rather
    #    than wrong, and the printed line says so.
    def _truncation_mask(db, lk):
        hi_m = round(N10_MASK_MAX_SOLO / 4.8, 4)
        lo_m = round(SLV.MIN_SPAWN_MIN_SOLO / 4.8 + 0.0001, 4)
        for N in SLV.CAGE_CHESTS:
            for tier in SLV.TIERS:
                for v in SLV.VARIANTS:
                    real = _must(lk, SLV.canon_cage_table(N, tier, v),
                                 'the N10 truncation-mask target')
                    for g in range(1, 7):
                        c = lk.gv(real, 'loot%dChance' % g)
                        if c is not None:
                            db.set_field(real, 'loot%dChance' % g,
                                         round(float(c) * N10_CHANCE_SCALE, 4))
                    db.set_field(real, 'numSpawnMinEquation',
                                 SLV.format_eq(BRACKET, lo_m))
                    db.set_field(real, 'numSpawnMaxEquation',
                                 SLV.format_eq(BRACKET, hi_m))
                    db._modified.add(real)

    def _p_v7b(db, lk):
        p = SLV.problems(db, lk)
        v7b, v7 = codes(p, 'V7b'), codes(p, 'V7')
        # V7 must stay SILENT. That is the assertion: the continuous model was
        # satisfied by an edit the player cannot feel, and only V7b noticed.
        return ('%d V7b, V7 silent as designed' % len(v7b)) if (v7b and not v7) else ''
    check('N10 MASK: guarantee "fixed" by raising numSpawnMax inside [1,2)',
          _truncation_mask, _p_v7b,
          'the continuous model can be satisfied by a number no player experiences')

    # ── N11: a SECOND apply_wave. The round-2 vet measured the consequence: 58 tables
    #    drift, the twin is re-cloned off the ALREADY-TRIMMED canonical records, and
    #    the canonical-vs-TESTHUB split silently ceases to exist (DEV lands at ~1.04x
    #    canonical instead of ~9.5x). Planted rather than trusted to a docstring,
    #    because four docstrings claimed the opposite and all four were wrong.
    def _double_apply(db, lk):
        try:
            SLV.apply_wave(db, verbose=False)
        except SystemExit as e:
            return str(e)
        return ''
    db2, lk2 = load_fixed(arz)
    hit = _double_apply(db2, lk2)
    ok = bool(hit) and 'ALREADY EXISTS' in hit
    print("%s %-58s -> %s"
          % ('OK ' if ok else 'XX ', 'N11 a second apply_wave on the same database',
             'RED (correct): SystemExit re-entry guard' if ok
             else 'GREEN (BLIND - the twin gets re-cloned off trimmed records and the '
                  'TESTHUB split silently vanishes)'))
    if not ok:
        fails.append('N11')

    print()
    if fails:
        print("NEGTEST FAIL: %d case(s) did not behave as designed: %s"
              % (len(fails), ', '.join(fails)))
        return 1
    print("NEGTEST PASS: 11 planted defects RED, 3 positive controls GREEN - the volume "
          "contract fires in BOTH directions, the guarantee holds under BOTH spawn-count "
          "models, the apply-once guard is real, and the artifact ruling is enforced.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
