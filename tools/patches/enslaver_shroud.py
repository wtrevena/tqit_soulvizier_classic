r"""enslaver_shroud - THE ENSLAVER'S BLACK SHADOW SHROUD, ON THE ONE MECHANISM
THAT HAS A CONFIRMED RENDERING EXEMPLAR (b98 R-95, b102 R-102, b93 R-250,
b99 R-255, **b101 R-257**).

WILL, verbatim, the FIFTH filing of the same sentence (2026-08-16, with a
screenshot: the Enslaver summoned at Hathor Basin on DEV, post-b99/b100 arz,
standing out of combat, ZERO smoke):

> "toxeus the murderer enslaver of souls summoned pets (when i summon them from
>  their souls) still do not have the black smoke around them"

--------------------------------------------------------------------------------
R-257 - THE NEW STANDARD, AND WHY IT HAD TO CHANGE
--------------------------------------------------------------------------------
Four rounds of this request were fixed in the `.dbr` FIELD layer. Every one of
them verified itself at the record level. Every one of them failed in game:

| round | what it wired | why it was believed | what actually happened |
|---|---|---|---|
| b39/b55/b55r2/b92 | `charFxPakRunningNames`, weapon-bone paks | "renders while running" | never rendered; smoke would have come off his fists anyway |
| b93 (R-250) | `skillName19` / `skillName18` | "the template reaches 23" | slots `MonsterSkillManager.tpl` does not declare - read by nobody |
| b99 (R-255) | `initialSkillName` + `buffSelfSkillName` | 838 Monsters + 90 Pets use them | declared, byte-verified, gate-verified - and STILL nothing on screen |

**The lesson this module now embodies: a channel being declared in the template
does NOT mean the pet controller executes it, or that a CharFxPak attaches on
this rig.** A record-level proof is not a rendering proof, and this request has
now cost five filings' worth of evidence for that one sentence.

So R-257 raises the bar: the fix must use a mechanism with a SHIPPING RENDERING
EXEMPLAR - a specific creature that VISIBLY displays a persistent shroud
delivered by that exact mechanism - and must then replicate it byte for byte.

THE CENSUS THAT PICKED THE MECHANISM (measured, `Toolset\Templates.arc` +
the 74,013-record base `database.arz` + 591 distinct vanilla creature meshes):

  (a) MESH-COMPILED FX (`CreateEntity` in the `.msh`)   -> **PASSES**
      Exemplar: `um_enslaver_marauder_99` + `enslaver_marauder_1/2/3` on
      `ShadowStalker.msh`. WILL CONFIRMED IT BY EYE (R-102 fourth amendment,
      verbatim: *"yes the demons that he summons have the proper black shroud
      and they dont have any green"*), and those four records carry
      `initialSkillName = buffSelfSkillName = None`, so nothing but the mesh can
      be producing it. 28 vanilla records wear that rig; 66 of 591 vanilla
      creature meshes use the mechanism. Decisively: **every** vanilla PET with a
      persistent ambient aura is mesh-driven with empty always-on fields
      (Ancestral Warriors, the Spirit Outsider, Storm Wisps, Spirit Ward, Battle
      Standard) - any player who has taken Warfare or Spirit has watched one
      stand still, out of combat, glowing.

  (b) `charFxPakRunningNames`-class fields                -> DEAD, no exemplar can exist.
      Declared in ZERO of the 566 shipped templates and carried by ZERO of the
      74,013 base records. The only 14 carriers on earth are this mod's own
      DRX-inherited records, 8 of them this family. R-95's "renders while
      running" had no evidence behind it; the running smoke was the marauders' mesh.

  (c) SKILL-GRANTED FX ON AN ALWAYS-ON CHANNEL (the b99 route) -> NO PET EXEMPLAR.
      Across all 341 vanilla Pets, `initialSkillName` reaches a
      `Skill_BuffSelfToggled` **zero** times and a `charFxPakSelfNames` **zero**
      times; `buffSelfSkillName` reaches a `charFxPakSelfNames` 20 times, all of
      them Neidan Terracotta pets on a WEAPON-HAND pak. The exact b99 shape - Pet
      + always-on channel + `Skill_BuffSelfToggled` + body-attach CharFxPak -
      occurs ZERO times in shipping data. R-255's ruling table ("838 Monsters +
      90 Pets; 153 point it at a Skill_BuffSelfToggled") conflated the two pools:
      all 153 are MONSTERS. That mis-scoped statistic is round 5's instrument
      error and is logged in `docs/MISTAKES.md`.

  (d) EFFECTENTITY FIELDS ON THE RECORD                   -> DEAD, the engine declares none.
      The full 1,923-field `Pet.tpl` closure carries exactly five
      EffectEntity-shaped fields and every one is event-scoped (`spawnEffect`,
      `prespawnEffect`, `deathEffect`, `dissolveEffect`, `levelUpFx`). There is no
      ambient/idle effect field anywhere on Character/Actor/Monster/Pet. **That
      absence is exactly why the base game compiles ambient auras into meshes.**

And the specific asset settles it: `ShadowStalker_Smoke.dbr` is referenced 13
times in the entire base game and every one is a `deathEffect`. It is named by no
CharFxPak anywhere. Its only persistent rendering, anywhere, is the block
compiled into `ShadowStalker.msh`.

--------------------------------------------------------------------------------
R-257 - THE FIX: HIS OWN RIG, CARRYING THE DEMONS' OWN BLOCK
--------------------------------------------------------------------------------
`tools/build_shroud_rig.py` authors ONE new asset:

    Creatures\Monster\Skeleton\svc_enslaver_shroudrig01.msh
      = base `SkeletonGrayBlack01New.msh` (his current rig, R-102's deliberate
        anti-green choice - his silhouette is NOT traded away)
      + the 115 bytes read VERBATIM off the end of `ShadowStalker.msh`:
            CreateEntity { attach = "SpecialHit01";
                           entity = "Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr" }
      + that one chunk-length u32 bumped by 115.

A `.msh` is a self-describing chunk chain with no global offset table (both
binaries walk to EOF-exact in 9 chunks; the last is the CRLF text section), so
append-and-bump is the format's own edit. `build_shroud_rig.verify_rig()`
re-derives all of it every build (A1..A8), including that the rig-name table is
IDENTICAL to the donor's 31 names - which is what makes the ANIMATION surface
provably untouched, the risk R-102's fourth amendment names as the real one.

It ships in the mod's own `Resources\Creatures.arc` under a NET-NEW name (that
archive already carries 288 net-new entries including two `.msh`, and shadows
ZERO base entries - the property that keeps every base creature resolving).

`champion_mesh` remains the SINGLE writer of `mesh`; it imports `SHROUD_RIG`
from this module so the asset and the wearer can never drift apart (the
`thrown_restore` -> `thrown_anim_rig` precedent).

Result: all 8 household members now smoke by the SAME mechanism, through the SAME
attach point, with the SAME entity reference and a byte-identical block, as the
marauders Will has already confirmed smoke in play.

--------------------------------------------------------------------------------
R-257 - WHAT IS RETIRED, AND WHY LEAVING IT WOULD BE WORSE THAN USELESS
--------------------------------------------------------------------------------
The b99 FIELD route is REMOVED, not left as a harmless belt-and-braces:

  1. It is the exact shape five filings have taught us reads as "wired" and is
     not. Leaving it means the next reader greps the arz, finds the shroud on two
     declared always-on channels, and concludes the feature works.
  2. It is a DOUBLING HAZARD by this module's own law. b99's `apply()` already
     refused to add the pak on top of a MESH-route member because "adding our
     emitter on top would double a shroud the demons wear once". Once every
     member is MESH, keeping FIELD is exactly that, on every member. Will asked
     for *the same* shroud his demons have, not a denser one.

So `apply()` now RETIRES, on every household member:
  * `initialSkillName` / `buffSelfSkillName` naming OUR shroud -> the field SLOT
    is deleted (absence, not `''` - see `_del_field`), restoring the pre-b99 state;
  * an `svc_alwayson_*` controller CLONE -> the record goes back to the SHARED
    original it was cloned from, so no family member runs a private AI record for
    a retired reason.
And it stops AUTHORING `svc_enslaver_shroud` / `_charfxpak` / `_fx` and the
controller clones at all: the build is COLD from the upstream `.arz`, so in the
shipped database those records simply never come into existence. The retirement
code exists for the re-run-over-a-built-arz case (`--negtest`, static dry-runs),
where they are already present.

RETIREMENT PROTOCOL, checked: R-250 and R-255 are the only rulings that name
those records, and R-257 supersedes exactly that part of them. `charFxPakRunningNames`
is still KEPT untouched on every surface (ADD, never take away - the demons carry
it too), and no kit skill is dropped.

--------------------------------------------------------------------------------
R-257 VET ROUND 2 - THE ASSET IS A PRECONDITION OF THE BUILD, NOT A DEPLOY CHORE
--------------------------------------------------------------------------------
Round 1 verified its RECORDS and its ASSET and never ran the build that has to
assemble them. The cold build was DEAD: the mod `Creatures.arc` was staged AFTER
the `.arz` build, and THREE fail-loud gates inside that build read it - this
module's M2, `validate_render_chain` A9 (a mod-authored pet with an unresolvable
`mesh` FAILS the build) and `champion_mesh.verify()`. Worse, the bootstrap caught
the non-zero exit and quietly substituted the RAW upstream database.

Three things changed, and the third is the one that mattered most:

  * `build_svc_database` declares a SHIPPING ANCHOR (`output.parent.parent /
    'Resources'`) and M2 asks THAT archive. Round 1 asked every
    `mesh_assets.mod_resource_dirs()` hit - a SEARCH PATH - so a stale scratch
    tree could red-lock a build whose own shipped archive was perfect.
  * `bootstrap_working_mod.ps1` stages the archive in Step 0e, before Step 1, and
    a fired gate now STOPS the bootstrap.
  * `build_svc_database._preflight_mod_creatures_arc()` stages it too, because
    THE SHIP LANE DRIVES THAT SCRIPT DIRECTLY AND HAS NEVER RUN THE BOOTSTRAP.
    A fix confined to the bootstrap would have passed every static gate and failed
    the very next ship.

`--negtest` grew from 29 to 37, and six of those run the REAL `rig_asset_state()`
against REAL archives written to a temp tree. Round 1 stubbed that function in
ALL 29 of its plants, which is exactly why neither P0 was visible to it - the
blind spot `docs/MISTAKES.md` had logged for R-256 one day earlier.

Re-runnable proof, five ways: `py tools/debug/r257_cold_order_control.py`.

--------------------------------------------------------------------------------
WHAT THIS MODULE CLAIMS, AND WHAT IT DOES NOT
--------------------------------------------------------------------------------
IT DOES NOT CLAIM THE SHROUD RENDERS. Nobody has seen this build.

What it claims - and what no previous round could - is narrower and checkable:
the four records that had no shroud now reach the screen by the SAME MECHANISM,
through the SAME attach point, with the SAME entity reference, carrying a
BYTE-IDENTICAL block, as four records Will has personally confirmed smoke in
play. The residual risk is no longer "does this channel render?" (it does, on
the marauders, in his own words) but only "does a mod-shipped copy of a base rig
load?" - and 1,105 of this mod's Monster/Pet records already resolve their mesh
out of a mod archive today, the Devourer's blood demons among them.

WHAT THIS MODULE DOES NOT TOUCH (reported, not silently deferred)
  * **The Devourer of Blood** still has no body shroud. Will did not ask for it,
    his demons are BLOOD demons with no shadow shroud to copy, and crimson is his
    design. `BL-R250-DEBT-2`, a QUESTION for Will.
  * **The Endless Hunt** wears `SkeletonRumorBoss.msh` (R-247.5a) with the base
    game's own Boss Aura. Different champion, different ruling.
  * **Stats, skills, loot, textures.** Not this lane's.
"""

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))   # tools/ on path

