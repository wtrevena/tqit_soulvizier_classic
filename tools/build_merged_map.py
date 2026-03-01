#!/usr/bin/env python3
"""
Build merged map with DATA2 count fix.
Uses merge_levels_binary for the core merge, then packages into ARC.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

svaera_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
output_map = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_binary.map')
output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

# Run the binary merge
sys.argv = [sys.argv[0], str(svaera_arc), str(sv_arc), str(output_map)]
from merge_levels_binary import main as merge_main
merge_main()

# Verify the output
import struct
data = output_map.read_bytes()
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_DATA2

sections = parse_sections(data)
sec_map = {s['type']: s for s in sections}

# Verify DATA2 count
d2_count = struct.unpack_from('<I', data, sec_map[SEC_DATA2]['data_offset'] + 4)[0]
levels = parse_level_index(data, sec_map[SEC_LEVELS])
print(f'\nVerification:')
print(f'  LEVELS count: {len(levels)}')
print(f'  DATA2 count:  {d2_count}')
print(f'  Match: {len(levels) == d2_count}')
print(f'  drxmap refs: {data.count(b"drxmap")}')
print(f'  Size: {len(data)/(1024**2):.1f} MB, under 2GB: {len(data) < 2147483647}')

# Check level data integrity
bad_offsets = sum(1 for lv in levels if lv['data_offset'] + lv['data_length'] > len(data))
bad_magic = sum(1 for lv in levels if data[lv['data_offset']:lv['data_offset']+3] != b'LVL')
print(f'  Bad offsets: {bad_offsets}, bad magic: {bad_magic}')

# Package into ARC
print(f'\nPackaging into ARC...')
from arc_patcher import ArcArchive
arc = ArcArchive.from_file(svaera_arc)
arc.set_file('world/world01.map', data)
arc.write(output_arc)
print(f'  ARC size: {output_arc.stat().st_size / (1024**2):.1f} MB')
print('Done!')

del data
