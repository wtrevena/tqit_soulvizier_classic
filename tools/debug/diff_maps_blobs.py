#!/usr/bin/env python3
"""Blob-level record-diff of two built Levels.arc maps.

The map lane's equivalent of the DB record-diff: for every level in both worlds, compare
the blob bytes; for every level that differs, report WHICH sections differ and the exact
0x05 instance delta (added / removed / moved). The gate the wave has to satisfy is
"ZERO unattributed changes and 0 REMOVED records", so removals and section changes other
than 0x05 are called out loudly - a 0x0b (navmesh) delta in particular is the b89
blood-cave crash class and must never appear from a placement change.

Usage: py tools/debug/diff_maps_blobs.py <baseline.arc> <new.arc>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from contracts_map import parse_0x05, parse_blob_sections   # noqa: E402
import survey_uberboss_spots as S                           # noqa: E402

BS = chr(92)
SECNAME = {0x05: '0x05 instances', 0x06: '0x06 doors', 0x09: '0x09 grid',
           0x0a: '0x0a PTH', 0x0b: '0x0b NAVMESH', 0x14: '0x14 meta', 0x17: '0x17 detail'}


def blobs(path):
    data, levels = S.load_world(path)
    out = {}
    for lv in levels:
        out[lv['fname'].replace(BS, '/').lower()] = (
            data[lv['data_offset']:lv['data_offset'] + lv['data_length']], lv)
    return out


def inst_key(i):
    return (i['dbr'].decode('latin1').lower(),
            round(i['pos'][0], 2), round(i['pos'][1], 2), round(i['pos'][2], 2))


def main():
    a, b = blobs(sys.argv[1]), blobs(sys.argv[2])
    print('baseline levels: %d   new levels: %d' % (len(a), len(b)))
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    if only_a:
        print('!! LEVELS REMOVED (%d): %s' % (len(only_a), only_a[:8]))
    if only_b:
        print('!! LEVELS ADDED   (%d): %s' % (len(only_b), only_b[:8]))

    changed = [k for k in sorted(set(a) & set(b)) if a[k][0] != b[k][0]]
    print('levels with differing blob bytes: %d\n' % len(changed))
    total_removed = 0
    navmesh_changes = 0
    for k in changed:
        ba, bb = a[k][0], b[k][0]
        sa = {t: d for t, d in parse_blob_sections(ba)}
        sb = {t: d for t, d in parse_blob_sections(bb)}
        diffsecs = sorted(set(sa) | set(sb),
                          key=lambda t: t)
        difflist = [t for t in diffsecs if sa.get(t) != sb.get(t)]
        names = ', '.join(SECNAME.get(t, hex(t)) for t in difflist)
        print('--- %s' % k)
        print('    sections differing: %s' % names)
        if 0x0b in difflist:
            navmesh_changes += 1
            print('    !! NAVMESH BYTES CHANGED - this is the b89 crash class')
        _s, ia = parse_0x05(ba)
        _s, ib = parse_0x05(bb)
        ka = [inst_key(i) for i in ia]
        kb = [inst_key(i) for i in ib]
        sa_set, sb_set = set(ka), set(kb)
        removed = sorted(sa_set - sb_set)
        added = sorted(sb_set - sa_set)
        print('    0x05 count %d -> %d' % (len(ia), len(ib)))
        for r in removed:
            print('      REMOVED  %-56s (%.2f,%.2f,%.2f)' % (r[0].split(BS)[-1], r[1], r[2], r[3]))
        for r in added:
            print('      ADDED    %-56s (%.2f,%.2f,%.2f)' % (r[0].split(BS)[-1], r[1], r[2], r[3]))
        total_removed += len(removed)
    print('\n' + '=' * 74)
    print('levels changed        : %d' % len(changed))
    print('0x05 instances removed: %d' % total_removed)
    print('navmesh (0x0b) changes: %d   <- MUST be 0 for a placement-only wave' % navmesh_changes)
    return 0


if __name__ == '__main__':
    sys.exit(main())
