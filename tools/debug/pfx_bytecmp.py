"""Byte-compare the occult .pfx across three DRXeffects.arc copies:
 (1) our DEPLOYED build40   work/SoulvizierClassic/Resources/DRXeffects.arc
 (2) our LIVE Workshop      steamapps/workshop/.../3759792705/.../DRXeffects.arc
 (3) SVAERA reference       steamapps/workshop/.../2076433374/.../DRXeffects.arc  (known-good DRX)

If DEPLOYED == SVAERA for each occult .pfx, the particle asset is the genuine DRX one
(not a nerfed same-name stub). If DEPLOYED == LIVE, what we analyse IS what subscribers see.
READ-ONLY.
"""
import hashlib
import sys
from pathlib import Path
MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arc_patcher import ArcArchive

COPIES = {
    'DEPLOYED': MAIN / 'work' / 'SoulvizierClassic' / 'Resources' / 'DRXeffects.arc',
    'LIVE_WS': Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\3759792705\SoulvizierClassic\resources\DRXeffects.arc'),
    'SVAERA': Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\Resources\DRXeffects.arc'),
}
PFX = ['other\\occultfog.pfx', 'other\\pitfx.pfx', 'other\\pitfx2.pfx',
       'other\\occult_aura.pfx', 'other\\cage_binding.pfx',
       'drxcreatures\\blooddemon\\disciple_eye.pfx']


def load(path):
    if not path.exists():
        return None
    arc = ArcArchive.from_file(path)
    idx = {}
    for e in arc.entries:
        if e.entry_type == 3 and e.name:
            idx[e.name.replace('/', '\\').lower()] = (arc, e)
    return idx


idxs = {k: load(p) for k, p in COPIES.items()}
for k, p in COPIES.items():
    print(f'{k:9s} {"OK" if idxs[k] else "ABSENT":6s} {p}')

print(f'\n{"pfx":34s} {"DEPLOYED":>12s} {"LIVE_WS":>12s} {"SVAERA":>12s}   verdict')
for pfx in PFX:
    row = {}
    for k, idx in idxs.items():
        if idx is None:
            row[k] = None; continue
        hit = idx.get(pfx.lower())
        if not hit:
            row[k] = ('MISSING', 0); continue
        arc, e = hit
        data = arc.decompress(e)
        row[k] = (hashlib.md5(data).hexdigest()[:10], len(data))
    dep = row.get('DEPLOYED'); live = row.get('LIVE_WS'); sv = row.get('SVAERA')
    def cell(v):
        return f'{v[0]}/{v[1]}' if v else 'n/a'
    vd = []
    if dep and sv and dep[0] == sv[0]:
        vd.append('DEP==SVAERA')
    elif dep and sv:
        vd.append('DEP!=SVAERA')
    if dep and live and dep[0] == live[0]:
        vd.append('DEP==LIVE')
    elif dep and live:
        vd.append('DEP!=LIVE')
    print(f'{pfx:34s} {cell(dep):>18s} {cell(live):>18s} {cell(sv):>18s}   {" ".join(vd)}')
