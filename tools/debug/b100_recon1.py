#!/usr/bin/env python3
"""Sanctuary recon step 1: which .lvl compose the 'Sanctuary of the Bloodborn'?

Ground truth only: the canonical Levels.arc the build produces.
Mechanism (b46 round 3, docs/reports/b46_minimap_result.md):
  level blob 0x17 -> REGION GUID list -> world SD(0x18) REGION record -> display tag.
"""
import sys, os, hashlib, struct, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

import contracts_map as CM
import sd_format as SD
from build_section_surgery import parse_0x17_header

ARC = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc')

print('== canonical arc ==')
print('path', ARC)
print('size', ARC.stat().st_size)

arc = CM.Arc.from_file(str(ARC))
mp = arc.world_map()
print('world01.map bytes', len(mp), 'md5', hashlib.md5(mp).hexdigest())

secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
print('levels', len(levels))

sd = SD.SDSection.parse(CM.sec_bytes(mp, secs, 0x18))
print('SD version', sd.version, 'env', len(sd.env_records), 'region', len(sd.region_records))

# region guid -> record
reg_by_guid = {}
for r in sd.region_records:
    reg_by_guid[bytes(r.guid)] = r

# find the Sanctuary region record
sanc = [r for r in sd.region_records if 'walkway' in r.name.lower() or 'walkway' in (r.tag or '').lower()]
print('\n== SD region records matching walkway ==')
for r in sanc:
    print(' name=%r tag=%r guid=%s' % (r.name, r.tag, bytes(r.guid).hex()))

# also dump all BCX regions
print('\n== all BCX* SD regions ==')
for r in sd.region_records:
    if 'bcx' in r.name.lower() or 'bcx' in (r.tag or '').lower():
        print(' name=%r tag=%r guid=%s' % (r.name, r.tag, bytes(r.guid).hex()))

# env records too (there is a "Sanctuary" env preset per SD_FORMAT_RE)
print('\n== env records matching sanctuary/blood ==')
for e in sd.env_records:
    if 'sanct' in e.name.lower() or 'blood' in e.name.lower():
        print(' env name=%r guid=%s' % (e.name, bytes(e.guid).hex()))

# Now walk every level's 0x17 REGION list, group levels by region guid
print('\n== scanning 2282 level 0x17 region lists ==')
by_region = {}
lvl_info = {}
for li, lv in enumerate(levels):
    blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    envs = regs = auds = None
    for t, sdta in CM.parse_blob_sections(blob):
        if t == 0x17:
            try:
                m, ver, envs, regs, auds, raster = parse_0x17_header(sdta)
            except Exception as ex:
                regs = None
            break
    lvl_info[li] = {'fname': lv['fname'], 'regs': regs}
    if regs:
        for idx, g in regs:
            by_region.setdefault(bytes(g), []).append(li)

for r in sanc:
    g = bytes(r.guid)
    print('\n>>> REGION %r tag=%r guid=%s' % (r.name, r.tag, g.hex()))
    mem = by_region.get(g, [])
    print('    levels binding this region: %d' % len(mem))
    for li in mem:
        lv = levels[li]
        print('      idx=%-5d %-70s corner=%s len=%d' % (
            li, lv['fname'], lv['corner'], lv['data_length']))

json.dump({'sanc_guids': [bytes(r.guid).hex() for r in sanc]},
          open(os.path.join(os.path.dirname(__file__), 'sanc_guids.json'), 'w'))
