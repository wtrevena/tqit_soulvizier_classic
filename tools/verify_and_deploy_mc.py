#!/usr/bin/env python3
"""Verify the new MapCompiler output and package for deployment."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_bitmap_index,
    SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_GROUPS, SEC_SD, SEC_BITMAPS, SEC_QUESTS)

mc_map = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_source\world01.map')
svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
out_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

print('Loading compiled map...')
data = mc_map.read_bytes()
sections = parse_sections(data)
sec_map = {s['type']: s for s in sections}

print(f'  Size: {len(data)} bytes ({len(data)/(1024**2):.1f} MB)')
print(f'  Under 2GB: {len(data) < 2147483647}')

# Check sections
print(f'\n=== Sections ===')
for s in sections:
    name = {0x01: 'LEVELS', 0x02: 'DATA', 0x11: 'GROUPS', 0x18: 'SD',
            0x19: 'BITMAPS', 0x1A: 'DATA2', 0x1B: 'QUESTS'}.get(s['type'], f'UNK-{s["type"]:#x}')
    print(f'  {name}: offset={s["header_offset"]}, size={s["size"]}')

# Check levels
levels = parse_level_index(data, sec_map[SEC_LEVELS])
print(f'\n=== LEVELS ===')
print(f'  Count: {len(levels)}')

# Check format versions
formats = {}
for lv in levels:
    blob = data[lv['data_offset']:lv['data_offset'] + 4]
    if blob[:3] == b'LVL':
        ver = blob[3]
        formats[ver] = formats.get(ver, 0) + 1
    else:
        formats['unknown'] = formats.get('unknown', 0) + 1
print(f'  LVL formats: { {(f"0x{k:02x}" if isinstance(k,int) else k): v for k, v in formats.items()} }')

# Check ints_raw (should NOT be all zeros now)
zero_ints = sum(1 for lv in levels if lv['ints_raw'] == b'\x00' * 52)
print(f'  Zero ints_raw: {zero_ints}')

# Check data integrity
bad_offsets = sum(1 for lv in levels if lv['data_offset'] + lv['data_length'] > len(data))
bad_magic = sum(1 for lv in levels if data[lv['data_offset']:lv['data_offset']+3] != b'LVL')
print(f'  Bad offsets: {bad_offsets}')
print(f'  Bad magic: {bad_magic}')

# Check DATA2
d2_count = struct.unpack_from('<I', data, sec_map[SEC_DATA2]['data_offset'] + 4)[0]
print(f'\n=== DATA2 ===')
print(f'  Level count: {d2_count} (should be {len(levels)})')
print(f'  Size: {sec_map[SEC_DATA2]["size"]} bytes ({sec_map[SEC_DATA2]["size"]/(1024**2):.1f} MB)')

# Check drxmap references
drxmap_count = data.count(b'drxmap')
print(f'\n  drxmap references: {drxmap_count}')

# EOF check
last = sections[-1]
eof = last['data_offset'] + last['size']
print(f'  EOF: expected={eof}, actual={len(data)}, ok={eof == len(data)}')

# Package into ARC
print(f'\nPackaging into ARC...')
arc = ArcArchive.from_file(svaera_arc_path)
arc.set_file('world/world01.map', data)
arc.write(out_arc)
print(f'  ARC: {out_arc.stat().st_size / (1024**2):.1f} MB')

del data
print('Done!')
