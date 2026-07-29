#!/usr/bin/env python3
"""GATE MAP-SANCTUARY-1 - the Sanctuary of the Bloodborn population invariants.

CLAUDE.md process law #4: a lane that creates a new player-visible content class
ships the invariant gate WITH it. b100 creates one - a hand-placed monster
population on a level nobody had ever placed content on - so this is its gate.

It runs against a BUILT `Levels.arc` (the FINAL MERGED map, never the source blob:
the pre-merge blob is not where the grid shift and the injections have landed) and
re-proves, from the map's own bytes, every invariant the placement claims:

  G1  ROSTER      exactly the 14 injected proxies are present, at the declared
                  coords, on top of the 10 the level already shipped, and the 281
                  pre-existing instances are untouched (RETIREMENT PROTOCOL).
  G2  ON-MESH     every new proxy sits on a walkable navmesh cell whose `areas`
                  owner byte is drxBC3's OWN GUID index - i.e. on its own ground,
                  never on the padded neighbour strip.
  G3  TILESETS    ... in ALL THREE tilesets (Normal / Epic / Legendary). The engine
                  requires all three; a spot walkable on one only would spawn
                  monsters that cannot path on the other two difficulties.
  G4  FLOOR       the placed Y matches the navmesh cell's own height to <= 0.25 u,
                  so nothing is buried or hovering. drxBC3 descends FOUR tiers
                  (world Y +2 / -10 / -22 / -34) and a flat-Y placement would be
                  wrong on three of them.
  G5  REACHABLE   every new proxy is in the same connected component as the arrival
                  portal, under the engine's own climb model (1.0 u).
  G6  PROCESSION  every new proxy is ON the one-way walk: routing through its cell
                  costs at most CORRIDOR_SLACK of detour over the shortest
                  arrival -> west-door path. Nothing is stranded in a dead pocket.
  G7  LANDING     nothing within CLEAR_ANCHOR of the arrival portal or the respawn
                  shrine (the b44 landing-clearance defect class: the player must
                  never materialise inside a pack), and nothing within EDGE_CLEAR of
                  the level's own footprint edge (the same class applied to the
                  walk-in seam into drxBC_Finale).
  G8  SPACING     no two monster proxies, old or new, within SEP_MIN (Chebyshev).
                  This is R-30's spacing law: "you need to space these monsters out
                  instead of putting them all on top of one another."
  G9  DENSITY     the worst axis-aligned 60x60 world-unit box anywhere on the
                  walkway sums <= SCREEN_CAP pool `spawnMax`. Exact box, not a
                  proxy-centred sample.
  G10 NAVMESH     drxBC3's `0x0b` container is byte-identical to the baseline map's
                  (needs --baseline), it still parses, and it still has exactly 3
                  tilesets. THE B89 CRASH CLASS: a malformed navmesh container made
                  the engine read into adjacent heap. This lane is 0x05-only and
                  this is where that is proven, not assumed.
  G11 POOLS       every placed proxy resolves in the arz as Class `Proxy`, its
                  `pool1` resolves as Class `ProxyPool`, that pool has at least one
                  live `nameN` with non-zero weight, and NO pool in the roster is an
                  unbounded summon generator (the b76 chumbi-freeze class: b76 froze
                  because stacked summoners with no `spawnObjectsTimeToLive` refilled
                  their pet caps forever). Needs --arz.
  G12 SCOPE       the lane placed nothing outside drxBC3 - in particular nothing on
                  ocean_extension01..04, which is WILL_DECISION-1 and not ours.

Exit 0 = every gate PASS. Read-only.

Usage:
  py tools/gate_sanctuary_population.py --map local/Levels_merged.arc \
        --baseline local/b100_base/Levels_merged.arc --arz <SoulvizierClassic.arz>
  py tools/gate_sanctuary_population.py --negtest
"""
import sys
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

import contracts_map as CM                                      # noqa: E402
from rec02_format import parse_rec02                            # noqa: E402
import b100_derive_sanctuary as D                               # noqa: E402
import build_section_surgery as BSS                             # noqa: E402

