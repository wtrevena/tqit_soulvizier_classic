r"""svc_loot_volume.py - THE DROP-VOLUME CONTRACT (Will 2026-08-11, R-240).

WILL, VERBATIM (2026-08-11), the report this module exists to answer:
  "we probably need to trip the loot-volume trim, especially on the steam version
   where maybe from the two chests, you get guaranteed 1 legendary item. on the
   testhub version we can spawn more that is fine."

WHAT WAS ALREADY KNOWN, AND WHY IT TOOK A RULING
------------------------------------------------
R-181 measured it and wrote it down as `BL-R181-DEBT-5`: `numSpawn` is the drop
VOLUME lever, lowering it REDUCES drops per open, and non-reduction (R-100 #17 /
Will 2026-08-08 / R-180) forbids that without Will's say-so. Three waves therefore
raised composition while volume stood still, and the honest sentence in the R-181
record was "much rarer for a spear, still routine for something". This ruling is the
say-so. Non-reduction is SUSPENDED for volume and volume only: pool membership,
weights, group chances and the guaranteed slot are all untouched here, so every
breadth and distribution property b75-b83 shipped survives at lower volume.

WHY THE TWO GATE FAMILIES SURVIVE A VOLUME CUT BY CONSTRUCTION
---------------------------------------------------------------
* `svc_loot_breadth` / `svc_orb_breadth` / `svc_craft_thrown` count DISTINCT
  REACHABLE items. Reachability is a property of the loot GRAPH; `numSpawn` is a
  multiplier on how many times that graph is sampled. Nothing here can change a
  pool's membership, so those gates are mathematically blind to this wave - and
  that blindness is the correct behaviour, not a gap.
* `svc_loot_distribution` D1-D6, D8, D9 and D7b are all RATIOS - a class's share of
  a surface's mass, an item's share of its class, weapon mass over armour mass, a
  worn slot's yield per SPAWN ITERATION. Every one of them divides the volume out.
* D7 is the single exception in the whole contract: an ABSOLUTE floor of
  `ARMOR_SLOT_FLOOR` worn-slot pieces PER OPEN. Its own block comment already says
  what to do here - "below that the number is a numSpawn demand rather than a parity
  one" - so R-240 re-anchors D7's volume reference and floor TOGETHER, preserving its
  per-iteration strength exactly. See `svc_loot_distribution` D7X2.

THE LEVER, AND THE ONE THING THAT MUST NEVER HAPPEN
----------------------------------------------------
Every in-scope table's numSpawn equation has the shape `(<bracket>)*<M>` and ONLY
`<M>` moves. The bracket carries `numberOfPlayers`, so co-op scaling is preserved
exactly and the RunEquation form is preserved byte-for-byte in shape.

THE BUILD28/29/30 P0 IS THE FLOOR OF THIS DESIGN, not a footnote. That wave replaced
a numSpawn equation with the bare literal '48'; the engine's evaluator returned 0 and
the chest opened and dropped NOTHING - a P0 that took three builds to find because
every byte comparison was broken-vs-broken. So this module:
  * NEVER writes a bare literal (V4 reds any equation that lost `numberOfPlayers`);
  * NEVER lets `numSpawnMin` evaluate below `MIN_SPAWN_MIN_SOLO` iterations at one
    player (V3), so a trimmed container still spawns at least one loot iteration and
    the guaranteed 100% row still fires. That floor is what turns Will's "guaranteed
    1 legendary item" into a property instead of an average.

THE MECHANICAL FLOOR, STATED PLAINLY BECAUSE IT IS NOT ONE
-----------------------------------------------------------
ONE spawn iteration of the canonical cage already pays 1.60 (chest_01) + 1.14
(chest_03) = 2.74 Legendary-grade gear pieces on Legendary difficulty, because six
loot groups roll independently per iteration and their chances sum past 280%. So the
numSpawn lever CANNOT reach a literal 1.0 per two-chest run; 2.74 is its floor, and
this wave lands at roughly 3.8 - within 40% of that floor. Going below it means
lowering group chances or the guaranteed row, which is composition, which this lane
is forbidden to touch. Registered as `BL-R240-DEBT-1`.

TESTHUB vs CANONICAL: THE SPLIT IS BY RECORD, BECAUSE THE ARZ IS SHARED
------------------------------------------------------------------------
The TESTHUB Levels variant is never uploaded, but there is only ONE database and both
map variants read it. The four TESTHUB farm-duplicate cage chests (Will 2026-08-08)
place the SAME two container records as the two canonical placements, so a trim
written into those records reaches Will's DEV farm too. The split is therefore made
where a shared arz CAN express it - in the RECORDS: this module clones the whole cage
chain to a `_hub` twin BEFORE trimming, so the hub twin keeps the shipped volume
byte-for-byte, and `build_section_surgery.build_hub_extra_specs` points the four
TESTHUB-only placements at the twin. The canonical `B41_SPECS` is untouched, so
`local/Levels_merged.arc` stays byte-identical and the Steam delta stays arz-only.

  ⚠ COUPLING: the hub half only reaches the game when the TESTHUB Levels variant is
  REBUILT (`SVC_TEST_HUB=1`). Until then the four duplicates keep naming the canonical
  records and the DEV cage is trimmed like canonical. That is the safe direction of
  failure - DEV under-pays, Steam never over-pays - and V5 proves the split exists in
  the db regardless of when the map catches up.

Shared by `tools/gate_loot_volume.py` (standalone), the in-build gate
`tools/patches/loot_volume_trim.verify()` and `tools/debug/negtest_loot_volume.py`,
so the three can never disagree (the `gate_relic_difficulty_tiers` precedent).
"""
import re
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD
import svc_loot_ownership as OWN

