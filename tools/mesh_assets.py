r"""mesh_assets - read creature ART (.msh / .anm) out of the shipped .arc archives.

WHY THIS EXISTS (R-102). Four fix waves chased the Enslaver's green glow through
`.dbr` FIELDS and all four failed, because the green was never in a field: it is
compiled INTO `Creatures\Monster\Skeleton\RevenantPoison.msh` as a trailing

    CreateEntity { attach = "Waist";
                   entity  = "Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr" }

block that pulls a green `.pfx`. No `.arz` scan can see it and no `baseTexture`
override can suppress it (`baseTexture` replaces the PRIMARY SKIN only).

So a mesh decision in this repo cannot be made from the database alone. This
module gives the build + its gates a way to ask the ASSET the two questions that
actually matter:

  * `embedded_fx_of(mesh)`  - does this mesh carry its own effect entity?
                              (a mesh with none cannot emit the green)
  * `bones_of(mesh|anm)`    - what rig is this? An `.anm` clip drives a mesh by
                              bone; if the new mesh does not carry the bones the
                              old clips drive, the champion T-poses. R-102's
                              fourth amendment names ANIMATION, not colour, as
                              the real risk in a mesh swap.
  * `attach_points_of(mesh)`- the OTHER name table (see below).
  * `rig_names_of(mesh)`    - both tables, which is what an attach-point check
                              must ask against.

TWO NAME TABLES, AND ASKING THE WRONG ONE IS A FALSE MEASUREMENT (b104 R-250).
A `.msh` declares names in two structurally different places:

  * the BONE table  - NUL-terminated ASCII inside the binary skeleton block
    (`Bone_Waist\x00`), which `bones_of()` reads; and
  * the ATTACHPOINT table - a CRLF *text* block near the tail:

        AttachPoint
        {
            name   = "SpecialHit01"
            origin = (0.000000, 0.000000, 0.000000)
            ...
        }

    which contains NO NUL terminators at all, so every NUL-anchored scanner is
    structurally blind to it and reports these names as ABSENT.

`particleEffectAttachPoints` on a CharFxPak draws from BOTH namespaces, and in
this database it draws overwhelmingly from the ATTACHPOINT one (measured on the
build83 arz: 'L Hand' x21, 'R Hand' x20, 'SpecialHit03' x4, 'HeadEffect' x4,
'EYE_LEFT'/'EYE_RIGHT'/'Lower Body'/'Eye'/'Prey_Effect' x3 each, 'Head'/'Target'
x2 ... against exactly 5 rows using a raw `Bone_*`). A gate that resolves those
values against the bone table alone therefore FALSE-FAILS the correct records
and cannot see the failure it advertises - which is how a gate gets waived
instead of fixed. Use `rig_names_of()`, never `bones_of()`, for that question.

NAME LOOKUP IS CASE-INSENSITIVE in practice and callers must match that: the
shipped DB addresses these tables as `Bone_spine01` (rig says `Bone_Spine01`)
and `Specialhit03` (rig says `SpecialHit03`). Compare casefolded.

ADDRESSING PITFALL, and it is the reason a naive prefix match returns zero rows:
the FIRST path component of a TQ art reference is the ARCHIVE NAME, not a
directory. `Creatures\Monster\Skeleton\RevenantPoison.msh` is the entry
`monster\skeleton\revenantpoison.msh` INSIDE `Creatures.arc`.

Read-only. Never writes an arc.
"""
import os
import re
from pathlib import Path

try:
    from arc_patcher import ArcArchive
except ImportError:                                          # imported as tools.mesh_assets
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from arc_patcher import ArcArchive

_DEFAULT_GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition'

# TQ rig bone names, plus the attach helpers the exporter emits alongside them.
_BONE_RE = re.compile(rb'(?:Bone_[A-Za-z0-9_]+|Smoke\d+|Waist|Root|Scene_Root)\x00')
_STR_RE = re.compile(rb'[ -~]{4,}')

