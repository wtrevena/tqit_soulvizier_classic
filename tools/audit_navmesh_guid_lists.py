"""Audit every level's 0x0b (REC\\x02) navmesh GUID list + container structure in a
Levels.arc, and flag structurally invalid / degenerate containers.

Born from the b89 ocean_extension05 crash (2026-07-27): two independent runtime
sessions died inside ProcessRLTD while streaming ocean_extension05, whose GUID list
read [own, own, own]. That signature is the fingerprint of the dead Approach-22
"148-byte stub" (tools/build_section_surgery.build_minimal_rec02), which is NOT a
valid REC\\x02 container: it emits ONE truncated 44-byte tileset instead of the three
complete 56-byte dtTileCacheParams+numTiles tilesets the engine parses, so
ProcessRLTD runs off the end of the section.

Usage:
  py tools/audit_navmesh_guid_lists.py <Levels.arc> [<Levels.arc> ...] [--json OUT]
"""
import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections

PARAMS_LEN = 52          # dtTileCacheParams
TILESET_HDR = PARAMS_LEN + 4   # + int32 numTiles
N_SETS = 3               # Normal / Epic / Legendary - engine requires all three


def basename(fname):
    b = fname.replace('\\', '/').split('/')[-1]
    return b[:-4] if b.lower().endswith('.lvl') else b


def decode_container(d):
    """Structural decode of a raw 0x0b section. Never raises; reports what it found."""
    out = {'size': len(d), 'ok': True, 'errors': []}
    if len(d) < 16 or d[:4] != b'REC\x02':
        out['ok'] = False
        out['errors'].append('bad magic')
        return out
    version, payload_size, guid_count = struct.unpack_from('<3I', d, 4)
    out['version'] = version
    out['payload_size'] = payload_size
    out['payload_size_expected'] = len(d) - 12
    out['guid_count'] = guid_count
    if version != 1:
        out['ok'] = False
        out['errors'].append(f'version={version} != 1')
    if payload_size != len(d) - 12:
        out['ok'] = False
        out['errors'].append(f'payload_size={payload_size} != {len(d)-12}')
    pos = 16
    if guid_count > 64 or pos + guid_count * 16 + 24 > len(d):
        out['ok'] = False
        out['errors'].append(f'guid_count={guid_count} does not fit in section')
        return out
    out['guids'] = [d[pos + i * 16: pos + (i + 1) * 16].hex() for i in range(guid_count)]
    pos += guid_count * 16
    out['center'] = list(struct.unpack_from('<3i', d, pos))
    out['dims'] = list(struct.unpack_from('<3I', d, pos + 12))
    pos += 24
    out['body_offset'] = pos
    sets = []
    while pos < len(d):
        if pos + TILESET_HDR > len(d):
            out['ok'] = False
            out['errors'].append(
                f'TRUNCATED tileset #{len(sets)+1}: {len(d)-pos} bytes left, '
                f'need >= {TILESET_HDR}')
            break
        pv = struct.unpack_from('<3f2f2i4f2i', d, pos)
        num_tiles = struct.unpack_from('<i', d, pos + PARAMS_LEN)[0]
        s = {'cs': pv[3], 'ch': pv[4], 'width': pv[5], 'height': pv[6],
             'maxTiles': pv[11], 'maxObstacles': pv[12], 'numTiles': num_tiles}
        pos += TILESET_HDR
        if num_tiles < 0 or num_tiles > 100000:
            out['ok'] = False
            out['errors'].append(f'tileset #{len(sets)+1}: absurd numTiles={num_tiles}')
            sets.append(s)
            break
        bad = False
        for t in range(num_tiles):
            if pos + 4 > len(d):
                out['ok'] = False
                out['errors'].append(f'tileset #{len(sets)+1} tile {t}: truncated dataSize')
                bad = True
                break
            dsize = struct.unpack_from('<i', d, pos)[0]
            pos += 4
            if dsize < 56 or pos + dsize + 8 > len(d):
                out['ok'] = False
                out['errors'].append(
                    f'tileset #{len(sets)+1} tile {t}: bad dataSize={dsize}')
                bad = True
                break
            if d[pos:pos + 4] != b'RLTD':
                out['ok'] = False
                out['errors'].append(f'tileset #{len(sets)+1} tile {t}: bad DTLR magic')
                bad = True
                break
            pos += dsize + 8
        sets.append(s)
        if bad:
            break
    out['sets'] = sets
    out['n_sets'] = len(sets)
    out['end_pos'] = pos
    if out['ok']:
        if len(sets) != N_SETS:
            out['ok'] = False
            out['errors'].append(f'{len(sets)} tilesets, engine requires {N_SETS}')
        if pos != len(d):
            out['ok'] = False
            out['errors'].append(f'trailing {len(d)-pos} bytes after last tileset')
    return out


