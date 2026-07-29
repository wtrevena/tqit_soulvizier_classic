r"""toxeus_hunt_encounter - THE ENDLESS HUNT (b98, Will 2026-07-28).

RENAMED from `toxeus_legendary_stalker` under the RETIREMENT PROTOCOL. The old
module NAME asserted something that is not true of the encounter any more (and was
only ever true of ONE of his two spawn mechanisms). The RECORDS keep their shipped
names - `q_toxeus_hunt_lone` proxy and pool are NOT renamed and NOT deleted (the
q_bloodtoxeus_lone_50 lesson: an "obviously stale" name was load-bearing).

--------------------------------------------------------------------------------
WHAT WAS WRONG WITH THE OLD NAME (ground truth, deployed arz md5 9f98e3e8)
--------------------------------------------------------------------------------
The Endless Hunt has TWO spawn mechanisms and only ONE was ever difficulty-gated:

 (A) THE ROAMING SWEEP (tools/patches/toxeus_suite.py PART C) - NOT gated at all.
     `um_toxeus_hunt_99` is a nameN member of 346 ProxyPools, 344 of them under
     `records\xpack\proxieshades\pools\`. 540 proxies reference those pools, and
     they span the WHOLE Immortal Throne expansion, not Hades:
         area001 Rhodes 70 | area002 Medea's Grove 76 | area003 Epirus 55
         area004 Styx 78   | area005 Plains of Judgement 79
         area006 Tower of Judgement 49 | area007 Elysian Fields 82
         area008 Hades Palace 49
     365 of those 540 proxies define ONLY `poolN` (which resolves on all three
     difficulties), 174 define `poolN` + `poolEpicN`, and ZERO define
     `poolLegendaryN`. So the roam has ALWAYS been Normal + Epic + Legendary.
     THE ROOT OF THE "HADES-ONLY" MYTH IS ONE COMMENT: toxeus_suite.py's
     `_LS_ALLOW_PREFIX = ('records\\xpack\\proxieshades',)` was annotated "Hades
     trash pools ONLY". `records\xpack\proxieshades\` is the whole Immortal Throne
     proxy namespace and the base game filed RHODES inside it as area001. Every
     downstream claim inherited that error. The comment is corrected in place.

 (B) THE FIXED PROXY `records\drxmap\proxy\q_toxeus_hunt_lone.dbr` - genuinely
     Legendary-only until this module: pool1='' / weight1=0 / poolEpic1 ABSENT /
     poolLegendary1 = the single-member pool.

Will met the ROAMING Hunt in Rhodes on Epic. That was never a defect; it was
mechanism (A) working as built. What made him invisible on Normal is RARITY, not a
gate: his slot carries weight 1 against pool totals of 36,001 to 660,001, i.e.
1/36,001 (best) to 1/660,001 (worst), median about 1/66,667.

--------------------------------------------------------------------------------
WHAT THIS MODULE SHIPS
--------------------------------------------------------------------------------
1. THE GATE COMES OFF THE FIXED ENCOUNTER (R-80 scope): pool1 and poolEpic1 now
   BOTH name the Hunt's pool explicitly, so the guaranteed Hades Palace encounter
   exists on Normal, Epic and Legendary. `poolEpic1` is set EXPLICITLY rather than
   left to fall back on `pool1`, because "poolEpic1 absent" is the Hydra gate
   idiom and reads as deliberate gating intent to the next maintainer.
   `poolLegendary1` is left naming the base pool here and is REPOINTED at the
   endless-pursuit variant pool by `toxeus_hunt_endless` (registered later).

2. THE RITE OF THE UNDIVIDED DROPS OFF HIM (R-82), mirroring the Enslaver EXACTLY:
   chanceToEquipMisc4=100 / chanceToEquipMisc4Item1=100 /
   lootMisc4Item1 = svc_rite_guaranteed on all three tiers. The Hunt had NO Misc4
   slot at all. R-13 reads the champion Rite drop as guaranteed-on-kill; the
   Enslaver's simple FixedWeight form is used (not the Devourer's master table -
   the Hunt has no rant scroll to co-schedule). The RECIPE still demands the three
   LEGENDARY souls (asserted in verify()), so the formula dropping on Normal/Epic
   cannot short-circuit R-8's gate.

3. HE CARRIES A SPEAR (R-83) - "Runbreaker", a bespoke 3-tier signature weapon on
   the Devourer's Crimson Verdict / Veinrender pattern, guaranteed in his RightHand
   slot so he both WIELDS and DROPS it. See THE ANIMATION PROOF below.

4. HE STOPS BEING AN ENSLAVER CLONE (R-84). Ground truth: 9 of his 12 skill slots
   were the SAME SKILL RECORD as the Enslaver's, and his only 3 non-shared slots
   are the globalproperties_{normal,epic,legendary}01 STAT hooks. He had ZERO
   unique active abilities. The three cast slots that overlapped the Enslaver
   (flashpowder / netherstrike / lifedrain) become a pursuit kit built from his own
   identity - mark at medium range, reach at long range, kill at short range.
   `toxeus_bladestorm` (the Toxeus family signature verb) and every passive are
   KEPT - this is an edit of 3 slots, never a stripping of his kit.

--------------------------------------------------------------------------------
THE ANIMATION PROOF (the brief's "if the spear needs an animation set, prove the
rig supports it")
--------------------------------------------------------------------------------
GROUND TRUTH: `um_toxeus_hunt_99` ships spearAttackIdleAnim, spearBuffSelfAnim1,
spearBuffOtherAnim1, spearSpellAttackAnim and spearWalkAnim - and is MISSING
spearAttackAnim1/2/3, spearRunAnim, spearDieAnim1, spearStunAnim. Equipping a spear
without those means he walks with it and never swings it.

The ShadowStalker rig ships NO spear animation of its own (13 .anm files, 0 spear),
so the attack poses must be borrowed. Cross-rig spear animation is the base game's
NORM, not an exception: 672 shipped records play a spear attack anim authored for a
different rig, versus 247 same-rig. This mod already does it on the Toxeus family's
own skeleton rig - `records\skills\soulskills\pets\boneash_1.dbr` carries a
complete Maenad-spear block on a RevenantFire mesh.

THE GRAFT IS DELIBERATELY MINIMAL - only what the rig genuinely lacks is borrowed:
  * spearAttackAnim1/2/3 <- Maenad_Spear_Att{Alpha,Beta,Gamma}  (BORROWED; the
    boneash_1 in-mod precedent, and the largest cross-rig spear donor in the
    shipped data)
  * spearRunAnim / spearDieAnim1 / spearStunAnim <- copied from the animation this
    RECORD ALREADY BINDS for its other weapon classes (sHanded), read at build time
    rather than hardcoded so it can never desync from the record.
So exactly THREE animations are unproven-by-eye instead of eight, and each of the
three is referenced by other shipped records (asserted in verify(), which is a
provenance proof, not an existence guess).
WARNING, PLAYER-SURFACE, HONEST: Maenad-spear-on-SHADOWSTALKER has no shipped
instance. This is a VISUAL check only Will's eye can settle (BL-b98-DEBT-1). Ranked
fallbacks if it looks wrong: MedusaMinion_Spear (103 users, humanoid), then
Machae_Spear (same expansion, same underworld).

--------------------------------------------------------------------------------
CASTABILITY LAW (the Ephialtes / boss_skill_fix / coldworm lesson)
--------------------------------------------------------------------------------
A monster skill whose `skillSpecialAnimationName` is not bound by the caster has no
playable animation, so the engine never starts it. GROUND TRUTH: `um_toxeus_hunt_99`
binds ZERO `unarmedSpecialAnimRef` slots - and so do the Enslaver and the Devourer.
Every skill this module adds therefore declares NO `skillSpecialAnimationName`
whatsoever, which is exactly the law `toxeus_champion_kits` already ships for these
champions. verify() proves it fail-loud.
NOTE, reported not silently claimed: the skill this module REPLACES at
specialAttack3, `netherstrike`, declares skillSpecialAnimationName='LethalStrike'
which the Hunt does not bind - so that slot was very likely dead already. Replacing
it is a repair as well as a differentiation.

--------------------------------------------------------------------------------
WHAT THIS MODULE DELIBERATELY DOES NOT DO
--------------------------------------------------------------------------------
* distressCallGroup is LEFT AT 'Skeleton'. The design brief called this a clone
  leftover ("a Demon-race boss calling the Skeleton distress group"). GROUND TRUTH
  SAYS OTHERWISE: all 28 shipped ShadowStalker-mesh monsters are race=Demon AND
  distressCallGroup='Skeleton', including the Enslaver's own marauders - it is the
  base game's convention for this rig, not a leak. There is also NO 'Demon' group in
  the DB (19 groups exist; Demon is not one), so "fixing" it would invent a group of
  one member and cut him out of the shadowstalker distress network. Reported, not
  changed.
* No mesh change to the Enslaver or the Devourer. That work belongs to the
  green-diff lane (b92) and turns on a Will answer.
* No roaming-sweep rate change. The roam rate is a WILL-VETO rate decision (R-18
  forbids the equivalent on the Enslaver); the numbers are in the report.
"""