# ─────────────────────────────────────────────────────────────────────────────
# THE LADDER (R-240). TWO committed constants and a floor; every per-table
# multiplier below is DERIVED from them, so nothing here is a typed table of
# magic numbers that can drift out of step with the surfaces it governs.
#
# CANON_TRIM is per DIFFICULTY TIER, which is how Will's "interpret sensibly per
# difficulty" is expressed: a Legendary-difficulty container keeps more of its
# shipped volume than a Normal one. The ladder is deliberately SHALLOW (8.5% ->
# 10.5%) because at these volumes the difference between tiers is whether the
# container rolls a second loot iteration at all, and a steeper ladder would buy
# nothing a player could feel while making the Normal cage feel broken.
#
# RANK IS PRESERVED IN SPAWN VOLUME (S), AND ONLY THERE. An earlier draft of this
# block claimed more, in a unit the table under it printed the opposite of, and the
# round-2 vet caught it. The trim is MULTIPLICATIVE on each table's own shipped
# multiplier, so S keeps its shipped order: the blood-cave mega chest stays the
# highest-S surface in the mod (1.991, against the cage's 1.310/1.512), and cage
# chest_03 stays above chest_01 on every difficulty. TWO CORRECTIONS to what that
# does NOT mean, both MEASURED rather than reasoned:
#   * IN GEAR PER OPEN THE ORDER IS DIFFERENT, AND IT WAS ALREADY DIFFERENT BEFORE
#     THIS WAVE - so the trim neither caused it nor can fix it. On the SHIPPED b83
#     arz the cage chest_01 [n] already paid 23.88 against the blood cave's 17.45
#     and the hoards' 19.19, and chest_03 already paid LESS than chest_01 on all
#     three difficulties (19.83 vs 23.88 on Normal). After the wave: cage 2.153,
#     hoards 1.730, blood cave 1.483-1.497; chest_03 1.686/1.193/1.724 against
#     chest_01 2.153/1.483/2.099. Gear-per-open is S times the surface's own group
#     COMPOSITION, and composition belongs to R-180/R-181/R-220, not to this lane.
#   * THE ORB RANK DOES NOT SURVIVE EVEN IN S. The never-empty floor lifts every
#     thin container to exactly the same floor volume, so `svc_uberorb_apex_n01c`
#     and `orb uberorb_default_n01c` both land on S 1.125 / 1.014 gear per open -
#     EQUAL, where shipped they were 10.58/9.53 against 5.06/4.56. What they are
#     sitting on is the floor, not the ladder. The b79 precedent Will asked to keep
#     ("orbs stay generous relative to chests") survives in the sense he asked for -
#     an orb paying 1.014 against a cage chest's 2.153 is generous - but "an apex
#     orb still beats a level-banded one" is a casualty of the discrete floor, and
#     it is recorded as one instead of repeated. `--calibrate` prints S and gear per
#     open side by side for all 63 surfaces so neither claim need be made from memory.
# ─────────────────────────────────────────────────────────────────────────────
CANON_TRIM = {'n': 0.085, 'e': 0.095, 'l': 0.105}

# ── THE NEVER-EMPTY FLOOR - the build28/29/30 P0, expressed as a number ──────
# `numSpawnMin` must still evaluate to at least this many iterations at ONE player.
# 1.05 rather than 1.00 so that no rounding mode the engine might use - truncate,
# floor, round-half-even - can land on zero. At six players every in-scope bracket
# is at least 13.8, so co-op is never near this floor.
MIN_SPAWN_MIN_SOLO = 1.05
# ... and `numSpawnMax` at least this, so a trimmed container can still roll a
# SECOND iteration and the per-difficulty ladder has somewhere to express itself.
MIN_SPAWN_MAX_SOLO = 1.20

# ── R-247.7a SCOPE CARVE-OUT (Will 2026-08-13, verbatim: "wtf did you do to all the
# chests like toxeus the murderer devourer of blood's stash? Revert it back to what
# it was dropping in the original sv you nerfed the fuck out of it.") ──────────────
# The THREE Devourer-stash tables (the blood-cave "Toxeus the Murderer, Devourer of
# Blood's Stash" Majestic chest, tiers n/e/l) LEAVE R-240's trim scope and its V1
# canonical ceiling. Their volume authority is now tools/patches/
# r247_bloodcave_rulings.py, which restores the SV 0.98i originals (*3.8/*4.1) and
# gates them at exactly those values. This is a Will-ratified supersession recorded
# in docs/WILL_RULINGS.md (R-240 amendment + R-247 part 7) - NOT a quiet exclusion:
# scope_tables() drops them (so trim_table never trims them and V3/V4 stop covering
# them - the r247 module's verify() re-asserts form+floor+exact values), and the V1
# per-surface ceiling skips any surface made up entirely of exempt tables. Every
# other R-240 surface is untouched by this carve-out.
R247_STASH_EXEMPT = frozenset(
    'records\\drxitem\\container\\loottable_hidden_bloodcave_0%d.dbr' % i
    for i in (1, 2, 3))


def _r247_exempt(path):
    return SLB._n(path) in R247_STASH_EXEMPT


# ── R-251 SCOPE CARVE-OUT (Will 2026-08-14) ─────────────────────────────────────────
# The SECOND carve-out, on the same Will-ratified mechanism as R-247.7a above and for
# the same reason: R-240's trim was aimed at the polis-vault CAGE FARM ("we probably
# need to trip the loot-volume trim ... from the two chests, you get guaranteed 1
# legendary item"), and it swept the one-per-world UBER/BOSS HOARDS along with it. Will
# reported the result five separate times on 2026-08-14 - Propontis ("literally just
# dropped two items one thing of gold and incarnation of guan-yu's grace"), Tantalus,
# Ephialtes's Dread-Hoard, the Obsidian hoards, plus the Devourer's stash already
# reverted in R-247.7a.
#
# For 21 of those chests the trim was not even the operative nerf - a b42 finalization
# pass had ALREADY repointed them at base-game `boss_default_*`, so the trimmed tables
# were orphans nobody could open (docs/WILL_RULINGS.md R-251; tools/svc_uber_hoards.py
# has the full measurement). R-251 re-wires them, which makes them LIVE - and a live
# table at *0.2188 would be far worse than what Will complained about. So the family
# leaves R-240's scope and keeps the volume the monolith AUTHORS it with (*2.4/*2.8).
#
# The membership test is IMPORTED from `svc_uber_hoards`, not re-typed, so the trim's
# carve-out and R-251's own contract are provably the same set - a second typed list is
# how the two would drift into a gap.
#
# EVERY OTHER R-240 SURFACE IS UNTOUCHED: the 21 polis-vault cage tables (canonical AND
# hub), the 3 DRX donors, the 3 uberorb apex tables, boss_charon_*01b and the 12
# uberorb_default_* keep their trim exactly. In particular the CAGE does not move, which
# is why `gate_loot_distribution`'s D7X2 anchor - derived from the cage's POST-TRIM
# volume - stays valid across R-251.
try:
    from svc_uber_hoards import is_hoard_table as _r251_exempt
except ImportError:                                              # pragma: no cover
    def _r251_exempt(path):                                      # pragma: no cover
        raise SystemExit(
            "[svc_loot_volume] tools/svc_uber_hoards.py is MISSING, so R-251's uber/boss "
            "hoard carve-out cannot be applied. Failing loud rather than silently "
            "re-trimming the family Will reported five times: an import gap that "
            "degrades to 'trim everything' is exactly the quiet regression this "
            "carve-out exists to prevent.")


