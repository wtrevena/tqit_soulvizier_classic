#!/usr/bin/env python3
"""Negative tests for contracts_map.py.

For each contract: build a COMPLIANT synthetic input (assert no target violation),
then surgically BREAK it (assert the contract fires the expected violation). Proves
each check actually detects the defect it claims to. Run:
  python tools/contracts/_negtest_map.py
Exits 0 if every contract's negative test PASSES, 1 otherwise. Self-contained
(builds tiny in-memory map/blob/arz structures; no big artifacts needed)."""
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


def make_rec02(guid, version=1):
    """Minimal valid REC\\x02 container header (enough for rec02_header)."""
    body = struct.pack('<I', 1)                       # guid_count = 1
    body += guid                                       # 16B guid
    body += struct.pack('<3i', 0, 0, 0)                # center
    body += struct.pack('<3I', 100, 0, 100)            # dims
    total = bytearray(b'REC\x02' + struct.pack('<II', version, 0) + body)
    struct.pack_into('<I', total, 8, len(total) - 12)  # payload_size = total-12
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
    # use the REAL baseline Quests.arc (has UnlockFixedItem refs); place a fake SV
    # door that is/ isn't referenced.
    base = Path(r'C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos'
                r'\55f6c1cb-5e9b-466b-a25d-f3fb1a0c56a8\scratchpad\contracts_baseline')
    qa = str(base / 'Quests.arc')
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


if __name__ == '__main__':
    for t in (test_quests, test_portals, test_navmesh, test_groups, test_doors, test_sd, test_refs):
        t()
    npass = sum(1 for _n, ok, _d in RESULTS if ok)
    print(f'\n{npass}/{len(RESULTS)} checks PASS')
    sys.exit(0 if npass == len(RESULTS) else 1)
