"""
Read and patch .arz database files with minimal corruption risk.

Key design: records are kept as raw compressed bytes unless they need
modification. Only records targeted for patching are decoded, modified,
and re-encoded. This avoids lossy round-trips on untouched records.
"""
import struct
import zlib
import sys
from pathlib import Path
from collections import OrderedDict


DATA_TYPE_INT = 0
DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2
DATA_TYPE_BOOL = 3


def read_lp_string(data: bytes, offset: int) -> tuple[str, int]:
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset + length].decode('latin-1')
    offset += length
    return s, offset


def write_lp_string(s: str) -> bytes:
    encoded = s.encode('latin-1')
    return struct.pack('<i', len(encoded)) + encoded


class TypedField:
    """Preserves original data type alongside value."""
    __slots__ = ('dtype', 'values')

    def __init__(self, dtype: int, values: list):
        self.dtype = dtype
        self.values = values

    @property
    def value(self):
        if len(self.values) == 1:
            return self.values[0]
        return self.values

    @value.setter
    def value(self, v):
        if isinstance(v, list):
            self.values = v
        else:
            self.values = [v]


class ArzDatabase:
    """In-memory .arz with raw passthrough for unmodified records."""

    def __init__(self):
        self.strings: list[str] = []
        self.string_to_id: dict[str, int] = {}
        self._raw_records: OrderedDict[str, tuple] = OrderedDict()
        self._decoded_cache: dict[str, OrderedDict[str, TypedField]] = {}
        self._record_types: dict[str, str] = {}
        self._record_timestamps: dict[str, int] = {}
        self._modified: set[str] = set()

    def ensure_string(self, s: str) -> int:
        if s in self.string_to_id:
            return self.string_to_id[s]
        idx = len(self.strings)
        self.strings.append(s)
        self.string_to_id[s] = idx
        return idx

    @classmethod
    def from_arz(cls, path: Path) -> 'ArzDatabase':
        db = cls()
        raw = path.read_bytes()

        magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = \
            struct.unpack_from('<HHiiiii', raw, 0)
        is_tqit = (magic == 2)

        st_data = raw[st_offset:st_offset + st_size]
        st_pos = 0
        st_num = struct.unpack_from('<i', st_data, st_pos)[0]
        st_pos += 4
        for i in range(st_num):
            s, st_pos = read_lp_string(st_data, st_pos)
            db.strings.append(s)
            db.string_to_id[s] = i

        pos = rt_offset
        for idx in range(rt_count):
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

            name = db.strings[name_id] if name_id < len(db.strings) else f'?{name_id}'
            abs_off = 24 + data_offset
            compressed = raw[abs_off:abs_off + compressed_size]

            db._raw_records[name] = (name_id, compressed)
            db._record_types[name] = record_type
            db._record_timestamps[name] = timestamp

            if (idx + 1) % 10000 == 0:
                print(f"  Read {idx + 1}/{rt_count}...")

        print(f"  Loaded: {len(db._raw_records)} records, {len(db.strings)} strings")
        return db

    def _decompress(self, compressed: bytes) -> bytes:
        for wbits in (15, -15, zlib.MAX_WBITS):
            try:
                return zlib.decompress(compressed, wbits)
            except zlib.error:
                continue
        try:
            return zlib.decompress(compressed[2:], -15)
        except zlib.error:
            return compressed

    def _decode_fields(self, compressed: bytes) -> OrderedDict[str, TypedField]:
        raw = self._decompress(compressed)
        fields = OrderedDict()
        pos = 0
        field_idx = 0
        while pos < len(raw):
            if pos + 8 > len(raw):
                break
            dtype = struct.unpack_from('<H', raw, pos)[0]
            num_values = struct.unpack_from('<H', raw, pos + 2)[0]
            var_id = struct.unpack_from('<i', raw, pos + 4)[0]
            pos += 8

            var_name = self.strings[var_id] if var_id < len(self.strings) else f'?{var_id}'
            values = []
            for _ in range(num_values):
                if dtype == DATA_TYPE_INT:
                    values.append(struct.unpack_from('<i', raw, pos)[0])
                    pos += 4
                elif dtype == DATA_TYPE_FLOAT:
                    values.append(struct.unpack_from('<f', raw, pos)[0])
                    pos += 4
                elif dtype == DATA_TYPE_STRING:
                    str_id = struct.unpack_from('<i', raw, pos)[0]
                    values.append(self.strings[str_id] if str_id < len(self.strings) else f'?{str_id}')
                    pos += 4
                elif dtype == DATA_TYPE_BOOL:
                    values.append(struct.unpack_from('<i', raw, pos)[0])
                    pos += 4
                else:
                    pos += 4 * num_values
                    break

            unique_key = f"{var_name}###{field_idx}"
            if var_name in fields:
                unique_key = f"{var_name}###{field_idx}"
            else:
                unique_key = var_name

            fields[unique_key] = TypedField(dtype, values)
            field_idx += 1

        return fields

    def _encode_fields(self, fields: OrderedDict[str, TypedField]) -> bytes:
        parts = bytearray()
        for key, tf in fields.items():
            real_name = key.split('###')[0]
            var_id = self.ensure_string(real_name)
            num = len(tf.values)
            if num == 0:
                continue

            parts += struct.pack('<HHi', tf.dtype, num, var_id)
            for v in tf.values:
                if tf.dtype == DATA_TYPE_INT:
                    parts += struct.pack('<i', int(v))
                elif tf.dtype == DATA_TYPE_FLOAT:
                    parts += struct.pack('<f', float(v))
                elif tf.dtype == DATA_TYPE_STRING:
                    str_id = self.ensure_string(str(v))
                    parts += struct.pack('<i', str_id)
                elif tf.dtype == DATA_TYPE_BOOL:
                    parts += struct.pack('<i', int(v))

        return bytes(parts)

    def get_fields(self, record_name: str) -> OrderedDict[str, TypedField] | None:
        if record_name in self._decoded_cache:
            return self._decoded_cache[record_name]
        if record_name not in self._raw_records:
            return None
        _, compressed = self._raw_records[record_name]
        fields = self._decode_fields(compressed)
        self._decoded_cache[record_name] = fields
        return fields

    def get_field_value(self, record_name: str, field_name: str):
        fields = self.get_fields(record_name)
        if fields is None:
            return None
        if field_name in fields:
            return fields[field_name].value
        for key, tf in fields.items():
            if key.split('###')[0] == field_name:
                return tf.value
        return None

    def set_field(self, record_name: str, field_name: str, value, dtype: int = None):
        fields = self.get_fields(record_name)
        if fields is None:
            return

        target_key = None
        for key in fields:
            if key == field_name or key.split('###')[0] == field_name:
                target_key = key
                break

        if target_key:
            tf = fields[target_key]
            if isinstance(value, list):
                tf.values = value
            else:
                tf.values = [value]
            if dtype is not None:
                tf.dtype = dtype
        else:
            if dtype is None:
                if isinstance(value, list):
                    sample = value[0] if value else 0
                else:
                    sample = value
                if isinstance(sample, float):
                    dtype = DATA_TYPE_FLOAT
                elif isinstance(sample, str):
                    dtype = DATA_TYPE_STRING
                elif isinstance(sample, bool):
                    dtype = DATA_TYPE_BOOL
                else:
                    dtype = DATA_TYPE_INT

            vals = value if isinstance(value, list) else [value]
            fields[field_name] = TypedField(dtype, vals)

        self._modified.add(record_name)

    def record_names(self):
        return list(self._raw_records.keys())

    def has_record(self, name: str) -> bool:
        return name in self._raw_records

    def clone_record(self, source_name: str, dest_name: str):
        """Create a copy of a record at a new path (e.g. for case-aliasing)."""
        if source_name not in self._raw_records:
            return False
        self._raw_records[dest_name] = self._raw_records[source_name]
        if source_name in self._decoded_cache:
            import copy
            self._decoded_cache[dest_name] = copy.deepcopy(
                self._decoded_cache[source_name])
        if source_name in self._record_types:
            self._record_types[dest_name] = self._record_types[source_name]
        if source_name in self._record_timestamps:
            self._record_timestamps[dest_name] = self._record_timestamps[source_name]
        self._modified.add(dest_name)
        return True

    def write_arz(self, output_path: Path):
        print(f"Writing {len(self._raw_records)} records to {output_path}...")
        print(f"  Modified records: {len(self._modified)}")

        data_block = bytearray()
        record_table = bytearray()

        count = 0
        for name in self._raw_records:
            name_id = self.ensure_string(name)
            rec_type = self._record_types.get(name, '')
            timestamp = self._record_timestamps.get(name, 0)

            if name in self._modified and name in self._decoded_cache:
                raw_data = self._encode_fields(self._decoded_cache[name])
                compressed = zlib.compress(raw_data, 6)
            else:
                _, compressed = self._raw_records[name]

            data_offset = len(data_block)
            data_block += compressed

            record_table += struct.pack('<i', name_id)
            record_table += write_lp_string(rec_type)
            record_table += struct.pack('<i', data_offset)
            record_table += struct.pack('<i', len(compressed))
            record_table += struct.pack('<q', timestamp)

            count += 1
            if count % 10000 == 0:
                print(f"  Written {count}/{len(self._raw_records)}...")

        st_data = struct.pack('<i', len(self.strings))
        for s in self.strings:
            st_data += write_lp_string(s)

        data_block = bytes(data_block)
        record_table = bytes(record_table)

        rt_offset = 24 + len(data_block)
        st_offset_val = rt_offset + len(record_table)

        header = struct.pack('<HHiiiii',
            4, 3,
            rt_offset,
            len(record_table),
            len(self._raw_records),
            st_offset_val,
            len(st_data),
        )

        body = header + data_block + record_table + st_data
        file_hash = zlib.adler32(body) & 0xFFFFFFFF
        st_hash = zlib.adler32(st_data) & 0xFFFFFFFF
        rd_hash = zlib.adler32(data_block) & 0xFFFFFFFF
        rt_hash = zlib.adler32(record_table) & 0xFFFFFFFF
        footer = struct.pack('<IIII', file_hash, st_hash, rd_hash, rt_hash)

        output_path.write_bytes(body + footer)
        total = len(body) + len(footer)
        print(f"  Size: {total} bytes ({total/1024/1024:.1f} MB)")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: arz_patcher.py <input.arz> [--info]")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    print(f"\nRecords: {len(db._raw_records)}")
    print(f"Strings: {len(db.strings)}")
