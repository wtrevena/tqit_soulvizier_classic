#!/usr/bin/env python3
"""Negative tests for contracts_map.py.

For each contract: build a COMPLIANT synthetic input (assert no target violation),
then surgically BREAK it (assert the contract fires the expected violation). Proves
each check actually detects the defect it claims to. Run:
  python tools/contracts/_negtest_map.py
Exits 0 if every contract's negative test PASSES, 1 otherwise. Self-contained
(builds tiny in-memory map/blob/arz structures; no big artifacts needed)."""
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import contracts_map as C


# ---- tiny binary builders (inverse of the module's parsers) ----------------
def lp(s):
    b = s if isinstance(s, bytes) else s.encode('latin-1')
    return struct.pack('<I', len(b)) + b


def make_0x05(dbrs, ver=0x11):
    """0x05 section: string table + one instance per dbr (flags=0)."""
    base_flagsize = 72 if ver in (0x11, 0x0f) else 56
    d = bytearray()
    d += struct.pack('<I', len(dbrs))
    for s in dbrs:
        d += lp(s)
    d += struct.pack('<I', len(dbrs))
    for i in range(len(dbrs)):
        rec = bytearray(base_flagsize)
        struct.pack_into('<I', rec, 0, i)      # sidx = i (1 instance per string)
        struct.pack_into('<I', rec, 52, 0)     # flags = 0
        d += rec
    return bytes(d)


def make_0x14(recs):
    """recs = {instance_index: payload_bytes}."""
    d = bytearray()
    for idx, pl in recs.items():
        d += struct.pack('<II', idx, len(pl)) + pl
    return bytes(d)


def make_blob(sections, ver=0x11):
    """sections = list of (type, data). magic byte[3] = ver."""
    out = bytearray(b'\x00\x00\x00' + bytes([ver]))
    for t, data in sections:
        out += struct.pack('<II', t, len(data)) + data
    return bytes(out)


def rec02_tileset(num_tiles=0, max_tiles=208):
    """One complete 56-byte tileset record: dtTileCacheParams (52) + int32 numTiles."""
    return struct.pack('<3f2f2i4f2i', 0.0, 0.0, 0.0, 0.2, 0.2, 64, 64,
                       2.0, 0.4, 1.0, 1.3, max_tiles, 128) + struct.pack('<i', num_tiles)


def make_rec02(guid, version=1, guids=None, n_sets=3, tail=b''):
    """A structurally VALID, empty REC\\x02 container - the shape stock ships for a
    level with terrain but no walkable floor (3 complete tilesets, numTiles 0).

    guids  : full GUID list override (default [guid]) - used to plant a DEGENERATE list.
    n_sets : number of tilesets emitted - used to plant a truncated/short body.
    tail   : extra bytes appended after the last tileset - used to plant trailing junk.
    """
    gl = list(guids) if guids is not None else [guid]
    body = struct.pack('<I', len(gl))                 # guid_count
    for g in gl:
        body += g                                      # 16B guid each
    body += struct.pack('<3i', 0, 0, 0)                # center
    body += struct.pack('<3I', 100, 0, 100)            # dims
    body += rec02_tileset() * n_sets                   # 3 complete empty tilesets
    body += tail
    total = bytearray(b'REC\x02' + struct.pack('<II', version, 0) + body)
    struct.pack_into('<I', total, 8, len(total) - 12)  # payload_size = total-12
    return bytes(total)


