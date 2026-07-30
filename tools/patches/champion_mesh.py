r"""champion_mesh - R-102: KILL THE GREEN BY REPLACING THE MESH. And R-93 with it.

WILL, VERBATIM (the report that reopened this):

> "ok i was wrong, toxeus the murderer enslaver of souls are still having a green
>  glow and it is not a skill of mine"
> "it is constant, he glows green the whole time"
> "yes the demons that he summons have the proper black shroud and they dont have
>  any green"
> "i cant summon the devourer since i havent been able to kill him to get his soul
>  but from what i remember he had the green glow too"

--------------------------------------------------------------------------------
WHY FOUR FIX WAVES FAILED, AND WHY THIS ONE IS A DIFFERENT KIND OF CHANGE
--------------------------------------------------------------------------------
b39 / b55 / b55r2 / b92 all edited FX FIELDS on the creature and pet `.dbr`
records. Every one of them could sincerely verify its own change and still not
move a pixel, because THE GREEN WAS NEVER IN A FIELD. It is compiled into the
mesh asset. Measured first-hand by this lane, from the shipped bytes:

    tools/mesh_assets.embedded_fx_of(Creatures\Monster\Skeleton\RevenantPoison.msh)
      -> ['Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr']

and that effect entity, read out of the base-game arz, is

    boneList   = Bone_R_Weapon; Bone_L_Weapon
    effectFile = Effects\MonsterFX\Buffs\RevenantPoison.pfx
    (that .pfx names Shaders\Particle\ParticleAdditive.ssh - an ADDITIVE-BLEND
     particle, which is exactly Will's "it depends on the lighting")

`baseTexture` replaces the PRIMARY SKIN only, so no `.dbr` field can suppress an
effect entity the MESH FILE itself instantiates. Will's own elimination closed
it: the marauders carry the byte-identical FX pak and show no green, and they
differ from the Enslaver in exactly one thing - the mesh.

--------------------------------------------------------------------------------
THE CHOICE OF MESH - MEASURED, AND IT CORRECTS R-102's OWN RECOMMENDATION
--------------------------------------------------------------------------------
R-102 proposed `ShadowStalker.msh` because it is "proven green-free in this exact
scene". Two measurements say do NOT use it for these two champions:

  1. IT IS NOT FX-FREE. `embedded_fx_of(ShadowStalker.msh)` ->
     `['Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr']`. It is green-FREE
     (Will confirmed the demons read black) but it is not effect-free, so it is
     evidence about one particular effect rather than about the mesh class.
  2. IT WOULD BREAK R-93 A SECOND WAY. `um_toxeus_hunt_99` - the THIRD champion -
     already wears `ShadowStalker.msh`. Moving the Enslaver onto it would fix the
     Enslaver-vs-Devourer collision by creating an Enslaver-vs-Hunt collision.

So each champion gets a DISTINCT mesh, and the two that are moving land on meshes
that carry NO embedded effect at all. The pool was derived, not guessed: every
`.msh` in the five Creatures arcs (986) filtered to those carrying the 20-bone
skeleton core (395) and then to those with zero embedded FX (303).

| champion | new mesh | embedded FX | rig vs RevenantPoison | why this one |
|---|---|---|---|---|
| Enslaver of Souls | `SkeletonGrayBlack01New.msh` | **none** | IDENTICAL 20-bone set | see THE ANIMATION PROOF - it is the NATIVE mesh of the clips he already plays |
| Devourer of Blood | `GoldenSkeleton01.msh` | **none** | IDENTICAL 20-bone set | closest clean sibling: only 4.6% of bytes differ from RevenantPoison, so his silhouette survives the fix; 464 shipped users, 59 of them on a `NewSkeleton_*` override + `ANM_Skeleton01` - the exact triple we need |
| The Endless Hunt | `ShadowStalker.msh` (UNCHANGED) | ShadowStalker_Smoke (Will-confirmed BLACK) | superset (30 bones) | already distinct; grandfathered, and named here so the gate can tell "known and confirmed" from "unaudited" |

`Skeleton01.msh` was the other FX-free candidate and is deliberately REJECTED:
it differs from `SkeletonGrayBlack01New.msh` by 784 bytes out of 348,798 (0.2%),
i.e. it is the same model. Using both would have "fixed" R-93 on paper while
leaving two champions that still read as one creature.

--------------------------------------------------------------------------------
THE ANIMATION PROOF - the risk R-102 flagged, and why it points the other way
--------------------------------------------------------------------------------
R-102: "THE REAL RISK IS ANIMATION, NOT COLOUR. A mesh swap re-rigs everything."
Correct as a warning, and measured out, it inverts for this particular swap:

  * BONE SET. `bones_of()` over all four meshes returns the SAME 20 bones for
    RevenantPoison, SkeletonGrayBlack01New, GoldenSkeleton01 (and Skeleton01).
    Nothing an existing clip drives goes missing.
  * THE CLIPS ARE ALREADY GRAYBLACK'S. Both champions bind
    `records\creature\monster\skeleton\anm\anm_skeleton01.dbr`, and that table -
    plus all 40 inline overrides on each champion record - is built from
    `SkeletonGrayBlackNEW_*.anm`. The Enslaver is TODAY playing SkeletonGrayBlack
    clips on a RevenantPoison body. Putting him on `SkeletonGrayBlack01New.msh`
    moves him ONTO the native mesh of his own animation set: this swap REMOVES a
    cross-rig mismatch rather than creating one.
  * CASTABILITY. Every skill in these records that names a
    `skillSpecialAnimationName` (LethalStrike / AoE360 / BloodBoil / Summon)
    is served by a `*SpecialAnimRef*` row on the SAME table, which is untouched -
    the mesh is not part of that resolution path.
  * The gate below re-proves all of this on the built db + shipped arcs, so it
    cannot rot.

--------------------------------------------------------------------------------
SHARED-RECORD LAW (the genericbossorb_04 / toxeus_passiveproperties lesson)
--------------------------------------------------------------------------------
`RevenantPoison.msh` has 30 carriers in the built arz. Only 13 are Toxeus
surfaces. The other 17 - four base/SV green revenants (`cm_revenanttainted_16`,
`um_nefesiris_30`, `um_rotbone_14`, `um_toxeus_21`, whose green is INTENDED:
they wear `newskeleton_grean.tex`), ten `pharaohshonorguard_mummyguardian_*`
summons and the `old_z_toxeus` dev dummy - are NOT ours and are NOT touched.
verify() proves that both ways: every roster member left, and every non-member
carrier stayed.

--------------------------------------------------------------------------------
ROSTER DERIVATION - "a future tier cannot be skipped"
--------------------------------------------------------------------------------
Only the ANCHORS are named (the champion monster records, the proxies that
preview them, and each champion's own soul-summon skill). Every PET TIER is read
out of the summon skill's `spawnObjects` array at build time, so adding a 4th
tier to a summon automatically puts it in scope for both the fix and the gate.
This is the same defect class as R-102's second amendment, where the shroud
reached the monster and none of the three pet tiers.
"""

