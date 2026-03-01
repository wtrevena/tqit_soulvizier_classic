#!/usr/bin/env python3
"""Compare level ordering between binary merge and MapCompiler output."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

# Load MapCompiler merged output
print('Loading MapCompiler merged...')
mc_data = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map').read_bytes()
mc_sections = parse_sections(mc_data)
mc_sec_map = {s['type']: s for s in mc_sections}
mc_levels = parse_level_index(mc_data, mc_sec_map[SEC_LEVELS])

# Load SVAERA
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sections = parse_sections(ae_data)
ae_sec_map = {s['type']: s for s in ae_sections}
ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])

# Load SV
print('Loading SV...')
sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sections = parse_sections(sv_data)
sv_sec_map = {s['type']: s for s in sv_sections}
sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])

# My binary merge order: first 2235 = SVAERA order, then 46 = SV-only order
ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i
sv_only = [lv for lv in sv_levels if lv['fname'].replace('\\', '/').lower() not in ae_by_name]

my_order = [lv['fname'].replace('\\', '/').lower() for lv in ae_levels]
for lv in sv_only:
    my_order.append(lv['fname'].replace('\\', '/').lower())

mc_order = [lv['fname'].replace('\\', '/').lower() for lv in mc_levels]

print(f'\nMy binary merge: {len(my_order)} levels')
print(f'MapCompiler: {len(mc_order)} levels')

# Compare orders
if my_order == mc_order:
    print('SAME ORDER')
else:
    print('DIFFERENT ORDER!')
    mismatches = 0
    for i in range(min(len(my_order), len(mc_order))):
        if my_order[i] != mc_order[i]:
            mismatches += 1
            if mismatches <= 10:
                print(f'  [{i}] mine: {my_order[i][-50:]}')
                print(f'       mc:   {mc_order[i][-50:]}')
    print(f'  Total mismatches: {mismatches}')

    # Check if it's just a reordering
    my_set = set(my_order)
    mc_set = set(mc_order)
    only_mine = my_set - mc_set
    only_mc = mc_set - my_set
    print(f'  Only in mine: {len(only_mine)}')
    print(f'  Only in MC: {len(only_mc)}')
    if only_mine:
        for n in list(only_mine)[:3]:
            print(f'    mine-only: {n[-60:]}')
    if only_mc:
        for n in list(only_mc)[:3]:
            print(f'    mc-only: {n[-60:]}')

del ae_data, sv_data, mc_data
