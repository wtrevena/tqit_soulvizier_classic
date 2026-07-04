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
AREA_ID = 2


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


def rasterize(verts, tris, off_x, off_z, off_y, gw, gh):
    """Rasterize triangles into a gw x gh cell grid.
    Returns dict cell_index -> height_index (max y wins)."""
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


def build_tiles(hgrid, open_cells, gw, gh, tw, th):
    """Slice global grid into tile records."""
    records = []
    climb = CLIMB_CELLS
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
                        cells.append((lx, lz, idx, h))
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
            for lx, lz, idx, h in cells:
                li = lz * TILE + lx
                heights[li] = h - hmin
                areas[li] = AREA_ID
                minx = min(minx, lx); maxx = max(maxx, lx)
                miny = min(miny, lz); maxy = max(maxy, lz)
            # connectivity: dirs 0=W(x-1) 1=N(z+1) 2=E(x+1) 3=S(z-1)
            for lx, lz, idx, h in cells:
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


def generate(lvl_path, own_guid=None, neighbor_guids=(), pad=PAD):
    guids_a, center_a, dims_a, verts, tris = load_tok_mesh(lvl_path)
    # 0x0b frame: same center, dims padded
    center = tuple(center_a)
    dims = (dims_a[0] + pad, dims_a[1] + pad, dims_a[2] + pad)
    # local offsets: tok is relative to 0x0a corner (center - dims_a); our grid
    # origin is center - dims  => shift by (dims - dims_a) = pad
    off = pad
    gw = int(math.ceil(2 * dims[0] / CS))
    gh = int(math.ceil(2 * dims[2] / CS))
    tw = int(math.ceil(2 * dims[0] / (TILE * CS)))
    th = int(math.ceil(2 * dims[2] / (TILE * CS)))
    hgrid = rasterize(verts, tris, off, off, off, gw, gh)
    open_cells = erode(set(hgrid), gw, gh, ERODE_CELLS)
    records = build_tiles(hgrid, open_cells, gw, gh, tw, th)
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
                     n_rast=len(hgrid), n_tiles=len(records), nv=len(verts),
                     nt=len(tris))


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
