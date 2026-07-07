#!/usr/bin/env python3
"""Gate helper for the Hemorrheus (Blood Toxeus) 0x05 entity injection.

Usage:
  bloodtoxeus_gates.py snapshot <merged.arc> <out.json>   # capture per-blob hashes + secretdoor state
  bloodtoxeus_gates.py compare  <baseline.json> <after.arc>  # S3/S5 collateral + regression diff

Compares two merged Levels.arc maps at the level-blob granularity so we can
prove ONLY new_secretdoor_transitionhallway changed, and only its 0x05 (plus
0x14 if the exemplar demands it). Everything else must be byte-identical.
"""
import sys, struct, json, hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections, count_0x05_instances

TARGET = 'new_secretdoor_transitionhallway'


def load_map(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    smap = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, smap[SEC_LEVELS])
    return data, levels


def blob_of(data, lv):
    return data[lv['data_offset']:lv['data_offset'] + lv['data_length']]


def section_hashes(blob):
    """Return {sec_type: sha256} for every internal section of a level blob."""
    secs, magic = parse_blob_sections(blob)
    out = {'_magic': magic.hex()}
    for s in secs:
        out['0x%02x' % s['type']] = hashlib.sha256(s['data']).hexdigest()
    return out


def snapshot(arc_path, out_path):
    data, levels = load_map(arc_path)
    entries = {}
    for i, lv in enumerate(levels):
        key = lv['fname'].replace('\\', '/').lower()
        blob = blob_of(data, lv)
        rec = {
            'idx': i,
            'len': len(blob),
            'sha': hashlib.sha256(blob).hexdigest(),
        }
        if TARGET in key:
            rec['sections'] = section_hashes(blob)
            secs, _ = parse_blob_sections(blob)
            s05 = [s for s in secs if s['type'] == 0x05]
            s14 = [s for s in secs if s['type'] == 0x14]
            s0b = [s for s in secs if s['type'] == 0x0b]
            rec['n_0x05'] = count_0x05_instances(s05[0]['data']) if s05 else 0
            rec['n_0x14'] = _count_0x14(s14[0]['data']) if s14 else 0
            rec['len_0x0b'] = len(s0b[0]['data']) if s0b else 0
        # collisions: multiple levels can share a name key; store as list
        entries.setdefault(key, []).append(rec)
    payload = {'arc': str(arc_path), 'n_levels': len(levels), 'entries': entries}
    Path(out_path).write_text(json.dumps(payload, indent=1))
    print('snapshot: %d levels -> %s' % (len(levels), out_path))
    # echo the target
    for key, recs in entries.items():
        if TARGET in key:
            for r in recs:
                print('  TARGET %s idx=%d len=%d n_0x05=%s n_0x14=%s len_0x0b=%s'
                      % (key, r['idx'], r['len'], r.get('n_0x05'), r.get('n_0x14'),
                         r.get('len_0x0b')))


def _count_0x14(sec14):
    pos = 0
    n = 0
    while pos + 8 <= len(sec14):
        psize = struct.unpack_from('<I', sec14, pos + 4)[0]
        pos += 8 + psize
        n += 1
    return n


def compare(baseline_json, after_arc):
    base = json.loads(Path(baseline_json).read_text())
    data, levels = load_map(after_arc)
    after = {}
    for i, lv in enumerate(levels):
        key = lv['fname'].replace('\\', '/').lower()
        blob = blob_of(data, lv)
        rec = {'idx': i, 'len': len(blob), 'sha': hashlib.sha256(blob).hexdigest()}
        if TARGET in key:
            rec['sections'] = section_hashes(blob)
            secs, _ = parse_blob_sections(blob)
            s05 = [s for s in secs if s['type'] == 0x05]
            s14 = [s for s in secs if s['type'] == 0x14]
            s0b = [s for s in secs if s['type'] == 0x0b]
            rec['n_0x05'] = count_0x05_instances(s05[0]['data']) if s05 else 0
            rec['n_0x14'] = _count_0x14(s14[0]['data']) if s14 else 0
            rec['len_0x0b'] = len(s0b[0]['data']) if s0b else 0
        after.setdefault(key, []).append(rec)

    bmap = base['entries']
    print('=== S3/S5 COLLATERAL + REGRESSION DIFF ===')
    print('baseline levels: %d   after levels: %d' % (base['n_levels'], len(levels)))
    if base['n_levels'] != len(levels):
        print('  !! LEVEL COUNT CHANGED')

    changed = []
    all_keys = set(bmap) | set(after)
    for key in sorted(all_keys):
        brecs = bmap.get(key, [])
        arecs = after.get(key, [])
        if len(brecs) != len(arecs):
            changed.append((key, 'count %d->%d' % (len(brecs), len(arecs))))
            continue
        for b, a in zip(brecs, arecs):
            if b['sha'] != a['sha']:
                changed.append((key, 'sha differs (len %d->%d)' % (b['len'], a['len'])))

    target_keys = [k for k in all_keys if TARGET in k]
    non_target_changed = [c for c in changed if TARGET not in c[0]]

    print('\nBlobs changed (total): %d' % len(changed))
    print('Non-target blobs changed: %d  (MUST be 0 for S3)' % len(non_target_changed))
    for key, why in non_target_changed[:20]:
        print('  CHANGED(collateral!): %s  %s' % (key, why))

    print('\n=== TARGET (%s) section-level diff ===' % TARGET)
    for key in target_keys:
        b = bmap[key][0]
        a = after[key][0]
        print('  %s' % key)
        print('    blob len %d -> %d   (n_0x05 %s->%s, n_0x14 %s->%s, len_0x0b %s->%s)'
              % (b['len'], a['len'], b.get('n_0x05'), a.get('n_0x05'),
                 b.get('n_0x14'), a.get('n_0x14'), b.get('len_0x0b'), a.get('len_0x0b')))
        bs = b.get('sections', {})
        as_ = a.get('sections', {})
        for st in sorted(set(bs) | set(as_)):
            bh = bs.get(st, '(absent)')
            ah = as_.get(st, '(absent)')
            mark = 'SAME' if bh == ah else 'CHANGED'
            print('      %-8s %s' % (st, mark))

    ok_s3 = len(non_target_changed) == 0
    print('\nS3 no-collateral (only target changed): %s' % ('PASS' if ok_s3 else 'FAIL'))
    return ok_s3


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'snapshot':
        snapshot(sys.argv[2], sys.argv[3])
    elif cmd == 'compare':
        ok = compare(sys.argv[2], sys.argv[3])
        sys.exit(0 if ok else 1)
    else:
        print('unknown cmd', cmd)
        sys.exit(2)