def _exempt(path):
    """Out of R-240's trim scope: the R-247.7a stash, or the R-251 uber/boss hoards."""
    return _r247_exempt(path) or _r251_exempt(path)

# ─────────────────────────────────────────────────────────────────────────────
# THE ENGINE'S ROUNDING MODE IS UNPROVEN, SO BOTH READINGS ARE ENFORCED
#
# `svc_loot_distribution.spawn_iterations` returns the CONTINUOUS mean (min+max)/2.
# Before this wave that was harmless: S ran 5.06 .. 18.96 and the fractional part
# was noise. AFTER the trim it is first-order, because every canonical cage table
# now evaluates to between 1.0502 and 1.6128 iterations solo - so under INTEGER
# TRUNCATION every one of them is exactly ONE iteration, and the per-difficulty
# ladder stops being expressible at all at one player. MEASURED, both readings of
# the two-chest run:
#
#     difficulty   continuous  P(>=1)   int-truncated  P(>=1)
#     Normal          3.839    0.9999       3.291      0.9996
#     Epic            2.676    0.9686       2.123      0.9378
#     Legendary       3.823    0.9963       2.742      0.9830
#
# We do not know which one the engine does, and this lane is not the place to find
# out (it needs an in-game count, which is `BL-R240-DEBT-5`). So the honest move is
# to enforce BOTH: V7 on the continuous reading, V7b on the truncated one, each
# with its own committed floor. Enforcing only the continuous reading would have
# let a 93.78% Epic guarantee ship under a PASS line that said 96.86%.
#
# TWO CONSEQUENCES WORTH READING TWICE, because they change what the ladder means:
#   * the truncated reading is the CONSERVATIVE one, and it is CLOSER to what Will
#     asked for ("guaranteed 1 legendary item"): 2.1 to 2.7 a run, not 2.7 to 3.8.
#     The direction of the modelling error is therefore benign for the ruling.
#   * `CANON_TRIM`'s per-difficulty ladder is, at these volumes, a CONTINUOUS-model
#     artefact. Solo, all three difficulties truncate to the same single iteration,
#     so what separates them under truncation is the tables' own composition, not
#     the multiplier. The ladder still does real work in co-op (at six players every
#     bracket is >= 13.8, where a multiplier difference is many whole iterations),
#     which is why it stays - but nobody should read "x0.085 vs x0.105" as a solo
#     difficulty difference.
# ─────────────────────────────────────────────────────────────────────────────


def spawn_iterations_trunc(d, table, players=1):
    """S under INTEGER TRUNCATION of each equation - the conservative reading.

    Deliberately NOT a rounding of the continuous mean: the engine evaluates the two
    equations separately, so if it truncates it truncates each one, and (int(min) +
    int(max))/2 is what that gives. At solo volumes this is the difference between a
    93.8% guarantee and a 96.9% one."""
    lo = SLD.eval_spawn(d.gv(table, 'numSpawnMinEquation'), players)
    hi = SLD.eval_spawn(d.gv(table, 'numSpawnMaxEquation'), players)
    if lo is None and hi is None:
        return 1.0
    if lo is None:
        return float(int(hi))
    if hi is None:
        return float(int(lo))
    return (int(lo) + int(hi)) / 2.0

# ─────────────────────────────────────────────────────────────────────────────
# THE HUB TWIN (naming). Deliberately a PREFIX (`polisvault_hub_01_l`) and not a
# suffix: `svc_armor_breadth.cage_surfaces` matches the canonical family by the
# pattern `polisvault_<N>_<tier><variant>`, and a suffix would have made the hub
# tables collide with that matcher. The prefix keeps the two families disjoint by
# construction instead of by a rule someone has to remember.
# ─────────────────────────────────────────────────────────────────────────────
HUB_MARK = 'hub'
_L = r'records\item\loottables\svc'
_C = r'records\drxitem\container'
CAGE_CHESTS = ('01', '03')
TIERS = ('n', 'e', 'l')
VARIANTS = ('a', 'b', 'c')
# The ProxyAccessoryPool weights polis_vault writes (50/25/25). Read here so the
# hub twin's surface is weighted exactly like the canonical one it mirrors.
VARIANT_W = (50, 25, 25)


def canon_cage_table(N, tier, variant):
    if variant == 'a':
        return (r'%s\polisvault_%s.dbr' % (_L, N) if tier == 'l'
                else r'%s\polisvault_%s_%s.dbr' % (_L, N, tier))
    return r'%s\polisvault_%s_%s%s.dbr' % (_L, N, tier, variant)


def hub_cage_table(N, tier, variant):
    return r'%s\polisvault_%s_%s_%s%s.dbr' % (_L, HUB_MARK, N, tier, variant)


def canon_cage_container(N, tier, variant):
    r"""`polis_vault._tier_container`: variant 'a' carries the BARE tier suffix, not
    `_na`. Mirrored here rather than imported because `polis_vault` is a registry
    module and importing one module from another's shared library would invert the
    dependency; V5 proves the two agree by resolving both sides against the db."""
    suffix = tier if variant == 'a' else '%s%s' % (tier, variant)
    return r'%s\svc_polisvault_chest_%s_%s.dbr' % (_C, N, suffix)


def hub_cage_container(N, tier, variant):
    return r'%s\svc_polisvault_%s_chest_%s_%s%s.dbr' % (_C, HUB_MARK, N, tier, variant)


def canon_cage_pool(N, tier):
    return r'%s\svc_polisvault_pool_%s_%s.dbr' % (_C, N, tier)


def hub_cage_pool(N, tier):
    return r'%s\svc_polisvault_%s_pool_%s_%s.dbr' % (_C, HUB_MARK, N, tier)


def canon_cage_chest(N):
    return r'%s\svc_polisvault_chest_%s.dbr' % (_C, N)


def hub_cage_chest(N):
    r"""The record the four TESTHUB-only duplicate placements name.

    `tools/build_section_surgery.build_hub_extra_specs` is the ONE caller, and it
    imports this function rather than typing the path, so the map side and the db
    side cannot drift apart (the split would then silently land on the wrong
    records, which is exactly the failure this whole lane is guarding against)."""
    return r'%s\svc_polisvault_%s_chest_%s.dbr' % (_C, HUB_MARK, N)


def is_hub(pathl):
    """Is this record part of the TESTHUB-only twin? Name-based, and the names are
    authored by the functions above, so this cannot disagree with them."""
    p = SLB._n(pathl)
    return ('\\polisvault_%s_' % HUB_MARK) in p or ('_%s_chest_' % HUB_MARK) in p \
        or ('_%s_pool_' % HUB_MARK) in p or p.endswith('_%s_chest_01.dbr' % HUB_MARK) \
        or p.endswith('_%s_chest_03.dbr' % HUB_MARK)


