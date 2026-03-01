#!/usr/bin/env python3
"""Find unwired/WIP content - quests, portals, DBRs that may be drafted but not connected."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

def load_levels(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec_map = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    return data, levels

print("Loading SV 0.98i...")
sv_data, sv_levels = load_levels(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
sv_names = {lv['fname'].replace('\\', '/').lower(): lv for lv in sv_levels}

ae_data, ae_levels = load_levels(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
ae_names = {lv['fname'].replace('\\', '/').lower(): lv for lv in ae_levels}

# Check SV quests
print("\n" + "="*80)
print("SV QUEST FILES - Analyzing for area references")
print("="*80)

sv_quests = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\XPack\Quests.arc'))
for entry in sv_quests.entries:
    if entry.name.endswith('.qst'):
        data = sv_quests.decompress(entry)
        # Extract strings
        strings = []
        current = []
        for b in data:
            if 32 <= b < 127:
                current.append(chr(b))
            else:
                if len(current) >= 4:
                    strings.append(''.join(current))
                current = []
        
        has_bloodcave = any('bloodcave' in s.lower() for s in strings)
        has_boss_arena = any('bossarena' in s.lower() or 'boss_arena' in s.lower() for s in strings)
        has_uber = any('uberdungeon' in s.lower() or 'uber_dungeon' in s.lower() or 'uber' in s.lower() for s in strings)
        has_secret = any('secret_place' in s.lower() or 'secretplace' in s.lower() for s in strings)
        has_garden = any('garden' in s.lower() for s in strings)
        has_drx = any('drx' in s.lower() for s in strings)
        
        tags = []
        if has_bloodcave: tags.append('bloodcave')
        if has_boss_arena: tags.append('bossarena')
        if has_uber: tags.append('uber')
        if has_secret: tags.append('secret_place')
        if has_garden: tags.append('garden')
        if has_drx: tags.append('drx')
        
        if tags:
            # Get quest name
            quest_name = ''
            for i, s in enumerate(strings):
                if s == 'title' and i + 1 < len(strings):
                    quest_name = strings[i + 1]
                    break
                if s == 'name' and i + 1 < len(strings):
                    quest_name = strings[i + 1]
                    break
            
            print(f"\n  {entry.name} [{', '.join(tags)}]")
            if quest_name:
                print(f"    Title/Name: {quest_name}")
            
            # Show relevant DBR references
            for s in strings:
                sl = s.lower()
                if ('drx' in sl or 'bloodcave' in sl or 'bossarena' in sl or 
                    'uberdungeon' in sl or 'secret' in sl or 'garden' in sl) and 'records/' in sl:
                    print(f"    -> {s}")

# Check for SVAERA quests
print("\n" + "="*80)
print("SVAERA QUEST FILES - Looking for custom quest files")
print("="*80)

ae_base = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources')
for arc_path in ae_base.rglob('*.arc'):
    if 'quest' in arc_path.name.lower():
        print(f"\n  Archive: {arc_path.relative_to(ae_base)}")
        arc = ArcArchive.from_file(arc_path)
        for entry in arc.entries:
            if entry.name.endswith('.qst'):
                print(f"    {entry.name}")

# Check boss_arena specifically for what quest triggers it
print("\n" + "="*80)
print("BOSS ARENA QUEST WIRING")
print("="*80)

for entry in sv_quests.entries:
    if 'bossarena' in entry.name.lower() or 'boss_arena' in entry.name.lower() or 'boss arena' in entry.name.lower():
        data = sv_quests.decompress(entry)
        strings = []
        current = []
        for b in data:
            if 32 <= b < 127:
                current.append(chr(b))
            else:
                if len(current) >= 3:
                    strings.append(''.join(current))
                current = []
        print(f"\n  {entry.name}:")
        for s in strings:
            print(f"    {s}")

# Check urder quest (the secret dungeon quest)
print("\n" + "="*80)
print("URDER QUEST (secret dungeon)")
print("="*80)

for entry in sv_quests.entries:
    if 'urder' in entry.name.lower():
        data = sv_quests.decompress(entry)
        strings = []
        current = []
        for b in data:
            if 32 <= b < 127:
                current.append(chr(b))
            else:
                if len(current) >= 3:
                    strings.append(''.join(current))
                current = []
        print(f"\n  {entry.name}:")
        for s in strings:
            print(f"    {s}")

# Check what "Secret_Place" levels are about
print("\n" + "="*80)
print("SECRET PLACE - DBR content in each level")
print("="*80)

for lv in sv_levels:
    if 'secret_place' in lv['fname'].lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        found = set()
        i = 0
        while i < len(blob):
            for prefix in [b'records/', b'xpack/']:
                idx = blob.find(prefix, i)
                if idx != -1:
                    break
            else:
                break
            end = blob.find(b'\x00', idx)
            if end == -1:
                break
            s = blob[idx:end].decode('ascii', errors='replace')
            found.add(s)
            i = end + 1
        
        short_name = lv['fname'].replace('\\', '/').split('/')[-1]
        print(f"\n  {short_name} ({len(found)} DBRs):")
        # Show interesting ones
        for s in sorted(found):
            sl = s.lower()
            if any(k in sl for k in ['drx', 'portal', 'door', 'boss', 'npc', 'merchant', 'proxy', 'quest', 'secret', 'trigger', 'spawn']):
                print(f"    {s}")

del sv_data, ae_data
