r"""svc_orb_legendary.py - THE UBER-ORB LEGENDARY CONTRACT (Will 2026-08-11, R-231).

WILL, VERBATIM (2026-08-11), and this ruling SUPERSEDES the b79 "orbs stay generous"
precedent it collides with:
  "you made the orbs way too good... those dont need to have guaranteed legendary
   drops, they should just have a chance to drop legendary items, but a low chance."

WILL ASKED FOR THE NUMBER FIRST, SO HERE IT IS, MEASURED ON THE SHIPPED b83 ARZ
--------------------------------------------------------------------------------
`44499f56`, 18 orb loot tables (15 ordinary + 3 apex), 6 per difficulty:

  GUARANTEED ROWS (a loot group at chance == 100) CARRYING LEGENDARY MASS:
      Normal     1     Epic     1     Legendary     1        3 in the whole surface

  and all three are the SAME row on the SAME family: group 4 of
  `svc_uberorb_apex_{n,e,l}01c`, the amulet/relic/ring/formula row, at chance 100.0
  where its five sibling orb tables run the identical row at 12.7% or 21.2%. Its
  legendary MASS is small (0.4% / 5.2% / 6.3% by weight), so ZERO of the three is a
  pure-legendary row. The literal count Will asked for is therefore **one per tier,
  three in total, none of them pure**.

THE ROW COUNT IS NOT WHERE THE GUARANTEE LIVED, AND THAT IS THE FINDING
------------------------------------------------------------------------
Reporting "3 rows, all nearly non-legendary" and stopping would have answered the
question and missed the report. What Will actually hit is a guarantee made of VOLUME,
not of a 100% row. On the shipped b83 arz, per ONE orb open:

  difficulty   E[legendary items]      P(at least one legendary)
  Normal          0.003 .. 0.047          0.3% ..  4.6%
  Epic            2.579 .. 6.291         93.6% .. 99.9%
  Legendary       3.738 .. 8.432         98.4% .. 99.99%

An apex Legendary orb paid EIGHT AND A HALF legendary-grade items per open and had a
99.99% chance of at least one. That is a guaranteed legendary drop in every sense a
player means it, and no 100%-chance row was needed to produce it: six loot groups
rolled independently on 10.58 spawn iterations.

WHAT THIS CONTRACT DOES, AND THE ONE THING IT DELIBERATELY DOES NOT
--------------------------------------------------------------------
1. R-230's volume trim (same lane) takes every orb's spawn volume to the never-empty
   floor: S 5.06/6.44/8.28/10.58 -> 1.125. That is what kills the volume guarantee.
2. THIS module then discharges the literal half of the ruling: the three guaranteed
   rows are DEMOTED to chance-based, at the richest NON-guaranteed chance the same row
   already carries elsewhere in the orb family (21.2%, `boss_charon_*01b`'s value).
   DERIVED from the shipped bytes, never typed, so the demotion cannot drift away from
   the family it is supposed to rejoin, and the apex keeps its rank as the richest orb.
   Will's ruling offers "chance-based OR non-legendary"; chance-based is the smaller
   change, because making the row non-legendary means deleting `amulet_{tier}01` and
   `finger_{tier}01` from it, which are the ONLY legendary amulet and ring an orb can
   pay - breadth Will asked for in b75-b83, destroyed to satisfy a rate ruling.

   Together those two land, per ONE orb open:

     difficulty   E[legendary items]      P(at least one legendary)
     Normal          0.001 .. 0.004          0.05% ..  0.35%
     Epic            0.451 .. 0.622         38.2%  .. 49.0%
     Legendary       0.699 .. 0.846         53.6%  .. 60.9%

   The headline is the first column, and it is the one that answers the report:
   **at most ONE legendary item per orb open on Legendary difficulty, against 8.43
   shipped - a 90% cut.** An orb has stopped being a legendary vending machine and
   become a boss reward that sometimes contains a legendary.

3. WHAT IT DOES NOT DO, STATED PLAINLY RATHER THAN LEFT FOR A VET TO FIND. P(at least
   one) lands at 54-61% on Legendary, and 60% IS NOT "A LOW CHANCE". The reason is
   arithmetic, not laziness: after the trim an orb pays about 2.06 items per open, and
   on the Legendary tier ~40% of ALL its drop mass is legendary-CLASSIFICATION, because
   R-180/R-220 deliberately weighted `svc_unique_weapons_l01` and `svc_unique_armor_l01`
   at ~47% of the weapon row and ~50% of the shield row to buy the CLASS BREADTH Will
   asked for in the same fortnight. So if the orb pays anything at all, there is a good
   chance the thing it pays is legendary.

   The one lever that would move it further is scaling those rows' `loot{g}Chance`
   down - and that is NOT the volume lever numSpawn is. `svc_loot_distribution` D7b
   asserts worn-slot armour pieces PER SPAWN ITERATION (>= 0.0375) on all 63 surfaces;
   a group-chance scale divides that reading by the same factor and reds armour parity
   on every orb. Lowering only the legendary-heavy rows moves D3/D4 (weapon:armour) and
   D6 (armour-slot share) instead. Either way the next step out of 60% is a COMPOSITION
   decision inside R-180/R-181/R-220's scope, not a volume one, and this lane is
   explicitly forbidden to take it quietly. It is priced for Will as
   `BL-R231-DEBT-1`, with the ceilings below set where the authorised levers actually
   reach so the gate is a true ratchet and not an aspiration nothing enforces.

THE CONTRACT IS TWO-SIDED, BECAUSE A RATE RULING HAS TWO WAYS TO BE WRONG
-------------------------------------------------------------------------
Will said "just a CHANCE to drop legendary items, but a LOW chance" - which is a
ceiling AND a floor in one sentence. O2/O3 hold the ceiling; O4 holds the floor, so a
future wave cannot satisfy this ruling by making legendary drops impossible. O5 is the
same mirror one level out: an orb must still PAY, so the ceiling cannot be met by
turning the orb into an empty box.

Shared by `tools/gate_orb_legendary.py` (standalone), the in-build gate
`tools/patches/orb_legendary_chance.verify()` and
`tools/debug/negtest_orb_legendary.py`, so the three can never disagree (the
`gate_relic_difficulty_tiers` / R-230 precedent).
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
TIERS = ('n', 'e', 'l')
TIER_NAME = {'n': 'Normal', 'e': 'Epic', 'l': 'Legendary'}

# ─────────────────────────────────────────────────────────────────────────────
# THE CEILINGS. Every one is DERIVED from the measured post-wave reading plus a
# stated margin, in the direction that makes the check fail - never rounded to a
# number that reads well. The margins are the R-230 construction (V7/V7b), so the
# two contracts in this lane can be compared line for line.
#
# O2 - E[legendary items per open]. THE HEADLINE. Measured worst after the wave:
#   n 0.004 | e 0.622 | l 0.846. Ceilings below give 92% / 21% / 18% headroom, and
#   the Legendary one is deliberately the round number ONE: "at most one legendary
#   item per orb open" is the sentence this ruling is about, and a constant a
#   player could state in words is worth more than a third decimal place.
# ─────────────────────────────────────────────────────────────────────────────
ORB_MAX_LEG_PER_OPEN = {'n': 0.05, 'e': 0.75, 'l': 1.00}

# O3 - P(at least one legendary per open), the CHANCE half of Will's sentence.
# Measured worst after the wave: n 0.0035 | e 0.4895 | l 0.6090. These are a
# RATCHET at roughly 11% headroom, not a target: see the docstring's point 3 and
# `BL-R231-DEBT-1`. They exist so the 90% cut can never be quietly given back.
ORB_MAX_P_LEGENDARY = {'n': 0.02, 'e': 0.55, 'l': 0.68}
# ... and the same reading under INTEGER TRUNCATION of the spawn count, the
# pessimistic engine model R-230 introduced (`BL-R230-DEBT-5`). Measured worst
# 0.0031 / 0.4498 / 0.5639. Held at the SAME headroom as O3 rather than at the
# same value, so neither model is the one the gate happens to be lenient about.
ORB_MAX_P_LEGENDARY_TRUNC = {'n': 0.02, 'e': 0.51, 'l': 0.63}

# ─────────────────────────────────────────────────────────────────────────────
# THE FLOORS - the mirror direction, and the reason this file is a contract and
# not a trim. "they should just have A CHANCE to drop legendary items" is an
# instruction that legendary drops must remain POSSIBLE and non-trivial.
#
# O4 - measured best-case after the wave is e 0.3818 / l 0.5356 (the THINNEST orb
# of each tier, which is the binding reading for a floor). Set at 0.15/0.25, so a
# wave would have to more than HALVE the thinnest orb's legendary chance before
# this reds - wide enough that honest retuning is not fought, tight enough that
# "satisfy the ceiling by deleting the legendary" is impossible.
# Normal is deliberately ABSENT: a Normal-difficulty orb legitimately measures
# 0.05%-0.35% legendary, and inventing a floor there would be a number with no
# ruling behind it.
# ─────────────────────────────────────────────────────────────────────────────
ORB_MIN_P_LEGENDARY = {'e': 0.15, 'l': 0.25}

# O5 - and an orb must still be worth opening. Measured worst after the wave is
# 2.056 items per open on every ordinary orb and 2.151 on the apex; the floor sits
# at 1.50, which is 27% below the measured worst. This is what stops the ceilings
# above from being satisfied the cheap way - by scaling an orb's group chances
# until it is an empty box that technically never pays a legendary.
ORB_MIN_DROPS_PER_OPEN = 1.50

# The demotion target is DERIVED (see `family_chance`), but the shipped value is
# recorded so a re-derivation that lands somewhere else is VISIBLE rather than
# silently accepted. MEASURED on b83: group 4's richest non-guaranteed chance
# across the 18 orb tables is 21.2 (`boss_charon_*01b`); the 12 `uberorb_default_*`
# run the same row at 12.7.
FAMILY_CHANCE_EXPECTED = {4: 21.2}
FAMILY_CHANCE_TOL = 1e-6


# ─────────────────────────────────────────────────────────────────────────────
# SCOPE - the orb surface, DERIVED from `svc_orb_breadth`, never a typed list.
# Same derivation R-220's own gate uses, so "the orbs" means exactly what the orb
# breadth gate means by it and the two cannot drift apart (the BL-R181-DEBT-7
# lesson: fifteen live surfaces starved because two waves disagreed about scope).
# ─────────────────────────────────────────────────────────────────────────────
def orb_tables(db, lk=None, base_rows=None):
    """{norm(table): (real, tier)} for every in-scope uber-orb loot table."""
    lk = lk or SLB.Lookup(db)
    chains = SOB.orb_chains(db, lk, base_rows)
    return SOB.scope_tables(db, lk, base_rows, chains)


def group_profile(d, dist, table):
    """[(g, chance, legendary_share)] for every LIVE loot group of `table`.

    `legendary_share` is P(the item this group pays is legendary-CLASSIFIED), resolved
    through the whole loot graph by `svc_loot_distribution.Distributor` - not guessed
    from a pool's name. A group with no chance or no weighted member is not live and is
    omitted, which is what makes "guaranteed row" mean a row that actually fires.
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
        leg = 0.0
        for p_, w in pairs:
            share = w / tot
            for it, q in dist.dist(p_).items():
                if str(d.gv(it, 'itemClassification') or '') == LEGENDARY:
                    leg += share * q
        out.append((g, chance, leg))
    return out


