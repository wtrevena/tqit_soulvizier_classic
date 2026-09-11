r"""R-260 - THE `Misc4` AUDIT: 32 DROPS RE-HOMED ONTO SLOTS THE ENGINE DECLARES, AND THE
UNDECLARED SLOT VARIABLES HELD AT ZERO.

THE DEFECT (BL-R258-DEBT-2, vet-proven from the engine bytes on the build102 lane):
`Toolset\Templates.arc -> templates\templatebase\characterloot.tpl` declares exactly
ELEVEN equip/loot slot groups - Head Torso Forearm LowerBody LeftHand RightHand Finger1
Finger2 Misc1 Misc2 Misc3 - each with `chanceToEquip<S>` (the % the SLOT rolls),
`chanceToEquip<S>Item1..6` (RELATIVE weights among the slot's rows, one row picked per
roll) and `loot<S>Item1..6`. `Misc4` / `Misc5` / `Misc6` / `Neck` occur in 0 of 566
templates and 0 of 74,013 base records (0 in SV 0.98i / 0.9 / 0.4.1 too). Yet
`apply_svc_patches._svc_guarantee_unique` chose its slot with `for n in (4, 5, 6, 3)`
(build36 `79de1d7`, 2026-07-11), so it ALWAYS landed on the phantom `Misc4`, and four
other writers copied the idiom. The shipped build102 arz `7dad9a8a` carries `Misc4`
fields on 32 records - 7 "guaranteed @100" and 25 animal-relic sources at 7-10% - none
of which could ever drop, plus `chanceToEquipNeck` (a dead 0.0) on the 3 EoAT disciple
pets. Every number below is read out of that file, not remembered.

WHAT THIS MODULE DOES (last in the registry before the no-op `visuals`, so it sees the
FINAL assembled db):
  apply()  - a mod-wide sweep that STRIPS every phantom slot variable off every record.
             By this slot the 31 re-homed carriers were already stripped by the helper
             and the Devourer by `toxeus_endofallthings`; what is left is the disciples'
             dead `chanceToEquipNeck` (inherited through the pet chain) and anything a
             future writer adds by the old idiom - printed by name, never silent.
  verify() - the two R-260 gate arms over the final db, shared with the standalone twins:
             (a) NO PHANTOM: zero records carry any chanceToEquipMisc4..9* / lootMisc4..9*
                 / chanceToEquipNeck* / lootNeck* field (tools/gate_no_phantom_loot_slots.py);
             (b) MEASURED DROPS: every roster record delivers its item at the intended %
                 - slot chance x row weight / sum of weights, re-derived from the bytes -
                 on the pinned REAL slot/row, with the tier's side conditions, and the
                 withheld Devourer channel stays withheld (tools/gate_guaranteed_drops_measured.py);
             plus the BL-R258-DEBT-1 freeze restated (Devourer Finger2 + Misc1 exactly
             R-258's) and a ledger cross-check: every roster record that is not withheld
             was actually wired THIS build by the helper (a caller that silently stops
             calling it reds here).

THE ROSTER, THE POLICY AND THE ARITHMETIC live in `tools/svc_loot_slots.py` (one
implementation for the helper, this module and both gates). The disposition per
record, the debts and the Devourer decision are in docs/WILL_RULINGS.md R-260.

Self test:      py tools/patches/phantom_loot_slots.py --selftest
Negative test:  py tools/patches/phantom_loot_slots.py --negtest
Standalone:     py tools/gate_no_phantom_loot_slots.py <arz> [--negtest]
                py tools/gate_guaranteed_drops_measured.py <arz> [--control <build102 arz>] [--negtest]
"""
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

import svc_loot_slots as _sls   # noqa: E402

MODULE_NAME = ("R-260 phantom loot slots - the 32 Misc4 carriers re-homed onto declared "
               "slots at measured rates; undeclared slot variables held at zero")


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    found = _sls.scan_phantom(db)
    stripped = 0
    for rec, fields in sorted(found.items()):
        got = _sls.strip_phantom(db, rec)
        stripped += len(got)
        print("  [R-260] stripped dead %s off %s" % (', '.join(got), _sls.short(rec)))
    print("  [R-260] mod-wide phantom sweep: %d record(s) carried undeclared slot fields at "
          "this registry slot, %d field(s) stripped; %d disposition(s) in the helper ledger"
          % (len(found), stripped, len(_sls.LEDGER)))
    return tags


