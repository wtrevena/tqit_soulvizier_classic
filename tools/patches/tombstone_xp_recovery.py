r"""tools/patches/tombstone_xp_recovery.py - the death marker gives back EXACTLY
what the death penalty took (R-109).

WILL'S RULING (docs/WILL_RULINGS.md R-109, 2026-07-30) - two steps, the second
supersedes the first and IS the ruling:

    "one thing we need to check is when you go find your tombstone after you die,
     you should only get 10% of the original xp that is awarded since we cut the
     death penalty"

    "lets make the tombstone xp recovery match the xp lost upon dying"

R-109: "THE RULING IS THE INVARIANT, NOT THE NUMBER: XP recovered from the death
marker == XP lost to the death penalty, exactly, on every difficulty. Implement
the equality; do not hardcode 10%."

================================================================================
1. THE MECHANISM, READ OUT OF THE SHIPPED BYTES (nothing here is assumed)
================================================================================
The whole death/recovery loop is FOUR exported `Game.dll` symbols and ONE DB
field. Every address below is from the stock 32-bit `Game.dll`
(`C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\
Game.dll`, image base 0x10000000), resolved through the PE export directory, and
is reproducible with `py tools/debug/probe_tombstone_xp.py --disasm`.

  (a) `?CharacterIsDying@Player@GAME@@UAEXXZ`            VA 0x10207fc0
      the on-death handler.

  (b) `?GetPlayerDeathExperiencePenalty@GameEngine@GAME@@QBEIPAVPlayer@2@I@Z`
                                                          VA 0x101945a0
      evaluates the GameEngine equation object at GE+0x103C
      (`deathPenaltyEquation`), floors the raw result at 0.0
      (`comiss xmm0,xmm1 / ja / movaps xmm0,xmm1`), rounds it, and clamps it
      between GE+0x1064 (`deathPenaltyMin`) and GE+0x1068 (`deathPenaltyMax`)
      with `cmovg`/`cmovl`. This is exactly the model `death_xp_penalty.penalty()`
      already reproduces in Python.

  (c) an XP-subtraction helper on the player's level object at Player+0xC2C,
      VA 0x1017d620 (not exported; named by its call site). MEASURED: it takes the
      nominal penalty, computes `new = max(total_at_+0x34 - penalty, FLOOR)`,
      writes `new` back to +0x34 and RETURNS `old - new`, i.e. **the amount
      ACTUALLY REMOVED**, clamped at 0 by `cmovs`. FLOOR comes from VA 0x1017d540,
      which evaluates an equation object and rounds it the same way (`+0.5` from
      0x103a3348, `fistp` with RC=11) for the index
      `min(max([+0x30] - 1, 0), [+0x2c])`.
      INTERPRETATION (consistent with TQ's known behaviour, but the binary carries
      no field names for these offsets): that index is the level below the current
      one and the equation is the XP table, so the floor is the current level's own
      XP threshold and a death cannot de-level you. **Nothing in this module
      depends on that reading** - all it needs is the measured part, that the value
      handed to the grave is the REALISED loss and is therefore <= the nominal
      penalty. `CharacterIsDying` separately does `sub dword ptr [esi+0xcf0], edi`
      with the nominal penalty for its own mirrored counter.

  (d) `?RegisterExperienceLoss@GameEngine@GAME@@QAEXIH@Z` VA 0x10194540
      stores that ACTUALLY-REMOVED amount into the player's grave record:
      `mov dword ptr [eax + 0xc], ecx` where `ecx` is its second argument, i.e.
      `GraveInfo+0x0C`. (`GraveInfo` is the 0x3C-byte struct
      `?GetMainPlayersGraveData@GameEngine@GAME@@QBEPBUGraveInfo@
      FixedItemGravestone@2@XZ` walks, stride 0x3c at GE+0x88.)

  (e) `?GetPlayerExperienceRedemptionAmount@GameEngine@GAME@@IAEII@Z`
                                                          VA 0x10194f60
      reads that same `GraveInfo+0x0C`, converts it to float, and does

          mulss  xmm0, dword ptr [edi + 0x2a04]

      then truncates (`fldcw` with RC=11 chop, `fistp`). GE+0x2A04 is
      `RedemptionMultiplier`: the ONLY writer of that member is the GameEngine
      field loader at VA 0x1019b8c3,

          mov   dword ptr [esp], 0x3f000000      ; the engine's own default, 0.5f
          push  0x10346548                       ; "RedemptionMultiplier"
          call  eax                              ; GetFloat(field, default)
          fstp  dword ptr [edi + 0x2a04]

      and the only reader is the `mulss` above (plus a constructor init to 1.0f
      at VA 0x101a378d). `?PlayerExperienceRedemption@GameEngine@GAME@@QAEXI_N@Z`
      (VA 0x101a3d20) is the grave-touch handler and its single call to (e) is
      the only one in the binary.

  So, exactly:

      recovered = trunc( (float)(XP ACTUALLY LOST ON DEATH) * RedemptionMultiplier )

  and the record the loader reads is the SAME one `death_xp_penalty` owns -
  `records\xpack\game\gameengine.dbr`, the only `*GameEngine.dbr` literal in any
  shipped binary (Game.dll 0x00344554 also hard-codes the ONE gravestone record,
  `Records/XPack/Item/Gravestones/GravestoneGreece.dbr`, Class
  `FixedItemGravestone`).

================================================================================
2. WHAT THIS MEANS FOR THE BUG R-109 WAS OPENED AGAINST
================================================================================
R-109 feared a free-XP loop: "the player loses 10% and recovers 100%". MEASURED,
that loop never existed. The grave stores the amount ACTUALLY REMOVED at death,
not a precomputed absolute, so b93's 90% cut scaled the recovery in lockstep:
before b93 you lost P and recovered 0.5P; after b93 you lost 0.1P and recovered
0.05P. Recovery was always HALF the loss, never above it. The honest report is:
no exploit shipped, and the pre-R-109 defect is the OPPOSITE one - **the player
was being punished twice**, losing X and getting only X/2 back.

R-109 rules the equality, and R-109's own gate clause says so explicitly:
"`recovered < lost` is no longer a pass: it would quietly punish the player
twice."

================================================================================
3. THE CHANGE - ONE FIELD, AND IT IS DERIVED, NOT HARDCODED
================================================================================
    records\xpack\game\gameengine.dbr
      RedemptionMultiplier   OLD 0.5   ->   NEW 1.0        (dtype FLOAT, kept)

With the multiplier at 1.0 the engine's own formula collapses to the identity

    recovered = trunc((float)lost * 1.0) = lost

R-109 asks for the recovery to be "expressed in terms of the penalty so the two
cannot drift". The ENGINE ALREADY DOES THAT - `RegisterExperienceLoss` records
the realised loss - so the equality needs no mirrored equation and no gate
against two equations diverging: retune `deathPenaltyEquation`,
`deathPenaltyMin` or `deathPenaltyMax` however you like and the marker follows
automatically, because it never sees those fields at all. That is the strongest
available form of R-109's "self-correcting" requirement, and it is why this
module writes a multiplier rather than a second equation.

**R-251 [2026-08-14] IS THE FIRST LIVE EXERCISE OF THAT PROPERTY.** Will halved
the death penalty again ("lets reduce the penalty for dying by another 50% from
what it currently is at"): `death_xp_penalty` moved the divisor 90 -> 180 and the
cap 50,000 -> 25,000, and THIS MODULE DID NOT CHANGE A SINGLE VALUE. The equality
still holds because it is derived, and `verify()` below re-proves it against the
NEW knobs it reads off the db (not against any constant in this file). Had R-109
been built as the "10% of the original" form Will first floated, R-251 would have
silently desynchronised the marker and re-opened the very drift R-109 named.

EXACTNESS OF THE IDENTITY (this is arithmetic, not a hope). The engine round-trip
is int32 -> double -> float32 -> `mulss` by 1.0f -> truncate. float32 represents
every integer up to 2^24 = 16,777,216 exactly, `x * 1.0f` is exact for every
finite float, and truncating an exactly-represented integer returns it. The
shipped `deathPenaltyMax` is 25,000 (R-251) and the realised loss is bounded above
by the nominal penalty, so every value this path can carry is < 2^24 by a factor
of 671 - the headroom only GREW when the penalty was cut.
`verify()` re-proves the identity numerically over L1..1000 x N/E/L rather than
asserting it, and separately re-proves the 2^24 headroom against the LIVE cap.

WHY 1.0 IS SAFE FOR THE ENGINE: 1.0f is the value `GameEngine`'s own constructor
puts in that member before the DBR load (VA 0x101a378d,
`mov dword ptr [ebx+0x2a04], 0x3f800000`). We are writing the engine's own
pre-load default, not an out-of-band number.

================================================================================
4. SHARED-RECORD LAW
================================================================================
`records\xpack\game\gameengine.dbr` is shared, so the law says enumerate the
carriers before editing and clone-and-repoint if a non-target carrier exists.
Enumerated here, and the answer is that cloning is IMPOSSIBLE and unnecessary:
`Records/XPack/Game/GameEngine.dbr` is a hard-coded ASCII literal in Game.dll and
is the ONLY GameEngine path any shipped binary contains, so there is exactly one
carrier and it IS the target. The five same-named lookalikes the engine never
loads are SEPARATE records, they are listed in `death_xp_penalty.DEAD_LOOKALIKES`
with their own values, and this module re-asserts all five unchanged (they all
carry `RedemptionMultiplier = 0.5` today; leaving them alone is what keeps a
future reader from mistaking one of them for the live one).

The record already has ONE registry writer of these balance fields
(`death_xp_penalty`, R-80) plus `damage_display` (FontStyles). This module is
registered immediately AFTER `death_xp_penalty`, reads its two fields to prove
the coupling, and writes exactly one field neither of them touches. The S4b
collision WARN naming this trio on this record is EXPECTED and benign; a FOURTH
module on it is a real finding.

CONTRACT (tools/patches/README.md): MODULE_NAME + apply(db, tags) + verify(db,
tags). No tags, no new records, no map bytes, no Text.arc surface.
"""
import math
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