# ─────────────────────────────────────────────────────────────────────────────
# THE EQUATION. `(<bracket>)*<M>` - and NOTHING else is accepted.
# ─────────────────────────────────────────────────────────────────────────────
_EQ_RE = re.compile(r'^\((?P<bracket>.+)\)\s*\*\s*(?P<mult>\d+(?:\.\d+)?)$')


def parse_eq(expr):
    """('(<bracket>)', M) or None. Deliberately strict: an equation this cannot
    parse is NOT silently left alone, it fails the sweep (see `trim_table`)."""
    if not isinstance(expr, str):
        return None
    m = _EQ_RE.match(expr.strip())
    if not m:
        return None
    return ('(%s)' % m.group('bracket'), float(m.group('mult')))


def format_eq(bracket, mult):
    """Render a multiplier the way the shipped records render one: `2.4`, not
    `2.400000`, so a re-run that computes the same number writes the same bytes."""
    txt = ('%.4f' % mult).rstrip('0').rstrip('.')
    return '%s*%s' % (bracket, txt or '0')


def solo_value(bracket, mult):
    v = SLD.eval_spawn('%s*%s' % (bracket, mult), players=1)
    return 0.0 if v is None else v


def trimmed_multipliers(bracket, m_min, m_max, tier):
    """The R-240 multipliers for one table: the shipped pair scaled by this tier's
    trim, then raised to the never-empty floor. Returns (new_min, new_max, floored)
    where `floored` names which side the floor bound, for the report."""
    base = SLD.eval_spawn(bracket, players=1) or 1.0
    t = CANON_TRIM[tier]
    lo, hi = m_min * t, m_max * t
    floor_lo, floor_hi = MIN_SPAWN_MIN_SOLO / base, MIN_SPAWN_MAX_SOLO / base
    marks = []
    if lo < floor_lo:
        lo, _ = floor_lo, marks.append('min')
    if hi < floor_hi:
        hi, _ = floor_hi, marks.append('max')
    # Round to 4 decimals so the written bytes are stable and re-derivable, then
    # re-assert the floor AFTER rounding - rounding down through the floor is
    # exactly the kind of last-bit erosion the D7 float-boundary defect was.
    lo, hi = round(lo, 4), round(hi, 4)
    if solo_value(bracket, lo) < MIN_SPAWN_MIN_SOLO:
        lo = round(lo + 0.0001, 4)
    if solo_value(bracket, hi) < MIN_SPAWN_MAX_SOLO:
        hi = round(hi + 0.0001, 4)
    if hi < lo:
        hi = lo
    return lo, hi, marks


# ─────────────────────────────────────────────────────────────────────────────
# SCOPE - DERIVED from the distribution surface set, never a typed list. That
# derivation is the BL-R181-DEBT-7 lesson: fifteen live surfaces starved for three
# builds because a wave decided its own scope by folder name while another wave
# wrote tables elsewhere. Anything the distribution gate audits is a surface a
# player opens, so it is exactly the set whose volume Will is talking about.
# ─────────────────────────────────────────────────────────────────────────────
def scope_tables(db, lk=None):
    """{norm: (real, tier, is_hub)} for every loot table R-240 governs."""
    lk = lk or SLB.Lookup(db)
    out = {}
    for _label, tables, _w, tier in SAB.all_surfaces(db, lk):
        for t in tables:
            real = lk.real(t)
            if not real:
                continue
            if _exempt(real):
                # R-247.7a: the Devourer-stash tables left R-240's scope.
                # R-251:    so did every uber/boss `svc_*hoard_loot_0N` table.
                continue
            out[SLB._n(real)] = (real, tier, is_hub(real))
    return out


def trim_table(db, real, tier, lk=None):
    """Apply the R-240 trim to ONE table. Returns a list of change strings.

    FAILS LOUD on an equation shape it cannot parse. A silent skip here is how a
    surface keeps shipping at 12x volume while the gate's PASS line claims the trim
    landed everywhere - the same class of defect as an unowned loot table."""
    lk = lk or SLB.Lookup(db)
    changes = []
    got = {}
    for field in ('numSpawnMinEquation', 'numSpawnMaxEquation'):
        raw = lk.gv(real, field)
        p = parse_eq(raw)
        if p is None:
            raise SystemExit(
                "[svc_loot_volume] %s.%s = %r does not have the `(<bracket>)*<M>` "
                "shape this module can trim safely. It is NOT skipped: a bare literal "
                "is the build28/29/30 numSpawn-evaluates-to-0 P0 and an unrecognised "
                "shape is a surface silently keeping its full volume. Give the record "
                "the equation form, or widen `parse_eq` deliberately and say why."
                % (SLB._n(real), field, raw))
        got[field] = p
    bracket = got['numSpawnMinEquation'][0]
    if got['numSpawnMaxEquation'][0] != bracket:
        raise SystemExit(
            "[svc_loot_volume] %s has two DIFFERENT numSpawn brackets (%s vs %s). The "
            "trim scales a shared bracket; two brackets means the co-op scaling of min "
            "and max already disagree and a multiplier change would compound it."
            % (SLB._n(real), bracket, got['numSpawnMaxEquation'][0]))
    m_min, m_max = got['numSpawnMinEquation'][1], got['numSpawnMaxEquation'][1]
    lo, hi, marks = trimmed_multipliers(bracket, m_min, m_max, tier)
    if (lo, hi) == (m_min, m_max):
        return changes
    db.set_field(real, 'numSpawnMinEquation', format_eq(bracket, lo))
    db.set_field(real, 'numSpawnMaxEquation', format_eq(bracket, hi))
    db._modified.add(real)
    OWN.note_write(real, 'loot_volume_trim')
    changes.append('numSpawn *%g/*%g -> *%g/*%g (S %.2f -> %.2f%s)'
                   % (m_min, m_max, lo, hi,
                      (solo_value(bracket, m_min) + solo_value(bracket, m_max)) / 2.0,
                      (solo_value(bracket, lo) + solo_value(bracket, hi)) / 2.0,
                      (', FLOORED on ' + '+'.join(marks)) if marks else ''))
    return changes


