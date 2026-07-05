#!/usr/bin/env python3
"""
Build merged Levels.arc: SVAERA clean base + SV-only levels + portal NPCs.

Strategy: Keep SVAERA's map untouched (no invisible wall), add SV's custom
levels (UberDungeon, xBloodCave, BossArena, Secret_Place) as disconnected
areas, and inject portal NPCs to connect them.

No shared+drxmap level replacements - those caused the invisible wall.
"""
import sys, os, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, parse_quests,
    parse_bitmap_index, build_level_index, build_quests, build_bitmap_index,
    MAP_MAGIC, SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS)
from build_section_surgery import (
    INJECT_SPECS, ALL_CUSTOM_QUEST_NAMES, inject_into_0x05_v11,
    parse_blob_sections, rebuild_blob, convert_v0e_blob_to_v11,
    inject_into_sv_only_blob, inject_rec02_into_blob)

# --- GROUPS parsing ---
def _find_next_groups_record(data, start, end_limit):
    for scan in range(start, min(end_limit, len(data) - 12)):
        sub = struct.unpack_from('<I', data, scan)[0]
        if sub > 20: continue
        slen = struct.unpack_from('<I', data, scan + 4)[0]
        if slen < 3 or slen > 200 or scan + 8 + slen > len(data): continue
        s = data[scan+8:scan+8+slen]
        if not all(32 <= b < 127 for b in s): continue
        pos2 = scan + 8 + slen
        if pos2 + 4 > len(data): continue
        slen2 = struct.unpack_from('<I', data, pos2)[0]
        if slen2 < 3 or slen2 > 200 or pos2 + 4 + slen2 > len(data): continue
        s2 = data[pos2+4:pos2+4+slen2]
        if all(32 <= b < 127 for b in s2): return scan
    return None

def _parse_groups(data):
    val0, count = struct.unpack_from('<II', data, 0)
    pos = 8
    records = []
    for i in range(count):
        sub_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        name_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
        name = data[pos:pos+name_len].decode('ascii', errors='replace'); pos += name_len
        cat_len = struct.unpack_from('<I', data, pos)[0]; pos += 4
        category = data[pos:pos+cat_len].decode('ascii', errors='replace'); pos += cat_len
        member_count = struct.unpack_from('<I', data, pos)[0]; pos += 4
        data_start = pos
        if i < count - 1:
            nxt = _find_next_groups_record(data, pos, pos + 200000)
            data_len = (nxt - pos) if nxt else (len(data) - pos)
        else:
            data_len = len(data) - pos
        records.append({'sub_count': sub_count, 'name': name, 'category': category,
                        'member_count': member_count, 'raw_data': data[data_start:data_start+data_len]})
        pos = data_start + data_len
    return val0, records

def _rebuild_groups(val0, records):
    out = bytearray(struct.pack('<II', val0, len(records)))
    for rec in records:
        name_b = rec['name'].encode('ascii')
        cat_b = rec['category'].encode('ascii')
        out += struct.pack('<I', rec['sub_count'])
        out += struct.pack('<I', len(name_b)) + name_b
        out += struct.pack('<I', len(cat_b)) + cat_b
        out += struct.pack('<I', rec['member_count'])
        out += rec['raw_data']
    return bytes(out)

# --- Grid shift (single source of truth) ---
# Move blood cave levels into the active SVAERA world grid so the engine includes
# them for pathfinding activation. Used BOTH when repositioning/writing a 0x0b
# navmesh (step 7b + the Random09A swap) and when writing the merged LEVELS index
# (step 8); they must agree so a navmesh header center (grid_corner + half_dims)
# matches the level's final merged grid corner.
#
# PLACEMENT-BUG FIX (2026-07-05, v2 - the real fix): the swapped Random09A doorway
# cave fails the engine's navmesh-load GUID gate, so the HiddenValley01 cave mouth
# stays an invisible wall. Byte+disasm-proven mechanism: a level's 0x0b navmesh
# lists own + neighbor level GUIDs, and the engine loads that navmesh ONLY if EVERY
# listed GUID is currently STREAM-RESIDENT. Random09A correctly lists its neighbor
# xPassageTransitionStart (needed to stitch the tunnel seam; 57/57 shipping
# connected-dungeon levels list their neighbors, so we do NOT strip it). The bug:
# at the earlier shifts Random09A's footprint EDGE-TOUCHED a SURFACE level
# (HighAltituedBorder01 at x=-198), so the surface streamed Random09A in EARLY,
# before its cave-neighbor xPTS was resident -> GUID gate fails -> navmesh never
# loads -> mouth wall. (The prior (1583,0,968) only removed AREA overlap; the
# residual edge-touch alone still triggers the early surface stream-in.) Every
# WORKING base-game cave interior is an ISOLATED ISLAND: zero footprint overlap AND
# zero edge-touch with any surface/non-cave level, so it only loads as a complete
# unit via the mouth portal, all its rooms co-resident.
#
# FIX = relocate the WHOLE blood-cave cluster (31 levels: 30 xBloodCave-path +
# swapped Random09A) RIGIDLY into empty map space with a real CLEARANCE GAP from
# every non-cluster level, eliminating the surface edge-touch. New total shift
# (7840,0,2030) parks the cluster at X[3426,6059] Z[2629,3545] - a genuine empty
# gap well inside the populated non-cluster map extent (X[-13017,17702]
# Z[-17793,8052]), coords comparable to existing levels. Measured MIN clearance to
# ANY of the 2251 non-cluster spatial levels = 3001.8 world-units (>> the 512
# preferred / 256 minimum target that mirrors the isolated-island pattern; nearest
# neighbours are SilkRoad/JadePalace/Atlantis-cave levels, all >= 3001.8u). NO
# overlap, NO edge-touch anywhere. A rigid shift preserves every intra-cluster seam
# automatically: Random09A's west edge still exactly abuts xPassageTransitionStart's
# east edge (both at x=5979, with an 80-unit z-overlap - identical to before the
# move), so the R09<->xPTS tunnel hand-off is unchanged. Both GRID_SHIFT keys MUST
# carry the identical delta or the seam breaks. gen_bc_navmeshes.py imports this
# dict, so the donors follow automatically (rerun it after any change here).
GRID_SHIFT = {
    'xbloodcave': (7840, 0, 2030),  # dx, dy, dz  (was (1583,0,968); relocated to empty map space, 3001.8u clearance)
    # Relocate the hijacked Silk Road cave (blood-cave walk-in) by the SAME shift
    # so its west edge stays abutting the shifted xPassageTransitionStart. Matched
    # by substring, so this key hits ONLY Random09A (path is
    # Levels/World/Orient/Underground/Random09A.lvl).
    'orient/underground/random09a': (7840, 0, 2030),
}