import os
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Toxeus champion meshes: kill the mesh-embedded green (R-102) + R-93 distinctness"

# ── the mesh the green is baked into (never a destination, always a source) ──
GREEN_MESH = r'Creatures\Monster\Skeleton\RevenantPoison.msh'

# ── destinations, measured FX-free (see the table in the docstring) ──────────
ENSLAVER_MESH = r'Creatures\Monster\Skeleton\SkeletonGrayBlack01New.msh'
DEVOURER_MESH = r'Creatures\Monster\Skeleton\GoldenSkeleton01.msh'
HUNT_MESH = r'Creatures\Monster\ShadowStalker\ShadowStalker.msh'

# The Hunt's mesh is NOT effect-free, and that is fine and deliberate: this is
# the smoke Will looked at and called "the proper black shroud". Naming it makes
# the gate able to distinguish CONFIRMED from MERELY-PRESENT, instead of either
# failing on it or ignoring FX entirely.
HUNT_GRANDFATHERED_FX = ['Records\\Effects\\MonsterFX\\ShadowStalker_Smoke.dbr']

_EN_MONSTER = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
_BT_MONSTER = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
_HUNT_MONSTER = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
_HUNT_MONSTER_L = r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr'
_MARAUDER = r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr'

_EN_SUMMON = r'records\skills\soulskills\summon_toxeus_enslaver.dbr'
_BT_SUMMON = r'records\skills\soulskills\summon_bloodtoxeus.dbr'
_EOAT_SUMMON = r'records\skills\soulskills\summon_toxeus_eoat.dbr'

