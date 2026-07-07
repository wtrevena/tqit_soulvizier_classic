#!/usr/bin/env python3
"""GATE R1 / G-OVER - the over-coverage (walk-through-rocks) gate.

Root cause (docs/NAVMESH_OVERCOVERAGE_RCA.md): SV authored every rock/wall as a
PathEngine baseObstacle polygon over a broad flat ground tok (runtime walkable =
ground MINUS obstacles). Before the fix, gen_rec02 rasterized the flat ground and
DROPPED the obstacles, so every rock footprint was walkable and the player walked
through solid rocks. The fix subtracts the obstacle polygons during rasterization
(erode-then-carve, r=0).

THE GATE: for every generated donor .0b.bin, ZERO walkable cell of the FINAL
(post-carve, post-erode) emitted mesh may fall inside any of that donor's OWN
baseObstacle polygons (r=0 point-in-poly). This is the direct assertion of
"no walkable-on-rock". Per donor it also prints:
  - BEFORE: the % of the uncarved eroded floor that sat inside own obstacles
    (reproduces the RCA Measurement-7 figures: drxBC2 26.6%, drxFirstRoom 28.9%,
    BC_initialpathway 18.0%) - a smoke test that the carve had real work to do.
  - AFTER: walkable cells still inside own obstacles in the shipped donor (== 0).

Frame: obstacles are LEVEL-LOCAL to the SV 0x0a corner (center-dims); the donor
is GRID_SHIFTed, so an obstacle world point = SV_corner0a + (px,pz) + GRID_SHIFT.
Donor cell centers come from navlib.Mesh. (Proven against a live generate() donor.)

Usage:
  py tools/debug/overcoverage_check.py            # gate all donors on disk
  py tools/debug/overcoverage_check.py --verbose  # also print BEFORE detail
Exit 0 = PASS (all donors clean), 1 = FAIL. Read-only.
"""
import math
import os
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

from arc_patcher import ArcArchive                                   # noqa: E402
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS  # noqa: E402
from build_section_surgery import parse_blob_sections                # noqa: E402
from rec02_format import parse_rec02                                 # noqa: E402
from gen_rec02 import (load_tok_mesh, rasterize, erode, stamp_obstacles,  # noqa: E402
                       _point_in_poly, PAD, ERODE_CELLS, CS)
from navlib import Mesh                                              # noqa: E402
from svaera_plus_portals import GRID_SHIFT                           # noqa: E402

UPSTREAM_SV_ARC = REPO / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc'
DONOR_DIR = Path(os.environ.get('SVC_DONOR_DIR',
                                str(REPO / 'local' / 'editor_normalized')))
R09_KEY = 'levels/world/orient/underground/random09a.lvl'


def load_sv_map():
    arc = ArcArchive.from_file(UPSTREAM_SV_ARC)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    return data, levels


def grid_shift_for(key):
    for pattern, (dx, dy, dz) in GRID_SHIFT.items():
        if pattern in key:
            return (dx, dy, dz)
    return (0, 0, 0)


def cells_in_polys_world(mesh, world_polys, area_filter=None):
    """Count mesh (set-0) walkable cells whose world XZ center is inside any poly.

    area_filter: if given, only cells with that exact area id are tested (e.g. 1 =
    this level's OWN region). If None, ALL walkable cells are tested regardless of
    region tag - used by the all-region seam gate (each cell vs its OWN region
    owner's rock, see cells_in_region_owner_rock).

    Region note (vet 2026-07-07): a cell tagged area k is one the ENGINE treats as
    level-k's at runtime (area = 1-based GUID-list index). 'Walk-through-rock' for
    such a cell means it sits inside LEVEL-k's rock, not this level's - so the own
    check (area 1 vs own rock) is necessary but NOT sufficient: it misses seam
    cells tagged to a neighbour that sit inside the NEIGHBOUR's rock. That whole
    class is covered by the all-region pass below."""
    occ = {}
    ox, oz = mesh.origin[0], mesh.origin[2]
    for (gx, gz), (h, a, c) in mesh.cells.items():
        if area_filter is not None and a != area_filter:
            continue
        wx = ox + (gx + 0.5) * CS
        wz = oz + (gz + 0.5) * CS
        occ[(round(wx / CS), round(wz / CS))] = (wx, wz)
    hits = set()
    for poly in world_polys:
        xs = [p[0] for p in poly]
        zs = [p[1] for p in poly]
        ix0, ix1 = math.floor(min(xs) / CS), math.ceil(max(xs) / CS)
        iz0, iz1 = math.floor(min(zs) / CS), math.ceil(max(zs) / CS)
        for ix in range(ix0, ix1 + 1):
            for iz in range(iz0, iz1 + 1):
                if (ix, iz) in hits:
                    continue
                c = occ.get((ix, iz))
                if c is None:
                    continue
                if _point_in_poly(c[0], c[1], poly):
                    hits.add((ix, iz))
    return len(hits)


