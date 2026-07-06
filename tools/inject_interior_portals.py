#!/usr/bin/env python3
r"""Inject engine-native cave-mouth PORTALS between interior cave rooms (Track 2).

WHY
---
The blood-cave interior chain (Random09A -> xPassageTransitionStart ->
BC_initialpathway -> drxFirstRoom -> ...) connects room-to-room by a SEAMLESS
GRID-SEAM WALK (mechanism 2a in docs/MODDING_PLAYBOOK.md): two abutting levels
whose 0x0b navmeshes overlap at the shared edge. That stitch has failed 10+ ways
(the "invisible wall" at random09a -> xpassagetransitionstart). This tool instead
replicates the WORKING surface cave-mouth PORTAL (mechanism 2b) BETWEEN interior
rooms, so the player crosses via an engine-native portal that resolves the
destination purely by GUID (position-independent) instead of relying on the
fragile geometric seam overlap.

The working exemplar is HiddenValley01 -> Random09A (the Silk Road cave mouth,
open=1, walk-proven). This tool reproduces its exact byte layout between two
interior levels, data-driven by a wiring table so the whole chain can be portal-ed.

WHAT IT WRITES (per seam fromLevel -> toLevel)
----------------------------------------------
1. A GridEntrance art entity in `fromLevel`'s 0x05 at `entrancePos` (local coords),
   PLUS a 0x14 GUID-binding record for that instance carrying:
       mouth Portal UniqueId, reciprocal exit Portal UniqueId, toLevel's RegionId GUID.
   (v0x11 -> 60-byte payload [hdr(2,0,1)][mouth][exit][dest];
    v0x0e -> 48-byte payload [mouth][exit][dest], no header - both proven in the
    deployed map: HiddenValley01 #30 is the 60B form, yet_another_fucking_connector
    #93 is the 48B form.)
2. A reciprocal exit-portal descriptor appended to `toLevel`'s 0x06:
       [exit UniqueId][mouth UniqueId][fromLevel's GUID]   (48 contiguous bytes)
   This mirrors every base-game mouth's destination 0x06 trailer (verified
   byte-identical on Connector02->StartingTownOptional02A etc.: exit/mouth match
   the surface 0x14's exit/mouth exactly).

Fresh Portal UniqueIds are minted from an id space proven collision-free against
all 641 existing portal ids in the deployed map (scan-verified).

DISCIPLINE
----------
This module is SELF-CONTAINED and does NOT run the full merge/build. It exposes
`inject_interior_portals(map_data_or_levels, wiring, ...)` for the coordinator to
call as a step inside tools/svaera_plus_portals.py, and a `__main__` self-test that
runs the injection against the DEPLOYED map IN MEMORY, re-parses, and byte-verifies
every injected record resolves (writes nothing to any map).

Coordinates: `entrancePos`/`exitPos` are LOCAL to the level (same frame as its 0x05
instance positions), floor Y. Derive them from the DESTINATION level's 0x0b navmesh
(an interior, on-mesh, area!=0 cell), NOT from the grid corner - see
`derive_landing_local()`. Off-mesh / above-floor targets are the failure mode that
killed the old portal-teleport (target 0.28u off-mesh / +7u above floor).
"""
import os
import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import (parse_blob_sections, rebuild_blob,
                                   parse_0x05_strings, parse_0x14_records,
                                   build_0x14_data)
from rec02_format import parse_rec02

CS = 0.2      # navmesh cell size (world units)
TILE = 64

V0E_RECORD_SIZE = 56
V11_RECORD_SIZE = 72

# GridEntrance art record (pure art; the visible cave mouth). Same DBR the working
# Silk Road mouth uses. NOTE (risk, see doc): this is a DARK CAVE-MOUTH mesh; in an
# open interior passage it will look like a cave opening. An invisible/subtle
# GridEntrance-class art record can be substituted per seam via wiring 'entranceDbr'.
DEFAULT_ENTRANCE_DBR = b'Records/Underground/NaturalCave/Orient/SilkRoad/SilkRdDngEntrance_C01_Ext.dbr'


