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
  2. Generates the 0x0b via gen_rec02.generate() with NEIGHBOR-AWARE
     rasterization: each level's heightfield unions in the tok geometry of
     every other cluster level (translated by the 0x0a-corner world delta and
     clipped to the level's padded grid), so the walkable floor EXTENDS across
     every shared grid-tile boundary into neighbor territory. Two adjacent
     levels connect (the engine builds the cross-level walk link) only where
     BOTH levels' walkable navmesh crosses the shared boundary and overlaps;
     SV shipped one continuous 0x0a mesh spanning all levels so it never had a
     per-level stitch gap, but several SV toks stop dead AT their own boundary
     (xPassageTransitionStart's west edge = the blood-cave invisible wall:
     BC_initialpathway crossed east 23.6u, xPTS crossed west 0u -> one-sided
     -> no link). The neighbor fill makes every seam interlock on both sides
     like the walk-proven Random09A<->xPTS seam.
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
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections
from gen_rec02 import generate, load_tok_mesh
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

    # Phase 1: extract + tok-parse every cluster level ONCE. Each parsed mesh
    # is used twice: as its own level's floor AND as neighbor geometry unioned
    # into every adjacent level's heightfield (see gen_rec02.generate
    # neighbors=). A level's tok verts are LEVEL-LOCAL, relative to its 0x0a
    # corner = 0x0a header center - dims per axis; that corner is the true
    # world anchor of the geometry (the LEVELS-index corner differs from it by
    # up to 1u in x/z and 12u in y on SV levels, which would misplace copied
    # floor heights past the 1.0u walkableClimb), so neighbor deltas are
    # computed 0x0a-corner to 0x0a-corner. All corners are SV-ORIGINAL; the
    # whole cluster is shifted rigidly by GRID_SHIFT afterwards (container
    # center only), so relative placement is preserved.
    entries = []
    skipped_no_geom = []
    print('\n=== Parsing cluster geometry ===')
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
        guids_0a, center_a, dims_a, verts, tris = load_tok_mesh(str(lvl_tmp))
        corner0a = tuple(center_a[i] - dims_a[i] for i in range(3))
        # SV-original LEVELS-index footprint, BOX tile triple (the merge
        # normalizes content tiles -> box tiles via shifted_ints_raw, so the
        # engine stitches at the BOX edges; SCALE = 2 world units per tile).
        # generate() grows the grid to cover it so the walkable fill can
        # always cross the index boundary (slack levels' 0x0a boxes are
        # smaller than their index footprints).
        ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
        fp_sv = (ints[6], ints[8],
                 ints[6] + ints[3] * 2, ints[8] + ints[5] * 2)
        entries.append(dict(
            lv=lv, fname=fname, basename=basename, lvl_tmp=lvl_tmp,
            guids_0a=guids_0a, center_a=center_a, dims_a=dims_a,
            verts=verts, tris=tris, corner0a=corner0a, fp_sv=fp_sv))
        print(f'  MESH  {basename:38s} verts={len(verts):6d} tris={len(tris):6d} '
              f'corner0a={corner0a} fp={fp_sv}')

    # Precompute each level's neighbor-GUID list from ACTUAL GRID ADJACENCY
    # (footprint abutment), NOT from its own 0x0a list. The engine builds a
    # cross-level WALK link only when the two levels MUTUALLY list each other's
    # GUID (base-game 57/57 connected-dungeon levels cross-list every grid
    # neighbor). SV's per-level 0x0a lists are ASYMMETRIC - e.g.
    # xPassageTransitionStart's 0x0a names Random09A but OMITS BC_initialpathway,
    # so deriving lists from 0x0a left xPTS->BC one-way (BC listed xPTS, xPTS did
    # not list BC) -> the engine linked only from BC's side -> the blood-cave
    # invisible wall that survived every geometry/footprint/cons/height fix.
    # Footprint adjacency is symmetric by construction, so every seam becomes
    # mutual like the walk-proven Random09A<->xPTS seam.
    def _merged_own(e):
        k = e['fname'].replace('\\', '/').lower()
        return OWN_GUID_OVERRIDE.get(k, e['lv']['ints_raw'][36:52])

    def _fp_adjacent(a, b):
        ax0, az0, ax1, az1 = a
        bx0, bz0, bx1, bz1 = b
        xgap = max(0, max(ax0, bx0) - min(ax1, bx1))
        zgap = max(0, max(az0, bz0) - min(az1, bz1))
        return xgap == 0 and zgap == 0  # touch on an edge or overlap

    adj_guids = {}
    for ent in entries:
        lst = [_merged_own(ent)]  # own GUID first (ProcessRLTD needs it first)
        for other in entries:
            if other is ent:
                continue
            if _fp_adjacent(ent['fp_sv'], other['fp_sv']):
                g = _merged_own(other)
                if g not in lst:
                    lst.append(g)
        adj_guids[ent['basename']] = lst

    # --- Y-ALIGNMENT (2026-07-06): adjacent SV cluster levels are anchored a CONSTANT
    # 0 or ~2.56u apart in Y (stdev 0 across the shared floor) - a placement artifact
    # of splitting SV's one continuous floor into per-level toks, NOT real terrain.
    # That constant step is exactly what froze the player at the seam (> the engine's
    # 1u climb / 2u findNearestPoly tolerance). Fix: rigidly shift each level's floor
    # so every abutting pair's shared floor meets at ONE height (no step, no ramp -
    # ramps created a NEW earlier cliff). Measure each seam's constant offset from the
    # toks, then propagate a per-level correction (BFS per connected component). Max
    # correction is ~2.56u (a tiny, imperceptible float vs the rendered terrain).
    def _floor_cells(e):
        c = e['corner0a']; pts = {}
        for tri in e['tris']:
            for vi in tri:
                vx, vz, vy = e['verts'][vi]
                k = (round(c[0] + vx), round(c[2] + vz)); wy = c[1] + vy
                if k not in pts or wy < pts[k]:
                    pts[k] = wy
        return pts
    _fc = {e['basename']: _floor_cells(e) for e in entries}
    _seam_off = {}
    for _i in range(len(entries)):
        for _j in range(_i + 1, len(entries)):
            a, b = entries[_i], entries[_j]
            if not _fp_adjacent(a['fp_sv'], b['fp_sv']):
                continue
            common = set(_fc[a['basename']]) & set(_fc[b['basename']])
            if len(common) < 30:
                continue
            d = [_fc[a['basename']][k] - _fc[b['basename']][k] for k in common]
            md = sorted(d)[len(d) // 2]
            sd = (sum((x - sum(d) / len(d)) ** 2 for x in d) / len(d)) ** 0.5
            if sd < 1.0:        # CONSTANT offset only; leave genuine terrain steps alone
                _seam_off[(a['basename'], b['basename'])] = md
    _yadj = {}
    for (a, b), off in _seam_off.items():
        _yadj.setdefault(a, []).append((b, off))
        _yadj.setdefault(b, []).append((a, -off))
    # ANCHOR (2026-07-06 entrance-regression fix): each connected component's BFS root
    # (shift=0) must be DETERMINISTIC and must be a level that interfaces FIXED,
    # non-regenerated data - never the arbitrary first entry. Random09A is the cave
    # ENTRANCE: HiddenValley01's native GridEntrance portal pair (0x14 record #30 +
    # R09's 0x06 reciprocal descriptor, FIXED world coords incl. Y at the door grid
    # cell) drops the player onto R09's mesh, and the engine's findNearestPoly
    # vertical extent is 2u - the arbitrary root shifted R09 by -3u and the landing
    # missed the mesh (frida-verified: navmesh loads ret=1, portal open=1 both ways;
    # purely the mesh-height-vs-fixed-landing mismatch -> could not enter the cave).
    # Root preference: Random09A, then any OWN_GUID_OVERRIDE level (those keep
    # AE-native GUIDs = native interfaces), then smallest basename (deterministic).
    # (Rank 1 is currently redundant - OWN_GUID_OVERRIDE == {Random09A} today, which
    # rank 0 already catches - but is kept deliberately: any FUTURE level added to
    # OWN_GUID_OVERRIDE is by definition another native-interface anchor and must
    # out-rank arbitrary cluster levels for the component root.)
    # Ground truth backing this root (0x05 entity-Y vs tok-floor survey, 2026-07-06):
    # R09-rooting also re-anchors every cluster level onto its OWN terrain - the +3u
    # levels (xPTS, BC_initialpathway, drxBC_Connector1, xTempleTransitionHallway)
    # are exactly the toks SV exported 2.56u BELOW their placed entities, so the
    # in-cluster door portals (drxBC_Finale<->bossfight 0x06 pair, yafc->drxBC3 and
    # xTTH->new_secretdoor 0x14 pairs) stay on-mesh too.
    _key_of = {e['basename']: e['fname'].replace('\\', '/').lower() for e in entries}

    def _root_rank(bn):
        return (0 if bn.lower() == 'random09a.lvl'
                else 1 if _key_of[bn] in OWN_GUID_OVERRIDE
                else 2, bn.lower())

    yshift = {}
    from collections import deque as _deque
    for e in entries:
        if e['basename'] in yshift:
            continue
        # Shifts are WHOLE world units: the container center is int32 (rec02_format
        # LHDR center[3]), so a fractional shift can't be stored, and a fractional
        # off_y risks pushing a stacked neighbour's cell heights out of uint16 range.
        # Rounding each seam offset (~2.56u -> 3u) leaves a constant <=0.5u residual
        # step, far under the engine's 1u climb / 2u findNearestPoly tolerance.
        _comp = [e['basename']]
        _cseen = {e['basename']}
        _q = _deque(_comp)
        while _q:
            u = _q.popleft()
            for v, _off in _yadj.get(u, ()):
                if v not in _cseen:
                    _cseen.add(v); _comp.append(v); _q.append(v)
        _root = min(_comp, key=_root_rank)
        yshift[_root] = 0; _q = _deque([_root])
        while _q:
            u = _q.popleft()
            for v, off in _yadj.get(u, ()):
                if v not in yshift:
                    yshift[v] = yshift[u] + int(round(off)); _q.append(v)
    # HARD anchor gate: Random09A must be UNSHIFTED (shift exactly 0). Its donor must
    # meet the FIXED HiddenValley01 GridEntrance landing, which we never regenerate.
    _r09_bn = next((e['basename'] for e in entries
                    if e['basename'].lower() == 'random09a.lvl'), None)
    if _r09_bn is not None and yshift.get(_r09_bn, 0) != 0:
        raise AssertionError(
            f'Y-ALIGN ANCHOR VIOLATION: Random09A yshift={yshift[_r09_bn]:+d} (must be 0). '
            f'Its mesh must stay at the 0x0a-authored height or the fixed HV01 '
            f'GridEntrance portal landing (findNearestPoly vertical ext 2u) misses it '
            f'and the cave cannot be entered at all. Fix _root_rank / the component '
            f'root selection; do NOT ship these donors.')
    _nsh = sum(1 for v in yshift.values() if v != 0)
    _sh_note = ', '.join(f'{k}:{v:+d}' for k, v in sorted(yshift.items()) if v != 0) or 'none'
    print(f'  Y-ALIGN: {len(_seam_off)} constant seam offsets; {_nsh} levels shifted; '
          f'max |shift|={max((abs(v) for v in yshift.values()), default=0)}u; '
          f'anchor Random09A shift={yshift.get(_r09_bn, 0) if _r09_bn is not None else "n/a"}; '
          f'shifts: {_sh_note}')

    generated = []
    print('\n=== Generating ===')
    for ent in entries:
        lv = ent['lv']
        fname = ent['fname']
        basename = ent['basename']
        key = fname.replace('\\', '/').lower()
        own_guid = OWN_GUID_OVERRIDE.get(key, lv['ints_raw'][36:52])
        guids_0a, center_a, dims_a = ent['guids_0a'], ent['center_a'], ent['dims_a']

        # Every other cluster level is offered as neighbor geometry, offset by
        # the world delta between the two levels' 0x0a corners; generate()'s
        # bbox prefilter + the rasterizer's per-tri clip keep only what falls
        # inside this level's padded grid (robust adjacency: the bbox clip
        # does the work, no fragile footprint-adjacency computation).
        # Neighbour Y delta carries the RELATIVE Y-alignment (yshift[neighbour] -
        # yshift[own]) on top of the 0x0a-corner delta, so a neighbour's strip lands
        # at its own aligned floor height in this level's grid (matches the reciprocal
        # handoff and this level's own aligned floor).
        _ys_own = yshift.get(basename, 0)
        nbrs = []
        for o in entries:
            if o is ent:
                continue
            dxyz = list(o['corner0a'][i] - ent['corner0a'][i] for i in range(3))
            dxyz[1] += yshift.get(o['basename'], 0) - _ys_own
            nbrs.append((o['verts'], o['tris'], tuple(dxyz)))

        # THE CROSS-LEVEL STITCH (disasm-proven, docs/CROSS_LEVEL_STITCH_RE.md):
        # there is NO walk-link and NO adjacency table. Each level owns a PRIVATE
        # dtNavMesh. The engine tags EVERY navmesh poly with its rasterized cell
        # AREA ID, and reads that area id at runtime as a 1-BASED INDEX INTO THIS
        # MESH'S GUID LIST, naming the level that owns the cell. A seamless seam
        # crossing is a SINGLE-mesh path: the level's mesh rasterizes its
        # neighbour's terrain ~16u PAST the shared boundary and tags that strip
        # with the neighbour's GUID index, so one mesh covers both sides of the
        # click and the entity's region flips as the poly tags change. Vanilla
        # meshes carry 2..13 GUIDs and mirror the strip from both sides; our
        # single-GUID/own-tagged/stops-at-the-plane donors gave the engine no
        # data connecting the rooms -> the wall (all 11 prior fixes missed this).
        #
        # So each donor's GUID list = [own] + every footprint-ABUTTING neighbour
        # (resolved to the merged world; own first so area 1 == own), and
        # area_boxes (parallel to the list) lets generate() tag each cell by
        # which level's footprint box contains it. resolve_guids stays only for
        # the `dropped` log. (Residency note: multi-GUID re-arms ProcessRLTD's
        # load-time residency gate at the mouth preload; build11/12 Frida logs
        # show the cluster co-streams so R09 loads fine - watch Level+0x6a48 on
        # R09 if the mouth ever walls again.)
        def _resolve_merged(g, tag):
            if g in merged_guids:
                return g
            if g in shared_remap and shared_remap[g] in merged_guids:
                return shared_remap[g]
            raise SystemExit(
                f'{basename}: abutting-neighbour GUID {g.hex()} ({tag}) does not '
                f'resolve in the merged world - cannot tag the seam. Fix the '
                f'GRID_SHIFT/merge so the neighbour is present, or drop the seam.')

        assert own_guid in merged_guids, f'{basename}: own GUID unresolved in merged world'
        guid_list = [own_guid]
        area_boxes = [ent['fp_sv']]              # parallel to guid_list; own box first
        for other in entries:
            if other is ent or not _fp_adjacent(ent['fp_sv'], other['fp_sv']):
                continue
            g = _resolve_merged(_merged_own(other), other['basename'])
            if g in guid_list:
                continue
            guid_list.append(g)
            area_boxes.append(other['fp_sv'])

        t0 = time.time()
        doc, stats = generate(
            str(ent['lvl_tmp']),
            own_guid=own_guid, neighbor_guids=guid_list[1:], area_boxes=area_boxes,
            mesh=(guids_0a, center_a, dims_a, ent['verts'], ent['tris']),
            neighbors=nbrs, footprint=ent['fp_sv'], y_shift=_ys_own)
        gen_dt = time.time() - t0

        # reposition to the merged grid by shifting the container center only.
        shift = grid_shift_for(fname)
        shifted_center = shift_center(doc['center'], shift)
        doc['center'] = shifted_center
        # ANCHOR gate (G1): a level that interfaces non-regenerated data
        # (OWN_GUID_OVERRIDE, e.g. Random09A vs HiddenValley01's fixed GridEntrance
        # landing) must keep its 0x0a-authored container height: donor center Y ==
        # 0x0a center Y + GRID_SHIFT dy, i.e. zero y_shift leaked in.
        if key in OWN_GUID_OVERRIDE:
            _want_y = center_a[1] + shift[1]
            if shifted_center[1] != _want_y:
                raise AssertionError(
                    f'{basename}: ANCHOR violated - donor center Y {shifted_center[1]} '
                    f'!= 0x0a center Y {center_a[1]} + grid dy {shift[1]} = {_want_y} '
                    f'(y_shift {_ys_own:+d} leaked into an anchored level). The fixed '
                    f'portal landing would miss this mesh; do NOT ship.')
        # generate() set doc['guids'] = [own] + neighbor_guids = guid_list.
        assert doc['guids'] == guid_list, \
            f'{basename}: guid list mismatch ({doc["guids"]} vs {guid_list})'
        _, dropped = resolve_guids(guids_0a, own_guid, merged_guids, shared_remap)
        remapped = own_guid != lv['ints_raw'][36:52]

        data = serialize_rec02(doc)

        # Self-verify: round-trip identity + structural invariants + our patches.
        doc2 = parse_rec02(data, decompress=True)
        assert serialize_rec02(doc2) == data, f'{basename}: round-trip mismatch'
        assert len(doc2['sets']) == 3, f'{basename}: expected 3 sets'
        assert doc2['center'] == list(shifted_center) or tuple(doc2['center']) == shifted_center, \
            f'{basename}: center not shifted ({doc2["center"]} vs {shifted_center})'
        assert all(g in merged_guids for g in doc2['guids']), \
            f'{basename}: a serialized GUID does not resolve'

        # CROSS-TAG self-verify (Track 1, docs/CROSS_LEVEL_STITCH_RE.md): decode
        # set 0's area histogram. area id == 1-based GUID-list index of the level
        # owning each cell. Two invariants: (i) no area id exceeds guid_count;
        # (ii) if this donor lists neighbours, the mesh MUST rasterize a strip
        # tagged with at least one neighbour index - a list with zero cross-tagged
        # cells is exactly the build13 failure mode (registration but no strip ->
        # the wall). The authoritative per-seam >=50-cell check is the merged-map
        # seam gate; this catches total failure cheaply, pre-merge.
        ahist = Counter()
        for rec in doc2['sets'][0]['records']:
            for a in rec['areas']:
                if a:
                    ahist[a] += 1
        gc = len(guid_list)
        if ahist:
            assert max(ahist) <= gc, \
                f'{basename}: area id {max(ahist)} exceeds guid_count {gc}'
        if gc > 1 and not any(a > 1 for a in ahist):
            raise SystemExit(
                f'{basename}: {gc} GUIDs listed but ZERO neighbour-tagged cells - '
                f'the seam strip was never rasterized (build13 failure mode). The '
                f'neighbour toks are not reaching past this level\'s boundary into '
                f'the padded grid; check the neighbour bbox prefilter / pad.')
        area_note = ' areas={' + ','.join(f'{k}:{ahist[k]}' for k in sorted(ahist)) + '}'

        if not dry_run:
            (OUT_DIR / f'{basename}.0b.bin').write_bytes(data)

        drop_note = f' dropped={dropped}' if dropped else ''
        remap_note = ' [REMAP]' if remapped else ''
        generated.append((basename, len(data), stats['n_tiles'], len(guid_list)))
        print(f'  GEN   {basename:38s} {len(data):7d} B  tiles={stats["n_tiles"]:3d} '
              f'guids={len(guid_list):2d} nbrs={stats["n_neighbors"]:2d} '
              f'cells={stats["n_rast_own"]}+{stats["n_rast"] - stats["n_rast_own"]}'
              f'{area_note} {gen_dt:4.1f}s{remap_note}{drop_note}')

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