MODULE_NAME = "Enslaver black shadow shroud, mesh-compiled (R-95/R-102/R-250/R-255/R-257)"

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

# ── THE EXEMPLAR: the only confirmed-rendering instance of this effect ───────
# `um_enslaver_marauder_99.mesh` = ShadowStalker.msh, whose binary ends in
#   CreateEntity { attach = "SpecialHit01"; entity = "<_DEMON_FX_REF>" }
# and that base-game EffectEntity plays <_DEMON_PFX>. verify() re-derives every
# one of these from the binaries each build, so "the same one that his demon
# summon guys have" stays a CHECKED claim rather than a comment.
_DEMON_FX_REF = r'records\effects\monsterfx\shadowstalker_smoke.dbr'
_DEMON_PFX = r'Effects\MonsterFX\ShadowStalker_Smoke01.pfx'
_DEMON_MESH_ATTACH = 'SpecialHit01'
# A name on the demons' rig that his rig does NOT declare. Kept as the concrete
# example of the silent-nothing trap, and exercised as a negtest plant.
_DEMON_ONLY_ATTACH = 'Smoke02'

# ── R-257: THE ASSET THIS LANE AUTHORS, AND ITS TWO SOURCES ─────────────────
# Imported by `champion_mesh` (the single writer of `mesh`) so the rig and its
# wearers can never drift - the thrown_restore -> thrown_anim_rig precedent.
import build_shroud_rig as _rig                                  # noqa: E402

SHROUD_RIG = _rig.SHROUD_RIG                # what the Enslaver family now wears
SHROUD_RIG_ENTRY = _rig.SHROUD_RIG_ENTRY    # its entry inside the mod Creatures.arc
DONOR_RIG = _rig.DONOR_MESH                 # R-102's FX-free skeleton (his silhouette)
EXEMPLAR_RIG = _rig.EXEMPLAR_MESH           # the demons' rig, Will-confirmed

# ── the running channel he and his demons already share (kept, never removed) ─
_SHADOWCLOAK_PAK = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr'

# ── RETIRED BY R-257 (authored by R-250, wired by R-255, rendered by nothing) ─
# These records are NO LONGER AUTHORED. They are named here so `apply()` can
# unwire them when this module is re-run over an arz that already carries them
# (a --negtest baseline, a static dry-run), and so verify() can assert that the
# shipped database references them from NOWHERE.
_SHROUD = r'records\skills\monster skills\buff_self\svc_enslaver_shroud.dbr'
_SHROUD_PAK = r'records\skills\monster skills\buff_self\svc_enslaver_shroud_charfxpak.dbr'
_SHROUD_FX = r'records\skills\monster skills\buff_self\svc_enslaver_shroud_fx.dbr'
_RETIRED_RECORDS = (_SHROUD, _SHROUD_PAK, _SHROUD_FX)
_CTRL_PREFIX = 'svc_alwayson_'

# R-255's codified list of the two channels the skill manager reads without
# combat-AI selection. Other lanes cite it (see lookout_uber's V14). R-257 keeps
# the constant and INVERTS its use: the family must now be CLEAR of our shroud on
# both, because the smoke comes from the rig instead.
_ALWAYS_ON_FIELDS = ('initialSkillName', 'buffSelfSkillName')

# R-255's engine ceiling. Nothing in this module writes a kit slot any more, but
# the gate still REPORTS skills parked above it (BL-R255-DEBT-1) and still fails
# loud if OUR shroud ever reappears up there (the b93 defect).
_ENGINE_SKILL_SLOT_MAX = 17

# every field that can name a pet-spawning skill, so the family closure is walked
# rather than listed (a 4th tier, a new escort or a new pet-of-pet joins by
# itself - the b98 failure mode was a roster that could go stale in silence)
_SPAWN_FIELDS = ('specialAttackSkillName', 'specialAttack2SkillName',
                 'specialAttack3SkillName', 'specialAttack4SkillName',
                 'specialAttack5SkillName', 'initialSkillName')
_FAMILY_MAX_DEPTH = 4

# Used ONLY on a loud archive-unreachable downgrade, never as the primary answer.
# R-257 adds our own rig beside the demons'; both are derived from the binary
# whenever the archives are readable.
_PINNED_SMOKE_RIGS = (r'creatures\monster\shadowstalker\shadowstalker.msh',
                      SHROUD_RIG.replace('/', '\\').lower())

# ── TEST HOOKS ──────────────────────────────────────────────────────────────
# The asset-level gates read `.msh` binaries out of the shipped `.arc`s. The
# negative test cannot ship archives, so it injects the answers instead. In a
# real build every one stays None and the gates read the real assets (or announce
# a loud DOWNGRADE - never a silent pass).
_RIG_NAMES_OVERRIDE = None      # {mesh_ref_lower: set(bone + AttachPoint names)}
_DEMON_FX_OVERRIDE = None       # [entity refs embedded in the demons' mesh]
_DEMON_ATTACH_OVERRIDE = None   # the attach name in the demons' CreateEntity
_MESH_SMOKE_OVERRIDE = None     # {mesh_ref_lower: (attach, entity) or None}
_RIG_ASSET_OVERRIDE = None      # ('PASS'|'FAIL'|'SKIP', detail) for the arc-staging arm


def _require_gates():
    r"""True when the build demands that an UNAVAILABLE gate be a FAILURE.

    R-257 makes this matter more than it did: the two arms that can go SKIP here
    (the rig-asset arm and the per-member MESH route) are the ONLY things standing
    between a shipped arz and four records naming a mesh that resolves nowhere -
    an INVISIBLE boss. In a real ship the archives are always reachable and
    `SVC_REQUIRE_GATES=1` is always set (see every build9x gate record), so a SKIP
    there means the environment is wrong, not that the question is unanswerable.
    Outside a ship (a bare worktree with no staged Resources) the SKIP stays a loud
    announced downgrade, exactly as the rest of this module has always behaved.
    """
    import os
    return os.environ.get('SVC_REQUIRE_GATES', '') not in ('', '0', 'false', 'False')


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
    r"""(status, set(CASEFOLDED rig names)) out of a mesh binary: BOTH namespaces.

    status PASS / SKIP. SKIP means the archives are not reachable from this
    working tree; the caller ANNOUNCES that rather than counting it as a pass.

    b104 round 2, and the reason this delegates instead of scanning: round 1
    scanned NUL-terminated strings only. Bone-table names are NUL-terminated;
    ATTACHPOINT names are not, they live in a CRLF text block. The reader was
    structurally blind to the class of name it was asked about, and its false
    answer became design law in `docs/WILL_RULINGS.md`. `rig_names_of()` reads
    the bone table UNION the AttachPoint table, casefolded because the shipped DB
    addresses these tables off-case (`Bone_spine01`, `Specialhit03`).
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


def _mesh_fx(mesh_ref):
    """(status, [(attach, entity)]) - every CreateEntity block a rig compiles in.

    This is THE reader of the whole R-257 design: it answers, from the binary,
    "does this creature smoke, and where does it hang it?". SKIP means the
    archives are unreachable; the caller announces the downgrade.
    """
    if not mesh_ref:
        return ('PASS', [])
    if _MESH_SMOKE_OVERRIDE is not None:
        got = _MESH_SMOKE_OVERRIDE.get(_norm(mesh_ref))
        return ('PASS', list(got or [])) if _norm(mesh_ref) in _MESH_SMOKE_OVERRIDE \
            else ('SKIP', [])
    try:
        import mesh_assets
        if not mesh_assets.arcs_available():
            return ('SKIP', [])
        data, _arc = mesh_assets.read_asset(str(mesh_ref))
        if not data:
            return ('SKIP', [])
        return ('PASS', mesh_assets.embedded_fx_attachments_of(data))
    except Exception:                                        # noqa: BLE001
        return ('SKIP', [])


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
    st, blocks = _mesh_fx(mesh)
    if st != 'PASS':
        return ('SKIP', None)
    want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
    for attach, entity in blocks:
        if entity and str(entity).replace('/', '\\').rsplit('\\', 1)[-1].lower() == want:
            return ('PASS', attach)
    return ('PASS', None)


def _demon_embedded_fx(db):
    """(status, [effect refs]) compiled into the MARAUDERS' mesh.

    The provenance anchor for the whole module: the shroud Will pointed at is not
    a field, it is this CreateEntity block. Deriving it every build is what makes
    "the same one that his demon summon guys have" a checked claim.
    """
    if _DEMON_FX_OVERRIDE is not None:
        return ('PASS', list(_DEMON_FX_OVERRIDE))
    mesh = _gv1(db, _MARAUDER, 'mesh')
    if not mesh:
        return ('FAIL', [])
    st, blocks = _mesh_fx(mesh)
    if st != 'PASS':
        return ('SKIP', [])
    return ('PASS', [e for _a, e in blocks if e])


def pfx_resolution(pfx=_DEMON_PFX):
    """A9-STYLE RENDER RESOLUTION: does the particle file actually SHIP?

    Resolution is not rendering (the A9/D5 lesson). The chain can be perfect and
    he still smokes nothing if the `.pfx` is in no shipped archive. Walks the
    mod's staged `Resources` first, then the game install, which is the order the
    engine uses - this particular file is a BASE-GAME asset, so a mod-only search
    would report a false failure.
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


