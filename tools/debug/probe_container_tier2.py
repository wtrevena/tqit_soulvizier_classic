"""probe_container_tier2.py - R-100 #17: dump the real container loot chain."""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def dump(db, lower, p, only=None):
    rec = lower.get(n(p))
    if not rec:
        print("\n(absent) %s" % p)
        return None
    print("\n== %s  Class=%s" % (rec, db.get_field_value(rec, 'Class')))
    ff = db.get_fields(rec) or {}
    for k in sorted(ff):
        b = k.split('###')[0]
        vals = ff[k].values
        if not vals or all(v in ('', 0, 0.0) for v in vals):
            continue
        if only and not b.lower().startswith(only):
            continue
        print("    %-26s n=%d %s" % (b, len(vals), vals))
    return rec


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    names = db.record_names()
    lower = {n(x): x for x in names}
    # any 'tables' field with >1 value?
    c = Counter()
    ex = {}
    for r in names:
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            b = k.split('###')[0]
            if b in ('tables',) and len([v for v in tf.values if isinstance(v, str) and v]) > 1:
                c[b] += 1
                ex.setdefault(b, r)
    print("records whose 'tables' field carries >1 value: %s  e.g. %s" % (dict(c), ex))

    for p in (r'records\item\containers\defaultloot\g_default_51-53.dbr',
              r'records\item\containers\defaultloot\boss_default_51-53.dbr',
              r'records\item\containers\defaultloot\boss_default_35-37.dbr'):
        dump(db, lower, p, only='loot')


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
