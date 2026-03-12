"""Extract the body of a real TQAE 0x0b (REC\x02) section for analysis.

Extracts from SVAERA's RuinedCity02 level. Saves:
  - rec02_full.bin      (complete 0x0b section)
  - rec02_body.bin      (body only, after variable header)
  - rec02_body_info.txt (hex dump + analysis)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections

REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
OUT_DIR = REPO / 'local' / 'pathengine_analysis'
OUT_DIR.mkdir(parents=True, exist_ok=True)

svaera_arc_path = REPO / 'reference_mods' / 'SVAERA_customquest' / 'Resources' / 'Levels.arc'

print('Loading SVAERA archive...')
ae_arc = ArcArchive.from_file(svaera_arc_path)
ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
ae_sec = {s['type']: s for s in parse_sections(ae_data)}
ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
print(f'  {len(ae_levels)} levels')

# Find RuinedCity02 (index 30)
ae_lv = ae_levels[30]
print(f'  Level: {ae_lv["fname"]}')

blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
secs, magic = parse_blob_sections(blob)

print(f'  Blob: {len(blob)} bytes, version 0x{blob[3]:02x}')
sec_strs = [f"0x{s['type']:02x}({len(s['data'])})" for s in secs]
print(f'  Sections: {sec_strs}')

# Find 0x0b section
sec_0b = None
for s in secs:
    if s['type'] == 0x0b:
        sec_0b = s
        break

if not sec_0b:
    print('ERROR: No 0x0b section found!')
    sys.exit(1)

data = sec_0b['data']
print(f'\n0x0b section: {len(data)} bytes')

# Save full section
(OUT_DIR / 'rec02_full.bin').write_bytes(data)

# Parse header
off = 0
magic_bytes = data[off:off+4]; off += 4
field1 = struct.unpack_from('<I', data, off)[0]; off += 4
payload_size = struct.unpack_from('<I', data, off)[0]; off += 4
diff_count = struct.unpack_from('<I', data, off)[0]; off += 4

print(f'  Magic: {magic_bytes}')
print(f'  Field1: {field1}')
print(f'  Payload size: {payload_size}')
print(f'  Diff count: {diff_count}')

guid_start = 16
for i in range(diff_count):
    g = data[guid_start + i*16 : guid_start + (i+1)*16]
    print(f'  GUID[{i}]: {g.hex()}')

center_start = guid_start + diff_count * 16
cx, cy, cz = struct.unpack_from('<iii', data, center_start)
print(f'  Center: ({cx}, {cy}, {cz})')

dims_start = center_start + 12
dx, dy, dz = struct.unpack_from('<III', data, dims_start)
print(f'  Dims: ({dx}, {dy}, {dz})')

body_start = dims_start + 12
body = data[body_start:]
print(f'  Header size: {body_start} bytes')
print(f'  Body size: {len(body)} bytes')

# Save body
(OUT_DIR / 'rec02_body.bin').write_bytes(body)

# Analysis
with open(OUT_DIR / 'rec02_body_info.txt', 'w') as f:
    f.write(f'Source: SVAERA RuinedCity02 0x0b section body\n')
    f.write(f'Body size: {len(body)} bytes\n')
    f.write(f'Header size: {body_start} bytes\n\n')

    # Full hex dump (first 512 bytes)
    f.write('First 512 bytes:\n')
    for row in range(min(32, (len(body) + 15) // 16)):
        chunk = body[row*16:(row+1)*16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        f.write(f'  {row*16:04x}: {hex_str:<48s} {ascii_str}\n')
    f.write('\n')

    # uint32 + float interpretation
    f.write('As uint32/float sequence (first 128 values):\n')
    for i in range(min(128, len(body) // 4)):
        val_u = struct.unpack_from('<I', body, i*4)[0]
        val_i = struct.unpack_from('<i', body, i*4)[0]
        val_f = struct.unpack_from('<f', body, i*4)[0]
        raw = body[i*4:(i+1)*4]
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw)
        f.write(f'  [{i:3d}] off={i*4:5d}: u={val_u:10d} i={val_i:10d} f={val_f:15.6f}  {ascii_str}\n')
    f.write('\n')

    # Search for magic strings
    f.write('Magic string search:\n')
    for needle_name, needle in [
        ('mesh\\0', b'mesh\x00'), ('tok', b'tok'), ('xml', b'xml'),
        ('RLTD', b'RLTD'), ('REC', b'REC'), ('PTH', b'PTH'),
        ('NOD', b'NOD'), ('EDG', b'EDG'), ('VER', b'VER'),
        ('TRI', b'TRI'), ('GRI', b'GRI'), ('NAV', b'NAV'),
        ('CEL', b'CEL'), ('MSH', b'MSH'),
    ]:
        hits = []
        pos = 0
        while True:
            idx = body.find(needle, pos)
            if idx < 0:
                break
            hits.append(idx)
            pos = idx + 1
        if hits:
            f.write(f'  "{needle_name}": {len(hits)} hits at {hits[:20]}\n')

    # Look for 4-char ASCII tags (potential sub-record markers)
    f.write('\n4-char ASCII tags scan:\n')
    tags = {}
    for i in range(len(body) - 3):
        chunk = body[i:i+4]
        if all(32 <= b < 127 for b in chunk):
            tag = chunk.decode('ascii')
            if tag not in tags:
                tags[tag] = []
            if len(tags[tag]) < 5:
                tags[tag].append(i)
    for tag, offsets in sorted(tags.items()):
        if len(offsets) >= 1:
            f.write(f'  "{tag}" at offsets {offsets}\n')

# Print key findings
print(f'\nKey body analysis:')
print(f'  First 16 bytes: {body[:16].hex()}')

# Search for key markers
for name, needle in [('mesh\\0', b'mesh\x00'), ('tok', b'tok'), ('RLTD', b'RLTD')]:
    idx = body.find(needle)
    if idx >= 0:
        print(f'  "{name}" found at body offset {idx}')
    else:
        print(f'  "{name}" NOT found')

# Check if body starts with "tok" format header
if body[:4] == b'mesh':
    print('  Body starts with "mesh" — likely PathEngine tok format!')
elif body[:3] == b'tok':
    print('  Body starts with "tok"')
else:
    print(f'  Body starts with: {body[:8].hex()} (not PathEngine tok format)')

# Also extract a SECOND level's 0x0b for comparison
ae_lv2 = ae_levels[100]  # Different level
blob2 = ae_data[ae_lv2['data_offset']:ae_lv2['data_offset'] + ae_lv2['data_length']]
secs2, _ = parse_blob_sections(blob2)
sec_0b_2 = None
for s in secs2:
    if s['type'] == 0x0b:
        sec_0b_2 = s
        break

if sec_0b_2:
    data2 = sec_0b_2['data']
    dc2 = struct.unpack_from('<I', data2, 12)[0]
    bs2 = 16 + dc2 * 16 + 24
    body2 = data2[bs2:]
    (OUT_DIR / 'rec02_body2.bin').write_bytes(body2)
    print(f'\nSecond level ({ae_lv2["fname"]}):')
    print(f'  0x0b: {len(data2)} bytes, body: {len(body2)} bytes')
    print(f'  Body starts: {body2[:16].hex()}')

    # Compare first few uint32s between the two bodies
    print(f'\nBody structure comparison (first 16 uint32s):')
    print(f'  {"Off":>5s}  {"Level1":>12s}  {"Level2":>12s}  {"Match?":>8s}')
    for i in range(min(16, min(len(body), len(body2)) // 4)):
        v1 = struct.unpack_from('<I', body, i*4)[0]
        v2 = struct.unpack_from('<I', body2, i*4)[0]
        match = "YES" if v1 == v2 else "no"
        print(f'  {i*4:5d}  {v1:12d}  {v2:12d}  {match:>8s}')

print(f'\nFiles written to: {OUT_DIR}')
print('Done.')
