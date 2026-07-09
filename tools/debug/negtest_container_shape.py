#!/usr/bin/env python3
"""Negative + positive tests for the P0/build30.1 container loot contract
(_validate_container_loot_shapes in build_svc_database.py), CALIBRATED to the
base game's measured idioms (611 FixedItemLoot records: 95 active-no-name
'chance of nothing' slots, 199 dormant-named parked slots - both are WARN-only;
see the gate docstring).

POSITIVE 1: the real shipped build30 chest record must PASS.
POSITIVE 2: an active-slot-without-name idiom (hermit-mage shape) must PASS.
NEGATIVE 1: a DANGLING lootNName1 (table not in the arz) must FAIL.
NEGATIVE 2: an emptied numSpawnMinEquation must FAIL.

Usage: py tools/debug/negtest_container_shape.py [<built.arz>]
Exit 0 = all four subtests behave as specified.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # tools/
from arz_patcher import ArzDatabase, DATA_TYPE_STRING  # noqa: E402
import build_svc_database as bsd              # noqa: E402

CHEST = r'records\item\containers\defaultloot\tutorialpotionchest.dbr'


def run_gate(db):
    try:
        bsd._validate_container_loot_shapes(db)
        return 'PASS'
    except SystemExit:
        return 'FAIL'


def field(db, rec, name):
    for k, tf in db.get_fields(rec).items():
        if k.split('###')[0] == name:
            return tf
    return None


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        str(HERE.parents[1] / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    db = ArzDatabase.from_arz(Path(arz))
    if not db.has_record(CHEST):
        print(f'ERROR: chest record missing from {arz}')
        return 2
    db._modified = {CHEST}

    results = []

    # POSITIVE 1: the real record must PASS
    results.append(('positive 1 (real build30 chest)', run_gate(db), 'PASS'))

    # POSITIVE 2: the base-precedented 'chance of nothing' idiom must PASS
    #   (active chance, name field emptied - the hermit-mage shape)
    nm = field(db, CHEST, 'loot2Name1')
    saved = list(nm.values)
    nm.values = []
    results.append(('positive 2 (active-no-name idiom)', run_gate(db), 'PASS'))
    nm.values = saved

    # NEGATIVE 1: dangling loot table ref must FAIL
    nm.values = [r'records\item\loottables\does\not\exist_anywhere.dbr']
    results.append(('negative 1 (dangling lootName1)', run_gate(db), 'FAIL'))
    nm.values = saved

    # NEGATIVE 2: emptied numSpawnMinEquation must FAIL
    eq = field(db, CHEST, 'numSpawnMinEquation')
    saved_eq = list(eq.values)
    eq.values = ['']
    results.append(('negative 2 (empty numSpawnMinEquation)', run_gate(db), 'FAIL'))
    eq.values = saved_eq

    ok = True
    print()
    for label, got, want in results:
        verdict = 'OK' if got == want else 'WRONG'
        if got != want:
            ok = False
        print(f'  {verdict:5s} {label}: gate={got} (expected {want})')
    print('\nNEGTEST RESULT:', 'ALL OK' if ok else 'MISMATCH')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
