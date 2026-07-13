#!/usr/bin/env python3
"""GATE: TESTHUB portal rig (Model C) - render chain + Steam-inertness.

Two fail-loud checks for the flag-gated LOCAL-ONLY travel rig
(records\\quests\\svc_testhub_master.dbr + svc_testhub_return.dbr):

  A. RENDER CHAIN (D5 law). Both rig NPCs must render like the two SHIPPING
     boat-dialog masters (Almyros/portal_master_helos + Keryx/portal_master_
     olympus): their mesh + baseTexture must be BYTE-IDENTICAL to the proven
     Knossos-boatman donor, and the mesh entry + every internal shader must
     resolve under engine-faithful archive scoping. A rig NPC whose art does
     not resolve would appear invisible/T-posed.

  B. STEAM-INERTNESS. The canonical/Steam map (local/Levels_merged.arc) must
     PLACE ZERO of the two rig NPC records in ANY level's 0x05 section, so the
     boat-dialog triggers (which ship UNCONDITIONALLY in Quests.arc) attach to
     nothing and are inert for canonical players (the D3 unplaced-record no-op).
     Only the TESTHUB map variant (placed by the map lane) may reference them.

Usage:
  py tools/debug/gate_testhub_portal_rig.py [<arz>] [<mod_resources>] [<game_dir>]
Defaults resolve the standard work/ layout. Exit 0 = PASS, non-zero = FAIL.
"""
import sys, struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
from arz_patcher import ArzDatabase
import validate_render_chain as vrc

MASTER = r'records\quests\svc_testhub_master.dbr'
RETURN = r'records\quests\svc_testhub_return.dbr'
DONOR = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'
SHIPPING = [r'records\quests\portal_master_helos.dbr',
            r'records\quests\portal_master_olympus.dbr']


def _norm(s):
    return str(s).replace('/', '\\').lower()


