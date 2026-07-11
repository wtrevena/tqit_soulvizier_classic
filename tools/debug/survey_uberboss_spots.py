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
    cell centres in grid-LOCAL frame, plus cs, for each of the 3 tilesets."""
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
            for lz in range(ht):
                row = lz * w
                for lx in range(w):
                    if areas[row + lx] != 0:
                        cells.append((bx + (lx + 0.5) * cs, bz + (lz + 0.5) * cs))
        out.append((cs, cells))
    return out


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
    corner = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
    print(f'  center={doc["center"]} dims={doc["dims"]} -> corner(world)={corner}')
    setcells = build_walk_cells(doc)
    for i, (cs, cells) in enumerate(setcells):
        print(f'  tileset {SETNAMES[i]}: cs={cs} walkable_cells={len(cells)}')
    if calibrate:
        insts = native_instances(blob, base)
        print(f'  CALIBRATION vs {len(insts)} native instances (nearest walkable cell dist, Normal set):')
        cs0, cells0 = setcells[0]
        shown = 0
        for (dbr, x, z) in insts:
            if shown >= 8:
                break
            d = nearest(cells0, x, z)
            print(f'    {dbr.decode(errors="replace")[:52]:52s} local({x:.1f},{z:.1f})  nearest={d:.2f}u')
            shown += 1
        return None
    results = []
    for (label, x, z, ext) in points:
        line = [f'  {label}: local({x},{z}) ext={ext}']
        allok = True
        for i, (cs, cells) in enumerate(setcells):
            d = nearest(cells, x, z)
            clr = clearance(cells, x, z, ext, cs)
            onmesh = d <= cs * 2.5
            allok = allok and onmesh and clr >= 0.95
            line.append(f'{SETNAMES[i][0]}:d={d:.2f}/clr={clr*100:.0f}%')
        verdict = 'OK' if allok else 'CHECK'
        print('  '.join(line) + f'   -> {verdict}')
        results.append((label, allok, x, z))
    return results


# The 5 build36 boss spots (level suffix, [(label,x,z,extents)]); extents = proxy placementExtents.
# build36 FINAL placements (re-surveyed + nudged on the built map; extents = proxy placementExtents).
# Each PRIMARY below is the SHIPPED coord in UBERBOSS_SPECS; the pre-nudge spec coord is kept as
# a labelled reference so the gate shows the before/after.
BOSS_SPOTS = [
    ('area02_medea/undergrounds/medea_templeug_tomb01.lvl',
     [('M4 Dorus PRIMARY (nudged)', 49.0, 63.0, 4.0), ('M4 Dorus spec(pre-nudge)', 52.0, 60.0, 4.0)]),
    ('area04_styx/styx_swampborder_01.lvl',
     [('M5 Tantalus PRIMARY (nudged)', 50.0, 116.0, 3.5), ('M5 Tantalus spec(pre-nudge)', 54.0, 114.3, 3.5)]),
    ('area04_styx/styx_riveredge_01.lvl',
     [('M6 GoldenBough FORECOURT (nudged)', 185.0, 48.0, 3.5), ('M6 GoldenBough SUMMIT (alt)', 219.0, 14.0, 3.5)]),
    ('area05_judgment/undergrounds/judgment_templeug_mnemosyne01.lvl',
     [('M7 Mnemophage PRIMARY', 43.0, 71.0, 3.5), ('M7 Mnemophage ALT-B', 41.0, 61.0, 3.5)]),
    ('area05_judgment/undergrounds/judgment_stonecity_exit01.lvl',
     [('M8 Ephialtes PRIMARY (nudged)', 22.0, 45.0, 3.5), ('M8 Ephialtes spec(pre-nudge)', 15.9, 34.7, 3.5)]),
]

WARDEN_SPOTS = [
    ('greece/startingtownver2/startingfarmland06d.lvl',
     [('M3 Helos warden FINAL', 64.5, 189.5, 3.0), ('M3 Helos warden draft(86, bad)', 86.0, 189.5, 3.0),
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