import re as _re
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Endless Hunt encounter (R-80/R-82/R-83/R-84): ungate, Rite, spear, pursuit kit"

DATA_TYPE_INT = 0
DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2

# -- the shipped records this module owns (NAMES KEPT - retirement protocol) --
_HUNT = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
_STALKER_POOL = r'records\drxmap\proxy\pools\q_toxeus_hunt_lone.dbr'
_STALKER_PROXY = r'records\drxmap\proxy\q_toxeus_hunt_lone.dbr'
_STALKER_MESH = r'Creatures\Monster\ShadowStalker\ShadowStalker.msh'
_STALKER_SCALE = 1.9

# -- R-82: the Rite of the Undivided (the EXACT table the Enslaver drops) ----
_RITE_TABLE = r'records\item\loottables\svc\svc_rite_guaranteed.dbr'
_EOAT_FORMULA = r'records\drxitem\supra\recipes\svc_toxeus_eoat_formula.dbr'

# -- R-83: the spear ---------------------------------------------------------
_SPEAR_DONOR = r'records\drxitem\supra\wep_spear.dbr'      # supra-tier calibre donor
# THE build30-F3 CORRECTED RIG. The donor's SHIPPED mesh is
# `DRX\meshes\supra\wep_spear.msh`, which embeds the XPack-scoped shader
# XPack/Shaders/standardblendedglowstatic.ssh that the engine can only resolve in
# Resources\XPack\Shaders.arc - where it does not exist. The result is an INVISIBLE
# weapon, and F3 (`apply_svc_patches._fix_wave30_render_and_refs`) repoints the donor
# to this base rig and strips its DRX skin. F3 runs in run_registry_gates, i.e. AFTER
# every registry module, so a clone taken here inherits the BROKEN pre-F3 state and F3
# never reaches it (it repoints exactly two records BY NAME). The corrected rig is
# therefore applied explicitly on the clones, and verify() asserts each tier's mesh
# equals the donor's FINAL post-F3 mesh so this can never silently desync from F3.
_SPEAR_MESH = r'Items\EquipmentWeapon\Spear\Default\RSpear14B.msh'
_INVISIBLE_MESH_PREFIX = 'drx\\meshes\\supra'
_ANIM_DONOR = r'records\skills\soulskills\pets\boneash_1.dbr'   # in-mod spear-block precedent
_SPEAR = {t: r'records\item\equipmentweapon\spear\svc_%s_runbreaker.dbr' % t for t in 'nel'}
_SPEAR_GUAR = {t: r'records\item\loottables\svc\runbreaker_guaranteed_%s.dbr' % t for t in 'nel'}
_SPEAR_NAME_TAG = 'tagSVCwpnRunbreaker'
# tier -> (itemClassification, itemLevel, levelRequirement, itemCost record, phys min, phys max)
_SPEAR_TIERS = {
    'n': ('Rare', 40, 35, r'records\game\itemcost_unique_primary.dbr', 78.0, 118.0),
    'e': ('Epic', 68, 63, r'records\game\itemcost_uniqueepic_primary.dbr', 132.0, 196.0),
    'l': ('Legendary', 95, 90, r'records\game\itemcost_uniquelegendary_primary.dbr', 245.0, 265.0),
}
# The 3 BORROWED spear attack poses (the rig ships none of its own).
_SPEAR_ATT_ANIMS = (
    r'Creatures\Monster\Maenad\ANM\Maenad_Spear_AttAlpha.anm',
    r'Creatures\Monster\Maenad\ANM\Maenad_Spear_AttBeta.anm',
    r'Creatures\Monster\Maenad\ANM\Maenad_Spear_AttGamma.anm',
)
# spear slot -> the slot on the SAME record whose animation is reused verbatim.
_SPEAR_SELF_ANIMS = {
    'spearRunAnim': 'sHandedRunAnim',
    'spearDieAnim1': 'sHandedDieAnim1',
    'spearStunAnim': 'sHandedStunAnim',
}

