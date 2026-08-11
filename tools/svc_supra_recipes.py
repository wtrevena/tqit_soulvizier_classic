r"""svc_supra_recipes.py - THE THREE SUPRA-RECIPE LAWS (Will 2026-08-11).

WILL, VERBATIM (2026-08-11), LAW A
-----------------------------------
"ok for the four epic craftable reagent's, we need to change it so that one of the items
needed to craft the formula needs to be found in legendary like the rest of the craftable
supra recipes."

WILL, VERBATIM (2026-08-11), LAW B
-----------------------------------
"each craftable supra should have different requirements (we should not have two formulas
that both require stymphalian, plisskey, and deathweavers legtip)"

WILL, VERBATIM (2026-08-11), LAW C
-----------------------------------
"the last word should not be dropped in epic, only legendary"

So: every one of the 42 supra recipes must name AT LEAST ONE reagent whose only obtain
paths are Legendary-tier; NO TWO recipes may name the same reagent set; and no supra ITEM
may be reachable from a Normal- or Epic-tier loot surface.

WHAT WAS ACTUALLY WRONG, MEASURED ON THE build83 SHIP ARZ 44499f56 (51,253 records)
-----------------------------------------------------------------------------------
LAW A - exactly 4 offenders, and they are exactly the four Will named. Every one of the
other 38 recipes already carries a `u_l_*` / `um_l_*` / `us_l_*` reagent that no Normal or
Epic surface reaches. The four thrown craftables (Charon's Toll, Hati, The Last Word,
Sanguine Orbit) name three DRX blood-cult wands each, and all three tiers of that wand
family were reachable below Legendary:
    u_vit_wand      Legendary ic - EPIC chest pool (svc_unique_thrown_e01) + Legendary
    m_vit_wand_0N   Common ic     - Normal/Epic/Legendary
    mi_vit_wand_0N  Rare ic       - monster green, any difficulty
Nothing in those four recipes was Legendary-gated, which is why the shipped guide could
say "only 4 of the 42 are craftable at Epic".

LAW B - 5 duplicate groups covering 15 of the 42 craftables. Will's example is the
2-group; he did not know about the 6-group:
    x6 axes    Pyrophoric Lop + Shai'tan + Head Hunter's Axe
               -> Charybdis Unchained, Darkflame Devourer, Erysichthon's Undying Hunger,
                  Phoenix Ascendant, Scylla Unbound, Wrath of the Furies
    x3 maces   Sapros the Corrupter + Demeter's Sorrow + Animus
               -> Omega, Sword Fish, The Doomcaller's Maul
    x2 swords  Stymphalian Talon + Plissken + Deathweaver's Legtip    <- WILL'S EXAMPLE
               -> Aquimae, Crystal Tear of Nyx
    x2 swords  Mindrazor + Griefmaker + Sabertooth
               -> Ripulsar, Shrike
    x2 bows    Helios' Fury + Khamsin + Brigand's Bow
               -> Stormbringer, Ten Suns' Wrath
The four thrown recipes are NOT a duplicate group - their sets already differ in the
middle and green slots - so LAW B costs them nothing.

LAW C - 4 offenders, and 38 clean. The 42 supra ITEMS are craft-only by design and 38 of
them are named by no loot table anywhere in the database. The four b81 authored - the
supra thrown - were members of BOTH `svc_unique_thrown_e01` and `svc_unique_thrown_l01`,
and through `svc_unique_weapons_e01` the Epic membership reached **51 surfaces**: every
mod chest, every general's hoard, both polis vaults, the blood-cave mega chest and all 18
uber orb tables. That is what Will saw. Measured leak surface, per tier:
    Normal 0 supra items | EPIC 4 | Legendary 4
There is NO name collision to disambiguate: exactly one record in the database carries
the name The Last Word, `records\drxitem\supra\svc_wep_lastword.dbr` (itemNameTag
`tagSVCwpnLastWord`). No monster pays any of the four (0 monster carriers).

=============================================================================
LAW A: FOUR RECIPES, ONE SLOT EACH - AND THE COLLATERAL THAT FORCED IT
=============================================================================
THE ONE-MOVE FIX WAS BUILT FIRST AND IT IS WRONG. The tempting change was to take
`u_vit_wand` (Scepter of Eternal Love), the reagent all four thrown recipes share, off
`svc_unique_thrown_e01` - one membership, four recipes fixed, no formula edited. The
monster half of that analysis holds and is kept for the record: `u_vit_wand`'s four live
carriers (DRX blood-cult reavers `d_reaver_40/41/42` + the mod's own
`svc_leinth_guard_reaver`) read a THREE-ELEMENT per-difficulty loot array

    lootFinger2Item1 = [01_m_wands, 02_m_wands, 03_m_wands]
    lootFinger2Item3 = [xrecords\...\u_wand.dbr, xrecords\...\u_wand.dbr,
                        records\...\u_wand.dbr]

whose Normal and Epic entries the DRX authors disabled with their own `x`-prefix
convention, and only `03_m_wands` (the LEGENDARY master) reaches `u_wand.dbr`. So the
monster path was already Legendary-only and the mod's own Epic table was the sole
sub-Legendary path.

**THE COLLATERAL IS LAW C.** Measured on the same arz, the ENTIRE
`WeaponHunting_RangedOneHand` universe at itemClassification = Legendary is FIVE records:
`u_vit_wand` plus the four supra thrown. (The class splits Common 3 / Rare 3 / Epic 3 /
Legendary 5, and the three "Epic" ones are `records\item\formulaitems\*` craft RESULTS
that no loot table pays.) `SLB.TARGET_IC['e']` is **Legendary** - in this mod an
Epic-difficulty chest pays Legendary-classification gear - so rule C1 ("the thrown class
is payable at its own tier") can only ever be satisfied by one of those five records.
LAW C takes four of them off the Epic table. Promoting `u_vit_wand` would take the fifth,
leaving `svc_unique_thrown_e01` holding three COMMON wands and **redding C1 on every Epic
mod chest in the game**. The record universe offers no third option, and authoring a new
droppable Legendary thrown purely to feed a gate is a new item class, not a smallest
correct change. So the shared move is OFF THE TABLE and `u_vit_wand` stays at 100 on the
Epic thrown table as its C1 carrier.

LAW A IS THEREFORE SATISFIED PER RECIPE - four formulas, ONE reagent slot each. Slot 3 is
untouchable (it is the green, and Will's own MI exemption says a monster-unique may be
farmed at any difficulty); slot 1 is untouchable (it is `u_vit_wand`, the blood-cult
family anchor and the item that makes these read as thrown recipes at all). So slot 2 -
the plain Common `m_vit_wand_0N`, the least load-bearing thing in the recipe - carries the
gate, and the shape improves from "legendary thrown + a plain thrown + a green thrown" to
"legendary thrown + a Legendary-only component + a green thrown".

    Charon's Toll    m_vit_wand_03 -> Essence of Styx            the toll is paid on the
                                                                 river he ferries
    Hati             m_vit_wand_01 -> Crescent Moon of Artemis   the wolf is handed the
                                                                 moon he chases
    Sanguine Orbit   m_vit_wand_03 -> Blood of Ouranos           sky-blood, still falling
    The Last Word    m_vit_wand_02 -> Scepter of Thanatos        Death gets the last word

Four different item classes (amulet, artifact, spear, mace) so the four recipes do not
all send the player to one farm surface, and every one is Legendary-only and reachable
from 19 of 19 Legendary chest surfaces (proved by rule S3, not asserted).

WHAT IT COSTS: `m_vit_wand_01/02/03` stop being reagents of anything. They are NOT
orphaned - they are the Common thrown band that keeps rule C2 (thrown payable on Normal)
satisfiable, and they stay members of all three thrown tables.

=============================================================================
LAW B: TEN RECIPES, ONE FIELD EACH
=============================================================================
Each duplicate group keeps ONE member on the original reagents - the DRX-authored
original, so upstream's recipe stays upstream's recipe - and every other member changes
EXACTLY ONE reagent slot. Ten recipes, ten fields. Every replacement is chosen for the
craftable it builds (the amgoz1 rule: a reagent should read like the thing it becomes),
and every replacement is a record that was ALREADY in the game and already reachable from
19/19 Legendary chest surfaces, so no loot table moves and G1/G4 cannot regress.

  AXES (keep Darkflame Devourer on Pyrophoric Lop)
    Erysichthon's Undying Hunger  <- Erysichthon's Hunger   the same cursed appetite,
                                                            one tier down
    Phoenix Ascendant             <- Phoenix                the bird that supplies its
                                                            own ashes
    Wrath of the Furies           <- The Furies             the Erinyes hand over their
                                                            own edge
    Scylla Unbound                <- Cerberus' Bite         six heads learn from three
    Charybdis Unchained           <- Acheron's Touch        the drowning water of the
                                                            underworld river

  MACES (keep Omega on Sapros the Corrupter)
    Sword Fish                    <- Kraken's Fist          the sea's own club for the
                                                            sea's own spear
    The Doomcaller's Maul         <- Horn of Tiamat         the chaos-dragon's horn calls
                                                            the doom

  SWORDS (keep Crystal Tear of Nyx on Stymphalian Talon; keep Ripulsar on Mindrazor)
    Aquimae                       <- Pagos                  pagos is Greek for the frost
                                                            this blade is made of
    Shrike                        <- Stymphalian Talon      the butcher-bird takes the
                                                            bronze bird's talon

  BOWS (keep Stormbringer on Khamsin - a khamsin IS a storm)
    Ten Suns' Wrath               <- Qin Warbow             Hou Yi shot nine of the ten
                                                            suns out of a Chinese sky,
                                                            so he gets a Chinese bow

Every replacement is `itemClassification = Legendary` AND Legendary-only, so every
touched recipe satisfies LAW A by the same edit that satisfies LAW B. That claim is
CHECKED, not asserted: rule S3 runs `legendary_only` over every replacement, which is
how the first draft of this table was caught pointing Ten Suns' Wrath at Zhurong's
Firebow - a thematically perfect bow that an EPIC chest pool reaches, so it would have
de-duplicated the recipe while adding no gate at all.

CAUTION, AND IT ALMOST BIT THIS LANE: five of the replacement axes exist TWICE in the
database - once at `records\item\equipmentweapon\axe\` (live) and once at
`records\equipmentweapon\axe\` (no `item\` level). The second folder is 13 of the 14 DEAD
axes `docs/CHEST_DROP_MATRIX.md` names: nothing in the 51k-record database references
them. Every constant below spells the full LIVE path, and rule S3 re-proves at build time
that every replacement is chest-reachable, so a path typo cannot ship as a dead reagent.

=============================================================================
LAW C: FOUR MEMBERSHIPS OFF ONE TABLE
=============================================================================
The write lives in `svc_craft_thrown.THROWN_MEMBERS['e']` (the module that OWNS
`svc_unique_thrown_e01`; two modules must never write one record) and is documented
there. The rule is asserted here so the law is stated where it is checked:

  * no supra ITEM may be reachable from a Normal- or Epic-tier chest/orb surface;
  * "only legendary" is a RELOCATION, not a retirement - the Legendary table is
    untouched, so R-186's "make the legendary thrown weapons droppable" still holds at
    the tier Will kept it for. S4 therefore also fails if the Legendary side goes to
    zero, so a later lane cannot quietly finish the job Will did not ask for.

=============================================================================
THE GATES (all fail loud, all in the craft gate family)
=============================================================================
  S1  every supra recipe names >= 1 reagent whose ONLY obtain paths are Legendary-tier.
  S2  no two supra craftables name an identical reagent multiset.
  S3  every reagent this module writes still resolves AND is reachable from the
      Legendary chest pool (the dead-twin guard).
  S4  no supra ITEM is reachable from a Normal- or Epic-tier chest/orb surface, and the
      four that are meant to stay droppable are still reachable on Legendary.
Negative tests: `py tools/debug/negtest_supra_recipe_laws.py <arz>`.
Standalone gate: `py tools/gate_supra_recipe_laws.py <arz>`.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import svc_craft_thrown as SCT
import svc_loot_breadth as SLB
from svc_loot_breadth import _n, _sc, Lookup, Expander

TIERS = SLB.TIERS

# ─────────────────────────────────────────────────────────────────────────────
# LAW C - the table the four supra thrown leave, and the one they stay on.
# ─────────────────────────────────────────────────────────────────────────────
# The write lives in `svc_craft_thrown.THROWN_MEMBERS`; these constants are what rule S4
# asserts, so the law is stated where it is checked and cannot drift from where it is
# applied. `EPIC_THROWN_TABLE` is also the handle the negative tests use to plant the
# exact shipped defect back.
EPIC_THROWN_TABLE = r'records\item\loottables\svc\svc_unique_thrown_e01.dbr'
LEG_THROWN_TABLE = r'records\item\loottables\svc\svc_unique_thrown_l01.dbr'
# The C1 carrier that must NOT be promoted off the Epic table (see the header): the whole
# Legendary-classification thrown universe is this record plus the four supra thrown.
EPIC_THROWN_C1_CARRIER = r'records\drxitem\equipmentweapon\wands\u_vit_wand.dbr'
# The supra items that are DELIBERATELY droppable, and only on Legendary. Every other
# supra craftable must be reachable from no loot table at all.
_SUP = r'records\drxitem\supra\%s.dbr'
LEGENDARY_DROPPABLE_SUPRAS = tuple(_SUP % n for n in (
    'svc_wep_charonstoll', 'svc_wep_hati', 'svc_wep_lastword', 'svc_wep_sanguineorbit'))

# ─────────────────────────────────────────────────────────────────────────────
# LAW A + LAW B - the fourteen one-field recipe edits, keyed by FORMULA record.
# ─────────────────────────────────────────────────────────────────────────────
# {formula record: (slot number, old reagent, new reagent)}. The slot is committed, not
# searched, so a future reagent reshuffle cannot silently retarget the edit; `apply`
# fails loud if the slot does not currently hold `old`.
#
# NOTE ON FORMULA RECORDS: a craftable can be built by more than one formula record
# (59 formulas, 42 craftables) and the pairs are NOT named after the craftable - e.g.
# Phoenix Ascendant is built by `zrecipes\wep_axe_formula` while Darkflame Devourer is
# built by `recipes\wep_axe_formula`. Every entry below was read off the built arz by
# following `artifactName`, never guessed from a file name. `apply` re-derives the
# formula -> result map from the database and fails loud if any keyed formula does not
# build the craftable this table says it does.
_ITEM = r'records\item\equipmentweapon\%s\%s.dbr'
_XP = r'records\xpack\item\equipmentweapons\%s\%s.dbr'
_ZR = r'records\drxitem\supra\zrecipes\%s.dbr'
_RC = r'records\drxitem\supra\recipes\%s.dbr'
_SUPRA = r'records\drxitem\supra\%s.dbr'
_WAND = r'records\drxitem\equipmentweapon\wands\%s.dbr'
_AMULET = r'records\item\equipmentamulet\%s.dbr'
_ARTIFACT = r'records\xpack\item\artifacts\%s.dbr'

RECIPE_OVERRIDES = {
    # ---- LAW A: the four thrown, slot 2 (the plain Common wand) carries the gate ------
    # Slot 1 (u_vit_wand) is the Epic tier's C1 carrier and the family anchor; slot 3 is
    # the green and Will's MI exemption protects it. Each replacement is a different item
    # CLASS so the four recipes do not funnel the player onto one farm surface.
    _ZR % 'svc_thrown_charonstoll_formula': (
        _SUPRA % 'svc_wep_charonstoll', 2,
        _WAND % 'm_vit_wand_03', _AMULET % 'u_l_essenceofstyx'),
    _ZR % 'svc_thrown_hati_formula': (
        _SUPRA % 'svc_wep_hati', 2,
        _WAND % 'm_vit_wand_01', _ARTIFACT % 'e_da_crescentmoonofartemis'),
    _ZR % 'svc_thrown_sanguineorbit_formula': (
        _SUPRA % 'svc_wep_sanguineorbit', 2,
        _WAND % 'm_vit_wand_03', _ITEM % ('spear', 'u_l_bloodofouranos')),
    _ZR % 'svc_thrown_lastword_formula': (
        _SUPRA % 'svc_wep_lastword', 2,
        _WAND % 'm_vit_wand_02', _ITEM % ('club', 'u_l_scepterofthanatos')),
    # ---- AXES: 5 of the 6-way group (Darkflame Devourer keeps Pyrophoric Lop) ------
    _ZR % 'svc_axe_erysichthon_formula': (
        _SUPRA % 'svc_wep_erysichthon', 1,
        _XP % ('axe', 'u_l_002'), _ITEM % ('axe', "u_l_erysichthon'shunger")),
    _ZR % 'wep_axe_formula': (                       # builds Phoenix Ascendant
        _SUPRA % 'svc_wep_phoenix', 1,
        _XP % ('axe', 'u_l_002'), _ITEM % ('axe', 'u_l_phoenix')),
    _ZR % 'svc_axe_furies_formula': (
        _SUPRA % 'svc_wep_furies', 1,
        _XP % ('axe', 'u_l_002'), _ITEM % ('axe', 'u_l_thefuries')),
    _ZR % 'svc_axe_scylla_formula': (
        _SUPRA % 'svc_wep_scylla', 1,
        _XP % ('axe', 'u_l_002'), _ITEM % ('axe', "u_l_cerberus'bite")),
    _ZR % 'svc_axe_charybdis_formula': (
        _SUPRA % 'svc_wep_charybdis', 1,
        _XP % ('axe', 'u_l_002'), _ITEM % ('axe', "u_l_acheron'stouch")),
    # ---- MACES: 2 of the 3-way group (Omega keeps Sapros the Corrupter) ------------
    _ZR % 'wep_club_formula': (                      # builds Sword Fish
        _SUPRA % 'svc_wep_swordfish', 1,
        _ITEM % ('club', 'u_l_saprosthecorrupter'), _ITEM % ('club', 'u_l_krakensfist')),
    _ZR % 'svc_mace_doomherald_formula': (
        _SUPRA % 'svc_wep_doomherald', 1,
        _ITEM % ('club', 'u_l_saprosthecorrupter'), _ITEM % ('club', 'u_l_hornoftiamat')),
    # ---- SWORDS: Will's own example, plus the Mindrazor pair ------------------------
    _ZR % 'wep_dagger_formula': (                    # builds Aquimae
        _SUPRA % 'svc_wep_aquimae', 1,
        _ITEM % ('sword', 'u_l_stymphaliantalon'), _ITEM % ('sword', 'u_l_pagos')),
    _RC % 'wep_sword_formula': (                     # builds Shrike
        _SUPRA % 'wep_sword', 1,
        _ITEM % ('sword', 'u_l_mindrazor'), _ITEM % ('sword', 'u_l_stymphaliantalon')),
    # ---- BOWS: Stormbringer keeps Khamsin (a khamsin IS a storm) --------------------
    _ZR % 'wep_bow_formula': (                       # builds Ten Suns' Wrath
        _SUPRA % 'svc_wep_tensunswrath', 2,
        _ITEM % ('bow', 'u_e_khamsin'), _ITEM % ('bow', 'u_l_qinwarbow')),
}

# Every record RECIPE_OVERRIDES introduces, for rule S3's dead-twin guard.
NEW_REAGENTS = tuple(sorted({new for _r, _s, _old, new in RECIPE_OVERRIDES.values()}))

# The folder the 13 dead axes live in (no `item\` level). A reagent must never come from
# here: nothing in the database references it, so it would be uncraftable-by-typo.
DEAD_RECORD_PREFIXES = (r'records\equipmentweapon\\',)


# ─────────────────────────────────────────────────────────────────────────────
# TIER READING (S1's evidence)
# ─────────────────────────────────────────────────────────────────────────────
# A loot table's difficulty tier, read off its own record NAME. This is the house
# convention that `svc_loot_breadth.infer_tier` already reads for chest tables, widened
# to the base game's `0N_` act/master prefixes so the walk can classify the tables a
# MONSTER names as well as the ones a chest names.
_TIER_SUFFIX_RE = re.compile(r'_([nel])0\d[a-z]?\.dbr$')
_ACT_PREFIX_RE = re.compile(r'\\(0[123])_(?:act|master|m_|l_|e_|n_)')
_RELIC_RE = re.compile(r'\\relics\\(0[123])_act')
_TIER_FOR_NUM = {'01': 'n', '02': 'e', '03': 'l'}


def table_tier(path):
    """'n' | 'e' | 'l' | None for a loot-table record name."""
    p = _n(path)
    m = _TIER_SUFFIX_RE.search(p)
    if m:
        return m.group(1)
    for rx in (_RELIC_RE, _ACT_PREFIX_RE):
        m = rx.search(p)
        if m:
            return _TIER_FOR_NUM.get(m.group(1))
    return None


def legendary_only(db, lk, ex, reagent, pools=None):
    """(bool, reason) - are ALL of `reagent`'s obtain paths Legendary-tier?

    Four conditions, every one measured off the database:
      1. `itemClassification == Legendary`. R-100 #17 (tier discipline) confines a
         Legendary item to `_l`-tier hosts, so this is what makes the other three
         checks a proof rather than a spot sample;
      2. no Normal-tier and no Epic-tier chest pool reaches it;
      3. a LEGENDARY chest pool DOES reach it - Will's completability law is not
         suspended by his gating law, and "gated behind nothing" is not a pass;
      4. no loot table in its upward reference closure is a Normal- or Epic-tier table.
         This is the check that catches a MONSTER path: a reaver's Epic loot slot names
         an `02_` master, and an `02_` master is not Legendary.
    """
    pools = pools if pools is not None else {t: SCT.chest_pool(db, lk, ex, t)
                                             for t in TIERS}
    rl = _n(reagent)
    real = lk.real(reagent)
    if not real:
        return False, 'record is absent from the database'
    ic = str(_sc(db.get_field_value(real, 'itemClassification')) or '')
    if ic != 'Legendary':
        return False, 'itemClassification=%s (only a Legendary item is tier-confined)' % (
            ic or 'none')
    if rl in pools['n']:
        return False, 'a NORMAL-tier chest pool reaches it'
    if rl in pools['e']:
        return False, 'an EPIC-tier chest pool reaches it'
    if rl not in pools['l']:
        return False, 'no Legendary chest pool reaches it (uncompletable, not gated)'
    _monsters, tables = SCT.mi_monster_sources(db, lk, reagent)
    bad = sorted(t for t in tables if table_tier(t) in ('n', 'e'))
    if bad:
        return False, 'named by %d non-Legendary-tier loot table(s), e.g. %s' % (
            len(bad), _n(bad[0]).rsplit('\\', 1)[-1])
    return True, 'Legendary-tier surfaces only'


# ─────────────────────────────────────────────────────────────────────────────
# SHARED DERIVATION
# ─────────────────────────────────────────────────────────────────────────────
def supra_drop_paths(db, lk, ex, forms=None, pools=None):
    r"""LAW C's evidence: {supra craftable: (tiers whose CHEST/ORB pool reaches it,
    [loot tables that name it directly])}.

    Direct naming is the exact test for "reachable from any loot table at all": an
    indirect path (a table naming a table naming the item) still has to begin with SOME
    table naming it, so a craftable no table names is reachable from nothing. The pool
    view is what answers "at which difficulty", and it is the same measurement the
    reagent rules and the shipped guide use, so the three cannot disagree."""
    forms = forms if forms is not None else SCT.uber_formulas(db, lk)
    pools = pools if pools is not None else {t: SCT.chest_pool(db, lk, ex, t)
                                             for t in TIERS}
    rev = SCT.reverse_index(db)
    out = {}
    for result in sorted({_n(r) for r in forms.values()}):
        tables = sorted(_n(h) for h in rev.get(result, ())
                        if SLB.is_loot_table(lk, h))
        tiers = tuple(t for t in TIERS if result in pools[t])
        out[result] = (tiers, tables)
    return out


def recipe_sets(db, lk, forms=None):
    """{craftable: (formulas, reagent multiset as a sorted tuple)}.

    A craftable built by several formula records must have ONE reagent set - two
    formulas for the same item with different reagents is itself a defect, so it is
    reported (S2b) rather than silently collapsed."""
    forms = forms if forms is not None else SCT.uber_formulas(db, lk)
    by_result = defaultdict(dict)
    for f, result in forms.items():
        by_result[_n(result)][_n(f)] = tuple(sorted(_n(x)
                                                    for x in SCT.reagents_of(db, f)))
    return by_result


# ─────────────────────────────────────────────────────────────────────────────
# WRITE SIDE
# ─────────────────────────────────────────────────────────────────────────────
def apply_recipe_overrides(db, lk=None, verbose=True):
    """LAW A + LAW B: fourteen recipes, ONE reagent slot each (4 thrown gated, 10
    de-duplicated). Idempotent; fails loud on any drift."""
    lk = lk or Lookup(db)
    forms = SCT.uber_formulas(db, lk)
    forms_l = {_n(f): _n(r) for f, r in forms.items()}
    changes = []
    for formula, (want_result, slot, old, new) in sorted(RECIPE_OVERRIDES.items()):
        real = lk.real(formula)
        if not real:
            raise SystemExit("svc_supra_recipes: formula record does not resolve: %s"
                             % formula)
        built = forms_l.get(_n(real))
        if built is None:
            raise SystemExit("svc_supra_recipes: %s is not a supra formula in this "
                             "database (it builds nothing under \\supra\\)" % formula)
        if built != _n(want_result):
            raise SystemExit(
                "svc_supra_recipes: %s builds %s, but the override table says %s - the "
                "formula/result map moved and the ten edits must be re-derived"
                % (_n(real).rsplit('\\', 1)[-1], built, _n(want_result)))
        target = lk.real(new)
        if not target:
            raise SystemExit("svc_supra_recipes: replacement reagent does not resolve: "
                             "%s (for %s)" % (new, formula))
        field = 'reagent%dBaseName' % slot
        cur = _sc(db.get_field_value(real, field))
        curl = _n(cur) if isinstance(cur, str) else ''
        if curl == _n(target):
            continue                                   # already applied: idempotent
        if curl != _n(old):
            raise SystemExit(
                "svc_supra_recipes: %s %s holds %r, expected %r - another lane moved "
                "this reagent, so the override must be re-derived rather than clobbered"
                % (_n(real).rsplit('\\', 1)[-1], field, curl, _n(old)))
        SLB._set_str(db, real, field, target)
        changes.append('%s %s: %s -> %s'
                       % (_n(real).rsplit('\\', 1)[-1], field,
                          _n(old).rsplit('\\', 1)[-1][:-4],
                          _n(target).rsplit('\\', 1)[-1][:-4]))
    if verbose:
        for c in changes:
            print("  SUPRA/LAWS: recipe reagent repointed - %s" % c)
    return changes


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT SIDE
# ─────────────────────────────────────────────────────────────────────────────
def audit_supra_laws(db, lk=None, ex=None, verbose=False):
    """S1 + S2 + S3 over one (final) database. Returns (problems, stats)."""
    lk = lk or Lookup(db)
    ex = ex or Expander(db, lk)
    problems = []
    pools = {t: SCT.chest_pool(db, lk, ex, t) for t in TIERS}
    forms = SCT.uber_formulas(db, lk)
    by_result = recipe_sets(db, lk, forms)

    # ---- S1 -----------------------------------------------------------------
    verdicts = {}
    gated = {}
    for result, per_formula in sorted(by_result.items()):
        reagents = sorted({r for rg in per_formula.values() for r in rg})
        good = []
        for r in reagents:
            if r not in verdicts:
                verdicts[r] = legendary_only(db, lk, ex, r, pools)
            if verdicts[r][0]:
                good.append(r)
        gated[result] = good
    offenders = sorted(r for r, g in gated.items() if not g)
    if offenders:
        problems.append(
            "S1 %d of %d supra craftable(s) can be completed WITHOUT any Legendary-only "
            "reagent (Will 2026-08-11: one of the items must be found in legendary like "
            "the rest): %s"
            % (len(offenders), len(gated),
               ', '.join(_n(x).rsplit('\\', 1)[-1][:-4] for x in offenders)))

    # ---- S2 -----------------------------------------------------------------
    by_set = defaultdict(list)
    for result, per_formula in by_result.items():
        sets = set(per_formula.values())
        if len(sets) > 1:
            problems.append(
                "S2b %s is built by %d formula records that do NOT agree on its reagents "
                "(%s) - a craftable has one recipe"
                % (_n(result).rsplit('\\', 1)[-1][:-4], len(per_formula),
                   ' | '.join(', '.join(y.rsplit('\\', 1)[-1][:-4] for y in s)
                              for s in sorted(sets))))
        by_set[sorted(sets)[0]].append(result)
    dupes = {k: sorted(v) for k, v in by_set.items() if len(v) > 1}
    if dupes:
        detail = '; '.join(
            '%s share [%s]' % (' + '.join(x.rsplit('\\', 1)[-1][:-4] for x in v),
                               ', '.join(y.rsplit('\\', 1)[-1][:-4] for y in k))
            for k, v in sorted(dupes.items(), key=lambda z: -len(z[1])))
        problems.append(
            "S2 %d group(s) of supra craftables name an IDENTICAL reagent set (Will "
            "2026-08-11: each craftable supra should have different requirements): %s"
            % (len(dupes), detail))

    # ---- S3 -----------------------------------------------------------------
    for new in NEW_REAGENTS:
        real = lk.real(new)
        if not real:
            problems.append("S3 replacement reagent %s does not resolve in the database"
                            % new)
            continue
        if any(_n(new).startswith(p.replace('\\\\', '\\')) for p in DEAD_RECORD_PREFIXES):
            problems.append(
                "S3 replacement reagent %s comes from the DEAD `records\\equipmentweapon\\` "
                "folder (nothing in the database references it); the live twin lives "
                "under `records\\item\\equipmentweapon\\`" % new)
        if _n(new) not in pools['l']:
            problems.append(
                "S3 replacement reagent %s is not reachable from any Legendary chest "
                "pool, so the recipe it entered is uncompletable"
                % _n(new).rsplit('\\', 1)[-1][:-4])

    # ---- S4 (LAW C) ---------------------------------------------------------
    # "the last word should not be dropped in epic, only legendary". Two halves: nothing
    # supra on a sub-Legendary surface, and the four that Will kept droppable still are.
    drops = supra_drop_paths(db, lk, ex, forms, pools)
    keep = {_n(x) for x in LEGENDARY_DROPPABLE_SUPRAS}
    below = sorted((r, t) for r, (t, _tb) in drops.items() if 'n' in t or 'e' in t)
    if below:
        problems.append(
            "S4 %d supra ITEM(s) are reachable from a sub-Legendary loot surface (Will "
            "2026-08-11: the last word should not be dropped in epic, only legendary): %s"
            % (len(below), '; '.join('%s on %s' % (r.rsplit('\\', 1)[-1][:-4],
                                                   '/'.join(x.upper() for x in t))
                                     for r, t in below)))
    stray = sorted(r for r, (_t, tb) in drops.items() if tb and r not in keep)
    if stray:
        problems.append(
            "S4b %d craft-only supra ITEM(s) are named by a loot table at all (the other "
            "38 craftables are built, never found): %s"
            % (len(stray), ', '.join('%s <- %s' % (r.rsplit('\\', 1)[-1][:-4],
                                                   drops[r][1][0].rsplit('\\', 1)[-1][:-4])
                                     for r in stray[:6])))
    unpaid = sorted(r for r in keep if r in drops and 'l' not in drops[r][0])
    if unpaid:
        problems.append(
            "S4c %d supra thrown weapon(s) that R-186 made droppable are no longer "
            "reachable on LEGENDARY either - \"only legendary\" is a relocation, not a "
            "retirement: %s"
            % (len(unpaid), ', '.join(r.rsplit('\\', 1)[-1][:-4] for r in unpaid)))

    stats = {'craftables': len(by_result), 'formulas': len(forms),
             'distinct_sets': len(by_set), 'duplicate_groups': len(dupes),
             'legendary_only_reagents': len([r for r, v in verdicts.items() if v[0]]),
             'reagents': len(verdicts),
             'min_gated': min((len(v) for v in gated.values()), default=0),
             'gated': gated, 'verdicts': verdicts, 'drops': drops,
             'droppable_supras': len([r for r, (t, _tb) in drops.items() if t]),
             'sub_legendary_supras': len(below)}
    if verbose:
        print("    supra laws: %d craftables / %d formulas, %d distinct reagent sets, "
              "%d duplicate group(s); %d of %d reagents are Legendary-only; every "
              "craftable carries at least %d of them; %d supra item(s) droppable "
              "(%d below Legendary)"
              % (stats['craftables'], stats['formulas'], stats['distinct_sets'],
                 stats['duplicate_groups'], stats['legendary_only_reagents'],
                 stats['reagents'], stats['min_gated'], stats['droppable_supras'],
                 stats['sub_legendary_supras']))
    return problems, stats
