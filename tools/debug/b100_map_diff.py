#!/usr/bin/env python3
"""b100 - whole-map blob diff between two built `Levels.arc` files.

Read-only. Walks all 2,282 level blobs in both maps and reports every level whose
blob differs, section by section. This is the "ZERO unattributed changes" proof for
a map lane: the ONLY level that may differ is the one the lane declares, and inside
it the ONLY section that may differ is 0x05.

Usage:
  py tools/debug/b100_map_diff.py --a <baseline.arc> --b <new.arc>
"""
import sys
import argparse
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import contracts_map as CM                        # noqa: E402

EXPECTED_LEVEL = 'levels/world/xbloodcave/drxbc3.lvl'
EXPECTED_SECTIONS = {0x05}


def load(path):
    arc = CM.Arc.from_file(path)
    mp = arc.world_map()
    secs = CM.parse_top_sections(mp)
    levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
    return mp, secs, levels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    a = ap.parse_args()

    mpa, seca, lva = load(a.a)
    mpb, secb, lvb = load(a.b)
    print(f'A {a.a}\nB {a.b}')
    print(f'levels: {len(lva)} vs {len(lvb)}')
    assert len(lva) == len(lvb), 'level COUNT changed - that is never an 0x05 injection'

    # top-level sections other than DATA must be identical
    ta = {t: CM.sec_bytes(mpa, seca, t) for t in seca}
    tb = {t: CM.sec_bytes(mpb, secb, t) for t in secb}
    print(f'\ntop-level sections: A {sorted(hex(t) for t in ta)}')
    top_changed = []
    for t in sorted(set(ta) | set(tb)):
        if ta.get(t) != tb.get(t):
            top_changed.append(t)
            print(f'  0x{t:02x}  CHANGED  {len(ta.get(t, b"")):,} -> {len(tb.get(t, b"")):,} B')
    if not top_changed:
        print('  (all identical)')

    changed = []
    for i, (la, lb) in enumerate(zip(lva, lvb)):
        assert la['fname'] == lb['fname'], f'level ORDER changed at {i}'
        ba = mpa[la['data_offset']:la['data_offset'] + la['data_length']]
        bb = mpb[lb['data_offset']:lb['data_offset'] + lb['data_length']]
        if ba != bb:
            changed.append((i, la['fname'], ba, bb))
        elif la['ints_raw'] != lb['ints_raw']:
            changed.append((i, la['fname'], ba, bb))

    print(f'\nlevel blobs differing: {len(changed)}')
    ok = True
    for i, fname, ba, bb in changed:
        key = fname.replace('\\', '/').lower()
        sa = {t: d for t, d in CM.parse_blob_sections(ba)}
        sb = {t: d for t, d in CM.parse_blob_sections(bb)}
        diff = sorted({t for t in set(sa) | set(sb) if sa.get(t) != sb.get(t)})
        print(f'  [{i:4d}] {fname}  {len(ba):,} -> {len(bb):,} B  '
              f'sections changed: {[hex(t) for t in diff]}')
        for t in diff:
            print(f'          0x{t:02x}: {len(sa.get(t, b"")):,} -> {len(sb.get(t, b"")):,} B')
        if key != EXPECTED_LEVEL:
            print(f'          UNATTRIBUTED: this lane declares only {EXPECTED_LEVEL}')
            ok = False
        if set(diff) - EXPECTED_SECTIONS:
            print(f'          UNATTRIBUTED SECTION(S): '
                  f'{[hex(t) for t in sorted(set(diff) - EXPECTED_SECTIONS)]}')
            ok = False
        if 0x0b in sa and 0x0b in sb:
            same = sa[0x0b] == sb[0x0b]
            print(f'          0x0b navmesh {"IDENTICAL" if same else "CHANGED"} '
                  f'({len(sa[0x0b]):,} B, md5 {hashlib.md5(sa[0x0b]).hexdigest()})')
            if not same:
                ok = False
    if top_changed:
        print('\nTOP-LEVEL SECTION ATTRIBUTION')
        print('  0x02 DATA holds every level blob, so growing one blob MUST change it.')
        print('  0x01 LEVELS holds each level\'s (data_offset, data_length), so growing one')
        print('       blob MUST shift every later offset. That is only legitimate if NOTHING')
        print('       ELSE in the index moved - checked field by field below.')
        for t in top_changed:
            if t in (0x01, 0x02):
                continue
            print(f'  UNATTRIBUTED top-level section 0x{t:02x}')
            ok = False
        if 0x01 in top_changed:
            bad_ident, bad_len, shifted = [], [], 0
            for i, (la, lb) in enumerate(zip(lva, lvb)):
                # identity fields: name, tile dims, grid corner, level GUID
                if la['fname'] != lb['fname'] or la['ints_raw'] != lb['ints_raw']:
                    bad_ident.append((i, la['fname']))
                if la['data_length'] != lb['data_length']:
                    if la['fname'].replace('\\', '/').lower() != EXPECTED_LEVEL:
                        bad_len.append((i, la['fname'],
                                        lb['data_length'] - la['data_length']))
                if la['data_offset'] != lb['data_offset']:
                    shifted += 1
            print(f'       identity (fname + ints_raw: tile dims / grid corner / GUID): '
                  f'{len(lva) - len(bad_ident)}/{len(lva)} unchanged')
            print(f'       data_length changed on {len(bad_len)} level(s) other than the '
                  f'declared one')
            print(f'       data_offset shifted on {shifted} level(s) (the expected ripple '
                  f'after a +{lvb[2253]["data_length"] - lva[2253]["data_length"]} B blob)')
            if bad_ident:
                print(f'       UNATTRIBUTED identity change: {bad_ident[:10]}')
                ok = False
            if bad_len:
                print(f'       UNATTRIBUTED length change: {bad_len[:10]}')
                ok = False
            if not bad_ident and not bad_len:
                print('       0x01 change is ENTIRELY the offset ripple - attributed.')

    print(f'\nMAP DIFF: {"PASS - every change attributed" if ok else "FAIL - unattributed change"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