# ─────────────────────────────────────────────────────────────────────────────
# THE HUB TWIN (write side)
# ─────────────────────────────────────────────────────────────────────────────
def _cloned(db, src, dst):
    r"""`db.clone_record(src, dst)`, but a FALSE return is fatal instead of silent.

    `arz_patcher.ArzDatabase.clone_record` returns False when the source is absent
    from `_raw_records` and writes nothing. Every call site here is preceded by an
    `lk.real()` that raises on a miss, so this is belt-and-braces - but a silently
    skipped clone inside the one function that creates the TESTHUB split is exactly
    the shape of defect this lane exists to prevent: the twin would come out
    incomplete, the four DEV placements would dangle, and the only thing left to
    notice would be V5 firing several hundred lines later with no idea why."""
    if not db.clone_record(src, dst):
        raise SystemExit(
            "[svc_loot_volume] clone_record(%s -> %s) returned False, so NOTHING was "
            "written. The source record is not in the database's raw record table. The "
            "TESTHUB twin would have shipped incomplete and the four DEV cage "
            "placements would name a record that does not exist." % (src, dst))
    return True


def already_applied(db, lk=None):
    r"""The TESTHUB twin records that already exist in `db` - i.e. the evidence that
    the R-240 wave has ALREADY run on this database.

    The twin IS the marker, and it is the only honest one available: nothing in a
    trimmed `numSpawn` equation says whether it was trimmed, so "has this wave run?"
    cannot be answered from the canonical records alone. It can be answered from the
    twin, because the twin exists only because this module authored it."""
    lk = lk or SLB.Lookup(db)
    seen = []
    for N in CAGE_CHESTS:
        if lk.real(hub_cage_chest(N)):
            seen.append(hub_cage_chest(N))
        for tier in TIERS:
            for v in VARIANTS:
                if lk.real(hub_cage_table(N, tier, v)):
                    seen.append(hub_cage_table(N, tier, v))
    return seen


def clone_hub_cage(db, lk=None, verbose=True):
    r"""Clone the whole canonical cage chain to its `_hub` twin, BEFORE the trim.

    Cloning before the trim is the entire trick: this module is registered LAST, so
    the canonical records already carry every breadth and armour-parity edit b75-b83
    made, and the twin inherits all of it plus the SHIPPED numSpawn - byte-for-byte,
    with no second copy of the tuning to keep in step. The hub is therefore
    definitionally "what shipped", and V5 proves it stayed that way.

    APPLY-ONCE, AND THE GUARD BELOW IS WHY (round-2 vet). An earlier draft of this
    docstring claimed the clone was idempotent. It is not, and the failure is silent
    and total: on a second call the "canonical" records it clones FROM are the
    already-TRIMMED ones, so the twin is re-authored at the trimmed volume and the
    TESTHUB-vs-canonical split simply ceases to exist. MEASURED on the b83 arz, a
    second `apply_wave` drifts 58 tables - `polisvault_hub_03_lb` falls from the
    shipped `*2.8/*3.2` to `*0.294/*0.336`, canonical falls a second time to
    `*0.2188/*0.25`, and the DEV farm ends up POORER than intended at ~1.04x
    canonical instead of ~9.5x. So the twin's own existence is the guard.

    Returns the list of records authored."""
    lk = lk or SLB.Lookup(db)
    seen = already_applied(db, lk)
    if seen:
        raise SystemExit(
            "[svc_loot_volume] the R-240 TESTHUB twin ALREADY EXISTS in this database "
            "(%d record(s), e.g. %s), so `clone_hub_cage` has already run on it. A "
            "second run would clone the twin off the ALREADY-TRIMMED canonical records "
            "and the canonical-vs-TESTHUB split would silently cease to exist (measured: "
            "58 tables drift, the DEV farm lands at ~1.04x canonical instead of ~9.5x). "
            "This wave is APPLY-ONCE by construction. In a build, `patches.run_registry` "
            "already asserts each module runs exactly once; if you are driving it by hand, "
            "load a fresh arz." % (len(seen), seen[0]))
    made = []
    for N in CAGE_CHESTS:
        src_chest = lk.real(canon_cage_chest(N))
        if not src_chest:
            raise SystemExit(
                "[svc_loot_volume] the canonical cage chest %s is missing, so the "
                "TESTHUB twin cannot be cloned. polis_vault authors it; this module "
                "runs after polis_vault, so a miss here means the cage chain itself "
                "did not build." % canon_cage_chest(N))
        for tier in TIERS:
            for v in VARIANTS:
                src_t = lk.real(canon_cage_table(N, tier, v))
                src_c = lk.real(canon_cage_container(N, tier, v))
                if not (src_t and src_c):
                    raise SystemExit(
                        "[svc_loot_volume] cage chain incomplete for chest %s tier %s "
                        "variant %s (table=%r container=%r). The twin must mirror the "
                        "canonical cage exactly or the DEV farm stops matching what "
                        "Will is testing." % (N, tier, v, src_t, src_c))
                dst_t, dst_c = hub_cage_table(N, tier, v), hub_cage_container(N, tier, v)
                _cloned(db, src_t, dst_t)
                db._modified.add(dst_t)
                OWN.note_write(dst_t, 'loot_volume_trim (TESTHUB twin)')
                _cloned(db, src_c, dst_c)
                db.set_field(dst_c, 'tables', dst_t)
                db._modified.add(dst_c)
                made += [dst_t, dst_c]
            src_p = lk.real(canon_cage_pool(N, tier))
            if not src_p:
                raise SystemExit(
                    "[svc_loot_volume] cage accessory pool %s is missing; the twin's "
                    "difficulty chain would dangle."
                    % canon_cage_pool(N, tier))
            dst_p = hub_cage_pool(N, tier)
            _cloned(db, src_p, dst_p)
            for i, v in enumerate(VARIANTS, start=1):
                db.set_field(dst_p, 'fixedItemName%d' % i, hub_cage_container(N, tier, v))
            db._modified.add(dst_p)
            made.append(dst_p)
        dst_chest = hub_cage_chest(N)
        _cloned(db, src_chest, dst_chest)
        db.set_field(dst_chest, 'accessory1', hub_cage_pool(N, 'n'))
        db.set_field(dst_chest, 'accessoryEpic1', hub_cage_pool(N, 'e'))
        db.set_field(dst_chest, 'accessoryLegendary1', hub_cage_pool(N, 'l'))
        db._modified.add(dst_chest)
        made.append(dst_chest)
    if verbose:
        print("  VOLUME: TESTHUB cage twin authored - %d record(s), cloned from the "
              "canonical chain BEFORE the trim so it carries the shipped numSpawn and "
              "every b75-b83 breadth/armour edit verbatim." % len(made))
    return made


