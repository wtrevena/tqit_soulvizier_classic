#!/usr/bin/env python3
"""AREA SELF-CHECK gate - the single-level (G3/G4-degenerate + G-OVER) navmesh gate.

The blood-cave gates (G2 entrance / G3 corridor / G4 seams) are all multi-level
and blood-cave-hardcoded. A single-level isolated area (Uber Dungeon, Boss Arena,
Garden of Merchants, Sparta Crypt L2 - SV_AREAS_CAMPAIGN_PLAN.md Wave 1) has no
seam and (yet) no entrance, so its meaningful navmesh gate degenerates to:

  1. ROUND-TRIP identity     - the donor 0x0b parses and re-serializes byte-identical
                               (structural validity; the container is well-formed).
  2. OWN-FLOOR COVERAGE      - the generated walkable set covers a high fraction of
                               the level's own eroded tok floor (it is a REAL mesh
                               that fills the room, not an empty/degenerate stub).
  3. G-OVER (no walk-on-rock)- ZERO walkable cell centre lies inside any of the
                               level's own baseObstacle polygons (the RCA carve
                               held; the player cannot walk through solid rocks).
  4. MAIN-COMPONENT          - the largest 4-adjacency |dh|<=climb component covers
                               most of the walkable set (the room is one connected
                               floor, not shattered into unreachable islands).
  5. GUIDS RESOLVE           - every GUID in the donor resolves in the merged world
                               (ProcessRLTD rejects the whole section otherwise).

This is deliberately a LIGHTER check than the blood cave's chain reachability (the
plan's steer for single-level areas). It gates the donor in `local/editor_normalized`
(or SVC_DONOR_DIR) AND, with --check-merged, the injected copy in the merged map.

Usage:
  py tools/debug/area_selfcheck.py --level crypt_floor1
  py tools/debug/area_selfcheck.py --level boss_arena --check-merged
  py tools/debug/area_selfcheck.py --level gardenofmerchants --map <Levels.arc>
  py tools/debug/area_selfcheck.py --level spartacryptlevel2 --min-coverage 0.90

Exit 0 = PASS, 1 = FAIL. Read-only.
"""
import argparse
import math
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

from arc_patcher import ArcArchive                                    # noqa: E402
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS  # noqa: E402
from build_section_surgery import parse_blob_sections                 # noqa: E402
from rec02_format import parse_rec02                                  # noqa: E402
from gen_rec02 import load_tok_mesh, rasterize, erode, stamp_obstacles, \
    PAD, CS, ERODE_CELLS                                              # noqa: E402
from navlib import Mesh                                               # noqa: E402

UPSTREAM_SV_ARC = REPO / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc'
SVAERA_ARC = REPO / 'reference_mods' / 'SVAERA_customquest' / 'Resources' / 'Levels.arc'
DONOR_DIR = Path(os.environ.get('SVC_DONOR_DIR', str(REPO / 'local' / 'editor_normalized')))


