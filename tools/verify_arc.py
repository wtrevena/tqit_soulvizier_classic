#!/usr/bin/env python3
"""Verify merged ARC contents match expected binary merge output."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_bitmap_index,
    SEC_LEVELS, SEC_BITMAPS, SEC_DATA, SEC_DATA2)

print('Loading merged ARC...')
arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc'))
entry = [e for e in arc.entries if e.entry_type == 3][0]
print(f'  decomp_size in header: {entry.decomp_size}')

data = arc.decompress(entry)
print(f'  actual decompressed: {len(data)}')

magic = struct.unpack_from('<I', data, 0)[0]
ok = "OK" if magic == 0x0650414D else "BAD!"
print(f'  MAP magic: 0x{magic:08X} ({ok})')

sections = parse_sections(data)
sec_map = {s['type']: s for s in sections}

for s in sections:
    names = {1:'LEVELS',2:'DATA',0x1A:'DATA2',0x1B:'QUESTS',0x11:'GROUPS',0x19:'BITMAPS',0x18:'SD',0x10:'UNK'}
    label = names.get(s['type'], f'0x{s["type"]:02X}')
    print(f'  {label}: off={s["data_offset"]} size={s["size"]}')

last = sections[-1]
expected_end = last['data_offset'] + last['size']
print(f'\nExpected EOF: {expected_end}, Actual: {len(data)}, Extra: {len(data) - expected_end}')

levels = parse_level_index(data, sec_map[SEC_LEVELS])
print(f'\nLevels: {len(levels)}')

bad_magic = 0
bad_offset = 0
for i, lv in enumerate(levels):
    if lv['data_offset'] + lv['data_length'] > len(data):
        bad_offset += 1
        if bad_offset <= 3:
            print(f'  OOB level {i}: {lv["fname"][:50]} off={lv["data_offset"]} len={lv["data_length"]}')
        continue
    m = data[lv['data_offset']:lv['data_offset']+3]
    if m != b'LVL':
        if bad_magic < 5:
            mhex = data[lv['data_offset']:lv['data_offset']+4].hex()
            print(f'  Bad magic level {i}: {lv["fname"][:50]} off={lv["data_offset"]} magic={mhex}')
        bad_magic += 1

print(f'Out-of-bounds offsets: {bad_offset}/{len(levels)}')
print(f'Bad LVL magic: {bad_magic}/{len(levels)}')

bitmaps = parse_bitmap_index(data, sec_map[SEC_BITMAPS])
print(f'\nBitmaps: {len(bitmaps)}')
zero_bmp = sum(1 for b in bitmaps if b['offset'] == 0 and b['length'] == 0)
bad_bmp = sum(1 for b in bitmaps if b['offset'] > 0 and b['offset'] + b['length'] > len(data))
print(f'Zero-entry bitmaps: {zero_bmp}')
print(f'Out-of-bounds bitmaps: {bad_bmp}')

# Verify first 3 and last 3 level data matches original SVAERA
print('\nComparing first 3 levels with original SVAERA...')
orig_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
orig_data = orig_arc.decompress([e for e in orig_arc.entries if e.entry_type == 3][0])
orig_sections = parse_sections(orig_data)
orig_sec_map = {s['type']: s for s in orig_sections}
orig_levels = parse_level_index(orig_data, orig_sec_map[SEC_LEVELS])

for i in range(3):
    ol = orig_levels[i]
    ml = levels[i]
    orig_chunk = orig_data[ol['data_offset']:ol['data_offset'] + ol['data_length']]
    merge_chunk = data[ml['data_offset']:ml['data_offset'] + ml['data_length']]
    match = "MATCH" if orig_chunk == merge_chunk else "MISMATCH"
    print(f'  Level {i} ({ol["fname"][:40]}): orig_off={ol["data_offset"]} merge_off={ml["data_offset"]} {match}')

# Check a few middle levels too
for i in [100, 500, 1000, 2000]:
    if i < len(orig_levels):
        ol = orig_levels[i]
        ml = levels[i]
        orig_chunk = orig_data[ol['data_offset']:ol['data_offset'] + ol['data_length']]
        merge_chunk = data[ml['data_offset']:ml['data_offset'] + ml['data_length']]
        match = "MATCH" if orig_chunk == merge_chunk else "MISMATCH"
        print(f'  Level {i} ({ol["fname"][:40]}): {match}')

del data, orig_data
