#!/usr/bin/env python3
"""Deep investigation of all custom areas in SV and SVAERA."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

def extract_strings(blob, min_len=4):
    """Extract all readable ASCII strings from binary blob."""
    strings = []
    current = []
    for b in blob:
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append(''.join(current))
            current = []
    if len(current) >= min_len:
        strings.append(''.join(current))
    return strings

def extract_dbr_strings(blob):
    """Extract DBR record path strings from blob."""
    found = set()
    i = 0
    while i < len(blob):
        idx = blob.find(b'records/', i)
        if idx == -1:
            idx = blob.find(b'xpack/', i)
        if idx == -1:
            break
        end = blob.find(b'\x00', idx)
        if end == -1:
            break
        s = blob[idx:end].decode('ascii', errors='replace')
        found.add(s)
        i = end + 1
    return found

def load_levels(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec_map = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    return data, levels

print("Loading SV 0.98i...")
sv_data, sv_levels = load_levels(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
sv_names = {lv['fname'].replace('\\', '/').lower(): lv for lv in sv_levels}

print("Loading SVAERA...")
ae_data, ae_levels = load_levels(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
ae_names = {lv['fname'].replace('\\', '/').lower(): lv for lv in ae_levels}

# Part 1: Detailed analysis of Boss Arena and Uber Dungeon
print("\n" + "="*80)
print("PART 1: BOSS ARENA & UBER DUNGEON - Detailed Analysis")
print("="*80)

for target in ['boss_arena', 'uberdungeon', 'crypt_floor']:
    for lv in sv_levels:
        if target in lv['fname'].lower():
            blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            dbrs = extract_dbr_strings(blob)
            key = lv['fname'].replace('\\', '/').lower()
            in_ae = key in ae_names
            print(f"\n--- {lv['fname']} ---")
            print(f"  Origin: {'Both SV+SVAERA' if in_ae else 'SV-only'}")
            print(f"  Blob size: {lv['data_length']:,} bytes")
            print(f"  Has drxmap: {'yes' if b'drxmap' in blob else 'no'}")
            print(f"  DBR references ({len(dbrs)}):")
            for s in sorted(dbrs):
                print(f"    {s}")
    # Also check SVAERA
    for lv in ae_levels:
        if target in lv['fname'].lower():
            key = lv['fname'].replace('\\', '/').lower()
            if key not in sv_names:
                blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
                dbrs = extract_dbr_strings(blob)
                print(f"\n--- {lv['fname']} (SVAERA-only) ---")
                print(f"  Blob size: {lv['data_length']:,} bytes")
                print(f"  DBR references ({len(dbrs)}):")
                for s in sorted(dbrs):
                    print(f"    {s}")

# Part 2: All SV-only custom areas with content analysis
print("\n" + "="*80)
print("PART 2: ALL SV-ONLY LEVELS - Content Analysis")
print("="*80)

sv_only = []
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    if key not in ae_names:
        sv_only.append(lv)

# Group by directory
from collections import defaultdict
groups = defaultdict(list)
for lv in sv_only:
    parts = lv['fname'].replace('\\', '/').split('/')
    if len(parts) >= 3:
        group = '/'.join(parts[:3])
    else:
        group = parts[0]
    groups[group].append(lv)

for group_name in sorted(groups.keys()):
    lvs = groups[group_name]
    print(f"\n--- {group_name} ({len(lvs)} levels) ---")
    for lv in lvs:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        has_drx = b'drxmap' in blob
        has_portal = b'portal' in blob.lower()
        has_proxy = b'proxy' in blob.lower()
        has_npc = b'npc' in blob.lower()
        has_merchant = b'merchant' in blob.lower()
        has_boss = b'boss' in blob.lower()
        tags = []
        if has_drx: tags.append('drxmap')
        if has_portal: tags.append('portal')
        if has_proxy: tags.append('proxy')
        if has_npc: tags.append('npc')
        if has_merchant: tags.append('merchant')
        if has_boss: tags.append('boss')
        short_name = lv['fname'].replace('\\', '/').split('/')[-1]
        print(f"  {short_name} ({lv['data_length']:,}b) [{', '.join(tags) if tags else 'empty/minimal'}]")

# Part 3: All SVAERA-only levels (not in SV)
print("\n" + "="*80)
print("PART 3: ALL SVAERA-ONLY LEVELS (not in SV 0.98i)")
print("="*80)

ae_only = []
for lv in ae_levels:
    key = lv['fname'].replace('\\', '/').lower()
    if key not in sv_names:
        ae_only.append(lv)

ae_groups = defaultdict(list)
for lv in ae_only:
    parts = lv['fname'].replace('\\', '/').split('/')
    if len(parts) >= 3:
        group = '/'.join(parts[:3])
    else:
        group = parts[0]
    ae_groups[group].append(lv)

for group_name in sorted(ae_groups.keys()):
    lvs = ae_groups[group_name]
    print(f"\n--- {group_name} ({len(lvs)} levels) ---")
    for lv in lvs:
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        has_drx = b'drxmap' in blob
        has_portal = b'portal' in blob.lower()
        has_proxy = b'proxy' in blob.lower()
        has_npc = b'npc' in blob.lower()
        has_merchant = b'merchant' in blob.lower()
        has_boss = b'boss' in blob.lower()
        tags = []
        if has_drx: tags.append('drxmap')
        if has_portal: tags.append('portal')
        if has_proxy: tags.append('proxy')
        if has_npc: tags.append('npc')
        if has_merchant: tags.append('merchant')
        if has_boss: tags.append('boss')
        short_name = lv['fname'].replace('\\', '/').split('/')[-1]
        print(f"  {short_name} ({lv['data_length']:,}b) [{', '.join(tags) if tags else 'empty/minimal'}]")

del sv_data, ae_data
