"""Sample brightness+greenness of candidate ShadowStalker skin/glow pairs to find a
DARK, non-green marauder skin (base dark + glow dark/non-green)."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive
GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'
MOD = r"C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV/Resources"

ARCS = {
    'Creatures': GAME + '/Creatures.arc',
    'DRXtextures': MOD + '/DRXtextures.arc',
    'SVTextures': MOD + '/SVTextures.arc',
    'drx': MOD + '/drx.arc',
}


def stat(arcpath, inner):
    p = Path(arcpath)
    if not p.exists():
        return None
    arc = ArcArchive.from_file(p)
    want = inner.lower().replace('\\', '/')
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == want:
            d = arc.decompress(e)
            pos = d.find(b'DDSR')
            if pos < 0:
                return None
            fourcc = d[pos + 84:pos + 88]
            off = pos + 128
            blk = 8 if fourcc == b'DXT1' else 16
            co = 0 if fourcc == b'DXT1' else 8
            rs = gs = bs = n = 0
            bestlum = 0
            greenest = -999
            p2 = off
            while p2 + blk <= len(d) and n < 60000:
                for cc in struct.unpack_from('<HH', d, p2 + co):
                    r = ((cc >> 11) & 0x1f) << 3
                    g = ((cc >> 5) & 0x3f) << 2
                    b = (cc & 0x1f) << 3
                    rs += r; gs += g; bs += b; n += 1
                    bestlum = max(bestlum, r + g + b)
                    greenest = max(greenest, g - max(r, b))
                p2 += blk
            if n:
                return (rs / n, gs / n, bs / n, bestlum, greenest)
    return None


PAIRS = [
    ('Creatures', 'Monster/ShadowStalker/ShadowStalker01.tex', 'Monster/ShadowStalker/ShadowStalker01Glow.tex', 'DEFAULT (current marauder)'),
    ('SVTextures', 'creatures/shadowstalker/nazur.tex', 'creatures/shadowstalker/nazurglow.tex', 'SV nazur'),
    ('SVTextures', 'creatures/shadowstalker/wahr.tex', 'creatures/shadowstalker/wahrglow.tex', 'SV wahr'),
    ('DRXtextures', 'creatures/nightstalker/nightstalker_ikaie.tex', 'creatures/nightstalker/nightstalker_ikaieglow.tex', 'DRX nightstalker ikaie'),
    ('DRXtextures', 'creatures/shadowstalker/shadowstalker_iceheart.tex', None, 'DRX iceheart (Hunt)'),
    ('DRXtextures', 'creatures/nightstalker/nightstalker_serafemos.tex', None, 'DRX serafemos'),
]


def fmt(s):
    if not s:
        return "MISSING"
    r, g, b, bl, gr = s
    return f"mean=({r:4.0f},{g:4.0f},{b:4.0f}) maxLum={bl:4d} greenest={gr:+4d}"


for arcname, base, glow, label in PAIRS:
    bs = stat(ARCS[arcname], base)
    gs = stat(ARCS[arcname], glow) if glow else None
    print(f"\n{label}  [{arcname}]")
    print(f"   base: {fmt(bs)}")
    print(f"   glow: {fmt(gs) if glow else '(no paired glow -> mesh default glow used)'}")
