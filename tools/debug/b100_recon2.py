#!/usr/bin/env python3
"""Sanctuary recon step 2: what is PLACED in drxBC3 (the Sanctuary), by class."""
import sys, os, struct, json, pickle
from pathlib import Path
from collections import Counter, defaultdict

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import contracts_map as CM

SCRATCH = Path(__file__).parent
ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')
ARZ = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
BASE_ARZ = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')

arc = CM.Arc.from_file(str(ARC))
mp = arc.world_map()
secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))

# cache blobs of the whole xBloodCave cluster for later steps
bc = [(i, lv) for i, lv in enumerate(levels) if 'xbloodcave' in lv['fname'].lower()]
print('xBloodCave levels: %d' % len(bc))

TARGET = 2253
lv = levels[TARGET]
blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
print('\n== drxBC3 (Sanctuary of the Bloodborn) ==')
print('fname   ', lv['fname'])
print('corner  ', lv['corner'])
print('ints[0:6] tile dims', struct.unpack_from('<6i', lv['ints_raw'], 0))
print('guid    ', lv['guid'].hex())
print('blob len', len(blob), 'lvl version', blob[3])
print('sections', [(hex(t), len(d)) for t, d in CM.parse_blob_sections(blob)])

strings, insts = CM.parse_0x05(blob)
print('\n0x05 strings=%d instances=%d' % (len(strings), len(insts)))

print('\nloading arz...')
arz = CM.Arz.from_arz(str(ARZ))
cls = {CM.norm_rec(n): t for n, t in arz.record_class().items()}
names = set(cls)
barz = None
if BASE_ARZ.exists():
    barz = CM.Arz.from_arz(str(BASE_ARZ))
    for n, t in barz.record_class().items():
        cls.setdefault(CM.norm_rec(n), t)
        names.add(CM.norm_rec(n))
print('arz records %d (+base) total classes %d' % (len(arz.record_names()), len(cls)))

byclass = Counter()
bydbr = Counter()
for it in insts:
    d = it['dbr'].decode('latin-1')
    n = CM.norm_rec(d)
    c = cls.get(n, '<UNRESOLVED>')
    byclass[c] += 1
    bydbr[(c, d)] += 1

print('\n== 0x05 instances by CLASS ==')
for c, n in byclass.most_common():
    print('  %-40s %5d' % (c, n))

print('\n== every distinct dbr placed (class, count, path) ==')
for (c, d), n in sorted(bydbr.items(), key=lambda kv: (-kv[1], kv[0])):
    print('  %-34s %4d  %s' % (c[:34], n, d))

# dump instance positions for the next step
out = [{'dbr': it['dbr'].decode('latin-1'),
        'cls': cls.get(CM.norm_rec(it['dbr'].decode('latin-1')), '<UNRESOLVED>'),
        'pos': list(it['pos']), 'flags': it['flags'],
        'uid': it['uid'].hex() if it['uid'] else None} for it in insts]
json.dump(out, open(SCRATCH / 'sanc_0x05.json', 'w'), indent=0)
print('\nwrote sanc_0x05.json (%d)' % len(out))

# also dump the whole blood-cave cluster's 0x05 counts, for the comparison table
print('\n== xBloodCave cluster 0x05 census ==')
rows = []
for i, l in bc:
    b = mp[l['data_offset']:l['data_offset'] + l['data_length']]
    st, ins = CM.parse_0x05(b)
    hasnav = any(t == 0x0b for t, _ in CM.parse_blob_sections(b))
    rows.append((i, l['fname'].split('/')[-1], len(ins), l['corner'], hasnav, len(b)))
for r in sorted(rows, key=lambda r: r[0]):
    print('  idx=%-5d %-38s inst=%-5d corner=%-22s nav=%s blob=%d' %
          (r[0], r[1], r[2], str(r[3]), r[4], r[5]))
json.dump([[r[0], r[1], r[2], list(r[3]), r[4], r[5]] for r in rows],
          open(SCRATCH / 'bc_census.json', 'w'))
