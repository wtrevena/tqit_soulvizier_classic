#!/usr/bin/env python3
"""GATE - TRAVEL Y-VS-TERRAIN + ON-MESH (R-248 proven-mechanism travel, 2026-08-14).

LINEAGE: the Y1/ON checks of the retired gate_device_resolution (R-246; the device
half of that gate died with the devices - WILL_RULINGS R-248, MODDING_PLAYBOOK sec
10/10a). The Y-vs-terrain LAW survives the device world: it kills the buried/floating
class (tantalus at Y=-12, the sunken SC2 spots, the boss_arena dais 27-vs-28.1) for
every placed travel NPC and every SVC boat destination.

CHECKS (on a BUILT map arc, either variant):
  Y1  every PLACED travel NPC (svc_helos_trav_* / svc_area_return_* /
      svc_testhub_return_* / svc_warden_* / portal_master_helos - derived live from
      build_section_surgery's INJECT_SPECS + hub folds, never hand-listed) asserts
      |y - floorCal| <= 0.5u, where floorCal = the host blob's 0x0b height at that
      cell + a per-level calibration (median native-entity offset; lights/fx/devices
      excluded, |off| <= 3).
  Y2  every SVC-authored Action_BoatDialog DEST coord (Almyros's 3 rows +
      build_quest_files' R248 step tables; TESTHUB rows under --hub) asserts the
      same law after world -> local conversion via the host level's grid corner.
  ON  every checked coordinate is ON-MESH (nearest walkable cell <= 0.5u, area != 0).

Usage:
  py tools/gate_travel_y_terrain.py --map <Levels.arc> [--hub] [--negtest]
Exit 0 = PASS. Read-only.
"""
import argparse
import math
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

from arc_patcher import ArcArchive                      # noqa: E402
from merge_levels_binary import parse_sections          # noqa: E402
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS  # noqa: E402
from rec02_format import parse_rec02                    # noqa: E402

BS = chr(92)
Y_TOL = 0.5
ONMESH_TOL = 0.5
# Placed-record prefixes that ARE the travel-NPC surface (Y1 scope).
TRAVEL_PREFIXES = ('svc_helos_trav_', 'svc_area_return_', 'svc_testhub_return_',
                   'svc_warden_', 'portal_master_helos')
# Almyros's 3 dests carry no level key in HELOS_PORTAL_DESTS; mapped here by tag.
ALMYROS_DEST_LEVELS = {
    'tagSVCHelosToGarden': 'levels/world/olympus/gardenofmerchants.lvl',
    'tagSVCHelosToSecret': 'xpack/levels/secret_place/darkforestenter.lvl',
    'tagSVCHelosToUber': 'levels/world/uberdungeon/crypt_floor1.lvl',
}


