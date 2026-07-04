"""Find PathMesh and PathMeshRecast class methods in Engine.dll."""
import re

ENGINE = r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll'
data = open(ENGINE, 'rb').read()

IMAGE_BASE = 0x10000000
TEXT_RVA = 0x1000
TEXT_RAW = 0x400

def fo_to_va(fo):
    return fo - TEXT_RAW + TEXT_RVA + IMAGE_BASE

# Find all mangled symbol names containing specific patterns
patterns = [
    (rb'PathMesh@GAME', 'PathMesh'),
    (rb'PathMeshRecast@GAME', 'PathMeshRecast'),
    (rb'ImpassableData@GAME', 'ImpassableData'),
]

for pat, label in patterns:
    print(f'\n=== {label} ===')
    results = []
    for m in re.finditer(pat, data):
        off = m.start()
        # Walk back to find start of string (null byte)
        start = off
        for i in range(200):
            if start <= 0:
                break
            if data[start - 1] == 0:
                break
            start -= 1
        end = data.index(b'\x00', off)
        name = data[start:end].decode('ascii', errors='replace')
        if name not in [n for _, n in results]:
            results.append((start, name))

    # Filter for the specific class
    for s, n in sorted(results):
        if label == 'PathMesh' and ('Recast' in n or 'Compiler' in n or 'Error' in n):
            continue
        # Check if this is in .rdata (likely export/symbol table)
        rdata_start = 0x2AAC00
        rdata_end = rdata_start + 0xC1C00
        loc = 'rdata' if rdata_start <= s < rdata_end else 'other'
        print(f'  [{loc}] 0x{s:06X}: {n}')

# Also find key strings
print('\n=== Key Strings ===')
for pat in [b'pathengine.dll', b'PathEngine loaded', b'SetRecastMode', b'recast_mode']:
    for m in re.finditer(pat, data):
        off = m.start()
        start = off
        for i in range(100):
            if start <= 0 or data[start-1] == 0:
                break
            start -= 1
        end = data.index(b'\x00', off)
        txt = data[start:end].decode('ascii', errors='replace')
        va = fo_to_va(off) if off < 0x2AAC00 else 0  # only .text
        print(f'  0x{off:06X}: {txt}')

# Find "Couldn't load PathEngine.dll" xrefs to find PathEngine loading code
print('\n=== PathEngine Loading Code ===')
load_str_off = data.find(b"pathengine.dll\x00")
if load_str_off >= 0:
    load_str_rva = load_str_off - 0x2AAC00 + 0x2AC000  # .rdata section
    load_str_va = load_str_rva + IMAGE_BASE
    print(f'  "pathengine.dll" at file 0x{load_str_off:06X}, VA 0x{load_str_va:08X}')
    # Search for push/lea of this VA in .text
    va_bytes = load_str_va.to_bytes(4, 'little')
    for m in re.finditer(re.escape(va_bytes), data[:0x2AAC00]):
        ref_off = m.start()
        ref_va = fo_to_va(ref_off)
        # Check preceding byte for push/lea
        pre = data[ref_off - 1] if ref_off > 0 else 0
        print(f'  Referenced at file 0x{ref_off:06X} VA 0x{ref_va:08X} (pre=0x{pre:02X})')