# FAMILIES: (label, mesh, anchor monsters, soul-summon skills whose spawnObjects
# ARE the pet tiers, preview proxies). Anchors only - tiers are derived.
FAMILIES = [
    {
        'label': 'Toxeus the Murderer, Enslaver of Souls',
        'mesh': ENSLAVER_MESH,
        'monsters': [_EN_MONSTER],
        'summons': [_EN_SUMMON],
        'proxies': [r'records\drxmap\proxy\q_enslaver_warband.dbr',
                    r'records\drxmap\proxy\q_yard_enslaver.dbr'],
        'must_be_fx_free': True,
    },
    {
        # The End of All Things pets are CLONES of the Devourer's own pets and
        # share his crimson identity, so they follow his mesh. Whether the EoAT
        # should instead get a FOURTH distinct silhouette of its own is a design
        # question this lane does not answer on its own authority - it is raised
        # in the R-102 amendment and registered as debt, not decided here.
        'label': 'Toxeus the Murderer, Devourer of Blood (+ End of All Things)',
        'mesh': DEVOURER_MESH,
        'monsters': [_BT_MONSTER],
        'summons': [_BT_SUMMON, _EOAT_SUMMON],
        'proxies': [r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr',
                    r'records\drxmap\proxy\q_bloodtoxeus_ambush.dbr'],
        'must_be_fx_free': True,
    },
    {
        'label': 'Toxeus the Murderer, The Endless Hunt',
        'mesh': HUNT_MESH,
        'monsters': [_HUNT_MONSTER, _HUNT_MONSTER_L],
        'summons': [],
        'proxies': [],
        'must_be_fx_free': False,          # grandfathered, see HUNT_GRANDFATHERED_FX
    },
]

# The 20-bone skeleton core every skeleton-family clip drives. Derived from
# RevenantPoison.msh itself at gate time; this literal is the fallback used when
# the arcs are unreachable and only exists so the constant is readable.
_CORE_BONES = (
    'Bone_Root', 'Bone_Waist', 'Bone_Spine01', 'Bone_R_Femur', 'Bone_L_Femur',
    'Bone_Spine02', 'Bone_R_Shin', 'Bone_L_Shin', 'Bone_Neck01',
    'Bone_R_Shoulder', 'Bone_L_Shoulder', 'Bone_R_Foot', 'Bone_L_Foot',
    'Bone_Head', 'Bone_R_ForeArm', 'Bone_L_ForeArm', 'Bone_R_Wrist',
    'Bone_L_Wrist', 'Bone_R_Weapon', 'Bone_L_Weapon')

# A base-game data defect this lane must NOT pretend away and must NOT "fix":
# 306 records in the built arz (Charon, the liches, the base skeleton pets, the
# Iron Lore test monsters, and two of ours by inheritance) carry an ArtManager
# BUILD PATH on `spearSpellAttackAnim`:
#     Build\Resources\Creatures\Monster\Skeleton\ANM\SkeletonGrayBlackNEW_OneHand_AttBeta.anm
# It resolves nowhere at runtime. It ships that way in the base game, it is
# unrelated to the mesh, and repointing 306 records - most of them not ours - is
# a different lane. The anim gate below therefore EXCLUDES this one prefix, by
# name, loudly, rather than silently passing or falsely failing. Registered as
# BL-R102-DEBT-3.
_UPSTREAM_BUILD_PATH_PREFIX = 'build\\resources\\'


