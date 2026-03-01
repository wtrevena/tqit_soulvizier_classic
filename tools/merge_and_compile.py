#!/usr/bin/env python3
"""
Create merged source directory and WRL for MapCompiler.
Uses proper editor-format .lvl files from proper_decompile.py.
"""
import sys, struct, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    SEC_LEVELS, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS, SEC_DATA2)

svaera_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
svaera_decomp = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_svaera')
sv_decomp = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_sv')
merged_dir = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_source')
output_wrl = merged_dir / 'world01.wrl'
output_sd = merged_dir / 'world01.sd'

# Load maps for metadata
print('Loading SVAERA...')
ae_arc = ArcArchive.from_file(svaera_arc)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
ae_quests = parse_quests(ae_data, ae_sec[SEC_QUESTS])

print('Loading SV...')
sv_arc_obj = ArcArchive.from_file(sv_arc)
sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
sv_sec = {s['type']: s for s in parse_sections(sv_data)}
sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])
sv_quests = parse_quests(sv_data, sv_sec[SEC_QUESTS])

# Build name lookups
ae_by_name = {}
for i, lv in enumerate(ae_levels):
    ae_by_name[lv['fname'].replace('\\', '/').lower()] = i

sv_by_name = {}
for i, lv in enumerate(sv_levels):
    sv_by_name[lv['fname'].replace('\\', '/').lower()] = i

# Identify SV-only and shared-with-drxmap levels
sv_only = []
sv_shared_drx = []
for lv in sv_levels:
    key = lv['fname'].replace('\\', '/').lower()
    chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    if key not in ae_by_name:
        sv_only.append(lv)
    elif b'drxmap' in chunk:
        sv_shared_drx.append(lv)

print(f'\n  SVAERA: {len(ae_levels)} levels')
print(f'  SV-only: {len(sv_only)} new levels')
print(f'  Shared with drxmap: {len(sv_shared_drx)} levels to replace')

# Step 1: Create merged source directory
print(f'\nCreating merged source directory: {merged_dir}')
if merged_dir.exists():
    shutil.rmtree(merged_dir)
merged_dir.mkdir(parents=True)

# Copy all SVAERA decompiled levels
print('  Copying SVAERA levels...')
copied = 0
for lv in ae_levels:
    fname = lv['fname'].replace('/', '\\')
    for ext in ['.lvl', '.rlv', '.LVL', '.RLV']:
        src_base = fname
        if ext in ['.rlv', '.RLV']:
            src_base = fname[:-4] + ext[-4:]
        else:
            src_base = fname
        src = svaera_decomp / src_base
        if src.exists():
            dst = merged_dir / src_base
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
print(f'  Copied {copied} files from SVAERA')

# Overlay SV-only levels and shared levels with drxmap
print('  Overlaying SV levels...')
overlaid = 0
for lv in sv_only + sv_shared_drx:
    fname = lv['fname'].replace('/', '\\')
    for ext_pair in [('', ''), ('.rlv', '.rlv')]:
        if ext_pair[1]:
            src_base = fname[:-4] + ext_pair[1]
        else:
            src_base = fname
        src = sv_decomp / src_base
        if src.exists():
            dst = merged_dir / src_base
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            overlaid += 1
print(f'  Overlaid {overlaid} files from SV')

# Step 2: Generate merged WRL file
print(f'\nGenerating merged WRL: {output_wrl}')

# Build merged level list (SVAERA order + SV-only appended)
merged_levels = list(ae_levels)
for lv in sv_only:
    merged_levels.append(lv)

# Merge quests
ae_quest_set = set(q.lower() for q in ae_quests)
new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]
merged_quests = ae_quests + new_quests

# Get raw section data for GROUPS, SD
groups_raw = ae_data[ae_sec[SEC_GROUPS]['data_offset']:ae_sec[SEC_GROUPS]['data_offset'] + ae_sec[SEC_GROUPS]['size']]
sd_raw = ae_data[ae_sec[SEC_SD]['data_offset']:ae_sec[SEC_SD]['data_offset'] + ae_sec[SEC_SD]['size']]

