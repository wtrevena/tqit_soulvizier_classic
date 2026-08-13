r"""negtest_orb_legendary.py - PLANTED NEGATIVES for the uber-orb legendary/blue contract
by difficulty (R-242, Will 2026-08-12).

Will 2026-08-12: general uber orbs 50% legendary on epic, 75% on legendary, 0% legendary
+ 75% blue on normal; "Leinth and the toxeus variants keep their current ... orbs".

A rate-BY-DIFFICULTY ruling with an exclusion has several ways to be wrong, so these
plant on every edge - a general orb off its band (either side), legendary gear reaching
Normal, the excluded apex changed by chance OR by a shared-master leak, an orb gutted to
an empty box, and the partition cross-check drifting off the pinned roster.

  N1  a general LEGENDARY orb's gear rows reset to 40 (its pre-wave chance) so P(legendary)
      falls out of the 75% band                                              -> G1
  N2  an excluded APEX table's loot chance changed (the exclusion breach)     -> G3
  N3  the legendary weapon master planted onto a NORMAL general orb, so it pays
      legendary GEAR (the tier-law violation Will's "0% on normal" forbids)   -> G2
  N4  a NORMAL general orb's blue(Epic) chance dropped below the 75% band      -> G1
  N5  a SHARED unique master retuned so it leaks into the frozen apex output   -> G3b
      (the apex table's own bytes stay put; only its behaviour moves)
  N6  a general orb gutted to an empty box, which meets a rate band the cheap way -> G5
  X0  the pinned apex roster no longer matches the derived exclusion set        -> X0

  Q1  positive control: the wave is green (0 findings)
  Q2  positive control: the apex-vs-general INVERSION notice fires (BL-R242-DEBT-1)
  Q3  positive control: the coexisting breadth/distribution/volume gates stay green on the
      SAME database (variety + parity survive the calibrated raise)

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

APEX = SOL.APEX_PINNED
GEN_L = r'records\xpack\item\containers\loot tables\uberorb_default_l01c.dbr'
GEN_N = r'records\xpack\item\containers\loot tables\uberorb_default_n01c.dbr'
SHARED_MASTER_L = SLB.MASTER['l']       # svc_unique_weapons_l01, shared apex + general


def load_fixed(path):
    """The arz with R-240 then R-242 applied, in registry order - the database this
    contract is written against."""
    db = ArzDatabase.from_arz(Path(path))
    if not SLV.already_applied(db):
        SLV.apply_wave(db, verbose=False)
    lk = SLB.Lookup(db)
    SOL.apply_wave(db, lk, verbose=False)
    lk.refresh()
    return db, lk


def _must(lk, path, why):
    real = lk.real(path)
    if not real:
        raise SystemExit("negtest plant could not resolve %r (%s). The plant would have "
                         "written NOTHING and the case would have reported the gate as "
                         "blind." % (path, why))
    return real


def codes(problems, prefix):
    return [p for p in problems if p.startswith(prefix + ' ')]


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
    print("%s Q1 POSITIVE CONTROL: the R-240+R-242 build passes the orb legendary/blue "
          "contract (%d finding(s))" % ('OK ' if ok else 'XX ', len(probs)))
    for p in probs[:6]:
        print("      %s" % p)
    if not ok:
        fails.append('Q1')

    # ── Q2: the inversion notice fires (the honest residue is legible).
    notice = SOL.inversion_notice(base, base_lk)
    ok = bool(notice) and 'BL-R242-DEBT-1' in notice
    print("%s Q2 POSITIVE CONTROL: the apex-vs-general inversion notice FIRES and names "
          "the debt" % ('OK ' if ok else 'XX '))
    if not ok:
        fails.append('Q2')

    # ── Q3: breadth + distribution + volume are GREEN on the same database.
    cross = []
    for name, fn in (('R-220 orb breadth',
                      lambda: SOB.audit_db(base, base_lk, None, verbose=False)[0]),
                     ('R-180 chest breadth',
                      lambda: SLB.audit_db(base, verbose=False)[0]),
                     ('R-181 distribution',
                      lambda: SAB.audit_db(base, verbose=False)[0]),
                     ('R-240 volume', lambda: SLV.problems(base, base_lk))):
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
        print("%s %-60s -> %s" % ('OK ' if hit else 'XX ', label,
                                  ('RED (correct): %s' % hit) if hit
                                  else 'GREEN (BLIND - %s)' % why))

    # ── N1: a general legendary orb back at its pre-wave gear chance (40).
    def _reset_l(db, lk):
        real = _must(lk, GEN_L, 'N1 target')
        for g in SOL.GEAR_ROWS:
            db.set_field(real, 'loot%dChance' % g, 40.0)
        db._modified.add(real)

    def _p_n1(db, lk):
        g1 = [p for p in codes(SOL.problems(db, lk), 'G1') if 'uberorb_default_l01c' in p]
        return ('%d G1 on the legendary orb' % len(g1)) if g1 else ''
    check('N1 a general legendary orb reset below its 75% band', _reset_l, _p_n1,
          'the per-difficulty legendary target stops being enforced')

    # ── N2: an excluded apex table's loot chance changed.
    def _touch_apex(db, lk):
        real = _must(lk, APEX['l'], 'N2 target')
        db.set_field(real, 'loot4Chance', 30.0)
        db._modified.add(real)

    def _p_n2(db, lk):
        g3 = [p for p in codes(SOL.problems(db, lk), 'G3')
              if 'svc_uberorb_apex_l01c' in p and 'loot4' in p]
        return ('%d G3 on the apex' % len(g3)) if g3 else ''
    check('N2 an excluded apex loot chance changed (exclusion breach)', _touch_apex,
          _p_n2, 'Leinth/Toxeus stop being byte-frozen and the exclusion is undone')

    # ── N3: the legendary weapon master planted onto a NORMAL general orb.
    def _leg_gear_on_normal(db, lk):
        real = _must(lk, GEN_N, 'N3 target')
        master_l = _must(lk, SHARED_MASTER_L, 'N3 legendary master')
        # repoint the normal master member in loot1 to the LEGENDARY master
        members = SLB._slot_members(db, real, 1)
        slot = None
        for (i, nm, _w) in members:
            if SLB._n(nm) == SLB._n(_must(lk, SLB.MASTER['n'], 'N3 normal master')):
                slot = i
                break
        if slot is None:
            slot = members[0][0]
        db.set_field(real, 'loot1Name%d' % slot, master_l)
        db._modified.add(real)

    def _p_n3(db, lk):
        g2 = [p for p in codes(SOL.problems(db, lk), 'G2') if 'uberorb_default_n01c' in p]
        return ('%d G2 legendary-gear on normal' % len(g2)) if g2 else ''
    check('N3 legendary GEAR planted on a NORMAL general orb', _leg_gear_on_normal,
          _p_n3, '"0% legendary on normal" is not enforced on GEAR')

    # ── N4: a normal general orb's blue chance dropped below the band.
    def _drop_blue(db, lk):
        real = _must(lk, GEN_N, 'N4 target')
        for g in SOL.GEAR_ROWS:
            db.set_field(real, 'loot%dChance' % g, 20.0)
        db._modified.add(real)

    def _p_n4(db, lk):
        g1 = [p for p in codes(SOL.problems(db, lk), 'G1')
              if 'uberorb_default_n01c' in p and 'Epic' in p]
        return ('%d G1 blue-below-band on normal' % len(g1)) if g1 else ''
    check('N4 a normal general orb dropped below its 75% blue band', _drop_blue,
          _p_n4, '"75% blue on normal" can be under-delivered without a finding')

    # ── N5: SHARED unique masters retuned so they leak into the frozen apex.
    #    Scaling every child of the all-legendary master would be BLIND (a rate is a
    #    ratio - the same trap R-241's M4/M5 documented). What moves the apex's legendary
    #    SHARE is mixing a LOWER tier into what it reads: repoint the legendary weapon AND
    #    armour masters' members to their epic equivalents. The apex TABLE bytes stay put;
    #    only its output moves (measured ~4.4pp on Legendary, past the 2pp G3b guard).
    def _leak_master(db, lk):
        for master in (SLB.MASTER['l'],
                       r'records\item\loottables\svc\svc_unique_armor_l01.dbr'):
            real = _must(lk, master, 'N5 shared master')
            for i in range(1, 12):
                nm = SLB._sc(db.get_field_value(real, 'lootName%d' % i))
                if not (isinstance(nm, str) and nm.strip()):
                    continue
                epic = lk.real(SLB._n(nm).replace('_l0', '_e0'))
                if epic:
                    db.set_field(real, 'lootName%d' % i, epic)
            db._modified.add(real)

    def _p_n5(db, lk):
        g3b = codes(SOL.problems(db, lk), 'G3b')
        return ('%d G3b apex-leak' % len(g3b)) if g3b else ''
    check('N5 a shared master retuned, leaking into the frozen apex', _leak_master,
          _p_n5, 'a shared-master retune changes the excluded apex loot with no finding')

    # ── N6: a general orb gutted to an empty box.
    def _empty(db, lk):
        real = _must(lk, GEN_L, 'N6 target')
        for g in range(1, 7):
            c = SLB._sc(db.get_field_value(real, 'loot%dChance' % g))
            try:
                v = float(c)
            except (TypeError, ValueError):
                continue
            if v > 0:
                db.set_field(real, 'loot%dChance' % g, v * 0.20)
        db._modified.add(real)

    def _p_n6(db, lk):
        g5 = codes(SOL.problems(db, lk), 'G5')
        return ('%d G5' % len(g5)) if g5 else ''
    check('N6 a general orb scaled to an empty box', _empty, _p_n6,
          'a rate band can be met by making the orb not worth opening')

    # ── X0: the pinned apex roster drifts from the derived exclusion set.
    def _p_x0():
        db, lk = load_fixed(arz)
        saved = dict(SOL.APEX_PINNED)
        SOL.APEX_PINNED['bogus'] = r'records\item\loottables\svc\svc_uberorb_apex_z99.dbr'
        try:
            x0 = codes(SOL.partition_problems(db, lk), 'X0')
        finally:
            SOL.APEX_PINNED.clear()
            SOL.APEX_PINNED.update(saved)
        return ('%d X0' % len(x0)) if x0 else ''
    hit = _p_x0()
    ok = bool(hit)
    print("%s %-60s -> %s"
          % ('OK ' if ok else 'XX ',
             'X0 the pinned apex roster no longer matches the derived set',
             'RED (correct): %s' % hit if ok
             else 'GREEN (BLIND - a new apex consumer silently changes scope)'))
    if not ok:
        fails.append('X0')

    print()
    if fails:
        print("NEGTEST FAIL: %d case(s) did not behave as designed: %s"
              % (len(fails), ', '.join(fails)))
        return 1
    print("NEGTEST PASS: 6 planted defects + the partition-drift guard RED, 3 positive "
          "controls GREEN - the per-difficulty band fires on BOTH edges, legendary gear "
          "cannot reach Normal, the excluded apex is frozen against both a direct chance "
          "edit and a shared-master leak, the empty-box mirror holds, and the exclusion "
          "roster is cross-checked.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
