"""probe_gaoler_chests.py - R-100 #17: the shipped Gaoler vault chests + the DRX
hidden-chest convention they were cloned from.

Usage: py tools/debug/probe_gaoler_chests.py <built.arz>
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def dump(db, rec, pref=('loot', 'tables', 'num', 'gold', 'locked', 'Locked')):
    print("\n== %s  Class=%s" % (rec, db.get_field_value(rec, 'Class')))
    ff = db.get_fields(rec) or {}
    for k in sorted(ff):
        b = k.split('###')[0]
        vals = ff[k].values
        if not vals or all(v in ('', 0, 0.0) for v in vals):
            continue
        if not b.lower().startswith(tuple(p.lower() for p in pref)):
            continue
        print("    %-24s n=%d %s" % (b, len(vals), vals))


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    names = db.record_names()
    lower = {n(x): x for x in names}

    print("### the 5 vault chests + their loot tables")
    for i in range(1, 6):
        for p in (r'records\drxitem\container\svc_polisvault_chest_%02d.dbr' % i,
                  r'records\item\loottables\svc\polisvault_%02d.dbr' % i):
            rec = lower.get(n(p))
            if rec:
                dump(db, rec)
            else:
                print("\n(absent) %s" % p)

    print("\n\n### DRX hidden-bloodcave loot tables and who references them")
    refs = defaultdict(set)
    for r in names:
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and 'loottable_hidden_bloodcave' in n(v):
                    refs[n(v)].add(r)
    for t in sorted(refs):
        print("  %s <- %d referencer(s)" % (t, len(refs[t])))
        for r in sorted(refs[t])[:6]:
            tv = db.get_field_value(r, 'tables')
            print("        %s   tables=%s" % (r, tv))

    print("\n\n### every record whose 'tables' names 2+ svc/drx loot tables")
    for r in sorted(names):
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            if k.split('###')[0] != 'tables':
                continue
            vv = [v for v in tf.values if isinstance(v, str) and v]
            if len(vv) > 1 and any('drx' in n(v) or '\\svc' in n(v) for v in vv):
                print("  %s -> %s" % (r, vv))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