def shipping_creatures_arcs():
    r"""(kind, [paths]) - the `Creatures.arc` THIS BUILD SHIPS. Never a glob sweep.

    ROUND 2 OF THIS LANE EXISTS BECAUSE ROUND 1 ASKED THE WRONG ADDRESS. It
    demanded the rig in EVERY `mesh_assets.mod_resource_dirs()` hit, and that list
    is a SEARCH PATH: `work/*/Resources` plus `local/*/Resources`, six rows in the
    ship checkout. Any stale tree under `local/` could therefore red a build whose
    own shipped archive was perfect - a permanent ship-blocker nobody could clear
    by rebuilding the right file. (The measured six turned out to be ONE archive
    seen through five det-2x junctions, but the defect class is real and the
    address was wrong either way.)

    The right address is the anchor `validate_render_chain` has always used and
    that `build_svc_database` now declares once: the `Resources` dir beside the
    `.arz` being written.

      kind 'ANCHORED'   - the build declared its anchor; that ONE archive answers.
      kind 'STAGED'     - no anchor (a CLI dry-run): fall back to the staged deploy
                          source `work/*/Resources` ONLY. `local/*` is scratch
                          output and ships nothing, so it can never gate a build.
      kind 'NO-ANCHOR-DIR' - an anchor was declared and its dir does not exist:
                          a scratch layout, honestly unanswerable, never a pass.
    """
    from pathlib import Path as _P
    import mesh_assets
    anchor = mesh_assets.shipping_resource_dir()
    if anchor is not None:
        if not anchor.is_dir():
            return ('NO-ANCHOR-DIR', [anchor / 'Creatures.arc'])
        return ('ANCHORED', [anchor / 'Creatures.arc'])
    return ('STAGED', sorted(d / 'Creatures.arc' for d in _P('.').glob('work/*/Resources')
                             if d.is_dir()))


def rig_asset_state():
    r"""(status, detail) for the authored rig - M1 derivability + M2 staging.

    M1 ALWAYS runs: the rig is rebuilt in memory from the two BASE binaries and
    put through `build_shroud_rig.verify_rig()`. It has no dependency on staging
    order, so every build proves the asset is derivable and correct.

    M2 asks the SHIPPING archive (see `shipping_creatures_arcs`) whether it carries
    the entry, byte-identical to the derived bytes. This is the arm that enforces
    the R-257 BUILD-TIME PRECONDITION: the Enslaver family's `mesh` resolves ONLY
    out of the mod archive, so an `.arz` built beside an archive without the rig
    would ship four records pointing at a mesh that resolves NOWHERE - an INVISIBLE
    boss, a far worse regression than the missing smoke this lane fixes. Two more
    build gates (`validate_render_chain` A9 and `champion_mesh.verify`) fail on the
    same state, which is why `bootstrap_working_mod.ps1` stages the archive in
    Step 0e, BEFORE the database build, and not at deploy time.
    """
    if _RIG_ASSET_OVERRIDE is not None:
        return _RIG_ASSET_OVERRIDE
    try:
        want = _rig.rig_bytes_checked()
    except SystemExit as e:                                  # noqa: BLE001
        return ('FAIL', 'the rig is not derivable from the base binaries: %s' % e)
    except Exception as e:                                   # noqa: BLE001
        return ('SKIP', 'the base archives are not reachable (%s)' % e)

    try:
        from arc_patcher import ArcArchive
        kind, staged = shipping_creatures_arcs()
    except Exception as e:                                   # noqa: BLE001
        return ('SKIP', 'M1 PASS (%d bytes derived + verified); M2 not run (%s)'
                % (len(want), e))

    if kind == 'NO-ANCHOR-DIR':
        return ('SKIP', 'M1 PASS (%d bytes derived + verified); M2 NOT RUN - this '
                        'build declared %s as its shipping Resources dir and that '
                        'directory does not exist (a scratch layout), so the '
                        'BUILD-TIME PRECONDITION is unproven here'
                % (len(want), staged[0].parent))
    if not staged:
        return ('SKIP', 'M1 PASS (%d bytes derived + verified); M2 NOT RUN - no mod '
                        'Creatures.arc reachable from this working tree, so the '
                        'BUILD-TIME PRECONDITION is unproven here and must be proven '
                        'in the build that ships' % len(want))
    for p in staged:
        if not p.exists():
            return ('FAIL', 'the shipping mod archive %s DOES NOT EXIST. The Enslaver '
                            'family names %r, which ships only from that archive, so '
                            'this arz would give them NO MESH AT ALL. Build it BEFORE '
                            'the database (bootstrap Step 0e): '
                            'py tools/build_creatures_dye_skins_arc.py --out %s'
                    % (p, SHROUD_RIG_ENTRY, p))
        got = _rig.entry_in(ArcArchive.from_file(p))
        if got is None:
            return ('FAIL', 'the shipping mod archive %s does NOT carry %r. The '
                            'Enslaver family names that mesh, so shipping this arz '
                            'beside this arc gives them NO MESH AT ALL. Build it '
                            'BEFORE the database (bootstrap Step 0e): '
                            'py tools/build_creatures_dye_skins_arc.py --out %s'
                    % (p, SHROUD_RIG_ENTRY, p))
        if got != want:
            return ('FAIL', 'the staged %r in %s is %d bytes, the derived rig is %d - '
                            'the shipped asset is not the one this build verified'
                    % (SHROUD_RIG_ENTRY, p, len(got), len(want)))
    return ('PASS', 'M1+M2 [%s]: %s derived from %s + the exemplar block (%d bytes, '
                    'A1..A8 verified) and byte-identical in %s'
            % (kind, SHROUD_RIG_ENTRY, DONOR_RIG.rsplit('\\', 1)[-1], len(want),
               ', '.join(str(p) for p in staged)))


# ── ROSTER (unchanged from R-255: derived, never listed) ────────────────────

def _pet_tiers(db):
    """Every Enslaver pet tier, READ from the summon skill's spawnObjects.

    b98 wired the shroud to the monster only, so the three tiers Will actually
    summons never got it and he correctly said the request was "still not
    implemented". Deriving the tiers is what makes that failure unrepeatable.
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

    R-255. The wild boss raises his escorts through `svc_enslaver_summonmarauders`
    and the SUMMONED Enslaver raises pet-of-pet marauders through
    `svc_enslaver_petmarauders`; walking them finds the whole household without a
    list to go stale.
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
    """W1: the WHOLE household, walked - boss + escorts + pet tiers + pet-of-pet."""
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
    """The name tags the walked family wears - derived, never listed."""
    tags = set(_NAME_TAGS)
    for r in members:
        d = _gv1(db, r, 'description')
        if d and str(d).strip():
            tags.add(str(d).lower())
    return tags


def _by_name_tag(db, tags=None):
    """W2: every Monster/Pet record described by one of the family's name tags.

    Catches a build-time DIFFICULTY CLONE, which the summon chain cannot see.
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


# ── THE ONE ROUTE, DERIVED FROM THE RIG BINARY ──────────────────────────────

def mesh_route(db, rec):
    """(status, ok, detail) - does this member's rig compile in the demons' smoke?

    THE proven channel, and after R-257 the ONLY one. Derived from the `.msh`
    binary every build: the day a member is moved onto an FX-free rig (exactly
    what `champion_mesh` once did to the Enslaver, which is how his last always-on
    emitter vanished) it stops satisfying this and the build fails.
    """
    mesh = _gv1(db, rec, 'mesh')
    if not mesh:
        return ('PASS', False, 'no mesh field at all')
    st, blocks = _mesh_fx(mesh)
    if st == 'SKIP':
        pinned = _norm(mesh) in {_norm(m) for m in _PINNED_SMOKE_RIGS}
        return ('SKIP', pinned, '%s (pinned smoke-rig list)' % mesh)
    want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
    for attach, entity in blocks:
        stem = str(entity or '').replace('/', '\\').rsplit('\\', 1)[-1].lower()
        if stem == want and str(attach or '').lower() == _DEMON_MESH_ATTACH.lower():
            return ('PASS', True, '%s -> CreateEntity{attach=%r; entity=%r}'
                    % (mesh, attach, entity))
    return ('PASS', False, '%s embeds %r' % (mesh, blocks or 'NOTHING'))


