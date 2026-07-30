r"""probe_mesh_fx_census - R-102: which creature meshes carry EMBEDDED FX (the green)?

R-102's fourth/fifth amendments proved by elimination that the Enslaver's green is
baked into `Creatures\Monster\Skeleton\RevenantPoison.msh` - the .msh file itself
ends with a `CreateEntity { attach=...; entity=...RevenantPoison_FX.dbr }` block
that pulls in `Effects\MonsterFX\Buffs\RevenantPoison.pfx` (green colour keys).
`baseTexture` on the .dbr only replaces the primary skin, so no .dbr edit can
reach it.

This probe answers the ONE question the fix needs: for every candidate mesh,
does the .msh binary reference an FX entity/particle at all?  A mesh with ZERO
FX references cannot emit the green.

Usage:
    py tools/debug/probe_mesh_fx_census.py                 # skeleton + stalker families
    py tools/debug/probe_mesh_fx_census.py --dir Creatures\Monster\Skeleton
    py tools/debug/probe_mesh_fx_census.py --mesh <exact msh path>
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arc_patcher import ArcArchive  # noqa: E402

GAME = Path(os.environ.get(
    'SVC_TQAE_DIR',
    r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition'))

ARCS = [
    GAME / 'Resources' / 'Creatures.arc',
    GAME / 'Resources' / 'xpack' / 'Creatures.arc',
    GAME / 'Resources' / 'XPack2' / 'Creatures.arc',
    GAME / 'Resources' / 'XPack3' / 'Creatures.arc',
    GAME / 'Resources' / 'XPack4' / 'Creatures.arc',
]

# every token that can pull an effect into a mesh at load time
FX_TOKENS = (b'CreateEntity', b'.pfx', b'_FX', b'Effects\\', b'Effects/')

_PRINTABLE = re.compile(rb'[ -~]{4,}')


def _key(dbr_path):
    r"""A .dbr mesh reference -> the archive ENTRY name.

    The FIRST path component of a TQ art reference is the ARCHIVE name, not a
    directory: `Creatures\Monster\Skeleton\RevenantPoison.msh` lives inside
    `Creatures.arc` as the entry `monster\skeleton\revenantpoison.msh`. Getting
    this wrong is why a naive prefix match returns zero rows.
    """
    p = str(dbr_path).lower().replace('/', '\\').lstrip('\\')
    for arcname in ('creatures\\', 'drx\\', 'xpack\\'):
        if p.startswith(arcname):
            p = p[len(arcname):]
            break
    return p


def _load():
    """{lower-name: (arcpath, ArcArchive, entryname)} for every .msh in the arcs."""
    idx = {}
    arcs = []
    for p in ARCS:
        if not p.exists():
            continue
        a = ArcArchive.from_file(p)
        arcs.append((p, a))
        for e in a.entries:
            if e.entry_type == 3 and e.name.lower().endswith('.msh'):
                idx.setdefault(e.name.lower().replace('/', '\\'), (p, a, e.name))
    return idx, arcs


def _fx_of(data):
    """Return (has_fx, [interesting strings]) for one .msh blob."""
    hits = []
    for s in _PRINTABLE.findall(data):
        t = s.decode('ascii', 'replace')
        tl = t.lower()
        if ('.pfx' in tl or '_fx' in tl or 'createentity' in tl
                or tl.startswith('effects\\') or tl.startswith('effects/')
                or '\\effects\\' in tl):
            hits.append(t)
    has = any(tok.lower() in data.lower() for tok in
              (b'createentity', b'.pfx')) or bool(
                  [h for h in hits if h.lower().endswith('.dbr')])
    return has, sorted(set(hits))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', action='append', default=None,
                    help=r'mesh directory prefix, e.g. Creatures\Monster\Skeleton')
    ap.add_argument('--mesh', action='append', default=None)
    ap.add_argument('--quiet-strings', action='store_true')
    args = ap.parse_args()

    idx, _arcs = _load()
    if not idx:
        raise SystemExit('no Creatures .arc found under %s' % GAME)
    print('indexed %d .msh entries across %d arcs' % (len(idx), len(ARCS)))

    if args.mesh:
        want = [_key(m) for m in args.mesh]
    else:
        dirs = args.dir or [r'Creatures\Monster\Skeleton',
                            r'Creatures\Monster\ShadowStalker',
                            r'Creatures\Monster\NightStalker']
        dl = [_key(d).rstrip('\\') + '\\' for d in dirs]
        want = sorted(n for n in idx if any(n.startswith(d) for d in dl))

    clean, dirty, missing = [], [], []
    for name in want:
        hit = idx.get(name)
        if not hit:
            missing.append(name)
            continue
        p, a, real = hit
        data = a.get_file(real) or b''
        has, strings = _fx_of(data)
        tag = 'FX' if has else '  '
        print('\n[%s] %-58s %8d B   (%s)' % (tag, real, len(data), p.name))
        if strings and not args.quiet_strings:
            for s in strings[:12]:
                print('        %s' % s)
        (dirty if has else clean).append(real)

    print('\n=== SUMMARY ===')
    print('FX-FREE (%d):' % len(clean))
    for c in clean:
        print('   CLEAN  %s' % c)
    print('CARRIES EMBEDDED FX (%d):' % len(dirty))
    for d in dirty:
        print('   FX     %s' % d)
    if missing:
        print('NOT FOUND (%d): %s' % (len(missing), missing))
    return 0


if __name__ == '__main__':
    sys.exit(main())
