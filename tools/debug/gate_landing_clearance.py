#!/usr/bin/env python3
"""GATE G-LAND - hub teleport LANDING clearance (travel-invariants family).

Closes the blind spot that shipped the 2026-07-13 "teleported inside the chest,
can't move, instantly killed" bug (Will). The v1 Helos traveler-hub boss
destinations reused the build36 boss SPEC-PRIMARY placement spots - i.e. the
exact (x,z) where each boss set-piece (the `q_<boss>_lone` proxy / its reward
container / props) is placed as a 0x05 ENTITY. The existing on-mesh survey
(survey_uberboss_spots.py) checks NAVMESH walkability + clearance but NOT
occupancy by a placed collidable entity, so a spot that is on-mesh AND sitting
on top of the boss passes every prior gate while pinning the player against the
entity's collision (then the boss kills him). See docs/reports/b44_landing_clearance.md.

THE GATE - every teleport landing must be BOTH:
  (a) ON-MESH: within ~1 cell of a walkable navmesh cell in all 3 tilesets, in
      the MAIN reachable component (reuses survey_uberboss_spots machinery); AND
  (b) CLEAR of every COLLIDABLE placed 0x05 entity in the destination level by at
      least a per-class minimum distance - CONTAINERS (chests) get the largest
      margin, boss/monster proxies next, then solid props, then talk NPCs.
      Non-colliding entities (lights / sound / FX / POI markers) never fail.

It also accepts EXTRA PLANNED placements (a level-keyed spec table, coords
LEVEL-LOCAL) so a future map wave can gate its landings BEFORE building - i.e.
prove that a new landing set stays clear of placements that are not on the map
yet (b41 map-pass bosses/chests, b42 3-chests-per-boss, ...).

Landing sets + planned placements for the cross-wave audit are embedded below
with provenance (branch + commit) so the audit is reproducible without checking
out the other worktrees.

Usage:
  # gate the LIVE v1 wiring (imported from build_quest_files) vs a built map:
  py tools/debug/gate_landing_clearance.py --map <Levels.arc> --wiring v1

  # cross-wave audit: the b39 hub-v2 landing set vs current + b41 (+ b42 model):
  py tools/debug/gate_landing_clearance.py --map <Levels.arc> --wiring v2 --placements b41
  py tools/debug/gate_landing_clearance.py --map <Levels.arc> --wiring v2 --placements b41b42

  # future wave: gate a landing/placement set from files (LANDINGS / SPECS globals):
  py tools/debug/gate_landing_clearance.py --map <arc> --wiring my_landings.py --extra my_specs.py

Exit 0 = every landing PASS; 1 = any landing DEADLY / FAIL / CHECK. Read-only.
"""
import sys
import os
import struct
import math
import argparse
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

import survey_uberboss_spots as S            # noqa: E402  (on-mesh machinery)
from contracts_map import parse_blob_sections  # noqa: E402
from rec02_format import parse_rec02            # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Collision model. All distances are CENTER-TO-CENTER world units. The player
# collision radius (~0.6u in TQAE) is folded into the class minimums, which are
# deliberately conservative. A landing FAILS if a collidable entity of a class is
# closer than that class' minimum; it is DEADLY (a hard pin - the player spawns
# inside the entity, exactly Will's report) if a hard collider is within PIN_DIST.
PIN_DIST = 1.5
CLASS_MIN = {
    'container': 4.0,   # chests / containers - the reported bug; largest margin
    'monster':   3.0,   # boss/hero/creature placements + q_*_lone spawn proxies
    'proxy':     3.0,   # spawn proxies (spawn a body AT the spot -> body pins)
    'prop':      2.5,   # solid decorations: walls, columns, sarcophagi, rocks, urns, tombs
    'npc':       2.0,   # talk NPCs (travelers, portal masters, villagers, caravan)
    'other':     1.5,   # unknown class -> DEADLY-within-PIN safety net only
    'portal':    0.0,   # portal / teleport / grid-entrance - non-colliding (informational)
    'soft':      0.0,   # lights / sound / FX / POI markers - non-colliding (informational)
}
# HARD_FAIL = classes whose class-min triggers a FAIL (dangerously close). NPC and
# portal are SOFT-collision in TQAE (crowd/overlap without pinning), so they only
# raise informational NOTES, never a FAIL. 'other' (unknown) triggers only a DEADLY
# pin if it is within PIN_DIST (a safety net for an unclassified solid).
HARD_FAIL = ('container', 'monster', 'proxy', 'prop')
DEADLY_CLASSES = ('container', 'monster', 'proxy', 'prop', 'other')
NOTE_DIST = 2.0         # npc/portal within this raises an informational note

# Nudge robustness (--nudge only). The emitted coord clears each collidable class by
# class_min PLUS this buffer and stands on solid footing, so the INTEGER-world coord
# actually emitted (and a built map whose entity positions drift slightly) still clears
# the GATE margin. Round 1 emitted a FLOAT-validated 2.57u spot whose rounded coord was
# 2.40u < the 2.5u prop min; the integer-lattice search + this buffer close that gap.
NUDGE_BUFFER = 0.5      # required clearance headroom over each class-min for a "robust" nudge
NUDGE_CLR = 0.95        # required footing (walkable disc fraction) for a "robust" nudge -
#                        prefers a fully-footed spot over a barely-robust pit/wall-edge one

