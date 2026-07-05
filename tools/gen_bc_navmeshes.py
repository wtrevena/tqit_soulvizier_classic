#!/usr/bin/env python3
"""Generate pre-positioned 0x0b (REC\\x02) navmeshes for the xBloodCave levels
from the PRISTINE upstream SV source, offline (no Editor, no Recast library).

Why this exists
---------------
The 30 xBloodCave levels ship with 0x0a (PathEngine PTH) navmeshes the stock
TQAE engine cannot parse, so those areas are unwalkable ("invisible wall"). The
fix is a valid 0x0b (Detour dtTileCache / RLTD) section per level. tools/
gen_rec02.py already reverse-engineers 0x0a -> 0x0b and self-round-trips. This
driver wraps it for the specific xBloodCave batch and, critically, makes each
generated section land correctly in the MERGED world:

  1. Reads the pristine 0x0a from upstream world01.map (the decompiled tree lost
     28/30 xBloodCave 0x0a to failed Editor re-saves; upstream is untouched).
  2. Generates the 0x0b via gen_rec02.generate().
  3. Repositions it to the merged grid by SHIFTING the container center by
     GRID_SHIFT (imported from svaera_plus_portals so the two never drift). The
     tile records are level-local (bmin = tx*12.8 ...), so shifting only the
     center repositions the whole mesh - same principle transplant_rec02 uses.
  4. Sets the GUID list from the level's own 0x0a GUID list (own + spatially
     adjacent neighbor level GUIDs the SV authors baked), REMAPPING any shared
     level whose merged-world copy is SVAERA's (different GUID) and dropping any
     GUID that still does not resolve. The engine's ProcessRLTD rejects the whole
     section unless EVERY GUID resolves in the merged level-GUID map, so this
     filter is mandatory (xPassageTransitionStart's 0x0a references SV-original
     Random09A, which the merge replaced with SVAERA's Random09A).

Output: local/editor_normalized/<basename>.0b.bin  (raw 0x0b section bytes).
svaera_plus_portals step 7b picks these up and injects them WITHOUT transplant
(they are already correctly positioned + GUID-correct).

7 of the 30 levels are ocean scenery with no 0x0a geometry; they legitimately
get no 0x0b (the engine tolerates levels without one).

Usage:
  py tools/gen_bc_navmeshes.py            # generate all, write .0b.bin files
  py tools/gen_bc_navmeshes.py --dry-run  # generate + verify, write nothing
"""
import os
import sys
import struct
import time
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections
from tok_parse import extract_mesh
from gen_rec02 import generate
from rec02_format import serialize_rec02, parse_rec02
from svaera_plus_portals import GRID_SHIFT  # single source of truth for the shift

UPSTREAM_SV_ARC = REPO / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc'
SVAERA_ARC = REPO / 'reference_mods' / 'SVAERA_customquest' / 'Resources' / 'Levels.arc'
OUT_DIR = Path(os.environ.get(
    'SVC_DONOR_DIR', str(REPO / 'local' / 'editor_normalized')))

BC_TOKEN = 'xbloodcave'


def _load_map(arc_path):
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    return data, levels


def build_merged_guid_map():
    """Return (merged_guids, shared_remap).

    merged_guids: set of 16-byte GUIDs registered in the MERGED world =
        every SVAERA level GUID + every SV-only level GUID (svaera_plus_portals
        appends the SV-only levels; shared levels keep SVAERA's GUID).
    shared_remap: {sv_guid -> ae_guid} for every level present under the SAME
        name in both maps whose GUIDs differ (the merge keeps SVAERA's copy, so
        a neighbor reference to the SV GUID must be redirected to the AE GUID of
        the level that actually exists in the merged world).
    """
    ae_data, ae_levels = _load_map(SVAERA_ARC)
    sv_data, sv_levels = _load_map(UPSTREAM_SV_ARC)

    ae_by_name = {lv['fname'].replace('\\', '/').lower(): lv for lv in ae_levels}
    sv_only = [lv for lv in sv_levels
               if lv['fname'].replace('\\', '/').lower() not in ae_by_name]

    merged_guids = set(lv['ints_raw'][36:52] for lv in ae_levels)
    merged_guids |= set(lv['ints_raw'][36:52] for lv in sv_only)

    shared_remap = {}
    for lv in sv_levels:
        key = lv['fname'].replace('\\', '/').lower()
        svg = lv['ints_raw'][36:52]
        ae = ae_by_name.get(key)
        if ae is not None:
            aeg = ae['ints_raw'][36:52]
            if svg != aeg:
                shared_remap[svg] = aeg
    return merged_guids, shared_remap


