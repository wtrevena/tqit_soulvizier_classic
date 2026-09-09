r"""toxeus_mesh_aura - b92 GREEN GLOW, root cause: the MESH attaches the aura.

WILL'S LEAD (verbatim, 2026-07-27) - and it was exactly right:
    "i am pretty sure it is a skill or ability or something that is causing the
     green glow. i think this was inherited from the Toxeus the Murderer uber
     boss base monster that we created these monsters off of. If you compare the
     visuals to the secret passage toxeus the murderer who doesnt have the green
     glow, you may be able to find the difference"

THE DIFFERENCE (differential diagnosis vs Will's clean control)
---------------------------------------------------------------
    CONTROL  um_toxeus_99   (secret passage, "dream" kit)  mesh = RevenantStorm.msh
    GREEN    um_toxeus_21   (Greece, green BY DESIGN)      mesh = RevenantPoison.msh
    DEVOURER um_bloodtoxeus_99                             mesh = RevenantPoison.msh  <-- inherited
    ENSLAVER um_toxeus_enslaver_99                         mesh = RevenantPoison.msh  <-- inherited

A TQ `.msh` can carry an embedded entity-attachment script. Every Revenant mesh
ends with, verbatim from the shipped Creatures.arc bytes:

    CreateEntity
    {
        attach = "Waist"
        entity = "Records\Effects\MonsterFX\Buffs\Revenant<Element>_FX.dbr"
    }

So the MESH ITSELF spawns a permanent elemental particle effect on whatever
creature wears it. RevenantPoison.msh spawns RevenantPoison_FX -> (that record
is ABSENT from the mod arz and resolves from the BASE game db: Class=EffectEntity,
effectFile=Effects\MonsterFX\Buffs\RevenantPoison.pfx, boneList=Bone_R_Weapon;
Bone_L_Weapon) -> a GREEN particle cloud.

*** THIS IS WHY FOUR DATABASE-LEVEL FIXES ALL MISSED IT. ***
b55 (FX fields), b71 (soul->skill->icon->pets chain), b75 (shroud pak swap),
b81 (pet identity/race) are all DB scans. The attachment lives in the MESH FILE.
No .arz scan of any depth can see it. The Devourer carries no charFxPakRunning
shroud at ALL, so no shroud theory could ever have explained his green.

COLOUR PROVEN FROM THE ASSET BYTES, NOT THE NAME (standing law, born from
343_dark_smoke being NAMED dark and RENDERING green)
--------------------------------------------------------------------------
All four Revenant*.pfx are structurally identical - same two emitters ("Dark
Clouds" / "New Dark Clouds"), same textures (Effects\Textures\Organism01.tex +
Organism02.tex), same shaders. Poison and Storm are byte-for-byte the same
length (2061 B) and differ in only 140 bytes, which resolve to three 4-float
colour keyframe tracks per emitter. Reading the SAME offsets in all files makes
the channel assignment self-validating (round 2 re-derived this independently
of round 1 and of the vet, and all three agree to 3 decimals):

    variant           R              G              B          => renders
    RevenantFrost     0.534 / 0.520  0.824 / 0.844  1.000        ice blue    (check)
    RevenantStorm     0.592 / 0.604  0.501 / 0.513  0.695/0.722  blue-violet (check)
    RevenantPoison    0.534 / 0.520  1.000 / 0.974  0.591/0.637  *** GREEN ***

RevenantPoison peaks the GREEN channel at 1.0. Frost coming out ice-blue and
Storm blue-violet from the identical offsets is what validates the read.

Roster corroboration: every OTHER RevenantPoison.msh wearer in the shipped DB
also wears newskeleton_grean.tex (cm_revenanttainted_16, um_nefesiris_30,
um_rotbone_14, um_toxeus_21) - vanilla pairs that mesh with the green skin on
purpose. Our Toxeus records are the only wearers with a crimson/charcoal skin:
the skin override landed, the mesh-baked FX did not, so a green cloud sat on a
red/black body.

THE FIX - `Creatures\Monster\Skeleton\GoldenSkeleton01.msh`
-----------------------------------------------------------
Chosen in ROUND 2 after the round-1 choice (Skeleton01.msh) was correctly
rejected by the vet as an unproven rig for LIVE creatures. Every claim below is
re-derived from the shipped bytes (base-game Creatures.arc + the ground-truth
deployed DEV arz 1c27d5fa + the base-game database.arz):

  * NO CreateEntity block AT ALL -> no attached particle effect of any colour.
  * IDENTICAL RIG. Its bone-name set is EXACTLY RevenantPoison's 24 bones -
    zero missing, zero extra.
    ⚠️ MEASUREMENT PROVENANCE (round 2 re-derivation; the earlier "25 bones"
    figure was wrong and is corrected here). Bone names must be counted with a
    regex over the RAW mesh bytes (`Bone_[A-Za-z0-9_]+`), NOT by extracting
    printable string-runs: a run-based scan silently drops `Bone_Neck01` in
    GoldenSkeleton01/RevenantStorm/RevenantFrost/SkeletonSpirit01 because the
    name is not run-initial there, which fabricates a phantom 1-bone delta. The
    raw substring `bone_neck01` occurs 3x in EVERY one of these meshes.
    Heuristic-free counts: RevenantPoison 77 `Bone_` refs / 24 unique names;
    GoldenSkeleton01 76 / 24 (the 1-ref delta IS the removed CreateEntity
    attach node's `parent = "Bone_Waist"`); RevenantStorm 77 / 24;
    Skeleton01 92 / 32 - it carries 8 EXTRA bones (bone_l/r_finger01,
    fingerpoint01, thumb01, toe) and is 6.4 KB larger.
    Bone names are the animation binding surface, so anm_skeleton01 drives
    GoldenSkeleton01 exactly as it drives RevenantPoison today.
  * CANONICAL for anm_skeleton01 - the animation table all our targets use:
    307 records in the mod DB and 299 in the base DB pair GoldenSkeleton01.msh
    with anm_skeleton01, far ahead of every other mesh. (Skeleton01.msh: ONE,
    the unreferenced zzdev dummy z_nate.)
  * LIVE-CREATURE PRECEDENT, which is what round 1 lacked: 285 Class=Monster +
    22 Class=Pet + 1 PetNonScaling wearers in the mod DB (332 Monster in base).
    19 of those Pet-class wearers sit in records\skills\soulskills\pets\ - the
    exact class, directory and role as our 9 pet targets. (Skeleton01.msh:
    203 of 205 mod wearers and 278 of 279 base wearers are Class=Proxy map
    placeholders - a PROXY mesh, not a creature mesh.)
  * CORRECT FOR THE 4 PROXY TARGETS TOO, so all 15 records can share one mesh:
    GoldenSkeleton01.msh already has 121 Class=Proxy wearers in the mod DB
    (131 in base). It is not a creature-only mesh that we are forcing onto
    proxies - it is the mesh both roles already use.
  * SAME shader (Shaders\StandardSkinned.ssh) and SAME bump map
    (GoldenSkeleton01BMP.tex) as RevenantPoison. Its default diffuse is
    GoldenSkeleton01.tex rather than NewSkeleton_White.tex, which never renders
    here because every target sets `baseTexture` explicitly (crimson /
    charcoal / proxyu_boss).
  * It satisfies this repo's OWN pet rig contract (validate_summon_pets
    _collect_mesh_anim_families, which requires a real Monster to have proven
    the mesh+anim family) with 285 proving Monsters instead of one dev dummy.

Rejected alternatives, on their merits (round 2):
  * RevenantStorm.msh - rig-identical and NOT green (green is its lowest
    channel), but it still carries a CreateEntity block and would hang a
    BLUE-VIOLET particle cloud on a boss Will has ruled must read BLACK (R-10)
    / crimson-and-black (R-7). Trading a green cloud for a purple one is not
    what was asked. It stays legal under verify() (it is not green) so this
    module does not legislate an unratified "no aura of any colour" policy.
  * Skeleton01.msh - round 1's pick. Superset rig, proxy-placeholder precedent
    only. Rejected.
  * SkeletonSpirit01.msh - rig-identical, no CreateEntity, but a different
    shader (StandardBlendedGlowSkinned) that would add a glow. Rejected.

The bosses keep their deliberate identity: the Devourer his crimson skin +
svc_black_poison (R-7), the Enslaver his charcoal skin + the Will-confirmed
BLACK drxshadowcloak smoke (R-10). Nothing green is left to render.

SCOPE - EXACTLY 15 RECORDS
--------------------------
The 12 briefed Devourer + Enslaver records, PLUS the 3 End of All Things soul
pets. The EoAT pets are direct clones of the Devourer's pets, inherit the same
RevenantPoison.msh and therefore the same green, and R-8 rules their body must
be "ash-pale" - so green is wrong there too. Round 1 deferred them to another
lane as debt; round 2 fixes them here because it is the identical one-field
operation on identical records and leaving a third green Toxeus in the build is
exactly the "triaged into follow-up = NOT done" failure. The EoAT ash-pale SKIN
(baseTexture, currently crimson) remains that lane's item - untouched here.

NOT TOUCHED, deliberately:
  * um_toxeus_21   - the Greece green-poison Toxeus. His green is INTENTIONAL
                     (Will). verify() asserts he still wears RevenantPoison.
  * um_toxeus_99   - Will's clean secret-passage control. verify() asserts he
                     still wears RevenantStorm.
  * every other RevenantPoison/Fire/Frost wearer in the roster (the vanilla
    mummy guardians, cm_revenanttainted_16, um_nefesiris_30, um_rotbone_14).

ORDERING
--------
Registered after toxeus_suite / toxeus_champion_kits / black_poison /
enslaver_pet_fx / toxeus_endofallthings / toxeus_souls_100 so it is the ratified
FINAL registry writer of `mesh` on these 15 records, and so toxeus_endofallthings
has already cloned the Devourer pets into the EoAT pets before this runs.

See docs/reports/b92_green_differential.md.
"""

