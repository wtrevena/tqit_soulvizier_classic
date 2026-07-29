#!/usr/bin/env python3
"""b100 - DERIVE the Sanctuary of the Bloodborn population placements.

Deterministic (no RNG, no hash-order dependence): given a built `Levels.arc` it
re-derives the exact `INJECT_SPECS` block that `tools/build_section_surgery.py`
carries for `levels/world/xbloodcave/drxbc3.lvl`. Read-only - it opens the map
and prints; it mutates nothing and writes no file unless `--json` is given.

WHY THIS EXISTS
---------------
The b100 DESIGN pass (docs/reports/b100_sanctuary_recon.md sec 4) proposed four
bands defined by WORLD-X ranges, on the premise that the player "walks strictly
WESTWARD" from the arrival portal to the west threshold. Implementation measured
the actual walk and **that premise is false**:

  * The processional is **690.6 u** of geodesic navmesh path, and **X is not
    monotonic along it** (4411 -> 4290 -> 4306 -> 4210 -> 4187).
  * It **descends four elevation tiers** - the arrival platform at world Y=+2,
    then Y=-10, then Y=-22, then the pit floor at Y=-34 where the west door into
    `drxBC_Finale` actually is (all 36,937 west-seam cells are at Y=-34).
  * The design's probe (`tools/debug/b100_plan.py`) collapsed the level to a flat
    XZ set and never computed a Y at all, so an X-banded placement can put a proxy
    on the wrong tier - i.e. in mid-air or under the floor.

So the design's INTENT is kept verbatim ("population escalates along the one-way
walk, climbing the cult's hierarchy") and its four bands + creature rosters are
kept verbatim, but the band AXIS is replaced by **geodesic route distance**, which
is what "along the walk" actually means. The tier transitions the route makes are
the band boundaries (see BAND_BOUNDS).

FRAME (the trap the design pinned, plus the one it missed)
----------------------------------------------------------
  * `0x05` instance positions are **level-LOCAL** -> world = level corner + local.
  * The `0x0b` REC\\x02 navmesh is in its own **mesh grid frame**, whose origin is
    `center - dims`. For drxBC3 that is world (4128,-60,2798), which is NOT the
    level corner (4186,-37,2869) - the mesh is padded and also rasterizes five
    neighbour levels. `tools/debug/survey_uberboss_spots.py` assumes org == corner,
    which is true for a self-contained level and false here; this module derives
    the frame from the container instead of assuming it.
  * Cell world Y = `org_y + (hmin + heights[i]) * ch`. Verified against all 10
    shipped drxBC3 proxies: max |dY| = 0.02 u.
  * A cell's `areas` byte is the **1-based index into the mesh GUID list of the
    level that OWNS the cell** (rec02_format.py header RE). drxBC3's own GUID is
    index 1, so `area == 1` IS "inside drxBC3's own ground" - a mechanism-derived
    replacement for the design's hand-typed footprint box (they agree: 599,856
    own cells = 23,994 sq u == the design's footprint-restricted figure).

Usage:
  py tools/debug/b100_derive_sanctuary.py --map local/Levels_merged.arc
  py tools/debug/b100_derive_sanctuary.py --map <arc> --json <out.json>
"""
import sys
import struct
import math
import json
import argparse
from pathlib import Path
from collections import deque, Counter

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

import contracts_map as CM                      # noqa: E402
from rec02_format import parse_rec02            # noqa: E402

LEVEL_KEY = 'levels/world/xbloodcave/drxbc3.lvl'
LEVEL_BASENAME = 'drxbc3'
CS = 0.2                      # navmesh cell size (world units)
CELL_AREA = CS * CS
CLIMB = 5                     # navlib.CLIMB: 5 CH steps == 1.0 u (engine model)

# --- the two fixed player anchors (measured from drxBC3's own 0x05) ------------
ARRIVAL = (4411.0, 3089.0)    # GridExitOneWay xprtl_et2fn_02 - where the player lands
SHRINE = (4388.0, 3085.0)     # StrategicMovementRespawnShrine respawn_hades_shrine01