# Write WRL file
wrl = bytearray()
wrl += struct.pack('<I', 0x074C5257)  # WRL magic

# LEVELS section (type 0x13 in WRL)
levels_payload = bytearray()
levels_payload += struct.pack('<I', len(merged_levels))
for lv in merged_levels:
    # fname
    fname_bytes = lv['fname_raw']
    levels_payload += struct.pack('<I', len(fname_bytes))
    levels_payload += fname_bytes
    # ints_raw as 13 values (first 6 cast to float, rest as-is)
    raw = lv['ints_raw']
    for j in range(6):
        int_val = struct.unpack_from('<I', raw, j * 4)[0]
        levels_payload += struct.pack('<f', float(int_val))
    levels_payload += raw[24:52]  # remaining 7 ints as-is
    # dbr
    dbr_bytes = lv['dbr_raw']
    levels_payload += struct.pack('<I', len(dbr_bytes))
    levels_payload += dbr_bytes

wrl += struct.pack('<II', 0x13, len(levels_payload))
wrl += levels_payload

# QUESTS section (type 0x1B)
quests_payload = bytearray()
quests_payload += struct.pack('<I', len(merged_quests))
for q in merged_quests:
    quests_payload += struct.pack('<I', len(q))
    quests_payload += q
wrl += struct.pack('<II', 0x1B, len(quests_payload))
wrl += quests_payload

# GROUPS section (type 0x11)
wrl += struct.pack('<II', 0x11, len(groups_raw))
wrl += groups_raw

# BITMAPS section (type 0x15) - write empty/minimal
# MapCompiler will regenerate bitmaps
bmp_payload = bytearray()
for lv in merged_levels:
    bmp_payload += struct.pack('<4I', 0, 0, 0, 0)
wrl += struct.pack('<II', 0x15, len(bmp_payload))
wrl += bmp_payload

output_wrl.write_bytes(bytes(wrl))
print(f'  WRL: {len(wrl)} bytes, {len(merged_levels)} levels')

# Write SD file
output_sd.write_bytes(sd_raw)
print(f'  SD: {len(sd_raw)} bytes')

# Verify .lvl files exist
missing = 0
for lv in merged_levels:
    fname = lv['fname'].replace('/', '\\')
    lvl_path = merged_dir / fname
    if not lvl_path.exists():
        missing += 1
        if missing <= 3:
            print(f'  MISSING: {fname}')
print(f'\n  Missing .lvl files: {missing}')

print(f'\nMerged source ready at: {merged_dir}')
print(f'  Total levels: {len(merged_levels)}')
print(f'  Total quests: {len(merged_quests)}')

del ae_data, sv_data

# Step 3: Run MapCompiler
mc_exe = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\MapCompiler.exe')
output_map = merged_dir / 'world01.map'

print(f'\n=== Running MapCompiler ===')
print(f'  WRL: {output_wrl}')
print(f'  Source: {merged_dir}\\')
print(f'  Output: {output_map}')

import subprocess
result = subprocess.run(
    [str(mc_exe), str(output_wrl), str(merged_dir) + '\\', str(output_map)],
    capture_output=True, text=True, timeout=600
)
print(f'\n  Exit code: {result.returncode}')
if result.stdout:
    lines = result.stdout.strip().split('\n')
    # Show first 30 and last 30 lines
    if len(lines) > 60:
        for line in lines[:30]:
            print(f'  {line}')
        print(f'  ... ({len(lines) - 60} more lines) ...')
        for line in lines[-30:]:
            print(f'  {line}')
    else:
        for line in lines:
            print(f'  {line}')
if result.stderr:
    print(f'  STDERR: {result.stderr[:500]}')

if output_map.exists():
    size = output_map.stat().st_size
    print(f'\n  Output: {size} bytes ({size/(1024**2):.1f} MB)')
    print(f'  Under 2GB: {size < 2147483647}')
