"""probe_soul_act_signal.py - R-100 #11 recon, step 3: WHAT DECIDES A SOUL'S ACT?

The 12 XP-potion formulas enumerate soul paths per (difficulty, act). To place OUR
minted souls into the right list we need an EVIDENCE-BASED act signal. This probe
measures, over SV 0.98i's own already-classified souls, three candidate signals:

  A. soul levelRequirement / itemLevel bands per act
  B. the dropping monster's record namespace (base / xpack / xpack2)
  C. the population-proxy path that spawns the dropping monster (records\\proxies\\...)

Usage: py tools/debug/probe_soul_act_signal.py <arz>
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def norm(s):
    return str(s).replace('/', '\\').lower()


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    names = db.record_names()
    # act membership from the NORMAL-difficulty formulas (n_0N_...)
    act_of = {}
    for act in range(1, 5):
        f = fr'records\item\formulas\n_0{act}_lesserpotionofexperience_formula.dbr'
        if not db.has_record(f):
            print("MISSING FORMULA", f)
            continue
        for v in (db.get_field_value(f, 'reagent1BaseName') or []) if isinstance(
                db.get_field_value(f, 'reagent1BaseName'), list) else []:
            pass
        ff = db.get_fields(f) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == 'reagent1BaseName':
                for v in tf.values:
                    if isinstance(v, str) and v:
                        act_of[norm(v)] = act
    print(f"classified normal-difficulty souls: {len(act_of)}")

    # ---- signal A: level bands
    bands = defaultdict(list)
    for p, act in act_of.items():
        if 'anysoul' in p:
            continue
        lr = db.get_field_value(p, 'levelRequirement')
        il = db.get_field_value(p, 'itemLevel')
        if lr is not None:
            bands[act].append((float(lr), float(il or 0)))
    print("\nSIGNAL A - levelRequirement per act (normal-difficulty souls):")
    for act in sorted(bands):
        lrs = sorted(x[0] for x in bands[act])
        ils = sorted(x[1] for x in bands[act])
        print(f"  act{act}: n={len(lrs)} lvlReq min={lrs[0]} p25={lrs[len(lrs)//4]} "
              f"med={lrs[len(lrs)//2]} p75={lrs[3*len(lrs)//4]} max={lrs[-1]} | "
              f"itemLevel med={ils[len(ils)//2]} max={ils[-1]}")

    # ---- map soul -> dropping monster(s)
    drop_of = defaultdict(set)
    for n in names:
        nl = norm(n)
        if '\\creature' not in nl:
            continue
        ff = db.get_fields(n) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == 'lootFinger2Item1':
                for v in tf.values:
                    if isinstance(v, str) and v:
                        drop_of[norm(v)].add(nl)
    print(f"\nsouls with a dropping monster: {len(drop_of)}")

    # ---- signal B: monster namespace per act
    print("\nSIGNAL B - dropping-monster namespace per act:")
    ns = defaultdict(Counter)
    for p, act in act_of.items():
        for m in drop_of.get(p, ()):
            parts = m.split('\\')
            ns[act][parts[1] if len(parts) > 1 else '?'] += 1
    for act in sorted(ns):
        print(f"  act{act}: {dict(ns[act])}")

    # ---- signal C: proxy path of the dropping monster
    print("\nSIGNAL C - population-proxy path segment per act:")
    proxy_refs = defaultdict(set)   # monster -> set of proxy paths referencing it
    for n in names:
        nl = norm(n)
        if not nl.startswith('records\\proxies'):
            continue
        ff = db.get_fields(n) or {}
        for k, tf in ff.items():
            for v in tf.values:
                if isinstance(v, str) and '\\creature' in norm(v):
                    proxy_refs[norm(v)].add(nl)
    seg = defaultdict(Counter)
    hit = miss = 0
    for p, act in act_of.items():
        for m in drop_of.get(p, ()):
            px = proxy_refs.get(m)
            if not px:
                miss += 1
                continue
            hit += 1
            for q in px:
                parts = q.split('\\')
                seg[act][parts[2] if len(parts) > 2 else '?'] += 1
    print(f"  monsters with a proxy ref: {hit}, without: {miss}")
    for act in sorted(seg):
        print(f"  act{act}: {seg[act].most_common(12)}")


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
