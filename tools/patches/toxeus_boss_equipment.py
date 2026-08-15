r"""toxeus_boss_equipment - R-251 (Will 2026-08-14): the Endless Hunt wears armour, the
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
THE SLOT LAW, proven by a full base-game census (6,085 Monster.tpl records, every hand
slot's loot chain expanded to leaf templateNames):

    class                RightHand   LeftHand
    Weapon_Spear             130          0      <- the Hunt's Runbreaker is CORRECT
    Weapon_Sword             100         21
    Weapon_Axe                68         26
    Weapon_Mace               88          8
    Weapon_Bow                 0         48      <- LeftHand IS the bow slot
    Weapon_Staff               0         60
    WeaponArmor_Shield         0        123      <- LeftHand IS the shield slot

So in this engine LeftHand is the shield / two-handed-ranged slot and RightHand is the
one-handed melee slot. That single table explains two of the three reports.

(-9) THE BOW IS REAL AND IT IS EQUIPPED. `um_bloodtoxeus_99.lootLeftHandItem1` =
`bleed_affix_high_{n,e,l}` at `chanceToEquipLeftHand` 100 / weight 100 (vs the unique
shield row at weight 19). Those three tables were curated by AFFIX, not by class:
`bleed_affix_high_n` = **u_n_tendonripper (Weapon_Bow)** + 2 axes, `bleed_affix_high_l` =
**u_l_nemesis'recurve (Weapon_Bow)** + 2 axes (`_e` is 3 axes, no bow). LeftHand is
exactly where the engine expects a bow, so ~28% of Devourer spawns wield one and fight as
an archer. Written by `apply_svc_patches._wire_blood_toxeus_loot`, which used the two hand
slots as generic "guaranteed drop" channels rather than as equipment slots.

(-3) THE HUNT HAS NO ARMOUR AT ALL. `um_toxeus_hunt_99` / `um_toxeus_hunt_l_99` carry NO
`lootTorso*`, `lootLowerBody*`, `lootForearm*`, `lootHead*` or `lootLeftHand*` fields
whatsoever, and `chanceToEquipFinger1/Misc1/Misc2/Misc3` are all 0.0 - three worn slots
missing outright and four more switched off. He is literally naked. His WEAPON, though, is
correct and stays untouched: RightHand 100% -> `runbreaker_guaranteed_{n,e,l}` -> exactly
one `Weapon_Spear` (`svc_{t}_runbreaker`), and spears ride RightHand 130-to-0 in the base
game. R-247 round 3 bound the spear + unarmed animation rows; the missing half was the
loadout, exactly as Will described it ("not wearing any equipment").
His mesh can wear armour: `SkeletonRumorBoss.msh` has 18 base-game carriers and the
boss-tier ones (`jg17_undeadtyrant_{17,19,22}`) wire Head 20 / Torso 100 / LowerBody 50 /
Forearm 50 / LeftHand 100 / RightHand 100 - the pairing is base-game-proven, not assumed.

(-10) THE 100% SOUL PIN IS INTACT; THE ANOMALY IS THE HANDS. Verified in the shipped arz:
`chanceToEquipFinger2` = 100.0 (R-243's pin, byte-unchanged), `lootFinger2Item1` =
`blood_toxeus_soul_{n,e,l}`, all three resolve, all three are `Jewelry_Ring` /
`itemClassification Magical` / `itemLevel 40` - structurally IDENTICAL to the Enslaver and
Hunt souls that have never been reported missing. Exactly ONE record in the whole DB
carries `tagMonsterHemorrheus` and every spawn pool (`q_bloodtoxeus_lone`,
`egg_blooddragon`, the ambush) names that same record, so "the killed instance was a
different variant" is refuted. The ONLY structural difference between the Devourer's equip
block and his three siblings' is the cross-class hand wiring above - his RightHand rolls
`crimsonverdict_guaranteed_*`, which is 3/4 ARMOUR (helm/torso/armband) in the weapon hand,
and his LeftHand rolls weapons. This module removes that anomaly. HONEST LIMIT: the engine
path from a class-mismatched hand roll to a skipped Finger2 equip is NOT provable from the
bytes, so -10 closes on Will's next kill, not on this gate - `BL-R251-DEBT-1`, with the
escalation lever pre-designed (move the soul onto the Misc4 channel, which R-247.6a proved
delivers in-game: "Will's kill DID drop it").

WHAT THIS MODULE WRITES (and nothing else)
------------------------------------------
THE DEVOURER (`um_bloodtoxeus_99`), 1 record + 2 table edits + 3 new tables:
  * LeftHand item1  `bleed_affix_high_*` -> `shields\commondynamic\shield_{n01b,e01,l01}`
    - the Enslaver's byte-identical shield array. The off-hand can now only ever hold a
    shield. THE BOW IS GONE.
  * RightHand item1 `crimsonverdict_guaranteed_*` -> NEW `veinrender_guaranteed_{n,e,l}`
    (FixedWeight, one row: `svc_{t}_veinrender` @100) - the Runbreaker pattern, so his
    signature sword is both wielded and guaranteed-dropped.
  * RightHand item2 = `crimsonverdict_guaranteed_{n,e,l}` @ weight 19 - the 4-piece set
    table KEEPS a drop channel (no reachability regression; R-247.6a's Misc4 evidence says
    a rolled item drops even when its class cannot be worn).
  * RightHand item3 = `bleed_affix_high_{n,e,l}` @ weight 19 - the high-bleed uniques move
    to the slot their class belongs in instead of being retired.
  * `bleed_affix_high_n` / `_l` are DE-BOWED: the Weapon_Bow row is dropped and the two
    Weapon_Axe rows compact to lootName1/2 (row 3 blanked, weight 0). `_e` is asserted
    bow-free and left byte-untouched.
THE HUNT (`um_toxeus_hunt_99` + `um_toxeus_hunt_l_99`), 2 records, 0 new tables:
  * Torso / LowerBody / Forearm wired at 100 with the tier-02 loot family his own record
    already uses everywhere else (finger_n02, amulet_n02, relic_15-21), common @5000 +
    unique @19 - his brothers' exact weight shape.
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

GATE (verify, post-finalization, over the FINAL assembled db):
  E1 no Toxeus champion slot's loot chain yields Weapon_Bow or Weapon_Staff anywhere;
  E2 the Devourer's LeftHand yields only shields, his RightHand's dominant row yields only
     one-handed melee, and the two mixed-class drop rows are exactly the allowlisted pair;
  E3 both Hunt records wear Torso + LowerBody + Forearm at 100 on class-correct tables,
     and still carry the Runbreaker spear at RightHand 100 and the Misc4 rite at 100;
  E4 all four R-48 champions keep `chanceToEquipFinger2` = 100 with a soul table that
     resolves to a real Jewelry_Ring (the -10 defect class);
  E5 MOD-WIDE: every creature pinned at `chanceToEquipFinger2` = 100 has a soul reference
     that resolves to a Jewelry_Ring item - a 100% pin pointing at nothing is the
     "did not drop his soul" bug in its purest form.
Standalone twin: `py tools/gate_toxeus_boss_equipment.py [arz]`
Negative test:   `py tools/patches/toxeus_boss_equipment.py --negtest`
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

MODULE_NAME = ("R-251 Toxeus boss equipment - the Endless Hunt wears the family's armour, "
               "the Devourer of Blood carries sword-and-shield instead of a bow, and every "
               "champion hand slot holds a class that slot can wear")

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
_SHIELD_UNIQUE = _t(_LOOT + 'shields\\unique\\shield_%s01.dbr')

# the Hunt's own tier-02 loot family (matches finger_n02 / amulet_n02 already on his record)
_HUNT_ARMOUR = {
    'Torso': (_t(_LOOT + 'torso\\commondynamic\\melee_%s02.dbr'),
              _t(_LOOT + 'torso\\unique\\melee_%s02.dbr')),
    'LowerBody': (_t(_LOOT + 'legs\\commondynamic\\greaves_%s02.dbr'),
                  _t(_LOOT + 'legs\\unique\\greaves_%s02.dbr')),
    'Forearm': (_t(_LOOT + 'arms\\commondynamic\\armband_%s02.dbr'),
                _t(_LOOT + 'arms\\unique\\armband_%s02.dbr')),
}
# the family (Enslaver + Devourer) weight shape for a worn armour slot
_W_COMMON, _W_UNIQUE = 5000, 19
# the family chances the Hunt's dead slots are switched on to
_HUNT_MISC_CHANCES = {'Finger1': 100.0, 'Misc1': 100.0, 'Misc2': 18.0, 'Misc3': 50.0}

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
_ONE_HAND_MELEE = {'Weapon_Sword', 'Weapon_Axe', 'Weapon_Mace', 'Weapon_Spear',
                   'WeaponMelee_Sword', 'weapon_rangedonehand'}
_SLOT_CLASSES = {
    'Head': {'Armor_Head'},
    'Torso': {'Armor_UpperBody'},
    'LowerBody': {'Armor_LowerBody'},
    'Forearm': {'Armor_Forearm'},
    'LeftHand': {'WeaponArmor_Shield'},
    'RightHand': set(_ONE_HAND_MELEE),
    'Finger1': {'Jewelry_Ring'},
    'Finger2': {'Jewelry_Ring'},
    'Misc3': {'Jewelry_Amulet'},
}
# Classes that must never appear in ANY Toxeus champion slot: the two-handed ranged
# families. This is Will's -9 defect class, stated as an invariant.
_BANNED_CLASSES = {'Weapon_Bow', 'Weapon_Staff'}
# The mixed-class rows this lane deliberately KEEPS as pure drop channels (a rolled item
# still drops when its class cannot be worn - R-247.6a's Misc4 evidence). Owner-accepted,
# named here so the gate can never be silently widened.
_MIXED_DROP_ROWS = {
    (_DEVOURER, 'RightHand', 2): 'crimsonverdict_guaranteed - the 4-piece set drop row',
    (_DEVOURER, 'Misc4', 1): 'svc_devourer_misc4_master - rant + EoAT rite (R-247.6a)',
    (_HUNT, 'Misc4', 1): 'svc_rite_guaranteed - the EoAT formula (R-247.6a)',
    (_HUNT_L, 'Misc4', 1): 'svc_rite_guaranteed - the EoAT formula (R-247.6a)',
    (_ENSLAVER, 'Misc4', 1): 'svc_rite_guaranteed - the EoAT formula (R-247.6a)',
    (_DEVOURER, 'Misc2', 2): 'arcane formulae row (shipped, base-game shape)',
    (_ENSLAVER, 'Misc2', 2): 'arcane formulae row (shipped, base-game shape)',
    (_HUNT, 'Misc2', 1): 'relic row (shipped, base-game shape)',
    (_HUNT_L, 'Misc2', 1): 'relic row (shipped, base-game shape)',
    (_DEVOURER, 'Misc1', 1): 'potion row', (_DEVOURER, 'Misc1', 2): 'potion row',
    (_ENSLAVER, 'Misc1', 1): 'potion row', (_ENSLAVER, 'Misc1', 2): 'potion row',
    (_HUNT, 'Misc1', 1): 'potion row', (_HUNT, 'Misc1', 2): 'potion row',
    (_HUNT_L, 'Misc1', 1): 'potion row', (_HUNT_L, 'Misc1', 2): 'potion row',
    (_DEVOURER, 'Misc2', 1): 'relic row', (_ENSLAVER, 'Misc2', 1): 'relic row',
}
_SLOTS = ('Head', 'Torso', 'LowerBody', 'Forearm', 'LeftHand', 'RightHand',
          'Finger1', 'Finger2', 'Misc1', 'Misc2', 'Misc3', 'Misc4')


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


def _set(db, rec, field, value, dtype_if_new=None):
    """Write a field, passing an explicit dtype ONLY when the field is NEW.

    The dtype-preservation law both ways: never pass a dtype to an existing field
    (silent INT/FLOAT corruption), always pass one to a field that does not exist yet
    (the sanctioned arm - a brand-new field has no dtype to preserve).
    """
    if db.get_field_value(rec, field) is None and dtype_if_new is not None:
        db.set_field(rec, field, value, dtype_if_new)
    else:
        db.set_field(rec, field, value)


def _leaf_classes(db, table, depth=0, seen=None, out=None):
    """Expand a loot chain to the set of leaf item templateName stems.

    Records that are not in `db` are base-game records that exist at runtime but not in
    the mod arz; they resolve to the sentinel '' and every caller IGNORES them (an
    unresolved leaf is never a violation - that would cry wolf on half the base game).
    """
    if seen is None:
        seen, out = set(), set()
    if not table or depth > 6:
        return out
    key = _norm(table)
    if key in seen:
        return out
    seen.add(key)
    if not db.has_record(table):
        out.add('')
        return out
    fields = db.get_fields(table) or {}
    kids = []
    for k in fields:
        kk = str(k).split('###')[0].lower()
        if kk.startswith(('lootname', 'itemname', 'bothname')):
            for x in _gl(db, table, str(k).split('###')[0]):
                if x.lower().endswith('.dbr'):
                    kids.append(x)
    if not kids:
        tpl = str(_gv(db, table, 'templateName', '') or '')
        stem = tpl.replace('/', '\\').rsplit('\\', 1)[-1]
        if stem.lower().endswith('.tpl'):
            stem = stem[:-4]
        out.add(stem)
        return out
    for c in kids:
        _leaf_classes(db, c, depth + 1, seen, out)
    return out


def _slot_rows(db, rec, slot):
    """[(index, weight, [tables per difficulty])] for every armed row of a slot."""
    rows = []
    for i in range(1, 7):
        w = _f(_gv(db, rec, 'chanceToEquip%sItem%d' % (slot, i), 0))
        tabs = [t for t in _gl(db, rec, 'loot%sItem%d' % (slot, i)) if t.lower().endswith('.dbr')]
        if w > 0 and tabs:
            rows.append((i, w, tabs))
    return rows


# ── apply ───────────────────────────────────────────────────────────────────
def _fixedweight(db, path, members, desc):
    """Author a LootItemTable_FixedWeight in the shape apply_svc_patches uses."""
    from apply_svc_patches import (_ensure_record, DATA_TYPE_STRING, DATA_TYPE_INT,
                                   DATA_TYPE_FLOAT)
    S, I, F = DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT
    _ensure_record(db, path, 'Database\\Templates\\LootItemTable_FixedWeight.tpl')
    db._record_types[path] = 'LootItemTable_FixedWeight'
    db.set_field(path, 'Class', 'LootItemTable_FixedWeight', S)
    db.set_field(path, 'templateName', 'Database\\Templates\\LootItemTable_FixedWeight.tpl', S)
    db.set_field(path, 'FileDescription', desc, S)
    db.set_field(path, 'brokenRandomizerChance', 0.0, F)
    db.set_field(path, 'prefixRandomizerChance', 0.0, F)
    db.set_field(path, 'suffixRandomizerChance', 0.0, F)
    for i, m in enumerate(members, start=1):
        db.set_field(path, 'lootName%d' % i, m, S)
        db.set_field(path, 'lootWeight%d' % i, 100, I)
    db._modified.add(path)


def apply(db, tags):
    from apply_svc_patches import DATA_TYPE_STRING as S
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    for rec in _CHAMPIONS:
        if not db.has_record(rec):
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
    _set(db, _DEVOURER, 'lootLeftHandItem1', list(_SHIELD_COMMON), S)
    _set(db, _DEVOURER, 'chanceToEquipLeftHandItem1', 100)
    _set(db, _DEVOURER, 'lootLeftHandItem5', list(_SHIELD_UNIQUE), S)
    _set(db, _DEVOURER, 'chanceToEquipLeftHandItem5', _W_UNIQUE)
    db._modified.add(_DEVOURER)

    # ── 2. his weapon hand: a guaranteed Vein Render, the Runbreaker pattern ──
    rh = _gl(db, _DEVOURER, 'lootRightHandItem1')
    if not _same(rh, _CRIMSON_SET):
        raise SystemExit(
            "[toxeus_boss_equipment] PRE-STATE DRIFT: Devourer lootRightHandItem1 = %r, "
            "expected the shipped crimsonverdict_guaranteed_{n,e,l}." % (rh,))
    for tab, item, tier in zip(_VEINRENDER_TAB, _VEINRENDER_ITEM, 'NEL'):
        if not db.has_record(item):
            raise SystemExit("[toxeus_boss_equipment] Vein Render item MISSING: %s" % item)
        _fixedweight(db, tab, [item], 'Vein Render guaranteed - the Devourer of Blood (%s)' % tier)
    _set(db, _DEVOURER, 'lootRightHandItem1', list(_VEINRENDER_TAB), S)
    _set(db, _DEVOURER, 'chanceToEquipRightHandItem1', 100)
    # the 4-piece set table keeps a drop channel (allowlisted mixed row)
    _set(db, _DEVOURER, 'lootRightHandItem2', list(_CRIMSON_SET), S)
    _set(db, _DEVOURER, 'chanceToEquipRightHandItem2', _W_UNIQUE)
    # the high-bleed uniques move to the slot their class belongs in
    _set(db, _DEVOURER, 'lootRightHandItem3', list(_BLEED), S)
    _set(db, _DEVOURER, 'chanceToEquipRightHandItem3', _W_UNIQUE)

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
            _set(db, tab, 'lootWeight%d' % i, 100)
        _set(db, tab, 'lootName%d' % (len(kept) + 1), '')
        _set(db, tab, 'lootWeight%d' % (len(kept) + 1), 0)
        db._modified.add(tab)
        debowed += 1
    print("  [-9] Devourer: LeftHand -> the Enslaver's shield array (common@100 + "
          "unique@%d), RightHand -> veinrender_guaranteed@100 + the set table@%d + the "
          "bleed uniques@%d; %d bleed table(s) de-bowed. He can no longer hold a bow in "
          "any slot." % (_W_UNIQUE, _W_UNIQUE, _W_UNIQUE, debowed))

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
                if not db.has_record(tab):
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
    print("=== toxeus_boss_equipment done ===\n")


# ── the gate ────────────────────────────────────────────────────────────────
def _check(db):
    """The R-251 contract over the FINAL db. Returns a list of problem strings."""
    out = []

    # E1 + E2 + E4: per-champion slot-class integrity.
    for rec in _CHAMPIONS:
        if not db.has_record(rec):
            out.append("E1 champion record MISSING: %s" % rec)
            continue
        short = rec.rsplit('\\', 1)[-1]
        for slot in _SLOTS:
            if _f(_gv(db, rec, 'chanceToEquip%s' % slot, 0)) <= 0:
                continue
            allowed = _SLOT_CLASSES.get(slot)
            for idx, _w, tabs in _slot_rows(db, rec, slot):
                for tab in tabs[:1]:                    # tier N is representative
                    classes = {c for c in _leaf_classes(db, tab) if c}
                    banned = classes & _BANNED_CLASSES
                    if banned:
                        out.append("E1 %s %s item%d -> %s yields %s - a two-handed ranged "
                                   "weapon on a Toxeus champion (Will's 'using a bow which "
                                   "makes no sense')"
                                   % (short, slot, idx, tab.rsplit('\\', 1)[-1],
                                      '/'.join(sorted(banned))))
                    if allowed is None:
                        continue
                    if (rec, slot, idx) in _MIXED_DROP_ROWS:
                        continue
                    wrong = classes - allowed
                    if wrong:
                        out.append("E2 %s %s item%d -> %s yields %s, which %s cannot wear "
                                   "(allowed: %s). Either fix the table or allowlist the "
                                   "row in _MIXED_DROP_ROWS with a reason."
                                   % (short, slot, idx, tab.rsplit('\\', 1)[-1],
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
            if not db.has_record(s):
                out.append("E4 %s soul reference does NOT resolve: %s" % (short, s))
                continue
            tpl = _norm(_gv(db, s, 'templateName', ''))
            if 'jewelry_ring' not in tpl:
                out.append("E4 %s soul %s is templateName %r, not a Jewelry_Ring - the "
                           "engine cannot equip it into Finger2, so it never drops"
                           % (short, s.rsplit('\\', 1)[-1], tpl))

    # E2b - the Devourer's hands, spelled out.
    if db.has_record(_DEVOURER):
        if not _same(_gl(db, _DEVOURER, 'lootLeftHandItem1'), _SHIELD_COMMON):
            out.append("E2 Devourer lootLeftHandItem1 = %r, must be the shield array %r"
                       % (_gl(db, _DEVOURER, 'lootLeftHandItem1'), _SHIELD_COMMON))
        if not _same(_gl(db, _DEVOURER, 'lootRightHandItem1'), _VEINRENDER_TAB):
            out.append("E2 Devourer lootRightHandItem1 = %r, must be the guaranteed Vein "
                       "Render array" % (_gl(db, _DEVOURER, 'lootRightHandItem1'),))
        dom = max(_slot_rows(db, _DEVOURER, 'RightHand') or [(0, 0, [])],
                  key=lambda r: r[1])
        if dom[0] != 1:
            out.append("E2 Devourer's dominant RightHand row is item%d, must be item1 "
                       "(the guaranteed Vein Render) so he always has a sword in hand"
                       % dom[0])
        for tab in _VEINRENDER_TAB:
            classes = {c for c in _leaf_classes(db, tab) if c}
            if classes != {'Weapon_Sword'}:
                out.append("E2 %s yields %r, must be exactly one Weapon_Sword"
                           % (tab.rsplit('\\', 1)[-1], sorted(classes)))
    # E1b - no bow row survives anywhere in the bleed tables.
    for tab in _BLEED:
        if not db.has_record(tab):
            out.append("E1 bleed table MISSING: %s" % tab)
            continue
        classes = {c for c in _leaf_classes(db, tab) if c}
        if classes & _BANNED_CLASSES:
            out.append("E1 %s still yields %s - the de-bow did not hold"
                       % (tab.rsplit('\\', 1)[-1],
                          '/'.join(sorted(classes & _BANNED_CLASSES))))

    # E3 - the Hunt wears armour and keeps his spear + rite.
    for rec in _HUNTS:
        if not db.has_record(rec):
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
    """E5 - mod-wide: a 100% soul pin that points at nothing IS the -10 bug."""
    out = []
    checked = 0
    for name in db.record_names():
        if not _close(_gv(db, name, 'chanceToEquipFinger2'), 100.0):
            continue
        souls = [s for s in _gl(db, name, 'lootFinger2Item1') if s.lower().endswith('.dbr')]
        if not souls:
            continue
        if not any('soul' in _norm(s) for s in souls):
            continue
        checked += 1
        for s in souls:
            if not db.has_record(s):
                out.append("E5 %s is pinned at a 100%% soul drop but %s does NOT resolve"
                           % (name.rsplit('\\', 1)[-1], s))
            elif 'jewelry_ring' not in _norm(_gv(db, s, 'templateName', '')):
                out.append("E5 %s is pinned at 100%% but its soul %s is not a Jewelry_Ring"
                           % (name.rsplit('\\', 1)[-1], s.rsplit('\\', 1)[-1]))
    return out, checked


def verify(db, tags):
    problems = _check(db)
    modwide, checked = _check_modwide(db)
    problems += modwide
    if problems:
        for p in problems[:25]:
            print("  R-251 OFFENDER: %s" % p)
        raise SystemExit("[toxeus_boss_equipment] verify FAILED: %d problem(s)"
                         % len(problems))
    print("  [toxeus_boss_equipment] verify OK: no Toxeus champion can hold a bow or "
          "staff in any slot; the Devourer carries a guaranteed Vein Render + a shield; "
          "both Endless Hunt records wear torso/legs/arms at 100%% and keep the Runbreaker "
          "spear + the EoAT rite; all 4 champions hold R-243's 100%% soul pin on a soul "
          "that resolves to a real ring; %d 100%%-pinned soul carrier(s) mod-wide all "
          "resolve." % checked)


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

    def table(members, desc='t'):
        r = {'templateName': 'Database\\Templates\\LootItemTable_FixedWeight.tpl'}
        for i, m in enumerate(members, start=1):
            r['lootName%d' % i] = m
            r['lootWeight%d' % i] = 100
        return r

    def healthy():
        db = _Stub()
        # leaf items
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
        for t in _VEINRENDER_TAB:
            db.d[t] = table([sword])
        for t in _CRIMSON_SET:
            db.d[t] = table([sword, 'i\\helm.dbr', torso, arms])
        for t in _BLEED:
            db.d[t] = table(['i\\axe.dbr', 'i\\axe.dbr'])
        for t in _SHIELD_COMMON + _SHIELD_UNIQUE:
            db.d[t] = table([shieldi])
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
        dev.update({'chanceToEquipLeftHand': 100.0, 'lootLeftHandItem1': list(_SHIELD_COMMON),
                    'chanceToEquipLeftHandItem1': 100,
                    'lootLeftHandItem5': list(_SHIELD_UNIQUE), 'chanceToEquipLeftHandItem5': 19,
                    'chanceToEquipRightHand': 100.0,
                    'lootRightHandItem1': list(_VEINRENDER_TAB), 'chanceToEquipRightHandItem1': 100,
                    'lootRightHandItem2': list(_CRIMSON_SET), 'chanceToEquipRightHandItem2': 19,
                    'lootRightHandItem3': list(_BLEED), 'chanceToEquipRightHandItem3': 19})
        ens = champ(_ENSLAVER)
        ens.update({'chanceToEquipLeftHand': 100.0, 'lootLeftHandItem1': list(_SHIELD_COMMON),
                    'chanceToEquipLeftHandItem1': 100,
                    'chanceToEquipRightHand': 100.0,
                    'lootRightHandItem1': list(_VEINRENDER_TAB), 'chanceToEquipRightHandItem1': 100})
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

    def plant_bow(d):
        d.d[_BLEED[0]]['lootName3'] = 'i\\bow.dbr'
        d.d['i\\bow.dbr'] = item('Weapon_Bow')

    def plant_lefthand_bow(d):
        d.d['i\\bow.dbr'] = item('Weapon_Bow')
        d.d['t\\bowtab.dbr'] = table(['i\\bow.dbr'])
        d.d[_DEVOURER]['lootLeftHandItem1'] = ['t\\bowtab.dbr'] * 3

    plants = [
        ("the bow row survives de-bowing", plant_bow),
        ("a bow pool back in the Devourer's off-hand", plant_lefthand_bow),
        ("staff in the Devourer's off-hand", lambda d: (
            d.d.__setitem__('i\\staff.dbr', item('Weapon_Staff')),
            d.d.__setitem__('t\\stafftab.dbr', table(['i\\staff.dbr'])),
            d.d[_DEVOURER].__setitem__('lootLeftHandItem1', ['t\\stafftab.dbr'] * 3))),
        ("armour back in the Devourer's weapon hand as the dominant row",
         lambda d: d.d[_DEVOURER].__setitem__('lootRightHandItem1', list(_CRIMSON_SET))),
        ("the dominant weapon row demoted below a mixed row",
         lambda d: d.d[_DEVOURER].__setitem__('chanceToEquipRightHandItem2', 5000)),
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
         lambda d: d.d[_HUNT]. __setitem__('chanceToEquipTorsoItem1', 1)),
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
    # positive control: an untouched healthy stub must still pass at the end
    if full(healthy()):
        print("  negtest FAIL: positive control went red")
        bad += 1
    else:
        print("  negtest OK  (positive control stays green)")
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    if '--negtest' in sys.argv:
        sys.exit(_negtest())
    print(__doc__)
