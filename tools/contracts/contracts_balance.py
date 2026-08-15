r"""PERMANENT CONTRACT SUITE - DOMAIN F: GLOBAL GAME-BALANCE KNOBS.

Scope (deliberately narrow): the handful of GLOBAL, engine-loaded balance knobs that
live on ONE record each and that a single stray write can silently revert, taking a
Will ruling with it. Everything here is asserted over the SHIPPED .arz.

This domain owns the on-death EXPERIENCE economy: the death penalty itself
(R-80, retuned by R-254) and the death-marker recovery that must EQUAL it
(R-109). They live on the SAME record and are ruled as a pair, so they are gated
as a pair - a lane that retunes one and not the other is exactly the regression
these contracts exist to red.

WHY IT NEEDS A PERMANENT GATE
-----------------------------
`records\xpack\game\gameengine.dbr` is a SHARED record - `tools/patches/damage_display.py`
already writes it, and any future module that "restores a vanilla field" on it could
put `deathPenaltyEquation` back to Iron Lore's `/ 9` without anyone noticing: nothing
in the game surfaces the number, and a player only feels it after dying at level 80.
There are also FIVE dead lookalike gameengine records carrying the vanilla value, so
a careless fix is one autocomplete away from editing the wrong one and shipping a
silent no-op.

METHOD (the suite's standard): the requirement is DERIVED from the engine's own
behaviour, implemented over our shipped artifact, and negative-tested
(tools/contracts/tests_balance_negative.py plants the exact regressions and proves
each check fires).

ENGINE GROUND TRUTH (measured 2026-07-28 from the shipped binaries):
  * `Game.dll` contains exactly ONE `*GameEngine.dbr` path literal in the entire
    install - `Records/XPack/Game/GameEngine.dbr` (TQ.exe and Editor.exe contain
    none). That is the record the engine loads; the other five deathPenalty-bearing
    records in the arz are dead authoring copies.
  * `Game.dll`'s string table carries `deathPenaltyEquation`, `deathPenaltyMin`,
    `deathPenaltyMax` next to the loader error `-=- GameEngine Equation load
    failure : deathPenaltyEquation`, and the equation variables `currentPlayerLevel`
    and `gameDifficultyDV`. => XP lost on death = clamp(equation, min, max), with
    difficulty entering ONLY through `gameDifficultyDV` (0/1/2).
  * Vanilla TQAE, SV 0.98i, SV 0.9 and SV 0.41 all ship the identical vanilla triple
    `(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)` / 500000 / 0, so any
    deviation from the ruled values is a regression, never inherited upstream drift.

INTERFACE (composes with the other domain modules without shared files):
  run(cfg: dict) -> list[dict]      cfg keys used: arz
  CONTRACTS: list of {'id','name','asserts','derived_from'}
  each violation: {'contract','severity','subject','message','evidence'}

WHITELIST: tools/contracts/whitelist_balance.txt - lines "<CONTRACT-ID> <subject>".

STANDALONE:
  python tools/contracts/contracts_balance.py <arz>
"""
import json
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # tools/ on path

# --------------------------------------------------------------------------- #
# The ruled values (R-80 as retuned by R-254, plus R-109). Single source of truth
# for the gate; the build-side modules tools/patches/death_xp_penalty.py and
# tools/patches/tombstone_xp_recovery.py carry the same constants and this
# contract cross-checks them so the two sides can never silently diverge.
# --------------------------------------------------------------------------- #
GAMEENGINE = r'records\xpack\game\gameengine.dbr'

RULED_EQUATION = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 180)'
RULED_MAX = 25000
RULED_MIN = 0

# The pair R-80 shipped through build92, SUPERSEDED by R-254 ("another 50%").
# Named, not anonymous: "the retune did not land" is a distinct regression from
# "the whole ruling reverted to vanilla", and the negative tests plant both.
SUPERSEDED_R80_EQUATION = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)'
SUPERSEDED_R80_MAX = 50000

VANILLA_EQUATION = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)'
VANILLA_MAX = 500000
RULED_REDUCTION = 0.05          # keep 5% of the vanilla loss == -95% (R-80 + R-254)