# -- R-84: the pursuit kit (donors are all DB-verified, all NO special anim) --
_D_MARK = r'records\skills\hunting\studyprey.dbr'
_D_MARK_BUFF = r'records\skills\hunting\studypreybuff.dbr'
_D_LANCE = r'records\skills\stealth\drxpet\drx_stalker_skills\zshadowblast.dbr'
_D_SWEEP = r'records\skills\stealth\drxflashpowder.dbr'

_MARK = r'records\skills\monster skills\attack_direct\svc_hunt_quarrysmark.dbr'
_MARK_BUFF = r'records\skills\monster skills\attack_direct\svc_hunt_quarrysmark_buff.dbr'
_LANCE = r'records\skills\monster skills\attack_projectile\svc_hunt_longreach.dbr'
_SWEEP = r'records\skills\monster skills\attack_radius\svc_hunt_rundown.dbr'

_NEW_SKILLS = (_MARK, _MARK_BUFF, _LANCE, _SWEEP)
_EXPECT_CLASS = {
    _MARK: 'Skill_AttackBuffRadius',
    _MARK_BUFF: 'SkillBuff_Debuf',
    _LANCE: 'Skill_AttackSpellChaos',
    _SWEEP: 'Skill_AttackRadius',
}
# the skills this module RETIRES from his cast slots (kept in the DB - shared records)
_REPLACED = {
    '': r'records\skills\stealth\flashpowder.dbr',
    '3': r'records\skills\monster skills\attack_melee\netherstrike.dbr',
    '4': r'records\skills\spirit\lifedrain.dbr',
}
# cast slot suffix -> (new skill, chance, range band)
_CAST_PLAN = {
    '': (_MARK, 45.0, 'MediumRange'),
    '3': (_LANCE, 30.0, 'LongRange'),
    '4': (_SWEEP, 30.0, 'ShortRange'),
}

# widened range bands: a two-handed reach weapon plus a long-range lance.
# (was short 0-4 / medium 4-8 / long 8-15, tuned for a one-handed ambusher)
_RANGE_BANDS = {
    'shortRangeMin': 0.0, 'shortRangeMax': 5.0,
    'mediumRangeMin': 5.0, 'mediumRangeMax': 12.0,
    'longRangeMin': 12.0, 'longRangeMax': 22.0,
}


# =============================================================================
# helpers
# =============================================================================
def _norm(p):
    return str(p).replace('/', '\\').lower()


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) and v else v


def _del_field(db, rec, name):
    """Remove a field slot entirely (NEVER blank a live ref to '' - the
    B-TOXEUS-2 zero-precedent loader-abort law)."""
    ff = db.get_fields(rec)
    if not ff:
        return False
    hit = False
    for k in list(ff):
        if k.split('###')[0] == name:
            del ff[k]
            hit = True
    if hit:
        db._modified.add(rec)
    return hit


def _require(db, *recs):
    missing = [r for r in recs if not db.has_record(r)]
    if missing:
        raise SystemExit(
            "[toxeus_hunt_encounter] required record(s) missing from the db: %s"
            % missing)


def _set(db, rec, field, value, dtype):
    """Set a field, passing dtype ONLY when the field is genuinely NEW on the
    record (the cloned-record dtype-corruption trap)."""
    if db.get_field_value(rec, field) is None:
        db.set_field(rec, field, value, dtype)
    else:
        db.set_field(rec, field, value)


# =============================================================================
# (1) the fixed encounter: pool + proxy, gate OFF (R-80 scope)
# =============================================================================
def _ensure_pool(db):
    from apply_svc_patches import _ensure_record
    PL = _STALKER_POOL
    _ensure_record(db, PL, r'database\Templates\ProxyPool.tpl')
    S, I, F = DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT
    db.set_field(PL, 'templateName', r'database\Templates\ProxyPool.tpl', S)
    db.set_field(PL, 'FileDescription',
                 'Fixed Endless Hunt encounter, all difficulties (1)', S)
    db.set_field(PL, 'name1', _HUNT, S)
    db.set_field(PL, 'weight1', 10, I)
    db.set_field(PL, 'spawnMin', 1, I)
    db.set_field(PL, 'spawnMax', 1, I)
    db.set_field(PL, 'championChance', 0.0, F)
    db.set_field(PL, 'championMin', 0, I)
    db.set_field(PL, 'championMax', 0, I)
    db._modified.add(PL)


def _author_proxy(db):
    """Author (first build) or re-gate (idempotent) the fixed encounter proxy.

    R-80 SCOPE: the MONSTER is available on all three difficulties, so pool1 AND
    poolEpic1 both name his pool. poolLegendary1 also names it here; the
    toxeus_hunt_endless module repoints it at the endless-pursuit variant pool.
    """
    import apply_svc_patches as asp
    donor_proxy = asp._BT_PROXY          # q_bloodtoxeus_lone (gate-proven donor)
    _require(db, donor_proxy, _HUNT)

    if not db.has_record(_STALKER_PROXY):
        db.clone_record(donor_proxy, _STALKER_PROXY)
    P = _STALKER_PROXY
    S, I = DATA_TYPE_STRING, DATA_TYPE_INT

    # pool1/weight1 exist on the donor -> value-only override (dtype preserved).
    db.set_field(P, 'pool1', _STALKER_POOL)
    db.set_field(P, 'weight1', 10)
    _set(db, P, 'poolEpic1', _STALKER_POOL, S)
    _set(db, P, 'weightEpic1', 10, I)
    _set(db, P, 'poolLegendary1', _STALKER_POOL, S)
    _set(db, P, 'weightLegendary1', 10, I)
    db.set_field(P, 'mesh', _STALKER_MESH)
    db.set_field(P, 'scale', _STALKER_SCALE)
    db._modified.add(P)

    already = any(spec.get('proxy') == _STALKER_PROXY
                  for spec in asp._MOD_AUTHORED_SPAWN_PROXIES)
    if not already:
        asp._MOD_AUTHORED_SPAWN_PROXIES.append({
            'proxy': _STALKER_PROXY,
            'pool': _STALKER_POOL,
            'main_monster': _HUNT,
            'name': 'q_toxeus_hunt_lone (fixed Endless Hunt encounter, N/E/L)',
        })
    print("  fixed encounter: pool1 + poolEpic1 + poolLegendary1 all name the "
          "Hunt's pool (Legendary-only gate REMOVED, R-80); registered for "
          "spawn-eligibility.")