# The CRLF text tables. These carry no NUL terminators, which is precisely why a
# NUL-anchored scanner cannot see them (see the module docstring).
_ATTACH_BLOCK_RE = re.compile(rb'AttachPoint\s*\{(.*?)\}', re.S)
_CREATE_ENTITY_RE = re.compile(rb'CreateEntity\s*\{(.*?)\}', re.S)
_NAME_KV_RE = re.compile(rb'name\s*=\s*"([^"]*)"')
_ATTACH_KV_RE = re.compile(rb'attach\s*=\s*"([^"]*)"')
_ENTITY_KV_RE = re.compile(rb'entity\s*=\s*"([^"]*)"')

# A mesh "carries embedded FX" iff its binary names an effect entity / particle.
_FX_MARKERS = (b'createentity', b'.pfx')

_ARC_CACHE = {}
_MISSING = object()


def game_dir():
    return Path(os.environ.get('SVC_TQAE_DIR', _DEFAULT_GAME))


# ── THE SHIPPING ANCHOR (R-257 round 2) ──────────────────────────────────────
# `mod_resource_dirs()` is a SEARCH PATH: every staged tree this working copy can
# see, so an asset lookup never false-fails. That is the right answer for "can
# this reference resolve?" and the WRONG one for "does the archive this build
# SHIPS carry X?" - a question that has exactly one correct address, the
# `Resources` dir beside the `.arz` being written (the anchor
# `validate_render_chain` has always used: `output.parent.parent / 'Resources'`).
#
# Conflating the two cost this lane a P0: `enslaver_shroud`'s rig-asset arm
# demanded the rig in EVERY glob hit, so a stale scratch tree anywhere under
# `local/` could red a build whose own shipped archive was perfect. The build
# declares its anchor here, once, and asset gates ask for it by name.
_SHIP_ENV = 'SVC_SHIP_RESOURCES'


def shipping_resource_dir():
    r"""The ONE staged `Resources` dir this build's output ships beside, or None.

    None means nobody declared one (a bare CLI run, a static dry-run, a negtest).
    A gate that needs the anchor must SAY it is unanchored rather than guessing -
    guessing is what turned a scratch tree into a ship-blocking FAIL.
    """
    v = os.environ.get(_SHIP_ENV)
    return Path(v) if v else None


def set_shipping_resource_dir(path):
    """Declare the anchor (the build entrypoint does this once, before any gate).

    Clears the archive cache: archives already opened were resolved against the
    OLD search order, and a gate that reads a cached chain built before the anchor
    existed is answering about a different tree than the one it names.
    """
    os.environ[_SHIP_ENV] = str(path)
    _ARC_CACHE.clear()
    return Path(path)


def mod_resource_dirs():
    r"""The MOD's own staged `Resources` dirs, in the order the engine sees them.

    A creature reference is NOT necessarily a base-game asset: this mod ships
    `SVMesh.arc`, `drx.arc`, `DRXeffects.arc` and friends, and records address
    them exactly like base archives (`SVMesh\anims\...anm`). A resolver that
    only reads the game install therefore reports every mod-shipped clip as
    MISSING - which is a false failure, and a loud one, because an anim gate
    that cries wolf gets waived instead of fixed.

    DE-DUPLICATED BY REAL PATH. The determinism (`det-2x`) run stages
    `local/b<N>_run2/Resources` as a JUNCTION to `work/<mod>/Resources`, so a raw
    glob reports the same archive up to six times. Six rows naming one file made
    a round-2 vet finding read as "five stale scratch archives" when it was one
    inode; a de-duplicated list cannot tell that story.
    """
    out = []
    for env_name in (_SHIP_ENV, 'SVC_MOD_RESOURCES'):
        env = os.environ.get(env_name)
        if env:
            out.append(Path(env))
    # the standard staged layouts, relative to the build's CWD
    for pat in ('work/*/Resources', 'local/*/Resources'):
        out.extend(sorted(Path('.').glob(pat)))
    uniq, seen = [], set()
    for p in out:
        if not p.is_dir():
            continue
        try:
            rp = p.resolve()
        except OSError:
            rp = p
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(p)
    return uniq


