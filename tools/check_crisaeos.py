#!/usr/bin/env python3
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])

ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
ae_names = set(lv['fname'].replace('\\', '/').lower() for lv in ae_levels)

print('=== SV-only levels (not in SVAERA) ===')
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    if key not in ae_names:
        print(f'  {lv["fname"]}')

print()
print('=== Levels with crisaeos/falls in name ===')
for lv in sv_levels:
    fn = lv['fname'].lower()
    if 'crisaeos' in fn or 'falls' in fn:
        key = fn.replace('\\', '/')
        tag = '(SV-only)' if key not in ae_names else '(shared)'
        print(f'  {lv["fname"]} {tag}')

print()
print('=== Levels near Delphi area ===')
for lv in sv_levels:
    fn = lv['fname'].lower()
    if 'delphi' in fn:
        key = fn.replace('\\', '/')
        tag = '(SV-only)' if key not in ae_names else '(shared)'
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        has_drx = 'drxmap' if b'drxmap' in blob else ''
        print(f'  {lv["fname"]} {tag} {has_drx}')

del sv_data, ae_data