# on-mesh thresholds (mirror survey_uberboss_spots.survey_level, calibrated to avoid
# false positives on big multi-region overworld hubs)
LANDING_EXT = 1.5       # clearance disc radius for a player landing (footing)
CLR_FLOOR = 0.50        # min walkable fraction of the disc (below = tight-footing NOTE)
ONMESH_CELLS = 2.5      # nearest walkable cell within cs*ONMESH_CELLS = truly on-mesh
MIN_ISLAND_CELLS = 500  # landing component smaller than this = a stranded island (CHECK)


def classify(dbr):
    """Map a 0x05 record path to a collision class (see CLASS_MIN)."""
    d = dbr.replace('\\', '/').lower()
    base = d.rsplit('/', 1)[-1]
    # 1) non-colliding first (so 'chest'-in-an-fx-name does not read as a container)
    SOFT = ('light', 'soundobject', 'sound_', '_snd', 'glyph', 'fog', 'smoke',
            'mist', 'particle', 'flare', 'ambient', 'glow', 'sparkle', 'firefly',
            '/poi/', 'poi_', '_poi', 'marker', 'fxpack', '_fx', 'fx_', 'effect',
            'dustcloud', 'lightsource', 'godray', 'lensflare')
    if any(k in d for k in SOFT):
        # containers/monsters never carry these tokens in practice; guard anyway
        if not any(k in base for k in ('chest', 'container', 'strongbox')):
            return 'soft'
    # 1b) talk-NPC portal masters / entrance NPCs are NPCs, not portal pads
    if any(k in base for k in ('portal_master', 'portal_bloodcave', 'portal_uberdungeon',
                               'portal_secret', 'portal_sparta')):
        return 'npc'
    # 1c) portal / teleport / grid-entrance pads - non-colliding (walk onto them)
    if (base.startswith('portal') or 'teleport' in base or 'passagetransition' in base
            or any(k in base for k in ('portalgate', 'gridentrance', 'gridexit',
                                       'levelchange', 'levelentrance'))):
        return 'portal'
    # 2) containers (the reported bug)
    if 'container' in d or any(k in base for k in
                               ('chest', 'goldenchest', 'strongbox', 'lootpile',
                                'reward', 'coffer', 'urnreward')):
        return 'container'
    # 3) spawn proxies / bosses / monsters (spawn a live body at the spot)
    if (base.startswith('q_') or '/proxy' in d or '/proxies' in d
            or any(k in base for k in ('lone', 'guardpair', 'warband', 'broodnest',
                                       'broodmother', 'roulette', 'yard', 'ambush',
                                       'proxyspawn', 'spawner', 'generator', 'pool'))):
        return 'proxy'
    if any(base.startswith(p) for p in ('um_', 'am_', 'bm_', 'bs_', 'ug_', 'sc_')) \
            or any(k in d for k in ('/monster', '/hero', '/boss', '/creatures/',
                                    '/creature/', 'minion', 'demon_', 'beastman',
                                    'undead_', 'skeleton', 'keres')):
        return 'monster'
    # 4) talk NPCs (ours + native)
    if any(k in d for k in ('npc', 'villager', 'townsperson', 'merchant', 'caravan',
                            'portal_master', 'helos_trav', 'area_return', 'return',
                            'storyteller', 'soulcollector', 'boatman', 'speaking')):
        return 'npc'
    # 5) solid props / setdressing with collision (incl. DRX blood-cave destructibles:
    # burst vessels / egg-sacs / fleshy growths have collision until killed)
    if any(k in base for k in ('wall', 'column', 'pillar', 'sarcophag', 'statue',
                               'door', 'gate', 'urn', 'tomb', 'rock', 'boulder',
                               'tree', 'pine', 'stone', 'arch', 'brazier', 'totem',
                               'cage', 'bars', 'fence', 'rubble', 'debris', 'coffin',
                               'crate', 'barrel', 'table', 'throne', 'altar',
                               'obelisk', 'fountain', 'giant', 'tholos',
                               'temple', 'sarcophagia', 'catacomb', 'vines', 'lever',
                               'vessle', 'vessel', 'eggsac', 'bloodegg', 'polyp',
                               'membrane', 'fleshgrowth', 'growth', 'pod', 'sac',
                               'pillarbase', 'column')):
        return 'prop'
    return 'other'


def parse_0x05_instances(blob):
    """Authoritative flag-aware 0x05 walk -> [(dbr_str, x, y, z, flags, klass)]
    level-LOCAL. Version base is 72 for v0x11/v0x0f else 56 (build_section_surgery
    rule); if that base does not consume the section exactly, the other base is
    tried and the one that lands on the section end is used (robust across the
    2282-level index). Returns ([], None) if no 0x05 / unparseable."""
    if len(blob) < 4:
        return [], None
    ver = blob[3] if blob[:3] == b'LVL' else None
    d = None
    for t, sd in parse_blob_sections(blob):
        if t == 0x05:
            d = sd
            break
    if d is None:
        return [], ver

    def walk(base):
        scount = struct.unpack_from('<I', d, 0)[0]
        p = 4
        strings = []
        for _ in range(scount):
            sl = struct.unpack_from('<I', d, p)[0]
            p += 4
            strings.append(d[p:p + sl])
            p += sl
        icount = struct.unpack_from('<I', d, p)[0]
        p += 4
        out = []
        q = p
        for _ in range(icount):
            if q + base > len(d):
                return None
            sidx = struct.unpack_from('<I', d, q)[0]
            x, y, z = struct.unpack_from('<fff', d, q + 40)
            flags = struct.unpack_from('<I', d, q + 52)[0]
            dbr = (strings[sidx] if sidx < len(strings) else b'?').decode('latin1')
            out.append((dbr, x, y, z, flags))
            q += base + (16 if flags != 0 else 0)
        return out if q == len(d) else None

    primary = 72 if ver in (0x11, 0x0f) else 56
    for base in (primary, 56 if primary == 72 else 72):
        res = walk(base)
        if res is not None:
            return [(dbr, x, y, z, fl, classify(dbr)) for (dbr, x, y, z, fl) in res], ver
    return [], ver   # unparseable (report as no-entities, on-mesh still gates)


