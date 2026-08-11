r"""svc_craft_thrown.py - THE CRAFT-CHAIN + THROWN-CLASS CONTRACT (Will 2026-08-10).

WILL, VERBATIM (2026-08-10)
---------------------------
"i meant do the mythic formulas drop. they can drop in normal as well, but the
legendary items should not drop in normal. All of the reagents need to be droppable
somewhere in the game, ideally from chests since that is where people will look. if
players farm legendary long enough, they should be able to find all the reagents
without having to farm a specific area or a specific character (except for the monster
unique droppable items like the green items that are needed to build some of the
formulas...). Yes we should make the legendary thrown weapons droppable."

THREE DEFECTS, ALL MEASURED ON THE LIVE arz 435cc485 (51,234 records, build77 era)
----------------------------------------------------------------------------------
(A) MYTHIC FORMULAS CANNOT DROP ON NORMAL. The 42 uber ("supra") craftables are built
    by 59 formula records; 42 of those sit on `arcaneformulae\supra.dbr`. The base game
    wires that pool into the EPIC and LEGENDARY act tables only:
        02_act{1..4}_arcaneformulae = LootMasterTable [ ..._table (98), supra (2) ]
        03_act{1..4}_arcaneformulae = LootMasterTable [ ..._table (95), supra (5) ]
        01_act{1..4}_arcaneformulae = LootItemTable_FixedWeight, 25 base formulas, NO supra
    So a Normal-tier mod chest reached 0 of 42 uber formulas. Will exempts FORMULAS from
    the tier rule (they are `itemClassification = Common` ItemArtifactFormula records, so
    no legendary GEAR moves at all) while legendary ITEMS stay out of Normal.

(B) 36 OF THE 78 UBER REAGENTS ARE UNREACHABLE FROM A LEGENDARY CHEST. Measured split:
       19 MI / "green" (itemClassification = Rare, the `mi_l_*` monster-infrequent items)
          -> EXEMPT BY WILL'S OWN WORDS, but each one must be PROVEN monster-farmable.
          ONE of them, `mi_l_gigantes2`, has ZERO live carriers (its only carrier is the
          dev duplicate `copy of anapaest_45`; the LIVE `anapaest_45` names placeholder
          `equip\bogus\*` ITEM records instead of the gigantes club tables, and the
          `03_master_legendary` that would have re-hung them has 0 holders). The
          exemption's whole premise is "a monster drops it", so a green item that NO
          live monster drops is NOT exempt - see rule 2 below.
        8 ordinary base uniques that live only on act-2/act-3 banded tables the chest
          pools never name (3 torso, 3 amulet, 2 ring).
        6 IT "divine artifacts" (ItemArtifact) - craftable from base arcane formulae the
          chests DO drop, but not droppable themselves; 0 of 292 artifacts were reachable
          from any mod chest at any difficulty.
        3 records THIS MOD'S DATABASE DOES NOT CARRY:
          `records\xpack2\item\equipmentweapons\1hranged\{u_l_08,u_e_06,mi_l_machae}.dbr`
          are RAGNAROK (xpack2) records. PRECISION (measured, and the round-1 wording was
          loose): they DO exist in an installed base-game database if the player owns
          Ragnarok - 12,483 `records\xpack2\*` in Will's 74,013-record install. They are
          still unreachable for a player of this mod: xpack2 ships only with the Ragnarok
          DLC, and R-210 caps the playable arc at Immortal Throne with the Atlantis /
          Ragnarok / Eternal Embers act pages suppressed. All four thrown craftables
          (Charon's Toll, Hati, The Last Word, Sanguine Orbit) name exactly those three,
          so those four formulas were DEAD IN PRACTICE for everyone playing the mod.
          Rule G0 asks the question it can answer: is the reagent absent from the MOD db.

(C) THE THROWN CLASS IS UNPAYABLE. 14 `WeaponHunting_RangedOneHand` records exist
    (5 Legendary, 3 Epic - all base craft results -, 3 Rare, 3 Common) and there is no
    "unique one-hand-ranged" loot table in this era's database for a master to name, so
    0 of 5 legendary thrown were reachable from anything.

THE FIX (this module is the ONE implementation; nothing may re-derive it)
-------------------------------------------------------------------------
1. MYTHIC FORMULAS ON NORMAL. `supra.dbr` is added as ONE new member of each
   `01_act{1..4}_arcaneformulae` table, at a weight computed to land on
   NORMAL_SUPRA_SHARE of that table's own total - so it is RARER on Normal (1%) than the
   base game already makes it on Epic (2%) and Legendary (5%). Base-game precedent for a
   `LootItemTable_FixedWeight` naming a loot TABLE in a `lootNameN` slot: 56 shipped
   records do it (e.g. `raremisc\01_rareunique_all.dbr` names `weapons\unique\sword_n01`).
   Nothing is removed and no weight is lowered.

2. REAGENT COMPLETABILITY. The 8 ordinary + 6 artifact reagents (plus the one orphaned
   MI, below) are placed into mod-owned `svc_craft_reagents_*_l01` tables that are added
   as MEMBERS of the LEGENDARY-tier hosts the chest pools already reach.
   SPREAD IS PART OF THE CONTRACT, not a side effect. Will: "without having to farm a
   specific area or a SPECIFIC CHARACTER". Measured over the 19 legendary mod chest
   tables: `unique_torso_l01`, `amulet_l01`, `finger_l01` and `unique_1h_l01` are reached
   by 19/19, but `04_l_misc` by 1/19 - and that ONE surface is `svc_uberorb_apex_l01c`,
   the apex uber-boss orb. Hanging the artifact reagents off `04_l_misc` ALONE therefore
   put six reagents behind exactly one boss family, which is the very thing Will ruled
   out. They are now hung off `amulet_l01` and `finger_l01` as well (the jewellery /
   trinket branch, the closest kin a divine artifact has), so all five families are
   19/19, and rule G4 fails the build if any non-MI reagent falls under half the
   legendary chest surfaces.
   THE ORPHANED GREEN: `mi_l_gigantes2` (needed by Doomherald, Swordfish and Omega) has
   no live monster at all, so it is chest-placed like an ordinary reagent - on
   `unique_1h_l01`, its own weapon class - and rule G3 makes "MI with no live carrier and
   no chest placement" a BUILD FAILURE rather than a warning.
   LEGENDARY-ONLY BY CONSTRUCTION for the 14: every one is
   `itemClassification = Legendary`, so it may only ever enter an `_l01` / `_l`-tier host
   (R-100 #17); the orphaned green is `Rare`, which is a strictly lower rung and can
   never breach the tier law. The 4 dead thrown formulas are repointed off the three
   Ragnarok ghosts onto thrown records that EXIST in this era (the DRX vit wands), which
   is the only possible fix - a record that is not in the database cannot be put into a
   pool - and they are repointed in the SHAPE the database's own recipes use (below).

3. THROWN. `records\item\loottables\svc\svc_unique_thrown_{n,e,l}01.dbr`, a
   `LootItemTable_FixedWeight` per tier (FixedWeight, not DynWeight, ON PURPOSE: every
   legendary thrown record is itemLevel 65, which sits OUTSIDE the 46-56 band the
   `_e01` DynWeight class tables use, so a level-banded table could never pay one on the
   Epic tier). Membership carries the tier law:
       n -> the two itemLevel-30 wands (Rare + Common). ZERO Legendary.
       e -> the 5 Legendary thrown + the 3 Common vit wands (reagent reachability).
       l -> the 5 Legendary thrown + the 3 Common vit wands (reagent reachability).
   The table is wired into `svc_loot_breadth._master_members` as the SEVENTH class of the
   `svc_unique_weapons_{tier}01` masters, so thrown becomes payable everywhere those
   masters are named (every mod chest's weapon row AND its guaranteed slot).
   A DELIBERATE OMISSION, stated so it is a choice and not an oversight: this era's only
   EPIC-classification thrown records (`f_n_kaskeron`, `f_l_qilinseternalpyre`,
   `f_l_godshatter`) are BASE-GAME craft results. They were NOT made droppable - making a
   base craft result fall out of a chest devalues base crafting, and Will asked for the
   LEGENDARY thrown to drop, not the Epic ones. The consequence is that Normal's thrown
   band cannot pay at the tier's target classification (Epic), so the Normal master
   weight is derived from the 2-record Normal band (100) instead of the 5-record
   legendary band (250) - the class stops consuming an end-game-sized share of a Normal
   weapon roll for level-30 filler.

NON-REDUCTION LAW (R-180, Will 2026-08-08): no member is removed, no chance or weight is
lowered, no numSpawn equation is touched. Every edit here is additive or a strict raise.

TIER LAW (R-100 #17): asserted, not assumed - `audit_db` re-proves that the Normal branch
reaches ZERO legendary GEAR after this module runs, and the thrown Normal table is the
only new Normal-side membership it creates.

CROSS-LANE RECORD OVERLAP (do NOT read this as "disjoint"). This module writes no chest
or hoard `FixedItemLoot` record, no orb table and no hoard weight - but it is NOT
record-disjoint from the concurrent lanes. Record-measured, baseline arz -> lane arz:
8 records ADDED, 0 REMOVED, 16 MODIFIED by this lane (24 written in total), and THREE of
the 16 - `records\item\loottables\svc\svc_unique_weapons_{n,e,l}01.dbr` - are also
rewritten by
`fix/armor-loot-breadth` (b80), which changes every member weight in the same producer,
`svc_loot_breadth._master_members`. That is a genuine write/write collision on three
records. BINDING RESOLUTION (not a suggestion): on merge, thrown keeps a QUARTER of a
class weight on e/l and a tenth of one on n, i.e. `_CLASS_WEIGHT // 4` and
`_CLASS_WEIGHT // 10` under b80's constants, because the derivation below is about the
size of the thrown class (5 legendary records against a 17-24 record class), not about
the absolute number. Whoever merges re-derives from b80's `_CLASS_WEIGHT`; nobody picks
a side by accident.

Standalone gate twin: `py tools/gate_craft_thrown_breadth.py <arz>`.
Negative tests:       `py tools/debug/negtest_craft_thrown.py <arz>`.
"""
import sys
from collections import defaultdict
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
import svc_loot_breadth as SLB
from svc_loot_breadth import _n, _sc, Lookup, Expander       # ONE resolver, one expander

