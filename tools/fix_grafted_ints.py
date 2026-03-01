#!/usr/bin/env python3
"""
Fix ints_raw corruption in the grafted MC+DATA2 map.

The MC compilation corrupted field[1] for 516 levels due to
int→float→int round-trip loss. Fix by restoring SVAERA's ints_raw
for matching levels and SV's for SV-only levels.
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')
svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')

# Load the grafted map from ARC
print('Loading grafted map...')
our_arc = ArcArchive.from_file(output_arc)
our_data = bytearray(our_arc.decompress([e for e in our_arc.entries if e.entry_type == 3][0]))
our_secs = parse_sections(our_data)
our_sec_map = {s['type']: s for s in our_secs}
our_levels = parse_level_index(bytes(our_data), our_sec_map[SEC_LEVELS])
print(f'  {len(our_levels)} levels')

# Load SVAERA for correct ints_raw
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(svaera_arc_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_levels = parse_level_index(ae_data, {s['type']:s for s in parse_sections(ae_data)}[SEC_LEVELS])
ae_by_name = {lv['fname'].replace('\\','/').lower(): lv for lv in ae_levels}
del ae_data

# Load SV for SV-only levels
print('Loading SV...')
sv_arc_obj = ArcArchive.from_file(sv_arc_path)
sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
sv_levels = parse_level_index(sv_data, {s['type']:s for s in parse_sections(sv_data)}[SEC_LEVELS])
sv_by_name = {lv['fname'].replace('\\','/').lower(): lv for lv in sv_levels}
del sv_data

# Walk through the LEVELS section and patch ints_raw in-place
levels_sec = our_sec_map[SEC_LEVELS]
base = levels_sec['data_offset']
idx = base + 4  # skip count

fixed_from_ae = 0
fixed_from_sv = 0
already_ok = 0
unmatched = 0

for i, lv in enumerate(our_levels):
    key = lv['fname'].replace('\\', '/').lower()
    ints_pos = idx  # ints_raw starts here
    
    if key in ae_by_name:
        correct_ints = ae_by_name[key]['ints_raw']
        if our_data[ints_pos:ints_pos + 52] != correct_ints:
            our_data[ints_pos:ints_pos + 52] = correct_ints
            fixed_from_ae += 1
        else:
            already_ok += 1
    elif key in sv_by_name:
        correct_ints = sv_by_name[key]['ints_raw']
        if our_data[ints_pos:ints_pos + 52] != correct_ints:
            our_data[ints_pos:ints_pos + 52] = correct_ints
            fixed_from_sv += 1
        else:
            already_ok += 1
    else:
        unmatched += 1
        if unmatched <= 3:
            print(f'  WARNING: No match for {lv["fname"]}')
    
    # Advance through the level entry
    idx += 52  # ints_raw
    dbr_len = struct.unpack_from('<I', our_data, idx)[0]
    idx += 4 + dbr_len
    fname_len = struct.unpack_from('<I', our_data, idx)[0]
    idx += 4 + fname_len
    idx += 8  # data_offset + data_length

print(f'\n  Fixed from SVAERA: {fixed_from_ae}')
print(f'  Fixed from SV: {fixed_from_sv}')
print(f'  Already correct: {already_ok}')
print(f'  Unmatched: {unmatched}')

# Verify
result = bytes(our_data)
v_levels = parse_level_index(result, our_sec_map[SEC_LEVELS])
bad_offsets = sum(1 for lv in v_levels if lv['data_offset'] + lv['data_length'] > len(result))
bad_magic = sum(1 for lv in v_levels if result[lv['data_offset']:lv['data_offset']+3] != b'LVL')

# Verify ints_raw restored
still_bad = 0
for lv in v_levels:
    key = lv['fname'].replace('\\','/').lower()
    if key in ae_by_name:
        if lv['ints_raw'] != ae_by_name[key]['ints_raw']:
            still_bad += 1
    elif key in sv_by_name:
        if lv['ints_raw'] != sv_by_name[key]['ints_raw']:
            still_bad += 1

print(f'\n  Verification:')
print(f'  Bad offsets: {bad_offsets}')
print(f'  Bad magic: {bad_magic}')
print(f'  Still mismatched ints_raw: {still_bad}')
print(f'  Size: {len(result)/(1024**2):.1f} MB')

# Write back to ARC
print(f'\nPackaging...')
arc = ArcArchive.from_file(svaera_arc_path)
arc.set_file('world/world01.map', result)
arc.write(output_arc)
print(f'  ARC: {output_arc.stat().st_size/(1024**2):.1f} MB')
print('Done!')