def _check(db, require_ledger=False):
    """The R-260 contract over `db`. Returns a list of problem strings."""
    P = []
    P += ['A ' + p for p in _sls.check_no_phantom(db)]
    P += ['B ' + p for p in _sls.check_roster(db)]
    P += ['F ' + p for p in _sls.check_devourer_freeze(db)]
    if require_ledger:
        wired = {_sls.norm(d['record']) for d in _sls.LEDGER}
        for e in _sls.ROSTER:
            if _sls.norm(e['record']) not in wired:
                P.append("L %s on %s was NOT wired by _svc_guarantee_unique this build - "
                         "a caller stopped calling the helper (the bytes may still be "
                         "right by inheritance, the process is not)"
                         % (e['label'], _sls.short(e['record'])))
    return P


def verify(db, tags=None):
    P = _check(db, require_ledger=True)
    if P:
        for p in P:
            print("  R-260 OFFENDER: %s" % p)
        raise SystemExit("[phantom_loot_slots] R-260 gate FAILED: %d problem(s)" % len(P))
    n_b = sum(1 for e in _sls.ROSTER if e['tier'] == 'B')
    n_c = sum(1 for e in _sls.ROSTER if e['tier'] == 'C')
    n_d = sum(1 for e in _sls.ROSTER if e['tier'] == 'D')
    print("  R-260 gate OK: 0 records carry an undeclared slot variable; %d roster records "
          "deliver their item at the intended MEASURED rate on a declared slot (%d dormant-"
          "slot, %d live-100 takeover, %d rate-preserving share); the Devourer's rant+rite "
          "channel is withheld with no phantom field (BL-R260-DEBT-1) and his Finger2 + "
          "Misc1 are R-258's. WHAT IS CLAIMED: the database now routes every one of these "
          "drops through a template-declared slot at the published rate. WHAT IS NOT "
          "CLAIMED: that anyone has SEEN one fall - that is BL-R260-DEBT-3, Will's kills."
          % (len(_sls.ROSTER), n_b, n_c, n_d))
    return True


# ── self test (constants only) ───────────────────────────────────────────────
def _selftest():
    bad = 0

    def ck(cond, msg):
        nonlocal bad
        print("  selftest %s: %s" % ('OK  ' if cond else 'FAIL', msg))
        if not cond:
            bad += 1

    recs = [e['record'] for e in _sls.ROSTER]
    ck(len(recs) == 31, "31 re-homed roster records (32 carriers minus the withheld Devourer)")
    ck(len(set(_sls.norm(r) for r in recs)) == 31, "roster records are distinct")
    ck(len(_sls.WITHHELD) == 1 and _sls.norm(_sls.WITHHELD[0]['record']) == _sls.norm(_sls.DEVOURER),
       "exactly one withheld record, the Devourer")
    ck(all(e['slot'] in _sls.MISC_ORDER for e in _sls.ROSTER), "every roster slot is Misc1/2/3")
    ck(all(e['row'] in _sls.ROWS for e in _sls.ROSTER), "every roster row is 1..6")
    ck(all(e['tier'] in ('A', 'B', 'C', 'D') for e in _sls.ROSTER), "every roster tier is A/B/C/D")
    ck(all(e['pct'] == 100.0 for e in _sls.ROSTER if e['tier'] == 'C'),
       "takeovers (tier C) are 100% only")
    ck(all(e['pct'] < 100.0 and 'base_rows' in e for e in _sls.ROSTER if e['tier'] == 'D'),
       "shares (tier D) are below 100% and pin their base rows")
    ck(sum(1 for e in _sls.ROSTER if e['pct'] == 100.0) == 6,
       "six guaranteed records (Enslaver, Hunt, Hunt_L, Bough, Lethe, Mask)")
    ck(sum(1 for e in _sls.ROSTER if e['pct'] in (7.0, 10.0)) == 25, "25 relic sources at 7-10%")
    ck(all(len(e['tables']) == 3 for e in _sls.ROSTER), "every roster item is a 3-tier array")
    ck(all(_sls.norm(p) == p for e in _sls.ROSTER for p in e['tables'] + [e['record']]),
       "every authored path is lowercase (exact-match resolvable)")
    ck(_sls.PHANTOM_RE.match('chanceToEquipMisc4') is not None
       and _sls.PHANTOM_RE.match('lootMisc6Item1') is not None
       and _sls.PHANTOM_RE.match('chanceToEquipNeck') is not None
       and _sls.PHANTOM_RE.match('lootNeckItem2') is not None
       and _sls.PHANTOM_RE.match('chanceToEquipMisc3') is None
       and _sls.PHANTOM_RE.match('lootMisc1Item6') is None,
       "the phantom pattern matches Misc4+/Neck and nothing declared")
    ck(len(_sls.SLOTS) == 11, "eleven declared slot groups")
    print("selftest: %s" % ("PASS" if not bad else "FAIL (%d)" % bad))
    return 1 if bad else 0


