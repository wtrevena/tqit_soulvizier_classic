#!/usr/bin/env python3
"""
Graft SVAERA's DATA2 onto MC map via in-place patching.
Preserves exact MC byte layout, only patches DATA2 and offsets.
"""
import sys, struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_DATA2, SEC_BITMAPS

mc_map = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_source\world01.map')
svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

print('Loading MC-compiled map...')
mc_data = mc_map.read_bytes()
mc_sections = parse_sections(mc_data)
mc_sec_map = {s['type']: s for s in mc_sections}

# Print section layout
print('\nMC section layout:')
for s in mc_sections:
    name = {0x01:'LEVELS',0x02:'DATA',0x10:'UNK10',0x11:'GROUPS',
            0x18:'SD',0x19:'BITMAPS',0x1A:'DATA2',0x1B:'QUESTS'}.get(s['type'],f'0x{s["type"]:02x}')
    end = s['data_offset'] + s['size']
    print(f'  {name}: [{s["header_offset"]}..{end}) = {end - s["header_offset"]} bytes')

# Load SVAERA DATA2
print('\nLoading SVAERA DATA2...')
ae_arc = ArcArchive.from_file(svaera_arc_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}

# Also check SVAERA section layout for reference
print('\nSVAERA section layout:')
for s in parse_sections(ae_data):
    name = {0x01:'LEVELS',0x02:'DATA',0x10:'UNK10',0x11:'GROUPS',
            0x18:'SD',0x19:'BITMAPS',0x1A:'DATA2',0x1B:'QUESTS'}.get(s['type'],f'0x{s["type"]:02x}')
    end = s['data_offset'] + s['size']
    print(f'  {name}: [{s["header_offset"]}..{end}) = {end - s["header_offset"]} bytes')

ae_d2 = ae_sec_map[SEC_DATA2]
ae_d2_data = ae_data[ae_d2['data_offset']:ae_d2['data_offset'] + ae_d2['size']]
print(f'\nSVAERA DATA2: {len(ae_d2_data)} bytes ({len(ae_d2_data)/(1024**2):.1f} MB)')

# Get level count
mc_levels = parse_level_index(mc_data, mc_sec_map[SEC_LEVELS])
total_levels = len(mc_levels)
print(f'MC levels: {total_levels}')

# Patch SVAERA DATA2 count
ae_d2_patched = bytearray(ae_d2_data)
old_count = struct.unpack_from('<I', ae_d2_patched, 4)[0]
struct.pack_into('<I', ae_d2_patched, 4, total_levels)
print(f'DATA2 count: {old_count} -> {total_levels}')

# MC map structure: DATA2 is second-to-last, DATA is last.
# Plan: splice SVAERA DATA2 in place of MC DATA2.
mc_d2 = mc_sec_map[SEC_DATA2]
mc_data_sec = mc_sec_map[0x02]

# Verify DATA is the last section
last_sec = mc_sections[-1]
assert last_sec['type'] == 0x02, f"Expected DATA as last section, got 0x{last_sec['type']:02x}"
second_last = mc_sections[-2]
assert second_last['type'] == SEC_DATA2, f"Expected DATA2 as second-to-last, got 0x{second_last['type']:02x}"

# Build new map:
# [everything before DATA2] + [new DATA2 header+data] + [DATA header+data]
prefix = mc_data[:mc_d2['header_offset']]
data_section = mc_data[mc_data_sec['header_offset']:]  # DATA to end of file

new_d2_header = struct.pack('<II', SEC_DATA2, len(ae_d2_patched))
new_map = bytearray(prefix) + new_d2_header + ae_d2_patched + bytearray(data_section)

# Calculate offset shift for level/bitmap pointers into DATA
old_data_start = mc_data_sec['data_offset']
new_data_start = len(prefix) + len(new_d2_header) + len(ae_d2_patched) + 8  # +8 for DATA section header
shift = new_data_start - old_data_start
print(f'\nDATA offset shift: {shift} ({shift/(1024**2):.1f} MB)')

