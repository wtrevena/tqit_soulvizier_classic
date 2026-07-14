#!/usr/bin/env python3
"""GATE: NPC-dialog travel invariants (the 2026-07-12 TRAVEL LAW + the build37 Helos hub).

The ONLY approved cross-area travel is talk-to-an-NPC boat-dialog (Model C: talk -> confirm
destination). Walk-through / proximity teleport portals are BANNED everywhere we author (a
shipped Helos walk-through was a live P0, commit 0f08297). This gate REPLACES the retired
walk-through-portal battery (gate_doors_hub placement/hubidentity/crosstalk, gate_sparta_*,
gate_portal_openness/visibility, gate_openness_collateral, gate_portal_records_global,
compare_gridentrance_0x14) with the honest post-P0 invariants.

Primary mode is SPEC-BASED (build-free): it reads the map/quests/arz tooling tables directly,
so it is valid without a 1.3GB map build. Pass a built .arc to also scan its live 0x05 sections.

  T1 NO WALK-THROUGHS: zero walk-through portal records (portal_olympianarena1/2, map_portal_aura)
     placed in EITHER the canonical INJECT_SPECS or the TESTHUB merged specs.
  T2 HELOS HUB: the 17 Helos-hub records (11 travelers + 6 returns) appear 0x in canonical and
     EXACTLY 1x in the TESTHUB build (WARDEN LAW: one boat-dialog record == one placement).
  T3 MASTERS RETIRED: BOTH split masters have 0 placements - svc_testhub_master_helos (superseded
     by the 11 travelers) AND svc_testhub_master_cave (b48 round 3: it was a mute ORPHAN - placed at
     the cave mouth with no boat trigger - now retired).
  T4 RETURN TRAVELERS (b48 round 3 WARDEN-SPLIT): the single svc_testhub_return is retired from
     placement; each of the 5 distinct per-area returns (svc_testhub_return_{garden,secret,uber,
     sparta,bossarena}) is placed EXACTLY ONCE (Garden/Secret/Uber/Sparta canonical, Boss Arena
     TESTHUB) so all 5 fire; Almyros (portal_master_helos) placed once canonically.
  T5 CROSS-FILE: map / quests / arz reference the SAME 17 hub records AND the SAME 5 per-area return
     records; every boat-menu label tag the quests use is minted or reused in the arz.
  T6 (built map, optional): a passed .arc's 0x05 sections contain ZERO walk-through portal
     instances; the canonical .arc places 0 hub records; the TESTHUB .arc places each once.
  RESPONDS (b48 round 3): the gate_traveler_responds invariants (no mute/orphan/warden/beyond-
     window traveler), derived build-free from the tooling tables. This is the wiring the brief asks
     for - a mute traveler cannot pass this battery.

Usage: py tools/debug/gate_travel_npc_invariants.py [<canonical.arc> [<testhub.arc>]]
Exit 0 = PASS, non-zero = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
import build_section_surgery as bss
import build_quest_files as bqf
import apply_svc_patches as asp

WALKTHROUGH_NEEDLES = (b'portal_olympianarena1', b'portal_olympianarena2', b'map_portal_aura')
# SV-NATIVE / UNTOUCHABLE baseline: portal_olympianarena / map_portal_aura instances that ship in
# the ORIGINAL SV/DRX blobs (NOT authored by us). The 2026-07-12 P0 removed only the walk-through
# portals WE injected; it explicitly LEFT SV-originals alone (inventory #20 "revert: leave
# SV-original alone"). These levels are the allowed baseline; a walk-through in ANY OTHER level =
# an authored leak = FAIL. (Measured on the build36a canonical map, 2026-07-13.)
SV_NATIVE_WALKTHROUGH_LEVELS = {
    'levels/world/bossarena/boss_arena.lvl',                 # SV boss-arena landing (portal_olympianarena2)
    'levels/world/uberdungeon/crypt_floor1.lvl',            # SV uber-arena landing (portal_olympianarena2)
    'levels/world/xbloodcave/yet_another_fucking_connector.lvl',  # SV/DRX blood-cave decor (map_portal_aura)
}
# Reused labels set by the earlier NPC creators (label_text=None in HELOS_HUB_OUTBOUND).
_REUSED_LABELS = {'tagSVCHelosToGarden', 'tagSVCHelosToSecret', 'tagSVCHelosToSparta',
                  'tagSVCHelosToUber', 'tagSVCTestHubToBossArena'}


def _norm(b):
    return (b.decode() if isinstance(b, bytes) else b).replace('/', '\\').lower()


def _count_in_specs(specs_dict, needle):
    """Count spec entries whose record path contains `needle` (a normalized substring)."""
    n = 0
    for _lvl, specs in specs_dict.items():
        for sp in specs:
            if needle in _norm(sp[0]):
                n += 1
    return n


def check_specs(fails):
    canonical = bss.INJECT_SPECS
    testhub = bss.merge_hub_into_inject_specs(bss.INJECT_SPECS)
    extra = bss.build_hub_extra_specs()

    # T1: NO WALK-THROUGHS in either build.
    for needle in WALKTHROUGH_NEEDLES:
        nd = _norm(needle)
        c = _count_in_specs(canonical, nd)
        t = _count_in_specs(testhub, nd)
        if c or t:
            fails.append(f'T1: walk-through portal record {needle!r} placed '
                         f'(canonical={c}, TESTHUB={t}) - BANNED')
    print(f'  T1 no-walk-throughs: canonical + TESTHUB place 0 of '
          f'{[n.decode() for n in WALKTHROUGH_NEEDLES]}')

    # T2: the 17 hub records: 0 canonical, exactly 1 TESTHUB.
    hub_records = [s[0] for s in bss.HELOS_HUB_PLAZA_SPECS] + \
                  [sp[0] for _k, sp in bss.HELOS_HUB_RETURN_SPECS]
    if len({_norm(r) for r in hub_records}) != 17:
        fails.append(f'T2: expected 17 distinct hub records, got '
                     f'{len({_norm(r) for r in hub_records})}')
    for r in hub_records:
        nd = _norm(r)
        c = _count_in_specs(canonical, nd)
        t = _count_in_specs(testhub, nd)
        if c != 0:
            fails.append(f'T2: hub record {nd} present in CANONICAL ({c}x) - must be TESTHUB-only')
        if t != 1:
            fails.append(f'T2: hub record {nd} placed {t}x in TESTHUB (WARDEN LAW: exactly 1)')
    print(f'  T2 helos-hub: 17 records, canonical=0 each, TESTHUB=1 each (warden law)')

    # T3: BOTH split masters retired (0 placements). b48 round 3 retires the cave master orphan.
    # NOTE: the cave master is placed via build_hub_extra_specs()[R09_LVL_KEY], which
    # merge_hub_into_inject_specs EXCLUDES (the swap path applies it) - so it never appears in
    # `testhub`. It MUST be counted against `extra` (the raw hub-extra specs) to actually detect it.
    mh = _norm(bss.SVC_TESTHUB_MASTER_HELOS_DBR)
    mc = _norm(bss.SVC_TESTHUB_MASTER_CAVE_DBR)
    if _count_in_specs(testhub, mh) != 0 or _count_in_specs(extra, mh) != 0:
        fails.append('T3: svc_testhub_master_helos still placed - should be retired')
    if _count_in_specs(extra, mc) != 0:
        fails.append(f'T3: svc_testhub_master_cave still placed ({_count_in_specs(extra, mc)}x in the '
                     f'hub-extra/R09 swap specs) - b48 round 3 RETIRED it (was a mute orphan; wire a '
                     f'trigger or leave it unplaced)')
    print('  T3 masters-retired: helos master + cave master both 0 placements (extra + testhub)')

    # T4: return travelers (b48 round 3 WARDEN-SPLIT). The single svc_testhub_return is retired from
    # placement; the 5 distinct per-area returns are placed exactly once each (4 canonical + 1 TESTHUB).
    almyros = _norm(bss.PORTAL_MASTER_NPC_DBR)
    if _count_in_specs(canonical, almyros) != 1:
        fails.append(f'T4: Almyros (portal_master_helos) must be placed once canonically '
                     f'(got {_count_in_specs(canonical, almyros)})')
    if _count_in_specs(testhub, _norm(bss.SVC_RETURN_NPC_DBR)) != 0:
        fails.append('T4: the shared svc_testhub_return must be UNPLACED (retired; warden-split '
                     'into 5 per-area records)')
    canon_returns = {'garden': bss.SVC_RETURN_GARDEN_DBR, 'secret': bss.SVC_RETURN_SECRET_DBR,
                     'uber': bss.SVC_RETURN_UBER_DBR, 'sparta': bss.SVC_RETURN_SPARTA_DBR}
    for area, dbr in canon_returns.items():
        nd = _norm(dbr)
        if _count_in_specs(canonical, nd) != 1:
            fails.append(f'T4: canonical return svc_testhub_return_{area} must be placed once '
                         f'canonically (got {_count_in_specs(canonical, nd)})')
        if _count_in_specs(testhub, nd) != 1:   # canonical placement is inherited by TESTHUB (warden law)
            fails.append(f'T4: return svc_testhub_return_{area} must be placed once in TESTHUB '
                         f'(warden law; got {_count_in_specs(testhub, nd)})')
    bnd = _norm(bss.SVC_RETURN_BOSSARENA_DBR)
    if _count_in_specs(canonical, bnd) != 0:
        fails.append(f'T4: Boss Arena return must be TESTHUB-only (0 canonical; got '
                     f'{_count_in_specs(canonical, bnd)})')
    if _count_in_specs(testhub, bnd) != 1:
        fails.append(f'T4: Boss Arena return must be placed once in TESTHUB (got '
                     f'{_count_in_specs(testhub, bnd)})')
    print('  T4 return-travelers: Almyros x1 canon; svc_testhub_return x0; 5 per-area returns x1 each '
          '(Garden/Secret/Uber/Sparta canon + Boss Arena TESTHUB)')

    # T5: cross-file agreement.
    map_recs = {_norm(r) for r in hub_records}
    q_recs = {_norm(npc) for npc, _xyz, _tag in bqf.HELOS_HUB_TRAVEL}
    if map_recs != q_recs:
        fails.append(f'T5: map vs quests record mismatch: only-map={map_recs - q_recs}, '
                     f'only-quests={q_recs - map_recs}')
    arz_recs = {_norm(r) for r, *_ in asp.HELOS_HUB_OUTBOUND} | \
               {_norm(r) for r in asp.HELOS_HUB_RETURNS}
    if map_recs != arz_recs:
        fails.append(f'T5: map vs arz record mismatch: only-map={map_recs - arz_recs}, '
                     f'only-arz={arz_recs - map_recs}')
    minted = {lt for _r, _nt, _tx, lt, ltx in asp.HELOS_HUB_OUTBOUND if ltx is not None}
    arz_labels = minted | _REUSED_LABELS | {'tagSVCAreaReturnToHelos'}
    q_labels = {t for _n, _x, t in bqf.HELOS_HUB_TRAVEL}
    missing = q_labels - arz_labels
    if missing:
        fails.append(f'T5: quest label tags not minted/reused in arz: {missing}')
    print(f'  T5 cross-file: map==quests==arz (17 records); {len(q_labels)} label tags resolve')

    # T5b (b48 round 3): the 5 warden-split per-area return records agree across arz / quests / map.
    ret_arz = {_norm(r) for r in asp.TESTHUB_AREA_RETURN_NPCS}
    ret_q = {_norm(r) for r in bqf.TESTHUB_AREA_RETURN_NPCS}
    ret_map = {_norm(d) for d in (bss.SVC_RETURN_GARDEN_DBR, bss.SVC_RETURN_SECRET_DBR,
                                  bss.SVC_RETURN_UBER_DBR, bss.SVC_RETURN_SPARTA_DBR,
                                  bss.SVC_RETURN_BOSSARENA_DBR)}
    if not (len(ret_arz) == 5 and ret_arz == ret_q == ret_map):
        fails.append(f'T5b: per-area return records disagree across files: arz={ret_arz}, '
                     f'quests={ret_q}, map={ret_map}')
    # the 2 return ports must resolve in the arz (both minted by _create_testhub_portal_npcs)
    ret_ports = {t for _xyz, t in bqf.TESTHUB_RETURN_DESTS}
    if ret_ports - {'tagSVCTestHubToHelos', 'tagSVCTestHubToBloodCave'}:
        fails.append(f'T5b: unexpected per-area return port tags: {ret_ports}')
    print(f'  T5b per-area returns: arz==quests==map (5 records); ports {sorted(ret_ports)} resolve')


def check_responds(fails):
    """b48 round 3 WIRING: run the gate_traveler_responds invariants build-free (spec-derived), so a
    mute / orphan / warden / beyond-fired-window traveler cannot pass this battery. Faults every PLACED
    hub boat NPC that would not RESPOND in-game. Uses the TESTHUB build (where every traveler exists)."""
    import gate_traveler_responds as gtr
    routes, placed = gtr.facts_from_specs(testhub=True)
    resp = gtr.evaluate(routes, placed)
    for cls, msg in resp:
        fails.append(f'RESPONDS/{cls}: {msg}')
    n_npcs = len({r["npc_short"] for r in routes})
    print(f'  RESPONDS (spec-derived TESTHUB): {"PASS" if not resp else f"FAIL ({len(resp)})"} - '
          f'{len(placed)} placed hub NPCs / {n_npcs} route owners; every placed traveler owns a '
          f'bound, fire-able route (no mute/orphan/warden/dead)')


def _scan_arc_walkthroughs_and_hub(arc_path, fails, is_testhub):
    from arc_patcher import ArcArchive
    from merge_levels_binary import parse_sections, parse_level_index
    from build_section_surgery import parse_blob_sections
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[0x01])
    hub_needles = [_norm(s[0]).split('\\')[-1].encode()
                   for s in bss.HELOS_HUB_PLAZA_SPECS] + \
                  [_norm(sp[0]).split('\\')[-1].encode()
                   for _k, sp in bss.HELOS_HUB_RETURN_SPECS]
    hub = {n: 0 for n in hub_needles}
    leaked = {}   # non-SV-native level -> walk-through count (any hit here is an authored leak)
    baseline = 0  # SV-native (allowlisted) walk-through instances
    for L in levels:
        blob = data[L['data_offset']:L['data_offset'] + L['data_length']]
        if len(blob) < 4 or blob[:3] != b'LVL':
            continue
        bsecs, _ = parse_blob_sections(blob)
        s05 = next((s for s in bsecs if s['type'] == 0x05), None)
        if not s05:
            continue
        low = s05['data'].lower()
        lvl_wt = sum(low.count(n) for n in WALKTHROUGH_NEEDLES)
        if lvl_wt:
            lname = L['fname'].replace('\\', '/').lower()
            if lname in SV_NATIVE_WALKTHROUGH_LEVELS:
                baseline += lvl_wt
            else:
                leaked[lname] = lvl_wt
        for n in hub:
            hub[n] += low.count(n)
    tag = 'TESTHUB' if is_testhub else 'canonical'
    if leaked:
        fails.append(f'T6: {tag} .arc places AUTHORED walk-through portal(s) outside the SV-native '
                     f'allowlist: {leaked} - BANNED')
    off = {n.decode(): v for n, v in hub.items() if (v != (1 if is_testhub else 0))}
    if off:
        fails.append(f'T6: {tag} .arc hub placements wrong (want {1 if is_testhub else 0} each): {off}')
    print(f'  T6 {tag} .arc: authored walk-throughs=0 (SV-native baseline={baseline}); '
          f'hub records {"1 each" if is_testhub else "0 each"} -> {"OK" if not off and not leaked else "BAD"}')


def main(argv):
    fails = []
    print('=== NPC-DIALOG TRAVEL INVARIANTS (post-P0 travel law + build37 Helos hub) ===')
    check_specs(fails)
    check_responds(fails)
    if len(argv) > 1 and Path(argv[1]).exists():
        _scan_arc_walkthroughs_and_hub(argv[1], fails, is_testhub=False)
    if len(argv) > 2 and Path(argv[2]).exists():
        _scan_arc_walkthroughs_and_hub(argv[2], fails, is_testhub=True)
    if fails:
        print('\nGATE FAIL (travel invariants):')
        for f in fails:
            print('  ' + f)
        return 1
    print('\nGATE PASS: NPC-dialog travel invariants hold (0 walk-throughs; the 17-record Helos hub '
          'is warden-clean + TESTHUB-only; the 5 per-area returns are warden-split + fire). NOTE: the '
          'b48 round-3 return-split intentionally CHANGES the canonical map/quests - the 4 established '
          'returns are canonical (a deliberate warden-mute bugfix), so a canonical rebuild + QA is '
          'required (see docs/reports/b48_sparta_mute_fix.md).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
