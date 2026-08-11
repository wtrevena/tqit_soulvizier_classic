r"""svc_loot_volume.py - THE DROP-VOLUME CONTRACT (Will 2026-08-11, R-230).

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
  one" - so R-230 re-anchors D7's volume reference and floor TOGETHER, preserving its
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
is forbidden to touch. Registered as `BL-R230-DEBT-1`.

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
# THE LADDER (R-230). TWO committed constants and a floor; every per-table
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
# RANK IS PRESERVED, NOT FLATTENED. The trim is MULTIPLICATIVE on each table's own
# shipped multiplier, so the shipped richness ORDER survives: the blood-cave mega
# chest stays the richest surface in the mod, cage chest_03 stays richer than
# chest_01, and the apex orb stays richer than a level-banded one - which is the
# b79 precedent Will asked to keep ("orbs stay generous relative to chests"). What
# the FLOOR below does to that order is measured and stated in the gate's own
# report rather than hidden: the thinnest orbs are already so close to one
# iteration that the floor lifts them off the multiplicative ladder, so the spread
# COMPRESSES. That is a mechanical consequence of a discrete spawn count, not a
# design choice, and V-CALIBRATE prints both numbers so it can never be silent.
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
    """The R-230 multipliers for one table: the shipped pair scaled by this tier's
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
    """{norm: (real, tier, is_hub)} for every loot table R-230 governs."""
    lk = lk or SLB.Lookup(db)
    out = {}
    for _label, tables, _w, tier in SAB.all_surfaces(db, lk):
        for t in tables:
            real = lk.real(t)
            if not real:
                continue
            out[SLB._n(real)] = (real, tier, is_hub(real))
    return out


def trim_table(db, real, tier, lk=None):
    """Apply the R-230 trim to ONE table. Returns a list of change strings.

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
def clone_hub_cage(db, lk=None, verbose=True):
    r"""Clone the whole canonical cage chain to its `_hub` twin, BEFORE the trim.

    Cloning before the trim is the entire trick: this module is registered LAST, so
    the canonical records already carry every breadth and armour-parity edit b75-b83
    made, and the twin inherits all of it plus the SHIPPED numSpawn - byte-for-byte,
    with no second copy of the tuning to keep in step. The hub is therefore
    definitionally "what shipped", and V5 proves it stayed that way.

    Returns the list of records authored (idempotent: a re-run rewrites the same
    bytes, which is what makes the det-2x build identical)."""
    lk = lk or SLB.Lookup(db)
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
                db.clone_record(src_t, dst_t)
                db._modified.add(dst_t)
                OWN.note_write(dst_t, 'loot_volume_trim (TESTHUB twin)')
                db.clone_record(src_c, dst_c)
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
            db.clone_record(src_p, dst_p)
            for i, v in enumerate(VARIANTS, start=1):
                db.set_field(dst_p, 'fixedItemName%d' % i, hub_cage_container(N, tier, v))
            db._modified.add(dst_p)
            made.append(dst_p)
        dst_chest = hub_cage_chest(N)
        db.clone_record(src_chest, dst_chest)
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
    """The whole R-230 write, in the ONE order that is correct.

    ORDER IS LOAD-BEARING and it is the reverse of the obvious one: the TESTHUB twin
    is cloned FIRST, off the untrimmed canonical records, so it captures the shipped
    volume without this module having to remember what the shipped volume WAS. Trim
    first and the twin would inherit the trim and the split would silently not exist.

    Idempotent: re-running writes the same bytes (the trim of an already-trimmed
    multiplier is floored to the same value, and the clone is a fresh copy), which is
    what lets the standalone gate run `--apply` against a BUILT arz.
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


def cage_run(d, dist, lk, tier, hub=False):
    """The reading a PLAYER gets: both cage chests opened once, at one difficulty.

    Returns (expected target-grade gear, P(at least one)). This is the quantity Will
    named - "from the two chests" - so it is measured as a RUN and not per chest."""
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
        S, leg, pn = surface_reading(d, dist, tabs, wts, tier)
        total += leg
        # One open = S iterations; the per-iteration miss probability compounds.
        p_none *= pn ** S
    return total, 1.0 - p_none


# ─────────────────────────────────────────────────────────────────────────────
# THE COMMITTED VOLUME TARGETS (R-230)
#
# Every number below was read off `py tools/gate_loot_volume.py <arz> --calibrate`
# on the shipped b83 arz `44499f56` (the DEFECT state, which every ceiling must red)
# and again with `--apply` (the FIXED state, which every ceiling must clear with
# margin). A threshold that does not red the reported defect is decoration; a
# threshold with no margin is a gate that gets switched off (the b63 1.0u lesson).
#
#   check                              b83 (defect)   R-230   threshold  reds b83  margin
#   V1 canonical gear / open, worst        23.892      2.153     2.55      yes  9x    18%
#   V6 canonical CAGE RUN, Normal          43.714      3.839     4.55      yes  9.6x  18%
#   V6 canonical CAGE RUN, Epic            28.166      2.676     3.20      yes  8.8x  20%
#   V6 canonical CAGE RUN, Legendary       36.411      3.823     4.55      yes  8.0x  19%
#   V2 TESTHUB cage run, Normal              n/a      43.714    35.00       -         20%
#   V2 TESTHUB cage run, Epic                n/a      28.166    23.00       -         18%
#   V2 TESTHUB cage run, Legendary           n/a      36.411    29.00       -         20%
#   V7 P(>=1 target-grade | canon run)     1.0000      0.9686    0.95      no*        37%
#
#   * V7 is a MIRROR guard, the D6b construction: the SHIPPED build cannot red it,
#     because shipped the cage paid 36 legendaries a run and the guarantee was never
#     in doubt. The defect V7 exists to red is THIS LANE'S OWN over-correction - a
#     trim taken far enough to turn Will's "guaranteed 1 legendary item" into a coin
#     flip - and its margin is honestly read on the FAILURE side: 3.14% of runs pay
#     nothing at Epic against the 5.00% the floor allows, so 37% headroom, not 2%.
#     Negtest N5 plants exactly that over-correction and N5 is what keeps it load-bearing.
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
# The TESTHUB half of the ruling - "on the testhub version we can spawn more that is
# fine". A FLOOR, in the opposite direction from every other number here, so a future
# lane cannot quietly trim the DEV farm to nothing while the ceilings all stay green.
HUB_MIN_CAGE_RUN = {'n': 35.00, 'e': 23.00, 'l': 29.00}


def problems(db, lk=None, report=None):
    """The R-230 contract. Returns a list of problem strings, empty when clean."""
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
    print('\n=== R-230 VOLUME CALIBRATION ===')
    print('  %-46s %3s %7s %9s' % ('surface', 'tie', 'S_eff', 'gear/open'))
    for leg, S, label, tier, ishub in rows:
        print('  %-46s %3s %7.3f %9.3f%s'
              % (label[:46], tier, S, leg, '   [TESTHUB]' if ishub else ''))
    cw = [r for r in rows if not r[4]]
    if cw:
        print('  worst CANONICAL gear/open: %.3f on %s (V1 ceiling %.2f)'
              % (cw[0][0], cw[0][2], CANON_MAX_GEAR_PER_OPEN))
    for tier in TIERS:
        tot, p1 = cage_run(d, dist, lk, tier, hub=False)
        htot, _ = cage_run(d, dist, lk, tier, hub=True)
        print('  cage RUN [%s]: canonical %.3f %s gear, P(>=1) %.4f | TESTHUB %.3f'
              % (tier, tot, _IC[tier], p1, htot))
