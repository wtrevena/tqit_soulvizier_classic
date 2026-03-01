#!/usr/bin/env python3
"""
Binary merge of SV custom map content into SVAERA's AE-compatible map.

Unlike the decompile-recompile approach, this directly patches the SVAERA binary
to add SV-only levels and replace shared levels with SV versions. This avoids
the recompilation bloat that pushes the map over the 2GB signed int limit.
"""

import struct
import sys
from pathlib import Path

MAP_MAGIC = 0x0650414D

SEC_LEVELS  = 0x01
SEC_DATA    = 0x02
SEC_GROUPS  = 0x11
SEC_SD      = 0x18
SEC_BITMAPS = 0x19
SEC_DATA2   = 0x1A
SEC_QUESTS  = 0x1B


def parse_sections(data):
    sections = []
    pos = 8
    while pos + 8 <= len(data):
        st = struct.unpack_from('<I', data, pos)[0]
        ss = struct.unpack_from('<I', data, pos + 4)[0]
        if ss > len(data) - pos - 8:
            break
        sections.append({'type': st, 'header_offset': pos, 'data_offset': pos + 8, 'size': ss})
        pos += 8 + ss
    return sections


def parse_level_index(data, sec):
    buf = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    count = struct.unpack_from('<I', buf, 0)[0]
    levels = []
    idx = 4
    for _ in range(count):
        entry_start = idx
        ints_raw = buf[idx:idx + 52]
        idx += 52
        dbr_len = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        dbr = buf[idx:idx + dbr_len]; idx += dbr_len
        fname_len = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        fname = buf[idx:idx + fname_len]; idx += fname_len
        data_offset = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        data_length = struct.unpack_from('<I', buf, idx)[0]; idx += 4

        levels.append({
            'ints_raw': ints_raw,
            'dbr_raw': dbr,
            'dbr': dbr.decode('ascii', errors='replace'),
            'fname_raw': fname,
            'fname': fname.decode('ascii', errors='replace'),
            'data_offset': data_offset,
            'data_length': data_length,
        })
    return levels


def build_level_index(levels):
    buf = bytearray()
    buf += struct.pack('<I', len(levels))
    for lv in levels:
        buf += lv['ints_raw']
        buf += struct.pack('<I', len(lv['dbr_raw']))
        buf += lv['dbr_raw']
        buf += struct.pack('<I', len(lv['fname_raw']))
        buf += lv['fname_raw']
        buf += struct.pack('<I', lv['data_offset'])
        buf += struct.pack('<I', lv['data_length'])
    return bytes(buf)


def parse_quests(data, sec):
    buf = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    count = struct.unpack_from('<I', buf, 0)[0]
    quests = []
    idx = 4
    for _ in range(count):
        qlen = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        qname = buf[idx:idx + qlen]
        idx += qlen
        quests.append(qname)
    return quests


def build_quests(quests):
    buf = bytearray()
    buf += struct.pack('<I', len(quests))
    for q in quests:
        buf += struct.pack('<I', len(q))
        buf += q
    return bytes(buf)


def parse_bitmap_index(data, sec):
    buf = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    if len(buf) < 8:
        return []
    unknown = struct.unpack_from('<I', buf, 0)[0]
    count = struct.unpack_from('<I', buf, 4)[0]
    entries = []
    for i in range(count):
        offset = struct.unpack_from('<I', buf, 8 + i * 8)[0]
        length = struct.unpack_from('<I', buf, 12 + i * 8)[0]
        entries.append({'offset': offset, 'length': length})
    return entries


