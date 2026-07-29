"""weapon_gate_truth - B100 WEAPON/HAND GATE HONESTY (Blade Mastery + Parry).

WILL'S QUESTION (2026-07-29, verbatim): "does the occult skill blade mastery
chance to dodge attacks bonus apply if you are using any weapon or only if you
are using a sword dagger or axe as the skill description says?"

GROUND TRUTH (engine-level, not inferred from field names). Evidence chain:

1. THE RECORD. `records\\skills\\stealth\\drx_dual_blade.dbr`. Read at
   investigation time out of the then-current built arz md5
   1c27d5fa650b5c076696db4ad379672f, and re-confirmed field-for-field (ZERO
   diffs) in this lane's own build md5 1e0990d7f934afb90151aa4672ddc049. NOTE
   the main checkout's `work/.../SoulvizierClassic.arz` moved under this lane
   mid-session (a parallel lane rebuilt it: 1c27d5fa -> 967b1f97, 51085 ->
   51124 records); both of those and this lane's build agree on every field of
   this record, so the reading does not depend on which one you open. It is a
   single `Skill_Passive` (template `Database\\Templates\\Skill_Passive.tpl`) carrying
   ALL FOUR bonuses itself, with no attached/child records:
       characterDodgePercent           5,7,9,10,12,14,16,18,19,21,23,25
       characterDefensiveAbility      11,17,23,29,35,41,47,60,66,72,80,90
       characterAttackSpeedModifier    5,7,9,10,12,14,16,18,19,21,23,25
       characterOffensiveAbilityModifier 5,7,9,10,12,14,16,18,19,21,23,25
   Gating fields: Sword=1, Axe=1, dualWieldOnly=1 (every other weapon flag 0,
   meleeOnly=0). skillMaxLevel=8, skillUltimateLevel=12.
   Because availability in this engine is a property of the SKILL, not of the
   individual modifier fields, the four bonuses share ONE gate: they are all on
   or all off together. Dodge is not special-cased.

2. THE TEMPLATE. `Toolset/Templates.arc` (md5 a9418cb0c7bffedb08245fa2559d31d5),
   `templates/templatebase/skill_base.tpl`, group "Qualifying Weapons":
   Sword/Axe/Bow/Spear/Mace/Staff/Magical/Shield/RangedOneHand/dualWieldOnly/
   meleeOnly. "Sword" carries the only description in the group: "Set to -1- to
   require type". dualWieldOnly and meleeOnly ship with EMPTY descriptions, so
   their meaning cannot honestly be read off the template - hence step 3.

3. THE ENGINE (Game.dll, md5 checked at read time; 32-bit, ImageBase 0x10000000;
   the DLL ships a full decorated export table, so these are the engine's OWN
   names, not guesses):
     - The record loader at 0x10258990..0x10258bb0 parses the group into a
       SkillProfile: each qualifying weapon name push_backs a Weapon_Type into
       the vector at profile+0xC8, then `dualWieldOnly` -> profile+0xD4 and
       `meleeOnly` -> profile+0xD5. The enum falls out of that same code:
       Axe=2, Sword=3, Mace=4, Spear=5, Bow=6, Staff=7, Magical=8, Shield=9,
       RangedOneHand=10.
     - `?GetQualifyingWeapons@SkillProfile@GAME@@...` @0x1025A8C0 = lea +0xC8,
       `?GetQualifyingDualWeapons@...` @0x1025A8D0 = byte +0xD4,
       `?GetQualifyingMeleeOnlyWeapons@...` @0x1025A8E0 = byte +0xD5.
     - `?IsQualifyingWeapons@Skill@GAME@@` @0x1023F510 takes TWO Weapon_Types
       and the list, and is an OR over both hands: empty list -> always true;
       otherwise true iff (hand1 in list) OR (hand2 in list).
     - `?QualifyingWeapon@Skill@GAME@@` @0x1023F570 calls
       `SkillManager::GetWeaponTypes(&t1,&t2)` (@0x10251000, the two equipped
       weapon types) and feeds both into IsQualifyingWeapons.
     - `?QualifyingHandState@Skill@GAME@@` @0x1023F410: if dualWieldOnly, the
       skill qualifies ONLY when `EquipManager::GetHandState()` returns 2 or 7.
     - `?GetHandState@EquipManager@GAME@@` @0x101792A0 branches on
       `GetWeaponIdLeft()` (@0x101789B0) FIRST: a weapon in the LEFT (off) hand
       of type Axe/Sword/Mace -> state 2; RangedOneHand -> state 7. With no
       off-hand weapon (or a shield) it falls through to `GetWeaponIdRight()`
       (@0x10178A00) and returns 1 (one-handed melee), 4 (spear), 5 (staff),
       6 (one thrown) or 0 - none of which are 2 or 7.
     - `?SetAvailability@Skill@GAME@@` @0x10245BC0 stores !QualifyingWeapon()
       at skill+0x93 and !QualifyingHandState() at skill+0x94, and at
       0x10245C9A returns FALSE with unavailable-reason 4 if EITHER is set.
       Reason 4 is the "Skill Requires Equipment" (tagSkillUnusableConfiguration)
       state.
     - `Skill_Passive` does NOT override SetAvailability: vtable
       `??_7Skill_Passive@GAME@@6BSkill@1@@` (0x1037C2B0) slot 54 == 0x10245BC0,
       byte-identical to `??_7Skill@GAME@@6B@` (0x1036C1F0) slot 54. So a
       passive's character modifiers ARE governed by both gates.
     - Bonus finding, and the reason the old tooltip's first sentence is true:
       `SkillManager::Update` @0x10254E93 ORs profile+0xD4 across every skill
       whose `GetCurrentLevel()` != 0 and calls
       `Character::AllowDualWieldWeapons(accum)` (@0x100DD990). Learning this
       skill therefore genuinely GRANTS the ability to wield two weapons.

4. PRECEDENT (same shape, in shipped data, so the reading is not a lone
   interpretation):
     - Skill_Passive + qualifying weapons: base-game `records\\skills\\warfare\\
       weapontraining.dbr` (Weapon Training, Sword/Axe/Mace/RangedOneHand,
       attack speed + OA) and `records\\skills\\hunting\\woodlore.dbr` (Wood
       Lore, Bow/Spear/RangedOneHand, attack speed + DA). Their shipped
       tooltips name the weapons in prose ("Years of training with the sword,
       axe, and club...", "...hunt with bow, spear or thrown objects...").
     - dualWieldOnly=1: exactly 6 base-game records, all weapon-pool attacks
       (warfare dualweapontraining / crosscut / jumpslash / tumult, the /old/
       twin, and xpack2 runemaster `hailofaxes.dbr`). hailofaxes is the only one
       with its own dedicated description, and it states the gate verbatim:
       `x2tagSkillRunesDescription010` = "...{^n}{^y}Allows and requires dual
       wielding." That is the game's OWN phrasing for this exact field.
     - Weapon-class clause house style: `tagSkillDescription015` (War Wind -
       Lacerate, Sword/Axe/Spear) = "...  Requires at least one sword, axe, or
       spear." The mod already uses the same shape ("{^n}{^y}Melee weapon or
       Staff required." on tagSlam_DESC).

5. "DAGGER" IS NOT A WEAPON CLASS. TQAE has no dagger class: the only Weapon*
   Class values in the shipped arz are WeaponMelee_{Sword,Axe,Mace},
   WeaponHunting_{Bow,Spear,RangedOneHand}, WeaponMagical_Staff,
   WeaponArmor_Shield. Every dagger/knife item in this mod is Sword-class -
   including the mod's own `records\\drxitem\\supra\\wep_dagger.dbr`
   (Class=WeaponMelee_Sword, itemNameTag=tagwep_dagger). So the tooltip's
   "Daggers" is accurate: daggers qualify because they ARE swords.

WHAT THE OLD TEXT GOT WRONG. Shipped `tagBladeMasteryDESC` (golden-frozen value)
was "The Occultist is able to wield two weapons at once. With lighter blades,
the Occultist can attack with greater proficiency and speed. ^y(Swords/Daggers/
Axes)". Sentence 1 is TRUE (see 3, the AllowDualWieldWeapons accumulation) but
reads as flavour/permission, not as a REQUIREMENT; and the "^y(Swords/Daggers/
Axes)" parenthetical reads as "hold one of these", which is neither necessary
(a club in the other hand is fine) nor sufficient (a sword plus a shield, or a
sword alone, gets nothing). The four bonuses are silently dead for any player
not holding a weapon in each hand.

THE FIX (text follows mechanics; mechanics are Will's call and are NOT touched):
  - `tagBladeMasteryDESC` gains the two engine-accurate clauses, in the game's
    own wording and colour convention (see tools/build_text_arc.py
    TEXT_FIX_TAGS). Occult is Will's hand-tuned mastery, so the golden A7 guard
    gets an owner_approved_overrides entry naming this ruling - the wording is
    vetoable in place.
  - SIBLING, same defect class, found by the standing sweep: Warfare "Parry"
    `records\\skills\\warfare\\drxdodge attack.dbr` is a Skill_Passive whose ONLY
    bonus is characterDodgePercent (3..30) and which carries dualWieldOnly=1
    with an EMPTY qualifying-weapon list - and its description is the shared
    base tag `tagSkillDescription192` ("Even the sturdiest armor has its
    chinks...") which never mentions dual wielding. That tag is also used by
    `records\\skills\\nature\\pet\\naturepetdodge_1%perlevelx100.dbr` (no dual
    gate), so per the standing "re-point over edit-a-shared-tag" preference
    (R-41 / formula_names) this module REPOINTS the Parry record onto a new
    mod-owned `tagParryDESC` instead of overriding the shared tag.

THE GATE (process law #4). Two halves, because the two artifacts are built by
two different tools:
  - DB half = verify() below. For every contracted record it asserts the gating
    fields still equal the contract, and it sweeps EVERY player-surface skill
    for dualWieldOnly=1 records that are not contracted/waived. A mechanics edit
    (adding Mace, dropping dualWieldOnly, gating a new skill) reds the DB build
    and forces the text to be revisited.
  - TEXT half = tools/validate_weapon_gate_text.py, wired into
    build_text_arc.py's main. It reads the BUILT Text.arc + BUILT arz back and
    asserts each contracted record's rendered description contains the clauses
    its gating fields require. Editing the text without the record, or the
    record without the text, reds.
Negative tests: tools/debug/negtest_weapon_gate_truth.py.
"""

