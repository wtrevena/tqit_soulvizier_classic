#!/usr/bin/env python3
"""build36 MAP WAVE - on-mesh re-survey probe for the new boss placements + the yard.

For a given map .arc + level fname-suffix, decode the level's own 0x0b (RLTD)
navmesh, build the walkable-cell set per difficulty tileset (Normal/Epic/Legendary),
and for each query point report:
  - nearest walkable cell distance (on-mesh if <= ~1 cell)
  - clearance = fraction of a filled disc at `extents` that is walkable

Frame: rec02 center = grid-corner + dims(half-extents); a walkable cell at global
index (gcx,gcz) has grid-LOCAL centre ((gcx+0.5)*cs, (gcz+0.5)*cs), and 0x05
instance positions are ALSO grid-local (world - corner). So query coords are the
LEVEL-LOCAL (x,z) exactly as they go into INJECT_SPECS. Calibration mode surveys
existing native 0x05 instances to prove the frame alignment (their spots must read
on-mesh).

Usage:
  py tools/debug/survey_uberboss_spots.py <map.arc> --bosses
  py tools/debug/survey_uberboss_spots.py <map.arc> --level <suffix> --pt X Z EXT [--pt ...]
  py tools/debug/survey_uberboss_spots.py <map.arc> --level <suffix> --calibrate
  py tools/debug/survey_uberboss_spots.py <map.arc> --yard        # HV01 yard spots
"""
import sys, os, struct, math, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS
from rec02_format import parse_rec02

BS = chr(92)
SETNAMES = ['Normal', 'Epic', 'Legendary']