# =============================================================================
# (2) R-82: the Rite of the Undivided drops off him too
# =============================================================================
def _wire_rite(db):
    _require(db, _RITE_TABLE, _EOAT_FORMULA)
    lootname = _gv1(db, _RITE_TABLE, 'lootName1')
    if _norm(lootname) != _norm(_EOAT_FORMULA):
        raise SystemExit(
            "[toxeus_hunt_encounter] %s no longer names the Rite formula "
            "(lootName1=%r); refusing to wire a Misc4 slot at 100 percent onto "
            "something else." % (_RITE_TABLE, lootname))
    F, I, S = DATA_TYPE_FLOAT, DATA_TYPE_INT, DATA_TYPE_STRING
    _set(db, _HUNT, 'chanceToEquipMisc4', 100.0, F)
    _set(db, _HUNT, 'chanceToEquipMisc4Item1', 100, I)
    _set(db, _HUNT, 'lootMisc4Item1', [_RITE_TABLE] * 3, S)
    db._modified.add(_HUNT)
    print("  R-82: Rite of the Undivided wired to Misc4 at 100 percent on all 3 "
          "tiers (mirrors the Enslaver exactly; he had NO Misc4 slot before).")


# =============================================================================
# (3) R-83: Runbreaker, his signature spear
# =============================================================================
def _build_spear_items(db, tags):
    _require(db, _SPEAR_DONOR)
    from apply_svc_patches import _ensure_record
    S, I, F = DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT
    for t in 'nel':
        item = _SPEAR[t]
        cls, ilvl, lreq, cost, pmin, pmax = _SPEAR_TIERS[t]
        if not db.has_record(item):
            db.clone_record(_SPEAR_DONOR, item)
        # value-only overrides on a cloned record: NEVER pass dtype here.
        db.set_field(item, 'itemNameTag', _SPEAR_NAME_TAG)
        db.set_field(item, 'itemClassification', cls)
        db.set_field(item, 'itemLevel', ilvl)
        db.set_field(item, 'levelRequirement', lreq)
        db.set_field(item, 'itemCostName', cost)
        db.set_field(item, 'offensivePhysicalMin', pmin)
        db.set_field(item, 'offensivePhysicalMax', pmax)
        db.set_field(item, 'FileDescription',
                     'Runbreaker - the Endless Hunt signature spear (%s)' % t.upper())
        # HIS identity is SPEED (run 1.8 / attack 1.3 - the fast champion), so his
        # own spear does NOT ship the supra spear's CharacterAttackSpeedSlow.
        # 'CharacterAttackSpeedAverage' + 0.25 are both inside the shipped spear
        # envelope (4 spears carry the tag; 0.25 is the fastest shipped value).
        # ONE-LINE WILL-VETO: flipping these two back to Slow/0.15 makes him the
        # heavy reach-hunter instead. Nothing else depends on the choice.
        db.set_field(item, 'characterBaseAttackSpeedTag', 'CharacterAttackSpeedAverage')
        db.set_field(item, 'characterBaseAttackSpeed', 0.25)
        # FIX-UPSTREAM (BL-103) - TWO defects the donor still carries AT THIS POINT
        # IN THE BUILD, both of which repoint the donor BY NAME later and so would
        # never reach a clone taken here:
        #  (a) build30 F3 (runs in run_registry_gates, after every registry module):
        #      the invisible-weapon DRX mesh + its DRX-only UV skin;
        #  (b) fx_dangling_cleanup (the last content module): the leftover
        #      `bumpTexture` companion of that same DRX skin.
        # Applying both here is what stops Runbreaker shipping as an invisible spear.
        db.set_field(item, 'mesh', _SPEAR_MESH)
        _del_field(db, item, 'baseTexture')
        _del_field(db, item, 'bumpTexture')
        db._modified.add(item)

        guar = _SPEAR_GUAR[t]
        _ensure_record(db, guar, r'Database\Templates\LootItemTable_FixedWeight.tpl')
        db.set_field(guar, 'templateName',
                     r'Database\Templates\LootItemTable_FixedWeight.tpl', S)
        db.set_field(guar, 'FileDescription',
                     'Runbreaker guaranteed - the Endless Hunt (%s)' % t.upper(), S)
        db.set_field(guar, 'lootName1', item, S)
        db.set_field(guar, 'lootWeight1', 100, I)
        db.set_field(guar, 'brokenRandomizerChance', 0.0, F)
        db.set_field(guar, 'prefixRandomizerChance', 0.0, F)
        db.set_field(guar, 'suffixRandomizerChance', 0.0, F)
        db._modified.add(guar)

    # PLAYER SURFACE: the display name. One tag across all 3 tiers, exactly the
    # Veinrender convention (tagSVCwpnVeinRender is shared by n/e/l).
    tags[_SPEAR_NAME_TAG] = 'Runbreaker'
    print("  R-83: Runbreaker authored (3 tiers) + 3 guaranteed loot tables; "
          "name tag %s." % _SPEAR_NAME_TAG)


def _graft_spear_anims(db):
    """Give the ShadowStalker rig a working spear block. See THE ANIMATION PROOF."""
    _require(db, _ANIM_DONOR)
    S = DATA_TYPE_STRING
    donor_att = [_gv1(db, _ANIM_DONOR, 'spearAttackAnim%d' % i) for i in (1, 2, 3)]
    for i, (want, have) in enumerate(zip(_SPEAR_ATT_ANIMS, donor_att), start=1):
        if _norm(have) != _norm(want):
            raise SystemExit(
                "[toxeus_hunt_encounter] the in-mod spear-block precedent "
                "%s no longer carries the expected spearAttackAnim%d "
                "(got %r, expected %r). Refusing to graft an animation whose "
                "shipped provenance just changed." % (_ANIM_DONOR, i, have, want))
        _set(db, _HUNT, 'spearAttackAnim%d' % i, want, S)

    for spear_slot, self_slot in sorted(_SPEAR_SELF_ANIMS.items()):
        src = _gv1(db, _HUNT, self_slot)
        if not src:
            raise SystemExit(
                "[toxeus_hunt_encounter] %s has no %s to reuse for %s; the "
                "record's own animation table changed shape."
                % (_HUNT, self_slot, spear_slot))
        _set(db, _HUNT, spear_slot, src, S)
    db._modified.add(_HUNT)
    print("  R-83: spear animation block grafted - 3 BORROWED attack poses "
          "(Maenad, boneash_1 precedent) + run/die/stun reused from this "
          "record's own sHanded slots.")