MODULE_NAME = "B100: weapon/hand gate honesty (Blade Mastery + Parry tooltips)"

# ── the records this wave contracts ────────────────────────────────────────
BLADE_MASTERY = r'records\skills\stealth\drx_dual_blade.dbr'
PARRY = r'records\skills\warfare\drxdodge attack.dbr'

PARRY_SHARED_TAG = 'tagSkillDescription192'   # shared with a Nature pet dodge skill
PARRY_OWN_TAG = 'tagParryDESC'                # mod-owned, authored in build_text_arc

# Clause fragments the TEXT half requires. Kept here so the DB module and the
# Text validator cannot drift apart.
CLAUSE_DUAL_WIELD = 'Allows and requires dual wielding.'
CLAUSE_SWORD_OR_AXE = 'Requires at least one sword, dagger, or axe.'

# record -> exact expected gate + the description tag + the clauses that gate
# demands. `weapons` is the EXACT set of qualifying-weapon flags that must be 1
# (any other flag must be 0).
CONTRACT = {
    BLADE_MASTERY: {
        'label': 'Occult - Blade Mastery',
        'weapons': frozenset({'Sword', 'Axe'}),
        'dualWieldOnly': 1,
        'meleeOnly': 0,
        'tag': 'tagBladeMasteryDESC',
        'clauses': (CLAUSE_DUAL_WIELD, CLAUSE_SWORD_OR_AXE),
    },
    PARRY: {
        'label': 'Warfare - Parry',
        'weapons': frozenset(),          # no weapon-class restriction at all
        'dualWieldOnly': 1,
        'meleeOnly': 0,
        'tag': PARRY_OWN_TAG,
        'clauses': (CLAUSE_DUAL_WIELD,),
    },
}

