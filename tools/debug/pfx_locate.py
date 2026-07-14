"""Locate the occult FX .pfx particle files in the DEPLOYED Resources arcs, confirm
present + non-empty, extract each, and scan its text for referenced .tex/.pfx assets.

A present+correct EffectEntity dbr renders NOTHING if its effectFile .pfx is missing
from the shipped arcs (or is empty/points at missing textures). This is the last data
lever after (entities present) + (FX records byte-identical to SV) both came back clean.

READ-ONLY. Reads arcs from the MAIN repo by absolute path.
"""
import re
import sys
from pathlib import Path
MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arc_patcher import ArcArchive

RES = MAIN / 'work' / 'SoulvizierClassic' / 'Resources'
GAME_RES = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Resources')

# effectFile .pfx referenced by the occult FX records (from fx_diff.py), lowercased
PFX_WANT = [
    r'drxeffects\other\occultfog.pfx',
    r'drxeffects\other\pitfx.pfx',
    r'drxeffects\other\pitfx2.pfx',
    r'xpack\effects\particles\environment\bugcloud_small.pfx',
    r'drxeffects\other\occult_aura.pfx',
    r'drxeffects\other\cage_binding.pfx',
    r'drxeffects\drxcreatures\blooddemon\disciple_eye.pfx',
]


def norm(s):
    return s.replace('/', '\\').lower().lstrip('\\')


def load_arc_index(path):
    """Return {normalized_entry_name: (arc, entry)} for entry_type==3 files."""
    arc = ArcArchive.from_file(path)
    idx = {}
    for e in arc.entries:
        if e.entry_type == 3 and e.name:
            idx[norm(e.name)] = (arc, e)
    return arc, idx


def main():
    # Build a combined index across every deployed Resources arc + the base game arcs.
    mod_arcs = sorted(RES.glob('*.arc'))
    combined = {}          # norm name -> (arcpath, arc, entry)
    per_arc_pfx = {}       # arcpath.name -> count of .pfx entries
    for p in mod_arcs:
        try:
            arc, idx = load_arc_index(p)
        except Exception as ex:
            print(f'  !! failed to read {p.name}: {ex}')
            continue
        npfx = sum(1 for k in idx if k.endswith('.pfx'))
        per_arc_pfx[p.name] = npfx
        for k, (a, e) in idx.items():
            combined.setdefault(k, (p, a, e))

    # base-game arcs (for the base bugcloud_small.pfx which is XPack, not mod-owned)
    base_combined = {}
    if GAME_RES.exists():
        for p in sorted(GAME_RES.glob('*.arc')):
            try:
                _, idx = load_arc_index(p)
            except Exception:
                continue
            for k, (a, e) in idx.items():
                base_combined.setdefault(k, (p, a, e))
        # xpack subfolder
        xp = GAME_RES / 'XPack'
        if xp.exists():
            for p in sorted(xp.glob('*.arc')):
                try:
                    _, idx = load_arc_index(p)
                except Exception:
                    continue
                for k, (a, e) in idx.items():
                    base_combined.setdefault('xpack\\' + k, (p, a, e))
        xp2 = GAME_RES / 'XPack2'
        if xp2.exists():
            for p in sorted(xp2.glob('*.arc')):
                try:
                    _, idx = load_arc_index(p)
                except Exception:
                    continue
                for k, (a, e) in idx.items():
                    base_combined.setdefault('xpack2\\' + k, (p, a, e))

    print(f'# deployed Resources arcs scanned: {len(mod_arcs)}')
    print('# .pfx entry counts per mod arc:')
    for name, n in sorted(per_arc_pfx.items(), key=lambda x: -x[1]):
        if n:
            print(f'   {name:28s} {n} .pfx')
    print(f'# total distinct entries across mod arcs: {len(combined)}')
    print(f'# base-game entries indexed: {len(base_combined)}')

    print(f'\n{"="*78}\n# OCCULT .pfx PRESENCE CHECK (mod arcs, then base fallback)')
    tex_refs = set()
    child_pfx = set()
    for want in PFX_WANT:
        w = norm(want)
        # try direct, and try arc-relative (strip leading arc-name component)
        hit = combined.get(w)
        note = 'mod'
        if hit is None:
            # some arcs store entries WITHOUT the leading arc-name component
            parts = w.split('\\', 1)
            if len(parts) == 2:
                hit = combined.get(parts[1])
                if hit:
                    note = f'mod(rel:{parts[0]})'
        if hit is None:
            hit = base_combined.get(w)
            note = 'BASE' if hit else note
        if hit is None:
            print(f'  ** MISSING **  {want}')
            continue
        arcpath, arc, entry = hit
        try:
            data = arc.decompress(entry)
        except Exception as ex:
            print(f'  ?? {want} present in {arcpath.name} but decompress failed: {ex}')
            continue
        n = len(data)
        # scan the .pfx bytes for asset refs (.tex / .pfx / .msh) as ascii-ish
        txt = data.decode('latin-1', 'ignore')
        texs = set(re.findall(r'[\w\\/][\w\\/ .-]+\.tex', txt, re.I))
        pfxs = set(re.findall(r'[\w\\/][\w\\/ .-]+\.pfx', txt, re.I))
        tex_refs |= {norm(t) for t in texs}
        child_pfx |= {norm(t) for t in pfxs}
        print(f'  OK [{note:14s}] {want}')
        print(f'        arc={arcpath.name} size={n}B  tex_refs={len(texs)} child_pfx={len(pfxs)}')
        for t in sorted(texs)[:12]:
            print(f'           tex: {t}')
        for t in sorted(pfxs):
            print(f'           pfx: {t}')

    # Check referenced textures exist somewhere (mod OR base)
    print(f'\n{"="*78}\n# TEXTURE RESOLUTION for referenced .tex ({len(tex_refs)} distinct)')
    missing = []
    for t in sorted(tex_refs):
        found = t in combined
        loc = 'mod'
        if not found:
            parts = t.split('\\', 1)
            if len(parts) == 2 and parts[1] in combined:
                found = True; loc = f'mod(rel)'
        if not found and (t in base_combined or ('xpack\\' + t) in base_combined):
            found = True; loc = 'BASE'
        if not found:
            missing.append(t)
        else:
            print(f'  OK   [{loc:9s}] {t}')
    if missing:
        print(f'\n  ** {len(missing)} referenced textures NOT FOUND in mod or base arcs:')
        for t in missing:
            print(f'     MISSING TEX: {t}')
    else:
        print('  ALL referenced textures resolve.')


if __name__ == '__main__':
    main()
