r"""tools/patches/death_xp_penalty.py - cut the on-death EXPERIENCE penalty to 5%
of vanilla (R-80 took it to 10%; R-251 halved that again).

WILL'S RULINGS (verbatim)
-------------------------
R-80, 2026-07-27:
    "also i want to drastically reduce the xp penalty for dying. at high levels
     the penalty is way too crazy, it needs to be cut by like 90%"

R-251, 2026-08-14 (BL-W0814-4) - the CURRENT ruling, it retunes R-80's number and
leaves R-80's mechanism, scope and reasoning standing:
    "lets reduce the penalty for dying by another 50% from what it currently is
     at."

"Another 50% from what it currently is at" is applied to the SHIPPED (R-80) state,
not to vanilla: divisor 90 -> 180, cap 50,000 -> 25,000. The result is a uniform
x0.05 of vanilla instead of x0.10, i.e. exactly half the loss build92 shipped, at
every level on every difficulty.

THE MECHANISM (found in the DEPLOYED bytes, not assumed)
--------------------------------------------------------
TQAE's on-death XP loss is ONE knob-set on ONE record. `Game.dll` hard-codes
exactly one GameEngine path - the ASCII literal `Records/XPack/Game/GameEngine.dbr`
is the ONLY `*GameEngine.dbr` string in any shipped binary (TQ.exe / Game.dll /
Editor.exe) - and reads three fields off it, whose names appear verbatim in
Game.dll's string table next to the loader's error message
`-=- GameEngine Equation load failure : deathPenaltyEquation`:

    deathPenaltyEquation   (STR)  the XP-loss formula, evaluated on death
    deathPenaltyMin        (INT)  lower clamp
    deathPenaltyMax        (INT)  upper clamp

Equation variables the engine binds (also verbatim in Game.dll): `currentPlayerLevel`,
`gameDifficultyDV` (0 Normal / 1 Epic / 2 Legendary), plus `averagePlayerLevel` /
`averagePartyLevel` for the XP-GAIN equation. There is NO separate flat-vs-percentage
knob and NO per-difficulty variant record: difficulty enters through the single
`gameDifficultyDV` term inside the one equation. So this module has exactly one
lever, and it is difficulty-aware by construction.

FIVE LOOKALIKES, ALL DEAD. Six records in the shipped arz carry `deathPenalty*`
fields; only the xpack one is loaded:

    records\xpack\game\gameengine.dbr        <- LIVE (the Game.dll literal)
    records\xpack\game\drxgameengine.dbr         dead (DRX authoring copy)
    records\xpack\game\copy of gameengine.dbr    dead (Iron Lore working copy)
    records\xpack\game\xxxgameengine.dbr         dead (Iron Lore working copy)
    records\game\gameengine.dbr                  dead (pre-Immortal-Throne path)
    records\game\cost backup\gameengine.dbr      dead (Iron Lore backup; note it
                                                 even carries a DIFFERENT formula,
                                                 `^2.95 * (1+2*DV)/3` - a decoy that
                                                 would have been the wrong target)

Independent corroboration that the xpack record is the live one: `damage_display`
(build38, shipped) fixed the missing floating-combat-text FontStyles by writing
this same record, and base TQAE keeps those style fields ONLY here while vanilla
demonstrably renders damage numbers. `records\game\gameengine.dbr` does not even
contain them.

PROVENANCE
----------
The vanilla values are pure TQAE, untouched by every upstream and by our own
pipeline before b93. Identical in: base TQAE database.arz, SV 0.98i, SV 0.9,
SV 0.41. b93 (R-80) moved them to the 90 / 50,000 pair that shipped through
build92; R-251 moves that pair on again. No tool or registry module other than
this one writes any `deathPenalty*` field.

THE CHANGE (a uniform, exactly-95%-of-vanilla cut)
--------------------------------------------------
    deathPenaltyEquation
      VANILLA  (currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)
      R-80     (currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)
      R-251    (currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 180)
    deathPenaltyMax
      VANILLA  500000     R-80  50000      R-251  25000
    deathPenaltyMin
      VANILLA  0          R-80  0          R-251  0   (UNTOUCHED - 0 x k is still 0)

WHY A DIVISOR CHANGE AND NOT A NEW FACTOR: `90 -> 180` is exactly x0.5 while
adding no new token, operator or nesting to a string the engine's equation parser
must accept. The parser is a narrower code path than the item-equation evaluator
(see docs/MULTIPLAYER_COMPAT.md M1 - it rejects `/` in the SPAWN evaluator), so the
minimal-syntax edit is the safe one. It also keeps the difficulty term intact, so
Normal/Epic/Legendary keep their 1 : 4 : 7 relative weighting.

WHY THE CAP MOVES TOO: the penalty is cubic in level, so the cap bites at the top
of the range (this mod ships `maxPlayerLevel = 1000`). Halving the equation while
leaving the cap at 50,000 would deliver LESS than the ruled half in exactly the
capped tail - the regime R-80 was opened about. Scaling the cap in lockstep makes
the reduction EXACTLY 50% of the shipped penalty (and exactly 95% off vanilla) at
every level on every difficulty, and keeps the cap doing its job.

WHY UNIFORM RATHER THAN RESHAPED: Will asked for "another 50% from what it
currently is at" - a scalar on the current state. A uniform x0.5 is the literal
reading, it leaves the curve's shape (the thing the base game tuned) untouched,
and because the penalty is cubic it still delivers by far the largest ABSOLUTE
relief at high level, which is where R-80 said the pain is.

R-109 COUPLING - THE TOMBSTONE RECOVERY FOLLOWS AUTOMATICALLY
-------------------------------------------------------------
R-109 [2026-07-30], verbatim: "lets make the tombstone xp recovery match the xp
lost upon dying" - an INVARIANT, not a number ("Implement the equality; do not
hardcode 10%"). It is implemented in the sibling module
`tools/patches/tombstone_xp_recovery.py` as `RedemptionMultiplier = 1.0` on THIS
SAME record, because Game.dll computes

    recovered = trunc( (float)(XP ACTUALLY LOST ON DEATH) * RedemptionMultiplier )

(`GetPlayerExperienceRedemptionAmount` VA 0x10194f60 reads the realised loss that
`RegisterExperienceLoss` VA 0x10194540 stored at `GraveInfo+0x0C`). The marker
never reads `deathPenalty*` at all, so retuning the penalty - which is exactly
what R-251 does - carries the recovery with it with NO edit on the recovery side.
That self-correcting property is the reason R-109 was built this way, and this
lane is its first live exercise. It is not asserted: `tombstone_xp_recovery.
verify()` re-derives `recovered == lost` numerically against the LIVE penalty
knobs it reads off the db, and its `--negtest` plant 6 halves the shipped divisor
again and requires the equality to hold with no edit on the recovery side.

SCOPE: two fields on one record. No other balance value moves. `experienceEquation`
(XP GAIN), the XP curve `records\creature\pc\playerlevels.dbr`, and all five dead
lookalikes are explicitly left alone and re-asserted byte-equal in verify().

MULTIPLAYER: this is a DATABASE record, so it is shared - every player must ship
the identical arz (docs/MULTIPLAYER_COMPAT.md "Determinism statement"). It carries
no `/`-in-spawn-equation hazard (M1 applies to proxy spawn equations only) and no
party-size term, so co-op behaves exactly like single-player at the new rate.

CONTRACT (tools/patches/README.md): MODULE_NAME + apply(db, tags) + the optional
verify(db, tags) hook, which re-asserts on the FINAL merged arz after the whole
gate battery. Permanent artifact-level cover: tools/contracts/contracts_balance.py
(BAL-DEATHXP-1/2/3, BAL-TOMBSTONE-1/2, BAL-XPGAIN-1). Planted negatives for this
module's own gate: `py tools/patches/death_xp_penalty.py --negtest <arz>`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

MODULE_NAME = 'Death XP penalty -95% of vanilla (R-80 + R-251)'

# The ONE record the TQAE engine loads for the death penalty.
GAMEENGINE = r'records\xpack\game\gameengine.dbr'

# The equation SHAPE. Iron Lore's original spacing ("(1+ (3 *") is byte-exact and
# the divisor token is the ONLY thing that ever changes - that is the whole point
# of the edit, so every equation below is built from this one template rather
# than retyped (a retyped string is how a retune ships a shape regression).
EQ_SHAPE = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / %d)'

# The three divisor/cap pairs this module knows about. VANILLA is what upstream
# ships; R80 is the pair build92 shipped and is kept as a NAMED, recognised
# pre-state (see apply()); NEW is the ruled state R-251 writes.
DIV_VANILLA, MAX_VANILLA = 9, 500000
DIV_R80, MAX_R80 = 90, 50000            # SUPERSEDED by R-251, still a legal input
DIV_NEW, MAX_NEW = 180, 25000           # R-251: "another 50%" on the R-80 pair
MIN_EXPECTED = 0

EQ_OLD = EQ_SHAPE % DIV_VANILLA         # kept under its historical name
EQ_R80 = EQ_SHAPE % DIV_R80
EQ_NEW = EQ_SHAPE % DIV_NEW
MAX_OLD = MAX_VANILLA                   # ditto

# The ruled multiplier: how much of the VANILLA loss survives. Derived, never
# retyped, so the divisor and the cap can never disagree with the headline number.
REDUCTION = float(DIV_VANILLA) / float(DIV_NEW)          # 0.05
# ...and how much of the PREVIOUSLY SHIPPED (R-80) loss survives. This is the
# number Will actually named: "another 50%".
REDUCTION_VS_R80 = float(DIV_R80) / float(DIV_NEW)       # 0.5
_TOL = 1e-9

# The five deathPenalty-bearing records the engine never loads. verify() proves
# we did not shotgun them (and that nobody "helpfully" mirrors the edit here,
# which would make a future reader think one of them is live).
DEAD_LOOKALIKES = {
    r'records\xpack\game\drxgameengine.dbr':      (EQ_OLD, MAX_VANILLA, MIN_EXPECTED),
    r'records\xpack\game\copy of gameengine.dbr': (EQ_OLD, MAX_VANILLA, MIN_EXPECTED),
    r'records\xpack\game\xxxgameengine.dbr':      (EQ_OLD, MAX_VANILLA, MIN_EXPECTED),
    r'records\game\gameengine.dbr':               (EQ_OLD, MAX_VANILLA, MIN_EXPECTED),
    r'records\game\cost backup\gameengine.dbr':
        ('(currentPlayerLevel^2.95) * ((1+ (2 * gameDifficultyDV)) / 3)',
         MAX_VANILLA, MIN_EXPECTED),
}

# Fields on the live record that must NOT move (the "only the death penalty
# changed" proof, checked field-by-field inside apply()).
_PROTECTED_SAMPLE = ('experienceEquation', 'transferCostEquation')

# Every (equation, cap) pre-state apply() may legally see, newest first. Anything
# else means another writer moved the field and the ordering must be resolved
# before shipping. The SUPERSEDED R-80 pair is listed deliberately: every arz
# already on disk carries it, and re-running the retune over one of those (the
# --negtest / --table paths, and any incremental rebuild) must not fail loud.
KNOWN_PRE_STATES = (
    ('the R-251 ruled pair (already applied)', EQ_NEW, MAX_NEW),
    ('the superseded R-80 pair (build92)',     EQ_R80, MAX_R80),
    ('vanilla TQAE',                           EQ_OLD, MAX_VANILLA),
)


def divisor_of(equation):
    """Pull the trailing '/ <n>)' divisor out of an equation of the ruled SHAPE.
    Returns None when the equation is not that shape (callers then report the
    shape mismatch rather than a number)."""
    head, tail = EQ_SHAPE.split('%d')
    if not (isinstance(equation, str)
            and equation.startswith(head) and equation.endswith(tail)):
        return None
    try:
        return float(equation[len(head):len(equation) - len(tail)])
    except ValueError:
        return None


def _check_constants():
    """Fail loud at IMPORT if the ruled constants ever stop agreeing with each
    other. THE defect class of a retune lane: someone halves the divisor and
    forgets the cap (or the headline fraction), and every downstream message then
    states a cut the build does not deliver."""
    if DIV_NEW != DIV_R80 * 2 or MAX_NEW != MAX_R80 // 2:
        raise SystemExit(
            'death_xp_penalty: R-251 is "another 50%%" on the R-80 pair, so the '
            'constants must be divisor %d and cap %d; got %d / %d.'
            % (DIV_R80 * 2, MAX_R80 // 2, DIV_NEW, MAX_NEW))
    if abs(MAX_NEW - REDUCTION * MAX_VANILLA) > _TOL * MAX_VANILLA:
        raise SystemExit(
            'death_xp_penalty: the cap and the equation disagree - cap %d is not '
            '%.4f x the vanilla cap %d. Scale BOTH or the cut stops being uniform '
            'in the capped tail.' % (MAX_NEW, REDUCTION, MAX_VANILLA))
    for name, eq, _cap in KNOWN_PRE_STATES:
        if divisor_of(eq) is None:
            raise SystemExit('death_xp_penalty: %s has an unparseable equation %r'
                             % (name, eq))


_check_constants()


def _dtype_of(db, rec, field):
    fields = db.get_fields(rec)
    if not fields:
        return None
    for key, tf in fields.items():
        if key == field or key.split('###')[0] == field:
            return tf.dtype
    return None


def penalty(level, difficulty_dv, equation_divisor, cap):
    """Reproduce the engine's clamp(equation, min, max) for the worked example
    and for the contract's numeric cross-check."""
    raw = (float(level) ** 3) * ((1.0 + (3.0 * difficulty_dv)) / float(equation_divisor))
    return min(max(raw, MIN_EXPECTED), float(cap))


