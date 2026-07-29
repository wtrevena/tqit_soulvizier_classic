"""
tools/patches/skill_quality.py

build37 GRANTED-SKILL QUALITY PASS  (BACKLOG #31 / task #31; spec:
scratchpad/specs/granted_skill_quality_pass_spec.md; binding decisions:
scratchpad/specs/WILL_DECISIONS_2026-07-11.md, section "GRANTED-SKILL QUALITY PASS").

WHAT THIS DOES
--------------
Will's Ground Smash complaint - "too many souls have the same skill, it doesn't make
any sense" - generalised. The load-bearing word is *sense*, not *count*: a big shared
count is fine when the skill is a monster family's genuine signature (amgoz voice V3 /
neg-list #13); the defect is a skill on a soul OUTSIDE its family (a rogue's blinding
powder on a carrion crow) or lazy sameness. This wave, per the spec's two-track fix:

  * Track B - REASSIGN off-theme souls onto an identity-true proc (a namesake move from
    the castability-verified palette) or, for a common mook with no signature, an honest
    STAT-ONLY ring with an amgoz downside (voice V1/V2, neg-list #2/#3).
  * Track A/C - keep genuine family skills, apply Will's GO-DEEPER differentiations
    (bats -> Bat Swarm, gorgons -> Petrifying Gaze/Arrow Nova, Dagon -> Tidal Strike,
    sp_toxeus -> Shadow Surge, sp_hades -> Star of Hades, maenads -> Blood Frenzy, ...),
    then LOCK every remaining family skill to an explicit named roster with a fail-loud
    diversity gate so filler can never silently balloon again.

WILL_DECISIONS applied: GO DEEPER (apply the optional splits) + Dagon = Tidal Strike +
sp_toxeus = Shadow Surge (differentiated from base Toxeus's flash powder) + Satyr Scout
KEEPS flash powder (the reworked skill is a real skill now).

REGISTRY CONTRACT
-----------------
MODULE_NAME + apply(db, tags). Runs AFTER the monolith
(apply_svc_patches.apply_all_extended_patches) on the SAME db/tags objects; the registry
runs modules in manifest order after the monolith and gates last over everything.

WHY POST-MONOLITH (not OVERHAULS source edits): the maximum-parallelism registry model -
this module never touches apply_svc_patches.py. It finds each soul in the BUILT db by
(current-skill-basename, itemNameTag) and reassigns EVERY tier + duplicate record, so it
is robust to OVERHAULS substring/site details and to the pcsafe/plain path split
(basename-collapsed, exactly like the monolith's own diversity gate).

CASTABILITY (pcsafe law, spec section 3): every target path below is the EXACT record an
existing, working soul already grants (probe-verified against the build36 arz), i.e. an
anim-less records/skills/soulskills/<x>.dbr record or an existing pcsafe/ clone - so every
pick is already player-castable and shows a real skill name (never a raw tag). As
belt-and-suspenders the module re-invokes the monolith's idempotent castability wave
(_fix_granted_skill_castability) after reassigning, so any controller/anim parity for the
changed grants is guaranteed regardless of registry gate-phase ordering.

No Text.arc change (spec section 6.4): every pick reuses an existing display-name tag and
every stat-only edit adds no name/desc, so this ships without a coupled Text rebuild -
the `tags` object is untouched.
"""

import os
import re
import sys

MODULE_NAME = 'skill_quality'

# --- import the monolith for the castability wave + shared constants -----------------
# The module lives at tools/patches/skill_quality.py; the monolith is tools/apply_svc_patches.py.
_TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
try:
    import apply_svc_patches as _svc
except Exception:  # pragma: no cover - the monolith is always importable in a build
    _svc = None

# Autocast controllers (base templates). Prefer the monolith's constants so we stay in
# lockstep; fall back to the literal paths (identical strings) if the import failed.
if _svc is not None:
    ON_ATTACK = _svc._AC_ON_ATTACK       # base_atenemy_onattack  (targetType Enemy)
    SELF_ATTACK = _svc._AC_SELF_ATTACK   # base_atself_onattack   (targetType Self)
else:  # pragma: no cover
    ON_ATTACK = (r'records\xpack\ai controllers\autocast_items\basetemplates'
                 r'\base_atenemy_onattack.dbr')
    SELF_ATTACK = (r'records\xpack\ai controllers\autocast_items\basetemplates'
                   r'\base_atself_onattack.dbr')