# SIBLING import. The registry loads this file as `patches.tombstone_xp_recovery`
# (`importlib.import_module('%s.%s' % (__name__, name))` in patches/__init__.py),
# so `death_xp_penalty` - which lives in patches/, NOT in tools/ - is only
# reachable package-relatively. A bare `import death_xp_penalty` builds and passes
# the CLI (where this file runs as __main__ with patches/ as the script dir) and
# then dies inside the real build; the registry's _load_module is fail-loud, so
# that mistake reds the build rather than silently skipping the R-109 ruling
# (measured: build exit 1, "REGISTRY entry 'tombstone_xp_recovery' failed to
# import ... No module named 'death_xp_penalty'"). Both paths are supported here.
try:                                    # imported as patches.tombstone_xp_recovery
    from . import death_xp_penalty as dxp          # noqa: E402
except ImportError:                     # run directly: py tools/patches/<this>.py
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import death_xp_penalty as dxp                 # noqa: E402

MODULE_NAME = 'tombstone XP recovery == XP lost (R-109)'

# The ONE record Game.dll loads (see death_xp_penalty for the literal-scan proof).
GAMEENGINE = dxp.GAMEENGINE

FIELD = 'RedemptionMultiplier'
MULT_OLD = 0.5      # vanilla TQAE, and the engine loader's own default (0x3f000000)
MULT_NEW = 1.0      # the R-109 identity, and the constructor's pre-load value
_TOL = 1e-9

