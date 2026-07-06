"""Shared analysis lib: donor 0x0b -> global walkable grid; seam profiling;
connected components; coverage vs tok raster."""
import sys
from collections import deque
from pathlib import Path

REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
SCRATCH = Path(__file__).parent
sys.path.insert(0, str(REPO / 'tools'))

from rec02_format import parse_rec02  # noqa
import gen_rec02  # noqa

CS = 0.2
CH = 0.2
TILE = 64
CLIMB = 5


class Mesh:
    """Global-grid view of one 0x0b tileset (set 0)."""

    def __init__(self, path_or_doc, name=''):
        if isinstance(path_or_doc, (str, Path)):
            doc = parse_rec02(Path(path_or_doc).read_bytes(), decompress=True)
        else:
            doc = path_or_doc
        self.name = name
        self.doc = doc
        self.center = tuple(doc['center'])
        self.dims = tuple(doc['dims'])
        self.origin = (self.center[0] - self.dims[0],
                       self.center[1] - self.dims[1],
                       self.center[2] - self.dims[2])
        self.guids = [g.hex() if isinstance(g, (bytes, bytearray)) else g
                      for g in doc['guids']]
        recs = doc['sets'][0]['records']
        self.cells = {}   # (gx,gz) -> (habs, area, cons)
        self.tiles = {}
        for r in recs:
            h = r['hdr']
            tx, ty, hmin = h['tx'], h['ty'], h['hmin']
            self.tiles[(tx, ty)] = r
            hs, ar, co = r['heights'], r['areas'], r['cons']
            for lz in range(TILE):
                base = lz * TILE
                gz = ty * TILE + lz
                for lx in range(TILE):
                    li = base + lx
                    if hs[li] != 0xff and ar[li] != 0:
                        self.cells[(tx * TILE + lx, gz)] = (hmin + hs[li], ar[li], co[li])

    # world <-> grid
    def wx(self, gx):
        return self.origin[0] + (gx + 0.5) * CS

    def wz(self, gz):
        return self.origin[2] + (gz + 0.5) * CS

    def wy(self, habs):
        return self.origin[1] + habs * CH

    def gx(self, wx):
        return int((wx - self.origin[0]) / CS)

    def gz(self, wz):
        return int((wz - self.origin[2]) / CS)

    def components(self):
        """Connected components under the ENGINE model:
        4-adjacency, both walkable, |dh| <= CLIMB (dtBuildTileCacheRegions'
        isConnected uses areas+heights, climb in cell units)."""
        seen = set()
        comps = []
        for start in self.cells:
            if start in seen:
                continue
            q = deque([start])
            seen.add(start)
            comp = []
            while q:
                c = q.popleft()
                comp.append(c)
                h = self.cells[c][0]
                for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    n = (c[0] + dx, c[1] + dz)
                    if n in seen or n not in self.cells:
                        continue
                    if abs(self.cells[n][0] - h) <= CLIMB:
                        seen.add(n)
                        q.append(n)
            comps.append(comp)
        comps.sort(key=len, reverse=True)
        return comps

    def cons_audit(self):
        """Verify cons bytes match the heights/areas adjacency model.
        Returns (n_cells, mismatches list, portal_stats)."""
        mism = []
        n_portal = 0
        n_con = 0
        for (gx, gz), (h, a, co) in self.cells.items():
            lx, lz = gx % TILE, gz % TILE
            for dbit, (dx, dz) in enumerate(((-1, 0), (0, 1), (1, 0), (0, -1))):
                n = (gx + dx, gz + dz)
                expect = n in self.cells and abs(self.cells[n][0] - h) <= CLIMB
                nlx, nlz = lx + dx, lz + dz
                intra = 0 <= nlx < TILE and 0 <= nlz < TILE
                bit_con = bool(co & (1 << dbit))
                bit_portal = bool((co >> 4) & (1 << dbit))
                got = bit_con if intra else bit_portal
                if got != expect:
                    mism.append(((gx, gz), dbit, intra, expect, got))
                n_con += bit_con
                n_portal += bit_portal
        return len(self.cells), mism, dict(con_bits=n_con, portal_bits=n_portal)


