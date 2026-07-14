r"""Dry-run replay + fail-loud proof for tools/patches/souls_quality.py (no heavy build).

Applies souls_quality over a COPY (in-memory) of a built .arz - the FINAL
post-monolith+registry state the module sees at run time - and proves:
  1. INTENDED-ONLY DIFF: db._modified after apply() == exactly the predicted set
     (the wrong-icon svc_uber e/l rings; the 3 DEFICIENT _l souls are a subset).
  2. FIELD-LEVEL MINIMALITY: each touched record changed ONLY its bitmap (icon
     rings) and/or the intended L-tier level fields (the 3 deficient souls);
     every other field byte-identical.
  3. CORRECTNESS: the 3 deficient souls now run n<=e<=l; every e/l ring shows its
     own tier icon.
  4. verify() passes (roster-wide monotonicity + icon gates).
  5. IDEMPOTENCY: a 2nd apply() touches nothing new.
  6. NEGATIVE: verify() fail-louds on an injected inversion AND on an injected
     wrong-tier icon.

Usage:  py tools/debug/souls_quality_replay.py <built.arz>
Read-only against the input file (loads into memory; never writes the arz).
"""
import os, sys, re, pathlib, io, contextlib

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_TOOLS, os.path.join(_TOOLS, 'patches')):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from arz_patcher import ArzDatabase          # noqa: E402
import souls_quality as SQ                   # noqa: E402


def _n(p):
    return str(p).replace('/', '\\').lower().strip()


def snap_fields(db, rec):
    """{field: tuple(values)} snapshot for byte-level field diffing."""
    ff = db.get_fields(rec) or {}
    out = {}
    for key, tf in ff.items():
        out[key.split('###')[0]] = tuple(tf.values)
    return out


