#!/usr/bin/env python3
"""Parse GROUPS and SD sections to understand their format."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS, SEC_SD

def read_string(buf, idx):
    slen = struct.unpack_from('<I', buf, idx)[0]
    idx += 4
    s = buf[idx:idx + slen].decode('ascii', errors='replace')
    idx += slen
    return s, idx

def parse_groups_section(buf):
    """Parse the GROUPS section."""
    idx = 0
    unk0 = struct.unpack_from('<I', buf, idx)[0]; idx += 4
    count = struct.unpack_from('<I', buf, idx)[0]; idx += 4

    groups = []
    for i in range(count):
        group = {}
        group['type'] = struct.unpack_from('<I', buf, idx)[0]; idx += 4
        name, idx = read_string(buf, idx)
        group['name'] = name

        if group['type'] == 2:
            # Level group - contains level indices
            num_levels = struct.unpack_from('<I', buf, idx)[0]; idx += 4
            level_indices = []
            for _ in range(num_levels):
                li = struct.unpack_from('<I', buf, idx)[0]; idx += 4
                level_indices.append(li)
            group['level_indices'] = level_indices
        elif group['type'] == 1:
            # Region group
            num_sub = struct.unpack_from('<I', buf, idx)[0]; idx += 4
            subs = []
            for _ in range(num_sub):
                si = struct.unpack_from('<I', buf, idx)[0]; idx += 4
                subs.append(si)
            group['sub_indices'] = subs
        else:
            # Unknown type - try to read a count + indices
            num = struct.unpack_from('<I', buf, idx)[0]; idx += 4
            vals = []
            for _ in range(num):
                v = struct.unpack_from('<I', buf, idx)[0]; idx += 4
                vals.append(v)
            group['values'] = vals

        groups.append(group)

    return {'unknown': unk0, 'groups': groups, 'bytes_consumed': idx}

def parse_sd_section(buf):
    """Parse the SD (scene data) section."""
    idx = 0
    vals = []
    # Just read first 20 uint32s to understand structure
    for i in range(min(20, len(buf) // 4)):
        v = struct.unpack_from('<I', buf, idx)[0]
        vals.append(v)
        idx += 4
    return vals

for label, path in [
    ('SVAERA', r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'),
    ('SV 0.98i', r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'),
]:
    print(f'\n=== {label} ===')
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sections = parse_sections(data)
    sec_map = {s['type']: s for s in sections}

    levels = parse_level_index(data, sec_map[SEC_LEVELS])

    # Parse GROUPS
    groups_sec = sec_map[SEC_GROUPS]
    gbuf = data[groups_sec['data_offset']:groups_sec['data_offset'] + groups_sec['size']]
    try:
        parsed = parse_groups_section(gbuf)
        print(f'  GROUPS: unknown={parsed["unknown"]}, count={len(parsed["groups"])}, bytes_consumed={parsed["bytes_consumed"]}/{len(gbuf)}')

        # Show types distribution
        types = {}
        for g in parsed['groups']:
            t = g['type']
            types[t] = types.get(t, 0) + 1
        print(f'  Group types: {types}')

        # Show first 5 groups
        for g in parsed['groups'][:5]:
            if 'level_indices' in g:
                print(f'    type={g["type"]} name="{g["name"]}" levels={g["level_indices"][:5]}{"..." if len(g["level_indices"]) > 5 else ""}')
            elif 'sub_indices' in g:
                print(f'    type={g["type"]} name="{g["name"]}" subs={g["sub_indices"][:5]}{"..." if len(g["sub_indices"]) > 5 else ""}')
            else:
                print(f'    type={g["type"]} name="{g["name"]}" vals={g.get("values", [])[:5]}')

        # Show last 5 groups
        print(f'  ... last 5:')
        for g in parsed['groups'][-5:]:
            if 'level_indices' in g:
                print(f'    type={g["type"]} name="{g["name"]}" levels={g["level_indices"][:5]}{"..." if len(g["level_indices"]) > 5 else ""}')
            elif 'sub_indices' in g:
                print(f'    type={g["type"]} name="{g["name"]}" subs={g["sub_indices"][:5]}{"..." if len(g["sub_indices"]) > 5 else ""}')

        # Find groups containing high level indices (>= original level count for SV custom)
        if label == 'SV 0.98i':
            # Find groups with levels that would be SV-only
            sv_level_names = set()
            ae_arc2 = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
            ae_data2 = ae_arc2.decompress([e for e in ae_arc2.entries if e.entry_type == 3][0])
            ae_sections2 = parse_sections(ae_data2)
            ae_sec_map2 = {s['type']: s for s in ae_sections2}
            ae_levels2 = parse_level_index(ae_data2, ae_sec_map2[SEC_LEVELS])
            ae_names = set(lv['fname'].replace('\\', '/').lower() for lv in ae_levels2)
            del ae_data2

            print(f'\n  SV groups containing SV-only levels:')
            for g in parsed['groups']:
                if 'level_indices' in g:
                    for li in g['level_indices']:
                        if li < len(levels):
                            lname = levels[li]['fname'].replace('\\', '/').lower()
                            if lname not in ae_names:
                                print(f'    "{g["name"]}" contains SV-only level [{li}]={levels[li]["fname"][:50]}')
                                break

    except Exception as e:
        print(f'  GROUPS parse error: {e}')
        import traceback
        traceback.print_exc()

    del data
