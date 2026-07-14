"""Sample the BRIGHTEST DXT endpoints (emissive glow spots + FX energy color)."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive
GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'


def bright_color(arcpath, inner):
    p = Path(arcpath)
    if not p.exists():
        return f"(arc missing {arcpath})"
    arc = ArcArchive.from_file(p)
    want = inner.lower().replace('\\', '/')
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == want:
            d = arc.decompress(e)
            pos = d.find(b'DDSR')
            if pos < 0:
                return "no DDSR"
            fourcc = d[pos + 84:pos + 88]
            off = pos + 128
            blk = 8 if fourcc == b'DXT1' else 16
            co = 0 if fourcc == b'DXT1' else 8
            best = (-1, 0, 0, 0)
            grn = (-1, 0, 0, 0)  # most-green
            p2 = off
            n = 0
            while p2 + blk <= len(d) and n < 60000:
                for cc in struct.unpack_from('<HH', d, p2 + co):
                    r = ((cc >> 11) & 0x1f) << 3
                    g = ((cc >> 5) & 0x3f) << 2
                    b = (cc & 0x1f) << 3
                    lum = r + g + b
                    if lum > best[0]:
                        best = (lum, r, g, b)
                    gscore = g - max(r, b)
                    if gscore > grn[0]:
                        grn = (gscore, r, g, b)
                    n += 1
                p2 += blk
            return (f"{fourcc.decode(errors='replace')} brightest=({best[1]},{best[2]},{best[3]}) "
                    f"most-green=({grn[1]},{grn[2]},{grn[3]})")
    return "(entry not found)"


T = [
    ('Creatures', 'Monster/ShadowStalker/ShadowStalker01Glow.tex', 'marauder mesh glow spots'),
    ('Effects', 'Textures/343bolt_02.tex', 'shadowcloak bolt energy'),
    ('Effects', 'Textures/lightning_missile01b.tex', 'shadowcloak lightning'),
    ('Effects', 'Textures/343Smoke_01.tex', 'smoke tex (control-grey)'),
    ('Creatures', 'Monster/Skeleton/newskeleton_grean.tex', 'green control'),
]
for arcname, inner, label in T:
    print(f"  {label:28s} {bright_color(GAME + f'/{arcname}.arc', inner)}")