# ── The identity-true palette (EXACT castable paths - mirror existing grantors) ───────
# Every path is the record a working soul already grants in the build36 arz (probe-verified:
# anim-less soulskills copy, or an existing pcsafe clone). Display name in comments.
_SK = 'records\\skills\\soulskills\\'
BATFLURRY    = _SK + 'alcestis_batflurry.dbr'          # "Bat Swarm"          (AttackProjectileBurst)
DEVOUR       = _SK + 'bloodtip_devour.dbr'             # "Devour"             (AttackRadius)
HARPOON      = _SK + 'dapoyan_harpoon.dbr'             # "Bloodspear"         (AttackProjectileBurst) cd 0->6
ARROWSTORM   = _SK + 'arrowstorm.dbr'                  # "Arrow Nova"         (AttackProjectileRing)
BLOODFRENZY  = _SK + 'quak_bloodfrenzy.dbr'            # "Blood Frenzy"       (BuffSelfDuration, self)
VENOMBOLT    = _SK + 'venombolt_nova.dbr'              # "Venombolt"          (AttackProjectileRing)
CROWSUMMON   = _SK + 'carrioncrow_summon.dbr'          # "Summon Carrion Crow"(SpawnPet)
SHADOWSURGE  = _SK + 'nightstalker_shadowsurge.dbr'    # "Shadow Surge"       (AttackRadius)
CHAINLEECH   = _SK + 'syrinx_chainleech.dbr'           # "Leeching Vein"      (AttackChain)
CENON        = _SK + 'cenon_lightningball.dbr'         # "Lightning Ball"     (AttackProjectileBurst)
PETRIFY      = _SK + 'pcsafe\\medusa_petrify.dbr'      # "Petrifying Gaze"    (AttackProjectile,  Ensnare->pcsafe)
WARSHOUT     = _SK + 'pcsafe\\korlhrut_warshout.dbr'   # "War Shout"          (AttackProjectileRing, CallOfTheHunt->pcsafe)
ECLIPSE      = _SK + 'pcsafe\\calybe_eclipse.dbr'      # "Eclipse"            (AttackRadius, Eclipse->pcsafe)
HADESSTAR    = _SK + 'pcsafe\\hades_star.dbr'          # "Star of Hades"      (AttackProjectileMultiHit, MultiStar->pcsafe)
THUNDERSTORM = _SK + 'pcsafe\\enyo_thunderstorm.dbr'   # "Thunderstorm"       (AttackProjectileAreaEffect, Thunderstorm->pcsafe)
TIDALSTRIKE  = _SK + 'pcsafe\\ichthian_tidalstrike.dbr'# "Tidal Strike"       (AttackProjectileAreaEffect, TidalStrike->pcsafe)

STAT_ONLY = 'STAT_ONLY'   # sentinel: delete itemSkillName/Level/Controller -> honest stat ring

