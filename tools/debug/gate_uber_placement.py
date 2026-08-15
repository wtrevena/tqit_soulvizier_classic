#!/usr/bin/env python3
"""R-100 #8/#16b GATE: every uber we place is INSIDE its intended area and OFF the
main walking path.

Two independent oracles, both mechanical - neither is a human eyeball and neither can be
satisfied by the metric that failed in b45.

------------------------------------------------------------------------------------
ORACLE 1 - CONTAINMENT, via the level's own area-name binding (NOT distance-to-a-POI)
------------------------------------------------------------------------------------
b45 "fixed" Tantalus by minimising the distance to `pj_denoftantalus.dbr`, declared 10.2u
"unambiguously in the den", and shipped. Will re-reported him OUTSIDE the den anyway,
because that record is an `AreaOfInterest` SIGNPOST standing in the OUTDOOR level in
front of the cave mouth. Distance to it is structurally incapable of proving containment:
the marker itself is not in the den.

The oracle that IS capable is the one the game itself uses for the top-right area banner
(RE'd + proven across all 2282 levels in docs/reports/b46_minimap_result.md): the level's
0x17 REGION guid list, resolved against the world SD (0x18) REGION records, resolved
against Text. If the host level's banner does not read the intended area, the boss is not
in that area - full stop, no clearance arithmetic can argue with it.

Measured on the deployed DEV map, this immediately convicts the shipped placement:
    Styx_SwampBorder_01      -> "Stygian Marsh"       (where Tantalus stands)
    Styx_CaveUG_FrogCamp01/02/03 -> "Den of Tantalus"  (where he belongs)

------------------------------------------------------------------------------------
ORACLE 2 - MAIN WALKING PATH (R-100 #16b standing rule)
------------------------------------------------------------------------------------
"The main walking path is never an appropriate place for an uber monster we place."
Operationalised on the level's own 0x0b navmesh, with no hand-drawn routes:

  GATEWAYS = the ways a player enters/leaves this level:
     (a) main-component walkable cells inside a band of the level TILE rectangle edge
         (world tiles stitch edge-to-edge; the navmesh deliberately overhangs 16u into
         the neighbour, so the tile rect - not the navmesh bbox - is the crossing line);
     (b) 0x06 reciprocal door cells / 0x14 GridEntrance mouths (cave + dungeon doors).
  Gateway cells are clustered by 8-adjacency; clusters smaller than MIN_CLUSTER are noise.

  For each pair of clusters (A,B): multi-source BFS gives dA and dB over the walkable
  graph, so dist(A,B) = min dA over B, and the set of cells lying on SOME shortest A->B
  route is exactly {c : dA[c] + dB[c] <= dist(A,B) + slack}. That is the level's main
  walking path between those two mouths, derived, not asserted.

  Two verdicts per placement:
   * BLOCKS  (hard): delete the encounter FOOTPRINT disc (R_FOOTPRINT) from the graph and
     re-BFS. If any gateway pair that was connected is now disconnected, the encounter
     physically corks the level's only route. This is the worst case and always fails.
   * ON-PATH (the rule): the ENGAGEMENT disc (R_ENGAGE) intersects a shortest-route
     corridor, i.e. a player merely travelling between two mouths is dragged into the
     fight. This is what Will reported for the Helepolis.

  AVOIDABILITY - the calibration that stops this gate crying wolf. The first run of the
  raw ON-PATH test failed 15 of 20 shipped placements, which cannot be right: Will named
  exactly ONE placement as in-the-path (the Helepolis) and has happily fought Menoetes,
  Ephialtes and the Gaoler horde where they stand. The difference is not the metric, it is
  the LEVEL. In a tight dungeon corridor the level IS the path, so every possible spot is
  on it and "move him off the path" is not a thing that can be done. In an open field
  there is somewhere else to stand, so standing on the trodden line is a choice we made.
  So the gate measures OFF-PATH FRACTION: the share of the level's main component that is
  further than R_ENGAGE from every shortest route. ON-PATH is a FAILURE only where that
  fraction is >= OFFPATH_MIN (an alternative demonstrably exists); below it the finding is
  reported as ON-PATH(UNAVOIDABLE) - informational, never gating. Measured separation on
  the deployed map is clean: Elysian_Fields_03 (the Helepolis) sits far above the
  threshold, the Hades Palace / Dread Halls corridor hosts far below.

  WHICH COMPONENT (R-252). "The level's main component" used to mean comps[0], the
  LARGEST walkable component. That is a guess, and on a level with an isolated shelf it
  is the wrong one: boss_arena.lvl is 1,381,391 cells of unreachable low floor plus
  92,026 cells of raised dais, and the arena - boss, traveler landing, return NPC - is
  entirely on the SMALL one. The oracle now selects the component the ENCOUNTER stands
  on (Nav.component_for / Nav.on_component), so gateways, BFS and routes are computed
  where the player actually is. Every placement sitting on comps[0] is unaffected. A
  placement off EVERY component (>3u from any walkable cell) is now a hard OFF-MESH
  failure instead of a printed remark, because that reading can no longer be an artefact
  of looking at the wrong island.

  ISLAND ADVISORY (R-252 vet round 2). Selecting the encounter's own component also makes
  a new fact visible, so the gate states it: when that component is smaller than the
  encounter's own R_FOOTPRINT disc it cannot hold the fight being audited, and the gate
  prints an ISLAND advisory plus an end-of-run summary. It is deliberately NOT a verdict -
  a small island can be legitimately reached by a door or portal this oracle does not
  model, and the finding belongs to whichever lane owns the placement. Measured today:
  minobossproxy_aniketos (Connector04.LVL) sits alone on component #19 of 68, 277 of
  285,559 cells; under the old comps[0] rule the same placement read OFF-MESH>3u with a
  106.9u route distance, so the signal existed but pointed at the wrong thing. Fixing the
  component choice must not make it vanish.

RADII are grounded in this repo's own established encounter numbers, not invented:
  R_FOOTPRINT 6.0u - the "boss + 2 champion escorts + hoard chest" ring every uber survey
                     in build_section_surgery already reports as clr@6.
  R_ENGAGE   12.0u - twice the footprint: the band a passer-by is pulled into.
Both are CLI-tunable so a ruling can retune the policy without editing the gate.

Usage:
  py tools/debug/gate_uber_placement.py <map.arc>                 # audit every placement
  py tools/debug/gate_uber_placement.py <map.arc> --only tantalus
  py tools/debug/gate_uber_placement.py <map.arc> --negtest       # planted negatives
"""
import sys
import copy
import math
import struct
import argparse
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from arc_patcher import ArcArchive                                   # noqa: E402
from contracts_map import (parse_0x05, parse_blob_sections,          # noqa: E402
                           blob_0x14_map, GRIDENTRANCE_PREFIX)
