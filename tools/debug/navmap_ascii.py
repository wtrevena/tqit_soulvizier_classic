#!/usr/bin/env python3
"""ASCII top-down render of a level's 0x0b navmesh + its 0x05 instance overlay.

Built for R-100 #8/#16/#16b (the map-placement lane): the numeric surveys
(`survey_uberboss_spots.py`) answer "is this point ON the mesh and clear?" but they
cannot answer the two questions Will's reports actually turn on:

  * #8  "he is sitting right in front of the den, outside of it" - an enclosure
        question. On-mesh + 10u from the POI marker was TRUE and still WRONG,
        because the marker sits at the den MOUTH, outside the alcove.
  * #16b "the main walking path is never an appropriate place for an uber monster"
        - a corridor-topology question. Needs the SHAPE of the walkable region.

So this renders the walkable cell set as characters and overlays every 0x05
instance, which makes enclosure and corridor structure directly readable.

Frame note (the b36-R4 lesson): 0x05 instance positions and rec02 cell centres are
BOTH grid-LOCAL (world - level grid corner). No +16 fudge belongs anywhere here;
survey_uberboss_spots.build_walk_cells is reused verbatim so this tool cannot drift
from the gate's frame.

Usage:
  py tools/debug/navmap_ascii.py <map.arc> --level <suffix> [--set 0]
      [--x0 A --x1 B --z0 C --z1 D] [--step 1.0] [--mark X,Z,label ...]
"""
import sys
import math
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from contracts_map import parse_0x05, parse_blob_sections  # noqa: E402
from rec02_format import parse_rec02                       # noqa: E402
import survey_uberboss_spots as S                          # noqa: E402

BS = chr(92)
SETNAMES = ['Normal', 'Epic', 'Legendary']

# Instances that do not block or define anything the player reads as geometry.
_NOISE = ('sounds' + BS + 'soundobjects', 'nature' + BS + 'clouds')


def frame_offset(blob, lv):
    """OFF = grid_corner - 0x0b origin, the SAME shift survey_uberboss_spots applies.

    0x05 instance coords are level-LOCAL against the LEVELS-index grid corner; the
    navmesh cell lattice is anchored to the 0x0b container origin (center - dims),
    which on base-game XPack hosts sits a fixed 16u out. Querying a 0x05-local point
    against raw cell coords is exactly the b36 R1-R3 frame bug that mis-read every
    boss spot for three rounds. This tool renders everything in the 0x05-LOCAL frame,
    so cells are shifted by -OFF and instances are drawn unmodified.
    """
    b = S.get_0x0b(blob)
    if b is None:
        raise SystemExit('level has no 0x0b navmesh section')
    doc = parse_rec02(b, decompress=True)
    origin = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
    import struct
    grid_corner = struct.unpack_from('<13i', lv['ints_raw'], 0)[6:9]
    return doc, (grid_corner[0] - origin[0], grid_corner[2] - origin[2])


def walk_set(doc, set_idx):
    """Return (cs, cellmap, comps) for one tileset, in the raw cell frame."""
    cellmap, cs = S.build_indexed_cells(doc, set_idx)
    comps = S.components_of(cellmap)
    return cs, cellmap, comps