def ints13(lv):
    return struct.unpack_from('<13i', lv['ints_raw'], 0)


def build_boxes(levels):
    """[(lv, cx, cy, cz, hx, hy, hz)] - corner=ints[6,7,8], half-extents=ints[3,4,5];
    world box = [corner, corner + 2*half]."""
    boxes = []
    for lv in levels:
        it = ints13(lv)
        boxes.append((lv, it[6], it[7], it[8], it[3], it[4], it[5]))
    return boxes


def resolve_level(boxes, wx, wy, wz):
    """Level whose (x,z) box contains the point; ties broken by smallest box area
    then nearest center-Y (undergrounds are far-flung so this is unambiguous in
    practice). Returns (lv, corner) or (None, None)."""
    hits = []
    for (lv, cx, cy, cz, hx, hy, hz) in boxes:
        if cx <= wx < cx + 2 * hx and cz <= wz < cz + 2 * hz:
            hits.append(((2 * hx) * (2 * hz), abs((cy + hy) - wy), lv, (cx, cy, cz)))
    if not hits:
        return None, None
    hits.sort(key=lambda h: (h[0], h[1]))
    return hits[0][2], hits[0][3]


class LevelCache:
    """Per-level 0x05 entities + on-mesh navmesh survey context, cached by blob
    offset (the returns all share one Helos level)."""

    def __init__(self, data):
        self.data = data
        self._ent = {}
        self._nav = {}

    def entities(self, lv):
        key = lv['data_offset']
        if key not in self._ent:
            blob = self.data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            self._ent[key] = parse_0x05_instances(blob)
        return self._ent[key]

    def nav(self, lv):
        key = lv['data_offset']
        if key not in self._nav:
            blob = self.data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            self._nav[key] = self._build_nav(lv, blob)
        return self._nav[key]

    def _build_nav(self, lv, blob):
        b0b = None
        for t, sd in parse_blob_sections(blob):
            if t == 0x0b:
                b0b = sd
                break
        if not b0b:
            return None
        doc = parse_rec02(b0b, decompress=True)
        origin = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
        corner = ints13(lv)
        off = (corner[6] - origin[0], corner[8] - origin[2])
        setcells = S.build_walk_cells(doc)
        # Precompute an integer cell-index SET per tileset so on-mesh + clearance
        # queries are O(window), not O(cells) - the nudge spiral calls them ~10^3x.
        idxsets = []
        for (cs, cells) in setcells:
            iset = set()
            for (cx, cz) in cells:
                iset.add((int(round(cx / cs - 0.5)), int(round(cz / cs - 0.5))))
            idxsets.append((cs, iset))
        cellmap0, cs0 = S.build_indexed_cells(doc, 0)
        comps0 = S.components_of(cellmap0)
        return dict(off=off, setcells=setcells, idxsets=idxsets,
                    cellmap0=cellmap0, cs0=cs0, comps0=comps0)


def fast_nearest(cs, iset, x, z, win=4):
    """Nearest walkable-cell distance using a precomputed integer index set.
    Searches a +-win cell window (win*cs covers the on-mesh threshold); returns inf
    if nothing walkable is within the window (genuinely off-mesh)."""
    gx = int(round(x / cs - 0.5))
    gz = int(round(z / cs - 0.5))
    best = 1e18
    for dx in range(-win, win + 1):
        for dz in range(-win, win + 1):
            if (gx + dx, gz + dz) in iset:
                cxc = (gx + dx + 0.5) * cs
                czc = (gz + dz + 0.5) * cs
                dd = (cxc - x) ** 2 + (czc - z) ** 2
                if dd < best:
                    best = dd
    return math.sqrt(best) if best < 1e17 else float('inf')


def fast_clearance(cs, iset, x, z, ext, n=9):
    """Walkable fraction of a filled disc (radius ext) via the index set (~1-cell
    tolerance). O(samples), independent of total cell count."""
    samples = hit = 0
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            sx = x + (i / n) * ext
            sz = z + (j / n) * ext
            if (sx - x) ** 2 + (sz - z) ** 2 > ext * ext:
                continue
            samples += 1
            gx = int(round(sx / cs - 0.5))
            gz = int(round(sz / cs - 0.5))
            ok = False
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    if (gx + a, gz + b) in iset:
                        ok = True
                        break
                if ok:
                    break
            if ok:
                hit += 1
    return hit / samples if samples else 0.0


