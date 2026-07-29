#!/usr/bin/env python3
"""Sanctuary recon step 7: minimap TGA presence (fixed parse) + base-game density
comparator + worst-case simultaneous-entity-per-screen math.

BITMAPS(0x19) layout (measured): [u32 a][u32 count] then count x (u32 off, u32 len)
into DATA2(0x1a). 8 + 2282*8 == 18264 == the section size (exact tiling proof).
"""
import sys, json, struct, math
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM
from rec02_format import parse_rec02

CS = 0.2; TILE = 64; CELL_AREA = CS*CS
SCREEN = 60.0   # world units; one screen-ish box edge (conservative for TQ's camera)
SCRATCH = Path(__file__).parent
ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
ARZ = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
BASE_ARZ = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')

arc = CM.Arc.from_file(str(ARC)); mp = arc.world_map()
secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
bm = CM.sec_bytes(mp, secs, 0x19); d2o, d2l = secs[0x1a]
a, ncount = struct.unpack_from('<II', bm, 0)
print('BITMAPS: a=%d count=%d levels=%d  8+count*8=%d == section %d -> %s'
      % (a, ncount, len(levels), 8+ncount*8, len(bm), 8+ncount*8 == len(bm)))

def bmp(i):
    return struct.unpack_from('<II', bm, 8 + i*8)

nz = sum(1 for i in range(len(levels)) if bmp(i)[1])
print('levels WITH a minimap TGA: %d / %d' % (nz, len(levels)))

SANC = ['drxBC3','ocean_extension01','ocean_extension02','ocean_extension03',
        'ocean_extension04','ocean_extension05','ocean_extensionx01','ocean_extensionx02',
        'ocean_extensionx03','ocean_extensionx04','ocean_extensionx05','ocean_extensionx06',
        'ocean_extensionx07','ocean_extensionx08','drxBC_Finale','drxFirstRoom','drxBC2',
        'bossfight','drxBC_Connector2','BC_initialpathway','xPassageTransitionStart']
print('\n== A. minimap TGA presence (Sanctuary complex + blood-cave refs) ==')
print('%-30s %12s %10s  %s' % ('level','off','len','TGA'))
for i, lv in enumerate(levels):
    nm = lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl','')
    if nm not in SANC: continue
    o, l = bmp(i)
    if l:
        h = mp[d2o+o:d2o+o+18]; w, hh = struct.unpack_from('<HH', h, 12)
        t = '%dx%d type=%d exact=%s' % (w, hh, h[2], 18+w*hh*3 == l)
    else:
        t = '*** NO MINIMAP (0,0) ***'
    print('%-30s %12d %10d  %s' % (nm, o, l, t))

# ---------- density comparator ----------
print('\nloading arz for class map...')
arz = CM.Arz.from_arz(str(ARZ))
cls = {CM.norm_rec(n): t for n, t in arz.record_class().items()}
names = {CM.norm_rec(x): x for x in arz.record_names()}
barz = CM.Arz.from_arz(str(BASE_ARZ)) if BASE_ARZ.exists() else None
bnames = {}
if barz:
    bnames = {CM.norm_rec(x): x for x in barz.record_names()}
    for n, t in barz.record_class().items(): cls.setdefault(CM.norm_rec(n), t)

def fld(rec, f):
    n = CM.norm_rec(rec)
    if n in names:
        v = arz.field(names[n], f)
        if v is not None: return v
    if n in bnames: return barz.field(bnames[n], f)
    return None

_spawn_cache = {}
def proxy_max(dbr):
    """Max monsters this proxy can put on the ground (pool1 spawnMax)."""
    if dbr in _spawn_cache: return _spawn_cache[dbr]
    tot = 0
    for pk in ('pool1','pool2','pool3','pool4'):
        pool = fld(dbr, pk)
        if isinstance(pool, list): pool = pool[0] if pool else None
        if not pool or not isinstance(pool, str): continue
        sm = fld(pool, 'spawnMax')
        if isinstance(sm, list): sm = sm[0] if sm else 0
        tot += int(sm or 0)
    _spawn_cache[dbr] = tot
    return tot

def mesh_cells(b0b):
    doc = parse_rec02(b0b, decompress=True)
    c = tuple(doc['center']); dm = tuple(doc['dims'])
    origin = (c[0]-dm[0], c[1]-dm[1], c[2]-dm[2])
    cells = set()
    for r in doc['sets'][0]['records']:
        h = r['hdr']; tx, ty = h['tx'], h['ty']
        hs, ar = r['heights'], r['areas']
        for lz in range(TILE):
            base = lz*TILE; gz = ty*TILE+lz
            for lx in range(TILE):
                li = base+lx
                if hs[li] != 0xff and ar[li] != 0:
                    cells.add((tx*TILE+lx, gz))
    return cells, origin

