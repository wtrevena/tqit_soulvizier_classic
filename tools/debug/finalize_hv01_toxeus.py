#!/usr/bin/env python3
"""Finalize the Toxeus spawn coord in HV01: for a chosen local (X,Z), snap to the exact
on-mesh floor, report dY (on-mesh 0.000-0.5u gate), and ENUMERATE all required distances
(fountain/caravan/occult-FX/friendly-NPC/A1 portals >=25u; mouth + nearest beastman for
design). Read-only. No em dashes.

Usage: finalize_hv01_toxeus.py [X Z]   (default 21.9 31.9)
"""
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
MOUTH = (14.0, 18.0, 26.0)

# Friendly scenery/NPC anchors the brief requires >=25u standoff from (must not wipe them).
# Enumerated from recon: the whole camp scene is at the NORTH end (Z~143), villager4 at Z~103.
FRIENDLY_NEEDLES = ['respawntempleorient', 'caravan', 'fog_occult', 'occultistaura',
                    'disciple_aura', 'merchant', 'occulttent', 'vendor',
                    'npc\\speaking', 'npc/speaking', 'villager', 'storyteller',
                    'pitspawner', 'lildude', 'pitsprite', 'olympianarena', 'campfire',
                    'totem']
BEASTMAN_NEEDLES = ['beastman', 'neanderthal', 'encact', 'proxies orient', 'proxies boss']


def get_level(levels, fname):
    for l in levels:
        if l['fname'].replace('\\', '/').lower() == fname:
            return l
    return None


def main():
    lx = float(sys.argv[1]) if len(sys.argv) > 1 else 21.9
    lz = float(sys.argv[2]) if len(sys.argv) > 2 else 31.9

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
    for it in insts:
        it['wx'] = corner[0] + it['x']; it['wy'] = corner[1] + it['y']; it['wz'] = corner[2] + it['z']

    nav = next(s for s in blobsecs if s['type'] == 0x0b)
    doc = parse_rec02(nav['data'], decompress=True)
    mesh = Mesh(doc, name='HV01')
    comps = mesh.components()
    largest = set(comps[0])

    # Snap chosen local -> nearest walkable cell in the LARGEST component; report its floor.
    wx, wz = corner[0] + lx, corner[2] + lz
    gx, gz = mesh.gx(wx), mesh.gz(wz)
    best = None
    for dz in range(-30, 31):
        for dx in range(-30, 31):
            c = (gx + dx, gz + dz)
            if c in largest:
                cwx, cwz = mesh.wx(c[0]), mesh.wz(c[1])
                dd = math.hypot(cwx - wx, cwz - wz)
                if best is None or dd < best[0]:
                    best = (dd, c, cwx, cwz, mesh.wy(mesh.cells[c][0]))
    dd, cell, cwx, cwz, floor_wy = best
    # Choose the FINAL spawn: the chosen local X,Z, with Y = mesh floor (so dY -> 0 exactly).
    floor_ly = floor_wy - corner[1]
    spawn_local = (lx, round(floor_ly, 2), lz)
    spawn_world = (corner[0] + spawn_local[0], corner[1] + spawn_local[1], corner[2] + spawn_local[2])

    print(f'HV01 corner={corner}')
    print(f'CHOSEN local (X,Z) = ({lx},{lz})  -> nearest LARGEST-comp cell '
          f'local=({cwx-corner[0]:.2f},{floor_ly:.2f},{cwz-corner[2]:.2f}) d2d_snap={dd:.2f}u')
    print(f'FINAL SPAWN local = ({spawn_local[0]:.2f},{spawn_local[1]:.2f},{spawn_local[2]:.2f})  '
          f'world=({spawn_world[0]:.2f},{spawn_world[1]:.2f},{spawn_world[2]:.2f})')

    # On-mesh gate: nearest walkable cell to the FINAL spawn (2D) + dY vs floor.
    sgx, sgz = mesh.gx(spawn_world[0]), mesh.gz(spawn_world[2])
    b2 = None
    for dz in range(-20, 21):
        for dx in range(-20, 21):
            c = (sgx + dx, sgz + dz)
            if c in mesh.cells:
                cwx, cwz = mesh.wx(c[0]), mesh.wz(c[1])
                cwy = mesh.wy(mesh.cells[c][0])
                dd2 = math.hypot(cwx - spawn_world[0], cwz - spawn_world[2])
                if b2 is None or dd2 < b2[0]:
                    b2 = (dd2, cwy - spawn_world[1], c, cwx, cwy, cwz)
    d2d, dY, cell2, _, _, _ = b2
    print(f'\n=== ON-MESH GATE ===')
    print(f'  nearest walkable cell d2d={d2d:.3f}u  dY={dY:+.3f}u  in_largest_comp={cell2 in largest}  '
          f'area={mesh.cells[cell2][1]}')
    print(f'  GATE d2d<=0.5: {"PASS" if d2d <= 0.5 else "FAIL"}   '
          f'|dY|<=0.5: {"PASS" if abs(dY) <= 0.5 else "FAIL"}')

    # Distances
    def d2(it):
        return math.hypot(it['wx'] - spawn_world[0], it['wz'] - spawn_world[2])

    print(f'\n=== DISTANCE TO CAVE MOUTH ===')
    mouth_w = (corner[0] + MOUTH[0], corner[1] + MOUTH[1], corner[2] + MOUTH[2])
    dmouth = math.hypot(mouth_w[0] - spawn_world[0], mouth_w[2] - spawn_world[2])
    print(f'  mouth local(14,18,26) -> d2d={dmouth:.2f}u  (right outside; player meets him)')

    print(f'\n=== FRIENDLY SCENERY/NPC DISTANCES (gate: ALL >= 25u) ===')
    friendlies = []
    for it in insts:
        dl = it['dbr'].lower()
        if any(n in dl for n in FRIENDLY_NEEDLES):
            friendlies.append(it)
    if not friendlies:
        print('  (none found)')
    worst = 1e9
    for it in sorted(friendlies, key=d2):
        dv = d2(it)
        worst = min(worst, dv)
        flag = 'OK' if dv >= 25.0 else 'VIOLATION'
        print(f'  d2d={dv:8.2f}u  [{flag}]  local=({it["x"]:.2f},{it["y"]:.2f},{it["z"]:.2f})  {it["dbr"]}')
    print(f'  --> MIN friendly distance = {worst:.2f}u  '
          f'GATE(>=25u): {"PASS" if worst >= 25.0 else "FAIL"}')

    print(f'\n=== NEAREST HOSTILE (beastman) PROXIES (design context, not a gate) ===')
    hostiles = [it for it in insts if any(n in it['dbr'].lower() for n in BEASTMAN_NEEDLES)]
    for it in sorted(hostiles, key=d2)[:5]:
        print(f'  d2d={d2(it):8.2f}u  local=({it["x"]:.2f},{it["y"]:.2f},{it["z"]:.2f})  {it["dbr"]}')


if __name__ == '__main__':
    main()
