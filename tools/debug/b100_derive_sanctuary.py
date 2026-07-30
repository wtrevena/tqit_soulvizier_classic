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
import re
import struct
import math
import json
import argparse
from pathlib import Path
from collections import deque

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

# --- what drxBC3 SHIPS, before this lane touches it ---------------------------
# These two numbers ARE the RETIREMENT PROTOCOL invariant, so they are constants
# rather than whatever the input map happens to hold. amgoz1's drxBC3 carries 281
# placed 0x05 instances of which TEN are monster proxies, and our merge is
# placement-IDENTICAL to pristine SV 0.98i on both counts.
# They also make the derivation fail LOUD if it is pointed at a map that already
# carries this lane's placements: `existing_proxies()` would then return 24 and the
# derivation would silently treat its own output as pre-existing content and produce
# garbage. Round 1's reproduce command did not guard that; this does.
BASELINE_INSTANCES = 281
BASELINE_PROXIES = 10

# --- hard placement rules -----------------------------------------------------
# Design sec 4.3 rule 3 kept verbatim. Rule 1 is restated in mesh terms (own-area
# + reachable + on-corridor). Rule 2 is REPLACED - see the block comment below.
CLEAR_ANCHOR = 20.0           # rule 3: b44 landing-clearance precedent
SEP_MIN = 16.0                # spacing floor, Chebyshev, EVERY pair. PROVENANCE, so
                              # nobody mistakes it for a ruling: this number is the
                              # DESIGN PASS's own (recon sec 4.3 rule 2, "any other
                              # pair never within 16 u"). R-30 is the LAW it serves
                              # ("you need to space these monsters out instead of
                              # putting them all on top of one another") but R-30
                              # states NO distance - it is a shape requirement, not a
                              # number. So 16.0 is a CHOICE that implements R-30, not
                              # a quantity R-30 fixes; it belongs on the same
                              # "constants, not laws" list as SCREEN_CAP_EFF,
                              # CORRIDOR_SLACK and EDGE_CLEAR. R-30 remains PENDING
                              # and this lane does not change its status.
SCREEN = 60.0                 # density model box (same box for every comparator)

# ---------------------------------------------------------------------------- #
# DENSITY IS GATED IN **EFFECTIVE ENTITIES**, NOT RAW `spawnMax`.
#
# ROUND-2 CORRECTION (this was a real defect in the round-1 numbers). A pool's
# `spawnMax` is NOT how many monsters the engine spawns: the pool's
# `proxyPoolEquation` record carries a `spawnMaxEquation` that multiplies it.
# MEASURED in the built arz:
#   records\proxies orient\proxypoolequation_01.dbr
#       poolValue * (2.623966 + 1.076769*nP - 0.100485*nP^2)  -> 3.60025x at nP=1
#   records\proxies orient\proxypoolequation_02.dbr
#       poolValue * (0.91     + 0.497143*nP - 0.05*nP^2)      -> 1.357143x at nP=1
# EVERY blood-cave pool uses _02; 854 of the 887 pool references in the base-game
# cave/crypt/tomb cohort use _01. So round 1's cross-family comparison ("42 is
# also the base-game cave/crypt/tomb p90") compared RAW field values across two
# different multipliers and was invalid as written. Corrected, measured with the
# identical 60x60 box (tools/debug/b100_density_census.py --effective):
#   blood cave, EFFECTIVE worst screen: drxBC2 109.9, drxFirstRoom 104.4,
#     drxBC_Finale 81.4, drxBC_Connector2 63.8, drxBC_finale_transitionconnector
#     58.4, yet_another_fucking_connector 57.0, drxBC3 32.6 today.
#   base-game cave/crypt/tomb (n=80), EFFECTIVE: min 27.2, p25 68.4, MEDIAN 90.0,
#     p75 126.0, p90 158.4, max 280.8.
# The direction of round 1's error was CONSERVATIVE - the change is further below
# base-game density than it claimed - but the numbers Will is handed must be right.
#
# The cap itself is unchanged in substance and DERIVED, not chosen: the Sanctuary
# may not become denser than the SPARSEST already-shipping blood-cave level that
# carries real content, which is yet_another_fucking_connector at 57.0 effective.
# Because every proxy in drxBC3 (all 24, ours included) uses _02, effective is an
# exact 1.357143x rescale of raw WITHIN this level, so re-expressing the cap in
# effective units moves NO placement - it only makes the constant comparable
# across families. 57.0 eff == 42 raw exactly.
# ---------------------------------------------------------------------------- #
SCREEN_CAP_EFF = 57.0
NPLAYERS = 1                  # the multiplier is player-count dependent; single
                              # player is the worst case for density per player and
                              # the case Will tests. MP raises every level in the
                              # comparison by the same factor, so the ranking holds.
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
#   * SEP_MIN 16 u Chebyshev between EVERY pair - the shape R-30 demands, at the
#     design pass's own distance (see the SEP_MIN provenance note above).
#   * SCREEN_CAP_EFF - the worst axis-aligned 60x60 world-unit box anywhere on the
#     walkway may not exceed 57.0 EFFECTIVE entities, enforced DURING selection,
#     not merely reported afterwards. That is the sparsest already-shipping
#     blood-cave level with real content, and it is 63% of the base-game
#     cave/crypt/tomb MEDIAN (90.0) and 36% of its p90 (158.4), all measured with
#     the same box and the same multiplier treatment.
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


