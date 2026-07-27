"""
Verify the FINAL merged map (local/Levels_merged.arc) actually carries real 0x0b
navmeshes at the blood-cave levels - not the dead 148-byte stub - before deploy.

For every xBloodCave level:
  - real navmesh expected: 0x0b size == the generated donor's .0b.bin size, 0x0a stripped.
  - ocean-scenery (no walkable geometry): the 224-byte EMPTY container, 0x0a stripped.

Exits non-zero if any walkable BC level is missing its navmesh or still carries 0x0a,
or if any 0x0b (real OR empty) is structurally malformed.

b89 (2026-07-27): the empty container used to be the dead 148-byte Approach-22 stub,
whose body held one TRUNCATED tileset instead of three complete ones - ProcessRLTD read
past the end of the section and killed the game on stream-in (two Frida sessions, both
at ocean_extension05). This verifier only ever compared SIZES, so it happily reported
'ok ocean-stub' for eight landmines. It now walks the container structure too.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections, EMPTY_REC02_SIZE
sys.path.insert(0, str(Path(__file__).parent / 'contracts'))
from contracts_map import rec02_structure

import os
REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
# Overridable so a scratch/worktree build (SVC_OUT_DIR + SVC_DONOR_DIR) can be verified
# without touching the live local/ build47 artifact; defaults preserve prior behaviour.
# SVC_MERGED_ARC names the exact merged arc to check (canonical OR TESTHUB); if unset it
# falls back to <SVC_OUT_DIR or local>/Levels_merged.arc.
_OUT_DIR = Path(os.environ.get('SVC_OUT_DIR', str(REPO / 'local')))
MAP_ARC = Path(os.environ.get('SVC_MERGED_ARC', str(_OUT_DIR / 'Levels_merged.arc')))
DONOR_DIR = Path(os.environ.get('SVC_DONOR_DIR', str(REPO / 'local' / 'editor_normalized')))
STUB_SIZE = EMPTY_REC02_SIZE   # 224 since b89 (was the malformed 148-byte Approach-22 stub)

# The 7 ocean-scenery BC levels have no 0x0a geometry -> get the empty container by design.
OCEAN_STUB = {
    'ocean_extension05', 'ocean_extensionx01', 'ocean_extensionx03',
    'ocean_extensionx05', 'ocean_extensionx04', 'ocean_extensionx06',
    'ocean_extensionx07',
}


def blob_0b_0a(blob):
    secs, _ = parse_blob_sections(blob)
    data_0b = next((s['data'] for s in secs if s['type'] == 0x0b), None)
    has_0a = any(s['type'] == 0x0a for s in secs)
    return data_0b, has_0a


def rec02_center_dims(d):
    """(center xyz, dims xyz) from a raw REC\\x02 section."""
    import struct
    gc = struct.unpack_from('<I', d, 12)[0]
    pos = 16 + gc * 16
    return struct.unpack_from('<3i', d, pos), struct.unpack_from('<3I', d, pos + 12)


def center_consistent(sec_0b, lv):
    """True if the navmesh is positioned right for this level's index corner.

    Layout invariant (global-lattice pipeline, 2026-07-05): the mesh corner
    (center - dims) is the level's padded corner (grid corner - 16) snapped DOWN
    to the generation frame's 64u tile lattice on x and z, and the far edge
    covers the level box + 16u pad. So: corner within [padded-63, padded], far
    edge >= padded far edge. (Cross-donor lattice phase consistency - the actual
    walkability requirement - is gated separately by the merged-map seam
    alignment check.) This still catches STALE donors generated at a different
    GRID_SHIFT (off by hundreds of units -> outside the snap window). y is not
    gated (half-extent rounding differs).
    """
    import struct
    (cx, _cy, cz), (dx, _dy, dz) = rec02_center_dims(sec_0b)
    ints = struct.unpack_from('<13i', lv['ints_raw'], 0)  # [6,7,8] = grid corner
    mx0, mz0, mx1, mz1 = cx - dx, cz - dz, cx + dx, cz + dz
    lo_x, lo_z = ints[6] - 16, ints[8] - 16
    hi_x, hi_z = ints[6] + 2 * ints[3] + 16, ints[8] + 2 * ints[5] + 16
    return (lo_x - 63 <= mx0 <= lo_x and lo_z - 63 <= mz0 <= lo_z
            and mx1 >= hi_x and mz1 >= hi_z)


def main():
    print('=== Verify merged-map blood-cave navmeshes ===')
    print(f'  map: {MAP_ARC}  ({MAP_ARC.stat().st_size:,} bytes)')

    # donor bytes by basename (e.g. BC_initialpathway -> 48172 raw bytes). ALL donors
    # on disk are read here; the pass/fail count below is restricted to donors whose
    # level is IN SCOPE (blood cave + Random09A), so other areas' donors in the same
    # dir (Wave 1+ single-level areas) neither inflate nor fail this blood-cave gate.
    donor_bytes = {}
    for p in DONOR_DIR.glob('*.0b.bin'):
        base = p.name[:-len('.0b.bin')]           # strip .0b.bin
        base = base[:-4] if base.lower().endswith('.lvl') else base  # strip .lvl
        donor_bytes[base.lower()] = p.read_bytes()
    donor_size = {k: len(v) for k, v in donor_bytes.items()}
    print(f'  generated donors on disk: {len(donor_size)}')

    arc = ArcArchive.from_file(MAP_ARC)
    world_entry = [e for e in arc.entries if e.entry_type == 3][0]
    data = arc.decompress(world_entry)
    print(f'  world01.map: {len(data):,} bytes decompressed')
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    print(f'  levels in map: {len(levels)}')

    def in_scope(lv):
        key = lv['fname'].replace('\\', '/').lower()
        # xBloodCave cluster + the blob-swapped SV-Random09A doorway cave
        # (Orient/Underground path, so the xbloodcave filter misses it).
        return 'xbloodcave' in key or key.endswith('orient/underground/random09a.lvl')

    bc = [lv for lv in levels if in_scope(lv)]
    # Donors that belong to an in-scope level = the count this gate must match
    # (a donor exists for a level, and that level is in scope).
    scope_bases = set()
    for lv in bc:
        b = lv['fname'].replace('\\', '/').split('/')[-1]
        b = b[:-4] if b.lower().endswith('.lvl') else b
        scope_bases.add(b.lower())
    n_scope_donors = sum(1 for k in donor_size if k in scope_bases)
    print(f'  levels in scope (xBloodCave + Random09A): {len(bc)}  '
          f'(in-scope donors: {n_scope_donors})\n')

    real_ok = stub_ok = 0
    fails = []
    print(f'  {"level":40s} {"0x0b":>10s}  {"expect":>10s}  0x0a  verdict')
    print('  ' + '-' * 78)
    for lv in sorted(bc, key=lambda l: l['fname'].lower()):
        base = lv['fname'].replace('\\', '/').split('/')[-1]
        base = base[:-4] if base.lower().endswith('.lvl') else base
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        sec_0b, has_0a = blob_0b_0a(blob)
        size_0b = len(sec_0b) if sec_0b is not None else None

        exp_bytes = donor_bytes.get(base.lower())
        exp = donor_size.get(base.lower())
        is_ocean = base.lower() in OCEAN_STUB
        verdict = 'OK'
        # b89: EVERY 0x0b here (real donor or empty container) must be structurally
        # walkable end-to-end, not merely the right size. This is the check whose
        # absence let 8 malformed containers ship.
        struct_errs = rec02_structure(sec_0b)[0] if sec_0b is not None else ['no 0x0b']
        if size_0b is None:
            verdict = 'FAIL: no 0x0b'; fails.append(base)
        elif has_0a:
            verdict = 'FAIL: 0x0a not stripped'; fails.append(base)
        elif struct_errs:
            verdict = f'FAIL: malformed container - {struct_errs[0]}'; fails.append(base)
        elif exp_bytes is not None:
            if sec_0b != exp_bytes:
                verdict = ('FAIL: bytes!=donor' if size_0b == exp
                           else f'FAIL: size!=donor({exp})')
                fails.append(base)
            elif not center_consistent(sec_0b, lv):
                import struct as _st
                c, _d = rec02_center_dims(sec_0b)
                _ir = _st.unpack_from('<13i', lv['ints_raw'], 0)
                verdict = (f'FAIL: STALE center {tuple(c)} vs corner '
                           f'{_ir[6:9]} (regen donors!)')
                fails.append(base)
            else:
                verdict = 'OK real navmesh (bytes+center)'; real_ok += 1
        elif is_ocean:
            if size_0b == STUB_SIZE:
                verdict = 'ok ocean empty-container (valid)'; stub_ok += 1
            else:
                verdict = f'FAIL: ocean but 0x0b={size_0b} (expect {STUB_SIZE})'
                fails.append(base)
        else:
            verdict = f'? no donor, 0x0b={size_0b} (non-BC-walkable empty)'
            if size_0b == STUB_SIZE:
                stub_ok += 1
        exp_s = str(exp) if exp is not None else (str(STUB_SIZE) if is_ocean else '-')
        print(f'  {base:40s} {str(size_0b):>10s}  {exp_s:>10s}  {str(has_0a):>5s}  {verdict}')

    print('\n  ' + '=' * 60)
    print(f'  real navmeshes matching donor: {real_ok}/{n_scope_donors} (in scope)')
    print(f'  ocean/other stubs: {stub_ok}')
    if fails:
        print(f'  FAIL ({len(fails)}): {fails}')
        sys.exit(1)
    if real_ok != n_scope_donors:
        print(f'  FAIL: expected {n_scope_donors} in-scope real navmeshes, got {real_ok}')
        sys.exit(1)
    print('  PASS: every in-scope generated navmesh is present in the merged map, 0x0a stripped.')


if __name__ == '__main__':
    main()
