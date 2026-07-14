"""Byte-identity + speed proof for HOTSPOT 3 (map pack):
  (A) thread-parallel pack == serial pack, byte-for-byte, on REAL world01.map
      data (the win); also measures the speedup.
  (B) reusing an already-loaded (and read-only-decompressed) ArcArchive to write
      == a fresh ArcArchive.from_file, byte-for-byte (the base-ARC-reuse win).

Memory-light: samples a slice of real map parts (seek-based) for (A); uses a
small real .arc for (B). No full map load, no full build. Read-only vs the repo.

Usage:  py verify_map_pack.py [sample_parts]
"""
import struct, zlib, time, os, sys, hashlib, importlib.util
from pathlib import Path

REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
BIG_ARC = REPO / 'local' / 'Levels_merged.arc'
SMALL_ARC = REPO / 'local' / 'Text.arc'
TOOLS = Path(__file__).resolve().parents[3] / 'tools'   # worktree tools/ (patched)


def load_arc_patcher():
    spec = importlib.util.spec_from_file_location(
        "arc_patcher_ut", str(TOOLS / 'arc_patcher.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_map_sample(arc_path: Path, sample_parts: int) -> bytes:
    """Reconstruct the first `sample_parts` decompressed parts of the biggest
    type-3 file (world01.map), seek-based, one part at a time."""
    with open(arc_path, 'rb') as f:
        hdr = f.read(28)
        assert hdr[0:4] == b'ARC\x00'
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
        n = min(sample_parts, nparts)
        out = bytearray()
        for pi in range(fidx, fidx + n):
            p_off  = struct.unpack_from('<I', toc_raw, pi*12)[0]
            p_comp = struct.unpack_from('<I', toc_raw, pi*12+4)[0]
            p_dec  = struct.unpack_from('<I', toc_raw, pi*12+8)[0]
            f.seek(p_off); cb = f.read(p_comp)
            if p_comp == p_dec:
                out += cb
            else:
                try: out += zlib.decompress(cb, 15)
                except zlib.error:
                    try: out += zlib.decompress(cb, -15)
                    except zlib.error: out += zlib.decompress(cb)
        return bytes(out), nparts


def parts_digest(parts):
    """A single md5 over the ordered (comp_size, decomp_size, bytes) of a part
    list - equal digest <=> byte-identical pack output."""
    h = hashlib.md5()
    for p in parts:
        h.update(struct.pack('<II', p.comp_size, p.decomp_size))
        h.update(p.compressed_data)
    return h.hexdigest()


def md5_bytes(b): return hashlib.md5(b).hexdigest()


def test_A(ap, sample_parts):
    print("=== TEST A: parallel pack == serial pack (REAL world01.map data) ===")
    sample, total_parts = read_map_sample(BIG_ARC, sample_parts)
    smb = len(sample) / 1024 / 1024
    n_chunks = (len(sample) + ap.PART_SIZE - 1) // ap.PART_SIZE
    print(f"  sample: {smb:.1f} MB -> {n_chunks} parts "
          f"(full map has {total_parts} parts)")

    os.environ['SVC_ARC_PARALLEL'] = '0'          # force serial
    t = time.perf_counter(); serial = ap._pack_parts(sample); ts = time.perf_counter() - t

    os.environ['SVC_ARC_PARALLEL'] = str(min(os.cpu_count() or 1, 8))  # parallel
    t = time.perf_counter(); par = ap._pack_parts(sample); tp = time.perf_counter() - t
    os.environ.pop('SVC_ARC_PARALLEL', None)

    dser, dpar = parts_digest(serial), parts_digest(par)
    ok = (dser == dpar) and (len(serial) == len(par))
    print(f"  serial  : {ts:7.3f} s  digest {dser}")
    print(f"  parallel: {tp:7.3f} s  digest {dpar}  ({min(os.cpu_count() or 1,8)} threads)")
    print(f"  BYTE-IDENTICAL: {ok}   speedup: {ts/tp:.2f}x   "
          f"(extrapolated full-map serial ~{ts/smb*1998:.0f}s -> parallel ~{tp/smb*1998:.0f}s)")
    return ok


def test_B(ap):
    print("\n=== TEST B: reuse-ARC write == fresh-from_file write (byte-identical) ===")
    # target = first type-3 entry of the small arc
    fresh = ap.ArcArchive.from_file(SMALL_ARC)
    name = next(e.name for e in fresh.entries if e.entry_type == 3)
    data = fresh.get_file(name)
    newdata = data + data[: len(data) // 3]   # a deterministic content change

    out_fresh = Path(os.environ['TMPDIR_PROBE']) / 'reuse_fresh.arc'
    out_reuse = Path(os.environ['TMPDIR_PROBE']) / 'reuse_reuse.arc'

    # FRESH path (mirrors the OLD code): load, set_file, write.
    a1 = ap.ArcArchive.from_file(SMALL_ARC)
    a1.set_file(name, newdata)
    a1.write(out_fresh)

    # REUSE path (mirrors ae_arc): load, DECOMPRESS an entry read-only (like the
    # top-of-main base-map read), THEN set_file the same entry + write.
    a2 = ap.ArcArchive.from_file(SMALL_ARC)
    _ = a2.decompress([e for e in a2.entries if e.entry_type == 3][0])  # read-only
    a2.set_file(name, newdata)
    a2.write(out_reuse)

    m1, m2 = md5_bytes(out_fresh.read_bytes()), md5_bytes(out_reuse.read_bytes())
    ok = (m1 == m2)
    print(f"  target entry: {name}")
    print(f"  fresh  md5: {m1}")
    print(f"  reuse  md5: {m2}")
    print(f"  BYTE-IDENTICAL: {ok}")
    return ok


if __name__ == '__main__':
    os.environ.setdefault('TMPDIR_PROBE', str(Path(sys.argv[2]) if len(sys.argv) > 2
                          else Path.cwd()))
    sample_parts = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    ap = load_arc_patcher()
    a = test_A(ap, sample_parts)
    b = test_B(ap)
    print(f"\nRESULT: parallel_pack_identical={a}  reuse_identical={b}")
    sys.exit(0 if (a and b) else 1)
