"""b73 registry module - TOXEUS CHAMPIONS KIT WAVE (Will 2026-07-16).

Gives the ENCOUNTER Toxeus champions the player FIGHTS their signature kits, built ONLY from
existing DB skills retuned + re-selected for castability and colour. Design + evidence:
docs/reports/b73_toxeus_champion_kits.md.

  DEVOURER OF BLOOD  (um_bloodtoxeus_99, "Toxeus the Murderer, Devourer of Blood"):
    * Tears of Blood (weak, 10s cd)  - NEW svc_devourer_tearsofblood (clone of the Blood-of-Ares
      artifact skill, damage cut + cd 120->10 + active 8->5), REPLACES the off-identity flashpowder
      at specialAttack2. Will: "the toxeus devourer of blood should have maybe a 10 second cool down
      on a weaker version of this ability."
    * Blood Frenzy  - EXISTING quak_bloodfrenzy passive (below 25% HP -> attack-speed + bleed/leech
      surge, crimson FX), added to a free skillName slot (a passive - no cast slot needed).

  ENSLAVER OF SOULS  (um_toxeus_enslaver_99, "Toxeus the Murderer, Enslaver of Souls"):
    Will: his kit is "pretty generic." The 3 generic cast slots (netherstrike/bladestorm/flashpowder)
    become the enslavement identity; his summon (raise the enslaved) + lethalstrike (the Murderer's
    finisher) are kept.
    * Soul-Rip           - NEW svc_enslaver_soulrip (clone of lifedrain, boosted leech + %-current-
      life): a ranged soul-drain that HEALS him.               REPLACES specialAttack2 (netherstrike).
    * Chains of Servitude - NEW svc_enslaver_dominate (+_buff) (clone of heretic_curse): a radius curse
      = short confusion + fumble + slow ("your body obeys him"). REPLACES specialAttack3 (bladestorm).
    * Unholy Dominion    - EXISTING unholy_rally: empowers his marauders in radius (his thralls surge).
                                                             REPLACES specialAttack4 (flashpowder).

WHY THE SHARED-RECORD / 5-SLOT DESIGN (see report 0):
  * The corridor ambush AND the deep waterfall boss both spawn um_bloodtoxeus_99 from the SAME pool
    (pools/q_bloodtoxeus_lone), so they get the ONE (weak-10s) Tears of Blood; a distinct full-strength
    corridor version = a monster+pool split, deferred as WILL-VETO #1.
  * No monster in the whole DB uses more than specialAttack5 (the Monster-template cap) and both
    champions already fill all 5, so new CAST abilities REPLACE the generic specials; new PASSIVES
    (Blood Frenzy) ride a free skillName slot (they auto-trigger, needing no cast slot).

CASTABILITY LAW (the Ephialtes-nova / boss_skill_fix lesson): both champions ride the anm_skeleton01
skeleton rig; every skill added has skillSpecialAnimationName absent (a no-special-anim cast) OR is a
passive/low-health trigger, so all are animatable. verify() proves this fail-loud.

ENGINE LAWS honoured: no explicit dtype on cloned-record overrides (INT/FLOAT corruption trap); never
blank a live donor ref to '' (B-TOXEUS-2); no pets/souls/pools/map touched (chain gate + champion-cap
gate untouched); no charFxPak edit (b28 crash trap) - dark/crimson FX come from SKILL SELECTION.
"""

import re as _re
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path
import apply_svc_patches as asp

MODULE_NAME = 'toxeus_champion_kits'

# ── champions (final paths in the built arz) ──
_DEVOURER = asp._BT_MONSTER   # records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr
_ENSLAVER = asp._EN_BOSS      # records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr

# ── donors (all DB-verified present in build45) ──
_TEARS_DONOR   = r'records\xpack\skills\artifactskills\e_da_bloodofares_tearsofblood.dbr'
_LIFEDRAIN     = r'records\skills\spirit\lifedrain.dbr'
_HERETIC_CURSE = r'records\skills\monster skills\attack_direct\heretic_curse.dbr'
_HERETIC_BUFF  = r'records\skills\monster skills\attack_direct\heretic_curse_buff.dbr'
# existing skills referenced as-is (NOT edited - shared records):
_BLOODFRENZY   = r'records\skills\monster skills\passive_buffs\quak_bloodfrenzy.dbr'
_UNHOLY_RALLY  = r'records\skills\monster skills\buff_other\unholy_rally.dbr'