def apply(db, tags):
    if not db.has_record(GAMEENGINE):
        raise SystemExit(
            'death_xp_penalty: %s absent from db - the engine-loaded GameEngine '
            'record is gone (build base changed?)' % GAMEENGINE)

    eq = db.get_field_value(GAMEENGINE, 'deathPenaltyEquation')
    mx = db.get_field_value(GAMEENGINE, 'deathPenaltyMax')
    mn = db.get_field_value(GAMEENGINE, 'deathPenaltyMin')

    seen = [(nm, want_eq, want_mx) for nm, want_eq, want_mx in KNOWN_PRE_STATES
            if eq == want_eq and int(mx) == want_mx]
    if not seen:
        raise SystemExit(
            'death_xp_penalty: unexpected pre-state on %s - deathPenaltyEquation=%r '
            'deathPenaltyMax=%r. Expected one of: %s. Another writer moved this '
            'field: resolve the ordering before shipping (last-writer-wins).'
            % (GAMEENGINE, eq, mx,
               '; '.join('%s (%r / %d)' % (nm, e, c) for nm, e, c in KNOWN_PRE_STATES)))
    already = (eq == EQ_NEW and int(mx) == MAX_NEW)
    if int(mn) != MIN_EXPECTED:
        raise SystemExit(
            'death_xp_penalty: deathPenaltyMin is %r, expected %d - the clamp floor '
            'moved, re-derive the reduction before shipping.' % (mn, MIN_EXPECTED))

    # dtypes BEFORE (the CLAUDE.md dtype-corruption law: never let a write flip
    # STR<->INT<->FLOAT). We re-assert these after writing.
    dt_eq = _dtype_of(db, GAMEENGINE, 'deathPenaltyEquation')
    dt_mx = _dtype_of(db, GAMEENGINE, 'deathPenaltyMax')

    # Snapshot every other field on this record + the modified-set, for the
    # scope proof below.
    before_fields = {
        k: list(v.values) for k, v in db.get_fields(GAMEENGINE).items()
    }
    modified_before = set(db._modified)

    # What SHOULD move, derived from the pre-state actually observed - so the
    # idempotent no-op path expects NOTHING to move and is genuinely checked
    # (the old fixed expectation made a second run raise its own scope error).
    expected_moved = sorted(f for f, old, new in
                            (('deathPenaltyEquation', eq, EQ_NEW),
                             ('deathPenaltyMax', int(mx), MAX_NEW)) if old != new)

    # No explicit dtype: set_field keeps the EXISTING TypedField's dtype when the
    # field already exists (both do), so STR stays STR and INT stays INT.
    db.set_field(GAMEENGINE, 'deathPenaltyEquation', EQ_NEW)
    db.set_field(GAMEENGINE, 'deathPenaltyMax', MAX_NEW)

    # --- dtype preservation proof ---
    for field, want in (('deathPenaltyEquation', dt_eq), ('deathPenaltyMax', dt_mx)):
        got = _dtype_of(db, GAMEENGINE, field)
        if got != want:
            raise SystemExit(
                'death_xp_penalty: dtype corruption on %s.%s (%r -> %r)'
                % (GAMEENGINE, field, want, got))

    # --- scope proof A: nothing else on this record moved ---
    after_fields = {
        k: list(v.values) for k, v in db.get_fields(GAMEENGINE).items()
    }
    if set(before_fields) != set(after_fields):
        raise SystemExit('death_xp_penalty: field set changed on %s' % GAMEENGINE)
    moved = sorted(k for k in before_fields if before_fields[k] != after_fields[k])
    if moved != expected_moved:
        raise SystemExit(
            'death_xp_penalty: expected exactly %r to move on %s, got %r'
            % (expected_moved, GAMEENGINE, moved))
    for f in _PROTECTED_SAMPLE:
        if f in before_fields and before_fields[f] != after_fields[f]:
            raise SystemExit(
                'death_xp_penalty: protected field %s moved on %s' % (f, GAMEENGINE))

    # --- scope proof B: this module dirtied no record but the one ---
    newly = set(db._modified) - modified_before
    if newly - {GAMEENGINE}:
        raise SystemExit(
            'death_xp_penalty: touched unexpected record(s): %s'
            % ', '.join(sorted(newly - {GAMEENGINE})))

    # Report the transition WE ACTUALLY MADE, off the pre-state we actually
    # observed - not a fixed vanilla->ruled headline. Re-running over an arz that
    # already carries the R-80 pair moves 90->180, and saying "9->180" there would
    # describe an edit this run did not perform.
    pre_name, pre_eq, pre_max = seen[0]
    pre_div = int(divisor_of(pre_eq))
    van85 = penalty(85, 2, DIV_VANILLA, MAX_VANILLA)
    r80_85 = penalty(85, 2, DIV_R80, MAX_R80)
    new85 = penalty(85, 2, DIV_NEW, MAX_NEW)
    print('    death_xp_penalty: %s (pre-state: %s) -> divisor %d->%d, cap %d->%d '
          '(L85 Legendary %.0f -> %.0f XP, -%.1f%% of vanilla; -%.1f%% of the '
          'build92 %.0f)'
          % ('ALREADY RULED (no-op)' if already else 'applied', pre_name,
             pre_div, DIV_NEW, pre_max, MAX_NEW, van85, new85,
             100.0 * (1.0 - new85 / van85),
             100.0 * (1.0 - REDUCTION_VS_R80), r80_85))


