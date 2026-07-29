#!/usr/bin/env python3
"""Is the zero-proxy ocean ring REACHABLE from drxBC3?

Engine model (docs/CROSS_LEVEL_STITCH_RE.md + build13 lattice fix): room-to-room
walking is navmesh TILE STITCHING - both levels' walkable cells must meet across
the shared grid line. Measure, per seam, how many world-space columns carry
walkable cells on BOTH sides within one cell of the seam line.
"""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM
from rec02_format import parse_rec02
CS = 0.2; TILE = 64

arc = CM.Arc.from_file(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
mp = arc.world_map(); secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))

def cellsw(i):
    lv = levels[i]
    blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
    b = None
    for t, d in CM.parse_blob_sections(blob):
        if t == 0x0b: b = d
    if b is None: return None, None
    doc = parse_rec02(b, decompress=True)
    c = tuple(doc['center']); dm = tuple(doc['dims'])
    org = (c[0]-dm[0], c[1]-dm[1], c[2]-dm[2])
    out = {}
    for r in doc['sets'][0]['records']:
        h = r['hdr']; tx, ty, hmin = h['tx'], h['ty'], h['hmin']
        hs, ar = r['heights'], r['areas']
        for lz in range(TILE):
            base = lz*TILE; gz = ty*TILE+lz
            for lx in range(TILE):
                li = base+lx
                if hs[li] != 0xff and ar[li] != 0:
                    wx = org[0]+(tx*TILE+lx+0.5)*CS
                    wz = org[2]+(gz+0.5)*CS
                    wy = org[1]+(hmin+hs[li])*0.2
                    out[(round(wx,1), round(wz,1))] = wy
    return out, org

byname = {}
for i, lv in enumerate(levels):
    if 'xbloodcave' in lv['fname'].lower():
        byname[lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl','')] = i

print('decoding navmeshes...')
W = {}
for n in ['drxBC3','ocean_extension01','ocean_extension02','ocean_extension03',
          'ocean_extension04','drxBC_Finale','ocean_extensionx02','ocean_extensionx08']:
    W[n], _ = cellsw(byname[n])
    print('  %-22s %d walkable cells' % (n, len(W[n]) if W[n] else 0))

# drxBC3 footprint X[4186,4426] Z[2869,3109]
SEAMS = [('drxBC3','ocean_extension02','x', 4426.0),   # east
         ('drxBC3','ocean_extension01','z', 2869.0),   # south
         ('drxBC3','ocean_extension03','z', 3109.0),   # north
         ('drxBC3','ocean_extension04','corner', None),
         ('drxBC3','drxBC_Finale','x', 4186.0)]        # west
print('\n%-22s %-22s %-6s %8s  %s' % ('A','B','axis','line','shared columns with walkable cells BOTH sides (<=0.6u of the line)'))
for a, b, axis, line in SEAMS:
    A, B = W[a], W[b]
    if axis == 'corner':
        # diagonal-only contact: just report closest approach
        best = None
        for (ax, az) in list(A)[::37]:
            for (bx, bz) in list(B)[::37]:
                d = (ax-bx)**2 + (az-bz)**2
                if best is None or d < best[0]: best = (d, (ax, az), (bx, bz))
        print('%-22s %-22s %-6s %8s  closest approach %.1f u  A%s B%s' %
              (a, b, axis, '-', best[0]**0.5, best[1], best[2]))
        continue
    tol = 0.6
    if axis == 'x':
        Acol = set(round(z,1) for (x,z) in A if abs(x-line) <= tol)
        Bcol = set(round(z,1) for (x,z) in B if abs(x-line) <= tol)
    else:
        Acol = set(round(x,1) for (x,z) in A if abs(z-line) <= tol)
        Bcol = set(round(x,1) for (x,z) in B if abs(z-line) <= tol)
    sh = Acol & Bcol
    # contiguous run length
    run = 0; best = 0; prev = None
    for v in sorted(sh):
        if prev is not None and abs(v-prev-0.2) < 0.01: run += 1
        else: run = 1
        best = max(best, run); prev = v
    print('%-22s %-22s %-6s %8.1f  A=%d B=%d SHARED=%d  widest contiguous run=%.1f u  -> %s' %
          (a, b, axis, line, len(Acol), len(Bcol), len(sh), best*0.2,
           'WALKABLE SEAM' if len(sh) else 'NO SHARED CELLS'))