MODULE_NAME = "Toxeus green mesh-aura removal (b92)"

# ── The mesh-embedded effects, read out of the shipped Creatures.arc bytes ────
# mesh basename -> (attached EffectEntity, .pfx, proven RGB peak, verdict, is_green)
AURA_MESHES = {
    'revenantpoison.msh': (r'Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantPoison.pfx',
                           (0.534, 1.000, 0.591), 'GREEN', True),
    'revenantstorm.msh':  (r'Records\Effects\MonsterFX\Buffs\RevenantStorm_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantStorm.pfx',
                           (0.592, 0.501, 0.695), 'blue-violet', False),
    'revenantfire.msh':   (r'Records\Effects\MonsterFX\Buffs\RevenantFire_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantFire01.pfx',
                           (1.000, 0.518, 0.007), 'orange/red', False),
    'revenantfrost.msh':  (r'Records\Effects\MonsterFX\Buffs\RevenantFrost_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantFrost.pfx',
                           (0.534, 0.824, 1.000), 'ice blue', False),
}

# Meshes byte-audited in round 2 and PROVEN to contain no CreateEntity block at
# all. A target on one of these carries no mesh-attached effect of any colour.
# (basename -> why it is safe for these records)
NO_EFFECT_MESHES = {
    'goldenskeleton01.msh':
        'no CreateEntity; identical 24-bone rig to RevenantPoison; canonical mesh '
        'for anm_skeleton01 (307 mod / 299 base records); 285 Monster + 22 Pet '
        'live wearers; same StandardSkinned shader + GoldenSkeleton01BMP bump',
    'skeleton01.msh':
        'no CreateEntity, but a PROXY placeholder in practice (203/205 mod and '
        '278/279 base wearers are Class=Proxy); superset rig (+8 finger/toe '
        'bones). Legal for the 4 proxy targets, NOT the choice for live creatures',
    'skeletonspirit01.msh':
        'no CreateEntity, rig-identical, but StandardBlendedGlowSkinned adds a glow',
}

