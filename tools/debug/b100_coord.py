#!/usr/bin/env python3
"""Pin the coordinate space: 0x05 instance pos vs 0x0b navmesh world extent."""
import sys, json, struct
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools')); sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import contracts_map as CM
from rec02_format import parse_rec02

ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
arc = CM.Arc.from_file(str(ARC)); mp = arc.world_map()
secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))

for IDX in (2253, 2248):
    lv = levels[IDX]
    blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    print('\n===', lv['fname'], 'idx', IDX)
    print('grid corner ints[6:9] =', lv['corner'])
    print('tile dims  ints[0:6] =', struct.unpack_from('<6i', lv['ints_raw'], 0))
    b = None
    for t, d in CM.parse_blob_sections(blob):
        if t == 0x0b:
            b = d
    doc = parse_rec02(b, decompress=False)
    c = tuple(doc['center']); dm = tuple(doc['dims'])
    print('0x0b center=%s dims=%s' % (c, dm))
    print('0x0b world extent X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]' %
          (c[0]-dm[0], c[0]+dm[0], c[1]-dm[1], c[1]+dm[1], c[2]-dm[2], c[2]+dm[2]))
    _s, insts = CM.parse_0x05(blob)
    xs = [i['pos'][0] for i in insts]; ys = [i['pos'][1] for i in insts]; zs = [i['pos'][2] for i in insts]
    if xs:
        print('0x05 pos extent  X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]  (n=%d)' %
              (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), len(insts)))
    for i in insts[:4]:
        print('   sample inst pos=%s dbr=%s' % (
            tuple(round(v,1) for v in i['pos']), i['dbr'].decode('latin-1')))