# float32 represents every integer below this exactly, so trunc(n * 1.0f) == n.
FLOAT32_EXACT_INT_BOUND = 1 << 24

# The five deathPenalty-bearing GameEngine lookalikes the engine never loads. They
# all carry the vanilla RedemptionMultiplier; verify() proves we did not shotgun
# them (mirroring the edit there would make a future reader think one is live).
DEAD_LOOKALIKES = tuple(dxp.DEAD_LOOKALIKES)

# The ONE gravestone record, hard-coded in Game.dll at 0x00344554. Read-only here:
# asserted present and Class-correct so a lane that retires it reds this build
# instead of silently removing the surface the ruling is about.
GRAVESTONE = r'records\xpack\item\gravestones\gravestonegreece.dbr'
GRAVESTONE_CLASS = 'FixedItemGravestone'


def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def _dtype_of(db, rec, field):
    fields = db.get_fields(rec)
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == field:
            return tf.dtype
    return None


def _val(db, rec, field):
    try:
        return _scalar(db.get_field_value(rec, field))
    except Exception:
        return None


# ── the two halves of the invariant, modelled on the actual instructions ────
def _f32(x):
    """Round a Python float through IEEE binary32, the way the engine's equation
    evaluator does when it stores its result with `fstp dword ptr`."""
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


def xp_lost(level, difficulty_dv, divisor, cap):
    """Real-valued penalty, before the engine's rounding/clamp. Delegates to
    death_xp_penalty's own model so the R-80 and R-109 sides cannot drift."""
    return dxp.penalty(level, difficulty_dv, divisor, cap)


def xp_lost_int(level, difficulty_dv, divisor, cap, floor=0):
    """The INTEGER the engine actually subtracts, modelled instruction by
    instruction from `GetPlayerDeathExperiencePenalty` (VA 0x101945a0):

        raw   = equation result, stored through float32 (`fstp dword ptr`)
        raw   = max(raw, 0.0)                     comiss xmm0,xmm1 / ja / movaps
        n     = trunc(double(raw) + 0.5)          addsd [0x103a3348] (== 0.5,
                                                  read out of the DLL) then fistp
                                                  with RC=11 (chop) -> round-half-up
        lost  = clamp(n, deathPenaltyMin, deathPenaltyMax)   cmovg / cmovl
    """
    raw = _f32(max((float(level) ** 3) * ((1.0 + (3.0 * difficulty_dv)) / float(divisor)), 0.0))
    n = math.trunc(float(raw) + 0.5)
    return min(max(n, int(floor)), int(cap))


