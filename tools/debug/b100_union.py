#!/usr/bin/env python3
"""THE headline measurement: the player-reachable Sanctuary, deduplicated.

The 0x0b container is PADDED beyond the level footprint, so per-level walkable
areas overlap at seams. Union the walkable cells in WORLD space (0.2u grid) so
every square unit is counted exactly once, then measure distance-to-nearest-proxy.
"""
import sys, math
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM
from rec02_format import parse_rec02
CS = 0.2; TILE = 64; CELL = CS*CS

arc = CM.Arc.from_file(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
mp = arc.world_map(); secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
arz = CM.Arz.from_arz(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}
byname = {lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl',''): i
          for i, lv in enumerate(levels) if 'xbloodcave' in lv['fname'].lower()}

GROUP = ['drxBC3','ocean_extension01','ocean_extension02','ocean_extension03','ocean_extension04']

union = set(); prox = []
per = {}
for n in GROUP:
    i = byname[n]; lv = levels[i]
    blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
    b = None
    for t, d in CM.parse_blob_sections(blob):
        if t == 0x0b: b = d
    doc = parse_rec02(b, decompress=True)
    c = tuple(doc['center']); dm = tuple(doc['dims'])
    org = (c[0]-dm[0], c[1]-dm[1], c[2]-dm[2])
    # EXACT integer lattice keys. Navmesh origins are whole world units (build13
    # 64u-lattice snap), so origin/CS is an exact multiple of 5 -> integer keys,
    # no float rounding. (A round(wx*5) keying silently collapsed ~4x the cells
    # via banker's rounding on the .5 cell centre; do not reintroduce it.)
    assert abs(org[0]*5 - round(org[0]*5)) < 1e-6, org
    assert abs(org[2]*5 - round(org[2]*5)) < 1e-6, org
    ox = int(round(org[0]*5)); oz = int(round(org[2]*5))
    own = set()
    for r in doc['sets'][0]['records']:
        h = r['hdr']; tx, ty = h['tx'], h['ty']
        hs, ar = r['heights'], r['areas']
        for lz in range(TILE):
            base = lz*TILE; gz = ty*TILE+lz
            for lx in range(TILE):
                li = base+lx
                if hs[li] != 0xff and ar[li] != 0:
                    own.add((ox + tx*TILE + lx, oz + gz))
    per[n] = len(own)
    union |= own
    cx, cy, cz = lv['corner']
    for it in CM.parse_0x05(blob)[1]:
        d = it['dbr'].decode('latin-1')
        if cls.get(CM.norm_rec(d)) == 'Proxy' and 'shrine' not in d.lower():
            prox.append((cx+it['pos'][0], cz+it['pos'][2], d))

print('== player-reachable Sanctuary (drxBC3 + the 4 navmesh-stitched ocean tiles) ==')
for n in GROUP:
    print('  %-22s %9d cells  %9.0f sq u (before dedup)' % (n, per[n], per[n]*CELL))
raw = sum(per.values())
print('  %-22s %9d cells  %9.0f sq u' % ('SUM (raw)', raw, raw*CELL))
print('  %-22s %9d cells  %9.0f sq u   <-- DEDUPLICATED UNION' % ('UNION', len(union), len(union)*CELL))
print('  overlap removed: %d cells = %.0f sq u (%.1f%%)'
      % (raw-len(union), (raw-len(union))*CELL, 100.0*(raw-len(union))/raw))
print('\n  monster proxies in the whole group: %d' % len(prox))
for p in prox:
    print('     (%7.1f,%7.1f)  %s' % (p[0], p[1], p[2].split('\\')[-1]))

print('\n== emptiness: distance from walkable ground to the nearest monster proxy ==')
pts = [(x, z) for x, z, _ in prox]
for R in (10, 15, 20, 25, 30, 40, 50):
    R2 = R*R; far = 0
    for (kx, kz) in union:
        wx = (kx+0.5)/5.0; wz = (kz+0.5)/5.0
        if not any((wx-px)**2 + (wz-pz)**2 <= R2 for px, pz in pts):
            far += 1
    print('   no proxy within %2du : %9d cells = %8.0f sq u = %5.1f%% of the reachable Sanctuary'
          % (R, far, far*CELL, 100.0*far/len(union)))

print('\n   density = %.0f sq u of reachable navmesh per monster proxy'
      % (len(union)*CELL/len(pts)))
