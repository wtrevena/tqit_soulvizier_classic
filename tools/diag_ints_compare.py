#!/usr/bin/env python3
"""Compare ints_raw between SV, SVAERA, and MapCompiler for shared+drxmap levels."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index,
    SEC_LEVELS)

def load_map(path, label):
    print(f'Loading {label}...')
    if path.suffix == '.arc':
        arc = ArcArchive.from_file(path)
        data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    else:
        data = path.read_bytes()
    sections = parse_sections(data)
    sec_map = {s['type']: s for s in sections}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    return data, levels

sv_data, sv_levels = load_map(
    Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'), 'SV')
ae_data, ae_levels = load_map(
    Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'), 'SVAERA')
mc_data, mc_levels = load_map(
    Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map'), 'MapCompiler')

# Build name indices
ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i
mc_by_name = {}
for i, lv in enumerate(mc_levels):
    mc_by_name[lv['fname'].replace('\\', '/').lower()] = i

# Find all shared+drxmap levels
print(f'\nComparing ints_raw for shared+drxmap levels:')
print(f'{"Level":<45} {"idx":>4} {"SV vs AE diff":>30} {"SV vs MC diff":>30}')
print('-' * 115)

for sv_lv in sv_levels:
    key = sv_lv['fname'].replace('\\', '/').lower()
    chunk = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
    if b'drxmap' not in chunk:
        continue
    ae_idx = ae_by_name.get(key)
    mc_idx = mc_by_name.get(key)
    if ae_idx is None:
        continue  # SV-only level

    ae_lv = ae_levels[ae_idx]
    sv_ints = struct.unpack_from('<13I', sv_lv['ints_raw'])
    ae_ints = struct.unpack_from('<13I', ae_lv['ints_raw'])

    mc_ints = None
    if mc_idx is not None:
        mc_ints = struct.unpack_from('<13I', mc_levels[mc_idx]['ints_raw'])

    short = sv_lv['fname'].split('\\')[-1]

    # Find differences
    ae_diffs = []
    mc_diffs = []
    for j in range(13):
        sv_v = sv_ints[j] if sv_ints[j] < 2**31 else sv_ints[j] - 2**32
        ae_v = ae_ints[j] if ae_ints[j] < 2**31 else ae_ints[j] - 2**32
        if sv_ints[j] != ae_ints[j]:
            ae_diffs.append(f'[{j}]:{sv_v}->{ae_v}(d={ae_v-sv_v})')
        if mc_ints is not None and sv_ints[j] != mc_ints[j]:
            mc_v = mc_ints[j] if mc_ints[j] < 2**31 else mc_ints[j] - 2**32
            mc_diffs.append(f'[{j}]:{sv_v}->{mc_v}(d={mc_v-sv_v})')

    ae_str = ', '.join(ae_diffs) if ae_diffs else 'IDENTICAL'
    mc_str = ', '.join(mc_diffs) if mc_diffs else ('IDENTICAL' if mc_ints else 'N/A')
    print(f'{short:<45} {ae_idx:4d}  {ae_str}')
    if mc_str != ae_str:
        print(f'{"":45} {"":4}  MC: {mc_str}')

# Detailed comparison for target levels
print('\n' + '='*80)
print('Detailed ints_raw for HiddenValley01 and Random09A:')
for target in ['hiddenvalley01', 'random09a']:
    print(f'\n  {target}:')
    sv_idx = None
    for i, lv in enumerate(sv_levels):
        if target in lv['fname'].lower():
            sv_idx = i
            break
    ae_idx_found = None
    for key in ae_by_name:
        if target in key:
            ae_idx_found = ae_by_name[key]
            break
    mc_idx_found = None
    for key in mc_by_name:
        if target in key:
            mc_idx_found = mc_by_name[key]
            break

    if sv_idx is None:
        continue

    sv_ints = struct.unpack_from('<13I', sv_levels[sv_idx]['ints_raw'])
    ae_ints = struct.unpack_from('<13I', ae_levels[ae_idx_found]['ints_raw']) if ae_idx_found is not None else None
    mc_ints = struct.unpack_from('<13I', mc_levels[mc_idx_found]['ints_raw']) if mc_idx_found is not None else None

    for j in range(13):
        sv_v = sv_ints[j]
        ae_v = ae_ints[j] if ae_ints else '?'
        mc_v = mc_ints[j] if mc_ints else '?'
        marker = ''
        if ae_ints and sv_ints[j] != ae_ints[j]:
            marker = ' <-- DIFF'
        print(f'    [{j:2d}] SV={sv_v:>12}  AE={ae_v:>12}  MC={mc_v:>12}{marker}')
