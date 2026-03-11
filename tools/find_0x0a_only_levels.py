#!/usr/bin/env python3
"""
Find SVAERA levels that have section 0x0a (PTH\x04) but NO section 0x0b (REC\x02).
Also reports levels with NEITHER 0x0a nor 0x0b.
"""
import sys, struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections


def main():
    svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic'
                       r'\reference_mods\SVAERA_customquest\Resources\Levels.arc')

    print('Loading SVAERA...')
    arc = ArcArchive.from_file(svaera_path)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec_map = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    print(f'  {len(levels)} levels loaded\n')

    has_0a_only = []     # 0x0a present, 0x0b absent
    has_neither = []     # neither 0x0a nor 0x0b
    has_both = 0
    has_0b_only = 0

    for idx, lv in enumerate(levels):
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if len(blob) < 4 or blob[:3] != b'LVL':
            has_neither.append((idx, lv, 0, set()))
            continue

        ver = blob[3]
        secs, _ = parse_blob_sections(blob)
        types = {s['type'] for s in secs}

        has_0a = 0x0a in types
        has_0b = 0x0b in types

        # Parse ints_raw for grid/dims info
        # 13 x int32:  [0]=?, [1]=?, [2]=?, [3]=half_w, [4]=?, [5]=half_h,
        #              [6]=grid_x, [7]=grid_y, [8]=grid_z, [9..12]=GUID
        ir = struct.unpack_from('<13i', lv['ints_raw'], 0)

        entry = (idx, lv, ver, types)

        if has_0a and not has_0b:
            has_0a_only.append(entry)
        elif not has_0a and not has_0b:
            has_neither.append(entry)
        elif has_0a and has_0b:
            has_both += 1
        else:
            has_0b_only += 1

    # --- Report: 0x0a only (no 0x0b) ---
    print('=' * 90)
    print(f'Levels with 0x0a (PTH) but NO 0x0b (REC): {len(has_0a_only)}')
    print('=' * 90)
    for idx, lv, ver, types in has_0a_only:
        ir = struct.unpack_from('<13i', lv['ints_raw'], 0)
        fname = lv['fname'].replace('\\', '/')
        grid = (ir[6], ir[7], ir[8])
        dims = (ir[3], ir[5])
        sec_list = sorted(types)
        print(f'  idx={idx:4d}  ver=0x{ver:02x}  grid=({grid[0]:5d},{grid[1]:5d},{grid[2]:5d})'
              f'  dims=({dims[0]:3d},{dims[1]:3d})  fname={fname}')
        print(f'           sections: {["0x%02x" % t for t in sec_list]}')

    # --- Report: neither 0x0a nor 0x0b ---
    print()
    print('=' * 90)
    print(f'Levels with NEITHER 0x0a nor 0x0b: {len(has_neither)}')
    print('=' * 90)
    for idx, lv, ver, types in has_neither:
        ir = struct.unpack_from('<13i', lv['ints_raw'], 0)
        fname = lv['fname'].replace('\\', '/')
        grid = (ir[6], ir[7], ir[8])
        dims = (ir[3], ir[5])
        sec_list = sorted(types)
        print(f'  idx={idx:4d}  ver=0x{ver:02x}  grid=({grid[0]:5d},{grid[1]:5d},{grid[2]:5d})'
              f'  dims=({dims[1]:3d},{dims[0]:3d})  fname={fname}')
        print(f'           sections: {["0x%02x" % t for t in sec_list]}')

    # --- Summary ---
    print()
    print('=' * 90)
    print('Summary:')
    print(f'  0x0a only (no 0x0b): {len(has_0a_only)}')
    print(f'  0x0b only (no 0x0a): {has_0b_only}')
    print(f'  Both 0x0a and 0x0b:  {has_both}')
    print(f'  Neither:             {len(has_neither)}')
    print(f'  Total:               {len(levels)}')


if __name__ == '__main__':
    main()
