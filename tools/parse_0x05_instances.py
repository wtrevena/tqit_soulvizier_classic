#!/usr/bin/env python3
"""
Parse 0x05 section completely: string list + instance placement records.
Determine exact record format to enable safe merging.
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

svaera_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')


def parse_blob_sections(blob):
    sections = []
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections


def read_strings(data):
    """Read the string block, return (strings_list, end_position)."""
    count = struct.unpack_from('<I', data, 0)[0]
    pos = 4
    strings = []
    for _ in range(count):
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        strings.append(data[pos:pos + slen])
        pos += slen
    return strings, pos


def analyze_trailing(data, trailing_start, num_types, label):
    """Analyze the trailing instance data to determine record format."""
    td = data[trailing_start:]
    if len(td) < 4:
        print(f'  [{label}] No trailing data')
        return

    instance_count = struct.unpack_from('<I', td, 0)[0]
    remaining = len(td) - 4
    print(f'  [{label}] Instance count: {instance_count}, remaining: {remaining} bytes')

    if instance_count == 0:
        return

    # Scan for record boundaries by looking at sequential type_index patterns
    # Records start with type_index (0..num_types-1), followed by data
    pos = 4
    records = []
    for i in range(instance_count):
        if pos + 4 > len(td):
            print(f'    Ran out of data at record {i}, pos={pos}')
            break
        type_idx = struct.unpack_from('<I', td, pos)[0]

        # Scan ahead to find next record boundary
        # Next record should start with a type_index in range [0, num_types)
        # We check at various offsets from current position
        found_next = False
        for candidate_size in range(48, 120, 4):
            next_pos = pos + candidate_size
            if next_pos >= len(td):
                # Last record - calculate size from remaining data
                rec_size = len(td) - pos
                records.append({'type_idx': type_idx, 'offset': pos, 'size': rec_size})
                found_next = True
                break
            if i + 1 < instance_count:
                next_val = struct.unpack_from('<I', td, next_pos)[0]
                if next_val < num_types:
                    # Could be a valid type_index for the next record
                    # Validate: the field after it should look like rotation data
                    if next_pos + 8 <= len(td):
                        next_field = struct.unpack_from('<f', td, next_pos + 4)[0]
                        # Rotation values are typically in [-1, 1] range or position values
                        if abs(next_field) < 10000:
                            records.append({'type_idx': type_idx, 'offset': pos, 'size': candidate_size})
                            pos = next_pos
                            found_next = True
                            break

        if not found_next:
            rec_size = len(td) - pos
            records.append({'type_idx': type_idx, 'offset': pos, 'size': rec_size})
            break

    # Analyze record sizes
    sizes = [r['size'] for r in records]
    unique_sizes = sorted(set(sizes))
    print(f'    Parsed {len(records)} records')
    print(f'    Record sizes: {unique_sizes}')
    for us in unique_sizes:
        cnt = sizes.count(us)
        print(f'      {us} bytes: {cnt} records ({100*cnt/len(records):.1f}%)')

    # Verify total
    total = 4 + sum(r['size'] for r in records)
    print(f'    Total: {total} bytes (actual trailing: {len(td)}, match: {total == len(td)})')

    # Show a few records
    for i in range(min(3, len(records))):
        r = records[i]
        rd = td[r['offset']:r['offset'] + r['size']]
        nf = r['size'] // 4
        vals = []
        for fi in range(nf):
            iv = struct.unpack_from('<I', rd, fi * 4)[0]
            fv = struct.unpack_from('<f', rd, fi * 4)[0]
            if abs(fv) < 100000 and abs(fv) > 0.001 and iv != 0:
                vals.append(f'{fv:>10.4f}')
            elif iv == 0:
                vals.append(f'{"0":>10}')
            else:
                vals.append(f'0x{iv:08x}')
        print(f'    Record {i} (type={r["type_idx"]}, {r["size"]} bytes): {vals}')

    # Find drxmap instances
    drxmap_records = [r for r in records if r['type_idx'] >= 0]
    return records


def main():
    print('Loading maps...')
    ae_arc = ArcArchive.from_file(svaera_arc)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}

    sv_arc_obj = ArcArchive.from_file(sv_arc)
    sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
    sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}

    targets = [
        'levels/world/greece/delphi/delphilowlands03.lvl',
        'levels/world/greece/delphi/delphilowlands04.lvl',
        'levels/world/orient/silkroad/hiddenvalleyborder04.lvl',
    ]

    for target in targets:
        print(f'\n{"="*70}')
        print(f'  {target}')
        print(f'{"="*70}')

        for label, data_src, levels, by_name in [
            ('SVAERA', ae_data, ae_levels, ae_by_name),
            ('SV', sv_data, sv_levels, sv_by_name),
        ]:
            if target not in by_name:
                continue
            lv = levels[by_name[target]]
            blob = data_src[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            secs = parse_blob_sections(blob)
            sec_05 = [s for s in secs if s['type'] == 0x05]
            if not sec_05:
                continue

            d = sec_05[0]['data']
            strings, str_end = read_strings(d)
            num_types = len(strings)
            print(f'\n  [{label}] {num_types} object types, string block ends at {str_end}')

            # Show drxmap strings
            drx_indices = [i for i, s in enumerate(strings) if b'drxmap' in s.lower()]
            if drx_indices:
                print(f'    drxmap types at indices: {drx_indices}')
                for di in drx_indices:
                    print(f'      [{di}] {strings[di].decode("ascii", errors="replace")}')

            analyze_trailing(d, str_end, num_types, label)

    del ae_data, sv_data


if __name__ == '__main__':
    main()