def load_tok_raster(lvl_path, erode_iters=(0, 1, 2)):
    """Rasterize a level's tok mesh exactly like gen_rec02.generate does.
    Returns dict with grid meta + hgrid + eroded cell sets per iteration."""
    import math
    guids_a, center_a, dims_a, verts, tris = gen_rec02.load_tok_mesh(str(lvl_path))
    pad = gen_rec02.PAD
    dims = (dims_a[0] + pad, dims_a[1] + pad, dims_a[2] + pad)
    off = pad
    gw = int(math.ceil(2 * dims[0] / CS))
    gh = int(math.ceil(2 * dims[2] / CS))
    hgrid = gen_rec02.rasterize(verts, tris, off, off, off, gw, gh)
    out = dict(center_a=center_a, dims_a=dims_a, dims=dims, gw=gw, gh=gh,
               hgrid=hgrid, nv=len(verts), nt=len(tris), verts=verts, tris=tris)
    full = set(hgrid)
    for it in erode_iters:
        out[f'erode{it}'] = gen_rec02.erode(full, gw, gh, it) if it else full
    return out


def tok_area(verts, tris):
    """Total 2D (x,z-plane) area of the tok triangles, world units^2."""
    s = 0.0
    for a, b, c in tris:
        ax, az = verts[a][0], verts[a][1]
        bx, bz = verts[b][0], verts[b][1]
        cx, cz = verts[c][0], verts[c][1]
        s += abs((bx - ax) * (cz - az) - (bz - az) * (cx - ax)) * 0.5
    return s


def seam_profile(A, B, x_line, z_lo, z_hi, reach=16.0, step=1.0):
    """Profile a NORTH-SOUTH seam at world x=x_line between mesh A (east of
    line) and mesh B (west of line). For each world-z bucket: how close does
    each mesh's walkable area come to the seam line (from ITS side and past
    it), the floor heights adjacent to the line, and the XZ overlap width."""
    rows = []
    z = z_lo
    while z < z_hi:
        z0, z1 = z, z + step
        a_min_x = None; a_y = None
        b_max_x = None; b_y = None
        ov = 0
        # A cells in bucket
        acells = {}
        for (gx, gz), (h, ar, co) in A.cells.items():
            wz = A.wz(gz)
            if z0 <= wz < z1:
                wx = A.wx(gx)
                if abs(wx - x_line) <= reach:
                    acells[(round(wx, 1), round(wz, 1))] = h
                    if a_min_x is None or wx < a_min_x:
                        a_min_x = wx; a_y = A.wy(h)
        for (gx, gz), (h, ar, co) in B.cells.items():
            wz = B.wz(gz)
            if z0 <= wz < z1:
                wx = B.wx(gx)
                if abs(wx - x_line) <= reach:
                    if (round(wx, 1), round(wz, 1)) in acells:
                        ov += 1
                    if b_max_x is None or wx > b_max_x:
                        b_max_x = wx; b_y = B.wy(h)
        rows.append(dict(z=z0, a_reach=a_min_x, a_y=a_y,
                         b_reach=b_max_x, b_y=b_y, overlap=ov))
        z += step
    return rows


def _f(v, fmt='{:.1f}'):
    return fmt.format(v) if v is not None else '-'


def print_seam(rows, x_line, a_name, b_name):
    print(f'  seam x={x_line}  A={a_name} (east)  B={b_name} (west)')
    print(f'  {"z":>7} | {"A minx":>8} {"A y":>6} | {"B maxx":>8} {"B y":>6} | '
          f'{"gap(u)":>7} {"ovl":>4} {"dy":>6}')
    for r in rows:
        gap = (r['a_reach'] - r['b_reach']) if (
            r['a_reach'] is not None and r['b_reach'] is not None) else None
        dy = (r['a_y'] - r['b_y']) if (
            r['a_y'] is not None and r['b_y'] is not None) else None
        print(f"  {r['z']:7.0f} | {_f(r['a_reach']):>8} {_f(r['a_y']):>6} | "
              f"{_f(r['b_reach']):>8} {_f(r['b_y']):>6} | "
              f"{_f(gap):>7} {r['overlap']:>4} {_f(dy, '{:+.1f}'):>6}")