def shifted_ints_raw(lv):
    """Return a level's ints_raw with GRID_SHIFT applied to its grid corner.

    Grid corner (world x,y,z) is ints_raw[6,7,8] at byte offset 24. Mirrors the
    shift applied in step 8's merged_levels build so a transplanted 0x0b header
    center (grid_corner + half_dims) lands at the level's FINAL merged position.
    Returns the original ints_raw unchanged if no GRID_SHIFT pattern matches.
    """
    key = lv['fname'].replace('\\', '/').lower()
    for pattern, (dx, dy, dz) in GRID_SHIFT.items():
        if pattern in key:
            raw = bytearray(lv['ints_raw'])
            ox, oy, oz = struct.unpack_from('<iii', raw, 24)
            struct.pack_into('<iii', raw, 24, ox + dx, oy + dy, oz + dz)
            return bytes(raw)
    return lv['ints_raw']


def extract_0x0b_body(lvl_path):
    """Extract the 0x0b (REC\\x02) section body from a standalone baked .lvl file.

    Reuses the repo's parse_blob_sections. Returns the raw 0x0b section bytes
    (the full REC\\x02 section, header + mesh) or None if the file has no 0x0b.
    """
    try:
        blob = Path(lvl_path).read_bytes()
    except OSError:
        return None
    secs, _magic = parse_blob_sections(blob)
    for s in secs:
        if s['type'] == 0x0b:
            return s['data']
    return None


# --- Donor directory (generated / harvested navmeshes) ---
# Default: local/editor_normalized/ (override via SVC_DONOR_DIR). Two donor
# kinds live here, keyed by level basename:
#   1. <basename>.0b.bin  = a PRE-POSITIONED raw 0x0b section produced offline by
#      tools/gen_bc_navmeshes.py. Its GUID list already resolves in the merged
#      world and its center is already shifted to the merged grid, so it is
#      injected VERBATIM (no transplant). This is the actual blood-cave fix.
#   2. <basename>.lvl     = a full baked .lvl donor (e.g. from a future TQAE
#      Editor bake). Its 0x0b is extracted and REPOSITIONED via transplant_rec02
#      to the level's shifted grid.
# If neither exists we fall back to the dead 148-byte stub so the build stays
# green (used by the 7 ocean-scenery levels with no walkable geometry).
DONOR_DIR = Path(os.environ.get(
    'SVC_DONOR_DIR',
    r'c:\Users\willi\repos\tqit_soulvizier_classic\local\editor_normalized'))


def find_pre_positioned_donor(lv):
    """Look up a pre-positioned generated 0x0b for a level by basename.

    Returns (raw_0x0b_bytes, donor_path) if <DONOR_DIR>/<basename>.0b.bin exists
    and looks like a REC\\x02 section, else (None, None). This file is a raw 0x0b
    section (not a .lvl blob), so it is read directly, not parsed for sections.
    """
    basename = lv['fname'].replace('\\', '/').split('/')[-1]  # e.g. BC_initialpathway.lvl
    donor_path = DONOR_DIR / f'{basename}.0b.bin'
    if not donor_path.is_file():
        return None, None
    try:
        body = donor_path.read_bytes()
    except OSError:
        return None, None
    if len(body) < 12 or body[:4] != b'REC\x02':
        return None, None
    return body, donor_path


# Tolerance (world-units) for the donor-freshness center check. The layout
# invariant center == corner-16+dims holds only up to tile-grid rounding: the
# donor's stored dims come from the rasterizer (ceil(2*extent/CS) tiling +
# erosion), so on levels with odd 0x0a half-extents the donor center legitimately
# differs from corner-16+dims by up to 2 world-units (measured max = 2 across all
# 24 tier-1 blood-cave donors). A genuine STALE-GRID_SHIFT donor - the class this
# gate exists to catch - is off by the shift delta on x and/or z, i.e. hundreds to
# thousands of world-units, so a small tolerance keeps full stale-shift protection
# while not false-tripping on odd geometry.
DONOR_FRESH_TOL = 32


