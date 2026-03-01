#!/usr/bin/env python3
"""
Proper map decompiler that produces editor-format .lvl files.
Port of MAPDecomp.cpp by p0a / knightsouldier.

The key difference from raw extraction: terrain sections (type 0x06)
are converted from compiled format to editor format, which allows
MapCompiler to properly optimize levels and generate AE pathfinding.
"""
import sys, struct, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2

def decompile_level(raw_data):
    """Convert compiled level data to editor .lvl format."""
    result = bytearray()
    idx = 0

    # Write magic/version uint32
    magic = struct.unpack_from('<I', raw_data, idx)[0]
    result += struct.pack('<I', magic)
    idx += 4

    while idx < len(raw_data):
        if idx + 8 > len(raw_data):
            break

        # Peek at section header (up to 7 ints = 28 bytes)
        peek_end = min(idx + 28, len(raw_data))
        peek = raw_data[idx:peek_end]
        if len(peek) < 8:
            break

        sec_type = struct.unpack_from('<I', peek, 0)[0]
        sec_size = struct.unpack_from('<I', peek, 4)[0]

        # Check for terrain section: type=0x06, flags at offsets 8,12 = 0x02, 0x01
        is_terrain = False
        if sec_type == 0x06 and len(peek) >= 28:
            flag1 = struct.unpack_from('<I', peek, 8)[0]
            flag2 = struct.unpack_from('<I', peek, 12)[0]
            if flag1 == 0x02 and flag2 == 0x01:
                is_terrain = True

        if is_terrain:
            # Terrain section: convert compiled -> editor format
            rlv_size = sec_size
            dbr_count = struct.unpack_from('<I', peek, 16)[0]
            x = struct.unpack_from('<I', peek, 20)[0]
            y = struct.unpack_from('<I', peek, 24)[0]
            dbr_word = (dbr_count // 8) + 1

            # Advance past 11 ints of header (2 consumed + 9 more)
            idx += 44

            # block1: heightmap (x * y * 4 bytes)
            block1_size = x * y * 4
            block1 = raw_data[idx:idx + block1_size]
            idx += block1_size

            # block2: terrain indices (x * y * dbr_word bytes)
            block2_size = x * y * dbr_word
            idx += block2_size

            # block3: DBR strings + terrain painting
            block3_start = idx
            # First DBR entry (just string)
            dbr_str_size = struct.unpack_from('<I', raw_data, idx)[0]
            idx += 4 + dbr_str_size
            # Subsequent DBR entries (string + painting data)
            for j in range(1, dbr_count):
                dbr_str_size = struct.unpack_from('<I', raw_data, idx)[0]
                idx += 4 + dbr_str_size
                idx += (x - 1) * (y - 1)
            block3 = raw_data[block3_start:idx]
            block3_size = len(block3)

            # block4: remaining data
            block4_size = rlv_size - 36 - block1_size - block2_size - block3_size
            idx += block4_size

            # Calculate editor format size
            lvl_size = (4 * 4) + block3_size + (block1_size * 2) + (block1_size * 3) + ((x - 1) * (y - 1) * 4)

            # Write editor format header
            result += struct.pack('<6I', 0x06, lvl_size, 0, x, y, dbr_count)

            # Write block3 (DBR strings + painting)
            result += block3

            # Expand heightmap to pairs (height + zero)
            for j in range(x * y):
                val = struct.unpack_from('<f', block1, j * 4)[0]
                result += struct.pack('<ff', val, 0.0)

            # Expand heightmap to triples (height + zero + zero)
            for j in range(x * y):
                val = struct.unpack_from('<f', block1, j * 4)[0]
                result += struct.pack('<fff', val, 0.0, 0.0)

            # Zeroed data for (x-1)*(y-1) uint32s
            result += b'\x00' * ((x - 1) * (y - 1) * 4)

        else:
            # Non-terrain section: copy as-is
            result += struct.pack('<II', sec_type, sec_size)
            idx += 8
            if sec_size > 0 and idx + sec_size <= len(raw_data):
                result += raw_data[idx:idx + sec_size]
                idx += sec_size
            elif sec_size > 0:
                # Truncated section, copy what we can
                result += raw_data[idx:]
                break

    return bytes(result)


def main():
    map_source = sys.argv[1] if len(sys.argv) > 1 else 'sv'  # 'sv' or 'svaera'
    
    if map_source == 'sv':
        arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
        out_dir = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_sv')
    else:
        arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
        out_dir = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_svaera')

    print(f'Loading {map_source} map from {arc_path}...')
    arc = ArcArchive.from_file(arc_path)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sections = parse_sections(data)
    sec_map = {s['type']: s for s in sections}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    
    print(f'  {len(levels)} levels, {len(data)/(1024**2):.1f} MB')
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Decompile each level to .rlv (raw) and .lvl (editor format)
    success = 0
    failed = 0
    for i, lv in enumerate(levels):
        fname = lv['fname'].replace('/', '\\')
        raw = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        
        # Create directory structure
        rlv_path = out_dir / fname.replace('.lvl', '.rlv').replace('.LVL', '.rlv')
        lvl_path = out_dir / fname
        rlv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write raw .rlv
        rlv_path.write_bytes(raw)
        
        # Decompile to editor .lvl
        try:
            editor_data = decompile_level(raw)
            lvl_path.write_bytes(editor_data)
            success += 1
        except Exception as e:
            # If decompilation fails, write raw data as .lvl too (fallback)
            lvl_path.write_bytes(raw)
            failed += 1
            if failed <= 5:
                print(f'  WARN: Failed to decompile {fname}: {e}')
        
        if (i + 1) % 500 == 0:
            print(f'  Decompiled {i+1}/{len(levels)}...')
    
    print(f'\nDecompiled: {success} success, {failed} failed')
    print(f'Output: {out_dir}')
    
    del data


if __name__ == '__main__':
    main()
