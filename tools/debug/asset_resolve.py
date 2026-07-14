"""Robust asset resolver: index EVERY arc (deployed mod Resources + base game +
XPack/XPack2/3/4) by the LOGICAL path = <arc-basename>\\<entry-name> (TQ's resolution
model: the first path component of a ref names the arc). Then resolve the occult .pfx
+ their referenced .tex and confirm each exists somewhere the shipping game can see it.

READ-ONLY.
"""
import re
import sys
from pathlib import Path
MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arc_patcher import ArcArchive

MOD_RES = MAIN / 'work' / 'SoulvizierClassic' / 'Resources'
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Resources')


def norm(s):
    return s.replace('/', '\\').lower().strip('\\')


def index_arc(path, logical=None):
    """Return dict logical_path -> (arcpath, arc, entry). logical prefix = arc stem
    unless overridden (for xpack subfolders we DON'T prefix the subfolder; TQ refs
    like xpack\\effects\\... resolve via additionalbuilddirs sitting at Resources root
    so the arc stem is still the first component)."""
    arc = ArcArchive.from_file(path)
    stem = (logical if logical is not None else path.stem).lower()
    out = {}
    for e in arc.entries:
        if e.entry_type == 3 and e.name:
            en = norm(e.name)
            # logical path the engine sees = arcstem\entryname (entry names are arc-relative)
            lp = f'{stem}\\{en}' if stem else en
            out.setdefault(lp, (path, arc, e))
            # also index the bare entry name (some refs omit the arc component)
            out.setdefault(en, (path, arc, e))
    return arc, out


def build_index():
    idx = {}
    arcs = []
    for p in sorted(MOD_RES.glob('*.arc')):
        arcs.append(('MOD', p))
    for p in sorted(GAME.glob('*.arc')):
        arcs.append(('BASE', p))
    for sub in ['xpack', 'XPack2', 'XPack3', 'XPack4']:
        d = GAME / sub
        if d.exists():
            for p in sorted(d.glob('*.arc')):
                arcs.append((f'BASE/{sub}', p))
    for tag, p in arcs:
        try:
            _, sub = index_arc(p)
        except Exception as ex:
            print(f'  !! {p}: {ex}')
            continue
        for lp, v in sub.items():
            idx.setdefault(lp, (tag,) + v)
    return idx


PFX_WANT = [
    r'drxeffects\other\occultfog.pfx',
    r'drxeffects\other\pitfx.pfx',
    r'drxeffects\other\pitfx2.pfx',
    r'xpack\effects\particles\environment\bugcloud_small.pfx',
    r'drxeffects\other\occult_aura.pfx',
    r'drxeffects\other\cage_binding.pfx',
    r'drxeffects\drxcreatures\blooddemon\disciple_eye.pfx',
]


def resolve(idx, ref):
    r = norm(ref)
    if r in idx:
        return idx[r], 'full'
    base = r.split('\\')[-1]
    if base in idx:
        return idx[base], 'bare'
    # last-ditch: any logical path ending with the ref's last 2 components
    tail = '\\'.join(r.split('\\')[-2:])
    for k, v in idx.items():
        if k.endswith('\\' + tail) or k == tail:
            return v, 'tail'
    return None, None


def main():
    print('Indexing all arcs (mod + base + xpack)...')
    idx = build_index()
    print(f'  logical paths indexed: {len(idx)}')

    all_tex = set()
    print(f'\n{"="*78}\n# OCCULT .pfx + their .tex refs')
    for want in PFX_WANT:
        hit, how = resolve(idx, want)
        if not hit:
            print(f'  ** PFX MISSING: {want}')
            continue
        tag, arcpath, arc, entry = hit
        data = arc.decompress(entry)
        txt = data.decode('latin-1', 'ignore')
        texs = {norm(t) for t in re.findall(r'[\w\\/][\w\\/ .-]+\.tex', txt, re.I)}
        all_tex |= texs
        print(f'  OK [{tag:10s}|{how:4s}] {want}  ({arcpath.name}, {len(data)}B, {len(texs)} tex)')

    print(f'\n{"="*78}\n# .tex RESOLUTION ({len(all_tex)} distinct)')
    miss = []
    for t in sorted(all_tex):
        hit, how = resolve(idx, t)
        if hit:
            tag, arcpath, arc, entry = hit
            print(f'  OK [{tag:10s}|{how:4s}] {t}  ({arcpath.name})')
        else:
            miss.append(t)
    if miss:
        print(f'\n  ** {len(miss)} .tex UNRESOLVED:')
        for t in miss:
            print(f'     {t}')
    else:
        print('  ALL .tex resolve in mod or base arcs.')

    # Also resolve the bugcloud .pfx explicitly against xpack
    print(f'\n{"="*78}\n# bugcloud_small.pfx explicit probe')
    for cand in ['xpack\\effects\\particles\\environment\\bugcloud_small.pfx',
                 'effects\\particles\\environment\\bugcloud_small.pfx',
                 'bugcloud_small.pfx']:
        hit, how = resolve(idx, cand)
        print(f'  {cand}: {"OK "+hit[1].name+" via "+how if hit else "MISS"}')


if __name__ == '__main__':
    main()