TIERS = SLB.TIERS

# ─────────────────────────────────────────────────────────────────────────────
# (1) MYTHIC FORMULAS ON EVERY DIFFICULTY
# ─────────────────────────────────────────────────────────────────────────────
SUPRA_POOL = r'records\xpack\item\loottables\arcaneformulae\supra.dbr'
SUPRA_SPECIAL = r'records\xpack\item\loottables\arcaneformulae\supra_special.dbr'
NORMAL_FORMULA_TABLES = tuple(
    r'records\xpack\item\loottables\arcaneformulae\01_act%d_arcaneformulae.dbr' % i
    for i in (1, 2, 3, 4))
# BOTH supra pools are needed: MEASURED on the built arz, `supra` carries 42 formula
# leaves and `supra_special` 43, and the two rosters are NOT the same.
# `artifact_mortoksskull_formula` (Mortok's Skull) exists
# ONLY on supra_special, which the base game wires into `03_act4_arcaneformulae_sp`
# (Legendary) alone - so wiring supra by itself would leave exactly one of the 42
# craftables formula-less on Normal, and the F1 gate reds. This is the same pair R-9
# ("let the Rite of the Undivided drop wherever else any supra / uber weapons formulas
# have a chance to drop") already treats as THE two supra pools.
#
# Shares are measured, not chosen: the base game gives `supra` 2% of the Epic act tables
# and 5% of the Legendary ones. Normal sits one rung BELOW the rarest of those (1%), and
# supra_special - the rarer pool, which the base game hides behind a dedicated `_sp`
# table - takes half of that again. Total mythic share on Normal 1.5%, still under Epic.
NORMAL_SUPRA_SHARE = 0.01
NORMAL_SUPRA_SPECIAL_SHARE = 0.005
NORMAL_FORMULA_POOLS = ((SUPRA_POOL, NORMAL_SUPRA_SHARE),
                        (SUPRA_SPECIAL, NORMAL_SUPRA_SPECIAL_SHARE))

# ─────────────────────────────────────────────────────────────────────────────
# (3) THE THROWN CLASS
# ─────────────────────────────────────────────────────────────────────────────
THROWN_CLASS = 'WeaponHunting_RangedOneHand'
THROWN_TABLE = {t: r'records\item\loottables\svc\svc_unique_thrown_%s01.dbr' % t
                for t in TIERS}
# A clean, small `LootItemTable_FixedWeight` to clone the shape from (Class + template).
_THROWN_DONOR = SUPRA_POOL
_THROWN_CLEAR_SLOTS = 48        # supra has 42 members; clear well past it after cloning