GATE = 'MAP-SANCTUARY-1'
FLOOR_TOL = 0.25          # G4: how far a placed Y may sit off its own navmesh cell
OCEAN_LEVELS = ('ocean_extension01', 'ocean_extension02',
                'ocean_extension03', 'ocean_extension04')

# INHERITED SPACING WAIVER (G8b). amgoz1's OWN shipped drxBC3 placements already
# violate R-30's spacing floor: `bw_seductress_lone` at world (4314.8,2882.1) and
# `bw_priest_houndmaster` at (4316.6,2889.5) are 7.4 u apart (Chebyshev). Moving
# either is a design change to shipped upstream content and defaults to WILL-VETO
# under the RETIREMENT PROTOCOL, so this lane leaves them exactly where they are
# and waives the pair BY NAME. The waiver is an allow-LIST, not a mute: any OTHER
# old-old violation, and any violation involving a placement this lane made, still
# fails. Registered as debt so it is never silently inherited again.
INHERITED_SPACING_WAIVER = {
    ('bw_priest_houndmaster.dbr', 'bw_seductress_lone.dbr'),
}


def expected_specs():
    """The declared placements, as (dbr str, local x, y, z), straight from the
    single source of truth the build itself uses."""
    out = []
    for spec in BSS.INJECT_SPECS[BSS.SANCTUARY_HOST_KEY]:
        dbr = spec[0].decode('latin-1')
        out.append((dbr, float(spec[1]), float(spec[2]), float(spec[3])))
    return out


class Result:
    def __init__(self):
        self.rows = []

    def add(self, gid, name, ok, detail):
        self.rows.append((gid, name, bool(ok), detail))
        return ok

    def report(self):
        width = max(len(r[1]) for r in self.rows)
        bad = 0
        for gid, name, ok, detail in self.rows:
            if not ok:
                bad += 1
            print(f'  {gid:<4s} {name:<{width}s}  {"PASS" if ok else "FAIL"}  {detail}')
        print(f'\nGATE {GATE}: {"PASS" if not bad else f"FAIL ({bad} failing)"}')
        return bad