WEAPON_FLAGS = ('Sword', 'Axe', 'Mace', 'Spear', 'Staff', 'Bow', 'Magical',
                'Shield', 'RangedOneHand')

# Player-surface skills that legitimately carry dualWieldOnly=1 WITHOUT being
# contracted here, with the reason. These are the base-game/DRX Warfare
# dual-wield ATTACKS: the gate is self-evident from the skill's own name and
# from its shipped description ("A Dual Wield technique that ..."), and they are
# vanilla text this wave does not own. Anything NOT in this set and NOT in
# CONTRACT fails the sweep, so a NEW silently-gated skill cannot slip in.
DUAL_WIELD_SWEEP_WAIVERS = {
    r'records\skills\warfare\dualweapontraining.dbr':
        'vanilla Warfare "Dual Wield" - the skill name IS the gate',
    r'records\skills\warfare\dualwieldtechnique_crosscut.dbr':
        'vanilla; desc reads "A Dual Wield technique that ..."',
    r'records\skills\warfare\dualwieldtechnique_jumpslash.dbr':
        'vanilla; desc reads "A Dual Wield technique that ..."',
    r'records\skills\warfare\dualwieldtechnique_tumult.dbr':
        'vanilla; desc reads "A Dual Wield technique that ..."',
    r'records\skills\warfare\drxdualweapontraining.dbr':
        'DRX Warfare "Dual Wield"; desc reads "Learn to effectively wield two weapons..."',
    r'records\skills\warfare\drxdualwieldtechnique_crosscut.dbr':
        'DRX; desc reads "A Dual Wield technique that ..."',
    r'records\skills\warfare\drxdualwieldtechnique_jumpslash.dbr':
        'DRX; desc reads "A dual-wield technique attack that bleeds the enemy."',
    r'records\skills\warfare\drxdualwieldtechnique_tumult.dbr':
        'DRX; desc reads "A Dual Wield technique that ..."',
    r'records\skills\warfare\drxdualwieldtechnique_wardance.dbr':
        'DRX War Dance, hangs off the Dual Wield ladder; DEBT B100-D2 (desc never '
        'states the gate) - vanilla-derived text, registered as debt not fixed here',
    r'records\xpack2\skills\runemaster\hailofaxes.dbr':
        'vanilla Runemaster "Reckless Offense"; desc already states '
        '"Allows and requires dual wielding."',
}


