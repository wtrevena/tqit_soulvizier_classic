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
    INJECT_SPECS, MOVE_SPECS, ALL_CUSTOM_QUEST_NAMES, inject_into_0x05_v11,
    parse_blob_sections, rebuild_blob, convert_v0e_blob_to_v11,
    inject_into_sv_only_blob, inject_rec02_into_blob, move_0x05_instances,
    merge_hub_into_inject_specs, build_hub_inject_specs, patch_respawn_group_position,
    RESPAWNTEMPLEORIENT01_UNIQUEID,
    REWRITE_0X06_SPECS, rewrite_0x06_descriptors,
    APPEND_0X06_SPECS, append_0x06_descriptors,
    REMOVE_0X05_BY_0X14_UID_SPECS, remove_0x05_instances_by_0x14_uid,
    REMOVE_BY_DBR_SPECS, remove_0x05_instances_by_dbr,
    REMOVE_DANGLING_SHRINE_SPECS, REMOVE_STRAY_PROP_SPECS,
    FLAG_UID_SPECS, set_0x05_flags_uid, build_teleport_shrine_group_record)

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


def _groups_key_seq(recs):
    """(name, occurrence#) keyed sequence - duplicate group names exist in both maps
    (Egypt_Ambush_ThebesUG07, GoldenChest_Orient_BabylonUG01, X2_Kenchreai_*, New Group),
    so records must be matched by ordinal occurrence, never by bare name."""
    seen = {}
    out = []
    for r in recs:
        n = seen.get(r['name'], 0)
        seen[r['name']] = n + 1
        out.append(((r['name'], n), r))
    return out


# M13a must-bind list (docs/DEAD_CONTENT_AUDIT_2026-07-10.md Lane B): after the GROUPS
# restoration these device uids MUST be members of the right-category group, else the
# build fails loud. (uid hex, group category, why)
M13A_MUST_BIND = [
    ('32703cacc540dc22f9a1e1ac35a39cc1', 'RespawnShrine',
     'respawn_towerofjudgement01 @ judgment_towerug_floor04 (Lane B dead shrine, mandatory Hades path)'),
    ('3c007d48f94617f2b400a9847eb12731', 'TeleportShrine',
     'teleportshrineolympus01 @ olympusfinal02 (Lower Olympus rift stop, B-OLYMPUS-TELESHRINE-1)'),
    ('dbbd704cc445cf869b9a2c8261784ac3', 'TeleportShrine',
     'base Shrine_Teleport_Orient 12th member (Olympus-side; harmless-if-unplaced base parity)'),
    ('feeb4bc6ce4e08c0e279b3824244aeeb', 'RespawnShrine',
     'SV HV01 rebirth fountain (the build18 fix - MUST survive the restoration)'),
    ('ca07e97f18434def27a529a7ccbb5c8b', 'RespawnShrine',
     'SV-added Greece maze respawn (Greece_Maze_Respawn01 6th member)'),
]


def merge_groups_svaera_base(ae_g_recs, sv_g_recs, merged_level_guids):
    """M13a GROUPS RESTORATION (2026-07-10, from the dead-content audit + the M6/M12 RCAs).

    THE OLD MERGE ('SV records + SVAERA-only names') let SV 0.98i's TQIT-era version of
    every same-named group CLOBBER SVAERA/base's - byte-proven to kill the shrine-binding
    class: Shrine_Respawn_Hades 53->51 (the Tower-of-Judgement floor-4 respawn 32703cac...
    + the Lower-Olympus trophy 90de912a...), Shrine_Teleport_Hades 5->4 (the Olympus rift
    shrine 3c007d48...), Shrine_Teleport_Orient 12->11, plus stale TQIT member positions/
    GUIDs in 42 more same-named records (golden chests, unified proxies, the Q15/xQ00
    portal-pairing [Any Entity] records). Lane B of docs/DEAD_CONTENT_AUDIT_2026-07-10.md:
    372/375 placed devices bound; the ONLY dead ones = these merge casualties.

    NEW MERGE (this function):
      base   = SVAERA's records, verbatim, in SVAERA order (byte-parity with the base-game
               GROUPS up to SVAERA's own upstream edits);
      + for each same-named record where SV differs: append SV's EXTRA members (uids absent
        from SVAERA's member set) - these are SV's legitimate additions (the HV01 fountain,
        the SV maze respawn, ...). A member payload = uid(16)+levelGUID(16)+pos(12) = 44 B;
        the record tail (20/36/68 B, byte-identical SV vs SVAERA for every differing record,
        verified) is preserved. An SV-extra whose levelGUID does not resolve in the merged
        LEVELS index is SKIPPED loudly (a stale TQIT-era reference, not content).
      + SV-only group NAMES appended verbatim (exactly 4: 'New Group' x2 [the SV respawn
        networks], 'DRXShrineTeleport_Duister' [the GoM rift shrine], 'zRespawnSanctuary').
    Member-set analysis: scratchpad m13_member_diff.py (2026-07-10): 46 differing same-name
    records, 0 layout violations, 4 records carry SV-extra members.

    Returns the merged record list (caller rebuilds bytes + runs C1/C2c on top).
    """
    ae_seq = _groups_key_seq(ae_g_recs)
    sv_seq = _groups_key_seq(sv_g_recs)
    svd = dict(sv_seq)
    ae_keys = {k for k, _ in ae_seq}

    out = []
    n_identical = n_sv_extra_recs = n_members_added = n_skipped = 0
    for key, ae_rec in ae_seq:
        sv_rec = svd.get(key)
        if (sv_rec is None
                or (sv_rec['raw_data'] == ae_rec['raw_data']
                    and sv_rec['member_count'] == ae_rec['member_count']
                    and sv_rec['category'] == ae_rec['category']
                    and sv_rec['sub_count'] == ae_rec['sub_count'])):
            out.append(ae_rec)
            n_identical += 1
            continue
        # differing same-name record: SVAERA base + SV-extra members
        m_ae, m_sv = ae_rec['member_count'], sv_rec['member_count']
        raw_ae, raw_sv = ae_rec['raw_data'], sv_rec['raw_data']
        if 44 * m_ae > len(raw_ae) or 44 * m_sv > len(raw_sv):
            raise ValueError(f'GROUPS {key!r}: member layout != 44*m + tail '
                             f'(ae {m_ae}/{len(raw_ae)}, sv {m_sv}/{len(raw_sv)}) - '
                             f'manual handling required')
        ae_uids = {raw_ae[i * 44:i * 44 + 16] for i in range(m_ae)}
        extras = []
        for i in range(m_sv):
            pay = raw_sv[i * 44:(i + 1) * 44]
            if pay[:16] in ae_uids:
                continue
            if pay[16:32].hex() not in merged_level_guids:
                print(f'    GROUPS {key[0]!r}: SKIP SV-extra member uid={pay[:16].hex()[:12]}.. '
                      f'(levelGUID {pay[16:32].hex()[:12]}.. not in the merged LEVELS index)')
                n_skipped += 1
                continue
            extras.append(pay)
        if extras:
            tail = raw_ae[44 * m_ae:]
            rec = dict(ae_rec)
            rec['raw_data'] = raw_ae[:44 * m_ae] + b''.join(extras) + tail
            rec['member_count'] = m_ae + len(extras)
            out.append(rec)
            n_sv_extra_recs += 1
            n_members_added += len(extras)
            print(f'    GROUPS {key[0]!r}: SVAERA base ({m_ae}) + {len(extras)} SV-extra '
                  f'member(s) -> {rec["member_count"]}')
        else:
            out.append(ae_rec)  # pos/guid drift only -> base truth wins
    sv_only_recs = [(k, r) for k, r in sv_seq if k not in ae_keys]
    for key, sv_rec in sv_only_recs:
        out.append(sv_rec)
    print(f'  GROUPS M13a: {len(ae_seq)} SVAERA-base records ({n_identical} byte-identical, '
          f'{n_sv_extra_recs} with SV-extra members [{n_members_added} added, {n_skipped} '
          f'skipped-stale]) + {len(sv_only_recs)} SV-only groups = {len(out)}')
    assert len(out) == len(ae_g_recs) + len(sv_only_recs), 'M13a record-count mismatch'
    assert len(sv_only_recs) == 4, \
        (f'M13a expected exactly 4 SV-only groups (New Group x2, DRXShrineTeleport_Duister, '
         f'zRespawnSanctuary), got {[k for k, _ in sv_only_recs]}')
    # fail-loud must-bind verification (Lane B's exact dead-device uids + the SV keepers)
    for uid_hex, cat, why in M13A_MUST_BIND:
        uid = bytes.fromhex(uid_hex)
        holders = [r['name'] for r in out if uid in r['raw_data'] and r['category'] == cat]
        assert holders, f'M13a MUST-BIND FAILED: {uid_hex[:12]}.. [{cat}] not bound - {why}'
    return out

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
            # SEAM FIX (2026-07-05, docs/NAVMESH_COVERAGE_FIX.md sec 4): the
            # engine's cross-region walk-link builder keys on INDEX-footprint
            # adjacency (corner + content_tiles*2); a 2u gap blocks the link
            # even when navmesh cells overlap. SV authored a few cluster levels
            # with content dims < box dims (harmless under SV's single
            # continuous 0x0a mesh, fatal for per-level 0x0b stitching):
            # BC_initialpathway content x=39 vs box x=40 left a 2u gap at the
            # xPTS seam = the in-game wall. Normalize content dims to box dims
            # (the base-game content==box invariant) for cluster levels; the
            # measured result is all 39 connecting cluster seams flush, no new
            # overlap (the other slack levels' widened edges face no
            # connecting neighbor).
            cx_t, cy_t, cz_t, bx_t, by_t, bz_t = struct.unpack_from('<6i', raw, 0)
            if (cx_t, cz_t) != (bx_t, bz_t):
                struct.pack_into('<2i', raw, 0, bx_t, cy_t)  # content x <- box x
                struct.pack_into('<i', raw, 8, bz_t)         # content z <- box z
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


