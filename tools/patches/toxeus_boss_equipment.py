r"""toxeus_boss_equipment - R-252 (Will 2026-08-14): the Endless Hunt wears armour, the
Devourer of Blood stops wielding a bow, and every hand slot on the fought Toxeus champions
holds an item class that slot can actually wear.

WILL, VERBATIM (three reports, one boss family, one system):
  BL-W0814-3  "toxeus the murderer the endless hunt is not wearing any equipment and i
               dont think he has a weapon"
  BL-W0814-9  "toxeus the murderer devourer of blood is using a bow which makes no sense"
  BL-W0814-10 "i killed toxeus the murderer devourer of blood and he did not drop his soul
               even though he should have 100% chance of dropping his soul"

WHAT THE BYTES SAID (measured against the SHIPPED build91/92 arz b888f022, read-only)
-------------------------------------------------------------------------------------
THE SLOT LAW, proven by a full base-game census. COUNTING RULE, stated so the numbers can
be re-derived: over all 5,556 records in the base-game `database.arz` whose `templateName`
BASENAME is exactly `Monster.tpl`, a record is counted ONCE per class its hand can yield -
every armed row of that hand (chanceToEquip<Hand> > 0, row weight > 0) is expanded through
the loot chain to leaf `templateName` stems, the per-record class sets are unioned, and each
class gets one tick. Item template stems are spelled inconsistently in the game data, so
BOTH spellings are listed and the module folds case everywhere.
ROUND-4 CORRECTION TO THE DENOMINATOR, recorded rather than quietly overwritten: rounds 1-3
published this denominator as "6,085 Monster.tpl records". 6,085 is what you get from
`templateName.lower().endswith('monster.tpl')`, which additionally sweeps in 411
`ControllerMonster.tpl` + 53 `FixedItemSkill_SpawnMonster.tpl` + 34
`Skill_SpawnPetMonster.tpl` + 31 `ControllerStationaryMonster.tpl` = 529 controllers and
skill records that are not monsters and carry no `chanceToEquip*` fields at all
(5556 + 529 = 6085). Measured on `database.arz`: 74,013 records total, 5,556 by basename,
5,561 by `Class == 'Monster'`. Every per-class tally below re-derives EXACTLY as published -
the 529 extras contributed nothing to any of them - so only the stated denominator was
wrong. It is corrected here because round 3 of this lane exists to retract a census
published under an explicitly "stated so this is re-derivable" rule, and publishing an
unreproducible denominator inside that correction is the same defect class.

    class stem (as spelled)   RightHand   LeftHand
    Weapon_Spear                  493          0    <- the Hunt's Runbreaker is CORRECT
    Weapon_Sword                 1164        244
    Weapon_Axe / weapon_axe      1074 / 132  221 / 36
    Weapon_Mace / weapon_mace    1069 / 105  172 / 33
    weapon_rangedonehand          127         12
    Weapon_Bow                     17        514    <- LeftHand IS the bow slot
    Weapon_Staff                   17        710
    WeaponArmor_Shield              0        805    <- LeftHand IS the shield slot

So in this engine LeftHand is the shield / two-handed-ranged slot and RightHand is the
one-handed melee slot. That table explains two of the three reports.

TWO ZEROS ARE ABSOLUTE and one pair is merely overwhelming, stated precisely because a
round-2 draft of this docstring claimed all four were zero and was WRONG:
  * WeaponArmor_Shield NEVER rides RightHand (0) and Weapon_Spear NEVER rides LeftHand (0).
  * Weapon_Bow and Weapon_Staff ride LeftHand 514 / 710 times against 17 / 17 on RightHand,
    and those 17 are the SAME 17 records for both classes - the tombrot / creeping-slime /
    repugnant-decay pile and the three earth elementals, none of which has a humanoid hand.
    All 17 reach a bow AND a staff through one shared chain
    (`...\MasterTables\All_Dyn_N0{1b,2,3}.dbr`), i.e. they use lootRightHandItem1 as a
    GENERIC DROP CHANNEL rather than as an equipment slot. That is precisely the
    anti-pattern this lane removes from the Devourer, so they corroborate the design rather
    than weaken it - but they are not zero, and this module does not pretend they are.
ROUND-3 CORRECTION, recorded rather than quietly overwritten: the census published at
rounds 1-2 (Spear 122/0, Sword 144/24, Bow 0/49, Shield 0/144) was an artefact of THIS
MODULE'S OWN BUG. `db.has_record()` is an exact-case dict lookup; the arz stores record
NAMES lowercase but its internal REFERENCES mixed-case, so every mixed-case chain resolved
to nothing, was classified as an "unresolved leaf" and was dropped by every caller. The
old table was therefore a census of the ~1/8 of chains whose reference spelling happened to
be lowercase. `_resolve()` below fixes the lookup; the numbers above are the re-derivation.

(-9) THE BOW IS REAL AND IT IS EQUIPPED. `um_bloodtoxeus_99.lootLeftHandItem1` =
`bleed_affix_high_{n,e,l}` at `chanceToEquipLeftHand` 100 / weight 100 (vs the unique
shield row at weight 19). Those three tables were curated by AFFIX, not by class:
`bleed_affix_high_n` = **u_n_tendonripper (Weapon_Bow)** + 2 axes, `bleed_affix_high_l` =
**u_l_nemesis'recurve (Weapon_Bow)** + 2 axes (`_e` is 3 axes, no bow). LeftHand is
exactly where the engine expects a bow, so ~28% of Devourer spawns wield one and fight as
an archer. Written by `apply_svc_patches._wire_blood_toxeus_loot`, which used the two hand
slots as generic "guaranteed drop" channels rather than as equipment slots - the same
mistake put `crimsonverdict_guaranteed_*` in his WEAPON hand at weight 100, and 3 of that
table's 4 equal-weight members are ARMOUR (Armor_Head / Armor_UpperBody / Armor_Forearm),
so 63.0% of shipped Devourer spawns roll a piece of armour into the sword hand.

(-3) THE HUNT HAS NO ARMOUR AT ALL. `um_toxeus_hunt_99` / `um_toxeus_hunt_l_99` carry NO
`lootTorso*`, `lootLowerBody*`, `lootForearm*`, `lootHead*` or `lootLeftHand*` fields
whatsoever, and `chanceToEquipFinger1/Misc1/Misc2/Misc3` are all 0.0 - three worn slots
missing outright and four more switched off. He is literally naked. His WEAPON, though, is
correct and stays untouched: RightHand 100% -> `runbreaker_guaranteed_{n,e,l}` -> exactly
one `Weapon_Spear` (`svc_{t}_runbreaker`), and spears ride RightHand 493-to-0 in the base
game. R-247 round 3 bound the spear + unarmed animation rows; the missing half was the
loadout, exactly as Will described it ("not wearing any equipment").
His mesh can wear armour: `SkeletonRumorBoss.msh` has 18 base-game carriers and the
boss-tier ones (`jg17_undeadtyrant_{17,19,22}`) wire Head 20 / Torso 100 / LowerBody 50 /
Forearm 50 / LeftHand 100 / RightHand 100 - the pairing is base-game-proven, not assumed.

(-10) THE 100% SOUL PIN IS INTACT; THE ANOMALY IS THE HANDS. Verified in the shipped arz:
`chanceToEquipFinger2` = 100.0 (R-243's pin, byte-unchanged), `lootFinger2Item1` =
`blood_toxeus_soul_{n,e,l}`, all three resolve, all three are `Jewelry_Ring` /
`itemClassification Magical` / `itemLevel 40 / 68 / 100` per difficulty - field-for-field
the same shape as the Enslaver and Hunt souls (also Ring / Magical / 40-68-100) that have
never been reported missing. Exactly ONE record in the whole DB carries
`tagMonsterHemorrheus` and every spawn pool (`q_bloodtoxeus_lone`, `egg_blooddragon`, the
ambush) names that same record, so "the killed instance was a different variant" is
refuted. The ONLY structural difference between the Devourer's equip block and his three
siblings' is the cross-class hand wiring above. This module removes that anomaly.
HONEST LIMIT, AND IT IS THE HEADLINE: the engine path from a class-mismatched hand roll to
a skipped Finger2 equip is NOT provable from the bytes, so **-10 IS NOT CLOSED BY THIS
LANE**. It closes on Will's next kill - `BL-R252-DEBT-1`, with the escalation lever
pre-designed (move the soul onto the Misc4 channel, which R-247.6a proved delivers
in-game: "Will's kill DID drop it").

WHAT THIS MODULE WRITES (and nothing else)
------------------------------------------
THE DEVOURER (`um_bloodtoxeus_99`), 8 fields on 1 record + 2 table edits + 3 new tables.
The governing idea: THE WEAPON HAND IS FOR WEAPONS. Every armed row of his RightHand
yields a one-handed melee weapon and nothing else, so the sword hand can never come up
empty; the one deliberately mixed row - the 4-piece set's drop channel - lives in the
OFF hand, where a mis-class roll costs a shield instead of the sword Will went looking for.
  * LeftHand item1  `bleed_affix_high_*` -> `shields\commondynamic\shield_{n01b,e01,l01}`
    @100 - the Enslaver's byte-identical shield array. THE BOW IS GONE.
  * LeftHand item2 = `crimsonverdict_guaranteed_{n,e,l}` @19 - the 4-piece set table keeps
    a drop channel (RETIREMENT PROTOCOL: it has exactly ONE referrer in the whole db, so
    dropping the row would orphan the entire set). This is the module's ONE allowlisted
    mixed row and the gate names it explicitly.
  * LeftHand item5 (`shields\unique\shield_{n,e,l}01` @19) is ASSERTED, never written.
  * RightHand item1 `crimsonverdict_guaranteed_*` -> NEW `veinrender_guaranteed_{n,e,l}`
    (FixedWeight, one row: `svc_{t}_veinrender` @100) - the Runbreaker pattern, so his
    signature sword is wielded and guaranteed-dropped whenever that row wins.
  * RightHand item2 = the de-bowed `bleed_affix_high_{n,e,l}` @19 - the high-bleed uniques
    move to the slot their class belongs in instead of being retired.
  * RightHand item5 (`weapons\unique\sword_{n,e,l}01` @19) is ASSERTED, never written.
  * `bleed_affix_high_n` / `_l` are DE-BOWED: the Weapon_Bow row is dropped and the two
    Weapon_Axe rows compact to lootName1/2 (row 3 blanked, weight 0). `_e` is asserted
    bow-free and left byte-untouched.

  THE RESULTING ROLLS, computed by the gate itself over the real arz (not asserted by
  hand - `verify()` prints them every build):
    RightHand, weights 100/19/19 = 138 total, EVERY row one-handed melee ->
        armed 100.0000%   his own Vein Render 72.4638%   bleed-affix axe 13.77%
        unique sword 13.77%.  The weapon hand can never be empty.
    LeftHand,  weights 100/19/19 = 138 total ->
        shield 86.2319%.  The other 13.7681% is the Crimson Verdict set roll: it DROPS
        the rolled piece (R-247.6a proved a rolled item drops even when its class cannot
        be worn) but leaves the off hand bare - 10.33% a set armour piece, 3.44% a second
        Vein Render.
  The gate re-derives these from the final db and fails below the named floors
  `_MIN_ARMED_HAND_PCT` / `_MIN_SIGNATURE_PCT` / `_MIN_SHIELD_PCT`, so the sentence in
  `docs/WILL_TEST_GUIDE.md` cannot drift away from the bytes.
  FOR CONTRAST, the SHIPPED b888f022 numbers the gate reports on the same arz:
        armed 36.97%   Vein Render 21.01%   shield 15.97%
  i.e. 63.03% of shipped Devourer spawns roll ARMOUR into the sword hand. Will filed
  "i dont think he has a weapon" about the Hunt; the Devourer had the same disease.

  ⚠️ DISCLOSED SIDE EFFECT (round 4) - THE CRIMSON VERDICT ARMOUR DROPS 6.1x LESS OFTEN.
  Rounds 1-3 stated the post-state numbers and never stated the DELTA, which made a
  player-visible balance change ride silently inside a bug-fix lane. Stated plainly now,
  measured on b888f022 and re-derived by gate arm E2d on every build:
      shipped   RightHand = crimson@100 + unique_sword@19 (119)  -> the set table wins
                84.0336% of that hand, so EACH of its 4 equal-weight members dropped at
                21.0084% per kill (the 3 armour members combined 63.03%).
      after     LeftHand  = shield@100 + crimson@19 + unique_shield@19 (138) -> the set
                table wins 13.7681%, so each member drops at 3.4420% (armour combined
                10.3261%).
  A full reverse-reference scan of the shipped arz confirms `crimsonverdict_guaranteed_*`
  is the ONLY drop path in the whole db for the helm / cuirass / armband (its single
  referrer is this record's `lootRightHandItem1`; the only other mention anywhere is
  `svc_crimsonverdict.dbr` setMembers, which is the set DEFINITION, not a drop). So this
  is a 6.1x slowdown on farming three pieces of a hand-designed 4-piece set. THE FOURTH
  member goes the other way: Vein Render 21.0084% -> 72.4638% wielded AND dropped.
  WHY THE CHEAP RESTORATION WAS NOT TAKEN, measured rather than assumed. The obvious
  remedy is a drop chute on a slot `_SLOT_CLASSES` does not govern, but the Devourer has
  no free one - all 12 slots are wired except `Head`, which is 0 by the family's
  bare-skull design:
      Misc2 is an 18%-chance slot (relics@88 + arcane formulae@12), so its per-member
        ceiling is 0.18/4 = 4.5% even at infinite weight. It CANNOT reach 21% at all.
      Misc4 is 100% chance but its single row is `svc_devourer_misc4_master`, a 50/50
        between the Toxeus rant scroll and the End-of-All-Things formula. Restoring 21.01%
        per member there needs weight 526 against 100, which cuts BOTH of those from 50%
        to 7.99% - trading this lane's undisclosed nerf for a fresh undisclosed nerf on
        R-247.6a content.
  Every remaining option (turn `Head` on, split the set table into class-correct rows on
  Torso/Forearm, or fatten the off-hand row and give up the shield share) is a BALANCE
  decision on content Will hand-designed and never asked this lane to touch. So the rate
  change is DISCLOSED, GATED (E2d) and REGISTERED as BL-R252-DEBT-7 with all three options
  costed, for Will to ratify - it is not decided here.

THE HUNT (`um_toxeus_hunt_99` + `um_toxeus_hunt_l_99`), 2 records, 0 new tables:
  * Torso / LowerBody / Forearm wired at 100 with the tier-02 loot family his own record
    already uses everywhere else (finger_n02, amulet_n02, relic_15-21), common @5000 +
    unique @19 - his brothers' exact weight shape. All 18 tables measured class-pure on
    all three difficulties.
  * `chanceToEquipFinger1` 0 -> 100, `Misc1` 0 -> 100, `Misc2` 0 -> 18, `Misc3` 0 -> 50:
    the family values, on loot tables ALREADY present and dead on his record.
  * Head and LeftHand stay OFF by design: both brothers ship Head 0 (the family's bare
    skull, and R-102/R-247.5a tuned that skull deliberately) and his spear is two-handed.
  * His spear, his soul pin and his Misc4 rite formula are ASSERTED, never written.

NOT WRITTEN BY THIS MODULE, deliberately: `controller` on any Toxeus record (the
`enslaver_shroud` R-250 lane owns that field on the 4 roster surfaces - zero field
intersection with this lane), `chanceToEquipFinger2` anywhere (R-243's pin is asserted
only, so `tools/verify_soul_drop_rates.py --gate` stays green by construction), and any
Pet.tpl record (the Monster.tpl-equipment-onto-Pet.tpl crash law never comes near this).

REGISTRY POSITION: immediately after `r247_bloodcave_rulings`, before the no-op `visuals`.
This module must be the LAST writer of these equip fields - every other writer of the two
records (`toxeus_hunt_encounter`, `toxeus_hunt_endless`, `enslaver_shroud`, `devourer_kit`,
`champion_mesh`, `r247_boss_forms`, `toxeus_champion_kits`, `r247_bloodcave_rulings`) is
registered earlier, and apply() FAILS LOUD on any pre-state it did not measure.

GATE (verify, post-finalization, over the FINAL assembled db). EVERY arm resolves record
references CASE-INSENSITIVELY via `_resolve` and compares class stems CASE-FOLDED, so a
violating row can no longer hide behind a mixed-case table reference (2,436 reference
occurrences in the shipped mod arz, spanning 402 distinct reference strings, resolve only
case-insensitively) or behind a lowercase template stem:
  E1 no Toxeus champion slot's loot chain yields Weapon_Bow or Weapon_Staff anywhere, on
     ANY difficulty (the shipped bug was Normal+Legendary-only, so every arm below walks
     all three difficulty tables of every row, never just tier N);
  E2 every armed row of every class-governed slot yields ONLY classes that slot can wear,
     except the single row named in `_MIXED_DROP_ROWS` - an allowlist that is validated at
     import time to contain nothing but governed slots, so it can neither be widened
     silently nor accumulate entries the gate never consults;
  E2b the Devourer's literal hand wiring, INCLUDING `chanceToEquipRightHand` /
     `chanceToEquipLeftHand` themselves at 100. E1/E2 SKIP any slot whose chanceToEquip is
     0, so switching a hand off would otherwise delete it from the sweep instead of failing
     it - and "he has no weapon" is the literal text of Will's -3 report;
  E2c the MEASURED roll arithmetic of the Devourer's two hands (armed / signature / shield
     shares, minimum over the three difficulties) clears the named floors - this is the arm
     that makes the player-facing claim falsifiable. A hand whose selectable distribution is
     EMPTY (slot on, every row weight 0) is reported as DEAD and fails; it is never scored
     as a vacuous 100%;
  E2d the MEASURED per-kill drop share of each Crimson Verdict ARMOUR member, summed over
     EVERY equip slot of the Devourer (not just the one this lane wires) and minimised over
     the three difficulties, must equal the published `_CRIMSON_MEMBER_PCT` within
     `_CRIMSON_MEMBER_TOL`. TWO-SIDED ON PURPOSE: the floor catches further dilution or a
     deleted channel, and the CEILING catches a silent restoration - because the number is
     published in four Will-visible places and a change that leaves those stale is the exact
     defect this arm exists to prevent (a balance change riding inside a bug-fix lane). The
     arm walks the MONSTER RECORD only, so a container-side channel (BL-R252-DEBT-3 parks
     the helm's natural home in the Devourer's stash chest, owned by the chest-generosity
     lane) does not trip it;
  E3 both Hunt records wear Torso + LowerBody + Forearm at 100 on class-correct tables,
     and still carry the Runbreaker spear at RightHand 100 and the Misc4 rite at 100;
  E4 all four R-48 champions keep `chanceToEquipFinger2` = 100 with a soul table that
     resolves to a real Jewelry_Ring (the -10 defect class);
  E5 MOD-WIDE: EVERY creature pinned at `chanceToEquipFinger2` = 100 must have a Finger2
     chain that resolves to a Jewelry_Ring - a 100% pin pointing at nothing, or at a class
     the ring slot cannot hold, is the "did not drop his soul" bug in its purest form. The
     seven PRE-EXISTING offenders measured in b888f022 (outside this lane's surface) are
     named individually in `_E5_PREEXISTING` and registered as BL-R252-DEBT-5, so the arm is
     live for anything NEW without this lane reding the build on someone else's records.
Standalone twin: `py tools/gate_toxeus_boss_equipment.py [arz]`
Negative test:   `py tools/patches/toxeus_boss_equipment.py --negtest`
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

MODULE_NAME = ("R-252 Toxeus boss equipment - the Endless Hunt wears the family's armour, "
               "the Devourer of Blood carries a melee weapon and a shield instead of a bow, "
               "and every champion hand slot holds a class that slot can wear")

# ── the records ─────────────────────────────────────────────────────────────
_DEVOURER = 'records\\xpack\\creatures\\monster\\skeleton\\um_bloodtoxeus_99.dbr'
_ENSLAVER = 'records\\creature\\monster\\shadowstalker\\um_toxeus_enslaver_99.dbr'
_HUNT = 'records\\creature\\monster\\shadowstalker\\um_toxeus_hunt_99.dbr'
_HUNT_L = 'records\\creature\\monster\\shadowstalker\\um_toxeus_hunt_l_99.dbr'
_HUNTS = (_HUNT, _HUNT_L)
# The four R-48 champions pinned at 100% soul by R-243 (asserted, never written).
_CHAMPIONS = (_DEVOURER, _ENSLAVER, _HUNT, _HUNT_L)


# ── the tables ──────────────────────────────────────────────────────────────
def _t(fmt):
    return [fmt % t for t in ('n', 'e', 'l')]


_LOOT = 'records\\item\\loottables\\'
_BLEED = _t(_LOOT + 'svc\\bleed_affix_high_%s.dbr')
_CRIMSON_SET = _t(_LOOT + 'svc\\crimsonverdict_guaranteed_%s.dbr')
_VEINRENDER_TAB = _t(_LOOT + 'svc\\veinrender_guaranteed_%s.dbr')     # NEW, this module
_VEINRENDER_ITEM = _t('records\\item\\equipmentweapon\\sword\\svc_%s_veinrender.dbr')
_RUNBREAKER = _t(_LOOT + 'svc\\runbreaker_guaranteed_%s.dbr')
_RITE = [_LOOT + 'svc\\svc_rite_guaranteed.dbr'] * 3

# the Enslaver's own shield array (tier-01 family, byte-identical to his record)
_SHIELD_COMMON = [_LOOT + 'shields\\commondynamic\\shield_n01b.dbr',
                  _LOOT + 'shields\\commondynamic\\shield_e01.dbr',
                  _LOOT + 'shields\\commondynamic\\shield_l01.dbr']
# the Devourer's SHIPPED unique rows on both hands - asserted, never written, because the
# measured roll arithmetic below depends on them.
_SHIELD_UNIQUE = _t(_LOOT + 'shields\\unique\\shield_%s01.dbr')
_SWORD_UNIQUE = _t(_LOOT + 'weapons\\unique\\sword_%s01.dbr')

# the Hunt's own tier-02 loot family (matches finger_n02 / amulet_n02 already on his record)
_HUNT_ARMOUR = {
    'Torso': (_t(_LOOT + 'torso\\commondynamic\\melee_%s02.dbr'),
              _t(_LOOT + 'torso\\unique\\melee_%s02.dbr')),
    'LowerBody': (_t(_LOOT + 'legs\\commondynamic\\greaves_%s02.dbr'),
                  _t(_LOOT + 'legs\\unique\\greaves_%s02.dbr')),
    'Forearm': (_t(_LOOT + 'arms\\commondynamic\\armband_%s02.dbr'),
                _t(_LOOT + 'arms\\unique\\armband_%s02.dbr')),
}
# the family (Enslaver + Devourer) weight vocabulary for an equipment slot
_W_COMMON, _W_UNIQUE, _W_GUARANTEED = 5000, 19, 100
# the family chances the Hunt's dead slots are switched on to
_HUNT_MISC_CHANCES = {'Finger1': 100.0, 'Misc1': 100.0, 'Misc2': 18.0, 'Misc3': 50.0}

# The Hunt's three soul pets (built by `r247_boss_forms`, R-247.6c). Dressing the
# SOURCE without re-dressing them breaks the PET-GEAR-PARITY law - see _resync_hunt_pets.
_HUNT_PETS = tuple('records\\skills\\soulskills\\pets\\toxeus_hunt_%d.dbr' % i
                   for i in (1, 2, 3))

# STRUCTURAL GUARD (import-time, not a runtime hope): the two slot sets this module
# writes may never include Finger2. R-243 pinned the four champions' soul rate at 100
# and its record-diff proved all 16 pin records byte-unchanged; this lane asserts that
# pin and must never touch it, which is what keeps `tools/verify_soul_drop_rates.py
# --gate` green by construction rather than by luck.
assert 'Finger2' not in _HUNT_ARMOUR, 'R-243: Finger2 is asserted, never written'
assert 'Finger2' not in _HUNT_MISC_CHANCES, 'R-243: Finger2 is asserted, never written'

# the bow rows this module removes (measured in the shipped arz b888f022)
_BOW_ROWS = {
    _BLEED[0]: 'records\\item\\equipmentweapon\\bow\\u_n_tendonripper.dbr',
    _BLEED[2]: "records\\item\\equipmentweapon\\bow\\u_l_nemesis'recurve.dbr",
}

# ── the slot-class law (base-game census, see docstring) ────────────────────
# STORED LOWERCASE, COMPARED CASE-FOLDED, and `_validate_class_sets` refuses any entry that
# is not lowercase. The base game spells the same class both ways - Weapon_Axe 407 records
# / weapon_axe 50, Weapon_Mace 469 / weapon_mace 42, Weapon_Sword 558 / weapon_sword 6,
# Weapon_Spear 439 / weapon_spear 1, Armor_Head 1382 / armor_head 2, Armor_UpperBody 1397 /
# armor_upperbody 1 - and the mod arz adds Weapon_RangedOneHand beside the base game's
# lowercase weapon_rangedonehand. A set written in one spelling silently fails to recognise
# the other, which is fail-CLOSED noise on a legitimate item (round-2 shipped exactly that:
# 'weapon_rangedonehand' was listed and 'Weapon_RangedOneHand' was not).
_ONE_HAND_MELEE = {'weapon_sword', 'weapon_axe', 'weapon_mace', 'weapon_spear',
                   'weaponmelee_sword', 'weapon_rangedonehand'}
_SLOT_CLASSES = {
    'Head': {'armor_head'},
    'Torso': {'armor_upperbody'},
    'LowerBody': {'armor_lowerbody'},
    'Forearm': {'armor_forearm'},
    'LeftHand': {'weaponarmor_shield'},
    'RightHand': set(_ONE_HAND_MELEE),
    'Finger1': {'jewelry_ring'},
    'Finger2': {'jewelry_ring'},
    'Misc3': {'jewelry_amulet'},
}
# Classes that must never appear in ANY Toxeus champion slot, governed or not: the
# two-handed ranged families. This is Will's -9 defect class, stated as an invariant.
_BANNED_CLASSES = {'weapon_bow', 'weapon_staff'}

# THE ALLOWLIST. Exactly one row in this lane is deliberately mixed-class: the 4-piece
# Crimson Verdict set's only drop channel, parked in the OFF hand so a mis-class roll can
# never cost the Devourer his weapon. Slots with no entry in _SLOT_CLASSES (Misc1 potions,
# Misc2 relics/formulae, Misc4 the EoAT rite) have no single wearable class and are NOT
# class-governed at all - they are covered by the E1 banned-class arm only, so listing them
# here would be dead weight that reads like coverage. `_validate_allowlist` enforces that.
_MIXED_DROP_ROWS = {
    (_DEVOURER, 'LeftHand', 2): 'crimsonverdict_guaranteed_{n,e,l} - the 4-piece set drop '
                                'row; it is the set table\'s ONLY referrer in the db, so '
                                'the row cannot be dropped without orphaning the set',
}
_SLOTS = ('Head', 'Torso', 'LowerBody', 'Forearm', 'LeftHand', 'RightHand',
          'Finger1', 'Finger2', 'Misc1', 'Misc2', 'Misc3', 'Misc4')

# The measured floors the Devourer's hands must clear, minimum over all three difficulties.
# Computed by the gate from the final db, never asserted by hand. Shipped values with the
# 100/19/19 weight shape: armed 100.00, Vein Render 72.46, shield 86.23.
_MIN_ARMED_HAND_PCT = 100.0     # every armed RightHand row is a one-handed melee weapon
_MIN_SIGNATURE_PCT = 70.0       # ... and most of them are his own sword
_MIN_SHIELD_PCT = 85.0          # the off hand is a shield, bar the set-drop roll

# THE DISCLOSED SET-DROP RATE (see the ⚠️ block in the docstring). The three worn Crimson
# Verdict pieces have exactly ONE drop path in the whole db, and this lane moves it from the
# weapon hand @100 to the off hand @19: 21.0084% -> 3.4420% per piece per kill, a 6.1x
# slowdown on a hand-designed 4-piece set. That is a BALANCE change inside a bug-fix lane,
# so it is published in four Will-visible places, registered as BL-R252-DEBT-7 for Will to
# ratify, and pinned here by gate arm E2d.
# TWO-SIDED, and the ceiling is the important half: a later lane that RESTORES the rate
# (any of DEBT-7's three costed options) must update this constant and the four documents
# in the same commit, exactly as a lane that dilutes it further must. A drop rate that can
# move without the docs moving is how round 1-3 shipped the nerf silently in the first
# place. Derivation, so it re-derives by hand: 19/(100+19+19) x 1/4 = 3.44203%.
_CRIMSON_MEMBER_PCT = 3.4420
_CRIMSON_MEMBER_TOL = 0.05
# The three WORN members of the set (the fourth, svc_{t}_veinrender, is covered by
# _MIN_SIGNATURE_PCT instead - it is the one member this lane makes commoner, not rarer).
_CRIMSON_ARMOUR = {
    'helm (Armor_Head)': _t('records\\item\\equipmenthelm\\svc_%s_crimsonverdict.dbr'),
    'cuirass (Armor_UpperBody)': _t('records\\item\\equipmentarmor\\svc_%s_crimsonverdict.dbr'),
    'armband (Armor_Forearm)': _t('records\\item\\equipmentarmband\\svc_%s_crimsonverdict.dbr'),
}


# E5's PRE-EXISTING offenders, measured in the shipped b888f022 and named individually so
# the arm stays LIVE for anything new. All seven are outside this lane's surface (harpy
# quest bosses and the DRX bloodwitch reavers), all seven predate R-252, and all seven are
# registered as BL-R252-DEBT-5. An entry here is a dated exception, not a blessing.
_E5_PREEXISTING = {
    'records\\creature\\monster\\harpy\\quest_celtheano_19.dbr':
        'pinned 100% with lootFinger2Item1 EMPTY (base-game harpy quest boss)',
    'records\\creature\\monster\\harpy\\quest_celtheano_20.dbr':
        'pinned 100% with lootFinger2Item1 EMPTY (base-game harpy quest boss)',
    'records\\drxcreatures\\bloodwitch\\d_reaver_40.dbr':
        'pinned 100% with Finger2 pointed at a WAND master table (DRX upstream)',
    'records\\drxcreatures\\bloodwitch\\d_reaver_41.dbr':
        'pinned 100% with Finger2 pointed at a WAND master table (DRX upstream)',
    'records\\drxcreatures\\bloodwitch\\d_reaver_42.dbr':
        'pinned 100% with Finger2 pointed at a WAND master table (DRX upstream)',
    'records\\drxcreatures\\bloodwitch\\x2d_reaver_01.dbr':
        'pinned 100% with Finger2 pointed at a WAND master table (DRX upstream)',
    'records\\drxcreatures\\bloodwitch\\svc_leinth_guard_reaver.dbr':
        'pinned 100% with Finger2 pointed at a WAND master table (DRX upstream)',
}
# (spelled out rather than via `_norm`, which is defined further down)
_E5_PREEXISTING_LC = {k.replace('/', '\\').strip().lower() for k in _E5_PREEXISTING}


def _validate_class_sets():
    """Every class name compared against must be stored lowercase.

    Comparisons are case-folded because the game data spells the same class both ways (see
    the block above `_ONE_HAND_MELEE`). A set entry that is NOT lowercase can therefore
    never match anything, which turns a coverage set into dead weight without any symptom.
    This refuses at import rather than at some later build.
    """
    sets = [('_ONE_HAND_MELEE', _ONE_HAND_MELEE), ('_BANNED_CLASSES', _BANNED_CLASSES)]
    sets += [('_SLOT_CLASSES[%s]' % k, v) for k, v in sorted(_SLOT_CLASSES.items())]
    bad = sorted({'%s: %r' % (n, c) for n, s in sets for c in s if c != c.lower()})
    if bad:
        raise AssertionError(
            "class sets must be stored lowercase because every comparison is case-folded; "
            "these are not: %s" % '; '.join(bad))
    return True


_validate_class_sets()


def _validate_allowlist(rows):
    """Every allowlisted row must name a slot the gate actually class-governs.

    Without this, an entry for an ungoverned slot (Misc1/Misc2/Misc4) sits in the dict
    looking like a sanctioned exception while the checker never reaches it - an allowlist
    that overstates what it governs is worse than no allowlist.
    """
    bad = sorted({slot for (_rec, slot, _idx) in rows if slot not in _SLOT_CLASSES})
    if bad:
        raise AssertionError(
            "_MIXED_DROP_ROWS names slot(s) %s that _SLOT_CLASSES does not govern, so the "
            "gate can never consult those entries. Either govern the slot or drop the "
            "entry." % ', '.join(bad))
    return True


_validate_allowlist(_MIXED_DROP_ROWS)


# ── tiny db helpers (work on the real ArzDatabase and on the negtest stub) ──
def _gv(db, rec, field, default=None):
    v = db.get_field_value(rec, field)
    if isinstance(v, (list, tuple)):
        v = v[0] if v else None
    return default if v is None else v


def _gl(db, rec, field):
    v = db.get_field_value(rec, field)
    if v is None:
        return []
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v]
    return [str(v)]


def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _i(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _close(a, b, tol=0.05):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def _norm(p):
    return str(p or '').replace('/', '\\').strip().lower()


def _same(got, want):
    return [_norm(x) for x in got] == [_norm(x) for x in want]


def _rec_count(db):
    """Cheap record count, used only to invalidate the case-fold index."""
    for attr in ('_raw_records', 'd'):
        m = getattr(db, attr, None)
        if isinstance(m, dict):
            return len(m)
    return len(db.record_names())


def _rec_index(db):
    """{lowercased record name: the db's own spelling}, built once and cached on the db.

    THE BUG THIS EXISTS TO KILL (round 3). `db.has_record()` is an exact-case dict lookup.
    The arz stores record NAMES lowercase (0 of the base game's 74,013 contain an uppercase
    letter) but its internal REFERENCES mixed-case - 2,436 references in the shipped mod arz
    resolve ONLY case-insensitively. Every such reference used to miss, `_leaf_items` filed
    the chain as an "unresolved leaf", and every caller then IGNORED it by design. Two
    consequences, both shipped at round 2: the class arms carrying Will's -9 invariant were
    BLIND to any violating row reached through a mixed-case reference, and the base-game
    census this lane published as design law counted only the ~1/8 of chains whose reference
    spelling happened to be lowercase.

    The index is invalidated by record COUNT, which is sound here because the only records
    this module creates are the three `veinrender_guaranteed_*` tables it spells itself in
    lowercase (so they resolve by exact match regardless) and because nothing in the build
    renames a record in place.
    """
    cached = getattr(db, '_r251_rec_index', None)
    n = _rec_count(db)
    if cached is not None and cached[0] == n:
        return cached[1]
    idx = {}
    for name in db.record_names():
        idx.setdefault(_norm(name), name)
    try:
        db._r251_rec_index = (n, idx)
    except AttributeError:                 # a db that refuses attributes: rebuild each call
        pass
    return idx


def _resolve(db, path):
    """The db's own spelling of `path`, or None when the record genuinely does not exist."""
    if not path:
        return None
    if db.has_record(path):
        return path
    return _rec_index(db).get(_norm(path))


def _has(db, path):
    return _resolve(db, path) is not None


def _banned_of(classes):
    """The banned class stems in `classes`, in their ORIGINAL spelling (for the message)."""
    return {c for c in classes if str(c).lower() in _BANNED_CLASSES}


def _wrong_of(classes, allowed):
    """The stems in `classes` that `allowed` (a lowercase set) does not permit."""
    return {c for c in classes if str(c).lower() not in allowed}


def _set(db, rec, field, value, dtype_if_new=None):
    """Write a field, passing an explicit dtype ONLY when the field is NEW.

    The dtype-preservation law both ways: never pass a dtype to an existing field
    (silent INT/FLOAT corruption), always pass one to a field that does not exist yet
    (the sanctioned arm - a brand-new field has no dtype to preserve). EVERY write in
    this module goes through here, including the ones that author new records: a table
    this module authored on a previous pass is an EXISTING record, and its fields must
    then be written dtype-free like any other.
    """
    if db.get_field_value(rec, field) is None and dtype_if_new is not None:
        db.set_field(rec, field, value, dtype_if_new)
    else:
        db.set_field(rec, field, value)


def _base_fields(db, rec):
    """Field base-names of a record, '###' suffixes stripped and de-duplicated."""
    out = []
    seen = set()
    for k in (db.get_fields(rec) or {}):
        kk = str(k).split('###')[0]
        if kk not in seen:
            seen.add(kk)
            out.append(kk)
    return out


def _leaf_items(db, table, weight=1.0, depth=0, seen=(), out=None):
    """Expand a loot chain to {leaf record path: probability}, honouring lootWeightN.

    The class SET alone cannot answer "how often is his hand empty" - that needs the
    per-member weights, because the Crimson Verdict table is 1 sword + 3 armour at equal
    weight. Records not in `db` are base-game records that exist at runtime but not in the
    mod arz; they come back as leaves whose class resolves to the sentinel '' and every
    caller IGNORES them (an unresolved leaf is never a violation - that would cry wolf on
    half the base game).

    CASE (round 3): resolution goes through `_resolve`, so a reference that differs from the
    stored record name only by case is FOLLOWED, not written off as unresolved. Before that
    fix the "unresolved leaf is never a violation" rule silently swallowed 2,436 references
    that do resolve, which is how a violating row could hide behind a mixed-case spelling.
    RE-MEASURED with the fixed resolver over b888f022, walking every armed slot of all four
    champions: 1,547 leaves pre-apply and 2,553 post-apply, ZERO unresolved in either. So
    the shares below are exact, not lower bounds - and unlike round 2, that is now a claim
    about the whole leaf set rather than about the subset the lookup happened to reach.
    """
    if out is None:
        out = {}
    if not table or weight <= 0 or depth > 6 or _norm(table) in seen:
        return out
    real = _resolve(db, table)
    if real is None:
        out[table] = out.get(table, 0.0) + weight
        return out
    kids = []
    for kk in _base_fields(db, real):
        low = kk.lower()
        if not low.startswith(('lootname', 'itemname', 'bothname')):
            continue
        idx = ''.join(ch for ch in kk if ch.isdigit())
        w = _f(_gv(db, real, 'lootWeight%s' % idx, 0)) if idx else 0.0
        paths = [x for x in _gl(db, real, kk) if x.lower().endswith('.dbr')]
        for p in paths:
            kids.append((p, w / len(paths)))
    if not kids:
        out[real] = out.get(real, 0.0) + weight
        return out
    total = sum(w for _p, w in kids)
    if total <= 0:                     # unweighted table: treat members as equiprobable
        kids = [(p, 1.0) for p, _w in kids]
        total = float(len(kids))
    nxt = tuple(seen) + (_norm(table),)
    for p, w in kids:
        _leaf_items(db, p, weight * w / total, depth + 1, nxt, out)
    return out


def _class_of(db, path):
    """The item's templateName stem in its ORIGINAL spelling, '' if not in this db.

    Callers compare case-folded (`_banned_of` / `_wrong_of` / `_pct_class`); the original
    spelling is kept so an offender message names the stem the way the record spells it.
    """
    real = _resolve(db, path)
    if real is None:
        return ''
    stem = str(_gv(db, real, 'templateName', '') or '').replace('/', '\\').rsplit('\\', 1)[-1]
    return stem[:-4] if stem.lower().endswith('.tpl') else stem


def _leaf_classes(db, table):
    """Set of leaf item class stems for a loot chain ('' = unresolved, always ignored)."""
    return {_class_of(db, p) for p in _leaf_items(db, table)}


def _slot_rows(db, rec, slot):
    """[(index, weight, [tables per difficulty])] for every armed row of a slot."""
    rows = []
    for i in range(1, 7):
        w = _f(_gv(db, rec, 'chanceToEquip%sItem%d' % (slot, i), 0))
        tabs = [t for t in _gl(db, rec, 'loot%sItem%d' % (slot, i)) if t.lower().endswith('.dbr')]
        if w > 0 and tabs:
            rows.append((i, w, tabs))
    return rows


def _slot_dist(db, rec, slot, diff):
    """{leaf item path: probability} for one slot on one difficulty, given it equips."""
    rows = _slot_rows(db, rec, slot)
    total = sum(w for _i, w, _t in rows)
    if total <= 0:
        return {}
    dist = {}
    for _i, w, tabs in rows:
        tab = tabs[diff] if diff < len(tabs) else tabs[0]
        for path, q in _leaf_items(db, tab).items():
            dist[path] = dist.get(path, 0.0) + q * w / total
    return dist


def _pct_class(db, dist, classes):
    """`classes` is a LOWERCASE set; the comparison is case-folded like every other."""
    return 100.0 * sum(q for p, q in dist.items()
                       if str(_class_of(db, p)).lower() in classes)


def _pct_items(dist, items):
    want = {_norm(x) for x in items}
    return 100.0 * sum(q for p, q in dist.items() if _norm(p) in want)


# ── apply ───────────────────────────────────────────────────────────────────
def _fixedweight(db, path, members, desc):
    """Author a LootItemTable_FixedWeight in the shape apply_svc_patches uses.

    Every write routes through `_set`, so a re-apply over a db where this table already
    exists writes dtype-free instead of re-declaring dtypes on existing fields.
    """
    from apply_svc_patches import (_ensure_record, DATA_TYPE_STRING, DATA_TYPE_INT,
                                   DATA_TYPE_FLOAT)
    S, I, F = DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT
    _ensure_record(db, path, 'Database\\Templates\\LootItemTable_FixedWeight.tpl')
    db._record_types[path] = 'LootItemTable_FixedWeight'
    _set(db, path, 'Class', 'LootItemTable_FixedWeight', S)
    _set(db, path, 'templateName', 'Database\\Templates\\LootItemTable_FixedWeight.tpl', S)
    _set(db, path, 'FileDescription', desc, S)
    for f in ('brokenRandomizerChance', 'prefixRandomizerChance', 'suffixRandomizerChance'):
        _set(db, path, f, 0.0, F)
    for i, m in enumerate(members, start=1):
        _set(db, path, 'lootName%d' % i, m, S)
        _set(db, path, 'lootWeight%d' % i, _W_GUARANTEED, I)
    # idempotency: blank any stale member row a previous pass may have left behind
    for i in range(len(members) + 1, 7):
        if db.get_field_value(path, 'lootName%d' % i) is not None:
            _set(db, path, 'lootName%d' % i, '')
            _set(db, path, 'lootWeight%d' % i, 0)
    db._modified.add(path)


def _assert_row(db, rec, slot, idx, want, why):
    got = _gl(db, rec, 'loot%sItem%d' % (slot, idx))
    if not _same(got, want):
        raise SystemExit(
            "[toxeus_boss_equipment] PRE-STATE DRIFT: %s loot%sItem%d = %r, expected %r "
            "(%s). This row is ASSERTED, never written - the measured roll arithmetic in "
            "the gate depends on it, so a different value means another writer appeared "
            "or this module is mis-ordered."
            % (rec.rsplit('\\', 1)[-1], slot, idx, got, want, why))


def apply(db, tags):
    from apply_svc_patches import DATA_TYPE_STRING as S
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    for rec in _CHAMPIONS:
        if not _has(db, rec):
            raise SystemExit("[toxeus_boss_equipment] champion record MISSING: %s" % rec)

    # ── 1. the Devourer's off-hand: bow pool -> the Enslaver's shield array ──
    lh = _gl(db, _DEVOURER, 'lootLeftHandItem1')
    if not _same(lh, _BLEED):
        raise SystemExit(
            "[toxeus_boss_equipment] PRE-STATE DRIFT: Devourer lootLeftHandItem1 = %r, "
            "expected the shipped bleed_affix_high_{n,e,l} written by "
            "apply_svc_patches._wire_blood_toxeus_loot. A different value means another "
            "writer appeared or this module is mis-ordered; refusing to overwrite an "
            "unmeasured state." % (lh,))
    if not _close(_gv(db, _DEVOURER, 'chanceToEquipLeftHand'), 100.0):
        raise SystemExit("[toxeus_boss_equipment] PRE-STATE DRIFT: Devourer "
                         "chanceToEquipLeftHand = %r, expected 100.0"
                         % _gv(db, _DEVOURER, 'chanceToEquipLeftHand'))
    _assert_row(db, _DEVOURER, 'LeftHand', 5, _SHIELD_UNIQUE, 'the shipped unique-shield row')
    _assert_row(db, _DEVOURER, 'RightHand', 5, _SWORD_UNIQUE, 'the shipped unique-sword row')
    _set(db, _DEVOURER, 'lootLeftHandItem1', list(_SHIELD_COMMON), S)
    _set(db, _DEVOURER, 'chanceToEquipLeftHandItem1', _W_GUARANTEED)
    # the 4-piece set table keeps its ONLY drop channel, in the hand where a mis-class
    # roll costs a shield rather than the sword (the module's one allowlisted mixed row)
    _set(db, _DEVOURER, 'lootLeftHandItem2', list(_CRIMSON_SET), S)
    _set(db, _DEVOURER, 'chanceToEquipLeftHandItem2', _W_UNIQUE)
    db._modified.add(_DEVOURER)

    # ── 2. his weapon hand: melee only, led by a guaranteed Vein Render ──────
    rh = _gl(db, _DEVOURER, 'lootRightHandItem1')
    if not _same(rh, _CRIMSON_SET):
        raise SystemExit(
            "[toxeus_boss_equipment] PRE-STATE DRIFT: Devourer lootRightHandItem1 = %r, "
            "expected the shipped crimsonverdict_guaranteed_{n,e,l}." % (rh,))
    for tab, item, tier in zip(_VEINRENDER_TAB, _VEINRENDER_ITEM, 'NEL'):
        if not _has(db, item):
            raise SystemExit("[toxeus_boss_equipment] Vein Render item MISSING: %s" % item)
        _fixedweight(db, tab, [item], 'Vein Render guaranteed - the Devourer of Blood (%s)' % tier)
    _set(db, _DEVOURER, 'lootRightHandItem1', list(_VEINRENDER_TAB), S)
    _set(db, _DEVOURER, 'chanceToEquipRightHandItem1', _W_GUARANTEED)
    # the high-bleed uniques move to the slot their class belongs in
    _set(db, _DEVOURER, 'lootRightHandItem2', list(_BLEED), S)
    _set(db, _DEVOURER, 'chanceToEquipRightHandItem2', _W_UNIQUE)

    # ── 3. de-bow the two bleed tables ──────────────────────────────────────
    debowed = 0
    for tab in _BLEED:
        members = []
        for i in range(1, 7):
            nm = _gv(db, tab, 'lootName%d' % i, '')
            if str(nm or '').lower().endswith('.dbr'):
                members.append(str(nm))
        bow = _BOW_ROWS.get(tab)
        if bow is None:
            known_bows = {_norm(v) for v in _BOW_ROWS.values()}
            if any(_norm(m) in known_bows for m in members):
                raise SystemExit("[toxeus_boss_equipment] unexpected bow in %s: %r"
                                 % (tab, members))
            continue
        if not any(_norm(m) == _norm(bow) for m in members):
            raise SystemExit(
                "[toxeus_boss_equipment] PRE-STATE DRIFT: %s no longer carries the "
                "measured bow row %s (members=%r). Measure before writing."
                % (tab.rsplit('\\', 1)[-1], bow.rsplit('\\', 1)[-1], members))
        kept = [m for m in members if _norm(m) != _norm(bow)]
        if len(kept) != 2:
            raise SystemExit("[toxeus_boss_equipment] %s: expected 2 non-bow members, "
                             "got %r" % (tab, kept))
        for i, m in enumerate(kept, start=1):
            _set(db, tab, 'lootName%d' % i, m)
            _set(db, tab, 'lootWeight%d' % i, _W_GUARANTEED)
        _set(db, tab, 'lootName%d' % (len(kept) + 1), '')
        _set(db, tab, 'lootWeight%d' % (len(kept) + 1), 0)
        db._modified.add(tab)
        debowed += 1
    print("  [-9] Devourer: RightHand is now MELEE-ONLY (veinrender_guaranteed@%d + the "
          "de-bowed bleed uniques@%d + the shipped unique-sword row@%d) so the weapon hand "
          "can never come up empty; LeftHand -> the Enslaver's shield array@%d + the "
          "4-piece set's drop row@%d + the shipped unique-shield row@%d; %d bleed table(s) "
          "de-bowed. He can no longer hold a bow in any slot."
          % (_W_GUARANTEED, _W_UNIQUE, _W_UNIQUE, _W_GUARANTEED, _W_UNIQUE, _W_UNIQUE,
             debowed))

    # ── 4. the Hunt puts on the family's armour ─────────────────────────────
    for rec in _HUNTS:
        spear = _gl(db, rec, 'lootRightHandItem1')
        if not _same(spear, _RUNBREAKER):
            raise SystemExit(
                "[toxeus_boss_equipment] PRE-STATE DRIFT: %s lootRightHandItem1 = %r, "
                "expected runbreaker_guaranteed_{n,e,l} (R-247.6b). His spear is asserted, "
                "never written - a different value means R-247 moved." % (rec, spear))
        if not _close(_gv(db, rec, 'chanceToEquipRightHand'), 100.0):
            raise SystemExit("[toxeus_boss_equipment] %s chanceToEquipRightHand = %r, "
                             "expected 100.0 (R-247.6b)" % (rec, _gv(db, rec, 'chanceToEquipRightHand')))
        if not _close(_gv(db, rec, 'chanceToEquipFinger2'), 100.0):
            raise SystemExit("[toxeus_boss_equipment] %s chanceToEquipFinger2 = %r, "
                             "expected R-243's 100.0 pin" % (rec, _gv(db, rec, 'chanceToEquipFinger2')))
        for slot, (common, unique) in sorted(_HUNT_ARMOUR.items()):
            if _f(_gv(db, rec, 'chanceToEquip%s' % slot, 0)) > 0:
                raise SystemExit(
                    "[toxeus_boss_equipment] PRE-STATE DRIFT: %s already equips %s at %r "
                    "- the measured defect is that all three armour slots are OFF. "
                    "Another writer got there first; measure before writing."
                    % (rec, slot, _gv(db, rec, 'chanceToEquip%s' % slot)))
            for tab in common + unique:
                if not _has(db, tab):
                    raise SystemExit("[toxeus_boss_equipment] armour table MISSING: %s" % tab)
            _set(db, rec, 'loot%sItem1' % slot, list(common), S)
            _set(db, rec, 'loot%sItem5' % slot, list(unique), S)
            _set(db, rec, 'chanceToEquip%sItem1' % slot, _W_COMMON)
            _set(db, rec, 'chanceToEquip%sItem5' % slot, _W_UNIQUE)
            _set(db, rec, 'chanceToEquip%s' % slot, 100.0)
        for slot, chance in sorted(_HUNT_MISC_CHANCES.items()):
            if not _slot_rows(db, rec, slot) and not _gl(db, rec, 'loot%sItem1' % slot):
                raise SystemExit("[toxeus_boss_equipment] %s has no loot table on %s - "
                                 "switching the slot on would equip nothing" % (rec, slot))
            _set(db, rec, 'chanceToEquip%s' % slot, chance)
        db._modified.add(rec)
    print("  [-3] Endless Hunt (both records): Torso/LowerBody/Forearm wired at 100%% on "
          "his own tier-02 loot family (common@%d + unique@%d) + Finger1 100 / Misc1 100 / "
          "Misc2 18 / Misc3 50 - the family shape. Spear, soul pin and Misc4 rite asserted "
          "and untouched; Head + LeftHand stay off by design (bare skull, two-handed spear)."
          % (_W_COMMON, _W_UNIQUE))
    # ── 5. the Hunt's SOUL PETS inherit the same armour ─────────────────────
    _resync_hunt_pets(db)

    print("  [-10] NOT CLOSED HERE: the 100% soul pin is asserted intact and the equip "
          "anomaly is gone, but the engine link is unprovable from the bytes - it closes on "
          "Will's next kill (BL-R252-DEBT-1).")
    print("=== toxeus_boss_equipment done ===\n")


def _resync_hunt_pets(db):
    """PET-GEAR-PARITY: re-mirror the Hunt's three soul pets onto the DRESSED source.

    Will's law, gated fail-loud by the monolith's `_verify_summon_pet_gear`, is that a
    summoned pet carries EXACTLY the gear its wild source form carries - both directions,
    per slot. `r247_boss_forms` (registry slot 32) builds `toxeus_hunt_1/2/3` through
    `_build_boss_summon` with `loadout=None`, which SNAPSHOTS the source's equip slots at
    that moment. This module is slot 67 and has to stay the last writer of those slots, so
    by the time it dresses the Hunt the pets' snapshot is three slots stale: the source
    wears Torso/LowerBody/Forearm and the pets stand there naked. That is 9 violations of
    the parity gate, and it is Will's own "not wearing any equipment" report reproduced on
    the pet - so the honest fix is to dress the pets too, not to narrow the gate.

    The re-mirror goes through the monolith's OWN sanctioned helpers, not a private path:
    `_mirror_source_loadout(strict=True)` reads the POST-R-252 source, `_loadout_spec`
    turns it into hard-coded item-table paths, and `_set_pet_equipment` writes them.
    **No Monster.tpl field is ever copied onto a Pet.tpl record** - that is the standing
    crash law (copying equipment/loot fields Monster -> Pet crashes the game, even when
    only changing the value of an existing field), and it is exactly why this uses
    `_set_pet_equipment` with hard-coded paths instead of any field-copy helper.

    The over-add half of the law is honoured too: every gear slot the source does NOT use
    is zeroed on the pet, the same clean-up `_build_boss_summon` does at build time.

    IDEMPOTENT and pre-state-checked like the rest of the module: it asserts the source is
    already dressed (this runs AFTER step 4) and fails loud if a pet record is missing.
    """
    from apply_svc_patches import (_mirror_source_loadout, _loadout_spec,
                                   _set_pet_equipment, _GEAR_SLOTS)

    for slot in sorted(_HUNT_ARMOUR):
        if not _close(_gv(db, _HUNT, 'chanceToEquip%s' % slot), 100.0):
            raise SystemExit(
                "[toxeus_boss_equipment] _resync_hunt_pets ran before the source was "
                "dressed: %s chanceToEquip%s = %r, expected 100.0. This must run AFTER "
                "step 4 or it would mirror the naked pre-state."
                % (_HUNT, slot, _gv(db, _HUNT, 'chanceToEquip%s' % slot)))

    missing = [p for p in _HUNT_PETS if not _has(db, p)]
    if missing:
        raise SystemExit(
            "[toxeus_boss_equipment] Hunt soul pet(s) MISSING: %s - r247_boss_forms "
            "(R-247.6c) builds them and must run before this module. Without them the "
            "PET-GEAR-PARITY gate has nothing to check and Will's summoned Hunt would "
            "keep fighting naked." % ', '.join(missing))

    loadout = _mirror_source_loadout(db, _HUNT, strict=True) or []
    slots = {s for s, _c, _w, _p in loadout}
    if not slots >= set(_HUNT_ARMOUR):
        raise SystemExit(
            "[toxeus_boss_equipment] the source mirror lost an armour slot: mirrored %s, "
            "expected at least %s. The pets would still fail PET-GEAR-PARITY."
            % (sorted(slots), sorted(_HUNT_ARMOUR)))

    for pet in _HUNT_PETS:
        _set_pet_equipment(db, pet, _loadout_spec(loadout))
        for slot in _GEAR_SLOTS:
            if slot not in slots:
                db.set_field(pet, 'chanceToEquip%s' % slot, 0.0)
        db._modified.add(pet)

    print("  [-3 pets] Endless Hunt soul pets (%d): gear re-mirrored from the DRESSED "
          "source through _set_pet_equipment - slots %s on, %s off. Will's summoned Hunt "
          "now wears what the fought one wears (PET-GEAR-PARITY, both directions); no "
          "Monster.tpl field was copied onto a Pet.tpl record."
          % (len(_HUNT_PETS), '/'.join(sorted(slots)),
             '/'.join(sorted(s for s in _GEAR_SLOTS if s not in slots)) or 'none'))


# ── the gate ────────────────────────────────────────────────────────────────
def _hand_metrics(db):
    """Measured roll shares for the Devourer's two hands, minimum over difficulties.

    Returns (armed, signature, shield, dead). `dead` names every hand/difficulty whose
    selectable distribution is EMPTY - the slot is switched on but no row can be picked.

    ROUND-3 FIX, and it was the ugly one: this used to seed all three shares at 100.0 and
    only ever LOWER them, so a hand with nothing selectable reported "armed 100.00%" - the
    exact number the ruling and the test guide hand Will as proof he is always armed. An
    empty distribution now zeroes the shares AND is named, so it fails E2c loudly instead of
    passing vacuously. A gate that reports 100% armed for a boss holding nothing is not a
    gate for "i dont think he has a weapon".
    """
    armed = signature = shield = 100.0
    dead = []
    for diff, tier in enumerate('NEL'):
        for slot in ('RightHand', 'LeftHand'):
            dist = _slot_dist(db, _DEVOURER, slot, diff)
            if not dist:
                dead.append('%s [%s]' % (slot, tier))
                continue
            if slot == 'RightHand':
                armed = min(armed, _pct_class(db, dist, _ONE_HAND_MELEE))
                signature = min(signature, _pct_items(dist, _VEINRENDER_ITEM))
            else:
                shield = min(shield, _pct_class(db, dist, _SLOT_CLASSES['LeftHand']))
    if dead:
        armed = signature = shield = 0.0
    return armed, signature, shield, dead


def _set_piece_shares(db):
    """{piece label: expected drops per 100 kills} for the three worn Crimson Verdict pieces.

    Summed over EVERY equip slot of the Devourer, not only the row this lane wires: the point
    of the arm is to notice a channel appearing or disappearing anywhere on the record, so a
    later lane that restores the rate (or dilutes it further) cannot leave the four published
    documents stale. `chanceToEquip<Slot>` is the slot's own gate and the row weights are a
    weighted pick WITHIN the slot, so the per-slot contribution is chance x share.

    The set's item records are per-difficulty (`svc_{n,e,l}_crimsonverdict`), so each
    difficulty is scored against ITS OWN tier's record and the reported value is the MINIMUM
    over the three - the same "worst difficulty wins" convention `_hand_metrics` uses.
    """
    out = {}
    for label, per_tier in sorted(_CRIMSON_ARMOUR.items()):
        worst = None
        for diff in range(3):
            want = {_norm(per_tier[diff])}
            acc = 0.0
            for slot in _SLOTS:
                chance = _f(_gv(db, _DEVOURER, 'chanceToEquip%s' % slot, 0))
                if chance <= 0:
                    continue
                chance = min(chance, 100.0) / 100.0
                for path, q in _slot_dist(db, _DEVOURER, slot, diff).items():
                    if _norm(path) in want:
                        acc += 100.0 * chance * q
            worst = acc if worst is None else min(worst, acc)
        out[label] = worst or 0.0
    return out


def _check(db):
    """The R-252 contract over the FINAL db. Returns a list of problem strings."""
    out = []
    _validate_allowlist(_MIXED_DROP_ROWS)

    # E1 + E2 + E4: per-champion slot-class integrity, on ALL THREE difficulty tables of
    # every row. The shipped bug was Normal+Legendary-only (bleed_affix_high_l's Nemesis
    # recurve is a Legendary-only bow), so a tier-N-only sweep is exactly the blind spot
    # that produced it.
    for rec in _CHAMPIONS:
        if not _has(db, rec):
            out.append("E1 champion record MISSING: %s" % rec)
            continue
        short = rec.rsplit('\\', 1)[-1]
        for slot in _SLOTS:
            if _f(_gv(db, rec, 'chanceToEquip%s' % slot, 0)) <= 0:
                continue
            allowed = _SLOT_CLASSES.get(slot)
            for idx, _w, tabs in _slot_rows(db, rec, slot):
                for tier, tab in zip('NEL', tabs):
                    classes = {c for c in _leaf_classes(db, tab) if c}
                    banned = _banned_of(classes)
                    if banned:
                        out.append("E1 %s %s item%d [%s] -> %s yields %s - a two-handed "
                                   "ranged weapon on a Toxeus champion (Will's 'using a "
                                   "bow which makes no sense')"
                                   % (short, slot, idx, tier, tab.rsplit('\\', 1)[-1],
                                      '/'.join(sorted(banned))))
                    if allowed is None:
                        continue
                    if (rec, slot, idx) in _MIXED_DROP_ROWS:
                        continue
                    wrong = _wrong_of(classes, allowed)
                    if wrong:
                        out.append("E2 %s %s item%d [%s] -> %s yields %s, which %s cannot "
                                   "wear (allowed: %s). Either fix the table or allowlist "
                                   "the row in _MIXED_DROP_ROWS with a reason."
                                   % (short, slot, idx, tier, tab.rsplit('\\', 1)[-1],
                                      '/'.join(sorted(wrong)), slot,
                                      '/'.join(sorted(allowed))))
        # E4 - the R-243 pin and a soul that resolves to a real ring.
        if not _close(_gv(db, rec, 'chanceToEquipFinger2'), 100.0):
            out.append("E4 %s chanceToEquipFinger2 = %r, must stay R-243's 100.0 pin"
                       % (short, _gv(db, rec, 'chanceToEquipFinger2')))
        souls = _gl(db, rec, 'lootFinger2Item1')
        if len(souls) != 3:
            out.append("E4 %s lootFinger2Item1 has %d entries, expected the 3-difficulty "
                       "soul array" % (short, len(souls)))
        for s in souls:
            real = _resolve(db, s)
            if real is None:
                out.append("E4 %s soul reference does NOT resolve: %s" % (short, s))
                continue
            if 'jewelry_ring' not in _norm(_gv(db, real, 'templateName', '')):
                out.append("E4 %s soul %s is templateName %r, not a Jewelry_Ring - the "
                           "engine cannot equip it into Finger2, so it never drops"
                           % (short, s.rsplit('\\', 1)[-1], _gv(db, real, 'templateName', '')))

    # E2b - the Devourer's hands, spelled out.
    if _has(db, _DEVOURER):
        # THE HAND SWITCHES THEMSELVES. E1/E2 above `continue` on any slot whose
        # chanceToEquip<Slot> is 0, so a hand switched OFF would be DELETED from the sweep
        # rather than failed by it - and "i dont think he has a weapon" is the literal text
        # of Will's report. These two lines are the only arms that can see that state.
        for hand, why in (('RightHand', "his weapon hand - Will's 'i dont think he has a "
                                        "weapon', filed against this boss's brother"),
                          ('LeftHand', 'his shield hand')):
            got = _gv(db, _DEVOURER, 'chanceToEquip%s' % hand)
            if not _close(got, 100.0):
                out.append("E2b Devourer chanceToEquip%s = %r, must be 100.0 - a hand "
                           "switched off holds NOTHING no matter how clean its loot rows "
                           "are, and every class arm skips a slot at chance 0 (%s)"
                           % (hand, got, why))
        if not _same(_gl(db, _DEVOURER, 'lootLeftHandItem1'), _SHIELD_COMMON):
            out.append("E2 Devourer lootLeftHandItem1 = %r, must be the shield array %r"
                       % (_gl(db, _DEVOURER, 'lootLeftHandItem1'), _SHIELD_COMMON))
        if not _same(_gl(db, _DEVOURER, 'lootRightHandItem1'), _VEINRENDER_TAB):
            out.append("E2 Devourer lootRightHandItem1 = %r, must be the guaranteed Vein "
                       "Render array" % (_gl(db, _DEVOURER, 'lootRightHandItem1'),))
        if not _same(_gl(db, _DEVOURER, 'lootLeftHandItem2'), _CRIMSON_SET):
            out.append("E2 Devourer lootLeftHandItem2 = %r, must be the Crimson Verdict set "
                       "table - it is the set's ONLY drop channel in the db, and it lives "
                       "in the OFF hand on purpose"
                       % (_gl(db, _DEVOURER, 'lootLeftHandItem2'),))
        dom = max(_slot_rows(db, _DEVOURER, 'RightHand') or [(0, 0, [])],
                  key=lambda r: r[1])
        if dom[0] != 1:
            out.append("E2 Devourer's dominant RightHand row is item%d, must be item1 "
                       "(the guaranteed Vein Render) so his own sword is the usual roll"
                       % dom[0])
        for tab in _VEINRENDER_TAB:
            classes = {str(c).lower() for c in _leaf_classes(db, tab) if c}
            if classes != {'weapon_sword'}:
                out.append("E2 %s yields %r, must be exactly one Weapon_Sword"
                           % (tab.rsplit('\\', 1)[-1], sorted(classes)))
        # E2c - the MEASURED arithmetic behind the player-facing claim.
        armed, signature, shield, dead = _hand_metrics(db)
        if dead:
            out.append("E2c Devourer hand(s) %s have an EMPTY selectable distribution - the "
                       "slot is switched on but every row weight is 0, so the engine equips "
                       "NOTHING there. This is not a 100%% share, it is a bare hand"
                       % ', '.join(dead))
        if armed + 1e-6 < _MIN_ARMED_HAND_PCT:
            out.append("E2c Devourer's weapon hand holds a one-handed melee weapon only "
                       "%.2f%% of spawns (floor %.2f%%) - the remaining %.2f%% roll a class "
                       "the hand cannot wear, i.e. Will sees an EMPTY hand ('i dont think "
                       "he has a weapon')" % (armed, _MIN_ARMED_HAND_PCT, 100.0 - armed))
        if signature + 1e-6 < _MIN_SIGNATURE_PCT:
            out.append("E2c Devourer wields his own Vein Render only %.2f%% of spawns "
                       "(floor %.2f%%) - the guaranteed row has been diluted"
                       % (signature, _MIN_SIGNATURE_PCT))
        if shield + 1e-6 < _MIN_SHIELD_PCT:
            out.append("E2c Devourer's off hand holds a shield only %.2f%% of spawns "
                       "(floor %.2f%%)" % (shield, _MIN_SHIELD_PCT))
        # E2d - the DISCLOSED set-drop rate. Two-sided: the published number must match the
        # bytes in BOTH directions, because it is the number four Will-visible documents say.
        lo = _CRIMSON_MEMBER_PCT - _CRIMSON_MEMBER_TOL
        hi = _CRIMSON_MEMBER_PCT + _CRIMSON_MEMBER_TOL
        for label, pct in sorted(_set_piece_shares(db).items()):
            if lo <= pct <= hi:
                continue
            out.append(
                "E2d Crimson Verdict %s drops on %.4f%% of Devourer kills, but "
                "_CRIMSON_MEMBER_PCT publishes %.4f%% (+/-%.2f). This table is the ONLY drop "
                "path for that piece in the whole db, so this IS the farm rate. %s If the "
                "change is intended, update _CRIMSON_MEMBER_PCT and the four documents that "
                "quote it IN THE SAME COMMIT (this module's docstring, "
                "tools/patches/__init__.py, docs/WILL_RULINGS.md R-252, "
                "docs/WILL_TEST_GUIDE.md) and re-state the delta for Will - see "
                "BL-R252-DEBT-7. A drop rate that moves without the docs moving is exactly "
                "how rounds 1-3 shipped a 6.1x nerf silently."
                % (label, pct, _CRIMSON_MEMBER_PCT, _CRIMSON_MEMBER_TOL,
                   'The channel has been DILUTED or DELETED.' if pct < lo
                   else 'The channel has been WIDENED.'))

    # E1b - no bow row survives anywhere in the bleed tables.
    for tab in _BLEED:
        if not _has(db, tab):
            out.append("E1 bleed table MISSING: %s" % tab)
            continue
        banned = _banned_of({c for c in _leaf_classes(db, tab) if c})
        if banned:
            out.append("E1 %s still yields %s - the de-bow did not hold"
                       % (tab.rsplit('\\', 1)[-1], '/'.join(sorted(banned))))

    # E3 - the Hunt wears armour and keeps his spear + rite.
    for rec in _HUNTS:
        if not _has(db, rec):
            out.append("E3 Hunt record MISSING: %s" % rec)
            continue
        short = rec.rsplit('\\', 1)[-1]
        for slot, (common, unique) in sorted(_HUNT_ARMOUR.items()):
            if not _close(_gv(db, rec, 'chanceToEquip%s' % slot), 100.0):
                out.append("E3 %s chanceToEquip%s = %r, must be 100.0 - Will: 'not wearing "
                           "any equipment'" % (short, slot, _gv(db, rec, 'chanceToEquip%s' % slot)))
            if not _same(_gl(db, rec, 'loot%sItem1' % slot), common):
                out.append("E3 %s loot%sItem1 = %r, must be his tier-02 %s array"
                           % (short, slot, _gl(db, rec, 'loot%sItem1' % slot), slot))
            if _i(_gv(db, rec, 'chanceToEquip%sItem1' % slot)) != _W_COMMON:
                out.append("E3 %s chanceToEquip%sItem1 = %r, must be the family weight %d"
                           % (short, slot, _gv(db, rec, 'chanceToEquip%sItem1' % slot), _W_COMMON))
        if not _same(_gl(db, rec, 'lootRightHandItem1'), _RUNBREAKER):
            out.append("E3 %s lost the Runbreaker spear: lootRightHandItem1 = %r"
                       % (short, _gl(db, rec, 'lootRightHandItem1')))
        if not _close(_gv(db, rec, 'chanceToEquipRightHand'), 100.0):
            out.append("E3 %s chanceToEquipRightHand = %r, must stay 100.0 (R-247.6b)"
                       % (short, _gv(db, rec, 'chanceToEquipRightHand')))
        if not _same(_gl(db, rec, 'lootMisc4Item1'), _RITE):
            out.append("E3 %s lootMisc4Item1 = %r, must stay the EoAT rite table (R-247.6a)"
                       % (short, _gl(db, rec, 'lootMisc4Item1')))
        if not _close(_gv(db, rec, 'chanceToEquipMisc4'), 100.0):
            out.append("E3 %s chanceToEquipMisc4 = %r, must stay 100.0 (R-247.6a)"
                       % (short, _gv(db, rec, 'chanceToEquipMisc4')))
        for slot, chance in sorted(_HUNT_MISC_CHANCES.items()):
            if not _close(_gv(db, rec, 'chanceToEquip%s' % slot), chance):
                out.append("E3 %s chanceToEquip%s = %r, must be the family value %s"
                           % (short, slot, _gv(db, rec, 'chanceToEquip%s' % slot), chance))
    return out


def _check_modwide(db):
    """E5 - mod-wide: a 100% Finger2 pin that cannot deliver a ring IS the -10 bug.

    ROUND-3 WIDENING. The arm used to filter to carriers whose `lootFinger2Item1` already
    contained the substring "soul", which meant the headline case in its own docstring - a
    pin pointing at NOTHING - could never be reached. It now covers EVERY record pinned at
    `chanceToEquipFinger2` = 100:
      * no Finger2 loot at all                                 -> FAIL
      * a reference that does not resolve                      -> FAIL
      * a chain whose leaves are not Jewelry_Ring              -> FAIL
    The seven offenders that already exist in b888f022 sit outside this lane's surface, so
    each is named individually in `_E5_PREEXISTING` with its reason and registered as
    BL-R252-DEBT-5. Naming them one by one (rather than narrowing the arm) keeps it LIVE:
    an eighth offender, or a change to one of the seven, still reds the build.

    Returns (problems, checked, waived) where `checked` counts the carriers actually held to
    the contract and `waived` the named pre-existing exceptions that were skipped.
    """
    out = []
    checked = 0
    waived = 0
    for name in db.record_names():
        if not _close(_gv(db, name, 'chanceToEquipFinger2'), 100.0):
            continue
        if _norm(name) in _E5_PREEXISTING_LC:
            waived += 1
            continue
        short = name.rsplit('\\', 1)[-1]
        souls = [s for s in _gl(db, name, 'lootFinger2Item1') if s.lower().endswith('.dbr')]
        checked += 1
        if not souls:
            out.append("E5 %s is pinned at chanceToEquipFinger2 = 100 but has NO "
                       "lootFinger2Item1 at all - a 100%% pin pointing at nothing is the "
                       "'did not drop his soul' bug in its purest form" % short)
            continue
        for s in souls:
            real = _resolve(db, s)
            if real is None:
                out.append("E5 %s is pinned at a 100%% Finger2 drop but %s does NOT resolve"
                           % (short, s))
                continue
            classes = {c for c in _leaf_classes(db, real) if c}
            if not classes:
                continue                       # every leaf is a base-game record: unknowable
            wrong = _wrong_of(classes, _SLOT_CLASSES['Finger2'])
            if wrong:
                out.append("E5 %s is pinned at 100%% but its Finger2 chain %s yields %s, "
                           "which the ring slot cannot hold - the engine cannot equip it, "
                           "so it never drops"
                           % (short, s.rsplit('\\', 1)[-1], '/'.join(sorted(wrong))))
    return out, checked, waived


def verify(db, tags):
    problems = _check(db)
    modwide, checked, waived = _check_modwide(db)
    problems += modwide
    if problems:
        for p in problems[:25]:
            print("  R-252 OFFENDER: %s" % p)
        raise SystemExit("[toxeus_boss_equipment] verify FAILED: %d problem(s)"
                         % len(problems))
    armed, signature, shield, dead = _hand_metrics(db)
    if dead:                       # unreachable: _check fails on `dead` first. Belt+braces.
        raise SystemExit("[toxeus_boss_equipment] verify FAILED: dead hand(s) %s"
                         % ', '.join(dead))
    print("  [toxeus_boss_equipment] verify OK: no Toxeus champion can hold a bow or staff "
          "in any slot on any difficulty; the Devourer holds both hands at 100%% and his "
          "weapon hand is a one-handed melee weapon %.2f%% of spawns (his own Vein Render "
          "%.2f%%) with a shield in the off hand %.2f%%; both Endless Hunt records wear "
          "torso/legs/arms at 100%% and keep the Runbreaker spear + the EoAT rite; all 4 "
          "champions hold R-243's 100%% soul pin on a soul that resolves to a real ring; "
          "%d mod-wide 100%%-pinned Finger2 carrier(s) all deliver a ring (%d pre-existing "
          "offender(s) waived by name, BL-R252-DEBT-5). BL-W0814-10 remains OPEN pending "
          "Will's next kill (BL-R252-DEBT-1)."
          % (armed, signature, shield, checked, waived))
    print("  [toxeus_boss_equipment] DISCLOSED BALANCE DELTA, re-measured this build: each "
          "worn Crimson Verdict piece drops on %s of Devourer kills, against 21.0084%% in "
          "the shipped b888f022 - a 6.1x slowdown on the set's ONLY drop path, published "
          "and pinned by E2d, awaiting Will's ratification as BL-R252-DEBT-7."
          % ', '.join('%.4f%% (%s)' % (v, k)
                      for k, v in sorted(_set_piece_shares(db).items())))


# ── planted negatives (stub db) ─────────────────────────────────────────────
def _negtest():
    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()
            self._record_types = {}

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_fields(self, n):
            return self.d.get(n)

        def get_field_value(self, n, f):
            rec = self.d.get(n)
            return None if rec is None else rec.get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v

    RING = {'templateName': 'database\\Templates\\Jewelry_Ring.tpl'}

    def item(tpl):
        return {'templateName': 'Database\\Templates\\%s.tpl' % tpl}

    def table(members):
        r = {'templateName': 'Database\\Templates\\LootItemTable_FixedWeight.tpl'}
        for i, m in enumerate(members, start=1):
            r['lootName%d' % i] = m
            r['lootWeight%d' % i] = 100
        return r

    def healthy():
        db = _Stub()
        sword, shieldi, torso, legs, arms, ring, amulet = (
            'i\\sword.dbr', 'i\\shield.dbr', 'i\\torso.dbr', 'i\\legs.dbr',
            'i\\arms.dbr', 'i\\ring.dbr', 'i\\amulet.dbr')
        db.d[sword] = item('Weapon_Sword')
        db.d[shieldi] = item('WeaponArmor_Shield')
        db.d[torso] = item('Armor_UpperBody')
        db.d[legs] = item('Armor_LowerBody')
        db.d[arms] = item('Armor_Forearm')
        db.d[ring] = item('Jewelry_Ring')
        db.d[amulet] = item('Jewelry_Amulet')
        db.d['i\\spear.dbr'] = item('Weapon_Spear')
        db.d['i\\axe.dbr'] = item('Weapon_Axe')
        db.d['i\\helm.dbr'] = item('Armor_Head')
        db.d['i\\formula.dbr'] = item('ItemArtifactFormula')
        # the real shape: each difficulty's veinrender table holds THAT tier's sword, and
        # the crimson set is 1 Vein Render + 3 armour at equal weight
        for i, t in enumerate(_VEINRENDER_TAB):
            db.d[_VEINRENDER_ITEM[i]] = item('Weapon_Sword')
            db.d[t] = table([_VEINRENDER_ITEM[i]])
        # the set table's real shape: 1 Vein Render + the THREE REAL worn-piece records at
        # equal weight. They must be the real paths, because E2d measures those paths by name.
        _armour_class = {'helm (Armor_Head)': 'Armor_Head',
                         'cuirass (Armor_UpperBody)': 'Armor_UpperBody',
                         'armband (Armor_Forearm)': 'Armor_Forearm'}
        for label, per_tier in _CRIMSON_ARMOUR.items():
            for path in per_tier:
                db.d[path] = item(_armour_class[label])
        for i, t in enumerate(_CRIMSON_SET):
            members = [_VEINRENDER_ITEM[i]]
            members += [per_tier[i] for _l, per_tier in sorted(_CRIMSON_ARMOUR.items())]
            db.d[t] = table(members)
        for t in _BLEED:
            db.d[t] = table(['i\\axe.dbr', 'i\\axe.dbr'])
        for t in _SHIELD_COMMON + _SHIELD_UNIQUE:
            db.d[t] = table([shieldi])
        for t in _SWORD_UNIQUE:
            db.d[t] = table([sword])
        for t in _RUNBREAKER:
            db.d[t] = table(['i\\spear.dbr'])
        for t in set(_RITE):
            db.d[t] = table(['i\\formula.dbr'])
        for slot, (common, unique) in _HUNT_ARMOUR.items():
            leaf = {'Torso': torso, 'LowerBody': legs, 'Forearm': arms}[slot]
            for t in common + unique:
                db.d[t] = table([leaf])
        souls = {}
        for rec, stem in ((_DEVOURER, 'blood_toxeus'), (_ENSLAVER, 'enslaver'),
                          (_HUNT, 'toxeus_hunt'), (_HUNT_L, 'toxeus_hunt')):
            souls[rec] = ['records\\soul\\%s_soul_%s.dbr' % (stem, t) for t in 'nel']
            for s in souls[rec]:
                db.d[s] = dict(RING)
        ringtab = 'records\\item\\loottables\\finger\\commondynamic\\finger.dbr'
        amutab = 'records\\item\\loottables\\amulet\\commondynamic\\amulet.dbr'
        db.d[ringtab] = table([ring])
        db.d[amutab] = table([amulet])

        def champ(rec):
            r = {'chanceToEquipFinger2': 100.0, 'lootFinger2Item1': souls[rec],
                 'chanceToEquipFinger2Item1': 100,
                 'chanceToEquipFinger1': 100.0, 'lootFinger1Item1': [ringtab] * 3,
                 'chanceToEquipFinger1Item1': 5000,
                 'chanceToEquipMisc3': 50.0, 'lootMisc3Item1': [amutab] * 3,
                 'chanceToEquipMisc3Item1': 5000}
            db.d[rec] = r
            return r

        dev = champ(_DEVOURER)
        dev.update({'chanceToEquipLeftHand': 100.0,
                    'lootLeftHandItem1': list(_SHIELD_COMMON),
                    'chanceToEquipLeftHandItem1': _W_GUARANTEED,
                    'lootLeftHandItem2': list(_CRIMSON_SET),
                    'chanceToEquipLeftHandItem2': _W_UNIQUE,
                    'lootLeftHandItem5': list(_SHIELD_UNIQUE),
                    'chanceToEquipLeftHandItem5': _W_UNIQUE,
                    'chanceToEquipRightHand': 100.0,
                    'lootRightHandItem1': list(_VEINRENDER_TAB),
                    'chanceToEquipRightHandItem1': _W_GUARANTEED,
                    'lootRightHandItem2': list(_BLEED),
                    'chanceToEquipRightHandItem2': _W_UNIQUE,
                    'lootRightHandItem5': list(_SWORD_UNIQUE),
                    'chanceToEquipRightHandItem5': _W_UNIQUE})
        ens = champ(_ENSLAVER)
        ens.update({'chanceToEquipLeftHand': 100.0, 'lootLeftHandItem1': list(_SHIELD_COMMON),
                    'chanceToEquipLeftHandItem1': 5000,
                    'chanceToEquipRightHand': 100.0,
                    'lootRightHandItem1': list(_SWORD_UNIQUE),
                    'chanceToEquipRightHandItem1': 5000})
        for rec in _HUNTS:
            h = champ(rec)
            h.update({'chanceToEquipRightHand': 100.0,
                      'lootRightHandItem1': list(_RUNBREAKER), 'chanceToEquipRightHandItem1': 100,
                      'chanceToEquipMisc4': 100.0, 'lootMisc4Item1': list(_RITE),
                      'chanceToEquipMisc4Item1': 100,
                      'chanceToEquipMisc1': 100.0, 'chanceToEquipMisc2': 18.0})
            for slot, (common, unique) in _HUNT_ARMOUR.items():
                h['chanceToEquip%s' % slot] = 100.0
                h['loot%sItem1' % slot] = list(common)
                h['loot%sItem5' % slot] = list(unique)
                h['chanceToEquip%sItem1' % slot] = _W_COMMON
                h['chanceToEquip%sItem5' % slot] = _W_UNIQUE
        return db

    def full(db):
        return _check(db) + _check_modwide(db)[0]

    base = healthy()
    if full(base):
        print("negtest BROKEN: the healthy stub fails its own contract:")
        for p in full(base):
            print("   ", p)
        return 1
    a, s, sh, dead = _hand_metrics(base)
    if dead:
        print("negtest BROKEN: the healthy stub has dead hand(s): %s" % ', '.join(dead))
        return 1
    print("  negtest baseline shares: armed=%.2f%% signature=%.2f%% shield=%.2f%%"
          % (a, s, sh))

    def plant_bow(d):
        d.d[_BLEED[0]]['lootName3'] = 'i\\bow.dbr'
        d.d[_BLEED[0]]['lootWeight3'] = 100
        d.d['i\\bow.dbr'] = item('Weapon_Bow')

    def plant_lefthand_bow(d):
        d.d['i\\bow.dbr'] = item('Weapon_Bow')
        d.d['t\\bowtab.dbr'] = table(['i\\bow.dbr'])
        d.d[_DEVOURER]['lootLeftHandItem1'] = ['t\\bowtab.dbr'] * 3

    def plant_mixedcase_bow(d):
        """The SAME violation, reached through a reference that differs only in CASE.

        Round 2 shipped blind to this: `has_record` is exact-case, the chain came back as an
        unresolved leaf, and every class arm ignores unresolved leaves by design. The table
        is stored lowercase (as the arz stores every record name) and referenced mixed-case
        (as the arz references them) - exactly the shape of the 2,436 such references in the
        shipped mod arz.
        """
        d.d['i\\bow.dbr'] = item('Weapon_Bow')
        d.d['t\\vet_bowtab.dbr'] = table(['i\\bow.dbr'])
        d.d[_DEVOURER]['lootLeftHandItem5'] = ['T\\Vet_BowTab.dbr'] * 3

    def plant_mixedcase_wrongclass(d):
        """A class violation on a row with NO literal assert and NO arithmetic backstop.

        The Hunt's Forearm row is class-governed but is not one of the shares E2c measures,
        so if the class arm cannot see through a mixed-case reference nothing else catches
        it. This is the latent half of the same defect.
        """
        d.d['t\\vet_wrongarm.dbr'] = table(['i\\sword.dbr'])
        d.d[_HUNT_L]['lootForearmItem5'] = ['T\\Vet_WrongArm.dbr'] * 3
        d.d[_HUNT_L]['chanceToEquipForearmItem5'] = _W_UNIQUE

    plants = [
        # the hands switched OFF - the defect class E1/E2 structurally cannot see, because
        # they `continue` on any slot at chance 0 (round-2 gate missed all three)
        ("the Devourer's WEAPON hand switched off entirely (he holds nothing)",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipRightHand', 0.0)),
        ("the Devourer's SHIELD hand switched off entirely",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipLeftHand', 0.0)),
        ("the Devourer's off-hand rows all zeroed (slot on, nothing selectable)",
         lambda d: [d.d[_DEVOURER].__setitem__('chanceToEquipLeftHandItem%d' % i, 0)
                    for i in range(1, 7)]),
        ("the Devourer's weapon rows all zeroed (slot on, nothing selectable)",
         lambda d: [d.d[_DEVOURER].__setitem__('chanceToEquipRightHandItem%d' % i, 0)
                    for i in range(1, 7)]),
        # case-blindness
        ("a bow reached through a MIXED-CASE table reference", plant_mixedcase_bow),
        ("a wrong-class Hunt row reached through a MIXED-CASE table reference",
         plant_mixedcase_wrongclass),
        # E5 widened: the docstring's own headline case
        ("mod-wide: a 100%-pinned carrier with NO Finger2 loot at all (pin -> nothing)",
         lambda d: d.d.__setitem__('records\\creature\\empty_pin_99.dbr',
                                   {'chanceToEquipFinger2': 100.0})),
        ("mod-wide: a 100%-pinned carrier whose Finger2 points at a non-ring class",
         lambda d: (d.d.__setitem__('t\\wandtab.dbr', table(['i\\axe.dbr'])),
                    d.d.__setitem__('records\\creature\\wand_pin_99.dbr',
                                    {'chanceToEquipFinger2': 100.0,
                                     'lootFinger2Item1': ['t\\wandtab.dbr'] * 3}))),
        ("the bow row survives de-bowing", plant_bow),
        ("a bow pool back in the Devourer's off-hand", plant_lefthand_bow),
        ("staff in the Devourer's off-hand", lambda d: (
            d.d.__setitem__('i\\staff.dbr', item('Weapon_Staff')),
            d.d.__setitem__('t\\stafftab.dbr', table(['i\\staff.dbr'])),
            d.d[_DEVOURER].__setitem__('lootLeftHandItem1', ['t\\stafftab.dbr'] * 3))),
        ("armour back in the Devourer's weapon hand as the dominant row",
         lambda d: d.d[_DEVOURER].__setitem__('lootRightHandItem1', list(_CRIMSON_SET))),
        ("the dominant weapon row demoted below another row",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipRightHandItem2', 5000)),
        # E2c - the arithmetic behind the player-facing sentence
        ("the 3/4-ARMOUR set table moved back into the weapon hand (empty-hand spawns)",
         lambda d: (d.d[_DEVOURER].__setitem__('lootRightHandItem3', list(_CRIMSON_SET)),
                    d.d[_DEVOURER].__setitem__('chanceToEquipRightHandItem3', _W_UNIQUE))),
        ("the guaranteed Vein Render row diluted below its floor without losing dominance",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipRightHandItem1', 30)),
        ("the off-hand shield share collapsed by a fat mixed row",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipLeftHandItem2', 5000)),
        ("the set table's ONLY drop channel deleted (orphaned content)",
         lambda d: d.d[_DEVOURER].__setitem__('lootLeftHandItem2', list(_SHIELD_UNIQUE))),
        # E2d - the DISCLOSED set-drop rate, both directions
        ("the set's drop channel quietly THINNED below the published farm rate",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipLeftHandItem2', 5)),
        ("the set's drop rate quietly RESTORED on an ungoverned slot, docs left stale",
         lambda d: d.d[_DEVOURER].update({'chanceToEquipMisc1': 100.0,
                                          'lootMisc1Item1': list(_CRIMSON_SET),
                                          'chanceToEquipMisc1Item1': 100})),
        # tier asymmetry - the exact blind spot that produced this bug
        ("an EPIC-ONLY class violation on a Hunt armour row",
         lambda d: d.d.__setitem__(_HUNT_ARMOUR['Torso'][0][1], table(['i\\sword.dbr']))),
        ("a LEGENDARY-ONLY bow in the Devourer's weapon hand", lambda d: (
            d.d.__setitem__('i\\bow.dbr', item('Weapon_Bow')),
            d.d.__setitem__(_BLEED[2], table(['i\\bow.dbr'])))),
        ("the Vein Render table stops being a sword", lambda d: (
            d.d.__setitem__('i\\notasword.dbr', item('Armor_Head')),
            d.d.__setitem__(_VEINRENDER_TAB[0], table(['i\\notasword.dbr'])))),
        ("Hunt torso switched back off",
         lambda d: d.d[_HUNT].__setitem__('chanceToEquipTorso', 0.0)),
        ("Hunt legs switched back off",
         lambda d: d.d[_HUNT_L].__setitem__('chanceToEquipLowerBody', 0.0)),
        ("Hunt forearm table repointed at the wrong class", lambda d: (
            d.d.__setitem__('t\\wrong.dbr', table(['i\\sword.dbr'])),
            d.d[_HUNT].__setitem__('lootForearmItem1', ['t\\wrong.dbr'] * 3))),
        ("Hunt armour weight drift",
         lambda d: d.d[_HUNT].__setitem__('chanceToEquipTorsoItem1', 1)),
        ("Hunt lost the Runbreaker spear",
         lambda d: d.d[_HUNT].__setitem__('lootRightHandItem1', list(_VEINRENDER_TAB))),
        ("Hunt spear chance dropped",
         lambda d: d.d[_HUNT_L].__setitem__('chanceToEquipRightHand', 35.0)),
        ("Hunt EoAT rite unwired",
         lambda d: d.d[_HUNT].__setitem__('chanceToEquipMisc4', 0.0)),
        ("Hunt family misc chance drift",
         lambda d: d.d[_HUNT].__setitem__('chanceToEquipMisc2', 0.0)),
        ("R-243 soul pin moved off 100",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipFinger2', 20.0)),
        ("the Devourer's soul reference stops resolving",
         lambda d: d.d[_DEVOURER].__setitem__(
             'lootFinger2Item1', ['records\\soul\\gone_soul_%s.dbr' % t for t in 'nel'])),
        ("a soul item stops being a ring", lambda d: d.d[
            d.d[_ENSLAVER]['lootFinger2Item1'][0]].__setitem__(
                'templateName', 'Database\\Templates\\OneShot_PotionHealth.tpl')),
        ("mod-wide: another 100%-pinned carrier points at a dead soul", lambda d: (
            d.d.__setitem__('records\\creature\\other_99.dbr', {
                'chanceToEquipFinger2': 100.0,
                'lootFinger2Item1': ['records\\soul\\dead_soul_%s.dbr' % t for t in 'nel']}))),
        ("the Devourer's ring slot repointed at a non-ring", lambda d: (
            d.d.__setitem__('t\\ringwrong.dbr', table(['i\\amulet.dbr'])),
            d.d[_DEVOURER].__setitem__('lootFinger1Item1', ['t\\ringwrong.dbr'] * 3))),
    ]
    bad = 0
    for label, plant in plants:
        db = healthy()
        plant(db)
        if full(db):
            print("  negtest OK  (caught): %s" % label)
        else:
            print("  negtest FAIL (missed): %s" % label)
            bad += 1

    # the two import-time guards are negtested by calling them directly
    try:
        _validate_allowlist({(_DEVOURER, 'Misc1', 1): 'a slot the gate never class-checks'})
        print("  negtest FAIL (missed): an allowlist entry naming an ungoverned slot")
        bad += 1
    except AssertionError:
        print("  negtest OK  (caught): an allowlist entry naming an ungoverned slot")

    global _BANNED_CLASSES
    _saved = _BANNED_CLASSES
    _BANNED_CLASSES = set(_saved) | {'Weapon_Crossbow'}
    try:
        _validate_class_sets()
        print("  negtest FAIL (missed): a NON-lowercase entry in a case-folded class set")
        bad += 1
    except AssertionError:
        print("  negtest OK  (caught): a NON-lowercase entry in a case-folded class set")
    finally:
        _BANNED_CLASSES = _saved

    # ARM-SPECIFIC PROOF for E2d. The plant list above only asserts that SOMETHING went red,
    # which is not enough for an arm whose whole job is to notice a number moving: a plant
    # that happens to trip E2c would score as "caught" while E2d slept. These assert that the
    # E2d text itself appears, in BOTH directions, and that its measurement is right.
    for label, plant, direction in (
            ("E2d specifically fires when the channel is THINNED",
             lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipLeftHandItem2', 5), 'DILUTED'),
            ("E2d specifically fires when the channel is WIDENED on an ungoverned slot",
             lambda d: d.d[_DEVOURER].update({'chanceToEquipMisc1': 100.0,
                                              'lootMisc1Item1': list(_CRIMSON_SET),
                                              'chanceToEquipMisc1Item1': 100}), 'WIDENED')):
        db = healthy()
        plant(db)
        hits = [p for p in full(db) if p.startswith('E2d')]
        if len(hits) == 3 and direction in hits[0]:
            print("  negtest OK  (caught): %s (all 3 worn pieces named)" % label)
        else:
            print("  negtest FAIL (missed): %s -> %d E2d problem(s): %s"
                  % (label, len(hits), hits[:1]))
            bad += 1

    # ... and that the healthy baseline measures the number the docs publish. A gate whose
    # published constant does not match its own clean state is a gate that will be edited
    # into silence the first time it fires.
    shares = _set_piece_shares(healthy())
    off = sorted(k for k, v in shares.items() if abs(v - _CRIMSON_MEMBER_PCT) > 1e-3)
    if off:
        print("  negtest FAIL: _CRIMSON_MEMBER_PCT %.4f does not match the clean stub %r"
              % (_CRIMSON_MEMBER_PCT, {k: round(v, 4) for k, v in shares.items()}))
        bad += 1
    else:
        print("  negtest OK  (measurement): all 3 worn set pieces measure %.4f%% on the "
              "clean stub, matching the published _CRIMSON_MEMBER_PCT" % _CRIMSON_MEMBER_PCT)

    # POSITIVE CONTROLS - the other half of a case-folded comparison. Round 2 listed
    # 'weapon_rangedonehand' and not 'Weapon_RangedOneHand' (10 records in the mod arz), and
    # omitted the lowercase stems the base game really uses (weapon_axe 50 records,
    # weapon_mace 42, weapon_sword 6, weapon_spear 1, armor_head 2, armor_upperbody 1), so a
    # legitimate item spelled the other way would have RED the build. These prove it cannot.
    for label, plant in (
            ("a legitimate LOWERCASE weapon stem in the weapon hand",
             lambda d: d.d.__setitem__('i\\axe.dbr', item('weapon_axe'))),
            ("a legitimate MIXED-CASE weapon stem in the weapon hand",
             lambda d: d.d.__setitem__('i\\axe.dbr', item('Weapon_RangedOneHand'))),
            ("a legitimate LOWERCASE armour stem on a Hunt armour row",
             lambda d: d.d.__setitem__('i\\torso.dbr', item('armor_upperbody'))),
            ("a Devourer loot table referenced in MIXED CASE but otherwise clean",
             lambda d: (d.d.__setitem__('t\\vet_okshield.dbr', table(['i\\shield.dbr'])),
                        d.d[_DEVOURER].__setitem__('lootLeftHandItem5',
                                                   ['T\\Vet_OkShield.dbr'] * 3)))):
        db = healthy()
        plant(db)
        found = full(db)
        if found:
            print("  negtest FAIL (false positive): %s -> %s" % (label, found[0]))
            bad += 1
        else:
            print("  negtest OK  (no false positive): %s" % label)

    # positive control: an untouched healthy stub must still pass at the end
    if full(healthy()):
        print("  negtest FAIL: positive control went red")
        bad += 1
    else:
        print("  negtest OK  (positive control stays green)")
    # plants + 2 import-time guards + 2 E2d arm-specific proofs + 1 E2d measurement check
    # + 4 positive controls + 1 untouched positive control
    total = len(plants) + 2 + 3 + 4 + 1
    print("negtest: %d/%d checks clean" % (total - bad, total))
    return 1 if bad else 0


if __name__ == '__main__':
    if '--negtest' in sys.argv:
        sys.exit(_negtest())
    print(__doc__)