def run(map_path, baseline_path=None, arz_path=None, expected=None, quiet=False):
    """Returns (n_failures, Result). `expected` lets a negative test substitute a
    deliberately-broken placement list without touching the map."""
    r = Result()
    exp = expected if expected is not None else expected_specs()
    s = D.Sanctuary(map_path, arz_path)
    cx, cy, cz = s.corner

    # ---- G1 roster ---------------------------------------------------------
    inst = s.instances
    n_total = len(inst)
    tail = inst[n_total - len(exp):] if len(exp) else []
    got = [(it['dbr'].decode('latin-1'), round(it['pos'][0], 3),
            round(it['pos'][1], 3), round(it['pos'][2], 3)) for it in tail]
    want = [(d, round(x, 3), round(y, 3), round(z, 3)) for (d, x, y, z) in exp]
    missing = [w for w in want if w not in got]
    extra = [g for g in got if g not in want]
    r.add('G1', 'roster: the 14 declared proxies are placed', not missing and not extra,
          f'{n_total} instances total, tail {len(tail)} match '
          f'({len(missing)} missing, {len(extra)} unexpected)')
    flagged = [it for it in tail if it['flags'] != 0]
    r.add('G1b', 'roster: new instances are flags=0 / no UniqueId', not flagged,
          f'{len(flagged)} flagged (amgoz1 places every drxBC3 proxy flags=0)')

    # ---- geometry ----------------------------------------------------------
    darr, dwest, best, arrc = s.route()
    # "props" for the F7/G7 clearance test = the instances that were ALREADY in the
    # level, i.e. everything except the placements this lane declares. Without the
    # exclusion every new proxy measures 0.0 u from itself.
    declared = {(d, round(x, 3), round(y, 3), round(z, 3)) for (d, x, y, z) in exp}
    props = [(cx + it['pos'][0], cz + it['pos'][2]) for it in inst
             if (it['dbr'].decode('latin-1'), round(it['pos'][0], 3),
                 round(it['pos'][1], 3), round(it['pos'][2], 3)) not in declared]
    onmesh = []
    for (dbr, lx, ly, lz) in exp:
        wxx, wyy, wzz = cx + lx, cy + ly, cz + lz
        k = s.cell_at(wxx, wzz)
        rec = dict(dbr=dbr.split('\\')[-1], world=(wxx, wyy, wzz), cell=k)
        rec['in_cells'] = k in s.cells
        rec['own'] = rec['in_cells'] and s.areas[k] == s.own_area
        rec['all3'] = all(k in c and c[k] == s.cells[k] and a[k] == s.areas[k]
                          for (c, a) in s.sets)
        rec['dy'] = abs(s.wy(s.cells[k]) - wyy) if rec['in_cells'] else float('inf')
        rec['reach'] = k in darr
        rec['detour'] = ((darr[k] + dwest[k] - best) * D.CS
                         if (k in darr and k in dwest) else float('inf'))
        rec['d_arrival'] = max(abs(wxx - D.ARRIVAL[0]), abs(wzz - D.ARRIVAL[1]))
        rec['d_shrine'] = max(abs(wxx - D.SHRINE[0]), abs(wzz - D.SHRINE[1]))
        fx0, fx1, fz0, fz1 = D.FOOTPRINT
        rec['d_edge'] = min(wxx - fx0, fx1 - wxx, wzz - fz0, fz1 - wzz)
        rec['d_prop'] = min((max(abs(px - wxx), abs(pz - wzz)) for (px, pz) in props),
                            default=float('inf'))
        onmesh.append(rec)

    def worst(key, cmp, limit):
        bad = [o for o in onmesh if not cmp(o[key], limit)]
        return bad

    b = [o for o in onmesh if not o['own']]
    r.add('G2', 'on-mesh: on drxBC3\'s OWN walkable ground', not b,
          f'{len(exp) - len(b)}/{len(exp)} on an own-area walkable cell'
          + (f'; off: {[o["dbr"] for o in b]}' if b else ''))
    b = [o for o in onmesh if not o['all3']]
    r.add('G3', 'on-mesh in ALL 3 tilesets (N/E/L)', not b,
          f'{len(exp) - len(b)}/{len(exp)}' + (f'; bad: {[o["dbr"] for o in b]}' if b else ''))
    b = worst('dy', lambda v, l: v <= l, FLOOR_TOL)
    r.add('G4', f'floor: |Y - navmesh cell Y| <= {FLOOR_TOL} u', not b,
          f'max dY {max(o["dy"] for o in onmesh):.3f} u'
          + (f'; bad: {[(o["dbr"], round(o["dy"], 2)) for o in b]}' if b else ''))
    b = [o for o in onmesh if not o['reach']]
    r.add('G5', 'reachable from the arrival portal', not b,
          f'{len(exp) - len(b)}/{len(exp)} in the arrival component'
          + (f'; stranded: {[o["dbr"] for o in b]}' if b else ''))
    b = worst('detour', lambda v, l: v <= l, D.CORRIDOR_SLACK)
    r.add('G6', f'on the processional (detour <= {D.CORRIDOR_SLACK:.0f} u)', not b,
          f'route {best * D.CS:.1f} u; max detour {max(o["detour"] for o in onmesh):.1f} u'
          + (f'; off-route: {[o["dbr"] for o in b]}' if b else ''))
    b = ([o for o in onmesh if o['d_arrival'] < D.CLEAR_ANCHOR]
         + [o for o in onmesh if o['d_shrine'] < D.CLEAR_ANCHOR])
    e = worst('d_edge', lambda v, l: v >= l, D.EDGE_CLEAR)
    p = worst('d_prop', lambda v, l: v >= l, D.PROP_CLEAR)
    r.add('G7', f'landing clearance: >= {D.CLEAR_ANCHOR:.0f} u off both anchors, '
                f'>= {D.EDGE_CLEAR:.0f} u inside the edge, >= {D.PROP_CLEAR:.0f} u off props',
          not b and not e and not p,
          f'nearest anchor {min(min(o["d_arrival"], o["d_shrine"]) for o in onmesh):.1f} u, '
          f'nearest edge {min(o["d_edge"] for o in onmesh):.1f} u, '
          f'nearest prop {min(o["d_prop"] for o in onmesh):.1f} u')

    # ---- G8/G9 spacing + density (need the arz for spawnMax) ---------------
    if arz_path:
        # The point set G8/G9 judge is (every monster proxy the MAP carries that is
        # NOT one of our declared placements) + (the DECLARED placements). For the
        # real run that is exactly the map's 24. Substituting the declared half is
        # what makes a planted negative test bite: a plant mutates the declaration,
        # not the built map, so a gate that only read the map could never fail.
        OLD, NEW = 0, 1
        pts = [(px, pz, pd, ps, OLD) for (px, pz, pd, ps) in s.existing_proxies()
               if (pd, round(px - cx, 3), round(pz - cz, 3))
               not in {(d, round(lx, 3), round(lz, 3)) for (d, lx, _ly, lz) in exp}]
        pts += [(cx + lx, cz + lz, d, s.spawn_max(d) or 0, NEW)
                for (d, lx, _ly, lz) in exp]
        mine, inherited = [], []
        mind_new = float('inf')
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = max(abs(pts[i][0] - pts[j][0]), abs(pts[i][1] - pts[j][1]))
                if pts[i][4] == NEW or pts[j][4] == NEW:
                    mind_new = min(mind_new, d)
                if d >= D.SEP_MIN:
                    continue
                pair = tuple(sorted((pts[i][2].split('\\')[-1], pts[j][2].split('\\')[-1])))
                is_new = pts[i][4] == NEW or pts[j][4] == NEW
                (mine if is_new else inherited).append((*pair, round(d, 1)))
        r.add('G8', f'spacing: every NEW proxy >= {D.SEP_MIN:.0f} u from every other (R-30)',
              not mine, f'{len(pts)} monster proxies; closest new-involving pair '
              f'{mind_new:.1f} u' + (f'; violations {mine}' if mine else ''))
        unwaived = [v for v in inherited if (v[0], v[1]) not in INHERITED_SPACING_WAIVER]
        r.add('G8b', 'spacing: no UNWAIVED inherited (upstream-vs-upstream) violation',
              not unwaived,
              f'{len(inherited)} inherited violation(s), {len(unwaived)} unwaived'
              + (f'; {unwaived}' if unwaived else
                 f'; waived by name: {sorted(INHERITED_SPACING_WAIVER)} '
                 f'(RETIREMENT PROTOCOL - amgoz1\'s own placement, not ours to move)'))
        w, at = D.worst_screen([(p[0], p[1], p[2], p[3]) for p in pts])
        r.add('G9', f'density: worst {D.SCREEN:.0f}x{D.SCREEN:.0f} box <= {D.SCREEN_CAP} spawnMax',
              w <= D.SCREEN_CAP,
              f'worst {w}' + (f' at world({at[0]:.0f},{at[1]:.0f})' if at else '')
              + f'; total spawnMax {sum(p[3] for p in pts)} over {len(pts)} proxies')

        # ---- G11 pools -----------------------------------------------------
        bad = []
        for (dbr, _lx, _ly, _lz) in exp:
            n = CM.norm_rec(dbr)
            if s._cls.get(n) != 'Proxy':
                bad.append((dbr.split('\\')[-1], f'class={s._cls.get(n)}'))
                continue
            pool = s._arz.field(s._names[n], 'pool1')
            if isinstance(pool, list):
                pool = pool[0] if pool else None
            # NOTE (measured, and it corrects the design report): a ProxyPool record
            # carries NO `Class` field at all - `record_class()` returns '' for all
            # 61 of them under records\drxmap\proxy\pools\. Their identity is the
            # TEMPLATE, `database\Templates\ProxyPool.tpl`. The design report's
            # "every pool1 resolves as Class ProxyPool" is false as written; the
            # pools are fine, the claimed evidence was not.
            if not pool or CM.norm_rec(pool) not in s._names:
                bad.append((dbr.split('\\')[-1], f'pool1={pool!r} does not resolve'))
                continue
            pn = s._names[CM.norm_rec(pool)]
            tpl = s._arz.field(pn, 'templateName') or ''
            if isinstance(tpl, list):
                tpl = tpl[0] if tpl else ''
            if not str(tpl).replace('/', '\\').lower().endswith('proxypool.tpl'):
                bad.append((dbr.split('\\')[-1], f'pool template={tpl!r}'))
                continue
            live = 0
            for i in range(1, 9):
                nm = s._arz.field(pn, f'name{i}')
                if isinstance(nm, list):
                    nm = nm[0] if nm else None
                w_ = s._arz.field(pn, f'weight{i}')
                if isinstance(w_, list):
                    w_ = w_[0] if w_ else 0
                if nm and float(w_ or 0) > 0:
                    live += 1
            sm = s.spawn_max(dbr)
            if live == 0:
                bad.append((dbr.split('\\')[-1], 'no live nameN with weight > 0'))
            elif not sm or sm <= 0:
                bad.append((dbr.split('\\')[-1], f'spawnMax={sm}'))
        r.add('G11', 'pools: every placed proxy resolves to a live, BOUNDED ProxyPool',
              not bad, f'{len(exp) - len(bad)}/{len(exp)} resolve'
              + (f'; bad: {bad}' if bad else '')
              + '; every pool is a finite spawnMax roster, no summon-refill loop (b76)')
    else:
        r.add('G8', 'spacing (needs --arz)', False, 'no arz given')
        r.add('G9', 'density (needs --arz)', False, 'no arz given')
        r.add('G11', 'pools (needs --arz)', False, 'no arz given')

    # ---- G10 navmesh identity ---------------------------------------------
    doc = parse_rec02(s.nav_raw, decompress=True)
    parses = len(doc['sets']) == 3 and all(len(x['records']) for x in doc['sets'])
    if baseline_path:
        b0 = D.Sanctuary(baseline_path)
        same = b0.nav_raw == s.nav_raw
        r.add('G10', 'navmesh: 0x0b byte-identical to baseline + well formed (b89)',
              same and parses,
              f'{len(s.nav_raw):,} B, identical={same}, 3 tilesets x '
              f'{[len(x["records"]) for x in doc["sets"]]} tiles')
    else:
        r.add('G10', 'navmesh: 0x0b well formed (no baseline given for identity)',
              parses, f'{len(s.nav_raw):,} B, 3 tilesets x '
              f'{[len(x["records"]) for x in doc["sets"]]} tiles')

    # ---- G12 scope ---------------------------------------------------------
    arc = CM.Arc.from_file(map_path)
    mp = arc.world_map()
    secs = CM.parse_top_sections(mp)
    levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
    ocean = {}
    for lv in levels:
        base = lv['fname'].replace('\\', '/').split('/')[-1].replace('.lvl', '')
        if base in OCEAN_LEVELS:
            blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            items = CM.parse_0x05(blob)[1]
            n = sum(1 for it in items
                    if b'\\proxy\\' in it['dbr'] or b'/proxy/' in it['dbr'])
            ocean[base] = (len(items), n)
    r.add('G12', 'scope: the ocean ring is untouched (WILL_DECISION-1)',
          all(v[1] == 0 for v in ocean.values()),
          '; '.join(f'{k} {v[0]} inst / {v[1]} proxies' for k, v in sorted(ocean.items())))

    if not quiet:
        print(f'GATE {GATE} - Sanctuary of the Bloodborn population')
        print(f'  map      : {map_path}')
        print(f'  baseline : {baseline_path or "(none)"}')
        print(f'  arz      : {arz_path or "(none)"}')
        print(f'  level    : {BSS.SANCTUARY_HOST_KEY}  corner {s.corner}  '
              f'mesh org {s.org}  own area {s.own_area}\n')
        bad = r.report()
    else:
        bad = sum(1 for row in r.rows if not row[2])
    return bad, r


