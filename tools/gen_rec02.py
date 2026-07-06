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
from tok_parse import extract_mesh, read_tables, parse_stream, validate  # noqa
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
    return guids, center, dims, verts, tris


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


def build_tiles(hgrid, open_cells, gw, gh, tw, th, grid_ox=0.0, grid_oz=0.0,
                area_boxes=None):
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
             neighbors=(), footprint=None, area_boxes=None):
    """Generate a 0x0b doc from a level's 0x0a tok mesh.

    mesh: optional pre-parsed load_tok_mesh() tuple (guids, center, dims,
        verts, tris) for lvl_path; skips re-reading the file.
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
    neighbors: iterable of (verts, tris, (dx, dy, dz)) tok meshes of
        grid-adjacent levels, rasterized IN ADDITION to the level's own mesh.
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
        guids_a, center_a, dims_a, verts, tris = mesh
    else:
        guids_a, center_a, dims_a, verts, tris = load_tok_mesh(lvl_path)
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
    center = (x0 + dims[0], center_a[1], z0 + dims[2])
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
    gx0f, gx1f = -off_x, 2 * dims[0] - off_x
    gz0f, gz1f = -off_z, 2 * dims[2] - off_z
    for nverts, ntris, (dx, dy, dz) in neighbors:
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
        n_nbr += 1
    fill = {i: h for i, h in nbr_grid.items() if i not in hgrid}
    # JOIN RAMP: multi-source BFS from own cells into the fill (4-neighbor),
    # carrying the adjacent own height as anchor; clamp each fill cell's
    # height to anchor +- climb*distance so the first steps off the own floor
    # are walkable. Only bites within RAMP_DEPTH cells of the join and only
    # for small (<= RAMP_MAX) disagreements; genuine cliffs are preserved.
    RAMP_MAX = 15                                  # height units (3.0u)
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
    open_cells = erode(set(hgrid), gw, gh, ERODE_CELLS)
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
                     n_tiles=len(records), nv=len(verts), nt=len(tris))


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
