"""Read-only build-speed micro-probes. Memory-conservative (build40 heavy build
may be running concurrently). No full builds. Uses seek-based reads + small samples."""
import struct, zlib, time, sys, gc
from pathlib import Path

REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
ARZ = REPO / 'local' / 'DEV_arz_deployed_prev.arz'
ARC = REPO / 'local' / 'Levels_merged.arc'

def read_lp_string(data, offset):
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    s = data[offset:offset+length].decode('latin-1')
    return s, offset + length

def write_lp_string(s):
    e = s.encode('latin-1')
    return struct.pack('<i', len(e)) + e

# ---------- PROBE 1: arz string-table serializer O(n^2) ----------
print("=== PROBE 1: write_arz string-table serialization ===")
raw = ARZ.read_bytes()
magic, version, rt_offset, rt_size, rt_count, st_offset, st_size = struct.unpack_from('<HHiiiii', raw, 0)
st_data_in = raw[st_offset:st_offset+st_size]
st_pos = 0
st_num = struct.unpack_from('<i', st_data_in, st_pos)[0]; st_pos += 4
strings = []
for i in range(st_num):
    s, st_pos = read_lp_string(st_data_in, st_pos)
    strings.append(s)
del raw, st_data_in
gc.collect()
print(f"  strings={len(strings)}  (real string table from {ARZ.name})")

# OLD path (arz_patcher.py:314-316): immutable bytes += in a loop -> O(n^2)
t = time.perf_counter()
st_old = struct.pack('<i', len(strings))
for s in strings:
    st_old += write_lp_string(s)
old_t = time.perf_counter() - t
print(f"  OLD (bytes +=):        {old_t:8.3f} s   ({len(st_old)/1024/1024:.1f} MB table)")

# NEW path: bytearray accumulator
t = time.perf_counter()
st_new = bytearray(struct.pack('<i', len(strings)))
for s in strings:
    st_new += write_lp_string(s)
st_new = bytes(st_new)
new_t = time.perf_counter() - t
print(f"  NEW (bytearray):       {new_t:8.3f} s")
print(f"  IDENTICAL BYTES: {st_old == st_new}   speedup: {old_t/new_t:.0f}x   saved/build: {old_t-new_t:.1f}s")
del st_old, st_new, strings
gc.collect()

# ---------- PROBE 2: zlib level-6 compress + decompress throughput on REAL map data ----------
print("\n=== PROBE 2: zlib throughput on real map DATA (seek-based sample) ===")
DATA_START = 0x800
with open(ARC, 'rb') as f:
    hdr = f.read(28)
    assert hdr[0:4] == b'ARC\x00'
    num_entries = struct.unpack_from('<I', hdr, 8)[0]
    num_data    = struct.unpack_from('<I', hdr, 0x0C)[0]
    toc_size    = struct.unpack_from('<I', hdr, 0x10)[0]
    string_size = struct.unpack_from('<I', hdr, 0x14)[0]
    toc_offset  = struct.unpack_from('<I', hdr, 0x18)[0]
    string_start = toc_offset + toc_size
    records_start = string_start + string_size
    # TOC: num_data parts x 12 bytes
    f.seek(toc_offset); toc_raw = f.read(num_data * 12)
    # records: num_entries x 44 bytes
    f.seek(records_start); rec_raw = f.read(num_entries * 44)
    # find world01.map = the entry_type==3 with the most parts (the big map)
    best = None
    for i in range(num_entries):
        r = rec_raw[i*44:(i+1)*44]
        etype = struct.unpack_from('<I', r, 0)[0]
        nparts = struct.unpack_from('<I', r, 28)[0]
        fidx   = struct.unpack_from('<I', r, 32)[0]
        if etype == 3 and (best is None or nparts > best[0]):
            best = (nparts, fidx)
    nparts, fidx = best
    print(f"  world01.map: {nparts} parts starting at TOC idx {fidx}")
    # Decompress the FIRST ~200 parts only (~50MB) to build a real sample
    SAMPLE_PARTS = min(200, nparts)
    sample = bytearray()
    for pi in range(fidx, fidx + SAMPLE_PARTS):
        p_off  = struct.unpack_from('<I', toc_raw, pi*12)[0]
        p_comp = struct.unpack_from('<I', toc_raw, pi*12+4)[0]
        p_dec  = struct.unpack_from('<I', toc_raw, pi*12+8)[0]
        f.seek(p_off); cbytes = f.read(p_comp)
        if p_comp == p_dec:
            sample += cbytes
        else:
            try: sample += zlib.decompress(cbytes, 15)
            except zlib.error:
                try: sample += zlib.decompress(cbytes, -15)
                except zlib.error: sample += zlib.decompress(cbytes)
sample = bytes(sample)
smb = len(sample)/1024/1024
print(f"  sample decompressed: {smb:.1f} MB from {SAMPLE_PARTS} parts")

# compress throughput at level 6 in 256KB parts (mirrors set_file exactly)
PART = 262144
t = time.perf_counter()
total_comp = 0
pos = 0
while pos < len(sample):
    chunk = sample[pos:pos+PART]
    c = zlib.compress(chunk, 6)
    if len(c) >= len(chunk): c = chunk
    total_comp += len(c)
    pos += PART
comp_t = time.perf_counter() - t
comp_mbps = smb / comp_t
print(f"  zlib L6 compress (256KB parts): {comp_t:.3f}s for {smb:.1f}MB -> {comp_mbps:.1f} MB/s  (ratio {total_comp/len(sample):.3f})")

# decompress throughput
comp_whole = zlib.compress(sample, 6)
t = time.perf_counter()
_ = zlib.decompress(comp_whole)
dec_t = time.perf_counter() - t
print(f"  zlib decompress:                {dec_t:.3f}s for {smb:.1f}MB -> {smb/dec_t:.1f} MB/s")

# Extrapolate to full map
FULL_MAP_MB = 685.0
print(f"\n  EXTRAPOLATION to {FULL_MAP_MB:.0f}MB map:")
print(f"    set_file recompress @ L6:  ~{FULL_MAP_MB/comp_mbps:.0f}s")
print(f"    base-map decompress (load):~{FULL_MAP_MB/(smb/dec_t):.0f}s  x2 loads (SVAERA+SV, SV smaller)")
del sample, comp_whole
gc.collect()
print("\nDONE.")