def resolve_guids(guids_0a, own_guid, merged_guids, shared_remap):
    """Map a level's 0x0a GUID list into merged-world-resolvable GUIDs.

    For each 0x0a GUID: keep if it resolves; else remap SV->AE for a replaced
    shared level; else drop. De-duplicates while preserving order and guarantees
    the level's OWN GUID is present and first (ProcessRLTD needs the own GUID;
    the SV data always includes it in the 0x0a list but not necessarily first).
    Returns (resolved_guids, dropped) where dropped is a list of hex strings.
    """
    out = []
    dropped = []
    seen = set()

    def _push(g):
        if g not in seen:
            seen.add(g)
            out.append(g)

    # own GUID first (it resolves - it is a registered level)
    if own_guid in merged_guids:
        _push(own_guid)
    for g in guids_0a:
        if g in merged_guids:
            _push(g)
        elif g in shared_remap and shared_remap[g] in merged_guids:
            _push(shared_remap[g])
        else:
            dropped.append(g.hex())
    return out, dropped


def shift_center(center, shift):
    return (center[0] + shift[0], center[1] + shift[1], center[2] + shift[2])


def grid_shift_for(fname):
    """Return the (dx,dy,dz) GRID_SHIFT applicable to a level, or (0,0,0)."""
    key = fname.replace('\\', '/').lower()
    for pattern, (dx, dy, dz) in GRID_SHIFT.items():
        if pattern in key:
            return (dx, dy, dz)
    return (0, 0, 0)


