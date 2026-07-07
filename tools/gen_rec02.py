"""PROTOTYPE offline navmesh generator: SV 0x0a (PathEngine tok mesh) -> TQAE 0x0b
(REC\x02 tile-cache) with no Editor and no Recast library.

Pipeline:
  1. parse 0x0a: center/dims + tok walkable-surface mesh (verts/tris)
  2. rasterize tris onto a global cs=0.2 cell grid (corner-relative local frame)
  3. erode by walkableRadius (2 cells), compute per-cell height indices
  4. slice into 64x64 tiles; build heights/areas/cons planes (Detour dtTileCacheLayer)
  5. fastlz-compress; emit 3 difficulty sets; wrap in REC\x02 container

Usage: py gen_rec02.py <level.lvl> <out.0b.bin> [--guid <hex32>]
"""
import math
import struct
import sys
from pathlib import Path

SCRATCH = Path(__file__).parent
sys.path.insert(0, str(SCRATCH))
from tok_parse import (extract_mesh, read_tables, parse_stream, validate,  # noqa
                       parse_obstacles)
from rec02_format import serialize_rec02, parse_rec02  # noqa

CS = 0.2
CH = 0.2
TILE = 64
PAD = 16            # world units of padding around level box (Editor-like)
ERODE_CELLS = 2     # walkableRadius 0.4 / cs 0.2
CLIMB_CELLS = 5     # walkableClimb 1.0 / ch 0.2
AREA_ID = 1     # base-game cave interiors use walkable area-id 1 (SpartaOptCave,
                # DelphiOptCave, etc.); id 2 is a surface-level class. Match the
                # working cave convention so any area-selective in-cave path query
                # treats our generated cells as walkable.


def load_tok_mesh(lvl_path):
    """Parse the level's 0x0a ground tok. Returns
    (guids, center, dims, verts, tris, obstacles) where obstacles is the list of
    level-local (x,z) baseObstacle polygons (RCA: the ONLY encoding of the rock
    walls; generate() carves them out of the walkable set). Back-compat: callers
    that unpacked 5 values must add the trailing `obstacles`."""
    guids, center, dims, tok = extract_mesh(lvl_path)
    elems, attrs, pos = read_tables(tok)
    # tok attr value widths by type id: 1=cstring, 2=int32, 3=int16, 4=int8, 7=int8
    root, endpos, err = parse_stream(tok, pos, elems, attrs, {2: 4, 3: 2, 4: 1, 7: 1})
    assert root is not None, err
    mesh = root[0]
    m3 = [c for c in mesh['children'] if c['tag'] == 'mesh3D'][0]
    verts_el = [c for c in m3['children'] if c['tag'] == 'verts'][0]
    tris_el = [c for c in m3['children'] if c['tag'] == 'tris'][0]
    verts = [(c['attrs']['x'] / 100.0, c['attrs']['y'] / 100.0,
              c['attrs'].get('z', 0) / 100.0) for c in verts_el['children']]
    tris = [(c['attrs']['edge0StartVert'], c['attrs']['edge1StartVert'],
             c['attrs']['edge2StartVert']) for c in tris_el['children']]
    obstacles = parse_obstacles(tok)
    return guids, center, dims, verts, tris, obstacles


def tri_box_overlap_2d(v0, v1, v2, bx0, bz0, bx1, bz1):
    """2D SAT: triangle (x,z) vs axis-aligned box."""
    xs = (v0[0], v1[0], v2[0])
    zs = (v0[1], v1[1], v2[1])
    if max(xs) < bx0 or min(xs) > bx1 or max(zs) < bz0 or min(zs) > bz1:
        return False
    # edge normals as separating axes
    pts = ((v0[0], v0[1]), (v1[0], v1[1]), (v2[0], v2[1]))
    corners = ((bx0, bz0), (bx1, bz0), (bx1, bz1), (bx0, bz1))
    for i in range(3):
        px, pz = pts[i]
        qx, qz = pts[(i + 1) % 3]
        nx, nz = -(qz - pz), (qx - px)
        tmin = min(nx * p[0] + nz * p[1] for p in pts)
        tmax = max(nx * p[0] + nz * p[1] for p in pts)
        bmin = min(nx * c[0] + nz * c[1] for c in corners)
        bmax = max(nx * c[0] + nz * c[1] for c in corners)
        if tmin > bmax or tmax < bmin:
            return False
    return True


def rasterize(verts, tris, off_x, off_z, off_y, gw, gh, hgrid=None):
    """Rasterize triangles into a gw x gh cell grid.
    Returns dict cell_index -> height_index (max y wins). Pass an existing
    hgrid to ACCUMULATE additional geometry (e.g. neighbor-level meshes) into
    the same grid; triangles outside the grid are clipped by the bbox test."""
    if hgrid is None:
        hgrid = {}
    for (a, b, c) in tris:
        v0 = (verts[a][0] + off_x, verts[a][1] + off_z, verts[a][2] + off_y)
        v1 = (verts[b][0] + off_x, verts[b][1] + off_z, verts[b][2] + off_y)
        v2 = (verts[c][0] + off_x, verts[c][1] + off_z, verts[c][2] + off_y)
        minx = max(int(min(v0[0], v1[0], v2[0]) / CS), 0)
        maxx = min(int(max(v0[0], v1[0], v2[0]) / CS) + 1, gw - 1)
        minz = max(int(min(v0[1], v1[1], v2[1]) / CS), 0)
        maxz = min(int(max(v0[1], v1[1], v2[1]) / CS) + 1, gh - 1)
        if minx > maxx or minz > maxz:
            continue
        # plane for y interpolation
        ux, uz, uy = v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]
        wx, wz, wy = v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]
        det = ux * wz - uz * wx
        p2d0 = (v0[0], v0[1]); p2d1 = (v1[0], v1[1]); p2d2 = (v2[0], v2[1])
        for cz in range(minz, maxz + 1):
            bz0, bz1 = cz * CS, (cz + 1) * CS
            for cx in range(minx, maxx + 1):
                bx0, bx1 = cx * CS, (cx + 1) * CS
                if not tri_box_overlap_2d(p2d0, p2d1, p2d2, bx0, bz0, bx1, bz1):
                    continue
                # y at clamped cell center (barycentric, clamped into tri)
                pxc = min(max((bx0 + bx1) * 0.5, min(p2d0[0], p2d1[0], p2d2[0])),
                          max(p2d0[0], p2d1[0], p2d2[0]))
                pzc = min(max((bz0 + bz1) * 0.5, min(p2d0[1], p2d1[1], p2d2[1])),
                          max(p2d0[1], p2d1[1], p2d2[1]))
                if det != 0:
                    s = ((pxc - v0[0]) * wz - (pzc - v0[1]) * wx) / det
                    t = (ux * (pzc - v0[1]) - uz * (pxc - v0[0])) / det
                    y = v0[2] + s * uy + t * wy
                else:
                    y = max(v0[2], v1[2], v2[2])
                h = int(round(y / CH))
                idx = cz * gw + cx
                cur = hgrid.get(idx)
                if cur is None or h > cur:
                    hgrid[idx] = h
    return hgrid


