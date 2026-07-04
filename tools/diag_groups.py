#!/usr/bin/env python3
"""
Diagnostic script for TQ map GROUPS (0x11) and SD (0x18) sections.

GROUPS section format (discovered):
  Header:
    uint32  unknown (always 0)
    uint32  record_count

  Each record:
    uint32  sub_count (observed: always 2)
    uint32  name_len
    char[]  name (ASCII, name_len bytes)
    uint32  category_len
    char[]  category (ASCII, category_len bytes)
    uint32  member_count

    Member data varies by category:
    - Most categories: 20 + 44 * member_count bytes
      = 16 GUID + 4 spare, then per member: 16 GUID + 12 floats (pos) + 16 GUID
      (but exact sub-structure of 44-byte members still TBD)
    - "Any Entity": 48 + 30 * member_count bytes
    - "Npc Wanderers" / "ProxyPatrollers": 36 + 44 * member_count (base)
      with some records having extra 16-byte GUID blocks appended
    - Some records in any category can have trailing linked-entity data
      (uint32 count + count * 16-byte GUIDs)

  Groups are NOT level-connectivity data. They are spatial entity groupings
  for proxies, wanderers, shrines, patrol points, etc. They use GUIDs to
  reference entities, NOT level indices.
"""

import struct
import sys
import string
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS, SEC_SD


def extract_map_data(arc_path):
    """Load a Levels.arc, find the Levels.map file inside, return its raw bytes."""
    arc = ArcArchive.from_file(Path(arc_path))
    for entry in arc.entries:
        if entry.name.lower().endswith('.map'):
            data = arc.decompress(entry)
            return data, entry.name
    raise RuntimeError(f"No .map file found in {arc_path}")


def extract_ascii_strings(data, min_len=4):
    """Extract all sequences of printable ASCII chars of at least min_len."""
    printable = set(string.printable) - set('\t\n\r\x0b\x0c')
    results = []
    current = []
    start = -1
    for i, b in enumerate(data):
        ch = chr(b) if b < 128 else None
        if ch and ch in printable:
            if not current:
                start = i
            current.append(ch)
        else:
            if len(current) >= min_len:
                results.append((start, ''.join(current)))
            current = []
    if len(current) >= min_len:
        results.append((start, ''.join(current)))
    return results


def hexdump(data, length=100, prefix=""):
    """Print hex dump of first `length` bytes."""
    for i in range(0, min(len(data), length), 16):
        hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
        print(f"{prefix}{i:06x}: {hex_part:<48s}  {ascii_part}")


def find_section(sections, sec_type):
    for s in sections:
        if s['type'] == sec_type:
            return s
    return None


def get_section_data(map_data, sec):
    return map_data[sec['data_offset']:sec['data_offset'] + sec['size']]


def find_next_record(data, start, end_limit):
    """Find the start of the next record by scanning for the structural pattern."""
    for scan in range(start, min(end_limit, len(data) - 12)):
        sub = struct.unpack_from('<I', data, scan)[0]
        if sub > 20:
            continue
        slen = struct.unpack_from('<I', data, scan + 4)[0]
        if slen < 3 or slen > 200 or scan + 8 + slen > len(data):
            continue
        s = data[scan+8:scan+8+slen]
        if not all(32 <= b < 127 for b in s):
            continue
        pos2 = scan + 8 + slen
        if pos2 + 4 > len(data):
            continue
        slen2 = struct.unpack_from('<I', data, pos2)[0]
        if slen2 < 3 or slen2 > 200 or pos2 + 4 + slen2 > len(data):
            continue
        s2 = data[pos2+4:pos2+4+slen2]
        if all(32 <= b < 127 for b in s2):
            return scan
    return None


def parse_groups_records(data):
    """Parse all records from a GROUPS section."""
    val0, count = struct.unpack_from('<II', data, 0)
    pos = 8
    records = []
    for i in range(count):
        rec_start = pos
        sub_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        name_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
        name = data[pos:pos+name_len].decode('ascii', errors='replace'); pos += name_len
        cat_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
        category = data[pos:pos+cat_len].decode('ascii', errors='replace'); pos += cat_len
        member_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        member_data_start = pos

        if i < count - 1:
            next_start = find_next_record(data, pos, pos + 200000)
            if next_start is None:
                member_data_len = len(data) - pos
            else:
                member_data_len = next_start - pos
        else:
            member_data_len = len(data) - pos

        records.append({
            'idx': i,
            'offset': rec_start,
            'sub_count': sub_count,
            'name': name,
            'category': category,
            'member_count': member_count,
            'data_start': member_data_start,
            'data_len': member_data_len,
            'raw_data': data[member_data_start:member_data_start + member_data_len],
        })

        pos = member_data_start + member_data_len
    return val0, count, records