def main():
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print('Usage: py tools/debug/souls_quality_replay.py <built.arz>')
        sys.exit(2)
    db = ArzDatabase.from_arz(pathlib.Path(sys.argv[1]))
    nm = {_n(x): x for x in db.record_names()}

    # ---- predict the intended set from the baseline (independent of the module) ----
    predicted_icon = set()        # e/l svc_uber rings currently showing a wrong-tier soul icon
    for rec, nn, tier in SQ._iter_uber_rings(db, nm):
        bmp = SQ._sval(db, rec, 'bitmap')
        if bmp:
            m = SQ._SOUL_ICON_RE.search(bmp)
            if m and m.group(1) != tier:
                predicted_icon.add(rec)
    deficient_recs = {nm[_n(p)] for p in SQ._DEFICIENT_L_FIX}
    predicted = set(predicted_icon)          # deficient _l are a subset of the wrong-icon set
    print("predicted wrong-icon e/l rings : %d" % len(predicted_icon))
    print("deficient _l records           : %d (%s)"
          % (len(deficient_recs), ', '.join(sorted(r.rsplit('\\', 1)[-1] for r in deficient_recs))))
    print("deficient subset of icon set   : %s" % deficient_recs.issubset(predicted_icon))

    before = {rec: snap_fields(db, rec) for rec in predicted}
    for rec in deficient_recs:
        before.setdefault(rec, snap_fields(db, rec))

    mod0 = set(db._modified)
    print('\n########## APPLY ##########')
    SQ.apply(db, {})
    delta = set(db._modified) - mod0

    ok = True

    # (1) intended-only diff
    diff_only = delta == predicted
    extra = sorted(r.rsplit('\\', 1)[-1] for r in (delta - predicted))
    missing = sorted(r.rsplit('\\', 1)[-1] for r in (predicted - delta))
    print('\n[1] INTENDED-ONLY DIFF: touched=%d predicted=%d  match=%s'
          % (len(delta), len(predicted), diff_only))
    if extra:
        print('    !!! UNEXPECTED touched:', extra[:12])
    if missing:
        print('    !!! predicted but NOT touched:', missing[:12])
    ok = ok and diff_only

    # (2) field-level minimality + (3) correctness
    ICON = 'SVItems\\jewelry\\soul_%s_icon.tex'
    field_ok = True
    for rec in delta:
        nn = _n(rec)
        tier = SQ._tier_of(nn)
        aft = snap_fields(db, rec)
        bef = before.get(rec, {})
        changed = {f for f in set(aft) | set(bef) if aft.get(f) != bef.get(f)}
        allowed = {'bitmap'}
        if rec in deficient_recs:
            allowed |= set(SQ._DEFICIENT_L_FIX[
                next(p for p in SQ._DEFICIENT_L_FIX if _n(p) == nn)])
        stray = changed - allowed
        if stray:
            field_ok = False
            print('    !!! %s changed stray field(s): %s'
                  % (rec.rsplit('\\', 1)[-1], sorted(stray)))
        # icon correctness
        if 'bitmap' in changed:
            got = _n(aft.get('bitmap', ('',))[0])
            if got != _n(ICON % tier):
                field_ok = False
                print('    !!! %s icon=%s (want tier %s)'
                      % (rec.rsplit('\\', 1)[-1], got, tier))
    print('[2/3] FIELD MINIMALITY + icon correctness: %s' % field_ok)
    ok = ok and field_ok

    # (3b) deficient monotonicity now holds
    mono_ok = True
    for rec in sorted(deficient_recs):
        fam = re.search(r'\\svc_uber\\(.+?)_soul_l\.dbr$', _n(rec)).group(1)
        rn = {t: nm[_n(r'records\item\equipmentring\soul\svc_uber\%s_soul_%s.dbr' % (fam, t))]
              for t in ('n', 'e', 'l')}
        for k in (1, 2):
            lv = [SQ._ival(db, rn[t], 'augmentSkillLevel%d' % k) for t in ('n', 'e', 'l')]
            good = lv[0] <= lv[1] <= lv[2] and lv[2] >= 3
            mono_ok = mono_ok and good
            print('    %-14s augmentSkillLevel%d n/e/l=%s  %s'
                  % (fam, k, lv, 'OK' if good else 'FAIL'))
        if SQ._sval(db, rn['l'], 'itemSkillName'):
            lv = [SQ._ival(db, rn[t], 'itemSkillLevel') for t in ('n', 'e', 'l')]
            good = lv[0] <= lv[1] <= lv[2]
            mono_ok = mono_ok and good
            print('    %-14s itemSkillLevel     n/e/l=%s  %s'
                  % (fam, lv, 'OK' if good else 'FAIL'))
    ok = ok and mono_ok

    # (4) verify()
    print('\n[4] verify() (roster-wide monotonicity + icon gates)')
    try:
        SQ.verify(db, {})
        verify_ok = True
    except SystemExit as e:
        verify_ok = False
        print('    !!! verify RAISED:', str(e)[:200])
    ok = ok and verify_ok

    # (5) idempotency
    mod1 = set(db._modified)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        SQ.apply(db, {})
    delta2 = set(db._modified) - mod1
    print('\n[5] IDEMPOTENCY: 2nd apply touched %d new record(s) (expect 0)' % len(delta2))
    ok = ok and (len(delta2) == 0)

    # (6) negative tests
    print('\n[6] NEGATIVE TESTS')
    crow_l = nm[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_l.dbr')]
    db.set_field(crow_l, 'augmentSkillLevel1', 1)          # re-introduce inversion
    caught_inv = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_inv = 'INVERSION' in str(e)
        print('    inversion -> verify RAISED:', caught_inv)
    db.set_field(crow_l, 'augmentSkillLevel1', 3)          # restore
    crow_e = nm[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_e.dbr')]
    db.set_field(crow_e, 'bitmap', 'SVItems\\jewelry\\soul_n_icon.tex')  # wrong-tier icon
    caught_icon = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_icon = 'wrong-tier soul' in str(e)
        print('    wrong icon -> verify RAISED:', caught_icon)
    ok = ok and caught_inv and caught_icon

    print('\nRESULT:', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
