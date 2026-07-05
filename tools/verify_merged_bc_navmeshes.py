"""
Verify the FINAL merged map (local/Levels_merged.arc) actually carries real 0x0b
navmeshes at the blood-cave levels - not the dead 148-byte stub - before deploy.

For every xBloodCave level:
  - real navmesh expected: 0x0b size == the generated donor's .0b.bin size, 0x0a stripped.
  - ocean-scenery (no walkable geometry): 148-byte stub, 0x0a stripped.

Exits non-zero if any walkable BC level is missing its navmesh or still carries 0x0a.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections

REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
MAP_ARC = REPO / 'local' / 'Levels_merged.arc'
DONOR_DIR = REPO / 'local' / 'editor_normalized'
STUB_SIZE = 148

# The 7 ocean-scenery BC levels have no 0x0a geometry -> get the stub by design.
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
    """True if the navmesh center matches this level's index corner.

    Layout invariant (proven on healthy donors): center = corner - 16 + dims on
    the x and z axes (y half-extent rounding differs, so y is not gated). This
    catches STALE donors generated at a different GRID_SHIFT (the 2026-07-05
    corruption class: donors regenerated at an abandoned shift would otherwise
    inject navmeshes kilometres from their level, and a size-only check passes).
    """
    import struct
    (cx, _cy, cz), (dx, _dy, dz) = rec02_center_dims(sec_0b)
    ints = struct.unpack_from('<13i', lv['ints_raw'], 0)  # [6,7,8] = grid corner
    # Tolerance: odd-geometry levels differ from corner-16+dims by <=2u (tile-grid
    # rounding, shift-independent); a stale-GRID_SHIFT donor is off by 100s-1000s.
    return (abs(cx - (ints[6] - 16 + dx)) <= 4
            and abs(cz - (ints[8] - 16 + dz)) <= 4)


def main():
    print('=== Verify merged-map blood-cave navmeshes ===')
    print(f'  map: {MAP_ARC}  ({MAP_ARC.stat().st_size:,} bytes)')

    # donor bytes by basename (e.g. BC_initialpathway -> 48172 raw bytes)
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
    print(f'  levels in scope (xBloodCave + Random09A): {len(bc)}\n')

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
        if size_0b is None:
            verdict = 'FAIL: no 0x0b'; fails.append(base)
        elif has_0a:
            verdict = 'FAIL: 0x0a not stripped'; fails.append(base)
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
                verdict = 'ok ocean-stub'; stub_ok += 1
            else:
                verdict = f'? ocean but 0x0b={size_0b}'
        else:
            verdict = f'? no donor, 0x0b={size_0b} (non-BC-walkable stub)'
            if size_0b == STUB_SIZE:
                stub_ok += 1
        exp_s = str(exp) if exp is not None else ('stub' if is_ocean else '-')
        print(f'  {base:40s} {str(size_0b):>10s}  {exp_s:>10s}  {str(has_0a):>5s}  {verdict}')

    print('\n  ' + '=' * 60)
    print(f'  real navmeshes matching donor: {real_ok}/{len(donor_size)}')
    print(f'  ocean/other stubs: {stub_ok}')
    if fails:
        print(f'  FAIL ({len(fails)}): {fails}')
        sys.exit(1)
    if real_ok != len(donor_size):
        print(f'  FAIL: expected {len(donor_size)} real navmeshes, got {real_ok}')
        sys.exit(1)
    print('  PASS: every generated navmesh is present in the merged map, 0x0a stripped.')


if __name__ == '__main__':
    main()