# ── REASSIGN plan: current_skill_basename -> { itemNameTag: (target, controller) } ───
# target = a palette path (reassign) or STAT_ONLY. controller = None keeps the existing
# controller; a value sets it (self-buffs need SELF_ATTACK; summons/offense use ON_ATTACK).
# Souls NOT listed under a skill KEEP it (they are the family roster).
REASSIGN = {
    # 4.1 hero_sonicwave 8 -> 1 (keep Alecto tagSoulName449, an SV-authored Fury's shriek).
    'hero_sonicwave.dbr': {
        'tagSoulName1':      (STAT_ONLY, None),            # Satyr Peltast (javelin mook)
        'tagSoulName2':      (STAT_ONLY, None),            # Satyr Veteran Peltast
        'tagSoulName3':      (HARPOON, ON_ATTACK),         # Satyr Elite Peltast -> Bloodspear
        'tagSoulName26':     (STAT_ONLY, None),            # Mountain Satyr Peltast
        'tagSoulName27':     (STAT_ONLY, None),            # Mountain Satyr Veteran Peltast
        'tagSVCSoulDevNate': (WARSHOUT, ON_ATTACK),        # z_nate "warfare bruiser" -> War Shout
        'tagSoulSVC9026':    (STAT_ONLY, None),            # hero_junshan (brute)
    },
    # 4.2 arachne_venomspray 14 -> 8 (2 off-theme reassigns + GO-DEEPER gorgon/dagon splits;
    # WILL_DECISIONS "venomspray -> 8"). The gorgon sub-family (guard/sstheno -> Petrifying
    # Gaze, archer -> Arrow Nova) differentiates onto the true gorgon signature.
    'arachne_venomspray.dbr': {
        'tagSoulName235':   (STAT_ONLY, None),             # gatekeeper (ascacophus: Plant/physical bruiser)
        'tagSoulName412':   (ECLIPSE, ON_ATTACK),          # bthokite (epiales nightmare demon) -> Eclipse (Fear)
        'tagSoulName53':    (PETRIFY, ON_ATTACK),          # gorgonguard -> Petrifying Gaze (true gorgon)
        'tagSoulName47':    (PETRIFY, ON_ATTACK),          # sstheno (Gorgon sister of Medusa) -> Petrifying Gaze
        'tagSoulName54':    (ARROWSTORM, ON_ATTACK),       # gorgonarcher -> Arrow Nova
        'tagSVCSoulDagon':  (TIDALSTRIKE, ON_ATTACK),      # Dagon (deep-sea lord) -> Tidal Strike [WILL]
    },
    # 4.3 lifedrain 20 -> 11 (bats -> Bat Swarm; GO-DEEPER flesh-eaters -> Devour, casters -> Leeching Vein).
    'lifedrain.dbr': {
        'tagSoulName51':               (BATFLURRY, ON_ATTACK),  # cavebat
        'tagSoulName52':               (BATFLURRY, ON_ATTACK),  # giganticbat
        'tagSoulName267':              (BATFLURRY, ON_ATTACK),  # elephantsnatcher
        'tagSoulName268':              (BATFLURRY, ON_ATTACK),  # goatsucker (chupacabra)
        'tagSoulName269':              (BATFLURRY, ON_ATTACK),  # leatherwing
        'tagSoulName301':              (DEVOUR, ON_ATTACK),     # corpsemanager (eurynomus, corpse-eater)
        'tagSVCSoulLimosLifeeater':    (DEVOUR, ON_ATTACK),     # limoslifeater ("Life-eater")
        'tagSoulName303':              (CHAINLEECH, ON_ATTACK), # theetheralone (drain caster)
        'tagSoulName183':              (CHAINLEECH, ON_ATTACK), # daeros (drain caster)
    },
    # 4.4 ringoflightning 13 -> 9 (assassin off-theme + GO-DEEPER storm-flier/caster splits).
    'ringoflightning.dbr': {
        'tagSVCSoulSPToxeus': (SHADOWSURGE, ON_ATTACK),    # sp_toxeus (assassin) -> Shadow Surge [WILL]
        'tagSoulName464':     (THUNDERSTORM, ON_ATTACK),   # stormbird (Storm Crow) -> Thunderstorm
        'tagSoulName173':     (THUNDERSTORM, ON_ATTACK),   # athenos (storm Fury) -> Thunderstorm
        'tagSVCSoulNVio':     (CENON, ON_ATTACK),          # n_vio (caster) -> Lightning Ball
    },
    # 4.6 melinoe_bloodboil 8 -> 7 (Hades gets his own signature).
    'melinoe_bloodboil.dbr': {
        'tagSVCSoulSPHades':  (HADESSTAR, ON_ATTACK),      # sp_hades -> Star of Hades
    },
    # 4.8 toxeus_flashpowder 13 -> 4 (the 9 off-theme reassigns; keep Toxeus + 2 dev rogues + Satyr Scout).
    'toxeus_flashpowder.dbr': {
        # carrionlord (bird boss) -> Summon Carrion Crow, MANUAL-CAST (controller=None).
        # RESOLVED (lowlift wave item 5, was ON_ATTACK): a mod-generated permanent
        # Skill_SpawnPet ring must be manual-cast, per the SAME class-wide convention
        # souls_quality.py's roster-derived summon-controller fix already enforces for
        # the other 8 mod-touched families (crowboar/glittertail/koroush/nkac + komara/
        # melalos/oythroneus) - ON_ATTACK on a PERMANENT summon is the exact reset-on-
        # attack bug class (D3), not a deliberate "swarm" identity (contrast the 18
        # amgoz1 SV-ORIGINAL swarm souls that SV098 itself ships with the controller -
        # carrionlord is NOT one of those; it is a mod REASSIGN target, so there is no
        # upstream design to defer to). Previously this line set ON_ATTACK, which
        # souls_quality (registry pos 13, running after skill_quality's pos 4) then
        # stripped again as a mod-introduced controller on a permanent summon - a
        # documented but confusing "later-wins" cross-module collision (S4b WARN).
        # Setting None here directly makes BOTH modules agree at the source: no
        # collision, no WARN, and the FINAL db is BYTE-IDENTICAL (souls_quality was
        # already producing manual-cast as the effective, shipped behavior).
        'tagSoulName49':  (CROWSUMMON, None),
        'tagSoulName29':  (STAT_ONLY, None),               # carrioncrow (mook bleed bird)
        'tagSoulName40':  (STAT_ONLY, None),               # bloodwing (mook bleed bird)
        'tagSoulName223': (ARROWSTORM, ON_ATTACK),         # pandarus (archer hero) -> Arrow Nova
        'tagSoulName34':  (BLOODFRENZY, SELF_ATTACK),      # maenad Vanguard -> Blood Frenzy (self)
        'tagSoulName35':  (BLOODFRENZY, SELF_ATTACK),      # maenad Tracker  -> Blood Frenzy (self)
        'tagSoulName114': (VENOMBOLT, ON_ATTACK),          # stingeye (mantid) -> Venombolt
        'tagSoulName96':  (STAT_ONLY, None),               # fluxfang (raptor stat ring)
        'tagSoulName352': (STAT_ONLY, None),               # wraithwing (vulture; authored sheet below)
    },
}

