#!/usr/bin/env python3
"""Negative + positive tests for the Enslaver roaming-sweep gate
(_verify_roaming_sweep in apply_svc_patches.py) AFTER the GROUP 1 test-yard
whitelist landed. Proves the gate enforces the leak property in BOTH directions
while allowing the dedicated yard pool's legitimate 100% Enslaver:

  POSITIVE 1: the real built arz PASSES (yard pool present at weight 100).
  POSITIVE 2: the yard pool q_yard_enslaver DOES carry the Enslaver at weight 100
              and is EXCLUDED from the swept set (that is why POS1 passes).
  NEGATIVE 1 (weight direction): bump the Enslaver's weight 1 -> 100 in one SWEPT
              (non-yard) trash pool -> gate FAILS (weight-1 rule).
  NEGATIVE 2 (leak direction): inject the Enslaver into a NON-swept, NON-yard pool
              (q_vashkarr_lone) at weight 1 -> gate FAILS (leak guard / set mismatch).
  NEGATIVE 3 (whitelist is load-bearing): blank _EN_YARD_POOLS -> the clean arz now
              FAILS (the yard pool's weight-100 Enslaver is no longer excused).

Usage: py tools/debug/negtest_roaming_yard.py [<built.arz>]
Exit 0 = all five subtests behave as specified.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # tools/
from arz_patcher import ArzDatabase, DATA_TYPE_STRING, DATA_TYPE_INT  # noqa: E402
import apply_svc_patches as asp                # noqa: E402

BS = chr(92)
VK_POOL = r'records\drxmap\proxy\pools\q_vashkarr_lone.dbr'


def gv(db, n, f):
    v = db.get_field_value(n, f)
    return (v[0] if isinstance(v, list) else v)


def enslaver_pools(db):
    """Every ProxyPool carrying the Enslaver in a name slot (mirrors the gate)."""
    enl = asp._EN_BOSS.replace('/', BS).lower()
    out = []
    for n in db.record_names():
        t = gv(db, n, 'templateName')
        if not (t and 'proxypool.tpl' in str(t).lower()):
            continue
        names = [gv(db, n, 'name%d' % i) for i in range(1, 19)]
        if any(x and str(x).replace('/', BS).lower() == enl for x in names):
            out.append(n)
    return out


def swept_set(db):
    """touched = enslaver pools MINUS the whitelisted yard pools (== what the
    build's _sweep_inject_roaming_rare produced)."""
    yard = {p.replace('/', BS).lower() for p in asp._EN_YARD_POOLS}
    return [n for n in enslaver_pools(db) if n.replace('/', BS).lower() not in yard]


def run_gate(db, touched):
    try:
        asp._verify_roaming_sweep(db, touched)
        return 'PASS'
    except SystemExit:
        return 'FAIL'


def enslaver_slot(db, pool):
    """Return the (name-index) slot holding the Enslaver in `pool`, or None."""
    enl = asp._EN_BOSS.replace('/', BS).lower()
    for i in range(1, 19):
        v = gv(db, pool, 'name%d' % i)
        if v and str(v).replace('/', BS).lower() == enl:
            return i
    return None


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        str(HERE.parents[1] / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    db = ArzDatabase.from_arz(Path(arz))

    touched = swept_set(db)
    yard_pool = asp._YARD_ENSLAVER_POOL
    results = []

    # POSITIVE 1: real built arz PASSES.
    results.append(('positive 1 (real built arz)', run_gate(db, touched), 'PASS'))

    # POSITIVE 2: yard pool carries the Enslaver @weight 100 and is NOT in touched.
    slot = enslaver_slot(db, yard_pool)
    yw = gv(db, yard_pool, 'weight%d' % slot) if slot else None
    in_touched = yard_pool.replace('/', BS).lower() in {t.replace('/', BS).lower() for t in touched}
    pos2_ok = (slot is not None and int(yw) == 100 and not in_touched)
    results.append((f'positive 2 (yard pool enslaver w={yw}, excluded={not in_touched})',
                    'OK' if pos2_ok else 'BAD', 'OK'))

    # NEGATIVE 1 (weight direction): bump a swept pool's enslaver weight 1 -> 100.
    victim = touched[0]
    vslot = enslaver_slot(db, victim)
    orig_w = gv(db, victim, 'weight%d' % vslot)
    db.set_field(victim, 'weight%d' % vslot, 100, DATA_TYPE_INT)
    results.append(('negative 1 (swept pool enslaver weight 1->100)',
                    run_gate(db, touched), 'FAIL'))
    db.set_field(victim, 'weight%d' % vslot, int(orig_w), DATA_TYPE_INT)   # restore
    results.append(('  (restore check: gate PASS again)', run_gate(db, touched), 'PASS'))

    # NEGATIVE 2 (leak direction): inject the Enslaver into a NON-swept, NON-yard
    # pool (q_vashkarr_lone) at weight 1 -> leak guard / set-mismatch FAIL.
    had_n4 = gv(db, VK_POOL, 'name4')
    db.set_field(VK_POOL, 'name4', asp._EN_BOSS, DATA_TYPE_STRING)
    db.set_field(VK_POOL, 'weight4', 1, DATA_TYPE_INT)
    results.append(('negative 2 (enslaver leaked into q_vashkarr_lone)',
                    run_gate(db, touched), 'FAIL'))
    db.set_field(VK_POOL, 'name4', str(had_n4) if had_n4 else '', DATA_TYPE_STRING)
    db.set_field(VK_POOL, 'weight4', 0, DATA_TYPE_INT)                     # neutralize
    results.append(('  (restore check: gate PASS again)', run_gate(db, touched), 'PASS'))

    # NEGATIVE 3 (whitelist is load-bearing): blank _EN_YARD_POOLS -> the clean
    # arz now FAILS because the yard pool's weight-100 Enslaver is no longer
    # excluded (proves the whitelist is what allows the yard, not a loophole).
    saved_wl = asp._EN_YARD_POOLS
    asp._EN_YARD_POOLS = set()
    results.append(('negative 3 (whitelist blanked -> yard pool no longer excused)',
                    run_gate(db, touched), 'FAIL'))
    asp._EN_YARD_POOLS = saved_wl
    results.append(('  (restore check: gate PASS again)', run_gate(db, touched), 'PASS'))

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
