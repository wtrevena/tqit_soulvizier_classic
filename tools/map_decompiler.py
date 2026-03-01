#!/usr/bin/env python3
"""
Titan Quest MAP decompiler.

Decompiles a compiled world01.map into:
  - world01.wrl  (world reference file for MapCompiler)
  - world01.sd   (scene data)
  - Per-level .lvl, .rlv, .tga files

Based on MAPDecomp.cpp by p0a/knightsouldier (tq-mapdecompiler).
"""

import struct
import os
import sys
from pathlib import Path

MAP_MAGIC = 0x0650414D  # "MAP\x06"
WRL_MAGIC = 0x074C5257  # "WRL\x07"

SEC_LEVELS  = 0x01
SEC_DATA    = 0x02
SEC_UNKNOWN = 0x10
SEC_GROUPS  = 0x11
SEC_SD      = 0x18
SEC_BITMAPS = 0x19
SEC_DATA2   = 0x1A
SEC_QUESTS  = 0x1B


def read_uint32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def read_int32(data, offset):
    return struct.unpack_from('<i', data, offset)[0]


def read_float(data, offset):
    return struct.unpack_from('<f', data, offset)[0]


def parse_sections(data):
    magic = read_uint32(data, 0)
    if magic != MAP_MAGIC:
        raise ValueError(f"Not a MAP file (magic=0x{magic:08X})")

    sections = []
    pos = 8
    while pos + 8 <= len(data):
        sec_type = read_uint32(data, pos)
        sec_size = read_uint32(data, pos + 4)
        if sec_size > len(data) - pos - 8:
            break
        sections.append({
            'type': sec_type,
            'offset': pos + 8,
            'size': sec_size,
        })
        pos += 8 + sec_size
    return sections


def parse_level_index(data, sec_offset, sec_size):
    buf = data[sec_offset:sec_offset + sec_size]
    count = read_uint32(buf, 0)
    levels = []
    idx = 4
    for _ in range(count):
        ints_raw = struct.unpack_from('<13I', buf, idx)
        idx += 52

        dbr_len = read_uint32(buf, idx); idx += 4
        dbr = buf[idx:idx + dbr_len].decode('ascii', errors='replace')
        idx += dbr_len

        fname_len = read_uint32(buf, idx); idx += 4
        fname = buf[idx:idx + fname_len].decode('ascii', errors='replace')
        idx += fname_len

        data_offset = read_uint32(buf, idx); idx += 4
        data_length = read_uint32(buf, idx); idx += 4

        floats = list(struct.unpack('<6f', struct.pack('<6I', *ints_raw[:6])))
        remaining_ints = list(ints_raw[6:])

        levels.append({
            'floats': floats,
            'ints': remaining_ints,
            'ints_raw': ints_raw,
            'dbr': dbr,
            'filename': fname,
            'data_offset': data_offset,
            'data_length': data_length,
        })
    return levels


