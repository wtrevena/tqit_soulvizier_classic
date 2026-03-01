"""Find where actual data is in the arc file."""
import struct
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_bytes()

first_nonzero = None
for i in range(28, len(raw)):
    if raw[i] != 0:
        first_nonzero = i
        break

last_nonzero = None
for i in range(len(raw) - 1, 27, -1):
    if raw[i] != 0:
        last_nonzero = i
        break

print(f"File size: {len(raw)}")
print(f"First non-zero byte after header: offset 0x{first_nonzero:X} ({first_nonzero})")
print(f"Last non-zero byte: offset 0x{last_nonzero:X} ({last_nonzero})")
print(f"Zero gap: 0x1C to 0x{first_nonzero:X} ({first_nonzero - 28} bytes of zeros)")

print(f"\nBytes around first non-zero:")
start = max(0, first_nonzero - 16)
for i in range(start, min(first_nonzero + 128, len(raw)), 16):
    hex_part = ' '.join(f'{b:02x}' for b in raw[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[i:i+16])
    print(f'  {i:06x}: {hex_part:<48} {ascii_part}')

print(f"\nBytes around end of file:")
start = max(0, last_nonzero - 64)
for i in range(start, min(last_nonzero + 32, len(raw)), 16):
    hex_part = ' '.join(f'{b:02x}' for b in raw[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[i:i+16])
    print(f'  {i:06x}: {hex_part:<48} {ascii_part}')

# Maybe the header values are offsets, not sizes
print(f"\nHeader interpretation as offsets:")
for off in [0x0C, 0x10, 0x14, 0x18]:
    val = struct.unpack_from('<I', raw, off)[0]
    print(f"  0x{off:02X}: {val} (0x{val:X})")
    if val < len(raw):
        context = raw[val:val+32]
        hex_part = ' '.join(f'{b:02x}' for b in context)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
        print(f"    At that offset: {hex_part}")
        print(f"    ASCII: {ascii_part}")
