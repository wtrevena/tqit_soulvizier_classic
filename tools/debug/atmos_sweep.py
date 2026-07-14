"""Full SV-wide atmosphere sweep: for EVERY level present in both SV and build40, compare
per-dbr atmosphere-instance COUNTS (robust to grid shift - no coord matching). Report any
level where build40 has FEWER of an atmosphere dbr than SV (DROPPED) or the level/atmo is
wholly absent. Also lists SV-only levels (not in the merged world at all) that carry atmo.

Catches occult/atmosphere areas beyond the named HV/Delphi/GoM set.
"""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import atmos_rca_lib as A

sv_data, sv_levels, sv_by = A.load_world(A.SV_ARC)
b40_data, b40_levels, b40_by = A.load_world(A.BUILD40_ARC)
print(f'SV levels={len(sv_levels)}  build40 levels={len(b40_levels)}')


def atmo_counter(data, lv):
    _, insts = A.parse_0x05(A.blob_of(data, lv))
    c = Counter()
    for it in insts:
        if A.is_atmo(it['dbr']):
            c[A.leaf(it['dbr'])] += 1
    return c


sv_only_with_atmo = []       # levels in SV not present in merged world
dropped_levels = []          # levels present in both, but build40 has fewer atmo of some dbr
total_sv_atmo_levels = 0
for key, sv_lv in sv_by.items():
    sc = atmo_counter(sv_data, sv_lv)
    if not sc:
        continue
    total_sv_atmo_levels += 1
    b40_lv = b40_by.get(key)
    if b40_lv is None:
        sv_only_with_atmo.append((key, sum(sc.values()), dict(sc)))
        continue
    bc = atmo_counter(b40_data, b40_lv)
    deficits = {}
    for dbr, n in sc.items():
        if bc.get(dbr, 0) < n:
            deficits[dbr] = (n, bc.get(dbr, 0))
    if deficits:
        dropped_levels.append((key, deficits))

print(f'\nSV levels carrying atmosphere: {total_sv_atmo_levels}')

print(f'\n{"="*78}\nSV-ONLY levels (absent from merged world) that carry atmosphere: '
      f'{len(sv_only_with_atmo)}')
for key, tot, c in sorted(sv_only_with_atmo, key=lambda x: -x[1]):
    print(f'  {key}  ({tot} atmo)')
    top = sorted(c.items(), key=lambda x: -x[1])[:8]
    print(f'      {", ".join(f"{k}x{v}" for k, v in top)}')

print(f'\n{"="*78}\nLevels present in BOTH but build40 has FEWER of some atmosphere dbr '
      f'(DROPPED): {len(dropped_levels)}')
for key, deficits in sorted(dropped_levels):
    print(f'  {key}')
    for dbr, (svn, b40n) in sorted(deficits.items()):
        print(f'      {dbr:40s} SV={svn} build40={b40n}  (dropped {svn-b40n})')
