"""probe_soul_act_assign.py - R-100 #11: how many souls are missing from the XP
forge formulas, and how many can be act-assigned from EVIDENCE in the db?

Signals, in precedence order (each one measured, none guessed):
  S1  the soul's own act is already declared by a sibling tier of the SAME soul
      (n/e/l triple: if _e is listed in act3, _n and _l belong to act3)
  S2  the dropping monster's namespace: records\\xpack\\ -> act4 (Hades / IT)
  S3  the dropping monster's population-proxy region: proxies greek -> act1,
      proxies egypt -> act2, proxies orient -> act3 (majority vote)
  S4  the dropping monster's PLACED proxy (drxmap) region name, when it names an
      act region unambiguously
  S5  other classified souls in the SAME soul folder (majority, only when
      unanimous)

Usage: py tools/debug/probe_soul_act_assign.py <built.arz> [--list]
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

DIFF_OF_PREFIX = {'n': 'n', 'e': 'e', 'l': 'l'}


def n(s):
    return str(s).replace('/', '\\').lower()


def soul_stem(p):
    return n(p).rsplit('\\', 1)[-1].replace('.dbr', '')


def tier_of(stem):
    if stem.endswith('_n'):
        return 'n'
    if stem.endswith('_e'):
        return 'e'
    if stem.endswith('_l'):
        return 'l'
    return None


def base_of(stem):
    t = tier_of(stem)
    return stem[:-2] if t else stem


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    names = db.record_names()
    lower = {n(x): x for x in names}

    # formula membership
    act_of = {}          # soul path (norm) -> act
    formula_of = {}      # (tier, act) -> record
    for tier in ('n', 'e', 'l'):
        for act in range(1, 6):
            f = 'records\\item\\formulas\\%s_0%d_lesserpotionofexperience_formula.dbr' % (tier, act)
            rec = lower.get(f)
            if not rec:
                continue
            formula_of[(tier, act)] = rec
            ff = db.get_fields(rec) or {}
            for k, tf in ff.items():
                if k.split('###')[0] == 'reagent1BaseName':
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            act_of[n(v)] = act
    print("formulas found: %s" % sorted(formula_of))
    print("classified soul paths: %d" % len(act_of))

    souls = [x for x in names
             if 'equipmentring\\soul\\' in n(x) and 'anysoul' not in n(x)]
    print("soul records: %d" % len(souls))

    # dropping monsters
    drop_of = defaultdict(set)
    for r in names:
        rl = n(r)
        if '\\creature' not in rl:
            continue
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == 'lootFinger2Item1':
                for v in tf.values:
                    if isinstance(v, str) and v:
                        drop_of[n(v)].add(rl)

    # proxy region membership
    region_of_monster = defaultdict(Counter)
    for r in names:
        rl = n(r)
        if not rl.startswith('records\\proxies'):
            continue
        seg = rl.split('\\')[1]         # e.g. 'proxies greek'
        region = None
        if 'greek' in seg:
            region = 1
        elif 'egypt' in seg:
            region = 2
        elif 'orient' in seg:
            region = 3
        if region is None:
            continue
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and '\\creature' in n(v):
                    region_of_monster[n(v)][region] += 1

    # folder majority
    folder_acts = defaultdict(Counter)
    for p, a in act_of.items():
        folder_acts['\\'.join(p.split('\\')[:5])][a] += 1

    unlisted = [s for s in souls if n(s) not in act_of]
    print("UNLISTED souls: %d" % len(unlisted))

    method = Counter()
    resolved = {}
    # S1 sibling tier
    by_base = defaultdict(dict)
    for s in souls:
        st = soul_stem(s)
        t = tier_of(st)
        if t:
            by_base[(n(s).rsplit('\\', 1)[0], base_of(st))][t] = n(s)
    for key, tiers in by_base.items():
        acts = {act_of[p] for p in tiers.values() if p in act_of}
        if len(acts) == 1:
            a = acts.pop()
            for p in tiers.values():
                if p not in act_of:
                    resolved[p] = ('S1-sibling-tier', a)

    for s in unlisted:
        p = n(s)
        if p in resolved:
            continue
        ms = drop_of.get(p, set())
        # S2 namespace
        acts = set()
        for m in ms:
            if m.startswith('records\\xpack\\'):
                acts.add(4)
        if len(acts) == 1:
            resolved[p] = ('S2-xpack-namespace', acts.pop())
            continue
        # S3 proxy region
        votes = Counter()
        for m in ms:
            votes.update(region_of_monster.get(m, {}))
        if votes:
            top, cnt = votes.most_common(1)[0]
            if len(votes) == 1 or cnt >= 2 * sum(v for k, v in votes.items() if k != top):
                resolved[p] = ('S3-proxy-region', top)
                continue
        # S5 folder unanimity
        fa = folder_acts.get('\\'.join(p.split('\\')[:5]))
        if fa and len(fa) == 1:
            resolved[p] = ('S5-folder-unanimous', next(iter(fa)))
            continue

    for p, (m, a) in resolved.items():
        method[m] += 1
    print("\nresolved: %d / %d unlisted" % (
        len([p for p in resolved if p not in act_of]), len(unlisted)))
    for k, v in method.most_common():
        print("    %-24s %d" % (k, v))
    unresolved = [s for s in unlisted if n(s) not in resolved]
    print("UNRESOLVED: %d" % len(unresolved))
    byfolder = Counter('\\'.join(n(s).split('\\')[:5]) for s in unresolved)
    for k, v in byfolder.most_common(25):
        print("    %5d  %s" % (v, k))
    if '--list' in argv:
        for s in sorted(unresolved):
            print("      ", s, " drops<-", sorted(drop_of.get(n(s), ()))[:2])


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