def reading(d, dist, table):
    """(drops, E[legendary], P(>=1 legendary), P(>=1 legendary | truncated S)).

    P is computed from the per-iteration miss probability raised to S, because the
    groups roll INDEPENDENTLY on each spawn iteration - the same construction R-230's
    `cage_run` uses, so "at least one" means the same thing in both contracts.
    """
    S = SLD.spawn_iterations(d, table)
    St = SLV.spawn_iterations_trunc(d, table)
    gs = group_profile(d, dist, table)
    drops = S * sum(c for (_g, c, _s) in gs)
    e_leg = S * sum(c * s for (_g, c, s) in gs)
    miss = 1.0
    for (_g, c, s) in gs:
        miss *= (1.0 - c * s)
    return (drops, e_leg,
            1.0 - miss ** max(S, 0.0),
            1.0 - miss ** max(St, 0.0))


# ─────────────────────────────────────────────────────────────────────────────
# THE CENSUS - the number Will asked for, as a function so the gate, the module
# and the negatives all report the SAME count from the SAME rule.
# ─────────────────────────────────────────────────────────────────────────────
def guaranteed_legendary_rows(db, lk=None, d=None, dist=None, base_rows=None):
    """[(real, tier, group, chance, legendary_share)] - every orb loot group that fires
    on EVERY spawn iteration AND can pay a legendary.

    `chance >= 1.0` rather than `== 1.0`: a row at 120% is even more guaranteed, and a
    contract that only recognised the exact literal would be blind to it.
    """
    lk = lk or SLB.Lookup(db)
    d = d or SLD.Db(db)
    dist = dist or SLD.Distributor(d)
    out = []
    for _k, (real, tier) in sorted(orb_tables(db, lk, base_rows).items()):
        for (g, chance, leg) in group_profile(d, dist, real):
            if chance >= 1.0 and leg > 0.0:
                out.append((real, tier, g, chance, leg))
    return out