# --- hard placement rules -----------------------------------------------------
# Design sec 4.3 rule 3 kept verbatim. Rule 1 is restated in mesh terms (own-area
# + reachable + on-corridor). Rule 2 is REPLACED - see the block comment below.
CLEAR_ANCHOR = 20.0           # rule 3: b44 landing-clearance precedent
SEP_MIN = 16.0                # R-30 SPACING LAW floor, Chebyshev, EVERY pair
SCREEN = 60.0                 # density model box (same box for every comparator)
SCREEN_CAP = 42               # hard ceiling on the worst 60x60 spawnMax sum.
                              # DERIVED, not chosen: the Sanctuary may not become
                              # denser than the SPARSEST already-shipping blood-cave
                              # level that carries real content. Measured by
                              # tools/debug/b100_density_census.py with this exact
                              # box: yet_another_fucking_connector 42, then
                              # drxBC_finale_transitionconnector 43, drxBC_Connector2
                              # 47, drxBC_Finale 60, drxFirstRoom 69, drxBC2 81.
                              # drxBC3 ships at 24 today. 42 is also the base-game
                              # cave/crypt/tomb p90 measured the same way (44, n=80:
                              # min 9, p25 19, MEDIAN 26, p75 35, max 78), so the
                              # walkway lands inside its own family and inside the
                              # base game's, and stays the sparsest of the blood cave
                              # - which is what a processional should be.
CORRIDOR_SLACK = 60.0         # a cell is ON the processional if walking through it
                              # costs at most this much detour over the best path
CLEAR_RADIUS = 3.0            # a proxy needs room for its pack to materialise
CLEAR_FRACTION = 0.90         # ... this much of that disc must be walkable
PROP_CLEAR = 3.0              # never inside a placed prop (the b44 defect class)
EDGE_CLEAR = 10.0             # never within this of drxBC3's own footprint edge.
                              # The b44 landing-clearance class applies to a WALK-IN
                              # seam too: the player crosses x=4186 into drxBC_Finale
                              # and must not arrive inside a pack with no reaction
                              # time. It also keeps every spawned monster inside
                              # drxBC3's own streaming region instead of straddling
                              # a level boundary. Without it the derivation put an
                              # 8-spawn abom_dancer_spear_mix at world x=4186.5,
                              # i.e. 0.5 u from the exit door.
FOOTPRINT = (4186.0, 4426.0, 2869.0, 3109.0)   # drxBC3's declared X0,X1,Z0,Z1
PARTY_SPAWNMAX = 6            # reporting only (what the design called a "party")

# WHY RULE 2 CHANGED. The design's rule 2 was "two spawnMax>=6 proxies never within
# 34 u of each other on both axes; any other pair never within 16 u", justified as
# "this is what holds the screen load down". Measured, it is unsatisfiable once the
# placements also have to be reachable, on the processional, clear of the props and
# clear of the arrival anchors: the roster contains SEVEN spawnMax>=6 proxies and
# the level already ships FIVE more, and band 2's party-eligible ground is 258 sq u
# against a 34 u Chebyshev exclusion of up to 68x68 = 4,624 sq u per proxy.
# So the INTENT is enforced directly instead of through a proxy variable:
#   * SEP_MIN 16 u Chebyshev between EVERY pair - this is R-30's own spacing law
#     ("you need to space these monsters out instead of putting them all on top of
#     one another"), applied universally rather than only to the small pairs.
#   * SCREEN_CAP - the worst axis-aligned 60x60 world-unit box anywhere on the
#     walkway may not exceed 24 summed spawnMax, enforced DURING selection, not
#     merely reported afterwards. The design's own target was 18 and its stated
#     ceiling was the base-game p90 of 70; 24 sits below every blood-cave sibling
#     already shipping (drxBC_Connector2 23 is the sparsest, drxBC2 72 the densest).
# The 34 u rule was only ever a sufficient condition for the cap; the cap is the
# thing Will actually cares about, and it is now the thing that is gated.

# --- band boundaries in GEODESIC ROUTE DISTANCE from the arrival portal --------
# 120.0 : a design CHOICE - the length of "the arrival breath". It has to clear
#         CLEAR_ANCHOR around both anchors, which alone rules out the whole 538
#         sq u arrival platform (a 20 u disc is 1,257 sq u), so band 1 necessarily
#         starts after the ramp.
# 265.0 : MEASURED - where the route leaves the Y=-10 tier for the Y=-22 tier.
# 460.0 : MEASURED - where the route leaves Y=-22 for the Y=-34 pit floor.
BAND_BOUNDS = (120.0, 265.0, 460.0)

