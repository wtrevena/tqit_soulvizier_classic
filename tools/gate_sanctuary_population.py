#!/usr/bin/env python3
"""GATE MAP-SANCTUARY-1 - the Sanctuary of the Bloodborn population invariants.

CLAUDE.md process law #4: a lane that creates a new player-visible content class
ships the invariant gate WITH it. b100 creates one - a hand-placed monster
population on a level nobody had ever placed content on - so this is its gate.

It runs against a BUILT `Levels.arc` (the FINAL MERGED map, never the source blob:
the pre-merge blob is not where the grid shift and the injections have landed) and
re-proves, from the map's own bytes, every invariant the placement claims:

  G1  ROSTER      exactly the 14 injected proxies are present, at the declared
                  coords, as the tail of the level's instance list.
  G1c RETIREMENT  ⚠️ THE INVARIANT MOST CENTRAL TO THIS LANE, and the one round 1
                  claimed but did NOT check. add-only means: the level carries
                  EXACTLY 281 + 14 instances, and every one of amgoz1's 11 shipped
                  Proxy placements is still present at its exact shipped local
                  coordinate. Needs no baseline map. Round 1 compared only the TAIL
                  14 as a set, so deleting a shipped instance, deleting one of
                  amgoz1's ten shipped MONSTER proxies (which also silently lowered
                  the G8/G9 numbers and still reported PASS), deleting-and-padding to
                  keep the total at 295, or teleporting a shipped proxy 500 u off the
                  level ALL passed every gate.
  G1d RETIREMENT  ... and, with --baseline, the 281 shipped instances are BYTE-FOR-BYTE
                  identical to the baseline map's, rotation bytes included.
  G2  ON-MESH     every new proxy sits on a walkable navmesh cell whose `areas`
                  owner byte is drxBC3's OWN GUID index - i.e. on its own ground,
                  never on the padded neighbour strip.
  G3  TILESETS    the three tilesets (Normal / Epic / Legendary) agree cell-for-cell
                  AND every new proxy is walkable in all three. The engine requires
                  all three; a spot walkable on one only would spawn monsters that
                  cannot path on the other two difficulties. Round 1 ASSERTED the
                  tilesets were identical inside Sanctuary.__init__, which made this
                  row a tautology of the G2 test and turned a genuine divergence into
                  a constructor crash rather than a G3 FAIL.
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
                  This implements R-30's spacing law ("you need to space these
                  monsters out instead of putting them all on top of one another");
                  the 16 u figure is the design pass's, not Will's - R-30 fixes no
                  distance.
  G9  DENSITY     the worst axis-aligned 60x60 world-unit box anywhere on the walkway
                  sums <= SCREEN_CAP_EFF **EFFECTIVE ENTITIES**. Exact box, not a
                  proxy-centred sample. ⚠️ Round 1 gated RAW pool `spawnMax`, which is
                  NOT what the engine spawns: the pool's `proxyPoolEquation` multiplies
                  it (measured: `proxypoolequation_01` 3.60025x at 1 player, `_02`
                  1.357143x). Every blood-cave pool uses `_02` and 854/887 of the
                  base-game cave/crypt/tomb cohort's references use `_01`, so round 1's
                  cross-family comparison was invalid. Within drxBC3 the two units are
                  exactly proportional, so the correction moves no placement.
  G10 NAVMESH     drxBC3's `0x0b` container is byte-identical to the baseline map's
                  (needs --baseline), it still parses, and it still has exactly 3
                  tilesets. THE B89 CRASH CLASS: a malformed navmesh container made
                  the engine read into adjacent heap. This lane is 0x05-only and
                  this is where that is proven, not assumed. Reports FAIL on a
                  corrupt container instead of raising out of the constructor.
  G11 POOLS       every placed proxy resolves in the arz as Class `Proxy`, its `pool1`
                  resolves to a record on template `ProxyPool.tpl`, that pool has at
                  least one live `nameN` with non-zero weight (ALL slots, not just
                  1..8 - `zparty_witchfest_2099` carries a `name9`), and NO pool in
                  the roster is an unbounded summon generator (the b76 chumbi-freeze
                  class: b76 froze because stacked summoners with no
                  `spawnObjectsTimeToLive` refilled their pet caps forever). Needs
                  --arz.
  G12 SCOPE       the lane placed nothing outside drxBC3 - in particular nothing on
                  ocean_extension01..04, which is WILL_DECISION-1 and not ours.

Exit 0 = every gate PASS. Read-only.

Usage:
  py tools/gate_sanctuary_population.py --map local/Levels_merged.arc \
        --baseline local/b100_base/Levels_merged.arc --arz <SoulvizierClassic.arz>
  py tools/gate_sanctuary_population.py --negtest
"""
import sys
import struct
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))

