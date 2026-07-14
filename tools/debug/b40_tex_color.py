"""B40 READ-ONLY: sample the dominant color of TQ .tex assets (wrapped DDS) to
confirm the marauder green source. Prints mean R,G,B of the decoded texture."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive

GAME = r'C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Resources'


def get_tex(arcpath, inner):
    p = Path(arcpath)
    if not p.exists():
        return None
    arc = ArcArchive.from_file(p)
    want = inner.lower().replace('\\', '/')
    for e in arc.entries:
        if e.name and e.name.lower().replace('\\', '/') == want:
            return arc.decompress(e)
    return None


def find_dds(data):
    i = data.find(b'DDS ')
    return data[i:] if i >= 0 else None


def decode_dds_meancolor(dds):
    if dds[:4] != b'DDS ':
        return None
    h, w = struct.unpack_from('<II', dds, 12)  # height, width
    fourcc = dds[84:88]
    off = 128
    # sample block-average endpoint colors for DXT1/3/5 (good enough for a hue check)
    if fourcc in (b'DXT1', b'DXT3', b'DXT5'):
        block = 8 if fourcc == b'DXT1' else 16
        col_off = 0 if fourcc == b'DXT1' else 8
        rs = gs = bs = n = 0
        pos = off
        end = len(dds)
        while pos + block <= end and n < 20000:
            c0 = struct.unpack_from('<H', dds, pos + col_off)[0]
            c1 = struct.unpack_from('<H', dds, pos + col_off + 2)[0]
            for c in (c0, c1):
                r = ((c >> 11) & 0x1f) << 3
                g = ((c >> 5) & 0x3f) << 2
                b = (c & 0x1f) << 3
                rs += r; gs += g; bs += b; n += 1
            pos += block
        if n:
            return (rs / n, gs / n, bs / n, f'{fourcc.decode()} {w}x{h}')
    elif fourcc == b'\x00\x00\x00\x00':
        # uncompressed - assume 32bpp BGRA
        rs = gs = bs = n = 0
        pos = off
        while pos + 4 <= len(dds) and n < 40000:
            b, g, r, a = dds[pos], dds[pos+1], dds[pos+2], dds[pos+3]
            rs += r; gs += g; bs += b; n += 1
            pos += 4
        if n:
            return (rs / n, gs / n, bs / n, f'RAW32 {w}x{h}')
    return (None, None, None, f'{fourcc} {w}x{h} (unhandled)')


TARGETS = [
    ('Creatures', 'Monster/ShadowStalker/ShadowStalker01Glow.tex', 'marauder mesh glow'),
    ('Creatures', 'Monster/ShadowStalker/ShadowStalker01.tex', 'marauder mesh base skin'),
    ('Creatures', 'Monster/Skeleton/NewSkeleton_Charcoal.tex', 'boss charcoal skin'),
    ('Creatures', 'Monster/Skeleton/newskeleton_crimson.tex', 'devourer crimson (control=red)'),
    ('Creatures', 'Monster/Skeleton/newskeleton_grean.tex', 'athens green (control=green)'),
]


def main():
    for arcname, inner, label in TARGETS:
        data = get_tex(GAME + f'/{arcname}.arc', inner)
        if not data:
            print(f"  MISSING {inner}")
            continue
        dds = find_dds(data)
        if not dds:
            print(f"  {label:32s} {inner}: no DDS payload (first bytes {data[:8]!r})")
            continue
        r, g, b, meta = decode_dds_meancolor(dds)
        if r is None:
            print(f"  {label:32s} {meta}")
            continue
        hue = 'GREEN' if (g > r + 12 and g > b + 12) else \
              'RED' if (r > g + 12 and r > b + 12) else \
              'BLUE' if (b > r + 12 and b > g + 12) else 'neutral/grey'
        print(f"  {label:32s} mean RGB=({r:5.1f},{g:5.1f},{b:5.1f})  -> {hue:12s} [{meta}]")


if __name__ == '__main__':
    main()