_WAND = r'records\drxitem\equipmentweapon\wands\%s.dbr'
_SUPRA = r'records\drxitem\supra\%s.dbr'
# The mass ONE weapon class carries in the aggregate master, taken from b80's own
# constant rather than copied - so if a later balance lane re-scales the master, thrown
# re-scales with it instead of silently becoming a rounding error again (the exact defect
# the b80 merge exposed; see THROWN_MASTER_WEIGHT).
_THROWN_CLASS_WEIGHT = SLB._CLASS_WEIGHT // 4
# (path, weight) per tier.
#
# ROUND 1 made the DRX legendary wand the common outcome (100) and each craft-tier supra a
# rare prize at a tenth of it (10), with the three COMMON vit wands at 5 because they are
# here for one reason only - they are reagents of the four thrown recipes, and Will's rule
# is that a legendary farmer must be able to find every reagent from chests.
#
# ROUND 2, AT THE b80 MERGE: this shape is KEPT, and it was re-tested rather than assumed.
# The alternative - flattening the five legendary thrown to uniform - is only forced if
# thrown carries a full class's mass, because b80's D5 caps any single item at 3.0% of a
# surface and a member holding 71% of a class-parity thrown table puts `u_vit_wand` at
# 3.2%-5.2% on 17 of the 42 surfaces. At the quarter-class weight this ruling actually
# ships, the worst single-item share in the whole mod is a SHIELD at 2.57%, and no thrown
# record appears in the D5 ranking at all. So the prize weighting survives, measured.
_COMMON_WAND_WEIGHT = 5
_SUPRA_THROWN_WEIGHT = 10       # a tenth of the ordinary legendary wand: these are prizes
# ─── WILL 2026-08-11 (LAW C): "the last word should not be dropped in epic, only
# legendary." ────────────────────────────────────────────────────────────────────────
# THE DEFECT HE SAW, LOCATED IN THE BYTES. There is exactly ONE record in the whole
# 51,253-record database whose name is The Last Word - `records\drxitem\supra\
# svc_wep_lastword.dbr` (no same-name base item, so nothing to disambiguate). It, and its
# three siblings, were members of `svc_unique_thrown_e01` as well as the Legendary table,
# and through `svc_unique_weapons_e01` that Epic membership reached **51 surfaces** (every
# mod chest, every general's hoard, both polis vaults, the blood-cave mega chest and all
# 18 uber orb tables). So a craft-only supra was a straight Epic chest drop. That is the
# whole defect, and it is closed by removing FOUR memberships from ONE table.
#
# SCOPE, STATED: Will named The Last Word; all four thrown supras are the same kind of
# object (craft-only, itemClassification = Legendary, authored by the same wave), so all
# four leave the Epic table together. Leaving the other three would ship the exact bug he
# filed, three more times.
#
# THEY STAY ON THE LEGENDARY TABLE. "only legendary" is a relocation, not a retirement -
# R-186's own ask ("make the legendary thrown weapons droppable") is untouched at the tier
# Will kept it for, and `svc_unique_thrown_l01` below is unchanged.
#
# R-180 NON-REDUCTION IS SUPERSEDED HERE, NOT SMUGGLED. R-180 says no member is removed
# from a table; Will's newer ruling requires exactly that, and there is no additive way to
# make an item stop dropping. The removal is scoped to four memberships of one Epic table,
# and every SURVIVOR gains: the Epic thrown total goes 155 -> 115, so `u_vit_wand` rises
# 64.5% -> 87.0% of a thrown roll and each Common vit wand 3.2% -> 4.3%. Nothing needs
# compensating because nothing lost reach, and `THROWN_MASTER_WEIGHT` is untouched so how
# OFTEN thrown rolls at all does not move.
#
# ─── WHY LAW A IS *NOT* SOLVED BY PROMOTING `u_vit_wand` (the collateral, measured) ────
# The tempting one-move fix for LAW A ("every recipe needs a Legendary-only reagent") was
# to take `u_vit_wand` - the reagent all four thrown recipes share - off this same Epic
# table. It was built, measured, and it is WRONG, because it collides with LAW C:
#
#   the ENTIRE `WeaponHunting_RangedOneHand` universe at itemClassification = Legendary is
#   FIVE records: `u_vit_wand` + the four supra thrown. (Measured on 44499f56: thrown
#   splits Common 3 / Rare 3 / Epic 3 / Legendary 5, and the three "Epic" ones are
#   `records\item\formulaitems\*` craft RESULTS that no table pays.)
#
# `SLB.TARGET_IC['e']` is **Legendary** - in this mod an Epic-difficulty chest pays
# Legendary-classification gear - so rule C1 ("the thrown class is payable at its own
# tier") can only ever be satisfied by one of those five. LAW C removes four of them from
# Epic; promoting `u_vit_wand` would remove the fifth, leaving `svc_unique_thrown_e01`
# holding three COMMON wands and reddng C1 on **every Epic mod chest in the game**. There
# is no third option in the record universe and inventing a droppable Legendary thrown to
# feed the gate is a new item class, not a smallest-correct change. So `u_vit_wand` STAYS
# here at 100 as the Epic tier's C1 carrier, and LAW A is satisfied per-recipe instead -
# four formulas, one reagent slot each, in `tools/svc_supra_recipes.RECIPE_OVERRIDES`.
THROWN_MEMBERS = {
    # Normal: itemLevel-30 wands only. ZERO Legendary -> R-100 #17 holds by construction.
    'n': ((_WAND % 'mi_vit_wand_01', 100), (_WAND % 'm_vit_wand_01', 50)),
    # Epic: `u_vit_wand` (the C1 carrier) + the three Common vit wands. NO supra thrown -
    # LAW C. This table is the ONLY sub-Legendary surface in the database that ever paid
    # one, so these four omissions close all 51 Epic-side surfaces at once.
    'e': ((_WAND % 'u_vit_wand', 100),
          (_WAND % 'm_vit_wand_01', _COMMON_WAND_WEIGHT),
          (_WAND % 'm_vit_wand_02', _COMMON_WAND_WEIGHT),
          (_WAND % 'm_vit_wand_03', _COMMON_WAND_WEIGHT)),
    # Legendary: unchanged - this is where "only legendary" puts them.
    'l': ((_WAND % 'u_vit_wand', 100),
          (_SUPRA % 'svc_wep_charonstoll', _SUPRA_THROWN_WEIGHT),
          (_SUPRA % 'svc_wep_hati', _SUPRA_THROWN_WEIGHT),
          (_SUPRA % 'svc_wep_lastword', _SUPRA_THROWN_WEIGHT),
          (_SUPRA % 'svc_wep_sanguineorbit', _SUPRA_THROWN_WEIGHT),
          (_WAND % 'm_vit_wand_01', _COMMON_WAND_WEIGHT),
          (_WAND % 'm_vit_wand_02', _COMMON_WAND_WEIGHT),
          (_WAND % 'm_vit_wand_03', _COMMON_WAND_WEIGHT)),
}
# Weight of the thrown member inside `svc_unique_weapons_{tier}01`, PER TIER. DERIVED,
# not chosen. **RE-DERIVED AT THE b80 MERGE (2026-08-11), and the first derivation is kept
# below because the reason it stopped holding is the whole point.**
#
# ROUND 1 (against the pre-b80 master): every member carried 1000 for a 17-24 record
# class, so a full class weight bought ~20 records; thrown is 5 legendary records -> 5/20
# = 0.25 of a class weight = 250, measured at 250/6350 = 3.94% of a weapon roll.
#
# WHY THAT BROKE, MEASURED, NOT GUESSED. b80 (R-181) re-weighted the same master by a
# DIFFERENT law - `weight per MEMBER = _CLASS_WEIGHT x (number of classes that member
# pays)`, which lifted `unique_1h` from 1000 to 3000 and took the master total from 6100
# to 8100 - and separately lifted armour to parity, so weapons now carry only ~55% of a
# surface's gear mass instead of ~83%. Both moves shrink a fixed thrown weight's share
# twice over. Run on the b80 SHIP arz `c5851a1a` with this wave applied, 250 put thrown at
# 0.35%-1.36% of gear mass on 9 of the 42 surfaces - UNDER b80's own D3 starvation floor
# of 1.45%, which reds. The right response to "my class trips your floor" is to feed the
# class, not to lower the floor: the floor is what makes "droppable" mean something, and
# switching it off for the one class this ruling exists to add would be self-defeating.
#
# ROUND 2 (the binding derivation): **round 1's ratio was RIGHT, and the b80 merge is what
# proved it from data instead of from a guess at class size.** The measured universe of
# every gear class at its own target classification, off the built arz:
#
#   Legendary:  thrown 5 | bow 23 | mace 24 | SPEAR 24 | staff 25 | sword 28 | legs 33
#               shield 33 | arms 37 | helm 39 | axe 41 | torso 71
#   Epic:       thrown 3 | SPEAR 32 | bow 33 | mace 37 | staff 38 | sword 44 | ...
#
# Round 1 assumed "a full class weight buys ~20 records" and gave thrown 5/20 = a quarter.
# The real smallest ordinary class is 23, so the true ratio is 5/23 - a quarter, to within
# rounding. `_CLASS_WEIGHT // 4` therefore stands, now DERIVED from `SLB._CLASS_WEIGHT` so
# a future balance lane re-scales thrown with everything else instead of silently
# shrinking it (which is exactly what b80 did to the hard-coded 250).
#
# WHY NOT FULL PARITY, MEASURED. The obvious alternative was to give thrown a whole class
# weight under b80's parity law (1000, or 1350 once you notice the three base act masters
# pay the other six classes and structurally cannot pay thrown). Both were built and
# measured, and full parity is WRONG for a five-record class:
#   at 1350, a six-chest Gaoler cage run on Legendary pays 6.48 thrown, so **each of the
#   four craft-only supra thrown lands 1.30 times per run - 2.9x as often as a plain
#   legendary SPEAR (0.44)**.
# That is the exact shape of the report Will already filed against this same wave family
# ("you overcorrected, that run 4 scorpions tail spears dropped"), and it would gut the
# craft chain that R-184 and R-185 exist to repair: nobody crafts Charon's Toll if a cage
# run hands him one. At `_CLASS_WEIGHT // 4` a specific supra thrown is ~0.09 per cage
# run, roughly a fifth as often as a specific legendary spear - reachable, and still a
# prize, which is what R-186 committed to.
# MEASURED against b80's master (7 members, total 8100 at every tier):
#   e / l   250 / 8350 = 2.99% of a weapon-master roll
#   n       100 / 8200 = 1.22% of a weapon-master roll
# NORMAL STAYS AT 100 ON PURPOSE. Its table names only the itemLevel-30 wand band, which
# sits BELOW the tier's target classification, so a full class weight would spend ~11% of
# every Normal weapon roll on filler the player cannot use - and no gate would say so,
# because D3 exempts thrown on Normal by era (`SLD.D3_ERA_EXEMPT`). A weight nothing
# measures is exactly where a number should be conservative.
# The other six classes are not re-weighted at any tier by this lane.
THROWN_MASTER_WEIGHT = {'n': 100, 'e': _THROWN_CLASS_WEIGHT, 'l': _THROWN_CLASS_WEIGHT}