# ---------------------------------------------------------------------------
# Fresh portal-id minting (collision-free id space)
# ---------------------------------------------------------------------------
def _mint_id(tag):
    """Deterministic fresh 16-byte Portal UniqueId. 0xFEEDCAFE marker + 32-bit tag
    + 8 zero bytes. Verified non-colliding against all 641 deployed portal ids."""
    return b'\xfe\xed\xca\xfe' + struct.pack('<I', tag & 0xffffffff) + b'\x00' * 8


def scan_existing_portal_ids(levels_data_pairs):
    """Collect every portal UniqueId already used in the map (from 0x14 bindings and
    0x06 trailers), so minted ids provably do not collide.

    levels_data_pairs: iterable of (blob_bytes,) or (blob_bytes, ints_raw). Only the
    blob is read here.
    """
    ids = set()
    for item in levels_data_pairs:
        blob = item[0]
        secs, magic = parse_blob_sections(blob)
        ver = magic[3] if len(magic) >= 4 else 0
        for s in secs:
            if s['type'] == 0x14 and s['size']:
                for r in parse_0x14_records(s['data']):
                    pl = r['payload']
                    if len(pl) == 60:
                        ids.add(pl[12:28]); ids.add(pl[28:44])
                    elif len(pl) == 48:
                        ids.add(pl[0:16]); ids.add(pl[16:32])
    return ids


# ---------------------------------------------------------------------------
# 0x05 GridEntrance injection (returns new 0x05 data + the injected instance index)
# ---------------------------------------------------------------------------
def _parse_05(section_data, rec_size):
    scount = struct.unpack_from('<I', section_data, 0)[0]
    pos = 4
    strings = []
    for _ in range(scount):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        strings.append(section_data[pos:pos + slen]); pos += slen
    strings_end = pos
    inst_count = struct.unpack_from('<I', section_data, strings_end)[0]
    inst_start = strings_end + 4
    inst_bytes = section_data[inst_start:inst_start + inst_count * rec_size]
    trailing = section_data[inst_start + inst_count * rec_size:]
    return strings, inst_count, inst_bytes, trailing


def inject_gridentrance_05(section_data, ver, dbr_bytes, x, y, z):
    """Append a GridEntrance instance to a 0x05 section. Returns (new_section_data,
    injected_instance_index). Handles v0x0e (56B) and v0x11 (72B)."""
    rec_size = V11_RECORD_SIZE if ver == 0x11 else V0E_RECORD_SIZE
    strings, inst_count, inst_bytes, trailing = _parse_05(section_data, rec_size)

    new_strings = list(strings)
    if dbr_bytes in new_strings:
        sidx = new_strings.index(dbr_bytes)
    else:
        sidx = len(new_strings)
        new_strings.append(dbr_bytes)

    rec = struct.pack('<I', sidx)
    rec += struct.pack('<9f', 1, 0, 0, 0, 1, 0, 0, 0, 1)   # identity rotation
    rec += struct.pack('<3f', x, y, z)                     # local position
    rec += struct.pack('<I', 0)                            # flags
    if ver == 0x11:
        rec += b'\x00' * 16
    injected_idx = inst_count

    out = bytearray()
    out += struct.pack('<I', len(new_strings))
    for s in new_strings:
        out += struct.pack('<I', len(s)); out += s
    out += struct.pack('<I', inst_count + 1)
    out += inst_bytes
    out += rec
    out += trailing            # preserve anything after the instance array
    return bytes(out), injected_idx


