"""probe_soul_act_signal2.py - R-100 #11 recon step 4: deeper act discriminators."""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    act_of = {}
    for act in range(1, 5):
        f = 'records\\item\\formulas\\n_0%d_lesserpotionofexperience_formula.dbr' % act
        ff = db.get_fields(f) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == 'reagent1BaseName':
                for v in tf.values:
                    if isinstance(v, str) and v:
                        act_of[n(v)] = act
    drop_of = defaultdict(set)
    for r in db.record_names():
        rl = n(r)
        if '\\creature' not in rl:
            continue
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == 'lootFinger2Item1':
                for v in tf.values:
                    if isinstance(v, str) and v:
                        drop_of[n(v)].add(rl)
    proxy_refs = defaultdict(set)
    for r in db.record_names():
        rl = n(r)
        if not rl.startswith('records\\proxies'):
            continue
        ff = db.get_fields(r) or {}
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and '\\creature' in n(v):
                    proxy_refs[n(v)].add(rl)
    seg = defaultdict(Counter)
    for p, act in act_of.items():
        for m in drop_of.get(p, ()):
            for q in proxy_refs.get(m, ()):
                parts = q.split('\\')
                seg[act]['\\'.join(parts[1:4])] += 1
    print("PROXY path segments 1..3 per act:")
    for act in sorted(seg):
        print("act%d:" % act)
        for k, v in seg[act].most_common(12):
            print("     %6d  %s" % (v, k))
    mseg = defaultdict(Counter)
    for p, act in act_of.items():
        for m in drop_of.get(p, ()):
            mseg[act]['\\'.join(m.split('\\')[1:4])] += 1
    print("\nMONSTER path segments 1..3 per act:")
    for act in sorted(mseg):
        print("act%d:" % act)
        for k, v in mseg[act].most_common(12):
            print("     %6d  %s" % (v, k))
    # cross-act ambiguity: does any monster folder appear in 2+ acts?
    folder_acts = defaultdict(set)
    for p, act in act_of.items():
        for m in drop_of.get(p, ()):
            folder_acts['\\'.join(m.split('\\')[1:4])].add(act)
    multi = {k: sorted(v) for k, v in folder_acts.items() if len(v) > 1}
    print("\nmonster folders spanning multiple acts: %d" % len(multi))
    for k, v in sorted(multi.items())[:20]:
        print("    ", k, v)
    # SOUL folder -> acts
    sf = defaultdict(set)
    for p, act in act_of.items():
        sf['\\'.join(p.split('\\')[:5])].add(act)
    print("\nsoul folders spanning multiple acts: %d / %d" %
          (sum(1 for v in sf.values() if len(v) > 1), len(sf)))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