def xp_recoverable(lost, multiplier):
    """What the death MARKER gives back, modelled from
    `GetPlayerExperienceRedemptionAmount` (VA 0x10194f60):

        f    = float32(GraveInfo+0x0C)   int -> double (+ the {0, 2^32} unsigned
                                         fixup at 0x103a34f0) -> cvtpd2ps
        back = trunc(f * RedemptionMultiplier)        mulss [GE+0x2A04], fistp RC=11

    NOTE the input is the amount ACTUALLY removed at death (RegisterExperienceLoss,
    VA 0x10194540), which the level-floor can make SMALLER than the clamped
    penalty - never larger. The identity below holds for every value < 2^24, so it
    holds for the realised loss as well as for the nominal one."""
    return math.trunc(_f32(float(lost)) * float(multiplier))


def _current_penalty_knobs(db):
    """Read the LIVE penalty knobs off the db so the proof is against what is
    actually shipping, never against a constant baked in here."""
    eq = _val(db, GAMEENGINE, 'deathPenaltyEquation')
    mx = int(_val(db, GAMEENGINE, 'deathPenaltyMax'))
    mn = int(_val(db, GAMEENGINE, 'deathPenaltyMin'))
    # the divisor is the only term this module needs from the equation string
    divisor = None
    if isinstance(eq, str) and eq.endswith(')') and '/' in eq:
        tail = eq.rsplit('/', 1)[1]
        try:
            divisor = float(tail.strip().rstrip(')').strip())
        except ValueError:
            divisor = None
    return eq, divisor, mn, mx


# ── registry hooks ──────────────────────────────────────────────────────────
def apply(db, tags):
    if not db.has_record(GAMEENGINE):
        raise SystemExit(
            'tombstone_xp_recovery: %s absent - the engine-loaded GameEngine record '
            'is gone (build base changed?)' % GAMEENGINE)

    cur = _val(db, GAMEENGINE, FIELD)
    if cur is None:
        raise SystemExit(
            'tombstone_xp_recovery: %s carries no %s field. The engine would then '
            'fall back to its loader default 0.5f and the R-109 equality would be '
            'silently unimplementable - fail rather than create the field blind.'
            % (GAMEENGINE, FIELD))
    cur = float(cur)

    already = abs(cur - MULT_NEW) <= _TOL
    if not already and abs(cur - MULT_OLD) > _TOL:
        raise SystemExit(
            'tombstone_xp_recovery: unexpected pre-state on %s.%s = %r. Expected the '
            'vanilla %.1f or the already-ruled %.1f. Another writer moved this field: '
            'resolve the ordering before shipping (last-writer-wins).'
            % (GAMEENGINE, FIELD, cur, MULT_OLD, MULT_NEW))

    # R-80 coupling: this module's whole justification is that the marker mirrors
    # the penalty, so the penalty must be in its ruled state when we run.
    eq = _val(db, GAMEENGINE, 'deathPenaltyEquation')
    mx = int(_val(db, GAMEENGINE, 'deathPenaltyMax'))
    if eq != dxp.EQ_NEW or mx != dxp.MAX_NEW:
        raise SystemExit(
            'tombstone_xp_recovery: the R-80 death penalty is not in its ruled state '
            '(deathPenaltyEquation=%r deathPenaltyMax=%r, expected %r / %d). This '
            'module must run AFTER death_xp_penalty - fix the registry order.'
            % (eq, mx, dxp.EQ_NEW, dxp.MAX_NEW))

    dt = _dtype_of(db, GAMEENGINE, FIELD)
    before_fields = {k: list(v.values) for k, v in db.get_fields(GAMEENGINE).items()}
    modified_before = set(db._modified)

    # No explicit dtype: the field exists, so set_field keeps its FLOAT dtype
    # (CLAUDE.md's dtype-preservation law).
    db.set_field(GAMEENGINE, FIELD, MULT_NEW)

    got = _dtype_of(db, GAMEENGINE, FIELD)
    if got != dt:
        raise SystemExit('tombstone_xp_recovery: dtype corruption on %s.%s (%r -> %r)'
                         % (GAMEENGINE, FIELD, dt, got))

    # scope proof A: exactly one field moved on this record
    after_fields = {k: list(v.values) for k, v in db.get_fields(GAMEENGINE).items()}
    if set(before_fields) != set(after_fields):
        raise SystemExit('tombstone_xp_recovery: field set changed on %s' % GAMEENGINE)
    moved = sorted(k for k in before_fields if before_fields[k] != after_fields[k])
    expected = [] if already else [FIELD]
    if moved != expected:
        raise SystemExit(
            'tombstone_xp_recovery: expected exactly %r to move on %s, got %r'
            % (expected, GAMEENGINE, moved))
    # scope proof A2: the R-80 fields are provably untouched BY US
    for f in ('deathPenaltyEquation', 'deathPenaltyMin', 'deathPenaltyMax'):
        if before_fields.get(f) != after_fields.get(f):
            raise SystemExit(
                'tombstone_xp_recovery: R-80 field %s moved - this module must never '
                'write the penalty side' % f)

    # scope proof B: no other record dirtied
    newly = set(db._modified) - modified_before
    if newly - {GAMEENGINE}:
        raise SystemExit('tombstone_xp_recovery: touched unexpected record(s): %s'
                         % ', '.join(sorted(newly - {GAMEENGINE})))

    _eq, divisor, mn, mx = _current_penalty_knobs(db)
    # The INTEGER the engine actually subtracts - not the real-valued equation
    # result. Printing the latter made the line read "lose 23883, recover 23882",
    # which slanders the very equality this module exists to hold.
    lost85 = xp_lost_int(85, 2, divisor, mx, mn)
    print('    tombstone_xp_recovery: %s %s %.1f -> %.1f  (L85 Legendary: lose %d XP, '
          'recover %d XP; was %d)'
          % ('ALREADY RULED (no-op)' if already else 'applied', FIELD, MULT_OLD,
             MULT_NEW, lost85, xp_recoverable(lost85, MULT_NEW),
             xp_recoverable(lost85, MULT_OLD)))


