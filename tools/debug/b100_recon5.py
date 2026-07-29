#!/usr/bin/env python3
"""Sanctuary recon step 5: region binding + zone dbr + navmesh neighbours for the
whole xBloodCave cluster.

If a level's 0x17 REGION list is EMPTY the banner RETAINS the previous region
(b46 round-3 mechanism). So an empty-region tile walked into FROM drxBC3 still
reads 'Sanctuary of the Bloodborn' to the player - it IS the Sanctuary as far as
the player can tell.
"""
import sys, json, struct
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM, sd_format as SD
from build_section_surgery import parse_0x17_header
from rec02_format import parse_rec02

ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
arc = CM.Arc.from_file(str(ARC)); mp = arc.world_map()
secs = CM.parse_top_sections(mp)
lsec = CM.sec_bytes(mp, secs, 0x01)
levels = CM.parse_level_index(lsec)
sd = SD.SDSection.parse(CM.sec_bytes(mp, secs, 0x18))
reg = {bytes(r.guid): r for r in sd.region_records}
env = {bytes(e.guid): e for e in sd.env_records}
guid2lvl = {lv['guid']: (i, lv['fname']) for i, lv in enumerate(levels)}

# re-parse the LEVELS index keeping the zone dbr string
def level_dbrs(buf):
    n = struct.unpack_from('<I', buf, 0)[0]; out=[]; idx=4
    for _ in range(n):
        idx += 52
        dl = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        dbr = buf[idx:idx+dl].decode('ascii','replace'); idx += dl
        fl = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        idx += fl; idx += 8
        out.append(dbr)
    return out
dbrs = level_dbrs(lsec)

BC = [(i,lv) for i,lv in enumerate(levels) if 'xbloodcave' in lv['fname'].lower()]
print('%-38s %-28s %-22s %s' % ('level','0x17 REGION -> SD name','0x17 ENV','zone dbr (minimap page)'))
print('-'*130)
rows={}
for i,lv in BC:
    blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
    rn, en = [], []
    for t,d in CM.parse_blob_sections(blob):
        if t==0x17:
            m,ver,e,r,a,ra = parse_0x17_header(d)
            rn = [reg[bytes(g)].name if bytes(g) in reg else '?'+bytes(g).hex()[:8] for _,g in r]
            en = [env[bytes(g)].name if bytes(g) in env else '?'+bytes(g).hex()[:8] for _,g in e]
            break
    nm = lv['fname'].split('/')[-1].split('\\')[-1]
    print('%-38s %-28s %-22s %s' % (nm, ','.join(rn) if rn else '*** EMPTY ***',
                                    ','.join(en) if en else '(none)', dbrs[i] or '*** EMPTY ***'))
    rows[nm]=dict(idx=i, regions=rn, envs=en, zone=dbrs[i])

# navmesh neighbour GUIDs for the Sanctuary + its ocean ring
print('\n== navmesh 0x0b GUID lists (own + declared neighbours) ==')
for i,lv in BC:
    nm = lv['fname'].split('/')[-1].split('\\')[-1]
    if not (nm.startswith('drxBC3') or nm.startswith('ocean_') or nm.startswith('drxBC_Finale')):
        continue
    blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
    for t,d in CM.parse_blob_sections(blob):
        if t==0x0b:
            doc = parse_rec02(d, decompress=False)
            gs=[g if isinstance(g,str) else g.hex() for g in doc['guids']]
            named=[]
            for g in gs:
                gb=bytes.fromhex(g)
                named.append(guid2lvl.get(gb,('?','?'))[1].split('/')[-1].split('\\')[-1])
            print('  %-30s -> %s' % (nm, ', '.join(named)))
            break
json.dump(rows, open(Path(__file__).parent/'bc_regions.json','w'), indent=1)
