"""
Build a delta .arz containing only records that differ between
the mod database and the AE base game database.

This produces a proper Custom Quest overlay .arz that works on AE:
- Records identical to AE base game are excluded (fall through to base)
- Records modified by the mod are included (override base)
- Records unique to the mod are included (new content)
"""
import struct
import zlib
import sys
from pathlib import Path


def read_lp_string(data: bytes, offset: int) -> tuple[str, int]:
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset + length].decode('latin-1')
    offset += length
    return s, offset


def write_lp_string(s: str) -> bytes:
    encoded = s.encode('latin-1')
    return struct.pack('<i', len(encoded)) + encoded


def read_arz_records_raw(arz_path: Path) -> dict:
    """Read an .arz and return {record_name: (record_type, compressed_bytes, timestamp)}."""
    raw = arz_path.read_bytes()

    if raw[:3] == b'ARC':
        print(f"  Skipping .arc file: {arz_path}")
        return {}

    magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = \
        struct.unpack_from('<HHiiiii', raw, 0)

    is_tqit = (magic == 2)

    # Read string table
    st_data = raw[st_offset:st_offset + st_size]
    st_pos = 0
    st_count = struct.unpack_from('<i', st_data, st_pos)[0]
    st_pos += 4
    strings = []
    for _ in range(st_count):
        s, st_pos = read_lp_string(st_data, st_pos)
        strings.append(s)

    # Read records
    records = {}
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
            pos += 4
        timestamp = struct.unpack_from('<q', raw, pos)[0]
        pos += 8

        name = strings[name_id] if name_id < len(strings) else f'unknown_{name_id}'
        abs_offset = 24 + data_offset
        compressed_data = raw[abs_offset:abs_offset + compressed_size]

        records[name] = (record_type, compressed_data, timestamp)

    return records


def decompress_record(compressed: bytes) -> bytes:
    """Decompress record data, trying multiple zlib modes."""
    for wbits in (15, -15, zlib.MAX_WBITS):
        try:
            return zlib.decompress(compressed, wbits)
        except zlib.error:
            continue
    try:
        return zlib.decompress(compressed[2:], -15)
    except zlib.error:
        return compressed  # return as-is if can't decompress


def build_delta_arz(mod_records: dict, base_records: dict, output_path: Path,
                    exclude_prefixes: list[str] = None):
    """Build a TQAE-format .arz with only records that differ from base."""

    delta_records = {}
    identical = 0
    modified = 0
    new_records = 0
    excluded = 0

    for name, (rec_type, compressed, timestamp) in mod_records.items():
        # Check exclusion prefixes
        if exclude_prefixes:
            name_lower = name.lower()
            if any(name_lower.startswith(p.lower()) for p in exclude_prefixes):
                excluded += 1
                continue

        if name in base_records:
            base_type, base_compressed, base_ts = base_records[name]
            mod_decompressed = decompress_record(compressed)
            base_decompressed = decompress_record(base_compressed)

            if mod_decompressed == base_decompressed:
                identical += 1
                continue
            else:
                modified += 1
        else:
            new_records += 1

        delta_records[name] = (rec_type, compressed, timestamp)

    print(f"  Identical (excluded): {identical}")
    print(f"  Modified (included):  {modified}")
    print(f"  New (included):       {new_records}")
    print(f"  Prefix-excluded:      {excluded}")
    print(f"  Delta total:          {len(delta_records)}")

    # Build string table
    all_strings = set()
    for name, (rec_type, _, _) in delta_records.items():
        all_strings.add(name)
        # We also need field names from the decompressed data, but those are
        # already encoded as string table indices. We need to build a new
        # mapping. For simplicity, collect ALL unique strings needed.

    # Actually, the record data blob contains string table indices from
    # the ORIGINAL string table. We need to remap them to a new string table.
    # This is complex. Instead, let's preserve the original string table
    # and just rebuild the record table + data block.

    # Simpler approach: build with the original mod's full string table,
    # only changing which records are included.

    # Re-read mod .arz to get the original string table
    # (we need it because compressed record data references string indices)
    return delta_records


