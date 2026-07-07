#!/usr/bin/env python3
"""R2 evidence - post-carve corridor-width report for the walk-chain donors.

The obstacle carve (gen_rec02, erode-then-carve) can narrow a corridor where a
rock polygon hugs a walkable channel edge. engine_corridor_full.py is the binding
gate (it proves the chain stays traversable through real region-handoff cells);
this reporter quantifies HOW tight the surviving corridors are, per donor, so a
corridor merely NARROWED (not severed) to sub-agent width is visible.

Per chain donor it prints the main connected component's local-width distribution
(min of the x-run and z-run through each own-area cell), reporting the 1st
percentile and minimum in world units. The RCA flagged BC_initialpathway's p1 at
2.0u -> 0.6u under carve-THEN-erode; the shipped pipeline uses erode-THEN-carve
(gentler). walkableRadius = 0.4u, so the agent needs > 0.8u clear width; p1 below
that is a doorway-pinch flag to investigate (genuine SV overlap = faithful; carve
artifact = fix).

Usage: py tools/debug/corridor_width_check.py
Read-only. Always exits 0 (informational); engine_corridor_full.py is the gate.
"""
import sys
from collections import deque
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from navlib import Mesh, CS                                          # noqa: E402

DON = Path(REPO / 'local' / 'editor_normalized')
CHAIN = ['Random09A', 'xPassageTransitionStart', 'BC_initialpathway',
         'drxFirstxistion_connection', 'drxFirstRoom', 'drxBC2', 'drxBC_Connector1',
         'river_extension01', 'riverextension02', 'xTempleTransitionHallway']
WALKABLE_RADIUS_U = 0.4


def main_component(cells):
    """Largest 4-adjacency component of a set of (gx,gz) cells."""
    seen = set()
    best = []
    for s in cells:
        if s in seen:
            continue
        q = deque([s])
        seen.add(s)
        comp = []
        while q:
            c = q.popleft()
            comp.append(c)
            for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (c[0] + dx, c[1] + dz)
                if n in cells and n not in seen:
                    seen.add(n)
                    q.append(n)
        if len(comp) > len(best):
            best = comp
    return set(best)


def widths(main):
    out = []
    for (x, z) in main:
        wx = 1
        i = x - 1
        while (i, z) in main:
            wx += 1
            i -= 1
        i = x + 1
        while (i, z) in main:
            wx += 1
            i += 1
        wz = 1
        j = z - 1
        while (x, j) in main:
            wz += 1
            j -= 1
        j = z + 1
        while (x, j) in main:
            wz += 1
            j += 1
        out.append(min(wx, wz))
    out.sort()
    return out


def main():
    print('=== R2 post-carve corridor widths (main component, own-area cells) ===')
    print(f'  walkableRadius={WALKABLE_RADIUS_U}u -> agent needs > {2*WALKABLE_RADIUS_U}u clear\n')
    print(f'  {"donor":36s} {"own":>8s} {"main":>8s} {"p1":>7s} {"min":>7s}  flag')
    print('  ' + '-' * 74)
    for nm in CHAIN:
        p = DON / f'{nm}.lvl.0b.bin'
        if not p.exists():
            print(f'  {nm:36s}  (donor missing)')
            continue
        m = Mesh(p, nm)
        own = {k for k, v in m.cells.items() if v[1] == 1}
        if not own:
            print(f'  {nm:36s} {0:>8d}  (no own-area cells)')
            continue
        main = main_component(own)
        w = widths(main)
        # 1st-percentile index (same convention as the RCA pinch metric, which
        # measured BC_initialpathway p1 = 2.0u pre-carve).
        p1 = w[min(len(w) - 1, int(0.01 * len(w)))] if w else 0
        mn = w[0] if w else 0
        flag = '' if p1 * CS > 2 * WALKABLE_RADIUS_U else '  <<< narrow - check vs SV'
        print(f'  {nm:36s} {len(own):>8d} {len(main):>8d} '
              f'{p1*CS:>6.1f}u {mn*CS:>6.1f}u{flag}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
