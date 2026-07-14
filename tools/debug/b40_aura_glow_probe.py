"""B40 READ-ONLY: resolve the boss alacrity aura FX color + the shadowstalker glow
texture, and list candidate dark shadowstalker skins."""
import sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'
MOD = r"C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV/Resources"


def norm(p):
    return str(p).replace('/', '\\').lower().strip()


def resolve(db, path):
    want = norm(path)
    for n in db.record_names():
        if norm(n) == want:
            return n
    return None


def dumprec(db, rec):
    real = resolve(db, rec)
    print(f"\n----- {rec}")
    if not real:
        print("  *** NOT PRESENT ***")
        return None
    f = db.get_fields(real)
    for key, tf in f.items():
        b = key.split('###')[0]
        if any(k in b.lower() for k in ('effect', 'texture', 'color', 'particle', 'file', 'pfx', 'class', 'template')):
            print(f"    {b:30s} = {tf.values}")
    return f


def grab_arc_strings(arcpath, inner, filt):
    p = Path(arcpath)
    if not p.exists():
        return None
    arc = ArcArchive.from_file(p)
    want = inner.lower().replace('\\', '/')
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == want:
            data = arc.decompress(e)
            strs = re.findall(rb'[\x20-\x7e]{4,}', data or b'')
            return [s.decode('latin1') for s in strs if any(x in s.lower() for x in filt)]
    return None


def main():
    arz = sys.argv[1]
    db = ArzDatabase.from_arz(Path(arz))

    print("################ boss alacrity aura FX record ################")
    f = dumprec(db, r'Records\Effects\MonsterFX\343_AlacrityAuraFX.dbr')
    # chase referenced .dbr/.pfx one hop
    if f:
        for key, tf in f.items():
            for v in (tf.values or []):
                if isinstance(v, str) and v.lower().endswith('.dbr'):
                    dumprec(db, v)

    print("\n\n################ Alacrity aura .pfx texture refs (color hint) ################")
    # find the effectFile pfx from the FX record
    for pfx in ['effects/monsterfx/343_alacrityaura.pfx', 'monsterfx/343_alacrityaura.pfx']:
        for root, arcname in [(GAME, 'Effects'), (MOD, 'SVEffects')]:
            hits = grab_arc_strings(root + f'/{arcname}.arc', pfx, [b'.tex', b'green', b'color'])
            if hits:
                print(f"  [{arcname}] {pfx}:")
                for x in hits:
                    print('    ', x)

    print("\n\n################ ShadowStalker01Glow.tex + candidate dark shadowstalker skins ################")
    # list all shadowstalker/stalker skins available in arcs
    for root, arcs in [(GAME, ['Creatures']),
                       (MOD, ['DRXtextures', 'drx', 'SVTextures'])]:
        for arcname in arcs:
            p = Path(root) / f'{arcname}.arc'
            if not p.exists():
                continue
            arc = ArcArchive.from_file(p)
            for e in arc.entries:
                nm = (e.name or '').lower()
                if ('stalker' in nm) and nm.endswith('.tex'):
                    print(f"  [{arcname}] {e.name}")


if __name__ == '__main__':
    main()