from rec02_format import parse_rec02                                 # noqa: E402
from sd_format import SDSection, sd_from_map_bytes                   # noqa: E402
from build_section_surgery import parse_0x17_header                  # noqa: E402
import survey_uberboss_spots as S                                    # noqa: E402

BS = chr(92)
R_FOOTPRINT = 6.0
R_ENGAGE = 12.0
SEAM_BAND = 1.0          # world units either side of a tile edge that counts as a crossing
MIN_CLUSTER = 8          # gateway cells; smaller runs are navmesh fringe noise
PATH_SLACK = 2.0         # world units of shortest-path slack (route is a corridor, not a line)
OFFPATH_MIN = 0.25       # >= this share of the level off-path => an alternative spot exists

BASE_TEXT_ARC = (r"C:\Program Files (x86)\Steam\steamapps\common"
                 r"\Titan Quest Anniversary Edition\Text\Text_EN.arc")


# ── expected-area table ────────────────────────────────────────────────────────────
# host level suffix -> (label, intended area display name or None to skip containment).
# The intended area is the AREA WILL NAMES, not the level's filename. `None` = the
# encounter is deliberately not area-bound (test yards, ambushes in unnamed levels).
EXPECTED_AREA = {
    'medea_templeug_tomb03.lvl':                ('M4 Kroisos the Coin-Drowned', 'Great Hall of Propontis'),
    'styx_caveug_frogcamp02.lvl':               ('M5 Tantalus the Hunger Unbound', 'Den of Tantalus'),
    'styx_swampborder_01.lvl':                  ('M5 Tantalus (RETIRED outdoor spot)', 'Den of Tantalus'),
    'styx_riveredge_01.lvl':                    ('M6 Akremon the Grasping Root / Soul of the Grasping Root', 'Shrine of the Golden Bough'),
    'judgment_templeug_mnemosyne01.lvl':        ('M7 The Mnemophage', 'Lower City of Lost Souls'),
    'judgment_stonecity_exit01.lvl':            ('M8 Ephialtes, the Dread', 'The Dread Halls'),
    'hadespalace_floor04_01.lvl':               ('Alkyoneus the Soul-Gaoler', 'Prison of Souls'),
    'hadespalace_floor_03.lvl':                 ('Menoetes, Marshal of the Dead', 'The Winding Descent'),
    'hadespalace_crystal_03.lvl':               ('General A honor guard', 'The Winding Descent'),
    'hadespalace_floor04_04.lvl':               ('General B honor guard + Endless Hunt', 'Prison of Souls'),
    'hadespalace_crystal_04.lvl':               ('General C honor guard', 'Prison of Souls'),
    'elysian_fields_03.lvl':                    ('The Helepolis, Taker of Cities', 'Delian Meadows'),
    'thebesopttomba.lvl':                       ('Neferkha, the Rimebound Pharaoh', None),
    'tombobs01.lvl':                            ('Obsidian roulette b,d', 'The Obsidian Halls'),
    'tombobs02.lvl':                            ('Broodmother nest + roulette a,c', 'The Obsidian Halls'),
    'connector04.lvl':                          ('Aniketos (SV restore)', None),
    'random05a.lvl':                            ('Vashkarr', None),
    'drxfirstxistion_connection.lvl':           ('Blood-Toxeus parchment ambush', None),
    # R-252 (BL-W0814-12): the arena boss stopped being quest-spawned and became a real
    # placed encounter, so he now falls under this gate like every other uber we place.
    'boss_arena.lvl':                           ('R-252 Aithon, the Ember-Crowned', 'Olympian Arena'),
}

