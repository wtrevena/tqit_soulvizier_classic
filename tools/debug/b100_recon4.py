#!/usr/bin/env python3
"""Sanctuary recon step 4 (CORRECTED): occupancy with the level-local -> world offset.

0x05 instance positions are LEVEL-LOCAL (0..240); the 0x0b navmesh is WORLD-space.
world = grid_corner + local. Proven by the ON-MESH GATE below: if the offset is
right, placed monster proxies land on walkable navmesh cells.
"""
import sys, os, json, math, struct
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools')); sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import contracts_map as CM
from rec02_format import parse_rec02

CS = 0.2; TILE = 64; CELL_AREA = CS * CS
SCRATCH = Path(__file__).parent
ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
ARZ = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
BASE_ARZ = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')


def mesh_cells(b0b):
    doc = parse_rec02(b0b, decompress=True)
    c = tuple(doc['center']); dm = tuple(doc['dims'])
    origin = (c[0] - dm[0], c[1] - dm[1], c[2] - dm[2])
    cells = set()
    for r in doc['sets'][0]['records']:
        h = r['hdr']; tx, ty = h['tx'], h['ty']
        hs, ar = r['heights'], r['areas']
        for lz in range(TILE):
            base = lz * TILE; gz = ty * TILE + lz
            for lx in range(TILE):
                li = base + lx
                if hs[li] != 0xff and ar[li] != 0:
                    cells.add((tx * TILE + lx, gz))
    return cells, origin


def sec(blob, want):
    for t, d in CM.parse_blob_sections(blob):
        if t == want:
            return d
    return None


print('loading...')
arc = CM.Arc.from_file(str(ARC)); mp = arc.world_map()
secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
arz = CM.Arz.from_arz(str(ARZ))
cls = {CM.norm_rec(n): t for n, t in arz.record_class().items()}
if BASE_ARZ.exists():
    for n, t in CM.Arz.from_arz(str(BASE_ARZ)).record_class().items():
        cls.setdefault(CM.norm_rec(n), t)

RADII = [10, 15, 20, 30]
BC = [(i, lv) for i, lv in enumerate(levels) if 'xbloodcave' in lv['fname'].lower()]

print('\nON-MESH GATE: fraction of monster proxies landing on a walkable cell')
print('(offset hypothesis: world = grid_corner + local)\n')
print('%-38s %8s %7s %6s %7s %6s   %s' % ('level','walk_squ','cells','prox','onmesh','inst',
      '  '.join('R=%-3d'%r for r in RADII)))

res = {}
for i, lv in BC:
    blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    b = sec(blob, 0x0b)
    if b is None: continue
    cells, origin = mesh_cells(b)
    if not cells: continue
    _s, insts = CM.parse_0x05(blob)
    cx, cy, cz = lv['corner']
    prox = [it for it in insts if cls.get(CM.norm_rec(it['dbr'].decode('latin-1'))) == 'Proxy']
    mon = [p for p in prox if 'shrine' not in p['dbr'].decode('latin-1').lower()]
    pts = [(cx + p['pos'][0], cz + p['pos'][2]) for p in mon]

    # ON-MESH GATE
    on = 0
    for (px, pz) in pts:
        gx = int((px - origin[0]) / CS); gz = int((pz - origin[2]) / CS)
        if any((gx+dx, gz+dz) in cells for dx in range(-3,4) for dz in range(-3,4)):
            on += 1

    area = len(cells) * CELL_AREA
    # bucket cells into a coarse grid for fast nearest-proxy queries
    frac = []
    for R in RADII:
        R2 = R*R
        if not pts:
            frac.append(1.0); continue
        far = 0
        for (gx, gz) in cells:
            wx = origin[0] + (gx+0.5)*CS; wz = origin[2] + (gz+0.5)*CS
            ok = False
            for (px, pz) in pts:
                if (wx-px)**2 + (wz-pz)**2 <= R2: ok = True; break
            if not ok: far += 1
        frac.append(far/len(cells))
    nm = lv['fname'].split('/')[-1].split('\\')[-1]
    print('%-38s %8.0f %7d %6d %6s%% %6d   %s' % (
        nm, area, len(cells), len(mon),
        ('%.0f'%(100*on/len(mon))) if mon else '  -', len(insts),
        '  '.join('%4.0f%%'%(f*100) for f in frac)))
    res[nm] = dict(idx=i, area=area, cells=len(cells), n_mon=len(mon), onmesh=on,
                   n_inst=len(insts), origin=list(origin), corner=list(lv['corner']),
                   frac_far=frac, pts=pts,
                   dbrs=[p['dbr'].decode('latin-1') for p in mon])

json.dump(res, open(SCRATCH/'bc_occ4.json','w'), indent=1)
ta = sum(r['area'] for r in res.values()); tm = sum(r['n_mon'] for r in res.values())
print('\nCLUSTER: walkable %.0f sq u, %d monster proxies, %.0f sq u per proxy' % (ta, tm, ta/max(tm,1)))
