#!/usr/bin/env python3
"""GATE G2 - cave ENTRANCE landing check (HiddenValley01 -> Random09A).

Closes the blind spot that let the 2026-07-06 Y-ALIGN anchoring regression ship:
the interior-chain gates (oracle reachability, seam medians) are all RELATIVE
between regenerated meshes, so a rigid whole-cluster (or whole-component) Y error
passes every one of them while breaking the ONE interface whose other side we do
NOT regenerate: the native cave entrance.

Mechanism (disasm/frida-proven, docs/CAVE_ENTRY_CHAIN_TRACE.md):
  - HiddenValley01's 0x14 record (the GridEntrance binding: [12B hdr][mouth
    UniqueId][exit UniqueId][dest LEVEL GUID @44]) + its 0x05 instance (mouth art,
    FIXED local coords incl. Y) define the surface mouth.
  - Random09A's 0x06 GridSystem section ends with the reciprocal portal
    descriptor: [u32 2][u32 64][u32 count=1][exit id][mouth id][src LEVEL GUID]
    [u32 doorX][u32 doorY][u32 doorZ] - the door GRID CELL in R09's dungeon grid
    (10x10 cells of 8u for the Silk Road cave). The exit portal / player landing
    sits at that cell's terrain, at FIXED world coords incl. Y.
  - The engine places the player via the paired portal transform and needs a
    navmesh poly under the landing within findNearestPoly's vertical extent
    (~2u). If Random09A's generated mesh floor is shifted away from the FIXED
    landing height, the player cannot enter (navmesh loads ret=1, portal open=1,
    yet the mouth walls - exactly the observed regression: donor center Y 21 vs
    authored 24 = mesh 3u low).

THE GATE: the landing cell's XZ box must contain donor-mesh walkable cells, and
at least one must be within 2.0u vertically of the FIXED landing height. The
fixed height is derived from the upstream SV 0x0a tok floor at the door cell
(the authored terrain the donors rasterize), cross-checked against the AE
Editor-baked Random09A navmesh (the proven-working vanilla landing).

Usage:
  py tools/debug/entrance_landing_check.py                # gate the donor
  py tools/debug/entrance_landing_check.py --check-merged # also gate the map's injected 0x0b
  py tools/debug/entrance_landing_check.py --map <Levels.arc>

Exit 0 = PASS, 1 = FAIL. Read-only.
"""
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
from gen_rec02 import load_tok_mesh                                  # noqa: E402
from navlib import Mesh, CS, CH                                      # noqa: E402

HV_KEY = 'levels/world/orient/silkroad/hiddenvalley01.lvl'
R09_KEY = 'levels/world/orient/underground/random09a.lvl'
UPSTREAM_SV_ARC = REPO / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc'
SVAERA_ARC = REPO / 'reference_mods' / 'SVAERA_customquest' / 'Resources' / 'Levels.arc'
DONOR = Path(os.environ.get('SVC_DONOR_DIR',
                            str(REPO / 'local' / 'editor_normalized'))) / 'Random09A.lvl.0b.bin'
SNAP_U = 2.0          # findNearestPoly vertical extent (engine)
MIN_BOX_CELLS = 50    # sanity: the door cell must be meaningfully meshed


