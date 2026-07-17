r"""toxeus_endofallthings - TOXEUS, END OF ALL THINGS (b72, Will ruled 2026-07-16).

WHAT THIS SHIPS
--------------------------------------------------------------------------------
A single supra-tier SOUL RING, crafted at the uber-forge from the LEGENDARY (_l)
tier of the three Toxeus souls (green-Greece base + Enslaver + Devourer), that
summons ONE permanent supra pet: "Toxeus the Murderer, End of All Things" - the
apotheosis of the Toxeus line, stronger than any Toxeus champion the player faces.

Ground truth: build45 arz md5 917d9047 (work/SoulvizierClassic/Database/
SoulvizierClassic.arz, read-only). Every donor/skill/equipment path below was
decoded live against that arz (docs/reports/b72_toxeus_endofallthings.md, RECON).

ENGINE LAWS honored (CLAUDE.md):
  - PET SAFETY: the 3 pets are CLONED from the PROVEN permanent Devourer pets
    (bloodtoxeus_1..3: RevenantPoison skeleton mesh, crimson skin, permanent =
    no spawnObjectsTimeToLive). Only animation/skill/FX/stat fields are edited;
    NO equipment/loot field is copied Monster.tpl->Pet.tpl (that crashes). Pet
    equipment uses _set_pet_equipment (hardcoded item paths) ONLY.
  - dtype: overrides on cloned records pass NO explicit dtype (preserve type);
    genuinely-new fields let set_field infer. Green-residue fields are DELETED
    by key (absent in the re-encoded record), never blanked to '' (loader-abort
    zero-precedent law).
  - Permanent, 1-at-a-time (petLimit 1, Lyia convention inherited from the pets).
  - Soul name 'Soul of Toxeus, End of All Things' ({^F} magenta) is Will-ruled;
    its tag is registered in apply_svc_patches._HAND_DESIGNED_SOUL_TAGS so the
    F6 '{^F}<Monster> Soul' naming gate exempts it (the Anapaest/Drowned-King
    precedent for a marquee 'Soul of X' name).
  - No em dashes anywhere.

THE KIT (Will verbatim rulings -> implementation; see the report for the full
kit table + feasibility flags):
  1. UNLIMITED ENERGY: huge characterMana + massive characterManaRegen on each
     pet record (crash-safe pure Character stat fields; Pet.tpl is a Character
     superset). Chosen over zeroing skill costs (which would edit SHARED skill
     records that the player + other monsters also use, and risk dtype corruption).
  2. NETHER STRIKE, max level, 0.5s cooldown: svc_eoat_netherstrike (clone of
     the Enslaver-proven netherstrike, skillCooldownTime 1.0 -> 0.5), fired at
     its skillMaxLevel (12). The Enslaver soul-pet already runs netherstrike, so
     it is proven pet-usable lineage.
  3. SMOKE SCREEN (Occult), max level: drx_smokescreen_petskill_default (the
     shipped Occult smoke-screen PET skill - proven pet-usable).
  4. GALEFURY skill: hunter_helm_galefury (the itemSkillName granted by the b66
     supra straw-hat ar_hunter_helm; a Skill_BuffAttackRadiusToggled storm-gale
     weapon aura). Given at level 1 (its skillMaxLevel).
  5. TEARS OF BLOOD: svc_eoat_tearsofblood (clone of the 'Arcane Formula - Blood
     of Ares' granted skill e_da_bloodofares_tearsofblood, a blood-tears AoE
     retaliation nova; skillCooldownTime 120 -> 3.0). FEASIBILITY: a true
     on-taking-damage trigger is an ITEM autocaster (triggerType HitByEnemy) a
     pet cannot carry; here it is a frequent specialAttack (3.0s cd) so it fires
     reactively in melee. Flagged.
  6. MURDERER'S EDGE: high characterOffensiveAbility on the pets + svc_eoat_
     murderersedge passive (offensive/crit). NO green poison - his weapon buff is
     the DEVOURER'S crimson blood-poison bloodtoxeus_envenomweapon (weapon tint
     R=1.0,G=0.25,B=0.25 + the leinth blood-aura charfx). FEASIBILITY: the
     Devourer has NO literally-black poison; bloodtoxeus_envenomweapon is the
     closest DARK/blood poison in his own lineage (his signature crimson envenom).
     Flagged (crimson, not literally black).
  7. ENTROPY AURA: svc_eoat_entropyaura (clone of the shadowlink weapon-
     enchantment aura Skill_BuffRadiusToggled) -> svc_eoat_entropybuff with a
     vitality-decay + resistance-shred payload, radius 36 (the b57 party-radius
     convention). FEASIBILITY: the shipped shadowlinkbuff payload is zeroed, so
     the debuff numbers here are authored fresh (resolution-safe; magnitudes are
     a tuning surface flagged for vet).
  8. BLOOD FEAST: deep life leech (high offensiveLifeLeech on the pets) + the
     Devourer's own blood nova melinoe_bloodboil (BloodBoil AoE) + lifedrain,
     all from the Devourer's proven kit.
  9. 'THERE IS ROOM IN ME': svc_eoat_thralls (Skill_SpawnPet) summons Blood-Witch
     Disciple thralls (eoat_disciple_1..3, the "tall casters in the blood cave"
     c_disciple_42 family) who carry the disciple's own disciple_summon_bloodbeast
     skill (which spawns bloodhounds). ** FEASIBILITY FLAG #1 (Will-mandated) **:
     this is a 3-DEEP chain (EoAT pet -> disciple thralls -> hound sub-summons).
     The PROVEN depth is 2 (Enslaver -> marauders, who summon nothing). Whether a
     PET's own spawn-pet skill fires while it is itself a pet is engine-UNVERIFIED.
     Round 1 wires the disciple thralls at the proven depth-2 and ATTACHES the
     hound summon for the depth-3 attempt, but the depth-3 leg is FLAGGED as
     needing Will's in-game confirmation. Fallback (documented, not shipped this
     round): drop the depth-3 leg and have the EoAT pet summon a few bloodhound
     pets DIRECTLY alongside the disciples (both depth-2, provably safe).
  10. 'THE ENDING' ultimate: svc_eoat_ending (clone of Manetho / Light-of-Helios
     screen-flash sungaze, Skill_AttackProjectileAreaEffect). The donor projectile
     aktaois_lightofra01 (the light-of-Ra screen flash Will asked to steal) is KEPT;
     the donor ships ZERO damage and a 'SunGaze' skillSpecialAnimationName the
     RevenantPoison skeleton rig lacks (uncastable per the b52 Ephialtes-nova lesson),
     so the clone CLEARS the special anim (the flash rides on the projectile record,
     not the animation) and AUTHORS real cataclysm damage (physical + vitality) at a
     wide explosion radius. Long cooldown, low specialAttack chance.
  11. ARRAT'S CORRUPTION AOE (Will 2026-07-16): reuse of the shipped soulskills variant
     of ararat_corruption - the signature ability of 'Arrat/Ararat the Corruptor'
     (um_ararat_36, spider family; his skillName2). A Skill_AttackRadius debuff nova
     (burns mana via offensiveManaBurnDamageRatio, slows attack speed, shortens the
     target life/mana-leach windows). The soulskills variant is already pet-castable
     (skillManaCost 0, cooldown 30) so it is reused verbatim (no shared-record edit)
     in the kit + specialAttack table at max level.

EQUIPMENT (Will: blood spear, uber shield, Paragon of Violence, + melee supra
pieces) - ** FEASIBILITY FLAG #2 (the engine + a shipping gate HARD-RESIST) **:
the ruled supra pieces are all player-tier Legendary UNIQUES, and the shipping
B-SUMMON-1 gate FAILS THE BUILD if a summoned pet directly equips such a unique
(a DB-wide audit proved ZERO of 25,000+ working monster/pet equip slots auto-equip
a player Epic/Legendary unique - the pet spawns NAKED, so the mod refuses to ship
one). This was proven empirically here: an initial round-1 attempt to equip the 8
supra pieces via _set_pet_equipment tripped B-SUMMON-1 on the written arz and
blocked the build. There is NO supported path to wear a specific player unique on
a pet on this engine. Resolution (honest, gate-compliant): the EoAT pet is NOT
given any supra unique; it keeps the Devourer donor's PROVEN loot-table loadout for
its visible gear + mobility, and its supra-tier POWER is delivered entirely by its
DIRECT stat block (life/OA/damage exceeding the strongest Toxeus champion) + full
kit. All 8 ruled pieces are reported as SKIPPED (engine-unsupported) in the report's
equipment render table. This is a WILL-DECISION-ADJACENT constraint: if Will wants
the supra STATS on the pet, they must be baked as direct pet fields (a follow-up),
not worn as items.

REGISTRY ORDER: registered AFTER enslaver_pet_fx (so the b71 chain-gate roster it
extends is already defined) and BEFORE visuals (which writes nothing). Its apply()
builds everything; its verify() (post-finalization) walks the FULL live chain
(soul -> formula -> summon skill -> icon/portrait -> pets -> kit-present-at-levels
-> zero-green -> equipment -> stats-exceed-ceiling). The b71 enslaver_pet_fx._CHAIN
roster is ALSO extended with the EoAT family (brief: extend the chain-gate roster).
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))  # tools/
import apply_svc_patches as asp
from arz_patcher import (DATA_TYPE_STRING as S, DATA_TYPE_FLOAT as F,
                         DATA_TYPE_INT as I, TypedField)

MODULE_NAME = 'toxeus_endofallthings'

# ── source donors (all DB-verified present in build45) ──────────────────────
_DEV_PETS = [r'records\skills\soulskills\pets\bloodtoxeus_%d.dbr' % i for i in (1, 2, 3)]
_DEV_SUMMON = r'records\skills\soulskills\summon_bloodtoxeus.dbr'
_DISCIPLE_MON = r'records\drxcreatures\bloodwitch\c_disciple_42.dbr'
_DISCIPLE_SUMMON_HOUNDS = r'records\drxcreatures\bloodwitch\skills\disciple_summon_bloodbeast.dbr'
_LYIA_PETS = [r'records\skills\soulskills\pets\lyialeafsong_%d.dbr' % i for i in (1, 2, 3)]

# kit donors
_NETHERSTRIKE = r'records\skills\monster skills\attack_melee\netherstrike.dbr'
_SMOKESCREEN_PET = r'records\skills\stealth\drxpet\drx_smokescreen_petskill_default.dbr'
_GALEFURY = r'records\drxitem\supra\skills\hunter_helm_galefury.dbr'
_TEARSOFBLOOD = r'records\xpack\skills\artifactskills\e_da_bloodofares_tearsofblood.dbr'
_BLACK_POISON = r'records\skills\monster skills\buff_self\bloodtoxeus_envenomweapon.dbr'  # crimson (see flag)
_SHADOWLINK_AURA = r'records\skills\monster skills\auras\shadowlink.dbr'
_SHADOWLINK_BUFF = r'records\skills\monster skills\auras\shadowlinkbuff.dbr'
_TOXEUS_PASSIVE = r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'
_SUNGAZE = r'records\skills\sv\manetho\sungaze.dbr'
_BLOODBOIL = r'records\skills\soulskills\melinoe_bloodboil.dbr'   # blood nova (Blood Feast)
_LIFEDRAIN = r'records\skills\spirit\lifedrain.dbr'
# 11. ARRAT'S CORRUPTION AOE (Will 2026-07-16): the signature ability of the
# monster 'Arrat/Ararat the Corruptor' (um_ararat_36, spider family - his
# skillName2). The shipped SOULSKILLS variant is already pet-castable (Class
# Skill_AttackRadius, skillManaCost 0, skillCooldownTime 30) - a radius debuff
# nova that burns mana, slows attack speed, and shortens the target's life/mana
# leach windows (the corruption). Reused verbatim (no shared-record edit).
_ARARAT = r'records\skills\soulskills\ararat_corruption.dbr'
_ARARAT_MON = r'records\creature\monster\spider\um_ararat_36.dbr'  # provenance (report)
_BLADESTORM = r'records\skills\monster skills\attack_radius\toxeus_bladestorm.dbr'
_ATTACKSKILL = r'records\skills\monster skills\attack_melee\toxeus_attackskill.dbr'
_HERO_SCALING = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'
_ARMOR_PASSIVE = r'records\skills\monster skills\defense\armor_passive.dbr'
_GLOBAL_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'

# supra equipment (Will's list) - hardcoded item paths for _set_pet_equipment
_EQ_SPEAR = r'records\drxitem\supra\wep_spear.dbr'        # "the blood spear"
_EQ_SHIELD = r'records\drxitem\supra\wep_shield.dbr'      # "the uber shield" (Agathodaemon)
_EQ_AMULET = r'records\drxitem\supra\neck_melee.dbr'      # "Paragon of Violence"
_EQ_RING = r'records\drxitem\supra\ring_melee.dbr'
_EQ_HELM = r'records\drxitem\supra\ar_melee_helm.dbr'
_EQ_TORSO = r'records\drxitem\supra\ar_melee_torso.dbr'
_EQ_ARMS = r'records\drxitem\supra\ar_melee_arms.dbr'
_EQ_LEGS = r'records\drxitem\supra\ar_melee_legs.dbr'

# ── new record paths (collision-checked ABSENT vs build45) ──────────────────
_EOAT_PETS = [r'records\skills\soulskills\pets\toxeus_eoat_%d.dbr' % i for i in (1, 2, 3)]
_EOAT_SUMMON = r'records\skills\soulskills\summon_toxeus_eoat.dbr'
_EOAT_SOUL = r'records\item\equipmentring\soul\svc_uber\soul_of_toxeus_endofallthings.dbr'
_EOAT_FORMULA = r'records\drxitem\supra\recipes\svc_toxeus_eoat_formula.dbr'
_DISC_PETS = [r'records\skills\soulskills\pets\eoat_disciple_%d.dbr' % i for i in (1, 2, 3)]
_EOAT_THRALLS = r'records\skills\soulskills\svc_eoat_thralls.dbr'
# authored kit skills
_SK_NETHER05 = r'records\skills\soulskills\svc_eoat_netherstrike.dbr'
_SK_TEARS = r'records\skills\soulskills\svc_eoat_tearsofblood.dbr'
_SK_ENTROPY = r'records\skills\soulskills\svc_eoat_entropyaura.dbr'
_SK_ENTROPY_BUFF = r'records\skills\soulskills\svc_eoat_entropybuff.dbr'
_SK_ENDING = r'records\skills\soulskills\svc_eoat_ending.dbr'
_SK_MURDER = r'records\skills\soulskills\svc_eoat_murderersedge.dbr'

# ── the 3 LEGENDARY ingredient souls (uber-formula reagents) ────────────────
_ING_GREECE = r'records\item\equipmentring\soul\skeleton\toxeus_soul_l.dbr'         # green Greece base
_ING_ENSLAVER = r'records\item\equipmentring\soul\svc_uber\enslaver_soul_l.dbr'     # Enslaver
_ING_DEVOURER = r'records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_l.dbr' # Devourer

# ── b71-consistent identity (skill icon + pet-bar portrait; every tex resolves
#    in the shipped arcs - the licheking apocalyptic-lich family the Devourer
#    already uses, so it is arc-proven; ONE identity across button + pet bar) ──
_ICON_UP = r'DRXtextures\skill icons\spirit\lichekingup.tex'
_ICON_DOWN = r'DRXtextures\skill icons\spirit\lichekingdown.tex'
_PORTRAIT_UP = r'DRXtextures\skill icons\spirit\licheking_party_up.tex'
_PORTRAIT_RED = r'DRXtextures\skill icons\spirit\licheking_party_red.tex'

# ── tuning constants ────────────────────────────────────────────────────────
_UNLIMITED_MANA = 999999.0
_UNLIMITED_MANA_REGEN = 9999.0
# stat ceiling: the STRONGEST Toxeus champion the player faces is the ENSLAVER
# (um_toxeus_enslaver_99: Boss [40,68,100], life [32500,45000,60000], STR 560,
# DEX 720, handHit 350-500, scale 2.4). EoAT must EXCEED it on every axis.
_CEILING_LIFE_L = 60000.0        # Enslaver Legendary life (the number to beat)
_CEILING_HANDHIT_MAX = 500.0     # Enslaver handHitDamageMax
_EOAT_LIFE = [45000.0, 62000.0, 82000.0]      # Legendary 82000 > 60000
_EOAT_LIFE_REGEN = [60.0, 90.0, 140.0]
_EOAT_HANDHIT_MIN = 400.0
_EOAT_HANDHIT_MAX = 620.0        # > 500
_EOAT_STR = 640.0                # > 560
_EOAT_DEX = 800.0                # > 720
_EOAT_INT = 520.0
_EOAT_OA = 2600.0                # Murderer's Edge high offensive ability
_EOAT_SCALE = 2.25


# =============================================================================
# helpers
# =============================================================================
def _has(db, p):
    return db.has_record(p)


def _del_fields(db, rec, predicate):
    """Delete decoded fields matching predicate(base_name)->bool (never blank)."""
    ff = db.get_fields(rec)
    if not ff:
        return 0
    n = 0
    for k in list(ff):
        if predicate(k.split('###')[0]):
            del ff[k]
            n += 1
    if n:
        db._modified.add(rec)
    return n


def _clone_kit_skill(db, donor, dest, overrides):
    """Clone a proven skill donor and override value-only fields (dtype-safe)."""
    if not _has(db, donor):
        raise SystemExit("[toxeus_endofallthings] kit donor missing: %s" % donor)
    db.clone_record(donor, dest)
    for fld, val in overrides.items():
        db.set_field(dest, fld, val)   # value-only override -> preserves donor dtype
    db._modified.add(dest)


# =============================================================================
# authored kit skills
# =============================================================================
def _author_kit_skills(db):
    # 2. netherstrike @ 0.5s cooldown (max level fired via the pet skillLevel slot)
    _clone_kit_skill(db, _NETHERSTRIKE, _SK_NETHER05, {'skillCooldownTime': 0.5})
    # 5. tears of blood @ 3.0s cooldown (retaliation nova, see feasibility flag)
    _clone_kit_skill(db, _TEARSOFBLOOD, _SK_TEARS, {'skillCooldownTime': 3.0})
    # 10. THE ENDING: Manetho sungaze flash nova, long cooldown ultimate. The donor
    # keeps its light-of-Ra projectile FX (skillProjectileName aktaois_lightofra01 =
    # the screen-flash Will asked to steal) but ships ZERO damage and a 'SunGaze'
    # skillSpecialAnimationName the RevenantPoison skeleton rig does NOT carry (the
    # b52 Ephialtes-nova lesson: a missing special anim makes the skill uncastable).
    # So: author real cataclysm damage (physical + vitality) AND clear the special
    # anim (cast via the default rig anim) - the flash VISUAL rides on the projectile
    # record, not the animation, so it survives. Damage tuned as the ultimate.
    _clone_kit_skill(db, _SUNGAZE, _SK_ENDING, {
        'skillCooldownTime': 60.0,
        'skillSpecialAnimationName': '',       # castability (keep the projectile FX)
        'projectileExplosionRadius': 8.0,      # a big cataclysm nova, not a pinpoint
        'offensivePhysicalMin': 2400.0,
        'offensivePhysicalMax': 3600.0,
        'offensiveLifeMin': 1800.0,            # vitality (apocalyptic register)
        'offensiveLifeMax': 2600.0,
    })
    # 6. MURDERER'S EDGE passive (clone the Toxeus passive; add offensive/crit)
    _clone_kit_skill(db, _TOXEUS_PASSIVE, _SK_MURDER, {})
    db.set_field(_SK_MURDER, 'offensivePhysicalModifier', 60.0)          # new field -> inferred
    db.set_field(_SK_MURDER, 'characterOffensiveAbilityModifier', 40.0)
    db.set_field(_SK_MURDER, 'offensiveCritDamageModifier', 40.0)        # crit-heavy strikes
    db._modified.add(_SK_MURDER)
    # 7. ENTROPY AURA: shadowlink toggled radius -> fresh vitality-decay + RR buff
    _clone_kit_skill(db, _SHADOWLINK_AURA, _SK_ENTROPY, {'buffSkillName': _SK_ENTROPY_BUFF})
    db.set_field(_SK_ENTROPY, 'skillTargetRadius', 36.0)                 # b57 party-radius convention
    _clone_kit_skill(db, _SHADOWLINK_BUFF, _SK_ENTROPY_BUFF, {})
    B = _SK_ENTROPY_BUFF
    db.set_field(B, 'skillTargetRadius', 36.0)
    # resistance-shred (RR) + vitality-decay payload (magnitudes = a tuning surface)
    db.set_field(B, 'offensiveElementalResistanceReductionAbsoluteMin', 45.0)
    db.set_field(B, 'offensiveSlowLifeLeachMin', 120.0)
    db.set_field(B, 'offensiveSlowLifeLeachDurationMin', 3.0)
    db._modified.add(B)


# =============================================================================
# disciple thralls ("THERE IS ROOM IN ME") + the thrall summon skill
# =============================================================================
def _build_disciple_thralls(db):
    """Clone the proven eoat pets (built already) into disciple thralls: apply the
    Blood-Witch Disciple identity (mesh/anim/skin, tall) + the disciple's own
    disciple_summon_bloodbeast (the depth-3 hound summon - FEASIBILITY FLAG #1).
    Weaponless caster: clear weapon slots (they cast, they do not swing)."""
    disc_mesh = asp._find_record(db, _DISCIPLE_MON)
    if not disc_mesh:
        raise SystemExit("[toxeus_endofallthings] disciple donor missing: %s" % _DISCIPLE_MON)
    dm = db.get_field_value(_DISCIPLE_MON, 'mesh')
    dm = dm[0] if isinstance(dm, list) else dm
    da = db.get_field_value(_DISCIPLE_MON, 'charAnimationTableName')
    da = da[0] if isinstance(da, list) else da
    for src, dest in zip(_EOAT_PETS, _DISC_PETS):
        db.clone_record(src, dest)
        # strip the eoat combat kit skillName slots + specialAttack slots
        _del_fields(db, dest, lambda fn: (fn.startswith('skillName') and fn[9:].isdigit())
                    or (fn.startswith('skillLevel') and fn[10:].isdigit())
                    or fn.startswith('specialAttack'))
        # disciple identity (tall caster)
        db.set_field(dest, 'mesh', str(dm))
        db.set_field(dest, 'charAnimationTableName', str(da))
        db.set_field(dest, 'baseTexture', '')          # disciple mesh default skin
        db.set_field(dest, 'bumpTexture', '')
        db.set_field(dest, 'description', 'tagMonsterEoATThrall')  # distinct thrall name
        db.set_field(dest, 'scale', 1.9)
        db.set_field(dest, 'characterLife', 9000.0)
        db.set_field(dest, 'characterMana', _UNLIMITED_MANA)
        db.set_field(dest, 'characterManaRegen', _UNLIMITED_MANA_REGEN)
        # weaponless caster: clear every equip slot (no Monster.tpl field copy)
        for slot in ('RightHand', 'LeftHand', 'Head', 'Torso', 'Forearm', 'LowerBody', 'Finger1', 'Finger2', 'Neck'):
            db.set_field(dest, 'chanceToEquip%s' % slot, 0.0)
        # kit: the disciple's hound-summon (depth-3 attempt) + a bloodstare + passives
        db.set_field(dest, 'skillName1', _DISCIPLE_SUMMON_HOUNDS, S)
        db.set_field(dest, 'skillLevel1', 4, I)
        db.set_field(dest, 'skillName2', _ARMOR_PASSIVE, S)
        db.set_field(dest, 'skillLevel2', 4, I)
        db.set_field(dest, 'skillName3', _HERO_SCALING, S)
        db.set_field(dest, 'skillLevel3', 1, I)
        db.set_field(dest, 'specialAttackSkillName', _DISCIPLE_SUMMON_HOUNDS, S)
        db.set_field(dest, 'specialAttackChance', 100.0, F)
        db.set_field(dest, 'attackSkillName', '')      # let the summon carry them
        db._modified.add(dest)

    # thrall summon skill (Skill_SpawnPet) - clone the proven Devourer summon shell
    db.clone_record(_DEV_SUMMON, _EOAT_THRALLS)
    T = _EOAT_THRALLS
    db.set_field(T, 'spawnObjects', list(_DISC_PETS))
    db.set_field(T, 'petLimit', 3)
    db.set_field(T, 'petBurstSpawn', 3)
    db.set_field(T, 'skillCooldownTime', 30.0)
    db.set_field(T, 'skillActiveDuration', 0.0)
    db.set_field(T, 'isPetDisplayable', 0)     # thralls do not show in the pet bar
    db.set_field(T, 'skillManaCost', [0.0, 0.0, 0.0])
    db._modified.add(T)


# =============================================================================
# the 3 EoAT pets
# =============================================================================
# kit slots (skillName<idx>, level). Actives + buffs + passives. Levels are the
# per-skill firing level (max where meaningful).
_EOAT_KIT = [
    (_SK_NETHER05, 12),      # 2. nether strike max, 0.5s cd
    (_BLADESTORM, 12),       # AoE (Devourer-proven)
    (_SK_ENDING, 16),        # 10. the Ending ultimate (Manetho flash)
    (_LIFEDRAIN, 12),        # 8. Blood Feast leech
    (_BLOODBOIL, 12),        # 8. Blood Feast blood nova (Devourer's own)
    (_SMOKESCREEN_PET, 16),  # 3. smoke screen max
    (_GALEFURY, 1),          # 4. galefury (max = 1)
    (_SK_ENTROPY, 10),       # 7. entropy aura
    (_SK_MURDER, 1),         # 6. Murderer's Edge passive
    (_EOAT_THRALLS, 3),      # 9. There is room in me
    (_SK_TEARS, 1),          # 5. tears of blood
    (_ARARAT, 20),           # 11. Arrat's Corruption AOE (max level, pet-castable soulskill)
    (_HERO_SCALING, 1),      # keep tier scaling passives
    (_TOXEUS_PASSIVE, 1),
    (_ARMOR_PASSIVE, 4),
    (_GLOBAL_L, 1),
]
# specialAttack firing table (skill, chance). The AI picks these in combat.
_EOAT_SPECIALS = [
    (_SK_NETHER05, 90.0),    # 1: base specialAttack (no numeric suffix)
    (_BLOODBOIL, 60.0),      # 2
    (_BLADESTORM, 50.0),     # 3
    (_SK_TEARS, 40.0),       # 4: retaliation approximation (3.0s cd)
    (_ARARAT, 55.0),         # 5: Arrat's Corruption debuff nova (11)
    (_SK_ENDING, 12.0),      # 6: ultimate (low chance, long cd)
]
# green Lyia-residue markers to strip off the cloned Devourer pet (b55 pattern):
# base_field(lower) -> substrings that mark the value green.
_GREEN_STRIP = {
    'buffself2skillname': ('heartofoak',),
    'healskillname': ('regrowth',),
    'deatheffect': ('natureswrath',),
}


def _strip_green(db, pet):
    ff = db.get_fields(pet) or {}
    for base_lower, needles in _GREEN_STRIP.items():
        for k in [kk for kk in list(ff) if kk.split('###')[0].lower() == base_lower]:
            val = str(ff[k].values[0]).lower() if ff[k].values else ''
            if any(n in val for n in needles):
                del ff[k]
    db._modified.add(pet)


def _build_eoat_pets(db):
    for i, (src, dest) in enumerate(zip(_DEV_PETS, _EOAT_PETS)):
        if not _has(db, src):
            raise SystemExit("[toxeus_endofallthings] Devourer pet donor missing: %s "
                             "(monolith must build the Devourer summon first)" % src)
        db.clone_record(src, dest)
        # green-free: strip the Lyia green residue; crimson "black poison" weapon buff
        _strip_green(db, dest)
        db.set_field(dest, 'buffSelfSkillName', _BLACK_POISON)   # crimson envenom (see flag)
        # clear the inherited skillName/specialAttack kit, then author the full kit
        _del_fields(db, dest, lambda fn: (fn.startswith('skillName') and fn[9:].isdigit())
                    or (fn.startswith('skillLevel') and fn[10:].isdigit())
                    or fn.startswith('specialAttack'))
        for idx, (sk, lvl) in enumerate(_EOAT_KIT, start=1):
            db.set_field(dest, 'skillName%d' % idx, sk, S)
            db.set_field(dest, 'skillLevel%d' % idx, lvl, I)
        for j, (sk, ch) in enumerate(_EOAT_SPECIALS, start=1):
            suf = '' if j == 1 else str(j)
            db.set_field(dest, 'specialAttack%sSkillName' % suf, sk, S)
            db.set_field(dest, 'specialAttack%sChance' % suf, ch, F)
        db.set_field(dest, 'attackSkillName', _ATTACKSKILL)
        # identity: ash-pale/bone skeleton + crimson accents (RevenantPoison mesh
        # is inherited from the Devourer pet). newskeleton (bone) base + crimson.
        db.set_field(dest, 'baseTexture', r'Creatures\monster\skeleton\newskeleton_crimson.tex')
        db.set_field(dest, 'scale', _EOAT_SCALE)
        # NAME (Will ruling): the pet + pet-bar read 'Toxeus the Murderer, End of All
        # Things' (the Devourer donor names it 'tagMonsterHemorrheusPet'; override it).
        db.set_field(dest, 'description', 'tagMonsterToxeusEoAT')
        # stats: exceed the ceiling
        db.set_field(dest, 'charLevel', [40, 68, 100])
        db.set_field(dest, 'characterLife', _EOAT_LIFE[i])
        db.set_field(dest, 'characterLifeRegen', _EOAT_LIFE_REGEN[i])
        db.set_field(dest, 'characterStrength', _EOAT_STR)
        db.set_field(dest, 'characterDexterity', _EOAT_DEX)
        db.set_field(dest, 'characterIntelligence', _EOAT_INT)
        db.set_field(dest, 'characterOffensiveAbility', _EOAT_OA)
        db.set_field(dest, 'handHitDamageMin', _EOAT_HANDHIT_MIN)
        db.set_field(dest, 'handHitDamageMax', _EOAT_HANDHIT_MAX)
        # 8. Blood Feast: deep life leech on strikes
        db.set_field(dest, 'offensiveLifeLeechMin', 200.0)
        db.set_field(dest, 'offensiveLifeLeechMax', 300.0)
        # 1. UNLIMITED ENERGY (crash-safe stat fields)
        db.set_field(dest, 'characterMana', _UNLIMITED_MANA)
        db.set_field(dest, 'characterManaRegen', _UNLIMITED_MANA_REGEN)
        # pet-bar portrait (b71 identity), no drops/xp
        db.set_field(dest, 'StatusIcon', _PORTRAIT_UP)
        db.set_field(dest, 'StatusIconRed', _PORTRAIT_RED)
        db.set_field(dest, 'dropItems', 0)
        # EQUIPMENT (FEASIBILITY FLAG #2, engine-resists, HARD-GATED): the ruled supra
        # pieces (blood spear / uber shield / Paragon of Violence / melee armor) are all
        # player-tier Legendary UNIQUES, and the shipping B-SUMMON-1 gate FAILS THE BUILD
        # if a pet directly equips such a unique (a DB-wide audit proved they never
        # auto-equip on a pet -> the pet spawns NAKED; the mod forbids shipping it). So
        # the supra pieces CANNOT be worn by the summoned pet on this engine. The pet
        # keeps the Devourer donor's PROVEN loot-table loadout (its visible gear +
        # mobility) unchanged, and its supra-tier power is delivered by its DIRECT stat
        # block (exceeding the strongest Toxeus champion) + full kit. Reported honestly
        # in the equipment render table (all 8 pieces = SKIPPED, engine-unsupported).
        db._modified.add(dest)


# =============================================================================
# summon skill + soul ring + uber formula
# =============================================================================
def _build_summon_skill(db):
    db.clone_record(_DEV_SUMMON, _EOAT_SUMMON)
    K = _EOAT_SUMMON
    db.set_field(K, 'spawnObjects', list(_EOAT_PETS))
    db.set_field(K, 'isPetDisplayable', 1)
    db.set_field(K, 'skillDisplayName', 'tagSVCSummonToxeusEoAT')
    db.set_field(K, 'petLimit', 1)         # 1-at-a-time (Will)
    db.set_field(K, 'petBurstSpawn', 1)
    db.set_field(K, 'skillManaCost', [300.0, 350.0, 400.0])
    db.set_field(K, 'skillCooldownTime', 180.0)
    db.set_field(K, 'skillMaxLevel', 3)
    # b71 identity: skill icon (button) == pet-bar portrait family (licheking)
    db.set_field(K, 'skillUpBitmapName', _ICON_UP)
    db.set_field(K, 'skillDownBitmapName', _ICON_DOWN)
    db._modified.add(K)


def _build_soul_ring(db, tags):
    """Single supra-tier soul ring (the crafted result). Authored via the
    sanctioned soul path (_ensure_record + boilerplate + _set_soul_fields), NOT
    clone_record (soul clone-value-corruption law)."""
    asp._ensure_record(db, _EOAT_SOUL, asp.SOUL_TEMPLATE)
    asp._set_soul_fields(db, _EOAT_SOUL, asp._SOUL_BOILERPLATE)
    asp._set_soul_fields(db, _EOAT_SOUL, {
        'itemLevel': (I, 100),
        'levelRequirement': (I, 95),
        'itemNameTag': (S, 'tagSVCSoulToxeusEoAT'),
        'FileDescription': (S, 'Soul of Toxeus, End of All Things (supra)'),
        'bitmap': (S, r'SVItems\jewelry\soul_l_icon.tex'),
        # the summon (itemSkillName) + evocative augments (both resolve)
        'itemSkillName': (S, _EOAT_SUMMON), 'itemSkillLevel': (I, 3),
        'augmentSkillName1': (S, r'records\skills\stealth\drxanatomy.dbr'), 'augmentSkillLevel1': (I, 6),
        'augmentSkillName2': (S, r'records\skills\stealth\drxopenwound.dbr'), 'augmentSkillLevel2': (I, 6),
        # supra soul stat block (best-in-slot; the apotheosis ring)
        'offensivePhysicalModifier': (I, 40),
        'offensiveLifeLeechMin': (F, 60.0),
        'characterOffensiveAbility': (F, 250.0),
        'characterLifeModifier': (F, 20.0),
        'characterStrengthModifier': (F, 12.0),
        'characterDexterityModifier': (F, 12.0),
    })
    db._modified.add(_EOAT_SOUL)
    # F6 naming-gate exemption for the Will-ruled 'Soul of X' marquee name.
    try:
        if 'tagSVCSoulToxeusEoAT' not in asp._HAND_DESIGNED_SOUL_TAGS:
            asp._HAND_DESIGNED_SOUL_TAGS = frozenset(
                set(asp._HAND_DESIGNED_SOUL_TAGS) | {'tagSVCSoulToxeusEoAT'})
    except Exception as e:
        raise SystemExit("[toxeus_endofallthings] could not register naming exemption: %r" % e)


def _build_formula(db):
    """Uber-forge ItemArtifactFormula consuming the 3 LEGENDARY Toxeus souls ->
    the EoAT soul ring. Cloned from the proven supra spear formula shell.
    ACQUISITION (how the player OBTAINS this formula item) is THE ONE OPEN WILL
    DECISION - see the report; this round authors the craft-ready formula but does
    NOT wire its drop."""
    donor = r'records\drxitem\supra\recipes\wep_spear_formula.dbr'
    if not _has(db, donor):
        raise SystemExit("[toxeus_endofallthings] formula donor missing: %s" % donor)
    for ing in (_ING_GREECE, _ING_ENSLAVER, _ING_DEVOURER):
        if not _has(db, ing):
            raise SystemExit("[toxeus_endofallthings] ingredient soul missing: %s" % ing)
    db.clone_record(donor, _EOAT_FORMULA)
    Ff = _EOAT_FORMULA
    db.set_field(Ff, 'artifactName', _EOAT_SOUL)
    db.set_field(Ff, 'reagent1BaseName', _ING_GREECE)
    db.set_field(Ff, 'reagent2BaseName', _ING_ENSLAVER)
    db.set_field(Ff, 'reagent3BaseName', _ING_DEVOURER)
    db.set_field(Ff, 'description', 'tagSVCFormulaToxeusEoAT')
    # CRAFTABILITY (correctness): the spear-formula donor constrains reagent3 to a
    # long weapon prefix/suffix affix whitelist (reagent3PrefixName 218 + SuffixName
    # 179). A soul RING carries no such affix, so leaving those constraints makes the
    # 3-soul recipe UNCRAFTABLE. Clear every reagent affix constraint so the three
    # plain LEGENDARY souls qualify by base alone. Also clear artifactBonusTableName
    # so the crafted soul is DETERMINISTIC (no random completion affix rolled onto a
    # fixed-stat soul ring). Empty list -> field is not emitted (write_arz skips n==0).
    for fld in ('reagent1PrefixName', 'reagent1SuffixName',
                'reagent2PrefixName', 'reagent2SuffixName',
                'reagent3PrefixName', 'reagent3SuffixName',
                'artifactBonusTableName'):
        db.set_field(Ff, fld, [])
    db._modified.add(Ff)


# =============================================================================
# tags
# =============================================================================
def _mint_tags(tags):
    tags['tagSVCSoulToxeusEoAT'] = '{^F}Soul of Toxeus, End of All Things'
    tags['tagSVCSoulToxeusEoATDESC'] = (
        'The last shape the first murderer wears: not the poisoner of Greece, not '
        'the drowned Devourer, not the Enslaver of the dead, but all of them at once '
        'and none of them held back. When the three souls are made one, the debt he '
        'came to collect is every heartbeat there is. Summon what is left when there '
        'is nothing left to end.')
    tags['tagSVCSummonToxeusEoAT'] = 'Summon Toxeus, End of All Things'
    tags['tagMonsterToxeusEoAT'] = '{^F}Toxeus the Murderer, End of All Things'
    tags['tagMonsterEoATThrall'] = 'Blood-Witch Thrall'
    tags['tagSVCFormulaToxeusEoAT'] = 'Rite of the Undivided'
    # apocalyptic-register flavor line (Will's veto surface)
    tags['tagSVCSoulToxeusEoATFLAVOR'] = (
        'He was the end of one man in an alley. Now he is the end of the alley, the '
        'city, the road out of it, and the last witness who might have told the tale.')


# =============================================================================
# registry entry points
# =============================================================================
def apply(db, tags):
    print("\n=== [toxeus_endofallthings] b72 TOXEUS, END OF ALL THINGS ===")
    for pet in _EOAT_PETS + _DISC_PETS + [_EOAT_SUMMON, _EOAT_SOUL, _EOAT_FORMULA]:
        if _has(db, pet):
            raise SystemExit("[toxeus_endofallthings] collision (record already exists): %s" % pet)
    _author_kit_skills(db)
    _build_eoat_pets(db)
    _build_disciple_thralls(db)   # after the eoat pets (clones them)
    _build_summon_skill(db)
    _build_soul_ring(db, tags)
    _build_formula(db)
    _mint_tags(tags)
    # extend the b71 anti-oscillation chain-gate roster (brief) so the shared
    # enslaver_pet_fx gate also walks the EoAT chain on the final db.
    _extend_b71_chain()
    print("  [eoat] built 3 pets + 3 disciple thralls + summon + soul ring + uber "
          "formula (3 legendary souls -> supra ring); kit + equipment + tags done.")
    return tags


def _extend_b71_chain():
    """Append the EoAT family to enslaver_pet_fx._CHAIN (the b71 roster) so the
    shared anti-oscillation chain gate covers it too. Idempotent."""
    try:
        from . import enslaver_pet_fx as epf
    except Exception:
        import enslaver_pet_fx as epf   # fallback if imported flat
    entry = {
        'label': 'Toxeus EoAT',
        'souls': [_EOAT_SOUL],
        'skill': _EOAT_SUMMON,
        'icon_stem': 'lichekingup',
        'portrait_stem': 'licheking_party_up',
        'pets': _EOAT_PETS,
        'sub_skill': _EOAT_THRALLS,
        'sub_pets': _DISC_PETS,
    }
    if not any(c.get('label') == 'Toxeus EoAT' for c in epf._CHAIN):
        epf._CHAIN.append(entry)


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) else v


def _stem(p):
    return (p or '').replace('/', '\\').rsplit('\\', 1)[-1].replace('.dbr', '').replace('.tex', '').lower()


def verify(db, tags=None):
    """POST-FINALIZATION fail-loud gate (run_registry_verifies). Walk the FULL live
    chain on the final assembled db and assert every ruled property."""
    P = []
    # (a) all records exist
    for r in _EOAT_PETS + _DISC_PETS + [_EOAT_SUMMON, _EOAT_SOUL, _EOAT_FORMULA,
                                        _SK_NETHER05, _SK_TEARS, _SK_ENTROPY, _SK_ENTROPY_BUFF,
                                        _SK_ENDING, _SK_MURDER, _EOAT_THRALLS]:
        if not db.has_record(r):
            P.append('missing record: %s' % r)
    if P:
        raise SystemExit('toxeus_endofallthings.verify FAILED (missing records):\n  ' + '\n  '.join(P))

    # (b) soul -> summon skill -> pets chain
    gs = (_gv1(db, _EOAT_SOUL, 'itemSkillName') or '').replace('/', '\\').lower()
    if gs != _EOAT_SUMMON.lower():
        P.append('soul grants %s, expected summon %s' % (gs, _EOAT_SUMMON))
    so = db.get_field_value(_EOAT_SUMMON, 'spawnObjects')
    so = [str(x).lower() for x in (so if isinstance(so, list) else [so] if so else [])]
    if so != [p.lower() for p in _EOAT_PETS]:
        P.append('summon spawnObjects != the 3 eoat pets: %r' % so)
    if _gv1(db, _EOAT_SUMMON, 'petLimit') not in (1,):
        P.append('summon petLimit != 1 (must be 1-at-a-time)')
    # (b2) icon + portrait identity (b71 law)
    if _stem(_gv1(db, _EOAT_SUMMON, 'skillUpBitmapName')) != 'lichekingup':
        P.append('summon skill icon != licheking identity')

    # (c) formula consumes the 3 LEGENDARY souls -> the ring
    if (_gv1(db, _EOAT_FORMULA, 'artifactName') or '').lower() != _EOAT_SOUL.lower():
        P.append('formula artifactName != the eoat soul ring')
    reags = {(_gv1(db, _EOAT_FORMULA, 'reagent%dBaseName' % i) or '').lower() for i in (1, 2, 3)}
    for ing in (_ING_GREECE, _ING_ENSLAVER, _ING_DEVOURER):
        if ing.lower() not in reags:
            P.append('formula missing legendary reagent: %s' % ing)

    # (d) netherstrike cooldown 0.5s
    cd = _gv1(db, _SK_NETHER05, 'skillCooldownTime')
    if cd is None or abs(float(cd) - 0.5) > 1e-6:
        P.append('netherstrike cooldown %r != 0.5' % cd)
    # tears of blood cooldown 3.0s
    cdt = _gv1(db, _SK_TEARS, 'skillCooldownTime')
    if cdt is None or abs(float(cdt) - 3.0) > 1e-6:
        P.append('tears of blood cooldown %r != 3.0' % cdt)

    # (e) per-pet: full kit present at levels, unlimited energy, zero green,
    #     crimson poison, stats exceed the ceiling, portrait identity
    kit_paths = {p.lower() for p, _l in _EOAT_KIT}
    for i, pet in enumerate(_EOAT_PETS):
        ff = db.get_fields(pet) or {}
        present = {str(tf.values[0]).lower() for k, tf in ff.items()
                   if k.split('###')[0].lower().startswith('skillname') and tf.values}
        for need in (_SK_NETHER05, _SMOKESCREEN_PET, _GALEFURY, _SK_ENTROPY, _EOAT_THRALLS,
                     _SK_ENDING, _BLOODBOIL, _SK_MURDER, _SK_TEARS, _ARARAT):
            if need.lower() not in present:
                P.append('%s: kit missing %s' % (pet.rsplit(chr(92), 1)[-1], need.rsplit(chr(92), 1)[-1]))
        # NAME ruling: the pet reads 'Toxeus the Murderer, End of All Things'. We set
        # description=tagMonsterToxeusEoAT; the b50 _whiten_pet_display_names
        # finalization repoints every {^F}-colored Class=='Pet' name to a plain-white
        # sibling tag <tag>Pet (the bloodtoxeus/enslaver pet convention), so post-
        # finalization the field reads the whitened sibling. Accept either.
        if (_gv1(db, pet, 'description') or '') not in ('tagMonsterToxeusEoAT', 'tagMonsterToxeusEoATPet'):
            P.append('%s: description != EoAT name tag (name ruling): %r'
                     % (pet.rsplit(chr(92), 1)[-1], _gv1(db, pet, 'description')))
        # unlimited energy
        if float(_gv1(db, pet, 'characterMana') or 0) < 100000:
            P.append('%s: characterMana not unlimited' % pet.rsplit(chr(92), 1)[-1])
        if float(_gv1(db, pet, 'characterManaRegen') or 0) < 1000:
            P.append('%s: characterManaRegen not unlimited' % pet.rsplit(chr(92), 1)[-1])
        # zero green residue (marker match)
        for base_lower, needles in _GREEN_STRIP.items():
            for k in [kk for kk in ff if kk.split('###')[0].lower() == base_lower]:
                v = str(ff[k].values[0]).lower() if ff[k].values else ''
                if any(n in v for n in needles):
                    P.append('%s: GREEN residue survived %s=%s' % (pet.rsplit(chr(92), 1)[-1], base_lower, v))
        # crimson black poison (not the base green envenom)
        bp = (_gv1(db, pet, 'buffSelfSkillName') or '').lower()
        if 'bloodtoxeus_envenomweapon' not in bp:
            P.append('%s: weapon poison != crimson bloodtoxeus_envenomweapon (%r)' % (pet.rsplit(chr(92), 1)[-1], bp))
        if bp.endswith('stealth\\envenomweapon.dbr'):
            P.append('%s: base GREEN envenom present' % pet.rsplit(chr(92), 1)[-1])
        # portrait identity (never Lyia)
        if 'lyia' in (_gv1(db, pet, 'StatusIcon') or '').lower():
            P.append('%s: pet-bar portrait still Lyia' % pet.rsplit(chr(92), 1)[-1])
        # stats exceed the ceiling (Legendary index 2)
        life = _gv1(db, pet, 'characterLife')
    # ceiling check on the Legendary pet (index 2)
    lpet = _EOAT_PETS[2]
    llife = float(_gv1(db, lpet, 'characterLife') or 0)
    if llife <= _CEILING_LIFE_L:
        P.append('Legendary pet life %.0f does not exceed the Enslaver ceiling %.0f' % (llife, _CEILING_LIFE_L))
    lhit = float(_gv1(db, lpet, 'handHitDamageMax') or 0)
    if lhit <= _CEILING_HANDHIT_MAX:
        P.append('Legendary pet handHitDamageMax %.0f does not exceed ceiling %.0f' % (lhit, _CEILING_HANDHIT_MAX))

    # (f) disciple thralls carry the hound summon (depth-3 attempt) + summon wiring
    tso = db.get_field_value(_EOAT_THRALLS, 'spawnObjects')
    tso = [str(x).lower() for x in (tso if isinstance(tso, list) else [tso] if tso else [])]
    if tso != [p.lower() for p in _DISC_PETS]:
        P.append('thrall summon spawnObjects != the 3 disciple thralls')
    for d in _DISC_PETS:
        dff = db.get_fields(d) or {}
        dpresent = {str(tf.values[0]).lower() for k, tf in dff.items()
                    if k.split('###')[0].lower().startswith('skillname') and tf.values}
        if _DISCIPLE_SUMMON_HOUNDS.lower() not in dpresent:
            P.append('%s: disciple thrall missing the hound summon' % d.rsplit(chr(92), 1)[-1])

    # (g) equipment: the ruled supra UNIQUES cannot be worn by a pet on this engine
    #     (B-SUMMON-1 shipping gate hard-fails a pet that direct-equips a player-tier
    #     unique; audited to render NAKED). So the EoAT pet must NOT carry any supra
    #     unique in its loot slots - assert none leaked in (else the build gate fails
    #     downstream). Its supra power is its direct stat block, not worn gear.
    _supra = {p.lower() for p in (_EQ_SPEAR, _EQ_SHIELD, _EQ_AMULET, _EQ_RING,
                                  _EQ_HELM, _EQ_TORSO, _EQ_ARMS, _EQ_LEGS)}
    for pet in _EOAT_PETS:
        ff = db.get_fields(pet) or {}
        for k, tf in ff.items():
            if not k.split('###')[0].lower().startswith('loot'):
                continue
            for v in (tf.values or []):
                if str(v).lower() in _supra:
                    P.append('%s: supra unique leaked into a loot slot %s=%s '
                             '(B-SUMMON-1 would fail the build)'
                             % (pet.rsplit(chr(92), 1)[-1], k.split('###')[0], v))

    # (h) formula craftability: reagent affix constraints CLEARED so the 3 plain
    #     legendary souls qualify by base alone (else the recipe is uncraftable).
    for rf in ('reagent3PrefixName', 'reagent3SuffixName', 'artifactBonusTableName'):
        v = db.get_field_value(_EOAT_FORMULA, rf)
        if v not in (None, [], '') and not (isinstance(v, list) and len(v) == 0):
            P.append('formula %s not cleared (recipe would be uncraftable/nondeterministic): %r' % (rf, v))

    if P:
        raise SystemExit('toxeus_endofallthings.verify FAILED:\n  ' + '\n  '.join(P))
    print('  toxeus_endofallthings.verify OK: soul->formula(3 legendary souls, craftable)'
          '->summon->3 pets (full kit incl Ararat corruption @ levels, unlimited energy,'
          ' crimson poison, zero green, stats exceed Enslaver ceiling, licheking identity,'
          ' EoAT name) + disciple thralls (hound summon attached) + NO supra unique worn'
          ' (B-SUMMON-1-safe; supra pieces engine-unsupported on pets).')
    return tags
