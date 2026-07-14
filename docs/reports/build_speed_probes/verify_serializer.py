"""Byte-identity + speed proof for the arz serializer O(n^2) fix (HOTSPOT 1).

Loads a given arz_patcher.py DYNAMICALLY (so we can run the SAME real arz through
the git-OLD serializer and the worktree-NEW serializer in separate processes) and
writes a real .arz to a temp output, printing its md5 + the write time.

Usage:
    py verify_serializer.py <arz_patcher.py> <input.arz> <output.arz>

Then compare the two md5s: OLD == NEW  ==>  the fix is byte-identical.
Read-only w.r.t. the repo (writes only to the given scratch output path).
Memory-light: one arz load + one write (raw passthrough for unmodified records).
"""
import sys, time, hashlib, importlib.util
from pathlib import Path


def load_module(pyfile: Path):
    spec = importlib.util.spec_from_file_location("arz_under_test", str(pyfile))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    pyfile = Path(sys.argv[1])
    in_arz = Path(sys.argv[2])
    out_arz = Path(sys.argv[3])
    mod = load_module(pyfile)
    t = time.perf_counter()
    db = mod.ArzDatabase.from_arz(in_arz)
    load_t = time.perf_counter() - t
    t = time.perf_counter()
    db.write_arz(out_arz)
    write_t = time.perf_counter() - t
    print(f"MODULE:  {pyfile}")
    print(f"RECORDS: {len(db._raw_records)}  STRINGS: {len(db.strings)}")
    print(f"LOAD:    {load_t:8.3f} s")
    print(f"WRITE:   {write_t:8.3f} s   <-- serializer cost")
    print(f"OUT_MD5: {md5(out_arz)}")
    print(f"OUT_SIZE:{out_arz.stat().st_size}")


if __name__ == '__main__':
    main()