P = 'records\\drxmap\\proxy\\'
BANDS = [
    ('1 THE OUTER COURT', [(P + 'bw_acolyte_lone.dbr', 2)]),
    ('2 THE CONGREGATION', [(P + 'zparty_witchfest_2099.dbr', 2),
                            (P + 'bw_acolyte_clutch.dbr', 2)]),
    ('3 THE CLERGY', [(P + 'bw_priest_houndmaster.dbr', 2),
                      (P + 'bw_priest_lone.dbr', 1),
                      (P + 'hound_01_pack.dbr', 1)]),
    ('4 THE THRESHOLD', [(P + 'abom_dancer_spear_mix.dbr', 2),
                         (P + 'abom_ravager_lone.dbr', 1),
                         (P + 'q_shaman_lone.dbr', 1)]),
]


# --------------------------------------------------------------------------- #
class Sanctuary:
    """Everything measured off one built map, in one place, so the gate and the
    derivation cannot drift apart."""

    def __init__(self, map_path, arz_path=None):
        self.map_path = str(map_path)
        arc = CM.Arc.from_file(self.map_path)
        mp = arc.world_map()
        secs = CM.parse_top_sections(mp)
        levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
        idx = None
        for i, lv in enumerate(levels):
            base = lv['fname'].replace('\\', '/').split('/')[-1].replace('.lvl', '').lower()
            if base == LEVEL_BASENAME:
                idx = i
                break
        assert idx is not None, f'{LEVEL_BASENAME}.lvl not found in {map_path}'
        self.level_index = idx
        lv = levels[idx]
        self.corner = tuple(lv['corner'])
        self.blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        self.blob_version = self.blob[3]
        own_guid = struct.pack('<4I', *struct.unpack_from('<13I', lv['ints_raw'], 0)[9:13]).hex()

        sec0b = [d for t, d in CM.parse_blob_sections(self.blob) if t == 0x0b]
        assert len(sec0b) == 1, f'expected exactly one 0x0b section, got {len(sec0b)}'
        self.nav_raw = sec0b[0]
        doc = parse_rec02(self.nav_raw, decompress=True)
        guids = [g.hex() for g in doc['guids']]
        assert own_guid in guids, 'drxBC3 own GUID is not in its own navmesh GUID list'
        self.own_area = guids.index(own_guid) + 1
        self.org = (doc['center'][0] - doc['dims'][0],
                    doc['center'][1] - doc['dims'][1],
                    doc['center'][2] - doc['dims'][2])
        assert len(doc['sets']) == 3, 'engine requires exactly 3 tilesets'
        self.ch = doc['sets'][0]['params']['ch']
        assert abs(doc['sets'][0]['params']['cs'] - CS) < 1e-5

        # per-tileset cell maps; the engine needs all 3, so a placement must be
        # walkable in all 3 (asserted rather than assumed).
        self.sets = [self._cells(doc, i) for i in range(3)]
        self.cells, self.areas = self.sets[0]
        for k, (c, a) in enumerate(self.sets[1:], 2):
            assert c == self.cells and a == self.areas, \
                f'tileset {k} differs from tileset 1 - placements would not hold on all difficulties'

        self.own = {k for k in self.cells if self.areas[k] == self.own_area}
        # instances
        self.instances = CM.parse_0x05(self.blob)[1]
        if arz_path:
            arz = CM.Arz.from_arz(str(arz_path))
            self._cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}
            self._names = {CM.norm_rec(x): x for x in arz.record_names()}
            self._arz = arz
        else:
            self._cls = self._names = self._arz = None

    def _cells(self, doc, si):
        cm, ar = {}, {}
        for rec in doc['sets'][si]['records']:
            h = rec['hdr']
            w, ht, hmin = h['width'], h['height'], h['hmin']
            tx, ty = h['tx'], h['ty']
            hs, aa = rec['heights'], rec['areas']
            for lz in range(ht):
                row = lz * w
                for lx in range(w):
                    i = row + lx
                    if hs[i] == 0xff or aa[i] == 0:
                        continue
                    k = (tx * w + lx, ty * ht + lz)
                    cm[k] = hmin + hs[i]
                    ar[k] = aa[i]
        return cm, ar

    # --- frame helpers -----------------------------------------------------
    def wx(self, gcx):
        return self.org[0] + (gcx + 0.5) * CS

    def wz(self, gcz):
        return self.org[2] + (gcz + 0.5) * CS

    def wy(self, habs):
        return self.org[1] + habs * self.ch

    def cell_at(self, x, z):
        return (int(round((x - self.org[0]) / CS - 0.5)),
                int(round((z - self.org[2]) / CS - 0.5)))

    def nearest_cell(self, x, z, max_r=8.0):
        k0 = self.cell_at(x, z)
        best, bd = None, 1e18
        rr = int(math.ceil(max_r / CS))
        for dx in range(-rr, rr + 1):
            for dz in range(-rr, rr + 1):
                k = (k0[0] + dx, k0[1] + dz)
                if k not in self.cells:
                    continue
                d = (self.wx(k[0]) - x) ** 2 + (self.wz(k[1]) - z) ** 2
                if d < bd:
                    bd, best = d, k
        return best, math.sqrt(bd) if best else float('inf')

    # --- graph -------------------------------------------------------------
    def bfs(self, seeds):
        d = {s: 0 for s in seeds if s in self.cells}
        q = deque(d)
        while q:
            c = q.popleft()
            hc, dc = self.cells[c], d[c]
            for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (c[0] + dx, c[1] + dz)
                if n in d or n not in self.cells:
                    continue
                if abs(self.cells[n] - hc) <= CLIMB:
                    d[n] = dc + 1
                    q.append(n)
        return d

    def route(self):
        """(d_from_arrival, d_from_west_seam, best_total_cells). Cached."""
        if getattr(self, '_route', None) is None:
            ac, _ = self.nearest_cell(*ARRIVAL)
            assert ac is not None, 'arrival portal is not on the navmesh'
            darr = self.bfs([ac])
            # the west threshold into drxBC_Finale: own-footprint z-span, x < 4187
            west = [k for k in self.cells
                    if k in darr and self.wx(k[0]) < 4187.0
                    and 2869.0 <= self.wz(k[1]) <= 3109.0]
            assert west, 'no reachable west-seam cell - the processional does not exist'
            dwest = self.bfs(west)
            best = min(darr[k] + dwest[k] for k in self.own if k in darr and k in dwest)
            self._route = (darr, dwest, best, ac)
        return self._route

    # --- placement filters --------------------------------------------------
    def prop_positions(self):
        cx, _cy, cz = self.corner
        return [(cx + it['pos'][0], cz + it['pos'][2]) for it in self.instances]

    def clearance(self, k):
        """Fraction of a filled CLEAR_RADIUS disc around cell k that is walkable."""
        n = 6
        hit = tot = 0
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                if i * i + j * j > n * n:
                    continue
                tot += 1
                if (k[0] + int(round(i * CLEAR_RADIUS / n / CS)),
                        k[1] + int(round(j * CLEAR_RADIUS / n / CS))) in self.cells:
                    hit += 1
        return hit / tot if tot else 0.0

    def candidates(self):
        """Every cell that satisfies EVERY hard filter, with its route distance."""
        darr, dwest, best, _ac = self.route()
        props = self.prop_positions()
        propgrid = {}
        for (px, pz) in props:
            propgrid.setdefault((int(px // 4), int(pz // 4)), []).append((px, pz))
        out = {}
        for k in self.own:
            if k not in darr or k not in dwest:
                continue                                  # F3 reachability
            if (darr[k] + dwest[k] - best) * CS > CORRIDOR_SLACK:
                continue                                  # F4 on the processional
            x, z = self.wx(k[0]), self.wz(k[1])
            if (max(abs(x - ARRIVAL[0]), abs(z - ARRIVAL[1])) < CLEAR_ANCHOR
                    or max(abs(x - SHRINE[0]), abs(z - SHRINE[1])) < CLEAR_ANCHOR):
                continue                                  # F5 landing clearance
            fx0, fx1, fz0, fz1 = FOOTPRINT
            if not (fx0 + EDGE_CLEAR <= x <= fx1 - EDGE_CLEAR
                    and fz0 + EDGE_CLEAR <= z <= fz1 - EDGE_CLEAR):
                continue                                  # F8 level-edge clearance
            gx, gz = int(x // 4), int(z // 4)
            near = False
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for (px, pz) in propgrid.get((gx + a, gz + b), ()):
                        if (px - x) ** 2 + (pz - z) ** 2 < PROP_CLEAR ** 2:
                            near = True
                            break
                    if near:
                        break
                if near:
                    break
            if near:
                continue                                  # F7 not inside a prop
            if self.clearance(k) < CLEAR_FRACTION:
                continue                                  # F6 room for the pack
            out[k] = darr[k] * CS
        return out

    # --- arz helpers --------------------------------------------------------
    def spawn_max(self, dbr):
        if self._arz is None:
            return None
        n = CM.norm_rec(dbr)
        if n not in self._names:
            return None
        pool = self._arz.field(self._names[n], 'pool1')
        if isinstance(pool, list):
            pool = pool[0] if pool else None
        if not pool:
            return 0
        pn = CM.norm_rec(pool)
        if pn not in self._names:
            return 0
        v = self._arz.field(self._names[pn], 'spawnMax')
        if isinstance(v, list):
            v = v[0] if v else 0
        return int(v or 0)

    def existing_proxies(self):
        """(world x, world z, dbr, spawnMax) for every MONSTER proxy already placed.
        `proxy_shrinepalace` is a shrine proxy, not a monster proxy - excluded, the
        same cut the design pass made."""
        cx, _cy, cz = self.corner
        out = []
        for it in self.instances:
            d = it['dbr'].decode('latin-1')
            if self._cls is not None and self._cls.get(CM.norm_rec(d)) != 'Proxy':
                continue
            if 'shrine' in d.lower():
                continue
            out.append((cx + it['pos'][0], cz + it['pos'][2], d, self.spawn_max(d) or 0))
        return out


def sep_ok(x, z, committed):
    """R-30 SPACING LAW floor - Chebyshev, every pair, no exceptions."""
    for (qx, qz, _qd, _qs) in committed:
        if max(abs(x - qx), abs(z - qz)) < SEP_MIN:
            return False
    return True


def worst_screen(points):
    """EXACT worst axis-aligned SCREEN x SCREEN box, by the standard argument that an
    optimal box can be slid until its low corner is pinned by a point on each axis.
    Enumerating (px, qz) over all points is therefore exhaustive, not a sample."""
    if not points:
        return 0, None
    w, at = 0, None
    xs = sorted({p[0] for p in points})
    zs = sorted({p[1] for p in points})
    for x0 in xs:
        for z0 in zs:
            tot = sum(s for (px, pz, _d, s) in points
                      if x0 <= px <= x0 + SCREEN and z0 <= pz <= z0 + SCREEN)
            if tot > w:
                w, at = tot, (x0 + SCREEN / 2, z0 + SCREEN / 2)
    return w, at


def derive(s):
    """Deterministic farthest-point insertion. No RNG: the winner is the candidate
    with the largest minimum Chebyshev distance to everything already committed,
    ties broken by (-route distance, -gcx, -gcz) - a total order, so the result is
    reproducible byte-for-byte on any machine and any Python build.

    Every candidate is rejected up front unless it keeps BOTH hard invariants:
    the SEP_MIN spacing floor and the SCREEN_CAP density ceiling."""
    cand = s.candidates()
    existing = s.existing_proxies()
    committed = list(existing)
    placed = []
    bounds = (0.0,) + BAND_BOUNDS + (float('inf'),)
    report = []
    for bi, (label, roster) in enumerate(BANDS):
        lo, hi = bounds[bi], bounds[bi + 1]
        band = {k: r for k, r in cand.items() if lo <= r < hi}
        report.append((label, lo, hi, len(band)))
        for dbr, n in roster:
            smax = s.spawn_max(dbr) or 0
            for _ in range(n):
                ranked = []
                for k, r in band.items():
                    x, z = s.wx(k[0]), s.wz(k[1])
                    if not sep_ok(x, z, committed):
                        continue
                    md = min(max(abs(x - qx), abs(z - qz)) for (qx, qz, _d, _sm) in committed)
                    ranked.append(((md, -r, -k[0], -k[1]), k, x, z))
                ranked.sort(key=lambda t: t[0], reverse=True)
                bestk = None
                for _score, k, x, z in ranked:
                    if worst_screen(committed + [(x, z, dbr, smax)])[0] <= SCREEN_CAP:
                        bestk = k
                        break
                assert bestk is not None, (
                    f'no rule-satisfying cell left in band {label} for {dbr} - '
                    f'{len(band)} band cells, {len(ranked)} passed the {SEP_MIN:.0f}u '
                    f'spacing floor, none kept the worst 60x60 box at or under '
                    f'{SCREEN_CAP}. Widen the band, widen the corridor, or cut the roster.')
                x, z = s.wx(bestk[0]), s.wz(bestk[1])
                y = s.wy(s.cells[bestk])
                committed.append((x, z, dbr, smax))
                placed.append(dict(band=label, dbr=dbr, cell=bestk,
                                   world=(x, y, z), route=cand[bestk], spawnMax=smax))
                del band[bestk]
    return placed, existing, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    ap.add_argument('--arz', default=str(REPO.parent.parent.parent /
                                         'work' / 'SoulvizierClassic' / 'Database' /
                                         'SoulvizierClassic.arz'))
    ap.add_argument('--json', default=None)
    a = ap.parse_args()

    s = Sanctuary(a.map, a.arz)
    print(f'map    : {a.map}')
    print(f'level  : {LEVEL_KEY}  idx={s.level_index}  blob v0x{s.blob_version:02x}  '
          f'0x05 stride={CM.blob_0x05_base(s.blob)}')
    print(f'corner : {s.corner}    mesh org: {s.org}    own area id: {s.own_area}')
    print(f'own-area walkable: {len(s.own)} cells = {len(s.own) * CELL_AREA:.0f} sq u')
    darr, dwest, best, _ac = s.route()
    print(f'processional     : {best * CS:.1f} u geodesic, arrival {ARRIVAL} -> west seam x<4187')

    cand = s.candidates()
    print(f'candidate cells (all hard filters): {len(cand)} = {len(cand) * CELL_AREA:.0f} sq u')

    placed, existing, report = derive(s)
    print('\n=== bands (geodesic route distance from the arrival portal) ===')
    for label, lo, hi, n in report:
        hs = 'end' if hi == float('inf') else f'{hi:.0f}'
        print(f'  {label:22s} route [{lo:.0f},{hs}) u   candidates {n:6d} = {n * CELL_AREA:7.0f} sq u')

    cx, cy, cz = s.corner
    print('\n=== derived placements (LEVEL-LOCAL, ready for INJECT_SPECS) ===')
    cur = None
    for p in placed:
        if p['band'] != cur:
            cur = p['band']
            print(f'  # --- {cur} ---')
        wxx, wyy, wzz = p['world']
        lx, ly, lz = wxx - cx, wyy - cy, wzz - cz
        print("        (P + '%s', %.3f, %.3f, %.3f),"
              "   # route %5.1fu  world(%.1f,%.1f,%.1f) spawnMax=%d"
              % (p['dbr'].split('\\')[-1], lx, ly + 0.005, lz,
                 p['route'], wxx, wyy, wzz, p['spawnMax']))

    allp = [(p['world'][0], p['world'][2], p['dbr'], p['spawnMax']) for p in placed]
    w0, _ = worst_screen(existing)
    w1, at1 = worst_screen(existing + allp)
    area = len(s.own) * CELL_AREA
    print('\n=== density ===')
    print(f'  proxies      : {len(existing)} existing + {len(placed)} new = {len(existing) + len(placed)}')
    print(f'  total spawnMax: {sum(p[3] for p in existing)} -> '
          f'{sum(p[3] for p in existing) + sum(p["spawnMax"] for p in placed)}')
    print(f'  sq u / proxy : {area / len(existing):.0f} -> {area / (len(existing) + len(placed)):.0f}')
    print(f'  worst {SCREEN:.0f}x{SCREEN:.0f} screen (spawnMax sum): {w0} -> {w1}'
          + (f'  at world({at1[0]:.0f},{at1[1]:.0f})' if at1 else ''))

    if a.json:
        Path(a.json).write_text(json.dumps(
            [dict(band=p['band'], dbr=p['dbr'], world=list(p['world']),
                  local=[p['world'][0] - cx, p['world'][1] - cy + 0.005, p['world'][2] - cz],
                  route=p['route'], spawnMax=p['spawnMax']) for p in placed], indent=1))
        print(f'\nwrote {a.json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
