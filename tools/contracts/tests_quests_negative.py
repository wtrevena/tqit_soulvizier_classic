#!/usr/bin/env python3
"""Negative tests for contracts_quests.py (DOMAIN E: QUEST CONTRACTS).

For every one of the 8 quest contracts: build a COMPLIANT synthetic Ctx (assert the
contract stays silent), then surgically break the exact thing the contract guards and
assert it FIRES on that subject. This guards the contracts themselves against silent
regression (a contract that never fires is worthless), the same discipline the other
four lanes' negative tests apply.

Self-contained: it builds tiny in-memory Ctx / parsed-quest structures and a small
FakeArz, so it needs NO big artifacts (unlike the souls/summons/resources negative
tests, which mutate a real arz). Run:
  python tools/contracts/tests_quests_negative.py
Exits 0 if every contract's negative test PASSES, 1 otherwise.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import contracts_quests as C   # noqa: E402


# ---------------------------------------------------------------------------
# tiny fakes: a parsed .qst is {basename: [(kind, cls, fields), ...]} where
# fields = {key: (type, value)}; a record DB answers get_field_value/get_fields.
# ---------------------------------------------------------------------------
def S(v):
    """A string-typed .qst field value (what str_fields() extracts)."""
    return ('str', v)


def cond(cls, **fields):
    return ('cond', cls, {k: S(v) for k, v in fields.items()})


def act(cls, **fields):
    return ('act', cls, {k: S(v) for k, v in fields.items()})


class _TF:
    __slots__ = ('values',)

    def __init__(self, values):
        self.values = list(values)


class FakeArz:
    """Answers the two accessors the class/loot checks use: get_field_value +
    get_fields. `records` maps a stored record name -> {field: [values]}."""

    def __init__(self, records):
        self._r = records

    def get_field_value(self, stored, field):
        rec = self._r.get(stored)
        if not rec:
            return None
        v = rec.get(field)
        if not v:
            return None
        return v[0] if len(v) == 1 else list(v)

    def get_fields(self, stored):
        rec = self._r.get(stored) or {}
        return {k: _TF(vals) for k, vals in rec.items()}

    def record_names(self):
        return list(self._r.keys())


def new_ctx(**over):
    """A Ctx with permissive defaults; override only what a test needs."""
    ctx = C.Ctx()
    ctx.quests = {}
    ctx.raw = {}
    ctx.moddb = None
    ctx.mod_names = {}
    ctx.basedb = None
    ctx.base_names = {}
    ctx.union = set()
    ctx.tags = set()
    ctx.registrations = None
    ctx.reg_index = None
    ctx.placed = None
    ctx.have_map = False
    ctx.have_base_arz = False
    ctx.have_tag_union = False
    for k, v in over.items():
        setattr(ctx, k, v)
    return ctx


RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), detail))
    tag = 'PASS' if ok else 'FAIL'
    line = '  [%s] %s' % (tag, name)
    if detail and not ok:
        line += ' :: ' + detail
    print(line)


def fires(viols, cid, needle=None):
    for v in viols:
        if v['contract'] != cid:
            continue
        if needle is None or needle.lower() in v['subject'].lower():
            return True
    return False


# ===========================================================================
# QST-REC-EXISTS
# ===========================================================================
def test_rec_exists():
    print('CONTRACT: QST-REC-EXISTS')
    good_ref = 'records/drx/quest/real.dbr'
    q = {'widowletter.qst': [cond('Condition_HasItem', itemRecord=good_ref)]}
    ok = new_ctx(quests=q, union={good_ref})
    inf = []
    check('QST-REC-EXISTS silent when mod ref resolves',
          not fires(C.check_rec_exists(ok, inf), 'QST-REC-EXISTS'))
    # break: same ref no longer in the union
    bad = new_ctx(quests=q, union=set())
    inf = []
    check('QST-REC-EXISTS fires on dangling mod-quest .dbr ref',
          fires(C.check_rec_exists(bad, inf), 'QST-REC-EXISTS', 'widowletter'))
    # scope guard: an INHERITED native quest's missing ref must NOT block (informational only)
    qn = {'sv_commonmechanics.qst': [cond('Condition_HasItem',
                                          itemRecord='records/item/native_gone.dbr')]}
    inf = []
    viols = C.check_rec_exists(new_ctx(quests=qn, union=set()), inf)
    check('QST-REC-EXISTS does NOT fire on inherited native ref (scope guard)',
          not fires(viols, 'QST-REC-EXISTS') and any(i['contract'].startswith('QST-REC-EXISTS')
                                                     for i in inf))


# ===========================================================================
# QST-PROXY-PLACED
# ===========================================================================
def test_proxy_placed():
    print('CONTRACT: QST-PROXY-PLACED')
    proxy = 'records/drx/quest/proxies custom/q_guardian.dbr'
    q = {'open_bloodcave_portal.qst':
         [cond('Condition_KillAllCreaturesFromProxy', proxyRecord=proxy)]}
    ok = new_ctx(quests=q, union={proxy}, placed={proxy}, have_map=True)
    check('QST-PROXY-PLACED silent when proxy is placed',
          not fires(C.check_proxy_placed(ok), 'QST-PROXY-PLACED'))
    bad = new_ctx(quests=q, union={proxy}, placed=set(), have_map=True)
    check('QST-PROXY-PLACED fires when watched proxy is unplaced',
          fires(C.check_proxy_placed(bad), 'QST-PROXY-PLACED', 'q_guardian'))


# ===========================================================================
# QST-DOOR-UNLOCK
# ===========================================================================
def test_door_unlock():
    print('CONTRACT: QST-DOOR-UNLOCK')
    door = 'records/drxmap/xurder/doors/tj_door01.dbr'
    q = {'urder.qst': [act('Action_UnlockFixedItem', fixedItem=door)]}
    ok = new_ctx(quests=q, union={door}, placed={door}, have_map=True)
    check('QST-DOOR-UNLOCK silent when door is placed',
          not fires(C.check_door_unlock(ok), 'QST-DOOR-UNLOCK'))
    bad = new_ctx(quests=q, union={door}, placed=set(), have_map=True)
    check('QST-DOOR-UNLOCK fires when unlock targets an unplaced door',
          fires(C.check_door_unlock(bad), 'QST-DOOR-UNLOCK', 'tj_door01'))
    # locked=0 no-op path (P2): a door authored unlocked yet handed to an unlock action
    db = FakeArz({door: {'Class': ['FixedItemDoor'], 'locked': [0]}})
    ctx2 = new_ctx(quests=q, union={door}, placed={door}, have_map=True,
                   moddb=db, mod_names={door: door})
    check('QST-DOOR-UNLOCK fires (P2) on locked=0 no-op unlock',
          fires(C.check_door_unlock(ctx2), 'QST-DOOR-UNLOCK'))


# ===========================================================================
# QST-GIVEITEM-NONEMPTY
# ===========================================================================
def test_giveitem():
    print('CONTRACT: QST-GIVEITEM-NONEMPTY')
    table = 'records/drx/quest/supra_special.dbr'
    recipe = 'records/drx/quest/supra_recipe1.dbr'
    q = {'open_bloodcave_portal.qst': [act('Action_GiveItem', **{'item[0]': table})]}
    # compliant: loot table with a resolving lootName entry
    db_ok = FakeArz({table: {'Class': ['LootItemTable_FixedWeight'],
                             'lootName1': [recipe]}})
    ok = new_ctx(quests=q, union={table, recipe}, moddb=db_ok, mod_names={table: table})
    check('QST-GIVEITEM-NONEMPTY silent on a non-empty resolving reward table',
          not fires(C.check_giveitem(ok), 'QST-GIVEITEM-NONEMPTY'))
    # break: loot table whose only entry does NOT resolve (gives nothing)
    db_bad = FakeArz({table: {'Class': ['LootItemTable_FixedWeight'],
                              'lootName1': ['records/drx/quest/dead_recipe.dbr']}})
    bad = new_ctx(quests=q, union={table}, moddb=db_bad, mod_names={table: table})
    check('QST-GIVEITEM-NONEMPTY fires on an all-dead reward loot table',
          fires(C.check_giveitem(bad), 'QST-GIVEITEM-NONEMPTY', 'supra_special'))


# ===========================================================================
# QST-TAG-RESOLVES + QST-TAG-PLACEHOLDER
# ===========================================================================
def test_tags():
    print('CONTRACT: QST-TAG-RESOLVES / QST-TAG-PLACEHOLDER')
    q_good = {'urder.qst': [act('Action_SetQuestNotification', titleTag='tagRealTitle')]}
    ok = new_ctx(quests=q_good, tags={'tagRealTitle'}, have_tag_union=True)
    v = C.check_tags(ok)
    check('QST-TAG-RESOLVES silent when the tag resolves',
          not fires(v, 'QST-TAG-RESOLVES') and not fires(v, 'QST-TAG-PLACEHOLDER'))
    # break resolution: a tag absent from the union
    q_miss = {'urder.qst': [act('Action_SetQuestNotification', titleTag='tagNegTestMissing')]}
    bad = new_ctx(quests=q_miss, tags=set(), have_tag_union=True)
    check('QST-TAG-RESOLVES fires on an unresolved display tag',
          fires(C.check_tags(bad), 'QST-TAG-RESOLVES', 'urder'))
    # break with a debug placeholder (the B-SUPRA-NOTIFY-1 TESTER class); union off so
    # only the placeholder contract can fire.
    q_ph = {'open_bloodcave_portal.qst':
            [act('Action_GiveItem', titleTag='tagLOCATIONTAGTESTER')]}
    ph = new_ctx(quests=q_ph, tags=set(), have_tag_union=False)
    check('QST-TAG-PLACEHOLDER fires on a TESTER placeholder tag',
          fires(C.check_tags(ph), 'QST-TAG-PLACEHOLDER', 'open_bloodcave_portal'))


# ===========================================================================
# QST-LOAD-WINDOW
# ===========================================================================
def test_load_window():
    print('CONTRACT: QST-LOAD-WINDOW')
    q = {'urder.qst': [cond('Condition_OnLevelLoad')]}
    ok = new_ctx(quests=q, have_map=True, reg_index={'urder': 100},
                 registrations=['q'] * 200)
    check('QST-LOAD-WINDOW silent when the SV quest is inside the window',
          not fires(C.check_load_window(ok), 'QST-LOAD-WINDOW'))
    # break: the ported SV quest registered past the proven-safe load window
    bad = new_ctx(quests=q, have_map=True, reg_index={'urder': 260},
                  registrations=['q'] * 270)
    check('QST-LOAD-WINDOW fires when an SV quest sits past idx 254',
          fires(C.check_load_window(bad), 'QST-LOAD-WINDOW', 'urder'))
    # break: total registration budget overflow (> 256)
    over = new_ctx(quests={}, have_map=True, reg_index={}, registrations=['q'] * 300)
    check('QST-LOAD-WINDOW fires when the map registers > 256 quests',
          fires(C.check_load_window(over), 'QST-LOAD-WINDOW', 'world01.map'))


# ===========================================================================
# QST-WIDOW-LETTER
# ===========================================================================
def test_widow_letter():
    print('CONTRACT: QST-WIDOW-LETTER')
    letter = C.LETTER_RECORD   # records/drxmap/quest/finalletter.dbr
    # compliant: no spawn action + the static letter placed in the map
    ok = new_ctx(quests={'widowletter.qst': [cond('Condition_OnLevelLoad')]},
                 have_map=True, placed={letter})
    check('QST-WIDOW-LETTER silent when spawn neutralized + letter placed',
          not fires(C.check_widow_letter(ok), 'QST-WIDOW-LETTER'))
    # break (double-letter regression, P0): the quest still spawns the letter
    dbl = new_ctx(quests={'widowletter.qst':
                          [act('Action_SpawnEntityAtLocation', entity=letter)]},
                  have_map=True, placed={letter})
    v = C.check_widow_letter(dbl)
    check('QST-WIDOW-LETTER fires (P0) on a re-introduced letter spawn',
          any(x['contract'] == 'QST-WIDOW-LETTER' and x['severity'] == 'P0' for x in v))
    # break (no-letter regression, P1): spawn neutralized AND the static letter absent
    none = new_ctx(quests={'widowletter.qst': [cond('Condition_OnLevelLoad')]},
                   have_map=True, placed=set())
    check('QST-WIDOW-LETTER fires (P1) when the static letter is not placed',
          any(x['contract'] == 'QST-WIDOW-LETTER' and x['severity'] == 'P1'
              for x in C.check_widow_letter(none)))


if __name__ == '__main__':
    for t in (test_rec_exists, test_proxy_placed, test_door_unlock, test_giveitem,
              test_tags, test_load_window, test_widow_letter):
        t()
    npass = sum(1 for _n, ok, _d in RESULTS if ok)
    print('\n%d/%d checks PASS' % (npass, len(RESULTS)))
    sys.exit(0 if npass == len(RESULTS) else 1)
