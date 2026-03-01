"""
Titan Quest .arz format converter: TQIT -> TQAE

The .arz binary format:
  Header (24 bytes):
    uint16 magic        (TQIT=2, TQAE=4)
    uint16 version      (always 3)
    int32  recordTableOffset
    int32  recordTableSize
    int32  recordTableCount
    int32  stringTableOffset
    int32  stringTableSize

  Record Data Block (offset 24 .. recordTableOffset):
    Contiguous zlib-compressed record blobs. Identical between formats.

  Record Table (at recordTableOffset, recordTableCount entries):
    Each entry:
      int32  nameId           (string table index for .dbr path)
      string recordType       (int32 length + raw bytes)
      int32  dataOffset       (into record data block, relative to byte 24)
      int32  compressedSize
      int32  decompressedSize (TQIT ONLY -- absent in TQAE)
      int64  timestamp

  String Table (at stringTableOffset):
    int32 count
    strings: int32 length + raw bytes each

  Footer (16 bytes after string table):
    4x uint32 checksums (Adler-32 variants, loosely validated)

To convert TQIT->TQAE: change magic 2->4, rewrite record table without
the decompressedSize field, adjust offsets, recompute footer checksums.
"""
import struct
import sys
import zlib
from pathlib import Path


def read_lp_string(data: bytes, offset: int) -> tuple[str, int]:
    """Read a length-prefixed string. Returns (string, new_offset)."""
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset + length].decode('latin-1')
    offset += length
    return s, offset


def write_lp_string(s: str) -> bytes:
    """Write a length-prefixed string."""
    encoded = s.encode('latin-1')
    return struct.pack('<i', len(encoded)) + encoded


def adler32(data: bytes) -> int:
    return zlib.adler32(data) & 0xFFFFFFFF


def read_arz(filepath: Path) -> dict:
    """Read a TQIT or TQAE .arz file and return parsed structure."""
    raw = filepath.read_bytes()
    if len(raw) < 24:
        raise ValueError(f"File too small: {len(raw)} bytes")

    magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = \
        struct.unpack_from('<HHiiiii', raw, 0)

    print(f"  Magic: {magic} ({'TQIT' if magic == 2 else 'TQAE' if magic == 4 else 'unknown'})")
    print(f"  Version: {version}")
    print(f"  Records: {rt_count}")
    print(f"  Record table at: {rt_offset} ({rt_size} bytes)")
    print(f"  String table at: {st_offset} ({st_size} bytes)")

    is_tqit = (magic == 2)

    record_data_block = raw[24:rt_offset]

    records = []
    pos = rt_offset
    for i in range(rt_count):
        name_id = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        record_type, pos = read_lp_string(raw, pos)
        data_offset = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        compressed_size = struct.unpack_from('<i', raw, pos)[0]
        pos += 4
        if is_tqit:
            decompressed_size = struct.unpack_from('<i', raw, pos)[0]
            pos += 4
        else:
            decompressed_size = None
        timestamp = struct.unpack_from('<q', raw, pos)[0]
        pos += 8

        records.append({
            'name_id': name_id,
            'record_type': record_type,
            'data_offset': data_offset,
            'compressed_size': compressed_size,
            'decompressed_size': decompressed_size,
            'timestamp': timestamp,
        })

    st_data = raw[st_offset:st_offset + st_size]
    st_pos = 0
    st_count = struct.unpack_from('<i', st_data, st_pos)[0]
    st_pos += 4
    strings = []
    for _ in range(st_count):
        s, st_pos = read_lp_string(st_data, st_pos)
        strings.append(s)

    footer_start = st_offset + st_size
    footer = raw[footer_start:footer_start + 16] if footer_start + 16 <= len(raw) else b'\x00' * 16

    return {
        'magic': magic,
        'version': version,
        'is_tqit': is_tqit,
        'record_data_block': record_data_block,
        'records': records,
        'strings': strings,
        'raw_string_table': st_data,
    }


def write_arz_tqae(arz: dict, output_path: Path):
    """Write an .arz file in TQAE format (magic=4, no decompressedSize)."""
    record_data = arz['record_data_block']

    rt_entries = bytearray()
    for rec in arz['records']:
        rt_entries += struct.pack('<i', rec['name_id'])
        rt_entries += write_lp_string(rec['record_type'])
        rt_entries += struct.pack('<i', rec['data_offset'])
        rt_entries += struct.pack('<i', rec['compressed_size'])
        # NO decompressedSize for TQAE
        rt_entries += struct.pack('<q', rec['timestamp'])

    rt_entries = bytes(rt_entries)
    st_data = arz['raw_string_table']

    rt_offset = 24 + len(record_data)
    rt_size = len(rt_entries)
    rt_count = len(arz['records'])
    st_offset = rt_offset + rt_size
    st_size = len(st_data)

    header = struct.pack('<HHiiiii',
        4,              # magic = TQAE
        3,              # version
        rt_offset,
        rt_size,
        rt_count,
        st_offset,
        st_size,
    )

    body = header + record_data + rt_entries + st_data

    file_hash = adler32(body)
    st_hash = adler32(st_data)
    rd_hash = adler32(record_data)
    rt_hash = adler32(rt_entries)
    footer = struct.pack('<IIII', file_hash, st_hash, rd_hash, rt_hash)

    output_path.write_bytes(body + footer)
    total = len(body) + len(footer)
    print(f"  Written: {output_path} ({total} bytes, {total / 1024 / 1024:.1f} MB)")


def validate_arz(filepath: Path):
    """Quick validation: read header and check magic."""
    raw = filepath.read_bytes()
    magic, version = struct.unpack_from('<HH', raw, 0)
    print(f"  Validation: magic={magic}, version={version}, size={len(raw)} bytes")
    if magic == 4 and version == 3:
        print(f"  PASS: Valid TQAE format")
        return True
    else:
        print(f"  FAIL: Expected magic=4 version=3")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: arz_converter.py <input.arz> <output.arz> [--validate]")
        print("  Converts a TQIT-format .arz (magic=2) to TQAE-format (magic=4)")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    do_validate = '--validate' in sys.argv

    print(f"Reading: {input_path}")
    arz = read_arz(input_path)

    if arz['is_tqit']:
        print(f"\nConverting TQIT -> TQAE ({len(arz['records'])} records, {len(arz['strings'])} strings)")
        write_arz_tqae(arz, output_path)
    elif arz['magic'] == 4:
        print(f"\nAlready TQAE format. Copying as-is.")
        output_path.write_bytes(input_path.read_bytes())
    else:
        print(f"\nUnknown magic {arz['magic']}, attempting TQAE conversion anyway...")
        write_arz_tqae(arz, output_path)

    if do_validate:
        print(f"\nValidating output:")
        validate_arz(output_path)

    print("\nDone.")


if __name__ == '__main__':
    main()
