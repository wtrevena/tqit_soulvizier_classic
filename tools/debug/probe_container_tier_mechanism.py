"""probe_container_tier_mechanism.py - R-100 #17: HOW does a container drop the
difficulty-correct relic tier?

Two candidate mechanisms:
  (M1) difficulty-indexed 3-value arrays (proven for Monster.tpl lootMisc2Item1)
  (M2) level-banded default tables (G_Default_<lo>-<hi>) that each name one tier

This probe measures which one container-side loot records actually use.

Usage: py tools/debug/probe_container_tier_mechanism.py <arz>
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    names = db.record_names()
    lower = {n(x): x for x in names}

    # M1: does ANY record carry a lootNNameM field with 3 values?
    multi = Counter()
    examples = {}
    for r in names:
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            b = k.split('###')[0]
            if b.startswith('loot') and 'Name' in b and len(tf.values) > 1:
                strs = [v for v in tf.values if isinstance(v, str) and v]
                if len(strs) > 1:
                    multi[b] += 1
                    examples.setdefault(b, (r, strs))
    print("M1 - lootNNameM fields with >1 value: %d field-instances" % sum(multi.values()))
    for k, v in multi.most_common(10):
        print("    %-16s %5d   e.g. %s -> %s" % (k, v, examples[k][0], examples[k][1][:3]))

    # M2: the level-banded default tables and the relic tier each names
    print("\nM2 - G_Default_* band tables and the relic tier they name:")
    rows = []
    for r in sorted(names):
        rl = n(r)
        if 'containers\\defaultloot\\' not in rl:
            continue
        ff = db.get_fields(r) or {}
        tiers = set()
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and 'loottables\\relics\\' in n(v):
                    tiers.add(n(v).rsplit('\\', 1)[-1][:2])
        if tiers:
            rows.append((rl.rsplit('\\', 1)[-1], sorted(tiers)))
    for name, tiers in rows[:60]:
        print("    %-28s %s" % (name, tiers))
    print("    ... %d band tables naming a relic table" % len(rows))

    # the SV mega-chest donor + the shipped vault chest loot tables
    for p in (r'records\drxitem\container\loottable_hidden_bloodcave_03.dbr',
              r'records\item\loottables\svc\polisvault_01.dbr',
              r'records\item\loottables\svc\polisvault_03.dbr',
              r'records\drxitem\container\svc_polisvault_chest_01.dbr'):
        rec = lower.get(n(p))
        if not rec:
            print("\n(absent) %s" % p)
            continue
        print("\n== %s Class=%s" % (rec, db.get_field_value(rec, 'Class')))
        ff = db.get_fields(rec) or {}
        for k in sorted(ff):
            b = k.split('###')[0]
            vals = ff[k].values
            if not vals:
                continue
            if not (b.lower().startswith(('loot', 'tables', 'num', 'gold'))):
                continue
            print("    %-24s n=%d %s" % (b, len(vals), vals))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