def verify(db, tags):
    """Post-finalization guard on the FINAL merged arz. R-109's gate, in its
    SUPERSEDING form: assert EQUALITY, not `<=`. Recovery above the penalty and
    recovery below it both red the build."""
    cur = _val(db, GAMEENGINE, FIELD)
    if cur is None:
        raise SystemExit('tombstone_xp_recovery verify: %s.%s is absent.'
                         % (GAMEENGINE, FIELD))
    cur = float(cur)
    if abs(cur - MULT_NEW) > _TOL:
        raise SystemExit(
            'tombstone_xp_recovery verify: %s is %r, expected %.1f - a later phase '
            'clobbered the R-109 ruling. At %r the death marker would return %.0f%% '
            'of the XP the death penalty took, which %s.'
            % (FIELD, cur, MULT_NEW, cur, 100.0 * cur,
               'is a free-XP loop' if cur > MULT_NEW else 'punishes the player twice'))
    if _dtype_of(db, GAMEENGINE, FIELD) != 1:      # DATA_TYPE_FLOAT
        raise SystemExit('tombstone_xp_recovery verify: %s is not FLOAT.' % FIELD)

    # --- THE RULED INVARIANT, RE-DERIVED NUMERICALLY (never asserted) ---------
    # Read the LIVE penalty knobs, so if a future lane retunes the penalty this
    # gate re-proves the equality against the NEW penalty rather than a constant.
    eq, divisor, mn, mx = _current_penalty_knobs(db)
    if divisor is None:
        raise SystemExit(
            'tombstone_xp_recovery verify: could not read the divisor out of '
            'deathPenaltyEquation=%r. The equality proof below needs it; if the '
            'equation shape changed, update this reader deliberately.' % eq)
    worst = None
    checked = 0
    for lvl in range(1, 1001):
        for dv in (0, 1, 2):
            lost = xp_lost_int(lvl, dv, divisor, mx, mn)
            back = xp_recoverable(lost, cur)
            checked += 1
            if back != lost:
                worst = (lvl, dv, lost, back)
                break
        if worst:
            break
    if worst:
        lvl, dv, lost, back = worst
        raise SystemExit(
            'tombstone_xp_recovery verify: EQUALITY BROKEN at level %d, difficulty '
            'DV %d - the death penalty takes %d XP but the marker returns %d (%s).'
            % (lvl, dv, lost, back,
               'FREE-XP LOOP' if back > lost else 'the player is punished twice'))

    # The realised loss can be SMALLER than the clamped penalty (the level-floor in
    # the XP helper at VA 0x1017d620), so re-prove the identity over the whole
    # integer domain the grave can carry, not just the nominal penalties above.
    for u in (0, 1, 2, 3, 7, 999, 12345, 65535, 1 << 20,
              int(mx) - 1, int(mx), FLOAT32_EXACT_INT_BOUND - 1):
        if u < 0:
            continue
        if xp_recoverable(u, cur) != u:
            raise SystemExit(
                'tombstone_xp_recovery verify: EQUALITY BROKEN for a realised loss of '
                '%d XP - the marker returns %d.' % (u, xp_recoverable(u, cur)))
        checked += 1

    # --- the exactness precondition, re-proved against the LIVE cap ----------
    if int(mx) <= 0:
        raise SystemExit(
            'tombstone_xp_recovery verify: deathPenaltyMax is %d. A non-positive cap '
            'means the death penalty can never take anything, so R-109 has nothing to '
            'mirror - that is a penalty-side change (R-80) that must be re-ruled, not '
            'a state this gate may pass silently.' % int(mx))
    if int(mx) >= FLOAT32_EXACT_INT_BOUND:
        raise SystemExit(
            'tombstone_xp_recovery verify: deathPenaltyMax is %d, at or above the '
            'float32 exact-integer bound %d. Above that bound the engine\'s '
            'int -> float32 -> mulss -> truncate round-trip can lose the low bits and '
            'the marker would return LESS than was lost. Re-derive R-109 before '
            'raising the cap this far.' % (int(mx), FLOAT32_EXACT_INT_BOUND))

    # --- nothing else in the XP economy moved -------------------------------
    for rec in DEAD_LOOKALIKES:
        if not db.has_record(rec):
            continue
        v = _val(db, rec, FIELD)
        if v is not None and abs(float(v) - MULT_OLD) > _TOL:
            raise SystemExit(
                'tombstone_xp_recovery verify: dead lookalike %s has %s=%r - only the '
                'engine-loaded xpack record may change.' % (rec, FIELD, v))

    # --- the player-visible surface the ruling is about still exists ---------
    if not db.has_record(GRAVESTONE):
        raise SystemExit(
            'tombstone_xp_recovery verify: %s is GONE. Game.dll hard-codes that exact '
            'path (0x00344554) as the ONE gravestone record; without it there is no '
            'death marker to recover from. RETIREMENT PROTOCOL: this record is design '
            'law, not dead content.' % GRAVESTONE)
    cls = _scalar(_val(db, GRAVESTONE, 'Class'))
    if str(cls) != GRAVESTONE_CLASS:
        raise SystemExit(
            'tombstone_xp_recovery verify: %s is Class=%r, expected %r.'
            % (GRAVESTONE, cls, GRAVESTONE_CLASS))

    print('  tombstone_xp_recovery.verify OK: %s = %.1f (FLOAT); XP recovered from the '
          'death marker == XP lost to the death penalty EXACTLY on %d checked points '
          '(L1-1000 x Normal/Epic/Legendary against the LIVE penalty - divisor %g, cap '
          '%d, min %d - plus the realised-loss domain up to the float32 bound); the cap '
          'is %.0fx inside the float32 exact-integer bound %d; all %d dead gameengine '
          'lookalikes still at %.1f; %s intact (Class %s).'
          % (FIELD, cur, checked, divisor, mx, mn,
             FLOAT32_EXACT_INT_BOUND / float(mx), FLOAT32_EXACT_INT_BOUND,
             len(DEAD_LOOKALIKES), MULT_OLD, GRAVESTONE.split('\\')[-1],
             GRAVESTONE_CLASS))


