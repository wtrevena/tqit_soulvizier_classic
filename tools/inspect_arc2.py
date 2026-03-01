"""Deeper inspection of arc format - examine actual bytes at key offsets."""
import struct
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_bytes()

version = struct.unpack_from('<I', raw, 4)[0]
num_entries = struct.unpack_from('<I', raw, 8)[0]
record_size = struct.unpack_from('<I', raw, 0x10)[0]
string_size = struct.unpack_from('<I', raw, 0x14)[0]
data_size = struct.unpack_from('<I', raw, 0x18)[0]

data_start = len(raw) - data_size
string_start = data_start - string_size
toc_start = string_start - record_size

print(f"=== Layout ===")
print(f"Header: 0x00 - 0x1C ({28} bytes)")
print(f"Gap: 0x1C - 0x{toc_start:X} ({toc_start - 28} bytes)")
print(f"TOC: 0x{toc_start:X} - 0x{string_start:X} ({record_size} bytes)")
print(f"Strings: 0x{string_start:X} - 0x{data_start:X} ({string_size} bytes)")
print(f"Data: 0x{data_start:X} - 0x{len(raw):X} ({data_size} bytes)")

print(f"\n=== Bytes after header (gap region) ===")
for i in range(0x1C, min(0x1C + 128, toc_start), 16):
    hex_part = ' '.join(f'{b:02x}' for b in raw[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[i:i+16])
    print(f'  {i:06x}: {hex_part:<48} {ascii_part}')

print(f"\n=== TOC region (first 128 bytes) ===")
for i in range(toc_start, min(toc_start + 128, string_start), 16):
    hex_part = ' '.join(f'{b:02x}' for b in raw[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[i:i+16])
    print(f'  {i:06x}: {hex_part:<48} {ascii_part}')

print(f"\n=== String region ===")
for i in range(string_start, min(string_start + 320, data_start), 16):
    hex_part = ' '.join(f'{b:02x}' for b in raw[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[i:i+16])
    print(f'  {i:06x}: {hex_part:<48} {ascii_part}')

print(f"\n=== First bytes of data region ===")
for i in range(data_start, min(data_start + 64, len(raw)), 16):
    hex_part = ' '.join(f'{b:02x}' for b in raw[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw[i:i+16])
    print(f'  {i:06x}: {hex_part:<48} {ascii_part}')
