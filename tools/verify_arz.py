"""Quick integrity check for a .arz file."""
import struct, zlib, sys
from pathlib import Path

def read_lp_string(data, offset):
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset + length].decode('latin-1')
    offset += length
    return s, offset

path = Path(sys.argv[1])
data = path.read_bytes()
magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = struct.unpack_from('<HHiiiii', data, 0)
print(f"Magic: {magic}, Version: {version}")
print(f"Records: {rt_count}")
print(f"Record table: offset={rt_offset}, size={rt_size}")
print(f"String table: offset={st_offset}, size={st_size}")
print(f"Total size: {len(data)} bytes")

body = data[:-16]
footer = data[-16:]
file_hash, st_hash, rd_hash, rt_hash = struct.unpack('<IIII', footer)
actual = zlib.adler32(body) & 0xFFFFFFFF
status = "PASS" if file_hash == actual else "FAIL"
print(f"Footer hash: {status}")

st_data = data[st_offset:st_offset + st_size]
num_str = struct.unpack_from('<i', st_data, 0)[0]
print(f"Strings: {num_str}")

pos = rt_offset
ok = err = 0
for i in range(min(200, rt_count)):
    try:
        name_id = struct.unpack_from('<i', data, pos)[0]
        pos += 4
        rec_type, pos = read_lp_string(data, pos)
        data_offset, comp_size = struct.unpack_from('<ii', data, pos)
        pos += 8
        timestamp = struct.unpack_from('<q', data, pos)[0]
        pos += 8
        abs_off = 24 + data_offset
        compressed = data[abs_off:abs_off + comp_size]
        raw = zlib.decompress(compressed)
        ok += 1
    except Exception as e:
        err += 1
        if err <= 3:
            print(f"  Error at record {i}: {e}")

print(f"First 200 records: {ok} OK, {err} errors")
if err == 0:
    print("ARZ integrity: GOOD")
else:
    print("ARZ integrity: ISSUES DETECTED")