def apply_wave(db, lk=None, verbose=True):
    """The whole R-240 write, in the ONE order that is correct.

    ORDER IS LOAD-BEARING and it is the reverse of the obvious one: the TESTHUB twin
    is cloned FIRST, off the untrimmed canonical records, so it captures the shipped
    volume without this module having to remember what the shipped volume WAS. Trim
    first and the twin would inherit the trim and the split would silently not exist.

    APPLY-ONCE, ENFORCED - NOT IDEMPOTENT. An earlier draft of this docstring said
    the opposite, in four places across the code and docs, and the round-2 vet
    measured it false: a second `apply_wave` on the same db drifts 58 tables. Two
    independent reasons, and neither is fixable by tidying:
      * `clone_hub_cage` would re-clone the twin off the ALREADY-TRIMMED canonical
        records, so the canonical-vs-TESTHUB split would cease to exist (the DEV farm
        lands at ~1.04x canonical instead of ~9.5x);
      * `trim_table` is MULTIPLICATIVE and the bytes carry no marker saying they have
        already been trimmed, so a second pass trims the trim (`*0.294` -> `*0.25`,
        floored). There is no way to tell an already-trimmed multiplier from a
        deliberately-small one by looking at it.
    So the guard is the twin's own existence, checked in `clone_hub_cage`, and a
    second call FAILS LOUD rather than half-working. Shipped builds were never at
    risk - `patches.run_registry` asserts each module runs exactly once, which is why
    det-2x is byte-identical - but the workflow the docs advertised did not exist.
    `tools/gate_loot_volume.py --apply` now detects the applied state and says so
    instead of corrupting its own measurement.
    """
    lk = lk or SLB.Lookup(db)
    made = clone_hub_cage(db, lk, verbose=verbose)
    lk.refresh()
    scope = scope_tables(db, lk)
    trimmed, changes = 0, []
    for _key, (real, tier, ishub) in sorted(scope.items()):
        if ishub:
            continue                      # the twin keeps the shipped volume
        ch = trim_table(db, real, tier, lk)
        if ch:
            trimmed += 1
            changes.append((real, tier, ch))
    n_canon = sum(1 for _k, (_r, _t, h) in scope.items() if not h)
    n_hub = len(scope) - n_canon
    if verbose:
        print("  VOLUME: %d of %d canonical loot table(s) trimmed; %d TESTHUB loot "
              "table(s) (of %d twin records) left at shipped volume"
              % (trimmed, n_canon, n_hub, len(made)))
    return made, changes


# ─────────────────────────────────────────────────────────────────────────────
# MEASUREMENT
# ─────────────────────────────────────────────────────────────────────────────
_IC = {'n': 'Epic', 'e': 'Legendary', 'l': 'Legendary'}


def surface_reading(d, dist, tables, weights, tier):
    """(S_eff, target-grade gear per open, P(no target-grade gear per iteration))."""
    ic = _IC[tier]
    profs = [SLD.ChestProfile(d, dist, t, 1, ic) for t in tables]
    w = [float(x) for x in (weights or [1] * len(profs))]
    tw = sum(w) or 1.0
    w = [x / tw for x in w]
    S = sum(wi * p.S for wi, p in zip(w, profs))
    leg = sum(wi * p.gear_mass() for wi, p in zip(w, profs))
    pn = 0.0
    for wi, p, t in zip(w, profs, tables):
        pn += wi * _p_none_per_iter(d, dist, t, ic)
    return S, leg, pn


def _p_none_per_iter(d, dist, table, ic):
    """P(one spawn iteration yields NO target-grade gear at all). The six loot groups
    roll independently, which is the measured engine reading `svc_loot_distribution`
    documents, so this is a product over groups - not 1 - E[count]."""
    f = d.fields(d.real(table) or table)
    q = 1.0
    for g in range(1, 7):
        c = f.get('loot%dChance' % g)
        chance = float(c[0]) / 100.0 if c else 0.0
        if chance <= 0:
            continue
        pairs = []
        for i in range(1, 7):
            nm = f.get('loot%dName%d' % (g, i))
            wt = f.get('loot%dWeight%d' % (g, i))
            if nm and isinstance(nm[0], str) and nm[0].strip():
                w = float(wt[0]) if wt else 0.0
                if w > 0:
                    pairs.append((nm[0], w))
        tot = sum(w for _p, w in pairs)
        if tot <= 0:
            continue
        p_gear = 0.0
        for p_, w in pairs:
            share = w / tot
            for it, prob in dist.dist(p_).items():
                if (str(d.gv(it, 'itemClassification') or '') == ic
                        and SLD.CLASS_TO_SLOT.get(d.cls(it))):
                    p_gear += share * prob
        q *= (1.0 - chance * p_gear)
    return q


def cage_run(d, dist, lk, tier, hub=False, truncate=False):
    """The reading a PLAYER gets: both cage chests opened once, at one difficulty.

    Returns (expected target-grade gear, P(at least one)). This is the quantity Will
    named - "from the two chests" - so it is measured as a RUN and not per chest.

    `truncate` selects the INTEGER reading of the spawn count instead of the
    continuous mean. The engine's rounding mode is unproven (`BL-R240-DEBT-5`), so
    both are computed and both are gated: the continuous reading is the higher one
    and carries the CEILINGS (V1/V6), the truncated reading is the lower one and
    carries the GUARANTEE floor (V7b). Pairing them the other way round would let
    each check be evaluated under whichever model happens to flatter it."""
    total, p_none = 0.0, 1.0
    for N in CAGE_CHESTS:
        tabs, wts = [], []
        for v, w in zip(VARIANTS, VARIANT_W):
            p = hub_cage_table(N, tier, v) if hub else canon_cage_table(N, tier, v)
            if lk.real(p):
                tabs.append(p)
                wts.append(w)
        if not tabs:
            continue
        if not truncate:
            S, leg, pn = surface_reading(d, dist, tabs, wts, tier)
            total += leg
            # One open = S iterations; the per-iteration miss probability compounds.
            p_none *= pn ** S
            continue
        # Truncated: rescale each variant's own per-open reading from its continuous
        # S to its integer S. Done PER TABLE and not on the weighted mean, because
        # int() is not linear and the three variants can truncate differently.
        ic = _IC[tier]
        tw = float(sum(wts)) or 1.0
        for t, w in zip(tabs, wts):
            share = w / tw
            real = d.real(t) or t
            prof = SLD.ChestProfile(d, dist, real, 1, ic)
            s_cont = prof.S or 1.0
            s_trunc = spawn_iterations_trunc(d, real)
            total += share * (prof.gear_mass() / s_cont) * s_trunc
            p_none *= (_p_none_per_iter(d, dist, real, ic) ** s_trunc) ** share
    return total, 1.0 - p_none


