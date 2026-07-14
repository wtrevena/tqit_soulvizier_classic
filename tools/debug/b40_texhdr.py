import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive
GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'
arc = ArcArchive.from_file(Path(GAME + '/Creatures.arc'))
targets = [
    'monster/shadowstalker/shadowstalker01glow.tex',
    'monster/shadowstalker/shadowstalker01.tex',
    'monster/skeleton/newskeleton_grean.tex',
]
for t in targets:
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == t:
            d = arc.decompress(e)
            ddspos = d.find(b'DDSR')
            print(f"\n{t}  len={len(d)} DDSat={ddspos}")
            print("  first48:", d[:48].hex())
            if ddspos >= 0:
                import struct
                h, w = struct.unpack_from('<II', d, ddspos + 12)
                fourcc = d[ddspos + 84:ddspos + 88]
                print(f"  DDS {w}x{h} fourcc={fourcc!r}")
                # mean of DXT endpoint colors
                off = ddspos + 128
                if fourcc in (b'DXT1', b'DXT3', b'DXT5'):
                    blk = 8 if fourcc == b'DXT1' else 16
                    co = 0 if fourcc == b'DXT1' else 8
                    rs = gs = bs = n = 0
                    pos = off
                    while pos + blk <= len(d) and n < 40000:
                        for cc in struct.unpack_from('<HH', d, pos + co):
                            rs += ((cc >> 11) & 0x1f) << 3
                            gs += ((cc >> 5) & 0x3f) << 2
                            bs += (cc & 0x1f) << 3
                            n += 1
                        pos += blk
                    if n:
                        r, g, b = rs / n, gs / n, bs / n
                        hue = 'GREEN' if g > r + 10 and g > b + 10 else \
                              'RED' if r > g + 10 and r > b + 10 else \
                              'BLUE' if b > r + 10 and b > g + 10 else 'neutral'
                        print(f"  MEAN RGB=({r:.0f},{g:.0f},{b:.0f}) -> {hue}")
            break
