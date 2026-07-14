"""B40 READ-ONLY: extract embedded skin/texture refs from meshes + pfx, to learn
the default ShadowStalker skin color and the shadowcloak/smoke FX texture."""
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive

GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'
MOD = r"C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV/Resources"


def grab(arcpath, inner, filt):
    p = Path(arcpath)
    if not p.exists():
        print(f"  (arc missing: {arcpath})")
        return None
    arc = ArcArchive.from_file(p)
    want = inner.lower().replace('\\', '/')
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == want:
            data = arc.decompress(e)
            if not data:
                print("  (empty entry data)")
                return []
            strs = re.findall(rb'[\x20-\x7e]{4,}', data)
            return [s.decode('latin1') for s in strs
                    if any(x in s.lower() for x in filt)]
    print(f"  (entry not found: {inner})")
    return None


print('=== ShadowStalker.msh embedded texture refs ===')
for x in (grab(GAME + '/Creatures.arc', 'Monster/ShadowStalker/ShadowStalker.msh',
               [b'.tex', b'.tga', b'.ssh']) or []):
    print('  ', x)

print('\n=== RevenantPoison.msh embedded texture/shader refs ===')
for x in (grab(GAME + '/Creatures.arc', 'Monster/Skeleton/RevenantPoison.msh',
               [b'.tex', b'.tga', b'.ssh']) or []):
    print('  ', x)

print('\n=== shadowcloakrunning.pfx embedded refs ===')
got = grab(MOD + '/DRXeffects.arc', 'shadowcloakrunning.pfx', [b'.tex', b'.tga', b'green', b'poison', b'color'])
if got is None:
    got = grab(GAME + '/DRXeffects.arc', 'shadowcloakrunning.pfx', [b'.tex', b'.tga'])
for x in (got or []):
    print('  ', x)

print('\n=== dark_smoke.pfx embedded refs ===')
got = grab(MOD + '/SVEffects.arc', 'ambient/dark_smoke.pfx', [b'.tex', b'.tga', b'color', b'smoke'])
for x in (got or []):
    print('  ', x)
