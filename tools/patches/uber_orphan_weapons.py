"""uber_orphan_weapons - B66 UBER FORMULA EXPANSION (round 2).

ROUND 2 (independent adversarial vet, commit d754359): fixes the vet's one HIGH +
one MEDIUM + three LOW/nit findings. (1) HIGH - Ten Suns' Wrath (Di Jun's Pride)
was ~2.3x its only bow sibling (Stormbringer, 145-160 phys) and the single
highest raw-damage weapon in the entire supra tier, contradicting the report's
"none exceed the strongest sibling" claim; RETUNED to the sibling's own band
(145-160 phys, modest flat pierce, fire raised to lean into the sun-god
identity) rather than waiting on a live design call, since it is a straight
band-compliance fix with no loss of identity. (2) MEDIUM - donor fields were
copied verbatim then overridden WITHOUT clearing inherited combat stats (unlike
the N5 template this cites), so a grab-bag of the orphan's original riders
(negative characterLifeRegen, stray characterStrength/OA, an undocumented
total-speed slow, etc) bled through; fixed via `_clear_inherited_combat_stats`
(same offensive*/retaliation*/character* prefix wipe N5 uses), run right after
build and before `_apply_overrides` on all 14. Two riders (Aquimae, The
Furies) that legitimately depended on an inherited `offensiveGlobalChance` now
set it explicitly. (3) LOW - the "verbatim" donor JSON snapshot for Di Jun's
Pride actually differed from the real base record on 3 fields (a retheme +
a zeroed modifier + an extra field); the JSON is now genuinely verbatim and the
intentional sun-projectile retheme is an explicit, documented override instead.
(4) LOW - Heartpierce/Ripulsar trimmed to the documented supra sword max (160).
(5) LOW/nit - Munderizer/Sword Fish hidePrefixName/hideSuffixName aligned to 1
(matches the other 12; no reason for a fixed-name Legendary to differ).

Buffs 14 curated ORPHANED weapon records (docs/reports/orphaned_weapons_curation.md)
to the DRX "supra" uber-forge tier, cloning the proven `svc_thrown_*` template
(N5, apply_svc_patches.py `_add_supra_thrown_weapons`) that SVC already used to
add 3 thrown ubers. Every result KEEPS its orphan's mesh/skin/icon (no new art -
Will's efficiency law) and, where the orphan already grants an identity skill/
proc (Helona's summon, Phoenix's Heat Shield, the DRX eggs' augments), that skill
is PRESERVED verbatim on the supra result. Naming follows the amgoz1 design-voice
bar (monster/myth-identity-driven, never generic filler) - see
docs/reports/b66_uber_formulas.md WILL VETO section for every naming call.
NOTE: `amgoz1_design_voice.md` (cited by the 2026-07-11 standing directive) is
NOT present anywhere in this repo as of this wave; names below follow the voice
as documented in CLAUDE.md/BACKLOG.md ("monster-identity-driven, flavorful,
never generic filler") pending that file's creation - flagged in the report.

SOURCE OF EACH ORPHAN (verified via a fresh read of build41 baseline
work/SoulvizierClassic/Database/SoulvizierClassic.arz, eb8bc377, cross-checked
against upstream/soulvizier_098i|0.9|041 and the base game database.arz):
  - 11 orphans are SV/DRX-AUTHORED and already present in `db` at registry time
    (Ripulsar, Aquimae, Helona, Phoenix, Erysichthon's Hunger, Scylla, Charybdis,
    The Furies, Heartpierce, Doom Herald, The Munderizer) -> handled via
    `db.clone_record(orphan_path, dest_path)` (gets every rendering-critical
    field - bumpTexture/castsShadows/actorRadius/etc - verbatim, zero risk of a
    missed field), then targeted `set_field` overrides for the supra buff.
  - 3 orphans are BASE-GAME-ONLY (Hati, Sword Fish, Di Jun's Pride) and are NOT
    reachable from a registry module's `db` (base_db is loaded+freed entirely
    inside `_run_prefix`, long before `run_registry` runs - see
    tools/build_svc_database.py `_run_prefix`/`del base_db`). Their COMPLETE
    field sets (628/624/631 fields, captured read-only from the live base
    database.arz) are bundled as literal data at
    tools/patches/data/b66_orphan_donor_fields.json and reconstructed here via
    `_ensure_record` + `set_field` per field - the same "copy every donor field
    verbatim, then override the identity stats" shape N5 used for base_db.

FORMULA SHELLS: 7 of the 14 reuse an existing orphaned `zrecipes\\*_formula.dbr`
duplicate (repointed IN PLACE - artifactName/reagents/description/cost only;
the live `recipes\\*_formula.dbr` twin is untouched and keeps crafting its
original result). The other 7 classes had no spare shell (5 axes need 5 shells,
only 1 existed; thrown needs 1, zero spare beyond the 3 already-wired svc_thrown_*)
so those are freshly authored at `records\\drxitem\\supra\\zrecipes\\svc_<class>_
<name>_formula.dbr` via `db.clone_record` from a LIVE recipes\\ formula of the
same class (gets the full formula schema - bitmap/sounds/bonus table - verbatim).
All 14 are wired into BOTH `supra.dbr` and `supra_special.dbr` at the next free
lootName slot, weight 100 (matches the 3 svc_thrown_* precedent exactly).

Reagents: 2 Legendary + 1 Rare per weapon (1 Legendary + 1 Epic + 1 Rare for the
thrown pick, matching the "3-thrown-style exception" the backlog explicitly
allows), drawn from the SAME already-proven-resolving reagent pool the 13
existing supra formulas use for that weapon class (guarantees resolution; TQ's
own crafting economy commonly reuses popular class reagents across a themed
family - documented per-candidate in the report, not a mistake).
"""
import json
from pathlib import Path

