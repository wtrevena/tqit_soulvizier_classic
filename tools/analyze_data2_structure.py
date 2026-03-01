#!/usr/bin/env python3
"""Analyze DATA2 internal structure to understand per-level pathfinding layout."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_DATA2, SEC_DATA

print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
d2_sec = ae_sec[SEC_DATA2]
d2_buf = ae_data[d2_sec['data_offset']:d2_sec['data_offset'] + d2_sec['size']]

print(f'DATA2 section: {len(d2_buf)} bytes ({len(d2_buf)/(1024**2):.1f} MB)')
print(f'LEVELS count: {len(ae_levels)}')

# Parse header
print(f'\n=== DATA2 Header ===')
for i in range(0, min(64, len(d2_buf)), 4):
    val = struct.unpack_from('<I', d2_buf, i)[0]
    fval = struct.unpack_from('<f', d2_buf, i)[0]
    print(f'  offset {i:4d}: {val:10d} (0x{val:08x})  float={fval:.4f}')

level_count = struct.unpack_from('<I', d2_buf, 4)[0]
print(f'\nLevel count from header: {level_count}')

# Check if there's a per-level offset table after the header
# Try different header sizes and see if we find an offset table
print(f'\n=== Looking for per-level offset table ===')
for header_size in [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64]:
    if header_size + level_count * 4 > len(d2_buf):
        continue
    # Read potential offset table
    offsets = []
    for i in range(min(level_count, 10)):
        val = struct.unpack_from('<I', d2_buf, header_size + i * 4)[0]
        offsets.append(val)
    
    # Check if offsets are monotonically increasing and reasonable
    is_monotonic = all(offsets[i] < offsets[i+1] for i in range(len(offsets)-1))
    in_range = all(0 < o < len(d2_buf) for o in offsets)
    
    if is_monotonic and in_range:
        print(f'  header_size={header_size}: monotonic+in-range offsets')
        print(f'    First 10: {offsets}')
        # Check stride between consecutive offsets
        strides = [offsets[i+1] - offsets[i] for i in range(len(offsets)-1)]
        print(f'    Strides: {strides}')
        
        # Read more offsets to confirm pattern
        more_offsets = []
        for i in range(min(level_count, 50)):
            val = struct.unpack_from('<I', d2_buf, header_size + i * 4)[0]
            more_offsets.append(val)
        print(f'    Range: {more_offsets[0]} - {more_offsets[-1]}')
        
        # Also check 8-byte stride (offset + length pairs)
    
    # Try 8-byte stride (offset, length) pairs
    if header_size + level_count * 8 > len(d2_buf):
        continue
    pairs = []
    for i in range(min(level_count, 10)):
        off = struct.unpack_from('<I', d2_buf, header_size + i * 8)[0]
        ln = struct.unpack_from('<I', d2_buf, header_size + i * 8 + 4)[0]
        pairs.append((off, ln))
    
    offsets_8 = [p[0] for p in pairs]
    is_monotonic_8 = all(offsets_8[i] <= offsets_8[i+1] for i in range(len(offsets_8)-1))
    in_range_8 = all(0 <= o < len(d2_buf) for o in offsets_8)
    
    if is_monotonic_8 and in_range_8 and offsets_8[0] > 0:
        print(f'  header_size={header_size} (8-byte pairs): monotonic+in-range')
        print(f'    First 10 pairs (offset, length): {pairs}')

# Also look at the LEVELS ints_raw to see if there's a DATA2 reference
print(f'\n=== Level ints_raw analysis ===')
print(f'ints_raw is 52 bytes per level. Checking structure...')
for i in range(min(5, len(ae_levels))):
    lv = ae_levels[i]
    raw = lv['ints_raw']
    vals = [struct.unpack_from('<I', raw, j)[0] for j in range(0, 52, 4)]
    fvals = [struct.unpack_from('<f', raw, j)[0] for j in range(0, 52, 4)]
    print(f'\n  Level {i}: {lv["fname"][-40:]}')
    print(f'    data_offset={lv["data_offset"]}, data_length={lv["data_length"]}')
    for j, (v, f) in enumerate(zip(vals, fvals)):
        print(f'    int[{j}]: {v:10d} (0x{v:08x})  float={f:.4f}')

# Check if any ints_raw field looks like a DATA2 offset
print(f'\n=== Checking ints_raw fields as potential DATA2 offsets ===')
for field_idx in range(13):  # 52 bytes / 4 = 13 fields
    values = []
    for lv in ae_levels[:20]:
        val = struct.unpack_from('<I', lv['ints_raw'], field_idx * 4)[0]
        values.append(val)
    
    # Check if values could be DATA2 offsets
    in_d2_range = all(0 <= v <= len(d2_buf) for v in values)
    is_sorted = all(values[i] <= values[i+1] for i in range(len(values)-1))
    
    if in_d2_range and max(values) > 1000:
        print(f'  ints_raw[{field_idx}]: in DATA2 range, sorted={is_sorted}')
        print(f'    Values: {values[:10]}...')

del ae_data
