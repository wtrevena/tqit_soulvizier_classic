#!/usr/bin/env python3
"""Read the FLOOR Y at a level-local (x,z) straight off the 0x0b navmesh.

Every uber placement needs a Y. The repo has historically taken Y from "the nearest
native instance", which is only as good as that native's own anchoring (the Elysian
plan sketch said 1.0 where the meadow is actually 4.0). The navmesh knows the answer
exactly: a dtTileCache cell stores a height index, and

    world_y = (center_y - dims_y) + (hmin + heights[cell]) * ch
    local_y = world_y - grid_corner_y

`--calibrate` proves the formula on this level by reading the Y under existing 0x05
instances and comparing to their authored Y; run it before trusting a new number.

Usage:
  py tools/debug/navmesh_floor_y.py <map.arc> --level <suffix> --pt X,Z [--pt ...]
  py tools/debug/navmesh_floor_y.py <map.arc> --level <suffix> --calibrate
"""
import sys
import math
import struct
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from contracts_map import parse_0x05          # noqa: E402
from rec02_format import parse_rec02          # noqa: E402
import survey_uberboss_spots as S             # noqa: E402

BS = chr(92)


def floor_field(blob, lv, set_idx=0):
    """{(gcx,gcz): local_y}, cs, and the 0x05-local frame offset."""
    doc = parse_rec02(S.get_0x0b(blob), decompress=True)
    origin = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
    gc = struct.unpack_from('<13i', lv['ints_raw'], 0)[6:9]
    off = (gc[0] - origin[0], gc[2] - origin[2])
    s = doc['sets'][set_idx]
    cs = s['params']['cs']
    ch = s['params']['ch']
    out = {}
    for rec in s['records']:
        h = rec['hdr']
        w, ht = h['width'], h['height']
        bx, _by, bz = h['bmin']
        hmin = h['hmin']
        areas, heights = rec['areas'], rec['heights']
        for lz in range(ht):
            row = lz * w
            for lx in range(w):
                idx = row + lx
                if areas[idx] == 0 or heights[idx] == 0xff:
                    continue
                gcx = int(round((bx + (lx + 0.5) * cs) / cs - 0.5))
                gcz = int(round((bz + (lz + 0.5) * cs) / cs - 0.5))
                out[(gcx, gcz)] = origin[1] + (hmin + heights[idx]) * ch - gc[1]
    return out, cs, off, ch


def sample(field, cs, off, x, z, r=2.0):
    """Median local-Y of cells within r of 0x05-local (x,z)."""
    k0 = (int(round((x + off[0]) / cs - 0.5)), int(round((z + off[1]) / cs - 0.5)))
    rr = int(math.ceil(r / cs))
    vals = []
    for dx in range(-rr, rr + 1):
        for dz in range(-rr, rr + 1):
            k = (k0[0] + dx, k0[1] + dz)
            if k in field and dx * dx + dz * dz <= rr * rr:
                vals.append(field[k])
    if not vals:
        return None, 0
    vals.sort()
    return vals[len(vals) // 2], len(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--level', required=True)
    ap.add_argument('--set', type=int, default=0)
    ap.add_argument('--pt', action='append', default=[])
    ap.add_argument('--radius', type=float, default=2.0)
    ap.add_argument('--calibrate', action='store_true')
    a = ap.parse_args()

    data, levels = S.load_world(a.map)
    lv, blob = S.get_blob(data, levels, a.level)
    field, cs, off, ch = floor_field(blob, lv, a.set)
    print('%s  cs=%.3f ch=%.3f  frame OFF=%s  cells=%d'
          % (lv['fname'], cs, ch, off, len(field)))

    if a.calibrate:
        _s, insts = parse_0x05(blob)
        errs = []
        shown = 0
        for i in insts:
            x, y, z = i['pos']
            fy, n = sample(field, cs, off, x, z, 1.0)
            if fy is None:
                continue
            errs.append(abs(fy - y))
            if shown < 12:
                print('   %-58s authored y=%7.2f  navmesh y=%7.2f  d=%5.2f'
                      % (i['dbr'].decode('latin1').split(BS)[-1][:58], y, fy, fy - y))
                shown += 1
        if errs:
            errs.sort()
            print('   CALIBRATION over %d on-mesh instances: median |dy| = %.2f, '
                  'p90 = %.2f  (low = formula correct)'
                  % (len(errs), errs[len(errs) // 2], errs[int(len(errs) * 0.9)]))
        return 0

    for p in a.pt:
        x, z = (float(v) for v in p.split(','))
        fy, n = sample(field, cs, off, x, z, a.radius)
        print('   local(%.1f, %.1f) -> floor Y = %s   (%d cells within %.1fu)'
              % (x, z, ('%.2f' % fy) if fy is not None else 'NO MESH', n, a.radius))
    return 0


if __name__ == '__main__':
    sys.exit(main())
