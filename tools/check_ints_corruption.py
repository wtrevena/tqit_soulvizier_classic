#!/usr/bin/env python3
"""Check if ints_raw float conversion corrupted values."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

# Load SVAERA
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_levels = parse_level_index(ae_data, {s['type']:s for s in parse_sections(ae_data)}[SEC_LEVELS])

# Load MC
mc_data = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_source\world01.map').read_bytes()
mc_levels = parse_level_index(mc_data, {s['type']:s for s in parse_sections(mc_data)}[SEC_LEVELS])

# Compare ints_raw for SVAERA levels
ae_by_name = {lv['fname'].lower(): lv for lv in ae_levels}
mc_by_name = {lv['fname'].lower(): lv for lv in mc_levels}

diffs = []
for key, ae_lv in ae_by_name.items():
    if key in mc_by_name:
        mc_lv = mc_by_name[key]
        if ae_lv['ints_raw'] != mc_lv['ints_raw']:
            ae_vals = struct.unpack_from('<13I', ae_lv['ints_raw'])
            mc_vals = struct.unpack_from('<13I', mc_lv['ints_raw'])
            diffs.append((key, ae_vals, mc_vals))

print(f'Total levels with different ints_raw: {len(diffs)}')
print(f'\nFirst 20 differences (showing all 13 fields):')
for key, ae_vals, mc_vals in diffs[:20]:
    print(f'\n  {key}:')
    for i in range(13):
        if ae_vals[i] != mc_vals[i]:
            # Check if MC value looks like a float representation of the AE int
            ae_as_float = struct.pack('<f', float(ae_vals[i]))
            ae_round_trip = struct.unpack('<I', ae_as_float)[0]
            is_float_corruption = (mc_vals[i] == ae_round_trip)
            marker = ' <-- FLOAT CORRUPTION!' if is_float_corruption else ''
            print(f'    [{i}] SVAERA={ae_vals[i]:10d} (0x{ae_vals[i]:08x})  MC={mc_vals[i]:10d} (0x{mc_vals[i]:08x}){marker}')

# Check if ALL differences are from float conversion
float_corrupted = 0
other_diff = 0
for key, ae_vals, mc_vals in diffs:
    for i in range(13):
        if ae_vals[i] != mc_vals[i]:
            ae_as_float = struct.pack('<f', float(ae_vals[i]))
            ae_round_trip = struct.unpack('<I', ae_as_float)[0]
            if mc_vals[i] == ae_round_trip:
                float_corrupted += 1
            else:
                other_diff += 1

print(f'\n\n=== Summary ===')
print(f'  Fields with float-conversion corruption: {float_corrupted}')
print(f'  Fields with other differences: {other_diff}')

del ae_data, mc_data