from apply_svc_patches import _ensure_record

MODULE_NAME = "B66: 14 orphan weapons -> supra uber tier"

_DONOR_JSON = Path(__file__).parent / 'data' / 'b66_orphan_donor_fields.json'
_DONOR_FIELDS = json.loads(_DONOR_JSON.read_text(encoding='utf-8'))

_COST = r'records\game\itemcost_uniquelegendary_primary.dbr'
_SUPRA_TABLE = r'records\xpack\item\loottables\arcaneformulae\supra.dbr'
_SUPRA_SPECIAL = r'records\xpack\item\loottables\arcaneformulae\supra_special.dbr'

# Existing DRX trail assets (reused, not authored) - one per weapon class.
_TRAIL_SWORD = r'records\drxeffects\item\trail_wep_dagger.dbr'
_TRAIL_AXE = r'records\drxeffects\item\trail_wep_axe.dbr'
_TRAIL_MACE = r'records\drxeffects\item\trail_wep_club.dbr'
_TRAIL_STAFF = r'Records\Effects\weapontrail\Default_Staff.dbr'
_TRAIL_THROWN = r'records\drxeffects\item\trail_wep_dagger.dbr'
# Bow supras (Stormbringer) carry NO weaponTrail field at all in this DB (bows
# have no melee swing trail) - Ten Suns' Wrath follows that precedent (None).

# Reagent pool per class, drawn verbatim from the 13 already-obtainable supra
# formulas (proven to resolve; see docs/reports/b66_uber_formulas.md sec 2).
_REAGENTS_SWORD_A = (
    r'records\item\equipmentweapon\sword\u_l_mindrazor.dbr',           # Mindrazor (L)
    r'records\item\equipmentweapon\sword\u_e_griefmaker.dbr',          # Griefmaker (L, base-tier "e" prefix, live-reagent Legendary)
    r'records\item\equipmentweapon\sword\mi_l_tigermanmelee.dbr',      # Sabertooth (R)
)
_REAGENTS_SWORD_B = (
    r'records\item\equipmentweapon\sword\u_l_stymphaliantalon.dbr',   # Stymphalian Talon (L)
    r'records\xpack\item\equipmentweapons\sword\u_e_001.dbr',         # Plissken (L)
    r'records\item\equipmentweapon\sword\mi_l_arachnos.dbr',          # Deathweaver's Legtip (R)
)
_REAGENTS_AXE = (
    r'records\xpack\item\equipmentweapons\axe\u_l_002.dbr',           # Pyrophoric Lop (L)
    r"records\item\equipmentweapon\axe\u_e_shai'tan.dbr",             # Shai'tan (L)
    r'records\item\equipmentweapon\axe\mi_l_dragonian.dbr',           # Head Hunter's Axe (R)
)
_REAGENTS_MACE = (
    r'records\item\equipmentweapon\club\u_l_saprosthecorrupter.dbr',  # Sapros the Corrupter (L)
    r"records\item\equipmentweapon\club\u_e_demeter'ssorrow.dbr",    # Demeter's Sorrow (L)
    r'records\drxcreatures\drxdishonorguard\equip\weapons\mi_l_gigantes2.dbr',  # Animus (R)
)
_REAGENTS_STAFF_A = (
    r'records\xpack\item\equipmentweapons\staff\u_l_001.dbr',         # Praxidikae (L)
    r'records\xpack\item\equipmentweapons\staff\u_l_002.dbr',         # Sakur-Aba (L)
    r'records\item\equipmentweapon\staff\mi_l_liche.dbr',             # Scepter of the Liche King (R)
)
_REAGENTS_STAFF_B = (
    r'records\item\equipmentweapon\staff\u_e_rodoftheancients.dbr',   # Rod of the Ancients (L)
    r'records\item\equipmentweapon\staff\u_l_riddleofthesphinx.dbr',  # Riddle of the Sphinx (L)
    r'records\item\equipmentweapon\staff\mi_l_satyrmage.dbr',         # Staff of the Magi (R)
)
_REAGENTS_THROWN = (
    r'records\xpack2\item\equipmentweapons\1hranged\u_l_08.dbr',      # Touch of Nyx (L)
    r'records\xpack2\item\equipmentweapons\1hranged\u_e_06.dbr',      # The Crow (Epic)
    r'records\xpack2\item\equipmentweapons\1hranged\mi_l_machae.dbr', # Demonic Rippers (R)
)
_REAGENTS_BOW = (
    r"records\item\equipmentweapon\bow\u_l_helios'fury.dbr",         # Helios' Fury (L) - literal sun god, perfect match
    r'records\item\equipmentweapon\bow\u_e_khamsin.dbr',              # Khamsin (L)
    r'records\item\equipmentweapon\bow\mi_l_satyrbrigand.dbr',        # Brigand's Bow (R)
)

_SUPRA_PATH = lambda n: r'records\drxitem\supra\svc_wep_' + n + '.dbr'

