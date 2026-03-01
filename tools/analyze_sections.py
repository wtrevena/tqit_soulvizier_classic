#!/usr/bin/env python3
"""Analyze section counts and formats for SVAERA, SV, and MapCompiler maps."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_bitmap_index,
    SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_GROUPS, SEC_SD, SEC_BITMAPS, SEC_QUESTS)

def analyze_groups(data, sec):
    buf = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    if len(buf) < 8:
        return 0
    val0 = struct.unpack_from('<I', buf, 0)[0]
    val1 = struct.unpack_from('<I', buf, 4)[0]
    return val1

def analyze_sd(data, sec):
    buf = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    if len(buf) < 4:
        return 0, 0
    count = struct.unpack_from('<I', buf, 0)[0]
    return count, len(buf)

def analyze_map(label, data):
    sections = parse_sections(data)
    sec_map = {s['type']: s for s in sections}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    bitmaps = parse_bitmap_index(data, sec_map[SEC_BITMAPS])
    groups_count = analyze_groups(data, sec_map[SEC_GROUPS])
    sd_count, sd_size = analyze_sd(data, sec_map[SEC_SD])
    
    print(f'\n=== {label} ===')
    print(f'  Total size: {len(data)} bytes ({len(data)/(1024**2):.1f} MB)')
    print(f'  Sections:')
    for s in sections:
        name = {0x01: 'LEVELS', 0x02: 'DATA', 0x11: 'GROUPS', 0x18: 'SD',
                0x19: 'BITMAPS', 0x1A: 'DATA2', 0x1B: 'QUESTS'}.get(s['type'], f'UNK-{s["type"]:#x}')
        print(f'    {name}: offset={s["header_offset"]}, size={s["size"]}')
    print(f'  LEVELS count: {len(levels)}')
    print(f'  BITMAPS count: {len(bitmaps)}')
    print(f'  GROUPS count (val1): {groups_count}')
    print(f'  SD count: {sd_count}, total SD size: {sd_size}')
    
    # Check level formats
    formats = {}
    for lv in levels:
        raw = lv['ints_raw']
        fmt_val = struct.unpack_from('<I', raw, 0)[0]
        formats[fmt_val] = formats.get(fmt_val, 0) + 1
    print(f'  Level formats: {formats}')
    
    return sec_map, levels

# SVAERA
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec_map, ae_levels = analyze_map('SVAERA', ae_data)

# SV
print('\nLoading SV...')
sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec_map, sv_levels = analyze_map('SV 0.98i', sv_data)

# MapCompiler merged
print('\nLoading MC merged...')
mc_data = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map').read_bytes()
mc_sec_map, mc_levels = analyze_map('MC merged', mc_data)

# Compare GROUPS sections
print('\n=== GROUPS Section Comparison ===')
ae_gs = ae_data[ae_sec_map[SEC_GROUPS]['data_offset']:ae_sec_map[SEC_GROUPS]['data_offset']+ae_sec_map[SEC_GROUPS]['size']]
sv_gs = sv_data[sv_sec_map[SEC_GROUPS]['data_offset']:sv_sec_map[SEC_GROUPS]['data_offset']+sv_sec_map[SEC_GROUPS]['size']]
mc_gs = mc_data[mc_sec_map[SEC_GROUPS]['data_offset']:mc_sec_map[SEC_GROUPS]['data_offset']+mc_sec_map[SEC_GROUPS]['size']]
print(f'  SVAERA GROUPS: {len(ae_gs)} bytes')
print(f'  SV GROUPS: {len(sv_gs)} bytes')
print(f'  MC GROUPS: {len(mc_gs)} bytes')
print(f'  AE==MC: {ae_gs == mc_gs}')
print(f'  AE==SV first 8: AE={ae_gs[:8].hex()} SV={sv_gs[:8].hex()} MC={mc_gs[:8].hex()}')

# Compare SD sections
print('\n=== SD Section Comparison ===')
ae_sd = ae_data[ae_sec_map[SEC_SD]['data_offset']:ae_sec_map[SEC_SD]['data_offset']+ae_sec_map[SEC_SD]['size']]
sv_sd = sv_data[sv_sec_map[SEC_SD]['data_offset']:sv_sec_map[SEC_SD]['data_offset']+sv_sec_map[SEC_SD]['size']]
mc_sd = mc_data[mc_sec_map[SEC_SD]['data_offset']:mc_sec_map[SEC_SD]['data_offset']+mc_sec_map[SEC_SD]['size']]
print(f'  SVAERA SD: {len(ae_sd)} bytes')
print(f'  SV SD: {len(sv_sd)} bytes')
print(f'  MC SD: {len(mc_sd)} bytes')
print(f'  AE==MC: {ae_sd == mc_sd}')

# Compare DATA2
print('\n=== DATA2 Section Comparison ===')
ae_d2 = ae_data[ae_sec_map[SEC_DATA2]['data_offset']:ae_sec_map[SEC_DATA2]['data_offset']+ae_sec_map[SEC_DATA2]['size']]
mc_d2 = mc_data[mc_sec_map[SEC_DATA2]['data_offset']:mc_sec_map[SEC_DATA2]['data_offset']+mc_sec_map[SEC_DATA2]['size']]
print(f'  SVAERA DATA2: {len(ae_d2)} bytes')
print(f'  MC DATA2: {len(mc_d2)} bytes')
print(f'  AE==MC: {ae_d2 == mc_d2}')

del ae_data, sv_data, mc_data