def assert_donor_fresh(donor, target_ints, name):
    """Fail loud if a pre-positioned donor was generated at a different GRID_SHIFT.

    A pre-positioned 0x0b is injected VERBATIM, so a donor regenerated at some
    other (e.g. abandoned/experimental) shift silently places the navmesh
    kilometres from its level (2026-07-05 corruption class: a size-only check
    passes because only the 12-byte center differs). Layout invariant on healthy
    donors (global-lattice pipeline, 2026-07-05): the mesh corner (center - dims)
    is the level's padded corner snapped DOWN to the 64u tile lattice of the SV
    generation frame, so on x and z it must (a) lie within [corner-16-63,
    corner-16] (snap distance < 64) and (b) the mesh far edge must cover the
    level box + 16u pad. (No absolute mod-64 check here: GRID_SHIFT moves the
    lattice phase in the merged frame; cross-donor phase CONSISTENCY - the
    walkability requirement - is gated by the seam alignment check on the merged
    map.) A wrong-GRID_SHIFT donor is off by hundreds of units and fails (a).
    """
    gc = struct.unpack_from('<I', donor, 12)[0]
    pos = 16 + gc * 16
    cx, _cy, cz = struct.unpack_from('<3i', donor, pos)
    dx, _dy, dz = struct.unpack_from('<3I', donor, pos + 12)
    ints = struct.unpack_from('<13i', target_ints, 0)
    mesh_x0, mesh_z0 = cx - dx, cz - dz
    mesh_x1, mesh_z1 = cx + dx, cz + dz
    lo_x, lo_z = ints[6] - 16, ints[8] - 16
    hi_x, hi_z = ints[6] + 2 * ints[3] + 16, ints[8] + 2 * ints[5] + 16
    bad = []
    if not (lo_x - 63 <= mesh_x0 <= lo_x and lo_z - 63 <= mesh_z0 <= lo_z):
        bad.append(f'corner ({mesh_x0},{mesh_z0}) outside snap window of padded corner ({lo_x},{lo_z})')
    if mesh_x1 < hi_x or mesh_z1 < hi_z:
        bad.append(f'far edge ({mesh_x1},{mesh_z1}) does not cover padded box ({hi_x},{hi_z})')
    if bad:
        raise SystemExit(
            f'STALE DONOR {name}: ' + '; '.join(bad) +
            f' [center=({cx},{cz}) dims=({dx},{dz}) grid corner=({ints[6]},{ints[8]})]. '
            f'Donors were generated at a different GRID_SHIFT or by the pre-lattice '
            f'pipeline - rerun: py tools/gen_bc_navmeshes.py')


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