# R-109: the death marker returns `trunc(realised_loss * RedemptionMultiplier)`,
# so 1.0 is the equality. 0.5 is vanilla TQAE (and the engine loader's default),
# which is what the five dead lookalikes still carry.
GRAVESTONE = r'records\xpack\item\gravestones\gravestonegreece.dbr'
GRAVESTONE_CLASS = 'FixedItemGravestone'
REDEMPTION_FIELD = 'RedemptionMultiplier'
RULED_MULTIPLIER = 1.0
VANILLA_MULTIPLIER = 0.5
FLOAT32_EXACT_INT_BOUND = 1 << 24
_TOL = 1e-9

DTYPE_INT, DTYPE_FLOAT, DTYPE_STRING = 0, 1, 2

# The five deathPenalty-bearing records the engine never loads. They must stay at
# their own vanilla values: an edit here is either a wrong-record fix (a silent
# no-op in game) or a confusing mirror that hides which record is live.
DEAD_LOOKALIKES = {
    r'records\xpack\game\drxgameengine.dbr':      VANILLA_EQUATION,
    r'records\xpack\game\copy of gameengine.dbr': VANILLA_EQUATION,
    r'records\xpack\game\xxxgameengine.dbr':      VANILLA_EQUATION,
    r'records\game\gameengine.dbr':               VANILLA_EQUATION,
    r'records\game\cost backup\gameengine.dbr':
        '(currentPlayerLevel^2.95) * ((1+ (2 * gameDifficultyDV)) / 3)',
}

CONTRACTS = [
    {'id': 'BAL-DEATHXP-1', 'name': 'Death XP penalty holds the ruled -95% values',
     'asserts': 'the engine-loaded xpack gameengine carries deathPenaltyEquation '
                '"/ 180", deathPenaltyMax 25000, deathPenaltyMin 0, with STR/INT '
                'dtypes intact',
     'derived_from': 'Will R-80 2026-07-27 ("cut by like 90%") retuned by R-254 '
                     '2026-08-14 ("another 50% from what it currently is at"); '
                     'Game.dll loads only Records/XPack/Game/GameEngine.dbr and '
                     'reads exactly these 3 fields'},
    {'id': 'BAL-DEATHXP-2', 'name': 'Death XP penalty really is a 95% cut',
     'asserts': 'clamp(shipped equation, min, max) == 0.05 x clamp(vanilla equation, '
                '0, 500000) at every level 1..maxPlayerLevel on Normal/Epic/Legendary',
     'derived_from': 'halving the divisor while leaving the previous cap in place '
                     'under-delivers in exactly the capped high-level regime the '
                     'ruling names (the "looks retuned but is not" regression)'},
    {'id': 'BAL-TOMBSTONE-1', 'name': 'Death-marker recovery multiplier holds R-109',
     'asserts': 'RedemptionMultiplier == 1.0 (FLOAT) on the engine-loaded xpack '
                'gameengine, the 5 dead lookalikes still carry vanilla 0.5, and the '
                'ONE gravestone record Game.dll hard-codes still exists as '
                'Class FixedItemGravestone',
     'derived_from': 'Will R-109 2026-07-30 ("lets make the tombstone xp recovery '
                     'match the xp lost upon dying"); Game.dll computes recovered = '
                     'trunc(realised_loss * RedemptionMultiplier), so 1.0 IS the '
                     'equality and 0.5 punishes the player twice'},
    {'id': 'BAL-TOMBSTONE-2', 'name': 'Recovery EQUALS the shipped death penalty',
     'asserts': 'trunc(float32(lost) * shipped multiplier) == lost for the penalty '
                'this arz actually ships, at every level x difficulty and across the '
                'realised-loss domain, with the cap inside the float32 exact-integer '
                'bound 2^24',
     'derived_from': 'R-109 rules the INVARIANT, not the number: it is re-derived '
                     'from the SHIPPED penalty knobs so a retune like R-254 proves '
                     'itself instead of silently desynchronising the marker'},
    {'id': 'BAL-DEATHXP-3', 'name': 'Dead gameengine lookalikes untouched',
     'asserts': 'the 5 non-engine-loaded deathPenalty-bearing records still carry '
                'their own vanilla values',
     'derived_from': 'only records\\xpack\\game\\gameengine.dbr is referenced by '
                     'Game.dll; editing a lookalike is a silent in-game no-op'},
    {'id': 'BAL-XPGAIN-1', 'name': 'XP-gain economy not collaterally moved',
     'asserts': 'experienceEquation on the engine-loaded gameengine and '
                'experienceLevelEquation/maxPlayerLevel on the live player-level '
                'record are unchanged from the shipped SV values',
     'derived_from': 'R-80 authorises a death-penalty change only; a build that also '
                     'moves XP gain or the level curve has exceeded the ruling'},
]

