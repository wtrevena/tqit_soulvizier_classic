#!/usr/bin/env python3
"""Test that rebuilding SVAERA map with no changes produces identical output."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    parse_bitmap_index, build_level_index, build_quests, build_bitmap_index,
    MAP_MAGIC, SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS)

arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])

ae_sections = parse_sections(ae_data)
ae_sec_map = {s['type']: s for s in ae_sections}

ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
ae_quests = parse_quests(ae_data, ae_sec_map[SEC_QUESTS])
ae_bitmaps = parse_bitmap_index(ae_data, ae_sec_map[SEC_BITMAPS])
bmp_raw = ae_data[ae_sec_map[SEC_BITMAPS]['data_offset']:ae_sec_map[SEC_BITMAPS]['data_offset'] + 4]
bmp_unknown = struct.unpack_from('<I', bmp_raw, 0)[0]

new_quests_data = build_quests(ae_quests)
new_levels_data = build_level_index(ae_levels)
new_bitmaps_data = build_bitmap_index(ae_bitmaps, bmp_unknown)

groups_data = ae_data[ae_sec_map[SEC_GROUPS]['data_offset']:ae_sec_map[SEC_GROUPS]['data_offset'] + ae_sec_map[SEC_GROUPS]['size']]
sd_data = ae_data[ae_sec_map[SEC_SD]['data_offset']:ae_sec_map[SEC_SD]['data_offset'] + ae_sec_map[SEC_SD]['size']]

unknown_sec = [s for s in ae_sections if s['type'] not in (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA)]
unknown_sections_data = [(s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]) for s in unknown_sec]

data2_raw = ae_data[ae_sec_map[SEC_DATA2]['data_offset']:ae_sec_map[SEC_DATA2]['data_offset'] + ae_sec_map[SEC_DATA2]['size']]
data_raw = ae_data[ae_sec_map[SEC_DATA]['data_offset']:ae_sec_map[SEC_DATA]['data_offset'] + ae_sec_map[SEC_DATA]['size']]

header2 = struct.unpack_from('<I', ae_data, 4)[0]

out = bytearray()
out += struct.pack('<II', MAP_MAGIC, header2)
out += struct.pack('<II', SEC_QUESTS, len(new_quests_data)); out += new_quests_data
out += struct.pack('<II', SEC_GROUPS, len(groups_data)); out += groups_data
out += struct.pack('<II', SEC_SD, len(sd_data)); out += sd_data
out += struct.pack('<II', SEC_LEVELS, len(new_levels_data)); out += new_levels_data
out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data)); out += new_bitmaps_data
for utype, udata in unknown_sections_data:
    out += struct.pack('<II', utype, len(udata)); out += udata
out += struct.pack('<II', SEC_DATA2, len(data2_raw)); out += data2_raw
out += struct.pack('<II', SEC_DATA, len(data_raw)); out += data_raw

result = bytes(out)

if result == ae_data:
    print('IDENTITY REBUILD: BYTE IDENTICAL')
else:
    print(f'NOT IDENTICAL! orig={len(ae_data)} rebuilt={len(result)}')
    diff_count = 0
    for i in range(min(len(ae_data), len(result))):
        if ae_data[i] != result[i]:
            if diff_count < 5:
                sec_label = "?"
                for s in ae_sections:
                    if s['data_offset'] <= i < s['data_offset'] + s['size']:
                        sec_label = {0x01:'LEVELS',0x02:'DATA',0x1A:'DATA2',0x1B:'QUESTS',
                                     0x11:'GROUPS',0x19:'BITMAPS',0x18:'SD',0x10:'UNK'}.get(s['type'], hex(s['type']))
                print(f'  Diff at byte {i} (section {sec_label}): orig=0x{ae_data[i]:02X} new=0x{result[i]:02X}')
            diff_count += 1
    print(f'  Total diffs: {diff_count}')

del ae_data, result