# ── small helpers (same idiom as tools/patches/formula_names.py) ────────────
def _get_field(db, rec, field):
    fields = db.get_fields(rec)
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == field:
            return tf.values[0] if tf.values else None
    return None


def _flag(db, rec, field):
    v = _get_field(db, rec, field)
    if v is None or v == '':
        return 0
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def gate_of(db, rec):
    """(frozenset of qualifying weapon flags that are 1, dualWieldOnly, meleeOnly)."""
    return (frozenset(w for w in WEAPON_FLAGS if _flag(db, rec, w)),
            _flag(db, rec, 'dualWieldOnly'),
            _flag(db, rec, 'meleeOnly'))


def player_surface_skills(db):
    """Records the player can actually see: whatever a mastery UI slot points at."""
    out = set()
    for rec in db.record_names():
        low = rec.replace('/', '\\').lower()
        if not low.startswith('records\\ingameui\\player skills\\'):
            continue
        target = _get_field(db, rec, 'skillName')
        if isinstance(target, str) and target.lower().endswith('.dbr'):
            out.add(target.replace('/', '\\').lower())
    return out


def tree_listed_skills(db):
    """Records any shipped mastery skill-tree lists (picks up the modifiers)."""
    out = set()
    for rec in db.record_names():
        if not rec.replace('/', '\\').lower().endswith('skilltree.dbr'):
            continue
        fields = db.get_fields(rec) or {}
        for key, tf in fields.items():
            if not key.split('###')[0].lower().startswith('skillname'):
                continue
            for val in (tf.values or []):
                if isinstance(val, str) and val.lower().endswith('.dbr'):
                    out.add(val.replace('/', '\\').lower())
    return out


# ── apply ──────────────────────────────────────────────────────────────────
def apply(db, tags):
    print("\n=== Patch B100: weapon/hand gate honesty (Blade Mastery + Parry) ===")

    # Blade Mastery: TEXT-ONLY. The record is untouched on purpose - changing
    # Sword/Axe/dualWieldOnly would be a BALANCE change and therefore Will's
    # call (see docs/WILL_RULINGS.md R-101). Assert it is what the contract
    # says so a silent upstream change cannot make the new text a lie.
    if not db.has_record(BLADE_MASTERY):
        raise SystemExit(f"B100 weapon_gate_truth: record missing: {BLADE_MASTERY!r}")
    got = gate_of(db, BLADE_MASTERY)
    want = (CONTRACT[BLADE_MASTERY]['weapons'],
            CONTRACT[BLADE_MASTERY]['dualWieldOnly'],
            CONTRACT[BLADE_MASTERY]['meleeOnly'])
    if got != want:
        raise SystemExit(
            f"B100 weapon_gate_truth: {BLADE_MASTERY} gate is "
            f"weapons={sorted(got[0])} dualWieldOnly={got[1]} meleeOnly={got[2]}, "
            f"expected weapons={sorted(want[0])} dualWieldOnly={want[1]} "
            f"meleeOnly={want[2]}. The shipped tooltip text was written against "
            f"the expected gate; update BOTH (tools/build_text_arc.py "
            f"TEXT_FIX_TAGS and this CONTRACT) or revert the record.")
    print(f"  {BLADE_MASTERY}: gate confirmed "
          f"weapons={sorted(got[0])} dualWieldOnly={got[1]} (record untouched; "
          f"text fixed in build_text_arc.TEXT_FIX_TAGS)")

    # Parry: repoint off the SHARED base tag onto its own mod-owned tag.
    if not db.has_record(PARRY):
        raise SystemExit(f"B100 weapon_gate_truth: record missing: {PARRY!r}")
    current = _get_field(db, PARRY, 'skillBaseDescription')
    if current == PARRY_OWN_TAG:
        print(f"  {PARRY}: skillBaseDescription already {PARRY_OWN_TAG!r} "
              f"(idempotent no-op)")
    elif current == PARRY_SHARED_TAG:
        db.set_field(PARRY, 'skillBaseDescription', PARRY_OWN_TAG)
        print(f"  {PARRY}: skillBaseDescription {PARRY_SHARED_TAG!r} -> "
              f"{PARRY_OWN_TAG!r} (the shared tag stays untouched for "
              f"naturepetdodge_1%perlevelx100.dbr)")
    else:
        raise SystemExit(
            f"B100 weapon_gate_truth: {PARRY} skillBaseDescription is "
            f"{current!r}; expected the known {PARRY_SHARED_TAG!r} (or the "
            f"already-fixed {PARRY_OWN_TAG!r}). Refusing to overwrite an "
            f"unexpected value.")


