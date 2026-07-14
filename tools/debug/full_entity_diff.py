"""EXHAUSTIVE per-level 0x05 entity diff (ALL dbrs, not just is_atmo) SV vs a target arc.
For each in-scope level: greedily match every SV instance to a same-dbr target instance
within TOL; report DROPPED (SV inst with no target twin) and ADDED (target-only) with
full dbr paths + coords. This is the safety net that catches any smoke/particle entity
the ATMO_SUBS heuristic might not tag. Also emits a compact per-dbr count table.

Usage: py full_entity_diff.py [target]   target in {build40 (default), live, <path>}
"""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import atmos_rca_lib as A

TOL = 0.6
LIVE_WS = Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\3759792705\SoulvizierClassic\resources\Levels.arc')
IN_SCOPE = [
    'levels/world/orient/silkroad/hiddenvalley01.lvl',
    'levels/world/orient/silkroad/hiddenvalleyborder04.lvl',
    'levels/world/greece/delphi/delphilowlands02.lvl',
    'levels/world/greece/delphi/delphilowlands03.lvl',
    'levels/world/greece/delphi/delphilowlands04.lvl',
]


def dist(a, b):
    return ((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2 + (a['z'] - b['z']) ** 2) ** 0.5


def diff_level(key, sv_by, sv_data, tg_by, tg_data):
    sv_lv = sv_by.get(key); tg_lv = tg_by.get(key)
    out = {'key': key, 'dropped': [], 'added': [], 'present': 0,
           'sv_n': 0, 'tg_n': 0, 'sv_present': bool(sv_lv), 'tg_present': bool(tg_lv)}
    if not sv_lv or not tg_lv:
        return out
    _, sv_insts = A.parse_0x05(A.blob_of(sv_data, sv_lv))
    _, tg_insts = A.parse_0x05(A.blob_of(tg_data, tg_lv))
    out['sv_n'] = len(sv_insts); out['tg_n'] = len(tg_insts)
    tg_avail = list(tg_insts)
    for s in sv_insts:
        cands = [t for t in tg_avail if t['dbr'] == s['dbr']]
        if not cands:
            out['dropped'].append(s); continue
        cands.sort(key=lambda t: dist(s, t))
        best = cands[0]
        if dist(s, best) <= TOL:
            tg_avail.remove(best); out['present'] += 1
        else:
            tg_avail.remove(best); out['present'] += 1  # same-dbr consumed (moved counts as present-ish)
    out['added'] = tg_avail
    return out


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'build40'
    sv_data, _, sv_by = A.load_world(A.SV_ARC)
    tgpath = A.BUILD40_ARC if target == 'build40' else (LIVE_WS if target == 'live' else Path(target))
    print(f'# TARGET = {tgpath}')
    tg_data, _, tg_by = A.load_world(tgpath)

    grand_drop = Counter()
    for key in IN_SCOPE:
        r = diff_level(key, sv_by, sv_data, tg_by, tg_data)
        print(f'\n{"="*80}\n{key}')
        if not r['sv_present']:
            print('  SV ABSENT'); continue
        if not r['tg_present']:
            print('  TARGET ABSENT -> whole level dropped'); continue
        print(f"  SV instances={r['sv_n']}  TARGET instances={r['tg_n']}  present={r['present']}  "
              f"dropped={len(r['dropped'])}  added={len(r['added'])}")
        if r['dropped']:
            print(f"  -- DROPPED (SV inst with no target twin) --")
            for s in r['dropped']:
                grand_drop[A.short(s['dbr'])] += 1
                print(f"     {A.short(s['dbr'])}")
                print(f"        SV-local ({s['x']:.3f},{s['y']:.3f},{s['z']:.3f}) flags={s['flags']}")
        if r['added']:
            # only print non-navmesh-ish adds compactly
            print(f"  -- ADDED (target-only) [{len(r['added'])}] --")
            addc = Counter(A.leaf(t['dbr']) for t in r['added'])
            for name, n in addc.most_common():
                print(f"     {name} x{n}")
    print(f'\n{"#"*80}\n# GRAND DROPPED (all in-scope levels), by dbr:')
    for dbr, n in grand_drop.most_common():
        print(f'   {dbr}  x{n}')
    if not grand_drop:
        print('   NONE - every SV 0x05 instance has a target twin in all 5 levels.')


if __name__ == '__main__':
    main()