# ── the 14 candidates ────────────────────────────────────────────────────────
# clone_from : orphan path already present in `db` (SV/DRX-authored) -> use
#              db.clone_record(). donor_key: key into _DONOR_FIELDS (base-game-
#              only orphan, reconstructed from the bundled JSON). Exactly one
#              of the two is set per entry.
_WEAPONS = [
    dict(
        key='ripulsar', name='Ripulsar',
        clone_from=r'records\item\equipmentweapon\sword\u_n_ripulsar.dbr',
        donor_key=None,
        result=_SUPRA_PATH('ripulsar'),
        trail=_TRAIL_SWORD,
        shell=r'records\drxitem\supra\zrecipes\wep_sword_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_SWORD_A,
        tag='tagSVCwpnRipulsar', formula_tag='tagSVCRecipeRipulsar',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra sword: Ripulsar',
            'itemNameTag': 'tagSVCwpnRipulsar',
            # ROUND 2 (vet LOW): max trimmed 165->160 - the documented supra
            # sword ceiling (wep_sword.dbr, 135-160); was +3% over.
            'offensivePhysicalMin': 140.0, 'offensivePhysicalMax': 160.0,
            'offensivePhysicalModifier': 50.0, 'offensivePierceRatioMin': 25.0,
            'offensiveLifeLeechMin': 60.0, 'offensiveLifeLeechChance': 100.0,
            'offensiveSlowLightningMin': 80.0, 'offensiveSlowLightningModifier': 150.0,
            'offensiveSlowLightningModifierChance': 25.0, 'offensiveSlowLightningDurationMin': 3.0,
            'characterAttackSpeedModifier': 30.0, 'characterDexterity': 60.0,
            'characterOffensiveAbility': 80.0,
            # identity KEPT: Dream-mastery psionic-touch augment, raised 2->4.
            'augmentSkillName1': r'records\xpack\skills\dream\drxpsionictouch.dbr',
            'augmentSkillLevel1': 4,
        },
    ),
    dict(
        key='aquimae', name='Aquimae',
        clone_from=r'records\xpack\item\equipmentweapons\sword\u_n_aquimae.dbr',
        donor_key=None,
        result=_SUPRA_PATH('aquimae'),
        trail=_TRAIL_SWORD,
        shell=r'records\drxitem\supra\zrecipes\wep_dagger_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_SWORD_B,
        tag='tagSVCwpnAquimae', formula_tag='tagSVCRecipeAquimae',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra sword: Aquimae',
            'itemNameTag': 'tagSVCwpnAquimae',
            'offensivePhysicalMin': 135.0, 'offensivePhysicalMax': 160.0,
            'offensivePhysicalModifier': 50.0, 'offensivePierceRatioMin': 20.0,
            'offensiveSlowLifeLeachMin': 90.0, 'offensiveSlowLifeLeachDurationMin': 4.0,
            'offensiveSlowLifeLeachChance': 100.0, 'offensiveSlowLifeLeachGlobal': 1,
            'offensiveSlowLifeLeachXOR': 1,
            'offensiveSlowManaLeachMin': 90.0, 'offensiveSlowManaLeachDurationMin': 4.0,
            'offensiveSlowManaLeachChance': 100.0, 'offensiveSlowManaLeachGlobal': 1,
            'offensiveSlowManaLeachXOR': 1,
            # ROUND 2 (vet MEDIUM): the 2 Global-flagged riders above proc off
            # a shared offensiveGlobalChance - round 1 left this unset and
            # relied on the donor's inherited value (100, worked by
            # coincidence); now cleared+re-added explicitly (see
            # `_clear_inherited_combat_stats`).
            'offensiveGlobalChance': 100.0,
            'offensiveTotalResistanceReductionPercentMin': 20.0,
            'offensiveTotalResistanceReductionPercentDurationMin': 4.0,
            'characterDexterity': 55.0, 'characterLife': 150.0, 'characterMana': 150.0,
        },
    ),
    dict(
        key='heartpierce', name='The Unholy Heartpiercer',
        clone_from=r'records\drxitem\eggs\zzz_unholykatana.dbr',
        donor_key=None,
        result=_SUPRA_PATH('heartpierce'),
        trail=_TRAIL_SWORD,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_sword_heartpierce_formula.dbr',
        fresh_template=r'records\drxitem\supra\recipes\wep_sword_formula.dbr',
        reagents=(_REAGENTS_SWORD_A[0], _REAGENTS_SWORD_B[0], _REAGENTS_SWORD_A[2]),
        tag='tagSVCwpnHeartpierce', formula_tag='tagSVCRecipeHeartpierce',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra sword: The Unholy Heartpiercer (Heartpierce, ascended)',
            'itemNameTag': 'tagSVCwpnHeartpierce',
            # ROUND 2 (vet LOW): max trimmed 175->160 - the documented supra
            # sword ceiling (wep_sword.dbr, 135-160); was +9% over.
            'offensivePhysicalMin': 150.0, 'offensivePhysicalMax': 160.0,
            'offensivePhysicalModifier': 50.0,
            'offensivePierceMin': 40.0, 'offensivePierceMax': 60.0, 'offensivePierceRatioMin': 30.0,
            'offensivePercentCurrentLifeMin': 25.0, 'offensivePercentCurrentLifeGlobal': 1,
            'offensiveGlobalChance': 20.0,
            'offensiveSlowBleedingMin': 250.0, 'offensiveSlowBleedingMax': 300.0,
            'offensiveSlowBleedingDurationMin': 5.0, 'offensiveSlowBleedingGlobal': 1,
            'characterAttackSpeedModifier': 35.0, 'characterDexterity': 50.0,
            # identity KEPT: DRX anatomy augment, raised 1->3.
            'augmentSkillName1': r'records\skills\stealth\drxanatomy.dbr',
            'augmentSkillLevel1': 3,
        },
    ),
    dict(
        key='helona', name="Helona's Ascension",
        clone_from=r'records\xpack\item\equipmentweapons\staff\u_n_helona.dbr',
        donor_key=None,
        result=_SUPRA_PATH('helona'),
        trail=_TRAIL_STAFF,
        shell=r'records\drxitem\supra\zrecipes\staff_dream_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_STAFF_A,
        tag='tagSVCwpnHelona', formula_tag='tagSVCRecipeHelona',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': "B66 supra staff: Helona's Ascension (Helona, ascended)",
            'itemNameTag': 'tagSVCwpnHelona',
            'offensiveBaseColdMin': 70.0, 'offensiveBaseColdMax': 78.0,
            'offensiveColdModifier': 20.0, 'offensiveDisruptionMin': 4.0,
            'characterIntelligence': 90.0, 'characterManaRegen': 4.0, 'characterMana': 180.0,
            # identity KEPT: this is the whole point - grants Helona's own summon.
            'itemSkillName': r'records\skills\item skills\helona_summon.dbr',
        },
    ),
    dict(
        key='munderizer', name='The Munderizer',
        clone_from=r'records\drxitem\eggs\zzz_munderizer.dbr',
        donor_key=None,
        result=_SUPRA_PATH('munderizer'),
        trail=_TRAIL_STAFF,
        shell=r'records\drxitem\supra\zrecipes\staff_vit_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_STAFF_B,
        tag='tagSVCwpnMunderizer', formula_tag='tagSVCRecipeMunderizer',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1,
            # ROUND 2 (vet nit): aligned to 1/1 like the other 12 - a
            # fixed-name Legendary should hide the rolled affix regardless of
            # whether the name itself changed; no reason found for the
            # round-1 exception.
            'hidePrefixName': 1, 'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra staff: The Munderizer (insider egg, unchanged name)',
            'itemNameTag': 'tagSVCwpnMunderizer',
            'offensiveBaseLifeMin': 350.0,
            'offensiveTotalDamageReductionPercentMin': 40.0,
            'offensiveTotalDamageReductionPercentDurationMin': 4.0,
            'characterLife': 150.0, 'characterLifeRegen': 5.0,
        },
    ),
    dict(
        key='phoenix', name='Phoenix Ascendant',
        clone_from=r'records\equipmentweapon\axe\u_l_phoenix.dbr',
        donor_key=None,
        result=_SUPRA_PATH('phoenix'),
        trail=_TRAIL_AXE,
        shell=r'records\drxitem\supra\zrecipes\wep_axe_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_AXE,
        tag='tagSVCwpnPhoenix', formula_tag='tagSVCRecipePhoenix',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra axe: Phoenix Ascendant (Phoenix, ascended)',
            'itemNameTag': 'tagSVCwpnPhoenix',
            'offensivePhysicalMin': 200.0, 'offensivePhysicalMax': 230.0,
            'offensivePhysicalModifier': 45.0,
            'offensiveFireMin': 60.0, 'offensiveFireMax': 90.0, 'offensiveFireModifier': 70.0,
            'offensiveSlowFireMin': 45.0, 'offensiveSlowFireMax': 60.0,
            'offensiveSlowFireDurationMin': 4.0,
            'characterLife': 150.0, 'characterLifeRegenModifier': 50.0,
            'characterTotalSpeedModifier': 15.0,
            # identity KEPT: this is the whole point - the live granted Heat Shield.
            'itemSkillName': r'records\skills\earth\heatshield.dbr',
        },
    ),
    dict(
        key='erysichthon', name="Erysichthon's Undying Hunger",
        clone_from=r"records\equipmentweapon\axe\u_l_erysichthon'shunger.dbr",
        donor_key=None,
        result=_SUPRA_PATH('erysichthon'),
        trail=_TRAIL_AXE,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_axe_erysichthon_formula.dbr',
        fresh_template=r'records\drxitem\supra\recipes\wep_axe_formula.dbr',
        reagents=_REAGENTS_AXE,
        tag='tagSVCwpnErysichthon', formula_tag='tagSVCRecipeErysichthon',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': "B66 supra axe: Erysichthon's Undying Hunger (ascended)",
            'itemNameTag': 'tagSVCwpnErysichthon',
            'offensivePhysicalMin': 200.0, 'offensivePhysicalMax': 230.0,
            'offensivePhysicalModifier': 45.0,
            'offensiveLifeLeechMin': 60.0, 'offensiveLifeLeechChance': 100.0,
            'offensiveManaBurnDrainMin': 30.0, 'offensiveManaBurnDamageRatio': 100.0,
            'offensivePercentCurrentLifeMin': 12.0, 'offensivePercentCurrentLifeGlobal': 1,
            'offensiveGlobalChance': 10.0,
            'characterLife': 150.0,
        },
    ),
    dict(
        key='scylla', name='Scylla Unbound',
        clone_from=r'records\equipmentweapon\axe\us_l_baneofmessia01.dbr',
        donor_key=None,
        result=_SUPRA_PATH('scylla'),
        trail=_TRAIL_AXE,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_axe_scylla_formula.dbr',
        fresh_template=r'records\drxitem\supra\recipes\wep_axe_formula.dbr',
        reagents=_REAGENTS_AXE,
        tag='tagSVCwpnScylla', formula_tag='tagSVCRecipeScylla',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra axe: Scylla Unbound (Scylla, ascended; paired with Charybdis)',
            'itemNameTag': 'tagSVCwpnScylla',
            'offensivePhysicalMin': 195.0, 'offensivePhysicalMax': 225.0,
            'offensivePhysicalModifier': 45.0,
            'offensiveFearMin': 4.0, 'offensiveFearGlobal': 1, 'offensiveGlobalChance': 15.0,
            'offensiveSlowLifeLeachMin': 90.0, 'offensiveSlowLifeLeachGlobal': 1,
            'offensiveSlowLifeLeachDurationMin': 4.0,
            'offensiveSlowAttackSpeedMin': 40.0, 'offensiveSlowAttackSpeedDurationMin': 4.0,
            'characterDefensiveAbility': 90.0,
        },
    ),
    dict(
        key='charybdis', name='Charybdis Unchained',
        clone_from=r'records\equipmentweapon\axe\us_l_baneofmessia02.dbr',
        donor_key=None,
        result=_SUPRA_PATH('charybdis'),
        trail=_TRAIL_AXE,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_axe_charybdis_formula.dbr',
        fresh_template=r'records\drxitem\supra\recipes\wep_axe_formula.dbr',
        reagents=_REAGENTS_AXE,
        tag='tagSVCwpnCharybdis', formula_tag='tagSVCRecipeCharybdis',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra axe: Charybdis Unchained (Charybdis, ascended; paired with Scylla)',
            'itemNameTag': 'tagSVCwpnCharybdis',
            'offensivePhysicalMin': 195.0, 'offensivePhysicalMax': 225.0,
            'offensivePhysicalModifier': 45.0,
            'offensiveManaBurnDrainMin': 15.0, 'offensiveManaBurnDrainMax': 22.0,
            'offensiveManaBurnDamageRatio': 100.0,
            'offensiveStunMin': 1.0, 'offensiveStunMax': 3.0, 'offensiveStunGlobal': 1,
            'offensiveGlobalChance': 15.0,
            'offensiveSlowLifeMin': 150.0, 'offensiveSlowLifeDurationMin': 4.0,
            'offensiveSlowLifeGlobal': 1,
            'offensiveSlowRunSpeedMin': 40.0, 'offensiveSlowRunSpeedDurationMin': 4.0,
            'characterMana': 150.0,
        },
    ),
    dict(
        key='furies', name='Wrath of the Furies',
        clone_from=r'records\equipmentweapon\axe\u_l_thefuries.dbr',
        donor_key=None,
        result=_SUPRA_PATH('furies'),
        trail=_TRAIL_AXE,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_axe_furies_formula.dbr',
        fresh_template=r'records\drxitem\supra\recipes\wep_axe_formula.dbr',
        reagents=_REAGENTS_AXE,
        tag='tagSVCwpnFuries', formula_tag='tagSVCRecipeFuries',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra axe: Wrath of the Furies (The Furies, ascended)',
            'itemNameTag': 'tagSVCwpnFuries',
            'offensivePhysicalMin': 200.0, 'offensivePhysicalMax': 230.0,
            'offensivePhysicalModifier': 45.0,
            'offensiveConfusionMin': 4.0, 'offensiveConfusionChance': 15.0,
            'offensiveSlowBleedingMin': 200.0, 'offensiveSlowBleedingMax': 240.0,
            'offensiveSlowBleedingDurationMin': 4.0, 'offensiveSlowBleedingGlobal': 1,
            'offensiveSlowBleedingXOR': 1,
            'offensiveSlowPoisonMin': 200.0, 'offensiveSlowPoisonMax': 230.0,
            'offensiveSlowPoisonDurationMin': 4.0, 'offensiveSlowPoisonGlobal': 1,
            'offensiveSlowPoisonXOR': 1,
            # ROUND 2 (vet MEDIUM): the 2 Global-flagged slows above proc off
            # a shared offensiveGlobalChance - round 1 left this unset and
            # relied on the donor's inherited value (100, worked by
            # coincidence); now cleared+re-added explicitly.
            'offensiveGlobalChance': 100.0,
            'characterLife': 150.0,
        },
    ),
    dict(
        key='swordfish', name='Sword Fish',
        clone_from=None,
        donor_key='swordfish',
        result=_SUPRA_PATH('swordfish'),
        trail=_TRAIL_MACE,
        shell=r'records\drxitem\supra\zrecipes\wep_club_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_MACE,
        tag='tagSVCwpnSwordFish', formula_tag='tagSVCRecipeSwordFish',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1,
            # ROUND 2 (vet nit): aligned to 1/1 like the other 12 (see
            # Munderizer's note above - same reasoning).
            'hidePrefixName': 1, 'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra mace: Sword Fish (unchanged name - the joke stands)',
            'itemNameTag': 'tagSVCwpnSwordFish',
            'offensivePhysicalMin': 260.0, 'offensivePhysicalMax': 300.0,
            'offensivePhysicalModifier': 60.0,
            'offensiveSlowColdMin': 60.0, 'offensiveSlowColdDurationMin': 4.0,
            'offensiveSlowPoisonMin': 110.0, 'offensiveSlowPoisonDurationMin': 4.0,
            'offensiveSlowTotalSpeedMin': 1.0, 'offensiveSlowTotalSpeedMax': 70.0,
            'offensiveSlowTotalSpeedDurationMin': 4.0,
            # identity KEPT: concussive-blow augment, raised 1->3.
            'augmentSkillName1': r'records\skills\defensive\concussiveblow.dbr',
            'augmentSkillLevel1': 3,
        },
    ),
    dict(
        key='doomherald', name="The Doomcaller's Maul",
        clone_from=r'records\drxitem\eggs\zzz_bamfhammer.dbr',
        donor_key=None,
        result=_SUPRA_PATH('doomherald'),
        trail=_TRAIL_MACE,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_mace_doomherald_formula.dbr',
        fresh_template=r'records\drxitem\supra\recipes\wep_club_formula.dbr',
        reagents=_REAGENTS_MACE,
        tag='tagSVCwpnDoomHerald', formula_tag='tagSVCRecipeDoomHerald',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': "B66 supra mace: The Doomcaller's Maul (Doom Herald, ascended)",
            'itemNameTag': 'tagSVCwpnDoomHerald',
            'offensivePhysicalMin': 280.0, 'offensivePhysicalMax': 310.0,
            'offensivePhysicalModifier': 90.0, 'offensivePhysicalModifierChance': 12.0,
            'offensiveSlowDefensiveReductionMin': 180.0, 'offensiveSlowDefensiveReductionDurationMin': 5.0,
            'offensiveSlowDefensiveReductionModifier': 150.0,
            'offensiveSlowDefensiveReductionModifierChance': 20.0,
            'characterOffensiveAbility': 90.0,
            # identity KEPT: DRX concussive-blow augment, raised 2->4.
            'augmentSkillName1': r'records\skills\defensive\drxconcussiveblow.dbr',
            'augmentSkillLevel1': 4,
        },
    ),
    dict(
        key='hati', name='Hati',
        clone_from=None,
        donor_key='hati',
        result=_SUPRA_PATH('hati'),
        trail=_TRAIL_THROWN,
        shell=None,
        fresh_formula=r'records\drxitem\supra\zrecipes\svc_thrown_hati_formula.dbr',
        fresh_template=r'records\drxitem\supra\zrecipes\svc_thrown_charonstoll_formula.dbr',
        reagents=_REAGENTS_THROWN,
        tag='tagSVCwpnHati', formula_tag='tagSVCRecipeHati',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': 'B66 supra thrown: Hati (unchanged name - 0 twin, joins the 3 SVC thrown)',
            'itemNameTag': 'tagSVCwpnHati',
            'offensivePhysicalMin': 220.0, 'offensivePhysicalMax': 260.0,
            'offensivePhysicalModifier': 30.0, 'offensivePierceRatioMin': 20.0,
            'offensiveSlowBleedingMin': 200.0, 'offensiveSlowBleedingDurationMin': 4.0,
            'offensiveSlowBleedingChance': 100.0,
            'characterAttackSpeedModifier': 25.0, 'characterStrength': 70.0, 'characterLife': 200.0,
            # identity KEPT: the moon-wolf's bonus-vs-big-prey proc, untouched.
            'offensiveTotalDamageModifier': 200.0, 'offensiveTotalDamageModifierChance': 33.0,
        },
    ),
    dict(
        key='tensunswrath', name="Ten Suns' Wrath",
        clone_from=None,
        donor_key='dijunspride',
        result=_SUPRA_PATH('tensunswrath'),
        trail=None,  # bows carry no weaponTrail in this DB (Stormbringer precedent)
        shell=r'records\drxitem\supra\zrecipes\wep_bow_formula.dbr',
        fresh_formula=None, fresh_template=None,
        reagents=_REAGENTS_BOW,
        tag='tagSVCwpnTenSunsWrath', formula_tag='tagSVCRecipeTenSunsWrath',
        overrides={
            'itemClassification': 'Legendary', 'itemLevel': 65, 'levelRequirement': 65,
            'itemCostName': _COST, 'numRelicSlots': 1, 'hidePrefixName': 1,
            'hideSuffixName': 1, 'augmentAllLevel': 1,
            'FileDescription': "B66 supra bow: Ten Suns' Wrath (Di Jun's Pride, RENAMED - 2 twins)",
            'itemNameTag': 'tagSVCwpnTenSunsWrath',
            # ROUND 2 RETUNE (vet HIGH): the round-1 block (340-390 phys, FLAT
            # 220-300 pierce, 40-60 fire) made this the single highest raw-
            # damage weapon in the entire supra tier at ~2.3x the bow class's
            # only other sibling (Stormbringer, wep_bow.dbr, 145-160 phys),
            # contradicting the "none exceed the strongest sibling" claim.
            # Capped physical to the sibling's own band ceiling (145-160 -
            # matches exactly, does not exceed) and cut the flat pierce rider
            # down to a modest accent (matching Heartpierce's own pierce
            # block); fire raised to lean into the "Ten Suns" identity as the
            # elemental-caster component (matches Phoenix's already-vetted
            # fire block exactly: 60-90, +70%). Max total flat damage
            # (160+60+90=310) now sits alongside Phoenix (230+90=320), well
            # below Omega (292-315) and Last Word (300-360) - no longer the
            # tier's damage outlier.
            'offensivePhysicalMin': 145.0, 'offensivePhysicalMax': 160.0,
            'offensivePhysicalModifier': 30.0,
            'offensivePierceMin': 40.0, 'offensivePierceMax': 60.0, 'offensivePierceRatioMin': 20.0,
            'offensiveFireMin': 60.0, 'offensiveFireMax': 90.0, 'offensiveFireModifier': 70.0,
            'characterOffensiveAbility': 80.0, 'characterDexterity': 55.0,
            # Di Jun's Pride's OWN base-game record carries a dead dropSoundWater
            # ref ('Records\Sounds\SoundPak\ItemsWaterMdDropPak.dbr', resolves
            # nowhere - a pre-existing vanilla data slip, cosmetically inert,
            # same category as the 2 documented supra dead-refs). Not propagated:
            # repointed to the resolving base-game water-drop sound instead.
            'dropSoundWater': r'records\sounds\soundpak\items\watersmdroppak.dbr',
            # ROUND 2 (vet LOW): the donor JSON snapshot is now genuinely
            # verbatim (round 1 silently baked this retheme + a zeroed
            # offensivePhysicalModifier into the "verbatim" capture - the JSON
            # is fixed to hold the real base values, and this retheme is now
            # an explicit, documented override instead). Themed sun-projectile
            # (resolves; matches the Houyi/ten-suns myth the bow mesh already
            # depicts) replacing the donor's stock ArrowDefault01.
            'basicProjectileName': r'records\XPack4\Effects\Projectiles\TheSuns_Bow_Projectile.dbr',
        },
    ),
]

