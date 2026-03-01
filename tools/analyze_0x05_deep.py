#!/usr/bin/env python3
"""
Deep analysis of 0x05 section format: find where strings end and what follows.
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
        return sections
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections


def parse_0x05_full(data, label):
    """Parse 0x05 section fully - strings then trailing data."""
    if len(data) < 4:
        return
    count = struct.unpack_from('<I', data, 0)[0]
    print(f'\n  [{label}] 0x05: {len(data)} bytes, count={count}')

    # Parse all strings
    pos = 4
    strings = []
    for i in range(count):
        if pos + 4 > len(data):
            print(f'    EOF reading string {i} length at pos {pos}')
            break
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        if pos + slen > len(data):
            print(f'    EOF reading string {i} data at pos {pos}, need {slen}')
            break
        s = data[pos:pos + slen].decode('ascii', errors='replace')
        strings.append(s)
        pos += slen

    string_block_end = pos
    trailing_size = len(data) - string_block_end
    print(f'    String block: offset 4 to {string_block_end} ({string_block_end - 4} bytes)')
    print(f'    Trailing data: offset {string_block_end} to {len(data)} ({trailing_size} bytes)')

    if trailing_size > 0:
        trailing_per_obj = trailing_size / count if count > 0 else 0
        print(f'    Trailing bytes per object: {trailing_per_obj:.2f}')

        # Try to detect fixed-size records
        for stride in range(4, 300, 4):
            if trailing_size == stride * count:
                print(f'    ** EXACT MATCH: {stride} bytes/object x {count} objects = {trailing_size} **')

        # Show first few records of trailing data
        print(f'\n    First 256 bytes of trailing data:')
        td = data[string_block_end:]
        for i in range(0, min(len(td), 256), 16):
            chunk = td[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            print(f'      {i:04x}: {hex_part:<48s}  {ascii_part}')

        # Try as float/int records
        print(f'\n    First 5 "records" as floats (assuming {trailing_size // count if count > 0 else 0} bytes each):')
        stride = trailing_size // count if count > 0 else 0
        if stride >= 4 and stride == trailing_size / count:
            for r in range(min(5, count)):
                off = r * stride
                nf = stride // 4
                vals = []
                for fi in range(nf):
                    fv = struct.unpack_from('<f', td, off + fi * 4)[0]
                    iv = struct.unpack_from('<I', td, off + fi * 4)[0]
                    if abs(fv) < 100000 and abs(fv) > 0.0001:
                        vals.append(f'{fv:.4f}')
                    else:
                        vals.append(f'0x{iv:08x}')
                print(f'      [{r}] ({strings[r][:50]}...)')
                print(f'          {vals}')

    return strings, data[string_block_end:]


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

    targets = [
        'levels/world/greece/delphi/delphilowlands04.lvl',
        'levels/world/greece/delphi/delphilowlands03.lvl',
    ]

    for target in targets:
        print(f'\n{"="*70}')
        print(f'  {target}')
        print(f'{"="*70}')

        if target in ae_by_name:
            ae_lv = ae_levels[ae_by_name[target]]
            ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
            ae_secs = parse_blob_sections(ae_blob)
            ae_05 = [s for s in ae_secs if s['type'] == 0x05]
            if ae_05:
                parse_0x05_full(ae_05[0]['data'], 'SVAERA')

        if target in sv_by_name:
            sv_lv = sv_levels[sv_by_name[target]]
            sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
            sv_secs = parse_blob_sections(sv_blob)
            sv_05 = [s for s in sv_secs if s['type'] == 0x05]
            if sv_05:
                parse_0x05_full(sv_05[0]['data'], 'SV')

    del ae_data, sv_data


if __name__ == '__main__':
    main()