# ─────────────────────────────────────────────────────────────────────────────
# (2) REAGENT COMPLETABILITY
# ─────────────────────────────────────────────────────────────────────────────
# The three Ragnarok (xpack2) ghosts the four thrown formulas name. NOT in this database.
GHOST_REAGENTS = (
    r'records\xpack2\item\equipmentweapons\1hranged\u_l_08.dbr',
    r'records\xpack2\item\equipmentweapons\1hranged\u_e_06.dbr',
    r'records\xpack2\item\equipmentweapons\1hranged\mi_l_machae.dbr',
)
# The repoint. MEASURED house shape over the 59 uber formula records: 43 read
# "2 ordinary + 1 MI, all three of the RESULT's own item Class" (e.g. ar_melee_torso =
# a Legendary torso + an Epic torso + the green torso), 8 read "3 ordinary", 4 read
# "3 artifact". The Ragnarok original for these four was the same 2+1 shape in thrown
# form (u_l_08 Legendary + u_e_06 Epic + mi_l_machae green).
# This era's thrown roster is: u_vit_wand (Legendary, chest-droppable), m_vit_wand_01/02/03
# (Common, itemLevel 30/50/65), mi_vit_wand_01/02/03 (Rare/green, 30/50/65). There is NO
# droppable Epic-classification thrown, so the middle slot takes the Common wand - and
# each recipe therefore reads "the legendary thrown + a plain thrown + ONE green thrown",
# the house shape exactly. The three Common wands are added to the e/l thrown tables
# above so a legendary farmer finds them in chests (rule G1 proves it).
# WHY IT CHANGED from the first cut of this lane (which used 1 ordinary + 2 green): all
# three green vit wands come from ONE DRX monster family (the blood-cave reavers), so
# two-greens-per-recipe made every thrown craftable depend on that family twice. One
# green per recipe halves that, and the four (common, green) pairs are all distinct.
THROWN_FORMULA_REAGENTS = {
    r'records\drxitem\supra\zrecipes\svc_thrown_charonstoll_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'm_vit_wand_03', _WAND % 'mi_vit_wand_01'),
    r'records\drxitem\supra\zrecipes\svc_thrown_hati_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'm_vit_wand_01', _WAND % 'mi_vit_wand_02'),
    r'records\drxitem\supra\zrecipes\svc_thrown_lastword_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'm_vit_wand_02', _WAND % 'mi_vit_wand_03'),
    r'records\drxitem\supra\zrecipes\svc_thrown_sanguineorbit_formula.dbr':
        (_WAND % 'u_vit_wand', _WAND % 'm_vit_wand_03', _WAND % 'mi_vit_wand_02'),
}

# The mod-owned reagent tables, one per FAMILY, LEGENDARY TIER ONLY (every reagent placed
# here is itemClassification = Legendary - except the orphaned green, which is Rare, a
# strictly LOWER rung - so none of them can ever enter a Normal or Epic host).
REAGENT_TABLE = {
    'torso': r'records\item\loottables\svc\svc_craft_reagents_torso_l01.dbr',
    'amulet': r'records\item\loottables\svc\svc_craft_reagents_amulet_l01.dbr',
    'ring': r'records\item\loottables\svc\svc_craft_reagents_ring_l01.dbr',
    'artifact': r'records\item\loottables\svc\svc_craft_reagents_artifact_l01.dbr',
    'orphanmi': r'records\item\loottables\svc\svc_craft_reagents_orphanmi_l01.dbr',
}
# The LEGENDARY-tier host(s) each family hangs off, as ((host, weight), ...). Every host
# is a LootMasterTable that the legendary chest pools already reach, so no chest row is
# touched - which is what keeps this lane off the chest/hoard surface entirely.
#
# SPREAD IS MEASURED, NOT ASSUMED (the defect the first cut of this lane shipped). Over
# the 19 legendary mod chest tables:
#     unique_torso_l01  19/19      amulet_l01  19/19      finger_l01   19/19
#     unique_1h_l01     19/19      04_l_misc    1/19  <-- svc_uberorb_apex_l01c ONLY
# `04_l_misc` is reached by exactly one surface, and that surface is the apex uber-boss
# orb, so the artifact family ALSO hangs off amulet_l01 + finger_l01 (a divine artifact
# is a trinket; the jewellery branch is its closest kin). Rule G4 re-measures this every
# build and fails if any non-MI reagent drops under half the legendary surfaces.
#
# Weights are each ~5% of the host's own measured total (torso 100, amulet 1000, finger
# 1000, 04_l_misc 1357, unique_1h_l01 300), so a reagent is a rare tail on an existing
# branch rather than a re-weighting of it. Nothing existing is lowered.
REAGENT_HOSTS = {
    'torso': ((r'records\xpack\item\loottables\torso\mastertables\unique_torso_l01.dbr', 5),),
    'amulet': ((r'records\xpack\item\loottables\amulet\unique\amulet_l01.dbr', 50),),
    'ring': ((r'records\xpack\item\loottables\finger\unique\finger_l01.dbr', 50),),
    'artifact': ((r'records\item\loottables\raremisc\mastertables\04_l_misc.dbr', 60),
                 (r'records\xpack\item\loottables\amulet\unique\amulet_l01.dbr', 50),
                 (r'records\xpack\item\loottables\finger\unique\finger_l01.dbr', 50)),
    # The orphaned green is a WeaponMelee_Mace, so it goes on the legendary one-hand
    # master - its own class, and the table every mod chest reaches through the breadth
    # master's first member.
    'orphanmi': ((r'records\xpack\item\loottables\weapons\mastertables\unique_1h_l01.dbr', 5),),
}

