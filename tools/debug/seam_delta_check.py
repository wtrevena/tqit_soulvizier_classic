"""GATE G4 - cross-mesh Y agreement at the walk-chain seams on the Y-aligned
donors: for each adjacent pair, median |Y(a) - Y(b)| over shared world-XZ own-floor
cells. Design target: <= 0.5u residual (integer-rounded 2.56u offsets), far below
the engine's 1u climb / 2u findNearestPoly tolerance."""
import statistics, sys
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools')); sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from navlib import Mesh, CS, CH
DON = REPO / 'local' / 'editor_normalized'

CHAIN = ['Random09A', 'xPassageTransitionStart', 'BC_initialpathway',
         'drxFirstxistion_connection', 'drxFirstRoom', 'drxBC2', 'drxBC_Connector1',
         'river_extension01', 'riverextension02', 'xTempleTransitionHallway']
cells = {}
for nm in CHAIN:
    m = Mesh(DON / f'{nm}.lvl.0b.bin', nm)
    offx = round(m.origin[0] / CS); offz = round(m.origin[2] / CS)
    cells[nm] = {(gx + offx, gz + offz): m.origin[1] + h * CH
                 for (gx, gz), (h, a, c) in m.cells.items()}

print(f"{'seam':64s} {'shared':>7s} {'median dY':>9s} {'max |dY|':>8s}")
worst = 0.0
for i, a in enumerate(CHAIN):
    for b in CHAIN[i + 1:]:
        common = set(cells[a]) & set(cells[b])
        if len(common) < 30:
            continue
        d = sorted(cells[a][k] - cells[b][k] for k in common)
        md = statistics.median(d)
        mx = max(abs(d[0]), abs(d[-1]))
        worst = max(worst, abs(md))
        print(f"{a + ' | ' + b:64s} {len(common):7d} {md:+9.2f} {mx:8.2f}")
print(f"\nworst median |dY| across chain seams: {worst:.2f}u "
      f"({'PASS <= 0.5u (Y-align residual budget)' if worst <= 0.5 else 'FAIL'})")