def _norm(p):
    return str(p).replace('/', '\\').lower()


def _require_gates():
    return os.environ.get('SVC_REQUIRE_GATES', '') not in ('', '0', 'false', 'False')


def _gv(db, rec, field):
    v = db.get_field_value(rec, field)
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _gv1(db, rec, field):
    v = _gv(db, rec, field)
    return v[0] if v else None


def _tiers_from_summon(db, summon):
    """The pet tiers of a champion, READ from its summon skill's spawnObjects.

    This is the whole point of the roster being derived: a 4th tier appended to
    `spawnObjects` is picked up by the fix AND by the gate with no code change.
    """
    if not db.has_record(summon):
        return []
    out = []
    for v in _gv(db, summon, 'spawnObjects'):
        s = str(v).strip()
        if s and db.has_record(s) and s not in out:
            out.append(s)
    return out


def family_members(db, fam):
    """Every record whose mesh this family owns: anchors + preview proxies +
    every derived pet tier. Order is stable and de-duplicated."""
    out = []
    for r in list(fam['monsters']) + list(fam['proxies']):
        if db.has_record(r) and r not in out:
            out.append(r)
    for s in fam['summons']:
        for t in _tiers_from_summon(db, s):
            if t not in out:
                out.append(t)
    return out


def roster(db):
    """[(family, [members])] over the whole champion roster."""
    return [(fam, family_members(db, fam)) for fam in FAMILIES]


def _set_mesh_if_different(db, rec, mesh):
    """Write only on a real change.

    A no-op write still marks the record modified and re-encodes it, which would
    put unattributed rows in this wave's record-diff. The proof required of this
    lane is ZERO unattributed changes, so identical values are left alone.
    """
    cur = _gv1(db, rec, 'mesh')
    if _norm(cur) == _norm(mesh):
        return False
    db.set_field(rec, 'mesh', mesh)
    db._modified.add(rec)
    return True


def apply(db, tags):
    print("\n=== [champion_mesh] R-102: the green is IN the mesh - swap it (R-93 too) ===")
    total = 0
    for fam, members in roster(db):
        moved = []
        for rec in members:
            before = _gv1(db, rec, 'mesh')
            if _set_mesh_if_different(db, rec, fam['mesh']):
                moved.append((rec, before))
        total += len(moved)
        print("  %-58s -> %s" % (fam['label'], fam['mesh'].rsplit('\\', 1)[-1]))
        print("     roster: %d record(s) derived (%d monster/proxy anchors + %d pet tier(s))"
              % (len(members), len(fam['monsters']) + len(fam['proxies']),
                 sum(len(_tiers_from_summon(db, s)) for s in fam['summons'])))
        for rec, before in moved:
            print("     MOVED  %-66s (was %s)"
                  % (rec, str(before).rsplit('\\', 1)[-1]))
        if not moved:
            print("     (already correct - nothing written)")
    print("=== [champion_mesh] %d record(s) moved off the green mesh; "
          "verify() runs post-finalization ===\n" % total)
    return tags


# ────────────────────────────────────────────────────────────────────────────
# GATE
# ────────────────────────────────────────────────────────────────────────────
def _anm_refs(db, rec):
    """Every .anm this record can play: its own inline overrides plus the ones
    its bound animation table names."""
    refs = set()

    def _harvest(r):
        for k, tf in (db.get_fields(r) or {}).items():
            for v in (tf.values or []):
                s = str(v).strip()
                if s.lower().endswith('.anm'):
                    refs.add(s)

    _harvest(rec)
    tab = _gv1(db, rec, 'charAnimationTableName')
    if tab and db.has_record(str(tab)):
        _harvest(str(tab))
    return refs


