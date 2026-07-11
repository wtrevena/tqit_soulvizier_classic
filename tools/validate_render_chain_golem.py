r"""D5 RENDER-CHAIN GATE for the Rune Golem graft (fail-loud).

The Rune Golem is a MASTERY skill (not a soul), so the soul-scoped
validate_render_chain.py does not cover it. This gate proves the graft's whole
pet render chain resolves from OUR SHIPPED PAYLOAD ALONE - the mod Resources dir
(work/.../Resources, which must contain the committed minimal _DRX_Meshes.arc +
_DRX_Textures.arc) UNION the base game - and NEVER from SVAERA's unshipped
_DRX_Meshes/_DRX_Textures/_DRX_Effects arcs. The SVAERA Workshop dir is
deliberately NOT a search root: if any golem art resolves only there, this gate
FAILS.

Checks, engine-faithfully (EngineArcResolver scoping, the build30/D5 law):
  - the summon skill's spawnObjects (20 pet tiers)
  - each pet: mesh, monsterBaseTexture (skins), StatusIcon/StatusIconRed, and the
    SVAERA spawn/respawn anim (unarmedSpawnAnim / unarmedRespawnAnim)
  - the mesh's OWN internal shader (.ssh) + texture (.tex) refs
  - the summon skill's + catalyst pet-skill's skill-bar icons

usage: py tools/validate_render_chain_golem.py <mod.arz> <mod_resources_dir> <game_dir>
exit 0 = PASS, 1 = FAIL (invisible/textureless golem), 2 = load error.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase           # noqa: E402
from validate_render_chain import (            # noqa: E402
    EngineArcResolver, ArcIndex, mesh_internal_shaders, _norm, XPACK_SCOPES)

SUMMON = r'records\xpack2\skills\runemaster\_drx_runegolem.dbr'
CATALYSTBUFF = r'records\xpack2\skills\runemaster\_drx_runegolem_petskill_catalystbuff.dbr'
_TEX_RE = re.compile(rb'[\x20-\x7e]{4,}')


def _mesh_internal_textures(resolver, mesh_ref):
    """Return [(tex_ref, ok, detail)] for every .tex the mesh embeds (the D5 'law
    of textures' beyond shaders: the golem mesh hardcodes its skin/glow archive)."""
    data = resolver.open_mesh_bytes(mesh_ref)
    if data is None:
        return None
    out, seen = [], set()
    for m in _TEX_RE.findall(data):
        s = m.decode('latin-1')
        sl = s.lower()
        if sl.endswith('.tex') and sl not in seen:
            seen.add(sl)
            ok, detail = resolver.resolve(s)
            out.append((s, ok, detail))
    return out


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
    # NOTE: SVAERA is intentionally NOT a root -> proves resolution from ours alone.
    idx = ArcIndex([mod_resources, game / 'Resources',
                    game / 'Resources' / 'XPack', game / 'Resources' / 'XPack2',
                    game / 'Resources' / 'XPack3'])
    eng = EngineArcResolver(mod_resources, game_dir)

    summon = resolve_rec(SUMMON)
    if not summon:
        print(f"RESULT: FAIL - summon skill {SUMMON} not in arz")
        return 1
    pets = field(summon, 'spawnObjects') or []
    print("=" * 72)
    print("RUNE GOLEM RENDER-CHAIN GATE (D5; resolve vs OUR arcs + base, never SVAERA)")
    print(f"  summon skill spawns {len(pets)} pet tier(s)")

    problems = []
    checked_art = 0
    meshes_done = set()
    for p in pets:
        pet = resolve_rec(str(p))
        if not pet:
            problems.append(('pet-missing', str(p), 'spawnObjects target not in arz'))
            continue
        # record-level art (merged resolution)
        for f in ('mesh', 'monsterBaseTexture', 'StatusIcon', 'StatusIconRed'):
            v = field(pet, f)
            if not v:
                continue
            for ref in v:
                checked_art += 1
                if not idx.resolves(str(ref)):
                    problems.append((pet.split('\\')[-1], f, f'{ref} UNRESOLVED (ours+base)'))
        # spawn anim (SVAERA-authored, must be in our _DRX_Meshes.arc)
        for f in ('unarmedSpawnAnim', 'unarmedRespawnAnim'):
            v = field(pet, f)
            if not v:
                continue
            ref = str(v[0])
            checked_art += 1
            ok, detail = eng.resolve(ref)
            if not ok:
                problems.append((pet.split('\\')[-1], f, f'{ref} UNRESOLVED in {detail}'))
        # mesh-internal shader + texture closure (engine-scoped)
        mv = field(pet, 'mesh')
        if mv and _norm(str(mv[0])) not in meshes_done:
            meshes_done.add(_norm(str(mv[0])))
            mesh_ref = str(mv[0])
            ok_mesh, shaders = mesh_internal_shaders(eng, mesh_ref)
            if not ok_mesh:
                problems.append((mesh_ref, 'mesh', 'mesh bytes not openable from our arcs'))
            for s, ok, d in shaders:
                checked_art += 1
                if not ok:
                    problems.append((mesh_ref, 'mesh-shader', f'{s} UNRESOLVED in {d}'))
            texs = _mesh_internal_textures(eng, mesh_ref)
            for s, ok, d in (texs or []):
                checked_art += 1
                if not ok:
                    problems.append((mesh_ref, 'mesh-texture', f'{s} UNRESOLVED in {d}'))

    # skill-bar icons (summon + catalyst pet-skill) - a grey box is not invisible
    # pet, but still a shipped-art contract; resolve them too.
    for rec_path, label in ((SUMMON, 'summon'), (CATALYSTBUFF, 'catalyst')):
        rec = resolve_rec(rec_path)
        if not rec:
            continue
        for f in ('skillUpBitmapName', 'skillDownBitmapName'):
            v = field(rec, f)
            if not v:
                continue
            checked_art += 1
            if not idx.resolves(str(v[0])):
                problems.append((f'{label}-skill', f, f'{v[0]} UNRESOLVED (ours+base)'))

    print(f"  art refs checked: {checked_art}")
    fails = 0
    for who, f, msg in sorted(set(problems)):
        print(f"  FAIL: {who} :: {f}: {msg}")
        fails += 1
    if fails:
        print(f"RESULT: FAIL - {fails} golem render ref(s) do not resolve from our payload")
        return 1
    print("RESULT: PASS - the Rune Golem renders from our shipped arcs + base alone")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(validate(sys.argv[1], sys.argv[2], sys.argv[3]))