def parse_0x05_raw(blob):
    """Per-instance FULL BYTE SHAPE of the 0x05 section, which `contracts_map.
    parse_0x05` does not expose: it drops the 36 rotation bytes.

    Returns a list of dicts (dbr bytes, rot 36 raw bytes, pos 12 raw bytes, flags,
    uid). The RETIREMENT PROTOCOL check needs this: "the shipped instances are
    untouched" is a claim about BYTES, and comparing decoded float triples would miss
    a rotation edit or a -0.0/NaN rewrite. The dbr STRING is carried rather than its
    table index, because an injection legitimately appends to the string table and
    would shift indices without touching any shipped instance.

    Stride is derived from `contracts_map.blob_0x05_base` - NEVER hardcoded. It is 72
    bytes for blob v0x11/v0x0f and 56 otherwise (drxBC3 is v0x0e -> 56); hardcoding 72
    silently desyncs the walk and drops records without erroring, which is the
    documented BUILD46 census bug that omitted 418 of 496 v0x0e levels."""
    base = CM.blob_0x05_base(blob)
    d = None
    for t, sd in CM.parse_blob_sections(blob):
        if t == 0x05:
            d = sd
            break
    if d is None:
        return []
    sc = struct.unpack_from('<I', d, 0)[0]
    pos = 4
    strings = []
    for _ in range(sc):
        sl = struct.unpack_from('<I', d, pos)[0]
        pos += 4
        strings.append(d[pos:pos + sl])
        pos += sl
    ic = struct.unpack_from('<I', d, pos)[0]
    pos += 4
    out = []
    for i in range(ic):
        if pos + base > len(d):
            break
        sidx = struct.unpack_from('<I', d, pos)[0]
        flags = struct.unpack_from('<I', d, pos + 52)[0]
        out.append(dict(i=i, dbr=strings[sidx] if sidx < len(strings) else b'?',
                        rot=d[pos + 4:pos + 40], posb=d[pos + 40:pos + 52],
                        flags=flags,
                        uid=d[pos + 56:pos + 72] if flags != 0 else None,
                        pos=struct.unpack_from('<3f', d, pos + 40)))
        pos += base + (16 if flags != 0 else 0)
    return out


def inst_key(it):
    """The full byte identity of one placed instance, order-independent of the
    string table."""
    return (it['dbr'], it['rot'], it['posb'], it['flags'], it['uid'])