def _arc_dirs(mod_resources=None):
    g = game_dir()
    dirs = []
    if mod_resources:
        dirs.append(Path(mod_resources))
    dirs += mod_resource_dirs()          # mod archives shadow the base game
    dirs += [g / 'Resources',
             g / 'Resources' / 'xpack',
             g / 'Resources' / 'XPack2',
             g / 'Resources' / 'XPack3',
             g / 'Resources' / 'XPack4']
    return dirs


def arcs_available(mod_resources=None):
    """True iff at least Creatures.arc is reachable - the precondition for every
    asset-level gate in this module. Callers use this to decide between running
    the gate and reporting it UNAVAILABLE (never between running it and silently
    passing)."""
    for d in _arc_dirs(mod_resources):
        if (d / 'Creatures.arc').exists():
            return True
    return False


def split_ref(dbr_path):
    r"""`Creatures\Monster\Skeleton\X.msh` -> ('Creatures', 'monster\skeleton\x.msh')."""
    p = str(dbr_path).replace('/', '\\').lstrip('\\')
    head, _, rest = p.partition('\\')
    return head, rest.lower()


def _load_arcs(archive_name, mod_resources=None):
    r"""EVERY reachable archive of this name, in resolution order (mod dirs first,
    then the game install), as [(path, ArcArchive, {inner_name: entry})].

    SHADOWING IS PER ENTRY, NOT PER ARCHIVE - that is what the engine does, and
    resolving only the FIRST archive of a name is a false-failure generator: the
    moment the mod shipped an archive carrying a base-game NAME (the 2026-08-06
    PR-2 dye layer stages an ADDITIVE 288-entry `work\<mod>\Resources\Creatures.arc`
    beside the base game's 3,520-entry one), every base-game asset under that name
    read as MISSING. That surfaced as 65 bogus "UNRESOLVED ANIMATION" offenders in
    `champion_mesh.verify` - the exact "anim gate that cries wolf" its own docstring
    warns about. A mod archive still WINS for any entry it actually contains; it
    just no longer deletes the entries it does not.
    """
    key = (archive_name.lower(), str(mod_resources or ''))
    if key in _ARC_CACHE:
        return _ARC_CACHE[key]
    chain, seen = [], set()
    for d in _arc_dirs(mod_resources):
        p = d / (archive_name + '.arc')
        if not p.exists():
            continue
        try:
            rp = p.resolve()
        except OSError:
            rp = p
        if rp in seen:
            continue
        seen.add(rp)
        a = ArcArchive.from_file(p)
        idx = {}
        for e in a.entries:
            if e.entry_type == 3:
                idx.setdefault(e.name.lower().replace('/', '\\'), e)
        chain.append((p, a, idx))
    _ARC_CACHE[key] = chain
    return chain


def _load_arc(archive_name, mod_resources=None):
    """Back-compat single-archive accessor: the FIRST reachable archive of this
    name, or (None, None). Prefer `_load_arcs` - see its docstring."""
    chain = _load_arcs(archive_name, mod_resources)
    return (chain[0][0], chain[0][1]) if chain else (None, None)


def read_asset(dbr_path, mod_resources=None):
    """(bytes, arc_path) for an art asset addressed the way a .dbr addresses it,
    or (None, arc_path_or_None) when it does not resolve. Walks the whole
    same-name archive chain and returns the FIRST archive that actually carries
    the entry (mod archives shadow the base game per entry)."""
    arcname, inner = split_ref(dbr_path)
    chain = _load_arcs(arcname, mod_resources)
    if not chain:
        return None, None
    for p, a, idx in chain:
        e = idx.get(inner)
        if e is not None:
            return a.get_file(e.name), p
    return None, chain[0][0]


def asset_exists(dbr_path, mod_resources=None):
    data, _ = read_asset(dbr_path, mod_resources)
    return bool(data)


