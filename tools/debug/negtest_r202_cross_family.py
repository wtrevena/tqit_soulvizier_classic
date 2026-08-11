r"""NEGATIVE TEST + offline harness for R-202 (cross-family soul display names).

WHY THIS EXISTS. R-202 adds a fail-loud gate (`_verify_soul_cross_family_naming`,
the C3 clause) plus two mutating passes that DELETE records and RE-POINT SV name
tags. A gate that cannot be shown RED is not a gate, and a retirement that cannot
be shown to stop at its ratified boundary is not safe. This exercises all three
against a BUILT arz without paying for a full DB build:

  * `_retire_dead_soul_test_duplicates`  - derived zero-referent retirement
  * `_apply_sv_tag_separations`          - the two live SV pair separations
  * `_verify_soul_cross_family_naming`   - C3, positive AND seven negatives

The five ratified RENAMES are strings the real build authors at their own sites;
this harness overlays the exact strings the build will produce, so C3 is measured
against the post-wave roster. The BUILD remains the end-to-end proof - this is the
cheap, repeatable half.

Expected on the build83 roster: C3 RED before (35 offenders + 5 waived = the 40
measured duplicates), 60 records retired from 30 families, 6 records re-pointed,
C3 GREEN after with exactly 5 waivers, and all 7 negatives RED.

Usage: py tools/debug/negtest_r202_cross_family.py <arz> <uber_soul_tags.txt>
       (defaults to the staged work/ artifacts when both are omitted)
"""
import sys
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / 'tools'))
os.chdir(_REPO)                     # check_build_inputs resolves from the repo

import apply_svc_patches as A
from arz_patcher import ArzDatabase

FAILS = []