# ─────────────────────────────────────────────────────────────────────────────
# THE COMMITTED VOLUME TARGETS (R-240)
#
# Every number below was read off `py tools/gate_loot_volume.py <arz> --calibrate`
# on the shipped b83 arz `44499f56` (the DEFECT state, which every ceiling must red)
# and again with `--apply` (the FIXED state, which every ceiling must clear with
# margin). A threshold that does not red the reported defect is decoration; a
# threshold with no margin is a gate that gets switched off (the b63 1.0u lesson).
#
#   check                              b83 (defect)   R-240   threshold  reds b83  margin
#   V1 canonical gear / open, worst        23.892      2.153     2.55      yes  9x    18%
#   V6 canonical CAGE RUN, Normal          43.714      3.839     4.55      yes  9.6x  18%
#   V6 canonical CAGE RUN, Epic            28.166      2.676     3.20      yes  8.8x  20%
#   V6 canonical CAGE RUN, Legendary       36.411      3.823     4.55      yes  8.0x  19%
#   V2 TESTHUB cage run, Normal              n/a      43.714    35.00       -         20%
#   V2 TESTHUB cage run, Epic                n/a      28.166    23.00       -         18%
#   V2 TESTHUB cage run, Legendary           n/a      36.411    29.00       -         20%
#   V7 P(>=1 target-grade | canon run)     1.0000      0.9686    0.95      no*        37%
#   V7b  ... the same, INTEGER-TRUNCATED    1.0000      0.9378    0.90      no*        38%
#
#   * V7/V7b are MIRROR guards, the D6b construction: the SHIPPED build cannot red
#     them, because shipped the cage paid 36 legendaries a run and the guarantee was
#     never in doubt. The defect they exist to red is THIS LANE'S OWN over-correction
#     - a trim taken far enough to turn Will's "guaranteed 1 legendary item" into a
#     coin flip - and their margins are honestly read on the FAILURE side: 3.14% of
#     Epic runs pay nothing against the 5.00% V7 allows (37% headroom, not 2%), and
#     6.22% against the 10.00% V7b allows (38%, the same construction). Negtests N5
#     and N10 plant the over-correction and are what keep them load-bearing.
#
#   V7b IS THE CONSERVATIVE READING AND IT EXISTS BECAUSE THE MODEL IS UNPROVEN.
#   `spawn_iterations` is a continuous mean; post-trim every canonical cage table
#   truncates to exactly ONE iteration solo, so if the engine truncates, the Epic
#   guarantee is 93.78% and not the 96.86% V7 measures - BELOW V7's own 95% floor,
#   with V7 reporting green because its model never discretises. That gap shipping
#   silently is the defect. It does NOT move the ceilings: V1/V6 stay on the
#   continuous reading, which is the HIGHER one, so each check is evaluated under
#   the model that is hardest on it rather than the one that flatters it.
#
# V1's ceiling is stated PER OPEN and per tier-target-classification, so one number
# governs 60 surfaces of wildly different shapes. The worst canonical surface after
# the wave is the NORMAL cage chest_01 at 2.153 EPIC-grade pieces (Normal pays Epic,
# never Legendary - the R-180 B3 law); the richest Legendary-grade surface is the
# Legendary cage chest_01 at 2.099.
# ─────────────────────────────────────────────────────────────────────────────
CANON_MAX_GEAR_PER_OPEN = 2.55
CANON_MAX_CAGE_RUN = {'n': 4.55, 'e': 3.20, 'l': 4.55}
# Will's own words are a GUARANTEE, not an average - "you get guaranteed 1 legendary
# item". The floor is what makes that true: `MIN_SPAWN_MIN_SOLO` keeps one loot
# iteration on each chest and the 100% guaranteed row fires inside it.
MIN_P_AT_LEAST_ONE = 0.95
# ... and the same guarantee read under INTEGER TRUNCATION of the spawn count, which
# is the pessimistic engine model (see `spawn_iterations_trunc`). Set at 0.90 by the
# SAME construction as V7 and not by taste: V7 allows 5.00% of runs to pay nothing
# and the measured worst is 3.14%, so 37% headroom on the failure side; V7b allows
# 10.00% and the measured worst is 6.22%, so 38% headroom, the identical margin. The
# two floors differ because the two models do, not because one check is softer.
MIN_P_AT_LEAST_ONE_TRUNC = 0.90
# The TESTHUB half of the ruling - "on the testhub version we can spawn more that is
# fine". A FLOOR, in the opposite direction from every other number here, so a future
# lane cannot quietly trim the DEV farm to nothing while the ceilings all stay green.
HUB_MIN_CAGE_RUN = {'n': 35.00, 'e': 23.00, 'l': 29.00}


