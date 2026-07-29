r"""tools/patches/death_xp_penalty.py - cut the on-death EXPERIENCE penalty by 90%.

WILL'S RULING (R-80, 2026-07-27, verbatim)
------------------------------------------
    "also i want to drastically reduce the xp penalty for dying. at high levels
     the penalty is way too crazy, it needs to be cut by like 90%"

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
The before-values are pure vanilla TQAE, untouched by every upstream and by our
own pipeline. Identical in: base TQAE database.arz, SV 0.98i, SV 0.9, SV 0.41,
and the deployed DEV arz (`1c27d5fa650b5c076696db4ad379672f`). No prior ruling in
docs/WILL_RULINGS.md touched death penalty or XP. No tool or registry module
wrote any `deathPenalty*` field before this one.

THE CHANGE (a uniform, exactly-90% cut)
---------------------------------------
    deathPenaltyEquation
      OLD  (currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)
      NEW  (currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)
    deathPenaltyMax
      OLD  500000        NEW  50000
    deathPenaltyMin
      OLD  0             NEW  0   (UNTOUCHED - 0 x 0.1 is still 0)

WHY A DIVISOR CHANGE AND NOT A NEW FACTOR: `9 -> 90` is exactly x0.1 while adding
no new token, operator or nesting to a string the engine's equation parser must
accept. The parser is a narrower code path than the item-equation evaluator (see
docs/MULTIPLAYER_COMPAT.md M1 - it rejects `/` in the SPAWN evaluator), so the
minimal-syntax edit is the safe one. It also keeps the difficulty term intact, so
Normal/Epic/Legendary keep their 1 : 4 : 7 relative weighting.

WHY THE CAP MOVES TOO: the penalty is cubic in level, so above L~86 on Legendary
the OLD equation exceeded `deathPenaltyMax` and every death cost a flat 500,000.
Scaling only the equation would have delivered less than the ruled 90% in exactly
the high-level regime Will complained about (L100 Legendary: 500,000 -> 77,778 is
only -84%). Scaling the cap in lockstep makes the reduction EXACTLY 90.0% at every
level on every difficulty, including the capped tail, and keeps the cap doing its
job (this mod ships `maxPlayerLevel = 1000`).

WHY UNIFORM RATHER THAN RESHAPED: Will asked for "cut by like 90%", and named high
levels as where it hurts. Because the penalty is cubic, a uniform x0.1 already
delivers by far the largest ABSOLUTE relief exactly there (L85 Legendary: -429,888
XP; L20 Legendary: -5,600 XP) while staying literally faithful to the number he
gave and leaving the curve's shape - the thing the base game tuned - untouched.

SCOPE: two fields on one record. No other balance value moves. `experienceEquation`
(XP GAIN), the XP curve `records\creature\pc\playerlevels.dbr`, and all five dead
lookalikes are explicitly left alone and re-asserted byte-equal in verify().

MULTIPLAYER: this is a DATABASE record, so it is shared - every player must ship
the identical arz (docs/MULTIPLAYER_COMPAT.md "Determinism statement"). It carries
no `/`-in-spawn-equation hazard (M1 applies to proxy spawn equations only) and no
party-size term, so co-op behaves exactly like single-player at the new rate.

CONTRACT (tools/patches/README.md): MODULE_NAME + apply(db, tags) + the optional
verify(db, tags) hook, which re-asserts on the FINAL merged arz after the whole
gate battery.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

MODULE_NAME = 'Death XP penalty -90% (R-80)'

# The ONE record the TQAE engine loads for the death penalty.
GAMEENGINE = r'records\xpack\game\gameengine.dbr'

# Exact before/after values. The strings are byte-exact including Iron Lore's
# original spacing ("(1+ (3 *"); only the divisor token changes.
EQ_OLD = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)'
EQ_NEW = '(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)'
MAX_OLD = 500000
MAX_NEW = 50000
MIN_EXPECTED = 0

REDUCTION = 0.10          # the ruled multiplier: keep 10% of the old loss
_TOL = 1e-9

# The five deathPenalty-bearing records the engine never loads. verify() proves
# we did not shotgun them (and that nobody "helpfully" mirrors the edit here,
# which would make a future reader think one of them is live).
DEAD_LOOKALIKES = {
    r'records\xpack\game\drxgameengine.dbr':      (EQ_OLD, MAX_OLD, MIN_EXPECTED),
    r'records\xpack\game\copy of gameengine.dbr': (EQ_OLD, MAX_OLD, MIN_EXPECTED),
    r'records\xpack\game\xxxgameengine.dbr':      (EQ_OLD, MAX_OLD, MIN_EXPECTED),
    r'records\game\gameengine.dbr':               (EQ_OLD, MAX_OLD, MIN_EXPECTED),
    r'records\game\cost backup\gameengine.dbr':
        ('(currentPlayerLevel^2.95) * ((1+ (2 * gameDifficultyDV)) / 3)',
         MAX_OLD, MIN_EXPECTED),
}

# Fields on the live record that must NOT move (the "only the death penalty
# changed" proof, checked field-by-field inside apply()).
_PROTECTED_SAMPLE = ('experienceEquation', 'transferCostEquation')


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

    # Idempotence: a second run over an already-patched db is a clean no-op.
    already = (eq == EQ_NEW and int(mx) == MAX_NEW)
    if not already and (eq != EQ_OLD or int(mx) != MAX_OLD):
        raise SystemExit(
            'death_xp_penalty: unexpected pre-state on %s - deathPenaltyEquation=%r '
            'deathPenaltyMax=%r. Expected the vanilla pair (%r / %d) or the already-'
            'ruled pair (%r / %d). Another writer moved this field: resolve the '
            'ordering before shipping (last-writer-wins).'
            % (GAMEENGINE, eq, mx, EQ_OLD, MAX_OLD, EQ_NEW, MAX_NEW))
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
    expected_moved = ['deathPenaltyEquation', 'deathPenaltyMax']
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

    # --- scope proof C: every dead lookalike still carries its own value ---
    for rec, (want_eq, want_max, want_min) in DEAD_LOOKALIKES.items():
        if not db.has_record(rec):
            continue
        got = (db.get_field_value(rec, 'deathPenaltyEquation'),
               int(db.get_field_value(rec, 'deathPenaltyMax')),
               int(db.get_field_value(rec, 'deathPenaltyMin')))
        if got != (want_eq, want_max, want_min):
            raise SystemExit(
                'death_xp_penalty: dead lookalike %s was modified (%r) - only the '
                'engine-loaded xpack record may change' % (rec, got))

    old85 = penalty(85, 2, 9, MAX_OLD)
    new85 = penalty(85, 2, 90, MAX_NEW)
    print('    death_xp_penalty: %s -> divisor 9->90, cap %d->%d '
          '(L85 Legendary %.0f -> %.0f XP, -%.1f%%)'
          % ('ALREADY RULED (no-op)' if already else 'applied',
             MAX_OLD, MAX_NEW, old85, new85, 100.0 * (1.0 - new85 / old85)))


def verify(db, tags):
    """Post-finalization guard: re-assert the ruled death-XP penalty on the FINAL
    merged arz, prove the reduction is exactly 90% across the whole level x
    difficulty domain, and prove nothing else in the XP economy moved."""
    eq = db.get_field_value(GAMEENGINE, 'deathPenaltyEquation')
    mx = db.get_field_value(GAMEENGINE, 'deathPenaltyMax')
    mn = db.get_field_value(GAMEENGINE, 'deathPenaltyMin')
    if eq != EQ_NEW:
        raise SystemExit(
            'death_xp_penalty verify: deathPenaltyEquation is %r, expected %r - a '
            'later phase clobbered the R-80 ruling.' % (eq, EQ_NEW))
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

    # The ruled reduction, re-derived numerically over the shipped level cap.
    worst = 0.0
    for lvl in range(1, 1001):
        for dv in (0, 1, 2):
            o = penalty(lvl, dv, 9, MAX_OLD)
            n = penalty(lvl, dv, 90, MAX_NEW)
            if o <= 0:
                continue
            worst = max(worst, abs((n / o) - REDUCTION))
    if worst > 1e-9:
        raise SystemExit(
            'death_xp_penalty verify: reduction is not a uniform %.0f%% cut '
            '(worst ratio deviation %.3g)' % (100 * (1 - REDUCTION), worst))

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
          'divisor 90 + deathPenaltyMax 50000 + deathPenaltyMin 0 (dtypes STR/INT '
          'intact); reduction is a uniform -90.0%% over L1-1000 x N/E/L; all 5 dead '
          'gameengine lookalikes byte-equal to their vanilla values.')