def assert_donor_fresh(donor, target_ints, name):
    """Fail loud if a pre-positioned donor was generated at a different GRID_SHIFT.

    A pre-positioned 0x0b is injected VERBATIM, so a donor regenerated at some
    other (e.g. abandoned/experimental) shift silently places the navmesh
    kilometres from its level (2026-07-05 corruption class: a size-only check
    passes because only the 12-byte center differs). Layout invariant on healthy
    donors: center == index corner - 16 + dims on the x and z axes, up to
    DONOR_FRESH_TOL world-units of tile-grid rounding (see the constant note).
    """
    gc = struct.unpack_from('<I', donor, 12)[0]
    pos = 16 + gc * 16
    cx, _cy, cz = struct.unpack_from('<3i', donor, pos)
    dx, _dy, dz = struct.unpack_from('<3I', donor, pos + 12)
    ints = struct.unpack_from('<13i', target_ints, 0)
    exp_x, exp_z = ints[6] - 16 + dx, ints[8] - 16 + dz
    if abs(cx - exp_x) > DONOR_FRESH_TOL or abs(cz - exp_z) > DONOR_FRESH_TOL:
        raise SystemExit(
            f'STALE DONOR {name}: 0x0b center ({cx},{cz}) != expected ({exp_x},{exp_z}) '
            f'+/-{DONOR_FRESH_TOL} for grid corner ({ints[6]},{ints[8]}). Donors were '
            f'generated at a different GRID_SHIFT - rerun: py tools/gen_bc_navmeshes.py')


def find_donor_0x0b(lv):
    """Look up a full baked .lvl donor for an SV-only level by basename.

    Returns (donor_0x0b_bytes, donor_path) if <DONOR_DIR>/<basename>.lvl exists
    and contains a 0x0b section, else (None, None). The returned 0x0b still needs
    transplant_rec02 repositioning (it is NOT pre-positioned).
    """
    basename = lv['fname'].replace('\\', '/').split('/')[-1]  # e.g. BC_initialpathway.lvl
    donor_path = DONOR_DIR / basename
    if not donor_path.is_file():
        return None, None
    body = extract_0x0b_body(donor_path)
    if body is None:
        return None, None
    return body, donor_path


