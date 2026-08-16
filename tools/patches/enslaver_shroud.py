r"""enslaver_shroud - THE ENSLAVER'S BLACK SHADOW SHROUD (b98 R-95, b102 R-102,
b104 R-250).

WILL (2026-08-11), verbatim, the THIRD filing of the same sentence:

> "toxeus the murderer, devourer of souls we need to add the black shadow shroud
>  around him, the same one that his demon summon guys have"

--------------------------------------------------------------------------------
b104 - WHICH TOXEUS. THE NAME IS FUSED; THE DEMON CLAUSE RESOLVES IT
--------------------------------------------------------------------------------
No variant is called "Devourer of Souls". The name fuses two of them - "Toxeus
the Murderer, DEVOURER OF BLOOD" and "Toxeus the Murderer, ENSLAVER OF SOULS" -
so the only discriminating words in the sentence are **"the same one that his
demon summon guys have"**. That clause was measured on the shipped `build83` arz
(`44499f56`, the hash `docs/HANDOFF_LIVE_STATE.md` records as LIVE) at the layer
that actually renders, which is NOT the `.dbr` field layer:

| whose demons | record | mesh | mesh-embedded FX (always on) |
|---|---|---|---|
| **ENSLAVER's** Enslaved Shadow Marauders | `um_enslaver_marauder_99`, `pets\enslaver_marauder_1..3` | `ShadowStalker.msh` | **`Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr`** -> `Effects\MonsterFX\ShadowStalker_Smoke01.pfx` |
| DEVOURER's Blood Demons | `drxcreatures\blooddemon\um_devourer_bloodspawn_99` | `DRX\meshes\blooddemon01.msh` | `FX_blood_CHEST/HANDS/HEAD_fx` - BLOOD effects, no shadow shroud |

Only the Enslaver's demons carry a black shadow shroud, and Will has confirmed
that one by eye (R-102 fourth amendment, verbatim: *"yes the demons that he
summons have the proper black shroud and they dont have any green"*). The same
sentence was filed as R-95 on 2026-07-28 ("the same black shroud smoke his
summoned demons have") and again as R-102's second amendment ("that is still not
implemented"). **Target: Toxeus the Murderer, ENSLAVER OF SOULS.**

--------------------------------------------------------------------------------
b104 - WHY HE STILL HAS NO SHROUD, AFTER TWO WAVES THAT SAID HE DID
--------------------------------------------------------------------------------
Because both prior waves worked in the `.dbr` FIELD layer and the demons' shroud
was never in a field. It is compiled into their MESH:

    ShadowStalker.msh ... CreateEntity { attach = "SpecialHit01";
                                         entity = "Records\Effects\MonsterFX\
                                                   ShadowStalker_Smoke.dbr" }

A mesh renders every frame. That is why the marauders smoke constantly, standing
still, out of combat - and why nothing the Enslaver had could match it. Note the
attach name in that block: it is the one we copy (section B below), and it is on
his rig too.

  1. `charFxPakRunningNames` -> `drxshadowcloakrunning_fx_pak` renders ONLY while
     the character RUNS (R-95's finding). He is a caster who stands and casts.
  2. `svc_enslaver_shroud` (b98/b102) is a `Skill_BuffSelfToggled`, and both his
     controllers shipped `BuffSelfBehavior = WhenEnemyIsSeen` - so it fires when
     a fight starts and is OFF when Will stands looking at the summoned pet,
     which is exactly how he inspects it (the R-102 screenshot).
  3. Worse, BOTH of those channels pointed at `drxshadowcloakrunning_fx`, whose
     own `boneList = Bone_R_Weapon; Bone_L_Weapon` pins the smoke to his two
     WEAPON bones. Even when it did play it came off his fists, not from around
     him - the round-4 defect R-95 fixed at the PAK layer while the EffectEntity
     underneath kept doing it.
  4. And `champion_mesh` (b102, R-102) moved him off `RevenantPoison.msh` to kill
     the green - onto `SkeletonGrayBlack01New.msh`, which carries NO embedded FX
     at all. That fix was right and it is not being undone; but it removed his
     last always-on emitter, which is why this request arrives now.

--------------------------------------------------------------------------------
b104 - THE FIX: THE DEMONS' OWN PARTICLE, ON A BODY BONE, ALWAYS ON
--------------------------------------------------------------------------------
Three legs, all on MONSTER-RECORD fields and skill records (CRASH LAW: never a
`charFxPak*` on a SpawnPet skill - the build28 trap, asserted in verify()):

  A. **THE ASSET.** `svc_enslaver_shroud_fx` is a FIELD-FOR-FIELD MIRROR of the
     demons' own base-game EffectEntity `Records\Effects\MonsterFX\
     ShadowStalker_Smoke.dbr`, which is exactly four fields:

         templateName = database\Templates\Effect.tpl
         ActorName    = Effects_Fire_EarthPet_Core02
         Class        = EffectEntity
         effectFile   = Effects\MonsterFX\ShadowStalker_Smoke01.pfx

     `drxshadowcloakrunning_fx` is used only as a record SHELL and then PRUNED to
     that set: its `boneList = Bone_R_Weapon;Bone_L_Weapon` (the reason every
     previous rendering came off his fists) and its `Anchored`/`emitterType`/
     `localOrientFix` all go. Donor residue is not a neutral default - those three
     came off a weapon-bone-attached effect and their behaviour on a body attach
     point is unproven, so the honest move is to carry none of them. verify()
     re-reads the demons' record out of the base `.arz` and FAILS if our field set
     or any value drifts from theirs, so "the same one his demons have" is a
     DERIVED claim about the whole record and not just about the `.pfx`.
     It is our own record rather than a live reference to theirs so that the build
     can read, gate and diff it, and so a future game patch cannot change what he
     wears without this gate noticing.

  B. **THE SHAPE.** `particleEffectAttachPoints = ['SpecialHit01']` - THE DEMONS'
     OWN ATTACH POINT, derived from their mesh's `CreateEntity{attach=...}` block
     rather than chosen. Measured in both binaries (b104 round 2, correcting a
     false measurement round 1 recorded as law):

       SkeletonGrayBlack01New.msh (his rig) AttachPoints: Head, HeadEffect,
         L Hand, Prey_Effect, R Hand, SpecialHit01..04, Target, Upper Body
       ShadowStalker.msh (the demons' rig): the SAME set plus `Smoke02`

     `SpecialHit01` is present on BOTH, and its block is byte-identical on both
     rigs - `origin = (0,0,0)` with identity axes, i.e. the model origin, a
     ground-up body column. So the smoke hangs on him exactly where it hangs on
     them. Round 1 excluded it on the claim that it "does not exist on
     `SkeletonGrayBlack01New.msh`"; that claim came from a reader that scanned only
     NUL-terminated strings, and AttachPoint names live in a CRLF text block with
     no NUL in it. The instrument was structurally blind to the class of name it
     was asked about. `tools/mesh_assets.rig_names_of()` now reads BOTH tables.

     Namespace matters as much as spelling: `particleEffectAttachPoints` values in
     this DB are overwhelmingly AttachPoint names ('L Hand' x21, 'R Hand' x20,
     'SpecialHit03' x4, 'HeadEffect' x4, ...) against exactly 5 rows using a raw
     `Bone_*`, and one of this mod's own shipped paks (`hemor_charfx`) already
     attaches at `SpecialHit03` on a skeleton rig. `Bone_Waist` (round 1's choice)
     is the thinly-precedented namespace, is an animated pelvis joint rather than
     the model origin, and its stated justification - "where `RevenantPoison_FX`
     hung its aura on his old mesh" - was also false: that mesh's block reads
     `attach = "Waist"`, the ATTACHPOINT `Waist`, which his current rig does not
     declare at all.

     verify() re-reads the wearer's mesh binary and FAILS if any attach point this
     pak names is missing from that rig, matching CASEFOLDED because the shipped
     DB addresses these tables off-case (`Bone_spine01`, `Specialhit03`).

  C. **ALWAYS ON.** Every roster surface gets an SVC-OWNED CLONE of whatever
     controller it currently carries, with the single field `BuffSelfBehavior`
     set to `WheneverPossible` (34 shipped carriers, including the DRX demon
     controllers). The shared originals are NEVER edited: `controller_skeleton_
     toxeus` also drives the Devourer and 4 others, and `controller_skelly_
     aggressive` drives 148 pets. Flipping this is provably visual-only here
     because the shroud is the ONLY `Skill_BuffSelf*` in either kit (measured:
     monster slot 19, pets slot 13, nothing else) - and verify() asserts that,
     so the day someone adds a real self-buff to him the gate fails instead of
     quietly changing a boss fight.

`charFxPakRunningNames` is KEPT untouched on every surface (ADD, never take
away): the demons carry it too, so he still smokes harder when he moves.

WHAT IS NOT CLAIMED: how it READS in game. Nobody has seen it. `BL-R250-DEBT-1`.

--------------------------------------------------------------------------------
WHAT THIS MODULE DOES NOT TOUCH (reported, not silently deferred)
--------------------------------------------------------------------------------
  * **The Devourer of Blood.** He has no body shroud either (`GoldenSkeleton01.msh`
    is FX-free, he has no `charFxPakRunningNames`, and his only FX is R-7's
    `svc_black_poison` = two HAND emitters of the not-colour-confirmed
    `343_dark_smoke`). That is a real gap - but Will did not ask for it, his
    demons are BLOOD demons with no shadow shroud to copy, and crimson is his
    design. It is a QUESTION for Will, registered as `BL-R250-DEBT-2`, not a
    change this lane makes on its own authority.
  * **The Endless Hunt** already wears `ShadowStalker.msh` and therefore already
    has the demons' embedded smoke, by construction. Nothing to do.
  * **`svc_black_poison`, meshes, textures, skills, stats.** Not this lane's.
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Enslaver persistent black shadow shroud (R-95 / R-102 / R-250)"

DATA_TYPE_INT = 0
DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2

_ENSLAVER = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
_MARAUDER = r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'
# b102 (R-102 second amendment): the surface Will actually looks at. The pet TIERS
# are never listed - they are read out of this summon's spawnObjects, so the
# roster cannot go stale when a tier is added.
_ENSLAVER_SUMMON = r'records\skills\soulskills\summon_toxeus_enslaver.dbr'
# W2, the second roster witness: anything carrying his name tag. This is what
# catches a difficulty CLONE minted at build time (the Hunt has exactly one,
# `um_toxeus_hunt_l_99`) that the summon chain cannot see.
_NAME_TAGS = ('tagsvcmonsterenslaver', 'tagsvcmonsterenslaverpet')

# ── the demons' own shroud, measured not assumed ────────────────────────────
# `um_enslaver_marauder_99.mesh` = ShadowStalker.msh, whose binary ends in
#   CreateEntity { attach = "SpecialHit01"; entity = "<_DEMON_FX_REF>" }
# and that base-game EffectEntity plays <_DEMON_PFX>. verify() re-derives the
# first from the mesh every build, so if the marauders' shroud ever moves, the
# "same one his demons have" claim fails loud instead of silently going stale.
_DEMON_FX_REF = r'records\effects\monsterfx\shadowstalker_smoke.dbr'
_DEMON_PFX = r'Effects\MonsterFX\ShadowStalker_Smoke01.pfx'
# The demons' MESH attach helper, and the one we COPY: it is declared on the
# Enslaver's rig too, with a byte-identical block (origin (0,0,0), identity axes).
# Pinned so the build is deterministic without the game install; verify() DERIVES
# it from the marauders' mesh binary and fails loud if the two ever disagree.
_DEMON_MESH_ATTACH = 'SpecialHit01'
# The demons' own EffectEntity, field for field (read out of the base-game .arz).
# Our record is pruned to exactly this; verify() re-derives it and fails on drift.
_DEMON_FX_FIELDS = (
    ('templateName', r'database\Templates\Effect.tpl'),
    ('ActorName', 'Effects_Fire_EarthPet_Core02'),
    ('Class', 'EffectEntity'),
    ('effectFile', _DEMON_PFX),
)

# the running channel both he and his demons already carry (kept, never removed)
_SHADOWCLOAK_FX = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx.dbr'
_SHADOWCLOAK_PAK = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr'

# structure donors (both DB-verified)
_SKILL_DONOR = r'records\skills\monster skills\buff_self\empusamerc_enchantment.dbr'
_PAK_DONOR = r'records\effects\weaponenchantments\343_weapon_poisoncharfxpak.dbr'
_FX_DONOR = _SHADOWCLOAK_FX          # an EffectEntity we already ship + gate

_SHROUD = r'records\skills\monster skills\buff_self\svc_enslaver_shroud.dbr'
_SHROUD_PAK = r'records\skills\monster skills\buff_self\svc_enslaver_shroud_charfxpak.dbr'
_SHROUD_FX = r'records\skills\monster skills\buff_self\svc_enslaver_shroud_fx.dbr'

# ── SHAPE (b104 round 2) ────────────────────────────────────────────────────
# THE DEMONS' OWN ATTACH POINT. Measured present on his rig (and byte-identical
# to theirs). Never 'R Hand'/'L Hand' (the b98 round-4 defect: smoke off two
# fists), and never `Smoke02` - THAT is the helper the demons have and he does
# not, so it is the one that would render nothing at all.
_ATTACH = [_DEMON_MESH_ATTACH]
_PARTICLE_COUNT = 1     # ONE body emitter, exactly like the demons' one CreateEntity
# A name on the demons' rig that his rig does NOT declare. Kept as the concrete
# example of the silent-nothing trap, and exercised as a negtest plant.
_DEMON_ONLY_ATTACH = 'Smoke02'

# ── ALWAYS ON (b104) ────────────────────────────────────────────────────────
_BUFF_TRIGGER = 'WheneverPossible'
_CTRL_PREFIX = 'svc_alwayson_'

# ── R-255 (b99): THE SLOT CEILING, AND THE TWO CHANNELS THAT ACTUALLY EXIST ──
# `skillName<N>` is NOT an open-ended array. It is declared, exactly once, in
# `Templates\TemplateBase\MonsterSkillManager.tpl` - the template `Monster.tpl`
# includes and `Pet.tpl` inherits through it - and that declaration stops at
# **skillName17 / skillLevel17**. Two independent witnesses, both re-checked by
# `--selftest`:
#   1. the vanilla template itself declares skillName1..17 and nothing above it;
#   2. across all 74,013 base-game records, the highest slot ANY Monster or Pet
#      uses is skillName17 (1,136 records sit exactly on it, 0 records above it).
# b98/R-250 wired the shroud with `_free_skillname_slot(..., hi=23)` on the
# written-down belief that "the template reaches 23". It does not; 23 was the
# highest slot THIS MOD had already written, i.e. the lane measured its own
# earlier overflow and read it as headroom. So the shroud landed at skillName19
# on the boss and skillName18 on all three pet tiers - fields no skill manager
# reads - and the whole b93 ship was a write into a slot that does not exist.
# That is why Will filed "still do not have the black smoke" a fourth time.
_ENGINE_SKILL_SLOT_MAX = 17
# The channels that DO exist, both declared in that same MonsterSkillManager and
# therefore identical on Monster and Pet, both crash-law-safe (skill fields, the
# only class Pet.tpl tolerates), both measured in the base game:
#   `initialSkillName`  - cast once at spawn; 90 vanilla Pets + 838 Monsters use
#                         it, 153 of them pointing at a Skill_BuffSelfToggled
#                         exactly like ours. A toggle cast at spawn is ON from
#                         the first frame and owes the AI nothing, which is the
#                         closest record-field analogue of the demons' mesh FX.
#   `buffSelfSkillName` - the AI's self-buff slot, gated by the controller's
#                         BuffSelfBehavior (ours are WheneverPossible clones);
#                         87 vanilla Pets + 522 Monsters use it, 60 on a
#                         Skill_BuffSelfToggled. This is the re-application leg:
#                         if the toggle is ever dropped it comes straight back.
# Both are FREE on all 8 family records today (measured on the shipped build98
# arz `15dacc68`), so this ADDS and displaces nothing.
_ALWAYS_ON_FIELDS = ('initialSkillName', 'buffSelfSkillName')

# ── R-255: THE FAMILY, AND THE TWO ROUTES A MEMBER MAY WEAR THE SHROUD BY ────
# b93 scoped itself to the wild boss + the pet tiers his soul summons. It never
# reached the MARAUDERS - neither the escorts the wild boss raises nor the
# pet-of-pet marauders the SUMMONED Enslaver raises - so "the family has the
# family FX" was never actually a checked claim. Those marauders wear
# ShadowStalker.msh and therefore already carry the shroud the only way it ever
# really worked: compiled into the mesh. So a member is covered if EITHER
#   MESH  - its rig embeds the demons' own `ShadowStalker_Smoke.dbr`, or
#   FIELD - it carries `svc_enslaver_shroud` in BOTH always-on fields above.
# Deriving MESH from the binary is what keeps this honest: the day a marauder is
# moved onto an FX-free rig (exactly what `champion_mesh` did to the Enslaver,
# which is how his last always-on emitter vanished) it stops satisfying MESH and
# the build fails until it is given FIELD instead.
_PINNED_SMOKE_RIGS = (r'creatures\monster\shadowstalker\shadowstalker.msh',)
# every field that can name a pet-spawning skill, so the family closure is walked
# rather than listed (a 4th tier, a new escort or a new pet-of-pet joins by
# itself - the b98 failure mode was a roster that could go stale in silence)
_SPAWN_FIELDS = ('specialAttackSkillName', 'specialAttack2SkillName',
                 'specialAttack3SkillName', 'specialAttack4SkillName',
                 'specialAttack5SkillName', 'initialSkillName')
_FAMILY_MAX_DEPTH = 4

# ── TEST HOOKS ──────────────────────────────────────────────────────────────
# The two asset-level gates read `.msh` binaries out of the shipped `.arc`s. The
# negative test cannot ship archives, so it injects the two answers instead. In a
# real build both stay None and the gates read the real assets (or announce a
# loud DOWNGRADE - never a silent pass).
_RIG_NAMES_OVERRIDE = None      # {mesh_ref_lower: set(bone + AttachPoint names)}
_DEMON_FX_OVERRIDE = None       # [entity refs embedded in the demons' mesh]
_DEMON_ATTACH_OVERRIDE = None   # the attach name in the demons' CreateEntity
_DEMON_FX_RECORD_OVERRIDE = None  # {field: value} of the demons' EffectEntity
_MESH_SMOKE_OVERRIDE = None     # {mesh_ref_lower: bool} does this rig embed it


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) and v else v


def _lst(db, rec, f):
    v = db.get_field_value(rec, f)
    if v is None:
        return []
    return [str(x) for x in (v if isinstance(v, list) else [v]) if str(x).strip()]


def _require(db, *recs):
    missing = [r for r in recs if not db.has_record(r)]
    if missing:
        raise SystemExit("[enslaver_shroud] required record(s) missing: %s" % missing)


def _skill_slots(db, rec):
    """{slot: skill path} for every non-blank skillName<i> on rec."""
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and str(tf.values[0]).strip():
            out[int(b[9:])] = str(tf.values[0])
    return out


def _level_slots(db, rec):
    """{slot} for every skillLevel<i> PRESENT on rec, blank name or not.

    Orphan `skillLevel` arrays with no `skillName` beside them are SV-donor
    residue and they are real: a name-only freeness test would silently
    overwrite one, which is a field change no record diff can explain.
    """
    out = set()
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if b.startswith('skillLevel') and b[10:].isdigit() and tf.values:
            out.add(int(b[10:]))
    return out


def _free_skillname_slot(db, rec, lo=1, hi=23):
    used = set(_skill_slots(db, rec)) | _level_slots(db, rec)
    for i in range(lo, hi + 1):
        if i not in used:
            return i
    return None


def _slot_of(db, rec, skill):
    want = _norm(skill)
    for i, p in _skill_slots(db, rec).items():
        if _norm(p) == want:
            return i
    return None


def _del_field(db, rec, name):
    """Remove a field slot entirely rather than blanking it to ''.

    A live reference blanked to the empty string is a loader hazard; an ABSENT
    field is the shipped way to say "this record does not use this". 86 of the
    131 CharFxPak records in the DB simply omit `particleEffectAttachPoints` and
    none carries an empty one, so absence - not emptiness - is precedented.
    """
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


# ── ASSET-LEVEL READERS (the layer four waves never looked at) ──────────────

def _mesh_names(mesh_ref):
    """(status, set(CASEFOLDED rig names)) out of a mesh binary: BOTH namespaces.

    status PASS / SKIP. SKIP means the archives are not reachable from this
    working tree; the caller ANNOUNCES that rather than counting it as a pass.

    ⚠️ b104 round 2, and the reason this delegates instead of scanning: round 1
    scanned `[A-Za-z][A-Za-z0-9_ ]{2,31}\\x00` here - NUL-terminated strings only.
    Bone-table names are NUL-terminated; ATTACHPOINT names are not, they live in a
    CRLF text block. So the reader could not see AttachPoint names AT ALL, and the
    round reported `SpecialHit01` "does not exist on SkeletonGrayBlack01New.msh"
    when it is declared there at byte 325003. A false measurement from a blind
    instrument then became a bolded warning in `docs/WILL_RULINGS.md`, i.e. design
    law for every future wave. `rig_names_of()` reads the bone table UNION the
    AttachPoint table, which is the set an attach value may legally resolve to.

    Casefolded because the shipped DB addresses these tables off-case
    (`Bone_spine01` vs the rig's `Bone_Spine01`, `Specialhit03` vs `SpecialHit03`).
    A case-sensitive gate would false-fail records that ship and work today, and a
    gate that cries wolf gets waived instead of fixed.
    """
    if _RIG_NAMES_OVERRIDE is not None:
        got = _RIG_NAMES_OVERRIDE.get(_norm(mesh_ref))
        return ('PASS', {str(n).lower() for n in got}) if got is not None \
            else ('SKIP', set())
    try:
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', set())
        data, _arc = mesh_assets.read_asset(mesh_ref)
        if not data:
            return ('SKIP', set())
        return ('PASS', {n.lower() for n in mesh_assets.rig_names_of(data)})
    except Exception:                                        # noqa: BLE001
        return ('SKIP', set())


def _demon_mesh_attach(db):
    """(status, attach_point) the demons' OWN mesh hangs their shroud on.

    The value we copy, derived from the binary rather than asserted. Round 1
    hard-coded a belief about this name and got it backwards; a derived value
    cannot go stale and cannot be wrong in a comment.
    """
    if _DEMON_ATTACH_OVERRIDE is not None:
        return ('PASS', _DEMON_ATTACH_OVERRIDE)
    mesh = _gv1(db, _MARAUDER, 'mesh')
    if not mesh:
        return ('FAIL', None)
    try:
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', None)
        data, _arc = mesh_assets.read_asset(str(mesh))
        if not data:
            return ('SKIP', None)
        want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
        for attach, entity in mesh_assets.embedded_fx_attachments_of(data):
            if entity and str(entity).replace('/', '\\').rsplit('\\', 1)[-1].lower() == want:
                return ('PASS', attach)
        return ('PASS', None)
    except Exception:                                        # noqa: BLE001
        return ('SKIP', None)


def _demon_fx_record(db):
    """(status, {field: value}) for the demons' own EffectEntity.

    It lives ONLY in the base-game `.arz` (it is not in the mod DB), so this reads
    the game install directly. Cheap: the parser is lazy-decode, ~0.4s for 74,013
    records. Used to prove our mirror really is a mirror, values included.
    """
    if _DEMON_FX_RECORD_OVERRIDE is not None:
        return ('PASS', dict(_DEMON_FX_RECORD_OVERRIDE))
    if db is not None and db.has_record(_DEMON_FX_REF):
        src = db                                  # already layered in: prefer it
    else:
        try:
            from pathlib import Path
            import mesh_assets
            from arz_patcher import ArzDatabase
            p = Path(mesh_assets.game_dir()) / 'Database' / 'database.arz'
            if not p.exists():
                return ('SKIP', {})
            src = _base_db_cached(ArzDatabase, p)
        except Exception:                                    # noqa: BLE001
            return ('SKIP', {})
    ff = src.get_fields(_DEMON_FX_REF)
    if ff is None:
        return ('SKIP', {})
    out = {}
    for k, tf in ff.items():
        vals = [str(v) for v in (tf.values or [])]
        out[k.split('###')[0]] = vals[0] if len(vals) == 1 else vals
    return ('PASS', out)


_BASE_DB_CACHE = {}


def _base_db_cached(cls, path):
    key = str(path)
    if key not in _BASE_DB_CACHE:
        import contextlib
        import io
        # the loader prints a progress banner; a gate's output is not the place
        with contextlib.redirect_stdout(io.StringIO()):
            _BASE_DB_CACHE[key] = cls.from_arz(path)
    return _BASE_DB_CACHE[key]


def _demon_embedded_fx(db):
    """(status, [effect refs]) compiled into the MARAUDERS' mesh.

    This is the provenance anchor for the whole module: the shroud Will pointed
    at is not a field, it is this CreateEntity block. Deriving it every build is
    what makes "the same one that his demon summon guys have" a checked claim.
    """
    if _DEMON_FX_OVERRIDE is not None:
        return ('PASS', list(_DEMON_FX_OVERRIDE))
    mesh = _gv1(db, _MARAUDER, 'mesh')
    if not mesh:
        return ('FAIL', [])
    try:
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', [])
        data, _arc = mesh_assets.read_asset(str(mesh))
        if not data:
            return ('SKIP', [])
        return ('PASS', mesh_assets.embedded_fx_of(data))
    except Exception:                                        # noqa: BLE001
        return ('SKIP', [])


def pfx_resolution(pfx=_DEMON_PFX):
    """A9-STYLE RENDER RESOLUTION: does the particle file actually SHIP?

    Resolution is not rendering (the A9/D5 lesson). The record chain can be
    perfect and he still smokes nothing if the `.pfx` is in no shipped archive.
    Walks the mod's staged `Resources` first, then the game install, which is the
    order the engine uses - this particular file is a BASE-GAME asset, so a
    mod-only search would report a false failure.
    """
    try:
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', 'no reachable .arc archives from this working tree')
        data, arcp = mesh_assets.read_asset(pfx)
        if not data:
            return ('FAIL', '%r is in NO shipped archive, so the shroud would '
                            'resolve to nothing and he would smoke nothing' % pfx)
        return ('PASS', '%s -> %s (%d bytes)' % (pfx, arcp, len(data)))
    except Exception as e:                                   # noqa: BLE001
        return ('SKIP', 'could not read the archives (%s)' % e)


# ── BUILD ───────────────────────────────────────────────────────────────────

def _build_fx(db):
    """A FIELD-FOR-FIELD MIRROR of the demons' own EffectEntity.

    The donor is a record SHELL, not a design. Round 1 cloned it, deleted the one
    field it knew was wrong (`boneList`) and shipped the rest - so `Anchored`,
    `emitterType` and `localOrientFix` rode along from a WEAPON-BONE-attached
    effect onto a body attach point, where their behaviour is unproven, while
    `ActorName` (which the demons' record does carry) was absent. "Byte-for-byte
    the demons' own particle" was then true of the `.pfx` and of nothing else.

    So: prune to exactly the demons' field set, then write exactly their values.
    verify() re-reads their record from the base `.arz` and fails on any drift.
    """
    _require(db, _FX_DONOR)
    if not db.has_record(_SHROUD_FX):
        db.clone_record(_FX_DONOR, _SHROUD_FX)
    want = dict(_DEMON_FX_FIELDS)
    for k in list(db.get_fields(_SHROUD_FX) or {}):
        base = k.split('###')[0]
        if base not in want:
            _del_field(db, _SHROUD_FX, base)
    for f, v in _DEMON_FX_FIELDS:
        db.set_field(_SHROUD_FX, f, v)
    db._modified.add(_SHROUD_FX)


def _build_pak(db):
    _require(db, _PAK_DONOR)
    if not db.has_record(_SHROUD_PAK):
        db.clone_record(_PAK_DONOR, _SHROUD_PAK)
    # value-only overrides on a cloned record (dtype preserved - the dtype lesson).
    db.set_field(_SHROUD_PAK, 'particleEffectNames', [_SHROUD_FX] * _PARTICLE_COUNT)
    if _ATTACH:
        db.set_field(_SHROUD_PAK, 'particleEffectAttachPoints', list(_ATTACH))
    else:
        _del_field(db, _SHROUD_PAK, 'particleEffectAttachPoints')
    db._modified.add(_SHROUD_PAK)


def _build_skill(db):
    _require(db, _SKILL_DONOR)
    if not db.has_record(_SHROUD):
        db.clone_record(_SKILL_DONOR, _SHROUD)
    db.set_field(_SHROUD, 'charFxPakSelfNames', _SHROUD_PAK)
    # the donor's purple weapon tint -> the inert (0,0,0) NO-TINT default (b83 model).
    for f in ('skillWeaponTintRed', 'skillWeaponTintGreen', 'skillWeaponTintBlue'):
        if db.get_field_value(_SHROUD, f) is not None:
            db.set_field(_SHROUD, f, 0.0)
    # `empusamerc_enchantment` residue: particleEffectAttachPoint1 = 'R Hand',
    # with no particleEffectName1 beside it. Inert, and it is the b98 round-4
    # "smoke off two fists" string sitting on the very record that fixes it - a
    # future reader trips over it and re-derives the wrong design. Placement on
    # this skill is the pak's job (`charFxPakSelfNames`) and nothing else's.
    for k in list(db.get_fields(_SHROUD) or {}):
        b = k.split('###')[0]
        if b.startswith('particleEffect'):
            _del_field(db, _SHROUD, b)
    db.set_field(_SHROUD, 'skillMaxLevel', 3)
    db.set_field(_SHROUD, 'FileDescription',
                 'SVC Enslaver: persistent black shadow shroud (visual only, no payload)')
    db._modified.add(_SHROUD)


def _always_on_controller(db, src):
    """An SVC-OWNED clone of `src` whose ONLY difference is BuffSelfBehavior.

    The shared originals are never written: `controller_skeleton_toxeus` also
    drives the Devourer, `um_toxeus_99`, `um_toxeus_21` and two dev dummies, and
    `controller_skelly_aggressive` drives 148 pets. Editing either in place to
    fix ONE champion's FX is the `genericbossorb_04` mistake (R-103's required
    check) with an AI field instead of a loot field.
    """
    head, _sep, base = str(src).rpartition('\\')
    dest = '%s\\%s%s' % (head, _CTRL_PREFIX, base)
    if not db.has_record(dest):
        if not db.clone_record(src, dest):
            raise SystemExit("[enslaver_shroud] could not clone controller %s" % src)
    db.set_field(dest, 'BuffSelfBehavior', _BUFF_TRIGGER)
    db._modified.add(dest)
    return dest


def _is_ours(ctrl):
    return str(ctrl).rsplit('\\', 1)[-1].lower().startswith(_CTRL_PREFIX)


def _pet_tiers(db):
    """Every Enslaver pet tier, READ from the summon skill's spawnObjects.

    b102 / R-102 second amendment. b98 wired the shroud to the monster only, so
    the three tiers Will actually summons never got it and he correctly said the
    request was "still not implemented". Deriving the tiers instead of listing
    them is what makes that failure unrepeatable: append a 4th pet to the summon
    and it is in scope for both apply() and verify() with no code change.
    """
    if not db.has_record(_ENSLAVER_SUMMON):
        return []
    out = []
    for x in _lst(db, _ENSLAVER_SUMMON, 'spawnObjects'):
        s = x.strip()
        if s and db.has_record(s) and s not in out:
            out.append(s)
    return out


def _spawned_by(db, rec):
    """Every creature record any SpawnPet skill in `rec`'s kit actually spawns.

    R-255. This is the leg b93 did not have. The wild boss raises his escorts
    through `svc_enslaver_summonmarauders`, and the SUMMONED Enslaver raises his
    pet-of-pet marauders through `svc_enslaver_petmarauders` - both are ordinary
    SpawnPet skills sitting in a kit slot / specialAttack field, so walking them
    finds the whole household without a list to go stale.
    """
    out = []
    cand = list(_skill_slots(db, rec).values())
    for f in _SPAWN_FIELDS:
        v = _gv1(db, rec, f)
        if v:
            cand.append(str(v))
    for sk in cand:
        if not sk or not db.has_record(sk):
            continue
        if not str(_gv1(db, sk, 'Class') or '').startswith('Skill_SpawnPet'):
            continue
        for x in _lst(db, sk, 'spawnObjects'):
            x = x.strip()
            if x and db.has_record(x) and x not in out:
                out.append(x)
    return out


def _family_closure(db):
    """W1: the WHOLE household, walked - boss + escorts + pet tiers + pet-of-pet.

    Seeds are the wild boss and whatever his soul-summon spawns; every seed then
    contributes what IT spawns, to a bounded depth. b93's roster stopped at the
    seeds, which is precisely why Will could summon a marauder that nobody had
    ever asked a question about.
    """
    seen, order = set(), []
    frontier = ([_ENSLAVER] if db.has_record(_ENSLAVER) else []) + _pet_tiers(db)
    depth = 0
    while frontier and depth <= _FAMILY_MAX_DEPTH:
        nxt = []
        for r in frontier:
            if r in seen:
                continue
            seen.add(r)
            order.append(r)
            nxt.extend(_spawned_by(db, r))
        frontier = [r for r in nxt if r not in seen]
        depth += 1
    return order


def _family_tags(db, members):
    """The name tags the walked family wears - derived, never listed.

    `_NAME_TAGS` stays as the pinned floor (it is what the b98/b102 rounds keyed
    on and the negtest still plants against it), but the sweep below is driven by
    what the family ACTUALLY wears, so a marauder tag joins the difficulty-clone
    hunt the moment a marauder joins the family.
    """
    tags = set(_NAME_TAGS)
    for r in members:
        d = _gv1(db, r, 'description')
        if d and str(d).strip():
            tags.add(str(d).lower())
    return tags


def _by_name_tag(db, tags=None):
    """W2: every Monster/Pet record described by one of the family's name tags.

    Catches a build-time DIFFICULTY CLONE, which the summon chain cannot see.
    Prefiltered on the .arz record-type index so this costs a slice of the DB
    rather than a full decode.
    """
    want = set(tags) if tags is not None else set(_NAME_TAGS)
    types = getattr(db, '_record_types', None) or {}
    out = []
    for n in db.record_names():
        t = types.get(n)
        if t and t not in ('Monster', 'Pet'):
            continue
        d = _gv1(db, n, 'description')
        if d and str(d).lower() in want:
            cls = str(_gv1(db, n, 'Class') or '')
            if cls.startswith('Monster') or cls.startswith('Pet'):
                out.append(n)
    return sorted(out)


def shroud_roster(db, w2=None):
    """The walked family + anything wearing one of the family's name tags."""
    w1 = _family_closure(db)
    if w2 is None:
        w2 = _by_name_tag(db, _family_tags(db, w1))
    seen, out = set(), []
    for r in list(w1) + list(w2):
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


# ── WHICH ROUTE DOES THIS MEMBER WEAR THE SHROUD BY? ────────────────────────

def _mesh_embeds_smoke(db, mesh_ref):
    """(status, bool) - does this rig carry the demons' own CreateEntity smoke?

    status PASS / SKIP. SKIP means the archives are unreachable from this working
    tree; the caller ANNOUNCES the downgrade and falls back to `_PINNED_SMOKE_RIGS`
    rather than counting an unread binary as a pass.
    """
    if not mesh_ref:
        return ('PASS', False)
    if _MESH_SMOKE_OVERRIDE is not None:
        got = _MESH_SMOKE_OVERRIDE.get(_norm(mesh_ref))
        return ('PASS', bool(got)) if got is not None else ('SKIP', False)
    want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
    try:
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', False)
        data, _arc = mesh_assets.read_asset(str(mesh_ref))
        if not data:
            return ('SKIP', False)
        for e in mesh_assets.embedded_fx_of(data):
            if str(e).replace('/', '\\').rsplit('\\', 1)[-1].lower() == want:
                return ('PASS', True)
        return ('PASS', False)
    except Exception:                                        # noqa: BLE001
        return ('SKIP', False)


def _has_mesh_route(db, rec):
    """(covered, downgraded) - MESH route, derived, pinned only on a loud SKIP."""
    mesh = _gv1(db, rec, 'mesh')
    st, hit = _mesh_embeds_smoke(db, mesh)
    if st == 'SKIP':
        return (_norm(mesh) in {_norm(m) for m in _PINNED_SMOKE_RIGS}, True)
    return (hit, False)


def _has_field_route(db, rec):
    """FIELD route: the shroud in BOTH declared always-on channels."""
    return all(_norm(_gv1(db, rec, f)) == _norm(_SHROUD) for f in _ALWAYS_ON_FIELDS)


def _dead_slots(db, rec):
    """{slot: skill} for every kit slot ABOVE the engine's declared ceiling.

    Reported for the whole family, but only OUR OWN shroud is ever removed from
    one (see `_retire_dead_shroud_slot`): another lane's skill parked up there is
    that lane's ruling to unwind, not this one's (RETIREMENT PROTOCOL).
    """
    return {i: s for i, s in _skill_slots(db, rec).items()
            if i > _ENGINE_SKILL_SLOT_MAX}


def _retire_dead_shroud_slot(db, rec):
    """Delete OUR shroud out of any kit slot above the engine ceiling.

    b93 wrote it to skillName19 (boss) / skillName18 (pets) - fields
    `MonsterSkillManager.tpl` never declares. Left in place they are worse than
    inert: the next reader greps the arz, sees `svc_enslaver_shroud` sitting in a
    skill slot, and concludes the shroud is wired. Only a slot whose value is OUR
    OWN record is touched; a neighbour's skill parked up there is reported by the
    gate and left exactly where its own lane put it.
    """
    gone = []
    for i, sk in sorted(_skill_slots(db, rec).items()):
        if i <= _ENGINE_SKILL_SLOT_MAX or _norm(sk) != _norm(_SHROUD):
            continue
        _del_field(db, rec, 'skillName%d' % i)
        _del_field(db, rec, 'skillLevel%d' % i)
        gone.append(i)
    if gone:
        db._modified.add(rec)
    return gone


def _wire_one(db, rec):
    """The two declared always-on channels + the always-on controller.

    NOT a kit slot any more. The shroud carries no payload (the VISUAL-ONLY
    invariant enforces that), so it wants a channel that fires without being
    chosen by combat AI, and `MonsterSkillManager` declares exactly two:
    `initialSkillName` (cast at spawn - ON from the first frame, the analogue of
    the demons' mesh FX) and `buffSelfSkillName` (re-applied by the controller,
    whose BuffSelfBehavior we already clone to WheneverPossible). Neither takes a
    level field - the template declares none for either - so there is no
    skillLevel to get wrong, which is one more way b93's shape could not work.
    """
    retired = _retire_dead_shroud_slot(db, rec)
    for f in _ALWAYS_ON_FIELDS:
        db.set_field(rec, f, _SHROUD)

    ctrl = _gv1(db, rec, 'controller')
    if not ctrl or not db.has_record(str(ctrl)):
        raise SystemExit(
            "[enslaver_shroud] %s has no resolvable controller (%r), so a "
            "self-buff shroud can never fire on it." % (rec, ctrl))
    ours = str(ctrl) if _is_ours(ctrl) else _always_on_controller(db, str(ctrl))
    db.set_field(rec, 'controller', ours)
    db._modified.add(rec)
    return retired, ours


def apply(db, tags):
    print("\n=== [enslaver_shroud] THE ENSLAVER'S BLACK SHADOW SHROUD "
          "(R-95 / R-102 / b104 R-250) ===")
    _require(db, _ENSLAVER)
    tiers = _pet_tiers(db)
    if not tiers:
        raise SystemExit(
            "[enslaver_shroud] %s spawns no resolvable pet, so the tier roster "
            "is EMPTY. That is the exact b98 failure this module exists to "
            "prevent (shroud on the monster, nothing on what Will summons) - "
            "stop rather than ship a monster-only shroud again." % _ENSLAVER_SUMMON)
    _build_fx(db)
    _build_pak(db)
    _build_skill(db)
    roster = shroud_roster(db)
    n_mesh = n_field = 0
    for rec in roster:
        mesh_ok, downgraded = _has_mesh_route(db, rec)
        if mesh_ok:
            # ALREADY smoking, the original way and the one Will confirmed by eye
            # ("the demons that he summons have the proper black shroud"). Adding
            # our emitter on top would double a shroud the demons wear once.
            n_mesh += 1
            print("  MESH   %-62s %s%s" % (rec, _gv1(db, rec, 'mesh'),
                                           '   [pinned: archives unreadable]'
                                           if downgraded else ''))
            continue
        retired, ctrl = _wire_one(db, rec)
        n_field += 1
        print("  FIELD  %-62s %s ctrl=%s%s"
              % (rec, '+'.join(_ALWAYS_ON_FIELDS), ctrl.rsplit('\\', 1)[-1],
                 '   [retired dead slot(s) %s]' % retired if retired else ''))
    print("  %d family surface(s): %d already smoke from their rig "
          "(%s compiled in), %d now carry the demons' own %s at their own attach "
          "point %s through %s - channels the skill manager actually declares "
          "(ceiling skillName%d), always on (BuffSelfBehavior=%s on SVC-owned "
          "controller clones); NO skill dropped; charFxPakRunningNames untouched."
          % (len(roster), n_mesh, _DEMON_FX_REF.rsplit('\\', 1)[-1], n_field,
             _DEMON_PFX.rsplit('\\', 1)[-1], _ATTACH[0],
             '+'.join(_ALWAYS_ON_FIELDS), _ENGINE_SKILL_SLOT_MAX, _BUFF_TRIGGER))
    print("=== [enslaver_shroud] done (verify() runs post-finalization) ===\n")
    return tags


# ── GATE ────────────────────────────────────────────────────────────────────

def verify(db, tags=None):
    problems = []
    notes = []

    # ── the skill ───────────────────────────────────────────────────────────
    if not db.has_record(_SHROUD):
        problems.append("shroud skill missing: %s" % _SHROUD)
    else:
        if _gv1(db, _SHROUD, 'Class') != 'Skill_BuffSelfToggled':
            problems.append("shroud Class=%r != Skill_BuffSelfToggled"
                            % _gv1(db, _SHROUD, 'Class'))
        if _norm(_gv1(db, _SHROUD, 'charFxPakSelfNames')) != _norm(_SHROUD_PAK):
            problems.append("shroud charFxPakSelfNames=%r != %s"
                            % (_gv1(db, _SHROUD, 'charFxPakSelfNames'), _SHROUD_PAK))
        # VISUAL-ONLY invariant: a shroud must never quietly become a stat buff.
        payload = []
        for k, tf in (db.get_fields(_SHROUD) or {}).items():
            b = k.split('###')[0]
            if not (b.startswith('offensive') or b.startswith('defensive')
                    or b.startswith('character')):
                continue
            for v in (tf.values or []):
                if isinstance(v, (int, float)) and v:
                    payload.append(b)
                    break
        if payload:
            problems.append(
                "VISUAL-ONLY: the shroud picked up a combat payload (%s). It is a "
                "cosmetic buff; a stat change here silently rebalances a boss."
                % sorted(set(payload))[:6])
        for f in ('skillWeaponTintRed', 'skillWeaponTintGreen', 'skillWeaponTintBlue'):
            t = _gv1(db, _SHROUD, f)
            if t not in (None, 0, 0.0):
                problems.append("shroud %s=%r (must stay the inert 0 NO-TINT default; "
                                "the donor's purple tint would recolour his weapon)"
                                % (f, t))
        stray = sorted({k.split('###')[0] for k in (db.get_fields(_SHROUD) or {})
                        if k.split('###')[0].startswith('particleEffect')})
        if stray:
            problems.append(
                "DONOR RESIDUE: the shroud skill still carries %r from "
                "`empusamerc_enchantment`. Placement on this skill belongs to the "
                "pak named in charFxPakSelfNames and to nothing else; an orphan "
                "'R Hand' attach on the record that FIXES the two-fists defect is "
                "how a future reader re-derives the wrong design." % stray)

    # ── the EffectEntity: the demons' particle, off the weapon bones ────────
    if not db.has_record(_SHROUD_FX):
        problems.append("shroud EffectEntity missing: %s" % _SHROUD_FX)
    else:
        if str(_gv1(db, _SHROUD_FX, 'Class') or '') != 'EffectEntity':
            problems.append("%s Class=%r != EffectEntity"
                            % (_SHROUD_FX, _gv1(db, _SHROUD_FX, 'Class')))
        eff = str(_gv1(db, _SHROUD_FX, 'effectFile') or '')
        if _norm(eff) != _norm(_DEMON_PFX):
            problems.append(
                "ASSET PROVENANCE: %s plays %r, expected %r - the exact particle "
                "file the demons' own mesh plays. Will asked for 'the same one "
                "that his demon summon guys have'; a different .pfx is a different "
                "shroud, and no colour check in this file would notice."
                % (_SHROUD_FX, eff, _DEMON_PFX))
        bl = _lst(db, _SHROUD_FX, 'boneList')
        if bl:
            problems.append(
                "SHAPE: %s carries boneList=%r. The donor pinned this smoke to "
                "Bone_R_Weapon/Bone_L_Weapon, which is why every previous version "
                "of this shroud came off his FISTS instead of from around him. A "
                "body shroud must carry no boneList and be placed by the pak's "
                "attach point." % (_SHROUD_FX, bl))

        # ── MIRROR: the WHOLE record, not just the .pfx ────────────────────
        ours = {}
        for k, tf in (db.get_fields(_SHROUD_FX) or {}).items():
            vals = [str(x) for x in (tf.values or [])]
            ours[k.split('###')[0]] = vals[0] if len(vals) == 1 else vals
        st, theirs = _demon_fx_record(db)
        if st == 'SKIP':
            notes.append("DEMON EFFECTENTITY MIRROR DOWNGRADED (not a pass): the "
                         "base-game .arz is not reachable, so %s could not be "
                         "re-derived; the pinned field set was used instead"
                         % _DEMON_FX_REF)
            theirs = {f: v for f, v in _DEMON_FX_FIELDS}
        elif not theirs:
            problems.append("the demons' own EffectEntity %s could not be read, so "
                            "the mirror claim cannot be checked" % _DEMON_FX_REF)
        if theirs:
            pinned = {f: v for f, v in _DEMON_FX_FIELDS}
            if st == 'PASS' and {k: str(v) for k, v in theirs.items()} != pinned:
                problems.append(
                    "PROVENANCE DRIFT: the demons' own %s now reads %r but this "
                    "module is pinned to %r. Re-derive rather than letting the "
                    "mirror silently stop mirroring." % (_DEMON_FX_REF, theirs, pinned))
            extra = sorted(set(ours) - set(theirs))
            missing = sorted(set(theirs) - set(ours))
            if extra or missing:
                problems.append(
                    "MIRROR: %s is not a field-for-field copy of the demons' own "
                    "EffectEntity - extra=%r missing=%r. Round 1 shipped donor "
                    "residue here (Anchored/emitterType/localOrientFix, all off a "
                    "WEAPON-BONE-attached effect, unproven on a body attach point) "
                    "and claimed 'byte-for-byte the demons' own particle' on the "
                    "strength of the .pfx alone." % (_SHROUD_FX, extra, missing))
            diff = {f: (ours.get(f), theirs[f]) for f in theirs
                    if f in ours and _norm(ours[f]) != _norm(theirs[f])}
            if diff:
                problems.append(
                    "MIRROR: %s disagrees with the demons' own record on %r "
                    "(ours, theirs). Will asked for 'the same one that his demon "
                    "summon guys have'." % (_SHROUD_FX, diff))

    # ── the pak: one body emitter, on a bone that exists on his rig ─────────
    if not db.has_record(_SHROUD_PAK):
        problems.append("shroud CharFxPak missing: %s" % _SHROUD_PAK)
    else:
        names = _lst(db, _SHROUD_PAK, 'particleEffectNames')
        if not names or any(_norm(n) != _norm(_SHROUD_FX) for n in names):
            problems.append("shroud pak particleEffectNames=%r, expected %r"
                            % (names, [_SHROUD_FX]))
        if len(names) != _PARTICLE_COUNT:
            problems.append(
                "shroud pak has %d particleEffectNames entr(ies), expected %d - the "
                "demons carry exactly ONE CreateEntity smoke, so one emitter is the "
                "faithful match and duplicates would just thicken it."
                % (len(names), _PARTICLE_COUNT))
        ap = _lst(db, _SHROUD_PAK, 'particleEffectAttachPoints')
        if ap != _ATTACH:
            problems.append(
                "SHAPE: shroud pak particleEffectAttachPoints=%r, expected %r - the "
                "attach point the demons' OWN mesh hangs this smoke on, which his "
                "rig declares too, with a byte-identical block. 'R Hand'/'L Hand' "
                "is the b98 round-4 defect (smoke off two fists); %r is the helper "
                "the demons have and he does NOT, so it would render nothing at all."
                % (ap, _ATTACH, _DEMON_ONLY_ATTACH))

    # ── THE ATTACH POINT IS THE DEMONS' OWN, DERIVED FROM THEIR MESH ────────
    st, demon_attach = _demon_mesh_attach(db)
    if st == 'FAIL':
        problems.append("the marauders (%s) have no mesh, so the attach point we "
                        "copy cannot be derived at all" % _MARAUDER)
    elif st == 'SKIP':
        notes.append("DEMON-ATTACH PARITY DOWNGRADED (not a pass): the .arc archives "
                     "are not reachable, so the demons' own CreateEntity attach "
                     "could not be re-derived; pinned %r was used" % _DEMON_MESH_ATTACH)
    elif not demon_attach:
        problems.append(
            "the marauders' mesh embeds %s with no readable attach point, so 'the "
            "same one that his demon summon guys have' cannot be matched by "
            "placement." % _DEMON_FX_REF)
    else:
        if demon_attach.lower() != _DEMON_MESH_ATTACH.lower():
            problems.append(
                "PROVENANCE DRIFT: the demons hang their shroud at %r but this "
                "module is pinned to %r. Re-derive; a pinned belief about this name "
                "is exactly what round 1 got backwards."
                % (demon_attach, _DEMON_MESH_ATTACH))
        if [a.lower() for a in _lst(db, _SHROUD_PAK, 'particleEffectAttachPoints')] \
                != [demon_attach.lower()]:
            problems.append(
                "SHAPE: the demons hang this smoke at %r; our pak attaches it at %r. "
                "Same particle at a different place is a different shroud."
                % (demon_attach,
                   _lst(db, _SHROUD_PAK, 'particleEffectAttachPoints')))

    # ── PROVENANCE, DERIVED FROM THE DEMONS' MESH (not from a comment) ──────
    st, refs = _demon_embedded_fx(db)
    if st == 'FAIL':
        problems.append("the marauders (%s) have no mesh, so the shroud's "
                        "provenance cannot be derived at all" % _MARAUDER)
    elif st == 'SKIP':
        notes.append("DEMON-MESH PROVENANCE DOWNGRADED (not a pass): the .arc "
                     "archives are not reachable from this working tree, so the "
                     "marauders' embedded shroud could not be re-derived")
    else:
        stems = [str(r).replace('/', '\\').rsplit('\\', 1)[-1].lower() for r in refs]
        want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
        if want not in stems:
            problems.append(
                "PROVENANCE: the marauders' mesh no longer embeds %s (it embeds "
                "%r). The whole premise of this module is that THAT is the shroud "
                "Will pointed at; re-derive it rather than letting the two drift "
                "apart." % (want, refs))
        pfx_stem = _DEMON_PFX.rsplit('\\', 1)[-1].lower()
        if not pfx_stem.startswith(want[:-4].rstrip('0123456789_')):
            problems.append(
                "PROVENANCE: the shroud plays %r, which is not a file of the "
                "demons' %r family." % (_DEMON_PFX, want))

    # ── A9 RENDER RESOLUTION: resolution is not rendering ──────────────────
    st, detail = pfx_resolution()
    if st == 'FAIL':
        problems.append("A9 RENDER RESOLUTION: %s" % detail)
    elif st == 'SKIP':
        notes.append("A9 render resolution DOWNGRADED (not a pass): %s" % detail)
    else:
        notes.append("A9 render resolution PASS: %s" % detail)

    # ── ROSTER: two witnesses, which must agree ────────────────────────────
    if not db.has_record(_ENSLAVER):
        problems.append("Enslaver missing: %s" % _ENSLAVER)
    if not db.has_record(_ENSLAVER_SUMMON):
        problems.append(
            "the Enslaver summon skill is missing (%s), so the pet-tier roster "
            "cannot be derived and a tier could be silently skipped"
            % _ENSLAVER_SUMMON)
    tiers = _pet_tiers(db)
    if db.has_record(_ENSLAVER_SUMMON) and not tiers:
        problems.append(
            "%s spawns NO resolvable pet: the derived tier roster is EMPTY. b98 "
            "shipped a monster-only shroud exactly this way and Will reported it "
            "as never implemented." % _ENSLAVER_SUMMON)
    # ── R-255: THE FAMILY, WALKED - boss + escorts + pet tiers + pet-of-pet ──
    w1_list = _family_closure(db)
    w1 = set(w1_list)
    escorts = _spawned_by(db, _ENSLAVER) if db.has_record(_ENSLAVER) else []
    if db.has_record(_ENSLAVER) and not escorts:
        problems.append(
            "FAMILY: the wild Enslaver spawns NO resolvable creature, so his "
            "ESCORTS are invisible to this gate. b93 never looked at them at all "
            "and shipped 'the family has the family FX' as an unchecked claim.")
    pet_of_pet = []
    for t in tiers:
        pet_of_pet.extend(r for r in _spawned_by(db, t) if r not in pet_of_pet)
    if tiers and not pet_of_pet:
        problems.append(
            "FAMILY: no pet tier spawns a pet-of-pet. The summoned Enslaver raises "
            "marauders through %s; an empty sub-roster means a family member Will "
            "can see in front of him is outside every check."
            % r'svc_enslaver_petmarauders')
    w2_list = _by_name_tag(db, _family_tags(db, w1_list))
    if w1 and set(w2_list) - w1:
        problems.append(
            "ROSTER WITNESS DISAGREEMENT: %r carr(y) a family name tag but are "
            "not reachable from the anchor + summon + spawn walk. A difficulty "
            "clone or a new tier has appeared (the Hunt has exactly such a clone, "
            "um_toxeus_hunt_l_99) and would ship with no shroud."
            % sorted(set(w2_list) - w1))

    roster = shroud_roster(db, w2=w2_list)
    ours_carriers = set()
    field_route = set()
    for rec in roster:
        is_pet = rec != _ENSLAVER
        tag = ' (PET TIER)' if is_pet else ' (MONSTER)'

        # ── FAMILY FX PARITY: every member, by MESH or by FIELD ────────────
        mesh_ok, downgraded = _has_mesh_route(db, rec)
        field_ok = _has_field_route(db, rec)
        if downgraded:
            notes.append("MESH ROUTE DOWNGRADED (not a pass) for %s: the .arc "
                         "archives are unreachable, so %r was resolved against the "
                         "pinned smoke-rig list"
                         % (rec.rsplit('\\', 1)[-1], _gv1(db, rec, 'mesh')))
        if not (mesh_ok or field_ok):
            missing = [f for f in _ALWAYS_ON_FIELDS
                       if _norm(_gv1(db, rec, f)) != _norm(_SHROUD)]
            problems.append(
                "FAMILY FX PARITY: %s%s wears NEITHER route. Its rig %r does not "
                "embed the demons' %s, and it is missing the shroud on %r. Every "
                "member of this household smokes - the wild boss, his escorts, the "
                "pet tiers a soul summons and the marauders those pets raise - so a "
                "member without the family FX is the bug Will has now filed four "
                "times." % (rec, tag, _gv1(db, rec, 'mesh'),
                            _DEMON_FX_REF.rsplit('\\', 1)[-1], missing))
        if field_ok:
            field_route.add(rec)

        # ── THE SLOT CEILING: never park the shroud where nothing reads it ──
        slot = _slot_of(db, rec, _SHROUD)
        if slot is not None and slot > _ENGINE_SKILL_SLOT_MAX:
            problems.append(
                "DEAD SLOT: %s carries the shroud at skillName%d. "
                "MonsterSkillManager.tpl declares skillName1..%d and NOTHING above "
                "it, and across 74,013 base-game records no Monster or Pet ever "
                "uses a higher slot - so that field is read by nobody. This is "
                "exactly what b93 shipped (skillName19 on the boss, skillName18 on "
                "every pet tier) and exactly why the smoke never appeared."
                % (rec, slot, _ENGINE_SKILL_SLOT_MAX))
        dead = _dead_slots(db, rec)
        if dead:
            notes.append(
                "SLOT-CEILING DEBT on %s: skill(s) %r sit above skillName%d and are "
                "read by nobody. Not this lane's to unwind (RETIREMENT PROTOCOL) - "
                "registered as BL-R255-DEBT-1."
                % (rec.rsplit('\\', 1)[-1],
                   {i: s.rsplit('\\', 1)[-1] for i, s in sorted(dead.items())},
                   _ENGINE_SKILL_SLOT_MAX))

        # A MESH-route member owes nothing below: its smoke is compiled into the
        # rig, so it needs no AI, no controller clone and no field of ours. The
        # legs after this block (running FX, CRASH LAW) still cover everybody.
        if field_ok:
            # ── ALWAYS ON, and provably visual-only ────────────────────────
            ctrl = _gv1(db, rec, 'controller')
            if not ctrl or not db.has_record(str(ctrl)):
                problems.append("%s has no resolvable controller (%r), so its "
                                "self-buff shroud can never fire" % (rec, ctrl))
            else:
                ours_carriers.add(str(ctrl))
                if not _is_ours(ctrl):
                    problems.append(
                        "%s%s still runs the SHARED controller %s. Either the shroud "
                        "is combat-gated on it (the WhenEnemyIsSeen default - OFF "
                        "while Will stands looking at the summoned pet, which is how "
                        "he inspects it), or a shared AI record was edited in place "
                        "and 148 other pets moved with it." % (rec, tag, ctrl))
                trig = str(_gv1(db, str(ctrl), 'BuffSelfBehavior'))
                if trig != _BUFF_TRIGGER:
                    problems.append(
                        "%s: controller %s has BuffSelfBehavior=%r, expected %r. A "
                        "toggled shroud the AI only fires in combat is not a shroud "
                        "he wears; that is why this request has now been filed three "
                        "times." % (rec, ctrl, trig, _BUFF_TRIGGER))
            # the AI flip is only safe while the shroud is the ONLY self-buff here.
            # Both declared always-on channels count as "the shroud", not as rivals.
            others = []
            probes = list(_skill_slots(db, rec).items())
            probes += [(f, _gv1(db, rec, f)) for f in _ALWAYS_ON_FIELDS]
            for i, sk in probes:
                if not sk or _norm(sk) == _norm(_SHROUD) or not db.has_record(str(sk)):
                    continue
                if 'BuffSelf' in str(_gv1(db, str(sk), 'Class') or ''):
                    others.append((i, sk))
            if others:
                problems.append(
                    "AI SIDE EFFECT: %s carries other Skill_BuffSelf* skill(s) %r. "
                    "BuffSelfBehavior=%s makes the AI fire ALL of them out of "
                    "combat, so this lane's visual-only claim no longer holds - "
                    "split the trigger or get Will's call before shipping."
                    % (rec, others, _BUFF_TRIGGER))

            # ── RIG: an attach point missing from the rig renders NOTHING ──
            mesh = _gv1(db, rec, 'mesh')
            if not mesh:
                problems.append("%s has no mesh field, so the shroud's attach point "
                                "cannot be checked against its rig" % rec)
            else:
                st, names = _mesh_names(str(mesh))
                if st == 'SKIP':
                    notes.append("RIG ATTACH DOWNGRADED (not a pass) for %s: %s could "
                                 "not be read" % (rec.rsplit('\\', 1)[-1], mesh))
                else:
                    # names is CASEFOLDED and spans BOTH namespaces (bone table +
                    # AttachPoint table). Round 1 resolved this against the bone
                    # table alone, which cannot see the names this field mostly uses.
                    missing = [a for a in _lst(db, _SHROUD_PAK,
                                               'particleEffectAttachPoints')
                               if a.lower() not in names]
                    if missing:
                        problems.append(
                            "RIG ATTACH: %s wears %s, which declares no %r in either "
                            "its bone table or its AttachPoint table. An FX aimed at "
                            "an attach point the mesh does not carry renders NOTHING, "
                            "silently - the trap R-95 wrote down. (%r is exactly such "
                            "a name here: the demons declare it, this rig does not.)"
                            % (rec, mesh, missing, _DEMON_ONLY_ATTACH))

        # ── ADD, never take away: the running channel he shares with them ──
        run = _gv1(db, rec, 'charFxPakRunningNames')
        if _norm(run) != _norm(_SHADOWCLOAK_PAK):
            problems.append(
                "%s: charFxPakRunningNames is %r, expected %s. This module ADDS a "
                "persistent channel; it must never take away the running one that "
                "matches his marauders." % (rec, run, _SHADOWCLOAK_PAK))

        # ── CRASH LAW (the build28 trap) over the WHOLE kit ────────────────
        for i, sk in sorted(_skill_slots(db, rec).items()):
            if not db.has_record(sk):
                continue
            if not str(_gv1(db, sk, 'Class') or '').startswith('Skill_SpawnPet'):
                continue
            bad = sorted({k.split('###')[0] for k in (db.get_fields(sk) or {})
                          if k.split('###')[0].lower().startswith('charfxpak')})
            if bad:
                problems.append(
                    "CRASH LAW: %s skillName%d -> %s is a SpawnPet skill carrying "
                    "%r. FX belong on MONSTER-RECORD fields or a "
                    "Skill_BuffSelfToggled, NEVER a charFxPak on a SpawnPet skill - "
                    "that is the build28 crash trap." % (rec, i, sk, bad))

    # ── SHARED-RECORD LAW: our clones may not leak onto anything else ───────
    for n in db.record_names():
        c = _gv1(db, n, 'controller')
        if c and _is_ours(c) and n not in set(roster):
            problems.append(
                "SHARED-RECORD LAW: %s (outside the Enslaver roster) now runs the "
                "always-on controller %s. This lane's AI change must reach the "
                "Enslaver family and nothing else." % (n, c))

    # the running channel's provenance must still hold on the demons themselves
    if db.has_record(_MARAUDER):
        if _norm(_gv1(db, _MARAUDER, 'charFxPakRunningNames')) != _norm(_SHADOWCLOAK_PAK):
            problems.append("the marauders lost their shadowcloak running FX (%r)"
                            % _gv1(db, _MARAUDER, 'charFxPakRunningNames'))
    else:
        problems.append("the shroud's provenance record is missing: %s" % _MARAUDER)

    for n in notes:
        print("  [enslaver_shroud] %s" % n)
    if problems:
        for p in problems:
            print("  ENSLAVER-SHROUD OFFENDER: %s" % p)
        raise SystemExit("enslaver_shroud.verify FAILED: %d problem(s)" % len(problems))
    print("  [enslaver_shroud].verify OK: the WHOLE Enslaver household smokes - all %d "
          "member(s) walked (the wild boss, his %d escort(s), the %d pet tier(s) his "
          "soul summons and the %d pet-of-pet marauder(s) those raise), each covered by "
          "one of the two proven routes: %d wear it compiled into their rig (%s, the "
          "original) and %d carry a field-for-field mirror of the demons' own "
          "EffectEntity (%s) at their OWN attach point %r through %s - channels "
          "MonsterSkillManager actually declares (ceiling skillName%d; b93's "
          "skillName18/19 were read by nobody) - fired by SVC-owned controller clones "
          "at BuffSelfBehavior=%s so it is ON out of combat, visual-only (no payload, "
          "no tint, no donor residue, the only self-buff in any kit). Running FX "
          "untouched everywhere; no charFxPak on any SpawnPet skill. "
          "WHAT IS STILL NOT CLAIMED: how it READS in game (BL-R250-DEBT-1)."
          % (len(roster), len(escorts), len(tiers), len(pet_of_pet),
             len(roster) - len(field_route), _DEMON_FX_REF.rsplit('\\', 1)[-1],
             len(field_route), _DEMON_PFX.rsplit('\\', 1)[-1], _ATTACH[0],
             '+'.join(_ALWAYS_ON_FIELDS), _ENGINE_SKILL_SLOT_MAX, _BUFF_TRIGGER))
    return tags


# ── NEGATIVE TEST ───────────────────────────────────────────────────────────

def _negtest():
    r"""py tools/patches/enslaver_shroud.py --negtest

    ⚠️ THE STUB'S RIG TABLE IS THE TEST'S OWN PREMISE, AND ROUND 1 PLANTED A FALSE
    ONE. It injected `{SkeletonGrayBlack01New: {Bone_Waist, Bone_Spine02, ...}}`,
    i.e. it asserted that his rig has no `SpecialHit01`, then "caught" a plant that
    aimed the shroud there - certifying the module's own error instead of detecting
    it. The 24/24 was real for the other 23 plants and circular for that one.

    The table below is now the MEASURED content of both binaries, and `--selftest`
    re-measures the two facts it rests on against the real archives, so the stub can
    never again quietly disagree with the assets it stands in for.
    """
    global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE, _DEMON_ATTACH_OVERRIDE
    global _DEMON_FX_RECORD_OVERRIDE, _MESH_SMOKE_OVERRIDE
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = v

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
            f = self.d.get(n)
            if f is None:
                return None
            return OrderedDict((k, _TF(v)) for k, v in f.items())

        def get_field_value(self, n, f):
            return self.d.get(n, {}).get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

    _MESH_M = r'Creatures\Monster\Skeleton\SkeletonGrayBlack01New.msh'
    _MESH_D = r'Creatures\Monster\ShadowStalker\ShadowStalker.msh'
    # MEASURED, both binaries, both namespaces (`--selftest` re-checks these two
    # rows against the real archives). The rigs carry the IDENTICAL SpecialHit0X
    # set; the demons' ONLY extra helper is `Smoke02`.
    _AP_COMMON = {'Head', 'HeadEffect', 'L Hand', 'Prey_Effect', 'R Hand',
                  'SpecialHit01', 'SpecialHit02', 'SpecialHit03', 'SpecialHit04',
                  'Target', 'Upper Body'}
    _BONES = {'Bone_Root', 'Bone_Waist', 'Bone_Spine01', 'Bone_Spine02', 'Bone_Head',
              'Bone_R_Weapon', 'Bone_L_Weapon'}
    _RIG = {_norm(_MESH_M): _AP_COMMON | _BONES,
            _norm(_MESH_D): _AP_COMMON | _BONES | {_DEMON_ONLY_ATTACH}}
    _PETS = [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
             for i in (1, 2, 3)]
    # R-255: the half of the household b93 never looked at - the pet-of-pet
    # marauders the SUMMONED Enslaver raises, which is what Will has in front of
    # him when he says "summoned pets ... still do not have the black smoke".
    _MPETS = [r'records\skills\soulskills\pets\enslaver_marauder_%d.dbr' % i
              for i in (1, 2, 3)]
    _CTRL_M = r'records\controllers\monster\svc_alwayson_controller_skeleton_toxeus.dbr'
    _CTRL_P = (r'records\skills\spirit\drxpet\drxpet_controllers'
               r'\svc_alwayson_controller_skelly_aggressive.dbr')
    _SHARED_P = (r'records\skills\spirit\drxpet\drxpet_controllers'
                 r'\controller_skelly_aggressive.dbr')
    _SPAWN = r'records\skills\boss skills\svc_enslaver_summonmarauders.dbr'
    _SUBSPAWN = r'records\skills\soulskills\svc_enslaver_petmarauders.dbr'

    def _base():
        db = _Stub()
        db.d[_SHADOWCLOAK_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX]}
        db.d[_SHADOWCLOAK_FX] = {'Class': ['EffectEntity'],
                                 'effectFile': [r'DRXeffects\shadowcloakrunning.pfx'],
                                 'boneList': ['Bone_R_Weapon', 'Bone_L_Weapon']}
        db.d[_SHROUD_FX] = {f: [v] for f, v in _DEMON_FX_FIELDS}
        db.d[_SHROUD_PAK] = {'particleEffectNames': [_SHROUD_FX] * _PARTICLE_COUNT,
                             'particleEffectAttachPoints': list(_ATTACH)}
        db.d[_SHROUD] = {'Class': ['Skill_BuffSelfToggled'],
                         'charFxPakSelfNames': [_SHROUD_PAK],
                         'skillWeaponTintRed': [0.0], 'skillWeaponTintGreen': [0.0],
                         'skillWeaponTintBlue': [0.0]}
        db.d[_MARAUDER] = {'Class': ['Monster'],
                           'description': ['tagSVCMonsterEnslaverMarauder'],
                           'mesh': [_MESH_D],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_SPAWN] = {'Class': ['Skill_SpawnPetMonster'], 'spawnObjects': [_MARAUDER]}
        db.d[_SUBSPAWN] = {'Class': ['Skill_SpawnPet'], 'spawnObjects': list(_MPETS)}
        db.d[_CTRL_M] = {'BuffSelfBehavior': [_BUFF_TRIGGER]}
        db.d[_CTRL_P] = {'BuffSelfBehavior': [_BUFF_TRIGGER]}
        db.d[_SHARED_P] = {'BuffSelfBehavior': ['WhenEnemyIsSeen']}
        db.d[_ENSLAVER] = {'Class': ['Monster'], 'description': ['tagSVCMonsterEnslaver'],
                           'mesh': [_MESH_M], 'controller': [_CTRL_M],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                           'skillName8': [_SPAWN],
                           'initialSkillName': [_SHROUD],
                           'buffSelfSkillName': [_SHROUD]}
        db.d[_ENSLAVER_SUMMON] = {'Class': ['Skill_SpawnPet'], 'spawnObjects': list(_PETS)}
        for p in _PETS:
            db.d[p] = {'Class': ['Pet'], 'description': ['tagSVCMonsterEnslaverPet'],
                       'mesh': [_MESH_M], 'controller': [_CTRL_P],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                       'skillName9': [_SUBSPAWN],
                       'initialSkillName': [_SHROUD],
                       'buffSelfSkillName': [_SHROUD]}
        # the pet-of-pet marauders: covered by the MESH route (ShadowStalker.msh
        # carries the shroud compiled in), so they carry no field of ours at all
        for p in _MPETS:
            db.d[p] = {'Class': ['Pet'],
                       'description': ['tagSVCMonsterEnslaverMarauderPet'],
                       'mesh': [_MESH_D], 'controller': [_SHARED_P],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        # a bystander that must NOT move with the Enslaver's AI change
        db.d[r'records\skills\soulskills\pets\boneash_1.dbr'] = {
            'Class': ['Pet'], 'controller': [_SHARED_P]}
        return db

    def _clear_always_on(db, rec):
        for f in _ALWAYS_ON_FIELDS:
            db.d[rec].pop(f, None)

    plants = [
        # ── R-255: the reason this was filed a FOURTH time ──────────────────
        ('THE R-255 DEFECT: the shroud goes back into a slot no skill manager '
         'reads (skillName19 boss / skillName18 pets, exactly what b93 shipped)',
         lambda db: [(_clear_always_on(db, r),
                      db.d[r].__setitem__('skillName19' if r == _ENSLAVER
                                          else 'skillName18', [_SHROUD]))
                     for r in [_ENSLAVER] + _PETS]),
        ('the shroud is parked in a dead slot ON TOP of the working channels, so '
         'a future reader re-derives the b93 shape as the one that worked',
         lambda db: db.d[_PETS[0]].__setitem__('skillName18', [_SHROUD])),
        ('a pet tier loses initialSkillName (the spawn-cast leg)',
         lambda db: db.d[_PETS[1]].pop('initialSkillName')),
        ('a pet tier loses buffSelfSkillName (the re-application leg)',
         lambda db: db.d[_PETS[2]].pop('buffSelfSkillName')),
        ('STRIP ONE PET: a pet-of-pet marauder is moved onto the FX-free rig and '
         'given no field route, so one family member wears no family FX',
         lambda db: db.d[_MPETS[1]].__setitem__('mesh', [_MESH_M])),
        ('the pet-of-pet sub-summon loses its spawnObjects, so the marauders Will '
         'actually sees fall out of the roster in silence',
         lambda db: db.d[_SUBSPAWN].__setitem__('spawnObjects', [])),
        ('the wild boss stops spawning escorts, so his half of the family is gone',
         lambda db: db.d[_SPAWN].__setitem__('spawnObjects', [])),
        ('a NEW pet-of-pet tier is raised and never gets either route',
         lambda db: (db.d.__setitem__(
             r'records\skills\soulskills\pets\enslaver_marauder_4.dbr',
             {'Class': ['Pet'],
              'description': ['tagSVCMonsterEnslaverMarauderPet'],
              'mesh': [_MESH_M], 'controller': [_SHARED_P],
              'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}),
             db.d[_SUBSPAWN].__setitem__(
                 'spawnObjects',
                 _MPETS + [r'records\skills\soulskills\pets\enslaver_marauder_4.dbr']))),
        ('a difficulty CLONE of a MARAUDER appears wearing the family name tag',
         lambda db: db.d.__setitem__(
             r'records\creature\monster\shadowstalker\um_enslaver_marauder_l_99.dbr',
             {'Class': ['Monster'], 'description': ['tagSVCMonsterEnslaverMarauder'],
              'mesh': [_MESH_D], 'charFxPakRunningNames': [_SHADOWCLOAK_PAK]})),
        ('the marauders rig stops carrying the compiled-in smoke, so the MESH '
         'route silently stops covering every marauder in the household',
         lambda db: _set_mesh_smoke({_norm(_MESH_M): False, _norm(_MESH_D): False})),
        # ── b104: the reason this was filed a third time ────────────────────
        ('THE b104 DEFECT: the shroud is combat-gated again (WhenEnemyIsSeen)',
         lambda db: db.d[_CTRL_P].__setitem__('BuffSelfBehavior', ['WhenEnemyIsSeen'])),
        ('a pet is left on the SHARED controller, so its shroud is combat-gated',
         lambda db: db.d[_PETS[0]].__setitem__('controller', [_SHARED_P])),
        ('the shared pet controller is edited IN PLACE (148 other pets move with it)',
         lambda db: [db.d[p].__setitem__('controller', [_SHARED_P]) for p in _PETS]
         + [db.d[_SHARED_P].__setitem__('BuffSelfBehavior', [_BUFF_TRIGGER])]),
        ('our always-on controller leaks onto a record outside the roster',
         lambda db: db.d[r'records\skills\soulskills\pets\boneash_1.dbr']
         .__setitem__('controller', [_CTRL_P])),
        ('a real self-buff joins the kit, so the AI flip stops being visual-only',
         lambda db: (db.d.__setitem__(r'records\skills\x\rage.dbr',
                                      {'Class': ['Skill_BuffSelfDuration']}),
                     db.d[_ENSLAVER].__setitem__('skillName20',
                                                 [r'records\skills\x\rage.dbr']))),
        # ── b104 round 2: the attach-point class, planted on TRUE rigs ──────
        ('the shroud is aimed at Smoke02 - a helper the DEMONS have and he does not',
         lambda db: db.d[_SHROUD_PAK].__setitem__('particleEffectAttachPoints',
                                                  [_DEMON_ONLY_ATTACH])),
        ('the shroud drifts off the demons OWN attach point (round 1s Bone_Waist)',
         lambda db: db.d[_SHROUD_PAK].__setitem__('particleEffectAttachPoints',
                                                  ['Bone_Waist'])),
        ('the demons move their shroud, so our pinned attach point goes stale',
         lambda db: _set_demon_attach('Smoke02')),
        ('the attach point is dropped, so placement is undefined',
         lambda db: db.d[_SHROUD_PAK].pop('particleEffectAttachPoints')),
        # ── b104 round 2: the EffectEntity-mirror class ─────────────────────
        ('donor residue survives on the EffectEntity (localOrientFix off a weapon FX)',
         lambda db: db.d[_SHROUD_FX].__setitem__('localOrientFix', [1])),
        ('the EffectEntity loses ActorName, which the demons record carries',
         lambda db: db.d[_SHROUD_FX].pop('ActorName')),
        ('the demons EffectEntity changes, so our pinned mirror goes stale',
         lambda db: _set_demon_fx_record(
             {'templateName': r'database\Templates\Effect.tpl',
              'ActorName': 'Something_Else', 'Class': 'EffectEntity',
              'effectFile': _DEMON_PFX})),
        ('the b98 R Hand attach residue is left on the shroud skill',
         lambda db: db.d[_SHROUD].__setitem__('particleEffectAttachPoint1',
                                              ['R Hand'])),
        ('the b98 round-4 defect returns: smoke off two fists',
         lambda db: db.d[_SHROUD_PAK].__setitem__('particleEffectAttachPoints',
                                                  ['R Hand', 'L Hand'])),
        ('the weapon boneList comes back on the EffectEntity (fists again)',
         lambda db: db.d[_SHROUD_FX].__setitem__('boneList',
                                                 ['Bone_R_Weapon', 'Bone_L_Weapon'])),
        ('the shroud stops playing the demons own .pfx',
         lambda db: db.d[_SHROUD_FX].__setitem__(
             'effectFile', [r'DRXeffects\shadowcloakrunning.pfx'])),
        ('the marauders mesh no longer embeds the shroud (provenance is gone)',
         lambda db: _set_demon_fx([r'Records\Effects\MonsterFX\Something_Else.dbr'])),
        ('the wearer loses his mesh, so the rig check cannot run',
         lambda db: db.d[_PETS[1]].pop('mesh')),
        # ── inherited legs that must not regress ───────────────────────────
        ('THE b98 DEFECT: shroud on the monster, on NO pet tier',
         lambda db: [_clear_always_on(db, p) for p in _PETS]),
        ('one pet tier is skipped while the other two are wired',
         lambda db: _clear_always_on(db, _PETS[1])),
        ('a NEW 4th pet tier is summoned and never gets the shroud',
         lambda db: (db.d.__setitem__(
             r'records\skills\soulskills\pets\toxeus_enslaver_4.dbr',
             {'Class': ['Pet'], 'description': ['tagSVCMonsterEnslaverPet'],
              'mesh': [_MESH_M], 'controller': [_CTRL_P],
              'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}),
             db.d[_ENSLAVER_SUMMON].__setitem__(
                 'spawnObjects',
                 _PETS + [r'records\skills\soulskills\pets\toxeus_enslaver_4.dbr']))),
        ('a LEGENDARY difficulty clone appears wearing his name tag',
         lambda db: db.d.__setitem__(
             r'records\creature\monster\shadowstalker\um_toxeus_enslaver_l_99.dbr',
             {'Class': ['Monster'], 'description': ['tagSVCMonsterEnslaver'],
              'mesh': [_MESH_M], 'controller': [_CTRL_M]})),
        ('the summon loses its spawnObjects, so the tier roster goes silently empty',
         lambda db: db.d[_ENSLAVER_SUMMON].__setitem__('spawnObjects', [])),
        ('the shroud is left ONLY on the AI leg, so a pet that never gets a '
         'BuffSelf tick out of combat shows nothing while Will inspects it',
         lambda db: db.d[_PETS[0]].pop('initialSkillName')),
        ('the shroud grows a combat payload',
         lambda db: db.d[_SHROUD].__setitem__('offensivePhysicalMin', [500.0])),
        ('the donor purple tint comes back',
         lambda db: db.d[_SHROUD].__setitem__('skillWeaponTintBlue', [1.0])),
        ('the shroud stops being a self-buff toggle',
         lambda db: db.d[_SHROUD].__setitem__('Class', ['Skill_AttackRadius'])),
        ('a pet loses the pre-existing DRX running smoke',
         lambda db: db.d[_PETS[2]].__setitem__('charFxPakRunningNames', [''])),
        ('CRASH LAW: a charFxPak lands on his SpawnPet skill (the build28 trap)',
         lambda db: db.d[_SPAWN].__setitem__('charFxPakSelfNames', [_SHROUD_PAK])),
        ('the demons themselves lose the running shroud (provenance unevidenced)',
         lambda db: db.d[_MARAUDER].__setitem__('charFxPakRunningNames', [''])),
    ]

    def _set_demon_fx(v):
        global _DEMON_FX_OVERRIDE
        _DEMON_FX_OVERRIDE = v

    def _set_demon_attach(v):
        global _DEMON_ATTACH_OVERRIDE
        _DEMON_ATTACH_OVERRIDE = v

    def _set_demon_fx_record(v):
        global _DEMON_FX_RECORD_OVERRIDE
        _DEMON_FX_RECORD_OVERRIDE = v

    def _set_mesh_smoke(v):
        global _MESH_SMOKE_OVERRIDE
        _MESH_SMOKE_OVERRIDE = v

    clean_fx = [r'Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr']
    clean_attach = _DEMON_MESH_ATTACH
    clean_rec = {f: v for f, v in _DEMON_FX_FIELDS}
    # MEASURED: the demons' rig carries the shroud compiled in, his does not.
    # That asymmetry IS the module's premise, so the stub states it explicitly
    # and `--selftest` re-derives both halves from the real binaries.
    clean_smoke = {_norm(_MESH_D): True, _norm(_MESH_M): False}

    def _reset():
        global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE
        global _DEMON_ATTACH_OVERRIDE, _DEMON_FX_RECORD_OVERRIDE
        global _MESH_SMOKE_OVERRIDE
        _RIG_NAMES_OVERRIDE = _RIG
        _DEMON_FX_OVERRIDE = list(clean_fx)
        _DEMON_ATTACH_OVERRIDE = clean_attach
        _DEMON_FX_RECORD_OVERRIDE = dict(clean_rec)
        _MESH_SMOKE_OVERRIDE = dict(clean_smoke)

    _reset()
    try:
        verify(_base())
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        _reset()
        db = _base()
        plant(db)
        try:
            verify(db)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    # CLEAR, never _reset(): leaving the clean overrides in place would make a
    # combined `--negtest --selftest` run check the pinned values against
    # themselves and report a real-asset PASS it never performed. Test hooks must
    # not survive the test - that is the same class of error as round 1's stub
    # asserting the module's own premise.
    _clear_overrides()
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


def _clear_overrides():
    global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE
    global _DEMON_ATTACH_OVERRIDE, _DEMON_FX_RECORD_OVERRIDE
    global _MESH_SMOKE_OVERRIDE
    _RIG_NAMES_OVERRIDE = None
    _DEMON_FX_OVERRIDE = None
    _DEMON_ATTACH_OVERRIDE = None
    _DEMON_FX_RECORD_OVERRIDE = None
    _MESH_SMOKE_OVERRIDE = None


# ── INSTRUMENT SELF-TEST (the round-1 failure mode, closed) ─────────────────

def _selftest():
    r"""py tools/patches/enslaver_shroud.py --selftest

    A negative test can only ever be as true as the premise its stub asserts, and
    round 1's stub asserted a false one. This checks the MEASUREMENT ITSELF against
    the real archives: it re-reads both mesh binaries and requires the facts this
    module's design rests on to still hold. Loud SKIP when the archives are not
    reachable - never a silent pass.
    """
    _clear_overrides()          # this leg reads the REAL assets or nothing at all
    try:
        import mesh_assets
    except Exception as e:                                   # noqa: BLE001
        print("SELFTEST SKIP: mesh_assets unavailable (%s)" % e)
        return 0
    if not mesh_assets.arcs_available():
        print("SELFTEST SKIP: no reachable .arc archives from this working tree")
        return 0
    m_his = r'Creatures\Monster\Skeleton\SkeletonGrayBlack01New.msh'
    m_dem = r'Creatures\Monster\ShadowStalker\ShadowStalker.msh'
    bad = []
    rigs = {}
    for ref in (m_his, m_dem):
        data, arc = mesh_assets.read_asset(ref)
        if not data:
            print("SELFTEST SKIP: %s did not resolve" % ref)
            return 0
        rigs[ref] = {'names': {n.lower() for n in mesh_assets.rig_names_of(data)},
                     'attach': mesh_assets.attach_points_of(data),
                     'bones': mesh_assets.bones_of(data),
                     'fx_at': mesh_assets.embedded_fx_attachments_of(data),
                     'arc': arc}
        print("  %-34s %d bone(s) + %d attach point(s)  %s"
              % (ref.rsplit('\\', 1)[-1], len(rigs[ref]['bones']),
                 len(rigs[ref]['attach']), rigs[ref]['attach']))

    # 1. the instrument is not blind: the AttachPoint table must be non-empty and
    #    must NOT be findable by a NUL-anchored scan (that is the whole bug).
    if not rigs[m_his]['attach']:
        bad.append("attach_points_of() found NO AttachPoint on %s - the reader is "
                   "blind again and every RIG ATTACH result is meaningless" % m_his)
    nul_only = {n.lower() for n in rigs[m_his]['bones']}
    if _DEMON_MESH_ATTACH.lower() in nul_only:
        bad.append("%r turned up in the BONE table, so this selftest no longer "
                   "distinguishes the two namespaces" % _DEMON_MESH_ATTACH)

    # 2. the load-bearing fact: the attach point we copy is on HIS rig.
    if _DEMON_MESH_ATTACH.lower() not in rigs[m_his]['names']:
        bad.append("%r is NOT on %s. That is round 1's claim, and if it is ever "
                   "true again this module aims at nothing." % (_DEMON_MESH_ATTACH, m_his))

    # 3. the counter-example must stay a counter-example.
    if _DEMON_ONLY_ATTACH.lower() in rigs[m_his]['names']:
        bad.append("%r is now on HIS rig too, so it is no longer the missing-attach "
                   "example the gate and the negtest use" % _DEMON_ONLY_ATTACH)
    if _DEMON_ONLY_ATTACH.lower() not in rigs[m_dem]['names']:
        bad.append("%r is not on the DEMONS' rig either" % _DEMON_ONLY_ATTACH)

    # 4. the demons really hang their shroud where we say they do.
    want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
    hung = [a for a, e in rigs[m_dem]['fx_at']
            if e and str(e).replace('/', '\\').rsplit('\\', 1)[-1].lower() == want]
    if [h.lower() for h in hung] != [_DEMON_MESH_ATTACH.lower()]:
        bad.append("the demons hang %s at %r, not at the pinned %r"
                   % (want, hung, _DEMON_MESH_ATTACH))

    # 4b. R-255: THE SLOT CEILING, re-measured against the vanilla template.
    #     This is the fact b93 got wrong from a comment instead of a binary, and
    #     the whole shape of this module now rests on it, so it is re-derived.
    try:
        from pathlib import Path
        from arc_patcher import ArcArchive
        tpl_arc = Path(mesh_assets.game_dir()) / 'Toolset' / 'Templates.arc'
        if not tpl_arc.exists():
            print("  Templates.arc not reachable: the slot ceiling was NOT re-measured")
        else:
            import re as _re
            blob = ArcArchive.from_file(tpl_arc).get_file(
                'templates/templatebase/monsterskillmanager.tpl')
            if not blob:
                bad.append("MonsterSkillManager.tpl is not in Templates.arc, so the "
                           "declared slot ceiling could not be re-measured at all")
            else:
                text = blob.decode('latin-1')
                slots = sorted({int(m) for m in _re.findall(r'skillName(\d+)', text)})
                if not slots:
                    bad.append("MonsterSkillManager.tpl declares NO skillName slot - "
                               "the reader is blind and the ceiling is meaningless")
                elif max(slots) != _ENGINE_SKILL_SLOT_MAX:
                    bad.append("MonsterSkillManager.tpl declares skillName1..%d but "
                               "this module is pinned to %d. Re-derive: b93 shipped "
                               "on a WRITTEN-DOWN belief about this number ('the "
                               "template reaches 23') that no binary ever supported."
                               % (max(slots), _ENGINE_SKILL_SLOT_MAX))
                else:
                    print("  MonsterSkillManager.tpl declares skillName1..%d (and "
                          "nothing above it) - the ceiling holds" % max(slots))
    except Exception as e:                                   # noqa: BLE001
        print("  slot ceiling NOT re-measured (%s)" % e)

    # 5. the pinned EffectEntity mirror still matches the base-game record.
    st, theirs = _demon_fx_record(None)
    if st != 'PASS' or not theirs:
        print("  base-game .arz not reachable: EffectEntity mirror NOT re-checked")
    else:
        pinned = {f: v for f, v in _DEMON_FX_FIELDS}
        if {k: str(v) for k, v in theirs.items()} != pinned:
            bad.append("the demons' own %s now reads %r, pinned %r"
                       % (_DEMON_FX_REF, theirs, pinned))
        else:
            print("  %s mirrors the base-game record exactly (%d fields)"
                  % (_SHROUD_FX.rsplit('\\', 1)[-1], len(pinned)))

    for b in bad:
        print("  SELFTEST OFFENDER: %s" % b)
    if bad:
        print("selftest: FAILED (%d)" % len(bad))
        return 1
    print("selftest OK: %r is declared on BOTH rigs (the round-1 measurement was "
          "false); %r is on the demons' rig ONLY and stays the silent-nothing "
          "example; the demons hang %s at %r."
          % (_DEMON_MESH_ATTACH, _DEMON_ONLY_ATTACH, want, _DEMON_MESH_ATTACH))
    return 0


if __name__ == '__main__':
    import sys
    rc = 0
    if '--negtest' in sys.argv:
        rc |= _negtest()
    if '--selftest' in sys.argv:
        rc |= _selftest()
    sys.exit(rc)