def _field_route_residue(db, rec):
    """Which always-on channels still name OUR retired shroud (should be none)."""
    return [f for f in _ALWAYS_ON_FIELDS if _norm(_gv1(db, rec, f)) == _norm(_SHROUD)]


def _is_ours_ctrl(ctrl):
    return str(ctrl).rsplit('\\', 1)[-1].lower().startswith(_CTRL_PREFIX)


def _shared_original(ctrl):
    """The record an `svc_alwayson_*` clone was cloned FROM (name-derived)."""
    head, _sep, base = str(ctrl).rpartition('\\')
    return '%s\\%s' % (head, base[len(_CTRL_PREFIX):]) if base.lower().startswith(_CTRL_PREFIX) \
        else str(ctrl)


def _dead_slots(db, rec):
    """{slot: skill} for every kit slot ABOVE the engine's declared ceiling.

    Reported for the whole family; only OUR OWN shroud is ever removed from one.
    Another lane's skill parked up there is that lane's ruling to unwind
    (RETIREMENT PROTOCOL, BL-R255-DEBT-1).
    """
    return {i: s for i, s in _skill_slots(db, rec).items()
            if i > _ENGINE_SKILL_SLOT_MAX}


def _retire(db, rec):
    """R-257: unwire every b99/b93 belief-channel from one household member.

    Returns (retired_fields, reverted_controller_or_None, retired_dead_slots).

    On a COLD build (what ships) this finds nothing to do, because the records it
    unwires are no longer authored at all. It exists for the re-run-over-a-built-
    arz case, which is what `--negtest` and every static dry-run actually are.
    """
    fields = []
    for f in _ALWAYS_ON_FIELDS:
        if _norm(_gv1(db, rec, f)) == _norm(_SHROUD):
            _del_field(db, rec, f)
            fields.append(f)

    slots = []
    for i, sk in sorted(_skill_slots(db, rec).items()):
        if i <= _ENGINE_SKILL_SLOT_MAX or _norm(sk) != _norm(_SHROUD):
            continue
        _del_field(db, rec, 'skillName%d' % i)
        _del_field(db, rec, 'skillLevel%d' % i)
        slots.append(i)

    ctrl = _gv1(db, rec, 'controller')
    reverted = None
    if ctrl and _is_ours_ctrl(ctrl):
        orig = _shared_original(str(ctrl))
        if db.has_record(orig):
            db.set_field(rec, 'controller', orig)
            reverted = orig
    if fields or slots or reverted:
        db._modified.add(rec)
    return fields, reverted, slots


def apply(db, tags):
    print("\n=== [enslaver_shroud] R-257: THE SHROUD MOVES TO THE ONE MECHANISM "
          "WITH A CONFIRMED RENDERING EXEMPLAR ===")
    _require(db, _ENSLAVER, _MARAUDER)
    tiers = _pet_tiers(db)
    if not tiers:
        raise SystemExit(
            "[enslaver_shroud] %s spawns no resolvable pet, so the tier roster is "
            "EMPTY. That is the exact b98 failure this module exists to prevent "
            "(shroud on the monster, nothing on what Will summons) - stop rather "
            "than ship a monster-only shroud again." % _ENSLAVER_SUMMON)

    # The asset must be derivable BEFORE anything is repointed at it. Repointing
    # `mesh` at a rig that cannot be built is an INVISIBLE boss, which is a much
    # worse regression than the missing smoke this lane is fixing.
    st, detail = rig_asset_state()
    if st == 'FAIL':
        raise SystemExit("[enslaver_shroud] THE RIG ASSET IS NOT SHIPPABLE: %s" % detail)
    print("  RIG    %s\n         %s" % (SHROUD_RIG, detail))
    if st == 'SKIP':
        print("         ^ DOWNGRADED, not a pass - see the BUILD-TIME PRECONDITION note")

    roster = shroud_roster(db)
    n_retired = 0
    for rec in roster:
        fields, reverted, slots = _retire(db, rec)
        if fields or reverted or slots:
            n_retired += 1
            bits = []
            if fields:
                bits.append('unwired %s' % '+'.join(fields))
            if slots:
                bits.append('retired dead slot(s) %r' % slots)
            if reverted:
                bits.append('controller -> %s' % reverted.rsplit('\\', 1)[-1])
            print("  RETIRE %-62s %s" % (rec, '; '.join(bits)))

    # `mesh` itself is written by champion_mesh (R-102's single-writer law), which
    # imports SHROUD_RIG from here. This module reports what it EXPECTS to see and
    # verify() - which runs post-finalization, after champion_mesh - proves it.
    print("  %d household member(s); %d had a b99/b93 belief-channel retired. The "
          "shroud is no longer a field on ANY of them: it is compiled into the rig, "
          "the way the marauders Will confirmed by eye have always carried it. "
          "`mesh` is written by champion_mesh, which imports SHROUD_RIG from this "
          "module; verify() proves the whole household afterwards."
          % (len(roster), n_retired))
    print("=== [enslaver_shroud] done (verify() runs post-finalization) ===\n")
    return tags


# ── GATE ────────────────────────────────────────────────────────────────────