def verify(db, tags):
    """Post-finalization guard: re-assert the ruled death-XP penalty on the FINAL
    merged arz, prove the reduction is exactly the ruled fraction across the whole
    level x difficulty domain, and prove nothing else in the XP economy moved."""
    eq = db.get_field_value(GAMEENGINE, 'deathPenaltyEquation')
    mx = db.get_field_value(GAMEENGINE, 'deathPenaltyMax')
    mn = db.get_field_value(GAMEENGINE, 'deathPenaltyMin')
    if eq != EQ_NEW:
        raise SystemExit(
            'death_xp_penalty verify: deathPenaltyEquation is %r, expected %r - a '
            'later phase clobbered the R-80/R-251 ruling.' % (eq, EQ_NEW))
    if int(mx) != MAX_NEW:
        raise SystemExit(
            'death_xp_penalty verify: deathPenaltyMax is %r, expected %d.'
            % (mx, MAX_NEW))
    if int(mn) != MIN_EXPECTED:
        raise SystemExit(
            'death_xp_penalty verify: deathPenaltyMin is %r, expected %d.'
            % (mn, MIN_EXPECTED))
    if _dtype_of(db, GAMEENGINE, 'deathPenaltyEquation') != 2:
        raise SystemExit('death_xp_penalty verify: deathPenaltyEquation is not STR.')
    if _dtype_of(db, GAMEENGINE, 'deathPenaltyMax') != 0:
        raise SystemExit('death_xp_penalty verify: deathPenaltyMax is not INT.')

    # The ruled reduction, re-derived numerically over the shipped level cap,
    # against BOTH baselines: vanilla (the R-80 headline) and the build92 pair
    # (the R-251 headline, "another 50%"). Both come off the constants, so a
    # future retune that edits one constant and not the others reds here.
    worst_v = worst_r80 = 0.0
    for lvl in range(1, 1001):
        for dv in (0, 1, 2):
            van = penalty(lvl, dv, DIV_VANILLA, MAX_VANILLA)
            r80 = penalty(lvl, dv, DIV_R80, MAX_R80)
            new = penalty(lvl, dv, DIV_NEW, MAX_NEW)
            if van > 0:
                worst_v = max(worst_v, abs((new / van) - REDUCTION))
            if r80 > 0:
                worst_r80 = max(worst_r80, abs((new / r80) - REDUCTION_VS_R80))
    if worst_v > _TOL:
        raise SystemExit(
            'death_xp_penalty verify: reduction is not a uniform %.0f%% cut of '
            'vanilla (worst ratio deviation %.3g)' % (100 * (1 - REDUCTION), worst_v))
    if worst_r80 > _TOL:
        raise SystemExit(
            'death_xp_penalty verify: R-251 is not a uniform %.0f%% cut of the '
            'build92 penalty (worst ratio deviation %.3g)'
            % (100 * (1 - REDUCTION_VS_R80), worst_r80))

    # Nothing else in the XP economy moved.
    for rec, (want_eq, want_max, want_min) in DEAD_LOOKALIKES.items():
        if not db.has_record(rec):
            continue
        got = (db.get_field_value(rec, 'deathPenaltyEquation'),
               int(db.get_field_value(rec, 'deathPenaltyMax')),
               int(db.get_field_value(rec, 'deathPenaltyMin')))
        if got != (want_eq, want_max, want_min):
            raise SystemExit(
                'death_xp_penalty verify: dead lookalike %s changed (%r)' % (rec, got))

    print('  death_xp_penalty.verify OK: xpack gameengine deathPenaltyEquation '
          'divisor %d + deathPenaltyMax %d + deathPenaltyMin %d (dtypes STR/INT '
          'intact); reduction is a uniform -%.1f%% vs vanilla and -%.1f%% vs the '
          'build92 penalty over L1-1000 x N/E/L; all %d dead gameengine lookalikes '
          'byte-equal to their vanilla values.'
          % (DIV_NEW, MAX_NEW, MIN_EXPECTED, 100 * (1 - REDUCTION),
             100 * (1 - REDUCTION_VS_R80), len(DEAD_LOOKALIKES)))