# ── planted negatives (stub db) ──────────────────────────────────────────────
class _Stub(object):
    """A plain-dict db with the four calls the model uses."""

    def __init__(self):
        self.d = {}
        self._modified = set()

    def has_record(self, n):
        return n in self.d

    def record_names(self):
        return list(self.d)

    def get_fields(self, n):
        return self.d.get(n)

    def get_field_value(self, n, f):
        rec = self.d.get(n)
        return None if rec is None else rec.get(f)

    def set_field(self, n, f, v, dt=None):
        self.d.setdefault(n, {})[f] = v


def _healthy():
    """A stub carrying every roster record in its shipped R-260 shape."""
    db = _Stub()
    tabs = set()
    for e in _sls.ROSTER:
        tabs.update(e['tables'])
    for w in _sls.WITHHELD:
        tabs.update(w['tables'])
    tabs.update(_sls.DEVOURER_SOUL_TABLES)
    for t in tabs:
        db.d[t] = {'Class': 'LootItemTable_FixedWeight'}
    db.d[_sls.DEVOURER_MASTER] = {'Class': 'LootMasterTable', 'lootName1': _sls.RANT_TABLE,
                                  'lootName2': _sls.RITE_TABLE}
    for e in _sls.ROSTER:
        r = {'dropItems': 1}
        s = e['slot']
        if e['tier'] in ('A', 'B', 'C'):
            r['chanceToEquip%s' % s] = e['pct']
            if e['tier'] != 'A':
                r['chanceToEquip%sItem1' % s] = 0
                r['loot%sItem1' % s] = ['t\\inherited.dbr'] * 3
            r['chanceToEquip%sItem%d' % (s, e['row'])] = 100
            r['loot%sItem%d' % (s, e['row'])] = list(e['tables'])
        else:
            base = e['base_rows']
            total = float(sum(base.values()))
            r['chanceToEquip%s' % s] = e['base_chance'] + e['pct']
            for i, w in base.items():
                r['chanceToEquip%sItem%d' % (s, i)] = w
                r['loot%sItem%d' % (s, i)] = ['t\\base%d.dbr' % i] * 3
            r['chanceToEquip%sItem%d' % (s, e['row'])] = int(round(total * e['pct'] / e['base_chance']))
            r['loot%sItem%d' % (s, e['row'])] = list(e['tables'])
        db.d[e['record']] = r
    db.d[_sls.DEVOURER] = {'dropItems': 1, 'chanceToEquipFinger2': 100.0,
                           'chanceToEquipMisc1': 100.0, 'chanceToEquipMisc1Item1': 0,
                           'chanceToEquipMisc1Item2': 0, 'chanceToEquipMisc1Item3': 100,
                           'lootMisc1Item3': list(_sls.DEVOURER_SOUL_TABLES)}
    db.d['t\\inherited.dbr'] = {}
    for i in (1, 5):
        db.d['t\\base%d.dbr' % i] = {}
    return db


def _entry(stem):
    """The roster entry whose record basename is `stem` (index-free lookup)."""
    for e in _sls.ROSTER:
        if _sls.short(e['record']) == stem:
            return e
    raise KeyError(stem)


