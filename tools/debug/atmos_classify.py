"""Classify every SV atmosphere 0x05 instance PRESENT / DROPPED / MOVED vs a target arc.

For each in-scope level: parse SV atmosphere instances + target (build40 / live) atmosphere
instances, greedily match by (dbr, nearest local coord). PRESENT if a same-dbr target inst
is within TOL. MOVED if a same-dbr target inst exists but all >TOL (report nearest delta).
DROPPED if no same-dbr target inst at all (or all consumed). Also flags target-only atmo
(ADDED). Prints a per-level table + machine summary line.

Usage: py atmos_classify.py [target]      target in {build40 (default), live}
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import atmos_rca_lib as A

TOL = 0.6  # world units; injected coords are byte-exact SV, so this is generous

IN_SCOPE = [
    'levels/world/orient/silkroad/hiddenvalley01.lvl',
    'levels/world/orient/silkroad/hiddenvalleyborder04.lvl',
    'levels/world/greece/delphi/delphilowlands02.lvl',
    'levels/world/greece/delphi/delphilowlands03.lvl',
    'levels/world/greece/delphi/delphilowlands04.lvl',
    'levels/world/olympus/gardenofmerchants.lvl',
]


def dist(a, b):
    return ((a['x'] - b['x']) ** 2 + (a['y'] - b['y']) ** 2 + (a['z'] - b['z']) ** 2) ** 0.5


def classify_level(key, sv_by, sv_data, tg_by, tg_data):
    sv_lv = sv_by.get(key)
    tg_lv = tg_by.get(key)
    res = {'key': key, 'present': [], 'moved': [], 'dropped': [], 'added': [],
           'sv_present': bool(sv_lv), 'tg_present': bool(tg_lv)}
    if not sv_lv:
        return res
    sv_ints = A.ints_of(sv_lv)
    sv_corner = (sv_ints[6], sv_ints[7], sv_ints[8]) if sv_ints else None
    _, sv_insts = A.parse_0x05(A.blob_of(sv_data, sv_lv))
    sv_atmo = [it for it in sv_insts if A.is_atmo(it['dbr'])]
    res['sv_corner'] = sv_corner
    res['sv_atmo_n'] = len(sv_atmo)
    if not tg_lv:
        res['dropped'] = sv_atmo
        return res
    tg_ints = A.ints_of(tg_lv)
    tg_corner = (tg_ints[6], tg_ints[7], tg_ints[8]) if tg_ints else None
    res['tg_corner'] = tg_corner
    _, tg_insts = A.parse_0x05(A.blob_of(tg_data, tg_lv))
    tg_atmo = [it for it in tg_insts if A.is_atmo(it['dbr'])]
    res['tg_atmo_n'] = len(tg_atmo)
    # corner check: if corners differ, coords are not directly comparable (grid shift)
    res['corner_match'] = (sv_corner == tg_corner)

    tg_avail = list(tg_atmo)  # consumable pool
    for s in sv_atmo:
        cands = [t for t in tg_avail if t['dbr'] == s['dbr']]
        if not cands:
            res['dropped'].append(s)
            continue
        cands.sort(key=lambda t: dist(s, t))
        best = cands[0]
        d = dist(s, best)
        if d <= TOL:
            tg_avail.remove(best)
            res['present'].append((s, best, d))
        else:
            # same dbr exists but not near -> MOVED (consume nearest)
            tg_avail.remove(best)
            res['moved'].append((s, best, d))
    # anything left in tg_avail that is atmo and not matched = ADDED (target-only)
    res['added'] = tg_avail
    return res


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'build40'
    sv_data, sv_levels, sv_by = A.load_world(A.SV_ARC)
    if target == 'build40':
        tgpath = A.BUILD40_ARC
    elif Path(target).exists():
        tgpath = Path(target)
    else:
        print(f'target not found: {target}'); return
    print(f'# TARGET = {tgpath}')
    tg_data, tg_levels, tg_by = A.load_world(tgpath)

    tot_sv = tot_present = tot_moved = tot_dropped = tot_added = 0
    for key in IN_SCOPE:
        r = classify_level(key, sv_by, sv_data, tg_by, tg_data)
        print(f'\n{"="*78}\n{key}')
        if not r['sv_present']:
            print('  SV: level ABSENT'); continue
        cm = r.get('corner_match')
        print(f"  SV v corner={r.get('sv_corner')} atmo={r['sv_atmo_n']}  |  "
              f"TG corner={r.get('tg_corner')} atmo={r.get('tg_atmo_n')}  corner_match={cm}")
        tot_sv += r['sv_atmo_n']
        tot_present += len(r['present']); tot_moved += len(r['moved'])
        tot_dropped += len(r['dropped']); tot_added += len(r['added'])
        if r['dropped']:
            print(f"  -- DROPPED ({len(r['dropped'])}) --")
            for s in r['dropped']:
                print(f"     {A.leaf(s['dbr']):38s} SV-local({s['x']:.3f},{s['y']:.3f},{s['z']:.3f}) flags={s['flags']}")
        if r['moved']:
            print(f"  -- MOVED ({len(r['moved'])}) --")
            for s, t, d in r['moved']:
                print(f"     {A.leaf(s['dbr']):38s} SV({s['x']:.2f},{s['y']:.2f},{s['z']:.2f}) -> TG({t['x']:.2f},{t['y']:.2f},{t['z']:.2f}) d={d:.2f}")
        if r['added']:
            print(f"  -- ADDED / target-only ({len(r['added'])}) --")
            for t in r['added']:
                print(f"     {A.leaf(t['dbr']):38s} TG-local({t['x']:.2f},{t['y']:.2f},{t['z']:.2f}) flags={t['flags']}")
        print(f"  -- PRESENT: {len(r['present'])} (matched within {TOL}u) --")
    print(f'\n{"#"*78}')
    print(f'# SUMMARY target={target}: sv_atmo={tot_sv} present={tot_present} '
          f'moved={tot_moved} dropped={tot_dropped} added={tot_added}')


if __name__ == '__main__':
    main()
