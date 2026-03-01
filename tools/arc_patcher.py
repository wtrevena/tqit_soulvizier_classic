"""
Safe .arc patcher for Titan Quest resource archives.

Strategy: parse the original fully, including per-part TOC entries
for multi-part files. On write, preserve all original metadata
(timestamps, hashes, flags) byte-for-byte. Only recalculate
data offsets and sizes.

.arc layout (version 1):
  [Header: 28 bytes]
  [Zero padding to 0x800]
  [Compressed data parts, contiguous]
  [TOC: 12 bytes per data PART (offset, comp_size, decomp_size)]
  [String table: null-terminated filenames]
  [File records: 44 bytes per entry, preserving unknown fields]

Each file with N parts uses N consecutive TOC entries starting at file_index.
"""
import struct
import zlib
import sys
from pathlib import Path

HEADER_SIZE = 28
DATA_START = 0x800
PART_SIZE = 262144  # 256KB


class FilePart:
    __slots__ = ('offset', 'comp_size', 'decomp_size', 'compressed_data')

    def __init__(self, offset=0, comp_size=0, decomp_size=0, data=b''):
        self.offset = offset
        self.comp_size = comp_size
        self.decomp_size = decomp_size
        self.compressed_data = data


class ArcEntry:
    __slots__ = ('raw_record', 'name', 'entry_type', 'comp_size',
                 'decomp_size', 'num_parts', 'file_index',
                 'parts', 'modified_data')

    def __init__(self, raw_record: bytes):
        self.raw_record = bytearray(raw_record)
        self.entry_type = struct.unpack_from('<I', raw_record, 0)[0]
        self.comp_size = struct.unpack_from('<I', raw_record, 8)[0]
        self.decomp_size = struct.unpack_from('<I', raw_record, 12)[0]
        self.num_parts = struct.unpack_from('<I', raw_record, 28)[0]
        self.file_index = struct.unpack_from('<I', raw_record, 32)[0]
        self.name = ''
        self.parts = []
        self.modified_data = None


