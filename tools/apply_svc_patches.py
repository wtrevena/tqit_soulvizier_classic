"""SoulvizierClassic extended patches.

Patch 13: Overhaul weak uber/boss souls with skills, summons, procs
Patch 14: Cascade mercenary scrolls across all difficulties/acts
Patch 15: Add Blood Mistress formula to boss loot tables
"""
import sys
from pathlib import Path
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import (
    ArzDatabase, TypedField,
    DATA_TYPE_INT, DATA_TYPE_FLOAT, DATA_TYPE_STRING, DATA_TYPE_BOOL,
)


def _ensure_record(db, path, template):
    """Create a new empty record in the database if it doesn't exist."""
    if not db.has_record(path):
        db.ensure_string(path)
        db._raw_records[path] = (db.ensure_string(path), b'')
        db._record_types[path] = template
        db._record_timestamps[path] = 0
        db._decoded_cache[path] = OrderedDict()
        db._modified.add(path)

# ── Skill / controller path constants ──────────────────────────────────────

_AC_ON_ATTACK = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atenemy_onattack.dbr'
_AC_ON_HIT = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onanyhit.dbr'
_AC_ON_EQUIP = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onequip.dbr'
_AC_THUNDER_REACT = r'records\xpack\ai controllers\autocast_items\basetemplates\thunderballnova_onattacked.dbr'
_AC_SELF_ATTACK = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onattack.dbr'
_AC_LOW_HEALTH = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_lowhealth.dbr'
_AC_FIRE_REACT = r'records\xpack\ai controllers\autocast_items\basetemplates\flamefragmentnova_onattacked.dbr'

SUMMON_CHIMERA_SKILL = r'records\skills\soulskills\summon_chimera.dbr'
SUMMON_HYDRA_SKILL = r'records\skills\soulskills\summon_hydra.dbr'
CHIMERA_PET_1 = r'records\skills\soulskills\pets\chimaera_1.dbr'

SOUL_TEMPLATE = 'database\\Templates\\Jewelry_Ring.tpl'

SUMMON_RAKANIZEUS_SKILL = r'records\skills\soulskills\summon_rakanizeus.dbr'
SUMMON_BONEASH_SKILL = r'records\skills\soulskills\summon_boneash.dbr'
SUMMON_PHARAOH_GUARD_SKILL = r'records\skills\soulskills\summon_pharaohguard.dbr'
# A10 (build29, owner request): summon-the-boss souls for Narok + Vort.
SUMMON_NAROK_SKILL = r'records\skills\soulskills\summon_narok.dbr'
SUMMON_VORT_SKILL = r'records\skills\soulskills\summon_vort.dbr'
# D7/D8/D9 (Will 2026-07-09): more boss-named-soul -> summons-that-boss.
SUMMON_TOXEUS_SKILL = r'records\skills\soulskills\summon_bloodtoxeus.dbr'
SUMMON_XEIWANG_SKILL = r'records\skills\soulskills\summon_xeiwang.dbr'
SUMMON_MOUNTAINBLADE_SKILL = r'records\skills\soulskills\summon_mountainblade.dbr'
SUMMON_ENSLAVER_SKILL = r'records\skills\soulskills\summon_toxeus_enslaver.dbr'
SUMMON_ENSLAVER_PETMARAUDERS = r'records\skills\soulskills\svc_enslaver_petmarauders.dbr'

# ── All mercenary scroll item paths ────────────────────────────────────────

NORMAL_SCROLLS = [
    'records/item/artifacts/n_mercscroll_euanthe.dbr',
    'records/item/artifacts/n_mercscroll_scyrna.dbr',
    'records/item/artifacts/n_mercscroll_iaera.dbr',
    'records/item/artifacts/n_mercscroll_kemzir.dbr',
    'records/item/artifacts/n_mercscroll_skoneros.dbr',
    'records/item/artifacts/n_mercscroll_apollinia.dbr',
]

EPIC_SCROLLS = [
    'records/item/artifacts/n_mercscroll_tykos.dbr',
    'records/item/artifacts/n_mercscroll_mivania.dbr',
    'records/item/artifacts/n_mercscroll_ixion.dbr',
]

LEGENDARY_SCROLLS = [
    'records/item/artifacts/n_mercscroll_vanati.dbr',
]

BLOOD_MISTRESS_FORMULA = r'records\item\formulas\n_mercupgrade_bloodmistress_formula.dbr'

# ── Merc scroll loot tables ────────────────────────────────────────────────

MERC_LOOT_TABLES = {
    'records\\item\\loottables\\mercscrolls\\01_n_mercscrolls.dbr': 'n1',
    'records\\item\\loottables\\mercscrolls\\02_n_mercscrolls.dbr': 'n2',
    'records\\item\\loottables\\mercscrolls\\03_n_mercscrolls.dbr': 'n3',
    'records\\item\\loottables\\mercscrolls\\04_n_mercscrolls.dbr': 'n4',
    'records\\item\\loottables\\mercscrolls\\01_e_mercscrolls.dbr': 'e1',
    'records\\item\\loottables\\mercscrolls\\02_e_mercscrolls.dbr': 'e2',
    'records\\item\\loottables\\mercscrolls\\03_e_mercscrolls.dbr': 'e3',
    'records\\item\\loottables\\mercscrolls\\04_e_mercscrolls.dbr': 'e4',
    'records\\item\\loottables\\mercscrolls\\01_l_mercscrolls.dbr': 'l1',
    'records\\item\\loottables\\mercscrolls\\02_l_mercscrolls.dbr': 'l2',
    'records\\item\\loottables\\mercscrolls\\03_l_mercscrolls.dbr': 'l3',
    'records\\item\\loottables\\mercscrolls\\04_l_mercscrolls.dbr': 'l4',
}

# ── Individual soul enhancement specs ──────────────────────────────────────
# For existing SV souls that need overhauls.
# Key = partial path match, Value = dict of fields to set/override.

SOUL_OVERHAULS = {
    # ── RAKANIZEUS: Lightning god-satyr. Summons Rakanizeus + speed + chain lightning skills
    'rakanizeus_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_RAKANIZEUS_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxstormsurge.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxlightningbolt_chainlightning.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 4),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, 45.0),
        'characterAttackSpeedModifier': (DATA_TYPE_INT, 35),
        'characterTotalSpeedModifier': (DATA_TYPE_INT, 25),
        'defensivePierce': (DATA_TYPE_FLOAT, 15.0),
        'characterLife': (DATA_TYPE_INT, 200),
        'characterMana': (DATA_TYPE_INT, 100),
        'characterStrength': (DATA_TYPE_INT, 40),
        'characterDexterity': (DATA_TYPE_INT, 40),
        'characterOffensiveAbility': (DATA_TYPE_INT, 50),
    },

    # ── BONEASH: Fire skeleton caster. Summons Boneash + cast speed + fire skills
    'boneash_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_BONEASH_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\earth\drxvolcanicorb.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\earth\drxfireenchantment.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 35),
        'characterMana': (DATA_TYPE_INT, 150),
        'characterIntelligence': (DATA_TYPE_INT, 50),
        'characterLifeModifier': (DATA_TYPE_FLOAT, -4.0),
    },

    # ── NAROK THE ROCKSKIN (A10 build29 + D2 build30, Will: he wanted the
    #    SOUL way more powerful, not the boss monster). Source: um_rockskin_42
    #    (dragonian storm/spirit caster, tagNewHero88; hostile record verified
    #    byte-identical build28->build29, untouched here). build30 D2b: the
    #    passive stat lines are buffed AGGRESSIVELY and LADDERED per the family
    #    convention (SV souls scale n < e < l with itemLevel 42/59/71; build29's
    #    flat lines broke that). Numbers flagged in needs_will_signoff.
    #    The three keys below each match exactly one tier (the parked
    #    "conflicted copy" n-variant matches the _n key, same as build29).
    'rockskin_soul_n': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_NAROK_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\spirit\drxternion.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 6),                 # b29 flat 6, SV 3
        'characterLife': (DATA_TYPE_INT, 350),                    # b29 flat 250, SV 85
        'characterMana': (DATA_TYPE_INT, 200),                    # b29 flat 150, SV -80
        'characterManaRegenModifier': (DATA_TYPE_FLOAT, 80.0),    # b29 flat 80, SV 60
        'characterIntelligence': (DATA_TYPE_INT, 60),             # b29 flat 50
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 25),   # b29 flat 25
        'defensiveFire': (DATA_TYPE_FLOAT, 25.0),                 # b29 flat 25, SV 12
    },
    'rockskin_soul_e': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_NAROK_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\spirit\drxternion.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 8),
        'characterLife': (DATA_TYPE_INT, 550),
        'characterMana': (DATA_TYPE_INT, 300),
        'characterManaRegenModifier': (DATA_TYPE_FLOAT, 100.0),
        'characterIntelligence': (DATA_TYPE_INT, 90),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 32),
        'defensiveFire': (DATA_TYPE_FLOAT, 32.0),
    },
    'rockskin_soul_l': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_NAROK_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\spirit\drxternion.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 10),
        'characterLife': (DATA_TYPE_INT, 800),
        'characterMana': (DATA_TYPE_INT, 450),
        'characterManaRegenModifier': (DATA_TYPE_FLOAT, 130.0),
        'characterIntelligence': (DATA_TYPE_INT, 130),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 40),
        'defensiveFire': (DATA_TYPE_FLOAT, 40.0),
    },

    # ── VORT THE RED (A10 build29 + D2 build30, same owner clarification):
    #    manual-cast boss summon + AGGRESSIVE laddered storm-bruiser stat lines
    #    (n/e/l per family convention, itemLevel 40/57/70). Source hero
    #    hero_tarthon_na'arak_40 (tagMonsterName1139; SV filename vs display
    #    mismatch is upstream; hostile verified byte-identical build28->build29,
    #    untouched here). Numbers flagged in needs_will_signoff.
    'vort_soul_n': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_VORT_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxthunderball_concussiveblast.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 5),                 # b29 flat 5, SV 2
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxthunderball.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 4),                 # b29 flat 4 (new augment)
        'characterLife': (DATA_TYPE_INT, 300),                    # b29 flat 200
        'characterMana': (DATA_TYPE_INT, 250),                    # b29 flat 200
        'characterIntelligence': (DATA_TYPE_INT, 70),             # b29 flat 60
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 30),   # b29 flat 30
        'defensiveLightning': (DATA_TYPE_FLOAT, 25.0),            # b29 flat 25, SV 25
    },
    'vort_soul_e': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_VORT_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxthunderball_concussiveblast.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 7),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxthunderball.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 6),
        'characterLife': (DATA_TYPE_INT, 500),
        'characterMana': (DATA_TYPE_INT, 350),
        'characterIntelligence': (DATA_TYPE_INT, 100),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 38),
        'defensiveLightning': (DATA_TYPE_FLOAT, 33.0),
    },
    'vort_soul_l': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_VORT_SKILL),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxthunderball_concussiveblast.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 9),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\storm\drxthunderball.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 8),
        'characterLife': (DATA_TYPE_INT, 750),
        'characterMana': (DATA_TYPE_INT, 500),
        'characterIntelligence': (DATA_TYPE_INT, 140),
        'characterSpellCastSpeedModifier': (DATA_TYPE_INT, 48),
        'defensiveLightning': (DATA_TYPE_FLOAT, 42.0),
    },

    # ── CALYBE THE WARDANCER: Dual-wield berserker. Eclipse blood drain on-hit
    'calybe_soul': {
        'itemSkillName': (DATA_TYPE_STRING, r'records\skills\soulskills\calybe_eclipse.dbr'),
        'itemSkillLevel': (DATA_TYPE_INT, 6),
        'itemSkillAutoController': (DATA_TYPE_STRING, _AC_ON_HIT),
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\warfare\drxdualwieldtechnique_wardance.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 4),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\warfare\drxdualwieldtechnique_crosscut.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterAttackSpeedModifier': (DATA_TYPE_FLOAT, 18.0),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, 8.0),
        'characterOffensiveAbility': (DATA_TYPE_FLOAT, 50.0),
        'characterDexterity': (DATA_TYPE_INT, 30),
        'characterDodgePercent': (DATA_TYPE_FLOAT, 10.0),
        'offensivePhysicalModifier': (DATA_TYPE_INT, 20),
        'offensiveSlowBleedingModifier': (DATA_TYPE_INT, 35),
        'offensivePierceRatioModifier': (DATA_TYPE_INT, 15),
        'characterLife': (DATA_TYPE_INT, -60),
    },

    # ── PHARAOH'S HONOR GUARD: Tanky construct. Summon + movement penalty only
    'pharaohshonorguard_soul': {
        'itemSkillName': (DATA_TYPE_STRING, SUMMON_PHARAOH_GUARD_SKILL),
        'characterTotalSpeedModifier': (DATA_TYPE_INT, 0),     # remove total speed penalty
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, -9.0),  # movement-only penalty
    },

    # ── XERKOS THE BETRAYER: Slow heavy-hitter. Stun + lethal strike, -move speed
    'xerkosthebetrayer_soul': {
        'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\warfare\drxdualweapontraining.dbr'),
        'augmentSkillLevel1': (DATA_TYPE_INT, 3),
        'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\stealth\drxlethalstrike.dbr'),
        'augmentSkillLevel2': (DATA_TYPE_INT, 3),
        'characterAttackSpeedModifier': (DATA_TYPE_FLOAT, 15.0),
        'characterOffensiveAbility': (DATA_TYPE_FLOAT, 50.0),
        'characterRunSpeedModifier': (DATA_TYPE_FLOAT, -8.0),
        'offensivePhysicalMin': (DATA_TYPE_FLOAT, 20.0),
        'offensivePhysicalMax': (DATA_TYPE_FLOAT, 45.0),
        'offensiveStunMin': (DATA_TYPE_FLOAT, 0.5),
        'offensiveStunMax': (DATA_TYPE_FLOAT, 1.5),
        'offensiveStunChance': (DATA_TYPE_FLOAT, 20.0),
        'characterLife': (DATA_TYPE_INT, 100),
        'characterStrength': (DATA_TYPE_INT, 30),
        'characterDexterity': (DATA_TYPE_INT, 30),
        'offensivePierceRatioModifier': (DATA_TYPE_INT, 15),
    },
}

# ── Scan-and-enhance: find ALL boss/hero souls that lack itemSkillName ─────

_BOSS_SOUL_ENHANCEMENTS = {
    'typhon': None,
    'hydra': None,
    'hades': None,
    'medusa': None,
    'cerberus': None,
    'manticore': None,
    'talos': None,
    'arachne': None,
    'charon': None,
    'chimaera': None,
    'chimera': None,
    'cyclops': None,
    'scorpos': None,
    'dragon': None,
}


def _set_soul_fields(db, record_path, field_dict):
    """Apply a dict of {field_name: (dtype, value)} to a soul record."""
    for fname, (dtype, val) in field_dict.items():
        db.set_field(record_path, fname, val, dtype)
    db._modified.add(record_path)


def _find_record(db, path):
    """Find a record by path, trying both slash conventions."""
    if db.has_record(path):
        return path
    alt = path.replace('\\', '/')
    if db.has_record(alt):
        return alt
    alt = path.replace('/', '\\')
    if db.has_record(alt):
        return alt
    # Try case-insensitive search
    lower = path.replace('\\', '/').lower()
    for name in db.record_names():
        if name.replace('\\', '/').lower() == lower:
            return name
    return None


def _copy_animation_fields(db, monster_path, pet_path):
    """Copy all animation fields from a monster record to a pet record.

    After cloning a pet from Hydra, the pet inherits Hydra-specific animation
    file paths that are incompatible with the target mesh.  This function
    copies the correct animation fields from the real monster record (which
    uses the same mesh) into the cloned pet record.
    """
    monster_fields = db.get_fields(monster_path)
    pet_fields = db.get_fields(pet_path)
    if not monster_fields or not pet_fields:
        return 0

    copied = 0
    for key, tf in monster_fields.items():
        field_name = key.split('###')[0]
        # Copy any field with "Anim" or "anim" in name (animation files,
        # weights, speeds, etc.)
        if 'Anim' in field_name or 'anim' in field_name:
            # Find matching key in pet record (may have different ### suffix)
            target_key = None
            for pk in pet_fields:
                if pk.split('###')[0] == field_name:
                    target_key = pk
                    break
            if target_key:
                pet_fields[target_key].dtype = tf.dtype
                pet_fields[target_key].values = list(tf.values)
            else:
                pet_fields[field_name] = TypedField(tf.dtype, list(tf.values))
            copied += 1

    # Blank out any leftover Hydra-specific animation fields that weren't
    # replaced (e.g. unarmedSpecialAnim1-4, unarmedLongIdleAnim which the
    # real monster doesn't have but the Hydra pet does)
    for pk in list(pet_fields.keys()):
        fn = pk.split('###')[0]
        if ('Anim' in fn or 'anim' in fn) and pet_fields[pk].dtype == 2:
            vals = pet_fields[pk].values
            if vals and isinstance(vals[0], str) and 'Hydra' in vals[0]:
                pet_fields[pk].values = ['']
                copied += 1

    db._modified.add(pet_path)
    return copied


def _strip_foreign_anim_overrides(db, pet_path, src_monster):
    """Make a summon pet's per-record animation-FILE (``.anm``) overrides match
    its SOURCE MONSTER exactly: strip every ``.anm`` override field the source
    monster does not itself define. This kills the B-SUMMON-2 invisible-body
    class without disturbing a source creature's legitimate cross-family rig.

    B-SUMMON-2 (Will screenshot-confirmed, build28): summon pets are cloned from
    Lyia (a MAENAD) and inherit ~59 Maenad / JackalMan per-weapon-class ``.anm``
    override fields. ``_copy_animation_fields`` overwrites the slots the source
    monster defines, but leaves every OTHER slot still pointing at the foreign
    Lyia animation. When the pet actively uses such a slot (e.g. DUAL-WIELDS ->
    ``dHanded*``), the engine plays a foreign-skeleton animation on the pet's
    body mesh, skinning the body vertices to a bone hierarchy the mesh lacks ->
    the BODY renders INVISIBLE while the weapons float at their hardpoints.

    The correct fix is source-faithful, NOT a blanket wipe: strip only the
    ``.anm`` override fields whose base name is NOT a field of ``src_monster``.
    What remains is exactly (a) the source monster's own overrides (already
    copied with the source's values by ``_copy_animation_fields``) and nothing
    else; every stripped slot falls back to the pet's ``charAnimationTableName``
    - the mesh's OWN-family table (same skeleton). So no foreign-skeleton
    animation can ever play. Proven byte-for-byte against the shipped DB:
      - blade-dancer (``discipleboss_bladedancer``): source has 0 ``.anm``
        fields -> all 59 foreign overrides stripped; the pet drives purely from
        ``anm_melinoe`` (which defines the melinoe dual-wield set
        ``dHandedAttackAnim = Melinoe01_DW_*``).
      - Lil'Lued (``lillued_big``): source defines 10 Bat overrides, all in the
        ``unarmed*`` slots (the ElderDjinn is an unarmed flying caster, DRX-rigged
        to Bat flying anims) -> those 10 Bat fields are KEPT; the 49 Maenad /
        JackalMan fields (``dHanded*``/``sHanded*``/spear/staff/bow) are stripped,
        and those slots fall back to ``anm_djinn``'s own Djinn dual-wield / one-hand
        set (``Djinn_DW_AttAlpha.anm`` etc.).

    ``charAnimationTableName`` is never touched. An empty value list is omitted by
    ``_encode_fields``, so a stripped field is ABSENT in the built record (exactly
    like the source monster), not present-but-empty. Deterministic: iterates the
    record's ordered field dict. Returns the count stripped.
    """
    if not src_monster:
        return 0
    src_fields = db.get_fields(src_monster) or {}
    src_names = {k.split('###')[0] for k in src_fields}
    fields = db.get_fields(pet_path)
    if not fields:
        return 0
    stripped = 0
    for key, tf in fields.items():
        base = key.split('###')[0]
        if base == 'charAnimationTableName' or base in src_names:
            continue
        if tf.dtype != DATA_TYPE_STRING:
            continue
        if any(isinstance(v, str) and v.lower().endswith('.anm') for v in tf.values):
            tf.values = []
            stripped += 1
    db._modified.add(pet_path)
    return stripped


_SKILL_PREFIXES = (
    'skillname', 'skilllevel', 'attackskillname',
    'specialattack', 'buffself', 'initialskillname',
)


def _update_existing_fields(db, monster_path, pet_path, prefixes):
    """Update VALUES of existing pet fields from monster — never add new fields.

    Uses set_field() which preserves the pet's original dtype (important!).
    Direct dtype overwrite from monster records can corrupt the encoding.
    """
    monster_fields = db.get_fields(monster_path)
    if not monster_fields:
        return 0

    # Build lookup: field_name_lower -> TypedField for monster
    monster_by_name = {}
    for key, tf in monster_fields.items():
        fn = key.split('###')[0].lower()
        if any(fn.startswith(p) for p in prefixes):
            monster_by_name[fn] = tf

    # Only update pet fields that already exist AND have a monster counterpart
    # Use set_field() to preserve pet's dtype — do NOT overwrite dtype.
    pet_fields = db.get_fields(pet_path)
    if not pet_fields:
        return 0
    updated = 0
    for pk in list(pet_fields.keys()):
        fn = pk.split('###')[0].lower()
        if fn in monster_by_name:
            mtf = monster_by_name[fn]
            db.set_field(pet_path, pk.split('###')[0], list(mtf.values))
            updated += 1

    return updated


def _set_pet_equipment(db, pet_path, equip_spec):
    """Set pet equipment from a spec dict using set_field() (dtype-safe).

    equip_spec is a dict of {field_name: value}.  All values are set via
    set_field() which preserves the existing field's dtype if the field
    already exists, or infers dtype from the Python value type for new fields.

    This is the SAFE way to assign equipment — hardcoded values, no monster
    record copying, no dtype overwriting.
    """
    sf = db.set_field
    for field_name, value in equip_spec.items():
        sf(pet_path, field_name, value)
    db._modified.add(pet_path)
    return len(equip_spec)


def _loadout_spec(loadout):
    """Build a _set_pet_equipment() spec dict from a source monster's proven
    equip loadout (B-SUMMON-1 fix).

    ``loadout`` is a list of ``(slot, chance, weight, [n, e, l paths])`` tuples
    transcribed HARD-CODED from the pet's source monster record. Soul-granted
    pets previously equipped player-tier UNIQUE items
    (``records\\item\\equipment...\\u_*``) in their loot slots; a DB-wide audit
    proved that of 25,000+ working monster/pet equip slots, ZERO auto-equip a
    player Epic/Legendary unique - every working slot points at a dynamic LOOT
    TABLE (``records\\item\\loottables\\...``) or a monster/merc weapon. So the
    unique-equipping pets spawned NAKED. This mirrors the source monster's own
    loot-table loadout (the proven-rendering configuration) using the sanctioned
    hard-coded ``_set_pet_equipment`` path (no Monster.tpl -> Pet.tpl field copy).
    """
    spec = {}
    for slot, chance, weight, paths in loadout:
        spec[f'chanceToEquip{slot}'] = float(chance)
        spec[f'chanceToEquip{slot}Item1'] = int(weight)
        spec[f'loot{slot}Item1'] = list(paths)
    return spec


def _create_rakanizeus_pet_skill(db):
    """Create Rakanizeus pet records by cloning from Lyia Leafsong.

    Lyia is the ideal clone source: she's already a permanent pet with full
    equipment, skills, and all required Pet.tpl fields.  After cloning, we
    clear her animations/equipment/skills and replace them with Rakanizeus's.
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    # Clone from Lyia (permanent pet with working equipment + skills)
    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    pet_paths = [
        r'records\skills\soulskills\pets\rakanizeus_1.dbr',
        r'records\skills\soulskills\pets\rakanizeus_2.dbr',
        r'records\skills\soulskills\pets\rakanizeus_3.dbr',
    ]

    # Per-level scaling: [level 1, level 2, level 3]
    life =       [4500, 6500, 8500]
    life_regen = [25.0, 45.0, 65.0]
    dmg_min =    [60, 90, 120]
    dmg_max =    [90, 130, 170]

    # Find the real Rakanizeus monster record
    rakan_monster = _find_record(
        db, r'records\creature\monster\satyr\um_rakanizeus_17.dbr')
    if not rakan_monster:
        print("  WARNING: Rakanizeus monster record not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Replace Lyia's animations and skills with Rakanizeus's.
        if rakan_monster:
            na = _copy_animation_fields(db, rakan_monster, path)
            ns = _update_existing_fields(db, rakan_monster, path, _SKILL_PREFIXES)
            if i == 0:
                print(f"  Copied from Rakanizeus monster: {na} anim, {ns} skill fields")

        sf = db.set_field

        # ── Equipment: fixed items per difficulty (warrior satyr loadout) ──
        # [Normal, Epic, Legendary] — game picks by current difficulty.
        # ── Equipment: mirror the SOURCE monster (um_rakanizeus_17) proven
        #    loot-table loadout (B-SUMMON-1). Player-unique gear never
        #    auto-equipped -> naked satyr; these are the dual-wield warrior
        #    tables the real Rakanizeus boss equips (1H + off-sword + armband
        #    + greaves; no helm/torso, matching the satyr body).
        _set_pet_equipment(db, path, _loadout_spec([
            ('LeftHand', 100.0, 5000, [
                r'records\item\loottables\weapons\mastertables\1h_dyn_n01b.dbr',
                r'records\item\loottables\weapons\mastertables\1h_dyn_e01.dbr',
                r'records\item\loottables\weapons\mastertables\1h_dyn_l01.dbr']),
            ('RightHand', 100.0, 5000, [
                r'records\item\loottables\weapons\commondynamic\sword_n01.dbr',
                r'records\item\loottables\weapons\commondynamic\sword_e01.dbr',
                r'records\item\loottables\weapons\commondynamic\sword_l01.dbr']),
            ('Forearm', 100.0, 5000, [
                r'records\item\loottables\arms\commondynamic\armband_n01.dbr',
                r'records\item\loottables\arms\commondynamic\armband_e01.dbr',
                r'records\item\loottables\arms\commondynamic\armband_l01.dbr']),
            ('LowerBody', 100.0, 5000, [
                r'records\item\loottables\legs\commondynamic\greaves_n01.dbr',
                r'records\item\loottables\legs\commondynamic\greaves_e01.dbr',
                r'records\item\loottables\legs\commondynamic\greaves_l01.dbr']),
        ]))
        # Disable the stale unique-ring slot from the earlier authoring (the
        # source Rakanizeus equips no ring; Lyia's clone base is chance 5).
        sf = db.set_field
        sf(path, 'chanceToEquipFinger1', 0.0)
        if i == 0:
            print("  Rakanizeus equipment: source loot-table loadout (1H/off-sword/armband/greaves)")

        # Override identity (replace Lyia's nymph identity with Rakanizeus)
        sf(path, 'charLevel', [17, 44, 61])  # match source Rakanizeus level band (B-SUMMON-1); was 1/2/3
        sf(path, 'mesh', r'SVMesh\meshes\rakanizeus.msh')
        sf(path, 'baseTexture', '')  # use mesh default
        sf(path, 'bumpTexture', '')
        sf(path, 'scale', 1.4)
        sf(path, 'description', 'tagNewHero87')
        sf(path, 'characterRacialProfile', 'Beastman')
        sf(path, 'controller', CONTROLLER)
        sf(path, 'charAnimationTableName', '')  # clear Lyia's; mesh has defaults

        # Override stats (dtype=None preserves clone's FLOAT types)
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 500.0)
        sf(path, 'characterManaRegen', 20.0)
        sf(path, 'characterStrength', 350.0)
        sf(path, 'characterDexterity', 300.0)
        sf(path, 'characterIntelligence', 200.0)
        sf(path, 'characterAttackSpeed', 0.85)
        sf(path, 'characterRunSpeed', 1.3)
        sf(path, 'characterSpellCastSpeed', 1.4)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))

        # Pet behavior — dropItems=0 prevents equipped gear from dropping as
        # loot when the pet dies (the lootItem fields still control what the
        # pet visually equips, but nothing is dropped on death).
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)

        # Party UI icons
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # ── Clone summon skill from Lyia (already permanent, no TTL) ─────────
    summon_path = SUMMON_RAKANIZEUS_SKILL
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Lyia summon {lyia_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonRakanizeus')
    sf(summon_path, 'skillManaCost', [300.0, 350.0, 400.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'rakanizeus_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3)

    print("  Rakanizeus summon: cloned 3 pet records from Lyia + summon skill")
    return True


def _create_boneash_pet_skill(db):
    """Create Boneash pet records by cloning from Lyia Leafsong.

    Boneash is a fire skeleton caster — slow movement, high INT, devastating
    fire spells (Fireball, Pillar of Flame, Flamestrike, Ternion).
    Clones from Lyia for a clean Pet.tpl baseline, then replaces animations,
    equipment, and skills with the real Boneash monster's.
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    pet_paths = [
        r'records\skills\soulskills\pets\boneash_1.dbr',
        r'records\skills\soulskills\pets\boneash_2.dbr',
        r'records\skills\soulskills\pets\boneash_3.dbr',
    ]

    # Per-level scaling
    life =       [3500, 5000, 6500]
    life_regen = [20.0, 35.0, 50.0]
    dmg_min =    [40, 60, 80]
    dmg_max =    [60, 90, 120]

    # Find the real Boneash monster record
    boneash_monster = _find_record(
        db, r'records\creature\monster\skeleton\um_boneash_30.dbr')
    if not boneash_monster:
        print("  WARNING: Boneash monster record not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Replace Lyia's animations and skills with Boneash's.
        if boneash_monster:
            na = _copy_animation_fields(db, boneash_monster, path)
            ns = _update_existing_fields(db, boneash_monster, path, _SKILL_PREFIXES)
            if i == 0:
                print(f"  Copied from Boneash monster: {na} anim, {ns} skill fields")

        sf = db.set_field

        # ── Equipment: mirror the SOURCE monster (um_boneash_30) proven
        #    loot-table loadout so the pet renders fully geared (B-SUMMON-1).
        #    The prior player-unique gear (u_*/usm_*, itemClassification Epic)
        #    never auto-equipped on a monster/pet -> the pet spawned NAKED. These
        #    are the exact dynamic loot tables the real Boneash hero equips
        #    (staff + bracelet + circlet + caster torso + caster greaves).
        _set_pet_equipment(db, path, _loadout_spec([
            ('LeftHand', 100.0, 5000, [
                r'records\item\loottables\weapons\mastertables\staff_dyn_n02.dbr',
                r'records\item\loottables\weapons\mastertables\staff_dyn_e02.dbr',
                r'records\item\loottables\weapons\mastertables\staff_dyn_l02.dbr']),
            ('Forearm', 100.0, 5000, [
                r'records\item\loottables\arms\commondynamic\bracelet_n02.dbr',
                r'records\item\loottables\arms\commondynamic\bracelet_e02.dbr',
                r'records\item\loottables\arms\commondynamic\bracelet_l02.dbr']),
            ('Head', 100.0, 5000, [
                r'records\item\loottables\head\commondynamic\circlet_n02.dbr',
                r'records\item\loottables\head\commondynamic\circlet_e02.dbr',
                r'records\item\loottables\head\commondynamic\circlet_l02.dbr']),
            ('Torso', 100.0, 5000, [
                r'records\item\loottables\torso\commondynamic\caster_n02.dbr',
                r'records\item\loottables\torso\commondynamic\caster_e02.dbr',
                r'records\item\loottables\torso\commondynamic\caster_l02.dbr']),
            ('LowerBody', 100.0, 5000, [
                r'records\item\loottables\legs\commondynamic\greavescaster_n02.dbr',
                r'records\item\loottables\legs\commondynamic\greavescaster_e02.dbr',
                r'records\item\loottables\legs\commondynamic\greavescaster_l02.dbr']),
            ('Finger1', 5.0, 5000, [
                r'records\item\loottables\finger\commondynamic\finger_n02.dbr',
                r'records\item\loottables\finger\commondynamic\finger_e02.dbr',
                r'records\item\loottables\finger\commondynamic\finger_l02.dbr']),
        ]))
        if i == 0:
            print("  Boneash equipment: source loot-table loadout (staff/bracelet/circlet/caster armor/greaves)")

        # Override identity (scale/height/texture match the real Boneash boss)
        sf(path, 'charLevel', [30, 50, 65])  # match source Boneash level band (B-SUMMON-1); was 1/2/3
        sf(path, 'mesh', r'Creatures\Monster\Skeleton\RevenantFire.msh')
        sf(path, 'scale', 1.5)
        sf(path, 'actorHeight', 2.0)
        sf(path, 'baseTexture',
           r'Creatures\Monster\Skeleton\NewSkeleton_Charcoal.tex')
        sf(path, 'charAnimationTableName',
           r'records\creature\monster\skeleton\anm\anm_skeleton01.dbr')
        sf(path, 'description', 'tagNewHero48')
        sf(path, 'characterRacialProfile', 'Undead')
        sf(path, 'controller', CONTROLLER)

        # Override stats (dtype=None preserves clone's FLOAT types)
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 1200.0)
        sf(path, 'characterManaRegen', 30.0)
        sf(path, 'characterStrength', 150.0)
        sf(path, 'characterDexterity', 150.0)
        sf(path, 'characterIntelligence', 400.0)
        sf(path, 'characterAttackSpeed', 1.2)
        sf(path, 'characterRunSpeed', 0.75)
        sf(path, 'characterSpellCastSpeed', 1.5)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))

        # Pet behavior — dropItems=0 prevents equipped gear from dropping as
        # loot when the pet dies (the lootItem fields still control what the
        # pet visually equips, but nothing is dropped on death).
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)

        # Party UI icons
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\spirit\bonefiendup.tex')
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\spirit\bonefienddown.tex')

    # ── Clone summon skill from Lyia (already permanent, no TTL) ─────────
    summon_path = SUMMON_BONEASH_SKILL
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Lyia summon {lyia_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonBoneash')
    sf(summon_path, 'skillManaCost', [250.0, 300.0, 350.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\spirit\bonefiendup.tex')
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\spirit\bonefienddown.tex')

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boneash_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3)

    print("  Boneash summon: cloned 3 pet records from Lyia + summon skill")
    return True


# ── A10 (build29): generic summon-the-boss builder (Narok + Vort) ────────────
# Mirrors the PROVEN _create_boneash_pet_skill pattern exactly: clone the
# working Lyia Leafsong pets for a clean Pet.tpl baseline, replace anims +
# skill refs with the SOURCE boss monster's own (rig-consistent by
# construction), equip via _set_pet_equipment loot-table loadouts (never
# player uniques), permanent companion (no spawnObjectsTimeToLive - inherited
# from Lyia), manual-cast summon skill (NO autocast controller; tonight's live
# evidence: manual-cast granted summons execute in-game).

_A10_BOSS_SUMMONS = [
    {
        # NAROK THE ROCKSKIN (um_rockskin_42, "Caster w Staff", storm/spirit)
        'label': 'Narok the Rockskin',
        'source': r'records\creature\monster\dragonian\um_rockskin_42.dbr',
        'summon_path': SUMMON_NAROK_SKILL,
        'pet_paths': [r'records\skills\soulskills\pets\narok_1.dbr',
                      r'records\skills\soulskills\pets\narok_2.dbr',
                      r'records\skills\soulskills\pets\narok_3.dbr'],
        'souls_partial': 'rockskin_soul',
        'display_tag': 'tagSVCSummonNarok',
        'icon_src': r'records\skills\spirit\ternion.dbr',   # his signature Ternion
        'attack_skill': r'records\skills\monster skills\attack_projectile\ternion.dbr',
        'pet_desc_tag': 'tagNewHero88',                     # = "Narok the Rockskin"
        'char_level': [42, 58, 73],                         # source band
        'life': [9500.0, 14000.0, 20000.0],                 # source floor 9.3k-13.9k
        'life_regen': [30.0, 50.0, 80.0],
        'mana': 1500.0, 'mana_regen': 30.0,
        'strength': 250.0, 'dexterity': 200.0, 'intelligence': 450.0,
        'dmg_min': [60.0, 90.0, 130.0], 'dmg_max': [90.0, 140.0, 200.0],
        'attack_speed': 1.2, 'run_speed': 0.85, 'cast_speed': 1.5,
        'scale': 1.3,   # source record carries no scale; dragonian bulk
    },
    {
        # VORT THE RED (hero_tarthon_na'arak_40 displays tagMonsterName1139 =
        # "Vort the Red"; SV filename/display mismatch is upstream)
        'label': 'Vort the Red',
        'source': "records\\creature\\monster\\dragonian\\hero_tarthon_na'arak_40.dbr",
        'summon_path': SUMMON_VORT_SKILL,
        'pet_paths': [r'records\skills\soulskills\pets\vort_1.dbr',
                      r'records\skills\soulskills\pets\vort_2.dbr',
                      r'records\skills\soulskills\pets\vort_3.dbr'],
        'souls_partial': 'vort_soul',
        'display_tag': 'tagSVCSummonVort',
        'icon_src': r'records\skills\storm\thunderball.dbr',  # his signature Thunderball
        'attack_skill': r'records\skills\monster skills\attack_projectile\damagelightning_lightningball.dbr',
        'pet_desc_tag': 'tagMonsterName1139',               # = "Vort the Red"
        'char_level': [40, 57, 71],                         # source band
        'life': [18000.0, 26000.0, 36000.0],                # source floor 17.8k-26.8k
        'life_regen': [40.0, 70.0, 110.0],
        'mana': 2900.0, 'mana_regen': 35.0,                 # source mana kept
        'strength': 450.0, 'dexterity': 350.0, 'intelligence': 400.0,
        'dmg_min': [70.0, 105.0, 150.0], 'dmg_max': [100.0, 160.0, 230.0],
        'attack_speed': 1.25, 'run_speed': 0.9, 'cast_speed': 1.5,
        'scale': 1.55,  # source's own scale
    },
]


def _create_boss_summon_from_source(db, spec):
    """Build one summon-the-boss chain (pets + summon skill + soul wiring)
    from _A10_BOSS_SUMMONS. Returns True when complete."""
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')
    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    source = _find_record(db, spec['source'])
    if not source:
        print(f"  WARNING A10: source monster missing for {spec['label']}; skipped")
        return False

    def src_val(rec, name):
        ff = db.get_fields(rec) or {}
        for key, tf in ff.items():
            if key.split('###')[0] == name and tf.values and str(tf.values[0]).strip():
                return tf.values
        return None

    mesh = src_val(source, 'mesh')
    anim = src_val(source, 'charAnimationTableName')
    tex = src_val(source, 'baseTexture')
    bump = src_val(source, 'bumpTexture')
    icon_rec = _find_record(db, spec['icon_src'])
    icon_up = src_val(icon_rec, 'skillUpBitmapName') if icon_rec else None
    icon_down = src_val(icon_rec, 'skillDownBitmapName') if icon_rec else None

    for i, path in enumerate(spec['pet_paths']):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING A10: Lyia source {lyia_sources[i]} missing")
            return False
        db.clone_record(src, path)
        # rig + skill refs from the SOURCE boss (values only, never new fields)
        _copy_animation_fields(db, source, path)
        _update_existing_fields(db, source, path, _SKILL_PREFIXES)

        sf = db.set_field
        # Equipment: the source is a staff caster (staff_dyn_*03 = its OWN
        # loot tables); armor set = the proven Boneash caster loadout.
        _set_pet_equipment(db, path, _loadout_spec([
            ('LeftHand', 100.0, 5000, [
                r'records\item\loottables\weapons\mastertables\staff_dyn_n03.dbr',
                r'records\item\loottables\weapons\mastertables\staff_dyn_e03.dbr',
                r'records\item\loottables\weapons\mastertables\staff_dyn_l03.dbr']),
            ('Forearm', 100.0, 5000, [
                r'records\item\loottables\arms\commondynamic\bracelet_n02.dbr',
                r'records\item\loottables\arms\commondynamic\bracelet_e02.dbr',
                r'records\item\loottables\arms\commondynamic\bracelet_l02.dbr']),
            ('Head', 100.0, 5000, [
                r'records\item\loottables\head\commondynamic\circlet_n02.dbr',
                r'records\item\loottables\head\commondynamic\circlet_e02.dbr',
                r'records\item\loottables\head\commondynamic\circlet_l02.dbr']),
            ('Torso', 100.0, 5000, [
                r'records\item\loottables\torso\commondynamic\caster_n02.dbr',
                r'records\item\loottables\torso\commondynamic\caster_e02.dbr',
                r'records\item\loottables\torso\commondynamic\caster_l02.dbr']),
            ('LowerBody', 100.0, 5000, [
                r'records\item\loottables\legs\commondynamic\greavescaster_n02.dbr',
                r'records\item\loottables\legs\commondynamic\greavescaster_e02.dbr',
                r'records\item\loottables\legs\commondynamic\greavescaster_l02.dbr']),
        ]))

        # identity = the source boss (render chain: mesh + texture + rig all
        # from ONE proven-rendering monster record)
        if mesh:
            sf(path, 'mesh', str(mesh[0]))
        if tex:
            sf(path, 'baseTexture', str(tex[0]))
        # bumpTexture: mirror the source boss so the normal map matches the
        # body mesh. The Lyia clone base carries her Maenad normal map
        # (maenad_lyiabmp.tex); leaving it un-reset paints that map onto the
        # source's mesh (wrong surface shading). src_val returns None when the
        # source has no bumpTexture (e.g. the Dragonian sources for Narok/Vort),
        # so this correctly clears the residue to ''.
        sf(path, 'bumpTexture', str(bump[0]) if bump else '')
        if anim:
            sf(path, 'charAnimationTableName', str(anim[0]))
        if spec.get('attack_skill'):
            atk = _find_record(db, spec['attack_skill'])
            if atk:
                sf(path, 'attackSkillName', atk)
        sf(path, 'scale', float(spec['scale']))
        sf(path, 'actorHeight', 2.0)
        sf(path, 'description', spec['pet_desc_tag'])
        sf(path, 'controller', CONTROLLER)
        sf(path, 'monsterClassification', 'Common')   # working-exemplar parity

        # per-tier power (floor = source stats; flagged for Will's sign-off)
        sf(path, 'charLevel', list(spec['char_level']))
        sf(path, 'characterLife', spec['life'][i])
        sf(path, 'characterLifeRegen', spec['life_regen'][i])
        sf(path, 'characterMana', spec['mana'])
        sf(path, 'characterManaRegen', spec['mana_regen'])
        sf(path, 'characterStrength', spec['strength'])
        sf(path, 'characterDexterity', spec['dexterity'])
        sf(path, 'characterIntelligence', spec['intelligence'])
        sf(path, 'characterAttackSpeed', spec['attack_speed'])
        sf(path, 'characterRunSpeed', spec['run_speed'])
        sf(path, 'characterSpellCastSpeed', spec['cast_speed'])
        sf(path, 'handHitDamageMin', spec['dmg_min'][i])
        sf(path, 'handHitDamageMax', spec['dmg_max'][i])

        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)
        if icon_up:
            sf(path, 'StatusIcon', str(icon_up[0]))
        if icon_down:
            sf(path, 'StatusIconRed', str(icon_down[0]))

    # summon skill (clone Lyia's = permanent pet, no TTL; boss-summon tier
    # cost/recharge = the Boneash/blade-dancer exemplar 250 energy / 180s)
    summon_path = spec['summon_path']
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)
    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', spec['display_tag'])
    sf(summon_path, 'skillManaCost', [250.0, 300.0, 350.0])
    sf(summon_path, 'skillCooldownTime', 180.0)
    sf(summon_path, 'skillCooldownReductionModifier', 180.0)
    sf(summon_path, 'skillMaxLevel', 3)
    sf(summon_path, 'petLimit', 1)
    sf(summon_path, 'petBurstSpawn', 1)
    sf(summon_path, 'spawnObjects', list(spec['pet_paths']))
    if icon_up:
        sf(summon_path, 'skillUpBitmapName', str(icon_up[0]))
    if icon_down:
        sf(summon_path, 'skillDownBitmapName', str(icon_down[0]))
    db._modified.add(summon_path)

    # per-tier itemSkillLevel on the souls (N=1 E=2 L=3; any other matched
    # variant - e.g. upstream "conflicted copy" parkings that SOUL_OVERHAULS
    # also touches - gets level 1 so the activation invariant holds)
    for name in list(db.record_names()):
        nl = name.lower()
        if spec['souls_partial'] in nl and 'equipmentring' in nl and '\\soul\\' in nl:
            if nl.endswith('_soul_n.dbr'):
                db.set_field(name, 'itemSkillLevel', 1)
            elif nl.endswith('_soul_e.dbr'):
                db.set_field(name, 'itemSkillLevel', 2)
            elif nl.endswith('_soul_l.dbr'):
                db.set_field(name, 'itemSkillLevel', 3)
            else:
                db.set_field(name, 'itemSkillLevel', 1)
            db._modified.add(name)

    print(f"  A10 {spec['label']}: 3 pets from source rig + summon skill "
          f"(250/300/350 en, 180s cd) + souls wired 1/2/3")
    return True


def _create_pharaoh_guard_pet_skill(db):
    """Create Pharaoh's Honor Guard pet records by cloning from Lyia.

    The Honor Guard is a tanky construct (stone guardian statue) — slow movement,
    high life, high physical damage, no mana/magic.  Fights barehanded (no equipment).
    """
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')

    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'

    pet_paths = [
        r'records\skills\soulskills\pets\pharaohguard_1.dbr',
        r'records\skills\soulskills\pets\pharaohguard_2.dbr',
        r'records\skills\soulskills\pets\pharaohguard_3.dbr',
    ]

    # Per-level scaling: tanky slow construct
    life =       [5000, 7500, 10000]
    life_regen = [30.0, 50.0, 70.0]
    dmg_min =    [55, 80, 110]
    dmg_max =    [85, 120, 160]

    # Find the real Honor Guard monster record
    guard_monster = _find_record(
        db, r'records\creature\monster\questbosses\boss_pharaohshonorguard1_31.dbr')
    if not guard_monster:
        print("  WARNING: Pharaoh's Honor Guard monster record not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)

        # Replace Lyia's animations and skills with Honor Guard's.
        if guard_monster:
            na = _copy_animation_fields(db, guard_monster, path)
            ns = _update_existing_fields(db, guard_monster, path, _SKILL_PREFIXES)
            if i == 0:
                print(f"  Copied from Honor Guard monster: {na} anim, {ns} skill fields")

        sf = db.set_field

        # No equipment — construct fights barehanded (like the real monster)
        # Disable all equipment slots inherited from Lyia
        for slot in ('LeftHand', 'RightHand', 'Forearm', 'Finger1',
                     'Finger2', 'Head', 'Torso', 'LowerBody',
                     'Misc1', 'Misc2', 'Misc3'):
            sf(path, f'chanceToEquip{slot}', 0.0)
        if i == 0:
            print("  Honor Guard equipment: none (barehanded construct)")

        # Override identity
        sf(path, 'charLevel', i + 1)
        sf(path, 'mesh', r'Creatures\Monster\GuardianStatue\StatuePossesed.msh')
        sf(path, 'baseTexture', '')  # use mesh default
        sf(path, 'bumpTexture', '')
        sf(path, 'scale', 1.1)
        sf(path, 'actorHeight', 1.7)
        sf(path, 'description', 'tagMonsterName1180')
        sf(path, 'characterRacialProfile', 'Construct')
        sf(path, 'controller', CONTROLLER)
        sf(path, 'charAnimationTableName', '')

        # Override stats — tanky slow melee (dtype=None preserves FLOAT)
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 0.0)
        sf(path, 'characterManaRegen', 0.0)
        sf(path, 'characterStrength', 350.0)
        sf(path, 'characterDexterity', 150.0)
        sf(path, 'characterIntelligence', 0.0)
        sf(path, 'characterAttackSpeed', 1.0)
        sf(path, 'characterRunSpeed', 0.7)
        sf(path, 'characterSpellCastSpeed', 1.0)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))

        # Pet behavior — dropItems=0 prevents any loot from dropping when
        # the pet dies (consistent with all other soul pets).
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)

        # Party UI icons (use generic summon icons)
        sf(path, 'StatusIcon',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
        sf(path, 'StatusIconRed',
           r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # ── Clone summon skill from Lyia (already permanent, no TTL) ─────────
    summon_path = SUMMON_PHARAOH_GUARD_SKILL
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        print(f"  WARNING: Lyia summon {lyia_summon} not found, creating empty")
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)

    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonPharaohGuard')
    sf(summon_path, 'skillManaCost', [350.0, 400.0, 450.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriorup.tex')
    sf(summon_path, 'skillDownBitmapName',
       r'DRXtextures\skill icons\scroll\summonsatyrwarriordown.tex')

    # Set per-variant itemSkillLevel on soul records (N=1, E=2, L=3)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'pharaohshonorguard_soul' in nl and 'equipmentring' in nl:
            if '_soul_n.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 1)
            elif '_soul_e.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 2)
            elif '_soul_l.dbr' in nl:
                db.set_field(name, 'itemSkillLevel', 3)

    print("  Pharaoh Guard summon: cloned 3 pet records from Lyia + summon skill")
    return True


def _update_pharaoh_guard_drop_rate(db):
    """Change Pharaoh's Honor Guard soul drop rate from 2.25% to 10%."""
    updated = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'pharaohshonorguard' in nl and 'creature' in nl:
            fields = db.get_fields(name)
            if not fields:
                continue
            # Check if this record has a soul drop (chanceToEquipFinger2 > 0)
            for key, tf in fields.items():
                fn = key.split('###')[0]
                if fn == 'chanceToEquipFinger2' and tf.values and float(tf.values[0]) > 0:
                    db.set_field(name, 'chanceToEquipFinger2', 10.0)
                    db._modified.add(name)
                    updated += 1
                    break
    print(f"  Pharaoh's Honor Guard drop rate: 2.25% -> 10% ({updated} monster records)")
    return updated


def _fix_low_boss_soul_drop_rates(db):
    """Raise soul drop rates to 25% for major bosses that have very low rates."""
    bosses = [
        ('boss_titan_typhon', 'Typhon', 25.0),
        ('boss_hadesform3', 'Hades Form 3', 25.0),
        ('boss_greektelkine_megalesios', 'Megalesios', 25.0),
        ('boss_egypttelkine_aktaios', 'Aktaios', 25.0),
        ('boss_chinatelkine_ormenos', 'Ormenos', 25.0),
        ('boss_cerberus', 'Cerberus', 25.0),
    ]
    total = 0
    for tag, label, target_rate in bosses:
        updated = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if tag in nl:
                fields = db.get_fields(name)
                if not fields:
                    continue
                # Check if this record has a soul drop (chanceToEquipFinger2 > 0)
                for key, tf in fields.items():
                    fn = key.split('###')[0]
                    if fn == 'chanceToEquipFinger2' and tf.values and float(tf.values[0]) > 0:
                        db.set_field(name, 'chanceToEquipFinger2', target_rate, DATA_TYPE_FLOAT)
                        db._modified.add(name)
                        updated += 1
                        break
        print(f"  {label} drop rate -> {target_rate}% ({updated} monster records)")
        total += updated
    return total


def _wire_missing_boss_souls(db):
    """Wire soul drops onto boss variants that are missing them."""
    total = 0

    # ── Helper: find lootFinger2Item1 values from a donor record ────────
    def _get_soul_paths(tag):
        """Find lootFinger2Item1 [N, E, L] from any record matching tag."""
        for name in db.record_names():
            nl = name.lower()
            if tag in nl:
                fields = db.get_fields(name)
                if not fields:
                    continue
                for key, tf in fields.items():
                    fn = key.split('###')[0]
                    if fn == 'lootFinger2Item1' and tf.values and len(tf.values) >= 3:
                        return list(tf.values)
        return None

    def _wire_soul(name, soul_paths, chance):
        """Set lootFinger2Item1 and chanceToEquipFinger2 on a record."""
        db.set_field(name, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
        db.set_field(name, 'chanceToEquipFinger2', chance, DATA_TYPE_FLOAT)
        db.set_field(name, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
        db._modified.add(name)

    # ── Ormenos (all variants): direct soul path wiring ─────────────────
    # Fuzzy matcher can't match "ormenos" (7 chars) in
    # "boss_chinatelkine_ormenos_44" — below score threshold of 10.
    ORMENOS_SOULS = [
        r'records\item\equipmentring\soul\telkine\ormenos_soul_n.dbr',
        r'records\item\equipmentring\soul\telkine\ormenos_soul_e.dbr',
        r'records\item\equipmentring\soul\telkine\ormenos_soul_l.dbr',
    ]
    wired = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boss_chinatelkine_ormenos' in nl:
            existing = db.get_field_value(name, 'lootFinger2Item1')
            if not existing or existing == '' or existing == 0:
                _wire_soul(name, ORMENOS_SOULS, 25.0)
                wired += 1
    print(f"  Ormenos soul wired: {wired} records")
    total += wired

    # ── Aktaios (all variants): direct soul path wiring ───────────────
    # "aktaios" (7 chars) also below threshold in "boss_egypttelkine_aktaios_27"
    AKTAIOS_SOULS = [
        r'records\item\equipmentring\soul\telkine\aktaios_soul_n.dbr',
        r'records\item\equipmentring\soul\telkine\aktaios_soul_e.dbr',
        r'records\item\equipmentring\soul\telkine\aktaios_soul_l.dbr',
    ]
    wired = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boss_egypttelkine_aktaios' in nl:
            existing = db.get_field_value(name, 'lootFinger2Item1')
            if not existing or existing == '' or existing == 0:
                _wire_soul(name, AKTAIOS_SOULS, 25.0)
                wired += 1
    print(f"  Aktaios soul wired: {wired} records")
    total += wired

    # ── Megalesios (all variants): direct soul path wiring ──────────
    # Borderline score=10 in fuzzy matcher; wire explicitly for reliability
    MEGALESIOS_SOULS = [
        r'records\item\equipmentring\soul\telkine\megalesios_soul_n.dbr',
        r'records\item\equipmentring\soul\telkine\megalesios_soul_e.dbr',
        r'records\item\equipmentring\soul\telkine\megalesios_soul_l.dbr',
    ]
    wired = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boss_greektelkine_megalesios' in nl:
            # The substring also matches boss_greektelkine_megalesiosstatue_*,
            # the possessed-statue props of the Megalesios fight
            # (Class=SpiritHost, monsterClassification=Champion). Those must
            # NEVER drop a soul (design: only Hero/Boss/Quest do). Wiring the
            # telkine soul onto them here is what _force_100_pct_soul_drops later
            # boosts to a 100% farmable-adds drop (the Inhabited Statue bug).
            # Gate on classification so only the real Boss variants get wired;
            # the real boss already carries base soul loot and is untouched by
            # this "if not existing" block regardless.
            mc = db.get_field_value(name, 'monsterClassification')
            if mc not in ('Hero', 'Boss', 'Quest'):
                continue
            existing = db.get_field_value(name, 'lootFinger2Item1')
            if not existing or existing == '' or existing == 0:
                _wire_soul(name, MEGALESIOS_SOULS, 25.0)
                wired += 1
    print(f"  Megalesios soul wired: {wired} records")
    total += wired

    # ── Typhon (living, all variants): direct soul path wiring ────────
    # "typhon" (6 chars) below threshold in "copy of boss_titan_typhon_42"
    TYPHON_SOULS = [
        r'records\item\equipmentring\soul\typhon\typhon_soul_n.dbr',
        r'records\item\equipmentring\soul\typhon\typhon_soul_e.dbr',
        r'records\item\equipmentring\soul\typhon\typhon_soul_l.dbr',
    ]
    wired = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boss_titan_typhon' in nl:
            existing = db.get_field_value(name, 'lootFinger2Item1')
            if not existing or existing == '' or existing == 0:
                _wire_soul(name, TYPHON_SOULS, 25.0)
                wired += 1
    print(f"  Typhon (living) soul wired: {wired} records")
    total += wired

    # ── Undead Typhon (skeletal, all variants): direct soul path wiring
    UNDEAD_TYPHON_SOULS = [
        r'records\item\equipmentring\soul\typhon\undeadtyphon_soul_n.dbr',
        r'records\item\equipmentring\soul\typhon\undeadtyphon_soul_e.dbr',
        r'records\item\equipmentring\soul\typhon\undeadtyphon_soul_l.dbr',
    ]
    wired = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'boss_skeletaltyphon' in nl or ('skeletaltyphon' in nl and 'creature' in nl):
            existing = db.get_field_value(name, 'lootFinger2Item1')
            if not existing or existing == '' or existing == 0:
                _wire_soul(name, UNDEAD_TYPHON_SOULS, 25.0)
                wired += 1
    print(f"  Undead Typhon soul wired: {wired} records")
    total += wired

    # ── xpack Yaoguai: wire soul from regular Yaoguai variants ──────────
    yaoguai_souls = _get_soul_paths('boss_daemonbull_yaoguai')
    if yaoguai_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if 'boss_daemonbull_yaoguai' in nl and 'xpack' in nl:
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, yaoguai_souls, 25.0)
                    wired += 1
        print(f"  Yaoguai xpack soul wired: {wired} records (soul: {yaoguai_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Yaoguai soul paths to wire xpack variants")

    # ── Charon Form 1: wire uber soul from boss_charon_39 ───────────────
    charon_souls = _get_soul_paths('boss_charon_39')
    if charon_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if ('boss_charon_41' in nl or 'boss_charon_43' in nl):
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, charon_souls, 66.0)
                    wired += 1
        print(f"  Charon Form 1 (41/43) soul wired: {wired} records (soul: {charon_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Charon_39 soul paths to wire Charon 41/43")

    # ── Hydra: wire soul from boss_hydra_66 ─────────────────────────────
    hydra_souls = _get_soul_paths('boss_hydra_66')
    if hydra_souls:
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if ('boss_hydra_60' in nl or 'boss_hydra_63' in nl):
                existing = db.get_field_value(name, 'lootFinger2Item1')
                if not existing or existing == '' or existing == 0:
                    _wire_soul(name, hydra_souls, 25.0)
                    wired += 1
        print(f"  Hydra (60/63) soul wired: {wired} records (soul: {hydra_souls[0].split(chr(92))[-1]})")
        total += wired
    else:
        print("  WARNING: Could not find Hydra_66 soul paths to wire Hydra 60/63")

    return total


def _add_dagon_to_ichthian_pools(db):
    """Add Dagon as a rare champion spawn in all ichthian spawn pools."""
    DAGON_RECORD = r'records\test\boss_dagon_66.dbr'
    DAGON_WEIGHT = 2  # Very rare spawn

    if not db.has_record(DAGON_RECORD):
        print("  WARNING: Dagon record not found in database")
        return 0

    # Find all ichthian spawn pools (records with nameN fields referencing ichthian)
    ichthian_pools = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        has_ichthian = False
        has_name_field = False
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn.startswith('name') and not fn.startswith('nameChampion'):
                has_name_field = True
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'ichthian' in v.lower():
                        has_ichthian = True
                        break
        if has_ichthian and has_name_field:
            ichthian_pools.append(name)

    total = 0
    for pool in ichthian_pools:
        fields = db.get_fields(pool)
        if not fields:
            continue

        # Check if Dagon is already in this pool
        already_has = False
        for key, tf in fields.items():
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'boss_dagon' in v.lower():
                        already_has = True
                        break
        if already_has:
            continue

        # Find the highest existing nameChampionN index
        max_champ_idx = 0
        for key in fields:
            fn = key.split('###')[0]
            m = __import__('re').match(r'nameChampion(\d+)', fn)
            if m:
                idx = int(m.group(1))
                if idx > max_champ_idx:
                    max_champ_idx = idx

        # Add Dagon at the next champion slot
        next_idx = max_champ_idx + 1
        db.set_field(pool, f'nameChampion{next_idx}', DAGON_RECORD, DATA_TYPE_STRING)
        db.set_field(pool, f'weightChampion{next_idx}', DAGON_WEIGHT, DATA_TYPE_INT)
        db._modified.add(pool)

        # Ensure champion spawning is enabled if it wasn't
        champ_chance = db.get_field_value(pool, 'championChance')
        if champ_chance is not None and float(champ_chance) == 0.0:
            db.set_field(pool, 'championChance', 15.0, DATA_TYPE_FLOAT)
            db.set_field(pool, 'championMax', 1, DATA_TYPE_INT)

        total += 1

    print(f"  Dagon added to {total} ichthian spawn pools as rare champion (weight={DAGON_WEIGHT})")
    return total


def _add_coldworm_to_egypt_pools(db):
    """Add Cold Worm as a rare champion spawn in Act 2 Egypt underground/insect pools."""
    COLDWORM_RECORD = r'records\test\boss_coldworm50.dbr'
    COLDWORM_WEIGHT = 2  # Very rare spawn

    if not db.has_record(COLDWORM_RECORD):
        print("  WARNING: Cold Worm record not found in database")
        return 0

    # Target: all cryptworm pools + scavenger beetle pools + bone scarab pools
    # These are Egypt underground cave/tomb insectoid pools
    target_pools = []
    for name in db.record_names():
        nl = name.lower()
        if 'proxies egypt' not in nl and 'proxies egypt' not in nl.replace('\\', ' '):
            # Also check with backslash
            if r'proxies egypt' not in nl:
                continue
        if 'pools' not in nl:
            continue
        # Match cryptworm, scavenger beetle, bone scarab, scorpion pools
        basename = nl.replace('\\', '/').split('/')[-1]
        if any(tag in basename for tag in ('cryptworm_', 'scavengerbeetle_', 'bonescarab_', 'scorpion_')):
            target_pools.append(name)

    total = 0
    for pool in target_pools:
        fields = db.get_fields(pool)
        if not fields:
            continue

        # Check if Cold Worm is already in this pool
        already_has = False
        for key, tf in fields.items():
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'boss_coldworm' in v.lower():
                        already_has = True
                        break
        if already_has:
            continue

        # Find the highest existing nameChampionN index
        max_champ_idx = 0
        for key in fields:
            fn = key.split('###')[0]
            m = __import__('re').match(r'nameChampion(\d+)', fn)
            if m:
                idx = int(m.group(1))
                if idx > max_champ_idx:
                    max_champ_idx = idx

        # Add Cold Worm at the next champion slot
        next_idx = max_champ_idx + 1
        db.set_field(pool, f'nameChampion{next_idx}', COLDWORM_RECORD, DATA_TYPE_STRING)
        db.set_field(pool, f'weightChampion{next_idx}', COLDWORM_WEIGHT, DATA_TYPE_INT)
        db._modified.add(pool)

        # Ensure champion spawning is enabled if it wasn't
        champ_chance = db.get_field_value(pool, 'championChance')
        if champ_chance is not None and float(champ_chance) == 0.0:
            db.set_field(pool, 'championChance', 15.0, DATA_TYPE_FLOAT)
            db.set_field(pool, 'championMax', 1, DATA_TYPE_INT)

        total += 1

    print(f"  Cold Worm added to {total} Egypt underground/insect spawn pools (weight={COLDWORM_WEIGHT})")
    return total


def _boost_coldworm_stats(db):
    """Boost Cold Worm monster stats — base record is too slow and weak.

    Original: runSpeed=0.4, handHit=50-100, life=10000, STR=2100, INT=50.
    Reference: Grimshell (beetle boss, Lv33) has runSpeed=0.48, handHit=146-170.
    Flarecrawler (CryptWorm unique) runs at 1.2.
    """
    COLDWORM = r'records\test\boss_coldworm50.dbr'
    if not db.has_record(COLDWORM):
        print("  WARNING: Cold Worm record not found for stat boost")
        return False

    # Speed: 0.4 -> 0.75 (still lumbering, but can actually reach the player)
    db.set_field(COLDWORM, 'characterRunSpeed', 0.75, DATA_TYPE_FLOAT)
    # Hand damage: 50-100 -> 180-280 (comparable to other Act 2 bosses)
    db.set_field(COLDWORM, 'handHitDamageMin', 180.0, DATA_TYPE_FLOAT)
    db.set_field(COLDWORM, 'handHitDamageMax', 280.0, DATA_TYPE_FLOAT)
    # Life: 10000 -> 14000;18000;22000 (scales with difficulty)
    db.set_field(COLDWORM, 'characterLife', [14000.0, 18000.0, 22000.0],
                 DATA_TYPE_FLOAT)
    # Intelligence: 50 -> 250 (uses spell skills: poison gas, shockwave)
    db.set_field(COLDWORM, 'characterIntelligence', 250.0, DATA_TYPE_FLOAT)
    # Defensive ability: give it some so it's not trivially hit
    db.set_field(COLDWORM, 'characterDefensiveAbility', 350.0, DATA_TYPE_FLOAT)
    db._modified.add(COLDWORM)

    print("  Cold Worm stats boosted (speed 0.75, hand 180-280, life 14k/18k/22k)")
    return True


def _create_coldworm_soul(db):
    """Create a hand-crafted Cold Worm soul and wire it to the monster.

    Cold Worm is a level 30/50/65 boss using CryptWorm mesh.  It uses poison
    gas, shockwave, and summons bugs.  The soul has a cold/poison theme with
    defensive bonuses, an ice-blast on-hit proc, and cold/poison augments.
    Drop rate: 66%.
    """
    COLDWORM_MONSTER = r'records\test\boss_coldworm50.dbr'
    SOUL_BASE = r'records\item\equipmentring\soul\svc_uber'

    if not db.has_record(COLDWORM_MONSTER):
        print("  WARNING: Cold Worm monster record not found")
        return False

    # ── Difficulty-scaled stats (N=Lv30, E=Lv50, L=Lv65) ──────────────
    # Comparable to peers: Arachne (Lv61), Scorpos (Lv63), Boneash (Lv65)
    # Scorpos L: +409 Life, 88-93 poison, +42% poison modifier
    # Arachne L: +23 Dex, +14% AS, 45-49 poison, +46% poison res
    tiers = [
        # (suffix, itemLevel, levelReq, skillLv, augLv1, augLv2,
        #  defCold, defPoison, coldMin, coldMax, poisMin, poisMax, poisDur,
        #  coldMod, poisMod, lifeMod, life, mana, strMod, intMod, daMod, castSpeed)
        ('n', 30, 25, 2, 2, 2,
         18.0, 15.0, 10.0, 22.0, 18.0, 35.0, 3.0,
         12, 15, 5.0, 80, 50, 4.0, 4.0, 3.0, 10),
        ('e', 50, 45, 4, 3, 3,
         30.0, 25.0, 22.0, 40.0, 35.0, 60.0, 3.0,
         25, 30, 10.0, 120, 80, 6.0, 6.0, 5.0, 18),
        ('l', 65, 60, 6, 5, 5,
         42.0, 38.0, 35.0, 58.0, 50.0, 85.0, 4.0,
         40, 48, 15.0, 150, 100, 8.0, 8.0, 6.0, 25),
    ]

    soul_paths = []
    for (diff, item_lv, lv_req, sk_lv, aug1_lv, aug2_lv,
         def_cold, def_poison, cold_min, cold_max, pois_min, pois_max, pois_dur,
         cold_mod, pois_mod,
         life_mod, life, mana, str_mod, int_mod, da_mod, cast_speed) in tiers:

        path = f'{SOUL_BASE}\\boss_coldworm50_soul_{diff}.dbr'
        soul_paths.append(path)

        _ensure_record(db, path, SOUL_TEMPLATE)

        # Boilerplate fields
        base = {
            'templateName': (DATA_TYPE_STRING, SOUL_TEMPLATE),
            'Class': (DATA_TYPE_STRING, 'ArmorJewelry_Ring'),
            'bitmap': (DATA_TYPE_STRING, r'SVItems\jewelry\soul_n_icon.tex'),
            'mesh': (DATA_TYPE_STRING, r'drx\meshes\n_soulmesh.msh'),
            'itemCostName': (DATA_TYPE_STRING, 'records/game/itemcost_soul.dbr'),
            'dropSound': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDropPak.dbr'),
            'dropSound3D': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDrop3DPak.dbr'),
            'dropSoundWater': (DATA_TYPE_STRING, r'Records\Sounds\SoundPak\Items\WaterSmDropPak.dbr'),
            'itemClassification': (DATA_TYPE_STRING, 'Magical'),
            'characterBaseAttackSpeedTag': (DATA_TYPE_STRING, 'CharacterAttackSpeedAverage'),
            'castsShadows': (DATA_TYPE_INT, 1),
            'maxTransparency': (DATA_TYPE_FLOAT, 0.5),
            'scale': (DATA_TYPE_FLOAT, 1.0),
            'shadowBias': (DATA_TYPE_FLOAT, 0.01),
            'cannotPickUp': (DATA_TYPE_INT, 0),
            'cannotPickUpMultiple': (DATA_TYPE_INT, 0),
            'hidePrefixName': (DATA_TYPE_INT, 0),
            'hideSuffixName': (DATA_TYPE_INT, 0),
            'quest': (DATA_TYPE_INT, 0),
            'itemLevel': (DATA_TYPE_INT, item_lv),
            'levelRequirement': (DATA_TYPE_INT, lv_req),
            'strengthRequirement': (DATA_TYPE_INT, 0),
            'intelligenceRequirement': (DATA_TYPE_INT, 0),
            'dexterityRequirement': (DATA_TYPE_INT, 0),
            'numRelicSlots': (DATA_TYPE_INT, 1),
            'itemNameTag': (DATA_TYPE_STRING, 'tagSVCSoulColdWorm'),
            'FileDescription': (DATA_TYPE_STRING, f'boss_coldworm50 soul ({diff.upper()})'),
        }
        _set_soul_fields(db, path, base)

        # Cold/poison themed stats — scaled per difficulty
        stats = {
            # On-hit proc: ice blast
            'itemSkillName': (DATA_TYPE_STRING, r'records\skills\soulskills\gargantuanyeti_iceblast.dbr'),
            'itemSkillLevel': (DATA_TYPE_INT, sk_lv),
            'itemSkillAutoController': (DATA_TYPE_STRING, _AC_ON_HIT),
            # Augment 1: Cold aura
            'augmentSkillName1': (DATA_TYPE_STRING, r'records\skills\storm\drxcoldaura.dbr'),
            'augmentSkillLevel1': (DATA_TYPE_INT, aug1_lv),
            # Augment 2: Plague (poison)
            'augmentSkillName2': (DATA_TYPE_STRING, r'records\skills\nature\drxplague.dbr'),
            'augmentSkillLevel2': (DATA_TYPE_INT, aug2_lv),
            # Defensive: cold & poison resistance
            'defensiveCold': (DATA_TYPE_FLOAT, def_cold),
            'defensivePoison': (DATA_TYPE_FLOAT, def_poison),
            # Offensive: cold + poison flat damage
            'offensiveColdMin': (DATA_TYPE_FLOAT, cold_min),
            'offensiveColdMax': (DATA_TYPE_FLOAT, cold_max),
            'offensiveSlowPoisonMin': (DATA_TYPE_FLOAT, pois_min),
            'offensiveSlowPoisonMax': (DATA_TYPE_FLOAT, pois_max),
            'offensiveSlowPoisonDurationMin': (DATA_TYPE_FLOAT, pois_dur),
            # Offensive: % damage modifiers
            'offensiveColdModifier': (DATA_TYPE_INT, cold_mod),
            'offensiveSlowPoisonModifier': (DATA_TYPE_INT, pois_mod),
            # Stat bonuses (mix of flat + %)
            'characterLifeModifier': (DATA_TYPE_FLOAT, life_mod),
            'characterLife': (DATA_TYPE_INT, life),
            'characterMana': (DATA_TYPE_INT, mana),
            'characterStrengthModifier': (DATA_TYPE_FLOAT, str_mod),
            'characterIntelligenceModifier': (DATA_TYPE_FLOAT, int_mod),
            'characterDefensiveAbilityModifier': (DATA_TYPE_FLOAT, da_mod),
            'characterSpellCastSpeedModifier': (DATA_TYPE_INT, cast_speed),
        }
        _set_soul_fields(db, path, stats)

    # ── Wire soul to monster record with 66% drop rate ──────────────────
    db.set_field(COLDWORM_MONSTER, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
    db.set_field(COLDWORM_MONSTER, 'chanceToEquipFinger2', 66.0, DATA_TYPE_FLOAT)
    db.set_field(COLDWORM_MONSTER, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
    db._modified.add(COLDWORM_MONSTER)

    print("  Cold Worm soul created (cold/poison theme, Lv 50, 66% drop rate)")
    print(f"    Paths: {soul_paths[0].split(chr(92))[-1]} / _e / _l")
    return True


# ── Shared boilerplate for hand-crafted soul creation ─────────────────────

_SOUL_BOILERPLATE = {
    'templateName': (DATA_TYPE_STRING, SOUL_TEMPLATE),
    'Class': (DATA_TYPE_STRING, 'ArmorJewelry_Ring'),
    'bitmap': (DATA_TYPE_STRING, r'SVItems\jewelry\soul_n_icon.tex'),
    'mesh': (DATA_TYPE_STRING, r'drx\meshes\n_soulmesh.msh'),
    'itemCostName': (DATA_TYPE_STRING, 'records/game/itemcost_soul.dbr'),
    'dropSound': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDropPak.dbr'),
    'dropSound3D': (DATA_TYPE_STRING, r'records/sounds/soundpak/Items/SoulDrop3DPak.dbr'),
    'dropSoundWater': (DATA_TYPE_STRING, r'Records\Sounds\SoundPak\Items\WaterSmDropPak.dbr'),
    'itemClassification': (DATA_TYPE_STRING, 'Magical'),
    'characterBaseAttackSpeedTag': (DATA_TYPE_STRING, 'CharacterAttackSpeedAverage'),
    'castsShadows': (DATA_TYPE_INT, 1),
    'maxTransparency': (DATA_TYPE_FLOAT, 0.5),
    'scale': (DATA_TYPE_FLOAT, 1.0),
    'shadowBias': (DATA_TYPE_FLOAT, 0.01),
    'cannotPickUp': (DATA_TYPE_INT, 0),
    'cannotPickUpMultiple': (DATA_TYPE_INT, 0),
    'hidePrefixName': (DATA_TYPE_INT, 0),
    'hideSuffixName': (DATA_TYPE_INT, 0),
    'quest': (DATA_TYPE_INT, 0),
    'numRelicSlots': (DATA_TYPE_INT, 1),
    'strengthRequirement': (DATA_TYPE_INT, 0),
    'intelligenceRequirement': (DATA_TYPE_INT, 0),
    'dexterityRequirement': (DATA_TYPE_INT, 0),
}

_SOUL_DIR = r'records\item\equipmentring\soul\svc_uber'

# Reference soul to clone — has all ~618 template fields pre-populated.
# Cloning this instead of bare _ensure_record ensures the game can render
# the icon/mesh properly (grey box fix).
_SOUL_CLONE_SOURCE = r'records\item\equipmentring\soul\skeleton\boneash_soul_n.dbr'


def _create_soul(db, base_name, tag, tiers, monster=None, drop_rate=66.0):
    """Create a hand-crafted soul with N/E/L difficulty scaling.

    tiers: list of 3 dicts, each with 'diff', 'itemLevel', and 'stats' keys.
    stats values are (dtype, value) tuples.
    Returns list of [n, e, l] soul paths.
    """
    soul_paths = []
    for tier in tiers:
        diff = tier['diff']
        path = f'{_SOUL_DIR}\\{base_name}_soul_{diff}.dbr'
        soul_paths.append(path)

        _ensure_record(db, path, SOUL_TEMPLATE)
        _set_soul_fields(db, path, _SOUL_BOILERPLATE)
        _set_soul_fields(db, path, {
            'itemLevel': (DATA_TYPE_INT, tier['itemLevel']),
            'levelRequirement': (DATA_TYPE_INT, max(1, tier['itemLevel'] - 5)),
            'itemNameTag': (DATA_TYPE_STRING, tag),
            'FileDescription': (DATA_TYPE_STRING, f'{base_name} soul ({diff.upper()})'),
        })
        _set_soul_fields(db, path, tier['stats'])

    if monster and db.has_record(monster):
        db.set_field(monster, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
        db.set_field(monster, 'chanceToEquipFinger2', drop_rate, DATA_TYPE_FLOAT)
        db.set_field(monster, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
        db.set_field(monster, 'dropItems', 1, DATA_TYPE_INT)
        db._modified.add(monster)

    return soul_paths


# ── Skill path shortcuts for soul designs ─────────────────────────────────

# Dream-mastery skills live under xpack\skills\dream (verified in the built arz;
# the bare records\skills\dream\drx* paths below never existed -> soul augments
# using them silently granted nothing).
_SK_PHANTOM_STRIKE = r'records\xpack\skills\dream\drxphantomstrike.dbr'
_SK_DISTORTION_WAVE = r'records\xpack\skills\dream\drxdistortionwave.dbr'
_SK_DISTORTION_FIELD = r'records\xpack\skills\dream\drxdistortionfield.dbr'
_SK_LUCID_DREAM = r'records\xpack\skills\dream\drxluciddream.dbr'
_SK_LETHAL_STRIKE = r'records\skills\stealth\drxlethalstrike.dbr'
_SK_BATTLE_RAGE = r'records\skills\warfare\drxbattlerage.dbr'
_SK_ONSLAUGHT = r'records\skills\warfare\drxonslaught.dbr'
_SK_DUAL_WEAPON = r'records\skills\warfare\drxdualweapontraining.dbr'
_SK_DARK_COVENANT = r'records\skills\spirit\drxdarkcovenant.dbr'
_SK_DEATH_CHILL = r'records\skills\spirit\drxdeathchillaura.dbr'
_SK_TERNION = r'records\skills\spirit\drxternion.dbr'
_SK_ENVENOM = r'records\skills\stealth\drxenvenomweapon.dbr'
_SK_PLAGUE = r'records\skills\nature\drxplague.dbr'
_SK_COLD_AURA = r'records\skills\storm\drxcoldaura.dbr'
_SK_STORM_NIMBUS = r'records\skills\storm\drxstormnimbus.dbr'
_SK_CHAIN_LIGHTNING = r'records\skills\storm\drxlightningbolt_chainlightning.dbr'  # no drxchainlightning record exists; matches rakanizeus_soul usage
_SK_FIRE_ENCHANT = r'records\skills\earth\drxfireenchantment.dbr'
_SK_HEART_OF_OAK = r'records\skills\nature\drxheartofoak.dbr'
_SK_STUDY_PREY = r'records\skills\hunting\drxstudyprey.dbr'  # Study Prey is a Hunting skill, not Rogue/stealth
_SK_FLASH_POWDER = r'records\skills\stealth\drxflashpowder.dbr'
_SK_CALCULATED_STRIKE = r'records\skills\stealth\drxcalculatedstrike.dbr'
_SK_SHIELD_CHARGE = r'records\skills\defensive\drxshieldcharge.dbr'  # Shield Charge is a Defense skill, not Warfare
_SK_WAR_HORN = r'records\skills\warfare\drxwarhorn.dbr'
# No "earth enchantment" skill exists in TQAE; Fire Enchantment IS the Earth
# mastery's weapon-enchant skill (tagSkillName105) -> the real thematic augment
# for the stone/construct souls (slabskin/qinshi/rustedrelic) that use this.
_SK_EARTH_ENCHANT = r'records\skills\earth\drxfireenchantment.dbr'
_SK_VOLCANIC_ORB = r'records\skills\earth\drxvolcanicorb.dbr'
_SK_STORM_SURGE = r'records\skills\storm\drxstormsurge.dbr'
_SK_SQUALL = r'records\skills\storm\drxsquall.dbr'
_SK_RAVAGES_OF_TIME = r'records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr'  # Ravages of Time is a Death Chill Aura modifier (Spirit), tagSkillName036
_SK_PSIONIC_TOUCH = r'records\xpack\skills\dream\drxpsionictouch.dbr'
_SK_REGROWTH = r'records\skills\nature\drxregrowth.dbr'
_SK_SPIRIT_WARD = r'records\skills\spirit\drxspiritward.dbr'
_SK_NECROSIS = r'records\skills\spirit\drxdeathchillaura_necrosis.dbr'  # Necrosis is a Death Chill Aura modifier (Spirit), tagSkillName037
_SK_VISION_OF_DEATH = r'records\skills\spirit\drxvisionofdeath.dbr'
# No Runemaster mastery exists in TQAE (no runeweapon/runemaster record in the
# arz). This constant is currently unused; point it at a real weapon-enchant
# skill so it can never dangle if a future soul references it.
_SK_RUNE_WEAPON = r'records\skills\earth\drxfireenchantment.dbr'

# Soul skill procs
_SS_RING_LIGHTNING = r'records\skills\soulskills\ringoflightning.dbr'
_SS_BLOOD_BOIL = r'records\skills\soulskills\melinoe_bloodboil.dbr'
_SS_GROUND_SMASH = r'records\skills\soulskills\cyclops_groundsmash.dbr'
_SS_VENOM_SPRAY = r'records\skills\soulskills\arachne_venomspray.dbr'
_SS_FLASH_POWDER = r'records\skills\soulskills\toxeus_flashpowder.dbr'
_SS_ZOMBIE_SUMMON = r'records\skills\soulskills\summon_zombiesoldier.dbr'
_SS_FIRE_NOVA = r'records\skills\soulskills\firefragmentnova.dbr'
_SS_SONIC_WAVE = r'records\skills\soulskills\hero_sonicwave.dbr'
_SS_HARPY_AURA = r'records\skills\soulskills\harpy_lightningaura.dbr'
_SS_LIFE_DRAIN = r'records\skills\spirit\lifedrain.dbr'
_SS_NESSUS_ENDURANCE = r'records\skills\soulskills\nessus_enduranceaura.dbr'


def _create_sp_toxeus_soul(db):
    """SP Toxeus (um_toxeus_99) — Tier 1: THE strongest soul in the game.

    Dream/Rogue assassin hybrid. Phantom Strike teleport, Distortion Wave,
    Distort Reality (phys + life + electrocution), extreme dodge and deflect.
    Level 33/66/99.  Must surpass Canace (current #1 soul).
    """
    MONSTER = r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr'
    TAG = 'tagSVCSoulSPToxeus'

    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = [
        {'diff': 'n', 'itemLevel': 33, 'stats': {
            # Proc: Ring of Lightning on hit (electrocution from Distortion Wave)
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            # Augments: Dream mastery — his signature moves
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 3),
            # Offensive: physical + life + electrocution (Distort Reality profile)
            'offensivePhysicalMin': (F, 50.0), 'offensivePhysicalMax': (F, 80.0),
            'offensiveLifeMin': (F, 35.0), 'offensiveLifeMax': (F, 55.0),
            'offensiveSlowLightningMin': (F, 80.0),
            'offensiveSlowLightningDurationMin': (F, 4.0),
            'offensivePhysicalModifier': (I, 30),
            'offensiveLifeModifier': (I, 25),
            'offensivePierceRatioModifier': (I, 15),
            'offensiveLifeLeechMin': (F, 35.0),
            'offensivePercentCurrentLifeMin': (F, 5.0),
            # Defensive (moderate — monster equips this soul too!)
            'characterDodgePercent': (F, 10.0),
            'characterDeflectProjectile': (F, 10.0),
            'defensiveLife': (F, 12.0),
            'characterEnergyAbsorptionPercent': (F, 15.0),
            # Speed (assassin)
            'characterAttackSpeedModifier': (I, 12),
            'characterTotalSpeedModifier': (I, 8),
            'characterRunSpeedModifier': (F, 10.0),
            # % Stats
            'characterLifeModifier': (F, 8.0),
            'characterManaModifier': (F, 8.0),
            'characterStrengthModifier': (F, 6.0),
            'characterDexterityModifier': (F, 8.0),
            'characterIntelligenceModifier': (F, 5.0),
            'characterOffensiveAbilityModifier': (F, 6.0),
            'characterDefensiveAbilityModifier': (F, 5.0),
            # Reflect + Armor (monster equips this — countered by absorption/resistances)
            'defensiveReflect': (F, 8.0),
            'defensiveProtectionModifier': (F, 8.0),
        }},
        {'diff': 'e', 'itemLevel': 66, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE),
            'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 4),
            'offensivePhysicalMin': (F, 90.0), 'offensivePhysicalMax': (F, 140.0),
            'offensiveLifeMin': (F, 60.0), 'offensiveLifeMax': (F, 100.0),
            'offensiveSlowLightningMin': (F, 150.0),
            'offensiveSlowLightningDurationMin': (F, 4.0),
            'offensivePhysicalModifier': (I, 55),
            'offensiveLifeModifier': (I, 45),
            'offensivePierceRatioModifier': (I, 22),
            'offensiveLifeLeechMin': (F, 60.0),
            'offensivePercentCurrentLifeMin': (F, 8.0),
            'characterDodgePercent': (F, 14.0),
            'characterDeflectProjectile': (F, 15.0),
            'defensiveLife': (F, 18.0),
            'characterEnergyAbsorptionPercent': (F, 25.0),
            'characterAttackSpeedModifier': (I, 16),
            'characterTotalSpeedModifier': (I, 12),
            'characterRunSpeedModifier': (F, 15.0),
            'characterLifeModifier': (F, 14.0),
            'characterManaModifier': (F, 14.0),
            'characterStrengthModifier': (F, 10.0),
            'characterDexterityModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterOffensiveAbilityModifier': (F, 10.0),
            'characterDefensiveAbilityModifier': (F, 8.0),
            'defensiveReflect': (F, 15.0),
            'defensiveProtectionModifier': (F, 12.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE),
            'augmentSkillLevel1': (I, 6),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 5),
            # Massive offensive: phys + life + electrocution
            'offensivePhysicalMin': (F, 140.0), 'offensivePhysicalMax': (F, 210.0),
            'offensiveLifeMin': (F, 95.0), 'offensiveLifeMax': (F, 150.0),
            'offensiveSlowLightningMin': (F, 240.0),
            'offensiveSlowLightningDurationMin': (F, 4.0),
            'offensivePhysicalModifier': (I, 85),
            'offensiveLifeModifier': (I, 70),
            'offensivePierceRatioModifier': (I, 30),
            'offensiveLifeLeechMin': (F, 90.0),
            'offensivePercentCurrentLifeMin': (F, 12.0),
            # Evasion (moderate — monster equips this!)
            'characterDodgePercent': (F, 18.0),
            'characterDeflectProjectile': (F, 22.0),
            'defensiveLife': (F, 25.0),
            'characterEnergyAbsorptionPercent': (F, 35.0),
            'defensiveManaBurnRatio': (F, 40.0),
            # Assassin speed
            'characterAttackSpeedModifier': (I, 20),
            'characterTotalSpeedModifier': (I, 16),
            'characterRunSpeedModifier': (F, 20.0),
            # % Stats (Tier 1 — strongest in game)
            'characterLifeModifier': (F, 20.0),
            'characterManaModifier': (F, 20.0),
            'characterStrengthModifier': (F, 15.0),
            'characterDexterityModifier': (F, 18.0),
            'characterIntelligenceModifier': (F, 12.0),
            'characterOffensiveAbilityModifier': (F, 15.0),
            'characterDefensiveAbilityModifier': (F, 10.0),
            # Reflect + Armor (monster equips this — countered by absorption/resistances)
            'defensiveReflect': (F, 25.0),
            'defensiveProtectionModifier': (F, 16.0),
        }},
    ]

    paths = _create_soul(db, 'sp_toxeus', TAG, tiers, MONSTER, 66.0)
    print(f"  SP Toxeus soul created (Tier 1 — Dream/Rogue assassin, 66% drop)")
    return paths


def _overhaul_main_toxeus_soul(db):
    """Main Toxeus (um_toxeus_21) — Tier 3: massively boost existing soul.

    Rogue/Warfare hybrid. Bladestorm, Flash Powder, Lethal Strike, Envenom
    Weapon, Shield Charge.  Keeps Flash Powder proc + Lethal Strike/Battle
    Rage augments from original soul but with much stronger stats.
    Level 25/45/65.
    """
    # Existing souls at records\item\equipmentring\soul\skeleton\toxeus_soul_*.dbr
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = {
        'n': {
            'itemSkillLevel': (I, 6),  # boost Flash Powder proc
            'augmentSkillLevel1': (I, 5),  # Lethal Strike
            'augmentSkillLevel2': (I, 5),  # Battle Rage
            # Massive physical + pierce + bleed (Bladestorm profile)
            'offensivePhysicalMin': (F, 55.0), 'offensivePhysicalMax': (F, 75.0),
            'offensivePierceMin': (F, 30.0),
            'offensivePierceRatioModifier': (I, 40),
            'offensivePhysicalModifier': (I, 30),
            'offensiveSlowBleedingMin': (F, 80.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            # Envenom weapon theme
            'offensiveSlowPoisonMin': (F, 35.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowTotalSpeedMin': (F, 10.0),
            'offensiveSlowTotalSpeedDurationMin': (F, 3.0),
            # Speed & evasion
            'characterAttackSpeedModifier': (F, 12.0),
            'characterTotalSpeedModifier': (I, 10),
            'characterRunSpeedModifier': (F, 8.0),
            'characterDodgePercent': (F, 8.0),
            'characterDeflectProjectile': (F, 8.0),
            # % Stats (favor modifiers)
            'characterOffensiveAbilityModifier': (F, 4.0),
            'characterDefensiveAbilityModifier': (F, 4.0),
            'characterLifeModifier': (F, 6.0),
            'characterStrengthModifier': (F, 5.0), 'characterDexterityModifier': (F, 6.0),
            'defensiveReflect': (F, 12.0),
            'defensiveProtectionModifier': (F, 8.0),
            'defensivePierce': (F, 20.0),
            'characterEnergyAbsorptionPercent': (F, 15.0),
            'racialBonusPercentDamage': (F, 40.0),  # vs Undead
        },
        'e': {
            'itemSkillLevel': (I, 10),
            'augmentSkillLevel1': (I, 6),
            'augmentSkillLevel2': (I, 6),
            'offensivePhysicalMin': (F, 80.0), 'offensivePhysicalMax': (F, 110.0),
            'offensivePierceMin': (F, 45.0),
            'offensivePierceRatioModifier': (I, 60),
            'offensivePhysicalModifier': (I, 50),
            'offensiveSlowBleedingMin': (F, 130.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowPoisonMin': (F, 55.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowTotalSpeedMin': (F, 15.0),
            'offensiveSlowTotalSpeedDurationMin': (F, 3.0),
            'characterAttackSpeedModifier': (F, 16.0),
            'characterTotalSpeedModifier': (I, 14),
            'characterRunSpeedModifier': (F, 11.0),
            'characterDodgePercent': (F, 11.0),
            'characterDeflectProjectile': (F, 12.0),
            'characterOffensiveAbilityModifier': (F, 6.0),
            'characterDefensiveAbilityModifier': (F, 6.0),
            'characterLifeModifier': (F, 10.0),
            'characterStrengthModifier': (F, 8.0), 'characterDexterityModifier': (F, 10.0),
            'defensiveReflect': (F, 16.0),
            'defensiveProtectionModifier': (F, 12.0),
            'defensivePierce': (F, 30.0),
            'characterEnergyAbsorptionPercent': (F, 22.0),
            'racialBonusPercentDamage': (F, 55.0),
        },
        'l': {
            'itemSkillLevel': (I, 14),
            'augmentSkillLevel1': (I, 8),
            'augmentSkillLevel2': (I, 7),
            'offensivePhysicalMin': (F, 120.0), 'offensivePhysicalMax': (F, 160.0),
            'offensivePierceMin': (F, 65.0),
            'offensivePierceRatioModifier': (I, 80),
            'offensivePhysicalModifier': (I, 75),
            'offensiveSlowBleedingMin': (F, 190.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowPoisonMin': (F, 80.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowTotalSpeedMin': (F, 20.0),
            'offensiveSlowTotalSpeedDurationMin': (F, 4.0),
            'characterAttackSpeedModifier': (F, 20.0),
            'characterTotalSpeedModifier': (I, 18),
            'characterRunSpeedModifier': (F, 14.0),
            'characterDodgePercent': (F, 14.0),
            'characterDeflectProjectile': (F, 16.0),
            'characterOffensiveAbilityModifier': (F, 8.0),
            'characterDefensiveAbilityModifier': (F, 8.0),
            'characterLifeModifier': (F, 15.0),
            'characterStrengthModifier': (F, 12.0), 'characterDexterityModifier': (F, 14.0),
            'defensiveReflect': (F, 20.0),
            'defensiveProtectionModifier': (F, 16.0),
            'defensivePierce': (F, 40.0),
            'characterEnergyAbsorptionPercent': (F, 30.0),
            'racialBonusPercentDamage': (F, 70.0),
        },
    }

    total = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'toxeus_soul' not in nl or 'equipmentring' not in nl:
            continue
        if 'sp_toxeus' in nl:
            continue  # skip our new SP soul
        for diff, stats in tiers.items():
            if f'_soul_{diff}.dbr' in nl:
                _set_soul_fields(db, name, stats)
                total += 1
                break

    print(f"  Main Toxeus soul overhauled ({total} records — Tier 3 rogue/warrior)")
    return total


def _create_leinth_soul(db):
    """Leinth the Blood Witch — blood/life/bleed caster boss.

    Blood Boil AoE (life leech), ranged bleed projectiles, summon minions,
    geyser poison, heatseeker pets.  Olympian race.  Poison weakness.
    Level 47-50 / 62-65 / 74-76.
    """
    # Wire to all 3 Leinth variants
    MONSTERS = [
        r'records\drxcreatures\bloodwitch\q_leinth_47.dbr',
        r'records\drxcreatures\bloodwitch\q_leinth_49.dbr',
        r'records\drxcreatures\bloodwitch\q_leinth_50.dbr',
    ]
    TAG = 'tagSVCSoulLeinth'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 47, 'stats': {
            # Proc: Blood Boil on hit (her SIGNATURE attack)
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            # Augments: Dark Covenant + Plague (summoner/caster)
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 2),
            # Life damage + bleed (blood witch theme)
            'offensiveLifeMin': (F, 30.0), 'offensiveLifeMax': (F, 50.0),
            'offensiveLifeModifier': (I, 20),
            'offensiveSlowBleedingMin': (F, 55.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 25),
            'offensiveLifeLeechMin': (F, 25.0),
            # % Stats (caster)
            'characterLifeModifier': (F, 8.0), 'characterManaModifier': (F, 8.0),
            'characterIntelligenceModifier': (F, 5.0),
            'characterSpellCastSpeedModifier': (I, 12),
            'characterManaRegenModifier': (I, 15),
            'defensiveLife': (F, 15.0),
            'defensiveBleeding': (F, 15.0),
            'defensivePoison': (F, -8.0),  # her weakness carried over
        }},
        {'diff': 'e', 'itemLevel': 62, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 5),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 3),
            'offensiveLifeMin': (F, 55.0), 'offensiveLifeMax': (F, 85.0),
            'offensiveLifeModifier': (I, 35),
            'offensiveSlowBleedingMin': (F, 95.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 40),
            'offensiveLifeLeechMin': (F, 40.0),
            'characterLifeModifier': (F, 12.0), 'characterManaModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterSpellCastSpeedModifier': (I, 20),
            'characterManaRegenModifier': (I, 22),
            'defensiveLife': (F, 22.0),
            'defensiveBleeding': (F, 20.0),
            'defensivePoison': (F, -8.0),
        }},
        {'diff': 'l', 'itemLevel': 74, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 7),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 4),
            'offensiveLifeMin': (F, 85.0), 'offensiveLifeMax': (F, 130.0),
            'offensiveLifeModifier': (I, 55),
            'offensiveSlowBleedingMin': (F, 145.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 60),
            'offensiveLifeLeechMin': (F, 60.0),
            'characterLifeModifier': (F, 18.0), 'characterManaModifier': (F, 16.0),
            'characterIntelligenceModifier': (F, 12.0),
            'characterSpellCastSpeedModifier': (I, 28),
            'characterManaRegenModifier': (I, 30),
            'defensiveLife': (F, 30.0),
            'defensiveBleeding': (F, 28.0),
            'defensivePoison': (F, -8.0),
        }},
    ]

    paths = _create_soul(db, 'leinth', TAG, tiers)
    # Wire to all 3 Leinth variants
    for m in MONSTERS:
        if db.has_record(m):
            db.set_field(m, 'lootFinger2Item1', paths, DATA_TYPE_STRING)
            db.set_field(m, 'chanceToEquipFinger2', 66.0, DATA_TYPE_FLOAT)
            db.set_field(m, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
            db._modified.add(m)
    print(f"  Leinth soul created (blood witch — life/bleed, 66% drop, 3 variants)")
    return paths


def _create_murder_bunny_soul(db):
    """Murder Bunny — Tier 2: endgame uber boss.

    275K HP ambush boss.  Egg bomb spawns + larvae, sandblast pierce+slow,
    massive physical damage (+375 at L), fire retaliation, dodge behavior.
    Level 66/79/99.
    """
    MONSTER = r'records\drxcreatures\crowheroes\murderbunny.dbr'
    TAG = 'tagSVCSoulMurderBunny'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 66, 'stats': {
            # Proc: Ground Smash on attack (physical devastation)
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillLevel': (I, 5),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            # Augments: Onslaught + Lethal Strike (raw killing power)
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE),
            'augmentSkillLevel2': (I, 3),
            # Massive physical + pierce (sandblast + melee theme)
            'offensivePhysicalMin': (F, 80.0), 'offensivePhysicalMax': (F, 130.0),
            'offensivePierceMin': (F, 40.0), 'offensivePierceMax': (F, 65.0),
            'offensivePhysicalModifier': (I, 45),
            'offensivePierceRatioModifier': (I, 18),
            'offensiveSlowBleedingMin': (F, 50.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            # Fire retaliation (his fire retaliation passive)
            'retaliationFireMin': (F, 30.0), 'retaliationFireMax': (F, 50.0),
            # Speed + dodge (ambush hunter)
            'characterAttackSpeedModifier': (I, 14),
            'characterRunSpeedModifier': (F, 10.0),
            'characterDodgePercent': (F, 8.0),
            # % Stats
            'characterLifeModifier': (F, 12.0), 'characterManaModifier': (F, 6.0),
            'characterStrengthModifier': (F, 6.0), 'characterDexterityModifier': (F, 8.0),
            'characterOffensiveAbilityModifier': (F, 6.0),
            'defensivePierce': (F, 25.0),
        }},
        {'diff': 'e', 'itemLevel': 79, 'stats': {
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE),
            'augmentSkillLevel2': (I, 4),
            'offensivePhysicalMin': (F, 130.0), 'offensivePhysicalMax': (F, 200.0),
            'offensivePierceMin': (F, 65.0), 'offensivePierceMax': (F, 100.0),
            'offensivePhysicalModifier': (I, 70),
            'offensivePierceRatioModifier': (I, 25),
            'offensiveSlowBleedingMin': (F, 85.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'retaliationFireMin': (F, 50.0), 'retaliationFireMax': (F, 80.0),
            'characterAttackSpeedModifier': (I, 18),
            'characterRunSpeedModifier': (F, 14.0),
            'characterDodgePercent': (F, 12.0),
            'characterLifeModifier': (F, 18.0), 'characterManaModifier': (F, 10.0),
            'characterStrengthModifier': (F, 10.0), 'characterDexterityModifier': (F, 12.0),
            'characterOffensiveAbilityModifier': (F, 8.0),
            'defensivePierce': (F, 35.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 6),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE),
            'augmentSkillLevel2': (I, 5),
            # Devastating physical + pierce
            'offensivePhysicalMin': (F, 190.0), 'offensivePhysicalMax': (F, 280.0),
            'offensivePierceMin': (F, 95.0), 'offensivePierceMax': (F, 145.0),
            'offensivePhysicalModifier': (I, 100),
            'offensivePierceRatioModifier': (I, 32),
            'offensiveSlowBleedingMin': (F, 130.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'retaliationFireMin': (F, 75.0), 'retaliationFireMax': (F, 120.0),
            # Ambush predator
            'characterAttackSpeedModifier': (I, 22),
            'characterRunSpeedModifier': (F, 18.0),
            'characterDodgePercent': (F, 16.0),
            'characterLifeModifier': (F, 25.0), 'characterManaModifier': (F, 14.0),
            'characterStrengthModifier': (F, 14.0), 'characterDexterityModifier': (F, 16.0),
            'characterOffensiveAbilityModifier': (F, 10.0),
            'defensivePierce': (F, 45.0),
        }},
    ]

    paths = _create_soul(db, 'murderbunny', TAG, tiers, MONSTER, 66.0)
    print(f"  Murder Bunny soul created (Tier 2 — physical devastation, 66% drop)")
    return paths


def _create_sp_hades_soul(db):
    """SP Hades — Tier 2: shadow god, stronger than main Hades soul.

    Uses Form 1 mesh/skills.  Sickle Sweep (massive phys + life damage),
    Shadow Bolt, Shadow Star.  Custom enrage regen passive.  Transforms
    on death to Form 2.  Level 57/71/80.
    """
    MONSTER = r'records\drxcreatures\bloodwitch\boss_hades_54.dbr'
    TAG = 'tagSVCSoulSPHades'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 57, 'stats': {
            # Proc: Blood Boil on attack (death god — life drain AoE)
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            # Augments: Death Chill Aura + Ternion Attack (Spirit mastery)
            'augmentSkillName1': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_TERNION),
            'augmentSkillLevel2': (I, 3),
            # Life + physical (sickle sweep profile)
            'offensiveLifeMin': (F, 50.0), 'offensiveLifeMax': (F, 80.0),
            'offensivePhysicalMin': (F, 40.0), 'offensivePhysicalMax': (F, 65.0),
            'offensiveLifeModifier': (I, 30),
            'offensivePercentCurrentLifeMin': (F, 5.0),
            'offensiveLifeLeechMin': (F, 30.0),
            # Resistance reduction (shadow bolt slow)
            'offensiveTotalResistanceReductionAbsoluteMin': (F, 12.0),
            'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, 3.0),
            # Dark god % stats
            'characterLifeModifier': (F, 10.0), 'characterManaModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 6.0),
            'characterSpellCastSpeedModifier': (I, 22),
            'characterDefensiveAbilityModifier': (F, 6.0),
            'defensiveLife': (F, 20.0),
            'defensiveFire': (F, 12.0), 'defensiveLightning': (F, 12.0),
            'defensiveProtectionModifier': (F, 8.0),
        }},
        {'diff': 'e', 'itemLevel': 71, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_TERNION),
            'augmentSkillLevel2': (I, 4),
            'offensiveLifeMin': (F, 85.0), 'offensiveLifeMax': (F, 130.0),
            'offensivePhysicalMin': (F, 65.0), 'offensivePhysicalMax': (F, 100.0),
            'offensiveLifeModifier': (I, 50),
            'offensivePercentCurrentLifeMin': (F, 8.0),
            'offensiveLifeLeechMin': (F, 50.0),
            'offensiveTotalResistanceReductionAbsoluteMin': (F, 20.0),
            'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, 3.0),
            'characterLifeModifier': (F, 16.0), 'characterManaModifier': (F, 18.0),
            'characterIntelligenceModifier': (F, 10.0),
            'characterSpellCastSpeedModifier': (I, 35),
            'characterDefensiveAbilityModifier': (F, 8.0),
            'defensiveLife': (F, 30.0),
            'defensiveFire': (F, 18.0), 'defensiveLightning': (F, 18.0),
            'defensiveProtectionModifier': (F, 14.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _SK_TERNION),
            'augmentSkillLevel2': (I, 5),
            # Massive life + physical (god of death)
            'offensiveLifeMin': (F, 130.0), 'offensiveLifeMax': (F, 195.0),
            'offensivePhysicalMin': (F, 100.0), 'offensivePhysicalMax': (F, 150.0),
            'offensiveLifeModifier': (I, 75),
            'offensivePercentCurrentLifeMin': (F, 12.0),
            'offensiveLifeLeechMin': (F, 75.0),
            # Shadow resistance shred
            'offensiveTotalResistanceReductionAbsoluteMin': (F, 30.0),
            'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, 3.0),
            # Dark overlord % stats
            'characterLifeModifier': (F, 22.0), 'characterManaModifier': (F, 25.0),
            'characterIntelligenceModifier': (F, 14.0),
            'characterSpellCastSpeedModifier': (I, 48),
            'characterDefensiveAbilityModifier': (F, 12.0),
            'defensiveLife': (F, 42.0),
            'defensiveFire': (F, 25.0), 'defensiveLightning': (F, 25.0),
            'defensiveProtectionModifier': (F, 20.0),
        }},
    ]

    paths = _create_soul(db, 'sp_hades', TAG, tiers, MONSTER, 66.0)
    print(f"  SP Hades soul created (Tier 2 — shadow/life, 66% drop)")
    return paths


def _create_dagon_soul(db):
    """Dagon — deep sea lord, ichthian boss.

    Super Bite (462-2214 poison DoT!), Tidal Wave, Mudstorm, Shadow Star,
    Poison Cloud on death.  100% poison immune.  Level 50/65/80.
    """
    MONSTER = r'records\test\boss_dagon_66.dbr'
    TAG = 'tagSVCSoulDagon'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    tiers = [
        {'diff': 'n', 'itemLevel': 50, 'stats': {
            # Proc: Venom Spray on attack (ichthian poison theme)
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            # Augments: Envenom Weapon + Plague
            'augmentSkillName1': (S, _SK_ENVENOM),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 2),
            # Massive poison (Super Bite theme)
            'offensiveSlowPoisonMin': (F, 100.0), 'offensiveSlowPoisonMax': (F, 160.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveSlowPoisonModifier': (I, 25),
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 35.0),
            'offensiveColdMin': (F, 10.0), 'offensiveColdMax': (F, 20.0),
            # % Stats
            'characterLifeModifier': (F, 8.0), 'characterManaModifier': (F, 6.0),
            'characterStrengthModifier': (F, 4.0), 'characterDexterityModifier': (F, 4.0),
            'characterAttackSpeedModifier': (I, 8),
            'defensivePoison': (F, 30.0),
            'defensiveCold': (F, 15.0),
        }},
        {'diff': 'e', 'itemLevel': 65, 'stats': {
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ENVENOM),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 3),
            'offensiveSlowPoisonMin': (F, 180.0), 'offensiveSlowPoisonMax': (F, 280.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveSlowPoisonModifier': (I, 40),
            'offensivePhysicalMin': (F, 35.0), 'offensivePhysicalMax': (F, 55.0),
            'offensiveColdMin': (F, 18.0), 'offensiveColdMax': (F, 30.0),
            'characterLifeModifier': (F, 12.0), 'characterManaModifier': (F, 10.0),
            'characterStrengthModifier': (F, 6.0), 'characterDexterityModifier': (F, 5.0),
            'characterAttackSpeedModifier': (I, 12),
            'defensivePoison': (F, 42.0),
            'defensiveCold': (F, 22.0),
        }},
        {'diff': 'l', 'itemLevel': 80, 'stats': {
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ENVENOM),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 4),
            # Devastating poison (Super Bite = 2214 poison at max)
            'offensiveSlowPoisonMin': (F, 280.0), 'offensiveSlowPoisonMax': (F, 420.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveSlowPoisonModifier': (I, 60),
            'offensivePhysicalMin': (F, 55.0), 'offensivePhysicalMax': (F, 80.0),
            'offensiveColdMin': (F, 28.0), 'offensiveColdMax': (F, 42.0),
            'characterLifeModifier': (F, 18.0), 'characterManaModifier': (F, 14.0),
            'characterStrengthModifier': (F, 8.0), 'characterDexterityModifier': (F, 7.0),
            'characterAttackSpeedModifier': (I, 15),
            'defensivePoison': (F, 55.0),
            'defensiveCold': (F, 30.0),
        }},
    ]

    paths = _create_soul(db, 'dagon', TAG, tiers, MONSTER, 66.0)
    print(f"  Dagon soul created (deep sea poison lord, 66% drop)")
    return paths


def _create_dev_skeleton_souls(db):
    """Create souls for 15 developer-named Secret Passage skeletons.

    Each soul is themed to match the skeleton's creature mesh and skills.
    Quest class, Level 40/56/71.
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # (record_path, soul_base_name, tag, theme_proc, theme_augment1, theme_augment2,
    #  element_stats for L tier — N/E scaled at 0.6x/0.8x)
    DEV_SKELETONS = [
        # z_arthur — Satyr, spawns z_toxeus on death. Dream theme (Toxeus connection).
        (r'records\xpack\creatures\monster\zzdev\z_arthur.dbr', 'z_arthur',
         'tagSVCSoulDevArthur', _SS_RING_LIGHTNING, _SK_PHANTOM_STRIKE, _SK_DISTORTION_WAVE,
         {'offensivePhysicalMin': 45.0, 'offensivePhysicalMax': 70.0,
          'offensiveSlowLightningMin': 40.0, 'offensiveSlowLightningDurationMin': 3.0,
          'characterStrengthModifier': 6.0, 'characterLifeModifier': 8.0, 'characterDexterityModifier': 6.0}),
        # z_ben — Anteok with club, barb flurry, groundbreaker, mass heal. Tank/healer.
        (r'records\xpack\creatures\monster\zzdev\z_ben.dbr', 'z_ben',
         'tagSVCSoulDevBen', _SS_NESSUS_ENDURANCE, _SK_HEART_OF_OAK, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 65.0, 'offensivePhysicalMax': 95.0,
          'characterStrengthModifier': 10.0, 'characterLifeModifier': 14.0, 'characterLifeRegen': 5.0}),
        # z_chooch — Skeletal Typhon. Bone shards, bone spire, bone trap, spirit breath.
        (r'records\xpack\creatures\monster\zzdev\z_chooch.dbr', 'z_chooch',
         'tagSVCSoulDevChooch', _SS_GROUND_SMASH, _SK_DEATH_CHILL, _SK_DARK_COVENANT,
         {'offensivePhysicalMin': 50.0, 'offensivePhysicalMax': 75.0,
          'offensiveLifeMin': 30.0, 'offensiveLifeMax': 50.0,
          'characterLifeModifier': 10.0, 'characterIntelligenceModifier': 7.0, 'defensiveLife': 20.0}),
        # z_cory — Siege Walker. Turret attack, fire spit.
        (r'records\xpack\creatures\monster\zzdev\z_cory.dbr', 'z_cory',
         'tagSVCSoulDevCory', r'records\skills\soulskills\firefragmentnova.dbr',
         r'records\skills\earth\drxfireenchantment.dbr', r'records\skills\earth\drxringofflame.dbr',
         {'offensiveFireMin': 45.0, 'offensiveFireMax': 70.0,
          'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0,
          'characterLifeModifier': 14.0, 'characterStrengthModifier': 7.0, 'defensiveFire': 25.0}),
        # z_dave — Satyr with Heart of Oak. Nature/physical.
        (r'records\xpack\creatures\monster\zzdev\z_dave.dbr', 'z_dave',
         'tagSVCSoulDevDave', _SS_GROUND_SMASH, r'records\skills\nature\drxheartofoak.dbr',
         _SK_PLAGUE,
         {'offensivePhysicalMin': 50.0, 'offensivePhysicalMax': 72.0,
          'characterLifeModifier': 10.0, 'characterStrengthModifier': 7.0, 'characterLifeRegen': 4.0}),
        # z_david — Skeleton. Study Prey, Ensnare + Barbed Netting. Rogue theme.
        (r'records\xpack\creatures\monster\zzdev\z_david.dbr', 'z_david',
         'tagSVCSoulDevDavid', _SS_FLASH_POWDER, _SK_LETHAL_STRIKE, _SK_ENVENOM,
         {'offensivePierceMin': 40.0, 'offensivePierceMax': 60.0,
          'offensivePhysicalMin': 30.0, 'characterDexterityModifier': 8.0,
          'characterLifeModifier': 8.0, 'characterAttackSpeedModifier': 12.0}),
        # z_frazier — Satyr, rogue theme. Flash Powder blind + poison.
        (r'records\xpack\creatures\monster\zzdev\z_frazier.dbr', 'z_frazier',
         'tagSVCSoulDevFrazier', _SS_FLASH_POWDER, _SK_LETHAL_STRIKE, _SK_ENVENOM,
         {'offensivePierceMin': 35.0, 'offensivePierceMax': 55.0,
          'offensiveSlowPoisonMin': 30.0, 'offensiveSlowPoisonDurationMin': 3.0,
          'characterDexterityModifier': 8.0, 'characterLifeModifier': 8.0, 'characterAttackSpeedModifier': 10.0}),
        # z_josh — Satyr, basic.
        (r'records\xpack\creatures\monster\zzdev\z_josh.dbr', 'z_josh',
         'tagSVCSoulDevJosh', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_DUAL_WEAPON,
         {'offensivePhysicalMin': 48.0, 'offensivePhysicalMax': 70.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'characterDexterityModifier': 6.0}),
        # z_morgan — HYDRA. Fire/cold/poison breath. Most complex dev skeleton.
        (r'records\xpack\creatures\monster\zzdev\z_morgan.dbr', 'z_morgan',
         'tagSVCSoulDevMorgan', r'records\skills\soulskills\firefragmentnova.dbr',
         _SK_COLD_AURA, _SK_PLAGUE,
         {'offensiveFireMin': 35.0, 'offensiveFireMax': 55.0,
          'offensiveColdMin': 30.0, 'offensiveColdMax': 48.0,
          'offensiveSlowPoisonMin': 60.0, 'offensiveSlowPoisonDurationMin': 3.0,
          'characterLifeModifier': 14.0, 'characterIntelligenceModifier': 8.0,
          'defensiveFire': 20.0, 'defensiveCold': 20.0, 'defensivePoison': 20.0}),
        # z_nate — Satyr, warfare bruiser. Sonic Wave proc + crushing power.
        (r'records\xpack\creatures\monster\zzdev\z_nate.dbr', 'z_nate',
         'tagSVCSoulDevNate', _SS_SONIC_WAVE, _SK_ONSLAUGHT, _SK_BATTLE_RAGE,
         {'offensivePhysicalMin': 55.0, 'offensivePhysicalMax': 82.0,
          'offensiveStunMin': 0.5, 'offensiveStunMax': 1.5, 'offensiveStunChance': 10.0,
          'characterStrengthModifier': 8.0, 'characterLifeModifier': 10.0}),
        # z_parnell — Odontotyrannus. Lightning beast, sonic wave + storm.
        (r'records\xpack\creatures\monster\zzdev\z_parnell.dbr', 'z_parnell',
         'tagSVCSoulDevParnell', _SS_HARPY_AURA, _SK_STORM_NIMBUS, _SK_CHAIN_LIGHTNING,
         {'offensivePhysicalMin': 50.0, 'offensivePhysicalMax': 75.0,
          'offensiveLightningMin': 30.0, 'offensiveLightningMax': 50.0,
          'characterStrengthModifier': 8.0, 'characterLifeModifier': 12.0, 'defensiveLightning': 15.0}),
        # z_scott — Satyr, fire theme. Fire nova retaliation.
        (r'records\xpack\creatures\monster\zzdev\z_scott.dbr', 'z_scott',
         'tagSVCSoulDevScott', _SS_FIRE_NOVA, _SK_FIRE_ENCHANT, _SK_ONSLAUGHT,
         {'offensiveFireMin': 35.0, 'offensiveFireMax': 55.0,
          'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 40.0,
          'characterStrengthModifier': 7.0, 'characterLifeModifier': 9.0, 'defensiveFire': 15.0}),
        # z_shawn — Satyr, lower HP (3000).
        (r'records\xpack\creatures\monster\zzdev\z_shawn.dbr', 'z_shawn',
         'tagSVCSoulDevShawn', _SS_GROUND_SMASH, _SK_ONSLAUGHT, _SK_LETHAL_STRIKE,
         {'offensivePhysicalMin': 42.0, 'offensivePhysicalMax': 62.0,
          'characterDexterityModifier': 8.0, 'characterLifeModifier': 7.0, 'characterAttackSpeedModifier': 10.0}),
        # z_tom — Satyr, spirit/life drain theme.
        (r'records\xpack\creatures\monster\zzdev\z_tom.dbr', 'z_tom',
         'tagSVCSoulDevTom', _SS_BLOOD_BOIL, _SK_DEATH_CHILL, _SK_DARK_COVENANT,
         {'offensiveLifeMin': 25.0, 'offensiveLifeMax': 42.0,
          'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 48.0,
          'offensiveLifeLeechMin': 15.0,
          'characterIntelligenceModifier': 7.0, 'characterLifeModifier': 9.0, 'defensiveLife': 15.0}),
        # z_~v~ — Nightmare. Dream/psionic. Psionic Beam, Hypnotic Gaze, Dream Surge.
        (r'records\xpack\creatures\monster\zzdev\z_~v~.dbr', 'z_tildavtilde',
         'tagSVCSoulDevTildaV', _SS_RING_LIGHTNING, _SK_PHANTOM_STRIKE, _SK_DISTORTION_WAVE,
         {'offensiveLightningMin': 40.0, 'offensiveLightningMax': 65.0,
          'offensiveLifeMin': 25.0, 'offensiveLifeMax': 40.0,
          'characterIntelligenceModifier': 10.0, 'characterManaModifier': 10.0, 'characterLifeModifier': 10.0,
          'characterSpellCastSpeedModifier': 15.0, 'defensiveLife': 18.0}),
    ]

    total = 0
    for record, base_name, tag, proc, aug1, aug2, l_stats in DEV_SKELETONS:
        if not db.has_record(record):
            continue

        # Build per-tier stats from L stats with 0.6x/0.8x scaling
        def _scale(stats_dict, factor):
            scaled = {}
            for k, v in stats_dict.items():
                if isinstance(v, float):
                    scaled[k] = round(v * factor, 1)
                elif isinstance(v, int):
                    scaled[k] = max(0, int(v * factor)) if v >= 0 else int(v * factor)
            return scaled

        n_stats = _scale(l_stats, 0.6)
        e_stats = _scale(l_stats, 0.8)

        def _typed(stats_dict):
            typed = {}
            for k, v in stats_dict.items():
                if isinstance(v, float):
                    typed[k] = (F, v)
                else:
                    typed[k] = (I, v)
            return typed

        common_skills = {
            'itemSkillName': (S, proc), 'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, aug1), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, aug2), 'augmentSkillLevel2': (I, 2),
        }
        n_skills = dict(common_skills)
        n_skills['itemSkillLevel'] = (I, 2)
        n_skills['augmentSkillLevel1'] = (I, 1)
        n_skills['augmentSkillLevel2'] = (I, 1)
        e_skills = dict(common_skills)
        e_skills['itemSkillLevel'] = (I, 2)

        tiers = [
            {'diff': 'n', 'itemLevel': 40, 'stats': {**n_skills, **_typed(n_stats)}},
            {'diff': 'e', 'itemLevel': 56, 'stats': {**e_skills, **_typed(e_stats)}},
            {'diff': 'l', 'itemLevel': 71, 'stats': {**common_skills, **_typed(l_stats)}},
        ]

        # These Secret-Passage dev skeletons are intended soul-droppers. 17 of the
        # 18 ship as monsterClassification=Quest in the base data; only z_~v~
        # shipped as Champion, which the soul-drop gate rejects (non-Hero/Boss/
        # Quest) - so its wired soul would leak a drop in BOTH release (66%) and
        # testing (100%). Force Quest here so every dev skeleton is uniformly a
        # gated, intended dropper. Only raises a non-gated class; never demotes a
        # Boss/Hero (none here are).
        _mc = db.get_field_value(record, 'monsterClassification')
        if _mc not in ('Hero', 'Boss', 'Quest'):
            db.set_field(record, 'monsterClassification', 'Quest', DATA_TYPE_STRING)
            db._modified.add(record)
            print(f"    dev skeleton {base_name}: promoted classification "
                  f"{_mc!r} -> 'Quest' (soul-dropper gate)")

        _create_soul(db, base_name, tag, tiers, record, 66.0)
        total += 1

    print(f"  Developer skeleton souls created: {total} (Secret Passage, 66% drop each)")
    return total


def _overhaul_melalos_soul(db):
    """Overhaul Melalos (um_melalos_19) — Greece cave zombie boss.

    Summons zombies, plague bolts, rotten grasp, weakening strike.
    Original soul is a weak stat-stick at 5% drop.  Add zombie summon proc,
    plague/death augments, boost stats and drop rate to 25%.
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = {
        'n': {
            'itemSkillName': (S, _SS_ZOMBIE_SUMMON),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 2),
            # Poison/life damage (plague bolt + rotten grasp)
            'offensiveSlowPoisonMin': (F, 40.0), 'offensiveSlowPoisonMax': (F, 65.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveLifeMin': (F, 15.0), 'offensiveLifeMax': (F, 25.0),
            'offensiveSlowPoisonModifier': (I, 15),
            'offensiveLifeLeechMin': (F, 15.0),
            # Stats
            'characterLifeModifier': (F, 6.0), 'characterLife': (I, 60),
            'characterStrengthModifier': (F, 4.0),
            'characterAttackSpeedModifier': (I, 8),
            'defensivePoison': (F, 15.0),
        },
        'e': {
            'itemSkillName': (S, _SS_ZOMBIE_SUMMON),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 3),
            'offensiveSlowPoisonMin': (F, 70.0), 'offensiveSlowPoisonMax': (F, 110.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveLifeMin': (F, 25.0), 'offensiveLifeMax': (F, 40.0),
            'offensiveSlowPoisonModifier': (I, 25),
            'offensiveLifeLeechMin': (F, 25.0),
            'characterLifeModifier': (F, 10.0), 'characterLife': (I, 90),
            'characterStrengthModifier': (F, 6.0),
            'characterAttackSpeedModifier': (I, 12),
            'defensivePoison': (F, 25.0),
        },
        'l': {
            'itemSkillName': (S, _SS_ZOMBIE_SUMMON),
            'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, 4),
            # Strong poison/life (plague bolts deal massive poison)
            'offensiveSlowPoisonMin': (F, 110.0), 'offensiveSlowPoisonMax': (F, 170.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensiveLifeMin': (F, 40.0), 'offensiveLifeMax': (F, 60.0),
            'offensiveSlowPoisonModifier': (I, 40),
            'offensiveLifeLeechMin': (F, 40.0),
            'characterLifeModifier': (F, 14.0), 'characterLife': (I, 120),
            'characterStrengthModifier': (F, 8.0),
            'characterAttackSpeedModifier': (I, 15),
            'defensivePoison': (F, 35.0),
        },
    }

    total = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'melalos_soul' not in nl or 'equipmentring' not in nl:
            continue
        for diff, stats in tiers.items():
            if f'_soul_{diff}.dbr' in nl:
                _set_soul_fields(db, name, stats)
                total += 1
                break

    # Boost drop rate to 25% (Boss class)
    for name in list(db.record_names()):
        nl = name.lower()
        if 'um_melalos' in nl and 'creatures' in nl:
            fields = db.get_fields(name)
            if not fields:
                continue
            for key, tf in fields.items():
                fn = key.split('###')[0]
                if fn == 'chanceToEquipFinger2' and tf.values and float(tf.values[0]) > 0:
                    db.set_field(name, 'chanceToEquipFinger2', 25.0, DATA_TYPE_FLOAT)
                    db._modified.add(name)
                    break

    print(f"  Melalos soul overhauled ({total} records — zombie summoner, 25% drop)")
    return total


def _create_neanderthal_warband_souls(db):
    """Create souls for the 3 Neanderthal warband monsters in zzdev.

    n_mega (Boss/tank, mounted, Rally+speed aura, bleeding, Lv28/49/64)
    n_emgiec (Hacker, Storm Nimbus lightning aura, axe, Lv27/48/63)
    n_vio (Wizard, Ternion+custom teleport, Chi Realignment, Lv27/48/63)
    All Quest class, Beastman race.
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # n_mega — mounted tank/support with Rally, bleeding, speed aura
    mega_tiers = [
        {'diff': 'n', 'itemLevel': 28, 'stats': {
            'itemSkillName': (S, _SS_NESSUS_ENDURANCE),
            'itemSkillLevel': (I, 2),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE),
            'augmentSkillLevel2': (I, 2),
            'offensivePhysicalMin': (F, 25.0), 'offensivePhysicalMax': (F, 40.0),
            'offensiveSlowBleedingMin': (F, 35.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterLifeModifier': (F, 6.0), 'characterLife': (I, 50),
            'characterStrengthModifier': (F, 5.0),
            'characterRunSpeedModifier': (F, 6.0),
            'characterTotalSpeedModifier': (I, 5),
        }},
        {'diff': 'e', 'itemLevel': 49, 'stats': {
            'itemSkillName': (S, _SS_NESSUS_ENDURANCE),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE),
            'augmentSkillLevel2': (I, 3),
            'offensivePhysicalMin': (F, 40.0), 'offensivePhysicalMax': (F, 65.0),
            'offensiveSlowBleedingMin': (F, 55.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterLifeModifier': (F, 10.0), 'characterLife': (I, 80),
            'characterStrengthModifier': (F, 7.0),
            'characterRunSpeedModifier': (F, 8.0),
            'characterTotalSpeedModifier': (I, 8),
        }},
        {'diff': 'l', 'itemLevel': 64, 'stats': {
            'itemSkillName': (S, _SS_NESSUS_ENDURANCE),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_ONSLAUGHT),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE),
            'augmentSkillLevel2': (I, 3),
            # Mounted charger: physical + bleed + speed
            'offensivePhysicalMin': (F, 60.0), 'offensivePhysicalMax': (F, 90.0),
            'offensiveSlowBleedingMin': (F, 80.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterLifeModifier': (F, 14.0), 'characterLife': (I, 100),
            'characterStrengthModifier': (F, 9.0),
            'characterRunSpeedModifier': (F, 10.0),
            'characterTotalSpeedModifier': (I, 10),
        }},
    ]
    MEGA = r'records\xpack\creatures\monster\zzdev\n_mega.dbr'
    paths_mega = _create_soul(db, 'n_mega', 'tagSVCSoulNMega', mega_tiers, MEGA, 66.0)

    # n_emgiec — Hacker with Storm Nimbus lightning aura, axe DPS
    emgiec_tiers = [
        {'diff': 'n', 'itemLevel': 27, 'stats': {
            'itemSkillName': (S, _SS_HARPY_AURA),
            'itemSkillLevel': (I, 2),
            'itemSkillAutoController': (S, r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onequip.dbr'),
            'augmentSkillName1': (S, _SK_STORM_NIMBUS),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_CHAIN_LIGHTNING),
            'augmentSkillLevel2': (I, 2),
            'offensivePhysicalMin': (F, 22.0), 'offensivePhysicalMax': (F, 35.0),
            'offensiveLightningMin': (F, 15.0), 'offensiveLightningMax': (F, 25.0),
            'characterLifeModifier': (F, 5.0), 'characterLife': (I, 40),
            'characterStrengthModifier': (F, 5.0),
            'characterDexterityModifier': (F, 4.0),
            'characterAttackSpeedModifier': (I, 8),
            'defensiveLightning': (F, 12.0),
        }},
        {'diff': 'e', 'itemLevel': 48, 'stats': {
            'itemSkillName': (S, _SS_HARPY_AURA),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onequip.dbr'),
            'augmentSkillName1': (S, _SK_STORM_NIMBUS),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_CHAIN_LIGHTNING),
            'augmentSkillLevel2': (I, 3),
            'offensivePhysicalMin': (F, 35.0), 'offensivePhysicalMax': (F, 55.0),
            'offensiveLightningMin': (F, 25.0), 'offensiveLightningMax': (F, 40.0),
            'characterLifeModifier': (F, 8.0), 'characterLife': (I, 60),
            'characterStrengthModifier': (F, 7.0),
            'characterDexterityModifier': (F, 6.0),
            'characterAttackSpeedModifier': (I, 12),
            'defensiveLightning': (F, 18.0),
        }},
        {'diff': 'l', 'itemLevel': 63, 'stats': {
            'itemSkillName': (S, _SS_HARPY_AURA),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, r'records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onequip.dbr'),
            'augmentSkillName1': (S, _SK_STORM_NIMBUS),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_CHAIN_LIGHTNING),
            'augmentSkillLevel2': (I, 3),
            # Lightning hacker: phys + lightning, speed
            'offensivePhysicalMin': (F, 50.0), 'offensivePhysicalMax': (F, 78.0),
            'offensiveLightningMin': (F, 38.0), 'offensiveLightningMax': (F, 58.0),
            'characterLifeModifier': (F, 12.0), 'characterLife': (I, 80),
            'characterStrengthModifier': (F, 9.0),
            'characterDexterityModifier': (F, 8.0),
            'characterAttackSpeedModifier': (I, 15),
            'defensiveLightning': (F, 22.0),
        }},
    ]
    EMGIEC = r'records\xpack\creatures\monster\zzdev\n_emgiec.dbr'
    paths_emgiec = _create_soul(db, 'n_emgiec', 'tagSVCSoulNEmgiec', emgiec_tiers, EMGIEC, 66.0)

    # n_vio — Wizard with Ternion, custom teleport, Chi Realignment, Death Ward
    vio_tiers = [
        {'diff': 'n', 'itemLevel': 27, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_TERNION),
            'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 2),
            'offensiveLightningMin': (F, 18.0), 'offensiveLightningMax': (F, 30.0),
            'offensiveLifeMin': (F, 10.0), 'offensiveLifeMax': (F, 18.0),
            'characterLifeModifier': (F, 5.0),
            'characterManaModifier': (F, 6.0),
            'characterIntelligenceModifier': (F, 6.0),
            'characterSpellCastSpeedModifier': (I, 10),
            'defensiveLife': (F, 12.0),
            'defensiveLightning': (F, 10.0),
        }},
        {'diff': 'e', 'itemLevel': 48, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_TERNION),
            'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 3),
            'offensiveLightningMin': (F, 30.0), 'offensiveLightningMax': (F, 48.0),
            'offensiveLifeMin': (F, 18.0), 'offensiveLifeMax': (F, 30.0),
            'characterLifeModifier': (F, 8.0),
            'characterManaModifier': (F, 10.0),
            'characterIntelligenceModifier': (F, 9.0),
            'characterSpellCastSpeedModifier': (I, 16),
            'defensiveLife': (F, 18.0),
            'defensiveLightning': (F, 15.0),
        }},
        {'diff': 'l', 'itemLevel': 63, 'stats': {
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillLevel': (I, 5),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _SK_TERNION),
            'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE),
            'augmentSkillLevel2': (I, 3),
            # Powerful caster: lightning + life, cast speed, INT
            'offensiveLightningMin': (F, 45.0), 'offensiveLightningMax': (F, 70.0),
            'offensiveLifeMin': (F, 28.0), 'offensiveLifeMax': (F, 45.0),
            'characterLifeModifier': (F, 12.0),
            'characterManaModifier': (F, 14.0),
            'characterIntelligenceModifier': (F, 12.0),
            'characterSpellCastSpeedModifier': (I, 22),
            'defensiveLife': (F, 25.0),
            'defensiveLightning': (F, 20.0),
        }},
    ]
    VIO = r'records\xpack\creatures\monster\zzdev\n_vio.dbr'
    paths_vio = _create_soul(db, 'n_vio', 'tagSVCSoulNVio', vio_tiers, VIO, 66.0)

    print(f"  Neanderthal warband souls created: n_mega (tank), n_emgiec (hacker), n_vio (wizard)")
    return [paths_mega, paths_emgiec, paths_vio]


def _find_auto_generated_souls(db):
    """Find svc_uber_ souls we auto-generated that could use skill enhancement."""
    results = []
    for name in db.record_names():
        nl = name.lower()
        if 'svc_uber' not in nl:
            continue
        if 'equipmentring' not in nl:
            continue
        if '_soul_n.dbr' not in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        has_skill = False
        has_augment = False
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'itemSkillName' and tf.values and tf.values[0]:
                has_skill = True
            if rk == 'augmentSkillName1' and tf.values and tf.values[0]:
                has_augment = True

        if has_skill:
            continue

        basename = nl.replace('\\', '/').split('/')[-1].replace('_soul_n.dbr', '')
        monster_level = 0
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'itemLevel' and tf.values:
                monster_level = int(tf.values[0])
                break

        results.append({
            'path_n': name,
            'path_e': name.replace('_soul_n.dbr', '_soul_e.dbr'),
            'path_l': name.replace('_soul_n.dbr', '_soul_l.dbr'),
            'basename': basename,
            'level': monster_level,
            'has_augment': has_augment,
        })
    return results


# Map elements/keywords to good granted skills + augments for auto-enhancement
_ELEMENT_SKILL_MAP = {
    'lightning': {
        'itemSkillName': r'records\skills\soulskills\ringoflightning.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\storm\drxstormnimbus.dbr',
        'augment2': r'records\skills\storm\drxlightningbolt_chainlightning.dbr',
    },
    'fire': {
        'itemSkillName': r'records\skills\soulskills\firefragmentnova.dbr',
        'itemSkillAutoController': _AC_FIRE_REACT,
        'augment1': r'records\skills\earth\drxfireenchantment.dbr',
        'augment2': r'records\skills\earth\drxringofflame.dbr',
    },
    'cold': {
        'itemSkillName': r'records\skills\soulskills\gargantuanyeti_iceblast.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\storm\drxcoldaura.dbr',
        'augment2': r'records\skills\storm\drxfreezingblast.dbr',
    },
    'poison': {
        'itemSkillName': r'records\skills\soulskills\arachne_venomspray.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\stealth\drxenvenomweapon.dbr',
        'augment2': r'records\skills\nature\drxplague.dbr',
    },
    'life': {
        'itemSkillName': r'records\skills\soulskills\melinoe_bloodboil.dbr',
        'itemSkillAutoController': _AC_ON_ATTACK,
        'augment1': r'records\skills\spirit\drxdeathchillaura.dbr',
        'augment2': r'records\skills\spirit\drxdarkcovenant.dbr',
    },
    'physical': {
        'itemSkillName': r'records\skills\soulskills\cyclops_groundsmash.dbr',
        'itemSkillAutoController': _AC_ON_HIT,
        'augment1': r'records\skills\warfare\drxonslaught.dbr',
        'augment2': r'records\skills\warfare\drxbattlerage.dbr',
    },
}

_ELEMENT_KEYWORDS = {
    'lightning': ['lightning', 'storm', 'thunder', 'electric', 'shock'],
    'fire': ['fire', 'flame', 'burn', 'magma', 'lava', 'pyro', 'inferno'],
    'cold': ['cold', 'ice', 'frost', 'freeze', 'blizzard', 'chill', 'yeti'],
    'poison': ['poison', 'venom', 'toxic', 'plague', 'spider', 'arachn', 'scorpo'],
    'life': ['life', 'death', 'undead', 'spirit', 'wraith', 'ghost', 'liche', 'necrotic', 'shadow', 'dark'],
}


def _guess_element(basename, fields):
    """Guess element from soul basename and existing damage fields."""
    text = basename.lower()
    damage_hints = {}
    for key, tf in fields.items():
        rk = key.split('###')[0].lower()
        if 'offensivefire' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['fire'] = damage_hints.get('fire', 0) + float(tf.values[0])
        elif 'offensivecold' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['cold'] = damage_hints.get('cold', 0) + float(tf.values[0])
        elif 'offensivelightning' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['lightning'] = damage_hints.get('lightning', 0) + float(tf.values[0])
        elif ('offensivepoison' in rk or 'offensiveslowpoison' in rk) and tf.values and float(tf.values[0]) > 0:
            damage_hints['poison'] = damage_hints.get('poison', 0) + float(tf.values[0])
        elif 'offensivelife' in rk and tf.values and float(tf.values[0]) > 0:
            damage_hints['life'] = damage_hints.get('life', 0) + float(tf.values[0])

    if damage_hints:
        return max(damage_hints, key=damage_hints.get)

    for elem, keywords in _ELEMENT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return elem

    return 'physical'


def overhaul_souls(db):
    """Patch 13: Overhaul weak uber/boss souls with skills, summons, procs."""
    print("\n=== Patch 13: Overhaul weak souls with skills/procs ===")
    total = 0

    rakan_ok = _create_rakanizeus_pet_skill(db)
    total += 1

    boneash_ok = _create_boneash_pet_skill(db)
    total += 1

    pharaoh_ok = _create_pharaoh_guard_pet_skill(db)
    total += 1

    # A10 (build29, owner request): summon-the-boss souls (Narok + Vort).
    a10_status = []
    for _spec in _A10_BOSS_SUMMONS:
        a10_status.append((_spec['label'],
                           _create_boss_summon_from_source(db, _spec)))
        total += 1

    # Surface pet-skill build failures instead of silently ignoring the return
    # values. Each helper returns False when a required source record is missing,
    # which leaves that summonable soul pet non-functional.
    pet_skill_status = [
        ('Rakanizeus', rakan_ok),
        ('Boneash', boneash_ok),
        ("Pharaoh's Honor Guard", pharaoh_ok),
    ] + a10_status
    failed_pet_skills = [nm for nm, ok in pet_skill_status if not ok]
    if failed_pet_skills:
        raise SystemExit(
            f"Pet skill build FAILED for: {', '.join(failed_pet_skills)} "
            f"(source record missing -- these soul pets would not summon); "
            f"fail-loud instead of shipping dead summons")
    else:
        print("  Pet skills built: Rakanizeus, Boneash, Pharaoh's Honor Guard, "
              "Narok, Vort")

    _update_pharaoh_guard_drop_rate(db)
    _fix_low_boss_soul_drop_rates(db)
    _wire_missing_boss_souls(db)

    eclipse_skill = r'records\skills\soulskills\calybe_eclipse.dbr'
    if db.has_record(eclipse_skill):
        db.set_field(eclipse_skill, 'skillCooldownTime', 18.0, DATA_TYPE_FLOAT)
        db.set_field(eclipse_skill, 'skillCooldownReductionModifier', 18.0, DATA_TYPE_FLOAT)
        db._modified.add(eclipse_skill)
        print("  Eclipse cooldown: 90s -> 18s (for on-hit proc)")

    for partial_key, field_dict in SOUL_OVERHAULS.items():
        for name in list(db.record_names()):
            nl = name.lower()
            if partial_key in nl and 'soul' in nl and 'equipmentring' in nl:
                _set_soul_fields(db, name, field_dict)
                total += 1
        print(f"  Enhanced: {partial_key} ({sum(1 for n in db.record_names() if partial_key in n.lower() and 'soul' in n.lower() and 'equipmentring' in n.lower())} variants)")

    auto_souls = _find_auto_generated_souls(db)
    enhanced = 0
    for soul in auto_souls:
        fields = db.get_fields(soul['path_n'])
        if not fields:
            continue

        elem = _guess_element(soul['basename'], fields)
        skill_map = _ELEMENT_SKILL_MAP.get(elem, _ELEMENT_SKILL_MAP['physical'])
        level = soul['level']
        power = max(1.0, level / 10.0)

        enhancements = {
            'itemSkillName': (DATA_TYPE_STRING, skill_map['itemSkillName']),
            'itemSkillLevel': (DATA_TYPE_INT, max(1, min(int(power), 5))),
            'itemSkillAutoController': (DATA_TYPE_STRING, skill_map['itemSkillAutoController']),
        }
        if not soul['has_augment']:
            enhancements['augmentSkillName1'] = (DATA_TYPE_STRING, skill_map['augment1'])
            enhancements['augmentSkillLevel1'] = (DATA_TYPE_INT, max(1, min(int(power * 0.8), 4)))
            enhancements['augmentSkillName2'] = (DATA_TYPE_STRING, skill_map['augment2'])
            enhancements['augmentSkillLevel2'] = (DATA_TYPE_INT, max(1, min(int(power * 0.6), 3)))

        for variant in (soul['path_n'], soul['path_e'], soul['path_l']):
            if db.has_record(variant):
                _set_soul_fields(db, variant, enhancements)

        enhanced += 1

    print(f"  Auto-enhanced {enhanced} auto-generated (svc_uber) souls with element-matched skills")
    total += enhanced

    print(f"  Total soul records modified: {total}")
    return total


def cascade_merc_scrolls(db):
    """Patch 14: Make all mercenary scrolls droppable everywhere.

    Normal scrolls cascade into Epic tables, Normal+Epic into Legendary.
    Every act's table gets ALL scrolls for that difficulty tier.
    """
    print("\n=== Patch 14: Cascade mercenary scrolls across difficulties ===")
    total = 0

    all_scrolls = NORMAL_SCROLLS + EPIC_SCROLLS + LEGENDARY_SCROLLS

    for table_path, tag in MERC_LOOT_TABLES.items():
        if not db.has_record(table_path):
            continue

        difficulty = tag[0]
        if difficulty == 'n':
            scrolls = NORMAL_SCROLLS
        elif difficulty == 'e':
            scrolls = NORMAL_SCROLLS + EPIC_SCROLLS
        else:
            scrolls = all_scrolls

        for i, scroll_path in enumerate(scrolls, 1):
            db.set_field(table_path, f'lootName{i}', scroll_path, DATA_TYPE_STRING)
            db.set_field(table_path, f'lootWeight{i}', 100, DATA_TYPE_INT)
        for i in range(len(scrolls) + 1, 31):
            db.set_field(table_path, f'lootWeight{i}', 0, DATA_TYPE_INT)

        db._modified.add(table_path)
        total += 1
        print(f"  {table_path}: {len(scrolls)} scrolls ({difficulty.upper()} tier)")

    print(f"  Updated {total} loot tables")
    return total


def add_blood_mistress_to_loot(db):
    """Patch 15: Add Blood Mistress upgrade formula to boss loot tables.

    Adds the formula to the forge formula drop tables in each act at each
    difficulty, so it can drop from bosses alongside other forge formulas.
    """
    print("\n=== Patch 15: Add Blood Mistress formula to boss loot tables ===")
    total = 0

    formula_path = BLOOD_MISTRESS_FORMULA
    if not db.has_record(formula_path):
        print(f"  WARN: Blood Mistress formula not found at {formula_path}")
        return 0

    forge_tables = []
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'forgeformulas' in nl and 'drop' in nl and 'loottable' in nl:
            forge_tables.append(name)

    for table in forge_tables:
        fields = db.get_fields(table)
        if not fields:
            continue

        max_slot = 0
        for key in fields:
            rk = key.split('###')[0]
            if rk.startswith('lootName'):
                try:
                    slot_num = int(rk.replace('lootName', ''))
                    if slot_num > max_slot:
                        max_slot = slot_num
                except ValueError:
                    pass

        new_slot = max_slot + 1
        db.set_field(table, f'lootName{new_slot}', formula_path, DATA_TYPE_STRING)
        db.set_field(table, f'lootWeight{new_slot}', 50, DATA_TYPE_INT)
        db._modified.add(table)
        total += 1

    print(f"  Added formula to {total} forge formula drop tables")
    return total


import re as _re


def _add_monster_to_pools(db, monster_path, pool_keyword, weight=2, tag=None):
    """Add a monster as a champion entry to spawn pools matching keyword.

    pool_keyword is matched against ALL string field values in a record.
    tag: string to check if monster is already in pool (defaults to monster filename).
    Returns count of pools modified.
    """
    if tag is None:
        tag = monster_path.rsplit('\\', 1)[-1].replace('.dbr', '').lower()

    pools = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        has_kw = False
        has_name = False
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn.startswith('name') and not fn.startswith('nameChampion'):
                has_name = True
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and pool_keyword in v.lower():
                        has_kw = True
                        break
        if has_kw and has_name:
            pools.append(name)

    total = 0
    for pool in pools:
        fields = db.get_fields(pool)
        if not fields:
            continue
        already = False
        for key, tf in fields.items():
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and tag in v.lower():
                        already = True
                        break
        if already:
            continue

        max_idx = 0
        for key in fields:
            fn = key.split('###')[0]
            m = _re.match(r'nameChampion(\d+)', fn)
            if m and int(m.group(1)) > max_idx:
                max_idx = int(m.group(1))

        nxt = max_idx + 1
        db.set_field(pool, f'nameChampion{nxt}', monster_path, DATA_TYPE_STRING)
        db.set_field(pool, f'weightChampion{nxt}', weight, DATA_TYPE_INT)
        db._modified.add(pool)

        cc = db.get_field_value(pool, 'championChance')
        if cc is not None and float(cc) == 0.0:
            db.set_field(pool, 'championChance', 15.0, DATA_TYPE_FLOAT)
            db.set_field(pool, 'championMax', 1, DATA_TYPE_INT)
        total += 1
    return total


def _find_record(db, substr):
    """Find first record containing substr (case-insensitive)."""
    sl = substr.lower()
    for name in db.record_names():
        if sl in name.lower():
            return name
    return None


def _wire_soul_to_monster(db, monster, soul_paths, drop_rate=66.0):
    """Wire a soul (list of [n,e,l] paths) to a monster record."""
    if not db.has_record(monster):
        return False
    db.set_field(monster, 'lootFinger2Item1', soul_paths, DATA_TYPE_STRING)
    db.set_field(monster, 'chanceToEquipFinger2', drop_rate, DATA_TYPE_FLOAT)
    db.set_field(monster, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
    db.set_field(monster, 'dropItems', 1, DATA_TYPE_INT)
    db._modified.add(monster)
    return True


def _has_soul(db, record):
    """Check if a monster record already has a *real* soul wired.

    A soul counts only if lootFinger2Item1 references a soul item AND at least
    one referenced record actually exists in the database. The mere presence of
    a 'soul' path is not enough: SV 0.98i ships dangling references (e.g.
    um_ainex_45 -> empusa/ainex_soul_{n,e,l}, records that were never authored),
    and treating those as "has a soul" silently disables the fallback
    soul-creator, leaving the boss dropping nothing at a wired 100% chance.
    Resolve references the same tolerant way the rest of this module does
    (_find_record: both slash conventions + case-insensitive) so a legitimately
    wired soul stored under a different slash/case convention is never counted
    as missing.
    """
    fields = db.get_fields(record)
    if not fields:
        return False
    for key, tf in fields.items():
        fn = key.split('###')[0]
        if fn == 'lootFinger2Item1' and tf.values:
            for v in tf.values:
                if isinstance(v, str) and 'soul' in v.lower():
                    if _find_record(db, v):
                        return True
    return False


def _get_soul_paths(db, record):
    """Get the soul paths wired to a monster record."""
    fields = db.get_fields(record)
    if not fields:
        return None
    for key, tf in fields.items():
        fn = key.split('###')[0]
        if fn == 'lootFinger2Item1' and tf.values:
            vals = list(tf.values)
            if vals and isinstance(vals[0], str) and 'soul' in vals[0].lower():
                return vals
    return None


# ── Task 2: Audit uber soul SKIP lists ──────────────────────────────────

def _audit_uber_soul_skips(db):
    """Print which monsters were skipped by create_uber_souls SKIP lists
    and whether they have a soul anyway."""
    from create_uber_souls import SKIP_NAMES, SKIP_EXACT, SKIP_COMMON_VARIANTS

    print("\n=== Audit: uber soul SKIP list coverage ===")
    skipped_no_soul = []
    skipped_has_soul = 0

    for name in db.record_names():
        nl = name.lower()
        if 'creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue

        # Check if it's a monster
        is_monster = False
        classification = ''
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn == 'Class' and tf.values and 'Monster' in str(tf.values[0]):
                is_monster = True
            if fn == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
        if not is_monster:
            continue

        # Must be Hero/Boss/Quest or um_ prefixed
        is_hero = classification in ('Hero', 'Boss', 'Quest')
        fname = nl.rsplit('\\', 1)[-1].replace('.dbr', '')
        is_um = fname.startswith('um_') or fname.startswith('boss_')
        if not is_hero and not is_um:
            continue

        # Check SKIP_NAMES
        skip_reason = None
        for skip in SKIP_NAMES:
            if skip in nl:
                skip_reason = f'SKIP_NAMES({skip})'
                break

        # Check SKIP_EXACT
        clean = _re.sub(r'_\d+$', '', fname)
        if clean in SKIP_EXACT:
            skip_reason = f'SKIP_EXACT({clean})'

        # Check SKIP_COMMON_VARIANTS
        if classification not in ('Hero', 'Boss', 'Quest') and clean in SKIP_COMMON_VARIANTS:
            skip_reason = f'SKIP_COMMON_VARIANTS({clean})'

        if not skip_reason:
            continue

        has = _has_soul(db, name)
        if has:
            skipped_has_soul += 1
        else:
            skipped_no_soul.append((fname, skip_reason))

    if skipped_no_soul:
        print(f"  Skipped WITHOUT soul ({len(skipped_no_soul)}):")
        for fname, reason in sorted(skipped_no_soul)[:30]:
            print(f"    {fname} — {reason}")
        if len(skipped_no_soul) > 30:
            print(f"    ... and {len(skipped_no_soul) - 30} more")
    print(f"  Skipped WITH soul (OK): {skipped_has_soul}")
    print(f"  Total skipped without soul: {len(skipped_no_soul)}")


# ── Task 4: um_feth variants + soul ─────────────────────────────────────

def _create_feth_variants_and_soul(db):
    """Create soul for um_feth (Reptilian Hero).

    um_feth_27 already has charLevel [27, 48, 63] for full N/E/L difficulty
    scaling.  Reptilian pools only exist in Egypt — no higher-level geographic
    variants are needed.
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    print("\n  Feth (Reptilian Hero):")

    feth27 = _find_record(db, 'um_feth_27')
    if not feth27:
        print("    WARNING: um_feth_27 not found")
        return

    tiers = [
        {'diff': 'n', 'itemLevel': 27, 'stats': {
            'offensivePhysicalMin': (F, 25.0), 'offensivePhysicalMax': (F, 40.0),
            'offensivePierceMin': (F, 15.0), 'offensivePierceMax': (F, 25.0),
            'characterStrengthModifier': (F, 4.0), 'characterLifeModifier': (F, 5.0),
            'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 1),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 1),
        }},
        {'diff': 'e', 'itemLevel': 42, 'stats': {
            'offensivePhysicalMin': (F, 38.0), 'offensivePhysicalMax': (F, 58.0),
            'offensivePierceMin': (F, 22.0), 'offensivePierceMax': (F, 36.0),
            'characterStrengthModifier': (F, 5.5), 'characterLifeModifier': (F, 7.0),
            'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 2),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 2),
        }},
        {'diff': 'l', 'itemLevel': 57, 'stats': {
            'offensivePhysicalMin': (F, 50.0), 'offensivePhysicalMax': (F, 75.0),
            'offensivePierceMin': (F, 30.0), 'offensivePierceMax': (F, 45.0),
            'characterStrengthModifier': (F, 7.0), 'characterLifeModifier': (F, 9.0),
            'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 3),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 3),
        }},
    ]
    _create_soul(db, 'um_feth', 'tagSVCSoulFeth', tiers, feth27, 66.0)
    print("    Soul created and wired to um_feth_27 (charLevel [27, 48, 63])")


# ── Task 5: Neanderthal warband monster records ─────────────────────────

def _create_neanderthal_warband_monsters(db):
    """Create monster records for n_mega, n_emgiec, n_vio.

    Clones from an existing neanderthal hero, adjusts stats.
    Must be called BEFORE _create_neanderthal_warband_souls().
    """
    MEGA  = r'records\xpack\creatures\monster\zzdev\n_mega.dbr'
    EMGIEC = r'records\xpack\creatures\monster\zzdev\n_emgiec.dbr'
    VIO    = r'records\xpack\creatures\monster\zzdev\n_vio.dbr'

    # Skip if already created
    if db.has_record(MEGA) and db.has_record(EMGIEC) and db.has_record(VIO):
        return

    # Find a neanderthal hero to clone from
    source = None
    for name in db.record_names():
        nl = name.lower()
        if 'neanderthal' in nl and ('hero' in nl or 'um_' in nl) and 'creature' in nl:
            if '.dbr' in nl and 'old' not in nl:
                source = name
                break

    if not source:
        # Fallback: any neanderthal monster
        for name in db.record_names():
            nl = name.lower()
            if 'neanderthal' in nl and 'creature' in nl and '.dbr' in nl:
                if 'old' not in nl and 'proxy' not in nl and 'pool' not in nl:
                    source = name
                    break

    if not source:
        print("  WARNING: No neanderthal source record found for warband cloning")
        return

    print(f"  Neanderthal warband: cloning from {source.rsplit(chr(92), 1)[-1]}")

    # Compute charLevel offsets from source for proper [N, E, L] arrays
    src_cl = db.get_field_value(source, 'charLevel')
    if isinstance(src_cl, (list, tuple)) and len(src_cl) >= 3:
        _e_off = int(src_cl[1]) - int(src_cl[0])
        _l_off = int(src_cl[2]) - int(src_cl[0])
    else:
        _e_off, _l_off = 20, 35  # fallback based on typical neanderthal scaling

    for dest, desc, lvl, hp in [
        (MEGA, 'n_mega (Boss/Tank)', 35, 8000),
        (EMGIEC, 'n_emgiec (Hacker)', 33, 5500),
        (VIO, 'n_vio (Wizard)', 33, 4500),
    ]:
        if db.has_record(dest):
            continue
        db.clone_record(source, dest)
        db.set_field(dest, 'charLevel', [lvl, lvl + _e_off, lvl + _l_off], DATA_TYPE_INT)
        db.set_field(dest, 'characterLife', hp, DATA_TYPE_INT)
        db.set_field(dest, 'monsterClassification', 'Quest', DATA_TYPE_STRING)
        db.set_field(dest, 'FileDescription', desc, DATA_TYPE_STRING)
        db.set_field(dest, 'dropItems', 1, DATA_TYPE_INT)
        db._modified.add(dest)
        print(f"    Created {dest.rsplit(chr(92), 1)[-1]} (Lv{lvl}, {hp} HP)")

    # Add to neanderthal spawn pools
    for dest in [MEGA, EMGIEC, VIO]:
        tag = dest.rsplit('\\', 1)[-1].replace('.dbr', '').lower()
        ct = _add_monster_to_pools(db, dest, 'neanderthal', 2, tag)
        if ct:
            print(f"    {tag} added to {ct} neanderthal pools")


# ── Task 6: Graeae verification ─────────────────────────────────────────

def _verify_graeae_wiring(db):
    """Verify and fix dropItems on active Graeae boss records."""
    GRAEAE = ['boss_deino', 'boss_enyo', 'boss_pemphredo']
    verified = 0
    fixed = 0

    for name in db.record_names():
        nl = name.lower()
        if not any(g in nl for g in GRAEAE):
            continue
        if 'creature' not in nl:
            continue
        if 'old' in nl:
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        has = _has_soul(db, name)
        drop_ok = False
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn == 'dropItems' and tf.values and int(tf.values[0]) == 1:
                drop_ok = True

        if has and not drop_ok:
            db.set_field(name, 'dropItems', 1, DATA_TYPE_INT)
            db._modified.add(name)
            fixed += 1

        verified += 1

    print(f"  Graeae verified: {verified} records, {fixed} dropItems fixed")
    return fixed


# ── Task 7: Place orphan monsters in pools ──────────────────────────────

# Authoritative deny-list: records that must NEVER drop a soul, regardless of any
# classification promotion. Enforced by _gate_common_soul_leaks (force-zero) AND
# respected by _place_orphan_monsters (which will not promote/re-soul these). Kept
# as a module constant so both stay in lockstep.
_SOUL_DROP_DENY_SUBSTRINGS = [
    r'04_skeletaltyphon\skeletaltyphon.dbr',
    r'04_skeletaltyphon\anm\anm_skeletaltyphon.dbr',
    r'tombguardian\um_tombguardian_26.dbr',
]


def _is_soul_drop_denied(record_name):
    nl = record_name.replace('/', '\\').lower()
    return any(sub in nl for sub in _SOUL_DROP_DENY_SUBSTRINGS)


def _place_orphan_monsters(db):
    """Place 10 unspawnable uber/boss monsters into spawn pools and ensure souls."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    print("\n  Placing orphan monsters in spawn pools:")

    # (record_substring, pool_keyword, description, level, soul_base_override)
    # soul_base_override: explicit soul-item base name when the record needs its
    # fallback soul under a specific canonical name. Ainex's boss soul MUST be
    # authored as ainex_soul_{n,e,l} (the name the design/audit specifies and the
    # Soul-of-Ainex tag pairs with); the default derivation would name it
    # um_ainex_soul_* off the um_ainex_45 record. None => derive as before, which
    # keeps every other orphan's existing soul name unchanged.
    ORPHANS = [
        ('um_phagia_34',       'maenad',       'Phagia Lv34',       34, None),
        ('um_phagia_44',       'djinn',        'Phagia Lv44',       44, None),
        ('um_frost_36',        'limos',        'Frost Lv36',        36, None),
        ('um_ainex_45',        'empusa',       'Ainex Lv45',        45, 'ainex'),
        ('um_droolbog_43',     'anouran',      'Droolbog Lv43',     43, None),
        ('um_prox_47',         'archlimos',    'Prox Lv47',         47, None),
        ('um_yama_38',         'neanderthal',  'Yama Lv38',         38, None),
        ('um_inkeyes2_45',     'ratman',       'Inkeyes2 Lv45',     45, None),
        ('um_tombguardian_26', 'tombguardian', 'Tomb Guardian Lv26', 26, None),
    ]

    total_placed = 0
    total_souled = 0

    for substr, pool_kw, desc, lvl, soul_base in ORPHANS:
        rec = _find_record(db, substr)
        if not rec:
            print(f"    WARNING: {substr} not found")
            continue

        # Ensure dropItems
        db.set_field(rec, 'dropItems', 1, DATA_TYPE_INT)
        db._modified.add(rec)

        # Ensure a soul-eligible classification. These orphans are deliberately
        # placed farmable uber/boss encounters and are wired to drop their soul
        # just below - but the soul-drop GATE (wire_souls_to_monsters +
        # _verify_no_unclassified_soul_leaks) only permits Hero/Boss/Quest. In the
        # base SV data um_prox_47 shipped with NO monsterClassification (its
        # archlimos siblings um_darkhellion_43 / um_frozenhorror_43 / xhero_* are
        # all Hero), so its wired soul would drop from a non-gated monster - a leak
        # in BOTH the release (66%) and testing (100%) builds. Promote any orphan
        # that is not already Hero/Boss/Quest to Hero (the sibling class), so the
        # intended drop is preserved AND the gate holds. Never DEMOTES an already
        # gated boss (only raises None/Common/Champion -> Hero).
        #
        # EXCEPTION: records on the soul-drop deny-list (um_tombguardian_26) must
        # STAY non-dropping - _gate_common_soul_leaks deliberately zeros them
        # (design: they are not real farmable soul sources). Skip the promotion so
        # the gate's later force-zero holds; the soul record is still created below
        # (harmless, chance ends at 0).
        if not _is_soul_drop_denied(rec):
            _mc = db.get_field_value(rec, 'monsterClassification')
            if _mc not in ('Hero', 'Boss', 'Quest'):
                db.set_field(rec, 'monsterClassification', 'Hero', DATA_TYPE_STRING)
                db._modified.add(rec)
                print(f"    {desc}: promoted classification {_mc!r} -> 'Hero' "
                      f"(soul-dropper gate)")

        # Create soul if needed
        if not _has_soul(db, rec):
            clean = soul_base if soul_base else _re.sub(r'_\d+$', '', substr)
            tag_name = 'tagSVCSoul' + clean.replace('um_', '').replace('_', '').title()
            e_lvl = lvl + 15
            l_lvl = lvl + 30
            tiers = [
                {'diff': 'n', 'itemLevel': lvl, 'stats': {
                    'offensivePhysicalMin': (F, lvl * 1.2), 'offensivePhysicalMax': (F, lvl * 1.8),
                    'characterStrengthModifier': (F, 4.0), 'characterLifeModifier': (F, 5.0),
                    'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 1),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                }},
                {'diff': 'e', 'itemLevel': e_lvl, 'stats': {
                    'offensivePhysicalMin': (F, e_lvl * 1.2), 'offensivePhysicalMax': (F, e_lvl * 1.8),
                    'characterStrengthModifier': (F, 5.5), 'characterLifeModifier': (F, 7.0),
                    'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 2),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                }},
                {'diff': 'l', 'itemLevel': l_lvl, 'stats': {
                    'offensivePhysicalMin': (F, l_lvl * 1.2), 'offensivePhysicalMax': (F, l_lvl * 1.8),
                    'characterStrengthModifier': (F, 7.0), 'characterLifeModifier': (F, 9.0),
                    'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 3),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                }},
            ]
            _create_soul(db, clean, tag_name, tiers, rec, 66.0)
            total_souled += 1

        ct = _add_monster_to_pools(db, rec, pool_kw, 2, substr)
        print(f"    {desc}: {ct} pools")
        total_placed += ct

    print(f"  Orphan monsters: {total_placed} pool entries, {total_souled} new souls")


# ── Task 8: Wire missing difficulty variants ─────────────────────────────

def _wire_difficulty_variants(db):
    """Add orphaned higher-difficulty variants to spawn pools alongside siblings."""
    print("\n  Wiring missing difficulty variants into pools:")

    VARIANTS = [
        ('um_dapoyan_42',   'um_dapoyan',   'ichthian'),
        ('um_indrajit_42',  'um_indrajit',   'ichthian'),
        ('um_vidja_43',     'um_vidja',      'ichthian'),
        ('um_rong_40',      'um_rong',       'neanderthal'),
        ('um_vuji_41',      'um_vuji',       'neanderthal'),
        ('um_rocksting_29', 'um_rocksting',  'scorpion'),
        ("hero_sehr'tunkah_30", "hero_sehr'tunkah", 'shadowstalker'),
        ("hero_sehr'tunkah_36", "hero_sehr'tunkah", 'shadowstalker'),
        ('boss_terracottamage_bandari_40', 'boss_terracottamage_bandari', 'bandari'),
    ]

    total = 0
    for var_sub, sibling_sub, pool_kw in VARIANTS:
        rec = _find_record(db, var_sub)
        if not rec:
            print(f"    WARNING: {var_sub} not found")
            continue

        # Ensure dropItems
        db.set_field(rec, 'dropItems', 1, DATA_TYPE_INT)
        db._modified.add(rec)

        # Copy soul from sibling if variant lacks one
        if not _has_soul(db, rec):
            sib = _find_record(db, sibling_sub)
            if sib:
                sib_souls = _get_soul_paths(db, sib)
                if sib_souls:
                    _wire_soul_to_monster(db, rec, sib_souls, 66.0)

        ct = _add_monster_to_pools(db, rec, pool_kw, 2, var_sub)
        print(f"    {var_sub}: {ct} pools")
        total += ct

    print(f"  Difficulty variants: {total} pool entries added")


# ── Task 9: Wire IT expansion orphans ────────────────────────────────────

def _wire_it_expansion_orphans(db):
    """Wire Blood Sisters + bonescourge/hydradon heroes: souls, pools, variants."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    print("\n  Wiring IT expansion orphans:")

    # ── Blood Sisters (souls already exist) ──
    for sister in ['safiya', 'sagira']:
        # Find existing soul records
        soul_n = soul_e = soul_l = None
        for name in db.record_names():
            nl = name.lower()
            if sister in nl and 'soul' in nl and 'equipmentring' in nl:
                if '_soul_n.dbr' in nl:
                    soul_n = name
                elif '_soul_e.dbr' in nl:
                    soul_e = name
                elif '_soul_l.dbr' in nl:
                    soul_l = name

        if not soul_n:
            print(f"    WARNING: {sister} soul records not found")
            continue

        soul_paths = [p for p in [soul_n, soul_e, soul_l] if p]
        if len(soul_paths) < 3:
            # Pad with the normal variant
            while len(soul_paths) < 3:
                soul_paths.append(soul_n)

        # Find and wire all monster variants
        wired = 0
        for name in list(db.record_names()):
            nl = name.lower()
            if f'bloodsister{sister}' in nl and 'creature' in nl and '.dbr' in nl:
                if 'soul' not in nl:
                    _wire_soul_to_monster(db, name, soul_paths, 66.0)
                    ct = _add_monster_to_pools(db, name, 'djinn', 2, f'bloodsister{sister}')
                    wired += 1
        print(f"    Blood Sister {sister.title()}: {wired} variants wired + pooled")

    # ── Bonescourge heroes (need souls) ──
    for hero_sub, tag, display, lvl, element in [
        ('xhero_lash_47', 'tagSVCSoulLash', '{^F}Soul of Lash', 47, 'physical'),
        ('xhero_theflayer_47', 'tagSVCSoulTheFlayer', '{^F}Soul of the Flayer', 47, 'physical'),
    ]:
        rec = _find_record(db, hero_sub)
        if not rec:
            print(f"    WARNING: {hero_sub} not found")
            continue

        if not _has_soul(db, rec):
            tiers = [
                {'diff': 'n', 'itemLevel': 31, 'stats': {
                    'offensivePhysicalMin': (F, 35.0), 'offensivePhysicalMax': (F, 55.0),
                    'offensiveLifeMin': (F, 20.0), 'offensiveLifeMax': (F, 35.0),
                    'characterStrengthModifier': (F, 5.0), 'characterLifeModifier': (F, 6.0),
                    'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 1),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                    'augmentSkillName1': (S, _SK_DEATH_CHILL), 'augmentSkillLevel1': (I, 1),
                }},
                {'diff': 'e', 'itemLevel': 52, 'stats': {
                    'offensivePhysicalMin': (F, 50.0), 'offensivePhysicalMax': (F, 75.0),
                    'offensiveLifeMin': (F, 30.0), 'offensiveLifeMax': (F, 50.0),
                    'characterStrengthModifier': (F, 7.0), 'characterLifeModifier': (F, 8.0),
                    'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 2),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                    'augmentSkillName1': (S, _SK_DEATH_CHILL), 'augmentSkillLevel1': (I, 2),
                }},
                {'diff': 'l', 'itemLevel': 68, 'stats': {
                    'offensivePhysicalMin': (F, 65.0), 'offensivePhysicalMax': (F, 95.0),
                    'offensiveLifeMin': (F, 40.0), 'offensiveLifeMax': (F, 65.0),
                    'characterStrengthModifier': (F, 9.0), 'characterLifeModifier': (F, 10.0),
                    'itemSkillName': (S, _SS_GROUND_SMASH), 'itemSkillLevel': (I, 3),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                    'augmentSkillName1': (S, _SK_DEATH_CHILL), 'augmentSkillLevel1': (I, 3),
                }},
            ]
            clean = _re.sub(r'_\d+$', '', hero_sub)
            _create_soul(db, clean, tag, tiers, rec, 66.0)

        db.set_field(rec, 'dropItems', 1, DATA_TYPE_INT)
        db._modified.add(rec)

        # Create lower-level variants with proper [N, E, L] charLevel arrays
        src_cl = db.get_field_value(rec, 'charLevel')
        if isinstance(src_cl, (list, tuple)) and len(src_cl) >= 3:
            bc_e_off = int(src_cl[1]) - int(src_cl[0])
            bc_l_off = int(src_cl[2]) - int(src_cl[0])
        else:
            bc_e_off, bc_l_off = 15, 27  # fallback from xhero_lash_47 [47,62,74]
        for dest_lvl, suffix in [(31, '_31'), (39, '_39')]:
            dest = rec.replace('_47.dbr', f'{suffix}.dbr')
            if not db.has_record(dest):
                db.clone_record(rec, dest)
                db.set_field(dest, 'charLevel',
                             [dest_lvl, dest_lvl + bc_e_off, dest_lvl + bc_l_off],
                             DATA_TYPE_INT)
                soul_p = _get_soul_paths(db, rec)
                if soul_p:
                    _wire_soul_to_monster(db, dest, soul_p, 66.0)
                db._modified.add(dest)

        # Add all variants to bonescourge pools
        ct = _add_monster_to_pools(db, rec, 'bonescourge', 2, hero_sub.split('_')[0] + '_' + hero_sub.split('_')[1])
        print(f"    {hero_sub}: soul created, {ct} pools, 2 lower variants")

    # ── Hydradon hero (needs soul) ──
    hero_sub = 'xhero_rottingdevourer_41'
    rec = _find_record(db, hero_sub)
    if rec:
        if not _has_soul(db, rec):
            tiers = [
                {'diff': 'n', 'itemLevel': 27, 'stats': {
                    'offensiveSlowPoisonMin': (F, 25.0), 'offensiveSlowPoisonDurationMin': (F, 3.0),
                    'offensivePhysicalMin': (F, 30.0), 'offensivePhysicalMax': (F, 48.0),
                    'characterStrengthModifier': (F, 4.0), 'characterLifeModifier': (F, 5.0),
                    'itemSkillName': (S, _SK_PLAGUE), 'itemSkillLevel': (I, 1),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                }},
                {'diff': 'e', 'itemLevel': 47, 'stats': {
                    'offensiveSlowPoisonMin': (F, 40.0), 'offensiveSlowPoisonDurationMin': (F, 4.0),
                    'offensivePhysicalMin': (F, 45.0), 'offensivePhysicalMax': (F, 68.0),
                    'characterStrengthModifier': (F, 6.0), 'characterLifeModifier': (F, 7.0),
                    'itemSkillName': (S, _SK_PLAGUE), 'itemSkillLevel': (I, 2),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                }},
                {'diff': 'l', 'itemLevel': 62, 'stats': {
                    'offensiveSlowPoisonMin': (F, 55.0), 'offensiveSlowPoisonDurationMin': (F, 5.0),
                    'offensivePhysicalMin': (F, 60.0), 'offensivePhysicalMax': (F, 88.0),
                    'characterStrengthModifier': (F, 8.0), 'characterLifeModifier': (F, 9.0),
                    'itemSkillName': (S, _SK_PLAGUE), 'itemSkillLevel': (I, 3),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                }},
            ]
            _create_soul(db, 'xhero_rottingdevourer', 'tagSVCSoulRottingDevourer',
                         tiers, rec, 66.0)

        db.set_field(rec, 'dropItems', 1, DATA_TYPE_INT)
        db._modified.add(rec)

        # Lower-level variants with proper [N, E, L] charLevel arrays
        hd_cl = db.get_field_value(rec, 'charLevel')
        if isinstance(hd_cl, (list, tuple)) and len(hd_cl) >= 3:
            hd_e_off = int(hd_cl[1]) - int(hd_cl[0])
            hd_l_off = int(hd_cl[2]) - int(hd_cl[0])
        else:
            hd_e_off, hd_l_off = 15, 28  # fallback from _41 [45,60,73]
        for dest_lvl, suffix in [(27, '_27'), (34, '_34')]:
            dest = rec.replace('_41.dbr', f'{suffix}.dbr')
            if not db.has_record(dest):
                db.clone_record(rec, dest)
                db.set_field(dest, 'charLevel',
                             [dest_lvl, dest_lvl + hd_e_off, dest_lvl + hd_l_off],
                             DATA_TYPE_INT)
                soul_p = _get_soul_paths(db, rec)
                if soul_p:
                    _wire_soul_to_monster(db, dest, soul_p, 66.0)
                db._modified.add(dest)

        ct = _add_monster_to_pools(db, rec, 'hydradon', 2, 'rottingdevourer')
        print(f"    xhero_rottingdevourer_41: soul created, {ct} pools, 2 lower variants")
    else:
        print(f"    WARNING: xhero_rottingdevourer_41 not found")


# ── Multiplayer spawn-scaling equation fix (docs/MULTIPLAYER_COMPAT.md) ──────
#
# SV 0.98i replaced the base game's monster-pool spawn-scaling equations with its
# own, more aggressive formulas that DIVIDE by numberOfPlayers, e.g.
#     spawnMaxEquation = ((poolValue * 2.3) - (poolValue / (0.4 + numberOfPlayers*0.6)))*2.7
# The tokens (poolValue, numberOfPlayers) are valid AE equation variables, and the
# '/' operator is fine in AE ITEM equations (targetLevelEquation etc. use it 822x
# in the base game). But the engine's PROXY SPAWN equation evaluator is a more
# limited code path: across the ENTIRE base TQAE database, spawn/champion pool
# equations use only  + - *  (never '/').  When the spawn evaluator hits SV's
# '/'-bearing formula it logs "RunEquation load failure" and falls back to a
# default pool value -> in MULTIPLAYER, monster/champion spawn density silently
# reverts to base-game (fewer monsters than SV intends). It is a benign,
# non-crashing, DETERMINISTIC fallback (same on host + client, so no desync), but
# it defeats SV's MP scaling. Evidence: docs/crash_analysis_report.md "Proxy
# RunEquation Failures"; tools/debug/mp_operator_audit.py (operator-set anomaly).
#
# FIX: rewrite every '/'-bearing spawn/champion equation to a '/'-free replacement
# in numberOfPlayers that reproduces SV's intended spawn count across the valid
# 1..6 player range, using only  + - *  (the operator set proven-good for the AE
# proxy-spawn evaluator: across ALL 53 distinct base-game spawn-eq forms the
# operator union is exactly {+,-,*}, max paren depth 2 -- tools/debug/
# mp_base_spawn_forms via database.arz). A binary-subtraction term is used (no
# unary-minus reliance).
#
# TWO replacement families are provided; select with the SVC_MP_SPAWN_LINEAR env
# flag (build_svc_database.py may thread it, else it defaults OFF -> quadratic):
#
#  DEFAULT = QUADRATIC  poolValue*(c0 + c1*np - c2*np*np):
#    Best fit to SV's saturating (concave) curve across the FULL 1..6 range, which
#    matters because the primary co-op case is np=2 (Will + one friend). Measured
#    error vs SV intent (tools/debug/mp_quad_pinned / mp_fit_bakeoff):
#      primary spawnMax '*2.7' form: np1=2.57%, np2=3.25%, max(1..6)=3.25%
#      pure '1/np' forms:            np1=4.40%, np2=5.32%, max(1..6)=5.32%
#    NOTE (was a doc overclaim, now corrected in docs/MULTIPLAYER_COMPAT.md): the
#    unconstrained polyfit is NOT exact at np=1 -- single-player differs by the
#    ~2.6-4.4% above. It is left UNPINNED on purpose: pinning np=1 exact is trivial
#    (constrained fit) BUT it pushes ~7-10% error onto np=2, i.e. it makes the
#    Will+friend case measurably WORSE (co-op under-delivers up to ~5 more monsters
#    at high poolValue) to buy an in-practice-invisible single-player nicety. The
#    engine FLOORS these budgets to integer counts, so the SP delta is <=1 spawn on
#    almost every pool and the replacement never REDUCES SP spawns below SV -- so
#    the honest, goal-optimal choice is the balanced unpinned fit + an accurate doc.
#
#  OPT-IN  = LINEAR  poolValue*(c0 + c1*np)   [SVC_MP_SPAWN_LINEAR=1]:
#    Structurally IDENTICAL to a real base-game spawn eq -- base game ships
#    '(poolValue * 1.6) * (0.53 +(0.2*numberOfPlayers))'  ==  poolValue*(0.848 +
#    0.32*np) -- so it uses ZERO novel structure. Exact at np=1, monotone by
#    construction, higher mid-range error (np2 ~11-16%). This is the SAFE FALLBACK
#    if a live game-log check ever shows the quadratic's  np*np  term failing to
#    parse in the narrow spawn evaluator: 'numberOfPlayers*numberOfPlayers'
#    (variable self-multiply) has NO precedent anywhere in the base game (proven:
#    0 self-multiply equations across all 74,013 base records / 16,519 equation
#    values, and the spawn evaluator has never been observed to accept it), so its
#    parseability is confirmed ONLY by an in-game launch (see MULTIPLAYER_COMPAT.md
#    M1.5 live-test). A sane arithmetic parser handles np*np and the quadratic is
#    strictly no-worse than the pre-fix '/'-parse-failure state, so it is the
#    default; flip to linear only if a launch log shows a spawn RunEquation failure.
_MP_SPAWN_EQ_FIELDS = (
    'spawnMaxEquation', 'spawnMinEquation',
    'championMaxEquation', 'championMinEquation',
    'numSpawnMaxEquation', 'numSpawnMinEquation',
)

# Exact SV equation string -> '/'-free QUADRATIC replacement (+ - * only, depth 2).
# c2 is always positive in the fit, written as a binary '-' term (idiomatic).
_MP_SPAWN_EQ_REPLACEMENTS = {
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))':
        'poolValue * (0.91 + (0.497143 * numberOfPlayers) - (0.05 * numberOfPlayers * numberOfPlayers))',
    '(poolValue * 2.3) - (poolValue / numberOfPlayers)':
        'poolValue * (0.91 + (0.497143 * numberOfPlayers) - (0.05 * numberOfPlayers * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))':
        'poolValue * (0.91 + (0.497143 * numberOfPlayers) - (0.05 * numberOfPlayers * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / (0.4 +(numberOfPlayers * 0.6))))*2.7':
        'poolValue * (2.623966 + (1.076769 * numberOfPlayers) - (0.100485 * numberOfPlayers * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))*2.7':
        'poolValue * (2.457 + (1.342286 * numberOfPlayers) - (0.135 * numberOfPlayers * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))*2':
        'poolValue * (1.82 + (0.994286 * numberOfPlayers) - (0.1 * numberOfPlayers * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))*2':
        'poolValue * (1.82 + (0.994286 * numberOfPlayers) - (0.1 * numberOfPlayers * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))*3':
        'poolValue * (2.73 + (1.491429 * numberOfPlayers) - (0.15 * numberOfPlayers * numberOfPlayers))',
}

# Exact SV equation string -> '/'-free LINEAR replacement (SVC_MP_SPAWN_LINEAR=1).
# poolValue*(c0 + c1*np): exact at np=1, monotone, base-game-idiomatic (no np*np).
# Pinned at np=1 with an LS slope over np=2..6 (tools/debug/mp_linear_design.py).
_MP_SPAWN_EQ_REPLACEMENTS_LINEAR = {
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))':
        'poolValue * (1.091818 + (0.208182 * numberOfPlayers))',
    '(poolValue * 2.3) - (poolValue / numberOfPlayers)':
        'poolValue * (1.091818 + (0.208182 * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))':
        'poolValue * (1.091818 + (0.208182 * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / (0.4 +(numberOfPlayers * 0.6))))*2.7':
        'poolValue * (3.020661 + (0.489339 * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))*2.7':
        'poolValue * (2.947909 + (0.562091 * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))*2':
        'poolValue * (2.183636 + (0.416364 * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))*2':
        'poolValue * (2.183636 + (0.416364 * numberOfPlayers))',
    '((poolValue * 2.3) - (poolValue / numberOfPlayers))*3':
        'poolValue * (3.275455 + (0.624545 * numberOfPlayers))',
}

# Safe '/'-free static fallback for any UNKNOWN '/'-bearing spawn equation that
# does not match the SV pattern (defensive; keeps the mod parseable + spawning).
# Mirrors SV's single-player intent (~2.2x poolValue) with mild player scaling,
# using only + - * (linear -> zero novel structure, always monotone).
_MP_SPAWN_EQ_FALLBACK = (
    'poolValue * (1.9 + (0.15 * numberOfPlayers))'
)


def _fix_mp_spawn_equations(db):
    """Rewrite SV's '/'-bearing proxy spawn/champion equations to '/'-free forms
    the AE spawn evaluator accepts, so multiplayer spawn scaling actually runs
    instead of silently falling back to base-game pool defaults.

    By default emits the QUADRATIC replacement (best co-op/full-range fidelity to
    SV's saturating curve). Set env SVC_MP_SPAWN_LINEAR=1 to emit the LINEAR
    replacement instead (base-game-idiomatic, no np*np term, exact at np=1) -- the
    safe fallback if a live game-log check ever shows the quadratic's np*np failing
    to parse in the narrow spawn evaluator. See the module comment above and
    docs/MULTIPLAYER_COMPAT.md M1.

    Returns the number of equation VALUES rewritten. Idempotent: replacement
    strings contain no '/', so a second pass is a no-op.
    """
    import os
    # Match build_svc_database.py's SVC_RELEASE_DROPS convention (case-insensitive
    # true-spellings). Anything else (incl. unset) -> default QUADRATIC.
    use_linear = (os.environ.get('SVC_MP_SPAWN_LINEAR') or '').strip().lower() \
        in ('1', 'true', 'yes', 'on')
    repl_table = _MP_SPAWN_EQ_REPLACEMENTS_LINEAR if use_linear else _MP_SPAWN_EQ_REPLACEMENTS
    mode = 'LINEAR (idiomatic, no np*np; np=1 exact)' if use_linear else \
           'QUADRATIC (best co-op fidelity; default)'
    print("\n=== Patch MP: Fix multiplayer spawn-scaling equations ===")
    print(f"  replacement family: {mode}")
    rewritten = 0
    records_touched = 0
    unknown_forms = {}
    for rec in db.record_names():
        fields = db.get_fields(rec)
        if not fields:
            continue
        touched_this = False
        for key, tf in list(fields.items()):
            fn = key.split('###')[0]
            if fn not in _MP_SPAWN_EQ_FIELDS:
                continue
            if tf.dtype != DATA_TYPE_STRING:
                continue
            new_vals = []
            changed = False
            for v in tf.values:
                s = str(v)
                if '/' not in s:
                    new_vals.append(s)
                    continue
                repl = repl_table.get(s.strip())
                if repl is None:
                    # Unknown '/'-bearing spawn equation: use the safe fallback so
                    # the mod stays parseable + spawning in MP. Record it loudly.
                    unknown_forms[s] = unknown_forms.get(s, 0) + 1
                    repl = _MP_SPAWN_EQ_FALLBACK
                new_vals.append(repl)
                changed = True
                rewritten += 1
            if changed:
                # Preserve single vs multi cardinality.
                if len(new_vals) == 1:
                    db.set_field(rec, fn, new_vals[0], DATA_TYPE_STRING)
                else:
                    db.set_field(rec, fn, new_vals, DATA_TYPE_STRING)
                touched_this = True
        if touched_this:
            db._modified.add(rec)
            records_touched += 1

    if unknown_forms:
        print(f"  WARNING: {len(unknown_forms)} UNKNOWN '/'-bearing spawn "
              f"equation form(s) hit the static fallback (review these):")
        for s, c in sorted(unknown_forms.items(), key=lambda kv: -kv[1]):
            print(f"    x{c}  {s!r}")
    print(f"  Rewrote {rewritten} spawn/champion equation value(s) across "
          f"{records_touched} proxy record(s) to '/'-free AE-valid form")
    return rewritten


def _verify_no_slash_in_spawn_equations(db):
    """Post-fix invariant check: assert NO spawn/champion equation field still
    contains '/'. Returns list of (record, field, value) offenders (empty = OK).
    """
    offenders = []
    for rec in db.record_names():
        fields = db.get_fields(rec)
        if not fields:
            continue
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn not in _MP_SPAWN_EQ_FIELDS or tf.dtype != DATA_TYPE_STRING:
                continue
            for v in tf.values:
                if '/' in str(v):
                    offenders.append((rec, fn, str(v)))
    return offenders


# ── Uber (DRX "supra") craftable-weapon dead-reference repair ────────────────
#
# The DRX "supra" supreme-tier craftables (records\drxitem\supra\* - Blood
# Whisper spear, Paragon of Violence, etc.) are passed through VERBATIM from the
# SV 0.98i upstream. Two dead references are baked into that upstream data by the
# original DRX authors (identical in SV098; not introduced by this port); both
# point at a record that DOES exist, so they are objectively-broken links the
# audit (docs/UBER_WEAPONS_AUDIT.md) is entitled to repair without changing any
# gameplay value, mesh, stat, or SV-authored design:
#
#   1. itemCostName = 'recordsgameitemcost_uniquelegendary_primary.dbr'
#      The leading path separators were stripped in the DRX source, so it
#      resolves to nothing and the item falls back to a default cost. The
#      intended target 'records\game\itemcost_uniquelegendary_primary.dbr' is a
#      real base-game record (the legendary-tier cost table). Present on all 23
#      supra result items.
#
#   2. xhunter_helm_galefury.dbr buffSkillName =
#      'records\drxitem\supra\skills\hunter_helm_galefurybuff.dbr'
#      The x-prefixed (xpack) galefury variant points at the NON-x buff, which
#      does not exist; the x-prefixed buff 'xhunter_helm_galefurybuff.dbr' does.
#      (The item ar_hunter_helm actually uses the non-x skill, which has no
#      buffSkillName, so its own proc was never broken - but the orphaned x
#      variant's dead edge is still a dangling ref we resolve to its obvious
#      twin.)
#
# Both fixes are EXACT-string, supra-scoped, and idempotent (a second pass finds
# nothing because the repaired value already resolves). The BMP bump-texture
# refs (*BMP.tex) on the 4 supra jewelry items are DELIBERATELY left untouched:
# no such texture file exists anywhere to point at, they are identical to SV098,
# and a missing normal-map is cosmetically inert (the engine simply skips
# normal-mapping) - inventing a texture would diverge from SV with no benefit.

_SUPRA_PREFIX = 'records\\drxitem\\supra\\'

# (record-substring-filter, field, dead-exact-value, repaired-value)
_SUPRA_DEAD_REF_FIXES = [
    (_SUPRA_PREFIX, 'itemCostName',
     'recordsgameitemcost_uniquelegendary_primary.dbr',
     'records\\game\\itemcost_uniquelegendary_primary.dbr'),
    ('records\\drxitem\\supra\\skills\\xhunter_helm_galefury.dbr', 'buffSkillName',
     'records\\drxitem\\supra\\skills\\hunter_helm_galefurybuff.dbr',
     'records\\drxitem\\supra\\skills\\xhunter_helm_galefurybuff.dbr'),
]


def _repair_supra_dead_refs(db):
    """Repair the DRX supra dead references (see the block comment above).

    EXACT-string match, supra-scoped, idempotent. Only rewrites a value that
    matches the known dead string on a record whose path contains the fix's
    record-filter substring. Returns the number of field values rewritten.
    """
    print("\n=== Patch U: Repair DRX supra craftable dead references ===")
    rewritten = 0
    records_touched = 0
    for rec_filter, field, dead, repl in _SUPRA_DEAD_REF_FIXES:
        # Safety: the intended target must actually resolve, else skip (never
        # trade one dead ref for another).
        if not _resolves_ci(db, repl):
            print(f"  SKIP {field}: repair target {repl!r} does not resolve; "
                  f"leaving dead ref untouched.")
            continue
        hits = 0
        for rec in db.record_names():
            rl = rec.replace('/', '\\').lower()
            if rec_filter.lower() not in rl:
                continue
            fields = db.get_fields(rec)
            if not fields:
                continue
            for key, tf in list(fields.items()):
                fn = key.split('###')[0]
                if fn != field or tf.dtype != DATA_TYPE_STRING or not tf.values:
                    continue
                new_vals = []
                changed = False
                for v in tf.values:
                    if isinstance(v, str) and v.replace('/', '\\').lower() == dead.lower():
                        new_vals.append(repl)
                        changed = True
                    else:
                        new_vals.append(v)
                if changed:
                    if len(new_vals) == 1:
                        db.set_field(rec, fn, new_vals[0], DATA_TYPE_STRING)
                    else:
                        db.set_field(rec, fn, new_vals, DATA_TYPE_STRING)
                    db._modified.add(rec)
                    hits += 1
                    rewritten += 1
        if hits:
            records_touched += hits
            print(f"  {field}: repaired {hits} record(s) "
                  f"({dead.split(chr(92))[-1]} -> {repl.split(chr(92))[-1]})")
    print(f"  Total supra dead references repaired: {rewritten} value(s) across "
          f"{records_touched} record(s)")
    return rewritten


def _resolves_ci(db, path):
    """Case/slash-insensitive: does `path` resolve to a record in this db?"""
    target = path.replace('/', '\\').lower()
    if not hasattr(db, '_ci_recset_cache') or db._ci_recset_cache_size != len(db.record_names()):
        db._ci_recset_cache = {n.replace('/', '\\').lower() for n in db.record_names()}
        db._ci_recset_cache_size = len(db.record_names())
    return target in db._ci_recset_cache


def _verify_no_supra_dead_refs(db):
    """Post-fix invariant: assert the specific supra dead refs we repair are gone.
    Returns list of (record, field, value) offenders still holding a known dead
    value (empty = OK). Scoped to the exact known dead strings so it never trips
    on the deliberately-preserved *BMP.tex refs."""
    offenders = []
    dead_by_field = {}
    for rec_filter, field, dead, repl in _SUPRA_DEAD_REF_FIXES:
        dead_by_field.setdefault(field, set()).add(dead.replace('/', '\\').lower())
    for rec in db.record_names():
        rl = rec.replace('/', '\\').lower()
        if _SUPRA_PREFIX not in rl:
            continue
        fields = db.get_fields(rec)
        if not fields:
            continue
        for key, tf in fields.items():
            fn = key.split('###')[0]
            deads = dead_by_field.get(fn)
            if not deads or not tf.values:
                continue
            for v in tf.values:
                if isinstance(v, str) and v.replace('/', '\\').lower() in deads:
                    offenders.append((rec, fn, v))
    return offenders


# ── Grid-portal UNCONDITIONAL OPENNESS + VISIBILITY via BORN-OPEN CLASS SWAP ──
#    (Will 2026-07-07: blood-cave hub + all invented doors invisible AND inert
#     in-game; wf_c0012e88-64a goal = "portals open from raw data, no quest") ──
# Every invented door + the whole test hub places `portal_olympianarena1.dbr` as
# the ENTRANCE. Upstream SV ships it as Class `GridEntranceDynamic` with
# `visibilityMode=NeverVisible`. TWO independent defects follow, BOTH requiring the
# bossarena.qst OnLevelLoad trigger to fire (i.e. per-character quest adoption):
#   (1) VISIBILITY: the mesh is hidden at spawn unless Action_ShowNpc fires.
#   (2) OPENNESS: the GridEntranceDynamic activate method calls SetPortalIsOpen(0)
#       UNCONDITIONALLY at every spawn (Game.dll 0x101ae2f1), so the teleport is
#       CLOSED until Action_OpenDynGridEntrance -> Open() (0x101ad910) reopens it.
# On a pre-existing char (or any char the quest never tracked) NEITHER fires ->
# portals are invisible-and-inert = exactly Will's report.
#
# ROOT CAUSE + FIX are fully disasm-proven in docs/DYNGRID_GATE_RCA.md sec 3-5
# (VAs in backups/game_dll/*.original; reproduce with tools/debug/disasm_*.py):
#  - `SetPortalIsOpen` (Engine export 0x10194d60) is CALLED from EXACTLY 3 sites in
#    ALL of Game.dll and 0 sites in Engine.dll: GridEntranceDynamic::Close (arg 0),
#    ::Open (arg 1), ::activate (arg 0). All three are the GridEntranceDynamic
#    state machine. => a STATIC `GridEntrance` (the cave-mouth class) NEVER closes
#    its portal; the Engine Portal is BORN OPEN ([+0xfc]=0x0101) and stays open.
#  - `GridEntrance` is a full instantiable Engine class used by 153 base-game
#    cave-mouth records (template Engine\GridEntrance.tpl), each ALWAYS-VISIBLE and
#    ALWAYS-OPEN with NO quest -> the decisive base-game precedent.
#  - The teleport RESOLUTION is identical for static + dynamic and reads ONLY the
#    0x14 binding: GridEntrance::GetConnectedPortalId=[this+0x2d8] (exit_uid),
#    GetConnectedRegionId=[this+0x2e8] (dest_guid); the linker pairs exit_uid to the
#    born-open GridExitOneWay landing via Region::GetPortal. NO 0x06 dependency.
#    This is the SAME pure-0x14 path A1/Sparta already rely on; the swap only
#    removes the quest-open GATE.
#
# THE FIX (this DB patch is HALF of it; the MAP half is the 48->60 byte 0x14 prefix
# in tools/build_section_surgery.py + a rebuild of BOTH map artifacts -- the two
# MUST ship together, see the COUPLING note below): swap the ENTRANCE record's Class
# from GridEntranceDynamic to the born-open static `GridEntrance`. Mirror a native
# GridEntrance cave-mouth record's minimal field set: keep mesh/scale/actorHeight/
# actorRadius, set templateName=database\Templates\Engine\GridEntrance.tpl, and DROP
# the Dynamic-only fields (visibilityMode, quest, opening/openIdleAnimationSpeed) so
# no field references a template that no longer includes it. Also update the arz
# per-record TYPE string (db._record_types[name]) to 'GridEntrance' to match Class
# (native GridEntrance records carry record_type='GridEntrance').
#
# >>> DEPLOY COUPLING (fail-loud): a class-swapped entrance record is read by the
# engine with GridEntrance::Read, which consumes a 60-byte 0x14 payload
# (12-byte (2,0,1) generic prefix + 48-byte mouth/exit/dest). Our maps historically
# wrote a BARE 48-byte 0x14 for the Dynamic class. Deploying THIS arz against a map
# whose portal 0x14 is still 48 bytes would make GridEntrance::Read eat 12 bytes of
# the binding and MISALIGN (visible-but-inert or worse). So this arz change is only
# valid paired with a map rebuilt by the current build_section_surgery.py (which
# emits 60-byte entrance 0x14). The _verify_portals_born_open invariant asserts the
# DB half; the map gate (tools/debug/gate_portal_openness.py) asserts the map half.
#
# NO base-game collateral: portal_olympianarena1/2 are placed ZERO times in the
# base-game map (tools/debug/count_portal_instances.py on the base Levels.arc = 0/0)
# -> changing the record's class/fields has no vanilla side effect.
_PORTAL_ENTRANCE_DBRS = [
    r'records\quests\portal_olympianarena1.dbr',
    # aliases the upstream SV tree also carries (kept for completeness; only the
    # base name is placed in the maps, but patch every casing/variant that exists)
    r'records\quests\portal_olympianarena1x.dbr',
]

# The native minimal GridEntrance record shape (mirrors silkrddngentrance_c01_ext):
# Class GridEntrance + templateName Engine\GridEntrance.tpl + mesh/scale/actor*.
_GRIDENTRANCE_TEMPLATE = r'database\Templates\Engine\GridEntrance.tpl'

# B-PORTAL-1 (VISUAL, DB-lane only). The born-open portal rendered as a flat blue
# panel because its mesh (TJ_JudgementRoom_PortalObject_01) is a NeverVisible,
# QUEST-SHOWN Dynamic-portal mesh whose swirl is its OPEN-IDLE ANIMATION; on the
# born-open STATIC GridEntrance (which never plays an idle anim) that mesh collapses
# to a near-invisible quad, leaving only the engine's blue entrance-plane + arrow.
# A static GridEntrance is MESH-ONLY (DB-verified: 0 of 153 base static GridEntrance
# records carry any fx/light/portal-glow field - there is NO DB-side FX field to
# set), so the mesh is the only visual lever.
#
# build29 (A2): build28 shipped HC_GoldMirror01.msh here, which turned out to be a
# REGRESSION - it is a large SOLID 3D "gold mirror" object (73,318 B mesh in
# SceneryUnderground.arc) whose collision AABB straddles the walkway, so the portal
# physically BLOCKS passage / force-teleports the player (Will, build28 public). The
# fix is a THIN glowing portal PANE: XPack\SceneryHades\Structure\Building\SetDress\
# Elysium_from_TOJ_PortalObject_01.msh - a 1,428 B upright pane (verified present in
# base-game SceneryHades.arc) whose depth is thin (D~1.7u << 2.5u), so it renders as a
# visible portal without obstructing the tunnel. It is the SAME size-class of pane as
# the build27 proven-teleporting TJ_JudgementRoom_PortalObject_01.msh (also 1,428 B,
# ships in drx.arc) - kept as the FALLBACK below if Elysium reads wrong in-game.
# CAVEAT (honest): our record is a base STATIC GridEntrance; whether the pane renders
# attractively on the static class is NOT provable from the DB and needs Will's in-game
# confirmation (needs_will_signoff / BACKLOG B-PORTAL-1). visibilityMode/openness/
# class/0x14 (the map-lane born-open mechanics) are NOT touched.
_PORTAL_VISUAL_MESH = r'XPack\SceneryHades\Structure\Building\SetDress\Elysium_from_TOJ_PortalObject_01.msh'
# Dynamic-only fields to strip on the swapped record (not in the GridEntrance
# template's include chain). Leaving them would reference a non-existent template
# field. mesh/scale/actorHeight/actorRadius are shared (Tile include) and KEPT.
_DYNAMIC_ONLY_FIELDS = (
    'visibilityMode', 'quest', 'openingAnimationSpeed', 'openIdleAnimationSpeed',
    'allowUnconnected', 'openingAnimation', 'openIdleAnimation', 'openIdleSound',
    'openingSound', 'sound1', 'sound2', 'sound3', 'sound4', 'sound5',
    'lightName', 'lightAttachPointName', 'lightFadeInTime',
)


def _resolve_record(db, path):
    """Return the actual record key matching path (tolerating '/'-vs-'\\' + case)."""
    if db.has_record(path):
        return path
    want = path.replace('/', '\\').lower()
    for cand in db.record_names():
        if cand.replace('/', '\\').lower() == want:
            return cand
    return None


def _make_portals_born_open_gridentrance(db):
    """Swap the shared portal ENTRANCE record from Class GridEntranceDynamic to the
    born-open static `GridEntrance`, so every invented-door + test-hub portal renders
    AND teleports at spawn with NO quest dependency (fresh AND pre-existing chars).
    Returns the number of records swapped. Idempotent (re-running on an already-
    GridEntrance record is a no-op).

    Requires the MAP half (60-byte entrance 0x14); see the module comment COUPLING
    note. The LANDING record portal_olympianarena2 (Class GridExitOneWay) is already
    born-open + invisibleInWorld=1 and is left UNTOUCHED (its 48-byte 0x14 is
    correct for GridExitOneWay).
    """
    print("\n=== Patch: grid portal ENTRANCE -> born-open GridEntrance "
          "(unconditional open + visible, no quest) ===")
    swapped = 0
    for path in _PORTAL_ENTRANCE_DBRS:
        rec = _resolve_record(db, path)
        if rec is None:
            continue
        cls = db.get_field_value(rec, 'Class')
        if cls == 'GridEntrance':
            print(f"  SKIP {rec}: already Class=GridEntrance (idempotent no-op)")
            continue
        if cls not in ('GridEntranceDynamic', 'DynGridEntrance'):
            print(f"  SKIP {rec}: Class={cls!r} (not a dynamic grid entrance)")
            continue
        mesh = db.get_field_value(rec, 'mesh')
        # 1) Class + templateName -> static GridEntrance
        db.set_field(rec, 'Class', 'GridEntrance', DATA_TYPE_STRING)
        db.set_field(rec, 'templateName', _GRIDENTRANCE_TEMPLATE, DATA_TYPE_STRING)
        # 2) drop every Dynamic-only field (not in the GridEntrance template chain)
        fields = db.get_fields(rec)
        dropped = []
        if fields is not None:
            for fname in list(fields.keys()):
                base = fname.split('###')[0]
                if base in _DYNAMIC_ONLY_FIELDS:
                    del fields[fname]
                    dropped.append(base)
            db._modified.add(rec)
        # 3) update the arz per-record TYPE string to match the Class (native
        #    GridEntrance records carry record_type='GridEntrance')
        old_type = db._record_types.get(rec)
        db._record_types[rec] = 'GridEntrance'
        db._modified.add(rec)
        print(f"  {rec}: Class GridEntranceDynamic -> GridEntrance; "
              f"record_type {old_type!r} -> 'GridEntrance'; "
              f"dropped {dropped}; mesh kept={mesh!r}")
        swapped += 1
    if swapped == 0:
        print("  (no dynamic-entrance record to swap; may already be GridEntrance)")
    return swapped


def _apply_portal_visual(db):
    """B-PORTAL-1 (VISUAL, DB-lane): repoint the portal ENTRANCE mesh to
    _PORTAL_VISUAL_MESH (Elysium_from_TOJ_PortalObject_01.msh, a thin glowing portal pane;
    see the _PORTAL_VISUAL_MESH block for the donor + the static-class caveat) so it renders as
    a visible portal object instead of the flat blue panel the prior quest-shown TJ mesh
    produced on the static class. Iterates _PORTAL_ENTRANCE_DBRS, so it repoints BOTH
    portal_olympianarena1 (the placed born-open GridEntrance) AND portal_olympianarena1x
    (an unplaced FixedItemTeleport - repointed defensively; it is placed 0 times in
    either map, so this has no in-game effect). VISUAL-ONLY: does NOT touch Class /
    openness / visibilityMode / the 60-byte 0x14 (the map-lane born-open mechanics).
    Idempotent. Run AFTER _make_portals_born_open_gridentrance (which keeps the old mesh)."""
    n = 0
    for path in _PORTAL_ENTRANCE_DBRS:
        rec = _resolve_record(db, path)
        if rec is None:
            continue
        db.set_field(rec, 'mesh', _PORTAL_VISUAL_MESH, DATA_TYPE_STRING)
        db._modified.add(rec)
        n += 1
    print(f"  Portal visual (B-PORTAL-1): mesh -> {_PORTAL_VISUAL_MESH} on {n} record(s)")
    return n


def _verify_portals_born_open(db):
    """Invariant: after the swap, the placed entrance record is a static GridEntrance
    (born-open, always-visible) with NO Dynamic-only fields left, its templateName is
    the GridEntrance template, and its arz record_type matches. Also (B-PORTAL-1)
    asserts the VISUAL mesh is the intended always-visible portal mesh. Returns a list
    of offenders (empty == PASS). Checks portal_olympianarena1 (the record placed in
    the maps)."""
    offenders = []
    path = r'records\quests\portal_olympianarena1.dbr'
    rec = _resolve_record(db, path)
    if rec is None:
        return [(path, 'MISSING', None)]
    cls = db.get_field_value(rec, 'Class')
    if cls != 'GridEntrance':
        offenders.append((rec, 'Class', cls))
    tpl = (db.get_field_value(rec, 'templateName') or '')
    if tpl.replace('/', '\\').lower() != _GRIDENTRANCE_TEMPLATE.lower():
        offenders.append((rec, 'templateName', tpl))
    rt = db._record_types.get(rec)
    if rt != 'GridEntrance':
        offenders.append((rec, 'record_type', rt))
    for f in _DYNAMIC_ONLY_FIELDS:
        if db.get_field_value(rec, f) is not None:
            offenders.append((rec, f'residual:{f}', db.get_field_value(rec, f)))
    # B-PORTAL-1: the mesh is the ONLY DB-side visual field on a static GridEntrance,
    # so assert it is the intended always-visible portal mesh (not empty, not the
    # flat/near-invisible quest-shown TJ quad that produced the blue-panel look).
    mesh = (db.get_field_value(rec, 'mesh') or '')
    if not mesh:
        offenders.append((rec, 'mesh', 'MISSING (portal would be invisible)'))
    elif mesh.replace('/', '\\').lower() != _PORTAL_VISUAL_MESH.lower():
        offenders.append((rec, 'mesh',
                          f'{mesh!r} != intended portal visual {_PORTAL_VISUAL_MESH!r}'))
    return offenders


# ── A4 (build36, Will 2026-07-11): Aphiastas Finger2 zero ────────────────────
# Will's order (live blood-cave testing): the Aphiastas keres bodies must STOP
# dropping the Aphiastas soul. Close the leak PROPERLY (not cosmetically): set
# chanceToEquipFinger2=0 on every Aphiastas keres record whose Finger2 loot is
# souls-ONLY, WITHOUT touching the lootFinger2Item refs (Will was informed of the
# aphiastas-soul / potion-recipe coupling; the soul-loot ref + any recipe stay
# intact, only the DROP CHANCE goes to 0). Runs BEFORE the drop-rate forcer so the
# forcer's chance>0 gate leaves these at 0 in BOTH testing and release builds.
# Fail-loud if a record is missing OR its Finger2 loot is NOT souls-only (never
# zero a slot that would strip a non-soul reward).
_APHIASTAS_FINGER2_ZERO = [
    r'records\xpack\creatures\monster\keres\um_afaistas_46.dbr',
    r'records\xpack\creatures\monster\keres\copy of uw_ar_huntress_40.dbr',
    r'records\xpack\creatures\monster\keres\copy of uw_ar_huntress_46.dbr',
    r'records\xpack\creatures\monster\keres\xsq09_am_scavenger_37.dbr',
    r'records\xpack\creatures\monster\keres\xsq09_am_scavenger_39.dbr',
    r'records\xpack\creatures\monster\keres\xsq09_ar_huntress_36.dbr',
    r'records\xpack\creatures\monster\keres\xsq09_ar_huntress_38.dbr',
]


def _apply_aphiastas_finger2_zero(db):
    """A4: set chanceToEquipFinger2=0 on the Aphiastas keres records after proving
    each one's Finger2 loot is souls-only. Leaves lootFinger2Item refs + any potion
    formula untouched. Fail-loud on a missing record or a non-souls-only Finger2
    slot. Uses exact-path resolution (never the substring _find_record)."""
    zeroed = 0
    for path in _APHIASTAS_FINGER2_ZERO:
        rec = _resolve_record(db, path)
        if rec is None:
            raise SystemExit(f"A4 Aphiastas-zero: record missing (exact): {path}")
        f2 = db.get_field_value(rec, 'lootFinger2Item1')
        f2 = f2 if isinstance(f2, list) else [f2]
        refs = [str(v) for v in f2 if v and str(v).strip()]
        if not refs:
            raise SystemExit(f"A4 Aphiastas-zero: {path} has EMPTY Finger2 loot "
                             f"(refusing to zero - nothing to gate)")
        non_soul = [v for v in refs if 'soul' not in v.lower()]
        if non_soul:
            raise SystemExit(f"A4 Aphiastas-zero: {path} Finger2 loot is NOT "
                             f"souls-only (non-soul refs: {non_soul}); refusing "
                             f"to zero (would strip a non-soul reward)")
        # existing FLOAT field -> no dtype (dtype-safe). lootFinger2Item refs kept.
        db.set_field(rec, 'chanceToEquipFinger2', 0.0)
        db._modified.add(rec)
        zeroed += 1
    print(f"  A4 Aphiastas-zero: chanceToEquipFinger2=0 on {zeroed}/"
          f"{len(_APHIASTAS_FINGER2_ZERO)} keres records (souls-only Finger2 "
          f"verified; loot refs + any potion formula untouched)")


def _force_100_pct_soul_drops(db):
    """Set chanceToEquipFinger2 to 100% for TESTING - but ONLY on monsters that
    are already configured to drop a soul (chanceToEquipFinger2 > 0).

    wire_souls_to_monsters() gates soul drops to Hero/Boss/Quest and forces
    Common/Champion (e.g. normal yetis, which inherit lootFinger2Item1=yeti_soul
    from base SV) to chanceToEquipFinger2=0. Keying the 100% boost off the
    soul-loot field alone would re-enable exactly those - the normal-yeti bug
    (every common yeti dropping a soul). Gating on the existing chance keeps the
    classification gate intact: only monsters meant to drop get boosted to 100%.
    """
    count = 0
    skipped = 0
    for rec in db.record_names():
        if 'creature' not in rec.lower():
            continue
        fields = db.get_fields(rec)
        if not fields:
            continue
        has_soul = False
        cur_chance = 0.0
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn == 'lootFinger2Item1' and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'soul' in v.lower():
                        has_soul = True
                        break
            elif fn == 'chanceToEquipFinger2' and tf.values:
                try:
                    cur_chance = float(tf.values[0])
                except (TypeError, ValueError):
                    cur_chance = 0.0
        if has_soul and cur_chance > 0:
            db.set_field(rec, 'chanceToEquipFinger2', 100.0, DATA_TYPE_FLOAT)
            db.set_field(rec, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
            db.set_field(rec, 'dropItems', 1, DATA_TYPE_INT)
            db._modified.add(rec)
            count += 1
        elif has_soul:
            # soul-loot present but drop gated off (Common/Champion) - leave at 0
            skipped += 1
    print(f"  Soul drop rate forced to 100% on {count} monster records (TESTING)")
    print(f"  Left gated-off (Common/Champion, no drop): {skipped}")


def _overhaul_generic_souls(db):
    """Overhaul all 78 generic/weak souls with thematic skills and abilities."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    SEP = chr(92)
    print("\n  Overhauling generic/weak souls:")

    # ── Design specs: {soul_path_substring: {field: (dtype, val)}} ──
    # Each entry overwrites fields on the _n, _e, and _l variants with scaling.
    # Format: (n_val, e_val, l_val) for tiered stats, or single val for flat.

    OVERHAULS = {
        # ══════════════════════════════════════════════════════════════════
        # SATYR GROUP — Physical/Fire warriors of Greece and Hades
        # ══════════════════════════════════════════════════════════════════

        # Satyr Scout — fast, light attacker
        'satyrpawn_soul': {
            'offensivePhysicalMin': (F, 15.0), 'offensivePhysicalMax': (F, 28.0),
            'offensivePierceRatioModifier': (I, 12),
            'characterDexterityModifier': (F, 6.0),
            'characterAttackSpeedModifier': (F, 10.0),
            'characterRunSpeedModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_LETHAL_STRIKE), 'augmentSkillLevel1': (I, 1),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Satyr Warrior — solid melee
        'satyrsoldier_soul': {
            'offensivePhysicalMin': (F, 18.0), 'offensivePhysicalMax': (F, 32.0),
            'characterStrengthModifier': (F, 6.0),
            'characterLifeModifier': (F, 8.0),
            'characterOffensiveAbility': (F, 40.0),
            'characterDefensiveAbility': (F, 40.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Satyr Peltast — shield bearer, defensive
        'satyrpeltast_soul': {
            'offensivePhysicalMin': (F, 12.0), 'offensivePhysicalMax': (F, 22.0),
            'offensivePierceMin': (F, 8.0), 'offensivePierceMax': (F, 16.0),
            'characterDefensiveAbility': (F, 50.0),
            'defensivePierce': (F, 10.0),
            'defensiveProtection': (F, 15.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_SONIC_WAVE),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Satyr Elite Peltast
        'satyrelitepeltast_soul': {
            'offensivePhysicalMin': (F, 16.0), 'offensivePhysicalMax': (F, 28.0),
            'offensivePierceMin': (F, 10.0), 'offensivePierceMax': (F, 20.0),
            'characterDefensiveAbility': (F, 60.0),
            'defensivePierce': (F, 14.0),
            'defensiveProtection': (F, 20.0),
            'characterLifeModifier': (F, 6.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 3),
            'itemSkillName': (S, _SS_SONIC_WAVE),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Satyr Veteran Peltast
        'satyrveteranpeltast_soul': {
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 35.0),
            'offensivePierceMin': (F, 12.0), 'offensivePierceMax': (F, 24.0),
            'characterDefensiveAbility': (F, 70.0),
            'defensivePierce': (F, 18.0),
            'defensiveProtection': (F, 25.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_SONIC_WAVE),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Satyr Veteran Warrior
        'satyrveteransoldier_soul': {
            'offensivePhysicalMin': (F, 25.0), 'offensivePhysicalMax': (F, 42.0),
            'characterStrengthModifier': (F, 8.0),
            'characterLifeModifier': (F, 10.0),
            'characterOffensiveAbility': (F, 60.0),
            'offensivePhysicalModifier': (I, 15),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Satyr Brute — heavy tank
        'satyrchampion_soul': {
            'offensivePhysicalMin': (F, 22.0), 'offensivePhysicalMax': (F, 40.0),
            'offensiveStunMin': (F, 0.5), 'offensiveStunMax': (F, 1.5),
            'offensiveStunChance': (F, 15.0),
            'characterStrengthModifier': (F, 10.0),
            'characterLifeModifier': (F, 12.0),
            'augmentSkillName1': (S, _SK_WAR_HORN), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Satyr Magi — caster
        'satyrmagi_soul': {
            'offensiveFireMin': (F, 20.0), 'offensiveFireMax': (F, 38.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterManaModifier': (F, 10.0),
            'characterSpellCastSpeedModifier': (F, 12.0),
            'augmentSkillName1': (S, _SK_FIRE_ENCHANT), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_FIRE_NOVA),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Satyr Spirit Caller — life/spirit caster
        'satyrspiritcaller_soul': {
            'offensiveLifeMin': (F, 15.0), 'offensiveLifeMax': (F, 30.0),
            'characterIntelligenceModifier': (F, 6.0),
            'characterManaModifier': (F, 8.0),
            'characterManaRegenModifier': (F, 50.0),
            'augmentSkillName1': (S, _SK_SPIRIT_WARD), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_DARK_COVENANT), 'augmentSkillLevel2': (I, 1),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },

        # ══════════════════════════════════════════════════════════════════
        # DARK SATYR GROUP — Fire/Shadow variants in Hades
        # ══════════════════════════════════════════════════════════════════

        'darksatyrpeltast_soul': {
            'offensiveFireMin': (F, 12.0), 'offensiveFireMax': (F, 22.0),
            'offensivePhysicalMin': (F, 10.0), 'offensivePhysicalMax': (F, 18.0),
            'characterDefensiveAbility': (F, 40.0),
            'defensiveFire': (F, 15.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_FIRE_NOVA),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'darksatyrelitepeltast_soul': {
            'offensiveFireMin': (F, 16.0), 'offensiveFireMax': (F, 30.0),
            'offensivePhysicalMin': (F, 14.0), 'offensivePhysicalMax': (F, 24.0),
            'characterDefensiveAbility': (F, 55.0),
            'defensiveFire': (F, 20.0),
            'characterLifeModifier': (F, 6.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 3),
            'itemSkillName': (S, _SS_FIRE_NOVA),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'darksatyrveteranpeltast_soul': {
            'offensiveFireMin': (F, 20.0), 'offensiveFireMax': (F, 38.0),
            'offensivePhysicalMin': (F, 16.0), 'offensivePhysicalMax': (F, 30.0),
            'characterDefensiveAbility': (F, 65.0),
            'defensiveFire': (F, 25.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_FIRE_ENCHANT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_FIRE_NOVA),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'darksatyrelitesoldier_soul': {
            'offensiveFireMin': (F, 18.0), 'offensiveFireMax': (F, 35.0),
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 36.0),
            'characterStrengthModifier': (F, 8.0),
            'characterOffensiveAbility': (F, 45.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_FIRE_ENCHANT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_FIRE_NOVA),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'darksatyrspiritcaller_soul': {
            'offensiveLifeMin': (F, 20.0), 'offensiveLifeMax': (F, 38.0),
            'offensiveFireMin': (F, 12.0), 'offensiveFireMax': (F, 22.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterManaRegenModifier': (F, 55.0),
            'augmentSkillName1': (S, _SK_DARK_COVENANT), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_SPIRIT_WARD), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },

        # ══════════════════════════════════════════════════════════════════
        # MOUNTAIN SATYR GROUP — Cold/Physical, from icy mountains
        # ══════════════════════════════════════════════════════════════════

        'mountainsatyrsoldier_soul': {
            'offensiveColdMin': (F, 14.0), 'offensiveColdMax': (F, 26.0),
            'offensivePhysicalMin': (F, 12.0), 'offensivePhysicalMax': (F, 22.0),
            'characterStrengthModifier': (F, 6.0),
            'defensiveCold': (F, 15.0),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'mountainsatyrpeltast_soul': {
            'offensiveColdMin': (F, 10.0), 'offensiveColdMax': (F, 20.0),
            'offensivePierceMin': (F, 10.0), 'offensivePierceMax': (F, 18.0),
            'characterDefensiveAbility': (F, 50.0),
            'defensiveCold': (F, 18.0), 'defensivePierce': (F, 10.0),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_SONIC_WAVE),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'mountainsatyrelitesoldier_soul': {
            'offensiveColdMin': (F, 20.0), 'offensiveColdMax': (F, 36.0),
            'offensivePhysicalMin': (F, 16.0), 'offensivePhysicalMax': (F, 30.0),
            'characterStrengthModifier': (F, 8.0),
            'characterLifeModifier': (F, 8.0),
            'defensiveCold': (F, 22.0),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'mountainsatyrveteranpeltast_soul': {
            'offensiveColdMin': (F, 16.0), 'offensiveColdMax': (F, 30.0),
            'offensivePierceMin': (F, 14.0), 'offensivePierceMax': (F, 26.0),
            'characterDefensiveAbility': (F, 65.0),
            'defensiveCold': (F, 24.0), 'defensivePierce': (F, 14.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel2': (I, 3),
            'itemSkillName': (S, _SS_SONIC_WAVE),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'mountainsatyrveteransoldier_soul': {
            'offensiveColdMin': (F, 24.0), 'offensiveColdMax': (F, 42.0),
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 36.0),
            'characterStrengthModifier': (F, 10.0),
            'characterLifeModifier': (F, 10.0),
            'defensiveCold': (F, 28.0),
            'offensiveFreezeMin': (F, 0.5), 'offensiveFreezeMax': (F, 1.5),
            'offensiveFreezeChance': (F, 10.0),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 3),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },

        # ══════════════════════════════════════════════════════════════════
        # MAENAD GROUP — Pierce/Bleed fast attackers
        # ══════════════════════════════════════════════════════════════════

        'maenadscout_soul': {
            'offensivePierceMin': (F, 14.0), 'offensivePierceMax': (F, 28.0),
            'offensiveSlowBleedingMin': (F, 30.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 8.0),
            'characterAttackSpeedModifier': (F, 12.0),
            'characterDodgePercent': (F, 5.0),
            'augmentSkillName1': (S, _SK_STUDY_PREY), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'maenadtracker_soul': {
            'offensivePierceMin': (F, 16.0), 'offensivePierceMax': (F, 32.0),
            'offensiveSlowBleedingMin': (F, 40.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 10.0),
            'characterAttackSpeedModifier': (F, 14.0),
            'characterDodgePercent': (F, 6.0),
            'augmentSkillName1': (S, _SK_STUDY_PREY), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_CALCULATED_STRIKE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'maenadvanguard_soul': {
            'offensivePierceMin': (F, 18.0), 'offensivePierceMax': (F, 36.0),
            'offensiveSlowBleedingMin': (F, 50.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 12.0),
            'characterAttackSpeedModifier': (F, 16.0),
            'characterDodgePercent': (F, 8.0),
            'characterRunSpeedModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_STUDY_PREY), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_CALCULATED_STRIKE), 'augmentSkillLevel2': (I, 3),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },

        # ══════════════════════════════════════════════════════════════════
        # BAT GROUP — Life leech, speed, evasion
        # ══════════════════════════════════════════════════════════════════

        'goatsucker_soul': {  # Lv7 early game
            'offensiveLifeMin': (F, 5.0), 'offensiveLifeMax': (F, 10.0),
            'characterLifeRegenModifier': (F, 10.0),
            'characterRunSpeedModifier': (F, 10.0),
            'characterDodgePercent': (F, 4.0),
            'augmentSkillName1': (S, _SK_ENVENOM), 'augmentSkillLevel1': (I, 1),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'leatherwing_soul': {  # Lv11
            'offensiveLifeMin': (F, 8.0), 'offensiveLifeMax': (F, 16.0),
            'characterDexterityModifier': (F, 5.0),
            'characterRunSpeedModifier': (F, 12.0),
            'characterDodgePercent': (F, 6.0),
            'defensiveCold': (F, 15.0),
            'augmentSkillName1': (S, _SK_ENVENOM), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'elephantsnatcher_soul': {  # Lv17
            'offensiveLifeMin': (F, 12.0), 'offensiveLifeMax': (F, 24.0),
            'offensivePhysicalMin': (F, 10.0), 'offensivePhysicalMax': (F, 20.0),
            'characterAttackSpeedModifier': (F, 15.0),
            'characterRunSpeedModifier': (F, 12.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'cavebat_soul': {  # Lv44
            'offensiveLifeMin': (F, 20.0), 'offensiveLifeMax': (F, 38.0),
            'characterDexterityModifier': (F, 8.0),
            'characterDodgePercent': (F, 8.0),
            'characterRunSpeedModifier': (F, 10.0),
            'augmentSkillName1': (S, _SK_DARK_COVENANT), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'giganticbat_soul': {  # Lv44
            'offensiveLifeMin': (F, 25.0), 'offensiveLifeMax': (F, 45.0),
            'offensivePhysicalMin': (F, 15.0), 'offensivePhysicalMax': (F, 28.0),
            'characterStrengthModifier': (F, 8.0),
            'characterDodgePercent': (F, 6.0),
            'characterAttackSpeedModifier': (F, 12.0),
            'augmentSkillName1': (S, _SK_DARK_COVENANT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },

        # ══════════════════════════════════════════════════════════════════
        # CARRION BIRD GROUP — Pierce/Bleed aerial predators
        # ══════════════════════════════════════════════════════════════════

        'bloodwing_soul': {  # Both Lv12 and Lv44 versions
            'offensivePierceMin': (F, 14.0), 'offensivePierceMax': (F, 28.0),
            'offensiveSlowBleedingMin': (F, 40.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterAttackSpeedModifier': (F, 15.0),
            'characterRunSpeedModifier': (F, 12.0),
            'characterDodgePercent': (F, 6.0),
            'augmentSkillName1': (S, _SK_STUDY_PREY), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'carrioncrow_soul': {
            'offensivePierceMin': (F, 10.0), 'offensivePierceMax': (F, 22.0),
            'offensiveSlowBleedingMin': (F, 35.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 6.0),
            'characterRunSpeedModifier': (F, 10.0),
            'augmentSkillName1': (S, _SK_CALCULATED_STRIKE), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        'carrionlord_soul': {
            'offensivePierceMin': (F, 18.0), 'offensivePierceMax': (F, 34.0),
            'offensiveSlowBleedingMin': (F, 55.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 10.0),
            'characterAttackSpeedModifier': (F, 14.0),
            'characterDodgePercent': (F, 8.0),
            'augmentSkillName1': (S, _SK_STUDY_PREY), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_CALCULATED_STRIKE), 'augmentSkillLevel2': (I, 3),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },

        # ══════════════════════════════════════════════════════════════════
        # BOAR GROUP — Physical chargers, stun
        # ══════════════════════════════════════════════════════════════════

        'sow_soul': {  # Lv7 early
            'offensivePhysicalMin': (F, 6.0), 'offensivePhysicalMax': (F, 12.0),
            'offensiveSlowBleedingMin': (F, 15.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterLifeModifier': (F, 5.0),
            'characterStrengthModifier': (F, 3.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 1),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'duskyboar_soul': {
            'offensivePhysicalMin': (F, 22.0), 'offensivePhysicalMax': (F, 40.0),
            'offensiveStunMin': (F, 0.5), 'offensiveStunMax': (F, 1.5),
            'offensiveStunChance': (F, 12.0),
            'characterStrengthModifier': (F, 8.0),
            'characterLifeModifier': (F, 10.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_WAR_HORN), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'ravenousboar_soul': {
            'offensivePhysicalMin': (F, 18.0), 'offensivePhysicalMax': (F, 34.0),
            'offensiveSlowBleedingMin': (F, 45.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'characterStrengthModifier': (F, 7.0),
            'characterLifeModifier': (F, 8.0),
            'characterAttackSpeedModifier': (F, 10.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },

        # ══════════════════════════════════════════════════════════════════
        # GORGON GROUP — Poison/Pierce, petrification
        # ══════════════════════════════════════════════════════════════════

        'gorgonarcher_soul': {
            'offensivePierceMin': (F, 22.0), 'offensivePierceMax': (F, 40.0),
            'offensiveSlowPoisonMin': (F, 15.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 10.0),
            'characterOffensiveAbility': (F, 50.0),
            'augmentSkillName1': (S, _SK_STUDY_PREY), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        'gorgonguard_soul': {
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 38.0),
            'offensiveSlowPoisonMin': (F, 20.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterStrengthModifier': (F, 8.0),
            'characterDefensiveAbility': (F, 60.0),
            'defensivePoison': (F, 20.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 3),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },

        # ══════════════════════════════════════════════════════════════════
        # INDIVIDUAL NAMED MONSTERS — Unique overhauls
        # ══════════════════════════════════════════════════════════════════

        # Pandarus — cunning eurynomus, dodge and strike
        'pandarus_soul': {
            'offensivePhysicalMin': (F, 8.0), 'offensivePhysicalMax': (F, 16.0),
            'offensiveLifeMin': (F, 5.0), 'offensiveLifeMax': (F, 10.0),
            'characterDexterityModifier': (F, 4.0),
            'characterDodgePercent': (F, 5.0),
            'augmentSkillName1': (S, _SK_ENVENOM), 'augmentSkillLevel1': (I, 1),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Alossos Tonefist — early satyr hero
        'alosstonefist_soul': {
            'offensivePhysicalMin': (F, 10.0), 'offensivePhysicalMax': (F, 20.0),
            'offensiveStunMin': (F, 0.3), 'offensiveStunMax': (F, 1.0),
            'offensiveStunChance': (F, 10.0),
            'characterStrengthModifier': (F, 5.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 1),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Old Snapper — giant turtle, tanky
        'oldsnapper_soul': {
            'offensivePhysicalMin': (F, 8.0), 'offensivePhysicalMax': (F, 16.0),
            'characterLifeModifier': (F, 12.0),
            'defensiveProtection': (F, 20.0),
            'defensivePierce': (F, 12.0),
            'characterTotalSpeedModifier': (F, -5.0),
            'augmentSkillName1': (S, _SK_HEART_OF_OAK), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Wraithwing — vulture, pierce and speed
        'wraithwing_soul': {
            'offensivePierceMin': (F, 16.0), 'offensivePierceMax': (F, 30.0),
            'characterDodgePercent': (F, 8.0),
            'characterRunSpeedModifier': (F, 14.0),
            'offensivePierceRatioModifier': (I, 25),
            'augmentSkillName1': (S, _SK_CALCULATED_STRIKE), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Slabskin — guardian statue, stone tank
        'slabskin_soul': {
            'offensivePhysicalMin': (F, 16.0), 'offensivePhysicalMax': (F, 30.0),
            'characterLifeModifier': (F, 12.0),
            'characterStrengthModifier': (F, 8.0),
            'defensiveProtection': (F, 25.0),
            'defensivePierce': (F, 15.0),
            'characterAttackSpeedModifier': (F, -10.0),
            'augmentSkillName1': (S, _SK_EARTH_ENCHANT), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Spikeclaw — scorpos, poison/physical
        'spikeclaw_soul': {
            'offensivePhysicalMin': (F, 14.0), 'offensivePhysicalMax': (F, 26.0),
            'offensiveSlowPoisonMin': (F, 20.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterOffensiveAbility': (F, 40.0),
            'defensivePoison': (F, 18.0),
            'augmentSkillName1': (S, _SK_ENVENOM), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Fluxfang — raptor, fast pierce attacker
        'fluxfang_soul': {
            'offensivePierceMin': (F, 18.0), 'offensivePierceMax': (F, 34.0),
            'characterDexterityModifier': (F, 10.0),
            'characterAttackSpeedModifier': (F, 14.0),
            'characterRunSpeedModifier': (F, 10.0),
            'characterOffensiveAbility': (F, 40.0),
            'augmentSkillName1': (S, _SK_LETHAL_STRIKE), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_STUDY_PREY), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Sentinel — elemental construct, physical powerhouse
        'sentinel_soul': {
            'offensivePhysicalMin': (F, 25.0), 'offensivePhysicalMax': (F, 45.0),
            'offensiveLightningMin': (F, 12.0), 'offensiveLightningMax': (F, 24.0),
            'characterStrengthModifier': (F, 10.0),
            'characterLifeModifier': (F, 10.0),
            'offensivePhysicalModifier': (I, 20),
            'augmentSkillName1': (S, _SK_STORM_NIMBUS), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Komara — zombie, undead caster
        'komara_soul': {
            'offensiveLifeMin': (F, 18.0), 'offensiveLifeMax': (F, 34.0),
            'offensiveSlowPoisonMin': (F, 15.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterStrengthModifier': (F, 6.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_NECROSIS), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_ZOMBIE_SUMMON),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Phyraxus — raptor, bleed/cold
        'phyraxus_soul': {
            'offensivePhysicalMin': (F, 14.0), 'offensivePhysicalMax': (F, 28.0),
            'offensiveSlowBleedingMin': (F, 40.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveColdMin': (F, 10.0), 'offensiveColdMax': (F, 20.0),
            'characterDexterityModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Darkmarsh — bog dweller, poison/nature
        'darkmarsh_soul': {
            'offensiveSlowPoisonMin': (F, 30.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'characterLifeModifier': (F, 8.0),
            'characterLifeRegenModifier': (F, 10.0),
            'defensivePoison': (F, 25.0),
            'augmentSkillName1': (S, _SK_PLAGUE), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_HEART_OF_OAK), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Hodesugo — ghost, ethereal dream caster
        'hodesugo_soul': {
            'offensiveLifeMin': (F, 18.0), 'offensiveLifeMax': (F, 34.0),
            'characterIntelligenceModifier': (F, 10.0),
            'characterSpellCastSpeedModifier': (F, 20.0),
            'characterDodgePercent': (F, 8.0),
            'defensiveLife': (F, 30.0),
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_DISTORTION_WAVE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Bloodfang — arachnos spider, bleed/poison
        'bloodfang_soul': {
            'offensiveSlowBleedingMin': (F, 50.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowPoisonMin': (F, 20.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterDexterityModifier': (F, 8.0),
            'defensivePoison': (F, 20.0),
            'augmentSkillName1': (S, _SK_ENVENOM), 'augmentSkillLevel1': (I, 3),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Shadefeaster — hydradon, resistance tank
        'shadefeaster_soul': {
            'offensivePhysicalMin': (F, 18.0), 'offensivePhysicalMax': (F, 34.0),
            'offensiveLifeMin': (F, 12.0), 'offensiveLifeMax': (F, 24.0),
            'characterStrengthModifier': (F, 8.0),
            'defensiveFire': (F, 18.0), 'defensiveCold': (F, 18.0),
            'defensivePierce': (F, 18.0),
            'augmentSkillName1': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel1': (I, 3),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Gatekeeper — ascacophus, plant guardian
        'gatekeeper_soul': {
            'offensivePhysicalMin': (F, 22.0), 'offensivePhysicalMax': (F, 42.0),
            'offensiveSlowPoisonMin': (F, 25.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterStrengthModifier': (F, 10.0),
            'characterLifeModifier': (F, 12.0),
            'augmentSkillName1': (S, _SK_PLAGUE), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_HEART_OF_OAK), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Barnacle — karkinos crab, armored physical
        'barnacle_soul': {
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 38.0),
            'characterDefensiveAbility': (F, 50.0),
            'defensivePierce': (F, 20.0),
            'defensiveProtection': (F, 20.0),
            'characterLifeModifier': (F, 10.0),
            'augmentSkillName1': (S, _SK_SHIELD_CHARGE), 'augmentSkillLevel1': (I, 3),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Deathclot — tomb rot undead, cold/fire resist, bleed
        'deathclot_soul': {
            'offensiveSlowBleedingMin': (F, 45.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveLifeMin': (F, 15.0), 'offensiveLifeMax': (F, 28.0),
            'defensiveCold': (F, 25.0), 'defensiveFire': (F, 30.0),
            'characterLifeModifier': (F, 6.0),
            'augmentSkillName1': (S, _SK_NECROSIS), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_DARK_COVENANT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Stingeye — mantid, fast dual-attacker
        'stingeye_soul': {
            'offensivePierceMin': (F, 16.0), 'offensivePierceMax': (F, 32.0),
            'characterDexterityModifier': (F, 10.0),
            'characterAttackSpeedModifier': (F, 18.0),
            'characterOffensiveAbility': (F, 55.0),
            'characterRunSpeedModifier': (F, 12.0),
            'augmentSkillName1': (S, _SK_DUAL_WEAPON), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_FLASH_POWDER),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Daeros — lost soul caster, spell focus
        'daeros_soul': {
            'offensiveLifeMin': (F, 22.0), 'offensiveLifeMax': (F, 40.0),
            'offensiveColdMin': (F, 14.0), 'offensiveColdMax': (F, 28.0),
            'characterIntelligenceModifier': (F, 10.0),
            'characterSpellCastSpeedModifier': (F, 25.0),
            'characterManaModifier': (F, 12.0),
            'augmentSkillName1': (S, _SK_TERNION), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_VISION_OF_DEATH), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Cursed Creeper — tomb rot, bleed/undead
        'cursedcreeper_soul': {
            'offensiveSlowBleedingMin': (F, 50.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveLifeMin': (F, 18.0), 'offensiveLifeMax': (F, 32.0),
            'defensiveCold': (F, 25.0), 'defensiveFire': (F, 30.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_NECROSIS), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_DARK_COVENANT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Nightmistress — empusa, life drain seductress
        'nightmistress_soul': {
            'offensiveLifeMin': (F, 25.0), 'offensiveLifeMax': (F, 45.0),
            'characterDexterityModifier': (F, 8.0),
            'characterIntelligenceModifier': (F, 8.0),
            'characterDodgePercent': (F, 8.0),
            'characterSpellCastSpeedModifier': (F, 15.0),
            'augmentSkillName1': (S, _SK_DARK_COVENANT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PHANTOM_STRIKE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Qinshi — terracotta warrior, construct
        'qinshi_soul': {
            'offensivePhysicalMin': (F, 22.0), 'offensivePhysicalMax': (F, 40.0),
            'characterStrengthModifier': (F, 8.0),
            'characterLifeModifier': (F, 12.0),
            'defensiveProtection': (F, 20.0),
            'augmentSkillName1': (S, _SK_EARTH_ENCHANT), 'augmentSkillLevel1': (I, 2),
            'augmentSkillName2': (S, _SK_ONSLAUGHT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Rusted Relic — terracotta, slow armored
        'rustedrelic_soul': {
            'offensivePhysicalMin': (F, 18.0), 'offensivePhysicalMax': (F, 35.0),
            'offensiveSlowPoisonMin': (F, 15.0),
            'offensiveSlowPoisonDurationMin': (F, 3.0),
            'characterStrengthModifier': (F, 8.0),
            'characterLifeModifier': (F, 10.0),
            'defensiveProtection': (F, 18.0),
            'defensivePoison': (F, 20.0),
            'augmentSkillName1': (S, _SK_EARTH_ENCHANT), 'augmentSkillLevel1': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Erebenea — lamia, bleed/physical, fast
        'erebenea_soul': {
            'offensiveSlowBleedingMin': (F, 55.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 38.0),
            'characterDexterityModifier': (F, 10.0),
            'characterRunSpeedModifier': (F, 10.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_LETHAL_STRIKE), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_ENVENOM), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Athenos — furies, dodge/speed caster
        'athenos': {  # matches both athenos_n_soul and athenos_soul_n
            'offensiveLightningMin': (F, 18.0), 'offensiveLightningMax': (F, 35.0),
            'offensiveLifeMin': (F, 12.0), 'offensiveLifeMax': (F, 24.0),
            'characterDexterityModifier': (F, 10.0),
            'characterDodgePercent': (F, 12.0),
            'characterSpellCastSpeedModifier': (F, 15.0),
            'characterOffensiveAbility': (F, 40.0),
            'augmentSkillName1': (S, _SK_STORM_SURGE), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_PHANTOM_STRIKE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_RING_LIGHTNING),
            'itemSkillAutoController': (S, _AC_ON_HIT),
        },
        # Oythroneus — zombie, completely empty! Undead brute
        'oythroneus_soul': {
            'offensivePhysicalMin': (F, 22.0), 'offensivePhysicalMax': (F, 42.0),
            'offensiveLifeMin': (F, 18.0), 'offensiveLifeMax': (F, 32.0),
            'characterStrengthModifier': (F, 10.0),
            'characterLifeModifier': (F, 12.0),
            'offensivePhysicalModifier': (I, 15),
            'augmentSkillName1': (S, _SK_NECROSIS), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_ONSLAUGHT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_ZOMBIE_SUMMON),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Sandwraith — completely empty! Spectral desert predator
        'sandwraith_soul': {
            'offensiveLifeMin': (F, 25.0), 'offensiveLifeMax': (F, 45.0),
            'offensiveColdMin': (F, 15.0), 'offensiveColdMax': (F, 28.0),
            'characterDodgePercent': (F, 10.0),
            'characterRunSpeedModifier': (F, 10.0),
            'characterIntelligenceModifier': (F, 8.0),
            'defensiveLife': (F, 25.0),
            'augmentSkillName1': (S, _SK_PHANTOM_STRIKE), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_RAVAGES_OF_TIME), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_LIFE_DRAIN),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Camelbane — antlion, fast striker
        'camelbane_soul': {
            'offensivePhysicalMin': (F, 20.0), 'offensivePhysicalMax': (F, 38.0),
            'offensivePierceMin': (F, 12.0), 'offensivePierceMax': (F, 24.0),
            'characterOffensiveAbility': (F, 50.0),
            'characterAttackSpeedModifier': (F, 12.0),
            'characterRunSpeedModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_LETHAL_STRIKE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Sybaris — limos, bleed/life drain
        'sybaris_soul': {
            'offensiveSlowBleedingMin': (F, 55.0),
            'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveLifeMin': (F, 20.0), 'offensiveLifeMax': (F, 38.0),
            'characterStrengthModifier': (F, 8.0),
            'characterLifeModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_DARK_COVENANT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_NECROSIS), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Beast (Odontotyrannus) — massive brute, raw power
        'beast_soul': {
            'offensivePhysicalMin': (F, 30.0), 'offensivePhysicalMax': (F, 55.0),
            'offensiveStunMin': (F, 0.5), 'offensiveStunMax': (F, 2.0),
            'offensiveStunChance': (F, 15.0),
            'characterStrengthModifier': (F, 12.0),
            'characterLifeModifier': (F, 15.0),
            'characterAttackSpeedModifier': (F, -8.0),
            'characterRunSpeedModifier': (F, -10.0),
            'augmentSkillName1': (S, _SK_WAR_HORN), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_BATTLE_RAGE), 'augmentSkillLevel2': (I, 3),
            'itemSkillName': (S, _SS_GROUND_SMASH),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Venophobia — spider, poison specialist
        'venophobia_soul': {
            'offensiveSlowPoisonMin': (F, 45.0),
            'offensiveSlowPoisonDurationMin': (F, 5.0),
            'offensivePierceMin': (F, 12.0), 'offensivePierceMax': (F, 24.0),
            'defensivePoison': (F, 30.0),
            'characterDexterityModifier': (F, 8.0),
            'augmentSkillName1': (S, _SK_ENVENOM), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _SK_PLAGUE), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Viluktia — empusa, fire/life
        'viluktia_soul': {
            'offensiveLifeMin': (F, 22.0), 'offensiveLifeMax': (F, 40.0),
            'offensiveFireMin': (F, 14.0), 'offensiveFireMax': (F, 28.0),
            'characterManaModifier': (F, 12.0),
            'characterIntelligenceModifier': (F, 8.0),
            'defensiveFire': (F, 18.0),
            'augmentSkillName1': (S, _SK_FIRE_ENCHANT), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_DARK_COVENANT), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_BLOOD_BOIL),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
        # Bthokite — epiales (nightmare), poison/life
        'bthokite_soul': {
            'offensiveSlowPoisonMin': (F, 35.0),
            'offensiveSlowPoisonDurationMin': (F, 4.0),
            'offensiveLifeMin': (F, 18.0), 'offensiveLifeMax': (F, 32.0),
            'characterLifeModifier': (F, 10.0),
            'defensivePoison': (F, 35.0),
            'augmentSkillName1': (S, _SK_PLAGUE), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _SK_VISION_OF_DEATH), 'augmentSkillLevel2': (I, 2),
            'itemSkillName': (S, _SS_VENOM_SPRAY),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
        },
    }

    # Apply overhauls to matching soul records
    total = 0
    for rec in list(db.record_names()):
        rl = rec.lower()
        if 'equipmentring' not in rl or 'soul' not in rl:
            continue
        # Skip template records
        if 'template' in rl or 'test' in rl:
            continue

        for pattern, stats in OVERHAULS.items():
            if pattern in rl:
                for fname, (dtype, val) in stats.items():
                    db.set_field(rec, fname, val, dtype)
                # B-SOUL-PROC-1: a granted item skill instantiates at
                # itemSkillLevel; absent (or 0) = level-0 = INACTIVE, so the
                # tooltip shows "Grants Skill" but the auto-controller never has
                # a castable skill (the Crommyonian Sow bug; 211 souls). Every
                # base-game (876/876) and SV-upstream (941/941) item that grants
                # a skill also sets itemSkillLevel >= 1. The OVERHAULS specs
                # above never set it, so inject the mod's established per-tier
                # default (n/e/l = 1/2/3) whenever a spec grants a skill
                # without a level.
                if 'itemSkillName' in stats and 'itemSkillLevel' not in stats:
                    # Never clobber a record that already carries a live level
                    # (>= 1) from upstream or an earlier pass - the previously
                    # OK souls must stay byte-identical.
                    _cur = None
                    _ff = db.get_fields(rec) or {}
                    for _k, _tf in _ff.items():
                        if _k.split('###')[0] == 'itemSkillLevel' and _tf.values:
                            _cur = int(_tf.values[0])
                            break
                    if _cur is None or _cur < 1:
                        tier_level = 3 if rl.endswith('_l.dbr') else \
                                     2 if rl.endswith('_e.dbr') else 1
                        db.set_field(rec, 'itemSkillLevel', tier_level,
                                     DATA_TYPE_INT)
                db._modified.add(rec)
                total += 1
                break

    print(f"  Generic souls overhauled: {total} records modified")
    # Also clean up the 5 Dropbox-era conflicted copies
    conflicts = 0
    for rec in list(db.record_names()):
        if 'conflicted copy' in rec.lower() and 'soul' in rec.lower():
            conflicts += 1
    if conflicts:
        print(f"  Note: {conflicts} Dropbox conflicted copy records still exist (harmless)")


def _fix_zero_level_soul_procs(db):
    """B-SOUL-PROC-1 FIX B: bump the souls whose records ship an EXPLICIT
    itemSkillLevel == 0 (a level-0 granted skill is inactive - it tooltips but
    never procs/summons). These come from two origins we cannot fix at source:
    the SV 0.98i upstream base records (snaptooth/rocksting/orythroneus - the
    upstream itself ships the e/l tiers at 0) and the parked-generator crowboar
    souls (create_uber_souls.py, other-lane owned - patched here instead).
    Values follow each family's own tier convention and NEVER touch a record
    whose level is already >= 1 (the previously-OK set stays byte-identical):
      - snaptooth   n=1 (upstream, kept) -> e=2, l=3  (1/2/3 ladder; Skill_Passive max 50)
      - orythroneus n=1 (upstream, kept) -> e=2, l=3  (same)
      - rocksting   n=4 (upstream, kept) -> e=6, l=8  (continue the n=4 ladder; skill max 20)
      - crowboar    l=1 (generator, kept) -> n=1, e=2 (summon-tier convention; the
        latent non-monotone l=1 [Legendary summons the weakest crow variant] is NOT
        changed because l is in the previously-OK set - flagged for Will).
    """
    S_DIR = r'records\item\equipmentring\soul'
    FIXES = {
        S_DIR + r'\jackalman\snaptooth_soul_e.dbr': 2,
        S_DIR + r'\jackalman\snaptooth_soul_l.dbr': 3,
        S_DIR + r'\zombie\orythroneus_soul_e.dbr': 2,
        S_DIR + r'\zombie\orythroneus_soul_l.dbr': 3,
        S_DIR + r'\scorpion\rocksting_soul_e.dbr': 6,
        S_DIR + r'\scorpion\rocksting_soul_l.dbr': 8,
        S_DIR + r'\svc_uber\crowboar_soul_n.dbr': 1,
        S_DIR + r'\svc_uber\crowboar_soul_e.dbr': 2,
    }
    fixed = 0
    for rec, lvl in FIXES.items():
        r = _find_record(db, rec)
        if not r:
            print(f"  WARNING B-SOUL-PROC-1: {rec} not found; zero-level fix skipped")
            continue
        fields = db.get_fields(r) or {}
        cur = None
        for key, tf in fields.items():
            if key.split('###')[0] == 'itemSkillLevel' and tf.values:
                cur = int(tf.values[0])
                break
        if cur is not None and cur >= 1:
            continue  # already active - never disturb the OK set
        db.set_field(r, 'itemSkillLevel', lvl, DATA_TYPE_INT)
        db._modified.add(r)
        fixed += 1
    print(f"  Zero-level soul procs fixed: {fixed} record(s) (B-SOUL-PROC-1 FIX B)")


# ── B-SOUL-PROC-2 (build29): PLAYER-CASTABILITY of soul-granted skills ──────
# The build28 itemSkillLevel fix was NECESSARY but NOT SUFFICIENT (Will,
# 2026-07-08 live on build28: "the ground attack in the soul is still not
# working"). Disasm-proven root cause (Game.dll SkillManager::StartSkill,
# string xref va 0x1025622a): when a skill carries a skillSpecialAnimationName,
# StartSkill asks the caster's ANIMATION TABLE to start that named animation;
# if the name is not in the table's <row>SpecialAnimRef1..15 entries for the
# CURRENT WEAPON row, the start fails, StartSkill logs "Animation failed to
# start in SkillManager::StartSkill - %s %s", SKIPS the entire skill-start
# continuation and returns false. The cast silently never happens.
#
# Our shipped PC tables (SV 0.98i's own, byte-identical port) define exactly
# 32 special-anim names, and only TWO of them (AoE360, Colossus) appear in
# EVERY weapon row of BOTH sexes. cyclops_groundsmash (the Crommyonian Sow
# "Ground Smash") carries anim 'ClubSlam' - a Cyclops-rig animation that is in
# NO PC row, so the proc can never fire for a player, at any itemSkillLevel.
# 39 distinct soul-granted skills carry such never-playable anims (ClubSlam,
# Spit, Punch, BloodBoil, Summon, GroundPound, ...); dozens more carry anims
# playable only with SOME weapon types. The proven-working precedent is anim-
# LESS granted skills (base game: wraithlordsummons + 172 of 204 proc items
# grant skills with NO special anim; our own summon_boneash - the one grant
# Will SAW fire - has none).
#
# FIX: for every soul-granted skill whose special anim is not universally
# playable, clone the skill to records\skills\soulskills\pcsafe\<name>.dbr,
# BLANK the clone's skillSpecialAnimationName (engine then uses the default
# attack/cast animation, always available), and repoint the souls'
# itemSkillName at the clone. Cloning (never editing in place) means monsters
# and pets that share the original skill keep their own animations
# (e.g. melinoe_bloodboil is also Blood Toxeus' kit; spellbreaker is cast by
# several monsters). Deterministic: souls are processed in sorted order.

_PC_ANM_TABLE_PATHS = (
    r'records\creature\pc\anm\anm_malepc01.dbr',
    r'records\creature\pc\anm\anm_femalepc.dbr',
)
_PCSAFE_DIR = r'records\skills\soulskills\pcsafe'
# The engine's SkillManager::StartSkill reads <row>SpecialAnimRef1..15 (disasm,
# va 0x1025622a; see the B-SOUL-PROC-2 block comment). GRAFT #0
# (build_svc_database `_complete_pc_anim_melee_rows`) deliberately restores the
# dropped melee tokens (Hew/Ensnare/Crosscut/Barrage/ThunderClap) at indices
# >15 - a SVAERA-proven space that HELPS the mastery melee skills if the engine
# reads past 15, and is harmless (no regression) if it does not. Those >15
# additions must NOT inflate this soul-castability set: if they did, souls whose
# grant carries Ensnare/ThunderClap would stop being pcsafe-cloned yet remain
# uncastable with a melee weapon should the 15-cap be real - a regression. So
# the soul pcsafe universal set is computed with the SAME <=15 bound the engine
# documents, keeping soul-grant behavior byte-identical to the pre-graft build.
_PCSAFE_ANIM_IDX_CAP = 15


def _pc_universal_special_anims(db):
    """Return the set of special-anim names (lowercase) present in EVERY
    weapon row of BOTH shipped PC animation tables - the only names a player
    character can be guaranteed to play regardless of equipped weapon. Only
    indices <=15 count (the engine's documented SpecialAnimRef read bound; see
    _PCSAFE_ANIM_IDX_CAP)."""
    import re as _re
    universal = None
    for tbl in _PC_ANM_TABLE_PATHS:
        rec = _find_record(db, tbl)
        if not rec:
            raise SystemExit(f"PC animation table missing from the build: {tbl}")
        rows = {}
        for key, tf in (db.get_fields(rec) or {}).items():
            fname = key.split('###')[0]
            m = _re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if m and int(m.group(2)) <= _PCSAFE_ANIM_IDX_CAP \
                    and tf.values and str(tf.values[0]).strip():
                rows.setdefault(m.group(1), set()).add(str(tf.values[0]).lower())
        for names in rows.values():
            universal = set(names) if universal is None else (universal & names)
    return universal or set()


def _soul_item_records(db):
    """All soul ITEM records (sorted, Monster-typed test parkings skipped)."""
    out = []
    for rec in db.record_names():
        rl = rec.lower()
        if '\\soul\\' not in rl and '/soul/' not in rl:
            continue
        if db._record_types.get(rec) == 'Monster':
            continue
        out.append(rec)
    return sorted(out)


def _fix_granted_skill_castability(db):
    """B-SOUL-PROC-2: make every soul-granted skill castable by the player.

    1. Skills with a special anim not universally playable -> pcsafe clone
       with the special-anim field REMOVED (base-absent parity); souls
       repointed (see block comment above).
    2. ENEMY-targeted auto-cast controllers used by souls that lack
       autoTargetRadius get the base-game concrete-controller value 15.0.
       Every WORKING base-game AttackEnemy controller carries autoTargetRadius
       7-15; the base_atenemy_* basetemplates the SV souls inherited carry
       NONE (their only base-game item user is the known-broken EE
       sihailongwang spear, so they have zero working precedent). Self/Ally
       controllers are deliberately left untouched (base Self controllers use a
       wide 10-15 radius; forcing a small value could suppress self-buff
       auto-casts, and the invariant only requires a radius on Enemy). Additive
       + idempotent: existing values are never changed.
    """
    S = DATA_TYPE_STRING
    universal = _pc_universal_special_anims(db)
    print(f"\n  B-SOUL-PROC-2: universally playable PC anims = {sorted(universal)}")

    # Exact case/slash-tolerant resolution map (O(1) lookups; the module-level
    # _find_record is a SUBSTRING matcher and O(n) per call, both wrong here).
    recmap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def resolve(path):
        return recmap.get(str(path).replace('/', '\\').lower().strip())

    def field(rec, name):
        ff = db.get_fields(rec) or {}
        for key, tf in ff.items():
            if key.split('###')[0] == name and tf.values:
                return tf.values
        return None

    def delete_field(rec, name):
        ff = db.get_fields(rec)
        if not ff:
            return
        for key in [k for k in ff if k.split('###')[0] == name]:
            del ff[key]
        db._modified.add(rec)

    clones = {}          # source skill rec -> pcsafe clone path
    repointed = 0
    controllers_seen = set()
    controllers_fixed = 0

    for rec in _soul_item_records(db):
        isn = field(rec, 'itemSkillName')
        if not isn or not str(isn[0]).strip():
            continue
        skill = resolve(str(isn[0]).strip())
        if not skill:
            continue  # dangling refs are the resolution invariant's job
        anim = field(skill, 'skillSpecialAnimationName')
        anim_val = str(anim[0]).strip() if anim and str(anim[0]).strip() else ''
        target = skill
        if anim_val and anim_val.lower() not in universal:
            if skill not in clones:
                if skill.replace('/', '\\').lower().startswith(_PCSAFE_DIR):
                    clones[skill] = skill  # already a pcsafe record (idempotence)
                else:
                    base_name = skill.replace('/', '\\').split('\\')[-1]
                    clone = _PCSAFE_DIR + '\\' + base_name
                    if not db.has_record(clone):
                        if not db.clone_record(skill, clone):
                            raise SystemExit(
                                f"B-SOUL-PROC-2: failed to clone {skill}")
                        recmap[clone.lower()] = clone
                    # REMOVE the special-anim field entirely (rather than set it
                    # to ''): the proven-working base-game anim-less grants OMIT
                    # skillSpecialAnimationName (verified: 60/60 sampled base
                    # controller-cast grants have the field ABSENT, 0 empty-str),
                    # so an absent field is the exact, ambiguity-free reproduction
                    # of the pattern that never trips SkillManager::StartSkill.
                    delete_field(clone, 'skillSpecialAnimationName')
                    clones[skill] = clone
            target = clones[skill]
        # repoint ONLY when a pcsafe clone replaced the skill; souls whose
        # grants are already playable stay byte-identical.
        if target != skill and _norm_ref(target) != _norm_ref(str(isn[0])):
            db.set_field(rec, 'itemSkillName', target, S)
            db._modified.add(rec)
            repointed += 1

        # 2. controller autoTargetRadius parity - ENEMY controllers only.
        # Every WORKING base-game Enemy/AttackEnemy autocast controller carries
        # autoTargetRadius 7-15; the base_atenemy_* templates the souls inherit
        # carry NONE (target-acquisition gap). Self/Ally controllers are left
        # untouched: base Self controllers use a WIDE radius (10-15), so forcing
        # a small value could SUPPRESS self-buff auto-casts, and the activation
        # invariant only requires a radius on Enemy controllers.
        ctl = field(rec, 'itemSkillAutoController')
        if ctl and str(ctl[0]).strip():
            c = resolve(str(ctl[0]).strip())
            if c and c not in controllers_seen:
                controllers_seen.add(c)
                tt = field(c, 'targetType')
                tt = str(tt[0]) if tt else 'Self'
                if tt == 'Enemy' and field(c, 'autoTargetRadius') is None:
                    db.set_field(c, 'autoTargetRadius', 15.0, DATA_TYPE_FLOAT)
                    db._modified.add(c)
                    controllers_fixed += 1

    n_cloned = len([1 for s, c in clones.items() if s != c])
    print(f"  B-SOUL-PROC-2: {n_cloned} skill(s) cloned to pcsafe with anim "
          f"removed; {repointed} soul grant(s) repointed; "
          f"{controllers_fixed} Enemy controller(s) given base-parity "
          f"autoTargetRadius (of {len(controllers_seen)} seen)")


def _norm_ref(path):
    return str(path).replace('/', '\\').lower().strip()


def _fix_wave29_contract_items(db):
    """build29 contract-suite fixes (DB side). Returns new display tags.

    - SOUL-NAME-RESOLVES: satyrmagi_soul + satyrspiritcaller_soul {n,e,l}
      carried placeholder tagSoul1 (undefined -> raw tag in-game); the parked
      test\\kyrashadowdancer_soul {e,l} carried bare tagSoulName. Real tags
      assigned; kyra test pair repointed at the live tagSoulName323.
    - SOUL-AUGMENT-LEVEL: crowboar_soul_n/e shipped augmentSkillLevel1/2 == 0
      (level-0 augment = no bonus). Bumped n=1, e=2 (l already live at 1).
    - MONSTER-SKILLS-LOOT: the 5 blood-cave ancestralwarrior bodies referenced
      Records\\Skills\\Monster Skills\\Melee_Poison09-12_10.dbr which does not
      exist in SV/AE; the real record is attackmelee_poison09-12_10.dbr
      (same dir, SV renamed it). Repointed.
    - MONSTER-SPAWN-ELIGIBILITY: bw_priest_houndmaster pool had spawnMax=2
      with championMin=championMax=2 -> guaranteed mains = 0, the disciple
      never spawns (Blood-Toxeus champion-crowd-out class). spawnMax -> 3.
    - SUMMON-PET-CLASSIFICATION: soulskills pets missing monsterClassification
      get 'Common' (the classification of every working exemplar: Lyia,
      Boneash, base WraithLord).
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tags = {}
    soul_dir = r'records\item\equipmentring\soul'

    # 1. real names for the placeholder-tagged souls
    name_fixes = {
        soul_dir + r'\satyrmagi_soul_n.dbr': 'tagSVCSoulSatyrMagi',
        soul_dir + r'\satyrmagi_soul_e.dbr': 'tagSVCSoulSatyrMagi',
        soul_dir + r'\satyrmagi_soul_l.dbr': 'tagSVCSoulSatyrMagi',
        soul_dir + r'\satyrspiritcaller_soul_n.dbr': 'tagSVCSoulSatyrSpiritcaller',
        soul_dir + r'\satyrspiritcaller_soul_e.dbr': 'tagSVCSoulSatyrSpiritcaller',
        soul_dir + r'\satyrspiritcaller_soul_l.dbr': 'tagSVCSoulSatyrSpiritcaller',
        soul_dir + r'\test\kyrashadowdancer_soul_e.dbr': 'tagSoulName323',
        soul_dir + r'\test\kyrashadowdancer_soul_l.dbr': 'tagSoulName323',
    }
    fixed_names = 0
    for path, tag in name_fixes.items():
        rec = _find_record(db, path)
        if not rec:
            print(f"  WARNING wave29: soul not found for name fix: {path}")
            continue
        db.set_field(rec, 'itemNameTag', tag, S)
        db._modified.add(rec)
        fixed_names += 1
    tags['tagSVCSoulSatyrMagi'] = '{^F}Satyr Magi Soul'
    tags['tagSVCSoulSatyrSpiritcaller'] = '{^F}Satyr Spirit Caller Soul'

    # 2. crowboar zero augment levels (never disturb a live >= 1 value)
    aug_fixes = {
        soul_dir + r'\svc_uber\crowboar_soul_n.dbr': 1,
        soul_dir + r'\svc_uber\crowboar_soul_e.dbr': 2,
    }
    fixed_augs = 0
    for path, lvl in aug_fixes.items():
        rec = _find_record(db, path)
        if not rec:
            print(f"  WARNING wave29: crowboar soul not found: {path}")
            continue
        ff = db.get_fields(rec) or {}
        for fname in ('augmentSkillLevel1', 'augmentSkillLevel2'):
            cur = None
            for key, tf in ff.items():
                if key.split('###')[0] == fname and tf.values:
                    cur = int(tf.values[0])
                    break
            if cur is not None and cur >= 1:
                continue
            db.set_field(rec, fname, lvl, I)
            db._modified.add(rec)
            fixed_augs += 1

    # 3. ancestralwarrior dead melee skill refs
    aw_target = r'records\skills\monster skills\attackmelee_poison09-12_10.dbr'
    if not _find_record(db, aw_target):
        raise SystemExit(f"wave29: repoint target missing: {aw_target}")
    fixed_aw = 0
    for suffix in 'abcde':
        path = (r'records\drxmap\bloodcave\bodies\ancestralwarrior'
                + suffix + '.dbr')
        rec = _find_record(db, path)
        if not rec:
            print(f"  WARNING wave29: ancestralwarrior body not found: {path}")
            continue
        db.set_field(rec, 'skillName1', aw_target, S)
        db._modified.add(rec)
        fixed_aw += 1

    # 4. houndmaster champion crowd-out: spawnMax 2 -> 3 (1 guaranteed main)
    pool = _find_record(db, r'records\drxmap\proxy\pools\bw_priest_houndmaster.dbr')
    fixed_pool = 0
    if pool:
        ff = db.get_fields(pool) or {}
        smax = cmax = None
        for key, tf in ff.items():
            fname = key.split('###')[0]
            if fname == 'spawnMax' and tf.values:
                smax = int(tf.values[0])
            elif fname == 'championMax' and tf.values:
                cmax = int(tf.values[0])
        if smax is not None and cmax is not None and smax - cmax < 1:
            db.set_field(pool, 'spawnMax', cmax + 1, I)
            db._modified.add(pool)
            fixed_pool = 1
    else:
        print("  WARNING wave29: bw_priest_houndmaster pool not found")

    # 5. soulskills pets missing monsterClassification
    fixed_pets = 0
    for rec in sorted(db.record_names()):
        rl = rec.lower()
        if not rl.startswith(r'records\skills\soulskills\pets'):
            continue
        ff = db.get_fields(rec) or {}
        tpl = mc = None
        for key, tf in ff.items():
            fname = key.split('###')[0]
            if fname == 'templateName' and tf.values:
                tpl = str(tf.values[0])
            elif fname == 'monsterClassification' and tf.values:
                mc = str(tf.values[0])
        if not tpl or not _norm_ref(tpl).endswith('\\pet.tpl'):
            continue
        if mc and mc.strip():
            continue
        db.set_field(rec, 'monsterClassification', 'Common', S)
        db._modified.add(rec)
        fixed_pets += 1

    print(f"  wave29 contract fixes: {fixed_names} soul name tag(s), "
          f"{fixed_augs} crowboar augment level(s), {fixed_aw} ancestralwarrior "
          f"skill ref(s), {fixed_pool} spawn pool(s), {fixed_pets} pet "
          f"classification(s)")
    return tags


def _fix_wave30_items(db):
    """build30 DB fixes.

    D4 HANIF NAMEPLATE: the summon_hanif pet ladder (soulskills\\pets\\
    hanifthecruel{,_1,_2,_3}.dbr, inherited from SV upstream) carries
    description = tagMonsterName1201 ("Senusnet Mal") - the wrong monster's
    nameplate. The correct tag is tagMonsterName1198 ("Hanif the Cruel"),
    verified defined in both SV upstream Text_EN and our shipped Text.arc.
    The base (suffix-less) pet record is orphaned (0 inbound refs) but carries
    the same wrong tag; fixed for family consistency. NOTE (report-only, not
    changed): the HOSTILE hero_hanifthecruel_34 carries tagMonsterName1200
    ("Nexeu, Doomed Prophet") - same upstream tag-shift debt class, but
    touching hostile monsters is out of the build30 D-item scope.

    D6 REST-SKILL VULNERABILITY (Will 2026-07-09): the drx REST self-buff
    (drxrest_skillbuff.dbr, Class Skill_BuffSelfImmobilize) is the channeled
    recover skill the player learns via the quest reward skill tree
    (questrewardskilltree.dbr skillName22 references THIS record directly - it
    is the ONLY player-reachable rest buff; drxrest_skill.dbr,
    drxrest_skillbuffx.dbr and "copy of drxrest_skillbuff.dbr" all have 0
    inbound refs and are never applied). While resting it drops six
    all-resistance stats to -300%. Will wants resting to be a hard commit -
    any hit taken while resting should effectively one-shot you - so each of
    the six penalty fields is scaled from -300% to -1000%. These fields are
    PERCENT-encoded floats (the stored value IS the percent: -300.0 = -300%),
    so the new value is -1000.0. Everything else (the recovery/regen effect,
    duration, energy cost, the immobilize) is untouched. A fail-loud pre-check
    asserts each field currently reads -300.0 so an upstream SV re-tune can not
    be silently over-written. The two dead orphan variants (drxrest_skillbuffx,
    "copy of drxrest_skillbuff") are left at -300 and reported in
    needs_will_signoff.
    """
    S = DATA_TYPE_STRING
    hanif_pets = [
        r'records\skills\soulskills\pets\hanifthecruel.dbr',
        r'records\skills\soulskills\pets\hanifthecruel_1.dbr',
        r'records\skills\soulskills\pets\hanifthecruel_2.dbr',
        r'records\skills\soulskills\pets\hanifthecruel_3.dbr',
    ]
    fixed = 0
    for path in hanif_pets:
        rec = _find_record(db, path)
        if not rec:
            raise SystemExit(f"wave30 D4: hanif pet record missing: {path}")
        db.set_field(rec, 'description', 'tagMonsterName1198', S)
        db._modified.add(rec)
        fixed += 1
    print(f"  wave30 fixes: {fixed} hanif pet nameplate(s) -> "
          f"tagMonsterName1198 (Hanif the Cruel)")

    # ── D6: rest-skill all-resistance penalty -300% -> -1000% (see docstring).
    rest_buff = r'records\quests\rewards\drxrest_skillbuff.dbr'
    rest_rec = _find_record(db, rest_buff)
    if not rest_rec:
        raise SystemExit(f"wave30 D6: rest skill buff record missing: {rest_buff}")
    rest_fields = ['defensiveBleeding', 'defensiveElementalResistance',
                   'defensiveLife', 'defensivePhysical', 'defensivePierce',
                   'defensivePoison']
    rest_cur = db.get_fields(rest_rec) or {}

    def _rest_val(fname):
        for k, tf in rest_cur.items():
            if k.split('###')[0] == fname:
                return tf.values[0] if tf.values else None
        return None

    rest_fixed = 0
    for fname in rest_fields:
        v = _rest_val(fname)
        if v is None or abs(float(v) - (-300.0)) > 1e-6:
            raise SystemExit(
                f"wave30 D6: {fname} expected -300.0 in {rest_buff}, got {v!r} "
                f"(upstream drift - reverify the rest-skill penalty encoding before scaling)")
        db.set_field(rest_rec, fname, -1000.0, DATA_TYPE_FLOAT)
        rest_fixed += 1
    db._modified.add(rest_rec)
    print(f"  wave30 D6: rest-skill all-resist penalty -300% -> -1000% "
          f"({rest_fixed} fields on drxrest_skillbuff)")
    return {}


def _fix_bladedancer_invisible_body(db):
    r"""build30/D5: the melinoe blade-dancer family renders an INVISIBLE body
    (floating blades only). Root cause is the SHARED mesh DRX\meshes\melinoe01.msh,
    which embeds its skin shader as `XPack\Shaders\standardblendedglowskinned.ssh`.
    The engine resolves an `XPackN\<Arc>\...` path ONLY in Resources\XPackN\<Arc>.arc,
    so it looks in Resources\XPack\Shaders.arc (Immortal Throne shaders, 2 entries)
    which does NOT contain that shader - it lives only in base Resources\Shaders.arc.
    The skin shader fails to load; the body never renders while the skeleton still
    animates the weapon hardpoints. This is NOT the per-record .anm overrides
    (build29's pet-only _strip_*_anim fix): the hostile discipleboss_bladedancer has
    ZERO .anm fields and is invisible too. Controls: base ElderDjinn01.msh uses the
    SAME shader via base-scoped `Shaders\...` and renders; base PC meshes use
    `XPack2\shaders\...` present in Resources\XPack2\Shaders.arc and render.

    Fix: repoint every melinoe01.msh user to the base melinoe mesh (base-scoped
    Shaders\standardskinned.ssh -> resolves). Same melinoe skeleton, so anm_melinoe
    and dual-wield equipment are unchanged; the crimson look is kept via each record's
    baseTexture (bladedancer.tex, a melinoe-UV skin). Proven-rendering by precedent:
    um_demastia_47 / um_insenzia_48 are DRX melinoe heroes already on the base mesh +
    a DRX .tex override + anm_melinoe. Covers all three owner-reported cases with ONE
    change: pets (soul-granted), the hostile discipleboss_bladedancer (roaming via
    q_melinoe_trap pools AND summoned 20x by c_disciple_miniboss), and the proxies.
    (Trade-off: loses the DRX self-illum glow, which DRX's own melinoe heroes also forgo.)

    NOTE on set_field dtype: 'mesh' is an existing STRING field on these records, and
    ArzDatabase.set_field(...dtype=None) preserves the existing field's dtype (verified
    in arz_patcher.py). This complies with the repo rule "never pass explicit dtype to
    set_field on existing/cloned records" (INT/FLOAT corruption trap).
    """
    BASE = r'XPack\Creatures\Monster\Melinoe\Melinoe01.msh'
    BROKEN = r'drx\meshes\melinoe01.msh'
    n = 0
    for rec in db.record_names():
        mv = db.get_field_value(rec, 'mesh')
        # F6c: slash-normalize (engine treats / and \ as equivalent path seps)
        if isinstance(mv, str) and mv.lower().replace('/', '\\') == BROKEN:
            db.set_field(rec, 'mesh', BASE)   # no dtype: preserve the string field
            n += 1
    # Expected sweep count = 3 (discipleboss_bladedancer + q_melinoe_trap + _trap02):
    # the bwpriest_1/2/3 pets are born-correct at their authoring site
    # (_create_bwpriest_pet_skill now sets the base mesh directly), so the sweep
    # only catches the upstream hostile + proxies. Fewer than 3 = the family
    # roster or the mesh-string casing drifted; fail loud.
    if n < 3:
        raise SystemExit(
            f"wave30 D5: blade-dancer mesh sweep repointed only {n} record(s) "
            f"(expected >= 3: discipleboss_bladedancer + 2 q_melinoe_trap proxies) "
            f"- family roster or mesh-string casing drifted; investigate")
    print(f"  blade-dancer invisible-body fix (D5): repointed {n} record(s) "
          f"off DRX\\meshes\\melinoe01.msh -> base Melinoe01.msh")
    return n


def _strip_record_fields(db, rec, field_names):
    """Remove fields from a record entirely (values=[] -> _encode_fields omits
    them -> ABSENT in the built record, never present-but-empty). The proven
    _strip_foreign_anim_overrides deletion mechanism, generalized."""
    fields = db.get_fields(rec)
    if not fields:
        return 0
    n = 0
    want = set(field_names)
    for key, tf in fields.items():
        if key.split('###')[0] in want and tf.values:
            tf.values = []
            n += 1
    if n:
        db._modified.add(rec)
    return n


def _fix_wave30_render_and_refs(db):
    """build30 F-wave (post-vet): F3 supra invisible weapons, F5 glacial orb
    projectile, F7a pcsafe dangling particle fx, F7b Melee_Poison dangling skill.

    F3 (MAJOR, Will's flagship Esti reward): the supra Legendary dagger + spear
    render INVISIBLE - DRX\\meshes\\supra\\wep_dagger.msh embeds the XPack-scoped
    shader XPack\\Shaders\\distortadditivestatic.ssh and wep_spear.msh embeds
    XPack/Shaders/standardblendedglowstatic.ssh; the engine resolves XPack\\ refs
    ONLY in Resources\\XPack\\Shaders.arc, which contains neither (the D5 melinoe
    class, EngineArcResolver-verified). Fix = the proven D5 DBR-level repoint to
    visually-close BASE weapon meshes whose internal shaders resolve (verified):
      wep_dagger.dbr -> XPack2 hochdorflordsdagger01.msh (a real dagger rig)
      wep_spear.dbr  -> base RSpear14B.msh (the Ares' Wrath legendary spear rig)
    wep_spear's DRX baseTexture is STRIPPED (its UV skin fits only the DRX mesh;
    the base mesh uses its own internal texture - wep_dagger carries none).

    F5 (MINOR): SVMesh\\meshes\\glacialorb01.msh embeds
    Shaders\\StandardBlendedScrollSkinned.ssh which ships NOWHERE (mod+base) ->
    the Storm drxiceshard projectile renders invisible. Repoint
    glacialorb_projectile_01.dbr to the base ice-shard projectile mesh
    Effects\\Projectiles\\ShardIce01.msh (shader-verified).

    F7a: our authored pcsafe soul-skill clones (arachne_venomspray, hero_sonicwave,
    yeti_sonicroar) carry particleEffectName2/3 = the nonexistent
    Records\\SandBox\\Chris\\UnarmedProjectile_FX01.dbr (inherited upstream debt).
    The fields are STRIPPED (absent = clean; a dangling fx layer draws nothing
    anyway, and empty-string refs are the B-TOXEUS-2 loader-abort class).

    F7b: 12 records (5 blood-cave bodies, scorpos, meshif3_dead, etc.) reference
    skillName1 = Records\\Skills\\Monster Skills\\Melee_Poison09-12_10.dbr which
    does not exist; the shipped sibling is attackmelee_poison09-12_10.dbr (same
    dir). Repoint the whole dangling class.
    """
    # ── F3: supra weapons ──
    fixes = [
        (r'records\drxitem\supra\wep_dagger.dbr',
         r'XPack2\items\equipmentweapon\sword\hochdorflordsdagger01.msh', False),
        (r'records\drxitem\supra\wep_spear.dbr',
         r'Items\EquipmentWeapon\Spear\Default\RSpear14B.msh', True),
    ]
    for rec, new_mesh, strip_tex in fixes:
        if not db.has_record(rec):
            raise SystemExit(f"wave30 F3: supra weapon record missing: {rec}")
        db.set_field(rec, 'mesh', new_mesh)   # no dtype: preserve STRING
        if strip_tex:
            _strip_record_fields(db, rec, ['baseTexture'])
        db._modified.add(rec)
    print("  F3 supra invisible weapons: wep_dagger -> hochdorflordsdagger01, "
          "wep_spear -> RSpear14B (+ DRX skin stripped)")

    # ── F5: glacial orb projectile ──
    g = r'records\skills\storm\sveffects\glacialorb_projectile_01.dbr'
    if db.has_record(g):
        db.set_field(g, 'mesh', r'Effects\Projectiles\ShardIce01.msh')
        db._modified.add(g)
        print("  F5 glacial orb: projectile mesh -> ShardIce01 (shader-verified)")
    else:
        print("  WARNING F5: glacialorb_projectile_01 missing; skipped")

    # ── F7a: pcsafe dangling particle fx ──
    stripped = 0
    for rec in [r'records\skills\soulskills\pcsafe\arachne_venomspray.dbr',
                r'records\skills\soulskills\pcsafe\hero_sonicwave.dbr',
                r'records\skills\soulskills\pcsafe\yeti_sonicroar.dbr']:
        if not db.has_record(rec):
            raise SystemExit(f"wave30 F7a: pcsafe record missing: {rec}")
        stripped += _strip_record_fields(
            db, rec, ['particleEffectName2', 'particleEffectName3'])
    print(f"  F7a pcsafe souls: stripped {stripped} dangling UnarmedProjectile_FX01 "
          f"particle refs (3 records)")

    # ── F7b: Melee_Poison dangling skill refs ──
    MISSING = r'records\skills\monster skills\melee_poison09-12_10.dbr'
    GOOD = r'records\skills\monster skills\attackmelee_poison09-12_10.dbr'
    if not db.has_record(GOOD):
        raise SystemExit(f"wave30 F7b: replacement skill missing: {GOOD}")
    repointed = 0
    for rec in db.record_names():
        ff = db.get_fields(rec) or {}
        for key, tf in ff.items():
            if not tf.values:
                continue
            changed = False
            new_vals = []
            for v in tf.values:
                if isinstance(v, str) and \
                        v.lower().replace('/', '\\') == MISSING:
                    new_vals.append(GOOD)
                    changed = True
                else:
                    new_vals.append(v)
            if changed:
                tf.values = new_vals
                db._modified.add(rec)
                repointed += 1
    if repointed < 5:
        raise SystemExit(f"wave30 F7b: only {repointed} Melee_Poison09-12_10 refs "
                         f"repointed (expected >= 5, vet counted 12) - "
                         f"path/casing drifted; investigate")
    print(f"  F7b Melee_Poison: repointed {repointed} dangling skillName refs "
          f"-> attackmelee_poison09-12_10")

    # ── F10 (delta vet, MINOR): melalos souls carried itemSkillLevel 3/4/6 vs
    #    summon_zombiesoldier's skillMaxLevel 3 - a harmless single-pet clamp,
    #    but the exact over-max class F1 eliminated. Normalize to the 1/2/3
    #    tier convention (clears the validator WARNs; the F1 Table-B guard
    #    already protects these levels from being re-stomped). ──
    f10 = 0
    for t, lv in (('n', 1), ('e', 2), ('l', 3)):
        tail = rf'\melalos_soul_{t}.dbr'
        cands = [n for n in db.record_names()
                 if n.lower().endswith(tail) and 'equipmentring' in n.lower()
                 and '\\soul\\' in n.lower()]
        if len(cands) != 1:
            raise SystemExit(f"wave30 F10: melalos soul {t} not found uniquely "
                             f"({len(cands)} candidates: {cands[:3]})")
        db.set_field(cands[0], 'itemSkillLevel', lv)
        db._modified.add(cands[0])
        f10 += 1
    print(f"  F10 melalos souls: itemSkillLevel normalized to 1/2/3 ({f10} records)")


# ── A3 / B-STARTER-CHEST-1: DEFERRED to the parallel disasm-grounded impl ───
# build29 note (reconciliation): A3 (the co-op starter chest = 12 bags + 36
# potions + Crommyonian Sow souls) is implemented in build_svc_database.py
# (~L632) by a parallel agent whose comment cites Game.dll disasm
# (FixedItemContainerController 0x10182120/0x10181530/0x10181da0): the chest
# spawns N = numSpawn items and picks each item's loot slot by ROULETTE over the
# slots' relative lootNChance weights - so per-CATEGORY counts are MULTINOMIAL
# and an EXACT composition (e.g. "exactly 1 soul") can NOT be guaranteed by any
# FixedItemLoot record; only the total N and the per-category EXPECTATION are
# exact (the only true exactly-once grant is a quest Action_GiveItem, the Esti
# pattern). My earlier _setup_starter_chest here (container.tables -> 49 single-
# item tables, assuming each `tables` entry resolves exactly once) was built on
# the WRONG engine model AND repointed the container away from the parallel
# agent's `defaultloot` edits, silently disabling their version. It is removed;
# A3 = the build_svc_database implementation. build30 D1 (owner revert): the
# sow-soul slot was REMOVED there. build30.2 POSTSCRIPT: the A3/D1 chest was
# DEAD IN-GAME anyway - build28 had replaced the native RunEquation numSpawn
# ('3+(2*numberOfPlayers)') with a bare literal ('48') which the engine
# evaluates to 0 on this container -> the chest dropped NOTHING through
# b28/b29/b30. Fixed in grant_all_inventory_bags (build_svc_database.py):
# equation-form numSpawn + single-slot dual-table construct, in-game verified
# on the DEV entry 2026-07-09.


# ── A4: Esti (hidden blood-cave) chest tier-1 supra formula = NOT APPLIED ───
# build29 FINAL DISPOSITION (disasm-refuted; the tables stay byte-identical to
# build28). The closed RCA's mechanism claim ("set the unused loot3 group to
# loot3Chance=100 -> the chest always drops exactly 1 supra formula") is FALSE
# under the real engine algorithm (Game.dll FixedItemContainerController,
# 0x10182120/0x10181530/0x10181da0): lootNChance values are RELATIVE ROULETTE
# WEIGHTS - every one of the numSpawn (~18-20) draws picks ONE slot with
# probability chance_i/sum(chances). The Esti tables' chances sum to 113.2, so
# a loot3Chance=100 slot means ~47% of EVERY draw = ~8-9 supra formulas per
# open (a loot-economy flood), never "exactly 1"; and a chance tuned for
# E[supra]=1 (about 6.66) would leave ~36% of opens with ZERO formulas. The
# ONLY exactly-once mechanism is the EXISTING quest Action_GiveItem
# (Condition_UseFixedItem -> OpenedHiddenChest token + GiveItem supra_special)
# = SV's original design, already live, with its notification tags resolving
# (B-SUPRA-NOTIFY-1). COUPLING FLAG: Lane B's _neutralize_esti_chest_supra in
# tools/build_quest_files.py (written expecting a chest-side grant) MUST NOT
# ship - with the quest grant removed and no chest change the player would
# never receive a formula. Keep the quest grant; the whole item needs no
# change. (An earlier in-tree implementation of the refuted spec was removed
# here; the record-diff gate asserts the 3 tables stay byte-identical to
# build28.)


def _verify_soul_itemskill_activation(db):
    """FAIL-LOUD invariant (B-SOUL-PROC-1): every soul that GRANTS an item skill
    must have a complete, ACTIVATABLE chain, or the grant is a silent no-op that
    still renders a 'Grants Skill' tooltip (the Crommyonian Sow bug - 219 souls
    shipped with itemSkillLevel absent/0 = the skill instantiates at level 0 =
    inactive, so the auto-cast controller has nothing castable).

    For every soul record with a non-empty itemSkillName:
      1. the skill record resolves and its Class starts with 'Skill_';
      2. itemSkillLevel is present and >= 1 (level-0 = inactive);
      3. if itemSkillAutoController is non-empty: it resolves, its templateName
         is the SkillAutoCastController template (controllers carry no Class
         field), its chanceToRun > 0 and triggerType is non-empty.
    Raises SystemExit on any violation. Re-checked standalone on the written
    .arz by tools/validate_soul_augments.py.

    build29 (B-SOUL-PROC-2) additions, disasm-grounded (Game.dll
    SkillManager::StartSkill aborts the cast when the special animation cannot
    start on the caster's animation table):
      4. the granted skill's skillSpecialAnimationName must be EMPTY or a name
         present in EVERY weapon row of both PC animation tables (universally
         playable); anything else is a sometimes/never-castable grant;
      5. an Enemy-targeted auto-cast controller must carry autoTargetRadius
         >= 1 (base-game concrete-controller parity; absent = 0 = no target
         acquisition).
    """
    CTRL_TPL = r'database\templates\skillautocastcontroller.tpl'
    universal = _pc_universal_special_anims(db)

    def field(rec, name):
        ff = db.get_fields(rec)
        if not ff:
            return None
        for key, tf in ff.items():
            if key.split('###')[0] == name and tf.values:
                return tf.values
        return None

    problems = []
    checked = 0
    for rec in db.record_names():
        rl = rec.lower()
        if '\\soul\\' not in rl and '/soul/' not in rl:
            continue
        if db._record_types.get(rec) == 'Monster':
            continue  # a few monster records live under soul\test\
        isn = field(rec, 'itemSkillName')
        if not isn or not str(isn[0]).strip():
            continue
        checked += 1
        skill = str(isn[0]).strip()
        sk = _find_record(db, skill)
        if not sk:
            problems.append((rec, f"itemSkillName does not resolve: {skill}"))
        else:
            cls = field(sk, 'Class')
            if not cls or not str(cls[0]).startswith('Skill_'):
                problems.append((rec, f"granted record is not a Skill_*: {skill} "
                                      f"(Class={cls[0] if cls else None})"))
            anim = field(sk, 'skillSpecialAnimationName')
            if anim and str(anim[0]).strip() and \
                    str(anim[0]).lower() not in universal:
                problems.append((rec,
                                 f"granted skill {skill} carries special anim "
                                 f"'{anim[0]}' which is NOT universally playable "
                                 f"by the PC (StartSkill aborts the cast; "
                                 f"B-SOUL-PROC-2 pcsafe clone missing)"))
        lvl = field(rec, 'itemSkillLevel')
        if lvl is None:
            problems.append((rec, "itemSkillLevel ABSENT (skill instantiates at "
                                  "level 0 = inactive, never procs)"))
        elif int(lvl[0]) < 1:
            problems.append((rec, f"itemSkillLevel == {int(lvl[0])} (level-0 "
                                  f"grant = inactive, never procs)"))
        ctl = field(rec, 'itemSkillAutoController')
        if ctl and str(ctl[0]).strip():
            c = _find_record(db, str(ctl[0]).strip())
            if not c:
                problems.append((rec, f"itemSkillAutoController does not resolve: {ctl[0]}"))
            else:
                tpl = field(c, 'templateName')
                if not tpl or str(tpl[0]).lower().replace('/', '\\') != CTRL_TPL:
                    problems.append((rec, f"controller {ctl[0]} has wrong template "
                                          f"{tpl[0] if tpl else None}"))
                chance = field(c, 'chanceToRun')
                if not chance or float(chance[0]) <= 0:
                    problems.append((rec, f"controller {ctl[0]} chanceToRun "
                                          f"{chance[0] if chance else None} (never fires)"))
                trig = field(c, 'triggerType')
                if not trig or not str(trig[0]).strip():
                    problems.append((rec, f"controller {ctl[0]} has empty triggerType"))
                tt = field(c, 'targetType')
                if tt and str(tt[0]) == 'Enemy':
                    rad = field(c, 'autoTargetRadius')
                    if not rad or float(rad[0]) < 1.0:
                        problems.append((rec,
                                         f"Enemy controller {ctl[0]} has "
                                         f"autoTargetRadius "
                                         f"{rad[0] if rad else 'ABSENT'} "
                                         f"(no target acquisition)"))
    if problems:
        for rec, why in problems[:20]:
            print(f"  SOUL-PROC OFFENDER: {rec} :: {why}")
        raise SystemExit(
            f"Soul item-skill activation invariant FAILED: {len(problems)} "
            f"problem(s) across granted-skill souls (see offenders above)")
    print(f"  Soul item-skill activation invariant OK: {checked} granted-skill "
          f"soul(s) all have resolving Skill_* + itemSkillLevel >= 1 + playable "
          f"anims + live controllers.")


# ══════════════════════════════════════════════════════════════════════════
# BOSS SOULS WAVE (docs/BOSS_SOULS_DESIGN.md) - headliner + faction + completion
# souls. Every proc/augment/pet/equipment path below was DB-verified to resolve
# against the built .arz (dangling paths from the doc's Section 0 are avoided).
# ══════════════════════════════════════════════════════════════════════════

# Verified soul-usable procs referenced by the new designs (all resolve).
_SS_SPIRITBOLT = r'records\xpack\skills\monsterskills\activeattackprojectile\empusasoulcarver_spiritbolt.dbr'
_SS_LICHEQUEEN_SOULSTRIKE = r'records\skills\soulskills\lichequeen_soulstrike.dbr'
_SS_BARMANU_BLIZZARD = r'records\skills\soulskills\barmanu_blizzard.dbr'
_SS_THUNDERBALLNOVA = r'records\skills\soulskills\thunderballnova.dbr'
_SS_QUILLVINES = r'records\skills\soulskills\strongbark_quillvines.dbr'
_SS_EARTHFURY_RING = r'records\skills\soulskills\earthfury_ring.dbr'
_SS_BLADETWIRL = r'records\xpack\skills\monsterskills\activeattackradius\hero_bladetwirl2_ring.dbr'
_SS_SHADOWSURGE = r'records\skills\soulskills\nightstalker_shadowsurge.dbr'
_SS_BATTLESTANDARD = r'records\skills\warfare\battlestandard.dbr'
_SS_MANTICORE_QUILLS = r'records\skills\soulskills\manticore_quills.dbr'
_SS_SPELLSHOCK = r'records\xpack\skills\dream\drxspellbreaker_spellshock.dbr'
_SS_POISONORBS = r'records\skills\soulskills\poisonorbs.dbr'
_SS_SABERSLASH = r'records\skills\soulskills\furyclaw_saberslash.dbr'
_SS_DEMASTIA_STRIKE = r'records\skills\soulskills\demastia_strike.dbr'

# Verified augment (drx mastery) paths - VERBATIM strings (never a dangling _SK_*).
_AUG_TERNION = r'records\skills\spirit\drxternion.dbr'
_AUG_DEATHCHILL = r'records\skills\spirit\drxdeathchillaura.dbr'
_AUG_RAVAGES = r'records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr'  # real "ravages of time"
_AUG_DARKCOVENANT = r'records\skills\spirit\drxdarkcovenant.dbr'
_AUG_ENSLAVESPIRIT = r'records\skills\spirit\drxenslavespirit.dbr'
_AUG_DUALWEAPON = r'records\skills\warfare\drxdualweapontraining.dbr'
_AUG_ONSLAUGHT = r'records\skills\warfare\drxonslaught.dbr'
_AUG_BATTLERAGE = r'records\skills\warfare\drxbattlerage.dbr'
_AUG_WARHORN = r'records\skills\warfare\drxwarhorn.dbr'
_AUG_COLDAURA = r'records\skills\storm\drxcoldaura.dbr'
_AUG_SQUALL = r'records\skills\storm\drxsquall.dbr'
_AUG_STORMNIMBUS = r'records\skills\storm\drxstormnimbus.dbr'
_AUG_CHAINLIGHTNING = r'records\skills\storm\drxlightningbolt_chainlightning.dbr'  # real chain lightning
_AUG_LIGHTNINGBOLT = r'records\skills\storm\drxlightningbolt.dbr'
_AUG_PLAGUE = r'records\skills\nature\drxplague.dbr'
_AUG_HEARTOFOAK = r'records\skills\nature\drxheartofoak.dbr'
_AUG_REGROWTH = r'records\skills\nature\drxregrowth.dbr'
_AUG_LETHALSTRIKE = r'records\skills\stealth\drxlethalstrike.dbr'
_AUG_PHANTOMSTRIKE = r'records\xpack\skills\dream\drxphantomstrike.dbr'  # xpack (dream path dangles)
_AUG_CONCUSSIVE = r'records\skills\defensive\drxconcussiveblow.dbr'
_AUG_RALLY = r'records\skills\defensive\drxrally.dbr'
_AUG_STUDYPREY = r'records\skills\hunting\drxstudyprey.dbr'  # hunting (stealth path dangles)
_AUG_ENVENOM = r'records\skills\stealth\drxenvenomweapon.dbr'
_AUG_CALCSTRIKE = r'records\skills\stealth\drxcalculatedstrike.dbr'
_AUG_FIREENCHANT = r'records\skills\earth\drxfireenchantment.dbr'
_AUG_RINGOFFLAME = r'records\skills\earth\drxringofflame.dbr'
_AUG_ENERGYSHIELD = r'records\skills\storm\drxenergyshield.dbr'
_AUG_VOLCANICORB = r'records\skills\earth\drxvolcanicorb.dbr'

_BITMAP = {
    'n': (DATA_TYPE_STRING, r'SVItems\jewelry\soul_n_icon.tex'),
    'e': (DATA_TYPE_STRING, r'SVItems\jewelry\soul_e_icon.tex'),
    'l': (DATA_TYPE_STRING, r'SVItems\jewelry\soul_l_icon.tex'),
}


def _bmp(diff):
    """Per-tier icon override tuple for the stats dict."""
    return {'bitmap': _BITMAP[diff]}


# ── 2.1 Ainex, Queen of Crows (REPLACE the thin orphan placeholder in place) ──

def _create_ainex_soul(db):
    """Ainex (um_ainex_45) - spectral vitality caster. REPLACES the thin
    svc_uber\\ainex_soul_{n,e,l} placeholder authored by _place_orphan_monsters
    at the SAME paths (no second creator). Proc = her soul-carver spirit bolt;
    augments = triple vitality bolts + crow-queen death aura. Level 45/59/71."""
    MONSTER = r'records\xpack\creatures\monster\empusa\um_ainex_45.dbr'
    TAG = 'tagSVCSoulAinex'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = [
        {'diff': 'n', 'itemLevel': 45, 'stats': {
            **_bmp('n'),
            'itemSkillName': (S, _SS_SPIRITBOLT), 'itemSkillLevel': (I, 4),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_TERNION), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, 3),
            'offensiveLifeMin': (F, 45.0), 'offensiveLifeMax': (F, 70.0), 'offensiveLifeModifier': (I, 25),
            'offensiveColdMin': (F, 25.0), 'offensiveColdMax': (F, 40.0),
            'offensiveLifeLeechMin': (F, 25.0), 'offensivePercentCurrentLifeMin': (F, 4.0),
            'characterDodgePercent': (F, 14.0), 'characterDeflectProjectile': (F, 14.0),
            'defensiveElementalResistance': (F, 15.0), 'defensiveLife': (F, 18.0),
            'characterIntelligenceModifier': (F, 8.0), 'characterDexterityModifier': (F, 6.0),
            'characterManaModifier': (F, 10.0), 'characterLifeModifier': (F, 8.0),
            'characterSpellCastSpeedModifier': (I, 18), 'characterDefensiveAbilityModifier': (F, 6.0),
            # Neutralize leftover physical/strength from the orphan placeholder (caster, no phys)
            'offensivePhysicalMin': (F, 0.0), 'offensivePhysicalMax': (F, 0.0),
            'characterStrengthModifier': (F, 0.0),
        }},
        {'diff': 'e', 'itemLevel': 59, 'stats': {
            **_bmp('e'),
            'itemSkillName': (S, _SS_SPIRITBOLT), 'itemSkillLevel': (I, 6),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_TERNION), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, 4),
            'offensiveLifeMin': (F, 80.0), 'offensiveLifeMax': (F, 120.0), 'offensiveLifeModifier': (I, 38),
            'offensiveColdMin': (F, 38.0), 'offensiveColdMax': (F, 58.0),
            'offensiveLifeLeechMin': (F, 38.0), 'offensivePercentCurrentLifeMin': (F, 5.0),
            'characterDodgePercent': (F, 18.0), 'characterDeflectProjectile': (F, 18.0),
            'defensiveElementalResistance': (F, 20.0), 'defensiveLife': (F, 26.0),
            'characterIntelligenceModifier': (F, 11.0), 'characterDexterityModifier': (F, 9.0),
            'characterManaModifier': (F, 14.0), 'characterLifeModifier': (F, 11.0),
            'characterSpellCastSpeedModifier': (I, 28), 'characterDefensiveAbilityModifier': (F, 9.0),
            'offensivePhysicalMin': (F, 0.0), 'offensivePhysicalMax': (F, 0.0),
            'characterStrengthModifier': (F, 0.0),
        }},
        {'diff': 'l', 'itemLevel': 71, 'stats': {
            **_bmp('l'),
            'itemSkillName': (S, _SS_SPIRITBOLT), 'itemSkillLevel': (I, 8),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_TERNION), 'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, 5),
            'offensiveLifeMin': (F, 120.0), 'offensiveLifeMax': (F, 185.0), 'offensiveLifeModifier': (I, 55),
            'offensiveColdMin': (F, 55.0), 'offensiveColdMax': (F, 82.0),
            'offensiveLifeLeechMin': (F, 55.0), 'offensivePercentCurrentLifeMin': (F, 6.0),
            'characterDodgePercent': (F, 22.0), 'characterDeflectProjectile': (F, 22.0),
            'defensiveElementalResistance': (F, 25.0), 'defensiveLife': (F, 34.0),
            'characterIntelligenceModifier': (F, 14.0), 'characterDexterityModifier': (F, 11.0),
            'characterManaModifier': (F, 18.0), 'characterLifeModifier': (F, 16.0),
            'characterSpellCastSpeedModifier': (I, 40), 'characterDefensiveAbilityModifier': (F, 11.0),
            'offensivePhysicalMin': (F, 0.0), 'offensivePhysicalMax': (F, 0.0),
            'characterStrengthModifier': (F, 0.0),
        }},
    ]
    paths = _create_soul(db, 'ainex', TAG, tiers, MONSTER, 66.0)
    print(f"  Ainex soul: rich spectral-caster block at {len(paths)} svc_uber paths (replaced placeholder)")
    return paths


# ── 2.3 Limos Lifeeater STUB FIX (scan-and-set the 3 existing stub records) ──

def _fix_limos_lifeeater_stub(db):
    """Limos Lifeeater (um_frost_36) - complete the 3 pure-stub
    limoslifeater_soul_{n,e,l} records in place (scan-and-set, keep wiring).
    Life-drain proc (convention: _AC_ON_ATTACK per sandwraith/elephantsnatcher)
    + dark-covenant + real ravages-of-time. Retag + reset itemLevel 36/54/69."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    # (diff, itemLevel, skLv, augLv, lifeMin, lifeMax, lifeMod, leech, curLife,
    #  resShred, resShredDur, lifeModPct, manaMod, intMod, defLife, defLeech, lifeRegenMod)
    tiers = [
        ('n', 36, 3, 2, 35.0, 55.0, 22, 35.0, 4.0, 10.0, 3.0, 12.0, 6.0, 5.0, 20.0, 25.0, 15),
        ('e', 54, 5, 3, 60.0, 92.0, 35, 48.0, 5.0, 15.0, 3.0, 17.0, 9.0, 8.0, 28.0, 35.0, 22),
        ('l', 69, 7, 4, 95.0, 150.0, 55, 65.0, 6.0, 20.0, 4.0, 24.0, 12.0, 11.0, 38.0, 48.0, 30),
    ]
    tier_by_diff = {t[0]: t for t in tiers}
    total = 0
    for name in list(db.record_names()):
        nl = name.lower()
        if 'limoslifeater_soul' not in nl or 'equipmentring' not in nl:
            continue
        if 'ancientlimoslifeater' in nl:
            continue  # separate Olympus super-variant soul, not this stub
        for diff, t in tier_by_diff.items():
            if nl.endswith(f'_soul_{diff}.dbr'):
                (_, ilvl, sk, aug, lmin, lmax, lmod, leech, cur, rs, rsd,
                 lmp, mm, im, dl, dll, lrm) = t
                stats = {
                    **_bmp(diff),
                    'itemNameTag': (S, 'tagSVCSoulLimosLifeeater'),
                    'itemLevel': (I, ilvl), 'levelRequirement': (I, ilvl - 5),
                    'itemSkillName': (S, _SS_LIFE_DRAIN), 'itemSkillLevel': (I, sk),
                    'itemSkillAutoController': (S, _AC_ON_ATTACK),
                    'augmentSkillName1': (S, _AUG_DARKCOVENANT), 'augmentSkillLevel1': (I, aug),
                    'augmentSkillName2': (S, _AUG_RAVAGES), 'augmentSkillLevel2': (I, aug),
                    'offensiveLifeMin': (F, lmin), 'offensiveLifeMax': (F, lmax),
                    'offensiveLifeModifier': (I, lmod), 'offensiveLifeLeechMin': (F, leech),
                    'offensivePercentCurrentLifeMin': (F, cur),
                    'offensiveTotalResistanceReductionAbsoluteMin': (F, rs),
                    'offensiveTotalResistanceReductionAbsoluteDurationMin': (F, rsd),
                    'characterLifeModifier': (F, lmp), 'characterManaModifier': (F, mm),
                    'characterIntelligenceModifier': (F, im),
                    'defensiveLife': (F, dl), 'defensiveLifeLeech': (F, dll),
                    'characterLifeRegenModifier': (I, lrm),
                }
                _set_soul_fields(db, name, stats)
                total += 1
                break
    print(f"  Limos Lifeeater stub completed: {total} records (life-drain, Lv 36/54/69)")
    return total


# ── 2.4 Kallixenia the Lich Queen (D2NPC Akara) ──

def _create_kallixenia_soul(db):
    """Kallixenia (01_akara) - lich-queen caster raining soul orbs. Level 36/54/69."""
    MONSTER = r'records\drxcreatures\xurder\d2npc\01_akara.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, lmin, lmax, lmod, cmin, cmax, leech, im, mm, lm,
             cast, manaregen, dl, dc, mb):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_LICHEQUEEN_SOULSTRIKE), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_DEATHCHILL), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_TERNION), 'augmentSkillLevel2': (I, aug),
            'offensiveLifeMin': (F, lmin), 'offensiveLifeMax': (F, lmax), 'offensiveLifeModifier': (I, lmod),
            'offensiveColdMin': (F, cmin), 'offensiveColdMax': (F, cmax), 'offensiveLifeLeechMin': (F, leech),
            'characterIntelligenceModifier': (F, im), 'characterManaModifier': (F, mm),
            'characterLifeModifier': (F, lm), 'characterSpellCastSpeedModifier': (I, cast),
            'characterManaRegenModifier': (I, manaregen),
            'defensiveLife': (F, dl), 'defensiveCold': (F, dc), 'defensiveManaBurnRatio': (F, mb),
        }}
    tiers = [
        tier('n', 36, 3, 2, 40.0, 62.0, 25, 25.0, 40.0, 30.0, 8.0, 12.0, 8.0, 20, 15, 20.0, 12.0, 20.0),
        tier('e', 54, 5, 3, 72.0, 110.0, 38, 40.0, 62.0, 45.0, 11.0, 17.0, 11.0, 32, 22, 28.0, 18.0, 28.0),
        tier('l', 69, 7, 4, 105.0, 165.0, 55, 55.0, 85.0, 60.0, 14.0, 22.0, 15.0, 46, 30, 36.0, 24.0, 36.0),
    ]
    paths = _create_soul(db, 'kallixenia', 'tagSVCSoulKallixenia', tiers, MONSTER, 66.0)
    print(f"  Kallixenia soul: lich-queen caster ({len(paths)} paths, 66% drop)")
    return paths


# ── 2.6 Zilla the Blade Dancer ──

def _create_zilla_soul(db):
    """Zilla (crowheroes\\zilla) - dual-blade freezing whirlwind. Level 45/60/73."""
    MONSTER = r'records\drxcreatures\crowheroes\zilla.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, pmin, pmax, pmod, cmin, cmax, frzchance,
             asm, tsm, dodge, strm, dexm, oam, lm, dc):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_BLADETWIRL), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_DUALWEAPON), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_ONSLAUGHT), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveColdMin': (F, cmin), 'offensiveColdMax': (F, cmax),
            'offensiveFreezeMin': (F, 0.5), 'offensiveFreezeMax': (F, 1.5), 'offensiveFreezeChance': (F, frzchance),
            'offensivePierceRatioModifier': (I, 15),
            'characterAttackSpeedModifier': (F, asm), 'characterTotalSpeedModifier': (I, tsm),
            'characterDodgePercent': (F, dodge),
            'characterStrengthModifier': (F, strm), 'characterDexterityModifier': (F, dexm),
            'characterOffensiveAbilityModifier': (F, oam), 'characterLifeModifier': (F, lm),
            'defensiveCold': (F, dc),
        }}
    tiers = [
        tier('n', 45, 4, 3, 55.0, 80.0, 30, 30.0, 48.0, 15.0, 14.0, 10, 10.0, 6.0, 8.0, 6.0, 10.0, 15.0),
        tier('e', 60, 6, 4, 85.0, 118.0, 42, 42.0, 66.0, 18.0, 18.0, 13, 13.0, 8.0, 11.0, 8.0, 13.0, 21.0),
        tier('l', 73, 8, 5, 120.0, 160.0, 57, 57.0, 90.0, 22.0, 22.0, 16, 16.0, 11.0, 15.0, 11.0, 18.0, 28.0),
    ]
    paths = _create_soul(db, 'zilla', 'tagSVCSoulZilla', tiers, MONSTER, 66.0)
    print(f"  Zilla soul: dual-blade cold whirlwind ({len(paths)} paths)")
    return paths


# ── 2.7 Numberouane the Frost King ──

def _create_numberouane_soul(db):
    """Numberouane (crowheroes\\numberouane) - walking blizzard. Level 45/60/73."""
    MONSTER = r'records\drxcreatures\crowheroes\numberouane.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, cmin, cmax, cmod, slow, slowdur, pmin, pmax, lm, im, dc):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_BARMANU_BLIZZARD), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_COLDAURA), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_SQUALL), 'augmentSkillLevel2': (I, aug),
            'offensiveColdMin': (F, cmin), 'offensiveColdMax': (F, cmax), 'offensiveColdModifier': (I, cmod),
            'offensiveSlowColdMin': (F, slow), 'offensiveSlowColdDurationMin': (F, slowdur),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax),
            'characterLifeModifier': (F, lm), 'characterIntelligenceModifier': (F, im),
            'characterManaModifier': (F, im), 'defensiveCold': (F, dc),
            'characterSpellCastSpeedModifier': (I, int(cmod)),
        }}
    tiers = [
        tier('n', 45, 4, 3, 40.0, 62.0, 25, 25.0, 3.0, 20.0, 34.0, 10.0, 8.0, 25.0),
        tier('e', 60, 6, 4, 58.0, 88.0, 35, 35.0, 3.0, 28.0, 48.0, 13.0, 11.0, 34.0),
        tier('l', 73, 8, 5, 78.0, 118.0, 48, 48.0, 4.0, 38.0, 62.0, 18.0, 14.0, 44.0),
    ]
    paths = _create_soul(db, 'numberouane', 'tagSVCSoulNumberouane', tiers, MONSTER, 66.0)
    print(f"  Numberouane soul: frost-king blizzard ({len(paths)} paths)")
    return paths


# ── 2.8 Kreeloo the Telkine Ghost ──

def _create_kreeloo_soul(db):
    """Kreeloo (crowheroes\\kreeloo) - telkine chaos-lightning. Level 21/44/60."""
    MONSTER = r'records\drxcreatures\crowheroes\kreeloo.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug1, aug2, lmin, lmax, lmod, lifemin, lifemax, im, mm, lm, cast, dl, dlife):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_THUNDERBALLNOVA), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_CHAINLIGHTNING), 'augmentSkillLevel1': (I, aug1),
            'augmentSkillName2': (S, _AUG_STORMNIMBUS), 'augmentSkillLevel2': (I, aug2),
            'offensiveLightningMin': (F, lmin), 'offensiveLightningMax': (F, lmax), 'offensiveLightningModifier': (I, lmod),
            'offensiveLifeMin': (F, lifemin), 'offensiveLifeMax': (F, lifemax),
            'characterIntelligenceModifier': (F, im), 'characterManaModifier': (F, mm),
            'characterLifeModifier': (F, lm), 'characterSpellCastSpeedModifier': (I, cast),
            'defensiveLightning': (F, dl), 'defensiveLife': (F, dlife),
        }}
    tiers = [
        tier('n', 21, 3, 2, 2, 25.0, 45.0, 25, 12.0, 20.0, 6.0, 8.0, 6.0, 14, 15.0, 12.0),
        tier('e', 44, 5, 3, 3, 40.0, 68.0, 32, 18.0, 30.0, 9.0, 12.0, 9.0, 22, 22.0, 18.0),
        tier('l', 60, 7, 4, 3, 70.0, 120.0, 42, 26.0, 44.0, 12.0, 16.0, 13.0, 30, 30.0, 24.0),
    ]
    paths = _create_soul(db, 'kreeloo', 'tagSVCSoulKreeloo', tiers, MONSTER, 66.0)
    print(f"  Kreeloo soul: telkine chaos-lightning ({len(paths)} paths)")
    return paths


# ── 2.9 Kaets the Ascacophus (plant summoner - reuses existing SpawnPet skill) ──

def _create_kaets_soul(db):
    """Kaets (crowheroes\\kaets) - nature summoner raising quill-vines. Level 44/60/73.
    itemSkillName = the existing soul-usable strongbark_quillvines SpawnPet, granted
    as an activated skill with NO autocast controller (chimera/hydra soul pattern)."""
    MONSTER = r'records\drxcreatures\crowheroes\kaets.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, pmin, pmax, pmod, poismin, poismax, poisdur, lm, lrm, defbleed, defpois):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_QUILLVINES), 'itemSkillLevel': (I, sk),
            # NO itemSkillAutoController (activated summon, like chimera_soul/hydra_soul)
            'augmentSkillName1': (S, _AUG_PLAGUE), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_HEARTOFOAK), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveSlowPoisonMin': (F, poismin), 'offensiveSlowPoisonMax': (F, poismax),
            'offensiveSlowPoisonDurationMin': (F, poisdur),
            'characterLifeModifier': (F, lm), 'characterLifeRegenModifier': (I, lrm),
            'defensiveBleeding': (F, defbleed), 'defensivePoison': (F, defpois),
        }}
    tiers = [
        tier('n', 44, 3, 2, 30.0, 48.0, 22, 30.0, 50.0, 3.0, 12.0, 15, 15.0, 15.0),
        tier('e', 60, 4, 3, 42.0, 66.0, 30, 45.0, 72.0, 3.0, 17.0, 22, 21.0, 21.0),
        tier('l', 73, 6, 4, 60.0, 92.0, 42, 65.0, 100.0, 4.0, 24.0, 30, 28.0, 28.0),
    ]
    paths = _create_soul(db, 'kaets', 'tagSVCSoulKaets', tiers, MONSTER, 66.0)
    print(f"  Kaets soul: nature quill-vine summoner ({len(paths)} paths)")
    return paths


# ── 2.10 Anapaest the Dishonor Guard ──

def _create_anapaest_soul(db):
    """Anapaest (drxdishonorguard\\anapaest_45) - gigantes ground-breaker tank.
    Level 51/64/75. NOTE: monster's Finger2 currently points at loot tables; the
    soul wiring re-points it (standard Finger2 soul slot)."""
    MONSTER = r'records\drxcreatures\drxdishonorguard\anapaest_45.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, pmin, pmax, pmod, slow, slowdur, strm, lm, lregen,
             lregenmod, defphys, defprotmod, oam, conmod):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_EARTHFURY_RING), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_ONSLAUGHT), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_WARHORN), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveSlowTotalSpeedMin': (F, slow), 'offensiveSlowTotalSpeedDurationMin': (F, slowdur),
            'characterStrengthModifier': (F, strm), 'characterLifeModifier': (F, lm),
            'characterLifeRegen': (F, lregen), 'characterLifeRegenModifier': (I, lregenmod),
            'defensivePhysical': (F, defphys), 'defensiveProtectionModifier': (F, defprotmod),
            'characterOffensiveAbilityModifier': (F, oam), 'characterConstitutionModifier': (F, conmod),
        }}
    tiers = [
        tier('n', 51, 4, 3, 70.0, 100.0, 35, 15.0, 3.0, 8.0, 14.0, 6.0, 20, 15.0, 10.0, 6.0, 6.0),
        tier('e', 64, 6, 4, 100.0, 145.0, 49, 21.0, 3.0, 11.0, 20.0, 9.0, 28, 21.0, 14.0, 8.0, 8.0),
        tier('l', 75, 8, 5, 150.0, 210.0, 66, 28.0, 4.0, 15.0, 27.0, 12.0, 38, 28.0, 19.0, 11.0, 11.0),
    ]
    paths = _create_soul(db, 'anapaest', 'tagSVCSoulAnapaest', tiers, MONSTER, 66.0)
    print(f"  Anapaest soul: gigantes ground-breaker tank ({len(paths)} paths)")
    return paths
# ── 2.2 Blood Witch High Priest - SUMMON (Melinoe blade-dancer pet from Lyia) ──

def _create_bwpriest_pet_skill(db):
    """Blood Witch High Priest summon: 3 Melinoe blade-dancer pets cloned from
    Lyia (Boneash pattern). Blade/necro/blood loadout. Permanent (no TTL)."""
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')
    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'
    pet_paths = [
        r'records\skills\soulskills\pets\bwpriest_1.dbr',
        r'records\skills\soulskills\pets\bwpriest_2.dbr',
        r'records\skills\soulskills\pets\bwpriest_3.dbr',
    ]
    life = [4200, 6000, 8000]
    life_regen = [22.0, 40.0, 60.0]
    dmg_min = [55, 85, 120]
    dmg_max = [85, 130, 180]
    src_monster = _find_record(db, r'records\drxcreatures\bloodwitch\skills\discipleboss_bladedancer.dbr')
    if not src_monster:
        print("  WARNING: bladedancer source not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)
        if src_monster:
            _copy_animation_fields(db, src_monster, path)
            _update_existing_fields(db, src_monster, path, _SKILL_PREFIXES)
        # B-SUMMON-2: the clone brought Lyia's Maenad/JackalMan per-weapon .anm
        # overrides; the source monster (discipleboss_bladedancer) has none to
        # overwrite them (it drives anim from anm_melinoe). The pet dual-wields,
        # so its foreign dHanded overrides play on the melinoe body -> INVISIBLE
        # body. Strip every override the source monster does not define so the
        # pet renders/animates purely from anm_melinoe, like the monster.
        n_stripped = _strip_foreign_anim_overrides(db, path, src_monster)
        if n_stripped:
            print(f"  {path.rsplit(chr(92), 1)[-1]}: stripped {n_stripped} "
                  f"foreign .anm overrides (anm_melinoe now drives the body)")
        sf = db.set_field
        # ── Equipment: mirror the SOURCE monster (discipleboss_bladedancer)
        #    proven loadout (B-SUMMON-1). The prior player-unique swords
        #    (u_n_003 etc., itemClassification Epic) never auto-equipped ->
        #    the blade-dancer showed no proper weapon. The real blade-dancer
        #    dual-wields the monster weapon wep_bladedancersword (Rare, which
        #    DOES auto-equip); no armor slots (the melinoe body is the look).
        _BDSWORD = r'records\drxcreatures\bloodwitch\skills\skilleffects'
        _bd_swords = [_BDSWORD + r'\wep_bladedancersword01.dbr',
                      _BDSWORD + r'\wep_bladedancersword02.dbr',
                      _BDSWORD + r'\wep_bladedancersword03.dbr']
        _set_pet_equipment(db, path, _loadout_spec([
            ('LeftHand', 100.0, 1000, _bd_swords),
            ('RightHand', 100.0, 1000, _bd_swords),
        ]))
        # Disable the stale unique armband/ring slots from the earlier
        # authoring (the source blade-dancer has Forearm/Finger1 chance 0).
        sf(path, 'chanceToEquipForearm', 0.0)
        sf(path, 'chanceToEquipFinger1', 0.0)
        sf(path, 'charLevel', [40, 56, 71])  # match source blade-dancer band (B-SUMMON-1); was 1/2/3
        # D5 (build30): the BASE melinoe mesh, NOT DRX\meshes\melinoe01.msh - the
        # DRX mesh embeds shader XPack\Shaders\standardblendedglowskinned.ssh which
        # the engine resolves only in Resources\XPack\Shaders.arc (absent there) ->
        # INVISIBLE body. Base mesh = base-scoped Shaders\standardskinned.ssh ->
        # renders; same melinoe skeleton (anm_melinoe + dual-wield unchanged);
        # crimson kept via bladedancer.tex. Precedent: um_demastia_47/um_insenzia_48.
        sf(path, 'mesh', r'XPack\Creatures\Monster\Melinoe\Melinoe01.msh')
        sf(path, 'baseTexture', r'DRXtextures\creatures\bloodwitch\bladedancer.tex')
        sf(path, 'bumpTexture', '')
        sf(path, 'scale', 1.4)
        sf(path, 'description', 'tagBWHighPriest')
        sf(path, 'characterRacialProfile', 'Demon')
        sf(path, 'controller', CONTROLLER)
        sf(path, 'charAnimationTableName', r'records\xpack\creatures\monster\melinoe\anm\anm_melinoe.dbr')
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 600.0)
        sf(path, 'characterManaRegen', 20.0)
        sf(path, 'characterStrength', 300.0)
        sf(path, 'characterDexterity', 300.0)
        sf(path, 'characterIntelligence', 200.0)
        sf(path, 'characterAttackSpeed', 1.0)
        sf(path, 'characterRunSpeed', 1.2)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)
        sf(path, 'StatusIcon', r'DRXtextures\skill icons\spirit\bonefiendup.tex')
        sf(path, 'StatusIconRed', r'DRXtextures\skill icons\spirit\bonefienddown.tex')

    summon_path = r'records\skills\soulskills\summon_bwpriest.dbr'
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)
    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonBWHighPriest')
    sf(summon_path, 'skillManaCost', [250.0, 300.0, 350.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName', r'DRXtextures\skill icons\spirit\bonefiendup.tex')
    sf(summon_path, 'skillDownBitmapName', r'DRXtextures\skill icons\spirit\bonefienddown.tex')
    print("  Blood High Priest summon: 3 Melinoe blade-dancer pets + summon skill")
    return True


def _create_bwpriest_soul(db):
    """Blood Witch High Priest soul (c_disciple_miniboss) - summon-soul shape.
    Level 39/56/71."""
    MONSTER = r'records\drxcreatures\bloodwitch\c_disciple_miniboss.dbr'
    SUMMON = r'records\skills\soulskills\summon_bwpriest.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, lm, im, mm, lmin, lmax, leech, dl, cast, manaregen):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, SUMMON), 'itemSkillLevel': (I, sk),
            'augmentSkillName1': (S, _AUG_DARKCOVENANT), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, aug),
            'characterLifeModifier': (F, lm), 'characterIntelligenceModifier': (F, im),
            'characterManaModifier': (F, mm),
            'offensiveLifeMin': (F, lmin), 'offensiveLifeMax': (F, lmax), 'offensiveLifeLeechMin': (F, leech),
            'defensiveLife': (F, dl), 'characterSpellCastSpeedModifier': (I, cast),
            'characterManaRegenModifier': (I, manaregen),
        }}
    tiers = [
        tier('n', 39, 1, 2, 10.0, 6.0, 8.0, 25.0, 40.0, 20.0, 18.0, 14, 12),
        tier('e', 56, 2, 3, 14.0, 9.0, 11.0, 38.0, 58.0, 30.0, 26.0, 20, 18),
        tier('l', 71, 3, 4, 19.0, 12.0, 15.0, 55.0, 82.0, 42.0, 34.0, 28, 24),
    ]
    paths = _create_soul(db, 'bwpriest', 'tagSVCSoulBWHighPriest', tiers, MONSTER, 66.0)
    print(f"  Blood High Priest soul: summon-soul ({len(paths)} paths)")
    return paths


# ── 2.5 Lil'Lued the Elder Djinn - SUMMON (storm djinn pet from Lyia) ──

def _create_lillued_pet_skill(db):
    """Lil'Lued Elder Djinn summon: 3 djinn pets cloned from Lyia (Boneash
    staff-caster pattern). Storm staff/armband/ring loadout. Permanent."""
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')
    lyia_sources = [
        r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
        r'records\skills\soulskills\pets\lyialeafsong_3.dbr',
    ]
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'
    pet_paths = [
        r'records\skills\soulskills\pets\lillued_1.dbr',
        r'records\skills\soulskills\pets\lillued_2.dbr',
        r'records\skills\soulskills\pets\lillued_3.dbr',
    ]
    life = [4800, 6800, 9000]
    life_regen = [25.0, 45.0, 65.0]
    dmg_min = [50, 75, 105]
    dmg_max = [80, 120, 165]
    src_monster = _find_record(db, r'records\drxcreatures\crowheroes\lillued_big.dbr')
    if not src_monster:
        print("  WARNING: lillued_big source not found!")

    for i, path in enumerate(pet_paths):
        src = _find_record(db, lyia_sources[i])
        if not src:
            print(f"  WARNING: Lyia source {lyia_sources[i]} not found!")
            return False
        db.clone_record(src, path)
        if src_monster:
            _copy_animation_fields(db, src_monster, path)
            _update_existing_fields(db, src_monster, path, _SKILL_PREFIXES)
        # B-SUMMON-2 (invisible body): the clone brought Lyia's Maenad/JackalMan
        # per-weapon .anm overrides. lillued_big (source) only defines Bat
        # unarmed anims, so the pet's foreign dHanded/sHanded overrides survived
        # -> playing JackalMan/Maenad on the Djinn body -> INVISIBLE. Strip every
        # override the source monster does not define; the kept Bat unarmed anims
        # match the source and the weapon slots fall back to anm_djinn (Djinn
        # dual-wield / one-hand set), all Djinn-skeleton -> the body renders.
        n_stripped = _strip_foreign_anim_overrides(db, path, src_monster)
        if n_stripped:
            print(f"  {path.rsplit(chr(92), 1)[-1]}: stripped {n_stripped} "
                  f"foreign .anm overrides (anm_djinn + Bat now drive the body)")
        sf = db.set_field
        # ── Equipment: mirror the SOURCE monster (lillued_big) proven
        #    loot-table loadout (B-SUMMON-1). Player-unique staves/gear never
        #    auto-equipped -> naked djinn; the real Lil'Lued dual-wields swords
        #    with a djinn monster-armband (no helm/torso on the djinn body).
        _set_pet_equipment(db, path, _loadout_spec([
            ('LeftHand', 50.0, 5000, [
                r'records\item\loottables\weapons\commondynamic\sword_n03.dbr',
                r'records\item\loottables\weapons\commondynamic\sword_e03.dbr',
                r'records\item\loottables\weapons\commondynamic\sword_l03.dbr']),
            ('RightHand', 100.0, 5000, [
                r'records\item\loottables\weapons\commondynamic\sword_n03.dbr',
                r'records\item\loottables\weapons\commondynamic\sword_e03.dbr',
                r'records\item\loottables\weapons\commondynamic\sword_l03.dbr']),
            ('Forearm', 45.0, 1000, [
                r'records\item\loottables\arms\mastertables\monster\n_djinn.dbr',
                r'records\item\loottables\arms\mastertables\monster\e_djinn.dbr',
                r'records\item\loottables\arms\mastertables\monster\l_djinn.dbr']),
            ('Finger1', 5.0, 5000, [
                r'records\item\loottables\finger\commondynamic\finger_n03.dbr',
                r'records\item\loottables\finger\commondynamic\finger_e03.dbr',
                r'records\item\loottables\finger\commondynamic\finger_l03.dbr']),
        ]))
        sf(path, 'charLevel', [40, 57, 71])  # match source Lil'Lued level band (B-SUMMON-1); was 1/2/3
        sf(path, 'mesh', r'Creatures\Monster\Djinn\ElderDjinn01.msh')
        sf(path, 'baseTexture', r'Creatures\Monster\Djinn\ElderDjinn01.tex')
        sf(path, 'bumpTexture', '')
        sf(path, 'scale', 2.7)
        sf(path, 'description', 'tagUrderBigLued')
        sf(path, 'characterRacialProfile', 'Demon')
        sf(path, 'controller', CONTROLLER)
        sf(path, 'charAnimationTableName', r'records\creature\monster\djinn\anm\anm_djinn.dbr')
        sf(path, 'characterLife', float(life[i]))
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 900.0)
        sf(path, 'characterManaRegen', 25.0)
        sf(path, 'characterStrength', 250.0)
        sf(path, 'characterDexterity', 200.0)
        sf(path, 'characterIntelligence', 350.0)
        sf(path, 'characterAttackSpeed', 1.0)
        sf(path, 'characterRunSpeed', 1.1)
        sf(path, 'characterSpellCastSpeed', 1.4)
        sf(path, 'handHitDamageMin', float(dmg_min[i]))
        sf(path, 'handHitDamageMax', float(dmg_max[i]))
        sf(path, 'dropItems', 0)
        sf(path, 'giveXP', 0)
        sf(path, 'experiencePoints', 0)
        sf(path, 'StatusIcon', r'DRXtextures\skill icons\spirit\bonefiendup.tex')
        sf(path, 'StatusIconRed', r'DRXtextures\skill icons\spirit\bonefienddown.tex')

    summon_path = r'records\skills\soulskills\summon_lillued.dbr'
    summon_src = _find_record(db, lyia_summon)
    if summon_src:
        db.clone_record(summon_src, summon_path)
    else:
        _ensure_record(db, summon_path, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_path, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)
    sf = db.set_field
    sf(summon_path, 'isPetDisplayable', 1)
    sf(summon_path, 'skillDisplayName', 'tagSVCSummonLilLued')
    sf(summon_path, 'skillManaCost', [300.0, 350.0, 400.0])
    sf(summon_path, 'spawnObjects', pet_paths)
    sf(summon_path, 'skillUpBitmapName', r'DRXtextures\skill icons\spirit\bonefiendup.tex')
    sf(summon_path, 'skillDownBitmapName', r'DRXtextures\skill icons\spirit\bonefienddown.tex')
    print("  Lil'Lued Elder Djinn summon: 3 storm-djinn pets + summon skill")
    return True


def _create_lillued_soul(db):
    """Lil'Lued Elder Djinn soul (lillued_big) - storm summon-soul. Level 40/57/71."""
    MONSTER = r'records\drxcreatures\crowheroes\lillued_big.dbr'
    SUMMON = r'records\skills\soulskills\summon_lillued.dbr'
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    def tier(diff, ilvl, sk, aug, lmin, lmax, lmod, tsm, lm, im, dl, cast):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, SUMMON), 'itemSkillLevel': (I, sk),
            'augmentSkillName1': (S, _AUG_STORMNIMBUS), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_SQUALL), 'augmentSkillLevel2': (I, aug),
            'offensiveLightningMin': (F, lmin), 'offensiveLightningMax': (F, lmax), 'offensiveLightningModifier': (I, lmod),
            'characterTotalSpeedModifier': (I, tsm), 'characterLifeModifier': (F, lm),
            'characterIntelligenceModifier': (F, im), 'defensiveLightning': (F, dl),
            'characterSpellCastSpeedModifier': (I, cast),
        }}
    tiers = [
        tier('n', 40, 1, 2, 25.0, 55.0, 22, 8, 10.0, 6.0, 15.0, 12),
        tier('e', 57, 2, 3, 38.0, 78.0, 30, 10, 14.0, 9.0, 22.0, 18),
        tier('l', 71, 3, 4, 55.0, 110.0, 40, 12, 19.0, 12.0, 30.0, 26),
    ]
    paths = _create_soul(db, 'lillued', 'tagSVCSoulLilLued', tiers, MONSTER, 66.0)
    print(f"  Lil'Lued soul: storm-djinn summon-soul ({len(paths)} paths)")
    return paths
# ── Section 3: Crow Heroes faction (remaining 9) - built together (warband style) ──

def _create_crow_heroes_souls(db):
    """The remaining 9 Crow Heroes souls (5 marquee full blocks + 4 novelties).
    Each calls _create_soul with per-monster tier tuples. Quest class, 66% drop.
    Uses only DB-verified proc/augment paths (never a dangling _SK_*)."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    CH = r'records\drxcreatures\crowheroes'
    total = 0

    # ---- Gorgus (Beastman DW blade-twin of Zilla, Lv 45/60/73) ----
    def gorgus_tier(diff, ilvl, sk, aug, pmin, pmax, pmod, cmin, cmax, asm, tsm, dodge, strm, dexm, oam, lm, dp):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_BLADETWIRL), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_DUALWEAPON), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_ONSLAUGHT), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveColdMin': (F, cmin), 'offensiveColdMax': (F, cmax), 'offensivePierceRatioModifier': (I, 15),
            'characterAttackSpeedModifier': (F, asm), 'characterTotalSpeedModifier': (I, tsm),
            'characterDodgePercent': (F, dodge), 'characterStrengthModifier': (F, strm),
            'characterDexterityModifier': (F, dexm), 'characterOffensiveAbilityModifier': (F, oam),
            'characterLifeModifier': (F, lm), 'defensivePhysical': (F, dp),
        }}
    total += len(_create_soul(db, 'gorgus', 'tagSVCSoulGorgus', [
        gorgus_tier('n', 45, 4, 3, 60.0, 88.0, 32, 22.0, 36.0, 14.0, 8, 10.0, 8.0, 6.0, 6.0, 10.0, 14.0),
        gorgus_tier('e', 60, 6, 4, 90.0, 130.0, 45, 32.0, 52.0, 18.0, 11, 13.0, 11.0, 8.0, 8.0, 13.0, 20.0),
        gorgus_tier('l', 73, 8, 5, 130.0, 168.0, 60, 44.0, 70.0, 22.0, 14, 16.0, 15.0, 11.0, 11.0, 18.0, 26.0),
    ], f'{CH}\\gorgus.dbr', 66.0))

    # ---- Jiaco the Nightstalker (Demon ninja, Lv 40/57/71) ----
    def jiaco_tier(diff, ilvl, sk, aug, pmin, pmax, pmod, pcmin, pcmax, leech, asm, rsm, dodge, dproj, dexm, oam, lm):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_SHADOWSURGE), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_LETHALSTRIKE), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_PHANTOMSTRIKE), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensivePierceMin': (F, pcmin), 'offensivePierceMax': (F, pcmax), 'offensivePierceRatioModifier': (I, 18),
            'offensiveLifeLeechMin': (F, leech),
            'characterAttackSpeedModifier': (F, asm), 'characterRunSpeedModifier': (F, rsm),
            'characterDodgePercent': (F, dodge), 'characterDeflectProjectile': (F, dproj),
            'characterDexterityModifier': (F, dexm), 'characterOffensiveAbilityModifier': (F, oam),
            'characterLifeModifier': (F, lm),
        }}
    total += len(_create_soul(db, 'jiaco', 'tagSVCSoulJiaco', [
        jiaco_tier('n', 40, 4, 3, 48.0, 72.0, 28, 28.0, 45.0, 20.0, 16.0, 10.0, 14.0, 12.0, 8.0, 8.0, 8.0),
        jiaco_tier('e', 57, 6, 4, 76.0, 108.0, 40, 40.0, 63.0, 28.0, 20.0, 13.0, 18.0, 15.0, 11.0, 11.0, 11.0),
        jiaco_tier('l', 71, 8, 5, 110.0, 150.0, 54, 55.0, 85.0, 38.0, 24.0, 16.0, 22.0, 18.0, 15.0, 15.0, 16.0),
    ], f'{CH}\\jiaco.dbr', 66.0))

    # ---- Yerk (Magical club-brute, Lv 41/57/71) ----
    def yerk_tier(diff, ilvl, sk, aug, pmin, pmax, pmod, stunmin, stunmax, sleepmin, sleepmax, strm, lm, conm, oam, dp, dpm):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_EARTHFURY_RING), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_BATTLERAGE), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_CONCUSSIVE), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveStunMin': (F, stunmin), 'offensiveStunMax': (F, stunmax),
            'offensiveSleepMin': (F, sleepmin), 'offensiveSleepMax': (F, sleepmax),
            'characterStrengthModifier': (F, strm), 'characterLifeModifier': (F, lm),
            'characterConstitutionModifier': (F, conm), 'characterOffensiveAbilityModifier': (F, oam),
            'defensivePhysical': (F, dp), 'defensiveProtectionModifier': (F, dpm),
        }}
    total += len(_create_soul(db, 'yerk', 'tagSVCSoulYerk', [
        yerk_tier('n', 41, 4, 3, 62.0, 92.0, 34, 1.0, 2.0, 1.5, 2.5, 8.0, 12.0, 6.0, 6.0, 15.0, 8.0),
        yerk_tier('e', 57, 6, 4, 92.0, 133.0, 47, 1.0, 2.0, 2.0, 3.0, 11.0, 17.0, 8.0, 8.0, 21.0, 11.0),
        yerk_tier('l', 71, 8, 5, 130.0, 175.0, 63, 1.0, 2.0, 2.5, 3.5, 15.0, 24.0, 11.0, 11.0, 28.0, 15.0),
    ], f'{CH}\\yerk.dbr', 66.0))

    # ---- Jabarto (Boarman storm-caster, Lv 18/42/58) ----
    def jabarto_tier(diff, ilvl, sk, aug, lmin, lmax, lmod, im, mm, lm, cast, dl):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_RING_LIGHTNING), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_STORMNIMBUS), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_CHAINLIGHTNING), 'augmentSkillLevel2': (I, aug),
            'offensiveLightningMin': (F, lmin), 'offensiveLightningMax': (F, lmax), 'offensiveLightningModifier': (I, lmod),
            'characterIntelligenceModifier': (F, im), 'characterManaModifier': (F, mm),
            'characterLifeModifier': (F, lm), 'characterSpellCastSpeedModifier': (I, cast),
            'defensiveLightning': (F, dl),
        }}
    total += len(_create_soul(db, 'jabarto', 'tagSVCSoulJabarto', [
        jabarto_tier('n', 18, 3, 2, 20.0, 40.0, 22, 6.0, 8.0, 6.0, 14, 15.0),
        jabarto_tier('e', 42, 5, 3, 34.0, 65.0, 32, 9.0, 12.0, 9.0, 22, 22.0),
        jabarto_tier('l', 58, 7, 4, 55.0, 100.0, 44, 12.0, 16.0, 13.0, 30, 30.0),
    ], f'{CH}\\jabarto.dbr', 66.0))

    # ---- Rainbowbright the Standard-Bearer (SUMMON via existing battlestandard SpawnPet) ----
    def rainbow_tier(diff, ilvl, sk, aug, pmin, pmax, pmod, strm, lm, oam, dam, dp, dpm):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_BATTLESTANDARD), 'itemSkillLevel': (I, sk),
            # NO autocast controller (activated summon, chimera/hydra pattern)
            'augmentSkillName1': (S, _AUG_BATTLERAGE), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_RALLY), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'characterStrengthModifier': (F, strm), 'characterLifeModifier': (F, lm),
            'characterOffensiveAbilityModifier': (F, oam), 'characterDefensiveAbilityModifier': (F, dam),
            'defensivePhysical': (F, dp), 'defensiveProtectionModifier': (F, dpm),
        }}
    total += len(_create_soul(db, 'rainbowbright', 'tagSVCSoulRainbowbright', [
        rainbow_tier('n', 46, 1, 2, 30.0, 48.0, 20, 8.0, 12.0, 8.0, 6.0, 14.0, 8.0),
        rainbow_tier('e', 61, 2, 3, 45.0, 70.0, 28, 11.0, 17.0, 11.0, 8.0, 20.0, 11.0),
        rainbow_tier('l', 74, 3, 4, 68.0, 95.0, 38, 15.0, 24.0, 15.0, 11.0, 28.0, 15.0),
    ], f'{CH}\\rainbowbright.dbr', 66.0))

    # ---- Novelties (recipe-row depth): Less, Nomnom, Gitar3, Kir4, Lil'Lued child ----
    # Less (Beast igloo-burst, Lv 10/37/54)
    def less_tier(diff, ilvl, sk, aug, cmin, cmax, im, lm, dc):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_SPELLSHOCK), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_RINGOFFLAME), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, aug),
            'offensiveColdMin': (F, cmin), 'offensiveColdMax': (F, cmax),
            'characterIntelligenceModifier': (F, im), 'characterLifeModifier': (F, lm),
            'defensiveCold': (F, dc),
        }}
    total += len(_create_soul(db, 'less', 'tagSVCSoulLess', [
        less_tier('n', 10, 2, 1, 8.0, 16.0, 4.0, 5.0, 10.0),
        less_tier('e', 37, 4, 2, 18.0, 32.0, 6.0, 7.0, 18.0),
        less_tier('l', 54, 6, 3, 30.0, 52.0, 9.0, 10.0, 26.0),
    ], f'{CH}\\less.dbr', 66.0))

    # Nomnom (Plague Feast beast, Lv 13/39/56)
    def nomnom_tier(diff, ilvl, sk, aug, poismin, poismax, poisdur, dexm, lm, dpois):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_VENOM_SPRAY), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_ENVENOM), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_PLAGUE), 'augmentSkillLevel2': (I, aug),
            'offensiveSlowPoisonMin': (F, poismin), 'offensiveSlowPoisonMax': (F, poismax),
            'offensiveSlowPoisonDurationMin': (F, poisdur),
            'characterDexterityModifier': (F, dexm), 'characterLifeModifier': (F, lm),
            'defensivePoison': (F, dpois),
        }}
    total += len(_create_soul(db, 'nomnom', 'tagSVCSoulNomnom', [
        nomnom_tier('n', 13, 2, 1, 20.0, 35.0, 3.0, 5.0, 5.0, 15.0),
        nomnom_tier('e', 39, 4, 2, 35.0, 55.0, 4.0, 7.0, 7.0, 22.0),
        nomnom_tier('l', 56, 6, 3, 55.0, 85.0, 5.0, 9.0, 10.0, 30.0),
    ], f'{CH}\\nomnom.dbr', 66.0))

    # Gitar3 (Lv1 reflect shrine turret novelty)
    def gitar_tier(diff, ilvl, sk, aug, lmin, lmax, refl, dl):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_RING_LIGHTNING), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_ENERGYSHIELD), 'augmentSkillLevel1': (I, aug),
            'offensiveLightningMin': (F, lmin), 'offensiveLightningMax': (F, lmax),
            'defensiveReflect': (F, refl), 'defensiveLightning': (F, dl),
        }}
    total += len(_create_soul(db, 'gitar3', 'tagSVCSoulGitar3', [
        gitar_tier('n', 1, 1, 1, 5.0, 12.0, 10.0, 12.0),
        gitar_tier('e', 20, 2, 2, 14.0, 26.0, 14.0, 18.0),
        gitar_tier('l', 40, 3, 3, 26.0, 44.0, 18.0, 24.0),
    ], f'{CH}\\gitar3.dbr', 66.0))

    # Kir4 (Lv20 bolt-trap novelty, pierce/ranged)
    def kir_tier(diff, ilvl, sk, aug, pcmin, pcmax, dexm, oam, dp):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_MANTICORE_QUILLS), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_STUDYPREY), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_CALCSTRIKE), 'augmentSkillLevel2': (I, aug),
            'offensivePierceMin': (F, pcmin), 'offensivePierceMax': (F, pcmax), 'offensivePierceRatioModifier': (I, 15),
            'characterDexterityModifier': (F, dexm), 'characterOffensiveAbilityModifier': (F, oam),
            'defensivePierce': (F, dp),
        }}
    total += len(_create_soul(db, 'kir4', 'tagSVCSoulKir4', [
        kir_tier('n', 20, 2, 1, 18.0, 32.0, 6.0, 6.0, 12.0),
        kir_tier('e', 42, 4, 2, 30.0, 52.0, 8.0, 8.0, 18.0),
        kir_tier('l', 58, 6, 3, 48.0, 78.0, 11.0, 11.0, 24.0),
    ], f'{CH}\\kir4.dbr', 66.0))

    # Lil'Lued CHILD (Lv8 "Standing Child" novelty). DISTINCT base name (lilluedchild)
    # so it never collides with the Elder Djinn's lillued_soul_* records.
    def child_tier(diff, ilvl, lm, im, dl):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'characterLifeModifier': (F, lm), 'characterIntelligenceModifier': (F, im),
            'characterManaModifier': (F, im), 'defensiveLife': (F, dl),
            'characterSpellCastSpeedModifier': (I, int(im)),
        }}
    total += len(_create_soul(db, 'lilluedchild', 'tagSVCSoulLilLuedChild', [
        child_tier('n', 8, 4.0, 4.0, 8.0),
        child_tier('e', 30, 6.0, 6.0, 14.0),
        child_tier('l', 50, 9.0, 9.0, 20.0),
    ], f'{CH}\\lillued.dbr', 66.0))

    print(f"  Crow Heroes faction: {total} soul records across 9 heroes")
    return total


# ── Section 4: D2 NPC trio (Charsi, Gheed; Kallixenia is separate) ──

def _create_d2npc_souls(db):
    """Charsi (smith bruiser) + Gheed (utility/luck merchant). Level 36/54/69."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    D2 = r'records\drxcreatures\xurder\d2npc'
    total = 0

    # Charsi the Smith - heavy physical charged-strike
    def charsi_tier(diff, ilvl, sk, aug, pmin, pmax, pmod, openmin, opendur, strm, oam, lm, dp):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_DEMASTIA_STRIKE), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_CALCSTRIKE), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_DUALWEAPON), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveSlowBleedingMin': (F, openmin), 'offensiveSlowBleedingDurationMin': (F, opendur),
            'characterStrengthModifier': (F, strm), 'characterOffensiveAbilityModifier': (F, oam),
            'characterLifeModifier': (F, lm), 'defensivePhysical': (F, dp),
        }}
    total += len(_create_soul(db, 'charsi', 'tagSVCSoulCharsi', [
        charsi_tier('n', 36, 4, 3, 48.0, 72.0, 28, 40.0, 3.0, 8.0, 6.0, 10.0, 14.0),
        charsi_tier('e', 54, 6, 4, 72.0, 108.0, 40, 60.0, 3.0, 11.0, 8.0, 14.0, 20.0),
        charsi_tier('l', 69, 8, 5, 105.0, 150.0, 55, 85.0, 4.0, 15.0, 11.0, 19.0, 28.0),
    ], f'{D2}\\01_charsi.dbr', 66.0))

    # Gheed the Merchant - the ONE intentionally non-combat utility soul (no proc/augments)
    def gheed_tier(diff, ilvl, life, lm, mm, tsm, dodge, dodgeproj, defprot, dam):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'characterLife': (I, life), 'characterLifeModifier': (F, lm),
            'characterManaModifier': (F, mm), 'characterTotalSpeedModifier': (I, tsm),
            'characterDodgePercent': (F, dodge), 'characterDeflectProjectile': (F, dodgeproj),
            'defensiveProtection': (F, defprot), 'characterDefensiveAbilityModifier': (F, dam),
        }}
    total += len(_create_soul(db, 'gheed', 'tagSVCSoulGheed', [
        gheed_tier('n', 36, 150, 12.0, 12.0, 8, 10.0, 8.0, 30.0, 8.0),
        gheed_tier('e', 54, 250, 16.0, 16.0, 10, 13.0, 11.0, 45.0, 11.0),
        gheed_tier('l', 69, 380, 22.0, 22.0, 12, 16.0, 14.0, 65.0, 15.0),
    ], f'{D2}\\01_gheed.dbr', 66.0))

    print(f"  D2 NPC souls: Charsi (smith) + Gheed (utility) = {total} records")
    return total


# ── Section 6: Other single-boss no-soul targets (5) ──

def _create_other_soul_targets(db):
    """Blood Shaman, Fleshrender, Anklesickle, Dark Monolith, Fire Trap souls."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    total = 0

    # Blood Abomination Spiritcaller (shadow/leech caster, Lv 40/56/71)
    def shaman_tier(diff, ilvl, sk, aug, cmin, cmax, lmin, lmax, leech, im, mm, lm, cast, dl):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_LIFE_DRAIN), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_DARKCOVENANT), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, aug),
            'offensiveColdMin': (F, cmin), 'offensiveColdMax': (F, cmax),
            'offensiveLifeMin': (F, lmin), 'offensiveLifeMax': (F, lmax), 'offensiveLifeLeechMin': (F, leech),
            'characterIntelligenceModifier': (F, im), 'characterManaModifier': (F, mm),
            'characterLifeModifier': (F, lm), 'characterSpellCastSpeedModifier': (I, cast),
            'defensiveLife': (F, dl),
        }}
    total += len(_create_soul(db, '04_spiritcaller', 'tagSVCSoulBloodShaman', [
        shaman_tier('n', 40, 3, 2, 20.0, 34.0, 35.0, 55.0, 30.0, 8.0, 10.0, 8.0, 18, 18.0),
        shaman_tier('e', 56, 5, 3, 30.0, 50.0, 55.0, 82.0, 42.0, 11.0, 14.0, 11.0, 28, 26.0),
        shaman_tier('l', 71, 7, 4, 44.0, 70.0, 82.0, 125.0, 58.0, 14.0, 18.0, 15.0, 40, 34.0),
    ], r'records\drxcreatures\bloodabomination\04_spiritcaller_40.dbr', 66.0))

    # Fleshrender (raptor rending bleed, Lv 30/50/65)
    def flesh_tier(diff, ilvl, sk, aug, pmin, pmax, pmod, bleedmin, bleeddur, pcmin, pcmax, dexm, strm, oam, asm):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_SABERSLASH), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_BATTLERAGE), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_LETHALSTRIKE), 'augmentSkillLevel2': (I, aug),
            'offensivePhysicalMin': (F, pmin), 'offensivePhysicalMax': (F, pmax), 'offensivePhysicalModifier': (I, pmod),
            'offensiveSlowBleedingMin': (F, bleedmin), 'offensiveSlowBleedingDurationMin': (F, bleeddur),
            'offensivePierceMin': (F, pcmin), 'offensivePierceMax': (F, pcmax), 'offensivePierceRatioModifier': (I, 15),
            'characterDexterityModifier': (F, dexm), 'characterStrengthModifier': (F, strm),
            'characterOffensiveAbilityModifier': (F, oam), 'characterAttackSpeedModifier': (F, asm),
        }}
    total += len(_create_soul(db, 'jo7_raptor', 'tagSVCSoulFleshrender', [
        flesh_tier('n', 30, 3, 2, 40.0, 62.0, 28, 55.0, 3.0, 20.0, 34.0, 8.0, 6.0, 6.0, 12.0),
        flesh_tier('e', 50, 5, 3, 62.0, 92.0, 40, 90.0, 3.0, 30.0, 48.0, 11.0, 8.0, 8.0, 16.0),
        flesh_tier('l', 65, 7, 4, 92.0, 130.0, 55, 135.0, 3.0, 42.0, 66.0, 15.0, 11.0, 11.0, 20.0),
    ], r'records\creature\monster\rumormonsters\orient\jo7_raptor_30.dbr', 66.0))

    # Ambush! Anklesickle (tidecrawler ambush strike, Lv 13/39/57)
    def ankle_tier(diff, ilvl, sk, aug, poismin, poismax, poisdur, pcmin, pcmax, dexm, dodge, dpois):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_POISONORBS), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _AUG_ENVENOM), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_STUDYPREY), 'augmentSkillLevel2': (I, aug),
            'offensiveSlowPoisonMin': (F, poismin), 'offensiveSlowPoisonMax': (F, poismax),
            'offensiveSlowPoisonDurationMin': (F, poisdur),
            'offensivePierceMin': (F, pcmin), 'offensivePierceMax': (F, pcmax), 'offensivePierceRatioModifier': (I, 15),
            'characterDexterityModifier': (F, dexm), 'characterDodgePercent': (F, dodge),
            'defensivePoison': (F, dpois),
        }}
    total += len(_create_soul(db, 'um_anklesickle', 'tagSVCSoulAnklesickle', [
        ankle_tier('n', 13, 2, 1, 20.0, 35.0, 3.0, 15.0, 26.0, 6.0, 6.0, 15.0),
        ankle_tier('e', 39, 4, 2, 35.0, 55.0, 4.0, 26.0, 42.0, 8.0, 8.0, 22.0),
        ankle_tier('l', 57, 6, 3, 55.0, 85.0, 5.0, 40.0, 62.0, 11.0, 10.0, 30.0),
    ], r'records\creature\monster\tidecrawler\um_anklesickle_13_ambush.dbr', 66.0))

    # Egypt Monolith (dark obelisk device, Lv 50/70/93)
    def monolith_tier(diff, ilvl, sk, aug, lmin, lmax, vmin, vmax, im, eleres, dl):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_RING_LIGHTNING), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_LIGHTNINGBOLT), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_DEATHCHILL), 'augmentSkillLevel2': (I, aug),
            'offensiveLightningMin': (F, lmin), 'offensiveLightningMax': (F, lmax),
            'offensiveLifeMin': (F, vmin), 'offensiveLifeMax': (F, vmax),
            'characterIntelligenceModifier': (F, im), 'defensiveElementalResistance': (F, eleres),
            'defensiveLife': (F, dl),
        }}
    total += len(_create_soul(db, 'egypt_monolith', 'tagSVCSoulDarkMonolith', [
        monolith_tier('n', 50, 3, 2, 30.0, 55.0, 15.0, 25.0, 8.0, 20.0, 20.0),
        monolith_tier('e', 70, 5, 3, 48.0, 80.0, 24.0, 40.0, 11.0, 26.0, 28.0),
        monolith_tier('l', 93, 7, 4, 72.0, 120.0, 36.0, 60.0, 15.0, 32.0, 36.0),
    ], r'records\creature\devices\darkobelisk\egypt_monolith_50.dbr', 66.0))

    # The Trap (fire trap device, Lv 25/45/68)
    def trap_tier(diff, ilvl, sk, aug, fmin, fmax, fmod, burnmin, burndur, retal, strm, df):
        return {'diff': diff, 'itemLevel': ilvl, 'stats': {
            **_bmp(diff),
            'itemSkillName': (S, _SS_FIRE_NOVA), 'itemSkillLevel': (I, sk),
            'itemSkillAutoController': (S, _AC_ON_HIT),
            'augmentSkillName1': (S, _AUG_FIREENCHANT), 'augmentSkillLevel1': (I, aug),
            'augmentSkillName2': (S, _AUG_RINGOFFLAME), 'augmentSkillLevel2': (I, aug),
            'offensiveFireMin': (F, fmin), 'offensiveFireMax': (F, fmax), 'offensiveFireModifier': (I, fmod),
            'offensiveSlowBurnMin': (F, burnmin), 'offensiveSlowBurnDurationMin': (F, burndur),
            'retaliationFireMin': (F, retal), 'retaliationFireMax': (F, retal * 1.6),
            'characterStrengthModifier': (F, strm), 'defensiveFire': (F, df),
        }}
    total += len(_create_soul(db, 'um_thetrap', 'tagSVCSoulFireTrap', [
        trap_tier('n', 25, 3, 2, 25.0, 45.0, 22, 12.0, 3.0, 15.0, 5.0, 20.0),
        trap_tier('e', 45, 5, 3, 40.0, 68.0, 32, 20.0, 3.0, 25.0, 7.0, 28.0),
        trap_tier('l', 68, 7, 4, 62.0, 100.0, 44, 32.0, 4.0, 40.0, 10.0, 36.0),
    ], r'records\creature\devices\firetrap\um_thetrap_25.dbr', 66.0))

    print(f"  Other single-boss soul targets: {total} records across 5 monsters")
    return total


# ── Guards: gate Common/no-class soul leaks (skeletaltyphon.dbr + tombguardian) ──

def _gate_common_soul_leaks(db):
    """Zero chanceToEquipFinger2 on records that carry soul loot but must NEVER
    drop a soul (design: only Hero/Boss/Quest drop souls, and these specific
    records are hand-picked exceptions that must stay dry):
      - skeletaltyphon.dbr (Common minion) + anm_skeletaltyphon.dbr (no class)
        both inherit undeadtyphon_soul at 100%. The real boss_skeletaltyphon_42/
        45/48 keep their soul (untouched).
      - um_tombguardian_26.dbr which _place_orphan_monsters wires to
        svc_uber\\um_tombguardian_soul (against the Hero/Boss/Quest design).

    This is an AUTHORITATIVE deny-list: it zeros the drop REGARDLESS of
    classification. _place_orphan_monsters deliberately skips these records when it
    promotes orphans (see _SOUL_DROP_DENY_SUBSTRINGS), so tombguardian is never
    promoted; but we force-zero here too so the deny-list is self-contained and
    robust to ordering.
    """
    gated = 0
    for name in list(db.record_names()):
        nl = name.replace('/', '\\').lower()
        if not any(sub in nl for sub in _SOUL_DROP_DENY_SUBSTRINGS):
            continue
        cur = db.get_field_value(name, 'chanceToEquipFinger2')
        if cur and float(cur) > 0:
            mc = db.get_field_value(name, 'monsterClassification')
            db.set_field(name, 'chanceToEquipFinger2', 0.0, DATA_TYPE_FLOAT)
            db._modified.add(name)
            gated += 1
            print(f"    gated soul drop OFF (class={mc}): {name}")
    print(f"  Common/no-class soul leaks gated: {gated} records")
    return gated


# All equipment slots a monster can carry an item in. A soul ring dropped in ANY
# of these leaks if the monster is not Hero/Boss/Quest.
_EQUIP_SLOTS = ('Finger1', 'Finger2', 'Head', 'Torso', 'LowerBody', 'Forearm',
                'RightHand', 'LeftHand', 'Misc1', 'Misc2', 'Misc3')
_SOUL_RING_MARK = 'equipmentring\\soul\\'


def _find_soul_drop_leaks(db):
    """Return every (record, class, [(slot, chance, soul_item), ...]) where a
    CREATURE that is NOT Hero/Boss/Quest has a soul ring in an equipment slot with
    a live chanceToEquip<slot> > 0.

    This is the exhaustive, slot-agnostic complement to the per-record gate in
    wire_souls_to_monsters (which only touches Finger2). It catches classification
    holes in the source data (e.g. um_prox_47 = no class, z_~v~ = Champion) and any
    future soul wired into Finger1/Misc/etc on a non-gated monster. Souls are the
    Hero/Boss/Quest-only design, so a non-gated live soul drop is always a bug.
    """
    leaks = []
    for name in db.record_names():
        nl = name.replace('/', '\\').lower()
        if '\\creature\\' not in nl and '\\creatures\\' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        # Fast screen: any soul-ring value in any loot*Item* field?
        has_soul_ring = False
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn.startswith('loot') and 'Item' in fn and tf.values:
                if any(isinstance(v, str) and _SOUL_RING_MARK in v.replace('/', '\\').lower()
                       for v in tf.values):
                    has_soul_ring = True
                    break
        if not has_soul_ring:
            continue
        mc = db.get_field_value(name, 'monsterClassification')
        if mc in ('Hero', 'Boss', 'Quest'):
            continue
        live = []
        for slot in _EQUIP_SLOTS:
            soul_item = None
            for i in range(1, 7):
                val = db.get_field_value(name, f'loot{slot}Item{i}')
                vals = val if isinstance(val, list) else ([val] if val is not None else [])
                for v in vals:
                    if isinstance(v, str) and _SOUL_RING_MARK in v.replace('/', '\\').lower():
                        soul_item = v
                        break
                if soul_item:
                    break
            if not soul_item:
                continue
            ch = db.get_field_value(name, f'chanceToEquip{slot}')
            if isinstance(ch, list):
                ch = ch[0] if ch else 0
            try:
                ch = float(ch)
            except (TypeError, ValueError):
                ch = 0.0
            if ch > 0:
                live.append((slot, ch, soul_item))
        if live:
            leaks.append((name, mc, live))
    return leaks


def _verify_no_unclassified_soul_leaks(db):
    """Build-time invariant: NO non-Hero/Boss/Quest creature may drop a soul in any
    equipment slot. Runs after all wiring + gating, before the drop forcer. Raises
    SystemExit (fails the build loud) on any leak, mirroring the MP spawn-equation
    guard. This is what makes flipping to the RELEASE default safe: it proves the
    Hero/Boss/Quest gate holds across EVERY slot for the whole roster, not just the
    Finger2 slot the per-record passes touch."""
    leaks = _find_soul_drop_leaks(db)
    if leaks:
        print(f"\n  SOUL-LEAK INVARIANT FAILED: {len(leaks)} non-Hero/Boss/Quest "
              f"creature(s) drop a soul:")
        for name, mc, live in leaks[:20]:
            for slot, ch, soul_item in live:
                print(f"    LEAK: {name} [class={mc!r}] "
                      f"chanceToEquip{slot}={ch} -> {soul_item}")
        raise SystemExit(
            f"Soul-drop gate breached: {len(leaks)} non-Hero/Boss/Quest creature(s) "
            f"still drop a soul (see leaks above). Fix classification or gate them.")
    print("  Soul-leak invariant OK: 0 non-Hero/Boss/Quest creatures drop a soul.")
    return 0


# Skill-granting string fields on a soul ring. Each holds a DBR path that MUST
# resolve to a real record or the engine silently grants nothing for it.
_SOUL_SKILL_FIELDS = (
    'itemSkillName', 'augmentSkillName1', 'augmentSkillName2',
    'augmentSkillName3', 'augmentSkillName4', 'itemSkillAutoController',
)
_SOUL_PATH_MARKERS = ('\\soul\\', '/soul/')


def _verify_soul_augments_resolve(db):
    """Build-time invariant: every skill a SOUL grants must resolve in the db.

    Soul rings grant skills by storing a DBR path verbatim (see
    `_set_soul_fields` -> `db.set_field`); nothing resolves the path, so a wrong
    one (a records\\skills\\dream\\* skill that really lives under
    records\\xpack\\skills\\dream\\*, or a skill that does not exist in TQAE at
    all like a Runemaster skill) makes the augment/proc a silent no-op in-game.
    This decodes augmentSkillName1..4 + itemSkillName + itemSkillAutoController on
    every soul and raises SystemExit (fails the build loud) on any dangling ref,
    mirroring the soul-leak and MP-equation invariants. The standalone
    tools/validate_soul_augments.py re-checks this on the WRITTEN .arz."""
    recset = {n.replace('/', '\\').lower() for n in db.record_names()}

    def _resolves(p):
        return p.replace('/', '\\').lower() in recset

    dangling = []  # (soul, field, dead_path)
    for name in db.record_names():
        low = name.lower()
        if not any(m in low for m in _SOUL_PATH_MARKERS):
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn not in _SOUL_SKILL_FIELDS or not tf.values:
                continue
            for val in tf.values:
                if isinstance(val, str) and val.strip() and not _resolves(val):
                    dangling.append((name, fn, val))

    if dangling:
        print(f"\n  SOUL-AUGMENT INVARIANT FAILED: {len(dangling)} soul skill "
              f"reference(s) do not resolve:")
        for soul, fn, val in dangling[:20]:
            print(f"    DANGLING: {soul} :: {fn} = {val!r}")
        raise SystemExit(
            f"Soul augment/proc gate breached: {len(dangling)} soul skill "
            f"reference(s) point at a record that does not exist (silent no-op). "
            f"Fix the skill-path constant(s) in apply_svc_patches.py.")
    print("  Soul-augment invariant OK: every soul augment/proc/item-skill "
          "reference resolves.")
    return 0
# ── Section 5: Table B "never-completed" completion pass (~51 bosses) ──
#
# Brings each wired-but-shallow boss soul up to exemplar depth by scan-and-setting
# a full stat block onto its existing <base>_soul_{n,e,l} records, KEEPING its proc
# and wiring (the _overhaul_main_toxeus_soul pattern; never clone_record, never
# re-wire the monster). Each spec gives BASE (Normal-tier) values; E/L auto-scale
# ~1.4x / 1.9x on numeric damage + modifier fields, proc level 4/6/8, aug 3/4/5.
# Matching is on the EXACT basename tail '\<base>_soul_{diff}.dbr' so greedy
# substrings (typhon vs undeadtyphon, hades vs sp_hades) never cross-hit.

# Exemplars already hand-crafted by dedicated fns - NEVER touched by this pass.
_COMPLETION_EXEMPLAR_BASES = frozenset({
    'boss_coldworm50', 'dagon', 'calybe', 'leinth', 'murderbunny',
    'sp_toxeus', 'toxeus', 'rakanizeus', 'boneash', 'pharaohshonorguard',
    'sp_hades', 'sphades',
})

# Damage/mod field names that get tier-scaled (E=1.4x, L=1.9x). Everything else
# (durations, chances, freeze secs, stun secs, small % speeds) is passed verbatim.
_SCALE_FIELDS = frozenset({
    'offensivePhysicalMin', 'offensivePhysicalMax', 'offensivePhysicalModifier',
    'offensiveFireMin', 'offensiveFireMax', 'offensiveFireModifier',
    'offensiveColdMin', 'offensiveColdMax', 'offensiveColdModifier',
    'offensiveLightningMin', 'offensiveLightningMax', 'offensiveLightningModifier',
    'offensiveLifeMin', 'offensiveLifeMax', 'offensiveLifeModifier',
    'offensivePierceMin', 'offensivePierceMax',
    'offensiveSlowPoisonMin', 'offensiveSlowPoisonMax',
    'offensiveSlowBleedingMin',
    'offensiveSlowBurnMin',
    'offensiveTotalResistanceReductionAbsoluteMin',
    'offensiveLifeLeechMin', 'offensivePercentCurrentLifeMin',
    'characterStrengthModifier', 'characterDexterityModifier', 'characterIntelligenceModifier',
    'characterLifeModifier', 'characterManaModifier',
    'characterOffensiveAbilityModifier', 'characterDefensiveAbilityModifier',
    'characterConstitutionModifier',
    'defensivePhysical', 'defensiveFire', 'defensiveCold', 'defensiveLightning',
    'defensivePoison', 'defensiveLife', 'defensivePierce', 'defensiveProtectionModifier',
    'characterSpellCastSpeedModifier', 'characterManaRegenModifier', 'characterLifeRegenModifier',
    'characterAttackSpeedModifier',
})


def _complete_boss_souls(db):
    """Deepen ~51 Table B boss souls in place (keep grant, add depth, tier-scale)."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # Each entry:
    #   base: exact soul basename stem (record tail = \<base>_soul_{n,e,l}.dbr)
    #   add_proc: (skill_path, controller) to ADD when the soul had no proc, else None
    #   aug1/aug2: (path, base_level) augments to (re)assert; None to leave existing
    #   base_stats: dict {field: value} at NORMAL tier (scaled for E/L per _SCALE_FIELDS)
    #   ctrl_for_kept: controller to (re)assert on the KEPT proc (matches its Class), or None
    # proc level: 4/6/8 (kept or added). aug level: base_level, base_level+1, base_level+2.
    C_ATK, C_HIT = _AC_ON_ATTACK, _AC_ON_HIT
    SPECS = [
        # ---- Quest-boss main-story bosses ----
        # Cyclops Polyphemus (worked example) - phys + stun (club)
        dict(base='polyphemus', ctrl=C_ATK,
             aug1=(_AUG_ONSLAUGHT, 3), aug2=(_AUG_BATTLERAGE, 3),
             stats={'offensivePhysicalMax': 60.0, 'offensivePhysicalModifier': 30,
                    'offensiveStunMin': 1.0, 'offensiveStunMax': 2.0,
                    'offensivePierceRatioModifier': 12, 'characterStrengthModifier': 8.0,
                    'characterConstitutionModifier': 6.0, 'characterOffensiveAbilityModifier': 6.0,
                    'defensivePhysical': 15.0, 'defensiveProtectionModifier': 8.0,
                    'characterTotalSpeedModifier': -4}),
        # Chimaera - summon (KEEP), pet-focused
        dict(base='chimera', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'characterStrengthModifier': 8.0, 'characterConstitutionModifier': 6.0,
                    'defensiveFire': 18.0}),
        # China Telkine Ormenos - cold+life caster. Reassert a VALID controller:
        # the base soul shipped a dangling ormenos_atenemy_onattack controller;
        # ormenos_energyblast is an on-attack projectile, so _AC_ON_ATTACK fits.
        dict(base='ormenos', ctrl=C_ATK, aug1=(_AUG_CHAINLIGHTNING, 3), aug2=(_AUG_DEATHCHILL, 3),
             stats={'offensiveColdMin': 25.0, 'offensiveColdMax': 42.0,
                    'offensiveLifeMin': 20.0, 'offensiveLifeMax': 34.0,
                    'offensiveSlowColdMin': 20.0, 'offensiveSlowColdDurationMin': 3.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 10.0,
                    'characterSpellCastSpeedModifier': 18, 'defensiveCold': 20.0}),
        # Yaoguai - fire + burn + phys
        dict(base='yaoguai', ctrl=C_ATK, aug1=(_AUG_FIREENCHANT, 3), aug2=(_AUG_BATTLERAGE, 3),
             stats={'offensiveFireMin': 30.0, 'offensiveFireMax': 50.0, 'offensiveFireModifier': 25,
                    'offensiveSlowBurnMin': 20.0, 'offensiveSlowBurnDurationMin': 3.0,
                    'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'characterStrengthModifier': 8.0, 'characterIntelligenceModifier': 6.0,
                    'defensiveFire': 22.0}),
        # Dragon Liche - cold + freeze + resist-shred, pet-steal flavor
        dict(base='dragonliche', ctrl=None, aug1=(_AUG_COLDAURA, 3), aug2=(_AUG_DEATHCHILL, 3),
             stats={'offensiveColdMin': 35.0, 'offensiveColdMax': 55.0, 'offensiveColdModifier': 25,
                    'offensiveFreezeMin': 0.5, 'offensiveFreezeMax': 1.5, 'offensiveFreezeChance': 15.0,
                    'offensivePercentCurrentLifeMin': 4.0,
                    'offensiveTotalResistanceReductionAbsoluteMin': 10.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 14.0,
                    'defensiveCold': 25.0}),
        # Gargantuan Yeti - cold + freeze
        dict(base='gargantuanyeti', ctrl=None, aug1=(_AUG_COLDAURA, 3), aug2=None,
             stats={'offensiveColdMin': 30.0, 'offensiveColdMax': 50.0, 'offensiveColdModifier': 25,
                    'offensiveFreezeMin': 0.5, 'offensiveFreezeMax': 1.5, 'offensiveFreezeChance': 15.0,
                    'characterStrengthModifier': 8.0, 'characterConstitutionModifier': 6.0,
                    'defensiveCold': 28.0}),
        # Euryale - cold+life (heal identity)
        dict(base='euryale', ctrl=None, aug1=None, aug2=(_AUG_DEATHCHILL, 3),
             stats={'offensiveColdMin': 22.0, 'offensiveColdMax': 38.0,
                    'offensiveLifeMin': 18.0, 'offensiveLifeMax': 30.0,
                    'characterIntelligenceModifier': 8.0, 'characterDexterityModifier': 6.0,
                    'characterManaRegenModifier': 20, 'defensiveCold': 20.0}),
        # Medusa - fire + phys, petrify star
        dict(base='medusa', ctrl=C_ATK, aug1=None, aug2=(_AUG_REGROWTH, 3),
             stats={'offensiveFireMin': 22.0, 'offensiveFireMax': 38.0,
                    'offensivePhysicalMin': 18.0, 'offensivePhysicalMax': 30.0,
                    'offensiveFreezeMin': 0.5, 'offensiveFreezeMax': 1.2, 'offensiveFreezeChance': 12.0,
                    'characterIntelligenceModifier': 8.0, 'characterDexterityModifier': 8.0,
                    'defensiveFire': 18.0}),
        # Sstheno - ADD arachne venomspray proc; poison + phys + pierce (spear)
        dict(base='sstheno', add_proc=(_SS_VENOM_SPRAY, C_ATK), aug1=None, aug2=None,
             stats={'offensiveSlowPoisonMin': 30.0, 'offensiveSlowPoisonMax': 50.0,
                    'offensiveSlowPoisonDurationMin': 3.0,
                    'offensivePhysicalMin': 18.0, 'offensivePhysicalMax': 32.0,
                    'offensivePierceMin': 15.0, 'offensivePierceMax': 26.0, 'offensivePierceRatioModifier': 15,
                    'characterStrengthModifier': 6.0, 'characterDexterityModifier': 8.0,
                    'characterOffensiveAbilityModifier': 8.0, 'defensivePoison': 20.0}),
        # Greek Telkine Megalesios - lightning + %life + disruption
        dict(base='megalesios', ctrl=None, aug1=(_AUG_CHAINLIGHTNING, 3), aug2=(_AUG_STORMNIMBUS, 3),
             stats={'offensiveLightningMin': 30.0, 'offensiveLightningMax': 55.0, 'offensiveLightningModifier': 25,
                    'offensiveLifeMin': 15.0, 'offensiveLifeMax': 26.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 20, 'defensiveLightning': 20.0}),
        # Hydra - summon (KEEP), tri-breath flat + tri-elem defense
        dict(base='hydra', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveFireMin': 12.0, 'offensiveFireMax': 22.0,
                    'offensiveColdMin': 12.0, 'offensiveColdMax': 22.0,
                    'offensiveSlowPoisonMin': 15.0, 'offensiveSlowPoisonDurationMin': 3.0,
                    'characterStrengthModifier': 8.0, 'characterConstitutionModifier': 6.0,
                    'defensiveFire': 12.0, 'defensiveCold': 12.0, 'defensivePoison': 12.0}),
        # Manticore - phys+poison quills + pierce + disruption
        dict(base='manticore', ctrl=C_ATK, aug1=(_AUG_STUDYPREY, 3), aug2=(_AUG_ENVENOM, 3),
             stats={'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensiveSlowPoisonMin': 30.0, 'offensiveSlowPoisonMax': 50.0,
                    'offensiveSlowPoisonDurationMin': 3.0,
                    'offensivePierceMin': 20.0, 'offensivePierceMax': 34.0, 'offensivePierceRatioModifier': 15,
                    'characterDexterityModifier': 8.0, 'characterStrengthModifier': 6.0}),
        # Minotaur Lord - ADD earthfury proc; phys + fire + battle-rage speed
        dict(base='minotaurlord', add_proc=(_SS_EARTHFURY_RING, C_ATK), aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0, 'offensivePhysicalModifier': 30,
                    'offensiveFireMin': 15.0, 'offensiveFireMax': 26.0,
                    'characterStrengthModifier': 8.0, 'characterOffensiveAbilityModifier': 8.0,
                    'characterAttackSpeedModifier': 12.0, 'defensivePhysical': 15.0}),
        # Barmanu - cold + stun + phys (blunt)
        dict(base='barmanu', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveColdMin': 25.0, 'offensiveColdMax': 42.0, 'offensiveColdModifier': 22,
                    'offensiveStunMin': 1.0, 'offensiveStunMax': 2.0,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'characterStrengthModifier': 8.0, 'characterOffensiveAbilityModifier': 8.0,
                    'defensiveCold': 22.0}),
        # Necromancer Alastor - ADD lifedrain proc; cold+life + leech
        dict(base='alastor', add_proc=(_SS_LIFE_DRAIN, C_ATK), aug1=None, aug2=None,
             stats={'offensiveColdMin': 20.0, 'offensiveColdMax': 34.0,
                    'offensiveLifeMin': 25.0, 'offensiveLifeMax': 42.0,
                    'offensiveLifeLeechMin': 25.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 18, 'defensiveLife': 20.0}),
        # Sandwraith Lord - phys + pierce (sandblast) + slow + resist-shred
        dict(base='sandwraithlord', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensivePierceMin': 18.0, 'offensivePierceMax': 30.0, 'offensivePierceRatioModifier': 15,
                    'offensiveSlowTotalSpeedMin': 12.0, 'offensiveSlowTotalSpeedDurationMin': 3.0,
                    'offensiveTotalResistanceReductionAbsoluteMin': 10.0,
                    'characterStrengthModifier': 8.0, 'characterOffensiveAbilityModifier': 8.0,
                    'defensivePierce': 18.0}),
        # Scarabaeus - poison spray + %life
        dict(base='scarabaeus', ctrl=C_ATK, aug1=None, aug2=(_AUG_PLAGUE, 3),
             stats={'offensiveSlowPoisonMin': 35.0, 'offensiveSlowPoisonMax': 58.0,
                    'offensiveSlowPoisonDurationMin': 3.0, 'offensivePercentCurrentLifeMin': 4.0,
                    'characterStrengthModifier': 8.0, 'characterConstitutionModifier': 6.0,
                    'defensivePoison': 22.0}),
        # Scorpos King Nehebkau - poison + phys sting + speed
        dict(base='nehebkau', ctrl=C_ATK, aug1=None, aug2=(_AUG_ENVENOM, 3),
             stats={'offensiveSlowPoisonMin': 35.0, 'offensiveSlowPoisonMax': 58.0,
                    'offensiveSlowPoisonDurationMin': 3.0,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'characterStrengthModifier': 6.0, 'characterDexterityModifier': 8.0,
                    'characterTotalSpeedModifier': 8, 'defensivePoison': 20.0}),
        # Spartacentaur Nessus - phys + bleed + endurance
        dict(base='nessus', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensiveSlowBleedingMin': 45.0, 'offensiveSlowBleedingDurationMin': 3.0,
                    'characterStrengthModifier': 8.0, 'defensiveProtection': 20.0,
                    'characterLifeRegenModifier': 20}),
        # Spider Queen Arachne - poison + %life + speed
        dict(base='arachne', ctrl=C_ATK, aug1=None, aug2=(_AUG_PLAGUE, 3),
             stats={'offensiveSlowPoisonMin': 35.0, 'offensiveSlowPoisonMax': 58.0,
                    'offensiveSlowPoisonDurationMin': 3.0, 'offensivePercentCurrentLifeMin': 4.0,
                    'characterDexterityModifier': 8.0, 'characterTotalSpeedModifier': 8,
                    'defensivePoison': 22.0}),
        # Talos - fire + phys (fist) + stun (stomp)
        dict(base='talos', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveFireMin': 25.0, 'offensiveFireMax': 42.0,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'offensiveStunMin': 1.0, 'offensiveStunMax': 2.0,
                    'characterStrengthModifier': 8.0, 'defensiveProtection': 30.0}),
        # Terracotta Mage Bandari - cold+lightning
        dict(base='bandari', ctrl=None, aug1=None, aug2=(_AUG_CHAINLIGHTNING, 3),
             stats={'offensiveColdMin': 20.0, 'offensiveColdMax': 34.0,
                    'offensiveLightningMin': 20.0, 'offensiveLightningMax': 40.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 18, 'defensiveLightning': 20.0}),
        # Titan Typhon (living) - fire meteors + phys + %life. EXACT base 'typhon' only.
        dict(base='typhon', ctrl=None, aug1=(_AUG_FIREENCHANT, 3), aug2=(_AUG_VOLCANICORB, 3),
             stats={'offensiveFireMin': 35.0, 'offensiveFireMax': 58.0, 'offensiveFireModifier': 25,
                    'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensivePercentCurrentLifeMin': 4.0,
                    'characterStrengthModifier': 8.0, 'characterIntelligenceModifier': 8.0,
                    'characterManaModifier': 12.0, 'defensiveFire': 22.0}),
        # Xiao - summon peng (KEEP), lightning-melee flavor, keep glass -life
        dict(base='xiao', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveLightningMin': 15.0, 'offensiveLightningMax': 28.0,
                    'offensivePhysicalMin': 15.0, 'offensivePhysicalMax': 26.0,
                    'characterDexterityModifier': 8.0, 'defensiveLightning': 18.0}),

        # ---- Hero um_ bosses across creature folders ----
        # Grimshell - vitality bolt + %life (necro augs kept)
        dict(base='grimshell', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveLifeMin': 25.0, 'offensiveLifeMax': 42.0,
                    'offensivePercentCurrentLifeMin': 4.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 10.0,
                    'defensiveLife': 18.0}),
        # Dark Satyr Shaman - ADD firefragmentnova proc; fire + mana
        dict(base='darksatyrshaman', add_proc=(_SS_FIRE_NOVA, C_HIT), aug1=None, aug2=(_AUG_VOLCANICORB, 3),
             stats={'offensiveFireMin': 30.0, 'offensiveFireMax': 50.0, 'offensiveFireModifier': 25,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 18, 'defensiveFire': 20.0}),
        # Stormbird Mormo - ADD ringoflightning proc; lightning + dodge
        dict(base='stormbird', add_proc=(_SS_RING_LIGHTNING, C_HIT), aug1=None, aug2=None,
             stats={'offensiveLightningMin': 25.0, 'offensiveLightningMax': 45.0, 'offensiveLightningModifier': 22,
                    'characterDexterityModifier': 8.0, 'characterIntelligenceModifier': 6.0,
                    'characterDodgePercent': 10.0, 'defensiveLightning': 18.0}),
        # Permean - phys+fire (sandspire/breath) + slow (pet-augment kept)
        dict(base='permean', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensiveFireMin': 20.0, 'offensiveFireMax': 34.0,
                    'offensiveSlowTotalSpeedMin': 12.0, 'offensiveSlowTotalSpeedDurationMin': 3.0,
                    'characterStrengthModifier': 8.0, 'defensiveFire': 18.0}),
        # Kaublasia - ADD firefragmentnova; fire + phys (bow/fire theme kept)
        dict(base='kaublasia', add_proc=(_SS_FIRE_NOVA, C_HIT), aug1=None, aug2=None,
             stats={'offensiveFireMin': 25.0, 'offensiveFireMax': 42.0, 'offensiveFireModifier': 22,
                    'offensivePhysicalMin': 18.0, 'offensivePhysicalMax': 30.0,
                    'characterDexterityModifier': 8.0, 'characterDefensiveAbilityModifier': 8.0,
                    'defensiveFire': 20.0}),
        # Phagia - summon (KEEP), maenad sorcery small lightning
        dict(base='phagia', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveLightningMin': 15.0, 'offensiveLightningMax': 28.0,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 10.0,
                    'defensiveLightning': 15.0}),
        # Maenad Sorceress (phagia's variant soul) - lightning caster
        dict(base='maenadsorceress', ctrl=None, aug1=None, aug2=(_AUG_STORMNIMBUS, 3),
             stats={'offensiveLightningMin': 20.0, 'offensiveLightningMax': 40.0, 'offensiveLightningModifier': 22,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 18, 'defensiveLightning': 18.0}),
        # Uber Limos - cold + freeze (glacial) + phys
        dict(base='uber', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveColdMin': 30.0, 'offensiveColdMax': 50.0, 'offensiveColdModifier': 25,
                    'offensiveFreezeMin': 0.5, 'offensiveFreezeMax': 1.5, 'offensiveFreezeChance': 15.0,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'characterStrengthModifier': 6.0, 'characterIntelligenceModifier': 6.0,
                    'defensiveCold': 28.0}),
        # Syrinx - lightning/void + %life (nymph-summon aug kept)
        dict(base='syrinx', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveLightningMin': 22.0, 'offensiveLightningMax': 40.0,
                    'offensiveLifeMin': 18.0, 'offensiveLifeMax': 30.0,
                    'offensivePercentCurrentLifeMin': 4.0,
                    'characterDexterityModifier': 8.0, 'characterIntelligenceModifier': 6.0,
                    'defensiveLightning': 18.0}),
        # Wheedletongue - ADD arachne venomspray; poison + phys + deathchill
        dict(base='wheedletongue', add_proc=(_SS_VENOM_SPRAY, C_ATK), aug1=None, aug2=None,
             stats={'offensiveSlowPoisonMin': 30.0, 'offensiveSlowPoisonMax': 50.0,
                    'offensiveSlowPoisonDurationMin': 3.0,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'characterDexterityModifier': 8.0, 'defensivePoison': 20.0}),
        # Palai - fire + phys (firebreath/nova) + fire retaliation
        dict(base='palai', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveFireMin': 30.0, 'offensiveFireMax': 50.0, 'offensiveFireModifier': 25,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'retaliationFireMin': 20.0, 'retaliationFireMax': 35.0,
                    'characterStrengthModifier': 6.0, 'characterIntelligenceModifier': 6.0,
                    'defensiveFire': 22.0}),
        # Xaiweng (xeiwang_soul): ENTRY REMOVED (build30 F1, vet-proven bug). The
        # soul is now the D8 summon-the-boss soul (itemSkillLevel 1/2/3 tier-selects
        # the pet); this Table-B entry ran AFTER _apply_d8_d9_summon_souls and its
        # PROC_LV rescale stomped the levels to 4/6/8 (> skillMaxLevel 3 -> every
        # tier clamped to the same pet). The systemic SpawnPet guard in the apply
        # loop below protects the whole class; the entry itself is retired.
        # Black Widow Arachne's Shame (arachnesshame) - poison + web-slow + %life
        dict(base='arachnesshame', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveSlowPoisonMin': 35.0, 'offensiveSlowPoisonMax': 58.0,
                    'offensiveSlowPoisonDurationMin': 3.0, 'offensivePercentCurrentLifeMin': 4.0,
                    'characterDexterityModifier': 8.0, 'defensivePoison': 22.0}),
        # Melalos - summon zombiesoldier (KEEP), plague/rot small poison-vitality (dark-cov/plague kept)
        dict(base='melalos', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveSlowPoisonMin': 25.0, 'offensiveSlowPoisonMax': 42.0,
                    'offensiveSlowPoisonDurationMin': 3.0,
                    'offensiveLifeMin': 15.0, 'offensiveLifeMax': 26.0,
                    'characterIntelligenceModifier': 8.0, 'defensivePoison': 18.0}),
        # Hades main (hades_soul) - shadow phys + life + resist-shred (ternion/bladehoning kept)
        dict(base='hades', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0,
                    'offensiveLifeMin': 25.0, 'offensiveLifeMax': 42.0,
                    'offensiveTotalResistanceReductionAbsoluteMin': 10.0,
                    'characterStrengthModifier': 8.0, 'characterIntelligenceModifier': 8.0,
                    'characterLifeModifier': 10.0, 'defensiveLife': 20.0}),
        # Aktaios - fire nova + mana (volcanic-orb augs kept)
        dict(base='aktaios', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveFireMin': 30.0, 'offensiveFireMax': 50.0, 'offensiveFireModifier': 25,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 18, 'defensiveFire': 20.0}),
        # Graeae sisters (3-soul lightning set) - built together
        dict(base='deino', ctrl=C_HIT, aug1=(_AUG_STORMNIMBUS, 3), aug2=(_AUG_CHAINLIGHTNING, 3),
             stats={'offensiveLightningMin': 30.0, 'offensiveLightningMax': 55.0, 'offensiveLightningModifier': 25,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 20, 'defensiveLightning': 20.0,
                    'characterStrengthModifier': -4.0}),
        dict(base='enyo', ctrl=C_HIT, aug1=(_AUG_STORMNIMBUS, 3), aug2=(_AUG_CHAINLIGHTNING, 3),
             stats={'offensiveLightningMin': 30.0, 'offensiveLightningMax': 55.0, 'offensiveLightningModifier': 25,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 20, 'defensiveLightning': 20.0,
                    'characterStrengthModifier': -4.0}),
        dict(base='pemphredo', ctrl=C_HIT, aug1=(_AUG_STORMNIMBUS, 3), aug2=(_AUG_CHAINLIGHTNING, 3),
             stats={'offensiveLightningMin': 30.0, 'offensiveLightningMax': 55.0, 'offensiveLightningModifier': 25,
                    'characterIntelligenceModifier': 8.0, 'characterManaModifier': 12.0,
                    'characterSpellCastSpeedModifier': 20, 'defensiveLightning': 20.0,
                    'characterStrengthModifier': -4.0}),
        # Charon Form2 - fire+phys (geyser/swoop) + mana
        dict(base='charon', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveFireMin': 30.0, 'offensiveFireMax': 50.0,
                    'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'characterIntelligenceModifier': 6.0, 'characterStrengthModifier': 6.0,
                    'characterManaModifier': 10.0, 'defensiveFire': 18.0}),
        # Cerberus - poison/acid breath + phys bite + roar-slow
        dict(base='cerberus', ctrl=None, aug1=None, aug2=None,
             stats={'offensiveSlowPoisonMin': 30.0, 'offensiveSlowPoisonMax': 50.0,
                    'offensiveSlowPoisonDurationMin': 3.0,
                    'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensiveSlowTotalSpeedMin': 12.0, 'offensiveSlowTotalSpeedDurationMin': 3.0,
                    'characterStrengthModifier': 8.0, 'characterDexterityModifier': 6.0,
                    'defensivePoison': 20.0}),
        # Skeletal Typhon (undeadtyphon_soul) - phys bone + spirit + trap-debuf (enslave kept)
        dict(base='undeadtyphon', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0,
                    'offensiveLifeMin': 20.0, 'offensiveLifeMax': 34.0,
                    'characterStrengthModifier': 8.0, 'characterIntelligenceModifier': 6.0,
                    'defensiveLife': 18.0}),
        # Antaeus - phys+poison charged + teleport (sword aug kept)
        dict(base='antaeus', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0, 'offensivePhysicalModifier': 25,
                    'offensiveSlowPoisonMin': 25.0, 'offensiveSlowPoisonDurationMin': 3.0,
                    'characterStrengthModifier': 8.0, 'defensivePhysical': 15.0}),
        # Deep Thresher (deeptresher_soul - note the data's single-s spelling) - phys+fire geyser + bleed + protection
        dict(base='deeptresher', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 30.0, 'offensivePhysicalMax': 50.0,
                    'offensiveFireMin': 20.0, 'offensiveFireMax': 34.0,
                    'offensiveSlowBleedingMin': 45.0, 'offensiveSlowBleedingDurationMin': 3.0,
                    'characterStrengthModifier': 8.0, 'characterDefensiveAbilityModifier': 8.0,
                    'defensiveProtection': 30.0}),
        # Meglograi (keres) - phys+life (bat/attack) + blink (heal life-regen)
        dict(base='meglograi', ctrl=None, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 25.0, 'offensivePhysicalMax': 42.0,
                    'offensiveLifeMin': 20.0, 'offensiveLifeMax': 34.0,
                    'characterDexterityModifier': 8.0, 'characterManaModifier': 8.0,
                    'characterLifeRegenModifier': 20}),
        # Blood Crow - ADD firefragmentnova; fire enchant + deathchill + keep glass -life
        dict(base='bloodcrow', add_proc=(_SS_FIRE_NOVA, C_HIT), aug1=None, aug2=None,
             stats={'offensiveFireMin': 25.0, 'offensiveFireMax': 42.0, 'offensiveFireModifier': 22,
                    'characterIntelligenceModifier': 8.0, 'defensiveFire': 20.0}),
        # Elephant Snatcher already in OVERHAULS (elephantsnatcher_soul) - deepen further:
        # (kept lifedrain + battlerage; add life-leech + frost flavor + con)
        dict(base='elephantsnatcher', ctrl=C_ATK, aug1=None, aug2=None,
             stats={'offensivePhysicalMin': 20.0, 'offensivePhysicalMax': 34.0,
                    'offensiveLifeMin': 18.0, 'offensiveLifeMax': 30.0, 'offensiveLifeLeechMin': 22.0,
                    'offensiveColdMin': 12.0, 'offensiveColdMax': 20.0,
                    'characterStrengthModifier': 6.0, 'characterConstitutionModifier': 6.0,
                    'defensiveLife': 15.0}),
    ]

    def scaled(val, mult):
        if isinstance(val, float):
            return round(val * mult, 1)
        if isinstance(val, int):
            return int(round(val * mult))
        return val

    DIFF_MULT = {'n': 1.0, 'e': 1.4, 'l': 1.9}
    PROC_LV = {'n': 4, 'e': 6, 'l': 8}
    AUG_OFF = {'n': 0, 'e': 1, 'l': 2}

    total = 0
    touched_bases = []
    for spec in SPECS:
        base = spec['base']
        add_proc = spec.get('add_proc')
        ctrl = spec.get('ctrl')
        aug1 = spec.get('aug1')
        aug2 = spec.get('aug2')
        base_stats = spec['stats']
        base_hits = 0
        for name in list(db.record_names()):
            nl = name.replace('/', '\\').lower()
            if 'equipmentring' not in nl or '\\soul\\' not in nl:
                continue
            if 'test' in nl or 'template' in nl:
                continue
            # exact basename match on the tail
            matched_diff = None
            for diff in ('n', 'e', 'l'):
                if nl.endswith(f'\\{base}_soul_{diff}.dbr'):
                    matched_diff = diff
                    break
            if matched_diff is None:
                continue
            diff = matched_diff
            fields = {}
            # ── F1 SYSTEMIC GUARD (build30, vet-proven): NEVER rescale/replace
            #    the proc of a summon-the-boss soul. On those souls itemSkillLevel
            #    IS the pet-tier selector (1/2/3, hard-coupled to the summon's
            #    skillMaxLevel=3); PROC_LV {4,6,8} clamps every tier to the same
            #    pet (the D8 xeiwang bug). Stats/augs below still apply. ──
            cur_skill = db.get_field_value(name, 'itemSkillName')
            skill_cls = None
            if cur_skill:
                sk_rec = _find_record(db, cur_skill)
                if sk_rec:
                    skill_cls = db.get_field_value(sk_rec, 'Class')
            is_summon_soul = bool(skill_cls) and str(skill_cls).startswith('Skill_SpawnPet')
            # proc: KEEP existing + rescale level + reassert controller; or ADD
            if add_proc and not is_summon_soul:
                fields['itemSkillName'] = (S, add_proc[0])
                fields['itemSkillLevel'] = (I, PROC_LV[diff])
                fields['itemSkillAutoController'] = (S, add_proc[1])
            elif not add_proc and not is_summon_soul:
                # only rescale level if the soul actually has a proc
                if cur_skill:
                    fields['itemSkillLevel'] = (I, PROC_LV[diff])
                    if ctrl:
                        fields['itemSkillAutoController'] = (S, ctrl)
            elif is_summon_soul:
                print(f"    F1 guard: {name.rsplit(chr(92), 1)[-1]} grants a "
                      f"{skill_cls} summon - proc level/controller left alone")
            if aug1:
                fields['augmentSkillName1'] = (S, aug1[0])
                fields['augmentSkillLevel1'] = (I, aug1[1] + AUG_OFF[diff])
            if aug2:
                fields['augmentSkillName2'] = (S, aug2[0])
                fields['augmentSkillLevel2'] = (I, aug2[1] + AUG_OFF[diff])
            mult = DIFF_MULT[diff]
            for fname, val in base_stats.items():
                sval = scaled(val, mult) if fname in _SCALE_FIELDS else val
                dtype = F if isinstance(sval, float) else I
                fields[fname] = (dtype, sval)
            _set_soul_fields(db, name, fields)
            total += 1
            base_hits += 1
        if base_hits:
            touched_bases.append(f'{base}({base_hits})')
        else:
            print(f"    WARNING: completion base '{base}' matched 0 records")
    print(f"  Table B completion: {total} soul records deepened across {len(touched_bases)} bases")
    print(f"    bases: {', '.join(touched_bases)}")
    return total


# ══════════════════════════════════════════════════════════════════════════
#  BLOOD TOXEUS wave (docs/BLOOD_TOXEUS_DESIGN.md)
#  Display name (Will 2026-07-07): "Toxeus the Murderer, Devourer of Blood"
#  (tagMonsterHemorrheus). "Hemorrheus" below is the internal build-time codename
#  only - the record path (um_bloodtoxeus_99), tag KEYS, function names, and this
#  codename are engine/code identity and stay; only the display-string VALUES were
#  renamed (see the tags block). A crimson Toxeus-revenant superboss + his Blood
#  Boil kit + the Crimson Verdict legendary bleed set + his soul + loot. DB side
#  only; the map spawn (proxy injection into new_secretdoor_transitionhallway) is
#  a separate lane.
# ══════════════════════════════════════════════════════════════════════════

# ── Verified record paths (all DB-confirmed present in the built .arz) ──────
_BT_MONSTER = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
_BT_DONOR_MONSTER = r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr'  # SP Toxeus (crimson revenant kin)
_BT_PROXY = r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr'
_BT_POOL = r'records\drxmap\proxy\pools\q_bloodtoxeus_lone.dbr'
_BT_DONOR_PROXY = r'records\drxmap\proxy\q_leinth_lone.dbr'
_BT_DONOR_POOL = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
# NEW no-cap boss limits file for Hemorrheus (collision-checked free). The donor
# proxy carries difficultyLimitsFile=limit_area002 whose player-level windows
# (N[23-26] E[38-51] L[60-65]) top out BELOW Hemorrheus's charLevel [40,68,100]
# on every difficulty, so the proxy's difficulty clamp would scale him DOWN toward
# those windows. limit_area002 is an area-TRASH limit; a lone superboss must carry
# a boss/no-cap limit (the base game gives its bosses herolimit_all N/E/L[1-75] or
# bosslimit_all). Hemorrheus is the single highest-level monster in the game
# (L=100), above EVERY shipped limit file's max (75), so we author a fresh no-cap
# file whose window CONTAINS [40,68,100] on all three modes (mirrors herolimit_all's
# ProxyLimits.tpl shape). See the eligibility math in docs/BLOOD_TOXEUS_DESIGN.md.
_BT_DONOR_LIMIT = r'records\proxies boss\herolimit_all.dbr'   # N/E/L [1..75] no-cap shape donor
_BT_LIMIT = r'records\proxies orient\limit_bloodtoxeus.dbr'   # NEW: window contains [40,68,100]
# D7 (Will 2026-07-09): the summon-the-boss pets + the 2nd (parchment, 50%) proxy.
_BT_PET_PATHS = [r'records\skills\soulskills\pets\bloodtoxeus_1.dbr',
                 r'records\skills\soulskills\pets\bloodtoxeus_2.dbr',
                 r'records\skills\soulskills\pets\bloodtoxeus_3.dbr']
_BT_PROXY_50 = r'records\drxmap\proxy\q_bloodtoxeus_lone_50.dbr'  # parchment @ chanceToRun=50

# Blood-demon champions + exploding blood sprites (the phase adds) - all EXIST.
_BT_BLOODDEMON = [
    r'records\drxcreatures\blooddemon\b_med_blooddemon_30.dbr',
    r'records\drxcreatures\blooddemon\b_med_blooddemon_31.dbr',
    r'records\drxcreatures\blooddemon\b_med_blooddemon_32.dbr',
]
_BT_LILDUDE_SUMMON_DONOR = r'records\drxmap\pitsprites\t1_skill_pitspawner_summonlildude_02.dbr'  # shared donor
# B-TOXEUS-2 (build29): the summon skill is the DONOR again, NOT a clone. The
# build28 recolor cloned it to bloodtoxeus_summonlildude.dbr and ADDED
# charFxPakSelfNames to it, but (a) the donor never carried the green pak in the
# first place (the recolor premise was wrong for this skill - byte-verified vs
# build27), and (b) NO Skill_SpawnPet*/Skill_SpawnPetMonster record in the base
# game OR build27 carries charFxPakSelfNames at all (zero-precedent field on the
# class = prime loadability suspect for the build28 boss no-spawn regression,
# B-TOXEUS-2). Reverting to the donor restores exact build27 bytes on the boss's
# skillName9/specialAttack5SkillName.
_BT_LILDUDE_SUMMON = _BT_LILDUDE_SUMMON_DONOR

# Kit skills (all EXIST, classes DB-verified against the design doc §2).
_BT_SK_BLOODBOIL      = r'records\skills\soulskills\melinoe_bloodboil.dbr'                       # Skill_AttackRadius (signature nova)
_BT_SK_BLADESTORM     = r'records\skills\monster skills\attack_radius\toxeus_bladestorm.dbr'      # Skill_AttackProjectileRing
_BT_SK_ENVENOM_DONOR  = r'records\skills\monster skills\buff_self\toxeus_envenomweapon.dbr'       # shared donor (Athens GREEN poison shroud)
_BT_SK_ENVENOM        = r'records\skills\monster skills\buff_self\bloodtoxeus_envenomweapon.dbr'  # NEW blood-recolored variant (B-TOXEUS-1)
# Blood-red character-FX pak replacing the green poison shroud (B-TOXEUS-1). Primary =
# the blood-witch Leinth persistent boss aura (same cult family, red). Documented
# alternatives for Will's eye: bloodboil_charfxpak (his signature Blood Boil FX),
# charfxpak_disciple_aura / charfxpak_seductress_aura (other blood-cult auras).
_BT_BLOOD_CHARFXPAK   = r'records\drxcreatures\bloodwitch\skills\skilleffects\charfxpak_leinth_aura.dbr'
_BT_SK_LIFEDRAIN      = r'records\skills\spirit\lifedrain.dbr'                                    # Skill_AttackSpellChaos (drinks it)
_BT_SK_FLASHPOWDER    = r'records\skills\stealth\flashpowder.dbr'                                 # Skill_AttackRadius (blink)
_BT_SK_LETHALSTRIKE   = r'records\skills\stealth\lethalstrike.dbr'                                # Skill_AttackWeapon
_BT_SK_MORTALWOUND    = r'records\skills\stealth\lethalstrike_mortalwound.dbr'                    # Skill_Modifier
_BT_SK_OPENWOUND      = r'records\skills\stealth\openwound.dbr'                                   # Skill_Passive (bleed-on-crit)
_BT_SK_HEROSCALING    = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'           # Skill_Passive
_BT_SK_TOXEUSPASSIVE  = r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'  # Skill_Passive
_BT_SK_ARMORPASSIVE   = r'records\skills\monster skills\defense\armor_passive.dbr'                # Skill_Passive
_BT_SK_BOSSIMMUNITY   = r'records\skills\boss skills\boss_conversionimmunity.dbr'                 # Skill_Passive
_BT_SK_BLEEDWALL      = r'records\drxcreatures\bloodwitch\skills\zpassive_resists_bleedvitleechconvert_x10plvl.dbr'  # Skill_Passive (his bleed wall)
_BT_SK_ATTACKSKILL    = r'records\skills\monster skills\attack_melee\toxeus_attackskill.dbr'      # base melee attack

# Soul augments (verified real Skill_Modifier records; the dangling variants are avoided).
_BT_AUG_OPENWOUND = r'records\skills\stealth\drxopenwound.dbr'                       # Skill_Modifier (Open Wound - the bleed augment)
_BT_AUG_RAVAGES   = r'records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr'     # Skill_Modifier (real Ravages of Time)

# Crimson Verdict set + item paths (all collision-free).
_BT_SET = r'records\item\sets\svc_crimsonverdict.dbr'
_BT_ITEM_BASES = {  # (slot key) -> per-tier derive-from base (EXISTS, correct Class)
    'wpn': {t: rf'records\xpack\item\equipmentweapons\sword\mi_{t}_melinoe.dbr' for t in 'nel'},
    'hlm': {t: rf'records\xpack\item\equipmentarmor\helm\mi_{t}_melinoemage.dbr' for t in 'nel'},
    'tor': {t: rf'records\xpack\item\equipmentarmor\torso\mi_{t}_melinoemage.dbr' for t in 'nel'},
    'arm': {t: rf'records\xpack\item\equipmentarmor\armband\mi_{t}_melinoemage.dbr' for t in 'nel'},
}
_BT_ITEM_DEST = {  # (slot key) -> per-tier NEW item path
    'wpn': {t: rf'records\item\equipmentweapon\sword\svc_{t}_veinrender.dbr' for t in 'nel'},
    'hlm': {t: rf'records\item\equipmenthelm\svc_{t}_crimsonverdict.dbr' for t in 'nel'},
    'tor': {t: rf'records\item\equipmentarmor\svc_{t}_crimsonverdict.dbr' for t in 'nel'},
    'arm': {t: rf'records\item\equipmentarmband\svc_{t}_crimsonverdict.dbr' for t in 'nel'},
}
_BT_ITEM_NAMETAG = {
    'wpn': 'tagSVCwpnVeinRender', 'hlm': 'tagSVChlmCrimsonVerdict',
    'tor': 'tagSVCtorCrimsonVerdict', 'arm': 'tagSVCarmCrimsonVerdict',
}
_BT_ITEM_CLASS = {'n': 'Rare', 'e': 'Epic', 'l': 'Legendary'}
_BT_ITEM_LEVEL = {'n': 40, 'e': 68, 'l': 95}  # L=95 (endgame, per doc); lr = itemLevel - 5

# Loot tables (per-tier; monster loot fields are [n,e,l] arrays).
_BT_LOOT_GUAR = {t: rf'records\item\loottables\svc\crimsonverdict_guaranteed_{t}.dbr' for t in 'nel'}
_BT_LOOT_BLEED = {t: rf'records\item\loottables\svc\bleed_affix_high_{t}.dbr' for t in 'nel'}
# High-bleed unique weapons per tier to seed the bleed-affix FixedWeight table (all EXIST, verified bleed>0).
_BT_BLEED_SRC = {
    'n': [r"records\item\equipmentweapon\bow\u_n_tendonripper.dbr",
          r"records\equipmentweapon\axe\u_n_butcher'sbride.dbr",
          r'records\equipmentweapon\axe\mi_n_tigermanchampion.dbr'],
    'e': [r'records\equipmentweapon\axe\u_e_fleshreaver.dbr',
          r'records\equipmentweapon\axe\u_e_ageaxe.dbr',
          r'records\equipmentweapon\axe\mi_e_tigermanchampion.dbr'],
    'l': [r"records\item\equipmentweapon\bow\u_l_nemesis'recurve.dbr",
          r"records\equipmentweapon\axe\u_l_cerberus'bite.dbr",
          r'records\equipmentweapon\axe\mi_l_tigermanchampion.dbr'],
}


def _create_blood_toxeus_monster(db):
    """Hemorrheus, the Red Verdict - the crimson Toxeus superboss (§7).

    Clone um_toxeus_99 (SP Toxeus, the crimson-revenant kin) so mesh/texture/
    animation all carry over correct, then override level/HP/attributes/resists
    and REPLACE the SP Dream kit with the Blood Boil hemorrhage kit (§2). One
    record with charLevel [40,68,100] (the um_toxeus_21 array style). NOT a pet
    (Monster.tpl), so the Pet.tpl crash rule does not apply. No explicit dtype on
    cloned fields (crash rule): set_field keeps each existing field's dtype.
    """
    if not db.has_record(_BT_DONOR_MONSTER):
        print("  BLOOD TOXEUS: WARNING donor um_toxeus_99 missing; monster skipped")
        return None
    db.clone_record(_BT_DONOR_MONSTER, _BT_MONSTER)
    M = _BT_MONSTER

    # ── Identity + power baseline (§7). No dtype -> preserve each field's type. ──
    db.set_field(M, 'description', 'tagMonsterHemorrheus')
    db.set_field(M, 'monsterClassification', 'Boss')      # hidden end-of-area guardian
    db.set_field(M, 'charLevel', [40, 68, 100])            # existing INT array -> INT
    db.set_field(M, 'characterLife', [13000.0, 18000.0, 24000.0])  # existing FLOAT array -> FLOAT
    db.set_field(M, 'characterStrength', 480.0)
    db.set_field(M, 'characterDexterity', 660.0)
    db.set_field(M, 'characterIntelligence', 420.0)
    db.set_field(M, 'characterLifeRegen', 10.0)           # blood-drinker
    db.set_field(M, 'handHitDamageMin', 60.0)             # bigger blades
    db.set_field(M, 'handHitDamageMax', 120.0)
    db.set_field(M, 'scale', 2.1)                          # visibly the bigger, redder Toxeus
    db.set_field(M, 'actorHeight', 2.0)
    # ── VISUAL: "the GREEN Athens Toxeus, but RED" (Will's directive #2). ──────
    # The green Athens Toxeus (um_toxeus_21) is DB-verified to use mesh
    # RevenantPoison.msh + baseTexture newskeleton_grean.tex. To read as the SAME
    # boss but red, use the IDENTICAL Athens mesh (RevenantPoison.msh) and the
    # crimson SIBLING skin from the SAME newskeleton_* family (newskeleton_crimson.tex).
    # Both resolve in the shipped Creatures.arc; the newskeleton_* skins are a
    # shared, mesh-independent skin set (crimson already rides revenantfire/storm/
    # goldenskeleton/skeletonrumorboss in the shipped DB), so crimson on the poison
    # rig is engine-valid and renders red. (The donor um_toxeus_99 SP variant uses
    # revenantstorm.msh, a DIFFERENT rig from the Athens boss Will pointed at; the
    # clone brought revenantstorm across, so we override it back to the Athens mesh.)
    db.set_field(M, 'mesh', r'Creatures\Monster\Skeleton\RevenantPoison.msh')
    db.set_field(M, 'baseTexture', r'Creatures\monster\skeleton\newskeleton_crimson.tex')

    # ── Resistance wall (§7): pierce 70, poison 80 (bleed identity, not green
    #    Toxeus), life 100, and his SIGNATURE bleed resist 80 (donor has none). ──
    db.set_field(M, 'defensivePierce', 70.0)
    db.set_field(M, 'defensivePoison', 80.0)
    db.set_field(M, 'defensiveLife', 100.0)
    db.set_field(M, 'defensiveBleeding', 80.0)            # NEW field -> auto FLOAT (his wall)

    # ── Blood kit: overwrite the donor's 17 SP-Dream skill slots with the
    #    hemorrhage kit (§2.1 + §2.3) + the exploding-blood-sprite summon
    #    (§2.2B). All strings -> existing STRING slots keep type. The summon is
    #    ALSO wired into the specialAttack rotation below so the AI actually
    #    casts it during the fight (monsters fire from specialAttack*/controller,
    #    not from an item-autocast controller, so no fake skillController field). ──
    kit = [
        (_BT_SK_BLOODBOIL,     [8, 12, 16]),   # signature nova, tier-scaled
        (_BT_SK_BLADESTORM,    [8, 12, 16]),   # bleeding bladestorm
        (_BT_SK_ENVENOM,       1),             # blood-slick blades (toggle)
        (_BT_SK_LIFEDRAIN,     [6, 10, 14]),   # ranged life drain
        (_BT_SK_FLASHPOWDER,   [6, 10, 14]),   # assassin blink
        (_BT_SK_LETHALSTRIKE,  [6, 10, 14]),   # crit strike
        (_BT_SK_MORTALWOUND,   [4, 6, 8]),     # crit modifier
        (_BT_SK_OPENWOUND,     [4, 6, 8]),     # bleed-on-crit passive
        (_BT_LILDUDE_SUMMON,   [1, 2, 3]),     # §2.2B exploding-blood-sprite burst
        (_BT_SK_HEROSCALING,   [1, 2, 3]),     # level scaling
        (_BT_SK_TOXEUSPASSIVE, [1, 2, 3]),     # Toxeus difficulty passive
        (_BT_SK_ARMORPASSIVE,  [142, 238, 396]),  # armor passive (donor's tier array)
        (_BT_SK_BOSSIMMUNITY,  1),             # convert/taunt/fear immunity bundle
        (_BT_SK_BLEEDWALL,     [1, 2, 3]),     # blood-witch bleed/vit/leech resist-per-level
        (_BT_SK_ATTACKSKILL,   1),             # base melee attack
    ]
    for idx, (path, lvl) in enumerate(kit, start=1):
        db.set_field(M, f'skillName{idx}', path)
        db.set_field(M, f'skillLevel{idx}', lvl)
    # Blank the donor's unused trailing slots (kit fills 1..15; donor had 17).
    for i in range(len(kit) + 1, 18):
        db.set_field(M, f'skillName{i}', '')

    # ── specialAttack* rotation: point the AI's cast slots at the blood skills
    #    (donor pointed them at Dream skills). The donor's per-slot Chance/Delay/
    #    Range/Timeout carry over via clone, so these fire. Slot 5 = the sprite
    #    burst so the exploding-blood adds actually appear mid-fight. ──
    db.set_field(M, 'specialAttackSkillName', _BT_SK_BLOODBOIL)     # signature primary
    db.set_field(M, 'specialAttack2SkillName', _BT_SK_FLASHPOWDER)
    db.set_field(M, 'specialAttack3SkillName', _BT_SK_BLADESTORM)
    db.set_field(M, 'specialAttack4SkillName', _BT_SK_LIFEDRAIN)
    db.set_field(M, 'specialAttack5SkillName', _BT_LILDUDE_SUMMON)  # exploding-sprite phase burst
    db.set_field(M, 'attackSkillName', _BT_SK_ATTACKSKILL)
    db.set_field(M, 'initialSkillName', _BT_SK_ENVENOM)             # buff up on spawn

    db.set_field(M, 'dropItems', 1)
    db._modified.add(M)
    print(f"  Hemorrheus monster created: Lv[40,68,100] HP[13000,18000,24000], blood kit + bleed wall")
    return M


def _create_blood_toxeus_proxy(db):
    """Placed-proxy + pool for Hemorrheus (§5.2). Mirror q_leinth_lone's STRUCTURE
    with two deliberate preview-only overrides (mesh->the Athens Toxeus rig, scale->2.1),
    a NO-CAP boss limits file (so his charLevel [40,68,100] is not clamped down by the
    donor's limit_area002 area-trash window), and the CORRECT boss+adds pool math.

    ── ROOT CAUSE of the "boss never spawned, only blood demons" bug (Will, TESTHUB,
       2026-07-07), DB-proven, not the limit-bracket hypothesis ──
    The prior code set the pool to spawnMin=spawnMax=1 + championChance=100 + championMin=1.
    In the TQ proxy resolver, championChance is the PER-SPAWN probability that a spawn
    slot is filled by a CHAMPION (drawn from nameChampionN = blood demons) INSTEAD of a
    main-pool monster (nameN = Hemorrheus). With ONE spawn slot and a 100% champion chance
    (and championMin=1 forcing >=1 champion), the single slot was ALWAYS converted to a
    blood-demon champion and Hemorrheus (the main) got ZERO slots -> he never materialized,
    while the blood demons Will saw ARE that converted slot. DB evidence: ALL 30 base-game
    boss pools (bosspool_02_nessus .. bosspool_24_hydra) use championChance=0.1 + spawnMax=1
    so the boss (the main) always spawns; q_bloodtoxeus_lone was the ONLY Boss-main pool in
    the game set to championChance=100. (The limit_area002 bracket is NOT the spawn blocker:
    Hades charLevel[57,71,80] via bosslimit_all[max 75], Murder Bunny L99, the high priest
    c_disciple_miniboss[39,56,71] via THIS SAME limit_area002, and 120 monsters with L>75 all
    spawn - exceeding the limit window SCALES a monster, it does not filter it out.)

    ── THE FIX (base-game-proven "boss + guaranteed champion escort" pattern) ──
    Copy the shipped xsq22_wave2_odontotyrranusandmelinoe_pool / xsq17_keres_escortparty_pool
    recipe: spawnMin=spawnMax=3, championChance=100, championMin=2, championMax=2. The
    championMax=2 cap leaves 3-2 = exactly 1 main-pool slot -> exactly 1 Hemorrheus, and
    championMin=2 guarantees exactly 2 blood-demon adds. So EVERY spawn = 1 Hemorrheus + 2
    blood demons, on all three difficulties, at both placements (this proxy record is what
    BOTH the TESTHUB HV01 placement and the canonical secret-area placement inject).
    """
    if not (db.has_record(_BT_DONOR_PROXY) and db.has_record(_BT_DONOR_POOL)):
        print("  BLOOD TOXEUS: WARNING donor q_leinth_lone proxy/pool missing; proxy skipped")
        return None

    # ── No-cap boss limits file (author BEFORE the proxy so it resolves) ──
    # herolimit_all is N/E/L [1..75]; Hemorrheus reaches L=100, so widen the upper
    # bound to 110 (> his 100) on every mode. Lower bounds stay at 1 (a lone
    # superboss should be spawnable/at-level for any player who reaches him). This is
    # the "boss/no-cap limits file" the working superboss precedent uses, corrected
    # to actually contain his level so the difficulty clamp never scales him down.
    if db.has_record(_BT_DONOR_LIMIT):
        db.clone_record(_BT_DONOR_LIMIT, _BT_LIMIT)
        L = _BT_LIMIT
        # ProxyLimits equations are STRING fields ("<n> * 1"); keep the donor's
        # STRING dtype (set_field preserves it) - never pass an INT here.
        db.set_field(L, 'minPlayerLevelEquationNormal',    '1 * 1')
        db.set_field(L, 'maxPlayerLevelEquationNormal',    '110 * 1')
        db.set_field(L, 'minPlayerLevelEquationEpic',      '1 * 1')
        db.set_field(L, 'maxPlayerLevelEquationEpic',      '110 * 1')
        db.set_field(L, 'minPlayerLevelEquationLegendary', '1 * 1')
        db.set_field(L, 'maxPlayerLevelEquationLegendary', '110 * 1')
        db._modified.add(L)
        _bt_limit_ref = _BT_LIMIT
    else:
        # Fallback: if the herolimit_all donor is somehow absent, keep the donor
        # proxy's limit_area002 (spawn still works - the fix is the pool math; the
        # limit only affects level scaling). The invariant below will flag it.
        print("  BLOOD TOXEUS: WARNING herolimit_all donor missing; keeping donor limit file")
        _bt_limit_ref = None

    # ── Proxy ──
    db.clone_record(_BT_DONOR_PROXY, _BT_PROXY)
    P = _BT_PROXY
    # Preview silhouette matches the ACTUAL boss rig: the green Athens Toxeus mesh
    # (RevenantPoison.msh), so the map preview reads as the Toxeus he is. (Not the
    # placed map instance - that lives in build_section_surgery INJECT_SPECS, a
    # separate lane; this is only the proxy DB record's preview visual.)
    db.set_field(P, 'mesh', r'Creatures\Monster\Skeleton\RevenantPoison.msh')  # Athens Toxeus preview silhouette
    db.set_field(P, 'scale', 2.1)                                             # Hemorrheus size (donor 4.0)
    db.set_field(P, 'pool1', _BT_POOL)
    db.set_field(P, 'chanceToRun', 100.0)   # D7: chest proxy always guards the stash (explicit)
    # Point at the no-cap boss limits file so his [40,68,100] is never clamped down
    # (donor cloned limit_area002; override it). difficultyEquationFile (difficulty_04)
    # + weight1 + baseTexture (proxyu_boss.tex) + placementExtents (3.5) carry over.
    if _bt_limit_ref:
        db.set_field(P, 'difficultyLimitsFile', _bt_limit_ref)
    db._modified.add(P)

    # ── Pool ── (base-game "boss + guaranteed champion escort" math; see docstring)
    db.clone_record(_BT_DONOR_POOL, _BT_POOL)
    PL = _BT_POOL
    db.set_field(PL, 'FileDescription', 'Hemorrheus (main) + 2 blood-demon champion adds')
    db.set_field(PL, 'name1', _BT_MONSTER)
    db.set_field(PL, 'name2', _BT_MONSTER)
    db.set_field(PL, 'name3', _BT_MONSTER)
    db.set_field(PL, 'nameChampion1', _BT_BLOODDEMON[0])
    db.set_field(PL, 'nameChampion2', _BT_BLOODDEMON[1])
    db.set_field(PL, 'nameChampion3', _BT_BLOODDEMON[2])
    # THE FIX: 3 spawn slots; exactly 2 become blood-demon champions (championMin=Max=2),
    # leaving exactly 1 main-pool slot for Hemorrheus. championChance=100 only decides
    # WHICH slots are champion-eligible; championMax=2 CAPS the count so the boss keeps a
    # slot (proven by xsq22_wave2 / xsq17 / duneraider_03). spawnMin=spawnMax=3.
    db.set_field(PL, 'spawnMin', 3)
    db.set_field(PL, 'spawnMax', 3)
    db.set_field(PL, 'championChance', 100.0)
    db.set_field(PL, 'championMin', 2)
    db.set_field(PL, 'championMax', 2)
    # weightChampion1-3 carry over (34/33/33) = which blood-demon variant; weight1-3 too.
    db._modified.add(PL)
    print(f"  Hemorrheus proxy + pool created (limit=limit_bloodtoxeus [1..110]; "
          f"spawn 1 boss + 2 blood-demon adds via spawn=3/champMin=Max=2/champChance=100)")
    return P


def _create_crimsonverdict_set(db):
    """The Crimson Verdict - a single-tier LEGENDARY 4-piece bleed set (§3.1) +
    12 item records (4 svc_l_* set members with itemSetName; 8 svc_{n,e}_*
    standalone bleed pieces with NO itemSetName). Set-bonus stats are per-count
    arrays [1pc,2pc,3pc,4pc] with idx0=0 (drxset026's [0,75,130,230] pattern).
    Dead fields (skillLifeBonus, set-level defensiveBleeding, defensiveLifeLeech
    on armor) are NOT authored - see the field-validity ledger §8.
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # ── 12 item records (per slot, per tier) ──
    # L stat blocks (§3.2). N ~0.55x, E ~0.78x on the offensive/leech lines; the
    # flat/defensive lines scale gently. Only item-VALID fields (no skillLifeBonus,
    # no defensiveLifeLeech on armor). itemSetName ONLY on the L pieces.
    #
    # dtype discipline (CRASH RULE): these items are CLONED from the melinoe
    # bases, and every stat field below is FLOAT (or absent) on those bases
    # (DB-audited). We therefore write FLOAT values and pass NO explicit dtype -
    # set_field then preserves each existing field's FLOAT type (and auto-infers
    # FLOAT for new fields). Passing an INT dtype onto a base FLOAT field would
    # silently corrupt the value to ~0 in-game (the INT/FLOAT trap in CLAUDE.md).
    def wpn_block(t):
        m = {'n': 0.55, 'e': 0.78, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        return {
            'offensivePhysicalMin': r(95.0), 'offensivePhysicalMax': r(150.0),
            'offensivePhysicalModifier': r(40.0),
            'offensiveSlowBleedingMin': r(180.0), 'offensiveSlowBleedingDurationMin': 3.0,
            'offensiveSlowBleedingModifier': r(60.0),
            'offensiveLifeMin': r(70.0), 'offensiveLifeMax': r(110.0), 'offensiveLifeModifier': r(35.0),
            'offensiveLifeLeechMin': r(45.0),
            'offensivePierceRatioModifier': r(25.0), 'offensivePercentCurrentLifeMin': r(6.0),
            'characterAttackSpeedModifier': r(16.0),
            'characterDexterityModifier': r(12.0), 'characterStrengthModifier': r(8.0),
            'characterLife': r(250.0),   # was skillLifeBonus (skill-only) -> characterLife (item-valid)
        }

    def hlm_block(t):
        m = {'n': 0.55, 'e': 0.78, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        return {
            'characterLife': r(400.0), 'characterLifeModifier': r(12.0),
            'defensiveBleeding': r(40.0), 'defensiveLife': r(25.0),
            'offensiveSlowBleedingModifier': r(30.0), 'offensiveLifeLeechMin': r(20.0),
            'characterOffensiveAbility': r(90.0), 'characterDefensiveAbility': r(60.0),
            'defensivePhysical': r(180.0),
        }

    def tor_block(t):
        m = {'n': 0.55, 'e': 0.78, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        # skillLifeBonus + defensiveLifeLeech dropped (inert on armor); intent carried
        # by characterLife (folded to 850) + defensiveBleeding + bumped defensiveLife.
        return {
            'characterLife': r(850.0), 'characterLifeModifier': r(15.0),
            'defensiveBleeding': r(45.0), 'defensiveLife': r(45.0),
            'defensivePhysical': r(260.0), 'characterLifeRegen': r(12.0),
            'characterDefensiveAbility': r(70.0),
        }

    def arm_block(t):
        m = {'n': 0.55, 'e': 0.78, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        return {
            'offensiveSlowBleedingMin': r(140.0), 'offensiveSlowBleedingDurationMin': 3.0,
            'offensiveSlowBleedingModifier': r(45.0),
            'offensiveLifeLeechMin': r(25.0), 'offensiveLifeModifier': r(25.0),
            'characterAttackSpeedModifier': r(12.0), 'characterOffensiveAbility': r(70.0),
            'defensiveBleeding': r(30.0), 'defensivePhysical': r(140.0),
        }

    blocks = {'wpn': wpn_block, 'hlm': hlm_block, 'tor': tor_block, 'arm': arm_block}
    item_count = 0
    for slot in ('wpn', 'hlm', 'tor', 'arm'):
        for t in 'nel':
            base = _BT_ITEM_BASES[slot][t]
            dest = _BT_ITEM_DEST[slot][t]
            if not db.has_record(base):
                print(f"  BLOOD TOXEUS: WARNING item base missing {base}")
                continue
            db.clone_record(base, dest)   # brings correct mesh/tex/template/base fields
            # Identity: no dtype (itemLevel/levelRequirement are INT on the base ->
            # preserved by the int values; itemNameTag/itemSetName are new STRING
            # slots -> auto STRING; itemClassification is STRING on the base).
            db.set_field(dest, 'itemNameTag', _BT_ITEM_NAMETAG[slot])
            db.set_field(dest, 'itemLevel', _BT_ITEM_LEVEL[t])
            db.set_field(dest, 'levelRequirement', max(1, _BT_ITEM_LEVEL[t] - 5))
            db.set_field(dest, 'itemClassification', _BT_ITEM_CLASS[t])
            if t == 'l':
                db.set_field(dest, 'itemSetName', _BT_SET)  # ONLY the L pieces are set members
            # Over-stat with the (tier-scaled) bespoke block. FLOAT values, no
            # explicit dtype -> preserves base FLOAT type / auto-infers FLOAT (safe).
            for fname, val in blocks[slot](t).items():
                db.set_field(dest, fname, val)
            db._modified.add(dest)
            item_count += 1

    # ── The set record (single-tier L; members = the 4 svc_l_* pieces) ──
    _ensure_record(db, _BT_SET, 'database\\Templates\\ItemSet.tpl')
    db._record_types[_BT_SET] = ''  # real ItemSet records store empty record-type header
    db.set_field(_BT_SET, 'Class', 'ItemSet', S)
    db.set_field(_BT_SET, 'templateName', 'database\\Templates\\ItemSet.tpl', S)
    db.set_field(_BT_SET, 'FileDescription', 'The Crimson Verdict', S)
    db.set_field(_BT_SET, 'setName', 'tagSVCSetCrimsonVerdict', S)
    db.set_field(_BT_SET, 'setMembers', [
        _BT_ITEM_DEST['wpn']['l'], _BT_ITEM_DEST['hlm']['l'],
        _BT_ITEM_DEST['tor']['l'], _BT_ITEM_DEST['arm']['l'],
    ], S)
    # Per-count set BONUS: 4-element arrays [1pc=0, 2pc, 3pc, 4pc]. Every field
    # DB-verified as carried by real ItemSet records (§3.1). NO skillLifeBonus,
    # NO set-level defensiveBleeding.
    set_bonus = {
        'characterLifeModifier':                 [0.0, 6.0, 10.0, 15.0],
        'offensiveSlowBleedingModifier':         [0.0, 25.0, 45.0, 75.0],   # the payoff
        'offensiveSlowBleedingDurationModifier': [0.0, 0.0, 20.0, 40.0],
        'offensiveLifeLeechMin':                 [0.0, 15.0, 25.0, 40.0],
        'offensiveLifeModifier':                 [0.0, 15.0, 25.0, 40.0],
        'characterAttackSpeedModifier':          [0.0, 8.0, 12.0, 18.0],
        'characterLife':                         [0.0, 150.0, 300.0, 600.0],  # was skillLifeBonus -> characterLife
        'retaliationSlowBleedingMin':            [0.0, 0.0, 0.0, 120.0],       # 4pc "bleed back" capstone
        'retaliationSlowBleedingDurationMin':    [0.0, 0.0, 0.0, 3.0],
    }
    for fname, arr in set_bonus.items():
        db.set_field(_BT_SET, fname, arr, F)
    db._modified.add(_BT_SET)
    print(f"  Crimson Verdict set created: single-tier L set + {item_count} item records "
          f"(4 L members + {item_count - 4} N/E standalone)")
    return _BT_SET


def _create_crimsonverdict_loot(db):
    """Loot tables (§3.3): a per-tier guaranteed-set-piece FixedWeight table
    (4 pieces @ weight 100 -> always one) + a per-tier high-bleed FixedWeight
    table (bleed uniques). Cloned in SHAPE from supra_special (FixedWeight);
    NONE of its formulae contents are used. Returns nothing; wiring is on the
    monster (done by the caller / wire step).
    """
    S, I = DATA_TYPE_STRING, DATA_TYPE_INT

    def fixedweight(path, members, desc):
        _ensure_record(db, path, 'Database\\Templates\\LootItemTable_FixedWeight.tpl')
        db._record_types[path] = 'LootItemTable_FixedWeight'  # match real FixedWeight records' header
        db.set_field(path, 'Class', 'LootItemTable_FixedWeight', S)
        db.set_field(path, 'templateName', 'Database\\Templates\\LootItemTable_FixedWeight.tpl', S)
        db.set_field(path, 'FileDescription', desc, S)
        db.set_field(path, 'brokenRandomizerChance', 0.0, DATA_TYPE_FLOAT)
        db.set_field(path, 'prefixRandomizerChance', 0.0, DATA_TYPE_FLOAT)
        db.set_field(path, 'suffixRandomizerChance', 0.0, DATA_TYPE_FLOAT)
        for i, m in enumerate(members, start=1):
            db.set_field(path, f'lootName{i}', m, S)
            db.set_field(path, f'lootWeight{i}', 100, I)
        db._modified.add(path)

    for t in 'nel':
        pieces = [_BT_ITEM_DEST[k][t] for k in ('wpn', 'hlm', 'tor', 'arm')]
        fixedweight(_BT_LOOT_GUAR[t], pieces, f'Crimson Verdict guaranteed piece ({t.upper()})')
        fixedweight(_BT_LOOT_BLEED[t], _BT_BLEED_SRC[t], f'High bleed-affix gear ({t.upper()})')
    print(f"  Crimson Verdict loot: 3 guaranteed-piece + 3 high-bleed FixedWeight tables")


def _create_blood_toxeus_soul(db):
    """{^F}Devourer of Blood Soul (§4; renamed from "Soul of Hemorrhage" per Will
    2026-07-07 - tag KEY tagSVCSoulHemorrhage kept, only the display value changed).
    Blood Boil proc on-hit + Open Wound + real Ravages-of-time augments,
    bleed/vitality/leech suite. Bare _ensure_record via _create_soul (NEVER
    clone_record). Three tiers, {^F} tag, per-tier icon. defensiveLifeLeech is
    VALID here (ring/jewelry record, like the Limos soul).
    """
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    tiers = [
        {'diff': 'n', 'itemLevel': 40, 'stats': {
            **_bmp('n'),
            'itemSkillName': (S, SUMMON_TOXEUS_SKILL), 'itemSkillLevel': (I, 1),  # D7: manual-cast summon-the-boss (N pet)
            'augmentSkillName1': (S, _BT_AUG_OPENWOUND), 'augmentSkillLevel1': (I, 3),
            'augmentSkillName2': (S, _BT_AUG_RAVAGES), 'augmentSkillLevel2': (I, 2),
            'offensiveLifeMin': (F, 45.0), 'offensiveLifeMax': (F, 70.0), 'offensiveLifeModifier': (I, 25),
            'offensiveSlowBleedingMin': (F, 70.0), 'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 35),
            'offensiveLifeLeechMin': (F, 35.0), 'offensivePercentCurrentLifeMin': (F, 4.0),
            'offensivePhysicalMin': (F, 35.0), 'offensivePhysicalMax': (F, 55.0),
            'offensivePhysicalModifier': (I, 20), 'offensivePierceRatioModifier': (I, 15),
            'characterAttackSpeedModifier': (I, 12), 'characterTotalSpeedModifier': (I, 8),
            'characterRunSpeedModifier': (F, 10.0), 'characterDodgePercent': (F, 8.0),
            'characterLifeModifier': (F, 10.0), 'characterStrengthModifier': (F, 6.0),
            'characterDexterityModifier': (F, 8.0),
            'defensiveLife': (F, 18.0), 'defensiveBleeding': (F, 20.0), 'defensiveLifeLeech': (F, 20.0),
        }},
        {'diff': 'e', 'itemLevel': 68, 'stats': {
            **_bmp('e'),
            'itemSkillName': (S, SUMMON_TOXEUS_SKILL), 'itemSkillLevel': (I, 2),  # D7: manual-cast summon-the-boss (E pet)
            'augmentSkillName1': (S, _BT_AUG_OPENWOUND), 'augmentSkillLevel1': (I, 4),
            'augmentSkillName2': (S, _BT_AUG_RAVAGES), 'augmentSkillLevel2': (I, 3),
            'offensiveLifeMin': (F, 65.0), 'offensiveLifeMax': (F, 100.0), 'offensiveLifeModifier': (I, 35),
            'offensiveSlowBleedingMin': (F, 120.0), 'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 50),
            'offensiveLifeLeechMin': (F, 55.0), 'offensivePercentCurrentLifeMin': (F, 6.0),
            'offensivePhysicalMin': (F, 60.0), 'offensivePhysicalMax': (F, 90.0),
            'offensivePhysicalModifier': (I, 28), 'offensivePierceRatioModifier': (I, 20),
            'characterAttackSpeedModifier': (I, 16), 'characterTotalSpeedModifier': (I, 12),
            'characterRunSpeedModifier': (F, 15.0), 'characterDodgePercent': (F, 11.0),
            'characterLifeModifier': (F, 14.0), 'characterStrengthModifier': (F, 8.0),
            'characterDexterityModifier': (F, 11.0),
            'defensiveLife': (F, 26.0), 'defensiveBleeding': (F, 28.0), 'defensiveLifeLeech': (F, 25.0),
        }},
        {'diff': 'l', 'itemLevel': 100, 'stats': {
            **_bmp('l'),
            'itemSkillName': (S, SUMMON_TOXEUS_SKILL), 'itemSkillLevel': (I, 3),  # D7: manual-cast summon-the-boss (L pet)
            'augmentSkillName1': (S, _BT_AUG_OPENWOUND), 'augmentSkillLevel1': (I, 5),
            'augmentSkillName2': (S, _BT_AUG_RAVAGES), 'augmentSkillLevel2': (I, 4),
            'offensiveLifeMin': (F, 95.0), 'offensiveLifeMax': (F, 150.0), 'offensiveLifeModifier': (I, 55),
            'offensiveSlowBleedingMin': (F, 190.0), 'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveSlowBleedingModifier': (I, 75),
            'offensiveLifeLeechMin': (F, 90.0), 'offensivePercentCurrentLifeMin': (F, 8.0),
            'offensivePhysicalMin': (F, 100.0), 'offensivePhysicalMax': (F, 160.0),
            'offensivePhysicalModifier': (I, 40), 'offensivePierceRatioModifier': (I, 25),
            'characterAttackSpeedModifier': (I, 20), 'characterTotalSpeedModifier': (I, 16),
            'characterRunSpeedModifier': (F, 20.0), 'characterDodgePercent': (F, 14.0),
            'characterLifeModifier': (F, 20.0), 'characterStrengthModifier': (F, 12.0),
            'characterDexterityModifier': (F, 14.0), 'characterOffensiveAbilityModifier': (F, 12.0),
            'defensiveLife': (F, 34.0), 'defensiveBleeding': (F, 40.0), 'defensiveLifeLeech': (F, 30.0),
        }},
    ]
    paths = _create_soul(db, 'blood_toxeus', 'tagSVCSoulHemorrhage', tiers, _BT_MONSTER, 25.0)
    print(f"  Toxeus (Devourer of Blood) summon-soul created: {len(paths)} tiers "
          f"(manual-cast summon-the-boss; 25% drop [release])")
    return paths


# ── build36 A1 PET BUILDER OVERHAUL (Will 2026-07-11: "audit all pets for stat
#    issues and gear issues") ───────────────────────────────────────────────
# Registry of every _build_boss_summon (source_path, [pet paths]) family, appended
# by the builder. Consumed by the three new fail-loud pet gates (parity/gear/
# skill-kit). Module-global so the gates need no threading through the orchestrator.
_SUMMON_PET_BUILDS = []

# Slot-appropriate COMMON substitute loot tables for the STRICT gear-mirror. Used
# ONLY when a source equips an \svc\ / \unique\ table in that slot (those spawn a
# pet NAKED - the F2 naked-pet law), so the pet stays source-faithful (same slot
# filled) without the unique-equip failure. All are proven 3-tier [n,e,l] common
# tables that render on the humanoid/skeleton rigs these pets use.
_GEAR_SUBSTITUTE = {
    'RightHand': [r'records\item\loottables\weapons\mastertables\1h_dyn_n03.dbr',
                  r'records\item\loottables\weapons\mastertables\1h_dyn_e03.dbr',
                  r'records\item\loottables\weapons\mastertables\1h_dyn_l03.dbr'],
    'LeftHand':  [r'records\item\loottables\shields\commondynamic\shield_n03.dbr',
                  r'records\item\loottables\shields\commondynamic\shield_e03.dbr',
                  r'records\item\loottables\shields\commondynamic\shield_l03.dbr'],
    'Head':      [r'records\item\loottables\head\commondynamic\helm_n01b.dbr',
                  r'records\item\loottables\head\commondynamic\helm_e01.dbr',
                  r'records\item\loottables\head\commondynamic\helm_l01.dbr'],
    'Torso':     [r'records\item\loottables\torso\commondynamic\melee_n01b.dbr',
                  r'records\item\loottables\torso\commondynamic\melee_e01.dbr',
                  r'records\item\loottables\torso\commondynamic\melee_l01.dbr'],
    'Forearm':   [r'records\item\loottables\arms\commondynamic\armband_n01b.dbr',
                  r'records\item\loottables\arms\commondynamic\armband_e01.dbr',
                  r'records\item\loottables\arms\commondynamic\armband_l01.dbr'],
    'LowerBody': [r'records\item\loottables\legs\commondynamic\greaves_n01b.dbr',
                  r'records\item\loottables\legs\commondynamic\greaves_e01.dbr',
                  r'records\item\loottables\legs\commondynamic\greaves_l01.dbr'],
}
_GEAR_SLOTS = ('RightHand', 'LeftHand', 'Head', 'Torso', 'Forearm', 'LowerBody')

# Pet-AI role slots. Summons fire ONLY from attack/special slots; a summon in a
# buff/init/dying/berserk slot NEVER casts (the Pygmalion "never summons" bug).
_PET_AI_SLOTS = ('attackSkillName', 'specialAttackSkillName', 'specialAttack2SkillName',
                 'specialAttack3SkillName', 'specialAttack4SkillName', 'specialAttack5SkillName')
_PET_SPECIAL_SLOTS = ('specialAttackSkillName', 'specialAttack2SkillName',
                      'specialAttack3SkillName', 'specialAttack4SkillName',
                      'specialAttack5SkillName')
_PET_SRC_KIT_SLOTS = ('specialAttack2SkillName', 'specialAttack3SkillName',
                      'specialAttack4SkillName', 'specialAttack5SkillName')
_PET_NONAI_SLOTS = ('buffSelfSkillName', 'buffSelf2SkillName', 'buffSelf3SkillName',
                    'buffOtherSkillName', 'buffOther2SkillName', 'buffOther3SkillName',
                    'healSkillName', 'initialSkillName', 'dyingSkillName', 'berserkSkillName')
# Lyia archer-clone residue skills the source boss does not itself use.
_LYIA_RESIDUE = ('envenomweapon', 'heartofoak', 'regrowth_lyia', "nature'swrath",
                 'maenadsummon_attack_default')


# Lazy normalized-name cache for _skill_class_of (build36 A1). The gates +
# relocation sweep resolve a Class for ~200 pets x ~16 slots; the bare
# _resolve_record fallback is an O(50k) linear scan per MISS, so cache the
# lowercase-name -> key map and rebuild it only when the record COUNT changes
# (records are only ADDED during the build, never removed -> a count change is
# the sole way the name set grows). Output-identical to _resolve_record.
_SKILL_NAME_CACHE = {'count': -1, 'map': {}}


def _skill_class_of(db, ref):
    """Resolve a skill ref's Class ('Skill_SpawnPet' / 'Skill_SpawnPetMonster' /
    ...); None if the ref does not resolve. Cached name-map (see above): the
    validity check is O(1) (record-table SIZE), so a stable record set (the gate
    phase) gives O(1) lookups instead of _resolve_record's O(50k) scan-on-miss."""
    raw = getattr(db, '_raw_records', None)
    n = len(raw) if raw is not None else None
    if n is None or _SKILL_NAME_CACHE['count'] != n:
        src = raw if raw is not None else db.record_names()
        _SKILL_NAME_CACHE['map'] = {str(x).replace('/', '\\').lower(): x for x in src}
        _SKILL_NAME_CACHE['count'] = n if n is not None else -1
    key = _SKILL_NAME_CACHE['map'].get(str(ref).replace('/', '\\').lower())
    if not key:
        return None
    c = db.get_field_value(key, 'Class')
    return c[0] if isinstance(c, list) else c


def _pet_slot_str(db, path, field):
    v = db.get_field_value(path, field)
    v = v[0] if isinstance(v, list) else v
    return str(v).strip() if v is not None and str(v).strip() else ''


def _free_pet_special_slot(db, path):
    for s in _PET_SPECIAL_SLOTS:
        if not _pet_slot_str(db, path, s):
            return s
    return None


def _source_skill_level(db, source, skill):
    """The level the SOURCE registers `skill` at (its skillLevelK), else 1."""
    ff = db.get_fields(source) or {}
    want = str(skill).replace('/', '\\').lower()
    for k, tf in ff.items():
        base = k.split('###')[0]
        if base.startswith('skillName') and tf.values and \
                str(tf.values[0]).replace('/', '\\').lower() == want:
            try:
                n = int(base[len('skillName'):])
            except ValueError:
                continue
            lv = db.get_field_value(source, f'skillLevel{n}')
            return lv if lv not in (None, '', []) else 1
    return 1


def _register_pet_skill(db, path, skill, level=1):
    """Ensure `skill` sits in some skillNameK/skillLevelK on the pet (registration
    = the per-level index; a role-slot skill with no registration fires at lvl 1)."""
    ff = db.get_fields(path) or {}
    want = str(skill).replace('/', '\\').lower()
    used = set()
    for k, tf in ff.items():
        base = k.split('###')[0]
        if base.startswith('skillName'):
            try:
                used.add(int(base[len('skillName'):]))
            except ValueError:
                pass
            if tf.values and str(tf.values[0]).replace('/', '\\').lower() == want:
                return  # already registered
    slot = next((i for i in range(1, 25) if i not in used), None)
    if slot is None:
        return
    db.set_field(path, f'skillName{slot}', str(skill))
    db.set_field(path, f'skillLevel{slot}', level if not isinstance(level, list) else list(level))


def _relocate_pet_buffslot_summon(db, path):
    """FIX the Pygmalion/Aquardia/Dayria class: a friendly Skill_SpawnPet wired
    into a NON-AI slot (buffSelf*/init/dying/berserk) never casts. Move it to a
    free specialAttack slot (Chance 60) + register it, and DELETE the vacated slot
    (never blank to '' - the B-TOXEUS-2 empty-ref law). Returns #relocated."""
    moved = 0
    for slot in _PET_NONAI_SLOTS:
        sk = _pet_slot_str(db, path, slot)
        if not sk or _skill_class_of(db, sk) != 'Skill_SpawnPet':
            continue
        in_ai = any(_pet_slot_str(db, path, s).replace('/', '\\').lower()
                    == sk.replace('/', '\\').lower() for s in _PET_AI_SLOTS)
        if not in_ai:
            free = _free_pet_special_slot(db, path)
            if free is not None:
                db.set_field(path, free, sk)
                db.set_field(path, free.replace('SkillName', 'Chance'), 60.0)
                _register_pet_skill(db, path, sk, 1)
        ff = db.get_fields(path) or {}
        for k in list(ff):
            if k.split('###')[0] == slot:
                del ff[k]
        moved += 1
    if moved:
        db._modified.add(path)
    return moved


def _mirror_source_skill_kit(db, source, path):
    """build36 A1 (pet-skill-kit): restore the source boss's AI-fired combat kit
    the Lyia-clone transplant structurally dropped. Copies the source's
    specialAttack2-5 combat skills (+ their Chance) into the pet's free special
    slots and registers them, EXCEPT a hostile Skill_SpawnPetMonster (never
    re-teamed onto a friendly pet - it would spawn ENEMIES) and Lyia residue.
    Then relocates any friendly summon the pet inherited into a non-AI slot.
    Additive + defensive; never blanks a slot the source populated to ''."""
    for slot in _PET_SRC_KIT_SLOTS:
        sk = _pet_slot_str(db, source, slot)
        if not sk:
            continue
        base = sk.replace('/', '\\').lower().rsplit('\\', 1)[-1].replace('.dbr', '')
        if _skill_class_of(db, sk) == 'Skill_SpawnPetMonster':
            continue
        if any(res in base for res in _LYIA_RESIDUE):
            continue
        if any(_pet_slot_str(db, path, s).replace('/', '\\').lower()
               == sk.replace('/', '\\').lower() for s in _PET_AI_SLOTS):
            continue  # pet already fires it
        free = _free_pet_special_slot(db, path)
        if free is None:
            break
        db.set_field(path, free, sk)
        ch = _pet_slot_str(db, source, slot.replace('SkillName', 'Chance'))
        if ch:
            try:
                db.set_field(path, free.replace('SkillName', 'Chance'), float(ch))
            except (TypeError, ValueError):
                pass
        _register_pet_skill(db, path, sk, _source_skill_level(db, source, sk))
    _relocate_pet_buffslot_summon(db, path)
    for slot in _PET_AI_SLOTS:
        sk = _pet_slot_str(db, path, slot)
        if sk and _skill_class_of(db, sk) is not None:
            _register_pet_skill(db, path, sk, 1)
    db._modified.add(path)


def _build_boss_summon(db, source_path, pet_paths, summon_skill, display_tag, desc_tag,
                       char_level, life, life_regen, dmg_min, dmg_max, scale=None,
                       loadout=None):
    """D7/D8/D9 shared summon-the-boss builder (3 permanent pets + manual-cast
    summon skill from a source boss's OWN rig). Same crash-safe contract as A10
    Narok/Vort: clone Lyia pets for a Pet.tpl baseline; copy ONLY anim + skill refs
    from the source Monster.tpl; permanent (Lyia base = no TTL). set_field with no
    explicit dtype (preserve type).

    loadout (build30/F2, SUMMON-PET-NAKED fix): optional _loadout_spec()-style list
    of (slot, chance, weight, [n,e,l loot-table paths]) HARD-CODED to mirror the
    source monster's own equip loadout - applied via the sanctioned
    _set_pet_equipment path (never Monster.tpl field copying). None = barehanded
    (correct only when the source itself equips nothing, e.g. Xeiwang)."""
    CONTROLLER = (r'records\skills\spirit\drxpet'
                  r'\drxpet_controllers\controller_skelly_aggressive.dbr')
    lyia_sources = [r'records\skills\soulskills\pets\lyialeafsong_1.dbr',
                    r'records\skills\soulskills\pets\lyialeafsong_2.dbr',
                    r'records\skills\soulskills\pets\lyialeafsong_3.dbr']
    lyia_summon = r'records\skills\soulskills\summon_lyia.dbr'
    source = _find_record(db, source_path)
    if not source:
        print(f"  WARNING D7/8/9: source monster missing: {source_path}")
        return False

    def src_val(rec, name):
        ff = db.get_fields(rec) or {}
        for key, tf in ff.items():
            if key.split('###')[0] == name and tf.values and str(tf.values[0]).strip():
                return tf.values
        return None

    mesh = src_val(source, 'mesh'); anim = src_val(source, 'charAnimationTableName')
    tex = src_val(source, 'baseTexture'); bump = src_val(source, 'bumpTexture')
    src_scale = src_val(source, 'scale'); src_atk = src_val(source, 'attackSkillName')
    # build36 A1 (pet-gear-parity, Will's verbatim law: "a summoned pet carries
    # exactly the gear its wild/hostile source form carries"): when no explicit
    # loadout is given, MIRROR the source's own equip slots (strict = svc/unique
    # source slots get a common substitute so the pet is not naked). An explicit
    # loadout= still wins (D8/D9 keep their proven hand-transcribed tables).
    if loadout is None:
        loadout = _mirror_source_loadout(db, source, strict=True)
    _loadout_slots = {s for s, _c, _w, _p in (loadout or [])}
    for i, path in enumerate(pet_paths):
        s = _find_record(db, lyia_sources[i])
        if not s:
            print(f"  WARNING D7/8/9: Lyia source {lyia_sources[i]} missing")
            return False
        db.clone_record(s, path)
        _copy_animation_fields(db, source, path)
        _update_existing_fields(db, source, path, _SKILL_PREFIXES)
        # F2 (SUMMON-PET-NAKED): mirror the source's armor via the sanctioned
        # hard-coded loadout path (loot TABLES on Pet.tpl equip slots, exactly
        # the proven A10 Narok/Vort mechanism - never Monster.tpl field copies).
        if loadout:
            _set_pet_equipment(db, path, _loadout_spec(loadout))
        # build36 A1 (pet-gear-parity): clear every equip slot the SOURCE does not
        # use (Lyia-clone residue) so the pet mirrors the source EXACTLY - no gear
        # the source lacks (the Xeiwang "no gear" / over-add direction of the law).
        for _gslot in _GEAR_SLOTS:
            if _gslot not in _loadout_slots:
                db.set_field(path, f'chanceToEquip{_gslot}', 0.0)
        # B-SUMMON-2 guard: strip every .anm override the SOURCE monster does not
        # itself define (kills the Lyia-clone Maenad residue; stripped slots fall
        # back to the source's own charAnimationTableName). Source-faithful: a
        # no-op for sources that define their full override set (Toxeus/Huo-ren),
        # and exactly the proven lillued/blade-dancer fix for table-driven sources
        # (Xeiwang's anm_skeleton01 - the build-gate caught 15 Maenad residues).
        n_stripped = _strip_foreign_anim_overrides(db, path, source)
        if n_stripped:
            print(f"    {path.rsplit(chr(92), 1)[-1]}: stripped {n_stripped} foreign "
                  f".anm overrides (source anm table now drives the body)")
        sf = db.set_field
        if mesh: sf(path, 'mesh', str(mesh[0]))
        if tex: sf(path, 'baseTexture', str(tex[0]))
        sf(path, 'bumpTexture', str(bump[0]) if bump else '')   # clear Lyia Maenad residue
        if anim:
            sf(path, 'charAnimationTableName', str(anim[0]))
        else:
            # table-less source (e.g. minotaur family): the live monster
            # drives purely from its own per-record .anm overrides (copied
            # above). Clear Lyia's Maenad table so no foreign clip can shadow
            # them (the proven Rakanizeus 'mesh has defaults' precedent).
            sf(path, 'charAnimationTableName', '')
        if src_atk: sf(path, 'attackSkillName', str(src_atk[0]))
        sf(path, 'scale', float(scale) if scale is not None
                          else (float(src_scale[0]) if src_scale else 1.0))
        sf(path, 'actorHeight', 2.0)
        sf(path, 'description', desc_tag)
        sf(path, 'controller', CONTROLLER)
        sf(path, 'monsterClassification', 'Common')            # working-exemplar parity
        sf(path, 'charLevel', list(char_level))
        sf(path, 'characterLife', life[i])
        sf(path, 'characterLifeRegen', life_regen[i])
        sf(path, 'characterMana', 1000.0); sf(path, 'characterManaRegen', 30.0)
        sf(path, 'handHitDamageMin', dmg_min[i]); sf(path, 'handHitDamageMax', dmg_max[i])
        sf(path, 'dropItems', 0); sf(path, 'giveXP', 0); sf(path, 'experiencePoints', 0)

        # ── build36 A1 (pet-stat-mirror): mirror the source monster's attack/
        #    locomotion cadence + primary attributes. The Lyia archer clone left
        #    every boss-summon pet at atkSpeed 0.5 / run 0.96 / cast 0.65 / DEX 81
        #    / STR 44 / INT 17 -> 38-56% of the hostile swing rate + near-zero
        #    physical/elemental scaling (the "attacks too slowly / hits soft" bug).
        #    set_field with NO dtype preserves each field's FLOAT type (all 12
        #    exist on the Lyia base and on the sources). Builder tuning (life,
        #    charLevel, handHitDamage, scale) above is intentional and kept.
        for _st in ('characterAttackSpeed', 'characterAttackSpeedModifier',
                    'characterRunSpeed', 'characterRunSpeedModifier',
                    'characterSpellCastSpeed', 'characterSpellCastSpeedModifier',
                    'characterDexterity', 'characterDexterityModifier',
                    'characterStrength', 'characterStrengthModifier',
                    'characterIntelligence', 'characterIntelligenceModifier'):
            _sv = src_val(source, _st)
            if _sv is not None:
                sf(path, _st, list(_sv))
        # ── build36 A1 (pet-skill-kit): restore the source's dropped specialAttack
        #    2-5 combat kit + force any friendly summon into an AI-fired slot (the
        #    Pygmalion "never summons" fix). Runs AFTER _update_existing_fields.
        _mirror_source_skill_kit(db, source, path)

        # ── D19 PET-MOBILITY assert (fail-loud; bone-proven 2026-07-09): the
        # pet's PRIMARY anim row must have TABLE locomotion. Foreign-family
        # per-record RunAnim overrides do NOT play (CrocMan_Run binds 2/19 bone
        # tracks on the dragonian/flameguard skeleton); live monsters move
        # because their WEAPONED row falls back to the table clip. A weaponless
        # pet on a table with no unarmedRunAnim has NOTHING playable ->
        # immobile statue (D19 Huo-ren). Weapon-slot loadouts move the pet onto
        # a table-covered row; this assert makes the class unbuildable.
        _rh = any(s == 'RightHand' and c > 0 for s, c, _w, _p in (loadout or []))
        _lh_weap = any(s == 'LeftHand' and c > 0
                       and not all('shield' in q.lower() for q in p)
                       for s, c, _w, p in (loadout or []))
        _row = ('dHanded' if (_rh and _lh_weap)
                else 'sHanded' if (_rh or _lh_weap) else 'unarmed')
        _tbl = _find_record(db, str(anim[0])) if anim else None
        if _tbl:
            _tblf = db.get_fields(_tbl) or {}
            _run_fields = {k.split('###')[0] for k, tf in _tblf.items()
                           if k.split('###')[0].endswith('RunAnim')
                           and tf.values and str(tf.values[0]).strip()}
            if _run_fields and f'{_row}RunAnim' not in _run_fields:
                raise SystemExit(
                    f"D19 pet-mobility: {path} primary anim row '{_row}' has "
                    f"no TABLE RunAnim in {anim[0]} (table rows with "
                    f"locomotion: {sorted(_run_fields)}) -> pet would be "
                    f"IMMOBILE. Equip the source monster's weapon "
                    f"(table-covered row) or use a table that covers "
                    f"'{_row}'.")
        else:
            # table-less source: locomotion must come from the source's OWN
            # per-record override on the primary row (native-rig, proven by
            # the live monster; copied onto the pet above).
            if not src_val(source, f'{_row}RunAnim'):
                raise SystemExit(
                    f"D19 pet-mobility: {path} has no anim table AND the "
                    f"source defines no {_row}RunAnim override -> pet would "
                    f"be IMMOBILE on its primary row '{_row}'.")
        db._modified.add(path)
    # build36 A1: register this family (source + pets) for the three fail-loud pet
    # gates (parity / gear / skill-kit), run once after all pets are built.
    _SUMMON_PET_BUILDS.append((source_path, list(pet_paths)))
    ss = _find_record(db, lyia_summon)
    if ss:
        db.clone_record(ss, summon_skill)
    else:
        _ensure_record(db, summon_skill, r'database\Templates\Skill_SpawnPet.tpl')
        db.set_field(summon_skill, 'Class', 'Skill_SpawnPet', DATA_TYPE_STRING)
    sf = db.set_field
    sf(summon_skill, 'isPetDisplayable', 1)
    sf(summon_skill, 'skillDisplayName', display_tag)
    sf(summon_skill, 'skillManaCost', [250.0, 300.0, 350.0])
    sf(summon_skill, 'skillCooldownTime', 180.0)
    sf(summon_skill, 'skillCooldownReductionModifier', 180.0)
    sf(summon_skill, 'skillMaxLevel', 3)
    sf(summon_skill, 'petLimit', 1); sf(summon_skill, 'petBurstSpawn', 1)
    sf(summon_skill, 'spawnObjects', list(pet_paths))
    db._modified.add(summon_skill)
    return True


def _create_blood_toxeus_summon(db):
    """D7 (Will 2026-07-09): the Devourer of Blood soul's summon chain - 3 permanent
    Toxeus pets (RevenantPoison.msh + newskeleton_crimson.tex, ship-verified in
    Creatures.arc) + the manual-cast summon skill. Aggressive superboss power
    (flagged in needs_will_signoff)."""
    ok = _build_boss_summon(
        db, _BT_MONSTER, _BT_PET_PATHS, SUMMON_TOXEUS_SKILL,
        'tagSVCSummonBloodToxeus', 'tagMonsterHemorrheus',
        char_level=[40, 68, 100], life=[12000.0, 18000.0, 26000.0],
        life_regen=[30.0, 60.0, 100.0],
        dmg_min=[70.0, 110.0, 160.0], dmg_max=[120.0, 180.0, 260.0], scale=2.1)
        # build36 A1 (pet-gear-parity): loadout OMITTED -> auto-derive the STRICT
        # source mirror. um_bloodtoxeus_99 equips RightHand(svc\crimsonverdict) +
        # LeftHand(svc\bleed_affix) + Torso + Forearm + LowerBody. The old Torso+
        # LowerBody-only loadout left the Devourer bare-fisted; the strict mirror
        # substitutes a common weapon+shield for the two svc slots (naked-pet law)
        # and mirrors the three common armor slots -> the Devourer "keeps its
        # weapon" (Will's law), fully geared like its wild form.
    if ok:
        print("  D7 Toxeus summon: 3 pets from boss rig (RevenantPoison + crimson) + "
              "summon skill (250/300/350 en, 180s cd); gear auto-mirrors the boss (A1)")
    return ok


def _create_blood_toxeus_proxy_50(db):
    """D7 (Will 2026-07-09): the 2nd Toxeus spawn proxy for the parchment placement
    at chanceToRun=50 (the chest proxy q_bloodtoxeus_lone stays chanceToRun=100).
    Same pool (_BT_POOL = same boss + 2 blood-demon adds). Map lane: place the record
    q_bloodtoxeus_lone_50 (records/drxmap/proxy/q_bloodtoxeus_lone_50.dbr) at the
    parchment placement."""
    if not db.has_record(_BT_PROXY):
        print("  WARNING D7: q_bloodtoxeus_lone missing; 50% proxy skipped")
        return None
    db.clone_record(_BT_PROXY, _BT_PROXY_50)
    db.set_field(_BT_PROXY_50, 'chanceToRun', 50.0)
    db._modified.add(_BT_PROXY_50)
    print("  D7 Toxeus 2nd proxy: q_bloodtoxeus_lone_50 @ chanceToRun=50 "
          "(same pool/boss; chest proxy stays 100%)")
    return _BT_PROXY_50


def _wire_summon_soul(db, soul_paths, summon_skill, name_tag=None):
    """D8/D9: repoint each n/e/l soul to the MANUAL-CAST summon (itemSkillLevel
    1/2/3). A summon soul is a pet BUTTON, never an on-attack proc, so any
    inherited itemSkillAutoController is DELETED here (absent shape, never
    blanked to '' per the B-TOXEUS-2 zero-precedent loader-abort law).

    D21 Long Nu fix (2026-07-10, live Steam b31): her souls are the SV
    palai_soul_{n,e,l} records, which carried an on-attack proc controller
    (base_atenemy_onattack) from their original proc wiring. build31 set
    itemSkillName=summon_longnu but LEFT the controller, so the game re-cast the
    summon on every player hit; with the summon skill's petLimit=1 she was
    re-summoned/reset each swing and never landed an attack. That single stray
    field is the ONE root cause of BOTH of Will's reports ('summons on attack'
    and 'does no damage'). Clearing it here fixes every summon soul uniformly
    (a no-op for the D8/D9/D13/D14/D20 souls, which carry no controller).
    Optionally reassign itemNameTag to a mod-owned disambiguated name tag."""
    for i, sp in enumerate(soul_paths):
        r = _find_record(db, sp)
        if not r:
            print(f"  WARNING D8/9: soul missing: {sp}")
            continue
        db.set_field(r, 'itemSkillName', summon_skill)
        db.set_field(r, 'itemSkillLevel', i + 1)
        cleared = False
        for k, tf in (db.get_fields(r) or {}).items():
            if k.split('###')[0] == 'itemSkillAutoController' and tf.values:
                tf.values = []
                cleared = True
        if cleared:
            print(f"    manual-cast: stripped inherited itemSkillAutoController "
                  f"from {sp.rsplit(chr(92), 1)[-1]} (summon = pet button)")
        if name_tag:
            db.set_field(r, 'itemNameTag', name_tag)
        db._modified.add(r)


# ── GROUP B (build32): Toxeus the Murderer, Enslaver of Souls ────────────────
# Will APPROVED (BACKLOG N6/Enslaver). A ShadowStalker-demon reincarnation of
# Toxeus who ROAMS the world as a rare mini-boss leading a warband of shadow
# marauders. Derived from am_deathstalker_55_ambush (the ShadowStalker.msh rig,
# racialProfile Demon, table-LESS inline anim block incl. unarmedRunAnim -
# rig-safe + summon-safe by construction; the um_toxeus_99 SP-Toxeus lineage is
# carried through the KIT + name, since the design mandates ShadowStalker.msh
# which um_toxeus_99 does not use). The ROAMING SWEEP appends him at weight 1 to
# every eligible hostile trash pool with each existing member weight x60 (so he
# stays rarer than 1/2400 per main-slot); a fail-loud gate proves ONLY eligible
# (non boss/quest/hero) pools were touched. His soul is a MANUAL summon-the-boss
# (pet-of-pet: the friendly Enslaver pet auto-casts a friendly marauder summon).
_EN_BOSS = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
_EN_RIG_DONOR = r'records\creature\monster\shadowstalker\am_deathstalker_55_ambush.dbr'  # ShadowStalker.msh, Demon, inline anim
_EN_MARAUDER = r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'      # hostile Champion
_EN_SUMMON_MARAUDERS = r'records\skills\boss skills\svc_enslaver_summonmarauders.dbr'      # boss's HOSTILE Skill_SpawnPetMonster
_EN_SUMMON_DONOR = r'records\skills\boss skills\yaoguai_summonshadowstalkers.dbr'
_EN_BAND = [40, 68, 100]
_EN_SHADOWCLOAK_FX = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr'
# build36 A2 (Enslaver rework, Will 2026-07-11: "black skeleton on the Blood-
# Toxeus rig"): the BOSS now clones the skeleton kin um_toxeus_99 (the exact rig
# the Devourer of Blood uses: RevenantPoison.msh + anm_skeleton01 + a full common
# skeleton weapon loadout + skeleton weapon/cast anims) and wears an ALL-BLACK
# charcoal skin, instead of the ShadowStalker demon. Its friendly summon pet
# inherits the black-skeleton rig automatically. The MARAUDERS stay ShadowStalker
# demons (Will: "keep the form he looks like now"), only super-strong.
_EN_SKELETON_DONOR = r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr'
_EN_BOSS_MESH = r'Creatures\Monster\Skeleton\RevenantPoison.msh'
_EN_BOSS_TEX = r'Creatures\Monster\Skeleton\NewSkeleton_Charcoal.tex'
_EN_SK_ATTACKSKILL = r'records\skills\monster skills\attack_melee\toxeus_attackskill.dbr'
# Enslaver kit (Toxeus lineage; all existence-verified).
_EN_SK_NETHERSTRIKE = r'records\skills\monster skills\attack_melee\netherstrike.dbr'
_EN_SK_BLADESTORM = r'records\skills\monster skills\attack_radius\toxeus_bladestorm.dbr'
_EN_SK_LIFEDRAIN = r'records\skills\spirit\lifedrain.dbr'
_EN_SK_FLASHPOWDER = r'records\skills\stealth\flashpowder.dbr'
_EN_SK_LETHALSTRIKE = r'records\skills\stealth\lethalstrike.dbr'
_EN_SK_MORTALWOUND = r'records\skills\stealth\lethalstrike_mortalwound.dbr'
_EN_SK_SPEEDALL = r'records\skills\monster skills\auras\character_speedall.dbr'
_EN_SK_CONVIMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_EN_SK_HEROSCALING = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'
_EN_SK_TOXEUSPASSIVE = r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'
_EN_SK_ARMORPASSIVE = r'records\skills\monster skills\defense\armor_passive.dbr'
_EN_SK_GP_N = r'records\skills\monster skills\globalproperties_normal01.dbr'
_EN_SK_GP_E = r'records\skills\monster skills\globalproperties_epic01.dbr'
_EN_SK_GP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'
# soul augments (Occult).
_EN_AUG_ANATOMY = r'records\skills\stealth\drxanatomy.dbr'
_EN_AUG_DARKAPERTURE = r'records\skills\stealth\drxdarklings_darkaperture.dbr'
# roaming sweep tuning.
_EN_SWEEP_K = 60          # existing-weight multiplier
_EN_SWEEP_MAX_P = 1.0 / (40 * 60)   # per-pool enslaver p_slot ceiling (1/2400)
_EN_SWEEP_ALLOW_PREFIX = (
    'records\\proxies orient\\pools',
    'records\\proxies egypt\\pools',
    'records\\proxies greek\\',
    'records\\xpack\\proxieshades',
)
_EN_SWEEP_BAD_SUB = ('boss', 'quest', 'hero', 'escort', 'summon', 'minion',
                     'ambush', 'unique', 'spawner', 'shrine', 'chest',
                     'telkine', 'gorgon')


def _create_enslaver(db, tags):
    """Build the whole Enslaver DB side (boss + marauder + hostile summon +
    friendly pet-of-pet + summon soul). The roaming sweep + verify gate run
    separately (after this, so the boss exists to reference)."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    if not db.has_record(_EN_RIG_DONOR) or not db.has_record(_EN_SUMMON_DONOR) \
            or not db.has_record(_EN_SKELETON_DONOR):
        print("  ENSLAVER: WARNING rig/summon/skeleton donor missing; group skipped")
        return

    def _clear_range(rec, prefix, lo, hi):
        ff = db.get_fields(rec)
        if not ff:
            return
        import re as _re
        for k in list(ff):
            base = k.split('###')[0]
            m = _re.match(_re.escape(prefix) + r'(\d+)$', base)
            if m and lo <= int(m.group(1)) <= hi:
                del ff[k]
        db._modified.add(rec)

    # ── 1. Hostile marauder (Champion, ~2x hand dmg, ShadowStalker rig + cloak). ──
    db.clone_record(_EN_RIG_DONOR, _EN_MARAUDER)
    M = _EN_MARAUDER
    sf(M, 'description', 'tagSVCMonsterEnslaverMarauder')
    sf(M, 'monsterClassification', 'Champion')
    sf(M, 'characterRacialProfile', 'Demon')
    sf(M, 'charLevel', list(_EN_BAND))
    # build36 A2 (super-strong shadow marauders, Will Option A): a 10-12 pack of
    # these on top of the boss is a real AoE-or-die swarm.
    sf(M, 'characterLife', [5000.0, 8500.0, 13000.0])
    sf(M, 'characterStrength', 460.0)
    sf(M, 'characterDexterity', 620.0)
    sf(M, 'handHitDamageMin', 300.0)
    sf(M, 'handHitDamageMax', 380.0)
    sf(M, 'characterRunSpeed', 1.7)
    sf(M, 'charFxPakRunningNames', [_EN_SHADOWCLOAK_FX], S)   # drxshadowcloakrunning_fx
    sf(M, 'dropItems', 0)
    db._modified.add(M)

    # ── 2. Boss's HOSTILE marauder summon (yaoguai clone). build36 A2: rapid
    #    many-summon (burst 6 / cd 2.0s / petLimit 12) - he reaches ~12 marauders
    #    within ~2s of aggro; all class-proven (donor is burst 5 / limit 15). ──
    db.clone_record(_EN_SUMMON_DONOR, _EN_SUMMON_MARAUDERS)
    sf(_EN_SUMMON_MARAUDERS, 'spawnObjects', [_EN_MARAUDER])
    sf(_EN_SUMMON_MARAUDERS, 'petBurstSpawn', 6)
    sf(_EN_SUMMON_MARAUDERS, 'skillCooldownTime', 2.0)
    sf(_EN_SUMMON_MARAUDERS, 'petLimit', 12)
    db._modified.add(_EN_SUMMON_MARAUDERS)
    _BOSS_KIT_CLONES.append((_EN_SUMMON_DONOR, _EN_SUMMON_MARAUDERS))

    # ── 3. The boss (build36 A2: ALL-BLACK SKELETON on the Blood-Toxeus rig).
    #    Clone the skeleton kin um_toxeus_99 (NOT am_deathstalker) so we inherit
    #    RevenantPoison.msh + charAnimationTableName=anm_skeleton01 + the full
    #    common skeleton weapon loadout + skeleton weapon/cast anims (every kit
    #    skill below is anim-safe on anm_skeleton01, shared with um_toxeus_21/99 +
    #    bloodtoxeus). Then override to the charcoal all-black skin. scale 2.0,
    #    actorHeight 2.5 ("towering"), HP/attrs/resists as before. ──
    db.clone_record(_EN_SKELETON_DONOR, _EN_BOSS)
    B = _EN_BOSS
    sf(B, 'description', 'tagSVCMonsterEnslaver')
    sf(B, 'monsterClassification', 'Boss')
    sf(B, 'mesh', _EN_BOSS_MESH)                          # RevenantPoison (Devourer rig)
    sf(B, 'baseTexture', _EN_BOSS_TEX)                    # ALL-BLACK charcoal skin
    sf(B, 'characterRacialProfile', 'Undead')            # skeleton (was Demon)
    sf(B, 'charLevel', list(_EN_BAND))
    sf(B, 'characterLife', [13000.0, 18000.0, 24000.0])
    sf(B, 'characterStrength', 480.0)
    sf(B, 'characterDexterity', 660.0)
    sf(B, 'characterIntelligence', 420.0)
    sf(B, 'characterLifeRegen', 12.0)
    sf(B, 'handHitDamageMin', 150.0)
    sf(B, 'handHitDamageMax', 250.0)
    sf(B, 'scale', 2.0)
    sf(B, 'actorHeight', 2.5)
    sf(B, 'characterRunSpeed', 1.5)
    # defensive wall (NO bleeding wall: expressed as flat resists, not the
    # bloodwitch zpassive_resists_bleed record).
    sf(B, 'defensiveLife', 100.0)
    sf(B, 'defensivePierce', 80.0)
    sf(B, 'defensivePhysical', 30.0)
    # kit (clear the donor's trash passives 1..18 first, then author; the
    # specialAttack*SkillName slots are explicitly overwritten below).
    _clear_range(B, 'skillName', 1, 18)
    kit = [
        _EN_SK_NETHERSTRIKE, _EN_SK_BLADESTORM, _EN_SK_LIFEDRAIN, _EN_SK_FLASHPOWDER,
        _EN_SK_LETHALSTRIKE, _EN_SK_MORTALWOUND, _EN_SK_SPEEDALL, _EN_SUMMON_MARAUDERS,
        _EN_SK_CONVIMMUNITY, _EN_SK_HEROSCALING, _EN_SK_TOXEUSPASSIVE, _EN_SK_ARMORPASSIVE,
        _EN_SK_GP_N, _EN_SK_GP_E, _EN_SK_GP_L,
    ]
    for i, sk in enumerate(kit, start=1):
        sf(B, f'skillName{i}', sk)
    # build36 A2: skeleton-native basic attack (what bloodtoxeus uses); netherstrike
    # stays a special-attack blink proc below.
    sf(B, 'attackSkillName', _EN_SK_ATTACKSKILL)
    # build36 A2: DELETE the inherited GREEN weapon-glow initialSkill (um_toxeus_99
    # carries initialSkillName=toxeus_envenomweapon -> a green blade shroud on an
    # all-black skeleton). Field-absence parity (never blank to '' - B-TOXEUS-2).
    _en_ff = db.get_fields(B) or {}
    for _k in list(_en_ff):
        if _k.split('###')[0] == 'initialSkillName':
            del _en_ff[_k]
    # build36 A2: he casts the rapid marauder summon aggressively (chance 50 -> 70).
    for i, (sk, ch) in enumerate([
            (_EN_SUMMON_MARAUDERS, 70.0), (_EN_SK_NETHERSTRIKE, 45.0),
            (_EN_SK_BLADESTORM, 40.0), (_EN_SK_FLASHPOWDER, 30.0),
            (_EN_SK_LETHALSTRIKE, 35.0)], start=1):
        suf = '' if i == 1 else str(i)
        sf(B, f'specialAttack{suf}SkillName', sk)
        sf(B, f'specialAttack{suf}Chance', ch)
    db._modified.add(B)

    # ── 4. Friendly pet-of-pet marauders (reuse _build_boss_summon on the
    #    marauder rig -> friendly pet + summon skill). isPetDisplayable off (the
    #    Enslaver PET auto-casts it, it is not a player button). ──
    marauder_pets = [rf'records\skills\soulskills\pets\enslaver_marauder_{i}.dbr' for i in (1, 2, 3)]
    # build36 A2: the player's raised shadow pack matches the super-strong ladder
    # (Will: "he raises his own shadow pack for you"). Gear/skills auto-mirror the
    # marauder source (RightHand dyn_1h) via the A1 builder overhaul.
    _build_boss_summon(
        db, _EN_MARAUDER, marauder_pets, SUMMON_ENSLAVER_PETMARAUDERS,
        'tagSVCSummonEnslaverMarauders', 'tagSVCMonsterEnslaverMarauder',
        char_level=list(_EN_BAND), life=[5000.0, 8500.0, 13000.0],
        life_regen=[25.0, 45.0, 70.0],
        dmg_min=[150.0, 230.0, 300.0], dmg_max=[220.0, 320.0, 420.0], scale=1.0)
    sf(SUMMON_ENSLAVER_PETMARAUDERS, 'isPetDisplayable', 0)
    sf(SUMMON_ENSLAVER_PETMARAUDERS, 'petLimit', 3)
    sf(SUMMON_ENSLAVER_PETMARAUDERS, 'petBurstSpawn', 1)
    sf(SUMMON_ENSLAVER_PETMARAUDERS, 'skillCooldownTime', 10.0)
    sf(SUMMON_ENSLAVER_PETMARAUDERS, 'skillManaCost', 0.0)
    db._modified.add(SUMMON_ENSLAVER_PETMARAUDERS)

    # ── 5. The summon-the-boss soul: friendly Enslaver pet via _build_boss_summon,
    #    then repoint the boss-pet's specialAttackSkillName to the FRIENDLY pet-of-pet
    #    summon (so the friendly pet raises FRIENDLY marauders, not the boss's hostile
    #    Skill_SpawnPetMonster). ──
    enslaver_pets = [rf'records\skills\soulskills\pets\toxeus_enslaver_{i}.dbr' for i in (1, 2, 3)]
    _build_boss_summon(
        db, _EN_BOSS, enslaver_pets, SUMMON_ENSLAVER_SKILL,
        'tagSVCSummonEnslaver', 'tagSVCMonsterEnslaver',
        char_level=list(_EN_BAND), life=[13000.0, 18000.0, 24000.0],
        life_regen=[30.0, 60.0, 100.0],
        dmg_min=[110.0, 170.0, 240.0], dmg_max=[160.0, 250.0, 350.0], scale=2.0)
    _host = _EN_SUMMON_MARAUDERS.replace('/', '\\').lower()
    for p in enslaver_pets:
        if not db.has_record(p):
            continue
        # replace EVERY inherited reference to the boss's HOSTILE marauder summon
        # (in any skillName / specialAttack*SkillName slot) with the friendly
        # pet-of-pet summon, so the friendly Enslaver pet raises FRIENDLY marauders
        # (never enemies for the player).
        ff = db.get_fields(p) or {}
        for k, tf in ff.items():
            for j, v in enumerate(list(tf.values)):
                if isinstance(v, str) and v.replace('/', '\\').lower() == _host:
                    tf.values[j] = SUMMON_ENSLAVER_PETMARAUDERS
        sf(p, 'specialAttackSkillName', SUMMON_ENSLAVER_PETMARAUDERS)
        sf(p, 'specialAttackChance', 40.0)
        db._modified.add(p)

    # ── 6. Soul records (manual summon; Occult augments; dense stats). ──
    def _en_stats(t, il, sklvl):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]; r = lambda v: round(v * m, 1)
        return {
            **_bmp(t),
            'itemSkillName': (S, SUMMON_ENSLAVER_SKILL), 'itemSkillLevel': (I, sklvl),
            'augmentSkillName1': (S, _EN_AUG_ANATOMY), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _EN_AUG_DARKAPERTURE), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(320.0)), 'characterLifeModifier': (F, r(12.0)),
            'characterStrength': (F, r(35.0)), 'characterDexterity': (F, r(40.0)),
            'characterOffensiveAbility': (F, r(100.0)),
            'characterRunSpeedModifier': (F, r(12.0)),
            'offensivePhysicalMin': (F, r(70.0)), 'offensivePhysicalMax': (F, r(110.0)),
            'offensivePhysicalModifier': (I, int(r(40))),
            'offensiveLifeLeechMin': (F, r(40.0)),
            'offensivePierceRatioMin': (F, r(25.0)),
            'defensiveDisruption': (F, r(40.0)),      # weird signature: soul-enslaver's grip resists mind magic
            'defensivePierce': (F, r(30.0)), 'defensiveLife': (F, r(25.0)),
            'characterDeflectProjectile': (F, r(10.0)),
        }
    en_tiers = [{'diff': t, 'itemLevel': il, 'stats': _en_stats(t, il, sk)}
                for t, il, sk in (('n', 40, 1), ('e', 68, 2), ('l', 100, 3))]
    # drop off the boss's Finger2 at 66% (Boss classification -> soul-leak gate OK).
    en_souls = _create_soul(db, 'enslaver', 'tagSVCSoulEnslaver', en_tiers,
                            monster=_EN_BOSS, drop_rate=66.0)
    _wire_summon_soul(db, en_souls, SUMMON_ENSLAVER_SKILL)   # manual: strip controller, level 1/2/3

    tags['tagSVCMonsterEnslaver'] = '{^r}Toxeus the Murderer, Enslaver of Souls'
    tags['tagSVCMonsterEnslaverMarauder'] = '{^r}Enslaved Shadow Marauder'
    tags['tagSVCSummonEnslaver'] = 'Summon Toxeus, Enslaver of Souls'
    tags['tagSVCSummonEnslaverMarauders'] = 'Raise Shadow Marauders'
    # build36 A2: full corrected soul name (was "{^F}Enslaver of Souls Soul").
    tags['tagSVCSoulEnslaver'] = '{^F}Toxeus the Murderer, Enslaver of Souls Soul'
    tags['tagSVCSoulEnslaverDESC'] = ('Toxeus the Murderer, reborn from the shadow as '
        'the Enslaver of Souls: a towering skeletal revenant robed all in black who '
        'binds the dead into a marauding warband. Its bearer may call him forth - and '
        'he raises his own shadow pack to fight beside you.')
    print("  Enslaver (A2): boss = ALL-BLACK skeleton (RevenantPoison + charcoal, "
          "um_toxeus_99 rig) scale 2.0 + rapid marauder summon (burst 6/cd 2/limit "
          "12); super-strong ShadowStalker-demon marauders [5000/8500/13000]; "
          "friendly pet-of-pet; summon soul (66% Finger2); tags set. Sweep runs next.")


def _sweep_inject_roaming_rare(db):
    """Append the Enslaver at weight 1 to every ELIGIBLE hostile trash pool, with
    each existing member weight x60, so he stays rarer than 1/2400 per main-slot.
    Only touches act-trash pools (orient/egypt/greek/hades) whose basename carries
    no boss/quest/hero/summon marker, whose resolvable name members are all
    Class=Monster, that have a free name slot (< 18), and whose x60 name-weight
    total reaches >= 2400 (so the weight-1 append satisfies the p_slot ceiling).
    Returns the list of touched pool record names."""
    if not db.has_record(_EN_BOSS):
        print("  ENSLAVER SWEEP: boss record missing; skipped")
        return []
    S, I = DATA_TYPE_STRING, DATA_TYPE_INT
    recmap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def gv(n, f):
        v = db.get_field_value(n, f)
        return (v[0] if isinstance(v, list) else v)

    def is_pool(n):
        t = gv(n, 'templateName')
        return t and 'proxypool.tpl' in str(t).lower()

    def eligible(n):
        nl = n.replace('/', '\\').lower()
        if not any(nl.startswith(p) for p in _EN_SWEEP_ALLOW_PREFIX):
            return False
        base = nl.split('\\')[-1]
        if base.startswith(('q_', 'sq', 'xsq', 'mq', 'svc_')):
            return False
        if any(b in base for b in _EN_SWEEP_BAD_SUB):
            return False
        # all resolvable name members must be hostile Class=Monster
        names = [gv(n, 'name%d' % i) for i in range(1, 19)]
        names = [str(x) for x in names if x and str(x).strip()]
        if not names:
            return False
        for m in names:
            r = recmap.get(m.replace('/', '\\').lower())
            if r is not None and str(gv(r, 'Class')) != 'Monster':
                return False
        return True

    touched = []
    for n in list(db.record_names()):
        if not is_pool(n) or not eligible(n):
            continue
        # find used name slots + total weight
        used = []
        wtotal = 0
        for i in range(1, 19):
            nm = gv(n, 'name%d' % i)
            if nm and str(nm).strip():
                used.append(i)
                w = gv(n, 'weight%d' % i)
                try:
                    wtotal += int(w) if w else 0
                except (TypeError, ValueError):
                    pass
        free = next((i for i in range(1, 19) if i not in used), None)
        if free is None:                    # at 18-slot cap
            continue
        if wtotal <= 0 or (_EN_SWEEP_K * wtotal + 1) < (40 * 60):
            continue                        # too small: would exceed the p_slot ceiling
        # x60 the existing member weights, append the enslaver at weight 1
        for i in used:
            w = gv(n, 'weight%d' % i)
            try:
                w = int(w) if w else 0
            except (TypeError, ValueError):
                w = 0
            db.set_field(n, 'weight%d' % i, w * _EN_SWEEP_K, I)
        db.set_field(n, 'name%d' % free, _EN_BOSS, S)
        db.set_field(n, 'weight%d' % free, 1, I)
        db._modified.add(n)
        touched.append(n)
    print("  ENSLAVER SWEEP: injected the roaming Enslaver into %d eligible hostile "
          "trash pool(s) (each existing weight x%d, him at weight 1)"
          % (len(touched), _EN_SWEEP_K))
    return touched


def _verify_roaming_sweep(db, touched):
    """FAIL-LOUD gate for the Enslaver roaming sweep: prove ONLY eligible
    (non boss/quest/hero) pools were touched, the enslaver is present at weight 1
    with p_slot <= 1/2400 in each, his boss + marauder + summon resolve at the
    right band, and no touched pool matches an exclusion marker. Re-derives the
    touched set from the arz (verifies the actual diff, not a passed list)."""
    S = DATA_TYPE_STRING
    problems = []

    def gv(n, f):
        v = db.get_field_value(n, f)
        return (v[0] if isinstance(v, list) else v)

    # (0) boss + marauder + summon resolve at band [40,68,100] (read the FULL
    # list, not gv() which collapses multi-value fields to their first element).
    for rec in (_EN_BOSS, _EN_MARAUDER):
        if not db.has_record(rec):
            problems.append(f"{rec} missing")
            continue
        cl = db.get_field_value(rec, 'charLevel')
        cl = cl if isinstance(cl, list) else [cl]
        if [int(x) for x in cl] != _EN_BAND:
            problems.append(f"{rec} charLevel {cl} != {_EN_BAND}")
    for sk in (SUMMON_ENSLAVER_SKILL, _EN_SUMMON_MARAUDERS):
        if not db.has_record(sk):
            problems.append(f"summon skill {sk} missing")

    # (1) re-derive touched pools = any ProxyPool containing the enslaver in a name
    # slot, EXCLUDING the whitelisted dedicated test-yard pool (which legitimately
    # carries him at weight 100, TESTHUB-only + inert on canonical). all_enslaver_
    # pools keeps EVERY enslaver-bearing pool (incl. yard) for the leak guard (4).
    enl = _EN_BOSS.replace('/', '\\').lower()
    yard_pools = {p.replace('/', '\\').lower() for p in _EN_YARD_POOLS}
    derived = []
    all_enslaver_pools = []
    for n in db.record_names():
        t = gv(n, 'templateName')
        if not (t and 'proxypool.tpl' in str(t).lower()):
            continue
        names = [gv(n, 'name%d' % i) for i in range(1, 19)]
        if any(x and str(x).replace('/', '\\').lower() == enl for x in names):
            all_enslaver_pools.append(n)
            if n.replace('/', '\\').lower() in yard_pools:
                continue        # yard pool: excluded from the swept-set derivation
            derived.append(n)

    if set(derived) != set(touched):
        problems.append(f"touched set mismatch: sweep touched {len(touched)}, "
                        f"arz shows {len(derived)} non-yard pools with the enslaver")

    for n in derived:
        nl = n.replace('/', '\\').lower()
        base = nl.split('\\')[-1]
        # (2) eligibility: allowed prefix + no boss/quest/hero marker
        if not any(nl.startswith(p) for p in _EN_SWEEP_ALLOW_PREFIX):
            problems.append(f"TOUCHED NON-ELIGIBLE PATH: {n}")
        if base.startswith(('q_', 'sq', 'xsq', 'mq', 'svc_')) or \
                any(b in base for b in _EN_SWEEP_BAD_SUB):
            problems.append(f"TOUCHED BOSS/QUEST/HERO POOL: {n}")
        # (3) enslaver at weight 1 + p_slot <= 1/2400
        wtotal = 0
        enl_w = None
        for i in range(1, 19):
            nm = gv(n, 'name%d' % i)
            if not (nm and str(nm).strip()):
                continue
            w = gv(n, 'weight%d' % i)
            try:
                w = int(w) if w else 0
            except (TypeError, ValueError):
                w = 0
            wtotal += w
            if str(nm).replace('/', '\\').lower() == enl:
                enl_w = w
        if enl_w != 1:
            problems.append(f"{n}: enslaver weight {enl_w} != 1")
        elif wtotal <= 0 or (1.0 / wtotal) > _EN_SWEEP_MAX_P + 1e-9:
            problems.append(f"{n}: enslaver p_slot {1.0/max(wtotal,1):.5f} > "
                            f"{_EN_SWEEP_MAX_P:.5f} (too common)")

    # (4) LEAK GUARD (proves BOTH directions): EVERY pool carrying the Enslaver
    # must be either a swept eligible trash pool (in `touched`) OR the whitelisted
    # dedicated yard pool (_EN_YARD_POOLS). Any enslaver-bearing pool that is
    # neither = a LEAK (he escaped into a non-eligible pool) -> FAIL loud. This is
    # paired with the weight-1 check above (which still fires for any NON-yard
    # derived pool), so together the gate FAILS if the Enslaver appears above
    # weight 1 in ANY non-yard pool AND if he appears in any unexpected pool at
    # all - while allowing the yard's legitimate 100% pool.
    touched_lc = {t.replace('/', '\\').lower() for t in touched}
    for n in all_enslaver_pools:
        nl = n.replace('/', '\\').lower()
        if nl not in touched_lc and nl not in yard_pools:
            problems.append(f"ENSLAVER LEAK: {n} carries the Enslaver but is "
                            f"neither a swept eligible trash pool nor a "
                            f"whitelisted yard pool ({sorted(_EN_YARD_POOLS)})")

    if not derived:
        problems.append("sweep touched ZERO pools (roaming Enslaver would never appear)")
    elif len(derived) < 500:
        problems.append(f"sweep touched only {len(derived)} pools (< 500 floor; "
                        f"a regression likely narrowed eligibility)")

    if problems:
        for p in problems[:20]:
            print(f"  ROAMING-SWEEP OFFENDER: {p}")
        raise SystemExit(
            f"Enslaver roaming-sweep gate FAILED: {len(problems)} problem(s) "
            f"(see offenders above)")
    print(f"  Roaming-sweep gate OK: {len(derived)} eligible hostile trash pools "
          f"carry the Enslaver at weight 1 (p_slot <= 1/2400), 0 dedicated "
          f"(basename) boss/quest/hero/escort/friendly pools touched; 19 general "
          f"trash pools legitimately contain rare low-weight hero MEMBERS per "
          f"vanilla (the roaming rare walks among area heroes), boss+marauder at "
          f"band {_EN_BAND}. Leak guard: all {len(all_enslaver_pools)} "
          f"enslaver-bearing pools are swept-or-yard ({len(_EN_YARD_POOLS)} "
          f"whitelisted yard pool(s) at weight 100 excluded from the weight-1 rule).")


def _apply_d8_d9_summon_souls(db, tags):
    """D8 (Xeiwang, Flame of Hatred) + D9 (Huo-ren, the Mountainblade): boss-named
    soul -> summons that boss (same proven A10/D7 pattern). Render assets SHIP:
    xaiwengmesh.msh (drx.arc) + skeleton_xeiwang.tex (DRXtextures.arc); flameguardmesh
    .msh (drx.arc) + mountainblade.tex (SVTextures.arc). Aggressive power flagged for
    Will's sign-off. D9 ALSO FIXES a wrong-drop: um_mountainblade_43 inherited
    lootFinger2Item1=mukesha_soul from SV upstream (wire_souls preserves inherited
    loot so it never self-corrected); _create_soul re-points it to its own new soul.
    Runs AFTER _overhaul_generic_souls so the summon rewire wins."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # ── D8: Xeiwang, Flame of Hatred (um_xaiweng_48, Boss L48/59/71; souls EXIST). ──
    XW_SRC = r'records\creature\monster\skeleton\um_xaiweng_48.dbr'
    xw_pets = [rf'records\skills\soulskills\pets\xeiwang_{i}.dbr' for i in (1, 2, 3)]
    xw_souls = [rf'records\item\equipmentring\soul\skeleton\xeiwang_soul_{t}.dbr' for t in 'nel']
    if _build_boss_summon(db, XW_SRC, xw_pets, SUMMON_XEIWANG_SKILL,
                          'tagSVCSummonXeiwang', 'tagNewHero196',
                          char_level=[48, 59, 71], life=[12000.0, 16000.0, 21000.0],
                          life_regen=[30.0, 60.0, 100.0],
                          dmg_min=[70.0, 105.0, 150.0], dmg_max=[110.0, 165.0, 235.0],
                          # D19 correction: the old loadout=None rode on a FALSE
                          # premise ("Xeiwang equips nothing") - um_xaiweng_48
                          # equips RightHand/Torso/Forearm/LowerBody at 100
                          # (decoded 2026-07-09). Mirror its own Item1 tables
                          # (commondynamic, the proven auto-equip path); the
                          # weapon also parks the pet on the sHanded row.
                          loadout=[
                              ('RightHand', 100.0, 5000, [
                                  r'records\item\loottables\weapons\mastertables\1h_dyn_n03.dbr',
                                  r'records\item\loottables\weapons\mastertables\1h_dyn_e03.dbr',
                                  r'records\item\loottables\weapons\mastertables\1h_dyn_l03.dbr']),
                              ('Torso', 100.0, 5000, [
                                  r'records\item\loottables\torso\commondynamic\melee_n03.dbr',
                                  r'records\item\loottables\torso\commondynamic\melee_e03.dbr',
                                  r'records\item\loottables\torso\commondynamic\melee_l03.dbr']),
                              ('Forearm', 100.0, 5000, [
                                  r'records\item\loottables\arms\commondynamic\armband_n03.dbr',
                                  r'records\item\loottables\arms\commondynamic\armband_e03.dbr',
                                  r'records\item\loottables\arms\commondynamic\armband_l03.dbr']),
                              ('LowerBody', 100.0, 5000, [
                                  r'records\item\loottables\legs\commondynamic\greaves_n03.dbr',
                                  r'records\item\loottables\legs\commondynamic\greaves_e03.dbr',
                                  r'records\item\loottables\legs\commondynamic\greaves_l03.dbr']),
                          ]):
        _wire_summon_soul(db, xw_souls, SUMMON_XEIWANG_SKILL, name_tag='tagSVCSoulXeiwang')
        print("  D8 Xeiwang summon-soul: 3 pets from um_xaiweng_48 rig + summon; souls rewired 1/2/3")
    tags['tagSVCSoulXeiwang'] = '{^F}Xeiwang, Flame of Hatred Soul'
    tags['tagSVCSoulXeiwangDESC'] = ('Xeiwang, the flame of undying hatred, boiled into a soul. '
        'Its bearer may call him forth to burn at their side.')
    tags['tagSVCSummonXeiwang'] = 'Summon Xeiwang, Flame of Hatred'

    # ── D9: Huo-ren, the Mountainblade (um_mountainblade_43, Hero L43/59/72). ──
    MB_SRC = r'records\creature\monster\dragonian\um_mountainblade_43.dbr'
    mb_tiers = []
    for t, il, sk, of, op, cs, cd, dfr in [
            ('n', 43, 1, (30.0, 50.0, 25), (28.0, 45.0, 18), 8.0, 6.0, 22.0),
            ('e', 59, 2, (50.0, 80.0, 35), (45.0, 70.0, 26), 11.0, 8.0, 30.0),
            ('l', 72, 3, (80.0, 125.0, 50), (70.0, 110.0, 38), 15.0, 11.0, 38.0)]:
        mb_tiers.append({'diff': t, 'itemLevel': il, 'stats': {
            **_bmp(t),
            'itemSkillName': (S, SUMMON_MOUNTAINBLADE_SKILL), 'itemSkillLevel': (I, sk),
            'offensiveFireMin': (F, of[0]), 'offensiveFireMax': (F, of[1]), 'offensiveFireModifier': (I, of[2]),
            'offensivePhysicalMin': (F, op[0]), 'offensivePhysicalMax': (F, op[1]), 'offensivePhysicalModifier': (I, op[2]),
            'characterStrengthModifier': (F, cs), 'characterDexterityModifier': (F, cd),
            'defensiveFire': (F, dfr)}})
    # _create_soul re-points um_mountainblade_43's lootFinger2Item1 to this new soul
    # (the wrong-drop fix) AND the tiers already set itemSkillName=SUMMON_MOUNTAINBLADE.
    _create_soul(db, 'mountainblade', 'tagSVCSoulMountainBlade', mb_tiers, MB_SRC, 66.0)
    mb_pets = [rf'records\skills\soulskills\pets\mountainblade_{i}.dbr' for i in (1, 2, 3)]
    if _build_boss_summon(db, MB_SRC, mb_pets, SUMMON_MOUNTAINBLADE_SKILL,
                          'tagSVCSummonMountainBlade', 'tagNewHero289',
                          char_level=[43, 59, 72], life=[11000.0, 15000.0, 20000.0],
                          life_regen=[30.0, 55.0, 90.0],
                          dmg_min=[65.0, 100.0, 145.0], dmg_max=[105.0, 160.0, 230.0],
                          # F2: mirror um_mountainblade_43's own armor (Torso @100,
                          # dragonian mastertables, DB-verified) - not naked.
                          # D19 (P1, bone-proven 2026-07-09): the source ALSO
                          # equips RightHand=100 (1h_dyn) + LeftHand=100 (shield)
                          # - the Torso-only loadout left the pet WEAPONLESS on
                          # the unarmed anim row, where anm_dragonian defines NO
                          # RunAnim and the source-copied CrocMan_Run override
                          # binds 2/19 bone tracks on the flameguard/dragonian
                          # skeleton -> nothing playable -> IMMOBILE (Will's
                          # "he doesnt move"). The weapon parks the pet on the
                          # sHanded row (table Dragonian_Run = the exact
                          # configuration the LIVE source hero moves with).
                          loadout=[
                              ('RightHand', 100.0, 5000, [
                                  r'records\item\loottables\weapons\mastertables\1h_dyn_n03.dbr',
                                  r'records\item\loottables\weapons\mastertables\1h_dyn_e03.dbr',
                                  r'records\item\loottables\weapons\mastertables\1h_dyn_l03.dbr']),
                              ('LeftHand', 100.0, 5000, [
                                  r'records\item\loottables\shields\commondynamic\shield_n03.dbr',
                                  r'records\item\loottables\shields\commondynamic\shield_e03.dbr',
                                  r'records\item\loottables\shields\commondynamic\shield_l03.dbr']),
                              ('Torso', 100.0, 5000, [
                                  r'records\item\loottables\torso\mastertables\monster\n_dragonian.dbr',
                                  r'records\item\loottables\torso\mastertables\monster\e_dragonian.dbr',
                                  r'records\item\loottables\torso\mastertables\monster\l_dragonian.dbr']),
                          ]):
        print("  D9 Huo-ren the Mountainblade: WRONG-DROP FIXED (um_mountainblade_43 -> own soul, "
              "was mukesha_soul) + summon-soul + 3 pets from flameguard rig")
    tags['tagSVCSoulMountainBlade'] = '{^F}Huo-ren, the Mountainblade Soul'
    tags['tagSVCSoulMountainBladeDESC'] = ('Huo-ren, the Mountainblade, whose fire never cooled. '
        'Its bearer may call him forth, blade and flame, to fight at their side.')
    tags['tagSVCSummonMountainBlade'] = 'Summon Huo-ren, the Mountainblade'


# ── Q3 (build31, campaign blocker): Olympus -> Rhodes herald NPC ─────────────
# M12 RCA (map lane, in-game confirmed): the base post-Typhon portal's
# destination is ENGINE-INTERNAL and never activates in a Custom Quest; the Q1
# token-gated Action_UnlockFixedItem shipped in build30.3 opened NOTHING for
# Will. Model C fix: a boat-dialog herald NPC on the Typhon summit plateau ->
# Action_BoatDialog to the Rhodes arrival (data-driven world coord, no engine
# hook), exactly the M8 portal-master mechanism. THE RECORD PATH IS LOCKED with
# the map lane (build_section_surgery.py OLYMPUS_RHODES_NPC_SPEC_PENDING wires
# the placement at OlympusFinal02 local (305.80, 90.20, 490.80) once this
# record ships). Donor = knossos_boatmantoegypt: the PROVEN base boat-dialog
# NPC shape (Class=Npc + GreekSailor02 mesh/anims, all base Creatures.arc =
# render-safe per the D5 law); a ferryman-to-Rhodes reads naturally at the
# summit. The boat-dialog quest trigger ships in the SAME wave via
# tools/build_quest_files.py (_add_olympus_rhodes_travel); Text tags ride the
# standard tags mechanism (validate_tags gates them).
OLYMPUS_HERALD_NPC = r'records\quests\portal_master_olympus.dbr'
_OLYMPUS_HERALD_DONOR = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'


def _create_olympus_rhodes_herald(db, tags):
    donor = _find_record(db, _OLYMPUS_HERALD_DONOR)
    if not donor:
        raise SystemExit(f"Q3 herald: donor NPC missing: {_OLYMPUS_HERALD_DONOR}")
    if db.has_record(OLYMPUS_HERALD_NPC):
        raise SystemExit(f"Q3 herald: {OLYMPUS_HERALD_NPC} already exists")
    db.clone_record(donor, OLYMPUS_HERALD_NPC)
    sf = db.set_field
    sf(OLYMPUS_HERALD_NPC, 'description', 'tagSVCNpcOlympusHerald')
    sf(OLYMPUS_HERALD_NPC, 'FileDescription',
       'SVC Q3: Olympus->Rhodes herald (Model C boat-dialog)')
    sf(OLYMPUS_HERALD_NPC, 'messageDialogTag', 'tagSVCOlympusHeraldChat')
    db._modified.add(OLYMPUS_HERALD_NPC)
    tags['tagSVCNpcOlympusHerald'] = 'Keryx, Herald of Olympus'
    tags['tagSVCOlympusHeraldChat'] = ('Typhon has fallen! Zeus bids you '
                                       'onward - the path to Rhodes opens.')
    tags['tagSVCOlympusRhodesTravel'] = 'Travel to Rhodes?'
    print("  Q3 herald: portal_master_olympus.dbr cloned from the Knossos "
          "boatman (proven boat-dialog NPC shape); name/chat/travel tags set")


# ── Q2 (build32, Group A): Helos portal-master for the 4 SV side-areas ───────
# Will chose Model C (boat-dialog NPC) for SV-area travel (BACKLOG Q2). This is
# the twin of the Q3 Olympus herald: a single friendly NPC placed in the Helos
# starting-town portal plaza (map lane build_section_surgery.py
# PORTAL_MASTER_SPEC_PENDING @ startingfarmland06d local (76.50,0.60,189.50))
# whose boat-dialog menu offers all FOUR SV destinations at once. Each
# Action_BoatDialog registered on this NPC adds one destination to its menu
# (base-game precedent: quest 8 registers Knossos->Rhakotis on
# Knossos_BoatmanToEgypt; multiple calls on ONE npc accumulate ports). Donor =
# knossos_boatmantoegypt (the same proven boat-dialog Npc shape the herald uses:
# Class=Npc + GreekSailor02 base art, render-safe per D5). The 4-destination
# boat-dialog trigger ships in the SAME wave via build_quest_files.py
# (_add_helos_portal_travel, appended to the already-registered, always-loaded
# sv_commonmechanics.qst refire step - QUESTS registry law: no new
# registrations). Text tags ride the standard mechanism (validate_tags gates).
PORTAL_MASTER_HELOS_NPC = r'records\quests\portal_master_helos.dbr'
_HELOS_PORTAL_DONOR = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'


def _create_helos_portal_master(db, tags):
    donor = _find_record(db, _HELOS_PORTAL_DONOR)
    if not donor:
        raise SystemExit(f"Q2 portal-master: donor NPC missing: {_HELOS_PORTAL_DONOR}")
    if db.has_record(PORTAL_MASTER_HELOS_NPC):
        raise SystemExit(f"Q2 portal-master: {PORTAL_MASTER_HELOS_NPC} already exists")
    db.clone_record(donor, PORTAL_MASTER_HELOS_NPC)
    sf = db.set_field
    sf(PORTAL_MASTER_HELOS_NPC, 'description', 'tagSVCNpcHelosPortalMaster')
    sf(PORTAL_MASTER_HELOS_NPC, 'FileDescription',
       'SVC Q2: Helos portal-master (Model C boat-dialog, 4 SV areas)')
    sf(PORTAL_MASTER_HELOS_NPC, 'messageDialogTag', 'tagSVCHelosPortalChat')
    db._modified.add(PORTAL_MASTER_HELOS_NPC)
    tags['tagSVCNpcHelosPortalMaster'] = 'Almyros the Wayfarer'
    tags['tagSVCHelosPortalChat'] = ('I have walked the hidden roads of this '
        'land, friend. Name where you would go, and I will set you upon the way.')
    # boat-menu destination labels (one per Action_BoatDialog in the quest)
    tags['tagSVCHelosToGarden'] = 'The Garden of Merchants'
    tags['tagSVCHelosToSecret'] = 'The Secret Place'
    tags['tagSVCHelosToUber'] = 'The Uber Dungeon'
    tags['tagSVCHelosToSparta'] = 'The Sparta Crypt'
    print("  Q2 portal-master: portal_master_helos.dbr cloned from the Knossos "
          "boatman (proven boat-dialog NPC shape); name/chat + 4 destination "
          "menu tags set")


# ── PORTAL RIG (2026-07-10, GROUP 2 unblock): TESTHUB travel rig NPCs ─────────
# Will's flag-gated LOCAL-ONLY travel rig (Model C, BoatDialog portal-master -
# the proven Almyros shape) so he can reach EVERY restored SV area from Helos
# AND from the blood-cave mouth, verify each area (its real gold portals + the
# area content), then return to the normal map. Two NPC records, both cloned
# from the SAME proven boat-dialog donor Almyros/Keryx use (knossos_boatmantoegypt:
# Class=Npc + GreekSailor02 mesh/tex, render-safe per D5 - mesh/baseTexture are
# inherited byte-identical, so the render chain matches the two shipping portal
# masters exactly):
#   svc_testhub_master  - the HUB portal-master. The map lane places it TWICE
#       (Helos plaza + blood-cave-mouth strip, TESTHUB map only). Its boat menu
#       (build_quest_files _add_testhub_portal_travel) offers all 7 ports:
#       Garden, Secret, Uber, Sparta, Boss Arena, Blood Cave interior, Helos.
#   svc_testhub_return  - the RETURN NPC, placed once INSIDE each of the 5 SV
#       destination areas (TESTHUB map only). Its 2-port menu (Helos, Blood Cave)
#       gives every area a deterministic round-trip back to the normal map. This
#       is why Model C beats born-open GridEntrance: BoatDialog is a quest-action
#       teleport, NOT a map portal, so the live-proven appended-host firing gate
#       (a born-open GridEntrance NEVER fires from an appended SV-only host, the
#       shipped B-PORTAL-3 bug) does NOT apply - returns from every SV area WORK.
#
# STEAM-INERTNESS (stated explicitly): both records are added to the arz
# UNCONDITIONALLY, but they are INERT on the canonical/Steam map because the
# canonical map PLACES NEITHER of them (only the TESTHUB Levels variant does).
# An Action_BoatDialog whose `npc` record is not placed in the loaded level has
# no entity to attach its dialog to, so it is a no-op - the exact same
# inert-unless-placed principle the flag design already relies on for the arz's
# TESTHUB-referenced records (the D3 unplaced-record no-op precedent + the
# Almyros shape: a boat-dialog trigger keyed to an NPC the map never places does
# not fire). A negative check (tools/debug/gate_testhub_inert.py) proves the
# canonical map places 0 of these records.
TESTHUB_MASTER_NPC = r'records\quests\svc_testhub_master.dbr'
TESTHUB_RETURN_NPC = r'records\quests\svc_testhub_return.dbr'
_TESTHUB_NPC_DONOR = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'
# build36 A6 (WARDEN SPLIT-FIX): the single svc_testhub_master was PLACED in TWO
# levels (Helos + blood-cave mouth), but Action_BoatDialog binds its menu to ONE
# entity resolved from the record path, so the second instance spawned mute-but-
# visible (byte-proven H1: identical record/trigger, only the double placement
# differs). Split into TWO singly-placed master records (each = the proven single-
# placement boat NPC). Quests + map wave (see docs/reports/build36_laneA_map_needs
# .md) emits a trigger per record + places each once.
TESTHUB_MASTER_HELOS_NPC = r'records\quests\svc_testhub_master_helos.dbr'
TESTHUB_MASTER_CAVE_NPC = r'records\quests\svc_testhub_master_cave.dbr'


def _create_testhub_portal_npcs(db, tags):
    donor = _find_record(db, _TESTHUB_NPC_DONOR)
    if not donor:
        raise SystemExit(f"Portal rig: donor NPC missing: {_TESTHUB_NPC_DONOR}")
    for path, desc_tag, chat_tag, filedesc in (
        (TESTHUB_MASTER_NPC, 'tagSVCNpcTestHubMaster', 'tagSVCTestHubMasterChat',
         'SVC portal rig: TESTHUB hub portal-master (Model C boat-dialog, 7 ports)'),
        (TESTHUB_RETURN_NPC, 'tagSVCNpcTestHubReturn', 'tagSVCTestHubReturnChat',
         'SVC portal rig: TESTHUB return NPC (Model C boat-dialog, Helos + Blood Cave)'),
    ):
        if db.has_record(path):
            raise SystemExit(f"Portal rig: {path} already exists")
        db.clone_record(donor, path)
        db.set_field(path, 'description', desc_tag)
        db.set_field(path, 'FileDescription', filedesc)
        db.set_field(path, 'messageDialogTag', chat_tag)
        db._modified.add(path)
    # NPC name + greeting tags (referenced by the arz records above; validate_tags
    # requires these to resolve in Text.arc).
    tags['tagSVCNpcTestHubMaster'] = 'Waypoint Warden (Test Rig)'
    tags['tagSVCTestHubMasterChat'] = ('I hold every hidden road to the restored '
        'lands. Name your destination and I will set you upon the way.')
    tags['tagSVCNpcTestHubReturn'] = 'Return Warden (Test Rig)'
    tags['tagSVCTestHubReturnChat'] = ('Seen enough? I can set you back on the '
        'road to Helos or to the Blood Cave.')
    # Boat-menu destination labels for the THREE new ports (Garden/Secret/Uber/
    # Sparta reuse the 4 Almyros labels set by _create_helos_portal_master, which
    # always runs just before this). These are referenced by the quest file only.
    tags['tagSVCTestHubToBossArena'] = 'The Boss Arena'
    tags['tagSVCTestHubToBloodCave'] = 'The Blood Cave'
    tags['tagSVCTestHubToHelos'] = 'Helos (Return)'
    # ── build36 A6 (WARDEN SPLIT-FIX): the two singly-placed master records (Helos
    #    + cave), reusing the SAME name/chat tags (no Text change). The map/quests
    #    wave places each once + emits a trigger per record; the original
    #    svc_testhub_master is kept until that wave retires its double placement. ──
    for path, filedesc in (
        (TESTHUB_MASTER_HELOS_NPC,
         'SVC portal rig: TESTHUB Helos master (Model C, split, 7 ports)'),
        (TESTHUB_MASTER_CAVE_NPC,
         'SVC portal rig: TESTHUB blood-cave master (Model C, split, 7 ports)'),
    ):
        if db.has_record(path):
            raise SystemExit(f"Portal rig A6: {path} already exists")
        db.clone_record(donor, path)
        db.set_field(path, 'description', 'tagSVCNpcTestHubMaster')
        db.set_field(path, 'FileDescription', filedesc)
        db.set_field(path, 'messageDialogTag', 'tagSVCTestHubMasterChat')
        db._modified.add(path)
    print("  Portal rig: svc_testhub_master + svc_testhub_return + A6 split masters "
          "(svc_testhub_master_helos/_cave) cloned from the Knossos boatman; name/"
          "chat + 3 new menu tags set (Garden/Secret/Uber/Sparta reuse Almyros)")


# ── GROUP C (build32): Vashkarr, Eldest of the Ancients (N4-DB) ──────────────
# Will signed off (BACKLOG N4-DB): a lone Ancient-Dragonian warlord in the
# Random05A cave east of Chang'an. Identity B - {^r}Vashkarr, Eldest of the
# Ancients, mesh AncientDragonian01.msh; derive the whole kit from the DRAGONIAN
# family for anim-safety (recon: bm_deathlance_32 = the AncientDragonian01
# takedown-melee base; bs_warlock_40 = the AncientDragonianB01 caster champion;
# bm_ravager_31 = the AncientDragonian01 melee brute). Band charLevel [38,56,71],
# HP [12000,16500,21000]. Escort = Vashkarr + 2 full-strength dragonian
# champions ALWAYS (pool spawnMax=3 / championChance=100 / championMin=Max=2 ->
# 3-2 = 1 guaranteed main slot; the spawnMax-championMax>=1 law holds). Minions:
# a frequent dragonian-fodder summon on his kit (yaoguai_summonshadowstalkers
# clone, burst 3 / ~6s). Proxy q_vashkarr_lone (chanceToRun=100) + pool staged in
# drxmap\proxy(\pools) per the q_bloodtoxeus_lone precedent; difficultyLimitsFile
# = herolimit_all (no-cap, [1..75] already contains the band). SOUL = STAT-ONLY,
# no summon ("it can just be really good"): a dense aggressive fire/physical
# ladder, 66% Finger2, {^F} tag. MAP-REF-1: these records land in the arz BEFORE
# the map lane injects the placement + the v0e routing case.
_VK_MONSTER = r'records\creature\monster\dragonian\um_vashkarr_99.dbr'
_VK_DONOR = r'records\creature\monster\dragonian\bm_deathlance_32.dbr'         # AncientDragonian01, takedown melee
_VK_FODDER = r'records\creature\monster\dragonian\svc_vashkarr_fodder.dbr'      # laddered dragonian minion
_VK_FODDER_DONOR = r'records\creature\monster\dragonian\bm_ravager_31.dbr'      # AncientDragonian01 melee brute
_VK_ESCORT_MELEE = r'records\creature\monster\dragonian\svc_vashkarr_lance.dbr'  # Champion melee escort
_VK_ESCORT_CASTER = r'records\creature\monster\dragonian\svc_vashkarr_warlock.dbr'  # Champion caster escort
_VK_ESCORT_CASTER_DONOR = r'records\creature\monster\dragonian\bs_warlock_40.dbr'   # AncientDragonianB01 caster champ
_VK_MINION_SUMMON = r'records\skills\boss skills\svc_vashkarr_summonhorde.dbr'
_VK_SUMMON_DONOR = r'records\skills\boss skills\yaoguai_summonshadowstalkers.dbr'   # Skill_SpawnPetMonster
_VK_PROXY = r'records\drxmap\proxy\q_vashkarr_lone.dbr'
_VK_POOL = r'records\drxmap\proxy\pools\q_vashkarr_lone.dbr'
_VK_PROXY_DONOR = r'records\drxmap\proxy\q_leinth_lone.dbr'
_VK_POOL_DONOR = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_VK_LIMIT = r'records\proxies boss\herolimit_all.dbr'   # no-cap [1..75] contains [38,56,71]
_VK_BAND = [38, 56, 71]
# Kit skill refs (all dragonian-family, existence-verified in recon).
_VK_SK_TAKEDOWN = r'records\skills\hunting\takedown.dbr'
_VK_SK_EVISCERATE = r'records\skills\hunting\takedown_eviscerate.dbr'
_VK_SK_DMGMOD = r'records\skills\monster skills\passive_buffs\attack_damagemodifier_02.dbr'
_VK_SK_SPEEDALL = r'records\skills\monster skills\auras\character_speedall.dbr'
_VK_SK_SHIELDCHARGE = r'records\skills\defensive\shieldcharge.dbr'
_VK_SK_DEFLECT = r'records\skills\monster skills\defense\deflectprojectiles_passive.dbr'
_VK_SK_MELEE = r'records\skills\monster skills\attack_melee\meleeattack_+3physicalandfireperlvlx100.dbr'
_VK_SK_BOSSIMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_VK_SK_BOSSSCALING = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
_VK_SK_GP_N = r'records\skills\monster skills\globalproperties_normal01.dbr'
_VK_SK_GP_E = r'records\skills\monster skills\globalproperties_epic01.dbr'
_VK_SK_GP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'


def _create_vashkarr(db, tags):
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    # ── 1. The minion-summon skill (clone the yaoguai donor; keep its field
    #    SHAPE - only change existing fields, so it stays loader-safe and is
    #    registered with the boss-kit clone invariant). ──
    if not db.has_record(_VK_SUMMON_DONOR):
        print("  VASHKARR: WARNING summon donor missing; group skipped")
        return
    if not db.has_record(_VK_FODDER_DONOR):
        print("  VASHKARR: WARNING fodder donor missing; group skipped")
        return

    # Fodder monster (laddered dragonian brute) - author BEFORE the summon skill
    # references it. Clone bm_ravager_31 (AncientDragonian01 melee, anim-safe).
    db.clone_record(_VK_FODDER_DONOR, _VK_FODDER)
    sf(_VK_FODDER, 'charLevel', list(_VK_BAND))              # INT array preserved
    sf(_VK_FODDER, 'characterLife', [900.0, 1400.0, 1900.0])  # fodder-tier
    sf(_VK_FODDER, 'monsterClassification', 'Common')        # Common -> no soul drop, fodder
    sf(_VK_FODDER, 'dropItems', 0)
    db._modified.add(_VK_FODDER)

    db.clone_record(_VK_SUMMON_DONOR, _VK_MINION_SUMMON)
    sf(_VK_MINION_SUMMON, 'spawnObjects', [_VK_FODDER])       # existing field -> repoint
    sf(_VK_MINION_SUMMON, 'petBurstSpawn', 3)                 # burst 3 per cast (design)
    sf(_VK_MINION_SUMMON, 'skillCooldownTime', 6.0)          # ~6s (design)
    sf(_VK_MINION_SUMMON, 'petLimit', 12)                    # "many minions"
    db._modified.add(_VK_MINION_SUMMON)
    _BOSS_KIT_CLONES.append((_VK_SUMMON_DONOR, _VK_MINION_SUMMON))

    # ── 2. Vashkarr (the boss). Clone bm_deathlance_32 (AncientDragonian01
    #    takedown-melee); override identity/power/kit. Monster.tpl clone -> free
    #    to add resist fields (blood_toxeus precedent). ──
    db.clone_record(_VK_DONOR, _VK_MONSTER)
    M = _VK_MONSTER
    sf(M, 'description', 'tagSVCMonsterVashkarr')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'charLevel', list(_VK_BAND))
    sf(M, 'characterLife', [12000.0, 16500.0, 21000.0])
    sf(M, 'characterStrength', 460.0)
    sf(M, 'characterDexterity', 380.0)
    sf(M, 'characterIntelligence', 300.0)
    sf(M, 'characterLifeRegen', 12.0)
    sf(M, 'handHitDamageMin', 90.0)
    sf(M, 'handHitDamageMax', 150.0)
    sf(M, 'scale', 1.55)                                      # visibly the Eldest
    sf(M, 'actorHeight', 2.0)
    # boss resistance wall (new fields auto-FLOAT on the Monster.tpl clone)
    sf(M, 'defensivePierce', 55.0)
    sf(M, 'defensiveFire', 70.0)                              # dragonfire kin
    sf(M, 'defensivePhysical', 30.0)
    sf(M, 'defensiveLife', 90.0)
    # kit: dragonian melee + frequent horde summon + boss passives (anim-safe;
    # attackSkillName gives him a real scaling basic melee - the deathlance donor
    # had none). All refs existence-verified.
    sf(M, 'attackSkillName', _VK_SK_MELEE)
    sf(M, 'skillName1', _VK_SK_TAKEDOWN)
    sf(M, 'skillName2', _VK_SK_EVISCERATE)
    sf(M, 'skillName3', _VK_SK_DMGMOD)
    sf(M, 'skillName4', _VK_SK_SPEEDALL)
    sf(M, 'skillName5', _VK_MINION_SUMMON)                    # the horde
    sf(M, 'skillName6', _VK_SK_SHIELDCHARGE)                  # gap-closer
    sf(M, 'skillName7', _VK_SK_DEFLECT)
    sf(M, 'skillName8', _VK_SK_BOSSIMMUNITY)
    sf(M, 'skillName9', _VK_SK_BOSSSCALING)
    sf(M, 'skillName10', _VK_SK_GP_N)
    sf(M, 'skillName11', _VK_SK_GP_E)
    sf(M, 'skillName12', _VK_SK_GP_L)
    # AI rotation: summon the horde often, takedown as the signature special.
    sf(M, 'specialAttackSkillName', _VK_MINION_SUMMON)
    sf(M, 'specialAttackChance', 55.0)
    sf(M, 'specialAttack2SkillName', _VK_SK_TAKEDOWN)
    sf(M, 'specialAttack2Chance', 45.0)
    db._modified.add(M)

    # ── 3. Two full-strength dragonian champion escorts (laddered [38,56,71]). ──
    db.clone_record(_VK_FODDER_DONOR, _VK_ESCORT_MELEE)      # ravager melee brute
    sf(_VK_ESCORT_MELEE, 'description', 'tagSVCMonsterVashkarrLance')
    sf(_VK_ESCORT_MELEE, 'monsterClassification', 'Champion')
    sf(_VK_ESCORT_MELEE, 'charLevel', list(_VK_BAND))
    sf(_VK_ESCORT_MELEE, 'characterLife', [3000.0, 4500.0, 6000.0])
    sf(_VK_ESCORT_MELEE, 'characterStrength', 300.0)
    sf(_VK_ESCORT_MELEE, 'handHitDamageMin', 60.0)
    sf(_VK_ESCORT_MELEE, 'handHitDamageMax', 100.0)
    sf(_VK_ESCORT_MELEE, 'dropItems', 0)
    db._modified.add(_VK_ESCORT_MELEE)

    if db.has_record(_VK_ESCORT_CASTER_DONOR):
        db.clone_record(_VK_ESCORT_CASTER_DONOR, _VK_ESCORT_CASTER)  # warlock caster
        sf(_VK_ESCORT_CASTER, 'description', 'tagSVCMonsterVashkarrWarlock')
        sf(_VK_ESCORT_CASTER, 'monsterClassification', 'Champion')
        sf(_VK_ESCORT_CASTER, 'charLevel', list(_VK_BAND))
        sf(_VK_ESCORT_CASTER, 'characterLife', [2500.0, 3800.0, 5000.0])
        sf(_VK_ESCORT_CASTER, 'characterIntelligence', 340.0)
        sf(_VK_ESCORT_CASTER, 'dropItems', 0)
        db._modified.add(_VK_ESCORT_CASTER)
    else:
        print("  VASHKARR: WARNING warlock escort donor missing; using melee escort twice")

    # ── 4. Proxy + pool (q_bloodtoxeus_lone precedent; boss + 2 guaranteed
    #    champion escorts via spawnMax=3 / champMin=Max=2). ──
    if db.has_record(_VK_PROXY_DONOR) and db.has_record(_VK_POOL_DONOR):
        db.clone_record(_VK_POOL_DONOR, _VK_POOL)
        PL = _VK_POOL
        sf(PL, 'FileDescription', 'Vashkarr (main) + 2 dragonian champion escorts')
        sf(PL, 'name1', _VK_MONSTER)
        sf(PL, 'name2', _VK_MONSTER)
        sf(PL, 'name3', _VK_MONSTER)
        sf(PL, 'nameChampion1', _VK_ESCORT_MELEE)
        sf(PL, 'nameChampion2', _VK_ESCORT_CASTER if db.has_record(_VK_ESCORT_CASTER)
           else _VK_ESCORT_MELEE)
        # Clear the q_leinth_lone clone-leftover THIRD champion (an off-theme
        # Common records\drxcreatures\blooddemon\b_med_blooddemon_32.dbr at w33):
        # with championMin=Max=2 the escorts roll 2-of-3, so ~2/3 of encounters
        # dropped a real lieutenant for the blood demon. Empty the slot + zero its
        # weight, and rebalance the two real escorts to 50/50 -> ALWAYS exactly
        # lance + warlock. (No explicit dtypes: the cloned fields keep STRING/INT.)
        sf(PL, 'nameChampion3', '')
        sf(PL, 'weightChampion1', 50)
        sf(PL, 'weightChampion2', 50)
        sf(PL, 'weightChampion3', 0)
        sf(PL, 'spawnMin', 3)
        sf(PL, 'spawnMax', 3)
        sf(PL, 'championChance', 100.0)
        sf(PL, 'championMin', 2)
        sf(PL, 'championMax', 2)
        db._modified.add(PL)

        db.clone_record(_VK_PROXY_DONOR, _VK_PROXY)
        P = _VK_PROXY
        sf(P, 'mesh', r'Creatures\Monster\Dragonian\AncientDragonian01.msh')  # preview silhouette
        sf(P, 'scale', 1.55)
        sf(P, 'pool1', _VK_POOL)
        sf(P, 'chanceToRun', 100.0)
        sf(P, 'difficultyLimitsFile', _VK_LIMIT)             # no-cap [1..75] contains the band
        db._modified.add(P)
        print("  Vashkarr proxy + pool: 1 boss + 2 dragonian champions "
              "(spawn=3/champMin=Max=2/champChance=100); chanceToRun=100")
    else:
        print("  VASHKARR: WARNING q_leinth_lone proxy/pool donor missing; proxy skipped")

    # ── 5. Stat-only soul (no summon; dense aggressive fire/physical ladder). ──
    def _vk_stats(t, il):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        return {
            **_bmp(t),
            'augmentSkillName1': (S, _SK_FIRE_ENCHANT), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _SK_ONSLAUGHT), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(280.0)), 'characterLifeModifier': (F, r(10.0)),
            'characterStrength': (F, r(30.0)), 'characterStrengthModifier': (F, r(8.0)),
            'characterOffensiveAbility': (F, r(90.0)),
            'characterAttackSpeedModifier': (F, r(16.0)),
            'offensivePhysicalMin': (F, r(60.0)), 'offensivePhysicalMax': (F, r(95.0)),
            'offensivePhysicalModifier': (F, r(35.0)),
            'offensiveFireMin': (F, r(50.0)), 'offensiveFireMax': (F, r(80.0)),
            'offensiveFireModifier': (F, r(30.0)),
            'offensiveSlowBleedingMin': (F, r(120.0)), 'offensiveSlowBleedingDurationMin': (F, 3.0),
            'offensiveLifeLeechMin': (F, r(25.0)),
            'defensivePhysical': (F, r(140.0)), 'defensiveBleeding': (F, r(30.0)),
            'defensiveFire': (F, r(25.0)), 'defensiveLife': (F, r(20.0)),
            'characterDefensiveAbility': (F, r(60.0)),
        }
    tiers = [{'diff': t, 'itemLevel': il, 'stats': _vk_stats(t, il)}
             for t, il in (('n', 38), ('e', 56), ('l', 71))]
    _create_soul(db, 'vashkarr', 'tagSVCSoulVashkarr', tiers, monster=_VK_MONSTER, drop_rate=66.0)

    tags['tagSVCMonsterVashkarr'] = '{^r}Vashkarr, Eldest of the Ancients'
    tags['tagSVCMonsterVashkarrLance'] = '{^r}Ancient Lancer of the Deep'
    tags['tagSVCMonsterVashkarrWarlock'] = '{^r}Ancient Warlock of the Deep'
    tags['tagSVCSoulVashkarr'] = '{^F}Soul of the Eldest'
    tags['tagSVCSoulVashkarrDESC'] = ('Torn from Vashkarr, Eldest of the Ancients, '
        'the last warlord of the dragonian race. It burns with the fury of an age '
        'the world has forgotten.')
    print("  Vashkarr: boss + fodder + 2 champion escorts + horde summon "
          "(burst 3/~6s) + stat-only soul (66% Finger2); tags set")


# ── build36 A5 (Will 2026-07-11): PROPONTIS SUPER BOSS - Dorus, the Drowned King
#    (DB side only; map lane places the proxy per docs/reports/build36_laneA_map_
#    needs.md). The risen last king of Propontis, guarding the fortune the xSQ06
#    treasure quest sends every hero after. Derived from the questline King Dorus
#    shade (xsq06_king_dorus_41, the crowned drowned-king royalty rig, anim-safe:
#    already casts Hero_ThunderClap/Thunderball) -> a Boss 7x his weight who raises
#    his whole court out of the sarcophagi. Vashkarr/broodmother recipe. S1 dense
#    STAT soul (Vashkarr precedent, NO summon). Hoard = a Boss-locked mega-chest
#    (reuses the proven Obsidian Hoard chest/pool records -> zero new loot tables).
_DK_BOSS = r'records\xpack\creatures\monster\lostsoul\um_dorus_99.dbr'
_DK_DONOR = r'records\xpack\creatures\monster\lostsoul\xsq06_king_dorus_41.dbr'
_DK_COURTIER = r'records\xpack\creatures\monster\lostsoul\svc_dorus_courtier_71.dbr'
_DK_COURTIER_DONOR = r'records\xpack\creatures\monster\lostsoul\xsq06_lostsoul_courtier_34.dbr'
_DK_ROYALGUARD = r'records\xpack\creatures\monster\lostsoul\svc_dorus_royalguard_71.dbr'
_DK_ROYALGUARD_DONOR = r'records\xpack\creatures\monster\lostsoul\xsq06_lostsoul_nobleman_39.dbr'
_DK_SUMMON = r'records\skills\boss skills\svc_dorus_raisecourt.dbr'
_DK_SUMMON_DONOR = r'records\skills\boss skills\yaoguai_summonshadowstalkers.dbr'
_DK_POOL = r'records\drxmap\proxy\pools\q_dorus_lone.dbr'
_DK_PROXY = r'records\drxmap\proxy\q_dorus_lone.dbr'
_DK_POOL_DONOR = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_DK_PROXY_DONOR = r'records\drxmap\proxy\q_leinth_lone.dbr'
_DK_LIMIT = r'records\proxies orient\limit_obsidianbosses.dbr'   # no-cap [1..110] contains L71
_DK_DIFFICULTY = r'records\proxies orient\difficulty_04.dbr'
_DK_HOARD = {t: r'records\drxitem\container\svc_dorushoard_%s.dbr' % t for t in ('01', '02', '03')}
_DK_HOARD_DONOR = {t: r'records\drxitem\container\svc_obsidianhoard_%s.dbr' % t for t in ('01', '02', '03')}
_DK_HOARD_POOL = {t: r'records\drxitem\container\svc_dorushoard_pool_%s.dbr' % t for t in ('01', '02', '03')}
_DK_HOARD_POOL_DONOR = {t: r'records\drxitem\container\svc_obsidianhoard_pool_%s.dbr' % t for t in ('01', '02', '03')}
_DK_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_dorus.dbr'
_DK_YARD_PROXY = r'records\drxmap\proxy\q_yard_dorus.dbr'
_DK_BAND = [41, 57, 71]
_DK_MESH = r'XPack\Creatures\Monster\Zombie\xSQ06_Royalty_NonQuest.msh'
_DK_SK_CONVIMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_DK_SK_GP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'


def _create_propontis_superboss(db, tags):
    """A5: Dorus, the Drowned King - Propontis super boss (DB side). Runs AFTER
    _create_obsidian_roulette (the hoard reuses its Boss-locked chest/pool
    records). Vashkarr/broodmother idiom: clone donors, override existing fields
    only on kit clones, _modified.add, fail-loud on missing donors."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field
    for donor in (_DK_DONOR, _DK_COURTIER_DONOR, _DK_ROYALGUARD_DONOR,
                  _DK_SUMMON_DONOR, _DK_POOL_DONOR, _DK_PROXY_DONOR,
                  _DK_HOARD_DONOR['01'], _DK_HOARD_POOL_DONOR['01']):
        if not db.has_record(donor):
            print(f"  PROPONTIS: WARNING donor missing: {donor}; group skipped")
            return

    # ── 1. The raise-the-court summon (uncapped burst; yaoguai clone -> only
    #    existing fields changed -> loader-safe + boss-kit clone-shape invariant).
    #    Spawns PURE Common courtier fodder (no soul/scale spam); the 2 guaranteed
    #    champion escorts come from the pool. ──
    db.clone_record(_DK_SUMMON_DONOR, _DK_SUMMON)
    sf(_DK_SUMMON, 'spawnObjects', [_DK_COURTIER])
    sf(_DK_SUMMON, 'petBurstSpawn', 3)
    sf(_DK_SUMMON, 'skillCooldownTime', 5.0)
    sf(_DK_SUMMON, 'petLimit', 20)                       # "no cap" in spirit
    db._modified.add(_DK_SUMMON)
    _BOSS_KIT_CLONES.append((_DK_SUMMON_DONOR, _DK_SUMMON))

    # ── 2. The Common courtier fodder (laddered to the band, no soul). ──
    db.clone_record(_DK_COURTIER_DONOR, _DK_COURTIER)
    sf(_DK_COURTIER, 'charLevel', list(_DK_BAND))
    sf(_DK_COURTIER, 'monsterClassification', 'Common')
    sf(_DK_COURTIER, 'characterLife', [900.0, 1400.0, 1900.0])
    sf(_DK_COURTIER, 'dropItems', 0)
    db._modified.add(_DK_COURTIER)

    # ── 3. The Champion royal-guard escort (laddered; keeps its court-necromancer
    #    lifedrain-ward summon, on-theme). ──
    db.clone_record(_DK_ROYALGUARD_DONOR, _DK_ROYALGUARD)
    sf(_DK_ROYALGUARD, 'description', 'tagSVCMonsterDorusGuard')
    sf(_DK_ROYALGUARD, 'monsterClassification', 'Champion')
    sf(_DK_ROYALGUARD, 'charLevel', list(_DK_BAND))
    sf(_DK_ROYALGUARD, 'characterLife', [2600.0, 3800.0, 5000.0])
    sf(_DK_ROYALGUARD, 'dropItems', 0)
    db._modified.add(_DK_ROYALGUARD)

    # ── 4. THE KING (boss). Clone the questline Dorus shade; keep its anim-safe
    #    ThunderClap/Thunderball kit + royalty rig, upgrade Hero->Boss, add the
    #    raise-court summon + boss passives + the resist wall. Monster.tpl clone ->
    #    free to add resist fields (Vashkarr precedent). ──
    db.clone_record(_DK_DONOR, _DK_BOSS)
    M = _DK_BOSS
    sf(M, 'description', 'tagSVCMonsterDrownedKing')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'mesh', _DK_MESH)                              # crowned drowned-king rig (explicit)
    sf(M, 'charLevel', list(_DK_BAND))
    sf(M, 'characterLife', [13500.0, 18500.0, 24000.0]) # between Vashkarr and Toxeus
    sf(M, 'characterLifeRegen', [12.0, 24.0, 40.0])
    sf(M, 'scale', 1.6)                                  # looms over his court
    sf(M, 'actorHeight', 2.0)
    # boss resistance wall (he IS a bloated corpse; new fields auto-FLOAT)
    sf(M, 'defensiveLife', 100.0)                        # vitality
    sf(M, 'defensivePierce', 55.0)
    sf(M, 'defensivePhysical', 30.0)
    sf(M, 'defensiveBleeding', 40.0)
    # ADD to the donor's kit (skillName1-4 + 10-12 used; 5-9 free): the raise-court
    # summon + boss immunity + legendary globals. Keep ThunderClap/Thunderball etc.
    sf(M, 'skillName5', _DK_SUMMON)
    sf(M, 'skillName6', _DK_SK_CONVIMMUNITY)
    sf(M, 'skillName7', _DK_SK_GP_L)
    # AI: he raises the court OFTEN (specialAttack1/2 = the donor's Thunder casts).
    sf(M, 'specialAttack3SkillName', _DK_SUMMON)
    sf(M, 'specialAttack3Chance', 55.0)
    db._modified.add(M)

    # ── 5. Lone-boss pool: 1 king + 2 guaranteed royal-guard escorts (spawnMax=3 /
    #    championMin=Max=2 -> 3-2=1 guaranteed main = the king; LAW holds). Clear
    #    the leinth clone-leftover 3rd champion (Vashkarr fix). ──
    def _dorus_pool(pool_path, desc):
        db.clone_record(_DK_POOL_DONOR, pool_path)
        sf(pool_path, 'FileDescription', desc)
        sf(pool_path, 'name1', _DK_BOSS)
        sf(pool_path, 'name2', _DK_BOSS)
        sf(pool_path, 'name3', _DK_BOSS)
        sf(pool_path, 'nameChampion1', _DK_ROYALGUARD)
        sf(pool_path, 'nameChampion2', _DK_ROYALGUARD)
        sf(pool_path, 'nameChampion3', '')
        sf(pool_path, 'weightChampion1', 50)
        sf(pool_path, 'weightChampion2', 50)
        sf(pool_path, 'weightChampion3', 0)
        sf(pool_path, 'spawnMin', 3); sf(pool_path, 'spawnMax', 3)
        sf(pool_path, 'championChance', 100.0)
        sf(pool_path, 'championMin', 2); sf(pool_path, 'championMax', 2)
        db._modified.add(pool_path)
    _dorus_pool(_DK_POOL, 'Dorus (main) + 2 royal-guard champion escorts')

    # ── 6. The hoard: reuse the proven Obsidian Hoard Boss-locked chest + pool
    #    records (locked=1 / Boss / radius 50 / gold gen 100 / rich loot). No new
    #    loot tables; the blood-cave mega chest stays the crown. ──
    for t in ('01', '02', '03'):
        db.clone_record(_DK_HOARD_DONOR[t], _DK_HOARD[t])
        sf(_DK_HOARD[t], 'FileDescription', "Dorus's Hoard (Boss-locked king's ransom)")
        db._modified.add(_DK_HOARD[t])
        db.clone_record(_DK_HOARD_POOL_DONOR[t], _DK_HOARD_POOL[t])
        sf(_DK_HOARD_POOL[t], 'fixedItemName1', _DK_HOARD[t])
        db._modified.add(_DK_HOARD_POOL[t])

    # ── 7. Proxy (q_leinth_lone precedent) - the king + 2 escorts, chanceToRun 100,
    #    no-cap limit, royalty preview mesh, hoard chest as the accessory. ──
    def _dorus_proxy(proxy_path, pool_ref):
        db.clone_record(_DK_PROXY_DONOR, proxy_path)
        sf(proxy_path, 'mesh', _DK_MESH)                # preview silhouette
        sf(proxy_path, 'scale', 1.6)
        sf(proxy_path, 'pool1', pool_ref)
        sf(proxy_path, 'chanceToRun', 100.0)
        sf(proxy_path, 'difficultyLimitsFile', _DK_LIMIT)
        sf(proxy_path, 'difficultyEquationFile', _DK_DIFFICULTY)
        sf(proxy_path, 'placementExtents', 4.0)
        db._modified.add(proxy_path)
    _dorus_proxy(_DK_PROXY, _DK_POOL)
    sf(_DK_PROXY, 'accessory1', _DK_HOARD_POOL['01'], S)
    sf(_DK_PROXY, 'accessoryEpic1', _DK_HOARD_POOL['02'], S)
    sf(_DK_PROXY, 'accessoryLegendary1', _DK_HOARD_POOL['03'], S)

    # ── 8. S1 dense STAT soul (Vashkarr precedent: NO summon, a king's-ransom
    #    sheet; ONLY the king drops it at 66% Finger2). ──
    def _dk_stats(t, il):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        return {
            **_bmp(t),
            'augmentSkillName1': (S, _SK_ONSLAUGHT), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _SK_DEATH_CHILL), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(340.0)), 'characterLifeModifier': (F, r(12.0)),
            'characterStrength': (F, r(35.0)), 'characterStrengthModifier': (F, r(8.0)),
            'characterOffensiveAbility': (F, r(100.0)), 'characterDefensiveAbility': (F, r(70.0)),
            'offensivePhysicalMin': (F, r(70.0)), 'offensivePhysicalMax': (F, r(110.0)),
            'offensivePhysicalModifier': (F, r(35.0)),
            'offensiveLifeMin': (F, r(50.0)), 'offensiveLifeMax': (F, r(80.0)),   # vitality
            'offensiveLifeModifier': (F, r(30.0)),
            'offensivePercentCurrentLifeMin': (F, r(3.0)),   # the bloated king tears current-life
            'offensiveLifeLeechMin': (F, r(30.0)),
            'offensiveFearMin': (F, 2.0),        # weird signature: the drowned dead make the living flee
            'defensiveLife': (F, r(25.0)), 'defensivePierce': (F, r(30.0)),
            'defensiveBleeding': (F, r(30.0)),
        }
    tiers = [{'diff': t, 'itemLevel': il, 'stats': _dk_stats(t, il)}
             for t, il in (('n', 41), ('e', 57), ('l', 71))]
    _create_soul(db, 'drowned_king', 'tagSVCSoulDrownedKing', tiers,
                 monster=_DK_BOSS, drop_rate=66.0)

    # ── 9. TESTHUB yard pool + proxy (king + 2 escorts @100%; SVC_TEST_HUB-gated
    #    placement; REAL records, so tuning the king tunes the yard 1:1). ──
    _dorus_pool(_DK_YARD_POOL, 'YARD: Dorus + 2 royal-guard escorts @100% (TESTHUB-only)')
    _dorus_proxy(_DK_YARD_PROXY, _DK_YARD_POOL)

    tags['tagSVCMonsterDrownedKing'] = '{^r}Dorus, the Drowned King'
    tags['tagSVCMonsterDorusGuard'] = '{^r}Drowned Royal Guard'
    tags['tagSVCSoulDrownedKing'] = '{^F}Soul of the Drowned King'
    tags['tagSVCSoulDrownedKingDESC'] = (
        'Torn from Dorus, the last king of Propontis, who hoarded a fortune and '
        'drowned with it. His soul is bloated with the coin he died clutching and '
        'the cold patience of a corpse that never let go.')
    print("  A5 Propontis: Dorus the Drowned King (Boss [41,57,71] HP 13.5/18.5/24k, "
          "royalty rig, ThunderClap/ball + raise-court summon burst3/petLimit20) + "
          "Common courtier fodder + Champion royal-guard escort + lone pool/proxy "
          "(1 king + 2 escorts) + Boss-locked hoard (Obsidian-chest reuse) + dense "
          "stat soul (66% Finger2) + TESTHUB yard; tags set. Map lane places it.")


# ── GROUP 4 (build31, overnight run): D13/D14/D20/D21 summon-the-boss souls ──
def _mirror_source_loadout(db, source, strict=False):
    """Build a _build_boss_summon loadout that mirrors the SOURCE monster's own
    equip slots (D19 law generalized: hands mirrored -> the pet lives on a
    weaponed, table-covered anim row). Only slots with chance>0 AND an Item1
    that is a \\loottables\\ table (the F2 proven auto-equip path) or a
    creature-namespace monster armor piece (defaultHeadPiece class) are
    mirrored; player unique/set tables are skipped.

    strict (build36 A1 pet-gear-parity): when a source slot has chance>0 but its
    loot is an \\svc\\/\\unique\\ table (would spawn the pet NAKED), substitute a
    slot-appropriate COMMON table (_GEAR_SUBSTITUTE) instead of dropping the slot,
    so the pet carries EXACTLY the gear-slots the source carries (Will's law)."""
    def val(f):
        v = db.get_field_value(source, f)
        if isinstance(v, list):
            return v
        return [v] if v is not None else None

    out = []
    for slot in _GEAR_SLOTS:
        ch = val('chanceToEquip%s' % slot)
        try:
            chance = float(ch[0]) if ch else 0.0
        except (TypeError, ValueError):
            chance = 0.0
        if chance <= 0:
            continue
        items = val('loot%sItem1' % slot)
        paths = [str(x) for x in (items or []) if isinstance(x, str) and x.strip()]
        ok = [x for x in paths
              if '\\loottables\\' in x.replace('/', '\\').lower()
              and '\\unique' not in x.replace('/', '\\').lower()
              and '\\svc\\' not in x.replace('/', '\\').lower()]
        if paths and len(ok) == len(paths) and len(ok) in (1, 3):
            if len(ok) == 1:
                ok = ok * 3
            out.append((slot, 100.0, 5000, ok))
        elif strict and slot in _GEAR_SUBSTITUTE:
            # source equips an \svc\/\unique\ (naked-pet) table here -> keep the
            # slot filled with a common substitute (bloodtoxeus RightHand=svc\
            # crimsonverdict / LeftHand=svc\bleed_affix -> the Devourer pet keeps
            # its weapon + offhand instead of fighting bare-fisted).
            out.append((slot, 100.0, 5000, list(_GEAR_SUBSTITUTE[slot])))
    # direct headpiece (pygmalion class): a creature-namespace armor .dbr
    hp = val('defaultHeadPiece')
    if hp and isinstance(hp[0], str) and hp[0].strip() \
            and not any(sl == 'Head' for sl, _c, _w, _p in out):
        out.append(('Head', 100.0, 5000, [str(hp[0])] * 3))
    return out or None


def _all_pet_records(db):
    """Every soul pet record under \\skills\\soulskills\\pets\\."""
    for n in db.record_names():
        nl = n.replace('/', '\\').lower()
        if '\\soulskills\\pets\\' in nl and nl.endswith('.dbr'):
            yield n


def _fix_sv_pet_summons(db):
    """build36 A1 (per-pet skill fixes): GLOBAL sweep - relocate every friendly
    Skill_SpawnPet wired into a non-AI slot on ANY soul pet into a free
    specialAttack slot so it actually casts. Fixes the SV-original 'never summons'
    pets the _build_boss_summon skill-kit mirror does not touch (Aquardia's
    coral_crabsummon + Dayria's carrionbirdsummons in buffSelf slots) alongside
    the _build_boss_summon products. Idempotent; run after every pet is built."""
    swept = fixed = 0
    for p in _all_pet_records(db):
        swept += 1
        if _relocate_pet_buffslot_summon(db, p):
            fixed += 1
    print(f"  A1 pet-summon relocation: swept {swept} soul pets, relocated buff-slot "
          f"summon(s) into AI-fired slots on {fixed} pet(s)")


# ── build36 A1: THREE fail-loud pet gates (parity / gear / skill-kit) ─────────
def _verify_summon_pet_parity(db, pairs):
    """PET-STAT-MIRROR gate (fail-loud). Every _build_boss_summon pet must mirror
    its source monster's attack/locomotion cadence + primary attributes. PASS iff
    each mirrored stat is >= threshold x the source's, with hard Lyia-archer-clone
    fingerprint tripwires (atkSpd 0.5 / DEX 81 / STR 44 / INT 17 vs a stronger
    source = the exact un-mirrored bug). Negative-tested against baseline (flags
    all 30); green after the builder mirror."""
    checks = [('characterAttackSpeed', 0.95), ('characterRunSpeed', 0.90),
              ('characterSpellCastSpeed', 0.90), ('characterDexterity', 0.90),
              ('characterStrength', 0.90), ('characterIntelligence', 0.90)]
    trips = [('characterAttackSpeed', 0.5, 0.6), ('characterDexterity', 81, 100),
             ('characterStrength', 44, 60), ('characterIntelligence', 17, 30)]

    def fv(rec, f):
        v = db.get_field_value(rec, f)
        v = v[0] if isinstance(v, list) else v
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    problems = []
    for src_path, pets in pairs:
        src = _resolve_record(db, src_path)
        if not src:
            continue
        for p in pets:
            pr = _resolve_record(db, p)
            if not pr:
                continue
            for f, ratio in checks:
                sv, pv = fv(src, f), fv(pr, f)
                if sv is None or sv <= 0:
                    continue
                if pv is None or pv < ratio * sv:
                    problems.append((p, f, pv, sv, 'below %.2fx source' % ratio))
            for f, bad, thr in trips:
                sv, pv = fv(src, f), fv(pr, f)
                if pv is not None and sv is not None and abs(pv - bad) < 1e-6 and sv > thr:
                    problems.append((p, f, pv, sv, 'Lyia fingerprint'))
    if problems:
        for p, f, pv, sv, why in problems[:40]:
            print(f"  PET-STAT-MIRROR OFFENDER: {p.rsplit(chr(92), 1)[-1]} :: "
                  f"{f} pet={pv} src={sv} ({why})")
        raise SystemExit(f"PET-STAT-MIRROR gate FAILED: {len(problems)} stat-parity "
                         f"violation(s) across {len(pairs)} summon families")
    print(f"  PET-STAT-MIRROR gate OK: {len(pairs)} summon families mirror source "
          f"cadence + attributes (no Lyia archer-clone fingerprint)")


def _verify_summon_pet_gear(db, pairs):
    """PET-GEAR-PARITY gate (fail-loud; Will's verbatim law). A summoned pet
    carries EXACTLY the gear its source form carries - no more, no less. STRICT +
    TWO-WAY per slot: if source.chanceToEquip<S> > 0 the pet MUST equip S (else it
    is bare-fisted/naked); if source.chanceToEquip<S> == 0 the pet must NOT (else
    it over-adds gear the source lacks - the Xeiwang case). Negative-tested against
    baseline (flags bloodtoxeus/toxeus_enslaver/enslaver_marauder bare-fisted);
    green after the strict source-mirror loadout."""
    def chance(rec, s):
        v = db.get_field_value(rec, 'chanceToEquip' + s)
        v = v[0] if isinstance(v, list) else v
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    def equips(rec, s):
        # source-faithful "equips slot S": chance>0, OR (Head only) a fixed
        # defaultHeadPiece - the Pygmalion-automatoi construct wears a baked head
        # piece the _mirror_source_loadout mirrors even though chanceToEquipHead=0.
        if chance(rec, s) > 0:
            return True
        if s == 'Head':
            hp = db.get_field_value(rec, 'defaultHeadPiece')
            hp = hp[0] if isinstance(hp, list) else hp
            return bool(hp and str(hp).strip())
        return False

    problems = []
    for src_path, pets in pairs:
        src = _resolve_record(db, src_path)
        if not src:
            continue
        for p in pets:
            pr = _resolve_record(db, p)
            if not pr:
                continue
            for s in _GEAR_SLOTS:
                sc = equips(src, s)
                pc = equips(pr, s)
                if sc and not pc:
                    problems.append((p, s, 'source equips it, pet is bare (bare-fisted/naked)'))
                elif pc and not sc:
                    problems.append((p, s, 'pet equips it, source does NOT (over-add)'))
    if problems:
        for p, s, why in problems[:40]:
            print(f"  PET-GEAR-PARITY OFFENDER: {p.rsplit(chr(92), 1)[-1]} :: {s}: {why}")
        raise SystemExit(f"PET-GEAR-PARITY gate FAILED: {len(problems)} gear-parity "
                         f"violation(s) (Will's law: exactly the source's gear, both ways)")
    print(f"  PET-GEAR-PARITY gate OK: {len(pairs)} summon families carry exactly "
          f"their source's gear (both directions)")


def _verify_summon_pet_skill_kit(db):
    """PET-SKILL-KIT gate (fail-loud). Sweeps EVERY soul pet and asserts its
    summon kit can actually FIRE: (a) no friendly Skill_SpawnPet sits in a non-AI
    slot (buffSelf*/init/dying/berserk -> the pet can never summon; the Pygmalion
    bug), and (d) no Skill_SpawnPetMonster (hostile spawner) sits in ANY role slot
    on a friendly pet (it would raise ENEMIES for the player). Negative-tested
    against baseline (flags Pygmalion/Aquardia/Dayria)."""
    nonai = ('buffSelfSkillName', 'buffSelf2SkillName', 'buffSelf3SkillName',
             'buffOtherSkillName', 'buffOther2SkillName', 'buffOther3SkillName',
             'healSkillName', 'initialSkillName', 'dyingSkillName', 'berserkSkillName')

    def fs(rec, f):
        v = db.get_field_value(rec, f)
        v = v[0] if isinstance(v, list) else v
        return str(v).strip() if v is not None and str(v).strip() else ''

    problems = []
    swept = 0
    for p in _all_pet_records(db):
        swept += 1
        for slot in _PET_AI_SLOTS + nonai:
            sk = fs(p, slot)
            if not sk:
                continue
            cls = _skill_class_of(db, sk)
            if cls == 'Skill_SpawnPetMonster':
                problems.append((p, slot, sk, 'HOSTILE Skill_SpawnPetMonster on a friendly pet'))
            elif cls == 'Skill_SpawnPet' and slot in nonai:
                problems.append((p, slot, sk, 'friendly summon in a non-AI slot -> never casts'))
    if problems:
        for p, slot, sk, why in problems[:40]:
            print(f"  PET-SKILL-KIT OFFENDER: {p.rsplit(chr(92), 1)[-1]} :: "
                  f"{slot}={sk.rsplit(chr(92), 1)[-1]}: {why}")
        raise SystemExit(f"PET-SKILL-KIT gate FAILED: {len(problems)} summon-wiring "
                         f"violation(s) across {swept} soul pets")
    print(f"  PET-SKILL-KIT gate OK: {swept} soul pets - every summon in an AI-fired "
          f"slot, no hostile spawner on a friendly pet")


def _apply_group4_summons(db, tags):
    """D13 Eater of Days + D14 Pygmalion (no-limits replicate, Will verbatim:
    'dont have the safe limits on the pygmalion replicator replicates make it
    crazy' - the kit transplant is FAITHFUL, replicate's own native bounds are
    kept, nothing added) + D20 War-King Sarpedon + D21 Long Nu the Flame
    Mother ('her soul needs to be able to summon her'). All via the
    D19-hardened _build_boss_summon (mobility assert + full law suite).
    Existing soul augments/petBonuses are KEPT (none of the four soul lines
    carries an itemSkillName proc, verified - the summon displaces nothing)."""
    namemap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def by_desc(tag):
        for n in db.record_names():
            v = db.get_field_value(n, 'description')
            v = v[0] if isinstance(v, list) else v
            if v == tag and '\\creature\\' in n.replace('/', '\\').lower():
                return n
        return None

    def src_charlevel(src):
        v = db.get_field_value(src, 'charLevel')
        v = v if isinstance(v, list) else [v]
        lv = [int(x) for x in v]
        while len(lv) < 3:
            lv.append(int(lv[-1] * 1.4))
        return lv[:3]

    def souls_by_nametag(tag):
        out = []
        for n in db.record_names():
            if '\\soul\\' not in n.replace('/', '\\').lower():
                continue
            v = db.get_field_value(n, 'itemNameTag')
            v = v[0] if isinstance(v, list) else v
            if v == tag:
                out.append(n)
        order = {'_n.dbr': 0, '_e.dbr': 1, '_l.dbr': 2}
        return sorted(out, key=lambda x: order.get(x[-6:].lower(), 9))

    jobs = [
        dict(label='D13 Eater of Days',
             src=r'records\creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr',
             pets=[r'records\skills\soulskills\pets\eaterofdays_%d.dbr' % i
                   for i in (1, 2, 3)],
             skill=r'records\skills\soulskills\summon_eaterofdays.dbr',
             disp='tagSVCSummonEaterOfDays', desc='tagNewHero91',
             souls=[r'records\item\equipmentring\soul\sepulchralwyrm'
                    r'\eaterofdays_soul_%s.dbr' % t for t in 'nel'],
             life=[12000.0, 16500.0, 21000.0], regen=[30.0, 60.0, 100.0],
             dmin=[70.0, 110.0, 160.0], dmax=[110.0, 170.0, 250.0]),
        dict(label='D14 Pygmalion',
             src=r'records\creature\monster\automatoi\um_pygmalion_41.dbr',
             pets=[r'records\skills\soulskills\pets\pygmalion_%d.dbr' % i
                   for i in (1, 2, 3)],
             skill=r'records\skills\soulskills\summon_pygmalion.dbr',
             disp='tagSVCSummonPygmalion', desc='tagNewHero262',
             souls=[r'records\item\equipmentring\soul\automatoi'
                    r'\pygmalion_soul_%s.dbr' % t for t in 'nel'],
             life=[9500.0, 12000.0, 14500.0], regen=[25.0, 50.0, 80.0],
             dmin=[60.0, 95.0, 140.0], dmax=[95.0, 150.0, 215.0]),
        dict(label='D20 War-King Sarpedon',
             src=r'records\creature\monster\minotaur\um_sarpedon_41.dbr',
             pets=[r'records\skills\soulskills\pets\sarpedon_%d.dbr' % i
                   for i in (1, 2, 3)],
             skill=r'records\skills\soulskills\summon_sarpedon.dbr',
             disp='tagSVCSummonSarpedon', desc=None,
             souls=[r'records\item\equipmentring\soul\minotaur'
                    r'\sarpedon_soul_%s.dbr' % t for t in 'nel'],
             life=[11000.0, 15000.0, 20000.0], regen=[30.0, 55.0, 90.0],
             dmin=[65.0, 105.0, 150.0], dmax=[105.0, 165.0, 235.0]),
        dict(label='D21 Long Nu the Flame Mother',
             src=None, src_desc='tagNewHero181',
             pets=[r'records\skills\soulskills\pets\longnu_%d.dbr' % i
                   for i in (1, 2, 3)],
             skill=r'records\skills\soulskills\summon_longnu.dbr',
             disp='tagSVCSummonLongNu', desc='tagNewHero181',
             souls=None, souls_tag='tagSoulName471',
             life=[12000.0, 16000.0, 21000.0], regen=[30.0, 60.0, 100.0],
             dmin=[70.0, 110.0, 160.0], dmax=[110.0, 170.0, 245.0]),
    ]
    tags['tagSVCSummonEaterOfDays'] = 'Summon the Eater of Days'
    tags['tagSVCSummonPygmalion'] = 'Summon Pygmalion, the Replicator'
    tags['tagSVCSummonSarpedon'] = 'Summon War-King Sarpedon'
    tags['tagSVCSummonLongNu'] = 'Summon Long Nu, the Flame Mother'

    for j in jobs:
        src = j['src']
        if src is None:
            src = by_desc(j['src_desc'])
            if not src:
                raise SystemExit('G4 %s: no creature record carries %s'
                                 % (j['label'], j['src_desc']))
        real = namemap.get(src.replace('/', '\\').lower())
        if not real:
            raise SystemExit('G4 %s: source missing: %s' % (j['label'], src))
        souls = j.get('souls')
        if souls is None:
            souls = souls_by_nametag(j['souls_tag'])
            if len(souls) != 3:
                raise SystemExit('G4 %s: expected 3 souls via %s, found %s'
                                 % (j['label'], j['souls_tag'], souls))
        for sp in souls:
            if not _find_record(db, sp):
                raise SystemExit('G4 %s: soul missing: %s' % (j['label'], sp))
            isk = db.get_field_value(_find_record(db, sp), 'itemSkillName')
            isk = isk[0] if isinstance(isk, list) else isk
            if isinstance(isk, str) and isk.strip():
                print('  G4 %s NOTE: soul %s had a proc %s - DISPLACED by the '
                      'summon per Will naming this soul' % (j['label'], sp, isk))
        desc_tag = j['desc']
        if desc_tag is None:
            v = db.get_field_value(real, 'description')
            desc_tag = v[0] if isinstance(v, list) else v
        loadout = _mirror_source_loadout(db, real)
        lv = src_charlevel(real)
        if not _build_boss_summon(db, src, j['pets'], j['skill'], j['disp'],
                                  desc_tag, char_level=lv, life=j['life'],
                                  life_regen=j['regen'], dmg_min=j['dmin'],
                                  dmg_max=j['dmax'], loadout=loadout):
            raise SystemExit('G4 %s: _build_boss_summon failed' % j['label'])
        _wire_summon_soul(db, souls, j['skill'])
        print('  G4 %s: 3 pets from %s (charLevel %s, loadout %s slot(s)) + '
              'summon skill; souls rewired 1/2/3'
              % (j['label'], real.rsplit(chr(92), 1)[-1], lv,
                 len(loadout) if loadout else 0))


# ── GROUP 3 (build31, overnight autonomous run): D11/D12/D16/D17/D18 ────────
def _apply_group3_tunes(db, tags):
    """D11 Rally cd 45->30; D12 Coastal Ichthian Myrmidon soul big boost;
    D16 Shadow Stalker overhaul (Will-ordered Occult exception: the suicide
    position-swap skill_shadowstrike [Skill_AttackSpellTeleport, teleports the
    squishy pet into packs] is SUBSTITUTED with the shadow distortion field -
    a defensive veil - plus a real stat ladder; golden drift rides
    owner_approved_overrides = Will's per-item sign-off mechanism);
    D17 Core Dweller much stronger (Will: 'make the volcano guy much
    stronger'); D18a Emberscale icon de-turtled (raptor-tooth family art =
    reptilian scale read); D18b Emberscale effect redesign (armor-melt out;
    escalating dragonfire in: big fire amp + burn-over-time on a weapons-only
    charm)."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    def val(rec, f):
        v = db.get_field_value(rec, f)
        if isinstance(v, list):
            return v[0] if v else None
        return v

    # ── D11: Rally cooldown 45 -> 30 (party heal-burst uptime) ──
    RB = r'records\skills\defensive\drxrallybuff.dbr'
    if not db.has_record(RB):
        raise SystemExit('G3 D11: drxrallybuff missing')
    cur = val(RB, 'skillCooldownTime')
    if abs(float(cur) - 45.0) > 0.01:
        raise SystemExit(f'G3 D11: rally cd {cur} != 45 - spec drift')
    sf(RB, 'skillCooldownTime', 30.0)
    print('  G3 D11 Rally: cooldown 45 -> 30')

    # ── D12: Coastal Ichthian Myrmidon souls - big boost ──
    d12 = {
        'n': dict(life=250.0, oa=60.0, cmin=15.0, cmax=25.0, cmod=20, res=20.0, atk=8.0),
        'e': dict(life=450.0, oa=120.0, cmin=30.0, cmax=45.0, cmod=35, res=30.0, atk=12.0),
        'l': dict(life=650.0, oa=180.0, cmin=50.0, cmax=75.0, cmod=50, res=40.0, atk=15.0),
    }
    for t, v in d12.items():
        rec = (r'records\item\equipmentring\soul\ichthian'
               '\\coastalichthianmyrmidon_soul_%s.dbr' % t)
        if not db.has_record(rec):
            raise SystemExit('G3 D12: soul missing: %s' % rec)
        sf(rec, 'characterLife', v['life'])
        sf(rec, 'characterOffensiveAbility', v['oa'])
        sf(rec, 'offensiveColdMin', v['cmin'])
        sf(rec, 'offensiveColdMax', v['cmax'])
        sf(rec, 'offensiveColdModifier', v['cmod'])
        sf(rec, 'defensiveCold', v['res'])
        sf(rec, 'characterAttackSpeedModifier', v['atk'])
        db._modified.add(rec)
    print('  G3 D12 Myrmidon souls: life 250/450/650, OA 60/120/180, cold '
          '15-25/30-45/50-75 +20/35/50 pct, cold res, +atk speed')

    # ── D16: Shadow Stalker overhaul (Occult exception, Will-ordered) ──
    VEIL = (r'records\skills\monster skills\passive_buffs'
            '\\shadowstalker_distortionfield.dbr')
    if not db.has_record(VEIL):
        raise SystemExit('G3 D16: distortionfield substitute missing')
    changed = 0
    for t in range(1, 21):
        rec = r'records\skills\stealth\drxpet' + '\\drx_shadow_stalker_%02d.dbr' % t
        if not db.has_record(rec):
            raise SystemExit('G3 D16: stalker tier missing: %s' % rec)
        s7 = val(rec, 'skillName7')
        if not (isinstance(s7, str) and s7.lower().endswith('skill_shadowstrike.dbr')):
            raise SystemExit('G3 D16: %s skillName7 is %r, expected '
                             'shadowstrike - spec drift' % (rec, s7))
        sf(rec, 'skillName7', VEIL, S)
        sf(rec, 'skillLevel7', min(t, 7), I)   # veil caps near the monster max
        sf(rec, 'characterLife', float(500 + 90 * (t - 1)))
        sf(rec, 'characterStrength', float(160 + 8 * t))
        sf(rec, 'characterDexterity', float(200 + 10 * t))
        sf(rec, 'handHitDamageMin', float(120 + 14 * (t - 1)))
        sf(rec, 'handHitDamageMax', float(150 + 18 * (t - 1)))
        db._modified.add(rec)
        changed += 1
    print('  G3 D16 Shadow Stalker (%d tiers): suicide shadowstrike -> '
          'distortion veil; life 500..2210 (was flat 297), dmg 120-150..'
          '386-492 (was flat 83-98), str/dex ladders. OCCULT EXCEPTION per '
          "Will: 'make him stronger, much stronger'" % changed)

    # ── D17: Core Dweller much stronger (keep the taunt identity) ──
    for t in range(1, 21):
        rec = r'records\skills\earth\pet' + '\\coredweller_%02d.dbr' % t
        if not db.has_record(rec):
            raise SystemExit('G3 D17: coredweller tier missing: %s' % rec)
        for f_, mult in (('characterLife', 1.75), ('handHitDamageMin', 1.6),
                         ('handHitDamageMax', 1.6), ('characterStrength', 1.25),
                         ('characterLifeRegen', 1.5)):
            cur = val(rec, f_)
            if cur is None:
                raise SystemExit('G3 D17: %s lacks %s' % (rec, f_))
            sf(rec, f_, round(float(cur) * mult, 1))
        db._modified.add(rec)
    print('  G3 D17 Core Dweller (20 tiers): life x1.75 (781->1367 .. '
          '2250->3937), dmg x1.6, str x1.25, regen x1.5; taunt kit untouched')

    # ── D18a+b: Emberscale icon + effect redesign ──
    d18 = {
        '01': dict(suff='', mod=[4.0, 8.0, 12.0, 16.0, 20.0],
                   burn=[6.0, 12.0, 18.0, 24.0, 30.0]),
        '02': dict(suff='_E', mod=[6.0, 12.0, 18.0, 24.0, 30.0],
                   burn=[10.0, 20.0, 30.0, 40.0, 50.0]),
        '03': dict(suff='_L', mod=[8.0, 16.0, 24.0, 32.0, 40.0],
                   burn=[14.0, 28.0, 42.0, 56.0, 70.0]),
    }
    for t, v in d18.items():
        rec = (r'records\item\animalrelics\svc_flameguard'
               '\\%s_flameguardslayer.dbr' % t)
        if not db.has_record(rec):
            raise SystemExit('G3 D18: charm missing: %s' % rec)
        # D18a: raptor-tooth family art (reptilian scale read; the turtle
        # donor bitmaps made it read as a Turtle Shell). Shard suffix mirrors
        # the donor pattern exactly (01=A, 02=A_E, 03=A).
        sf(rec, 'relicBitmap',
           'Items\\AnimalRelics\\AnimalPart13B%s.tex' % v['suff'], S)
        shard_suff = '_E' if t == '02' else ''
        sf(rec, 'shardBitmap',
           'Items\\AnimalRelics\\AnimalPart13A%s.tex' % shard_suff, S)
        # D18b: drop the armor melt (absent-shape clear, never '')
        ff = db.get_fields(rec) or {}
        for k, tf in ff.items():
            if k.split('###')[0] in ('offensiveSlowDefensiveReductionMin',
                                     'offensiveSlowDefensiveReductionDurationMin'):
                tf.values = []
        # escalating dragonfire: fire amp + burn over 3s (flat fire kept)
        sf(rec, 'offensiveFireModifier', v['mod'])
        sf(rec, 'offensiveSlowFireMin', v['burn'])
        sf(rec, 'offensiveSlowFireDurationMin', 3.0)
        sf(rec, 'FileDescription', 'Emberscale: fire damage + pct fire + burn', S)
        db._modified.add(rec)
    tags['tagSVCFlameguardRelicDESC'] = (
        'A scale pried from a Flameguard Slayer, still smoldering. Weapons '
        'socketed with it bite with dragonfire that clings and burns.')
    print('  G3 D18 Emberscale: raptor-tooth icon (de-turtled) + redesigned '
          'effect (flat fire + 20/30/40 pct fire amp + 30/50/70 burn over 3s; '
          'armor-melt removed)')


# ── M15 (Will, 2026-07-09 night): Toxeus joins the existing spawn groups ────
# 'find the spawn group that currently exists within the esti chest area and
# add toxeus devourer of blood to it with 100% spawn rate' + 'there is a spawn
# group of little demon guys that are right on top of the tattered parchment -
# you can put toxeus devourer of blood there too with 50% spawn chance.'
# Map recon (m15_proxy_recon.py, byte-decoded from the shipped 0x05):
#   CHEST ROOM (drxBC2): proxy egg_blooddragon_pack @ local (13.17,28,136.06),
#     4.2u from the chest; pool pools\egg_blooddragon.dbr; BOTH proxy and pool
#     are EXCLUSIVE (1 placement, 1 referencing proxy) -> edit the pool IN
#     PLACE: guaranteed-boss construction, championChance=100/championMax=1,
#     Toxeus the only champion entry; spawnMax(4)-championMax(1)>=1 law holds
#     (3 blood dragons + Toxeus every run).
#   PARCHMENT (drxFirstxistion_connection): proxy demon_01_cluster @ local
#     (37.16,10,20.46), 5.5u from the letter; its pool is proxy-exclusive but
#     the PROXY has 19 placements across 3 levels -> DERIVE copies
#     (demon_01_cluster_toxeus50 proxy + pool) with the champion list replaced
#     by Toxeus-only @50 (the 3-8 small demons stay; the other 18 placements
#     keep the original 40% med-demon champion). spawnMax(8)-championMax(1)>=1.
# COUPLED SHIP (map lane): repoint the ONE parchment instance to the derived
# proxy record + REMOVE both standalone proxies (q_bloodtoxeus_lone in drxBC2
# + q_bloodtoxeus_lone_50 on the letter) or the old double-spawn returns.
# Champion field shapes mirror the demon pool's own live shape verbatim
# (championChance FLOAT / championMax INT / nameChampionN / weightChampionN;
# no championMin - zero-precedent in this pool family).
_M15_EGG_POOL = r'records\drxmap\proxy\pools\egg_blooddragon.dbr'
_M15_DEMON_PROXY = r'records\drxmap\proxy\demon_01_cluster.dbr'
_M15_DEMON_POOL = r'records\drxmap\proxy\pools\demon_01_cluster.dbr'
_M15_DERIVED_PROXY = r'records\drxmap\proxy\demon_01_cluster_toxeus50.dbr'
_M15_DERIVED_POOL = r'records\drxmap\proxy\pools\demon_01_cluster_toxeus50.dbr'
_M15_TOXEUS = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'


def _apply_m15_toxeus_group_joins(db):
    if not db.has_record(_M15_TOXEUS):
        raise SystemExit("M15: um_bloodtoxeus_99 missing")

    def val(rec, f, default=None):
        v = db.get_field_value(rec, f)
        if isinstance(v, list):
            v = v[0] if v else None
        return default if v is None else v

    # ── chest room: edit the exclusive egg pool in place (@100) ──
    if not db.has_record(_M15_EGG_POOL):
        raise SystemExit(f"M15: pool missing: {_M15_EGG_POOL}")
    if val(_M15_EGG_POOL, 'championChance') not in (None, 0, 0.0):
        raise SystemExit("M15: egg pool already has champion fields - "
                         "pre-shape changed, reconcile")
    sf = db.set_field
    sf(_M15_EGG_POOL, 'championChance', 100.0)
    sf(_M15_EGG_POOL, 'championMax', 1)
    sf(_M15_EGG_POOL, 'nameChampion1', _M15_TOXEUS)
    sf(_M15_EGG_POOL, 'weightChampion1', 100)
    smax = int(float(val(_M15_EGG_POOL, 'spawnMax', 0)))
    if smax - 1 < 1:
        raise SystemExit(f"M15: egg pool spawnMax {smax} - championMax 1 < 1 "
                         f"(champion crowd-out law)")
    db._modified.add(_M15_EGG_POOL)
    print(f"  M15 chest room: egg_blooddragon pool += Toxeus champion @100 "
          f"(spawnMax {smax}, {smax - 1} dragons + the Devourer every run)")

    # ── parchment: derive proxy+pool copies (@50); map lane repoints ──
    for rec in (_M15_DERIVED_PROXY, _M15_DERIVED_POOL):
        if db.has_record(rec):
            raise SystemExit(f"M15: derived record already exists: {rec}")
    if not db.has_record(_M15_DEMON_POOL) or not db.has_record(_M15_DEMON_PROXY):
        raise SystemExit("M15: demon_01_cluster proxy/pool missing")
    if float(val(_M15_DEMON_POOL, 'championChance', 0)) != 40.0:
        raise SystemExit("M15: demon pool championChance != 40 - pre-shape "
                         "changed, reconcile")
    db.clone_record(_M15_DEMON_POOL, _M15_DERIVED_POOL)
    # pure VALUE edits on the clone (no field-shape change; empty-string .dbr
    # refs are the B-TOXEUS-2 loader-abort class, so all three existing
    # champion entries are repointed at Toxeus instead of blanked - any
    # champion roll yields him; weights keep their native 34/33/33 values).
    sf(_M15_DERIVED_POOL, 'championChance', 50.0)
    sf(_M15_DERIVED_POOL, 'nameChampion1', _M15_TOXEUS)
    sf(_M15_DERIVED_POOL, 'nameChampion2', _M15_TOXEUS)
    sf(_M15_DERIVED_POOL, 'nameChampion3', _M15_TOXEUS)
    db._modified.add(_M15_DERIVED_POOL)
    db.clone_record(_M15_DEMON_PROXY, _M15_DERIVED_PROXY)
    sf(_M15_DERIVED_PROXY, 'pool1', _M15_DERIVED_POOL)
    db._modified.add(_M15_DERIVED_PROXY)
    smax2 = int(float(val(_M15_DERIVED_POOL, 'spawnMax', 0)))
    if smax2 - 1 < 1:
        raise SystemExit(f"M15: derived pool spawnMax {smax2} law violation")
    print(f"  M15 parchment: derived demon_01_cluster_toxeus50 proxy+pool "
          f"(Toxeus only champion @50; {smax2} max small demons). MAP LANE: "
          f"repoint the parchment instance + remove both standalone proxies.")


# ══════════════════════════════════════════════════════════════════════════
#  D10 EMBERSCALE (Will 2026-07-09): a new 5-shard collectible charm (ItemCharm,
#  exact Turtle Shell pattern) dropped by the "{^G}Flameguard Slayer" green
#  Dragonian champion (em_ravager_39 + em_ravager_41, Act 3 Orient). Weapons-only,
#  fire damage + armor melt (offensiveSlowDefensiveReduction), NO granted skill
#  (deliberate: charms have no skill hook; the armor-melt passive is the fantasy).
#  Drop = the turtle-matched 7% on the first UNUSED lootMisc slot (slot 3,
#  DB-verified free on both bodies), mirroring the turtle wiring shape exactly
#  (chanceToEquipMisc3=7.0, chanceToEquipMisc3Item1=100, [N,E,L] table array).
# ══════════════════════════════════════════════════════════════════════════
_D10_CHARM = {t: rf'records\item\animalrelics\svc_flameguard\{t}_flameguardslayer.dbr'
              for t in ('01', '02', '03')}
_D10_CHARM_DONOR = {t: rf'records\item\animalrelics\{t}_act1_turtleshell.dbr'
                    for t in ('01', '02', '03')}
_D10_BONUS = {t: rf'records\item\lootmagicalaffixes\animalrelics\svc_flameguard\{t}_flameguardslayer.dbr'
              for t in ('01', '02', '03')}
_D10_LOOT = {t: rf'records\item\loottables\animalrelics\svc_flameguard\{t}_flameguardslayer.dbr'
             for t in ('01', '02', '03')}
_D10_LOOT_DONOR = r'records\item\loottables\animalrelics\01_act1_turtleshell.dbr'
_D10_RAVAGERS = [r'records\creature\monster\dragonian\em_ravager_39.dbr',
                 r'records\creature\monster\dragonian\em_ravager_41.dbr']
_D10_AFF = r'records\item\lootmagicalaffixes'
# Completion-bonus entries per tier: 6 weighted rolls, total weight 1500 per tier.
# Legendary = the Will-approved set; N/E step the same affix families down to the
# tier-appropriate existing variants (all 18 paths DB-verified to exist).
_D10_BONUS_ENTRIES = {
    '01': [(_D10_AFF + r'\suffix\default\offensive_+%fire_02.dbr', 250),
           (_D10_AFF + r'\animalrelics\bonuses\offensive_+%fire_01.dbr', 300),
           (_D10_AFF + r'\suffix\default\character_abilityoffensive_02.dbr', 300),
           (_D10_AFF + r'\suffix\default\character_attributestrength_01.dbr', 250),
           (_D10_AFF + r'\suffix\default\character_attributelife_01.dbr', 200),
           (_D10_AFF + r'\prefix\default\defensive_resistfire_01.dbr', 200)],
    '02': [(_D10_AFF + r'\suffix\default\offensive_+%fire_03.dbr', 250),
           (_D10_AFF + r'\animalrelics\bonuses\offensive_+%fire_02.dbr', 300),
           (_D10_AFF + r'\suffix\default\character_abilityoffensive_04.dbr', 300),
           (_D10_AFF + r'\suffix\default\character_attributestrength_03.dbr', 250),
           (_D10_AFF + r'\suffix\default\character_attributelife_02.dbr', 200),
           (_D10_AFF + r'\prefix\default\defensive_resistfire_02.dbr', 200)],
    '03': [(_D10_AFF + r'\suffix\default\offensive_+%fire_04.dbr', 250),
           (_D10_AFF + r'\animalrelics\bonuses\offensive_+%fire_03.dbr', 300),
           (_D10_AFF + r'\suffix\default\character_abilityoffensive_06.dbr', 300),
           (_D10_AFF + r'\suffix\default\character_attributestrength_05.dbr', 250),
           (_D10_AFF + r'\suffix\default\character_attributelife_03.dbr', 200),
           (_D10_AFF + r'\prefix\default\defensive_resistfire_03.dbr', 200)],
}
# Per-shard length-5 FLOAT arrays (shards 1..5), per tier N/E/L (Will-approved).
_D10_STATS = {
    '01': {'offensiveFireMin': [3.0, 6.0, 9.0, 12.0, 15.0],
           'offensiveFireMax': [7.0, 14.0, 21.0, 28.0, 35.0],
           'offensiveSlowDefensiveReductionMin': [4.0, 8.0, 12.0, 16.0, 20.0]},
    '02': {'offensiveFireMin': [5.0, 10.0, 15.0, 20.0, 25.0],
           'offensiveFireMax': [10.0, 20.0, 30.0, 40.0, 50.0],
           'offensiveSlowDefensiveReductionMin': [6.0, 12.0, 18.0, 24.0, 30.0]},
    '03': {'offensiveFireMin': [7.0, 14.0, 21.0, 28.0, 35.0],
           'offensiveFireMax': [13.0, 26.0, 39.0, 52.0, 65.0],
           'offensiveSlowDefensiveReductionMin': [8.0, 16.0, 24.0, 32.0, 40.0]},
}
_D10_LEVELREQ = {'01': 24, '02': 38, '03': 50}
# ItemCharm slot-permission fields (all exist on the donor as 0/1 INTs).
_D10_SLOTS_ON = ('sword', 'axe', 'mace', 'spear', 'bow', 'staff')
_D10_SLOTS_OFF = ('shield', 'amulet', 'armband', 'bodyArmor', 'bracelet',
                  'greaves', 'helmet', 'ring')


def _create_emberscale_charm(db, tags):
    """D10: build the Emberscale charm chain: 3 tier charms (clone the turtle
    donors = full ItemCharm field population + shipping icon/mesh/bitmaps, so no
    grey box), 3 completion-bonus LootRandomizerTables, 3 FixedWeight loot
    tables, and the 7% lootMisc3 wiring on both Flameguard Slayer bodies.
    dtype discipline: cloned-record overrides pass NO dtype (preserve each
    existing field's type); explicit dtypes only on NEW records' fields."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    for t in ('01', '02', '03'):
        # F6b (vet): EXACT-path asserts - _find_record is a shadowed SUBSTRING
        # matcher (module def at ~3271 shadows the exact-path def at ~292), so a
        # substring hit could silently select the wrong donor. has_record is
        # exact-match on the record table.
        donor = _D10_CHARM_DONOR[t]
        if not db.has_record(donor):
            raise SystemExit(f"D10: turtle charm donor missing (exact): {donor}")
        for path, _w in _D10_BONUS_ENTRIES[t]:
            if not db.has_record(path):
                raise SystemExit(f"D10: completion-bonus affix missing (exact): {path}")

        # ── charm (clone -> override; NO dtypes on existing fields) ──
        charm = _D10_CHARM[t]
        db.clone_record(donor, charm)
        sf = db.set_field
        sf(charm, 'description', 'tagSVCFlameguardRelic')
        sf(charm, 'itemText', 'tagSVCFlameguardRelicDESC')
        sf(charm, 'FileDescription', 'Fire damage + armor melt')
        sf(charm, 'levelRequirement', _D10_LEVELREQ[t])
        # the turtle's block identity is zeroed out (Emberscale is offensive)
        sf(charm, 'defensiveBlockModifier', [0.0, 0.0, 0.0, 0.0, 0.0])
        sf(charm, 'characterDefensiveBlockRecoveryReduction', 0.0)
        # per-shard fire + armor-melt ladder
        for fname, arr in _D10_STATS[t].items():
            sf(charm, fname, list(arr))
        sf(charm, 'offensiveSlowDefensiveReductionDurationMin', 3.0)
        # weapons-only
        for slot in _D10_SLOTS_ON:
            sf(charm, slot, 1)
        for slot in _D10_SLOTS_OFF:
            sf(charm, slot, 0)
        sf(charm, 'bonusTableName', _D10_BONUS[t])
        db._modified.add(charm)

        # ── completion-bonus table (NEW record; explicit dtypes OK on new fields) ──
        bt = _D10_BONUS[t]
        _ensure_record(db, bt, r'database\Templates\LootRandomizerTable.tpl')
        db.set_field(bt, 'templateName', r'database\Templates\LootRandomizerTable.tpl', S)
        db.set_field(bt, 'Class', 'LootRandomizerTable', S)
        total_w = 0
        for i, (path, w) in enumerate(_D10_BONUS_ENTRIES[t], start=1):
            db.set_field(bt, f'randomizerName{i}', path, S)
            db.set_field(bt, f'randomizerWeight{i}', w, I)
            total_w += w
        if total_w != 1500:
            raise SystemExit(f"D10: tier {t} bonus weights sum {total_w} != 1500")
        db._modified.add(bt)

        # ── loot table (clone the turtle FixedWeight table: only slot 1 active,
        #    noPrefixNoSuffix already 100 on the donor) ──
        lt = _D10_LOOT[t]
        if not db.has_record(_D10_LOOT_DONOR):   # F6b: exact-path assert
            raise SystemExit(f"D10: turtle loot table donor missing (exact): {_D10_LOOT_DONOR}")
        ldonor = _D10_LOOT_DONOR
        db.clone_record(ldonor, lt)
        db.set_field(lt, 'lootName1', charm)
        db._modified.add(lt)

    # ── wire both Flameguard Slayer bodies: turtle-shape 7% on the free slot 3 ──
    loot_arr = [_D10_LOOT['01'], _D10_LOOT['02'], _D10_LOOT['03']]
    for mon in _D10_RAVAGERS:
        if not db.has_record(mon):   # F6b: exact-path assert
            raise SystemExit(f"D10: Flameguard Slayer body missing (exact): {mon}")
        rec = mon
        cur = db.get_field_value(rec, 'lootMisc3Item1')
        if cur not in (None, '', 0):
            raise SystemExit(f"D10: {mon} lootMisc3 is NOT free (has {cur!r}); "
                             f"slot assumption broken - pick another slot")
        # lootMisc3Item1 is a NEW field on these records -> explicit STRING dtype;
        # the chanceToEquipMisc3* fields EXIST (0.0 FLOAT / 0 INT) -> no dtype.
        db.set_field(rec, 'lootMisc3Item1', list(loot_arr), S)
        db.set_field(rec, 'chanceToEquipMisc3', 7.0)
        db.set_field(rec, 'chanceToEquipMisc3Item1', 100)
        db._modified.add(rec)

    tags['tagSVCFlameguardRelic'] = 'Emberscale'
    tags['tagSVCFlameguardRelicDESC'] = (
        'Pried still-smoking from the Flameguard Slayer. Where its edge fell, '
        'good armor ran like candle wax.')
    print("  D10 Emberscale: 3 charms (turtle-pattern, weapons-only, fire + armor melt) "
          "+ 3 bonus tables (w1500) + 3 loot tables; wired em_ravager_39/41 "
          "lootMisc3 @ 7% (turtle-matched)")


# ── build36 A3 (Will 2026-07-11): SANGUINE TITHE relic off the Sileni ────────
# "the blood harness guys with the green name should drop a special relic." The
# mod's THIRD custom charm (after Emberscale/fire-weapon + Sepulchral Scale/cold-
# armor): a JEWELRY blood charm (life leech + vitality damage + %-current-life
# bleed) off the Sileni (DRX bloodabomination satyr-brutes = the blood-harness
# guys). Same builder shape as D10 Emberscale / Group-G Sepulchral Scale. Donor =
# the base-game Demon's Blood animalrelic (already blood art + ItemCharm +
# completedRelicLevel=5 + jewelry slots -> NO art repoint, one better than
# Emberscale/Sepulchral which had to repoint their bitmaps).
_ST_CHARM = {t: r'records\item\animalrelics\svc_sanguinetithe\%s_sanguinetithe.dbr' % t for t in ('01', '02', '03')}
_ST_DONOR = {t: r'records\item\animalrelics\%s_multacts_demonsblood.dbr' % t for t in ('01', '02', '03')}
_ST_BONUS = {t: r'records\item\lootmagicalaffixes\animalrelics\svc_sanguinetithe\%s_sanguinetithe.dbr' % t for t in ('01', '02', '03')}
_ST_LOOT = {t: r'records\item\loottables\animalrelics\svc_sanguinetithe\%s_sanguinetithe.dbr' % t for t in ('01', '02', '03')}
_ST_LOOTDON = r'records\item\loottables\animalrelics\01_multacts_demonsblood.dbr'
_ST_SILENI = [
    r'records\drxcreatures\bloodabomination\01_bladedancer_35.dbr',
    r'records\drxcreatures\bloodabomination\01_bladedancer_36.dbr',
    r'records\drxcreatures\bloodabomination\01_bladedancer_37.dbr',
    r'records\drxcreatures\bloodabomination\02_spearrunner_37.dbr',
    r'records\drxcreatures\bloodabomination\02_spearrunner_38.dbr',
    r'records\drxcreatures\bloodabomination\02_spearrunner_39.dbr',
    r'records\drxcreatures\bloodabomination\03_ravager_38.dbr',
    r'records\drxcreatures\bloodabomination\03_ravager_39.dbr',
    r'records\drxcreatures\bloodabomination\03_ravager_40.dbr',
]
_ST_LEVELREQ = {'01': 34, '02': 48, '03': 60}
_ST_DROP_PCT = 7.0
_ST_SLOTS_OFF = ('sword', 'axe', 'mace', 'spear', 'bow', 'staff', 'shield',
                 'bodyArmor', 'greaves', 'helmet', 'armband', 'bracelet')
# per-shard 5-arrays (Legendary 03; 02 ~0.66x; 01 ~0.4x). SIGNATURE = GUARANTEED
# Life Leech at 5/5 only (the vampiric awakening), like Sepulchral's guaranteed
# fear ([0,0,0,0,X]): the charm is inert-leech while incomplete, then "wakes up".
_ST_STATS = {
    '03': {'offensiveLifeMin': [15.0, 30.0, 45.0, 60.0, 75.0],
           'offensiveLifeMax': [25.0, 50.0, 75.0, 100.0, 125.0],
           'offensivePercentCurrentLifeMin': [1.0, 2.0, 3.0, 4.0, 5.0],
           'characterLife': [40.0, 80.0, 120.0, 160.0, 200.0],
           'offensiveLifeLeechMin': [0.0, 0.0, 0.0, 0.0, 16.0]},
    '02': {'offensiveLifeMin': [10.0, 20.0, 30.0, 40.0, 50.0],
           'offensiveLifeMax': [16.0, 32.0, 48.0, 64.0, 80.0],
           'offensivePercentCurrentLifeMin': [0.6, 1.2, 1.8, 2.4, 3.0],
           'characterLife': [26.0, 52.0, 78.0, 104.0, 130.0],
           'offensiveLifeLeechMin': [0.0, 0.0, 0.0, 0.0, 12.0]},
    '01': {'offensiveLifeMin': [6.0, 12.0, 18.0, 24.0, 30.0],
           'offensiveLifeMax': [10.0, 20.0, 30.0, 40.0, 50.0],
           'offensivePercentCurrentLifeMin': [0.4, 0.8, 1.2, 1.6, 2.0],
           'characterLife': [16.0, 32.0, 48.0, 64.0, 80.0],
           'offensiveLifeLeechMin': [0.0, 0.0, 0.0, 0.0, 8.0]},
}
# blood/life/vitality completion-bonus affixes (all 3-tier verified present). 1500.
_ST_BONUS_ENTRIES = {t: [
    (r'records\item\lootmagicalaffixes\animalrelics\bonuses\offensive_damagelife_%s.dbr' % t, 300),
    (r'records\item\lootmagicalaffixes\forge\bonuses\offensive_vitality_%s.dbr' % t, 250),
    (r'records\item\lootmagicalaffixes\animalrelics\bonuses\glowingmoss_%%health_%s.dbr' % t, 250),
    (r'records\item\lootmagicalaffixes\suffix\default\character_attributelife_%s.dbr' % t, 250),
    (r'records\item\lootmagicalaffixes\animalrelics\bonuses\defensive_liferesist_%s.dbr' % t, 250),
    (r'records\item\lootmagicalaffixes\animalrelics\bonuses\glowingmoss_healthregen_%s.dbr' % t, 200),
] for t in ('01', '02', '03')}


def _create_sanguine_tithe(db, tags):
    """A3: build the Sanguine Tithe jewelry blood charm (Emberscale/D10 +
    Sepulchral/Group-G pattern): 3 tier charms (clone the Demon's Blood donor ->
    override to the blood ladder), 3 completion-bonus LootRandomizerTables, 3
    FixedWeight loot tables, and the 7% lootMisc4 wiring on all 9 Sileni combat
    bodies. dtype discipline: cloned overrides pass NO dtype; NEW records' brand-
    new fields carry explicit dtypes."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    if not db.has_record(_ST_DONOR['01']) or not db.has_record(_ST_LOOTDON):
        print("  SANGUINE TITHE: WARNING Demon's Blood donor missing; group skipped")
        return
    for t in ('01', '02', '03'):
        donor = _ST_DONOR[t]
        if not db.has_record(donor):                     # exact-path assert (D10 rule)
            raise SystemExit(f"A3: Demon's Blood charm donor missing (exact): {donor}")
        for path, _w in _ST_BONUS_ENTRIES[t]:
            if not db.has_record(path):
                raise SystemExit(f"A3: completion-bonus affix missing (exact): {path}")
        # ── charm (clone -> override; NO dtypes on existing fields) ──
        charm = _ST_CHARM[t]
        db.clone_record(donor, charm)
        sf = db.set_field
        sf(charm, 'description', 'tagSVCSanguineTithe')
        sf(charm, 'itemText', 'tagSVCSanguineTitheDESC')
        sf(charm, 'FileDescription', 'Sanguine Tithe: life leech + vitality + %current-life bleed')
        sf(charm, 'levelRequirement', _ST_LEVELREQ[t])
        # jewelry only (the donor is already amulet+ring; force weapon/armor OFF)
        sf(charm, 'amulet', 1); sf(charm, 'ring', 1)
        for slot in _ST_SLOTS_OFF:
            sf(charm, slot, 0)
        # zero the donor's non-blood stat block, then author the blood ladder
        sf(charm, 'defensiveStun', [0.0, 0.0, 0.0, 0.0, 0.0])
        sf(charm, 'defensiveLife', [0.0, 0.0, 0.0, 0.0, 0.0])
        for fname, arr in _ST_STATS[t].items():
            sf(charm, fname, list(arr))
        sf(charm, 'bonusTableName', _ST_BONUS[t])
        db._modified.add(charm)
        # ── completion-bonus table (NEW LootRandomizerTable) ──
        bt = _ST_BONUS[t]
        _ensure_record(db, bt, r'database\Templates\LootRandomizerTable.tpl')
        db.set_field(bt, 'templateName', r'database\Templates\LootRandomizerTable.tpl', S)
        db.set_field(bt, 'Class', 'LootRandomizerTable', S)
        total_w = 0
        for i, (path, w) in enumerate(_ST_BONUS_ENTRIES[t], start=1):
            db.set_field(bt, f'randomizerName{i}', path, S)
            db.set_field(bt, f'randomizerWeight{i}', w, I)
            total_w += w
        if total_w != 1500:
            raise SystemExit(f"A3: tier {t} bonus weights sum {total_w} != 1500")
        db._modified.add(bt)
        # ── loot table (clone the Demon's Blood FixedWeight table; slot 1 = charm) ──
        lt = _ST_LOOT[t]
        db.clone_record(_ST_LOOTDON, lt)
        db.set_field(lt, 'lootName1', charm)
        db._modified.add(lt)
    # ── wire all 9 Sileni combat bodies: turtle-matched 7% on the free lootMisc4 ──
    loot_arr = [_ST_LOOT['01'], _ST_LOOT['02'], _ST_LOOT['03']]
    wired = 0
    for w in _ST_SILENI:
        if not db.has_record(w):                          # exact-path assert
            raise SystemExit(f"A3: Sileni combat body missing (exact): {w}")
        cur = db.get_field_value(w, 'lootMisc4Item1')
        if cur not in (None, '', 0, []):
            raise SystemExit(f"A3: {w} lootMisc4 is NOT free (has {cur!r}); pick another slot")
        db.set_field(w, 'lootMisc4Item1', list(loot_arr), S)   # NEW field -> STRING dtype
        db.set_field(w, 'chanceToEquipMisc4', _ST_DROP_PCT)    # existing 0.0 FLOAT -> no dtype
        db.set_field(w, 'chanceToEquipMisc4Item1', 100)        # existing 0 INT -> no dtype
        db._modified.add(w)
        wired += 1
    tags['tagSVCSanguineTithe'] = 'Sanguine Tithe'
    tags['tagSVCSanguineTitheDESC'] = (
        "Cut from a Sileni's harness, still warm. It was never a decoration. Wear "
        "it, and every wound you open pays its due back to you in blood.")
    # NOTE: the green-name polish (Will's "green name"): the 3 Sileni name tags
    # (tagAbomDW/Spear/Brute) get the {^G} green prefix via build_text_arc.py's
    # TEXT_FIX_TAGS single-definition override, NOT here - putting an OVERRIDE of an
    # existing base/SV tag in the uber-soul-tags section would trip the fail-loud
    # duplicate-tag gate (the engine keeps the FIRST definition).
    print(f"  A3 Sanguine Tithe: 3 jewelry charms (life leech + vitality + %-current-"
          f"life bleed, guaranteed 5/5 leech) + 3 bonus tables (w1500) + 3 loot "
          f"tables; wired {wired}/9 Sileni lootMisc4 @ {_ST_DROP_PCT}%; Sileni -> green")


# ── GROUP G (build32): N7 Wyrm Hordes + the Sepulchral Scale charm ──────────
# Will PRE-AUTHORIZED (BACKLOG N7). Transform the 6 Act-3 tomb ug_demon_wyrmsprite
# encounters into escalating SEPULCHRAL WYRM HORDES + a themed cold charm.
# - Common horde body: um_sepulchralwyrm_common_31 DERIVED (the base ships only
#   Champion um_sepulchralwyrm_31/34/37/40; clone _31 -> Common for the main
#   pool slots so the horde reads as fodder and drops no souls).
# - 3 NEW pools (svc_wyrmhorde_0{1,2,3}, cloned from the firesprite pools so all
#   flavor/weight fields carry over) sized 4/8, 6/12, 8/16; tier-03 adds the
#   champion config 100/4/6 (nameChampion = the 4 champion worms) - spawnMax 16
#   - championMax 6 = 10 guaranteed main slots (the spawnMax-championMax>=1 law).
#   NEW pools + repointing the 6 proxies leaves the shared firesprite pools
#   untouched (they may spawn elsewhere).
# - no-cap limit_wyrmhorde (herolimit_all clone) on all 6 proxies.
# - Sepulchral Scale charm (svc_sepulchralscale, Emberscale/D10 pattern): clone
#   the yeti-fur ARMOR charm (keeps its armor-slot flags + working cold-themed
#   completion bonus table), retheme to cold/frostburn/cold-slow/life + a
#   GUARANTEED completion fear (2/2/3), lvlReq 30/44/56; 7% on the 4 champion
#   worms via a free lootMisc slot (D10 mechanism).
_WH_COMMON = r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_common_31.dbr'
_WH_COMMON_DONOR = r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_31.dbr'
_WH_CHAMP_WORMS = [rf'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_{lv}.dbr'
                   for lv in ('31', '34', '37', '40')]
_WH_PROXY_TIERS = {
    '01': [r'records\proxies orient\area007 - tomb\ug_demon_wyrmsprite_01n.dbr',
           r'records\proxies orient\area007 - tomb\ug_demon_wyrmsprite_01t.dbr'],
    '02': [r'records\proxies orient\area007 - tomb\ug_demon_wyrmsprite_02n.dbr',
           r'records\proxies orient\area007 - tomb\ug_demon_wyrmsprite_02t.dbr'],
    '03': [r'records\proxies orient\area007 - tomb\ug_demon_wyrmsprite_03n.dbr',
           r'records\proxies orient\area007 - tomb\ug_demon_wyrmsprite_03t.dbr'],
}
_WH_POOL_DONOR = {t: rf'records\proxies orient\pools\demon\firesprite_{t}_general06.dbr'
                  for t in ('01', '02', '03')}
_WH_POOL = {t: rf'records\proxies orient\pools\demon\svc_wyrmhorde_{t}.dbr'
            for t in ('01', '02', '03')}
_WH_SIZE = {'01': (4, 8), '02': (6, 12), '03': (8, 16)}
_WH_LIMIT = r'records\proxies orient\limit_wyrmhorde.dbr'
_WH_LIMIT_DONOR = r'records\proxies boss\herolimit_all.dbr'
_WH_CHARM_DONOR = {t: rf'records\item\animalrelics\{t}_act3_yetifur.dbr' for t in ('01', '02', '03')}
_WH_CHARM = {t: rf'records\item\animalrelics\svc_sepulchralscale\{t}_sepulchralscale.dbr'
             for t in ('01', '02', '03')}
_WH_LOOT_DONOR = {t: rf'records\item\loottables\animalrelics\{t}_act3_yetifur.dbr'
                  for t in ('01', '02', '03')}
_WH_LOOT = {t: rf'records\item\loottables\animalrelics\svc_sepulchralscale\{t}_sepulchralscale.dbr'
            for t in ('01', '02', '03')}
_WH_LEVELREQ = {'01': 30, '02': 44, '03': 56}
# per-shard 5-arrays (escalate with each socketed shard); completion fear at full.
_WH_STATS = {
    '01': {'defensiveCold': [6.0, 12.0, 18.0, 24.0, 30.0],
           'offensiveColdMin': [10.0, 20.0, 30.0, 40.0, 50.0],
           'offensiveColdMax': [16.0, 32.0, 48.0, 64.0, 80.0],
           'offensiveSlowColdMin': [8.0, 16.0, 24.0, 32.0, 40.0],
           'offensiveSlowColdDurationMin': [1.0, 1.5, 2.0, 2.5, 3.0],
           'offensiveSlowRunSpeedMin': [8.0, 12.0, 16.0, 20.0, 24.0],
           'offensiveSlowRunSpeedDurationMin': [1.0, 1.25, 1.5, 1.75, 2.0],
           'characterLife': [40.0, 80.0, 120.0, 160.0, 200.0],
           'offensiveFearMin': [0.0, 0.0, 0.0, 0.0, 2.0]},
    '02': {'defensiveCold': [9.0, 18.0, 27.0, 36.0, 45.0],
           'offensiveColdMin': [15.0, 30.0, 45.0, 60.0, 75.0],
           'offensiveColdMax': [24.0, 48.0, 72.0, 96.0, 120.0],
           'offensiveSlowColdMin': [12.0, 24.0, 36.0, 48.0, 60.0],
           'offensiveSlowColdDurationMin': [1.0, 1.5, 2.0, 2.5, 3.0],
           'offensiveSlowRunSpeedMin': [10.0, 15.0, 20.0, 25.0, 30.0],
           'offensiveSlowRunSpeedDurationMin': [1.0, 1.5, 2.0, 2.5, 3.0],
           'characterLife': [70.0, 140.0, 210.0, 280.0, 350.0],
           'offensiveFearMin': [0.0, 0.0, 0.0, 0.0, 2.0]},
    '03': {'defensiveCold': [12.0, 24.0, 36.0, 48.0, 60.0],
           'offensiveColdMin': [22.0, 44.0, 66.0, 88.0, 110.0],
           'offensiveColdMax': [34.0, 68.0, 102.0, 136.0, 170.0],
           'offensiveSlowColdMin': [16.0, 32.0, 48.0, 64.0, 80.0],
           'offensiveSlowColdDurationMin': [1.0, 1.5, 2.0, 2.5, 3.0],
           'offensiveSlowRunSpeedMin': [12.0, 18.0, 24.0, 30.0, 36.0],
           'offensiveSlowRunSpeedDurationMin': [1.0, 1.5, 2.0, 2.5, 3.0],
           'characterLife': [100.0, 200.0, 300.0, 400.0, 500.0],
           'offensiveFearMin': [0.0, 0.0, 0.0, 0.0, 3.0]},
}


def _create_wyrm_hordes(db, tags):
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    if not db.has_record(_WH_COMMON_DONOR):
        print("  WYRM HORDES: WARNING common-wyrm donor missing; group skipped")
        return

    # ── 1. Common horde body (Common-classified derived wyrm) ──
    db.clone_record(_WH_COMMON_DONOR, _WH_COMMON)
    sf(_WH_COMMON, 'monsterClassification', 'Common')
    sf(_WH_COMMON, 'dropItems', 0)
    db._modified.add(_WH_COMMON)

    # ── 2. No-cap limit ──
    if db.has_record(_WH_LIMIT_DONOR):
        db.clone_record(_WH_LIMIT_DONOR, _WH_LIMIT)
        db._modified.add(_WH_LIMIT)
        limit_ref = _WH_LIMIT
    else:
        limit_ref = None

    # ── 3. New pools (clone firesprite pools; retheme to wyrm hordes) ──
    for t in ('01', '02', '03'):
        donor = _WH_POOL_DONOR[t]
        if not db.has_record(donor):
            raise SystemExit(f"WYRM HORDES: firesprite pool donor missing: {donor}")
        pool = _WH_POOL[t]
        db.clone_record(donor, pool)
        smin, smax = _WH_SIZE[t]
        sf(pool, 'FileDescription', f'Sepulchral Wyrm Horde tier {t}')
        sf(pool, 'spawnMin', smin)
        sf(pool, 'spawnMax', smax)
        # main slots -> the common wyrm (a true wyrm horde)
        sf(pool, 'name1', _WH_COMMON)
        sf(pool, 'name2', _WH_COMMON)
        sf(pool, 'name3', _WH_COMMON)
        sf(pool, 'name4', _WH_COMMON)
        if t == '03':
            # tier-03 champion config: the 4 champion worms lead the horde
            sf(pool, 'championChance', 100.0)
            sf(pool, 'championMin', 4)
            sf(pool, 'championMax', 6)
            for i, w in enumerate(_WH_CHAMP_WORMS, start=1):
                sf(pool, f'nameChampion{i}', w)
                sf(pool, f'weightChampion{i}', 100)
        else:
            # tiers 1/2 = pure common hordes (no champion crowd-out)
            sf(pool, 'championChance', 0.0)
            sf(pool, 'championMin', 0)
            sf(pool, 'championMax', 0)
        db._modified.add(pool)

    # ── 4. Repoint the 6 proxies to the new pools + no-cap limit ──
    for t, proxies in _WH_PROXY_TIERS.items():
        for px in proxies:
            if not db.has_record(px):
                raise SystemExit(f"WYRM HORDES: wyrmsprite proxy missing: {px}")
            sf(px, 'pool1', _WH_POOL[t])
            if limit_ref:
                sf(px, 'difficultyLimitsFile', limit_ref)
            db._modified.add(px)

    # ── 5. Sepulchral Scale charm (Emberscale/D10 pattern) ──
    for t in ('01', '02', '03'):
        donor = _WH_CHARM_DONOR[t]
        if not db.has_record(donor):
            raise SystemExit(f"WYRM HORDES: yeti-fur charm donor missing: {donor}")
        charm = _WH_CHARM[t]
        db.clone_record(donor, charm)
        sf(charm, 'description', 'tagSVCSepulchralScale')
        sf(charm, 'itemText', 'tagSVCSepulchralScaleDESC')
        sf(charm, 'FileDescription', 'Sepulchral Scale: cold + frostbite + fear on completion')
        sf(charm, 'levelRequirement', _WH_LEVELREQ[t])
        sf(charm, 'relicBitmap', r'Items\AnimalRelics\AnimalPart01B.tex')   # RelicAnimal01 art (yeti-fur bitmaps)
        sf(charm, 'shardBitmap', r'Items\AnimalRelics\AnimalPart01A.tex')
        for fname, arr in _WH_STATS[t].items():
            sf(charm, fname, list(arr))
        db._modified.add(charm)
        # loot table (clone the yeti-fur FixedWeight table; point at our charm)
        ldonor = _WH_LOOT_DONOR[t]
        if not db.has_record(ldonor):
            raise SystemExit(f"WYRM HORDES: yeti-fur loot-table donor missing: {ldonor}")
        lt = _WH_LOOT[t]
        db.clone_record(ldonor, lt)
        sf(lt, 'lootName1', charm)
        db._modified.add(lt)

    # ── 6. Wire the charm onto the 4 champion worms at 7% (a free lootMisc slot) ──
    loot_arr = [_WH_LOOT['01'], _WH_LOOT['02'], _WH_LOOT['03']]
    slot = None
    for cand in (3, 4, 2, 1):
        if all((db.get_field_value(w, f'lootMisc{cand}Item1') in (None, '', 0))
               for w in _WH_CHAMP_WORMS if db.has_record(w)):
            slot = cand
            break
    if slot is None:
        raise SystemExit("WYRM HORDES: no free lootMisc slot on the champion worms")
    for w in _WH_CHAMP_WORMS:
        if not db.has_record(w):
            raise SystemExit(f"WYRM HORDES: champion worm missing: {w}")
        sf(w, f'lootMisc{slot}Item1', list(loot_arr), S)
        sf(w, f'chanceToEquipMisc{slot}', 7.0)
        sf(w, f'chanceToEquipMisc{slot}Item1', 100)
        db._modified.add(w)

    tags['tagSVCSepulchralScale'] = 'Sepulchral Scale'
    tags['tagSVCSepulchralScaleDESC'] = (
        'A frost-riven scale shed by the sepulchral wyrms of the deep tombs. '
        'Cold clings to it, and the dead things it touched learned fear.')
    print(f"  Wyrm Hordes: common wyrm + 3 pools (4/8, 6/12, 8/16; tier03 champ "
          f"100/4/6) + no-cap limit; 6 wyrmsprite proxies repointed; Sepulchral "
          f"Scale charm x3 (lvlReq 30/44/56) @ 7% on 4 champion worms (lootMisc{slot})")


# ── BROODMOTHER NEST (deferred wyrm set-piece; docs/BROODMOTHER_NEST_DESIGN.md) ──
# WILL SIGNED OFF 2026-07-10 ("proceed with the broodmother nest implementation";
# 7 flagged decisions DELEGATED = take each doc recommendation, amgoz1 taste, NO
# artificial caps). The apex of the N7 sepulchral-wyrm-horde chain: a titanic
# mother wyrm coiled over an uncapped hatchery. She derives from the DRX
# Eater-of-Days rig (um_eaterofdays_45), which build31 D13 already proved render-
# AND summon-safe (its own summon_eaterofdays + pets passed the D19 mobility +
# summon-pet STRICT gates). While she lives the eggs never stop hatching (no
# petLimit-cap in spirit: 6 static egg clusters + a burst-4/petLimit-24 mother
# summon). Kill her before the room fills. Reward = a guaranteed apex tier-03
# Sepulchral Scale + (66% Finger2) the ONE summon of the set: the manual-cast
# Broodmother Soul (Skill_SpawnPet, NO itemSkillAutoController) whose friendly
# broodmother pet in turn raises a small FRIENDLY wyrmling brood (the pet-of-pet
# twist the Enslaver soul already ships). MAP-REF-1: these records (esp. the
# q_broodmother_lone + q_broodnest_egg_* proxies) land in the arz FIRST; the map
# lane then injects the placements (recommended host tombobs02, surveyed on-mesh).
_BM_BAND = [40, 58, 74]                        # Obsidian-guardian / Ilsevar Act-3 band
_BM_MONSTER = r'records\creature\monster\sepulchralwyrm\um_broodmother_99.dbr'
_BM_DONOR = r'records\creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr'          # DRX Eater-of-Days rig (D13-proven)
_BM_COMMON = r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_common_31.dbr'  # Common wyrmling (hatch + summon fodder + friendly-pet src)
_BM_ESCORT = r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_40.dbr'         # Champion elder-worm escort
# The uncapped hostile brood-summon (yaoguai clone; boss-kit clone-shape invariant).
_BM_SUMMON = r'records\skills\boss skills\svc_broodnest_summon.dbr'
_BM_SUMMON_DONOR = r'records\skills\boss skills\yaoguai_summonshadowstalkers.dbr'
# Egg-cluster hatch pool (clone a firesprite general pool; retheme to wyrmlings).
_BM_HATCH_POOL = r'records\proxies orient\pools\demon\svc_broodnest_hatch.dbr'
_BM_HATCH_POOL_DONOR = r'records\proxies orient\pools\demon\firesprite_01_general06.dbr'
# Lone-boss pool + proxy (q_leinth_lone "lone" pattern; Vashkarr accounting).
_BM_POOL = r'records\drxmap\proxy\pools\svc_broodmother_pool.dbr'
_BM_POOL_DONOR = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_BM_PROXY = r'records\drxmap\proxy\q_broodmother_lone.dbr'
_BM_PROXY_DONOR = r'records\drxmap\proxy\q_leinth_lone.dbr'
_BM_EGG_PROXIES = [rf'records\drxmap\proxy\q_broodnest_egg_{c}.dbr' for c in 'abcdef']  # 6 clusters (crazier; no caps)
# No-cap [1..110] limit (clone the BASE herolimit_all -> bump the max window to 110,
# the exact obsidian-limit recipe; build-order-independent - herolimit_all is a base
# record). Contains the mother L74 with headroom AND the L71 escort (eligibility-safe).
_BM_LIMIT = r'records\proxies orient\limit_broodnest.dbr'
_BM_LIMIT_DONOR = r'records\proxies boss\herolimit_all.dbr'   # base [1..75] -> bumped to [1..110]
_BM_DIFFICULTY = r'records\proxies orient\difficulty_04.dbr'
# Soul summon chain (fresh summon_broodmother + pet-of-pet friendly wyrmling brood).
_BM_SUMMON_SKILL = r'records\skills\soulskills\summon_broodmother.dbr'
_BM_PETS = [rf'records\skills\soulskills\pets\broodmother_{i}.dbr' for i in (1, 2, 3)]
_BM_WYRMLING_SUMMON = r'records\skills\soulskills\summon_broodmother_wyrmlings.dbr'
_BM_WYRMLING_PETS = [rf'records\skills\soulskills\pets\broodmother_wyrmling_{i}.dbr' for i in (1, 2, 3)]
# Guaranteed apex loot: the Group-G tier-03 Sepulchral Scale loot TABLE.
_BM_SCALE_LOOT = r'records\item\loottables\animalrelics\svc_sepulchralscale\03_sepulchralscale.dbr'
# TESTHUB yard placement (q_yard_ namespace; real records; 100%).
_BM_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_broodmother.dbr'
_BM_YARD_PROXY = r'records\drxmap\proxy\q_yard_broodmother.dbr'
# Mother kit (all existence-verified vs the eater's own kit + this build's records).
_BM_SK_NECROBOLT = r'records\skills\monster skills\attack_projectile\eaterofdays_necrobolt.dbr'
_BM_SK_ARMOR = r'records\skills\monster skills\defense\armor_passive.dbr'
_BM_SK_FROSTSLOW = r'records\skills\monster skills\passive_buffs\raptor_frostslow.dbr'
_BM_SK_DEFLECT = r'records\skills\monster skills\defense\deflectprojectiles_passive.dbr'
_BM_SK_CIRCLEOFDECAY = r'records\skills\boss skills\alastor_circleofdecay.dbr'
_BM_SK_FIREBREATH = r'records\skills\monster skills\attack_melee\sepulchralwyrm_firebreath.dbr'
_BM_SK_SPELLBREAKER = r'records\skills\monster skills\attack_radius\spellbreaker.dbr'
_BM_SK_COLDBONUS = r'records\skills\monster skills\passive_buffs\bonusdamage_cold_+5perlevelx500.dbr'
_BM_SK_BOSSIMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_BM_SK_BOSSSCALING = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
_BM_SK_GP_N = r'records\skills\monster skills\globalproperties_normal01.dbr'
_BM_SK_GP_E = r'records\skills\monster skills\globalproperties_epic01.dbr'
_BM_SK_GP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'


def _create_broodmother_nest(db, tags):
    """Build the whole Broodmother Nest DB side in dependency order: the uncapped
    hostile brood-summon -> the mother boss (Eater-of-Days derivation; kit + brood
    summon) -> egg-cluster hatch pool -> no-cap limit -> lone-boss pool (2 guaranteed
    escorts) -> lone + 6 egg proxies -> friendly wyrmling pet-of-pet -> the
    broodmother pets + manual summon (hostile->friendly repoint) -> soul (manual
    cast, 2 cold augments, weird stat, 66% Finger2) -> guaranteed tier-03 Sepulchral
    Scale loot hook -> TESTHUB yard pool/proxy -> tags. Monster.tpl clone -> free to
    add resist fields (Vashkarr precedent); dtype-free set_field on clones preserves
    each field's type. All refs existence-verified. Must run AFTER _create_wyrm_hordes
    (the tier-03 scale loot table + the champion/common wyrms it references exist)."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    for donor in (_BM_DONOR, _BM_COMMON, _BM_ESCORT, _BM_SUMMON_DONOR,
                  _BM_HATCH_POOL_DONOR, _BM_POOL_DONOR, _BM_PROXY_DONOR,
                  _BM_LIMIT_DONOR):
        if not db.has_record(donor):
            print(f"  BROODMOTHER: WARNING donor missing: {donor}; group skipped")
            return
    if not db.has_record(_BM_SCALE_LOOT):
        print(f"  BROODMOTHER: WARNING tier-03 scale loot table missing "
              f"({_BM_SCALE_LOOT}); group skipped (run after _create_wyrm_hordes)")
        return

    def _clear_skill_slots_above(rec, keep):
        """Delete skillName slots above `keep` the donor carried (avoid stray donor
        skills; DELETE not blank, per the B-TOXEUS-2 empty-ref law)."""
        ff = db.get_fields(rec)
        if not ff:
            return
        for key in [k for k in list(ff) if k.split('###')[0].startswith('skillName')]:
            base = key.split('###')[0]
            try:
                n = int(base[len('skillName'):])
            except ValueError:
                continue
            if n > keep:
                del ff[key]
        db._modified.add(rec)

    # ── 1. The uncapped hostile brood-summon (yaoguai clone; only existing fields
    #    changed -> loader-safe + boss-kit clone-shape invariant). Spawns PURE common
    #    wyrmlings (Common, no soul, no scale drop) so the churn is fodder, never a
    #    scale-loot / over-tough flood; the guaranteed champion escorts come from the
    #    pool (2d), keeping the two density sources cleanly separate. burst 4 / cd 5 /
    #    petLimit 24 = "no cap" in spirit (the engine needs a finite petLimit). ──
    db.clone_record(_BM_SUMMON_DONOR, _BM_SUMMON)
    sf(_BM_SUMMON, 'spawnObjects', [_BM_COMMON])
    sf(_BM_SUMMON, 'petBurstSpawn', 4)
    sf(_BM_SUMMON, 'skillCooldownTime', 5.0)
    sf(_BM_SUMMON, 'petLimit', 24)
    db._modified.add(_BM_SUMMON)
    _BOSS_KIT_CLONES.append((_BM_SUMMON_DONOR, _BM_SUMMON))

    # ── 2. THE BROODMOTHER (boss). Clone the Eater-of-Days rig; override identity /
    #    power / kit. Keep the eater's proven anim-safe wyrm kit, upgrade Hero->Boss
    #    passives, add firebreath + the brood-summon; she summons OFTEN. ──
    db.clone_record(_BM_DONOR, _BM_MONSTER)
    M = _BM_MONSTER
    sf(M, 'description', 'tagSVCMonsterBroodmother')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'charLevel', list(_BM_BAND))
    sf(M, 'characterLife', [22000.0, 30000.0, 40000.0])
    sf(M, 'characterLifeRegen', [40.0, 70.0, 110.0])
    sf(M, 'scale', 1.9)                                       # visibly the mother
    sf(M, 'actorHeight', 2.4)
    # boss resistance wall (new fields auto-FLOAT on the Monster.tpl clone)
    sf(M, 'defensiveLife', 100.0)
    sf(M, 'defensivePierce', 60.0)
    sf(M, 'defensiveCold', 80.0)                              # she IS the cold
    sf(M, 'defensivePhysical', 30.0)
    kit = [
        _BM_SK_NECROBOLT, _BM_SK_ARMOR, _BM_SK_FROSTSLOW, _BM_SK_DEFLECT,
        _BM_SK_CIRCLEOFDECAY, _BM_SK_FIREBREATH, _BM_SK_SPELLBREAKER,
        _BM_SK_COLDBONUS, _BM_SUMMON, _BM_SK_BOSSIMMUNITY, _BM_SK_BOSSSCALING,
        _BM_SK_GP_N, _BM_SK_GP_E, _BM_SK_GP_L,
    ]
    for i, sk in enumerate(kit, start=1):
        sf(M, f'skillName{i}', sk)
    _clear_skill_slots_above(M, len(kit))
    sf(M, 'initialSkillName', _BM_SK_CIRCLEOFDECAY)           # persistent death aura (eater default)
    # AI rotation: summon the brood OFTEN (the nest churns even without the static
    # clusters), necrobolt + firebreath as the offensive specials.
    sf(M, 'specialAttackSkillName', _BM_SUMMON)
    sf(M, 'specialAttackChance', 55.0)
    sf(M, 'specialAttack2SkillName', _BM_SK_NECROBOLT)
    sf(M, 'specialAttack2Chance', 40.0)
    sf(M, 'specialAttack3SkillName', _BM_SK_FIREBREATH)
    sf(M, 'specialAttack3Chance', 50.0)
    db._modified.add(M)

    # ── 3. Egg-cluster hatch pool (clone a firesprite general pool; pure common
    #    wyrmling fodder, 3-6 per cluster, no champion crowd-out). ──
    db.clone_record(_BM_HATCH_POOL_DONOR, _BM_HATCH_POOL)
    HP = _BM_HATCH_POOL
    sf(HP, 'FileDescription', 'Broodmother nest egg cluster (common wyrmling hatch)')
    for i in (1, 2, 3, 4):
        sf(HP, f'name{i}', _BM_COMMON)
    sf(HP, 'spawnMin', 3); sf(HP, 'spawnMax', 6)
    sf(HP, 'championChance', 0.0); sf(HP, 'championMin', 0); sf(HP, 'championMax', 0)
    db._modified.add(HP)

    # ── 4. No-cap [1..110] limit (clone base herolimit_all -> bump max window to
    #    110, the exact obsidian-limit recipe; contains the mother L74 + escort L71
    #    with headroom). Build-order-independent (herolimit_all is a base record). ──
    db.clone_record(_BM_LIMIT_DONOR, _BM_LIMIT)
    for f in ('maxPlayerLevelEquationNormal', 'maxPlayerLevelEquationEpic',
              'maxPlayerLevelEquationLegendary'):
        sf(_BM_LIMIT, f, '110*1')
    sf(_BM_LIMIT, 'FileDescription', 'Broodmother nest no-cap limit [1..110]')
    db._modified.add(_BM_LIMIT)

    # ── 5. Lone-boss pool: 1 mother + 2 guaranteed um_sepulchralwyrm_40 escorts
    #    (spawnMax=3 / championMin=Max=2 -> 3-2 = 1 guaranteed main = the mother;
    #    the spawnMax-championMax>=1 LAW holds). Clear the leinth clone-leftover
    #    3rd champion (Vashkarr fix). ──
    db.clone_record(_BM_POOL_DONOR, _BM_POOL)
    PL = _BM_POOL
    sf(PL, 'FileDescription', 'Broodmother (main) + 2 elder-worm champion escorts')
    sf(PL, 'name1', _BM_MONSTER)
    sf(PL, 'name2', _BM_MONSTER)
    sf(PL, 'name3', _BM_MONSTER)
    sf(PL, 'nameChampion1', _BM_ESCORT)
    sf(PL, 'nameChampion2', _BM_ESCORT)
    sf(PL, 'nameChampion3', '')
    sf(PL, 'weightChampion1', 50)
    sf(PL, 'weightChampion2', 50)
    sf(PL, 'weightChampion3', 0)
    sf(PL, 'spawnMin', 3); sf(PL, 'spawnMax', 3)
    sf(PL, 'championChance', 100.0); sf(PL, 'championMin', 2); sf(PL, 'championMax', 2)
    db._modified.add(PL)

    def _make_nest_proxy(proxy, pool_ref, extents, mesh_from=None, scale=None):
        db.clone_record(_BM_PROXY_DONOR, proxy)
        sf(proxy, 'pool1', pool_ref)
        sf(proxy, 'chanceToRun', 100.0)
        sf(proxy, 'difficultyLimitsFile', _BM_LIMIT)
        sf(proxy, 'difficultyEquationFile', _BM_DIFFICULTY)
        sf(proxy, 'placementExtents', float(extents))
        if mesh_from and db.has_record(mesh_from):
            m = db.get_field_value(mesh_from, 'mesh')
            m = m[0] if isinstance(m, list) else m
            if m and str(m).strip():
                sf(proxy, 'mesh', str(m))
        if scale is not None:
            sf(proxy, 'scale', float(scale))
        db._modified.add(proxy)

    # ── 6. The mother placement (lone proxy) + the 6 egg-cluster proxies. ──
    _make_nest_proxy(_BM_PROXY, _BM_POOL, 3.5, mesh_from=_BM_MONSTER, scale=1.9)
    for egg in _BM_EGG_PROXIES:
        _make_nest_proxy(egg, _BM_HATCH_POOL, 2.5, mesh_from=_BM_COMMON, scale=1.0)

    # ── 7. Friendly wyrmling pet-of-pet brood (the soul's brood twist): 3 friendly
    #    wyrmling pets on the SepulchralWyrm01 rig (Voranthys-proven as a pet) +
    #    their summon skill (auto-cast by the broodmother pet, NOT a player button:
    #    isPetDisplayable off, low petLimit). ──
    if not _build_boss_summon(
            db, _BM_COMMON, _BM_WYRMLING_PETS, _BM_WYRMLING_SUMMON,
            'tagSVCSummonBroodmotherBrood', 'tagSVCMonsterBroodmotherWyrmling',
            char_level=[31, 51, 66], life=[1200.0, 2000.0, 3000.0],
            life_regen=[10.0, 20.0, 30.0],
            dmg_min=[40.0, 70.0, 110.0], dmg_max=[70.0, 110.0, 160.0], scale=1.0,
            loadout=_mirror_source_loadout(db, _BM_COMMON)):
        raise SystemExit('BROODMOTHER: wyrmling pet-of-pet _build_boss_summon failed')
    sf(_BM_WYRMLING_SUMMON, 'isPetDisplayable', 0)
    sf(_BM_WYRMLING_SUMMON, 'petLimit', 6)
    sf(_BM_WYRMLING_SUMMON, 'petBurstSpawn', 2)
    sf(_BM_WYRMLING_SUMMON, 'skillCooldownTime', 8.0)
    sf(_BM_WYRMLING_SUMMON, 'skillManaCost', 0.0)
    db._modified.add(_BM_WYRMLING_SUMMON)

    # ── 8. The manual-cast Broodmother summon (3 permanent pets on the mother's own
    #    Eater-of-Days rig, D13-proven) + the player summon skill. Then repoint the
    #    pet's inherited HOSTILE brood-summon -> the FRIENDLY wyrmling summon so the
    #    broodmother pet raises FRIENDLY wyrmlings (never enemies), the exact Enslaver
    #    pet-of-pet mechanism. ──
    if not _build_boss_summon(
            db, _BM_MONSTER, _BM_PETS, _BM_SUMMON_SKILL,
            'tagSVCSummonBroodmother', 'tagSVCMonsterBroodmother',
            char_level=list(_BM_BAND), life=[16000.0, 22000.0, 30000.0],
            life_regen=[30.0, 60.0, 100.0],
            dmg_min=[70.0, 110.0, 160.0], dmg_max=[110.0, 170.0, 250.0], scale=1.6,
            loadout=_mirror_source_loadout(db, _BM_MONSTER)):
        raise SystemExit('BROODMOTHER: summon_broodmother _build_boss_summon failed')
    _hostile = _BM_SUMMON.replace('/', '\\').lower()
    for p in _BM_PETS:
        if not db.has_record(p):
            continue
        ff = db.get_fields(p) or {}
        for k, tf in ff.items():
            for j, v in enumerate(list(tf.values)):
                if isinstance(v, str) and v.replace('/', '\\').lower() == _hostile:
                    tf.values[j] = _BM_WYRMLING_SUMMON
        sf(p, 'specialAttackSkillName', _BM_WYRMLING_SUMMON)
        sf(p, 'specialAttackChance', 40.0)
        db._modified.add(p)

    # ── 9. The soul (amgoz1 voice, the ONE summon). Dense cold/vitality sheet + 2
    #    thematic cold augments (Cold Aura + Death Chill Aura) + one weird signature
    #    stat (defensiveFreeze 100 - the cold mother cannot be frozen). Grants the
    #    MANUAL summon (_wire_summon_soul strips any inherited itemSkillAutoController
    #    -> a pet BUTTON, never an on-attack proc). 66% Finger2, ONLY on the mother. ──
    def _bm_stats(t, il):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        lvl = {'n': 3, 'e': 4, 'l': 5}[t]
        return {
            **_bmp(t),
            'augmentSkillName1': (S, _SK_COLD_AURA), 'augmentSkillLevel1': (I, lvl),
            'augmentSkillName2': (S, _SK_DEATH_CHILL), 'augmentSkillLevel2': (I, lvl),
            'characterLife': (F, r(360.0)), 'characterLifeModifier': (F, r(14.0)),
            'characterLifeRegen': (F, r(12.0)),
            'characterIntelligence': (F, r(40.0)), 'characterIntelligenceModifier': (F, r(8.0)),
            'characterManaModifier': (F, r(12.0)),
            'characterOffensiveAbility': (F, r(90.0)),
            'characterSpellCastSpeedModifier': (I, int(r(16))),
            'offensiveColdMin': (F, r(60.0)), 'offensiveColdMax': (F, r(95.0)),
            'offensiveColdModifier': (I, int(r(35))),
            'offensiveLifeMin': (F, r(40.0)), 'offensiveLifeMax': (F, r(65.0)),
            'offensiveLifeModifier': (I, int(r(25))),
            'offensiveSlowColdMin': (F, r(60.0)), 'offensiveSlowColdDurationMin': (F, 3.0),
            'offensiveSlowRunSpeedMin': (F, r(30.0)), 'offensiveSlowRunSpeedDurationMin': (F, 2.0),
            'offensiveLifeLeechMin': (F, r(25.0)),
            'defensiveFreeze': (F, 100.0),        # weird signature: the cold mother cannot be frozen
            'defensiveCold': (F, r(45.0)), 'defensiveLife': (F, r(22.0)),
            'characterDefensiveAbility': (F, r(60.0)),
        }
    bm_tiers = [{'diff': t, 'itemLevel': il, 'stats': _bm_stats(t, il)}
                for t, il in (('n', 40), ('e', 58), ('l', 74))]
    bm_souls = _create_soul(db, 'broodmother', 'tagSVCSoulBroodmother', bm_tiers,
                            monster=_BM_MONSTER, drop_rate=66.0)
    _wire_summon_soul(db, bm_souls, _BM_SUMMON_SKILL)   # manual: strip controller, level 1/2/3

    # ── 10. Guaranteed apex loot: the tier-03 Sepulchral Scale on a DEDICATED Misc3
    #    slot at 100% (the nest is where a player reliably completes the horde charm).
    #    Repurposes the eater-inherited low-value Misc3 slot; soul stays on Finger2. ──
    sf(M, 'chanceToEquipMisc3', 100.0)
    sf(M, 'lootMisc3Item1', [_BM_SCALE_LOOT, _BM_SCALE_LOOT, _BM_SCALE_LOOT], S)
    sf(M, 'chanceToEquipMisc3Item1', 100, I)
    for j in (2, 3, 4, 5, 6):
        sf(M, f'chanceToEquipMisc3Item{j}', 0, I)
    db._modified.add(M)

    # ── 11. TESTHUB yard placement (q_yard_ namespace; REAL records; 100%): the full
    #    nest (mother + 2 escorts) so the map lane can give Will a yard spot to fight
    #    and tune her 1:1. INERT on the canonical/Steam map (only the TESTHUB map
    #    places it). Registered in _MOD_AUTHORED_SPAWN_PROXIES (spawn-eligibility). ──
    db.clone_record(_BM_POOL_DONOR, _BM_YARD_POOL)
    YP = _BM_YARD_POOL
    sf(YP, 'FileDescription', 'YARD: Broodmother nest (mother + 2 escorts) @100% (TESTHUB-only)')
    sf(YP, 'name1', _BM_MONSTER); sf(YP, 'name2', _BM_MONSTER); sf(YP, 'name3', _BM_MONSTER)
    sf(YP, 'nameChampion1', _BM_ESCORT); sf(YP, 'nameChampion2', _BM_ESCORT)
    sf(YP, 'nameChampion3', '')
    sf(YP, 'weightChampion1', 50); sf(YP, 'weightChampion2', 50); sf(YP, 'weightChampion3', 0)
    sf(YP, 'spawnMin', 3); sf(YP, 'spawnMax', 3)
    sf(YP, 'championChance', 100.0); sf(YP, 'championMin', 2); sf(YP, 'championMax', 2)
    db._modified.add(YP)
    _make_nest_proxy(_BM_YARD_PROXY, _BM_YARD_POOL, 3.5, mesh_from=_BM_MONSTER, scale=1.9)

    # ── 12. Tags (Text.arc COUPLED with the arz; validate_tags must pass). ──
    tags['tagSVCMonsterBroodmother'] = '{^r}The Broodmother of the Deep'
    tags['tagSVCMonsterBroodmotherWyrmling'] = 'Broodmother Wyrmling'
    tags['tagSVCSummonBroodmother'] = 'Summon the Broodmother'
    tags['tagSVCSummonBroodmotherBrood'] = 'Spawn the Brood'
    tags['tagSVCSoulBroodmother'] = '{^F}Broodmother Soul'
    tags['tagSVCSoulBroodmotherDESC'] = (
        'Torn from the Broodmother of the Deep, the titanic mother wyrm whose eggs '
        'never stopped hatching. It calls her forth to coil at your side, and her '
        'brood spills out to swarm your enemies in her cold.')
    print("  Broodmother Nest: mother boss (Eater-of-Days rig, band [40,58,74], HP "
          "[22k,30k,40k], cold wall) + uncapped brood-summon (burst 4/cd 5/petLimit "
          "24) + egg hatch pool (3-6 common) + no-cap limit + lone pool (1 mother + "
          "2 escorts) + 1 lone proxy + 6 egg proxies + friendly wyrmling pet-of-pet "
          "+ manual Broodmother Soul (66% Finger2, cold augments, defensiveFreeze) + "
          "guaranteed tier-03 Sepulchral Scale (Misc3@100) + TESTHUB yard; tags set")


# ── GROUP F (build32): N6 Obsidian Halls Treasure Roulette ──────────────────
# WILL SIGNED OFF 2026-07-09 (docs/OBSIDIAN_ROULETTE_DESIGN.md, all decisions
# locked). Four guardian bosses derived from region natives with wild theatrical
# kits + ondeath skills; a shared 4-boss warband pool (spawnMin=Max=6,
# championChance=100, championMin=Max=5 -> 6-5=1 guaranteed main = a RANDOM
# guardian; the LAW holds); four corner proxies (chanceToRun=25 = the roulette
# dial) each carrying pool1=the shared pool AND the accessory chest chain
# (accessory1/Epic1/Legendary1 -> ProxyAccessoryPool -> FixedItemContainer),
# exactly the shipped 1,819-proxy monster+container pattern (donor
# proxy_hidden_bloodcave_chest, TutorialPotionChestProxy chain). One Boss-locked
# Obsidian Hoard chest per difficulty (clone of the blood-cave mega chest,
# container_hpalace_chestlg01.msh scale 1.4, LockedClassification=Boss/50,
# goldGeneratorChance=100, below-mega loot). Four amgoz1-voice souls: Sarkoth +
# Gorrahk = MANUAL pcsafe signature-move grants (typhon_meteorstorm 2/3/4 /
# cyclops_groundsmash 3/4/5); Voranthys = THE ONE SUMMON (manual summon_voranthys
# via _build_boss_summon on the render-verified SepulchralWyrm01 rig, D19 +
# damage-sanity gated); Ilsevar = lifedrain ON-ATTACK proc (autocast correct -
# manual-cast law binds only Skill_SpawnPet grants). MAP-REF-1: the
# q_obs_roulette_{a,b,c,d} records MUST land in the arz BEFORE the map lane
# injects the 4 INJECT_SPECS + shared v0e branch (M10).
_OBS_BAND = [40, 58, 72]                 # Sarkoth/Gorrahk/Voranthys band
_OBS_BAND_ILS = [42, 60, 74]             # Ilsevar band
# Guardian monsters (derive natives; rig + anim table stay compatible - D5).
_OBS_SARKOTH = r'records\creature\monster\abyssalliche\um_sarkoth_99.dbr'
_OBS_SARKOTH_DONOR = r'records\xpack\creatures\monster\abyssalliche\uw_as_abyssalliche_flame_42.dbr'  # LicheKing02Flame caster
_OBS_GORRAHK = r'records\creature\monster\skeleton\um_gorrahk_99.dbr'
_OBS_GORRAHK_DONOR = r'records\creature\monster\skeleton\orient_cm_gildedskeleton_27.dbr'  # GoldenSkeleton01 melee
_OBS_VORANTHYS = r'records\creature\monster\questbosses\um_voranthys_99.dbr'
_OBS_VORANTHYS_DONOR = r'records\creature\monster\questbosses\boss_dragonliche_57.dbr'  # DragonLich01 summon-storm boss
_OBS_ILSEVAR = r'records\creature\monster\skeleton\um_ilsevar_99.dbr'
_OBS_ILSEVAR_DONOR = r'records\creature\monster\skeleton\cm_revenantstorm_17.dbr'  # RevenantStorm poltergeist
# Voranthys summon pet rig (SepulchralWyrm01 per design section 3).
_OBS_VORANTHYS_PET_SRC = r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_31.dbr'
SUMMON_VORANTHYS_SKILL = r'records\skills\soulskills\summon_voranthys.dbr'
# Kit skills (all existence-verified this session).
_OBS_SK_DROPTELE = r'records\skills\boss skills\ormenos_droptelekinesis.dbr'
_OBS_SK_ARENAMETEOR = r'records\skills\monster skills\attack_radius\arena_meteor.dbr'
_OBS_SK_VOLCORB = r'records\skills\earth\volcanicorb.dbr'
_OBS_SK_VOLCFRAG = r'records\skills\earth\volcanicorb_fragmentation.dbr'
_OBS_SK_VOLCIMMO = r'records\skills\earth\volcanicorb_immolation.dbr'
_OBS_SK_RINGFLAME = r'records\skills\earth\ringofflame.dbr'
_OBS_SK_ICESHARD = r'records\skills\storm\iceshard.dbr'
_OBS_SK_SQUALL = r'records\skills\storm\squall.dbr'
_OBS_SK_SPELLBREAKER = r'records\skills\storm\drxspellbreaker.dbr'
_OBS_SK_ONDEATH_FROSTNOVA = r'records\skills\monster skills\attack_radius\ondeath_frostnova.dbr'
_OBS_SK_BLADESTORM = r'records\skills\monster skills\attack_radius\bladestorm.dbr'
_OBS_SK_GROUNDSMASH = r'records\skills\soulskills\cyclops_groundsmash.dbr'
_OBS_SK_TERRIFYROAR = r'records\skills\boss skills\cyclops_terrifyingroar.dbr'
_OBS_SK_DMGMOD = r'records\skills\monster skills\passive_buffs\attack_damagemodifier_02.dbr'
_OBS_SK_SPEEDALL = r'records\skills\monster skills\auras\character_speedall.dbr'
_OBS_SK_ONDEATH_BLADENOVA = r'records\skills\monster skills\ondeath\skills\bladenova.dbr'
_OBS_SK_FIREBREATH = r'records\skills\monster skills\attack_melee\sepulchralwyrm_firebreath.dbr'
_OBS_SK_FREEZEBREATH = r'records\skills\boss skills\dragonliche_freezingbreath.dbr'
_OBS_SK_DECOMP = r'records\skills\boss skills\dragonliche_decomposition.dbr'
_OBS_SK_BUFFETWINGS = r'records\skills\boss skills\dragonliche_buffetingwings.dbr'
_OBS_SK_SUMMONARCHER = r'records\skills\boss skills\alastor_summonskeletonarcher.dbr'
_OBS_SK_SUMMONWARRIOR = r'records\skills\boss skills\alastor_summonskeletonwarrior.dbr'
_OBS_SK_SUMMONTOMB = r'records\skills\boss skills\aktaios_summontombguardians.dbr'
_OBS_SK_ONDEATH_SPAWNSKEL = r'records\skills\monster skills\ondeath_spawnskeleton.dbr'
_OBS_SK_ONDEATH_NECRONOVA = r'records\skills\monster skills\attack_radius\ondeath_necronova.dbr'
_OBS_SK_PHANTOMSTRIKE = r'records\skills\monster skills\attack_melee\phantomstrike.dbr'
_OBS_SK_KIKASTRIKE = r'records\skills\monster skills\attack_projectile\kika_phantomstrike.dbr'
_OBS_SK_DISTORTWAVE = r'records\xpack\skills\dream\distortionwave.dbr'   # xpack (base twin dangles)
_OBS_SK_LIFEDRAIN = r'records\skills\spirit\lifedrain.dbr'
_OBS_SK_DEATHCHILLAURA = r'records\skills\spirit\drxdeathchillaura.dbr'
_OBS_SK_HALIROAR = r'records\skills\monster skills\attack_projectile\halimedes_terrifyingroar.dbr'
_OBS_SK_ONDEATH_DETONATE = r'records\skills\monster skills\attack_radius\ondeath_detonate.dbr'
# Boss passive suite (shared).
_OBS_SK_BOSSIMMUNITY = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_OBS_SK_BOSSSCALING = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
_OBS_SK_ARMORPASSIVE = r'records\skills\monster skills\defense\armor_passive.dbr'
_OBS_SK_GP_N = r'records\skills\monster skills\globalproperties_normal01.dbr'
_OBS_SK_GP_E = r'records\skills\monster skills\globalproperties_epic01.dbr'
_OBS_SK_GP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'
# Soul-grant skills (pcsafe = player-castable) + augments.
_OBS_SS_TYPHON_METEOR = r'records\skills\soulskills\pcsafe\typhon_meteorstorm.dbr'   # Sarkoth manual grant
_OBS_SS_GROUNDSMASH_PC = r'records\skills\soulskills\pcsafe\cyclops_groundsmash.dbr'  # Gorrahk manual grant
_OBS_AUG_VOLCORB = r'records\skills\earth\drxvolcanicorb.dbr'
_OBS_AUG_STONESKIN = r'records\skills\earth\drxfireenchantment_stoneskin.dbr'
_OBS_AUG_CONCUSSIVE = r'records\skills\defensive\drxconcussiveblow.dbr'
_OBS_AUG_ONSLAUGHT = r'records\skills\warfare\drxonslaught.dbr'
_OBS_AUG_COLDAURA = r'records\skills\storm\drxcoldaura.dbr'
_OBS_AUG_DEATHCHILL = r'records\skills\spirit\drxdeathchillaura.dbr'
_OBS_AUG_PHANTOMSTRIKE = r'records\xpack\skills\dream\drxphantomstrike.dbr'   # xpack (base dream twin dangles)
_OBS_AUG_DISTORTWAVE = r'records\xpack\skills\dream\drxdistortionwave.dbr'    # xpack
# Warband champions (6, equal weights): 3 abyssalliche Champs + permean hero +
# a dragonian champ + a golden-skeleton hero.
_OBS_WARBAND = [
    r'records\creature\monster\abyssalliche\us_abyssalliche_flame_42.dbr',
    r'records\creature\monster\abyssalliche\us_abyssalliche_frost_42.dbr',
    r'records\creature\monster\abyssalliche\us_abyssalliche_plague_42.dbr',
    r'records\creature\monster\dragonlich\um_permean_35.dbr',
    r'records\creature\monster\dragonian\em_ravager_41.dbr',
    r'records\creature\monster\skeleton\um_bonehallow_37.dbr',
]
# Proxy/pool/limit/chest chain.
_OBS_WARBAND_POOL = r'records\drxmap\proxy\pools\q_obs_warband.dbr'
_OBS_POOL_DONOR = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_OBS_PROXY_DONOR = r'records\drxmap\proxy\q_leinth_lone.dbr'
_OBS_CORNERS = {c: rf'records\drxmap\proxy\q_obs_roulette_{c}.dbr' for c in 'abcd'}
_OBS_LIMIT = r'records\proxies orient\limit_obsidianbosses.dbr'
_OBS_LIMIT_DONOR = r'records\proxies boss\herolimit_all.dbr'
_OBS_DIFFICULTY = r'records\proxies orient\difficulty_04.dbr'
_OBS_CHEST = {t: rf'records\drxitem\container\svc_obsidianhoard_{t}.dbr' for t in ('01', '02', '03')}
_OBS_CHEST_DONOR = {t: rf'records\drxitem\container\hidden_bloodcave_chest_{t}.dbr' for t in ('01', '02', '03')}
_OBS_HOARD_LOOT = {t: rf'records\drxitem\container\svc_obsidianhoard_loot_{t}.dbr' for t in ('01', '02', '03')}
_OBS_HOARD_LOOT_DONOR = {t: rf'records\drxitem\container\loottable_hidden_bloodcave_{t}.dbr' for t in ('01', '02', '03')}
_OBS_ACC_POOL = {t: rf'records\drxitem\container\svc_obsidianhoard_pool_{t}.dbr' for t in ('01', '02', '03')}
_OBS_ACC_POOL_DONOR = {t: rf'records\drxitem\container\pool_hidden_{t}.dbr' for t in ('01', '02', '03')}
# Guaranteed high-value table for the hoard's loot3 slot (already resolves - the
# mega chest references it in loot1Name3).
_OBS_GUAR_UNIQUE = r'records\xpack\item\loottables\weapons\mastertables\unique_1h_n01.dbr'
_OBS_GUAR_RELIC = r'records\xpack\item\loottables\relics\01_act4_relics.dbr'


# ── RUNE GOLEM (SVAERA Runemaster graft; docs/SVAERA_MASTERY_COMPARISON.md §3/§5.2) ──
# Will signed off 2026-07-10 ("yes make them"). This is the doc's deferred, D5-blocked
# item: a durable elite Runemaster construct pet whose mesh lived only in SVAERA's
# unshipped ~430MB _DRX_Meshes.arc. The render closure was proven CLEAN and extracted
# into two shipped minimal arcs (assets/runegolem/_DRX_Meshes.arc = mesh + 3 skins +
# glow + spawn anim, 6 files; _DRX_Textures.arc = 4 skill-bar icons); EVERY other art
# ref resolves in base AE (the mesh's own shader Shaders\standardglowskinned.ssh is
# base-scoped - NOT the XPack-scoped melinoe trap; granitegolem bump + EarthElemental
# anims + party icons all base). Proof: tools/validate_render_chain_golem.py resolves
# the whole pet render chain against OUR arcs only.
# The records are a faithful snapshot of the TREE-WIRED xpack2 golem set
# (assets/runegolem/runegolem_svaera_snapshot.json - the copy actually referenced by
# SVAERA's _drx_runemaster_skilltree + mastery-10 UI, not the unreferenced monster-
# skills orphan). SVAERA-only COSMETIC deps are repointed to base so NOTHING but the
# render closure is added: the Menhir-Wall prerequisite -> vanilla menhirwall (present
# on our base-inherited Runemaster tree at UI skill21); the custom death/summon .pfx FX
# (in the unshipped _DRX_Effects.arc) and custom sound paks -> dropped / base stone
# sound. Appended as a NEW Runemaster tree slot (UI skill23, grid 628,217 = directly
# above Menhir Wall) - additive, character-safe (never renumbers an existing slot,
# never swaps the tree pointer to SVAERA's _drx tree, so no invested points are
# stranded). Summon cast anim = ThunderClap (covered by the G0 anim-row completion).
_RG_SNAPSHOT = (Path(__file__).resolve().parent.parent / 'assets' / 'runegolem'
                / 'runegolem_svaera_snapshot.json')
_RG_SUMMON = r'records\xpack2\skills\runemaster\_drx_runegolem.dbr'
_RG_UI = r'records\xpack2\ui\skills\mastery 10\skill23.dbr'
_RG_MENHIR_BASE = r'records\xpack2\skills\runemaster\menhirwall.dbr'   # vanilla, on our tree
_RG_STONE_SOUND = r'Records\Sounds\SoundPak\Armor\StoneImpactPak.dbr'  # base (pet impactSound already uses it)


def _create_rune_golem(db, tags):
    """Graft the SVAERA Rune Golem onto our vanilla Runemaster tree from a committed
    faithful snapshot: 35 records (summon skill + 20-tier pet ladder + 7 pet-skills +
    6 stat passives + AI controller) + 1 appended UI tree slot + 6 Text tags. Render
    art ships in assets/runegolem/*.arc (staged into Resources by bootstrap/deploy);
    the D5 render closure is proven by tools/validate_render_chain_golem.py. Cosmetic
    SVAERA-only deps are repointed/dropped to base (menhir prereq -> vanilla; FX/sounds
    -> base) so only the render closure is a new asset. Additive + character-safe."""
    import json
    S, I = DATA_TYPE_STRING, DATA_TYPE_INT
    if not _RG_SNAPSHOT.exists():
        print(f"  RUNE GOLEM: WARNING snapshot missing ({_RG_SNAPSHOT}); group skipped")
        return
    snap = json.loads(_RG_SNAPSHOT.read_text(encoding='utf-8'))

    def _put(path, rectype, fields, drop=(), repoint=None):
        _ensure_record(db, path, rectype)
        for name, dt, vals in fields:
            if name in drop:
                continue
            v = list(repoint[name]) if (repoint and name in repoint) else list(vals)
            db.set_field(path, name, v, dt)
        db._modified.add(path)

    created = 0
    # 1) non-pet records (summon skill, 7 pet-skills, 6 passives, AI controller)
    for path, rec in snap['records'].items():
        drop, repoint = (), None
        if path.lower() == _RG_SUMMON.lower():
            # keep the Menhir-Wall prereq but point it at OUR vanilla menhirwall
            repoint = {'skillDependancy': [_RG_MENHIR_BASE]}
        if path.lower().endswith('_drx_runegolem_petskill_catalystbuff.dbr'):
            # drop the SVAERA-only catalyst aura FX (in the unshipped _DRX_Effects.arc);
            # the passive mana buff still applies, just without the custom sparkle
            drop = ('skillCastAuraName', 'targetFxPakName')
        _put(path, rec['type'], rec['fields'], drop=drop, repoint=repoint)
        created += 1

    # 2) 20-tier pet ladder = pet_base (full) overlaid with per-tier deltas.
    base = snap['pet_base']
    varying = set(snap['pet_varying_fields'])
    pet_drop = ('deathEffect', 'genericSound1')       # SVAERA-only .pfx FX + summon soundpak
    pet_repoint = {'deathSound1': [_RG_STONE_SOUND]}   # -> base stone thud (dust crumble stays)
    for idx, pet_path in enumerate(snap['pet_paths']):
        _ensure_record(db, pet_path, base['type'])
        for name, dt, vals in base['fields']:
            if name in varying or name in pet_drop:
                continue
            v = list(pet_repoint[name]) if name in pet_repoint else list(vals)
            db.set_field(pet_path, name, v, dt)
        for name, dv in snap['pet_deltas'][idx].items():
            if dv is None or name in pet_drop:          # None = field absent in this tier
                continue
            dt, vals = dv
            v = list(pet_repoint[name]) if name in pet_repoint else list(vals)
            db.set_field(pet_path, name, v, dt)
        db._modified.add(pet_path)
        created += 1

    # 3) appended UI tree slot (clone-shape of base skill21/MenhirWall; grid 628,217 =
    #    one row above Menhir Wall). Base ships skill01..22 contiguous -> skill23 is the
    #    next enumerated slot; UI records store an EMPTY record-type header.
    _ensure_record(db, _RG_UI, '')
    for name, dt, vals in (
        ('templateName', S, [r'database\Templates\InGameUI\SkillButton.tpl']),
        ('FileDescription', S, ['Rune Golem']),
        ('bitmapNameDown', S, [r'InGameUI\SkillButtonBorderDown01.tex']),
        ('bitmapNameInFocus', S, [r'InGameUI\SkillButtonBorderOver01.tex']),
        ('bitmapNameUp', S, [r'InGameUI\SkillButtonBorder01.tex']),
        ('bitmapPositionX', I, [628]),
        ('bitmapPositionY', I, [217]),
        ('isCircular', I, [0]),
        ('skillName', S, [_RG_SUMMON]),
        ('skillOffsetX', I, [4]),
        ('skillOffsetY', I, [4]),
        ('soundNameDown', S, [r'Records\Sounds\SoundPak\UI\AddSkillPointPak.dbr']),
    ):
        db.set_field(_RG_UI, name, vals, dt)
    db._modified.add(_RG_UI)
    created += 1

    # 4) Text tags (6 new golem strings; the menhir-bolt clause is trimmed since our
    #    vanilla Menhir Wall lacks SVAERA's catalyst-bolt synergy).
    tags['x2tagNewSkillRunes001'] = 'Runic Golem'
    tags['x2tagNewSkillRunesDescription001'] = (
        'Call for a Runic Golem with a special affinity for energy. Two Golems can be '
        'summoned at higher levels.{^n}{^y}Catalyst: the Golem improves the Energy of '
        'nearby allies.')
    tags['x2tagNewPetRunes001'] = 'Runic Golem'
    tags['x2tagNewSkillRunesPet001'] = 'Catalyst Aura'
    tags['x2tagNewSkillRunesPetDescription001'] = (
        'Grants energy and reduces energy reservations from aura skills.')
    tags['x2tagNewSkillRunesPet002'] = 'Cleave'

    print(f"  Rune Golem: {created} records (summon + 20-tier pet ladder + 7 pet-skills "
          f"+ 6 passives + AI controller + UI slot23); render closure in "
          f"assets/runegolem/_DRX_Meshes.arc + _DRX_Textures.arc; menhir prereq -> "
          f"vanilla, cosmetic FX/sounds -> base; 6 tags")


def _create_obsidian_roulette(db, tags):
    """Build the whole N6 obsidian roulette DB side in dependency order:
    guardians (with kits + ondeath) -> Voranthys summon pet+skill -> warband pool
    + limit -> hoard loot tables -> chests -> accessory pools -> 4 corner proxies
    -> 4 souls -> tags. All refs existence-verified. Monster.tpl clones are free
    to add resist fields (blood_toxeus/Vashkarr precedent); dtype-free set_field
    on cloned records preserves each field's type."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    for donor in (_OBS_SARKOTH_DONOR, _OBS_GORRAHK_DONOR, _OBS_VORANTHYS_DONOR,
                  _OBS_ILSEVAR_DONOR, _OBS_VORANTHYS_PET_SRC, _OBS_POOL_DONOR,
                  _OBS_PROXY_DONOR):
        if not db.has_record(donor):
            print(f"  OBSIDIAN: WARNING donor missing: {donor}; group skipped")
            return

    def _clear_extra_skills(rec, keep_upto):
        """Delete skillName slots ABOVE keep_upto that the donor carried (avoid
        stray donor skills; DELETE not blank, per the B-TOXEUS-2 zero-precedent
        empty-ref law)."""
        ff = db.get_fields(rec)
        if not ff:
            return
        for key in [k for k in list(ff) if k.split('###')[0].startswith('skillName')]:
            base = key.split('###')[0]
            try:
                n = int(base[len('skillName'):])
            except ValueError:
                continue
            if n > keep_upto:
                del ff[key]
        db._modified.add(rec)

    def _clear_special_attacks(rec, keep_upto):
        """Delete specialAttack{N}SkillName + its paired chance/delay/etc. slots
        ABOVE keep_upto (so leftover donor special attacks don't fire)."""
        ff = db.get_fields(rec)
        if not ff:
            return
        import re as _re
        for key in list(ff):
            base = key.split('###')[0]
            m = _re.match(r'specialAttack(\d*)([A-Za-z].*)', base)
            if not m:
                continue
            num = m.group(1)
            idx = 1 if num == '' else int(num)
            if idx > keep_upto:
                del ff[key]
        db._modified.add(rec)

    def _set_kit(rec, skills, specials):
        """skills = ordered list -> skillName1..N; specials = list of
        (skill, chance) -> specialAttackSkillName / specialAttack2.. rotation."""
        for i, sk in enumerate(skills, start=1):
            sf(rec, f'skillName{i}', sk)
        _clear_extra_skills(rec, len(skills))
        _clear_special_attacks(rec, len(specials))
        for i, (sk, ch) in enumerate(specials, start=1):
            suffix = '' if i == 1 else str(i)
            sf(rec, f'specialAttack{suffix}SkillName', sk)
            sf(rec, f'specialAttack{suffix}Chance', float(ch))

    # ── 1. SARKOTH, the Glasswright (flame-liche caster; obsidian drop + meteor). ──
    db.clone_record(_OBS_SARKOTH_DONOR, _OBS_SARKOTH)
    M = _OBS_SARKOTH
    sf(M, 'description', 'tagSVCMonsterSarkoth')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'charLevel', list(_OBS_BAND))
    sf(M, 'characterLife', [4500.0, 7000.0, 10500.0])
    sf(M, 'characterLifeRegen', 10.0)
    sf(M, 'scale', 1.35)
    sf(M, 'defensiveFire', 80.0); sf(M, 'defensivePierce', 45.0)
    sf(M, 'defensiveLife', 60.0)
    _set_kit(M, [
        _OBS_SK_DROPTELE, _OBS_SK_ARENAMETEOR, _OBS_SK_VOLCORB, _OBS_SK_VOLCFRAG,
        _OBS_SK_VOLCIMMO, _OBS_SK_RINGFLAME, _OBS_SK_ICESHARD, _OBS_SK_SQUALL,
        _OBS_SK_SPELLBREAKER, _OBS_SK_ONDEATH_FROSTNOVA, _OBS_SK_ARMORPASSIVE,
        _OBS_SK_BOSSIMMUNITY, _OBS_SK_BOSSSCALING,
        _OBS_SK_GP_N, _OBS_SK_GP_E, _OBS_SK_GP_L,
    ], [(_OBS_SK_DROPTELE, 55.0), (_OBS_SK_ARENAMETEOR, 40.0),
        (_OBS_SK_VOLCORB, 50.0), (_OBS_SK_SQUALL, 35.0)])
    db._modified.add(M)

    # ── 2. GORRAHK, the Tombsplitter (golden-skeleton bruiser; 16-knife death). ──
    db.clone_record(_OBS_GORRAHK_DONOR, _OBS_GORRAHK)
    M = _OBS_GORRAHK
    sf(M, 'description', 'tagSVCMonsterGorrahk')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'charLevel', list(_OBS_BAND))
    sf(M, 'characterLife', [6500.0, 10000.0, 15000.0])
    sf(M, 'characterLifeRegen', 12.0)
    sf(M, 'characterStrength', 460.0)
    sf(M, 'handHitDamageMin', 95.0); sf(M, 'handHitDamageMax', 155.0)
    sf(M, 'scale', 1.5)
    sf(M, 'defensivePhysical', 35.0); sf(M, 'defensiveLife', 70.0)
    _set_kit(M, [
        _OBS_SK_BLADESTORM, _OBS_SK_GROUNDSMASH, _OBS_SK_TERRIFYROAR,
        _OBS_SK_DMGMOD, _OBS_SK_SPEEDALL, _OBS_SK_ONDEATH_BLADENOVA,
        _OBS_SK_ARMORPASSIVE, _OBS_SK_BOSSIMMUNITY, _OBS_SK_BOSSSCALING,
        _OBS_SK_GP_N, _OBS_SK_GP_E, _OBS_SK_GP_L,
    ], [(_OBS_SK_BLADESTORM, 55.0), (_OBS_SK_GROUNDSMASH, 45.0),
        (_OBS_SK_TERRIFYROAR, 35.0)])
    db._modified.add(M)

    # ── 3. VORANTHYS, the Sepulchral (dragon-lich summon-storm; ondeath raise). ──
    db.clone_record(_OBS_VORANTHYS_DONOR, _OBS_VORANTHYS)
    M = _OBS_VORANTHYS
    sf(M, 'description', 'tagSVCMonsterVoranthys')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'charLevel', list(_OBS_BAND))
    sf(M, 'characterLife', [5000.0, 8000.0, 12000.0])
    sf(M, 'characterLifeRegen', 12.0)
    sf(M, 'scale', 1.3)
    sf(M, 'defensiveCold', 60.0); sf(M, 'defensiveLife', 80.0)
    _set_kit(M, [
        _OBS_SK_FIREBREATH, _OBS_SK_FREEZEBREATH, _OBS_SK_DECOMP,
        _OBS_SK_BUFFETWINGS, _OBS_SK_SUMMONWARRIOR, _OBS_SK_SUMMONARCHER,
        _OBS_SK_SUMMONTOMB, _OBS_SK_ONDEATH_SPAWNSKEL, _OBS_SK_ONDEATH_NECRONOVA,
        _OBS_SK_ARMORPASSIVE, _OBS_SK_BOSSIMMUNITY, _OBS_SK_BOSSSCALING,
        _OBS_SK_GP_N, _OBS_SK_GP_E, _OBS_SK_GP_L,
    ], [(_OBS_SK_SUMMONWARRIOR, 60.0), (_OBS_SK_SUMMONARCHER, 55.0),
        (_OBS_SK_SUMMONTOMB, 45.0), (_OBS_SK_FREEZEBREATH, 40.0)])
    db._modified.add(M)

    # ── 4. ILSEVAR, the Ashen Watch (blink-flicker poltergeist duelist). ──
    db.clone_record(_OBS_ILSEVAR_DONOR, _OBS_ILSEVAR)
    M = _OBS_ILSEVAR
    sf(M, 'description', 'tagSVCMonsterIlsevar')
    sf(M, 'monsterClassification', 'Boss')
    sf(M, 'charLevel', list(_OBS_BAND_ILS))
    sf(M, 'characterLife', [5500.0, 8500.0, 13000.0])
    sf(M, 'characterLifeRegen', 12.0)
    sf(M, 'characterStrength', 360.0); sf(M, 'characterDexterity', 340.0)
    sf(M, 'handHitDamageMin', 80.0); sf(M, 'handHitDamageMax', 130.0)
    sf(M, 'scale', 1.45)
    sf(M, 'defensiveLife', 70.0); sf(M, 'defensivePierce', 40.0)
    _set_kit(M, [
        _OBS_SK_PHANTOMSTRIKE, _OBS_SK_KIKASTRIKE, _OBS_SK_DISTORTWAVE,
        _OBS_SK_LIFEDRAIN, _OBS_SK_DEATHCHILLAURA, _OBS_SK_HALIROAR,
        _OBS_SK_ONDEATH_DETONATE, _OBS_SK_ARMORPASSIVE, _OBS_SK_BOSSIMMUNITY,
        _OBS_SK_BOSSSCALING, _OBS_SK_GP_N, _OBS_SK_GP_E, _OBS_SK_GP_L,
    ], [(_OBS_SK_PHANTOMSTRIKE, 55.0), (_OBS_SK_KIKASTRIKE, 45.0),
        (_OBS_SK_DISTORTWAVE, 40.0), (_OBS_SK_HALIROAR, 35.0)])
    db._modified.add(M)

    # ── 5. Voranthys summon pet + skill (SepulchralWyrm01 rig, D19-hardened). ──
    vor_pets = [rf'records\skills\soulskills\pets\voranthys_{i}.dbr' for i in (1, 2, 3)]
    _build_boss_summon(
        db, _OBS_VORANTHYS_PET_SRC, vor_pets, SUMMON_VORANTHYS_SKILL,
        'tagSVCSummonVoranthys', 'tagSVCMonsterVoranthys',
        char_level=[42, 60, 72], life=[5000.0, 8000.0, 12000.0],
        life_regen=[30.0, 60.0, 100.0],
        dmg_min=[70.0, 110.0, 160.0], dmg_max=[115.0, 175.0, 250.0], scale=1.2)

    # ── 6. Shared warband pool + no-cap limit. ──
    db.clone_record(_OBS_LIMIT_DONOR, _OBS_LIMIT)
    for f in ('maxPlayerLevelEquationNormal', 'maxPlayerLevelEquationEpic',
              'maxPlayerLevelEquationLegendary'):
        sf(_OBS_LIMIT, f, '110*1')
    db._modified.add(_OBS_LIMIT)

    db.clone_record(_OBS_POOL_DONOR, _OBS_WARBAND_POOL)
    PL = _OBS_WARBAND_POOL
    sf(PL, 'FileDescription', 'Obsidian roulette warband: 1 random guardian + 5 elites')
    guardians = [_OBS_SARKOTH, _OBS_GORRAHK, _OBS_VORANTHYS, _OBS_ILSEVAR]
    for i in range(1, 7):    # clear donor name1..3 residue, then set 1..4
        ff = db.get_fields(PL) or {}
        for key in [k for k in ff if k.split('###')[0] in (f'name{i}', f'weight{i}')]:
            del ff[key]
    for i, g in enumerate(guardians, start=1):
        sf(PL, f'name{i}', g)
        sf(PL, f'weight{i}', 25)
    for i, w in enumerate(_OBS_WARBAND, start=1):
        sf(PL, f'nameChampion{i}', w)
        sf(PL, f'weightChampion{i}', 100)
    sf(PL, 'spawnMin', 6)
    sf(PL, 'spawnMax', 6)
    sf(PL, 'championChance', 100.0)
    sf(PL, 'championMin', 5)
    sf(PL, 'championMax', 5)
    db._modified.add(PL)

    # ── 7. Hoard chest chain (loot tables -> chests -> accessory pools). ──
    for t in ('01', '02', '03'):
        # loot table: clone the mega-chest table (valid slot shapes), reduce
        # numSpawn below-mega, add a guaranteed high-value loot3 slot.
        lt = _OBS_HOARD_LOOT[t]
        db.clone_record(_OBS_HOARD_LOOT_DONOR[t], lt)
        sf(lt, 'numSpawnMinEquation', '(3+(1.8*numberOfPlayers))*2.4')
        sf(lt, 'numSpawnMaxEquation', '(3+(1.8*numberOfPlayers))*2.8')
        sf(lt, 'loot3Chance', 100.0)
        sf(lt, 'loot3Name1', _OBS_GUAR_UNIQUE); sf(lt, 'loot3Weight1', 100)
        sf(lt, 'loot3Name2', _OBS_GUAR_RELIC); sf(lt, 'loot3Weight2', 60)
        db._modified.add(lt)

        # chest: clone the blood-cave mega chest, retheme to a Boss-locked hoard.
        ch = _OBS_CHEST[t]
        db.clone_record(_OBS_CHEST_DONOR[t], ch)
        sf(ch, 'description', 'tagSVCObsidianHoard')
        sf(ch, 'LockedClassification', 'Boss')
        sf(ch, 'LockedRadius', 50.0)
        sf(ch, 'locked', 1)
        sf(ch, 'goldGeneratorChance', 100.0)
        sf(ch, 'tables', lt)
        db._modified.add(ch)

        # accessory pool: clone the mega-chest accessory pool, point at our chest.
        ap = _OBS_ACC_POOL[t]
        db.clone_record(_OBS_ACC_POOL_DONOR[t], ap)
        sf(ap, 'fixedItemName1', ch)
        sf(ap, 'fixedItemChance', 100)
        sf(ap, 'fixedItemWeight1', 100)
        db._modified.add(ap)

    # ── 8. Four corner proxies (roulette dial + monster pool + accessory chest). ──
    for c, px in _OBS_CORNERS.items():
        db.clone_record(_OBS_PROXY_DONOR, px)
        sf(px, 'chanceToRun', 25.0)
        sf(px, 'pool1', _OBS_WARBAND_POOL)
        sf(px, 'accessory1', _OBS_ACC_POOL['01'], S)
        sf(px, 'accessoryEpic1', _OBS_ACC_POOL['02'], S)
        sf(px, 'accessoryLegendary1', _OBS_ACC_POOL['03'], S)
        sf(px, 'difficultyEquationFile', _OBS_DIFFICULTY)
        sf(px, 'difficultyLimitsFile', _OBS_LIMIT)
        sf(px, 'placementExtents', 4.0)
        db._modified.add(px)

    # ── 9. Four amgoz1-voice souls (flat iconic names, signature-move grants). ──
    def _soul_stats(base, extra):
        return {**_bmp(base), **extra}

    # SARKOTH: manual pcsafe typhon_meteorstorm 2/3/4 + drxvolcanicorb/stoneskin.
    sarkoth_tiers = []
    for t, il, sklvl in (('n', 40, 2), ('e', 58, 3), ('l', 72, 4)):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]; r = lambda v: round(v * m, 1)
        sarkoth_tiers.append({'diff': t, 'itemLevel': il, 'stats': _soul_stats(t, {
            'itemSkillName': (S, _OBS_SS_TYPHON_METEOR), 'itemSkillLevel': (I, sklvl),
            'augmentSkillName1': (S, _OBS_AUG_VOLCORB), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _OBS_AUG_STONESKIN), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(240.0)),
            'offensiveFireMin': (F, r(60.0)), 'offensiveFireMax': (F, r(100.0)), 'offensiveFireModifier': (I, int(r(40))),
            'offensiveColdMin': (F, r(30.0)), 'offensiveColdMax': (F, r(55.0)),
            'retaliationSlowRunSpeedMin': (F, r(40.0)), 'retaliationSlowRunSpeedDurationMin': (F, 2.0),
            'defensiveFire': (F, r(30.0)), 'characterOffensiveAbility': (F, r(80.0)),
        })})
    _create_soul(db, 'sarkoth', 'tagSVCSoulSarkoth', sarkoth_tiers, monster=_OBS_SARKOTH, drop_rate=66.0)

    # GORRAHK: manual pcsafe cyclops_groundsmash 3/4/5 + drxconcussive/onslaught.
    gorrahk_tiers = []
    for t, il, sklvl in (('n', 40, 3), ('e', 58, 4), ('l', 72, 5)):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]; r = lambda v: round(v * m, 1)
        gorrahk_tiers.append({'diff': t, 'itemLevel': il, 'stats': _soul_stats(t, {
            'itemSkillName': (S, _OBS_SS_GROUNDSMASH_PC), 'itemSkillLevel': (I, sklvl),
            'augmentSkillName1': (S, _OBS_AUG_CONCUSSIVE), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _OBS_AUG_ONSLAUGHT), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(300.0)), 'characterStrength': (F, r(35.0)),
            'offensivePhysicalMin': (F, r(70.0)), 'offensivePhysicalMax': (F, r(110.0)), 'offensivePhysicalModifier': (I, int(r(45))),
            'offensiveStunMin': (F, 0.5), 'offensiveStunModifier': (I, int(r(30))),
            'retaliationPhysicalMin': (F, r(80.0)), 'retaliationPhysicalMax': (F, r(140.0)),
            'characterDeflectProjectile': (F, r(12.0)),
            'defensivePhysical': (F, r(120.0)), 'characterDefensiveAbility': (F, r(70.0)),
        })})
    _create_soul(db, 'gorrahk', 'tagSVCSoulGorrahk', gorrahk_tiers, monster=_OBS_GORRAHK, drop_rate=66.0)

    # VORANTHYS: THE SUMMON (manual summon_voranthys) + drxcoldaura/deathchill.
    voranthys_tiers = []
    for t, il in (('n', 40), ('e', 58), ('l', 72)):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]; r = lambda v: round(v * m, 1)
        voranthys_tiers.append({'diff': t, 'itemLevel': il, 'stats': _soul_stats(t, {
            'itemSkillName': (S, SUMMON_VORANTHYS_SKILL), 'itemSkillLevel': (I, {'n': 1, 'e': 2, 'l': 3}[t]),
            'augmentSkillName1': (S, _OBS_AUG_COLDAURA), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _OBS_AUG_DEATHCHILL), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(260.0)), 'characterMana': (F, r(180.0)),
            'offensiveColdMin': (F, r(45.0)), 'offensiveColdMax': (F, r(75.0)), 'offensiveColdModifier': (I, int(r(35))),
            'offensiveLifeMin': (F, r(30.0)), 'offensiveLifeMax': (F, r(50.0)),
            'defensiveFreeze': (F, 100.0),           # weird signature stat (Dragon Liche weirdness)
            'defensiveCold': (F, r(30.0)), 'skillCooldownReduction': (F, r(10.0)),
        })})
    voranthys_souls = _create_soul(db, 'voranthys', 'tagSVCSoulVoranthys', voranthys_tiers,
                                   monster=_OBS_VORANTHYS, drop_rate=66.0)
    _wire_summon_soul(db, voranthys_souls, SUMMON_VORANTHYS_SKILL)   # strip controller, level 1/2/3

    # ILSEVAR: lifedrain ON-ATTACK proc + drxphantomstrike/drxdistortionwave.
    ilsevar_tiers = []
    for t, il, sklvl in (('n', 42, 2), ('e', 60, 3), ('l', 74, 4)):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]; r = lambda v: round(v * m, 1)
        ilsevar_tiers.append({'diff': t, 'itemLevel': il, 'stats': _soul_stats(t, {
            'itemSkillName': (S, _OBS_SK_LIFEDRAIN), 'itemSkillLevel': (I, sklvl),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _OBS_AUG_PHANTOMSTRIKE), 'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _OBS_AUG_DISTORTWAVE), 'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'characterLife': (F, r(240.0)), 'characterDexterity': (F, r(30.0)),
            'offensiveLifeLeechMin': (F, r(30.0)),
            'offensivePierceRatioMin': (F, r(25.0)),
            'offensiveFearMin': (F, 2.0),            # weird signature stat (ghost fear)
            'defensiveDisruption': (F, r(30.0)),
            'characterDodgePercent': (F, r(12.0)), 'characterDeflectProjectile': (F, r(12.0)),
        })})
    _create_soul(db, 'ilsevar', 'tagSVCSoulIlsevar', ilsevar_tiers, monster=_OBS_ILSEVAR, drop_rate=66.0)

    # ── 10. Tags (amgoz1 voice: flat iconic names). ──
    tags['tagSVCMonsterSarkoth'] = '{^r}Sarkoth, the Glasswright'
    tags['tagSVCMonsterGorrahk'] = '{^r}Gorrahk, the Tombsplitter'
    tags['tagSVCMonsterVoranthys'] = '{^r}Voranthys, the Sepulchral'
    tags['tagSVCMonsterIlsevar'] = '{^r}Ilsevar, the Ashen Watch'
    tags['tagSVCObsidianHoard'] = 'Obsidian Hoard'
    tags['tagSVCSummonVoranthys'] = 'Summon Voranthys, the Sepulchral'
    tags['tagSVCSoulSarkoth'] = '{^F}Sarkoth the Glasswright Soul'
    tags['tagSVCSoulSarkothDESC'] = ('Sarkoth ripped the black glass of the halls '
        'from the dark and rained it down. His soul calls that same sky of falling '
        'obsidian upon the bearer\'s foes.')
    tags['tagSVCSoulGorrahk'] = '{^F}Gorrahk the Tombsplitter Soul'
    tags['tagSVCSoulGorrahkDESC'] = ('Gorrahk split tombs with a single blow and '
        'died in a burst of sixteen knives. His soul grants that earth-breaking '
        'slam and the tireless fury of the tombsplitter.')
    tags['tagSVCSoulVoranthys'] = '{^F}Voranthys the Sepulchral Soul'
    tags['tagSVCSoulVoranthysDESC'] = ('Voranthys raised a rising tide of the dead '
        'and, when cut down, raised more. Its bearer may call the sepulchral wyrm '
        'forth to fight and freeze at their side.')
    tags['tagSVCSoulIlsevar'] = '{^F}Ilsevar the Ashen Watch Soul'
    tags['tagSVCSoulIlsevarDESC'] = ('Ilsevar flickered through the corner-pockets '
        'of the halls, draining the life of all it touched. Its soul drinks the '
        'vitality of the bearer\'s enemies and wraps them in a duelist\'s dread.')

    print("  Obsidian Roulette: 4 guardians (Sarkoth/Gorrahk/Voranthys/Ilsevar) "
          "+ warband pool (6/champ5) + no-cap limit + 4 corner proxies "
          "(chanceToRun=25) + 3 Boss-locked hoard chests + 3 accessory pools + "
          "4 souls (Voranthys summons; Sarkoth/Gorrahk manual; Ilsevar proc); tags set")


# ── GROUP E (build32): N5 Thrown Weapons in the campaign ─────────────────────
# Will APPROVED at all designer recommendations (BACKLOG N5). Two halves:
#   (1) _restore_thrown_weapon_drops(db, base_db): the base game drops thrown
#       weapons (roh = ranged-one-hand) from Act-1..4 monsters via loot6Name5
#       (static_roh_NN @ w400) + loot6Name6 (roh_NN @ band weight) on its
#       defaultloot tables; SV DROPPED these when it overrode the tables. Copy
#       them back VERBATIM (level-matched by the same-named base twin), only into
#       an ACTIVE loot6 slot whose Name5/Name6 are EMPTY (never clobber SV). Runs
#       in main() while base_db is alive; fail-loud restored-count gate.
#   (2) _add_supra_thrown_weapons(db, base_db): 3 Legendary supra thrown weapons
#       (Sanguine Orbit / The Last Word / Charon's Toll) built from the base roh
#       uniques carrying the design meshes (chakramofthesun01 / mjolnir01 /
#       fingerofcharon01) + the u_l_05/09/08 projectiles + DRX supra trail, retuned
#       to the wep_spear supra conventions; 3 ItemArtifactFormula records mirroring
#       wep_spear_formula (1L u_l_08 + 1E u_e_06 + 1MI mi_l_machae reagents,
#       03_act4_offense bonus) wired into supra.dbr lootName25-27 + supra_special
#       26-28 @ w100. (Both run in main(): they need base_db, which is del'd before
#       apply_all_extended_patches.)
_E_DL_MARK = 'containers\\defaultloot\\'
# 3 supra thrown weapons (crafted artifacts).
_E_SUPRA_WPN = {
    'sanguineorbit': r'records\drxitem\supra\svc_wep_sanguineorbit.dbr',
    'lastword':      r'records\drxitem\supra\svc_wep_lastword.dbr',
    'charonstoll':   r'records\drxitem\supra\svc_wep_charonstoll.dbr',
}
# base roh donor per super (carries the design mesh + a complete valid roh weapon).
_E_SUPRA_DONOR = {
    'sanguineorbit': r'records\xpack2\item\equipmentweapons\1hranged\u_l_03.dbr',           # chakramofthesun01
    'lastword':      r'records\xpack2\item\equipmentweapons\1hranged\us_l_donarsmight.dbr',  # mjolnir01
    'charonstoll':   r'records\xpack2\item\equipmentweapons\1hranged\u_n_12.dbr',            # fingerofcharon01
}
_E_SUPRA_PROJ = {
    'sanguineorbit': r'records\xpack2\item\equipmentweapons\1hranged\projectiles\u_l_05.dbr',
    'lastword':      r'records\xpack2\item\equipmentweapons\1hranged\projectiles\u_l_09.dbr',
    'charonstoll':   r'records\xpack2\item\equipmentweapons\1hranged\projectiles\u_l_08.dbr',
}
_E_SUPRA_TAG = {
    'sanguineorbit': 'tagSVCwpnSanguineOrbit',
    'lastword':      'tagSVCwpnLastWord',
    'charonstoll':   'tagSVCwpnCharonsToll',
}
_E_SUPRA_TRAIL = r'records\drxeffects\item\trail_wep_dagger.dbr'         # DRX supra trail (thrown blade)
_E_SUPRA_COSTNAME = r'records\game\itemcost_uniquelegendary_primary.dbr'  # wep_spear supra cost
_E_FORMULA_DONOR = r'records\drxitem\supra\zrecipes\wep_spear_formula.dbr'
_E_FORMULA = {
    'sanguineorbit': r'records\drxitem\supra\zrecipes\svc_thrown_sanguineorbit_formula.dbr',
    'lastword':      r'records\drxitem\supra\zrecipes\svc_thrown_lastword_formula.dbr',
    'charonstoll':   r'records\drxitem\supra\zrecipes\svc_thrown_charonstoll_formula.dbr',
}
_E_FORMULA_TAG = {
    'sanguineorbit': 'tagSVCRecipeSanguineOrbit',
    'lastword':      'tagSVCRecipeLastWord',
    'charonstoll':   'tagSVCRecipeCharonsToll',
}
# reagents: 1 Legendary + 1 Epic + 1 MI thrown weapon (all base roh uniques).
_E_REAGENTS = [
    r'records\xpack2\item\equipmentweapons\1hranged\u_l_08.dbr',       # 1L
    r'records\xpack2\item\equipmentweapons\1hranged\u_e_06.dbr',       # 1E
    r'records\xpack2\item\equipmentweapons\1hranged\mi_l_machae.dbr',  # 1MI
]
_E_SUPRA_TABLE = r'records\xpack\item\loottables\arcaneformulae\supra.dbr'
_E_SUPRA_SPECIAL = r'records\xpack\item\loottables\arcaneformulae\supra_special.dbr'
# per-super Legendary supra stat block + name value.
_E_SUPRA_STATS = {
    'sanguineorbit': {
        'name': 'Sanguine Orbit',
        'stats': {
            'offensivePhysicalMin': 180.0, 'offensivePhysicalMax': 215.0, 'offensivePhysicalModifier': 30.0,
            'offensiveSlowBleedingMin': 350.0, 'offensiveSlowBleedingDurationMin': 3.0,
            'offensiveSlowBleedingChance': 100.0,
            'offensiveLifeLeechMin': 80.0, 'offensiveLifeLeechChance': 100.0,
            'offensivePierceRatioMin': 25.0,
            'characterAttackSpeedModifier': 25.0,
            'characterDexterity': 60.0, 'characterLife': 200.0, 'characterOffensiveAbility': 80.0,
        }},
    'lastword': {
        'name': 'The Last Word',
        'stats': {
            'offensivePhysicalMin': 300.0, 'offensivePhysicalMax': 360.0, 'offensivePhysicalModifier': 25.0,
            'offensiveLightningMin': 5.0, 'offensiveLightningMax': 500.0,
            'offensiveStunMin': 1.0,
            'characterStrength': 80.0, 'characterLife': 250.0, 'characterOffensiveAbility': 90.0,
        }},
    'charonstoll': {
        'name': "Charon's Toll",
        'stats': {
            'offensivePhysicalMin': 180.0, 'offensivePhysicalMax': 210.0, 'offensivePhysicalModifier': 20.0,
            'offensiveLifeMin': 60.0, 'offensiveLifeMax': 90.0, 'offensiveLifeModifier': 20.0,
            'offensiveSlowLifeMin': 60.0, 'offensiveSlowLifeMax': 90.0, 'offensiveSlowLifeDurationMin': 5.0,
            'offensiveManaBurnDrainMin': 20.0,
            'offensiveLifeLeechMin': 60.0, 'offensiveLifeLeechChance': 100.0,
            'characterIntelligence': 60.0, 'characterLife': 200.0, 'characterOffensiveAbility': 80.0,
        }},
}


def _resolve_in(db_, path):
    """Case/slash-tolerant exact resolution against a db's record table."""
    want = str(path).replace('/', '\\').lower()
    for n in db_.record_names():
        if n.replace('/', '\\').lower() == want:
            return n
    return None


def _restore_thrown_weapon_drops(db, base_db):
    """N5 (Group E) part 1: faithful base-game thrown-weapon (roh) drop restore."""
    if base_db is None:
        print("  N5 thrown drops: base_db unavailable; SKIPPED")
        return 0
    S, I = DATA_TYPE_STRING, DATA_TYPE_INT

    def gv(db_, rec, f):
        v = db_.get_field_value(rec, f)
        return (v[0] if isinstance(v, list) else v)

    base_map = {n.replace('/', '\\').lower(): n for n in base_db.record_names()}
    eligible = restored = skipped = 0
    for n in db.record_names():
        nl = n.replace('/', '\\').lower()
        if _E_DL_MARK not in nl:
            continue
        bn = base_map.get(nl)
        if not bn:
            continue
        b5 = str(gv(base_db, bn, 'loot6Name5') or '')
        b6 = str(gv(base_db, bn, 'loot6Name6') or '')
        if 'roh' not in b5.lower() and 'roh' not in b6.lower():
            continue
        eligible += 1
        m5 = str(gv(db, n, 'loot6Name5') or '')
        m6 = str(gv(db, n, 'loot6Name6') or '')
        mch = gv(db, n, 'loot6Chance')
        # only a live loot6 group with empty Name5/6 (never clobber SV; a name in
        # a dormant chance-0 slot would break the container loot-shape gate).
        if m5.strip() or m6.strip() or not mch or float(mch) <= 0:
            skipped += 1
            continue
        if b5.strip():
            db.set_field(n, 'loot6Name5', b5, S)
            db.set_field(n, 'loot6Weight5', int(gv(base_db, bn, 'loot6Weight5') or 0), I)
        if b6.strip():
            db.set_field(n, 'loot6Name6', b6, S)
            db.set_field(n, 'loot6Weight6', int(gv(base_db, bn, 'loot6Weight6') or 0), I)
        db._modified.add(n)
        restored += 1
    print(f"  N5 thrown-weapon drops RESTORED: {restored} defaultloot tables "
          f"(eligible {eligible}, skipped-occupied {skipped})")
    if restored != (eligible - skipped) or restored < 150:
        raise SystemExit(
            f"N5 thrown-drop restore count gate FAILED: restored={restored} != "
            f"eligible-skipped={eligible - skipped} (or < 150). The base roh drop "
            f"pattern changed - reverify before shipping.")
    return restored


def _add_supra_thrown_weapons(db, base_db):
    """N5 (Group E) part 2: 3 supra thrown weapons + 3 formulas + supra wiring.
    Returns the Text tags dict (merged into uber_soul_tags.txt by main())."""
    tags = {}
    if base_db is None:
        print("  N5 supra thrown: base_db unavailable; SKIPPED")
        return tags
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

    # ── the 3 supra weapons (copy the base roh donor's full field set into a mod
    #    supra path so the weapon is structurally complete, then override to
    #    Legendary supra conventions + a fresh thematic stat block). ──
    for key, dest in _E_SUPRA_WPN.items():
        bn = _resolve_in(base_db, _E_SUPRA_DONOR[key])
        if not bn:
            raise SystemExit(f"N5 supra: base donor missing: {_E_SUPRA_DONOR[key]}")
        fields = base_db.get_fields(bn) or {}
        template = ''
        for k, tf in fields.items():
            if k.split('###')[0] == 'templateName' and tf.values:
                template = str(tf.values[0]); break
        _ensure_record(db, dest, template)
        # copy every donor field verbatim (complete valid roh weapon)...
        for k, tf in fields.items():
            fn = k.split('###')[0]
            vals = list(tf.values) if tf.values else []
            if len(vals) == 1:
                db.set_field(dest, fn, vals[0], tf.dtype)
            elif len(vals) > 1:
                db.set_field(dest, fn, vals, tf.dtype)
        # ...then CLEAR the donor's offensive/retaliation/character bonus stats so
        # its native element does not bleed into the retheme.
        ff = db.get_fields(dest)
        for k in [k for k in list(ff) if k.split('###')[0].startswith(
                ('offensive', 'retaliation', 'characterDexterity',
                 'characterStrength', 'characterIntelligence', 'characterLife',
                 'characterOffensiveAbility', 'characterAttackSpeedModifier'))]:
            del ff[k]
        # supra conventions (wep_spear parity): L65 Legendary, DRX trail, supra
        # cost, hide affix names, +1 all skills, 1 relic slot, design projectile.
        db.set_field(dest, 'itemClassification', 'Legendary', S)
        db.set_field(dest, 'itemLevel', 65, I)
        db.set_field(dest, 'levelRequirement', 65, I)
        db.set_field(dest, 'itemCostName', _E_SUPRA_COSTNAME, S)
        db.set_field(dest, 'weaponTrail', _E_SUPRA_TRAIL, S)
        db.set_field(dest, 'basicProjectileName', _E_SUPRA_PROJ[key], S)
        db.set_field(dest, 'itemNameTag', _E_SUPRA_TAG[key], S)
        db.set_field(dest, 'FileDescription', 'SVC N5 supra thrown weapon: '
                     + _E_SUPRA_STATS[key]['name'], S)
        db.set_field(dest, 'augmentAllLevel', 1, I)
        db.set_field(dest, 'numRelicSlots', 1, I)
        db.set_field(dest, 'hidePrefixName', 1, I)
        db.set_field(dest, 'hideSuffixName', 1, I)
        # (keep the donor's native inventory bitmap/mesh/textures - the DRX
        #  recipe bitmap belongs on the FORMULA scroll, not the weapon.)
        for fn, v in _E_SUPRA_STATS[key]['stats'].items():
            db.set_field(dest, fn, float(v), F)
        db._modified.add(dest)
        tags[_E_SUPRA_TAG[key]] = _E_SUPRA_STATS[key]['name']

    # ── the 3 formulas (clone the wep_spear formula = a MOD record; keep its big
    #    affix pools + bonus table, repoint artifactName + reagents + costs). ──
    for key in _E_SUPRA_WPN:
        fdest = _E_FORMULA[key]
        if not db.has_record(_E_FORMULA_DONOR):
            raise SystemExit(f"N5 supra: formula donor missing: {_E_FORMULA_DONOR}")
        db.clone_record(_E_FORMULA_DONOR, fdest)
        db.set_field(fdest, 'artifactName', _E_SUPRA_WPN[key])
        db.set_field(fdest, 'reagent1BaseName', _E_REAGENTS[0])
        db.set_field(fdest, 'reagent2BaseName', _E_REAGENTS[1])
        db.set_field(fdest, 'reagent3BaseName', _E_REAGENTS[2])
        db.set_field(fdest, 'description', _E_FORMULA_TAG[key])
        db.set_field(fdest, 'FileDescription',
                     'SVC N5 supra thrown formula: ' + _E_SUPRA_STATS[key]['name'])
        db.set_field(fdest, 'artifactCreationCost', 10000000)
        db.set_field(fdest, 'itemCost', 500000)
        db._modified.add(fdest)
        tags[_E_FORMULA_TAG[key]] = 'Arcane Formula - ' + _E_SUPRA_STATS[key]['name']

    # ── wire the formulas into the supra tables at the next free lootName slot. ──
    def _next_slot(table):
        i = 1
        while db.get_field_value(table, f'lootName{i}') not in (None, '', 0):
            i += 1
        return i

    for table in (_E_SUPRA_TABLE, _E_SUPRA_SPECIAL):
        if not db.has_record(table):
            raise SystemExit(f"N5 supra: loot table missing: {table}")
        for key in _E_SUPRA_WPN:
            slot = _next_slot(table)
            db.set_field(table, f'lootName{slot}', _E_FORMULA[key], S)
            db.set_field(table, f'lootWeight{slot}', 100, I)
        db._modified.add(table)

    print(f"  N5 supra thrown weapons: 3 supers ({', '.join(v['name'] for v in _E_SUPRA_STATS.values())}) "
          f"+ 3 formulas wired into supra.dbr + supra_special.dbr @ w100")
    return tags


def _wire_blood_toxeus_loot(db):
    """Wire the guaranteed-set-piece + high-bleed tables onto Hemorrheus (§3.3).

    Guaranteed set piece: FixedWeight table on the RightHand weapon slot at
    chance 100 (mirrors how q_leinth_47 guarantees lenithsveil on lootHeadItem1,
    and how the donor already drops a RightHand weapon). High-bleed table: on the
    LeftHand slot at chance 100. Soul stays on Finger2 (wired by _create_soul).
    Per-tier [n,e,l] arrays, matching every loot field's shape.
    """
    if not db.has_record(_BT_MONSTER):
        return
    M = _BT_MONSTER
    guar = [_BT_LOOT_GUAR['n'], _BT_LOOT_GUAR['e'], _BT_LOOT_GUAR['l']]
    bleed = [_BT_LOOT_BLEED['n'], _BT_LOOT_BLEED['e'], _BT_LOOT_BLEED['l']]
    # Guaranteed Crimson Verdict piece -> RightHand slot @100.
    db.set_field(M, 'lootRightHandItem1', guar, DATA_TYPE_STRING)
    db.set_field(M, 'chanceToEquipRightHand', 100.0)
    db.set_field(M, 'chanceToEquipRightHandItem1', 100)
    # High-bleed gear -> LeftHand slot @100.
    db.set_field(M, 'lootLeftHandItem1', bleed, DATA_TYPE_STRING)
    db.set_field(M, 'chanceToEquipLeftHand', 100.0)
    db.set_field(M, 'chanceToEquipLeftHandItem1', 100)
    db._modified.add(M)
    print(f"  Hemorrheus loot wired: guaranteed set piece (RightHand@100) + high-bleed (LeftHand@100)")


def _create_blood_toxeus_fx(db):
    """B-TOXEUS-1: recolor the boss's GREEN shroud to RED.
    B-TOXEUS-2 (build29): rebuilt so the recolor cannot break boss loadability.

    The green aura comes from toxeus_envenomweapon (cast on spawn via
    initialSkillName, a toggle that stays on): charFxPakSelfNames =
    343_weapon_poisoncharfxpak (green hand-mist), green weapon tint, and the green
    poisonweaponenchantment blade glow. The skill is SHARED with the real Athens
    Toxeus (um_toxeus_21, must stay green), so we CLONE a per-boss blood variant
    and repoint ONLY Hemorrheus's kit (_BT_SK_ENVENOM).

    Red replacement = charfxpak_leinth_aura (_BT_BLOOD_CHARFXPAK): the blood-witch
    Leinth persistent boss aura - red, same cult family, and PROVEN LOADABLE in
    this exact field shape (leinth_aura_buff carries the same pak in
    charFxPakSelfNames on a monster that spawns live).

    B-TOXEUS-2 regression lessons (byte-verified build27 vs build28; the boss
    stopped spawning on the SAME proxy/pool/map with only the arz changed):
      - NEVER set weaponEnchantment to '' - ZERO base-game or build27 records
        carry an EMPTY weaponEnchantment (base: 0 of 56); enchantment-less
        Skill_BuffSelfToggled records OMIT the field (31 of 50 in base). The
        field is DELETED from the clone instead.
      - NEVER add charFxPakSelfNames to the lildude summon skill - its donor
        never had it and NO Skill_SpawnPet*/Monster record in base or build27
        carries that field (zero-precedent shape). The summon stays the shared
        donor record, untouched (_BT_LILDUDE_SUMMON == donor).
    The clone-shape invariant (_verify_boss_kit_clone_shape) gates both rules.
    """
    # Blood envenom = the persistent shroud + weapon tint (the ONLY clone).
    if db.has_record(_BT_SK_ENVENOM_DONOR):
        db.clone_record(_BT_SK_ENVENOM_DONOR, _BT_SK_ENVENOM)
        db.set_field(_BT_SK_ENVENOM, 'charFxPakSelfNames', _BT_BLOOD_CHARFXPAK)  # green mist -> red aura
        db.set_field(_BT_SK_ENVENOM, 'skillWeaponTintRed', 1.0)    # was 0.25
        db.set_field(_BT_SK_ENVENOM, 'skillWeaponTintGreen', 0.25)  # was 1.0
        db.set_field(_BT_SK_ENVENOM, 'skillWeaponTintBlue', 0.25)
        # Drop the green poison blade glow by DELETING the field (field-absence
        # parity with the 31 enchantment-less base Skill_BuffSelfToggled records;
        # an empty-string value has zero precedent anywhere - B-TOXEUS-2).
        fields = db.get_fields(_BT_SK_ENVENOM)
        if fields is not None:
            for key in list(fields.keys()):
                if key.split('###')[0] == 'weaponEnchantment':
                    del fields[key]
        db._modified.add(_BT_SK_ENVENOM)
        _BOSS_KIT_CLONES.append((_BT_SK_ENVENOM_DONOR, _BT_SK_ENVENOM))
    else:
        print("  BLOOD TOXEUS FX: WARNING envenom donor missing; shroud NOT recolored")
    print("  Blood Toxeus FX: GREEN poison shroud recolored RED (envenom blood "
          "variant only; lildude summon = shared donor untouched; Athens Toxeus "
          "untouched) [B-TOXEUS-2 safe shape]")


# ── B-TOXEUS-2 invariant: clone-shape loadability guard ────────────────────────
# Registry of (donor, clone) skill/record pairs authored for the Blood Toxeus kit
# (and any future boss kit). The build28 no-spawn regression was caused by a clone
# whose FIELD SHAPE had zero base-game precedent; this guard makes both failure
# modes fail-loud at build time.
_BOSS_KIT_CLONES = []


def _verify_boss_kit_clone_shape(db):
    """FAIL-LOUD invariant (B-TOXEUS-2): every registered boss-kit clone must
    keep its donor's field SHAPE:
      1. the clone must not ADD any field the donor lacks (zero-precedent field
         on the class = potential loader abort -> silent boss no-spawn);
      2. any field holding a non-empty .dbr reference on the donor must not be
         EMPTY on the clone (empty-string ref values have zero precedent; delete
         the field instead);
      3. every .dbr reference the clone changed or kept must resolve in the mod
         db when the donor's value also resolved there.
    Raises SystemExit on any violation."""
    problems = []
    for donor, clone in _BOSS_KIT_CLONES:
        drec = _resolve_record(db, donor)
        crec = _resolve_record(db, clone)
        if drec is None or crec is None:
            problems.append((clone, f"donor or clone missing (donor={drec}, clone={crec})"))
            continue
        dfields = {}
        for key, tf in (db.get_fields(drec) or {}).items():
            dfields[key.split('###')[0]] = [str(v) for v in tf.values]
        for key, tf in (db.get_fields(crec) or {}).items():
            fname = key.split('###')[0]
            cvals = [str(v) for v in tf.values]
            if fname not in dfields:
                problems.append((clone, f"ADDS field '{fname}' absent on donor "
                                        f"{donor} (zero-precedent shape)"))
                continue
            dvals = dfields[fname]
            for i, dv in enumerate(dvals):
                if dv.strip().lower().endswith('.dbr'):
                    cv = cvals[i] if i < len(cvals) else ''
                    if not cv.strip():
                        problems.append((clone, f"field '{fname}' EMPTY where donor "
                                                f"held ref {dv} (delete the field "
                                                f"instead of blanking)"))
                    elif _resolve_record(db, dv) is not None and \
                            _resolve_record(db, cv) is None:
                        problems.append((clone, f"field '{fname}' ref does not "
                                                f"resolve: {cv}"))
    if problems:
        for rec, why in problems:
            print(f"  BOSS-KIT-CLONE OFFENDER: {rec} :: {why}")
        raise SystemExit(
            f"Boss-kit clone-shape invariant FAILED: {len(problems)} problem(s) "
            f"(B-TOXEUS-2 class regression; see offenders above)")
    print(f"  Boss-kit clone-shape invariant OK: {len(_BOSS_KIT_CLONES)} "
          f"clone pair(s) keep donor field shape.")


def _create_blood_toxeus(db):
    """Build the whole Blood Toxeus DB side in dependency order (§6.1):
    monster -> proxy/pool (references monster) -> set + items (loot references
    members) -> loot -> soul (wires to monster) -> wire loot tables to monster.
    """
    print("\n=== Blood Toxeus wave (Hemorrheus, the Red Verdict) ===")
    _create_blood_toxeus_fx(db)   # B-TOXEUS-1: blood shroud skills BEFORE the monster refs them
    _create_blood_toxeus_monster(db)
    _create_blood_toxeus_proxy(db)
    _create_blood_toxeus_proxy_50(db)   # D7: 2nd (50%) proxy for the parchment placement
    _create_blood_toxeus_summon(db)     # D7: pets + summon skill (needs the monster; before the soul)
    _create_crimsonverdict_set(db)
    _create_crimsonverdict_loot(db)
    _create_blood_toxeus_soul(db)       # D7: soul's itemSkill = SUMMON_TOXEUS_SKILL
    _wire_blood_toxeus_loot(db)


# ── MONSTER TEST YARD (TESTHUB-only; build31/32 hostiles) ────────────────────
# Will's dedicated fight-and-tune yard at the HiddenValley01 blood-cave mouth.
# The arz gets these pool/proxy records UNCONDITIONALLY, but they stay INERT
# because ONLY the TESTHUB map (build_section_surgery.build_hub_extra_specs, the
# separate map lane) places their proxies; the canonical/Steam map references
# none of them (that is why the flag design can never ship test content). Every
# yard pool references the REAL shipped monster records (never a clone), so
# stat-tuning those records in the arz tunes the yard fight 1:1. Donor for every
# pool/proxy = q_leinth_lone (the 1-placement/1-level "lone" dedicated pattern,
# the Vashkarr/bloodtoxeus precedent). All refs existence-verified vs the shipped
# arz e27dd1cb (scratchpad/yard_recon.py). NOTE: q_yard_* basenames start with
# 'q_' AND live under records\drxmap\proxy (NOT proxies orient/egypt/greek/hades)
# -> the roaming-sweep eligibility filter skips them on BOTH counts, so the sweep
# never touches them; the ONE yard pool that carries the Enslaver is whitelisted
# in _verify_roaming_sweep via _EN_YARD_POOLS below.
_YARD_POOL_DONOR = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_YARD_PROXY_DONOR = r'records\drxmap\proxy\q_leinth_lone.dbr'
_YARD_LIMIT = r'records\proxies orient\limit_obsidianbosses.dbr'   # [1..110] contains L100 Enslaver + L74 Ilsevar
_YARD_DIFFICULTY = r'records\proxies orient\difficulty_04.dbr'
# Enslaver cluster (SPOT A1 boss + A2 marauder pack).
_YARD_ENSLAVER_POOL = r'records\drxmap\proxy\pools\q_yard_enslaver.dbr'
_YARD_ENSLAVER_PROXY = r'records\drxmap\proxy\q_yard_enslaver.dbr'
_YARD_MARAUDERS_POOL = r'records\drxmap\proxy\pools\q_yard_marauders.dbr'
_YARD_MARAUDERS_PROXY = r'records\drxmap\proxy\q_yard_marauders.dbr'
# Obsidian guardians (SPOT C + adjacent pockets): one dedicated 100% pool each.
_YARD_OBS_GUARDIANS = {
    'sarkoth':   _OBS_SARKOTH,
    'gorrahk':   _OBS_GORRAHK,
    'voranthys': _OBS_VORANTHYS,
    'ilsevar':   _OBS_ILSEVAR,
}
_YARD_OBS_POOL = {c: rf'records\drxmap\proxy\pools\q_yard_obs_{c}.dbr' for c in _YARD_OBS_GUARDIANS}
_YARD_OBS_PROXY = {c: rf'records\drxmap\proxy\q_yard_obs_{c}.dbr' for c in _YARD_OBS_GUARDIANS}
# Wyrm horde (SPOT D): reuse the shipped tier-03 pool; one dedicated proxy.
_YARD_WYRM_POOL = r'records\proxies orient\pools\demon\svc_wyrmhorde_03.dbr'   # REUSE (no new pool)
_YARD_WYRM_PROXY = r'records\drxmap\proxy\q_yard_wyrm.dbr'
# Obsidian hoard accessory chest chain (existing GROUP F records) reused so the
# yard obs fights also drop the Boss-locked hoard (no new container records).
_YARD_OBS_ACC = {t: rf'records\drxitem\container\svc_obsidianhoard_pool_{t}.dbr'
                 for t in ('01', '02', '03')}
# The ONE yard pool that legitimately carries the Enslaver at weight > 1
# (whitelisted out of the roaming-sweep derivation). EXACT record-path set (never
# a loose substring), per the roaming-sweep leak-detection contract.
_EN_YARD_POOLS = {_YARD_ENSLAVER_POOL}


def _create_test_yard(db, tags):
    """GROUP 1 (yard): build the dedicated TESTHUB monster-yard pool/proxy records.
    Pools reference the REAL shipped monster records (never clones), so tuning
    those records tunes the yard fight. Records are added unconditionally (inert
    on the canonical map). Must run AFTER the enslaver/obsidian/wyrm/vashkarr
    groups (their monster records must exist) and BEFORE _sweep_inject_roaming_rare
    + _verify_roaming_sweep (so the sweep gate sees + whitelists the yard enslaver
    pool). No souls/monsters/containers created here - only proxies + pools."""
    S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT
    sf = db.set_field

    for donor in (_YARD_POOL_DONOR, _YARD_PROXY_DONOR):
        if not db.has_record(donor):
            print(f"  TEST YARD: WARNING donor missing: {donor}; group skipped")
            return

    def _gv(rec, f):
        v = db.get_field_value(rec, f)
        return (v[0] if isinstance(v, list) else v)

    def _clear_champions(pool):
        """Blank the q_leinth_lone donor's 3 blood-demon champion slots
        (nameChampion1..3 + weightChampion1..3) to the inert empty-string/0 shape
        (the proven vashkarr-pool nameChampion3='' shape). Only the donor's real
        slots are touched - no empty high slots are added. Callers that WANT
        champions (the obsidian pools) overwrite these afterwards."""
        for i in (1, 2, 3):
            sf(pool, f'nameChampion{i}', '')
            sf(pool, f'weightChampion{i}', 0)

    def _make_proxy(proxy, pool_ref, primary_monster, extents,
                    accessory=None, mesh_from=None):
        """Clone the q_leinth_lone proxy -> a yard proxy pointing at pool_ref.
        chanceToRun=100 (donor has none), no-cap [1..110] limit, difficulty_04.
        Preview mesh/scale mirror the primary spawned monster (falls back to the
        donor's leinth silhouette if the monster defines none)."""
        db.clone_record(_YARD_PROXY_DONOR, proxy)
        sf(proxy, 'pool1', pool_ref)
        sf(proxy, 'chanceToRun', 100.0)
        sf(proxy, 'difficultyLimitsFile', _YARD_LIMIT)
        sf(proxy, 'difficultyEquationFile', _YARD_DIFFICULTY)
        sf(proxy, 'placementExtents', float(extents))
        if mesh_from and db.has_record(mesh_from):
            m = _gv(mesh_from, 'mesh')
            sc = _gv(mesh_from, 'scale')
            if m and str(m).strip():
                sf(proxy, 'mesh', str(m))
            if sc is not None:
                sf(proxy, 'scale', float(sc))
        if accessory:
            sf(proxy, 'accessory1', accessory['01'], S)
            sf(proxy, 'accessoryEpic1', accessory['02'], S)
            sf(proxy, 'accessoryLegendary1', accessory['03'], S)
        db._modified.add(proxy)

    # ── 1. ENSLAVER boss (SPOT A1): pool name1..3 = the real Enslaver, spawn 1,
    #    championChance 0 -> the boss alone @100%. He auto-summons his own hostile
    #    marauder burst (svc_enslaver_summonmarauders, petLimit 8) in-fight. ──
    db.clone_record(_YARD_POOL_DONOR, _YARD_ENSLAVER_POOL)
    PL = _YARD_ENSLAVER_POOL
    sf(PL, 'FileDescription', 'YARD: Toxeus the Enslaver boss @100% (TESTHUB-only)')
    for i in (1, 2, 3):
        sf(PL, f'name{i}', _EN_BOSS)
        sf(PL, f'weight{i}', 100)
    _clear_champions(PL)                   # no champions; blank the leinth donor residue
    sf(PL, 'spawnMin', 1); sf(PL, 'spawnMax', 1)
    sf(PL, 'championChance', 0.0); sf(PL, 'championMin', 0); sf(PL, 'championMax', 0)
    db._modified.add(PL)
    _make_proxy(_YARD_ENSLAVER_PROXY, _YARD_ENSLAVER_POOL, _EN_BOSS, 3.0,
                mesh_from=_EN_BOSS)

    # ── 2. MARAUDER pack (SPOT A2): pool name1..4 = the real Champion marauder,
    #    championChance 0 -> a guaranteed marauder pack @100%. build36 A2: spawn
    #    10 (Will's "guaranteed 10-pack" - a real AoE-or-die swarm in the yard). ──
    db.clone_record(_YARD_POOL_DONOR, _YARD_MARAUDERS_POOL)
    PL = _YARD_MARAUDERS_POOL
    sf(PL, 'FileDescription', 'YARD: Enslaved Shadow Marauder pack 10 @100% (TESTHUB-only)')
    for i in (1, 2, 3, 4):
        sf(PL, f'name{i}', _EN_MARAUDER)
        sf(PL, f'weight{i}', 100)
    _clear_champions(PL)
    sf(PL, 'spawnMin', 10); sf(PL, 'spawnMax', 10)
    sf(PL, 'championChance', 0.0); sf(PL, 'championMin', 0); sf(PL, 'championMax', 0)
    db._modified.add(PL)
    _make_proxy(_YARD_MARAUDERS_PROXY, _YARD_MARAUDERS_POOL, _EN_MARAUDER, 3.0,
                mesh_from=_EN_MARAUDER)

    # ── 3. OBSIDIAN guardians (SPOT C + pockets): FOUR dedicated pools, EACH
    #    guaranteeing its ONE named guardian at 100% + the 5-elite warband (the
    #    shipped q_obs_warband gives only 1 RANDOM guardian, so it cannot pin each
    #    one). name1..3 = that guardian (all identical -> the guaranteed main is
    #    always him); championMin=Max=5 + nameChampion1..6 = the real warband set. ──
    for c, guardian in _YARD_OBS_GUARDIANS.items():
        pool = _YARD_OBS_POOL[c]
        db.clone_record(_YARD_POOL_DONOR, pool)
        sf(pool, 'FileDescription', f'YARD: obsidian guardian {c} @100% + 5-elite warband (TESTHUB-only)')
        for i in (1, 2, 3):
            sf(pool, f'name{i}', guardian)
            sf(pool, f'weight{i}', 100)
        # the 6 warband members OVERWRITE the donor's 3 champion slots + add 3 more
        for i, w in enumerate(_OBS_WARBAND, start=1):
            sf(pool, f'nameChampion{i}', w)
            sf(pool, f'weightChampion{i}', 100)
        sf(pool, 'spawnMin', 6); sf(pool, 'spawnMax', 6)
        sf(pool, 'championChance', 100.0)
        sf(pool, 'championMin', 5); sf(pool, 'championMax', 5)   # 6-5=1 guaranteed guardian
        db._modified.add(pool)
        _make_proxy(_YARD_OBS_PROXY[c], pool, guardian, 3.0,
                    accessory=_YARD_OBS_ACC, mesh_from=guardian)

    # ── 4. WYRM horde (SPOT D): reuse the shipped tier-03 pool verbatim (no new
    #    pool), one dedicated proxy. placementExtents 2.5 (SPOT D is the tightest
    #    pocket; the map lane re-verifies + nudges the coord to >=~95% at 2.5u). ──
    _make_proxy(_YARD_WYRM_PROXY, _YARD_WYRM_POOL,
                r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_common_31.dbr',
                2.5, mesh_from=r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_common_31.dbr')

    print("  TEST YARD: enslaver + marauder + 4 obsidian-guardian pools + 4 corner "
          "proxies (hoard chests) + wyrm proxy (reuse svc_wyrmhorde_03); 6 new pools "
          "+ 7 new proxies (13 records), all referencing REAL records (inert without "
          "the TESTHUB map)")


# ── Spawn-eligibility gate for mod-authored spawn proxies (fail-loud) ──────────
# Registry of every proxy this build AUTHORS/edits, with the "main" (boss/hero) monster
# that MUST reliably spawn. Add future mod-authored spawn proxies here so the invariant
# below guards them too. (Base-game proxies are NOT listed - we only gate our own.)
_MOD_AUTHORED_SPAWN_PROXIES = [
    {
        'proxy': _BT_PROXY,
        'pool': _BT_POOL,
        'main_monster': _BT_MONSTER,   # the boss that must not be crowded out
        'name': 'q_bloodtoxeus_lone (Hemorrheus, chest @100%)',
    },
    {
        # D7: the 2nd (parchment) proxy shares the SAME pool/boss, so the same
        # spawn-eligibility math must hold. chanceToRun only gates WHETHER it fires.
        'proxy': _BT_PROXY_50,
        'pool': _BT_POOL,
        'main_monster': _BT_MONSTER,
        'name': 'q_bloodtoxeus_lone_50 (Hemorrheus, parchment @50%)',
    },
] + [
    {
        # GROUP F: the 4 obsidian-roulette corner proxies all share the ONE
        # warband pool (spawnMax=6, championChance=100, championMax=5 -> 1
        # guaranteed main = a RANDOM guardian). main_monster = Ilsevar (in a
        # name slot, highest band L74 <= the [1..110] limit window). The
        # champion-crowd-out math is identical for all 4; register each so both
        # the math AND the per-proxy limit window are proven for every placement.
        'proxy': _OBS_CORNERS[_c],
        'pool': _OBS_WARBAND_POOL,
        'main_monster': _OBS_ILSEVAR,
        'name': f'q_obs_roulette_{_c} (obsidian roulette corner @25%)',
    }
    for _c in 'abcd'
] + [
    # GROUP 1 (test yard): every NEW yard proxy is registered so the champion-
    # crowd-out (spawnMax-championMax>=1) + limit-window (main charLevel <= the
    # [1..110] limit max on N/E/L) checks prove each yard fight spawns its main.
    # THIS is why the yard pools use limit_obsidianbosses ([1..110]): the Enslaver
    # (L100) and Ilsevar (L74) exceed herolimit_all's Legendary cap of 75.
    {
        'proxy': _YARD_ENSLAVER_PROXY, 'pool': _YARD_ENSLAVER_POOL,
        'main_monster': _EN_BOSS,
        'name': 'q_yard_enslaver (yard: Enslaver boss @100%)',
    },
    {
        # marauder pack: championChance=0 -> all spawnMax(=4) slots are mains; the
        # Champion marauder (L[40,68,100]) needs the [1..110] window too.
        'proxy': _YARD_MARAUDERS_PROXY, 'pool': _YARD_MARAUDERS_POOL,
        'main_monster': _EN_MARAUDER,
        'name': 'q_yard_marauders (yard: marauder pack 3-4 @100%)',
    },
] + [
    {
        # 4 obsidian-guardian yard pools: name1..3 = the ONE guardian,
        # championMin=Max=5 -> 6-5=1 guaranteed guardian; main = that guardian.
        'proxy': _YARD_OBS_PROXY[_c], 'pool': _YARD_OBS_POOL[_c],
        'main_monster': _YARD_OBS_GUARDIANS[_c],
        'name': f'q_yard_obs_{_c} (yard: obsidian guardian @100% + warband)',
    }
    for _c in _YARD_OBS_GUARDIANS
] + [
    {
        # wyrm horde: reuses svc_wyrmhorde_03 (spawnMax=16, championMax=6 ->
        # 16-6=10 guaranteed common wyrms); main = the common wyrm (L[31,51,66]).
        'proxy': _YARD_WYRM_PROXY, 'pool': _YARD_WYRM_POOL,
        'main_monster': r'records\creature\monster\sepulchralwyrm\um_sepulchralwyrm_common_31.dbr',
        'name': 'q_yard_wyrm (yard: sepulchral wyrm horde @100%)',
    },
] + [
    {
        # BROODMOTHER NEST: the lone-boss placement (spawnMax=3, championMin=Max=2 ->
        # 3-2=1 guaranteed main = the mother; limit_broodnest [1..110] contains her
        # L74 + the L71 escort). main = um_broodmother_99.
        'proxy': _BM_PROXY, 'pool': _BM_POOL,
        'main_monster': _BM_MONSTER,
        'name': 'q_broodmother_lone (Broodmother + 2 elder-worm escorts)',
    },
    {
        # BROODMOTHER yard placement (TESTHUB-only): same nest shape (mother + 2
        # escorts @100%); same spawn-eligibility math + limit window.
        'proxy': _BM_YARD_PROXY, 'pool': _BM_YARD_POOL,
        'main_monster': _BM_MONSTER,
        'name': 'q_yard_broodmother (yard: Broodmother nest @100%)',
    },
] + [
    {
        # A5 PROPONTIS: Dorus the Drowned King lone placement (spawnMax=3,
        # championMin=Max=2 -> 3-2=1 guaranteed main = the king; limit_
        # obsidianbosses [1..110] contains his L71). main = um_dorus_99.
        'proxy': _DK_PROXY, 'pool': _DK_POOL,
        'main_monster': _DK_BOSS,
        'name': 'q_dorus_lone (Dorus, the Drowned King + 2 royal-guard escorts)',
    },
    {
        # A5 Dorus TESTHUB yard placement (same shape @100%).
        'proxy': _DK_YARD_PROXY, 'pool': _DK_YARD_POOL,
        'main_monster': _DK_BOSS,
        'name': 'q_yard_dorus (yard: Dorus + escorts @100%)',
    },
]


def _lim_eq_to_int(s):
    """Parse a ProxyLimits equation string like '110 * 1' / '38* 1' / '26 * 1' to its
    integer coefficient (the level). Returns None if unparseable."""
    if s is None:
        return None
    try:
        # equations are '<level> * 1' (spacing varies); take the leading number
        head = str(s).split('*')[0].strip()
        return int(float(head))
    except (ValueError, TypeError):
        return None


def _verify_mod_spawn_proxies_eligible(db):
    """FAIL-LOUD invariant: for every mod-authored spawn proxy, prove the MAIN (boss)
    monster will actually SPAWN on all three difficulties. Two independent checks,
    each of which silently produced a no-spawn boss in a shipped build if wrong:

      (A) CHAMPION-CROWD-OUT (the 2026-07-07 Hemorrheus bug): championChance is the
          per-spawn chance a slot is filled by a nameChampionN monster INSTEAD of a
          main-pool nameN monster. If the pool cannot leave >=1 slot for the main, the
          boss NEVER spawns. Guaranteed main slots = spawnMax - championMax (when
          championChance>0); if championChance==0 all spawnMax slots are mains. Assert
          this is >= 1. (Root cause: spawnMax=1 + championChance=100 + championMin=1 ->
          0 guaranteed mains -> only blood demons spawned, never the boss.)

      (B) LIMIT-WINDOW CONTAINMENT: the proxy's difficultyLimitsFile sets per-mode
          max PLAYER-level windows; a main monster whose charLevel exceeds the window
          max is SCALED DOWN toward it (it still spawns - Hades L80 via bosslimit_all
          max75 proves exceeding does not filter - but a lone superboss should fight at
          his authored level). Assert the main's charLevel <= the limit window's max on
          every difficulty, so he is never diluted. (This is the "brackets intersect on
          ALL difficulties" gate the fix brief requires; for a single-level boss,
          intersection == the boss level sitting within [min,max].)
    """
    def _base(p):
        """basename without importing os (paths use backslashes)."""
        return str(p).replace('/', '\\').split('\\')[-1]

    problems = []
    for spec in _MOD_AUTHORED_SPAWN_PROXIES:
        proxy, pool, main = spec['proxy'], spec['pool'], spec['main_monster']
        label = spec['name']
        if not db.has_record(proxy):
            problems.append(f"{label}: proxy record {proxy} MISSING")
            continue
        if not db.has_record(pool):
            problems.append(f"{label}: pool record {pool} MISSING")
            continue

        def gi(rec, f, d=0):
            v = db.get_field_value(rec, f)
            if v is None:
                return d
            return (v[0] if isinstance(v, list) else v)

        # (A) champion-crowd-out
        spawn_max = gi(pool, 'spawnMax', 0)
        champ_chance = gi(pool, 'championChance', 0.0)
        champ_max = gi(pool, 'championMax', 0)
        guaranteed_mains = spawn_max if (champ_chance or 0) <= 0 else (spawn_max - champ_max)
        if guaranteed_mains < 1:
            problems.append(
                f"{label}: CHAMPION-CROWD-OUT - guaranteed main slots = "
                f"{guaranteed_mains} (spawnMax={spawn_max}, championChance={champ_chance}, "
                f"championMax={champ_max}); the boss will NEVER spawn (only champion adds). "
                f"Need spawnMax - championMax >= 1 (or championChance == 0).")
        # sanity: the main must actually be in a name-slot
        name_slots = [gi(pool, f'name{i}', None) for i in range(1, 7)]
        if not any(n and str(n).lower() == main.lower() for n in name_slots):
            problems.append(
                f"{label}: main monster {main} is not in any pool nameN slot "
                f"(name1..6 = {[_base(str(n)) for n in name_slots if n]})")

        # (B) limit-window containment (per difficulty)
        lim = db.get_field_value(proxy, 'difficultyLimitsFile')
        lim = lim[0] if isinstance(lim, list) else lim
        cl = db.get_field_value(main, 'charLevel')
        if lim and db.has_record(lim) and cl:
            levels = cl if isinstance(cl, list) else [cl]
            mode_fields = [
                ('Normal', 'minPlayerLevelEquationNormal', 'maxPlayerLevelEquationNormal', 0),
                ('Epic', 'minPlayerLevelEquationEpic', 'maxPlayerLevelEquationEpic', 1),
                ('Legendary', 'minPlayerLevelEquationLegendary', 'maxPlayerLevelEquationLegendary', 2),
            ]
            for mode, minf, maxf, idx in mode_fields:
                if idx >= len(levels):
                    continue
                mlvl = levels[idx]
                wmin = _lim_eq_to_int(db.get_field_value(lim, minf))
                wmax = _lim_eq_to_int(db.get_field_value(lim, maxf))
                if wmax is not None and mlvl > wmax:
                    problems.append(
                        f"{label}: LIMIT-WINDOW - {mode} main charLevel {mlvl} > limit "
                        f"window max {wmax} ({_base(str(lim))}); the boss is "
                        f"scaled DOWN below his authored level. Use a limits file whose "
                        f"{mode} window contains {mlvl}.")
                if wmin is not None and mlvl < wmin:
                    problems.append(
                        f"{label}: LIMIT-WINDOW - {mode} main charLevel {mlvl} < limit "
                        f"window min {wmin} ({_base(str(lim))}).")
        elif lim and not db.has_record(lim):
            problems.append(f"{label}: difficultyLimitsFile {lim} does not resolve")

    if problems:
        print(f"\n  SPAWN-ELIGIBILITY INVARIANT FAILED: {len(problems)} problem(s):")
        for p in problems:
            print(f"    - {p}")
        raise SystemExit(
            f"Spawn-eligibility gate breached: {len(problems)} mod-authored spawn "
            f"proxy problem(s) (see above). A boss that cannot claim a spawn slot, or "
            f"is scaled below its level, must be fixed before shipping.")
    print(f"  Spawn-eligibility invariant OK: {len(_MOD_AUTHORED_SPAWN_PROXIES)} "
          f"mod-authored spawn proxy(ies) spawn their boss on N/E/L with adds.")


def apply_all_extended_patches(db, force_full_drops=True):
    """Run all extended patches. Call after create_uber_souls.

    force_full_drops: when True (the current default for testing builds),
    override every monster's soul drop rate to 100% (see
    _force_100_pct_soul_drops) so souls are easy to test in-game. Pass False
    (wired to the SVC_RELEASE_DROPS=1 env var by build_svc_database.py) to keep
    the tuned 66% (Hero/Quest) / 25% (Boss) rates for a release build.
    """
    tags = {}
    _SUMMON_PET_BUILDS.clear()   # build36 A1: fresh per-run registry for the pet gates

    tags['tagSVCSummonRakanizeus'] = 'Call of the Storm Tyrant'
    tags['tagSVCSummonRakanizeusDESC'] = (
        'The captured soul of Rakanizeus strains against its bonds, '
        'desperate to reform. Release it and the lightning god-satyr '
        'manifests in a crackling storm of chain lightning, '
        'bound to serve until the tempest fades.'
    )

    tags['tagSVCSummonBoneash'] = 'Summon Boneash'
    tags['tagSVCSummonBoneashDESC'] = (
        'Release the imprisoned essence of Boneash, '
        'a skeletal fire mage consumed by arcane flame. '
        'The revenant rises wreathed in fire, hurling bolts of destruction '
        'and igniting the ground beneath its enemies.'
    )

    tags['tagSVCSummonPharaohGuard'] = "Summon Pharaoh's Honor Guard"
    tags['tagSVCSummonPharaohGuardDESC'] = (
        'Awaken the ancient stone guardian, eternally bound to protect '
        "the pharaoh's tomb. The construct rises with unyielding resolve, "
        'crushing enemies with devastating physical force while shrugging '
        'off blows that would fell lesser beings.'
    )

    # A10 (build29, owner request): summon-the-boss souls
    tags['tagSVCSummonNarok'] = 'Summon Narok the Rockskin'
    tags['tagSVCSummonNarokDESC'] = (
        'The stone-scaled dragonian sorcerer answers the call of his own '
        'captured soul. Narok strides forth with staff in claw, weaving '
        'ternion bolts and storm orbs while his rocky hide turns aside '
        'the blows of lesser foes.'
    )
    tags['tagSVCSummonVort'] = 'Summon Vort the Red'
    tags['tagSVCSummonVortDESC'] = (
        'Vort the Red erupts from his soul-prison in a crackle of crimson '
        'lightning. The dragonian storm-lord hurls thunderballs and '
        'concussive blasts, his red-scaled bulk a living bulwark before '
        'his summoner.'
    )

    # Soul name tags ({^F} = pink/magenta color, matching original SV soul style)
    tags['tagSVCSoulColdWorm'] = '{^F}Cold Worm Soul'
    tags['tagSVCSoulSPToxeus'] = '{^F}Soul of Toxeus the Murderer (SP)'
    tags['tagSVCSoulLeinth'] = '{^F}Soul of Leinth the Blood Witch'
    tags['tagSVCSoulMurderBunny'] = '{^F}Soul of the Murder Bunny'
    tags['tagSVCSoulSPHades'] = '{^F}Soul of Hades (SP)'
    tags['tagSVCSoulDagon'] = '{^F}Soul of Dagon'
    tags['tagSVCSoulNMega'] = '{^F}Soul of the Neanderthal Boss'
    tags['tagSVCSoulNEmgiec'] = '{^F}Soul of the Neanderthal Hacker'
    tags['tagSVCSoulNVio'] = '{^F}Soul of the Neanderthal Wizard'
    # Monster name tag (Cold Worm's description tag was undefined)
    tags['tagD2Boss004'] = 'Cold Worm'

    # Dev skeleton soul name tags (Task 3 — pink prefix)
    tags['tagSVCSoulDevArthur']  = '{^F}Soul of Arthur'
    tags['tagSVCSoulDevBen']     = '{^F}Soul of Ben'
    tags['tagSVCSoulDevChooch']  = '{^F}Soul of Chooch'
    tags['tagSVCSoulDevCory']    = '{^F}Soul of Cory'
    tags['tagSVCSoulDevDave']    = '{^F}Soul of Dave'
    tags['tagSVCSoulDevDavid']   = '{^F}Soul of David'
    tags['tagSVCSoulDevFrazier'] = '{^F}Soul of Frazier'
    tags['tagSVCSoulDevJosh']    = '{^F}Soul of Josh'
    tags['tagSVCSoulDevMorgan']  = '{^F}Soul of Morgan'
    tags['tagSVCSoulDevNate']    = '{^F}Soul of Nate'
    tags['tagSVCSoulDevParnell'] = '{^F}Soul of Parnell'
    tags['tagSVCSoulDevScott']   = '{^F}Soul of Scott'
    tags['tagSVCSoulDevShawn']   = '{^F}Soul of Shawn'
    tags['tagSVCSoulDevTom']     = '{^F}Soul of Tom'
    tags['tagSVCSoulDevTildaV']  = '{^F}Soul of ~V~'

    # New soul tags (Tasks 4, 7, 9)
    tags['tagSVCSoulFeth'] = '{^F}Soul of Feth'
    tags['tagSVCSoulPhagia'] = '{^F}Soul of Phagia'
    tags['tagSVCSoulFrost'] = '{^F}Soul of Frost'
    tags['tagSVCSoulAinex'] = '{^F}Soul of Ainex'
    tags['tagSVCSoulDroolbog'] = '{^F}Soul of Droolbog'
    tags['tagSVCSoulProx'] = '{^F}Soul of Prox'
    tags['tagSVCSoulYama'] = '{^F}Soul of Yama'
    tags['tagSVCSoulInkeyes2'] = '{^F}Soul of Inkeyes'
    tags['tagSVCSoulTombguardian'] = '{^F}Soul of the Tomb Guardian'
    tags['tagSVCSoulLash'] = '{^F}Soul of Lash'
    tags['tagSVCSoulTheFlayer'] = '{^F}Soul of the Flayer'
    tags['tagSVCSoulRottingDevourer'] = '{^F}Soul of the Rotting Devourer'

    # ── Boss Souls wave tags (docs/BOSS_SOULS_DESIGN.md Section 9) ──
    # tagSVCSoulAinex already defined above (its rich block reuses the existing tag).
    tags['tagSVCSoulAinexDESC'] = (
        'The Queen of Crows carves souls from the air with spectral bolts. Bound '
        'into this ring, her essence lends the bearer her uncanny evasion and the '
        'killing lance of her gaze.')
    tags['tagSVCSoulBWHighPriest'] = '{^F}Soul of the Blood High Priest'
    tags['tagSVCSoulBWHighPriestDESC'] = (
        'High Priest of the Blood Witch cult, who tore living demons from the '
        'blood of his victims. His soul, released, calls forth a Melinoe '
        'blade-dancer to fight at your side until it is cut down.')
    tags['tagSVCSummonBWHighPriest'] = 'Call the Blood Blade-Dancer'
    tags['tagSVCSummonBWHighPriestDESC'] = (
        'Release the imprisoned Melinoe blade-dancer, a synergy demon torn from '
        'blood, to dance her killing dance at your side.')
    tags['tagSVCSoulLimosLifeeater'] = '{^F}Soul of the Lifeeater'
    tags['tagSVCSoulLimosLifeeaterDESC'] = (
        'The Lifeeater knows only endless hunger. Its soul drains the vitality of '
        'all it touches, feeding the bearer on the lives of the slain.')
    tags['tagSVCSoulKallixenia'] = '{^F}Soul of Kallixenia'
    tags['tagSVCSoulKallixeniaDESC'] = (
        'Kallixenia, the Lich Queen, rained soul-orbs from a poisoned sky. Her '
        "soul answers the call, drawing down a storm of life-stealing spirits "
        "upon the bearer's foes.")
    tags['tagSVCSoulLilLued'] = "{^F}Soul of Lil'Lued the Elder Djinn"
    tags['tagSVCSoulLilLuedDESC'] = (
        "Bound in a crow-cursed lamp, the Elder Djinn Lil'Lued rages against its "
        'imprisonment. Freed by the soul, it fights beside you wreathed in storm '
        'and blood-pact, hastening your step and blasting your enemies.')
    tags['tagSVCSummonLilLued'] = 'Free the Elder Djinn'
    tags['tagSVCSummonLilLuedDESC'] = (
        'Shatter the crow-cursed lamp and loose the Elder Djinn, a towering '
        'storm-wreathed ally, to blast your foes and haste your step.')
    tags['tagSVCSoulZilla'] = '{^F}Soul of Zilla the Blade Dancer'
    tags['tagSVCSoulZillaDESC'] = (
        'Zilla dances between two frost-forged blades, freezing all he cuts. His '
        'soul grants the whirling blade-storm and the killing cold of the Crow '
        'assassins.')
    tags['tagSVCSoulNumberouane'] = '{^F}Soul of Numberouane'
    tags['tagSVCSoulNumberouaneDESC'] = (
        'The Frost King of the Crow court buries his foes beneath endless '
        'blizzards. His soul calls down the frost-storm and armors the bearer '
        'against the cold he commands.')
    tags['tagSVCSoulKreeloo'] = '{^F}Soul of Kreeloo the Telkine'
    tags['tagSVCSoulKreelooDESC'] = (
        'Kreeloo, ghost of a fallen Telkine, still crackles with the '
        'chaos-lightning of the god-kings. His soul looses spectral thunderballs '
        "and wraps the bearer in a telkine's storm.")
    tags['tagSVCSoulKaets'] = '{^F}Soul of Kaets the Thornheart'
    tags['tagSVCSoulKaetsDESC'] = (
        'Kaets, the walking thornwood of the Crow court, seeds the earth with '
        'living quill-vines. Its soul lets the bearer raise a thicket of thrashing '
        'thorns to rend the enemy.')
    tags['tagSVCSoulAnapaest'] = '{^F}Soul of Anapaest the Dishonored'
    tags['tagSVCSoulAnapaestDESC'] = (
        'Anapaest, a gigantes cast out for dishonor, shatters the earth with every '
        'blow. His soul grants the ground-breaking wave and the tireless '
        'regeneration of the giant-kind.')
    # Crow Heroes (remaining)
    tags['tagSVCSoulGorgus'] = '{^F}Soul of Gorgus'
    tags['tagSVCSoulGorgusDESC'] = (
        'Gorgus, blade-twin of Zilla, spins a beastman whirlwind of frost-forged '
        'steel. His soul grants the whirling blades and the cold of the Crow court.')
    tags['tagSVCSoulJiaco'] = '{^F}Soul of Jiaco the Nightstalker'
    tags['tagSVCSoulJiacoDESC'] = (
        'Jiaco stalks the shadows and strikes from nowhere. His soul grants the '
        "nightstalker's shadow-surge and the killing precision of the Crow assassins.")
    tags['tagSVCSoulYerk'] = '{^F}Soul of Yerk'
    tags['tagSVCSoulYerkDESC'] = (
        'Yerk pounds the earth with his great club and lulls his foes to a deadly '
        'sleep. His soul grants the ground-pound and the chain-sleep of the brute.')
    tags['tagSVCSoulJabarto'] = '{^F}Soul of Jabarto'
    tags['tagSVCSoulJabartoDESC'] = (
        'Jabarto, boarman storm-caller of the Crow court, wreathes himself in '
        'lightning. His soul looses the storm-nimbus and the chaining bolt.')
    tags['tagSVCSoulRainbowbright'] = '{^F}Soul of Rainbowbright the Standard-Bearer'
    tags['tagSVCSoulRainbowbrightDESC'] = (
        'Rainbowbright rallies the insectoid host beneath his battle standard. His '
        'soul raises that standard to hearten your allies and break your foes.')
    tags['tagSVCSoulLess'] = '{^F}Soul of Less'
    tags['tagSVCSoulLessDESC'] = (
        'Less bursts from its icy igloo in a shock of spell-broken frost. Its soul '
        'grants the igloo-burst and the biting cold of the Crow beasts.')
    tags['tagSVCSoulNomnom'] = '{^F}Soul of Nomnom'
    tags['tagSVCSoulNomnomDESC'] = (
        'Nomnom feasts on plague and rot. Its soul spits venom and festering '
        'poison upon all who draw near.')
    tags['tagSVCSoulGitar3'] = '{^F}Soul of the Gitar Shrine'
    tags['tagSVCSoulGitar3DESC'] = (
        'A crackling rock-shrine of the Crow court, the Gitar turret reflects '
        'harm back upon its attackers. Its soul lends that reflecting ward and a '
        'lash of lightning.')
    tags['tagSVCSoulKir4'] = '{^F}Soul of the Kir Trap'
    tags['tagSVCSoulKir4DESC'] = (
        'The Kir tiki-trap looses a burst of piercing bolts at the unwary. Its '
        "soul grants that trap-hunter's volley and the hunter's eye.")
    tags['tagSVCSoulLilLuedChild'] = '{^F}Soul of Little Lued'
    tags['tagSVCSoulLilLuedChildDESC'] = (
        'The child-spirit of Little Lued lingers, a small and stubborn ember of '
        'the djinn it might have become.')
    # D2 NPC trio (Charsi, Gheed; Kallixenia above)
    tags['tagSVCSoulCharsi'] = '{^F}Soul of Charsi the Smith'
    tags['tagSVCSoulCharsiDESC'] = (
        "Charsi the smith swings her hammer like a weapon of war, opening wounds "
        "that will not close. Her soul grants the smith's crushing strike.")
    tags['tagSVCSoulGheed'] = '{^F}Soul of Gheed the Merchant'
    tags['tagSVCSoulGheedDESC'] = (
        'Gheed the caravan merchant survives by luck, speed, and a merchant\'s '
        'cunning. His soul lends the bearer his charmed endurance and quick feet.')
    # Other single-boss targets
    tags['tagSVCSoulBloodShaman'] = '{^F}Soul of the Blood Shaman'
    tags['tagSVCSoulBloodShamanDESC'] = (
        'The Blood Shaman drains life and mana with shadow spells. His soul feeds '
        "the bearer on the enemy's vitality and chills the air with decay.")
    tags['tagSVCSoulFleshrender'] = '{^F}Soul of the Fleshrender'
    tags['tagSVCSoulFleshrenderDESC'] = (
        'The Fleshrender raptor tears its prey to ribbons. Its soul grants the '
        'rending saber-slash and the bleeding hunger of the pack.')
    tags['tagSVCSoulAnklesickle'] = '{^F}Soul of the Anklesickle'
    tags['tagSVCSoulAnklesickleDESC'] = (
        'The Anklesickle strikes from ambush with venom-slick blades. Its soul '
        'grants the poisoned ambush-volley and the tidecrawler\'s evasion.')
    tags['tagSVCSoulDarkMonolith'] = '{^F}Soul of the Dark Monolith'
    tags['tagSVCSoulDarkMonolithDESC'] = (
        'The Dark Monolith crackles with a stone-bound curse. Its soul looses '
        'that curse as lightning and vitality and armors the bearer like ancient '
        'stone.')
    tags['tagSVCSoulFireTrap'] = '{^F}Soul of the Fire Trap'
    tags['tagSVCSoulFireTrapDESC'] = (
        'The Fire Trap erupts in a burst of flame at the careless. Its soul grants '
        'that fiery burst and turns the bearer\'s skin to searing retaliation.')

    # ── Blood Toxeus wave tags (docs/BLOOD_TOXEUS_DESIGN.md §6.3) ──
    # RENAME (Will 2026-07-07): the boss is now explicitly a Toxeus derivative -
    # "Toxeus the Murderer, Devourer of Blood" (verbatim from Will). The Athens
    # Toxeus display name is "Toxeus the Murderer" (tagMonsterName190); this name
    # extends it with the blood-devourer epithet so both bosses read as the same
    # murderer, one crimson-reborn. 38 visible chars (color code {^r} is free) -
    # shorter than 8 shipped boss/hero names (e.g. "Sentinel Nok-hai, Guardian of
    # the Necklace" 42, "Fenuku, Martyr of the Crimson Brotherhood" 41), and the
    # "Name, Epithet of X" comma form is a shipped convention, so it fits the
    # nameplate. The record path (um_bloodtoxeus_99) is UNCHANGED - only the
    # display tag is renamed.
    tags['tagMonsterHemorrheus'] = '{^r}Toxeus the Murderer, Devourer of Blood'
    # His soul keeps the new identity WITHOUT duplicating the green Toxeus's soul
    # ("{^F}Toxeus the Murderer Soul" = tagSoulName505) or the SP soul
    # ("{^F}Soul of Toxeus the Murderer (SP)" = tagSVCSoulSPToxeus). "Devourer of
    # Blood Soul" (Will's suggestion) is distinct from both and on-identity.
    # (Tag key stays tagSVCSoulHemorrhage - key is engine identity, only the value
    # is renamed; renaming the key would orphan the soul's itemNameTag binding.)
    # D7 (Will 2026-07-09): summon-the-boss soul; full disambiguated name.
    tags['tagSVCSoulHemorrhage'] = '{^F}Toxeus the Murderer, Devourer of Blood Soul'
    tags['tagSVCSoulHemorrhageDESC'] = (
        'Toxeus the Murderer, boiled down and refilled with the blood of the drowned. '
        'Its bearer may call him forth to fight at their side - a crimson revenant '
        'who opens every wound and drinks the field dry.')
    tags['tagSVCSummonBloodToxeus'] = 'Summon Toxeus the Murderer, Devourer of Blood'
    tags['tagSVCSetCrimsonVerdict'] = 'The Crimson Verdict'
    tags['tagSVCwpnVeinRender'] = '{^r}Vein-Render'
    tags['tagSVChlmCrimsonVerdict'] = '{^r}Cowl of the Red Verdict'
    tags['tagSVCtorCrimsonVerdict'] = '{^r}Sanguine Shroud'
    tags['tagSVCarmCrimsonVerdict'] = '{^r}Hemorrhage Bindings'

    overhaul_souls(db)
    _add_dagon_to_ichthian_pools(db)
    _add_coldworm_to_egypt_pools(db)
    _boost_coldworm_stats(db)
    _create_coldworm_soul(db)
    _create_sp_toxeus_soul(db)
    _overhaul_main_toxeus_soul(db)
    _create_leinth_soul(db)
    _create_murder_bunny_soul(db)
    _create_sp_hades_soul(db)
    _create_dagon_soul(db)
    _create_dev_skeleton_souls(db)
    _overhaul_melalos_soul(db)
    _create_neanderthal_warband_monsters(db)   # Task 5: create records first
    _create_neanderthal_warband_souls(db)
    cascade_merc_scrolls(db)
    add_blood_mistress_to_loot(db)

    # New patches (Tasks 2, 4, 6-9)
    _audit_uber_soul_skips(db)
    _create_feth_variants_and_soul(db)
    _verify_graeae_wiring(db)
    _place_orphan_monsters(db)
    _wire_difficulty_variants(db)
    _wire_it_expansion_orphans(db)

    # Soul quality passes
    _overhaul_generic_souls(db)
    _apply_d8_d9_summon_souls(db, tags)   # D8 Xeiwang + D9 Huo-ren summon-souls (after the overhaul, so the summon rewire wins)
    _create_olympus_rhodes_herald(db, tags)   # Q3: Olympus->Rhodes boat-dialog herald (record path locked with the map lane)
    _create_helos_portal_master(db, tags)     # Q2 (Group A): Helos portal-master NPC -> 4 SV-area boat destinations (map lane places it)
    _create_testhub_portal_npcs(db, tags)     # Portal rig (GROUP 2 unblock): TESTHUB hub + return NPCs -> Model C travel (map lane places them; INERT on canonical)
    _create_emberscale_charm(db, tags)    # D10 Emberscale charm (turtle pattern; Flameguard Slayer 7%)
    # B-SOUL-PROC-1 FIX B: the 8 explicit itemSkillLevel==0 souls (SV-upstream
    # snaptooth/rocksting/orythroneus e/l tiers + generator crowboar n/e). Runs
    # after the overhauls; crowboar_* exist already (create_uber_souls runs
    # before apply_all_extended_patches).
    _fix_zero_level_soul_procs(db)

    # ── Boss Souls wave (docs/BOSS_SOULS_DESIGN.md) ──
    # Order: run AFTER _place_orphan_monsters (so _create_ainex_soul REPLACES the
    # thin svc_uber\ainex_soul placeholder at the same paths) and AFTER
    # _overhaul_generic_souls (so _complete_boss_souls deepens the OVERHAULS-touched
    # Table B souls with proper N/E/L tier scaling). Gate leaks BEFORE the drop
    # forcer so it never boosts a gated Common/no-class record to 100%.
    print("\n=== Boss Souls wave (design doc) ===")
    # Headliners (skill souls + in-place stub/placeholder fixes)
    _create_ainex_soul(db)
    _fix_limos_lifeeater_stub(db)
    _create_kallixenia_soul(db)
    _create_zilla_soul(db)
    _create_numberouane_soul(db)
    _create_kreeloo_soul(db)
    _create_kaets_soul(db)
    _create_anapaest_soul(db)
    # Headliner summon souls (pet built first, then soul)
    _create_bwpriest_pet_skill(db)
    _create_bwpriest_soul(db)
    _create_lillued_pet_skill(db)
    _create_lillued_soul(db)
    # Faction + trio + other single-boss targets
    _create_crow_heroes_souls(db)
    _create_d2npc_souls(db)
    _create_other_soul_targets(db)
    # Table B completion pass (deepen ~51 wired-but-shallow boss souls in place)
    _complete_boss_souls(db)
    # Gate Common/no-class soul leaks (skeletaltyphon.dbr, um_tombguardian_26)
    _gate_common_soul_leaks(db)

    # ── Blood Toxeus wave (docs/BLOOD_TOXEUS_DESIGN.md) ──
    # Hemorrheus superboss + Crimson Verdict legendary set + his soul + loot.
    # Runs AFTER the gate (he is a legit Boss, so the drop forcer keeping his
    # soul at 100% is intended) and BEFORE _force_100_pct_soul_drops.
    _create_blood_toxeus(db)

    # M15 (Will): Toxeus joins the chest-room egg group @100 + the derived
    # parchment demon group @50. Must run AFTER _create_blood_toxeus (needs
    # um_bloodtoxeus_99 to exist).
    _apply_m15_toxeus_group_joins(db)

    # GROUP 3 (build31): D11 Rally + D12 Myrmidon + D16 Shadow Stalker +
    # D17 Core Dweller + D18 Emberscale (D15 potion colors ride
    # build_text_arc). After D10 above, so the charm records exist.
    print("\n=== GROUP 3: D11/D12/D16/D17/D18 tunes ===")
    _apply_group3_tunes(db, tags)

    # GROUP 4 (build31): the four Will-named summon-the-boss souls.
    print("\n=== GROUP 4: D13/D14/D20/D21 summon souls ===")
    _apply_group4_summons(db, tags)

    # GROUP C (build32): Vashkarr, Eldest of the Ancients (N4-DB). After the
    # groups (a legit Boss, so the drop forcer keeping his soul at 100% in test
    # mode is intended) and BEFORE _verify_boss_kit_clone_shape (registers its
    # minion-summon clone) + _force_100_pct_soul_drops.
    print("\n=== GROUP C: Vashkarr, Eldest of the Ancients ===")
    _create_vashkarr(db, tags)

    # GROUP G (build32): N7 sepulchral wyrm hordes + the Sepulchral Scale charm.
    print("\n=== GROUP G: Wyrm Hordes + Sepulchral Scale ===")
    _create_wyrm_hordes(db, tags)

    # build36 A3 (Will 2026-07-11): Sanguine Tithe jewelry blood charm off the
    # Sileni (blood-harness satyrs). After the charm builders (D10/Group-G), the
    # same turtle/emberscale/sepulchral pattern; coupled arz + Text (2 new tags +
    # the {^G} Sileni green-name polish).
    print("\n=== build36 A3: Sanguine Tithe (Sileni blood relic) ===")
    _create_sanguine_tithe(db, tags)

    # BROODMOTHER NEST (build34+, Will 2026-07-10): the deferred apex wyrm set-piece.
    # MUST run AFTER _create_wyrm_hordes (references its tier-03 Sepulchral Scale loot
    # table + the common/champion wyrms) and BEFORE the clone-shape / spawn-eligibility
    # / soul gates + the build29 castability wave (which post-processes her summon soul).
    # MAP-REF-1: her q_broodmother_lone + q_broodnest_egg_* proxies land here so the map
    # lane can inject the placements (recommended host tombobs02).
    print("\n=== BROODMOTHER NEST: apex wyrm set-piece ===")
    _create_broodmother_nest(db, tags)

    # RUNE GOLEM (SVAERA Runemaster graft; docs/SVAERA_MASTERY_COMPARISON.md). The
    # doc's deferred D5-blocked item: a durable elite construct pet grafted onto our
    # vanilla Runemaster tree from a committed faithful snapshot, its render closure
    # shipped in assets/runegolem/*.arc. Independent of the boss/soul machinery (not a
    # soul, not a boss), so it neither trips nor needs the clone-shape / soul gates; it
    # IS covered by validate_render_chain_golem + validate_player_skill_anims (its
    # ThunderClap summon anim rides the G0 anim-row completion).
    print("\n=== RUNE GOLEM: Runemaster construct pet (SVAERA graft) ===")
    _create_rune_golem(db, tags)

    # GROUP F (build32): N6 Obsidian Halls treasure roulette. After the groups
    # (guardians are legit Bosses, so the drop forcer keeping their souls at 100%
    # in test mode is intended) and BEFORE the build29 castability wave (which
    # post-processes the souls' granted skills) + the clone-shape / spawn-
    # eligibility gates. MAP-REF-1: the q_obs_roulette records land here so the
    # map lane can inject the 4 INJECT_SPECS + shared v0e branch (M10).
    print("\n=== GROUP F: Obsidian Halls Treasure Roulette ===")
    _create_obsidian_roulette(db, tags)

    # build36 A5 (Will 2026-07-11): PROPONTIS SUPER BOSS - Dorus, the Drowned King
    # (DB side only). MUST run AFTER _create_obsidian_roulette (the hoard reuses
    # its Boss-locked chest/pool records). Map lane places q_dorus_lone per
    # docs/reports/build36_laneA_map_needs.md.
    print("\n=== build36 A5: Propontis Super Boss (Dorus, the Drowned King) ===")
    _create_propontis_superboss(db, tags)

    # GROUP B (build32): Toxeus the Enslaver of Souls - a roaming rare mini-boss.
    # Build the boss/marauder/soul, then the roaming sweep (append him at weight 1
    # to eligible hostile trash pools, existing weights x60) + the fail-loud verify
    # gate. Before the build29 castability wave (processes his summon soul) and the
    # clone-shape gate (registers his hostile marauder-summon clone).
    print("\n=== GROUP B: Toxeus the Enslaver of Souls ===")
    _create_enslaver(db, tags)

    # GROUP 1 (test yard): build the TESTHUB monster-yard pool/proxy records. MUST
    # sit AFTER every yard-referenced group (Vashkarr/wyrm/obsidian/enslaver all
    # created above) and BEFORE the sweep + verify below, so _verify_roaming_sweep
    # sees the yard enslaver pool and whitelists it (_EN_YARD_POOLS). The sweep
    # itself never touches q_yard_* (basename q_ + non-allow-prefix path).
    print("\n=== GROUP 1: Monster Test Yard (TESTHUB-only) ===")
    _create_test_yard(db, tags)

    _enslaver_touched = _sweep_inject_roaming_rare(db)
    _verify_roaming_sweep(db, _enslaver_touched)

    # ── build29 wave: B-SOUL-PROC-2 + contract-suite DB fixes ────────────────
    # MUST run after EVERY soul-authoring pass above (it post-processes all
    # soul-granted skills) and before the activation invariant below (which now
    # also gates on anim playability + Enemy-controller autoTargetRadius).
    print("\n=== build29 wave: granted-skill castability + contract fixes ===")
    tags.update(_fix_wave29_contract_items(db))
    _fix_granted_skill_castability(db)
    # A4 (esti chest tier-1): NOT APPLIED - the closed RCA's mechanism is
    # disasm-REFUTED (see the block comment at _setup_esti_chest_tier1). A3
    # (starter chest) lives in build_svc_database.py (disasm-grounded).

    # ── build30 wave: D-item fixes (hanif nameplate; see _fix_wave30_items) ──
    print("\n=== build30 wave: D-item fixes ===")
    tags.update(_fix_wave30_items(db))
    # ── build30 wave: blade-dancer invisible-body family fix (D5) - runs after
    #    all record creation so it also catches the upstream hostile + proxies ──
    _fix_bladedancer_invisible_body(db)
    # ── build30 F-wave (post-vet): supra/glacialorb invisible renders + the
    #    pcsafe/Melee_Poison dangling-ref P1s (see _fix_wave30_render_and_refs) ──
    _fix_wave30_render_and_refs(db)

    # ── build36 A1 PET BUILDER OVERHAUL gates (fail-loud) ─────────────────────
    # After every summon pet is built: (1) relocate any SV-original buff-slot
    # summon (Aquardia/Dayria) globally so it can fire, then (2) run the three new
    # pet invariants - stat-mirror (source cadence + attributes), gear-parity
    # (exactly the source's gear both ways, Will's law) over every _build_boss_
    # summon family, and skill-kit (every summon in an AI-fired slot, no hostile
    # spawner) over every soul pet. A pet that trips any of these does NOT ship.
    print("\n=== build36 A1: pet builder overhaul gates ===")
    _fix_sv_pet_summons(db)
    _verify_summon_pet_parity(db, _SUMMON_PET_BUILDS)
    _verify_summon_pet_gear(db, _SUMMON_PET_BUILDS)
    _verify_summon_pet_skill_kit(db)

    # ── Boss-kit clone-shape invariant (fail-loud, B-TOXEUS-2) ────────────────
    # After all boss authoring: every registered boss-kit clone must keep its
    # donor's field shape (no added fields, no blanked .dbr refs, refs resolve).
    _verify_boss_kit_clone_shape(db)

    # ── Spawn-eligibility invariant (fail-loud) ───────────────────────────────
    # After the boss/proxy/pool are built, prove every mod-authored spawn proxy will
    # actually spawn its BOSS on all three difficulties: (A) the champion mechanic
    # cannot crowd the boss out of every spawn slot (the 2026-07-07 Hemorrheus
    # no-spawn bug: spawnMax=1 + championChance=100 -> 0 main slots -> only blood
    # demons), and (B) the boss's charLevel fits within the proxy's limits window on
    # N/E/L so he is never scaled below his authored level. Guards BOTH placements
    # (this proxy record is injected at the TESTHUB HV01 mouth AND the canonical
    # secret area). A silent no-spawn boss can never ship past this.
    _verify_mod_spawn_proxies_eligible(db)

    # ── Uber (DRX supra) craftable dead-reference repair ──────────────────────
    # Repair the two objectively-dead references baked into the DRX supra
    # craftables by their original authors (itemCostName stripped-separator on
    # all 23 results; the orphaned x-galefury buff edge). Both targets resolve;
    # no gameplay value changes. See docs/UBER_WEAPONS_AUDIT.md. The post-fix
    # invariant below fails the build loud if any known dead ref survives.
    _repair_supra_dead_refs(db)
    _supra_offenders = _verify_no_supra_dead_refs(db)
    if _supra_offenders:
        for _rec, _fn, _val in _supra_offenders[:10]:
            print(f"  SUPRA-REF OFFENDER: {_rec} :: {_fn} = {_val!r}")
        raise SystemExit(
            f"Supra dead-reference repair incomplete: {len(_supra_offenders)} "
            f"known-dead supra reference(s) still present (see offenders above)")

    # ── Soul-drop gate invariant (fail-loud) ──────────────────────────────────
    # After EVERY soul is wired and every known Common/no-class leak is gated,
    # prove that no non-Hero/Boss/Quest creature drops a soul in ANY equipment
    # slot. Runs in BOTH release and testing builds (before the drop forcer), so a
    # classification hole can never silently ship - the reason flipping to the
    # RELEASE default (tuned 66%/25%) is safe.
    _verify_no_unclassified_soul_leaks(db)

    # ── Soul augment/proc resolution invariant (fail-loud) ────────────────────
    # After every soul is wired, prove that every skill each soul GRANTS
    # (augmentSkillName1..4 / itemSkillName / itemSkillAutoController) points at a
    # real record. A dangling path is a silent no-op in-game (the bug that left
    # "the strongest soul in the game" with two dead augments). The standalone
    # tools/validate_soul_augments.py re-checks this on the written .arz.
    _verify_soul_augments_resolve(db)

    # ── Soul item-skill ACTIVATION invariant (fail-loud, B-SOUL-PROC-1) ──────
    # Resolution alone is not enough: a granted skill with itemSkillLevel
    # absent/0 instantiates at level 0 = INACTIVE (tooltip renders, proc never
    # fires - the Crommyonian Sow bug, 219 souls). Prove every granted-skill
    # soul has Class Skill_*, itemSkillLevel >= 1, and a live auto-controller.
    _verify_soul_itemskill_activation(db)

    # ── Multiplayer spawn-scaling equation fix (docs/MULTIPLAYER_COMPAT.md) ──
    # Rewrite SV's '/'-bearing proxy spawn/champion equations to '/'-free AE-valid
    # forms so MP monster/champion density scales as SV intends instead of
    # silently falling back to base-game pool defaults. Then assert the invariant
    # (no '/' left in any spawn equation) and fail the build loud if violated.
    _fix_mp_spawn_equations(db)
    _mp_offenders = _verify_no_slash_in_spawn_equations(db)
    if _mp_offenders:
        for _rec, _fn, _val in _mp_offenders[:10]:
            print(f"  MP-EQ OFFENDER: {_rec} :: {_fn} = {_val!r}")
        raise SystemExit(
            f"MP spawn-equation fix incomplete: {len(_mp_offenders)} spawn/champion "
            f"equation value(s) still contain '/' (see offenders above)")

    # Grid portals unconditionally OPEN + VISIBLE, no quest: swap the shared portal
    # ENTRANCE record (portal_olympianarena1) from Class GridEntranceDynamic (which
    # self-closes at every spawn and hides until a quest fires) to the born-open
    # static GridEntrance (always-visible + always-open, like every base-game cave
    # mouth), so every invented door + test-hub portal renders AND teleports on fresh
    # AND pre-existing characters with no bossarena.qst adoption dependency
    # (wf_c0012e88-64a goal; disasm-proven in docs/DYNGRID_GATE_RCA.md sec 5). Then
    # assert the invariant and fail the build loud if violated. NOTE: this DB half is
    # only valid paired with a map rebuilt by the current build_section_surgery.py
    # (60-byte entrance 0x14); see the COUPLING note at _make_portals_born_open_*.
    _make_portals_born_open_gridentrance(db)
    _apply_portal_visual(db)   # B-PORTAL-1: visible portal mesh (visual-only; after the class swap)
    _portal_offenders = _verify_portals_born_open(db)
    if _portal_offenders:
        for _rec, _fn, _val in _portal_offenders[:10]:
            print(f"  PORTAL-OPENNESS OFFENDER: {_rec} :: {_fn} = {_val!r}")
        raise SystemExit(
            "Grid-portal born-open class swap incomplete: the placed entrance record "
            "portal_olympianarena1.dbr is not a clean static GridEntrance "
            "(see offenders above). The map 0x14 must also be 60-byte; do not ship "
            "this arz against a 48-byte-0x14 map.")

    # ── A4 (build36, Will): zero the Aphiastas keres Finger2 soul drops ────────
    # Runs AFTER the soul-leak gate (the leak gate ignores chance=0 records) and
    # BEFORE the drop-rate forcer so the forcer's chance>0 gate leaves these at 0
    # in BOTH testing and release builds (they stop dropping the Aphiastas soul;
    # the souls-only Finger2 loot ref + any potion recipe stay intact).
    _apply_aphiastas_finger2_zero(db)

    # Soul drop rate. ON (100%) by default so souls are easy to test in-game.
    # The release build flips this to the tuned 66% (Hero/Quest) / 25% (Boss)
    # rates via SVC_RELEASE_DROPS=1 (threaded here as force_full_drops=False).
    if force_full_drops:
        _force_100_pct_soul_drops(db)
        print("  TESTING BUILD: soul drops forced to 100% "
              "(set SVC_RELEASE_DROPS=1 for tuned 66%/25% rates)")
    else:
        print("  RELEASE BUILD: tuned soul drop rates kept (66% Hero/Quest, 25% Boss)")

    return tags