def render(blob, lv, set_idx=0, bounds=None, step=1.0, marks=(),
           show_instances=True):
    level_name = lv['fname']
    doc, off = frame_offset(blob, lv)
    cs, cellmap, comps = walk_set(doc, set_idx)
    comp_rank = {}
    for rank, comp in enumerate(comps, 1):
        for c in comp:
            comp_rank[c] = rank

    _, insts = parse_0x05(blob)
    props = [i for i in insts
             if not any(p in i['dbr'].decode('latin1').lower() for p in _NOISE)]

    if bounds is None:
        xs = [(k[0] + 0.5) * cs - off[0] for k in cellmap]
        zs = [(k[1] + 0.5) * cs - off[1] for k in cellmap]
        bounds = (min(xs), max(xs), min(zs), max(zs))
    x0, x1, z0, z1 = bounds

    # Overlay layers, highest priority last.
    overlay = {}
    if show_instances:
        for i in props:
            x, _y, z = i['pos']
            if x0 <= x <= x1 and z0 <= z <= z1:
                d = i['dbr'].decode('latin1').lower()
                if 'clifftiles' in d or 'cliffobj' in d or 'cliffwall' in d:
                    ch = '#'
                elif 'rockobj' in d:
                    ch = 'o'
                elif 'poi' + BS in d:
                    ch = 'P'
                elif 'proxieshades' in d or 'proxies' in d:
                    ch = 'm'
                else:
                    ch = '+'
                overlay[(round(x / step), round(z / step))] = ch
    for (mx, mz, label) in marks:
        overlay[(round(mx / step), round(mz / step))] = label[0]

    nz = int(math.ceil((z1 - z0) / step)) + 1
    nx = int(math.ceil((x1 - x0) / step)) + 1
    print('  level      : %s' % level_name)
    print('  tileset    : %d (%s)   cs=%.3f  cells=%d  components=%d'
          % (set_idx, SETNAMES[set_idx], cs, len(cellmap), len(comps)))
    print('  frame OFF  : %s  (cells drawn in the 0x05-LOCAL frame)' % (off,))
    print('  bounds     : x %.1f..%.1f   z %.1f..%.1f   step=%.2f' % (x0, x1, z0, z1, step))
    print('  legend     : "." walkable(main comp)  "," walkable(other comp)  " " void')
    print('               "#" cliff/wall  "o" rock  "P" POI  "m" monster proxy  "+" other object')
    print('               marks: ' + (', '.join('%s=%s@(%.1f,%.1f)' % (l[0], l, mx, mz)
                                                for mx, mz, l in marks) or '(none)'))
    print()
    # Two ruler lines (tens digit, units digit). PREFIX must match the data rows'
    # 'z=%6.1f ' exactly (9 chars) or every column reads one cell off - the kind of
    # off-by-one that produced the b36 frame-bug wild goose chase.
    PREFIX = ' ' * 9
    xs_axis = [x0 + ix * step for ix in range(nx)]
    print(PREFIX + ''.join(('%d' % (int(round(x)) // 10 % 10)) if abs(x - round(x)) < 1e-6 and int(round(x)) % 10 == 0 else ' '
                           for x in xs_axis))
    print(PREFIX + ''.join(('%d' % (int(round(x)) % 10)) if abs(x - round(x)) < 1e-6 and int(round(x)) % 5 == 0 else ' '
                           for x in xs_axis))
    for iz in range(nz):
        z = z0 + iz * step
        row = []
        for ix in range(nx):
            x = x0 + ix * step
            key = (round(x / step), round(z / step))
            if key in overlay:
                row.append(overlay[key])
                continue
            # 0x05-local -> cell frame (see frame_offset)
            gc = (int(round((x + off[0]) / cs - 0.5)), int(round((z + off[1]) / cs - 0.5)))
            if gc in cellmap:
                row.append('.' if comp_rank.get(gc) == 1 else ',')
            else:
                row.append(' ')
        print('z=%6.1f %s' % (z, ''.join(row)))
    return cs, cellmap, comps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--level', required=True)
    ap.add_argument('--set', type=int, default=0)
    ap.add_argument('--x0', type=float)
    ap.add_argument('--x1', type=float)
    ap.add_argument('--z0', type=float)
    ap.add_argument('--z1', type=float)
    ap.add_argument('--step', type=float, default=1.0)
    ap.add_argument('--mark', action='append', default=[],
                    help='X,Z,LABEL - LABEL[0] is drawn at that cell')
    ap.add_argument('--no-instances', action='store_true')
    a = ap.parse_args()

    data, levels = S.load_world(a.map)
    lv, blob = S.get_blob(data, levels, a.level)
    bounds = None
    if None not in (a.x0, a.x1, a.z0, a.z1):
        bounds = (a.x0, a.x1, a.z0, a.z1)
    marks = []
    for m in a.mark:
        px, pz, label = m.split(',', 2)
        marks.append((float(px), float(pz), label))
    render(blob, lv, a.set, bounds, a.step, marks, not a.no_instances)


if __name__ == '__main__':
    main()
