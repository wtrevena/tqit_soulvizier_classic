#!/usr/bin/env python3
"""Check how Boss Arena, Uber Dungeon, Cold Tombs, and Sparta Crypt connect."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from arz_patcher import ArzDatabase

def load_levels(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec_map = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    return data, levels

def extract_all_strings(blob, min_len=4):
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

print("Loading SV 0.98i...")
sv_data, sv_levels = load_levels(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')

# Part 1: Check if any level in the world references these areas
print("\n" + "="*80)
print("PART 1: Which levels reference bossarena/uberdungeon/coldtombs/spartacrypt?")
print("="*80)

targets = [b'bossarena', b'boss_arena', b'uberdungeon', b'uber_dungeon', 
           b'crypt_floor', b'coldtomb', b'spartacrypt']

for lv in sv_levels:
    fn = lv['fname']
    blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    lower_blob = blob.lower()
    matches = []
    for t in targets:
        if t in lower_blob:
            matches.append(t.decode())
    if matches:
        # Don't report self-references
        fn_lower = fn.lower()
        real_matches = [m for m in matches if m not in fn_lower.replace('\\','/').replace('/','')]
        if real_matches:
            print(f"  {fn} references: {', '.join(real_matches)}")

# Part 2: Check what's inside these levels - full string dump
print("\n" + "="*80)
print("PART 2: Full string content of Boss Arena, Uber Dungeon, Cold Tombs")
print("="*80)

for lv in sv_levels:
    fn_lower = lv['fname'].lower().replace('\\', '/')
    if any(x in fn_lower for x in ['boss_arena', 'bossarena', 'crypt_floor1', 'coldtombs', 'spartacryptlevel2']):
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        strings = extract_all_strings(blob, 6)
        # Filter to interesting strings
        interesting = [s for s in strings if any(k in s.lower() for k in 
            ['record', 'proxy', 'portal', 'door', 'entrance', 'spawn', 'trigger',
             'boss', 'level', 'grid', 'connect', 'npc', 'merchant', 'quest',
             'dyngridentrance', 'fixeditem', '.dbr', '.msh', '.tex'])]
        
        print(f"\n  --- {lv['fname']} ({lv['data_length']:,} bytes) ---")
        print(f"  All strings with paths/records ({len(interesting)}):")
        seen = set()
        for s in interesting:
            if s not in seen:
                seen.add(s)
                print(f"    {s}")

# Part 3: Sparta Crypt Level 1 - find it and check for L2 connections
print("\n" + "="*80)
print("PART 3: Sparta Crypt Level 1 - location and L2 connection")
print("="*80)

for lv in sv_levels:
    fn_lower = lv['fname'].lower()
    if 'spartacrypt' in fn_lower and 'level2' not in fn_lower:
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        strings = extract_all_strings(blob, 4)
        has_l2_ref = any('level2' in s.lower() or 'spartacryptl' in s.lower() for s in strings)
        print(f"  {lv['fname']} ({lv['data_length']:,} bytes)")
        print(f"    References Level 2: {has_l2_ref}")
        # Show connection-related strings
        for s in strings:
            sl = s.lower()
            if any(k in sl for k in ['level', 'door', 'portal', 'entrance', 'connect', 'dyngridentrance']):
                print(f"    -> {s}")

# Also search for any level with "spartacrypt" in any form
print("\n  All levels matching 'sparta' + 'crypt' or 'spartacrypt':")
for lv in sv_levels:
    fn_lower = lv['fname'].lower()
    if 'spartacrypt' in fn_lower or ('sparta' in fn_lower and 'crypt' in fn_lower):
        print(f"    {lv['fname']}")

# Part 4: Check the bossarena quest for how entry works
print("\n" + "="*80)
print("PART 4: Boss Arena quest - entry mechanism")
print("="*80)

sv_quests = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\XPack\Quests.arc'))
for entry in sv_quests.entries:
    if 'bossarena' in entry.name.lower():
        data = sv_quests.decompress(entry)
        strings = extract_all_strings(data, 3)
        print(f"  {entry.name}:")
        for s in strings:
            print(f"    {s}")

# Part 5: Check Garden of Merchants trigger conditions
print("\n" + "="*80)
print("PART 5: Garden of Merchants trigger - entry conditions")
print("="*80)

# Check the StartingFarmland06D level for the trigger
for lv in sv_levels:
    if 'startingfarmland06d' in lv['fname'].lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        strings = extract_all_strings(blob, 4)
        print(f"  {lv['fname']}:")
        for s in strings:
            sl = s.lower()
            if any(k in sl for k in ['garden', 'merchant', 'duister', 'portal', 'trigger', 'drx', 'token', 'imhere']):
                print(f"    -> {s}")

# Check the open_bloodcave_portal quest for the Duister entry conditions
print("\n  Duister/Garden entry conditions from quest:")
for entry in sv_quests.entries:
    if 'bloodcave' in entry.name.lower():
        data = sv_quests.decompress(entry)
        strings = extract_all_strings(data, 3)
        # Find the Duister section
        in_duister = False
        for i, s in enumerate(strings):
            if 'Duister' in s:
                in_duister = True
            if in_duister:
                print(f"    {s}")
            if in_duister and s == 'end_block' and i > 0 and strings[i-1] == 'end_block':
                break

del sv_data
