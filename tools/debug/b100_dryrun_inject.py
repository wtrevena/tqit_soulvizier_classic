#!/usr/bin/env python3
"""b100 - DRY RUN the Sanctuary injection into a COPY of a built level blob.

Read-only against the map on disk: it pulls drxBC3's blob out of a built
`Levels.arc`, runs the SAME injector the real build runs
(`build_section_surgery.inject_into_sv_only_blob`) against an in-memory COPY, and
diffs the result section by section. Nothing is written unless `--out` is given.

This is the pre-build proof demanded by the b89 navmesh-crash lesson: the b89
crash was a malformed 148-byte stub `0x0b`, and the one thing this lane must never
do is disturb a navmesh container. The dry run proves, before a single real byte
moves, that ONLY `0x05` changes and that `0x0b` is byte-identical.

Usage:
  py tools/debug/b100_dryrun_inject.py --map local/b100_base/Levels_merged.arc
"""
import sys
import argparse
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

import contracts_map as CM                       # noqa: E402
import build_section_surgery as BSS               # noqa: E402

SECTION_NAMES = {0x05: '0x05 placed instances', 0x06: '0x06 grid descriptors',
                 0x09: '0x09 terrain', 0x0a: '0x0a PTH (legacy)',
                 0x0b: '0x0b REC\\x02 navmesh', 0x14: '0x14 instance bindings',
                 0x17: '0x17 REGION list'}


def sections(blob):
    return {t: d for t, d in CM.parse_blob_sections(blob)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'b100_base' / 'Levels_merged.arc'))
    ap.add_argument('--out', default=None, help='optional: write the patched blob for inspection')
    a = ap.parse_args()

    key = BSS.SANCTUARY_HOST_KEY
    specs = BSS.INJECT_SPECS[key]

    arc = CM.Arc.from_file(a.map)
    mp = arc.world_map()
    secs = CM.parse_top_sections(mp)
    levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
    lv = next(l for l in levels
              if l['fname'].replace('\\', '/').lower() == key)
    before = bytes(mp[lv['data_offset']:lv['data_offset'] + lv['data_length']])

    print(f'map   : {a.map}')
    print(f'level : {key}  blob v0x{before[3]:02x}  {len(before):,} B  '
          f'md5 {hashlib.md5(before).hexdigest()}')
    print(f'specs : {len(specs)} injections\n')

    after = BSS.inject_into_sv_only_blob(bytearray(before), specs, key)
    after = bytes(after)
    print(f'patched blob: {len(after):,} B  md5 {hashlib.md5(after).hexdigest()}  '
          f'delta {len(after) - len(before):+,} B\n')

    sb, sa = sections(before), sections(after)
    assert set(sb) == set(sa), f'section SET changed: {sorted(sb)} -> {sorted(sa)}'
    changed = []
    print('%-26s %14s %14s  %s' % ('section', 'before', 'after', 'verdict'))
    for t in sorted(sb):
        nm = SECTION_NAMES.get(t, f'0x{t:02x}')
        same = sb[t] == sa[t]
        if not same:
            changed.append(t)
        print('%-26s %14s %14s  %s'
              % (nm, f'{len(sb[t]):,} B', f'{len(sa[t]):,} B',
                 'IDENTICAL' if same else f'CHANGED ({len(sa[t]) - len(sb[t]):+,} B)'))

    print()
    ok = True
    if changed != [0x05]:
        print(f'FAIL: expected ONLY 0x05 to change, got {[hex(c) for c in changed]}')
        ok = False
    else:
        print('PASS: exactly one section changed and it is 0x05.')
    if sb[0x0b] != sa[0x0b]:
        print('FAIL: the 0x0b navmesh container moved - this is the b89 crash class.')
        ok = False
    else:
        print(f'PASS: 0x0b navmesh byte-identical ({len(sb[0x0b]):,} B, '
              f'md5 {hashlib.md5(sb[0x0b]).hexdigest()}).')

    n_before = len(CM.parse_0x05(before)[1])
    n_after = len(CM.parse_0x05(after)[1])
    print(f'0x05 instances: {n_before} -> {n_after}  (expected +{len(specs)})')
    if n_after - n_before != len(specs):
        print('FAIL: instance-count delta does not match the spec count.')
        ok = False

    # the first n_before instances must be byte-for-byte the ORIGINAL ones (add-only)
    ib, ia = CM.parse_0x05(before)[1], CM.parse_0x05(after)[1]
    moved = [i for i in range(n_before)
             if ib[i]['dbr'] != ia[i]['dbr'] or ib[i]['pos'] != ia[i]['pos']
             or ib[i]['flags'] != ia[i]['flags'] or ib[i]['uid'] != ia[i]['uid']]
    if moved:
        print(f'FAIL: {len(moved)} pre-existing instance(s) moved or changed: {moved[:10]}')
        ok = False
    else:
        print(f'PASS: all {n_before} pre-existing instances byte-preserved (ADD-ONLY, '
              f'retirement protocol).')

    print('\nNEW instances appended at the tail:')
    for i in range(n_before, n_after):
        it = ia[i]
        print('  [%4d] %-34s local(%8.3f,%7.3f,%8.3f) flags=%d uid=%s'
              % (i, it['dbr'].decode('latin-1').split('\\')[-1], it['pos'][0],
                 it['pos'][1], it['pos'][2], it['flags'],
                 'none' if it['uid'] is None else it['uid'].hex()))

    if a.out:
        Path(a.out).write_bytes(after)
        print(f'\nwrote {a.out}')
    print(f'\nDRY RUN: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