def main(argv):
    arz = Path(argv[1]) if len(argv) > 1 else \
        REPO / 'work/SoulvizierClassic/Database/SoulvizierClassic.arz'
    mod_res = Path(argv[2]) if len(argv) > 2 else \
        REPO / 'work/SoulvizierClassic/Resources'
    game = Path(argv[3]) if len(argv) > 3 else Path(
        r'C:/Program Files (x86)/Steam/steamapps/common/'
        r'Titan Quest Anniversary Edition')

    db = ArzDatabase.from_arz(arz)
    recmap = {_norm(n): n for n in db.record_names()}

    def rec(p):
        return recmap.get(_norm(p))

    def fld(name, key):
        ff = db.get_fields(name) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == key and tf.values:
                return str(tf.values[0])
        return None

    fails = []

    # ---- A: render chain ----
    for p in (MASTER, RETURN):
        if not rec(p):
            fails.append(f'A: rig NPC MISSING from arz: {p}')
    dn = rec(DONOR)
    if not dn:
        fails.append(f'A: donor MISSING from arz: {DONOR}')

    if not fails:
        dmesh, dtex = fld(dn, 'mesh'), fld(dn, 'baseTexture')
        for p in (MASTER, RETURN):
            r = rec(p)
            m, t = fld(r, 'mesh'), fld(r, 'baseTexture')
            if _norm(m) != _norm(dmesh):
                fails.append(f'A: {p} mesh {m!r} != donor {dmesh!r}')
            if _norm(t) != _norm(dtex):
                fails.append(f'A: {p} baseTexture {t!r} != donor {dtex!r}')
        # shipping masters must share the same art (sanity anchor)
        for sp in SHIPPING:
            r = rec(sp)
            if r and _norm(fld(r, 'mesh')) != _norm(dmesh):
                fails.append(f'A: shipping {sp} mesh drifted from donor - anchor broken')

        # engine-faithful mesh + shader closure (only if art dirs present)
        if mod_res.is_dir() and (game / 'Resources').is_dir():
            eng = vrc.EngineArcResolver(str(mod_res), str(game))
            ok_mesh, shaders = vrc.mesh_internal_shaders(eng, dmesh)
            ok_tex, tdet = eng.resolve(dtex)
            bad = [s for s in shaders if not s[1]]
            if not ok_mesh:
                fails.append(f'A: mesh entry unresolved under engine scoping: {dmesh}')
            if bad:
                fails.append(f'A: mesh {dmesh} internal shader(s) unresolved: '
                             f'{[s[0] for s in bad]}')
            if not ok_tex:
                fails.append(f'A: baseTexture unresolved: {dtex} ({tdet})')
            print(f"  A render: mesh={dmesh} resolvable={ok_mesh} "
                  f"shaders={len(shaders)} bad={len(bad)}; tex={dtex} ok={ok_tex} ({tdet})")
        else:
            print(f"  A render: mesh/tex byte-identity vs donor OK; "
                  f"(art dirs absent -> engine-scoping shader check SKIPPED)")
        print(f"  A: both rig NPCs share donor mesh={dmesh} tex={dtex}")

    # ---- B: canonical placement invariants (UPDATED post-P0 2026-07-12 + build37 hub) ----
    # The PRE-P0 assertion was "canonical places 0 of both rig NPCs". That is now WRONG: the P0
    # hotfix PROMOTED svc_testhub_return into the 4 canonical areas (Garden/Secret/Uber/Sparta) as
    # the NPC-dialog way back after the walk-through portals were deleted. Updated invariants:
    #   - the hub MASTERS (svc_testhub_master / _helos / _cave) stay TESTHUB-only -> 0 canonical.
    #   - svc_testhub_return is canonical in EXACTLY the 4 P0 areas.
    #   - the build37 Helos traveler hub (svc_helos_trav_* / svc_area_return_*) is TESTHUB-only
    #     -> 0 canonical (delegated in full to gate_travel_npc_invariants.py).
    canon = REPO / 'local' / 'Levels_merged.arc'
    if canon.exists():
        from arc_patcher import ArcArchive
        from merge_levels_binary import parse_sections, parse_level_index
        from build_section_surgery import parse_blob_sections
        arc = ArcArchive.from_file(canon)
        data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
        sec = {s['type']: s for s in parse_sections(data)}
        levels = parse_level_index(data, sec[0x01])
        needles = (b'svc_testhub_master', b'svc_testhub_return',
                   b'svc_helos_trav_', b'svc_area_return_')
        placements = {n: 0 for n in needles}
        for L in levels:
            blob = data[L['data_offset']:L['data_offset'] + L['data_length']]
            if len(blob) < 4 or blob[:3] != b'LVL':
                continue
            bsecs, _ = parse_blob_sections(blob)
            s05 = next((s for s in bsecs if s['type'] == 0x05), None)
            if not s05:
                continue
            low = s05['data'].lower()
            for n in needles:
                placements[n] += low.count(n)
        m, r, ht, hr = (placements[b'svc_testhub_master'], placements[b'svc_testhub_return'],
                        placements[b'svc_helos_trav_'], placements[b'svc_area_return_'])
        print(f"  B placement: canonical places master={m} return={r} "
              f"helos_trav={ht} area_return={hr}")
        if m != 0:
            fails.append(f'B: canonical places {m} hub-MASTER instance(s) - masters are TESTHUB-only')
        if r != 4:
            fails.append(f'B: canonical must place svc_testhub_return in the 4 P0 areas '
                         f'(Garden/Secret/Uber/Sparta); got {r}')
        if ht or hr:
            fails.append(f'B: canonical places {ht + hr} build37 Helos-hub instance(s) - the '
                         f'hub is TESTHUB-only (see gate_travel_npc_invariants.py)')
    else:
        print(f"  B placement: SKIPPED (no {canon}); check once the map is built")

    if fails:
        print("\nGATE FAIL (TESTHUB portal rig):")
        for f in fails:
            print("  " + f)
        return 1
    print("\nGATE PASS: TESTHUB portal rig render chain + Steam-inertness OK")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
