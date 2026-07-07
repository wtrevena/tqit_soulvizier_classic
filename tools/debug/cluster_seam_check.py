#!/usr/bin/env python3
"""CLUSTER SEAM + REACHABILITY gate (generalized G3/G4) for a MULTI-LEVEL area.

The blood-cave gates seam_delta_check.py / engine_corridor_full.py hardcode the
blood-cave CHAIN. This is the parameterized version: given a set of level basenames
(a cluster), it loads their generated donors and:

  G4 (seams): for every footprint-ABUTTING donor pair, the median |Y(a)-Y(b)| over
       shared world-XZ own-floor cells must be <= --max-seam (default 0.5u, the
       Y-align integer-residual budget). A cross-level seam walks only if both meshes
       meet at ~one height; a constant step > the engine's 1u climb / 2u
       findNearestPoly tolerance freezes the player (the blood-cave root cause).

  G3 (reachability): BFS from the designated ROOT level under the engine's cross-mesh
       model (intra-mesh 4-adjacency |dh|<=1u; cross-mesh handoff where a cell is
       area-tagged with a neighbour's GUID index AND the neighbour's own mesh has a
       cell at that world XZ within 2u vertically). Reports per-level reachability.
       Every level that is footprint-connected to the root component should read high;
       footprint-DISJOINT levels (separate rooms reached by quest teleport, not a grid
       seam) are expected 0 and listed as such (not a failure - the frontier rule).

Usage:
  py tools/debug/cluster_seam_check.py --levels behindthesp,darkforestenter,... --root darkforestenter
  py tools/debug/cluster_seam_check.py --cluster secretplace     # uses gen_bc_navmeshes config
Exit 0 = PASS (all abutting seams within budget), 1 = FAIL. Read-only.
"""
import argparse
import statistics
import struct
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

from navlib import Mesh, CS, CH                                     # noqa: E402

DON = REPO / 'local' / 'editor_normalized'
CLIMB_U = 1.0
SNAP_U = 2.0


def donor_path(stem):
    stem_l = stem.lower().replace('.lvl', '')
    for p in DON.glob('*.0b.bin'):
        base = p.name[:-len('.0b.bin')]
        base = base[:-4] if base.lower().endswith('.lvl') else base
        if base.lower() == stem_l:
            return p
    return None