def problems(db, lk=None, report=None):
    """The R-240 contract. Returns a list of problem strings, empty when clean."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    out = []
    scope = scope_tables(db, lk)
    canon = {k: v for k, v in scope.items() if not v[2]}
    hub = {k: v for k, v in scope.items() if v[2]}

    # V4 - the equation FORM survived, on EVERY in-scope table. The build28/29/30 P0.
    # V3 - and it still spawns at least one iteration solo.
    for key, (real, tier, ishub) in sorted(scope.items()):
        for field in ('numSpawnMinEquation', 'numSpawnMaxEquation'):
            raw = lk.gv(real, field)
            if not isinstance(raw, str) or 'numberOfPlayers' not in raw:
                out.append(
                    "V4 %s.%s = %r has lost its `numberOfPlayers` term. A RunEquation "
                    "field given a bare literal evaluated to 0 in build28/29/30 and the "
                    "chest opened and dropped NOTHING - a P0 that took three builds to "
                    "find. It also silently kills co-op scaling."
                    % (SLB._n(real), field, raw))
                continue
            if parse_eq(raw) is None:
                out.append(
                    "V4 %s.%s = %r no longer has the `(<bracket>)*<M>` shape the volume "
                    "contract can read, so no gate can tell what volume this surface "
                    "ships at." % (SLB._n(real), field, raw))
        p = parse_eq(lk.gv(real, 'numSpawnMinEquation') or '')
        if p and solo_value(*p) < MIN_SPAWN_MIN_SOLO:
            out.append(
                "V3 %s spawns only %.3f loot iteration(s) at ONE player (floor %.2f). "
                "Below one iteration a container can roll ZERO items, so the 100%% "
                "guaranteed row never fires and Will's \"guaranteed 1 legendary item\" "
                "stops being a guarantee."
                % (SLB._n(real), solo_value(*p), MIN_SPAWN_MIN_SOLO))

    # V1 - the canonical ceiling, per surface.
    worst = (0.0, '')
    for label, tables, weights, tier in SAB.all_surfaces(db, lk):
        if any(is_hub(t) for t in tables):
            continue
        if all(_exempt(t) for t in tables):
            # R-247.7a: the Devourer stash is ruled SV-rich; its own gate owns it.
            # R-251:    the uber/boss hoards are ruled uber-rich; gate_uber_hoard_
            #           generosity owns them (H3 pins their exact volume).
            continue
        S, leg, _pn = surface_reading(d, dist, tables, weights, tier)
        if leg > worst[0]:
            worst = (leg, label)
        if leg > CANON_MAX_GEAR_PER_OPEN:
            out.append(
                "V1 %s pays %.2f %s gear piece(s) per open (ceiling %.2f). Will: \"we "
                "probably need to trip the loot-volume trim, especially on the steam "
                "version\"." % (label, leg, _IC[tier], CANON_MAX_GEAR_PER_OPEN))

    # V6/V7 - the CAGE RUN, which is the quantity Will actually named.
    for tier in TIERS:
        total, p_one = cage_run(d, dist, lk, tier, hub=False)
        if total <= 0:
            out.append("V6 the canonical cage pays NOTHING at tier %s - the trim has "
                       "gone past a trim." % tier)
            continue
        if total > CANON_MAX_CAGE_RUN[tier]:
            out.append(
                "V6 the canonical two-chest cage run pays %.2f %s gear piece(s) at "
                "difficulty %s (ceiling %.2f). Will asked for \"maybe from the two "
                "chests, you get guaranteed 1 legendary item\"."
                % (total, _IC[tier], tier, CANON_MAX_CAGE_RUN[tier]))
        if p_one < MIN_P_AT_LEAST_ONE:
            out.append(
                "V7 the canonical two-chest cage run pays at least one %s gear piece "
                "only %.1f%% of the time at difficulty %s (floor %.1f%%). The trim has "
                "turned Will's GUARANTEE into a coin flip."
                % (_IC[tier], 100.0 * p_one, tier, 100.0 * MIN_P_AT_LEAST_ONE))
        # V7b - the same guarantee under the PESSIMISTIC engine model. Separate from V7
        # rather than folded into it, so a report can say which reading failed: V7 alone
        # means the trim went too far under any model, V7b alone means it went too far
        # only if the engine truncates, which is a different (and cheaper) conversation.
        _tot_t, p_one_t = cage_run(d, dist, lk, tier, hub=False, truncate=True)
        if p_one_t < MIN_P_AT_LEAST_ONE_TRUNC:
            out.append(
                "V7b under INTEGER TRUNCATION of the spawn count the canonical "
                "two-chest cage run pays at least one %s gear piece only %.1f%% of the "
                "time at difficulty %s (floor %.1f%%), against %.1f%% on the continuous "
                "reading V7 uses. The engine's rounding mode is unproven "
                "(BL-R240-DEBT-5), so the guarantee has to hold under the pessimistic "
                "one too, or the PASS line is quoting a model instead of a drop rate."
                % (_IC[tier], 100.0 * p_one_t, tier, 100.0 * MIN_P_AT_LEAST_ONE_TRUNC,
                   100.0 * p_one))

    # V2/V5 - the TESTHUB half. Only asserted once the twin exists, so a db built
    # before this lane is not retro-failed; V5's own absence check is what makes
    # "the twin quietly stopped being authored" visible instead of silent.
    if hub:
        for tier in TIERS:
            total, _p = cage_run(d, dist, lk, tier, hub=True)
            if total < HUB_MIN_CAGE_RUN[tier]:
                out.append(
                    "V2 the TESTHUB cage run pays only %.2f %s gear piece(s) at "
                    "difficulty %s (FLOOR %.2f). Will: \"on the testhub version we can "
                    "spawn more that is fine\" - the DEV farm is not allowed to be "
                    "trimmed with canonical."
                    % (total, _IC[tier], tier, HUB_MIN_CAGE_RUN[tier]))
        for N in CAGE_CHESTS:
            for tier in TIERS:
                for v in VARIANTS:
                    ct, ht = canon_cage_table(N, tier, v), hub_cage_table(N, tier, v)
                    cr, hr = lk.real(ct), lk.real(ht)
                    if not (cr and hr):
                        out.append("V5 the cage twin is incomplete: %s / %s" % (ct, ht))
                        continue
                    cs = SLD.spawn_iterations(d, cr)
                    hs = SLD.spawn_iterations(d, hr)
                    if not hs > cs:
                        out.append(
                            "V5 %s spawns %.3f iteration(s) and its TESTHUB twin %s "
                            "spawns %.3f - the twin must be STRICTLY richer or the "
                            "split does not exist and the four DEV duplicates are "
                            "farming the trimmed canonical records."
                            % (SLB._n(cr), cs, SLB._n(hr), hs))
    if report is not None:
        report.update({'scope': len(scope), 'canonical': len(canon), 'hub': len(hub),
                       'worst_surface': worst})
    return out


def calibrate(db, lk=None):
    """Print the worst OBSERVED value per check, so every constant above is derived
    from measurement instead of taste, and two builds can be compared in one command."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    rows = []
    for label, tables, weights, tier in SAB.all_surfaces(db, lk):
        S, leg, _pn = surface_reading(d, dist, tables, weights, tier)
        rows.append((leg, S, label, tier, any(is_hub(t) for t in tables)))
    rows.sort(key=lambda r: -r[0])
    print('\n=== R-240 VOLUME CALIBRATION ===')
    print('  %-46s %3s %7s %9s' % ('surface', 'tie', 'S_eff', 'gear/open'))
    for leg, S, label, tier, ishub in rows:
        print('  %-46s %3s %7.3f %9.3f%s'
              % (label[:46], tier, S, leg, '   [TESTHUB]' if ishub else ''))
    cw = [r for r in rows if not r[4]]
    if cw:
        print('  worst CANONICAL gear/open: %.3f on %s (V1 ceiling %.2f)'
              % (cw[0][0], cw[0][2], CANON_MAX_GEAR_PER_OPEN))
    # BOTH readings, side by side, because the engine's rounding mode is unproven and
    # a single printed number would be read as a measurement (BL-R240-DEBT-5).
    print('  cage RUN - continuous mean S vs INTEGER-TRUNCATED S (both gated: V6/V7 '
          'on the first, V7b on the second)')
    for tier in TIERS:
        tot, p1 = cage_run(d, dist, lk, tier, hub=False)
        tot_t, p1_t = cage_run(d, dist, lk, tier, hub=False, truncate=True)
        htot, _ = cage_run(d, dist, lk, tier, hub=True)
        htot_t, _ = cage_run(d, dist, lk, tier, hub=True, truncate=True)
        print('    [%s] canonical %.3f %s gear P(>=1) %.4f | trunc %.3f P(>=1) %.4f '
              '|| TESTHUB %.3f | trunc %.3f'
              % (tier, tot, _IC[tier], p1, tot_t, p1_t, htot, htot_t))
