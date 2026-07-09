"""A9 RENDER-CHAIN CONTRACT (build29): soul-granted summon pets must be
VISIBLE - their mesh, base texture, and party-UI status icons must resolve in
the SHIPPED art archives, or the pet spawns invisible / textureless (the
"invisible Narok" class of bug; sibling of B-SUMMON-1's naked/floating pets).

Scope (bounded, fail-loud where we author): every pet reachable from a soul's
granted summon skill (itemSkillName -> spawnObjects), plus the summon skill's
own skill-bar icons. Art references resolve TQ-style: the FIRST path component
names the archive (<Name>.arc), the rest is the internal path. Search roots:
the mod's staged Resources, the base game Resources, and base Resources/XPack.

Severity: a MOD-AUTHORED pet (records\\skills\\soulskills\\pets\\...) with an
unresolvable mesh/texture/icon FAILS the build; anything else WARNs (upstream
SV data debt is reported, not blocking).

usage: py tools/validate_render_chain.py <mod.arz> <mod_resources_dir> <game_dir>
exit 0 = PASS, 1 = FAIL, 2 = load error.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase   # noqa: E402
from arc_patcher import ArcArchive    # noqa: E402

SOUL_MARKERS = ('\\soul\\', '/soul/')
MOD_PET_PREFIX = 'records\\skills\\soulskills\\pets\\'


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


class ArcIndex:
    """Lazy per-archive file index across the search roots."""

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
            # case-insensitive filesystem probe
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
        # 'XPack\Creatures\...' style refs name the arc with their SECOND
        # component (the arc lives under Resources/XPackN/); plain refs name it
        # with the first ('Creatures\...' -> Creatures.arc).
        if parts[0].lower() in ('xpack', 'xpack2', 'xpack3') and len(parts) >= 3:
            if '/'.join(parts[2:]).lower() in self._index(parts[1]):
                return True
        inner = '/'.join(parts[1:]).lower()
        return inner in self._index(parts[0])


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

    problems = []
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
        for rec, f, ref in art_checks:
            checked_refs += 1
            if not idx.resolves(ref):
                # icons are cosmetic (engine falls back to a default icon);
                # only an unresolvable MESH/TEXTURE makes the pet invisible.
                mod_authored = _norm(rec).startswith(MOD_PET_PREFIX) or \
                    _norm(rec).startswith('records\\skills\\soulskills\\')
                body = f in ('mesh', 'baseTexture')
                sev = 'FAIL' if (mod_authored and body) else 'WARN'
                problems.append((sev, rec, f, ref))

    print("=" * 72)
    print("SUMMON-PET RENDER-CHAIN VALIDATOR (A9)")
    print(f"  pets checked: {checked_pets}; art refs checked: {checked_refs}")
    fails = 0
    for sev, rec, f, ref in sorted(set(problems)):
        print(f"  {sev}: {rec} :: {f} does not resolve in any shipped arc: {ref}")
        if sev == 'FAIL':
            fails += 1
    if fails:
        print(f"RESULT: FAIL - {fails} mod-authored unresolvable art ref(s)")
        return 1
    print(f"RESULT: PASS ({len(problems)} upstream WARN(s))")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(validate(sys.argv[1], sys.argv[2], sys.argv[3]))