# The reagents that no chest could pay, by family. COMMITTED (not derived at apply
# time) so the placement is deterministic and reviewable; `audit_db` then re-proves
# completability over the FINAL database, so a future content change that strands a
# different reagent fails loud instead of silently shipping.
REAGENT_PLACEMENTS = {
    'torso': (
        r'records\item\equipmentarmor\um_l_mantleofamunra.dbr',
        r'records\item\equipmentarmor\um_e_raimentoflogos.dbr',
        r'records\item\equipmentarmor\u_l_wyrmskinharness.dbr',
    ),
    'amulet': (
        r'records\item\equipmentamulet\u_e_blessingofthegods.dbr',
        r'records\sandbox\chris\chrisamulet01.dbr',
        r'records\sandbox\chris\chrisrelic2.dbr',
    ),
    'ring': (
        r"records\item\equipmentring\u_e_thoth'smark.dbr",
        r'records\item\equipmentring\u_l_blackpearlring.dbr',
    ),
    'artifact': (
        r'records\xpack\item\artifacts\l_da_thothsglory.dbr',
        r'records\xpack\item\artifacts\l_da_ikonofzeus.dbr',
        r'records\xpack\item\artifacts\l_da_mardukstabletofdestiny.dbr',
        r'records\xpack\item\artifacts\l_da_goldeneyeofsunwukong.dbr',
        r'records\xpack\item\artifacts\e_da_crescentmoonofartemis.dbr',
        r'records\xpack\item\artifacts\e_da_demetersbounty.dbr',
    ),
    # THE ORPHANED GREEN. `mi_l_gigantes2` gates Doomherald, Swordfish and Omega, and no
    # LIVE monster drops it: the only carrier is the dev duplicate `copy of anapaest_45`
    # (the live `anapaest_45` names placeholder `equip\bogus\*` ITEM records in the same
    # slots, and `03_master_legendary`, which would have re-hung the gigantes tables, has
    # zero holders). Will's exemption is for greens that a monster drops; this one has no
    # monster, so it is chest-placed like an ordinary reagent. Rule G3 enforces the
    # general form of that: an MI reagent that is neither live-monster-farmable nor
    # chest-reachable FAILS the build.
    'orphanmi': (
        r'records\drxcreatures\drxdishonorguard\equip\weapons\mi_l_gigantes2.dbr',
    ),
}
REAGENT_ITEM_WEIGHT = 100

# G4, THE SPREAD RULE. Will: "if players farm legendary long enough, they should be able
# to find all the reagents without having to farm a specific area or a SPECIFIC
# CHARACTER". Reachability from the UNION of the legendary chest pools cannot see the
# difference between 19 surfaces and 1, so the rule is expressed in surfaces: a non-MI
# reagent must be payable by at least half of the legendary mod chest tables (a fraction,
# so it self-scales when a lane adds or retires chests), and never fewer than 3 whether
# or not the fraction says so. MEASURED after this wave: 60/60 non-MI reagents (54 ordinary + 6 artifact) at 19/19.
SPREAD_MIN_FRACTION = 0.5
SPREAD_MIN_SURFACES = 3

# MI / "green" reagents: Will's own exemption ("except for the monster unique droppable
# items like the green items"). The RULE is `itemClassification == 'Rare'`; this list is
# the committed roster that rule produced on the live arz, and `audit_db` fails loud if
# the derived set ever diverges from it, so neither can rot silently.
MI_CLASSIFICATION = 'Rare'
MI_REAGENTS = (
    'mi_l_arachnos', 'mi_l_bandari', 'mi_l_dragonian', 'mi_l_empousa', 'mi_l_gigantes2',
    'mi_l_ichthianmelee', 'mi_l_lamiamelee', 'mi_l_liche', 'mi_l_minotaur',
    'mi_l_neanderthalmage', 'mi_l_satyrbrigand', 'mi_l_satyrmage', 'mi_l_tigermanchampion',
    'mi_l_tigermanmage', 'mi_l_tigermanmelee', 'mi_l_troglodytemelee',
    'mi_l_tropicalarachnos', 'mi_l_wraith',
    # The three DRX green wands this lane's thrown-formula repoint introduces. They are
    # MI records by the same rule as every entry above (itemClassification = Rare) and are
    # covered by the same Will exemption; `audit_db` proves each one monster-farmable.
    'mi_vit_wand_01', 'mi_vit_wand_02', 'mi_vit_wand_03',
)
# The MI reagents whose exemption is NOT earned by a live monster, and which are therefore
# chest-placed instead (see REAGENT_PLACEMENTS['orphanmi']). COMMITTED so it cannot rot:
# G3 fails if the set the database derives differs from this one in either direction, so
# a future lane that wires a real carrier - or one that kills another green's last live
# carrier - has to come back here.
MI_NO_LIVE_CARRIER = ('mi_l_gigantes2',)


# ─────────────────────────────────────────────────────────────────────────────
# shared derivations (the craft chain, read straight off the records)
# ─────────────────────────────────────────────────────────────────────────────
def _is_supra_result(path):
    p = _n(path)
    return '\\supra\\' in p and p.endswith('.dbr') and '\\recipes\\' not in p \
        and '\\zrecipes\\' not in p


def uber_formulas(db, lk):
    """{formula record: result record} for every formula that builds a supra craftable."""
    out = {}
    for name in db.record_names():
        cls = str(_sc(db.get_field_value(name, 'Class')) or '')
        if 'formula' not in cls.lower():
            continue
        art = _sc(db.get_field_value(name, 'artifactName'))
        if isinstance(art, str) and _is_supra_result(art):
            out[name] = art
    return out


def reagents_of(db, formula):
    """The reagent paths a formula names, in slot order."""
    out = []
    ff = db.get_fields(formula) or {}
    for k in sorted(ff, key=lambda z: z.split('###')[0]):
        b = k.split('###')[0]
        if b.startswith('reagent') and b.endswith('BaseName'):
            for v in ff[k].values:
                if isinstance(v, str) and v:
                    out.append(v)
    return out


def reagent_universe(db, lk, forms=None):
    """{reagent path (lowercased): set(craftable)} over every uber formula."""
    forms = forms if forms is not None else uber_formulas(db, lk)
    users = defaultdict(set)
    for f, result in forms.items():
        for r in reagents_of(db, f):
            users[_n(r)].add(_n(result))
    return users


def classify_reagent(db, lk, path):
    """'missing' | 'mi' | 'artifact' | 'ordinary'."""
    real = lk.real(path)
    if not real:
        return 'missing'
    ic = str(_sc(db.get_field_value(real, 'itemClassification')) or '')
    cls = str(_sc(db.get_field_value(real, 'Class')) or '')
    if ic == MI_CLASSIFICATION:
        return 'mi'
    if cls.startswith('ItemArtifact'):
        return 'artifact'
    return 'ordinary'


def chest_leaf_sets(db, lk, ex, tier):
    """{mod chest table of `tier`: frozenset(leaf items it can pay)} - the per-SURFACE
    view. Cached on the expander because both the pool and the spread rule want it and a
    whole-build audit expands 51 chest tables."""
    cache = getattr(ex, '_svc_chest_leaf_sets', None)
    if cache is None:
        cache = {}
        try:
            ex._svc_chest_leaf_sets = cache
        except AttributeError:
            pass
    hit = cache.get(tier)
    if hit is not None:
        return hit
    exempt = {_n(k) for k in SLB.EXEMPT}
    out = {}
    for table in SLB.chest_tables(db, lk):
        if _n(table) in exempt:
            continue
        if SLB.infer_tier(db, table, lk) == tier:
            out[table] = frozenset(_n(x) for x in ex.leaves(table))
    cache[tier] = out
    return out


def chest_pool(db, lk, ex, tier):
    """The set of leaf items every mod chest of `tier` can pay (lowercased)."""
    out = set()
    for leaves in chest_leaf_sets(db, lk, ex, tier).values():
        out |= leaves
    return out


def spread_floor(n_surfaces):
    """How many distinct legendary chest surfaces a non-MI reagent must be payable by."""
    if n_surfaces <= SPREAD_MIN_SURFACES:
        return n_surfaces               # tiny worlds: every surface must carry it
    want = int(SPREAD_MIN_FRACTION * n_surfaces)
    if SPREAD_MIN_FRACTION * n_surfaces > want:
        want += 1                       # ceil, without importing math for one call
    return max(SPREAD_MIN_SURFACES, want)


