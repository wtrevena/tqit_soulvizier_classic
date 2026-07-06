"""Cross-tag SEAM GATE (Track 1, docs/CROSS_LEVEL_STITCH_RE.md).

The engine walks across a level seam only as a SINGLE-mesh path: level A's navmesh
must rasterize a strip of cells PAST the shared boundary into B's territory and TAG
them with B's GUID-list index (area id == 1-based index into the mesh GUID list =
the owning level). The neighbour mirrors it. This gate proves that happened.

For every cluster pair (A,B) that is a real WALK seam - footprints share an edge
with a perpendicular band AND both meshes have walkable floor within 4u of the
shared plane on their own side - REQUIRE: A carries >= MIN_STRIP walkable cells
tagged as B beyond the plane, and B carries >= MIN_STRIP tagged as A. All 11 prior
builds fail this (zero cross-tagged cells).

Reads the generated donors in local/editor_normalized (byte-identical to the
deployed map per verify_merged_bc_navmeshes.py). Exit 0 = pass, 1 = a walk seam is
not stitched, 2 = setup error.

Usage: py tools/verify_cross_tags.py
"""
import sys
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections
from svaera_plus_portals import GRID_SHIFT
from navlib import Mesh, CS

DON = Path(__import__('os').environ.get('SVC_DONOR_DIR', str(REPO / 'local/editor_normalized')))
UPSTREAM = REPO / 'upstream/soulvizier_098i/Resources/Levels.arc'
MIN_STRIP = 50        # cells a neighbour must own past the plane (vanilla ~6k-13k)
EDGE_NEAR = 4.0       # world units: "floor at the seam" search depth
MIN_EDGE = 20         # own cells needed at the seam to call it a walk seam
BAND_MIN = 8.0        # min perpendicular overlap to count as a shared EDGE (not corner)


def grid_shift_for(fname):
    key = fname.replace('\\', '/').lower()
    for pat, s in GRID_SHIFT.items():
        if pat in key:
            return s
    return (0, 0, 0)


def load_cluster():
    """Return {basename: dict(merged_box, own_guid_hex, mesh)} for cluster donors."""
    arc = ArcArchive.from_file(UPSTREAM)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    # donor files are '<OriginalCaseBasename>.lvl.0b.bin'; index them case-folded
    donors = {p.name.lower(): p for p in DON.glob('*.0b.bin')}
    out = {}
    for lv in parse_level_index(data, sec[SEC_LEVELS]):
        fn = lv['fname'].replace('\\', '/').lower()
        leaf = fn.split('/')[-1]                       # e.g. random09a.lvl
        base = leaf.replace('.lvl', '')
        if 'xbloodcave' not in fn and base != 'random09a':
            continue
        donor = donors.get(f'{leaf}.0b.bin')
        if donor is None or not donor.is_file():
            continue                       # ocean scenery / no navmesh
        ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
        sx, _sy, sz = grid_shift_for(fn)
        # merged footprint box (LEVELS-index corner + box dims*2, shifted)
        mx0, mz0 = ints[6] + sx, ints[8] + sz
        mbox = (mx0, mz0, mx0 + ints[3] * 2, mz0 + ints[5] * 2)
        m = Mesh(donor, base)
        out[base] = dict(box=mbox, mesh=m,
                         own=(m.guids[0] if m.guids else None))
    return out


def shared_edge(a, b):
    """If boxes a,b share an edge with a real band, return (axis, plane, lo, hi)
    where axis 'x' means the seam plane is x=plane and the band is on z."""
    ax0, az0, ax1, az1 = a
    bx0, bz0, bx1, bz1 = b
    # x-edge: a.x1 == b.x0 or b.x1 == a.x0, z overlap
    zlo, zhi = max(az0, bz0), min(az1, bz1)
    if zhi - zlo >= BAND_MIN:
        if ax1 == bx0:
            return ('x', ax1, zlo, zhi)
        if bx1 == ax0:
            return ('x', ax0, zlo, zhi)
    xlo, xhi = max(ax0, bx0), min(ax1, bx1)
    if xhi - xlo >= BAND_MIN:
        if az1 == bz0:
            return ('z', az1, xlo, xhi)
        if bz1 == az0:
            return ('z', az0, xlo, xhi)
    return None