class ArcArchive:
    def __init__(self):
        self.version = 1
        self.entries = []
        self.raw_string_table = b''

    @classmethod
    def from_file(cls, path: Path) -> 'ArcArchive':
        arc = cls()
        raw = path.read_bytes()

        assert raw[0:4] == b'ARC\x00'
        arc.version = struct.unpack_from('<I', raw, 4)[0]
        num_entries = struct.unpack_from('<I', raw, 8)[0]
        num_data = struct.unpack_from('<I', raw, 0x0C)[0]
        toc_size = struct.unpack_from('<I', raw, 0x10)[0]
        string_size = struct.unpack_from('<I', raw, 0x14)[0]
        toc_offset = struct.unpack_from('<I', raw, 0x18)[0]

        string_start = toc_offset + toc_size
        records_start = string_start + string_size

        arc.raw_string_table = raw[string_start:string_start + string_size]

        names_by_offset = {}
        pos = 0
        while pos < len(arc.raw_string_table):
            null = arc.raw_string_table.find(b'\x00', pos)
            if null < 0:
                break
            name = arc.raw_string_table[pos:null].decode('utf-8', errors='replace')
            if name:
                names_by_offset[pos] = name
            pos = null + 1

        # Parse TOC (12 bytes per data part)
        toc_parts = []
        for i in range(num_data):
            tpos = toc_offset + i * 12
            p_off = struct.unpack_from('<I', raw, tpos)[0]
            p_comp = struct.unpack_from('<I', raw, tpos + 4)[0]
            p_decomp = struct.unpack_from('<I', raw, tpos + 8)[0]
            p_data = raw[p_off:p_off + p_comp]
            toc_parts.append(FilePart(p_off, p_comp, p_decomp, p_data))

        # Parse file records
        for i in range(num_entries):
            rpos = records_start + i * 44
            raw_record = raw[rpos:rpos + 44]
            entry = ArcEntry(raw_record)

            str_off = struct.unpack_from('<I', raw_record, 40)[0]
            entry.name = names_by_offset.get(str_off, '')

            if entry.entry_type == 3 and entry.num_parts > 0:
                fi = entry.file_index
                for pi in range(entry.num_parts):
                    if fi + pi < len(toc_parts):
                        entry.parts.append(toc_parts[fi + pi])

            arc.entries.append(entry)

        return arc

    def decompress(self, entry: ArcEntry) -> bytes:
        if not entry.parts:
            return b''

        result = bytearray()
        for part in entry.parts:
            if part.comp_size == part.decomp_size:
                result += part.compressed_data
            else:
                try:
                    result += zlib.decompress(part.compressed_data, 15)
                except zlib.error:
                    try:
                        result += zlib.decompress(part.compressed_data, -15)
                    except zlib.error:
                        result += zlib.decompress(part.compressed_data)

        return bytes(result)

    def get_file(self, name: str) -> bytes | None:
        for entry in self.entries:
            if entry.name.lower() == name.lower() and entry.entry_type == 3:
                if entry.modified_data is not None:
                    return entry.modified_data
                return self.decompress(entry)
        return None

    def set_file(self, name: str, data: bytes):
        for entry in self.entries:
            if entry.name.lower() == name.lower() and entry.entry_type == 3:
                entry.modified_data = data

                # Recompress into parts
                entry.parts = []
                pos = 0
                while pos < len(data):
                    chunk = data[pos:pos + PART_SIZE]
                    compressed = zlib.compress(chunk, 6)
                    if len(compressed) >= len(chunk):
                        compressed = chunk
                    entry.parts.append(FilePart(
                        0, len(compressed), len(chunk), compressed))
                    pos += PART_SIZE

                entry.decomp_size = len(data)
                entry.comp_size = sum(p.comp_size for p in entry.parts)
                entry.num_parts = len(entry.parts)
                return True
        return False

    def add_file(self, name: str, data: bytes):
        """Add a new file entry to the archive (or overwrite if exists)."""
        if self.get_file(name) is not None:
            return self.set_file(name, data)

        str_offset = len(self.raw_string_table)
        name_bytes = name.encode('ascii') + b'\x00'
        self.raw_string_table += name_bytes

        raw = bytearray(44)
        struct.pack_into('<I', raw, 0, 3)       # entry_type = file
        struct.pack_into('<I', raw, 12, len(data))  # decomp_size
        struct.pack_into('<I', raw, 40, str_offset)  # string table offset

        entry = ArcEntry(bytes(raw))
        entry.raw_record = bytearray(raw)
        entry.name = name
        entry.entry_type = 3
        entry.modified_data = data

        parts = []
        pos = 0
        while pos < len(data):
            chunk = data[pos:pos + PART_SIZE]
            compressed = zlib.compress(chunk, 6)
            if len(compressed) >= len(chunk):
                compressed = chunk
            parts.append(FilePart(0, len(compressed), len(chunk), compressed))
            pos += PART_SIZE
        entry.parts = parts
        entry.decomp_size = len(data)
        entry.comp_size = sum(p.comp_size for p in parts)
        entry.num_parts = len(parts)

        self.entries.append(entry)
        return True

    def write(self, path: Path):
        # Lay out data parts sequentially starting at DATA_START
        current_offset = DATA_START
        toc_index = 0

        for entry in self.entries:
            if entry.entry_type == 3 and entry.parts:
                entry.file_index = toc_index
                first_offset = current_offset
                total_comp = 0

                for part in entry.parts:
                    part.offset = current_offset
                    current_offset += part.comp_size
                    total_comp += part.comp_size
                    toc_index += 1

                entry.comp_size = total_comp
                entry.decomp_size = sum(p.decomp_size for p in entry.parts)
                entry.num_parts = len(entry.parts)

                # Update raw record bytes
                struct.pack_into('<I', entry.raw_record, 4, first_offset)
                struct.pack_into('<I', entry.raw_record, 8, entry.comp_size)
                struct.pack_into('<I', entry.raw_record, 12, entry.decomp_size)
                struct.pack_into('<I', entry.raw_record, 28, entry.num_parts)
                struct.pack_into('<I', entry.raw_record, 32, entry.file_index)

        num_data = toc_index

        # Build data block
        data_block = bytearray()
        for entry in self.entries:
            for part in entry.parts:
                expected_off = DATA_START + len(data_block)
                assert part.offset == expected_off, \
                    f"Offset mismatch: {part.offset} vs {expected_off}"
                data_block += part.compressed_data

        # Build TOC
        toc = bytearray()
        for entry in self.entries:
            for part in entry.parts:
                toc += struct.pack('<III',
                    part.offset, part.comp_size, part.decomp_size)

        toc_offset = DATA_START + len(data_block)
        toc_size = len(toc)
        string_size = len(self.raw_string_table)

        # Build file records
        records = bytearray()
        for entry in self.entries:
            records += bytes(entry.raw_record)

        # Build header
        padding = bytes(DATA_START - HEADER_SIZE)

        header = b'ARC\x00'
        header += struct.pack('<I', self.version)
        header += struct.pack('<I', len(self.entries))
        header += struct.pack('<I', num_data)
        header += struct.pack('<I', toc_size)
        header += struct.pack('<I', string_size)
        header += struct.pack('<I', toc_offset)

        output = header + padding + bytes(data_block) + \
                 bytes(toc) + self.raw_string_table + bytes(records)

        path.write_bytes(output)
        return len(output)


    def get_text(self, name: str) -> str | None:
        """Get file as decoded text string, auto-detecting encoding."""
        raw = self.get_file(name)
        if raw is None:
            return None
        if raw[:2] == b'\xff\xfe':
            return raw[2:].decode('utf-16-le')
        if raw[:2] == b'\xfe\xff':
            return raw[2:].decode('utf-16-be')
        if raw[:3] == b'\xef\xbb\xbf':
            return raw[3:].decode('utf-8')
        return raw.decode('utf-8', errors='replace')

    def set_text(self, name: str, text: str):
        """Set file from text string, preserving original encoding (UTF-16LE BOM)."""
        encoded = b'\xff\xfe' + text.encode('utf-16-le')
        return self.set_file(name, encoded)

    def append_text_lines(self, name: str, lines: str) -> bool:
        """Append lines to a text file, preserving encoding."""
        existing = self.get_text(name)
        if existing is None:
            return False
        if not existing.endswith('\r\n') and not existing.endswith('\n'):
            existing += '\r\n'
        modified = existing + lines
        return self.set_text(name, modified)


