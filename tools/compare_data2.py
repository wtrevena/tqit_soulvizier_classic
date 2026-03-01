#!/usr/bin/env python3
"""Compare DATA2 sections between SVAERA and MC to understand pathfinding differences."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, SEC_DATA2

print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_d2 = ae_data[ae_sec[SEC_DATA2]['data_offset']:ae_sec[SEC_DATA2]['data_offset']+ae_sec[SEC_DATA2]['size']]

print('Loading MC...')
mc_data = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map').read_bytes()
mc_sec = {s['type']: s for s in parse_sections(mc_data)}
mc_d2 = mc_data[mc_sec[SEC_DATA2]['data_offset']:mc_sec[SEC_DATA2]['data_offset']+mc_sec[SEC_DATA2]['size']]

print(f'SVAERA DATA2: {len(ae_d2)} bytes')
print(f'MC DATA2:     {len(mc_d2)} bytes')
print(f'Same size: {len(ae_d2) == len(mc_d2)}')

# Count byte differences
diff_count = 0
diff_regions = []
in_diff = False
diff_start = 0
for i in range(len(ae_d2)):
    if ae_d2[i] != mc_d2[i]:
        diff_count += 1
        if not in_diff:
            in_diff = True
            diff_start = i
    else:
        if in_diff:
            in_diff = False
            diff_regions.append((diff_start, i))
if in_diff:
    diff_regions.append((diff_start, len(ae_d2)))

print(f'Different bytes: {diff_count} out of {len(ae_d2)} ({diff_count*100/len(ae_d2):.4f}%)')
print(f'Diff regions: {len(diff_regions)}')
for r_start, r_end in diff_regions[:20]:
    print(f'  offset {r_start}-{r_end} ({r_end-r_start} bytes)')
    if r_end - r_start <= 32:
        print(f'    AE: {ae_d2[r_start:r_end].hex()}')
        print(f'    MC: {mc_d2[r_start:r_end].hex()}')
if len(diff_regions) > 20:
    print(f'  ... and {len(diff_regions)-20} more regions')

# Check first 100 bytes (header)
print(f'\nDATA2 header (first 32 bytes):')
print(f'  AE: {ae_d2[:32].hex()}')
print(f'  MC: {mc_d2[:32].hex()}')

del ae_data, mc_data