def load_world(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    return data, levels


def get_blob(data, levels, suffix):
    suffix = suffix.replace(BS, '/').lower()
    for lv in levels:
        k = lv['fname'].replace(BS, '/').lower()
        if k.endswith(suffix):
            return lv, data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    raise SystemExit(f'level {suffix} not found')


def get_0x0b(blob):
    for t, d in parse_blob_sections(blob):
        if t == 0x0b:
            return d
    return None


def native_instances(blob, base):
    """Return [(dbr_str, x, z)] of the level's existing 0x05 instances."""
    for t, d in parse_blob_sections(blob):
        if t != 0x05:
            continue
        pos = 0
        nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
        strings = []
        for _ in range(nstr):
            ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
            strings.append(d[pos:pos + ln]); pos += ln
        ninst = struct.unpack_from('<I', d, pos)[0]; pos += 4
        out = []
        for _ in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            x, y, z = struct.unpack_from('<fff', d, pos + 40)
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            out.append((strings[sid] if sid < len(strings) else b'?', x, z))
            pos += base + (16 if flags != 0 else 0)
        return out
    return []


def build_walk_cells(doc):
    """doc = parse_rec02(decompress=True). Return per-set list of (wx, wz) walkable
    cell centres in grid-LOCAL frame, plus cs, for each of the 3 tilesets.

    A cell is walkable only if areas != 0 AND heights != 0xff. The height (0xff =
    null/hole) check mirrors the engine's dtTileCache model (see navlib.Mesh) - a
    cell over a null-height hole is NOT walkable even if its area byte is nonzero.
    Skipping it here prevents the survey from reporting a spot as clear when it
    actually sits over a hole (survey blind-spot #1)."""
    out = []
    for s in doc['sets']:
        cs = s['params']['cs']
        cells = []
        for rec in s['records']:
            h = rec['hdr']
            w, ht = h['width'], h['height']
            # tile min corner in grid-local frame = header bmin (x,z)
            bx, _, bz = h['bmin']
            areas = rec['areas']
            heights = rec['heights']
            for lz in range(ht):
                row = lz * w
                for lx in range(w):
                    idx = row + lx
                    if areas[idx] != 0 and heights[idx] != 0xff:
                        cells.append((bx + (lx + 0.5) * cs, bz + (lz + 0.5) * cs))
        out.append((cs, cells))
    return out


# --- Absolute-height connected-component model (survey blind-spot #2) ----------
# Mirrors navlib.Mesh.components: a cell's absolute height is hmin+hs (in CH step
# units); two 4-adjacent walkable cells are connected iff |dh| <= CLIMB. Using this
# lets the survey confirm a query spot lands in the MAIN reachable component and not
# on an isolated navmesh island that a raw clearance% would still read as "clear".
COMP_CLIMB = 5   # navlib.CLIMB: 5 CH-steps (= 1.0 world unit at CH=0.2)


def build_indexed_cells(doc, set_idx=0):
    """Return ({(gcx,gcz): habs}, cs) for one tileset in a global integer cell grid
    (gcx = round(cx/cs - 0.5)), null-height holes skipped. habs = hmin+hs (steps)."""
    s = doc['sets'][set_idx]
    cs = s['params']['cs']
    cm = {}
    for rec in s['records']:
        h = rec['hdr']
        w, ht = h['width'], h['height']
        bx, _, bz = h['bmin']
        hmin = h['hmin']
        areas = rec['areas']
        heights = rec['heights']
        for lz in range(ht):
            row = lz * w
            for lx in range(w):
                idx = row + lx
                if areas[idx] != 0 and heights[idx] != 0xff:
                    cx = bx + (lx + 0.5) * cs
                    cz = bz + (lz + 0.5) * cs
                    gcx = int(round(cx / cs - 0.5))
                    gcz = int(round(cz / cs - 0.5))
                    cm[(gcx, gcz)] = hmin + heights[idx]
    return cm, cs


def components_of(cellmap, climb=COMP_CLIMB):
    """Connected components (frozensets of (gcx,gcz)), largest first, engine model."""
    from collections import deque
    seen = set()
    comps = []
    for start in cellmap:
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        comp = []
        while q:
            c = q.popleft()
            comp.append(c)
            hc = cellmap[c]
            for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (c[0] + dx, c[1] + dz)
                if n in seen or n not in cellmap:
                    continue
                if abs(cellmap[n] - hc) <= climb:
                    seen.add(n)
                    q.append(n)
        comps.append(frozenset(comp))
    comps.sort(key=len, reverse=True)
    return comps


def point_component(cellmap, cs, comps, x, z, max_r=6.0):
    """Rank (1=largest) + size of the component the nearest cell to (x,z) belongs to,
    searching within max_r units. Returns (rank, size, dist) or (None, 0, inf)."""
    gcx0 = int(round(x / cs - 0.5))
    gcz0 = int(round(z / cs - 0.5))
    rr = int(math.ceil(max_r / cs))
    best = None
    bestd = 1e18
    for dx in range(-rr, rr + 1):
        for dz in range(-rr, rr + 1):
            key = (gcx0 + dx, gcz0 + dz)
            if key not in cellmap:
                continue
            cx = (key[0] + 0.5) * cs
            cz = (key[1] + 0.5) * cs
            d = (cx - x) ** 2 + (cz - z) ** 2
            if d < bestd:
                bestd = d
                best = key
    if best is None:
        return None, 0, float('inf')
    for rank, comp in enumerate(comps, 1):
        if best in comp:
            return rank, len(comp), math.sqrt(bestd)
    return None, 0, math.sqrt(bestd)


def nearest(cells, x, z):
    best = 1e18
    for (cx, cz) in cells:
        dx = cx - x; dz = cz - z
        d = dx * dx + dz * dz
        if d < best:
            best = d
    return math.sqrt(best)


def clearance(cells, x, z, ext, cs):
    """Fraction of a filled disc (radius ext) around (x,z) whose sample points are
    within ~1 cell of a walkable cell."""
    if not cells:
        return 0.0
    # build a coarse spatial hash for speed
    inv = 1.0 / max(cs, 0.05)
    grid = {}
    for (cx, cz) in cells:
        grid.setdefault((int(cx * inv), int(cz * inv)), True)
    tol = cs * 1.0
    samples = 0; hit = 0
    n = 9
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            sx = x + (i / n) * ext
            sz = z + (j / n) * ext
            if (sx - x) ** 2 + (sz - z) ** 2 > ext * ext:
                continue
            samples += 1
            # check the hash bucket + neighbours
            gx, gz = int(sx * inv), int(sz * inv)
            ok = False
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    if (gx + a, gz + b) in grid:
                        ok = True; break
                if ok:
                    break
            if ok:
                hit += 1
    return hit / samples if samples else 0.0


def survey_level(data, levels, suffix, points, base, calibrate=False):
    lv, blob = get_blob(data, levels, suffix)
    ver = blob[3] if blob[:3] == b'LVL' else None
    b0b = get_0x0b(blob)
    print(f'\n=== {suffix}  (v0x{ver:02x}, 0x05={"present" if any(t==0x05 for t,_ in parse_blob_sections(blob)) else "none"}, '
          f'0x0b={len(b0b) if b0b else 0} B) ===')
    if not b0b:
        print('  NO 0x0b navmesh - cannot survey')
        return None
    doc = parse_rec02(b0b, decompress=True)
    # --- FRAME (R4 fix): 0x05 instance coords are LEVEL-LOCAL relative to the LEVELS-index
    # grid corner (ints_raw[6,7,8]); the 0x0b navmesh's own origin = center - dims can DIFFER
    # from the grid corner (a fixed 16u border on the base-game XPack hosts). The walkable-cell
    # frame (build_walk_cells: cell = bmin + (l+0.5)*cs, bmin = tile*12.8) is anchored to the
    # 0x0b origin, NOT the grid corner. So a 0x05-local query (x,z) must be shifted by
    # OFF = grid_corner - origin before it is compared to the cells. R1-R3 skipped this shift
    # and mis-read every spec-primary as off-mesh/near-wall (the survey narrative was wrong 3
    # rounds running). Native floor-instance calibration in the corrected frame reads ~0-1u.
    origin = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
    grid_corner = struct.unpack_from('<13i', lv['ints_raw'], 0)[6:9]
    off = (grid_corner[0] - origin[0], grid_corner[2] - origin[2])
    print(f'  center={doc["center"]} dims={doc["dims"]} -> origin(0x0b)={origin}')
    print(f'  grid_corner(LEVELS)={grid_corner}  frame OFF(0x05-local -> cell-frame)={off}')
    setcells = build_walk_cells(doc)
    for i, (cs, cells) in enumerate(setcells):
        print(f'  tileset {SETNAMES[i]}: cs={cs} walkable_cells={len(cells)}')
    # Set-0 connected components (absolute-height model) for reachability checks.
    cellmap0, cs0c = build_indexed_cells(doc, 0)
    comps0 = components_of(cellmap0)
    if comps0:
        sizes = ', '.join(str(len(c)) for c in comps0[:4])
        print(f'  set0 components: {len(comps0)} (top sizes: {sizes}'
              f'{" ..." if len(comps0) > 4 else ""})')
    if calibrate:
        insts = native_instances(blob, base)
        cs0, cells0 = setcells[0]
        # Frame validation: floor-anchored native instances (POI/containers/proxies/
        # setdressing/sound) must read on-mesh in the offset-corrected frame. The median
        # nearest is the gate - if OFF is right it is ~0-1u; in the RAW (unshifted) frame it
        # is ~the offset magnitude. Report BOTH so the frame fix is auditable.
        floor = [(d, x, z) for (d, x, z) in insts if any(
            k in d for k in (b'poi', b'containers', b'proxies', b'setdress', b'soundobject'))]
        def _med(shift):
            ds = sorted(nearest(cells0, x + shift[0], z + shift[1]) for (_, x, z) in floor)
            return ds[len(ds) // 2] if ds else float('nan')
        print(f'  CALIBRATION: {len(insts)} native 0x05 instances, {len(floor)} floor-anchors.')
        print(f'    median nearest RAW(unshifted)={_med((0,0)):.2f}u  '
              f'OFFSET-CORRECTED(+{off})={_med(off):.2f}u  (lower = true frame)')
        for (dbr, x, z) in insts[:8]:
            d = nearest(cells0, x + off[0], z + off[1])
            print(f'    {dbr.decode(errors="replace")[:52]:52s} local({x:.1f},{z:.1f})  nearest(corr)={d:.2f}u')
        return None
    results = []
    for (label, x, z, ext) in points:
        # offset-corrected query: 0x05-local -> cell frame (see FRAME note above)
        qx, qz = x + off[0], z + off[1]
        wx, wz = grid_corner[0] + x, grid_corner[2] + z
        line = [f'  {label}: local({x},{z}) world({wx:.1f},{wz:.1f}) ext={ext}']
        allok = True
        for i, (cs, cells) in enumerate(setcells):
            d = nearest(cells, qx, qz)
            clr = clearance(cells, qx, qz, ext, cs)
            onmesh = d <= cs * 2.5
            allok = allok and onmesh and clr >= 0.95
            line.append(f'{SETNAMES[i][0]}:d={d:.2f}/clr={clr*100:.0f}%')
        # Reachability: the nearest set-0 cell must belong to the MAIN component
        # (rank 1). A clear-but-isolated island spot (rank > 1) now reads CHECK.
        rank, size, _cd = point_component(cellmap0, cs0c, comps0, qx, qz)
        if rank is None:
            line.append('comp=NONE')
            allok = False
        else:
            line.append(f'comp#{rank}/{size}')
            if rank != 1:
                allok = False
        verdict = 'OK' if allok else 'CHECK'
        print('  '.join(line) + f'   -> {verdict}')
        results.append((label, allok, x, z))
    return results


# The 5 build36 boss spots (level suffix, [(label,x,z,extents)]); extents = proxy placementExtents.
# build36 FINAL placements (re-surveyed + nudged on the built map; extents = proxy placementExtents).
# Each PRIMARY below is the SHIPPED coord in UBERBOSS_SPECS; the pre-nudge spec coord is kept as
# a labelled reference so the gate shows the before/after.
# R4: shipped coord = the spec-primary (the R1-R3 "nudges" were driven by the 16u frame bug
# fixed above; every spec-primary is on-mesh clr 100% in the corrected frame). M6 keeps the
# spec's FORECOURT fallback (the summit ring is genuinely tight - 82% on Legendary). The old
# nudge is kept as a labelled reference so the gate shows before/after.
BOSS_SPOTS = [
    ('area02_medea/undergrounds/medea_templeug_tomb01.lvl',
     [('M4 Dorus SPEC-PRIMARY (shipped)', 52.0, 60.0, 4.0), ('M4 R3-nudge (reverted)', 49.0, 63.0, 4.0)]),
    ('area04_styx/styx_swampborder_01.lvl',
     [('M5 Tantalus SPEC-PRIMARY (shipped)', 54.0, 114.3, 3.5), ('M5 R3-nudge (reverted)', 50.0, 116.0, 3.5)]),
    ('area04_styx/styx_riveredge_01.lvl',
     [('M6 GoldenBough FORECOURT-spec (shipped)', 187.9, 46.9, 3.5), ('M6 SUMMIT-spec (tight, 82% Leg)', 217.7, 12.5, 3.5)]),
    ('area05_judgment/undergrounds/judgment_templeug_mnemosyne01.lvl',
     [('M7 Mnemophage SPEC-PRIMARY (shipped)', 43.0, 71.0, 3.5), ('M7 Mnemophage ALT-B', 41.0, 61.0, 3.5)]),
    ('area05_judgment/undergrounds/judgment_stonecity_exit01.lvl',
     [('M8 Ephialtes SPEC-PRIMARY (shipped)', 15.9, 34.7, 3.5), ('M8 R3-nudge (reverted)', 22.0, 45.0, 3.5)]),
]

WARDEN_SPOTS = [
    ('greece/startingtownver2/startingfarmland06d.lvl',
     [('M3 Helos warden FINAL (R5 clean)', 72.0, 184.0, 3.0),
      ('M3 Helos warden R4 (near-wall 64/51/42%, reverted)', 64.5, 189.5, 3.0),
      ('Almyros (ref)', 76.5, 189.5, 3.0)]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--level')
    ap.add_argument('--pt', nargs=3, action='append', type=float, metavar=('X', 'Z', 'EXT'))
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--bosses', action='store_true')
    ap.add_argument('--warden', action='store_true')
    ap.add_argument('--yard', action='store_true')
    ap.add_argument('--base', type=int, default=72)
    args = ap.parse_args()

    data, levels = load_world(args.map)

    if args.bosses:
        for suffix, pts in BOSS_SPOTS:
            survey_level(data, levels, suffix, pts, 72)
        return
    if args.warden:
        for suffix, pts in WARDEN_SPOTS:
            survey_level(data, levels, suffix, [(l, x, z, e) for (l, x, z, e) in pts], 72)
        return
    if args.yard:
        # HV01 = Silk Road (single tileset region); survey a broad grid for the respace.
        survey_level(data, levels, 'orient/silkroad/hiddenvalley01.lvl', [], 72, calibrate=True)
        return
    if args.level:
        if args.calibrate:
            survey_level(data, levels, args.level, [], args.base, calibrate=True)
        else:
            pts = [(f'pt{i}', p[0], p[1], p[2]) for i, p in enumerate(args.pt or [])]
            survey_level(data, levels, args.level, pts, args.base)
        return
    ap.error('need --bosses / --warden / --yard / --level')


if __name__ == '__main__':
    main()