_NAME_TAGS = {
    'tagSVCwpnRipulsar': 'Ripulsar',
    'tagSVCwpnAquimae': 'Aquimae',
    'tagSVCwpnHeartpierce': 'The Unholy Heartpiercer',
    'tagSVCwpnHelona': "Helona's Ascension",
    'tagSVCwpnMunderizer': 'The Munderizer',
    'tagSVCwpnPhoenix': 'Phoenix Ascendant',
    'tagSVCwpnErysichthon': "Erysichthon's Undying Hunger",
    'tagSVCwpnScylla': 'Scylla Unbound',
    'tagSVCwpnCharybdis': 'Charybdis Unchained',
    'tagSVCwpnFuries': 'Wrath of the Furies',
    'tagSVCwpnSwordFish': 'Sword Fish',
    'tagSVCwpnDoomHerald': "The Doomcaller's Maul",
    'tagSVCwpnHati': 'Hati',
    'tagSVCwpnTenSunsWrath': "Ten Suns' Wrath",
}
_FORMULA_TAGS = {
    'tagSVCRecipeRipulsar': 'Mythic Formula - Ripulsar',
    'tagSVCRecipeAquimae': 'Mythic Formula - Aquimae',
    'tagSVCRecipeHeartpierce': 'Mythic Formula - The Unholy Heartpiercer',
    'tagSVCRecipeHelona': "Mythic Formula - Helona's Ascension",
    'tagSVCRecipeMunderizer': 'Mythic Formula - The Munderizer',
    'tagSVCRecipePhoenix': 'Mythic Formula - Phoenix Ascendant',
    'tagSVCRecipeErysichthon': "Mythic Formula - Erysichthon's Undying Hunger",
    'tagSVCRecipeScylla': 'Mythic Formula - Scylla Unbound',
    'tagSVCRecipeCharybdis': 'Mythic Formula - Charybdis Unchained',
    'tagSVCRecipeFuries': 'Mythic Formula - Wrath of the Furies',
    'tagSVCRecipeSwordFish': 'Mythic Formula - Sword Fish',
    'tagSVCRecipeDoomHerald': "Mythic Formula - The Doomcaller's Maul",
    'tagSVCRecipeHati': 'Arcane Formula - Hati',
    'tagSVCRecipeTenSunsWrath': "Mythic Formula - Ten Suns' Wrath",
}


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _resolve(db, path):
    want = _norm(path)
    for n in db.record_names():
        if _norm(n) == want:
            return n
    return None


