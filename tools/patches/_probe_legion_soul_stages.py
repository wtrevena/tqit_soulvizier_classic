"""b56 legion_soul_stages implementer/vet probe (READ-ONLY vs the arz on disk).

Loads a golden arz, applies legion_soul_stages.apply() IN MEMORY (never writes),
and proves:
  * the RCA: every actorToSpawnOnDeath chain with >=2 soul-bearing stages,
    classified same-soul (the Legion defect) vs distinct-soul (design-ruling).
  * the fix: exactly the Legion non-terminals are zeroed; terminal + all
    distinct-soul chains untouched; the surviving Legion drop stays obtainable.
  * verify() PASSES; a planted second same-soul stage FAILS verify() (negative).
  * idempotency.

Run:
  PYTHONIOENCODING=utf-8 py tools/patches/_probe_legion_soul_stages.py \
      work/SoulvizierClassic/Database/SoulvizierClassic.arz
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]      # tools/
sys.path.insert(0, str(_TOOLS))
from arz_patcher import ArzDatabase
from patches import legion_soul_stages as M


def _scalar(v):
    return (v[0] if v else None) if isinstance(v, list) else v


def _chance(db, rec):
    v = _scalar(db.get_field_value(rec, 'chanceToEquipFinger2'))
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def _snapshot(db):
    out = {}
    for n in db.record_names():
        _ch, refs = M._soul_drop(db, n)
        if refs:
            out[n] = _chance(db, n)
    return out


LEG = r'records\creature\monster\eurynomus'
NONTERM = [rf'{LEG}\um_legion_28.dbr', rf'{LEG}\um_legion_28a.dbr',
           rf'{LEG}\um_legion_28b.dbr']
TERM = rf'{LEG}\um_legion_28c.dbr'


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        r'work/SoulvizierClassic/Database/SoulvizierClassic.arz'
    db = ArzDatabase.from_arz(Path(arz))
    if not hasattr(db, '_modified') or db._modified is None:
        db._modified = set()
    names = db.record_names()
    canon = {n.replace('/', '\\').lower(): n for n in names}

    def R(p):
        return canon.get(p.replace('/', '\\').lower())

    # ---- RCA dump (chains before the fix) ----
    res0 = M._analyze(db)
    print("== RCA: same-soul chains (the Legion defect) ==")
    for c in res0['same_soul_chains']:
        print(f"   soul '{c['soul']}': keep {[Path(x).name for x in c['keep']]}; "
              f"zero {[Path(x).name for x in c['zeroed']]}")
    print("== RCA: distinct-soul chains (design ruling, NOT auto-fixed) ==")
    for c in res0['distinct_multi']:
        print(f"   {' -> '.join(Path(m).name for m in c['members'])}  souls={c['souls']}")
    print(f"== RCA: inverse (empty) chains: {res0['inverse_empty']}")

    before = _snapshot(db)
    assert all(before[R(p)] == 66.0 for p in NONTERM), "pre: legion non-terminals not 66"
    assert before[R(TERM)] == 66.0, "pre: terminal 28c not 66"

    # ---- apply ----
    M.apply(db, {})
    after = _snapshot(db)
    changed = {n for n in before if before[n] != after[n]}
    assert changed == {R(p) for p in NONTERM}, \
        f"FAIL exact-diff: {sorted(changed)}"
    assert all(_chance(db, R(p)) == 0.0 for p in NONTERM), "FAIL non-terminals not 0"
    assert _chance(db, R(TERM)) == 66.0, "FAIL terminal changed"
    _ch, tref = M._soul_drop(db, R(TERM))
    assert any('legion_soul' in r.lower() for r in tref), "FAIL terminal lost legion_soul"
    print(f"\nPASS exact-diff: {len(changed)} records zeroed (Legion non-terminals); "
          "terminal keeps legion_soul; distinct-soul chains untouched.")

    # ---- verify PASS ----
    M.verify(db, {})
    print("PASS verify().")

    # ---- idempotent ----
    b2 = _snapshot(db); M.apply(db, {}); a2 = _snapshot(db)
    assert b2 == a2, "FAIL not idempotent"
    print("PASS idempotent.")

    # ---- negative: plant a second same-soul stage ----
    db.set_field(R(NONTERM[2]), 'chanceToEquipFinger2', 66.0)
    db._modified.add(R(NONTERM[2]))
    tripped = False
    try:
        M.verify(db, {})
    except SystemExit:
        tripped = True
    assert tripped, "FAIL negative test did not trip verify()"
    print("PASS negative test (re-armed stage trips verify()).")
    print("\nALL PROBE CHECKS PASSED")


if __name__ == '__main__':
    main()