def make_b89_stub(guid):
    """Byte-faithful reconstruction of the DEAD 148-byte Approach-22 stub that killed
    two Frida sessions on 2026-07-27 (b89): a valid header (version 1, correct
    payload_size, guid_count 3, every GUID resolving) over a body holding ONE
    TRUNCATED 44-byte parameter block + 4 stray zero uint32s, i.e. neither three
    tilesets nor a clean end. This is the exact planted condition MAP-NAV-5 and
    MAP-NAV-6 must both catch."""
    body = struct.pack('<I', 3) + guid * 3             # DEGENERATE list: own x3
    body += struct.pack('<3i', 0, 0, 0)                # center
    body += struct.pack('<3I', 100, 0, 100)            # dims
    body += struct.pack('<3f', 0.0, 0.0, 0.0)          # orig
    body += struct.pack('<2f', 0.2, 0.2)               # cs, ch
    body += struct.pack('<2I', 64, 64)                 # width, height
    body += struct.pack('<4f', 2.0, 0.4, 1.0, 1.3)     # walkable* + maxSimplifError
    body += struct.pack('<4I', 0, 0, 0, 0)             # the stray "tile counts"
    total = bytearray(b'REC\x02' + struct.pack('<II', 1, 0) + body)
    struct.pack_into('<I', total, 8, len(total) - 12)
    assert len(total) == 148, len(total)
    return bytes(total)


def make_top_map(sections):
    """Top-level world map: 8B header + type/size/data sections."""
    out = bytearray(struct.pack('<II', 0x0650414D, 0))
    for t, data in sections:
        out += struct.pack('<II', t, len(data)) + data
    return bytes(out)