def analyse(i):
    lv = levels[i]
    blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
    b = None
    for t, d in CM.parse_blob_sections(blob):
        if t == 0x0b: b = d
    if b is None: return None
    cells, origin = mesh_cells(b)
    if not cells: return None
    _s, insts = CM.parse_0x05(blob)
    cx, cy, cz = lv['corner']
    prox = [it for it in insts
            if cls.get(CM.norm_rec(it['dbr'].decode('latin-1'))) == 'Proxy'
            and 'shrine' not in it['dbr'].decode('latin-1').lower()]
    pts = [(cx+p['pos'][0], cz+p['pos'][2], p['dbr'].decode('latin-1')) for p in prox]
    area = len(cells)*CELL_AREA
    # worst-case simultaneous entities in ONE screen box
    worst = 0; worst_at = None
    for (ax, az, _d) in pts:
        s = 0
        for (bx, bz, bd) in pts:
            if abs(bx-ax) <= SCREEN/2 and abs(bz-az) <= SCREEN/2:
                s += proxy_max(bd)
        if s > worst: worst, worst_at = s, (ax, az)
    return dict(name=lv['fname'].split('/')[-1].split('\\')[-1], area=area,
                n=len(pts), worst=worst, worst_at=worst_at,
                per=area/len(pts) if pts else None)

print('\n== B. Sanctuary complex + blood-cave, measured ==')
targets = [i for i, lv in enumerate(levels) if 'xbloodcave' in lv['fname'].lower()]
bcres = {}
for i in targets:
    r = analyse(i)
    if r: bcres[r['name'].replace('.lvl','')] = r
for k in ['drxBC3','ocean_extension01','ocean_extension02','ocean_extension03','ocean_extension04',
          'drxBC_Finale','drxFirstRoom','drxBC2','drxBC_Connector2','yet_another_fucking_connector']:
    r = bcres.get(k)
    if not r: continue
    print('  %-34s area=%8.0f proxies=%3d  squ/proxy=%9s  worst_screen_entities=%d'
          % (k, r['area'], r['n'], ('%.0f'%r['per']) if r['per'] else 'inf', r['worst']))

# ---------- base-game comparators ----------
print('\n== C. BASE-GAME comparators (measured the same way, same canonical map) ==')
CAND = ['startingcave01','spartaoptcave02','athenssewer','cave', 'crypt', 'random09a']
rows = []
for i, lv in enumerate(levels):
    f = lv['fname'].lower()
    if 'xbloodcave' in f or 'secret_place' in f or 'uberdungeon' in f: continue
    if not any(c in f for c in ('cave','crypt','tomb','sewer','catacomb','labyrinth')): continue
    r = analyse(i)
    if r and r['n'] >= 5 and r['area'] > 3000:
        rows.append(r)
rows.sort(key=lambda r: r['per'])
print('  %d base-game cave/crypt/tomb levels with >=5 proxies and >3000 squ walkable' % len(rows))
import statistics as st
pers = [r['per'] for r in rows]
worsts = [r['worst'] for r in rows]
if pers:
    print('  squ per proxy: min=%.0f p25=%.0f MEDIAN=%.0f p75=%.0f max=%.0f'
          % (min(pers), st.quantiles(pers, n=4)[0], st.median(pers),
             st.quantiles(pers, n=4)[2], max(pers)))
    print('  worst-screen entities: median=%.0f p90=%.0f MAX=%d'
          % (st.median(worsts), st.quantiles(worsts, n=10)[8], max(worsts)))
    print('\n  tightest 8 (densest):')
    for r in rows[:8]:
        print('    %-44s area=%7.0f prox=%3d squ/proxy=%6.0f worst_screen=%d'
              % (r['name'], r['area'], r['n'], r['per'], r['worst']))
    print('  loosest 5:')
    for r in rows[-5:]:
        print('    %-44s area=%7.0f prox=%3d squ/proxy=%6.0f worst_screen=%d'
              % (r['name'], r['area'], r['n'], r['per'], r['worst']))
    mx = max(rows, key=lambda r: r['worst'])
    print('\n  MAX worst-screen base-game level: %s = %d entities (area %.0f, %d proxies)'
          % (mx['name'], mx['worst'], mx['area'], mx['n']))

json.dump({'bc': {k: {kk: vv for kk, vv in v.items() if kk != 'worst_at'} for k, v in bcres.items()},
           'base': [{kk: vv for kk, vv in r.items() if kk != 'worst_at'} for r in rows]},
          open(SCRATCH/'density.json','w'), indent=1)

print('\n== D. per-proxy spawnMax used above (drxBC3 roster) ==')
for d in sorted(set(p[2] for p in [(0,0,x) for x in bcres['drxBC3'].get('dbrs',[])])) or []:
    pass
for d in ['records\\drxmap\\proxy\\zparty_witchfest_2099.dbr',
          'records\\drxmap\\proxy\\bw_priest_houndmaster.dbr',
          'records\\drxmap\\proxy\\bw_reaver_lone.dbr',
          'records\\drxmap\\proxy\\bw_seductress_lone.dbr',
          'records\\drxmap\\proxy\\hound_01_pack.dbr']:
    pool = fld(d, 'pool1')
    if isinstance(pool, list): pool = pool[0]
    print('  %-46s spawnMin=%s spawnMax=%s champMin=%s champMax=%s' % (
        d.split('\\')[-1], fld(pool,'spawnMin'), fld(pool,'spawnMax'),
        fld(pool,'championMin'), fld(pool,'championMax')))