# ── amgoz-voice enrichment (V1: the stat line is characterisation, downsides included) ──
# FLAT downsides (tier-uniform, like Polyphemus's flat -6 speed) for the stat-only mooks
# that otherwise ship all-upside (neg-list #3). Every field is present-at-0 in the soul
# item template, so set_field only updates a value (dtype preserved). tag -> (field, value).
FLAT_DOWNSIDE = {
    'tagSoulName1':   ('characterOffensiveAbilityModifier', -5.0),   # satyr peltast: a mook's poor aim
    'tagSoulName2':   ('characterOffensiveAbilityModifier', -5.0),   # satyr veteran peltast
    'tagSoulName26':  ('characterOffensiveAbilityModifier', -5.0),   # mountain satyr peltast
    'tagSoulName27':  ('characterOffensiveAbilityModifier', -5.0),   # mountain satyr veteran peltast
    'tagSoulSVC9026': ('characterTotalSpeedModifier',       -6.0),   # hero_junshan brute: lumbering (Polyphemus precedent)
    'tagSoulName29':  ('characterLifeModifier',             -8.0),   # carrion crow: a frail glass-cannon bird
    'tagSoulName40':  ('characterLifeModifier',             -8.0),   # blood wing: bleed glass-cannon
    'tagSoulName96':  ('characterLifeModifier',             -8.0),   # flux fang: raptor glass-cannon
    'tagSoulName235': ('characterRunSpeedModifier',         -6.0),   # gatekeeper: a slow, rooted guardian
}

# Wrathwing (tagSoulName352) authored carrion-scavenger sheet (spec 4.8: the single best
# "make it feel authored" opportunity). KEEP its existing characterLifeModifier -15 downside,
# characterRunSpeedModifier +14, offensivePierce 16/30, drxcalculatedstrike aug. ADD rending
# talons (bleed), carrion rot (poison), a fast-scavenger attack speed, and a Beast racial.
# Tier-scaled n/e/l ~= 0.6/0.8/1.0. wraithwing has clean n/e/l (no doubled-suffix duplicates).
WRAITHWING_TAG = 'tagSoulName352'
WRAITHWING_TIER = {
    'n': {'offensiveSlowBleedingMin': 33.0, 'offensiveSlowBleedingDurationMin': 3.0,
          'offensivePoisonMin': 12.0, 'offensivePoisonMax': 24.0, 'offensivePoisonDurationMin': 3.0,
          'characterAttackSpeedModifier': 10.0, 'racialBonusPercentDamage': 18.0},
    'e': {'offensiveSlowBleedingMin': 44.0, 'offensiveSlowBleedingDurationMin': 3.0,
          'offensivePoisonMin': 16.0, 'offensivePoisonMax': 32.0, 'offensivePoisonDurationMin': 3.0,
          'characterAttackSpeedModifier': 11.0, 'racialBonusPercentDamage': 24.0},
    'l': {'offensiveSlowBleedingMin': 55.0, 'offensiveSlowBleedingDurationMin': 3.0,
          'offensivePoisonMin': 20.0, 'offensivePoisonMax': 40.0, 'offensivePoisonDurationMin': 3.0,
          'characterAttackSpeedModifier': 12.0, 'racialBonusPercentDamage': 30.0},
}
WRAITHWING_RACE = 'Beast'   # racialBonusRace (a carrion beast that preys on beasts), all tiers

# ── One skill-record cooldown fix (spec 4.1 / 6): dapoyan_harpoon soul-copy has cd 0.0 ──
# (fires every frame as an autocast). Set it to 6.0. Blast radius: also granted by its one
# pre-existing grantor (Dapoyan the Deepstalker) - the 0->6 change is a strict fix for it too.
DAPOYAN_HARPOON_RECORD = HARPOON
DAPOYAN_HARPOON_CD = 6.0

