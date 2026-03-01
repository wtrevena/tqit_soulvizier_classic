#!/usr/bin/env python3
"""Find which levels contain references to bloodcave portals/entrances."""
import sys
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

keywords = [b'bloodcave', b'blood_cave', b'portal', b'secretdoor', b'secret_door',
            b'hidden_door', b'hiddendoor', b'gardenofmerchants', b'garden_of_merchants',
            b'boss_arena', b'uberdungeon']

print('=== ALL levels containing bloodcave/portal/secret/garden refs ===')
for lv in sv_levels:
    fn = lv['fname']
    blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    lower_blob = blob.lower()
    
    matches = []
    for kw in keywords:
        if kw in lower_blob:
            matches.append(kw.decode())
    
    if matches:
        key = fn.replace('\\', '/').lower()
        tag = '(SV-only)' if key not in ae_names else '(shared)'
        print(f'  {fn} {tag}: {", ".join(matches)}')

print()
print('=== All drxmap strings across ALL shared levels ===')
for lv in sv_levels:
    fn = lv['fname']
    key = fn.replace('\\', '/').lower()
    if key in ae_names:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if b'drxmap' in blob:
            strings = set()
            i = 0
            while i < len(blob):
                idx = blob.find(b'drxmap', i)
                if idx == -1:
                    break
                start = blob.rfind(b'\x00', max(0, idx - 200), idx)
                start = start + 1 if start >= 0 else idx
                end = blob.find(b'\x00', idx)
                if end == -1:
                    break
                s = blob[start:end].decode('ascii', errors='replace')
                strings.add(s)
                i = end + 1
            if strings:
                print(f'\n  {fn}:')
                for s in sorted(strings):
                    # Clean trailing non-printable
                    clean = ''.join(c for c in s if c.isprintable())
                    print(f'    {clean}')

del sv_data, ae_data