def _next_loot_slot(db, table):
    i = 1
    while db.get_field_value(table, 'lootName%d' % i) not in (None, '', 0):
        i += 1
    return i


def _build_result_from_donor_json(db, spec):
    """Reconstruct a base-game-only orphan verbatim from the bundled JSON
    field snapshot (base_db is unreachable at registry time - see module
    docstring), then apply the supra overrides."""
    donor = _DONOR_FIELDS[spec['donor_key']]
    dest = spec['result']
    template = donor.get('templateName', '')
    _ensure_record(db, dest, template)
    for field, value in donor.items():
        db.set_field(dest, field, value)
    db._modified.add(dest)


def _build_result_from_clone(db, spec):
    src = _resolve(db, spec['clone_from'])
    if not src:
        raise SystemExit(
            "uber_orphan_weapons: clone source missing: %r (%s) - the orphan "
            "record is not present in db at registry time; re-verify against "
            "the current baseline arz." % (spec['clone_from'], spec['key']))
    db.clone_record(src, spec['result'])


# ROUND 2 (vet MEDIUM): prefixes whose donor-inherited values must be wiped
# before the supra retune is applied - mirrors N5's `_add_supra_thrown_weapons`
# in apply_svc_patches.py exactly ("...then CLEAR the donor's offensive/
# retaliation/character bonus stats so its native element does not bleed into
# the retheme"). Without this, the orphan's original combat stats bleed
# through uncontrolled (round-1 examples: erysichthon's negative
# characterLifeRegen, furies'/scylla's stray characterStrength, charybdis'
# stray characterOffensiveAbility, doomherald's stray Str/Dex/Int, furies'
# undocumented total-speed slow). Fields a weapon is meant to KEEP (identity
# skills: itemSkillName, augmentSkillName1/Level1) do not match any of these
# prefixes and are set independently via `overrides`, so they are never
# touched by this clear. Any rider that legitimately depends on an inherited
# value cleared here (Aquimae/Furies' shared offensiveGlobalChance) is
# re-added explicitly in that weapon's `overrides` dict.
_CLEAR_PREFIXES = (
    'offensive', 'retaliation', 'characterDexterity', 'characterStrength',
    'characterIntelligence', 'characterLife', 'characterOffensiveAbility',
    'characterAttackSpeedModifier',
)