# ── The fail-loud diversity gate roster (spec section 5), POST-this-wave end state ──────
# Each family skill -> the EXACT set of itemNameTags allowed to grant it. The gate requires
# each skill's grantor tag-set be a subset of its roster (a new soul silently joining a
# family = fail) and caps every other non-exempt skill at MAX_SHARED. cyclops_groundsmash is
# already locked by the monolith to its 6-soul roster; we mirror it here so this gate also
# guards it end-to-end.
MAX_SHARED = 8
SUMMON_EXEMPT = {
    'skeleton_summon.dbr', 'skeletonarcher_summon.dbr', 'mummy_summon.dbr',
    'carrioncrow_summon.dbr', 'formicid_summon.dbr', 'peng_summon.dbr',
    'summon_zombiesoldier.dbr', 'foulbeast_summon_soul.dbr',
}
ALLOW = {
    'lifedrain.dbr': {  # undead / spirit / corpse / decay drain family (12, post bats/devour/leech)
        'tagSVCSoulSatyrSpiritcaller', 'tagSoulName25', 'tagSoulName456', 'tagSoulName313',
        'tagSoulName228', 'tagSoulName82', 'tagSoulName132', 'tagSoulName132B', 'tagSoulName70',
        'tagSVCSoulBloodShaman', 'tagSVCSoulIlsevar',
        # polis_vault's Alkyoneus the Soul-Gaoler (registry module runs AFTER this one, so its
        # grant is only visible to this gate now that it runs POST-finalization): the giant IS a
        # life-drinker (spirit\lifedrain grant + big ADCtH), family-appropriate.
        'tagSVCSoulGaoler'},
    'firefragmentnova.dbr': {  # fire family (Bloodcrow spec governs the record CD; unchanged here) (15)
        'tagSVCSoulSatyrMagi', 'tagSoulName17', 'tagSoulName18', 'tagSoulName19', 'tagSoulName21',
        'tagSoulName24', 'tagSoulName465', 'tagSoulName112', 'tagSVCSoulDevCory', 'tagSVCSoulDevMorgan',
        'tagSVCSoulDevScott', 'tagSVCSoulFireTrap', 'tagSoulSVC9019', 'tagSoulName98',
        # bossarena's Aithon the Ember-Crowned (registry module runs AFTER this one, so its grant
        # is only visible to this gate now that it runs POST-finalization): a fire boss (volcanic-orb
        # + fire-enchant kit, "he IS fire" identity resist) reusing the fire-family nova proc,
        # family-appropriate by design - mirrors the Gaoler/ToxeusHunt late-registry roster entries.
        'tagSVCSoulAithon'},
    'arachne_venomspray.dbr': {  # venomous family (ascacophus/epiales/gorgons/dagon removed) (8)
        'tagSoulName231', 'tagSoulName71', 'tagSoulName194', 'tagSoulName206',
        'tagSoulName332', 'tagSoulName418', 'tagSVCSoulNomnom', 'tagSoulSVC9023'},
    'ringoflightning.dbr': {  # lightning / storm family (assassin + storm-fliers + caster removed) (10)
        'tagSoulName553', 'tagSoulName602', 'tagSVCSoulDarkMonolith', 'tagSVCSoulJabarto',
        'tagSoulSVC9020', 'tagSoulSVC9016', 'tagSVCSoulGitar3', 'tagSVCSoulDevArthur',
        'tagSVCSoulDevTildaV',
        # HC uber Xix (svc_uber\xix_soul_{n,e,l}): a real lightning grantor shipped in
        # build36a, family-appropriate (a ring-of-lightning storm soul); was the 2nd
        # genuine roster gap the build37 full-registry gate surfaced.
        'tagSVCSoulHCXix'},
    'melinoe_bloodboil.dbr': {  # blood-demon family (sp_hades -> Star of Hades removed) (8)
        'tagSoulName178', 'tagSoulName410', 'tagSoulName151', 'tagSoulName607', 'tagSoulName426',
        'tagSVCSoulDevTom', 'tagSVCSoulLeinth',
        # HC uber Bloodrunner (svc_uber\bloodrunner_soul_{n,e,l}): a real blood-boil
        # grantor shipped in build36a, family-appropriate (a blood-demon soul); the 1st
        # genuine roster gap the build37 full-registry gate surfaced.
        'tagSVCSoulHCBloodrunner'},
    'harpy_lightningaura.dbr': {  # harpy / lightning-aura family (SV-authored, kept whole) (9)
        'tagSoulName56', 'tagSoulName57', 'tagSoulName58', 'tagSoulName216', 'tagSoulName314',
        'tagSoulName497', 'tagSVCSoulDevParnell', 'tagSVCSoulNEmgiec', 'tagSoulSVC9001'},
    'toxeus_flashpowder.dbr': {  # rogue / assassin family (post 9-reassign; sp_toxeus -> Shadow Surge) (4)
        'tagSoulName505', 'tagSVCSoulDevDavid', 'tagSVCSoulDevFrazier', 'tagSoulName4'},
        # ⚠️ 'tagSVCSoulToxeusHunt' REMOVED, b98 round 2 (R-84, feat/endless-hunt), BL-103
        # fix-upstream: this roster is ground truth and the Endless Hunt LEFT the family.
        # `toxeus_hunt_encounter` retires flash powder from his own kit as "the Enslaver's"
        # and repoints his soul at `svc_hunt_quarrysmark`, so leaving him listed here would
        # be a stale claim about who grants what. The gate is subset-based, so a stale entry
        # would not have failed the build - which is exactly why it had to be removed by
        # hand. Keeping it accurate also makes the coupling FAIL-LOUD in the other
        # direction: if the repoint ever regresses, he is back outside this locked roster
        # and this gate goes red.
    # cyclops_groundsmash.dbr roster is injected from the monolith's _GS_ROSTER_TAGS at gate time.
}


