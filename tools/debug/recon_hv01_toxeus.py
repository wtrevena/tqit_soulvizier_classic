#!/usr/bin/env python3
"""RECON for placing Toxeus (q_bloodtoxeus_lone proxy) OUTSIDE the blood-cave entrance
in HiddenValley01 (HV01), TESTHUB-only.

Read-only. No em dashes.

Dumps:
  - HV01 blob version (must confirm v0x11 -> base-72 0x05 record) + grid corner.
  - EVERY 0x05 instance (dbr, local, world, flags, size) so we can locate the cave-mouth
    GridEntrance, the fountain, caravan, occultist, sprites, and any friendly NPC.
  - EVERY 0x14 record (index + payload hex) so we can find the GridEntrance cave-mouth
    binding and read the destination GUID it warps to (Random09A / blood cave).
  - The 0x0b navmesh (Editor-baked) parsed via navlib.Mesh: cells, components, largest
    component world bounds.
  - For a set of candidate spawn points near the cave mouth: nearest walkable cell,
    dist2d, dY, in-largest-comp, + distance to fountain/caravan/occultist/sprites/NPCs.
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
RANDOM09A_GUID = 'd840e7ae4a42c504453f13a47940bc55'


def get_level(levels, fname):
    for l in levels:
        if l['fname'].replace('\\', '/').lower() == fname:
            return l
    return None


def parse_0x14(data):
    """0x14 = variable records: index(4) + payload_size(4) + payload."""
    recs = []
    pos = 0
    while pos + 8 <= len(data):
        idx = struct.unpack_from('<I', data, pos)[0]
        psize = struct.unpack_from('<I', data, pos + 4)[0]
        if pos + 8 + psize > len(data):
            break
        payload = data[pos + 8:pos + 8 + psize]
        recs.append((idx, payload))
        pos += 8 + psize
    return recs


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'testhub'
    if which == 'testhub':
        arc_path = REPO / 'local' / 'Levels_merged_TESTHUB.arc'
    elif which == 'merged':
        arc_path = REPO / 'local' / 'Levels_merged.arc'
    elif which == 'deployed':
        arc_path = REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Levels.arc'
    else:
        arc_path = Path(which)
    print(f'MAP = {arc_path}')
    data, name = load_map(arc_path)
    secs = parse_sections(data)
    levels = parse_level_index(data, next(s for s in secs if s['type'] == SEC_LEVELS))

    lv = get_level(levels, HV01_KEY)
    ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
    corner = (ints[6], ints[7], ints[8])
    guid = lv['ints_raw'][36:52].hex()
    blob = get_level_blob(data, levels, None, lv)
    blobsecs, magic = parse_blob_sections(blob)
    ver = magic[3]
    print(f'HV01 blob version = v0x{ver:02x}  (base-72 record if 0x11)')
    print(f'HV01 grid corner (world x,y,z) = {corner}')
    print(f'HV01 merged GUID = {guid}')
    print(f'sections = {[hex(s["type"]) for s in blobsecs]}')

    sec05 = next(s for s in blobsecs if s['type'] == 0x05)
    strings, instmeta = parse_0x05(sec05['data'])
    insts, endpos, dlen = walk_instances(magic, strings, instmeta)
    print(f'0x05: {len(strings)} strings, {instmeta[0]} instances, trailing={dlen-endpos}')
    for it in insts:
        it['wx'] = corner[0] + it['x']; it['wy'] = corner[1] + it['y']; it['wz'] = corner[2] + it['z']

    # 0x14
    sec14 = next((s for s in blobsecs if s['type'] == 0x14), None)
    x14 = parse_0x14(sec14['data']) if sec14 else []
    x14_by_idx = {idx: pl for idx, pl in x14}
    print(f'0x14: {len(x14)} records')

    # --- Locate GridEntrance instances (cave mouths) + their 0x14 dest GUID ---
    print('\n=== GridEntrance / portal / cave-mouth instances (0x05 + their 0x14) ===')
    for it in insts:
        d = it['dbr'].lower()
        if ('gridentrance' in d or 'portal' in d or 'entrance' in d or 'random09' in d
                or 'cave' in d or 'grid' in d):
            pl = x14_by_idx.get(it['i'])
            plhex = pl.hex() if pl else None
            destguid = None
            if pl and len(pl) >= 48:
                destguid = pl[32:48].hex()
            print(f'  [inst {it["i"]}] {it["dbr"]}')
            print(f'      local=({it["x"]:.3f},{it["y"]:.3f},{it["z"]:.3f}) '
                  f'world=({it["wx"]:.1f},{it["wy"]:.1f},{it["wz"]:.1f}) flags={it["flags"]} size={it["size"]}')
            print(f'      0x14={plhex}')
            if destguid:
                tag = ' == RANDOM09A (blood cave)!' if destguid == RANDOM09A_GUID else ''
                print(f'      0x14 dest_guid={destguid}{tag}')

    # --- Any 0x14 record whose payload references the Random09A GUID (cave-mouth binding) ---
    print('\n=== 0x14 records referencing RANDOM09A GUID (blood-cave doorway) ===')
    for idx, pl in x14:
        if RANDOM09A_GUID in pl.hex():
            owner = next((it for it in insts if it['i'] == idx), None)
            od = owner['dbr'] if owner else '?'
            ol = f'local=({owner["x"]:.2f},{owner["y"]:.2f},{owner["z"]:.2f})' if owner else ''
            print(f'  0x14 idx={idx} -> {od} {ol}')
            print(f'      payload={pl.hex()}')

    # --- Entity inventory: fountain / caravan / occultist / sprites / NPCs / friendlies ---
    print('\n=== KEY SCENERY / NPC INSTANCES ===')
    KEYS = {
        'fountain/shrine': ['respawntempleorient', 'shrine'],
        'caravan': ['caravan'],
        'occultist merchant': ['merchant', 'occulttent', 'vendor', 'stall'],
        'occult FX/aura': ['occultistaura', 'fog_occult', 'disciple_aura'],
        'sprites (pit)': ['pitspawner', 'lildude', 'pitsprite'],
        'NPC (speaking)': ['npc\\speaking', 'npc/speaking', 'villager', 'storyteller'],
        'A1 door portal': ['olympianarena'],
    }
    found = {}
    for tag, needles in KEYS.items():
        hits = [it for it in insts if any(n in it['dbr'].lower() for n in needles)]
        found[tag] = hits
        print(f'  --- {tag}: {len(hits)} ---')
        for h in hits:
            print(f'      {h["dbr"]}')
            print(f'        local=({h["x"]:.3f},{h["y"]:.3f},{h["z"]:.3f}) '
                  f'world=({h["wx"]:.1f},{h["wy"]:.1f},{h["wz"]:.1f}) flags={h["flags"]}')

    # --- Navmesh ---
    nav = next((s for s in blobsecs if s['type'] == 0x0b), None)
    print(f'\n=== HV01 0x0b navmesh: size={nav["size"] if nav else "NONE"} ===')
    if not nav:
        print('  NO 0x0b! cannot on-mesh check')
        return
    doc = parse_rec02(nav['data'], decompress=True)
    mesh = Mesh(doc, name='HV01')
    print(f'  mesh center={mesh.center} dims={mesh.dims}')
    print(f'  mesh origin={mesh.origin}')
    print(f'  guids in nav: {mesh.guids}')
    comps = mesh.components()
    largest = set(comps[0]) if comps else set()
    print(f'  cells={len(mesh.cells)} comps={len(comps)} largest={len(largest)}')
    if largest:
        xs = [mesh.wx(c[0]) for c in largest]; zs = [mesh.wz(c[1]) for c in largest]
        ys = [mesh.wy(mesh.cells[c][0]) for c in largest]
        print(f'  largest-comp world bounds: X[{min(xs):.1f},{max(xs):.1f}] '
              f'Y[{min(ys):.1f},{max(ys):.1f}] Z[{min(zs):.1f},{max(zs):.1f}]')
        print(f'  largest-comp local bounds:  X[{min(xs)-corner[0]:.1f},{max(xs)-corner[0]:.1f}] '
              f'Z[{min(zs)-corner[2]:.1f},{max(zs)-corner[2]:.1f}]')

    def nearest_walkable(wx, wy, wz, R=80):
        gx, gz = mesh.gx(wx), mesh.gz(wz)
        best = None
        for dz in range(-R, R + 1):
            for dx in range(-R, R + 1):
                c = (gx + dx, gz + dz)
                if c in mesh.cells:
                    cwx, cwz = mesh.wx(c[0]), mesh.wz(c[1])
                    cwy = mesh.wy(mesh.cells[c][0])
                    d2 = math.hypot(cwx - wx, cwz - wz)
                    if best is None or d2 < best[0]:
                        best = (d2, cwy - wy, (cwx, cwy, cwz), c)
        return best

    # Reference points for distance enumeration (world)
    refs = {}
    for tag in ['fountain/shrine', 'caravan', 'occultist merchant', 'occult FX/aura',
                'sprites (pit)', 'NPC (speaking)']:
        for h in found.get(tag, []):
            refs[f'{tag}:{h["dbr"].split(chr(92))[-1]}'] = (h['wx'], h['wy'], h['wz'])

    # Candidate cave-mouth-ish local coords to test (verify against real mouth found above).
    # Old notes: mouth ~ local (14,18,26). We test a fan around it.
    print('\n=== CANDIDATE SPAWN POINTS near cave mouth (local) ===')
    cands = []
    for cx in [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]:
        for cz in [18, 22, 26, 30, 34, 38]:
            cands.append((cx, 18.0, cz))
    for (lx, ly, lz) in cands:
        wx, wy, wz = corner[0] + lx, corner[1] + ly, corner[2] + lz
        b = nearest_walkable(wx, wy, wz)
        if b is None:
            continue
        d2, dy, cw, cell = b
        if d2 > 3.0:
            continue
        in_l = cell in largest
        # distances to references (2D)
        dmin = min((math.hypot(cw[0] - rx, cw[2] - rz) for (rx, ry, rz) in refs.values()),
                   default=999)
        print(f'  local~({lx},{ly},{lz}) -> on-mesh cell world=({cw[0]:.1f},{cw[1]:.1f},{cw[2]:.1f}) '
              f'local=({cw[0]-corner[0]:.2f},{cw[1]-corner[1]:.2f},{cw[2]-corner[2]:.2f}) '
              f'd2d={d2:.2f} dY={dy:+.2f} in_largest={in_l} min_ref_dist={dmin:.1f}u')

    print('\n=== REFERENCE POINTS (for distance enumeration) ===')
    for k, (rx, ry, rz) in refs.items():
        print(f'  {k}: world=({rx:.1f},{ry:.1f},{rz:.1f}) local=({rx-corner[0]:.2f},{ry-corner[1]:.2f},{rz-corner[2]:.2f})')


if __name__ == '__main__':
    main()
