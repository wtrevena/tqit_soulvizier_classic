r"""svc_orb_legendary.py - THE UBER-ORB LEGENDARY/BLUE CONTRACT BY DIFFICULTY
(Will 2026-08-12, R-242). This SUPERSEDES R-241's flat 21.2% apex demotion and
CLOSES BL-R241-DEBT-1.

WILL, VERBATIM (2026-08-12), part 1
-----------------------------------
  "all the orbs that uber monsters drop should have a 50% chance of dropping a
   legendary item on epic, a 75% of dropping a legendary item on legendary, a 0%
   chance of dropping a legendary item on normal, but a 75% chance of dropping a
   blue item on normal (this is a sub legendary item, idk what the name of this
   class of item is but they show up blue)"

WILL, VERBATIM (2026-08-12), part 2 (the exclusion)
---------------------------------------------------
  "Note that Leinth and the toxeus variants keep their current higher / better orbs
   / better drop rates / more loot"

WHAT "BLUE" IS, PROVEN FROM THE BYTES
-------------------------------------
"blue" = itemClassification Epic, the tier directly below Legendary (the standard TQ
ladder Broken < Common < Magical < Rare < Epic < Legendary; Epic renders blue,
Legendary purple/red, engine-baked). MEASURED on the build85 arz: on every NORMAL orb
the four unique-gear rows resolve to Epic-classification records with ZERO legendary
GEAR, and on the EPIC/LEGENDARY orbs those SAME rows resolve to Legendary. So "the blue
item a Normal orb drops" IS the Epic-classification gear it pays, and raising "75% blue
on normal" means raising the chance the Normal orb's Epic gear rows fire.

HOW THE TARGET IS REACHED - THE LOAD-BEARING CORRECTION TO THE RULING'S ASSUMPTION
---------------------------------------------------------------------------------
There is NO single "legendary row" whose chance is the legendary chance. The four
unique-GEAR rows - loot1 (weapons), loot2 (torso/head), loot5 (legs/arms), loot6
(shield) - each fire at their own loot{g}Chance and each pay a per-tier mix, so the
legendary/blue output is EMERGENT across them over S spawn iterations. Setting loot4
(amulet/relic/ring/formula) to 50% would yield ~2.5% legendary, not 50%; loot4 carries
almost no legendary mass. So Will's "50% chance of dropping a legendary item" is read
faithfully as the observable orb behaviour:

    P(at least one legendary item per orb open) = the target,

and the lever is a UNIFORM per-(table, difficulty) chance on the four gear rows
loot1/2/5/6. Uniform because it preserves the weapon:armour:shield mass ratio (R-181
D3/D4/D6 parity) and RAISING chances only strengthens the D7b armour-per-iteration
floor, so the change is armour-parity-safe by construction and touches only
loot{g}Chance - the exact field domain R-241's scope proof already permitted.

THE PARTITION - GENERAL vs EXCLUDED, DERIVED NOT TYPED
------------------------------------------------------
The 18 in-scope uber-orb loot tables (svc_orb_breadth's own derived scope) split:
  * EXCLUDED (3): svc_uberorb_apex_{n,e,l}01c - the shared loot of the Toxeus roster
    (genericbossorb_05: um_toxeus_21/99, um_bloodtoxeus_99, um_toxeus_enslaver_99,
    um_toxeus_hunt_99/_l_99) AND Leinth (bosschest_leinth_0N). DERIVED: a table is
    EXCLUDED iff every uber chain that reaches it has carriers that are ALL Toxeus (or
    Leinth) records; cross-checked against the pinned apex set so a NEW apex consumer
    reds instead of silently shrinking scope. These keep their build85 bytes verbatim
    (Will part 2), which means the wave STILL demotes their guaranteed relic row 100 ->
    21.2 exactly as R-241 did - that IS their build85 state, and letting it revert to
    100 would both change the bytes and re-arm a guaranteed legendary row.
  * GENERAL (15): the other per-difficulty records (uberorb_default_* and
    boss_charon_*01b). These get the 0/50/75 legendary + 75 blue-on-normal treatment.

THE DIFFICULTY MECHANISM
------------------------
Each difficulty of each general orb is a physically SEPARATE FixedItemLoot record; the
difficulty is selected UPSTREAM by the proxy's accessory1/accessoryEpic1/
accessoryLegendary1 slot, so the row chances are set DIRECTLY on each of the 15 distinct
records (the relic-tiering-approved pattern, NOT a container game-mode array).

THE HONEST RESIDUE, STATED NOT HIDDEN (`BL-R242-DEBT-1`)
-------------------------------------------------------
Freezing the excluded apex at its build85 numbers makes it WEAKER than the general orbs
on Legendary legendary-chance: apex P(>=1 legendary) = 60.9%, general target = 75%. That
is an inversion of Will's "keep their better orbs", and it is the literal instruction of
this lane (byte-unchanged exclusion). The apex's remaining edge is volume (S 1.131 vs
1.125) and its richer loot4 (21.2 vs 12.7 relics/jewelry/formulae). Whether to accept
the inversion or bump the apex above the general target is Will's call, priced as
BL-R242-DEBT-1; this gate PRINTS it on every run and does NOT red on it. Also disclosed:
raising the gear rows raises total gear VOLUME per open (partially re-inflating R-240's
trim, ~+45% gear on Legendary) - intrinsic to "more legendary chance" and the
smallest-blast-radius lever.

Shared by `tools/gate_orb_legendary.py` (standalone), the in-build gate
`tools/patches/orb_legendary_chance.verify()` and
`tools/debug/negtest_orb_legendary.py`, so the three can never disagree.
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import svc_loot_breadth as SLB
import svc_loot_distribution as SLD
import svc_loot_ownership as OWN
import svc_loot_volume as SLV
import svc_orb_breadth as SOB

LEGENDARY = 'Legendary'
EPIC = 'Epic'
TIERS = ('n', 'e', 'l')
TIER_NAME = {'n': 'Normal', 'e': 'Epic', 'l': 'Legendary'}

# The equipment classes - a legendary item is GEAR iff its engine Class is one a player
# wears or wields (the ItemArtifact / ItemArtifactFormula mercenary scrolls and arcane
# formulae are NOT gear, and are the base-game leak that makes "0% legendary on Normal"
# read 0.1-0.35% if you count everything). Sourced from svc_loot_distribution so the two
# contracts mean the same thing by "gear".
GEAR_CLASSES = frozenset(SLD.CLASS_TO_SLOT)

# ─────────────────────────────────────────────────────────────────────────────
# THE TARGETS (Will's numbers) AND THE BANDS (design intent, +/-5pp per the recon).
# The calibration aims each general table at the exact ruling number; the gate holds
# the band around it. Normal's legendary target is GEAR-legendary = 0 (the tier law:
# a Normal orb's gear rows carry zero Legendary gear), asserted as <= NORMAL_LEG_GEAR_MAX
# so the base-game scroll/formula leak on loot4 cannot red a check about GEAR.
# ─────────────────────────────────────────────────────────────────────────────
TARGET_CLS = {'n': EPIC, 'e': LEGENDARY, 'l': LEGENDARY}   # the class each tier targets
TARGET_P = {'n': 0.75, 'e': 0.50, 'l': 0.75}               # Will's per-difficulty numbers
BAND_HALF = 0.05                                           # +/-5pp gate band
NORMAL_LEG_GEAR_MAX = 0.01                                 # "0% legendary on normal" (GEAR)

# The four unique-GEAR rows the calibration moves, and NOTHING else. loot3 (potions) and
# loot4 (amulet/relic/ring/formula) are left verbatim, so the relic law and the loot4
# family value survive and the volume lever (numSpawn) is never touched.
GEAR_ROWS = (1, 2, 5, 6)
CHANCE_DECIMALS = 1          # write calibrated chances at one decimal (the 12.7/21.2 style)
CHANCE_MAX = 100.0

# An orb must still be worth opening - the mirror that stops a future retune from meeting
# the bands the cheap way (an empty box technically pays no legendary). This wave RAISES
# chances so it cannot trip this itself; it is a guard for the gate, negative-tested.
ORB_MIN_DROPS_PER_OPEN = 1.50

# ─────────────────────────────────────────────────────────────────────────────
# THE EXCLUDED APEX - Leinth + Toxeus, kept byte-identical to build85 (Will part 2).
# PINNED so the derived partition is cross-checked against a known roster: a new apex
# consumer (a general orb rewired onto these tables, or a fourth apex table) makes the
# derived set differ from the pin and reds, rather than silently changing scope.
# The BYTE-UNCHANGED assertion is sufficient over just these fields because the wave's
# ONLY field domain is per-table loot{g}Chance: members, weights and numSpawn on the apex
# come from earlier modules identical to build85 and this wave never writes them, so
# pinning the apex loot profile + numSpawn proves the whole record unchanged.
# ─────────────────────────────────────────────────────────────────────────────
APEX_PINNED = {
    'n': r'records\item\loottables\svc\svc_uberorb_apex_n01c.dbr',
    'e': r'records\item\loottables\svc\svc_uberorb_apex_e01c.dbr',
    'l': r'records\item\loottables\svc\svc_uberorb_apex_l01c.dbr',
}
# The build85 bytes each apex table must still carry after the wave (MEASURED on
# 5a6d63a9). loot4 = 21.2 is the R-241 family-demotion value, retained.
APEX_EXPECTED_CHANCE = {1: 40.0, 2: 40.0, 3: 10.0, 4: 21.2, 5: 40.0, 6: 40.0}
APEX_EXPECTED_NUMSPAWN = {
    'n': ('(3+(1.6*numberOfPlayers))*0.2283', '(3+(1.6*numberOfPlayers))*0.2609'),
    'e': ('(3+(1.6*numberOfPlayers))*0.2283', '(3+(1.6*numberOfPlayers))*0.2609'),
    'l': ('(3+(1.6*numberOfPlayers))*0.231', '(3+(1.6*numberOfPlayers))*0.2609'),
}
CHANCE_TOL = 1e-4

# The apex ORB OUTPUT each excluded table must still produce, MEASURED on build85
# (5a6d63a9): P(>=1 blue/Epic) and P(>=1 legendary) per open. Pinning the chances alone
# proves the apex TABLE is unchanged, but a shared unique master the apex READS (e.g.
# svc_unique_weapons_l01, shared with the general orbs) could be retuned by a future
# breadth/distribution lane and leak into the apex output while the apex table's own bytes
# stay put. G3b freezes the apex behaviour too, so such a leak reds here (and, when a
# baseline arz is passed, the reading is recomputed from it rather than trusting the pin).
APEX_EXPECTED_READING = {
    'n': {EPIC: 0.6897, LEGENDARY: 0.0011},
    'e': {EPIC: 0.3478, LEGENDARY: 0.4895},
    'l': {EPIC: 0.1768, LEGENDARY: 0.6090},
}
APEX_READING_TOL = 0.02      # 2pp - absorbs nothing this wave does, reds a real leak

# The demotion target for the apex guaranteed relic row, DERIVED (family_chance) and
# cross-checked against the value this contract was measured on (R-241's 21.2).
FAMILY_CHANCE_EXPECTED = {4: 21.2}
FAMILY_CHANCE_TOL = 1e-6

# The predicate that puts a table in the EXCLUDED set: every carrier of every chain that
# reaches it is a Toxeus variant or Leinth.
_EXCLUDED_CARRIER_TOKENS = ('toxeus', 'leinth')


# ─────────────────────────────────────────────────────────────────────────────
# SCOPE + PARTITION
# ─────────────────────────────────────────────────────────────────────────────
def orb_tables(db, lk=None, base_rows=None, scope=None):
    """{norm(table): (real, tier)} for every in-scope uber-orb loot table (all 18).

    DERIVED from svc_orb_breadth, never typed - same derivation R-220's own gate uses.
    `scope` lets a caller pass an already-derived map (deriving costs a full 51k scan).
    """
    if scope is not None:
        return scope
    lk = lk or SLB.Lookup(db)
    chains = SOB.orb_chains(db, lk, base_rows)
    return SOB.scope_tables(db, lk, base_rows, chains)


def _is_excluded_carrier(name):
    n = SLB._n(name).lower()
    return any(tok in n for tok in _EXCLUDED_CARRIER_TOKENS)


def table_carriers(db, lk=None, base_rows=None, chains=None):
    """{norm(table): [carrier record, ...]} - every uber carrier whose chain reaches the
    table, aggregated over all difficulty slots. DERIVED from svc_orb_breadth.orb_chains.
    """
    lk = lk or SLB.Lookup(db)
    chains = SOB.orb_chains(db, lk, base_rows) if chains is None else chains
    out = {}
    for (_proxy, _tier, _pool, _chest, table, carriers) in chains:
        if not table:
            continue
        out.setdefault(SLB._n(table), []).extend(carriers)
    return out


def partition(db, lk=None, base_rows=None, scope=None, carriers=None):
    """(general, excluded) each a {norm(table): (real, tier)} map.

    EXCLUDED = every table whose chains' carriers are ALL Toxeus/Leinth. The derived
    excluded set is cross-checked against APEX_PINNED by `partition_problems`; here it is
    derived cleanly so the write side and the gate share one rule.
    """
    lk = lk or SLB.Lookup(db)
    scope = orb_tables(db, lk, base_rows, scope)
    carriers = table_carriers(db, lk, base_rows) if carriers is None else carriers
    general, excluded = {}, {}
    for k, (real, tier) in scope.items():
        cars = carriers.get(k, [])
        is_excl = bool(cars) and all(_is_excluded_carrier(c) for c in cars)
        (excluded if is_excl else general)[k] = (real, tier)
    return general, excluded


def partition_problems(db, lk=None, base_rows=None, scope=None, carriers=None):
    """The ROSTER_PINNED cross-check: the DERIVED excluded set must equal the pinned apex
    set. A mismatch means either a new apex consumer appeared (a table wrongly excluded)
    or a general table picked up a Toxeus/Leinth carrier (wrongly excluded) - either way a
    human decision, not a silent scope change.
    """
    lk = lk or SLB.Lookup(db)
    _general, excluded = partition(db, lk, base_rows, scope, carriers)
    derived = {SLB._n(real) for (real, _t) in excluded.values()}
    pinned = set()
    for _tier, path in APEX_PINNED.items():
        real = lk.real(path)
        pinned.add(SLB._n(real) if real else SLB._n(path))
    out = []
    for extra in sorted(derived - pinned):
        out.append("X0 DERIVED-EXCLUDED table %s is not in the pinned apex set. A general "
                   "orb has been rewired onto Toxeus/Leinth loot, or a new apex table "
                   "exists. Decide deliberately and update APEX_PINNED." % extra)
    for missing in sorted(pinned - derived):
        out.append("X0 PINNED apex table %s is no longer derived-excluded (its carriers "
                   "are no longer all Toxeus/Leinth). The exclusion Will ruled has been "
                   "broken, or the roster moved. Re-derive and update APEX_PINNED." % missing)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# THE MODEL - per-classification, so the same code reads legendary AND blue(Epic)
# ─────────────────────────────────────────────────────────────────────────────
def group_profile(d, dist, table):
    """[(g, chance, shares)] for every LIVE loot group of `table`, where `shares` is
    {classification: P(the item this group pays is that classification)} resolved through
    the whole loot graph. Legendary is additionally split into 'LegGear' / 'LegArtifact'
    so a Normal orb's GEAR-legendary (the tier-law zero) is measurable apart from the
    base-game scroll/formula leak.
    """
    f = d.fields(table)
    out = []
    for g in range(1, 7):
        c = f.get('loot%dChance' % g)
        chance = float(c[0]) / 100.0 if c else 0.0
        pairs = []
        for i in range(1, 7):
            nm = f.get('loot%dName%d' % (g, i))
            wt = f.get('loot%dWeight%d' % (g, i))
            if nm and isinstance(nm[0], str) and nm[0].strip():
                w = float(wt[0]) if wt else 0.0
                if w > 0:
                    pairs.append((nm[0], w))
        tot = sum(w for _p, w in pairs)
        if chance <= 0 or tot <= 0:
            continue
        shares = {}
        for p_, w in pairs:
            share = w / tot
            for it, q in dist.dist(p_).items():
                cls = str(d.gv(it, 'itemClassification') or '')
                shares[cls] = shares.get(cls, 0.0) + share * q
                if cls == LEGENDARY:
                    key = ('LegGear' if str(d.gv(it, 'Class') or '') in GEAR_CLASSES
                           else 'LegArtifact')
                    shares[key] = shares.get(key, 0.0) + share * q
        out.append((g, chance, shares))
    return out


def _p_at_least_one(gs, S, key, override=None):
    """P(>=1 item whose share-key is `key`) over S independent spawn iterations.

    `override` = {group index: chance} temporarily replaces those groups' chances (used by
    the calibration to vary the gear rows without re-resolving the loot graph - the shares
    do not depend on chance).
    """
    miss = 1.0
    for (g, c, sh) in gs:
        cc = override.get(g, c) if override else c
        miss *= (1.0 - cc * sh.get(key, 0.0))
    return 1.0 - miss ** max(S, 0.0)


def reading(d, dist, table, gs=None, S=None):
    """A dict of every reading the gate and calibration report for one table.

    Keys: drops, p_epic, p_leg, p_leg_gear, e_leg, S. All under the CONTINUOUS spawn
    model (the pessimistic side of a two-sided band: P is monotone in S, so the larger
    continuous reading is the conservative one for both edges of a band around a target).
    """
    S = SLD.spawn_iterations(d, table) if S is None else S
    gs = group_profile(d, dist, table) if gs is None else gs
    drops = S * sum(c for (_g, c, _s) in gs)
    e_leg = S * sum(c * sh.get(LEGENDARY, 0.0) for (_g, c, sh) in gs)
    return {
        'drops': drops,
        'p_epic': _p_at_least_one(gs, S, EPIC),
        'p_leg': _p_at_least_one(gs, S, LEGENDARY),
        'p_leg_gear': _p_at_least_one(gs, S, 'LegGear'),
        'p_leg_artifact': _p_at_least_one(gs, S, 'LegArtifact'),
        'e_leg': e_leg,
        'S': S,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CALIBRATION (general tables) - solve the uniform gear-row chance that hits the target
# ─────────────────────────────────────────────────────────────────────────────
def calibrate_chance(d, dist, real, tier, gs=None, S=None):
    """The uniform loot1/2/5/6 chance (percent, rounded to CHANCE_DECIMALS) that puts this
    general table's P(>=1 target-classification) at Will's number for its difficulty.

    DERIVED per table from its own bytes by bisection on the emergent model - not a typed
    constant - so a content retune that shifts a table's per-tier mix moves the calibrated
    chance with it. P is monotone increasing in the gear-row chance, so bisection is exact.
    """
    gs = group_profile(d, dist, real) if gs is None else gs
    S = SLD.spawn_iterations(d, real) if S is None else S
    cls, target = TARGET_CLS[tier], TARGET_P[tier]

    def P(x_frac):
        return _p_at_least_one(gs, S, cls, override={g: x_frac for g in GEAR_ROWS})

    lo, hi = 0.0, CHANCE_MAX / 100.0
    # If even a full 100% gear row cannot reach the target, return the max and let the
    # band check red - a silent under-shoot would be the expensive kind of wrong.
    if P(hi) < target:
        return CHANCE_MAX
    for _ in range(64):
        mid = (lo + hi) / 2.0
        if P(mid) < target:
            lo = mid
        else:
            hi = mid
    return round(((lo + hi) / 2.0) * 100.0, CHANCE_DECIMALS)


# ─────────────────────────────────────────────────────────────────────────────
# THE APEX GUARANTEED-ROW DEMOTION (retained from R-241, for the EXCLUDED tables only)
# ─────────────────────────────────────────────────────────────────────────────
def guaranteed_legendary_rows(d, dist, tables):
    """[(real, tier, group, chance, legendary_share)] - every loot group in `tables` that
    fires on EVERY spawn iteration AND can pay a legendary. In a fresh build these are the
    3 apex group-4 relic rows at chance 100; demoting them to the family value is what
    keeps the apex byte-identical to build85 (Will part 2)."""
    out = []
    for _k, (real, tier) in sorted(tables.items()):
        for (g, chance, sh) in group_profile(d, dist, real):
            if chance >= 1.0 and sh.get(LEGENDARY, 0.0) > 0.0:
                out.append((real, tier, g, chance, sh.get(LEGENDARY, 0.0)))
    return out


def family_chance(d, dist, tables):
    """{group index: the richest NON-guaranteed chance that row carries across the orb
    family} - the demotion target for the apex guaranteed row, DERIVED from the bytes.
    Group 4 exists across the family at 12.7 / 21.2, so this returns 21.2 for group 4."""
    out = {}
    for _k, (real, _tier) in sorted(tables.items()):
        for (g, chance, _sh) in group_profile(d, dist, real):
            if chance < 1.0:
                out[g] = max(out.get(g, 0.0), chance)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# THE WAVE (write side)
# ─────────────────────────────────────────────────────────────────────────────
def apply_wave(db, lk=None, base_rows=None, verbose=True, scope=None, carriers=None):
    """Calibrate the 15 general orbs and demote the 3 apex guaranteed rows.

    Returns (general_changes, apex_changes):
      general_changes = [(real, tier, [(g, old, new), ...])]
      apex_changes    = [(real, tier, group, old_chance, new_chance)]
    """
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    general, excluded = partition(db, lk, base_rows, scope, carriers)

    # ── the general orbs: uniform gear-row chance to the per-difficulty target ──
    general_changes = []
    for _k, (real, tier) in sorted(general.items(), key=lambda kv: (kv[1][1], kv[0])):
        gs = group_profile(d, dist, real)
        S = SLD.spawn_iterations(d, real)
        x = calibrate_chance(d, dist, real, tier, gs, S)
        moves = []
        for g in GEAR_ROWS:
            old = float(d.fields(real).get('loot%dChance' % g, [0.0])[0])
            if abs(old - x) > CHANCE_TOL:
                db.set_field(real, 'loot%dChance' % g, x)
                moves.append((g, old, x))
        if moves:
            db._modified.add(real)
            OWN.note_write(real, 'orb_legendary_chance')
            general_changes.append((real, tier, moves))
            if verbose:
                print("    %-30s [%s] loot%s -> %.1f%% (P(%s) target %.0f%%)"
                      % (SLB._n(real).rsplit('\\', 1)[-1], tier,
                         '/'.join(str(g) for g in GEAR_ROWS), x,
                         TARGET_CLS[tier], 100.0 * TARGET_P[tier]))

    # ── the apex: demote the guaranteed relic row to the family value (byte == build85) ──
    d.refresh()
    dist = SLD.Distributor(d)
    apex_changes = []
    rows = guaranteed_legendary_rows(d, dist, excluded)
    fam = family_chance(d, dist, orb_tables(db, lk, base_rows, scope))
    for (real, tier, g, chance, leg) in rows:
        target = fam.get(g)
        if target is None:
            raise SystemExit(
                "[svc_orb_legendary] apex group %d is guaranteed on %s and no orb table "
                "carries that row at a non-guaranteed chance - no family value to demote "
                "to. Give the row a non-guaranteed sibling or make the target a Will-ruled "
                "constant." % (g, SLB._n(real)))
        expected = FAMILY_CHANCE_EXPECTED.get(g)
        if expected is not None and abs(100.0 * target - expected) > FAMILY_CHANCE_TOL:
            raise SystemExit(
                "[svc_orb_legendary] the DERIVED apex demotion target for group %d is "
                "%.4f%% but this contract was measured against %.4f%%. The orb family was "
                "retuned: re-measure and update FAMILY_CHANCE_EXPECTED deliberately."
                % (g, 100.0 * target, expected))
        db.set_field(real, 'loot%dChance' % g, 100.0 * target)
        db._modified.add(real)
        OWN.note_write(real, 'orb_legendary_chance')
        apex_changes.append((real, tier, g, chance, target))
        if verbose:
            print("    %-30s [%s] loot%dChance %.1f%% -> %.1f%% (excluded apex, kept at "
                  "its build85 family value)"
                  % (SLB._n(real).rsplit('\\', 1)[-1], tier, g,
                     100.0 * chance, 100.0 * target))
    return general_changes, apex_changes


def already_applied(db, lk=None, base_rows=None, scope=None, carriers=None):
    """The work this wave would still do. Empty == already applied (or never needed).

    True when the general gear rows already sit at their calibrated value AND no apex
    guaranteed row remains. Measured, not claimed - the apply-once guard idiom.
    """
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    general, excluded = partition(db, lk, base_rows, scope, carriers)
    pending = []
    for _k, (real, tier) in sorted(general.items()):
        gs = group_profile(d, dist, real)
        S = SLD.spawn_iterations(d, real)
        x = calibrate_chance(d, dist, real, tier, gs, S)
        for g in GEAR_ROWS:
            old = float(d.fields(real).get('loot%dChance' % g, [0.0])[0])
            if abs(old - x) > CHANCE_TOL:
                pending.append((real, tier, g))
                break
    pending.extend(guaranteed_legendary_rows(d, dist, excluded))
    return pending


# ─────────────────────────────────────────────────────────────────────────────
# THE CONTRACT (audit side, shared by every gate)
# ─────────────────────────────────────────────────────────────────────────────
def problems(db, lk=None, base_rows=None, report=None, scope=None, carriers=None):
    """R-242. Returns a list of problem strings, empty when clean.

    General (15): per-difficulty legendary/blue band, Normal GEAR-legendary <= 1%.
    Excluded (3): byte-unchanged vs build85 (loot profile + numSpawn pinned).
    Both:         the orb still pays (drops floor) - the empty-box mirror.
    """
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    out = []

    scope_map = orb_tables(db, lk, base_rows, scope)
    if not scope_map:
        return ["O0 the orb surface derived EMPTY. R-242 measures nothing and would report "
                "success - the BL-R181-DEBT-7 failure verbatim. Check "
                "svc_orb_breadth.orb_chains against this database."]

    out.extend(partition_problems(db, lk, base_rows, scope_map, carriers))
    general, excluded = partition(db, lk, base_rows, scope_map, carriers)

    worst = {'n': (0.0, '-'), 'e': (0.0, '-'), 'l': (0.0, '-')}
    for _k, (real, tier) in sorted(general.items()):
        r = reading(d, dist, real)
        short = SLB._n(real).rsplit('\\', 1)[-1]
        cls = TARGET_CLS[tier]
        p = r['p_epic'] if cls == EPIC else r['p_leg']
        lo, hi = TARGET_P[tier] - BAND_HALF, TARGET_P[tier] + BAND_HALF

        # G1 - the per-difficulty band (Will's number, +/-5pp)
        if not (lo <= p <= hi):
            out.append(
                "G1 %s [%s] pays at least one %s item %.1f%% of opens (target %.0f%%, band "
                "%.0f-%.0f%%). Will 2026-08-12: 50%% legendary on epic, 75%% on legendary, "
                "0%% legendary + 75%% blue on normal."
                % (SLB._n(real), TIER_NAME[tier], cls, 100.0 * p, 100.0 * TARGET_P[tier],
                   100.0 * lo, 100.0 * hi))
        # G2 - Normal must pay 0% legendary GEAR (the tier law; scroll/formula leak exempt)
        if tier == 'n' and r['p_leg_gear'] > NORMAL_LEG_GEAR_MAX:
            out.append(
                "G2 %s [Normal] pays legendary GEAR %.2f%% of opens (max %.0f%%). Will: "
                "\"a 0%% chance of dropping a legendary item on normal\" - a Normal orb's "
                "gear rows must stay Epic-classification (the base-game scroll/formula leak "
                "on loot4 is exempt and measured separately)."
                % (SLB._n(real), 100.0 * r['p_leg_gear'], 100.0 * NORMAL_LEG_GEAR_MAX))
        # O5 - and the orb must still be worth opening (empty-box mirror)
        if r['drops'] < ORB_MIN_DROPS_PER_OPEN:
            out.append(
                "G5 %s pays only %.2f item(s) of ANY kind per open (floor %.2f). The cheap "
                "way to meet a rate band is to make the orb an empty box; this check costs "
                "more than it saves." % (SLB._n(real), r['drops'], ORB_MIN_DROPS_PER_OPEN))
        if p > worst[tier][0]:
            worst[tier] = (p, '%s [%s]' % (short, tier))

    # G3 - the excluded apex, byte-unchanged vs build85 (its whole field domain here is
    # loot{g}Chance + numSpawn; members/weights are never written by this wave).
    for _k, (real, tier) in sorted(excluded.items()):
        f = d.fields(real)
        short = SLB._n(real).rsplit('\\', 1)[-1]
        for g in range(1, 7):
            got = float(f.get('loot%dChance' % g, [0.0])[0])
            exp = APEX_EXPECTED_CHANCE[g]
            if abs(got - exp) > CHANCE_TOL:
                out.append(
                    "G3 EXCLUDED apex %s loot%dChance = %.2f%%, expected the build85 value "
                    "%.2f%%. Will 2026-08-12: \"Leinth and the toxeus variants keep their "
                    "current ... orbs\" - these tables must stay byte-identical to build85."
                    % (short, g, got, exp))
        mn = str(SLB._sc(db.get_field_value(real, 'numSpawnMinEquation')) or '')
        mx = str(SLB._sc(db.get_field_value(real, 'numSpawnMaxEquation')) or '')
        emn, emx = APEX_EXPECTED_NUMSPAWN[tier]
        if mn != emn or mx != emx:
            out.append(
                "G3 EXCLUDED apex %s numSpawn = (%s, %s), expected build85 (%s, %s). The "
                "excluded orbs keep their volume verbatim." % (short, mn, mx, emn, emx))
        # G3b - and the apex OUTPUT is frozen too, so a shared-master retune cannot leak
        # into the excluded orbs while their own bytes stay put.
        r = reading(d, dist, real)
        for cls in (EPIC, LEGENDARY):
            got = r['p_epic'] if cls == EPIC else r['p_leg']
            exp = APEX_EXPECTED_READING[tier][cls]
            if abs(got - exp) > APEX_READING_TOL:
                out.append(
                    "G3b EXCLUDED apex %s pays %s %.2f%% of opens, expected the build85 "
                    "value %.2f%% (tol %.0fpp). A shared unique master the apex reads has "
                    "been retuned and leaked into the frozen Toxeus/Leinth loot; re-pin "
                    "APEX_EXPECTED_READING only if Will intends the apex to change."
                    % (short, cls, 100.0 * got, 100.0 * exp, 100.0 * APEX_READING_TOL))

    if report is not None:
        report.update({
            'general': len(general), 'excluded': len(excluded),
            'tables': len(scope_map), 'worst': worst,
        })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# THE STANDING NOTICE - the apex-vs-general inversion (BL-R242-DEBT-1)
# ─────────────────────────────────────────────────────────────────────────────
def inversion_notice(db, lk=None, base_rows=None, scope=None, carriers=None):
    """The standing notice that the excluded apex is now WEAKER than the general orbs on
    Legendary legendary-chance (an inversion of Will's 'keep their better orbs'), or None
    if it does not hold. Printed on every run so the residue cannot rot in a comment; not
    a finding (Will has not ruled the A/B call).
    """
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    general, excluded = partition(db, lk, base_rows, scope, carriers)
    gen_l = [reading(d, dist, real)['p_leg']
             for _k, (real, t) in general.items() if t == 'l']
    apex_l = [reading(d, dist, real)['p_leg']
              for _k, (real, t) in excluded.items() if t == 'l']
    if not gen_l or not apex_l:
        return None
    if max(apex_l) >= max(gen_l):
        return None
    return (
        "R-242 APEX-vs-GENERAL INVERSION (`BL-R242-DEBT-1`, awaiting Will's A/B call).\n"
        "  The excluded Toxeus/Leinth apex is frozen at its build85 numbers, so on Legendary\n"
        "  it now pays a legendary %.1f%% of opens against the general orbs' %.1f%% - the\n"
        "  general orbs drop legendaries MORE OFTEN than the 'better' apex. The apex keeps a\n"
        "  volume/loot4 edge only. This is the LITERAL byte-unchanged exclusion Will ruled\n"
        "  (part 2). Option (B) - bump the apex Legendary/Epic chance above the general\n"
        "  target - is a follow-up lane, and lowers this notice in the same commit."
        % (100.0 * max(apex_l), 100.0 * max(gen_l)))


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS (census / calibrate)
# ─────────────────────────────────────────────────────────────────────────────
def census(db, lk=None, base_rows=None, scope=None, carriers=None):
    """The partition and each table's target, printed."""
    lk = lk or SLB.Lookup(db)
    general, excluded = partition(db, lk, base_rows, scope, carriers)
    print('\n=== R-242 ORB PARTITION (general get 0/50/75; Toxeus+Leinth excluded) ===')
    print('  GENERAL (%d) - 0%% leg + 75%% blue on normal, 50%% leg epic, 75%% leg legendary:'
          % len(general))
    for _k, (real, tier) in sorted(general.items(), key=lambda kv: (kv[1][1], kv[0])):
        print('    [%s] %s' % (tier, SLB._n(real).rsplit('\\', 1)[-1]))
    print('  EXCLUDED (%d) - Toxeus/Leinth apex, kept byte-identical to build85:'
          % len(excluded))
    for _k, (real, tier) in sorted(excluded.items(), key=lambda kv: (kv[1][1], kv[0])):
        print('    [%s] %s' % (tier, SLB._n(real).rsplit('\\', 1)[-1]))


def calibrate(db, lk=None, base_rows=None, scope=None, carriers=None):
    """Every reading behind every band, so none of them is taste."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    census(db, lk, base_rows, scope, carriers)
    general, excluded = partition(db, lk, base_rows, scope, carriers)
    print('\n=== R-242 ORB LEGENDARY/BLUE CALIBRATION ===')
    print('  %-4s %-28s %6s %8s %8s %9s %9s %10s'
          % ('tier', 'table', 'S', 'drops', 'P>=1 Ep', 'P>=1 Le', 'P>=1 LeG', 'target'))
    for label, tables in (('GENERAL', general), ('EXCLUDED', excluded)):
        print('  -- %s --' % label)
        for _k, (real, tier) in sorted(tables.items(), key=lambda kv: (kv[1][1], kv[0])):
            r = reading(d, dist, real)
            tgt = ('%s %.0f%%' % (TARGET_CLS[tier], 100.0 * TARGET_P[tier])
                   if label == 'GENERAL' else 'frozen b85')
            print('  %-4s %-28s %6.3f %8.3f %8.4f %9.4f %10.5f %10s'
                  % (tier, SLB._n(real).rsplit('\\', 1)[-1][:28], r['S'], r['drops'],
                     r['p_epic'], r['p_leg'], r['p_leg_gear'], tgt))
    print('  targets  Normal blue(Epic) %.0f%% + leg-GEAR<=%.0f%% | Epic leg %.0f%% | '
          'Legendary leg %.0f%%  (band +/-%.0fpp)'
          % (100.0 * TARGET_P['n'], 100.0 * NORMAL_LEG_GEAR_MAX, 100.0 * TARGET_P['e'],
             100.0 * TARGET_P['l'], 100.0 * BAND_HALF))


def pass_line(report):
    w = report.get('worst', {})
    return ("%d general orb(s) in band + %d excluded apex byte-frozen; worst-in-band "
            "P(target): Normal %.1f%% (%s), Epic %.1f%% (%s), Legendary %.1f%% (%s)"
            % (report.get('general', 0), report.get('excluded', 0),
               100.0 * w.get('n', (0, '-'))[0], w.get('n', (0, '-'))[1],
               100.0 * w.get('e', (0, '-'))[0], w.get('e', (0, '-'))[1],
               100.0 * w.get('l', (0, '-'))[0], w.get('l', (0, '-'))[1]))