import contracts_map as CM                                      # noqa: E402
from rec02_format import parse_rec02, serialize_rec02           # noqa: E402
import b100_derive_sanctuary as D                               # noqa: E402
import build_section_surgery as BSS                             # noqa: E402
from build_section_surgery import IDENTITY_ROT as _IDROT        # noqa: E402

IDENTITY_ROT = struct.pack('<9f', *_IDROT)

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


def run(map_path, baseline_path=None, arz_path=None, expected=None, quiet=False,
        blob_patch=None):
    """Returns (n_failures, Result).

    `expected`   - substitute a deliberately-broken DECLARATION (map untouched).
    `blob_patch` - callable(bytes)->bytes applied to drxBC3's raw level blob before
                   anything is parsed: a MAP-SIDE plant. Both kinds exist because the
                   gate has two kinds of invariant, and round 1 only ever exercised
                   the first."""
    r = Result()
    exp = expected if expected is not None else expected_specs()
    # strict=False: a corrupt navmesh must produce a G10 FAIL, not a traceback.
    s = D.Sanctuary(map_path, arz_path, strict=False, blob_patch=blob_patch)
    cx, cy, cz = s.corner
    mesh_ok = s.nav_error is None

    # ---- G1 roster ---------------------------------------------------------
    inst = s.instances
    n_total = len(inst)
    tail = inst[n_total - len(exp):] if len(exp) else []
    got = [(it['dbr'].decode('latin-1'), round(it['pos'][0], 3),
            round(it['pos'][1], 3), round(it['pos'][2], 3)) for it in tail]
    want = [(d, round(x, 3), round(y, 3), round(z, 3)) for (d, x, y, z) in exp]
    missing = [w for w in want if w not in got]
    extra = [g for g in got if g not in want]
    r.add('G1', 'roster: the 14 declared proxies are placed',
          not missing and not extra and s.inst_error is None,
          f'{n_total} instances total, tail {len(tail)} match '
          f'({len(missing)} missing, {len(extra)} unexpected)'
          + (f'; 0x05 PARSE ERROR {s.inst_error}' if s.inst_error else ''))
    flagged = [it for it in tail if it['flags'] != 0]
    rotated = [it for it in s.raw_instances[n_total - len(exp):] if it['rot'] != IDENTITY_ROT]
    r.add('G1b', 'roster: new instances are flags=0 / identity rotation',
          not flagged and not rotated,
          f'{len(flagged)} flagged, {len(rotated)} rotated (measured: ALL 25 Proxy '
          f'instances amgoz1 placed in drxBC3 are identity/flags=0, though 228 of its '
          f'269 non-proxy instances are rotated - identity is this level\'s own convention)')

    # ---- G1c/G1d RETIREMENT PROTOCOL: add-only, nothing of amgoz1's moved ---
    # This is the row round 1 was missing. It is deliberately independent of the tail
    # comparison above: a plant that deletes a shipped instance and pads the count so
    # the total and the tail both still look right must still fail here.
    n_expect = D.BASELINE_INSTANCES + len(exp)
    problems = []
    if n_total != n_expect:
        problems.append(f'instance count {n_total} != {D.BASELINE_INSTANCES} shipped '
                        f'+ {len(exp)} declared = {n_expect}')
    head = s.raw_instances[:D.BASELINE_INSTANCES]
    head_set = {}
    for it in head:
        k = (it['dbr'].decode('latin-1').split('\\')[-1].lower(),
             round(it['pos'][0], 3), round(it['pos'][1], 3), round(it['pos'][2], 3))
        head_set[k] = head_set.get(k, 0) + 1
    for (dbr, x, y, z) in D.SHIPPED_PROXIES:
        k = (dbr.lower(), round(x, 3), round(y, 3), round(z, 3))
        if head_set.get(k, 0) < 1:
            problems.append(f'SHIPPED proxy {dbr} @ local({x},{y},{z}) is GONE or MOVED')
        else:
            head_set[k] -= 1
    r.add('G1c', 'RETIREMENT PROTOCOL: add-only - 281 shipped instances still there, '
                 'all 11 shipped Proxy placements at their shipped coords',
          not problems,
          f'{n_total} instances (= {D.BASELINE_INSTANCES} + {len(exp)}), '
          f'{len(D.SHIPPED_PROXIES)}/{len(D.SHIPPED_PROXIES)} shipped proxies in place'
          if not problems else '; '.join(problems[:4]))
    if baseline_path:
        b0 = D.Sanctuary(baseline_path, strict=False)
        bh = b0.raw_instances
        diff = [i for i, (a_, b_) in enumerate(zip(s.raw_instances[:len(bh)], bh))
                if D.inst_key(a_) != D.inst_key(b_)]
        r.add('G1d', 'RETIREMENT PROTOCOL: shipped instances BYTE-identical to baseline',
              not diff and len(bh) == D.BASELINE_INSTANCES,
              f'{len(bh)} baseline instances, {len(diff)} differ'
              + (f' at indices {diff[:6]}' if diff else
                 ' (dbr + 36 rotation bytes + 12 position bytes + flags + uid all equal)'))
    else:
        r.add('G1d', 'RETIREMENT PROTOCOL byte-identity (needs --baseline)', False,
              'no baseline given')

    # ---- geometry ----------------------------------------------------------
    if not mesh_ok:
        # Every mesh-derived row is unevaluable; say so once per row rather than
        # pretending, and let G10 carry the actual diagnosis.
        for gid, nm in (('G2', 'on-mesh'), ('G3', 'tilesets'), ('G4', 'floor Y'),
                        ('G5', 'reachable'), ('G6', 'on the processional'),
                        ('G7', 'landing clearance')):
            r.add(gid, f'{nm}: NOT EVALUABLE - navmesh unusable', False,
                  f'see G10: {s.nav_error}')
        if arz_path:
            _density_and_pools(r, s, exp, cx, cz)
        else:
            for gid in ('G8', 'G8b', 'G9', 'G11'):
                r.add(gid, f'{gid} (needs --arz)', False, 'no arz given')
        _navmesh_row(r, s, baseline_path)
        _scope_row(r, map_path)
        return _finish(r, s, map_path, baseline_path, arz_path, quiet)
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
    # G3 is now TWO independent things: (a) do the three tilesets actually agree
    # (recorded by Sanctuary, no longer asserted inside it), and (b) is every new
    # placement walkable in each of them. Round 1 only had (b), and (a) being an
    # assertion made (b) a tautology of G2.
    b = [o for o in onmesh if not o['all3']]
    r.add('G3', 'tilesets: all 3 agree cell-for-cell AND every proxy walkable in each',
          not b and not s.tileset_diffs,
          f'{len(exp) - len(b)}/{len(exp)} walkable in all 3; tilesets differing from '
          f'tileset 1: {s.tileset_diffs or "none"}'
          + (f'; bad: {[o["dbr"] for o in b]}' if b else ''))
    b = worst('dy', lambda v, l: v <= l, FLOOR_TOL)
    r.add('G4', f'floor: |Y - navmesh cell Y| <= {FLOOR_TOL} u', not b,
          f'max dY {max(o["dy"] for o in onmesh):.3f} u'
          + (f'; bad: {[(o["dbr"], round(o["dy"], 2)) for o in b]}' if b else ''))
    b = [o for o in onmesh if not o['reach']]
    r.add('G5', 'reachable from the arrival portal', not b,
          f'{len(exp) - len(b)}/{len(exp)} in the arrival component'
          + (f'; stranded: {[o["dbr"] for o in b]}' if b else ''))
    b = worst('detour', lambda v, l: v <= l, D.CORRIDOR_SLACK)
    mx = max(o['detour'] for o in onmesh)
    r.add('G6', f'on the processional (detour <= {D.CORRIDOR_SLACK:.0f} u)', not b,
          f'route {best * D.CS:.1f} u; max detour {mx:.1f} u, '
          f'MARGIN {D.CORRIDOR_SLACK - mx:.1f} u'
          + (f'; off-route: {[o["dbr"] for o in b]}' if b else ''))
    b = ([o for o in onmesh if o['d_arrival'] < D.CLEAR_ANCHOR]
         + [o for o in onmesh if o['d_shrine'] < D.CLEAR_ANCHOR])
    e = worst('d_edge', lambda v, l: v >= l, D.EDGE_CLEAR)
    p = worst('d_prop', lambda v, l: v >= l, D.PROP_CLEAR)
    na = min(min(o['d_arrival'], o['d_shrine']) for o in onmesh)
    ne = min(o['d_edge'] for o in onmesh)
    np_ = min(o['d_prop'] for o in onmesh)
    r.add('G7', f'landing clearance: >= {D.CLEAR_ANCHOR:.0f} u off both anchors, '
                f'>= {D.EDGE_CLEAR:.0f} u inside the edge, >= {D.PROP_CLEAR:.0f} u off props',
          not b and not e and not p,
          f'nearest anchor {na:.1f} u (margin {na - D.CLEAR_ANCHOR:+.1f}), '
          f'nearest edge {ne:.1f} u (margin {ne - D.EDGE_CLEAR:+.1f}), '
          f'nearest prop {np_:.1f} u (margin {np_ - D.PROP_CLEAR:+.1f})')

    # ---- G8/G9 spacing + density (need the arz) ----------------------------
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
        # WEIGHT IS EFFECTIVE ENTITIES, not raw spawnMax - see the G9 docstring.
        pts += [(cx + lx, cz + lz, d, s.effective(d) or 0.0, NEW)
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
        r.add('G8', f'spacing: every NEW proxy >= {D.SEP_MIN:.0f} u from every other '
                    f'(R-30\'s law; the 16 u is the design pass\'s number, not Will\'s)',
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
        r.add('G9', f'density: worst {D.SCREEN:.0f}x{D.SCREEN:.0f} box <= '
                    f'{D.SCREEN_CAP_EFF:.1f} EFFECTIVE entities',
              w <= D.SCREEN_CAP_EFF,
              f'worst {w:.1f} (margin {D.SCREEN_CAP_EFF - w:+.1f})'
              + (f' at world({at[0]:.0f},{at[1]:.0f})' if at else '')
              + f'; total effective {sum(p[3] for p in pts):.1f} over {len(pts)} proxies'
              + f'; cap = the sparsest already-shipping blood-cave level with real '
                f'content (yet_another_fucking_connector 57.0), vs base-game '
                f'cave/crypt/tomb median 90.0 / p90 158.4')

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
            # ALL name slots, not name1..name8. ROUND-2 FIX: round 1 stopped at 8, and
            # `zparty_witchfest_2099`'s pool carries a `name9` (c_bloodhound_44). It was
            # harmless here (the pool has other live slots and this row only needs one)
            # but it is a silent undercount for any pool with 9+ slots, so the slot set
            # is now discovered from the record's own fields.
            pf = s._arz.get_fields(pn) or {}
            slots = sorted(int(k[4:]) for k in pf
                           if k.startswith('name') and k[4:].isdigit())
            live = 0
            for i in slots:
                nm = s._arz.field(pn, f'name{i}')
                if isinstance(nm, list):
                    nm = nm[0] if nm else None
                w_ = s._arz.field(pn, f'weight{i}')
                if isinstance(w_, list):
                    w_ = w_[0] if w_ else 0
                if nm and float(w_ or 0) > 0:
                    live += 1
            sm = s.spawn_max(dbr)
            mult = s.multiplier(dbr)
            if live == 0:
                bad.append((dbr.split('\\')[-1], 'no live nameN with weight > 0'))
            elif not sm or sm <= 0:
                bad.append((dbr.split('\\')[-1], f'spawnMax={sm}'))
            elif mult is None:
                # An unparsed spawnMaxEquation means the load this proxy adds is
                # UNKNOWN, which is exactly the thing the density cap exists to bound.
                bad.append((dbr.split('\\')[-1],
                            'spawnMaxEquation did not parse - effective load unknown'))
        r.add('G11', 'pools: every placed proxy resolves to a live, BOUNDED ProxyPool '
                     'with a parseable spawn multiplier',
              not bad, f'{len(exp) - len(bad)}/{len(exp)} resolve'
              + (f'; bad: {bad}' if bad else '')
              + '; every pool is a finite spawnMax roster, no summon-refill loop (b76)')
    else:
        for gid, nm in (('G8', 'spacing'), ('G8b', 'inherited spacing'),
                        ('G9', 'density'), ('G11', 'pools')):
            r.add(gid, f'{nm} (needs --arz)', False, 'no arz given')

    _navmesh_row(r, s, baseline_path)
    _scope_row(r, map_path)
    return _finish(r, s, map_path, baseline_path, arz_path, quiet)


def _density_and_pools(r, s, exp, cx, cz):
    """Placeholder used only on the navmesh-unusable path: the spacing/density/pool
    rows do not need the mesh, but they DO need the same point set, so rather than
    duplicate that logic we simply mark them unevaluated. Keeping them explicit means
    a corrupt-navmesh run still prints all 13 rows."""
    for gid, nm in (('G8', 'spacing'), ('G8b', 'inherited spacing'),
                    ('G9', 'density'), ('G11', 'pools')):
        r.add(gid, f'{nm}: NOT EVALUATED on the navmesh-failure path', False,
              'rerun once the 0x0b container is valid')


def _navmesh_row(r, s, baseline_path):
    """G10 - the b89 crash class. Must FAIL, not raise, on a corrupt container."""
    if s.nav_error is not None:
        r.add('G10', 'navmesh: 0x0b well formed (b89 CRASH CLASS)', False,
              f'{len(s.nav_raw):,} B - UNUSABLE: {s.nav_error}')
        return
    try:
        doc = parse_rec02(s.nav_raw, decompress=True)
        parses = len(doc['sets']) == 3 and all(len(x['records']) for x in doc['sets'])
        tiles = [len(x['records']) for x in doc['sets']]
    except Exception as exc:                          # noqa: BLE001 - reported
        r.add('G10', 'navmesh: 0x0b well formed (b89 CRASH CLASS)', False,
              f'{len(s.nav_raw):,} B - parse raised {type(exc).__name__}: {exc}')
        return
    if baseline_path:
        b0 = D.Sanctuary(baseline_path, strict=False)
        same = b0.nav_raw == s.nav_raw
        r.add('G10', 'navmesh: 0x0b byte-identical to baseline + well formed (b89)',
              same and parses,
              f'{len(s.nav_raw):,} B, identical={same}, 3 tilesets x {tiles} tiles')
    else:
        r.add('G10', 'navmesh: 0x0b well formed (no baseline given for identity)',
              parses, f'{len(s.nav_raw):,} B, 3 tilesets x {tiles} tiles')


def _scope_row(r, map_path):
    """G12 - the lane placed nothing outside drxBC3, in particular nothing on the
    ocean ring, which is WILL_DECISION-1 and not this lane's to take."""
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


def _finish(r, s, map_path, baseline_path, arz_path, quiet):
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
#
# ROUND-2 REWRITE. Round 1 had 8 plants and ALL EIGHT mutated only the DECLARATION
# while leaving the built map correct. Consequences the round-1 vet demonstrated:
#   * the RETIREMENT PROTOCOL - the invariant most central to this lane - was never
#     exercised, and four map-side negatives (delete a shipped instance; delete one
#     of amgoz1's ten shipped monster proxies; delete-and-pad so the count still
#     reads 295; teleport a shipped proxy 500 u off the level) were ALL MISSED with
#     every gate green;
#   * two b89-class navmesh negatives aborted the gate with an uncaught
#     AssertionError instead of failing G10;
#   * because every declaration plant also perturbs the roster, every plant also
#     tripped G1, so "one plant per invariant" was not true and no plant isolated
#     its target.
#
# There are now TWO plant kinds, and each plant declares BOTH the gate it must trip
# and the full set of gates it is ALLOWED to trip. The runner checks both directions:
# the target must fail, and nothing outside the allow-set may fail. That is the
# converse round 1 never checked.
#   DECL plants mutate the declared placement list (the map stays correct).
#   MAP  plants rewrite drxBC3's raw level blob (the declaration stays correct) -
#        real byte surgery on the level, which is what the vet did by hand.
# --------------------------------------------------------------------------- #

def _split_0x05(blob):
    """(magic, sections, section_index, strings, raw_records) for byte surgery."""
    magic = blob[:4]
    secs = [dict(type=t, data=d) for t, d in BSS.parse_blob_sections(blob)]
    si = next(i for i, s in enumerate(secs) if s['type'] == 0x05)
    d = secs[si]['data']
    base = CM.blob_0x05_base(blob)
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
    recs = []
    for _ in range(ic):
        flags = struct.unpack_from('<I', d, pos + 52)[0]
        n = base + (16 if flags != 0 else 0)
        recs.append(bytearray(d[pos:pos + n]))
        pos += n
    return magic, secs, si, strings, recs


def _emit_0x05(magic, secs, si, strings, recs):
    out = bytearray(struct.pack('<I', len(strings)))
    for s in strings:
        out += struct.pack('<I', len(s)) + s
    out += struct.pack('<I', len(recs))
    for rc in recs:
        out += rc
    secs[si]['data'] = bytes(out)
    return BSS.rebuild_blob(magic, secs)


def map_del_instance(idx):
    """Delete shipped instance #idx outright."""
    def patch(blob):
        magic, secs, si, strings, recs = _split_0x05(blob)
        del recs[idx]
        return _emit_0x05(magic, secs, si, strings, recs)
    return patch


def map_del_and_pad(idx, src):
    """Delete shipped instance #idx and duplicate #src, so the COUNT is unchanged and
    the tail still matches. This is the plant that proves G1c is not a count check."""
    def patch(blob):
        magic, secs, si, strings, recs = _split_0x05(blob)
        dup = bytearray(recs[src])
        del recs[idx]
        recs.insert(idx, dup)
        return _emit_0x05(magic, secs, si, strings, recs)
    return patch


def map_move_instance(idx, dx, dy, dz):
    """Teleport shipped instance #idx. Rewrites only its 12 position bytes, so the
    section length is unchanged - the subtlest of the four."""
    def patch(blob):
        magic, secs, si, strings, recs = _split_0x05(blob)
        x, y, z = struct.unpack_from('<3f', bytes(recs[idx]), 40)
        struct.pack_into('<3f', recs[idx], 40, x + dx, y + dy, z + dz)
        return _emit_0x05(magic, secs, si, strings, recs)
    return patch


def map_rotate_instance(idx):
    """Give a NEW instance a non-identity rotation (G1b's own subject)."""
    def patch(blob):
        magic, secs, si, strings, recs = _split_0x05(blob)
        struct.pack_into('<9f', recs[idx], 4, 0, 0, 1, 0, 1, 0, -1, 0, 0)
        return _emit_0x05(magic, secs, si, strings, recs)
    return patch


def map_navmesh(mode):
    """b89 CRASH CLASS: corrupt drxBC3's 0x0b container. `flip` changes one payload
    byte; `truncate` cuts it to a 148-byte stub, which is the exact shape of the b89
    navmesh that made the engine read into adjacent heap."""
    def patch(blob):
        magic = blob[:4]
        secs = [dict(type=t, data=d) for t, d in BSS.parse_blob_sections(blob)]
        si = next(i for i, s in enumerate(secs) if s['type'] == 0x0b)
        d = bytearray(secs[si]['data'])
        if mode == 'flip':
            d[len(d) // 2] ^= 0xFF
        elif mode == 'truncate':
            d = d[:148]
        secs[si]['data'] = bytes(d)
        return BSS.rebuild_blob(magic, secs)
    return patch


def map_tileset_divergence():
    """Make tileset 3 disagree with tileset 1 - G3's own subject. Implemented by
    zeroing one tile record's area bytes in the third tileset only."""
    def patch(blob):
        magic = blob[:4]
        secs = [dict(type=t, data=d) for t, d in BSS.parse_blob_sections(blob)]
        si = next(i for i, s in enumerate(secs) if s['type'] == 0x0b)
        raw = secs[si]['data']
        doc = parse_rec02(raw, decompress=True)
        doc['sets'][2]['records'][0]['areas'] = \
            bytearray(len(doc['sets'][2]['records'][0]['areas']))
        secs[si]['data'] = serialize_rec02(doc)
        return BSS.rebuild_blob(magic, secs)
    return patch


# (kind, target gate id prefix, allowed-to-fail gate ids, label, mutator)
DECL, MAP = 'DECL', 'MAP'
_G1FAMILY = ('G1', 'G1b', 'G1c', 'G1d')
PLANTS = [
    # ---- DECLARATION plants. Every one of these necessarily perturbs the roster, so
    # the G1 family is in every allow-set; that is disclosed, not hidden.
    (DECL, 'G1', _G1FAMILY + ('G8', 'G9'), 'drop one proxy from the roster',
     lambda e: e[:-1]),
    (DECL, 'G1', _G1FAMILY + ('G8', 'G9'), 'move a proxy 5 u off its declared coord',
     lambda e: e[:-1] + [(e[-1][0], e[-1][1] + 5.0, e[-1][2], e[-1][3])]),
    (DECL, 'G2', _G1FAMILY + ('G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9'),
     'push a proxy onto the padded neighbour strip outside drxBC3',
     lambda e: e[:-1] + [(e[-1][0], -30.0, e[-1][2], e[-1][3])]),
    (DECL, 'G4', _G1FAMILY + ('G4', 'G6', 'G7', 'G8', 'G9'),
     'keep the XZ but flatten Y to the top tier (the design\'s missing axis)',
     lambda e: [(e[0][0], e[0][1], 39.0, e[0][3])] + e[1:]),
    (DECL, 'G7', _G1FAMILY + ('G4', 'G6', 'G7', 'G8', 'G9'),
     'drop a pack on the arrival portal (the b44 landing-pileup class)',
     lambda e: [(e[0][0], 225.0, 39.005, 220.0)] + e[1:]),
    (DECL, 'G7', _G1FAMILY + ('G4', 'G6', 'G7', 'G8', 'G9'),
     'drop a pack 0.5 u from the west door seam (the walk-in variant)',
     lambda e: e[:-1] + [(e[-1][0], 0.5, 3.005, e[-1][3])]),
    (DECL, 'G8', _G1FAMILY + ('G6', 'G7', 'G8', 'G9'),
     'stack two proxies on top of one another (R-30\'s own words)',
     lambda e: e[:-1] + [(e[-1][0], e[-2][1] + 1.0, e[-2][2], e[-2][3])]),
    (DECL, 'G9', _G1FAMILY + ('G4', 'G6', 'G7', 'G8', 'G9'),
     'pile the whole congregation into one screen box',
     lambda e: [(d, 100.0 + i * 2.0, 15.005, 160.0) for i, (d, _x, _y, _z) in enumerate(e)]),
    # ---- MAP plants. These are the four the round-1 vet planted and round 1 missed,
    # plus the three the round-1 gate CRASHED on, plus G1b's own subject.
    (MAP, 'G1c', _G1FAMILY, 'delete one of the 281 SHIPPED instances (a decoration)',
     map_del_instance(0)),
    (MAP, 'G1c', _G1FAMILY + ('G7', 'G8', 'G9'),
     'delete one of amgoz1\'s TEN shipped MONSTER proxies',
     map_del_instance(127)),
    (MAP, 'G1c', _G1FAMILY,
     'delete a shipped instance AND pad, so the count still reads 295',
     map_del_and_pad(0, 1)),
    (MAP, 'G1c', _G1FAMILY + ('G7', 'G8', 'G9'),
     'teleport a shipped proxy 500 u off the level',
     map_move_instance(127, 500.0, 0.0, 500.0)),
    (MAP, 'G1b', _G1FAMILY, 'give a NEW instance a non-identity rotation',
     map_rotate_instance(D.BASELINE_INSTANCES)),
    (MAP, 'G10', ('G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G8b', 'G9', 'G10', 'G11'),
     'b89: flip one byte inside the 0x0b navmesh container',
     map_navmesh('flip')),
    (MAP, 'G10', ('G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G8b', 'G9', 'G10', 'G11'),
     'b89: truncate the 0x0b container to a 148-byte stub',
     map_navmesh('truncate')),
    (MAP, 'G3', ('G3',), 'make tileset 3 disagree with tileset 1',
     map_tileset_divergence()),
]


def negtest(map_path, arz_path, baseline_path=None):
    print(f'PLANTED NEGATIVE TESTS for gate {GATE}')
    print(f'  map      : {map_path}')
    print(f'  baseline : {baseline_path or "(none) - G1d/G10 identity halves inactive"}\n')
    base_bad, base_r = run(map_path, baseline_path=baseline_path, arz_path=arz_path,
                           quiet=True)
    print(f'  baseline (unmodified): {base_bad} failing '
          f'-> {"OK, the gate is green before we break it" if base_bad == 0 else "PROBLEM"}')
    if base_bad:
        for gid, name, ok, detail in base_r.rows:
            if not ok:
                print(f'      {gid} {name}: {detail}')
        print('\nNEGTEST: ABORTED - the gate is not green on the real placements.')
        return 1
    exp = expected_specs()
    fails = 0
    for kind, want_gid, allowed, label, mutate in PLANTS:
        if kind == DECL:
            bad, res = run(map_path, baseline_path=baseline_path, arz_path=arz_path,
                           expected=mutate(list(exp)), quiet=True)
        else:
            bad, res = run(map_path, baseline_path=baseline_path, arz_path=arz_path,
                           blob_patch=mutate, quiet=True)
        caught = {row[0] for row in res.rows if not row[2]}
        hit = want_gid in caught
        stray = sorted(caught - set(allowed))
        ok = hit and not stray
        print(f'  [{kind}] plant must fail {want_gid:<4s} {label:<60s} -> '
              f'{"CAUGHT" if hit else "MISSED":7s} by {sorted(caught) or "nothing"}'
              + (f'  ⚠️ STRAY {stray}' if stray else ''))
        if not ok:
            fails += 1
    ndecl = sum(1 for p in PLANTS if p[0] == DECL)
    print(f'\nNEGTEST: {len(PLANTS) - fails}/{len(PLANTS)} plants correct '
          f'({ndecl} declaration + {len(PLANTS) - ndecl} map-side); each had to fail its '
          f'target gate AND stay inside its allow-set -> {"PASS" if not fails else "FAIL"}')
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
        # ROUND-2 FIX: --baseline is now threaded into the negative tests, so G1d's and
        # G10's byte-identity halves are actually exercised by the plants. Round 1's
        # negtest never passed it, leaving those halves unproven.
        return negtest(a.map, a.arz, a.baseline)
    bad, _ = run(a.map, a.baseline, a.arz)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