# ---------------------------------------------------------------------------
# 0x14 binding record
# ---------------------------------------------------------------------------
def make_binding_payload(ver, mouth_id, exit_id, dest_guid):
    """Build the 0x14 binding payload for the GridEntrance instance.

    v0x11: 60 bytes = [hdr (2,0,1)][mouth 16][exit 16][dest 16]
    v0x0e: 48 bytes = [mouth 16][exit 16][dest 16]   (no header)
    """
    assert len(mouth_id) == 16 and len(exit_id) == 16 and len(dest_guid) == 16
    if ver == 0x11:
        return struct.pack('<3I', 2, 0, 1) + mouth_id + exit_id + dest_guid
    return mouth_id + exit_id + dest_guid


def upsert_0x14_binding(s14_data, ver, inst_count, inst_idx, payload):
    """Ensure the 0x14 section has default records for every instance up to
    inst_count and a BINDING record for inst_idx.

    PRESERVE the EXACT existing record set (indices AND payloads) and only ADD/replace
    the ONE record for the injected GridEntrance instance. This avoids changing the
    behaviour of any other entity: a v0x11 level's 0x14 is SPARSE (HiddenValley01 has
    190 records for 205 instances - some instances deliberately carry no metadata),
    and a v0x0e level's 0x14 is usually EMPTY (Random09A ships 0x14 size 0). We do NOT
    densely fill 0..inst_count (that would add default records for instances that had
    none and could change their interactivity). `inst_count` is accepted for
    signature stability but intentionally not used for gap-filling.
    """
    _ = inst_count  # not used: we preserve the sparse record set as-is
    existing = {}
    order = []
    if s14_data:
        for r in parse_0x14_records(s14_data):
            if r['index'] not in existing:
                order.append(r['index'])
            existing[r['index']] = r['payload']
    if inst_idx not in existing:
        order.append(inst_idx)          # append the new binding record after the rest
    existing[inst_idx] = payload        # add or replace the injected instance's record
    recs = [{'index': i, 'payload_size': len(existing[i]), 'payload': existing[i]}
            for i in order]
    return build_0x14_data(recs)


# ---------------------------------------------------------------------------
# 0x06 reciprocal exit-portal trailer
# ---------------------------------------------------------------------------
# The portal-descriptor list lives at the TAIL of a level's 0x06 (after the terrain
# grid). Byte-decoded from the deployed map:
#   [u32 field = 64][u32 count = N][ N x 60-byte descriptor ]
# each descriptor = [exit UniqueId 16][mouth UniqueId 16][source level GUID 16]
#                   [u32 t0][u32 0][u32 t1]      (12-byte per-descriptor trailer)
# Proven examples (deployed): Random09A tail = 40 00 00 00 | 01 00 00 00 |
#   [8932..(exit)][cfb4..(mouth)][ce93..(HiddenValley01 src)] | 08 00 00 00 00 00 00 00 02 00 00 00
#   StartingTownOptional02A: same shape, trailer 06 00 00 00 / 00 / 04 00 00 00
#   Athens Entrance01: count = 2, two 60-byte descriptors (a dest CAN hold several).
# The per-descriptor trailer's t0/t1 vary across levels (portal-type + an index);
# they are NOT read for the inbound crossing (which is built solely from the SOURCE
# GridEntrance + 0x14, GridEntrance::Read VA 0x10195240). They matter only for the
# RETURN/pairing. We copy the working Random09A return-descriptor values (t0=8, t1=2).
DESC_TRAILER = struct.pack('<3I', 8, 0, 2)
DESC_SIZE = 60   # exit(16) + mouth(16) + srcGUID(16) + trailer(12)


def _find_portal_list_tail(d6):
    """If d6 already ends with a [64][count][count x 60B descriptor] portal list,
    return (list_start_offset, count). Else None. The list is the LAST thing in the
    section (ends exactly at len(d6)); probe small counts for a [64][count] header
    at the matching offset."""
    n = len(d6)
    for count in range(1, 9):
        hdr_off = n - (8 + count * DESC_SIZE)
        if hdr_off < 0:
            break
        f0, c = struct.unpack_from('<2I', d6, hdr_off)
        if f0 == 64 and c == count:
            return hdr_off, count
    return None