# ── verify: the DB half of the gate ────────────────────────────────────────
def find_gate_drift(db):
    """[(record, message)] for every contracted record whose gate no longer
    matches the gate its shipped text was written against."""
    out = []
    for rec, spec in CONTRACT.items():
        if not db.has_record(rec):
            out.append((rec, f"{spec['label']}: contracted record MISSING"))
            continue
        got = gate_of(db, rec)
        want = (spec['weapons'], spec['dualWieldOnly'], spec['meleeOnly'])
        if got != want:
            out.append((rec, (
                f"{spec['label']}: gate changed - weapons "
                f"{sorted(want[0])} -> {sorted(got[0])}, dualWieldOnly "
                f"{want[1]} -> {got[1]}, meleeOnly {want[2]} -> {got[2]}. The "
                f"shipped tooltip ({spec['tag']}) says: "
                f"{' / '.join(spec['clauses'])}")))
        tag = _get_field(db, rec, 'skillBaseDescription')
        if tag != spec['tag']:
            out.append((rec, (
                f"{spec['label']}: skillBaseDescription is {tag!r}, contract "
                f"requires {spec['tag']!r} (the tag whose text states the gate)")))
    return out


def find_uncontracted_dual_wield_skills(db):
    """[(record, gate)] for player-surface skills carrying dualWieldOnly=1 that
    are neither contracted nor waived - i.e. a NEW silently-gated skill."""
    surface = player_surface_skills(db) | tree_listed_skills(db)
    contracted = {r.lower() for r in CONTRACT}
    waived = {r.lower() for r in DUAL_WIELD_SWEEP_WAIVERS}
    out = []
    for rec in sorted(surface):
        if rec in contracted or rec in waived:
            continue
        if not db.has_record(rec):
            continue
        cls = _get_field(db, rec, 'Class')
        if not isinstance(cls, str) or not cls.startswith('Skill'):
            continue
        if _flag(db, rec, 'dualWieldOnly'):
            out.append((rec, gate_of(db, rec)))
    return out


def verify(db, tags):
    print("\n=== Gate B100: weapon/hand gate honesty ===")
    drift = find_gate_drift(db)
    strays = find_uncontracted_dual_wield_skills(db)
    for rec, msg in drift:
        print(f"  GATE-DRIFT [{rec}]\n      {msg}")
    for rec, gate in strays:
        print(f"  UNCONTRACTED dualWieldOnly=1 player skill: {rec} "
              f"(weapons={sorted(gate[0])})")
    if drift or strays:
        raise SystemExit(
            f"B100 weapon-gate honesty gate FAILED: {len(drift)} contracted "
            f"record(s) drifted from the gate their shipped tooltip describes, "
            f"{len(strays)} player-surface skill(s) carry dualWieldOnly=1 "
            f"without a contract or a waiver. A skill whose bonuses are "
            f"silently dead unless the player dual wields MUST say so "
            f"(docs/WILL_RULINGS.md R-100). Fix the text and the CONTRACT "
            f"together, or waive with a reason in DUAL_WIELD_SWEEP_WAIVERS.")
    print(f"  OK: {len(CONTRACT)} contracted record(s) match their tooltip's "
          f"stated gate; no uncontracted dualWieldOnly player skills "
          f"({len(DUAL_WIELD_SWEEP_WAIVERS)} waived).")
