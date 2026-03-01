#!/usr/bin/env python3
"""Identify which levels contain drxmap content and whether they're shared or SV-only."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

# Load SV
print('Loading SV...')
sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])

# Load SVAERA
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])

ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i

print('\n=== SV levels with drxmap content ===')
print('\n--- SHARED levels (exist in both, SV has drxmap) ---')
shared_drx = []
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    if key in ae_by_name and b'drxmap' in chunk:
        drx_count = chunk.count(b'drxmap')
        # Look for specific keywords
        has_merchant = b'merchant' in chunk.lower() or b'pitsprite' in chunk.lower()
        has_crisaeos = b'crisaeos' in chunk.lower() or b'greece' in chunk.lower()
        # Find all drxmap references
        drx_refs = []
        pos = 0
        while True:
            idx = chunk.find(b'drxmap', pos)
            if idx == -1:
                break
            # Extract surrounding context
            start = max(0, idx - 20)
            end = min(len(chunk), idx + 80)
            ctx = chunk[start:end]
            # Extract printable string around it
            text = ''.join(chr(b) if 32 <= b < 127 else '.' for b in ctx)
            drx_refs.append(text)
            pos = idx + 6
        
        shared_drx.append(lv['fname'])
        print(f'\n  {lv["fname"]} ({drx_count} drxmap refs, {lv["data_length"]} bytes)')
        for ref in drx_refs[:5]:
            print(f'    {ref}')
        if len(drx_refs) > 5:
            print(f'    ... and {len(drx_refs)-5} more')

print(f'\n\n--- SV-ONLY levels (new areas, not in SVAERA) ---')
sv_only_drx = []
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    if key not in ae_by_name:
        chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        has_drx = b'drxmap' in chunk
        drx_count = chunk.count(b'drxmap') if has_drx else 0
        
        # Look for keywords
        text_chunk = chunk.lower()
        keywords = []
        for kw in [b'merchant', b'pitsprite', b'crisaeos', b'garden', b'blood', b'xurder', 
                    b'volcano', b'sprite', b'demon', b'purple', b'cave', b'fissure']:
            if kw in text_chunk:
                keywords.append(kw.decode())
        
        sv_only_drx.append((lv['fname'], drx_count, lv['data_length'], keywords))
        marker = ' [drxmap]' if has_drx else ''
        kw_str = f' keywords: {keywords}' if keywords else ''
        print(f'  {lv["fname"]} ({lv["data_length"]} bytes, {drx_count} drxmap refs){kw_str}')

print(f'\n\n=== Summary ===')
print(f'Shared levels with drxmap (replaced): {len(shared_drx)}')
print(f'SV-only levels (new areas): {len(sv_only_drx)}')
print(f'SV-only with drxmap: {sum(1 for _, c, _, _ in sv_only_drx if c > 0)}')
print(f'SV-only with keywords: {sum(1 for _, _, _, kw in sv_only_drx if kw)}')

del ae_data, sv_data