def load_map(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    return data, levels


def level_by_suffix(levels, key):
    k = key.replace(BS, '/').lower()
    for lv in levels:
        if lv['fname'].replace(BS, '/').lower() == k:
            return lv
    return None


def parse_0x05(blob):
    """[(dbr_lc, x, y, z, flags, uid_or_None, idx)]"""
    base = 72 if blob[3] in (0x11, 0x0f) else 56
    out = []
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
        for i in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            x, y, z = struct.unpack_from('<fff', d, pos + 40)
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            uid = bytes(d[pos + 56:pos + 72]) if flags != 0 else None
            nm = strings[sid].replace(b'/', BS.encode()).lower().decode('ascii', 'replace')
            out.append((nm, x, y, z, flags, uid, i))
            pos += base + (16 if flags != 0 else 0)
    return out


class Mesh:
    """0x0b walkable-cell frame + floorCal for one level (migrated verbatim from the
    retired gate_device_resolution: survey R4 frame fix + R-246 calibration = median
    native-entity offset, lights/fx/devices excluded)."""

    def __init__(self, lv, blob, instances):
        d0b = None
        for t, d in parse_blob_sections(blob):
            if t == 0x0b:
                d0b = d
        self.ok = bool(d0b)
        if not self.ok:
            return
        doc = parse_rec02(d0b, decompress=True)
        ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
        origin = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
        self.offx = ints[6] - origin[0]
        self.offz = ints[8] - origin[2]
        self.y_datum = origin[1] - ints[7]
        s0 = doc['sets'][0]
        self.cs = s0['params']['cs']
        self.ch = s0['params']['ch']
        self.cm = {}
        for rec in s0['records']:
            h = rec['hdr']
            w, ht = h['width'], h['height']
            bx, _, bz = h['bmin']
            hmin = h['hmin']
            areas, heights = rec['areas'], rec['heights']
            for lz in range(ht):
                row = lz * w
                for lx in range(w):
                    idx = row + lx
                    if areas[idx] != 0 and heights[idx] != 0xff:
                        cx = bx + (lx + 0.5) * self.cs
                        cz = bz + (lz + 0.5) * self.cs
                        self.cm[(int(round(cx / self.cs - 0.5)),
                                 int(round(cz / self.cs - 0.5)))] = hmin + heights[idx]
        offs = []
        maxr = int(2.0 / self.cs)
        for (nm, ix, iy, iz, _f, _u, _i) in instances:
            if any(k in nm for k in ('svc_', 'portal_olympianarena', 'map_portal_aura',
                                     'teleportshrine', 'light', 'fx', 'sound')):
                continue
            bc = self._near_cell(ix, iz, maxr)
            if bc is None:
                continue
            off = iy - (self.y_datum + self.cm[bc] * self.ch)
            if abs(off) <= 3.0:
                offs.append(off)
        offs.sort()
        self.cal = offs[len(offs) // 2] if offs else 0.0

    def _near_cell(self, x, z, maxr):
        cx, cz = x + self.offx, z + self.offz
        gx, gz = int(round(cx / self.cs - 0.5)), int(round(cz / self.cs - 0.5))
        for r in range(maxr + 1):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if max(abs(dx), abs(dz)) == r and (gx + dx, gz + dz) in self.cm:
                        return (gx + dx, gz + dz)
        return None

    def onmesh_dist(self, x, z):
        bc = self._near_cell(x, z, int(6.0 / self.cs))
        if bc is None:
            return 999.0
        cx, cz = x + self.offx, z + self.offz
        bx = (bc[0] + 0.5) * self.cs
        bz = (bc[1] + 0.5) * self.cs
        return max(0.0, math.hypot(bx - cx, bz - cz) - self.cs * 0.71)

    def floor_cal(self, x, z):
        bc = self._near_cell(x, z, int(6.0 / self.cs))
        if bc is None:
            return None
        return self.y_datum + self.cm[bc] * self.ch + self.cal


def expected_placements(hub):
    """{(level_key, dbr_basename): (x, y, z)} derived LIVE from the map tooling tables."""
    import build_section_surgery as bss
    specs = bss.merge_hub_into_inject_specs(bss.INJECT_SPECS) if hub else bss.INJECT_SPECS
    out = {}
    for key, entries in specs.items():
        for s in entries:
            rec = s if isinstance(s, (bytes, bytearray)) else s[0]
            nm = bytes(rec).replace(b'/', BS.encode()).lower().decode()
            base = nm.rsplit(BS, 1)[-1]
            if any(base.startswith(p) for p in TRAVEL_PREFIXES):
                _r, x, y, z = (None, s[1], s[2], s[3])
                out[(key.replace(BS, '/').lower(), base)] = (float(x), float(y), float(z))
    return out


def expected_dests(hub):
    """[(tag, level_key, (wx, wy, wz))] from build_quest_files' live tables."""
    import build_quest_files as bqf
    dests = []
    for (xyz, tag) in bqf.HELOS_PORTAL_DESTS:
        dests.append((f'almyros:{tag}', ALMYROS_DEST_LEVELS[tag], xyz))
    steps = list(bqf.R248_CANONICAL_STEPS) + (list(bqf.R248_TESTHUB_STEPS) if hub else [])
    for (_sname, rows) in steps:
        for (npc, xyz, tag, lk) in rows:
            short = npc.rsplit(BS, 1)[-1].replace('.dbr', '')
            dests.append((f'{short}:{tag}', lk, xyz))
    return dests


def run_gate(map_path, hub, verbose=True):
    data, levels = load_map(map_path)
    viols = []
    mesh_cache = {}
    blob_cache = {}

    def get(key):
        k = key.replace(BS, '/').lower()
        if k not in blob_cache:
            lv = level_by_suffix(levels, k)
            if lv is None:
                blob_cache[k] = (None, None, None)
            else:
                blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
                blob_cache[k] = (lv, blob, parse_0x05(blob))
        return blob_cache[k]

    def get_mesh(key):
        k = key.replace(BS, '/').lower()
        if k not in mesh_cache:
            lv, blob, inst = get(k)
            mesh_cache[k] = Mesh(lv, blob, inst) if blob else None
        return mesh_cache[k]

    def check(tag, key, lx, ly, lz):
        mesh = get_mesh(key)
        if mesh is None:
            viols.append(f'{tag}: host level {key} missing from map')
            return
        if not mesh.ok:
            viols.append(f'Y {tag}: host {key} has no 0x0b navmesh')
            return
        f = mesh.floor_cal(lx, lz)
        if f is None:
            viols.append(f'Y {tag}: no walkable cell near ({lx},{lz}) in {key}')
        elif abs(ly - f) > Y_TOL:
            viols.append(f'Y {tag}: y={ly} vs floorCal={f:.2f} in {key} '
                         f'(|dy|={abs(ly - f):.2f} > {Y_TOL}) - the buried/floating class')
        d = mesh.onmesh_dist(lx, lz)
        if d > ONMESH_TOL:
            viols.append(f'ON {tag}: ({lx},{lz}) is OFF-MESH in {key} (d={d:.2f})')

    # Y1: placed travel NPCs (local coords straight from the tables; the placements in
    # the BUILT blob are separately asserted by gate_testhub_portal_rig's census).
    placements = expected_placements(hub)
    for ((key, base), (x, y, z)) in sorted(placements.items()):
        check(f'npc {base}@{key.split("/")[-1]}({x},{z})', key, x, y, z)

    # Y2: SVC boat dests (world -> local via the host level's grid corner).
    n_dests = 0
    for (tag, key, (wx, wy, wz)) in expected_dests(hub):
        lv, _blob, _inst = get(key)
        if lv is None:
            viols.append(f'Y2 dest {tag}: host level {key} missing from map')
            continue
        ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
        check(f'dest {tag}', key, wx - ints[6], wy - ints[7], wz - ints[8])
        n_dests += 1

    if viols:
        print(f'TRAVEL Y-VS-TERRAIN GATE ({"TESTHUB" if hub else "canonical"}): '
              f'{len(viols)} VIOLATION(S)')
        for v in viols:
            print(f'  FAIL {v}')
        return False
    print(f'TRAVEL Y-VS-TERRAIN GATE ({"TESTHUB" if hub else "canonical"}): PASS - '
          f'{len(placements)} placed travel NPCs + {n_dests} SVC boat dests all at '
          f'floorCal Y (|dy|<={Y_TOL}) and on-mesh (<={ONMESH_TOL})')
    return True


def negtest(map_path, hub):
    """Planted defects on in-memory table copies must each RED the gate."""
    import io
    import contextlib
    import build_quest_files as bqf

    def run_quiet():
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            return run_gate(map_path, hub)

    ok = True
    base = run_quiet()
    if not base:
        print('  NEGTEST positive control FAILED (base map does not pass)')
        return False
    print('  [GREEN OK] positive control passes')

    # N1 buried BOAT DEST: sink the uber enter dest by 3u (the pre-R-248 tantalus class)
    step_name, rows = bqf.R248_CANONICAL_STEPS[0]
    saved = rows[0]
    rows[0] = (saved[0], (saved[1][0], saved[1][1] - 3, saved[1][2]), saved[2], saved[3])
    r = run_quiet()
    rows[0] = saved
    print(f'  [{"RED   OK" if not r else "FAIL"}] buried boat dest (uber enter y-3)')
    ok &= (not r)

    # N2 off-mesh dest: shove the garden-return Helos dest 40u into the void
    step_name2, rows2 = bqf.R248_CANONICAL_STEPS[2]
    saved2 = rows2[0]
    rows2[0] = (saved2[0], (saved2[1][0] + 4000, saved2[1][1], saved2[1][2]),
                saved2[2], saved2[3])
    r = run_quiet()
    rows2[0] = saved2
    print(f'  [{"RED   OK" if not r else "FAIL"}] off-mesh boat dest (+4000u x)')
    ok &= (not r)

    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', required=True)
    ap.add_argument('--hub', action='store_true')
    ap.add_argument('--negtest', action='store_true')
    args = ap.parse_args()
    if args.negtest:
        sys.exit(0 if negtest(args.map, args.hub) else 1)
    sys.exit(0 if run_gate(args.map, args.hub) else 1)


if __name__ == '__main__':
    main()