# ── NEW skill records (collision-free vs build45, probe-verified) ──
_TEARS_WEAK    = r'records\skills\monster skills\attack_radius\svc_devourer_tearsofblood.dbr'
_SOULRIP       = r'records\skills\spirit\svc_enslaver_soulrip.dbr'
_DOMINATE      = r'records\skills\monster skills\attack_direct\svc_enslaver_dominate.dbr'
_DOMINATE_BUFF = r'records\skills\monster skills\attack_direct\svc_enslaver_dominate_buff.dbr'

_NEW_SKILLS = (_TEARS_WEAK, _SOULRIP, _DOMINATE, _DOMINATE_BUFF)

# expected Class per new skill (castability proof key)
_EXPECT_CLASS = {
    _TEARS_WEAK:    'Skill_AttackProjectileAreaEffect',
    _SOULRIP:       'Skill_AttackSpellChaos',
    _DOMINATE:      'Skill_AttackBuffRadius',
    _DOMINATE_BUFF: 'SkillBuff_Debuf',
}


# =============================================================================
# helpers
# =============================================================================
def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) else v


def _free_skillname_slot(db, rec, lo=1, hi=24):
    """Lowest skillName<i> slot in [lo,hi] that is absent or blank ('')."""
    ff = db.get_fields(rec) or {}
    used = set()
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values and str(tf.values[0]).strip():
            used.add(int(b[9:]))
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _add_kit_skill(db, rec, skillpath, level):
    """Add skillpath into the lowest free skillName slot with the given level (so it is a KNOWN,
    non-level-0 kit skill). Returns the slot index. Fail-loud if no slot free.
    Already-present guard: a re-apply over a patched db must not duplicate kit slots."""
    want = skillpath.replace('/', '\\').lower()
    for i in range(1, 33):
        cur = db.get_field_value(rec, f'skillName{i}')
        cur1 = cur[0] if isinstance(cur, list) and cur else cur
        if cur1 and str(cur1).replace('/', '\\').lower() == want:
            return i
    slot = _free_skillname_slot(db, rec)
    if slot is None:
        raise SystemExit(f"[toxeus_champion_kits] no free skillName slot on {rec}")
    db.set_field(rec, f'skillName{slot}', skillpath)
    db.set_field(rec, f'skillLevel{slot}', level)
    db._modified.add(rec)
    return slot


def _set_special(db, rec, suffix, skillpath, chance):
    """Point specialAttack<suffix> at skillpath @ chance (replaces whatever was there). suffix '' = the
    unnumbered slot 1; '2'..'5' the numbered ones. Value-only overrides preserve donor dtype."""
    db.set_field(rec, f'specialAttack{suffix}SkillName', skillpath)
    db.set_field(rec, f'specialAttack{suffix}Chance', float(chance))
    db._modified.add(rec)


# =============================================================================
# NEW skill records
# =============================================================================
def _build_tears_weak(db):
    """svc_devourer_tearsofblood = clone of the Blood-of-Ares artifact skill, weakened + 10s cd."""
    if not db.has_record(_TEARS_DONOR):
        raise SystemExit(f"[toxeus_champion_kits] Tears donor missing ({_TEARS_DONOR})")
    db.clone_record(_TEARS_DONOR, _TEARS_WEAK)
    T = _TEARS_WEAK
    # damage cut to a 3-tier ramp (monster uses skillLevel [1,2,3]); base level-1 was 88/99 fire, 975 bleed.
    db.set_field(T, 'offensiveSlowFireMin', [50.0, 95.0, 160.0])
    db.set_field(T, 'offensiveSlowFireMax', [60.0, 110.0, 185.0])
    db.set_field(T, 'offensiveSlowBleedingMin', [320.0, 520.0, 760.0])
    db.set_field(T, 'skillCooldownTime', 10.0)      # base 120.0
    db.set_field(T, 'skillActiveDuration', 5.0)     # base 8.0 (shorter rain)
    db.set_field(T, 'skillMaxLevel', 3)             # base 1 (so tier levels resolve)
    db.set_field(T, 'FileDescription', 'SVC Devourer: weakened Tears of Blood (Will 2026-07-16)')
    db._modified.add(T)