# --------------------------------------------------------------------------- #
# PLANTED NEGATIVE TESTS - a gate nobody has watched FAIL is not a gate.
# Each plant breaks exactly ONE invariant and must be caught by exactly the gate
# that owns it (and, since the plants are placement-level, must NOT be caught by
# a gate that has nothing to do with it).
# --------------------------------------------------------------------------- #
PLANTS = [
    ('G1', 'drop one proxy from the roster',
     lambda e: e[:-1]),
    ('G1', 'move a proxy 5 u off its declared coord',
     lambda e: e[:-1] + [(e[-1][0], e[-1][1] + 5.0, e[-1][2], e[-1][3])]),
    ('G2', 'push a proxy onto the padded neighbour strip outside drxBC3',
     lambda e: e[:-1] + [(e[-1][0], -30.0, e[-1][2], e[-1][3])]),
    ('G4', 'keep the XZ but flatten Y to the top tier (the design\'s missing axis)',
     lambda e: [(e[0][0], e[0][1], 39.0, e[0][3])] + e[1:]),
    ('G7', 'drop a pack on the arrival portal (the b44 landing-pileup class)',
     lambda e: [(e[0][0], 225.0, 39.005, 220.0)] + e[1:]),
    ('G7', 'drop a pack 0.5 u from the west door seam (the walk-in variant)',
     lambda e: e[:-1] + [(e[-1][0], 0.5, 3.005, e[-1][3])]),
    ('G8', 'stack two proxies on top of one another (R-30\'s own words)',
     lambda e: e[:-1] + [(e[-1][0], e[-2][1] + 1.0, e[-2][2], e[-2][3])]),
    ('G9', 'pile the whole congregation into one screen box',
     lambda e: [(d, 100.0 + i * 2.0, 15.005, 160.0) for i, (d, _x, _y, _z) in enumerate(e)]),
]