# Record-name shapes the upstream authors used for dev duplicates / disabled copies.
# A carrier whose name matches one is not evidence that anything in the world drops it.
_DEV_DEAD_MARKERS = ('copy of ', 'copy (', 'xxx', 'backup', 'conflicted copy', '_old')


def _looks_dev_dead(record):
    base = _n(record).rsplit('\\', 1)[-1]
    return any(m in base for m in _DEV_DEAD_MARKERS)


def reverse_index(db):
    r"""{referenced .dbr (lowercased): {records that name it}} over the WHOLE db, built
    once and cached on the db object (the walk below runs for ~22 MI reagents and a
    per-reagent full scan would be 22 whole-database passes)."""
    cached = getattr(db, '_svc_craft_rev', None)
    if cached is not None:
        return cached
    rev = defaultdict(set)
    for rec in db.record_names():
        for k, tf in (db.get_fields(rec) or {}).items():
            b = k.split('###')[0].lower()
            if 'weight' in b or 'chance' in b or 'equation' in b:
                continue
            for v in tf.values:
                if isinstance(v, str) and v.lower().endswith('.dbr'):
                    rev[_n(v)].add(rec)
    try:
        db._svc_craft_rev = rev
    except AttributeError:
        pass
    return rev


def monster_sources(db, lk, reagent, max_depth=6, exclude=None):
    """(monsters, tables) that can pay `reagent`, found by walking the reference graph
    UPWARD from the item through loot tables until a non-table holder is reached. This is
    the EVIDENCE behind Will's MI exemption ("except for the monster unique droppable
    items like the green items"): an exemption is only honest if something in the game
    actually drops the thing.

    `exclude` is a set of loot-table paths the walk refuses to traverse. It exists for one
    reason and it is load-bearing: once a green is CHEST-placed through a mod reagent
    table, the walk would climb that table into every monster that shares the host, and
    the reagent would look monster-farmed BECAUSE we placed it. Passing the mod's own
    reagent tables keeps the "does a live monster drop it" question answerable after the
    fix, so rule G3's committed roster stays measurable instead of self-erasing."""
    rev = reverse_index(db)
    skip = {_n(x) for x in (exclude or ())}
    seen = set()
    frontier = [_n(reagent)]
    monsters, tables = set(), set()
    depth = 0
    while frontier and depth <= max_depth:
        nxt = []
        for cur in frontier:
            for holder in rev.get(cur, ()):
                hl = _n(holder)
                if hl in seen or hl in skip:
                    continue
                seen.add(hl)
                cls = str(_sc(db.get_field_value(holder, 'Class')) or '')
                if cls.startswith('Monster'):
                    monsters.add(holder)
                    continue
                if SLB.is_loot_table(lk, holder):
                    tables.add(holder)
                    nxt.append(hl)
        frontier = nxt
        depth += 1
    return sorted(monsters), sorted(tables)


def mi_monster_sources(db, lk, reagent):
    """`monster_sources` with the mod's own reagent tables cut out of the graph - the
    form every MI-exemption question must use."""
    return monster_sources(db, lk, reagent, exclude=REAGENT_TABLE.values())


# ─────────────────────────────────────────────────────────────────────────────
# WRITE SIDE
# ─────────────────────────────────────────────────────────────────────────────
def _members(db, real):
    """[(index, name, weight)] for the occupied lootNameN members of a table."""
    out = []
    for k in (db.get_fields(real) or {}):
        b = k.split('###')[0]
        if not b.startswith('lootName'):
            continue
        try:
            i = int(b[len('lootName'):])
        except ValueError:
            continue
        v = _sc(db.get_field_value(real, b))
        if v:
            w = _sc(db.get_field_value(real, 'lootWeight%d' % i)) or 0
            out.append((i, str(v), int(w)))
    return sorted(out)


def _first_free(db, real, limit=64):
    used = {i for i, _nm, _w in _members(db, real)}
    for i in range(1, limit):
        if i not in used:
            return i
    return None


def add_member(db, real, path, weight, lk=None):
    """Add ONE member to a loot table, idempotently. Never touches an existing member,
    never lowers a weight. Returns a change string or None."""
    lk = lk or Lookup(db)
    target = lk.real(path) or path
    for _i, nm, _w in _members(db, real):
        if _n(nm) == _n(target):
            return None                      # already a member: leave it exactly as-is
    idx = _first_free(db, real)
    if idx is None:
        raise SystemExit("svc_craft_thrown: %s has no free lootName slot for %s"
                         % (real, target))
    SLB._set_str(db, real, 'lootName%d' % idx, target)
    db.set_field(real, 'lootWeight%d' % idx, int(weight))
    return 'lootName%d=%s (w=%d)' % (idx, _n(target).rsplit('\\', 1)[-1], weight)


def wire_mythic_formulas_into_normal(db, lk=None, verbose=True):
    """(1) BOTH supra pools become members of every Normal-tier act formula table."""
    lk = lk or Lookup(db)
    changes = []
    for table in NORMAL_FORMULA_TABLES:
        real = lk.real(table)
        if not real:
            print("  CRAFT/THROWN: WARNING Normal formula table missing: %s" % table)
            continue
        # The baseline total is read ONCE, before either pool is added, so the two shares
        # are both measured against the table as it shipped (never compounding).
        base_total = sum(w for _i, _nm, w in _members(db, real))
        for pool, share in NORMAL_FORMULA_POOLS:
            target = lk.real(pool)
            if not target:
                print("  CRAFT/THROWN: WARNING supra pool missing (%s); not wired into "
                      "Normal" % pool)
                continue
            # weight w such that w / (base_total + w) == share
            weight = max(1, int(round(base_total * share / (1.0 - share))))
            c = add_member(db, real, target, weight, lk)   # idempotent
            if c:
                changes.append('%s: %s [%.2f%% of %d]'
                               % (_n(real).rsplit('\\', 1)[-1], c,
                                  100.0 * weight / float(base_total + weight),
                                  base_total + weight))
    if verbose:
        for c in changes:
            print("  CRAFT/THROWN: mythic formulas on Normal - %s" % c)
    return changes


def ensure_thrown_tables(db, lk=None, verbose=True):
    """(3) Author `svc_unique_thrown_{n,e,l}01`. Idempotent: a table that already carries
    exactly the right members is not rewritten."""
    lk = lk or Lookup(db)
    donor = lk.real(_THROWN_DONOR)
    if not donor:
        print("  CRAFT/THROWN: WARNING thrown donor missing (%s); thrown tables not "
              "authored" % _THROWN_DONOR)
        return {}
    built = {}
    for tier in TIERS:
        path = THROWN_TABLE[tier]
        members = [(lk.real(p), w) for (p, w) in THROWN_MEMBERS[tier] if lk.real(p)]
        if not members:
            print("  CRAFT/THROWN: WARNING no thrown records resolve for tier %r; table "
                  "skipped" % tier)
            continue
        want = [(_n(p), w) for p, w in members]
        real = lk.real(path)
        if real:
            have = [(_n(nm), w) for _i, nm, w in _members(db, real)]
            if have == want:
                built[tier] = real
                continue
            path = real
        else:
            db.clone_record(donor, path)
        db.set_field(path, 'FileDescription',
                     'SVC thrown class: every unique one-hand-ranged weapon, %s tier'
                     % tier)
        for i, (p, w) in enumerate(members, start=1):
            SLB._set_str(db, path, 'lootName%d' % i, p)
            db.set_field(path, 'lootWeight%d' % i, int(w))
        for i in range(len(members) + 1, _THROWN_CLEAR_SLOTS):
            if _sc(db.get_field_value(path, 'lootName%d' % i)):
                db.set_field(path, 'lootName%d' % i, '')
            if _sc(db.get_field_value(path, 'lootWeight%d' % i)) not in (None, 0):
                db.set_field(path, 'lootWeight%d' % i, 0)
        built[tier] = path
        if verbose:
            print("  CRAFT/THROWN: %s = %d thrown record(s)"
                  % (_n(path).rsplit('\\', 1)[-1], len(members)))
    lk.refresh()
    return built


