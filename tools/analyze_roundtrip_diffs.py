#!/usr/bin/env python3
"""Analyze which sections have byte differences in the MapCompiler round-trip."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

print('Loading original SVAERA map...')
arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
orig = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
print(f'  {len(orig)} bytes')

print('Loading MapCompiler round-trip...')
rt = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\test_rawtrip.map').read_bytes()
print(f'  {len(rt)} bytes')

assert len(orig) == len(rt), f'Size mismatch: {len(orig)} vs {len(rt)}'

# Parse sections in original
sections = parse_sections(orig)
sec_map = {}
for s in sections:
    sec_map[s['type']] = s
names = {1:'LEVELS', 2:'DATA', 0x10:'UNK', 0x11:'GROUPS', 0x18:'SD',
         0x19:'BITMAPS', 0x1A:'DATA2', 0x1B:'QUESTS'}

print('\nByte differences by section:')
total_diffs = 0
for s in sections:
    label = names.get(s['type'], f'0x{s["type"]:02X}')
    start = s['data_offset']
    end = start + s['size']
    diffs = sum(1 for i in range(start, end) if orig[i] != rt[i])
    total_diffs += diffs
    if diffs > 0:
        # Find first diff in this section
        first_diff = None
        for i in range(start, end):
            if orig[i] != rt[i]:
                first_diff = i - start
                break
        print(f'  {label:8s}: {diffs:6d} diffs (first at section offset {first_diff})')
    else:
        print(f'  {label:8s}:      0 diffs')

# Check header
header_diffs = sum(1 for i in range(8) if orig[i] != rt[i])
print(f'  HEADER  :      {header_diffs} diffs')

# Also check between sections (padding/headers)
section_header_diffs = 0
for s in sections:
    hdr_start = s['data_offset'] - 8
    for i in range(hdr_start, s['data_offset']):
        if orig[i] != rt[i]:
            section_header_diffs += 1
print(f'  SEC HDRS:      {section_header_diffs} diffs')

print(f'\nTotal: {total_diffs}')

# If diffs are only in DATA section, check which levels are affected
data_sec = sec_map[2]  # DATA
levels = parse_level_index(orig, sec_map[1])  # LEVELS section

print('\nLevels with data differences:')
affected = 0
for i, lv in enumerate(levels):
    start = lv['data_offset']
    end = start + lv['data_length']
    if end > len(orig):
        continue
    diffs = sum(1 for j in range(start, end) if orig[j] != rt[j])
    if diffs > 0:
        affected += 1
        if affected <= 10:
            print(f'  Level {i} ({lv["fname"][:50]}): {diffs} diffs')

print(f'\nTotal affected levels: {affected}/{len(levels)}')

del orig, rt
