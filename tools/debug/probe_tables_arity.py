"""probe_tables_arity.py - R-100 #17: what does a multi-value container `tables`
array MEAN? (difficulty triple, level bands, or a plain multi-roll list?)"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    by_arity = defaultdict(list)
    for r in db.record_names():
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            if k.split('###')[0] != 'tables':
                continue
            vv = [v for v in tf.values if isinstance(v, str) and v]
            if vv:
                by_arity[len(vv)].append((r, vv))
    for ar in sorted(by_arity):
        rows = by_arity[ar]
        print("\n=== arity %d : %d records" % (ar, len(rows)))
        for r, vv in rows[:6]:
            print("   %s" % r)
            for v in vv:
                print("        %s" % v)
    # relic tier per band table
    print("\n\nband table -> relic table named:")
    for r in sorted(db.record_names()):
        rl = n(r)
        if 'containers\\defaultloot\\' not in rl:
            continue
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and 'loottables\\relics\\' in n(v):
                    print("    %-32s %s" % (rl.rsplit('\\', 1)[-1], v))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
