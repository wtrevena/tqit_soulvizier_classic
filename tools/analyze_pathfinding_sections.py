#!/usr/bin/env python3
"""
Deep analysis of 0x0a (PTH\x04) vs 0x0b (REC\x02) pathfinding sections.

Compares the internal structure of TQIT pathfinding (0x0a) from SV levels
with TQAE pathfinding (0x0b) from SVAERA levels to determine if programmatic
conversion from 0x0a -> 0x0b is feasible.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections


def hex_ascii_dump(data, offset=0, length=256, prefix='  '):
    """Dump data as hex + ascii, 16 bytes per line."""
    lines = []
    end = min(offset + length, len(data))
    for i in range(offset, end, 16):
        chunk = data[i:min(i + 16, end)]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'{prefix}{i:08x}: {hex_part:<48s} {ascii_part}')
    return '\n'.join(lines)


def analyze_0x0a_section(data, label='0x0a'):
    """Parse and analyze PTH\x04 (TQIT pathfinding) section structure."""
    print(f'\n{"="*70}')
    print(f'=== {label}: 0x0a Section Analysis (PTH\\x04) ===')
    print(f'{"="*70}')
    print(f'Total size: {len(data)} bytes ({len(data)/1024:.1f} KB)')

    if len(data) < 16:
        print('  TOO SHORT to analyze')
        return {}

    # First 256 bytes hex dump
    print(f'\nFirst 256 bytes:')
    print(hex_ascii_dump(data, 0, 256))

    # Check magic bytes
    magic = data[:4]
    magic_str = ''.join(chr(b) if 32 <= b < 127 else f'\\x{b:02x}' for b in magic)
    print(f'\nMagic: {magic.hex()} = "{magic_str}"')

    result = {'size': len(data), 'magic': magic}

    # Try to parse as PTH\x04 format
    if magic == b'PTH\x04':
        print('  Confirmed: PTH version 4')
        result['format'] = 'PTH_v4'
    elif magic[:3] == b'PTH':
        ver = magic[3]
        print(f'  PTH version {ver}')
        result['format'] = f'PTH_v{ver}'
    else:
        print(f'  NOT PTH magic! Got: {magic.hex()}')
        result['format'] = 'unknown'

    # Parse header fields after magic
    print(f'\nHeader fields (uint32 after magic):')
    for i in range(4, min(128, len(data)), 4):
        val_u = struct.unpack_from('<I', data, i)[0]
        val_i = struct.unpack_from('<i', data, i)[0]
        val_f = struct.unpack_from('<f', data, i)[0]
        # Show float if it looks like a coordinate (-100000 < f < 100000 and not near 0 or integer)
        float_str = ''
        if abs(val_f) > 0.001 and abs(val_f) < 100000 and val_f != float(val_i):
            float_str = f'  float={val_f:.4f}'
        print(f'  offset {i:4d} (0x{i:03x}): {val_u:10d} (0x{val_u:08x})  int={val_i:10d}{float_str}')

    # Look for sub-structures: scan for known magic bytes
    print(f'\nScanning for sub-structure magic bytes...')
    scan_patterns = {
        b'PTH': 'PTH (pathfinding)',
        b'REC': 'REC (record)',
        b'NOD': 'NOD (node)',
        b'EDG': 'EDG (edge)',
        b'CEL': 'CEL (cell)',
        b'TRI': 'TRI (triangle)',
        b'VER': 'VER (vertex)',
        b'GRI': 'GRI (grid)',
        b'NAV': 'NAV (navigation)',
        b'MSH': 'MSH (mesh)',
    }
    for pat, desc in scan_patterns.items():
        pos = 0
        hits = []
        while True:
            idx = data.find(pat, pos)
            if idx < 0:
                break
            hits.append(idx)
            pos = idx + 1
        if hits:
            print(f'  {desc}: {len(hits)} occurrences at offsets {hits[:10]}{"..." if len(hits) > 10 else ""}')

    # Analyze data patterns: look for float-heavy regions (likely vertex/coordinate data)
    print(f'\nData pattern analysis:')
    float_count = 0
    int_count = 0
    zero_count = 0
    for i in range(0, len(data) - 3, 4):
        val_u = struct.unpack_from('<I', data, i)[0]
        val_f = struct.unpack_from('<f', data, i)[0]
        if val_u == 0:
            zero_count += 1
        elif abs(val_f) > 0.001 and abs(val_f) < 100000 and not (val_f == float(int(val_f)) and abs(val_f) < 10000):
            float_count += 1
        else:
            int_count += 1
    total = float_count + int_count + zero_count
    print(f'  Float-like values: {float_count} ({100*float_count/max(total,1):.1f}%)')
    print(f'  Integer-like values: {int_count} ({100*int_count/max(total,1):.1f}%)')
    print(f'  Zero values: {zero_count} ({100*zero_count/max(total,1):.1f}%)')

    return result


def analyze_0x0b_section(data, label='0x0b'):
    """Parse and analyze REC\x02 (TQAE pathfinding) section structure."""
    print(f'\n{"="*70}')
    print(f'=== {label}: 0x0b Section Analysis (REC\\x02) ===')
    print(f'{"="*70}')
    print(f'Total size: {len(data)} bytes ({len(data)/1024:.1f} KB)')

    if len(data) < 16:
        print('  TOO SHORT to analyze')
        return {}

    # First 256 bytes hex dump
    print(f'\nFirst 256 bytes:')
    print(hex_ascii_dump(data, 0, 256))

    # Check magic bytes
    magic = data[:4]
    magic_str = ''.join(chr(b) if 32 <= b < 127 else f'\\x{b:02x}' for b in magic)
    print(f'\nMagic: {magic.hex()} = "{magic_str}"')

    result = {'size': len(data), 'magic': magic}

    if magic == b'REC\x02':
        print('  Confirmed: REC version 2')
        result['format'] = 'REC_v2'
    elif magic[:3] == b'REC':
        ver = magic[3]
        print(f'  REC version {ver}')
        result['format'] = f'REC_v{ver}'
    else:
        print(f'  NOT REC magic! Got: {magic.hex()}')
        result['format'] = 'unknown'

    # Parse header using known layout from transplant_rec02
    # Header layout (from build_section_surgery.py):
    #   [0-3]:   REC\x02 magic
    #   [4-7]:   uint32(1) constant?
    #   [8-11]:  uint32(payload_size)
    #   [12-15]: uint32 difficulty_count (N)
    #   [16..16+N*16]: N x 16-byte GUID/hash blocks
    #   [+0..+12]: Level center (3 x int32)
    #   [+12..+24]: Level dimensions (3 x uint32)
    #   [+24..]: Sub-records and mesh data
    print(f'\nParsing known REC\\x02 header layout:')
    if len(data) >= 16:
        field1 = struct.unpack_from('<I', data, 4)[0]
        payload_size = struct.unpack_from('<I', data, 8)[0]
        diff_count = struct.unpack_from('<I', data, 12)[0]
        print(f'  [4-7]   field1 (constant?): {field1} (0x{field1:08x})')
        print(f'  [8-11]  payload_size: {payload_size}')
        print(f'  [12-15] difficulty_count: {diff_count}')
        result['field1'] = field1
        result['payload_size'] = payload_size
        result['diff_count'] = diff_count

        if 1 <= diff_count <= 4:
            guid_start = 16
            for i in range(diff_count):
                off = guid_start + i * 16
                if off + 16 <= len(data):
                    guid_bytes = data[off:off + 16]
                    print(f'  GUID block {i}: {guid_bytes.hex()}')
                    result[f'guid_{i}'] = guid_bytes.hex()

            center_start = guid_start + diff_count * 16
            dims_start = center_start + 12

            if center_start + 12 <= len(data):
                cx, cy, cz = struct.unpack_from('<iii', data, center_start)
                print(f'  Center: ({cx}, {cy}, {cz})')
                result['center'] = (cx, cy, cz)

            if dims_start + 12 <= len(data):
                dx, dy, dz = struct.unpack_from('<III', data, dims_start)
                print(f'  Dimensions: ({dx}, {dy}, {dz})')
                result['dims'] = (dx, dy, dz)

            # What comes after the header?
            body_start = dims_start + 12
            if body_start < len(data):
                body_size = len(data) - body_start
                print(f'\n  Body data starts at offset {body_start}, size: {body_size} bytes')
                print(f'\n  Body first 128 bytes:')
                print(hex_ascii_dump(data, body_start, 128))

                # Scan for sub-record magics in body
                body = data[body_start:]
                for pat_name, pat_bytes in [
                    ('REC', b'REC'), ('NOD', b'NOD'), ('EDG', b'EDG'),
                    ('CEL', b'CEL'), ('TRI', b'TRI'), ('VER', b'VER'),
                    ('GRI', b'GRI'), ('NAV', b'NAV'), ('MSH', b'MSH'),
                    ('PTH', b'PTH'),
                ]:
                    pos = 0
                    hits = []
                    while True:
                        idx = body.find(pat_bytes, pos)
                        if idx < 0:
                            break
                        hits.append(body_start + idx)
                        pos = idx + 1
                    if hits:
                        print(f'  Sub-records "{pat_name}": {len(hits)} at offsets {hits[:10]}{"..." if len(hits) > 10 else ""}')

    # Parse header fields generically
    print(f'\nAll header fields (uint32):')
    for i in range(0, min(128, len(data)), 4):
        val_u = struct.unpack_from('<I', data, i)[0]
        val_i = struct.unpack_from('<i', data, i)[0]
        val_f = struct.unpack_from('<f', data, i)[0]
        float_str = ''
        if abs(val_f) > 0.001 and abs(val_f) < 100000 and val_f != float(val_i):
            float_str = f'  float={val_f:.4f}'
        print(f'  offset {i:4d} (0x{i:03x}): {val_u:10d} (0x{val_u:08x})  int={val_i:10d}{float_str}')

    # Data pattern analysis
    print(f'\nData pattern analysis:')
    float_count = 0
    int_count = 0
    zero_count = 0
    for i in range(0, len(data) - 3, 4):
        val_u = struct.unpack_from('<I', data, i)[0]
        val_f = struct.unpack_from('<f', data, i)[0]
        if val_u == 0:
            zero_count += 1
        elif abs(val_f) > 0.001 and abs(val_f) < 100000 and not (val_f == float(int(val_f)) and abs(val_f) < 10000):
            float_count += 1
        else:
            int_count += 1
    total = float_count + int_count + zero_count
    print(f'  Float-like values: {float_count} ({100*float_count/max(total,1):.1f}%)')
    print(f'  Integer-like values: {int_count} ({100*int_count/max(total,1):.1f}%)')
    print(f'  Zero values: {zero_count} ({100*zero_count/max(total,1):.1f}%)')

    return result


def deep_structure_parse_0x0a(data):
    """Attempt to parse 0x0a internal sub-record structure."""
    print(f'\n{"="*70}')
    print(f'=== Deep Structure Parse: 0x0a (PTH) ===')
    print(f'{"="*70}')

    if len(data) < 8 or data[:3] != b'PTH':
        print('  Not a PTH section')
        return

    version = data[3]
    print(f'  Version: {version}')

    # Try parsing as: magic(4) + header fields, then look for sub-records
    # Sub-records might use the same type+size framing as blob sections
    pos = 4
    print(f'\n  Scanning for type+size sub-record framing (starting at offset 4)...')

    # First check: is the next uint32 a plausible sub-record type or a count?
    if pos + 4 <= len(data):
        first_field = struct.unpack_from('<I', data, pos)[0]
        print(f'  First field after magic: {first_field} (0x{first_field:08x})')

    # Try to parse as sub-records with type(4)+size(4)+data(size) framing
    # like parse_blob_sections does
    test_pos = 4
    sub_records = []
    while test_pos + 8 <= len(data):
        st = struct.unpack_from('<I', data, test_pos)[0]
        ss = struct.unpack_from('<I', data, test_pos + 4)[0]
        if ss > len(data) - test_pos - 8 or ss > 10_000_000:
            break
        if st > 0x100:  # unlikely to be a section type
            break
        sub_records.append({'type': st, 'size': ss, 'offset': test_pos})
        test_pos += 8 + ss

    if sub_records and len(sub_records) > 1:
        print(f'  Found {len(sub_records)} sub-records with type+size framing:')
        for sr in sub_records:
            print(f'    type=0x{sr["type"]:02x}, size={sr["size"]}, offset={sr["offset"]}')
    else:
        print(f'  No type+size sub-record framing detected.')

    # Alternative: try to find repeating structures
    # Look at byte patterns after initial header
    if len(data) > 64:
        print(f'\n  Bytes 256-512 (mid-section sample):')
        mid = min(256, len(data) // 2)
        print(hex_ascii_dump(data, mid, 256))

    # Check for vertex-like float triples
    print(f'\n  Scanning for float triple patterns (potential vertices)...')
    float_triples = 0
    for i in range(4, len(data) - 11, 4):
        try:
            f1, f2, f3 = struct.unpack_from('<fff', data, i)
            if (0.1 < abs(f1) < 50000 and 0.1 < abs(f2) < 50000 and 0.1 < abs(f3) < 50000):
                float_triples += 1
        except struct.error:
            break
    print(f'  Potential float triples: {float_triples}')

    # Last 64 bytes (trailer)
    if len(data) > 64:
        print(f'\n  Last 64 bytes:')
        print(hex_ascii_dump(data, len(data) - 64, 64))


def deep_structure_parse_0x0b(data):
    """Attempt to parse 0x0b internal sub-record structure."""
    print(f'\n{"="*70}')
    print(f'=== Deep Structure Parse: 0x0b (REC) ===')
    print(f'{"="*70}')

    if len(data) < 12 or data[:3] != b'REC':
        print('  Not a REC section')
        return

    version = data[3]
    field1 = struct.unpack_from('<I', data, 4)[0]
    payload_size = struct.unpack_from('<I', data, 8)[0]
    diff_count = struct.unpack_from('<I', data, 12)[0]

    print(f'  Version: {version}')
    print(f'  Field1: {field1}')
    print(f'  Payload size: {payload_size} (actual remaining: {len(data) - 12})')
    print(f'  Difficulty count: {diff_count}')

    if diff_count < 1 or diff_count > 4:
        print(f'  WARNING: unusual difficulty count, clamping to 3')
        diff_count = 3

    guid_start = 16
    center_start = guid_start + diff_count * 16
    dims_start = center_start + 12
    body_start = dims_start + 12

    print(f'  Header ends at offset: {body_start}')

    if body_start >= len(data):
        print(f'  No body data!')
        return

    body = data[body_start:]
    print(f'  Body size: {len(body)} bytes')

    # Try to parse body as sub-records
    pos = 0
    sub_records = []
    while pos + 8 <= len(body):
        # Check if next 4 bytes look like a magic string
        potential_magic = body[pos:pos + 4]
        if any(32 <= b < 127 for b in potential_magic[:3]):
            # Could be a named sub-record
            magic_str = ''.join(chr(b) if 32 <= b < 127 else f'\\x{b:02x}' for b in potential_magic)

            # Try various size field positions
            for size_offset in [4, 8]:
                if pos + size_offset + 4 <= len(body):
                    potential_size = struct.unpack_from('<I', body, pos + size_offset)[0]
                    if 0 < potential_size < len(body) - pos:
                        sub_records.append({
                            'magic': magic_str,
                            'offset': body_start + pos,
                            'size_offset': size_offset,
                            'size': potential_size,
                        })
            break  # Just check first potential sub-record
        else:
            break

    if sub_records:
        print(f'\n  Potential sub-records at body start:')
        for sr in sub_records:
            print(f'    magic="{sr["magic"]}", offset={sr["offset"]}, size_off={sr["size_offset"]}, size={sr["size"]}')

    # Sample body data
    print(f'\n  Body bytes 0-128:')
    print(hex_ascii_dump(data, body_start, 128))

    if len(body) > 256:
        mid = len(body) // 2
        print(f'\n  Body bytes {mid}-{mid+128} (midpoint):')
        print(hex_ascii_dump(data, body_start + mid, 128))

    # Scan for vertex triples
    print(f'\n  Scanning for float triple patterns (potential vertices)...')
    float_triples = 0
    for i in range(0, len(body) - 11, 4):
        try:
            f1, f2, f3 = struct.unpack_from('<fff', body, i)
            if (0.1 < abs(f1) < 50000 and 0.1 < abs(f2) < 50000 and 0.1 < abs(f3) < 50000):
                float_triples += 1
        except struct.error:
            break
    print(f'  Potential float triples: {float_triples}')

    # Last 64 bytes
    print(f'\n  Last 64 bytes:')
    print(hex_ascii_dump(data, len(data) - 64, 64))


def main():
    sv_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
    svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')

    print('Loading SV archive...')
    sv_arc = ArcArchive.from_file(sv_arc_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    sv_sec = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])
    print(f'  SV: {len(sv_levels)} levels')

    print('Loading SVAERA archive...')
    ae_arc = ArcArchive.from_file(svaera_arc_path)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
    print(f'  SVAERA: {len(ae_levels)} levels')

    # Build name lookups
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}
    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}

    # ========================================================
    # PRIMARY ANALYSIS: RuinedCity02 (idx 30 in SVAERA)
    # ========================================================
    print(f'\n{"#"*70}')
    print(f'# PRIMARY ANALYSIS: RuinedCity02 (SVAERA idx 30)')
    print(f'{"#"*70}')

    ae_lv = ae_levels[30]
    ae_key = ae_lv['fname'].replace('\\', '/').lower()
    sv_idx = sv_by_name.get(ae_key)

    if sv_idx is None:
        print(f'ERROR: RuinedCity02 not found in SV by name: {ae_key}')
        return

    sv_lv = sv_levels[sv_idx]
    print(f'  SVAERA: idx={30}, fname={ae_lv["fname"]}')
    print(f'  SV:     idx={sv_idx}, fname={sv_lv["fname"]}')

    # Extract blobs
    ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
    sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]

    print(f'\n  SVAERA blob: {len(ae_blob)} bytes, magic: {ae_blob[:4].hex()} (LVL v0x{ae_blob[3]:02x})')
    print(f'  SV blob:     {len(sv_blob)} bytes, magic: {sv_blob[:4].hex()} (LVL v0x{sv_blob[3]:02x})')

    # Parse sections
    ae_secs, ae_magic = parse_blob_sections(ae_blob)
    sv_secs, sv_magic = parse_blob_sections(sv_blob)

    print(f'\n  SVAERA sections:')
    for s in ae_secs:
        print(f'    type=0x{s["type"]:02x}, size={s["size"]:8d} bytes')
    print(f'\n  SV sections:')
    for s in sv_secs:
        print(f'    type=0x{s["type"]:02x}, size={s["size"]:8d} bytes')

    # Extract pathfinding sections
    sv_0a = [s for s in sv_secs if s['type'] == 0x0a]
    ae_0b = [s for s in ae_secs if s['type'] == 0x0b]
    sv_0b = [s for s in sv_secs if s['type'] == 0x0b]
    ae_0a = [s for s in ae_secs if s['type'] == 0x0a]

    print(f'\n  SV has 0x0a: {len(sv_0a) > 0} ({len(sv_0a[0]["data"])} bytes)' if sv_0a else '\n  SV has 0x0a: False')
    print(f'  SV has 0x0b: {len(sv_0b) > 0}')
    print(f'  SVAERA has 0x0a: {len(ae_0a) > 0}')
    print(f'  SVAERA has 0x0b: {len(ae_0b) > 0} ({len(ae_0b[0]["data"])} bytes)' if ae_0b else '  SVAERA has 0x0b: False')

    # Deep analysis of each
    if sv_0a:
        info_0a = analyze_0x0a_section(sv_0a[0]['data'], f'SV RuinedCity02')
        deep_structure_parse_0x0a(sv_0a[0]['data'])

    if ae_0b:
        info_0b = analyze_0x0b_section(ae_0b[0]['data'], f'SVAERA RuinedCity02')
        deep_structure_parse_0x0b(ae_0b[0]['data'])

    # ========================================================
    # COMPARISON
    # ========================================================
    print(f'\n{"#"*70}')
    print(f'# HEADER STRUCTURE COMPARISON')
    print(f'{"#"*70}')

    if sv_0a and ae_0b:
        d0a = sv_0a[0]['data']
        d0b = ae_0b[0]['data']

        print(f'\n  0x0a size: {len(d0a)} bytes')
        print(f'  0x0b size: {len(d0b)} bytes')
        print(f'  Size ratio (0x0b / 0x0a): {len(d0b) / max(len(d0a), 1):.4f}')
        print(f'  Size difference: {len(d0b) - len(d0a):+d} bytes')

        # Compare first 64 bytes side by side
        print(f'\n  First 64 bytes side-by-side:')
        print(f'  {"Offset":>8s}  {"0x0a (SV)":>48s}  {"0x0b (SVAERA)":>48s}')
        for i in range(0, 64, 16):
            chunk_a = d0a[i:min(i + 16, len(d0a))]
            chunk_b = d0b[i:min(i + 16, len(d0b))]
            hex_a = ' '.join(f'{b:02x}' for b in chunk_a)
            hex_b = ' '.join(f'{b:02x}' for b in chunk_b)
            match = 'SAME' if chunk_a == chunk_b else 'DIFF'
            print(f'  {i:08x}: {hex_a:<48s}  {hex_b:<48s}  [{match}]')

        # Check if one could be a simple re-header of the other
        # Test: skip headers and compare body data
        print(f'\n  Re-header feasibility test:')

        # 0x0a: magic(4) + ???
        # 0x0b: magic(4) + field1(4) + payload_size(4) + diff_count(4) + N*16 guid + center(12) + dims(12)
        if len(d0b) >= 16:
            diff_count = struct.unpack_from('<I', d0b, 12)[0]
            if diff_count < 1 or diff_count > 4:
                diff_count = 3
            body_0b_start = 16 + diff_count * 16 + 12 + 12
            print(f'  0x0b body starts at offset: {body_0b_start}')
            print(f'  0x0b body size: {len(d0b) - body_0b_start}')

        # Try various header sizes for 0x0a and see if body matches
        for hdr_a in [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 48, 52, 56, 60, 64, 68, 72, 76, 80]:
            if hdr_a >= len(d0a):
                break
            body_a = d0a[hdr_a:]
            # Compare with 0x0b body
            if len(d0b) > body_0b_start:
                body_b = d0b[body_0b_start:]
                if len(body_a) == len(body_b):
                    if body_a == body_b:
                        print(f'  ** MATCH at 0x0a header={hdr_a}, 0x0b header={body_0b_start}: BODIES IDENTICAL **')
                    else:
                        # Count matching bytes
                        matching = sum(1 for a, b in zip(body_a, body_b) if a == b)
                        print(f'  Header {hdr_a}/{body_0b_start}: same body size ({len(body_a)}), matching: {matching}/{len(body_a)} ({100*matching/len(body_a):.1f}%)')
                elif abs(len(body_a) - len(body_b)) < 100:
                    print(f'  Header {hdr_a}/{body_0b_start}: body size close ({len(body_a)} vs {len(body_b)}, delta={len(body_b)-len(body_a):+d})')

        # Binary content comparison: what fraction of 0x0a bytes appear in 0x0b?
        print(f'\n  Structural similarity:')

        # Check if 0x0a body appears as a substring anywhere in 0x0b
        # (test with a 64-byte sample from middle of 0x0a)
        if len(d0a) > 128:
            mid = len(d0a) // 2
            sample = d0a[mid:mid + 64]
            found = d0b.find(sample)
            if found >= 0:
                print(f'  64-byte sample from 0x0a midpoint found in 0x0b at offset {found}')
                print(f'  Offset difference: {found - mid}')
            else:
                print(f'  64-byte sample from 0x0a midpoint NOT found in 0x0b')

        # Check 32-byte samples at various positions
        sample_hits = 0
        sample_total = 0
        for frac in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            pos_a = int(len(d0a) * frac)
            if pos_a + 32 > len(d0a):
                continue
            sample = d0a[pos_a:pos_a + 32]
            sample_total += 1
            if d0b.find(sample) >= 0:
                sample_hits += 1
        print(f'  32-byte samples from 0x0a found in 0x0b: {sample_hits}/{sample_total}')

    # ========================================================
    # MULTI-LEVEL SIZE RATIO ANALYSIS
    # ========================================================
    print(f'\n{"#"*70}')
    print(f'# MULTI-LEVEL SIZE RATIO ANALYSIS')
    print(f'{"#"*70}')

    # Find all shared levels that have both 0x0a (SV) and 0x0b (SVAERA)
    size_ratios = []
    level_data = []

    for ae_idx, ae_lv_i in enumerate(ae_levels):
        ae_key_i = ae_lv_i['fname'].replace('\\', '/').lower()
        sv_idx_i = sv_by_name.get(ae_key_i)
        if sv_idx_i is None:
            continue

        sv_lv_i = sv_levels[sv_idx_i]
        ae_blob_i = ae_data[ae_lv_i['data_offset']:ae_lv_i['data_offset'] + ae_lv_i['data_length']]
        sv_blob_i = sv_data[sv_lv_i['data_offset']:sv_lv_i['data_offset'] + sv_lv_i['data_length']]

        ae_secs_i, _ = parse_blob_sections(ae_blob_i)
        sv_secs_i, _ = parse_blob_sections(sv_blob_i)

        sv_0a_i = [s for s in sv_secs_i if s['type'] == 0x0a]
        ae_0b_i = [s for s in ae_secs_i if s['type'] == 0x0b]

        if sv_0a_i and ae_0b_i:
            size_a = len(sv_0a_i[0]['data'])
            size_b = len(ae_0b_i[0]['data'])
            if size_a > 0:
                ratio = size_b / size_a
                # Get level dimensions from ints_raw for context
                ae_ints = struct.unpack_from('<13i', ae_lv_i['ints_raw'], 0)
                sv_ints = struct.unpack_from('<13i', sv_lv_i['ints_raw'], 0)

                size_ratios.append(ratio)
                level_data.append({
                    'name': ae_lv_i['fname'],
                    'ae_idx': ae_idx,
                    'size_0a': size_a,
                    'size_0b': size_b,
                    'ratio': ratio,
                    'ae_dims': (ae_ints[3], ae_ints[4], ae_ints[5]),
                    'sv_dims': (sv_ints[3], sv_ints[4], sv_ints[5]),
                    'ae_magic_0a': sv_0a_i[0]['data'][:4].hex(),
                    'ae_magic_0b': ae_0b_i[0]['data'][:4].hex(),
                })

    if not size_ratios:
        print('  No shared levels with both 0x0a and 0x0b found!')
    else:
        print(f'\n  Found {len(size_ratios)} shared levels with both 0x0a (SV) and 0x0b (SVAERA)')

        # Sort by ratio
        level_data.sort(key=lambda x: x['ratio'])

        print(f'\n  {"Level Name":<55s}  {"0x0a":>8s}  {"0x0b":>8s}  {"Ratio":>8s}  {"AE dims":>20s}  {"SV dims":>20s}')
        print(f'  {"-"*55}  {"-"*8}  {"-"*8}  {"-"*8}  {"-"*20}  {"-"*20}')
        for ld in level_data[:30]:
            name = ld['name'][-50:]
            print(f'  {name:<55s}  {ld["size_0a"]:>8d}  {ld["size_0b"]:>8d}  {ld["ratio"]:>8.4f}  {str(ld["ae_dims"]):>20s}  {str(ld["sv_dims"]):>20s}')

        if len(level_data) > 30:
            print(f'  ... ({len(level_data) - 30} more levels)')
            print(f'\n  Last 10 (largest ratios):')
            for ld in level_data[-10:]:
                name = ld['name'][-50:]
                print(f'  {name:<55s}  {ld["size_0a"]:>8d}  {ld["size_0b"]:>8d}  {ld["ratio"]:>8.4f}  {str(ld["ae_dims"]):>20s}  {str(ld["sv_dims"]):>20s}')

        # Statistics
        print(f'\n  Size ratio statistics (0x0b / 0x0a):')
        print(f'    Min:    {min(size_ratios):.4f}')
        print(f'    Max:    {max(size_ratios):.4f}')
        print(f'    Mean:   {sum(size_ratios)/len(size_ratios):.4f}')
        sorted_ratios = sorted(size_ratios)
        median = sorted_ratios[len(sorted_ratios) // 2]
        print(f'    Median: {median:.4f}')
        stddev = (sum((r - sum(size_ratios)/len(size_ratios))**2 for r in size_ratios) / len(size_ratios)) ** 0.5
        print(f'    StdDev: {stddev:.4f}')

        # Check consistency
        if max(size_ratios) - min(size_ratios) < 0.01:
            print(f'\n  ** SIZE RATIO IS VERY CONSISTENT -- suggests simple re-encoding **')
        elif stddev < 0.1:
            print(f'\n  ** SIZE RATIO IS FAIRLY CONSISTENT (low stddev) **')
        else:
            print(f'\n  ** SIZE RATIO VARIES SIGNIFICANTLY -- suggests different data structures **')

    # ========================================================
    # ADDITIONAL: Check a few specific shared levels in detail
    # ========================================================
    print(f'\n{"#"*70}')
    print(f'# ADDITIONAL LEVEL SPOT-CHECKS')
    print(f'{"#"*70}')

    # Pick 3 more levels from level_data (smallest, median, largest ratio)
    if len(level_data) >= 3:
        spot_checks = [
            level_data[0],  # smallest ratio
            level_data[len(level_data) // 2],  # median ratio
            level_data[-1],  # largest ratio
        ]
    elif level_data:
        spot_checks = level_data[:3]
    else:
        spot_checks = []

    for ld in spot_checks:
        ae_lv_sc = ae_levels[ld['ae_idx']]
        ae_key_sc = ae_lv_sc['fname'].replace('\\', '/').lower()
        sv_idx_sc = sv_by_name.get(ae_key_sc)
        sv_lv_sc = sv_levels[sv_idx_sc]

        ae_blob_sc = ae_data[ae_lv_sc['data_offset']:ae_lv_sc['data_offset'] + ae_lv_sc['data_length']]
        sv_blob_sc = sv_data[sv_lv_sc['data_offset']:sv_lv_sc['data_offset'] + sv_lv_sc['data_length']]

        ae_secs_sc, _ = parse_blob_sections(ae_blob_sc)
        sv_secs_sc, _ = parse_blob_sections(sv_blob_sc)

        sv_0a_sc = [s for s in sv_secs_sc if s['type'] == 0x0a][0]['data']
        ae_0b_sc = [s for s in ae_secs_sc if s['type'] == 0x0b][0]['data']

        print(f'\n  --- Spot check: {ld["name"]} (ratio={ld["ratio"]:.4f}) ---')
        print(f'  0x0a magic: {sv_0a_sc[:4].hex()}')
        print(f'  0x0b magic: {ae_0b_sc[:4].hex()}')
        print(f'  0x0a size: {len(sv_0a_sc)}, 0x0b size: {len(ae_0b_sc)}')

        # Compare header structure
        if ae_0b_sc[:4] == b'REC\x02' and len(ae_0b_sc) >= 16:
            dc = struct.unpack_from('<I', ae_0b_sc, 12)[0]
            if dc < 1 or dc > 4:
                dc = 3
            body_start_sc = 16 + dc * 16 + 12 + 12
            print(f'  0x0b header size: {body_start_sc}, body size: {len(ae_0b_sc) - body_start_sc}')

        # First 64 bytes of each
        print(f'  0x0a first 64 bytes:')
        print(hex_ascii_dump(sv_0a_sc, 0, 64, '    '))
        print(f'  0x0b first 64 bytes:')
        print(hex_ascii_dump(ae_0b_sc, 0, 64, '    '))

    # ========================================================
    # FINAL ASSESSMENT
    # ========================================================
    print(f'\n{"#"*70}')
    print(f'# FINAL ASSESSMENT')
    print(f'{"#"*70}')

    if sv_0a and ae_0b:
        d0a = sv_0a[0]['data']
        d0b = ae_0b[0]['data']

        print(f'\n  0x0a (PTH\\x04) magic: {d0a[:4].hex()}')
        print(f'  0x0b (REC\\x02) magic: {d0b[:4].hex()}')
        print(f'  Different magic bytes: {"YES" if d0a[:4] != d0b[:4] else "NO"}')
        print(f'  Different sizes: {"YES" if len(d0a) != len(d0b) else "NO"} ({len(d0a)} vs {len(d0b)})')

        # Check if one is a prefix/suffix of the other
        min_len = min(len(d0a), len(d0b))
        matching_prefix = 0
        for i in range(min_len):
            if d0a[i] == d0b[i]:
                matching_prefix += 1
            else:
                break
        print(f'  Matching prefix bytes: {matching_prefix}')

        matching_suffix = 0
        for i in range(1, min_len + 1):
            if d0a[-i] == d0b[-i]:
                matching_suffix += 1
            else:
                break
        print(f'  Matching suffix bytes: {matching_suffix}')

        # Byte-level similarity
        if len(d0a) == len(d0b):
            matching = sum(1 for a, b in zip(d0a, d0b) if a == b)
            print(f'  Byte-level match (same length): {matching}/{len(d0a)} ({100*matching/len(d0a):.1f}%)')
        else:
            # Compare overlapping portion
            overlap = min(len(d0a), len(d0b))
            matching = sum(1 for a, b in zip(d0a[:overlap], d0b[:overlap]) if a == b)
            print(f'  Byte-level match (first {overlap} bytes): {matching}/{overlap} ({100*matching/overlap:.1f}%)')

    print(f'\n  Conversion feasibility:')
    if size_ratios:
        if max(size_ratios) - min(size_ratios) < 0.01:
            print(f'  LIKELY FEASIBLE: Consistent size ratios suggest systematic transformation')
        elif stddev < 0.1:
            print(f'  POSSIBLY FEASIBLE: Ratios vary but are correlated with level size')
        else:
            print(f'  UNLIKELY FEASIBLE AS SIMPLE RE-HEADER: Ratios vary widely ({min(size_ratios):.4f} to {max(size_ratios):.4f})')
            print(f'  The data structures appear fundamentally different.')
            print(f'  0x0a (PTH\\x04) and 0x0b (REC\\x02) likely encode pathfinding in different ways.')

    print(f'\nDone.')


if __name__ == '__main__':
    main()
