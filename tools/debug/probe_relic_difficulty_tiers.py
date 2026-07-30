"""probe_relic_difficulty_tiers.py - R-100 #17 recon: the essence/embodiment mis-wire.

Will: the Soul Gaoler's chests "on epic are dropping 'essence' like 'essence of the
chill of tartarus' which should only drop on normal instead of dropping the epic
version which starts with 'embodiment'".

Measures:
  1. what 01_/02_/03_actN_relics.dbr actually contain (tier naming proof)
  2. HOW the base game selects the difficulty-correct relic table for a container
     (who references 01_ vs 02_ vs 03_, and through what field)

Usage: py tools/debug/probe_relic_difficulty_tiers.py <arz>
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

    # 1. tier naming proof
    for tier in ('01', '02', '03'):
        p = n(r'records\xpack\item\loottables\relics\%s_act4_relics.dbr' % tier)
        real = lower.get(p)
        if not real:
            print("MISSING", p)
            continue
        ff = db.get_fields(real) or {}
        items = []
        for k, tf in ff.items():
            b = k.split('###')[0]
            if b.startswith('lootName'):
                for v in tf.values:
                    if isinstance(v, str) and v:
                        items.append(v)
        print("\n%s : Class=%s  entries=%d" % (real, db.get_field_value(real, 'Class'), len(items)))
        for it in items[:4]:
            rp = lower.get(n(it))
            tag = db.get_field_value(rp, 'description') if rp else None
            tag2 = db.get_field_value(rp, 'itemNameTag') if rp else None
            print("      %s  desc=%s nameTag=%s" % (it, tag, tag2))

    # 2. who references each tier, and via which field
    refs = defaultdict(Counter)
    field_of = defaultdict(Counter)
    for r in names:
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            b = k.split('###')[0]
            for v in tf.values:
                if not isinstance(v, str):
                    continue
                vl = n(v)
                if 'loottables\\relics\\' in vl and vl.endswith('_relics.dbr'):
                    stem = vl.rsplit('\\', 1)[-1]
                    refs[stem][n(r).rsplit('\\', 1)[-1]] += 1
                    field_of[stem][b] += 1
    print("\n\nreferencers per relic table (act4 only):")
    for stem in sorted(refs):
        if 'act4' not in stem:
            continue
        print("  %s : %d distinct referencers; fields=%s" %
              (stem, len(refs[stem]), dict(field_of[stem])))
        for k, v in refs[stem].most_common(8):
            print("        ", k)


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