def survey_onmesh(nav, lx, lz, ext=LANDING_EXT):
    """Per-tileset nearest + clearance + component membership, in the offset-
    corrected cell frame, using the precomputed index sets (fast). Calibrated so a
    landing on a large (non-island) navmesh region passes even if it is not the
    single largest component (big overworld hubs have many large regions).

    onmesh_bad (the on-mesh sub-gate FAIL) is True only when the landing is
    genuinely OFF the mesh in some tileset (nearest > cs*ONMESH_CELLS) OR stranded
    on a tiny island (component < MIN_ISLAND_CELLS). Low footing clearance is
    surfaced as a NOTE, not a hard fail."""
    if nav is None:
        return None
    off = nav['off']
    qx, qz = lx + off[0], lz + off[1]
    per = []
    on_all = True
    for (cs, iset) in nav['idxsets']:
        d = fast_nearest(cs, iset, qx, qz)
        clr = fast_clearance(cs, iset, qx, qz, ext)
        onmesh = d <= cs * ONMESH_CELLS
        per.append((d, clr, onmesh))
        on_all = on_all and onmesh
    rank, size, _cd = S.point_component(nav['cellmap0'], nav['cs0'], nav['comps0'], qx, qz)
    min_clr = min(c for _d, c, _o in per)
    tiny_island = (size is not None and size < MIN_ISLAND_CELLS)
    onmesh_bad = (not on_all) or tiny_island
    return dict(per=per, rank=rank, size=size, min_clr=min_clr,
                on_all=on_all, tiny_island=tiny_island, onmesh_bad=onmesh_bad)


def nearest_entities(entities, lx, lz, extra=None):
    """entities = [(dbr,x,y,z,fl,klass)] level-local (+ optional extra planned
    placements same shape). Return sorted [(dist, dbr, x, z, klass, is_extra)]."""
    out = []
    for (dbr, x, y, z, fl, klass) in entities:
        out.append((math.hypot(x - lx, z - lz), dbr, x, z, klass, False))
    for (dbr, x, y, z, fl, klass) in (extra or []):
        out.append((math.hypot(x - lx, z - lz), dbr, x, z, klass, True))
    out.sort(key=lambda e: e[0])
    return out


def _clearance_slack(near_at, strict_npc):
    """Smallest signed clearance at a candidate point = min over colliders of
    (dist - class threshold). >= 0 => clears the GATE; >= NUDGE_BUFFER => robust.
    Thresholds: CLASS_MIN for hard classes, PIN_DIST for 'other', NOTE_DIST for
    npc/portal when strict; soft never binds. near_at = [(dist,dbr,x,z,klass,ex)]."""
    slack = 1e18
    for (dist, _dbr, _x, _z, klass, _ex) in near_at:
        if klass in HARD_FAIL:
            thr = CLASS_MIN[klass]
        elif klass == 'other':
            thr = PIN_DIST
        elif strict_npc and klass in ('npc', 'portal'):
            thr = NOTE_DIST
        else:
            continue
        slack = min(slack, dist - thr)
    return slack


def _binding_collider(near_at):
    """The FAIL/DEADLY-determining collider at a point = the one with the smallest
    (dist - threshold) over hard classes + 'other' (npc/portal are soft, never bind a
    FAIL). Returns (slack, dist, klass, dbr, thr) or None. This is what CONSTRAINS the
    landing - what --nudge reports (not merely the nearest entity, which may be a
    low-threshold 'other' that is not the binding constraint)."""
    best = None
    for (dist, dbr, _x, _z, klass, _ex) in near_at:
        if klass in HARD_FAIL:
            thr = CLASS_MIN[klass]
        elif klass == 'other':
            thr = PIN_DIST
        else:
            continue
        s = dist - thr
        if best is None or s < best[0]:
            best = (s, dist, klass, dbr, thr)
    return best


def find_nudge(nav, entities, extra, lx, lz, max_r=16.0):
    """Search the INTEGER-WORLD lattice outward from (lx,lz) for the closest point that
    is on-mesh (all tilesets, not a tiny island), well-footed, AND clears every collidable
    entity. The world grid corner is an integer, so an integer LEVEL-LOCAL offset is
    exactly an integer WORLD coord - the point validated here is byte-for-byte the point
    main() emits (corner + local). That closes the round-1 bug where the nudge validated a
    FLOAT local (2.57u) but emitted its rounded coord (2.40u < the 2.5u prop min).

    Prefers a ROBUST spot: clears every class by class_min + NUDGE_BUFFER AND footing
    >= NUDGE_CLR, so the landing stays clear even if built-map entity positions drift.
    Falls back to the closest merely-gate-passing spot (returned robust=False) if none is
    robust within max_r. Two npc passes (strict then relaxed - npc/portal are soft).
    Returns (nlx, nlz, radius, near_at, onmesh, robust) with INTEGER nlx,nlz, or None."""
    ilx, ilz = int(round(lx)), int(round(lz))
    R = int(math.ceil(max_r))
    offs = [(math.hypot(dx, dz), dx, dz)
            for dx in range(-R, R + 1) for dz in range(-R, R + 1)
            if 1.0 <= math.hypot(dx, dz) <= max_r]
    offs.sort(key=lambda o: o[0])                        # closest integer coord first
    for strict_npc in (True, False):
        passing = None     # closest gate-passing (slack >= 0) this pass = tight fallback
        for (r, dx, dz) in offs:
            nlx, nlz = ilx + dx, ilz + dz
            om = survey_onmesh(nav, nlx, nlz)
            if om is None or om['onmesh_bad'] or om['min_clr'] < CLR_FLOOR:
                continue
            near_at = nearest_entities(entities, nlx, nlz, extra)
            slack = _clearance_slack(near_at, strict_npc)
            if slack < 0:
                continue
            if passing is None:
                passing = (nlx, nlz, r, near_at, om, False)
            if slack >= NUDGE_BUFFER and om['min_clr'] >= NUDGE_CLR:
                return (nlx, nlz, r, near_at, om, True)   # robust; closest-first
        if passing is not None:
            return passing                                # tight fallback (flagged)
    return None