def ensure_reagent_tables(db, lk=None, verbose=True):
    """(2a) Author the per-family reagent tables and hang each off its LEGENDARY host."""
    lk = lk or Lookup(db)
    donor = lk.real(_THROWN_DONOR)
    if not donor:
        print("  CRAFT/THROWN: WARNING reagent donor missing; reagent tables not authored")
        return {}
    built = {}
    for family, path in sorted(REAGENT_TABLE.items()):
        items = [lk.real(p) for p in REAGENT_PLACEMENTS[family]]
        missing = [p for p, r in zip(REAGENT_PLACEMENTS[family], items) if not r]
        if missing:
            # Fail loud: a committed reagent that no longer resolves is a real defect,
            # never something to place silently or skip.
            raise SystemExit("svc_craft_thrown: committed reagent(s) do not resolve in "
                             "the db: %s" % ', '.join(missing))
        want = [(_n(p), REAGENT_ITEM_WEIGHT) for p in items]
        real = lk.real(path)
        if real:
            have = [(_n(nm), w) for _i, nm, w in _members(db, real)]
            if have != want:
                path = real
            else:
                built[family] = real
                continue
        else:
            db.clone_record(donor, path)
        db.set_field(path, 'FileDescription',
                     'SVC uber-craft reagents (%s), legendary tier' % family)
        for i, p in enumerate(items, start=1):
            SLB._set_str(db, path, 'lootName%d' % i, p)
            db.set_field(path, 'lootWeight%d' % i, int(REAGENT_ITEM_WEIGHT))
        for i in range(len(items) + 1, _THROWN_CLEAR_SLOTS):
            if _sc(db.get_field_value(path, 'lootName%d' % i)):
                db.set_field(path, 'lootName%d' % i, '')
            if _sc(db.get_field_value(path, 'lootWeight%d' % i)) not in (None, 0):
                db.set_field(path, 'lootWeight%d' % i, 0)
        built[family] = path
        if verbose:
            print("  CRAFT/THROWN: %s = %d reagent(s)"
                  % (_n(path).rsplit('\\', 1)[-1], len(items)))
    lk.refresh()
    return built


def wire_reagent_hosts(db, lk=None, verbose=True):
    """(2b) Add each reagent table to EVERY legendary host it is contracted to hang off
    (additive, idempotent). A family may name more than one host on purpose: reachability
    from the union of the chest pools is not the same thing as reachability from enough
    distinct chest SURFACES (rule G4)."""
    lk = lk or Lookup(db)
    changes = []
    for family, hosts in sorted(REAGENT_HOSTS.items()):
        table = lk.real(REAGENT_TABLE[family])
        if not table:
            print("  CRAFT/THROWN: WARNING reagent table missing for %r" % family)
            continue
        for host, weight in hosts:
            host_real = lk.real(host)
            if not host_real:
                print("  CRAFT/THROWN: WARNING reagent host missing for %r: %s"
                      % (family, host))
                continue
            c = add_member(db, host_real, table, weight, lk)
            if c:
                changes.append('%s <- %s' % (_n(host_real).rsplit('\\', 1)[-1], c))
    if verbose:
        for c in changes:
            print("  CRAFT/THROWN: reagent host - %s" % c)
    return changes


def repoint_thrown_formula_reagents(db, lk=None, verbose=True):
    """(2c) Move the 4 thrown formulas off the three Ragnarok ghost records."""
    lk = lk or Lookup(db)
    changes = []
    for formula, reagents in sorted(THROWN_FORMULA_REAGENTS.items()):
        real = lk.real(formula)
        if not real:
            print("  CRAFT/THROWN: WARNING thrown formula missing: %s" % formula)
            continue
        resolved = [lk.real(p) for p in reagents]
        if any(r is None for r in resolved):
            raise SystemExit("svc_craft_thrown: thrown-formula replacement reagent(s) do "
                             "not resolve: %s" % formula)
        touched = []
        for i, target in enumerate(resolved, start=1):
            field = 'reagent%dBaseName' % i
            cur = _sc(db.get_field_value(real, field))
            if cur is not None and _n(cur) == _n(target):
                continue
            SLB._set_str(db, real, field, target)
            touched.append('%s=%s' % (field, _n(target).rsplit('\\', 1)[-1]))
        if touched:
            changes.append('%s: %s' % (_n(real).rsplit('\\', 1)[-1], ', '.join(touched)))
    if verbose:
        for c in changes:
            print("  CRAFT/THROWN: thrown formula repoint - %s" % c)
    return changes


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT SIDE (shared by the standalone gate, the in-build verify and the negtests)
# ─────────────────────────────────────────────────────────────────────────────
def thrown_problems(db, table, tier, ex, lk=None):
    """(d) THE THROWN-CLASS RULE, folded into the class-breadth gate family.

    Every mod chest must be able to pay the one-hand-ranged class at its own tier:
      C1 tiers e/l - at least one thrown record of the tier's TARGET classification
         (Legendary), i.e. the class is genuinely payable at end game;
      C2 tier n    - at least one thrown record of ANY classification (measured: this
         TQIT-era db has no droppable Epic-classification thrown record at all - the only
         three are base-game craft RESULTS - so Normal's thrown presence is carried by the
         itemLevel-30 Rare/Common wand band), and ZERO Legendary thrown (the tier law).
    """
    lk = lk or (ex.lk if hasattr(ex, 'lk') else Lookup(db))
    base = _n(table).rsplit('\\', 1)[-1]
    problems = []
    reachable = []
    for it in ex.leaves(table):
        if str(_sc(db.get_field_value(it, 'Class')) or '') == THROWN_CLASS:
            reachable.append(it)
    if tier == 'n':
        if not reachable:
            problems.append(
                "C2 %s [n tier] reaches NO %s item; the thrown class is unpayable on "
                "Normal" % (base, THROWN_CLASS))
        leaked = [x for x in reachable
                  if str(_sc(db.get_field_value(x, 'itemClassification')) or '')
                  == 'Legendary']
        if leaked:
            problems.append(
                "C2 %s [n tier] reaches %d LEGENDARY thrown item(s) (tier law: no "
                "legendary gear on Normal); e.g. %s"
                % (base, len(leaked), sorted(leaked)[0]))
    else:
        want = SLB.TARGET_IC[tier]
        good = [x for x in reachable
                if str(_sc(db.get_field_value(x, 'itemClassification')) or '') == want]
        if not good:
            problems.append(
                "C1 %s [%s tier] reaches no %s %s item (the thrown class is unpayable at "
                "its own tier)" % (base, tier, want, THROWN_CLASS))
    return problems


def audit_formula_reachability(db, lk, ex):
    """(a) Every uber craftable must have at least one chest-droppable formula on EVERY
    difficulty tier - Normal included (Will: "they can drop in normal as well")."""
    problems = []
    forms = uber_formulas(db, lk)
    craftables = {_n(v) for v in forms.values()}
    stats = {}
    for tier in TIERS:
        pool = chest_pool(db, lk, ex, tier)
        covered = {_n(result) for f, result in forms.items() if _n(f) in pool}
        stats[tier] = (len(covered), len(craftables),
                       len([f for f in forms if _n(f) in pool]), len(forms))
        missing = sorted(craftables - covered)
        if missing:
            problems.append(
                "F1 [%s tier] %d of %d uber craftables have NO chest-droppable formula "
                "(e.g. %s)" % (tier, len(missing), len(craftables), missing[0]))
    return problems, stats