def make_groups(records):
    """records = list of (sub_count, name, category, member_bytes)."""
    out = bytearray(struct.pack('<II', 0, len(records)))
    for sub, name, cat, mem in records:
        out += struct.pack('<I', sub)
        out += lp(name)
        out += lp(cat)
        # member_count derived from mem length / 44
        out += struct.pack('<I', len(mem) // 44)
        out += mem
    return bytes(out)


def make_sd(tags):
    """SD section that embeds each tag as a length-prefixed ASCII string,
    padded so the recon scanner locks onto the length prefixes."""
    out = bytearray(b'\x00' * 4)
    for t in tags:
        out += lp(t) + b'\x00\x00\x00\x00'
    return bytes(out)


# ---- fake ctx: only the attributes the contract-under-test touches ----------
class FakeArz:
    def __init__(self, fields=None):
        self._f = fields or {}

    def field(self, name, field):
        return self._f.get((name, field))


class FakeCtx:
    def __init__(self, **kw):
        self.cfg = {}
        self.levels = []
        self.level_guids = set()
        self.merged_quests = []
        self.base_quests = None
        self.map_data = b''
        self.secs = {}
        self.arz = FakeArz()
        self.base_arz = None
        self.arz_class = {}
        self.base_class = {}
        self.text_keys = set()
        self.text_values = {}
        self._uids = set()
        self._names = set()
        for k, v in kw.items():
            setattr(self, k, v)

    def blob(self, lv):
        return lv['_blob']

    def class_of(self, np):
        return self.arz_class.get(np) or self.base_class.get(np)

    def rec_resolves(self, np):
        return np in self._names

    def all_instance_uids(self):
        return self._uids


RESULTS = []


def check(name, condition, detail=''):
    RESULTS.append((name, bool(condition), detail))
    print(f'  [{"PASS" if condition else "FAIL"}] {name}' + (f' :: {detail}' if detail and not condition else ''))


def has(viols, cid):
    return any(v['contract'] == cid for v in viols)


GUID_A = bytes.fromhex('11' * 16)
GUID_B = bytes.fromhex('22' * 16)
BADGUID = bytes.fromhex('99' * 16)


# ===========================================================================
def test_quests():
    print('CONTRACT 1: QUESTS')
    good = [b'Quests/x.qst'] * 96 + [b'Quests/widowletter.qst', b'Quests/urder.qst',
            b'Quests/bossarena.qst', b'Quests/open_bloodcave_portal.qst'] + [b'Quests/y.qst'] * 156
    van = list(good)
    # compliant
    ctx = FakeCtx(merged_quests=list(good), base_quests=list(van))
    base_v = C.contract_quests(ctx)
    check('QUESTS-1/2/3 clean on compliant', len(base_v) == 0, f'{base_v}')
    # break 1: >256 entries
    ctx1 = FakeCtx(merged_quests=list(good) + [b'Quests/extra.qst'] * 10, base_quests=list(van))
    check('QUESTS-1 fires when >256', has(C.contract_quests(ctx1), 'MAP-QUESTS-1'))
    # break 2: widowletter moved past the load window
    bad2 = [q for q in good if b'widowletter' not in q.lower()]
    bad2 = bad2[:254] + [b'Quests/widowletter.qst'] + bad2[254:]
    ctx2 = FakeCtx(merged_quests=bad2, base_quests=list(van))
    check('QUESTS-2 fires when SV quest >= idx 254',
          any(v['contract'] == 'MAP-QUESTS-2' for v in C.contract_quests(ctx2)))
    # break 2b: SV quest missing entirely
    bad2b = [q for q in good if b'bossarena' not in q.lower()]
    ctx2b = FakeCtx(merged_quests=bad2b, base_quests=list(van))
    check('QUESTS-2 fires when SV quest absent',
          any('bossarena' in v['subject'] for v in C.contract_quests(ctx2b) if v['contract'] == 'MAP-QUESTS-2'))
    # break 3: boundary parity
    bad3 = list(good)
    bad3[254] = b'Quests/somethingelse.qst'
    ctx3 = FakeCtx(merged_quests=bad3, base_quests=list(van))
    check('QUESTS-3 fires on boundary mismatch', has(C.contract_quests(ctx3), 'MAP-QUESTS-3'))


def _portal_ctx(dest, exit_uid, landing_exists=True, mouth=b'\xaa' * 16):
    P1 = b'records\\quests\\portal_olympianarena1.dbr'
    P2 = b'records\\quests\\portal_olympianarena2.dbr'
    binding_ent = mouth + exit_uid + dest
    ent_blob = make_blob([(0x05, make_0x05([P1])),
                          (0x14, make_0x14({0: C.GRIDENTRANCE_PREFIX + binding_ent}))])
    levels = [{'fname': 'xBloodCave/test_entrance.lvl', '_blob': ent_blob, 'guid': GUID_A}]
    if landing_exists:
        land_binding = exit_uid + b'\x00' * 32
        land_blob = make_blob([(0x05, make_0x05([P2])),
                               (0x14, make_0x14({0: land_binding}))])
        levels.append({'fname': 'xBloodCave/test_landing.lvl', '_blob': land_blob, 'guid': GUID_B})
    return FakeCtx(levels=levels, level_guids={GUID_A, GUID_B},
                   arz_class={C.norm_rec(P1): 'GridEntrance', C.norm_rec(P2): 'GridExitOneWay'})


def test_portals():
    print('CONTRACT 2: PORTALS')
    exit_uid = b'\xbb' * 16
    ok = C.contract_portals(_portal_ctx(GUID_B, exit_uid, landing_exists=True))
    check('PORTAL compliant -> no violation', len(ok) == 0, f'{ok}')
    bad1 = C.contract_portals(_portal_ctx(BADGUID, exit_uid, landing_exists=True))
    check('PORTAL-1 fires on unresolvable dest (ours=P0)',
          any(v['contract'] == 'MAP-PORTAL-1' and v['severity'] == 'P0' for v in bad1))
    bad3 = C.contract_portals(_portal_ctx(GUID_B, exit_uid, landing_exists=False))
    check('PORTAL-3 fires on dangling exit (no landing/0x06)',
          any(v['contract'] == 'MAP-PORTAL-3' and v['severity'] == 'P1' for v in bad3))
    # collision: two entrances sharing a mouth
    P1 = b'records\\quests\\portal_olympianarena1.dbr'
    b1 = make_blob([(0x05, make_0x05([P1])), (0x14, make_0x14({0: C.GRIDENTRANCE_PREFIX + b'\xcc' * 16 + exit_uid + GUID_B}))])
    b2 = make_blob([(0x05, make_0x05([P1])), (0x14, make_0x14({0: C.GRIDENTRANCE_PREFIX + b'\xcc' * 16 + (b'\xdd' * 16) + GUID_B}))])
    ctxc = FakeCtx(levels=[{'fname': 'a.lvl', '_blob': b1, 'guid': GUID_A},
                           {'fname': 'b.lvl', '_blob': b2, 'guid': GUID_B}],
                   level_guids={GUID_A, GUID_B}, arz_class={C.norm_rec(P1): 'GridEntrance'})
    check('PORTAL-2 fires on mouth-UID collision', has(C.contract_portals(ctxc), 'MAP-PORTAL-2'))


def _nav_ctx(sections, fname='xBloodCave/test.lvl'):
    return FakeCtx(levels=[{'fname': fname, '_blob': make_blob(sections), 'guid': GUID_A}],
                   level_guids={GUID_A, GUID_B})


def test_navmesh():
    print('CONTRACT 3: NAVMESH')
    good = make_rec02(GUID_A)
    ok = C.contract_navmesh(_nav_ctx([(0x0b, good)]))
    check('NAV compliant -> no violation', len(ok) == 0, f'{ok}')
    # NAV-1: unresolved guid in list
    badnav = make_rec02(BADGUID)
    check('NAV-1 fires on unresolved navmesh GUID',
          has(C.contract_navmesh(_nav_ctx([(0x0b, badnav)])), 'MAP-NAV-1'))
    # NAV-1: bad magic
    check('NAV-1 fires on bad REC magic',
          has(C.contract_navmesh(_nav_ctx([(0x0b, b'XXXX' + good[4:])])), 'MAP-NAV-1'))
    # NAV-2: both 0x0a and 0x0b
    check('NAV-2 fires when 0x0a coexists with 0x0b',
          has(C.contract_navmesh(_nav_ctx([(0x0a, b'PTH\x00'), (0x0b, good)])), 'MAP-NAV-2'))
    # NAV-3: drxmap level (blob contains 'drxmap') with no 0x0b
    drxblob = make_blob([(0x05, make_0x05([b'records\\drxmap\\bloodcave\\x.dbr']))])
    ctx3 = FakeCtx(levels=[{'fname': 'xBloodCave/nodx.lvl', '_blob': drxblob, 'guid': GUID_A}],
                   level_guids={GUID_A})
    check('NAV-3 fires on drxmap level lacking 0x0b', has(C.contract_navmesh(ctx3), 'MAP-NAV-3'))

    # ---- b89 (2026-07-27): the ocean_extension05 stream-in crash ------------------
    # THE planted condition: the real dead 148-byte stub, verbatim. Must trip BOTH the
    # structural gate (truncated body) and the degenerate-list gate.
    stub = make_b89_stub(GUID_A)
    got = C.contract_navmesh(_nav_ctx([(0x0b, stub)]))
    check('NAV-5 fires on the real b89 148-byte stub (truncated tileset body)',
          has(got, 'MAP-NAV-5'), f'{got}')
    check('NAV-6 fires on the real b89 148-byte stub (self-duplicated GUID list)',
          has(got, 'MAP-NAV-6'), f'{got}')
    check('b89 stub is P0 on both gates',
          all(x['severity'] == 'P0' for x in got
              if x['contract'] in ('MAP-NAV-5', 'MAP-NAV-6')))
    # the header-only checks it slipped past - proof the OLD gates could not see it
    check('b89 stub passes every pre-existing NAV-1 header check (why it shipped)',
          not has(got, 'MAP-NAV-1'), f'{got}')

    # NAV-5 variants: too few / too many tilesets, trailing junk, garbage tile record
    check('NAV-5 fires on 2 tilesets (one short)',
          has(C.contract_navmesh(_nav_ctx([(0x0b, make_rec02(GUID_A, n_sets=2))])),
              'MAP-NAV-5'))
    check('NAV-5 fires on 4 tilesets (one extra)',
          has(C.contract_navmesh(_nav_ctx([(0x0b, make_rec02(GUID_A, n_sets=4))])),
              'MAP-NAV-5'))
    check('NAV-5 fires on trailing bytes after the last tileset',
          has(C.contract_navmesh(_nav_ctx([(0x0b, make_rec02(GUID_A, tail=b'\x00' * 9))])),
              'MAP-NAV-5'))
    # a tileset claiming a tile whose data is not there at all
    lying = bytearray(make_rec02(GUID_A))
    struct.pack_into('<i', lying, 16 + 16 + 24 + 52, 1)   # set 1 numTiles 0 -> 1
    check('NAV-5 fires on a tileset claiming a tile it does not carry',
          has(C.contract_navmesh(_nav_ctx([(0x0b, bytes(lying))])), 'MAP-NAV-5'))

    # NAV-6: degenerate list on an otherwise well-formed container
    degen = make_rec02(GUID_A, guids=[GUID_A, GUID_A, GUID_A])
    gotd = C.contract_navmesh(_nav_ctx([(0x0b, degen)]))
    check('NAV-6 fires on a degenerate list in a structurally valid container',
          has(gotd, 'MAP-NAV-6'), f'{gotd}')
    check('NAV-5 stays silent on that (body is fine)', not has(gotd, 'MAP-NAV-5'), f'{gotd}')
    # a DISTINCT multi-GUID list is normal (stock ships thousands) - must NOT fire
    check('NAV-6 silent on a distinct multi-GUID list',
          not has(C.contract_navmesh(_nav_ctx([(0x0b, make_rec02(GUID_A, guids=[GUID_A, GUID_B]))])),
                  'MAP-NAV-6'))
    # own-only (guid_count == 1) is stock-normal (251 base levels) - must NOT fire
    check('NAV-6 silent on a single-own-GUID list (stock-normal, 251 base levels)',
          not has(C.contract_navmesh(_nav_ctx([(0x0b, make_rec02(GUID_A))])), 'MAP-NAV-6'))

    # the SHIPPED replacement container must clear both new gates
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from build_section_surgery import build_minimal_rec02
    ints = bytearray(struct.pack('<13i', 120, 24, 120, 120, 24, 120, 4426, -37, 3109, 0, 0, 0, 0))
    ints[36:52] = GUID_A
    fixed = build_minimal_rec02(bytes(ints))
    gotf = C.contract_navmesh(_nav_ctx([(0x0b, fixed)]))
    check('the b89 REPLACEMENT empty container passes every navmesh contract',
          len(gotf) == 0 and len(fixed) == 224, f'{len(fixed)}B {gotf}')


def test_groups():
    print('CONTRACT 4: GROUPS')
    good_uid = b'\x77' * 16
    member = good_uid + GUID_A + struct.pack('<3f', 1, 2, 3)   # 44B: uid+guid+pos
    sec = make_groups([(2, 'Shrine_Respawn_Test', 'RespawnShrine', member)])
    ctx = FakeCtx(map_data=make_top_map([(C.SEC_GROUPS, sec)]),
                  secs=None, _uids={good_uid})
    ctx.secs = C.parse_top_sections(ctx.map_data)
    ok = C.contract_groups(ctx)
    check('GROUPS compliant -> no violation', len(ok) == 0, f'{ok}')
    # break: member uid resolves to nothing (wholly stale)
    ctx_bad = FakeCtx(map_data=ctx.map_data, secs=ctx.secs, _uids=set())
    check('GROUPS-1 fires when no member resolves', has(C.contract_groups(ctx_bad), 'MAP-GROUPS-1'))
    # break: empty group
    sec0 = make_groups([(2, 'Shrine_Empty', 'RespawnShrine', b'')])
    ctx0 = FakeCtx(map_data=make_top_map([(C.SEC_GROUPS, sec0)]), _uids={good_uid})
    ctx0.secs = C.parse_top_sections(ctx0.map_data)
    check('GROUPS-1 fires on empty binding group', has(C.contract_groups(ctx0), 'MAP-GROUPS-1'))


def test_doors():
    print('CONTRACT 5: DOORS')
    # use a REAL Quests.arc (has UnlockFixedItem refs); place a fake SV door that
    # is / isn't referenced. The path was hard-coded to one session's scratchpad, which
    # made this whole harness un-runnable once that scratchpad was cleaned (b89 found it
    # while wiring the NAV-5/NAV-6 planted tests). Resolve the live staged/local artifact
    # instead, honour SVC_QUESTS_ARC, and SKIP loudly rather than crash if none exists.
    repo = Path(__file__).resolve().parent.parent.parent
    cands = [os.environ.get('SVC_QUESTS_ARC'),
             repo / 'work' / 'SoulvizierClassic' / 'Resources' / 'Quests.arc',
             repo / 'local' / 'Quests_scratch.arc']
    qa = next((str(c) for c in cands if c and Path(c).exists()), None)
    if qa is None:
        print('  [SKIP] DOORS negative test: no Quests.arc found '
              '(set SVC_QUESTS_ARC to run it)')
        return
    referenced = b'records\\drxmap\\xurder\\doors\\tj_door01.dbr'    # urder.qst unlocks it
    unref = b'records\\drxmap\\bloodcave\\doors\\ghost_sealed_door.dbr'  # nothing unlocks it
    fake_arz = FakeArz({(C.norm_rec(referenced), 'locked'): 1, (C.norm_rec(unref), 'locked'): 1})
    cls = {C.norm_rec(referenced): 'FixedItemDoor', C.norm_rec(unref): 'FixedItemDoor'}
    # compliant: only the referenced locked SV door
    blob_ok = make_blob([(0x05, make_0x05([referenced]))])
    ctx_ok = FakeCtx(cfg={'quests_arc': qa}, arz=fake_arz, arz_class=cls,
                     levels=[{'fname': 'xBloodCave/d.lvl', '_blob': blob_ok, 'guid': GUID_A}])
    ok = C.contract_doors(ctx_ok)
    check('DOOR compliant (referenced) -> no violation', len(ok) == 0, f'{ok}')
    # broken: an unreferenced locked SV door
    blob_bad = make_blob([(0x05, make_0x05([unref]))])
    ctx_bad = FakeCtx(cfg={'quests_arc': qa}, arz=fake_arz, arz_class=cls,
                      levels=[{'fname': 'xBloodCave/d.lvl', '_blob': blob_bad, 'guid': GUID_A}])
    check('DOOR-1 fires on unreferenced locked SV door', has(C.contract_doors(ctx_bad), 'MAP-DOOR-1'))


def test_sd():
    print('CONTRACT 6: SD TAGS')
    # compliant: a resolving display tag + a correctly-labelled restored zone
    sd = make_sd(['tagRegionName01', 'tagMZoneGoM'])
    ctx = FakeCtx(map_data=make_top_map([(C.SEC_SD, sd)]),
                  text_keys={'tagRegionName01', 'tagMZoneGoM'},
                  text_values={'tagRegionName01': 'Helos', 'tagMZoneGoM': 'Garden of Merchants'})
    ctx.secs = C.parse_top_sections(ctx.map_data)
    ok = C.contract_sd_tags(ctx)
    check('SD compliant -> no violation', len(ok) == 0, f'{ok}')
    # SD-1: an unresolved display tag
    ctx1 = FakeCtx(map_data=ctx.map_data, secs=ctx.secs,
                   text_keys={'tagMZoneGoM'}, text_values={'tagMZoneGoM': 'Garden of Merchants'})
    check('SD-1 fires on unresolved display tag', has(C.contract_sd_tags(ctx1), 'MAP-SD-1'))
    # SD-2: restored zone mislabelled (the Duister class)
    ctx2 = FakeCtx(map_data=ctx.map_data, secs=ctx.secs,
                   text_keys={'tagRegionName01', 'tagMZoneGoM'},
                   text_values={'tagRegionName01': 'Helos', 'tagMZoneGoM': 'Duister'})
    check('SD-2 fires on mislabelled restored zone (GoM->Duister)',
          has(C.contract_sd_tags(ctx2), 'MAP-SD-2'))


def test_refs():
    print('CONTRACT 7: PLACED REFS')
    sv_rec = b'records\\all_sv\\creature\\npc\\dyer\\test_dyer.dbr'
    blob = make_blob([(0x05, make_0x05([sv_rec]))])
    lv = {'fname': 'Levels/World/Greece/Town.lvl', '_blob': blob, 'guid': GUID_A}
    # compliant: record resolves
    ctx = FakeCtx(levels=[lv], _names={C.norm_rec(sv_rec)}, arz_names=set(), base_arz_names=set())
    check('REF compliant -> no violation', len(C.contract_placed_refs(ctx)) == 0)
    # broken: SV record does not resolve
    ctx_bad = FakeCtx(levels=[lv], _names=set(), arz_names=set(), base_arz_names=set())
    check('REF-1 fires on unresolved SV placed record', has(C.contract_placed_refs(ctx_bad), 'MAP-REF-1'))
    # a NON-SV unresolved record must NOT fire (base engine-tolerated, out of scope)
    base_rec = b'records\\creature\\pc\\base.dbr'
    blob_b = make_blob([(0x05, make_0x05([base_rec]))])
    lv_b = {'fname': 'Levels/World/Greece/Town.lvl', '_blob': blob_b, 'guid': GUID_A}
    ctx_b = FakeCtx(levels=[lv_b], _names=set(), arz_names=set(), base_arz_names=set())
    check('REF-1 does NOT fire on non-SV base record (scope guard)',
          not has(C.contract_placed_refs(ctx_b), 'MAP-REF-1'))


# ===========================================================================
def _cg_ctx(pool_fields, proxy_fields=None, insts=None, extra_names=()):
    """Build a FakeCtx for MAP-CHESTGUARD-1: one blood-cave level holding the chest
    + guard instances (make_0x05 zeroes positions, so they sit 0u apart = adjacent),
    an arz carrying the proxy/pool/monster/limits fields the contract reads."""
    chest = C.CHESTGUARD_CHEST.encode('latin-1')
    proxy = C.CHESTGUARD_PROXY.encode('latin-1')
    mon = C.CHESTGUARD_MONSTER
    pool = r'records\drxmap\proxy\pools\egg_blooddragon.dbr'
    lim = r'records\proxies orient\limit_bloodtoxeus.dbr'
    dbrs = insts if insts is not None else [chest, proxy]
    blob = make_blob([(0x05, make_0x05(dbrs))])
    lv = {'fname': 'Levels/World/xBloodCave/drxBC2.lvl', '_blob': blob, 'guid': GUID_A}
    f = {(C.CHESTGUARD_PROXY, 'pool1'): pool,
         (C.CHESTGUARD_PROXY, 'difficultyLimitsFile'): lim,
         (mon, 'charLevel'): [40, 68, 100],
         (lim, 'maxPlayerLevelEquationNormal'): '110 * 1',
         (lim, 'maxPlayerLevelEquationEpic'): '110 * 1',
         (lim, 'maxPlayerLevelEquationLegendary'): '110 * 1'}
    for k, val in (proxy_fields or {}).items():
        f[(C.CHESTGUARD_PROXY, k)] = val
    for k, val in pool_fields.items():
        f[(pool, k)] = val
    names = {C.norm_rec(x) for x in (chest, proxy, mon, pool, lim)} | set(extra_names)
    return FakeCtx(levels=[lv], arz=FakeArz(f), _names=names)


def test_chest_guard():
    print('CONTRACT 11: DEEP-CHEST DEVOURER GUARD')
    mon = C.CHESTGUARD_MONSTER
    dragon = r'records\drxcreatures\blooddragons\blooddragon01.dbr'
    # COMPLIANT = the b91 shipped shape: Devourer MAIN x3, 3 dragon champion escorts,
    # spawnMax 4 - championMax 3 = exactly 1 guaranteed Devourer, no pool equation.
    good = {'name1': mon, 'name2': mon, 'name3': mon,
            'weight1': 100, 'weight2': 100, 'weight3': 100,
            'nameChampion1': dragon, 'nameChampion2': dragon, 'nameChampion3': dragon,
            'spawnMin': 4, 'spawnMax': 4, 'championChance': 100.0,
            'championMin': 3, 'championMax': 3, 'proxyPoolEquation': ''}
    check('CHESTGUARD compliant (b91 shape) -> no violation',
          len(C.contract_chest_guard(_cg_ctx(good))) == 0)

    # BREAK 1 - THE ACTUAL b79/b91 DEFECT: the Devourer demoted to the sole champion
    # entry with championMin=championMax=1 (the shape that shipped and did not spawn).
    broken_shape = {'name1': dragon, 'name2': dragon, 'name3': dragon,
                    'weight1': 100, 'weight2': 100, 'weight3': 100,
                    'nameChampion1': mon, 'weightChampion1': 100,
                    'spawnMin': 4, 'spawnMax': 4, 'championChance': 100.0,
                    'championMin': 1, 'championMax': 1, 'proxyPoolEquation': ''}
    check('CHESTGUARD-1 fires when the Devourer is champion-only (the shipped defect)',
          has(C.contract_chest_guard(_cg_ctx(broken_shape)), 'MAP-CHESTGUARD-1'))

    # BREAK 2 - champion crowd-out: no main slot left for the boss.
    crowded = dict(good, championMin=4, championMax=4)
    check('CHESTGUARD-1 fires on champion crowd-out (0 guaranteed mains)',
          has(C.contract_chest_guard(_cg_ctx(crowded)), 'MAP-CHESTGUARD-1'))

    # BREAK 3 - duplicate Devourers (2 guaranteed mains).
    dup = dict(good, championMin=2, championMax=2)
    check('CHESTGUARD-1 fires on >1 guaranteed Devourer',
          has(C.contract_chest_guard(_cg_ctx(dup)), 'MAP-CHESTGUARD-1'))

    # BREAK 4 - the party-size rescaler is back, so the literal counts are fiction.
    eqd = dict(good, proxyPoolEquation=r'records\proxies orient\proxypoolequation_02.dbr')
    check('CHESTGUARD-1 fires when proxyPoolEquation is not neutralized',
          has(C.contract_chest_guard(_cg_ctx(eqd)), 'MAP-CHESTGUARD-1'))

    # BREAK 5 - the guard proxy is not placed at all (b79 map-lane class).
    chest_only = [C.CHESTGUARD_CHEST.encode('latin-1')]
    check('CHESTGUARD-1 fires when the guard proxy is not placed',
          has(C.contract_chest_guard(_cg_ctx(good, insts=chest_only)), 'MAP-CHESTGUARD-1'))

    # BREAK 6 - the area-trash limit window that dilutes the level-100 superboss.
    trash = r'records\proxies orient\limit_area002.dbr'
    ctx = _cg_ctx(good, proxy_fields={'difficultyLimitsFile': trash},
                  extra_names={C.norm_rec(trash)})
    ctx.arz._f[(trash, 'maxPlayerLevelEquationNormal')] = '26 * 1'
    ctx.arz._f[(trash, 'maxPlayerLevelEquationEpic')] = '51 * 1'
    ctx.arz._f[(trash, 'maxPlayerLevelEquationLegendary')] = '65 * 1'
    check('CHESTGUARD-1 fires on a limit window below the Devourer charLevel',
          has(C.contract_chest_guard(ctx), 'MAP-CHESTGUARD-1'))


if __name__ == '__main__':
    for t in (test_quests, test_portals, test_navmesh, test_groups, test_doors, test_sd, test_refs,
              test_chest_guard):
        t()
    npass = sum(1 for _n, ok, _d in RESULTS if ok)
    print(f'\n{npass}/{len(RESULTS)} checks PASS')
    sys.exit(0 if npass == len(RESULTS) else 1)