def verify(db, tags=None):
    problems = []
    notes = []

    # ── M1/M2: THE AUTHORED ASSET ──────────────────────────────────────────
    st, detail = rig_asset_state()
    if st == 'FAIL':
        problems.append("RIG ASSET: %s" % detail)
    elif st == 'SKIP':
        if _require_gates():
            problems.append(
                "RIG ASSET UNAVAILABLE under SVC_REQUIRE_GATES: %s. This is the arm "
                "that stops a ship from putting four records on a mesh that resolves "
                "nowhere; it may not be skipped in a build that ships." % detail)
        else:
            notes.append("RIG ASSET DOWNGRADED (not a pass): %s" % detail)
    else:
        notes.append("RIG ASSET PASS: %s" % detail)

    # ── PROVENANCE: the exemplar still smokes, and still smokes THAT ────────
    st, refs = _demon_embedded_fx(db)
    if st == 'FAIL':
        problems.append("the marauders (%s) have no mesh, so the shroud's provenance "
                        "cannot be derived at all" % _MARAUDER)
    elif st == 'SKIP':
        notes.append("DEMON-MESH PROVENANCE DOWNGRADED (not a pass): the .arc archives "
                     "are not reachable from this working tree")
    else:
        stems = [str(r).replace('/', '\\').rsplit('\\', 1)[-1].lower() for r in refs]
        want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
        if want not in stems:
            problems.append(
                "PROVENANCE: the marauders' mesh no longer embeds %s (it embeds %r). "
                "The whole premise of this module is that THAT is the shroud Will "
                "confirmed by eye; re-derive rather than letting the two drift apart."
                % (want, refs))

    st, demon_attach = _demon_mesh_attach(db)
    if st == 'FAIL':
        problems.append("the marauders (%s) have no mesh, so the attach point we copy "
                        "cannot be derived at all" % _MARAUDER)
    elif st == 'SKIP':
        notes.append("DEMON-ATTACH PARITY DOWNGRADED (not a pass): pinned %r was used"
                     % _DEMON_MESH_ATTACH)
    elif not demon_attach:
        problems.append("the marauders' mesh embeds %s with no readable attach point, "
                        "so 'the same one that his demon summon guys have' cannot be "
                        "matched by placement." % _DEMON_FX_REF)
    elif demon_attach.lower() != _DEMON_MESH_ATTACH.lower():
        problems.append(
            "PROVENANCE DRIFT: the demons hang their shroud at %r but this module is "
            "pinned to %r. Re-derive; a pinned belief about this name is exactly what "
            "round 1 got backwards." % (demon_attach, _DEMON_MESH_ATTACH))

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
        problems.append("the Enslaver summon skill is missing (%s), so the pet-tier "
                        "roster cannot be derived and a tier could be silently skipped"
                        % _ENSLAVER_SUMMON)
    tiers = _pet_tiers(db)
    if db.has_record(_ENSLAVER_SUMMON) and not tiers:
        problems.append(
            "%s spawns NO resolvable pet: the derived tier roster is EMPTY. b98 "
            "shipped a monster-only shroud exactly this way and Will reported it as "
            "never implemented." % _ENSLAVER_SUMMON)
    w1_list = _family_closure(db)
    w1 = set(w1_list)
    escorts = _spawned_by(db, _ENSLAVER) if db.has_record(_ENSLAVER) else []
    if db.has_record(_ENSLAVER) and not escorts:
        problems.append(
            "FAMILY: the wild Enslaver spawns NO resolvable creature, so his ESCORTS "
            "are invisible to this gate. b93 never looked at them at all and shipped "
            "'the family has the family FX' as an unchecked claim.")
    pet_of_pet = []
    for t in tiers:
        pet_of_pet.extend(r for r in _spawned_by(db, t) if r not in pet_of_pet)
    if tiers and not pet_of_pet:
        problems.append(
            "FAMILY: no pet tier spawns a pet-of-pet. The summoned Enslaver raises "
            "marauders through svc_enslaver_petmarauders; an empty sub-roster means a "
            "family member Will can see in front of him is outside every check.")
    w2_list = _by_name_tag(db, _family_tags(db, w1_list))
    if w1 and set(w2_list) - w1:
        problems.append(
            "ROSTER WITNESS DISAGREEMENT: %r carr(y) a family name tag but are not "
            "reachable from the anchor + summon + spawn walk. A difficulty clone or a "
            "new tier has appeared (the Hunt has exactly such a clone, "
            "um_toxeus_hunt_l_99) and would ship with no shroud."
            % sorted(set(w2_list) - w1))

    roster = shroud_roster(db, w2=w2_list)
    rigs = {}
    for rec in roster:
        tag = ' (MONSTER)' if rec == _ENSLAVER else ' (PET/ESCORT)'

        # ── THE PROVEN CHANNEL, AND NOW THE ONLY ONE ───────────────────────
        st, ok, detail = mesh_route(db, rec)
        if st == 'SKIP':
            if _require_gates():
                problems.append(
                    "MESH ROUTE UNAVAILABLE under SVC_REQUIRE_GATES for %s: %s. The "
                    "shroud is now DERIVED from the rig binary and from nothing else, "
                    "so an unreadable archive means this member is unchecked."
                    % (rec, detail))
            else:
                notes.append("MESH ROUTE DOWNGRADED (not a pass) for %s: %s"
                             % (rec.rsplit('\\', 1)[-1], detail))
        if not ok:
            problems.append(
                "FAMILY FX PARITY: %s%s does NOT smoke. %s. Every member of this "
                "household must carry the demons' own CreateEntity block compiled "
                "into its rig - that is the ONLY mechanism with a confirmed "
                "rendering exemplar (Will, by eye, on the marauders), and four "
                "rounds of record-layer channels all failed in game. Give it "
                "%s (or another rig that embeds %s), never a field."
                % (rec, tag, detail, SHROUD_RIG,
                   _DEMON_FX_REF.rsplit('\\', 1)[-1]))
        rigs[rec] = _gv1(db, rec, 'mesh')

        # ── NO BELIEF CHANNELS LEFT BEHIND ─────────────────────────────────
        residue = _field_route_residue(db, rec)
        if residue:
            problems.append(
                "RETIRED CHANNEL: %s still names the retired %s on %r. R-257 removed "
                "the FIELD route for two reasons and both still hold: it is the shape "
                "that reads as 'wired' and is not (five filings), and on a member that "
                "already smokes from its rig it would DOUBLE the shroud Will asked to "
                "have 'the same' as his demons'." % (rec, _SHROUD, residue))
        slot = _slot_of(db, rec, _SHROUD)
        if slot is not None:
            problems.append(
                "RETIRED CHANNEL: %s carries the retired shroud at skillName%d. b93 "
                "shipped exactly this (skillName19 boss / skillName18 pets), in fields "
                "MonsterSkillManager.tpl declares nowhere." % (rec, slot))
        ctrl = _gv1(db, rec, 'controller')
        if ctrl and _is_ours_ctrl(ctrl):
            problems.append(
                "RETIRED CHANNEL: %s still runs the R-250 always-on controller clone "
                "%s. Its only purpose was to fire the retired self-buff shroud; a "
                "family member on a private AI record for a retired reason is the kind "
                "of leftover this lane exists to stop." % (rec, ctrl))
        dead = _dead_slots(db, rec)
        if dead:
            notes.append(
                "SLOT-CEILING DEBT on %s: skill(s) %r sit above skillName%d and are "
                "read by nobody. Not this lane's to unwind (RETIREMENT PROTOCOL) - "
                "registered as BL-R255-DEBT-1."
                % (rec.rsplit('\\', 1)[-1],
                   {i: s.rsplit('\\', 1)[-1] for i, s in sorted(dead.items())},
                   _ENGINE_SKILL_SLOT_MAX))

        # ── ADD, never take away: the running channel he shares with them ──
        run = _gv1(db, rec, 'charFxPakRunningNames')
        if _norm(run) != _norm(_SHADOWCLOAK_PAK):
            problems.append(
                "%s: charFxPakRunningNames is %r, expected %s. This module CHANGES a "
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
                    "CRASH LAW: %s skillName%d -> %s is a SpawnPet skill carrying %r. "
                    "FX belong on the MESH or on monster-record fields, NEVER a "
                    "charFxPak on a SpawnPet skill - the build28 crash trap."
                    % (rec, i, sk, bad))

    # ── ONE SWEEP OF THE WHOLE DATABASE, THREE QUESTIONS ───────────────────
    #   1. does anything still REFERENCE the retired R-250 shroud chain?
    #   2. does anything still RUN an svc_alwayson_* controller clone?
    #   3. which (mesh, charAnimationTableName) pairs does a MONSTER vouch for?
    retired = {_norm(r) for r in _RETIRED_RECORDS}
    leaks = []
    monster_pairings = {}
    for n in db.record_names():
        for k, tf in (db.get_fields(n) or {}).items():
            for v in (tf.values or []):
                if _norm(v) in retired:
                    leaks.append('%s :: %s -> %s' % (n, k.split('###')[0], v))
        c = _gv1(db, n, 'controller')
        if c and _is_ours_ctrl(c):
            problems.append(
                "RETIRED CHANNEL: %s runs the retired always-on controller clone %s."
                % (n, c))
        if str(_gv1(db, n, 'Class') or '').startswith('Monster'):
            m = _gv1(db, n, 'mesh')
            if m:
                monster_pairings.setdefault(
                    (_norm(m), _norm(_gv1(db, n, 'charAnimationTableName') or '')),
                    []).append(n)
    # the retired chain naturally references ITSELF when the records survive a
    # re-run over an already-built arz; only references from OUTSIDE it are a leak.
    leaks = [s for s in leaks if _norm(s.split(' :: ')[0]) not in retired]
    if leaks:
        problems.append(
            "RETIRED CHANNEL: %d live reference(s) to the R-250 shroud chain remain: "
            "%r. R-257 retired those records; anything still naming them either "
            "double-emits the shroud or teaches the next reader the wrong design."
            % (len(leaks), leaks[:6]))

    # ── B-SUMMON-1 SAFETY PROPERTY THE MESH SWAP QUIETLY NARROWED ──────────
    # `validate_summon_pets` step (b) requires every summoned pet's
    # (mesh, charAnimationTableName) to appear in `proven_pairings`, collected from
    # real Monster/Pet records. While the tiers rode the BASE rig, dozens of base
    # records vouched for them. On the mod-authored R-257 rig the ONLY witness in
    # existence is `um_toxeus_enslaver_99`, a mod Monster that happens to share the
    # tiers' anim table - so the day a future lane moves the boss off this rig (which
    # is exactly what champion_mesh's b102 swap once did to him) the three pets'
    # pairing goes unproven and B-SUMMON-1 reds the build with a message about
    # rendering rather than about this lane's choice. This arm makes the dependency
    # explicit and names the cause.
    ours = _norm(SHROUD_RIG)
    for rec in roster:
        if _norm(rigs.get(rec)) != ours:
            continue
        if str(_gv1(db, rec, 'Class') or '').startswith('Monster'):
            continue                              # a Monster vouches for itself
        anim = _norm(_gv1(db, rec, 'charAnimationTableName') or '')
        if not monster_pairings.get((ours, anim)):
            problems.append(
                "RIG PAIRING UNVOUCHED: %s rides the mod-authored %s with "
                "charAnimationTableName=%r and NO Monster record wears that same "
                "(mesh, anim) pair. `validate_summon_pets` B-SUMMON-1 step (b) would "
                "red this build. The rig is mod-authored, so no base record can ever "
                "vouch for it: the witness has to be a mod Monster on the same rig "
                "(today `um_toxeus_enslaver_99`). If a lane deliberately moves the "
                "boss off this rig, it must move the pets or supply another witness "
                "in the SAME change."
                % (rec, SHROUD_RIG, _gv1(db, rec, 'charAnimationTableName')))

    # the running channel's provenance must still hold on the exemplar itself
    if db.has_record(_MARAUDER):
        if _norm(_gv1(db, _MARAUDER, 'charFxPakRunningNames')) != _norm(_SHADOWCLOAK_PAK):
            problems.append("the marauders lost their shadowcloak running FX (%r)"
                            % _gv1(db, _MARAUDER, 'charFxPakRunningNames'))
    else:
        problems.append("the shroud's exemplar record is missing: %s" % _MARAUDER)

    for n in notes:
        print("  [enslaver_shroud] %s" % n)
    if problems:
        for p in problems:
            print("  ENSLAVER-SHROUD OFFENDER: %s" % p)
        raise SystemExit("enslaver_shroud.verify FAILED: %d problem(s)" % len(problems))

    by_rig = {}
    for rec, m in rigs.items():
        by_rig.setdefault(str(m), []).append(rec)
    print("  [enslaver_shroud].verify OK: all %d household member(s) walked (the wild "
          "boss, his %d escort(s), the %d pet tier(s) his soul summons and the %d "
          "pet-of-pet marauder(s) those raise) smoke by the ONE mechanism with a "
          "confirmed rendering exemplar - %s compiled into the rig at attach %r, "
          "derived from each wearer's .msh binary this build: %s. NO field channel "
          "survives anywhere (no initialSkillName/buffSelfSkillName shroud, no kit "
          "slot, no always-on controller clone, zero live references to the retired "
          "R-250 chain). Running FX untouched; no charFxPak on any SpawnPet skill.\n"
          "  WHAT IS CLAIMED: these records now reach the screen by the SAME "
          "mechanism, through the SAME attach point, with the SAME entity reference "
          "and a byte-identical block, as the marauders Will confirmed by eye. WHAT IS "
          "NOT CLAIMED: that anyone has SEEN this build render (BL-R250-DEBT-1)."
          % (len(roster), len(escorts), len(tiers), len(pet_of_pet),
             _DEMON_FX_REF.rsplit('\\', 1)[-1], _DEMON_MESH_ATTACH,
             '; '.join('%d on %s' % (len(v), k.rsplit('\\', 1)[-1])
                       for k, v in sorted(by_rig.items()))))
    return tags


# ── NEGATIVE TEST ───────────────────────────────────────────────────────────