# ── CLI: the measured before/after table + the planted negative test ─────────
def _load(arz):
    from arz_patcher import ArzDatabase
    return ArzDatabase.from_arz(Path(arz))


def _table(arz, applied=False):
    """R-109's 'report the measured before/after BOTH WAYS' clause, computed from
    the arz's own knobs rather than from constants in this file.

    `applied=True` runs the two registry modules in memory first, so the table
    reports what the NEXT build will ship rather than what this (older) artifact
    holds. Which one you are reading is printed, never implied."""
    db = _load(arz)
    if applied:
        dxp.apply(db, {})
        apply(db, {})
    eq, divisor, mn, mx = _current_penalty_knobs(db)
    mult = float(_val(db, GAMEENGINE, FIELD))
    print('\nARZ: %s' % arz)
    print('  STATE: %s' % ('the arz AS IT WILL SHIP (death_xp_penalty + '
                           'tombstone_xp_recovery applied in memory)' if applied
                           else 'the artifact ON DISK, unmodified'))
    print('  deathPenaltyEquation : %s' % eq)
    print('  deathPenaltyMin/Max  : %d / %d' % (mn, mx))
    print('  %-20s : %.2f' % (FIELD, mult))
    print('\n  R-109 requires the report BOTH WAYS. Three penalty baselines - VANILLA')
    print('  (divisor %d / cap %d), the PREVIOUSLY SHIPPED R-80 pair (divisor %d / cap'
          % (dxp.DIV_VANILLA, dxp.MAX_VANILLA, dxp.DIV_R80))
    print('  %d, build92) and the penalty in THIS arz - against what the death marker'
          % dxp.MAX_R80)
    print('  gives back at the pre-R-109 multiplier 0.5 and at this arz\'s multiplier:\n')
    hdr = ('%-6s %-11s | %11s %11s %11s | %11s %11s %8s'
           % ('level', 'difficulty', 'LOST van', 'LOST b92', 'LOST now',
              'BACK@0.5', 'BACK now', 'back/lost'))
    print('  ' + hdr)
    print('  ' + '-' * len(hdr))
    worst_ratio = None
    halved = True
    for lvl in (10, 25, 40, 55, 70, 85, 100):
        for dv, nm in ((0, 'Normal'), (1, 'Epic'), (2, 'Legendary')):
            van_lost = xp_lost_int(lvl, dv, dxp.DIV_VANILLA, dxp.MAX_VANILLA, 0)
            b92_lost = xp_lost_int(lvl, dv, dxp.DIV_R80, dxp.MAX_R80, 0)
            new_lost = xp_lost_int(lvl, dv, divisor, mx, mn)
            back = xp_recoverable(new_lost, mult)
            ratio = (back / float(new_lost)) if new_lost else float('nan')
            if new_lost and (worst_ratio is None or abs(ratio - 1.0) > abs(worst_ratio - 1.0)):
                worst_ratio = ratio
            if abs(new_lost - b92_lost / 2.0) > 0.5:
                halved = False
            print('  %-6d %-11s | %11d %11d %11d | %11d %11d %8.4f'
                  % (lvl, nm, van_lost, b92_lost, new_lost,
                     xp_recoverable(new_lost, 0.5), back, ratio))
    print('\n  RATIO recovered/lost at the SHIPPED multiplier %.2f: worst %.4f over the'
          % (mult, worst_ratio if worst_ratio is not None else float('nan')))
    print('  rows above (R-109 requires exactly 1.0000 - equality, not <=).')
    # MEASURED, not asserted: an artifact built before R-251 will say so here.
    print('  LOST b92 -> LOST now: %s'
          % ('every row is exactly half - this is R-251 ("another 50%")' if halved
             else 'NOT halved (divisor %g / cap %d) - this artifact predates R-251; '
                  're-run with --applied to see what the next build ships'
                  % (divisor, mx)))
    print('  Every LOST / BACK column above is an INTEGER because the engine rounds '
          '(x + 0.5, chop) before the clamp; the recovery then multiplies that integer.')


