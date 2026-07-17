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
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS

BASE = 72


def load_world(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    return data, levels


def instances(blob):
    """[(dbr_bytes, x, y, z)] across all 0x05 sections in blob."""
    out = []
    for t, d in parse_blob_sections(blob):
        if t != 0x05:
            continue
        pos = 0
        nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
        strings = []
        for _ in range(nstr):
            ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
            strings.append(d[pos:pos + ln]); pos += ln
        ninst = struct.unpack_from('<I', d, pos)[0]; pos += 4
        for _ in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            x, y, z = struct.unpack_from('<fff', d, pos + 40)
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            out.append((strings[sid] if sid < len(strings) else b'?', x, y, z))
            pos += BASE + (16 if flags != 0 else 0)
    return out


# Patterns that indicate a mod-authored encounter (boss/proxy/summon monster).
CUSTOM = [b'drxmap\\proxy', b'\\proxy\\', b'svc', b'um_', b'q_', b'uber', b'toxeus',
          b'enslaver', b'permean', b'dragonliche', b'tombguardian', b'sepulcher',
          b'bloodcave', b'monsters\\bosses', b'bossproxy']


def is_custom(dbr):
    low = dbr.lower()
    return any(p in low for p in CUSTOM)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--dbr', default=None, help='only count dbrs containing this substr')
    ap.add_argument('--level', default=None, help='dump full per-instance for this level suffix')
    ap.add_argument('--top', type=int, default=30)
    args = ap.parse_args()

    data, levels = load_world(args.map)
    per_level = []  # (fname, custom_count, total, [(dbr,x,y,z)])
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        try:
            insts = instances(blob)
        except Exception as e:
            continue
        if args.dbr:
            sel = [i for i in insts if args.dbr.lower().encode() in i[0].lower()]
        else:
            sel = [i for i in insts if is_custom(i[0])]
        per_level.append((lv['fname'], len(sel), len(insts), sel))

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
    main()