def _negtest():
    r"""py tools/patches/enslaver_shroud.py --negtest

    THE STUB'S RIG TABLE IS THE TEST'S OWN PREMISE, AND ROUND 1 PLANTED A FALSE
    ONE (it asserted his rig has no `SpecialHit01`, then "caught" a plant that
    aimed there - certifying the module's own error). Every row below is the
    MEASURED content of the real binaries, and `--selftest` re-measures them
    against the archives, so the stub can never again quietly disagree with the
    assets it stands in for.
    """
    global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE, _DEMON_ATTACH_OVERRIDE
    global _MESH_SMOKE_OVERRIDE, _RIG_ASSET_OVERRIDE
    import os as _os
    from collections import OrderedDict

    _REQ_GATES_WAS = _os.environ.get('SVC_REQUIRE_GATES')

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

    _MESH_PLAIN = DONOR_RIG                      # FX-free: R-102's anti-green rig
    _MESH_D = EXEMPLAR_RIG                       # the demons', Will-confirmed
    _MESH_OURS = SHROUD_RIG                      # R-257's authored rig
    _AP_COMMON = {'Head', 'HeadEffect', 'L Hand', 'Prey_Effect', 'R Hand',
                  'SpecialHit01', 'SpecialHit02', 'SpecialHit03', 'SpecialHit04',
                  'Target', 'Upper Body'}
    _BONES = {'Bone_Root', 'Bone_Waist', 'Bone_Spine01', 'Bone_Spine02', 'Bone_Head',
              'Bone_R_Weapon', 'Bone_L_Weapon'}
    _RIG_NAMES = {_norm(_MESH_PLAIN): _AP_COMMON | _BONES,
                  _norm(_MESH_OURS): _AP_COMMON | _BONES,
                  _norm(_MESH_D): _AP_COMMON | _BONES | {_DEMON_ONLY_ATTACH}}
    _SMOKE_BLOCK = [(_DEMON_MESH_ATTACH, r'Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr')]
    _FX_TABLE = {_norm(_MESH_PLAIN): [],
                 _norm(_MESH_OURS): list(_SMOKE_BLOCK),
                 _norm(_MESH_D): list(_SMOKE_BLOCK)}

    _PETS = [r'records\skills\soulskills\pets\toxeus_enslaver_%d.dbr' % i
             for i in (1, 2, 3)]
    _MPETS = [r'records\skills\soulskills\pets\enslaver_marauder_%d.dbr' % i
              for i in (1, 2, 3)]
    _CTRL_M = r'records\controllers\monster\controller_skeleton_toxeus.dbr'
    _CTRL_M_CLONE = (r'records\controllers\monster'
                     r'\svc_alwayson_controller_skeleton_toxeus.dbr')
    _SHARED_P = (r'records\skills\spirit\drxpet\drxpet_controllers'
                 r'\controller_skelly_aggressive.dbr')
    _CTRL_P_CLONE = (r'records\skills\spirit\drxpet\drxpet_controllers'
                     r'\svc_alwayson_controller_skelly_aggressive.dbr')
    _SPAWN = r'records\skills\boss skills\svc_enslaver_summonmarauders.dbr'
    _SUBSPAWN = r'records\skills\soulskills\svc_enslaver_petmarauders.dbr'

    def _base():
        """The POST-R-257 shipped shape: everyone smokes from a rig, no fields."""
        db = _Stub()
        db.d[_SHADOWCLOAK_PAK] = {'particleEffectNames': ['x']}
        db.d[_MARAUDER] = {'Class': ['Monster'],
                           'description': ['tagSVCMonsterEnslaverMarauder'],
                           'mesh': [_MESH_D],
                           'controller': [_SHARED_P],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        db.d[_SPAWN] = {'Class': ['Skill_SpawnPetMonster'], 'spawnObjects': [_MARAUDER]}
        db.d[_SUBSPAWN] = {'Class': ['Skill_SpawnPet'], 'spawnObjects': list(_MPETS)}
        db.d[_CTRL_M] = {'BuffSelfBehavior': ['WhenEnemyIsSeen']}
        db.d[_CTRL_M_CLONE] = {'BuffSelfBehavior': ['WheneverPossible']}
        db.d[_SHARED_P] = {'BuffSelfBehavior': ['WhenEnemyIsSeen']}
        db.d[_CTRL_P_CLONE] = {'BuffSelfBehavior': ['WheneverPossible']}
        db.d[_ENSLAVER] = {'Class': ['Monster'], 'description': ['tagSVCMonsterEnslaver'],
                           'mesh': [_MESH_OURS], 'controller': [_CTRL_M],
                           'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                           'skillName8': [_SPAWN]}
        db.d[_ENSLAVER_SUMMON] = {'Class': ['Skill_SpawnPet'], 'spawnObjects': list(_PETS)}
        for p in _PETS:
            db.d[p] = {'Class': ['Pet'], 'description': ['tagSVCMonsterEnslaverPet'],
                       'mesh': [_MESH_OURS], 'controller': [_SHARED_P],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK],
                       'skillName9': [_SUBSPAWN]}
        for p in _MPETS:
            db.d[p] = {'Class': ['Pet'],
                       'description': ['tagSVCMonsterEnslaverMarauderPet'],
                       'mesh': [_MESH_D], 'controller': [_SHARED_P],
                       'charFxPakRunningNames': [_SHADOWCLOAK_PAK]}
        # a bystander that must never pick up anything of ours
        db.d[r'records\skills\soulskills\pets\boneash_1.dbr'] = {
            'Class': ['Pet'], 'controller': [_SHARED_P]}
        return db

    def _plant_retired_chain(db):
        """Re-create the b93/R-250 records so a plant can reference them."""
        db.d[_SHROUD_FX] = {'Class': ['EffectEntity'], 'effectFile': [_DEMON_PFX]}
        db.d[_SHROUD_PAK] = {'particleEffectNames': [_SHROUD_FX],
                             'particleEffectAttachPoints': [_DEMON_MESH_ATTACH]}
        db.d[_SHROUD] = {'Class': ['Skill_BuffSelfToggled'],
                         'charFxPakSelfNames': [_SHROUD_PAK]}

    plants = [
        # ── R-257: the five-filings defect itself ───────────────────────────
        ('THE R-257 DEFECT: a summoned pet tier is left on the FX-free rig, so it '
         'renders no smoke at all (Will\'s 08-15 screenshot)',
         lambda db: db.d[_PETS[0]].__setitem__('mesh', [_MESH_PLAIN])),
        ('the WILD boss is left on the FX-free rig',
         lambda db: db.d[_ENSLAVER].__setitem__('mesh', [_MESH_PLAIN])),
        ('ALL THREE pet tiers left on the FX-free rig',
         lambda db: [db.d[p].__setitem__('mesh', [_MESH_PLAIN]) for p in _PETS]),
        ('STRIP ONE PET: a pet-of-pet marauder is moved onto the FX-free rig '
         '(the R-255 negtest, still required)',
         lambda db: db.d[_MPETS[2]].__setitem__('mesh', [_MESH_PLAIN])),
        ('the wild marauder - the EXEMPLAR - is moved onto the FX-free rig',
         lambda db: db.d[_MARAUDER].__setitem__('mesh', [_MESH_PLAIN])),
        ('a family member has no mesh field at all',
         lambda db: db.d[_PETS[1]].pop('mesh')),

        # ── the BELIEF-CHANNEL replant: the whole point of R-257's retirement ─
        ('BELIEF CHANNEL REPLANTED: a member wears the R-257 rig but ALSO carries '
         'the retired shroud on both always-on channels (the b99 shape, which now '
         'DOUBLES the smoke and re-teaches the wrong design)',
         lambda db: (_plant_retired_chain(db),
                     [db.d[_PETS[0]].__setitem__(f, [_SHROUD])
                      for f in _ALWAYS_ON_FIELDS])),
        ('BELIEF-CHANNEL-ONLY MEMBER: a pet tier is put back on the FX-free rig and '
         'given the b99 field route instead - exactly what shipped as build99 and '
         'exactly what Will photographed not working',
         lambda db: (_plant_retired_chain(db),
                     db.d[_PETS[2]].__setitem__('mesh', [_MESH_PLAIN]),
                     [db.d[_PETS[2]].__setitem__(f, [_SHROUD])
                      for f in _ALWAYS_ON_FIELDS])),
        ('the retired shroud comes back in ONE always-on channel only',
         lambda db: (_plant_retired_chain(db),
                     db.d[_ENSLAVER].__setitem__('initialSkillName', [_SHROUD]))),
        ('THE b93 DEFECT REPLAYED: the retired shroud back in skillName19/18',
         lambda db: (_plant_retired_chain(db),
                     db.d[_ENSLAVER].__setitem__('skillName19', [_SHROUD]),
                     [db.d[p].__setitem__('skillName18', [_SHROUD]) for p in _PETS])),
        ('a member is left on the R-250 always-on controller clone',
         lambda db: db.d[_PETS[1]].__setitem__('controller', [_CTRL_M_CLONE])),
        ('a BYSTANDER outside the family is left on an always-on controller clone',
         lambda db: db.d[r'records\skills\soulskills\pets\boneash_1.dbr']
         .__setitem__('controller', [_CTRL_P_CLONE])),
        ('an unrelated record still REFERENCES the retired shroud skill',
         lambda db: (_plant_retired_chain(db),
                     db.d.__setitem__(r'records\skills\zz_someone_else.dbr',
                                      {'buffSelfSkillName': [_SHROUD]}))),

        # ── the rig itself, and the asset behind it ────────────────────────
        ('THE DEPLOY COUPLING: the authored rig is not in the staged mod '
         'Creatures.arc, so the whole family would resolve NO MESH',
         lambda db: globals().__setitem__(
             '_RIG_ASSET_OVERRIDE',
             ('FAIL', 'the staged mod archive does NOT carry %r' % SHROUD_RIG_ENTRY))),
        ('the authored rig is not derivable from the base binaries at all',
         lambda db: globals().__setitem__(
             '_RIG_ASSET_OVERRIDE',
             ('FAIL', 'the rig is not derivable from the base binaries'))),
        # NOTE: these plants edit the PER-RUN copy `_MESH_SMOKE_OVERRIDE`, never the
        # master `_FX_TABLE` - a leaked mutation would make the NEXT plant's "catch"
        # a lie about a different defect.
        ('the rig embeds the effect but hangs it on the WRONG attach point '
         '(Smoke02 - the helper the demons have and his rig does not)',
         lambda db: _MESH_SMOKE_OVERRIDE.__setitem__(
             _norm(_MESH_OURS), [(_DEMON_ONLY_ATTACH,
                                  r'Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr')])),
        ('the rig embeds the WRONG effect (the R-102 green)',
         lambda db: _MESH_SMOKE_OVERRIDE.__setitem__(
             _norm(_MESH_OURS),
             [(_DEMON_MESH_ATTACH,
               r'Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr')])),
        ('the EXEMPLAR mesh loses its compiled-in smoke, so the provenance claim '
         'is no longer true of anything',
         lambda db: (_MESH_SMOKE_OVERRIDE.__setitem__(_norm(_MESH_D), []),
                     _MESH_SMOKE_OVERRIDE.__setitem__(_norm(_MESH_OURS), []))),
        ('the demons move their shroud to a different attach point',
         lambda db: (_MESH_SMOKE_OVERRIDE.__setitem__(
             _norm(_MESH_D), [('Smoke02',
                               r'Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr')]),
             globals().__setitem__('_DEMON_ATTACH_OVERRIDE', 'Smoke02'))),

        # ── the B-SUMMON-1 pairing property the mesh swap narrowed ──────────
        # These two cannot be seen by ANY other arm: the family still smokes, the
        # rig is still correct, every retirement still holds. Only the pairing
        # witness is gone, and the build would red much later in
        # validate_summon_pets with a message about rendering.
        ('PAIRING WITNESS LOST: the boss is moved onto the demons\' rig - he still '
         'smokes, so every FX arm is happy - and the three pet tiers left on the '
         'mod-authored rig now have NO Monster vouching their (mesh, anim) pair',
         lambda db: db.d[_ENSLAVER].__setitem__('mesh', [_MESH_D])),
        ('PAIRING WITNESS LOST the other way: a pet tier is given an anim table no '
         'Monster on its rig uses',
         lambda db: db.d[_PETS[1]].__setitem__(
             'charAnimationTableName',
             [r'records\creature\pc\anm_something_else.dbr'])),

        # ── roster integrity (the R-255 half, unchanged) ────────────────────
        ('the summon spawns nothing, so the pet-tier roster goes silently empty',
         lambda db: db.d[_ENSLAVER_SUMMON].__setitem__('spawnObjects', [])),
        ('the wild boss stops spawning escorts, so his marauders leave the gate',
         lambda db: db.d[_SPAWN].__setitem__('spawnObjects', [])),
        ('the pet tiers stop raising pet-of-pet marauders',
         lambda db: db.d[_SUBSPAWN].__setitem__('spawnObjects', [])),
        ('a DIFFICULTY CLONE wearing a family name tag appears outside the walk',
         lambda db: db.d.__setitem__(
             r'records\creature\monster\shadowstalker\um_toxeus_enslaver_l_99.dbr',
             {'Class': ['Monster'], 'description': ['tagSVCMonsterEnslaver'],
              'mesh': [_MESH_PLAIN], 'controller': [_CTRL_M],
              'charFxPakRunningNames': [_SHADOWCLOAK_PAK]})),

        # ── standing laws ──────────────────────────────────────────────────
        ('a member loses the running channel he shares with his demons',
         lambda db: db.d[_PETS[1]].pop('charFxPakRunningNames')),
        ('the marauders lose their running channel',
         lambda db: db.d[_MARAUDER].__setitem__('charFxPakRunningNames', ['other'])),
        ('CRASH LAW: a charFxPak is put on a SpawnPet skill (the build28 trap)',
         lambda db: db.d[_SPAWN].__setitem__('charFxPakSelfNames', [_SHADOWCLOAK_PAK])),
        ('the exemplar record itself disappears',
         lambda db: db.d.pop(_MARAUDER)),

        # ── an UNANSWERABLE gate is not a passing gate (SVC_REQUIRE_GATES) ──
        ('SHIP BUILD with the rig-asset arm UNAVAILABLE: the archives cannot be '
         'read, so nothing proves the mesh those four records name actually ships',
         lambda db: (_os.environ.__setitem__('SVC_REQUIRE_GATES', '1'),
                     globals().__setitem__(
                         '_RIG_ASSET_OVERRIDE',
                         ('SKIP', 'no mod Creatures.arc reachable')))),
        ('SHIP BUILD with a member\'s RIG UNREADABLE: the shroud is derived from the '
         'binary and from nothing else, so that member is simply unchecked',
         lambda db: (_os.environ.__setitem__('SVC_REQUIRE_GATES', '1'),
                     _MESH_SMOKE_OVERRIDE.pop(_norm(_MESH_OURS)))),
    ]

    def _arm():
        """Re-arm every injected answer to its MEASURED clean value.

        Rebuilt from scratch per plant: several plants mutate the FX table in
        place, and a leaked mutation would make the NEXT plant's 'catch' a lie
        about a different defect - the negtest twin of the round-1 stub error.
        """
        global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE, _DEMON_ATTACH_OVERRIDE
        global _MESH_SMOKE_OVERRIDE, _RIG_ASSET_OVERRIDE
        _RIG_NAMES_OVERRIDE = {k: set(v) for k, v in _RIG_NAMES.items()}
        _DEMON_FX_OVERRIDE = None
        _DEMON_ATTACH_OVERRIDE = None
        _RIG_ASSET_OVERRIDE = ('PASS', 'stub: derived + staged')
        _MESH_SMOKE_OVERRIDE = {k: list(v) for k, v in _FX_TABLE.items()}
        # the two SVC_REQUIRE_GATES plants set this; a leak would make every LATER
        # plant run under a different contract than the baseline it was compared to
        _os.environ.pop('SVC_REQUIRE_GATES', None)
        return _MESH_SMOKE_OVERRIDE

    bad = 0
    for label, mutate in plants:
        # sanity: the CLEAN baseline must PASS, or every "catch" below is noise
        _arm()
        try:
            verify(_base())
        except SystemExit as e:
            print("SETUP FAIL (clean baseline does not verify): %s" % e)
            _clear_overrides()
            return 1
        _arm()
        db = _base()
        mutate(db)
        try:
            verify(db)
        except SystemExit:
            print("  CAUGHT  %s" % label)
        else:
            print("  MISSED  %s   <<< the gate did not see this" % label)
            bad += 1

    # A gate left holding its stubs would pass on injected answers for the rest of
    # the process and report a real-asset PASS it never performed. Same for the env
    # var two plants set: restore whatever the caller had.
    _clear_overrides()
    if _REQ_GATES_WAS is None:
        _os.environ.pop('SVC_REQUIRE_GATES', None)
    else:
        _os.environ['SVC_REQUIRE_GATES'] = _REQ_GATES_WAS
    stub_caught = len(plants) - bad
    print("  stub plants: %d/%d caught" % (stub_caught, len(plants)))

    # The half that runs the REAL function against REAL archives. Kept in the same
    # command deliberately: a `--negtest` that green-lights a module while the
    # build-deciding function was never executed is the defect this lane shipped.
    ra_ok, ra_n = _negtest_rig_asset()
    print("negtest: %d/%d caught (%d/%d stubbed plants + %d/%d unstubbed rig-asset "
          "arms)" % (stub_caught + ra_ok, len(plants) + ra_n,
                     stub_caught, len(plants), ra_ok, ra_n))
    return 1 if (bad or ra_ok != ra_n) else 0


def _clear_overrides():
    global _RIG_NAMES_OVERRIDE, _DEMON_FX_OVERRIDE
    global _DEMON_ATTACH_OVERRIDE, _MESH_SMOKE_OVERRIDE, _RIG_ASSET_OVERRIDE
    _RIG_NAMES_OVERRIDE = None
    _DEMON_FX_OVERRIDE = None
    _DEMON_ATTACH_OVERRIDE = None
    _MESH_SMOKE_OVERRIDE = None
    _RIG_ASSET_OVERRIDE = None


# ── NEGATIVE TEST, PART 2: THE REAL rig_asset_state() ────────────────────────

def _negtest_rig_asset():
    r"""py tools/patches/enslaver_shroud.py --negtest   (this half runs unstubbed)

    ROUND 1'S NEGTEST COULD NOT SEE EITHER OF ITS OWN P0s, AND THAT WAS STRUCTURAL.
    Every plant above runs against a dict stub with `_RIG_ASSET_OVERRIDE` injected,
    so the function that walks the staged archives and decides the build's fate -
    `rig_asset_state()` - was executed by NO plant. `docs/MISTAKES.md` had logged
    exactly that shape for R-256 one day earlier ("--negtest runs this module
    STANDALONE ... and never the shared gates the module opts into") and this lane
    reproduced the blind spot while citing the entry.

    So this half plants REAL archives on disk, points the REAL shipping anchor at
    them and runs the REAL function. It needs the base binaries (the rig is derived,
    never checked in); when they are unreachable it says so and passes nothing.
    """
    import os as _os
    import shutil as _shutil
    import tempfile as _tempfile
    from pathlib import Path as _P

    print('--- rig-asset arm, UNSTUBBED (real archives on disk) ---')
    _clear_overrides()
    import mesh_assets
    from arc_patcher import ArcArchive
    try:
        rig = _rig.rig_bytes_checked()
    except Exception as e:                                   # noqa: BLE001
        print('  SKIP: the base archives are not reachable, so no real rig can be '
              'derived and none of these arms can run (%s)' % e)
        return 0, 0

    was_ship = _os.environ.get('SVC_SHIP_RESOURCES')
    was_mod = _os.environ.get('SVC_MOD_RESOURCES')
    was_cwd = _os.getcwd()
    root = _P(_tempfile.mkdtemp(prefix='svc_rigasset_'))

    def _arc(path, entries):
        a = ArcArchive()
        for name, data in entries.items():
            a.add_file(name, data)
        path.parent.mkdir(parents=True, exist_ok=True)
        a.write(path)
        return path

    DYE = 'pc/male/svc_dummy_skin.tex'          # stands in for the PR-2 dye payload
    good = {DYE: b'x' * 64, SHROUD_RIG_ENTRY: rig}
    stale = {DYE: b'x' * 64}                    # the SHIPPED build100 shape: no rig
    torn = {DYE: b'x' * 64, SHROUD_RIG_ENTRY: rig[:-40]}

    _arc(root / 'ship_ok' / 'Resources' / 'Creatures.arc', good)
    _arc(root / 'ship_stale' / 'Resources' / 'Creatures.arc', stale)
    _arc(root / 'ship_torn' / 'Resources' / 'Creatures.arc', torn)
    (root / 'ship_noarc' / 'Resources').mkdir(parents=True, exist_ok=True)
    # a STALE scratch tree in the CWD glob path - round 1 let this red the build
    _arc(root / 'cwd' / 'local' / 'b100_run2' / 'Resources' / 'Creatures.arc', stale)
    _arc(root / 'cwd' / 'work' / 'SoulvizierClassic' / 'Resources' / 'Creatures.arc', good)

    arms = [
        ('the shipping archive CARRIES the byte-identical rig',
         root / 'ship_ok' / 'Resources', root / 'cwd', 'PASS'),
        ('THE ROUND-1 P0: the shipping archive is the build100-era dye arc with NO '
         'rig, so the family would resolve no mesh at all',
         root / 'ship_stale' / 'Resources', root / 'cwd', 'FAIL'),
        ('the shipping Resources dir exists but holds NO Creatures.arc',
         root / 'ship_noarc' / 'Resources', root / 'cwd', 'FAIL'),
        ('the shipping archive carries a TORN rig (right name, wrong bytes)',
         root / 'ship_torn' / 'Resources', root / 'cwd', 'FAIL'),
        ('the anchor names a Resources dir that does not exist (scratch layout) - '
         'honestly unanswerable, never a pass',
         root / 'ship_missing' / 'Resources', root / 'cwd', 'SKIP'),
        ('THE ROUND-1 P0, OTHER HALF: the shipping archive is GOOD while a STALE '
         'scratch archive sits in local/*/Resources - round 1 asked every glob hit '
         'and would have red-locked this build forever',
         root / 'cwd' / 'work' / 'SoulvizierClassic' / 'Resources', root / 'cwd',
         'PASS'),
    ]

    bad = 0
    try:
        for label, anchor, cwd, want in arms:
            _os.chdir(str(cwd))
            _os.environ.pop('SVC_MOD_RESOURCES', None)
            mesh_assets.set_shipping_resource_dir(anchor)
            st, detail = rig_asset_state()
            ok = (st == want)
            print('  %-7s %s%s\n          -> %s: %s'
                  % ('OK' if ok else 'WRONG', label,
                     '' if ok else '   <<< expected %s, got %s' % (want, st),
                     st, detail[:150]))
            if not ok:
                bad += 1
    finally:
        _os.chdir(was_cwd)
        _os.environ.pop('SVC_SHIP_RESOURCES', None)
        _os.environ.pop('SVC_MOD_RESOURCES', None)
        if was_ship is not None:
            _os.environ['SVC_SHIP_RESOURCES'] = was_ship
        if was_mod is not None:
            _os.environ['SVC_MOD_RESOURCES'] = was_mod
        mesh_assets._ARC_CACHE.clear()
        _shutil.rmtree(root, ignore_errors=True)
    print('  rig-asset arms: %d/%d correct' % (len(arms) - bad, len(arms)))
    return len(arms) - bad, len(arms)


# ── INSTRUMENT SELF-TEST (the round-1 failure mode, closed) ─────────────────

def _selftest():
    r"""py tools/patches/enslaver_shroud.py --selftest

    A negative test can only ever be as true as the premise its stub asserts, and
    round 1's stub asserted a false one. This checks the MEASUREMENT ITSELF
    against the real archives. Loud SKIP when they are not reachable - never a
    silent pass.
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
    bad = []
    rigs = {}
    for ref in (DONOR_RIG, EXEMPLAR_RIG):
        data, arc = mesh_assets.read_asset(ref)
        if not data:
            print("SELFTEST SKIP: %s did not resolve" % ref)
            return 0
        rigs[ref] = {'names': {n.lower() for n in mesh_assets.rig_names_of(data)},
                     'attach': mesh_assets.attach_points_of(data),
                     'bones': mesh_assets.bones_of(data),
                     'fx_at': mesh_assets.embedded_fx_attachments_of(data)}
        print("  %-34s %d bone(s) + %d attach point(s), FX %r"
              % (ref.rsplit('\\', 1)[-1], len(rigs[ref]['bones']),
                 len(rigs[ref]['attach']), rigs[ref]['fx_at']))

    # 1. the instrument is not blind: AttachPoint names are NOT NUL-terminated and
    #    must be found anyway (the round-1 bug that became design law).
    if not rigs[DONOR_RIG]['attach']:
        bad.append("attach_points_of() found NO AttachPoint on %s - the reader is "
                   "blind again and every rig result is meaningless" % DONOR_RIG)
    if _DEMON_MESH_ATTACH.lower() in {n.lower() for n in rigs[DONOR_RIG]['bones']}:
        bad.append("%r turned up in the BONE table, so this selftest no longer "
                   "distinguishes the two namespaces" % _DEMON_MESH_ATTACH)

    # 2. the load-bearing fact: the attach point we copy is on HIS rig.
    if _DEMON_MESH_ATTACH.lower() not in rigs[DONOR_RIG]['names']:
        bad.append("%r is NOT on %s. That is round 1's claim, and if it is ever true "
                   "again this module aims at nothing." % (_DEMON_MESH_ATTACH, DONOR_RIG))

    # 3. the counter-example must stay a counter-example.
    if _DEMON_ONLY_ATTACH.lower() in rigs[DONOR_RIG]['names']:
        bad.append("%r is now on HIS rig too, so it is no longer the missing-attach "
                   "example the gate and the negtest use" % _DEMON_ONLY_ATTACH)
    if _DEMON_ONLY_ATTACH.lower() not in rigs[EXEMPLAR_RIG]['names']:
        bad.append("%r is not on the DEMONS' rig either" % _DEMON_ONLY_ATTACH)

    # 4. the exemplar really hangs its shroud where we say it does.
    want = _DEMON_FX_REF.rsplit('\\', 1)[-1].lower()
    hung = [a for a, e in rigs[EXEMPLAR_RIG]['fx_at']
            if e and str(e).replace('/', '\\').rsplit('\\', 1)[-1].lower() == want]
    if [h.lower() for h in hung] != [_DEMON_MESH_ATTACH.lower()]:
        bad.append("the demons hang %s at %r, not at the pinned %r"
                   % (want, hung, _DEMON_MESH_ATTACH))

    # 5. the donor must still be FX-FREE, or R-257 is stacking on something.
    if rigs[DONOR_RIG]['fx_at']:
        bad.append("%s now carries embedded FX %r - it is no longer the FX-free rig "
                   "R-102 chose, and the authored rig would double-emit"
                   % (DONOR_RIG, rigs[DONOR_RIG]['fx_at']))

    # 6. R-257's own asset: derivable, verified, and (if staged) byte-identical.
    st, detail = rig_asset_state()
    print("  RIG ASSET %s: %s" % (st, detail))
    if st == 'FAIL':
        bad.append("RIG ASSET: %s" % detail)

    # 7. R-255's ceiling, still re-measured: nothing writes a kit slot any more,
    #    but the gate still reports debt against it and still reds if the shroud
    #    reappears there, so the number must stay derived rather than believed.
    try:
        from pathlib import Path
        from arc_patcher import ArcArchive
        import re as _re
        tpl_arc = Path(mesh_assets.game_dir()) / 'Toolset' / 'Templates.arc'
        if not tpl_arc.exists():
            print("  Templates.arc not reachable: the slot ceiling was NOT re-measured")
        else:
            blob = ArcArchive.from_file(tpl_arc).get_file(
                'templates/templatebase/monsterskillmanager.tpl')
            if not blob:
                bad.append("MonsterSkillManager.tpl is not in Templates.arc, so the "
                           "declared slot ceiling could not be re-measured at all")
            else:
                slots = sorted({int(m) for m in
                                _re.findall(r'skillName(\d+)', blob.decode('latin-1'))})
                if not slots:
                    bad.append("MonsterSkillManager.tpl declares NO skillName slot")
                elif max(slots) != _ENGINE_SKILL_SLOT_MAX:
                    bad.append("MonsterSkillManager.tpl declares skillName1..%d but "
                               "this module is pinned to %d"
                               % (max(slots), _ENGINE_SKILL_SLOT_MAX))
                else:
                    print("  MonsterSkillManager.tpl declares skillName1..%d (and "
                          "nothing above it) - the ceiling holds" % max(slots))
    except Exception as e:                                   # noqa: BLE001
        print("  slot ceiling NOT re-measured (%s)" % e)

    for b in bad:
        print("  SELFTEST OFFENDER: %s" % b)
    if bad:
        print("selftest: FAILED (%d)" % len(bad))
        return 1
    print("selftest OK: the exemplar hangs %s at %r; %r is declared on BOTH rigs; %r "
          "is on the demons' rig ONLY and stays the silent-nothing example; the donor "
          "is FX-free; the authored rig derives and verifies."
          % (want, _DEMON_MESH_ATTACH, _DEMON_MESH_ATTACH, _DEMON_ONLY_ATTACH))
    return 0


if __name__ == '__main__':
    import sys
    rc = 0
    if '--negtest' in sys.argv:
        rc |= _negtest()
    if '--selftest' in sys.argv:
        rc |= _selftest()
    sys.exit(rc)