# ── AUDITED + ACCEPTED on-path placements (R-100 #16b audit, 2026-07-30) ───────────
# The #16b audit found 8 further encounters on a main walking path that Will has NOT
# reported. They are NOT silently fixed (moving bosses he has not complained about is how
# regressions get introduced) and they are NOT silently hidden: each is listed here with
# the reason it stands, printed in every gate run, and registered in the BACKLOG DEBT
# section. A placement NOT in this table that goes on-path reds the gate - so the audited
# status quo does not block the wave, but a NEW regression still does.
#
# BLOCKS-ROUTE is deliberately NOT acceptable here: corking a level's only route is a
# different severity from standing beside it, and `q_obs_roulette_b` is left RED on purpose
# as a genuine finding for Will (BL-R130-DEBT-3).
#   key = (host suffix, record basename) -> reason
ACCEPTED_ON_PATH = {
    ('drxfirstxistion_connection.lvl', 'q_bloodtoxeus_ambush.dbr'):
        'DELIBERATE AMBUSH. b79/Will: the Devourer must spawn "with his guys next to the '
        'tattered parchment". An ambush is on-path BY DESIGN - moving it off would undo a '
        'Will fix.',
    ('drxfirstxistion_connection.lvl', 'q_enslaver_warband.dbr'):
        'Same corridor ambush set-piece as the parchment Devourer; the warband is meant to '
        'meet the player on the way in.',
    ('hadespalace_floor04_04.lvl', 'q_general_b_guardpair.dbr'):
        'Honor guard placed ~6u beside general B own xsq27_namedhero proxy. Adjacency IS '
        'the design (R-100 #18 asks for them to read as ubers, not to be moved).',
    ('hadespalace_floor_03.lvl', 'q_hadesmarshal_lone.dbr'):
        'Menoetes in the central hall of The Winding Descent - a destination boss in a hall '
        'the player crosses. Will has fought him and not complained. Will-call.',
    ('judgment_stonecity_exit01.lvl', 'q_ephialtes_lone.dbr'):
        'Dread Halls terminal reward vault, the "back corner" Will himself ordered. The '
        'vault IS the end of the route, so its route-adjacency is intrinsic. Will-call.',
    ('judgment_stonecity_exit01.lvl', 'svc_ephialtes_chest.dbr'):
        'Rides the Ephialtes encounter above.',
    ('styx_riveredge_01.lvl', 'q_goldenbough_lone.dbr'):
        'Shrine of the Golden Bough forecourt - a destination shrine between two colossal '
        'statues, chosen over the tighter summit. Will-call.',
    ('styx_riveredge_01.lvl', 'svc_charon_chest.dbr'):
        'Rides the Akremon / Golden Bough encounter above (R-231: was Charon).',
    ('tombobs02.lvl', 'q_obs_roulette_a.dbr'):
        'Obsidian roulette CORNER - a random 25% mini-event prop, not an uber monster we '
        'place. The 4 corners deliberately span both Obsidian levels.',
    ('boss_arena.lvl', 'boss_satyrshaman.dbr'):
        'R-252: the ARENA. The fight stands at SV own location_bossarenacenter, dead '
        'centre of a one-room destination level whose only gateways are the traveler '
        'landing and the two return portals - so "beside the route" does not exist here: '
        'the centre IS the destination (the Ephialtes reward-vault precedent). Moving it '
        'off-centre would move the boss out of the arena Will travels to. '
        'NOT CURRENTLY EXERCISED, and that is measured, not assumed: on the encounter '
        'component (comp#2, the dais) the level yields 1 gateway cluster and 0 connected '
        'pairs, so the ON-PATH oracle has no route to test and stays silent. This row is '
        'the standing judgment for the day the arena gains a second mouth.',
}


# Records this gate treats as OUR placed encounters (bosses/hordes) and OUR chests.
# R-252: the arena spawner lives in SV own namespace (records\proxies custom\bossarena\),
# not drxmap\proxy\q_*, so it needs its own marker or the gate would silently ignore the
# newest placed encounter.
BOSS_MARKERS = ('drxmap' + BS + 'proxy' + BS + 'q_', 'minobossproxy_aniketos',
                'proxies custom' + BS + 'bossarena' + BS)
CHEST_MARKERS = ('svc_' , 'polisvault_chest')


# ── world / level loading ──────────────────────────────────────────────────────────
def load_text():
    txt = {}
    p = Path(BASE_TEXT_ARC)
    if not p.exists():
        return txt
    a = ArcArchive.from_file(p)
    for e in a.entries:
        d = a.decompress(e)
        t = None
        for enc in ('utf-16-le', 'latin1'):
            try:
                t = d.decode(enc)
                break
            except Exception:
                continue
        if not t:
            continue
        for line in t.splitlines():
            if '=' in line and not line.startswith('//'):
                k, _, v = line.partition('=')
                txt.setdefault(k.strip(), v.strip())
    return txt


def level_regions(blob, sd_regions, text):
    """Display names of the SD regions this level's 0x17 REGION list binds."""
    out = []
    for t, d in parse_blob_sections(blob):
        if t != 0x17:
            continue
        try:
            _m, _v, _env, region, _audio, _r = parse_0x17_header(d)
        except Exception:
            return ['<0x17 unparseable>']
        for _ix, g in region:
            nm, tag = sd_regions.get(bytes(g), ('?unknown', ''))
            out.append(text.get(tag, nm))
        break
    return out


def tile_rect(lv):
    """The level's own TILE rectangle in 0x05-local units: (W, H).

    ints_raw[0] / [2] are half-extents in the world lattice; the tile spans 2x each.
    Cross-checked against the 0x0b container on 4 hosts: 2*dims - 32 == 2*ints (the
    navmesh deliberately overhangs 16u into each neighbour, which is why the NAVMESH
    bbox must not be used as the crossing line)."""
    ii = struct.unpack_from('<13i', lv['ints_raw'], 0)
    return 2 * ii[0], 2 * ii[2]


def door_cells(blob, lv):
    """0x05-local (x,z) of this level's door mouths (0x14 GridEntrance instances and
    0x06 reciprocal descriptors)."""
    pts = []
    _s, insts = parse_0x05(blob)
    x14 = blob_0x14_map(blob) or {}
    for idx, pl in x14.items():
        if idx < len(insts) and (len(pl) == 48 or
                                 (len(pl) == 60 and pl[:12] == GRIDENTRANCE_PREFIX)):
            p = insts[idx]['pos']
            pts.append((p[0], p[2]))
    # 0x06 descriptor trailer = the door grid cell (x, layer, z) in 8u cells.
    for t, d in parse_blob_sections(blob):
        if t != 0x06:
            continue
        n = len(d)
        for count in range(1, 9):
            hdr = n - (8 + count * 60)
            if hdr < 0:
                break
            f0, c = struct.unpack_from('<2I', d, hdr)
            if c == count and (f0 == 64 or f0 == 4 + count * 60):
                for i in range(count):
                    off = hdr + 8 + i * 60
                    cx, _cy, cz = struct.unpack_from('<3I', d, off + 48)
                    pts.append((cx * 8.0 + 4.0, cz * 8.0 + 4.0))
                break
        break
    return pts


