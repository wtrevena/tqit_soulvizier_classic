#!/usr/bin/env python3
"""Pin the DATA2 minimap payload for the Sanctuary complex vs a known-good control."""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM

arc = CM.Arc.from_file(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
mp = arc.world_map(); secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
bm = CM.sec_bytes(mp, secs, 0x19); d2o, d2l = secs[0x1a]

def bmp(i): return struct.unpack_from('<II', bm, 8+i*8)

WANT = ['drxBC3','ocean_extension01','ocean_extension02','ocean_extension03','ocean_extension04',
        'drxBC_Finale','drxFirstRoom','drxBC2','bossfight','xPassageTransitionStart',
        'StartingCave01','crypt_floor1','boss_arena','Crypt01']
print('%-28s %11s %10s  %-26s %s' % ('level','off','len','first 20 bytes','decode'))
for i, lv in enumerate(levels):
    nm = lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl','')
    if nm not in WANT: continue
    o, l = bmp(i)
    if l == 0:
        print('%-28s %11d %10d  %-26s %s' % (nm, o, l, '-', '*** NO BITMAP ENTRY ***'))
        continue
    raw = mp[d2o+o:d2o+o+24]
    # bare 24-bit TGA: 18-byte header, byte[2]==2 (uncompressed truecolour)
    w, h = struct.unpack_from('<HH', raw, 12)
    depth = raw[16]
    ok = (18 + w*h*(depth//8) == l)
    print('%-28s %11d %10d  %-26s %s' % (
        nm, o, l, raw[:20].hex(),
        ('TGA type=%d %dx%d depth=%d EXACT=%s' % (raw[2], w, h, depth, ok)) if ok
        else 'header does not tile (type=%d %dx%d d=%d)' % (raw[2], w, h, depth)))