def verdict_for(landing, boxes, cache, extra_by_level):
    """Full per-landing evaluation. Returns a result dict."""
    name, (wx, wy, wz), tag = landing
    lv, corner = resolve_level(boxes, wx, wy, wz)
    if lv is None:
        return dict(name=name, tag=tag, world=(wx, wy, wz), level='<void - no box>',
                    verdict='CHECK', reason='landing world point is inside no level box',
                    near=[], onmesh=None, local=None)
    lx, lz = wx - corner[0], wz - corner[2]
    fnorm = lv['fname'].replace('\\', '/').lower()
    entities, ver = cache.entities(lv)
    extra = extra_by_level.get(fnorm, [])
    near = nearest_entities(entities, lx, lz, extra)
    nav = cache.nav(lv)
    onmesh = survey_onmesh(nav, lx, lz)

    def short(e):
        return e[1].rsplit('\\', 1)[-1].rsplit('/', 1)[-1]

    # collision evaluation. DEADLY = a hard/unknown collider within PIN (the reported
    # pin). FAIL = a hard collider within its (larger) class-min. NPC/portal only note.
    deadly = [e for e in near if e[4] in DEADLY_CLASSES and e[0] <= PIN_DIST]
    violations = [e for e in near if e[4] in HARD_FAIL and e[0] < CLASS_MIN[e[4]]]
    notes = []
    for e in near:
        if e[4] == 'npc' and e[0] < NOTE_DIST:
            notes.append(f'crowded: {e[0]:.2f}u from NPC {short(e)}')
        elif e[4] == 'portal' and e[0] < NOTE_DIST:
            notes.append(f'on a portal pad: {e[0]:.2f}u from {short(e)} (verify no travel re-trigger)')
    if onmesh is not None and onmesh['min_clr'] < CLR_FLOOR and onmesh['on_all']:
        notes.append(f'tight footing: {onmesh["min_clr"]*100:.0f}% disc walkable')

    if deadly:
        verdict = 'DEADLY'
        reason = (f'lands {deadly[0][0]:.2f}u from {deadly[0][4]} {short(deadly[0])} '
                  f'(<= PIN {PIN_DIST}u -> player pinned inside the entity)')
    elif violations:
        verdict = 'FAIL'
        v = violations[0]
        reason = f'{v[0]:.2f}u from {v[4]} {short(v)} (class min {CLASS_MIN[v[4]]}u)'
    elif onmesh is not None and onmesh['onmesh_bad']:
        verdict = 'CHECK'
        reason = ('off-mesh in some tileset' if not onmesh['on_all']
                  else f'stranded on a {onmesh["size"]}-cell island')
    else:
        verdict = 'PASS'
        reason = 'clear + on-mesh' + (f'  [notes: {"; ".join(notes)}]' if notes else '')
    return dict(name=name, tag=tag, world=(wx, wy, wz), level=lv['fname'], ver=ver,
                local=(lx, lz), near=near, onmesh=onmesh, verdict=verdict,
                reason=reason, deadly=deadly, violations=violations, notes=notes,
                n_extra=len(extra), lv=lv, corner=corner, entities=entities, extra=extra)


def print_result(r):
    print(f'\n[{r["verdict"]}] {r["name"]:16s} world={tuple(r["world"])} tag={r["tag"]}')
    if r['local'] is None:
        print(f'    {r["reason"]}')
        return
    fn = r['level'].replace('\\', '/').split('World/')[-1].split('world/')[-1]
    extra_note = f' (+{r["n_extra"]} planned)' if r.get('n_extra') else ''
    print(f'    -> {fn} v0x{r["ver"]:02x} local=({r["local"][0]:.1f},{r["local"][1]:.1f}){extra_note}')
    if r['onmesh'] is not None:
        om = r['onmesh']
        cells = '  '.join(f'{S.SETNAMES[i][0]}:d={d:.2f}/clr={clr*100:.0f}%'
                          for i, (d, clr, ok) in enumerate(om['per']))
        state = 'OFF-MESH' if not om['on_all'] else ('ISLAND' if om['tiny_island'] else 'on-mesh')
        print(f'    nav: {cells}  comp#{om["rank"]}/{om["size"]}  {state}')
    else:
        print('    nav: <no 0x0b navmesh in destination level>')
    shown = 0
    for (dist, dbr, x, z, klass, is_extra) in r['near']:
        if klass == 'soft' and shown >= 3:
            continue
        tagx = ' [PLANNED]' if is_extra else ''
        mark = ''
        if klass in DEADLY_CLASSES and dist <= PIN_DIST:
            mark = '  <<< PIN/DEADLY'
        elif klass in HARD_FAIL and dist < CLASS_MIN[klass]:
            mark = f'  <<< < {CLASS_MIN[klass]}u'
        elif klass in ('npc', 'portal') and dist < NOTE_DIST:
            mark = '  <- note'
        short = dbr.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]
        print(f'      d={dist:6.2f}u  {klass:9s} {short:42s} local=({x:.1f},{z:.1f}){tagx}{mark}')
        shown += 1
        if shown >= 8:
            break
    print(f'    => {r["reason"]}')


# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDED landing sets + planned placements for the cross-wave audit.
# ─────────────────────────────────────────────────────────────────────────────
# V1 = the DEPLOYED-map wiring. Preferred source = the LIVE build_quest_files
# (imported below); this embedded copy is a provenance-pinned fallback ONLY.
# Provenance: build_quest_files.HELOS_HUB_TRAVEL @ da918c5 (world signed-int).
V1_LANDINGS = [
    ('garden', (1173, -39, -4001), 'tagSVCHelosToGarden'),
    ('secret', (-2396, 2, -5790), 'tagSVCHelosToSecret'),
    ('sparta', (-5602, -2, -1409), 'tagSVCHelosToSparta'),
    ('uber', (-2438, 10, -2450), 'tagSVCHelosToUber'),
    ('bossarena', (-433, 0, -3602), 'tagSVCTestHubToBossArena'),
    ('warband', (5680, 1, 3285), 'tagSVCHelosToWarband'),
    ('dorus', (312, 1, -8462), 'tagSVCHelosToDorus'),
    ('tantalus', (-342, -15, -10095), 'tagSVCHelosToTantalus'),
    ('charon', (-336, -7, -9650), 'tagSVCHelosToCharon'),
    ('mnemophage', (170, -10, -11438), 'tagSVCHelosToMnemophage'),
    ('ephialtes', (-1828, 3, -13285), 'tagSVCHelosToEphialtes'),
    ('ret_dorus', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_tantalus', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_charon', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_mnemophage', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_ephialtes', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_warband', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
]

# V2 = the b39 hub-v2 landing set (boss destinations RETARGETED to area ENTRANCES,
# deliberately offset from the boss; + devourer/vashkarr/obsidian added).
# Provenance: feat/b39-hub-v2 build_quest_files.HELOS_HUB_TRAVEL @ cf5a0e4.
V2_LANDINGS = [
    ('garden', (1173, -39, -4001), 'tagSVCHelosToGarden'),
    ('secret', (-2396, 2, -5790), 'tagSVCHelosToSecret'),
    ('sparta', (-6588, 1, -3180), 'tagSVCHelosToSparta'),        # Athens catacomb DOOR (retarget)
    ('uber', (-7793, 1, -3793), 'tagSVCHelosToUber'),            # Knossos->Uber maze03 DOOR (retarget)
    ('bossarena', (-433, 0, -3602), 'tagSVCTestHubToBossArena'),
    ('warband', (5699, 1, 3315), 'tagSVCHelosToWarband'),
    ('dorus', (330, 1, -8380), 'tagSVCHelosToDorus'),            # Medea tomb ENTRANCE (~82u off Dorus)
    ('tantalus', (-346, -12, -10131), 'tagSVCHelosToTantalus'),  # Styx swamp stairs (~36u off)
    ('charon', (-480, -12, -9591), 'tagSVCHelosToCharon'),       # Styx Hades-city (walk E to bough)
    ('mnemophage', (169, -10, -11418), 'tagSVCHelosToMnemophage'),  # Mnemosyne stairs (~20u off)
    ('ephialtes', (-1756, 3, -13198), 'tagSVCHelosToEphialtes'), # Dread Halls stairs (~130u off)
    ('devourer', (5345, 1, 3010), 'tagSVCHelosToDevourer'),      # drxbc2 chamber (~92u off Toxeus)
    ('vashkarr', (-227, 1, 146), 'tagSVCHelosToVashkarr'),       # random05a Chang'an cave (~28u off)
    ('obsidian', (-1827, -74, -462), 'tagSVCHelosToObsidian'),   # tombobs02 Obsidian Halls stairs
    ('ret_dorus', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_tantalus', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_charon', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_mnemophage', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_ephialtes', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_warband', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_uber', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_sparta', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_devourer', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_vashkarr', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
    ('ret_obsidian', (-5980, 1, 909), 'tagSVCAreaReturnToHelos'),
]

# B41 planned placements (level-keyed, coords LEVEL-LOCAL). NOT on the current map.
# Provenance: feat/b41-map-pass docs/reports/b41_map_pass_plan.md B41_SPECS.
B41_PLACEMENTS = {
    'xpack/levels/area08_hadespalace/hadespalace_floor04_01.lvl': [
        ('q_polisgaoler_lone', 72.1, 3.2, 37.1), ('ss_warden_behemoth', 66.0, 3.6, 37.5),
        ('ss_warden_behemoth', 78.2, 3.6, 37.5), ('q_polis_limos', 67.1, 3.6, 41.5),
        ('q_polis_bloodwitch', 77.1, 3.6, 41.5), ('q_polis_vindicator', 66.4, 3.6, 36.2),
        ('q_polis_lieutenant', 77.5, 3.6, 36.2),
        (r'drxitem\container\svc_polisvault_chest_01', 65.2, 3.6, 32.6),
        (r'drxitem\container\svc_polisvault_chest_02', 68.5, 3.6, 30.5),
        (r'drxitem\container\svc_polisvault_chest_03', 72.1, 3.6, 29.5),
        (r'drxitem\container\svc_polisvault_chest_04', 75.5, 3.6, 30.5),
        (r'drxitem\container\svc_polisvault_chest_05', 78.8, 3.6, 32.6)],
    'xpack/levels/area08_hadespalace/hadespalace_floor_03.lvl': [
        ('q_hadesmarshal_lone', 155.7, 11.5, 102.3)],
    'xpack/levels/area08_hadespalace/hadespalace_crystal_03.lvl': [
        ('q_general_a_guardpair', 27.83, 27.0, 44.39)],
    'xpack/levels/area08_hadespalace/hadespalace_floor04_04.lvl': [
        ('q_general_b_guardpair', 68.39, 15.0, 40.26)],
    'xpack/levels/area08_hadespalace/hadespalace_crystal_04.lvl': [
        ('q_general_c_guardpair', 72.46, 27.0, 55.98)],
    'xpack/levels/area06_elysian/elysian_fields_03.lvl': [
        ('q_diadochi_lone', 20.7, 4.0, 81.7)],   # Y=4.0 matches b41 build_section_surgery.py:1121
    'xpack/levels/egypt/minidungeons/thebesopttomba.lvl': [
        ('q_neferkha_lone', 32.0, 1.0, 85.0), ('q_sarcophagus_a', 25.0, 1.0, 85.0),
        ('q_sarcophagus_b', 39.0, 1.0, 85.0), ('q_sarcophagus_c', 32.0, 1.0, 79.0),
        ('q_sarcophagus_d', 32.0, 1.0, 91.0)],
    'levels/world/xbloodcave/drxfirstroom.lvl': [
        ('q_bloodtoxeus_ambush', 100.0, 1.0, 50.0)],
}

# B42 STRESS MODEL. As built (feat/b42-waking-dread @ 4b3f2d7) b42 is DB-ONLY: it
# de-dups boss pools (proxyPoolEquation neutralize) and re-tunes existing bespoke-hoard
# LOOT - it adds NO new map placements, hence no new collision sources. This ring is
# therefore a HYPOTHETICAL conservative stress test (NOT b42's actual output): 3 synthetic
# containers ringing each build36 IT boss' CURRENT-MAP local position at radius 5u, to
# prove the v2 ENTRANCE landings keep clearance even if a FUTURE wave ever co-locates
# chests with a boss. Replace with real coords via --extra <file> if one ever does.
# Boss local coords = the q_<boss>_lone positions surveyed from the deployed map.
_B42_BOSSES = {  # level_key: (boss_local_x, boss_local_z)
    'xpack/levels/area02_medea/undergrounds/medea_templeug_tomb01.lvl': (52.0, 60.0),
    'xpack/levels/area04_styx/styx_swampborder_01.lvl': (54.0, 114.3),
    'xpack/levels/area04_styx/styx_riveredge_01.lvl': (187.9, 46.9),
    'xpack/levels/area05_judgment/undergrounds/judgment_templeug_mnemosyne01.lvl': (43.0, 71.0),
    'xpack/levels/area05_judgment/undergrounds/judgment_stonecity_exit01.lvl': (15.9, 34.7),
}


def b42_model_placements():
    specs = {}
    for lk, (bx, bz) in _B42_BOSSES.items():
        ring = []
        for i in range(3):
            ang = math.radians(90 + i * 120)
            ring.append((r'drxitem\container\svc_wakingdread_chest_%02d' % (i + 1),
                         bx + 5.0 * math.cos(ang), 1.0, bz + 5.0 * math.sin(ang)))
        specs[lk] = ring
    return specs


def placements_to_extra(specs):
    """specs {level_key: [(dbr, x, y, z), ...]} -> {level_key: [(dbr,x,y,z,0,klass)]}
    normalized to lowercase '/' level keys for matching resolve_level output."""
    out = {}
    for lk, rows in specs.items():
        key = lk.replace('\\', '/').lower()
        out.setdefault(key, [])
        for (dbr, x, y, z) in rows:
            out[key].append((dbr, x, y, z, 0, classify(dbr)))
    return out


def load_landings_arg(wiring):
    if wiring == 'v1':
        try:
            from build_quest_files import HELOS_HUB_TRAVEL
            # HELOS_HUB_TRAVEL rows are (npc_dbr, (x,y,z), tag) - derive a name from the npc
            out = []
            for (npc, xyz, tag) in HELOS_HUB_TRAVEL:
                nm = npc.rsplit('\\', 1)[-1].replace('svc_helos_trav_', '').replace(
                    'svc_area_return_', 'ret_').replace('.dbr', '')
                out.append((nm, tuple(xyz), tag))
            return out, 'v1 (LIVE build_quest_files.HELOS_HUB_TRAVEL)'
        except Exception as e:
            print(f'  (live import failed: {e}; using embedded V1 fallback)')
            return V1_LANDINGS, 'v1 (embedded fallback)'
    if wiring == 'v2':
        return V2_LANDINGS, 'v2 (feat/b39-hub-v2 @ cf5a0e4)'
    # else a file path exposing LANDINGS
    p = Path(wiring)
    spec = importlib.util.spec_from_file_location('_landings_mod', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.LANDINGS), f'file:{p.name}'


def load_extra_arg(placements):
    if not placements or placements == 'none':
        return {}, 'none'
    if placements == 'b41':
        return placements_to_extra(B41_PLACEMENTS), 'b41 (map-pass plan)'
    if placements == 'b41b42':
        merged = dict(B41_PLACEMENTS)
        for lk, rows in b42_model_placements().items():
            merged.setdefault(lk, [])
            merged[lk] = list(merged[lk]) + rows
        return placements_to_extra(merged), 'b41 + b42-model (3 chests/boss)'
    if placements == 'b42':
        return placements_to_extra(b42_model_placements()), 'b42-model (3 chests/boss)'
    p = Path(placements)
    spec = importlib.util.spec_from_file_location('_extra_mod', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return placements_to_extra(mod.SPECS), f'file:{p.name}'


DEFAULT_MAPS = [
    Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
         r"\CustomMaps\SoulvizierClassicDEV\Resources\Levels.arc"),
    REPO / 'local' / 'Levels_merged.arc',
    REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Levels.arc',
]


def main():
    ap = argparse.ArgumentParser(description='Hub teleport landing-clearance gate.')
    ap.add_argument('--map', help='Levels.arc to gate (default: deployed DEV / local merged)')
    ap.add_argument('--wiring', default='v1',
                    help="'v1' (live) | 'v2' (b39 hub-v2) | path to a .py exposing LANDINGS")
    ap.add_argument('--placements', default='none',
                    help="extra planned placements: 'none'|'b41'|'b42'|'b41b42'|path to .py (SPECS)")
    ap.add_argument('--strict-check', action='store_true',
                    help='treat CHECK (off-mesh/void) as a failure for the exit code')
    ap.add_argument('--nudge', action='store_true',
                    help='for every DEADLY/FAIL landing, spiral-search + print a clear nudged coord')
    args = ap.parse_args()

    map_path = None
    if args.map:
        map_path = Path(args.map)
    else:
        for c in DEFAULT_MAPS:
            if c.exists():
                map_path = c
                break
    if map_path is None or not map_path.exists():
        print('FAIL: no map found (pass --map <Levels.arc>)')
        return 1

    landings, lsrc = load_landings_arg(args.wiring)
    extra_by_level, esrc = load_extra_arg(args.placements)

    print('=' * 78)
    print('GATE G-LAND  hub teleport landing clearance')
    print(f'  map:        {map_path}')
    print(f'  landings:   {lsrc}  ({len(landings)} landings)')
    print(f'  placements: {esrc}' + (f'  ({sum(len(v) for v in extra_by_level.values())} '
          f'planned entities in {len(extra_by_level)} levels)' if extra_by_level else ''))
    print(f'  thresholds: PIN<={PIN_DIST}u  container>={CLASS_MIN["container"]}u  '
          f'monster/proxy>={CLASS_MIN["monster"]}u  prop>={CLASS_MIN["prop"]}u  npc>={CLASS_MIN["npc"]}u')
    print('  loading map (decompress ~685MB)...', flush=True)
    data, levels = S.load_world(str(map_path))
    boxes = build_boxes(levels)
    cache = LevelCache(data)
    print(f'  levels indexed: {len(levels)}')

    results = [verdict_for(l, boxes, cache, extra_by_level) for l in landings]
    for r in results:
        print_result(r)

    counts = {}
    for r in results:
        counts[r['verdict']] = counts.get(r['verdict'], 0) + 1
    deadly = [r for r in results if r['verdict'] == 'DEADLY']
    fails = [r for r in results if r['verdict'] == 'FAIL']
    checks = [r for r in results if r['verdict'] == 'CHECK']
    print('\n' + '=' * 78)
    print(f'SUMMARY  ' + '  '.join(f'{k}={v}' for k, v in sorted(counts.items())))
    if deadly:
        print('  DEADLY (player pinned inside a placed entity - the reported bug):')
        for r in deadly:
            print(f'    - {r["name"]:16s} {r["reason"]}')
    if fails:
        print('  FAIL (dangerously close - nudge recommended):')
        for r in fails:
            print(f'    - {r["name"]:16s} {r["reason"]}')
    if args.nudge:
        todo = [r for r in results if r['verdict'] in ('DEADLY', 'FAIL')]
        if todo:
            print('\n' + '=' * 78)
            print('NUDGE SPECS (closest clear INTEGER-world coord; validated AT the emitted coord)')
            for r in todo:
                nav = cache.nav(r['lv'])
                res = find_nudge(nav, r['entities'], r['extra'], r['local'][0], r['local'][1])
                wx, wy, wz = r['world']
                cx, _cy, cz = r['corner']
                if res is None:
                    print(f'  {r["name"]:14s} {tuple(r["world"])}  -> NO clear spot within range '
                          f'(hand-place; widen the search area)')
                    continue
                nlx, nlz, rad, near_at, om, robust = res
                nwx, nwz = cx + nlx, cz + nlz     # integer corner + integer local = integer world
                b = _binding_collider(near_at)
                binding = (f'{b[1]:.2f}u {b[2]} {b[3].rsplit(chr(92), 1)[-1].rsplit("/", 1)[-1]} '
                           f'(slack {b[0]:+.2f}u vs {b[4]}u min)') if b else 'none within scan'
                clr = '/'.join(f'{c*100:.0f}%' for _d, c, _o in om['per'])
                tag = 'ROBUST' if robust else 'TIGHT - no robust spot in range, hand-verify'
                print(f'  {r["name"]:14s} ({wx},{wy},{wz}) -> ({nwx},{wy},{nwz})  '
                      f'[nudge {rad:.1f}u, {tag}]  binding collider {binding}  clr {clr}')
    bad = bool(deadly or fails) or (args.strict_check and bool(checks))
    print(f'\nGATE G-LAND: {"FAIL" if bad else "PASS"}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
