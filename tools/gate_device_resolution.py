#!/usr/bin/env python3
"""GATE - R-246 DEVICE RESOLUTION + Y-VS-TERRAIN (native-device travel, 2026-08-13).

Runs on a BUILT map arc (either variant). The device inventory is DERIVED from
build_section_surgery's R-246 tables (never hand-listed), so a table edit and the
built map can never drift apart silently.

CHECKS
  D1  every expected DOOR ENTRANCE (portal_olympianarena1) exists exactly once at its
      spec spot with a 60-byte 0x14 = (2,0,1) prefix + mouth+exit+destGUID matching the
      minted constants; its co-located map_portal_aura swirl exists.
  D2  every expected LANDING (portal_olympianarena2) exists exactly once with a 48-byte
      0x14 = mouth(==its entrance's exit)+32 zero bytes.
  D3  every entrance's dest GUID resolves in the LEVELS index, and the paired landing
      lives in EXACTLY that level.
  D4  minted-UID global uniqueness: each mouth uid appears exactly once in the whole
      map file; each exit uid exactly twice (entrance 0x14 + landing 0x14); shrine uids
      exactly twice (0x05 instance + GROUPS member).
  D5  APPENDED-HOST LAW, structural: every door ENTRANCE host is in the named
      ORIGINAL-INDEX allowlist (live-proven 2026-07-08 discriminator).
  D6  every SHRINE: 0x05 flags=1 + 16B minted uid + a GROUPS 'TeleportShrine' record
      whose member is uid+hostLevelGUID+pos == the 0x05 pos (Duister/Garden byte-law);
      canonical map carries exactly the 2 canonical shrines, TESTHUB all 11.
  D7  VARIANT SEPARATION: the canonical map contains ZERO hub-only device UIDs / GROUPS
      names (the TESTHUB-never-reaches-Steam law, structurally).
  C1-C5 TRAFFIC-LANE/CLEARANCE (the SURVIVING half of the 2026-07-12 P0; B-PORTAL-2):
      court door planes >= 4.1u pairwise; every door plane >= 6.69u from every CLICKABLE
      npc (R-246 mute markers excluded - they ARE the label surface); every landing +
      shrine clear of placed collidables per the proven b44 CLASS_MIN model; shrines
      >= 5u from their co-level landing; the catacube entrance >= 8u off stairsdown01.
  Y1  Y-VS-TERRAIN: every device instance (entrances, landings, shrines, swirls), every
      R-246 marker NPC, and every SVC-authored BoatDialog dest coord asserts
      |y - floorCal| <= 0.5u, where floorCal = the destination blob's 0x0b height at
      that cell + a per-level calibration = median (entityY - floor0x0b) over native
      floor anchors (svc_*/portal/aura/shrine/light/fx excluded; |off|<=3). This kills
      the buried-NPC class (tantalus/warband/sparta/secret named offenders green).
  ON  every landing + shrine is ON-MESH (nearest walkable cell <= 0.5u, area != 0).

Usage:
  py tools/gate_device_resolution.py --map <Levels.arc> [--hub] [--arz <arz>] [--negtest]
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
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

from arc_patcher import ArcArchive                      # noqa: E402
from merge_levels_binary import parse_sections          # noqa: E402
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS  # noqa: E402
from rec02_format import parse_rec02                    # noqa: E402
import build_section_surgery as bss                     # noqa: E402
import gate_landing_clearance as glc                    # noqa: E402  (proven b44 collision model)

BS = chr(92)
SEC_GROUPS = 0x11
Y_TOL = 0.5
ONMESH_TOL = 0.5

# D5: ORIGINAL-INDEX door-entrance hosts (live-proven 2026-07-08: entrances in appended
# SV-only levels NEVER fire). Extend ONLY with a new live proof.
ALLOWED_ENTRANCE_HOSTS = {
    bss.MAZE03_LVL_KEY,
    bss.CATACUBE_FLOORLAST_LVL_KEY,
    bss.HELOS_HOST_KEY,          # startingfarmland06d (v0x11 hosting live-proven, old H1)
}

# Native/pre-existing devices the inventory must TOLERATE (whitelisted, never faulted):
#   crypt_floor1 inert SV-native portal_olympianarena2 (mouth 6e513e90..) - ships since P0;
#   the Garden teleportshrine_gom + RogueEncampment/Duister shrine (native TeleportShrine).
NATIVE_LANDING_MOUTHS = {bytes.fromhex('6e513e901549b1d558db968c61bda66a')}

# ── C-block: TRAFFIC-LANE / CLEARANCE (the half of the 2026-07-12 P0 that SURVIVES R-246:
# doors OFF every traffic lane, walked into deliberately; B-PORTAL-2). Collision model =
# the PROVEN b44 gate_landing_clearance CLASS_MIN (per-class center-to-center minimums,
# live-calibrated by Will's land-in-chest reports) - deliberately REUSED rather than
# minting a stricter parallel law (the brief's flat ">=3u prop" would newly outlaw the
# b44-documented, accepted devourer pitwedge 2.83u; CLASS_MIN prop=2.5 is the ratified
# line, and N5 proves this scanner sees that exact prop).
COURT_MIN_PAIRWISE = 4.1     # court door planes, pairwise (R-246 court law)
DOOR_MIN_CLICKABLE = 6.69    # any door plane to any CLICKABLE npc (Almyros law)
SHRINE_MIN_LANDING = 5.0     # shrine standoff from its co-level landing (C5/C7/T15)
STAIRS_MIN = 8.0             # catacube entrance off the stairsdown01 traffic funnel
# R-246 device/marker records: excluded from clearance targets (deliberate adjacency -
# markers ARE the label surface; post-rip they are MUTE, hence not 'clickable').
_R246_OWN = ('portal_olympianarena', 'map_portal_aura', 'teleportshrine',
             'svc_helos_trav', 'svc_area_return', 'svc_testhub_return', 'svc_warden')


def load_map(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    gsec = secs[SEC_GROUPS]
    groups_raw = data[gsec['data_offset']:gsec['data_offset'] + gsec['size']]
    return data, levels, groups_raw


def level_by_suffix(levels, key):
    k = key.replace(BS, '/').lower()
    for lv in levels:
        if lv['fname'].replace(BS, '/').lower() == k:
            return lv
    return None


def parse_0x05(blob):
    """[(dbr_lc, x, y, z, flags, uid_or_None, idx)] + base size."""
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
    return out, base


def parse_0x14(blob):
    """{instance_index: payload_bytes}"""
    out = {}
    for t, d in parse_blob_sections(blob):
        if t != 0x14:
            continue
        pos = 0
        while pos + 8 <= len(d):
            idx, psz = struct.unpack_from('<II', d, pos)
            out[idx] = bytes(d[pos + 8:pos + 8 + psz])
            pos += 8 + psz
    return out


class Mesh:
    """0x0b walkable-cell frame + floorCal for one level (survey R4 frame fix +
    R-246 calibration: median native-entity offset, lights/fx/devices excluded)."""

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
        # calibration
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


def parse_groups_shrine_members(groups_raw):
    """{group_name: (uid, level_guid, (x,y,z))} for SVC R-246 shrine records."""
    out = {}
    for spec in bss.R246_SHRINE_SPECS:
        nb = spec['group_name'].encode('ascii')
        off = groups_raw.find(nb)
        if off < 0:
            continue
        # record layout: sub_count(4) name_len(4) name cat_len(4) cat member_count(4) raw
        p = off + len(nb)
        cat_len = struct.unpack_from('<I', groups_raw, p)[0]
        cat = groups_raw[p + 4:p + 4 + cat_len].decode('ascii', 'replace')
        p2 = p + 4 + cat_len
        member_count = struct.unpack_from('<I', groups_raw, p2)[0]
        raw = groups_raw[p2 + 4:p2 + 4 + 64]
        uid = raw[0:16]
        guid = raw[16:32]
        pos = struct.unpack_from('<3f', raw, 32)
        out[spec['group_name']] = (cat, member_count, uid, guid, pos)
    return out


def expected_devices(hub):
    """Return (entrances, landings, shrines) from the R-246 tables.
    entrance = (host_key, (x,y,z), mouth, exit, dest_guid, dest_key)
    landing  = (host_key, (x,y,z), mouth)
    shrine   = spec dict"""
    entrances = [
        (bss.MAZE03_LVL_KEY, bss.UBER_LABYRINTH_ENTRANCE_SPOT,
         bss.R246_UBER_M1, bss.R246_UBER_X1, bss.CRYPT_FLOOR1_GUID, bss.CRYPT_FLOOR1_LEVEL_KEY),
        (bss.CATACUBE_FLOORLAST_LVL_KEY, (20.0, 1.0, 44.0),
         bss.SPARTA_M1, bss.SPARTA_X1, bss.SC2_MERGED_GUID, bss.SPARTA_LVL_KEY),
    ]
    landings = [
        (bss.CRYPT_FLOOR1_LEVEL_KEY, (140.0, 10.0, 225.0), bss.R246_UBER_X1),
        (bss.SPARTA_LVL_KEY, (48.9, 1.0, 34.7), bss.SPARTA_X1),
    ]
    shrines = [s for s in bss.R246_SHRINE_SPECS if not s['hub_only']]
    if hub:
        for (lbl, _mdbr, door, _mk, dest_key, dest_guid, land) in bss.R246_COURT:
            m, x = bss.R246_COURT_UIDS[lbl]
            entrances.append((bss.HELOS_HOST_KEY, door, m, x, dest_guid, dest_key))
            landings.append((dest_key, land, x))
        shrines = list(bss.R246_SHRINE_SPECS)
    return entrances, landings, shrines


def run_gate(map_path, hub, arz=None, verbose=True):
    data, levels, groups_raw = load_map(map_path)
    guid_by_key = {}
    key_by_guid = {}
    for lv in levels:
        ints = struct.unpack_from('<13I', lv['ints_raw'], 0)
        g = struct.pack('<4I', *ints[9:13])
        k = lv['fname'].replace(BS, '/').lower()
        guid_by_key[k] = g
        key_by_guid[g] = k
    entrances, landings, shrines = expected_devices(hub)
    viols = []
    blob_cache = {}
    inst_cache = {}
    mesh_cache = {}

    def get_blob(key):
        k = key.replace(BS, '/').lower()
        if k not in blob_cache:
            lv = level_by_suffix(levels, k)
            if lv is None:
                return None, None
            blob_cache[k] = (lv, data[lv['data_offset']:lv['data_offset'] + lv['data_length']])
        return blob_cache[k]

    def get_inst(key):
        k = key.replace(BS, '/').lower()
        if k not in inst_cache:
            lv, blob = get_blob(k)
            inst_cache[k] = parse_0x05(blob)[0] if blob else []
        return inst_cache[k]

    def get_mesh(key):
        k = key.replace(BS, '/').lower()
        if k not in mesh_cache:
            lv, blob = get_blob(k)
            mesh_cache[k] = Mesh(lv, blob, get_inst(k)) if blob else None
        return mesh_cache[k]

    def y_check(tag, key, x, y, z):
        mesh = get_mesh(key)
        if mesh is None or not mesh.ok:
            viols.append(f'Y1 {tag}: host {key} has no 0x0b navmesh')
            return
        f = mesh.floor_cal(x, z)
        if f is None:
            viols.append(f'Y1 {tag}: no walkable cell near ({x},{z}) in {key}')
        elif abs(y - f) > Y_TOL:
            viols.append(f'Y1 {tag}: y={y} vs floorCal={f:.2f} in {key} '
                         f'(|dy|={abs(y - f):.2f} > {Y_TOL}) - the buried/floating class')

    def onmesh_check(tag, key, x, z):
        mesh = get_mesh(key)
        if mesh and mesh.ok and mesh.onmesh_dist(x, z) > ONMESH_TOL:
            viols.append(f'ON {tag}: ({x},{z}) is OFF-MESH in {key} '
                         f'(d={mesh.onmesh_dist(x, z):.2f} > {ONMESH_TOL})')

    # ── doors ──────────────────────────────────────────────────────────────────
    exit_to_entrance = {}
    for (host, (x, y, z), mouth, exitu, dest_guid, dest_key) in entrances:
        hk = host.replace(BS, '/').lower()
        tag = f'door@{hk.split("/")[-1]}({x},{z})'
        if hk not in ALLOWED_ENTRANCE_HOSTS:
            viols.append(f'D5 {tag}: entrance host {hk} is NOT in the original-index '
                         f'allowlist (appended-host law: it would NEVER fire)')
        lv, blob = get_blob(hk)
        if blob is None:
            viols.append(f'D1 {tag}: host level missing from map')
            continue
        inst = get_inst(hk)
        x14 = parse_0x14(blob)
        hits = [(nm, ix, iy, iz, f, u, i) for (nm, ix, iy, iz, f, u, i) in inst
                if nm.endswith('portal_olympianarena1.dbr')
                and abs(ix - x) < 0.05 and abs(iz - z) < 0.05]
        if len(hits) != 1:
            viols.append(f'D1 {tag}: expected exactly 1 entrance instance, found {len(hits)}')
            continue
        _nm, ix, iy, iz, _f, _u, idx = hits[0]
        pl = x14.get(idx)
        if pl is None or len(pl) != 60:
            viols.append(f'D1 {tag}: entrance 0x14 missing or not 60B (got '
                         f'{len(pl) if pl else None})')
            continue
        if pl[:12] != bss.GRIDENTRANCE_0x14_PREFIX:
            viols.append(f'D1 {tag}: 60B 0x14 lacks the (2,0,1) GridEntrance prefix')
        if pl[12:28] != mouth or pl[28:44] != exitu or pl[44:60] != dest_guid:
            viols.append(f'D1 {tag}: 0x14 binding mismatch vs minted constants')
        swirl = [1 for (nm, sx, _sy, sz, _f2, _u2, _i2) in inst
                 if nm.endswith('map_portal_aura.dbr') and abs(sx - x) < 0.05 and abs(sz - z) < 0.05]
        if not swirl:
            viols.append(f'D1 {tag}: co-located map_portal_aura swirl missing')
        if dest_guid not in key_by_guid:
            viols.append(f'D3 {tag}: dest GUID {dest_guid.hex()[:12]}.. resolves to NO level')
        elif key_by_guid[dest_guid] != dest_key.replace(BS, '/').lower():
            viols.append(f'D3 {tag}: dest GUID resolves to {key_by_guid[dest_guid]}, '
                         f'expected {dest_key}')
        exit_to_entrance[exitu] = tag
        y_check(tag, hk, x, y, z)

    # ── landings ───────────────────────────────────────────────────────────────
    for (host, (x, y, z), mouth) in landings:
        hk = host.replace(BS, '/').lower()
        tag = f'landing@{hk.split("/")[-1]}({x},{z})'
        lv, blob = get_blob(hk)
        if blob is None:
            viols.append(f'D2 {tag}: host level missing from map')
            continue
        inst = get_inst(hk)
        x14 = parse_0x14(blob)
        hits = [(nm, ix, iy, iz, f, u, i) for (nm, ix, iy, iz, f, u, i) in inst
                if nm.endswith('portal_olympianarena2.dbr')
                and abs(ix - x) < 0.05 and abs(iz - z) < 0.05]
        if len(hits) != 1:
            viols.append(f'D2 {tag}: expected exactly 1 landing instance, found {len(hits)}')
            continue
        idx = hits[0][6]
        pl = x14.get(idx)
        if pl is None or len(pl) != 48:
            viols.append(f'D2 {tag}: landing 0x14 missing or not 48B')
            continue
        if pl[:16] != mouth or pl[16:] != b'\x00' * 32:
            viols.append(f'D2 {tag}: landing 0x14 != mouth+zeros')
        if mouth not in exit_to_entrance:
            viols.append(f'D2 {tag}: landing mouth {mouth.hex()[:12]}.. pairs NO entrance exit')
        y_check(tag, hk, x, y, z)
        onmesh_check(tag, hk, x, z)

    # ── minted-UID global uniqueness (D4) ─────────────────────────────────────
    for (host, _xyz, mouth, exitu, _dg, _dk) in entrances:
        n_m, n_x = data.count(mouth), data.count(exitu)
        if n_m != 1:
            viols.append(f'D4 mouth {mouth.hex()[:12]}..: {n_m} occurrences in map, expected 1')
        if n_x != 2:
            viols.append(f'D4 exit {exitu.hex()[:12]}..: {n_x} occurrences in map, expected 2 '
                         f'(entrance + landing)')

    # ── shrines (D6) ──────────────────────────────────────────────────────────
    gm = parse_groups_shrine_members(groups_raw)
    for spec in shrines:
        hk = spec['level_key'].replace(BS, '/').lower()
        tag = f'shrine-{spec["label"]}@{hk.split("/")[-1]}'
        inst = get_inst(hk)
        hits = [(nm, ix, iy, iz, f, u, i) for (nm, ix, iy, iz, f, u, i) in inst
                if nm.endswith('teleportshrineorient01.dbr') and u == spec['uid']]
        if len(hits) != 1:
            viols.append(f'D6 {tag}: expected exactly 1 flags=1 shrine instance with the '
                         f'minted uid, found {len(hits)}')
            continue
        _nm, ix, iy, iz, flags, _u, _i = hits[0]
        if flags != 1:
            viols.append(f'D6 {tag}: shrine flags={flags} != 1')
        if spec['group_name'] not in gm:
            viols.append(f'D6 {tag}: GROUPS record {spec["group_name"]} missing')
            continue
        cat, mc, uid, guid, pos = gm[spec['group_name']]
        if cat != 'TeleportShrine' or mc != 1:
            viols.append(f'D6 {tag}: GROUPS record cat={cat} members={mc}, expected '
                         f'TeleportShrine/1')
        if uid != spec['uid']:
            viols.append(f'D6 {tag}: GROUPS member uid != 0x05 uid')
        if guid != guid_by_key.get(hk):
            viols.append(f'D6 {tag}: GROUPS member level GUID != host level GUID')
        if any(abs(pos[i] - spec['pos'][i]) > 0.01 for i in range(3)):
            viols.append(f'D6 {tag}: GROUPS member pos {pos} != 0x05 pos {spec["pos"]}')
        n_u = data.count(spec['uid'])
        if n_u != 2:
            viols.append(f'D4 shrine uid {spec["uid"].hex()[:12]}..: {n_u} occurrences, '
                         f'expected 2 (0x05 + GROUPS)')
        y_check(tag, hk, ix, iy, iz)
        onmesh_check(tag, hk, ix, iz)

    # ── D7 variant separation ─────────────────────────────────────────────────
    if not hub:
        for (lbl, *_r) in bss.R246_COURT:
            m, x = bss.R246_COURT_UIDS[lbl]
            if data.count(m) or data.count(x):
                viols.append(f'D7 canonical map contains hub court uid ({lbl}) - the '
                             f'TESTHUB surface is leaking toward Steam')
        for spec in bss.R246_SHRINE_SPECS:
            if spec['hub_only'] and (data.count(spec['uid'])
                                     or spec['group_name'].encode() in groups_raw):
                viols.append(f'D7 canonical map contains hub-only shrine {spec["label"]}')

    # ── C-block: traffic-lane / clearance (the surviving half of the 07-12 P0) ─
    def _is_own(nm):
        return any(k in nm for k in _R246_OWN)

    # C1 court pairwise: every door plane >= COURT_MIN_PAIRWISE from every other door
    ent_pos = [(host.replace(BS, '/').lower(), x, z, f'door@{host.split(BS)[-1].split("/")[-1]}({x},{z})')
               for (host, (x, y, z), *_r) in entrances]
    for i in range(len(ent_pos)):
        for j in range(i + 1, len(ent_pos)):
            if ent_pos[i][0] != ent_pos[j][0]:
                continue
            d = math.hypot(ent_pos[i][1] - ent_pos[j][1], ent_pos[i][2] - ent_pos[j][2])
            if d < COURT_MIN_PAIRWISE:
                viols.append(f'C1 {ent_pos[i][3]} and {ent_pos[j][3]}: door planes '
                             f'{d:.2f}u apart < {COURT_MIN_PAIRWISE} (court law)')

    # C2 clickable standoff + C5 stairs funnel: per door entrance
    for (host, (x, y, z), *_r) in entrances:
        hk = host.replace(BS, '/').lower()
        tag = f'door@{hk.split("/")[-1]}({x},{z})'
        for (nm, ix, iy, iz, _f, _u, _i) in get_inst(hk):
            if _is_own(nm):
                continue
            d = math.hypot(ix - x, iz - z)
            if glc.classify(nm) == 'npc' and d < DOOR_MIN_CLICKABLE:
                viols.append(f'C2 {tag}: clickable NPC {nm.split(BS)[-1]} at {d:.2f}u '
                             f'< {DOOR_MIN_CLICKABLE} (a walk-through plane near a '
                             f'clickable = the forced-teleport class)')
            if 'stairsdown' in nm and hk == bss.CATACUBE_FLOORLAST_LVL_KEY.replace(BS, '/').lower() \
                    and d < STAIRS_MIN:
                viols.append(f'C5 {tag}: {d:.2f}u from the stairsdown01 traffic funnel '
                             f'< {STAIRS_MIN} (B-PORTAL-2 lane law)')

    # C3 landing/shrine clearance vs placed collidables (b44 CLASS_MIN model)
    clr_targets = [(host.replace(BS, '/').lower(), x, z,
                    f'landing@{host.split(BS)[-1].split("/")[-1]}({x},{z})')
                   for (host, (x, y, z), _m) in landings]
    clr_targets += [(s['level_key'].replace(BS, '/').lower(), s['pos'][0], s['pos'][2],
                     f'shrine-{s["label"]}') for s in shrines]
    for (hk, x, z, tag) in clr_targets:
        for (nm, ix, iy, iz, _f, _u, _i) in get_inst(hk):
            if _is_own(nm):
                continue
            k = glc.classify(nm)
            mn = glc.CLASS_MIN.get(k, 0.0)
            if mn <= 0:
                continue
            d = math.hypot(ix - x, iz - z)
            if d < mn:
                viols.append(f'C3 {tag}: {k} {nm.split(BS)[-1]} at {d:.2f}u < class '
                             f'minimum {mn} (the land-in-chest class)')

    # C4 shrine standoff from its co-level landing
    land_by_level = {}
    for (host, (x, y, z), _m) in landings:
        land_by_level.setdefault(host.replace(BS, '/').lower(), []).append((x, z))
    for s in shrines:
        hk = s['level_key'].replace(BS, '/').lower()
        for (lx, lz) in land_by_level.get(hk, []):
            d = math.hypot(s['pos'][0] - lx, s['pos'][2] - lz)
            if d < SHRINE_MIN_LANDING:
                viols.append(f'C4 shrine-{s["label"]}: {d:.2f}u from the landing at '
                             f'({lx},{lz}) < {SHRINE_MIN_LANDING} (arrive-inside-the-'
                             f'shrine class)')

    # ── Y1 for marker NPCs + SVC boat dests ───────────────────────────────────
    markers = [
        ('marker-uber-greeter', bss.MAZE03_LVL_KEY, 278.0, 1.0, 147.5),
        ('marker-warden', bss.CATACUBE_FLOORLAST_LVL_KEY, 25.0, 1.0, 32.0),
        ('marker-crypt', bss.CRYPT_FLOOR1_LEVEL_KEY, 140.0, 10.0, 229.0),
        ('marker-sc2', bss.SPARTA_LVL_KEY, 45.0, 1.0, 42.0),
        ('dest-almyros-garden', bss.GARDEN_LVL_KEY, 130.0, -39.0, 73.0),
        ('dest-almyros-secret', bss.SECRET_LVL_KEY, 24.0, 2.0, 30.0),
        ('dest-almyros-uber', bss.CRYPT_FLOOR1_LEVEL_KEY, 140.0, 10.0, 225.0),
    ]
    if hub:
        for (lbl, mdbr, door, (mx, my, mz), dest_key, _dg, _land) in bss.R246_COURT:
            markers.append((f'marker-court-{lbl}', bss.HELOS_HOST_KEY, mx, my, mz))
        for (rk, rspec) in bss.HELOS_HUB_RETURN_SPECS:
            markers.append((f'marker-{rspec[0].split(BS.encode())[-1].decode()}',
                            rk, rspec[1], rspec[2], rspec[3]))
    for (tag, key, x, y, z) in markers:
        y_check(tag, key, x, y, z)

    # ── arz side (optional): born-open class check ────────────────────────────
    if arz:
        from arz_patcher import ArzDatabase
        db = ArzDatabase.from_arz(Path(arz))
        rec = db.get_record(r'records\quests\portal_olympianarena1.dbr')
        cls = None
        if rec is not None:
            for k, v in rec.fields():
                if k == 'Class':
                    cls = v
        if cls != 'GridEntrance':
            viols.append(f'ARZ portal_olympianarena1 Class={cls!r}, expected the born-open '
                         f'static GridEntrance (B-PORTAL-1: Dynamic never opens quest-free)')

    n_dev = len(entrances) + len(landings) + len(shrines)
    if viols:
        print(f'DEVICE-RESOLUTION GATE ({"TESTHUB" if hub else "canonical"}): '
              f'{len(viols)} VIOLATION(S) over {n_dev} devices')
        for v in viols:
            print(f'  FAIL {v}')
        return False
    print(f'DEVICE-RESOLUTION GATE ({"TESTHUB" if hub else "canonical"}): PASS - '
          f'{len(entrances)} door entrances + {len(landings)} landings + {len(shrines)} '
          f'shrines all resolve, pair, sit on-mesh at floorCal Y with C1-C5 lane/'
          f'clearance green (+{len(markers)} marker/dest Y checks)')
    return True


def negtest(map_path, hub):
    """Planted defects on IN-MEMORY table copies must each RED the gate."""
    import copy
    ok = True

    def run_quiet():
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            r = run_gate(map_path, hub)
        return r

    base = run_quiet()
    if not base:
        print('  NEGTEST positive control FAILED (base map does not pass)')
        return False
    print('  [GREEN OK] positive control passes')

    # N1 buried device: shift the crypt shrine spec Y by -1.5
    saved = bss.R246_SHRINE_SPECS[0]['pos']
    bss.R246_SHRINE_SPECS[0]['pos'] = (saved[0], saved[1] - 1.5, saved[2])
    r = run_quiet()
    bss.R246_SHRINE_SPECS[0]['pos'] = saved
    print(f'  [{"RED   OK" if not r else "FAIL"}] buried device (shrine Y-1.5)')
    ok &= (not r)

    # N2 dangling dest GUID
    saved_g = bss.CRYPT_FLOOR1_GUID
    try:
        bss.CRYPT_FLOOR1_GUID = b'\xde\xad' * 8
        r = run_quiet()
    finally:
        bss.CRYPT_FLOOR1_GUID = saved_g
    print(f'  [{"RED   OK" if not r else "FAIL"}] dangling dest GUID')
    ok &= (not r)

    # N3 door entrance in an appended host (move the maze03 door expectation to crypt)
    saved_k = bss.MAZE03_LVL_KEY
    try:
        bss.MAZE03_LVL_KEY = bss.CRYPT_FLOOR1_LEVEL_KEY
        r = run_quiet()
    finally:
        bss.MAZE03_LVL_KEY = saved_k
    print(f'  [{"RED   OK" if not r else "FAIL"}] door entrance in an appended host')
    ok &= (not r)

    # N4 shrine GROUPS member missing (rename the expected group)
    saved_n = bss.R246_SHRINE_SPECS[0]['group_name']
    bss.R246_SHRINE_SPECS[0]['group_name'] = 'SVCShrineTeleport_R246_PLANTED'
    r = run_quiet()
    bss.R246_SHRINE_SPECS[0]['group_name'] = saved_n
    print(f'  [{"RED   OK" if not r else "FAIL"}] shrine missing its GROUPS member')
    ok &= (not r)

    # N5 clearance scanner is LIVE (hub only): raising the 'other' minimum to 3.0 must
    # trip C3 on the b44-documented devourer pitwedge (classify='other', min 1.5) at
    # 2.83u from the drxbc2 landing - proves the scan path sees real placed scenery,
    # and pins the 2.83u fact structurally.
    if hub:
        import gate_landing_clearance as _glc
        saved_p = _glc.CLASS_MIN['other']
        _glc.CLASS_MIN['other'] = 3.0
        r = run_quiet()
        _glc.CLASS_MIN['other'] = saved_p
        print(f'  [{"RED   OK" if not r else "FAIL"}] clearance scanner live '
              f'(other-min 3.0 trips the 2.83u devourer pitwedge)')
        ok &= (not r)

    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', required=True)
    ap.add_argument('--hub', action='store_true')
    ap.add_argument('--arz')
    ap.add_argument('--negtest', action='store_true')
    args = ap.parse_args()
    if args.negtest:
        sys.exit(0 if negtest(args.map, args.hub) else 1)
    sys.exit(0 if run_gate(args.map, args.hub, args.arz) else 1)


if __name__ == '__main__':
    main()
