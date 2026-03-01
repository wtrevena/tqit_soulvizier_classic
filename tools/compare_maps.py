#!/usr/bin/env python3
"""Quick structural comparison between grafted map and SVAERA."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

print('Loading maps...')
ae_arc = ArcArchive.from_file(svaera_arc_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])

our_arc = ArcArchive.from_file(output_arc)
our_data = our_arc.decompress([e for e in our_arc.entries if e.entry_type == 3][0])

# File headers
print(f'\n=== File Headers ===')
print(f'SVAERA: {ae_data[:8].hex()}')
print(f'OURS:   {our_data[:8].hex()}')

# Compare section structure
ae_secs = parse_sections(ae_data)
our_secs = parse_sections(our_data)

print(f'\n=== Section Count ===')
print(f'SVAERA: {len(ae_secs)} sections')
print(f'OURS:   {len(our_secs)} sections')

print(f'\n=== Section Order ===')
for i, (ae_s, our_s) in enumerate(zip(ae_secs, our_secs)):
    match = 'OK' if ae_s['type'] == our_s['type'] else 'MISMATCH'
    print(f'  [{i}] SVAERA=0x{ae_s["type"]:02x} OURS=0x{our_s["type"]:02x} {match}')

# Compare first few levels
ae_sec_map = {s['type']: s for s in ae_secs}
our_sec_map = {s['type']: s for s in our_secs}
ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
our_levels = parse_level_index(our_data, our_sec_map[SEC_LEVELS])

print(f'\n=== Level Comparison (first 10) ===')
for i in range(min(10, len(ae_levels), len(our_levels))):
    ae_lv = ae_levels[i]
    our_lv = our_levels[i]
    ae_ver = ae_data[ae_lv['data_offset']+3] if ae_data[ae_lv['data_offset']:ae_lv['data_offset']+3] == b'LVL' else '?'
    our_ver = our_data[our_lv['data_offset']+3] if our_data[our_lv['data_offset']:our_lv['data_offset']+3] == b'LVL' else '?'
    
    name_match = ae_lv['fname'] == our_lv['fname']
    ints_match = ae_lv['ints_raw'] == our_lv['ints_raw']
    size_match = ae_lv['data_length'] == our_lv['data_length']
    ver_match = ae_ver == our_ver
    
    flags = []
    if not name_match: flags.append('NAME')
    if not ints_match: flags.append('INTS')
    if not size_match: flags.append(f'SIZE({ae_lv["data_length"]}vs{our_lv["data_length"]})')
    if not ver_match: flags.append(f'VER(0x{ae_ver:02x}vs0x{our_ver:02x})')
    
    status = ' '.join(flags) if flags else 'OK'
    print(f'  [{i}] {ae_lv["fname"][:60]:60s} {status}')

# Check for the shared drxmap levels
print(f'\n=== Shared drxmap levels ===')
targets = ['delphilowlands04', 'delphilowlands02', 'delphilowlands03', 'delphilowlands01', 'random09a']
ae_by_name = {lv['fname'].lower(): (i, lv) for i, lv in enumerate(ae_levels)}
our_by_name = {lv['fname'].lower(): (i, lv) for i, lv in enumerate(our_levels)}

for t in targets:
    for key in ae_by_name:
        if t in key.lower():
            ae_i, ae_lv = ae_by_name[key]
            if key in our_by_name:
                our_i, our_lv = our_by_name[key]
                ae_ver = ae_data[ae_lv['data_offset']+3]
                our_ver = our_data[our_lv['data_offset']+3]
                ae_drx = b'drxmap' in ae_data[ae_lv['data_offset']:ae_lv['data_offset']+ae_lv['data_length']]
                our_drx = b'drxmap' in our_data[our_lv['data_offset']:our_lv['data_offset']+our_lv['data_length']]
                ints_match = ae_lv['ints_raw'] == our_lv['ints_raw']
                
                print(f'  {ae_lv["fname"]}:')
                print(f'    SVAERA: ver=0x{ae_ver:02x}, size={ae_lv["data_length"]}, drxmap={ae_drx}')
                print(f'    OURS:   ver=0x{our_ver:02x}, size={our_lv["data_length"]}, drxmap={our_drx}')
                print(f'    ints_raw match: {ints_match}')
            break

# Count differing levels
print(f'\n=== Level Differences Summary ===')
diff_ver = 0
diff_size = 0
diff_ints = 0
same = 0
for i in range(min(len(ae_levels), len(our_levels))):
    ae_lv = ae_levels[i]
    our_lv = our_levels[i]
    if ae_lv['fname'] != our_lv['fname']:
        continue
    ae_ver = ae_data[ae_lv['data_offset']+3]
    our_ver = our_data[our_lv['data_offset']+3]
    if ae_ver != our_ver: diff_ver += 1
    if ae_lv['data_length'] != our_lv['data_length']: diff_size += 1
    if ae_lv['ints_raw'] != our_lv['ints_raw']: diff_ints += 1
    if ae_ver == our_ver and ae_lv['data_length'] == our_lv['data_length'] and ae_lv['ints_raw'] == our_lv['ints_raw']:
        same += 1

print(f'  Identical: {same}')
print(f'  Different version: {diff_ver}')
print(f'  Different size: {diff_size}')
print(f'  Different ints_raw: {diff_ints}')
print(f'  New (SV-only): {len(our_levels) - len(ae_levels)}')

del ae_data, our_data
