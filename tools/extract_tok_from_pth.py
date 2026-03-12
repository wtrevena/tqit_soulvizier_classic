"""
Extract PathEngine TOK mesh data from a level's 0x0a (PTH\x04) section.

The PTH section contains:
  - 4 bytes: magic "PTH\x04"
  - 4 bytes: version (little-endian uint32)
  - 4 bytes: payload_size (little-endian uint32)
  - GUID block: diff_count (uint32) + N * 16 bytes
  - Spatial params: center_x, center_y, center_z (3 * int32) + dim_x, dim_y, dim_z (3 * uint32)
  - The rest is PathEngine TOK format mesh data

Usage:
  py tools/extract_tok_from_pth.py <level.lvl> <output.tok>
  py tools/extract_tok_from_pth.py  (defaults to SV RuinedCity02)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_section_surgery import parse_blob_sections

REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')


def extract_tok(lvl_path, out_path=None):
    blob = Path(lvl_path).read_bytes()
    secs, _ = parse_blob_sections(blob)

    sec_types = [s['type'] for s in secs]
    print(f'Level: {lvl_path}')
    print(f'Size: {len(blob):,} bytes')
    print(f'Version byte: 0x{blob[3]:02x}')
    print(f'Sections: {["0x%02x" % t for t in sec_types]}')

    # Find 0x0a section
    pth_sec = None
    for s in secs:
        if s['type'] == 0x0a:
            pth_sec = s
            break

    if not pth_sec:
        print('ERROR: No 0x0a (PTH) section found')
        return None

    data = pth_sec['data']
    print(f'\nPTH section: {len(data):,} bytes')

    # Parse PTH header
    off = 0
    magic = data[off:off+4]
    off += 4
    print(f'Magic: {magic}')

    if magic[:3] != b'PTH':
        print('ERROR: Bad PTH magic')
        return None

    version = struct.unpack_from('<I', data, off)[0]
    off += 4
    print(f'Version: {version}')

    payload_size = struct.unpack_from('<I', data, off)[0]
    off += 4
    print(f'Payload size: {payload_size}')

    # GUID block
    diff_count = struct.unpack_from('<I', data, off)[0]
    off += 4
    print(f'GUID diff_count: {diff_count}')

    guids = []
    for i in range(diff_count):
        guid = data[off:off+16]
        off += 16
        guid_hex = guid.hex()
        guids.append(guid_hex)
        if i < 5:
            print(f'  GUID[{i}]: {guid_hex}')
    if diff_count > 5:
        print(f'  ... ({diff_count} total)')

    # Spatial params: center (3 * int32) + dims (3 * uint32)
    cx, cy, cz = struct.unpack_from('<iii', data, off)
    off += 12
    dx, dy, dz = struct.unpack_from('<III', data, off)
    off += 12
    print(f'Center: ({cx}, {cy}, {cz})')
    print(f'Dims: ({dx}, {dy}, {dz})')

    # Everything after spatial params is the TOK mesh data
    tok_data = data[off:]
    print(f'\nTOK data: {len(tok_data):,} bytes (offset {off} in PTH section)')

    # Show first 256 bytes as hex + ascii
    print('First 256 bytes:')
    for row in range(min(16, (len(tok_data) + 15) // 16)):
        chunk = tok_data[row*16:(row+1)*16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f'  {row*16:04x}: {hex_str:<48s} {ascii_str}')

    # Check if it starts with TOK signature
    if tok_data[:3] == b'tok':
        print('\nStarts with "tok" - confirmed PathEngine TOK format!')
    elif tok_data[:4] == b'\x00\x00\x00\x00':
        print('\nStarts with zeros - may need different offset')
    else:
        print(f'\nStarts with: {tok_data[:8]}')

    if out_path:
        Path(out_path).write_bytes(tok_data)
        print(f'\nWrote TOK data: {out_path} ({len(tok_data):,} bytes)')

    return tok_data


def main():
    if len(sys.argv) >= 2:
        lvl_path = sys.argv[1]
    else:
        # Default: SV RuinedCity02
        lvl_path = REPO / 'local' / 'decompiled_sv' / 'Levels' / 'World' / 'Greece' / 'Area004' / 'RuinedCity02.LVL'

    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
    else:
        out_path = REPO / 'local' / 'rc02_sv_mesh.tok'

    extract_tok(lvl_path, out_path)


if __name__ == '__main__':
    main()
