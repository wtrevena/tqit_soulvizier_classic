#!/usr/bin/env python3
"""Compare LVL blob headers between SVAERA and SV for shared levels."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])

print('Loading SV...')
sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])

ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i

# Check LVL blob headers for shared levels with drxmap
shared_drx_names = [
    'DelphiLowlands03', 'DelphiLowlands04', 'DelphiLowlands02',
    'StartingFarmland06D', 'HiddenValley01', 'HiddenValleyBorder04',
    'RoadToTown03A', 'ScrabledEggs_Floor06', 'Random09A'
]

print('\n=== LVL Blob Headers: SVAERA vs SV ===')
for sv_lv in sv_levels:
    key = sv_lv['fname'].replace('\\', '/').lower()
    if key not in ae_by_name:
        continue
    
    matching = False
    for name in shared_drx_names:
        if name.lower() in key.lower():
            matching = True
            break
    if not matching:
        continue
    
    ae_idx = ae_by_name[key]
    ae_lv = ae_levels[ae_idx]
    
    ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + min(ae_lv['data_length'], 128)]
    sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + min(sv_lv['data_length'], 128)]
    
    print(f'\n  {sv_lv["fname"]}')
    print(f'    SVAERA: {ae_lv["data_length"]} bytes, header: {ae_blob[:20].hex()}')
    print(f'    SV:     {sv_lv["data_length"]} bytes, header: {sv_blob[:20].hex()}')
    
    # Parse LVL header: 'LVL' + version byte
    if ae_blob[:3] == b'LVL' and sv_blob[:3] == b'LVL':
        ae_ver = ae_blob[3]
        sv_ver = sv_blob[3]
        print(f'    LVL format: SVAERA=0x{ae_ver:02x} SV=0x{sv_ver:02x} {"MATCH" if ae_ver == sv_ver else "MISMATCH!"}')
    
    # Compare ints_raw
    ae_raw = ae_lv['ints_raw']
    sv_raw = sv_lv['ints_raw']
    ae_vals = [struct.unpack_from('<I', ae_raw, j)[0] for j in range(0, 52, 4)]
    sv_vals = [struct.unpack_from('<I', sv_raw, j)[0] for j in range(0, 52, 4)]
    
    diffs = [(i, a, s) for i, (a, s) in enumerate(zip(ae_vals, sv_vals)) if a != s]
    if diffs:
        print(f'    ints_raw differences ({len(diffs)}):')
        for idx, ae_v, sv_v in diffs:
            print(f'      int[{idx}]: AE={ae_v} SV={sv_v}')
    else:
        print(f'    ints_raw: IDENTICAL')

# Also check a few SV-only levels for their format version
print('\n\n=== SV-Only Level LVL Versions ===')
sv_only_count = 0
format_counts = {}
for sv_lv in sv_levels:
    key = sv_lv['fname'].replace('\\', '/').lower()
    if key not in ae_by_name:
        blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + 4]
        if blob[:3] == b'LVL':
            ver = blob[3]
            format_counts[ver] = format_counts.get(ver, 0) + 1
            sv_only_count += 1
            if sv_only_count <= 5:
                print(f'  {sv_lv["fname"]}: LVL v0x{ver:02x}')

print(f'\n  SV-only level format versions: { {f"0x{k:02x}": v for k, v in format_counts.items()} }')

# And check all SVAERA level formats
print('\n=== ALL SVAERA Level LVL Versions ===')
ae_format_counts = {}
for lv in ae_levels:
    blob = ae_data[lv['data_offset']:lv['data_offset'] + 4]
    if blob[:3] == b'LVL':
        ver = blob[3]
        ae_format_counts[ver] = ae_format_counts.get(ver, 0) + 1
print(f'  SVAERA format versions: { {f"0x{k:02x}": v for k, v in ae_format_counts.items()} }')

del ae_data, sv_data
