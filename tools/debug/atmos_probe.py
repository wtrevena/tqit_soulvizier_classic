"""Validation probe: parse delphilowlands02 0x05 in SV vs build40, list atmosphere insts."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import atmos_rca_lib as A

KEY = 'levels/world/greece/delphi/delphilowlands02.lvl'

sv_data, sv_levels, sv_by = A.load_world(A.SV_ARC)
b40_data, b40_levels, b40_by = A.load_world(A.BUILD40_ARC)

for label, data, by in [('SV', sv_data, sv_by), ('BUILD40', b40_data, b40_by)]:
    lv = by.get(KEY)
    if not lv:
        print(f'{label}: {KEY} NOT PRESENT')
        continue
    blob = A.blob_of(data, lv)
    ver = A.blob_version(blob)
    ints = A.ints_of(lv)
    corner = (ints[6], ints[7], ints[8]) if ints else None
    strings, insts = A.parse_0x05(blob)
    atmo = [it for it in insts if A.is_atmo(it['dbr'])]
    print(f'\n==== {label} {KEY} v0x{ver:02x} corner={corner} '
          f'total_inst={len(insts)} atmo={len(atmo)} ====')
    for it in atmo:
        print(f"  [{it['i']:4d}] {A.leaf(it['dbr']):40s} "
              f"({it['x']:.2f},{it['y']:.2f},{it['z']:.2f}) flags={it['flags']}")