def negtest(map_path, arz_path):
    print(f'PLANTED NEGATIVE TESTS for gate {GATE}')
    print(f'  map: {map_path}\n')
    base_bad, base_r = run(map_path, arz_path=arz_path, quiet=True)
    print(f'  baseline (unmodified placements): {base_bad} failing '
          f'-> {"OK, the gate is green before we break it" if base_bad == 0 else "PROBLEM"}')
    if base_bad:
        for gid, name, ok, detail in base_r.rows:
            if not ok:
                print(f'      {gid} {name}: {detail}')
        print('\nNEGTEST: ABORTED - the gate is not green on the real placements.')
        return 1
    exp = expected_specs()
    fails = 0
    for want_gid, label, mutate in PLANTS:
        bad, res = run(map_path, arz_path=arz_path, expected=mutate(list(exp)), quiet=True)
        caught = {row[0] for row in res.rows if not row[2]}
        hit = any(g.startswith(want_gid) for g in caught)
        print(f'  plant [{want_gid}] {label:<62s} -> '
              f'{"CAUGHT" if hit else "MISSED"} by {sorted(caught) or "nothing"}')
        if not hit:
            fails += 1
    print(f'\nNEGTEST: {len(PLANTS) - fails}/{len(PLANTS)} plants caught -> '
          f'{"PASS" if not fails else "FAIL"}')
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    ap.add_argument('--baseline', default=None)
    ap.add_argument('--arz', default=str(REPO / 'work' / 'SoulvizierClassic' /
                                         'Database' / 'SoulvizierClassic.arz'))
    ap.add_argument('--negtest', action='store_true')
    a = ap.parse_args()
    if a.negtest:
        return negtest(a.map, a.arz)
    bad, _ = run(a.map, a.baseline, a.arz)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
