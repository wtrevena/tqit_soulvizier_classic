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
    ap.add_argument('--m10-baseline',
                    default=str(REPO / 'local' / 'Levels_merged.build32a-baseline.arc'),
                    help='baseline for the M10 tombobs checks (the pre-M10 build32a map)')
    ap.add_argument('--skip-m10', action='store_true',
                    help='skip the M10 tombobs checks (to gate a pre-M10 build)')
    ap.add_argument('--testhub', action='store_true',
                    help='expect the TESTHUB variant (same M8/M9 assertions; farmland/random05a '
                         'counts are hub-independent) PLUS the MYARD HiddenValley01 monster-yard '
                         'checks (8 TESTHUB-only proxy placements)')
    ap.add_argument('--yard-baseline', default=str(REPO / 'local' / 'Levels_merged.arc'),
                    help='canonical map (no yard) baseline for the TESTHUB HV01 yard collateral')
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
    # canonical appends only Almyros (portal_master_helos) at [995] -> count 996. The build34
    # TESTHUB rig ALSO appends svc_testhub_master AFTER Almyros -> Almyros at [995], hub master at
    # [996] -> count 997. Both are flags=0 NPCs (no 0x14).
    exp_count = 997 if args.testhub else 996
    check(f'0x05 instance count 995 -> {exp_count}', ninst == exp_count, f'count={ninst}')
    check('0x05 flag-aware walk lands at exact section end', endpos == len(sd),
          f'end={endpos} len={len(sd)}')
    helos = insts[995]
    check('instance[995] is portal_master_helos.dbr (Almyros)',
          helos['dbr'].lower() == b'records' + BS.encode() + b'quests' + BS.encode()
          + b'portal_master_helos.dbr', helos['dbr'].decode('latin-1'))
    check('Almyros at local (76.50,0.60,189.50)',
          abs(helos['pos'][0] - 76.5) < 1e-4 and abs(helos['pos'][1] - 0.6) < 1e-4
          and abs(helos['pos'][2] - 189.5) < 1e-4, str(helos['pos']))
    check('Almyros flags == 0 (NPC byte-shape, no UniqueId)', helos['flags'] == 0,
          f"flags={helos['flags']}")
    if args.testhub:
        master = insts[996]
        check('instance[996] is svc_testhub_master.dbr (rig hub master)',
              master['dbr'].lower() == b'records' + BS.encode() + b'quests' + BS.encode()
              + b'svc_testhub_master.dbr', master['dbr'].decode('latin-1'))
        check('rig hub master at local (79.50,0.80,189.50)',
              abs(master['pos'][0] - 79.5) < 1e-4 and abs(master['pos'][1] - 0.8) < 1e-4
              and abs(master['pos'][2] - 189.5) < 1e-4, str(master['pos']))
        check('rig hub master flags == 0', master['flags'] == 0, f"flags={master['flags']}")
    # 0x14 must be UNCHANGED (NPC appends no 0x14)
    check('0x14 section byte-identical to baseline (no 0x14 for the NPC)',
          secs.get(0x14) == bsecs.get(0x14),
          f'{len(bsecs.get(0x14, b""))} -> {len(secs.get(0x14, b""))} bytes')
    _, binsts, _, bninst = walk_0x05(bsecs[0x05], 72)
    check('baseline instance count was 995', bninst == 995, f'count={bninst}')
    same = all(insts[i]['dbr'] == binsts[i]['dbr'] and insts[i]['pos'] == binsts[i]['pos']
               for i in range(bninst))
    check('all 995 pre-existing instances unchanged (dbr+pos)', same)

    # ---------------- M10: tombobs01/02 Obsidian roulette corners (v0x0e) ----------------
    if not args.skip_m10:
        mdata, mlevels = load_world(args.m10_baseline)
        # tombobs02 carries the 2 roulette corners (build32b) AND, since build35, the 7
        # Broodmother Nest proxies APPENDED after them (mother + 6 eggs, Y=1.2). tombobs01
        # carries only the 2 roulette corners. The M10 baseline (build32a) predates BOTH, so
        # the tombobs02 delta vs build32a is +9 and tombobs01 is +2. The nest proxies are
        # canonical, so this holds identically for the canonical AND TESTHUB variants.
        M10 = {
            'orient/typhonug/tombobs02.lvl': [
                (b'q_obs_roulette_a.dbr', (50.4, 1.0, 143.6)),
                (b'q_obs_roulette_c.dbr', (200.4, 1.0, 97.6)),
                (b'q_broodmother_lone.dbr', (184.0, 1.2, 192.0)),
                (b'q_broodnest_egg_a.dbr', (184.0, 1.2, 202.0)),
                (b'q_broodnest_egg_b.dbr', (175.3, 1.2, 197.0)),
                (b'q_broodnest_egg_c.dbr', (175.3, 1.2, 187.0)),
                (b'q_broodnest_egg_d.dbr', (184.0, 1.2, 182.0)),
                (b'q_broodnest_egg_e.dbr', (192.7, 1.2, 187.0)),
                (b'q_broodnest_egg_f.dbr', (192.7, 1.2, 197.0)),
            ],
            'orient/typhonug/tombobs01.lvl': [
                (b'q_obs_roulette_b.dbr', (220.8, 1.0, 89.6)),
                (b'q_obs_roulette_d.dbr', (92.8, 1.0, 47.6)),
            ],
        }
        for suffix, expect in M10.items():
            print(f'--- M10 {suffix} (v0x0e branch) ---')
            lv, blob = get_blob(data, levels, suffix)
            blv, bblob = get_blob(mdata, mlevels, suffix)
            check('blob version v0x0e', blob[3] == 0x0e, f'v0x{blob[3]:02x}')
            ok, end = blob_walk_exact(blob)
            check('blob section walk reaches exact blob end', ok, f'end={end} len={len(blob)}')
            secs = dict(parse_blob_sections(blob))
            bsecs = dict(parse_blob_sections(bblob))
            sd = secs[0x05]
            strings, insts, endpos, ninst = walk_0x05(sd, 56)
            _, binsts, _, bninst = walk_0x05(bsecs[0x05], 56)
            check(f'0x05 instance count {bninst} -> {bninst + len(expect)}',
                  ninst == bninst + len(expect), f'count={ninst}')
            check('0x05 flag-aware walk lands at exact section end', endpos == len(sd),
                  f'end={endpos} len={len(sd)}')
            for k, (base, pos3) in enumerate(expect):
                inst = insts[bninst + k]
                check(f'appended[{k}] is {base.decode()}',
                      inst['dbr'].lower().endswith(BS.encode() + base),
                      inst['dbr'].decode('latin-1'))
                check(f'appended[{k}] at local {pos3}',
                      all(abs(inst['pos'][i] - pos3[i]) < 1e-3 for i in range(3)),
                      str(inst['pos']))
                check(f'appended[{k}] flags == 0 (proxy byte-shape)', inst['flags'] == 0,
                      f"flags={inst['flags']}")
            for t in sorted(set(bsecs) | set(secs)):
                if t == 0x05:
                    continue
                check(f'section 0x{t:02x} byte-identical to M10 baseline',
                      secs.get(t) == bsecs.get(t),
                      f'{len(bsecs.get(t, b""))} -> {len(secs.get(t, b""))} bytes')
            same = all(insts[i]['dbr'] == binsts[i]['dbr'] and insts[i]['pos'] == binsts[i]['pos']
                       for i in range(bninst))
            check(f'all {bninst} pre-existing instances unchanged (dbr+pos)', same)
            check('0x0b navmesh section survived byte-identical',
                  secs.get(0x0b) == bsecs.get(0x0b), f'{len(bsecs.get(0x0b, b""))} bytes')

    # ---------------- MYARD: HiddenValley01 monster test yard (TESTHUB-only, v0x11) ------------
    # The yard is 8 proxy placements appended to HV01 ONLY in the TESTHUB build (build_hub_extra_
    # specs). Baseline = the canonical map (no yard); TESTHUB HV01 must equal canonical HV01 plus
    # exactly these 8 appended flags=0 instances, with every other section (incl. 0x0b navmesh)
    # byte-identical (append-only -> the byte-identity + hub-identity guarantees hold).
    if args.testhub:
        ydata, ylevels = load_world(args.yard_baseline)
        print('--- MYARD HiddenValley01 (v0x11, TESTHUB-only monster yard) ---')
        lv, blob = get_blob(data, levels, 'orient/silkroad/hiddenvalley01.lvl')
        blv, bblob = get_blob(ydata, ylevels, 'orient/silkroad/hiddenvalley01.lvl')
        check('blob version v0x11', blob[3] == 0x11, f'v0x{blob[3]:02x}')
        ok, end = blob_walk_exact(blob)
        check('blob section walk reaches exact blob end', ok, f'end={end} len={len(blob)}')
        secs = dict(parse_blob_sections(blob))
        bsecs = dict(parse_blob_sections(bblob))
        sd = secs[0x05]
        strings, insts, endpos, ninst = walk_0x05(sd, 72)
        _, binsts, _, bninst = walk_0x05(bsecs[0x05], 72)
        # build35: the yard grew from 8 to 9 with the broodmother apex (q_yard_broodmother).
        check(f'0x05 instance count {bninst} -> {bninst + 9}', ninst == bninst + 9, f'count={ninst}')
        check('0x05 flag-aware walk lands at exact section end', endpos == len(sd),
              f'end={endpos} len={len(sd)}')
        YARD = [
            (b'q_yard_enslaver.dbr',      (23.0, 17.0, 33.0)),
            (b'q_yard_marauders.dbr',     (31.9, 16.2, 26.9)),
            (b'q_vashkarr_lone.dbr',      (36.0, 16.0, 28.5)),
            (b'q_yard_obs_sarkoth.dbr',   (42.0, 15.2, 91.0)),
            (b'q_yard_obs_gorrahk.dbr',   (36.0, 15.2, 90.0)),
            (b'q_yard_obs_voranthys.dbr', (47.0, 15.4, 87.0)),
            (b'q_yard_obs_ilsevar.dbr',   (47.0, 15.2, 95.0)),
            (b'q_yard_wyrm.dbr',          (30.0, 15.2, 113.0)),
            (b'q_yard_broodmother.dbr',   (89.0,  6.6, 100.0)),
        ]
        for k, (bname, pos3) in enumerate(YARD):
            inst = insts[bninst + k]
            check(f'yard[{k}] is {bname.decode()}',
                  inst['dbr'].lower().endswith(BS.encode() + bname), inst['dbr'].decode('latin-1'))
            check(f'yard[{k}] at local {pos3}',
                  all(abs(inst['pos'][i] - pos3[i]) < 1e-3 for i in range(3)), str(inst['pos']))
            check(f'yard[{k}] flags == 0 (proxy byte-shape)', inst['flags'] == 0,
                  f"flags={inst['flags']}")
        for t in sorted(set(bsecs) | set(secs)):
            if t == 0x05:
                continue
            check(f'section 0x{t:02x} byte-identical to canonical HV01',
                  secs.get(t) == bsecs.get(t),
                  f'{len(bsecs.get(t, b""))} -> {len(secs.get(t, b""))} bytes')
        same = all(insts[i]['dbr'] == binsts[i]['dbr'] and insts[i]['pos'] == binsts[i]['pos']
                   for i in range(bninst))
        check(f'all {bninst} pre-existing HV01 instances unchanged (dbr+pos)', same)
        check('0x0b navmesh section survived byte-identical', secs.get(0x0b) == bsecs.get(0x0b),
              f'{len(bsecs.get(0x0b, b""))} bytes')
        check('no stale 0x0a alongside 0x0b', 0x0a not in secs or 0x0b not in secs)

    # ---------------- RIG: portal test rig (build34, TESTHUB-only, Model C boat-dialog NPCs) ------
    # The Model C rig appends ONE flags=0 NPC to each of 6 hosts (the Helos hub master is checked by
    # the M8 block above). Each TESTHUB host must equal its CANONICAL blob (yard_baseline) PLUS
    # exactly that one appended NPC, with every OTHER section (incl the 0x0b navmesh, and the 0x06/
    # 0x14 sections that the Uber/Sparta native-door patches touch) BYTE-IDENTICAL. random09a is the
    # decisive one: retiring the GridEntrance hub reverts TESTHUB random09a to the canonical SV
    # blood-cave swap blob, so its 0x0b/0x06/0x17 must now match canonical exactly.
    if args.testhub:
        cdata, clevels = load_world(args.yard_baseline)
        print('--- RIG portal test rig (TESTHUB = canonical + 1 appended NPC per host) ---')
        RIG = [
            ('orient/underground/random09a.lvl',   56, b'svc_testhub_master.dbr', (32.0, 1.0, 45.0)),
            ('olympus/gardenofmerchants.lvl',      56, b'svc_testhub_return.dbr', (133.0, -39.0, 73.0)),
            ('secret_place/darkforestenter.lvl',   56, b'svc_testhub_return.dbr', (27.0, 1.0, 30.0)),
            ('uberdungeon/crypt_floor1.lvl',       56, b'svc_testhub_return.dbr', (140.0, 10.0, 229.0)),
            ('minidungeons/spartacryptlevel2.lvl', 56, b'svc_testhub_return.dbr', (45.0, -1.6, 42.0)),
            ('bossarena/boss_arena.lvl',           56, b'svc_testhub_return.dbr', (131.0, 0.0, 40.0)),
        ]
        for suffix, base, bname, pos3 in RIG:
            print(f'--- RIG {suffix} ---')
            lv, blob = get_blob(data, levels, suffix)
            clv, cblob = get_blob(cdata, clevels, suffix)
            ok, end = blob_walk_exact(blob)
            check(f'{suffix}: blob walk reaches exact end', ok, f'end={end} len={len(blob)}')
            secs = dict(parse_blob_sections(blob))
            csecs = dict(parse_blob_sections(cblob))
            _, insts, endpos, ninst = walk_0x05(secs[0x05], base)
            _, cinsts, _, cninst = walk_0x05(csecs[0x05], base)
            check(f'{suffix}: 0x05 count {cninst} -> {cninst + 1}', ninst == cninst + 1,
                  f'count={ninst}')
            check(f'{suffix}: 0x05 walk lands at exact section end', endpos == len(secs[0x05]),
                  f'end={endpos} len={len(secs[0x05])}')
            last = insts[-1]
            check(f'{suffix}: appended is {bname.decode()}',
                  last['dbr'].lower().endswith(BS.encode() + bname), last['dbr'].decode('latin-1'))
            check(f'{suffix}: appended at local {pos3}',
                  all(abs(last['pos'][i] - pos3[i]) < 1e-3 for i in range(3)), str(last['pos']))
            check(f'{suffix}: appended flags == 0 (NPC byte-shape)', last['flags'] == 0,
                  f"flags={last['flags']}")
            same = all(insts[i]['dbr'] == cinsts[i]['dbr'] and insts[i]['pos'] == cinsts[i]['pos']
                       for i in range(cninst))
            check(f'{suffix}: all {cninst} canonical instances unchanged (dbr+pos)', same)
            for t in sorted(set(csecs) | set(secs)):
                if t == 0x05:
                    continue
                check(f'{suffix}: section 0x{t:02x} byte-identical to canonical',
                      secs.get(t) == csecs.get(t),
                      f'{len(csecs.get(t, b""))} -> {len(secs.get(t, b""))} bytes')

    print()
    if FAIL:
        print(f'RESULT: FAIL ({len(FAIL)}): {FAIL}')
        return 1
    scope = 'M8 + M9' if args.skip_m10 else 'M8 + M9 + M10'
    if args.testhub:
        scope += ' + MYARD + RIG'
    print(f'RESULT: PASS ({scope} parse-back clean)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