# --- QUESTS(0x1b) registration list (single source of truth) ----------------
# The world-file's QUESTS section is the ONLY quest registry the engine reads at
# world-load (byte-verified 2026-07-06: NO parallel registry exists - no .wrl, no
# second count field in SD/GROUPS/BITMAPS/DATA2; each entry = u32 len + path bytes,
# no null terminator). Quest IDENTITY is 100% path-based: the engine strips each
# registry path to its BASENAME and instantiates md5(`quests\<basename>.qst`)
# (proven in docs/QUEST_STATE_INJECT.md sec 1.1 + confirmed here: identity(
# `XPack/Quests/bossarena.qst`) == identity(`Quests/bossarena.qst`)). Level-entity
# bindings use DBR path strings, NOT registry paths. So the section's ORDER is
# engine-internal and REORDERING/INSERTING/DROPPING-a-duplicate is provably safe for
# existing saves and every level's entity bindings, PROVIDED every distinct identity
# that must load is still present at least once, at an index the engine loads.
#
# THE LOAD-WINDOW DEFECT (this is the fix for the "widow letter STILL missing" repeat
# report). Empirically proven across 5 custom-quest chars + vanilla saves
# (docs/QUEST_STATE_INJECT.md sec 2, docs/LETTER_SPAWN_DIAGNOSIS.md 2026-07-06
# correction): the engine NEVER loads a QUESTS entry appended past the original
# SVAERA count. The prior build APPENDED the 4 SV quests right after the 254 natives
# -> widowletter landed at index 256 -> it never loaded for ANY character (fresh OR
# existing), so the letter never spawned and the questline never tracked. Reference
# counts: vanilla TQAE world01.map registers EXACTLY 256 quests and all 256 load;
# SVAERA registers 254. So the safe, proven-loading window is the first <=256 entries.
#
# THE FIX: put the 4 SV quests at LOW indices INSIDE the native block and keep the
# whole list <= 256 (vanilla's proven-loading length), so NOTHING a player needs ever
# shifts past the window:
#   1. Take the SVAERA natives in their exact original order, but DROP the 2 redundant
#      `x2quest_controlsdoors.qst` re-registrations (SVAERA lists it 3x at idx
#      159/196/199, all the SAME identity `quests\x2quest_controlsdoors.qst`; one copy
#      is enough - dropping 2 loses ZERO identity). 254 -> 252 natives.
#   2. INSERT the 4 primary `Quests/<name>.qst` forms immediately AFTER
#      `Quests/sv_commonmechanics.qst` (native idx 96) -> they sit at idx ~97..100,
#      deep inside the load window. `Quests/bossarena.qst` is SYNTHESIZED (SV ships
#      only `XPack/Quests/bossarena.qst`; same identity but we emit the `Quests/` form
#      to mirror how the mod Quests.arc + the other 3 are stored). 252 -> 256 entries.
#   3. DROP the entire ~46-entry appended `XPack/Quests/*` tail: every one is either a
#      dup-of-native (same identity as a native `Quests/` twin), a dup-of-primary
#      (`XPack/Quests/{widowletter,urder,bossarena,open_bloodcave_portal}.qst`), or a
#      dead file (`imhotepfix`, `typhonportal` - exist nowhere). Dropping the tail
#      loses ZERO distinct identity: each identity is preserved by a native twin (1)
#      or by the relocated primary form (2).
# Net: exactly 256 entries, indices 0..255, the 4 SV quests at ~97..100 inside the
# proven window; every SVAERA native identity preserved; no player-facing quest can
# regress. Will's EXISTING _Toxeus now auto-adopts widowletter on next load (the
# engine auto-adopts newly-loadable quests for existing chars, proven in
# QUEST_STATE_INJECT.md sec 2) and step 0 fires -> the static letter is already there,
# pickup grants SQWL_PickedUpLetter, and the chain can complete. No save surgery.
FOUR_PRIMARY_QUEST_FORMS = [
    b'Quests/open_bloodcave_portal.qst',
    b'Quests/urder.qst',
    b'Quests/widowletter.qst',
    b'Quests/bossarena.qst',
]
# The redundant native re-registrations to drop (identity-duplicates within the 254
# SVAERA natives). Keyed by BASENAME; we keep the FIRST occurrence, drop later ones.
# `x2quest_controlsdoors.qst` is registered 3x (idx 159/196/199) differing only in
# case/folder - all hash to `quests\x2quest_controlsdoors.qst`. Dropping the 2 extra
# copies frees 2 slots to keep the list at 256 after inserting the 4 SV quests, with
# ZERO identity lost. Verified 2026-07-07: this is the ONLY basename-duplicate group in
# the 254 SVAERA natives (all other basenames are unique). The build fails loud (invariant
# (v) below) if any duplicate identity survives, so a future SVAERA change that adds a new
# duplicate group cannot silently ship a bad registry.
NATIVE_REDUNDANT_BASENAMES = {'x2quest_controlsdoors.qst'}  # str, matches _quest_basename()
# M14 (docs/DEAD_CONTENT_AUDIT_2026-07-10.md Lane D): natives deliberately DE-REGISTERED
# from the QUESTS load window. testquesttoopendoors.qst is a leftover DEVELOPER TEST quest
# (its literal name) shipped registered at idx 101: it duplicates door unlocks the real
# controller ('quest that controls bosses and their doors.qst') already owns, references
# Ragnarok-DLC Surtr monsters unreachable in the IT-bounded campaign, could open the
# Gorgon/Changan doors on unintended conditions, and burns one of the EXACTLY-256 slots
# whose overflow was the widow-letter root cause. De-registering frees the slot; the .qst
# stays in the arcs harmlessly (an unregistered quest never loads). Quest identity is by
# NAME, not index, so natives after idx 101 shifting down by one is functionally neutral.
DEREGISTERED_NATIVE_BASENAMES = {'testquesttoopendoors.qst'}
# Insert the 4 SV quests immediately after this native (a stable, low anchor well
# inside the load window). sv_commonmechanics is SV-added, present since char creation.
QUEST_INSERT_ANCHOR = b'Quests/sv_commonmechanics.qst'


def _quest_basename(entry):
    """The identity basename of a QUESTS entry (folder stripped, lowercased)."""
    return entry.decode('ascii', 'replace').replace('/', '\\').lower().split('\\')[-1]


