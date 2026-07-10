"""build32 parse-back gate: M8 (farmland06d v11) + M9 (random05a v0e FIRST LIVE v0e-branch use).

Asserts, against a freshly built map arc:
  M9 random05a (v0x0e):
    - 0x05 instance count == 60 (was 59)
    - the appended instance references q_vashkarr_lone.dbr at local (24.00,1.00,31.70)
    - blob re-parses flag-aware to the EXACT 0x05 stream end (no desync)
    - blob section walk reaches the exact blob end (no trailing garbage)
    - spot is on the level's own 0x0b navmesh (container present, cell walkable per
      the same simple bbox check used at survey time is NOT re-run here; we assert the
      0x0b section survived byte-identical instead - the spec was navmesh-verified at
      survey time and injection never touches 0x0b)
  M8 farmland06d (v0x11):
    - 0x05 instance count == 996 (was 995)
    - the appended instance references portal_master_helos.dbr at local (76.50,0.60,189.50)
    - 0x14 entry count UNCHANGED (NPC spec appends no 0x14)

Usage: py tools/debug/gate_build32_parseback.py [--map local/Levels_merged.arc] [--baseline local/Levels_merged.build31g-baseline.arc]
"""
import argparse
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

import importlib
vg = importlib.import_module('verify_groups_bindings')
ArcArchive = vg.ArcArchive
parse_sections = vg.parse_sections
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS

BS = chr(92)

FAIL = []


def check(name, cond, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'  [{tag}] {name}' + (f'  ({detail})' if detail else ''))
    if not cond:
        FAIL.append(name)


