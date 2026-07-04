"""Dump raw hex of PTH section to understand exact header format."""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_section_surgery import parse_blob_sections

REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')

lvl_path = sys.argv[1] if len(sys.argv) > 1 else str(
    REPO / 'local' / 'decompiled_sv' / 'Levels' / 'World' / 'Greece' / 'Area004' / 'RuinedCity02.LVL')

blob = Path(lvl_path).read_bytes()
secs, _ = parse_blob_sections(blob)

for s in secs:
    if s['type'] == 0x0a:
        data = s['data']
        print(f'PTH section: {len(data)} bytes')
        print(f'Magic: {data[:4]}')
        print()

        # Dump first 256 bytes as hex + ascii
        print('Raw hex dump of PTH section (first 256 bytes):')
        for row in range(min(16, (len(data) + 15) // 16)):
            chunk = data[row*16:(row+1)*16]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            print(f'  {row*16:04x}: {hex_str:<48s} {ascii_str}')

        # Try parsing as various uint32 values
        print('\nAs uint32 sequence:')
        for i in range(min(36, len(data) // 4)):
            val = struct.unpack_from('<I', data, i*4)[0]
            sval = struct.unpack_from('<i', data, i*4)[0]
            raw = data[i*4:(i+1)*4]
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw)
            print(f'  [{i:2d}] offset {i*4:3d}: 0x{val:08x} = {val:>12d} (signed: {sval:>12d})  {ascii_str}')

        # Find "mesh" string
        mesh_pos = data.find(b'mesh\x00')
        if mesh_pos >= 0:
            print(f'\n"mesh\\0" found at offset {mesh_pos} in PTH section')
            # Show context before mesh
            ctx_start = max(0, mesh_pos - 32)
            print(f'Context (offset {ctx_start} to {mesh_pos + 32}):')
            for row_start in range(ctx_start, min(mesh_pos + 32, len(data)), 16):
                chunk = data[row_start:row_start+16]
                hex_str = ' '.join(f'{b:02x}' for b in chunk)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                marker = ' <-- mesh' if mesh_pos >= row_start and mesh_pos < row_start + 16 else ''
                print(f'  {row_start:04x}: {hex_str:<48s} {ascii_str}{marker}')
        break