def family_chance(db, lk=None, d=None, dist=None, base_rows=None):
    """{group index: the richest NON-guaranteed chance that row carries across the orb
    family} - the demotion target, DERIVED from the shipped bytes.

    Deriving rather than typing is the whole point. The three guaranteed rows are
    group 4 of the apex tables, and group 4 exists on all 18 orb tables at 12.7% or
    21.2%; taking the RICHEST of those rejoins the apex to its family while keeping it
    the most generous orb in the mod, which is as much of the b79 "orbs stay generous"
    precedent as Will's newer ruling leaves standing. A typed 21.2 would go stale the
    first time anyone retuned `boss_charon_*01b`.
    """
    lk = lk or SLB.Lookup(db)
    d = d or SLD.Db(db)
    dist = dist or SLD.Distributor(d)
    out = {}
    for _k, (real, _tier) in sorted(orb_tables(db, lk, base_rows).items()):
        for (g, chance, _leg) in group_profile(d, dist, real):
            if chance < 1.0:
                out[g] = max(out.get(g, 0.0), chance)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# THE WAVE (write side)
# ─────────────────────────────────────────────────────────────────────────────
def already_applied(db, lk=None, base_rows=None):
    """The rows this wave would still have to demote. Empty == already applied (or
    never needed). Used as the apply-once guard, exactly like R-230's twin check:
    the demotion IS idempotent - a second run finds nothing at chance 100 and writes
    nothing - but saying so from a MEASUREMENT beats claiming it in a comment.
    """
    return guaranteed_legendary_rows(db, lk, base_rows=base_rows)


