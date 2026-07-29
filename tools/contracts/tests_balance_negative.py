#!/usr/bin/env python3
r"""Negative tests for contracts_balance.py (DOMAIN F: GLOBAL BALANCE KNOBS).

For every contract: build a COMPLIANT synthetic Ctx (assert the contract stays
silent), then surgically plant the exact regression the contract guards and assert
it FIRES on that subject. A contract that never fires is worthless, so each plant
is a regression that has a real in-game consequence:

  * BAL-DEATHXP-1  the R-80 divisor reverted to Iron Lore's `/ 9`; the cap put back
                   to 500000; the floor lifted off 0; STR/INT dtype corruption; the
                   engine-loaded record deleted outright.
  * BAL-DEATHXP-2  the "looks fixed but isn't" regression: the divisor is scaled to
                   90 but deathPenaltyMax is left at 500000, so a level-100
                   Legendary character still loses 500000 XP - a -84% cut where the
                   ruling says -90%. Also: an over-cut (divisor 900).
  * BAL-DEATHXP-3  the wrong-record fix: the ruled value written into a dead
                   lookalike (silent in-game no-op).
  * BAL-XPGAIN-1   scope creep: XP GAIN or the level curve moved along with the
                   death penalty.

Self-contained - it builds tiny in-memory Ctx objects, so it needs NO big artifacts.
Run:
  python tools/contracts/tests_balance_negative.py
Exits 0 if every contract's negative test PASSES, 1 otherwise.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import contracts_balance as C   # noqa: E402

RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, ok, detail))
    print('  %s %s%s' % ('PASS' if ok else 'FAIL', name,
                         ('  [%s]' % detail) if detail and not ok else ''))


def fires(viols, cid, subject=None, severity=None):
    for v in viols:
        if v['contract'] != cid:
            continue
        if subject is not None and C._norm(subject) not in C._norm(v['subject']):
            continue
        if severity is not None and v['severity'] != severity:
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Ctx builders
# ---------------------------------------------------------------------------
STR, INT = C.DTYPE_STRING, C.DTYPE_INT


def good_gameengine(**over):
    d = {
        'deathPenaltyEquation': (STR, C.RULED_EQUATION),
        'deathPenaltyMax':      (INT, C.RULED_MAX),
        'deathPenaltyMin':      (INT, C.RULED_MIN),
        'experienceEquation':   (STR, C.SV_EXPERIENCE_EQUATION),
    }
    d.update(over)
    return d


def good_playerlevels(**over):
    d = {
        'experienceLevelEquation': (STR, C.SV_LEVEL_EQUATION),
        'maxPlayerLevel':          (INT, C.SV_MAX_PLAYER_LEVEL),
    }
    d.update(over)
    return d


def good_lookalikes(**over):
    d = {}
    for rec, eq in C.DEAD_LOOKALIKES.items():
        d[rec] = {'deathPenaltyEquation': (STR, eq),
                  'deathPenaltyMax':      (INT, C.VANILLA_MAX),
                  'deathPenaltyMin':      (INT, 0)}
    for rec, fields in over.items():
        d[rec] = fields
    return d


def new_ctx(ge=None, pl=None, look=None, drop_gameengine=False, maxlvl=None):
    recs = {}
    if not drop_gameengine:
        recs[C.GAMEENGINE] = ge if ge is not None else good_gameengine()
    recs[C.PLAYERLEVELS] = pl if pl is not None else good_playerlevels()
    recs.update(look if look is not None else good_lookalikes())
    # Keep the sweep cheap in the negative tests; the real gate sweeps 1..1000.
    return C.Ctx(recs, max_player_level=maxlvl or 120)


# ===========================================================================
# BAL-DEATHXP-1
# ===========================================================================
def test_values():
    print('CONTRACT: BAL-DEATHXP-1')
    check('silent on a compliant R-80 gameengine',
          not fires(C.check_deathxp_values(new_ctx()), 'BAL-DEATHXP-1'))

    # break: the ruling reverted to Iron Lore's vanilla divisor
    bad = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, C.VANILLA_EQUATION)))
    check('fires (P0) when deathPenaltyEquation reverts to the vanilla "/ 9"',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))

    # break: the cap put back
    bad = new_ctx(ge=good_gameengine(deathPenaltyMax=(INT, C.VANILLA_MAX)))
    check('fires (P0) when deathPenaltyMax reverts to 500000',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))

    # break: the clamp floor lifted off 0
    bad = new_ctx(ge=good_gameengine(deathPenaltyMin=(INT, 5000)))
    check('fires (P0) when deathPenaltyMin is lifted off 0',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))

    # break: dtype corruption (the CLAUDE.md INT/FLOAT/STR law)
    bad = new_ctx(ge=good_gameengine(deathPenaltyMax=(1, C.RULED_MAX)))
    check('fires (P0) on deathPenaltyMax dtype corruption (INT -> FLOAT)',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))
    bad = new_ctx(ge=good_gameengine(deathPenaltyEquation=(INT, C.RULED_EQUATION)))
    check('fires (P0) on deathPenaltyEquation dtype corruption (STR -> INT)',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))

    # break: the engine-loaded record is gone entirely
    bad = new_ctx(drop_gameengine=True)
    check('fires (P0) when the engine-loaded gameengine record is absent',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))


# ===========================================================================
# BAL-DEATHXP-2
# ===========================================================================
def test_reduction():
    print('CONTRACT: BAL-DEATHXP-2')
    check('silent when equation AND cap are both scaled by 0.1',
          not fires(C.check_deathxp_reduction(new_ctx()), 'BAL-DEATHXP-2'))

    # THE headline plant: divisor scaled, cap forgotten. Passes a naive
    # "is the equation right?" eyeball and still costs a L100 Legendary
    # character the full 500000 XP.
    half = new_ctx(ge=good_gameengine(deathPenaltyMax=(INT, C.VANILLA_MAX)))
    v = C.check_deathxp_reduction(half)
    check('fires (P0) when the cap is left at 500000 (only -84% at high level)',
          fires(v, 'BAL-DEATHXP-2', C.GAMEENGINE, 'P0'))
    # and its evidence must name the HIGH-level regime (where the ruling says the
    # pain is), not level 1 where the absolute error is a fraction of an XP point.
    ev = [x['evidence'] for x in v if x['contract'] == 'BAL-DEATHXP-2']
    named_level = None
    if ev:
        head = ev[0].split('difficulty')[0]           # "...at level <N> "
        named_level = int(head.strip().split()[-1])
    check('evidence names a high level (>= 80), not level 1',
          named_level is not None and named_level >= 80,
          'named level %r' % (named_level,))

    # break: over-cut (someone "rounds" the divisor to 900)
    over = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, C.RULED_EQUATION.replace('/ 90)', '/ 900)')),
        deathPenaltyMax=(INT, 5000)))
    check('fires (P0) on an over-cut (divisor 900 = -99%)',
          fires(C.check_deathxp_reduction(over), 'BAL-DEATHXP-2', C.GAMEENGINE, 'P0'))

    # break: the equation SHAPE changed, so the reduction is unverifiable
    shape = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, 'currentPlayerLevel * 100')))
    check('fires (P0) when the equation shape is no longer numerically checkable',
          fires(C.check_deathxp_reduction(shape), 'BAL-DEATHXP-2', C.GAMEENGINE, 'P0'))


# ===========================================================================
# BAL-DEATHXP-3
# ===========================================================================
def test_lookalikes():
    print('CONTRACT: BAL-DEATHXP-3')
    check('silent when all 5 dead lookalikes hold their vanilla values',
          not fires(C.check_dead_lookalikes(new_ctx()), 'BAL-DEATHXP-3'))

    # break: the classic wrong-record fix - the ruled value written into the
    # pre-Immortal-Throne records\game\gameengine.dbr (a silent in-game no-op)
    wrong = r'records\game\gameengine.dbr'
    look = good_lookalikes()
    look[wrong] = {'deathPenaltyEquation': (STR, C.RULED_EQUATION),
                   'deathPenaltyMax':      (INT, C.RULED_MAX),
                   'deathPenaltyMin':      (INT, 0)}
    check('fires (P1) when the ruled value is written into a dead lookalike',
          fires(C.check_dead_lookalikes(new_ctx(look=look)), 'BAL-DEATHXP-3', wrong, 'P1'))

    # break: a lookalike's cap edited
    look = good_lookalikes()
    look[r'records\xpack\game\drxgameengine.dbr']['deathPenaltyMax'] = (INT, 50000)
    check('fires (P1) when a lookalike deathPenaltyMax is edited',
          fires(C.check_dead_lookalikes(new_ctx(look=look)), 'BAL-DEATHXP-3',
                'drxgameengine', 'P1'))


# ===========================================================================
# BAL-XPGAIN-1
# ===========================================================================
def test_xp_gain():
    print('CONTRACT: BAL-XPGAIN-1')
    check('silent when XP gain + curve are untouched',
          not fires(C.check_xp_gain_untouched(new_ctx()), 'BAL-XPGAIN-1'))

    # break: the lane "helpfully" also buffed XP gain
    bad = new_ctx(ge=good_gameengine(
        experienceEquation=(STR, C.SV_EXPERIENCE_EQUATION.replace('*15', '*30'))))
    check('fires (P1) when experienceEquation (XP gain) is moved',
          fires(C.check_xp_gain_untouched(bad), 'BAL-XPGAIN-1', C.GAMEENGINE, 'P1'))

    # break: the level curve flattened
    bad = new_ctx(pl=good_playerlevels(
        experienceLevelEquation=(STR, C.SV_LEVEL_EQUATION.replace('^3.25', '^2.5'))))
    check('fires (P1) when the XP level curve is moved',
          fires(C.check_xp_gain_untouched(bad), 'BAL-XPGAIN-1', C.PLAYERLEVELS, 'P1'))

    # break: the level cap moved
    bad = new_ctx(pl=good_playerlevels(maxPlayerLevel=(INT, 85)))
    check('fires (P1) when maxPlayerLevel is moved',
          fires(C.check_xp_gain_untouched(bad), 'BAL-XPGAIN-1', C.PLAYERLEVELS, 'P1'))


# ===========================================================================
# cross-check: the gate constants and the BUILD module constants agree
# ===========================================================================
def test_module_agreement():
    print('CROSS-CHECK: contract constants == tools/patches/death_xp_penalty.py')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'patches'))
    import death_xp_penalty as M   # noqa: E402
    check('ruled equation matches the build module', M.EQ_NEW == C.RULED_EQUATION,
          '%r vs %r' % (M.EQ_NEW, C.RULED_EQUATION))
    check('ruled cap matches the build module', M.MAX_NEW == C.RULED_MAX)
    check('vanilla equation matches the build module', M.EQ_OLD == C.VANILLA_EQUATION)
    check('vanilla cap matches the build module', M.MAX_OLD == C.VANILLA_MAX)
    check('reduction constant matches the build module',
          abs(M.REDUCTION - C.RULED_REDUCTION) < 1e-12)
    check('the same 5 dead lookalikes are enumerated on both sides',
          set(M.DEAD_LOOKALIKES) == set(C.DEAD_LOOKALIKES))
    check('penalty math agrees between build module and gate',
          abs(M.penalty(85, 2, 90, M.MAX_NEW)
              - C.clamp_penalty(85, 2, 90, C.RULED_MAX)) < 1e-9)


if __name__ == '__main__':
    for t in (test_values, test_reduction, test_lookalikes, test_xp_gain,
              test_module_agreement):
        t()
    npass = sum(1 for _n, ok, _d in RESULTS if ok)
    print('\n%d/%d checks PASS' % (npass, len(RESULTS)))
    sys.exit(0 if npass == len(RESULTS) else 1)