def audit(arc_path):
    arc = ArcArchive.from_file(arc_path)
    world = [e for e in arc.entries if e.entry_type == 3][0]
    data = arc.decompress(world)
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])

    guid2name, guid2idx = {}, {}
    for i, lv in enumerate(levels):
        g = lv['ints_raw'][36:52].hex()
        guid2name[g] = basename(lv['fname'])
        guid2idx[g] = i

    rows = []
    for i, lv in enumerate(levels):
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        try:
            secs, _ = parse_blob_sections(blob)
        except Exception as e:                                     # noqa: BLE001
            rows.append({'idx': i, 'name': basename(lv['fname']), 'parse_error': str(e)})
            continue
        sec_0b = next((s['data'] for s in secs if s['type'] == 0x0b), None)
        has_0a = any(s['type'] == 0x0a for s in secs)
        own = lv['ints_raw'][36:52].hex()
        ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
        row = {'idx': i, 'name': basename(lv['fname']), 'fname': lv['fname'],
               'own_guid': own, 'grid_corner': list(ints[6:9]),
               'tile_dims': list(ints[0:6]), 'has_0a': has_0a,
               'has_0b': sec_0b is not None}
        if sec_0b is not None:
            c = decode_container(sec_0b)
            row['c'] = c
            gs = c.get('guids', [])
            row['guid_names'] = [guid2name.get(g, 'UNRESOLVED:' + g[:8]) for g in gs]
            row['n_unresolved'] = sum(1 for g in gs if g not in guid2name)
            row['n_distinct'] = len(set(gs))
            row['own_in_list'] = own in gs
            row['degenerate'] = len(gs) > 1 and len(set(gs)) == 1
            row['own_only'] = len(gs) == 1 and gs[0] == own
            row['struct_ok'] = c['ok']
        rows.append(row)
    return {'arc': str(arc_path), 'levels': len(levels), 'rows': rows,
            'guid2name': guid2name, 'guid2idx': guid2idx}


def report(res):
    rows = res['rows']
    print(f"\n===== {res['arc']}  ({res['levels']} levels) =====")
    no0b = [r for r in rows if not r.get('has_0b') and 'parse_error' not in r]
    bad_struct = [r for r in rows if r.get('has_0b') and not r.get('struct_ok', True)]
    degen = [r for r in rows if r.get('degenerate')]
    ownonly = [r for r in rows if r.get('own_only')]
    unres = [r for r in rows if r.get('n_unresolved', 0)]
    still0a = [r for r in rows if r.get('has_0a')]
    print(f"  levels with 0x0b            : {sum(1 for r in rows if r.get('has_0b'))}")
    print(f"  levels WITHOUT 0x0b         : {len(no0b)}")
    print(f"  levels still carrying 0x0a  : {len(still0a)}")
    print(f"  STRUCTURALLY INVALID 0x0b   : {len(bad_struct)}")
    print(f"  DEGENERATE guid list (>1 entry, all identical): {len(degen)}")
    print(f"  own-only guid list (exactly 1 entry == own)   : {len(ownonly)}")
    print(f"  lists with UNRESOLVABLE guids                 : {len(unres)}")
    for label, group in (('STRUCTURALLY INVALID', bad_struct), ('DEGENERATE', degen),
                         ('OWN-ONLY', ownonly), ('UNRESOLVED-GUIDS', unres)):
        if not group:
            continue
        print(f"\n  --- {label} ({len(group)}) ---")
        for r in sorted(group, key=lambda x: x['idx']):
            c = r.get('c', {})
            print(f"    [{r['idx']:4d}] {r['name']:38s} size={c.get('size')} "
                  f"gc={c.get('guid_count')} sets={c.get('n_sets')} "
                  f"names={r.get('guid_names')} err={c.get('errors')}")
    return {'no0b': len(no0b), 'bad_struct': len(bad_struct), 'degen': len(degen),
            'ownonly': len(ownonly), 'unres': len(unres), 'still0a': len(still0a)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('arcs', nargs='+')
    ap.add_argument('--json')
    args = ap.parse_args()
    allres = []
    for a in args.arcs:
        res = audit(Path(a))
        report(res)
        allres.append(res)
    if args.json:
        Path(args.json).write_text(json.dumps(allres, indent=1), encoding='utf-8')
        print(f'\nwrote {args.json}')


if __name__ == '__main__':
    main()
