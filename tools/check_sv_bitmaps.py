#!/usr/bin/env python3
"""Check bitmap entries in original SV and SVAERA maps."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_bitmap_index,
    SEC_LEVELS, SEC_BITMAPS)

for name, path in [
    ('SVAERA', r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'),
    ('SV 0.98i', r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'),
]:
    print(f'\n=== {name} ===')
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sections = parse_sections(data)
    sec_map = {s['type']: s for s in sections}
    
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    bitmaps = parse_bitmap_index(data, sec_map[SEC_BITMAPS])
    
    print(f'  Levels: {len(levels)}')
    print(f'  Bitmaps: {len(bitmaps)}')
    
    zero = sum(1 for b in bitmaps if b['offset'] == 0 and b['length'] == 0)
    nonzero = sum(1 for b in bitmaps if b['offset'] > 0)
    zero_len_only = sum(1 for b in bitmaps if b['offset'] > 0 and b['length'] == 0)
    
    print(f'  Zero offset+length: {zero}')
    print(f'  Non-zero offset: {nonzero}')
    print(f'  Non-zero offset but zero length: {zero_len_only}')
    
    # Show bitmap section raw header
    bmp_sec = sec_map[SEC_BITMAPS]
    raw = data[bmp_sec['data_offset']:bmp_sec['data_offset'] + 16]
    vals = struct.unpack_from('<4I', raw, 0)
    print(f'  Bitmap header: unknown={vals[0]} count={vals[1]} first_entry=({vals[2]}, {vals[3]})')
    
    # Show first and last few bitmap entries
    for i in [0, 1, len(bitmaps)-2, len(bitmaps)-1]:
        if i < len(bitmaps):
            b = bitmaps[i]
            print(f'  Bitmap[{i}]: offset={b["offset"]} length={b["length"]}')
    
    del data
