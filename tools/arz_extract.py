"""
Extract all .dbr records from a TQAE .arz file into a directory tree.

Each record is written as a key=value text file mirroring the original
.dbr path structure. This enables diffing between databases.
"""
import struct
import zlib
import sys
import os
from pathlib import Path


def read_lp_string(data: bytes, offset: int) -> tuple[str, int]:
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset + length].decode('latin-1')
    offset += length
    return s, offset


DATA_TYPE_INT = 0
DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2
DATA_TYPE_BOOL = 3


def decode_record_data(compressed: bytes, string_table: list[str]) -> list[tuple[str, str]]:
    """Decompress and decode a record's binary data into key-value pairs."""
    # TQ .arz uses zlib with 2-byte header; try multiple approaches
    raw = None
    for wbits in (15, -15, zlib.MAX_WBITS):
        try:
            raw = zlib.decompress(compressed, wbits)
            break
        except zlib.error:
            continue
    if raw is None:
        # Try skipping first 2 bytes (zlib header) and using raw deflate
        try:
            raw = zlib.decompress(compressed[2:], -15)
        except zlib.error:
            raise ValueError("Could not decompress record data")
    fields = []
    pos = 0
    while pos < len(raw):
        if pos + 8 > len(raw):
            break
        data_type = struct.unpack_from('<h', raw, pos)[0]
        value_count = struct.unpack_from('<h', raw, pos + 2)[0]
        var_name_id = struct.unpack_from('<i', raw, pos + 4)[0]
        pos += 8

        var_name = string_table[var_name_id] if var_name_id < len(string_table) else f'?{var_name_id}'
        values = []
        for _ in range(value_count):
            if pos + 4 > len(raw):
                break
            raw_val = struct.unpack_from('<i', raw, pos)[0]
            if data_type == DATA_TYPE_INT:
                values.append(str(raw_val))
            elif data_type == DATA_TYPE_FLOAT:
                fval = struct.unpack_from('<f', raw, pos)[0]
                values.append(f'{fval:g}')
            elif data_type == DATA_TYPE_STRING:
                s = string_table[raw_val] if raw_val < len(string_table) else f'?{raw_val}'
                values.append(s)
            elif data_type == DATA_TYPE_BOOL:
                values.append(str(raw_val))
            else:
                values.append(f'0x{raw_val:08x}')
            pos += 4

        fields.append((var_name, ';'.join(values)))

    return fields


def extract_arz(arz_path: Path, output_dir: Path, filter_prefix: str = None):
    """Extract all records from an .arz to text .dbr files."""
    raw = arz_path.read_bytes()

    magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = \
        struct.unpack_from('<HHiiiii', raw, 0)

    is_tqit = (magic == 2)
    is_arc = (raw[:3] == b'ARC')

    if is_arc:
        print(f"File is an .arc (not .arz), skipping")
        return {}

    print(f"Format: {'TQIT' if is_tqit else 'TQAE'} (magic={magic})")
    print(f"Records: {rt_count}")

    # Read string table
    st_data = raw[st_offset:st_offset + st_size]
    st_pos = 0
    st_count = struct.unpack_from('<i', st_data, st_pos)[0]
    st_pos += 4
    strings = []
    for _ in range(st_count):
        s, st_pos = read_lp_string(st_data, st_pos)
        strings.append(s)

    print(f"Strings: {len(strings)}")

    # Read record table
    records = []
    pos = rt_offset
    for _ in range(rt_count):
        name_id = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        record_type, pos = read_lp_string(raw, pos)
        data_offset = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        compressed_size = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        if is_tqit:
            pos += 4  # skip decompressed_size
        timestamp = struct.unpack_from('<q', raw, pos)[0]
        pos += 8

        name = strings[name_id] if name_id < len(strings) else f'unknown_{name_id}'
        records.append({
            'name': name,
            'type': record_type,
            'data_offset': data_offset,
            'compressed_size': compressed_size,
        })

    # Extract records
    extracted = {}
    skipped = 0
    errors = 0
    for i, rec in enumerate(records):
        if filter_prefix and not rec['name'].startswith(filter_prefix):
            skipped += 1
            continue

        abs_offset = 24 + rec['data_offset']
        compressed = raw[abs_offset:abs_offset + rec['compressed_size']]

        try:
            fields = decode_record_data(compressed, strings)
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error decoding {rec['name']}: {e}")
            continue

        extracted[rec['name']] = fields

        if output_dir:
            out_path = output_dir / rec['name']
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'w', encoding='latin-1') as f:
                for key, val in fields:
                    f.write(f'{key},{val},\n')

        if (i + 1) % 10000 == 0:
            print(f"  Extracted {i + 1}/{rt_count}...")

    print(f"Extracted: {len(extracted)}, Skipped: {skipped}, Errors: {errors}")
    return extracted


def main():
    if len(sys.argv) < 3:
        print("Usage: arz_extract.py <input.arz> <output_dir> [filter_prefix]")
        print("  filter_prefix: only extract records starting with this path")
        print("  Example: arz_extract.py database.arz ./extracted records/game/")
        sys.exit(1)

    arz_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    filter_prefix = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Extracting: {arz_path}")
    if filter_prefix:
        print(f"Filter: {filter_prefix}")

    extract_arz(arz_path, output_dir, filter_prefix)
    print("Done.")


if __name__ == '__main__':
    main()