def bones_of(data):
    """Ordered, de-duplicated bone-name table of a .msh (or .anm) blob."""
    out, seen = [], set()
    for m in _BONE_RE.finditer(data):
        b = m.group(0)[:-1].decode('ascii')
        if b not in seen:
            seen.add(b)
            out.append(b)
    return out


def attach_points_of(data):
    r"""Ordered, de-duplicated ATTACHPOINT helper names declared by a .msh blob.

    These are the `AttachPoint { name = "X" ... }` text blocks, NOT bones. They
    are the namespace `particleEffectAttachPoints` mostly draws from, and no
    NUL-anchored scan can find them - see the module docstring.
    """
    out, seen = [], set()
    for blk in _ATTACH_BLOCK_RE.findall(data):
        m = _NAME_KV_RE.search(blk)
        if not m:
            continue
        n = m.group(1).decode('ascii', 'replace')
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def rig_names_of(data):
    r"""EVERY name an attach value may legally resolve to on this rig: the bone
    table UNION the AttachPoint table.

    This is the only correct input to an "is this attach point present on the
    wearer's mesh?" gate. `bones_of()` alone answers a different question and
    reports every AttachPoint name as missing (b104 R-250: that blind spot was
    once measured, believed, and written into the rulings ledger as design law).
    """
    out, seen = [], set()
    for n in list(bones_of(data)) + list(attach_points_of(data)):
        if n.lower() not in seen:
            seen.add(n.lower())
            out.append(n)
    return out


def embedded_fx_attachments_of(data):
    r"""[(attach_point, entity_ref)] for every `CreateEntity` block in a .msh.

    `embedded_fx_of()` answers WHAT a mesh emits; this answers WHERE it hangs it.
    Copying a mesh-embedded effect onto another creature faithfully needs both,
    and both must be DERIVED from the binary rather than asserted in a comment.
    """
    out = []
    for blk in _CREATE_ENTITY_RE.findall(data):
        a = _ATTACH_KV_RE.search(blk)
        e = _ENTITY_KV_RE.search(blk)
        out.append((a.group(1).decode('ascii', 'replace') if a else None,
                    e.group(1).decode('ascii', 'replace') if e else None))
    return out


def embedded_fx_of(data):
    """[effect references] compiled into a mesh blob. EMPTY == cannot emit FX.

    This is the exact layer R-102 proved the Enslaver's green lives in.
    """
    lo = data.lower()
    if not any(mk in lo for mk in _FX_MARKERS):
        return []
    refs = []
    for s in _STR_RE.findall(data):
        # the mesh stores these inside a text block: `entity = "....dbr";` - so
        # strip the punctuation the exporter wraps around the path before
        # testing the extension, or every ref reads as "unparsed".
        t = s.decode('ascii', 'replace').strip().strip(';').strip().strip('"').strip()
        if '=' in t:
            t = t.split('=', 1)[1].strip().strip(';').strip().strip('"').strip()
        tl = t.lower()
        if tl.endswith('.pfx') or tl.endswith('_fx.dbr') \
                or (tl.endswith('.dbr') and '\\effects\\' in tl):
            refs.append(t)
    if not refs:
        # CreateEntity present but the entity string did not match the shapes
        # above: report the raw marker rather than claiming the mesh is clean.
        refs.append('<CreateEntity block, entity ref unparsed>')
    return sorted(set(refs))


def mesh_report(dbr_path, mod_resources=None):
    """{'exists','size','bones','attach','fx','fx_at','arc'} - the row a gate prints."""
    data, arcp = read_asset(dbr_path, mod_resources)
    if not data:
        return {'exists': False, 'size': 0, 'bones': [], 'attach': [], 'fx': [],
                'fx_at': [], 'arc': str(arcp) if arcp else None}
    return {'exists': True, 'size': len(data), 'bones': bones_of(data),
            'attach': attach_points_of(data), 'fx': embedded_fx_of(data),
            'fx_at': embedded_fx_attachments_of(data),
            'arc': str(arcp) if arcp else None}
