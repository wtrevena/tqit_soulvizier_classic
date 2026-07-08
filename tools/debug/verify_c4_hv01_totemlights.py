"""ROUND-2 VET VERIFICATION (independent): confirm the 4 SV-dropped HV01 totem under-lights
(2x 10mlight_dyn_purple + 2x 10mlight_dyn_red) that the round-1 C4 recon omitted.

Enumerates, from the PRISTINE SV 0.98i HiddenValley01 0x05:
  - EVERY 10mlight_dyn_purple + 10mlight_dyn_red instance (coords, flags, rotation)
  - the 2 totem instances (the anchors)
  - distance from each dyn-light to the nearest totem (proves they are totem under-lights)
Then cross-checks the CURRENT CANONICAL merged map (local/Levels_merged.arc):
  - what 10mlight_dyn_purple/red instances exist in HV01 (should be the 2 B1 FOUNTAIN emitters
    at local ~(33.5/38.0,145), NOT the SV totem lights at ~(65,98)/(65,106))
  - confirms the 4 SV totem lights are ABSENT from the shipped HV01.
No writes. Pure read-only proof for the vet finding.
"""
import sys, struct
from pathlib import Path
REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
import recon_doors_hub as R

HV01_KEY = 'levels/world/orient/silkroad/hiddenvalley01.lvl'
CANON = REPO / 'local' / 'Levels_merged.arc'
DYN_PURPLE = b'10mlight_dyn_purple'
DYN_RED = b'10mlight_dyn_red'
TOTEM = b'dress2\\totem'


def dist_xz(a, b):
    return ((a[0] - b[0]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def dist3(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def collect(arc_path, label):
    data, _, levels = R.load_world(arc_path)
    by = {lv['fname'].replace('\\', '/').lower(): lv for lv in levels}
    lv = by.get(HV01_KEY)
    if not lv:
        print(f'# {label}: HV01 NOT FOUND'); return None, None, None
    corner = R.ints_of(lv)[0]
    strings, insts, ver = R.parse_0x05(R.blob_of(data, lv))
    purples, reds, totems = [], [], []
    for it in insts:
        low = it['dbr'].lower()
        rec = {'coord': (it['x'], it['y'], it['z']), 'flags': it['flags'], 'rot': it['rot'],
               'dbr': it['dbr']}
        if DYN_PURPLE in low:
            purples.append(rec)
        elif DYN_RED in low:
            reds.append(rec)
        elif TOTEM in low:
            totems.append(rec)
    print(f'\n# ==== {label} : HiddenValley01 (corner {corner}, v0x{ver:02x}) ====')
    print(f'#   10mlight_dyn_purple: {len(purples)}   10mlight_dyn_red: {len(reds)}   totem: {len(totems)}')
    return purples, reds, totems


def is_identity(rot):
    return all(abs(rot[i] - (1.0 if i in (0, 4, 8) else 0.0)) < 1e-6 for i in range(9))


def dump(recs, kind, totems):
    for r in recs:
        c = r['coord']
        ident = is_identity(r['rot'])
        # nearest totem
        if totems:
            nt = min(totems, key=lambda t: dist_xz(c, t['coord']))
            dt = dist3(c, nt['coord'])
            dtxz = dist_xz(c, nt['coord'])
            near = f' nearest-totem d3={dt:.2f}u dXZ={dtxz:.2f}u @ {tuple(round(v,1) for v in nt["coord"])}'
        else:
            near = ''
        print(f'  {kind}  coord=({c[0]!r}, {c[1]!r}, {c[2]!r}) flags={r["flags"]} '
              f'rot={"identity" if ident else tuple(round(v,4) for v in r["rot"])}{near}')


def main():
    print('=' * 78)
    print('SV 0.98i UPSTREAM (the ground truth for what SHOULD be at HV01)')
    print('=' * 78)
    svp, svr, svt = collect(R.SV_ARC, 'SV-098i')
    print('\n-- SV totems (anchors) --')
    for t in (svt or []):
        c = t['coord']; print(f'  totem coord=({c[0]!r}, {c[1]!r}, {c[2]!r}) flags={t["flags"]}')
    print('\n-- SV 10mlight_dyn_purple --')
    dump(svp or [], '10mlight_dyn_purple', svt or [])
    print('\n-- SV 10mlight_dyn_red --')
    dump(svr or [], '10mlight_dyn_red', svt or [])

    print('\n' + '=' * 78)
    print('CURRENT CANONICAL local/Levels_merged.arc (what is SHIPPED at HV01)')
    print('=' * 78)
    cp, cr, ct = collect(CANON, 'CANON')
    print('\n-- CANON 10mlight_dyn_purple --')
    dump(cp or [], '10mlight_dyn_purple', ct or [])
    print('\n-- CANON 10mlight_dyn_red --')
    dump(cr or [], '10mlight_dyn_red', ct or [])

    # verdict: are the 4 SV totem-lights present in CANON?
    print('\n' + '=' * 78)
    print('VERDICT: are SV\'s 4 totem under-lights present in the shipped HV01?')
    print('=' * 78)
    def present_at(recs, target, tol=0.5):
        for r in recs:
            if dist3(r['coord'], target) <= tol:
                return True
        return False
    missing = 0
    for r in (svp or []):
        tgt = r['coord']
        # only the totem-adjacent SV purples (near a totem, i.e. dXZ small)
        found = present_at(cp or [], tgt)
        tag = 'PRESENT' if found else 'MISSING'
        if not found:
            missing += 1
        print(f'  SV purple @ {tuple(round(v,2) for v in tgt)} -> {tag} in CANON')
    for r in (svr or []):
        tgt = r['coord']
        found = present_at(cr or [], tgt)
        tag = 'PRESENT' if found else 'MISSING'
        if not found:
            missing += 1
        print(f'  SV red    @ {tuple(round(v,2) for v in tgt)} -> {tag} in CANON')
    print(f'\n  => {missing} SV totem-dyn-light(s) MISSING from shipped HV01 (vet claims 4).')


if __name__ == '__main__':
    main()