def main():
    svaera_arc = Path(r"c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc")
    sv_arc = Path(r"c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc")

    print("=" * 80)
    print("LOADING ARCHIVES")
    print("=" * 80)

    svaera_map, svaera_name = extract_map_data(svaera_arc)
    print(f"SVAERA map: {svaera_name}, size: {len(svaera_map)} bytes")

    sv_map, sv_name = extract_map_data(sv_arc)
    print(f"SV map: {sv_name}, size: {len(sv_map)} bytes")

    svaera_secs = parse_sections(svaera_map)
    sv_secs = parse_sections(sv_map)

    print(f"\nSVAERA sections: {[(hex(s['type']), s['size']) for s in svaera_secs]}")
    print(f"SV sections:     {[(hex(s['type']), s['size']) for s in sv_secs]}")

    # =========================================================================
    # A) Parse GROUPS format
    # =========================================================================
    print("\n" + "=" * 80)
    print("A) GROUPS FORMAT ANALYSIS")
    print("=" * 80)

    for label, map_data, secs in [("SVAERA", svaera_map, svaera_secs), ("SV", sv_map, sv_secs)]:
        groups_data = get_section_data(map_data, find_section(secs, SEC_GROUPS))
        print(f"\n--- {label} GROUPS section: {len(groups_data)} bytes ---")

        print(f"\nFirst 200 bytes hex dump:")
        hexdump(groups_data, 200, prefix="  ")

        val0, count, records = parse_groups_records(groups_data)
        print(f"\n  Header: val0={val0}, count={count}")
        print(f"  Parsed {len(records)} records")

        # Category distribution
        cat_counts = Counter(r['category'] for r in records)
        print(f"\n  Category distribution:")
        for cat, cnt in cat_counts.most_common():
            print(f"    \"{cat}\": {cnt}")

        # Per-category size formulas
        by_cat = defaultdict(list)
        for r in records:
            by_cat[r['category']].append(r)

        print(f"\n  Per-category size formulas (data_len = A * member_count + B):")
        for cat in sorted(by_cat.keys()):
            recs = by_cat[cat]
            # Test formula: data_len = 44 * mc + 20
            m44_20 = sum(1 for r in recs if r['member_count'] > 0 and r['data_len'] == 44 * r['member_count'] + 20)
            m44_36 = sum(1 for r in recs if r['member_count'] > 0 and r['data_len'] == 44 * r['member_count'] + 36)
            m30_48 = sum(1 for r in recs if r['member_count'] > 0 and r['data_len'] == 30 * r['member_count'] + 48)
            total_nonzero = sum(1 for r in recs if r['member_count'] > 0)

            if m44_20 == total_nonzero and total_nonzero > 0:
                print(f"    \"{cat}\": 44*mc + 20  ({m44_20}/{total_nonzero} match)")
            elif m44_36 == total_nonzero and total_nonzero > 0:
                print(f"    \"{cat}\": 44*mc + 36  ({m44_36}/{total_nonzero} match)")
            elif m30_48 == total_nonzero and total_nonzero > 0:
                print(f"    \"{cat}\": 30*mc + 48  ({m30_48}/{total_nonzero} match)")
            else:
                best = max([(m44_20, "44*mc+20"), (m44_36, "44*mc+36"), (m30_48, "30*mc+48")], key=lambda x: x[0])
                print(f"    \"{cat}\": ~{best[1]}  ({best[0]}/{total_nonzero} match, mixed)")

        # First 10 and last 5 records
        print(f"\n  First 10 records:")
        for r in records[:10]:
            print(f"    [{r['idx']:4d}] sub={r['sub_count']} members={r['member_count']:3d} "
                  f"data={r['data_len']:5d} cat=\"{r['category']}\" name=\"{r['name']}\"")
        print(f"  Last 5 records:")
        for r in records[-5:]:
            print(f"    [{r['idx']:4d}] sub={r['sub_count']} members={r['member_count']:3d} "
                  f"data={r['data_len']:5d} cat=\"{r['category']}\" name=\"{r['name']}\"")

    # =========================================================================
    # B) Extract ALL ASCII strings from GROUPS
    # =========================================================================
    print("\n" + "=" * 80)
    print("B) ASCII STRING EXTRACTION FROM GROUPS")
    print("=" * 80)

    for label, map_data, secs in [("SVAERA", svaera_map, svaera_secs), ("SV", sv_map, sv_secs)]:
        groups_data = get_section_data(map_data, find_section(secs, SEC_GROUPS))
        strings = extract_ascii_strings(groups_data, min_len=4)
        # Only show actual group/category names (filter out noise)
        real_strings = [(off, s) for off, s in strings
                       if any(c.isalpha() for c in s[:3]) and len(s) >= 6]
        print(f"\n--- {label} GROUPS: {len(strings)} total strings, {len(real_strings)} likely names ---")
        for offset, s in real_strings[:50]:
            print(f"  offset {offset:6d} (0x{offset:06x}): \"{s}\"")
        if len(real_strings) > 50:
            print(f"  ... and {len(real_strings) - 50} more")

    # =========================================================================
    # C) Compare SVAERA vs SV GROUPS
    # =========================================================================
    print("\n" + "=" * 80)
    print("C) SVAERA vs SV GROUPS COMPARISON")
    print("=" * 80)

    svaera_groups = get_section_data(svaera_map, find_section(svaera_secs, SEC_GROUPS))
    sv_groups = get_section_data(sv_map, find_section(sv_secs, SEC_GROUPS))

    _, _, svaera_recs = parse_groups_records(svaera_groups)
    _, _, sv_recs = parse_groups_records(sv_groups)

    print(f"SVAERA GROUPS: {len(svaera_groups)} bytes, {len(svaera_recs)} records")
    print(f"SV GROUPS:     {len(sv_groups)} bytes, {len(sv_recs)} records")

    svaera_names = set(r['name'] for r in svaera_recs)
    sv_names = set(r['name'] for r in sv_recs)

    shared = svaera_names & sv_names
    svaera_only = svaera_names - sv_names
    sv_only = sv_names - svaera_names

    print(f"\nShared groups: {len(shared)}")
    print(f"SVAERA-only groups: {len(svaera_only)}")
    print(f"SV-only groups: {len(sv_only)}")

    if svaera_only:
        print(f"\nSVAERA-only group names (first 30):")
        for name in sorted(svaera_only)[:30]:
            r = next(r for r in svaera_recs if r['name'] == name)
            print(f"  \"{name}\" cat=\"{r['category']}\" members={r['member_count']}")

    if sv_only:
        print(f"\nSV-only group names:")
        for name in sorted(sv_only):
            r = next(r for r in sv_recs if r['name'] == name)
            print(f"  \"{name}\" cat=\"{r['category']}\" members={r['member_count']}")

    # =========================================================================
    # D) Blood cave content in SV GROUPS
    # =========================================================================
    print("\n" + "=" * 80)
    print("D) BLOOD CAVE REFERENCES IN GROUPS")
    print("=" * 80)

    for label, recs in [("SVAERA", svaera_recs), ("SV", sv_recs)]:
        bc_groups = [r for r in recs if any(t in r['name'].lower()
                     for t in ['blood', 'bc_', 'xblood', 'cave'])]
        print(f"\n{label}: {len(bc_groups)} groups with blood/cave in name")
        for r in bc_groups:
            print(f"  [{r['idx']}] \"{r['name']}\" cat=\"{r['category']}\" members={r['member_count']}")

    # =========================================================================
    # E) SD section analysis
    # =========================================================================
    print("\n" + "=" * 80)
    print("E) SD SECTION (0x18) ANALYSIS")
    print("=" * 80)

    for label, map_data, secs in [("SVAERA", svaera_map, svaera_secs), ("SV", sv_map, sv_secs)]:
        sd_sec = find_section(secs, SEC_SD)
        if not sd_sec:
            print(f"{label} SD: NOT FOUND")
            continue
        sd_data = get_section_data(map_data, sd_sec)
        print(f"\n{label} SD: {len(sd_data)} bytes")
        print(f"  First 100 bytes:")
        hexdump(sd_data, 100, prefix="    ")

        strings = extract_ascii_strings(sd_data, min_len=6)
        real_strings = [(off, s) for off, s in strings
                       if any(c.isalpha() for c in s[:3])]
        print(f"  {len(real_strings)} likely name strings (showing first 30):")
        for offset, s in real_strings[:30]:
            print(f"    offset {offset:6d}: \"{s}\"")
        if len(real_strings) > 30:
            print(f"    ... and {len(real_strings) - 30} more")

        # Blood cave search
        bc_strings = [(off, s) for off, s in strings
                     if any(t in s.lower() for t in ['blood', 'bc_', 'xblood', 'cave'])]
        if bc_strings:
            print(f"\n  Blood cave references in SD:")
            for off, s in bc_strings:
                print(f"    offset {off}: \"{s}\"")

    # SD comparison
    svaera_sd = get_section_data(svaera_map, find_section(svaera_secs, SEC_SD))
    sv_sd = get_section_data(sv_map, find_section(sv_secs, SEC_SD))

    print(f"\nSD comparison:")
    print(f"  SVAERA SD size: {len(svaera_sd)} bytes")
    print(f"  SV SD size:     {len(sv_sd)} bytes")
    if svaera_sd == sv_sd:
        print("  RESULT: SD sections are IDENTICAL")
    else:
        print(f"  RESULT: SD sections DIFFER (size diff: {len(sv_sd) - len(svaera_sd):+d} bytes)")

    # =========================================================================
    # F) Level indices and GROUPS cross-reference
    # =========================================================================
    print("\n" + "=" * 80)
    print("F) LEVEL INDICES AND GROUPS CROSS-REFERENCE")
    print("=" * 80)

    for label, map_data, secs, groups_data in [
        ("SVAERA", svaera_map, svaera_secs, svaera_groups),
        ("SV", sv_map, sv_secs, sv_groups)
    ]:
        levels_sec = find_section(secs, SEC_LEVELS)
        levels = parse_level_index(map_data, levels_sec)
        print(f"\n--- {label}: {len(levels)} levels ---")

        # Find specific levels
        for i, lv in enumerate(levels):
            fname = lv['fname']
            if any(t in fname.lower() for t in ['random09a', 'xbloodcave', 'bc_initial']):
                print(f"  Level [{i:3d}]: \"{fname}\"")

        # Print first and last levels
        print(f"\n  First 5 levels:")
        for i in range(min(5, len(levels))):
            print(f"    [{i:3d}]: \"{levels[i]['fname']}\"")
        print(f"  Last 5 levels:")
        for i in range(max(0, len(levels)-5), len(levels)):
            print(f"    [{i:3d}]: \"{levels[i]['fname']}\"")

        # Search for Random09A level index in GROUPS binary
        random09a_idx = None
        for i, lv in enumerate(levels):
            if 'random09a' in lv['fname'].lower():
                random09a_idx = i
                break

        if random09a_idx is not None:
            print(f"\n  Random09A at level index {random09a_idx}")
            needle = struct.pack('<I', random09a_idx)
            occurrences = []
            start = 0
            while True:
                idx = groups_data.find(needle, start)
                if idx < 0:
                    break
                occurrences.append(idx)
                start = idx + 1
            print(f"  uint32 {random09a_idx} (0x{random09a_idx:08x}) found in GROUPS: {len(occurrences)} times")
            if occurrences:
                print(f"  Occurrences at byte offsets: {occurrences[:10]}")

        # Blood cave level indices
        bc_levels = [(i, lv['fname']) for i, lv in enumerate(levels)
                    if any(t in lv['fname'].lower() for t in ['xbloodcave', 'bc_'])]
        if bc_levels:
            print(f"\n  Blood cave levels ({len(bc_levels)}):")
            found_in_groups = 0
            for idx, fname in bc_levels[:10]:
                needle = struct.pack('<I', idx)
                occ_count = groups_data.count(needle)
                if occ_count > 0:
                    found_in_groups += 1
                print(f"    [{idx:3d}]: \"{fname}\" -> uint32 in GROUPS: {occ_count}")
            print(f"  Blood cave indices found in GROUPS data: {found_in_groups}/{len(bc_levels[:10])}")

    # =========================================================================
    # SUMMARY: What GROUPS is and isn't
    # =========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY: GROUPS SECTION FORMAT")
    print("=" * 80)
    print("""
GROUPS section (type 0x11) stores SPATIAL ENTITY GROUPINGS, not level connectivity.

Structure:
  Header: uint32(0) + uint32(record_count)

  Per record:
    uint32  sub_count (always 2 in observed data)
    string  name (length-prefixed ASCII)
    string  category (length-prefixed ASCII)
    uint32  member_count
    bytes   member_data (variable length, see formulas below)

  Member data size by category:
    Most categories:     44 * member_count + 20 bytes
    Npc Wanderers:       44 * member_count + 36 bytes (base, some have extras)
    ProxyPatrollers:     44 * member_count + 36 bytes
    Any Entity:          30 * member_count + 48 bytes

  The member data contains GUIDs (16-byte identifiers referencing game entities)
  and float values (positions/coordinates).

  Key findings:
  - GROUPS does NOT store level indices or level connectivity
  - GROUPS uses GUIDs to reference entities (proxies, NPCs, shrines)
  - SVAERA has more groups than SV (889 vs 548) due to AE expansion content
  - SV's blood cave levels (xBloodCave) are NOT referenced in SV's GROUPS
  - Blood cave levels have NO groups entries in SV
  - The SVAERA version has 'bc_' string at offset 148453 but SV does not
""")

    print("=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == '__main__':
    main()
