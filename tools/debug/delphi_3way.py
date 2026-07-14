"""3-way dump of the Delphi occult entities (fog/pit/spawner/lildude/vitstaff/cage) in
delphilowlands02/03/04 across SV(0.98i) / SVAERA base / build40(work). Resolves whether
the occult sprites are SVAERA-native, SV-merge-kept, or injected - and confirms the
classify 'PRESENT' verdict against the raw instances.
"""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import atmos_rca_lib as A

LEVELS = [
    'levels/world/greece/delphi/delphilowlands02.lvl',
    'levels/world/greece/delphi/delphilowlands03.lvl',
    'levels/world/greece/delphi/delphilowlands04.lvl',
]
# occult-scene markers (leaf substrings)
MARK = ['fog_occult', 'pit_fx', 'pitspawner', 'lildude', 'vitstaff', 'cage',
        'occultistaura', 'bugcloud', 'anouranfirepit', 'soundobject', 'blooddemon',
        'occulttent', 'merchant_delphi']

srcs = [('SV', A.SV_ARC), ('SVAERA', A.SVAERA_ARC), ('BUILD40', A.BUILD40_ARC)]
worlds = {}
for name, path in srcs:
    if not Path(path).exists():
        print(f'{name}: MISSING {path}'); continue
    worlds[name] = A.load_world(path)


def occ_counter(data, by, key):
    lv = by.get(key)
    if not lv:
        return None
    _, insts = A.parse_0x05(A.blob_of(data, lv))
    c = Counter()
    for it in insts:
        leaf = A.leaf(it['dbr'])
        if any(m in leaf for m in MARK):
            c[leaf] += 1
    return c


for key in LEVELS:
    print(f'\n{"="*80}\n{key}')
    cols = {}
    allnames = set()
    for name in worlds:
        data, _, by = worlds[name]
        c = occ_counter(data, by, key)
        cols[name] = c
        if c is not None:
            allnames |= set(c.keys())
    if all(c is None for c in cols.values()):
        print('  absent everywhere'); continue
    hdr = f'  {"entity":38s}' + ''.join(f'{n:>9s}' for n in worlds)
    print(hdr)
    for nm in sorted(allnames):
        row = f'  {nm:38s}'
        for name in worlds:
            c = cols[name]
            row += f'{(c.get(nm,0) if c is not None else "-"):>9}'
        print(row)
    # totals
    row = f'  {"TOTAL occult":38s}'
    for name in worlds:
        c = cols[name]
        row += f'{(sum(c.values()) if c is not None else "-"):>9}'
    print(row)
