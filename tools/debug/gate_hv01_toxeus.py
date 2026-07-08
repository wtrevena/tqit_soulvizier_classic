#!/usr/bin/env python3
r"""GATE: the lone Toxeus proxy placed OUTSIDE the blood-cave mouth in HiddenValley01, TESTHUB-only.

Verbatim to the task's GATES:
  (1) entity present in the REBUILT TESTHUB at intended coords, byte-shape exemplar-matched
      (flags=0, v0x11 72B, no 0x14, rot == Q_LEINTH_EXEMPLAR_ROT); proxy->pool->monster chain
      resolves in the deployed arz (delegated to gate_toxeus_chain.py).
  (2) on-mesh 0.000-0.5u + ALL distances listed (friendlies >=25u; mouth + beastman for design).
  (3) containment: canonical BYTE-IDENTICAL to build26 (md5 3f1b2e4d..); TESTHUB diff vs its
      build26 ref = EXACTLY HV01's 0x05 (+1 instance, +0x14 only if exemplar demands -> it does NOT).
  (4) full re-parse 0 malformed (delegated to a full parse); this gate proves HV01 parses clean.

Read-only. No em dashes.
Usage: py tools/debug/gate_hv01_toxeus.py
"""
import sys, struct, math, hashlib
from pathlib import Path

REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
import build_section_surgery as bss
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from diag_bugs import load_map, get_level_blob, parse_blob_sections, parse_0x05, walk_instances
from rec02_format import parse_rec02
from navlib import Mesh

CANON = REPO / 'local' / 'Levels_merged.arc'
HUB = REPO / 'local' / 'Levels_merged_TESTHUB.arc'
HUB_REF = REPO / 'local' / 'Levels_merged_TESTHUB.build26-ref.arc'
HV01_KEY = 'levels/world/orient/silkroad/hiddenvalley01.lvl'
CANON_BUILD26_MD5 = '3f1b2e4d43a856f4df067f8f023da365'
TOXEUS_DBR = r'records\drxmap\proxy\q_bloodtoxeus_lone.dbr'.lower()
MOUTH = (14.0, 18.0, 26.0)
EXEMPLAR_ROT = bss.Q_LEINTH_EXEMPLAR_ROT
FRIENDLY_NEEDLES = ['respawntempleorient', 'caravan', 'fog_occult', 'occultistaura',
                    'disciple_aura', 'merchant', 'occulttent', 'vendor',
                    'npc\\speaking', 'npc/speaking', 'villager', 'storyteller',
                    'pitspawner', 'lildude', 'pitsprite', 'olympianarena', 'campfire', 'totem']
BEASTMAN_NEEDLES = ['beastman', 'neanderthal', 'encact']
PASS = 'PASS'; FAIL = 'FAIL'


def md5(p):
    h = hashlib.md5()
    h.update(Path(p).read_bytes())
    return h.hexdigest()


def load_hv(arc):
    data, _ = load_map(arc)
    secs = parse_sections(data)
    levels = parse_level_index(data, next(s for s in secs if s['type'] == SEC_LEVELS))
    lv = next(l for l in levels if l['fname'].replace('\\', '/').lower() == HV01_KEY)
    ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
    corner = (ints[6], ints[7], ints[8])
    blob = get_level_blob(data, levels, None, lv)
    return data, blob, corner


def parse_0x14_map(blob):
    secs, _ = parse_blob_sections(blob)
    out = {}
    for s in secs:
        if s['type'] == 0x14:
            d = s['data']; pos = 0
            while pos + 8 <= len(d):
                idx = struct.unpack_from('<I', d, pos)[0]
                psz = struct.unpack_from('<I', d, pos + 4)[0]
                out[idx] = d[pos + 8:pos + 8 + psz]
                pos += 8 + psz
    return out


