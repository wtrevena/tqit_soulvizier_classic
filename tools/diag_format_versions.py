#!/usr/bin/env python3
"""Check level format versions across SVAERA and SV maps.
Identify which levels are v0x0e vs v0x11 in each map."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

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

ae_data, ae_levels = load_map(
    Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'), 'SVAERA')
sv_data, sv_levels = load_map(
    Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'), 'SV')

# Count format versions in SVAERA
ae_versions = {}
ae_0e_outdoor = []
for lv in ae_levels:
    blob = ae_data[lv['data_offset']:lv['data_offset'] + min(4, lv['data_length'])]
    if len(blob) >= 4 and blob[:3] == b'LVL':
        ver = blob[3]
        ae_versions[ver] = ae_versions.get(ver, 0) + 1
        if ver == 0x0e:
            fname = lv['fname'].replace('\\', '/')
            # Check if it's outdoor (contains World/ but not Underground/)
            is_outdoor = 'World/' in fname and 'Underground' not in fname and 'Undergrounds' not in fname
            if is_outdoor:
                ae_0e_outdoor.append(fname)

print(f'\nSVAERA level format versions:')
for ver, count in sorted(ae_versions.items()):
    print(f'  v0x{ver:02x}: {count} levels')

print(f'\nSVAERA v0x0e OUTDOOR levels ({len(ae_0e_outdoor)}):')
for f in ae_0e_outdoor[:20]:
    print(f'  {f}')
if len(ae_0e_outdoor) > 20:
    print(f'  ... and {len(ae_0e_outdoor) - 20} more')

# Count format versions in SV
sv_versions = {}
for lv in sv_levels:
    blob = sv_data[lv['data_offset']:lv['data_offset'] + min(4, lv['data_length'])]
    if len(blob) >= 4 and blob[:3] == b'LVL':
        ver = blob[3]
        sv_versions[ver] = sv_versions.get(ver, 0) + 1

print(f'\nSV level format versions:')
for ver, count in sorted(sv_versions.items()):
    print(f'  v0x{ver:02x}: {count} levels')

# Show all SVAERA v0x0e levels (both outdoor and underground)
ae_0e_all = []
for lv in ae_levels:
    blob = ae_data[lv['data_offset']:lv['data_offset'] + min(4, lv['data_length'])]
    if len(blob) >= 4 and blob[:3] == b'LVL' and blob[3] == 0x0e:
        ae_0e_all.append(lv['fname'].replace('\\', '/'))

print(f'\nALL SVAERA v0x0e levels ({len(ae_0e_all)}):')
for f in ae_0e_all:
    print(f'  {f}')

# Find levels ADJACENT to HiddenValley01 in SVAERA (same directory or related dirs)
print(f'\nLevels near HiddenValley01 in SVAERA:')
hidden_valley_levels = []
for lv in ae_levels:
    fname = lv['fname'].replace('\\', '/')
    if 'HiddenValley' in fname or 'SilkRoad' in fname:
        blob = ae_data[lv['data_offset']:lv['data_offset'] + min(4, lv['data_length'])]
        ver = blob[3] if len(blob) >= 4 and blob[:3] == b'LVL' else 0
        print(f'  {fname}: v0x{ver:02x}')