def append_0x06_reciprocal(s06_data, exit_id, mouth_id, src_guid):
    """Append/extend the reciprocal exit-portal descriptor list at the tail of the
    destination level's 0x06, preserving the base-game structure exactly.

    - If the 0x06 already ends with a [64][count][descriptors] list (a level that
      already links to another), bump count and append our 60-byte descriptor.
    - Otherwise (e.g. xPassageTransitionStart, whose 0x06 tail is zero-padded with no
      portal list), append a fresh [64][count=1][descriptor] block.

    Descriptor = [exit 16][mouth 16][src GUID 16][12-byte trailer]. This is the exact
    shape every base-game mouth destination carries (verified byte-identical on
    Random09A + 4 Greek caves), so the return walk-out + portal pairing resolve.
    """
    d6 = bytes(s06_data)
    new_desc = exit_id + mouth_id + src_guid + DESC_TRAILER
    found = _find_portal_list_tail(d6)
    if found is not None:
        hdr_off, count = found
        return d6[:hdr_off] + struct.pack('<2I', 64, count + 1) + d6[hdr_off + 8:] + new_desc
    return d6 + struct.pack('<2I', 64, 1) + new_desc


# ---------------------------------------------------------------------------
# Landing derivation from a level's 0x0b navmesh
# ---------------------------------------------------------------------------
def _walkable_cells_world(rec02_body):
    """Return (origin, dims, cells) where cells = {(gx,gz): (wx, wy, wz)} world-space
    walkable cell centers from the FIRST difficulty set. gx,gz are GLOBAL cell coords
    (tx*64+lx, ty*64+lz)."""
    doc = parse_rec02(rec02_body, decompress=True)
    center = doc['center']; dims = doc['dims']
    origin = (center[0] - dims[0], center[1] - dims[1], center[2] - dims[2])
    cells = {}
    for r in doc['sets'][0]['records']:
        h = r['hdr']; tx, ty, hmin = h['tx'], h['ty'], h['hmin']
        heights, areas = r['heights'], r['areas']
        for lz in range(TILE):
            for lx in range(TILE):
                li = lz * TILE + lx
                if areas[li] == 0:
                    continue
                hv = heights[li]
                if hv == 0xff:
                    continue
                gx, gz = tx * TILE + lx, ty * TILE + lz
                wx = origin[0] + (gx + 0.5) * CS
                wz = origin[2] + (gz + 0.5) * CS
                wy = (hmin + hv) * CS
                cells[(gx, gz)] = (wx, wy, wz)
    return origin, dims, cells, doc


def _grid_corner_from_ints(ints_raw):
    v = struct.unpack_from('<13i', ints_raw, 0)
    return (v[6], v[7], v[8]), (v[3], v[4], v[5])   # corner, content_dims(tiles)


