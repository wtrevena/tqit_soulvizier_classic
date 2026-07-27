"""Section-level diff of two merged Levels.arc builds.

Answers the only questions a map wave's gate record needs: which LEVEL BLOBS changed,
which TOP-LEVEL sections changed (QUESTS/GROUPS/SD/BITMAPS/DATA2 must normally be
byte-identical), and - for a navmesh wave - what happened to each changed level's 0x0b.

Usage:
  py tools/diff_merged_maps.py <before.arc> <after.arc> [--expect a,b,c]

--expect names the level basenames that are ALLOWED to differ; the tool exits 1 if the
actual changed set is not exactly that set.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'contracts'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections
from contracts_map import rec02_structure

SEC_NAMES = {0x01: 'LEVELS', 0x02: 'DATA', 0x10: 'SEC_0x10', 0x11: 'GROUPS',
             0x18: 'SD', 0x19: 'BITMAPS', 0x1a: 'DATA2', 0x1b: 'QUESTS'}


def load(p):
    arc = ArcArchive.from_file(Path(p))
    world = [e for e in arc.entries if e.entry_type == 3][0]
    data = arc.decompress(world)
    secs = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, secs[SEC_LEVELS])
    return data, secs, levels


def basename(fn):
    b = fn.replace('\\', '/').split('/')[-1]
    return b[:-4] if b.lower().endswith('.lvl') else b


def sec0b(blob):
    try:
        secs, _ = parse_blob_sections(blob)
    except Exception:                                              # noqa: BLE001
        return None
    return next((s['data'] for s in secs if s['type'] == 0x0b), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('before')
    ap.add_argument('after')
    ap.add_argument('--expect', default=None,
                    help='comma-separated level basenames allowed to differ')
    args = ap.parse_args()

    da, sa, la = load(args.before)
    db, sb, lb = load(args.after)
    print(f'BEFORE {args.before}  ({Path(args.before).stat().st_size:,} B, {len(la)} levels)')
    print(f'AFTER  {args.after}  ({Path(args.after).stat().st_size:,} B, {len(lb)} levels)')

    print('\n--- top-level sections ---')
    for t in sorted(set(sa) | set(sb)):
        nm = SEC_NAMES.get(t, f'0x{t:02x}')
        A = da[sa[t]['data_offset']:sa[t]['data_offset'] + sa[t]['size']] if t in sa else None
        B = db[sb[t]['data_offset']:sb[t]['data_offset'] + sb[t]['size']] if t in sb else None
        if A is None or B is None:
            print(f'  {nm:9s} PRESENT-ONLY-IN-{"AFTER" if A is None else "BEFORE"}')
        elif A == B:
            print(f'  {nm:9s} byte-identical ({len(A):,} B)')
        else:
            print(f'  {nm:9s} DIFFERS  {len(A):,} -> {len(B):,} B  ({len(B) - len(A):+,})')

    ia = {basename(l['fname']): l for l in la}
    ib = {basename(l['fname']): l for l in lb}
    only_a, only_b = sorted(set(ia) - set(ib)), sorted(set(ib) - set(ia))
    if only_a or only_b:
        print(f'\n  LEVEL SET CHANGED: only-before={only_a} only-after={only_b}')

    print('\n--- level blobs ---')
    changed = []
    for nm in sorted(set(ia) & set(ib)):
        A = da[ia[nm]['data_offset']:ia[nm]['data_offset'] + ia[nm]['data_length']]
        B = db[ib[nm]['data_offset']:ib[nm]['data_offset'] + ib[nm]['data_length']]
        if A != B:
            changed.append(nm)
            oa, ob = sec0b(A), sec0b(B)
            ea = rec02_structure(oa)[0] if oa else ['(absent)']
            eb = rec02_structure(ob)[0] if ob else ['(absent)']
            print(f'  {nm:38s} blob {len(A):>9,} -> {len(B):>9,}   '
                  f'0x0b {str(len(oa) if oa else None):>8s} -> {str(len(ob) if ob else None):<8s}')
            print(f'  {"":38s}   struct: {("OK" if not ea else ea[0])!s}'
                  f'  ->  {("OK" if not eb else eb[0])!s}')
            if oa and ob:
                gca = struct.unpack_from('<I', oa, 12)[0]
                gcb = struct.unpack_from('<I', ob, 12)[0]
                ga = [oa[16 + i * 16:32 + i * 16].hex() for i in range(min(gca, 16))]
                gb = [ob[16 + i * 16:32 + i * 16].hex() for i in range(min(gcb, 16))]
                print(f'  {"":38s}   guids: gc={gca} distinct={len(set(ga))}'
                      f'  ->  gc={gcb} distinct={len(set(gb))}')
    print(f'\n  changed level blobs: {len(changed)}')
    if not changed:
        print('  (none)')

    rc = 0
    if args.expect is not None:
        want = sorted(x.strip() for x in args.expect.split(',') if x.strip())
        got = sorted(changed)
        if got == want:
            print(f'\nEXPECT-SET MATCH: exactly {len(want)} intended blobs changed.')
        else:
            print(f'\nEXPECT-SET MISMATCH\n  expected: {want}\n  actual:   {got}\n'
                  f'  unexpected: {sorted(set(got) - set(want))}\n'
                  f'  missing:    {sorted(set(want) - set(got))}')
            rc = 1
    sys.exit(rc)


if __name__ == '__main__':
    main()
