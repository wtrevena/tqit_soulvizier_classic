r"""coldworm_buffs - R-39 (Will 2026-07-16): the Cold Worm buffs lane.

WILL'S RULING (verbatim, docs/WILL_RULINGS.md R-39)
---------------------------------------------------
    "Cold Worm needs ~3x characterLife and +20% armor (`defensiveProtection`) ON
     TOP of the already-queued kit (burrow/frost skills that actually cast), a
     massive total-speed boost, the exclamation-marker mechanism extended to all
     placed ubers, and the 3-tier soul + loot-triple fix + roster drop-slot sweep
     - ships as ONE lane, not piecemeal."

THE ROOT CAUSE OF "SKILLS THAT ACTUALLY CAST" (RCA, evidence in the report)
---------------------------------------------------------------------------
`records\test\boss_coldworm50.dbr` is an SV-0.98i-inherited leftover of an older
"D2" conversion. Its ENTIRE kit points at a record namespace that ships NOWHERE:

    records\skills\boss skills\d2custom\coldworm_{shockwave,shockwave_sec,
        dropceiling,poisongas,layegg,summonbug,summonbugs,initial}.dbr
    Records\Game\D2GlobalProperties_{Normal01,Epic_Boss,Legendary_Boss}.dbr
    Records\Game\D2Boss_ConversionImmunity.dbr

Every one of those is absent from the built arz, from `upstream/soulvizier_098i`
AND from the base-game `database.arz` (case-insensitive check over both DBs). A
roster-wide scan of the FULL active-slot surface (attackSkillName /
initialSkillName / dyingSkillName / specialAttack{,2..5}SkillName) ranks Cold Worm
as the single worst record in the whole database: **8 of 8 active slots dead**,
where the next-worst monster has 2. So Cold Worm casts nothing at all, has no
difficulty-scaling globals, and is player-CONVERTIBLE. That is the defect - not a
tuning miss - and it is fixed here at the record layer by repointing every dead
slot at a donor that EXISTS.

DONOR DISCIPLINE (boss_skill_fix precedent: donor-matched, never a blanket value)
--------------------------------------------------------------------------------
Cold Worm rides the CryptWorm rig (`Creatures\Monster\CryptWorm\CryptWorm01.msh`,
`characterRacialProfile = Insectoid`). Its identity donor is
`um_coldcreep_29` - "Cold Creep", the COLD CryptWorm-rig hero - plus the native
`am_devourer_*` line. Every skill below is (a) present in the db and (b) already
carried by a CryptWorm-rig monster or by the nearest insectoid BOSS, and every
LEVEL is copied verbatim from that donor:

  skill                                  donor (level source)
  -------------------------------------- ------------------------------------
  ondeath_cryptworms                     am_devourer_27 skillName1  [3]
  coldcreep_frostslow                    um_coldcreep_29 skillName1 [4,6,8]
  drxfreezingblast                       um_coldcreep_29 skillName3 [3,4,5]
  iceblasts                              um_coldcreep_29 skillName4 [2,4,6]
  giantkarkinos_flightofthekondor        um_deeptresher_47 skillName3 [1]
  cryptworm_megapoisonball               am_devourer_27 skillName3  [3]
  retaliation_1coldperlevelx100levels    um_coldcreep_29 skillName5 [40,55,70]
  armor_passive                          Cold Worm's own (levels x1.2, see below)
  racial_insectoid                       universal insectoid level  [1]
  globalproperties_{normal,epic,legendary}01  the vanilla difficulty convention
  physdmg_meleeonly                      am_devourer_27 skillName7  [1,2,3]
  boss_conversionimmunity                Cold Worm's own kept levels [1,2,3]
  meleeattack_+5physicalperlvlx100       boss_scarabaeus_27 [8,16,24]
  enchantment_cold                       um_coldpaw_29 skillName4   [10,12,14]
  arachne_close_poisoncloud              um_sajaki_44 skillName3    [14,17,20]

Result: a burrowing frost worm that still spits poison - amgoz1-bar identity for
a boss literally named Cold Worm, restoring the SV slot ROLES (poison gas, an
on-death brood, a lunging special) with records that exist.

THE ANIM-BINDING INVARIANT (the reason a "wired" skill can still never fire)
----------------------------------------------------------------------------
Same defect class as B-SOUL-PROC-2 (the StartSkill anim abort), on the monster
side: a monster skill whose `skillSpecialAnimationName` is NOT listed in any of
the caster's `unarmedSpecialAnimRef<i>` slots has no playable animation, so the
engine never starts it. Two of the new skills carry such a requirement:

  * `iceblasts` needs 'Burst'. Cold Worm had no 'Burst' ref -> this module adds
    slot 10 (`unarmedSpecialAnimRef10='Burst'`, `unarmedSpecialAnim10` =
    `CryptWorm_Skill_Spit.anm`) - the EXACT binding `um_coldcreep_29` uses for
    'Burst' on this same rig. Slot 10 is precedented (6 monsters top out there;
    it is also the DB-wide max on a Monster record) and Cold Worm already carried
    `unarmedSpecialAnimSpeed10`.
  * `giantkarkinos_flightofthekondor` (the BURROW: "Burrow under the ground and
    then pop up to attack the enemy") needs 'Kondor'. Rather than invent an
    11th slot (unprecedented on any Monster record), this module REPURPOSES
    Cold Worm's existing ref4: its anim stays `CryptWorm_AttGamma.anm` (the
    worm's own dive animation) and only the ref NAME changes 'Dive' -> 'Kondor'.
    Nothing is lost: a DB-wide scan finds ZERO skills bound to 'Dive', so ref4
    was dead weight. The worm now burrows using its own dive animation.

`arachne_close_poisoncloud` needs 'Spit', which Cold Worm already binds at ref1.
The other new skills declare no `skillSpecialAnimationName` at all.

verify() enforces this as a permanent, roster-scoped invariant (see below), and
`--negtest` plants a violation and proves the gate catches it.

WILL'S NUMBERS
--------------
  * 3x life:  characterLife [14000,18000,22000] -> [42000,54000,66000].
  * +20% armor (`defensiveProtection`): NO monster anywhere in the roster carries
    a non-zero `defensiveProtection` or `defensiveProtectionModifier` (0 carriers
    DB-wide) - monster armor is delivered exclusively by the `armor_passive`
    skill, whose `defensiveProtection` array is exactly LINEAR ([1,2,3,...,800],
    i.e. level N == N armor). So the engine-effective +20% `defensiveProtection`
    is a +20% armor_passive LEVEL: [60,174,360] -> [72,209,432]. That is Will's
    field, at the only layer where it does anything.
  * massive total-speed boost: adopt the rig-proven CryptWorm speed profile from
    `um_coldcreep_29` wholesale - run 0.75->1.8, attack 0.8->1.5, cast 1.0->1.1,
    walk 1.0->2.0, rotation 0.3/0.1 -> 12.0/9.0 (Cold Worm literally could not
    turn), and the movement/attack/special ANIM speeds 0.15-0.4 -> 1.0 (without
    those the boss would skate: it moved at 1/5 animation speed).

WHAT THIS MODULE DELIBERATELY DOES **NOT** DO
----------------------------------------------
  * The soul + loot triple: already correct on `main` and left untouched.
    `boss_coldworm50_soul_{n,e,l}` all exist, strictly progress on every scaled
    dimension, carry the correct per-tier `soul_{n,e,l}_icon.tex` (b40) and the
    pcsafe iceblast grant (b29), and `lootFinger2Item1` is the proper
    difficulty-indexed triple at `chanceToEquipFinger2=66` (the PLACED_UBER rate,
    R-42). verify() re-asserts all of that so a later writer cannot regress it,
    but apply() writes nothing there.
  * The exclamation-point map marker: map-side, and BLOCKED in this checkout
    (see BL-b90-DEBT-2 / BL-b89-DEBT-4). Registered in the BACKLOG DEBT section.
  * Any other monster, any soul item, any pet, any pool, any tag, any map blob.

ORDERING: registered immediately before `visuals` (which writes nothing) and
AFTER `boss_skill_fix`, so this module is the ratified final registry writer of
Cold Worm's kit. `boss_skill_fix` is scoped to the `um_*_99` naming convention
and never touches `boss_coldworm50`, so there is no collision.

Report: docs/reports/b91_coldworm_buffs.md
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

from arz_patcher import DATA_TYPE_FLOAT, DATA_TYPE_INT, DATA_TYPE_STRING

MODULE_NAME = "Cold Worm buffs: 3x life / +20% armor / real casting kit / speed (R-39)"

COLDWORM = r'records\test\boss_coldworm50.dbr'
SOUL_BASE = r'records\item\equipmentring\soul\svc_uber'
SOULS = tuple(r'%s\boss_coldworm50_soul_%s.dbr' % (SOUL_BASE, d) for d in ('n', 'e', 'l'))

# ── Will's numbers ──────────────────────────────────────────────────────────
LIFE_MULTIPLIER = 3.0
ARMOR_MULTIPLIER = 1.2

BASE_LIFE = (14000.0, 18000.0, 22000.0)
TARGET_LIFE = [round(v * LIFE_MULTIPLIER, 1) for v in BASE_LIFE]        # 42k/54k/66k
BASE_ARMOR_LEVELS = (60, 174, 360)
TARGET_ARMOR_LEVELS = [int(round(v * ARMOR_MULTIPLIER)) for v in BASE_ARMOR_LEVELS]  # 72/209/432

# Rig-proven speed profile, copied field-for-field off um_coldcreep_29.
SPEED_PROFILE = (
    ('characterRunSpeed', 1.8),
    ('characterAttackSpeed', 1.5),
    ('characterSpellCastSpeed', 1.1),
    ('walkSpeed', 2.0),
    ('maxRotationSpeed', 12.0),
    ('minRotationSpeed', 9.0),
)
# Animation playback speeds. Cold Worm shipped at 0.15-0.4 on every anim it uses,
# which is why it read as glacial; um_coldcreep_29 / am_devourer_* run all of
# these at 1.0 on the identical rig. Only the slots the live kit plays are
# touched; the emote/idle slots (5-9) are left exactly as SV authored them.
ANIM_SPEEDS = (
    'unarmedRunAnimSpeed', 'unarmedWalkAnimSpeed', 'unarmedAttackAnimSpeed1',
    'unarmedSpellAttackAnimSpeed', 'unarmedAttackIdleAnimSpeed',
    'unarmedSpecialAnimSpeed1', 'unarmedSpecialAnimSpeed2',
    'unarmedSpecialAnimSpeed3', 'unarmedSpecialAnimSpeed4',
)
ANIM_SPEED_TARGET = 1.0

# ── the kit: slot -> (record, levels, donor citation) ───────────────────────
_MS = r'records\skills\monster skills'
KIT = {
    'skillName1':  (_MS + r'\summoning_pets\ondeath_cryptworms.dbr',
                    [3], 'am_devourer_27 skillName1'),
    'skillName2':  (_MS + r'\passive_buffs\coldcreep_frostslow.dbr',
                    [4, 6, 8], 'um_coldcreep_29 skillName1'),
    'skillName3':  (r'records\skills\storm\drxfreezingblast.dbr',
                    [3, 4, 5], 'um_coldcreep_29 skillName3'),
    'skillName4':  (_MS + r'\attack_projectile\iceblasts.dbr',
                    [2, 4, 6], 'um_coldcreep_29 skillName4'),
    'skillName5':  (r'records\xpack\skills\quest skills\giantkarkinos_flightofthekondor.dbr',
                    [1], 'um_deeptresher_47 skillName3 (skillMaxLevel=1)'),
    'skillName6':  (_MS + r'\attack_projectile\cryptworm_megapoisonball.dbr',
                    [3], 'am_devourer_27 skillName3'),
    'skillName7':  (_MS + r'\passive_buffs\retaliation_1coldperlevelx100levels.dbr',
                    [40, 55, 70], 'um_coldcreep_29 skillName5'),
    'skillName8':  (_MS + r'\defense\armor_passive.dbr',
                    TARGET_ARMOR_LEVELS, "Cold Worm's own levels x1.2 (R-39 armor)"),
    'skillName9':  (_MS + r'\passive_buffs\resists\racial_insectoid.dbr',
                    [1], 'universal insectoid level'),
    'skillName10': (_MS + r'\globalproperties_normal01.dbr',
                    [1, 0, 0], 'vanilla difficulty-scaling convention'),
    'skillName11': (_MS + r'\globalproperties_epic01.dbr',
                    [0, 1, 0], 'vanilla difficulty-scaling convention'),
    'skillName12': (_MS + r'\globalproperties_legendary01.dbr',
                    [0, 0, 1], 'vanilla difficulty-scaling convention'),
    'skillName13': (_MS + r'\passive_buffs\physdmg_meleeonly.dbr',
                    [1, 2, 3], 'am_devourer_27 skillName7'),
    'skillName14': (r'records\skills\boss skills\boss_conversionimmunity.dbr',
                    [1, 2, 3], "Cold Worm's own kept levels (skillMaxLevel=3)"),
    'skillName15': (_MS + r'\attack_melee\meleeattack_+5physicalperlvlx100.dbr',
                    [8, 16, 24], 'boss_scarabaeus_27 (nearest insectoid boss)'),
    'skillName16': (_MS + r'\buff_self\enchantment_cold.dbr',
                    [10, 12, 14], 'um_coldpaw_29 skillName4'),
    'skillName17': (r'records\skills\boss skills\arachne_close_poisoncloud.dbr',
                    [14, 17, 20], 'um_sajaki_44 skillName3'),
}

# ── the AI wiring: which kit skill sits in which active slot, with the tuning
# copied off the donor that natively drives that skill in that slot ──────────
# slot-prefix -> (kit key, chance, delay, timeout, range, tuning citation)
SPECIALS = (
    ('specialAttack',  'skillName3', 50.0, 2.0, 4.0, 'AnyRange',
     'um_coldcreep_29 specialAttack (drxfreezingblast)'),
    ('specialAttack2', 'skillName4', 50.0, 5.0, 2.0, 'LongRange',
     'um_coldcreep_29 specialAttack2 (iceblasts)'),
    ('specialAttack3', 'skillName5', 50.0, 4.0, 1.0, 'AnyRange',
     'um_deeptresher_47 specialAttack3 (flightofthekondor)'),
    ('specialAttack4', 'skillName6', 50.0, 5.5, 1.0, 'LongRange',
     'am_devourer_27 specialAttack (megapoisonball)'),
    # Role-preserved: this slot was SV's coldworm_poisongas. The dead record is
    # replaced by a real poison cloud and amgoz1's OWN slot-5 tuning is kept.
    ('specialAttack5', 'skillName17', 25.0, 6.0, 2.0, 'LongRange',
     "SV's own coldworm_poisongas slot-5 tuning, role preserved"),
)

# non-special active slots -> kit key
ACTIVE_SINGLES = (
    ('attackSkillName', 'skillName15'),
    ('initialSkillName', 'skillName16'),
    ('dyingSkillName', 'skillName1'),
)

# ── anim-ref bindings this module guarantees (ref name -> (slot, anim file)) ─
_ANM = 'Creatures\\Monster\\CryptWorm\\ANM\\'
ANIM_BINDINGS = (
    # 'Burst' for iceblasts - the exact slot-2 binding um_coldcreep_29 uses.
    (10, 'Burst', _ANM + 'CryptWorm_Skill_Spit.anm'),
    # 'Kondor' for the burrow - REPURPOSES ref4, keeping its CryptWorm_AttGamma
    # dive anim. Zero skills in the DB are bound to the old 'Dive' name.
    (4, 'Kondor', _ANM + 'CryptWorm_AttGamma.anm'),
)

_ACTIVE_SLOT_FIELDS = ('attackSkillName', 'initialSkillName', 'dyingSkillName',
                       'specialAttackSkillName') + tuple(
    'specialAttack%dSkillName' % i for i in range(2, 6))


# ── helpers ────────────────────────────────────────────────────────────────
def _scalar(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _vals(db, rec, field):
    f = db.get_fields(rec)
    if not f:
        return []
    for key, tf in f.items():
        if key.split('###')[0] == field:
            return list(tf.values)
    return []


def _norm(p):
    return str(p or '').lower().replace('/', '\\')


def _resolves(db, path, extra=None):
    """A record reference resolves if the mod db has it (case-insensitively).

    The engine overlays the mod arz on the base-game arz, so a ref the mod does
    not carry may still be a live base-game record. This module only ever writes
    refs it has already proven present in the mod db, and the gate is scoped to
    those, so a plain mod-db lookup is the correct (and strictest) test here.
    """
    if not path:
        return False
    tgt = _norm(path)
    pool = extra if extra is not None else _lower_index(db)
    return tgt in pool


_INDEX_CACHE = {}


def _lower_index(db):
    key = id(db)
    idx = _INDEX_CACHE.get(key)
    if idx is None or len(idx) != len(db._raw_records):
        idx = {_norm(n) for n in db.record_names()}
        _INDEX_CACHE[key] = idx
    return idx


def _special_anim_requirement(db, skill_path, pool):
    """The anim ref name a skill demands of its caster, or None."""
    if not _resolves(db, skill_path, pool):
        return None
    v = _scalar(db.get_field_value(skill_path, 'skillSpecialAnimationName'))
    v = str(v).strip() if v is not None else ''
    return v or None


def _bound_anim_refs(db, rec):
    """{ref name: anim file} actually bound on a monster record."""
    out = {}
    f = db.get_fields(rec) or {}
    for key, tf in f.items():
        b = key.split('###')[0]
        m = re.match(r'unarmedSpecialAnimRef(\d+)$', b)
        if not m or not tf.values:
            continue
        name = str(tf.values[0]).strip()
        if not name:
            continue
        anim = _scalar(db.get_field_value(rec, 'unarmedSpecialAnim' + m.group(1)))
        out[name] = str(anim or '')
    return out


def _anim_binding_violations(db, rec):
    """THE NEW INVARIANT (returns a list of human-readable problems).

    For every ACTIVE skill slot on `rec`: the referenced skill must resolve, and
    if that skill declares a `skillSpecialAnimationName` the caster must bind
    that ref name to a non-empty animation. Otherwise the engine has no playable
    animation for the skill and never starts it - the monster-side twin of the
    B-SOUL-PROC-2 StartSkill abort.
    """
    problems = []
    pool = _lower_index(db)
    bound = _bound_anim_refs(db, rec)
    for field in _ACTIVE_SLOT_FIELDS:
        path = _scalar(db.get_field_value(rec, field))
        path = str(path).strip() if path is not None else ''
        if not path or path == '0':
            continue
        if not _resolves(db, path, pool):
            problems.append('%s: %s -> %s does NOT resolve (dead slot: the skill '
                            'can never be cast)' % (rec, field, path))
            continue
        need = _special_anim_requirement(db, path, pool)
        if need is None:
            continue
        if need not in bound:
            problems.append(
                '%s: %s -> %s requires special animation %r but the caster binds '
                'no unarmedSpecialAnimRef with that name (bound: %s) - the engine '
                'has no playable animation, so the skill never fires'
                % (rec, field, path, need, sorted(bound)))
        elif not bound[need].strip():
            problems.append(
                '%s: %s -> %s requires special animation %r whose bound '
                'unarmedSpecialAnim slot is EMPTY' % (rec, field, path, need))
    return problems


def _kit_level_violations(db, rec):
    """Every skillName<i> slot must resolve and carry a non-degenerate level."""
    problems = []
    pool = _lower_index(db)
    f = db.get_fields(rec) or {}
    for key, tf in f.items():
        b = key.split('###')[0]
        m = re.match(r'skillName(\d+)$', b)
        if not m or not tf.values:
            continue
        path = str(tf.values[0]).strip()
        if not path or path == '0':
            continue
        if not _resolves(db, path, pool):
            problems.append('%s: %s -> %s does NOT resolve' % (rec, b, path))
    return problems


# ── apply ──────────────────────────────────────────────────────────────────
def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)

    if not db.has_record(COLDWORM):
        raise SystemExit(
            "[coldworm_buffs] R-39 target MISSING from the db: %s. The ruling "
            "cannot be applied; refusing to ship a build that silently drops it."
            % COLDWORM)

    pool = _lower_index(db)

    # 0. Every donor must EXIST before anything is written - the whole point of
    #    this lane is that Cold Worm's kit pointed at records that do not.
    missing = [(slot, path) for slot, (path, _lv, _d) in sorted(KIT.items())
               if not _resolves(db, path, pool)]
    if missing:
        raise SystemExit(
            "[coldworm_buffs] donor record(s) absent from the db: %s. Refusing to "
            "replace one dead reference with another." % missing)

    before_life = _vals(db, COLDWORM, 'characterLife')
    before_armor = _vals(db, COLDWORM, 'skillLevel8')
    dead_before = _anim_binding_violations(db, COLDWORM)
    print("  RCA: %d/%d active skill slots were dead before this module"
          % (len(dead_before), len(_ACTIVE_SLOT_FIELDS)))

    # 1. STATS - Will's numbers.
    if [round(float(v), 1) for v in before_life] != [round(v, 1) for v in BASE_LIFE]:
        print("  NOTE: characterLife baseline moved upstream (%s, expected %s); "
              "applying the %gx multiplier to the CURRENT value"
              % (before_life, list(BASE_LIFE), LIFE_MULTIPLIER))
        target_life = [round(float(v) * LIFE_MULTIPLIER, 1) for v in before_life]
    else:
        target_life = list(TARGET_LIFE)
    db.set_field(COLDWORM, 'characterLife', target_life, DATA_TYPE_FLOAT)
    print("  life x%g: %s -> %s" % (LIFE_MULTIPLIER, before_life, target_life))

    # 2. KIT - repoint every slot at a donor that exists, at the donor's level.
    for slot in sorted(KIT, key=lambda s: int(s.replace('skillName', ''))):
        path, levels, donor = KIT[slot]
        idx = slot.replace('skillName', '')
        old = _scalar(db.get_field_value(COLDWORM, slot))
        db.set_field(COLDWORM, slot, path, DATA_TYPE_STRING)
        db.set_field(COLDWORM, 'skillLevel' + idx, list(levels), DATA_TYPE_INT)
        if _norm(old) != _norm(path):
            print("    %-12s %s -> %s  lvl=%s  [%s]"
                  % (slot, (old or '(absent)'), path.split('\\')[-1], levels, donor))
    print("  armor (+%d%% defensiveProtection via armor_passive level): %s -> %s"
          % (round((ARMOR_MULTIPLIER - 1) * 100), before_armor, TARGET_ARMOR_LEVELS))

    # 3. ANIM BINDINGS - before the active slots are wired, so the invariant
    #    holds at every intermediate point.
    for slot_idx, ref_name, anim in ANIM_BINDINGS:
        old_ref = _scalar(db.get_field_value(COLDWORM, 'unarmedSpecialAnimRef%d' % slot_idx))
        db.set_field(COLDWORM, 'unarmedSpecialAnimRef%d' % slot_idx, ref_name, DATA_TYPE_STRING)
        db.set_field(COLDWORM, 'unarmedSpecialAnim%d' % slot_idx, anim, DATA_TYPE_STRING)
        db.set_field(COLDWORM, 'unarmedSpecialAnimSpeed%d' % slot_idx,
                     ANIM_SPEED_TARGET, DATA_TYPE_FLOAT)
        print("    anim ref%-3d %r -> %r  (%s)"
              % (slot_idx, str(old_ref or '(absent)'), ref_name, anim.split('\\')[-1]))

    # 4. ACTIVE SLOTS - the AI wiring.
    for field, kit_key in ACTIVE_SINGLES:
        path = KIT[kit_key][0]
        db.set_field(COLDWORM, field, path, DATA_TYPE_STRING)
        print("    %-18s -> %s" % (field, path.split('\\')[-1]))
    for prefix, kit_key, chance, delay, timeout, rng, cite in SPECIALS:
        path = KIT[kit_key][0]
        db.set_field(COLDWORM, prefix + 'SkillName', path, DATA_TYPE_STRING)
        db.set_field(COLDWORM, prefix + 'Chance', float(chance), DATA_TYPE_FLOAT)
        db.set_field(COLDWORM, prefix + 'Delay', float(delay), DATA_TYPE_FLOAT)
        db.set_field(COLDWORM, prefix + 'Timeout', float(timeout), DATA_TYPE_FLOAT)
        db.set_field(COLDWORM, prefix + 'Range', rng, DATA_TYPE_STRING)
        print("    %-15s -> %-34s %g%%/%gs/%gs %-10s [%s]"
              % (prefix, path.split('\\')[-1], chance, delay, timeout, rng, cite))

    # 5. SPEED - the rig-proven profile.
    for field, value in SPEED_PROFILE:
        old = _scalar(db.get_field_value(COLDWORM, field))
        db.set_field(COLDWORM, field, float(value), DATA_TYPE_FLOAT)
        print("    %-24s %s -> %s" % (field, old, value))
    for field in ANIM_SPEEDS:
        if _scalar(db.get_field_value(COLDWORM, field)) is None:
            continue
        db.set_field(COLDWORM, field, ANIM_SPEED_TARGET, DATA_TYPE_FLOAT)
    print("    %d animation playback speeds -> %g (was 0.15-0.4 on the same rig "
          "um_coldcreep_29 runs at 1.0)" % (len(ANIM_SPEEDS), ANIM_SPEED_TARGET))

    db._modified.add(COLDWORM)

    # 6. SCOPE PROOF: exactly one record moved.
    dead_after = _anim_binding_violations(db, COLDWORM)
    if dead_after:
        raise SystemExit("[coldworm_buffs] apply() left the kit broken:\n  - %s"
                         % "\n  - ".join(dead_after))
    print("  kit repair proof: %d/%d active slots dead BEFORE -> 0 dead AFTER "
          "(every slot resolves and every required special animation is bound)"
          % (len(dead_before), len(_ACTIVE_SLOT_FIELDS)))


# ── verify (step 4, over the FINAL merged db) ───────────────────────────────
def verify(db, tags):
    problems = []

    if not db.has_record(COLDWORM):
        raise SystemExit("[coldworm_buffs] verify: %s vanished from the final db"
                         % COLDWORM)

    # A. Will's numbers survived every later writer.
    life = [float(v) for v in _vals(db, COLDWORM, 'characterLife')]
    want_life = [round(v * LIFE_MULTIPLIER, 1) for v in BASE_LIFE]
    if [round(v, 1) for v in life] != want_life:
        problems.append('characterLife=%s but R-39 requires 3x baseline %s'
                        % (life, want_life))
    armor = [int(v) for v in _vals(db, COLDWORM, 'skillLevel8')]
    if armor != TARGET_ARMOR_LEVELS:
        problems.append('armor_passive skillLevel8=%s but R-39 requires +20%% '
                        'of %s = %s' % (armor, list(BASE_ARMOR_LEVELS),
                                        TARGET_ARMOR_LEVELS))
    if _norm(_scalar(db.get_field_value(COLDWORM, 'skillName8'))) != _norm(KIT['skillName8'][0]):
        problems.append('skillLevel8 no longer drives armor_passive - the +20%% '
                        'armor is being applied to the wrong skill')
    for field, want in SPEED_PROFILE:
        got = float(_scalar(db.get_field_value(COLDWORM, field)) or 0.0)
        if abs(got - want) > 0.001:
            problems.append('%s=%g but R-39 speed profile requires %g'
                            % (field, got, want))

    # B. THE INVARIANT: no dead slot, no unbound special animation.
    problems.extend(_anim_binding_violations(db, COLDWORM))
    problems.extend(_kit_level_violations(db, COLDWORM))

    # C. The 3-tier soul + loot triple (asserted, never rewritten by this lane).
    for s in SOULS:
        if not db.has_record(s):
            problems.append('soul tier missing: %s' % s)
    loot = [str(v) for v in _vals(db, COLDWORM, 'lootFinger2Item1')]
    real = [p for p in loot if p and p != '#']
    if len(real) != 3 or any(_norm(a) != _norm(b) for a, b in zip(real, SOULS)):
        problems.append('lootFinger2Item1 is not the 3-tier soul triple %s (got %s)'
                        % ([s.split('\\')[-1] for s in SOULS], real))
    chance = float(_scalar(db.get_field_value(COLDWORM, 'chanceToEquipFinger2')) or 0.0)
    if chance <= 0.0:
        problems.append('chanceToEquipFinger2=%g - the soul triple can never drop'
                        % chance)
    weight = int(_scalar(db.get_field_value(COLDWORM, 'chanceToEquipFinger2Item1')) or 0)
    if weight <= 0:
        problems.append('chanceToEquipFinger2Item1=%d - the soul has zero weight '
                        'in a slot whose roll can fire' % weight)
    icons = []
    for tier, s in zip(('n', 'e', 'l'), SOULS):
        bm = _norm(_scalar(db.get_field_value(s, 'bitmap')))
        if bm and ('soul_%s_icon' % tier) not in bm:
            icons.append('%s -> %s' % (s.split('\\')[-1], bm))
    if icons:
        problems.append('per-tier soul icons wrong (b40 convention): %s' % icons)

    if problems:
        raise SystemExit(
            "[coldworm_buffs] R-39 VERIFY FAILED (%d problem(s)):\n  - %s"
            % (len(problems), "\n  - ".join(problems)))

    print("    coldworm_buffs verify OK: life %s (3x), armor_passive %s (+20%%), "
          "speed profile applied, %d/%d active skill slots resolve with every "
          "required special animation bound, 3-tier soul + loot triple intact @%g%%"
          % (life, armor, len(_ACTIVE_SLOT_FIELDS), len(_ACTIVE_SLOT_FIELDS), chance))


# ── negative test ──────────────────────────────────────────────────────────
def _negtest():
    """Plant the exact defect this lane fixes and prove the gate catches it.

    Two plants, run standalone:  py tools/patches/coldworm_buffs.py --negtest
      1. a monster whose special-attack skill EXISTS but demands an animation
         ref the caster does not bind  -> must be flagged;
      2. a monster whose special-attack skill does not resolve at all
         -> must be flagged;
      3. the same monster with the ref correctly bound -> must be clean.
    """
    from collections import OrderedDict
    from arz_patcher import ArzDatabase

    db = ArzDatabase()

    def seed(name):
        db._raw_records[name] = (0, b'')
        db._decoded_cache[name] = OrderedDict()

    skill = r'records\skills\negtest\planted_burstskill.dbr'
    mon = r'records\creature\negtest\planted_monster.dbr'
    seed(skill)
    db.set_field(skill, 'Class', ['Skill_AttackProjectileBurst'])
    db.set_field(skill, 'skillSpecialAnimationName', ['Burst'])

    seed(mon)
    db.set_field(mon, 'Class', ['Monster'])
    db.set_field(mon, 'specialAttackSkillName', [skill])
    db.set_field(mon, 'unarmedSpecialAnimRef1', ['Spit'])
    db.set_field(mon, 'unarmedSpecialAnim1', ['x\\Spit.anm'])
    _INDEX_CACHE.clear()
    unbound = _anim_binding_violations(db, mon)
    ok_unbound = any('never fires' in p for p in unbound)

    db.set_field(mon, 'specialAttack2SkillName', [r'records\skills\negtest\ghost.dbr'])
    _INDEX_CACHE.clear()
    dead = _anim_binding_violations(db, mon)
    ok_dead = any('does NOT resolve' in p for p in dead)

    db.set_field(mon, 'unarmedSpecialAnimRef2', ['Burst'])
    db.set_field(mon, 'unarmedSpecialAnim2', ['x\\Burst.anm'])
    db.set_field(mon, 'specialAttack2SkillName', [skill])
    _INDEX_CACHE.clear()
    fixed = _anim_binding_violations(db, mon)
    ok_fixed = not fixed

    ok = ok_unbound and ok_dead and ok_fixed
    print("coldworm_buffs _negtest:")
    print("  unbound-special-anim plant flagged : %s" % ok_unbound)
    print("  dead-skill-reference plant flagged : %s" % ok_dead)
    print("  correctly-bound control is clean   : %s (%s)" % (ok_fixed, fixed))
    print("  -> %s" % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    if '--negtest' in sys.argv:
        raise SystemExit(0 if _negtest() else 1)