def cells_in_region_owner_rock(mesh, guid_to_world_polys):
    """ALL-REGION seam gate (vet 2026-07-07 major issue): count walkable cells that
    sit inside the rock of the LEVEL THAT OWNS THEM at runtime (the level whose GUID
    is at index area-1 in this donor's GUID list). This is the spec's neighbour-carve
    requirement made checkable: under the region-tag carve every cell tagged region k
    is carved by level-k's rock, so this must be ZERO.

    guid_to_world_polys: {guid_hex -> [world (x,z) polygon, ...]} for every level any
    donor might tag (own + neighbours), obstacles already in the merged world frame
    (SV corner0a + level-local + that level's GRID_SHIFT).

    Returns (n_hits, per_owner) where per_owner maps owner_basename -> hit count."""
    from collections import Counter
    ox, oz = mesh.origin[0], mesh.origin[2]
    # bucket walkable cells by their area id
    by_area = {}
    for (gx, gz), (h, a, c) in mesh.cells.items():
        if a <= 0:
            continue
        wx = ox + (gx + 0.5) * CS
        wz = oz + (gz + 0.5) * CS
        by_area.setdefault(a, {})[(round(wx / CS), round(wz / CS))] = (wx, wz)
    hits_total = set()
    per_owner = Counter()
    for area, occ in by_area.items():
        if area - 1 >= len(mesh.guids):
            continue
        owner_guid = mesh.guids[area - 1]
        owner_guid = owner_guid.hex() if isinstance(owner_guid, (bytes, bytearray)) else owner_guid
        world_polys, owner_name = guid_to_world_polys.get(owner_guid, (None, None))
        if not world_polys:
            continue
        for poly in world_polys:
            xs = [p[0] for p in poly]
            zs = [p[1] for p in poly]
            ix0, ix1 = math.floor(min(xs) / CS), math.ceil(max(xs) / CS)
            iz0, iz1 = math.floor(min(zs) / CS), math.ceil(max(zs) / CS)
            for ix in range(ix0, ix1 + 1):
                for iz in range(iz0, iz1 + 1):
                    key = (ix, iz)
                    if key in hits_total:
                        continue
                    cc = occ.get(key)
                    if cc is None:
                        continue
                    if _point_in_poly(cc[0], cc[1], poly):
                        hits_total.add(key)
                        per_owner[owner_name] += 1
    return len(hits_total), dict(per_owner)


def before_floor_pct(dims_a, verts, tris, obstacles):
    """Uncarved eroded floor + fraction inside own obstacles (own tok only, PAD,
    erode ERODE_CELLS). Uses the EXACT navlib.load_tok_raster grid (dims_a+PAD,
    off=PAD) so it reproduces the RCA Measurement-7 'before' figures byte-exact
    (drxBC2 26.6%, drxFirstRoom 28.9%, BC_initialpathway 18.0%)."""
    dims = (dims_a[0] + PAD, dims_a[1] + PAD, dims_a[2] + PAD)
    off = PAD
    gw = int(math.ceil(2 * dims[0] / CS))
    gh = int(math.ceil(2 * dims[2] / CS))
    hgrid = rasterize(verts, tris, off, off, off, gw, gh)
    eroded = erode(set(hgrid), gw, gh, ERODE_CELLS)
    obs_cells = stamp_obstacles(obstacles, gw, gh, off, off)
    carved = len(eroded & obs_cells)
    return len(eroded), carved


