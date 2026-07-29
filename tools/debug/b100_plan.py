#!/usr/bin/env python3
"""Derive CONCRETE on-mesh placement candidates for the Sanctuary population plan
and PROVE the resulting worst-case simultaneous-entity load per screen.

Bands run along the player's actual walk: arrival portal (NE, x~4411) -> west
threshold into drxBC_Finale (x~4186).
"""
import sys, math, json, random
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM
from rec02_format import parse_rec02
CS = 0.2; TILE = 64; CELL = CS*CS; SCREEN = 60.0
random.seed(0)

arc = CM.Arc.from_file(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
mp = arc.world_map(); secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
arz = CM.Arz.from_arz(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}
names = {CM.norm_rec(x): x for x in arz.record_names()}
def fld(r, f):
    n = CM.norm_rec(r)
    return arz.field(names[n], f) if n in names else None
def smax(dbr):
    p = fld(dbr, 'pool1')
    if isinstance(p, list): p = p[0]
    if not p: return 0
    v = fld(p, 'spawnMax')
    return int(v[0] if isinstance(v, list) else v or 0)

IDX = {lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl',''): i
       for i, lv in enumerate(levels) if 'xbloodcave' in lv['fname'].lower()}

# walkable set of drxBC3 ONLY (the walkway proper; the ocean ring is a Will call)
lv = levels[IDX['drxBC3']]
blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
b0b = [d for t, d in CM.parse_blob_sections(blob) if t == 0x0b][0]
doc = parse_rec02(b0b, decompress=True)
c = tuple(doc['center']); dm = tuple(doc['dims'])
org = (c[0]-dm[0], c[1]-dm[1], c[2]-dm[2])
walk = set()
for r in doc['sets'][0]['records']:
    h = r['hdr']; tx, ty = h['tx'], h['ty']
    hs, ar = r['heights'], r['areas']
    for lz in range(TILE):
        base = lz*TILE; gz = ty*TILE+lz
        for lx in range(TILE):
            li = base+lx
            if hs[li] != 0xff and ar[li] != 0:
                walk.add((org[0]+(tx*TILE+lx+0.5)*CS, org[2]+(gz+0.5)*CS))
# restrict to the level's own declared footprint X[4186,4426] Z[2869,3109]
FX0, FX1, FZ0, FZ1 = 4186.0, 4426.0, 2869.0, 3109.0
walk = {(x, z) for (x, z) in walk if FX0 <= x <= FX1 and FZ0 <= z <= FZ1}
print('drxBC3 walkable INSIDE its own footprint: %d cells = %.0f sq u' % (len(walk), len(walk)*CELL))

cx, cy, cz = lv['corner']
existing = []
for it in CM.parse_0x05(blob)[1]:
    d = it['dbr'].decode('latin-1')
    if cls.get(CM.norm_rec(d)) == 'Proxy' and 'shrine' not in d.lower():
        existing.append((cx+it['pos'][0], cz+it['pos'][2], d, smax(d)))

# ---- the band plan (west-bound: 4426 = arrival, 4186 = threshold to the Finale)
P = 'records\\drxmap\\proxy\\'
BANDS = [
    ('1 OUTER COURT  (arrival, breath after the portal)', 4380, 4426,
     [(P+'bw_acolyte_lone.dbr', 2)]),
    ('2 THE CONGREGATION (the rite in full voice)', 4310, 4380,
     [(P+'zparty_witchfest_2099.dbr', 2), (P+'bw_acolyte_clutch.dbr', 2)]),
    ('3 THE CLERGY (priests and their hounds)', 4245, 4310,
     [(P+'bw_priest_houndmaster.dbr', 2), (P+'bw_priest_lone.dbr', 1),
      (P+'hound_01_pack.dbr', 1)]),
    ('4 THE THRESHOLD (flesh-crafted gate-wardens)', 4186, 4245,
     [(P+'abom_dancer_spear_mix.dbr', 2), (P+'abom_ravager_lone.dbr', 1),
      (P+'q_shaman_lone.dbr', 1)]),
]
MINSEP = 34.0        # no two PARTY proxies closer than this in both axes
placed = []
wl = sorted(walk)
for label, x0, x1, roster in BANDS:
    cand = [p for p in wl if x0 <= p[0] < x1]
    print('\n%s   band x[%d,%d]  %d walkable cells = %.0f sq u'
          % (label, x0, x1, len(cand), len(cand)*CELL))
    for dbr, n in roster:
        sm = smax(dbr)
        got = 0; tries = 0
        while got < n and tries < 400000:
            tries += 1
            px, pz = cand[random.randrange(len(cand))]
            big = sm >= 6
            ok = True
            for (qx, qz, qd, qs) in existing + [(a, b, cc, dd) for a, b, cc, dd in placed]:
                need = MINSEP if (big and qs >= 6) else 16.0
                if abs(px-qx) < need and abs(pz-qz) < need:
                    ok = False; break
            if ok:
                placed.append((px, pz, dbr, sm)); got += 1
        print('   + %-2d x %-34s spawnMax=%-3d %s'
              % (n, dbr.split('\\')[-1], sm, 'PLACED' if got == n else 'ONLY %d' % got))

allp = existing + placed
print('\n== resulting roster: %d existing + %d new = %d monster proxies ==' % (len(existing), len(placed), len(allp)))
tot = sum(p[3] for p in allp)
area = len(walk)*CELL
print('   total spawnMax across the walkway = %d' % tot)
print('   density = %.0f sq u per proxy  (was %.0f)' % (area/len(allp), area/len(existing)))

def worst(pts):
    w = 0; at = None
    for (ax, az, _d, _s) in pts:
        s = sum(qs for (qx, qz, _qd, qs) in pts
                if abs(qx-ax) <= SCREEN/2 and abs(qz-az) <= SCREEN/2)
        if s > w: w, at = s, (ax, az)
    return w, at
w0, _ = worst(existing); w1, at1 = worst(allp)
print('\n== DENSITY SAFETY (60x60 world-unit screen box, spawnMax summed) ==')
print('   worst-case simultaneous entities BEFORE : %d' % w0)
print('   worst-case simultaneous entities AFTER  : %d   at (%.0f,%.0f)' % (w1, at1[0], at1[1]))
print('   b76 chumbi-freeze precedent             : "well over 100" (unbounded, no-TTL refill)')
print('   base-game cave/crypt/tomb comparators   : median 14, p90 70, MAX 162 (Crypt01)')
json.dump([{'x': p[0], 'z': p[1], 'dbr': p[2], 'spawnMax': p[3]} for p in placed],
          open(Path(__file__).parent/'plan_placements.json', 'w'), indent=1)
