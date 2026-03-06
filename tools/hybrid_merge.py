#!/usr/bin/env python3
"""
Hybrid merge: combines MapCompiler's GROUPS/SD/BITMAPS (correct for all 2281 levels)
with full SV blob swap on shared levels that have drxmap content.

For shared levels with drxmap content: uses SV's complete blob + SV's ints_raw,
with bitmap entries zeroed so the engine uses SV's embedded pathfinding instead
of SVAERA's DATA2. This preserves SV's internally-consistent level data without
any cross-format conversion.
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    parse_bitmap_index, build_level_index, build_quests, build_bitmap_index,
    MAP_MAGIC, SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS)
from build_section_surgery import (
    INJECT_SPECS, inject_into_sv_only_blob, UBER_DUNGEON_QUEST_NAMES)

svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
mc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map')
out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

# Load SVAERA original
print('Loading SVAERA original...')
ae_arc = ArcArchive.from_file(svaera_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sections = parse_sections(ae_data)
ae_sec_map = {s['type']: s for s in ae_sections}
ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
ae_quests = parse_quests(ae_data, ae_sec_map[SEC_QUESTS])
ae_bitmaps = parse_bitmap_index(ae_data, ae_sec_map[SEC_BITMAPS])
bmp_unknown = struct.unpack_from('<I', ae_data, ae_sec_map[SEC_BITMAPS]['data_offset'])[0]

# Load SV original
print('Loading SV original...')
sv_arc = ArcArchive.from_file(sv_path)
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sections = parse_sections(sv_data)
sv_sec_map = {s['type']: s for s in sv_sections}
sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
sv_quests = parse_quests(sv_data, sv_sec_map[SEC_QUESTS])

# Load MapCompiler output (has correct GROUPS, SD, BITMAPS for all 2281 levels)
print('Loading MapCompiler merged output...')
mc_data = mc_path.read_bytes()
mc_sections = parse_sections(mc_data)
mc_sec_map = {s['type']: s for s in mc_sections}

print(f'  SVAERA: {len(ae_levels)} levels')
print(f'  SV: {len(sv_levels)} levels')
mc_levels = parse_level_index(mc_data, mc_sec_map[SEC_LEVELS])
print(f'  MapCompiler: {len(mc_levels)} levels')

# Identify SV-only and shared levels
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

print(f'  SV-only: {len(sv_only)}, shared+drxmap: {len(sv_custom_shared)}')

# Merge quests
ae_quest_set = set(q.lower() for q in ae_quests)
new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]
merged_quests = ae_quests + new_quests

# Add custom quests for Uber Dungeon portal wiring
existing_lower = set(q.lower() if isinstance(q, str) else q.decode('ascii', errors='replace').lower()
                     for q in merged_quests)
added_quests = 0
for qname in UBER_DUNGEON_QUEST_NAMES:
    if qname.lower() not in existing_lower:
        merged_quests.append(qname.encode('ascii'))
        existing_lower.add(qname.lower())
        added_quests += 1
print(f'  Quests: {len(ae_quests)} + {len(new_quests)} new + {added_quests} custom = {len(merged_quests)}')

# === Sections from MapCompiler (correct for all 2281 levels) ===
mc_groups = mc_data[mc_sec_map[SEC_GROUPS]['data_offset']:
                    mc_sec_map[SEC_GROUPS]['data_offset'] + mc_sec_map[SEC_GROUPS]['size']]
mc_sd = mc_data[mc_sec_map[SEC_SD]['data_offset']:
                mc_sec_map[SEC_SD]['data_offset'] + mc_sec_map[SEC_SD]['size']]
mc_bitmaps_raw = mc_data[mc_sec_map[SEC_BITMAPS]['data_offset']:
                         mc_sec_map[SEC_BITMAPS]['data_offset'] + mc_sec_map[SEC_BITMAPS]['size']]

# UNK section from SVAERA
ae_unk_sec = [s for s in ae_sections if s['type'] not in
              (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA)]
unk_sections = [(s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]) for s in ae_unk_sec]

# DATA2 from SVAERA (AE pathfinding)
data2_raw = ae_data[ae_sec_map[SEC_DATA2]['data_offset']:
                    ae_sec_map[SEC_DATA2]['data_offset'] + ae_sec_map[SEC_DATA2]['size']]

# DATA from SVAERA + appended SV blobs
data_raw = ae_data[ae_sec_map[SEC_DATA]['data_offset']:
                   ae_sec_map[SEC_DATA]['data_offset'] + ae_sec_map[SEC_DATA]['size']]

# === Full blob swap for shared levels with drxmap content ===
# Use SV's complete blob + SV's ints_raw for ALL shared+drxmap levels.
# This is the same approach that works for SV-only levels — no format conversion,
# no cross-section mismatches. Bitmap entries are zeroed so the engine uses
# SV's embedded pathfinding instead of SVAERA's DATA2.
print('\n=== Full blob swap for shared+drxmap levels ===')
shared_swap_levels = {}  # ae_idx -> (sv_blob, sv_lv)
for sv_lv, ae_idx in sv_custom_shared:
    ae_lv = ae_levels[ae_idx]
    sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]

    # Inject objects into shared levels if specified (e.g. uber dungeon portal)
    lv_key = ae_lv['fname'].replace('\\', '/').lower()
    if lv_key in INJECT_SPECS:
        from build_section_surgery import inject_into_sv_only_blob as _inject
        sv_blob = _inject(sv_blob, INJECT_SPECS[lv_key], ae_lv['fname'])

    ae_ver = ae_data[ae_lv['data_offset'] + 3] if ae_lv['data_length'] > 3 else 0
    sv_ver = sv_blob[3] if len(sv_blob) > 3 else 0
    shared_swap_levels[ae_idx] = (sv_blob, sv_lv)
    drx = sv_blob.count(b'drxmap')
    print(f'  SWAP: {ae_lv["fname"]} (AE=v0x{ae_ver:02x} -> SV=v0x{sv_ver:02x}, drxmap: {drx})')

# Collect blobs to append
append_blobs = []
sv_only_indices = []
shared_swap_indices = {}

for lv in sv_only:
    blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    # Inject objects into SV-only levels if specified
    lv_key = lv['fname'].replace('\\', '/').lower()
    if lv_key in INJECT_SPECS:
        blob = inject_into_sv_only_blob(blob, INJECT_SPECS[lv_key], lv['fname'])
    sv_only_indices.append(len(append_blobs))
    append_blobs.append(blob)

for ae_idx, (sv_blob, sv_lv) in shared_swap_levels.items():
    shared_swap_indices[ae_idx] = len(append_blobs)
    append_blobs.append(sv_blob)

total_append = sum(len(b) for b in append_blobs)

# Build LEVELS section with correct metadata from originals (deep copy!)
merged_levels = [dict(lv) for lv in ae_levels]
for lv in sv_only:
    merged_levels.append(dict(lv))

# Build quests
new_quests_data = build_quests(merged_quests)

# Build level index (preliminary, to get size)
prelim_levels_data = build_level_index(merged_levels)

# Calculate new section layout
# Order: header(8) + quests + groups + sd + levels + bitmaps + unk... + data2 + data
new_pre_data_size = 8
new_pre_data_size += 8 + len(new_quests_data)
new_pre_data_size += 8 + len(mc_groups)
new_pre_data_size += 8 + len(mc_sd)
new_pre_data_size += 8 + len(prelim_levels_data)
new_pre_data_size += 8 + len(mc_bitmaps_raw)
for _, ud in unk_sections:
    new_pre_data_size += 8 + len(ud)

orig_pre_data_size = ae_sec_map[SEC_DATA2]['data_offset'] - 8  # header_offset
offset_shift = new_pre_data_size - orig_pre_data_size
print(f'\n  Offset shift: {offset_shift} bytes')

# Calculate append start
append_start = new_pre_data_size + 8 + len(data2_raw) + 8 + len(data_raw)

# Fix level offsets
for i in range(len(ae_levels)):
    merged_levels[i]['data_offset'] = ae_levels[i]['data_offset'] + offset_shift

# Shared+drxmap levels: use SV's full blob + SV's ints_raw
for ae_idx, blob_idx in shared_swap_indices.items():
    blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
    sv_lv = shared_swap_levels[ae_idx][1]
    merged_levels[ae_idx]['data_offset'] = blob_offset
    merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])
    merged_levels[ae_idx]['ints_raw'] = sv_lv['ints_raw']

for i, sv_blob_idx in enumerate(sv_only_indices):
    lv_idx = len(ae_levels) + i
    blob_offset = append_start + sum(len(append_blobs[j]) for j in range(sv_blob_idx))
    merged_levels[lv_idx]['data_offset'] = blob_offset
    merged_levels[lv_idx]['data_length'] = len(append_blobs[sv_blob_idx])

# Rebuild LEVELS section
new_levels_data = build_level_index(merged_levels)

# Fix bitmap offsets in the MapCompiler bitmaps
# MapCompiler bitmaps have offsets for its own section layout - need to adjust
mc_bitmaps = parse_bitmap_index(mc_data, mc_sec_map[SEC_BITMAPS])
mc_bmp_unknown = struct.unpack_from('<I', mc_data, mc_sec_map[SEC_BITMAPS]['data_offset'])[0]

# MapCompiler's pre-data offset
mc_pre_data = mc_sec_map[SEC_DATA2]['data_offset'] - 8
mc_offset_shift = new_pre_data_size - mc_pre_data

# Adjust MC bitmap offsets: they point into MC's DATA2 section.
# We're using SVAERA's DATA2 section. MC's DATA2 and SVAERA's DATA2 should be identical
# (confirmed 0 diffs). So we just need to shift from MC layout to our layout.
adjusted_bitmaps = [dict(b) for b in mc_bitmaps]
for i in range(len(adjusted_bitmaps)):
    if adjusted_bitmaps[i]['offset'] > 0:
        adjusted_bitmaps[i]['offset'] = mc_bitmaps[i]['offset'] + mc_offset_shift

# Zero bitmap entries for ALL shared+drxmap levels.
# These levels use SV's full blob with embedded pathfinding.
# SVAERA's DATA2 pathfinding doesn't match SV's level layout,
# so we zero the bitmap entry to use SV's embedded pathfinding.
for ae_idx in shared_swap_levels:
    adjusted_bitmaps[ae_idx]['offset'] = 0
    adjusted_bitmaps[ae_idx]['length'] = 0
    print(f'  Zeroed bitmap for level {ae_idx} ({ae_levels[ae_idx]["fname"].split(chr(92))[-1]})')

new_bitmaps_data = build_bitmap_index(adjusted_bitmaps, mc_bmp_unknown)

# Verify bitmap section size matches
assert len(new_bitmaps_data) == len(mc_bitmaps_raw), \
    f'Bitmap size mismatch: {len(new_bitmaps_data)} vs {len(mc_bitmaps_raw)}'

# Recalculate with final bitmaps
final_pre_data = 8
final_pre_data += 8 + len(new_quests_data)
final_pre_data += 8 + len(mc_groups)
final_pre_data += 8 + len(mc_sd)
final_pre_data += 8 + len(new_levels_data)
final_pre_data += 8 + len(new_bitmaps_data)
for _, ud in unk_sections:
    final_pre_data += 8 + len(ud)
assert final_pre_data == new_pre_data_size, 'Pre-data size changed!'

# Write the hybrid map
print('Writing hybrid map...')
# header2 = total size of metadata sections (before DATA2), excluding 8-byte MAP header
header2 = new_pre_data_size - 8
print(f'  header2: {header2} (SVAERA was {struct.unpack_from("<I", ae_data, 4)[0]})')
out = bytearray()
out += struct.pack('<II', MAP_MAGIC, header2)
out += struct.pack('<II', SEC_QUESTS, len(new_quests_data)); out += new_quests_data
out += struct.pack('<II', SEC_GROUPS, len(mc_groups)); out += mc_groups
out += struct.pack('<II', SEC_SD, len(mc_sd)); out += mc_sd
out += struct.pack('<II', SEC_LEVELS, len(new_levels_data)); out += new_levels_data
out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data)); out += new_bitmaps_data
for utype, udata in unk_sections:
    out += struct.pack('<II', utype, len(udata)); out += udata
out += struct.pack('<II', SEC_DATA2, len(data2_raw)); out += data2_raw

extended_data_size = len(data_raw) + total_append
out += struct.pack('<II', SEC_DATA, extended_data_size)
out += data_raw
for blob in append_blobs:
    out += blob

result = bytes(out)
print(f'  Size: {len(result)} bytes ({len(result)/(1024**2):.1f} MB)')
print(f'  Under 2GB: {len(result) < 2147483647}')
print(f'  drxmap refs: {result.count(b"drxmap")}')

# Verify structure
test_sections = parse_sections(result)
last = test_sections[-1]
eof = last['data_offset'] + last['size']
print(f'  EOF check: expected={eof} actual={len(result)} ok={eof == len(result)}')

test_levels = parse_level_index(result, {s['type']: s for s in test_sections}[SEC_LEVELS])
bad = sum(1 for lv in test_levels if lv['data_offset'] + lv['data_length'] > len(result))
bad_magic = sum(1 for lv in test_levels if result[lv['data_offset']:lv['data_offset']+3] != b'LVL')
print(f'  Levels: {len(test_levels)}, bad offsets: {bad}, bad magic: {bad_magic}')

# Verify swapped levels
for ae_idx in shared_swap_levels:
    lv = test_levels[ae_idx]
    ver_byte = result[lv['data_offset'] + 3]
    drx = result[lv['data_offset']:lv['data_offset'] + lv['data_length']].count(b'drxmap')
    short = ae_levels[ae_idx]["fname"].split(chr(92))[-1]
    print(f'  Swapped {short}: v0x{ver_byte:02x}, drxmap: {drx}')

# Package into ARC
print('\nPackaging into ARC...')
ae_arc2 = ArcArchive.from_file(svaera_path)
ae_arc2.set_file('world/world01.map', result)
ae_arc2.write(out_arc_path)
print(f'  Written: {out_arc_path.stat().st_size / (1024**2):.1f} MB')

del ae_data, sv_data, mc_data, result
print('Done.')