# The live XP economy values the death-penalty lane must NOT move. Taken from the
# shipped SV 0.98i base (identical in the deployed DEV arz 1c27d5fa).
PLAYERLEVELS = r'records\creature\pc\playerlevels.dbr'
SV_EXPERIENCE_EQUATION = ('((monsterLevel*15)+((monsterLevel-averagePlayerLevel)*'
                          '(averagePlayerLevel/3.5)))*(1+(monsterExperience/100))')
SV_LEVEL_EQUATION = ('((1.2 ^ playerLevel) * ((1 + (playerLevel / 0.8)) * '
                     '(0.0 * playerLevel))) + (65 * ((playerLevel + 1) ^3.25)')
SV_MAX_PLAYER_LEVEL = 1000


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _norm(s):
    return str(s).replace('/', '\\').strip().lower()


def _v(contract, severity, subject, message, evidence):
    return {'contract': contract, 'severity': severity, 'subject': subject,
            'message': message, 'evidence': evidence}


def clamp_penalty(level, dv, divisor, cap, floor=0):
    """The engine's clamp(equation, deathPenaltyMin, deathPenaltyMax)."""
    raw = (float(level) ** 3) * ((1.0 + (3.0 * dv)) / float(divisor))
    return min(max(raw, floor), float(cap))


def _f32(x):
    """Round through IEEE binary32, the way the engine stores an equation result
    with `fstp dword ptr` and reloads it for `mulss`."""
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


def xp_lost_int(level, dv, divisor, cap, floor=0):
    """The INTEGER the engine subtracts on death, modelled from
    GetPlayerDeathExperiencePenalty (Game.dll VA 0x101945a0): float32 equation
    result, floored at 0, rounded half-up (+0.5 then fistp/chop), then clamped."""
    raw = _f32(max((float(level) ** 3) * ((1.0 + (3.0 * dv)) / float(divisor)), 0.0))
    return min(max(math.trunc(float(raw) + 0.5), int(floor)), int(cap))


def xp_recoverable(lost, multiplier):
    """What the death marker returns, modelled from
    GetPlayerExperienceRedemptionAmount (Game.dll VA 0x10194f60):
    trunc(float32(realised_loss) * RedemptionMultiplier)."""
    return math.trunc(_f32(float(lost)) * float(multiplier))


def _divisor_of(equation):
    """Pull the trailing '/ <n>)' divisor out of an equation of the ruled SHAPE.
    Returns None when the equation is not that shape (the caller then reports the
    shape mismatch rather than a number)."""
    head = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / '
    if not (equation.startswith(head) and equation.endswith(')')):
        return None
    try:
        return float(equation[len(head):-1])
    except ValueError:
        return None


class Ctx(object):
    """Everything the checks read. Built from the arz, or handed in directly by the
    negative tests (which never need a 54 MB artifact)."""

    def __init__(self, fields_by_record, max_player_level=SV_MAX_PLAYER_LEVEL):
        # {record_path_lower: {field: (dtype, value)}}
        self.recs = {_norm(k): v for k, v in fields_by_record.items()}
        self.max_player_level = max_player_level

    def get(self, rec, field):
        return self.recs.get(_norm(rec), {}).get(field)

    def has(self, rec):
        return _norm(rec) in self.recs

    def value(self, rec, field):
        got = self.get(rec, field)
        return None if got is None else got[1]

    def dtype(self, rec, field):
        got = self.get(rec, field)
        return None if got is None else got[0]


def _build_context(cfg):
    from arz_patcher import ArzDatabase
    db = ArzDatabase.from_arz(Path(cfg['arz']))
    wanted = ([GAMEENGINE] + list(DEAD_LOOKALIKES) + [PLAYERLEVELS, GRAVESTONE])
    by_lower = {_norm(n): n for n in db.record_names()}
    out = {}
    for rec in wanted:
        real = by_lower.get(_norm(rec))
        if real is None:
            continue
        fields = db.get_fields(real) or {}
        out[rec] = {k.split('###')[0]: (tf.dtype, tf.value) for k, tf in fields.items()}
    maxlvl = SV_MAX_PLAYER_LEVEL
    if PLAYERLEVELS in out and 'maxPlayerLevel' in out[PLAYERLEVELS]:
        try:
            maxlvl = int(out[PLAYERLEVELS]['maxPlayerLevel'][1])
        except (TypeError, ValueError):
            pass
    return Ctx(out, max_player_level=maxlvl)


