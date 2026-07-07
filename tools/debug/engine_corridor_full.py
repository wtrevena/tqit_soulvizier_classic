"""GATE G3 - ENGINE-ACCURATE corridor test over ALL generated donors (3D, per-mesh +
region handoff). Same model as engine_corridor.py (intra-mesh 4-adj walk with |dh| <=
walkableClimb=1u; cross-mesh handoff where a cell is tagged with a neighbour's GUID
index AND the neighbour's own mesh has a cell at that world XZ within
findNearestPoly's 2u vertical tolerance), but loads every *.lvl.0b.bin donor so the
BFS can route through the whole cave. Reports per-level reachability from deep
Random09A. Levels whose own floor is genuinely disconnected from the walk chain
(ocean scenery rims, the finale component behind a boss door, etc.) are expected
to read low/zero - the WALK CHAIN levels are the gate:
Random09A (99%+), xPassageTransitionStart, BC_initialpathway,
drxFirstxistion_connection, drxFirstRoom, drxBC2, drxBC_Connector1,
river_extension01, riverextension02, xTempleTransitionHallway all 100%."""
import sys
from collections import deque
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools')); sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from navlib import Mesh, CS, CH
DON = REPO / 'local' / 'editor_normalized'
CLIMB_U = 1.0
SNAP_U = 2.0

g2n, meshes = {}, {}
for p in sorted(DON.glob('*.lvl.0b.bin')):
    nm = p.name[:-len('.lvl.0b.bin')]
    m = Mesh(p, nm)
    meshes[nm] = m
    g2n[m.guids[0]] = nm

cells = {}
for nm, m in meshes.items():
    offx = round(m.origin[0] / CS); offz = round(m.origin[2] / CS)
    cells[nm] = {(gx + offx, gz + offz): (m.origin[1] + h * CH, a)
                 for (gx, gz), (h, a, c) in m.cells.items()}

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

r09 = cells['Random09A']
start_key = max((k for k, v in r09.items() if v[1] == 1), key=lambda k: k[0])
start = ('Random09A', start_key)
seen = {start}; q = deque([start])
while q:
    node = q.popleft()
    for nb in neighbours(*node):
        if nb not in seen:
            seen.add(nb); q.append(nb)

print("ENGINE-ACCURATE reachability from deep Random09A (ALL donors):")
for nm in sorted(cells):
    own = [k for k, v in cells[nm].items() if v[1] == 1]
    r = sum(1 for k in own if (nm, k) in seen)
    pct = 100 * r // max(len(own), 1)
    tag = '' if pct >= 30 else '   <<< not reached'
    print(f"  {nm:36s}: {r:7d}/{len(own):7d} own cells ({pct:3d}%){tag}")
