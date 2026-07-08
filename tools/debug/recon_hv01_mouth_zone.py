#!/usr/bin/env python3
"""Zoom on the HV01 cave-mouth zone: enumerate EVERY 0x05 instance within a radius of the
cave-mouth GridEntrance (local 14,18,26), and map the walkable-mesh shape immediately
around the mouth so we can pick a Toxeus spot on the natural approach/exit path.
Read-only. No em dashes."""
import sys, struct, math
from pathlib import Path

REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from diag_bugs import load_map, get_level_blob, parse_blob_sections, parse_0x05, walk_instances
from rec02_format import parse_rec02
from navlib import Mesh

HV01_KEY = 'levels/world/orient/silkroad/hiddenvalley01.lvl'
MOUTH = (14.0, 18.0, 26.0)  # local, verified GridEntrance SilkRdDngEntrance_C01_Ext


def get_level(levels, fname):
    for l in levels:
        if l['fname'].replace('\\', '/').lower() == fname:
            return l
    return None


def main():
    arc_path = REPO / 'local' / 'Levels_merged_TESTHUB.arc'
    data, name = load_map(arc_path)
    secs = parse_sections(data)
    levels = parse_level_index(data, next(s for s in secs if s['type'] == SEC_LEVELS))
    lv = get_level(levels, HV01_KEY)
    ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
    corner = (ints[6], ints[7], ints[8])
    blob = get_level_blob(data, levels, None, lv)
    blobsecs, magic = parse_blob_sections(blob)
    sec05 = next(s for s in blobsecs if s['type'] == 0x05)
    strings, instmeta = parse_0x05(sec05['data'])
    insts, _, _ = walk_instances(magic, strings, instmeta)

    print(f'HV01 corner={corner}, mouth local={MOUTH} world='
          f'({corner[0]+MOUTH[0]:.1f},{corner[1]+MOUTH[1]:.1f},{corner[2]+MOUTH[2]:.1f})')

    # Every instance within 40u (2D) of the mouth, sorted by distance.
    print('\n=== ALL 0x05 instances within 40u (2D) of the cave mouth ===')
    near = []
    for it in insts:
        d = math.hypot(it['x'] - MOUTH[0], it['z'] - MOUTH[2])
        if d <= 40.0:
            near.append((d, it))
    near.sort(key=lambda t: t[0])
    for d, it in near:
        print(f'  d2d={d:6.2f}u  local=({it["x"]:7.2f},{it["y"]:6.2f},{it["z"]:7.2f}) '
              f'flags={it["flags"]}  {it["dbr"]}')

    # Mesh shape around the mouth: which local cells are walkable in a box around it.
    nav = next(s for s in blobsecs if s['type'] == 0x0b)
    doc = parse_rec02(nav['data'], decompress=True)
    mesh = Mesh(doc, name='HV01')
    comps = mesh.components()
    largest = set(comps[0])

    print('\n=== Walkable map around the mouth (local X 0..45, Z 8..55), "." off-mesh, "#" on largest ===')
    # sample every 1.5u
    zc = 8.0
    header = '     ' + ''.join(f'{int(x):>3}' for x in range(0, 46, 3))
    print(header + '   (local X ->)')
    while zc <= 55.0:
        row = f'{zc:5.0f}'
        xc = 0.0
        while xc <= 45.0:
            wx, wz = corner[0] + xc, corner[2] + zc
            gx, gz = mesh.gx(wx), mesh.gz(wz)
            ch = ' . '
            if (gx, gz) in largest:
                ch = ' # '
            elif (gx, gz) in mesh.cells:
                ch = ' o '
            # mark the mouth
            if abs(xc - MOUTH[0]) < 1.5 and abs(zc - MOUTH[2]) < 1.5:
                ch = ' M '
            row += ch
            xc += 3.0
        print(row)
        zc += 3.0

    # For a line of candidate spots radiating OUT from the mouth (increasing X and Z,
    # i.e. into the valley/approach), report on-mesh + floor Y + clearance to the mouth.
    print('\n=== Candidate Toxeus spots: radiate from mouth along approach ===')

    def onmesh(lx, ly, lz, R=40):
        wx, wy, wz = corner[0] + lx, corner[1] + ly, corner[2] + lz
        gx, gz = mesh.gx(wx), mesh.gz(wz)
        best = None
        for dz in range(-R, R + 1):
            for dx in range(-R, R + 1):
                c = (gx + dx, gz + dz)
                if c in mesh.cells:
                    cwx, cwz = mesh.wx(c[0]), mesh.wz(c[1])
                    cwy = mesh.wy(mesh.cells[c][0])
                    dd = math.hypot(cwx - wx, cwz - wz)
                    if best is None or dd < best[0]:
                        best = (dd, cwy - wy, c, cwx, cwy, cwz)
        return best

    for (lx, lz) in [(18, 30), (20, 32), (22, 34), (24, 34), (20, 26), (24, 26), (26, 30),
                     (22, 30), (18, 26), (16, 32), (20, 38), (24, 40), (28, 34), (22, 26)]:
        b = onmesh(lx, 18.0, lz)
        if not b:
            print(f'  local({lx},{lz}): no mesh')
            continue
        dd, dy, c, cwx, cwy, cwz = b
        in_l = c in largest
        dmouth = math.hypot((cwx - corner[0]) - MOUTH[0], (cwz - corner[2]) - MOUTH[2])
        print(f'  local({lx},{lz}) -> cell local=({cwx-corner[0]:6.2f},{cwy-corner[1]:6.2f},'
              f'{cwz-corner[2]:6.2f}) d2d={dd:.2f} dY={dy:+.2f} in_largest={in_l} d_mouth={dmouth:.1f}u')


if __name__ == '__main__':
    main()
