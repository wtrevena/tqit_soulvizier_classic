r"""r247_boss_forms - R-247 rulings 3, 5(a) and 6 (Will 2026-08-13).

One lane, four surfaces, every number justified from the measured shipped arz
(a86afc15; probes: tools/debug/r247_boss_form_audit.py + r247_hunt_chain_probe.py):

RULING 3 - LETHAEUS, THE UNREMEMBERED (um_mnemophage_99 -> um_mnemophage_core_99).
  Will, verbatim: "the second form of the boss is much smaller and much weaker
  than the original form." Measured: shell scale 2.9 / height 2.4 / life
  14/19/25k / hand 262-284 -> core scale 1.8 / height 1.8 / life 7/9.5/12.5k /
  hand 262-284 = the audit's ONE blatant boss-tier offender (smaller + shorter +
  half the life). The design law is the Soul-Gaoler pattern: the final form is
  the ESCALATION. Fix (scale+power only; the kit is intact and stays):
    scale  1.8 -> 3.1   (strictly above the shell's 2.9; inside the roster's
                         proven band - Gigantes ships 3.5/3.8, Vashkarr 3.0)
    height 1.8 -> 2.4   (the SHELL's own value on the SAME Epiales01 mesh -
                         restored, not invented; R-126 reads the rig constant
                         off the sibling record)
    life   7/9.5/12.5k -> 16/21/28k (strictly above the shell at every
                         difficulty; the Gaoler-form-1 class 15/20/27k; top
                         quartile of the 50-boss band, below the marshal's
                         26/32/40k - the core is one form of a two-form fight)
    hand   262-284 -> 300-330 (strictly above the shell's; modest - the core's
                         menace is its kit, not its swing)

RULING 5(a) - THE ENDLESS HUNT IS A SKELETON (um_toxeus_hunt_99).
  Will, verbatim: "toxeus the murderer the endless hunt is still a demon not a
  skeleton". Measured: mesh ShadowStalker.msh, characterRacialProfile 'Demon',
  NO charAnimationTableName - the whole anim set is INLINE rows of
  ShadowStalker/JackalMan/Maenad clips. GIT-ARCHAEOLOGY (b98, branches
  feat/endless-hunt + feat/mythic-hunt): the b98 encounter was purpose-built ON
  the DRX shadow-stalker body (its ambush controller, its iceheart skin, the
  Maenad spear rows transplanted inline per the thrown-wielder lesson) - the
  demon body was the b98 DESIGN, not a drift; Will's R-247 ruling supersedes it.
  Fix follows the family precedent (Enslaver = SkeletonGrayBlack01New +
  anm_skeleton01; Devourer = GoldenSkeleton01 + anm_skeleton01, both Undead):
    mesh        -> Creatures\Monster\Skeleton\SkeletonRumorBoss.msh - the base
                   game's own GIANT-SKELETON boss mesh (q4_giantskeleton_* -
                   in-game-confirmed), DISTINCT from both brothers.
    baseTexture -> NewSkeleton_White.tex - pale bone: the cold/spectral read of
                   his iceheart identity AND his own huntsman pack's skin (the
                   R-247.5b summons ride the hoplite donor that ships this
                   texture). Cross-mesh pairing inside the one skeleton texture
                   family, the exact class the Devourer already proves in-game
                   (crimson on GoldenSkeleton01). FLAGGED for Will's veto with
                   NewSkeleton_Yellow (this mesh's own proven pairing) as the
                   one-constant fallback.
    anm table   -> anm_skeleton01 (the family rig: 108 spear rows, 7 base-game
                   skeletal hoplites equip spears on it, unarmedRunAnim bound)
                   and EVERY inline foreign-rig .anm override CLEARED - foreign
                   clips on a skeleton mesh are the A9/Dagon-frozen class.
    >>> ROUND 3 (the round-2 vet blocker). Round 2 stopped at the clear and
        wrote ZERO inline rows, betting the table drives everything. The vet
        refuted that on one axis: anm_skeleton01 binds 'AoE360' ONLY on its
        sHanded/dHanded rows - never on the SPEAR row a spear-guaranteed
        monster occupies, never on unarmed - so toxeus_bladestorm (kept per
        ruling 5: "Keep his 4 b98 skills ... + spear intact") was uncastable
        under ANY engine model, and toxeus_hunt_encounter's SPEAR-ANIM-1 /
        CASTABILITY-1 gates (which read INLINE rows, the b98 lane's proven
        surface) went red 14x. Fix = the adfda67 BOTH-SURFACES law
        (dagon_anim_rig, IN-GAME-proven on build90): after the clear, the two
        rows he can actually read are REBOUND INLINE with the table's OWN
        clips, read live from anm_skeleton01 at build time so they can never
        desync from the rig:
          * the full SPEAR row (his live row - spear-guaranteed @100) and the
            full UNARMED row (the engine's universal fallback; the coldworm
            precedent): attack 1-3 / run / walk / attackIdle / die1 / stun /
            spawn. spearAttackAnim3 duplicates the table's spearAttackAnim1 -
            the rig's own idiom (anm_skeleton01 binds ONE clip on all three
            unarmedAttackAnim slots; 1,063 shipped records share the
            duplicate-slot pattern).
          * 'AoE360' bound on BOTH rows: <row>SpecialAnimRef1='AoE360' ->
            the table's own sHandedSpecialAnim1 clip
            (MalePC_DW_Skill_AOE360.anm - the rig's proven AoE360 clip; the
            same table drives it on every base skeletal hoplite in-game, and
            the rig plays MalePC clips throughout: MalePC_SPear_AttAlpha IS
            its spear attack).
        Inline rows on a table-carrying record are the shipped data's own
        idiom - 3,498 of 3,807 charAnimationTableName carriers also bind
        inline .anm rows (measured, a86afc15). What the law excludes is
        FOREIGN-RIG clips, not inline-ness: verify() now asserts every inline
        clip on the Hunt is one the resolved rig table itself binds.
    race        -> Undead (the family value; both brothers measured Undead).
    actorHeight -> 2.0 (R-126: the RIG constant, measured on this mesh's own
                   q4_giantskeleton records AND on the GoldenSkeleton hoplites;
                   the shipped 2.4 was the shadowstalker rig's constant).
    scale 1.9 UNTOUCHED (size was never this ruling's complaint; 1.9 on the
                   giant-skeleton mesh reads properly imposing - 1.46x the q4
                   carrier's 1.3, under the Enslaver's 2.4 rig-class stretch).
  ORDERING IS LOAD-BEARING: this module runs AFTER devourer_kit (which builds
  the huntsman pack + hunt summon this identity references) and BEFORE
  toxeus_hunt_endless (whose um_toxeus_hunt_l_99 is a build-time clone of the
  base - so the Legendary variant inherits the skeleton identity by
  construction, and the one-field-diff invariant stays green).

RULING 6(b) - THE SPEAR, VERIFIED (no fix - the bytes prove it correct).
  Measured on the shipped arz: chanceToEquipRightHand 100 / Item1 100 ->
  runbreaker_guaranteed_{n,e,l} (FixedWeight @100) -> svc_{n,e,l}_runbreaker
  (real Weapon_Spear records, RSpear14B.msh), and the shipped inline rows bound
  spearAttackAnim1-3 (Maenad spear clips) + walk/run/idle/spawn/stun spear rows.
  VERDICT: the shipped spear chain was byte-correct - Will's softened "maybe he
  was using a spear and i couldnt see it" is the likely truth. After this
  module's rig swap the chain is RE-proven on the new rig: anm_skeleton01
  carries the spear stance rows and base-game skeletal hoplites wield spears
  on it in-game. ROUND-3 CORRECTION: round 2 overstated "the full spear row
  set" - the table ships NO spearSpecialAnimRef rows and only 2 spear attack
  clips, which is exactly why the ruling-5a round-3 inline rebind exists
  (see above). verify() gates the whole chain either way.

RULING 6(c) - THE HUNT SOUL SUMMONS HIM (a BUILD, not a fix).
  Measured: toxeus_hunt_soul_{n,e,l} grant svc_hunt_quarrysmark @ 1/2/3 via an
  on-hit autocast controller; NO summon skill and NO hunt pets exist anywhere
  in the DB - b98 shipped the soul before the family's summon pattern existed.
  Built here exactly on the family pattern: pets toxeus_hunt_1/2/3 via the
  monolith's _build_boss_summon (Lyia Pet.tpl baseline, source = the POST-fix
  skeleton Hunt, so the pets inherit the skeleton identity + anm_skeleton01 +
  a spear loadout mirrored from his own equip chain; permanent = TTL-free by
  construction; PET-STAT-MIRROR / gear / kit gates all registered), summon
  skill summon_toxeus_hunt (Skill_SpawnPet, the exact summon_toxeus_enslaver
  shape), souls repointed itemSkillName -> the summon at their existing
  itemSkillLevel 1/2/3, autocast controller REMOVED (a 180s manual summon on an
  on-any-hit autocast would be burned instantly; no other summon soul carries
  one - measured). COST: Quarry's Mark stops being the wearer's granted skill
  (a soul grants ONE skill; the summon is the family contract) - FLAGGED for
  Will. The Hunt pets keep quarrysmark/bladestorm/longreach/rundown in their
  mirrored kit; their inherited reference to the HOSTILE huntsman summon is
  stripped (the enslaver-marauder lesson: a player pet must never raise enemies).

RULING 6(d) - TIERED SOUL SUMMONS, made REAL and made VISIBLE.
  Measured: the tiers already ladder (souls at itemSkillLevel 1/2/3 -> pets
  _1/_2/_3: enslaver 13/18/24k life + 110-160/170-250/240-350 hand; blood
  12/-/26k same shape) BUT epic/legendary were only ~1.4x/1.9x normal AND all
  three tiers of each family share ONE display name = the ladder is invisible
  in-game (why Will read them as identical). Fix, uniform across the family:
    life:  _2 -> 1.5x its shipped value, _3 -> 1.75x its shipped value
           (enslaver 18k->27k, 24k->42k: the Legendary summon lands at the
           dropper's own Epic-form 45k class while staying under the crafted
           EoAT apex pet's measured 82k; same multipliers for blood + the new
           hunt ladder is authored directly on that curve)
    hand:  _2 -> 1.5x, _3 -> 1.75x shipped
    names: per-tier display tags - base name (tier 1), ", Ascendant" (tier 2),
           ", Unbound" (tier 3 - the mod's own escalation vocabulary: the
           Gaoler/Tantalus final forms). Minted PLAIN (white) so the b50
           pet-whiten pass skips them. Strings FLAGGED for Will's veto.
  EoAT: single supra soul, permanently tier-3 - nothing to ladder (measured:
  its pet is already the family apex at 82k/400-620). MOD-WIDE soul tiering =
  a Will decision, NOT implemented here (flagged in the lane report).

RULING 6(e) - THE +ALL-SKILLS LAW.
  augmentAllLevel 1/2/3 on the Toxeus-family soul tiers (enslaver, blood/
  Devourer, hunt) + 3 on the single Legendary-class EoAT soul. The field is the
  base-game +all-skills mechanism, proven by 7 base ItemArtifactFormula-era
  items AND in-mod by svc_e_runbreaker's shipped `augmentAllLevel 1`. INT
  dtype, passed ONLY because the field is absent on every one of these souls
  (the dtype-preservation law's sanctioned arm). Stacks with the souls'
  existing augmentSkillName grants (different fields, no collision). The
  original skeleton\toxeus_soul_{n,e,l} ("Toxeus the Murderer" himself) is NOT
  in ruling 6(d)'s roster and is NOT touched - flagged as a Will question.

RULING 6(a) - THE EOAT FORMULA IS VISIBLE.
  Measured: the drop wiring was ALREADY CORRECT - svc_rite_guaranteed
  (FixedWeight, lootName1 = the formula @100) rides lootMisc4Item1 on BOTH hunt
  records at chanceToEquipMisc4 100, all three difficulty rows. Will's kill DID
  drop it. The real defect: itemClassification 'Common' + the generic blank-
  recipe mesh/bitmap = a plain white drop buried under a Legendary boss-kill's
  orb/soul/spear explosion, and hidden by any loot filter. Fix:
  itemClassification -> 'Legendary' (proven value: 7 base-game
  ItemArtifactFormula records ship it, e.g. l_da_thothsglory_formula) - orange
  name, filter-proof. The 100% drop chance is KEPT and the drop stays UNGATED
  by difficulty: the craft is self-gated (its reagents are three LEGENDARY
  souls), so a Normal-difficulty pickup is inert foreshadowing, and gating it
  would re-create the "Will kills the boss and gets nothing" defect one
  difficulty down. FLAGGED as a decision Will can reverse with one constant.
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "R-247 boss forms: Lethaeus escalation + skeleton Hunt + soul chain"

I = 0     # DATA_TYPE_INT
F = 1     # DATA_TYPE_FLOAT
S = 2     # DATA_TYPE_STRING

# ── Lethaeus ────────────────────────────────────────────────────────────────
_SHELL = r'records\xpack\creatures\monster\epiales\um_mnemophage_99.dbr'
_CORE = r'records\xpack\creatures\monster\epiales\um_mnemophage_core_99.dbr'
_CORE_SCALE = 3.1
_CORE_HEIGHT = 2.4          # the shell's own value on the same Epiales01 mesh
_CORE_LIFE = [16000.0, 21000.0, 28000.0]
_CORE_HAND = (300.0, 330.0)
# the core's signature kit, asserted intact (this is a scale+power fix ONLY).
# ROUND-3 CORRECTION (found by the first build in which this verify ever ran):
# round 1 listed sandsofsleep/distortreality/epiales_summon2/ondeath_voidnova
# here - those are the SHELL's skills (um_mnemophage_99 skillName17/18/19/23,
# byte-decoded on shipped a86afc15); the CORE never carried them, so the gate
# redded on a kit that was never his. The sentinels below are the core's OWN
# shipped kit, byte-decoded from a86afc15: chainconvert (skillName4 +
# specialAttack3), chainconvert_cascade (skillName5), mnemophage_mindshroud
# (initialSkillName), breach_shadowgrasp (skillName7),
# shadowstalker_distortionfield (skillName9).
_CORE_KIT_SENTINELS = ('chainconvert', 'chainconvert_cascade',
                       'mnemophage_mindshroud', 'breach_shadowgrasp',
                       'shadowstalker_distortionfield')

# ── the Endless Hunt ────────────────────────────────────────────────────────
_HUNT = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
_HUNT_L = r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr'
_HUNT_MESH = r'Creatures\Monster\Skeleton\SkeletonRumorBoss.msh'
_HUNT_SKIN = r'Creatures\Monster\Skeleton\NewSkeleton_White.tex'
_HUNT_ANM = r'records\creature\monster\skeleton\anm\anm_skeleton01.dbr'
_HUNT_RACE = 'Undead'
_HUNT_HEIGHT = 2.0          # R-126 rig constant: q4_giantskeleton + hoplites
_RUNBREAKER_N = r'records\item\loottables\svc\runbreaker_guaranteed_n.dbr'
# ── R-247.5a ROUND 3: the inline rebind (adfda67 both-surfaces law) ────────
# dst inline slot on the Hunt -> src slot on anm_skeleton01 whose clip is
# copied VERBATIM at build time. spearAttackAnim3 <- spearAttackAnim1 is the
# rig's own duplicate-slot idiom (its unarmed row binds one clip on all 3
# attack slots; 1,063 shipped records share the pattern). Both rows he can
# read (spear = live @100% equip, unarmed = engine universal fallback) are
# bound in full, so the resolved animation set is identical whichever surface
# the engine reads.
_INLINE_REBIND = {}
for _row in ('spear', 'unarmed'):
    for _slot, _src in (('AttackAnim1', 'AttackAnim1'),
                        ('AttackAnim2', 'AttackAnim2'),
                        ('AttackAnim3', 'AttackAnim1'),
                        ('RunAnim', 'RunAnim'), ('WalkAnim', 'WalkAnim'),
                        ('AttackIdleAnim', 'AttackIdleAnim'),
                        ('DieAnim1', 'DieAnim1'), ('StunAnim', 'StunAnim'),
                        ('SpawnAnim', 'SpawnAnim')):
        _INLINE_REBIND[_row + _slot] = _row + _src
del _row, _slot, _src
# the table's spear row has no AttackAnim3 and unarmed's 3 slots are all one
# clip, so both AttackAnim3 entries above self-heal to slot 1's clip.
_AOE360_REF = 'AoE360'                     # toxeus_bladestorm's declared anim
_AOE360_SRC = 'sHandedSpecialAnim1'        # the rig's own AoE360 clip slot
_AOE360_SRC_REF = 'sHandedSpecialAnimRef1'  # asserted == 'AoE360' at build
_AOE360_ROWS = ('spear', 'unarmed')        # live row + universal fallback row
# the 9 SPEAR-ANIM-1 slots toxeus_hunt_encounter's gate requires inline
_SPEAR_GATE_SLOTS = ('spearAttackAnim1', 'spearAttackAnim2', 'spearAttackAnim3',
                     'spearRunAnim', 'spearWalkAnim', 'spearAttackIdleAnim',
                     'spearDieAnim1', 'spearStunAnim', 'spearSpawnAnim')

# ── the Hunt soul chain (6c) ────────────────────────────────────────────────
_SOUL_ROOT = r'records\item\equipmentring\soul\svc_uber'
_HUNT_SOULS = tuple(_SOUL_ROOT + r'\toxeus_hunt_soul_%s.dbr' % t
                    for t in ('n', 'e', 'l'))
_HUNT_PETS = tuple(r'records\skills\soulskills\pets\toxeus_hunt_%d.dbr' % i
                   for i in (1, 2, 3))
_HUNT_SUMMON = r'records\skills\soulskills\summon_toxeus_hunt.dbr'
_TAG_HUNT_SUMMON = 'tagSVCSummonToxeusHunt'
_TAG_HUNT_PET = 'tagSVCPetToxeusHunt'
# authored on the retuned family curve (see 6d): _1 at the family normal-tier
# baseline, _2 = 1.5x _1's class, _3 = 1.75x _2's class; all < the EoAT 82k apex
_HUNT_PET_LIFE = [12000.0, 18000.0, 31500.0]
_HUNT_PET_REGEN = [30.0, 60.0, 100.0]
_HUNT_PET_DMG_MIN = [110.0, 165.0, 290.0]
_HUNT_PET_DMG_MAX = [180.0, 270.0, 470.0]

# ── the tier retune (6d) ────────────────────────────────────────────────────
_T2_FACTOR = 1.5
_T3_FACTOR = 1.75
_PET_FAMILIES = {
    # family key -> (pet paths _1.._3, fallback plain base name)
    'enslaver': (tuple(r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
                       for i in (1, 2, 3)),
                 'Toxeus the Murderer, Enslaver of Souls'),
    'blood': (tuple(r'records\skills\soulskills\pets\bloodtoxeus_%d.dbr' % i
                    for i in (1, 2, 3)),
              'Toxeus the Murderer, Devourer of Blood'),
    'hunt': (_HUNT_PETS, 'Toxeus the Murderer, the Endless Hunt'),
}
_TIER_SUFFIX = {2: ', Ascendant', 3: ', Unbound'}
_TIER_TAG = {('enslaver', 2): 'tagSVCPetEnslaverT2',
             ('enslaver', 3): 'tagSVCPetEnslaverT3',
             ('blood', 2): 'tagSVCPetDevourerT2',
             ('blood', 3): 'tagSVCPetDevourerT3',
             ('hunt', 2): 'tagSVCPetToxeusHuntT2',
             ('hunt', 3): 'tagSVCPetToxeusHuntT3'}

# ── the +all-skills law (6e) ────────────────────────────────────────────────
_FAMILY_SOULS = {
    1: (_SOUL_ROOT + r'\enslaver_soul_n.dbr',
        _SOUL_ROOT + r'\blood_toxeus_soul_n.dbr',
        _SOUL_ROOT + r'\toxeus_hunt_soul_n.dbr'),
    2: (_SOUL_ROOT + r'\enslaver_soul_e.dbr',
        _SOUL_ROOT + r'\blood_toxeus_soul_e.dbr',
        _SOUL_ROOT + r'\toxeus_hunt_soul_e.dbr'),
    3: (_SOUL_ROOT + r'\enslaver_soul_l.dbr',
        _SOUL_ROOT + r'\blood_toxeus_soul_l.dbr',
        _SOUL_ROOT + r'\toxeus_hunt_soul_l.dbr',
        _SOUL_ROOT + r'\soul_of_toxeus_endofallthings.dbr'),
}

# ── the EoAT formula (6a) ───────────────────────────────────────────────────
_FORMULA = r'records\drxitem\supra\recipes\svc_toxeus_eoat_formula.dbr'
_FORMULA_CLASSIFICATION = 'Legendary'   # proven: 7 base ItemArtifactFormula carriers
_RITE_TABLE = r'records\item\loottables\svc\svc_rite_guaranteed.dbr'
_EOAT_SOUL = _SOUL_ROOT + r'\soul_of_toxeus_endofallthings.dbr'
_EOAT_SUMMON = r'records\skills\soulskills\summon_toxeus_eoat.dbr'


def _norm(p):
    return str(p).replace('/', '\\').strip().lower()


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) and v else v


def _gvl(db, rec, f):
    v = db.get_field_value(rec, f)
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _fix_lethaeus(db):
    for rec in (_SHELL, _CORE):
        if not db.has_record(rec):
            raise SystemExit("[r247] Lethaeus record missing: %s" % rec)
    # assert the measured defect before overwriting (never a blind write)
    got = _gvl(db, _CORE, 'characterLife')
    if got and float(got[min(1, len(got) - 1)]) > 12500.0 + 0.5:
        raise SystemExit(
            "[r247] um_mnemophage_core_99 characterLife=%r is not the measured "
            "defective 7/9.5/12.5k - a later writer moved it; re-measure before "
            "retuning (NO-ESTIMATES law)." % (got,))
    db.set_field(_CORE, 'scale', _CORE_SCALE)
    db.set_field(_CORE, 'actorHeight', _CORE_HEIGHT)
    db.set_field(_CORE, 'characterLife', list(_CORE_LIFE))
    db.set_field(_CORE, 'handHitDamageMin', _CORE_HAND[0])
    db.set_field(_CORE, 'handHitDamageMax', _CORE_HAND[1])
    db._modified.add(_CORE)
    print("  [r247.3] Lethaeus core: scale 1.8->%.1f (> shell 2.9), height "
          "->%.1f (the shell's own rig value), life 7/9.5/12.5k -> %s, hand "
          "262-284 -> %g-%g; kit untouched."
          % (_CORE_SCALE, _CORE_HEIGHT,
             [int(x) for x in _CORE_LIFE], _CORE_HAND[0], _CORE_HAND[1]))


def _table_clip(db, slot):
    """The .anm clip anm_skeleton01 itself binds at `slot` - fail-loud if the
    rig table no longer carries it (NO-ESTIMATES: the rebind copies the rig's
    own bytes, never a hand-typed path)."""
    v = _gv1(db, _HUNT_ANM, slot)
    v = str(v).strip() if v is not None else ''
    if not v.lower().endswith('.anm'):
        raise SystemExit(
            "[r247] anm_skeleton01 %s=%r - the rig table no longer binds the "
            "clip the round-3 inline rebind copies; re-measure before building "
            "(NO-ESTIMATES law)." % (slot, v))
    return v


def _set_str(db, rec, field, value):
    """Write a string field; type it explicitly ONLY when absent (the
    dtype-preservation law's sanctioned arm - same pattern this module already
    uses for charAnimationTableName)."""
    if db.get_field_value(rec, field) is None:
        db.set_field(rec, field, value, S)
    else:
        db.set_field(rec, field, value)


def _fix_hunt_identity(db):
    if not db.has_record(_HUNT):
        raise SystemExit("[r247] the Endless Hunt is missing: %s" % _HUNT)
    if db.has_record(_HUNT_L):
        raise SystemExit(
            "[r247] um_toxeus_hunt_l_99 already exists - this module MUST run "
            "before toxeus_hunt_endless so the Legendary clone inherits the "
            "skeleton identity. The registry order moved; fix the ordering, "
            "never patch the clone by hand.")
    if not db.has_record(_HUNT_ANM):
        raise SystemExit("[r247] the skeleton rig table is missing: %s" % _HUNT_ANM)
    # every inline .anm override goes: foreign-rig clips on a skeleton mesh are
    # the A9 / Dagon-frozen class. Enumerated live, never a hand list.
    ff = db.get_fields(_HUNT) or {}
    cleared = 0
    for k, tf in list(ff.items()):
        base = k.split('###')[0]
        vals = tf.values or []
        if any(isinstance(v, str) and v.lower().endswith('.anm') for v in vals):
            db.set_field(_HUNT, base, '')
            cleared += 1
    db.set_field(_HUNT, 'mesh', _HUNT_MESH)
    db.set_field(_HUNT, 'baseTexture', _HUNT_SKIN)
    if db.get_field_value(_HUNT, 'charAnimationTableName') is None:
        db.set_field(_HUNT, 'charAnimationTableName', _HUNT_ANM, S)
    else:
        db.set_field(_HUNT, 'charAnimationTableName', _HUNT_ANM)
    db.set_field(_HUNT, 'characterRacialProfile', _HUNT_RACE)
    db.set_field(_HUNT, 'actorHeight', _HUNT_HEIGHT)
    # ── ROUND 3: rebind his two readable rows INLINE from the rig's own
    # clips (adfda67 both-surfaces law; see the module docstring, ruling 5a).
    rebound = 0
    for dst, src in sorted(_INLINE_REBIND.items()):
        _set_str(db, _HUNT, dst, _table_clip(db, src))
        rebound += 1
    ref = _gv1(db, _HUNT_ANM, _AOE360_SRC_REF)
    if str(ref or '').strip() != _AOE360_REF:
        raise SystemExit(
            "[r247] anm_skeleton01 %s=%r != %r - the rig's AoE360 slot moved; "
            "re-measure before building (NO-ESTIMATES law)."
            % (_AOE360_SRC_REF, ref, _AOE360_REF))
    aoe_clip = _table_clip(db, _AOE360_SRC)
    for row in _AOE360_ROWS:
        _set_str(db, _HUNT, row + 'SpecialAnimRef1', _AOE360_REF)
        _set_str(db, _HUNT, row + 'SpecialAnim1', aoe_clip)
        rebound += 2
    db._modified.add(_HUNT)
    print("  [r247.5a] the Endless Hunt is a SKELETON: SkeletonRumorBoss.msh + "
          "NewSkeleton_White + anm_skeleton01 (family rig), race Undead, "
          "actorHeight 2.0 (rig constant), %d inline foreign-rig .anm "
          "override(s) cleared, then %d inline slot(s) REBOUND from the rig's "
          "own clips (spear + unarmed rows in full, 'AoE360' on both - "
          "toxeus_bladestorm castable; adfda67 both-surfaces law); scale 1.9 "
          "untouched. The _l variant inherits all of it at clone time."
          % (cleared, rebound))


def _build_hunt_soul_summon(db, tags):
    from apply_svc_patches import _build_boss_summon
    ok = _build_boss_summon(
        db, _HUNT, list(_HUNT_PETS), _HUNT_SUMMON,
        _TAG_HUNT_SUMMON, _TAG_HUNT_PET,
        char_level=[40, 68, 100],
        life=list(_HUNT_PET_LIFE), life_regen=list(_HUNT_PET_REGEN),
        dmg_min=list(_HUNT_PET_DMG_MIN), dmg_max=list(_HUNT_PET_DMG_MAX),
        scale=1.9)
    if ok is False:
        raise SystemExit("[r247] _build_boss_summon failed for the Hunt pets")
    # a player's pet must never raise HOSTILE adds: strip the mirrored
    # reference to the Hunt's own Skill_SpawnPetMonster (the enslaver-marauder
    # lesson, same shape).
    hostile = r'records\skills\boss skills\svc_hunt_summoncoursers.dbr'
    for p in _HUNT_PETS:
        ff = db.get_fields(p) or {}
        for k, tf in list(ff.items()):
            base = k.split('###')[0]
            vals = tf.values or []
            if any(isinstance(v, str) and _norm(v) == _norm(hostile)
                   for v in vals):
                db.set_field(p, base, '')
        db._modified.add(p)
    # the souls grant the summon at their existing tier levels; the autocast
    # controller goes (no summon soul carries one - measured across the family)
    for soul, lvl in zip(_HUNT_SOULS, (1, 2, 3)):
        if not db.has_record(soul):
            raise SystemExit("[r247] hunt soul missing: %s" % soul)
        db.set_field(soul, 'itemSkillName', _HUNT_SUMMON)
        got = _gv1(db, soul, 'itemSkillLevel')
        if int(got or 0) != lvl:
            db.set_field(soul, 'itemSkillLevel', lvl)
        if db.get_field_value(soul, 'itemSkillAutoController') is not None:
            db.set_field(soul, 'itemSkillAutoController', '')
        db._modified.add(soul)
    tags[_TAG_HUNT_SUMMON] = 'Loose the Endless Hunt'
    tags[_TAG_HUNT_SUMMON + 'DESC'] = (
        'The Murderer who never stopped walking answers the soul that binds '
        'him. He does not tire. He does not forget. He does not stop.')
    tags[_TAG_HUNT_PET] = _PET_FAMILIES['hunt'][1]
    print("  [r247.6c] Hunt soul summon BUILT: pets toxeus_hunt_1/2/3 (life %s, "
          "hand %s-%s, skeleton identity inherited from the fixed Hunt), "
          "summon_toxeus_hunt granted at itemSkillLevel 1/2/3, autocast "
          "controller removed; Quarry's Mark grant superseded (FLAGGED)."
          % ([int(x) for x in _HUNT_PET_LIFE],
             [int(x) for x in _HUNT_PET_DMG_MIN],
             [int(x) for x in _HUNT_PET_DMG_MAX]))


def _retune_tiers(db, tags):
    for fam, (pets, fallback) in _PET_FAMILIES.items():
        for tier, pet in ((2, pets[1]), (3, pets[2])):
            if not db.has_record(pet):
                raise SystemExit("[r247] tier pet missing: %s" % pet)
            if fam != 'hunt':
                factor = _T2_FACTOR if tier == 2 else _T3_FACTOR
                for fld in ('characterLife', 'handHitDamageMin',
                            'handHitDamageMax'):
                    cur = _gv1(db, pet, fld)
                    if cur is None or float(cur) <= 0:
                        raise SystemExit(
                            "[r247] %s %s=%r - expected the monolith's shipped "
                            "value; a writer moved, re-measure." % (pet, fld, cur))
                    db.set_field(pet, fld, round(float(cur) * factor, 1))
            # the visible tier: its own display tag (plain white; the b50
            # whiten pass skips tags without color codes)
            base_tag = _gv1(db, pets[0], 'description') or ''
            base_text = tags.get(base_tag) or fallback
            import re as _re
            white = _re.sub(r'\{\^.\}', '', str(base_text)).strip() or fallback
            tag = _TIER_TAG[(fam, tier)]
            tags[tag] = white + _TIER_SUFFIX[tier]
            db.set_field(pet, 'description', tag)
            db._modified.add(pet)
    print("  [r247.6d] tier ladders retuned (x%.2f epic / x%.2f legendary on "
          "life+hand for enslaver/blood; hunt authored on the same curve) and "
          "made VISIBLE: per-tier names ', Ascendant' / ', Unbound' minted for "
          "all three families (FLAGGED for veto)." % (_T2_FACTOR, _T3_FACTOR))


def _grant_all_skills(db):
    wrote = 0
    for lvl, souls in _FAMILY_SOULS.items():
        for soul in souls:
            if not db.has_record(soul):
                raise SystemExit("[r247] +all-skills target missing: %s" % soul)
            if db.get_field_value(soul, 'augmentAllLevel') is None:
                db.set_field(soul, 'augmentAllLevel', lvl, I)   # absent -> typed
            else:
                db.set_field(soul, 'augmentAllLevel', lvl)
            db._modified.add(soul)
            wrote += 1
    print("  [r247.6e] +all-skills law: augmentAllLevel 1/2/3 written on %d "
          "Toxeus-family souls (EoAT at 3); INT, the svc_e_runbreaker-proven "
          "field." % wrote)


def _formula_visibility(db):
    if not db.has_record(_FORMULA):
        raise SystemExit("[r247] EoAT formula missing: %s" % _FORMULA)
    got = _gv1(db, _FORMULA, 'itemClassification')
    if got not in ('Common', _FORMULA_CLASSIFICATION):
        raise SystemExit(
            "[r247] EoAT formula itemClassification=%r - expected the measured "
            "'Common' defect (or an idempotent re-run); re-measure." % got)
    db.set_field(_FORMULA, 'itemClassification', _FORMULA_CLASSIFICATION)
    db._modified.add(_FORMULA)
    print("  [r247.6a] EoAT formula: itemClassification Common -> %s (orange "
          "name, filter-proof; 100%% drop + no difficulty gate KEPT - the "
          "craft is self-gated by its three Legendary-soul reagents)."
          % _FORMULA_CLASSIFICATION)


def apply(db, tags):
    print("\n=== [r247_boss_forms] R-247 rulings 3 / 5a / 6 ===")
    _fix_lethaeus(db)
    _fix_hunt_identity(db)
    _build_hunt_soul_summon(db, tags)
    _retune_tiers(db, tags)
    _grant_all_skills(db)
    _formula_visibility(db)
    print("=== [r247_boss_forms] done (verify() runs post-finalization) ===\n")
    return tags


def verify(db, tags=None):
    p = []
    tags = tags or {}

    def gv(rec, f):
        return _gv1(db, rec, f)

    def gl(rec, f):
        return _gvl(db, rec, f)

    # ---- ruling 3: Lethaeus is the escalation ------------------------------
    if not (db.has_record(_SHELL) and db.has_record(_CORE)):
        p.append("Lethaeus records missing")
    else:
        for fld, cmp_ in (('characterLife', 'gt'), ('scale', 'ge'),
                          ('actorHeight', 'ge'), ('handHitDamageMax', 'ge')):
            a, b = gl(_SHELL, fld), gl(_CORE, fld)
            for i in range(min(len(a), len(b))):
                try:
                    x, y = float(a[i] or 0), float(b[i] or 0)
                except (TypeError, ValueError):
                    p.append("Lethaeus %s unreadable (%r/%r)" % (fld, a, b))
                    break
                bad = (y <= x) if cmp_ == 'gt' else (y < x)
                if bad:
                    p.append("R-247.3: Lethaeus core %s row %d = %.2f vs shell "
                             "%.2f - the final form must be the escalation"
                             % (fld, i, y, x))
        kit = ' '.join(str(v) for k, tf in (db.get_fields(_CORE) or {}).items()
                       for v in (tf.values or []) if isinstance(v, str)).lower()
        for s in _CORE_KIT_SENTINELS:
            if s not in kit:
                p.append("R-247.3: Lethaeus core kit sentinel %r GONE - this "
                         "lane was scale+power only; the kit must survive" % s)

    # ---- ruling 5a: the Hunt is a skeleton ---------------------------------
    if not db.has_record(_HUNT):
        p.append("the Endless Hunt is missing")
    else:
        if _norm(gv(_HUNT, 'mesh') or '') != _norm(_HUNT_MESH):
            p.append("R-247.5a: Hunt mesh=%r != %s" % (gv(_HUNT, 'mesh'), _HUNT_MESH))
        if _norm(gv(_HUNT, 'charAnimationTableName') or '') != _norm(_HUNT_ANM):
            p.append("R-247.5a: Hunt anm table=%r != %s"
                     % (gv(_HUNT, 'charAnimationTableName'), _HUNT_ANM))
        if gv(_HUNT, 'characterRacialProfile') != _HUNT_RACE:
            p.append("R-247.5a: Hunt race=%r != %s (Will: 'still a demon not a "
                     "skeleton')" % (gv(_HUNT, 'characterRacialProfile'), _HUNT_RACE))
        # ROUND 3 LAW (supersedes round 2's zero-inline law, which the vet
        # refuted): inline .anm rows are LEGAL - what is banned is a clip the
        # resolved rig table does not itself bind (the A9/Dagon-frozen
        # foreign-rig class). 3,498/3,807 shipped table-carriers bind inline
        # rows; the ban is on FOREIGN clips, not inline-ness.
        table_clips = {_norm(v) for _k, _tf in (db.get_fields(_HUNT_ANM) or {}).items()
                       for v in (_tf.values or [])
                       if isinstance(v, str) and v.lower().endswith('.anm')}
        if not table_clips:
            p.append("R-247.5a: anm_skeleton01 binds no .anm clips at all - "
                     "the rig table is gutted")
        for _k, _tf in (db.get_fields(_HUNT) or {}).items():
            base = _k.split('###')[0]
            for v in (_tf.values or []):
                if (isinstance(v, str) and v.lower().endswith('.anm')
                        and _norm(v) not in table_clips):
                    p.append("R-247.5a: Hunt inline %s=%r is NOT a clip the "
                             "resolved rig table binds - the A9/Dagon-frozen "
                             "foreign-rig class" % (base, v))
        # ROUND 3: his two readable rows are fully bound INLINE (adfda67
        # both-surfaces law) - the spear row is his live row (SPEAR-ANIM-1,
        # toxeus_hunt_encounter's gate reads these inline slots), unarmed is
        # the engine's universal fallback row.
        for dst in sorted(_INLINE_REBIND):
            v = gv(_HUNT, dst)
            if not v or not str(v).strip().lower().endswith('.anm'):
                p.append("R-247.5a r3: Hunt inline %s=%r - the live/fallback "
                         "row must be fully bound on both surfaces" % (dst, v))
        # ROUND 3: bladestorm's 'AoE360' is bound on BOTH readable rows, and
        # the kept skill still declares exactly that ref (the castability
        # chain re-proven end to end).
        for row in _AOE360_ROWS:
            ref = str(gv(_HUNT, row + 'SpecialAnimRef1') or '').strip()
            if ref != _AOE360_REF:
                p.append("R-247.5a r3: Hunt %sSpecialAnimRef1=%r != %r - "
                         "toxeus_bladestorm has no playable animation on that "
                         "row" % (row, ref, _AOE360_REF))
            clip = gv(_HUNT, row + 'SpecialAnim1')
            if not clip or _norm(clip) not in table_clips:
                p.append("R-247.5a r3: Hunt %sSpecialAnim1=%r is empty or "
                         "foreign to the rig - the AoE360 cast dies on that "
                         "row" % (row, clip))
        bs = gv(_HUNT, 'specialAttack2SkillName')
        if bs and db.has_record(bs):
            need = str(gv(bs, 'skillSpecialAnimationName') or '').strip()
            if need and need != _AOE360_REF:
                p.append("R-247.5a r3: specialAttack2 skill declares anim %r "
                         "but this module binds only %r - the kept cast slot "
                         "is dead again" % (need, _AOE360_REF))
        # 6b: the spear chain, byte-proven end to end on the NEW rig
        if float(gv(_HUNT, 'chanceToEquipRightHand') or 0) < 100.0:
            p.append("R-247.6b: Hunt chanceToEquipRightHand=%r != 100"
                     % gv(_HUNT, 'chanceToEquipRightHand'))
        rh = gl(_HUNT, 'lootRightHandItem1')
        if not rh or 'runbreaker_guaranteed' not in _norm(rh[0]):
            p.append("R-247.6b: Hunt lootRightHandItem1=%r does not lead with "
                     "the Runbreaker guaranteed tables" % (rh,))
        if db.has_record(_RUNBREAKER_N):
            tgt = gv(_RUNBREAKER_N, 'lootName1')
            if not (tgt and db.has_record(tgt) and
                    gv(tgt, 'Class') == 'WeaponHunting_Spear'):
                p.append("R-247.6b: runbreaker_guaranteed_n -> %r is not a live "
                         "spear record" % tgt)
        else:
            p.append("R-247.6b: runbreaker_guaranteed_n missing")
        anm = db.get_fields(_HUNT_ANM) or {}
        spear_rows = [k for k, tf in anm.items()
                      if 'spearattackanim' in k.split('###')[0].lower()
                      and tf.values and str(tf.values[0]).strip()]
        run_rows = [k for k, tf in anm.items()
                    if k.split('###')[0] == 'unarmedRunAnim'
                    and tf.values and str(tf.values[0]).strip()]
        if not spear_rows:
            p.append("R-247.6b: anm_skeleton01 binds no spearAttackAnim - the "
                     "spear would never swing on the new rig")
        if not run_rows:
            p.append("R-247.5a: anm_skeleton01 binds no unarmedRunAnim - D19")

    # ---- ruling 6c: the soul summons him -----------------------------------
    if not db.has_record(_HUNT_SUMMON):
        p.append("R-247.6c: summon_toxeus_hunt missing")
    else:
        anim = gv(_HUNT_SUMMON, 'skillSpecialAnimationName')
        if anim and str(anim).strip():
            p.append("R-247.6c: the summon declares anim %r - never fires" % anim)
        objs = gl(_HUNT_SUMMON, 'spawnObjects')
        if [_norm(o) for o in objs] != [_norm(x) for x in _HUNT_PETS]:
            p.append("R-247.6c: summon spawnObjects=%r != the 3 hunt pets" % (objs,))
    for i, pet in enumerate(_HUNT_PETS):
        if not db.has_record(pet):
            p.append("R-247.6c: hunt pet missing: %s" % pet)
            continue
        ttl = gl(pet, 'spawnObjectsTimeToLive')
        if any(float(v or 0) > 0 for v in ttl):
            p.append("R-247.6c: %s carries spawnObjectsTimeToLive=%r - a "
                     "permanent pet must be TTL-free" % (pet, ttl))
        hostile = r'svc_hunt_summoncoursers'
        blob = ' '.join(str(v) for k, tf in (db.get_fields(pet) or {}).items()
                        for v in (tf.values or []) if isinstance(v, str)).lower()
        if hostile in blob:
            p.append("R-247.6c: %s still references the HOSTILE huntsman summon "
                     "- a player pet must never raise enemies" % pet)
    for soul, lvl in zip(_HUNT_SOULS, (1, 2, 3)):
        if not db.has_record(soul):
            p.append("R-247.6c: hunt soul missing: %s" % soul)
            continue
        if _norm(gv(soul, 'itemSkillName') or '') != _norm(_HUNT_SUMMON):
            p.append("R-247.6c: %s grants %r, not the summon"
                     % (soul, gv(soul, 'itemSkillName')))
        if int(gv(soul, 'itemSkillLevel') or 0) != lvl:
            p.append("R-247.6c: %s itemSkillLevel=%r != %d (the tier ladder)"
                     % (soul, gv(soul, 'itemSkillLevel'), lvl))
        ac = gv(soul, 'itemSkillAutoController')
        if ac and str(ac).strip():
            p.append("R-247.6c: %s still carries an autocast controller %r - a "
                     "180s manual summon would be burned on any hit" % (soul, ac))

    # ---- ruling 6d: the ladders are real and visible -----------------------
    for fam, (pets, _fb) in _PET_FAMILIES.items():
        lifes, descs = [], []
        for pet in pets:
            if not db.has_record(pet):
                p.append("R-247.6d: %s pet missing: %s" % (fam, pet))
                break
            lifes.append(float(gv(pet, 'characterLife') or 0))
            descs.append(gv(pet, 'description') or '')
        else:
            if not (lifes[0] < lifes[1] < lifes[2]):
                p.append("R-247.6d: %s pet life %s does not strictly ascend"
                         % (fam, lifes))
            if lifes[0] > 0 and lifes[1] < lifes[0] * 1.4:
                p.append("R-247.6d: %s epic pet %.0f < 1.4x normal %.0f - not "
                         "'much stronger'" % (fam, lifes[1], lifes[0]))
            if lifes[0] > 0 and lifes[2] < lifes[0] * 2.2:
                p.append("R-247.6d: %s legendary pet %.0f < 2.2x normal %.0f - "
                         "not 'much stronger'" % (fam, lifes[2], lifes[0]))
            if len(set(descs)) != 3:
                p.append("R-247.6d: %s tiers share display tags %s - the ladder "
                         "is invisible in-game again" % (fam, descs))
            for tier in (2, 3):
                tag = _TIER_TAG[(fam, tier)]
                if tags and tag not in tags:
                    p.append("R-247.6d: tier tag %s not in the text manifest" % tag)

    # ---- ruling 6e: the +all-skills law ------------------------------------
    for lvl, souls in _FAMILY_SOULS.items():
        for soul in souls:
            got = gv(soul, 'augmentAllLevel')
            try:
                ok = int(got) == lvl and not isinstance(got, float)
            except (TypeError, ValueError):
                ok = False
            if not ok:
                p.append("R-247.6e: %s augmentAllLevel=%r != %d (INT)"
                         % (soul, got, lvl))

    # ---- ruling 6a: the formula chain, every link --------------------------
    if gv(_FORMULA, 'itemClassification') != _FORMULA_CLASSIFICATION:
        p.append("R-247.6a: formula itemClassification=%r != %s"
                 % (gv(_FORMULA, 'itemClassification'), _FORMULA_CLASSIFICATION))
    if db.has_record(_RITE_TABLE):
        if _norm(gv(_RITE_TABLE, 'lootName1') or '') != _norm(_FORMULA):
            p.append("R-247.6a: svc_rite_guaranteed lootName1=%r != the formula"
                     % gv(_RITE_TABLE, 'lootName1'))
        if int(gv(_RITE_TABLE, 'lootWeight1') or 0) != 100:
            p.append("R-247.6a: svc_rite_guaranteed weight=%r != 100"
                     % gv(_RITE_TABLE, 'lootWeight1'))
    else:
        p.append("R-247.6a: svc_rite_guaranteed missing")
    if db.has_record(_HUNT):
        m4 = gl(_HUNT, 'lootMisc4Item1')
        if not m4 or any(_norm(v) != _norm(_RITE_TABLE) for v in m4):
            p.append("R-247.6a: Hunt lootMisc4Item1=%r - the guaranteed formula "
                     "row moved" % (m4,))
        if float(gv(_HUNT, 'chanceToEquipMisc4') or 0) < 100.0:
            p.append("R-247.6a: Hunt chanceToEquipMisc4=%r != 100"
                     % gv(_HUNT, 'chanceToEquipMisc4'))
    # every link of craft -> summon: formula -> soul -> summon -> pet
    art = gv(_FORMULA, 'artifactName')
    if _norm(art or '') != _norm(_EOAT_SOUL) or not db.has_record(_EOAT_SOUL):
        p.append("R-247.6a: formula artifactName=%r does not resolve to the "
                 "EoAT soul" % art)
    for i in (1, 2, 3):
        rg = gv(_FORMULA, 'reagent%dBaseName' % i)
        if not (rg and db.has_record(rg)):
            p.append("R-247.6a: formula reagent%d=%r does not resolve" % (i, rg))
    if _norm(gv(_EOAT_SOUL, 'itemSkillName') or '') != _norm(_EOAT_SUMMON):
        p.append("R-247.6a: EoAT soul grants %r, not its summon"
                 % gv(_EOAT_SOUL, 'itemSkillName'))
    if db.has_record(_EOAT_SUMMON):
        anim = gv(_EOAT_SUMMON, 'skillSpecialAnimationName')
        if anim and str(anim).strip():
            p.append("R-247.6a: EoAT summon declares anim %r - never fires" % anim)
        objs = gl(_EOAT_SUMMON, 'spawnObjects')
        dead = [o for o in objs if not db.has_record(o)]
        if not objs or dead:
            p.append("R-247.6a: EoAT summon spawnObjects unresolved: %r" % (dead,))
    else:
        p.append("R-247.6a: summon_toxeus_eoat missing")

    if p:
        for x in p:
            print("  R247 OFFENDER: %s" % x)
        raise SystemExit("r247_boss_forms.verify FAILED: %d problem(s)" % len(p))
    print("  [r247_boss_forms].verify OK: Lethaeus core is the escalation "
          "(kit intact); the Hunt is an Undead giant skeleton on the family "
          "rig, every inline clip rig-proven, spear + unarmed rows fully "
          "bound on both surfaces with 'AoE360' castable on each (r3), and a "
          "byte-proven spear chain; his soul summons him at 1/2/3 with "
          "TTL-free pets that raise no enemies; all three family ladders "
          "strictly ascend with visible per-tier names; the +all-skills law "
          "is 1/2/3 (+EoAT 3, INT); the formula is Legendary-classified with "
          "its guaranteed 100%% drop and the full craft->summon chain "
          "resolving.")
    return tags


def _negtest():
    """py tools/patches/r247_boss_forms.py --negtest (verify-level plants)"""
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = v

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return _norm(n) in {_norm(k) for k in self.d}

        def record_names(self):
            return list(self.d)

        def _k(self, n):
            for k in self.d:
                if _norm(k) == _norm(n):
                    return k
            return n

        def get_fields(self, n):
            f = self.d.get(self._k(n))
            if f is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in f.items())

        def get_field_value(self, n, f):
            return self.d.get(self._k(n), {}).get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(self._k(n), {})[f] = v if isinstance(v, list) else [v]

    def _base():
        db = _Stub()
        db.d[_SHELL] = {'characterLife': [14000.0, 19000.0, 25000.0],
                        'scale': [2.9], 'actorHeight': [2.4],
                        'handHitDamageMax': [284.0]}
        # the core's REAL shipped kit (round-3 correction; see _CORE_KIT_SENTINELS)
        db.d[_CORE] = {'characterLife': list(_CORE_LIFE),
                       'scale': [_CORE_SCALE], 'actorHeight': [_CORE_HEIGHT],
                       'handHitDamageMax': [_CORE_HAND[1]],
                       'skillName4': ['records\\skills\\sv\\refnat\\chainconvert.dbr'],
                       'skillName5': ['records\\skills\\sv\\refnat\\chainconvert_cascade.dbr'],
                       'initialSkillName': ['records\\skills\\monster skills\\buff_self\\mnemophage_mindshroud.dbr'],
                       'skillName7': ['records\\skills\\monster skills\\attack_radius\\breach_shadowgrasp.dbr'],
                       'skillName9': ['records\\skills\\monster skills\\passive_buffs\\shadowstalker_distortionfield.dbr']}
        anm = {'spearAttackAnim1': ['spear_a.anm'],
               'spearAttackAnim2': ['spear_b.anm'],
               'spearRunAnim': ['run.anm'], 'spearWalkAnim': ['walk.anm'],
               'spearAttackIdleAnim': ['idle.anm'],
               'spearDieAnim1': ['die.anm'], 'spearStunAnim': ['stun.anm'],
               'spearSpawnAnim': ['spawn.anm'],
               'unarmedAttackAnim1': ['una_a.anm'],
               'unarmedAttackAnim2': ['una_b.anm'],
               'unarmedRunAnim': ['b.anm'], 'unarmedWalkAnim': ['walk.anm'],
               'unarmedAttackIdleAnim': ['idle.anm'],
               'unarmedDieAnim1': ['die.anm'], 'unarmedStunAnim': ['stun.anm'],
               'unarmedSpawnAnim': ['spawn.anm'],
               _AOE360_SRC_REF: [_AOE360_REF], _AOE360_SRC: ['aoe360.anm']}
        db.d[_HUNT_ANM] = anm
        hunt = {'mesh': [_HUNT_MESH], 'baseTexture': [_HUNT_SKIN],
                'charAnimationTableName': [_HUNT_ANM],
                'characterRacialProfile': [_HUNT_RACE],
                'chanceToEquipRightHand': [100.0],
                'lootRightHandItem1': [
                    _RUNBREAKER_N,
                    _RUNBREAKER_N.replace('_n', '_e'),
                    _RUNBREAKER_N.replace('_n', '_l')],
                'lootMisc4Item1': [_RITE_TABLE] * 3,
                'chanceToEquipMisc4': [100.0]}
        # the round-3 inline rebind, mirrored exactly (both-surfaces law)
        for dst, src in _INLINE_REBIND.items():
            hunt[dst] = list(anm[src])
        for row in _AOE360_ROWS:
            hunt[row + 'SpecialAnimRef1'] = [_AOE360_REF]
            hunt[row + 'SpecialAnim1'] = list(anm[_AOE360_SRC])
        db.d[_HUNT] = hunt
        db.d[_RUNBREAKER_N] = {
            'lootName1': [r'records\item\equipmentweapon\spear\svc_n_runbreaker.dbr'],
            'lootWeight1': [100]}
        db.d[r'records\item\equipmentweapon\spear\svc_n_runbreaker.dbr'] = {
            'Class': ['WeaponHunting_Spear']}
        db.d[_HUNT_SUMMON] = {'spawnObjects': list(_HUNT_PETS)}
        for i, pth in enumerate(_HUNT_PETS):
            db.d[pth] = {'characterLife': [_HUNT_PET_LIFE[i]],
                         'description': ['tagSVCPetToxeusHunt' if i == 0 else
                                         _TIER_TAG[('hunt', i + 1)]],
                         'spawnObjectsTimeToLive': []}
        for fam, (pets, _fb) in _PET_FAMILIES.items():
            if fam == 'hunt':
                continue
            base = {'enslaver': 13000.0, 'blood': 12000.0}[fam]
            for i, pth in enumerate(pets):
                db.d[pth] = {'characterLife': [base * (1, 1.5 * 18 / 13, 1.75 * 24 / 13)[i]
                                               if fam == 'enslaver' else
                                               base * (1, 2.25, 3.79)[i]],
                             'description': ['tag%sBase' % fam if i == 0 else
                                             _TIER_TAG[(fam, i + 1)]]}
        for lvl, souls in _FAMILY_SOULS.items():
            for soul in souls:
                db.d.setdefault(soul, {})['augmentAllLevel'] = [lvl]
        for soul, lvl in zip(_HUNT_SOULS, (1, 2, 3)):
            db.d[soul]['itemSkillName'] = [_HUNT_SUMMON]
            db.d[soul]['itemSkillLevel'] = [lvl]
        db.d[_FORMULA] = {'itemClassification': [_FORMULA_CLASSIFICATION],
                          'artifactName': [_EOAT_SOUL],
                          'reagent1BaseName': [_EOAT_SOUL],
                          'reagent2BaseName': [_EOAT_SOUL],
                          'reagent3BaseName': [_EOAT_SOUL]}
        db.d[_RITE_TABLE] = {'lootName1': [_FORMULA], 'lootWeight1': [100]}
        db.d[_EOAT_SOUL]['itemSkillName'] = [_EOAT_SUMMON]
        db.d[_EOAT_SUMMON] = {'spawnObjects': [_HUNT_PETS[0]]}
        tags = {t: 'x' for t in
                [_TIER_TAG[k] for k in _TIER_TAG] + [_TAG_HUNT_PET]}
        return db, tags

    plants = [
        ('Lethaeus core shrinks again',
         lambda db, t: db.d[_CORE].__setitem__('scale', [1.8])),
        ('Lethaeus core life falls below the shell',
         lambda db, t: db.d[_CORE].__setitem__('characterLife',
                                               [7000.0, 9500.0, 12500.0])),
        ('Lethaeus loses a kit signature',
         lambda db, t: db.d[_CORE].__delitem__('initialSkillName')),
        ('the Hunt goes back to the demon body',
         lambda db, t: db.d[_HUNT].__setitem__(
             'mesh', ['Creatures\\Monster\\ShadowStalker\\ShadowStalker.msh'])),
        ('a foreign-rig inline anim row returns',
         lambda db, t: db.d[_HUNT].__setitem__(
             'spearAttackAnim1', ['Creatures\\Monster\\Maenad\\ANM\\x.anm'])),
        ('a live spear slot goes empty again (the round-2 defect)',
         lambda db, t: db.d[_HUNT].__setitem__('spearRunAnim', [''])),
        ('the spear row loses its AoE360 binding (bladestorm dies)',
         lambda db, t: db.d[_HUNT].__setitem__('spearSpecialAnimRef1', [''])),
        ('the AoE360 clip goes foreign to the rig',
         lambda db, t: db.d[_HUNT].__setitem__('unarmedSpecialAnim1',
                                               ['foreign.anm'])),
        ('the spear equip chain breaks',
         lambda db, t: db.d[_HUNT].__setitem__('chanceToEquipRightHand', [0.0])),
        ('a hunt soul stops granting the summon',
         lambda db, t: db.d[_HUNT_SOULS[2]].__setitem__(
             'itemSkillName', ['records\\skills\\monster skills\\attack_direct'
                               '\\svc_hunt_quarrysmark.dbr'])),
        ('the tier ladder collapses to one strength',
         lambda db, t: db.d[_PET_FAMILIES['enslaver'][0][2]].__setitem__(
             'characterLife', [13000.0])),
        ('two tiers share one display name again',
         lambda db, t: db.d[_PET_FAMILIES['blood'][0][2]].__setitem__(
             'description', db.d[_PET_FAMILIES['blood'][0][1]]['description'])),
        ('the +all-skills law drifts',
         lambda db, t: db.d[_FAMILY_SOULS[3][0]].__setitem__(
             'augmentAllLevel', [1])),
        ('the formula goes Common again',
         lambda db, t: db.d[_FORMULA].__setitem__('itemClassification',
                                                  ['Common'])),
        ('the guaranteed drop row is unhooked',
         lambda db, t: db.d[_HUNT].__setitem__('lootMisc4Item1', [])),
    ]
    db, tags = _base()
    try:
        verify(db, tags)
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        db, tags = _base()
        plant(db, tags)
        try:
            verify(db, tags)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    _sys.exit(_negtest() if '--negtest' in _sys.argv else 0)