def write_delta_arz(mod_path: Path, base_path: Path, output_path: Path,
                    exclude_prefixes: list[str] = None):
    """Full pipeline: read both .arz files, compute delta, write output."""

    print(f"Reading mod: {mod_path}")
    mod_raw = mod_path.read_bytes()
    magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = \
        struct.unpack_from('<HHiiiii', mod_raw, 0)
    is_tqit = (magic == 2)
    print(f"  Format: {'TQIT' if is_tqit else 'TQAE'}, {rt_count} records")

    # Read mod string table (preserve it fully for data blob compatibility)
    mod_st_data = mod_raw[st_offset:st_offset + st_size]

    # Read mod strings for record name lookup
    st_pos = 0
    st_count_val = struct.unpack_from('<i', mod_st_data, st_pos)[0]
    st_pos += 4
    mod_strings = []
    for _ in range(st_count_val):
        s, st_pos = read_lp_string(mod_st_data, st_pos)
        mod_strings.append(s)

    # Read mod record entries with their raw compressed data
    mod_entries = []
    pos = rt_offset
    for _ in range(rt_count):
        name_id = struct.unpack_from('<i', mod_raw, pos)[0]
        pos += 4
        record_type, pos = read_lp_string(mod_raw, pos)
        data_offset = struct.unpack_from('<i', mod_raw, pos)[0]
        pos += 4
        compressed_size = struct.unpack_from('<i', mod_raw, pos)[0]
        pos += 4
        if is_tqit:
            pos += 4
        timestamp = struct.unpack_from('<q', mod_raw, pos)[0]
        pos += 8

        name = mod_strings[name_id] if name_id < len(mod_strings) else f'?{name_id}'
        abs_off = 24 + data_offset
        compressed = mod_raw[abs_off:abs_off + compressed_size]
        mod_entries.append((name, name_id, record_type, compressed, timestamp))

    print(f"\nReading base: {base_path}")
    base_records = read_arz_records_raw(base_path)
    print(f"  {len(base_records)} records")

    print(f"\nComputing delta...")
    # Determine which mod records to keep
    keep = []
    identical = 0
    modified = 0
    new_count = 0
    excluded_count = 0

    for name, name_id, rec_type, compressed, timestamp in mod_entries:
        if exclude_prefixes:
            name_lower = name.lower()
            if any(name_lower.startswith(p.lower()) for p in exclude_prefixes):
                excluded_count += 1
                continue

        if name in base_records:
            base_type, base_compressed, base_ts = base_records[name]
            mod_decompressed = decompress_record(compressed)
            base_decompressed = decompress_record(base_compressed)
            if mod_decompressed == base_decompressed:
                identical += 1
                continue
            modified += 1
        else:
            new_count += 1

        keep.append((name, name_id, rec_type, compressed, timestamp))

    print(f"  Identical (dropped):  {identical}")
    print(f"  Modified (kept):      {modified}")
    print(f"  New to mod (kept):    {new_count}")
    print(f"  Prefix-excluded:      {excluded_count}")
    print(f"  Delta records:        {len(keep)}")

    # Build output .arz in TQAE format
    print(f"\nWriting delta .arz...")

    # Record data block: pack compressed data contiguously
    data_block = bytearray()
    record_table = bytearray()

    for name, name_id, rec_type, compressed, timestamp in keep:
        data_offset = len(data_block)
        data_block += compressed

        record_table += struct.pack('<i', name_id)
        record_table += write_lp_string(rec_type)
        record_table += struct.pack('<i', data_offset)
        record_table += struct.pack('<i', len(compressed))
        record_table += struct.pack('<q', timestamp)

    data_block = bytes(data_block)
    record_table = bytes(record_table)

    rt_offset_new = 24 + len(data_block)
    st_offset_new = rt_offset_new + len(record_table)

    header = struct.pack('<HHiiiii',
        4,  # TQAE magic
        3,  # version
        rt_offset_new,
        len(record_table),
        len(keep),
        st_offset_new,
        len(mod_st_data),
    )

    body = header + data_block + record_table + mod_st_data

    file_hash = zlib.adler32(body) & 0xFFFFFFFF
    st_hash = zlib.adler32(mod_st_data) & 0xFFFFFFFF
    rd_hash = zlib.adler32(data_block) & 0xFFFFFFFF
    rt_hash = zlib.adler32(record_table) & 0xFFFFFFFF
    footer = struct.pack('<IIII', file_hash, st_hash, rd_hash, rt_hash)

    output_path.write_bytes(body + footer)
    total_size = len(body) + len(footer)
    print(f"  Output: {output_path}")
    print(f"  Size: {total_size} bytes ({total_size / 1024 / 1024:.1f} MB)")
    print(f"  Records: {len(keep)}")

    return len(keep)


def main():
    if len(sys.argv) < 4:
        print("Usage: arz_build_delta.py <mod.arz> <base_game.arz> <output.arz> [--exclude prefix1,prefix2,...]")
        sys.exit(1)

    mod_path = Path(sys.argv[1])
    base_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    exclude_prefixes = []
    for arg in sys.argv[4:]:
        if arg.startswith('--exclude='):
            exclude_prefixes = arg.split('=', 1)[1].split(',')

    if exclude_prefixes:
        print(f"Excluding prefixes: {exclude_prefixes}")

    write_delta_arz(mod_path, base_path, output_path, exclude_prefixes)
    print("\nDone.")


if __name__ == '__main__':
    main()
