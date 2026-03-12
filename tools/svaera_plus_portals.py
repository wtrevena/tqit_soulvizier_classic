#!/usr/bin/env python3
"""
Build merged Levels.arc: SVAERA clean base + SV-only levels + portal NPCs.

Strategy: Keep SVAERA's map untouched (no invisible wall), add SV's custom
levels (UberDungeon, xBloodCave, BossArena, Secret_Place) as disconnected
areas, and inject portal NPCs to connect them.

No shared+drxmap level replacements — those caused the invisible wall.
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    parse_bitmap_index, build_level_index, build_quests, build_bitmap_index,
    MAP_MAGIC, SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS)
from build_section_surgery import (
    INJECT_SPECS, ALL_CUSTOM_QUEST_NAMES, inject_into_0x05_v11,
    parse_blob_sections, rebuild_blob, convert_v0e_blob_to_v11,
    inject_into_sv_only_blob, inject_rec02_into_blob)

# --- GROUPS parsing ---
def _find_next_groups_record(data, start, end_limit):
    for scan in range(start, min(end_limit, len(data) - 12)):
        sub = struct.unpack_from('<I', data, scan)[0]
        if sub > 20: continue
        slen = struct.unpack_from('<I', data, scan + 4)[0]
        if slen < 3 or slen > 200 or scan + 8 + slen > len(data): continue
        s = data[scan+8:scan+8+slen]
        if not all(32 <= b < 127 for b in s): continue
        pos2 = scan + 8 + slen
        if pos2 + 4 > len(data): continue
        slen2 = struct.unpack_from('<I', data, pos2)[0]
        if slen2 < 3 or slen2 > 200 or pos2 + 4 + slen2 > len(data): continue
        s2 = data[pos2+4:pos2+4+slen2]
        if all(32 <= b < 127 for b in s2): return scan
    return None

def _parse_groups(data):
    val0, count = struct.unpack_from('<II', data, 0)
    pos = 8
    records = []
    for i in range(count):
        sub_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        name_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
        name = data[pos:pos+name_len].decode('ascii', errors='replace'); pos += name_len
        cat_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
        category = data[pos:pos+cat_len].decode('ascii', errors='replace'); pos += cat_len
        member_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        data_start = pos
        if i < count - 1:
            nxt = _find_next_groups_record(data, pos, pos + 200000)
            data_len = (nxt - pos) if nxt else (len(data) - pos)
        else:
            data_len = len(data) - pos
        records.append({'sub_count': sub_count, 'name': name, 'category': category,
                        'member_count': member_count, 'raw_data': data[data_start:data_start+data_len]})
        pos = data_start + data_len
    return val0, records

def _rebuild_groups(val0, records):
    out = bytearray(struct.pack('<II', val0, len(records)))
    for rec in records:
        name_b = rec['name'].encode('ascii')
        cat_b = rec['category'].encode('ascii')
        out += struct.pack('<I', rec['sub_count'])
        out += struct.pack('<I', len(name_b)) + name_b
        out += struct.pack('<I', len(cat_b)) + cat_b
        out += struct.pack('<I', rec['member_count'])
        out += rec['raw_data']
    return bytes(out)

# --- Paths ---
svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

# --- Load maps ---
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(svaera_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
ae_quests = parse_quests(ae_data, ae_sec[SEC_QUESTS])
ae_bitmaps = parse_bitmap_index(ae_data, ae_sec[SEC_BITMAPS])
ae_bmp_unknown = struct.unpack_from('<I', ae_data, ae_sec[SEC_BITMAPS]['data_offset'])[0]

# Build REC\x02 donor pool from SVAERA v0x0e levels (real 0x0b mesh data)
print('Building REC\\x02 donor pool...')
rec02_donor_pool = {}  # (half_w, half_h) -> smallest real 0x0b data
for lv in ae_levels:
    blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    if len(blob) < 4 or blob[:3] != b'LVL' or blob[3] != 0x0e:
        continue
    secs, _ = parse_blob_sections(blob)
    for s in secs:
        if s['type'] == 0x0b and len(s['data']) > 500:
            ir = struct.unpack_from('<13I', lv['ints_raw'], 0)
            key = (ir[3], ir[5])
            # Keep the smallest real 0x0b for each dimension pair (minimize output size)
            if key not in rec02_donor_pool or len(s['data']) < len(rec02_donor_pool[key]):
                rec02_donor_pool[key] = s['data']
            break
print(f'  {len(rec02_donor_pool)} unique dimension pairs with real 0x0b data')

print('Loading SV...')
sv_arc_obj = ArcArchive.from_file(sv_path)
sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
sv_sec = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])
sv_quests = parse_quests(sv_data, sv_sec[SEC_QUESTS])
sv_bitmaps = parse_bitmap_index(sv_data, sv_sec[SEC_BITMAPS])

ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}
sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}

print(f'  SVAERA: {len(ae_levels)} levels, SV: {len(sv_levels)} levels')

# --- 1. Identify SV-only levels (not in SVAERA) ---
sv_only = []
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    if key not in ae_by_name:
        sv_only.append(lv)
print(f'\n  SV-only levels to add: {len(sv_only)}')

# --- 2. GROUPS: SV's + SVAERA-only ---
print('\n=== Merging GROUPS ===')
sv_groups_raw = sv_data[sv_sec[SEC_GROUPS]['data_offset']:
                        sv_sec[SEC_GROUPS]['data_offset'] + sv_sec[SEC_GROUPS]['size']]
ae_groups_raw = ae_data[ae_sec[SEC_GROUPS]['data_offset']:
                        ae_sec[SEC_GROUPS]['data_offset'] + ae_sec[SEC_GROUPS]['size']]
sv_g_val0, sv_g_recs = _parse_groups(sv_groups_raw)
_, ae_g_recs = _parse_groups(ae_groups_raw)
sv_g_names = set(r['name'] for r in sv_g_recs)
ae_only_recs = [r for r in ae_g_recs if r['name'] not in sv_g_names]
merged_groups = _rebuild_groups(sv_g_val0, sv_g_recs + ae_only_recs)
print(f'  SV: {len(sv_g_recs)}, SVAERA-only: {len(ae_only_recs)}, merged: {len(sv_g_recs) + len(ae_only_recs)}')

# --- 3. SD: SV's (blood cave zone definitions) ---
sv_sd = sv_data[sv_sec[SEC_SD]['data_offset']:
                sv_sec[SEC_SD]['data_offset'] + sv_sec[SEC_SD]['size']]
print(f'  Using SV SD: {len(sv_sd)} bytes')

# --- 4. QUESTS: merged + custom ---
ae_quest_set = set(q.lower() if isinstance(q, str) else q.lower() for q in ae_quests)
new_quests = [q for q in sv_quests if (q.lower() if isinstance(q, str) else q.lower()) not in ae_quest_set]
merged_quests = ae_quests + new_quests
existing_lower = set(q.lower() if isinstance(q, str) else q.decode('ascii', errors='replace').lower()
                     for q in merged_quests)
added_quests = 0
for qname in ALL_CUSTOM_QUEST_NAMES:
    if qname.lower() not in existing_lower:
        merged_quests.append(qname.encode('ascii'))
        existing_lower.add(qname.lower())
        added_quests += 1
new_quests_data = build_quests(merged_quests)
print(f'  Quests: {len(ae_quests)} + {len(new_quests)} SV + {added_quests} custom = {len(merged_quests)}')

# --- 5. Load SV-only level blobs (will convert to v0x11 after NPC injection) ---
print('\n=== Loading SV-only level blobs ===')
converted_blobs = {}  # sv_only index -> blob
v0e_count = v11_count = other_count = 0
for i, lv in enumerate(sv_only):
    blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    converted_blobs[i] = blob
    if len(blob) >= 4 and blob[:3] == b'LVL':
        ver = blob[3]
        if ver == 0x0e:
            v0e_count += 1
        elif ver == 0x11:
            v11_count += 1
        else:
            other_count += 1
    else:
        other_count += 1
print(f'  v0x0e: {v0e_count}, v0x11: {v11_count}, other: {other_count}')

# --- 6. Inject portal NPCs into level blobs ---
print('\n=== Injecting portal NPCs ===')

# Build lookup: level key -> (source, index, blob)
# "ae" levels are in ae_data, "sv_only" are in converted_blobs
ae_inject_keys = {}
for lv_key, specs in INJECT_SPECS.items():
    if lv_key in ae_by_name:
        ae_inject_keys[lv_key] = specs

sv_inject_keys = {}
for lv_key, specs in INJECT_SPECS.items():
    for i, lv in enumerate(sv_only):
        if lv['fname'].replace('\\', '/').lower() == lv_key:
            sv_inject_keys[i] = specs

# Inject into SVAERA levels (these will be patched blobs)
ae_patched_blobs = {}  # ae_level_index -> patched blob
for lv_key, specs in ae_inject_keys.items():
    ae_idx = ae_by_name[lv_key]
    lv = ae_levels[ae_idx]
    blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    blob_ver = blob[3] if blob[:3] == b'LVL' else None

    if blob_ver == 0x11:
        secs, magic = parse_blob_sections(blob)
        for j, s in enumerate(secs):
            if s['type'] == 0x05:
                secs[j] = {'type': 0x05, 'data': inject_into_0x05_v11(s['data'], specs)}
        ae_patched_blobs[ae_idx] = rebuild_blob(magic, secs)
        print(f'  Injected {len(specs)} NPC(s) into SVAERA {lv_key} (v0x11)')
    else:
        print(f'  WARN: {lv_key} is v0x{blob_ver:02x}, skipping injection')

# Inject into SV-only levels
for sv_idx, specs in sv_inject_keys.items():
    blob = converted_blobs[sv_idx]
    blob_ver = blob[3] if blob[:3] == b'LVL' else None
    lv_key = sv_only[sv_idx]['fname'].replace('\\', '/').lower()

    if blob_ver == 0x11:
        secs, magic = parse_blob_sections(blob)
        for j, s in enumerate(secs):
            if s['type'] == 0x05:
                secs[j] = {'type': 0x05, 'data': inject_into_0x05_v11(s['data'], specs)}
        converted_blobs[sv_idx] = rebuild_blob(magic, secs)
        print(f'  Injected {len(specs)} NPC(s) into SV-only {lv_key} (v0x11)')
    elif blob_ver == 0x0e:
        converted_blobs[sv_idx] = inject_into_sv_only_blob(blob, specs, lv_key)
        print(f'  Injected {len(specs)} NPC(s) into SV-only {lv_key} (v0x0e)')
    else:
        print(f'  WARN: {lv_key} has unknown format v0x{blob_ver:02x}')

# --- 7. Append 0x14 entries for injected instances (preserve originals) ---
from build_section_surgery import count_0x05_instances, DEFAULT_0x14_PAYLOAD
for ae_idx, patched_blob in ae_patched_blobs.items():
    secs, magic = parse_blob_sections(patched_blob)
    # Count total instances after injection
    new_count = 0
    for s in secs:
        if s['type'] == 0x05:
            new_count = count_0x05_instances(s['data'])
            break
    else:
        continue
    # Append new 0x14 entries for injected instances (keep original entries intact)
    new_secs = []
    for s in secs:
        if s['type'] == 0x14:
            # Original 0x14 data covers existing instances; append entries for new ones
            orig_data = bytearray(s['data'])
            # Parse existing 0x14 to count entries
            orig_entries = 0
            pos = 0
            while pos + 8 <= len(orig_data):
                idx = struct.unpack_from('<I', orig_data, pos)[0]
                psize = struct.unpack_from('<I', orig_data, pos + 4)[0]
                pos += 8 + psize
                orig_entries += 1
            # Append default entries for new instances (indices after original count)
            for idx in range(orig_entries, new_count):
                orig_data += struct.pack('<II', idx, len(DEFAULT_0x14_PAYLOAD))
                orig_data += DEFAULT_0x14_PAYLOAD
            new_secs.append({'type': 0x14, 'data': bytes(orig_data)})
            print(f'  0x14: kept {orig_entries} original + added {new_count - orig_entries} new entries')
        else:
            new_secs.append(s)
    ae_patched_blobs[ae_idx] = rebuild_blob(magic, new_secs)

# --- 7b. Transplant 0x0b (REC\x02) pathfinding into SV-only level blobs ---
# DISABLED: Engine.dll is now patched to route 0x0a sections through the 0x0b
# handler's init path. This initializes the pathfinding handler (preventing
# crashes) while preserving the original PTH\x04 data. Testing pure 0x0a
# handling with the Engine.dll code-cave patch.
print('\n=== 0x0b transplant DISABLED (testing Engine.dll 0x0a patch) ===')

# --- 7d. DIAGNOSTIC: Append a byte-for-byte SVAERA clone as level 2281+ ---
# Tests whether there is a hidden append-time registration gate.
# Clone ArcadiaDungeonPassage (idx 973, known-good SVAERA v0x0e level).
# Shift grid to non-overlapping position. New unique GUID. Blob unchanged.
CLONE_DONOR_IDX = 973
CLONE_GRID_SHIFT = (80, 0, 0)  # one tile-width right of donor, adjacent for streaming
_donor = ae_levels[CLONE_DONOR_IDX]
_donor_blob = ae_data[_donor['data_offset']:_donor['data_offset'] + _donor['data_length']]

# Build new LEVELS record: copy donor metadata, shift grid, new GUID
_clone_ints = bytearray(_donor['ints_raw'])
_orig_gx, _orig_gy, _orig_gz = struct.unpack_from('<iii', _clone_ints, 24)
_new_gx = _orig_gx + CLONE_GRID_SHIFT[0]
_new_gy = _orig_gy + CLONE_GRID_SHIFT[1]
_new_gz = _orig_gz + CLONE_GRID_SHIFT[2]
struct.pack_into('<iii', _clone_ints, 24, _new_gx, _new_gy, _new_gz)
# Write a new unique GUID (deterministic, won't collide with any existing)
struct.pack_into('<iiii', _clone_ints, 36, 0x7F000001, 0x7F000002, 0x7F000003, 0x7F000004)
_clone_entry = {
    'ints_raw': bytes(_clone_ints),
    'dbr_raw': _donor['dbr_raw'],
    'dbr': _donor['dbr'],
    'fname_raw': _donor['fname_raw'],
    'fname': _donor['fname'],
    'data_offset': 0,  # patched later
    'data_length': len(_donor_blob),
}
# Store for use during map rebuild
_append_clone_blob = _donor_blob
_append_clone_entry = _clone_entry

# Clone's bitmap: copy from donor (shifted later during bitmap fixup)
_donor_bm = ae_bitmaps[CLONE_DONOR_IDX]

_ir = struct.unpack_from('<13i', _clone_ints, 0)
print(f'  APPEND-CLONE: Cloning SVAERA idx {CLONE_DONOR_IDX} as new appended level')
print(f'    Donor: {_donor["fname"]}')
print(f'    Blob: {len(_donor_blob)} bytes (unchanged)')
print(f'    Grid: ({_orig_gx},{_orig_gy},{_orig_gz}) -> ({_new_gx},{_new_gy},{_new_gz})')
print(f'    New GUID: [{_ir[9]}, {_ir[10]}, {_ir[11]}, {_ir[12]}]')
print(f'    Donor bitmap: offset={_donor_bm["offset"]}, length={_donor_bm["length"]}')

# --- 8. Rebuild map ---
print('\n=== Rebuilding map ===')

# Collect SVAERA sections we keep as-is
ae_sections = parse_sections(ae_data)
unk_sections = []
for s in ae_sections:
    if s['type'] not in (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA):
        unk_sections.append((s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]))

# DATA2 from SVAERA (base) + SV's DATA2 appended for SV-only levels
data2_raw = bytearray(ae_data[ae_sec[SEC_DATA2]['data_offset']:
                              ae_sec[SEC_DATA2]['data_offset'] + ae_sec[SEC_DATA2]['size']])
orig_data2_len = len(data2_raw)

# Build merged level list: all SVAERA levels + SV-only levels
# Move blood cave levels to overlap with HiddenValley01's grid area so the engine
# includes them in the active world grid (required for pathfinding activation).
# Cave interiors are visually independent of world position.
GRID_SHIFT = {
    # Shift entire xBloodCave cluster so xPassageTransitionStart's east edge
    # touches HighAltituedBorder01's west edge (X=-198, Z[2135,2263]).
    # This connects the blood cave chain to the SVAERA world grid.
    # xPassageTransitionStart: original (-2021, 1213), w=160 → new X=[-358,-198]
    # bc_initialpathway: new grid (-438, 18, 2215), walkable center at (-397, 18, 2244)
    'xbloodcave': (1663, 0, 922),  # dx, dy, dz
}

merged_levels = [dict(lv) for lv in ae_levels]
grid_shifted = 0
for i, lv in enumerate(sv_only):
    entry = dict(lv)
    key = lv['fname'].replace('\\', '/').lower()
    for pattern, (dx, dy, dz) in GRID_SHIFT.items():
        if pattern in key:
            raw = bytearray(entry['ints_raw'])
            ox, oy, oz = struct.unpack_from('<iii', raw, 24)
            struct.pack_into('<iii', raw, 24, ox + dx, oy + dy, oz + dz)
            entry['ints_raw'] = bytes(raw)
            grid_shifted += 1
            break
    merged_levels.append(entry)
# Append the SVAERA clone as the final level
merged_levels.append(_append_clone_entry)
_clone_merged_idx = len(merged_levels) - 1
print(f'  Grid-shifted {grid_shifted} SV-only levels for world grid connectivity')
print(f'  Appended SVAERA clone at merged index {_clone_merged_idx}')

# Build merged bitmaps: SVAERA bitmaps + SV DATA2 entries for SV-only levels
merged_bitmaps = list(ae_bitmaps)
sv_only_data2 = {}
sv_only_d2_count = 0
for i, lv in enumerate(sv_only):
    lv_key = lv['fname'].replace(chr(92), '/').lower()
    sv_idx = sv_by_name.get(lv_key)
    if sv_idx is not None and sv_idx < len(sv_bitmaps) and sv_bitmaps[sv_idx]['length'] > 0:
        sv_bm = sv_bitmaps[sv_idx]
        sv_path_data = sv_data[sv_bm['offset']:sv_bm['offset'] + sv_bm['length']]
        offset_in_data2 = len(data2_raw)
        data2_raw += sv_path_data
        sv_only_data2[i] = (offset_in_data2, sv_bm['length'])
        sv_only_d2_count += 1
    else:
        sv_only_data2[i] = None
    merged_bitmaps.append({'offset': 0, 'length': 0, 'parts': 0, 'unknown': 0})

# Append clone's bitmap (copy donor's DATA2 data)
if _donor_bm['length'] > 0:
    _clone_bm_offset = len(data2_raw)
    _clone_bm_data = ae_data[_donor_bm['offset']:_donor_bm['offset'] + _donor_bm['length']]
    data2_raw += _clone_bm_data
    merged_bitmaps.append({'offset': 0, 'length': _donor_bm['length']})
    sv_only_data2[len(sv_only)] = (_clone_bm_offset, _donor_bm['length'])
    print(f'  Clone bitmap: {len(_clone_bm_data)} bytes appended to DATA2')
else:
    merged_bitmaps.append({'offset': 0, 'length': 0})
    sv_only_data2[len(sv_only)] = None
    print(f'  Clone bitmap: donor has no bitmap data')

# Append any pending bitmap data from replaced levels
_replace_bm_offsets = {}  # ae_idx -> offset_in_data2
for i in range(len(ae_bitmaps)):
    if isinstance(ae_bitmaps[i], dict) and '_pending_data' in ae_bitmaps[i]:
        _replace_bm_offsets[i] = len(data2_raw)
        data2_raw += ae_bitmaps[i]['_pending_data']
        print(f'  Appended replacement bitmap for idx {i} at DATA2 offset {_replace_bm_offsets[i]}')

# Patch DATA2 level count to match merged level count
# DATA2 header: uint32(0) + uint32(level_count) at offset 4
orig_d2_count = struct.unpack_from('<I', data2_raw, 4)[0]
struct.pack_into('<I', data2_raw, 4, len(merged_levels))
print(f'  DATA2 level count: {orig_d2_count} -> {len(merged_levels)}')

data2_raw = bytes(data2_raw)
print(f'  SV-only DATA2: {sv_only_d2_count}/{len(sv_only)} levels, +{(len(data2_raw) - orig_data2_len)/(1024*1024):.1f} MB')

# Calculate pre-data section layout
new_levels_data = build_level_index(merged_levels)
new_bitmaps_data = build_bitmap_index(merged_bitmaps, ae_bmp_unknown)

new_pre_data_size = 8  # MAP header
new_pre_data_size += 8 + len(new_quests_data)
new_pre_data_size += 8 + len(merged_groups)
new_pre_data_size += 8 + len(sv_sd)
new_pre_data_size += 8 + len(new_levels_data)
new_pre_data_size += 8 + len(new_bitmaps_data)
for _, ud in unk_sections:
    new_pre_data_size += 8 + len(ud)

# DATA section: SVAERA blobs (with patches) + SV-only blobs
print('  Building DATA section...')
data_start = new_pre_data_size + 8 + len(data2_raw) + 8  # after DATA2 + DATA header
compacted_data = bytearray()

for i in range(len(ae_levels)):
    if i in ae_patched_blobs:
        blob = ae_patched_blobs[i]
    else:
        lv = ae_levels[i]
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    merged_levels[i]['data_offset'] = data_start + len(compacted_data)
    merged_levels[i]['data_length'] = len(blob)
    compacted_data += blob

for i, lv in enumerate(sv_only):
    ae_count = len(ae_levels)
    blob = converted_blobs[i]
    merged_levels[ae_count + i]['data_offset'] = data_start + len(compacted_data)
    merged_levels[ae_count + i]['data_length'] = len(blob)
    compacted_data += blob

# Append the SVAERA clone blob
merged_levels[_clone_merged_idx]['data_offset'] = data_start + len(compacted_data)
merged_levels[_clone_merged_idx]['data_length'] = len(_append_clone_blob)
compacted_data += _append_clone_blob

print(f'  DATA: {len(compacted_data)/(1024**2):.1f} MB ({len(ae_levels)} SVAERA + {len(sv_only)} SV-only + 1 clone)')

# Rebuild levels index with corrected offsets
new_levels_data = build_level_index(merged_levels)

# Fix bitmap offsets (shift SVAERA bitmap offsets for new layout)
ae_pre_data = ae_sec[SEC_DATA2]['header_offset']
bmp_offset_shift = new_pre_data_size - ae_pre_data
adjusted_bitmaps = [dict(b) for b in merged_bitmaps]
for i in range(len(ae_bitmaps)):
    if i in _replace_bm_offsets:
        # Replaced level — use pre-computed offset from DATA2 append
        bm_entry = ae_bitmaps[i]
        abs_off = (new_pre_data_size + 8) + _replace_bm_offsets[i]
        adjusted_bitmaps[i]['offset'] = abs_off
        adjusted_bitmaps[i]['length'] = bm_entry['length']
        print(f'  Replaced bitmap at idx {i}: offset={abs_off}, length={bm_entry["length"]}')
    elif adjusted_bitmaps[i]['offset'] > 0:
        adjusted_bitmaps[i]['offset'] = ae_bitmaps[i]['offset'] + bmp_offset_shift

# Set bitmap entries for SV-only levels (DATA2 pathfinding)
new_data2_data_start = new_pre_data_size + 8  # after pre-data sections + DATA2 header
for i, appended_info in sv_only_data2.items():
    merged_idx = len(ae_levels) + i
    if appended_info is not None:
        offset_in_data2, length = appended_info
        abs_offset = new_data2_data_start + offset_in_data2
        adjusted_bitmaps[merged_idx]['offset'] = abs_offset
        adjusted_bitmaps[merged_idx]['length'] = length

new_bitmaps_data = build_bitmap_index(adjusted_bitmaps, ae_bmp_unknown)

# Write map
print('\nWriting map...')
header2 = new_pre_data_size - 8
out = bytearray()
out += struct.pack('<II', MAP_MAGIC, header2)
out += struct.pack('<II', SEC_QUESTS, len(new_quests_data)); out += new_quests_data
out += struct.pack('<II', SEC_GROUPS, len(merged_groups)); out += merged_groups
out += struct.pack('<II', SEC_SD, len(sv_sd)); out += sv_sd
out += struct.pack('<II', SEC_LEVELS, len(new_levels_data)); out += new_levels_data
out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data)); out += new_bitmaps_data
for utype, udata in unk_sections:
    out += struct.pack('<II', utype, len(udata)); out += udata
out += struct.pack('<II', SEC_DATA2, len(data2_raw)); out += data2_raw
out += struct.pack('<II', SEC_DATA, len(compacted_data))
out += compacted_data

result = bytes(out)
print(f'  Size: {len(result)/(1024**2):.1f} MB, under 2GB: {len(result) < 2147483647}')

# Verify
test_sections = parse_sections(result)
test_sec = {s['type']: s for s in test_sections}
test_levels = parse_level_index(result, test_sec[SEC_LEVELS])
bad = sum(1 for lv in test_levels if lv['data_offset'] + lv['data_length'] > len(result))
bad_magic = sum(1 for lv in test_levels if result[lv['data_offset']:lv['data_offset']+3] != b'LVL')
zero_ints = sum(1 for lv in test_levels if lv['ints_raw'] == b'\x00' * 52)
print(f'  Levels: {len(test_levels)}, bad offsets: {bad}, bad magic: {bad_magic}, zero ints: {zero_ints}')
print(f'  drxmap refs: {result.count(b"drxmap")}')

v11 = sum(1 for lv in test_levels if result[lv['data_offset']+3:lv['data_offset']+4] == b'\x11')
v0e = sum(1 for lv in test_levels if result[lv['data_offset']+3:lv['data_offset']+4] == b'\x0e')
print(f'  Format: v0x11={v11}, v0x0e={v0e}, other={len(test_levels)-v11-v0e}')

# Package into ARC
print('\nPackaging into ARC...')
arc = ArcArchive.from_file(svaera_path)
arc.set_file('world/world01.map', result)
arc.write(out_arc_path)
print(f'  Written: {out_arc_path.stat().st_size / (1024**2):.1f} MB')

del ae_data, sv_data, result
print('Done.')
