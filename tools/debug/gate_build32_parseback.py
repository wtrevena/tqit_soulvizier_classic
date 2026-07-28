"""Map APPEND parse-back gate (historically "build32"; REFRESHED 2026-07-28, BUILD46 debt).

WHAT IT PROVES
Every entity the map build injects into a level's 0x05 section must land as a clean
APPEND: the blob still parses to its exact end, the 0x05 section walks flag-aware to
its exact end at the VERSION-DERIVED stride, the new instances sit at the tail with
flags=0, no pre-existing instance moved, and no other section (navmesh 0x0b included)
changed except where a delta is explicitly declared.

WHY IT WAS REFRESHED (docs/BACKLOG.md "BUILD46 GATE RECORD DEBT")
The build32-era gate froze absolute instance COUNTS and INDICES ("count 995 -> 996",
`insts[995]`). Four builds of legitimate map work later every one of those constants
was wrong, so the gate could not run at all:
  * it died at IMPORT time - it pulled ArcArchive/parse_sections through
    `verify_groups_bindings`, which imports the never-committed `arz_lookup`;
  * M8 farmland06d is now 993 instances, not 996 (b44/b46 removed the two
    portal_olympianarena entities + their aura, and Almyros is at index 992);
  * the MYARD block asserted the HiddenValley01 Monster Test Yard, which b76 REMOVED
    as the chumbi-freeze P0 root cause (docs/reports/b76_chumbi_freeze_rca.md, Will's
    verbatim "the game is frozen" report, R-30/R-31);
  * the RIG block asserted the build34 Model-C rig's exact per-host coords, which the
    traveller hub (svc_helos_trav_* / svc_testhub_return_<area>) superseded.
The frozen constants were the defect: a parse-back gate should assert the SHAPE of an
append, not a snapshot of the world's instance count. So the checks are now DELTA-based
(what changed vs the baseline) and STRUCTURAL (tail, flags, exact-end, collateral), and
the two obsolete blocks are replaced by invariants that still describe live design:
  * MYARD -> INVERTED: TESTHUB HiddenValley01 must be IDENTICAL to canonical, i.e. the
    b76-removed monster yard must never come back (retirement protocol: the yard's
    removal is recorded in the b76 RCA + BACKLOG BUILD46; nothing is deleted here).
  * RIG   -> namespace/shape invariant: every TESTHUB-only host is canonical PLUS
    tail-appended flags=0 instances in the `records\\quests\\svc_` hub namespace, with
    every other section byte-identical. It no longer freezes the hub roster.

Usage:
  py tools/debug/gate_build32_parseback.py [--map local/Levels_merged.arc]
      [--baseline local/Levels_merged.build31g-baseline.arc]
      [--m10-baseline local/Levels_merged.build32a-baseline.arc]
      [--skip-m10] [--testhub --canonical local/Levels_merged.arc]
  py tools/debug/gate_build32_parseback.py --selftest    # planted negative tests
"""
import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

# BUILD46: this used to reach ArcArchive/parse_sections through
# `verify_groups_bindings` - a gate module that itself imports the never-committed
# `arz_lookup`, so THIS gate died at import time with ModuleNotFoundError on any clean
# checkout. Import them from their real homes instead.
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections
from contracts_map import (parse_level_index, parse_blob_sections, blob_0x05_base,
                           SEC_LEVELS)

BS = chr(92)

FAIL = []


def check(name, cond, detail=''):
    tag = 'PASS' if cond else 'FAIL'
    print(f'  [{tag}] {name}' + (f'  ({detail})' if detail else ''))
    if not cond:
        FAIL.append(name)
    return bool(cond)


_WORLDS = {}


