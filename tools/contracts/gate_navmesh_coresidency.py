#!/usr/bin/env python3
r"""MAP-NAV-4 standalone reporter: SV-custom respawn-chamber navmesh SHAPE **ADVISORY**.

STATUS: ADVISORY (P2), NOT A CRASH GATE - demoted 2026-07-28, BL-b89-DEBT-4A
---------------------------------------------------------------------------
This tool shipped as a P0 crash gate built on the b87 reading that the Frida probe's
`navOK=0` at ENTER meant ProcessRLTD had REJECTED the navmesh. The 2026-07-27 runtime
captures REFUTED that reading: `navOK=0` at ENTER is the NORMAL in-progress state -
every ENTER shows it, LEAVE flips it to 1 (docs/reports/b89_ocean_ext05_hotfix.md
sec 1). The ENTER-with-no-LEAVE signature was the malformed 148-byte REC02 container
body, which is now gated properly and at P0 by MAP-NAV-5 (body structure) and
MAP-NAV-6 (self-duplicated GUID list). No runtime capture has ever shown a well-formed
multi-GUID SV-custom navmesh failing to load.

Consequently this reporter exits 0 by default (advisory). `--strict` restores the old
fail-on-finding behaviour for a lane that deliberately wants the stricter shape.

WHAT IT STILL REPORTS, AND WHY THAT IS WORTH KEEPING
----------------------------------------------------
An SV-CUSTOM level (own level GUID absent from the stock TQAE Levels.arc index) that
hosts a StrategicMovementRespawnShrine is a SAVE / RESPAWN point: the engine can load
it in ISOLATION on a fresh save-load or a death-respawn, before its grid-neighbour
levels stream in. ProcessRLTD's per-GUID live-residency check is still disasm-proven
(Engine 0x101f4ba0: for every listed GUID, [reg+0x50][idx] must be a stream-RESIDENT
region, not merely resolve in the world GUID map), so every neighbour GUID a navmesh
lists IS a load-time dependency on that neighbour's residency. And guid_count == 1 is
stock-normal (251 base levels) and runtime-proven on our own map
(new_secretdoor_transitionhallway gc=1, ENTER+LEAVE al=1 in probe session B) -
residency-proof by construction, since the only GUID named is the level being loaded.
So "an isolated-loadable SV-custom chamber carries a single-own-GUID navmesh" is a
sound HARDENING preference. It is not a demonstrated defect class.

WHY "SV-CUSTOM" IS THE SCOPE (and why multi-GUID is NOT a defect anywhere)
--------------------------------------------------------------------------
The stock game ships 264 respawn chambers with multi-GUID navmeshes (DelphiTownStart
gc=12, Memphis gc=13, Utgard, ...) that save/reload fine. Provenance by own level GUID
separates them name-free: a base/IT/XPack level's GUID is present in the stock TQAE
Levels.arc index; an SV-custom level's is not. This excludes the byte-identical Silk
Road HiddenValley01 spawn hub (a round-1 false positive) and surfaces exactly the
SV-custom respawn chambers our own pipeline generates.

Shares its classifier (contracts_map.scan_isolated_load_risk) with the battery contract
contract_navmesh_coresidency so their scope can never drift apart.

Usage:
  py tools/contracts/gate_navmesh_coresidency.py <Levels.arc> <mod.arz> --base "<game>/Database/database.arz"
      (base level provenance is read from <game>/Resources/Levels.arc, derived from --base)
  py tools/contracts/gate_navmesh_coresidency.py ... --strict   # exit 1 on any finding
  py tools/contracts/gate_navmesh_coresidency.py --negtest      # planted-condition self-test (no args)
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


def run_gate(arc_path, mod_arz, base_arz, strict=False):
    data, levels = load_levels(arc_path)
    cls_map = load_class_map(mod_arz, base_arz)
    base_guids = base_level_guids(base_arz)
    mode = 'STRICT' if strict else 'ADVISORY (P2 - exit 0; --strict to fail)'
    print(f'=== MAP-NAV-4 navmesh-shape advisory [{mode}]: {Path(arc_path).name} ===')
    if not base_guids:
        print('  DID NOT RUN: base-game Levels.arc not found (need --base <game>/Database/'
              'database.arz with ../Resources/Levels.arc); cannot establish SV-custom provenance.')
        return 1 if strict else 0
    viols, checked = scan(data, levels, cls_map, base_guids)
    print(f'  SV-custom respawn/save chambers checked: {checked}')
    if not viols:
        print('  CLEAN: every SV-custom respawn/save chamber carries the residency-proof '
              'single-own-GUID navmesh shape.')
        return 0
    label = 'FAIL' if strict else 'ADVISORY'
    print(f'  {label} ({len(viols)}): SV-custom respawn chamber(s) with a MULTI-GUID navmesh '
          f'(hardening note, NOT a demonstrated crash - see the module docstring):')
    for v in viols:
        print(f'    {v["level"]}: shrine={v["shrines"]} guid_count={v["guid_count"]} '
              f'neighbour-deps={v["neighbours"]} own-guid={v["guid"].hex()[:8]}(SV-custom)')
    return 1 if strict else 0


def negtest():
    """Planted-condition self-test: prove the shared classifier still SCOPES correctly -
    it flags the advisory shape (SV-custom respawn shrine + multi-GUID), clears the
    residency-proof shape (single-GUID), clears no-shrine, AND clears a base-provenance
    respawn+multi-GUID chamber (the 264-strong stock class that ships and reloads fine -
    the discriminator that was missing before b87 round 2).

    Case E additionally asserts the SEVERITY contract of the demotion (BL-b89-DEBT-4A):
    the battery contract must report these at P2 (advisory, non-blocking), never P0."""
    print('=== MAP-NAV-4 planted negative test (advisory scope + severity) ===')

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
    # E: SEVERITY CONTRACT (BL-b89-DEBT-4A). The battery contract must emit the flagged
    #    shape at P2 (advisory, non-blocking). A regression back to P0 would re-block
    #    builds on the refuted b87 premise, so it is asserted here, not just documented.
    from types import SimpleNamespace
    blob_e, lv_e = mk([r'records\drx\respawn.dbr'], 3, OWN_SV)
    ctx_e = SimpleNamespace(levels=[lv_e], blob=lambda l: blob_e,
                            class_of=cls_map.get, base_level_guids=base_guids)
    sev = [x['severity'] for x in _cm.contract_navmesh_coresidency(ctx_e)]
    sev_ok = sev == ['P2']
    print(f'  E battery severity is advisory P2: {sev} '
          f'{"(correct)" if sev_ok else "(BUG - MAP-NAV-4 must not block a build)"}')
    ok &= sev_ok
    # F: the advisory must still REPORT (never silently pass) when it cannot run.
    ctx_f = SimpleNamespace(levels=[], blob=lambda l: b'', class_of=cls_map.get,
                            base_level_guids=set())
    nr = _cm.contract_navmesh_coresidency(ctx_f)
    nr_ok = len(nr) == 1 and nr[0]['severity'] == 'P2'
    print(f'  F no-provenance reports P2 (not silent, not blocking): '
          f'{[x["severity"] for x in nr]} {"(correct)" if nr_ok else "(BUG)"}')
    ok &= nr_ok
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
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 on any finding (default: advisory, exit 0) - see BL-b89-DEBT-4A')
    a = ap.parse_args()
    if a.negtest:
        sys.exit(negtest())
    if not a.levels_arc or not a.mod_arz:
        ap.error('need <Levels.arc> <mod.arz> (or --negtest)')
    sys.exit(run_gate(a.levels_arc, a.mod_arz, a.base, strict=a.strict))


if __name__ == '__main__':
    main()