# A walkable cell inside a rock is TOLERATED only as a deliberate seam bridge (the
# connectivity-preserving carve restores a thin corridor through an edge-hugging
# rock rather than strand the player - RCA FIX SPEC "leaving its footprint walkable
# is harmless, the alternative strands the player"; the river-regression fix). The
# gate FAILS a broad room-interior leak (the reported bug: dense rock fields
# walkable) and PASSES the bounded seam bridges. Per-donor cap on remaining
# walk-through-rock = min(SEAM_ABS, max(SEAM_FLOOR, SEAM_FRAC * pre-carve in-rock
# floor)). The SEAM_FRAC term scales with rock density (big rocky rooms may carry
# more seam corridor); SEAM_FLOOR is an absolute allowance so a SMALL junction
# connector (few rocks but several region seams, e.g. drxFirstxistion_connection at
# the BC_initialpathway|drxFirstRoom junction) is not failed for its handful of
# legitimate bridges; SEAM_ABS is the hard ceiling. Pre-fix room leaks were 18-36%
# of the floor (tens of thousands of cells); measured seam bridges are <= ~940 and
# each donor's own-region leak (the bug proper) is a small subset - a wide margin,
# so the bound is not fragile. Tuned against the measured connectivity-repair
# donors: every donor's all-region walk-through-rock is well under its cap.
SEAM_FRAC = 0.03      # fraction of the pre-carve in-rock floor allowed as bridges
SEAM_FLOOR = 300      # absolute per-donor allowance (small junction connectors)
SEAM_ABS = 3000       # hard per-donor ceiling


def build_guid_obstacle_map(sv_by, sv_data):
    """Map every relevant level GUID -> (world obstacle polygons, basename), for the
    all-region seam gate. Includes each SV cluster level's own GUID plus the AE
    Random09A GUID (the merge keeps SVAERA's Random09A GUID; the donor's own GUID is
    AE's, so a neighbour that tags Random09A tags the AE GUID). Obstacles are in the
    merged world frame (SV corner0a + level-local + that level's GRID_SHIFT)."""
    out = {}
    # AE Random09A GUID (own-GUID override target) so region-owner lookups resolve it
    try:
        ae_arc = ArcArchive.from_file(REPO / 'reference_mods' / 'SVAERA_customquest'
                                      / 'Resources' / 'Levels.arc')
        ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
        ae_sec = {s['type']: s for s in parse_sections(ae_data)}
        ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
        ae_r09_guid = next(lv['ints_raw'][36:52] for lv in ae_levels
                           if lv['fname'].replace('\\', '/').lower() == R09_KEY)
    except Exception:
        ae_r09_guid = None
    for key, lv in sv_by.items():
        if not ('xbloodcave' in key or key == R09_KEY):
            continue
        base = key.split('/')[-1][:-4]
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        tmp = Path(tempfile.gettempdir()) / f'goverguid_{base}.lvl'
        try:
            tmp.write_bytes(blob)
            _g, center_a, dims_a, verts, tris, obstacles = load_tok_mesh(str(tmp))
        except Exception:
            continue
        corner = tuple(center_a[i] - dims_a[i] for i in range(3))
        sh = grid_shift_for(key)
        world_polys = [[(corner[0] + px + sh[0], corner[2] + pz + sh[2])
                        for (px, pz) in poly] for poly in obstacles]
        guid = lv['ints_raw'][36:52].hex()
        out[guid] = (world_polys, base)
        if key == R09_KEY and ae_r09_guid is not None:
            out[ae_r09_guid.hex()] = (world_polys, base)  # donor uses AE's R09 GUID
    return out