# --------------------------------------------------------------------------- #
# BAL-DEATHXP-1 - the ruled values are on the engine-loaded record
# --------------------------------------------------------------------------- #
def check_deathxp_values(ctx):
    cid = 'BAL-DEATHXP-1'
    out = []
    if not ctx.has(GAMEENGINE):
        return [_v(cid, 'P0', GAMEENGINE,
                   'the engine-loaded GameEngine record is absent from the shipped arz',
                   'Game.dll loads Records/XPack/Game/GameEngine.dbr')]

    eq = ctx.value(GAMEENGINE, 'deathPenaltyEquation')
    if eq != RULED_EQUATION:
        out.append(_v(cid, 'P0', GAMEENGINE,
                      'deathPenaltyEquation is not the ruled value (death XP penalty '
                      'reverted, or re-tuned without a ruling). The ruled state is '
                      'R-80 as retuned by R-254; an arz built before R-254 lands '
                      'shows the superseded "/ 90" here',
                      'want %r, got %r' % (RULED_EQUATION, eq)))
    elif ctx.dtype(GAMEENGINE, 'deathPenaltyEquation') != DTYPE_STRING:
        out.append(_v(cid, 'P0', GAMEENGINE,
                      'deathPenaltyEquation dtype corrupted (must stay STR)',
                      'dtype=%r want %r' % (ctx.dtype(GAMEENGINE, 'deathPenaltyEquation'),
                                            DTYPE_STRING)))

    mx = ctx.value(GAMEENGINE, 'deathPenaltyMax')
    try:
        mx_i = int(mx)
    except (TypeError, ValueError):
        mx_i = None
    if mx_i != RULED_MAX:
        out.append(_v(cid, 'P0', GAMEENGINE,
                      'deathPenaltyMax is not the ruled cap (R-80 as retuned by '
                      'R-254; an arz built before R-254 lands shows 50000 here)',
                      'want %d, got %r' % (RULED_MAX, mx)))
    elif ctx.dtype(GAMEENGINE, 'deathPenaltyMax') != DTYPE_INT:
        out.append(_v(cid, 'P0', GAMEENGINE,
                      'deathPenaltyMax dtype corrupted (must stay INT)',
                      'dtype=%r want %r' % (ctx.dtype(GAMEENGINE, 'deathPenaltyMax'),
                                            DTYPE_INT)))

    mn = ctx.value(GAMEENGINE, 'deathPenaltyMin')
    try:
        mn_i = int(mn)
    except (TypeError, ValueError):
        mn_i = None
    if mn_i != RULED_MIN:
        out.append(_v(cid, 'P0', GAMEENGINE,
                      'deathPenaltyMin moved off 0 - the clamp floor is part of the '
                      'ruled reduction',
                      'want %d, got %r' % (RULED_MIN, mn)))
    return out