def _negtest():
    ENS = _entry('um_toxeus_enslaver_99.dbr')['record']        # tier C
    ENS_TABS = _entry('um_toxeus_enslaver_99.dbr')['tables']
    B01 = _entry('ar_archer_01.dbr')['record']                 # tier B
    B01_TAB1 = _entry('ar_archer_01.dbr')['tables'][1]
    B05 = _entry('ar_archer_05.dbr')['record']                 # tier D
    BOUGH = _entry('um_charonform2_ferryman_99.dbr')['record']  # tier B
    plants = (
        ("a phantom Misc4 field grows back on a roster record",
         lambda d: d.d[ENS].__setitem__('chanceToEquipMisc4', 100.0), 'A'),
        ("a phantom Neck field on an unrelated record",
         lambda d: d.d.__setitem__('records\\x\\pet.dbr', {'chanceToEquipNeck': 0.0}), 'A'),
        ("a phantom lootMisc5 array on an unrelated record",
         lambda d: d.d.__setitem__('records\\x\\mon.dbr', {'lootMisc5Item1': ['a', 'b', 'c']}), 'A'),
        ("the Enslaver's rite row deleted",
         lambda d: d.d[ENS].pop('lootMisc1Item3'), 'B'),
        ("the Enslaver's rite row weight zeroed (slot goes silent)",
         lambda d: d.d[ENS].__setitem__('chanceToEquipMisc1Item3', 0), 'B'),
        ("a muted potion row un-muted beside the rite (a 50/50 again)",
         lambda d: d.d[ENS].__setitem__('chanceToEquipMisc1Item1', 100), 'B'),
        ("the Enslaver's slot chance dropped to 50",
         lambda d: d.d[ENS].__setitem__('chanceToEquipMisc1', 50.0), 'B'),
        ("the rite moved to a different real slot than the roster pins",
         lambda d: (d.d[ENS].pop('lootMisc1Item3'),
                    d.d[ENS].__setitem__('chanceToEquipMisc2', 100.0),
                    d.d[ENS].__setitem__('chanceToEquipMisc2Item1', 100),
                    d.d[ENS].__setitem__('lootMisc2Item1', list(ENS_TABS))), 'B'),
        ("dropItems switched off on a carrier",
         lambda d: d.d[BOUGH].__setitem__('dropItems', 0), 'B'),
        ("the Bough's dormant inherited row un-muted",
         lambda d: d.d[BOUGH].__setitem__('chanceToEquipMisc3Item1', 25), 'B'),
        ("a relic source's chance drifts (7 -> 3.5)",
         lambda d: d.d[B01].__setitem__('chanceToEquipMisc3', 3.5), 'B'),
        ("a shared slot's pre-existing amulet row weight changed (skew)",
         lambda d: d.d[B05].__setitem__('chanceToEquipMisc3Item1', 2500), 'B'),
        ("a shared slot's chance moved (skews every row)",
         lambda d: d.d[B05].__setitem__('chanceToEquipMisc3', 9.0), 'B'),
        ("a shared slot grows an unpinned live row",
         lambda d: d.d[B05].__setitem__('chanceToEquipMisc3Item6', 40), 'B'),
        ("a roster record missing",
         lambda d: d.d.pop(B01), 'B'),
        ("a roster loot table missing",
         lambda d: d.d.pop(B01_TAB1), 'B'),
        ("the Devourer silently re-wired onto the withheld master",
         lambda d: (d.d[_sls.DEVOURER].__setitem__('chanceToEquipMisc3', 100.0),
                    d.d[_sls.DEVOURER].__setitem__('chanceToEquipMisc3Item1', 100),
                    d.d[_sls.DEVOURER].__setitem__('lootMisc3Item1', [_sls.DEVOURER_MASTER] * 3)), 'B'),
        ("the withheld master DELETED",
         lambda d: d.d.pop(_sls.DEVOURER_MASTER), 'B'),
        ("the Devourer grows his phantom Misc4 back",
         lambda d: d.d[_sls.DEVOURER].__setitem__('lootMisc4Item1', [_sls.DEVOURER_MASTER] * 3), 'A'),
        ("R-243's Finger2 pin knocked off 100 on the Devourer",
         lambda d: d.d[_sls.DEVOURER].__setitem__('chanceToEquipFinger2', 25.0), 'F'),
        ("the R-258 soul chute diluted (a potion row un-muted)",
         lambda d: d.d[_sls.DEVOURER].__setitem__('chanceToEquipMisc1Item1', 80), 'F'),
    )
    bad = 0
    for label, plant, arm in plants:
        db = _healthy()
        plant(db)
        found = _check(db)
        if not found:
            print("  negtest FAIL (MISSED): %s" % label)
            bad += 1
        elif not any(p.startswith(arm + ' ') for p in found):
            print("  negtest FAIL (wrong arm, %s never fired): %s -> %s" % (arm, label, found[0][:90]))
            bad += 1
        else:
            print("  negtest OK  (caught by %s): %-58s -> %s" % (arm, label, found[0][:80]))
    controls = (
        ("an untouched healthy stub", lambda d: None),
        ("a roster table referenced in MIXED CASE",
         lambda d: d.d[ENS].__setitem__('lootMisc1Item3', [t.upper() for t in ENS_TABS])),
        ("a muted inherited row still named at weight 0",
         lambda d: d.d[BOUGH].__setitem__('chanceToEquipMisc3Item2', 0)),
    )
    for label, plant in controls:
        db = _healthy()
        plant(db)
        found = _check(db)
        if found:
            print("  negtest FAIL (false positive): %s -> %s" % (label, found[0]))
            bad += 1
        else:
            print("  negtest OK  (no false positive): %s" % label)
    # the writer itself: the helper must refuse to skew a live slot silently
    db = _healthy()
    db.d['records\\x\\live.dbr'] = {'dropItems': 1, 'chanceToEquipMisc1': 5.0,
                                    'chanceToEquipMisc1Item1': 100, 'lootMisc1Item1': ['t\\inherited.dbr'] * 3,
                                    'chanceToEquipMisc2': 5.0, 'chanceToEquipMisc2Item1': 100,
                                    'lootMisc2Item1': ['t\\inherited.dbr'] * 3,
                                    'chanceToEquipMisc3': 5.0, 'chanceToEquipMisc3Item1': 100,
                                    'lootMisc3Item1': ['t\\inherited.dbr'] * 3}
    tabs = list(_entry('ar_archer_01.dbr')['tables'])
    try:
        _sls.wire_misc_drop(db, 'records\\x\\live.dbr', tabs, 100.0)
        print("  negtest FAIL (MISSED): the helper took a live slot at 100%% without a pin")
        bad += 1
    except SystemExit:
        print("  negtest OK  (fail-loud): the helper refuses a 100%% guarantee on all-live slots without a pin")
    try:
        _sls.wire_misc_drop(db, 'records\\x\\live.dbr', tabs, 7.0)
        print("  negtest FAIL (MISSED): the helper shared a live slot without share=True")
        bad += 1
    except SystemExit:
        print("  negtest OK  (fail-loud): the helper refuses to share a live slot without opt-in")
    d = _sls.wire_misc_drop(db, 'records\\x\\live.dbr', tabs, 7.0, share=True)
    ok = (d['tier'] == 'D' and _sls.close(d['measured'], 7.0)
          and _sls.close(_sls.row_share(db, 'records\\x\\live.dbr', d['slot'], 1), 5.0, 1e-6))
    print("  negtest %s: rate-preserving share keeps the live row at 5.0000%% and the item at 7.0000%%"
          % ('OK ' if ok else 'FAIL'))
    bad += 0 if ok else 1
    d2 = _sls.wire_misc_drop(db, 'records\\x\\live.dbr', tabs, 7.0, share=True)
    print("  negtest %s: a second call is idempotent (tier %s)" % ('OK ' if d2['tier'] == 'kept' else 'FAIL', d2['tier']))
    bad += 0 if d2['tier'] == 'kept' else 1
    db.d['records\\x\\live.dbr']['chanceToEquipMisc4'] = 100.0
    d3 = _sls.wire_misc_drop(db, 'records\\x\\live.dbr', tabs, 7.0, share=True)
    print("  negtest %s: a phantom field is stripped on re-apply (%s)"
          % ('OK ' if d3['stripped'] == ['chanceToEquipMisc4'] else 'FAIL', d3['stripped']))
    bad += 0 if d3['stripped'] == ['chanceToEquipMisc4'] else 1
    total = len(plants) + len(controls) + 5
    print("negtest: %d/%d checks clean" % (total - bad, total))
    return 1 if bad else 0


if __name__ == '__main__':
    if '--negtest' in _sys.argv:
        _sys.exit(_negtest())
    if '--selftest' in _sys.argv:
        _sys.exit(_selftest())
    print(__doc__)