# ───────────────────────── helpers ──────────────────────────────────────────────────
def _basename(path):
    return str(path).replace('/', '\\').rsplit('\\', 1)[-1].lower()


def _first_value(v):
    """get_field_value may return a scalar or a list; normalise to a scalar."""
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _iter_soul_item_records(db):
    for rec in db.record_names():
        rl = rec.replace('/', '\\').lower()
        if '\\soul\\' in rl and 'equipmentring' in rl:
            yield rec, rl


def _delete_fields(db, rec, names):
    """Remove named fields from a record (stat-only) and mark it modified."""
    fields = db.get_fields(rec)
    if not fields:
        return
    doomed = [k for k in list(fields.keys()) if k.split('###')[0] in names]
    for k in doomed:
        del fields[k]
    if doomed:
        db._modified.add(rec)


def _tier_of(rec_lower):
    """n/e/l tier from a soul record path suffix; default 'n' (conservative)."""
    if '_soul_l' in rec_lower:
        return 'l'
    if '_soul_e' in rec_lower:
        return 'e'
    return 'n'


# ───────────────────────── the wave ─────────────────────────────────────────────────
def _apply_reassignments(db):
    """Re-point itemSkillName off the filler skills onto identity-true procs / stat-only,
    across every tier + duplicate record. Idempotent (a second run finds nothing to do)."""
    n_reassigned = 0
    n_statonly = 0
    for rec, rl in _iter_soul_item_records(db):
        isk = _first_value(db.get_field_value(rec, 'itemSkillName'))
        if not (isinstance(isk, str) and isk.strip()):
            continue
        plan = REASSIGN.get(_basename(isk))
        if not plan:
            continue
        tag = str(_first_value(db.get_field_value(rec, 'itemNameTag')))
        action = plan.get(tag)
        if action is None:
            continue  # this identity KEEPS the skill (it is the family roster)
        target, controller = action
        if target is STAT_ONLY or target == STAT_ONLY:
            _delete_fields(db, rec, {'itemSkillName', 'itemSkillLevel',
                                     'itemSkillAutoController'})
            n_statonly += 1
        else:
            db.set_field(rec, 'itemSkillName', target)          # no dtype (field exists)
            if controller:
                db.set_field(rec, 'itemSkillAutoController', controller)
            db._modified.add(rec)
            n_reassigned += 1
    return n_reassigned, n_statonly


def _apply_enrichment(db):
    """amgoz V1 downsides on the stat-only mooks + Wrathwing's authored carrion sheet."""
    n = 0
    for rec, rl in _iter_soul_item_records(db):
        tag = str(_first_value(db.get_field_value(rec, 'itemNameTag')))
        if tag in FLAT_DOWNSIDE:
            field, value = FLAT_DOWNSIDE[tag]
            db.set_field(rec, field, value)      # field present-at-0; dtype preserved
            db._modified.add(rec)
            n += 1
        if tag == WRAITHWING_TAG:
            vals = WRAITHWING_TIER[_tier_of(rl)]
            for field, value in vals.items():
                db.set_field(rec, field, value)
            db.set_field(rec, 'racialBonusRace', WRAITHWING_RACE)
            db._modified.add(rec)
            n += 1
    return n


