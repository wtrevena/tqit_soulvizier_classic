"""probe_loot_difficulty_arrays.py - R-100 #17 root cause: loot slots are
DIFFICULTY-INDEXED ARRAYS (index 0=normal, 1=epic, 2=legendary), exactly like
lootFinger2Item1 carries [soul_n, soul_e, soul_l].

Prints the raw value shape of every loot slot that references a tiered relic /
unique-weapon master table, for a handful of native referencers, so the 3-element
convention is proven rather than assumed.

Usage: py tools/debug/probe_loot_difficulty_arrays.py <arz> [record ...]
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


SAMPLES = [
    r'records\xpack\creatures\monster\gigantes\xsecrethero_wardenofsouls_48.dbr',
    r'records\item\containers\boss\small chests\greece\goldenchest_legendary_01.dbr',
    r'records\item\containers\boss\small chests\greece\goldenchest_legendary_02.dbr',
]


def dump(db, rec):
    ff = db.get_fields(rec) or {}
    if not ff:
        print("  (absent) %s" % rec)
        return
    print("\n== %s  Class=%s" % (rec, db.get_field_value(rec, 'Class')))
    for k in sorted(ff):
        b = k.split('###')[0]
        vals = ff[k].values
        if not any(isinstance(v, str) and v for v in vals):
            continue
        if not (b.lower().startswith('loot') or b.lower().startswith('tables')):
            continue
        print("    %-22s n=%d  %s" % (b, len(vals), vals))


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    names = db.record_names()
    lower = {n(x): x for x in names}
    for s in (argv[2:] or SAMPLES):
        rec = lower.get(n(s))
        if rec:
            dump(db, rec)
        else:
            print("  (absent) %s" % s)

    # global: how many values do loot slots that name a tiered relic table carry?
    shapes = Counter()
    for r in names:
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            b = k.split('###')[0]
            hit = any(isinstance(v, str) and 'loottables\\relics\\' in n(v)
                      for v in tf.values)
            if hit:
                shapes[(b, len(tf.values))] += 1
    print("\n\n(field, value-count) shapes for slots naming a relic table:")
    for k, v in shapes.most_common(20):
        print("    %-32s %s" % (k, v))

    # the unique-weapon master tables: is unique_1h_n01 a normal-only tier?
    print("\nunique_*_?01 master tables present:")
    for r in sorted(names):
        rl = n(r)
        if 'mastertables\\unique_' in rl:
            print("   ", r)


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