# --------------------------------------------------------------------------- #
# BAL-DEATHXP-2 - it really is a 90% cut, everywhere
# --------------------------------------------------------------------------- #
def check_deathxp_reduction(ctx):
    cid = 'BAL-DEATHXP-2'
    if not ctx.has(GAMEENGINE):
        return []
    eq = ctx.value(GAMEENGINE, 'deathPenaltyEquation')
    div = _divisor_of(eq or '')
    if div is None:
        return [_v(cid, 'P0', GAMEENGINE,
                   'deathPenaltyEquation no longer has the vanilla SHAPE, so the '
                   'reduction cannot be verified numerically',
                   'got %r' % (eq,))]
    try:
        cap = int(ctx.value(GAMEENGINE, 'deathPenaltyMax'))
        floor = int(ctx.value(GAMEENGINE, 'deathPenaltyMin'))
    except (TypeError, ValueError):
        return [_v(cid, 'P0', GAMEENGINE, 'deathPenaltyMax/Min are not integers',
                   'max=%r min=%r' % (ctx.value(GAMEENGINE, 'deathPenaltyMax'),
                                      ctx.value(GAMEENGINE, 'deathPenaltyMin')))]

    # Sweep the whole level x difficulty domain. Two separate roll-ups:
    #   ratio_bad  - ANY point whose ratio deviates from the ruled 0.10 (the gate)
    #   worst      - the point with the largest ABSOLUTE XP error (the evidence).
    # Ranking the evidence by absolute XP, not by ratio, makes the message name the
    # regime the player actually feels: a divisor-only "fix" that leaves the 500000
    # cap in place is off by ~450,000 XP at level 100 Legendary and by 0.01 XP at
    # level 1, and only the former is worth printing.
    ratio_bad = False
    worst = None
    for lvl in range(1, int(ctx.max_player_level) + 1):
        for dv in (0, 1, 2):
            vanilla = clamp_penalty(lvl, dv, 9.0, VANILLA_MAX, 0)
            shipped = clamp_penalty(lvl, dv, div, cap, floor)
            if vanilla <= 0:
                continue
            if abs((shipped / vanilla) - RULED_REDUCTION) > 1e-9:
                ratio_bad = True
            err = abs(shipped - (RULED_REDUCTION * vanilla))
            if worst is None or err > worst[0]:
                worst = (err, lvl, dv, vanilla, shipped)
    if not ratio_bad or worst is None:
        return []
    err, lvl, dv, vanilla, shipped = worst
    return [_v(cid, 'P0', GAMEENGINE,
               'the shipped death penalty is not a uniform %.0f%% cut of vanilla'
               % (100 * (1 - RULED_REDUCTION)),
               'largest XP error at level %d difficulty DV=%d: vanilla %.0f XP -> '
               'shipped %.0f XP (%.1f%% cut, want %.1f%%; off by %.0f XP)'
               % (lvl, dv, vanilla, shipped, 100 * (1 - shipped / vanilla),
                  100 * (1 - RULED_REDUCTION), err))]


# --------------------------------------------------------------------------- #
# BAL-DEATHXP-3 - the dead lookalikes stay dead
# --------------------------------------------------------------------------- #
def check_dead_lookalikes(ctx):
    cid = 'BAL-DEATHXP-3'
    out = []
    for rec, want_eq in DEAD_LOOKALIKES.items():
        if not ctx.has(rec):
            continue
        eq = ctx.value(rec, 'deathPenaltyEquation')
        if eq != want_eq:
            out.append(_v(cid, 'P1', rec,
                          'a gameengine record the engine never loads was edited - '
                          'either the wrong record was fixed (in-game no-op) or the '
                          'ruled value was mirrored into a decoy',
                          'want %r, got %r' % (want_eq, eq)))
            continue
        mx = ctx.value(rec, 'deathPenaltyMax')
        try:
            mx_i = int(mx)
        except (TypeError, ValueError):
            mx_i = None
        if mx_i != VANILLA_MAX:
            out.append(_v(cid, 'P1', rec,
                          'a non-engine-loaded gameengine record had deathPenaltyMax '
                          'edited', 'want %d, got %r' % (VANILLA_MAX, mx)))
    return out


# --------------------------------------------------------------------------- #
# BAL-XPGAIN-1 - the death-penalty lane must not move XP gain or the curve
# --------------------------------------------------------------------------- #
def check_xp_gain_untouched(ctx):
    cid = 'BAL-XPGAIN-1'
    out = []
    if ctx.has(GAMEENGINE):
        got = ctx.value(GAMEENGINE, 'experienceEquation')
        if got != SV_EXPERIENCE_EQUATION:
            out.append(_v(cid, 'P1', GAMEENGINE,
                          'experienceEquation (XP GAIN) moved - out of scope for the '
                          'death-penalty ruling',
                          'want %r, got %r' % (SV_EXPERIENCE_EQUATION, got)))
    if ctx.has(PLAYERLEVELS):
        got = ctx.value(PLAYERLEVELS, 'experienceLevelEquation')
        if got != SV_LEVEL_EQUATION:
            out.append(_v(cid, 'P1', PLAYERLEVELS,
                          'the XP level curve moved - out of scope for the '
                          'death-penalty ruling',
                          'want %r, got %r' % (SV_LEVEL_EQUATION, got)))
        try:
            lvl = int(ctx.value(PLAYERLEVELS, 'maxPlayerLevel'))
        except (TypeError, ValueError):
            lvl = None
        if lvl != SV_MAX_PLAYER_LEVEL:
            out.append(_v(cid, 'P1', PLAYERLEVELS,
                          'maxPlayerLevel moved - out of scope for the death-penalty '
                          'ruling',
                          'want %d, got %r' % (SV_MAX_PLAYER_LEVEL, lvl)))
    return out


