#!/usr/bin/env python3
"""GATE: every placed strategic-movement DEVICE must be GROUPS-bound (M13a, 2026-07-10).

The forward-direction per-instance check the old contract missed (contracts_map
MAP-GROUPS-1 only flags a WHOLLY dead group; a single unbound device among many bound
ones shipped invisibly - the exact class behind the dead Tower-of-Judgement respawn,
the Lower-Olympus trophy and the Olympus rift shrine; docs/DEAD_CONTENT_AUDIT_2026-07-10.md
Lane B).

CONTRACT: for every 0x05 instance with flags != 0 (uid-tracked) whose record Class is
  StrategicMovementRespawnShrine  -> uid must be a member of a GROUPS record with
                                     category 'RespawnShrine'
  StrategicMovementTeleportShrine -> category 'TeleportShrine'
(uid membership = the 16-byte UniqueId appears as a member payload head in a record of
the right category; member layout uid(16)+levelGUID(16)+pos(12), tail-tolerant scan).

Also asserts the Lane-B must-bind uids (imported from svaera_plus_portals.M13A_MUST_BIND).
Inverse danglers (members without a placed instance) are reported informationally only -
the base game ships ~60 of them and they are harmless (Lane B).

Exit 0 = PASS, 1 = FAIL. Usage:
  py tools/verify_groups_bindings.py [--map local/Levels_merged.arc]
"""
import sys
import struct
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS
from svaera_plus_portals import _parse_groups, M13A_MUST_BIND
from arz_lookup import load_arz

DEVICE_CLASSES = {
    'StrategicMovementRespawnShrine': 'RespawnShrine',
    'StrategicMovementTeleportShrine': 'TeleportShrine',
}
BASE_ARZ = Path(r'C:/Program Files (x86)/Steam/steamapps/common/'
                r'Titan Quest Anniversary Edition/Database/database.arz')
MOD_ARZ = REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'


def class_index():
    """record path (lowercase, backslash) -> Class. The .arz record 'type' field IS the
    Class string (audit Lane A discovery), so no payload decode is needed."""
    idx = {}
    for arz in (BASE_ARZ, MOD_ARZ):          # mod second: mod overrides base
        if not arz.exists():
            print(f'  !! arz missing: {arz}')
            continue
        _, _, records = load_arz(str(arz))
        for k, rec in records.items():
            idx[k.replace('/', '\\')] = rec['type']
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    args = ap.parse_args()

    print(f'=== GATE verify_groups_bindings: {args.map} ===')
    arc = ArcArchive.from_file(Path(args.map))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, secs[SEC_LEVELS])
    graw = data[secs[SEC_GROUPS]['data_offset']:
                secs[SEC_GROUPS]['data_offset'] + secs[SEC_GROUPS]['size']]
    _, grecs = _parse_groups(graw)

    # category -> set of member uids (tail-tolerant: first member_count*44 bytes are members)
    members_by_cat = {}
    for r in grecs:
        cat = r['category']
        s = members_by_cat.setdefault(cat, set())
        raw = r['raw_data']
        for i in range(r['member_count']):
            if (i + 1) * 44 > len(raw):
                break
            s.add(raw[i * 44:i * 44 + 16])

    print('  building arz Class index...')
    cls = class_index()

    checked = bound = 0
    dead = []
    placed_uids = set()
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if len(blob) < 4 or blob[:3] != b'LVL':
            continue
        ver = blob[3]
        base = 72 if ver in (0x11, 0x0f) else 56
        # walk sections for 0x05
        pos = 4
        d05 = None
        while pos + 8 <= len(blob):
            st = struct.unpack_from('<I', blob, pos)[0]
            ss = struct.unpack_from('<I', blob, pos + 4)[0]
            if ss > len(blob) - pos - 8:
                break
            if st == 0x05:
                d05 = blob[pos + 8:pos + 8 + ss]
                break
            pos += 8 + ss
        if d05 is None:
            continue
        scount = struct.unpack_from('<I', d05, 0)[0]
        p = 4
        strings = []
        for _ in range(scount):
            sl = struct.unpack_from('<I', d05, p)[0]
            p += 4
            strings.append(d05[p:p + sl])
            p += sl
        icount = struct.unpack_from('<I', d05, p)[0]
        p += 4
        q = p
        for _ in range(icount):
            if q + base > len(d05):
                break
            sidx = struct.unpack_from('<I', d05, q)[0]
            flags = struct.unpack_from('<I', d05, q + 52)[0]
            rs = base + (16 if flags != 0 else 0)
            if flags != 0:
                uid = d05[q + 56:q + 72]
                placed_uids.add(uid)
                dbr = (strings[sidx] if sidx < len(strings) else b'').decode(
                    'latin-1').replace('/', '\\').lower()
                klass = cls.get(dbr)
                if klass in DEVICE_CLASSES:
                    checked += 1
                    cat = DEVICE_CLASSES[klass]
                    if uid in members_by_cat.get(cat, set()):
                        bound += 1
                    else:
                        dead.append((lv['fname'], dbr.split('\\')[-1], uid.hex(), klass))
            q += rs

    print(f'  devices checked: {checked}; bound: {bound}; DEAD: {len(dead)}')
    fail = False
    for fname, rec, uid, klass in dead:
        print(f'  !! DEAD DEVICE: {rec} ({klass}) uid={uid[:16]}.. in {fname}')
        fail = True

    # Lane-B must-bind uids
    for uid_hex, cat, why in M13A_MUST_BIND:
        ok = bytes.fromhex(uid_hex) in members_by_cat.get(cat, set())
        print(f'  must-bind {uid_hex[:12]}.. [{cat}]: {"OK" if ok else "MISSING"}  ({why.split("(")[0].strip()})')
        if not ok:
            fail = True

    # informational: inverse danglers among shrine categories (harmless, base ships ~60)
    for cat in ('RespawnShrine', 'TeleportShrine'):
        m = members_by_cat.get(cat, set())
        dang = sum(1 for u in m if u not in placed_uids)
        print(f'  info: {cat} members={len(m)} inverse-danglers(no placed instance)={dang} (harmless)')

    print(f'RESULT: {"FAIL" if fail else "PASS"}')
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
