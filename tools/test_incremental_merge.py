#!/usr/bin/env python3
"""Incremental binary merge tests to isolate crash cause."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    parse_bitmap_index, build_level_index, build_quests, build_bitmap_index,
    MAP_MAGIC, SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS)

# Modes: quests_only, levels_only, full
mode = sys.argv[1] if len(sys.argv) > 1 else 'quests_only'
print(f"Mode: {mode}")

svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

print("Loading SVAERA...")
ae_arc = ArcArchive.from_file(svaera_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sections = parse_sections(ae_data)
ae_sec_map = {s['type']: s for s in ae_sections}
ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
ae_quests = parse_quests(ae_data, ae_sec_map[SEC_QUESTS])
ae_bitmaps = parse_bitmap_index(ae_data, ae_sec_map[SEC_BITMAPS])
bmp_raw = ae_data[ae_sec_map[SEC_BITMAPS]['data_offset']:ae_sec_map[SEC_BITMAPS]['data_offset'] + 4]
bmp_unknown = struct.unpack_from('<I', bmp_raw, 0)[0]

print("Loading SV...")
sv_arc = ArcArchive.from_file(sv_path)
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sections = parse_sections(sv_data)
sv_sec_map = {s['type']: s for s in sv_sections}
sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
sv_quests = parse_quests(sv_data, sv_sec_map[SEC_QUESTS])

# Identify SV content
ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i

sv_only = []
sv_custom_shared = []
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    if key not in ae_by_name:
        sv_only.append(lv)
    elif b'drxmap' in chunk:
        sv_custom_shared.append((lv, ae_by_name[key]))

ae_quest_set = set(q.lower() for q in ae_quests)
new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]

print(f"  SV-only levels: {len(sv_only)}, shared+drxmap: {len(sv_custom_shared)}, new quests: {len(new_quests)}")

# Decide what to include based on mode
add_quests = mode in ('quests_only', 'shared_only', 'levels_only', 'full')
add_sv_levels = mode in ('levels_only', 'full')
replace_shared = mode in ('shared_only', 'full')

merged_quests = ae_quests + (new_quests if add_quests else [])

# Build append blobs and merged levels
append_blobs = []
sv_only_indices = []
shared_replace_map = {}

merged_levels = [dict(lv) for lv in ae_levels]
merged_bitmaps = [dict(b) for b in ae_bitmaps]

if add_sv_levels:
    for lv in sv_only:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        sv_only_indices.append(len(append_blobs))
        append_blobs.append(blob)
        merged_levels.append(dict(lv))
        merged_bitmaps.append({'offset': 0, 'length': 0})

if replace_shared:
    for lv, ae_idx in sv_custom_shared:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        shared_replace_map[ae_idx] = len(append_blobs)
        append_blobs.append(blob)

total_append = sum(len(b) for b in append_blobs)
print(f"  Append blobs: {len(append_blobs)} ({total_append / (1024**2):.1f} MB)")
print(f"  Merged levels: {len(merged_levels)}, bitmaps: {len(merged_bitmaps)}")

# Build sections
new_quests_data = build_quests(merged_quests)
new_levels_data = build_level_index(merged_levels)
new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

groups_data = ae_data[ae_sec_map[SEC_GROUPS]['data_offset']:ae_sec_map[SEC_GROUPS]['data_offset'] + ae_sec_map[SEC_GROUPS]['size']]
sd_data = ae_data[ae_sec_map[SEC_SD]['data_offset']:ae_sec_map[SEC_SD]['data_offset'] + ae_sec_map[SEC_SD]['size']]

unknown_sec = [s for s in ae_sections if s['type'] not in (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA)]
unknown_sections_data = [(s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]) for s in unknown_sec]

data2_raw = ae_data[ae_sec_map[SEC_DATA2]['data_offset']:ae_sec_map[SEC_DATA2]['data_offset'] + ae_sec_map[SEC_DATA2]['size']]
data_raw = ae_data[ae_sec_map[SEC_DATA]['data_offset']:ae_sec_map[SEC_DATA]['data_offset'] + ae_sec_map[SEC_DATA]['size']]

# Calculate offset shift
orig_pre_data_size = ae_sec_map[SEC_DATA2]['header_offset']
new_pre_data_size = 8
new_pre_data_size += 8 + len(new_quests_data)
new_pre_data_size += 8 + len(groups_data)
new_pre_data_size += 8 + len(sd_data)
new_pre_data_size += 8 + len(new_levels_data)
new_pre_data_size += 8 + len(new_bitmaps_data)
for _, ud in unknown_sections_data:
    new_pre_data_size += 8 + len(ud)

offset_shift = new_pre_data_size - orig_pre_data_size
print(f"  Offset shift: {offset_shift} bytes")

# Calculate append start
append_start = new_pre_data_size + 8 + len(data2_raw) + 8 + len(data_raw)

# Fix level offsets
for i in range(len(ae_levels)):
    merged_levels[i]['data_offset'] = ae_levels[i]['data_offset'] + offset_shift

if replace_shared:
    for ae_idx, blob_idx in shared_replace_map.items():
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
        merged_levels[ae_idx]['data_offset'] = blob_offset
        merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])

if add_sv_levels:
    for i, sv_blob_idx in enumerate(sv_only_indices):
        lv_idx = len(ae_levels) + i
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(sv_blob_idx))
        merged_levels[lv_idx]['data_offset'] = blob_offset
        merged_levels[lv_idx]['data_length'] = len(append_blobs[sv_blob_idx])

# Fix bitmap offsets
for i in range(len(ae_bitmaps)):
    if merged_bitmaps[i]['offset'] > 0:
        merged_bitmaps[i]['offset'] = ae_bitmaps[i]['offset'] + offset_shift

# Rebuild
new_levels_data = build_level_index(merged_levels)
new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

# Write merged map
header2 = new_pre_data_size - 8
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

extended_data_size = len(data_raw) + total_append
out += struct.pack('<II', SEC_DATA, extended_data_size)
out += data_raw
for blob in append_blobs:
    out += blob

map_result = bytes(out)
print(f"\n  Map size: {len(map_result)} bytes ({len(map_result) / (1024**2):.1f} MB)")
print(f"  Under 2GB: {len(map_result) < 2147483647}")
print(f"  drxmap refs: {map_result.count(b'drxmap')}")

# Verify level offsets
test_sections = parse_sections(map_result)
test_sec_map = {s['type']: s for s in test_sections}
test_levels = parse_level_index(map_result, test_sec_map[SEC_LEVELS])
bad = 0
for i, lv in enumerate(test_levels):
    if lv['data_offset'] + lv['data_length'] > len(map_result):
        bad += 1
print(f"  Bad level offsets: {bad}/{len(test_levels)}")

# Verify first SVAERA level data unchanged
orig_first = ae_data[ae_levels[0]['data_offset']:ae_levels[0]['data_offset'] + 4]
new_first = map_result[merged_levels[0]['data_offset']:merged_levels[0]['data_offset'] + 4]
print(f"  First level data: orig={orig_first.hex()} new={new_first.hex()} {'OK' if orig_first == new_first else 'MISMATCH!'}")

# Package into ARC
print("\nPackaging into ARC...")
ae_arc2 = ArcArchive.from_file(svaera_path)
ae_arc2.set_file('world/world01.map', map_result)
ae_arc2.write(out_arc_path)
print(f"  Written: {out_arc_path.stat().st_size / (1024**2):.1f} MB")

del ae_data, sv_data, map_result
print("Done.")
