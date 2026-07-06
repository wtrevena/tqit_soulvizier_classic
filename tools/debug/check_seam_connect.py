"""Pre-walk-test sanity: for the key seams, are the OWN cells and the
NEIGHBOUR-tagged strip cells in the SAME walkable connected component (engine
model: 4-adj, |dh|<=CLIMB=5)? If they're separate components, a height cliff at
the seam would wall despite correct cross-tags."""
import sys
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools')); sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from navlib import Mesh

DON = REPO / 'local' / 'editor_normalized'
PAIRS = [('Random09A.lvl', 'xPassageTransitionStart.lvl'),
         ('xPassageTransitionStart.lvl', 'BC_initialpathway.lvl'),
         ('BC_initialpathway.lvl', 'drxFirstxistion_Connection.lvl'),
         ('drxFirstxistion_Connection.lvl', 'drxFirstRoom.lvl')]

def own_and_nbr_component(mesh, nbr_own_guid):
    """Does the biggest component contain BOTH own-tagged (area 1) and
    neighbour-tagged (area == nbr index+1) cells?"""
    if nbr_own_guid not in mesh.guids:
        return None
    nbr_area = mesh.guids.index(nbr_own_guid) + 1
    comps = mesh.components()
    for ci, comp in enumerate(comps):
        areas = set(mesh.cells[c][1] for c in comp)
        if 1 in areas and nbr_area in areas:
            return (ci, len(comp), len(comps))
    # not together: report where each lives
    return (None, None, len(comps))

meshes = {}
for a, b in PAIRS:
    for n in (a, b):
        if n not in meshes:
            p = DON / f'{n}.0b.bin'
            meshes[n] = Mesh(p, n) if p.exists() else None

print("Seam connectivity (own <-> neighbour strip in one walkable component?):")
all_ok = True
for a, b in PAIRS:
    ma, mb = meshes[a], meshes[b]
    if not ma or not mb:
        print(f"  {a}|{b}: donor missing"); all_ok = False; continue
    gb = mb.guids[0]  # b's own guid = the neighbour entry inside a's list
    ga = ma.guids[0]
    ra = own_and_nbr_component(ma, gb)
    rb = own_and_nbr_component(mb, ga)
    oka = ra and ra[0] is not None
    okb = rb and rb[0] is not None
    all_ok = all_ok and oka and okb
    print(f"  {a[:26]:26s} own+strip together: {'YES comp#%d (%d cells, %d comps)'%ra if oka else 'NO ('+str(ra)+')'}")
    print(f"  {b[:26]:26s} own+strip together: {'YES comp#%d (%d cells, %d comps)'%rb if okb else 'NO ('+str(rb)+')'}")
print("\nRESULT:", "ALL SEAMS WALK-CONNECTED (no cliff)" if all_ok else "SOME SEAM HAS A DISCONNECT - would still wall")