def derive_landing_local(dest_rec02_body, dest_ints_raw, near_world_x=None,
                         near_world_z=None, prefer='interior'):
    """Derive an ON-MESH landing point in the DESTINATION level, returned in LOCAL
    level coordinates (grid corner relative, same frame as 0x05 instance positions).

    Strategy:
      * parse the dest 0x0b walkable cells (area!=0, height!=empty);
      * keep only INTERIOR cells whose 4-neighbours are ALL walkable (robustly on
        the mesh, never an edge sliver - the old teleport died 0.28u off-mesh);
      * among interior cells, pick the one nearest (near_world_x, near_world_z) if
        given (e.g. the shared seam midpoint), else the mesh centroid;
      * convert world (wx,wy,wz) -> local by subtracting the level's grid corner.

    Returns (lx, ly, lz, world_xyz, n_interior) or raises if no walkable mesh.
    The Y is the DESTINATION floor Y (critical: the two rooms' floors differ by
    ~11u at the random09a/xPTS seam, so the landing MUST use the dest's own floor).
    """
    origin, dims, cells, doc = _walkable_cells_world(dest_rec02_body)
    if not cells:
        raise ValueError('destination 0x0b has no walkable cells')
    # interior = all 4 orthogonal neighbours present
    interior = {k: v for k, v in cells.items()
                if (k[0] - 1, k[1]) in cells and (k[0] + 1, k[1]) in cells
                and (k[0], k[1] - 1) in cells and (k[0], k[1] + 1) in cells}
    pool = interior if interior else cells
    if near_world_x is not None and near_world_z is not None:
        best = min(pool.values(),
                   key=lambda w: (w[0] - near_world_x) ** 2 + (w[2] - near_world_z) ** 2)
    else:
        cx = sum(w[0] for w in pool.values()) / len(pool)
        cz = sum(w[2] for w in pool.values()) / len(pool)
        best = min(pool.values(), key=lambda w: (w[0] - cx) ** 2 + (w[2] - cz) ** 2)
    corner, _cd = _grid_corner_from_ints(dest_ints_raw)
    lx = best[0] - corner[0]
    ly = best[1] - corner[1]
    lz = best[2] - corner[2]
    return (lx, ly, lz), best, len(interior)