def build_bitmap_index(entries, unknown_val=0):
    buf = bytearray()
    buf += struct.pack('<I', unknown_val)
    buf += struct.pack('<I', len(entries))
    for e in entries:
        buf += struct.pack('<II', e['offset'], e['length'])
    return bytes(buf)


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <svaera_levels.arc> <sv_levels.arc> <output.map>")
        sys.exit(1)

    svaera_arc_path = Path(sys.argv[1])
    sv_arc_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    sys.path.insert(0, str(Path(__file__).parent))
    from arc_patcher import ArcArchive

    print("Loading SVAERA map...")
    ae_arc = ArcArchive.from_file(svaera_arc_path)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    print(f"  {len(ae_data)} bytes ({len(ae_data) / (1024**2):.1f} MB)")

    print("Loading SV 0.98i map...")
    sv_arc = ArcArchive.from_file(sv_arc_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    print(f"  {len(sv_data)} bytes ({len(sv_data) / (1024**2):.1f} MB)")

    # Parse SVAERA sections
    ae_sections = parse_sections(ae_data)
    ae_sec_map = {}
    for s in ae_sections:
        ae_sec_map[s['type']] = s

    # Parse SV sections
    sv_sections = parse_sections(sv_data)
    sv_sec_map = {}
    for s in sv_sections:
        sv_sec_map[s['type']] = s

    # Parse level indices
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    print(f"\n  SVAERA: {len(ae_levels)} levels")
    print(f"  SV:     {len(sv_levels)} levels")

    # Build SVAERA name lookup
    ae_by_name = {}
    for i, lv in enumerate(ae_levels):
        key = lv['fname'].replace('\\', '/').lower()
        ae_by_name[key] = i

    # Identify SV-only levels and shared levels with custom content
    sv_only = []
    sv_custom_shared = []
    for lv in sv_levels:
        key = lv['fname'].replace('\\', '/').lower()
        chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if key not in ae_by_name:
            sv_only.append(lv)
        elif b'drxmap' in chunk:
            sv_custom_shared.append((lv, ae_by_name[key]))

    print(f"\n  SV-only levels to add: {len(sv_only)}")
    print(f"  Shared levels to replace: {len(sv_custom_shared)} (with ints_raw swap for 0x0e compat)")

    # Parse quests
    ae_quests = parse_quests(ae_data, ae_sec_map[SEC_QUESTS])
    sv_quests = parse_quests(sv_data, sv_sec_map[SEC_QUESTS])
    ae_quest_set = set(q.lower() for q in ae_quests)
    new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]
    merged_quests = ae_quests + new_quests
    print(f"\n  SVAERA quests: {len(ae_quests)}")
    print(f"  SV-only quests to add: {len(new_quests)}")

    # Parse bitmap index
    ae_bitmaps = parse_bitmap_index(ae_data, ae_sec_map[SEC_BITMAPS])
    bmp_raw = ae_data[ae_sec_map[SEC_BITMAPS]['data_offset']:
                       ae_sec_map[SEC_BITMAPS]['data_offset'] + 4]
    bmp_unknown = struct.unpack_from('<I', bmp_raw, 0)[0]

    # ===== BUILD MERGED MAP =====
    print("\nBuilding merged map...")

    # Collect SV data blobs to append
    append_blobs = []
    sv_only_indices = []
    for lv in sv_only:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        sv_only_indices.append(len(append_blobs))
        append_blobs.append(blob)

    shared_replace_info = []
    for lv, ae_idx in sv_custom_shared:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        shared_replace_info.append((ae_idx, len(append_blobs), lv))
        append_blobs.append(blob)

    total_append = sum(len(b) for b in append_blobs)
    print(f"  Total data to append: {total_append} bytes ({total_append / (1024**2):.1f} MB)")

    # Build new sections in order, calculating offsets
    new_quests_data = build_quests(merged_quests)

    # Section order: header(8) + quests + groups + sd + levels + bitmaps + unknown + data2 + data + appended
    # We need to figure out the offset where DATA2 section starts, because level entries
    # reference absolute file positions within DATA2/DATA.

    # Calculate original pre-data offset (everything before DATA2)
    orig_pre_data_size = ae_sec_map[SEC_DATA2]['header_offset']

    # Build new level index and bitmap index with placeholder offsets
    # MUST deep-copy dicts to avoid corrupting ae_levels/ae_bitmaps originals
    merged_levels = [dict(lv) for lv in ae_levels]
    for lv in sv_only:
        merged_levels.append(dict(lv))

    new_levels_data = build_level_index(merged_levels)

    # New bitmap entries: SVAERA's + empty entries for SV-only levels
    merged_bitmaps = [dict(b) for b in ae_bitmaps]
    for _ in sv_only:
        merged_bitmaps.append({'offset': 0, 'length': 0})
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

    # Get other section raw data
    groups_data = ae_data[ae_sec_map[SEC_GROUPS]['data_offset']:
                          ae_sec_map[SEC_GROUPS]['data_offset'] + ae_sec_map[SEC_GROUPS]['size']]
    sd_data = ae_data[ae_sec_map[SEC_SD]['data_offset']:
                      ae_sec_map[SEC_SD]['data_offset'] + ae_sec_map[SEC_SD]['size']]

    unknown_sec = [s for s in ae_sections if s['type'] not in
                   (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA)]
    unknown_sections_data = []
    for s in unknown_sec:
        unknown_sections_data.append((s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]))

    # Calculate new pre-data size
    new_pre_data_size = 8  # header
    new_pre_data_size += 8 + len(new_quests_data)
    new_pre_data_size += 8 + len(groups_data)
    new_pre_data_size += 8 + len(sd_data)
    new_pre_data_size += 8 + len(new_levels_data)
    new_pre_data_size += 8 + len(new_bitmaps_data)
    for _, ud in unknown_sections_data:
        new_pre_data_size += 8 + len(ud)

    # The offset shift for all absolute file references
    offset_shift = new_pre_data_size - orig_pre_data_size
    print(f"  Offset shift: {offset_shift} bytes")

    # Get the raw DATA2 + DATA sections
    data2_sec = ae_sec_map[SEC_DATA2]
    data_sec = ae_sec_map[SEC_DATA]
    data2_raw = bytearray(ae_data[data2_sec['data_offset']:data2_sec['data_offset'] + data2_sec['size']])
    data_raw = ae_data[data_sec['data_offset']:data_sec['data_offset'] + data_sec['size']]

    # Patch DATA2 level count to match merged level count
    # DATA2 header: uint32(0) + uint32(level_count) at offset 4
    orig_d2_count = struct.unpack_from('<I', data2_raw, 4)[0]
    new_d2_count = len(merged_levels)
    struct.pack_into('<I', data2_raw, 4, new_d2_count)
    print(f"  DATA2 level count: {orig_d2_count} -> {new_d2_count}")
    data2_raw = bytes(data2_raw)

    # Calculate where appended blobs will start (after all original data)
    append_start = new_pre_data_size + 8 + len(data2_raw) + 8 + len(data_raw)

    # Now fix up level offsets
    # 1. Shift all original SVAERA level offsets
    for i in range(len(ae_levels)):
        merged_levels[i]['data_offset'] = ae_levels[i]['data_offset'] + offset_shift

    # 2. For shared levels being replaced, point to appended SV data AND swap ints_raw
    # Using SV's ints_raw ensures the engine treats them as 0x0e (TQIT format) levels
    # with matching metadata, so it uses TQIT-embedded pathfinding instead of DATA2's
    for ae_idx, blob_idx, sv_lv in shared_replace_info:
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
        merged_levels[ae_idx]['data_offset'] = blob_offset
        merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])
        merged_levels[ae_idx]['ints_raw'] = sv_lv['ints_raw']

    # 3. For SV-only levels, point to appended data
    for i, sv_blob_idx in enumerate(sv_only_indices):
        lv_idx = len(ae_levels) + i
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(sv_blob_idx))
        merged_levels[lv_idx]['data_offset'] = blob_offset

    # 4. Fix bitmap offsets
    for i in range(len(ae_bitmaps)):
        if merged_bitmaps[i]['offset'] > 0:
            merged_bitmaps[i]['offset'] = ae_bitmaps[i]['offset'] + offset_shift

    # Rebuild level and bitmap sections with corrected offsets
    new_levels_data = build_level_index(merged_levels)
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

    # Write the merged map
    print("  Writing merged map...")
    out = bytearray()

    # header2 = total metadata section size (before DATA2), excluding 8-byte MAP header
    header2 = new_pre_data_size - 8
    out += struct.pack('<II', MAP_MAGIC, header2)

    # Sections in original order
    out += struct.pack('<II', SEC_QUESTS, len(new_quests_data))
    out += new_quests_data
    out += struct.pack('<II', SEC_GROUPS, len(groups_data))
    out += groups_data
    out += struct.pack('<II', SEC_SD, len(sd_data))
    out += sd_data
    out += struct.pack('<II', SEC_LEVELS, len(new_levels_data))
    out += new_levels_data
    out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data))
    out += new_bitmaps_data
    for utype, udata in unknown_sections_data:
        out += struct.pack('<II', utype, len(udata))
        out += udata
    out += struct.pack('<II', SEC_DATA2, len(data2_raw))
    out += data2_raw

    # Extend DATA section to include appended SV level blobs
    # The game reads level data by absolute offset and only maps up to declared section ends
    extended_data_size = len(data_raw) + total_append
    out += struct.pack('<II', SEC_DATA, extended_data_size)
    out += data_raw
    for blob in append_blobs:
        out += blob

    result = bytes(out)
    print(f"\n  Final size: {len(result)} bytes ({len(result) / (1024**2):.1f} MB)")
    print(f"  Under 2GB limit: {len(result) < 2147483647}")

    # Verify
    drxmap_count = result.count(b'drxmap')
    print(f"  drxmap refs: {drxmap_count}")

    output_path.write_bytes(result)
    print(f"\n  Written to: {output_path}")

    del ae_data, sv_data, result
    print("Done.")


if __name__ == '__main__':
    main()