def verify(db, tags=None):
    problems = []
    notes = []

    all_members = {}
    meshes_by_family = {}
    for fam, members in roster(db):
        meshes_by_family[fam['label']] = fam['mesh']
        if not members:
            problems.append("family %r resolved to ZERO records - the roster "
                            "derivation is broken (anchors renamed?)" % fam['label'])
            continue
        # 0. the anchors must actually be present, or the derivation silently
        #    shrinks and every other check below passes vacuously.
        for anchor in fam['monsters']:
            if not db.has_record(anchor):
                problems.append("family %r: anchor monster MISSING: %s"
                                % (fam['label'], anchor))
        for s in fam['summons']:
            if not db.has_record(s):
                problems.append("family %r: summon skill MISSING (its pet tiers "
                                "cannot be derived): %s" % (fam['label'], s))
            elif not _tiers_from_summon(db, s):
                problems.append("family %r: summon %s spawns NO resolvable pet - "
                                "the tier derivation returned nothing, so a tier "
                                "could be silently skipped" % (fam['label'], s))
        for rec in members:
            all_members[rec] = fam
            got = _gv1(db, rec, 'mesh')
            if _norm(got) != _norm(fam['mesh']):
                problems.append("%s carries mesh %r, expected %s (%s)"
                                % (rec, got, fam['mesh'], fam['label']))
            if _norm(got) == _norm(GREEN_MESH):
                problems.append(
                    "GREEN MESH STILL ON A CHAMPION SURFACE: %s. R-102 proved the "
                    "glow is the CreateEntity block inside %s; no .dbr field can "
                    "suppress it." % (rec, GREEN_MESH))

    # 1. R-93: the champions must not share a mesh.
    seen = {}
    for label, mesh in meshes_by_family.items():
        seen.setdefault(_norm(mesh), []).append(label)
    for mesh, labels in seen.items():
        if len(labels) > 1:
            problems.append(
                "R-93: %d champions share the mesh %s (%s). The whole point of "
                "this swap is that the three Toxeus champions read as three "
                "different creatures - fixing the green by collapsing two of "
                "them onto one silhouette trades one ruling for another."
                % (len(labels), mesh, ', '.join(sorted(labels))))

    # 2. SHARED-RECORD LAW + RETIREMENT PROTOCOL. `RevenantPoison.msh` is a SHARED
    #    asset: 30 carriers in the built arz, only 13 of them ours. This module
    #    REPOINTS our surfaces off it and must leave every other carrier - the
    #    base/SV green revenants (whose green is intended: they wear
    #    `newskeleton_grean.tex`), the ten pharaoh honour-guard summons and the
    #    dev dummy - exactly where they are. Proven both directions: no roster
    #    record still carries it, and it is never emptied out of the DB.
    green_carriers = sorted(
        n for n in db.record_names()
        if _norm(_gv1(db, n, 'mesh') or '') == _norm(GREEN_MESH))
    roster_still_green = [n for n in green_carriers if n in all_members]
    if roster_still_green:
        problems.append("roster records still on the green mesh: %s"
                        % roster_still_green)
    if not green_carriers:
        problems.append(
            "ZERO records carry %s. This module REPOINTS the Toxeus surfaces; it "
            "must never blank or retire the mesh for the base-game revenants and "
            "pharaoh guardians that legitimately wear it (RETIREMENT PROTOCOL)."
            % GREEN_MESH)
    notes.append("%d non-roster carrier(s) of %s left untouched"
                 % (len(green_carriers), GREEN_MESH.rsplit('\\', 1)[-1]))

    # 3. ANIMATION: every .anm any roster record can play must resolve.
    from mesh_assets import (arcs_available, asset_exists, mesh_report,
                             mod_resource_dirs)

    # B-GATE-HARDEN-1 shape. TWO preconditions, and the second one is the
    # non-obvious half: this mod SHIPS animation archives of its own
    # (`SVMesh\anims\...`), so a resolver that can only see the game install
    # reports every mod-authored clip as MISSING. That is a false failure, and a
    # false failure in an anim gate is worse than no gate - it teaches the next
    # lane to waive it. So an un-findable mod Resources dir is reported as the
    # gate being UNAVAILABLE, never as the animations being broken.
    _mod_res = mod_resource_dirs()
    if not arcs_available() or not _mod_res:
        msg = ("champion_mesh ASSET gate DID NOT RUN - %s\n"
               "    remedy: build into the work/ layout "
               "(work/<mod>/Database/<mod>.arz with work/<mod>/Resources beside "
               "it), and set SVC_TQAE_DIR if the game is not at the default "
               "Steam path"
               % ('the Creatures arcs are not reachable under %s'
                  % os.environ.get('SVC_TQAE_DIR', '<default Steam path>')
                  if not arcs_available() else
                  'the MOD Resources dir was not found, so mod-shipped .anm '
                  'archives (SVMesh.arc et al) could not be searched'))
        if _require_gates():
            problems.append(msg)
        else:
            notes.append("WARNING: " + msg)
    else:
        # 3a. every destination mesh must EXIST and (where required) be FX-free.
        ref = mesh_report(GREEN_MESH)
        if not ref['exists']:
            problems.append("the reference mesh %s does not resolve - the rig "
                            "comparison below has no baseline" % GREEN_MESH)
        if ref['exists'] and not ref['fx']:
            problems.append(
                "%s reports NO embedded FX. That contradicts the measured root "
                "cause of R-102 (its CreateEntity block is the green). Either the "
                "asset changed or embedded_fx_of() regressed - either way this "
                "module's whole premise needs re-proving before it ships."
                % GREEN_MESH)
        core = set(ref['bones']) if ref['exists'] else set(_CORE_BONES)
        for fam in FAMILIES:
            rep = mesh_report(fam['mesh'])
            if not rep['exists']:
                problems.append("%s: destination mesh does not resolve in any arc: %s"
                                % (fam['label'], fam['mesh']))
                continue
            if fam['must_be_fx_free'] and rep['fx']:
                problems.append(
                    "%s: destination mesh %s carries EMBEDDED FX %s. The entire "
                    "point of this swap is to land on a mesh that instantiates no "
                    "effect entity of its own - an embedded effect is invisible to "
                    "every .dbr scan and is exactly how four waves missed the green."
                    % (fam['label'], fam['mesh'], rep['fx']))
            if not fam['must_be_fx_free']:
                unexpected = [f for f in rep['fx'] if f not in HUNT_GRANDFATHERED_FX]
                if unexpected:
                    problems.append(
                        "%s: mesh %s grew an embedded effect that is NOT the "
                        "Will-confirmed black shroud: %s (grandfathered: %s)"
                        % (fam['label'], fam['mesh'], unexpected,
                           HUNT_GRANDFATHERED_FX))
            missing_bones = core - set(rep['bones'])
            if missing_bones:
                problems.append(
                    "%s: mesh %s is MISSING %d bone(s) the old rig drives (%s). "
                    "Every .anm binds by bone; a missing bone is a limb that stops "
                    "animating, which is R-102's stated real risk."
                    % (fam['label'], fam['mesh'], len(missing_bones),
                       sorted(missing_bones)[:8]))

        # 3b. every .anm reachable from every roster record must resolve.
        unresolved = {}
        waived = 0
        checked = set()
        for rec in sorted(all_members):
            for a in sorted(_anm_refs(db, rec)):
                if _norm(a).startswith(_UPSTREAM_BUILD_PATH_PREFIX):
                    waived += 1
                    continue
                if a in checked:
                    continue
                checked.add(a)
                if not asset_exists(a):
                    unresolved.setdefault(a, []).append(rec)
        if unresolved:
            for a, recs in sorted(unresolved.items()):
                problems.append(
                    "UNRESOLVED ANIMATION %s (played by %d roster record(s), e.g. "
                    "%s). A champion whose clip does not resolve T-poses."
                    % (a, len(recs), recs[0]))
        notes.append("animation: %d distinct .anm reachable from the roster, all "
                     "resolve (mod arcs searched: %s); %d reference(s) waived as "
                     "the base-game '%s' build-path defect (BL-R102-DEBT-3)"
                     % (len(checked), [str(p) for p in _mod_res], waived,
                        _UPSTREAM_BUILD_PATH_PREFIX))

    if problems:
        for p in problems:
            print("  CHAMPION-MESH OFFENDER: %s" % p)
        raise SystemExit("champion_mesh.verify FAILED: %d problem(s)" % len(problems))
    for n in notes:
        print("  [champion_mesh] %s" % n)
    print("  [champion_mesh].verify OK: %d roster record(s) across %d champions, "
          "0 on %s, 3 distinct meshes (R-93), every destination mesh FX-audited "
          "and rig-complete, every reachable .anm resolves."
          % (len(all_members), len(FAMILIES), GREEN_MESH.rsplit('\\', 1)[-1]))
    return tags


