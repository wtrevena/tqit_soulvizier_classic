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
still, out of combat - and why nothing the Enslaver had could match it:

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

  A. **THE ASSET.** `svc_enslaver_shroud_fx` (our own EffectEntity, cloned from
     the shipped `drxshadowcloakrunning_fx` for structure) points at
     `Effects\MonsterFX\ShadowStalker_Smoke01.pfx` - byte-for-byte the file the
     demons' mesh plays - and its donor's weapon `boneList` is DELETED, so the
     smoke is no longer nailed to his fists.
     It is our own record rather than a direct reference to the base-game
     `Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr` for one reason: a record
     that lives only in the base `.arz` cannot be read, gated or diffed by this
     build. The `.pfx` - the thing that renders - is identical either way, and
     verify() proves that file ships (A9 render resolution) rather than assuming.

  B. **THE SHAPE.** `particleEffectAttachPoints = ['Bone_Waist']`.
     ⚠️ We may NOT copy the demons' own attach name: `SpecialHit01` is a helper
     that exists on `ShadowStalker.msh` and **does NOT exist on
     `SkeletonGrayBlack01New.msh`** (measured in both mesh binaries), and an FX
     aimed at a missing attach point silently renders NOTHING - the exact trap
     R-95 wrote down and nobody had checked since. `Bone_Waist` IS present on his
     rig (and on the demons'), it is where `RevenantPoison_FX` hung its aura on
     his old mesh, and the base game ships body-wrap paks that attach at raw bone
     names (`dmgabsolute_*charfxpak` -> `Bone_Spine02`, both shoulders). verify()
     re-reads the wearer's mesh binary and FAILS if any attach point this pak
     names is missing from that rig.

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
# the demons' MESH attach helper - NAMED HERE ONLY TO BE REFUSED. It does not
# exist on the Enslaver's rig; copying it would render nothing at all.
_DEMON_MESH_ATTACH = 'SpecialHit01'

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

# ── SHAPE (b104) ────────────────────────────────────────────────────────────
# A bone that EXISTS on his rig, and the one his old mesh hung its aura on.
# Never `SpecialHit01` (missing from his rig -> silent nothing) and never
# 'R Hand'/'L Hand' (the b98 round-4 defect: smoke off two fists).
_ATTACH = ['Bone_Waist']
_PARTICLE_COUNT = 1     # ONE body emitter, exactly like the demons' one CreateEntity

# ── ALWAYS ON (b104) ────────────────────────────────────────────────────────
_BUFF_TRIGGER = 'WheneverPossible'
_CTRL_PREFIX = 'svc_alwayson_'

# ── TEST HOOKS ──────────────────────────────────────────────────────────────
# The two asset-level gates read `.msh` binaries out of the shipped `.arc`s. The
# negative test cannot ship archives, so it injects the two answers instead. In a
# real build both stay None and the gates read the real assets (or announce a
# loud DOWNGRADE - never a silent pass).
_RIG_NAMES_OVERRIDE = None      # {mesh_ref_lower: set(attach/bone names)}
_DEMON_FX_OVERRIDE = None       # [entity refs embedded in the demons' mesh]


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
    """(status, set(attach/bone helper names)) out of a mesh binary.

    status PASS / SKIP. SKIP means the archives are not reachable from this
    working tree; the caller ANNOUNCES that rather than counting it as a pass.
    """
    if _RIG_NAMES_OVERRIDE is not None:
        got = _RIG_NAMES_OVERRIDE.get(_norm(mesh_ref))
        return ('PASS', got) if got is not None else ('SKIP', set())
    try:
        import re
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', set())
        data, _arc = mesh_assets.read_asset(mesh_ref)
        if not data:
            return ('SKIP', set())
        names = set()
        for m in re.finditer(rb'[A-Za-z][A-Za-z0-9_ ]{2,31}\x00', data):
            names.add(m.group(0)[:-1].decode('ascii'))
        return ('PASS', names)
    except Exception:                                        # noqa: BLE001
        return ('SKIP', set())


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
    """Our own EffectEntity playing the demons' own .pfx, body-attachable."""
    _require(db, _FX_DONOR)
    if not db.has_record(_SHROUD_FX):
        db.clone_record(_FX_DONOR, _SHROUD_FX)
    db.set_field(_SHROUD_FX, 'effectFile', _DEMON_PFX)
    # THE DONOR'S WEAPON BONES MUST GO. `drxshadowcloakrunning_fx` carries
    # boneList = Bone_R_Weapon;Bone_L_Weapon, which is why every previous
    # rendering of this shroud came off his fists instead of from around him.
    _del_field(db, _SHROUD_FX, 'boneList')
    db.set_field(_SHROUD_FX, 'FileDescription',
                 'SVC Enslaver: the demons own ShadowStalker smoke, body-attached '
                 '(visual only)')
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


def _by_name_tag(db):
    """W2: every Monster/Pet record described by one of his name tags.

    Catches a build-time DIFFICULTY CLONE, which the summon chain cannot see.
    Prefiltered on the .arz record-type index so this costs a slice of the DB
    rather than a full decode.
    """
    types = getattr(db, '_record_types', None) or {}
    out = []
    for n in db.record_names():
        t = types.get(n)
        if t and t not in ('Monster', 'Pet'):
            continue
        d = _gv1(db, n, 'description')
        if d and str(d).lower() in _NAME_TAGS:
            cls = str(_gv1(db, n, 'Class') or '')
            if cls.startswith('Monster') or cls.startswith('Pet'):
                out.append(n)
    return sorted(out)


def shroud_roster(db, w2=None):
    """{monster} + {every derived pet tier} + {anything wearing his name tag}."""
    w1 = ([_ENSLAVER] if db.has_record(_ENSLAVER) else []) + _pet_tiers(db)
    seen, out = set(), []
    for r in w1 + (list(w2) if w2 is not None else _by_name_tag(db)):
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def _wire_one(db, rec):
    """Shroud slot + always-on controller on one surface."""
    slot = _slot_of(db, rec, _SHROUD) or _free_skillname_slot(db, rec)
    if slot is None:
        raise SystemExit(
            "[enslaver_shroud] no free skillName slot on %s. R-26's spirit "
            "forbids dropping a functional skill to make room - stop and ask "
            "Will rather than sacrificing one." % rec)
    db.set_field(rec, 'skillName%d' % slot, _SHROUD)
    # Level is cosmetic here (the shroud carries no payload at all - the
    # VISUAL-ONLY invariant enforces that), it only has to be non-zero to show.
    # The monster keeps its per-difficulty [1,2,3]; a pet tier IS one record per
    # tier, so a scalar 1 is the honest shape there.
    db.set_field(rec, 'skillLevel%d' % slot, [1, 2, 3] if rec == _ENSLAVER else 1)

    ctrl = _gv1(db, rec, 'controller')
    if not ctrl or not db.has_record(str(ctrl)):
        raise SystemExit(
            "[enslaver_shroud] %s has no resolvable controller (%r), so a "
            "self-buff shroud can never fire on it." % (rec, ctrl))
    ours = str(ctrl) if _is_ours(ctrl) else _always_on_controller(db, str(ctrl))
    db.set_field(rec, 'controller', ours)
    db._modified.add(rec)
    return slot, ours


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
    for rec in shroud_roster(db):
        slot, ctrl = _wire_one(db, rec)
        print("  shroud -> skillName%-2d  ctrl=%-58s %s%s"
              % (slot, ctrl.rsplit('\\', 1)[-1], rec,
                 '   (MONSTER)' if rec == _ENSLAVER else '   (PET TIER)'))
    print("  %d surface(s): the demons' own %s on Bone_Waist, always on "
          "(BuffSelfBehavior=%s on SVC-owned controller clones); NO skill dropped; "
          "charFxPakRunningNames untouched everywhere."
          % (len(shroud_roster(db)), _DEMON_PFX.rsplit('\\', 1)[-1], _BUFF_TRIGGER))
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
                "SHAPE: shroud pak particleEffectAttachPoints=%r, expected %r. "
                "'R Hand'/'L Hand' is the b98 round-4 defect (smoke off two fists) "
                "and %r is the demons' OWN mesh helper, which does not exist on his "
                "rig and would render nothing at all."
                % (ap, _ATTACH, _DEMON_MESH_ATTACH))

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
    w2_list = _by_name_tag(db)
    w1 = set([_ENSLAVER] if db.has_record(_ENSLAVER) else []) | set(tiers)
    if w1 and set(w2_list) - w1:
        problems.append(
            "ROSTER WITNESS DISAGREEMENT: %r carr(y) an Enslaver name tag but are "
            "not reachable from the anchor + summon. A difficulty clone or a new "
            "tier has appeared (the Hunt has exactly such a clone, "
            "um_toxeus_hunt_l_99) and would ship with no shroud."
            % sorted(set(w2_list) - w1))

    roster = shroud_roster(db, w2=w2_list)
    ours_carriers = set()
    for rec in roster:
        is_pet = rec != _ENSLAVER
        tag = ' (PET TIER)' if is_pet else ' (MONSTER)'
        slot = _slot_of(db, rec, _SHROUD)
        if slot is None:
            problems.append(
                "SHROUD MISSING on %s%s - it is in none of its skillName slots. "
                "R-102's second amendment: b98 wired the MONSTER ONLY, every pet "
                "tier was skipped, and the pet is what Will summons." % (rec, tag))
        else:
            lv = db.get_field_value(rec, 'skillLevel%d' % slot)
            lv0 = lv[0] if isinstance(lv, list) and lv else lv
            if not lv0:
                problems.append("%s: shroud sits at skillLevel%d=%r (level 0 is not "
                                "granted, so it never displays)" % (rec, slot, lv))

        # ── ALWAYS ON, and provably visual-only ────────────────────────────
        ctrl = _gv1(db, rec, 'controller')
        if not ctrl or not db.has_record(str(ctrl)):
            problems.append("%s has no resolvable controller (%r), so its self-buff "
                            "shroud can never fire" % (rec, ctrl))
        else:
            ours_carriers.add(str(ctrl))
            if not _is_ours(ctrl):
                problems.append(
                    "%s%s still runs the SHARED controller %s. Either the shroud is "
                    "combat-gated on it (the WhenEnemyIsSeen default - OFF while "
                    "Will stands looking at the summoned pet, which is how he "
                    "inspects it), or a shared AI record was edited in place and "
                    "148 other pets moved with it." % (rec, tag, ctrl))
            trig = str(_gv1(db, str(ctrl), 'BuffSelfBehavior'))
            if trig != _BUFF_TRIGGER:
                problems.append(
                    "%s: controller %s has BuffSelfBehavior=%r, expected %r. A "
                    "toggled shroud the AI only fires in combat is not a shroud "
                    "he wears; that is why this request has now been filed three "
                    "times." % (rec, ctrl, trig, _BUFF_TRIGGER))
        # the AI flip is only safe while the shroud is the ONLY self-buff here
        others = []
        for i, sk in sorted(_skill_slots(db, rec).items()):
            if _norm(sk) == _norm(_SHROUD) or not db.has_record(sk):
                continue
            if 'BuffSelf' in str(_gv1(db, sk, 'Class') or ''):
                others.append((i, sk))
        if others:
            problems.append(
                "AI SIDE EFFECT: %s carries other Skill_BuffSelf* skill(s) %r. "
                "BuffSelfBehavior=%s makes the AI fire ALL of them out of combat, "
                "so this lane's visual-only claim no longer holds - split the "
                "trigger or get Will's call before shipping."
                % (rec, others, _BUFF_TRIGGER))

        # ── RIG: an attach point missing from the wearer's mesh renders NOTHING
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
                missing = [a for a in _lst(db, _SHROUD_PAK, 'particleEffectAttachPoints')
                           if a not in names]
                if missing:
                    problems.append(
                        "RIG ATTACH: %s wears %s, which has no %r. An FX aimed at an "
                        "attach point the mesh does not carry renders NOTHING, "
                        "silently - the trap R-95 wrote down and no wave checked. "
                        "(The demons' own %r is exactly such a name on this rig.)"
                        % (rec, mesh, missing, _DEMON_MESH_ATTACH))

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
    print("  [enslaver_shroud].verify OK: the Enslaver of Souls wears the demons' own "
          "%s on Bone_Waist - a bone his rig actually carries - fired by SVC-owned "
          "controller clones at BuffSelfBehavior=%s so it is ON out of combat, "
          "visual-only (no payload, no tint, and the shroud is the only self-buff in "
          "either kit), on ALL %d surface(s): the monster AND every derived pet tier "
          "(%d). Running FX untouched everywhere; no charFxPak on any SpawnPet skill. "
          "WHAT IS STILL NOT CLAIMED: how it READS in game (BL-R250-DEBT-1)."
          % (_DEMON_PFX.rsplit('\\', 1)[-1], _BUFF_TRIGGER, len(roster), len(tiers)))
    return tags