def side_counts(mesh, axis, plane, lo, hi, other_idx):
    """Return (own_at_edge, tagged_other_past_plane_low, ..._high). We count on
    BOTH sides so the caller (which knows which side is 'past') can pick."""
    own_edge_lowside = own_edge_highside = 0
    tag_past_low = tag_past_high = 0
    for (gx, gz), (h, a, c) in mesh.cells.items():
        along = mesh.wx(gx) if axis == 'x' else mesh.wz(gz)
        perp = mesh.wz(gz) if axis == 'x' else mesh.wx(gx)
        if not (lo - 0.5 <= perp <= hi + 0.5):
            continue
        d = along - plane                     # >0 = high side, <0 = low side
        if a == other_idx + 1:                # tagged as the neighbour
            if d > 0:
                tag_past_high += 1
            elif d < 0:
                tag_past_low += 1
        if -EDGE_NEAR <= d < 0:
            own_edge_lowside += 1
        elif 0 <= d <= EDGE_NEAR:
            own_edge_highside += 1
    return own_edge_lowside, own_edge_highside, tag_past_low, tag_past_high


def main():
    cl = load_cluster()
    if len(cl) < 5:
        print(f'SETUP ERROR: only {len(cl)} cluster donors found in {DON}')
        return 2
    names = sorted(cl)
    print(f'Cross-tag seam gate: {len(cl)} cluster donors')
    checked = passed = 0
    failures = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            A, B = cl[names[i]], cl[names[j]]
            se = shared_edge(A['box'], B['box'])
            if not se:
                continue
            axis, plane, lo, hi = se
            # index of each other's own GUID in the other's guid list
            bIdxInA = A['mesh'].guids.index(B['own']) if B['own'] in A['mesh'].guids else None
            aIdxInB = B['mesh'].guids.index(A['own']) if A['own'] in B['mesh'].guids else None
            # A on low or high side of the plane?
            aLow = (A['box'][0] if axis == 'x' else A['box'][1]) < plane
            # measure
            if bIdxInA is None or aIdxInB is None:
                # not mutually registered - only a problem if it's a walk seam
                a_lo, a_hi, _, _ = side_counts(A['mesh'], axis, plane, lo, hi, 0)
                b_lo, b_hi, _, _ = side_counts(B['mesh'], axis, plane, lo, hi, 0)
                aEdge = a_lo if aLow else a_hi
                bEdge = b_hi if aLow else b_lo
                if aEdge >= MIN_EDGE and bEdge >= MIN_EDGE:
                    failures.append(f'{names[i]}|{names[j]} axis={axis}@{plane}: walk seam but '
                                    f'NOT mutually registered (A lists B: {bIdxInA is not None}, '
                                    f'B lists A: {aIdxInB is not None})')
                    checked += 1
                continue
            a_lo, a_hi, aTagLo, aTagHi = side_counts(A['mesh'], axis, plane, lo, hi, bIdxInA)
            b_lo, b_hi, bTagLo, bTagHi = side_counts(B['mesh'], axis, plane, lo, hi, aIdxInB)
            aEdge = a_lo if aLow else a_hi          # A's own floor at the seam
            bEdge = b_hi if aLow else b_lo          # B's own floor at the seam
            if aEdge < MIN_EDGE or bEdge < MIN_EDGE:
                continue                            # not a walk seam (wall / no floor)
            checked += 1
            aPast = aTagHi if aLow else aTagLo       # A's B-tagged cells PAST plane (into B)
            bPast = bTagLo if aLow else bTagHi       # B's A-tagged cells PAST plane (into A)
            if aPast >= MIN_STRIP and bPast >= MIN_STRIP:
                passed += 1
                print(f'  PASS {names[i]:26s}|{names[j]:26s} {axis}@{plane}  '
                      f'A->B={aPast} B->A={bPast} (edge {aEdge}/{bEdge})')
            else:
                failures.append(f'{names[i]}|{names[j]} axis={axis}@{plane}: walk seam (edge '
                                f'{aEdge}/{bEdge}) but cross-strip A->B={aPast} B->A={bPast} '
                                f'(need >={MIN_STRIP} each) - NOT stitched')
    print(f'\nWalk seams checked: {checked}   passed: {passed}   failed: {len(failures)}')
    if failures:
        print('\nFAILURES:')
        for f in failures:
            print('  ' + f)
        print('\nGATE FAIL: at least one walk seam is not cross-tagged (would wall in-game).')
        return 1
    if passed == 0:
        print('GATE FAIL: no walk seams passed - the chain has no stitched seam (setup wrong?).')
        return 1
    print('GATE PASS: every real walk seam carries a mutual cross-tagged strip.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
