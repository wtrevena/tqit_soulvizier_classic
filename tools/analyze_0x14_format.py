#!/usr/bin/env python3
"""
Analyze section 0x14 (AE-specific data) and its relationship to section 0x05.
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

svaera_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')


def parse_blob_sections(blob):
    sections = []
    if len(blob) < 4:
        return sections, b''
    magic = blob[:4]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections, magic


def hex_dump(data, max_bytes=128, offset=0):
    lines = []
    for i in range(0, min(len(data), max_bytes), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'  {offset+i:04x}: {hex_part:<48s}  {ascii_part}')
    if len(data) > max_bytes:
        lines.append(f'  ... ({len(data) - max_bytes} more bytes)')
    return '\n'.join(lines)


def parse_0x05_strings(data):
    """Parse section 0x05 as a flat list of length-prefixed strings."""
    if len(data) < 4:
        return []
    count = struct.unpack_from('<I', data, 0)[0]
    strings = []
    pos = 4
    for _ in range(count):
        if pos + 4 > len(data):
            break
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        if pos + slen > len(data):
            break
        s = data[pos:pos + slen].decode('ascii', errors='replace')
        strings.append(s)
        pos += slen
    return strings


def analyze_0x14_section(data, obj_count):
    """Analyze section 0x14 structure and its relationship to 0x05 count."""
    print(f'  0x14 section: {len(data)} bytes')
    if len(data) == 0:
        print(f'  Empty')
        return

    print(f'  0x05 has {obj_count} objects')

    # Check if size is a multiple of obj_count
    if obj_count > 0:
        bytes_per_obj = len(data) / obj_count
        print(f'  Bytes per object (if parallel array): {bytes_per_obj:.2f}')

        # Check common record sizes
        for stride in [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80]:
            if len(data) == stride * obj_count:
                print(f'  EXACT MATCH: {stride} bytes per object * {obj_count} objects = {len(data)} bytes')
            elif len(data) == 4 + stride * obj_count:
                print(f'  MATCH WITH HEADER: 4 + {stride} bytes per object * {obj_count} objects = {4 + stride * obj_count} bytes')

    # Check if it starts with a count
    first_uint = struct.unpack_from('<I', data, 0)[0]
    print(f'  First uint32: {first_uint} (0x{first_uint:08x})')

    if first_uint == obj_count:
        print(f'  ** First uint32 MATCHES 0x05 object count! **')

    # Show first 256 bytes
    print(f'  First 256 bytes:')
    print(hex_dump(data, 256))

    # Try to detect record structure if it's a parallel array
    if obj_count > 0 and len(data) >= 4:
        # If first uint is a count, try parsing records after it
        if first_uint == obj_count and len(data) > 4:
            remaining = len(data) - 4
            stride = remaining // obj_count if obj_count > 0 else 0
            print(f'\n  With {first_uint} as count: {remaining} remaining bytes, {stride} bytes/record')
            if stride > 0 and remaining == stride * obj_count:
                print(f'  Records are fixed-size: {stride} bytes each')
                for i in range(min(3, obj_count)):
                    rec_off = 4 + i * stride
                    print(f'  Record {i}:')
                    print(hex_dump(data[rec_off:rec_off + stride], stride, rec_off))
                    # Try as floats
                    nf = stride // 4
                    floats = [struct.unpack_from('<f', data, rec_off + j*4)[0] for j in range(nf)]
                    ints = [struct.unpack_from('<I', data, rec_off + j*4)[0] for j in range(nf)]
                    print(f'    floats: {floats}')
                    print(f'    ints:   {ints}')


def main():
    print('Loading SVAERA map...')
    ae_arc = ArcArchive.from_file(svaera_arc)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])

    # Analyze several levels
    targets = [
        'levels/world/greece/delphi/delphilowlands04.lvl',
        'levels/world/greece/delphi/delphilowlands03.lvl',
        'levels/world/greece/delphi/delphilowlands02.lvl',
    ]

    for target in targets:
        ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}
        if target not in ae_by_name:
            continue

        ae_lv = ae_levels[ae_by_name[target]]
        ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
        ae_secs, ae_magic = parse_blob_sections(ae_blob)

        print(f'\n{"="*60}')
        print(f'  {target}')
        print(f'{"="*60}')

        ae_05 = [s for s in ae_secs if s['type'] == 0x05]
        ae_14 = [s for s in ae_secs if s['type'] == 0x14]

        obj_count = 0
        if ae_05:
            strings = parse_0x05_strings(ae_05[0]['data'])
            obj_count = len(strings)
            print(f'\n  0x05: {len(ae_05[0]["data"])} bytes, {obj_count} objects')
            for i, s in enumerate(strings[:5]):
                print(f'    [{i}] {s}')
            if len(strings) > 5:
                print(f'    ... ({len(strings) - 5} more)')

        if ae_14:
            print()
            analyze_0x14_section(ae_14[0]['data'], obj_count)

    del ae_data


if __name__ == '__main__':
    main()
