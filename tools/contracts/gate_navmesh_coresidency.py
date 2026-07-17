#!/usr/bin/env python3
r"""MAP-NAV-4 standalone gate: SV-custom respawn-chamber navmesh isolated-load safety.

THE CRASH (runtime-proven, 2026-07-17 Frida probe; docs/reports/b87_bloodcave_navok_rca.md)
--------------------------------------------------------------------------------------------
An SV-CUSTOM level that hosts a StrategicMovementRespawnShrine is a SAVE / RESPAWN
point: the engine loads the player's current level in ISOLATION on a fresh save-load
or a death-respawn, BEFORE its grid-neighbour levels stream in. If that chamber's
0x0b navmesh is MULTI-GUID (own + grid-seam neighbours), ProcessRLTD's live-residency
gate (Engine 0x101f4ba0: for every listed GUID, [reg+0x50][idx] must be a stream-
RESIDENT region, not merely resolve in the world GUID map) cannot complete - the
neighbours are not resident - so the navmesh load fails (Level+0x6a48 stays 0) and
the region code dereferences the absent navmesh (Engine RVA 0x20e270, EDI=0) = the
deterministic near-null 0xc0000005. The probe pinned this at
new_secretdoor_transitionhallway (respawn_hadescave01), ENTER-with-no-LEAVE, navOK=0,
resident-alone.

WHY "SV-CUSTOM" IS THE DISCRIMINATOR (not "respawn + multi-GUID")
----------------------------------------------------------------
The stock game ships 264 respawn chambers with multi-GUID navmeshes (DelphiTownStart
gc=12, Memphis gc=13, Utgard, ...) that save/reload fine, because a base region keeps
its navmesh-neighbour levels CO-RESIDENT (region-packed). The SV blood-cave /
secret-place clusters are grid-shifted into empty world space with offline-generated
navmeshes, so their neighbours are NOT co-resident on an isolated respawn. Provenance
by own level GUID cleanly separates the two: a base/IT/XPack level's GUID is present
in the stock TQAE Levels.arc index; an SV-custom level's is not. This excludes the
byte-identical Silk Road HiddenValley01 spawn hub (a false positive) name-free and
surfaces exactly the SV-custom respawn chambers our pipeline generates.

Static GUID resolution (MAP-NAV-1) is GREEN - every listed GUID resolves in the LEVELS
index of BOTH map variants. This gate covers the RESIDENCY half MAP-NAV-1 cannot see,
and shares its classifier (contracts_map.scan_isolated_load_risk) with the battery
contract contract_navmesh_coresidency so their scope can never drift apart.

RUNTIME PARITY: run against BOTH the canonical (Steam) and TESTHUB arc - the crash
chamber is byte-identical in both, so both are affected.

Usage:
  py tools/contracts/gate_navmesh_coresidency.py <Levels.arc> <mod.arz> --base "<game>/Database/database.arz"
      (base level provenance is read from <game>/Resources/Levels.arc, derived from --base)
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
import contracts_map as _cm

RESPAWN_SHRINE_CLASS = _cm.RESPAWN_SHRINE_CLASS


def _norm(p):
    if isinstance(p, bytes):
        p = p.decode('latin-1')
    return p.replace('/', '\\').strip().lower()


def load_class_map(*arz_paths):
    """norm-record -> class for the union of the given arz files."""
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


def base_level_guids(base_arz_path):
    """Own-GUID set of every level in the stock base-game Levels.arc, derived from
    the --base database.arz path (<game>/Database/database.arz -> ../Resources/Levels.arc)."""
    if not base_arz_path:
        return set()
    blv = Path(base_arz_path).resolve().parent.parent / 'Resources' / 'Levels.arc'
    if not blv.exists():
        return set()
    _bdata, blevels = load_levels(blv)
    return set(lv['ints_raw'][36:52] for lv in blevels)


def scan(data, levels, cls_map, base_guids):
    """Flag SV-custom (own GUID absent from stock) respawn chambers with a multi-GUID
    navmesh. Delegates to the SHARED classifier so this gate and the battery contract
    stay in lock-step. Returns (violations, checked_chambers)."""
    def blob_of(lv):
        return data[lv['data_offset']:lv['data_offset'] + lv['data_length']]

    # normalise the level dicts to the shape scan_isolated_load_risk expects
    # (merge_levels_binary uses ints_raw[36:52] as the own-GUID; contracts_map uses lv['guid'])
    norm_levels = []
    for lv in levels:
        d = dict(lv)
        d['guid'] = lv['ints_raw'][36:52]
        norm_levels.append(d)

    checked = 0
    for lv in norm_levels:
        blob = blob_of(lv)
        if _cm._respawn_shrines_in_blob(cls_map.get, blob) and lv['guid'] not in base_guids:
            checked += 1
    viols = _cm.scan_isolated_load_risk(norm_levels, blob_of, cls_map.get, base_guids)
    return viols, checked


def run_gate(arc_path, mod_arz, base_arz):
    data, levels = load_levels(arc_path)
    cls_map = load_class_map(mod_arz, base_arz)
    base_guids = base_level_guids(base_arz)
    print(f'=== MAP-NAV-4 gate: {Path(arc_path).name} ===')
    if not base_guids:
        print('  FAIL: base-game Levels.arc not found (need --base <game>/Database/database.arz '
              'with ../Resources/Levels.arc); cannot establish SV-custom provenance.')
        return 1
    viols, checked = scan(data, levels, cls_map, base_guids)
    print(f'  SV-custom respawn/save chambers checked: {checked}')
    if not viols:
        print('  PASS: every SV-custom respawn/save chamber has an isolated-load-safe (single-GUID) navmesh.')
        return 0
    print(f'  FAIL ({len(viols)}): SV-custom respawn chamber(s) with a co-residency-unsafe navmesh:')
    for v in viols:
        print(f'    {v["level"]}: shrine={v["shrines"]} guid_count={v["guid_count"]} '
              f'neighbour-deps={v["neighbours"]} own-guid={v["guid"].hex()[:8]}(SV-custom)')
    return 1


def negtest():
    """Planted-condition self-test: prove the shared classifier catches the exact crash
    condition (SV-custom respawn shrine + multi-GUID), clears the fixed one (single-GUID),
    clears no-shrine, AND clears a base-provenance respawn+multi-GUID chamber (the
    proven-safe control - the discriminator that was missing before b87 round 2)."""
    print('=== MAP-NAV-4 planted negative test ===')

    def rec02(n):
        body = b'REC\x02' + struct.pack('<3I', 1, 0, n) + b'\x11' * (n * 16) + b'\x00' * 24
        return body[:8] + struct.pack('<I', len(body) - 12) + body[12:]

    OWN_SV = b'\x22' * 16     # SV-custom own GUID (NOT in base index)
    OWN_BASE = b'\x33' * 16   # base-provenance own GUID (IN base index)
    cls_map = {r'records\drx\respawn.dbr': RESPAWN_SHRINE_CLASS,
               r'records\drx\torch.dbr': 'Decoration'}

    def mk(dbr_refs, guid_count, own):
        recs = b''.join(r.encode('latin-1') + b'\x00' for r in dbr_refs)
        nav = rec02(guid_count)
        blob = (b'LVL\x00' +
                b'\x05\x00\x00\x00' + struct.pack('<I', len(recs)) + recs +
                b'\x0b\x00\x00\x00' + struct.pack('<I', len(nav)) + nav)
        return blob, {'fname': r'levels\world\synth\s.lvl', 'guid': own,
                      'data_offset': 0, 'data_length': len(blob)}

    base_guids = {OWN_BASE}

    def run_one(dbr, gc, own):
        blob, lv = mk(dbr, gc, own)
        return _cm.scan_isolated_load_risk([lv], lambda l: blob, cls_map.get, base_guids)

    ok = True
    # A: SV-custom respawn + MULTI-GUID -> MUST flag (the crash condition)
    hit = len(run_one([r'records\drx\respawn.dbr'], 3, OWN_SV)) == 1
    print(f'  A SV-custom respawn+multiGUID(3): {"FLAGGED (correct)" if hit else "MISSED (BUG)"}')
    ok &= hit
    # B: SV-custom respawn + SINGLE-GUID -> MUST clear (the fixed condition)
    clr = len(run_one([r'records\drx\respawn.dbr'], 1, OWN_SV)) == 0
    print(f'  B SV-custom respawn+singleGUID(1): {"CLEAR (correct)" if clr else "FLAGGED (BUG)"}')
    ok &= clr
    # C: SV-custom NO shrine + MULTI-GUID -> MUST clear (not a respawn chamber)
    clr = len(run_one([r'records\drx\torch.dbr'], 4, OWN_SV)) == 0
    print(f'  C SV-custom no-shrine+multiGUID(4): {"CLEAR (correct)" if clr else "FLAGGED (BUG)"}')
    ok &= clr
    # D: BASE-provenance respawn + MULTI-GUID -> MUST clear (region-packed, proven safe:
    #    the 264 stock respawn+multiGUID chambers). THIS is the false-positive class b87
    #    round 2 fixed (HiddenValley01).
    clr = len(run_one([r'records\drx\respawn.dbr'], 5, OWN_BASE)) == 0
    print(f'  D base respawn+multiGUID(5): {"CLEAR (correct)" if clr else "FLAGGED (BUG - false positive)"}')
    ok &= clr
    print('  NEGTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('levels_arc', nargs='?')
    ap.add_argument('mod_arz', nargs='?')
    ap.add_argument('--base', default=None,
                    help='base-game database.arz; its ../Resources/Levels.arc supplies '
                         'the SV-custom provenance GUID set')
    ap.add_argument('--negtest', action='store_true')
    a = ap.parse_args()
    if a.negtest:
        sys.exit(negtest())
    if not a.levels_arc or not a.mod_arz:
        ap.error('need <Levels.arc> <mod.arz> (or --negtest)')
    sys.exit(run_gate(a.levels_arc, a.mod_arz, a.base))


if __name__ == '__main__':
    main()