def _wire_spear_to_hunt(db):
    """He WIELDS and DROPS Runbreaker instead of a random one-hander."""
    db.set_field(_HUNT, 'lootRightHandItem1', [_SPEAR_GUAR[t] for t in 'nel'])
    db.set_field(_HUNT, 'chanceToEquipRightHand', 100.0)
    db.set_field(_HUNT, 'chanceToEquipRightHandItem1', 100)
    # the donor's Item5 unique-1H master table would otherwise still roll a
    # non-spear against the guaranteed slot; zero its weight (the slot record
    # itself is left in place - never blank a live ref).
    if db.get_field_value(_HUNT, 'chanceToEquipRightHandItem5') is not None:
        db.set_field(_HUNT, 'chanceToEquipRightHandItem5', 0)
    for f, v in sorted(_RANGE_BANDS.items()):
        db.set_field(_HUNT, f, v)
    db._modified.add(_HUNT)
    print("  R-83: RightHand -> runbreaker_guaranteed_{n,e,l} at 100 percent; "
          "range bands widened for a two-handed reach weapon "
          "(short 0-5 / med 5-12 / long 12-22).")


# =============================================================================
# (4) R-84: the pursuit kit
# =============================================================================
def _build_kit_skills(db):
    _require(db, _D_MARK, _D_MARK_BUFF, _D_LANCE, _D_SWEEP)

    # -- QUARRY'S MARK: he studies you, then you cannot outrun him. ----------
    db.clone_record(_D_MARK_BUFF, _MARK_BUFF)
    B = _MARK_BUFF
    db.set_field(B, 'offensiveSlowRunSpeedMin', [35.0, 42.0, 50.0])
    db.set_field(B, 'offensiveSlowRunSpeedDurationMin', 6.0)
    db.set_field(B, 'offensiveSlowDefensiveAbilityMin', [45.0, 70.0, 100.0])
    db.set_field(B, 'offensiveSlowDefensiveAbilityDurationMin', 6.0)
    db.set_field(B, 'offensiveSlowBleedingMin', [70.0, 130.0, 210.0])
    db.set_field(B, 'offensiveSlowBleedingDurationMin', 6.0)
    db.set_field(B, 'FileDescription',
                 "SVC Endless Hunt: Quarry's Mark debuff (slow + DA shred + bleed)")
    db._modified.add(B)

    db.clone_record(_D_MARK, _MARK)
    db.set_field(_MARK, 'buffSkillName', _MARK_BUFF)
    db.set_field(_MARK, 'skillCooldownTime', 12.0)
    db.set_field(_MARK, 'skillMaxLevel', 3)
    db.set_field(_MARK, 'skillTargetRadius', [5.0, 6.0, 7.0])
    db.set_field(_MARK, 'FileDescription',
                 "SVC Endless Hunt: Quarry's Mark (he has your scent now)")
    db._modified.add(_MARK)

    # -- THE LONG REACH: distance is not safety. -----------------------------
    db.clone_record(_D_LANCE, _LANCE)
    L = _LANCE
    db.set_field(L, 'offensiveColdMin', [110.0, 190.0, 300.0])
    db.set_field(L, 'offensiveColdMax', [150.0, 250.0, 390.0])
    db.set_field(L, 'offensivePierceRatioMin', [35.0, 42.0, 50.0])
    db.set_field(L, 'offensiveSlowRunSpeedMin', [20.0, 25.0, 30.0])
    db.set_field(L, 'offensiveSlowRunSpeedDurationMin', 3.0)
    db.set_field(L, 'skillCooldownTime', 5.0)
    db.set_field(L, 'skillMaxLevel', 3)
    db.set_field(L, 'FileDescription',
                 'SVC Endless Hunt: The Long Reach (cold spectral spear at range)')
    db._modified.add(L)

    # -- RUN THEM DOWN: when he closes, it ends. -----------------------------
    db.clone_record(_D_SWEEP, _SWEEP)
    W = _SWEEP
    db.set_field(W, 'offensivePhysicalMin', [130.0, 230.0, 360.0])
    db.set_field(W, 'offensivePhysicalMax', [175.0, 300.0, 470.0])
    db.set_field(W, 'offensivePierceRatioMin', [40.0, 45.0, 50.0])
    db.set_field(W, 'offensiveSlowBleedingMin', [90.0, 160.0, 250.0])
    db.set_field(W, 'offensiveSlowBleedingDurationMin', 4.0)
    db.set_field(W, 'skillTargetRadius', [4.0, 4.5, 5.0])
    db.set_field(W, 'skillCooldownTime', 8.0)
    db.set_field(W, 'skillMaxLevel', 3)
    db.set_field(W, 'FileDescription',
                 'SVC Endless Hunt: Run Them Down (close-range spear sweep)')
    db._modified.add(W)


def _free_skillname_slot(db, rec, lo=1, hi=30):
    ff = db.get_fields(rec) or {}
    used = set()
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and str(tf.values[0]).strip():
            used.add(int(b[9:]))
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _slot_of(db, rec, skill):
    want = _norm(skill)
    ff = db.get_fields(rec) or {}
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and _norm(tf.values[0]) == want:
            return int(b[9:])
    return None