def full_insts(blob, corner):
    secs, magic = parse_blob_sections(blob)
    sec05 = next(s for s in secs if s['type'] == 0x05)
    data = sec05['data']
    strings, instmeta = parse_0x05(data)
    insts, endpos, dlen = walk_instances(magic, strings, instmeta)
    for it in insts:
        it['wx'] = corner[0] + it['x']; it['wy'] = corner[1] + it['y']; it['wz'] = corner[2] + it['z']
        # rotation 3x3 is at record offset +4 (after the 4-byte string_index).
        it['rot'] = struct.unpack_from('<9f', data, it['off'] + 4)
    return insts, magic, (endpos, dlen)


def gate1_present_and_shape():
    print('=== GATE 1: entity present + byte-shape exemplar-matched (TESTHUB) ===')
    data, blob, corner = load_hv(HUB)
    insts, magic, (endpos, dlen) = full_insts(blob, corner)
    x14 = parse_0x14_map(blob)
    tox = [it for it in insts if it['dbr'].lower() == TOXEUS_DBR]
    ok = True
    print(f'  HV01 blob v0x{magic[3]:02x}, {len(insts)} instances, 0x05 trailing={dlen-endpos}')
    if len(tox) != 1:
        print(f'  FAIL: expected exactly 1 Toxeus proxy, found {len(tox)}'); return False
    it = tox[0]
    exp_local = bss._TOXEUS_HV01_LOCAL
    at_coord = (abs(it['x'] - exp_local[0]) < 1e-3 and abs(it['y'] - exp_local[1]) < 1e-3
                and abs(it['z'] - exp_local[2]) < 1e-3)
    rot_ok = all(abs(it['rot'][i] - EXEMPLAR_ROT[i]) < 1e-6 for i in range(9))
    flags_ok = (it['flags'] == 0)
    size_ok = (it['size'] == 72)  # v0x11 unflagged
    no_14 = (it['i'] not in x14)
    is_last = (it['i'] == len(insts) - 1)  # appended at the tail
    print(f'  instance idx={it["i"]} (last={is_last})  dbr={it["dbr"]}')
    print(f'  local=({it["x"]:.3f},{it["y"]:.3f},{it["z"]:.3f}) world=({it["wx"]:.2f},{it["wy"]:.2f},{it["wz"]:.2f})')
    print(f'  at intended coord {exp_local}: {at_coord}')
    print(f'  flags==0: {flags_ok}   record size==72 (v0x11 unflagged): {size_ok}')
    print(f'  rot == Q_LEINTH_EXEMPLAR_ROT: {rot_ok}')
    print(f'  NO 0x14 entry (exemplar-faithful): {no_14}')
    ok = at_coord and rot_ok and flags_ok and size_ok and no_14
    print(f'  GATE 1: {PASS if ok else FAIL}')
    return ok