# --------------------------------------------------------------------------- #
# BAL-TOMBSTONE-1 - the R-109 multiplier is on the engine-loaded record
# --------------------------------------------------------------------------- #
def check_tombstone_multiplier(ctx):
    cid = 'BAL-TOMBSTONE-1'
    out = []
    if not ctx.has(GAMEENGINE):
        return []
    got = ctx.value(GAMEENGINE, REDEMPTION_FIELD)
    if got is None:
        out.append(_v(cid, 'P0', GAMEENGINE,
                      '%s is absent - the engine would fall back to its loader '
                      'default 0.5 and the death marker would return HALF the XP '
                      'the death penalty took' % REDEMPTION_FIELD,
                      'Game.dll VA 0x1019b8c3 pushes 0x3f000000 (0.5f) as the default'))
    else:
        try:
            mult = float(got)
        except (TypeError, ValueError):
            mult = None
        if mult is None or abs(mult - RULED_MULTIPLIER) > _TOL:
            out.append(_v(cid, 'P0', GAMEENGINE,
                          '%s is not the R-109 identity - the death marker no longer '
                          'returns what the death penalty took' % REDEMPTION_FIELD,
                          'want %.1f, got %r (%s)'
                          % (RULED_MULTIPLIER, got,
                             'free-XP loop' if (mult or 0) > RULED_MULTIPLIER
                             else 'punishes the player twice')))
        elif ctx.dtype(GAMEENGINE, REDEMPTION_FIELD) != DTYPE_FLOAT:
            out.append(_v(cid, 'P0', GAMEENGINE,
                          '%s dtype corrupted (must stay FLOAT)' % REDEMPTION_FIELD,
                          'dtype=%r want %r'
                          % (ctx.dtype(GAMEENGINE, REDEMPTION_FIELD), DTYPE_FLOAT)))

    for rec in DEAD_LOOKALIKES:
        if not ctx.has(rec):
            continue
        v = ctx.value(rec, REDEMPTION_FIELD)
        if v is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            fv = None
        if fv is None or abs(fv - VANILLA_MULTIPLIER) > _TOL:
            out.append(_v(cid, 'P1', rec,
                          'a gameengine record the engine never loads had %s edited - '
                          'either the wrong record was fixed (in-game no-op) or the '
                          'ruled value was mirrored into a decoy' % REDEMPTION_FIELD,
                          'want %.1f, got %r' % (VANILLA_MULTIPLIER, v)))

    if not ctx.has(GRAVESTONE):
        out.append(_v(cid, 'P0', GRAVESTONE,
                      'the ONE gravestone record is gone - without it there is no '
                      'death marker for the recovery to come from (RETIREMENT '
                      'PROTOCOL: this record is design law, not dead content)',
                      'Game.dll hard-codes Records/XPack/Item/Gravestones/'
                      'GravestoneGreece.dbr at 0x00344554'))
    else:
        cls = ctx.value(GRAVESTONE, 'Class')
        if str(cls) != GRAVESTONE_CLASS:
            out.append(_v(cid, 'P0', GRAVESTONE, 'the gravestone record was de-classed',
                          'want %r, got %r' % (GRAVESTONE_CLASS, cls)))
    return out


