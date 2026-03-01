#!/usr/bin/env python3
"""
Analyze the LVL blob format to understand object placement structure.
Compare SVAERA and SV versions of the same level to find where drxmap objects are stored.
"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])

print('Loading SV...')
sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
sv_sec = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])

ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i

# Focus on DelphiLowlands02 (pit sprites) as a test case
target = 'delphilowlands02'
sv_lv = None
ae_lv = None
for lv in sv_levels:
    if target in lv['fname'].lower():
        key = lv['fname'].replace('\\', '/').lower()
        if key in ae_by_name:
            sv_lv = lv
            ae_lv = ae_levels[ae_by_name[key]]
            break

print(f'\nTarget: {sv_lv["fname"]}')
ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]
print(f'  SVAERA: {len(ae_blob)} bytes (LVL v0x{ae_blob[3]:02x})')
print(f'  SV:     {len(sv_blob)} bytes (LVL v0x{sv_blob[3]:02x})')

# Find all drxmap references in SV blob and their positions
print(f'\n=== drxmap references in SV blob ===')
pos = 0
drx_positions = []
while True:
    idx = sv_blob.find(b'drxmap', pos)
    if idx == -1:
        break
    # Find the full string (look for string length prefix)
    # DBR paths are typically: uint32(length) + ascii_string
    # Search backwards from drxmap for the start of the string
    str_start = idx
    while str_start > 0 and sv_blob[str_start-1] >= 32 and sv_blob[str_start-1] < 127:
        str_start -= 1
    str_end = idx + 6
    while str_end < len(sv_blob) and sv_blob[str_end] >= 32 and sv_blob[str_end] < 127:
        str_end += 1
    dbr_path = sv_blob[str_start:str_end].decode('ascii', errors='replace')
    
    # Check for length prefix
    if str_start >= 4:
        prefix_len = struct.unpack_from('<I', sv_blob, str_start - 4)[0]
        if prefix_len == str_end - str_start:
            str_start -= 4  # include length prefix
    
    drx_positions.append((str_start, str_end, dbr_path))
    print(f'  offset {idx}: {dbr_path}')
    pos = idx + 6

# Analyze the area around each drxmap reference to understand the object format
print(f'\n=== Object structure around first drxmap ref ===')
if drx_positions:
    start, end, path = drx_positions[0]
    # Show surrounding bytes
    ctx_start = max(0, start - 64)
    ctx_end = min(len(sv_blob), end + 64)
    print(f'  Context ({ctx_start} to {ctx_end}):')
    for i in range(ctx_start, ctx_end, 16):
        chunk = sv_blob[i:min(i+16, ctx_end)]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f'    {i:8d}: {hex_str:<48s} {ascii_str}')

# Look for object count differences
# Parse LVL header
def parse_lvl_header(blob, label):
    print(f'\n=== {label} LVL Header ===')
    print(f'  Magic: {blob[:3]}  Version: 0x{blob[3]:02x}')
    # After LVL\x0e or LVL\x11: version(1) then data
    idx = 4
    for i in range(min(20, (len(blob) - 4) // 4)):
        val = struct.unpack_from('<I', blob, idx)[0]
        fval = struct.unpack_from('<f', blob, idx)[0]
        signed = struct.unpack_from('<i', blob, idx)[0]
        print(f'  +{idx:5d}: uint32={val:10d} (0x{val:08x})  float={fval:12.4f}  int32={signed}')
        idx += 4

parse_lvl_header(ae_blob, 'SVAERA DelphiLowlands02')
parse_lvl_header(sv_blob, 'SV DelphiLowlands02')

# Count all string references in both blobs
def count_dbr_refs(blob, label):
    count = 0
    pos = 0
    while True:
        idx = blob.find(b'.dbr', pos)
        if idx == -1:
            break
        count += 1
        pos = idx + 4
    return count

ae_dbr_count = count_dbr_refs(ae_blob, 'SVAERA')
sv_dbr_count = count_dbr_refs(sv_blob, 'SV')
print(f'\n=== DBR reference counts ===')
print(f'  SVAERA: {ae_dbr_count} .dbr references')
print(f'  SV:     {sv_dbr_count} .dbr references')
print(f'  Diff:   {sv_dbr_count - ae_dbr_count} (SV has more)')

# Find DBR refs in SV that don't exist in SVAERA
sv_dbr_set = set()
pos = 0
while True:
    idx = sv_blob.find(b'.dbr', pos)
    if idx == -1:
        break
    # Find string start
    str_start = idx
    while str_start > 0 and sv_blob[str_start-1] >= 32 and sv_blob[str_start-1] < 127:
        str_start -= 1
    dbr = sv_blob[str_start:idx+4].decode('ascii', errors='replace')
    sv_dbr_set.add(dbr)
    pos = idx + 4

ae_dbr_set = set()
pos = 0
while True:
    idx = ae_blob.find(b'.dbr', pos)
    if idx == -1:
        break
    str_start = idx
    while str_start > 0 and ae_blob[str_start-1] >= 32 and ae_blob[str_start-1] < 127:
        str_start -= 1
    dbr = ae_blob[str_start:idx+4].decode('ascii', errors='replace')
    ae_dbr_set.add(dbr)
    pos = idx + 4

sv_only_dbrs = sv_dbr_set - ae_dbr_set
print(f'\n=== DBR references only in SV (custom objects) ===')
for dbr in sorted(sv_only_dbrs):
    print(f'  {dbr}')

del ae_data, sv_data