def _wire_kit(db):
    """Replace the three Enslaver-shared cast slots in place; keep everything else.

    Each retired skill's skillName slot is REUSED by its replacement (so the kit
    stays 12 slots and no slot is orphaned at level 0). The skill RECORDS
    themselves are shared base-game/mod records and are never touched.
    """
    for suffix in sorted(_CAST_PLAN):
        new_skill, chance, band = _CAST_PLAN[suffix]
        old = _REPLACED[suffix]
        cur = _gv1(db, _HUNT, 'specialAttack%sSkillName' % suffix)
        if _norm(cur) not in (_norm(old), _norm(new_skill)):
            raise SystemExit(
                "[toxeus_hunt_encounter] specialAttack%s on %s is %r, expected "
                "the shipped %r (or an already-applied %r). Another writer "
                "changed his kit; refusing to overwrite it blind."
                % (suffix, _HUNT, cur, old, new_skill))
        slot = _slot_of(db, _HUNT, old)
        if slot is None:
            slot = _slot_of(db, _HUNT, new_skill)
        if slot is None:
            slot = _free_skillname_slot(db, _HUNT)
        if slot is None:
            raise SystemExit("[toxeus_hunt_encounter] no skillName slot free on %s" % _HUNT)
        db.set_field(_HUNT, 'skillName%d' % slot, new_skill)
        db.set_field(_HUNT, 'skillLevel%d' % slot, [1, 2, 3])
        db.set_field(_HUNT, 'specialAttack%sSkillName' % suffix, new_skill)
        db.set_field(_HUNT, 'specialAttack%sChance' % suffix, float(chance))
        _set(db, _HUNT, 'specialAttack%sRange' % suffix, band, DATA_TYPE_STRING)
        db._modified.add(_HUNT)
        print("    slot %-2d specialAttack%-2s %-22s -> %-24s @%.0f%% (%s)"
              % (slot, suffix or '1', old.rsplit('\\', 1)[-1],
                 new_skill.rsplit('\\', 1)[-1], chance, band))


# =============================================================================
# entry points
# =============================================================================
def apply(db, tags):
    print("\n=== [toxeus_hunt_encounter] b98 THE ENDLESS HUNT ===")
    _require(db, _HUNT)
    _ensure_pool(db)
    _author_proxy(db)
    _wire_rite(db)
    _build_spear_items(db, tags)
    _graft_spear_anims(db)
    _wire_spear_to_hunt(db)
    _build_kit_skills(db)
    print("  R-84: pursuit kit (the 3 Enslaver-shared cast slots become his own):")
    _wire_kit(db)
    print("=== [toxeus_hunt_encounter] done (verify() runs post-finalization) ===\n")
    return tags


# -- THE GATES (a new content class ships its gate) --------------------------
def _spear_gate(db, mon, label, problems):
    """SPEAR-ANIM-1: if a monster is guaranteed a WeaponHunting_Spear in its
    RightHand slot, its rig must be able to SWING it - spearAttackAnim1..3 plus a
    run/walk/idle/die/stun pose, all naming a non-empty .anm. The Ephialtes lesson
    applied to weapon animation instead of skill animation."""
    tables = db.get_field_value(mon, 'lootRightHandItem1') or []
    if not isinstance(tables, list):
        tables = [tables]
    spear_tiers = 0
    for tbl in tables:
        if not tbl or not db.has_record(tbl):
            continue
        it = _gv1(db, tbl, 'lootName1')
        if it and db.has_record(it) and _gv1(db, it, 'Class') == 'WeaponHunting_Spear':
            spear_tiers += 1
    if not spear_tiers:
        problems.append(
            "%s: lootRightHandItem1 no longer resolves to a WeaponHunting_Spear "
            "on any tier (%s) - the spear identity was silently dropped"
            % (label, [str(t).rsplit('\\', 1)[-1] for t in tables]))
        return
    if spear_tiers != 3:
        problems.append("%s: only %d/3 RightHand tiers resolve to a spear"
                        % (label, spear_tiers))
    needed = ['spearAttackAnim1', 'spearAttackAnim2', 'spearAttackAnim3',
              'spearRunAnim', 'spearWalkAnim', 'spearAttackIdleAnim',
              'spearDieAnim1', 'spearStunAnim']
    for f in needed:
        v = _gv1(db, mon, f)
        if not v or not str(v).strip().lower().endswith('.anm'):
            problems.append(
                "%s: wields a spear but %s=%r - the rig has no playable spear "
                "animation for that slot (SPEAR-ANIM-1)" % (label, f, v))


def _anim_provenance(db, problems):
    """The 3 BORROWED poses must each be referenced by at least one OTHER shipped
    record. Provenance, not a guess that the .anm file exists."""
    want = dict((_norm(a), 0) for a in _SPEAR_ATT_ANIMS)
    for name in db.record_names():
        if name == _HUNT:
            continue
        ff = db.get_fields(name)
        if not ff:
            continue
        for k, tf in ff.items():
            if not k.split('###')[0].startswith('spearAttackAnim'):
                continue
            for v in (tf.values or []):
                n = _norm(v)
                if n in want:
                    want[n] += 1
    for a in _SPEAR_ATT_ANIMS:
        if want[_norm(a)] < 1:
            problems.append(
                "SPEAR-ANIM-1 provenance: %s is referenced by NO other shipped "
                "record, so nothing proves the .anm exists" % a)


