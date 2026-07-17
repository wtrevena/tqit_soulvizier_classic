#!/usr/bin/env python3
"""Negative + positive tests for the B80 formula-name gate
(tools/patches/formula_names.py verify() / find_tag_sharing_offenders).

POSITIVE 1: the real shipped arz, AFTER formula_names.apply(), must PASS verify().
POSITIVE 2: the real shipped arz BEFORE the fix (raw, as read from disk) must FAIL
            verify() (proves the gate actually catches the bug it was written for).
NEGATIVE 1 (planted): repoint a DIFFERENT, already-correct supra formula's
            description onto another supra formula's tag (a fresh, synthetic
            mismatch) -> find_tag_sharing_offenders() must report it.
POSITIVE 3: idempotent - running apply() twice on the same db is a no-op the
            second time and verify() still PASSes.

Usage: py tools/debug/negtest_formula_names.py [<built.arz>]
Exit 0 = all subtests behave as specified.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))            # tools/
sys.path.insert(0, str(HERE.parent / 'patches'))  # tools/patches/
from arz_patcher import ArzDatabase  # noqa: E402
import formula_names as FN           # noqa: E402


def run_verify(db):
    try:
        FN.verify(db, {})
        return 'PASS'
    except SystemExit:
        return 'FAIL'


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        str(HERE.parents[1] / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    results = []

    # POSITIVE 2: raw (pre-fix) state must FAIL.
    db_raw = ArzDatabase.from_arz(Path(arz))
    if not db_raw.has_record(FN._AR_HUNTER_HELM_FORMULA):
        print(f'ERROR: {FN._AR_HUNTER_HELM_FORMULA} missing from {arz}')
        return 2
    current = FN._get_field(db_raw, FN._AR_HUNTER_HELM_FORMULA, 'description')
    if current == FN._WRONG_TAG:
        results.append(('positive 2 (raw pre-fix state)', run_verify(db_raw), 'FAIL'))
    elif current == FN._CORRECT_TAG:
        print('  NOTE: input arz already has the fix applied (description == '
              f'{FN._CORRECT_TAG!r}); positive-2 (pre-fix must FAIL) subtest is '
              'not exercisable against this input and is SKIPPED. Re-run against '
              'a pre-fix arz to exercise it, or trust positive-1/negative-1 below.')
    else:
        print(f'  WARNING: unexpected description {current!r} on raw input; '
              'positive-2 subtest skipped.')

    # POSITIVE 1: apply() then verify() must PASS.
    db_fixed = ArzDatabase.from_arz(Path(arz))
    db_fixed._modified = set()
    FN.apply(db_fixed, {})
    results.append(('positive 1 (post-fix)', run_verify(db_fixed), 'PASS'))

    # POSITIVE 3: idempotent - apply() again is a no-op, still PASS.
    FN.apply(db_fixed, {})
    results.append(('positive 3 (idempotent re-apply)', run_verify(db_fixed), 'PASS'))
    after_desc = FN._get_field(db_fixed, FN._AR_HUNTER_HELM_FORMULA, 'description')
    if after_desc != FN._CORRECT_TAG:
        print(f'  ERROR: after apply(), description = {after_desc!r}, expected '
              f'{FN._CORRECT_TAG!r}')
        return 2

    # NEGATIVE 1: plant a fresh mismatch (independent of the real bug) - repoint
    # ar_melee_helm_formula.dbr's description onto ar_caster_legs_formula's tag
    # (two DIFFERENT supra results, a synthetic collision) - the gate must catch it.
    db_neg = ArzDatabase.from_arz(Path(arz))
    db_neg._modified = set()
    FN.apply(db_neg, {})  # start from the fixed state (real bug not a confound)
    plant_target = r'records\drxitem\supra\recipes\ar_melee_helm_formula.dbr'
    plant_tag = FN._get_field(db_neg, r'records\drxitem\supra\recipes\ar_caster_legs_formula.dbr', 'description')
    if not db_neg.has_record(plant_target) or not plant_tag:
        print('  ERROR: negative-test fixture records missing')
        return 2
    db_neg.set_field(plant_target, 'description', plant_tag)
    offenders = FN.find_tag_sharing_offenders(db_neg)
    planted_seen = any(tag == plant_tag for tag, _entries in offenders)
    results.append(('negative 1 (planted mismatch)',
                     'FAIL' if planted_seen else 'PASS-WRONGLY', 'FAIL'))

    print()
    ok = True
    for name, got, expected in results:
        status = 'OK' if got == expected else 'MISMATCH'
        if status != 'OK':
            ok = False
        print(f'  [{status}] {name}: got={got} expected={expected}')

    if ok:
        print('\nALL SUBTESTS BEHAVED AS SPECIFIED.')
        return 0
    print('\nSOME SUBTESTS DID NOT BEHAVE AS SPECIFIED - see MISMATCH above.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