def relax_gradient_down(hgrid, gw, gh, climb):
    """Make every 4-adjacent walkable pair <= climb apart by LOWERING any cell that
    sits > climb above its lowest walkable neighbour, to (lowest_nbr + climb). Repeat
    until stable. Lowering-only + bounded: a high plateau only ramps down within
    ~(step/climb) cells of a lower neighbour, so real floor away from seams is
    untouched. This reconciles the up-to-2.6u disagreement between adjacent SV toks
    at a shared boundary into a WALKABLE ramp (the 2026-07-06 seam-handoff fix: an
    unramped 2.6u step froze the player at the region hand-off, > the engine's 2u
    findNearestPoly tolerance). Queue-based: only steep edges do work."""
    from collections import deque
    ncell = gw * gh

    def steps(i):
        x = i % gw
        out = []
        if x > 0 and (i - 1) in hgrid: out.append(i - 1)
        if x < gw - 1 and (i + 1) in hgrid: out.append(i + 1)
        if i >= gw and (i - gw) in hgrid: out.append(i - gw)
        if i < ncell - gw and (i + gw) in hgrid: out.append(i + gw)
        return out

    q = deque(hgrid.keys())
    inq = set(hgrid.keys())
    guard = 0
    limit = 60 * len(hgrid) + 10000
    while q and guard < limit:
        guard += 1
        i = q.popleft(); inq.discard(i)
        nb = steps(i)
        if not nb:
            continue
        lo = min(hgrid[n] for n in nb)
        if hgrid[i] - lo > climb:
            hgrid[i] = lo + climb
            for n in nb:
                if n not in inq:
                    q.append(n); inq.add(n)
    return guard


def erode(open_cells, gw, gh, iterations):
    cur = open_cells
    for _ in range(iterations):
        nxt = set()
        for idx in cur:
            x, z = idx % gw, idx // gw
            if (x > 0 and (idx - 1) in cur and x < gw - 1 and (idx + 1) in cur and
                    z > 0 and (idx - gw) in cur and z < gh - 1 and (idx + gw) in cur):
                nxt.add(idx)
        cur = nxt
    return cur


_EDGE_EPS = 1e-6   # world units; << the 0.01u obstacle quantum and 0.2u cell


def _on_segment(x, z, ax, az, bx, bz):
    """True if (x,z) lies on segment (a)-(b) within _EDGE_EPS (colinear + in bbox)."""
    cross = (bx - ax) * (z - az) - (bz - az) * (x - ax)
    seg_len = math.hypot(bx - ax, bz - az)
    if seg_len == 0:
        return math.hypot(x - ax, z - az) <= _EDGE_EPS
    # perpendicular distance = |cross| / seg_len
    if abs(cross) / seg_len > _EDGE_EPS:
        return False
    return (min(ax, bx) - _EDGE_EPS <= x <= max(ax, bx) + _EDGE_EPS and
            min(az, bz) - _EDGE_EPS <= z <= max(az, bz) + _EDGE_EPS)


def _point_in_poly(x, z, poly, edge_inclusive=False):
    """Even-odd (ray-cast) point-in-polygon test on the XZ plane. With
    edge_inclusive, a point lying exactly on a polygon edge (within _EDGE_EPS)
    counts as inside. The plain even-odd result is FRAME-SENSITIVE for a point
    that sits exactly on an edge (the < comparison flips with sub-ULP coordinate
    changes), so the carve stamps edge-inclusive to remove on-edge cells in ANY
    frame; the G-OVER gate can then verify with the strict (exclusive) rule and
    still find zero. See docs/NAVMESH_OVERCOVERAGE_RCA.md."""
    if edge_inclusive:
        n = len(poly)
        for i in range(n):
            ax, az = poly[i]
            bx, bz = poly[(i + 1) % n]
            if _on_segment(x, z, ax, az, bx, bz):
                return True
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if ((zi > z) != (zj > z)) and \
                (x < (xj - xi) * (z - zi) / (zj - zi) + xi):
            inside = not inside
        j = i
    return inside


def stamp_obstacles(obstacles, gw, gh, off_x, off_z, r=0.0):
    """Return the set of cell indices whose CENTER lies inside any obstacle polygon.

    obstacles: level-local (x,z) polygons (tok_parse.parse_obstacles). off_x/off_z
    shift level-local -> grid world (a cell (cx,cz) center is at world-local
    (cx+0.5)*CS - off on each axis). r is an OPTIONAL isotropic dilation of the
    per-poly bbox prefilter ONLY when r>0 the point-in-poly still tests the raw
    polygon (no vertex offsetting); the fix uses r=0 (RCA FIX SPEC: dilation
    over-carves 15% of AE-walkable and buys only +8pt, and erode(2) already trims
    the 0.4u walkableRadius rim). Even-odd rule, per-poly bbox prefilter - exactly
    batch_validate.stamp_obstacles, which reproduced the RCA Measurement-7 carve
    counts byte-exact."""
    obs = set()
    for poly in obstacles:
        if len(poly) < 3:
            continue
        xs = [p[0] for p in poly]
        zs = [p[1] for p in poly]
        cx0 = max(int((min(xs) - r + off_x) / CS), 0)
        cx1 = min(int((max(xs) + r + off_x) / CS) + 1, gw - 1)
        cz0 = max(int((min(zs) - r + off_z) / CS), 0)
        cz1 = min(int((max(zs) + r + off_z) / CS) + 1, gh - 1)
        for cz in range(cz0, cz1 + 1):
            wz = (cz + 0.5) * CS - off_z   # grid cell center -> level-local
            for cx in range(cx0, cx1 + 1):
                wx = (cx + 0.5) * CS - off_x
                # edge_inclusive: a cell center exactly on an obstacle outline is
                # carved deterministically, so G-OVER holds regardless of the
                # (integer-translated) frame the verifier recomputes cells in.
                if _point_in_poly(wx, wz, poly, edge_inclusive=True):
                    obs.add(cz * gw + cx)
    return obs