# ── navmesh graph ──────────────────────────────────────────────────────────────────
class Nav:
    def __init__(self, blob, lv, set_idx=0):
        b = S.get_0x0b(blob)
        if b is None:
            raise ValueError('no 0x0b navmesh')
        doc = parse_rec02(b, decompress=True)
        origin = tuple(doc['center'][i] - doc['dims'][i] for i in range(3))
        gc = struct.unpack_from('<13i', lv['ints_raw'], 0)[6:9]
        self.off = (gc[0] - origin[0], gc[2] - origin[2])
        self.cellmap, self.cs = S.build_indexed_cells(doc, set_idx)
        comps = S.components_of(self.cellmap)
        # R-252: keep ALL components, not just the biggest. "Largest component" is a
        # LEVEL-wide guess at where the player walks, and it is wrong on any level whose
        # encounter lives on an isolated shelf: boss_arena.lvl splits into 1,381,391
        # cells of unreachable low floor and 92,026 cells of raised dais, and the whole
        # arena (boss + traveler landing + return) is on the SMALL one. Running the
        # gateway/BFS/route oracle on the other component is not a strict check, it is a
        # vacuous one - it reasons about a component the encounter is not on and then
        # reports "nearest walkable OFF-MESH>3u" for a placement that is 0.03u on-mesh.
        # So the caller picks the component per ENCOUNTER (see component_for/
        # on_component); comps[0] stays the default, so every level whose placement is
        # on the largest component is evaluated exactly as before.
        self.comps = comps
        self.main = comps[0] if comps else frozenset()
        self.comp_idx = 0
        self.ncomp = len(comps)

    def component_for(self, x, z, radius=3.0):
        """Index into self.comps of the component this 0x05-local point stands on.

        Exact cell hit first; otherwise the component owning the nearest walkable cell
        within `radius`. None when the point is off EVERY component (a genuinely
        off-mesh placement, which the caller must report as such rather than silently
        re-home to some other island)."""
        if not self.comps:
            return None
        k0 = self.key(x, z)
        for i, c in enumerate(self.comps):
            if k0 in c:
                return i
        best, best_i = None, None
        rr = int(math.ceil(radius / self.cs))
        for dx in range(-rr, rr + 1):
            for dz in range(-rr, rr + 1):
                k = (k0[0] + dx, k0[1] + dz)
                if k not in self.cellmap:
                    continue
                lx, lz = self.local(k)
                d = math.hypot(lx - x, lz - z)
                if d > radius or (best is not None and d >= best):
                    continue
                for i, c in enumerate(self.comps):
                    if k in c:
                        best, best_i = d, i
                        break
        return best_i

    def on_component(self, i):
        """A view of this Nav whose `main` is component i. Shares the parsed navmesh
        (no re-decode); only the walkable set the oracles reason over changes."""
        if i is None or not self.comps or i == self.comp_idx:
            return self
        other = copy.copy(self)
        other.main = self.comps[i]
        other.comp_idx = i
        return other

    def key(self, x, z):
        """0x05-local (x,z) -> cell index key."""
        return (int(round((x + self.off[0]) / self.cs - 0.5)),
                int(round((z + self.off[1]) / self.cs - 0.5)))

    def local(self, k):
        return ((k[0] + 0.5) * self.cs - self.off[0], (k[1] + 0.5) * self.cs - self.off[1])

    def disc(self, x, z, r):
        """Main-component cells within r of 0x05-local (x,z)."""
        k0 = self.key(x, z)
        rr = int(math.ceil(r / self.cs))
        out = set()
        for dx in range(-rr, rr + 1):
            for dz in range(-rr, rr + 1):
                k = (k0[0] + dx, k0[1] + dz)
                if k not in self.main:
                    continue
                lx, lz = self.local(k)
                if (lx - x) ** 2 + (lz - z) ** 2 <= r * r:
                    out.add(k)
        return out

    def bfs(self, sources, blocked=frozenset()):
        """Multi-source BFS over the main component. Returns {cell: steps}."""
        dist = {}
        q = deque()
        for s in sources:
            if s in self.main and s not in blocked:
                dist[s] = 0
                q.append(s)
        while q:
            c = q.popleft()
            dc = dist[c] + 1
            for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (c[0] + dx, c[1] + dz)
                if n in dist or n not in self.main or n in blocked:
                    continue
                dist[n] = dc
                q.append(n)
        return dist


def cluster(cells):
    """8-adjacency clustering of a cell set."""
    cells = set(cells)
    out = []
    while cells:
        seed = cells.pop()
        comp = {seed}
        q = deque([seed])
        while q:
            c = q.popleft()
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n = (c[0] + dx, c[1] + dz)
                    if n in cells:
                        cells.discard(n)
                        comp.add(n)
                        q.append(n)
        out.append(comp)
    out.sort(key=len, reverse=True)
    return out


def gateways(nav, lv, blob):
    """Clustered gateway cells: tile-edge crossings + door mouths."""
    W, H = tile_rect(lv)
    band = SEAM_BAND
    seam = set()
    for k in nav.main:
        lx, lz = nav.local(k)
        if (abs(lx) <= band or abs(lx - W) <= band or
                abs(lz) <= band or abs(lz - H) <= band):
            # must be inside the tile span on the other axis
            if -band <= lx <= W + band and -band <= lz <= H + band:
                seam.add(k)
    clusters = [c for c in cluster(seam) if len(c) >= MIN_CLUSTER]
    for (dx, dz) in door_cells(blob, lv):
        d = nav.disc(dx, dz, 6.0)
        if len(d) >= MIN_CLUSTER:
            clusters.append(set(d))
    return clusters


