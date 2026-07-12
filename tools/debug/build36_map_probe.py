"""build36 MAP WAVE probe (round 3): level-blob diff + TESTHUB yard count/spacing.

Read-only. Reuses the repo's proven parsers (svaera_plus_portals.parse_sections /
parse_level_index + build_section_surgery.parse_blob_sections). Not a build input.

Usage:
  py tools/debug/build36_map_probe.py diff  <build36.arc> <build35_baseline.arc>
  py tools/debug/build36_map_probe.py yard  <TESTHUB.arc>
"""
import sys
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
from arc_patcher import ArcArchive  # noqa
from merge_levels_binary import parse_sections  # noqa
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS  # noqa

BS = '\\'


def load_blobs(path):
    """Return {fname_lower: (fname, blob_bytes)} for every level in the map."""
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    out = {}
    for lv in levels:
        fn = lv['fname']
        out[fn.replace(BS, '/').lower()] = (fn, data[lv['data_offset']:lv['data_offset'] + lv['data_length']])
    return out


def sec_map(blob):
    return {t: d for t, d in parse_blob_sections(blob)}


def count_0x05(blob):
    for t, d in parse_blob_sections(blob):
        if t == 0x05:
            nstr = struct.unpack_from('<I', d, 0)[0]
            pos = 4
            for _ in range(nstr):
                ln = struct.unpack_from('<I', d, pos)[0]
                pos += 4 + ln
            return struct.unpack_from('<I', d, pos)[0]
    return 0


def instances(blob):
    """[(dbr_str, x, y, z, flags)] for the level's 0x05 instances (base per LVL version)."""
    ver = blob[3] if blob[:3] == b'LVL' else 0x11
    base = 56 if ver == 0x0e else 72
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
        out = []
        for _ in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            x, y, z = struct.unpack_from('<fff', d, pos + 40)
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            out.append((strings[sid] if sid < len(strings) else b'?', x, y, z, flags))
            pos += base + (16 if flags != 0 else 0)
        return out
    return []


def cmd_diff(build36, build35):
    a = load_blobs(build36)   # build36
    b = load_blobs(build35)   # build35 baseline
    ka, kb = set(a), set(b)
    added = sorted(ka - kb)
    removed = sorted(kb - ka)
    print(f'levels: build36={len(a)}  build35={len(b)}  added={len(added)}  removed={len(removed)}')
    if added:
        print('  ADDED levels:', added)
    if removed:
        print('  REMOVED levels:', removed)
    changed = []
    for k in sorted(ka & kb):
        if a[k][1] != b[k][1]:
            changed.append(k)
    print(f'\nCHANGED level blobs: {len(changed)}')
    for k in changed:
        fn36, blob36 = a[k]
        fn35, blob35 = b[k]
        s36, s35 = sec_map(blob36), sec_map(blob35)
        alltypes = sorted(set(s36) | set(s35))
        difftypes = [t for t in alltypes if s36.get(t) != s35.get(t)]
        c36, c35 = count_0x05(blob36), count_0x05(blob35)
        z0b = '0x0b IDENTICAL' if s36.get(0x0b) == s35.get(0x0b) else '0x0b CHANGED!'
        dt = ' '.join(f'0x{t:02x}' for t in difftypes)
        print(f'  {fn36}')
        print(f'     diff sections: [{dt}]   0x05 count {c35}->{c36} (delta {c36 - c35:+d})   {z0b}')
    return changed


def cmd_yard(testhub):
    a = load_blobs(testhub)
    hv = None
    for k, v in a.items():
        if k.endswith('orient/silkroad/hiddenvalley01.lvl'):
            hv = v
            break
    if not hv:
        raise SystemExit('HV01 not found in TESTHUB')
    fn, blob = hv
    ver = blob[3]
    insts = instances(blob)
    yard = [(dbr.decode('latin1'), x, y, z, fl) for (dbr, x, y, z, fl) in insts
            if b'q_yard_' in dbr.lower() or b'vashkarr' in dbr.lower()]
    print(f'HV01 ({fn}) v0x{ver:02x}: {len(insts)} total 0x05 instances; {len(yard)} yard proxies\n')
    print(f'{"#":>2} {"dbr":<44} {"x":>8} {"y":>8} {"z":>8} flags')
    for i, (dbr, x, y, z, fl) in enumerate(yard):
        base = dbr.split('\\')[-1]
        print(f'{i:>2} {base:<44} {x:>8.2f} {y:>8.2f} {z:>8.2f} {fl}')
    # min pairwise (x,z)
    mind, mpair = 1e9, None
    for i in range(len(yard)):
        for j in range(i + 1, len(yard)):
            dx = yard[i][1] - yard[j][1]
            dz = yard[i][3] - yard[j][3]
            d = (dx * dx + dz * dz) ** 0.5
            if d < mind:
                mind, mpair = d, (yard[i][0].split('\\')[-1], yard[j][0].split('\\')[-1])
    print(f'\nMIN PAIRWISE (x,z) = {mind:.2f}u  between {mpair[0]} and {mpair[1]}')
    print(f'YARD PROXY COUNT = {len(yard)}')
    return len(yard), mind


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'diff':
        cmd_diff(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == 'yard':
        cmd_yard(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(2)
