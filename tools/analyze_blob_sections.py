#!/usr/bin/env python3
"""Analyze internal section types of level blobs."""
import struct, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

def parse_blob_sections(blob):
    sections = []
    if len(blob) < 4: return sections, 0
    magic = struct.unpack_from('<I', blob, 0)[0]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8 or ss > 50_000_000:
            break
        sections.append({'type': st, 'size': ss, 'offset': pos + 8, 'data': blob[pos+8:pos+8+ss]})
        pos += 8 + ss
    return sections, magic

def load(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = parse_sections(data)
    levels = parse_level_index(data, {s['type']:s for s in secs}[SEC_LEVELS])
    return data, levels

print('Loading maps...')
ae_data, ae_levels = load(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_data, sv_levels = load(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')

ae_by = {lv['fname'].replace('\\','/').lower(): lv for lv in ae_levels}
sv_by = {lv['fname'].replace('\\','/').lower(): lv for lv in sv_levels}

for name in ['levels/world/greece/delphi/delphilowlands02.lvl',
             'levels/world/greece/delphi/delphilowlands04.lvl']:
    print(f'\n{"="*70}\n{name}\n{"="*70}')
    for label, mdata, by in [('SVAERA', ae_data, ae_by), ('SV', sv_data, sv_by)]:
        lv = by.get(name)
        if not lv:
            print(f'  [{label}] NOT FOUND'); continue
        blob = mdata[lv['data_offset']:lv['data_offset']+lv['data_length']]
        secs, magic = parse_blob_sections(blob)
        print(f'  [{label}] magic=0x{magic:08X}, {len(secs)} sections, {len(blob)} bytes')
        for i, s in enumerate(secs):
            drx = ' *** HAS drxmap ***' if b'drxmap' in s['data'] else ''
            print(f'    [{i}] type=0x{s["type"]:02X} size={s["size"]:>8}{drx}')

# Global section type frequency
print(f'\n{"="*70}\nSVAERA section type frequency ({len(ae_levels)} levels)\n{"="*70}')
tc = Counter()
for lv in ae_levels:
    blob = ae_data[lv['data_offset']:lv['data_offset']+lv['data_length']]
    for s, _ in [parse_blob_sections(blob)]:
        for sec in s:
            tc[sec['type']] += 1
for t, c in tc.most_common():
    print(f'  0x{t:02X}: {c} occurrences')

# drxmap section types in SV
print(f'\n{"="*70}\nSV drxmap section types\n{"="*70}')
drx_types = Counter()
for lv in sv_levels:
    blob = sv_data[lv['data_offset']:lv['data_offset']+lv['data_length']]
    for s, _ in [parse_blob_sections(blob)]:
        for sec in s:
            if b'drxmap' in sec['data']:
                drx_types[sec['type']] += 1
for t, c in drx_types.most_common():
    print(f'  0x{t:02X}: {c} occurrences')

del ae_data, sv_data