def _clear_inherited_combat_stats(db, dest):
    ff = db.get_fields(dest)
    if not ff:
        return
    for k in [k for k in list(ff) if k.split('###')[0].startswith(_CLEAR_PREFIXES)]:
        del ff[k]


def _apply_overrides(db, spec):
    dest = spec['result']
    if spec.get('trail'):
        db.set_field(dest, 'weaponTrail', spec['trail'])
    for field, value in spec['overrides'].items():
        db.set_field(dest, field, value)
    db._modified.add(dest)


def _build_formula(db, spec):
    dest = spec['shell'] if spec['shell'] else spec['fresh_formula']
    if spec['shell']:
        src = _resolve(db, spec['shell'])
        if not src:
            raise SystemExit(
                "uber_orphan_weapons: formula shell missing: %r (%s)"
                % (spec['shell'], spec['key']))
        # repoint the existing orphaned shell IN PLACE (its live `recipes\`
        # twin, if any, is a DIFFERENT record and is never touched).
        dest = src
    else:
        tmpl_src = _resolve(db, spec['fresh_template'])
        if not tmpl_src:
            raise SystemExit(
                "uber_orphan_weapons: formula template missing: %r (%s)"
                % (spec['fresh_template'], spec['key']))
        db.clone_record(tmpl_src, dest)

    r1, r2, r3 = spec['reagents']
    db.set_field(dest, 'artifactName', spec['result'])
    db.set_field(dest, 'reagent1BaseName', r1)
    db.set_field(dest, 'reagent2BaseName', r2)
    db.set_field(dest, 'reagent3BaseName', r3)
    db.set_field(dest, 'description', spec['formula_tag'])
    db.set_field(dest, 'FileDescription', 'B66 supra formula: ' + spec['name'])
    db.set_field(dest, 'artifactCreationCost', 10000000)
    db.set_field(dest, 'itemCost', 500000)
    db._modified.add(dest)
    return dest