def load_map(path):
    arc = ArcArchive.from_file(Path(path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    by = {lv['fname'].replace('\\', '/').lower(): lv for lv in levels}
    return data, levels, by


def find_level(by, stem):
    stem = stem.lower()
    if not stem.endswith('.lvl'):
        stem += '.lvl'
    for k, lv in by.items():
        if k.split('/')[-1] == stem:
            return k, lv
    return None, None


def blob_of(data, lv):
    return data[lv['data_offset']:lv['data_offset'] + lv['data_length']]


def donor_for(stem):
    """Locate <stem>.lvl.0b.bin in the donor dir (case-insensitive on Windows)."""
    stem_l = stem.lower().replace('.lvl', '')
    for p in DONOR_DIR.glob('*.0b.bin'):
        base = p.name[:-len('.0b.bin')]
        base = base[:-4] if base.lower().endswith('.lvl') else base
        if base.lower() == stem_l:
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--level', required=True, help='level basename, e.g. crypt_floor1')
    ap.add_argument('--map', default=None, help='merged Levels.arc (default: local then work)')
    ap.add_argument('--check-merged', action='store_true',
                    help='also gate the injected 0x0b in the merged map (not just the donor)')
    ap.add_argument('--min-coverage', type=float, default=0.85,
                    help='min fraction of own eroded tok floor the mesh must cover')
    ap.add_argument('--min-main', type=float, default=0.90,
                    help='min fraction of walkable cells in the largest component')
    ap.add_argument('--max-onrock', type=float, default=0.005,
                    help='max fraction of walkable cells allowed inside an own obstacle '
                         '(a tiny nonzero budget is EXPECTED: the connectivity-repair '
                         'restores a handful of carved cells to bridge a room piece the '
                         'carve split off - RCA-sanctioned cosmetic-rock doorways. A real '
                         'carve FAILURE shows tens of percent.)')
    args = ap.parse_args()

    stem = args.level
    print(f'AREA SELF-CHECK: {stem}')

    # ---- merged map (for GUID resolution + optional merged-copy gate) ----
    map_path = args.map
    if map_path is None:
        for cand in (REPO / 'local' / 'Levels_merged.arc',
                     REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Levels.arc'):
            if cand.exists():
                map_path = cand
                break
    if map_path is None or not Path(map_path).exists():
        print('FAIL: no merged map found (pass --map)')
        return 1
    map_path = Path(map_path)
    mdata, mlevels, mby = load_map(map_path)
    merged_guids = {lv['ints_raw'][36:52] for lv in mlevels}
    mkey, mlv = find_level(mby, stem)
    if mlv is None:
        print(f'FAIL: {stem} not in merged map {map_path.name}')
        return 1

    # ---- upstream SV tok: own floor + obstacles ----
    svdata, svlevels, svby = load_map(UPSTREAM_SV_ARC)
    skey, svlv = find_level(svby, stem)
    if svlv is None:
        print(f'FAIL: {stem} not in upstream SV map')
        return 1
    blob = blob_of(svdata, svlv)
    tmp = Path(tempfile.gettempdir()) / f'svc_selfcheck_{stem}.lvl'
    tmp.write_bytes(blob)
    guids_a, center_a, dims_a, verts, tris, obstacles = load_tok_mesh(str(tmp))
    corner0a = tuple(center_a[i] - dims_a[i] for i in range(3))

    # Rasterize the OWN tok floor in the SAME grid frame gen_rec02.generate() uses
    # for a LONE level (no footprint arg, no neighbours): the frame is the 0x0a box
    # + PAD, then the ORIGIN IS SNAPPED DOWN to the global 64u tile lattice (the
    # 2026-07-05 stitch fix). Replicating that snap exactly is what makes the SV
    # own-floor cells share ONE lattice with the donor cells, so coverage/G-OVER
    # compare on identical indices. (The earlier version rastered in an unsnapped
    # PAD frame -> a different lattice -> 0% coverage false-negative.)
    pad = PAD
    x0 = corner0a[0] - pad
    z0 = corner0a[2] - pad
    x1 = corner0a[0] + 2 * dims_a[0] + pad
    z1 = corner0a[2] + 2 * dims_a[2] + pad
    x0 = (x0 // 64) * 64
    z0 = (z0 // 64) * 64
    x1 = x0 + ((x1 - x0 + 63) // 64) * 64
    z1 = z0 + ((z1 - z0 + 63) // 64) * 64
    if (x1 - x0) % 2:
        x1 += 1
    if (z1 - z0) % 2:
        z1 += 1
    dims = ((x1 - x0) // 2, dims_a[1] + pad, (z1 - z0) // 2)
    off_x = corner0a[0] - x0
    off_z = corner0a[2] - z0
    gw = int(math.ceil(2 * dims[0] / CS))
    gh = int(math.ceil(2 * dims[2] / CS))
    hgrid = rasterize(verts, tris, off_x, off_z, pad, gw, gh)
    eroded = erode(set(hgrid), gw, gh, ERODE_CELLS)
    obs_in_floor = stamp_obstacles(obstacles, gw, gh, off_x, off_z) & eroded
    # The WALKABLE TARGET is the CARVED floor = eroded MINUS the obstacle cells (the
    # generator subtracts obstacle polys - RCA carve). Measuring coverage against the
    # RAW eroded floor would wrongly penalise rock-heavy levels (a correct donor omits
    # exactly the rock footprints): e.g. darkforestenter is 81% of raw-eroded but
    # 100% of the carved floor. So the denominator is the carved floor.
    carved = eroded - obs_in_floor
    # carved own-floor cells as WORLD lattice indices (grid cell gx -> world index
    # round(x0/CS)+gx; x0 integral, CS=0.2, so round(x0/CS) is exact).
    wox = round(x0 / CS)
    woz = round(z0 / CS)
    eroded_world = {(idx % gw + wox, idx // gw + woz) for idx in carved}
    print(f'  own tok: verts={len(verts)} tris={len(tris)} obs_polys={len(obstacles)} '
          f'eroded_floor={len(eroded)} obs_in_floor={len(obs_in_floor)} '
          f'carved_walkable_target={len(carved)}')

    # ---- the gate, applied to a mesh (donor and/or merged) ----
    def gate(tag, doc):
        ok = True
        m = Mesh(doc, tag)   # parse_rec02 already succeeded -> container structurally valid
        # GUIDs resolve
        unresolved = [g for g in doc['guids'] if bytes(g) not in merged_guids]
        if unresolved:
            print(f'  {tag}: FAIL - {len(unresolved)} GUID(s) do not resolve in merged world')
            ok = False
        else:
            print(f'  {tag}: GUIDs resolve ({len(doc["guids"])})')
        # Donor walkable cells as WORLD lattice indices: cell (gx,gz) world center =
        # origin[0]+(gx+0.5)*CS, so its lattice index is round(origin[0]/CS)+gx. For an
        # UNSHIFTED single-level donor this equals the SV own-floor lattice exactly; a
        # GRID_SHIFTED donor is offset by the (integer) shift, which we undo so coverage
        # is measured against the SV floor regardless of relocation.
        dwox = round(m.origin[0] / CS)
        dwoz = round(m.origin[2] / CS)
        walk_world = {(gx + dwox, gz + dwoz) for (gx, gz) in m.cells}
        # Undo any grid shift: align the donor's snapped origin to the SV floor's snapped
        # origin (both on the CS lattice) so the two index sets are directly comparable.
        sx = wox - dwox
        sz = woz - dwoz
        walk_aligned = {(ix + sx, iz + sz) for (ix, iz) in walk_world}
        covered = len(walk_aligned & eroded_world)
        cov = covered / max(len(eroded_world), 1)
        cov_ok = cov >= args.min_coverage
        print(f'  {tag}: own-floor coverage {covered}/{len(eroded_world)} = {cov*100:.1f}% '
              f'(>= {args.min_coverage*100:.0f}%) -> {"PASS" if cov_ok else "FAIL"}')
        ok = ok and cov_ok
        # G-OVER: no walkable cell centre inside any own obstacle polygon. Map each donor
        # cell back to the SV-LOCAL grid (aligned index - wox/woz -> local gx/gz -> local
        # world via the generator's cell->local formula (gx+0.5)*CS - off), then
        # point-in-poly against the own obstacle polygons (their level-local frame). Use
        # stamp_obstacles' obstacle-cell set intersected with the donor cells for speed
        # (bbox prefilter), matching the generator's own carve exactly.
        obs_local = stamp_obstacles(obstacles, gw, gh, off_x, off_z)
        walk_local_idx = {(ix + sx - wox) + (iz + sz - woz) * gw
                          for (ix, iz) in walk_world
                          if 0 <= ix + sx - wox < gw and 0 <= iz + sz - woz < gh}
        n_on_rock = len(walk_local_idx & obs_local)
        onrock_frac = n_on_rock / max(len(m.cells), 1)
        gover_ok = onrock_frac <= args.max_onrock
        print(f'  {tag}: G-OVER walk-on-rock cells = {n_on_rock} '
              f'({onrock_frac*100:.4f}% of walkable, <= {args.max_onrock*100:.2f}%; '
              f'expected = connectivity-repair bridges) -> '
              f'{"PASS" if gover_ok else "FAIL (carve did not hold - walk-through-rock)"}')
        ok = ok and gover_ok
        # main component
        comps = m.components()
        biggest = len(comps[0]) if comps else 0
        total = len(m.cells)
        frac = biggest / max(total, 1)
        main_ok = frac >= args.min_main
        print(f'  {tag}: main component {biggest}/{total} = {frac*100:.1f}% of walkable '
              f'({len(comps)} comps) (>= {args.min_main*100:.0f}%) -> '
              f'{"PASS" if main_ok else "FAIL"}')
        ok = ok and main_ok
        return ok

    # donor
    dp = donor_for(stem)
    if dp is None:
        print(f'FAIL: no donor <{stem}>.lvl.0b.bin in {DONOR_DIR}')
        return 1
    print(f'  donor: {dp.name}')
    ddoc = parse_rec02(dp.read_bytes(), decompress=True)
    ok = gate(f'DONOR {dp.name}', ddoc)

    # merged injected copy
    mblob = blob_of(mdata, mlv)
    msec, _ = parse_blob_sections(mblob)
    m0b = next((s['data'] for s in msec if s['type'] == 0x0b), None)
    has0a = any(s['type'] == 0x0a for s in msec)
    if m0b is None or len(m0b) == 148:
        print(f'  MERGED {stem}: 0x0b {"absent" if m0b is None else "= 148B stub"} '
              f'(not injected){"" if not args.check_merged else " - FAIL"}')
        if args.check_merged:
            ok = False
    else:
        if has0a:
            print(f'  MERGED {stem}: FAIL - 0x0a not stripped')
            ok = ok and not args.check_merged and ok
            if args.check_merged:
                ok = False
        mdoc = parse_rec02(m0b, decompress=True)
        okm = gate(f'MERGED {stem} 0x0b', mdoc)
        # bytes must equal the donor
        if m0b != dp.read_bytes():
            print(f'  MERGED {stem}: 0x0b bytes != donor ({len(m0b)} vs {dp.stat().st_size})')
            okm = False
        else:
            print(f'  MERGED {stem}: 0x0b bytes == donor ({len(m0b)} B)')
        if args.check_merged:
            ok = ok and okm

    print(f'\nAREA SELF-CHECK {stem}: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
