"""Definitive map-pack cost: stream all world01.map parts, decompress + recompress
each (mirrors ArcArchive.set_file exactly). Low memory (one part at a time).
Also proves whether recompress(decompress(part)) == part  -> byte-identity of an
incremental part-cache. Read-only."""
import struct, zlib, time
from pathlib import Path

ARC = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')
PART = 262144

with open(ARC, 'rb') as f:
    hdr = f.read(28)
    num_entries = struct.unpack_from('<I', hdr, 8)[0]
    num_data    = struct.unpack_from('<I', hdr, 0x0C)[0]
    toc_size    = struct.unpack_from('<I', hdr, 0x10)[0]
    string_size = struct.unpack_from('<I', hdr, 0x14)[0]
    toc_offset  = struct.unpack_from('<I', hdr, 0x18)[0]
    records_start = toc_offset + toc_size + string_size
    f.seek(toc_offset); toc_raw = f.read(num_data * 12)
    f.seek(records_start); rec_raw = f.read(num_entries * 44)
    best = None
    for i in range(num_entries):
        r = rec_raw[i*44:(i+1)*44]
        if struct.unpack_from('<I', r, 0)[0] == 3:
            nparts = struct.unpack_from('<I', r, 28)[0]
            fidx   = struct.unpack_from('<I', r, 32)[0]
            if best is None or nparts > best[0]:
                best = (nparts, fidx)
    nparts, fidx = best
    print(f"world01.map: {nparts} parts")

    comp_t = 0.0; dec_t = 0.0
    total_dec = 0; total_comp_in = 0; total_comp_out = 0
    identical = 0; stored = 0; differ = 0
    diff_examples = []
    for k, pi in enumerate(range(fidx, fidx + nparts)):
        p_off  = struct.unpack_from('<I', toc_raw, pi*12)[0]
        p_comp = struct.unpack_from('<I', toc_raw, pi*12+4)[0]
        p_dec  = struct.unpack_from('<I', toc_raw, pi*12+8)[0]
        f.seek(p_off); cbytes = f.read(p_comp)
        if p_comp == p_dec:
            stored += 1
            total_dec += p_dec
            continue
        t = time.perf_counter()
        dec = zlib.decompress(cbytes, 15) if cbytes[:1] else zlib.decompress(cbytes)
        dec_t += time.perf_counter() - t
        total_dec += len(dec)
        # recompress exactly as set_file does
        t = time.perf_counter()
        rc = zlib.compress(dec, 6)
        if len(rc) >= len(dec): rc = dec
        comp_t += time.perf_counter() - t
        total_comp_in += len(dec); total_comp_out += len(rc)
        if rc == cbytes:
            identical += 1
        else:
            differ += 1
            if len(diff_examples) < 3:
                diff_examples.append((pi, len(cbytes), len(rc)))

print(f"\n--- DECOMPRESS (load side) ---")
print(f"  decompressed total: {total_dec/1024/1024:.0f} MB   time: {dec_t:.1f}s   -> {(total_dec/1024/1024)/dec_t:.0f} MB/s")
print(f"--- RECOMPRESS L6 (set_file pack side) ---")
print(f"  compress input: {total_comp_in/1024/1024:.0f} MB   time: {comp_t:.1f}s   -> {(total_comp_in/1024/1024)/comp_t:.0f} MB/s")
print(f"  compressed out: {total_comp_out/1024/1024:.0f} MB (ratio {total_comp_out/max(1,total_comp_in):.3f})")
print(f"--- BYTE-IDENTITY of recompress(decompress(part)) ---")
print(f"  identical parts: {identical}   stored(raw) parts: {stored}   DIFFERING: {differ}")
if diff_examples:
    print(f"  diff examples (partIdx, origComp, recomp): {diff_examples}")
print(f"\nINTERPRETATION: full-map set_file pack ~= {comp_t:.0f}s; full-map load decompress ~= {dec_t:.0f}s")
print(f"  If DIFFERING==0 -> an incremental part-cache (skip unchanged parts) is byte-identical & safe.")