# ── NEGATIVE TEST ───────────────────────────────────────────────────────────

def _negtest():
    """py tools/patches/enslaver_shroud.py --negtest"""
    global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE
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
    _RIG = {_norm(_MESH_M): {'Bone_Waist', 'Bone_Spine02', 'Bone_Head',
                             'Bone_R_Weapon', 'Bone_L_Weapon'},
            _norm(_MESH_D): {'Bone_Waist', 'SpecialHit01'}}
    _PETS = [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
             for i in (1, 2, 3)]
    _CTRL_M = r'records\controllers\monster\svc_alwayson_controller_skeleton_toxeus.dbr'
    _CTRL_P = (r'records\skills\spirit\drxpet\drxpet_controllers'
               r'\svc_alwayson_controller_skelly_aggressive.dbr')
    _SHARED_P = (r'records\skills\spirit\drxpet\drxpet_controllers'
                 r'\controller_skelly_aggressive.dbr')
    _SPAWN = r'records\skills\boss skills\svc_enslaver_summonmarauders.dbr'

    def _base():
        db = _Stub()
        db.d[_SHADOWCLOAK_PAK] = {'particleEffectNames': [_SHADOWCLOAK_FX]}
        db.d[_SHADOWCLOAK_FX] = {'Class': ['EffectEntity'],
                                 'effectFile': [r'DRXeffects\shadowcloakrunning.pfx'],
                                 'boneList': ['Bone_R_Weapon', 'Bone_L_Weapon']}
        db.d[_SHROUD_FX] = {'Class': ['EffectEntity'], 'effectFile': [_DEMON_PFX]}
        db.d[_SHROUD_PAK] = {'particleEffectNames': [_SHROUD_FX] * _PARTICLE_COUNT,
                             'particleEffectAttachPoints': list(_ATTACH)}
        db.d[_SHROUD] = {'Class': ['Skill_BuffSelfToggled'],
                         'charFxPakSelfNames': [_SHROUD_PAK],
                         'skillWeaponTintRed': [0.0], 'skillWeaponTintGreen': [0.0],
                         'skillWeaponTintBlue': [0.0]}
        db.d[_MARAUDER] = {'Class': ['Monster'], 'mesh': [_MESH_D],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_SPAWN] = {'Class': ['Skill_SpawnPetMonster'], 'spawnObjects': [_MARAUDER]}
        db.d[_CTRL_M] = {'BuffSelfBehavior': [_BUFF_TRIGGER]}
        db.d[_CTRL_P] = {'BuffSelfBehavior': [_BUFF_TRIGGER]}
        db.d[_SHARED_P] = {'BuffSelfBehavior': ['WhenEnemyIsSeen']}
        db.d[_ENSLAVER] = {'Class': ['Monster'], 'description': ['tagSVCMonsterEnslaver'],
                           'mesh': [_MESH_M], 'controller': [_CTRL_M],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                           'skillName8': [_SPAWN],
                           'skillName19': [_SHROUD], 'skillLevel19': [1, 2, 3]}
        db.d[_ENSLAVER_SUMMON] = {'Class': ['Skill_SpawnPet'], 'spawnObjects': list(_PETS)}
        for p in _PETS:
            db.d[p] = {'Class': ['Pet'], 'description': ['tagSVCMonsterEnslaverPet'],
                       'mesh': [_MESH_M], 'controller': [_CTRL_P],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                       'skillName13': [_SHROUD], 'skillLevel13': [1]}
        # a bystander that must NOT move with the Enslaver's AI change
        db.d[r'records\skills\soulskills\pets\boneash_1.dbr'] = {
            'Class': ['Pet'], 'controller': [_SHARED_P]}
        return db

    plants = [
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
        ('the shroud is aimed at the demons OWN mesh helper, absent from his rig',
         lambda db: db.d[_SHROUD_PAK].__setitem__('particleEffectAttachPoints',
                                                  [_DEMON_MESH_ATTACH])),
        ('the attach point is dropped, so placement is undefined',
         lambda db: db.d[_SHROUD_PAK].pop('particleEffectAttachPoints')),
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
         lambda db: [db.d[p].pop('skillName13') for p in _PETS]),
        ('one pet tier is skipped while the other two are wired',
         lambda db: db.d[_PETS[1]].pop('skillName13')),
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
        ('a pet gets the shroud at level 0 (in a slot, never displayed)',
         lambda db: db.d[_PETS[0]].__setitem__('skillLevel13', [0])),
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

    _RIG_NAMES_OVERRIDE = _RIG
    _DEMON_FX_OVERRIDE = [r'Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr']
    clean_fx = list(_DEMON_FX_OVERRIDE)
    try:
        verify(_base())
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        _DEMON_FX_OVERRIDE = list(clean_fx)
        db = _base()
        plant(db)
        try:
            verify(db)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    _DEMON_FX_OVERRIDE = list(clean_fx)
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    sys.exit(_negtest() if '--negtest' in sys.argv else 0)