# --------------------------------------------------------------------------- #
# BAL-TOMBSTONE-2 - recovered == lost, re-derived from the SHIPPED penalty
# --------------------------------------------------------------------------- #
def check_tombstone_equality(ctx):
    cid = 'BAL-TOMBSTONE-2'
    if not ctx.has(GAMEENGINE):
        return []
    eq = ctx.value(GAMEENGINE, 'deathPenaltyEquation')
    div = _divisor_of(eq or '')
    mult = ctx.value(GAMEENGINE, REDEMPTION_FIELD)
    try:
        cap = int(ctx.value(GAMEENGINE, 'deathPenaltyMax'))
        floor = int(ctx.value(GAMEENGINE, 'deathPenaltyMin'))
        mult = float(mult)
    except (TypeError, ValueError):
        return [_v(cid, 'P0', GAMEENGINE,
                   'the penalty knobs or the recovery multiplier are unreadable, so '
                   'the R-109 equality cannot be re-derived',
                   'max=%r min=%r %s=%r'
                   % (ctx.value(GAMEENGINE, 'deathPenaltyMax'),
                      ctx.value(GAMEENGINE, 'deathPenaltyMin'),
                      REDEMPTION_FIELD, ctx.value(GAMEENGINE, REDEMPTION_FIELD)))]
    if div is None:
        return [_v(cid, 'P0', GAMEENGINE,
                   'deathPenaltyEquation no longer has the vanilla SHAPE, so the '
                   'recovery equality cannot be verified numerically', 'got %r' % (eq,))]
    if cap <= 0 or cap >= FLOAT32_EXACT_INT_BOUND:
        return [_v(cid, 'P0', GAMEENGINE,
                   'deathPenaltyMax is outside the range the engine round-trip can '
                   'return exactly, so recovery == loss is not provable',
                   'cap %d, must be 0 < cap < %d (float32 exact-integer bound)'
                   % (cap, FLOAT32_EXACT_INT_BOUND))]

    # The whole shipped domain, then the realised-loss domain (the engine hands the
    # grave the amount ACTUALLY removed, which the level floor can make smaller).
    for lvl in range(1, int(ctx.max_player_level) + 1):
        for dv in (0, 1, 2):
            lost = xp_lost_int(lvl, dv, div, cap, floor)
            back = xp_recoverable(lost, mult)
            if back != lost:
                return [_v(cid, 'P0', GAMEENGINE,
                           'the death marker does not return what the death penalty '
                           'took (%s)'
                           % ('FREE-XP LOOP' if back > lost
                              else 'the player is punished twice'),
                           'level %d difficulty DV=%d: lost %d XP, recovered %d XP '
                           '(multiplier %r, divisor %g, cap %d)'
                           % (lvl, dv, lost, back, mult, div, cap))]
    for u in (0, 1, 2, 3, 7, 999, 12345, 65535, 1 << 20, cap - 1, cap,
              FLOAT32_EXACT_INT_BOUND - 1):
        if u < 0:
            continue
        if xp_recoverable(u, mult) != u:
            return [_v(cid, 'P0', GAMEENGINE,
                       'the death marker does not return a realised loss exactly',
                       'realised loss %d XP -> recovered %d XP (multiplier %r)'
                       % (u, xp_recoverable(u, mult), mult))]
    return []


_CHECKS = [
    ('BAL-DEATHXP-1', check_deathxp_values),
    ('BAL-DEATHXP-2', check_deathxp_reduction),
    ('BAL-DEATHXP-3', check_dead_lookalikes),
    ('BAL-TOMBSTONE-1', check_tombstone_multiplier),
    ('BAL-TOMBSTONE-2', check_tombstone_equality),
    ('BAL-XPGAIN-1', check_xp_gain_untouched),
]


# --------------------------------------------------------------------------- #
# whitelist
# --------------------------------------------------------------------------- #
def _load_whitelist():
    wl = set()
    p = Path(__file__).resolve().parent / 'whitelist_balance.txt'
    if p.is_file():
        for line in p.read_text(encoding='utf-8', errors='replace').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            toks = line.split(None, 1)
            if len(toks) >= 2:
                wl.add((toks[0], _norm(toks[1].split('#', 1)[0])))
            else:
                wl.add((toks[0], None))
    return wl


# --------------------------------------------------------------------------- #
# public entry point
# --------------------------------------------------------------------------- #
def run(cfg):
    ctx = _build_context(cfg)
    wl = _load_whitelist()
    viols = []
    for _cid, fn in _CHECKS:
        for v in fn(ctx):
            key = (v['contract'], _norm(v['subject']))
            if key in wl or (v['contract'], None) in wl:
                continue
            viols.append(v)
    rank = {'P0': 0, 'P1': 1, 'P2': 2}
    viols.sort(key=lambda x: (rank.get(x['severity'], 9), x['contract'], x['subject']))
    return viols


def main(argv):
    if not argv:
        print('usage: contracts_balance.py <arz>', file=sys.stderr)
        return 2
    viols = run({'arz': argv[0]})
    for v in viols:
        print(json.dumps(v, ensure_ascii=False))
    n_block = sum(1 for v in viols if v['severity'] in ('P0', 'P1'))
    print('# %d violations (%d P0/P1, %d P2)'
          % (len(viols), n_block, len(viols) - n_block), file=sys.stderr)
    return 1 if n_block else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