def _main_component(cells, gw, gh, climb, hgrid):
    """Largest 4-adjacency, |Δh|<=climb component of a cell-index set (engine model)."""
    seen = set()
    best = ()
    ncell = gw * gh
    for start in cells:
        if start in seen:
            continue
        from collections import deque as _dq
        q = _dq([start])
        seen.add(start)
        comp = [start]
        while q:
            i = q.popleft()
            h = hgrid[i]
            x = i % gw
            for step, ok in ((-1, x > 0), (1, x < gw - 1),
                             (-gw, i >= gw), (gw, i < ncell - gw)):
                n = i + step
                if n in cells and n not in seen and abs(hgrid[n] - h) <= climb:
                    seen.add(n)
                    q.append(n)
                    comp.append(n)
        if len(comp) > len(best):
            best = comp
    return set(best)


def _connectivity_repair(open_cells, eroded, obs_cells, region_cells,
                         gw, gh, climb, hgrid, max_restore=6000):
    """Restore the MINIMAL carved cells needed to keep every region-handoff strip
    (and any walk-chain fragment the carve split off) attached to the main walkable
    component, so the obstacle carve never severs the walk chain (RCA doorway/seam
    guard; the river-regression fix - see generate()).

    Model: 0-1 BFS over the ERODED set (the pre-carve, walk-proven connectivity)
    seeded from the main open component. Stepping to an already-open cell costs 0;
    stepping to a CARVED cell costs 1 (it must be restored) - both only across a
    4-adjacency edge with |Δh|<=climb (the engine's intra-mesh adjacency). This
    yields, per eroded cell, the fewest carved cells to reconnect it to main. For
    every target that is still disconnected we walk its predecessor chain and
    restore the carved cells on it; restored cells become cost-0 for later targets
    so shared seam bridges are counted once.

    Targets (must reconnect): each disconnected OPEN component that either carries a
    cross-level handoff strip (any region>=1 cell) or is a substantial own-region
    room piece (>= MIN_FRAG cells); tiny own rim slivers are left disconnected (see
    the reps loop). Carved rock-INTERIOR cells are never targets, so a genuinely
    walled rock island stays carved. max_restore bounds the work as a guard (a
    correct seam bridge is tens of cells; blowing the cap signals a mis-set carve and
    returns what it has).

    Returns the set of carved cell indices to restore (subset of obs_cells)."""
    from collections import deque as _dq
    main = _main_component(open_cells, gw, gh, climb, hgrid)
    if not main:
        return set()
    ncell = gw * gh
    restored = set()
    # membership: a cell is "free" (cost 0 to traverse) if open or already restored.
    free = set(open_cells)
    # dist = fewest carved cells to reach from main; pred for path reconstruction.
    # 0-1 BFS with a deque: cost-0 edges push front, cost-1 (onto carved) push back.
    INF = None
    dist = {i: 0 for i in main}
    pred = {i: None for i in main}
    dq = _dq(main)
    # We process lazily; because we restore incrementally we run a full 0-1 BFS over
    # `eroded` once from main (restoring changes only reduce costs, so a single pass
    # from main with carved=cost1 is an admissible upper bound; the reconstructed
    # paths share cells and we dedupe on restore).
    while dq:
        i = dq.popleft()
        di = dist[i]
        h = hgrid[i]
        x = i % gw
        for step, ok in ((-1, x > 0), (1, x < gw - 1),
                         (-gw, i >= gw), (gw, i < ncell - gw)):
            if not ok:
                continue
            n = i + step
            if n not in eroded or abs(hgrid[n] - h) > climb:
                continue
            w = 0 if n in free else 1
            nd = di + w
            if n not in dist or nd < dist[n]:
                dist[n] = nd
                pred[n] = i
                if w == 0:
                    dq.appendleft(n)
                else:
                    dq.append(n)
    # Targets = the DISCONNECTED WALKABLE pieces: open components other than main.
    # Restoring the cheapest carved bridge to ONE cell of a piece reconnects the
    # whole piece (it is internally connected in `open`), so we bridge each
    # disconnected open component exactly once, at its min-dist cell. Carved
    # rock-interior cells are NOT targets, so a genuinely walled rock island (no
    # eroded path to main except through more rock) is never restored - the room
    # interiors stay solid. A rock island IS reachable in `eroded` (rock has floor
    # under it), so its min bridge cost equals its erosion rim thickness; we only
    # restore pieces that are actual WALKABLE open components, never the carved rock
    # cells themselves as destinations, so islands re-open only if they carry a
    # region-strip or own floor the chain needs. Cheapest-first minimises shared
    # bridges (a later piece reuses an already-restored one at cost 0).
    comp_id = {}
    open_comps = []
    for s in open_cells:
        if s in main or s in comp_id:
            continue
        cid = len(open_comps)
        stack = [s]
        comp_id[s] = cid
        members = [s]
        while stack:
            i = stack.pop()
            h = hgrid[i]
            x = i % gw
            for step, ok in ((-1, x > 0), (1, x < gw - 1),
                             (-gw, i >= gw), (gw, i < ncell - gw)):
                if not ok:
                    continue
                n = i + step
                if (n in open_cells and n not in comp_id and n not in main
                        and abs(hgrid[n] - h) <= climb):
                    comp_id[n] = cid
                    stack.append(n)
                    members.append(n)
        open_comps.append(members)
    # Cells tagged to a cross-level neighbour region (region>=1) = the seam strips.
    # (Only these are needed to classify a component; building the full per-cell
    # inverse map over every eroded cell would be far larger - region>=1 is a small
    # fraction of the grid - so union just the strip regions.)
    strip_cells = set()
    for _k, _cs in region_cells.items():
        if _k >= 1:
            strip_cells |= _cs
    # For each disconnected open component decide whether to bridge it. Bridge iff it
    # carries a cross-level HANDOFF strip (any region>=1 cell - the river-reconnect
    # requirement) OR it is a SUBSTANTIAL own-region area (>= MIN_FRAG cells = a real
    # room piece the carve fragmented, whose reconnection restores the build19
    # topology). Tiny own-region rim fragments (< MIN_FRAG, no strip) are NOT bridged
    # - they are erosion/rock-rim slivers, and bridging them would drill a needless
    # walk-through-rock corridor to a scrap of floor. This keeps the walk chain fully
    # connected (strips + real rooms) while minimising walk-through-rock (measured:
    # cuts own-region walk-on-rock ~70% on drxFirstRoom vs bridging every fragment).
    MIN_FRAG = 200
    reps = []
    for members in open_comps:
        has_strip = any(i in strip_cells for i in members)
        if not has_strip and len(members) < MIN_FRAG:
            continue
        best = None
        for i in members:
            if i in dist and (best is None or dist[i] < dist[best]):
                best = i
        if best is not None and dist[best] > 0:
            reps.append(best)
    reps.sort(key=lambda i: dist[i])
    for t in reps:
        if len(restored) >= max_restore:
            break
        path_restore = []
        u = t
        guard = 0
        lim = 4 * (gw + gh) + 8
        while u is not None and u not in main and guard < lim:
            if u not in free:
                path_restore.append(u)
            u = pred.get(u)
            guard += 1
        for c in path_restore:
            if c not in restored:
                restored.add(c)
                free.add(c)
    return restored & obs_cells


