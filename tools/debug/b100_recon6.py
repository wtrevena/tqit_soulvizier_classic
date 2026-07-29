#!/usr/bin/env python3
"""Sanctuary recon step 6: minimap BITMAPS/DATA2, proxy->pool resolution, entry/exit."""
import sys, json, struct
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM

ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
ARZ = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
BASE_ARZ = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')

arc = CM.Arc.from_file(str(ARC)); mp = arc.world_map()
secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))

# --- A. BITMAPS(0x19) index parallel to LEVELS; DATA2(0x1a) holds bare TGAs
bm = CM.sec_bytes(mp, secs, 0x19)
d2off, d2len = secs.get(0x1a, (0, 0))
n = struct.unpack_from('<I', bm, 0)[0] if len(bm) >= 4 else 0
print('BITMAPS entries=%d (levels=%d)  DATA2=%d B' % (n, len(levels), d2len))
ents = []
for i in range(n):
    o, l = struct.unpack_from('<II', bm, 4 + i*8)
    ents.append((o, l))

def tga_dims(off, ln):
    if ln == 0: return None
    hdr = mp[d2off+off:d2off+off+18]
    if len(hdr) < 18: return None
    w, h = struct.unpack_from('<HH', hdr, 12)
    return (w, h, hdr[2])

SANC = ['drxBC3','ocean_extension01','ocean_extension02','ocean_extension03',
        'ocean_extension04','drxBC_Finale','drxFirstRoom','drxBC2',
        'ocean_extensionx02','ocean_extensionx08','ocean_extension05','ocean_extensionx01']
print('\n== A. minimap BITMAPS/DATA2 for the Sanctuary complex ==')
print('%-34s %8s %10s %14s' % ('level','bmp_off','bmp_len','TGA w x h (type)'))
for i, lv in enumerate(levels):
    nm = lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl','')
    if nm not in SANC: continue
    o, l = ents[i] if i < len(ents) else (0,0)
    d = tga_dims(o, l)
    print('%-34s %8d %10d %14s' % (nm, o, l, ('%dx%d (t=%d)'%d) if d else '*** NONE ***'))

# --- B. proxy -> pool resolution for drxBC3
print('\nloading arz...')
arz = CM.Arz.from_arz(str(ARZ))
names = {CM.norm_rec(x): x for x in arz.record_names()}
cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}
barz = CM.Arz.from_arz(str(BASE_ARZ)) if BASE_ARZ.exists() else None
bnames = {CM.norm_rec(x): x for x in barz.record_names()} if barz else {}
if barz:
    for k, v in barz.record_class().items(): cls.setdefault(CM.norm_rec(k), v)

def getf(rec, f):
    n = CM.norm_rec(rec)
    if n in names:
        v = arz.field(names[n], f)
        if v is not None: return v
    if n in bnames:
        return barz.field(bnames[n], f)
    return None

def resolves(rec):
    n = CM.norm_rec(rec)
    return n in names or n in bnames

PROX = ['records\\drxmap\\proxy\\zparty_witchfest_2099.dbr',
        'records\\drxmap\\proxy\\bw_priest_houndmaster.dbr',
        'records\\drxmap\\proxy\\bw_reaver_lone.dbr',
        'records\\drxmap\\proxy\\bw_seductress_lone.dbr',
        'records\\drxmap\\proxy\\hound_01_pack.dbr',
        'records\\drxmap\\bloodcave\\shrines\\proxies\\proxy_shrinepalace.dbr']
print('\n== B. drxBC3 proxy -> pool -> monster resolution ==')
for p in PROX:
    print('\n--- %s  [class=%s resolves=%s]' % (p, cls.get(CM.norm_rec(p)), resolves(p)))
    fl = arz.get_fields(names.get(CM.norm_rec(p), '')) or (barz.get_fields(bnames.get(CM.norm_rec(p),'')) if barz else {}) or {}
    for k in sorted(fl):
        if any(s in k.lower() for s in ('pool','spawn','number','limit','difficulty','chance','equation','template')):
            print('     %-32s = %s' % (k, fl[k]))
    for pk in ('spawnPool1','spawnPool2','spawnPool3','pool1','pool2','pool3'):
        v = fl.get(pk)
        if not v: continue
        for pool in (v if isinstance(v, list) else [v]):
            if not isinstance(pool, str) or not pool.strip(): continue
            print('     POOL %s resolves=%s' % (pool, resolves(pool)))
            pf = arz.get_fields(names.get(CM.norm_rec(pool),'')) or (barz.get_fields(bnames.get(CM.norm_rec(pool),'')) if barz else {}) or {}
            for k in sorted(pf):
                if any(s in k.lower() for s in ('name','weight','min','max','equation','level')):
                    val = pf[k]
                    print('        %-28s = %s' % (k, val))

# --- E. entry / exit
print('\n== E. drxBC3 entry/exit objects ==')
lv = levels[2253]
blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
_s, insts = CM.parse_0x05(blob)
cx, cy, cz = lv['corner']
for it in insts:
    d = it['dbr'].decode('latin-1')
    c = cls.get(CM.norm_rec(d), '?')
    if c in ('GridExitOneWay','GridEntrance','StrategicMovementRespawnShrine','Portal') or 'portal' in d.lower():
        print('  %-32s %-30s local=%s world=(%.1f,%.1f,%.1f) uid=%s' % (
            c, d.split('\\')[-1], tuple(round(v,1) for v in it['pos']),
            cx+it['pos'][0], cy+it['pos'][1], cz+it['pos'][2],
            it['uid'].hex() if it['uid'] else None))
# 0x14 metadata
for t, d in CM.parse_blob_sections(blob):
    if t == 0x14:
        print('  0x14 (%d B) hex=%s' % (len(d), d.hex()))