def load_map(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    by = {lv['fname'].replace('\\', '/').lower(): lv for lv in levels}
    return data, by


def blob_of(data, lv):
    return data[lv['data_offset']:lv['data_offset'] + lv['data_length']]


def ints13(lv):
    return struct.unpack_from('<13i', lv['ints_raw'], 0)


def parse_0x05(d05, magic_ver):
    """String table + instance records. v0x11 = 72B records, v0x0e = 56B."""
    pos = 0
    scount = struct.unpack_from('<I', d05, 0)[0]; pos = 4
    strings = []
    for _ in range(scount):
        slen = struct.unpack_from('<I', d05, pos)[0]; pos += 4
        strings.append(d05[pos:pos + slen]); pos += slen
    icount = struct.unpack_from('<I', d05, pos)[0]; pos += 4
    rec = 72 if magic_ver >= 0x11 else 56
    inst = {}
    for i in range(icount):
        off = pos + i * rec
        r = d05[off:off + rec]
        if len(r) < 52:
            break
        sidx = struct.unpack_from('<I', r, 0)[0]
        x, y, z = struct.unpack_from('<fff', r, 40)
        inst[i] = (sidx, x, y, z)
    return strings, inst


def parse_0x14(d14):
    recs = {}
    pos = 0
    while pos + 8 <= len(d14):
        idx = struct.unpack_from('<I', d14, pos)[0]
        psize = struct.unpack_from('<I', d14, pos + 4)[0]
        if pos + 8 + psize > len(d14):
            break
        recs[idx] = d14[pos + 8:pos + 8 + psize]
        pos += 8 + psize
    return recs


def mesh_cells_world(doc_or_path):
    """set-0 walkable cells -> {(wx_idx, wz_idx): world_y} on the shared CS grid."""
    m = Mesh(doc_or_path, 'x')
    offx = round(m.origin[0] / CS)
    offz = round(m.origin[2] / CS)
    return m, {(gx + offx, gz + offz): m.origin[1] + h * CH
               for (gx, gz), (h, a, c) in m.cells.items()}


def cells_in_box(cells, x0, x1, z0, z1):
    return [y for (gx, gz), y in cells.items()
            if x0 <= (gx + 0.5) * CS < x1 and z0 <= (gz + 0.5) * CS < z1]


def median(v):
    s = sorted(v)
    return s[len(s) // 2]


def main():
    args = sys.argv[1:]
    check_merged = '--check-merged' in args
    map_path = None
    if '--map' in args:
        map_path = Path(args[args.index('--map') + 1])
    else:
        for cand in (REPO / 'local' / 'Levels_merged.arc',
                     REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Levels.arc'):
            if cand.exists():
                map_path = cand
                break
    if map_path is None or not map_path.exists():
        print('FAIL: no merged map found (pass --map <Levels.arc>)')
        return 1

    print(f'G2 ENTRANCE LANDING CHECK\n  merged map: {map_path}\n  donor:      {DONOR}')
    data, by = load_map(map_path)
    hv, r09 = by[HV_KEY], by[R09_KEY]
    hv_i, r_i = ints13(hv), ints13(r09)
    hv_guid, r09_guid = hv['ints_raw'][36:52], r09['ints_raw'][36:52]
    print(f'  HV01 corner=({hv_i[6]},{hv_i[7]},{hv_i[8]})  R09 corner=({r_i[6]},{r_i[7]},{r_i[8]})'
          f'  R09 guid={r09_guid.hex()[:8]}...')

    # ---- surface side: HV01 0x14 record with dest == R09 guid + its 0x05 instance
    hb = blob_of(data, hv)
    hsec, _ = parse_blob_sections(hb)
    hsd = {s['type']: s['data'] for s in hsec}
    recs14 = parse_0x14(hsd.get(0x14, b''))
    mouth_recs = [(i, p) for i, p in recs14.items() if len(p) >= 60 and p[44:60] == r09_guid]
    if len(mouth_recs) != 1:
        print(f'FAIL: expected exactly 1 HV01 0x14 record with dest=Random09A, got {len(mouth_recs)}')
        return 1
    rec_idx, payload = mouth_recs[0]
    mouth_id, exit_id = payload[12:28], payload[28:44]
    strings, inst = parse_0x05(hsd[0x05], hb[3])
    art = pos = None
    if rec_idx in inst:
        sidx, x, y, z = inst[rec_idx]
        art = strings[sidx].decode('ascii', 'replace') if sidx < len(strings) else '?'
        pos = (hv_i[6] + x, hv_i[7] + y, hv_i[8] + z)
    print(f'  mouth: HV01 0x14 rec#{rec_idx}  art={art}')
    print(f'         mouth id={mouth_id.hex()[:12]}... exit id={exit_id.hex()[:12]}...'
          f'  world={tuple(round(v, 2) for v in pos) if pos else "?"}')

    # ---- destination side: R09 0x06 reciprocal descriptor + door grid cell
    rb = blob_of(data, r09)
    rsec, _ = parse_blob_sections(rb)
    rsd = {s['type']: s['data'] for s in rsec}
    d06 = rsd.get(0x06, b'')
    ep = d06.find(exit_id)
    if ep < 0:
        print('FAIL: R09 0x06 has no reciprocal descriptor for the HV01 exit id '
              '(the return portal binding is missing - the mouth cannot pair)')
        return 1
    if d06[ep + 16:ep + 32] != mouth_id or d06[ep + 32:ep + 48] != hv_guid:
        print('FAIL: R09 0x06 descriptor ids do not mirror HV01 0x14 '
              f'(mouth match={d06[ep + 16:ep + 32] == mouth_id}, '
              f'src-guid match={d06[ep + 32:ep + 48] == hv_guid})')
        return 1
    pre = struct.unpack_from('<3I', d06, ep - 12)
    door = struct.unpack_from('<3I', d06, ep + 48)
    # dungeon grid dims: [u32 strlen][DBR string][u32 gw][u32 layers][u32 gh] @16
    slen = struct.unpack_from('<I', d06, 16)[0]
    gw, glay, gh = struct.unpack_from('<3I', d06, 20 + slen)
    cw = (r_i[3] * 2) / gw
    ch = (r_i[5] * 2) / gh
    print(f'  R09 0x06 descriptor @ {ep}: preamble={pre} door cell=(x={door[0]},y={door[1]},z={door[2]})'
          f'  grid {gw}x{gh}, cell {cw:g}x{ch:g}u')
    if not (door[0] < gw and door[2] < gh):
        print('FAIL: door cell outside the dungeon grid - descriptor decode is wrong')
        return 1
    x0 = r_i[6] + door[0] * cw
    z0 = r_i[8] + door[2] * ch
    x1, z1 = x0 + cw, z0 + ch
    print(f'  LANDING box (world): X[{x0:g},{x1:g}) Z[{z0:g},{z1:g})')

    # ---- FIXED landing height: upstream SV tok floor at the door cell (authored
    # terrain), cross-checked vs the AE Editor-baked mesh (proven vanilla landing).
    sv_data, sv_by = load_map(UPSTREAM_SV_ARC)
    sv_lv = sv_by[R09_KEY]
    sv_i = ints13(sv_lv)
    tmp = Path(tempfile.gettempdir()) / 'svc_g2_r09_upstream.lvl'
    tmp.write_bytes(blob_of(sv_data, sv_lv))
    _g, center_a, dims_a, verts, tris = load_tok_mesh(str(tmp))
    corner0a = tuple(center_a[i] - dims_a[i] for i in range(3))
    dxz = (r_i[6] - sv_i[6], r_i[8] - sv_i[8])
    dy = r_i[7] - sv_i[7]
    tok_ys = []
    for tri in tris:
        for vi in tri:
            vx, vz, vy = verts[vi]
            wx = corner0a[0] + vx + dxz[0]
            wz = corner0a[2] + vz + dxz[1]
            if x0 <= wx < x1 and z0 <= wz < z1:
                tok_ys.append(corner0a[1] + vy + dy)
    if not tok_ys:
        print('FAIL: upstream tok has no floor at the door cell - cannot derive the fixed landing Y')
        return 1
    landing_y = median(tok_ys)
    print(f'  FIXED landing Y (SV tok floor at door cell, merged frame): {landing_y:.2f} '
          f'({len(tok_ys)} verts, range [{min(tok_ys):.2f},{max(tok_ys):.2f}])')
    # AE cross-check (best-effort)
    try:
        ae_data, ae_by = load_map(SVAERA_ARC)
        ae_lv = ae_by[R09_KEY]
        ae_i = ints13(ae_lv)
        asec, _ = parse_blob_sections(blob_of(ae_data, ae_lv))
        asd = {s['type']: s['data'] for s in asec}
        _m, ae_cells = mesh_cells_world(parse_rec02(asd[0x0b], decompress=True))
        lx0, lz0 = x0 - r_i[6], z0 - r_i[8]
        ys = cells_in_box(ae_cells, ae_i[6] + lx0, ae_i[6] + lx0 + cw,
                          ae_i[8] + lz0, ae_i[8] + lz0 + ch)
        if ys:
            ae_landing = median(ys) - ae_i[7] + r_i[7]
            note = '' if abs(ae_landing - landing_y) <= 1.0 else '  <<< references disagree >1u'
            print(f'  cross-check AE Editor-baked landing Y (merged frame): {ae_landing:.2f} '
                  f'({len(ys)} cells){note}')
        else:
            print('  cross-check AE: no mesh cells at the door cell (unexpected)')
    except Exception as e:  # cross-check only; the tok reference gates
        print(f'  cross-check AE unavailable: {e}')

    # ---- THE GATE: donor mesh at the landing
    def gate(tag, cells):
        ys = cells_in_box(cells, x0, x1, z0, z1)
        if len(ys) < MIN_BOX_CELLS:
            print(f'  {tag}: FAIL - only {len(ys)} walkable cells in the landing box '
                  f'(need >= {MIN_BOX_CELLS}; the door cell is not meshed)')
            return False
        md = median(ys)
        within = sum(1 for y in ys if abs(y - landing_y) <= SNAP_U)
        verdict = within >= 1 and abs(md - landing_y) <= SNAP_U
        print(f'  {tag}: {len(ys)} cells in box, median Y={md:.2f}, dY vs landing='
              f'{md - landing_y:+.2f}u, cells within {SNAP_U}u: {within} -> '
              f'{"PASS" if verdict else "FAIL (landing misses the mesh: findNearestPoly ext 2u)"}')
        return verdict

    if not DONOR.exists():
        print(f'FAIL: donor missing: {DONOR}')
        return 1
    dm, don_cells = mesh_cells_world(DONOR)
    print(f'  donor container center={dm.center} (0x0a-authored center Y + grid dy must match: '
          f'{center_a[1]} + {dy} = {center_a[1] + dy})')
    ok = gate('DONOR  Random09A.lvl.0b.bin', don_cells)
    if dm.center[1] != center_a[1] + dy:
        print(f'  DONOR: FAIL - container center Y {dm.center[1]} != authored {center_a[1] + dy} '
              f'(G1 anchor violated)')
        ok = False

    # merged map's injected copy (informative; gates only with --check-merged)
    if 0x0b in rsd:
        _m2, mg_cells = mesh_cells_world(parse_rec02(rsd[0x0b], decompress=True))
        ok_m = gate('MERGED injected R09 0x0b   ', mg_cells)
        if check_merged:
            ok = ok and ok_m
        elif not ok_m:
            print('  (merged map copy fails - STALE map; rebuild via svaera_plus_portals '
                  'after regenerating donors. Not gating without --check-merged.)')
    else:
        print('  merged map R09 has no 0x0b section' + (' - FAIL' if check_merged else ''))
        if check_merged:
            ok = False

    print(f'\nG2 ENTRANCE LANDING: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
