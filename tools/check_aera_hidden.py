#!/usr/bin/env python3
"""Check if SVAERA added hidden doors/portals/secret areas near Delphi/Crisaeos."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec_map = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])

sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
sv_names = {lv['fname'].replace('\\', '/').lower(): lv for lv in sv_levels}

keywords = [b'secret', b'hidden', b'portal', b'door', b'entrance', b'crisaeos', b'falls', b'dyngridentrance']

print('=== SVAERA Delphi levels: searching for hidden/secret/portal/door refs ===')
for lv in ae_levels:
    fn = lv['fname']
    if 'delphi' in fn.lower():
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        lower_blob = blob.lower()
        matches = []
        for kw in keywords:
            if kw in lower_blob:
                matches.append(kw.decode())
        if matches:
            print(f'\n  {fn}: {", ".join(matches)}')
            # Extract all strings containing the keywords
            i = 0
            found = set()
            while i < len(blob):
                for prefix in [b'records/', b'xpack/', b'levels/']:
                    idx = blob.find(prefix, i)
                    if idx != -1:
                        break
                else:
                    break
                end = blob.find(b'\x00', idx)
                if end == -1:
                    break
                s = blob[idx:end].decode('ascii', errors='replace')
                sl = s.lower()
                for kw in keywords:
                    if kw.decode() in sl:
                        found.add(s)
                        break
                i = end + 1
            for s in sorted(found):
                print(f'    {s}')

print('\n\n=== SVAERA-only levels (not in SV 0.98i) ===')
for lv in ae_levels:
    key = lv['fname'].replace('\\', '/').lower()
    if key not in sv_names:
        print(f'  {lv["fname"]}')

print('\n\n=== SVAERA Delphi: ALL unique DBR strings (to find anything custom) ===')
for lv in ae_levels:
    fn = lv['fname']
    if 'delphilowlands' in fn.lower():
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        strings = set()
        i = 0
        while i < len(blob):
            idx = blob.find(b'records/', i)
            if idx == -1:
                break
            end = blob.find(b'\x00', idx)
            if end == -1:
                break
            s = blob[idx:end].decode('ascii', errors='replace')
            strings.add(s)
            i = end + 1
        # Compare with SV version
        sv_key = fn.replace('\\', '/').lower()
        sv_strings = set()
        if sv_key in sv_names:
            sv_lv = sv_names[sv_key]
            sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
            j = 0
            while j < len(sv_blob):
                idx2 = sv_blob.find(b'records/', j)
                if idx2 == -1:
                    break
                end2 = sv_blob.find(b'\x00', idx2)
                if end2 == -1:
                    break
                s2 = sv_blob[idx2:end2].decode('ascii', errors='replace')
                sv_strings.add(s2)
                j = end2 + 1
        
        ae_only = strings - sv_strings
        if ae_only:
            print(f'\n  {fn} - SVAERA-only strings (not in SV):')
            for s in sorted(ae_only):
                print(f'    {s}')
        else:
            sv_only = sv_strings - strings
            if sv_only:
                print(f'\n  {fn} - SV-only strings (stripped by SVAERA):')
                for s in sorted(sv_only):
                    print(f'    {s}')
            else:
                print(f'\n  {fn} - identical string sets')

del ae_data, sv_data