def _build_soulrip(db):
    """svc_enslaver_soulrip = clone of lifedrain, boosted into a healing soul-drain."""
    if not db.has_record(_LIFEDRAIN):
        raise SystemExit(f"[toxeus_champion_kits] lifedrain donor missing ({_LIFEDRAIN})")
    db.clone_record(_LIFEDRAIN, _SOULRIP)
    S = _SOULRIP
    db.set_field(S, 'offensiveLifeLeechMin', [200.0, 260.0, 340.0])   # he heals from the drain
    db.set_field(S, 'offensiveLifeMin', [90.0, 140.0, 210.0])
    db.set_field(S, 'offensiveLifeMax', [120.0, 180.0, 270.0])
    db.set_field(S, 'offensivePercentCurrentLifeMin', [3.0, 4.0, 5.0])  # rips a % of your life
    db.set_field(S, 'skillCooldownTime', 5.0)
    db.set_field(S, 'skillMaxLevel', 3)
    db._modified.add(S)


def _build_dominate(db):
    """svc_enslaver_dominate (+_buff) = clone of heretic_curse, tuned to short confusion + fumble +
    slow ('your body obeys him'). The debuff fields live on the buff record."""
    for donor in (_HERETIC_CURSE, _HERETIC_BUFF):
        if not db.has_record(donor):
            raise SystemExit(f"[toxeus_champion_kits] curse donor missing ({donor})")
    db.clone_record(_HERETIC_BUFF, _DOMINATE_BUFF)
    B = _DOMINATE_BUFF
    # SHORTEN the donor's 3-8s confusion / 8s fumble to a threat, not a lock. Add slow (donor had it 0).
    db.set_field(B, 'offensiveConfusionChance', [30.0, 35.0, 40.0])
    db.set_field(B, 'offensiveConfusionMin', 2.0)
    db.set_field(B, 'offensiveConfusionMax', 3.0)
    db.set_field(B, 'offensiveFumbleMin', [40.0, 50.0, 60.0])
    db.set_field(B, 'offensiveFumbleDurationMin', 3.0)
    db.set_field(B, 'offensiveSlowRunSpeedMin', [30.0, 35.0, 40.0])
    db.set_field(B, 'offensiveSlowRunSpeedDurationMin', 3.0)
    db.set_field(B, 'offensiveSlowAttackSpeedMin', [25.0, 30.0, 35.0])
    db.set_field(B, 'offensiveSlowAttackSpeedDurationMin', 3.0)
    db._modified.add(B)

    db.clone_record(_HERETIC_CURSE, _DOMINATE)
    db.set_field(_DOMINATE, 'buffSkillName', _DOMINATE_BUFF)
    db.set_field(_DOMINATE, 'skillCooldownTime', 12.0)   # cannot be spammed
    db.set_field(_DOMINATE, 'skillMaxLevel', 3)
    db._modified.add(_DOMINATE)


# =============================================================================
# wiring
# =============================================================================
def _wire_devourer(db):
    if not db.has_record(_DEVOURER):
        raise SystemExit(f"[toxeus_champion_kits] Devourer missing ({_DEVOURER})")
    M = _DEVOURER
    # Tears of Blood: kit slot + REPLACE specialAttack2 (was flashpowder).
    _add_kit_skill(db, M, _TEARS_WEAK, [1, 2, 3])
    _set_special(db, M, '2', _TEARS_WEAK, 35.0)
    # Blood Frenzy: a passive - kit slot only, auto-triggers below 25% HP (no cast slot).
    _add_kit_skill(db, M, _BLOODFRENZY, [4, 8, 12])
    print("  [DEVOURER] Tears of Blood (weak,10s) -> specialAttack2 (was flashpowder) @35; "
          "Blood Frenzy passive added (sub-25% HP surge).")