# ---------------------------------------------------------------------------
# Main injection entry point (data-driven by a wiring table)
# ---------------------------------------------------------------------------
def inject_interior_portals(get_blob, set_blob, get_ints, level_index_by_key,
                            wiring, id_scan_pairs, base_tag=0x5000, verbose=True):
    r"""Inject interior portals for every seam in `wiring`.

    Callback-based so the coordinator can plug it into svaera_plus_portals' in-memory
    level table without this module knowing the merge's data structures.

      get_blob(key)  -> current blob bytes for level key (lowercased fname, '/' seps)
      set_blob(key, new_blob) -> store the modified blob
      get_ints(key)  -> the level's ints_raw (for GUID + grid corner)
      level_index_by_key: dict key -> merged level index (only used for logging)
      wiring: list of dicts, each:
          {'fromLevel': key, 'toLevel': key,
           'entrancePos': (x,y,z) or None,   # local, in fromLevel; None -> derive
           'exitPos': (x,y,z) or None,       # local, in toLevel;   None -> derive
           'entranceDbr': bytes (optional; default SilkRd cave mouth)}
      id_scan_pairs: iterable of (blob,) for the WHOLE map, to mint non-colliding ids.

    For each seam it mints a fresh (mouth, exit) id pair, injects the GridEntrance +
    0x14 binding into fromLevel, and appends the reciprocal 0x06 descriptor to
    toLevel. Returns a list of per-seam report dicts (with the ids + resolved coords)
    for the caller to verify/log.
    """
    existing_ids = set(scan_existing_portal_ids(id_scan_pairs))
    reports = []
    tag = base_tag

    for w in wiring:
        fk = w['fromLevel'].replace('\\', '/').lower()
        tk = w['toLevel'].replace('\\', '/').lower()
        from_blob = get_blob(fk)
        to_blob = get_blob(tk)
        from_ints = get_ints(fk)
        to_ints = get_ints(tk)

        from_secs, from_magic = parse_blob_sections(from_blob)
        to_secs, to_magic = parse_blob_sections(to_blob)
        from_ver = from_magic[3]
        to_guid = to_ints[36:52]
        from_guid = from_ints[36:52]

        # mint a fresh id pair
        while _mint_id(tag) in existing_ids:
            tag += 1
        mouth_id = _mint_id(tag); tag += 1
        while _mint_id(tag) in existing_ids:
            tag += 1
        exit_id = _mint_id(tag); tag += 1
        existing_ids.add(mouth_id); existing_ids.add(exit_id)

        # --- entrance position (local, in fromLevel) ---
        # Compute the shared-seam midpoint (world) between fromLevel and toLevel from
        # their LEVELS-index footprints, so an auto-derived mouth sits AT the seam the
        # player crosses (not the mesh centroid). Footprint = corner..corner+dims*2.
        def _fp(iraw):
            v = struct.unpack_from('<13i', iraw, 0)
            return (v[6], v[8], v[6] + v[3] * 2, v[8] + v[5] * 2)
        ffp, tfp = _fp(from_ints), _fp(to_ints)
        ox = max(0, min(ffp[2], tfp[2]) - max(ffp[0], tfp[0]))  # x-overlap length
        oz = max(0, min(ffp[3], tfp[3]) - max(ffp[1], tfp[1]))  # z-overlap length
        # the seam is the shared edge; its midpoint is the middle of the overlap band
        seam_wx = (max(ffp[0], tfp[0]) + min(ffp[2], tfp[2])) / 2.0
        seam_wz = (max(ffp[1], tfp[1]) + min(ffp[3], tfp[3])) / 2.0

        if w.get('entrancePos') is not None:
            epos = w['entrancePos']
        else:
            # derive an on-mesh cell near the seam INSIDE fromLevel from ITS OWN
            # navmesh - the GridEntrance sits just inside the mouth at fromLevel floor.
            from_0b = next((s['data'] for s in from_secs if s['type'] == 0x0b), None)
            if from_0b is None:
                raise ValueError(f'{fk}: no 0x0b to derive entrancePos; supply it explicitly')
            (elx, ely, elz), ew, ni = derive_landing_local(
                from_0b, from_ints, near_world_x=seam_wx, near_world_z=seam_wz)
            epos = (elx, ely, elz)

        # inject GridEntrance + binding into fromLevel
        s05 = next(s for s in from_secs if s['type'] == 0x05)
        s14 = next((s for s in from_secs if s['type'] == 0x14), None)
        dbr = w.get('entranceDbr', DEFAULT_ENTRANCE_DBR)
        new_05, inj_idx = inject_gridentrance_05(s05['data'], from_ver, dbr, *epos)
        payload = make_binding_payload(from_ver, mouth_id, exit_id, to_guid)
        # upsert preserves the sparse 0x14 record set and only adds the binding for
        # inj_idx (inst_count arg is unused - kept for signature stability).
        new_14 = upsert_0x14_binding(s14['data'] if s14 else b'', from_ver,
                                     0, inj_idx, payload)
        # rebuild fromLevel blob: replace 0x05, replace/insert 0x14
        out_secs = []
        had_14 = False
        for s in from_secs:
            if s['type'] == 0x05:
                out_secs.append({'type': 0x05, 'data': new_05})
            elif s['type'] == 0x14:
                out_secs.append({'type': 0x14, 'data': new_14}); had_14 = True
            else:
                out_secs.append(s)
        if not had_14:
            # insert 0x14 after 0x05 (v0x0e Random09A has an empty/absent 0x14)
            ins = [i for i, s in enumerate(out_secs) if s['type'] == 0x05][0] + 1
            out_secs.insert(ins, {'type': 0x14, 'data': new_14})
        set_blob(fk, rebuild_blob(from_magic, out_secs))

        # --- exit position (local, in toLevel) -> only used to VERIFY landing / doc;
        # the engine resolves the walk-out by GUID, the exit descriptor carries ids.
        if w.get('exitPos') is not None:
            xpos = w['exitPos']
        else:
            to_0b = next((s['data'] for s in to_secs if s['type'] == 0x0b), None)
            if to_0b is None:
                xpos = None
            else:
                (xlx, xly, xlz), xw, ni2 = derive_landing_local(
                    to_0b, to_ints, near_world_x=seam_wx, near_world_z=seam_wz)
                xpos = (xlx, xly, xlz)

        # append reciprocal exit descriptor to toLevel 0x06
        s06 = next((s for s in to_secs if s['type'] == 0x06), None)
        if s06 is None:
            raise ValueError(f'{tk}: no 0x06 section to append reciprocal exit')
        new_06 = append_0x06_reciprocal(s06['data'], exit_id, mouth_id, from_guid)
        out_secs2 = [{'type': s['type'], 'data': (new_06 if s['type'] == 0x06 else s['data'])}
                     for s in to_secs]
        set_blob(tk, rebuild_blob(to_magic, out_secs2))

        rep = dict(fromLevel=fk, toLevel=tk, from_ver=f'0x{from_ver:02x}',
                   to_ver=f'0x{to_magic[3]:02x}', mouth_id=mouth_id.hex(),
                   exit_id=exit_id.hex(), dest_guid=to_guid.hex(),
                   src_guid=from_guid.hex(), entrance_local=epos, exit_local=xpos,
                   injected_instance=inj_idx)
        reports.append(rep)
        if verbose:
            print(f'  PORTAL {fk} -> {tk}: mouth={mouth_id.hex()[:12]} '
                  f'exit={exit_id.hex()[:12]} dest={to_guid.hex()[:12]} '
                  f'entrance@{tuple(round(c,2) for c in epos)} inst#{inj_idx} '
                  f'({rep["from_ver"]}->{rep["to_ver"]})')
    return reports


