import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive
GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'
MOD = r"C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV/Resources"


def stat(arcpath, inner):
    p = Path(arcpath)
    if not p.exists():
        return f'(no arc {Path(arcpath).name})'
    arc = ArcArchive.from_file(p)
    want = inner.lower().replace('\\', '/')
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == want:
            d = arc.decompress(e)
            pos = d.find(b'DDSR')
            if pos < 0:
                return 'noDDSR'
            fourcc = d[pos + 84:pos + 88]
            off = pos + 128
            blk = 8 if fourcc == b'DXT1' else 16
            co = 0 if fourcc == b'DXT1' else 8
            rs = gs = bs = n = 0
            mx = 0
            gr = -999
            p2 = off
            while p2 + blk <= len(d) and n < 60000:
                for cc in struct.unpack_from('<HH', d, p2 + co):
                    r = ((cc >> 11) & 0x1f) << 3
                    g = ((cc >> 5) & 0x3f) << 2
                    b = (cc & 0x1f) << 3
                    rs += r; gs += g; bs += b; n += 1
                    mx = max(mx, r + g + b)
                    gr = max(gr, g - max(r, b))
                p2 += blk
            if n:
                return f"mean=({rs/n:.0f},{gs/n:.0f},{bs/n:.0f}) maxLum={mx} greenest={gr:+d}"
    return '(not found)'


def show(lbl, arc, base, glow):
    print(f"{lbl}")
    print(f"   base[{base.split('/')[-1]}] = {stat(arc, base)}")
    if glow:
        print(f"   glow[{glow.split('/')[-1]}] = {stat(arc, glow)}")


# NightStalker01 could be in base Creatures.arc or XPack folders
for arcname in ['Creatures', 'XPack/Creatures', 'XPack2/Creatures', 'XPack3/Creatures']:
    show(f'NightStalker01 [{arcname}]', GAME + f'/{arcname}.arc',
         'Creatures/Monster/Nightstalker/NightStalker01.tex',
         'Creatures/Monster/Nightstalker/NightStalker01Glow.tex')
# darkstalker in mod arcs
for arcname in ['drx', 'DRXtextures', 'SVTextures']:
    show(f'darkstalker01 [{arcname}]', MOD + f'/{arcname}.arc',
         'summonersdelighttextures/creatures/monsters/darkstalker/darkstalker01.tex',
         'summonersdelighttextures/creatures/monsters/darkstalker/darkstalker01glow.tex')
