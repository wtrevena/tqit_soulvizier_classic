#!/usr/bin/env python3
r"""Planted negative + positive tests for the b94 PART A gate
(tools/patches/uber_apex_orb.py :: verify).

A gate that never fires is worthless (the contract-suite discipline). This proves
the orb-calibre gate actually catches every failure mode it claims to guard.

POSITIVE 1: the real built .arz must PASS.
NEGATIVE 1: a champion put back on genericbossorb_04 must FAIL (the whole point).
NEGATIVE 2: a THIRD record pointed at genericbossorb_05 must FAIL (scope creep).
NEGATIVE 3: an orb05 loot table whose numSpawn multiplier is cut below Leinth's
            must FAIL (calibre regression).
NEGATIVE 4: an orb05 loot4Chance dropped back to the orb04 value must FAIL.
NEGATIVE 5: a unique-entry weight lowered below Leinth's must FAIL.
NEGATIVE 6: a broken orb05 chain link (pool -> chest) must FAIL.
NEGATIVE 7: R-48 collateral damage (a champion's soul rate cut) must FAIL.
NEGATIVE 8: an orb04 consumer chest retargeted (donor-chain tamper) must FAIL.

Usage: py tools/debug/negtest_uber_apex_orb.py [<built.arz>]
Exit 0 = every subtest behaves as specified.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                 # tools/
sys.path.insert(0, str(HERE.parent / 'patches'))     # not needed, but harmless
from arz_patcher import ArzDatabase                  # noqa: E402
from patches import uber_apex_orb as M               # noqa: E402


def run_gate(db):
    try:
        M.verify(db, {})
        return 'PASS'
    except SystemExit:
        return 'FAIL'


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        str(HERE.parents[1] / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    p = Path(arz)
    if not p.exists():
        print(f'ERROR: arz not found: {arz}')
        return 2
    db = ArzDatabase.from_arz(p)

    results = []

    def sub(label, mutate, want):
        """Snapshot -> mutate -> gate -> restore."""
        saved = []
        for rec, field in mutate.get('_touch', []):
            saved.append((rec, field, db.get_field_value(rec, field)))
        mutate['do']()
        got = run_gate(db)
        for rec, field, val in saved:
            db.set_field(rec, field, val)
        results.append((label, got, want))

    ENSLAVER, DEVOURER = (r for _l, r in M._CHAMPIONS)
    N_TABLE = M.CHAIN['normal'][5]
    N_POOL = M.CHAIN['normal'][1]
    N_CHEST = M.CHAIN['normal'][3]
    ORB04_CHEST_N = M.CHAIN['normal'][2]

    # POSITIVE 1
    results.append(('positive 1 (real built arz)', run_gate(db), 'PASS'))

    # NEGATIVE 1: champion back on orb04
    sub('negative 1 (Enslaver reverted to genericbossorb_04)',
        {'_touch': [(ENSLAVER, M._TREASURE)],
         'do': lambda: db.set_field(ENSLAVER, M._TREASURE, M.ORB04)}, 'FAIL')

    # NEGATIVE 2: a third record joins orb05
    third = r'records\creature\monster\questbosses\boss_titan_typhon_42.dbr'
    if db.has_record(third):
        sub('negative 2 (a third record points at genericbossorb_05)',
            {'_touch': [(third, M._TREASURE)],
             'do': lambda: db.set_field(third, M._TREASURE, M.ORB05)}, 'FAIL')

    # NEGATIVE 3: spawn multiplier cut below Leinth's
    sub('negative 3 (orb05 numSpawnMin multiplier cut below Leinth)',
        {'_touch': [(N_TABLE, 'numSpawnMinEquation')],
         'do': lambda: db.set_field(N_TABLE, 'numSpawnMinEquation',
                                    '(3+(1.6*numberOfPlayers))*0.9')}, 'FAIL')

    # NEGATIVE 4: loot4Chance back to the orb04 value
    sub('negative 4 (orb05 loot4Chance reverted to 12.7)',
        {'_touch': [(N_TABLE, 'loot4Chance')],
         'do': lambda: db.set_field(N_TABLE, 'loot4Chance', 12.7)}, 'FAIL')

    # NEGATIVE 5: a unique weight lowered
    uw_key = None
    ff = M._fields(db, N_TABLE)
    for k, v in sorted(ff.items()):
        if k.startswith('loot') and 'Name' in k and v and isinstance(v[0], str) \
                and 'unique' in v[0].lower():
            uw_key = k.replace('Name', 'Weight')
            break
    if uw_key:
        sub('negative 5 (an orb05 unique-entry weight cut below Leinth\'s 50)',
            {'_touch': [(N_TABLE, uw_key)],
             'do': lambda: db.set_field(N_TABLE, uw_key, 27)}, 'FAIL')

    # NEGATIVE 6: broken chain link
    sub('negative 6 (orb05 normal pool no longer points at its chest)',
        {'_touch': [(N_POOL, 'fixedItemName1')],
         'do': lambda: db.set_field(N_POOL, 'fixedItemName1',
                                    r'records\item\containers\new\nope.dbr')}, 'FAIL')

    # NEGATIVE 7: R-48 collateral damage
    sub('negative 7 (Devourer soul rate cut below R-48\'s 100)',
        {'_touch': [(DEVOURER, 'chanceToEquipFinger2')],
         'do': lambda: db.set_field(DEVOURER, 'chanceToEquipFinger2', 25.0)}, 'FAIL')

    # NEGATIVE 8: donor-chain tamper
    sub('negative 8 (the orb04 normal chest retargeted - donor chain tampered)',
        {'_touch': [(ORB04_CHEST_N, 'tables')],
         'do': lambda: db.set_field(ORB04_CHEST_N, 'tables', N_TABLE)}, 'FAIL')

    # FINAL POSITIVE: everything restored, gate green again
    results.append(('positive 2 (all mutations restored)', run_gate(db), 'PASS'))

    ok = 0
    print()
    for label, got, want in results:
        good = got == want
        ok += good
        print(f'  [{"PASS" if good else "FAIL"}] {label}: gate={got} (expected {want})')
    print(f'\n{ok}/{len(results)} subtests behaved as specified')
    return 0 if ok == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