def apply_wave(db, lk=None, verbose=True, base_rows=None):
    """Demote every guaranteed-legendary orb row to the family chance. Returns
    [(real, tier, group, old_chance, new_chance)]."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    rows = guaranteed_legendary_rows(db, lk, d, dist, base_rows)
    if not rows:
        if verbose:
            print("  ORB LEGENDARY: no guaranteed-legendary orb row present - nothing "
                  "to demote (the wave is a no-op on an already-ruled database).")
        return []
    fam = family_chance(db, lk, d, dist, base_rows)
    changed = []
    for (real, tier, g, chance, _leg) in rows:
        target = fam.get(g)
        if target is None:
            raise SystemExit(
                "[svc_orb_legendary] group %d is at chance %.1f%% on %s and NO other orb "
                "table carries that row at a non-guaranteed chance, so there is no family "
                "value to demote it to. Deriving the target is what keeps this wave "
                "honest; inventing one here would be a balance decision taken by a gate. "
                "Give the row a non-guaranteed sibling, or make the target an explicit, "
                "Will-ruled constant." % (g, 100.0 * chance, SLB._n(real)))
        expected = FAMILY_CHANCE_EXPECTED.get(g)
        if expected is not None and abs(100.0 * target - expected) > FAMILY_CHANCE_TOL:
            raise SystemExit(
                "[svc_orb_legendary] the DERIVED demotion target for group %d is %.4f%% "
                "but this contract was written and measured against %.4f%%. The orb "
                "family has been retuned under the ruling: re-measure "
                "(py tools/gate_orb_legendary.py <arz> --census), re-derive the ceilings, "
                "and update FAMILY_CHANCE_EXPECTED deliberately - do not let a demotion "
                "silently land somewhere nobody chose."
                % (g, 100.0 * target, expected))
        db.set_field(real, 'loot%dChance' % g, 100.0 * target)
        db._modified.add(real)
        OWN.note_write(real, 'orb_legendary_chance')
        changed.append((real, tier, g, chance, target))
        if verbose:
            print("    %-46s [%s] loot%dChance %.1f%% -> %.1f%% (guaranteed row "
                  "carrying %.1f%% legendary mass, demoted to the family value)"
                  % (SLB._n(real).rsplit('\\', 1)[-1], tier, g,
                     100.0 * chance, 100.0 * target, 100.0 * _leg))
    return changed


# ─────────────────────────────────────────────────────────────────────────────
# THE CONTRACT
# ─────────────────────────────────────────────────────────────────────────────
def problems(db, lk=None, report=None, base_rows=None):
    """R-231. Returns a list of problem strings, empty when clean."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    out = []
    scope = orb_tables(db, lk, base_rows)
    if not scope:
        return ["O0 the orb surface derived EMPTY. R-231 measures nothing and would "
                "report success - the BL-R181-DEBT-7 failure verbatim. Check "
                "svc_orb_breadth.orb_chains against this database."]

    # O1 - Will's literal ruling: ZERO guaranteed-legendary rows.
    for (real, tier, g, chance, leg) in guaranteed_legendary_rows(db, lk, d, dist,
                                                                 base_rows):
        out.append(
            "O1 %s group %d fires on EVERY spawn iteration (chance %.1f%%) and pays "
            "legendary %.1f%% of the time, so an open of this orb is a guaranteed roll "
            "at a legendary item. Will 2026-08-11: \"those dont need to have guaranteed "
            "legendary drops, they should just have a chance to drop legendary items, "
            "but a low chance.\""
            % (SLB._n(real), g, 100.0 * chance, 100.0 * leg))

    worst_leg, worst_p, thinnest = (0.0, '-'), (0.0, '-'), (1e9, '-')
    for _k, (real, tier) in sorted(scope.items()):
        drops, e_leg, p1, p1t = reading(d, dist, real)
        short = SLB._n(real).rsplit('\\', 1)[-1]
        if e_leg > worst_leg[0]:
            worst_leg = (e_leg, '%s [%s]' % (short, tier))
        if p1 > worst_p[0]:
            worst_p = (p1, '%s [%s]' % (short, tier))
        if drops < thinnest[0]:
            thinnest = (drops, '%s [%s]' % (short, tier))

        # O2 - the headline ceiling, in ITEMS, which is the unit Will's report is in.
        if e_leg > ORB_MAX_LEG_PER_OPEN[tier]:
            out.append(
                "O2 %s pays %.3f legendary item(s) per open at difficulty %s (ceiling "
                "%.2f). Will: \"you made the orbs way too good\" - the shipped b83 orb "
                "paid up to 8.43 and this is the number that answers it."
                % (SLB._n(real), e_leg, TIER_NAME[tier], ORB_MAX_LEG_PER_OPEN[tier]))
        # O3 - the CHANCE ceiling, on both readings of the spawn count.
        if p1 > ORB_MAX_P_LEGENDARY[tier]:
            out.append(
                "O3 %s pays at least one legendary %.1f%% of the opens at difficulty %s "
                "(ceiling %.1f%%). \"a chance to drop legendary items, but a low "
                "chance\" is a CEILING, and this ratchet is what stops the 90%% cut "
                "being quietly given back."
                % (SLB._n(real), 100.0 * p1, TIER_NAME[tier],
                   100.0 * ORB_MAX_P_LEGENDARY[tier]))
        if p1t > ORB_MAX_P_LEGENDARY_TRUNC[tier]:
            out.append(
                "O3b under INTEGER TRUNCATION of the spawn count %s pays at least one "
                "legendary %.1f%% of the opens at difficulty %s (ceiling %.1f%%), "
                "against %.1f%% on the continuous reading. The engine's rounding mode is "
                "unproven (BL-R230-DEBT-5), so the ceiling has to hold under both or the "
                "PASS line is quoting a model instead of a drop rate."
                % (SLB._n(real), 100.0 * p1t, TIER_NAME[tier],
                   100.0 * ORB_MAX_P_LEGENDARY_TRUNC[tier], 100.0 * p1))
        # O4 - the MIRROR. "just a CHANCE" means a chance that still exists.
        floor = ORB_MIN_P_LEGENDARY.get(tier)
        if floor is not None and p1 < floor:
            out.append(
                "O4 %s pays at least one legendary only %.1f%% of the opens at "
                "difficulty %s (FLOOR %.1f%%). Will asked for a LOW chance, not for no "
                "chance - an uber orb that can no longer pay a legendary satisfies the "
                "ceiling by deleting the reward."
                % (SLB._n(real), 100.0 * p1, TIER_NAME[tier], 100.0 * floor))
        # O5 - ... and the orb must still be worth opening at all.
        if drops < ORB_MIN_DROPS_PER_OPEN:
            out.append(
                "O5 %s pays only %.2f item(s) of ANY kind per open (FLOOR %.2f). The "
                "cheap way to satisfy every ceiling above is to make the orb an empty "
                "box; this is the check that costs more than it saves."
                % (SLB._n(real), drops, ORB_MIN_DROPS_PER_OPEN))

    if report is not None:
        report.update({'tables': len(scope), 'worst_leg_per_open': worst_leg,
                       'worst_p': worst_p, 'thinnest_drops': thinnest,
                       'guaranteed': len(guaranteed_legendary_rows(db, lk, d, dist,
                                                                  base_rows))})
    return out


