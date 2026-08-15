#!/usr/bin/env python3
r"""Negative tests for contracts_balance.py (DOMAIN F: GLOBAL BALANCE KNOBS).

For every contract: build a COMPLIANT synthetic Ctx (assert the contract stays
silent), then surgically plant the exact regression the contract guards and assert
it FIRES on that subject. A contract that never fires is worthless, so each plant
is a regression that has a real in-game consequence:

  * BAL-DEATHXP-1  the ruling reverted to Iron Lore's `/ 9`; the cap put back to
                   500000; the SUPERSEDED R-80 pair (`/ 90` + 50000) left in place,
                   i.e. the R-251 halving silently did not land; the floor lifted
                   off 0; STR/INT dtype corruption; the engine-loaded record
                   deleted outright.
  * BAL-DEATHXP-2  the "looks retuned but isn't" regression: the divisor is scaled
                   to 180 but deathPenaltyMax is left at the previous 50000, so the
                   capped high-level tail keeps more than the ruled fraction. Also:
                   the same shape with the vanilla 500000 cap, and an over-cut.
  * BAL-TOMBSTONE-1 the R-109 multiplier reverted to vanilla 0.5 (the player is
                   punished twice), pushed above 1.0 (a free-XP loop), dropped,
                   dtype-corrupted, mirrored into a dead lookalike, or the ONE
                   gravestone record retired/de-classed.
  * BAL-TOMBSTONE-2 the equality broken by a multiplier that is not 1.0, and - the
                   defect class R-109 was written against - a cap raised past the
                   float32 exact-integer bound so the marker silently short-changes.
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
STR, INT, FLT = C.DTYPE_STRING, C.DTYPE_INT, C.DTYPE_FLOAT

# The ruled divisor, read out of the ruled equation instead of retyped - so these
# tests keep planting REAL regressions after the next retune instead of quietly
# no-opping (the exact trap R-251 found in the R-109 negtest's '/ 90)' literal).
RULED_DIV = C._divisor_of(C.RULED_EQUATION)


def with_divisor(n):
    """Build an equation of the ruled shape with a different divisor."""
    head = C.RULED_EQUATION[:C.RULED_EQUATION.rindex('/ ') + 2]
    return '%s%g)' % (head, n)


def good_gameengine(**over):
    d = {
        'deathPenaltyEquation': (STR, C.RULED_EQUATION),
        'deathPenaltyMax':      (INT, C.RULED_MAX),
        'deathPenaltyMin':      (INT, C.RULED_MIN),
        'experienceEquation':   (STR, C.SV_EXPERIENCE_EQUATION),
        C.REDEMPTION_FIELD:     (FLT, C.RULED_MULTIPLIER),
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
                  'deathPenaltyMin':      (INT, 0),
                  C.REDEMPTION_FIELD:     (FLT, C.VANILLA_MULTIPLIER)}
    for rec, fields in over.items():
        d[rec] = fields
    return d


def good_gravestone(**over):
    d = {'Class': (STR, C.GRAVESTONE_CLASS)}
    d.update(over)
    return d


def new_ctx(ge=None, pl=None, look=None, grave=None, drop_gameengine=False,
            drop_gravestone=False, maxlvl=None):
    recs = {}
    if not drop_gameengine:
        recs[C.GAMEENGINE] = ge if ge is not None else good_gameengine()
    recs[C.PLAYERLEVELS] = pl if pl is not None else good_playerlevels()
    if not drop_gravestone:
        recs[C.GRAVESTONE] = grave if grave is not None else good_gravestone()
    recs.update(look if look is not None else good_lookalikes())
    # Keep the sweep cheap in the negative tests; the real gate sweeps 1..1000.
    return C.Ctx(recs, max_player_level=maxlvl or 120)


# ===========================================================================
# BAL-DEATHXP-1
# ===========================================================================
def test_values():
    print('CONTRACT: BAL-DEATHXP-1')
    check('silent on a compliant R-80/R-251 gameengine',
          not fires(C.check_deathxp_values(new_ctx()), 'BAL-DEATHXP-1'))

    # break: the ruling reverted to Iron Lore's vanilla divisor
    bad = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, C.VANILLA_EQUATION)))
    check('fires (P0) when deathPenaltyEquation reverts to the vanilla "/ 9"',
          fires(C.check_deathxp_values(bad), 'BAL-DEATHXP-1', C.GAMEENGINE, 'P0'))

    # break: THE R-251 REGRESSION - the halving did not land and the record still
    # carries the pair build92 shipped.
    bad = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, C.SUPERSEDED_R80_EQUATION),
        deathPenaltyMax=(INT, C.SUPERSEDED_R80_MAX)))
    check('fires (P0) when the SUPERSEDED R-80 pair (/ 90 + 50000) is still shipped',
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
    bad = new_ctx(ge=good_gameengine(deathPenaltyMax=(FLT, C.RULED_MAX)))
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
    check('silent when equation AND cap are both scaled by the ruled fraction',
          not fires(C.check_deathxp_reduction(new_ctx()), 'BAL-DEATHXP-2'))

    # THE R-251 headline plant: the divisor was halved to 180 and the cap was left
    # at the PREVIOUS 50000. It passes a naive "is the equation right?" eyeball and
    # still over-charges every capped high-level death.
    half = new_ctx(ge=good_gameengine(deathPenaltyMax=(INT, C.SUPERSEDED_R80_MAX)))
    v = C.check_deathxp_reduction(half)
    check('fires (P0) when the cap is left at the superseded %d (retune half-done)'
          % C.SUPERSEDED_R80_MAX,
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

    # break: the vanilla cap left behind entirely
    bad = new_ctx(ge=good_gameengine(deathPenaltyMax=(INT, C.VANILLA_MAX)))
    check('fires (P0) when the cap is left at the vanilla 500000',
          fires(C.check_deathxp_reduction(bad), 'BAL-DEATHXP-2', C.GAMEENGINE, 'P0'))

    # break: over-cut (someone halves once too often)
    over = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, with_divisor(RULED_DIV * 2)),
        deathPenaltyMax=(INT, C.RULED_MAX // 2)))
    check('fires (P0) on an over-cut (divisor %g, cap %d)'
          % (RULED_DIV * 2, C.RULED_MAX // 2),
          fires(C.check_deathxp_reduction(over), 'BAL-DEATHXP-2', C.GAMEENGINE, 'P0'))
    # ...and the plant really is a different equation (a plant that plants nothing
    # is worse than no plant: it reports PASS forever).
    check('the over-cut plant actually changed the equation',
          with_divisor(RULED_DIV * 2) != C.RULED_EQUATION,
          '%r' % (with_divisor(RULED_DIV * 2),))

    # break: the equation SHAPE changed, so the reduction is unverifiable
    shape = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, 'currentPlayerLevel * 100')))
    check('fires (P0) when the equation shape is no longer numerically checkable',
          fires(C.check_deathxp_reduction(shape), 'BAL-DEATHXP-2', C.GAMEENGINE, 'P0'))


# ===========================================================================
# BAL-TOMBSTONE-1
# ===========================================================================
def test_tombstone_multiplier():
    print('CONTRACT: BAL-TOMBSTONE-1')
    check('silent on a compliant R-109 gameengine + gravestone',
          not fires(C.check_tombstone_multiplier(new_ctx()), 'BAL-TOMBSTONE-1'))

    # break: reverted to the vanilla 0.5 - the player is punished twice
    bad = new_ctx(ge=good_gameengine(
        **{C.REDEMPTION_FIELD: (FLT, C.VANILLA_MULTIPLIER)}))
    check('fires (P0) when RedemptionMultiplier reverts to the vanilla 0.5',
          fires(C.check_tombstone_multiplier(bad), 'BAL-TOMBSTONE-1',
                C.GAMEENGINE, 'P0'))

    # break: above 1.0 - a real free-XP loop
    bad = new_ctx(ge=good_gameengine(**{C.REDEMPTION_FIELD: (FLT, 2.0)}))
    check('fires (P0) when RedemptionMultiplier is above 1.0 (free-XP loop)',
          fires(C.check_tombstone_multiplier(bad), 'BAL-TOMBSTONE-1',
                C.GAMEENGINE, 'P0'))

    # break: the hardcoded-10% reading R-109 explicitly rejects
    bad = new_ctx(ge=good_gameengine(**{C.REDEMPTION_FIELD: (FLT, 0.1)}))
    check('fires (P0) on the rejected hardcoded-10% form (0.1)',
          fires(C.check_tombstone_multiplier(bad), 'BAL-TOMBSTONE-1',
                C.GAMEENGINE, 'P0'))

    # break: the field dropped (engine falls back to its own 0.5 default)
    ge = good_gameengine()
    del ge[C.REDEMPTION_FIELD]
    check('fires (P0) when RedemptionMultiplier is absent entirely',
          fires(C.check_tombstone_multiplier(new_ctx(ge=ge)), 'BAL-TOMBSTONE-1',
                C.GAMEENGINE, 'P0'))

    # break: dtype corruption
    bad = new_ctx(ge=good_gameengine(**{C.REDEMPTION_FIELD: (INT, 1)}))
    check('fires (P0) on RedemptionMultiplier dtype corruption (FLOAT -> INT)',
          fires(C.check_tombstone_multiplier(bad), 'BAL-TOMBSTONE-1',
                C.GAMEENGINE, 'P0'))

    # break: the edit shotgunned into a dead lookalike
    wrong = r'records\game\gameengine.dbr'
    look = good_lookalikes()
    look[wrong] = dict(look[wrong])
    look[wrong][C.REDEMPTION_FIELD] = (FLT, C.RULED_MULTIPLIER)
    check('fires (P1) when the ruled multiplier is mirrored into a dead lookalike',
          fires(C.check_tombstone_multiplier(new_ctx(look=look)), 'BAL-TOMBSTONE-1',
                wrong, 'P1'))

    # break: the ONE gravestone record retired or de-classed (retirement protocol)
    check('fires (P0) when the gravestone record is gone',
          fires(C.check_tombstone_multiplier(new_ctx(drop_gravestone=True)),
                'BAL-TOMBSTONE-1', C.GRAVESTONE, 'P0'))
    check('fires (P0) when the gravestone record is de-classed',
          fires(C.check_tombstone_multiplier(new_ctx(grave=good_gravestone(
              Class=(STR, 'Tile')))), 'BAL-TOMBSTONE-1', C.GRAVESTONE, 'P0'))


# ===========================================================================
# BAL-TOMBSTONE-2
# ===========================================================================
def test_tombstone_equality():
    print('CONTRACT: BAL-TOMBSTONE-2')
    check('silent when recovered == lost on the shipped penalty',
          not fires(C.check_tombstone_equality(new_ctx()), 'BAL-TOMBSTONE-2'))

    # THE COUPLING, in the direction R-251 moved: halve the penalty and the
    # equality must STILL hold with no edit on the recovery side. This is the
    # property R-109 was built for, asserted rather than assumed.
    retuned = new_ctx(ge=good_gameengine(
        deathPenaltyEquation=(STR, with_divisor(RULED_DIV * 2)),
        deathPenaltyMax=(INT, C.RULED_MAX // 2)))
    check('silent when the PENALTY is retuned (halved again) and nothing else moves',
          not fires(C.check_tombstone_equality(retuned), 'BAL-TOMBSTONE-2'))

    # break: recovery below the loss
    bad = new_ctx(ge=good_gameengine(
        **{C.REDEMPTION_FIELD: (FLT, C.VANILLA_MULTIPLIER)}))
    check('fires (P0) when the marker returns HALF the loss (punished twice)',
          fires(C.check_tombstone_equality(bad), 'BAL-TOMBSTONE-2',
                C.GAMEENGINE, 'P0'))

    # break: recovery above the loss
    bad = new_ctx(ge=good_gameengine(**{C.REDEMPTION_FIELD: (FLT, 1.5)}))
    check('fires (P0) when the marker returns MORE than the loss (free-XP loop)',
          fires(C.check_tombstone_equality(bad), 'BAL-TOMBSTONE-2',
                C.GAMEENGINE, 'P0'))

    # break: the cap pushed past the float32 exact-integer bound, where the
    # engine's int -> float32 -> mulss -> truncate round-trip loses low bits
    bad = new_ctx(ge=good_gameengine(
        deathPenaltyMax=(INT, C.FLOAT32_EXACT_INT_BOUND + 1)))
    check('fires (P0) when deathPenaltyMax is at/above the float32 exact-int bound',
          fires(C.check_tombstone_equality(bad), 'BAL-TOMBSTONE-2',
                C.GAMEENGINE, 'P0'))

    # break: a non-positive cap - the penalty can never take anything, so R-109
    # has nothing to mirror; that is a penalty-side change needing its own ruling.
    bad = new_ctx(ge=good_gameengine(deathPenaltyMax=(INT, 0)))
    check('fires (P0) when deathPenaltyMax is non-positive',
          fires(C.check_tombstone_equality(bad), 'BAL-TOMBSTONE-2',
                C.GAMEENGINE, 'P0'))


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
                   'deathPenaltyMin':      (INT, 0),
                   C.REDEMPTION_FIELD:     (FLT, C.VANILLA_MULTIPLIER)}
    check('fires (P1) when the ruled value is written into a dead lookalike',
          fires(C.check_dead_lookalikes(new_ctx(look=look)), 'BAL-DEATHXP-3', wrong, 'P1'))

    # break: a lookalike's cap edited
    look = good_lookalikes()
    look[r'records\xpack\game\drxgameengine.dbr']['deathPenaltyMax'] = (INT, C.RULED_MAX)
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
    print('CROSS-CHECK: contract constants == tools/patches/*.py')
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'patches'))
    import death_xp_penalty as M   # noqa: E402
    import tombstone_xp_recovery as T   # noqa: E402
    check('ruled equation matches the build module', M.EQ_NEW == C.RULED_EQUATION,
          '%r vs %r' % (M.EQ_NEW, C.RULED_EQUATION))
    check('ruled cap matches the build module', M.MAX_NEW == C.RULED_MAX)
    check('superseded R-80 equation matches the build module',
          M.EQ_R80 == C.SUPERSEDED_R80_EQUATION)
    check('superseded R-80 cap matches the build module',
          M.MAX_R80 == C.SUPERSEDED_R80_MAX)
    check('vanilla equation matches the build module', M.EQ_OLD == C.VANILLA_EQUATION)
    check('vanilla cap matches the build module', M.MAX_OLD == C.VANILLA_MAX)
    check('reduction constant matches the build module',
          abs(M.REDUCTION - C.RULED_REDUCTION) < 1e-12)
    check('the same 5 dead lookalikes are enumerated on both sides',
          set(M.DEAD_LOOKALIKES) == set(C.DEAD_LOOKALIKES))
    check('penalty math agrees between build module and gate',
          abs(M.penalty(85, 2, M.DIV_NEW, M.MAX_NEW)
              - C.clamp_penalty(85, 2, RULED_DIV, C.RULED_MAX)) < 1e-9)

    # the ruled constants are internally coherent: the cap is the same fraction of
    # vanilla as the equation, and R-251 really is "another 50%" on R-80.
    check('the ruled cap is exactly the ruled fraction of the vanilla cap',
          abs(C.RULED_MAX - C.RULED_REDUCTION * C.VANILLA_MAX) < 1e-6 * C.VANILLA_MAX,
          '%d vs %.3f x %d' % (C.RULED_MAX, C.RULED_REDUCTION, C.VANILLA_MAX))
    check('the ruled divisor is exactly vanilla / the ruled fraction',
          abs(RULED_DIV - (C._divisor_of(C.VANILLA_EQUATION) / C.RULED_REDUCTION))
          < 1e-9,
          'divisor %r' % (RULED_DIV,))
    check('R-251 is exactly half of the R-80 penalty (divisor x2, cap /2)',
          RULED_DIV == 2 * C._divisor_of(C.SUPERSEDED_R80_EQUATION)
          and C.RULED_MAX * 2 == C.SUPERSEDED_R80_MAX)

    # R-109 side
    check('ruled RedemptionMultiplier matches the build module',
          abs(T.MULT_NEW - C.RULED_MULTIPLIER) < 1e-12)
    check('vanilla RedemptionMultiplier matches the build module',
          abs(T.MULT_OLD - C.VANILLA_MULTIPLIER) < 1e-12)
    check('the float32 exact-integer bound matches the build module',
          T.FLOAT32_EXACT_INT_BOUND == C.FLOAT32_EXACT_INT_BOUND)
    check('the gravestone record + Class match the build module',
          T.GRAVESTONE == C.GRAVESTONE and T.GRAVESTONE_CLASS == C.GRAVESTONE_CLASS)

    # the two independent models of the engine round-trip must agree, or one of
    # them is proving something the other does not.
    same = all(T.xp_lost_int(lvl, dv, RULED_DIV, C.RULED_MAX, C.RULED_MIN)
               == C.xp_lost_int(lvl, dv, RULED_DIV, C.RULED_MAX, C.RULED_MIN)
               for lvl in (1, 5, 40, 85, 100, 260, 1000) for dv in (0, 1, 2))
    check('the engine death-penalty model agrees between module and gate', same)
    same = all(T.xp_recoverable(u, C.RULED_MULTIPLIER)
               == C.xp_recoverable(u, C.RULED_MULTIPLIER)
               for u in (0, 1, 7, 12345, C.RULED_MAX, C.FLOAT32_EXACT_INT_BOUND - 1))
    check('the engine recovery model agrees between module and gate', same)


if __name__ == '__main__':
    for t in (test_values, test_reduction, test_tombstone_multiplier,
              test_tombstone_equality, test_lookalikes, test_xp_gain,
              test_module_agreement):
        t()
    npass = sum(1 for _n, ok, _d in RESULTS if ok)
    print('\n%d/%d checks PASS' % (npass, len(RESULTS)))
    sys.exit(0 if npass == len(RESULTS) else 1)
