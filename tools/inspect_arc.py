"""Deep inspection of .arc format to understand exact binary layout."""
import struct
import sys
from pathlib import Path

raw = Path(sys.argv[1]).read_bytes()
total = len(raw)
print(f"Total: {total} bytes")

magic = raw[0:4]
print(f"Magic: {magic}")
version = struct.unpack_from('<I', raw, 4)[0]
print(f"Version: {version}")
num_entries = struct.unpack_from('<I', raw, 8)[0]
print(f"Num entries: {num_entries}")

val_0c = struct.unpack_from('<I', raw, 0x0C)[0]
val_10 = struct.unpack_from('<I', raw, 0x10)[0]
val_14 = struct.unpack_from('<I', raw, 0x14)[0]
val_18 = struct.unpack_from('<I', raw, 0x18)[0]
print(f"0x0C: {val_0c}")
print(f"0x10 (recordSize): {val_10}")
print(f"0x14 (stringSize): {val_14}")
print(f"0x18 (dataSize): {val_18}")

header_end = 0x1C

data_start = total - val_18
string_start = data_start - val_14
toc_start = string_start - val_10

print(f"\nInferred layout:")
print(f"  Header: 0 - {header_end}")
print(f"  TOC: {toc_start} - {string_start} (size {val_10})")
print(f"  Strings: {string_start} - {data_start} (size {val_14})")
print(f"  Data: {data_start} - {total} (size {val_18})")
print(f"  Gap between header and TOC: {toc_start - header_end}")

print(f"\nString table:")
pos = string_start
names = []
while pos < data_start:
    end = raw.index(b'\x00', pos) if b'\x00' in raw[pos:data_start] else data_start
    name = raw[pos:end].decode('utf-8', errors='replace')
    if name:
        names.append((pos - string_start, name))
    pos = end + 1

for offset, name in names:
    print(f"  [{offset:4d}] {name}")
print(f"  Total names: {len(names)}")

print(f"\nTOC entries:")
toc_entry_size = val_10 // num_entries if num_entries > 0 else 0
print(f"  Entry size: {toc_entry_size} bytes ({val_10} / {num_entries})")

pos = toc_start
for i in range(min(num_entries, 35)):
    if toc_entry_size == 0:
        break
    entry_data = raw[pos:pos + toc_entry_size]
    fields = []
    for j in range(0, len(entry_data), 4):
        if j + 4 <= len(entry_data):
            val = struct.unpack_from('<I', entry_data, j)[0]
            fields.append(val)
    if any(f != 0 for f in fields):
        name = names[i][1] if i < len(names) else '?'
        print(f"  [{i:2d}] {name}: {fields}")
    pos += toc_entry_size
