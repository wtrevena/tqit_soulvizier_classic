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
    size_0b = next((len(s['data']) for s in secs if s['type'] == 0x0b), None)
    has_0a = any(s['type'] == 0x0a for s in secs)
    return size_0b, has_0a


def main():
    print('=== Verify merged-map blood-cave navmeshes ===')
    print(f'  map: {MAP_ARC}  ({MAP_ARC.stat().st_size:,} bytes)')

    # donor sizes by basename (e.g. BC_initialpathway -> 48172)
    donor_size = {}
    for p in DONOR_DIR.glob('*.0b.bin'):
        base = p.name[:-len('.0b.bin')]           # strip .0b.bin
        base = base[:-4] if base.lower().endswith('.lvl') else base  # strip .lvl
        donor_size[base.lower()] = p.stat().st_size
    print(f'  generated donors on disk: {len(donor_size)}')

    arc = ArcArchive.from_file(MAP_ARC)
    world_entry = [e for e in arc.entries if e.entry_type == 3][0]
    data = arc.decompress(world_entry)
    print(f'  world01.map: {len(data):,} bytes decompressed')
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    print(f'  levels in map: {len(levels)}')

    bc = [lv for lv in levels if 'xbloodcave' in lv['fname'].replace('\\', '/').lower()]
    print(f'  xBloodCave levels: {len(bc)}\n')

    real_ok = stub_ok = 0
    fails = []
    print(f'  {"level":40s} {"0x0b":>10s}  {"expect":>10s}  0x0a  verdict')
    print('  ' + '-' * 78)
    for lv in sorted(bc, key=lambda l: l['fname'].lower()):
        base = lv['fname'].replace('\\', '/').split('/')[-1]
        base = base[:-4] if base.lower().endswith('.lvl') else base
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        size_0b, has_0a = blob_0b_0a(blob)

        exp = donor_size.get(base.lower())
        is_ocean = base.lower() in OCEAN_STUB
        verdict = 'OK'
        if size_0b is None:
            verdict = 'FAIL: no 0x0b'; fails.append(base)
        elif has_0a:
            verdict = 'FAIL: 0x0a not stripped'; fails.append(base)
        elif exp is not None:
            if size_0b == exp:
                verdict = 'OK real navmesh'; real_ok += 1
            else:
                verdict = f'FAIL: size!=donor({exp})'; fails.append(base)
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
