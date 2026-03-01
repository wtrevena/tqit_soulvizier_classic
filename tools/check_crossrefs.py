#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])

print('=== Delphi levels referencing bloodcave/secret/portal/hidden ===')
for lv in sv_levels:
    fn = lv['fname']
    if 'delphi' in fn.lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        lower_blob = blob.lower()
        for kw in [b'bloodcave', b'blood_cave', b'secret', b'portal', b'hidden']:
            if kw in lower_blob:
                print(f'  {fn} contains "{kw.decode()}"')

print()
print('=== xBloodCave levels referencing delphi/crisaeos ===')
for lv in sv_levels:
    fn = lv['fname']
    if 'bloodcave' in fn.lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        lower_blob = blob.lower()
        for kw in [b'delphi', b'crisaeos', b'lowlands']:
            if kw in lower_blob:
                print(f'  {fn} contains "{kw.decode()}"')

print()
print('=== All DBR strings in BC_initialpathway.lvl ===')
for lv in sv_levels:
    if 'bc_initialpathway' in lv['fname'].lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        i = 0
        found = set()
        while i < len(blob):
            for prefix in [b'records/', b'xpack/']:
                idx = blob.find(prefix, i)
                if idx != -1:
                    break
            else:
                break
            end = blob.find(b'\x00', idx)
            if end == -1:
                break
            s = blob[idx:end].decode('ascii', errors='replace')
            found.add(s)
            i = end + 1
        for s in sorted(found):
            print(f'    {s}')
