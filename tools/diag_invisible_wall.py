#!/usr/bin/env python3
"""Diagnose invisible wall: compare merged map vs SV original for swapped levels."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_bitmap_index,
    SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_BITMAPS)

def load_map(path, label):
    print(f'\nLoading {label}: {path}')
    if path.suffix == '.arc':
        arc = ArcArchive.from_file(path)
        data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    else:
        data = path.read_bytes()
    sections = parse_sections(data)
    sec_map = {s['type']: s for s in sections}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    bitmaps = parse_bitmap_index(data, sec_map[SEC_BITMAPS])
    d2_start = sec_map[SEC_DATA2]['data_offset']
    d2_size = sec_map[SEC_DATA2]['size']
    print(f'  {len(levels)} levels, {len(bitmaps)} bitmaps')
    print(f'  DATA2: offset={d2_start}, size={d2_size}')
    print(f'  DATA: offset={sec_map[SEC_DATA]["data_offset"]}, size={sec_map[SEC_DATA]["size"]}')
    return data, levels, bitmaps, sec_map

sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
merged_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

sv_data, sv_levels, sv_bitmaps, sv_sec = load_map(sv_path, 'SV original')
mg_data, mg_levels, mg_bitmaps, mg_sec = load_map(merged_path, 'Merged')

# Build name indices
sv_by_name = {}
for i, lv in enumerate(sv_levels):
    sv_by_name[lv['fname'].replace('\\', '/').lower()] = i
mg_by_name = {}
for i, lv in enumerate(mg_levels):
    mg_by_name[lv['fname'].replace('\\', '/').lower()] = i

# Check specific levels
targets = ['hiddenvalley01', 'random09a']
for target in targets:
    print(f'\n{"="*60}')
    print(f'  Level: {target}')
    print(f'{"="*60}')

    # Find in both maps
    sv_idx = mg_idx = None
    for key in sv_by_name:
        if target in key.lower():
            sv_idx = sv_by_name[key]
            break
    for key in mg_by_name:
        if target in key.lower():
            mg_idx = mg_by_name[key]
            break

    if sv_idx is None or mg_idx is None:
        print(f'  NOT FOUND: sv={sv_idx}, merged={mg_idx}')
        continue

    sv_lv = sv_levels[sv_idx]
    mg_lv = mg_levels[mg_idx]

    # Compare ints_raw
    sv_ints = struct.unpack_from('<13I', sv_lv['ints_raw'])
    mg_ints = struct.unpack_from('<13I', mg_lv['ints_raw'])
    print(f'\n  ints_raw comparison:')
    for j in range(13):
        match = 'OK' if sv_ints[j] == mg_ints[j] else f'DIFF sv={sv_ints[j]} mg={mg_ints[j]}'
        print(f'    [{j:2d}] SV={sv_ints[j]:10d}  MG={mg_ints[j]:10d}  {match}')

    # Compare level blob
    sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
    mg_blob = mg_data[mg_lv['data_offset']:mg_lv['data_offset'] + mg_lv['data_length']]
    print(f'\n  Level blob:')
    print(f'    SV: offset={sv_lv["data_offset"]}, len={sv_lv["data_length"]}, magic={sv_blob[:4]}')
    print(f'    MG: offset={mg_lv["data_offset"]}, len={mg_lv["data_length"]}, magic={mg_blob[:4]}')
    print(f'    Same length: {len(sv_blob) == len(mg_blob)}')
    if len(sv_blob) == len(mg_blob):
        print(f'    Byte-identical: {sv_blob == mg_blob}')
    else:
        print(f'    Length diff: {len(mg_blob) - len(sv_blob)} bytes')
        # Check if first N bytes match
        cmp_len = min(len(sv_blob), len(mg_blob))
        first_diff = -1
        for k in range(cmp_len):
            if sv_blob[k] != mg_blob[k]:
                first_diff = k
                break
        if first_diff >= 0:
            print(f'    First byte diff at: {first_diff}')
        else:
            print(f'    First {cmp_len} bytes identical (extra bytes in {"merged" if len(mg_blob) > len(sv_blob) else "SV"})')

    # Compare bitmap entries
    print(f'\n  Bitmap entries:')
    if sv_idx < len(sv_bitmaps):
        sv_bm = sv_bitmaps[sv_idx]
        print(f'    SV: offset={sv_bm["offset"]}, length={sv_bm["length"]}')
        # Check if SV offset is absolute or relative
        d2_data_start = sv_sec[SEC_DATA2]['data_offset']
        d2_end = d2_data_start + sv_sec[SEC_DATA2]['size']
        if sv_bm['offset'] >= d2_data_start and sv_bm['offset'] < d2_end:
            print(f'    SV offset is WITHIN DATA2 section (abs offset, relative to DATA2 start: {sv_bm["offset"] - d2_data_start})')
        elif sv_bm['offset'] < d2_data_start:
            print(f'    SV offset is BEFORE DATA2 section — might be relative offset')
        else:
            print(f'    SV offset is AFTER DATA2 section end — ERROR?')

    if mg_idx < len(mg_bitmaps):
        mg_bm = mg_bitmaps[mg_idx]
        print(f'    MG: offset={mg_bm["offset"]}, length={mg_bm["length"]}')
        d2_data_start = mg_sec[SEC_DATA2]['data_offset']
        d2_end = d2_data_start + mg_sec[SEC_DATA2]['size']
        if mg_bm['offset'] >= d2_data_start and mg_bm['offset'] < d2_end:
            print(f'    MG offset is WITHIN DATA2 section (abs offset, relative to DATA2 start: {mg_bm["offset"] - d2_data_start})')
        elif mg_bm['offset'] < d2_data_start:
            print(f'    MG offset is BEFORE DATA2 section — ERROR: wrong offset!')
        else:
            print(f'    MG offset is AFTER DATA2 section end — ERROR?')

    # Compare actual DATA2 bytes
    if sv_idx < len(sv_bitmaps) and mg_idx < len(mg_bitmaps):
        sv_bm = sv_bitmaps[sv_idx]
        mg_bm = mg_bitmaps[mg_idx]
        if sv_bm['length'] > 0 and mg_bm['length'] > 0:
            sv_d2 = sv_data[sv_bm['offset']:sv_bm['offset'] + sv_bm['length']]
            mg_d2 = mg_data[mg_bm['offset']:mg_bm['offset'] + mg_bm['length']]
            print(f'\n  DATA2 content comparison:')
            print(f'    SV: {len(sv_d2)} bytes, first 16: {sv_d2[:16].hex()}')
            print(f'    MG: {len(mg_d2)} bytes, first 16: {mg_d2[:16].hex()}')
            print(f'    Same length: {len(sv_d2) == len(mg_d2)}')
            if len(sv_d2) == len(mg_d2):
                print(f'    Byte-identical: {sv_d2 == mg_d2}')
            else:
                print(f'    Length diff: {len(mg_d2) - len(sv_d2)} bytes')

# Also show a summary of ALL swapped levels
print(f'\n{"="*60}')
print(f'  All swapped levels (shared + drxmap in SV)')
print(f'{"="*60}')
for i, lv in enumerate(sv_levels):
    key = lv['fname'].replace('\\', '/').lower()
    chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    if b'drxmap' in chunk:
        mg_key_idx = mg_by_name.get(key)
        if mg_key_idx is not None:
            mg_lv = mg_levels[mg_key_idx]
            sv_ver = chunk[3] if len(chunk) > 3 else 0
            mg_blob = mg_data[mg_lv['data_offset']:mg_lv['data_offset'] + mg_lv['data_length']]
            mg_ver = mg_blob[3] if len(mg_blob) > 3 else 0
            sv_bm = sv_bitmaps[i] if i < len(sv_bitmaps) else {'offset': 0, 'length': 0}
            mg_bm = mg_bitmaps[mg_key_idx] if mg_key_idx < len(mg_bitmaps) else {'offset': 0, 'length': 0}
            short = lv['fname'].split('\\')[-1]
            blob_ok = 'OK' if len(sv_data[lv['data_offset']:lv['data_offset']+lv['data_length']]) == mg_lv['data_length'] else 'SIZE_DIFF'
            bm_ok = 'OK' if sv_bm['length'] == mg_bm['length'] else f'LEN_DIFF({sv_bm["length"]} vs {mg_bm["length"]})'
            print(f'  {short}: sv_ver=0x{sv_ver:02x} mg_ver=0x{mg_ver:02x} blob={blob_ok} bm_len={bm_ok}')