def _wire_enslaver(db):
    if not db.has_record(_ENSLAVER):
        raise SystemExit(f"[toxeus_champion_kits] Enslaver missing ({_ENSLAVER})")
    M = _ENSLAVER
    # Soul-Rip -> specialAttack2 (netherstrike); Chains -> specialAttack3 (bladestorm);
    # Unholy Dominion -> specialAttack4 (flashpowder). summon(1) + lethalstrike(5) KEPT.
    _add_kit_skill(db, M, _SOULRIP, [1, 2, 3])
    _set_special(db, M, '2', _SOULRIP, 40.0)
    _add_kit_skill(db, M, _DOMINATE, [1, 2, 3])
    _set_special(db, M, '3', _DOMINATE, 30.0)
    _add_kit_skill(db, M, _UNHOLY_RALLY, [1, 2, 3])
    _set_special(db, M, '4', _UNHOLY_RALLY, 30.0)
    print("  [ENSLAVER] Soul-Rip -> specialAttack2 (was netherstrike) @40; Chains of Servitude -> "
          "specialAttack3 (was bladestorm) @30; Unholy Dominion -> specialAttack4 (was flashpowder) "
          "@30. summonmarauders(1) + lethalstrike(5) kept.")


# =============================================================================
# entry points
# =============================================================================
def apply(db, tags):
    assert hasattr(db, 'record_names') and hasattr(db, 'set_field'), \
        'toxeus_champion_kits.apply: db is not an ArzDatabase'
    print("\n=== [toxeus_champion_kits] b73 TOXEUS CHAMPIONS KIT WAVE ===")
    _build_tears_weak(db)
    _build_soulrip(db)
    _build_dominate(db)
    _wire_devourer(db)
    _wire_enslaver(db)
    print("=== [toxeus_champion_kits] done (verify() runs post-finalization) ===\n")
    return tags


# ── the castability + no-level-0-special invariants (mirrors boss_skill_fix._l0_specials scope) ──
def _l0_special_offenders(db, rec):
    """[(special_field, skill)] for every specialAttack the AI casts (chance>0) whose skill sits in a
    skillName slot at level 0 - the 'tries to cast, does nothing' defect. Specials NOT in a skillName
    slot are ignored (they fire at base)."""
    ff = db.get_fields(rec) or {}
    names, levels = {}, {}
    for k, tf in ff.items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values:
            names[int(b[9:])] = str(tf.values[0])
        m = _re.match(r'skillLevel(\d+)$', b)
        if m and tf.values:
            levels[int(m.group(1))] = tf.values[0]
    lvl_by_ref = {names[i].replace('/', '\\').lower(): levels.get(i, 0) for i in names}
    out = []
    for k, tf in ff.items():
        b = k.split('###')[0]
        m = _re.match(r'specialAttack(\d*)SkillName$', b)
        if not (m and tf.values and str(tf.values[0]).strip()):
            continue
        suf = m.group(1)
        ref = str(tf.values[0]).replace('/', '\\').lower()
        ch = _gv1(db, rec, f'specialAttack{suf}Chance')
        if (ch or 0) > 0 and lvl_by_ref.get(ref) == 0:
            out.append((f'specialAttack{suf}', ref.rsplit('\\', 1)[-1]))
    return out