def gate2_onmesh_and_distances():
    print('=== GATE 2: on-mesh 0.000-0.5u + ALL distances ===')
    data, blob, corner = load_hv(HUB)
    insts, magic, _ = full_insts(blob, corner)
    it = next(i for i in insts if i['dbr'].lower() == TOXEUS_DBR)
    spawn = (it['wx'], it['wy'], it['wz'])

    secs, _ = parse_blob_sections(blob)
    nav = next(s for s in secs if s['type'] == 0x0b)
    mesh = Mesh(parse_rec02(nav['data'], decompress=True), name='HV01')
    largest = set(mesh.components()[0])

    gx, gz = mesh.gx(spawn[0]), mesh.gz(spawn[2])
    best = None
    for dz in range(-25, 26):
        for dx in range(-25, 26):
            c = (gx + dx, gz + dz)
            if c in mesh.cells:
                cwx, cwz = mesh.wx(c[0]), mesh.wz(c[1])
                cwy = mesh.wy(mesh.cells[c][0])
                dd = math.hypot(cwx - spawn[0], cwz - spawn[2])
                if best is None or dd < best[0]:
                    best = (dd, cwy - spawn[1], c)
    d2d, dY, cell = best
    in_l = cell in largest
    onmesh_ok = (d2d <= 0.5 and abs(dY) <= 0.5 and in_l)
    print(f'  spawn world=({spawn[0]:.2f},{spawn[1]:.2f},{spawn[2]:.2f}) '
          f'local=({it["x"]:.2f},{it["y"]:.2f},{it["z"]:.2f})')
    print(f'  nearest walkable d2d={d2d:.3f}u  dY={dY:+.3f}u  in_largest_comp={in_l}  '
          f'area={mesh.cells[cell][1]}')
    print(f'  on-mesh gate (d2d<=0.5, |dY|<=0.5, largest-comp): {onmesh_ok}')

    def d2(i):
        return math.hypot(i['wx'] - spawn[0], i['wz'] - spawn[2])

    mouth_w = (corner[0] + MOUTH[0], corner[2] + MOUTH[2])
    dmouth = math.hypot(mouth_w[0] - spawn[0], mouth_w[1] - spawn[2])
    print(f'\n  DISTANCE to cave mouth (14,18,26): {dmouth:.2f}u  '
          f'(player exiting/approaching meets him)')

    print('\n  FRIENDLY scenery/NPC distances (gate: ALL >= 25u):')
    friendlies = [i for i in insts if any(n in i['dbr'].lower() for n in FRIENDLY_NEEDLES)]
    worst = 1e9
    for i in sorted(friendlies, key=d2):
        dv = d2(i); worst = min(worst, dv)
        print(f'    d2d={dv:8.2f}u  [{("OK" if dv >= 25 else "VIOLATION")}]  '
              f'local=({i["x"]:.2f},{i["y"]:.2f},{i["z"]:.2f})  {i["dbr"]}')
    friendly_ok = worst >= 25.0
    print(f'    MIN friendly distance = {worst:.2f}u  gate(>=25u): {friendly_ok}')

    print('\n  Nearest hostile beastman proxies (design context, not a gate):')
    hostiles = [i for i in insts if any(n in i['dbr'].lower() for n in BEASTMAN_NEEDLES)]
    for i in sorted(hostiles, key=d2)[:4]:
        print(f'    d2d={d2(i):8.2f}u  local=({i["x"]:.2f},{i["y"]:.2f},{i["z"]:.2f})  {i["dbr"]}')

    ok = onmesh_ok and friendly_ok
    print(f'  GATE 2: {PASS if ok else FAIL}')
    return ok


