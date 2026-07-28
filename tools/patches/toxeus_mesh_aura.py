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

So the mesh ITSELF hangs a permanent elemental particle aura off the Waist bone
of whatever creature wears it. RevenantPoison.msh hangs RevenantPoison_FX ->
Effects\MonsterFX\Buffs\RevenantPoison.pfx.

*** THIS IS WHY FOUR DATABASE-LEVEL FIXES ALL MISSED IT. ***
b55 (FX fields), b71 (soul->skill->icon->pets chain), b75 (shroud pak swap),
b81 (pet identity/race) are all DB scans. The attachment lives in the MESH FILE.
No .arz scan of any depth can see it. The Devourer carries no charFxPakRunning
shroud at ALL, so no shroud theory could ever have explained his green.

COLOUR PROVEN FROM THE ASSET BYTES, NOT THE NAME (standing law, born from
343_dark_smoke being NAMED dark and RENDERING green)
--------------------------------------------------------------------------
All four Revenant*.pfx are structurally identical - same emitter names ("Dark
Clouds"/"New Dark Clouds"), same textures (Effects\Textures\Organism01.tex +
Organism02.tex), same shaders. They differ ONLY in three numeric keyframe
tracks. Decoding those tracks as R/G/B reproduces all four known element
colours simultaneously, which is what validates the channel assignment:

    variant           R              G              B          => renders
    RevenantFire      1.000          0.518          0.007         orange/red
    RevenantFrost     0.534/0.520    0.824/0.844    1.000         ice blue
    RevenantPoison    0.534/0.520    1.000/0.974    0.591/0.637   *** GREEN ***
    RevenantStorm     0.592/0.604    0.501/0.513    0.695/0.722   blue-violet