def _apply_dapoyan_cooldown(db):
    """dapoyan_harpoon soul-copy cd 0.0 -> 6.0 (a 0-cd autocast fires every frame)."""
    rec = None
    for cand in db.record_names():
        if cand.replace('/', '\\').lower() == DAPOYAN_HARPOON_RECORD.lower():
            rec = cand
            break
    if rec is None:
        # Only relevant if the Elite Peltast actually got Bloodspear; warn, do not crash.
        print("  [skill_quality] WARN: dapoyan_harpoon soul record not found for cd fix")
        return
    db.set_field(rec, 'skillCooldownTime', DAPOYAN_HARPOON_CD)   # FLOAT field exists
    db._modified.add(rec)


def _self_check_reassignments(db):
    """Scoped fail-loud: every soul THIS wave re-pointed must grant a resolvable Skill_*
    record with itemSkillLevel >= 1 and a resolvable controller (the activation contract,
    scoped to our own edits so it can never trip on unrelated monolith state)."""
    recmap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def resolve(p):
        return recmap.get(str(p).replace('/', '\\').lower().strip()) if p else None

    targets = {t for plan in REASSIGN.values() for (t, _c) in plan.values()
               if t is not STAT_ONLY and t != STAT_ONLY}
    problems = []
    for target in sorted(targets):
        rec = resolve(target)
        if not rec:
            problems.append(f"reassign target missing from db: {target}")
            continue
        cls = _first_value(db.get_field_value(rec, 'Class'))
        if not (isinstance(cls, str) and cls.startswith('Skill_')):
            problems.append(f"{target}: Class {cls!r} is not Skill_* (non-castable grant)")
    # every reassigned soul record: level >= 1 + controller resolves
    for rec, rl in _iter_soul_item_records(db):
        isk = _first_value(db.get_field_value(rec, 'itemSkillName'))
        if not (isinstance(isk, str) and _basename(isk) in
                {_basename(t) for t in targets}):
            continue
        lvl = _first_value(db.get_field_value(rec, 'itemSkillLevel'))
        try:
            if lvl is None or int(lvl) < 1:
                problems.append(f"{rec}: itemSkillLevel {lvl!r} < 1 (grant inactive)")
        except (TypeError, ValueError):
            problems.append(f"{rec}: itemSkillLevel {lvl!r} not an int")
        ctl = _first_value(db.get_field_value(rec, 'itemSkillAutoController'))
        if isinstance(ctl, str) and ctl.strip() and not resolve(ctl):
            problems.append(f"{rec}: controller {ctl} does not resolve")
    if problems:
        for p in problems[:20]:
            print(f"  SKILL-QUALITY SELF-CHECK OFFENDER: {p}")
        raise SystemExit(f"skill_quality self-check FAILED: {len(problems)} issue(s)")


def verify_diversity(db):
    """FAIL-LOUD roster-locked granted-skill diversity gate (spec section 5). Collapses
    n/e/l + pcsafe/plain by skill basename, counts DISTINCT soul identities (itemNameTag):
      1. EXEMPT summon skills (legitimately shared).
      2. For each ALLOW family skill: grantor tag-set must be a SUBSET of its roster
         (any tag NOT in the roster = a new soul silently joined a family -> FAIL).
      3. Every other non-exempt skill: FAIL if it exceeds MAX_SHARED; WARN at 6..MAX_SHARED.
    Callable standalone by the registry gate phase AND run at the end of apply()."""
    allow = dict(ALLOW)
    gs_roster = set(getattr(_svc, '_GS_ROSTER_TAGS', ())) if _svc is not None else set()
    if gs_roster:
        allow['cyclops_groundsmash.dbr'] = gs_roster

    skill_ids = {}   # skill basename -> set(itemNameTag)
    for rec, rl in _iter_soul_item_records(db):
        isk = _first_value(db.get_field_value(rec, 'itemSkillName'))
        if not (isinstance(isk, str) and isk.strip()):
            continue
        tag = str(_first_value(db.get_field_value(rec, 'itemNameTag')))
        skill_ids.setdefault(_basename(isk), set()).add(tag)

    def is_summon(sk):
        return (sk in SUMMON_EXEMPT or sk.endswith('_summon.dbr') or 'summon' in sk
                or 'skeleton' in sk or 'skelly' in sk)

    problems = []
    warns = []
    for sk, tags in sorted(skill_ids.items(), key=lambda x: -len(x[1])):
        if is_summon(sk):
            continue
        if sk in allow:
            bad = sorted(t for t in tags if t not in allow[sk])
            if bad:
                problems.append(f"'{sk}' granted by {len(bad)} soul(s) OUTSIDE its locked "
                                f"roster: {bad[:12]}")
            continue
        if len(tags) > MAX_SHARED:
            problems.append(f"'{sk}' mass-assigned to {len(tags)} distinct soul identities "
                            f"(> MAX_SHARED {MAX_SHARED}) - unrostered filler")
        elif len(tags) >= 6:
            warns.append(f"{sk}={len(tags)}")

    if warns:
        print("  [skill_quality diversity] approaching-cap (6..%d, non-fatal): %s"
              % (MAX_SHARED, ", ".join(warns)))
    if problems:
        for p in problems:
            print(f"  GRANTED-SKILL-DIVERSITY OFFENDER: {p}")
        raise SystemExit(f"skill_quality diversity gate FAILED: {len(problems)} issue(s) "
                         f"(see offenders above)")
    locked = ", ".join(f"{_basename(k)}={len(skill_ids.get(k, ()))}/{len(v)}"
                       for k, v in sorted(allow.items()))
    print(f"  skill_quality diversity gate OK: {len(allow)} family skills locked to roster "
          f"[{locked}]; no unrostered skill > {MAX_SHARED}")


