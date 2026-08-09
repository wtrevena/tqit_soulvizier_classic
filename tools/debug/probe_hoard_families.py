"""probe_hoard_families.py - trace every MOD proxy's accessory1/Epic1/Legendary1
difficulty chain to its FixedItemLoot table and print each relic/unique slot with its
tier letter, so the wrong-tier leaks (general guards, etc.) are visible from bytes.

Usage: py tools/debug/probe_hoard_families.py <arz>
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def scalar(v):
    return v[0] if isinstance(v, list) and v else v


def tier_of_relic(pathl):
    m = re.search(r'\\relics\\(\d\d)_act', pathl)
    return m.group(1) if m else None


def tier_of_unique(pathl):
    m = re.search(r'unique_[a-z0-9]+_([nel])0?\d', pathl)
    return m.group(1) if m else None


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    lower = {n(x): x for x in db.record_names()}

    def real(p):
        return lower.get(n(p))

    def gv(rec, f):
        r = real(rec) if isinstance(rec, str) else rec
        return scalar(db.get_field_value(r, f)) if r else None

    def loot_slots(loot):
        r = real(loot)
        if not r:
            return []
        ff = db.get_fields(r) or {}
        out = []
        for k, tf in ff.items():
            b = k.split('###')[0]
            if not b.lower().startswith('loot'):
                continue
            for v in tf.values:
                if isinstance(v, str) and v:
                    out.append((b, v))
        return out

    # find mod proxies with accessory difficulty slots
    ACC = [('accessory1', 'n'), ('accessoryEpic1', 'e'), ('accessoryLegendary1', 'l')]
    proxies = []
    for name in db.record_names():
        nl = n(name)
        if db._record_types.get(name) != 'Proxy':
            continue
        if 'svc_' not in nl and '\\drxmap\\proxy\\' not in nl and 'obs_roulette' not in nl:
            continue
        if any(db.get_field_value(name, slot) for slot, _ in ACC):
            proxies.append(name)

    print("mod proxies with accessory chains: %d" % len(proxies))
    for px in sorted(proxies):
        rows = []
        flagged = False
        for slot, want in ACC:
            pool = gv(px, slot)
            if not pool:
                continue
            fin = gv(pool, 'fixedItemName1')
            loot = gv(fin, 'tables') if fin else None
            finl = n(fin or '')
            mod_owned = ('svc_' in n(loot or '') or 'loottables\\svc\\' in n(loot or ''))
            tier_hits = []
            for f, val in loot_slots(loot):
                vl = n(val)
                if '\\relics\\' in vl and vl.endswith('_relics.dbr'):
                    t = tier_of_relic(vl)
                    ok = {'n': '01', 'e': '02', 'l': '03'}[want] == t
                    tier_hits.append(('relic', f, t, ok))
                    if not ok and mod_owned:
                        flagged = True
                elif 'unique_' in vl and '\\mastertables\\' in vl:
                    t = tier_of_unique(vl)
                    ok = (t == want)
                    tier_hits.append(('unique', f, t, ok))
                    if not ok and mod_owned:
                        flagged = True
            rows.append((slot, want, loot, mod_owned, tier_hits))
        if not rows:
            continue
        mark = 'LEAK>>' if flagged else '  ok  '
        print("\n%s %s" % (mark, px))
        for slot, want, loot, mod_owned, hits in rows:
            print("    %-20s want=%s mod=%s loot=%s" %
                  (slot, want, mod_owned, (loot or '-').split('\\')[-1]))
            for kind, f, t, ok in hits:
                if not ok:
                    print("        %s %s = tier %s  %s" %
                          (kind, f, t, 'WRONG' if not ok else ''))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