def decompile_rlv_to_lvl(rlv_data):
    """Convert .rlv binary data to .lvl editor format."""
    lvl_out = bytearray()

    first_uint = struct.unpack_from('<I', rlv_data, 0)[0]
    lvl_out += struct.pack('<I', first_uint)

    idx = 4
    while idx < len(rlv_data):
        if idx + 28 > len(rlv_data):
            sec_type = read_uint32(rlv_data, idx)
            sec_size = read_uint32(rlv_data, idx + 4)
            lvl_out += struct.pack('<II', sec_type, sec_size)
            idx += 8
            lvl_out += rlv_data[idx:idx + sec_size]
            idx += sec_size
            continue

        sec_type = read_uint32(rlv_data, idx)
        sec_size = read_uint32(rlv_data, idx + 4)

        if sec_type == 0x06:
            sub_vals = struct.unpack_from('<5I', rlv_data, idx + 8)
            sub_type = sub_vals[0]
            sub_flag = sub_vals[1]

            if sub_type == 0x02 and sub_flag == 0x01:
                idx += 8  # skip sec_type + sec_size

                rlv_size = sec_size
                dbr_count = sub_vals[2]
                x = sub_vals[3]
                y = sub_vals[4]
                dbr_word = (dbr_count // 8) + 1

                idx += 20  # skip the 5 sub_vals

                # Skip 4 more ints (9 total ints after type+size in the original)
                idx += 16

                block1_start = idx
                block1_size = x * y * 4
                idx += block1_size

                block2_size = x * y * dbr_word
                idx += block2_size

                block3_start = idx
                block3_size = 0
                dbr_size = read_uint32(rlv_data, idx)
                idx += dbr_size + 4
                block3_size += dbr_size + 4
                for j in range(1, dbr_count):
                    dbr_size = read_uint32(rlv_data, idx)
                    idx += dbr_size + 4
                    block3_size += dbr_size + 4
                    idx += (x - 1) * (y - 1)
                    block3_size += (x - 1) * (y - 1)

                block4_size = rlv_size - 36 - block1_size - block2_size - block3_size
                idx += block4_size

                lvl_size = 16 + block3_size + (block1_size * 2) + (block1_size * 3) + ((x - 1) * (y - 1) * 4)

                lvl_out += struct.pack('<6I', 0x06, lvl_size, 0, x, y, dbr_count)

                lvl_out += rlv_data[block3_start:block3_start + block3_size]

                block = block1_size // 4
                for j in range(block):
                    val = rlv_data[block1_start + j * 4:block1_start + j * 4 + 4]
                    lvl_out += val + b'\x00\x00\x00\x00'
                for j in range(block):
                    val = rlv_data[block1_start + j * 4:block1_start + j * 4 + 4]
                    lvl_out += val + b'\x00\x00\x00\x00\x00\x00\x00\x00'
                lvl_out += b'\x00' * ((x - 1) * (y - 1) * 4)

                continue

        lvl_out += struct.pack('<II', sec_type, sec_size)
        idx += 8
        lvl_out += rlv_data[idx:idx + sec_size]
        idx += sec_size

    return bytes(lvl_out)


def decompile_map(map_data, output_dir, wrl_name='world01.wrl'):
    """Decompile a MAP binary into WRL + level files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sections = parse_sections(map_data)
    print(f"  Parsed {len(sections)} sections")

    level_sec = quest_sec = group_sec = bitmap_sec = sd_sec = None
    for sec in sections:
        if sec['type'] == SEC_LEVELS:
            level_sec = sec
        elif sec['type'] == SEC_QUESTS:
            quest_sec = sec
        elif sec['type'] == SEC_GROUPS:
            group_sec = sec
        elif sec['type'] == SEC_BITMAPS:
            bitmap_sec = sec
        elif sec['type'] == SEC_SD:
            sd_sec = sec

    if level_sec is None:
        raise ValueError("No LEVELS section found")

    levels = parse_level_index(map_data, level_sec['offset'], level_sec['size'])
    print(f"  {len(levels)} levels")

    # Write .sd file
    if sd_sec:
        sd_path = output_dir / wrl_name.replace('.wrl', '.sd')
        sd_path.write_bytes(map_data[sd_sec['offset']:sd_sec['offset'] + sd_sec['size']])
        print(f"  Wrote {sd_path.name}")

    # Build WRL file
    wrl_data = bytearray()
    wrl_data += struct.pack('<I', WRL_MAGIC)

    # Write levels section to WRL
    level_body = bytearray()
    level_body += struct.pack('<I', len(levels))
    for lv in levels:
        fname_bytes = lv['filename'].encode('ascii')
        dbr_bytes = lv['dbr'].encode('ascii')

        level_body += struct.pack('<I', len(fname_bytes))
        level_body += fname_bytes
        floats = lv['floats']
        remaining = lv['ints']
        level_body += struct.pack('<6f', *floats)
        level_body += struct.pack('<7I', *remaining)
        level_body += struct.pack('<I', len(dbr_bytes))
        level_body += dbr_bytes

    wrl_data += struct.pack('<II', 0x13, len(level_body))
    wrl_data += level_body

    # Write quests to WRL
    if quest_sec:
        wrl_data += struct.pack('<II', SEC_QUESTS, quest_sec['size'])
        wrl_data += map_data[quest_sec['offset']:quest_sec['offset'] + quest_sec['size']]

    # Write groups to WRL
    if group_sec:
        wrl_data += struct.pack('<II', SEC_GROUPS, group_sec['size'])
        wrl_data += map_data[group_sec['offset']:group_sec['offset'] + group_sec['size']]

    # Extract and write .rlv, .lvl, .tga files
    for i, lv in enumerate(levels):
        fname = lv['filename']
        rlv_data = map_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]

        base = fname[:-4] if fname.lower().endswith(('.lvl', '.rlv')) else fname

        # Write .rlv (raw compiled level data)
        rlv_path = output_dir / (base + '.rlv')
        rlv_path.parent.mkdir(parents=True, exist_ok=True)
        rlv_path.write_bytes(rlv_data)

        # Write .lvl (decompiled editor format)
        try:
            lvl_data = decompile_rlv_to_lvl(rlv_data)
            lvl_path = output_dir / (base + '.lvl')
            lvl_path.write_bytes(lvl_data)
        except Exception as e:
            print(f"  WARNING: Failed to decompile {fname} to .lvl: {e}")

    print(f"  Extracted {len(levels)} level files")

    # Extract bitmaps (minimap TGAs)
    if bitmap_sec:
        bmp_buf = map_data[bitmap_sec['offset']:bitmap_sec['offset'] + bitmap_sec['size']]
        tga_count = read_uint32(bmp_buf, 4)

        tga_entries = []
        bmp_body = bytearray()
        for i in range(tga_count):
            offset = read_uint32(bmp_buf, 8 + i * 8)
            length = read_uint32(bmp_buf, 12 + i * 8)

            fname = levels[i]['filename']
            tga_fname = fname[:-3] + 'tga'
            tga_path = output_dir / tga_fname

            if length > 0:
                tga_data = map_data[offset:offset + length]
                tga_path.write_bytes(tga_data)

                # Shrink for WRL
                if len(tga_data) >= 0x12 + 6:
                    old_x = struct.unpack_from('<H', tga_data, 12)[0]
                    old_y = struct.unpack_from('<H', tga_data, 14)[0]
                    new_x = old_x // 4
                    new_y = old_y // 4
                    if new_x > 0 and new_y > 0:
                        shrunk = bytearray(0x12 + new_x * new_y * 3)
                        shrunk[:0x12] = tga_data[:0x12]
                        struct.pack_into('<H', shrunk, 12, new_x)
                        struct.pack_into('<H', shrunk, 14, new_y)
                        for sy in range(new_y):
                            for sx in range(new_x):
                                src = 0x12 + (sy * 4 * old_x + sx * 4) * 3
                                dst = 0x12 + (sy * new_x + sx) * 3
                                if src + 3 <= len(tga_data):
                                    shrunk[dst:dst + 3] = tga_data[src:src + 3]
                        tga_entries.append(bytes(shrunk))
                    else:
                        tga_entries.append(b'')
                else:
                    tga_entries.append(b'')
            else:
                tga_entries.append(b'')

        # Write bitmap section to WRL
        bmp_wrl_size = sum(len(t) + 16 for t in tga_entries)
        wrl_data += struct.pack('<II', 0x15, bmp_wrl_size)
        for i, tga_bytes in enumerate(tga_entries):
            if len(tga_bytes) >= 0x12:
                tx = struct.unpack_from('<H', tga_bytes, 12)[0]
                ty = struct.unpack_from('<H', tga_bytes, 14)[0]
            else:
                tx = ty = 0
            wrl_data += struct.pack('<4I', 0, tx, ty, len(tga_bytes))
            wrl_data += tga_bytes

        print(f"  Extracted {tga_count} minimap TGAs")

    # Write WRL
    wrl_path = output_dir / wrl_name
    wrl_path.write_bytes(bytes(wrl_data))
    print(f"  Wrote {wrl_path.name} ({len(wrl_data)} bytes)")

    return levels


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_levels.arc_or_map> <output_dir>")
        print("  If .arc, extracts world01.map first, then decompiles.")
        print("  If .map, decompiles directly.")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if input_path.suffix.lower() == '.arc':
        print(f"Loading ARC: {input_path}")
        sys.path.insert(0, str(input_path.parent))
        from arc_patcher import ArcArchive
        arc = ArcArchive.from_file(input_path)
        entry = [e for e in arc.entries if e.entry_type == 3][0]
        print(f"  Decompressing {entry.name} ({entry.decomp_size} bytes)...")
        map_data = arc.decompress(entry)
    else:
        print(f"Loading MAP: {input_path}")
        map_data = input_path.read_bytes()

    print(f"Decompiling ({len(map_data)} bytes)...")
    decompile_map(map_data, output_dir)
    print("Done.")


if __name__ == '__main__':
    main()