# ────────────────────────────────────────────────────────────────────────────
# PLANTED NEGATIVES
# ────────────────────────────────────────────────────────────────────────────
def _negtest():
    """py tools/patches/champion_mesh.py --negtest"""
    from collections import OrderedDict

    class _TF(object):
        def __init__(self, v):
            self.values = list(v) if isinstance(v, list) else [v]

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

    EN_PETS = [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
               for i in (1, 2, 3)]
    BT_PETS = [r'records\skills\soulskills\pets\bloodtoxeus_%d.dbr' % i
               for i in (1, 2, 3)]
    EOAT_PETS = [r'records\skills\soulskills\pets\toxeus_eoat_%d.dbr' % i
                 for i in (1, 2, 3)]
    TABLE = r'records\creature\monster\skeleton\anm\anm_skeleton01.dbr'
    LIVE_ANM = r'Creatures\Monster\Skeleton\ANM\SkeletonGrayBlackNEW_Run.anm'
    DEAD_ANM = (r'Build\Resources\Creatures\Monster\Skeleton\ANM'
                r'\SkeletonGrayBlackNEW_OneHand_AttBeta.anm')

    def _base():
        db = _Stub()
        db.d[TABLE] = {'sHandedRunAnim': [LIVE_ANM],
                       'spearSpellAttackAnim': [DEAD_ANM]}
        for r in [_EN_MONSTER] + EN_PETS + [
                r'records\drxmap\proxy\q_enslaver_warband.dbr',
                r'records\drxmap\proxy\q_yard_enslaver.dbr']:
            db.d[r] = {'mesh': [ENSLAVER_MESH], 'charAnimationTableName': [TABLE]}
        for r in [_BT_MONSTER] + BT_PETS + EOAT_PETS + [
                r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr',
                r'records\drxmap\proxy\q_bloodtoxeus_ambush.dbr']:
            db.d[r] = {'mesh': [DEVOURER_MESH], 'charAnimationTableName': [TABLE]}
        for r in (_HUNT_MONSTER, _HUNT_MONSTER_L):
            db.d[r] = {'mesh': [HUNT_MESH]}
        db.d[_MARAUDER] = {'mesh': [HUNT_MESH]}
        db.d[_EN_SUMMON] = {'spawnObjects': list(EN_PETS)}
        db.d[_BT_SUMMON] = {'spawnObjects': list(BT_PETS)}
        db.d[_EOAT_SUMMON] = {'spawnObjects': list(EOAT_PETS)}
        # the non-target carriers the shared-record law protects
        for r in (r'records\creature\monster\skeleton\um_toxeus_21.dbr',
                  r'records\creature\monster\skeleton\um_rotbone_14.dbr'):
            db.d[r] = {'mesh': [GREEN_MESH]}
        return db

    plants = [
        ('the monster is fixed but a PET TIER is left on the green mesh '
         '(the R-102 second-amendment defect class)',
         lambda db: db.d[EN_PETS[2]].__setitem__('mesh', [GREEN_MESH])),
        ('a NEW 4th pet tier is added to the summon and never repointed',
         lambda db: (db.d.__setitem__(
             r'records\skills\soulskills\pets\toxeus_enslaver_4.dbr',
             {'mesh': [GREEN_MESH], 'charAnimationTableName': [TABLE]}),
             db.d[_EN_SUMMON].__setitem__(
                 'spawnObjects', EN_PETS + [
                     r'records\skills\soulskills\pets\toxeus_enslaver_4.dbr']))),
        ('the Devourer is put on the Enslaver mesh (green fixed, R-93 broken)',
         lambda db: [db.d[r].__setitem__('mesh', [ENSLAVER_MESH])
                     for r in [_BT_MONSTER] + BT_PETS]),
        ('the monster record itself is missed while the pets move',
         lambda db: db.d[_EN_MONSTER].__setitem__('mesh', [GREEN_MESH])),
        ('a preview proxy is left behind on the green mesh',
         lambda db: db.d[r'records\drxmap\proxy\q_yard_enslaver.dbr']
         .__setitem__('mesh', [GREEN_MESH])),
        ('the EoAT pets are forgotten (they clone the Devourer pets)',
         lambda db: [db.d[r].__setitem__('mesh', [GREEN_MESH]) for r in EOAT_PETS]),
        ('the summon skill loses its spawnObjects, so tier derivation goes silent',
         lambda db: db.d[_EN_SUMMON].__setitem__('spawnObjects', [])),
        ('an anchor monster disappears',
         lambda db: db.d.pop(_BT_MONSTER)),
        ('a champion is put on a mesh that does not exist',
         lambda db: [db.d[r].__setitem__(
             'mesh', [r'Creatures\Monster\Skeleton\NoSuchMesh.msh'])
             for r in [_EN_MONSTER] + EN_PETS + [
                 r'records\drxmap\proxy\q_enslaver_warband.dbr',
                 r'records\drxmap\proxy\q_yard_enslaver.dbr']]),
        ('a live (non-waived) animation reference stops resolving',
         lambda db: db.d[TABLE].__setitem__(
             'sHandedRunAnim',
             [r'Creatures\Monster\Skeleton\ANM\NoSuchClip.anm'])),
        ('the green mesh is RETIRED out of the DB instead of repointed '
         '(RETIREMENT PROTOCOL)',
         lambda db: [db.d[r].__setitem__('mesh', [ENSLAVER_MESH])
                     for r in (r'records\creature\monster\skeleton\um_toxeus_21.dbr',
                               r'records\creature\monster\skeleton\um_rotbone_14.dbr')]),
        ('the Hunt is dragged onto the Enslaver mesh',
         lambda db: [db.d[r].__setitem__('mesh', [ENSLAVER_MESH])
                     for r in (_HUNT_MONSTER, _HUNT_MONSTER_L)]),
    ]

    try:
        verify(_base())
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        db = _base()
        plant(db)
        try:
            verify(db)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    if '--negtest' in sys.argv:
        sys.exit(_negtest())
    if '--report' in sys.argv:
        from mesh_assets import mesh_report
        for m in (GREEN_MESH, ENSLAVER_MESH, DEVOURER_MESH, HUNT_MESH):
            r = mesh_report(m)
            print('%-56s exists=%-5s %8s B  bones=%-3d fx=%s'
                  % (m, r['exists'], r['size'], len(r['bones']), r['fx']))
    sys.exit(0)