def main():
    dry_run = '--dry-run' in sys.argv[1:]
    t_all = time.time()

    print('Loading merged-world GUID map (SVAERA + SV-only)...')
    merged_guids, shared_remap = build_merged_guid_map()
    print(f'  merged GUIDs: {len(merged_guids)}   shared SV->AE remaps: {len(shared_remap)}')

    print(f'Loading upstream SV map: {UPSTREAM_SV_ARC.name}')
    sv_data, sv_levels = _load_map(UPSTREAM_SV_ARC)
    bc = [lv for lv in sv_levels
          if BC_TOKEN in lv['fname'].replace('\\', '/').lower()]
    print(f'  xBloodCave levels: {len(bc)}')

    # Relocated Silk Road cave (blood-cave walk-in). Not under xBloodCave; add it
    # explicitly. It carries the WEST tunnel into the blood cave, and its 0x0a
    # grid edge points at xPassageTransitionStart, so its 0x0b must resolve both
    # its own (AE) GUID and the xPTS GUID in the merged world.
    R09_KEY = 'levels/world/orient/underground/random09a.lvl'
    sv_r09 = next(lv for lv in sv_levels
                  if lv['fname'].replace('\\', '/').lower() == R09_KEY)
    bc.append(sv_r09)
    # Own-GUID override: the merge keeps SVAERA's Random09A GUID in the index (so
    # HiddenValley01's cave-mouth 0x14 binding + xPTS's navmesh neighbor list keep
    # resolving without regen), so the donor's own GUID must be AE's, not SV's.
    _ae_data2, ae_levels2 = _load_map(SVAERA_ARC)
    AE_R09_GUID = next(lv['ints_raw'][36:52] for lv in ae_levels2
                       if lv['fname'].replace('\\', '/').lower() == R09_KEY)
    OWN_GUID_OVERRIDE = {R09_KEY: AE_R09_GUID}
    print(f'  + Random09A (own-GUID override -> {AE_R09_GUID.hex()})')

    if not dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f'Output dir: {OUT_DIR}  (dry_run={dry_run})')

    # Extract pristine upstream .lvl blobs to a private temp dir OUTSIDE the
    # donor dir, so they can never be mistaken for a tier-2 <basename>.lvl donor
    # by svaera_plus_portals.find_donor_0x0b.
    tmp = Path(tempfile.gettempdir()) / 'svc_bc_upstream_lvl_cache'
    tmp.mkdir(parents=True, exist_ok=True)

    generated = []
    skipped_no_geom = []
    print('\n=== Generating ===')
    for lv in bc:
        fname = lv['fname']
        basename = fname.replace('\\', '/').split('/')[-1]  # e.g. BC_initialpathway.lvl
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        secs, _ = parse_blob_sections(blob)
        if not any(s['type'] == 0x0a for s in secs):
            skipped_no_geom.append(basename)
            print(f'  SKIP  {basename:38s} (no 0x0a geometry - ocean scenery)')
            continue

        # Extract the pristine blob to a loose .lvl gen_rec02 can read.
        lvl_tmp = tmp / basename
        lvl_tmp.write_bytes(blob)

        key = fname.replace('\\', '/').lower()
        own_guid = OWN_GUID_OVERRIDE.get(key, lv['ints_raw'][36:52])
        guids_0a, center_a, dims_a, _tok = extract_mesh(str(lvl_tmp))

        t0 = time.time()
        doc, stats = generate(str(lvl_tmp))
        gen_dt = time.time() - t0

        # (a) reposition to the merged grid by shifting the container center.
        shift = grid_shift_for(fname)
        shifted_center = shift_center(doc['center'], shift)
        doc['center'] = shifted_center

        # (b) install the merged-world-resolvable GUID list.
        resolved, dropped = resolve_guids(guids_0a, own_guid, merged_guids, shared_remap)
        assert resolved, f'{basename}: no resolvable GUIDs (own GUID unregistered?)'
        # Residency-gate hardening: ProcessRLTD (0x101f4ba0) refuses the WHOLE
        # navmesh unless EVERY listed GUID's level is RESIDENT at load time,
        # and a failed load is never retried (docs/CAVE_ENTRY_CHAIN_TRACE.md).
        # Donors that list far-side neighbors therefore wall the first seam
        # whose neighbor sits beyond the streaming frontier (proven in-game at
        # xPTS -> BC_initialpathway, 2026-07-05). Ship every donor gate-free
        # with its own GUID alone, EXCEPT the walk-proven entrance pair which
        # stays byte-identical. Single-GUID meshes are base-game-normal
        # (251/2214, including AE-Random09A itself). Grid seams carry no other
        # cross-level link data, so this cannot break seam handoff
        # (docs/NAVMESH_COVERAGE_FIX.md sections 4-5).
        KEEP_NEIGHBOR_GUIDS = {
            R09_KEY,
            'levels/world/xbloodcave/xpassagetransitionstart.lvl',
        }
        if key not in KEEP_NEIGHBOR_GUIDS:
            resolved = [resolved[0]]        # own GUID only (resolve_guids puts it first)
        doc['guids'] = resolved
        # Did any 0x0a GUID get redirected SV->AE (a replaced shared level)?
        remapped = any(g in shared_remap for g in guids_0a)

        data = serialize_rec02(doc)

        # Self-verify: round-trip identity + structural invariants + our patches.
        doc2 = parse_rec02(data, decompress=True)
        assert serialize_rec02(doc2) == data, f'{basename}: round-trip mismatch'
        assert len(doc2['sets']) == 3, f'{basename}: expected 3 sets'
        assert doc2['center'] == list(shifted_center) or tuple(doc2['center']) == shifted_center, \
            f'{basename}: center not shifted ({doc2["center"]} vs {shifted_center})'
        assert all(g in merged_guids for g in doc2['guids']), \
            f'{basename}: a serialized GUID does not resolve'
        # center must equal shifted (grid_corner+half_extents) => grid_corner+shift+half
        # (center_a already = grid_corner + half; shift moves it to the merged grid)

        if not dry_run:
            (OUT_DIR / f'{basename}.0b.bin').write_bytes(data)

        drop_note = f' dropped={dropped}' if dropped else ''
        remap_note = ' [REMAP]' if remapped else ''
        generated.append((basename, len(data), stats['n_tiles'], len(resolved)))
        print(f'  GEN   {basename:38s} {len(data):7d} B  tiles={stats["n_tiles"]:3d} '
              f'guids={len(resolved):2d} center{tuple(doc["center"])} '
              f'{gen_dt:4.1f}s{remap_note}{drop_note}')

    print('\n=== Summary ===')
    print(f'  generated: {len(generated)}   skipped-no-geometry: {len(skipped_no_geom)}   '
          f'total xBloodCave: {len(bc)}')
    print(f'  total time: {time.time() - t_all:.1f}s')
    if skipped_no_geom:
        print(f'  ocean-scenery (no 0x0b, by design): {", ".join(skipped_no_geom)}')
    if not dry_run:
        print(f'  wrote {len(generated)} .0b.bin -> {OUT_DIR}')
    return generated, skipped_no_geom


if __name__ == '__main__':
    main()
