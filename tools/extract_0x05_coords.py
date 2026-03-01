#!/usr/bin/env python3
"""
Extract object coordinates from 0x05 sections of specific levels.
Parses: string_count, DBR strings, instance records with XYZ coordinates.
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

sv_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')


def parse_blob_sections(blob):
    sections = []
    if len(blob) < 4:
        return sections
    magic_val = struct.unpack_from('<I', blob, 0)[0]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections, magic_val


def parse_0x05_full(data, label):
    """Parse 0x05 section: strings block + instance records."""
    if len(data) < 4:
        print(f"  [{label}] 0x05 section too small: {len(data)} bytes")
        return None

    string_count = struct.unpack_from('<I', data, 0)[0]
    print(f"\n{'='*80}")
    print(f"  [{label}] 0x05 Section: {len(data)} bytes")
    print(f"  string_count = {string_count}")
    print(f"{'='*80}")

    # Parse all strings
    pos = 4
    strings = []
    for i in range(string_count):
        if pos + 4 > len(data):
            print(f"  !! EOF reading string {i} length at pos {pos}")
            break
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        if pos + slen > len(data):
            print(f"  !! EOF reading string {i} data at pos {pos}, need {slen}")
            break
        s = data[pos:pos + slen].decode('ascii', errors='replace')
        strings.append(s)
        pos += slen

    string_block_end = pos
    trailing = data[string_block_end:]
    trailing_size = len(trailing)

    print(f"\n  String block: bytes 4..{string_block_end} ({string_block_end - 4} bytes)")
    print(f"  Trailing (instance) data: bytes {string_block_end}..{len(data)} ({trailing_size} bytes)")

    print(f"\n  --- All {len(strings)} DBR strings ---")
    for i, s in enumerate(strings):
        print(f"    [{i:3d}] {s}")

    if trailing_size == 0:
        print("  No instance records (trailing data is empty)")
        return {
            'string_count': string_count,
            'strings': strings,
            'instances': [],
            'trailing_raw': trailing,
        }

    # v0x0e format: instance records follow strings
    # Try parsing as variable-length records: each has
    #   uint32 string_index
    #   float x, y, z  (world coordinates)
    #   float rx, ry, rz (rotation - Euler or quaternion component)
    #   float scale (or uint32 flags)
    #   possibly more fields
    #
    # Strategy: parse record-by-record, trying to detect boundaries by
    # looking for valid string indices followed by reasonable float coords.

    instances = []

    # First, try the "count + fixed stride" approach for various record sizes
    first_uint = struct.unpack_from('<I', trailing, 0)[0]
    print(f"\n  First uint32 of trailing: {first_uint}")

    # Try interpreting WITHOUT a leading count (v0x0e may just be records)
    # Also try WITH a leading count
    best_parse = None
    for has_count in [True, False]:
        for rec_size in [56, 52, 48, 44, 40, 36, 32, 28, 24, 20, 16, 60, 64]:
            start_off = 4 if has_count else 0
            count_val = first_uint if has_count else None
            usable = trailing_size - start_off

            if has_count and count_val > 0 and count_val < 10000:
                expected = count_val * rec_size
                if expected == usable:
                    print(f"  ** MATCH: has_count={has_count}, count={count_val}, rec_size={rec_size}, total={usable}")
                    if best_parse is None or has_count:
                        best_parse = (has_count, count_val, rec_size, start_off)
            elif not has_count:
                if usable % rec_size == 0:
                    implied_count = usable // rec_size
                    if 50 < implied_count < 1000:
                        print(f"  ** MATCH (no count): rec_size={rec_size}, implied_count={implied_count}")
                        if best_parse is None:
                            best_parse = (False, implied_count, rec_size, 0)

    if best_parse:
        has_count, inst_count, rec_size, start_off = best_parse
        print(f"\n  Using: has_count={has_count}, count={inst_count}, rec_size={rec_size}")

        ipos = start_off
        for idx in range(inst_count):
            if ipos + rec_size > trailing_size:
                break

            rec_data = trailing[ipos:ipos + rec_size]
            n_fields = rec_size // 4
            fields_u = [struct.unpack_from('<I', rec_data, i*4)[0] for i in range(n_fields)]
            fields_f = [struct.unpack_from('<f', rec_data, i*4)[0] for i in range(n_fields)]

            str_idx = fields_u[0]
            x, y, z = fields_f[1], fields_f[2], fields_f[3]
            str_name = strings[str_idx] if str_idx < len(strings) else f"??idx={str_idx}"

            inst = {
                'index': idx,
                'string_index': str_idx,
                'string': str_name,
                'x': x, 'y': y, 'z': z,
                'extra_u': fields_u[4:],
                'extra_f': fields_f[4:],
            }
            instances.append(inst)

            short_name = str_name.split('/')[-1] if '/' in str_name else str_name
            coords_valid = all(abs(v) < 1e6 for v in [x, y, z])
            flag = " " if coords_valid else " (!)"
            extra_str = ""
            if idx < 10:
                ef = []
                for eu, ef_val in zip(fields_u[4:], fields_f[4:]):
                    if abs(ef_val) < 1e5 and abs(ef_val) > 1e-6:
                        ef.append(f"{ef_val:.4f}")
                    else:
                        ef.append(f"0x{eu:08x}")
                extra_str = f" extra=[{', '.join(ef)}]"
            print(f"    [{idx:3d}] str={str_idx:3d} XYZ=({x:10.2f}, {y:10.2f}, {z:10.2f}){flag} {short_name}{extra_str}")

            ipos += rec_size
    else:
        print("  No exact stride match found. Trying brute-force variable-length parse...")
        # Try variable-length: each record = string_index(4) + some_size(4) + payload
        # Or just scan for valid string_index + float triples
        ipos = 0
        while ipos + 16 <= trailing_size:
            str_idx = struct.unpack_from('<I', trailing, ipos)[0]
            if str_idx < len(strings):
                x = struct.unpack_from('<f', trailing, ipos + 4)[0]
                y = struct.unpack_from('<f', trailing, ipos + 8)[0]
                z = struct.unpack_from('<f', trailing, ipos + 12)[0]
                if all(abs(v) < 1e5 for v in [x, y, z]):
                    str_name = strings[str_idx]
                    short_name = str_name.split('/')[-1]
                    instances.append({
                        'index': len(instances),
                        'string_index': str_idx,
                        'string': str_name,
                        'x': x, 'y': y, 'z': z,
                        'extra_u': [], 'extra_f': [],
                    })
                    print(f"    [{len(instances)-1}] @{ipos} str={str_idx} XYZ=({x:.2f}, {y:.2f}, {z:.2f}) {short_name}")
            ipos += 4

    # Also dump first 512 bytes of trailing as hex for deep analysis
    print(f"\n  --- First 512 bytes of trailing data (hex dump) ---")
    for i in range(0, min(len(trailing), 512), 16):
        chunk = trailing[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        # Also show as floats
        floats = []
        for fi in range(0, len(chunk) - 3, 4):
            fv = struct.unpack_from('<f', chunk, fi)[0]
            floats.append(f"{fv:12.4f}")
        print(f"    {i:04x}: {hex_part:<48s}  {ascii_part}  | {' '.join(floats)}")

    return {
        'string_count': string_count,
        'strings': strings,
        'instances': instances,
        'trailing_raw': trailing,
    }


def find_objects(result, search_terms):
    """Find objects matching any of the search terms."""
    if not result:
        return
    print(f"\n  --- Search Results ---")
    for term in search_terms:
        term_lower = term.lower()
        matches = [inst for inst in result['instances'] if term_lower in inst['string'].lower()]
        if matches:
            for m in matches:
                print(f"  FOUND '{term}': instance[{m['index']}] str[{m['string_index']}]")
                print(f"    DBR: {m['string']}")
                print(f"    XYZ: ({m['x']:.4f}, {m['y']:.4f}, {m['z']:.4f})")
        else:
            print(f"  NOT FOUND: '{term}'")


def find_extremes(result):
    """Find objects at coordinate extremes (edges of the level)."""
    if not result or not result['instances']:
        return
    insts = result['instances']
    valid = [i for i in insts if all(abs(v) < 1e6 for v in [i['x'], i['y'], i['z']])]
    if not valid:
        print("  No valid coordinate instances found")
        return

    print(f"\n  --- Coordinate Extremes ({len(valid)} valid instances) ---")
    for axis, key in [('X', 'x'), ('Y', 'y'), ('Z', 'z')]:
        vals = [i[key] for i in valid]
        mn, mx = min(vals), max(vals)
        min_inst = min(valid, key=lambda i: i[key])
        max_inst = max(valid, key=lambda i: i[key])
        print(f"  {axis} range: {mn:.2f} to {mx:.2f}")
        short_min = min_inst['string'].split('/')[-1]
        short_max = max_inst['string'].split('/')[-1]
        print(f"    Min: [{min_inst['index']}] ({min_inst['x']:.2f}, {min_inst['y']:.2f}, {min_inst['z']:.2f}) {short_min}")
        print(f"    Max: [{max_inst['index']}] ({max_inst['x']:.2f}, {max_inst['y']:.2f}, {max_inst['z']:.2f}) {short_max}")


def main():
    print("Loading SV 0.98i Levels.arc...")
    sv_arc = ArcArchive.from_file(sv_arc_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}
    print(f"  Loaded {len(sv_levels)} levels")

    # === DelphiLowlands04 ===
    target1 = 'levels/world/greece/delphi/delphilowlands04.lvl'
    print(f"\n\n{'#'*80}")
    print(f"# TARGET 1: {target1}")
    print(f"{'#'*80}")

    if target1 in sv_by_name:
        lv = sv_levels[sv_by_name[target1]]
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        secs, magic = parse_blob_sections(blob)
        magic_ver = (magic >> 24) & 0xFF
        print(f"  Magic: 0x{magic:08x} (version byte: 0x{magic_ver:02x})")
        sec_info = [(hex(s['type']), s['size']) for s in secs]
        print(f"  Sections: {sec_info}")

        sec_05 = [s for s in secs if s['type'] == 0x05]
        if sec_05:
            result1 = parse_0x05_full(sec_05[0]['data'], 'DelphiLowlands04')
            find_objects(result1, [
                'merchant_delphi_occulttent01',
                'merchant',
                'occulttent',
                'waterfall',
                'portal',
                'drxmap',
                'proxy',
            ])
            find_extremes(result1)
        else:
            print("  No 0x05 section found!")
    else:
        print(f"  Level not found: {target1}")

    # === crypt_floor1 ===
    crypt_candidates = [k for k in sv_by_name if 'crypt' in k and 'floor1' in k]
    print(f"\n\n{'#'*80}")
    print(f"# TARGET 2: crypt_floor1")
    print(f"  Candidates: {crypt_candidates}")
    print(f"{'#'*80}")

    for target2 in crypt_candidates:
        lv = sv_levels[sv_by_name[target2]]
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        secs, magic = parse_blob_sections(blob)
        magic_ver = (magic >> 24) & 0xFF
        print(f"\n  {target2}")
        print(f"  Magic: 0x{magic:08x} (version byte: 0x{magic_ver:02x})")
        sec_info2 = [(hex(s['type']), s['size']) for s in secs]
        print(f"  Sections: {sec_info2}")

        sec_05 = [s for s in secs if s['type'] == 0x05]
        if sec_05:
            result2 = parse_0x05_full(sec_05[0]['data'], target2)
            find_objects(result2, [
                'drxmap',
                'portal',
                'proxy',
                'marker',
                'trigger',
                'chest',
                'boss',
            ])
            find_extremes(result2)
        else:
            print("  No 0x05 section found!")

    del sv_data
    print("\n\nDone!")


if __name__ == '__main__':
    main()