def _wire_drop_tables(db, formula_path):
    for table in (_SUPRA_TABLE, _SUPRA_SPECIAL):
        if not db.has_record(table):
            raise SystemExit("uber_orphan_weapons: loot table missing: %r" % table)
        slot = _next_loot_slot(db, table)
        db.set_field(table, 'lootName%d' % slot, formula_path)
        db.set_field(table, 'lootWeight%d' % slot, 100)
        db._modified.add(table)


def apply(db, tags):
    formula_paths = []
    for spec in _WEAPONS:
        if spec['clone_from']:
            _build_result_from_clone(db, spec)
        else:
            _build_result_from_donor_json(db, spec)
        # ROUND 2 (vet MEDIUM): wipe donor-inherited combat stats before the
        # retune so orphan riders never bleed through uncontrolled.
        _clear_inherited_combat_stats(db, spec['result'])
        _apply_overrides(db, spec)
        fpath = _build_formula(db, spec)
        _wire_drop_tables(db, fpath)
        formula_paths.append((spec['key'], spec['result'], fpath))

    for tag_key, text in _NAME_TAGS.items():
        tags[tag_key] = text
    for tag_key, text in _FORMULA_TAGS.items():
        tags[tag_key] = text

    print("  B66: %d orphan weapons -> supra (%s); %d formula(s) wired into "
          "supra.dbr + supra_special.dbr @ w100"
          % (len(_WEAPONS), ', '.join(s['name'] for s in _WEAPONS), len(formula_paths)))