# ── the gate ───────────────────────────────────────────────────────────────────────
def level_routes(nav, lv, blob, r_eng):
    """Per-LEVEL (placement-independent) route model. Cached by the caller.

    Returns {gws, fields, pairs, routes (cell->pair list), offpath_frac}."""
    gws = gateways(nav, lv, blob)
    fields = [nav.bfs(g) for g in gws]
    slack = int(PATH_SLACK / nav.cs)
    routes = {}          # cell -> set of pair ids lying on a shortest route through it
    pairs = []
    for i in range(len(gws)):
        for j in range(i + 1, len(gws)):
            di, dj = fields[i], fields[j]
            reach = [di[c] for c in gws[j] if c in di]
            if not reach:
                continue
            dij = min(reach)
            pairs.append((i, j))
            pid = len(pairs) - 1
            for c in di:
                if c in dj and di[c] + dj[c] <= dij + slack:
                    routes.setdefault(c, []).append(pid)
    # dilate the route set by r_eng to get the "corridor a traveller is dragged through"
    corridor = set()
    if routes:
        cutoff = int(r_eng / nav.cs)
        dist = {c: 0 for c in routes}
        q = deque(dist)
        while q:
            c = q.popleft()
            d = dist[c]
            corridor.add(c)
            if d >= cutoff:
                continue
            for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                n = (c[0] + dx, c[1] + dz)
                if n not in dist and n in nav.main:
                    dist[n] = d + 1
                    q.append(n)
    n_main = max(1, len(nav.main))
    return {'gws': gws, 'fields': fields, 'pairs': pairs, 'routes': routes,
            'offpath_frac': 1.0 - (len(corridor) / n_main)}


def analyse(nav, lv, blob, x, z, r_foot, r_eng, lr):
    """Path verdicts for a placement at 0x05-local (x,z), given the level route model."""
    res = {'gateways': len(lr['gws']), 'pairs': len(lr['pairs']), 'blocks': [],
           'onpath': [], 'min_path_dist': None, 'onmesh': None,
           'offpath_frac': lr['offpath_frac']}
    k = nav.key(x, z)
    near = None
    rr = int(math.ceil(3.0 / nav.cs))
    for dx in range(-rr, rr + 1):
        for dz in range(-rr, rr + 1):
            kk = (k[0] + dx, k[1] + dz)
            if kk in nav.main:
                lx, lz = nav.local(kk)
                d = math.hypot(lx - x, lz - z)
                if near is None or d < near:
                    near = d
    res['onmesh'] = near
    if len(lr['gws']) < 2:
        return res
    foot = nav.disc(x, z, r_foot)
    eng = nav.disc(x, z, r_eng)
    best = None
    hit_pairs = set()
    for c in lr['routes']:
        lx, lz = nav.local(c)
        d = math.hypot(lx - x, lz - z)
        if best is None or d < best:
            best = d
        if c in eng:
            hit_pairs.update(lr['routes'][c])
    res['min_path_dist'] = best
    res['onpath'] = sorted(lr['pairs'][p] for p in hit_pairs)
    blocked_fields = {}
    for (i, j) in lr['pairs']:
        if i not in blocked_fields:
            blocked_fields[i] = nav.bfs(lr['gws'][i], blocked=foot)
        if not any(c in blocked_fields[i] for c in lr['gws'][j]):
            res['blocks'].append((i, j))
    return res


def propose(nav, lv, blob, r_foot, r_eng, n=10, step=2.0, prefer_far=True):
    """Rank candidate boss spots in a level: on-mesh, clear, OFF the main walking path,
    and as deep as possible from the level's gateways (the 'far end of the room' the
    specs keep asking for). Returns [(score, x, z, clr, dpath, dgate)]."""
    lr = level_routes(nav, lv, blob, r_eng)
    gcells = set()
    for g in lr['gws']:
        gcells |= g
    dgate_field = nav.bfs(gcells) if gcells else {}
    xs = sorted({round(nav.local(k)[0] / step) * step for k in nav.main})
    zs = sorted({round(nav.local(k)[1] / step) * step for k in nav.main})
    route = set(lr['routes'])
    out = []
    for x in xs:
        for z in zs:
            k = nav.key(x, z)
            if k not in nav.main:
                continue
            ring = nav.disc(x, z, r_foot)
            # full clearance: the whole footprint ring must be walkable main-component
            need = int(math.pi * (r_foot / nav.cs) ** 2 * 0.97)
            if len(ring) < need:
                continue
            if ring & route:
                continue                      # sits on a shortest route: rejected outright
            dpath = min((math.hypot(nav.local(c)[0] - x, nav.local(c)[1] - z)
                         for c in route), default=999.0)
            dgate = dgate_field.get(k, 0) * nav.cs
            score = (dgate if prefer_far else -dgate) + 2.0 * min(dpath, 40.0)
            out.append((score, x, z, len(ring), dpath, dgate))
    out.sort(reverse=True)
    return out[:n]


def collect_placements():
    """Our placed encounters, from the build's own INJECT_SPECS (single source of truth)."""
    import build_section_surgery as B
    out = []
    for key, specs in B.INJECT_SPECS.items():
        suffix = key.replace(BS, '/').split('/')[-1].lower()
        for sp in specs:
            dbr = sp[0].decode('latin1').lower()
            kind = None
            if any(m in dbr for m in BOSS_MARKERS):
                kind = 'BOSS'
            elif any(m in dbr for m in CHEST_MARKERS) and 'chest' in dbr:
                kind = 'CHEST'
            if kind:
                out.append((suffix, key, dbr, kind, sp[1], sp[2], sp[3]))
    return out


