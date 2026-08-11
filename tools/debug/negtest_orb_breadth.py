r"""negtest_orb_breadth.py - PLANTED NEGATIVES for the uber-ORB breadth gate
(Will 2026-08-10, R-210: "for the mystical orbs that the uber monsters drop, the
items should drop with increased breadth as well so all classes of items could be
dropped").

Proves the contract in tools/svc_orb_breadth.py actually FIRES. The arz is loaded
ONCE and `orb_loot_breadth.apply()` is run on it, so the battery works from a
PRE-fix build (no ship build needed) and every case is planted against the real,
fully-applied state; each negative is then planted, verified and UNDONE (the
red_uber_orbs undo-callable idiom - re-decoding 51k records per case would make
this a minutes-long tool for no extra evidence).

The planted defects are the REAL defect classes, not synthetic ones:
  N1  the shipped bug itself - one orb table's weapon row re-collapsed to
      axe/club/sword + bow + staff (the exact state build76 shipped);
  N2  a pool collapse that still leaves ONE spear (O1 alone would be blind; only
      the O2 floor can catch it) - planted on the normal branch, the branch whose
      floor is deliberately set high enough to bite;
  N3  the tier law broken the way breadth makes tempting - the LEGENDARY master
      wired onto a NORMAL orb table (O3);
  N4  a chain link broken - an accessory pool that no longer names its chest, so
      the orb resolves to nothing on one difficulty (O4);
  N5  the derivation itself killed - every uber carrier of the ladder stripped of
      its treasureProxyName, so the scope collapses (O4's "audits nothing" trap);
  N6  A NEW UBER planted on a collapsed, currently-out-of-scope chain (the
      base-boss Aktaios orb): the derived scope must GROW to cover it and RED.
      This is the R-200 regression shape - a new uber whose orb nobody widened.
Positive controls:
  P1  the unmodified post-apply build is GREEN;
  P2  the Aktaios chain with NO uber carrier stays GREEN (scope-boundary proof:
      the gate does not invent policy for the base game's act/quest bosses, the
      same boundary R-200 drew and registered as debt).

Usage: py tools/debug/negtest_orb_breadth.py <arz>   (pre- OR post-fix build)
Exit 0 = every negative fired and both positive controls passed.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_TOOLS / 'patches'))
from arz_patcher import ArzDatabase
import svc_loot_breadth as SLB
import svc_orb_breadth as SOB
import red_uber_orbs as RUO
import orb_loot_breadth as OLB

# The orb tables the cases are planted on (each resolved case-insensitively).
ORB01_N = r'records\item\containers\defaultloot\uberorb_default_13-15.dbr'
ORB04_L = r'records\xpack\item\containers\loot tables\uberorb_default_l01c.dbr'
ORB01_POOL_N = r'records\item\containers\new\genericboss01_normal_repeat.dbr'
SPEAR_N = r'records\xpack\item\loottables\weapons\unique\spear_n01.dbr'

# An UBER that carries the ladder, used to kill the derivation in N5.
LADDER_PROXIES = tuple(r'records\item\containers\new\genericbossorb_%02d.dbr' % i
                       for i in range(1, 6))
# The base-game Telkine orb: same collapsed weapon row, ZERO uber carriers, so it
# is out of scope today (P2) and must come INTO scope the moment an uber names it (N6).
AKTAIOS = r'records\item\containers\boss\proxy\bosschestproxy11_aktaios.dbr'
NEW_UBER = r'records\creature\monster\skeleton\um_negtest_orbless_99.dbr'
UBER_DONOR = r'records\creature\monster\skeleton\um_gorrahk_99.dbr'


def audit(db):
    """Fresh Lookup + Expander every call (records move between cases)."""
    return SOB.audit_db(db, lk=None, base_rows=None)[0]


def _strip_master(db, table):
    """Re-collapse a table: drop the breadth master out of its weapon row."""
    lk = SLB.Lookup(db)
    real = lk.real(table)
    undo = []
    for i, name, _w in SLB._slot_members(db, real, 1):
        if 'svc_unique_weapons' in SLB._n(name):
            undo.append(RUO._snapshot_field(db, real, 'loot1Name%d' % i))
            undo.append(RUO._snapshot_field(db, real, 'loot1Weight%d' % i))
            db.set_field(real, 'loot1Name%d' % i, '')
            db.set_field(real, 'loot1Weight%d' % i, 0)

    def _undo():
        for saved in undo:
            if saved:
                RUO._restore_field(db, real, saved[0][0].split('###')[0], saved)
    return _undo


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_orb_breadth.py <arz>")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))
    print("\n=== R-210 orb-breadth negatives ===")
    OLB.apply(db, {})

    results = []

    def run(label, mutate, must_fail=True, expect=(), forbid=()):
        """`expect`/`forbid` name the CHECK CODES that must / must not fire, so each
        case proves its own invariant instead of merely turning something red."""
        undo = mutate(db) if mutate is not None else (lambda: None)
        try:
            problems = audit(db)
            codes = {p.split(None, 1)[0] for p in problems}
            ok = bool(problems) == must_fail
            missing = [c for c in expect if c not in codes]
            leaked = [c for c in forbid if c in codes]
            ok = ok and not missing and not leaked
            got = ('RED %s: %s' % (sorted(codes), problems[0][:88])) if problems else 'GREEN'
            if missing:
                got += '   ** expected %s **' % missing
            if leaked:
                got += '   ** forbidden %s fired **' % leaked
        finally:
            undo()
        results.append((ok, label))
        print("  [%s] %-64s -> %s" % ('OK ' if ok else 'BAD', label, got))

    # ── P1 positive control ─────────────────────────────────────────────────
    run("P1 the unmodified post-apply build", None, must_fail=False)

    # ── N1 the shipped bug, reproduced verbatim ─────────────────────────────
    run("N1 one orb table re-collapsed to the shipped 3-class weapon row",
        lambda d: _strip_master(d, ORB04_L), expect=('B1', 'O2b'))

    # ── N2 the pool collapsed with EVERY weapon class still reachable ───────
    # Only the breadth master is left in the weapon row and every armour /
    # jewellery / shield member is blanked. B1 is therefore satisfied (the master
    # alone pays all six classes) and ONLY the O2 floor can see the collapse -
    # which is exactly the case the floor exists for. `forbid=('B1',)` asserts
    # that isolation instead of assuming it.
    def _collapse_keep_classes(d):
        lk = SLB.Lookup(d)
        real = lk.real(ORB01_N)
        master = SLB._n(lk.real(SLB.MASTER['n']))
        saved = []
        for g in range(1, 7):
            for i, name, _w in SLB._slot_members(d, real, g):
                if g == 1 and SLB._n(name) == master:
                    continue
                saved.append(RUO._snapshot_field(d, real, 'loot%dName%d' % (g, i)))
                d.set_field(real, 'loot%dName%d' % (g, i), '')

        def _undo():
            for s in saved:
                if s:
                    RUO._restore_field(d, real, s[0][0].split('###')[0], s)
        return _undo
    run("N2 orb pool collapsed to the master alone (only the O2 floor can see it)",
        _collapse_keep_classes, expect=('B2',), forbid=('B1',))

    # ── N3 the tier law: the LEGENDARY master on a NORMAL orb table ─────────
    def _tier_leak(d):
        lk = SLB.Lookup(d)
        real = lk.real(ORB01_N)
        saved = RUO._snapshot_field(d, real, 'loot1Name6')
        d.set_field(real, 'loot1Name6', lk.real(SLB.MASTER['l']))
        return lambda: RUO._restore_field(d, real, 'loot1Name6', saved)
    run("N3 the LEGENDARY master wired onto a NORMAL orb table (tier leak)",
        _tier_leak, expect=('B3', 'O2b'))

    # ── N4 a broken chain link ──────────────────────────────────────────────
    def _break_chain(d):
        lk = SLB.Lookup(d)
        real = lk.real(ORB01_POOL_N)
        saved = RUO._snapshot_field(d, real, 'fixedItemName1')
        d.set_field(real, 'fixedItemName1', r'records\item\containers\new\nope_99.dbr')
        return lambda: RUO._restore_field(d, real, 'fixedItemName1', saved)
    run("N4 an accessory pool that no longer names its orb chest", _break_chain,
        expect=('O4',))

    # ── N5 the derivation killed: no uber names the ladder any more ─────────
    def _kill_derivation(d):
        low = {SLB._n(p) for p in LADDER_PROXIES}
        saved = []
        for name in d.record_names():
            tpl = SLB._sc(d.get_field_value(name, 'templateName'))
            if not (isinstance(tpl, str) and SLB._n(tpl).endswith(SOB._MONSTER_TPL)):
                continue
            proxy = SLB._sc(d.get_field_value(name, SOB._TREASURE))
            if isinstance(proxy, str) and SLB._n(proxy) in low:
                saved.append((name, RUO._snapshot_field(d, name, SOB._TREASURE)))
                RUO._del_field(d, name, SOB._TREASURE)

        def _undo():
            for name, s in saved:
                RUO._restore_field(d, name, SOB._TREASURE, s)
        return _undo
    run("N5 every uber carrier of the ladder stripped (scope collapses)",
        _kill_derivation, expect=('O4',))

    # ── N6 a NEW uber planted on a collapsed, out-of-scope orb ──────────────
    def _new_uber_on_collapsed_orb(d):
        lk = SLB.Lookup(d)
        d.clone_record(lk.real(UBER_DONOR), NEW_UBER)
        d.set_field(NEW_UBER, SOB._TREASURE, lk.real(AKTAIOS))
        d._modified.add(NEW_UBER)
        return lambda: RUO._drop_record(d, NEW_UBER)
    run("N6 a NEW uber wired to a collapsed base-boss orb (the R-200 shape)",
        _new_uber_on_collapsed_orb, expect=('B1', 'O2b'))

    # ── P2 scope boundary: that same collapsed orb, with no uber, is GREEN ──
    run("P2 the base-boss Aktaios orb with no uber carrier stays out of scope",
        None, must_fail=False)

    bad = [lbl for ok, lbl in results if not ok]
    print()
    if bad:
        print("NEGTEST FAILED: %d case(s)" % len(bad))
        for b in bad:
            print("   - %s" % b)
        return 1
    print("NEGTEST PASS: %d/%d as designed - every planted collapse reds the orb "
          "breadth gate, a new uber's collapsed orb is caught by derivation, and "
          "the base-boss boundary stays green." % (len(results), len(results)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
