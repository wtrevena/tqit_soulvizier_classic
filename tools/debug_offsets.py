#!/usr/bin/env python3
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_DATA, SEC_DATA2

arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sections = parse_sections(ae_data)
sec_map = {s['type']: s for s in sections}

data2_start = sec_map[SEC_DATA2]['data_offset']
data2_size = sec_map[SEC_DATA2]['size']
data_start = sec_map[SEC_DATA]['data_offset']
data_size = sec_map[SEC_DATA]['size']
print(f'DATA2: offset={data2_start} size={data2_size}')
print(f'DATA:  offset={data_start} size={data_size}')
print()

levels = parse_level_index(ae_data, sec_map[SEC_LEVELS])

for i in range(5):
    lv = levels[i]
    off = lv['data_offset']
    ln = lv['data_length']
    fname = lv['fname']

    magic_abs = ae_data[off:off+4].hex() if off + 4 <= len(ae_data) else 'OOB'

    in_data2 = data2_start <= off < data2_start + data2_size
    in_data = data_start <= off < data_start + data_size

    print(f'Level {i}: {fname}')
    print(f'  stored offset: {off}  length: {ln}')
    print(f'  in DATA2: {in_data2}  in DATA: {in_data}')
    print(f'  bytes at stored offset: {magic_abs}')

    # Try relative to DATA section
    if off < data_size:
        test_abs = data_start + off
        if test_abs + 4 <= len(ae_data):
            magic_rel = ae_data[test_abs:test_abs+4].hex()
            print(f'  bytes at DATA+offset: {magic_rel} (if offset is relative)')
    print()

del ae_data