def build_tiles(hgrid, open_cells, gw, gh, tw, th, grid_ox=0.0, grid_oz=0.0,
                area_boxes=None, area_map=None):
    """Slice global grid into tile records.

    area_boxes: optional ordered list of (x0,z0,x1,z1) WORLD footprint boxes
    parallel to the navmesh GUID list. When given, each walkable cell's area id
    (== its poly flags at runtime, which the engine reads as a 1-BASED INDEX
    INTO THE GUID LIST to decide which level owns the cell - see
    docs/CROSS_LEVEL_STITCH_RE.md) is set to 1 + index of the first box (own
    first) whose half-open [x0,x1)x[z0,z1) contains the cell CENTER. This is the
    cross-level seam mechanism: a level's mesh rasterizes its neighbours' strip
    and tags those cells with the neighbour's GUID index, so one mesh covers
    both sides of a seam. Cell -> world uses the grid origin (grid_ox,grid_oz).
    Without area_boxes, the constant AREA_ID is stamped (legacy single-level)."""
    records = []
    climb = CLIMB_CELLS

    def _cell_area(gx, gz):
        if area_map is not None:            # preserved areas (retile post-pass)
            return area_map.get((gx, gz), 1)
        if not area_boxes:
            return AREA_ID
        wx = grid_ox + (gx + 0.5) * CS
        wz = grid_oz + (gz + 0.5) * CS
        for k, (bx0, bz0, bx1, bz1) in enumerate(area_boxes):
            if bx0 <= wx < bx1 and bz0 <= wz < bz1:
                return k + 1
        return 1  # inside no declared box -> own (index 0); avoids notching own mesh

    for ty in range(th):
        for tx in range(tw):
            x0, z0 = tx * TILE, ty * TILE
            cells = []
            hmin, hmax = None, None
            for lz in range(TILE):
                gz = z0 + lz
                if gz >= gh:
                    break
                base = gz * gw + x0
                for lx in range(TILE):
                    gx = x0 + lx
                    if gx >= gw:
                        break
                    idx = base + lx
                    if idx in open_cells:
                        h = hgrid[idx]
                        cells.append((lx, lz, idx, h, _cell_area(gx, gz)))
                        hmin = h if hmin is None else min(hmin, h)
                        hmax = h if hmax is None else max(hmax, h)
            if not cells:
                continue
            assert hmax - hmin <= 255, f'tile ({tx},{ty}) height range {hmax-hmin}'
            heights = bytearray(b'\xff' * (TILE * TILE))
            areas = bytearray(TILE * TILE)
            cons = bytearray(TILE * TILE)
            minx = miny = 255
            maxx = maxy = 0
            for lx, lz, idx, h, area in cells:
                li = lz * TILE + lx
                heights[li] = h - hmin
                areas[li] = area
                minx = min(minx, lx); maxx = max(maxx, lx)
                miny = min(miny, lz); maxy = max(maxy, lz)
            # connectivity: dirs 0=W(x-1) 1=N(z+1) 2=E(x+1) 3=S(z-1)
            for lx, lz, idx, h, area in cells:
                li = lz * TILE + lx
                con = 0
                portal = 0
                for dbit, (dx, dz) in enumerate(((-1, 0), (0, 1), (1, 0), (0, -1))):
                    gx, gz = tx * TILE + lx + dx, ty * TILE + lz + dz
                    if not (0 <= gx < gw and 0 <= gz < gh):
                        continue
                    nidx = gz * gw + gx
                    if nidx not in open_cells:
                        continue
                    if abs(hgrid[nidx] - h) > climb:
                        continue
                    nlx, nlz = lx + dx, lz + dz
                    if 0 <= nlx < TILE and 0 <= nlz < TILE:
                        con |= 1 << dbit
                    else:
                        portal |= 1 << dbit
                cons[li] = (portal << 4) | con
            hdr = dict(magic=0x44544c52, version=1, tx=tx, ty=ty, tlayer=0,
                       bmin=(tx * TILE * CS, hmin * CH, ty * TILE * CS),
                       bmax=((tx + 1) * TILE * CS, hmax * CH, (ty + 1) * TILE * CS),
                       hmin=hmin, hmax=hmax, width=TILE, height=TILE,
                       minx=minx, maxx=maxx, miny=miny, maxy=maxy, pad=b'\x00\x00')
            records.append(dict(hdr=hdr, trail_tx=tx, trail_ty=ty,
                                heights=bytes(heights), areas=bytes(areas),
                                cons=bytes(cons)))
    return records


