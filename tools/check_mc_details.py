#!/usr/bin/env python3
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

data = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_source\world01.map').read_bytes()
sections = parse_sections(data)
sec_map = {s['type']: s for s in sections}

# Check 0x10 section
for s in sections:
    if s['type'] == 0x10:
        d = data[s['data_offset']:s['data_offset'] + s['size']]
        print(f"Section 0x10: {s['size']} bytes")
        print(f"  Hex (first 64): {d[:64].hex()}")
        vals = struct.unpack_from('<10I', d)
        print(f"  First 10 ints: {vals}")

# Check ints_raw for shared drxmap levels
levels = parse_level_index(data, sec_map[SEC_LEVELS])
targets = ['delphilowlands04', 'delphilowlands02', 'delphilowlands03',
           'random09a', 'greecehiddenpath01', 'greecehiddenpath02',
           'megara01', 'greececave01b', 'delphilowlands01']

print("\n=== Shared drxmap level details ===")
for lv in levels:
    key = lv['fname'].lower().replace('\\', '/')
    for t in targets:
        if t in key:
            ver = data[lv['data_offset'] + 3]
            ints = struct.unpack_from('<13I', lv['ints_raw'])
            size = lv['data_length']
            print(f"  {lv['fname']}: ver=0x{ver:02x}, size={size}, ints4={ints[4]}")
            break

# Compare with SVAERA version counts
print("\n=== Loading SVAERA for comparison ===")
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sections = parse_sections(ae_data)
ae_sec_map = {s['type']: s for s in ae_sections}

print(f"SVAERA DATA2: {ae_sec_map[0x1A]['size']} bytes")
print(f"MC DATA2: {sec_map[0x1A]['size']} bytes")
print(f"SVAERA DATA: {ae_sec_map[0x02]['size']} bytes")
print(f"MC DATA: {sec_map[0x02]['size']} bytes")

# Check if 0x10 exists in SVAERA
for s in ae_sections:
    if s['type'] == 0x10:
        print(f"SVAERA has 0x10: {s['size']} bytes")
        break
else:
    print("SVAERA does NOT have section 0x10")

del data, ae_data