def load_world(path):
    path = str(path)
    if path not in _WORLDS:
        arc = ArcArchive.from_file(Path(path))
        data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
        secs = {s['type']: s for s in parse_sections(data)}
        lsec = secs[SEC_LEVELS]
        levels = parse_level_index(
            data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
        _WORLDS[path] = (data, levels)
    return _WORLDS[path]


def get_blob(data, levels, suffix):
    for lv in levels:
        k = lv['fname'].replace(BS, '/').lower()
        if k.endswith(suffix):
            return lv, data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    raise SystemExit(f'level {suffix} not found')


def walk_0x05(sd, base):
    """Walk the 0x05 payload flag-aware at `base`. Returns (strings, insts, end, count).

    `base` MUST come from contracts_map.blob_0x05_base(blob) - 72 for v0x11/v0x0f,
    56 for v0x0e. Passing the wrong one desyncs after the first record (the same
    class of bug as the census_placements hardcoded-72 stride).
    """
    pos = 0
    nstr = struct.unpack_from('<I', sd, pos)[0]; pos += 4
    strings = []
    for _ in range(nstr):
        ln = struct.unpack_from('<I', sd, pos)[0]; pos += 4
        strings.append(sd[pos:pos + ln]); pos += ln
    ninst = struct.unpack_from('<I', sd, pos)[0]; pos += 4
    insts = []
    for _ in range(ninst):
        if pos + base > len(sd):
            break
        sid = struct.unpack_from('<I', sd, pos)[0]
        # measured layout: str_idx(4) + rot 3x3(36) + position(12) + flags(4)
        x, y, z = struct.unpack_from('<fff', sd, pos + 40)
        flags = struct.unpack_from('<I', sd, pos + 52)[0]
        insts.append({'sid': sid, 'dbr': strings[sid] if sid < len(strings) else b'?',
                      'pos': (x, y, z), 'flags': flags})
        pos += base + (16 if flags != 0 else 0)
    return strings, insts, pos, ninst


def blob_walk_exact(blob):
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            return False, pos
        pos += 8 + ss
    return pos == len(blob), pos


def _key(inst):
    return (inst['dbr'].replace(b'/', BS.encode()).lower(),
            tuple(round(v, 3) for v in inst['pos']))


def _fmt(k):
    return f'{k[0].decode("latin-1")} @ {k[1]}'


def compare_level(label, blob, bblob, appended, removed=(), allow_sections=(),
                  require_tail=True):
    """The one delta+shape check every block below uses.

    appended / removed = iterables of (dbr_basename_bytes, (x, y, z)) the build is
    EXPECTED to add / drop vs `bblob`. Anything else in the delta fails.
    """
    base = blob_0x05_base(blob)
    bbase = blob_0x05_base(bblob)
    check(f'{label}: blob version stable v0x{bblob[3]:02x}', blob[3] == bblob[3],
          f'v0x{blob[3]:02x} vs v0x{bblob[3]:02x}')
    ok, end = blob_walk_exact(blob)
    check(f'{label}: blob section walk reaches exact blob end', ok,
          f'end={end} len={len(blob)}')

    secs = dict(parse_blob_sections(blob))
    bsecs = dict(parse_blob_sections(bblob))
    sd = secs[0x05]
    _s, insts, endpos, ninst = walk_0x05(sd, base)
    _bs, binsts, _be, bninst = walk_0x05(bsecs[0x05], bbase)
    check(f'{label}: 0x05 flag-aware walk lands at exact section end (stride {base})',
          endpos == len(sd), f'end={endpos} len={len(sd)}')
    check(f'{label}: every declared instance was walked', len(insts) == ninst,
          f'{len(insts)}/{ninst}')

    cur = Counter(_key(i) for i in insts)
    bas = Counter(_key(i) for i in binsts)
    got_added = cur - bas
    got_removed = bas - cur

    def want(pairs):
        c = Counter()
        for name, pos3 in pairs:
            c[(name.lower(), tuple(round(v, 3) for v in pos3))] += 1
        return c

    # expectations are given by BASENAME; match the delta on basename+pos.
    def by_basename(counter):
        out = Counter()
        for (dbr, pos3), n in counter.items():
            out[(dbr.split(BS.encode())[-1], pos3)] += n
        return out

    check(f'{label}: appended set is exactly as declared ({len(list(appended))})',
          by_basename(got_added) == want(appended),
          f'got {[_fmt(k) for k in got_added]}')
    check(f'{label}: removed set is exactly as declared ({len(list(removed))})',
          by_basename(got_removed) == want(removed),
          f'got {[_fmt(k) for k in got_removed]}')

    # every appended instance sits at the TAIL, flags=0 (append-only byte-shape)
    n_add = sum(got_added.values())
    if require_tail and n_add:
        tail = insts[-n_add:]
        check(f'{label}: the {n_add} appended instance(s) are the LAST instances',
              by_basename(Counter(_key(i) for i in tail)) == want(appended),
              f'tail={[i["dbr"].decode("latin-1").split(BS)[-1] for i in tail]}')
        check(f'{label}: every appended instance has flags == 0 (proxy/NPC byte-shape)',
              all(i['flags'] == 0 for i in tail),
              f'flags={[i["flags"] for i in tail]}')

    # the surviving pre-existing instances kept their order AND position
    surviving = [i for i in binsts if _key(i) not in got_removed]
    kept = insts[:len(insts) - n_add] if n_add else insts
    check(f'{label}: all {len(surviving)} pre-existing instances unchanged (dbr+pos)',
          [_key(i) for i in kept] == [_key(i) for i in surviving])

    # collateral: every OTHER section byte-identical unless declared
    for t in sorted(set(bsecs) | set(secs)):
        if t == 0x05 or t in allow_sections:
            continue
        check(f'{label}: section 0x{t:02x} byte-identical to baseline',
              secs.get(t) == bsecs.get(t),
              f'{len(bsecs.get(t, b""))} -> {len(secs.get(t, b""))} bytes')
    if 0x0b in bsecs or 0x0b in secs:
        check(f'{label}: 0x0b navmesh byte-identical (injection never touches it)',
              secs.get(0x0b) == bsecs.get(0x0b))
    check(f'{label}: no stale 0x0a alongside 0x0b',
          0x0a not in secs or 0x0b not in secs)
    return insts


# ---------------------------------------------------------------------------
# The declared deltas. Each entry: level suffix -> (appended, removed, allow_sections).
# APPENDED/REMOVED are (dbr basename, (x, y, z)) - basenames, so a namespace move does
# not silently pass. Sources: the INJECT_SPECS / removal tables in
# tools/build_section_surgery.py; see the module notes there for the design rationale.
# ---------------------------------------------------------------------------

# M9: random05a (v0x0e) - the FIRST live use of the v0e SVAERA-host inject branch.
M9 = ('orient/underground/random05a.lvl',
      [(b'q_vashkarr_lone.dbr', (24.0, 1.0, 31.7))], [], ())

# M8: startingfarmland06d (v0x11) - the Almyros portal master. The two
# portal_olympianarena entities + their aura were REMOVED after build31g
# (remove_0x05_instances_by_0x14_uid / _by_dbr; the 0x14 binding table changes with
# them, hence 0x14 is a DECLARED delta rather than a silent one).
M8 = ('startingtownver2/startingfarmland06d.lvl',
      [(b'portal_master_helos.dbr', (76.5, 0.6, 189.5))],
      [(b'portal_olympianarena1.dbr', (74.0, 0.4, 184.0)),
       (b'map_portal_aura.dbr', (74.0, 0.4, 184.0)),
       (b'portal_olympianarena2.dbr', (68.0, -0.4, 181.0))],
      (0x14,))

# M10: the Obsidian roulette corners + the Broodmother nest (v0x0e branch), vs build32a.
M10 = [
    ('orient/typhonug/tombobs02.lvl',
     [(b'q_obs_roulette_a.dbr', (50.4, 1.0, 143.6)),
      (b'q_obs_roulette_c.dbr', (200.4, 1.0, 97.6)),
      (b'q_broodmother_lone.dbr', (184.0, 1.2, 192.0)),
      (b'q_broodnest_egg_a.dbr', (184.0, 1.2, 202.0)),
      (b'q_broodnest_egg_b.dbr', (175.3, 1.2, 197.0)),
      (b'q_broodnest_egg_c.dbr', (175.3, 1.2, 187.0)),
      (b'q_broodnest_egg_d.dbr', (184.0, 1.2, 182.0)),
      (b'q_broodnest_egg_e.dbr', (192.7, 1.2, 187.0)),
      (b'q_broodnest_egg_f.dbr', (192.7, 1.2, 197.0))], [], ()),
    ('orient/typhonug/tombobs01.lvl',
     [(b'q_obs_roulette_b.dbr', (220.8, 1.0, 89.6)),
      (b'q_obs_roulette_d.dbr', (92.8, 1.0, 47.6))], [], ()),
]

# TESTHUB hosts: every one must be canonical PLUS tail-appended hub NPCs, and nothing
# else. HiddenValley01 is the b76 guard - it must be IDENTICAL (no monster yard).
HUB_NAMESPACE = b'records' + BS.encode() + b'quests' + BS.encode()
HUB_PREFIXES = (b'svc_testhub', b'svc_helos_trav')
HV01 = 'orient/silkroad/hiddenvalley01.lvl'
# The ONLY canonical placement the TESTHUB build is allowed to drop: the b48
# SPARTA-MUTE FIX deliberately removes the canonical Almyros master from the Helos
# plaza so the dedicated one-route-each travellers own their routes (the engine's
# boat dialog is strictly 1 route : 1 NPC). See merge_hub_into_inject_specs in
# tools/build_section_surgery.py - the canonical/Steam build is untouched.
HUB_DECLARED_DROPS = {
    'startingtownver2/startingfarmland06d.lvl': {
        (b'records' + BS.encode() + b'quests' + BS.encode() + b'portal_master_helos.dbr',
         (76.5, 0.6, 189.5)),
    },
}
HUB_HOSTS = [
    'startingtownver2/startingfarmland06d.lvl',
    'orient/underground/random09a.lvl',
    'olympus/gardenofmerchants.lvl',
    'secret_place/darkforestenter.lvl',
    'uberdungeon/crypt_floor1.lvl',
    'minidungeons/spartacryptlevel2.lvl',
    'bossarena/boss_arena.lvl',
]


def run_hub_checks(map_path, canonical_path):
    data, levels = load_world(map_path)
    cdata, clevels = load_world(canonical_path)

    print('--- HV01 b76 GUARD: the removed Monster Test Yard must NOT come back ---')
    _lv, blob = get_blob(data, levels, HV01)
    _clv, cblob = get_blob(cdata, clevels, HV01)
    check('TESTHUB HiddenValley01 is byte-identical to canonical (no yard)',
          blob == cblob, f'{len(cblob)} -> {len(blob)} bytes')
    if blob != cblob:
        base = blob_0x05_base(blob)
        _s, ins, _e, _n = walk_0x05(dict(parse_blob_sections(blob))[0x05], base)
        _s, cin, _e, _n = walk_0x05(dict(parse_blob_sections(cblob))[0x05], base)
        extra = Counter(_key(i) for i in ins) - Counter(_key(i) for i in cin)
        for k in extra:
            print(f'      !! TESTHUB-only HV01 placement: {_fmt(k)}')

    for suffix in HUB_HOSTS:
        print(f'--- HUB {suffix} (canonical + tail-appended hub NPCs only) ---')
        _lv, blob = get_blob(data, levels, suffix)
        _clv, cblob = get_blob(cdata, clevels, suffix)
        base = blob_0x05_base(blob)
        secs = dict(parse_blob_sections(blob))
        csecs = dict(parse_blob_sections(cblob))
        _s, insts, endpos, ninst = walk_0x05(secs[0x05], base)
        _s, cinsts, _ce, cninst = walk_0x05(csecs[0x05], base)
        ok, end = blob_walk_exact(blob)
        check(f'{suffix}: blob walk reaches exact end', ok, f'end={end} len={len(blob)}')
        check(f'{suffix}: 0x05 walk lands at exact section end (stride {base})',
              endpos == len(secs[0x05]), f'end={endpos} len={len(secs[0x05])}')
        added = Counter(_key(i) for i in insts) - Counter(_key(i) for i in cinsts)
        dropped = Counter(_key(i) for i in cinsts) - Counter(_key(i) for i in insts)
        n_add = sum(added.values())
        # Some hub NPCs have since been promoted into the CANONICAL map; a host with a
        # zero delta is legitimate. What must NEVER happen is an UNDECLARED drop, a
        # non-hub addition, or a non-tail insertion.
        allowed_drops = HUB_DECLARED_DROPS.get(suffix, set())
        undeclared = [k for k in dropped if k not in allowed_drops]
        check(f'{suffix}: TESTHUB drops nothing beyond the declared '
              f'{len(allowed_drops)} exception(s)', not undeclared,
              f'undeclared drops {[_fmt(k) for k in undeclared]}')
        bad_ns = [k for k in added
                  if not (k[0].startswith(HUB_NAMESPACE)
                          and any(k[0].split(BS.encode())[-1].startswith(p)
                                  for p in HUB_PREFIXES))]
        check(f'{suffix}: all {n_add} TESTHUB-only addition(s) are in the '
              f'records{BS}quests{BS}svc_ hub namespace', not bad_ns,
              f'offenders {[_fmt(k) for k in bad_ns]}')
        surviving = [_key(i) for i in cinsts if _key(i) not in dropped]
        head = [_key(i) for i in (insts[:-n_add] if n_add else insts)]
        if n_add:
            tail = insts[-n_add:]
            check(f'{suffix}: the {n_add} hub NPC(s) are the LAST instances',
                  Counter(_key(i) for i in tail) == added,
                  f'tail={[i["dbr"].decode("latin-1").split(BS)[-1] for i in tail]}')
            check(f'{suffix}: every hub NPC has flags == 0',
                  all(i['flags'] == 0 for i in tail))
        check(f'{suffix}: all {len(surviving)} surviving canonical instances unchanged '
              f'(dbr+pos, order)', head == surviving)
        for t in sorted(set(csecs) | set(secs)):
            if t == 0x05:
                continue
            check(f'{suffix}: section 0x{t:02x} byte-identical to canonical',
                  secs.get(t) == csecs.get(t),
                  f'{len(csecs.get(t, b""))} -> {len(secs.get(t, b""))} bytes')


def selftest():
    """PLANTED NEGATIVE TESTS: the checks must FAIL on a deliberately broken input.

    A gate nobody has seen fail is not a gate. These mutate an in-memory blob and
    assert the comparison rejects it - no artifact is written or read.
    """
    global FAIL
    print('=== gate_build32_parseback SELFTEST (planted negatives) ===')
    results = []

    def mk_section_0x05(entries, base=56):
        """Build a synthetic 0x05 section: entries = [(dbr, (x,y,z))]."""
        strings = []
        for dbr, _p in entries:
            if dbr not in strings:
                strings.append(dbr)
        out = struct.pack('<I', len(strings))
        for s in strings:
            out += struct.pack('<I', len(s)) + s
        out += struct.pack('<I', len(entries))
        for dbr, (x, y, z) in entries:
            rec = struct.pack('<I', strings.index(dbr))
            rec += struct.pack('<9f', 1, 0, 0, 0, 1, 0, 0, 0, 1)
            rec += struct.pack('<3f', x, y, z)
            rec += struct.pack('<I', 0)
            if base == 72:
                rec += b'\x00' * 16
            out += rec
        return out

    def mk_blob(entries, ver=0x0e):
        sd = mk_section_0x05(entries, 72 if ver in (0x11, 0x0f) else 56)
        return (b'LVL' + bytes([ver]) + struct.pack('<II', 0x05, len(sd)) + sd)

    base_entries = [(b'records' + BS.encode() + b'a.dbr', (1.0, 2.0, 3.0)),
                    (b'records' + BS.encode() + b'b.dbr', (4.0, 5.0, 6.0))]
    appended = (b'records' + BS.encode() + b'new.dbr', (7.0, 8.0, 9.0))

    scenarios = [
        ('NEG-1 undeclared extra append is rejected',
         base_entries + [appended, (b'records' + BS.encode() + b'sneak.dbr', (1., 1., 1.))],
         [(b'new.dbr', (7.0, 8.0, 9.0))]),
        ('NEG-2 silent removal of a pre-existing instance is rejected',
         [base_entries[0], appended],
         [(b'new.dbr', (7.0, 8.0, 9.0))]),
        ('NEG-3 a moved pre-existing instance is rejected',
         [base_entries[0], (b'records' + BS.encode() + b'b.dbr', (4.0, 5.0, 99.0)), appended],
         [(b'new.dbr', (7.0, 8.0, 9.0))]),
        ('NEG-4 a NON-tail insertion is rejected',
         [base_entries[0], appended, base_entries[1]],
         [(b'new.dbr', (7.0, 8.0, 9.0))]),
    ]
    bblob = mk_blob(base_entries)
    for name, entries, declared in scenarios:
        FAIL = []
        compare_level('SELFTEST', mk_blob(entries), bblob, declared)
        ok = bool(FAIL)
        results.append((name, ok, f'{len(FAIL)} sub-check(s) failed as intended'))

    # POS-1: the honest append must PASS cleanly.
    FAIL = []
    compare_level('SELFTEST', mk_blob(base_entries + [appended]), bblob,
                  [(b'new.dbr', (7.0, 8.0, 9.0))])
    results.append(('POS-1 an honest tail append passes', not FAIL, str(FAIL)))

    FAIL = []
    print()
    bad = []
    for name, ok, detail in results:
        print(f'  [{"PASS" if ok else "FAIL"}] {name}  ({detail})')
        if not ok:
            bad.append(name)
    print()
    print(f'RESULT: {"FAIL " + str(bad) if bad else "PASS (selftest clean)"}')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    ap.add_argument('--baseline',
                    default=str(REPO / 'local' / 'Levels_merged.build31g-baseline.arc'),
                    help='baseline for the M8/M9 deltas')
    ap.add_argument('--m10-baseline',
                    default=str(REPO / 'local' / 'Levels_merged.build32a-baseline.arc'),
                    help='baseline for the M10 tombobs deltas (the pre-M10 build32a map)')
    ap.add_argument('--skip-m10', action='store_true',
                    help='skip the M10 tombobs checks (to gate a pre-M10 build)')
    ap.add_argument('--testhub', action='store_true',
                    help='--map is the TESTHUB variant: run the HV01 b76 guard + the '
                         'hub-host append/namespace invariants against --canonical')
    ap.add_argument('--canonical', default=str(REPO / 'local' / 'Levels_merged.arc'),
                    help='with --testhub: the canonical map to diff against')
    ap.add_argument('--selftest', action='store_true',
                    help='run the planted negative tests and exit')
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    print(f'=== GATE map append parse-back: {args.map} ===')
    # The M8/M9/M10 deltas describe the CANONICAL build. Under --testhub the map under
    # test carries the hub NPCs on top, so those blocks run against --canonical and the
    # TESTHUB map is judged by the hub invariants below (this is what the old gate got
    # wrong by patching a single `exp_count = 997 if args.testhub`).
    m_map = args.canonical if args.testhub else args.map
    if args.testhub:
        print(f'    (--testhub: M8/M9/M10 evaluated against the canonical map {m_map})')
    data, levels = load_world(m_map)
    bdata, blevels = load_world(args.baseline)

    print('--- M9 random05a (v0x0e host inject branch) ---')
    suffix, appended, removed, allow = M9
    _lv, blob = get_blob(data, levels, suffix)
    _blv, bblob = get_blob(bdata, blevels, suffix)
    compare_level('M9 random05a', blob, bblob, appended, removed, allow)

    print('--- M8 startingfarmland06d (v0x11 host inject branch) ---')
    suffix, appended, removed, allow = M8
    _lv, blob = get_blob(data, levels, suffix)
    _blv, bblob = get_blob(bdata, blevels, suffix)
    compare_level('M8 farmland06d', blob, bblob, appended, removed, allow)

    if not args.skip_m10:
        mdata, mlevels = load_world(args.m10_baseline)
        for suffix, appended, removed, allow in M10:
            print(f'--- M10 {suffix} (v0x0e branch) ---')
            _lv, blob = get_blob(data, levels, suffix)
            _blv, bblob = get_blob(mdata, mlevels, suffix)
            compare_level(f'M10 {suffix.split("/")[-1]}', blob, bblob,
                          appended, removed, allow)

    if args.testhub:
        run_hub_checks(args.map, args.canonical)

    print()
    if FAIL:
        print(f'RESULT: FAIL ({len(FAIL)}): {FAIL}')
        return 1
    scope = 'M8 + M9' if args.skip_m10 else 'M8 + M9 + M10'
    if args.testhub:
        scope += ' + HV01-b76-guard + HUB'
    print(f'RESULT: PASS ({scope} parse-back clean)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