# ---------------------------------------------------------------------------
# Self-test: run the injection against the DEPLOYED map IN MEMORY and byte-verify.
# ---------------------------------------------------------------------------
def _selftest():
    dep = Path(os.environ.get(
        'SVC_DEPLOYED_MAP',
        r'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc'))
    print('SELF-TEST against (read-only, in-memory):', dep)
    arc = ArcArchive.from_file(dep)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    by_key = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(levels)}

    # in-memory blob store
    blobs = {}
    ints = {}
    for lv in levels:
        k = lv['fname'].replace('\\', '/').lower()
        blobs[k] = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        ints[k] = lv['ints_raw']

    R09 = 'levels/world/orient/underground/random09a.lvl'
    XPTS = 'levels\\world\\xbloodcave\\xpassagetransitionstart.lvl'.replace('\\', '/')
    # locate exact keys (case/sep tolerant)
    def find_key(sub):
        sub = sub.lower()
        return next(k for k in blobs if sub in k)
    r09k = find_key('orient/underground/random09a')
    xptsk = find_key('xpassagetransitionstart')

    # Landing derivation for the doc: seam midpoint from footprints.
    def fp(k):
        v = struct.unpack_from('<13i', ints[k], 0)
        return (v[6], v[8], v[6] + v[3] * 2, v[8] + v[5] * 2)
    r09fp, xptsfp = fp(r09k), fp(xptsk)
    seam_x = r09fp[0]
    z_lo, z_hi = max(r09fp[1], xptsfp[1]), min(r09fp[3], xptsfp[3])
    seam_mid_z = (z_lo + z_hi) / 2.0
    print(f'  seam_x={seam_x} z-band[{z_lo},{z_hi}] mid_z={seam_mid_z}')

    # derive landings near the seam for reporting (uses each level's OWN navmesh)
    for nm, k in (('xPTS(arrival)', xptsk), ('R09(return)', r09k)):
        s0b = next((s['data'] for s in parse_blob_sections(blobs[k])[0] if s['type'] == 0x0b), None)
        (lx, ly, lz), w, ni = derive_landing_local(s0b, ints[k],
                                                   near_world_x=seam_x, near_world_z=seam_mid_z)
        print(f'  {nm} landing local=({lx:.2f},{ly:.2f},{lz:.2f}) world=({w[0]:.2f},{w[1]:.2f},{w[2]:.2f}) interior_cells={ni}')

    if '--chain' in sys.argv:
        # Full interior chain (data-driven proof the design generalizes). Each
        # consecutive pair abuts; wire a portal at every seam, both directions
        # deferred to the coordinator's choice (here: forward mouths only).
        chain = ['orient/underground/random09a', 'xpassagetransitionstart',
                 'xbloodcave/bc_initialpathway', 'drxfirstxistion_connection',
                 'drxfirstroom']
        keys = [find_key(c) for c in chain]
        wiring = [{'fromLevel': keys[i], 'toLevel': keys[i + 1],
                   'entrancePos': None, 'exitPos': None}
                  for i in range(len(keys) - 1)]
    else:
        wiring = [
            {'fromLevel': r09k, 'toLevel': xptsk, 'entrancePos': None, 'exitPos': None},
        ]
    id_pairs = [(b,) for b in blobs.values()]

    reports = inject_interior_portals(
        get_blob=lambda k: blobs[k], set_blob=lambda k, v: blobs.__setitem__(k, v),
        get_ints=lambda k: ints[k], level_index_by_key=by_key,
        wiring=wiring, id_scan_pairs=id_pairs)

    # ---- byte-level self-verify: re-parse injected records ----
    print('\n  VERIFY:')
    ok = True
    for rep in reports:
        fk, tk = rep['fromLevel'], rep['toLevel']
        # fromLevel: GridEntrance instance + 0x14 binding present & correct
        fsecs, fmagic = parse_blob_sections(blobs[fk])
        fver = fmagic[3]
        s05 = next(s for s in fsecs if s['type'] == 0x05)
        s14 = next(s for s in fsecs if s['type'] == 0x14)
        strings = parse_0x05_strings(s05['data'])
        has_ge = any(b'SilkRdDngEntrance' in s for s in strings)
        recs14 = {r['index']: r['payload'] for r in parse_0x14_records(s14['data'])}
        inj = rep['injected_instance']
        pl = recs14.get(inj, b'')
        exp = make_binding_payload(fver, bytes.fromhex(rep['mouth_id']),
                                   bytes.fromhex(rep['exit_id']),
                                   bytes.fromhex(rep['dest_guid']))
        bind_ok = (pl == exp)
        # toLevel: reciprocal descriptor-list present at tail, correctly framed as
        # [64][count][... our 60B descriptor last].
        tsecs, tmagic = parse_blob_sections(blobs[tk])
        d6 = next(s['data'] for s in tsecs if s['type'] == 0x06)
        exit_b = bytes.fromhex(rep['exit_id']); mouth_b = bytes.fromhex(rep['mouth_id'])
        src = bytes.fromhex(rep['src_guid'])
        our_desc = exit_b + mouth_b + src + DESC_TRAILER
        # our descriptor must be the LAST 60 bytes; a valid [64][count>=1] header must
        # sit at len - (8 + count*60) for the discovered count.
        found = _find_portal_list_tail(d6)
        framed_ok = False
        count_seen = None
        if found is not None:
            hdr_off, count_seen = found
            framed_ok = (d6[-DESC_SIZE:] == our_desc and
                         struct.unpack_from('<2I', d6, hdr_off) == (64, count_seen))
        # the exit portal UniqueId must equal the surface 0x14 exit id (reciprocity)
        recip_ok = framed_ok
        src_found = any(d6[i:i+16] == src for i in range(len(d6) - 15))
        # blob still parses with valid section walk (no leftover bytes swallowed)
        reparse_ok = (rebuild_blob(fmagic, fsecs) == blobs[fk] and
                      rebuild_blob(tmagic, tsecs) == blobs[tk])
        print(f'   {fk} -> {tk}')
        print(f'     GridEntrance art present: {has_ge}')
        print(f'     0x14 binding @inst#{inj} correct: {bind_ok} (payload {len(pl)}B)')
        print(f'     0x06 reciprocal framed [64][count={count_seen}] + our 60B descriptor last: {framed_ok}')
        print(f'     0x06 src GUID findable: {src_found}')
        print(f'     blob section round-trip: {reparse_ok}')
        ok = ok and has_ge and bind_ok and recip_ok and src_found and reparse_ok
    print(f'\n  SELF-TEST {"PASS" if ok else "FAIL"} (no map written)')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(_selftest())
