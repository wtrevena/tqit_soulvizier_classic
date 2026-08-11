r"""negtest_chest_breadth.py - PLANTED NEGATIVES for the chest-loot BREADTH gate
(Will 2026-08-10: "there are never any legendary spears dropped ... the same items
dropped over and over by all chests").

Proves the breadth contract in tools/svc_loot_breadth.py actually FIRES. Each case
breaks ONE invariant on a fresh in-memory copy of a real BUILT arz (post-fix) and
asserts the audit reds; the positive controls assert the unmodified build is green.

The planted defects are the REAL defect classes, not synthetic ones:
  1. the shipped bug itself - the weapon row back to unique_1h only (no spear path);
  2. the guaranteed slot back to unique_1h (breadth lost on the one slot that always
     fires);
  3. a pool collapse that still leaves one spear (B1 alone would miss it, B2 reds);
  4. the tier law broken the way breadth makes tempting - the LEGENDARY master wired
     onto a Normal chest table (B3);
  5. two Gaoler-cage variant tables made field-identical again (differentiation).

Usage: py tools/debug/negtest_chest_breadth.py <built.arz>   (a POST-FIX build)
Exit 0 = every negative fired and both positive controls passed.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_TOOLS / 'patches'))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB

L = r'records\item\loottables\svc'
CAGE_L = rf'{L}\polisvault_01.dbr'          # chest_01 Legendary (variant a, martial)
CAGE_LB = rf'{L}\polisvault_01_lb.dbr'      # chest_01 Legendary (variant b, hunter)
CAGE_N = rf'{L}\polisvault_01_n.dbr'        # chest_01 Normal
# chest_03 variant a (apex theme). Deliberately the case-1 target: the apex theme's
# guaranteed slot is relic + the aggregate master, with NO explicit per-class member,
# so removing the master reproduces the SHIPPED weapon row exactly (bow + staff +
# unique_1h + statics, zero spear path). The martial/hunter themes keep an explicit
# spear member by design, so a revert there still reaches spears - which is the point
# of theming, not a hole in the gate.
APEX_L = rf'{L}\polisvault_03.dbr'
HOARD_L = r'records\drxitem\container\svc_charonhoard_loot_03.dbr'
UNIQUE_1H_L = r'records\xpack\item\loottables\weapons\mastertables\unique_1h_l01.dbr'
SPEAR_L = r'records\xpack\item\loottables\weapons\unique\spear_l01.dbr'


def load(p):
    return ArzDatabase.from_arz(Path(p))


def _strip_master(db, lk, table, groups=(1, 3)):
    """Remove every reference to the breadth master from a table (the revert)."""
    real = lk.real(table)
    for g in groups:
        for i, name, _w in SLB._slot_members(db, real, g):
            if 'svc_unique_weapons' in SLB._n(name):
                db.set_field(real, 'loot%dName%d' % (g, i), UNIQUE_1H_L)
    return real


def audit_one(db, lk, table, tier):
    return SLB.audit_table(db, table, tier, SLB.Expander(db, lk))


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_chest_breadth.py <built.arz>")
        return 2
    arz = argv[1]
    fails = []

    # ── POSITIVE CONTROL 1: the whole build is green.
    db = load(arz)
    lk = SLB.Lookup(db)
    problems, stats = SLB.audit_db(db, lk=lk)
    ok = (not problems) and len(stats) > 0
    print("%s POSITIVE CONTROL: unmodified post-fix build passes (%d tables audited, "
          "%d problems)" % ('OK ' if ok else 'XX ', len(stats), len(problems)))
    if not ok:
        fails.append('positive control (whole build)')
        for p in problems[:8]:
            print("      %s" % p)

    # ── POSITIVE CONTROL 2: the cage tables are differentiated.
    fam = {'cage[l]': [CAGE_L, CAGE_LB]}
    dp = SLB.differentiation_problems(db, fam, lk)
    print("%s POSITIVE CONTROL: cage variants are not field-identical"
          % ('OK ' if not dp else 'XX '))
    if dp:
        fails.append('positive control (differentiation)')

    def check(label, mutate, probe):
        d = load(arz)
        k = SLB.Lookup(d)
        mutate(d, k)
        hit = bool(probe(d, k))
        if not hit:
            fails.append(label)
        print("%s %-66s -> %s" % ('OK ' if hit else 'XX ', label,
                                  'RED (correct)' if hit else 'GREEN (BLIND)'))

    # 1. THE SHIPPED BUG, reproduced verbatim: the apex cage Legendary table back to
    #    the 3-class weapon row (bow + staff + unique_1h + statics, no spear path).
    check("B1 apex cage Legendary table reverted to the shipped 3-class weapon row",
          lambda d, k: _strip_master(d, k, APEX_L),
          lambda d, k: [p for p in audit_one(d, k, APEX_L, 'l') if p.startswith('B1')])

    # 2. The guaranteed slot alone reverted (loot1 keeps the master).
    check("B1/B2 guaranteed loot3 slot reverted to unique_1h on a boss hoard",
          lambda d, k: _strip_master(d, k, HOARD_L, groups=(1, 3)),
          lambda d, k: audit_one(d, k, HOARD_L, 'l'))

    # 3. A pool collapse that still leaves ONE spear class member: B1 is satisfied,
    #    only the B2 floor can catch it. Proves the floor is not decorative.
    def _collapse_but_one_spear(d, k):
        real = _strip_master(d, k, CAGE_L)
        for g in (1, 2, 4, 5, 6):
            for i, _name, _w in SLB._slot_members(d, real, g):
                d.set_field(real, 'loot%dName%d' % (g, i), '')
        d.set_field(real, 'loot1Name1', SPEAR_L)
        d.set_field(real, 'loot3Name1', UNIQUE_1H_L)
    check("B2 pool collapsed to spear + unique_1h only (B1 alone would be blind)",
          _collapse_but_one_spear,
          lambda d, k: [p for p in audit_one(d, k, CAGE_L, 'l') if p.startswith('B2')])

    # 4. TIER LAW: the LEGENDARY master wired onto the Normal chest table.
    check("B3 legendary weapon master wired onto the NORMAL cage table (tier leak)",
          lambda d, k: d.set_field(k.real(CAGE_N), 'loot1Name6', SLB.MASTER['l']),
          lambda d, k: [p for p in audit_one(d, k, CAGE_N, 'n') if p.startswith('B3')])

    # 5. DIFFERENTIATION: a variant re-cloned over its sibling (the re-flatten).
    def _reflatten(d, k):
        src = k.real(CAGE_L)
        d._raw_records[k.real(CAGE_LB)] = d._raw_records[src]
        d._decoded_cache.pop(k.real(CAGE_LB), None)
    check("B3-diff cage variant re-cloned over its sibling (chests mirror again)",
          _reflatten,
          lambda d, k: SLB.differentiation_problems(d, {'cage[l]': [CAGE_L, CAGE_LB]}, k))

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted collapse reds the breadth gate and the "
          "unmodified build is green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
