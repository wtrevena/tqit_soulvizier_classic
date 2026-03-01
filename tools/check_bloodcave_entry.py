#!/usr/bin/env python3
"""Check how Blood Cave was originally entered - the Orient/Asia connection."""
import sys
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

sv_data, sv_levels = load_levels(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')

# Random09A is the Orient level that has bloodcave rocks - check its full content
print("=== Random09A.lvl (Orient Underground) - full content ===")
for lv in sv_levels:
    if 'random09a' in lv['fname'].lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        strings = extract_all_strings(blob, 4)
        interesting = [s for s in strings if any(k in s.lower() for k in 
            ['record', 'proxy', 'portal', 'door', 'entrance', 'blood', 'cave',
             'dyngridentrance', '.dbr', 'edge', 'connect', 'grid'])]
        seen = set()
        for s in interesting:
            if s not in seen:
                seen.add(s)
                print(f"  {s}")

# Check BC_initialpathway for how it connects
print("\n=== BC_initialpathway.lvl - connection points ===")
for lv in sv_levels:
    if 'bc_initialpathway' in lv['fname'].lower():
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        strings = extract_all_strings(blob, 4)
        interesting = [s for s in strings if any(k in s.lower() for k in 
            ['record', 'portal', 'door', 'entrance', '.dbr', 'edge', 'connect',
             'grid', 'dyngridentrance'])]
        seen = set()
        for s in interesting:
            if s not in seen:
                seen.add(s)
                print(f"  {s}")

# Check the portal DBRs
print("\n=== Checking portal_olympianarena DBRs in database ===")
db = ArzDatabase.from_arz(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz'))

for rp in db._raw_records:
    if 'portal_olympianarena' in rp.lower() or 'volume_startolympianarena' in rp.lower():
        name_id, compressed = db._raw_records[rp]
        fields = db._decode_fields(compressed)
        print(f"\n  {rp} (type: {db._record_types.get(rp, '?')}):")
        for fn, tf in fields.items():
            vals = [str(v) for v in tf.values[:3]]
            print(f"    {fn} = {', '.join(vals)}")

# Also check where StartingFarmland06D's imhere trigger goes
print("\n=== Checking imhere.dbr (the GardenOfMerchants trigger volume) ===")
for rp in db._raw_records:
    if 'imhere' in rp.lower():
        name_id, compressed = db._raw_records[rp]
        fields = db._decode_fields(compressed)
        print(f"\n  {rp} (type: {db._record_types.get(rp, '?')}):")
        for fn, tf in fields.items():
            vals = [str(v) for v in tf.values[:3]]
            print(f"    {fn} = {', '.join(vals)}")

# Check Duister trigger in the quest more carefully - full Duister section
print("\n=== Checking zzz_theunderlord egg item ===")
for rp in db._raw_records:
    if 'theunderlord' in rp.lower() or 'underlord' in rp.lower():
        name_id, compressed = db._raw_records[rp]
        fields = db._decode_fields(compressed)
        print(f"\n  {rp} (type: {db._record_types.get(rp, '?')}):")
        for fn, tf in fields.items():
            if any(k in fn.lower() for k in ['name', 'class', 'description', 'tag', 'file', 'bitmap', 'loot', 'drop']):
                vals = [str(v) for v in tf.values[:3]]
                print(f"    {fn} = {', '.join(vals)}")

# Check what levels have grid connections to xBloodCave  
print("\n=== Checking how xBloodCave levels connect to each other ===")
bc_levels = []
for lv in sv_levels:
    if 'xbloodcave' in lv['fname'].lower().replace('\\', '/'):
        bc_levels.append(lv)

for lv in bc_levels[:5]:
    blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    strings = extract_all_strings(blob, 4)
    conn_strings = [s for s in strings if 'connect' in s.lower() or 'edge' in s.lower()]
    short_name = lv['fname'].replace('\\', '/').split('/')[-1]
    print(f"  {short_name}: {conn_strings}")

del sv_data