def audit_reagent_completability(db, lk, ex, prove_mi=True):
    """(c) Every NON-MI reagent of every uber craftable must be reachable from the
    LEGENDARY-tier chest pools (G1) and from ENOUGH DISTINCT legendary chest surfaces
    (G4), and every MI exemption must be earned by a LIVE monster or replaced by a chest
    placement (G3)."""
    problems = []
    forms = uber_formulas(db, lk)
    users = reagent_universe(db, lk, forms)
    pool_l = chest_pool(db, lk, ex, 'l')
    buckets = defaultdict(list)
    for reagent in sorted(users):
        buckets[classify_reagent(db, lk, reagent)].append(reagent)

    if buckets['missing']:
        problems.append(
            "G0 %d reagent(s) name a record the MOD database does not carry (a base-game "
            "or DLC record is not an answer: R-210 caps the playable arc at Immortal "
            "Throne, so DLC-only content is unreachable for a player of this mod): %s"
            % (len(buckets['missing']),
               ', '.join(_n(x).rsplit('\\', 1)[-1] for x in buckets['missing'])))

    unreachable = [r for r in buckets['ordinary'] + buckets['artifact']
                   if r not in pool_l]
    if unreachable:
        problems.append(
            "G1 %d non-MI reagent(s) are unreachable from every Legendary-tier chest "
            "pool (Will: farm legendary long enough -> find all the reagents): %s"
            % (len(unreachable),
               ', '.join(_n(x).rsplit('\\', 1)[-1] for x in sorted(unreachable))))

    derived_mi = {_n(x).rsplit('\\', 1)[-1][:-4] for x in buckets['mi']}
    committed = set(MI_REAGENTS)
    if derived_mi != committed:
        problems.append(
            "G2 the MI exemption roster drifted: derived-not-committed=%s "
            "committed-not-derived=%s (the list in svc_craft_thrown.MI_REAGENTS must be "
            "updated in the same commit as whatever moved)"
            % (sorted(derived_mi - committed) or 'none',
               sorted(committed - derived_mi) or 'none'))

    # G4 - THE SPREAD RULE. Reachability from the UNION of the legendary chest pools
    # cannot tell 19 surfaces from 1, and 1 surface IS "farm a specific character" when
    # that surface is a boss orb. Only reagents that already pass G1 are graded, so a
    # missing reagent is reported once, not twice.
    surfaces = chest_leaf_sets(db, lk, ex, 'l')
    floor = spread_floor(len(surfaces))
    spread = {}
    thin_spread = []
    for reagent in buckets['ordinary'] + buckets['artifact']:
        hits = sum(1 for leaves in surfaces.values() if reagent in leaves)
        spread[reagent] = hits
        if 0 < hits < floor:
            thin_spread.append((reagent, hits))
    if thin_spread:
        problems.append(
            "G4 %d non-MI reagent(s) are payable by too few distinct Legendary chest "
            "surfaces (need >= %d of %d; Will: no farming a specific area or character): "
            "%s" % (len(thin_spread), floor, len(surfaces),
                    ', '.join('%s %d/%d' % (_n(r).rsplit('\\', 1)[-1], h, len(surfaces))
                              for r, h in sorted(thin_spread))))

    mi_srcs = {}
    if prove_mi:
        # G3 - the exemption must be EARNED, and it is earned by a LIVE monster. Will
        # exempts the greens because "the monster unique droppable items" are farmed off
        # monsters; a green whose only carrier is a dev duplicate is not farmed off
        # anything, so the exemption does not apply to it and it must be chest-placed
        # like an ordinary reagent. FAIL, not WARN - the old warning let three
        # uncompletable craftables ship while the docs called them completable.
        no_live = []
        for reagent in buckets['mi']:
            monsters, tables = mi_monster_sources(db, lk, reagent)
            mi_srcs[reagent] = (monsters, tables)
            if [m for m in monsters if not _looks_dev_dead(m)]:
                continue
            no_live.append(reagent)
            if reagent not in pool_l:
                problems.append(
                    "G3 MI/green reagent %s is exempt as 'monster-farmed' but NO LIVE "
                    "monster can pay it (%s) and no Legendary chest pool reaches it "
                    "either, so the %d craftable(s) it gates are uncompletable"
                    % (_n(reagent).rsplit('\\', 1)[-1],
                       ', '.join(_n(m).rsplit('\\', 1)[-1] for m in monsters[:3])
                       or 'no carrier at all', len(users[reagent])))
        derived_no_live = {_n(x).rsplit('\\', 1)[-1][:-4] for x in no_live}
        if derived_no_live != set(MI_NO_LIVE_CARRIER):
            problems.append(
                "G3 the no-live-carrier MI roster drifted: derived-not-committed=%s "
                "committed-not-derived=%s (svc_craft_thrown.MI_NO_LIVE_CARRIER and the "
                "'orphanmi' placement must move in the same commit as whatever changed)"
                % (sorted(derived_no_live - set(MI_NO_LIVE_CARRIER)) or 'none',
                   sorted(set(MI_NO_LIVE_CARRIER) - derived_no_live) or 'none'))

    stats = {'total': len(users), 'mi': len(buckets['mi']),
             'ordinary': len(buckets['ordinary']), 'artifact': len(buckets['artifact']),
             'missing': len(buckets['missing']),
             'reachable_l': len([r for r in users if r in pool_l]),
             'surfaces': len(surfaces), 'spread_floor': floor,
             'spread_min': min(spread.values()) if spread else 0,
             'spread': spread,
             'buckets': {k: sorted(v) for k, v in buckets.items()},
             'mi_sources': mi_srcs}
    return problems, stats


def audit_db(db, verbose=False, lk=None):
    """The whole craft+thrown contract over one (final) database."""
    lk = lk or Lookup(db)
    ex = Expander(db, lk)
    problems = []
    fprob, fstats = audit_formula_reachability(db, lk, ex)
    problems.extend(fprob)
    rprob, rstats = audit_reagent_completability(db, lk, ex)
    problems.extend(rprob)

    # thrown presence, per mod chest table (the class-breadth family)
    exempt = {_n(k) for k in SLB.EXEMPT}
    tprob = []
    audited = 0
    for table in SLB.chest_tables(db, lk):
        if _n(table) in exempt:
            continue
        tier = SLB.infer_tier(db, table, lk)
        if tier is None:
            continue
        audited += 1
        tprob.extend(thrown_problems(db, table, tier, ex, lk))
    if not audited:
        problems.append("C0 no mod chest table was audited for the thrown class at all "
                        "(scope rule broken - it must never be empty)")
    problems.extend(tprob)

    if verbose:
        for tier in TIERS:
            c, tot, fr, ftot = fstats[tier]
            print("    formulas [%s] %d/%d craftables covered, %d/%d formula records "
                  "reachable" % (tier, c, tot, fr, ftot))
        print("    reagents: %d total = %d MI + %d ordinary + %d artifact + %d missing; "
              "%d reachable from Legendary chests; thinnest non-MI spread %d of %d "
              "legendary chest surfaces (floor %d)"
              % (rstats['total'], rstats['mi'], rstats['ordinary'], rstats['artifact'],
                 rstats['missing'], rstats['reachable_l'], rstats['spread_min'],
                 rstats['surfaces'], rstats['spread_floor']))
        print("    thrown: %d mod chest table(s) audited" % audited)
    return problems, {'formulas': fstats, 'reagents': rstats, 'chests': audited}