def _negtest(arz):
    """Prove the R-109 gate is not vacuous. Plants on BOTH sides, as R-109 demands."""
    db = _load(arz)
    # Bring the PENALTY side to its currently ruled state first, exactly as the
    # registry does (death_xp_penalty runs immediately before this module). Without
    # this, running against any already-built arz - which carries whatever penalty
    # pair was ruled when it was built - would trip this module's own R-80 coupling
    # guard and the whole negative suite would never run.
    dxp.apply(db, {})
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
        ok = (failed == expect_fail)
        results.append((label, expect_fail, failed, ok))
        return ok

    good = float(_val(db, GAMEENGINE, FIELD))

    # CONTROL: the ruled state must PASS.
    check('control - ruled state passes', False, lambda: None, lambda: None)

    # PLANT 1 (R-109's "recovery above the penalty must red the build").
    check('recovery ABOVE the loss (multiplier 2.0) rejected', True,
          lambda: db.set_field(GAMEENGINE, FIELD, 2.0),
          lambda: db.set_field(GAMEENGINE, FIELD, good))

    # PLANT 2 (R-109's "recovery below it must red the build" - the OLD shipped
    # value 0.5 is itself the negative now).
    check('recovery BELOW the loss (the pre-R-109 0.5) rejected', True,
          lambda: db.set_field(GAMEENGINE, FIELD, MULT_OLD),
          lambda: db.set_field(GAMEENGINE, FIELD, good))

    # PLANT 3: the "10%" reading R-109 explicitly rejects must also red.
    check('the rejected hardcoded-10% form (multiplier 0.1) rejected', True,
          lambda: db.set_field(GAMEENGINE, FIELD, 0.1),
          lambda: db.set_field(GAMEENGINE, FIELD, good))

    # PLANT 4: a dead lookalike mirroring the edit must red (anti-shotgun).
    live_lookalikes = [r for r in DEAD_LOOKALIKES if db.has_record(r)]
    if live_lookalikes:
        la = live_lookalikes[0]
        prev = float(_val(db, la, FIELD))
        check('dead lookalike shotgunned (%s) rejected' % la.split('\\')[-1], True,
              lambda: db.set_field(la, FIELD, MULT_NEW),
              lambda: db.set_field(la, FIELD, prev))
    else:
        results.append(('dead lookalike plant', True, False, False))

    # PLANT 5: retiring the ONE gravestone record must red (retirement protocol).
    if db.has_record(GRAVESTONE):
        prev_cls = _scalar(_val(db, GRAVESTONE, 'Class'))
        check('gravestone record de-classed rejected', True,
              lambda: db.set_field(GRAVESTONE, 'Class', 'Tile'),
              lambda: db.set_field(GRAVESTONE, 'Class', prev_cls))
    else:
        results.append(('gravestone plant', True, False, False))

    # PLANT 6: THE COUPLING. Retune the death penalty and the equality must still
    # hold with NO change here - this is what proves the fix is derived and not a
    # hardcoded 10%. The gate must PASS with a different penalty.
    # The retune is DERIVED from whatever divisor is live (it used to be a literal
    # '/ 90)' -> '/ 45)' string swap, which silently became a NO-OP the moment
    # R-251 moved the divisor to 180 - a plant that plants nothing is worse than
    # no plant at all, so the swap is asserted to have actually changed the string).
    prev_eq = _val(db, GAMEENGINE, 'deathPenaltyEquation')
    prev_mx = int(_val(db, GAMEENGINE, 'deathPenaltyMax'))
    live_div = int(dxp.divisor_of(prev_eq) or 0)
    retuned_eq = dxp.EQ_SHAPE % (live_div * 2) if live_div else None
    if not retuned_eq or retuned_eq == prev_eq:
        results.append(('penalty RETUNE plant could not be built from %r' % (prev_eq,),
                        False, True, False))
    else:
        check('penalty RETUNED (divisor %d -> %d, cap -> 123456) still passes untouched'
              % (live_div, live_div * 2), False,
              lambda: (db.set_field(GAMEENGINE, 'deathPenaltyEquation', retuned_eq),
                       db.set_field(GAMEENGINE, 'deathPenaltyMax', 123456)),
              lambda: (db.set_field(GAMEENGINE, 'deathPenaltyEquation', prev_eq),
                       db.set_field(GAMEENGINE, 'deathPenaltyMax', prev_mx)))

    # PLANT 7: the same coupling in the direction R-251 actually moved - HALVE the
    # live penalty (divisor x2, cap /2, exactly what death_xp_penalty just did) and
    # require the equality to hold with no edit on the recovery side. This is the
    # R-251 regression test for R-109.
    if retuned_eq:
        check('penalty HALVED like R-251 (divisor %d -> %d, cap %d -> %d) still passes'
              % (live_div, live_div * 2, prev_mx, prev_mx // 2), False,
              lambda: (db.set_field(GAMEENGINE, 'deathPenaltyEquation', retuned_eq),
                       db.set_field(GAMEENGINE, 'deathPenaltyMax', prev_mx // 2)),
              lambda: (db.set_field(GAMEENGINE, 'deathPenaltyEquation', prev_eq),
                       db.set_field(GAMEENGINE, 'deathPenaltyMax', prev_mx)))

    print('\ntombstone_xp_recovery _negtest:')
    for label, expect_fail, failed, ok in results:
        print('  [%s] %-62s expected=%s got=%s'
              % ('PASS' if ok else 'FAIL', label,
                 'REJECT' if expect_fail else 'ACCEPT',
                 'REJECT' if failed else 'ACCEPT'))
    allok = all(o for _, _, _, o in results)
    print('  -> %s (%d/%d)' % ('PASS' if allok else 'FAIL',
                               sum(1 for _, _, _, o in results if o), len(results)))
    return 0 if allok else 1


if __name__ == '__main__':
    args = sys.argv[1:]
    DEFAULT_ARZ = (Path(__file__).resolve().parents[2]
                   / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    if '--table' in args:
        i = args.index('--table')
        target = DEFAULT_ARZ
        if len(args) > i + 1 and not args[i + 1].startswith('--'):
            target = args[i + 1]
        _table(target, applied='--applied' in args)
    elif '--negtest' in args:
        i = args.index('--negtest')
        raise SystemExit(_negtest(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ))
    else:
        print(__doc__)
