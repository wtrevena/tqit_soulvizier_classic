"""Verify that UI records in patched .arz are identical to original."""
import struct
import zlib
import sys
from pathlib import Path


def read_lp_string(data, offset):
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset + length].decode('latin-1')
    offset += length
    return s, offset


def read_records_raw(path):
    raw = path.read_bytes()
    magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = \
        struct.unpack_from('<HHiiiii', raw, 0)

    st_data = raw[st_offset:st_offset + st_size]
    num_str = struct.unpack_from('<i', st_data, 0)[0]
    strings = []
    pos = 4
    for _ in range(num_str):
        s, pos = read_lp_string(st_data, pos)
        strings.append(s)

    records = {}
    pos = rt_offset
    for _ in range(rt_count):
        name_id = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        rec_type, pos = read_lp_string(raw, pos)
        data_offset, comp_size = struct.unpack_from('<ii', raw, pos)
        pos += 8
        timestamp = struct.unpack_from('<q', raw, pos)[0]
        pos += 8

        name = strings[name_id]
        abs_off = 24 + data_offset
        compressed = raw[abs_off:abs_off + comp_size]

        for wbits in (15, -15, zlib.MAX_WBITS):
            try:
                decompressed = zlib.decompress(compressed, wbits)
                break
            except zlib.error:
                decompressed = compressed

        records[name] = decompressed

    return records


orig_path = Path(sys.argv[1])
patched_path = Path(sys.argv[2])

print(f"Loading original: {orig_path}")
orig = read_records_raw(orig_path)
print(f"Loading patched: {patched_path}")
patched = read_records_raw(patched_path)

ui_patterns = ['masterypane', 'panectrl', 'ingameui', 'select mastery',
               'skilltree', 'playerlevels', 'gameengine']

print(f"\n=== UI record comparison ===")
checked = 0
identical = 0
different = 0
missing = 0

for name in sorted(orig.keys()):
    nl = name.lower()
    if not any(p in nl for p in ui_patterns):
        continue

    checked += 1
    if name not in patched:
        print(f"  MISSING: {name}")
        missing += 1
    elif orig[name] == patched[name]:
        identical += 1
    else:
        print(f"  DIFFERENT: {name}")
        print(f"    orig size={len(orig[name])}, patched size={len(patched[name])}")
        different += 1

print(f"\nChecked: {checked}")
print(f"Identical: {identical}")
print(f"Different: {different}")
print(f"Missing: {missing}")