RevenantPoison peaks the GREEN channel at 1.0 with red lowest. RevenantStorm
(the control's mesh) puts green at its LOWEST channel. Corroboration from the
shipped roster: every OTHER RevenantPoison.msh wearer in the DB also wears
newskeleton_grean.tex (cm_revenanttainted_16, um_nefesiris_30, um_rotbone_14,
um_toxeus_21) - vanilla pairs that mesh with the green skin on purpose. Our two
bosses are the only wearers with a crimson/charcoal skin: the skin override
landed, the mesh-baked aura did not, so a green cloud sat on a red/black body.

THE FIX
-------
Repoint the mesh to `Creatures\Monster\Skeleton\Skeleton01.msh`:
  * SAME shader + SAME textures as RevenantPoison (StandardSkinned.ssh,
    NewSkeleton_White.tex, GoldenSkeleton01BMP.tex) so each boss's baseTexture
    override keeps landing exactly as it does today;
  * closest geometry of every candidate (94.8% byte-identical body);
  * canonical mesh for anm_skeleton01.dbr - the animation table BOTH bosses
    already use;
  * NO CreateEntity block at all -> no attached aura of any colour;
  * 721 shipped records already wear it, many with a charcoal skin override.
The bosses keep their deliberate identity: the Devourer his crimson skin +
svc_black_poison (R-7), the Enslaver his charcoal skin + the Will-confirmed
BLACK drxshadowcloak smoke (R-10). Nothing green is left to render.

SCOPE - EXACTLY 12 RECORDS, THE DEVOURER + ENSLAVER FAMILIES, NOTHING ELSE
--------------------------------------------------------------------------
NOT TOUCHED, deliberately:
  * um_toxeus_21   - the Greece green-poison Toxeus. His green is INTENTIONAL
                     (Will). verify() asserts he still wears RevenantPoison.
  * um_toxeus_99   - Will's clean secret-passage control. verify() asserts he
                     still wears RevenantStorm.
  * toxeus_eoat_1..3 - the End of All Things pets. Owned by the
                     toxeus_endofallthings lane (R-8, "ash-pale body"); they
                     clone the Devourer pets and inherit the same green aura.
                     This module is registered AFTER that lane precisely so the
                     record-diff stays exactly these 12. REGISTERED AS DEBT.
  * every other RevenantPoison/Fire/Frost wearer in the roster.

ORDERING
--------
Registered after toxeus_suite / toxeus_champion_kits / black_poison /
enslaver_pet_fx / toxeus_endofallthings / toxeus_souls_100 so it is the ratified
FINAL registry writer of `mesh` on these 12 records, and so toxeus_endofallthings
has already cloned the Devourer pets (leaving EoAT provably unchanged).

See docs/reports/b92_green_differential.md.
"""

MODULE_NAME = "Toxeus green mesh-aura removal (b92)"

# ── The mesh-embedded auras, read out of the shipped Creatures.arc bytes ──────
# mesh basename -> (attached EffectEntity, .pfx, proven RGB peak, verdict)
AURA_MESHES = {
    'revenantpoison.msh': (r'Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantPoison.pfx',
                           (0.534, 1.000, 0.591), 'GREEN'),
    'revenantstorm.msh':  (r'Records\Effects\MonsterFX\Buffs\RevenantStorm_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantStorm.pfx',
                           (0.592, 0.501, 0.695), 'blue-violet'),
    'revenantfire.msh':   (r'Records\Effects\MonsterFX\Buffs\RevenantFire_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantFire01.pfx',
                           (1.000, 0.518, 0.007), 'orange/red'),
    'revenantfrost.msh':  (r'Records\Effects\MonsterFX\Buffs\RevenantFrost_FX.dbr',
                           r'Effects\MonsterFX\Buffs\RevenantFrost.pfx',
                           (0.534, 0.824, 1.000), 'ice blue'),
}
# The one mesh in the family that carries NO CreateEntity block.
CLEAN_MESH = r'Creatures\Monster\Skeleton\Skeleton01.msh'
GREEN_MESH_BASENAME = 'revenantpoison.msh'

_MESH = 'mesh'

# ── The 12 records (label, path) ─────────────────────────────────────────────
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
TARGETS = DEVOURER_FAMILY + ENSLAVER_FAMILY

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
        # No explicit dtype: 'mesh' is an existing STRING field on all 12
        # (CLAUDE.md dtype-preservation rule).
        db.set_field(rec, _MESH, CLEAN_MESH)

    # ── Blast-radius proof: ONLY the 12 targets' mesh may have moved ──────────
    after = _snapshot(db)
    changed = sorted(n for n in after if before.get(n) != after.get(n))
    expected = sorted(r for _, r in TARGETS)
    if changed != expected:
        stray = [n for n in changed if n not in expected]
        missed = [n for n in expected if n not in changed]
        raise SystemExit(
            "[toxeus_mesh_aura] b92 ABORT: mesh blast radius is not the 12 targets.\n"
            f"  stray changes: {stray}\n  targets not changed: {missed}")

    fx, pfx, rgb, verdict = AURA_MESHES[GREEN_MESH_BASENAME]
    print(f"  [toxeus_mesh_aura] b92: {len(TARGETS)} records off {GREEN_MESH_BASENAME} "
          f"-> Skeleton01.msh (no CreateEntity). Removed the mesh-attached "
          f"{verdict} aura {fx} -> {pfx} (RGB peak {rgb}).")
    print("  [toxeus_mesh_aura] untouched by design: um_toxeus_21 (Greece green), "
          "um_toxeus_99 (control), toxeus_eoat_1-3 (EoAT lane - registered debt).")


def verify(db, tags):
    """Runs in step 4 on the FINAL merged db. Four recurrences of this bug means
    it gets a machine check, not another report."""
    problems = []

    for lbl, rec in TARGETS:
        if not db.has_record(rec):
            problems.append(f"{lbl}: record {rec} MISSING from the final db")
            continue
        m = _mesh_of(db, rec)
        base = _basename(m)
        if base in AURA_MESHES:
            fx, pfx, rgb, verdict = AURA_MESHES[base]
            problems.append(
                f"{lbl} ({rec}): mesh={m!r} - that mesh embeds "
                f'CreateEntity{{attach="Waist"; entity="{fx}"}} which renders '
                f"{verdict} ({pfx}, RGB peak {rgb}). The b92 green regressed.")
        elif base != _basename(CLEAN_MESH):
            problems.append(
                f"{lbl} ({rec}): mesh={m!r} is neither the b92 clean mesh "
                f"{CLEAN_MESH!r} nor a known aura mesh - re-derive before shipping "
                f"(an unaudited mesh may carry its own CreateEntity aura).")

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
            "Waist aura, inherited from the green Greece Toxeus):\n  - "
            + "\n  - ".join(problems))

    print(f"  [toxeus_mesh_aura] verify OK: {len(TARGETS)} Devourer/Enslaver records "
          f"carry no aura-bearing mesh; um_toxeus_21 keeps its intended green and "
          f"um_toxeus_99 (control) is untouched.")