# --------------------------------------------------------------------------- #
class Sanctuary:
    """Everything measured off one built map, in one place, so the gate and the
    derivation cannot drift apart."""

    def __init__(self, map_path, arz_path=None, strict=True):
        """strict=True (the derivation): a malformed navmesh is an AssertionError.
        strict=False (the GATE): a malformed navmesh is RECORDED in self.nav_error and
        the object still exposes `nav_raw` + `instances`, so the gate can report a
        G10/G3 FAIL instead of dying with a traceback. ROUND-2 FIX: round 1 asserted
        unconditionally in here, so the two b89-class navmesh plants (flip one byte /
        truncate the 0x0b container) aborted the gate with an uncaught AssertionError
        rather than failing the invariant that owns them. Exit code was still non-zero,
        so it was fail-SAFE, but it was not the PASS/FAIL behaviour the gate claims."""
        self.map_path = str(map_path)
        self.strict = strict
        self.nav_error = None
        self.tileset_diffs = []
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

        # instances FIRST - they do not depend on the navmesh, so a corrupt 0x0b must
        # not cost the gate its ability to check the roster / retirement protocol.
        self.instances = CM.parse_0x05(self.blob)[1]
        self.raw_instances = parse_0x05_raw(self.blob)

        sec0b = [d for t, d in CM.parse_blob_sections(self.blob) if t == 0x0b]
        self.nav_raw = sec0b[0] if len(sec0b) == 1 else b''
        self.own_area = None
        self.org = None
        self.ch = None
        self.sets = []
        self.cells, self.areas, self.own = {}, {}, set()
        try:
            if len(sec0b) != 1:
                raise ValueError(f'expected exactly one 0x0b section, got {len(sec0b)}')
            doc = parse_rec02(self.nav_raw, decompress=True)
            guids = [g.hex() for g in doc['guids']]
            if own_guid not in guids:
                raise ValueError('drxBC3 own GUID is not in its own navmesh GUID list')
            self.own_area = guids.index(own_guid) + 1
            self.org = (doc['center'][0] - doc['dims'][0],
                        doc['center'][1] - doc['dims'][1],
                        doc['center'][2] - doc['dims'][2])
            if len(doc['sets']) != 3:
                raise ValueError(f'engine requires exactly 3 tilesets, got '
                                 f'{len(doc["sets"])}')
            self.ch = doc['sets'][0]['params']['ch']
            if abs(doc['sets'][0]['params']['cs'] - CS) >= 1e-5:
                raise ValueError(f'cell size {doc["sets"][0]["params"]["cs"]} != {CS}')
            # per-tileset cell maps. The engine needs all 3, so a placement must be
            # walkable in all 3. ROUND-2 FIX: round 1 ASSERTED the three tilesets were
            # cell-for-cell identical right here, which made the gate's "walkable in
            # ALL 3 tilesets" row a tautology of the tileset-1 test and turned a
            # genuine tileset divergence into a constructor crash. The comparison is
            # now RECORDED and the gate reports it as its own invariant.
            self.sets = [self._cells(doc, i) for i in range(3)]
            self.cells, self.areas = self.sets[0]
            for k, (c, a) in enumerate(self.sets[1:], 2):
                if c != self.cells or a != self.areas:
                    self.tileset_diffs.append(k)
            self.own = {k for k in self.cells if self.areas[k] == self.own_area}
        except Exception as exc:                      # noqa: BLE001 - reported, not hidden
            self.nav_error = f'{type(exc).__name__}: {exc}'
            if strict:
                raise
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
    def _pool_of(self, dbr):
        if self._arz is None:
            return None
        n = CM.norm_rec(dbr)
        if n not in self._names:
            return None
        pool = self._arz.field(self._names[n], 'pool1')
        if isinstance(pool, list):
            pool = pool[0] if pool else None
        if not pool:
            return None
        pn = CM.norm_rec(pool)
        return self._names.get(pn)

    def spawn_max(self, dbr):
        """The pool's RAW `spawnMax` field. NOT the number the engine spawns - see
        `multiplier` / `effective`."""
        if self._arz is None:
            return None
        pn = self._pool_of(dbr)
        if pn is None:
            return 0 if CM.norm_rec(dbr) in (self._names or {}) else None
        v = self._arz.field(pn, 'spawnMax')
        if isinstance(v, list):
            v = v[0] if v else 0
        return int(v or 0)

    def multiplier(self, dbr):
        """The pool's `proxyPoolEquation` -> `spawnMaxEquation` factor at NPLAYERS.

        The equations shipped in this database are all of the exact form
        `poolValue * (<polynomial in numberOfPlayers>)`, so the factor is the
        polynomial. A pool with NO equation record spawns `spawnMax` as-is -> 1.0.
        Anything that does not match that form returns None so the caller can fail
        loud instead of silently pretending the factor is 1.0."""
        if self._arz is None:
            return None
        pn = self._pool_of(dbr)
        if pn is None:
            return None
        if not hasattr(self, '_multc'):
            self._multc = {}
        if pn in self._multc:
            return self._multc[pn]
        eq = self._arz.field(pn, 'proxyPoolEquation')
        if isinstance(eq, list):
            eq = eq[0] if eq else None
        m = 1.0                                  # no equation record -> raw spawnMax
        if eq:
            k = CM.norm_rec(eq)
            m = None
            if k in self._names:
                expr = self._arz.field(self._names[k], 'spawnMaxEquation')
                if isinstance(expr, list):
                    expr = expr[0] if expr else None
                if expr:
                    mm = re.match(r'^\s*poolValue\s*\*\s*(.*)$', str(expr), re.I)
                    if mm:
                        try:
                            m = float(eval(  # noqa: S307 - fixed-form arithmetic only
                                mm.group(1).replace('numberOfPlayers', str(NPLAYERS)),
                                {'__builtins__': {}}, {}))
                        except Exception:
                            m = None
        self._multc[pn] = m
        return m

    def effective(self, dbr):
        """spawnMax * multiplier = the entities the engine actually spawns."""
        sm = self.spawn_max(dbr)
        m = self.multiplier(dbr)
        if sm is None:
            return None
        if m is None:
            return None
        return sm * m

    def existing_proxies(self):
        """(world x, world z, dbr, effective) for every MONSTER proxy already placed.
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
            eff = self.effective(d)
            assert eff is not None or self._arz is None, (
                f'{d}: could not resolve an effective spawn count - refusing to '
                f'silently treat an unparsed spawnMaxEquation as 1.0')
            out.append((cx + it['pos'][0], cz + it['pos'][2], d, eff or 0.0))
        return out


def sep_ok(x, z, committed):
    """The SEP_MIN spacing floor - Chebyshev, every pair, no exceptions."""
    for (qx, qz, _qd, _qs) in committed:
        if max(abs(x - qx), abs(z - qz)) < SEP_MIN:
            return False
    return True


def worst_screen(points):
    """EXACT worst axis-aligned SCREEN x SCREEN box, by the standard argument that an
    optimal box can be slid until its low corner is pinned by a point on each axis.
    Enumerating (px, qz) over all points is therefore exhaustive, not a sample.

    `points` are (x, z, dbr, weight); the weight is EFFECTIVE entities everywhere in
    this module (see the SCREEN_CAP_EFF block)."""
    if not points:
        return 0.0, None
    w, at = 0.0, None
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
    """Deterministic GROUP-CLUSTERED insertion: a congregation at rite, not a patrol.

    ROUND-2 CORRECTION - THE ROUND-1 MECHANISM PRODUCED THE OPPOSITE OF THE STATED
    DESIGN. Round 1 used farthest-point insertion, which MAXIMISES the minimum
    spacing, i.e. it is the most evenly spread arrangement the filters permit. That
    is precisely the "evenly spaced patrol" the design and the amgoz1 bar forbid.
    MEASURED on the round-1 build: the 14 new proxies had nearest-neighbour Chebyshev
    min 23.2 u / median 31.8 u, while amgoz1's own ten shipped drxBC3 proxies measure
    min 7.4 u / median 41.9 u - he CLUSTERS, and round 1 could not. So the ledger
    recorded an intent the code contradicted, and the content was the generic filler
    the bar exists to prevent.

    THE SHAPE IS NOW TWO-MODE, which is what a congregation actually looks like and
    what amgoz1's own measured distribution looks like (tight knots, wide gaps):

      * GROUP ANCHOR (the first member of each roster entry) - farthest-point: the
        candidate whose minimum Chebyshev distance to everything already committed is
        LARGEST. This is what puts distinct groups in distinct places along the walk,
        and it reproduces round 1's behaviour for the four singleton groups.
      * GROUP MEMBERS (every subsequent member of the same roster entry) - nearest
        -point: the candidate CLOSEST to that group's own anchor. Two novices kneel
        TOGETHER; the witchfest is a knot; the houndmasters are a pair. Members land
        hard against the SEP_MIN floor, which is exactly the "as close as the spacing
        law allows" reading of the design text.

    Still no RNG and still a total order on every tie-break, so the output reproduces
    byte-for-byte on any machine and any Python build. Every candidate is rejected up
    front unless it keeps BOTH hard invariants: the SEP_MIN spacing floor and the
    SCREEN_CAP_EFF effective-density ceiling."""
    existing = s.existing_proxies()
    # checked BEFORE the (multi-minute) candidate scan so a wrong --map fails in a
    # second rather than after a full pass
    assert len(s.instances) == BASELINE_INSTANCES and len(existing) == BASELINE_PROXIES, (
        f'this map carries {len(s.instances)} instances / {len(existing)} monster '
        f'proxies in drxBC3, not the shipped {BASELINE_INSTANCES}/{BASELINE_PROXIES}. '
        f'The derivation must be run against a BASELINE map (one WITHOUT this lane\'s '
        f'placements) - deriving from the post-change map would feed this lane\'s own '
        f'14 proxies back in as pre-existing content.')
    cand = s.candidates()
    committed = list(existing)
    placed = []
    bounds = (0.0,) + BAND_BOUNDS + (float('inf'),)
    report = []
    for bi, (label, roster) in enumerate(BANDS):
        lo, hi = bounds[bi], bounds[bi + 1]
        band = {k: r for k, r in cand.items() if lo <= r < hi}
        report.append((label, lo, hi, len(band)))
        for dbr, n in roster:
            eff = s.effective(dbr)
            assert eff is not None, (
                f'{dbr}: no resolvable effective spawn count (spawnMax x '
                f'spawnMaxEquation) - refusing to place a proxy whose load is unknown')
            anchor = None                       # (x, z) of this group's first member
            for m in range(n):
                ranked = []
                for k, r in band.items():
                    x, z = s.wx(k[0]), s.wz(k[1])
                    if not sep_ok(x, z, committed):
                        continue
                    if anchor is None:
                        # ANCHOR: largest min-distance first. Ascending on the negated
                        # key == round 1's (md, -route, -gcx, -gcz) descending.
                        md = min(max(abs(x - qx), abs(z - qz))
                                 for (qx, qz, _d, _sm) in committed)
                        key = (-md, r, k[0], k[1])
                    else:
                        # MEMBER: smallest distance to this group's anchor first.
                        da = max(abs(x - anchor[0]), abs(z - anchor[1]))
                        key = (da, r, k[0], k[1])
                    ranked.append((key, k, x, z))
                ranked.sort(key=lambda t: t[0])
                bestk = None
                for _score, k, x, z in ranked:
                    if worst_screen(committed + [(x, z, dbr, eff)])[0] <= SCREEN_CAP_EFF:
                        bestk = k
                        break
                assert bestk is not None, (
                    f'no rule-satisfying cell left in band {label} for {dbr} '
                    f'(member {m + 1}/{n}) - {len(band)} band cells, {len(ranked)} '
                    f'passed the {SEP_MIN:.0f}u spacing floor, none kept the worst '
                    f'{SCREEN:.0f}x{SCREEN:.0f} box at or under {SCREEN_CAP_EFF:.1f} '
                    f'effective. Widen the band, widen the corridor, or cut the roster.')
                x, z = s.wx(bestk[0]), s.wz(bestk[1])
                y = s.wy(s.cells[bestk])
                if anchor is None:
                    anchor = (x, z)
                committed.append((x, z, dbr, eff))
                placed.append(dict(band=label, dbr=dbr, cell=bestk, world=(x, y, z),
                                   route=cand[bestk], spawnMax=s.spawn_max(dbr) or 0,
                                   mult=s.multiplier(dbr), eff=eff,
                                   role=('anchor' if m == 0 else 'member')))
                del band[bestk]
    return placed, existing, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    # ROUND-2 FIX: this default used to be REPO.parent.parent.parent/'work'/..., which
    # from a worktree resolved to the MAIN CHECKOUT's staged arz (another lane's
    # artifact, and a live footgun for the re-derive this module tells the next lane to
    # run) and from the main checkout resolved to a nonexistent C:/Users/work/...
    # It is now REPO-relative, matching tools/gate_sanctuary_population.py.
    ap.add_argument('--arz', default=str(REPO / 'work' / 'SoulvizierClassic' /
                                        'Database' / 'SoulvizierClassic.arz'))
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
              "   # route %5.1fu  world(%.1f,%.1f,%.1f) sMax=%d x%.4f = %.1f eff  [%s]"
              % (p['dbr'].split('\\')[-1], lx, ly + 0.005, lz,
                 p['route'], wxx, wyy, wzz, p['spawnMax'], p['mult'], p['eff'],
                 p['role']))

    allp = [(p['world'][0], p['world'][2], p['dbr'], p['eff']) for p in placed]
    w0, _ = worst_screen(existing)
    w1, at1 = worst_screen(existing + allp)
    area = len(s.own) * CELL_AREA
    print('\n=== density (EFFECTIVE entities = spawnMax x spawnMaxEquation @ '
          f'{NPLAYERS} player) ===')
    print(f'  proxies       : {len(existing)} existing + {len(placed)} new = '
          f'{len(existing) + len(placed)}')
    print(f'  total raw spawnMax : {sum(s.spawn_max(p[2]) or 0 for p in existing)} -> '
          f'{sum(s.spawn_max(p[2]) or 0 for p in existing) + sum(p["spawnMax"] for p in placed)}')
    print(f'  total EFFECTIVE    : {sum(p[3] for p in existing):.1f} -> '
          f'{sum(p[3] for p in existing) + sum(p["eff"] for p in placed):.1f}')
    print(f'  sq u / proxy  : {area / len(existing):.0f} -> '
          f'{area / (len(existing) + len(placed)):.0f}')
    print(f'  worst {SCREEN:.0f}x{SCREEN:.0f} screen, EFFECTIVE: {w0:.1f} -> {w1:.1f} '
          f'(cap {SCREEN_CAP_EFF:.1f})'
          + (f'  at world({at1[0]:.0f},{at1[1]:.0f})' if at1 else ''))

    # SHAPE - the number the round-1 vet caught. A congregation clusters; a patrol
    # does not. Printed every run so the claim can never drift from the code again.
    def nnd(pts):
        return sorted(min(max(abs(pts[i][0] - pts[j][0]), abs(pts[i][1] - pts[j][1]))
                          for j in range(len(pts)) if j != i)
                      for i in range(len(pts)))
    ex2 = [(p[0], p[1]) for p in existing]
    new2 = [(p['world'][0], p['world'][2]) for p in placed]
    print('\n=== shape: nearest-neighbour Chebyshev (a congregation clusters) ===')
    for nm, pts in (("amgoz1's shipped", ex2), ('this lane\'s new', new2)):
        if len(pts) < 2:
            continue
        v = nnd(pts)
        print(f'  {nm:18s} n={len(pts):2d}  min {v[0]:5.1f}  median '
              f'{v[len(v) // 2]:5.1f}  max {v[-1]:5.1f}   {[round(t, 1) for t in v]}')

    if a.json:
        Path(a.json).write_text(json.dumps(
            [dict(band=p['band'], dbr=p['dbr'], world=list(p['world']),
                  local=[p['world'][0] - cx, p['world'][1] - cy + 0.005, p['world'][2] - cz],
                  route=p['route'], spawnMax=p['spawnMax'], mult=p['mult'],
                  eff=p['eff'], role=p['role']) for p in placed], indent=1))
        print(f'\nwrote {a.json}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