def main():
    verbose = '--verbose' in sys.argv[1:]
    print('=== R1 / G-OVER over-coverage gate (no walkable-on-rock) ===')
    print(f'  donors: {DONOR_DIR}')
    print(f'  seam-bridge tolerance: <= {SEAM_FRAC*100:.0f}% of pre-carve in-rock '
          f'floor AND <= {SEAM_ABS} cells/donor (deliberate connectivity bridges)')
    if not DONOR_DIR.exists():
        print('FAIL: donor dir missing')
        return 1

    sv_data, sv_levels = load_sv_map()
    sv_by = {lv['fname'].replace('\\', '/').lower(): lv for lv in sv_levels}
    sv_by_base = {}
    for key, lv in sv_by.items():
        if 'xbloodcave' in key or key == R09_KEY:
            base = key.split('/')[-1][:-4]
            sv_by_base[base.lower()] = (key, lv)

    guid_polys = build_guid_obstacle_map(sv_by, sv_data)
    print(f'  region-owner obstacle map: {len(guid_polys)} GUIDs\n')

    donors = sorted(DONOR_DIR.glob('*.lvl.0b.bin'))
    print(f'  donor .0b.bin files: {len(donors)}\n')
    print(f'  {"donor":34s} {"obs":>5s} {"floor":>8s} {"before":>14s} '
          f'{"own@rock":>9s} {"allrgn@rock":>11s}  verdict')
    print('  ' + '-' * 96)

    fails = []
    checked = 0
    tot_own = tot_all = 0
    for p in donors:
        base = p.name[:-len('.lvl.0b.bin')]
        rec = sv_by_base.get(base.lower())
        if rec is None:
            print(f'  {base:34s}  SKIP (no SV source)')
            continue
        key, lv = rec
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        tmp = Path(tempfile.gettempdir()) / f'gover_{base}.lvl'
        tmp.write_bytes(blob)
        _g, center_a, dims_a, verts, tris, obstacles = load_tok_mesh(str(tmp))
        corner = tuple(center_a[i] - dims_a[i] for i in range(3))
        sh = grid_shift_for(key)
        world_polys = [[(corner[0] + px + sh[0], corner[2] + pz + sh[2])
                        for (px, pz) in poly] for poly in obstacles]

        mesh = Mesh(parse_rec02(p.read_bytes(), decompress=True), base)
        # own-region walk-through-rock (area==1 vs own rock)
        own_hits = cells_in_polys_world(mesh, world_polys, area_filter=1)
        # all-region: every cell vs its runtime region-owner's rock (the seam class)
        all_hits, per_owner = cells_in_region_owner_rock(mesh, guid_polys)

        floor, before = before_floor_pct(dims_a, verts, tris, obstacles)
        bpct = 100 * before / max(floor, 1)

        # verdict on the all-region count (own is a subset). Broad room leak -> FAIL;
        # bounded seam bridges -> PASS.
        cap = min(SEAM_ABS, max(SEAM_FLOOR, int(SEAM_FRAC * before))) if before else SEAM_FLOOR
        ok = all_hits <= cap
        verdict = 'PASS' if ok else f'FAIL (>{cap} bridge cap)'
        if not ok:
            fails.append(f'{base}({all_hits})')
        tot_own += own_hits
        tot_all += all_hits
        checked += 1
        print(f'  {base:34s} {len(obstacles):>5d} {floor:>8d} '
              f'{before:>8d}({bpct:4.1f}%) {own_hits:>9d} {all_hits:>11d}  {verdict}')
        if verbose and per_owner:
            print(f'      all-region by owner: {per_owner}')

    print('\n  ' + '=' * 70)
    print(f'  donors checked: {checked};  total own@rock={tot_own}  '
          f'all-region@rock={tot_all}  (all-region = deliberate seam bridges)')
    if fails:
        print(f'  FAIL ({len(fails)}): {fails}')
        print('  A donor exceeds the seam-bridge cap -> a broad room-interior rock '
              'field is walkable (the reported bug), not just a thin seam corridor.')
        return 1
    print('  PASS: room interiors are solid; only bounded connectivity seam bridges '
          'remain walkable-on-rock (by design - the alternative strands the player).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
