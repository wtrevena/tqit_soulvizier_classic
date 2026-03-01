#!/usr/bin/env python3
"""
Fix MapCompiler output by restoring correct ints_raw metadata.

The MC compiled all 2281 levels together (correct DATA2, borders, etc.)
but zeroed out all level metadata (ints_raw). This script restores
ints_raw from the original sources (SVAERA for existing levels, SV for new ones).
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    parse_bitmap_index, build_level_index, MAP_MAGIC,
    SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS)

svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
mc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map')
out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

# Load all three maps
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(svaera_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])

print('Loading SV...')
sv_arc = ArcArchive.from_file(sv_path)
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])

print('Loading MC output...')
mc_data = mc_path.read_bytes()
mc_sections = parse_sections(mc_data)
mc_sec = {s['type']: s for s in mc_sections}
mc_levels = parse_level_index(mc_data, mc_sec[SEC_LEVELS])

print(f'  SVAERA: {len(ae_levels)} levels')
print(f'  SV: {len(sv_levels)} levels')
print(f'  MC: {len(mc_levels)} levels')

# Build name lookups
ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i

sv_by_name = {}
for i, lv in enumerate(sv_levels):
    sv_by_name[lv['fname'].replace('\\', '/').lower()] = i

# Check MC level blob formats to determine which ints_raw to use
print('\n=== Checking MC level blob formats ===')
format_counts = {}
for lv in mc_levels[:20]:
    blob_start = mc_data[lv['data_offset']:lv['data_offset'] + 4]
    if blob_start[:3] == b'LVL':
        ver = blob_start[3]
        format_counts[ver] = format_counts.get(ver, 0) + 1

# Check all levels
all_format_counts = {}
for lv in mc_levels:
    blob_start = mc_data[lv['data_offset']:lv['data_offset'] + 4]
    if blob_start[:3] == b'LVL':
        ver = blob_start[3]
        all_format_counts[ver] = all_format_counts.get(ver, 0) + 1
    else:
        all_format_counts['unknown'] = all_format_counts.get('unknown', 0) + 1

print(f'  MC level blob formats: { {(f"0x{k:02x}" if isinstance(k,int) else k): v for k, v in all_format_counts.items()} }')

# For each MC level, find matching source and determine correct ints_raw
print('\n=== Restoring ints_raw ===')
fixed_levels = [dict(lv) for lv in mc_levels]
matched_ae = 0
matched_sv = 0
unmatched = 0

for i, mc_lv in enumerate(mc_levels):
    mc_key = mc_lv['fname'].replace('\\', '/').lower()
    mc_blob_ver = mc_data[mc_lv['data_offset'] + 3] if mc_data[mc_lv['data_offset']:mc_lv['data_offset']+3] == b'LVL' else None
    
    if mc_key in ae_by_name:
        ae_idx = ae_by_name[mc_key]
        ae_lv = ae_levels[ae_idx]
        ae_blob_ver = ae_data[ae_lv['data_offset'] + 3] if ae_data[ae_lv['data_offset']:ae_lv['data_offset']+3] == b'LVL' else None
        
        if mc_blob_ver == ae_blob_ver:
            # Same format, use SVAERA ints_raw directly
            fixed_levels[i]['ints_raw'] = ae_lv['ints_raw']
            matched_ae += 1
        elif mc_blob_ver is not None and ae_blob_ver is not None:
            # Format changed (e.g., MC has 0x0e but SVAERA has 0x11)
            # Use SVAERA's ints_raw but adjust int[4] if needed
            if mc_key in sv_by_name:
                sv_idx = sv_by_name[mc_key]
                sv_lv = sv_levels[sv_idx]
                sv_blob_ver = sv_data[sv_lv['data_offset'] + 3]
                if mc_blob_ver == sv_blob_ver:
                    # MC blob matches SV format, use SV ints_raw
                    fixed_levels[i]['ints_raw'] = sv_lv['ints_raw']
                    matched_sv += 1
                else:
                    # Neither matches perfectly, use SVAERA's
                    fixed_levels[i]['ints_raw'] = ae_lv['ints_raw']
                    matched_ae += 1
            else:
                fixed_levels[i]['ints_raw'] = ae_lv['ints_raw']
                matched_ae += 1
        else:
            fixed_levels[i]['ints_raw'] = ae_lv['ints_raw']
            matched_ae += 1
    elif mc_key in sv_by_name:
        sv_idx = sv_by_name[mc_key]
        sv_lv = sv_levels[sv_idx]
        fixed_levels[i]['ints_raw'] = sv_lv['ints_raw']
        matched_sv += 1
    else:
        unmatched += 1
        if unmatched <= 5:
            print(f'  WARNING: No match for level {i}: {mc_lv["fname"]}')

print(f'  Matched to SVAERA: {matched_ae}')
print(f'  Matched to SV: {matched_sv}')
print(f'  Unmatched: {unmatched}')

# Verify ints_raw was actually restored (not all zeros)
zero_count = sum(1 for lv in fixed_levels if lv['ints_raw'] == b'\x00' * 52)
print(f'  Levels still with zero ints_raw: {zero_count}')

# Rebuild the LEVELS section with fixed ints_raw
new_levels_data = build_level_index(fixed_levels)
old_levels_sec = mc_sec[SEC_LEVELS]

print(f'\n=== Rebuilding MC output ===')
print(f'  Old LEVELS section: {old_levels_sec["size"]} bytes')
print(f'  New LEVELS section: {len(new_levels_data)} bytes')

# The section sizes should be identical since we only changed ints_raw content
if len(new_levels_data) == old_levels_sec['size']:
    print('  Section size MATCH - can do in-place replacement!')
    result = bytearray(mc_data)
    result[old_levels_sec['data_offset']:old_levels_sec['data_offset'] + old_levels_sec['size']] = new_levels_data
    result = bytes(result)
else:
    print('  Section size MISMATCH - need full rebuild')
    # Full rebuild preserving all MC sections except LEVELS
    out = bytearray()
    header2 = struct.unpack_from('<I', mc_data, 4)[0]
    out += struct.pack('<II', MAP_MAGIC, header2)
    
    for sec in mc_sections:
        if sec['type'] == SEC_LEVELS:
            out += struct.pack('<II', SEC_LEVELS, len(new_levels_data))
            out += new_levels_data
        else:
            sec_data = mc_data[sec['data_offset']:sec['data_offset'] + sec['size']]
            out += struct.pack('<II', sec['type'], sec['size'])
            out += sec_data
    result = bytes(out)

print(f'  Output size: {len(result)} bytes ({len(result)/(1024**2):.1f} MB)')
print(f'  Under 2GB: {len(result) < 2147483647}')
print(f'  drxmap refs: {result.count(b"drxmap")}')

# Verify structure
test_sections = parse_sections(result)
test_sec = {s['type']: s for s in test_sections}
test_levels = parse_level_index(result, test_sec[SEC_LEVELS])
bad_offsets = sum(1 for lv in test_levels if lv['data_offset'] + lv['data_length'] > len(result))
bad_magic = sum(1 for lv in test_levels if result[lv['data_offset']:lv['data_offset']+3] != b'LVL')
zero_ints = sum(1 for lv in test_levels if lv['ints_raw'] == b'\x00' * 52)
print(f'  Levels: {len(test_levels)}, bad offsets: {bad_offsets}, bad magic: {bad_magic}, zero ints: {zero_ints}')

# Check DATA2 count
d2_count = struct.unpack_from('<I', result, test_sec[SEC_DATA2]['data_offset'] + 4)[0]
print(f'  DATA2 level count: {d2_count} (should be {len(test_levels)})')

# Package into ARC
print('\nPackaging into ARC...')
ae_arc2 = ArcArchive.from_file(svaera_path)
ae_arc2.set_file('world/world01.map', result)
ae_arc2.write(out_arc_path)
print(f'  ARC size: {out_arc_path.stat().st_size / (1024**2):.1f} MB')

del ae_data, sv_data, mc_data, result
print('Done!')
