#!/usr/bin/env python3
"""Hex dump and parse GROUPS section."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, SEC_GROUPS

arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc'))
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sections = parse_sections(data)
sec_map = {s['type']: s for s in sections}
gs = sec_map[SEC_GROUPS]
gbuf = data[gs['data_offset']:gs['data_offset'] + gs['size']]

print('GROUPS first 300 bytes:')
for i in range(0, min(300, len(gbuf)), 16):
    hex_str = ' '.join(f'{b:02x}' for b in gbuf[i:i+16])
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in gbuf[i:i+16])
    print(f'  {i:6d}: {hex_str:<48s} {ascii_str}')

# Parse: first two uint32
idx = 0
val0 = struct.unpack_from('<I', gbuf, idx)[0]; idx += 4
val1 = struct.unpack_from('<I', gbuf, idx)[0]; idx += 4
print(f'\nval0={val0}, val1={val1}')

# Try parsing entries with format: type(4), name_len(4), name, count(4), indices(count*4)
for i in range(min(20, val1)):
    if idx >= len(gbuf):
        break
    etype = struct.unpack_from('<I', gbuf, idx)[0]; idx += 4
    nlen = struct.unpack_from('<I', gbuf, idx)[0]; idx += 4

    if nlen > 500 or nlen == 0:
        print(f'Entry {i}: type={etype} bad nlen={nlen}, stopping')
        break

    name = gbuf[idx:idx+nlen].decode('ascii', errors='replace')
    idx += nlen

    if idx + 4 > len(gbuf):
        print(f'Entry {i}: type={etype} name="{name}" (EOF)')
        break

    count = struct.unpack_from('<I', gbuf, idx)[0]; idx += 4

    if count > 10000:
        print(f'Entry {i}: type={etype} name="{name}" bad count={count}, stopping')
        break

    indices = []
    for j in range(count):
        if idx + 4 > len(gbuf):
            break
        v = struct.unpack_from('<I', gbuf, idx)[0]; idx += 4
        indices.append(v)

    summary = str(indices[:5])
    if len(indices) > 5:
        summary += f'... ({len(indices)} total)'
    print(f'Entry {i}: type={etype} name="{name}" count={count} values={summary}')

print(f'\nBytes consumed: {idx}/{len(gbuf)}')
del data
