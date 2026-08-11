r"""negtest_orb_breadth.py - PLANTED NEGATIVES for the uber-ORB breadth gate
(Will 2026-08-10, R-220: "for the mystical orbs that the uber monsters drop, the
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
ORB01_POOL_E = r'records\item\containers\new\genericboss01_epic_repeat.dbr'
SPEAR_N = r'records\xpack\item\loottables\weapons\unique\spear_n01.dbr'

# An UBER that carries the ladder, used to kill the derivation in N5.
LADDER_PROXIES = tuple(r'records\item\containers\new\genericbossorb_%02d.dbr' % i
                       for i in range(1, 6))
# The base-game Telkine orb: same collapsed weapon row, ZERO uber carriers, so it
# is out of scope today (P2) and must come INTO scope the moment an uber names it (N6).
AKTAIOS = r'records\item\containers\boss\proxy\bosschestproxy11_aktaios.dbr'
NEW_UBER = r'records\creature\monster\skeleton\um_negtest_orbless_99.dbr'
UBER_DONOR = r'records\creature\monster\skeleton\um_gorrahk_99.dbr'
# A base act-4 GOLDEN chest (tagChest006). Its own tables have 5 base referrers,
# which is why the Dark Obelisk's chain is pinned OUT_OF_REACH; N7 uses it as the
# outside container that must never be allowed to drag an orb table into a sweep.
GOLDEN_CHEST = r'records\xpack\item\containers\01c_goldenchest.dbr'

_BASE_ROWS = None


def audit(db):
    """Fresh Lookup + Expander every call (records move between cases).

    Runs over mod UNION base, like the build gate does, so the base-only chains
    (the Dark Obelisk) are visible to N8 instead of being invisible to the test
    battery - which is the R-200 HOLE 2 mistake in miniature.
    """
    return SOB.audit_db(db, lk=None, base_rows=_BASE_ROWS)[0]


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
    global _BASE_ROWS
    db = ArzDatabase.from_arz(Path(argv[1]))
    print("\n=== R-220 orb-breadth negatives ===")
    OLB.apply(db, {})
    _BASE_ROWS = RUO.load_base_rows(required=False, who='negtest')   # cached by apply()
    if not _BASE_ROWS:
        print("  WARNING running MOD-ONLY: the base arz is unreadable, so N8 (the "
              "base-only chain) cannot be exercised. Not a pass.")

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

    # ── N6 a NEW uber drags a previously-unseen chain into scope ────────────
    # The R-200 regression shape: nobody widened the new uber's orb. The base-boss
    # Aktaios chain is invisible to this gate until an uber names it (P2 proves
    # that), so the gate going RED and naming `telkine_default_19-21` - a table it
    # never mentioned before - proves the derivation is LIVE, not a snapshot.
    # HONEST NOTE ON WHICH CODE FIRES: it reds on O6, not B1, because every
    # non-uber chain in this db shares its loot tables with sibling base chests
    # (the three Telkines share one table set), so the gate's correct answer is
    # "a human must decide whether to widen shared base loot", not "widen it".
    # There is no chain in this db that is BOTH outside the current scope AND
    # exclusive, so the collapse-is-caught half is proven by N1 against a real
    # in-scope table rather than by fabricating a synthetic chain.
    def _new_uber_on_unseen_orb(d):
        lk = SLB.Lookup(d)
        d.clone_record(lk.real(UBER_DONOR), NEW_UBER)
        d.set_field(NEW_UBER, SOB._TREASURE, lk.real(AKTAIOS))
        d._modified.add(NEW_UBER)
        return lambda: RUO._drop_record(d, NEW_UBER)
    run("N6 a NEW uber drags an unseen base-boss orb chain into scope",
        _new_uber_on_unseen_orb, expect=('O6',))

    # ── N7 an in-scope orb table that the BASE GAME starts sharing ─────────
    # The guard that stops this lane from ever rewriting loot nobody asked about.
    # A base golden chest is pointed at an orb table; the table must then be
    # EXCLUDED from the sweep and reported (O6), never widened. `forbid=('B1','B2')`
    # proves it was excluded rather than merely failing some other way.
    def _share_an_orb_table(d):
        lk = SLB.Lookup(d)
        real = lk.real(GOLDEN_CHEST)
        saved = RUO._snapshot_field(d, real, 'tables')
        d.set_field(real, 'tables', lk.real(ORB04_L))
        return lambda: RUO._restore_field(d, real, 'tables', saved)
    run("N7 a base golden chest starts sharing an orb table (shared-loot guard)",
        _share_an_orb_table, expect=('O6',), forbid=('B1', 'B2'))

    # ── N8 a base-only uber chain that is NOT pinned ────────────────────────
    def _unpin(d):
        saved = dict(SOB.OUT_OF_REACH)
        SOB.OUT_OF_REACH.clear()
        return lambda: SOB.OUT_OF_REACH.update(saved)
    run("N8 the base-only Dark Obelisk chain with its OUT_OF_REACH pin removed",
        _unpin, expect=('O5',))

    # ── N9 ONE TABLE, TWO DIFFICULTIES: the narrowing a COUNT cannot show ───
    # `scope_tables` de-duplicates first-wins, so a table reachable through two
    # difficulty slots would be widened with ONE tier's master and audited against
    # ONE tier's floor - silently. O4b is the only check that can see it. Planted by
    # pointing orb01's EPIC accessory pool at orb01's NORMAL chest.
    def _two_difficulties_one_table(d):
        lk = SLB.Lookup(d)
        pool_e = lk.real(ORB01_POOL_E)
        chest_n = SLB._sc(d.get_field_value(lk.real(ORB01_POOL_N), 'fixedItemName1'))
        saved = RUO._snapshot_field(d, pool_e, 'fixedItemName1')
        d.set_field(pool_e, 'fixedItemName1', chest_n)
        return lambda: RUO._restore_field(d, pool_e, 'fixedItemName1', saved)
    run("N9 one orb table reached at TWO difficulties (first-wins narrowing)",
        _two_difficulties_one_table, expect=('O4b',))

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