def gate3_containment():
    print('=== GATE 3: containment (canonical byte-identical + TESTHUB diff = HV01 0x05 +1) ===')
    ok = True
    # 3a canonical md5
    cm = md5(CANON)
    a = (cm == CANON_BUILD26_MD5)
    print(f'  canonical md5 = {cm}  == build26 {CANON_BUILD26_MD5}: {a}')
    ok = ok and a

    # 3b TESTHUB diff vs build26 ref: EXACTLY HV01 blob differs, +1 0x05 instance (Toxeus), no
    # top-level section changes, every OTHER blob byte-identical.
    if not HUB_REF.exists():
        print(f'  TESTHUB build26 ref missing ({HUB_REF}) - cannot diff'); return False
    d_new, _ = load_map(HUB)
    d_ref, _ = load_map(HUB_REF)
    s_new = parse_sections(d_new); s_ref = parse_sections(d_ref)
    lv_new = parse_level_index(d_new, next(s for s in s_new if s['type'] == SEC_LEVELS))
    lv_ref = parse_level_index(d_ref, next(s for s in s_ref if s['type'] == SEC_LEVELS))

    def bm(data, levels):
        return {l['fname'].replace('\\', '/').lower():
                get_level_blob(data, levels, None, l) for l in levels}
    b_new = bm(d_new, lv_new); b_ref = bm(d_ref, lv_ref)

    def sec_bytes(data, secs, t):
        for s in secs:
            if s['type'] == t:
                return data[s['data_offset']:s['data_offset'] + s['size']]
        return b''
    for t, nm in [(0x11, 'GROUPS'), (0x18, 'SD'), (0x1b, 'QUESTS'), (0x19, 'BITMAPS')]:
        same = sec_bytes(d_new, s_new, t) == sec_bytes(d_ref, s_ref, t)
        print(f'  section {nm}: identical new-vs-ref = {same}')
        ok = ok and same

    changed = [k for k in set(b_new) | set(b_ref) if b_new.get(k) != b_ref.get(k)]
    print(f'  CHANGED blobs new-vs-build26ref: {len(changed)} -> {changed}')
    only_hv = (changed == [HV01_KEY])
    ok = ok and only_hv
    if HV01_KEY in b_new and HV01_KEY in b_ref:
        _, corner = None, None
        lv = next(l for l in lv_new if l['fname'].replace('\\', '/').lower() == HV01_KEY)
        ints = struct.unpack_from('<13i', lv['ints_raw'], 0); corner = (ints[6], ints[7], ints[8])
        i_new, _, _ = full_insts(b_new[HV01_KEY], corner)
        i_ref, _, _ = full_insts(b_ref[HV01_KEY], corner)
        added = len(i_new) - len(i_ref)
        # prefix check: ref instances are a byte-shape prefix of new
        prefix_ok = True
        for a2, b2 in zip(i_ref, i_new):
            if a2['dbr'] != b2['dbr'] or abs(a2['x'] - b2['x']) > 1e-4 or abs(a2['z'] - b2['z']) > 1e-4:
                prefix_ok = False; break
        added_is_toxeus = (added == 1 and i_new[-1]['dbr'].lower() == TOXEUS_DBR)
        # 0x14 count unchanged (no 0x14 appended)
        x_new = parse_0x14_map(b_new[HV01_KEY]); x_ref = parse_0x14_map(b_ref[HV01_KEY])
        x14_same = (len(x_new) == len(x_ref))
        print(f'  HV01 0x05 instances: ref={len(i_ref)} new={len(i_new)} (+{added})  '
              f'prefix_preserved={prefix_ok}  added_is_toxeus={added_is_toxeus}')
        print(f'  HV01 0x14 entries: ref={len(x_ref)} new={len(x_new)} unchanged={x14_same} '
              f'(exemplar demands NO 0x14)')
        ok = ok and prefix_ok and added_is_toxeus and x14_same
    print(f'  only HV01 blob changed: {only_hv}')
    print(f'  GATE 3: {PASS if ok else FAIL}')
    return ok


def gate4_hv01_parses():
    print('=== GATE 4: HV01 parses clean in both artifacts ===')
    ok = True
    for arc, nm in [(CANON, 'canonical'), (HUB, 'TESTHUB')]:
        data, blob, corner = load_hv(arc)
        try:
            insts, magic, (endpos, dlen) = full_insts(blob, corner)
            trailing = dlen - endpos
            clean = (magic[:3] == b'LVL' and trailing == 0)
            print(f'  {nm}: v0x{magic[3]:02x}, {len(insts)} insts, 0x05 trailing={trailing}, clean={clean}')
            ok = ok and clean
        except Exception as e:
            print(f'  {nm}: PARSE ERROR {e}'); ok = False
    print(f'  GATE 4: {PASS if ok else FAIL}')
    return ok


if __name__ == '__main__':
    r1 = gate1_present_and_shape(); print()
    r2 = gate2_onmesh_and_distances(); print()
    r3 = gate3_containment(); print()
    r4 = gate4_hv01_parses(); print()
    print('===== TOXEUS GATE SUMMARY =====')
    for nm, r in [('1 present+shape', r1), ('2 onmesh+dist', r2),
                  ('3 containment', r3), ('4 parse', r4)]:
        print(f'  gate {nm}: {PASS if r else FAIL}')
    sys.exit(0 if all([r1, r2, r3, r4]) else 1)
