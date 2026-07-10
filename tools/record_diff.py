"""Bucketed record-diff between two .arz files (build-wave verification).

Decodes every record in OLD and NEW, then reports ADDED / REMOVED / MODIFIED
records. For MODIFIED records it lists the changed fields (old -> new). An
optional --bucket substring filter and --summary mode keep the output readable
for large waves.

Usage:
  py tools/record_diff.py <old.arz> <new.arz> [--summary] [--grep SUBSTR]
      [--fields] [--limit N]

Exit code is always 0 (informational tool).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def _norm(s):
    return str(s).replace('/', '\\').lower()


def _fields(db, name):
    out = {}
    ff = db.get_fields(name)
    if not ff:
        return out
    for k, tf in ff.items():
        base = k.split('###')[0]
        out.setdefault(base, tf.values)
    return out


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 0
    old_p, new_p = argv[1], argv[2]
    summary = '--summary' in argv
    show_fields = '--fields' in argv
    grep = None
    limit = None
    for i, a in enumerate(argv):
        if a == '--grep' and i + 1 < len(argv):
            grep = _norm(argv[i + 1])
        if a == '--limit' and i + 1 < len(argv):
            limit = int(argv[i + 1])

    old = ArzDatabase.from_arz(Path(old_p))
    new = ArzDatabase.from_arz(Path(new_p))

    old_names = {_norm(n): n for n in old.record_names()}
    new_names = {_norm(n): n for n in new.record_names()}

    if grep:
        old_names = {k: v for k, v in old_names.items() if grep in k}
        new_names = {k: v for k, v in new_names.items() if grep in k}

    added = sorted(set(new_names) - set(old_names))
    removed = sorted(set(old_names) - set(new_names))
    common = sorted(set(old_names) & set(new_names))

    modified = []
    for k in common:
        of = _fields(old, old_names[k])
        nf = _fields(new, new_names[k])
        keys = set(of) | set(nf)
        deltas = []
        for fk in sorted(keys):
            ov = of.get(fk)
            nv = nf.get(fk)
            if ov != nv:
                deltas.append((fk, ov, nv))
        if deltas:
            modified.append((new_names[k], deltas))

    print("=" * 72)
    print("RECORD DIFF")
    print(f"  OLD: {old_p}")
    print(f"  NEW: {new_p}")
    if grep:
        print(f"  grep: {grep}")
    print(f"  ADDED   : {len(added)}")
    print(f"  REMOVED : {len(removed)}")
    print(f"  MODIFIED: {len(modified)}")
    print("=" * 72)

    def cap(lst):
        return lst[:limit] if limit else lst

    if added:
        print(f"\n-- ADDED ({len(added)}) --")
        for k in cap(added):
            print(f"  + {new_names[k]}")
    if removed:
        print(f"\n-- REMOVED ({len(removed)}) --")
        for k in cap(removed):
            print(f"  - {old_names[k]}")
    if modified:
        print(f"\n-- MODIFIED ({len(modified)}) --")
        for name, deltas in cap(modified):
            print(f"  ~ {name}  ({len(deltas)} field(s))")
            if not summary:
                for fk, ov, nv in deltas:
                    if show_fields or len(str(ov)) + len(str(nv)) < 160:
                        print(f"      {fk}: {ov} -> {nv}")
                    else:
                        print(f"      {fk}: <changed> (len {len(str(ov))}->{len(str(nv))})")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