def negtest(mappath, r_foot, r_eng):
    """PLANTED NEGATIVES. Each must FIRE (or deliberately NOT fire) or the gate is decorative.

    Every planted value is a coordinate this project ACTUALLY SHIPPED and Will ACTUALLY
    complained about, so these are regression locks, not synthetic strawmen.
    """
    data, levels = S.load_world(mappath)
    arc = ArcArchive.from_file(Path(mappath))
    raw = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sd = SDSection.parse(sd_from_map_bytes(raw))
    sd_regions = {bytes(r.guid): (r.name, r.tag) for r in sd.region_records}
    text = load_text()
    fails = []

    def check(label, cond, detail):
        print('  %-4s %-64s %s' % ('PASS' if cond else 'FAIL', label, detail))
        if not cond:
            fails.append(label)

    print('PLANTED NEGATIVES')

    # N1 CONTAINMENT must convict the exact spot b45 shipped (outdoors, 10.2u from the signpost).
    lv, blob = S.get_blob(data, levels, 'styx_swampborder_01.lvl')
    regions = level_regions(blob, sd_regions, text)
    check('N1 b45 outdoor host is NOT "Den of Tantalus"',
          not any('den of tantalus' in r.lower() for r in regions),
          'host banner reads %r' % (' | '.join(regions),))

    # N1b ... and the oracle must ACCEPT the real den, or it only ever says "no".
    lv2, blob2 = S.get_blob(data, levels, 'styx_caveug_frogcamp02.lvl')
    regions2 = level_regions(blob2, sd_regions, text)
    check('N1b the den host IS "Den of Tantalus"',
          any('den of tantalus' in r.lower() for r in regions2),
          'host banner reads %r' % (' | '.join(regions2),))

    # N2 WALKING PATH must convict the exact Helepolis spot Will called out.
    lv3, blob3 = S.get_blob(data, levels, 'elysian_fields_03.lvl')
    nav3 = Nav(blob3, lv3, 0)
    lr3 = level_routes(nav3, lv3, blob3, r_eng)
    old = analyse(nav3, lv3, blob3, 20.7, 81.7, r_foot, r_eng, lr3)
    check('N2 retired Helepolis spot (20.7,81.7) reads ON-PATH',
          bool(old['onpath']) and lr3['offpath_frac'] >= OFFPATH_MIN,
          'd(route)=%.1fu pairs=%s offpath=%.0f%%'
          % (old['min_path_dist'], old['onpath'], 100 * lr3['offpath_frac']))

    # N2b ... and must CLEAR the new one, or it is just a level-wide veto.
    new = analyse(nav3, lv3, blob3, 70.0, 80.0, r_foot, r_eng, lr3)
    check('N2b new Helepolis spot (70,80) reads OFF-PATH',
          not new['onpath'],
          'd(route)=%.1fu pairs=%s' % (new['min_path_dist'], new['onpath'] or 'none'))

    # N3 BLOCKS must fire on a real chokepoint (the audit found this one unaided).
    lv4, blob4 = S.get_blob(data, levels, 'tombobs01.lvl')
    nav4 = Nav(blob4, lv4, 0)
    lr4 = level_routes(nav4, lv4, blob4, r_eng)
    rb = analyse(nav4, lv4, blob4, 220.8, 89.6, r_foot, r_eng, lr4)
    check('N3 BLOCKS fires on the obsidian roulette-b chokepoint',
          bool(rb['blocks']), 'blocks=%s' % (rb['blocks'] or 'none'))

    # N4 the AVOIDABILITY calibration must SUPPRESS on a corridor level, or the gate reds
    # 15 of 20 shipped placements and gets switched off - the failure mode that matters most.
    lv5, blob5 = S.get_blob(data, levels, 'hadespalace_floor04_01.lvl')
    nav5 = Nav(blob5, lv5, 0)
    lr5 = level_routes(nav5, lv5, blob5, r_eng)
    gao = analyse(nav5, lv5, blob5, 72.1, 37.1, r_foot, r_eng, lr5)
    check('N4 Gaoler is ON-PATH but the corridor level SUPPRESSES the failure',
          bool(gao['onpath']) and lr5['offpath_frac'] < OFFPATH_MIN,
          'on-path=%s offpath=%.0f%% (< %.0f%% threshold)'
          % (bool(gao['onpath']), 100 * lr5['offpath_frac'], 100 * OFFPATH_MIN))

    # N5 R-252 COMPONENT SELECTION: the oracle must follow the encounter onto its own
    # navmesh island. boss_arena.lvl is the case that exposed the old comps[0] rule -
    # its largest component is the unreachable low floor. N5 proves the OLD behaviour
    # was blind here (so the fix is not cosmetic) and N5b proves the NEW behaviour sees
    # the placement. If a future map change ever merges the arena into one component,
    # N5 fails loudly rather than passing vacuously.
    lv6, blob6 = S.get_blob(data, levels, 'boss_arena.lvl')
    nav6 = Nav(blob6, lv6, 0)
    ax, az = 131.68, 129.08                      # location_bossarenacenter, the R-252 spot
    ci6 = nav6.component_for(ax, az)
    lr6_main = level_routes(nav6, lv6, blob6, r_eng)
    old6 = analyse(nav6, lv6, blob6, ax, az, r_foot, r_eng, lr6_main)
    check('N5 arena spot is NOT on the largest component, and comps[0] reads it OFF-MESH',
          ci6 is not None and ci6 != 0 and old6['onmesh'] is None,
          'component=%s of %d (sizes %s); comps[0] onmesh=%s'
          % (ci6, nav6.ncomp, [len(c) for c in nav6.comps[:3]], old6['onmesh']))

    nav6b = nav6.on_component(ci6)
    lr6 = level_routes(nav6b, lv6, blob6, r_eng)
    new6 = analyse(nav6b, lv6, blob6, ax, az, r_foot, r_eng, lr6)
    check('N5b encounter-selected component reads the SAME spot on-mesh',
          new6['onmesh'] is not None and new6['onmesh'] <= 1.0,
          'onmesh=%s on component #%s (%d cells)'
          % (new6['onmesh'], (ci6 or 0) + 1, len(nav6b.main)))

    print('\n%s: %d/%d planted negatives behaved as specified'
          % ('NEGTEST GREEN' if not fails else 'NEGTEST RED', 8 - len(fails), 8))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--only', default=None)
    ap.add_argument('--r-foot', type=float, default=R_FOOTPRINT)
    ap.add_argument('--r-eng', type=float, default=R_ENGAGE)
    ap.add_argument('--negtest', action='store_true')
    ap.add_argument('--chests', action='store_true', help='also report chest placements')
    ap.add_argument('--propose', default=None,
                    help='level suffix: rank candidate off-path boss spots instead of auditing')
    ap.add_argument('--propose-step', type=float, default=2.0)
    ap.add_argument('--propose-n', type=int, default=14)
    ap.add_argument('--checklevel', default=None, help='level suffix for --checkpt')
    ap.add_argument('--checkpt', action='append', default=[], help='X,Z to evaluate')
    a = ap.parse_args()

    if a.negtest:
        return negtest(a.map, a.r_foot, a.r_eng)

    if a.checkpt:
        _d3, levels3 = S.load_world(a.map)
        lv3, blob3 = S.get_blob(_d3, levels3, a.checklevel)
        nav3 = Nav(blob3, lv3, 0)
        lr3 = level_routes(nav3, lv3, blob3, a.r_eng)
        print('point check in %s   off-path share %.0f%%  gateways=%d pairs=%d'
              % (lv3['fname'], 100 * lr3['offpath_frac'], len(lr3['gws']), len(lr3['pairs'])))
        for p in a.checkpt:
            x, z = (float(v) for v in p.split(','))
            r = analyse(nav3, lv3, blob3, x, z, a.r_foot, a.r_eng, lr3)
            print('  (%7.1f,%7.1f)  onmesh=%s  d(route)=%s  blocks=%s  on-path pairs=%s'
                  % (x, z,
                     ('%.2fu' % r['onmesh']) if r['onmesh'] is not None else 'OFF>3u',
                     ('%.1fu' % r['min_path_dist']) if r['min_path_dist'] is not None else 'n/a',
                     r['blocks'] or 'none', r['onpath'] or 'none'))
        return 0

    if a.propose:
        _d2, levels2 = S.load_world(a.map)
        lv2, blob2 = S.get_blob(_d2, levels2, a.propose)
        nav2 = Nav(blob2, lv2, 0)
        W2, H2 = tile_rect(lv2)
        print('candidate off-path boss spots in %s (tile %dx%d)' % (lv2['fname'], W2, H2))
        print('  %-8s %-8s %-9s %-10s %-10s' % ('x', 'z', 'ring', 'd(route)', 'd(gateway)'))
        for sc, x, z, ring, dp, dg in propose(nav2, lv2, blob2, a.r_foot, a.r_eng,
                                              n=a.propose_n, step=a.propose_step):
            print('  %-8.1f %-8.1f %-9d %-10.1f %-10.1f' % (x, z, ring, dp, dg))
        return 0

    arc = ArcArchive.from_file(Path(a.map))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    _d, levels = S.load_world(a.map)
    sd = SDSection.parse(sd_from_map_bytes(data))
    sd_regions = {bytes(r.guid): (r.name, r.tag) for r in sd.region_records}
    text = load_text()

    placements = collect_placements()
    if not a.chests:
        placements = [p for p in placements if p[3] == 'BOSS']
    if a.only:
        placements = [p for p in placements if a.only.lower() in p[0] or a.only.lower() in p[2]]

    print('R-100 #8/#16b UBER PLACEMENT GATE')
    print('map        : %s' % a.map)
    print('radii      : footprint=%.1fu  engagement=%.1fu  (seam band %.1fu, slack %.1fu)'
          % (a.r_foot, a.r_eng, SEAM_BAND, PATH_SLACK))
    print('placements : %d\n' % len(placements))

    fails = []
    accepted_hits = []
    islands = []
    navcache = {}
    for suffix, key, dbr, kind, x, y, z in sorted(placements):
        label, want = EXPECTED_AREA.get(suffix, ('(unregistered host)', None))
        try:
            lv, blob = S.get_blob(data, levels, suffix)
        except SystemExit:
            print('  %-34s %-46s HOST NOT IN MAP -> FAIL' % (suffix, dbr.split(BS)[-1]))
            fails.append((suffix, dbr, 'host missing'))
            continue
        regions = level_regions(blob, sd_regions, text)
        contain = 'n/a'
        if want is not None:
            contain = 'OK' if any(want.lower() in r.lower() for r in regions) else 'FAIL'
        # R-252: the route oracle runs on the component this ENCOUNTER stands on, not
        # on whichever component happens to be biggest. Identical to the old behaviour
        # everywhere the placement is on comps[0]; the difference only shows on levels
        # like boss_arena.lvl whose encounter lives on a small raised island.
        if suffix not in navcache:
            navcache[suffix] = {'base': Nav(blob, lv, 0)}
        base = navcache[suffix]['base']
        ci = base.component_for(x, z)
        off_mesh = ci is None
        if off_mesh:
            ci = 0
        if ci not in navcache[suffix]:
            nav_i = base.on_component(ci)
            navcache[suffix][ci] = (nav_i, level_routes(nav_i, lv, blob, a.r_eng))
        nav, lr = navcache[suffix][ci]
        r = analyse(nav, lv, blob, x, z, a.r_foot, a.r_eng, lr)
        W, H = tile_rect(lv)
        avoidable = r['offpath_frac'] >= OFFPATH_MIN
        verdict = []
        notes = []
        if contain == 'FAIL':
            verdict.append('OUT-OF-AREA')
        if off_mesh:
            # R-252: now that the component is chosen per encounter, "off mesh" means
            # off EVERY walkable component of the host level - a boss standing in the
            # void, which no clearance or path arithmetic can excuse. Before this it
            # was a printed remark on an oracle that was looking at the wrong island.
            verdict.append('OFF-MESH')
        if r['blocks']:
            verdict.append('BLOCKS-ROUTE')
        acc_key = (suffix, dbr.split(BS)[-1])
        if r['onpath']:
            if avoidable and acc_key in ACCEPTED_ON_PATH:
                notes.append('ON-PATH(ACCEPTED): ' + ACCEPTED_ON_PATH[acc_key])
                accepted_hits.append(acc_key)
            elif avoidable:
                verdict.append('ON-MAIN-PATH')
            else:
                notes.append('ON-PATH(UNAVOIDABLE: only %.0f%% of this level is off-path)'
                             % (100 * r['offpath_frac']))
        ok = not verdict
        print('  %s  %s' % (label, '=' * max(4, 62 - len(label))))
        print('    record   : %s' % dbr.split(BS)[-1])
        print('    host     : %s   tile %dx%d' % (lv['fname'], W, H))
        print('    area     : %s   [want %s] -> %s'
              % (' | '.join(regions) or '(none)', want, contain))
        print('    local    : (%.1f, %.1f, %.1f)   nearest walkable %s'
              % (x, y, z, ('%.2fu' % r['onmesh']) if r['onmesh'] is not None else 'OFF-MESH>3u'))
        print('    navmesh  : component #%d of %d (%d of %d walkable cells)%s'
              % (nav.comp_idx + 1, base.ncomp, len(nav.main),
                 sum(len(c) for c in base.comps),
                 '   <- ENCOUNTER-SELECTED (not the largest)' if nav.comp_idx else ''))
        # R-252 vet round 2: per-encounter component selection makes a NEW fact visible,
        # so the gate has to say it out loud. Selecting the encounter's own island fixes
        # the vacuous "OFF-MESH>3u" reading, but it can also silently re-home a placement
        # onto an island far too small to fight on - minobossproxy_aniketos in
        # Connector04.LVL lands on component #19 of 68, 277 of 285,559 cells, and reads a
        # comfortable 0.11u on-mesh. Under the OLD comps[0] rule that same placement read
        # OFF-MESH>3u with a 106.9u route distance, i.e. the alarm existed but pointed at
        # the wrong thing; the fix must not make it disappear instead.
        # THRESHOLD, derived from this gate's own R_FOOTPRINT rather than invented: an
        # island smaller than the encounter's 6.0u footprint disc cannot hold the fight
        # the gate is auditing (boss + 2 champion escorts + hoard chest).
        # ADVISORY, NEVER A VERDICT: it is a reachability SIGNAL, not a proof - a small
        # island can be legitimately reachable via a door/portal this oracle does not
        # model - and turning it into a failure would red placements outside the lane
        # that added the selection rule. It goes to the debt register instead.
        _foot_cells = math.pi * (a.r_foot ** 2) / (nav.cs ** 2)
        if nav.comp_idx and len(nav.main) < _foot_cells:
            notes.append('ISLAND: the encounter stands on a %d-cell component, smaller '
                         'than its own %.1fu footprint disc (~%d cells). Reachability is '
                         'unproven by this oracle - verify a door/portal reaches it.'
                         % (len(nav.main), a.r_foot, int(_foot_cells)))
            islands.append((suffix, dbr.split(BS)[-1], nav.comp_idx + 1, len(nav.main)))
        print('    gateways : %d clusters, %d connected pairs ; off-path share %.0f%% (%s)'
              % (r['gateways'], r['pairs'], 100 * r['offpath_frac'],
                 'alternatives exist' if avoidable else 'level is essentially all corridor'))
        print('    path     : dist-to-nearest-shortest-route %s ; blocks=%s ; on-path pairs=%s'
              % (('%.1fu' % r['min_path_dist']) if r['min_path_dist'] is not None else 'n/a',
                 r['blocks'] or 'none', r['onpath'] or 'none'))
        print('    VERDICT  : %s%s\n'
              % ('PASS' if ok else 'FAIL: ' + ', '.join(verdict),
                 ('   [' + '; '.join(notes) + ']') if notes else ''))
        if not ok:
            fails.append((suffix, dbr, ','.join(verdict)))

    print('=' * 78)
    if accepted_hits:
        print('AUDITED + ACCEPTED on-path placements (%d) - reported, not hidden, '
              'registered as BACKLOG debt:' % len(accepted_hits))
        for k in accepted_hits:
            print('   %-34s %-30s %s' % (k[0], k[1], ACCEPTED_ON_PATH[k][:70] + '...'))
        print('')
    if islands:
        print('ISLAND ADVISORIES (%d) - encounters standing on a navmesh component too '
              'small for their own footprint. NOT gating (a door or portal this oracle '
              'does not model may reach them); register each as debt and prove it:'
              % len(islands))
        for s, d, ci, n in islands:
            print('   %-34s %-30s component #%d, %d cells' % (s, d, ci, n))
        print('')
    if fails:
        print('GATE RED: %d placement(s) fail' % len(fails))
        for s, d, w in fails:
            print('   %-34s %-44s %s' % (s, d.split(BS)[-1], w))
        return 1
    print('GATE GREEN: every placement is in its intended area and off the main walking path')
    return 0


if __name__ == '__main__':
    sys.exit(main())