def verify(db, tags):
    """Post-finalization: every result + formula resolves, every formula is in
    BOTH drop tables, every tag we reference is present, no weapon lost its
    kept identity skill."""
    errors = []
    for spec in _WEAPONS:
        if not db.has_record(spec['result']):
            errors.append('result missing: %s' % spec['result'])
        fpath = spec['shell'] if spec['shell'] else spec['fresh_formula']
        if not db.has_record(fpath):
            errors.append('formula missing: %s' % fpath)
        else:
            art = db.get_field_value(fpath, 'artifactName')
            if _norm(art) != _norm(spec['result']):
                errors.append('formula %s artifactName mismatch: %r != %r'
                               % (fpath, art, spec['result']))
            for rfield in ('reagent1BaseName', 'reagent2BaseName', 'reagent3BaseName'):
                rv = db.get_field_value(fpath, rfield)
                if not rv:
                    errors.append('formula %s %s empty' % (fpath, rfield))

    for table in (_SUPRA_TABLE, _SUPRA_SPECIAL):
        listed = set()
        i = 1
        while True:
            v = db.get_field_value(table, 'lootName%d' % i)
            if v in (None, '', 0):
                break
            listed.add(_norm(v))
            i += 1
        for spec in _WEAPONS:
            fpath = spec['shell'] if spec['shell'] else spec['fresh_formula']
            if _norm(fpath) not in listed:
                errors.append('%s: formula %s not listed (table has %d slots)'
                               % (table, fpath, i - 1))

    for tag_key in list(_NAME_TAGS) + list(_FORMULA_TAGS):
        if tag_key not in tags:
            errors.append('tag never added: %s' % tag_key)

    # Identity-skill preservation spot-check (the 4 KEPT-proc weapons).
    _IDENTITY = {
        'helona': ('itemSkillName', r'records\skills\item skills\helona_summon.dbr'),
        'phoenix': ('itemSkillName', r'records\skills\earth\heatshield.dbr'),
    }
    by_key = {s['key']: s for s in _WEAPONS}
    for key, (field, expect) in _IDENTITY.items():
        got = db.get_field_value(by_key[key]['result'], field)
        if _norm(got) != _norm(expect):
            errors.append('%s lost its identity skill on %s: got %r' % (key, field, got))

    # ROUND 2 guards (regression protection for the vet's HIGH/MEDIUM/LOW fixes):
    # (a) no weapon's overrides-declared physical max exceeds its class band
    #     ceiling (bow/sword capped this round at 160 - see the retune notes
    #     on tensunswrath/heartpierce/ripulsar above).
    _BAND_CAP = {'tensunswrath': 160.0, 'heartpierce': 160.0, 'ripulsar': 160.0}
    for key, cap in _BAND_CAP.items():
        got = db.get_field_value(by_key[key]['result'], 'offensivePhysicalMax')
        if got is None or float(got) > cap:
            errors.append('%s: offensivePhysicalMax %r exceeds band cap %.1f'
                           % (key, got, cap))
    # (b) the 2 riders whose Global-flagged effects depend on a shared
    #     offensiveGlobalChance (round-1 relied on donor-inherited luck; round
    #     2 clears then re-adds it explicitly) must actually be non-zero.
    for key in ('aquimae', 'furies'):
        got = db.get_field_value(by_key[key]['result'], 'offensiveGlobalChance')
        if not got:
            errors.append('%s: offensiveGlobalChance missing/zero after clear - '
                           'its Global-flagged riders cannot proc' % key)
    # (c) every result hides rolled prefix/suffix (fixed-name Legendary
    #     convention - round 1 left Munderizer/Sword Fish at 0/0 by oversight).
    for spec in _WEAPONS:
        for f in ('hidePrefixName', 'hideSuffixName'):
            got = db.get_field_value(spec['result'], f)
            if got not in (1, 1.0, '1'):
                errors.append('%s: %s = %r (expected 1)' % (spec['key'], f, got))

    if errors:
        raise SystemExit(
            "uber_orphan_weapons.verify FAILED (%d issue(s)):\n  %s"
            % (len(errors), "\n  ".join(errors)))
    print("  uber_orphan_weapons.verify: 14 results + 14 formulas resolve, "
          "wired in both supra tables, identity skills intact, all tags present")
