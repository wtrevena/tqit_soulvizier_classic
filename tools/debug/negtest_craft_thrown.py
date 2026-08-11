r"""negtest_craft_thrown.py - NEGATIVE TESTS for the craft-chain + thrown gate.

A gate that has never been seen to FAIL is not a gate. This plants each defect the
contract exists to catch into an in-memory copy of the database and asserts the gate
reds on it - and then asserts the UNTOUCHED build is green, so a gate that reds on
everything (or on nothing) is caught too.

Planted defects, one per rule:
  N1  F1  - strip both supra pools out of the Normal act tables  -> Normal formula
            coverage collapses to 0/42 (the exact shipped defect).
  N2  F1  - strip supra_special ONLY  -> Mortok's Skull alone loses Normal coverage
            (the one-craftable hole the first dry run actually found).
  N3  G0  - repoint a thrown formula back onto a Ragnarok ghost record -> a reagent
            that does not exist in the database.
  N4  G1  - unhook the artifact reagent table from `04_l_misc` -> 6 non-MI reagents
            become unreachable from every legendary chest.
  N5  G2  - drop an entry from the committed MI roster -> exemption-roster drift.
  N6  C1  - empty the legendary thrown table -> the thrown class is unpayable at its
            own tier on every legendary chest.
  N7  C2  - put the legendary thrown table on the NORMAL master -> legendary thrown
            reachable from Normal (the R-100 #17 tier law).
  N8  B3  - a control on the neighbouring rule: the same N7 edit must ALSO red
            svc_loot_breadth's Normal tier check, proving the two gates see it.

Usage: py tools/debug/negtest_craft_thrown.py <arz>
"""
import copy
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))
from arz_patcher import ArzDatabase
import svc_craft_thrown as SCT
import svc_loot_breadth as SLB


def _fresh(path):
    """A pristine db per test (records are decoded lazily, so a reload is the only
    honest isolation)."""
    return ArzDatabase.from_arz(path)


def _clear_members(db, lk, table, limit=48):
    real = lk.real(table)
    for i in range(1, limit):
        if SLB._sc(db.get_field_value(real, 'lootName%d' % i)):
            db.set_field(real, 'lootName%d' % i, '')
            db.set_field(real, 'lootWeight%d' % i, 0)
    return real


def _drop_member(db, lk, table, needle):
    real = lk.real(table)
    hit = 0
    for i, nm, _w in SCT._members(db, real):
        if needle in SLB._n(nm):
            db.set_field(real, 'lootName%d' % i, '')
            db.set_field(real, 'lootWeight%d' % i, 0)
            hit += 1
    return hit


def _run(label, rule, db, expect_fail=True):
    problems, _stats = SCT.audit_db(db)
    hit = [p for p in problems if p.startswith(rule)]
    ok = bool(hit) if expect_fail else not problems
    print("  %-4s %-3s %-58s %s" % (label, rule, ('EXPECT RED' if expect_fail
                                                  else 'EXPECT GREEN'),
                                    'PASS' if ok else 'FAIL'))
    if hit:
        print("        %s" % hit[0][:150])
    if not ok and not expect_fail:
        for p in problems[:3]:
            print("        UNEXPECTED %s" % p[:150])
    return ok


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_craft_thrown.py <arz>")
        return 2
    arz = Path(argv[1])
    results = []

    print("\n=== negative tests: craft chain + thrown class ===")

    # N0 control - the build as it stands must be GREEN.
    db = _fresh(arz)
    results.append(_run('N0', '', db, expect_fail=False))

    # N1 - both supra pools gone from Normal
    db = _fresh(arz)
    lk = SLB.Lookup(db)
    for t in SCT.NORMAL_FORMULA_TABLES:
        _drop_member(db, lk, t, 'arcaneformulae\\supra')
    results.append(_run('N1', 'F1', db))

    # N2 - only supra_special gone from Normal (Mortok's Skull)
    db = _fresh(arz)
    lk = SLB.Lookup(db)
    for t in SCT.NORMAL_FORMULA_TABLES:
        _drop_member(db, lk, t, 'supra_special')
    results.append(_run('N2', 'F1', db))

    # N3 - a thrown formula back on a Ragnarok ghost
    db = _fresh(arz)
    lk = SLB.Lookup(db)
    formula = lk.real(sorted(SCT.THROWN_FORMULA_REAGENTS)[0])
    db.set_field(formula, 'reagent1BaseName', SCT.GHOST_REAGENTS[0])
    results.append(_run('N3', 'G0', db))

    # N4 - artifact reagents unhooked from their legendary host
    db = _fresh(arz)
    lk = SLB.Lookup(db)
    _drop_member(db, lk, SCT.REAGENT_HOST['artifact'], 'svc_craft_reagents_artifact')
    results.append(_run('N4', 'G1', db))

    # N5 - committed MI roster drift
    db = _fresh(arz)
    saved = SCT.MI_REAGENTS
    try:
        SCT.MI_REAGENTS = tuple(x for x in saved if x != 'mi_l_wraith')
        results.append(_run('N5', 'G2', db))
    finally:
        SCT.MI_REAGENTS = saved

    # N6 - legendary thrown table emptied
    db = _fresh(arz)
    lk = SLB.Lookup(db)
    _clear_members(db, lk, SCT.THROWN_TABLE['l'])
    results.append(_run('N6', 'C1', db))

    # N7 - legendary thrown table wired onto the NORMAL master (tier-law breach)
    db = _fresh(arz)
    lk = SLB.Lookup(db)
    nmaster = lk.real(SLB.MASTER['n'])
    for i, nm, _w in SCT._members(db, nmaster):
        if 'svc_unique_thrown_n01' in SLB._n(nm):
            SLB._set_str(db, nmaster, 'lootName%d' % i, lk.real(SCT.THROWN_TABLE['l']))
    results.append(_run('N7', 'C2', db))

    # N8 - the SAME edit must also red the neighbouring B3 rule in svc_loot_breadth
    probs, _s = SLB.audit_db(db)
    b3 = [p for p in probs if p.startswith('B3')]
    print("  N8   B3  %-58s %s" % ('EXPECT RED (same edit, sibling gate)',
                                   'PASS' if b3 else 'FAIL'))
    if b3:
        print("        %s" % b3[0][:150])
    results.append(bool(b3))

    bad = results.count(False)
    print("\n%d/%d negative tests behaved as specified." % (len(results) - bad,
                                                            len(results)))
    if bad:
        print("NEGTEST FAIL: the gate does not catch what it claims to catch.")
        return 1
    print("NEGTEST PASS.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