# Patch level data_offset values in-place within new_map's LEVELS section
levels_sec = mc_sec_map[SEC_LEVELS]
levels_buf = mc_data[levels_sec['data_offset']:levels_sec['data_offset'] + levels_sec['size']]
count = struct.unpack_from('<I', levels_buf, 0)[0]
assert count == total_levels

# Walk through level entries and find offset positions
idx = 4
for i in range(count):
    idx += 52  # ints_raw
    dbr_len = struct.unpack_from('<I', levels_buf, idx)[0]
    idx += 4 + dbr_len
    fname_len = struct.unpack_from('<I', levels_buf, idx)[0]
    idx += 4 + fname_len
    # data_offset is at this position
    offset_pos_in_levels = idx
    offset_pos_in_file = levels_sec['data_offset'] + offset_pos_in_levels
    old_off = struct.unpack_from('<I', new_map, offset_pos_in_file)[0]
    struct.pack_into('<I', new_map, offset_pos_in_file, old_off + shift)
    idx += 4  # data_offset
    idx += 4  # data_length

print(f'Patched {count} level offsets')

# Patch bitmap offsets
bmp_sec = mc_sec_map[SEC_BITMAPS]
bmp_base = bmp_sec['data_offset']
bmp_count = struct.unpack_from('<I', new_map, bmp_base)[0]
bmp_idx = bmp_base + 4
patched_bmps = 0
for i in range(bmp_count):
    if bmp_idx + 8 <= bmp_base + bmp_sec['size']:
        old_off = struct.unpack_from('<I', new_map, bmp_idx)[0]
        old_len = struct.unpack_from('<I', new_map, bmp_idx + 4)[0]
        if old_off > 0 and old_len > 0:
            struct.pack_into('<I', new_map, bmp_idx, old_off + shift)
            patched_bmps += 1
        bmp_idx += 8
print(f'Patched {patched_bmps} bitmap offsets')

# Verify
print('\nVerifying...')
result = bytes(new_map)
v_sections = parse_sections(result)
v_sec_map = {s['type']: s for s in v_sections}
v_levels = parse_level_index(result, v_sec_map[SEC_LEVELS])

bad_offsets = sum(1 for lv in v_levels if lv['data_offset'] + lv['data_length'] > len(result))
bad_magic = sum(1 for lv in v_levels if result[lv['data_offset']:lv['data_offset']+3] != b'LVL')
d2_count = struct.unpack_from('<I', result, v_sec_map[SEC_DATA2]['data_offset'] + 4)[0]
zero_ints = sum(1 for lv in v_levels if lv['ints_raw'] == b'\x00' * 52)

formats = {}
for lv in v_levels:
    ver = result[lv['data_offset'] + 3]
    formats[f'0x{ver:02x}'] = formats.get(f'0x{ver:02x}', 0) + 1

print(f'  Levels: {len(v_levels)}')
print(f'  Formats: {formats}')
print(f'  DATA2 count: {d2_count}')
print(f'  DATA2 size: {v_sec_map[SEC_DATA2]["size"]/(1024**2):.1f} MB')
print(f'  Bad offsets: {bad_offsets}')
print(f'  Bad magic: {bad_magic}')
print(f'  Zero ints_raw: {zero_ints}')
print(f'  drxmap refs: {result.count(b"drxmap")}')
print(f'  Size: {len(result)/(1024**2):.1f} MB, under 2GB: {len(result) < 2147483647}')

# Section layout
print('\nNew section layout:')
for s in v_sections:
    name = {0x01:'LEVELS',0x02:'DATA',0x10:'UNK10',0x11:'GROUPS',
            0x18:'SD',0x19:'BITMAPS',0x1A:'DATA2',0x1B:'QUESTS'}.get(s['type'],f'0x{s["type"]:02x}')
    end = s['data_offset'] + s['size']
    print(f'  {name}: [{s["header_offset"]}..{end})')

# Package
print(f'\nPackaging into ARC...')
arc = ArcArchive.from_file(svaera_arc_path)
arc.set_file('world/world01.map', result)
arc.write(output_arc)
print(f'  ARC: {output_arc.stat().st_size/(1024**2):.1f} MB')

del mc_data, ae_data, new_map, result
print('Done!')