def census(db, lk=None, base_rows=None):
    """Will's question, printed: how many guaranteed-legendary rows per orb tier."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    scope = orb_tables(db, lk, base_rows)
    rows = guaranteed_legendary_rows(db, lk, d, dist, base_rows)
    print('\n=== R-231 GUARANTEED-LEGENDARY CENSUS (Will asked for this number) ===')
    print('  %-11s %7s %10s   %s' % ('difficulty', 'tables', 'guar rows', 'which'))
    for tier in TIERS:
        mine = [r for r in rows if r[1] == tier]
        n = sum(1 for _k, (_r, t) in scope.items() if t == tier)
        which = ', '.join('%s g%d @%.1f%% (%.1f%% legendary)'
                          % (SLB._n(r[0]).rsplit('\\', 1)[-1], r[2],
                             100.0 * r[3], 100.0 * r[4]) for r in mine) or '-'
        print('  %-11s %7d %10d   %s' % (TIER_NAME[tier], n, len(mine), which))
    print('  TOTAL guaranteed-legendary rows across the whole orb surface: %d'
          % len(rows))


def calibrate(db, lk=None, base_rows=None):
    """Every reading behind every constant above, so none of them is taste."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    census(db, lk, base_rows)
    scope = orb_tables(db, lk, base_rows)
    print('\n=== R-231 ORB LEGENDARY CALIBRATION ===')
    print('  %-4s %-34s %7s %8s %9s %9s %9s'
          % ('tier', 'table', 'S', 'drops', 'E[leg]', 'P>=1', 'P>=1 tr'))
    agg = {}
    for _k, (real, tier) in sorted(scope.items(), key=lambda kv: (kv[1][1], kv[0])):
        S = SLD.spawn_iterations(d, real)
        drops, e_leg, p1, p1t = reading(d, dist, real)
        print('  %-4s %-34s %7.3f %8.3f %9.3f %9.4f %9.4f'
              % (tier, SLB._n(real).rsplit('\\', 1)[-1][:34], S, drops, e_leg, p1, p1t))
        a = agg.setdefault(tier, [0.0, 0.0, 0.0, 1e9, 1e9])
        a[0] = max(a[0], e_leg)
        a[1] = max(a[1], p1)
        a[2] = max(a[2], p1t)
        a[3] = min(a[3], p1)
        a[4] = min(a[4], drops)
    print('  %-11s %10s %10s %11s %11s %10s' % ('difficulty', 'maxE[leg]', 'maxP>=1',
                                                'maxP>=1 tr', 'minP>=1', 'minDrops'))
    for tier in TIERS:
        if tier not in agg:
            continue
        a = agg[tier]
        print('  %-11s %10.3f %10.4f %11.4f %11.4f %10.3f'
              % (TIER_NAME[tier], a[0], a[1], a[2], a[3], a[4]))
    print('  ceilings O2 %s | O3 %s | O3b %s' % (ORB_MAX_LEG_PER_OPEN,
                                                 ORB_MAX_P_LEGENDARY,
                                                 ORB_MAX_P_LEGENDARY_TRUNC))
    print('  floors   O4 %s | O5 %.2f items/open'
          % (ORB_MIN_P_LEGENDARY, ORB_MIN_DROPS_PER_OPEN))


def pass_line(report):
    return ("%d orb table(s), %d guaranteed-legendary row(s); worst %.3f legendary "
            "item(s)/open on %s (ceiling %.2f), worst chance %.1f%% on %s, thinnest orb "
            "still pays %.2f item(s)/open"
            % (report.get('tables', 0), report.get('guaranteed', 0),
               report.get('worst_leg_per_open', (0, '-'))[0],
               report.get('worst_leg_per_open', (0, '-'))[1],
               max(ORB_MAX_LEG_PER_OPEN.values()),
               100.0 * report.get('worst_p', (0, '-'))[0],
               report.get('worst_p', (0, '-'))[1],
               report.get('thinnest_drops', (0, '-'))[0]))
