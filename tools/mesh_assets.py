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

# A mesh "carries embedded FX" iff its binary names an effect entity / particle.
_FX_MARKERS = (b'createentity', b'.pfx')

_ARC_CACHE = {}
_MISSING = object()


def game_dir():
    return Path(os.environ.get('SVC_TQAE_DIR', _DEFAULT_GAME))


def mod_resource_dirs():
    r"""The MOD's own staged `Resources` dirs, in the order the engine sees them.

    A creature reference is NOT necessarily a base-game asset: this mod ships
    `SVMesh.arc`, `drx.arc`, `DRXeffects.arc` and friends, and records address
    them exactly like base archives (`SVMesh\anims\...anm`). A resolver that
    only reads the game install therefore reports every mod-shipped clip as
    MISSING - which is a false failure, and a loud one, because an anim gate
    that cries wolf gets waived instead of fixed.
    """
    out = []
    env = os.environ.get('SVC_MOD_RESOURCES')
    if env:
        out.append(Path(env))
    # the standard staged layouts, relative to the build's CWD
    for pat in ('work/*/Resources', 'local/*/Resources'):
        out.extend(sorted(Path('.').glob(pat)))
    return [p for p in out if p.is_dir()]


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
    """{'exists','size','bones','fx','arc'} for one mesh - the row a gate prints."""
    data, arcp = read_asset(dbr_path, mod_resources)
    if not data:
        return {'exists': False, 'size': 0, 'bones': [], 'fx': [],
                'arc': str(arcp) if arcp else None}
    return {'exists': True, 'size': len(data), 'bones': bones_of(data),
            'fx': embedded_fx_of(data), 'arc': str(arcp) if arcp else None}
