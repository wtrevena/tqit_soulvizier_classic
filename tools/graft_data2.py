#!/usr/bin/env python3
"""
Graft SVAERA's DATA2 pathfinding onto MC-compiled map.

MC compiled all levels properly from editor .lvl files but produced
an empty DATA2. We splice in SVAERA's full 682 MB DATA2 (with patched
level count) and recalculate all offsets into the DATA section.
"""
import sys, struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, build_level_index,
    SEC_LEVELS, SEC_DATA2, SEC_BITMAPS)

mc_map = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_source\world01.map')
svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

# Load MC map
print('Loading MC-compiled map...')
mc_data = mc_map.read_bytes()
mc_sections = parse_sections(mc_data)
mc_sec_map = {s['type']: s for s in mc_sections}
mc_levels = parse_level_index(mc_data, mc_sec_map[SEC_LEVELS])
print(f'  {len(mc_levels)} levels, {len(mc_data)/(1024**2):.1f} MB')

# Load SVAERA for DATA2
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(svaera_arc_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}
ae_d2_sec = ae_sec_map[SEC_DATA2]
ae_d2_raw = ae_data[ae_d2_sec['data_offset']:ae_d2_sec['data_offset'] + ae_d2_sec['size']]
print(f'  SVAERA DATA2: {len(ae_d2_raw)} bytes ({len(ae_d2_raw)/(1024**2):.1f} MB)')
ae_d2_count = struct.unpack_from('<I', ae_d2_raw, 4)[0]
print(f'  SVAERA DATA2 level count: {ae_d2_count}')
del ae_data

# Patch DATA2 level count
ae_d2_patched = bytearray(ae_d2_raw)
struct.pack_into('<I', ae_d2_patched, 4, len(mc_levels))
print(f'  Patched count: {len(mc_levels)}')

# Map section layout (from MC):
# QUESTS, GROUPS, SD, LEVELS, BITMAPS, UNK-0x10, DATA2, DATA
# DATA2 and DATA are the last two sections.
# We replace DATA2 and keep DATA, adjusting offsets.
mc_d2 = mc_sec_map[SEC_DATA2]
mc_data_sec = mc_sec_map[0x02]  # DATA

# Everything before DATA2
prefix = mc_data[:mc_d2['header_offset']]
# DATA section raw (header + data)
data_raw = mc_data[mc_data_sec['header_offset']:mc_data_sec['data_offset'] + mc_data_sec['size']]

# New DATA2 section (header + data)
new_d2_section = struct.pack('<II', SEC_DATA2, len(ae_d2_patched)) + bytes(ae_d2_patched)

# Calculate where DATA section will start in the new file
new_data_start = len(prefix) + len(new_d2_section) + 8  # +8 for DATA section header
old_data_start = mc_data_sec['data_offset']
shift = new_data_start - old_data_start
print(f'\n  Old DATA offset: {old_data_start}')
print(f'  New DATA offset: {new_data_start}')
print(f'  Shift: {shift} bytes ({shift/(1024**2):.1f} MB)')

# Adjust level data_offset values
adjusted_levels = []
for lv in mc_levels:
    new_lv = dict(lv)
    new_lv['data_offset'] = lv['data_offset'] + shift
    adjusted_levels.append(new_lv)

# Rebuild LEVELS section
new_levels_payload = build_level_index(adjusted_levels)

# Adjust bitmap offsets too
bmp_sec = mc_sec_map[SEC_BITMAPS]
bmp_raw = bytearray(mc_data[bmp_sec['data_offset']:bmp_sec['data_offset'] + bmp_sec['size']])
bmp_count = struct.unpack_from('<I', bmp_raw, 0)[0]
if bmp_count > 0:
    bmp_idx = 4
    for i in range(bmp_count):
        if bmp_idx + 8 <= len(bmp_raw):
            old_off = struct.unpack_from('<I', bmp_raw, bmp_idx)[0]
            old_len = struct.unpack_from('<I', bmp_raw, bmp_idx + 4)[0]
            if old_off > 0:
                struct.pack_into('<I', bmp_raw, bmp_idx, old_off + shift)
            bmp_idx += 8

# Now rebuild the entire map
print('\nRebuilding map...')
result = bytearray()

# MAP magic header (first 8 bytes)
result += mc_data[:8]

# Write sections in order (skip the 8-byte file header)
for s in mc_sections:
    sec_type = s['type']
    if sec_type == SEC_DATA2:
        # Replace with SVAERA's DATA2
        result += new_d2_section
    elif sec_type == SEC_LEVELS:
        # Replace with adjusted levels
        result += struct.pack('<II', SEC_LEVELS, len(new_levels_payload))
        result += new_levels_payload
    elif sec_type == SEC_BITMAPS:
        # Replace with adjusted bitmaps
        result += struct.pack('<II', SEC_BITMAPS, len(bmp_raw))
        result += bytes(bmp_raw)
    elif sec_type == 0x02:
        # DATA section - copy as-is (level blob data hasn't changed)
        result += mc_data[s['header_offset']:s['data_offset'] + s['size']]
    else:
        # Other sections (QUESTS, GROUPS, SD, UNK-0x10) - copy as-is
        result += mc_data[s['header_offset']:s['data_offset'] + s['size']]

result_bytes = bytes(result)

# Verify
print('\nVerifying...')
v_sections = parse_sections(result_bytes)
v_sec_map = {s['type']: s for s in v_sections}
v_levels = parse_level_index(result_bytes, v_sec_map[SEC_LEVELS])

bad_offsets = sum(1 for lv in v_levels if lv['data_offset'] + lv['data_length'] > len(result))
bad_magic = sum(1 for lv in v_levels if result_bytes[lv['data_offset']:lv['data_offset']+3] != b'LVL')
d2_count = struct.unpack_from('<I', result_bytes, v_sec_map[SEC_DATA2]['data_offset'] + 4)[0]
zero_ints = sum(1 for lv in v_levels if lv['ints_raw'] == b'\x00' * 52)

formats = {}
for lv in v_levels:
    ver = result_bytes[lv['data_offset'] + 3]
    formats[f'0x{ver:02x}'] = formats.get(f'0x{ver:02x}', 0) + 1

print(f'  Levels: {len(v_levels)}')
print(f'  Formats: {formats}')
print(f'  DATA2 count: {d2_count} (should be {len(v_levels)})')
print(f'  DATA2 size: {v_sec_map[SEC_DATA2]["size"]/(1024**2):.1f} MB')
print(f'  Bad offsets: {bad_offsets}')
print(f'  Bad magic: {bad_magic}')
print(f'  Zero ints_raw: {zero_ints}')
print(f'  drxmap refs: {result_bytes.count(b"drxmap")}')
print(f'  Total size: {len(result)/(1024**2):.1f} MB')
print(f'  Under 2GB: {len(result) < 2147483647}')

# Package into ARC
print(f'\nPackaging into ARC...')
arc = ArcArchive.from_file(svaera_arc_path)
arc.set_file('world/world01.map', result_bytes)
arc.write(output_arc)
print(f'  ARC: {output_arc.stat().st_size/(1024**2):.1f} MB')

del mc_data, result, result_bytes
print('Done!')
