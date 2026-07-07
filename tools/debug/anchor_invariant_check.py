#!/usr/bin/env python3
"""R5 - anchor / Y-align invariants on the regenerated donors.

The obstacle carve must not disturb the Y-alignment anchoring: carving only
REMOVES walkable cells, never moves a container center. This gate re-asserts the
two invariants the entrance depends on:
  1. Random09A donor container center Y == the 0x0a-authored center Y (24) +
     GRID_SHIFT dy (0) == 24. R09 is the cave entrance anchor; the fixed
     HiddenValley01 GridEntrance landing (findNearestPoly vertical ext 2u) misses
     the mesh if this drifts. (gen_bc_navmeshes' Y-ALIGN ANCHOR gate enforces
     R09 yshift==0; this checks the emitted donor.)
  2. Every walk-chain donor's container center is present and dims are integral.

Usage: py tools/debug/anchor_invariant_check.py
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
from rec02_format import parse_rec02                                 # noqa: E402
from gen_rec02 import load_tok_mesh                                  # noqa: E402

DONOR_DIR = Path(os.environ.get('SVC_DONOR_DIR',
                                str(REPO / 'local' / 'editor_normalized')))
UPSTREAM_SV_ARC = REPO / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc'
R09_KEY = 'levels/world/orient/underground/random09a.lvl'
R09_EXPECT_CENTER_Y = 24   # RCA + old donor: Random09A center Y (0x0a-authored, shift 0)


def main():
    print('=== R5 anchor / Y-align invariant check ===')
    ok = True

    # R09 authored center Y from upstream 0x0a
    arc = ArcArchive.from_file(UPSTREAM_SV_ARC)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    r09 = next(lv for lv in levels if lv['fname'].replace('\\', '/').lower() == R09_KEY)
    blob = data[r09['data_offset']:r09['data_offset'] + r09['data_length']]
    tmp = Path(tempfile.gettempdir()) / 'anchor_r09.lvl'
    tmp.write_bytes(blob)
    _g, center_a, _d, _v, _t, _o = load_tok_mesh(str(tmp))
    print(f'  Random09A 0x0a authored center Y = {center_a[1]} (expect {R09_EXPECT_CENTER_Y})')

    donor = DONOR_DIR / 'Random09A.lvl.0b.bin'
    if not donor.exists():
        print('  FAIL: Random09A donor missing')
        return 1
    d = parse_rec02(donor.read_bytes(), decompress=True)
    cy = d['center'][1]
    print(f'  Random09A donor center = {tuple(d["center"])} dims = {tuple(d["dims"])}')
    if center_a[1] != R09_EXPECT_CENTER_Y:
        print(f'  WARN: authored center Y {center_a[1]} != documented {R09_EXPECT_CENTER_Y}')
    if cy != R09_EXPECT_CENTER_Y:
        print(f'  FAIL: Random09A donor center Y {cy} != {R09_EXPECT_CENTER_Y} '
              f'(anchor drifted - entrance landing would miss the mesh)')
        ok = False
    else:
        print(f'  PASS: Random09A donor center Y == {R09_EXPECT_CENTER_Y} (anchor shift 0)')

    # integral dims across all donors
    bad = []
    for p in sorted(DONOR_DIR.glob('*.lvl.0b.bin')):
        dd = parse_rec02(p.read_bytes(), decompress=True)
        cx, cyv, cz = dd['center']
        dx, dy, dz = dd['dims']
        if any(not float(v).is_integer() for v in (cx, cyv, cz, dx, dy, dz)):
            bad.append(p.name)
    if bad:
        print(f'  FAIL: non-integral center/dims in {bad}')
        ok = False
    else:
        print(f'  PASS: all {len(list(DONOR_DIR.glob("*.lvl.0b.bin")))} donor centers/dims integral')

    print(f'\nR5 ANCHOR INVARIANT: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
