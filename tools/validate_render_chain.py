r"""A9 RENDER-CHAIN CONTRACT (build29 + build30/D5): soul-granted summon pets must
be VISIBLE - their mesh, base texture, and party-UI status icons must resolve in
the SHIPPED art archives, AND the mesh's OWN internal shader references must
resolve under the engine's real (XPack-folder-SCOPED) archive rule, or the pet
spawns invisible / textureless.

Two independent signals:
  (1) RECORD-LEVEL resolution (build29): the pet record's mesh/baseTexture/icons
      resolve in some shipped arc (TQ archive-name resolution, incl. the XPack
      second-component convention). This is the "invisible Narok" class.
  (2) MESH-INTERNAL shader closure (build30/D5): OPEN the pet's mesh and resolve
      every shader (.ssh) reference it embeds, using ENGINE-FAITHFUL scoping:
      `XPackN\<Arc>\<inner>` resolves ONLY in `Resources\XPackN\<Arc>.arc`, never
      by merging that archive with the base-Resources archive of the same name.
      This catches the blade-dancer / melinoe family (build29 shipped it twice):
      DRX\meshes\melinoe01.msh embeds `XPack\Shaders\standardblendedglowskinned.ssh`,
      which the engine looks for in Resources\XPack\Shaders.arc (IT shaders, absent
      there) - the shader is only in base Resources\Shaders.arc - so the body's
      skin material never renders (invisible body, floating weapons). Every
      record's art ref RESOLVED statically, so signal (1) passed it; resolution is
      not rendering. Signal (2) is the renderability check.

Scope (bounded, fail-loud where we author): every pet reachable from a soul's
granted summon skill (itemSkillName -> spawnObjects), plus the summon skill's own
skill-bar icons. A MOD-AUTHORED pet (records\\skills\\soulskills\\...) with an
unresolvable mesh/texture/icon OR an unresolvable mesh-internal shader FAILS the
build; anything else WARNs (upstream SV/DRX data debt is reported, not blocking).
A CURIOSITY section additionally reports every OTHER record (hostile monsters,
proxies) that shares a mesh whose internal shader does not resolve - so the whole
shared-render-chain family is visible - without gating on upstream debt.

usage: py tools/validate_render_chain.py <mod.arz> <mod_resources_dir> <game_dir>
exit 0 = PASS, 1 = FAIL, 2 = load error.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase   # noqa: E402
from arc_patcher import ArcArchive    # noqa: E402

SOUL_MARKERS = ('\\soul\\', '/soul/')
MOD_PET_PREFIX = 'records\\skills\\soulskills\\pets\\'
XPACK_SCOPES = ('xpack', 'xpack2', 'xpack3', 'xpack4')
_MESH_STR_RE = re.compile(rb'[\x20-\x7e]{4,}')


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


class ArcIndex:
    """Lazy per-archive file index across the search roots (build29 model:
    same-named archives across roots are MERGED into one name set). Used for the
    record-level resolution signal, kept byte-for-byte compatible with build29."""

    def __init__(self, roots):
        self.roots = [Path(r) for r in roots if r and Path(r).is_dir()]
        self._cache = {}

    def _index(self, archive):
        key = archive.lower()
        if key in self._cache:
            return self._cache[key]
        names = set()
        for root in self.roots:
            cand = root / f"{archive}.arc"
            if not cand.exists():
                hits = [p for p in root.glob('*.arc')
                        if p.stem.lower() == key]
                cand = hits[0] if hits else None
            if cand and cand.exists():
                try:
                    arc = ArcArchive.from_file(cand)
                except Exception:
                    continue
                for e in arc.entries:
                    if e.name:
                        names.add(e.name.lower().replace('\\', '/'))
        self._cache[key] = names
        return names

    def resolves(self, ref):
        parts = str(ref).replace('/', '\\').split('\\')
        if len(parts) < 2:
            return False
        if parts[0].lower() in XPACK_SCOPES and len(parts) >= 3:
            if '/'.join(parts[2:]).lower() in self._index(parts[1]):
                return True
        inner = '/'.join(parts[1:]).lower()
        return inner in self._index(parts[0])


class EngineArcResolver:
    """ENGINE-FAITHFUL archive resolution (build30/D5). Unlike ArcIndex, it does
    NOT merge same-named archives across roots: an `XPackN\\<Arc>\\<inner>` ref is
    resolved ONLY in `<game>\\Resources\\XPackN\\<Arc>.arc`; a plain `<Arc>\\<inner>`
    ref is resolved in the mod Resources <Arc>.arc first, then base
    `<game>\\Resources\\<Arc>.arc`. This mirrors how TQAE actually scopes the
    XPack expansion folders, which is the signal build29's merged model missed.

    Proven by two base-game data points:
      - base PC meshes embed `XPack2\\shaders\\standardskinnedfresnelmask.ssh`,
        present ONLY in Resources\\XPack2\\Shaders.arc, and the PC renders.
      - base ElderDjinn01.msh embeds `Shaders\\StandardBlendedGlowSkinned.ssh`
        (base-scoped) and renders; DRX melinoe01.msh embeds the SAME shader via
        `XPack\\Shaders\\...` (-> empty IT Shaders.arc) and is invisible.
    """

    def __init__(self, mod_resources, game_dir):
        self.mod_res = Path(mod_resources) if mod_resources else None
        self.game = Path(game_dir)
        self._arc_names = {}   # resolved arc Path -> set(names) (or None if absent)
        self._arc_obj = {}     # resolved arc Path -> parsed ArcArchive (parse once)

    def _arc(self, arc_path):
        """Parse an ArcArchive once and cache it (arcs are large; re-parsing per
        mesh is O(minutes))."""
        if arc_path is None:
            return None
        key = str(arc_path).lower()
        if key in self._arc_obj:
            return self._arc_obj[key]
        obj = None
        if arc_path.exists():
            try:
                obj = ArcArchive.from_file(arc_path)
            except Exception:
                obj = None
        self._arc_obj[key] = obj
        return obj

    def _names(self, arc_path):
        if arc_path is None:
            return None
        key = str(arc_path).lower()
        if key in self._arc_names:
            return self._arc_names[key]
        arc = self._arc(arc_path)
        names = None
        if arc is not None:
            names = set()
            for e in arc.entries:
                if e.name:
                    names.add(e.name.lower().replace('\\', '/'))
        self._arc_names[key] = names
        return names

    def _arc_in(self, folder, arcname):
        """case-insensitive <folder>/<arcname>.arc lookup."""
        if folder is None or not Path(folder).is_dir():
            return None
        cand = Path(folder) / f"{arcname}.arc"
        if cand.exists():
            return cand
        hits = [p for p in Path(folder).glob('*.arc') if p.stem.lower() == arcname.lower()]
        return hits[0] if hits else None

    def resolve(self, ref):
        """Return (ok, detail). detail names the scoped archive it looked in."""
        parts = str(ref).replace('/', '\\').split('\\')
        if len(parts) < 2:
            return (False, 'too-short')
        p0 = parts[0].lower()
        if p0 in XPACK_SCOPES and len(parts) >= 3:
            arcname = parts[1]
            inner = '/'.join(parts[2:]).lower()
            arc = self._arc_in(self.game / 'Resources' / parts[0], arcname)
            names = self._names(arc)
            if names is None:
                return (False, f'no {parts[0]}\\{arcname}.arc')
            return (inner in names, f'{parts[0]}\\{arcname}.arc')
        arcname = parts[0]
        inner = '/'.join(parts[1:]).lower()
        for label, folder in (('mod', self.mod_res),
                              ('base', self.game / 'Resources')):
            arc = self._arc_in(folder, arcname)
            names = self._names(arc)
            if names is not None and inner in names:
                return (True, f'{label}:{arcname}.arc')
        return (False, f'{arcname}.arc (mod+base)')

    def open_mesh_bytes(self, mesh_ref):
        """Return the decompressed mesh bytes, or None if the mesh entry is
        unresolvable under engine-faithful scoping."""
        parts = str(mesh_ref).replace('/', '\\').split('\\')
        if len(parts) < 2:
            return None
        p0 = parts[0].lower()
        if p0 in XPACK_SCOPES and len(parts) >= 3:
            folder = self.game / 'Resources' / parts[0]
            arcname = parts[1]
            inner = '/'.join(parts[2:]).lower()
            arcs = [self._arc_in(folder, arcname)]
        else:
            arcname = parts[0]
            inner = '/'.join(parts[1:]).lower()
            arcs = [self._arc_in(self.mod_res, arcname),
                    self._arc_in(self.game / 'Resources', arcname)]
        for arc_path in arcs:
            arc = self._arc(arc_path)
            if arc is None:
                continue
            for e in arc.entries:
                if e.name and e.name.lower().replace('\\', '/') == inner and e.entry_type == 3:
                    try:
                        return arc.decompress(e)
                    except Exception:
                        return None
        return None


_MESH_SHADER_CACHE = {}


def mesh_internal_shaders(resolver, mesh_ref):
    """Return (resolvable_mesh, [(shader_ref, ok, detail), ...]).
    resolvable_mesh False => the mesh entry itself was not found."""
    key = _norm(mesh_ref)
    if key in _MESH_SHADER_CACHE:
        return _MESH_SHADER_CACHE[key]
    data = resolver.open_mesh_bytes(mesh_ref)
    if data is None:
        result = (False, [])
        _MESH_SHADER_CACHE[key] = result
        return result
    shaders = []
    seen = set()
    for m in _MESH_STR_RE.findall(data):
        s = m.decode('latin-1')
        if s.lower().endswith('.ssh') and s.lower() not in seen:
            seen.add(s.lower())
            ok, detail = resolver.resolve(s)
            shaders.append((s, ok, detail))
    result = (True, shaders)
    _MESH_SHADER_CACHE[key] = result
    return result


def validate(arz_path, mod_resources, game_dir):
    db = ArzDatabase.from_arz(Path(arz_path))
    recmap = {_norm(n): n for n in db.record_names()}

    def resolve_rec(p):
        return recmap.get(_norm(p))

    def field(rec, name):
        ff = db.get_fields(rec) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == name and tf.values and str(tf.values[0]).strip():
                return tf.values
        return None

    game = Path(game_dir)
    idx = ArcIndex([mod_resources,
                    game / 'Resources',
                    game / 'Resources' / 'XPack',
                    game / 'Resources' / 'XPack2',
                    game / 'Resources' / 'XPack3'])
    eng = EngineArcResolver(mod_resources, game_dir)

    problems = []
    # mesh_ref(lower) -> (bad_shaders, mesh_missing) for records reachable as pets
    broken_mesh = {}
    pet_mesh = {}          # pet rec -> mesh ref
    checked_pets = 0
    checked_refs = 0
    seen = set()
    for name in db.record_names():
        nl = name.lower()
        if not any(mk in nl for mk in SOUL_MARKERS):
            continue
        isn = field(name, 'itemSkillName')
        if not isn:
            continue
        skill = resolve_rec(str(isn[0]))
        if not skill:
            continue
        spawns = field(skill, 'spawnObjects') or []
        art_checks = []
        for icon_f in ('skillUpBitmapName', 'skillDownBitmapName'):
            v = field(skill, icon_f)
            if v:
                art_checks.append((skill, icon_f, str(v[0])))
        for p in spawns:
            pet = resolve_rec(str(p))
            if not pet or pet in seen:
                continue
            seen.add(pet)
            checked_pets += 1
            for f in ('mesh', 'baseTexture', 'StatusIcon', 'StatusIconRed'):
                v = field(pet, f)
                if v:
                    art_checks.append((pet, f, str(v[0])))
            # signal (2): mesh-internal shader closure (engine-faithful)
            mv = field(pet, 'mesh')
            if mv:
                mesh_ref = str(mv[0])
                pet_mesh[pet] = mesh_ref
                ok_mesh, shaders = mesh_internal_shaders(eng, mesh_ref)
                bad = [(s, d) for (s, o, d) in shaders if not o]
                if (not ok_mesh) or bad:
                    broken_mesh[_norm(mesh_ref)] = (mesh_ref, ok_mesh, bad)
                    mod_authored = _norm(pet).startswith(MOD_PET_PREFIX) or \
                        _norm(pet).startswith('records\\skills\\soulskills\\')
                    sev = 'FAIL' if mod_authored else 'WARN'
                    if not ok_mesh:
                        problems.append((sev, pet, 'mesh',
                                         f'{mesh_ref} :: mesh entry not found under engine scoping'))
                    for s, d in bad:
                        problems.append((sev, pet, 'mesh-shader',
                                         f'{mesh_ref} embeds shader {s} -> UNRESOLVED in {d} (invisible body)'))
        for rec, f, ref in art_checks:
            checked_refs += 1
            if not idx.resolves(ref):
                mod_authored = _norm(rec).startswith(MOD_PET_PREFIX) or \
                    _norm(rec).startswith('records\\skills\\soulskills\\')
                body = f in ('mesh', 'baseTexture')
                sev = 'FAIL' if (mod_authored and body) else 'WARN'
                problems.append((sev, rec, f, ref))

    # CURIOSITY: every OTHER record (hostile monsters, proxies, other pets) that
    # shares a broken-internal-shader mesh - the full shared-render-chain family.
    curiosity = []
    if broken_mesh:
        for rec in db.record_names():
            mv = field(rec, 'mesh')
            if not mv:
                continue
            mref = _norm(str(mv[0]))
            if mref in broken_mesh and rec not in pet_mesh:
                cls = field(rec, 'Class')
                curiosity.append((str(mv[0]), rec, cls[0] if cls else '?'))
    # Optional full sibling sweep (opt-in; opens every distinct creature mesh, so
    # it is slow). Surfaces meshes NOT reached via pets whose internal shaders
    # fail (e.g. bastien02 / supra weapons found in D5 recon). Enable with
    # D5_FULL_MESH_SCAN=1.
    if os.environ.get('D5_FULL_MESH_SCAN') == '1':
        scanned = set(broken_mesh)
        for rec in db.record_names():
            mv = field(rec, 'mesh')
            if not mv:
                continue
            mref = str(mv[0])
            key = _norm(mref)
            if key in scanned:
                continue
            scanned.add(key)
            ok_mesh, shaders = mesh_internal_shaders(eng, mref)
            bad = [(s, d) for (s, o, d) in shaders if not o]
            if ok_mesh and bad:
                cls = field(rec, 'Class')
                curiosity.append((mref + '  [NEW]', rec, cls[0] if cls else '?'))

    print("=" * 72)
    print("SUMMON-PET RENDER-CHAIN VALIDATOR (A9 + D5 mesh-shader closure)")
    print(f"  pets checked: {checked_pets}; art refs checked: {checked_refs}")
    fails = 0
    for sev, rec, f, ref in sorted(set(problems)):
        print(f"  {sev}: {rec} :: {f}: {ref}")
        if sev == 'FAIL':
            fails += 1
    if curiosity:
        print("  --- CURIOSITY: records sharing a broken-internal-shader mesh ---")
        for mref, rec, cls in sorted(set(curiosity)):
            print(f"  NOTE: {rec} ({cls}) uses {mref}")
    if fails:
        print(f"RESULT: FAIL - {fails} mod-authored unrenderable pet art/shader ref(s)")
        return 1
    print(f"RESULT: PASS ({len(problems)} upstream WARN(s))")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(validate(sys.argv[1], sys.argv[2], sys.argv[3]))