def main():
    """Build the merged Levels.arc (heavy: multi-GB). Not run on import."""
    # --- Paths ---
    svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
    sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
    out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

    # --- Load maps ---
    print('Loading SVAERA...')
    ae_arc = ArcArchive.from_file(svaera_path)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
    ae_quests = parse_quests(ae_data, ae_sec[SEC_QUESTS])
    ae_bitmaps = parse_bitmap_index(ae_data, ae_sec[SEC_BITMAPS])
    ae_bmp_unknown = struct.unpack_from('<I', ae_data, ae_sec[SEC_BITMAPS]['data_offset'])[0]

    # Donor pool no longer needed - using minimal REC\x02 stubs instead.
    # The engine's built-in Recast generator (ProcessRLTD_flow @ VA 0x101F6210)
    # builds navmeshes from level geometry at runtime when the RLTD handler has
    # valid Recast parameters but no pre-built tiles.

    print('Loading SV...')
    sv_arc_obj = ArcArchive.from_file(sv_path)
    sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
    sv_sec = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])
    sv_quests = parse_quests(sv_data, sv_sec[SEC_QUESTS])
    sv_bitmaps = parse_bitmap_index(sv_data, sv_sec[SEC_BITMAPS])

    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}

    print(f'  SVAERA: {len(ae_levels)} levels, SV: {len(sv_levels)} levels')

    # --- 1. Identify SV-only levels (not in SVAERA) ---
    sv_only = []
    for lv in sv_levels:
        key = lv['fname'].replace('\\', '/').lower()
        if key not in ae_by_name:
            sv_only.append(lv)
    print(f'\n  SV-only levels to add: {len(sv_only)}')

    # --- 2. GROUPS: SV's + SVAERA-only ---
    print('\n=== Merging GROUPS ===')
    sv_groups_raw = sv_data[sv_sec[SEC_GROUPS]['data_offset']:
                            sv_sec[SEC_GROUPS]['data_offset'] + sv_sec[SEC_GROUPS]['size']]
    ae_groups_raw = ae_data[ae_sec[SEC_GROUPS]['data_offset']:
                            ae_sec[SEC_GROUPS]['data_offset'] + ae_sec[SEC_GROUPS]['size']]
    sv_g_val0, sv_g_recs = _parse_groups(sv_groups_raw)
    _, ae_g_recs = _parse_groups(ae_groups_raw)
    sv_g_names = set(r['name'] for r in sv_g_recs)
    ae_only_recs = [r for r in ae_g_recs if r['name'] not in sv_g_names]
    merged_groups = _rebuild_groups(sv_g_val0, sv_g_recs + ae_only_recs)
    print(f'  SV: {len(sv_g_recs)}, SVAERA-only: {len(ae_only_recs)}, merged: {len(sv_g_recs) + len(ae_only_recs)}')

    # --- 3. SD: SV's (blood cave zone definitions) ---
    sv_sd = sv_data[sv_sec[SEC_SD]['data_offset']:
                    sv_sec[SEC_SD]['data_offset'] + sv_sec[SEC_SD]['size']]
    print(f'  Using SV SD: {len(sv_sd)} bytes')

    # --- 4. QUESTS: merged + custom ---
    ae_quest_set = set(q.lower() if isinstance(q, str) else q.lower() for q in ae_quests)
    new_quests = [q for q in sv_quests if (q.lower() if isinstance(q, str) else q.lower()) not in ae_quest_set]
    merged_quests = ae_quests + new_quests
    existing_lower = set(q.lower() if isinstance(q, str) else q.decode('ascii', errors='replace').lower()
                         for q in merged_quests)
    added_quests = 0
    for qname in ALL_CUSTOM_QUEST_NAMES:
        if qname.lower() not in existing_lower:
            merged_quests.append(qname.encode('ascii'))
            existing_lower.add(qname.lower())
            added_quests += 1
    new_quests_data = build_quests(merged_quests)
    print(f'  Quests: {len(ae_quests)} + {len(new_quests)} SV + {added_quests} custom = {len(merged_quests)}')

    # --- 5. Load SV-only level blobs (will convert to v0x11 after NPC injection) ---
    print('\n=== Loading SV-only level blobs ===')
    converted_blobs = {}  # sv_only index -> blob
    v0e_count = v11_count = other_count = 0
    for i, lv in enumerate(sv_only):
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        converted_blobs[i] = blob
        if len(blob) >= 4 and blob[:3] == b'LVL':
            ver = blob[3]
            if ver == 0x0e:
                v0e_count += 1
            elif ver == 0x11:
                v11_count += 1
            else:
                other_count += 1
        else:
            other_count += 1
    print(f'  v0x0e: {v0e_count}, v0x11: {v11_count}, other: {other_count}')

    # --- 6. Inject portal NPCs into level blobs ---
    print('\n=== Injecting portal NPCs ===')

    # Build lookup: level key -> (source, index, blob)
    # "ae" levels are in ae_data, "sv_only" are in converted_blobs
    ae_inject_keys = {}
    for lv_key, specs in INJECT_SPECS.items():
        if lv_key in ae_by_name:
            ae_inject_keys[lv_key] = specs

    sv_inject_keys = {}
    for lv_key, specs in INJECT_SPECS.items():
        for i, lv in enumerate(sv_only):
            if lv['fname'].replace('\\', '/').lower() == lv_key:
                sv_inject_keys[i] = specs

    # Inject into SVAERA levels (these will be patched blobs)
    ae_patched_blobs = {}  # ae_level_index -> patched blob
    for lv_key, specs in ae_inject_keys.items():
        ae_idx = ae_by_name[lv_key]
        lv = ae_levels[ae_idx]
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        blob_ver = blob[3] if blob[:3] == b'LVL' else None

        if blob_ver == 0x11:
            secs, magic = parse_blob_sections(blob)
            for j, s in enumerate(secs):
                if s['type'] == 0x05:
                    secs[j] = {'type': 0x05, 'data': inject_into_0x05_v11(s['data'], specs)}
            ae_patched_blobs[ae_idx] = rebuild_blob(magic, secs)
            print(f'  Injected {len(specs)} NPC(s) into SVAERA {lv_key} (v0x11)')
        else:
            print(f'  WARN: {lv_key} is v0x{blob_ver:02x}, skipping injection')

    # Inject into SV-only levels
    for sv_idx, specs in sv_inject_keys.items():
        blob = converted_blobs[sv_idx]
        blob_ver = blob[3] if blob[:3] == b'LVL' else None
        lv_key = sv_only[sv_idx]['fname'].replace('\\', '/').lower()

        if blob_ver == 0x11:
            secs, magic = parse_blob_sections(blob)
            for j, s in enumerate(secs):
                if s['type'] == 0x05:
                    secs[j] = {'type': 0x05, 'data': inject_into_0x05_v11(s['data'], specs)}
            converted_blobs[sv_idx] = rebuild_blob(magic, secs)
            print(f'  Injected {len(specs)} NPC(s) into SV-only {lv_key} (v0x11)')
        elif blob_ver == 0x0e:
            converted_blobs[sv_idx] = inject_into_sv_only_blob(blob, specs, lv_key)
            print(f'  Injected {len(specs)} NPC(s) into SV-only {lv_key} (v0x0e)')
        else:
            print(f'  WARN: {lv_key} has unknown format v0x{blob_ver:02x}')

    # --- 7. Append 0x14 entries for injected instances (preserve originals) ---
    from build_section_surgery import count_0x05_instances, DEFAULT_0x14_PAYLOAD
    for ae_idx, patched_blob in ae_patched_blobs.items():
        secs, magic = parse_blob_sections(patched_blob)
        # Count total instances after injection
        new_count = 0
        for s in secs:
            if s['type'] == 0x05:
                new_count = count_0x05_instances(s['data'])
                break
        else:
            continue
        # Append new 0x14 entries for injected instances (keep original entries intact)
        new_secs = []
        for s in secs:
            if s['type'] == 0x14:
                # Original 0x14 data covers existing instances; append entries for new ones
                orig_data = bytearray(s['data'])
                # Parse existing 0x14 to count entries
                orig_entries = 0
                pos = 0
                while pos + 8 <= len(orig_data):
                    idx = struct.unpack_from('<I', orig_data, pos)[0]
                    psize = struct.unpack_from('<I', orig_data, pos + 4)[0]
                    pos += 8 + psize
                    orig_entries += 1
                # Append default entries for new instances (indices after original count)
                for idx in range(orig_entries, new_count):
                    orig_data += struct.pack('<II', idx, len(DEFAULT_0x14_PAYLOAD))
                    orig_data += DEFAULT_0x14_PAYLOAD
                new_secs.append({'type': 0x14, 'data': bytes(orig_data)})
                print(f'  0x14: kept {orig_entries} original + added {new_count - orig_entries} new entries')
            else:
                new_secs.append(s)
        ae_patched_blobs[ae_idx] = rebuild_blob(magic, new_secs)

    # --- 7b. Inject 0x0b (REC\x02) pathfinding into SV-only level blobs ---
    # SV-only levels ship with 0x0a (PTH\x04) pathfinding the TQAE engine cannot
    # parse. Each level is resolved against the donor dir (default
    # local/editor_normalized/ or SVC_DONOR_DIR) in THREE tiers:
    #
    #   1. GENERATED donor  <basename>.0b.bin  - a pre-positioned raw 0x0b built
    #      offline by tools/gen_bc_navmeshes.py. GUIDs already resolve in the
    #      merged world and the center is already shifted to the merged grid, so
    #      it is injected VERBATIM (pre_positioned=True, NO transplant). This is
    #      the actual blood-cave fix.
    #   2. LVL donor        <basename>.lvl      - a full baked .lvl (e.g. future
    #      Editor bake). Its 0x0b is extracted and REPOSITIONED to this level's
    #      SHIFTED grid via transplant_rec02.
    #   3. STUB             - no donor: inject the (dead) 148-byte stub so the
    #      build stays green. Used by the 7 ocean-scenery BC levels + anything
    #      still missing a donor.
    #
    # inject_rec02_into_blob always strips the 0x0a section so ProcessRLTD reinit
    # cannot clobber the 0x0b handler state. The SHIFTED ints_raw (grid corner +
    # GRID_SHIFT) is passed so tier-2/3 land at the level's FINAL merged position.
    print('\n=== Injecting 0x0b pathfinding into SV-only levels ===')
    print(f'  Donor dir: {DONOR_DIR}  (exists={DONOR_DIR.is_dir()})')
    gen_ok = 0
    lvl_ok = 0
    stub_ok = 0
    inject_fail = 0
    for i in range(len(sv_only)):
        blob = converted_blobs[i]
        lv = sv_only[i]
        target_ints = shifted_ints_raw(lv)  # carries the SHIFTED grid corner
        basename = lv['fname'].replace('\\', '/').split('/')[-1]

        gen_0x0b, gen_path = find_pre_positioned_donor(lv)
        lvl_0x0b, lvl_path = (None, None)
        if gen_0x0b is not None:
            # Tier 1: pre-positioned generated donor - insert as-is.
            assert_donor_fresh(gen_0x0b, target_ints, basename)
            result = inject_rec02_into_blob(blob, target_ints, donor_data=gen_0x0b,
                                            use_stub=False, pre_positioned=True)
            kind, donor_path, donor_len = 'generated', gen_path, len(gen_0x0b)
        else:
            lvl_0x0b, lvl_path = find_donor_0x0b(lv)
            if lvl_0x0b is not None:
                # Tier 2: full baked .lvl donor - transplant/reposition.
                result = inject_rec02_into_blob(blob, target_ints, donor_data=lvl_0x0b,
                                                use_stub=False)
                kind, donor_path, donor_len = 'lvl', lvl_path, len(lvl_0x0b)
            else:
                # Tier 3: no donor - stub fallback.
                result = inject_rec02_into_blob(blob, target_ints, use_stub=True)
                kind, donor_path, donor_len = 'stub', None, 0

        if result != blob:
            converted_blobs[i] = result
            if kind == 'generated':
                gen_ok += 1
                print(f'  GENERATED donor: {basename} <- {donor_path.name} ({donor_len} B 0x0b)')
            elif kind == 'lvl':
                lvl_ok += 1
                print(f'  LVL donor: {basename} <- {donor_path.name} ({donor_len} B 0x0b)')
            else:
                stub_ok += 1
        else:
            inject_fail += 1
            print(f'  {kind}: {basename} -> NO CHANGE (already has 0x0b or empty)')
    print(f'  Injected: {gen_ok} generated-donor / {lvl_ok} lvl-donor / {stub_ok} stub  '
          f'(of {len(sv_only)} SV-only)')
    if inject_fail:
        print(f'  Failed/skipped: {inject_fail}')

    # --- 7d. DIAGNOSTIC: Append a byte-for-byte SVAERA clone as level 2281+ ---
    # Tests whether there is a hidden append-time registration gate.
    # Clone ArcadiaDungeonPassage (idx 973, known-good SVAERA v0x0e level).
    # Shift grid to non-overlapping position. New unique GUID. Blob unchanged.
    CLONE_DONOR_IDX = 973
    CLONE_GRID_SHIFT = (80, 0, 0)  # one tile-width right of donor, adjacent for streaming
    _donor = ae_levels[CLONE_DONOR_IDX]
    _donor_blob = ae_data[_donor['data_offset']:_donor['data_offset'] + _donor['data_length']]

    # Build new LEVELS record: copy donor metadata, shift grid, new GUID
    _clone_ints = bytearray(_donor['ints_raw'])
    _orig_gx, _orig_gy, _orig_gz = struct.unpack_from('<iii', _clone_ints, 24)
    _new_gx = _orig_gx + CLONE_GRID_SHIFT[0]
    _new_gy = _orig_gy + CLONE_GRID_SHIFT[1]
    _new_gz = _orig_gz + CLONE_GRID_SHIFT[2]
    struct.pack_into('<iii', _clone_ints, 24, _new_gx, _new_gy, _new_gz)
    # Write a new unique GUID (deterministic, won't collide with any existing)
    struct.pack_into('<iiii', _clone_ints, 36, 0x7F000001, 0x7F000002, 0x7F000003, 0x7F000004)
    _clone_entry = {
        'ints_raw': bytes(_clone_ints),
        'dbr_raw': _donor['dbr_raw'],
        'dbr': _donor['dbr'],
        'fname_raw': _donor['fname_raw'],
        'fname': _donor['fname'],
        'data_offset': 0,  # patched later
        'data_length': len(_donor_blob),
    }
    # Store for use during map rebuild
    _append_clone_blob = _donor_blob
    _append_clone_entry = _clone_entry

    # Clone's bitmap: copy from donor (shifted later during bitmap fixup)
    _donor_bm = ae_bitmaps[CLONE_DONOR_IDX]

    _ir = struct.unpack_from('<13i', _clone_ints, 0)
    print(f'  APPEND-CLONE: Cloning SVAERA idx {CLONE_DONOR_IDX} as new appended level')
    print(f'    Donor: {_donor["fname"]}')
    print(f'    Blob: {len(_donor_blob)} bytes (unchanged)')
    print(f'    Grid: ({_orig_gx},{_orig_gy},{_orig_gz}) -> ({_new_gx},{_new_gy},{_new_gz})')
    print(f'    New GUID: [{_ir[9]}, {_ir[10]}, {_ir[11]}, {_ir[12]}]')
    print(f'    Donor bitmap: offset={_donor_bm["offset"]}, length={_donor_bm["length"]}')

    # --- 8. Rebuild map ---
    print('\n=== Rebuilding map ===')

    # Collect SVAERA sections we keep as-is
    ae_sections = parse_sections(ae_data)
    unk_sections = []
    for s in ae_sections:
        if s['type'] not in (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA):
            unk_sections.append((s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]))

    # DATA2 from SVAERA (base) + SV's DATA2 appended for SV-only levels
    data2_raw = bytearray(ae_data[ae_sec[SEC_DATA2]['data_offset']:
                                  ae_sec[SEC_DATA2]['data_offset'] + ae_sec[SEC_DATA2]['size']])
    orig_data2_len = len(data2_raw)

    # Build merged level list: all SVAERA levels + SV-only levels.
    # Apply GRID_SHIFT (defined once near the top) to each SV-only level's grid
    # corner via shifted_ints_raw so the world-grid position here MATCHES the
    # navmesh header center written in step 7b. The whole xBloodCave cluster +
    # Random09A move by the same shift (7840,0,2030), keeping the Random09A<->xPTS
    # grid-seam aligned while parking the WHOLE cluster in empty map space with a
    # 3001.8u clearance gap from every non-cluster level (Random09A corner
    # (5979,18,3243); see the GRID_SHIFT note for the placement fix).
    merged_levels = [dict(lv) for lv in ae_levels]
    grid_shifted = 0
    for i, lv in enumerate(sv_only):
        entry = dict(lv)
        new_ints = shifted_ints_raw(lv)
        if new_ints != lv['ints_raw']:
            entry['ints_raw'] = new_ints
            grid_shifted += 1
        merged_levels.append(entry)
    # Append the SVAERA clone as the final level
    merged_levels.append(_append_clone_entry)
    _clone_merged_idx = len(merged_levels) - 1
    print(f'  Grid-shifted {grid_shifted} SV-only levels for world grid connectivity')
    print(f'  Appended SVAERA clone at merged index {_clone_merged_idx}')

    # --- Blood-cave walk-in: swap SVAERA's Random09A blob for SV's (west tunnel) ---
    # Keep AE's GUID/fname/bitmap (index identity) so HiddenValley01's cave-mouth
    # 0x14 binding + xPTS's navmesh neighbor list still resolve. Take SV's blob (it
    # adds the west tunnel + the 0x0a edge to xPassageTransitionStart), shift its
    # grid corner by GRID_SHIFT so its west edge abuts the shifted xPTS, strip 0x0a,
    # and inject the pre-positioned generated 0x0b (own-GUID = AE's). This is an
    # in-place swap: no new level/GUID is added, so the level count + GUID set are
    # unchanged and xPTS needs no navmesh regen.
    R09_KEY = 'levels/world/orient/underground/random09a.lvl'
    ae_r09_idx = ae_by_name[R09_KEY]
    sv_r09_idx = sv_by_name[R09_KEY]
    sv_r09 = sv_levels[sv_r09_idx]
    sv_r09_blob = sv_data[sv_r09['data_offset']:sv_r09['data_offset'] + sv_r09['data_length']]

    # Shifted grid corner, but carry AE's GUID (ints_raw[9..12], bytes 36:52) so
    # the merged index identity stays AE's.
    swapped_ints = bytearray(shifted_ints_raw(sv_r09))              # SV dims + shifted corner
    swapped_ints[36:52] = ae_levels[ae_r09_idx]['ints_raw'][36:52]  # keep AE GUID
    # Inject the pre-positioned generated 0x0b (Random09A.lvl.0b.bin) + strip 0x0a.
    gen_0b, gen_path = find_pre_positioned_donor(sv_r09)            # basename Random09A.lvl -> .0b.bin
    assert gen_0b is not None, 'Random09A.lvl.0b.bin donor missing - run gen_bc_navmeshes.py'
    assert_donor_fresh(gen_0b, bytes(swapped_ints), 'Random09A.lvl')
    swapped_blob = inject_rec02_into_blob(sv_r09_blob, bytes(swapped_ints),
                                          donor_data=gen_0b, use_stub=False,
                                          pre_positioned=True)

    # Overwrite the merged Random09A entry in-place (index identity stays AE's).
    merged_levels[ae_r09_idx]['ints_raw'] = bytes(swapped_ints)
    # Record the swapped blob so the DATA-compaction loop writes it instead of AE's.
    _r09_swap = (ae_r09_idx, swapped_blob)
    _sw_ir = struct.unpack_from('<13i', swapped_ints, 0)
    print(f'  R09-SWAP: SVAERA Random09A (idx {ae_r09_idx}) blob <- SV ({len(sv_r09_blob)} B), '
          f'0x0b donor {gen_path.name} ({len(gen_0b)} B)')
    print(f'    corner ({_sw_ir[6]},{_sw_ir[7]},{_sw_ir[8]}) + AE GUID kept; '
          f'swapped blob {len(swapped_blob)} B')

    # Build merged bitmaps: SVAERA bitmaps + SV DATA2 entries for SV-only levels
    merged_bitmaps = list(ae_bitmaps)
    sv_only_data2 = {}
    sv_only_d2_count = 0
    for i, lv in enumerate(sv_only):
        lv_key = lv['fname'].replace(chr(92), '/').lower()
        sv_idx = sv_by_name.get(lv_key)
        if sv_idx is not None and sv_idx < len(sv_bitmaps) and sv_bitmaps[sv_idx]['length'] > 0:
            sv_bm = sv_bitmaps[sv_idx]
            sv_path_data = sv_data[sv_bm['offset']:sv_bm['offset'] + sv_bm['length']]
            offset_in_data2 = len(data2_raw)
            data2_raw += sv_path_data
            sv_only_data2[i] = (offset_in_data2, sv_bm['length'])
            sv_only_d2_count += 1
        else:
            sv_only_data2[i] = None
        merged_bitmaps.append({'offset': 0, 'length': 0, 'parts': 0, 'unknown': 0})

    # Append clone's bitmap (copy donor's DATA2 data)
    if _donor_bm['length'] > 0:
        _clone_bm_offset = len(data2_raw)
        _clone_bm_data = ae_data[_donor_bm['offset']:_donor_bm['offset'] + _donor_bm['length']]
        data2_raw += _clone_bm_data
        merged_bitmaps.append({'offset': 0, 'length': _donor_bm['length']})
        sv_only_data2[len(sv_only)] = (_clone_bm_offset, _donor_bm['length'])
        print(f'  Clone bitmap: {len(_clone_bm_data)} bytes appended to DATA2')
    else:
        merged_bitmaps.append({'offset': 0, 'length': 0})
        sv_only_data2[len(sv_only)] = None
        print(f'  Clone bitmap: donor has no bitmap data')

    # Append any pending bitmap data from replaced levels
    _replace_bm_offsets = {}  # ae_idx -> offset_in_data2
    for i in range(len(ae_bitmaps)):
        if isinstance(ae_bitmaps[i], dict) and '_pending_data' in ae_bitmaps[i]:
            _replace_bm_offsets[i] = len(data2_raw)
            data2_raw += ae_bitmaps[i]['_pending_data']
            print(f'  Appended replacement bitmap for idx {i} at DATA2 offset {_replace_bm_offsets[i]}')

    # Patch DATA2 level count to match merged level count
    # DATA2 header: uint32(0) + uint32(level_count) at offset 4
    orig_d2_count = struct.unpack_from('<I', data2_raw, 4)[0]
    struct.pack_into('<I', data2_raw, 4, len(merged_levels))
    print(f'  DATA2 level count: {orig_d2_count} -> {len(merged_levels)}')

    data2_raw = bytes(data2_raw)
    print(f'  SV-only DATA2: {sv_only_d2_count}/{len(sv_only)} levels, +{(len(data2_raw) - orig_data2_len)/(1024*1024):.1f} MB')

    # Calculate pre-data section layout
    new_levels_data = build_level_index(merged_levels)
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, ae_bmp_unknown)

    new_pre_data_size = 8  # MAP header
    new_pre_data_size += 8 + len(new_quests_data)
    new_pre_data_size += 8 + len(merged_groups)
    new_pre_data_size += 8 + len(sv_sd)
    new_pre_data_size += 8 + len(new_levels_data)
    new_pre_data_size += 8 + len(new_bitmaps_data)
    for _, ud in unk_sections:
        new_pre_data_size += 8 + len(ud)

    # DATA section: SVAERA blobs (with patches) + SV-only blobs
    print('  Building DATA section...')
    data_start = new_pre_data_size + 8 + len(data2_raw) + 8  # after DATA2 + DATA header
    compacted_data = bytearray()

    for i in range(len(ae_levels)):
        if i in ae_patched_blobs:
            blob = ae_patched_blobs[i]
        elif _r09_swap and i == _r09_swap[0]:
            blob = _r09_swap[1]                 # SV blob + shifted corner + generated 0x0b
        else:
            lv = ae_levels[i]
            blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        merged_levels[i]['data_offset'] = data_start + len(compacted_data)
        merged_levels[i]['data_length'] = len(blob)
        compacted_data += blob

    for i, lv in enumerate(sv_only):
        ae_count = len(ae_levels)
        blob = converted_blobs[i]
        merged_levels[ae_count + i]['data_offset'] = data_start + len(compacted_data)
        merged_levels[ae_count + i]['data_length'] = len(blob)
        compacted_data += blob

    # Append the SVAERA clone blob
    merged_levels[_clone_merged_idx]['data_offset'] = data_start + len(compacted_data)
    merged_levels[_clone_merged_idx]['data_length'] = len(_append_clone_blob)
    compacted_data += _append_clone_blob

    print(f'  DATA: {len(compacted_data)/(1024**2):.1f} MB ({len(ae_levels)} SVAERA + {len(sv_only)} SV-only + 1 clone)')

    # Rebuild levels index with corrected offsets
    new_levels_data = build_level_index(merged_levels)

    # Fix bitmap offsets (shift SVAERA bitmap offsets for new layout)
    ae_pre_data = ae_sec[SEC_DATA2]['header_offset']
    bmp_offset_shift = new_pre_data_size - ae_pre_data
    adjusted_bitmaps = [dict(b) for b in merged_bitmaps]
    for i in range(len(ae_bitmaps)):
        if i in _replace_bm_offsets:
            # Replaced level - use pre-computed offset from DATA2 append
            bm_entry = ae_bitmaps[i]
            abs_off = (new_pre_data_size + 8) + _replace_bm_offsets[i]
            adjusted_bitmaps[i]['offset'] = abs_off
            adjusted_bitmaps[i]['length'] = bm_entry['length']
            print(f'  Replaced bitmap at idx {i}: offset={abs_off}, length={bm_entry["length"]}')
        elif adjusted_bitmaps[i]['offset'] > 0:
            adjusted_bitmaps[i]['offset'] = ae_bitmaps[i]['offset'] + bmp_offset_shift

    # Set bitmap entries for SV-only levels (DATA2 pathfinding)
    new_data2_data_start = new_pre_data_size + 8  # after pre-data sections + DATA2 header
    for i, appended_info in sv_only_data2.items():
        merged_idx = len(ae_levels) + i
        if appended_info is not None:
            offset_in_data2, length = appended_info
            abs_offset = new_data2_data_start + offset_in_data2
            adjusted_bitmaps[merged_idx]['offset'] = abs_offset
            adjusted_bitmaps[merged_idx]['length'] = length

    new_bitmaps_data = build_bitmap_index(adjusted_bitmaps, ae_bmp_unknown)

    # Write map
    print('\nWriting map...')
    header2 = new_pre_data_size - 8
    out = bytearray()
    out += struct.pack('<II', MAP_MAGIC, header2)
    out += struct.pack('<II', SEC_QUESTS, len(new_quests_data)); out += new_quests_data
    out += struct.pack('<II', SEC_GROUPS, len(merged_groups)); out += merged_groups
    out += struct.pack('<II', SEC_SD, len(sv_sd)); out += sv_sd
    out += struct.pack('<II', SEC_LEVELS, len(new_levels_data)); out += new_levels_data
    out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data)); out += new_bitmaps_data
    for utype, udata in unk_sections:
        out += struct.pack('<II', utype, len(udata)); out += udata
    out += struct.pack('<II', SEC_DATA2, len(data2_raw)); out += data2_raw
    out += struct.pack('<II', SEC_DATA, len(compacted_data))
    out += compacted_data

    result = bytes(out)
    print(f'  Size: {len(result)/(1024**2):.1f} MB, under 2GB: {len(result) < 2147483647}')

    # Verify
    test_sections = parse_sections(result)
    test_sec = {s['type']: s for s in test_sections}
    test_levels = parse_level_index(result, test_sec[SEC_LEVELS])
    bad = sum(1 for lv in test_levels if lv['data_offset'] + lv['data_length'] > len(result))
    bad_magic = sum(1 for lv in test_levels if result[lv['data_offset']:lv['data_offset']+3] != b'LVL')
    zero_ints = sum(1 for lv in test_levels if lv['ints_raw'] == b'\x00' * 52)
    print(f'  Levels: {len(test_levels)}, bad offsets: {bad}, bad magic: {bad_magic}, zero ints: {zero_ints}')
    print(f'  drxmap refs: {result.count(b"drxmap")}')

    v11 = sum(1 for lv in test_levels if result[lv['data_offset']+3:lv['data_offset']+4] == b'\x11')
    v0e = sum(1 for lv in test_levels if result[lv['data_offset']+3:lv['data_offset']+4] == b'\x0e')
    print(f'  Format: v0x11={v11}, v0x0e={v0e}, other={len(test_levels)-v11-v0e}')

    # Package into ARC
    print('\nPackaging into ARC...')
    arc = ArcArchive.from_file(svaera_path)
    arc.set_file('world/world01.map', result)
    arc.write(out_arc_path)
    print(f'  Written: {out_arc_path.stat().st_size / (1024**2):.1f} MB')

    del ae_data, sv_data, result
    print('Done.')


if __name__ == "__main__":
    main()
