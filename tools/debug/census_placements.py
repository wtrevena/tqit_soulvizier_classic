#!/usr/bin/env python3
"""Census EVERY 0x05 instance in a Levels.arc, grouped by level, flag custom bosses.

Usage: py tools/debug/census_placements.py <map.arc> [--dbr SUBSTR] [--level SUFFIX]
"""
import sys, os, struct, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections
from contracts_map import (parse_level_index, parse_blob_sections, parse_0x05,
                           blob_0x05_base, SEC_LEVELS)


def load_world(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    return data, levels


def instances(blob):
    """[(dbr_bytes, x, y, z)] for the blob's 0x05 section.

    BUILD46 FIX (fix-upstream): this used to walk with a HARDCODED 72-byte base
    record. The 0x05 stride is version-dependent - 72 only for v0x11/v0x0f, 56 for
    v0x0e - so on every v0x0e level the walk desynced after the first record and
    ran off the end of the section. `main()` swallowed the resulting struct.error
    in a bare `except: continue`, so 418 of the merged map's 496 v0x0e levels were
    SILENTLY DROPPED from the census (custom-encounter total 1705 instead of 3446).
    A census that silently omits a third of the world is worse than no census, so
    the walk now delegates to the ONE canonical version-aware parser
    (contracts_map.parse_0x05 / blob_0x05_base) instead of keeping a second copy.
    """
    return [(i['dbr'], i['pos'][0], i['pos'][1], i['pos'][2])
            for i in parse_0x05(blob)[1]]


# Patterns that indicate a mod-authored encounter (boss/proxy/summon monster).
CUSTOM = [b'drxmap\\proxy', b'\\proxy\\', b'svc', b'um_', b'q_', b'uber', b'toxeus',
          b'enslaver', b'permean', b'dragonliche', b'tombguardian', b'sepulcher',
          b'bloodcave', b'monsters\\bosses', b'bossproxy']


def is_custom(dbr):
    low = dbr.lower()
    return any(p in low for p in CUSTOM)


def _walk_0x05_exact(blob, base):
    """Independent flag-aware walk at an EXPLICIT base size.

    Returns (declared_count, walked_count, end_pos, section_len). A correct stride
    walks exactly `declared_count` records and lands EXACTLY on the section end -
    the same structural invariant gate_build32_parseback asserts. Deliberately does
    NOT call parse_0x05, so it is a genuine cross-check of the stride rule rather
    than a restatement of it.
    """
    d = None
    for t, sd in parse_blob_sections(blob):
        if t == 0x05:
            d = sd
            break
    if d is None:
        return 0, 0, 0, 0
    pos = 0
    nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
    for _ in range(nstr):
        ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
        pos += ln
    ninst = struct.unpack_from('<I', d, pos)[0]; pos += 4
    walked = 0
    for _ in range(ninst):
        if pos + base > len(d):
            break
        flags = struct.unpack_from('<I', d, pos + 52)[0]
        pos += base + (16 if flags != 0 else 0)
        walked += 1
    return ninst, walked, pos, len(d)


def verify_stride(map_path):
    """GATE: the version-aware stride walks every 0x05 section to its exact end, and
    the old hardcoded base-72 stride provably does not (planted negative test)."""
    from collections import Counter
    data, levels = load_world(map_path)
    ok = Counter(); bad = []
    neg_desync = Counter(); neg_total = Counter()
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        ver = blob[3]
        base = blob_0x05_base(blob)
        try:
            declared, walked, end, size = _walk_0x05_exact(blob, base)
        except Exception as e:
            bad.append((lv['fname'], f'v0x{ver:02x}', f'raised {e!r}'))
            continue
        if size == 0:
            ok[ver] += 1
            continue
        if walked != declared or end != size:
            bad.append((lv['fname'], f'v0x{ver:02x}',
                        f'walked {walked}/{declared}, end {end} != {size}'))
        else:
            ok[ver] += 1
        # planted negative: the pre-fix hardcoded stride on the SAME level
        neg_total[ver] += 1
        try:
            d2, w2, e2, s2 = _walk_0x05_exact(blob, 72)
            if w2 != d2 or e2 != s2:
                neg_desync[ver] += 1
        except Exception:
            neg_desync[ver] += 1

    print(f'=== GATE census stride: {map_path} ===')
    print(f'  levels: {len(levels)}')
    print('  version-aware stride (blob_0x05_base) - sections walked to EXACT end:')
    for ver in sorted(ok):
        print(f'    v0x{ver:02x}: {ok[ver]} PASS')
    print('  PLANTED NEGATIVE - the pre-fix hardcoded base-72 stride, same levels:')
    for ver in sorted(neg_total):
        print(f'    v0x{ver:02x}: {neg_desync[ver]} / {neg_total[ver]} levels DESYNC')
    if bad:
        print(f'  [FAIL] {len(bad)} level(s) failed the exact-end invariant:')
        for row in bad[:20]:
            print(f'    {row}')
        return 1
    if not neg_desync:
        print('  [FAIL] the planted negative did NOT desync anywhere - the gate is '
              'not actually testing the stride rule')
        return 1
    print()
    print('RESULT: PASS (every 0x05 section walks to its exact end at the '
          'version-derived stride; the hardcoded-72 stride demonstrably does not)')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--dbr', default=None, help='only count dbrs containing this substr')
    ap.add_argument('--level', default=None, help='dump full per-instance for this level suffix')
    ap.add_argument('--top', type=int, default=30)
    ap.add_argument('--verify-stride', action='store_true',
                    help='GATE: prove the 0x05 stride rule on every level in the map '
                         '(with a planted negative for the old hardcoded base-72)')
    args = ap.parse_args()

    if args.verify_stride:
        return verify_stride(args.map)

    data, levels = load_world(args.map)
    per_level = []  # (fname, custom_count, total, [(dbr,x,y,z)])
    unparsed = []   # levels whose 0x05 could not be walked - REPORTED, never silent
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        try:
            insts = instances(blob)
        except Exception as e:
            # BUILD46: this used to be a bare `continue`, which is how the v0e stride
            # bug hid 418 levels. A census must never quietly lose a level.
            unparsed.append((lv['fname'], f'v0x{blob[3]:02x}', repr(e)))
            continue
        if args.dbr:
            sel = [i for i in insts if args.dbr.lower().encode() in i[0].lower()]
        else:
            sel = [i for i in insts if is_custom(i[0])]
        per_level.append((lv['fname'], len(sel), len(insts), sel))

    if unparsed:
        print(f'!! {len(unparsed)} level(s) whose 0x05 section could NOT be walked '
              f'(NOT counted below):')
        for fname, ver, err in unparsed[:20]:
            print(f'   {fname}  {ver}  {err}')
        if len(unparsed) > 20:
            print(f'   ... and {len(unparsed) - 20} more')

    if args.level:
        suf = args.level.replace('/', '\\').lower()
        for fname, nc, nt, sel in per_level:
            if fname.replace('/', '\\').lower().endswith(suf) or suf in fname.replace('/', '\\').lower():
                print(f'=== {fname}  custom={nc} total={nt} ===')
                # group by dbr
                from collections import Counter
                cnt = Counter(i[0] for i in sel)
                for dbr, n in cnt.most_common():
                    xs = [i for i in sel if i[0] == dbr]
                    coords = ' '.join(f'({i[1]:.0f},{i[2]:.0f},{i[3]:.0f})' for i in xs[:12])
                    print(f'  {n:3d}x {dbr.decode(errors="replace")}')
                    print(f'        {coords}')
        return

    per_level.sort(key=lambda r: -r[1])
    print(f'MAP: {args.map}')
    print(f'levels={len(levels)}  (showing top {args.top} by custom-encounter count)')
    for fname, nc, nt, sel in per_level[:args.top]:
        if nc == 0:
            break
        print(f'  {nc:4d} custom / {nt:4d} total  {fname}')


if __name__ == '__main__':
    sys.exit(main() or 0)