def load_world(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    return data, levels


def get_blob(data, levels, suffix):
    for lv in levels:
        k = lv['fname'].replace(BS, '/').lower()
        if k.endswith(suffix):
            return lv, data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    raise SystemExit(f'level {suffix} not found')


def walk_0x05(sd, base):
    """Walk the 0x05 payload flag-aware. Returns (strings, [instances], end_pos_exact)."""
    pos = 0
    nstr = struct.unpack_from('<I', sd, pos)[0]; pos += 4
    strings = []
    for _ in range(nstr):
        ln = struct.unpack_from('<I', sd, pos)[0]; pos += 4
        strings.append(sd[pos:pos + ln]); pos += ln
    ninst = struct.unpack_from('<I', sd, pos)[0]; pos += 4
    insts = []
    for _ in range(ninst):
        rec = sd[pos:pos + base]
        sid = struct.unpack_from('<I', rec, 0)[0]
        # measured layout (_build_0x05_record): str_idx(4) + rot 3x3(36) + position(12) + flags(4)
        x, y, z = struct.unpack_from('<fff', rec, 40)
        flags = struct.unpack_from('<I', rec, 52)[0]
        sz = base + (16 if flags != 0 else 0)
        if base == 72:
            # v11 flagged records ALSO carry a 16B zero pad after the UniqueId
            # (v0e->v11 conversion rule); SHARED v11/v0f levels use base-72 + 16 if flagged
            # (no extra pad) per the audit parser. base=72 handled by caller choice.
            pass
        insts.append({'sid': sid, 'dbr': strings[sid] if sid < len(strings) else b'?',
                      'pos': (x, y, z), 'flags': flags})
        pos += sz
    return strings, insts, pos, ninst


def section_sizes(blob):
    return {t: len(d) for t, d in parse_blob_sections(blob)}


def blob_walk_exact(blob):
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            return False, pos
        pos += 8 + ss
    return pos == len(blob), pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    ap.add_argument('--baseline', default=str(REPO / 'local' / 'Levels_merged.build31g-baseline.arc'))
    ap.add_argument('--testhub', action='store_true',
                    help='expect the TESTHUB variant (same M8/M9 assertions; farmland/random05a '
                         'counts are hub-independent)')
    args = ap.parse_args()

    print(f'=== GATE build32 parse-back: {args.map} ===')
    data, levels = load_world(args.map)
    bdata, blevels = load_world(args.baseline)

    # ---------------- M9: random05a (v0x0e) ----------------
    print('--- M9 random05a (v0x0e, FIRST LIVE v0e-branch use) ---')
    lv, blob = get_blob(data, levels, 'orient/underground/random05a.lvl')
    blv, bblob = get_blob(bdata, blevels, 'orient/underground/random05a.lvl')
    check('blob version v0x0e', blob[3] == 0x0e, f'v0x{blob[3]:02x}')
    ok, end = blob_walk_exact(blob)
    check('blob section walk reaches exact blob end', ok, f'end={end} len={len(blob)}')

    secs = dict(parse_blob_sections(blob))
    bsecs = dict(parse_blob_sections(bblob))
    sd = secs[0x05]
    strings, insts, endpos, ninst = walk_0x05(sd, 56)
    check('0x05 instance count 59 -> 60', ninst == 60, f'count={ninst}')
    check('0x05 flag-aware walk lands at exact section end', endpos == len(sd),
          f'end={endpos} len={len(sd)}')
    last = insts[-1]
    check('appended instance is q_vashkarr_lone.dbr',
          last['dbr'].lower() == b'records' + BS.encode() + b'drxmap' + BS.encode() + b'proxy'
          + BS.encode() + b'q_vashkarr_lone.dbr',
          last['dbr'].decode('latin-1'))
    check('appended instance at local (24.00,1.00,31.70)',
          abs(last['pos'][0] - 24.0) < 1e-4 and abs(last['pos'][1] - 1.0) < 1e-4
          and abs(last['pos'][2] - 31.7) < 1e-4, str(last['pos']))
    check('appended instance flags == 0 (proxy byte-shape)', last['flags'] == 0,
          f"flags={last['flags']}")
    # collateral: every OTHER section byte-identical to baseline
    for t in sorted(set(bsecs) | set(secs)):
        if t == 0x05:
            continue
        check(f'section 0x{t:02x} byte-identical to baseline',
              secs.get(t) == bsecs.get(t),
              f'{len(bsecs.get(t, b""))} -> {len(secs.get(t, b""))} bytes')
    # baseline instances 0..58 byte-stable (prefix of 0x05 unchanged up to the count field)
    bsd = bsecs[0x05]
    _, binsts, bend, bninst = walk_0x05(bsd, 56)
    check('baseline instance count was 59', bninst == 59, f'count={bninst}')
    same = all(insts[i]['dbr'] == binsts[i]['dbr'] and insts[i]['pos'] == binsts[i]['pos']
               for i in range(bninst))
    check('all 59 pre-existing instances unchanged (dbr+pos)', same)
    check('0x0b navmesh section survived byte-identical', secs.get(0x0b) == bsecs.get(0x0b),
          f'{len(bsecs.get(0x0b, b""))} bytes')
    check('no stale 0x0a alongside 0x0b', 0x0a not in secs or 0x0b not in secs)

    # ---------------- M8: startingfarmland06d (v0x11) ----------------
    print('--- M8 startingfarmland06d (v0x11) ---')
    lv, blob = get_blob(data, levels, 'startingtownver2/startingfarmland06d.lvl')
    blv, bblob = get_blob(bdata, blevels, 'startingtownver2/startingfarmland06d.lvl')
    check('blob version v0x11', blob[3] == 0x11, f'v0x{blob[3]:02x}')
    ok, end = blob_walk_exact(blob)
    check('blob section walk reaches exact blob end', ok, f'end={end} len={len(blob)}')
    secs = dict(parse_blob_sections(blob))
    bsecs = dict(parse_blob_sections(bblob))
    sd = secs[0x05]
    strings, insts, endpos, ninst = walk_0x05(sd, 72)
    check('0x05 instance count 995 -> 996', ninst == 996, f'count={ninst}')
    check('0x05 flag-aware walk lands at exact section end', endpos == len(sd),
          f'end={endpos} len={len(sd)}')
    last = insts[-1]
    check('appended instance is portal_master_helos.dbr',
          last['dbr'].lower() == b'records' + BS.encode() + b'quests' + BS.encode()
          + b'portal_master_helos.dbr', last['dbr'].decode('latin-1'))
    check('appended instance at local (76.50,0.60,189.50)',
          abs(last['pos'][0] - 76.5) < 1e-4 and abs(last['pos'][1] - 0.6) < 1e-4
          and abs(last['pos'][2] - 189.5) < 1e-4, str(last['pos']))
    check('appended instance flags == 0 (NPC byte-shape, no UniqueId)', last['flags'] == 0,
          f"flags={last['flags']}")
    # 0x14 must be UNCHANGED (NPC appends no 0x14)
    check('0x14 section byte-identical to baseline (no 0x14 for the NPC)',
          secs.get(0x14) == bsecs.get(0x14),
          f'{len(bsecs.get(0x14, b""))} -> {len(secs.get(0x14, b""))} bytes')
    _, binsts, _, bninst = walk_0x05(bsecs[0x05], 72)
    check('baseline instance count was 995', bninst == 995, f'count={bninst}')
    same = all(insts[i]['dbr'] == binsts[i]['dbr'] and insts[i]['pos'] == binsts[i]['pos']
               for i in range(bninst))
    check('all 995 pre-existing instances unchanged (dbr+pos)', same)

    print()
    if FAIL:
        print(f'RESULT: FAIL ({len(FAIL)}): {FAIL}')
        return 1
    print('RESULT: PASS (M8 + M9 parse-back clean)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