def cluster_levels(name):
    """Resolve a cluster name -> its member basenames via the generator config +
    the SV map (so this stays in sync with gen_bc_navmeshes)."""
    import gen_bc_navmeshes as G
    from arc_patcher import ArcArchive
    from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
    cfg = G.CLUSTERS[name]
    arc = ArcArchive.from_file(G.UPSTREAM_SV_ARC)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    lvls = parse_level_index(data, sec[SEC_LEVELS])
    out = []
    for lv in lvls:
        k = lv['fname'].replace('\\', '/').lower()
        if cfg.matches(k):
            out.append(k.split('/')[-1][:-4] if k.endswith('.lvl') else k.split('/')[-1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--levels', help='comma-separated level basenames')
    ap.add_argument('--cluster', help='cluster name from gen_bc_navmeshes.CLUSTERS')
    ap.add_argument('--root', help='root level basename for reachability BFS '
                                   '(default: first level)')
    ap.add_argument('--max-seam', type=float, default=0.5)
    args = ap.parse_args()

    if args.cluster:
        levels = cluster_levels(args.cluster)
    elif args.levels:
        levels = [s.strip() for s in args.levels.split(',') if s.strip()]
    else:
        print('FAIL: pass --levels or --cluster')
        return 1
    print(f'CLUSTER SEAM + REACHABILITY: {len(levels)} levels')

    # load donors. Levels with NO donor (ocean-scenery / no-0x0a stub levels) are
    # skipped - they carry no navmesh and no seams, so they are out of scope for a
    # seam/reachability gate (not a failure). Only the levels that GOT a donor matter.
    meshes = {}
    cells = {}      # name -> {(worldgx,worldgz): (worldY, area)}
    g2n = {}
    no_donor = []
    for nm in levels:
        p = donor_path(nm)
        if p is None:
            no_donor.append(nm)
            continue
        m = Mesh(p, nm)
        meshes[nm] = m
        g2n[m.guids[0]] = nm
        offx = round(m.origin[0] / CS)
        offz = round(m.origin[2] / CS)
        cells[nm] = {(gx + offx, gz + offz): (m.origin[1] + h * CH, a)
                     for (gx, gz), (h, a, c) in m.cells.items()}
    if no_donor:
        print(f'  (skipping {len(no_donor)} stub/no-donor levels: {no_donor})')
    levels = [nm for nm in levels if nm in cells]
    if not levels:
        print('FAIL: no donors found for any cluster level')
        return 1

    # G4 seams: all abutting pairs (>=30 shared world-XZ own-floor cells)
    print('\nG4 SEAMS (median dY over shared own-floor cells):')
    print(f'  {"seam":58s} {"shared":>7s} {"medY":>7s} {"maxY":>7s}')
    worst = 0.0
    n_seams = 0
    for i, a in enumerate(levels):
        for b in levels[i + 1:]:
            # ALL walkable cells keyed by world index (a seam's overlap cells are
            # area-tagged to the NEIGHBOUR on each side, so restricting to own-area
            # would find nothing - the blood-cave seam gate also uses all cells).
            ca = {k: y for k, (y, ar) in cells[a].items()}
            cb = {k: y for k, (y, ar) in cells[b].items()}
            common = set(ca) & set(cb)
            if len(common) < 30:
                continue
            d = sorted(ca[k] - cb[k] for k in common)
            md = statistics.median(d)
            mx = max(abs(d[0]), abs(d[-1]))
            worst = max(worst, abs(md))
            n_seams += 1
            flag = '' if abs(md) <= args.max_seam else '  <<< OVER'
            print(f'  {a + " | " + b:58s} {len(common):7d} {md:+7.2f} {mx:7.2f}{flag}')
    seam_ok = worst <= args.max_seam
    print(f'  worst median |dY| = {worst:.2f}u over {n_seams} abutting seams '
          f'({"PASS" if seam_ok else "FAIL"} <= {args.max_seam}u)')

    # G3 reachability from root (case-insensitive match against loaded level names)
    root = args.root or levels[0]
    if root not in cells:
        _rl = root.lower()
        match = next((nm for nm in cells if nm.lower() == _rl), None)
        if match is None:
            print(f'FAIL: root {root!r} has no donor (loaded: {list(cells)})')
            return 1
        root = match

    def neighbours(nm, key):
        y, area = cells[nm][key]
        ix, iz = key
        for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nk = (ix + dx, iz + dz)
            c = cells[nm].get(nk)
            if c and abs(c[0] - y) <= CLIMB_U:
                yield (nm, nk)
        if area and area > 1:
            gl = meshes[nm].guids
            if area - 1 < len(gl):
                B = g2n.get(gl[area - 1])
                if B and B in cells:
                    c = cells[B].get(key)
                    if c and abs(c[0] - y) <= SNAP_U:
                        yield (B, key)

    rc = cells[root]
    start_key = max((k for k, v in rc.items() if v[1] == 1), key=lambda k: k[0])
    start = (root, start_key)
    seen = {start}
    q = deque([start])
    while q:
        node = q.popleft()
        for nb in neighbours(*node):
            if nb not in seen:
                seen.add(nb)
                q.append(nb)

    print(f'\nG3 REACHABILITY from {root} (own area==1 cells):')
    for nm in levels:
        own = [k for k, v in cells[nm].items() if v[1] == 1]
        r = sum(1 for k in own if (nm, k) in seen)
        pct = 100 * r // max(len(own), 1)
        tag = '' if pct >= 90 else ('   <<< footprint-disjoint (quest-linked room, not a grid seam)'
                                    if pct == 0 else '   <<< partial')
        print(f'  {nm:36s}: {r:8d}/{len(own):8d} ({pct:3d}%){tag}')

    print(f'\nCLUSTER SEAM CHECK: {"PASS" if seam_ok else "FAIL"} '
          f'(seams within {args.max_seam}u; reachability is informational - '
          f'footprint-disjoint rooms are quest-linked by design)')
    return 0 if seam_ok else 1


if __name__ == '__main__':
    sys.exit(main())
