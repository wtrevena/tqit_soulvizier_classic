#!/usr/bin/env python3
"""
Extract real world coordinates from 0x05 sections.

v0x0e 0x05 format:
  uint32 string_count
  string_count × (uint32 len + char[len])     -- DBR string table
  uint32 instance_count
  instance_count × 56-byte records:
    +0:  uint32 string_index
    +4:  float[9] rotation_matrix (3x3, stored as 3 rows of 3 floats with 1 pad zero each)
         Row0: bytes 4-15 (3 floats: r00,r01,r02) + byte 16-19 (pad 0)
         Row1: bytes 20-31 (3 floats: r10,r11,r12) + byte 32-35 (pad 0)
         Row2: bytes 36-39 (1 float: r20) -- only first component before position
    +40: float[3] world_position (X, Y, Z)
    +52: uint32 flags
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

sv_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
RECORD_SIZE = 56


def parse_blob_sections(blob):
    sections = []
    if len(blob) < 4:
        return sections, 0
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


def parse_0x05_v0e(data, label):
    """Parse v0x0e 0x05 section with 56-byte instance records."""
    if len(data) < 4:
        return None

    string_count = struct.unpack_from('<I', data, 0)[0]
    print(f"\n{'='*80}")
    print(f"  [{label}] 0x05: {len(data)} bytes, string_count={string_count}")

    pos = 4
    strings = []
    for i in range(string_count):
        if pos + 4 > len(data):
            break
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        if pos + slen > len(data):
            break
        strings.append(data[pos:pos + slen].decode('ascii', errors='replace'))
        pos += slen

    string_block_end = pos
    trailing = data[string_block_end:]
    print(f"  Strings: {len(strings)}, string block ends at {string_block_end}")
    print(f"  Trailing data: {len(trailing)} bytes")

    if len(trailing) < 4:
        return {'strings': strings, 'instances': []}

    instance_count = struct.unpack_from('<I', trailing, 0)[0]
    record_data_size = len(trailing) - 4
    expected_size = instance_count * RECORD_SIZE
    extra_trailing = record_data_size - expected_size

    print(f"  instance_count = {instance_count}")
    print(f"  Expected record data: {expected_size}, actual: {record_data_size}, extra: {extra_trailing}")

    instances = []
    ipos = 4
    for idx in range(instance_count):
        if ipos + RECORD_SIZE > len(trailing):
            print(f"  !! Truncated at instance {idx}")
            break

        rec = trailing[ipos:ipos + RECORD_SIZE]
        str_idx = struct.unpack_from('<I', rec, 0)[0]

        r00, r01, r02 = struct.unpack_from('<3f', rec, 4)
        pad0 = struct.unpack_from('<f', rec, 16)[0]
        r10, r11, r12 = struct.unpack_from('<3f', rec, 20)
        pad1 = struct.unpack_from('<f', rec, 32)[0]
        r20 = struct.unpack_from('<f', rec, 36)[0]

        wx, wy, wz = struct.unpack_from('<3f', rec, 40)
        flags = struct.unpack_from('<I', rec, 52)[0]

        str_name = strings[str_idx] if str_idx < len(strings) else f"??idx={str_idx}"
        short = str_name.split('\\')[-1].split('/')[-1]

        instances.append({
            'index': idx,
            'string_index': str_idx,
            'string': str_name,
            'short': short,
            'wx': wx, 'wy': wy, 'wz': wz,
            'rot': (r00, r01, r02, r10, r11, r12, r20),
            'flags': flags,
        })
        ipos += RECORD_SIZE

    print(f"\n  Parsed {len(instances)} instances")

    for i, inst in enumerate(instances):
        tag = ""
        if 'drxmap' in inst['string'].lower():
            tag = " [DRXMAP]"
        elif 'merchant' in inst['string'].lower():
            tag = " [MERCHANT]"
        elif 'proxy' in inst['string'].lower():
            tag = " [PROXY]"
        elif 'portal' in inst['string'].lower():
            tag = " [PORTAL]"
        elif 'trigger' in inst['string'].lower():
            tag = " [TRIGGER]"
        print(f"    [{i:3d}] str={inst['string_index']:3d} pos=({inst['wx']:8.2f}, {inst['wy']:8.2f}, {inst['wz']:8.2f}) flags={inst['flags']}{tag}  {inst['short']}")

    return {'strings': strings, 'instances': instances}


def highlight_objects(result, search_terms):
    if not result:
        return
    print(f"\n  --- Highlighted Objects ---")
    for term in search_terms:
        tl = term.lower()
        matches = [i for i in result['instances'] if tl in i['string'].lower()]
        if matches:
            for m in matches:
                print(f"  ** '{term}' => instance[{m['index']}] str[{m['string_index']}]")
                print(f"     DBR: {m['string']}")
                print(f"     World XYZ: ({m['wx']:.4f}, {m['wy']:.4f}, {m['wz']:.4f})")
                print(f"     Flags: {m['flags']}")
        else:
            print(f"  -- '{term}': not found")


def coord_extremes(result):
    if not result or not result['instances']:
        return
    insts = result['instances']
    print(f"\n  --- World Coordinate Ranges ({len(insts)} instances) ---")
    for axis, key in [('X', 'wx'), ('Y', 'wy'), ('Z', 'wz')]:
        vals = [i[key] for i in insts]
        mn_i = min(insts, key=lambda i: i[key])
        mx_i = max(insts, key=lambda i: i[key])
        print(f"  {axis}: {min(vals):.2f} to {max(vals):.2f}")
        print(f"    Min: [{mn_i['index']}] ({mn_i['wx']:.2f}, {mn_i['wy']:.2f}, {mn_i['wz']:.2f}) {mn_i['short']}")
        print(f"    Max: [{mx_i['index']}] ({mx_i['wx']:.2f}, {mx_i['wy']:.2f}, {mx_i['wz']:.2f}) {mx_i['short']}")


def main():
    print("Loading SV 0.98i Levels.arc...")
    sv_arc = ArcArchive.from_file(sv_arc_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    sv_by_name = {}
    for i, lv in enumerate(sv_levels):
        sv_by_name[lv['fname'].replace('\\', '/').lower()] = i
    print(f"  {len(sv_levels)} levels")

    # === DelphiLowlands04 ===
    t1 = 'levels/world/greece/delphi/delphilowlands04.lvl'
    print(f"\n{'#'*80}")
    print(f"# {t1}")
    print(f"{'#'*80}")
    if t1 in sv_by_name:
        lv = sv_levels[sv_by_name[t1]]
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        secs, magic = parse_blob_sections(blob)
        sec_05 = [s for s in secs if s['type'] == 0x05]
        if sec_05:
            r1 = parse_0x05_v0e(sec_05[0]['data'], 'DelphiLowlands04')
            highlight_objects(r1, [
                'merchant_delphi_occulttent01',
                'Merchant_Delphi_Quest',
                'drxmap',
                'cage_binding',
                'fog_occult',
                'blooddemon',
                'JG10b',
            ])
            coord_extremes(r1)

    # === crypt_floor1 ===
    t2 = 'levels/world/uberdungeon/crypt_floor1.lvl'
    print(f"\n{'#'*80}")
    print(f"# {t2}")
    print(f"{'#'*80}")
    if t2 in sv_by_name:
        lv = sv_levels[sv_by_name[t2]]
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        secs, magic = parse_blob_sections(blob)
        sec_05 = [s for s in secs if s['type'] == 0x05]
        if sec_05:
            r2 = parse_0x05_v0e(sec_05[0]['data'], 'crypt_floor1')
            highlight_objects(r2, [
                'portal_olympianarena2',
                'goldenchest',
                'deathstalker',
                'fellminotaur',
                'ghost',
            ])
            coord_extremes(r2)

    del sv_data
    print("\nDone!")


if __name__ == '__main__':
    main()