# ── CLI: the planted negative tests for this module's own gate ──────────────
def _load(arz):
    from arz_patcher import ArzDatabase
    return ArzDatabase.from_arz(Path(arz))


def _negtest(arz):
    """Prove verify() is not vacuous: plant every regression this retune can
    ship and require the gate to RED, with the ruled state as the control."""
    db = _load(arz)
    apply(db, {})

    results = []

    def check(label, expect_fail, mutate, restore):
        mutate()
        try:
            verify(db, {})
            failed = False
        except SystemExit:
            failed = True
        restore()
        results.append((label, expect_fail, failed, failed == expect_fail))

    good_eq = db.get_field_value(GAMEENGINE, 'deathPenaltyEquation')
    good_mx = int(db.get_field_value(GAMEENGINE, 'deathPenaltyMax'))
    good_mn = int(db.get_field_value(GAMEENGINE, 'deathPenaltyMin'))

    def set_eq(v):
        db.set_field(GAMEENGINE, 'deathPenaltyEquation', v)

    def set_mx(v):
        db.set_field(GAMEENGINE, 'deathPenaltyMax', v)

    # CONTROL: the ruled state passes.
    check('control - the R-251 ruled state passes', False, lambda: None, lambda: None)

    # PLANT 1: the whole ruling reverted to Iron Lore's vanilla divisor.
    check('equation reverted to vanilla "/ %d" rejected' % DIV_VANILLA, True,
          lambda: set_eq(EQ_OLD), lambda: set_eq(good_eq))

    # PLANT 2 (THIS LANE'S OWN DEFECT CLASS): the halving silently did not land -
    # the record still carries the SUPERSEDED build92 pair.
    check('superseded R-80 pair (divisor %d / cap %d) rejected' % (DIV_R80, MAX_R80),
          True,
          lambda: (set_eq(EQ_R80), set_mx(MAX_R80)),
          lambda: (set_eq(good_eq), set_mx(good_mx)))

    # PLANT 3 (THE HALF-FIX): equation halved, cap forgotten. Passes an eyeball
    # and under-delivers in exactly the capped high-level tail.
    check('equation halved but cap left at %d rejected' % MAX_R80, True,
          lambda: set_mx(MAX_R80), lambda: set_mx(good_mx))

    # PLANT 4: cap put back to vanilla.
    check('cap reverted to vanilla %d rejected' % MAX_VANILLA, True,
          lambda: set_mx(MAX_VANILLA), lambda: set_mx(good_mx))

    # PLANT 5: an over-cut (someone halves twice).
    check('over-cut (divisor %d / cap %d) rejected' % (DIV_NEW * 2, MAX_NEW // 2), True,
          lambda: (set_eq(EQ_SHAPE % (DIV_NEW * 2)), set_mx(MAX_NEW // 2)),
          lambda: (set_eq(good_eq), set_mx(good_mx)))

    # PLANT 6: the clamp floor lifted off 0.
    check('deathPenaltyMin lifted off %d rejected' % MIN_EXPECTED, True,
          lambda: db.set_field(GAMEENGINE, 'deathPenaltyMin', 5000),
          lambda: db.set_field(GAMEENGINE, 'deathPenaltyMin', good_mn))

    # PLANT 7: the wrong-record fix - a dead lookalike carrying the ruled value.
    live = [r for r in DEAD_LOOKALIKES if db.has_record(r)]
    if live:
        la = live[0]
        prev = db.get_field_value(la, 'deathPenaltyEquation')
        check('dead lookalike shotgunned (%s) rejected' % la.split('\\')[-1], True,
              lambda: db.set_field(la, 'deathPenaltyEquation', EQ_NEW),
              lambda: db.set_field(la, 'deathPenaltyEquation', prev))
    else:
        results.append(('dead lookalike plant', True, False, False))

    print('\ndeath_xp_penalty _negtest:')
    for label, expect_fail, failed, ok in results:
        print('  [%s] %-62s expected=%s got=%s'
              % ('PASS' if ok else 'FAIL', label,
                 'REJECT' if expect_fail else 'ACCEPT',
                 'REJECT' if failed else 'ACCEPT'))
    allok = all(o for _l, _e, _f, o in results)
    print('  -> %s (%d/%d)' % ('PASS' if allok else 'FAIL',
                               sum(1 for _l, _e, _f, o in results if o), len(results)))
    return 0 if allok else 1


if __name__ == '__main__':
    args = sys.argv[1:]
    DEFAULT_ARZ = (Path(__file__).resolve().parents[2]
                   / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    if '--negtest' in args:
        i = args.index('--negtest')
        raise SystemExit(_negtest(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ))
    print(__doc__)
