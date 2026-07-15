r"""Dry-run replay + fail-loud proof for tools/patches/souls_quality.py (no heavy build).

Applies souls_quality over a COPY (in-memory) of a built .arz - the FINAL
post-monolith+registry state the module sees at run time - and proves:
  1. INTENDED-ONLY DIFF: db._modified after apply() == exactly the predicted set
     (the wrong-icon svc_uber e/l rings UNION the 5 tier-inversion level-fix
     records).
  2. FIELD-LEVEL MINIMALITY: each touched record changed ONLY its bitmap (icon
     rings) and/or the intended level fields (the inversion fixes); every other
     field byte-identical.
  3. CORRECTNESS: all 5 inverted families now run n<=e<=l on the fixed field(s);
     every svc_uber e/l ring shows its own tier icon.
  4. verify() passes (roster-wide monotonicity + svc_uber icon gates).
  5. IDEMPOTENCY: a 2nd apply() touches nothing new.
  6. NEGATIVE: verify() fail-louds on an injected svc_uber inversion, on an
     injected NON-svc_uber (roster-wide) inversion, AND on an injected wrong-tier
     icon.

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
    # level-fix records that will actually change (raise-only: cur < target)
    level_recs = {}               # rec -> {field: target}
    for path, fields in SQ._LEVEL_FIX.items():
        rec = nm[_n(path)]
        eff = {f: t for f, t in fields.items()
               if (SQ._ival(db, rec, f) or 0) < t}
        if eff:
            level_recs[rec] = eff
    predicted = set(predicted_icon) | set(level_recs)
    print("predicted wrong-icon e/l rings : %d" % len(predicted_icon))
    print("level-fix records (raise-only) : %d (%s)"
          % (len(level_recs), ', '.join(sorted(r.rsplit('\\', 1)[-1] for r in level_recs))))
    print("predicted total touched        : %d" % len(predicted))

    before = {rec: snap_fields(db, rec) for rec in predicted}

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

    # (2) field-level minimality + (3) icon correctness
    ICON = 'SVItems\\jewelry\\soul_%s_icon.tex'
    field_ok = True
    for rec in delta:
        nn = _n(rec)
        tier = SQ._tier_of(nn)
        aft = snap_fields(db, rec)
        bef = before.get(rec, {})
        changed = {f for f in set(aft) | set(bef) if aft.get(f) != bef.get(f)}
        allowed = set(level_recs.get(rec, {}))
        if rec in predicted_icon:
            allowed |= {'bitmap'}
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

    # (3b) every fixed family's fixed field(s) now monotonic n<=e<=l
    print('\n[3b] fixed-family monotonicity')
    mono_ok = True

    def fam_levels(fam_dir_stem, field):
        rn = {t: nm[_n(r'records\item\equipmentring\soul\%s_%s.dbr'
                       % (fam_dir_stem, t))] for t in ('n', 'e', 'l')}
        return [SQ._ival(db, rn[t], field) for t in ('n', 'e', 'l')]

    checks = [
        ('svc_uber\\crowboar_soul', 'augmentSkillLevel1'),
        ('svc_uber\\crowboar_soul', 'augmentSkillLevel2'),
        ('svc_uber\\crowboar_soul', 'itemSkillLevel'),
        ('svc_uber\\onyxspine_soul', 'augmentSkillLevel1'),
        ('svc_uber\\onyxspine_soul', 'augmentSkillLevel2'),
        ('svc_uber\\onyxspine_soul', 'itemSkillLevel'),
        ('svc_uber\\steamcrawler_soul', 'augmentSkillLevel1'),
        ('svc_uber\\steamcrawler_soul', 'augmentSkillLevel2'),
        ('spider\\bloodtip_soul', 'itemSkillLevel'),
        ('vulture\\gustleech_soul', 'itemSkillLevel'),
    ]
    for stem, field in checks:
        lv = fam_levels(stem, field)
        good = None not in lv and lv[0] <= lv[1] <= lv[2]
        mono_ok = mono_ok and good
        print('    %-28s %-20s n/e/l=%s  %s'
              % (stem, field, lv, 'OK' if good else 'FAIL'))
    ok = ok and mono_ok

    # (4) verify()
    print('\n[4] verify() (roster-wide monotonicity + svc_uber icon gates)')
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
    # (6a) svc_uber inversion
    crow_l = nm[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_l.dbr')]
    db.set_field(crow_l, 'augmentSkillLevel1', 1)
    caught_uber = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_uber = 'INVERSION' in str(e)
        print('    svc_uber inversion   -> verify RAISED:', caught_uber)
    db.set_field(crow_l, 'augmentSkillLevel1', 3)
    # (6b) NON-svc_uber (roster-wide) inversion - proves the widening
    blt_e = nm[_n(r'records\item\equipmentring\soul\spider\bloodtip_soul_e.dbr')]
    db.set_field(blt_e, 'itemSkillLevel', 1)          # re-introduce SV inversion
    caught_roster = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_roster = 'INVERSION' in str(e) and 'bloodtip' in str(e)
        print('    NON-svc_uber inversion-> verify RAISED (names bloodtip):', caught_roster)
    db.set_field(blt_e, 'itemSkillLevel', 7)          # restore
    # (6c) wrong-tier icon
    crow_e = nm[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_e.dbr')]
    db.set_field(crow_e, 'bitmap', 'SVItems\\jewelry\\soul_n_icon.tex')
    caught_icon = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_icon = 'wrong-tier soul' in str(e)
        print('    wrong-tier icon      -> verify RAISED:', caught_icon)
    ok = ok and caught_uber and caught_roster and caught_icon

    print('\nRESULT:', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
