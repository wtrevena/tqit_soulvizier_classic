r"""svc_loot_distribution.py - THE DROP-DISTRIBUTION MODEL (Will 2026-08-10, R-181).

WILL, VERBATIM (2026-08-10), the two reports this module exists to answer:
  1. "also what about the armor? i am not really seeing armor drops like shields,
     chest plates, helmets, etc."
  2. "you overcorrected, that run 4 scorpions tail spears dropped"

R-180 proved a chest CAN reach a class (a reachability question). Neither report is a
reachability question: both are about HOW OFTEN. `svc_loot_breadth` counts distinct
reachable items; it cannot see that a chest reaches 22 legendary spears and 16 legendary
helms and still pays 15 weapons for every 1.6 armour pieces. This module is the missing
half: it computes the actual PROBABILITY MASS a chest puts on each equipment class and
on each individual item, so "roughly even across classes" and "no outsized single-item
share" are measurable, committed numbers instead of adjectives.

THE ENGINE (how TQAE resolves a FixedItemLoot container, measured on the shipped db)
------------------------------------------------------------------------------------
* A FixedItemLoot record has SIX loot groups. Per spawn iteration each group rolls
  INDEPENDENTLY at `loot{G}Chance` percent, and a group that fires picks exactly ONE
  member by `loot{G}Weight{i}`. Independence is measured, not assumed: 167 of the 296
  base-game FixedItemLoot tables have group chances summing to MORE than 100 (up to
  226.2 on `hermit mage chest_*`), which is impossible under a mutually-exclusive
  reading. The ~100% median is a design convention (one item per iteration on average),
  not a mechanic.
* The number of iterations is `numSpawnMin/MaxEquation`, evaluated with
  `numberOfPlayers` and `averagePlayerLevel`. Expected iterations S = (min+max)/2.
* So:  E[drops of item x per open] = S * SUM_G ( chance_G/100 * P(x | group G) ).
  Everything this module reports is that one formula.

LOOT-NODE KINDS (the `Class` field, measured counts in the shipped db)
  LootMasterTable          table of tables, `lootName{i}`/`lootWeight{i}`  -> recurse
  LootItemTable_FixedWeight  direct item paths + fixed weights            -> leaves
  LootItemTable_DynWeight    `itemNames` + a level bell curve             -> leaves
  LootRandomizerTable        affixes, not items                           -> ignored

THE DynWeight ASSUMPTION, STATED ONCE AND USED EVERYWHERE
---------------------------------------------------------
`LootItemTable_DynWeight` weights its `itemNames` by a level bell curve whose peak
depends on runtime state (`parentLevel`, `averagePlayerLevel`), so no static analysis
can pin one exact number. This module models it as UNIFORM over `itemNames`. That is
deliberately the assumption most FAVOURABLE to the shipped build: any real bell
concentration only makes a single item's share HIGHER than reported, never lower. So
every "before" skew number here is a LOWER BOUND on the skew Will actually saw, and
every threshold this module enforces is enforced against the optimistic case.

WHAT IT MEASURES (the committed balance targets of R-181)
----------------------------------------------------------
  ACROSS-CLASS  D1/D2 - no equipment class may hold more than its share cap of a table's
                or a surface's legendary mass; D3 - every class the surface claims to pay
                must clear a floor. Even is 1/11 = 9.1% over the 6 weapon + 5 worn slots.
  WITHIN-SIDE   D8/D9 - the same evenness measured INSIDE the weapon side and INSIDE the
                armour side, in their own denominators. Necessary, not decorative: once
                armour carries half the mass, a weapon-side skew hides under D1/D2 (a
                planted negative proved it by coming back GREEN).
  WITHIN-CLASS  D4 - no item may exceed MAX_ITEM_OVER_UNIFORM times its class's uniform
                share; D5 - and none may exceed MAX_ITEM_SHARE_TOTAL of the surface.
  ARMOUR PARITY D7 - every worn slot clears ARMOR_SLOT_FLOOR pieces per open; D6 - the
                weapon:armour mass ratio stays inside MAX_WEAPON_ARMOUR_RATIO. This is
                the half `svc_loot_breadth` is blind to and the half Will reported.

Shared by `tools/gate_loot_distribution.py` (standalone), the in-build gate
`tools/patches/armor_loot_breadth.verify()` and `tools/debug/negtest_armor_breadth.py`,
so the three can never disagree (the gate_relic_difficulty_tiers precedent).
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

# ─────────────────────────────────────────────────────────────────────────────
# THE EQUIPMENT SLOTS THIS CONTRACT BALANCES
#
# A SLOT is what a player wears or wields, which is not always one engine `Class`.
# MEASURED on the shipped db, so nobody re-guesses these strings:
#   * a shield's Class is `WeaponArmor_Shield` (475 records) - it is NOT
#     `ArmorProtective_*`. A naive `startswith('Armor')` armour audit sees ZERO
#     shields and a naive `startswith('Weapon')` weapon audit counts every shield as
#     a weapon. Both errors point the same way: shields vanish from armour.
#   * the arm slot is TWO classes - `ArmorProtective_Forearm` (armbands, 669) and
#     `ArmorJewelry_Bracelet` (62, the caster armband line that
#     `unique_arms_l01 -> bracelet_l01` pays at weight 50 of 100).
# ─────────────────────────────────────────────────────────────────────────────
# ⚠ CROSS-LANE MERGE HAZARD, WRITTEN DOWN BECAUSE IT IS INVISIBLE AT MERGE TIME.
# `WeaponHunting_RangedOneHand` is bucketed into `bow` here because, on the db this was
# calibrated against, nothing in scope pays that class and giving it its own slot would
# make D3 (the starvation floor) red every surface for a class that does not exist yet.
# The concurrent lane `fix/craft-thrown-breadth` adds a THROWN / one-hand-ranged member to
# `svc_loot_breadth._master_members` plus a C1/C2 rule in `audit_table`. The moment that
# lane merges, every legendary thrown item the master pays is counted as BOW mass by D2
# and D8 - inflating the measured bow share and masking exactly the thrown starvation this
# gate should be able to see. AT MERGE, DO BOTH:
#   1. give thrown its own entry here and in SLOT_ORDER / SLOT_LABEL, and
#   2. re-run `--calibrate` and re-derive MAX_WEAPON_CLASS_SHARE - it is 0.29 against SIX
#      weapon classes (even 16.7%); with seven, even is 14.3%.
# Tracked as BL-R181-DEBT-4. The two Python files themselves auto-merge cleanly (verified
# with `git merge-tree --write-tree` against fix/orb-loot-breadth, fix/craft-thrown-breadth
# and main - the only conflicts are append-adjacent lines in the three doc ledgers), which
# is precisely why this needs a written note: nothing will fail to tell you.
WEAPON_SLOTS = {
    'axe': ('WeaponMelee_Axe',),
    'mace': ('WeaponMelee_Mace',),
    'sword': ('WeaponMelee_Sword',),
    'spear': ('WeaponHunting_Spear',),
    'bow': ('WeaponHunting_Bow', 'WeaponHunting_RangedOneHand'),
    'staff': ('WeaponMagical_Staff',),
}
# Will's own words: "shields, chest plates, helmets, etc." - one entry per worn slot.
ARMOR_SLOTS = {
    'helm': ('ArmorProtective_Head',),
    'arms': ('ArmorProtective_Forearm', 'ArmorJewelry_Bracelet'),
    'torso': ('ArmorProtective_UpperBody',),
    'legs': ('ArmorProtective_LowerBody',),
    'shield': ('WeaponArmor_Shield',),
}
GEAR_SLOTS = dict(WEAPON_SLOTS)
GEAR_SLOTS.update(ARMOR_SLOTS)
SLOT_ORDER = ('axe', 'mace', 'sword', 'spear', 'bow', 'staff',
              'helm', 'arms', 'torso', 'legs', 'shield')
CLASS_TO_SLOT = {c: s for s, cs in GEAR_SLOTS.items() for c in cs}
SLOT_LABEL = {'axe': 'axe', 'mace': 'mace/club', 'sword': 'sword', 'spear': 'SPEAR',
              'bow': 'bow', 'staff': 'staff', 'helm': 'helm', 'arms': 'arms',
              'torso': 'torso', 'legs': 'legs', 'shield': 'shield'}

# ─────────────────────────────────────────────────────────────────────────────
# THE COMMITTED BALANCE TARGETS (R-181)
#
# Every threshold below is DERIVED, not chosen: each was read off
# `py tools/gate_loot_distribution.py <arz> --calibrate` (shipped) and the same command
# with `--apply` (fixed), run against the CURRENT build78 arz
# `f663846233295da3e8824bfa4d8925c8`, and then placed so that it REDS the shipped state
# and CLEARS the fixed state with margin. A threshold that does not red the reported
# defect is decoration; a threshold with no margin is a gate that gets switched off (the
# b63 1.0u lesson).
#
# THESE NUMBERS WERE RE-DERIVED, AND SAYING SO IS THE POINT. The first R-181 round
# calibrated against a 36-surface set that silently EXCLUDED the six structurally hardest
# surfaces in the mod - the 3 `svc_uberorb_apex_*` tables (deferred to a lane that did not
# own them) and the 3 DRX donors (written by the wave, absent from the audit). With all 42
# surfaces in scope the same 15-20% margin discipline lands on different values: four
# thresholds move OUT (D2, D3, D6, D7) and one moves IN (D1 0.42 -> 0.35, which the old
# set could not afford). Every one still reds the reported defect by a wide margin; none
# was moved to make a red go away without a stated derivation.
#
#   check                      shipped   R-181   threshold   reds shipped   margin
#   D1 class share, table       0.4313   0.2083    0.35        yes  (23%)     40%
#   D2 class share, surface     0.3431   0.2083    0.25        yes  (37%)     17%
#   D3 thinnest class share     0.0106   0.0175    0.0145      yes  (27%)     17%
#   D4 item share / uniform     4.19x    5.04x     5.8x        no*             13%
#   D5 item share, surface      0.0583   0.0260    0.030       yes  (94%)     13%
#   D6 weapon : armour          7.206    1.5857    1.85        yes (289%)     14%
#   D6b lowest weapon : armour  1.5257   0.2845    0.24        yes  (30%)**   16%
#   D7 thinnest armour slot     0.0397   0.6229    0.52        yes  (13x)     16%
#   D8 class share of weapons   0.4145   0.2413    0.29        yes  (43%)     17%
#   D9 slot share of armour     0.5352   0.2918    0.44        yes  (22%)     34%
#
#   ** D6b is a MIRROR guard, so the shipped build cannot red it (shipped, weapons
#      dominated everywhere - the lowest ratio in the mod was 1.53:1). The defect it must
#      red is this wave's OWN over-correction, and it caught one for real: with armour
#      lifted to parity but the weapon row still carrying the apex donor's diluted 29.6%
#      legendary share, `svc_uberorb_apex_n01c` inverted to 0.1683:1 - an 85%-armour
#      surface. 0.24 reds that by 30%. That measurement is the derivation, and negtest N7
#      re-plants it so the number stays load-bearing.
#
#   * D4 is a REGRESSION GUARD, and the report says so plainly rather than pretending
#     otherwise. The cage's within-class spread was ALREADY near-uniform in the shipped
#     build (the top spear carried 1.33x its class's uniform share), so the four
#     Scorpion's Tails were a VOLUME x CLASS-SHARE event, not a within-class one - see
#     the R-181 arithmetic. The worst within-class concentration in the whole mod, 4.9x
#     uniform, sits on the NORMAL branch and is a base-game artefact: the static
#     randomiser tables and the unique tables overlap on the same `u_n_*` items, and
#     this mod owns neither. What R-181 does move is the number a player actually
#     feels, D5: that same item's share of everything the surface drops falls 0.0583 ->
#     0.0250 because the pool it competes in is far wider.
# ─────────────────────────────────────────────────────────────────────────────
# Even across the 11 gear classes is 9.1%. D1 is the coarse "no table collapses onto one
# class" bound - a THEMED variant is designed to bias, and it is only ever met alongside
# its two siblings, so D2 (the surface the player actually opens) is the binding
# evenness contract. D1 exists to catch what shipped: SPEAR at 43.1% of one cage table.
MAX_CLASS_SHARE_TABLE = 0.35
MAX_CLASS_SHARE_AGGREGATE = 0.25
# A class the surface claims to pay must actually be payable. The shipped cage put the
# helm at 1.06% of its Epic mass - reachable, and invisible.
MIN_CLASS_SHARE_TABLE = 0.0145
# "Near-uniform within a class": no item may carry more than this multiple of its
# class's uniform share (1/n). Expressed as a MULTIPLE because a 7-item class cannot be
# held to an absolute share below its own uniform 14.3%.
MAX_ITEM_OVER_UNIFORM = 5.8
# ... and no item may own more than this share of the whole surface's gear mass. This is
# the absolute "one item dominates the run" bound and it DOES red the shipped build.
MAX_ITEM_SHARE_TOTAL = 0.030
# ── D5 PINS: a measured, reasoned per-surface ceiling. NOT a loosened cap. ────
# BL-R181-DEBT-7 brought four level-banded orb tiers into the audit whose top item sits
# at 3.2-4.5% of the surface's gear mass. MEASURED on build79, the state BEFORE any of
# this: 3.2%, 4.58%, 4.61%, 4.47%. So these are PRE-EXISTING concentrations that were
# invisible only because nobody audited the table - and the armour treatment IMPROVES two
# of them (4.58 -> 3.84, 4.61 -> 3.38) and leaves the others flat. They cannot be
# improved further from here: diluting a narrow pool needs more WIDE mass, and every one
# of these surfaces is already at weapon:armour 0.42-0.49 against D6b's 0.24 floor.
# WHY A PIN AND NOT A POOL-SIZE CLAUSE. The obvious alternative - let the cap scale with
# the surface's pool size, the argument D4 makes for classes one block above - was
# MEASURED AND REJECTED: the smallest x-uniform among the 24 pre-existing surfaces D5 reds
# in the defect state is 3.53, and the largest among the new orb surfaces AFTER the wave
# is 6.35, so any clause loose enough to pass the orbs would let 23 of those 24 shipped
# defects through. The cap stays 0.030 for every surface in the mod; these four are held
# to their OWN measured ceiling instead, and a regression on them still reds.
# The CAUSE is base-game content this mod does not own - the same finding D4 records one
# block below: the level-banded `all_<band>` static randomisers pay a narrow set of
# high-band legendaries that overlap the unique tables. Registered as BL-R181-DEBT-9.
# A pin whose surface has fallen back under the global cap is DEAD CONFIG and fails the
# gate (the svc_orb_breadth.OUT_OF_REACH stale-pin discipline), so these cannot rot.
D5_PINNED = {
    'orb uberorb_default_29-31.dbr': (0.037, 'level-banded normal tier; MEASURED 0.0322 '
        'after the wave and 0.0322 before it - unchanged by this contract, pre-existing'),
    'orb uberorb_default_39-41.dbr': (0.044, 'level-banded epic tier; MEASURED 0.0384 '
        'after the wave, IMPROVED from 0.0458 before it'),
    'orb uberorb_default_43-45.dbr': (0.039, 'level-banded epic tier; MEASURED 0.0338 '
        'after the wave, IMPROVED from 0.0461 before it'),
    'orb uberorb_default_49-51.dbr': (0.052, 'level-banded epic tier; MEASURED 0.0453 '
        'after the wave and 0.0447 before it - the thinnest legendary pool of the family '
        '(N=103), and the worst single-item share left in the mod'),
}
# Armour parity. Every worn slot must be a REAL drop, not a rounding error.
ARMOR_SLOT_FLOOR = 0.52          # expected legendary pieces of that slot per chest open
# ── D7's VOLUME PROBLEM, and the volume-free form of the same invariant ──────
# "0.52 pieces per open" is a statement about a container that spawns roughly 10.6 items
# per open, because that is the container it was derived on: the R-181 calibration's
# binding surface was `svc_uberorb_apex_e01c` at 0.6229, and its numSpawn equations
# (Leinth's `(3+(1.6*numberOfPlayers))*2.2 / *2.4`) give S = 10.58. Every one of the 42
# surfaces R-181 audited spawns AT LEAST that much (10.58 .. 18.96), so the number was
# never volume-sensitive in practice and nothing said so.
# BL-R181-DEBT-7 brought in 15 surfaces that spawn 5.06 .. 8.28. On those the same
# absolute number is not a parity demand at all - it is a demand for MORE DROPS, i.e. for
# numSpawn, and BL-R181-DEBT-5 reserves that lever to Will. MEASURED after the armour
# treatment lands on them: they are pinned from the other side by D6b, running
# weapon:armour 0.28 .. 0.49 against its 0.24 floor, so armour on them CANNOT be lifted
# further without burying weapons. The absolute floor is unreachable there by
# construction, not by neglect.
# So D7 keeps its exact number and its exact behaviour on every container big enough for
# it to mean what it says, and the volume-free form of the same invariant - the same
# armour yield measured PER SPAWN ITERATION - is asserted on every surface as D7b.
# THAT QUANTITY IS NEARLY A CONSTANT OF THE CONTRACT, which is why it is the honest form:
# measured after the wave, EVERY chest, hoard, cage variant, DRX donor and orb in the mod
# lands on 0.1406 (normal) / 0.0589 (epic) / 0.0996 (legendary) per iteration, and the
# only surfaces below that are the three level-banded epic orb tiers at 0.0443 .. 0.0531.
#   check                       defect (build79)   after wave   threshold   margin
#   D7  thinnest slot / open     0.0071 .. 0.3314    >= 0.6229*   0.52        16%
#   D7b thinnest slot / spawn    0.0011 .. 0.0175    >= 0.0443    0.0375      18%
#   * on surfaces at or above the reference volume; D7 is not asserted below it.
# D7b at 0.0375 REDS ALL 57 defect surfaces (the defect state's BEST reading is 0.0175,
# 2.1x under), which makes it a strictly stronger revert-detector than the absolute floor.
ARMOR_SLOT_FLOOR_REF_SPAWN = 10.58   # spawn iterations of the surface 0.52 was derived on
ARMOR_SLOT_FLOOR_PER_SPAWN = 0.0375  # D7b: worn-slot pieces per SPAWN ITERATION
MAX_WEAPON_ARMOUR_RATIO = 1.85   # legendary weapon mass : legendary armour mass
# ... and the MIRROR, so "fix the armour" cannot quietly become "bury the weapons". The
# binding case is the blood-cave mega chest `loottable_hidden_bloodcave_03`, which has NO
# guaranteed weapon slot at all (`loot3Chance = 0`) and was already armour-leaning at
# 1.60:1 before this wave; it measures 0.33:1 after, so the floor sits at 0.25 (24%
# margin) to catch a future inversion without reding a surface whose SHAPE is the reason.
MIN_WEAPON_ARMOUR_RATIO = 0.24
# D8/D9 - the WITHIN-SIDE balance, and the reason they exist is a negative test that
# came back GREEN when it should have been RED. D1/D2 measure a class's share of ALL
# gear; once armour parity lands, armour takes half the mass, so re-planting the shipped
# spear over-weighting drops SPEAR to ~21% of total gear and slides under D1/D2. The
# skew Will reported is INSIDE the weapon side, so it has to be measured there.
# Even is 1/6 = 16.7% for weapons and 1/5 = 20.0% for armour; both thresholds are in
# the table at the top of this block.
MAX_WEAPON_CLASS_SHARE = 0.29
MAX_ARMOUR_SLOT_SHARE = 0.44


def _n(s):
    return str(s).replace('/', '\\').lower()


def _sc(v):
    return v[0] if isinstance(v, list) and v else v


class Db:
    """Case-insensitive read layer over one ArzDatabase (the db itself is case
    sensitive and the shipped records are not internally consistent about case)."""

    def __init__(self, db):
        self.db = db
        self._lower = {_n(x): x for x in db.record_names()}
        self._fcache = {}

    def refresh(self):
        self._lower = {_n(x): x for x in self.db.record_names()}
        self._fcache.clear()

    def real(self, path):
        if not isinstance(path, str):
            path = _sc(path)
            if not isinstance(path, str):
                return None
        return self._lower.get(_n(path))

    def fields(self, path):
        real = self.real(path)
        if not real:
            return {}
        hit = self._fcache.get(real)
        if hit is None:
            hit = {}
            for k, tf in (self.db.get_fields(real) or {}).items():
                hit[k.split('###')[0]] = list(tf.values)
            self._fcache[real] = hit
        return hit

    def gv(self, path, field):
        v = self.fields(path).get(field)
        return v[0] if v else None

    def cls(self, path):
        return str(self.gv(path, 'Class') or '')

    def tpl(self, path):
        return _n(self.gv(path, 'templateName') or '')


# ─────────────────────────────────────────────────────────────────────────────
# NODE DISTRIBUTION: P(item | one pick from this loot node)
# ─────────────────────────────────────────────────────────────────────────────
class Distributor:
    def __init__(self, d):
        self.d = d
        self._memo = {}

    def dist(self, path, _stack=None, _depth=0):
        """{item_record: probability} for ONE pick from `path`. Probabilities sum to
        1.0 when the node resolves to anything at all, else {}."""
        real = self.d.real(path)
        if not real:
            return {}
        key = _n(real)
        hit = self._memo.get(key)
        if hit is not None:
            return hit
        stack = _stack or set()
        if key in stack or _depth > 12:
            return {}
        tpl = self.d.tpl(real)
        f = self.d.fields(real)
        out = {}
        if 'loot' not in tpl:
            self._memo[key] = {real: 1.0}       # a plain item record: the leaf
            return self._memo[key]
        stack = stack | {key}
        if tpl.endswith('lootitemtable_dynweight.tpl'):
            names = [x for x in f.get('itemNames', []) if isinstance(x, str)]
            # DOCUMENTED ASSUMPTION (module docstring): uniform over itemNames, the
            # assumption most favourable to the shipped build.
            if names:
                p = 1.0 / len(names)
                for it in names:
                    r = self.d.real(it)
                    if r:
                        out[r] = out.get(r, 0.0) + p
        elif tpl.endswith('lootrandomizertable.tpl'):
            out = {}                             # affixes, not items
        else:
            # LootMasterTable + LootItemTable_FixedWeight share the lootName/lootWeight
            # shape; the only difference is whether a child is a table or an item, and
            # the recursion below decides that per child.
            pairs = []
            for i in range(1, 31):
                nm = f.get('lootName%d' % i)
                if not nm or not isinstance(nm[0], str) or not nm[0].strip():
                    continue
                wt = f.get('lootWeight%d' % i)
                w = float(wt[0]) if wt else 0.0
                if w > 0:
                    pairs.append((nm[0], w))
            tot = sum(w for _p, w in pairs)
            if tot > 0:
                for p_, w in pairs:
                    share = w / tot
                    for it, q in self.dist(p_, stack, _depth + 1).items():
                        out[it] = out.get(it, 0.0) + share * q
        if not _stack:
            self._memo[key] = out
        return out


_NUM_SAFE = re.compile(r'^[\d\.\+\-\*\/\(\) ]+$')


def eval_spawn(expr, players=1, apl=70):
    """Evaluate a numSpawn equation. Arithmetic only, regex-guarded, never eval of
    anything the regex has not already proven is arithmetic."""
    if not expr:
        return None
    e = (str(expr).replace('numberOfPlayers', str(players))
                  .replace('averagePlayerLevel', str(apl)))
    if not _NUM_SAFE.match(e):
        return None
    try:
        return float(eval(e, {'__builtins__': {}}, {}))   # noqa: S307 - guarded above
    except Exception:
        return None


def spawn_iterations(d, table, players=1):
    """Expected spawn iterations S for one open of `table`."""
    lo = eval_spawn(d.gv(table, 'numSpawnMinEquation'), players)
    hi = eval_spawn(d.gv(table, 'numSpawnMaxEquation'), players)
    if lo is None and hi is None:
        return 1.0
    if lo is None:
        return hi
    if hi is None:
        return lo
    return (lo + hi) / 2.0


class ChestProfile:
    """The expected drop profile of ONE FixedItemLoot chest table, per open."""

    def __init__(self, d, dist, table, players=1, classification='Legendary'):
        self.table = d.real(table) or table
        self.d = d
        self.S = spawn_iterations(d, self.table, players)
        f = d.fields(self.table)
        self.groups = []
        # E[count of item x per open], restricted to `classification` gear items.
        self.per_item = defaultdict(float)
        self.per_item_all = defaultdict(float)
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
            self.groups.append((g, chance, pairs, tot))
            if chance <= 0 or tot <= 0:
                continue
            for p_, w in pairs:
                share = w / tot
                for it, q in dist.dist(p_).items():
                    self.per_item_all[it] += self.S * chance * share * q
        for it, ev in self.per_item_all.items():
            if str(d.gv(it, 'itemClassification') or '') == classification:
                self.per_item[it] += ev

    def by_slot(self):
        out = defaultdict(float)
        for it, ev in self.per_item.items():
            s = CLASS_TO_SLOT.get(self.d.cls(it))
            if s:
                out[s] += ev
        return dict(out)

    def gear_mass(self):
        return sum(self.by_slot().values())

    def items_in_slot(self, slot):
        return {it: ev for it, ev in self.per_item.items()
                if CLASS_TO_SLOT.get(self.d.cls(it)) == slot}

    def expected_drops(self):
        """Expected item drops of ANY kind per open (the non-reduction quantity)."""
        return self.S * sum(c for (_g, c, _p, t) in self.groups if t > 0)


# ─────────────────────────────────────────────────────────────────────────────
# THE AUDIT (shared by the standalone gate, the in-build gate and the negtests)
# ─────────────────────────────────────────────────────────────────────────────
def audit_surface(d, dist, label, tables, weights=None, tier='l', players=1,
                  require_armor=True, classification=None):
    """Audit one SURFACE: a set of chest tables a player experiences together
    (the cage's six physical chests, a boss hoard, the blood-cave mega chest).

    `weights` = spawn-time selection weights over `tables` (a ProxyAccessoryPool's
    per-variant weights); None = equal. Returns (problems, report)."""
    ic = classification or {'n': 'Epic', 'e': 'Legendary', 'l': 'Legendary'}[tier]
    profs = [ChestProfile(d, dist, t, players, ic) for t in tables]
    profs = [p for p in profs if p.gear_mass() > 0]
    if not profs:
        return (['D0 %s: no chest table carries any %s gear at all' % (label, ic)], {})
    if weights:
        w = [float(x) for x in weights][:len(profs)]
    else:
        w = [1.0] * len(profs)
    tw = sum(w) or 1.0
    w = [x / tw for x in w]

    agg_slot = defaultdict(float)
    agg_item = defaultdict(float)
    spawn = 0.0
    for wi, p in zip(w, profs):
        spawn += wi * p.S
        for s, ev in p.by_slot().items():
            agg_slot[s] += wi * ev
        for it, ev in p.per_item.items():
            if CLASS_TO_SLOT.get(d.cls(it)):
                agg_item[it] += wi * ev
    total = sum(agg_slot.values()) or 1.0
    n_slots = len(GEAR_SLOTS) if require_armor else len(WEAPON_SLOTS)

    problems = []
    # D1 across-class evenness, per table (a theme may bias, but only so far).
    for p in profs:
        bs = p.by_slot()
        m = sum(bs.values()) or 1.0
        for s, ev in sorted(bs.items(), key=lambda kv: -kv[1]):
            if ev / m > MAX_CLASS_SHARE_TABLE:
                problems.append(
                    "D1 %s / %s: class %s holds %.1f%% of the table's %s gear mass "
                    "(cap %.1f%%, even is %.1f%%)"
                    % (label, _n(p.table).rsplit('\\', 1)[-1], SLOT_LABEL.get(s, s),
                       100.0 * ev / m, ic, 100.0 * MAX_CLASS_SHARE_TABLE,
                       100.0 / n_slots))
    # D2 across-class evenness, surface aggregate (what a farm run feels).
    for s, ev in sorted(agg_slot.items(), key=lambda kv: -kv[1]):
        if ev / total > MAX_CLASS_SHARE_AGGREGATE:
            problems.append(
                "D2 %s: class %s holds %.1f%% of the surface's %s gear mass "
                "(cap %.1f%%, even is %.1f%%)"
                % (label, SLOT_LABEL.get(s, s), 100.0 * ev / total, ic,
                   100.0 * MAX_CLASS_SHARE_AGGREGATE, 100.0 / n_slots))
    # D3 every gear class the surface pays must be reachable with real mass.
    want = SLOT_ORDER if require_armor else tuple(WEAPON_SLOTS)
    for s in want:
        if agg_slot.get(s, 0.0) / total < MIN_CLASS_SHARE_TABLE:
            problems.append(
                "D3 %s: class %s holds only %.2f%% of the surface's %s gear mass "
                "(floor %.1f%%) - the slot is starving, not merely thin"
                % (label, SLOT_LABEL.get(s, s), 100.0 * agg_slot.get(s, 0.0) / total,
                   ic, 100.0 * MIN_CLASS_SHARE_TABLE))
    # D4/D5 within-class near-uniformity: no outsized single item.
    by_slot_items = defaultdict(dict)
    for it, ev in agg_item.items():
        by_slot_items[CLASS_TO_SLOT[d.cls(it)]][it] = ev
    for s, items in by_slot_items.items():
        m = sum(items.values())
        if m <= 0:
            continue
        top, tev = max(items.items(), key=lambda kv: kv[1])
        over_uniform = (tev / m) * len(items)     # x the class's uniform share
        if over_uniform > MAX_ITEM_OVER_UNIFORM:
            problems.append(
                "D4 %s: %s is %.1f%% of all %s drops = %.2fx the class's uniform share "
                "(cap %.1fx; uniform over %d items is %.1f%%) - one item dominates its "
                "class" % (label, _n(top).rsplit('\\', 1)[-1], 100.0 * tev / m,
                           SLOT_LABEL.get(s, s), over_uniform, MAX_ITEM_OVER_UNIFORM,
                           len(items), 100.0 / len(items)))
        pin, why = D5_PINNED.get(label, (None, None))
        cap = MAX_ITEM_SHARE_TOTAL if pin is None else pin
        if tev / total > cap:
            problems.append(
                "D5 %s: %s is %.1f%% of the surface's whole %s gear mass (cap %.1f%%%s)"
                % (label, _n(top).rsplit('\\', 1)[-1], 100.0 * tev / total, ic,
                   100.0 * cap, '' if pin is None else ', its PINNED ceiling - %s' % why))
    # D8/D9 the WITHIN-SIDE balance. D1/D2 measure a class against ALL gear, so once
    # armour carries half the mass a weapon-side skew hides under them - which a planted
    # negative proved by coming back GREEN. Measure each side in its own denominator.
    wmass = sum(agg_slot.get(s, 0.0) for s in WEAPON_SLOTS)
    if wmass > 0:
        for s in WEAPON_SLOTS:
            if agg_slot.get(s, 0.0) / wmass > MAX_WEAPON_CLASS_SHARE:
                problems.append(
                    "D8 %s: class %s holds %.1f%% of the surface's %s WEAPON mass "
                    "(cap %.1f%%, even is %.1f%%) - the weapon side is skewed even when "
                    "the whole-gear share looks calm"
                    % (label, SLOT_LABEL[s], 100.0 * agg_slot.get(s, 0.0) / wmass, ic,
                       100.0 * MAX_WEAPON_CLASS_SHARE, 100.0 / len(WEAPON_SLOTS)))
    if require_armor:
        _am = sum(agg_slot.get(s, 0.0) for s in ARMOR_SLOTS)
        if _am > 0:
            for s in ARMOR_SLOTS:
                if agg_slot.get(s, 0.0) / _am > MAX_ARMOUR_SLOT_SHARE:
                    problems.append(
                        "D9 %s: slot %s holds %.1f%% of the surface's %s ARMOUR mass "
                        "(cap %.1f%%, even is %.1f%%)"
                        % (label, SLOT_LABEL[s], 100.0 * agg_slot.get(s, 0.0) / _am,
                           ic, 100.0 * MAX_ARMOUR_SLOT_SHARE, 100.0 / len(ARMOR_SLOTS)))
    # D6/D7 armour parity: every wearable slot is a real drop, and weapons do not
    # drown armour. This is the half Will reported and R-180 could not see.
    if require_armor:
        amass = sum(agg_slot.get(s, 0.0) for s in ARMOR_SLOTS)
        if amass <= 0 or wmass / amass > MAX_WEAPON_ARMOUR_RATIO:
            problems.append(
                "D6 %s: weapon:armour mass is %s:1 (cap %.2f:1) - %.2f %s weapons vs "
                "%.2f %s armour pieces per open"
                % (label, ('inf' if amass <= 0 else '%.2f' % (wmass / amass)),
                   MAX_WEAPON_ARMOUR_RATIO, wmass, ic, amass, ic))
        elif wmass / amass < MIN_WEAPON_ARMOUR_RATIO:
            problems.append(
                "D6b %s: weapon:armour mass is %.2f:1 (floor %.2f:1) - fixing armour "
                "must not bury weapons: %.2f %s weapons vs %.2f %s armour per open"
                % (label, wmass / amass, MIN_WEAPON_ARMOUR_RATIO, wmass, ic, amass, ic))
        for s in ARMOR_SLOTS:
            per_open = agg_slot.get(s, 0.0)
            # D7 - the absolute per-open floor, asserted on every container whose own
            # spawn volume is at least the volume the floor was derived at. Below that
            # the number is a numSpawn demand rather than a parity one (BL-R181-DEBT-5
            # reserves numSpawn to Will), so D7b carries the invariant instead.
            if spawn >= ARMOR_SLOT_FLOOR_REF_SPAWN and per_open < ARMOR_SLOT_FLOOR:
                problems.append(
                    "D7 %s: armour slot %s pays only %.2f %s piece(s) per open "
                    "(floor %.2f) - Will's \"i am not really seeing armor drops\""
                    % (label, SLOT_LABEL.get(s, s), per_open, ic, ARMOR_SLOT_FLOOR))
            # D7b - the same invariant with the container's own volume divided out, so a
            # low-volume orb is held to the same CONTRACT as a cage without being asked
            # for drops it does not spawn. Asserted on every surface, and it reds all 57
            # surfaces of the defect state on its own.
            if spawn > 0 and per_open / spawn < ARMOR_SLOT_FLOOR_PER_SPAWN:
                problems.append(
                    "D7b %s: armour slot %s pays %.4f %s piece(s) per SPAWN ITERATION "
                    "(floor %.4f; %.2f per open over S=%.2f iterations) - the worn slot "
                    "is thin for what this container actually pays, not merely for its "
                    "size" % (label, SLOT_LABEL.get(s, s), per_open / spawn, ic,
                              ARMOR_SLOT_FLOOR_PER_SPAWN, per_open, spawn))
    report = {
        'label': label, 'tier': tier, 'classification': ic,
        'tables': [p.table for p in profs],
        'S': [p.S for p in profs],
        'S_eff': spawn,
        'drops_per_open': [p.expected_drops() for p in profs],
        'slot_mass': dict(agg_slot), 'total': total,
        'top_items': sorted(agg_item.items(), key=lambda kv: -kv[1])[:12],
        'weights': w,
    }
    return problems, report


def p_at_least_k_same(n_draws, item_probs, k=4):
    """P(some single item is drawn >= k times in n_draws), Poisson approximation over
    independent items (exact enough at these rates; the draws are independent picks).
    `item_probs` = iterable of per-draw probabilities for each item in the pool."""
    import math
    q = 1.0
    for p in item_probs:
        lam = n_draws * p
        if lam <= 0:
            continue
        # P(X < k) for X ~ Poisson(lam)
        term = math.exp(-lam)
        cum = term
        for i in range(1, k):
            term *= lam / i
            cum += term
        q *= max(0.0, min(1.0, cum))
    return 1.0 - q