def build_ordered_quest_list(ae_quests, sv_quests):
    """Return the merged QUESTS entry list (list[bytes]) with the 4 SV questlines
    placed INSIDE the engine's proven load window (first <=256 entries), not appended
    past it. See the module comment above for the full rationale + proof.

    ae_quests / sv_quests are the parsed native-byte name lists (no length prefix).
    Guarantees, all re-asserted by the caller's Z1 gate:
      - every DISTINCT native identity (by basename) is still present, in the natives'
        original relative order, minus only redundant re-registrations of an identity
        that still appears earlier (NATIVE_REDUNDANT_BASENAMES);
      - the 4 FOUR_PRIMARY_QUEST_FORMS are inserted right after QUEST_INSERT_ANCHOR, so
        they load; a synthesized `Quests/bossarena.qst` is used since SV lacks it;
      - the whole list is <= 256 entries (vanilla's proven-loading length), so no
        surviving native shifts past the window;
      - NO appended `XPack/Quests/*` dup tail and NO dead ALL_CUSTOM_QUEST_NAMES stub.
    """
    # (1) Natives in original order, dropping redundant re-registrations of an
    # identity that already appeared (keep the first occurrence of each basename in
    # NATIVE_REDUNDANT_BASENAMES; every other basename is kept as-is).
    natives_deduped = []
    seen_redundant = set()
    for q in ae_quests:
        b = _quest_basename(q)
        if b in DEREGISTERED_NATIVE_BASENAMES:
            continue  # M14: deliberately de-registered (see the constant's rationale)
        if b in NATIVE_REDUNDANT_BASENAMES:
            if b in seen_redundant:
                continue  # drop this extra re-registration (identity kept via the first)
            seen_redundant.add(b)
        natives_deduped.append(q)

    # (2) The 4 primary forms, in intent order (unique among themselves).
    primary = []
    primary_lower = set()
    for form in FOUR_PRIMARY_QUEST_FORMS:
        if form.lower() not in primary_lower:
            primary.append(form)
            primary_lower.add(form.lower())

    # Splice the 4 primary forms immediately AFTER the insert anchor within the
    # deduped natives, so they sit at a low, in-window index.
    anchor_idx = next((i for i, q in enumerate(natives_deduped)
                       if q == QUEST_INSERT_ANCHOR), None)
    assert anchor_idx is not None, \
        f'insert anchor {QUEST_INSERT_ANCHOR!r} not found among SVAERA natives'
    ordered = (natives_deduped[:anchor_idx + 1] + primary
               + natives_deduped[anchor_idx + 1:])

    # (3) The appended SV-only `XPack/Quests/*` tail + dead stubs are intentionally
    # NOT carried over: every distinct identity there is already present (a native
    # `Quests/` twin, or a relocated primary form). We assert that below.

    # --- Hard invariants (fail loud rather than ship a bad registry) -------------
    # (i) size stays within the proven-loading window.
    assert len(ordered) <= 256, \
        f'QUESTS list {len(ordered)} > 256 exceeds the proven vanilla load window'

    # (ii) the 4 primary forms are inside the window and contiguous after the anchor.
    for k, form in enumerate(primary):
        assert ordered[anchor_idx + 1 + k] == form, \
            f'primary form {form!r} not spliced at expected position'
        assert anchor_idx + 1 + k < 256, \
            f'primary form {form!r} at index {anchor_idx + 1 + k} outside load window'

    # (iii) EVERY distinct native identity (basename) still appears at least once, at
    # an index < 256. This is the anti-regression guarantee: dropping the redundant
    # copies + the appended tail must not lose any quest a character could load.
    ordered_basenames_in_window = {_quest_basename(q) for q in ordered[:256]}
    for q in ae_quests:
        b = _quest_basename(q)
        if b in DEREGISTERED_NATIVE_BASENAMES:
            continue  # M14: intentionally absent
        assert b in ordered_basenames_in_window, \
            f'native identity {b!r} lost from the load window - regression!'
    # M14: the de-registration actually happened (fail loud if the dev quest sneaks back).
    for b in DEREGISTERED_NATIVE_BASENAMES:
        assert b not in ordered_basenames_in_window, \
            f'M14: {b!r} must be DE-REGISTERED from the QUESTS window but is present'
    # every distinct SV-only identity we intend to ship (the 4) is present too.
    for form in primary:
        assert _quest_basename(form) in ordered_basenames_in_window, \
            f'SV quest identity {_quest_basename(form)!r} missing from the load window'

    # (iv) no dead stub survived (uberdungeon/bloodcave _entrance/_return).
    dead_lower = {q.lower() for q in ALL_CUSTOM_QUEST_NAMES}
    for q in ordered:
        assert q.decode('ascii', 'replace').lower() not in dead_lower, \
            f'dead stub {q!r} must not be registered'

    # (v) the only basename that may appear more than once is a benign leftover we
    # explicitly allow NONE of - after dedup every basename in the window is unique.
    from collections import Counter
    bn_counts = Counter(_quest_basename(q) for q in ordered)
    dups = {b: c for b, c in bn_counts.items() if c > 1}
    assert not dups, f'duplicate identities remain after dedup: {dups}'

    return ordered