def verify(db, tags=None):
    """POST-FINALIZATION fail-loud gates."""
    problems = []

    # --- (A) the fixed encounter resolves on ALL THREE difficulties (R-80) --
    if not db.has_record(_STALKER_PROXY):
        problems.append("proxy missing: %s" % _STALKER_PROXY)
    else:
        for f in ('pool1', 'poolEpic1', 'poolLegendary1'):
            v = _gv1(db, _STALKER_PROXY, f)
            if not v:
                problems.append(
                    "R-80: %s %s is EMPTY - the fixed Endless Hunt encounter does "
                    "not resolve on that difficulty. Will's ruling put the monster "
                    "on Normal, Epic AND Legendary." % (_STALKER_PROXY, f))
            elif not db.has_record(v):
                problems.append("%s %s -> %s does not resolve" % (_STALKER_PROXY, f, v))
        for f in ('weight1', 'weightEpic1', 'weightLegendary1'):
            w = _gv1(db, _STALKER_PROXY, f)
            if not w or int(w) <= 0:
                problems.append("%s %s=%r (must be > 0)" % (_STALKER_PROXY, f, w))
    if not db.has_record(_STALKER_POOL):
        problems.append("pool missing: %s" % _STALKER_POOL)
    else:
        if _norm(_gv1(db, _STALKER_POOL, 'name1')) != _norm(_HUNT):
            problems.append("pool name1 != %s" % _HUNT)
        for i in range(2, 19):
            if _gv1(db, _STALKER_POOL, 'name%d' % i):
                problems.append("pool has an extra member name%d (single-member pool)" % i)

    # --- (B) R-82: the Rite drops, and the RECIPE still gates on LEGENDARY --
    if abs(float(_gv1(db, _HUNT, 'chanceToEquipMisc4') or 0.0) - 100.0) > 0.001:
        problems.append("R-82: %s chanceToEquipMisc4=%r (must be 100)"
                        % (_HUNT, _gv1(db, _HUNT, 'chanceToEquipMisc4')))
    m4 = db.get_field_value(_HUNT, 'lootMisc4Item1') or []
    m4 = m4 if isinstance(m4, list) else [m4]
    if len(m4) != 3 or any(_norm(x) != _norm(_RITE_TABLE) for x in m4):
        problems.append("R-82: %s lootMisc4Item1=%r (must be the Rite table on all "
                        "3 tiers)" % (_HUNT, m4))
    if db.has_record(_EOAT_FORMULA):
        for i in (1, 2, 3):
            r = _gv1(db, _EOAT_FORMULA, 'reagent%dBaseName' % i)
            if not r or not str(r).lower().endswith('_l.dbr'):
                problems.append(
                    "R-82 GATE: the End of All Things formula's reagent%d is %r - "
                    "it must stay a LEGENDARY (_l) soul. The formula item is now "
                    "obtainable on Normal/Epic, so the LEGENDARY gate has to live "
                    "on the recipe or R-8 is broken." % (i, r))
    else:
        problems.append("R-82 GATE: the EoAT formula record is missing (%s)" % _EOAT_FORMULA)

    # --- (C) R-83: the spear, its items and its animations ------------------
    for t in 'nel':
        item, guar = _SPEAR[t], _SPEAR_GUAR[t]
        if not db.has_record(item):
            problems.append("R-83: spear tier missing: %s" % item)
            continue
        if _gv1(db, item, 'Class') != 'WeaponHunting_Spear':
            problems.append("R-83: %s Class=%r != WeaponHunting_Spear"
                            % (item, _gv1(db, item, 'Class')))
        if _gv1(db, item, 'itemNameTag') != _SPEAR_NAME_TAG:
            problems.append("R-83: %s itemNameTag=%r != %s"
                            % (item, _gv1(db, item, 'itemNameTag'), _SPEAR_NAME_TAG))
        for f in ('bumpTexture', 'baseTexture'):
            if _gv1(db, item, f):
                problems.append("R-83: %s carries the build30-F3 DRX-only skin %s "
                                "(it fits only the DRX mesh)" % (item, f))
        m = _norm(_gv1(db, item, 'mesh'))
        if m.startswith(_INVISIBLE_MESH_PREFIX):
            problems.append(
                "R-83 INVISIBLE WEAPON: %s mesh=%r is the build30-F3 class - a "
                "DRX supra mesh embedding an XPack-scoped shader the engine cannot "
                "resolve, so the spear renders INVISIBLE in his hand." % (item, m))
        donor_mesh = _norm(_gv1(db, _SPEAR_DONOR, 'mesh')) if db.has_record(_SPEAR_DONOR) else None
        if donor_mesh and m != donor_mesh:
            problems.append(
                "R-83: %s mesh=%r != the FINAL (post-F3) supra spear mesh %r. "
                "Runbreaker must track whatever rig F3 settles on, or the two "
                "silently diverge." % (item, m, donor_mesh))
        if not db.has_record(guar):
            problems.append("R-83: guaranteed table missing: %s" % guar)
        elif _norm(_gv1(db, guar, 'lootName1')) != _norm(item):
            problems.append("R-83: %s lootName1 != %s" % (guar, item))
    if tags is not None and _SPEAR_NAME_TAG not in tags:
        problems.append("R-83 PLAYER SURFACE: %s is not in the Text tag set, so "
                        "Runbreaker would show a raw tag in game" % _SPEAR_NAME_TAG)
    _spear_gate(db, _HUNT, 'Endless Hunt', problems)
    _anim_provenance(db, problems)

    # --- (D) R-84: the pursuit kit exists, is CASTABLE, and is wired --------
    for sk in _NEW_SKILLS:
        if not db.has_record(sk):
            problems.append("R-84: new skill missing: %s" % sk)
            continue
        cls = _gv1(db, sk, 'Class')
        if cls != _EXPECT_CLASS[sk]:
            problems.append("R-84: %s Class=%r != %r"
                            % (sk.rsplit('\\', 1)[-1], cls, _EXPECT_CLASS[sk]))
        if sk == _MARK_BUFF:
            continue    # a buff payload is never cast directly
        anim = _gv1(db, sk, 'skillSpecialAnimationName')
        if anim not in (None, '', '0'):
            problems.append(
                "R-84 CASTABILITY: %s declares skillSpecialAnimationName=%r but "
                "%s binds no unarmedSpecialAnimRef at all - the engine would have "
                "no playable animation and would never fire the skill"
                % (sk.rsplit('\\', 1)[-1], anim, _HUNT.rsplit('\\', 1)[-1]))
    if db.has_record(_MARK) and _norm(_gv1(db, _MARK, 'buffSkillName')) != _norm(_MARK_BUFF):
        problems.append("R-84: Quarry's Mark buffSkillName != its own buff record")

    for suffix in sorted(_CAST_PLAN):
        new_skill, chance, band = _CAST_PLAN[suffix]
        sn = _gv1(db, _HUNT, 'specialAttack%sSkillName' % suffix)
        ch = _gv1(db, _HUNT, 'specialAttack%sChance' % suffix)
        if _norm(sn) != _norm(new_skill):
            problems.append("R-84: specialAttack%s=%r != %s"
                            % (suffix or '1', sn, new_skill.rsplit('\\', 1)[-1]))
        elif (ch or 0) <= 0:
            problems.append("R-84: specialAttack%s chance %r <= 0" % (suffix or '1', ch))
        slot = _slot_of(db, _HUNT, new_skill)
        if slot is None:
            problems.append("R-84: %s is not in any skillName slot"
                            % new_skill.rsplit('\\', 1)[-1])
        else:
            lv = db.get_field_value(_HUNT, 'skillLevel%d' % slot)
            lv0 = lv[0] if isinstance(lv, list) and lv else lv
            if not lv0:
                problems.append("R-84: %s sits at skillLevel%d=%r (level 0 never fires)"
                                % (new_skill.rsplit('\\', 1)[-1], slot, lv))

    # SAMENESS GATE: he must not share every active cast slot with the Enslaver again.
    ens = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
    if db.has_record(ens):
        def _casts(rec):
            out = set()
            ff = db.get_fields(rec) or {}
            for k, tf in ff.items():
                m = _re.match(r'specialAttack(\d*)SkillName$', k.split('###')[0])
                if m and tf.values and str(tf.values[0]).strip():
                    out.add(_norm(tf.values[0]))
            return out
        mine = _casts(_HUNT)
        shared = mine & _casts(ens)
        if mine and len(shared) >= len(mine):
            problems.append(
                "R-84 SAMENESS: every one of the Endless Hunt's %d cast slots is "
                "also an Enslaver cast slot (%s) - he is an Enslaver clone again"
                % (len(mine), sorted(s.rsplit('\\', 1)[-1] for s in shared)))

    if problems:
        for p in problems:
            print("  ENDLESS-HUNT OFFENDER: %s" % p)
        raise SystemExit("toxeus_hunt_encounter.verify FAILED: %d problem(s)"
                         % len(problems))
    print("  [toxeus_hunt_encounter].verify OK: fixed encounter resolves on N/E/L; "
          "Rite at 100 percent Misc4 with the recipe still gated on LEGENDARY "
          "souls; Runbreaker x3 + a playable spear animation block (3 borrowed "
          "poses, provenance proven); pursuit kit castable, wired and no longer an "
          "Enslaver clone.")
    return tags