def main():
    if len(sys.argv) < 3:
        print("Usage: arc_patcher.py <input.arc> <output.arc> [name=file ...]")
        print("  Or:  arc_patcher.py <input.arc> --verify")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if sys.argv[2] == '--verify':
        arc = ArcArchive.from_file(input_path)
        ok = 0
        fail = 0
        for entry in arc.entries:
            if entry.entry_type == 3 and entry.parts:
                data = arc.decompress(entry)
                if len(data) == entry.decomp_size:
                    print(f"  OK  {entry.name}: {entry.decomp_size} bytes "
                          f"({entry.num_parts} parts)")
                    ok += 1
                else:
                    print(f"  FAIL {entry.name}: expected {entry.decomp_size}, "
                          f"got {len(data)}")
                    fail += 1
        print(f"\n{ok} OK, {fail} FAIL")
        sys.exit(1 if fail > 0 else 0)

    output_path = Path(sys.argv[2])
    modifications = {}
    for arg in sys.argv[3:]:
        if '=' in arg:
            name, filepath = arg.split('=', 1)
            modifications[name] = Path(filepath).read_bytes()

    if modifications:
        print(f"Loading: {input_path}")
        arc = ArcArchive.from_file(input_path)
        for name, content in modifications.items():
            if arc.set_file(name, content):
                print(f"  Replaced: {name} ({len(content)} bytes)")
            else:
                print(f"  NOT FOUND: {name}")
        size = arc.write(output_path)
        print(f"Written: {output_path} ({size} bytes)")
    else:
        print("Round-trip test...")
        arc = ArcArchive.from_file(input_path)
        size = arc.write(output_path)
        orig_size = input_path.stat().st_size
        print(f"  Original: {orig_size} bytes")
        print(f"  Written:  {size} bytes")

        orig = input_path.read_bytes()
        copy = output_path.read_bytes()
        if orig == copy:
            print("  PERFECT MATCH!")
        else:
            print(f"  Size diff: {size - orig_size}")
            # Find first difference
            for i in range(min(len(orig), len(copy))):
                if orig[i] != copy[i]:
                    print(f"  First diff at offset 0x{i:X}")
                    break


if __name__ == '__main__':
    main()
