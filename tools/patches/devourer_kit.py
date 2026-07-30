r"""devourer_kit - b102: THE DEVOURER + THE ENDLESS HUNT WAVE.

Implements, in one module, four ruled items that all land on the two Toxeus
champions Will cannot currently fight on fair terms:

  R-103 / R-107  the REFLECT + PIERCE retune (he one-shots himself, and his
                 spear build is countered 70%)
  R-100 #1       Bloodbath on the Devourer, cooldown 45s -> 15s
  R-100 #12      Blood Frenzy on the Devourer (already present - asserted, NOT
                 duplicated)
  R-100 #13      summonable minions for the Devourer AND the Endless Hunt

WILL, VERBATIM (R-103): "yes harder is the point, keep all three. if we need to
make him more killable we will reduce his reflect damage or his health or
something. currently the reflect damage is what makes these variants nearly
unkillable since i one shot myself when i hit them" / "the answer is not cutting
skills but cutting elsewhere".
WILL, VERBATIM (R-107): "i just tried to kill the blood cave toxeus the devourer
and I one hit myself when i hit him, he is basically unkillable with the current
reflect damage unless you use pets to kill him but i am playing on epic and i
have two toxeus the murderer, enslaver of souls pets summoned and they cant kill
him so i guess i cant kill him".

Nothing here waters any of the three power additions down. The reflect and pierce
cuts are the levers Will himself named; both sit behind NAMED CONSTANTS at the
top of this file so he can retune either in one line. `characterLife` is
deliberately NOT touched - R-107 ranks it third and calls it the reserve lever.


================================================================================
1. THE SHARED-RECORD LAW, TWICE OVER (this is the part that bites)
================================================================================
`toxeus_passiveproperties` has **18 carriers**, measured on the built arz
6a3a491db546b603c52132237c40aa63 (51,124 records):

  6 Toxeus MONSTERS  um_toxeus_enslaver_99, um_toxeus_hunt_99,
                     um_toxeus_hunt_l_99, um_bloodtoxeus_99, um_toxeus_21,
                     um_toxeus_99
  9 PETS Will SUMMONS  pets\toxeus_enslaver_{1,2,3}, pets\bloodtoxeus_{1,2,3},
                     pets\toxeus_eoat_{1,2,3}
  1 FOREIGN           drxcreatures\crowheroes\less.dbr - a DRX crow hero that is
                     not a Toxeus creature at all
  2 zzdev dummies     z_toxeus, old_z_toxeus

So `defensiveReflect 100 -> 30` IN PLACE would strip 70 points of reflect off the
**nine pets Will is using to try to kill this boss** and off a DRX crow hero we do
not own. That is the `genericbossorb_04` lesson exactly. This module therefore
CLONES a monster-only passive and repoints ONLY the 6 Toxeus monsters. Pets,
`less.dbr` and the zzdev pair stay on the original 100/33, byte-unchanged.

`melinoe_bloodboil` ("Bloodbath") is shared the same way: 8 carriers on the
non-pcsafe record (the Devourer + `pets\bloodtoxeus_{1,2,3}` +
`pets\toxeus_eoat_{1,2,3}`), plus 26 player-soul carriers on its `pcsafe\` twin.
Cutting its cooldown in place would silently buff six of Will's own pets. So the
45s -> 15s cut lands on a CLONE and only the Devourer is repointed.


================================================================================
2. WHY "GRANT BLOODBATH" IS AN ANIM-BINDING FIX, NOT A WIRING FIX
================================================================================
The Devourer ALREADY carries `melinoe_bloodboil` on `skillName1` (level [8,12,16])
AND on `specialAttackSkillName` at chance **90.0**, shipped since build32. Will
nonetheless asked for the skill as if it were absent. Measured, it is:

  melinoe_bloodboil.skillSpecialAnimationName = 'BloodBoil'
  the Devourer's caster table = records\creature\monster\skeleton\anm\anm_skeleton01.dbr
  every SpecialAnimRef that table binds =
      dHanded : DwAttAlpha, JumpSlash, Crosscut, AoE360, BladeSweep, Charge
      sHanded : AoE360, LethalStrike, Absorb, Charge, Bolts, Strike,
                ShieldSkill01, Staff
      staff   : Spellshock
      unarmed : Halfring, Fullring
  'BloodBoil' : ABSENT
  records in the whole DB that bind a 'BloodBoil' ref : exactly 2, neither of them
      a skeleton (anm_maenad bowSpecialAnimRef7, anm_acolyte unarmedSpecialAnimRef1)

Under this repo's disasm-proven hard law **B-SOUL-PROC-2** (BACKLOG "RCA v2":
`Game.dll SkillManager::StartSkill`, log string "Animation failed to start in
SkillManager::StartSkill" va 0x1035c3b0, gate vcall va 0x102561d4) a cast whose
`skillSpecialAnimationName` cannot start on the CASTER's animation table is
ABORTED and returns false. The BACKLOG entry even names this exact token in its
census of never-playable monster anims: "BloodBoil x29".

**So the Devourer's signature nova, wired at 90% chance, has never once fired.**
That is the defect behind R-100 #1, and it is why Will experienced the skill as
missing. The remedy used here is the one this repo already shipped for the same
law: the CLONE carries **no** `skillSpecialAnimationName` at all (field DELETED,
never blanked to '' - exact base parity; the BACKLOG records 172/204 base proc
grants as anim-less). The cast then starts on the default animation instead of
being aborted.

The same law kills `svc_enslaver_summonmarauders` (`skillSpecialAnimationName =
'Summon'`, single carrier `um_toxeus_enslaver_99`, same anm_skeleton01 table,
no 'Summon' ref) - the very summon R-100 #13 tells us to pattern the new ones
on. Shipping two working summons while the reference one stays dead would be the
"triaged-into-follow-up = NOT done" failure, so it is fixed here too, in place
(one carrier, so the shared-record law does not force a clone). FLAGGED for Will:
this makes the Enslaver harder, which R-103 sanctions ("harder is the point") but
which he did not specifically ask for.


================================================================================
3. THE MINIONS - held to the amgoz1 bar, not a marauder recolour
================================================================================
**`docs/amgoz1_design_voice.md` IS ABSENT FROM THIS TREE.** It is cited as law in
BACKLOG.md (3x), HUNTING_IMPROVEMENT_SUGGESTIONS.md, four wave reports,
tools/patches/bossarena.py and a wip workflow, but the file itself does not
exist on `main` @ 7efd107 and `git log --all --diff-filter=A -- '*amgoz1_design_
voice*'` returns nothing - it was never committed. b65 already recorded this
("re-distilled from first principles since amgoz1_design_voice.md is gone from
the tree"). Registered as debt below; the bar used here is RECONSTRUCTED from
shipped SV/DRX content actually measured in this arz:

  * a creature's kit and its retinue come from ITS OWN family, not from a
    convenient neighbour's (SV's Erebenea the Bloodletter grants Bloodbath, a
    bleed nova, because she is a lamia bloodletter; DRX's blood-cult disciple
    summons bloodhounds, its blood demons bleed on attack);
  * names are concrete and physical, never a category label - "Enslaved Shadow
    Marauder", "Leinth the Blood Witch", "Erebenea the Bloodletter",
    "Neferkha, the Rimebound Pharaoh";
  * a champion's adds are a different SILHOUETTE from him, so the fight reads at
    a glance (Leinth fields uglies, the Enslaver fields marauders);
  * and Will's own complaint (R-100 #18) is the negative form of the same bar:
    adds that "look just like the other guys ... not big with no special skills
    or anything to make them even noticeable besides their red names" fail it.

DEVOURER OF BLOOD -> "Gorged Bloodspawn"
  Donor `drxcreatures\blooddemon\c_large_blooddemon_40` (Champion, Demon,
  DRX\meshes\blooddemon01.msh). Scaled up via `scale` ONLY - `actorHeight` is
  inherited, see R-126. This is not an arbitrary pick: the blood demons
  are ALREADY his declared retinue - `_BT_BLOODDEMON` in apply_svc_patches names
  b_med_blooddemon_30/31/32 as his phase adds, and his placed pool
  `q_bloodtoxeus_lone` spawns exactly those three as his championMin=2 escort. He
  is the Devourer *of blood*; what he summons is the blood he has drunk, congealed
  and sent back out. Different mesh, different race and different silhouette from
  the Enslaver's ShadowStalker marauders.

  It REPLACES `specialAttack5` = `t1_skill_pitspawner_summonlildude_02`, a shared
  DRX map-dressing spawner whose payload `t1_lildude_02` is a **charLevel 9,
  1.0-HP, scale 0.5** pit sprite on a boss whose own band is [40,68,100]. That is
  precisely the "not real minions" Will is complaining about. RETIREMENT PROTOCOL
  OBSERVED: the pit-spawner skill record is NOT deleted, blanked or renamed, it
  keeps its two other carriers (t1_pitspawner_01/02), and it keeps its place in
  the Devourer's `skillName9` slot - only the AI cast slot moves.

ENDLESS HUNT -> "Courser of the Endless Hunt"
  Donor `drxcreatures\bloodhound\c_bloodhound_44` (Champion, Demon,
  DRX\meshes\bloodhound.msh). He is the hunter: Quarry's Mark, Long Reach, Run
  Down, the Runbreaker spear, endless pursuit. What a hunter fields is a pack that
  runs the quarry to ground, so his minions are coursing hounds - four-legged,
  fast, and visually nothing like a marauder. Lands on his FREE `specialAttack5`,
  so nothing is displaced at all.

  The donor's own `specialAttack2` -> `bloodhound\skills\puke.dbr` is itself
  B-SOUL-PROC-2 dead (it demands anim 'BloodPuke'; the donor binds only 'Roar'),
  so the courser gets an anim-less clone of it and actually spits.

DENSITY (the b76 chumbi-freeze precedent). Both summons are petLimit 3 /
petBurstSpawn 3, against the Enslaver's shipped 4/6.
  WORST-CASE SIMULTANEOUS ENTITY COUNT, measured from the placed pools:
    Devourer  q_bloodtoxeus_lone : spawnMin=Max 3, championMin=Max 2
                                 -> 1 boss + 2 blood demons + 3 summoned = 6
              egg_blooddragon    : spawnMin=Max 4, championMin=Max 3
                                 -> 1 boss + 3 blood dragons + 3 summoned = 7
    Hunt      q_toxeus_hunt_lone : spawnMin=Max 1, championChance 0
                                 -> 1 boss + 3 summoned = 4
              roaming sweep      : the host pool's own members + 1 Hunt + 3
                                   coursers (his per-pool cap is 1)
  For comparison the shipped Enslaver reaches 1 + 4 warband + 4 summoned = 9, and
  the b76 offenders were UNCAPPED. Neither new summon is unbounded.


================================================================================
4. WHY THIS MODULE'S REGISTRY SLOT IS LOAD-BEARING
================================================================================
It sits AFTER `uber_quest_markers` and BEFORE `toxeus_hunt_endless`.

  * BEFORE `toxeus_hunt_endless` is REQUIRED, not stylistic. That module generates
    `um_toxeus_hunt_l_99` as a clone-then-override of `um_toxeus_hunt_99` at build
    time and its verify() asserts the two differ in EXACTLY the `controller`
    field. Registering after it would (a) leave the Legendary variant without the
    summon and still on the un-retuned passive, and (b) make the base differ from
    the variant in three more fields, red-lining its gate. Running first means the
    variant inherits both by construction - the same reason R-91's soul rate and
    the quest marker are inherited rather than re-applied.
  * AFTER every writer of the two champions' kits (toxeus_suite,
    toxeus_champion_kits, boss_skill_fix, black_poison, toxeus_hunt_encounter,
    toxeus_souls_100, uber_apex_orb, uber_quest_markers), so this module is the
    ratified last writer of the slots it claims.
  * BEFORE `fx_dangling_cleanup` (LAST content module), so the FX hygiene sweep
    still covers the four new records.

ENGINE LAWS honoured: no explicit dtype on any field a cloned record already
carries (INT/FLOAT corruption trap); a retired field is DELETED, never set to ''
(B-TOXEUS-2); no Pet.tpl record is touched (the Pet.tpl equipment-field crash rule
is out of scope by construction); no charFxPak added to any SpawnPet skill (the
build28 crash trap, restated verbatim in `_create_blood_toxeus_skills`); no map,
no pool, no proxy, no soul rate, no treasure proxy.

WHAT THIS LANE WROTE BACK INTO THE LEDGER (docs/WILL_RULINGS.md, none of them a new
Will decision - they are the measured amendments plus this lane's two vetoable
design choices):
  R-120  Bloodbath was already wired at 90% and had never fired (B-SOUL-PROC-2)
  R-121  the Enslaver's own summon is dead the same way - fixed, FLAGGED FOR VETO
  R-122  reflect + pierce were not the only walls; the castability walk is the audit
  R-123  Blood Frenzy is present but its payload is thin - OPEN WILL DECISION
  R-125  the two minion families; `docs/amgoz1_design_voice.md` does not exist
         (was R-124 until two other live lanes took that number the same day)
  R-126  `actorHeight` is a per-RIG constant, not a size knob - the first draft
         of THIS module invented one on each minion and the record-diff could
         not see it (an invented value on a NEW record is not a "change" against
         any baseline). Measured DB-wide: 0 of 2,122 rigs scale actorHeight;
         both donor rigs hold it flat across their whole size ladder, including
         `xbloodhound_36` at scale 2.25 - LARGER than our courser. Now inherited
         from the donor and gated against it (plant N10).

Negative test: `py tools/patches/devourer_kit.py --negtest <baseline.arz>`
Census only : `py tools/patches/devourer_kit.py --analyze <arz>`
R-126 data  : `py tools/debug/probe_actorheight.py <arz>`
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # tools/ on path
import apply_svc_patches as asp                                # noqa: E402
from arz_patcher import DATA_TYPE_FLOAT, DATA_TYPE_STRING      # noqa: E402

MODULE_NAME = "Devourer + Endless Hunt kit (R-100 #1/#12/#13, R-103, R-107)"


# =============================================================================
# WILL'S NUMBERS - retune either of these in ONE line (R-103 / R-107)
# =============================================================================
# R-103: "if we need to make him more killable we will reduce his reflect damage
# or his health or something". R-107 lever 1, recommended 30, and 30 is what
# ships. `defensiveReflectChance` deliberately stays 33.0 - R-103 ruled that
# lowering the CHANCE instead "leaves it a coin-flip instadeath that is simply
# rarer. That is worse design".
REFLECT_MONSTER = 30.0          # was 100.0 on the shared passive
REFLECT_CHANCE = 33.0           # UNCHANGED - do not "fix" this instead

# R-107 lever 2: "his own character is a SPEAR user - pierce damage - and this
# boss has 70% pierce resistance ... a near-immunity". Recommended 40.
DEVOURER_PIERCE = 40.0          # was 70.0

# R-100 #1, Will verbatim: "lets reduce the cooldown on the skill from 45s to
# like 15s". 15 is his number.
BLOODBATH_COOLDOWN = 15.0       # was 45.0 on melinoe_bloodboil

# R-100 #13 density, bounded per the b76 chumbi-freeze precedent (the Enslaver
# ships 4/6; these are deliberately tighter).
SUMMON_PET_LIMIT = 3
SUMMON_BURST = 3
SUMMON_COOLDOWN = 8.0
SUMMON_CAST_CHANCE = 100.0
# The ruled ceiling the gate enforces on OUR new summons (never unbounded).
SUMMON_LIMIT_CEILING = 4

# R-107 explicitly ranks characterLife THIRD and calls it the reserve lever, so
# this wave must not move it. The gate asserts it.
DEVOURER_LIFE_RESERVED = [13000.0, 18000.0, 24000.0]


# =============================================================================
# RECORDS
# =============================================================================
SHARED_PASSIVE = r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'
# THE NAME IS LOAD-BEARING, and the first build proved it. `boss_skill_fix.verify`
# re-asserts its own b39 fixes survived finalization by looking for the SUBSTRING
# 'toxeus_passiveproperties' in a skillName slot on um_toxeus_hunt_99, and it failed
# the build with "skill toxeus_passiveproperties vanished from kit (regression)" when
# an earlier draft named this clone `svc_toxeus_monster_passive`. Keeping the donor's
# basename inside the clone's basename satisfies that gate WITHOUT weakening it - and
# it is the honest name anyway: this IS the Toxeus passive properties, monster-only
# variant. Our own carrier census matches on EXACT normalized paths (the reverse
# index), never on substrings, so the two records never bleed into each other.
MONSTER_PASSIVE = (r'records\skills\monster skills\passive_buffs'
                   r'\svc_toxeus_passiveproperties_monster.dbr')

DEVOURER = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
HUNT = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
HUNT_L = r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr'
ENSLAVER = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
TOXEUS_21 = r'records\creature\monster\skeleton\um_toxeus_21.dbr'
TOXEUS_99 = r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr'

# The 6 Toxeus MONSTERS that move to the monster-only passive. um_toxeus_hunt_l_99
# is NOT repointed directly: it does not exist yet at apply() time (its author
# `toxeus_hunt_endless` runs after this module) and inherits the repoint from its
# clone base. verify(), which runs post-finalization, asserts it landed.
PASSIVE_TARGETS_DIRECT = (ENSLAVER, HUNT, DEVOURER, TOXEUS_21, TOXEUS_99)
PASSIVE_TARGETS_ALL = PASSIVE_TARGETS_DIRECT + (HUNT_L,)

# Everything that MUST stay on the original 100/33 (R-107 Part 2).
PETS_KEEP_ORIGINAL = tuple(
    r'records\skills\soulskills\pets\%s_%d.dbr' % (fam, i)
    for fam in ('toxeus_enslaver', 'bloodtoxeus', 'toxeus_eoat') for i in (1, 2, 3))
FOREIGN_KEEP_ORIGINAL = (r'records\drxcreatures\crowheroes\less.dbr',)
ZZDEV_KEEP_ORIGINAL = (r'records\xpack\creatures\monster\zzdev\z_toxeus.dbr',
                       r'records\xpack\creatures\monster\zzdev\old_z_toxeus.dbr')
KEEP_ORIGINAL = PETS_KEEP_ORIGINAL + FOREIGN_KEEP_ORIGINAL + ZZDEV_KEEP_ORIGINAL

# Bloodbath
BLOODBOIL_SHARED = r'records\skills\soulskills\melinoe_bloodboil.dbr'
BLOODBATH = r'records\skills\boss skills\svc_devourer_bloodbath.dbr'

# Blood Frenzy - PRESENT ALREADY (b73). Asserted, never re-added.
BLOODFRENZY = r'records\skills\monster skills\passive_buffs\quak_bloodfrenzy.dbr'

# Summons
ENSLAVER_SUMMON = r'records\skills\boss skills\svc_enslaver_summonmarauders.dbr'
LILDUDE_SUMMON = r'records\drxmap\pitsprites\t1_skill_pitspawner_summonlildude_02.dbr'

BLOODSPAWN_DONOR = r'records\drxcreatures\blooddemon\c_large_blooddemon_40.dbr'
BLOODSPAWN = r'records\drxcreatures\blooddemon\um_devourer_bloodspawn_99.dbr'
DEV_SUMMON = r'records\skills\boss skills\svc_devourer_summonbloodspawn.dbr'

COURSER_DONOR = r'records\drxcreatures\bloodhound\c_bloodhound_44.dbr'
COURSER = r'records\drxcreatures\bloodhound\um_hunt_courser_99.dbr'
HUNT_SUMMON = r'records\skills\boss skills\svc_hunt_summoncoursers.dbr'
PUKE_DONOR = r'records\drxcreatures\bloodhound\skills\puke.dbr'
COURSER_SPEW = r'records\drxcreatures\bloodhound\skills\svc_courser_bloodspew.dbr'

NEW_RECORDS = (MONSTER_PASSIVE, BLOODBATH, BLOODSPAWN, DEV_SUMMON,
               COURSER, HUNT_SUMMON, COURSER_SPEW)

TAGS = {
    'tagSVCMonsterDevourerBloodspawn': 'Gorged Bloodspawn',
    'tagSVCMonsterHuntCourser': 'Courser of the Endless Hunt',
}

# every monster this module makes the gate walk for castability
CASTERS = (DEVOURER, HUNT, HUNT_L, ENSLAVER, BLOODSPAWN, COURSER)

# minion -> the donor it was cloned from. The gate reads the DONOR live out of
# the same db (both are proven byte-unchanged by the record-diff), so the
# actorHeight invariant is checked against ground truth rather than a number
# copied into this file that could drift away from the rig. See R-126.
MINION_DONORS = {BLOODSPAWN: BLOODSPAWN_DONOR, COURSER: COURSER_DONOR}

ACTIVE_SLOT_FIELDS = ('attackSkillName', 'initialSkillName', 'dyingSkillName',
                      'specialAttackSkillName') + tuple(
    'specialAttack%dSkillName' % i for i in range(2, 6))

_ANIM_REF_RE = re.compile(r'^([A-Za-z]+)SpecialAnimRef(\d+)$')


# =============================================================================
# helpers
# =============================================================================
def _norm(p):
    return str(p).replace('/', '\\').strip().lower()


def _one(db, rec, field):
    try:
        v = db.get_field_value(rec, field)
    except Exception:
        return None
    return v[0] if isinstance(v, list) and v else v


def _vals(db, rec, field):
    try:
        v = db.get_field_value(rec, field)
    except Exception:
        return None
    return v if isinstance(v, list) else ([] if v is None else [v])


def _require(db, rec, label):
    if not db.has_record(rec):
        raise SystemExit('[devourer_kit] %s missing: %s' % (label, rec))


def _del_field(db, rec, field):
    """Delete a field ENTIRELY (base-absence parity). Never blank to '' -
    B-TOXEUS-2. Returns True if anything was removed."""
    ff = db.get_fields(rec)
    if not ff:
        return False
    hit = False
    for k in list(ff):
        if k.split('###')[0] == field:
            del ff[k]
            hit = True
    if hit:
        db._modified.add(rec)
        _bump()
    return hit


def _set_ref(db, rec, field, value, dtype=None):
    """Write a .dbr-valued field and invalidate the reverse index."""
    if dtype is None:
        db.set_field(rec, field, value)
    else:
        db.set_field(rec, field, value, dtype)
    db._modified.add(rec)
    _bump()


def _clone(db, src, dest):
    db.clone_record(src, dest)
    _bump()


def _skill_slots(db, rec):
    """{slot index: skill path} for every non-blank skillName<i> on rec."""
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        m = re.match(r'^skillName(\d+)$', b)
        if m and tf.values and str(tf.values[0]).strip():
            out[int(m.group(1))] = str(tf.values[0])
    return out


def _slot_of(db, rec, skill):
    want = _norm(skill)
    for i, p in _skill_slots(db, rec).items():
        if _norm(p) == want:
            return i
    return None


def _free_slot(db, rec, lo=1, hi=23):
    used = set(_skill_slots(db, rec))
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    raise SystemExit('[devourer_kit] no free skillName slot on %s' % rec)


def _add_kit_skill(db, rec, skill, level):
    """Idempotent: put `skill` in the lowest free skillName slot at `level`."""
    got = _slot_of(db, rec, skill)
    if got is not None:
        return got
    slot = _free_slot(db, rec)
    db.set_field(rec, 'skillName%d' % slot, skill, DATA_TYPE_STRING)
    db.set_field(rec, 'skillLevel%d' % slot, level)
    db._modified.add(rec)
    _bump()
    return slot


def _repoint_slot(db, rec, old, new):
    """Repoint the skillName slot holding `old` at `new`. Value-only write, so
    the slot keeps its dtype. Returns the slot index, or None if `old` absent."""
    i = _slot_of(db, rec, old)
    if i is None:
        return None
    db.set_field(rec, 'skillName%d' % i, new)
    db._modified.add(rec)
    _bump()
    return i


# ── the reverse reference index ──────────────────────────────────────────────
# A carrier census is a full-DB scan (51k records), and both the shared-record law
# and the gate need several of them. The index is built once and reused until a
# REFERENCE is rewritten; `_bump()` is called only by the write paths that can
# actually move a .dbr-valued field, so a plain float plant never pays for a
# rebuild. Scalar-only mutations therefore cost nothing.
_REF_INDEX = {}
_REF_GEN = [0]


def _bump():
    _REF_GEN[0] += 1


def _ref_index(db):
    key = id(db)
    cached = _REF_INDEX.get(key)
    if cached is not None and cached[0] == _REF_GEN[0]:
        return cached[1]
    idx = {}
    for n in db.record_names():
        ff = db.get_fields(n)
        if not ff:
            continue
        for k, tf in ff.items():
            vals = tf.values
            if not vals:
                continue
            base = None
            for v in vals:
                if isinstance(v, str) and len(v) > 4 and v[-4:].lower() == '.dbr':
                    if base is None:
                        base = k.split('###')[0]
                    idx.setdefault(v.replace('/', '\\').lower(), []).append((n, base))
    _REF_INDEX[key] = (_REF_GEN[0], idx)
    return idx


def _carriers(db, target, field_re=None):
    """Every (record, field) referencing `target` (optionally field-name filtered)."""
    hits = _ref_index(db).get(_norm(target), ())
    if field_re:
        return [(n, f) for n, f in hits if re.match(field_re, f)]
    return list(hits)


def _passive_carriers(db, target):
    """Records carrying `target` in a skillName<i> slot - the reflect blast radius."""
    return sorted({n for n, _ in _carriers(db, target, r'^skillName\d+$')})


# ── the B-SOUL-PROC-2 castability walk (the b94 lesson, monster side) ────────
def _bound_anim_refs(db, rec):
    """{ref name: (source, anim file)} for a caster, following BOTH its own inline
    <family>SpecialAnimRef<i> block AND its charAnimationTableName table. The
    coldworm_buffs gate only read the monster's own `unarmedSpecialAnimRef*`; the
    Devourer and the Enslaver carry NONE of their own and get every binding they
    have from anm_skeleton01, so a walk that stops at the record would report both
    champions as having no animations at all."""
    out = {}
    for src in (_one(db, rec, 'charAnimationTableName'), rec):
        if not src or not db.has_record(src):
            continue
        for k, tf in (db.get_fields(src) or {}).items():
            b = k.split('###')[0]
            m = _ANIM_REF_RE.match(b)
            if not m or not tf.values:
                continue
            name = str(tf.values[0]).strip()
            if not name:
                continue
            anim = _one(db, src, '%sSpecialAnim%s' % (m.group(1), m.group(2)))
            if str(anim or '').strip():
                # the record's own inline block wins over its table
                out[name] = (src, str(anim))
    return out


def _anim_violations(db, rec):
    """B-SOUL-PROC-2 on the monster side: for every ACTIVE cast slot, the skill
    must resolve, and any `skillSpecialAnimationName` it declares must be bound by
    the caster in at least one weapon family - otherwise
    SkillManager::StartSkill aborts the cast and the skill NEVER fires."""
    problems = []
    if not db.has_record(rec):
        return ['%s: caster record missing' % rec]
    bound = _bound_anim_refs(db, rec)
    for field in ACTIVE_SLOT_FIELDS:
        path = _one(db, rec, field)
        path = str(path).strip() if path is not None else ''
        if not path or path == '0':
            continue
        if not db.has_record(path):
            problems.append('%s: %s -> %s does NOT resolve (dead cast slot)'
                            % (rec, field, path))
            continue
        need = _one(db, path, 'skillSpecialAnimationName')
        need = str(need).strip() if need is not None else ''
        if not need:
            continue
        if need not in bound:
            problems.append(
                '%s: %s -> %s demands special animation %r which the caster binds '
                'NOWHERE (bound: %s) - StartSkill aborts, the skill never fires'
                % (rec, field, path.rsplit('\\', 1)[-1], need, sorted(bound)))
    return problems


def _l0_special_offenders(db, rec):
    """Every chance>0 specialAttack whose skill sits in a skillName slot at level 0
    (the 'tries to cast, does nothing' defect boss_skill_fix owns)."""
    slots = _skill_slots(db, rec)
    lvl_by_ref = {}
    for i, p in slots.items():
        lv = _one(db, rec, 'skillLevel%d' % i)
        lvl_by_ref[_norm(p)] = lv
    out = []
    for field in ACTIVE_SLOT_FIELDS:
        if not field.startswith('specialAttack'):
            continue
        suf = field[len('specialAttack'):-len('SkillName')]
        path = _one(db, rec, field)
        if not path or not str(path).strip():
            continue
        ch = _one(db, rec, 'specialAttack%sChance' % suf) or 0
        if ch > 0 and lvl_by_ref.get(_norm(path)) == 0:
            out.append((field, str(path).rsplit('\\', 1)[-1]))
    return out


# =============================================================================
# PART A - R-103 / R-107: the monster-only reflect passive + the pierce cut
# =============================================================================
def _build_monster_passive(db, census):
    _require(db, SHARED_PASSIVE, 'the shared Toxeus passive')

    # SHARED-RECORD LAW: the carriers were enumerated BEFORE anything was touched.
    before = census['passive']
    pets_on_it = [c for c in before if _norm(c) in {_norm(p) for p in PETS_KEEP_ORIGINAL}]
    print('  [R-107] shared passive blast radius: %d carrier(s), %d of them Will\'s '
          'own PETS -> cloning a monster-only passive instead of editing in place'
          % (len(before), len(pets_on_it)))

    _clone(db, SHARED_PASSIVE, MONSTER_PASSIVE)
    # value-only overrides: the clone already carries both fields as FLOAT
    db.set_field(MONSTER_PASSIVE, 'defensiveReflect', REFLECT_MONSTER)
    db.set_field(MONSTER_PASSIVE, 'defensiveReflectChance', REFLECT_CHANCE)
    db.set_field(MONSTER_PASSIVE, 'FileDescription',
                 'SVC monster-only Toxeus passive: defensiveReflect %g (was 100) at '
                 '%g%% chance - R-103/R-107, Will "i one shot myself when i hit them". '
                 'The 9 Toxeus PETS + drxcreatures\\crowheroes\\less.dbr stay on the '
                 'ORIGINAL toxeus_passiveproperties at 100/33.'
                 % (REFLECT_MONSTER, REFLECT_CHANCE))
    db._modified.add(MONSTER_PASSIVE)

    moved = []
    for rec in PASSIVE_TARGETS_DIRECT:
        _require(db, rec, 'Toxeus monster')
        slot = _repoint_slot(db, rec, SHARED_PASSIVE, MONSTER_PASSIVE)
        if slot is None:
            raise SystemExit('[devourer_kit] %s does not carry the shared passive in '
                             'any skillName slot - the R-107 census is stale, STOP'
                             % rec)
        moved.append((rec, slot))
    for rec, slot in moved:
        print('    reflect %g -> %g : %-72s [skillName%d]'
              % (100.0, REFLECT_MONSTER, rec.rsplit('\\', 1)[-1], slot))
    # In the REGISTRY, um_toxeus_hunt_l_99 does not exist yet (toxeus_hunt_endless
    # mints it later off the base Hunt) and inherits the repoint by construction.
    # Running standalone against an ALREADY-BUILT arz (--negtest / --analyze) it
    # does exist, so repoint it directly. Both routes end in the same state, and
    # toxeus_hunt_endless's "base and variant differ in EXACTLY `controller`"
    # assertion holds either way.
    if db.has_record(HUNT_L):
        slot = _repoint_slot(db, HUNT_L, SHARED_PASSIVE, MONSTER_PASSIVE)
        print('    reflect %g -> %g : %-72s [skillName%s] (already minted)'
              % (100.0, REFLECT_MONSTER, HUNT_L.rsplit('\\', 1)[-1], slot))
    else:
        print('    um_toxeus_hunt_l_99 inherits the repoint from its clone base '
              '(toxeus_hunt_endless runs after this module); verify() asserts it '
              'landed.')


def _cut_devourer_pierce(db):
    _require(db, DEVOURER, 'the Devourer')
    was = _one(db, DEVOURER, 'defensivePierce')
    db.set_field(DEVOURER, 'defensivePierce', DEVOURER_PIERCE)
    db._modified.add(DEVOURER)
    print('  [R-107 lever 2] Devourer defensivePierce %s -> %g (Will plays a SPEAR '
          'build; 70%% was a near-immunity). characterLife UNTOUCHED - R-107 keeps '
          'it as the reserve lever.' % (was, DEVOURER_PIERCE))


# =============================================================================
# PART B - R-100 #1: Bloodbath, cd 45 -> 15, and made castable at all
# =============================================================================
def _build_bloodbath(db, census):
    _require(db, BLOODBOIL_SHARED, 'melinoe_bloodboil (the Bloodbath donor)')
    shared_carriers = census['bloodboil']
    print('  [R-100 #1] melinoe_bloodboil blast radius: %d carrier(s) (%d of them '
          'Will\'s own pets) -> cloning rather than cutting the cooldown in place'
          % (len(shared_carriers), sum(1 for c in shared_carriers if '\\pets\\' in c)))

    _clone(db, BLOODBOIL_SHARED, BLOODBATH)
    db.set_field(BLOODBATH, 'skillCooldownTime', BLOODBATH_COOLDOWN)
    # B-SOUL-PROC-2: DELETE the anim (base-absence parity), never blank it.
    had = _one(db, BLOODBATH, 'skillSpecialAnimationName')
    _del_field(db, BLOODBATH, 'skillSpecialAnimationName')
    db.set_field(BLOODBATH, 'FileDescription',
                 'SVC Devourer: Bloodbath, cooldown %g (was 45) - R-100 #1. '
                 'skillSpecialAnimationName %r DELETED: anm_skeleton01 binds no '
                 "'BloodBoil' ref, so B-SOUL-PROC-2 aborted every cast."
                 % (BLOODBATH_COOLDOWN, had))
    db._modified.add(BLOODBATH)

    slot = _repoint_slot(db, DEVOURER, BLOODBOIL_SHARED, BLOODBATH)
    if slot is None:
        slot = _add_kit_skill(db, DEVOURER, BLOODBATH, [8, 12, 16])
    _set_ref(db, DEVOURER, 'specialAttackSkillName', BLOODBATH)
    print('    svc_devourer_bloodbath: cd %g (was 45), special anim %r REMOVED; '
          'Devourer skillName%d + specialAttackSkillName repointed (chance %s kept). '
          'melinoe_bloodboil itself is byte-unchanged for its %d other carriers.'
          % (BLOODBATH_COOLDOWN, had, slot,
             _one(db, DEVOURER, 'specialAttackChance'), len(shared_carriers) - 1))


# =============================================================================
# PART C - R-100 #12: Blood Frenzy. ALREADY PRESENT (b73) - assert, never dup.
# =============================================================================
def _assert_bloodfrenzy(db):
    _require(db, BLOODFRENZY, 'quak_bloodfrenzy')
    hits = [i for i, p in _skill_slots(db, DEVOURER).items() if _norm(p) == _norm(BLOODFRENZY)]
    if len(hits) != 1:
        raise SystemExit('[devourer_kit] R-100 #12: the Devourer carries '
                         'quak_bloodfrenzy in %d slot(s), expected exactly 1 '
                         '(b73 put it in one). Slots: %s' % (len(hits), hits))
    lvl = _vals(db, DEVOURER, 'skillLevel%d' % hits[0])
    print('  [R-100 #12] Blood Frenzy ALREADY on the Devourer from b73 - '
          'skillName%d @ level %s, Class %s, fires below %g%% life. NOT duplicated.'
          % (hits[0], lvl, _one(db, BLOODFRENZY, 'Class'),
             _one(db, BLOODFRENZY, 'lifeMonitorPercent')))


# =============================================================================
# PART D - R-100 #13: the two minion families + their summons
# =============================================================================
def _build_minion(db, donor, dest, name_tag, life, hand_min, hand_max,
                  scale, run_speed, label):
    _require(db, donor, '%s donor' % label)
    _clone(db, donor, dest)
    db.set_field(dest, 'description', name_tag)
    db.set_field(dest, 'monsterClassification', 'Champion')
    db.set_field(dest, 'charLevel', [40, 68, 100])
    db.set_field(dest, 'characterLife', list(life))
    db.set_field(dest, 'handHitDamageMin', hand_min)
    db.set_field(dest, 'handHitDamageMax', hand_max)
    db.set_field(dest, 'scale', scale)
    # `actorHeight` is DELIBERATELY NOT WRITTEN - it is inherited from the donor.
    # It is a per-RIG constant, not a size knob, and this was measured DB-wide on
    # the built arz (`tools/debug/probe_actorheight.py`):
    #   * 2,122 mesh groups carry an actorHeight on more than one record;
    #     in ZERO of them is actorHeight proportional to `scale`.
    #   * `DRX\meshes\blooddemon01.msh`: 24 records spanning scale 0.7 -> 1.75,
    #     every one of them actorHeight 1.0 (or 0.0 for the no-height class).
    #   * `DRX\meshes\bloodhound.msh`: 9 records spanning scale 1.0 -> **2.25**
    #     - larger than our courser - every one of them actorHeight 1.7.
    # `xbloodhound_36` is the control that settles it: the rig ALREADY has a
    # record scaled bigger than ours and it did not touch the field. An earlier
    # draft of this module invented 1.6 / 1.4, which made both minions the only
    # records on their rig with a bespoke value - and moved the courser's height
    # DOWN while scaling it UP. `scale` is what makes them big; actorHeight is
    # where the engine hangs the name plate and hit FX on the rig. See R-126.
    db.set_field(dest, 'characterRunSpeed', run_speed)
    # A summoned add is not a loot pinata and must never carry a soul (R-101:
    # clones inherit their donor's drops; R-106/R-42: only real encounters pay
    # souls out). uber_quest_markers' roster and soul_identity's rule both key off
    # these two fields, so zeroing them keeps the minions out of both.
    db.set_field(dest, 'dropItems', 0)
    db.set_field(dest, 'chanceToEquipFinger2', 0.0)
    db.set_field(dest, 'DisplayAsQuestItem', 0)
    db._modified.add(dest)
    print('    %s: Champion, band [40,68,100], HP %s, %gx scale, %g/%g hand dmg, '
          'runSpeed %g, dropItems 0, soul chance 0, actorHeight %s INHERITED from '
          'the donor rig (R-126)'
          % (label, list(life), scale, hand_min, hand_max, run_speed,
             _one(db, dest, 'actorHeight')))


def _build_summon(db, dest, spawn, label, note):
    """Clone the PROVEN Enslaver summon shell, repoint its payload, and strip the
    special anim that makes the original never fire."""
    _require(db, ENSLAVER_SUMMON, 'the Enslaver summon shell')
    _clone(db, ENSLAVER_SUMMON, dest)
    _set_ref(db, dest, 'spawnObjects', [spawn])
    db.set_field(dest, 'petBurstSpawn', SUMMON_BURST)
    db.set_field(dest, 'petLimit', SUMMON_PET_LIMIT)
    db.set_field(dest, 'skillCooldownTime', SUMMON_COOLDOWN)
    _del_field(db, dest, 'skillSpecialAnimationName')     # B-SOUL-PROC-2
    db.set_field(dest, 'FileDescription', note)
    db._modified.add(dest)
    print('    %s: petLimit %d / burst %d / cd %gs, anim-less (castable), '
          'spawns %s' % (label, SUMMON_PET_LIMIT, SUMMON_BURST, SUMMON_COOLDOWN,
                         spawn.rsplit('\\', 1)[-1]))


def _build_devourer_summon(db):
    _build_minion(
        db, BLOODSPAWN_DONOR, BLOODSPAWN, 'tagSVCMonsterDevourerBloodspawn',
        life=[4500.0, 6200.0, 8400.0], hand_min=200.0, hand_max=260.0,
        scale=2.4, run_speed=1.3, label='Gorged Bloodspawn')
    _build_summon(
        db, DEV_SUMMON, BLOODSPAWN, 'svc_devourer_summonbloodspawn',
        'SVC Devourer: summons Gorged Bloodspawn - the blood he has drunk, sent '
        'back out (R-100 #13). Anim-less by construction (B-SOUL-PROC-2).')

    slot = _add_kit_skill(db, DEVOURER, DEV_SUMMON, [1, 2, 3])
    was = _one(db, DEVOURER, 'specialAttack5SkillName')
    _set_ref(db, DEVOURER, 'specialAttack5SkillName', DEV_SUMMON)
    db.set_field(DEVOURER, 'specialAttack5Chance', SUMMON_CAST_CHANCE)
    keeps = _slot_of(db, DEVOURER, LILDUDE_SUMMON)
    print('    Devourer skillName%d + specialAttack5 @%g (was %s - a charLevel-9, '
          '1.0-HP pit sprite). RETIREMENT PROTOCOL: that skill record is NOT '
          'deleted, keeps its 2 other carriers, and stays in the Devourer\'s '
          'skillName%s slot.'
          % (slot, SUMMON_CAST_CHANCE,
             str(was).rsplit('\\', 1)[-1] if was else 'absent', keeps))


def _build_hunt_summon(db):
    # the donor hound's own spit is B-SOUL-PROC-2 dead; give the courser a live one
    _require(db, PUKE_DONOR, 'the bloodhound spit donor')
    _clone(db, PUKE_DONOR, COURSER_SPEW)
    had = _one(db, COURSER_SPEW, 'skillSpecialAnimationName')
    _del_field(db, COURSER_SPEW, 'skillSpecialAnimationName')
    db.set_field(COURSER_SPEW, 'FileDescription',
                 'SVC Courser: the hound spit, special anim %r DELETED (the donor '
                 "binds only 'Roar', so B-SOUL-PROC-2 aborted every cast)." % had)
    db._modified.add(COURSER_SPEW)

    _build_minion(
        db, COURSER_DONOR, COURSER, 'tagSVCMonsterHuntCourser',
        life=[3500.0, 4800.0, 6500.0], hand_min=180.0, hand_max=240.0,
        scale=1.7, run_speed=1.6, label='Courser of the Endless Hunt')
    _set_ref(db, COURSER, 'specialAttack2SkillName', COURSER_SPEW)

    _build_summon(
        db, HUNT_SUMMON, COURSER, 'svc_hunt_summoncoursers',
        'SVC Endless Hunt: looses the coursing pack that runs the quarry to '
        'ground (R-100 #13). Anim-less by construction (B-SOUL-PROC-2).')

    _require(db, HUNT, 'the Endless Hunt')
    slot = _add_kit_skill(db, HUNT, HUNT_SUMMON, [1, 2, 3])
    prior = _one(db, HUNT, 'specialAttack5SkillName')
    if prior and str(prior).strip():
        raise SystemExit('[devourer_kit] the Hunt\'s specialAttack5 is no longer '
                         'free (%s) - re-derive the slot plan, do NOT displace it'
                         % prior)
    _set_ref(db, HUNT, 'specialAttack5SkillName', HUNT_SUMMON, DATA_TYPE_STRING)
    db.set_field(HUNT, 'specialAttack5Chance', SUMMON_CAST_CHANCE, DATA_TYPE_FLOAT)
    print('    Hunt skillName%d + specialAttack5 @%g (slot was FREE - nothing '
          'displaced).' % (slot, SUMMON_CAST_CHANCE))
    # same clone-order note as the passive repoint above
    if db.has_record(HUNT_L):
        lslot = _add_kit_skill(db, HUNT_L, HUNT_SUMMON, [1, 2, 3])
        _set_ref(db, HUNT_L, 'specialAttack5SkillName', HUNT_SUMMON, DATA_TYPE_STRING)
        db.set_field(HUNT_L, 'specialAttack5Chance', SUMMON_CAST_CHANCE, DATA_TYPE_FLOAT)
        print('    Hunt(L) skillName%d + specialAttack5 @%g (already minted)'
              % (lslot, SUMMON_CAST_CHANCE))
    else:
        print('    um_toxeus_hunt_l_99 inherits both from its clone base.')


# =============================================================================
# PART E - the sibling defect: the Enslaver's own summon has never fired either
# =============================================================================
def _fix_enslaver_summon(db, census):
    _require(db, ENSLAVER_SUMMON, 'the Enslaver summon')
    outside = [c for c in census['enslaver_summon'] if _norm(c) != _norm(ENSLAVER)]
    if outside:
        raise SystemExit('[devourer_kit] svc_enslaver_summonmarauders has carriers '
                         'outside the Enslaver (%s) - clone instead of editing in '
                         'place (SHARED-RECORD LAW)' % outside)
    had = _one(db, ENSLAVER_SUMMON, 'skillSpecialAnimationName')
    if had and str(had).strip():
        _del_field(db, ENSLAVER_SUMMON, 'skillSpecialAnimationName')
        print('  [SIBLING, flagged for Will] svc_enslaver_summonmarauders demanded '
              'anim %r; anm_skeleton01 binds no such ref, so the marauder summon '
              'R-100 #13 is patterned on has NEVER fired either. Anim DELETED '
              '(1 carrier, so no clone needed). This makes the Enslaver harder - '
              'sanctioned by R-103 "harder is the point", but he did not ask for '
              'it by name.' % had)


# =============================================================================
# entry points
# =============================================================================
def apply(db, tags):
    assert hasattr(db, 'record_names') and hasattr(db, 'set_field'), \
        'devourer_kit.apply: db is not an ArzDatabase'
    print('\n=== patches-registry: %s ===' % MODULE_NAME)

    for r in NEW_RECORDS:
        if db.has_record(r):
            raise SystemExit('[devourer_kit] name collision: %s already exists' % r)

    # SHARED-RECORD LAW: every carrier census is taken ONCE, BEFORE the first
    # mutation, off a single reverse-reference index. Taking them pre-mutation is
    # not just cheaper, it is more honest - "does anything outside our scope carry
    # this record" is a question about the state we INHERITED.
    _bump()
    census = {
        'passive': _passive_carriers(db, SHARED_PASSIVE),
        'bloodboil': sorted({n for n, _ in _carriers(db, BLOODBOIL_SHARED)}),
        'enslaver_summon': sorted({n for n, _ in _carriers(db, ENSLAVER_SUMMON)}),
    }

    _build_monster_passive(db, census)
    _cut_devourer_pierce(db)
    _build_bloodbath(db, census)
    _assert_bloodfrenzy(db)
    _build_devourer_summon(db)
    _build_hunt_summon(db)
    _fix_enslaver_summon(db, census)

    for k, v in TAGS.items():
        tags[k] = v
    print('  authored %d new records + %d Text tags' % (len(NEW_RECORDS), len(TAGS)))
    return tags


# ── THE GATE ─────────────────────────────────────────────────────────────────
def gate_violations(db):
    """Every invariant this wave ships, as a list of human-readable problems.
    Shared by verify() and the planted-negative test, so the negatives exercise
    the SAME code the build gates on."""
    p = []

    # -- 1. the monster-only passive carries Will's numbers ------------------
    if not db.has_record(MONSTER_PASSIVE):
        p.append('monster-only passive missing: %s' % MONSTER_PASSIVE)
    else:
        r = _one(db, MONSTER_PASSIVE, 'defensiveReflect')
        c = _one(db, MONSTER_PASSIVE, 'defensiveReflectChance')
        if r != REFLECT_MONSTER:
            p.append('monster passive defensiveReflect %s != %g' % (r, REFLECT_MONSTER))
        if c != REFLECT_CHANCE:
            p.append('monster passive defensiveReflectChance %s != %g (R-103 ruled '
                     'the CHANCE must not be the lever)' % (c, REFLECT_CHANCE))

    # -- 2. carrier sets, tested in BOTH directions -------------------------
    new_carriers = set(_passive_carriers(db, MONSTER_PASSIVE))
    old_carriers = set(_passive_carriers(db, SHARED_PASSIVE))
    want_new = {c for c in PASSIVE_TARGETS_ALL if db.has_record(c)}
    missing = {_norm(x) for x in want_new} - {_norm(x) for x in new_carriers}
    extra = {_norm(x) for x in new_carriers} - {_norm(x) for x in want_new}
    for m in sorted(missing):
        p.append('Toxeus MONSTER not on the monster-only passive: %s' % m)
    for e in sorted(extra):
        p.append('SCOPE CREEP - unexpected carrier on the monster-only passive: %s' % e)

    for keep in KEEP_ORIGINAL:
        if not db.has_record(keep):
            continue
        if _norm(keep) in {_norm(x) for x in new_carriers}:
            p.append('R-107 VIOLATION - %s landed on the MONSTER passive; pets, '
                     'less.dbr and the zzdev dummies must keep 100/33' % keep)
        if _norm(keep) not in {_norm(x) for x in old_carriers}:
            p.append('R-107 VIOLATION - %s fell OFF the original shared passive' % keep)

    # -- 3. the original passive is untouched -------------------------------
    if db.has_record(SHARED_PASSIVE):
        if _one(db, SHARED_PASSIVE, 'defensiveReflect') != 100.0:
            p.append('the ORIGINAL toxeus_passiveproperties was edited '
                     '(defensiveReflect %s != 100.0) - that is the in-place nerf '
                     'R-107 forbids' % _one(db, SHARED_PASSIVE, 'defensiveReflect'))
        if _one(db, SHARED_PASSIVE, 'defensiveReflectChance') != 33.0:
            p.append('the ORIGINAL toxeus_passiveproperties chance was edited')

    # -- 4. the Devourer's pierce cut + the reserved life lever --------------
    if db.has_record(DEVOURER):
        pierce = _one(db, DEVOURER, 'defensivePierce')
        if pierce != DEVOURER_PIERCE:
            p.append('Devourer defensivePierce %s != %g' % (pierce, DEVOURER_PIERCE))
        life = _vals(db, DEVOURER, 'characterLife')
        if life != DEVOURER_LIFE_RESERVED:
            p.append('Devourer characterLife %s moved - R-107 reserves it as the '
                     'THIRD lever and this wave must not spend it' % life)

    # -- 5. Bloodbath: cloned, retuned, castable, wired ----------------------
    if not db.has_record(BLOODBATH):
        p.append('svc_devourer_bloodbath missing')
    else:
        cd = _one(db, BLOODBATH, 'skillCooldownTime')
        if cd != BLOODBATH_COOLDOWN:
            p.append('Bloodbath skillCooldownTime %s != %g' % (cd, BLOODBATH_COOLDOWN))
        anim = _one(db, BLOODBATH, 'skillSpecialAnimationName')
        if anim is not None and str(anim).strip():
            p.append('Bloodbath still declares skillSpecialAnimationName %r - '
                     'B-SOUL-PROC-2 will abort every cast' % anim)
        if _one(db, BLOODBATH, 'Class') != 'Skill_AttackRadius':
            p.append('Bloodbath Class %r != Skill_AttackRadius' % _one(db, BLOODBATH, 'Class'))
        sn = _one(db, DEVOURER, 'specialAttackSkillName')
        if _norm(sn or '') != _norm(BLOODBATH):
            p.append('Devourer specialAttackSkillName %r is not Bloodbath' % sn)
        elif (_one(db, DEVOURER, 'specialAttackChance') or 0) <= 0:
            p.append('Devourer Bloodbath cast chance <= 0')
        if _slot_of(db, DEVOURER, BLOODBATH) is None:
            p.append('Bloodbath is not in any Devourer skillName slot')

    # -- 6. the shared Bloodbath donor is untouched --------------------------
    if db.has_record(BLOODBOIL_SHARED):
        if _one(db, BLOODBOIL_SHARED, 'skillCooldownTime') != 45.0:
            p.append('melinoe_bloodboil cooldown was edited in place - that buffs '
                     'the 6 Toxeus PET carriers Will did not ask about')
        if not str(_one(db, BLOODBOIL_SHARED, 'skillSpecialAnimationName') or '').strip():
            p.append('melinoe_bloodboil lost its own special anim (it must stay '
                     'intact for its pet + pcsafe consumers)')

    # -- 7. Blood Frenzy: present exactly once, live, in range ---------------
    if db.has_record(DEVOURER) and db.has_record(BLOODFRENZY):
        hits = [i for i, s in _skill_slots(db, DEVOURER).items()
                if _norm(s) == _norm(BLOODFRENZY)]
        if len(hits) != 1:
            p.append('Blood Frenzy sits in %d Devourer slot(s), expected exactly 1' % len(hits))
        else:
            lv = _vals(db, DEVOURER, 'skillLevel%d' % hits[0])
            mx = _one(db, BLOODFRENZY, 'skillMaxLevel') or 0
            if not lv or min(lv) < 1:
                p.append('Blood Frenzy level %s has a 0 - a level-0 passive does nothing' % lv)
            if lv and max(lv) > mx:
                p.append('Blood Frenzy level %s exceeds skillMaxLevel %s' % (lv, mx))
        if _one(db, BLOODFRENZY, 'Class') != 'Skill_PassiveOnLifeBuffSelf':
            p.append('quak_bloodfrenzy is not an on-life trigger any more')
        if (_one(db, BLOODFRENZY, 'lifeMonitorPercent') or 0) <= 0:
            p.append('quak_bloodfrenzy lifeMonitorPercent <= 0 - it can never trigger')

    # -- 8. the summons ------------------------------------------------------
    for skill, host, spawn, label in ((DEV_SUMMON, DEVOURER, BLOODSPAWN, 'Devourer'),
                                      (HUNT_SUMMON, HUNT, COURSER, 'Hunt'),
                                      (HUNT_SUMMON, HUNT_L, COURSER, 'Hunt(L)')):
        if not db.has_record(skill):
            p.append('%s summon missing: %s' % (label, skill))
            continue
        if _one(db, skill, 'Class') != 'Skill_SpawnPetMonster':
            p.append('%s summon Class %r != Skill_SpawnPetMonster'
                     % (label, _one(db, skill, 'Class')))
        anim = _one(db, skill, 'skillSpecialAnimationName')
        if anim is not None and str(anim).strip():
            p.append('%s summon still declares anim %r - it would never fire'
                     % (label, anim))
        objs = _vals(db, skill, 'spawnObjects')
        if not objs or _norm(objs[0]) != _norm(spawn):
            p.append('%s summon spawnObjects %s does not name %s' % (label, objs, spawn))
        elif not db.has_record(objs[0]):
            p.append('%s summon payload does not resolve: %s' % (label, objs[0]))
        lim = _one(db, skill, 'petLimit') or 0
        if not 0 < lim <= SUMMON_LIMIT_CEILING:
            p.append('%s summon petLimit %s outside the ruled 1..%d band (b76 '
                     'chumbi-freeze density law)' % (label, lim, SUMMON_LIMIT_CEILING))
        if not db.has_record(host):
            continue
        if _norm(_one(db, host, 'specialAttack5SkillName') or '') != _norm(skill):
            p.append('%s specialAttack5 does not point at its own summon' % label)
        elif (_one(db, host, 'specialAttack5Chance') or 0) <= 0:
            p.append('%s summon cast chance <= 0' % label)
        if _slot_of(db, host, skill) is None:
            p.append('%s summon is not in any skillName slot on its caster' % label)

    # -- 9. the minions read as real, and leak nothing -----------------------
    for mon, label in ((BLOODSPAWN, 'Gorged Bloodspawn'),
                       (COURSER, 'Courser of the Endless Hunt')):
        if not db.has_record(mon):
            p.append('%s missing: %s' % (label, mon))
            continue
        if _one(db, mon, 'monsterClassification') != 'Champion':
            p.append('%s is not a Champion (Will: the adds "appear just like '
                     'normal guys")' % label)
        if (_one(db, mon, 'chanceToEquipFinger2') or 0) != 0:
            p.append('%s can drop a SOUL - a summoned add must never pay one out '
                     '(R-42/R-106)' % label)
        if (_one(db, mon, 'dropItems') or 0) != 0:
            p.append('%s has dropItems != 0 - a re-summonable add would be an '
                     'infinite loot faucet' % label)
        if (_one(db, mon, 'DisplayAsQuestItem') or 0) != 0:
            p.append('%s carries the uber quest marker - it is not a placed uber' % label)
        if str(_one(db, mon, 'treasureProxyName') or '').strip():
            p.append('%s carries a treasureProxyName (orb chain leak)' % label)
        if not _vals(db, mon, 'characterLife') or min(_vals(db, mon, 'characterLife')) < 1000:
            p.append('%s characterLife %s is trash-tier'
                     % (label, _vals(db, mon, 'characterLife')))
        # R-126: actorHeight is a per-RIG constant, never a size knob. Measured
        # DB-wide: of 2,122 mesh groups carrying an actorHeight on >1 record,
        # ZERO make it proportional to `scale`. Both donor rigs hold it flat
        # across their whole size ladder (blooddemon01 1.0 over scale 0.7..1.75;
        # bloodhound 1.7 over scale 1.0..2.25, i.e. a record BIGGER than ours).
        # So the invariant is inheritance from the donor, checked live against
        # the donor record - which the record-diff proves byte-unchanged.
        donor = MINION_DONORS.get(mon)
        if donor and db.has_record(donor):
            got = _one(db, mon, 'actorHeight')
            want = _one(db, donor, 'actorHeight')
            if got != want:
                p.append('%s actorHeight %s != its donor rig\'s %s - actorHeight is '
                         'where the engine hangs the name plate and hit FX on the '
                         'mesh, and it is NOT a size knob (R-126). Scale the model '
                         'with `scale`, inherit this.' % (label, got, want))

    # -- 10. THE CASTABILITY GATE (b94 lesson, B-SOUL-PROC-2 monster side) ---
    for rec in CASTERS:
        if not db.has_record(rec):
            continue
        p.extend(_anim_violations(db, rec))
        for field, sk in _l0_special_offenders(db, rec):
            p.append('%s: %s casts level-0 skill %s' % (rec, field, sk))

    # -- 11. every new record actually exists --------------------------------
    for r in NEW_RECORDS:
        if not db.has_record(r):
            p.append('new record missing from the built db: %s' % r)

    return p


def verify(db, tags=None):
    # every other registry module has run since apply(); toxeus_hunt_endless in
    # particular MINTED um_toxeus_hunt_l_99 off the base Hunt. Force a fresh index.
    _bump()
    problems = gate_violations(db)
    if problems:
        for x in problems:
            print('  DEVOURER-KIT OFFENDER: %s' % x)
        raise SystemExit('devourer_kit.verify FAILED: %d problem(s)' % len(problems))

    new_c = _passive_carriers(db, MONSTER_PASSIVE)
    old_c = _passive_carriers(db, SHARED_PASSIVE)
    print('  [devourer_kit] verify OK: monster-only passive %g/%g carried by EXACTLY '
          'the %d Toxeus monsters; the original stays 100/33 for %d carrier(s) '
          'incl. all 9 pets + less.dbr; Devourer pierce %g, life %s untouched; '
          'Bloodbath cd %g anim-less and cast @%s; Blood Frenzy present once; '
          'both summons anim-less @petLimit %d; both minions Champion, soul-less, '
          'loot-less; 0 unbound special animations across %d casters.'
          % (REFLECT_MONSTER, REFLECT_CHANCE, len(new_c), len(old_c),
             DEVOURER_PIERCE, _vals(db, DEVOURER, 'characterLife'),
             BLOODBATH_COOLDOWN, _one(db, DEVOURER, 'specialAttackChance'),
             SUMMON_PET_LIMIT, len(CASTERS)))
    return tags


# ── planted negatives ────────────────────────────────────────────────────────
def _negtest(arz):
    """Prove the gate is not vacuous: eight plants, each over a throwaway db,
    each asserted to FIRE, plus a clean control."""
    from arz_patcher import ArzDatabase
    db = ArzDatabase.from_arz(Path(arz))
    apply(db, {})
    # the L variant does not exist in a bare apply() (its author runs later), so
    # mint the same clone the registry would, to exercise the full carrier gate.
    if not db.has_record(HUNT_L):
        _clone(db, HUNT, HUNT_L)

    control = gate_violations(db)
    results = []

    def plant(label, mutate, restore, needle, moves_a_ref=False):
        mutate()
        if moves_a_ref:
            _bump()
        fired = any(needle.lower() in v.lower() for v in gate_violations(db))
        restore()
        if moves_a_ref:
            _bump()
        results.append((label, fired))

    plant('N1 reflect back to 100 on the monster passive',
          lambda: db.set_field(MONSTER_PASSIVE, 'defensiveReflect', 100.0),
          lambda: db.set_field(MONSTER_PASSIVE, 'defensiveReflect', REFLECT_MONSTER),
          'defensiveReflect')

    pet = PETS_KEEP_ORIGINAL[3]      # pets\bloodtoxeus_1
    pet_slot = _slot_of(db, pet, SHARED_PASSIVE)
    plant('N2 a PET dragged onto the monster passive',
          lambda: db.set_field(pet, 'skillName%d' % pet_slot, MONSTER_PASSIVE),
          lambda: db.set_field(pet, 'skillName%d' % pet_slot, SHARED_PASSIVE),
          'R-107 VIOLATION', moves_a_ref=True)

    plant("N3 'BloodBoil' put back on Bloodbath",
          lambda: db.set_field(BLOODBATH, 'skillSpecialAnimationName', 'BloodBoil',
                               DATA_TYPE_STRING),
          lambda: _del_field(db, BLOODBATH, 'skillSpecialAnimationName'),
          'B-SOUL-PROC-2')

    plant('N4 an unbounded summon (petLimit 12)',
          lambda: db.set_field(DEV_SUMMON, 'petLimit', 12),
          lambda: db.set_field(DEV_SUMMON, 'petLimit', SUMMON_PET_LIMIT),
          'petLimit')

    plant('N5 a minion given a soul drop',
          lambda: db.set_field(BLOODSPAWN, 'chanceToEquipFinger2', 66.0),
          lambda: db.set_field(BLOODSPAWN, 'chanceToEquipFinger2', 0.0),
          'can drop a SOUL')

    plant('N6 pierce back to 70 on the Devourer',
          lambda: db.set_field(DEVOURER, 'defensivePierce', 70.0),
          lambda: db.set_field(DEVOURER, 'defensivePierce', DEVOURER_PIERCE),
          'defensivePierce')

    bf_slot = _slot_of(db, DEVOURER, BLOODFRENZY)
    plant('N7 Blood Frenzy removed from the Devourer',
          lambda: db.set_field(DEVOURER, 'skillName%d' % bf_slot, BLOODFRENZY.replace(
              'quak_bloodfrenzy', 'hero_scaling')),
          lambda: db.set_field(DEVOURER, 'skillName%d' % bf_slot, BLOODFRENZY),
          'Blood Frenzy sits in 0', moves_a_ref=True)

    plant('N8 characterLife spent (the reserved third lever)',
          lambda: db.set_field(DEVOURER, 'characterLife', [9000.0, 12000.0, 16000.0]),
          lambda: db.set_field(DEVOURER, 'characterLife', DEVOURER_LIFE_RESERVED),
          'reserves it as the THIRD lever')

    plant('N9 the in-place edit R-107 forbids (original passive nerfed)',
          lambda: db.set_field(SHARED_PASSIVE, 'defensiveReflect', 30.0),
          lambda: db.set_field(SHARED_PASSIVE, 'defensiveReflect', 100.0),
          'ORIGINAL toxeus_passiveproperties was edited')

    # This is the EXACT defect that shipped in the first draft of this module and
    # that the record-diff could never have caught (an invented value on a record
    # that is itself new is not a "change" against any baseline). It took a
    # DB-wide measurement of the rig to see. The plant re-creates it verbatim.
    courser_h = _one(db, COURSER, 'actorHeight')
    plant('N10 a minion given a bespoke actorHeight (the R-126 defect)',
          lambda: db.set_field(COURSER, 'actorHeight', 1.4),
          lambda: db.set_field(COURSER, 'actorHeight', courser_h),
          "actorHeight is where the engine hangs the name plate")

    print('\ndevourer_kit _negtest (%s):' % arz)
    for label, fired in results:
        print('  %-52s flagged: %s' % (label, fired))
    print('  %-52s clean  : %s %s'
          % ('control (the shipped state)', control == [], control))
    ok = all(f for _, f in results) and control == []
    print('  -> %s (%d/%d plants fired)'
          % ('PASS' if ok else 'FAIL', sum(1 for _, f in results if f), len(results)))
    return 0 if ok else 1


def _analyze(arz):
    """Read-only census of the two shared records this wave must not edit."""
    from arz_patcher import ArzDatabase
    db = ArzDatabase.from_arz(Path(arz))
    print('\nARZ: %s' % arz)
    for rec, label in ((SHARED_PASSIVE, 'toxeus_passiveproperties'),
                       (BLOODBOIL_SHARED, 'melinoe_bloodboil')):
        cs = sorted({n for n, _ in _carriers(db, rec)})
        print('\n  %s : %d carrier(s)' % (label, len(cs)))
        for c in cs:
            kind = ('PET' if '\\pets\\' in c else
                    'zzdev' if '\\zzdev\\' in c else
                    'FOREIGN' if 'crowheroes' in c else 'monster/other')
            print('    [%-13s] %s' % (kind, c))
    for rec in CASTERS:
        if db.has_record(rec):
            v = _anim_violations(db, rec)
            print('\n  castability %s : %s' % (rec.rsplit('\\', 1)[-1],
                                               v if v else 'clean'))


if __name__ == '__main__':
    args = sys.argv[1:]
    DEFAULT_ARZ = (Path(__file__).resolve().parents[2]
                   / 'work' / 'SoulvizierClassic' / 'Database' / 'BASELINE.arz')
    if '--negtest' in args:
        i = args.index('--negtest')
        raise SystemExit(_negtest(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ))
    elif '--analyze' in args:
        i = args.index('--analyze')
        _analyze(args[i + 1] if len(args) > i + 1 else DEFAULT_ARZ)
    else:
        print(__doc__)