def apply(db, tags=None):
    """Registry entry point. Reassign off-theme/over-shared filler -> identity-true procs
    (or stat-only), enrich the stat-only mooks with amgoz downsides, fix the dapoyan_harpoon
    cooldown, re-run the idempotent castability wave for the changed grants, then run the
    fail-loud self-check of THIS wave's own reassignments. `tags` is accepted for contract
    parity but untouched (no Text.arc change - every pick reuses an existing display name).

    The roster-locked diversity GATE does NOT run here. It runs in verify() below,
    which the registry calls in its POST-FINALIZATION verify phase (step 4), AFTER
    apply_svc_patches.run_registry_gates has de-filled Ground Smash and renamed the
    wave29 placeholder-tag souls (satyrmagi/satyrspiritcaller: tagSoul1 -> real tags).
    Running the gate here (apply time, mid-registry) would fail loud on those ordering
    artifacts before the finalization clears them - the build37 blocker. NOTE: the gate
    is NOT disabled by this - it is RELOCATED; build_svc_database.py MUST call
    patches.run_registry_verifies(db, tags) after run_registry_gates (it does)."""
    print(f"\n[patch:{MODULE_NAME}] granted-skill quality pass (build37 / BACKLOG #31)")
    n_re, n_stat = _apply_reassignments(db)
    n_enrich = _apply_enrichment(db)
    _apply_dapoyan_cooldown(db)
    print(f"  reassigned {n_re} soul grant(s) to identity-true procs; {n_stat} soul "
          f"record(s) made stat-only; {n_enrich} soul record(s) amgoz-enriched")

    # Castability (spec section 3): belt-and-suspenders. Every pick is already castable
    # (mirrors a working grantor), but the monolith castability wave is idempotent and
    # guarantees pcsafe + Enemy-controller autoTargetRadius parity for the changed grants,
    # independent of whether the registry gate phase re-runs it.
    if _svc is not None:
        _svc._fix_granted_skill_castability(db)

    # Scoped self-check of THIS wave's reassignments only (targets resolve, level >= 1,
    # controller resolves). Valid at apply time (depends only on the reassign+castability
    # just done, not on run_registry_gates finalization). The db-wide roster diversity
    # gate is deferred to verify() (see the docstring).
    _self_check_reassignments(db)
    return tags


def verify(db, tags=None):
    """POST-FINALIZATION registry verify hook (patches.run_registry_verifies, step 4).

    Runs the fail-loud roster-locked granted-skill diversity gate over the FINAL
    assembled db - AFTER run_registry_gates has de-filled Ground Smash (clearing the
    8 dev-soul cyclops_groundsmash grants) and renamed the wave29 placeholder-tag
    souls (satyrmagi -> tagSVCSoulSatyrMagi in the firefragmentnova roster;
    satyrspiritcaller -> tagSVCSoulSatyrSpiritcaller in the lifedrain roster). Those
    three offenders are ORDERING ARTIFACTS cleared by construction here; the genuine
    family gaps are held by the ALLOW roster. Fail-loud (SystemExit) on any real
    violation, which run_registry_verifies propagates to abort the build."""
    verify_diversity(db)
    return tags