# -- PLANTED NEGATIVE TEST (the gate must go red when the invariant breaks) --
def _negtest():
    """py tools/patches/toxeus_hunt_encounter.py --negtest

    Four plants, each run against a tiny stub db, each of which MUST be caught:
      1. the Legendary-only gate comes back (poolEpic1 emptied)
      2. a spear is equipped but the rig has no spearAttackAnim1
      3. a kit skill declares a skillSpecialAnimationName the caster cannot bind
      4. the EoAT recipe stops demanding LEGENDARY souls
    """
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = v

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_fields(self, n):
            f = self.d.get(n)
            if f is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in f.items())

        def get_field_value(self, n, f):
            return self.d.get(n, {}).get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

    def _base():
        db = _Stub()
        db.d[_STALKER_PROXY] = {
            'pool1': [_STALKER_POOL], 'poolEpic1': [_STALKER_POOL],
            'poolLegendary1': [_STALKER_POOL],
            'weight1': [10], 'weightEpic1': [10], 'weightLegendary1': [10]}
        db.d[_STALKER_POOL] = {'name1': [_HUNT]}
        db.d[_EOAT_FORMULA] = {
            'reagent1BaseName': [r'records\item\equipmentring\soul\skeleton\toxeus_soul_l.dbr'],
            'reagent2BaseName': [r'records\item\equipmentring\soul\svc_uber\enslaver_soul_l.dbr'],
            'reagent3BaseName': [r'records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_l.dbr']}
        db.d[_RITE_TABLE] = {'lootName1': [_EOAT_FORMULA]}
        hunt = {'chanceToEquipMisc4': [100.0],
                'lootMisc4Item1': [_RITE_TABLE, _RITE_TABLE, _RITE_TABLE],
                'lootRightHandItem1': [_SPEAR_GUAR[t] for t in 'nel']}
        for i, a in enumerate(_SPEAR_ATT_ANIMS, start=1):
            hunt['spearAttackAnim%d' % i] = [a]
        for f in ('spearRunAnim', 'spearWalkAnim', 'spearAttackIdleAnim',
                  'spearDieAnim1', 'spearStunAnim'):
            hunt[f] = [r'Creatures\Monster\ShadowStalker\ANM\ShadowStalker_Run.anm']
        for i, suffix in enumerate(sorted(_CAST_PLAN), start=1):
            sk, ch, band = _CAST_PLAN[suffix]
            hunt['specialAttack%sSkillName' % suffix] = [sk]
            hunt['specialAttack%sChance' % suffix] = [ch]
            hunt['skillName%d' % i] = [sk]
            hunt['skillLevel%d' % i] = [1, 2, 3]
        db.d[_HUNT] = hunt
        # a second record carrying the borrowed poses = the provenance proof
        db.d[r'records\provenance\donor.dbr'] = dict(
            ('spearAttackAnim%d' % i, [a])
            for i, a in enumerate(_SPEAR_ATT_ANIMS, start=1))
        db.d[_SPEAR_DONOR] = {'mesh': [_SPEAR_MESH]}
        for t in 'nel':
            db.d[_SPEAR[t]] = {'Class': ['WeaponHunting_Spear'],
                               'itemNameTag': [_SPEAR_NAME_TAG],
                               'mesh': [_SPEAR_MESH]}
            db.d[_SPEAR_GUAR[t]] = {'lootName1': [_SPEAR[t]]}
        for sk, cls in _EXPECT_CLASS.items():
            db.d[sk] = {'Class': [cls]}
        db.d[_MARK]['buffSkillName'] = [_MARK_BUFF]
        return db

    plants = [
        ('Legendary-only gate returns',
         lambda db: db.d[_STALKER_PROXY].__setitem__('poolEpic1', [''])),
        ('spear equipped, no attack animation',
         lambda db: db.d[_HUNT].__setitem__('spearAttackAnim1', [''])),
        ('kit skill needs an unbindable special animation',
         lambda db: db.d[_LANCE].__setitem__('skillSpecialAnimationName', ['Harpoon'])),
        ('EoAT recipe stops demanding LEGENDARY souls',
         lambda db: db.d[_EOAT_FORMULA].__setitem__(
             'reagent3BaseName',
             [r'records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_n.dbr'])),
        ('the spear ships on the invisible-weapon DRX supra mesh (build30 F3)',
         lambda db: db.d[_SPEAR['l']].__setitem__(
             'mesh', [r'DRX\meshes\supra\wep_spear.msh'])),
    ]
    tags = {_SPEAR_NAME_TAG: 'Runbreaker'}
    try:
        verify(_base(), dict(tags))
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        db = _base()
        plant(db)
        try:
            verify(db, dict(tags))
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    sys.exit(_negtest() if '--negtest' in sys.argv else 0)