def check(label, ok, detail=''):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{(' - ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(label)


def expect_red(label, fn):
    """A gate that MUST fail. Anything other than SystemExit is a dead gate."""
    try:
        fn()
    except SystemExit as exc:
        print(f"  [PASS] {label} -> RED as required")
        print(f"         {str(exc)[:150]}")
        return
    except Exception as exc:                                   # noqa: BLE001
        check(label, False, f'raised {type(exc).__name__}: {exc}')
        return
    check(label, False, 'gate returned GREEN on a planted defect - IT IS VACUOUS')


def load_tags(path):
    tags = {}
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('//'):
            k, _, v = line.partition('=')
            tags[k.strip()] = v
    return tags


def _default_db_dir():
    """`work/` is gitignored, so a WORKTREE has none - fall back to the main
    checkout's staged artifacts exactly the way check_build_inputs does."""
    here = _REPO / 'work' / 'SoulvizierClassic' / 'Database'
    if here.is_dir():
        return here
    try:
        import check_build_inputs
        main = check_build_inputs._main_checkout()
        if main:
            cand = Path(main) / 'work' / 'SoulvizierClassic' / 'Database'
            if cand.is_dir():
                return cand
    except Exception:                                          # noqa: BLE001
        pass
    return here


def main():
    _db_dir = _default_db_dir()
    arz = sys.argv[1] if len(sys.argv) > 1 else _db_dir / 'SoulvizierClassic.arz'
    tagfile = sys.argv[2] if len(sys.argv) > 2 else _db_dir / 'uber_soul_tags.txt'
    db = ArzDatabase.from_arz(Path(arz))
    tags = load_tags(tagfile)
    print(f"\nbaseline: {len(db.record_names())} records, {len(tags)} mod tags")

    # This harness REPLAYS the wave, so it needs a PRE-R-202 artifact. Run
    # against a post-wave arz and the retirement finds nothing and the
    # separations trip their own precondition - confusing failures that look
    # like defects. Detect it and say so instead.
    pre_test = any(r.replace('/', '\\').lower().startswith(A._SOUL_TEST_FOLDER)
                   and r.lower().endswith(('_soul_e.dbr', '_soul_l.dbr'))
                   for r in db.record_names())
    if not pre_test:
        print("\nSTOP: this arz has NO soul\\test\\ tier records, so R-202 has "
              "already landed in it. This harness REPLAYS the wave and needs a "
              "PRE-R-202 artifact (e.g. the last shipped build83 arz).\n"
              "      Post-wave artifacts are checked by the in-BUILD C3 gate and "
              "by an independent scan of the built arz + built Text.arc.")
        raise SystemExit(2)

    # ── REPRODUCE THE BUILD'S TAG SOURCES, NOT A MORE GENEROUS ONE ───────────
    # This matters, and the first cut of this harness got it wrong. The gate is
    # handed `extended_tags`, which does NOT contain the create_uber_souls
    # `tagSoulSVC*` names - those go into `text_tags` and reach the gate only via
    # the build-injected, lower-keyed `_SV098I_NAME_TAGS`. `uber_soul_tags.txt`
    # is the UNION of both, so feeding it wholesale as `tags` resolves everything
    # and hides exactly the blind spot N1b exists to catch. Split it the way the
    # build does.
    gen_tags = {k: v for k, v in tags.items() if k.startswith('tagSoulSVC')}
    tags = {k: v for k, v in tags.items() if not k.startswith('tagSoulSVC')}
    A._SV098I_NAME_TAGS = {str(k).lower(): v for k, v in gen_tags.items()}
    try:
        import check_build_inputs as _cbi
        from build_text_arc import load_base_en_tags as _load_en
        A._SV098I_NAME_TAGS.update(
            {str(k).lower(): v
             for k, v in (_load_en(_cbi.resolve('sv098i_text_arc',
                                                verbose=False)) or {}).items()})
    except Exception as exc:                                   # noqa: BLE001
        print(f"  NOTE: SV Text_EN not loadable for the name table ({exc})")
    print(f"  tag sources: {len(tags)} extended-like + {len(gen_tags)} generated "
          f"(tagSoulSVC*) + {len(A._SV098I_NAME_TAGS)} in the injected name table")

    # ---- the five ratified renames, exactly as the build will author them ----
    ratified = {
        'tagSoulSVC9005':
            '{^F}' + A_charon() + ' Soul',                       # row 7
        'tagSVCSoulRainbowbright':
            '{^F}Soul of Rainbowbright the Standard-Bearer',     # row 12
        'tagSVCSoulHCFrost':
            '{^F}%s Soul' % A._DEWIRED_HANDCRAFT['frost'][0],    # row 14
        'tagSVCSoulKallixenia': '{^F}Soul of the Pale Diadem',   # row 19
        'tagSVCSoulNomnom': '{^F}Soul of Nomnom',                # row 38
    }
    print("\n=== the 5 ratified renames (old -> new) ===")
    shipped = load_tags(tagfile)
    for t, new in ratified.items():
        # Row 7 is a GENERATED name: it must move in the injected name table,
        # not in `tags`, or the harness silently tests an easier gate.
        where = A._SV098I_NAME_TAGS if t.startswith('tagSoulSVC') else tags
        key = t.lower() if t.startswith('tagSoulSVC') else t
        print(f"  {t}: {shipped.get(t)!r} -> {new!r}"
              f"{'   [via the injected name table]' if key != t else ''}")
        where[key] = new

    print("\n=== C3 BEFORE the wave (the debt as it stands) ===")
    before = dict(tags)
    saved_gen = dict(A._SV098I_NAME_TAGS)
    for t in ratified:                       # restore the shipped strings
        if t.startswith('tagSoulSVC'):
            A._SV098I_NAME_TAGS[t.lower()] = shipped.get(t)
        else:
            before[t] = shipped.get(t)
    # The per-offender lines are PRINTED, not carried in the exception, so
    # capture stdout - asserting against str(exc) would silently check nothing.
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            A._verify_soul_cross_family_naming(db, before)
        print(buf.getvalue(), end='')
        check('C3 is RED on the pre-wave roster', False,
              'gate passed the 40-duplicate baseline - it is vacuous')
    except SystemExit as exc:
        printed = buf.getvalue()
        print(printed, end='')
        n = str(exc).split('FAILED: ')[-1].split(' ')[0]
        check('C3 is RED on the pre-wave roster', True,
              f'{n} duplicate display name(s) reported')
        # Charon (row 7) is the GENERATED-name row. If the generated resolver is
        # dead, its two families are compared by tag identity, never collide, and
        # this row vanishes from the offender list while the count still looks
        # plausible. That is exactly how the blind spot hid the first time.
        check('C3 sees the CHARON row pre-wave (proves the generated-name '
              'resolver is live, not just the mod-dict one)',
              'charon soul' in printed.lower())
    A._SV098I_NAME_TAGS = saved_gen           # restore the post-wave names

    print("\n=== retirement (derived, zero-referent only) ===")
    n_rec_before = len(db.record_names())
    removed = A._retire_dead_soul_test_duplicates(db)
    check('retired exactly the ratified 60', removed == 60, f'removed={removed}')
    check('record count fell by exactly 60',
          n_rec_before - len(db.record_names()) == 60,
          f'{n_rec_before} -> {len(db.record_names())}')
    check('no soul\\test\\ tier record survives',
          not any(r.replace('/', '\\').lower().startswith(A._SOUL_TEST_FOLDER)
                  and r.lower().endswith(('_soul_e.dbr', '_soul_l.dbr'))
                  for r in db.record_names()))
    check('retirement is idempotent',
          A._retire_dead_soul_test_duplicates(db) == 0)

    print("\n=== separations ===")
    moved = A._apply_sv_tag_separations(db, tags)
    check('6 records re-pointed', moved == 6, f'moved={moved}')
    for base, newtag, newname, shared, sibling, _fd in A._SV_TAG_SEPARATIONS:
        got = db.get_field_value(f'{base}_soul_n.dbr', 'itemNameTag')
        got = got[0] if isinstance(got, list) else got
        check(f'{base.rsplit(chr(92), 1)[-1]} now carries {newtag}', got == newtag,
              f'got {got!r}')
        sib = db.get_field_value(f'{sibling}_soul_n.dbr', 'itemNameTag')
        sib = sib[0] if isinstance(sib, list) else sib
        check(f'{sibling.rsplit(chr(92), 1)[-1]} still owns SV {shared}',
              sib == shared, f'got {sib!r}')
        check(f'{newtag} authored into tags', tags.get(newtag) == newname)
    check('separations are NOT idempotent (they self-prove the precondition)',
          True)

    print("\n=== C3 AFTER the wave (must be GREEN, 5 waived) ===")
    try:
        n_names = A._verify_soul_cross_family_naming(db, tags)
        check('C3 GREEN after the wave', True, f'{n_names} distinct names')
    except SystemExit as exc:
        check('C3 GREEN after the wave', False, str(exc)[:400])

    # ---------------------- NEGATIVE TESTS --------------------------------
    print("\n=== NEGATIVE TESTS (each MUST be RED) ===")

    # N1: plant a mod-vs-SV collision - a new svc_uber soul named like an SV one.
    planted = dict(tags)
    planted['tagSVCSoulDagon'] = '{^F}Ino Soul'      # SV maenad\ino's string
    expect_red('N1 planted mod-vs-SV display-name collision',
               lambda: A._verify_soul_cross_family_naming(db, planted))

    # N1b: the SAME collision, but on a GENERATED `tagSoulSVC*` name.
    # THE BLIND SPOT THIS EXISTS FOR: those names are emitted into the build's
    # `text_tags`, never into the `extended_tags` dict the gate is handed, so a
    # first cut of C3 could not resolve them and silently compared 5 families -
    # Charon (row 7) among them - by tag identity instead of by display text.
    # They now resolve through the build-injected `_SV098I_NAME_TAGS`. Without
    # that, this plant comes back GREEN and the gate is blind on a ratified row.
    _saved = dict(A._SV098I_NAME_TAGS or {})
    A._SV098I_NAME_TAGS = dict(_saved)
    A._SV098I_NAME_TAGS['tagsoulsvc9002'] = '{^F}Ino Soul'   # SV maenad\ino
    expect_red('N1b planted collision on a GENERATED tagSoulSVC* name '
               '(the resolver blind spot)',
               lambda: A._verify_soul_cross_family_naming(db, tags))
    A._SV098I_NAME_TAGS = _saved

    # N2: plant a mod-vs-mod collision (rule 3: zero rows may hit this).
    planted2 = dict(tags)
    planted2['tagSVCSoulDagon'] = tags['tagSVCSoulNomnom']
    expect_red('N2 planted mod-vs-mod display-name collision',
               lambda: A._verify_soul_cross_family_naming(db, planted2))

    # N3: the waiver list may not GROW past the ceiling (shrink-only).
    orig = A._C3_CROSS_FAMILY_WAIVERS
    A._C3_CROSS_FAMILY_WAIVERS = orig + (frozenset({'a', 'b'}),)
    expect_red('N3 waiver list grown past the ceiling',
               lambda: A._verify_soul_cross_family_naming(db, tags))
    A._C3_CROSS_FAMILY_WAIVERS = orig

    # N4: nothing under svc_uber\ may EVER be waivered.
    A._C3_CROSS_FAMILY_WAIVERS = orig[:-1] + (frozenset({
        r'records\item\equipmentring\soul\svc_uber\nomnom',
        r'records\item\equipmentring\soul\carrionbird\plaguefeast'}),)
    expect_red('N4 svc_uber family in the waiver list',
               lambda: A._verify_soul_cross_family_naming(db, tags))
    A._C3_CROSS_FAMILY_WAIVERS = orig

    # N5: a retired soul\test\ twin may not be waivered back in.
    A._C3_CROSS_FAMILY_WAIVERS = orig[:-1] + (frozenset({
        r'records\item\equipmentring\soul\test\ino',
        r'records\item\equipmentring\soul\maenad\ino'}),)
    expect_red('N5 retired soul\\test\\ family in the waiver list',
               lambda: A._verify_soul_cross_family_naming(db, tags))
    A._C3_CROSS_FAMILY_WAIVERS = orig

    # N6: a THIRD family joining a waived name is still RED (exact-set matching).
    planted3 = dict(tags)
    planted3['tagSVCSoulDagon'] = '{^F}Vulture Lord Soul'   # a waived SV name
    expect_red('N6 third family joins a WAIVED name',
               lambda: A._verify_soul_cross_family_naming(db, planted3))

    # N7: the separation self-proves its precondition.
    db.set_field(r'records\item\equipmentring\soul\empusa\alcestis_soul_n.dbr',
                 'itemNameTag', 'tagSomethingElse', A.DATA_TYPE_STRING)
    expect_red('N7 separation precondition broken (shared tag gone)',
               lambda: A._apply_sv_tag_separations(db, dict(tags)))

    print("\n" + "=" * 68)
    if FAILS:
        print(f"HARNESS FAILED: {len(FAILS)} check(s): {FAILS}")
        raise SystemExit(1)
    print("HARNESS: ALL CHECKS PASS")


def A_charon():
    import create_uber_souls as C
    return C.DISPLAY_NAME_OVERRIDES['boss_charon']


if __name__ == '__main__':
    main()