CLEAN_MESH = r'Creatures\Monster\Skeleton\GoldenSkeleton01.msh'
GREEN_MESH_BASENAME = 'revenantpoison.msh'

_MESH = 'mesh'

# ── The 15 records (label, path) ─────────────────────────────────────────────
DEVOURER_FAMILY = [
    ('Devourer of Blood (fought boss)',
     r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'),
    ('Devourer soul pet 1', r'records\skills\soulskills\pets\bloodtoxeus_1.dbr'),
    ('Devourer soul pet 2', r'records\skills\soulskills\pets\bloodtoxeus_2.dbr'),
    ('Devourer soul pet 3', r'records\skills\soulskills\pets\bloodtoxeus_3.dbr'),
    ('Devourer chest-guard proxy', r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr'),
    ('Devourer corridor-ambush proxy', r'records\drxmap\proxy\q_bloodtoxeus_ambush.dbr'),
]
ENSLAVER_FAMILY = [
    ('Enslaver of Souls (fought boss)',
     r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'),
    ('Enslaver soul pet 1', r'records\skills\soulskills\pets\toxeus_enslaver_1.dbr'),
    ('Enslaver soul pet 2', r'records\skills\soulskills\pets\toxeus_enslaver_2.dbr'),
    ('Enslaver soul pet 3', r'records\skills\soulskills\pets\toxeus_enslaver_3.dbr'),
    ('Enslaver warband proxy', r'records\drxmap\proxy\q_enslaver_warband.dbr'),
    ('Enslaver yard proxy', r'records\drxmap\proxy\q_yard_enslaver.dbr'),
]
# Cloned FROM the Devourer pets by toxeus_endofallthings, so they inherited the
# identical green. R-8 rules the EoAT body "ash-pale"; the SKIN stays that
# lane's item, only the green-bearing mesh is removed here.
EOAT_FAMILY = [
    ('End of All Things soul pet 1', r'records\skills\soulskills\pets\toxeus_eoat_1.dbr'),
    ('End of All Things soul pet 2', r'records\skills\soulskills\pets\toxeus_eoat_2.dbr'),
    ('End of All Things soul pet 3', r'records\skills\soulskills\pets\toxeus_eoat_3.dbr'),
]
TARGETS = DEVOURER_FAMILY + ENSLAVER_FAMILY + EOAT_FAMILY

# ── Records whose mesh must NOT move (Will's design intent, both directions) ──
PROTECTED = [
    ('Greece Toxeus the Murderer (green BY DESIGN - Will)',
     r'records\creature\monster\skeleton\um_toxeus_21.dbr', 'revenantpoison.msh'),
    ("Secret-passage Toxeus the Murderer (Will's clean control)",
     r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr', 'revenantstorm.msh'),
]


def _mesh_of(db, rec):
    v = db.get_field_value(rec, _MESH)
    if isinstance(v, list):
        v = v[0] if v else ''
    return v if isinstance(v, str) else ''


def _basename(path):
    return (path or '').lower().replace('/', '\\').rsplit('\\', 1)[-1]


def _snapshot(db):
    """mesh value of every record that has one -> proves the blast radius."""
    out = {}
    for n in db.record_names():
        f = db.get_fields(n)
        if not f or _MESH not in f:
            continue
        out[n] = _mesh_of(db, n)
    return out


def apply(db, tags):
    before = _snapshot(db)

    missing = [r for _, r in TARGETS if not db.has_record(r)]
    if missing:
        raise SystemExit(
            "[toxeus_mesh_aura] b92 ABORT: target record(s) absent from the db:\n  - "
            + "\n  - ".join(missing))

    # Every target must currently be wearing the GREEN mesh. If one is not, the
    # upstream shape changed and this module must be re-derived, not silently
    # applied on top of a different rig.
    wrong = [(lbl, r, _mesh_of(db, r)) for lbl, r in TARGETS
             if _basename(_mesh_of(db, r)) != GREEN_MESH_BASENAME]
    if wrong:
        raise SystemExit(
            "[toxeus_mesh_aura] b92 ABORT: expected every target to wear "
            f"{GREEN_MESH_BASENAME} before the fix, but:\n  - "
            + "\n  - ".join(f"{lbl} ({r}) wears {m!r}" for lbl, r, m in wrong))

    for _, rec in TARGETS:
        # No explicit dtype: 'mesh' is an existing STRING field on all 15
        # (CLAUDE.md dtype-preservation rule).
        db.set_field(rec, _MESH, CLEAN_MESH)

    # ── Blast-radius proof: ONLY the 15 targets' mesh may have moved ──────────
    after = _snapshot(db)
    changed = sorted(n for n in after if before.get(n) != after.get(n))
    expected = sorted(r for _, r in TARGETS)
    if changed != expected:
        stray = [n for n in changed if n not in expected]
        missed = [n for n in expected if n not in changed]
        raise SystemExit(
            "[toxeus_mesh_aura] b92 ABORT: mesh blast radius is not the 15 targets.\n"
            f"  stray changes: {stray}\n  targets not changed: {missed}")

    fx, pfx, rgb, verdict, _is_green = AURA_MESHES[GREEN_MESH_BASENAME]
    print(f"  [toxeus_mesh_aura] b92: {len(TARGETS)} records off {GREEN_MESH_BASENAME} "
          f"-> GoldenSkeleton01.msh (no CreateEntity, identical 24-bone rig). Removed "
          f"the mesh-attached {verdict} effect {fx} -> {pfx} (RGB peak {rgb}).")
    print("  [toxeus_mesh_aura] untouched by design: um_toxeus_21 (Greece green, "
          "intentional), um_toxeus_99 (Will's control), and every vanilla "
          "RevenantPoison wearer.")


def verify(db, tags):
    """Runs in step 4 on the FINAL merged db. Four recurrences of this bug means
    it gets a machine check, not another report.

    WHAT THIS GATE ASSERTS (deliberately narrow - it encodes the BUG, not an
    unratified art-direction policy):
      * no target wears a mesh whose embedded CreateEntity spawns a GREEN
        effect  -> that is the b92 bug, regressed;
      * no target wears a mesh that has never been byte-audited -> an unknown
        mesh may carry its own effect, so it must be read before it ships;
      * Will's two protected records keep the mesh he ruled for them.
    A non-green audited effect mesh (Storm / Fire / Frost) is ALLOWED to pass:
    it is not this bug, and choosing boss art is Will's call, not the gate's.
    """
    problems = []
    notes = []

    for lbl, rec in TARGETS:
        if not db.has_record(rec):
            problems.append(f"{lbl}: record {rec} MISSING from the final db")
            continue
        m = _mesh_of(db, rec)
        base = _basename(m)
        if base in AURA_MESHES:
            fx, pfx, rgb, verdict, is_green = AURA_MESHES[base]
            if is_green:
                problems.append(
                    f"{lbl} ({rec}): mesh={m!r} - that mesh embeds "
                    f'CreateEntity{{attach="Waist"; entity="{fx}"}} which renders '
                    f"{verdict} ({pfx}, RGB peak {rgb}). The b92 green regressed.")
            else:
                notes.append(
                    f"{lbl} ({rec}) wears {base} - a NON-green mesh-attached "
                    f"effect ({verdict}, {pfx}). Not the b92 bug, allowed, but it "
                    f"is a visible aura: confirm it is intended.")
        elif base not in NO_EFFECT_MESHES:
            problems.append(
                f"{lbl} ({rec}): mesh={m!r} has never been byte-audited for an "
                f"embedded CreateEntity block. Read the .msh out of the shipped "
                f"Creatures.arc and add it to AURA_MESHES or NO_EFFECT_MESHES "
                f"before shipping - an unaudited mesh may carry its own effect.")

    # Will's intent is protected in BOTH directions: we must not have "fixed"
    # the green he deliberately kept, nor disturbed his control.
    for lbl, rec, want in PROTECTED:
        if not db.has_record(rec):
            problems.append(f"PROTECTED {lbl}: record {rec} MISSING")
            continue
        got = _basename(_mesh_of(db, rec))
        if got != want:
            problems.append(
                f"PROTECTED {lbl} ({rec}): mesh basename is {got!r} but must stay "
                f"{want!r} - b92 must not alter this record.")

    if problems:
        raise SystemExit(
            "[toxeus_mesh_aura] b92 VERIFY FAILED (Will 2026-07-27: the green glow "
            "on the Devourer + Enslaver is the RevenantPoison.msh mesh-attached "
            "particle effect, inherited from the green Greece Toxeus):\n  - "
            + "\n  - ".join(problems))

    for n in notes:
        print(f"  [toxeus_mesh_aura] NOTE: {n}")
    print(f"  [toxeus_mesh_aura] verify OK: {len(TARGETS)} Devourer/Enslaver/EoAT "
          f"records carry no green mesh-attached effect; um_toxeus_21 keeps its "
          f"intended green and um_toxeus_99 (control) is untouched.")
