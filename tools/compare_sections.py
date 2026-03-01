#!/usr/bin/env python3
"""Compare section structures between SVAERA and SV maps."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS, SEC_SD

names = {1:'LEVELS', 2:'DATA', 0x10:'UNK', 0x11:'GROUPS', 0x18:'SD',
         0x19:'BITMAPS', 0x1A:'DATA2', 0x1B:'QUESTS'}

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
    print(f'  Levels: {len(levels)}')

    for s in sections:
        n = names.get(s['type'], f'0x{s["type"]:02X}')
        ratio = s['size'] / len(levels) if len(levels) > 0 else 0
        print(f'  {n:8s}: size={s["size"]:>12d} ({s["size"]/(1024*1024):>7.1f} MB)  per_level={ratio:.1f}')

    # Check GROUPS structure
    groups = sec_map.get(SEC_GROUPS)
    if groups:
        gbuf = data[groups['data_offset']:groups['data_offset'] + min(groups['size'], 100)]
        first_vals = struct.unpack_from(f'<{min(25, len(gbuf)//4)}I', gbuf, 0)
        print(f'  GROUPS first 10 uint32s: {list(first_vals[:10])}')

    # Check SD structure
    sd = sec_map.get(SEC_SD)
    if sd:
        sbuf = data[sd['data_offset']:sd['data_offset'] + min(sd['size'], 100)]
        first_vals = struct.unpack_from(f'<{min(25, len(sbuf)//4)}I', sbuf, 0)
        print(f'  SD first 10 uint32s: {list(first_vals[:10])}')

    # Check UNK section
    unk = [s for s in sections if s['type'] == 0x10]
    if unk:
        ubuf = data[unk[0]['data_offset']:unk[0]['data_offset'] + unk[0]['size']]
        first_vals = struct.unpack_from(f'<{min(25, len(ubuf)//4)}I', ubuf, 0)
        print(f'  UNK first vals: {list(first_vals[:10])}')

    del data
