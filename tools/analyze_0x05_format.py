#!/usr/bin/env python3
"""
Deep-analyze section 0x05 (object placements) format differences between
LVL v0x0e (SV/TQIT) and v0x11 (SVAERA/AE) for shared levels with drxmap.
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

svaera_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')


def parse_blob_sections(blob):
    sections = []
    if len(blob) < 4:
        return sections, blob[:4] if len(blob) >= 4 else b''
    magic = blob[:4]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'offset': pos + 8, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections, magic


def hex_dump(data, max_bytes=128):
    lines = []
    for i in range(0, min(len(data), max_bytes), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'  {i:04x}: {hex_part:<48s}  {ascii_part}')
    if len(data) > max_bytes:
        lines.append(f'  ... ({len(data) - max_bytes} more bytes)')
    return '\n'.join(lines)


def analyze_0x05_section(data, label):
    """Try to parse the 0x05 section as object placement records."""
    pos = 0
    print(f'\n  [{label}] 0x05 section: {len(data)} bytes')
    print(f'  First 128 bytes:')
    print(hex_dump(data, 128))

    if len(data) < 4:
        print(f'  Too small to parse')
        return

    # Try to detect the structure
    # Common pattern: uint32 count, then records
    val0 = struct.unpack_from('<I', data, 0)[0]
    print(f'\n  First uint32: {val0} (0x{val0:08x})')

    if val0 > 10000 or val0 == 0:
        print(f'  Does not look like a simple count, trying other interpretations...')
        # Maybe it starts with some header
        for i in range(0, min(32, len(data) - 3), 4):
            v = struct.unpack_from('<I', data, i)[0]
            print(f'    offset {i}: {v} (0x{v:08x})')
        return

    # Assume val0 is a record count, try to parse records
    print(f'  Interpreting as {val0} records...')
    pos = 4
    for rec_idx in range(min(val0, 5)):  # Show first 5 records
        if pos + 4 > len(data):
            print(f'  Record {rec_idx}: EOF at {pos}')
            break

        # Try to detect record structure
        # Records likely have: string (DBR path), position (x,y,z floats), rotation, etc.
        rec_start = pos
        print(f'\n  Record {rec_idx} at offset {pos}:')
        print(hex_dump(data[pos:pos+64], 64))

        # Try: length-prefixed string
        slen = struct.unpack_from('<I', data, pos)[0]
        if 0 < slen < 1000:
            try:
                s = data[pos+4:pos+4+slen].decode('ascii', errors='replace')
                print(f'    String ({slen} chars): {s}')
                pos += 4 + slen
                # Read what follows the string
                remaining = min(48, len(data) - pos)
                if remaining > 0:
                    print(f'    After string ({remaining} bytes):')
                    print(hex_dump(data[pos:pos+remaining], remaining))
                    # Try to read as floats
                    nfloats = remaining // 4
                    floats = []
                    for fi in range(min(nfloats, 12)):
                        fv = struct.unpack_from('<f', data, pos + fi * 4)[0]
                        floats.append(fv)
                    print(f'    As floats: {floats}')
            except:
                pass
        else:
            # Not a string, try as floats/ints
            nvals = min(8, (len(data) - pos) // 4)
            ints = [struct.unpack_from('<I', data, pos + i*4)[0] for i in range(nvals)]
            floats = [struct.unpack_from('<f', data, pos + i*4)[0] for i in range(nvals)]
            print(f'    As uint32: {ints}')
            print(f'    As float:  {floats}')

        # Don't advance further since we don't know record size
        break


def main():
    print('Loading maps...')
    ae_arc = ArcArchive.from_file(svaera_arc)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}

    sv_arc_obj = ArcArchive.from_file(sv_arc)
    sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
    sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}

    # Focus on DelphiLowlands04 - the crash level
    target = 'levels/world/greece/delphi/delphilowlands04.lvl'

    print(f'\n=== Analyzing: {target} ===')

    if target in ae_by_name:
        ae_lv = ae_levels[ae_by_name[target]]
        ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
        ae_secs, ae_magic = parse_blob_sections(ae_blob)
        magic_ver = struct.unpack_from('<I', ae_magic, 0)[0]
        print(f'\n  SVAERA: magic=0x{magic_ver:08x}, {len(ae_secs)} sections, {len(ae_blob)} bytes')
        for i, s in enumerate(ae_secs):
            drx = b'drxmap' in s['data']
            print(f'    [{i}] type=0x{s["type"]:02x} size={s["size"]:>8}' + (' *** HAS drxmap ***' if drx else ''))

        ae_05 = [s for s in ae_secs if s['type'] == 0x05]
        if ae_05:
            analyze_0x05_section(ae_05[0]['data'], 'SVAERA')

    if target in sv_by_name:
        sv_lv = sv_levels[sv_by_name[target]]
        sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
        sv_secs, sv_magic = parse_blob_sections(sv_blob)
        magic_ver = struct.unpack_from('<I', sv_magic, 0)[0]
        print(f'\n  SV: magic=0x{magic_ver:08x}, {len(sv_secs)} sections, {len(sv_blob)} bytes')
        for i, s in enumerate(sv_secs):
            drx = b'drxmap' in s['data']
            print(f'    [{i}] type=0x{s["type"]:02x} size={s["size"]:>8}' + (' *** HAS drxmap ***' if drx else ''))

        sv_05 = [s for s in sv_secs if s['type'] == 0x05]
        if sv_05:
            analyze_0x05_section(sv_05[0]['data'], 'SV')

    # Also compare all section types between versions
    print('\n\n=== Section type comparison across all 9 shared drxmap levels ===')
    for sv_lv in sv_levels:
        key = sv_lv['fname'].replace('\\', '/').lower()
        sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
        if b'drxmap' not in sv_blob:
            continue
        if key not in ae_by_name:
            continue

        ae_lv = ae_levels[ae_by_name[key]]
        ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]

        ae_secs, ae_magic = parse_blob_sections(ae_blob)
        sv_secs, sv_magic = parse_blob_sections(sv_blob)

        ae_types = [s['type'] for s in ae_secs]
        sv_types = [s['type'] for s in sv_secs]

        ae_ver = struct.unpack_from('<I', ae_magic, 0)[0]
        sv_ver = struct.unpack_from('<I', sv_magic, 0)[0]

        ae_05_size = sum(s['size'] for s in ae_secs if s['type'] == 0x05)
        sv_05_size = sum(s['size'] for s in sv_secs if s['type'] == 0x05)

        print(f'\n  {sv_lv["fname"]}')
        print(f'    SVAERA: ver=0x{ae_ver:08x}, sections={ae_types}')
        print(f'    SV:     ver=0x{sv_ver:08x}, sections={sv_types}')
        print(f'    0x05 size: SVAERA={ae_05_size}, SV={sv_05_size}')

        # Check if 0x05 format looks the same
        ae_05 = [s for s in ae_secs if s['type'] == 0x05]
        sv_05 = [s for s in sv_secs if s['type'] == 0x05]
        if ae_05 and sv_05:
            ae_first4 = struct.unpack_from('<I', ae_05[0]['data'], 0)[0] if len(ae_05[0]['data']) >= 4 else -1
            sv_first4 = struct.unpack_from('<I', sv_05[0]['data'], 0)[0] if len(sv_05[0]['data']) >= 4 else -1
            print(f'    0x05 first uint32: SVAERA={ae_first4}, SV={sv_first4}')

    del ae_data, sv_data


if __name__ == '__main__':
    main()
