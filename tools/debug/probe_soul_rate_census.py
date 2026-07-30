"""probe_soul_rate_census.py - R-105/R-106/R-107 baseline census.

Cross-tabulates chanceToEquipFinger2 x monsterClassification over every
soul-CARRYING creature in a BUILT arz, using the same helpers the shipped
verify_soul_drop_rates gate uses, so the numbers are comparable to R-104/R-106.

Two carrier definitions are printed because R-104/R-106 counted 1,722 while the
shipped gate's own _has_soul() (lootFinger2Item1 must contain 'soul') is narrower:
  WIDE   = record has a chanceToEquipFinger2 field at all
  NARROW = record's lootFinger2Item1 names a soul (the gate's roster)

Usage: py tools/debug/probe_soul_rate_census.py <built.arz>
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import build_svc_database as bsd


def fv(fields, name):
    for k, tf in fields.items():
        if k.split('###')[0] == name and tf.values:
            return tf.values[0]
    return None


def fvl(fields, name):
    for k, tf in fields.items():
        if k.split('###')[0] == name:
            return list(tf.values)
    return []


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    wide = defaultdict(Counter)
    narrow = defaultdict(Counter)
    rows = []
    for name in db.record_names():
        f = db.get_fields(name)
        if not f:
            continue
        ch = fv(f, 'chanceToEquipFinger2')
        if ch is None:
            continue
        try:
            ch = float(ch)
        except (TypeError, ValueError):
            continue
        cls = str(fv(f, 'monsterClassification') or '(unset)')
        has_soul = any(isinstance(v, str) and 'soul' in v.lower()
                       for v in fvl(f, 'lootFinger2Item1'))
        wide[ch][cls] += 1
        if has_soul:
            narrow[ch][cls] += 1
        rows.append((name, cls, ch, has_soul))

    for label, tab in (('WIDE (any chanceToEquipFinger2 field)', wide),
                       ('NARROW (lootFinger2Item1 names a soul)', narrow)):
        print("\n==== %s" % label)
        total = 0
        for ch in sorted(tab, reverse=True):
            n = sum(tab[ch].values())
            total += n
            print("  %8.2f%%  n=%-5d  %s" % (ch, n, dict(tab[ch])))
        print("  TOTAL %d" % total)

    print("\n==== the cohorts this wave must move (NARROW roster)")
    for ch in (100.0, 66.0, 50.0, 25.0, 10.0, 5.0, 2.0, 0.5, 0.3):
        sel = [r for r in rows if r[3] and abs(r[2] - ch) < 0.001]
        if not sel:
            continue
        print("\n  --- %s%% : %d" % (ch, len(sel)))
        by = defaultdict(list)
        for name, cls, c, _ in sel:
            by[cls].append(name)
        for cls in sorted(by):
            print("      %-10s %d" % (cls, len(by[cls])))
            if len(by[cls]) <= 20 or cls in ('Common', '(unset)', 'Champion'):
                for nm in sorted(by[cls])[:20]:
                    print("            %s" % nm)


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