def verify(db, tags=None):
    """POST-FINALIZATION fail-loud gate (run_registry_verifies).

    (1) Each NEW skill record exists with the expected Class AND no skillSpecialAnimationName
        (castability on the anm_skeleton01 skeleton rig - the Ephialtes/boss_skill_fix law).
    (2) Each champion's re-pointed specialAttack points at the intended new/kept skill @ chance>0.
    (3) Each new kit skill sits in a skillName slot at level>=1 on its champion, AND neither champion
        has ANY chance>0 specialAttack referencing a level-0 skillName-slot skill (so boss_skill_fix's
        roster scan stays green over these two records)."""
    problems = []

    # (1) new skill records: exist + class + castable (no special anim)
    for sk in _NEW_SKILLS:
        if not db.has_record(sk):
            problems.append(f"NEW skill missing: {sk}")
            continue
        cls = _gv1(db, sk, 'Class')
        if cls != _EXPECT_CLASS[sk]:
            problems.append(f"{sk.rsplit(chr(92),1)[-1]}: Class {cls!r} != {_EXPECT_CLASS[sk]!r}")
        # buff records are not cast; the 3 cast/aura skills must carry NO special anim.
        if sk != _DOMINATE_BUFF:
            anim = _gv1(db, sk, 'skillSpecialAnimationName')
            if anim not in (None, '', '0'):
                problems.append(f"{sk.rsplit(chr(92),1)[-1]}: skillSpecialAnimationName={anim!r} "
                                f"(NOT castable on the skeleton rig)")
    # dominate must point at its buff
    if db.has_record(_DOMINATE):
        bs = _gv1(db, _DOMINATE, 'buffSkillName')
        if not bs or bs.replace('/', '\\').lower() != _DOMINATE_BUFF.replace('/', '\\').lower():
            problems.append(f"svc_enslaver_dominate buffSkillName != svc_enslaver_dominate_buff ({bs!r})")

    # (2) re-pointed specials landed @ chance>0
    def _assert_special(rec, suf, skill, label):
        if not db.has_record(rec):
            problems.append(f"{label}: champion record missing"); return
        sn = _gv1(db, rec, f'specialAttack{suf}SkillName')
        ch = _gv1(db, rec, f'specialAttack{suf}Chance')
        if not sn or sn.replace('/', '\\').lower() != skill.replace('/', '\\').lower():
            problems.append(f"{label}: specialAttack{suf}SkillName={str(sn).rsplit(chr(92),1)[-1]!r} "
                            f"!= {skill.rsplit(chr(92),1)[-1]}")
        elif (ch or 0) <= 0:
            problems.append(f"{label}: specialAttack{suf} chance {ch} <= 0")
    _assert_special(_DEVOURER, '2', _TEARS_WEAK, 'Devourer/Tears')
    _assert_special(_ENSLAVER, '2', _SOULRIP, 'Enslaver/Soul-Rip')
    _assert_special(_ENSLAVER, '3', _DOMINATE, 'Enslaver/Chains')
    _assert_special(_ENSLAVER, '4', _UNHOLY_RALLY, 'Enslaver/Dominion')

    # (3) new kit skills present at level>=1 + no level-0 special on either champion
    def _kit_level(rec, skill):
        ff = db.get_fields(rec) or {}
        target = skill.replace('/', '\\').lower()
        for k, tf in ff.items():
            b = k.split('###')[0]
            if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                    and str(tf.values[0]).replace('/', '\\').lower() == target:
                lv = _gv1(db, rec, f'skillLevel{b[9:]}')
                lv = lv[0] if isinstance(lv, list) else lv
                return lv
        return None
    for rec, skill, label in [
        (_DEVOURER, _TEARS_WEAK, 'Devourer/Tears'), (_DEVOURER, _BLOODFRENZY, 'Devourer/Frenzy'),
        (_ENSLAVER, _SOULRIP, 'Enslaver/Soul-Rip'), (_ENSLAVER, _DOMINATE, 'Enslaver/Chains'),
        (_ENSLAVER, _UNHOLY_RALLY, 'Enslaver/Dominion'),
    ]:
        lv = _kit_level(rec, skill)
        if lv in (None, 0):
            problems.append(f"{label}: not in a skillName slot at level>=1 (level={lv})")
    for rec, label in [(_DEVOURER, 'Devourer'), (_ENSLAVER, 'Enslaver')]:
        for field, skill in _l0_special_offenders(db, rec):
            problems.append(f"{label}: {field} casts level-0 skill {skill} (boss_skill_fix would fail)")

    if problems:
        for p in problems:
            print(f"  CHAMPION-KIT OFFENDER: {p}")
        raise SystemExit(f"toxeus_champion_kits.verify FAILED: {len(problems)} problem(s)")
    print("  [toxeus_champion_kits].verify: OK (4 new skills castable [no special anim]; Devourer "
          "Tears@2 + Enslaver Soul-Rip@2/Chains@3/Dominion@4 wired @chance>0; all new kit skills "
          "level>=1; no level-0 special on either champion).")
    return tags
