#!/usr/bin/env python3
r"""MAP-NAV-4 standalone gate: blood-cave respawn-chamber navmesh isolated-load safety.

THE CRASH (runtime-proven, 2026-07-17 Frida probe; docs/reports/b87_bloodcave_navok_rca.md)
--------------------------------------------------------------------------------------------
A blood-cave chamber that hosts a StrategicMovementRespawnShrine is a SAVE / RESPAWN
point: the engine loads the player's current level in ISOLATION on a fresh save-load or
a death-respawn, BEFORE its grid-neighbour levels stream in. If that chamber's 0x0b
navmesh is MULTI-GUID (own + grid-seam neighbours), ProcessRLTD's live-residency gate
(Engine 0x101f4ba0: for every listed GUID, [reg+0x50][idx] must be a stream-RESIDENT
region, not merely resolve in the world GUID map) cannot complete - the neighbours are
not resident - so the navmesh load fails (Level+0x6a48 stays 0) and the region code
dereferences the absent navmesh (Engine RVA 0x20e270, EDI=0) = the deterministic
near-null 0xc0000005. The probe pinned this at new_secretdoor_transitionhallway
(respawn_hadescave01), ENTER-with-no-LEAVE, navOK=0, resident-alone.

Static GUID resolution (MAP-NAV-1) is GREEN - every listed GUID resolves in the LEVELS
index of BOTH map variants. This gate covers the RESIDENCY half MAP-NAV-1 cannot see.

INVARIANT: every blood-cave chamber that hosts a StrategicMovementRespawnShrine must
carry a single-own-GUID navmesh (guid_count == 1, always resident on isolated load).

RUNTIME PARITY: run against BOTH the canonical (Steam) and TESTHUB arc - the crash
chamber is byte-identical in both, so both are affected.

Usage:
  py tools/contracts/gate_navmesh_coresidency.py <Levels.arc> <mod.arz> --base "<game>/Database/database.arz"
  py tools/contracts/gate_navmesh_coresidency.py --negtest   # planted-condition self-test (no args)
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections
import contracts_map as _cm

RESPAWN_SHRINE_CLASS = 'StrategicMovementRespawnShrine'
BLOODCAVE_SUBSTRINGS = ('xbloodcave', 'bloodcave')
import re
_DBR_RE = re.compile(rb'records[\\/][!-~]*?\.dbr', re.IGNORECASE)


def _norm(p):
    if isinstance(p, bytes):
        p = p.decode('latin-1')
    return p.replace('/', '\\').strip().lower()


def load_class_map(*arz_paths):
    """norm-record -> class for the union of the given arz files (uses the proven
    contracts_map Arz reader)."""
    cls = {}
    for ap in arz_paths:
        if not ap or not Path(ap).exists():
            continue
        arz = _cm.Arz.from_arz(Path(ap))
        for name, t in arz.record_class().items():
            cls[_norm(name)] = t
    return cls


def load_levels(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    world = [e for e in arc.entries if e.entry_type == 3][0]
    data = arc.decompress(world)
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    return data, levels


def scan(data, levels, cls_map, level_guids):
    """Return (violations, checked_chambers). A violation = a blood-cave respawn
    chamber whose 0x0b navmesh has guid_count > 1."""
    viols = []
    checked = 0
    for lv in levels:
        fn = lv['fname'].replace('\\', '/').lower()
        if not any(s in fn for s in BLOODCAVE_SUBSTRINGS):
            continue
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        shrines = sorted({_norm(m.group(0)) for m in _DBR_RE.finditer(blob)
                          if cls_map.get(_norm(m.group(0))) == RESPAWN_SHRINE_CLASS})
        if not shrines:
            continue
        checked += 1
        secs, _magic = parse_blob_sections(blob)
        d0b = next((s['data'] for s in secs if s['type'] == 0x0b), None)
        if not d0b or d0b[:4] != b'REC\x02':
            continue
        gc = struct.unpack_from('<I', d0b, 12)[0]
        own = lv['ints_raw'][36:52]
        guids = [d0b[16 + i * 16:16 + (i + 1) * 16] for i in range(gc)]
        # runtime parity: every listed GUID must resolve in the LEVELS index
        unresolved = [g.hex()[:8] for g in guids if g not in level_guids]
        if gc > 1 or unresolved:
            nbrs = [g.hex()[:8] for g in guids if g != own]
            viols.append({
                'level': lv['fname'], 'shrines': shrines, 'guid_count': gc,
                'neighbours': nbrs, 'unresolved': unresolved,
            })
    return viols, checked


def run_gate(arc_path, mod_arz, base_arz):
    data, levels = load_levels(arc_path)
    level_guids = set(lv['ints_raw'][36:52] for lv in levels)
    cls_map = load_class_map(mod_arz, base_arz)
    viols, checked = scan(data, levels, cls_map, level_guids)
    print(f'=== MAP-NAV-4 gate: {Path(arc_path).name} ===')
    print(f'  respawn-shrine blood-cave chambers checked: {checked}')
    if not viols:
        print('  PASS: every respawn/save chamber has an isolated-load-safe (single-GUID) navmesh.')
        return 0
    print(f'  FAIL ({len(viols)}): respawn chamber(s) with a co-residency-unsafe navmesh:')
    for v in viols:
        extra = f' UNRESOLVED={v["unresolved"]}' if v['unresolved'] else ''
        print(f'    {v["level"]}: shrine={v["shrines"]} guid_count={v["guid_count"]} '
              f'neighbour-deps={v["neighbours"]}{extra}')
    return 1


def negtest():
    """Planted-condition self-test: prove the gate's classifier catches the exact
    crash condition (respawn shrine + multi-GUID) and clears the safe one."""
    print('=== MAP-NAV-4 planted negative test ===')
    # Minimal synthetic REC\x02: header + guid_count + N*16 guid bytes + 24 pad.
    def rec02(n):
        body = b'REC\x02' + struct.pack('<3I', 1, 0, n) + b'\x11' * (n * 16) + b'\x00' * 24
        return body[:8] + struct.pack('<I', len(body) - 12) + body[12:]
    OWN = b'\x11' * 16
    cls_map = {r'records\drx\respawn.dbr': RESPAWN_SHRINE_CLASS,
               r'records\drx\torch.dbr': 'Decoration'}

    def mk(dbr_refs, guid_count):
        # blob layout parse_blob_sections expects: 4-byte magic + [type(4) size(4) data].
        recs = b''.join(r.encode('latin-1') + b'\x00' for r in dbr_refs)
        nav = rec02(guid_count)
        blob = (b'LVL\x00' +
                b'\x05\x00\x00\x00' + struct.pack('<I', len(recs)) + recs +
                b'\x0b\x00\x00\x00' + struct.pack('<I', len(nav)) + nav)
        ints = b'\x00' * 36 + OWN
        return blob, {'fname': r'levels\world\xbloodcave\synth.lvl', 'ints_raw': ints,
                      'data_offset': 0, 'data_length': len(blob)}

    ok = True
    # Case A: respawn shrine + MULTI-GUID (gc=3) -> MUST flag (the crash condition)
    blob, lv = mk([r'records\drx\respawn.dbr'], 3)
    viols, checked = scan(blob, [lv], cls_map, {OWN, b'\x11' * 16})
    hit = len(viols) == 1 and viols[0]['guid_count'] == 3
    print(f'  A respawn+multiGUID(3): {"FLAGGED (correct)" if hit else "MISSED (BUG)"}')
    ok &= hit
    # Case B: respawn shrine + SINGLE-GUID (gc=1) -> MUST clear (the fixed condition)
    blob, lv = mk([r'records\drx\respawn.dbr'], 1)
    viols, checked = scan(blob, [lv], cls_map, {OWN})
    clear = len(viols) == 0 and checked == 1
    print(f'  B respawn+singleGUID(1): {"CLEAR (correct)" if clear else "FLAGGED (BUG)"}')
    ok &= clear
    # Case C: NO shrine + MULTI-GUID (gc=4) -> not a respawn chamber, MUST clear
    blob, lv = mk([r'records\drx\torch.dbr'], 4)
    viols, checked = scan(blob, [lv], cls_map, {OWN, b'\x11' * 16})
    clear = len(viols) == 0 and checked == 0
    print(f'  C no-shrine+multiGUID(4): {"CLEAR (correct)" if clear else "FLAGGED (BUG)"}')
    ok &= clear
    print('  NEGTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('levels_arc', nargs='?')
    ap.add_argument('mod_arz', nargs='?')
    ap.add_argument('--base', default=None)
    ap.add_argument('--negtest', action='store_true')
    a = ap.parse_args()
    if a.negtest:
        sys.exit(negtest())
    if not a.levels_arc or not a.mod_arz:
        ap.error('need <Levels.arc> <mod.arz> (or --negtest)')
    sys.exit(run_gate(a.levels_arc, a.mod_arz, a.base))


if __name__ == '__main__':
    main()