def main():
    """Build the merged Levels.arc (heavy: multi-GB). Not run on import."""
    # --- Paths ---
    svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
    sv_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')

    # --- TEST HUB flag (SVC_TEST_HUB=1) ---
    # OFF (default): canonical build -> local/Levels_merged.arc (A1/A2 doors + C1-C4 fixes, hub-free).
    # ON: build the SEPARATE hub artifact -> local/Levels_merged_TESTHUB.arc (canonical + the 20
    # blood-cave hub portals). The flag-OFF build MUST be byte-identical to flag-ON minus the hub
    # entities (proven by gate_hub_identity.py); the hub specs are APPENDED after base specs so base
    # instance indices never shift. Everything ELSE (A1/A2/C1-C4) is in BOTH builds.
    USE_HUB = os.environ.get('SVC_TEST_HUB') == '1'
    inject_specs = merge_hub_into_inject_specs(INJECT_SPECS) if USE_HUB else INJECT_SPECS
    out_name = 'Levels_merged_TESTHUB.arc' if USE_HUB else 'Levels_merged.arc'
    out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local') / out_name
    print(f'BUILD MODE: {"TEST HUB (SVC_TEST_HUB=1)" if USE_HUB else "canonical"} -> {out_name}')

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

    # --- 2. GROUPS: M13a RESTORATION - SVAERA/base as the BASE + SV's additions on top ---
    # (was: 'SV records + SVAERA-only names', which let SV's TQIT-era sections clobber the
    # base shrine bindings - the proven-dead-device class. See merge_groups_svaera_base.)
    print('\n=== Merging GROUPS (M13a: SVAERA base + SV additions) ===')
    sv_groups_raw = sv_data[sv_sec[SEC_GROUPS]['data_offset']:
                            sv_sec[SEC_GROUPS]['data_offset'] + sv_sec[SEC_GROUPS]['size']]
    ae_groups_raw = ae_data[ae_sec[SEC_GROUPS]['data_offset']:
                            ae_sec[SEC_GROUPS]['data_offset'] + ae_sec[SEC_GROUPS]['size']]
    sv_g_val0, sv_g_recs = _parse_groups(sv_groups_raw)
    ae_g_val0, ae_g_recs = _parse_groups(ae_groups_raw)
    # merged-world level-GUID set (AE levels keep their GUIDs incl. the R09 swap; SV-only
    # levels keep SV GUIDs) - validates SV-extra member payloads before they are appended.
    _merged_guids = set()
    for _lv in ae_levels:
        _ints = struct.unpack_from('<13I', _lv['ints_raw'], 0)
        _merged_guids.add(struct.pack('<4I', *_ints[9:13]).hex())
    for _lv in sv_only:
        _ints = struct.unpack_from('<13I', _lv['ints_raw'], 0)
        _merged_guids.add(struct.pack('<4I', *_ints[9:13]).hex())
    _m13a_recs = merge_groups_svaera_base(ae_g_recs, sv_g_recs, _merged_guids)
    merged_groups = _rebuild_groups(ae_g_val0, _m13a_recs)

    # --- 2b. C1 FIX (respawn position): the HV01 fountain's GROUPS respawnorient member still
    # carries the OLD (49.263,15.634,14.950) position; the engine respawns THERE, not at the moved
    # 0x05 instance. Rewrite the GROUPS member position to the fountain's NEW 0x05 position so GROUPS
    # == 0x05 (native-shrine parity). Byte-scan-proven root cause (docs/DOORS_HUB_LOG.md C1). This is
    # the ONLY stale copy (SD is byte-identical + carries no fountain coord; 0x05 is already correct).
    print('=== C1: respawn-position GROUPS fix ===')
    merged_groups = patch_respawn_group_position(
        merged_groups, RESPAWNTEMPLEORIENT01_UNIQUEID, (35.70, 17.60, 143.10),
        level_name='HiddenValley01 fountain')

    # --- 2c. DUISTER RETURN (2026-07-08): wire the RogueEncampment rift shrine into the
    # TeleportShrine portal network - the GROUPS half. Mirrors the Garden shrine's record
    # byte-shape exactly (1 member = uid+levelGUID+pos + 20B tail; sub_count=2 like every
    # native TeleportShrine record). The 0x05 half (flags=1 + UniqueId on the existing
    # inert instance) is applied in step 6c via FLAG_UID_SPECS. See the DUISTER block in
    # build_section_surgery.py for the full mechanism + byte evidence.
    print('=== C2c: Duister shrine GROUPS record (TeleportShrine network) ===')
    # Direct byte-append (val0 + count header, records back-to-back): safer than
    # re-parsing the rebuilt section through the heuristic boundary scanner. The new
    # record's serialized form matches _rebuild_groups' per-record layout exactly.
    _duister_rec = build_teleport_shrine_group_record()
    _name_b = _duister_rec['name'].encode('ascii')
    _cat_b = _duister_rec['category'].encode('ascii')
    assert _name_b not in merged_groups, f'GROUPS already contains {_duister_rec["name"]!r}'
    _rec_bytes = (struct.pack('<I', _duister_rec['sub_count'])
                  + struct.pack('<I', len(_name_b)) + _name_b
                  + struct.pack('<I', len(_cat_b)) + _cat_b
                  + struct.pack('<I', _duister_rec['member_count'])
                  + _duister_rec['raw_data'])
    _g_count = struct.unpack_from('<I', merged_groups, 4)[0]
    _mg = bytearray(merged_groups + _rec_bytes)
    struct.pack_into('<I', _mg, 4, _g_count + 1)
    merged_groups = bytes(_mg)
    print(f'  appended GROUPS record {_duister_rec["name"]!r} cat={_duister_rec["category"]!r} '
          f'(count {_g_count} -> {_g_count + 1}, +{len(_rec_bytes)} B)')

    # --- 3. SD: SV's (blood cave zone definitions) ---
    sv_sd = sv_data[sv_sec[SEC_SD]['data_offset']:
                    sv_sec[SEC_SD]['data_offset'] + sv_sec[SEC_SD]['size']]
    print(f'  Using SV SD: {len(sv_sd)} bytes')

    # --- 4. QUESTS: 4 SV questlines spliced INSIDE the load window ---
    # See build_ordered_quest_list: the 4 primary `Quests/<name>.qst` forms are
    # inserted right after Quests/sv_commonmechanics.qst (native idx 96 -> they land
    # at ~97..100, inside the proven <=256 load window), 2 redundant native
    # re-registrations of x2quest_controlsdoors.qst are dropped to keep the list at
    # 256, and the whole ~46-entry appended XPack/Quests/* dup+dead tail is dropped
    # (every identity preserved by a native twin or the relocated primary form). This
    # FIXES the "widow letter STILL missing" repeat report: widowletter was at index
    # 256 (past the window, never loaded for ANY char); it now loads.
    merged_quests = build_ordered_quest_list(ae_quests, sv_quests)
    new_quests_data = build_quests(merged_quests)
    _wl_idx = next((i for i, q in enumerate(merged_quests)
                    if b'widowletter' in q.lower()), None)
    print(f'  Quests: {len(ae_quests)} SVAERA natives -> {len(merged_quests)} entries '
          f'(4 SV quests spliced in-window; widowletter now at idx {_wl_idx}; '
          f'2 redundant natives + ~46 appended dup/dead entries dropped)')

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
    for lv_key, specs in inject_specs.items():
        if lv_key in ae_by_name:
            ae_inject_keys[lv_key] = specs

    sv_inject_keys = {}
    for lv_key, specs in inject_specs.items():
        for i, lv in enumerate(sv_only):
            if lv['fname'].replace('\\', '/').lower() == lv_key:
                sv_inject_keys[i] = specs

    # Inject into SVAERA levels (these will be patched blobs)
    ae_patched_blobs = {}  # ae_level_index -> patched blob
    ae_injected_count = {}  # ae_level_index -> number of instances injected
    ae_injected_specs = {}  # ae_level_index -> the injected spec list (for 0x14 decisions)
    for lv_key, specs in ae_inject_keys.items():
        ae_idx = ae_by_name[lv_key]
        lv = ae_levels[ae_idx]
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        blob_ver = blob[3] if blob[:3] == b'LVL' else None

        # v0x11 AND v0x0f use the SAME base-72 0x05 instance record (+16 if flags@+52 != 0).
        # Byte-verified on AE Maze03 (v0x0f, 447 instances): walking base=72 lands EXACTLY at
        # the 0x05 data end (base=56 desyncs at instance 5). So inject_into_0x05_v11 (which
        # walks base V11_RECORD_SIZE=72 and preserves flagged UniqueId tails) is correct for
        # both. This unblocks the maze03 (v0x0f) portal restore. The section rebuild preserves
        # the original blob magic (v0x0f stays v0x0f).
        if blob_ver in (0x11, 0x0f):
            secs, magic = parse_blob_sections(blob)
            move_specs = MOVE_SPECS.get(lv_key, [])
            base_size = 72 if blob_ver in (0x11, 0x0f) else 56
            for j, s in enumerate(secs):
                if s['type'] == 0x05:
                    data = s['data']
                    # Workstream B: MOVE native instances in place FIRST (rewrites only their
                    # position bytes), THEN append the injected records. Moves target existing
                    # instances by dbr+from_xyz; injection appends new ones to the tail - the
                    # two do not interact (moves never change instance count or ordering).
                    if move_specs:
                        data = move_0x05_instances(data, move_specs, base_size, lv_key)
                    secs[j] = {'type': 0x05, 'data': inject_into_0x05_v11(data, specs)}
            ae_patched_blobs[ae_idx] = rebuild_blob(magic, secs)
            ae_injected_count[ae_idx] = len(specs)
            ae_injected_specs[ae_idx] = specs
            print(f'  Injected {len(specs)} NPC(s) into SVAERA {lv_key} (v0x{blob_ver:02x})'
                  + (f' + moved {len(move_specs)} native instance(s)' if move_specs else ''))
        elif blob_ver == 0x0e:
            # build31h (M9 prerequisite - the Vashkarr FotA-cave class): native v0x0e
            # SVAERA-side hosts. Same LVL v0e blob structure as SV-only v0e levels, so
            # route through the PROVEN SV-only v0e injector (inject_into_0x05 base-56;
            # per-spec x14_payload/0x14 appends handled INSIDE inject_into_sv_only_blob).
            # Deliberately NOT registered in ae_injected_specs/ae_injected_count: step 7's
            # v11 0x14-append pass must not double-append (it no-ops on this blob since
            # n_injected=0 and specs=[]). Previously this case WARN-skipped, silently
            # dropping any spec targeting a base-game v0e host. MOVE_SPECS on a v0e host
            # stays unsupported - fail loud rather than silently skip.
            if MOVE_SPECS.get(lv_key):
                raise ValueError(f'{lv_key}: MOVE_SPECS on a v0x0e SVAERA host is not '
                                 f'supported (only the v11/v0f move path exists)')
            ae_patched_blobs[ae_idx] = inject_into_sv_only_blob(blob, specs, lv_key)
            print(f'  Injected {len(specs)} NPC(s) into SVAERA {lv_key} (v0x0e branch)')
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

    # --- 6c. SV-only structural patches (2026-07-08 wave) ---------------------------
    # (a) FLAG_UID_SPECS: set flags=1 + UniqueId on an EXISTING 0x05 instance (the
    #     inert RogueEncampment rift shrine; pairs the step-2c GROUPS record).
    # (b) REWRITE_0X06_SPECS: repurpose SpartaCryptLevel2's dangling 0x06 portal
    #     descriptor into the native return door to the catacube (in-place 60-byte
    #     rewrite; count unchanged). See build_section_surgery.py for both mechanisms.
    # (c) APPEND_0X06_SPECS + REMOVE_0X05_BY_0X14_UID_SPECS: the Uber Dungeon native
    #     return door (M1) - APPEND a reciprocal 0x06 descriptor to crypt_floor1 (count
    #     2->3) mirroring maze03's host mouth, and REMOVE crypt's GridExitOneWay landing
    #     portal_olympianarena2 (0x05 inst + its 48B 0x14) so it does not duplicate the
    #     descriptor's portal id. maze03 (base, host) is UNCHANGED. Both run AFTER step-6
    #     injection so instance-index accounting (portal_uberdungeon_return at the tail) is
    #     already settled.
    print('\n=== SV-only structural patches (flags/uid + 0x06 rewrites/appends + removals) ===')
    for i, lv in enumerate(sv_only):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in FLAG_UID_SPECS:
            blob = converted_blobs[i]
            blob_ver = blob[3] if blob[:3] == b'LVL' else None
            assert blob_ver == 0x0e, f'{lv_key}: FLAG_UID_SPECS expects v0x0e, got v0x{blob_ver:02x}'
            secs, magic = parse_blob_sections(blob)
            new_secs = []
            for s in secs:
                if s['type'] == 0x05:
                    d = s['data']
                    for spec in FLAG_UID_SPECS[lv_key]:
                        d = set_0x05_flags_uid(d, spec['dbr'], spec['from_xyz'],
                                               spec['uid'], 56, lv_key)
                    new_secs.append({'type': 0x05, 'data': d})
                else:
                    new_secs.append(s)
            converted_blobs[i] = rebuild_blob(magic, new_secs)
        if lv_key in REWRITE_0X06_SPECS:
            converted_blobs[i] = rewrite_0x06_descriptors(
                converted_blobs[i], REWRITE_0X06_SPECS[lv_key], lv_key)
        if lv_key in APPEND_0X06_SPECS:
            converted_blobs[i] = append_0x06_descriptors(
                converted_blobs[i], APPEND_0X06_SPECS[lv_key], lv_key)
        if lv_key in REMOVE_0X05_BY_0X14_UID_SPECS:
            converted_blobs[i] = remove_0x05_instances_by_0x14_uid(
                converted_blobs[i], REMOVE_0X05_BY_0X14_UID_SPECS[lv_key], lv_key)

    # --- 7. Append 0x14 entries ONLY for injected instances that need one (SV-faithful) ---
    # A 0x14 entry is per-instance engine BINDING metadata (e.g. a cave-mouth GridEntrance
    # GUID binding). It is keyed by INSTANCE INDEX (the `idx` field) and the section is
    # SPARSE: shared AE levels have FEWER 0x14 entries than 0x05 instances (e.g. HV01
    # 205 inst / 190 entries, RoadToTown03A 288/276, HVBorder04 37/36 - many flags=0
    # entities carry NO 0x14). So NOT every injected instance should get a 0x14 entry.
    #
    # SV-FAITHFUL RULE (measured against SV 0.98i, gate F1): append a default 0x14 entry
    # ONLY for injected specs that explicitly set opts['wants_0x14']=True. None of the
    # currently-restored entities do: SV's respawn shrine, merchant wagon, and the 3
    # widow entities ALL have NO 0x14 entry in SV, so appending one is non-faithful (and
    # for the shrine it was part of the build18 defect). The append index for a wanting
    # instance is its INSTANCE index (tail range [orig_instance_count, new_count)); using
    # the 0x14 ENTRY count instead would collide with existing sparse indices (the latent
    # bug fixed in build18). A hard collision assert still guards against mis-accounting.
    from build_section_surgery import (count_0x05_instances, DEFAULT_0x14_PAYLOAD,
                                        _normalize_spec)
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
        n_injected = ae_injected_count.get(ae_idx, 0)
        orig_instance_count = new_count - n_injected
        # Injected instances occupy the tail [orig_instance_count, new_count) in spec order.
        # Decide per spec whether it wants a 0x14 entry.
        specs = ae_injected_specs.get(ae_idx, [])
        want_idx = []  # list of (instance_index, payload_bytes)
        for j, spec in enumerate(specs):
            _, _, _, _, _flags, _uid, wants_0x14, _rot, x14pl = _normalize_spec(spec)
            if wants_0x14:
                want_idx.append((orig_instance_count + j,
                                 x14pl if x14pl is not None else DEFAULT_0x14_PAYLOAD))
        new_secs = []
        for s in secs:
            if s['type'] == 0x14:
                # Preserve the original (possibly sparse) 0x14 verbatim.
                orig_data = bytearray(s['data'])
                # Collect existing indices so we can assert no collision with the appended ones.
                existing_idx = set()
                pos = 0
                orig_entries = 0
                while pos + 8 <= len(orig_data):
                    idx = struct.unpack_from('<I', orig_data, pos)[0]
                    psize = struct.unpack_from('<I', orig_data, pos + 4)[0]
                    existing_idx.add(idx)
                    pos += 8 + psize
                    orig_entries += 1
                # Append an entry ONLY for injected instances that requested one, using
                # each spec's own payload (custom x14_payload, else the 20-byte default).
                added = 0
                for idx, payload in want_idx:
                    if idx in existing_idx:
                        raise ValueError(
                            f'0x14 append collision: instance index {idx} already has a '
                            f'0x14 entry (orig_instance_count={orig_instance_count}, '
                            f'new_count={new_count}, n_injected={n_injected}). The 0x05 '
                            f'injection accounting is wrong; refusing to corrupt the blob.')
                    orig_data += struct.pack('<II', idx, len(payload))
                    orig_data += payload
                    added += 1
                new_secs.append({'type': 0x14, 'data': bytes(orig_data)})
                print(f'  0x14: kept {orig_entries} original entries + added {added} new '
                      f'({"instance idx " + str([i for i, _ in want_idx]) if want_idx else "none - SV-faithful"})')
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

    # TEST HUB: inject the 10 blood-cave hub portals into Random09A's 0x05 (+ their 48-byte 0x14
    # bindings). Random09A is v0x0e and handled by the special swap path (NOT the normal INJECT_SPECS
    # loop), so the hub R09 specs must be applied to swapped_blob here. Only when SVC_TEST_HUB=1; the
    # canonical build leaves swapped_blob untouched (byte-identity requirement). The 0x0b navmesh was
    # already injected above; inject_into_sv_only_blob only touches 0x05/0x14.
    if USE_HUB:
        _r09_hub_specs = build_hub_inject_specs().get(R09_KEY, [])
        if _r09_hub_specs:
            swapped_blob = inject_into_sv_only_blob(swapped_blob, _r09_hub_specs, R09_KEY)
            print(f'  TEST HUB: injected {len(_r09_hub_specs)} hub portal(s) into Random09A 0x05/0x14')

    # Overwrite the merged Random09A entry in-place (index identity stays AE's).
    merged_levels[ae_r09_idx]['ints_raw'] = bytes(swapped_ints)
    # Record the swapped blob so the DATA-compaction loop writes it instead of AE's.
    _r09_swap = (ae_r09_idx, swapped_blob)
    _sw_ir = struct.unpack_from('<13i', swapped_ints, 0)
    print(f'  R09-SWAP: SVAERA Random09A (idx {ae_r09_idx}) blob <- SV ({len(sv_r09_blob)} B), '
          f'0x0b donor {gen_path.name} ({len(gen_0b)} B)')
    print(f'    corner ({_sw_ir[6]},{_sw_ir[7]},{_sw_ir[8]}) + AE GUID kept; '
          f'swapped blob {len(swapped_blob)} B')

    # --- 7e. INTERIOR PORTALS (Track 2, flag SVC_INTERIOR_PORTALS=1) ---
    # The seamless grid-seam stitch failed 12x: the Frida debugger proved the
    # navmeshes load (R09/xPTS navmeshOK=1) and the cross-tag strips are present,
    # yet it still walls - and the R09|xPTS floors differ ~11u (a cliff). So we
    # replicate the WORKING HiddenValley01->Random09A cave-mouth PORTAL between the
    # interior rooms: a portal resolves the destination purely by GUID (height- and
    # geometry-independent), the one mechanism proven to move the player between
    # these relocated levels. Injects a GridEntrance + 0x14 binding into the source
    # and a reciprocal 0x06 descriptor into the destination (see
    # tools/inject_interior_portals.py + docs/CAVE_INTERIOR_PORTALS.md).
    if os.environ.get('SVC_INTERIOR_PORTALS') == '1':
        from inject_interior_portals import inject_interior_portals
        XPTS_KEY = 'levels/world/xbloodcave/xpassagetransitionstart.lvl'
        _xpts_sv_idx = next(i for i, lv in enumerate(sv_only)
                            if lv['fname'].replace(chr(92), '/').lower() == XPTS_KEY)
        _pblobs = {R09_KEY: swapped_blob, XPTS_KEY: converted_blobs[_xpts_sv_idx]}
        _pints = {R09_KEY: bytes(swapped_ints),
                  XPTS_KEY: shifted_ints_raw(sv_only[_xpts_sv_idx])}
        _idscan = [(b,) for b in converted_blobs.values()] + [(swapped_blob,)]
        _wiring = [{'fromLevel': R09_KEY, 'toLevel': XPTS_KEY,
                    'entrancePos': None, 'exitPos': None}]
        _preps = inject_interior_portals(
            get_blob=lambda k: _pblobs[k],
            set_blob=lambda k, v: _pblobs.__setitem__(k, v),
            get_ints=lambda k: _pints[k], level_index_by_key={},
            wiring=_wiring, id_scan_pairs=_idscan)
        swapped_blob = _pblobs[R09_KEY]
        converted_blobs[_xpts_sv_idx] = _pblobs[XPTS_KEY]
        _r09_swap = (ae_r09_idx, swapped_blob)   # compaction reads this for R09
        print(f'  INTERIOR PORTALS: injected {len(_preps)} seam(s) '
              f'(R09 blob now {len(swapped_blob)} B, xPTS {len(converted_blobs[_xpts_sv_idx])} B)')

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

    # --- M2: DE-PLACE MAP-REF-1 records (SV NPCs/setdress absent from the arz) -----------
    # Runs as the FINAL per-blob edit (after all injection + step-7 0x14 appends + navmesh),
    # so remove_0x05_instances_by_dbr's 0x14 reindex accounts for every injected binding.
    # Interim build30 default (Will can override to full-restore-later); see REMOVE_BY_DBR_SPECS.
    print('\n=== M2: de-placing MAP-REF-1 records ===')
    _m2_total = 0
    _m2_per_level = {}
    for i, lv in enumerate(ae_levels):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in REMOVE_BY_DBR_SPECS:
            if i in ae_patched_blobs:
                _base = ae_patched_blobs[i]
            elif _r09_swap and i == _r09_swap[0]:
                _base = _r09_swap[1]
            else:
                _base = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            newb, n = remove_0x05_instances_by_dbr(_base, REMOVE_BY_DBR_SPECS[lv_key], lv_key)
            ae_patched_blobs[i] = newb
            _m2_total += n
            _m2_per_level[lv_key] = n
    for i, lv in enumerate(sv_only):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in REMOVE_BY_DBR_SPECS:
            newb, n = remove_0x05_instances_by_dbr(converted_blobs[i], REMOVE_BY_DBR_SPECS[lv_key], lv_key)
            converted_blobs[i] = newb
            _m2_total += n
            _m2_per_level[lv_key] = n
    print(f'  M2: de-placed {_m2_total} instance(s) across {len(_m2_per_level)} level(s)')
    assert len(_m2_per_level) == len(REMOVE_BY_DBR_SPECS), \
        (f'M2 touched {len(_m2_per_level)} levels, expected {len(REMOVE_BY_DBR_SPECS)} '
         f'(missing: {sorted(set(REMOVE_BY_DBR_SPECS) - set(_m2_per_level))})')
    # 72 = build30's 70 (68 D3 pairs, 2 double-placed) + build31's 2 latent Helos soul
    # collectors (exposed by the N1 portal making startingfarmland06d a scanned level).
    assert _m2_total == 72, f'M2 expected 72 de-placements, got {_m2_total}'

    # --- M6: DE-PLACE the DANGLING Olympus respawn shrine (Will 2026-07-09) --------------
    # Same de-place mechanism as M2 but a distinct concern (a base-game respawn shrine whose
    # world GROUPS(0x11) binding was lost in the SVAERA merge -> visible but non-functional).
    # See build_section_surgery.REMOVE_DANGLING_SHRINE_SPECS for the full RCA. Runs after M2
    # so the by-dbr 0x14 reindex accounts for every prior edit (OlympusFinal02 is untouched by
    # M2, so this is the only edit to it). Applies to BOTH the canonical and TESTHUB builds.
    print('\n=== M6: de-placing the dangling Olympus respawn shrine ===')
    _m6_total = 0
    _m6_per_level = {}
    for i, lv in enumerate(ae_levels):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in REMOVE_DANGLING_SHRINE_SPECS:
            if i in ae_patched_blobs:
                _base = ae_patched_blobs[i]
            elif _r09_swap and i == _r09_swap[0]:
                _base = _r09_swap[1]
            else:
                _base = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            newb, n = remove_0x05_instances_by_dbr(
                _base, REMOVE_DANGLING_SHRINE_SPECS[lv_key], lv_key)
            ae_patched_blobs[i] = newb
            _m6_total += n
            _m6_per_level[lv_key] = n
    for i, lv in enumerate(sv_only):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in REMOVE_DANGLING_SHRINE_SPECS:
            newb, n = remove_0x05_instances_by_dbr(
                converted_blobs[i], REMOVE_DANGLING_SHRINE_SPECS[lv_key], lv_key)
            converted_blobs[i] = newb
            _m6_total += n
            _m6_per_level[lv_key] = n
    print(f'  M6: de-placed {_m6_total} instance(s) across {len(_m6_per_level)} level(s)')
    assert len(_m6_per_level) == len(REMOVE_DANGLING_SHRINE_SPECS), \
        (f'M6 touched {len(_m6_per_level)} levels, expected '
         f'{len(REMOVE_DANGLING_SHRINE_SPECS)} '
         f'(missing: {sorted(set(REMOVE_DANGLING_SHRINE_SPECS) - set(_m6_per_level))})')
    assert _m6_total == 1, f'M6 expected 1 de-placement (respawn_olympus_new), got {_m6_total}'

    # --- M14: DE-PLACE stray cross-expansion props (audit 2026-07-10 Lane A) --------------
    # Same mechanism as M2/M6; distinct concern (a functionless locked Atlantis prop inside a
    # Greek minidungeon). See build_section_surgery.REMOVE_STRAY_PROP_SPECS for the RCA.
    print('\n=== M14: de-placing stray cross-expansion props ===')
    _m14_total = 0
    _m14_per_level = {}
    for i, lv in enumerate(ae_levels):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in REMOVE_STRAY_PROP_SPECS:
            if i in ae_patched_blobs:
                _base = ae_patched_blobs[i]
            elif _r09_swap and i == _r09_swap[0]:
                _base = _r09_swap[1]
            else:
                _base = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            newb, n = remove_0x05_instances_by_dbr(
                _base, REMOVE_STRAY_PROP_SPECS[lv_key], lv_key)
            ae_patched_blobs[i] = newb
            _m14_total += n
            _m14_per_level[lv_key] = n
    for i, lv in enumerate(sv_only):
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in REMOVE_STRAY_PROP_SPECS:
            newb, n = remove_0x05_instances_by_dbr(
                converted_blobs[i], REMOVE_STRAY_PROP_SPECS[lv_key], lv_key)
            converted_blobs[i] = newb
            _m14_total += n
            _m14_per_level[lv_key] = n
    print(f'  M14: de-placed {_m14_total} instance(s) across {len(_m14_per_level)} level(s)')
    assert len(_m14_per_level) == len(REMOVE_STRAY_PROP_SPECS), \
        (f'M14 touched {len(_m14_per_level)} levels, expected '
         f'{len(REMOVE_STRAY_PROP_SPECS)} '
         f'(missing: {sorted(set(REMOVE_STRAY_PROP_SPECS) - set(_m14_per_level))})')
    assert _m14_total == 1, f'M14 expected 1 de-placement (tombstone), got {_m14_total}'

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
