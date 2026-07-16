r"""Dry-run replay + fail-loud proof for tools/patches/souls_quality.py (no heavy build).

Applies souls_quality over a COPY (in-memory) of a built .arz - the FINAL
post-monolith+registry state the module sees at run time - and proves:
  1. INTENDED-ONLY DIFF: db._modified after apply() == exactly the predicted
     modified set (wrong-icon svc_uber e/l rings UNION the tier-inversion level-fix
     records UNION the 24 mod-introduced summon-controller records [8 families A+B,
     independently re-derived here vs the SV098 design bible and cross-checked
     against the module] UNION the tombguardian monster detach); AND exactly the 3
     tombguardian soul records are REMOVED.
  2. FIELD-LEVEL MINIMALITY: each touched record changed ONLY its allowed field(s)
     - bitmap (icon rings), the intended level fields (inversions),
     itemSkillAutoController REMOVED (summon rings), lootFinger2Item1 cleared
     (tombguardian monster); every other field byte-identical.
  3. CORRECTNESS: all inverted families now run n<=e<=l; every svc_uber e/l ring
     shows its own tier icon; every mod-introduced summon ring (svc_uber A +
     non-svc_uber B: carrionlord/komara/melalos/oythroneus) has NO controller while
     amgoz1's designed swarm (direflock) KEEPS its controller (no over-reach); the
     tombguardian soul is fully retired (detached + records gone).
  4. verify() passes (all four gates).
  5. IDEMPOTENCY: a 2nd apply() touches nothing new and removes nothing new.
  6. NEGATIVE: verify() fail-louds on an injected svc_uber inversion, an injected
     NON-svc_uber inversion, an injected wrong-tier icon, a mod-introduced on-attack
     controller re-injected on a svc_uber (crowboar) AND on a NON-svc_uber (komara)
     permanent summon - proving the gate is roster-wide, not svc_uber-scoped - AND an
     injected tombguardian soul re-attach.

Usage:  py tools/debug/souls_quality_replay.py <built.arz>
Read-only against the input file (loads into memory; never writes the arz).
"""
import os, sys, pathlib, io, contextlib

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

    # ---- predict the intended sets from the baseline (independent of the module) ----
    # (a) tombguardian retirement
    tg_mon = nm.get(_n(SQ._TG_MONSTER))
    tg_soul_recs = [nm[_n(sp)] for sp in SQ._TG_SOULS if _n(sp) in nm]
    tg_detach = set([tg_mon]) if tg_mon is not None else set()
    # (b) MOD-INTRODUCED on-attack summon controllers - INDEPENDENTLY re-derived here
    #     from the SV098 design bible (NOT via SQ's own function), then cross-checked
    #     against SQ._summon_controller_fix_records so the module can't self-certify.
    sv_db, sv_nm = SQ._load_sv098()

    def _ctlbase(d, r):
        c = SQ._sval(d, r, 'itemSkillAutoController')
        return _n(c).rsplit('\\', 1)[-1] if c else None

    def _perm_summon(d, dnm, r):
        isn = SQ._sval(d, r, 'itemSkillName')
        if not isn:
            return False
        sk = dnm.get(_n(isn))
        if sk is None or SQ._sval(d, sk, 'Class') != 'Skill_SpawnPet':
            return False
        ttl = d.get_field_value(sk, 'spawnObjectsTimeToLive')
        tl = ttl if isinstance(ttl, list) else ([ttl] if ttl not in (None, '') else [])
        return not tl

    def _onatk(b):   # independent heuristic (module uses a curated set + heuristic)
        if not b:
            return False
        b = b.lower()
        return ('onattacked' not in b) and (
            'onattack' in b or 'onmeleehit' in b or 'onrangedhit' in b or 'onanyhit' in b)

    ctl_recs = {}                 # rec -> was controller value (mod-introduced only)
    amgoz_kept = 0
    for rec, nn, tier in SQ._iter_soul_rings(db, nm):
        cb = _ctlbase(db, rec)
        if not _onatk(cb) or not _perm_summon(db, nm, rec):
            continue
        sv = sv_nm.get(nn)
        if sv is not None and _onatk(_ctlbase(sv_db, sv)):
            amgoz_kept += 1        # amgoz1 shipped this on-attack swarm - leave it
            continue
        ctl_recs[rec] = SQ._sval(db, rec, 'itemSkillAutoController')
    # the module MUST agree with this independent derivation (no drift)
    module_fix = SQ._summon_controller_fix_records(db, nm)
    assert set(ctl_recs) == module_fix, (
        "controller fix-set mismatch: independent=%d module=%d symdiff=%s"
        % (len(ctl_recs), len(module_fix), sorted(r.rsplit('\\', 1)[-1]
                                                   for r in (set(ctl_recs) ^ module_fix))))
    # positive control: an amgoz1 SV-original on-attack swarm (direflock) is NOT fixed
    _dire = nm.get(_n(r'records\item\equipmentring\soul\carrionbird\direflock_soul_n.dbr'))
    assert _dire is not None and _dire not in module_fix, \
        "amgoz-designed direflock_soul_n must NOT be in the fix set"
    print("controller fix-set: %d mod-introduced (independent==module); %d amgoz swarms kept"
          % (len(ctl_recs), amgoz_kept))
    # (c) wrong-tier icons on e/l svc_uber rings, EXCLUDING the removed tombguardian souls
    removed = set(tg_soul_recs)
    predicted_icon = set()
    for rec, nn, tier in SQ._iter_uber_rings(db, nm):
        if rec in removed:
            continue
        bmp = SQ._sval(db, rec, 'bitmap')
        if bmp:
            m = SQ._SOUL_ICON_RE.search(bmp)
            if m and m.group(1) != tier:
                predicted_icon.add(rec)
    # (d) raise-only level fixes that will actually change
    level_recs = {}
    for path, fields in SQ._LEVEL_FIX.items():
        rec = nm[_n(path)]
        eff = {f: t for f, t in fields.items()
               if (SQ._ival(db, rec, f) or 0) < t}
        if eff:
            level_recs[rec] = eff

    predicted_mod = set(predicted_icon) | set(level_recs) | set(ctl_recs) | tg_detach
    print("predicted wrong-icon e/l rings : %d" % len(predicted_icon))
    print("crow-controller records        : %d (%s)"
          % (len(ctl_recs), ', '.join(sorted(r.rsplit('\\', 1)[-1] for r in ctl_recs))))
    print("level-fix records (raise-only) : %d (%s)"
          % (len(level_recs), ', '.join(sorted(r.rsplit('\\', 1)[-1] for r in level_recs))))
    print("tombguardian detach record     : %d ; soul records to remove: %d"
          % (len(tg_detach), len(tg_soul_recs)))
    print("predicted total MODIFIED        : %d ; predicted REMOVED: %d"
          % (len(predicted_mod), len(tg_soul_recs)))

    before = {rec: snap_fields(db, rec) for rec in predicted_mod}
    n_records_before = len(db.record_names())

    mod0 = set(db._modified)
    print('\n########## APPLY ##########')
    SQ.apply(db, {})
    delta = set(db._modified) - mod0

    ok = True

    # (1) intended-only MODIFIED diff
    diff_only = delta == predicted_mod
    extra = sorted(r.rsplit('\\', 1)[-1] for r in (delta - predicted_mod))
    missing = sorted(r.rsplit('\\', 1)[-1] for r in (predicted_mod - delta))
    print('\n[1] INTENDED-ONLY DIFF: modified=%d predicted=%d  match=%s'
          % (len(delta), len(predicted_mod), diff_only))
    if extra:
        print('    !!! UNEXPECTED modified:', extra[:12])
    if missing:
        print('    !!! predicted but NOT modified:', missing[:12])
    ok = ok and diff_only

    # (1b) exactly the 3 tombguardian souls REMOVED
    now_names = {_n(x) for x in db.record_names()}
    still_present = [sp for sp in SQ._TG_SOULS if _n(sp) in now_names]
    n_removed = n_records_before - len(db.record_names())
    rem_ok = (n_removed == len(tg_soul_recs)) and not still_present
    print('[1b] RECORD REMOVAL: removed=%d expected=%d tombguardian souls still present=%s  ok=%s'
          % (n_removed, len(tg_soul_recs), [s.rsplit('\\', 1)[-1] for s in still_present], rem_ok))
    ok = ok and rem_ok

    # (2) field-level minimality + (3) correctness
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
        if rec in ctl_recs:
            allowed |= {'itemSkillAutoController'}
        if rec in tg_detach:
            allowed |= {'lootFinger2Item1'}
        stray = changed - allowed
        if stray:
            field_ok = False
            print('    !!! %s changed stray field(s): %s'
                  % (rec.rsplit('\\', 1)[-1], sorted(stray)))
        if 'bitmap' in changed and rec in predicted_icon:
            got = _n(aft.get('bitmap', ('',))[0])
            if got != _n(ICON % tier):
                field_ok = False
                print('    !!! %s icon=%s (want tier %s)'
                      % (rec.rsplit('\\', 1)[-1], got, tier))
        if rec in ctl_recs and 'itemSkillAutoController' in aft:
            field_ok = False
            print('    !!! %s still has itemSkillAutoController' % rec.rsplit('\\', 1)[-1])
    print('[2/3] FIELD MINIMALITY + icon + controller-removal correctness: %s' % field_ok)
    ok = ok and field_ok

    # (3b) every mod-introduced summon ring (A+B, incl. non-svc_uber komara/melalos/
    #      oythroneus/carrionlord) now has NO controller; the module's residual set is
    #      empty; and no amgoz swarm was stripped (direflock keeps its controller).
    crow_ok = True
    for rec in ctl_recs:
        if SQ._field_key(db, rec, 'itemSkillAutoController') is not None:
            crow_ok = False
            print('    !!! %s still has a controller' % rec.rsplit('\\', 1)[-1])
    resid = SQ._summon_controller_fix_records(db)
    if resid:
        crow_ok = False
        print('    !!! module residual fix-set non-empty after apply: %s'
              % sorted(r.rsplit('\\', 1)[-1] for r in resid))
    if SQ._field_key(db, _dire, 'itemSkillAutoController') is None:
        crow_ok = False
        print('    !!! amgoz direflock_soul_n lost its on-attack controller (over-reach)')
    print('[3b] mod-introduced summon controllers removed roster-wide (manual-cast), '
          'amgoz swarms intact: %s' % crow_ok)
    ok = ok and crow_ok

    # (3c) tombguardian monster carries no soul ref
    tg_ok = True
    if tg_mon is not None:
        for k, vals in snap_fields(db, tg_mon).items():
            for v in vals:
                if isinstance(v, str) and 'um_tombguardian_soul' in v.lower():
                    tg_ok = False
                    print('    !!! um_tombguardian_26 still refs soul via %s: %s' % (k, v))
    print('[3d] tombguardian detached (no soul loot ref): %s' % tg_ok)
    ok = ok and tg_ok

    # (3e) fixed-family monotonicity
    print('\n[3e] fixed-family monotonicity')
    mono_ok = True
    nm2 = {_n(x): x for x in db.record_names()}

    def fam_levels(fam_dir_stem, field):
        rn = {t: nm2[_n(r'records\item\equipmentring\soul\%s_%s.dbr'
                       % (fam_dir_stem, t))] for t in ('n', 'e', 'l')}
        return [SQ._ival(db, rn[t], field) for t in ('n', 'e', 'l')]

    checks = [
        ('svc_uber\\crowboar_soul', 'augmentSkillLevel1'),
        ('svc_uber\\crowboar_soul', 'augmentSkillLevel2'),
        ('svc_uber\\crowboar_soul', 'itemSkillLevel'),
        ('svc_uber\\onyxspine_soul', 'augmentSkillLevel1'),
        ('svc_uber\\onyxspine_soul', 'augmentSkillLevel2'),
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
    print('\n[4] verify() (monotonicity + icon + crow-controller + tombguardian gates)')
    try:
        SQ.verify(db, {})
        verify_ok = True
    except SystemExit as e:
        verify_ok = False
        print('    !!! verify RAISED:', str(e)[:200])
    ok = ok and verify_ok

    # (5) idempotency
    mod1 = set(db._modified)
    n_before2 = len(db.record_names())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        SQ.apply(db, {})
    delta2 = set(db._modified) - mod1
    removed2 = n_before2 - len(db.record_names())
    print('\n[5] IDEMPOTENCY: 2nd apply modified %d new, removed %d (expect 0/0)'
          % (len(delta2), removed2))
    ok = ok and (len(delta2) == 0) and (removed2 == 0)

    # (6) negative tests
    print('\n[6] NEGATIVE TESTS')
    # (6a) svc_uber inversion
    crow_l = nm2[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_l.dbr')]
    db.set_field(crow_l, 'augmentSkillLevel1', 1)
    caught_uber = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_uber = 'INVERSION' in str(e)
        print('    svc_uber inversion   -> verify RAISED:', caught_uber)
    db.set_field(crow_l, 'augmentSkillLevel1', 3)
    # (6b) NON-svc_uber (roster-wide) inversion
    blt_e = nm2[_n(r'records\item\equipmentring\soul\spider\bloodtip_soul_e.dbr')]
    db.set_field(blt_e, 'itemSkillLevel', 1)
    caught_roster = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_roster = 'INVERSION' in str(e) and 'bloodtip' in str(e)
        print('    NON-svc_uber inversion-> verify RAISED (names bloodtip):', caught_roster)
    db.set_field(blt_e, 'itemSkillLevel', 7)
    # (6c) wrong-tier icon
    crow_e = nm2[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_e.dbr')]
    db.set_field(crow_e, 'bitmap', 'SVItems\\jewelry\\soul_n_icon.tex')
    caught_icon = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_icon = 'wrong-tier soul' in str(e)
        print('    wrong-tier icon      -> verify RAISED:', caught_icon)
    db.set_field(crow_e, 'bitmap', 'SVItems\\jewelry\\soul_e_icon.tex')
    # (6d) mod-introduced on-attack controller re-injected on an svc_uber (Category A) summon
    _ONATK = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atenemy_onattack.dbr'
    crow_n = nm2[_n(r'records\item\equipmentring\soul\svc_uber\crowboar_soul_n.dbr')]
    db.set_field(crow_n, 'itemSkillAutoController', _ONATK)
    caught_ctl = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_ctl = 'on-attack controller' in str(e) and 'crowboar' in str(e)
        print('    on-attack ctl (svc_uber A) -> verify RAISED (names crowboar):', caught_ctl)
    SQ._remove_field(db, crow_n, 'itemSkillAutoController')
    # (6f) ROSTER-WIDE proof: re-inject on a NON-svc_uber (Category B) SV-original summon
    #      whose SV098 original is controller-free (komara). A svc_uber-scoped gate would
    #      MISS this - the exact vet MEDIUM. Must fail-loud AND name komara.
    komara_n = nm2[_n(r'records\item\equipmentring\soul\zombie\komara_soul_n.dbr')]
    db.set_field(komara_n, 'itemSkillAutoController', _ONATK)
    caught_nonsvc_ctl = False
    try:
        SQ.verify(db, {})
    except SystemExit as e:
        caught_nonsvc_ctl = 'on-attack controller' in str(e) and 'komara' in str(e)
        print('    on-attack ctl (non-svc B) -> verify RAISED (names komara):', caught_nonsvc_ctl)
    SQ._remove_field(db, komara_n, 'itemSkillAutoController')
    # (6e) tombguardian soul re-attached to the monster loot
    caught_tg = False
    if tg_mon is not None:
        db.set_field(tg_mon, 'lootFinger2Item1',
                     [r'records\item\equipmentring\soul\svc_uber\um_tombguardian_soul_n.dbr', '', ''])
        try:
            SQ.verify(db, {})
        except SystemExit as e:
            caught_tg = 'Tomb Guardian retirement' in str(e)
            print('    tombguardian re-attach-> verify RAISED:', caught_tg)
        db.set_field(tg_mon, 'lootFinger2Item1', ['', '', ''])
    else:
        caught_tg = True
    ok = (ok and caught_uber and caught_roster and caught_icon and caught_ctl
          and caught_nonsvc_ctl and caught_tg)

    print('\nRESULT:', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
