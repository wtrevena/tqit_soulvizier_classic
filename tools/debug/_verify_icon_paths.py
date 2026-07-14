"""Verify a set of TQ resource paths (DRXtextures\\... etc.) resolve to a real
file inside one of the shipped Resources .arc archives.

A TQ resource path's FIRST component is the archive name (e.g. DRXtextures ->
DRXtextures.arc); the remainder is the in-arc file path. Match is
case-insensitive and slash-insensitive.

Usage: py tools/debug/_verify_icon_paths.py <resources_dir> < paths_on_stdin
   or  py ... <resources_dir> path1 path2 ...
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from arc_patcher import ArcArchive


def norm(p):
    return p.replace('\\', '/').lower().strip()


def main():
    res = Path(sys.argv[1])
    paths = sys.argv[2:]
    if not paths:
        paths = [l.strip() for l in sys.stdin if l.strip()]

    # Cache arc file lists lazily by archive name
    arc_cache = {}

    def arc_files(archive):
        if archive not in arc_cache:
            p = res / f'{archive}.arc'
            if not p.exists():
                arc_cache[archive] = None
            else:
                arc = ArcArchive.from_file(p)
                arc_cache[archive] = {norm(e.name) for e in arc.entries}
        return arc_cache[archive]

    ok = True
    for path in paths:
        parts = path.replace('/', '\\').split('\\')
        archive = parts[0]
        rest = norm('/'.join(parts[1:]))
        files = arc_files(archive)
        if files is None:
            print(f"  MISSING-ARC  {path}   (no {archive}.arc)")
            ok = False
            continue
        if rest in files:
            print(f"  OK           {path}")
        else:
            print(f"  NOT-FOUND    {path}   (in {archive}.arc)")
            ok = False
    print("\nALL RESOLVE" if ok else "\nSOME FAILED")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