def generate(lvl_path, own_guid=None, neighbor_guids=(), pad=PAD, mesh=None,
             neighbors=(), footprint=None, area_boxes=None, y_shift=0.0,
             obstacles=(), region_obstacles=None):
    """Generate a 0x0b doc from a level's 0x0a tok mesh.

    obstacles: this level's LEVEL-LOCAL (x,z) baseObstacle polygons
        (tok_parse.parse_obstacles). SV authored every rock/wall as a PathEngine
        baseObstacle polygon ON TOP of a broad flat ground tok (runtime walkable =
        ground MINUS expanded obstacles); the ground mesh3D alone rasterizes every
        rock footprint as walkable floor, so the player walks through solid rocks
        (RCA docs/NAVMESH_OVERCOVERAGE_RCA.md). These polygons are subtracted from
        the walkable set with ERODE-THEN-CARVE order (erode first, then remove
        obstacle cells) at r=0. Erode-then-carve fragments far less than
        carve-then-erode (RCA Measurement-7: 10/62/121 vs 47/731/1235 frags) and
        makes G-OVER (zero walkable cell inside any obstacle) hold by construction.

    region_obstacles: optional list PARALLEL to `area_boxes`, where
        region_obstacles[k] is level-k's LEVEL-LOCAL (x,z) baseObstacle polygons
        ALREADY TRANSLATED into THIS level's local frame (region 0 == own
        obstacles; region k>=1 == the k-th area_box neighbour's obstacles shifted
        by that neighbour's (dx,dz)). When given, the carve is REGION-TAG-SCOPED:
        each walkable cell is carved by the obstacles of the level whose area_box
        tags it (build_tiles._cell_area's exact partition = the level the ENGINE
        treats the cell as belonging to at runtime). This is the correct carve
        (RCA FIX SPEC "carve each region k's cells with level-k's obstacles"):
        the raster-ownership partition (own_cells vs the neighbour fill strip)
        DISAGREES with the runtime region tag - a cell can be in own_cells yet
        area-tagged to a neighbour by geometry - so the old own/fill carve both
        (a) LEAKED walk-through-rock at seams (a neighbour-region cell inside the
        neighbour's rock was in own_cells, so neither the own carve nor the fill
        carve removed it) and (b) SEVERED region handoffs (the own carve ate own
        rocks across cells the engine tags to a neighbour, fragmenting the seam so
        river_extension01/02 went unreachable). Carving by the runtime tag fixes
        both. Falls back to the legacy own/fill carve when None (single-level or
        callers that do not pass area_boxes).

    mesh: optional pre-parsed load_tok_mesh() tuple (guids, center, dims,
        verts, tris, obstacles) for lvl_path; skips re-reading the file. When
        `obstacles` is not passed explicitly it is taken from this tuple's 6th
        element (if present).
    footprint: optional (fx0, fz0, fx1, fz1) = the level's LEVELS-INDEX
        footprint (grid corner .. corner + BOX tiles * 2) in the SAME world
        frame as the 0x0a header (SV-original). The generation grid covers
        the UNION of the 0x0a box and this footprint, plus pad. Without it
        the grid is the 0x0a box + pad only - and on levels whose 0x0a box
        is SMALLER than their index footprint (SV slack levels; also
        BC_initialpathway after the merge's content->box widen) the
        walkable fill physically cannot reach past the index boundary the
        engine stitches at, leaving a one-sided seam (measured:
        ocean_extension01's east fill was clipped 2u past the boundary
        instead of crossing 15.6u).
    neighbors: iterable of (verts, tris, (dx, dy, dz)) OR
        (verts, tris, (dx, dy, dz), nobstacles) tok meshes of grid-adjacent
        levels, rasterized IN ADDITION to the level's own mesh. nobstacles (4th
        element, optional) is that neighbour's own level-local baseObstacle
        polygons; they are carved from the merged walkable set translated by the
        SAME (dx,dz) as the neighbour's geometry, so a rock the neighbour authored
        near the shared seam carves the strip this mesh rasterizes past the
        boundary (that rock is solid on both sides). Without a 4th element the
        neighbour strip is rasterized but not carved (back-compat).
        The delta is world-units neighbor_0x0a_corner - own_0x0a_corner, where
        a level's 0x0a corner = its 0x0a header center - dims per axis (NOT
        the LEVELS-index corner: the two differ by up to 1u in x/z and 12u in
        y on SV levels, and the tok/0x0b world anchor is the 0x0a center).
        Vert tuples are (x, z_ground, y_height), so dx/dz shift the ground
        plane and dy shifts the height. Purpose: extend the walkable floor
        ACROSS shared level boundaries into neighbor territory, mimicking
        SV's single continuous 0x0a mesh - two adjacent levels' 0x0b
        navmeshes only stitch (player walks across) where BOTH cross the
        shared boundary and overlap. Neighbor tris outside this level's
        padded grid are clipped by the rasterizer's bbox test.

        OWN-WINS merge (do NOT change to max-y): neighbor cells fill ONLY
        where the level's own tok has no floor. Adjacent SV toks genuinely
        DISAGREE about the floor height where they overlap (measured:
        Random09A says 19.0 vs xPassageTransitionStart 16.4 at the same
        world cells, 2.6u apart, across their whole 30u overlap strip - and
        the engine's cross-level stitch tolerates that in-game). A max-y
        merge would overwrite a level's own walk-proven floor with the
        neighbor's higher copy and cut an internal cons cliff (climb is 5
        height units = 1.0u) INSIDE the level = a NEW invisible wall a few
        units past the seam. Own-wins keeps every level's own floor heights
        and only ADDS floor.

        JOIN RAMP: where the fill meets the own floor with a small height
        disagreement (<= RAMP_MAX = 15 height units = 3.0u, just above the
        measured 2.6u tok disagreement), the first fill cells are blended
        toward the adjacent own height so no step exceeds walkableClimb
        (5 units/cell) - otherwise a level whose own tok stops exactly AT
        the shared boundary gets a cons cliff at the own|fill join and the
        outward edge bits stay 0 exactly like the original xPTS wall
        (measured at drxBC2|drxBC_Connector1: 2.6u join = outward bits
        0/10). Disagreements > RAMP_MAX are genuine vertical separations
        (bridge over pit, stacked floors) and are deliberately NOT ramped.
    """
    if mesh is not None:
        # accept the legacy 5-tuple or the new 6-tuple (with obstacles)
        guids_a, center_a, dims_a, verts, tris = mesh[:5]
        mesh_obs = mesh[5] if len(mesh) > 5 else ()
    else:
        guids_a, center_a, dims_a, verts, tris, mesh_obs = load_tok_mesh(lvl_path)
    # obstacles: explicit arg wins; else the ones the mesh tuple carried.
    if not obstacles:
        obstacles = mesh_obs
    corner = tuple(center_a[i] - dims_a[i] for i in range(3))
    # 0x0b frame: cover the union of the 0x0a box and the index footprint,
    # padded; degenerates to the old center_a/dims_a+pad frame when the
    # footprint is absent or inside the 0x0a box.
    x0, x1 = corner[0], corner[0] + 2 * dims_a[0]
    z0, z1 = corner[2], corner[2] + 2 * dims_a[2]
    if footprint is not None:
        fx0, fz0, fx1, fz1 = footprint
        x0, x1 = min(x0, fx0), max(x1, fx1)
        z0, z1 = min(z0, fz0), max(z1, fz1)
    x0 -= pad; x1 += pad; z0 -= pad; z1 += pad
    # GLOBAL TILE LATTICE (2026-07-05 invisible-wall root cause): the engine
    # stitches walk-links across a grid seam only when both levels' 12.8u tile
    # lattices coincide. Every Editor-baked AE batch measures offset 0.000 mod
    # 12.8 across its seams (levels sit 64u = exactly 5 tiles apart); SV levels
    # sit at arbitrary offsets, so per-level-anchored meshes cannot stitch =
    # invisible wall at every generated<->generated seam while each room stays
    # internally walkable. Snap the grid origin DOWN and the extent UP to the
    # global 64u lattice: 64 = 5 tiles keeps corner deltas == 0 mod 12.8 AND
    # center/dims exactly integral (int32/uint32 header fields).
    x0 = (x0 // 64) * 64
    z0 = (z0 // 64) * 64
    x1 = x0 + ((x1 - x0 + 63) // 64) * 64
    z1 = z0 + ((z1 - z0 + 63) // 64) * 64
    if (x1 - x0) % 2:
        x1 += 1
    if (z1 - z0) % 2:
        z1 += 1
    dims = ((x1 - x0) // 2, dims_a[1] + pad, (z1 - z0) // 2)
    # y_shift (2026-07-06 Y-alignment): rigidly raise/lower the whole navmesh in Y via
    # the container center (integer world units) so this level's floor meets its
    # neighbours at one height (levels are anchored a constant 0/2.56u apart). Applied
    # to the CENTER (not the cell heights) so heights stay in valid uint16 range;
    # neighbour strips carry (shift_nbr - shift_own) via their dy so they land right.
    center = (x0 + dims[0], center_a[1] + int(round(y_shift)), z0 + dims[2])
    # local offsets: tok verts are relative to the 0x0a corner; grid origin is
    # (x0, z0) on the ground plane and (0x0a corner - pad) on the y axis
    off_x = corner[0] - x0
    off_z = corner[2] - z0
    off_y = pad
    gw = int(math.ceil(2 * dims[0] / CS))
    gh = int(math.ceil(2 * dims[2] / CS))
    tw = int(math.ceil(2 * dims[0] / (TILE * CS)))
    th = int(math.ceil(2 * dims[2] / (TILE * CS)))
    hgrid = rasterize(verts, tris, off_x, off_z, off_y, gw, gh)
    n_own = len(hgrid)
    own_cells = set(hgrid)   # cells from THIS level's OWN tok (before neighbour fill).
    #   Own obstacles carve only these (a neighbour strip is the neighbour's floor,
    #   carved by the neighbour's obstacles - RCA FIX SPEC: "carve only own-level
    #   obstacles into own-level cells"). Carving own rocks across the neighbour
    #   strip wrongly walls a seam handoff shut (measured: drxBC2's own rocks
    #   isolated the river-extension strip -> river unreachable).
    # Neighbor-aware rasterization: union in adjacent levels' geometry so the
    # walkable floor crosses every shared boundary (fills the pad margin).
    # Cheap prefilter: skip neighbors whose translated xz bbox misses this
    # level's grid rect ([-off, 2*dims - off] in own-0x0a-corner frame).
    # Neighbors rasterize into a SEPARATE grid (max-y among neighbors), then
    # merge OWN-WINS + JOIN RAMP: only cells the own tok left empty are
    # filled, and fill heights are blended at the own|fill join (see the
    # docstring - overlapping SV toks disagree by up to 2.6u about the same
    # floor; overwriting own cells would cut an internal cons cliff, and an
    # unramped join cliff kills the outward seam bits).
    n_nbr = 0
    nbr_grid = {}
    nbr_obstacles = []   # neighbour obstacle polygons, already translated to this
    #                      level's level-local frame (by the neighbour's dx,dz),
    #                      to carve the rasterized neighbour strip (a rock near a
    #                      seam is solid on both sides of the boundary).
    gx0f, gx1f = -off_x, 2 * dims[0] - off_x
    gz0f, gz1f = -off_z, 2 * dims[2] - off_z
    for nbr in neighbors:
        nverts, ntris, (dx, dy, dz) = nbr[0], nbr[1], nbr[2]
        nobs = nbr[3] if len(nbr) > 3 else ()
        if not nverts or not ntris:
            continue
        nx0 = min(v[0] for v in nverts) + dx
        nx1 = max(v[0] for v in nverts) + dx
        nz0 = min(v[1] for v in nverts) + dz
        nz1 = max(v[1] for v in nverts) + dz
        if nx1 < gx0f or nx0 > gx1f or nz1 < gz0f or nz0 > gz1f:
            continue
        tverts = [(v[0] + dx, v[1] + dz, v[2] + dy) for v in nverts]
        rasterize(tverts, ntris, off_x, off_z, off_y, gw, gh, hgrid=nbr_grid)
        # translate this neighbour's obstacle polys by the SAME (dx,dz) so they
        # sit in this level's level-local frame (verts local (x,z) -> local+d).
        for poly in nobs:
            nbr_obstacles.append([(px + dx, pz + dz) for (px, pz) in poly])
        n_nbr += 1
    # OWN-WINS + JOIN-RAMP fill. Own tok wins where it has floor; neighbour toks
    # only fill the pad strip past the own footprint. NOTE (2026-07-06): the
    # earlier owner-wins+relax height surgery was REVERTED - it created a NEW cliff
    # earlier than the seam (the ramp bent one floor down unevenly). The real cause
    # of the seam step is a CONSTANT per-level Y ANCHOR offset (levels are 0 or 2.56u
    # apart, stdev 0); gen_bc_navmeshes now rigidly Y-aligns adjacent levels so the
    # own floor and the neighbour strip meet at the SAME height with no step and no
    # ramp needed. area_boxes is still used purely for per-cell REGION TAGGING below.
    fill = {i: h for i, h in nbr_grid.items() if i not in hgrid}
    RAMP_MAX = 15
    RAMP_DEPTH = (RAMP_MAX + CLIMB_CELLS - 1) // CLIMB_CELLS
    ncells = gw * gh
    dist, anch, frontier = {}, {}, []
    for i in fill:
        x = i % gw
        best = None
        for step, ok in ((-1, x > 0), (1, x < gw - 1),
                         (-gw, i >= gw), (gw, i < ncells - gw)):
            if not ok:
                continue
            a = hgrid.get(i + step)
            if a is not None and (best is None or a > best):
                best = a
        if best is not None:
            dist[i], anch[i] = 1, best
            frontier.append(i)
    d = 1
    while frontier and d < RAMP_DEPTH:
        nxt = []
        for i in frontier:
            x = i % gw
            for step, ok in ((-1, x > 0), (1, x < gw - 1),
                             (-gw, i >= gw), (gw, i < ncells - gw)):
                nb = i + step
                if ok and nb in fill and nb not in dist:
                    dist[nb], anch[nb] = d + 1, anch[i]
                    nxt.append(nb)
        frontier = nxt
        d += 1
    for i, di in dist.items():
        h = fill[i]
        if abs(h - anch[i]) <= RAMP_MAX:
            lo_b, hi_b = anch[i] - CLIMB_CELLS * di, anch[i] + CLIMB_CELLS * di
            fill[i] = min(max(h, lo_b), hi_b)
    hgrid.update(fill)
    # Drop cells that landed below the valid height floor (h < 0). These are only
    # ever stacked-below NEIGHBOUR contributions - a different level 16u+ under this
    # one that overlaps only in XZ (the neighbour rasteriser is XZ-bbox clipped, not
    # Y-clipped). Own floor can never be here (own uses off_y = pad, so h >= pad/CH =
    # 80). They are unwalkable garbage far below the floor; keeping them is harmless
    # in gen18 but the Y-alignment shift on a neighbour strip can push such a cell from
    # ~0 to negative, and bmin.y = hmin*CH is packed as uint16 -> serialize crash.
    for _i in [i for i, h in hgrid.items() if h < 0]:
        del hgrid[_i]
    # ERODE-THEN-CARVE (RCA docs/NAVMESH_OVERCOVERAGE_RCA.md FIX SPEC): erode the
    # walkable set by walkableRadius (ERODE_CELLS) FIRST, THEN subtract the cells
    # covered by baseObstacle polygons (r=0 point-in-poly). SV modelled every
    # rock/wall as an obstacle polygon over a broad flat ground tok, so without
    # this carve every rock footprint is walkable and the player walks through
    # solid rocks. Order matters: erode-then-carve retains far more of the
    # walk-chain corridors and fragments an order of magnitude less than
    # carve-then-erode (Measurement-7: 10/62/121 vs 47/731/1235 frags), and it
    # makes G-OVER hold by construction (subtracting last leaves zero in obs).
    # r=0, NO dilation (dilation over-carves 15% of AE-walkable for +8pt;
    # erode(2) already trims the 0.4u walkableRadius rim the Editor bake erodes
    # by). edge_inclusive stamps make G-OVER hold in any (integer-translated) frame.
    fill_cells = set(fill)      # neighbour-strip cells (own tok empty here)
    _eroded = erode(set(hgrid), gw, gh, ERODE_CELLS)
    if region_obstacles is not None:
        # REGION-TAG CARVE (RCA FIX SPEC "carve each region k's cells with
        # level-k's obstacles"): a cell is carved by the obstacles of the level
        # whose area_box TAGS it - the exact partition build_tiles._cell_area uses
        # and the level the ENGINE treats the cell as at runtime. This is correct
        # where the old own/fill carve was wrong: the raster-ownership partition
        # (own_cells vs the fill strip) DISAGREES with the runtime tag - a cell can
        # be in own_cells yet area-tagged to a neighbour by geometry. The old carve
        # therefore (a) LEAKED walk-through-rock at every seam (a neighbour-region
        # cell inside the neighbour's rock sat in own_cells, so obs_own missed it -
        # own level has no rock there - and obs_nbr missed it - not a fill cell) and
        # (b) SEVERED region handoffs (own rocks carved across cells the engine tags
        # to a neighbour, fragmenting the seam -> river_extension01/02 unreachable).
        # Carving strictly by the runtime tag fixes both, and keeps G-OVER
        # (no own-region cell inside an own rock) true by construction because a
        # cell tagged own (region 0) IS carved by the own obstacles.
        #
        # Region tag == build_tiles._cell_area but 0-BASED (area id = region+1):
        # first area_box (own first) whose half-open box contains the cell center,
        # else region 0 (own). Partition the eroded set by region, then carve each
        # region's cells with that region's (already own-frame-translated) polys.
        def _region_of(idx):
            gx = idx % gw
            gz = idx // gw
            wx = x0 + (gx + 0.5) * CS
            wz = z0 + (gz + 0.5) * CS
            if area_boxes:
                for _k, (bx0, bz0, bx1, bz1) in enumerate(area_boxes):
                    if bx0 <= wx < bx1 and bz0 <= wz < bz1:
                        return _k
            return 0
        region_cells = {}
        for _i in _eroded:
            region_cells.setdefault(_region_of(_i), set()).add(_i)
        obs_cells = set()
        n_obs_polys = 0
        for _k, _rcells in region_cells.items():
            _polys = region_obstacles[_k] if _k < len(region_obstacles) else ()
            if not _polys:
                continue
            n_obs_polys += len(_polys)
            obs_cells |= (stamp_obstacles(_polys, gw, gh, off_x, off_z) & _rcells)
        open_cells = _eroded - obs_cells
        # CONNECTIVITY-PRESERVING REPAIR (RCA FIX SPEC doorway/seam guard + the
        # 2026-07-07 river-regression fix): the carve must not disconnect the walk
        # chain. SV shipped ONE continuous PathEngine mesh spanning all cluster
        # levels, so two adjacent levels' floors were joined THROUGH the shared
        # overlap; when we split that into per-level meshes and carve each with its
        # own rocks, a rock the carve legitimately removes can sit exactly on the
        # thin NECK that joined a neighbour-region strip to this mesh's body -
        # stranding it (measured: river_extension01/02 went 100% reachable in the
        # walk-proven build19 baseline -> 0% after the carve, because drxBC2 /
        # drxFirstRoom / drxBC_Connector1 / xTempleTransitionHallway all carved the
        # neck joining their body to the river strip they rasterise past the seam).
        #
        # The eroded set _eroded (pre-carve) is the build19-baseline connectivity =
        # the walk chain fully joined. The repair RESTORES the minimal carved cells
        # needed to keep every region strip (and any own-region fragment the carve
        # split off) attached to the main walkable component, via a shortest bridge
        # through _eroded. This is the RCA's explicit fallback ("exclude the
        # offending edge-hugging obstacle from the carve for that donor - the rock is
        # cosmetic there; leaving its footprint walkable is harmless, the alternative
        # strands the player"). Restored cells are a THIN seam corridor (a handful of
        # cells per strip), not a rock field, so the room interiors stay solid and
        # G-OVER's own-region-in-own-rock count is only the deliberate seam bridges.
        _restored = _connectivity_repair(open_cells, _eroded, obs_cells, region_cells,
                                         gw, gh, CLIMB_CELLS, hgrid)
        if _restored:
            open_cells = open_cells | _restored
            obs_cells = obs_cells - _restored
        n_seam_restored = len(_restored)
    else:
        # LEGACY own/fill carve (single-level or callers without area_boxes):
        #   - OWN obstacles carve only OWN-tok cells (own_cells).
        #   - each NEIGHBOUR's obstacles carve only the fill strip (fill_cells).
        obs_own = stamp_obstacles(obstacles, gw, gh, off_x, off_z) & own_cells
        obs_nbr = stamp_obstacles(nbr_obstacles, gw, gh, off_x, off_z) & fill_cells
        obs_cells = obs_own | obs_nbr
        n_obs_polys = len(obstacles) + len(nbr_obstacles)
        open_cells = _eroded - obs_cells
        n_seam_restored = 0
    n_carved = len(_eroded) - len(open_cells)   # eroded cells removed by the carve
    # grid origin in WORLD coords: cell (gx,gz) center = (x0 + (gx+.5)*CS, ...).
    # area_boxes must be in this same world frame (the SV-original frame the toks
    # live in - GRID_SHIFT is applied to the container center AFTER generate()).
    records = build_tiles(hgrid, open_cells, gw, gh, tw, th,
                          grid_ox=x0, grid_oz=z0, area_boxes=area_boxes)
    params = dict(orig=(0.0, 0.0, 0.0), cs=CS, ch=CH, width=TILE, height=TILE,
                  walkableHeight=2.0, walkableRadius=0.4, walkableClimb=1.0,
                  maxSimplificationError=1.3, maxTiles=2 * tw * th, maxObstacles=128)
    guids = []
    if own_guid:
        guids.append(own_guid)
    guids.extend(neighbor_guids)
    if not guids:
        guids = [g for g in guids_a]  # fall back to 0x0a GUID entries
    doc = dict(version=1, guids=guids, center=center, dims=dims,
               sets=[dict(params=params, records=records) for _ in range(3)])
    return doc, dict(tw=tw, th=th, gw=gw, gh=gh, n_open=len(open_cells),
                     n_rast=len(hgrid), n_rast_own=n_own, n_neighbors=n_nbr,
                     n_tiles=len(records), nv=len(verts), nt=len(tris),
                     n_obs_polys=n_obs_polys, n_carved=n_carved,
                     n_open_pre_carve=len(_eroded))


if __name__ == '__main__':
    lvl = sys.argv[1] if len(sys.argv) > 1 else \
        r'C:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_sv\Levels\World\xBloodCave\BC_initialpathway.lvl'
    out = sys.argv[2] if len(sys.argv) > 2 else str(SCRATCH / 'bc_initialpathway_generated.0b.bin')
    doc, stats = generate(lvl)
    data = serialize_rec02(doc)
    Path(out).write_bytes(data)
    print(f'generated {out}: {len(data)} bytes; stats={stats}')
    # self-validate with the reference parser (round-trip + invariants)
    doc2 = parse_rec02(data, decompress=True)
    assert len(doc2['sets']) == 3
    for s in doc2['sets']:
        for r in s['records']:
            h = r['hdr']
            assert abs(h['bmin'][0] - h['tx'] * 12.8) < 1e-3
            assert abs(h['bmin'][2] - h['ty'] * 12.8) < 1e-3
            assert abs(h['bmin'][1] - h['hmin'] * CH) < 1e-4
            g = h['width'] * h['height']
            assert len(r['heights']) == g
    re = serialize_rec02(doc2)
    print(f'reference-parser round-trip: {"BYTE-IDENTICAL" if re == data else "MISMATCH"}')
    print(f'sets={len(doc2["sets"])} tiles/set={len(doc2["sets"][0]["records"])} '
          f'guids={[g.hex()[:8] for g in doc2["guids"]]} center={doc2["center"]} dims={doc2["dims"]}')
