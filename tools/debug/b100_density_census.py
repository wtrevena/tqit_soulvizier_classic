#!/usr/bin/env python3
"""b100 - worst-screen DENSITY census over the whole built map, EXACT method.

Read-only. For every level in a built `Levels.arc`, sum each placed monster proxy's
pool `spawnMax` and report the worst axis-aligned SCREEN x SCREEN world-unit box.

WHY THIS EXISTS: the b100 design pass measured "worst-case simultaneous entities in
one screen" with a box CENTRED ON A PROXY. That undercounts - the worst box is
generally not centred on any point. Example from the level this lane touches: the
two shipped `zparty_witchfest_2099` proxies at world (4288.6,3074.9) and
(4344.4,3044.1) are 55.8 u apart in x and 30.8 u in z, so no 60x60 box centred on
either contains the other (the design read 12), but the box with its low corner at
(4288.6, 3044.1) contains both (the true answer is 24). Every comparator the design
quoted - base-game median 14 / p90 70 / max 162 - carries the same undercount, so
the design's headline "the proposal sits at the base-game median" was compared
against numbers produced by a different, weaker measurement than the one the gate
would use. This module recomputes both, side by side, so the comparison is honest.

The exact box uses the standard argument: an optimal axis-aligned box may be slid
until its low corner is pinned on each axis by a point, so enumerating (px, qz) over
all placed proxies is exhaustive.

Usage:
  py tools/debug/b100_density_census.py --map local/Levels_merged.arc
  py tools/debug/b100_density_census.py --map <arc> --level drxbc3
"""
import sys
import re
import argparse
import statistics
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import contracts_map as CM                      # noqa: E402
from rec02_format import parse_rec02            # noqa: E402

SCREEN = 60.0
CELL_AREA = 0.04
# the design's comparator cohort, kept identical so the numbers are like-for-like
COHORT_HINTS = ('cave', 'crypt', 'tomb')
MIN_PROXIES = 5
NPLAYERS = 1
# (round-2: MIN_AREA = 3000.0 used to live here and was never read by anything. The
# design pass's cohort filter was ">= 5 proxies AND > 3000 sq u", but computing a
# per-level walkable area needs a full 0x0b decompress for all 2,282 levels, so this
# module only ever applied the proxy-count half. Removed rather than left as a lie;
# the cohort is exactly "cave/crypt/tomb in the name, not blood cave, >= 5 monster
# proxies", n=80, and that is what every number below is computed over.)


def worst_exact(pts, wi=3):
    """Worst EXACT box. `wi` picks the weight column: 3 = raw spawnMax, 4 = effective."""
    if not pts:
        return 0, None
    best, at = 0, None
    for p0 in pts:
        x0 = p0[0]
        for p1 in pts:
            z0 = p1[1]
            tot = sum(p[wi] for p in pts
                      if x0 <= p[0] <= x0 + SCREEN and z0 <= p[1] <= z0 + SCREEN)
            if tot > best:
                best, at = tot, (x0 + SCREEN / 2, z0 + SCREEN / 2)
    return best, at


def worst_centred(pts):
    """The design pass's method, reproduced so the delta is visible."""
    best, at = 0, None
    for p0 in pts:
        ax, az = p0[0], p0[1]
        tot = sum(p[3] for p in pts
                  if abs(p[0] - ax) <= SCREEN / 2 and abs(p[1] - az) <= SCREEN / 2)
        if tot > best:
            best, at = tot, (ax, az)
    return best, at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default=str(REPO / 'local' / 'Levels_merged.arc'))
    # ROUND-2 FIX: was REPO.parent.parent.parent/'work'/... which from a worktree
    # resolved to the MAIN CHECKOUT's staged arz (another lane's artifact) and from
    # the main checkout to a nonexistent C:/Users/work/... Now REPO-relative.
    ap.add_argument('--arz', default=str(REPO / 'work' / 'SoulvizierClassic' /
                                        'Database' / 'SoulvizierClassic.arz'))
    ap.add_argument('--level', default=None, help='report one level in detail')
    a = ap.parse_args()

    arc = CM.Arc.from_file(a.map)
    mp = arc.world_map()
    secs = CM.parse_top_sections(mp)
    levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
    arz = CM.Arz.from_arz(a.arz)
    cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}
    names = {CM.norm_rec(x): x for x in arz.record_names()}

    # ROUND-2: the census now reports EFFECTIVE entities alongside raw spawnMax.
    # A pool's spawnMax is not what the engine spawns - the pool's proxyPoolEquation
    # multiplies it (proxypoolequation_01 = 3.60025x at 1 player, _02 = 1.357143x).
    # Every blood-cave pool uses _02; 854 of the base-game cohort's 887 pool
    # references use _01. Comparing RAW spawnMax across those two families, which is
    # what round 1 did, compares different units.
    info_cache = {}
    eq_mix = Counter()

    def info(dbr):
        """(raw spawnMax, effective, equation basename)"""
        n = CM.norm_rec(dbr)
        if n in info_cache:
            return info_cache[n]
        sm, mult, eqn = 0, 1.0, ''
        if n in names:
            pool = arz.field(names[n], 'pool1')
            if isinstance(pool, list):
                pool = pool[0] if pool else None
            if pool and CM.norm_rec(pool) in names:
                pn = names[CM.norm_rec(pool)]
                q = arz.field(pn, 'spawnMax')
                if isinstance(q, list):
                    q = q[0] if q else 0
                sm = int(q or 0)
                eq = arz.field(pn, 'proxyPoolEquation')
                if isinstance(eq, list):
                    eq = eq[0] if eq else None
                if eq:
                    eqn = str(eq).replace('/', '\\').split('\\')[-1]
                    k = CM.norm_rec(eq)
                    mult = None
                    if k in names:
                        expr = arz.field(names[k], 'spawnMaxEquation')
                        if isinstance(expr, list):
                            expr = expr[0] if expr else None
                        m = re.match(r'^\s*poolValue\s*\*\s*(.*)$', str(expr or ''), re.I)
                        if m:
                            try:
                                mult = float(eval(  # noqa: S307 - fixed-form arithmetic
                                    m.group(1).replace('numberOfPlayers', str(NPLAYERS)),
                                    {'__builtins__': {}}, {}))
                            except Exception:
                                mult = None
        info_cache[n] = (sm, sm * (mult if mult is not None else 1.0), eqn,
                         mult is None)
        return info_cache[n]

    def smax(dbr):
        return info(dbr)[0]

    rows = []
    for lv in levels:
        fname = lv['fname'].replace('\\', '/')
        base = fname.split('/')[-1].replace('.lvl', '')
        blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        try:
            items = CM.parse_0x05(blob)[1]
        except Exception:
            continue
        cx, _cy, cz = lv['corner']
        pts = []
        for it in items:
            d = it['dbr'].decode('latin-1')
            if cls.get(CM.norm_rec(d)) != 'Proxy' or 'shrine' in d.lower():
                continue
            sm, eff, eqn, unparsed = info(d)
            if sm <= 0:
                continue
            eq_mix[eqn or '(none)'] += 1
            if unparsed:
                eq_mix['(UNPARSED spawnMaxEquation)'] += 1
            pts.append((cx + it['pos'][0], cz + it['pos'][2], d, sm, eff, eqn))
        if not pts:
            continue
        area = None
        if a.level and base.lower() == a.level.lower():
            try:
                b0b = [s for t, s in CM.parse_blob_sections(blob) if t == 0x0b][0]
                doc = parse_rec02(b0b, decompress=True)
                n = 0
                for rec in doc['sets'][0]['records']:
                    n += sum(1 for i, h in enumerate(rec['heights'])
                             if h != 0xff and rec['areas'][i] != 0)
                area = n * CELL_AREA
            except Exception:
                area = None
        we, at = worst_exact(pts, 3)
        wf, atf = worst_exact(pts, 4)
        wc, _ = worst_centred(pts)
        rows.append(dict(base=base, fname=fname, n=len(pts), we=we, wf=wf, wc=wc,
                         at=at, atf=atf, area=area,
                         eqs=Counter(p[5] or '(none)' for p in pts),
                         raw_total=sum(p[3] for p in pts),
                         eff_total=sum(p[4] for p in pts)))

    if a.level:
        for r in rows:
            if r['base'].lower() == a.level.lower():
                print(f"{r['fname']}: {r['n']} monster proxies, "
                      f"total raw spawnMax {r['raw_total']}, "
                      f"total EFFECTIVE {r['eff_total']:.1f}")
                print(f"  worst {SCREEN:.0f}x{SCREEN:.0f} EXACT raw       = {r['we']}"
                      + (f"  (box centre world {r['at'][0]:.1f},{r['at'][1]:.1f})"
                         if r['at'] else ''))
                print(f"  worst {SCREEN:.0f}x{SCREEN:.0f} EXACT EFFECTIVE = "
                      f"{r['wf']:.1f}"
                      + (f"  (box centre world {r['atf'][0]:.1f},{r['atf'][1]:.1f})"
                         if r['atf'] else ''))
                print(f"  worst {SCREEN:.0f}x{SCREEN:.0f} CENTRED raw     = {r['wc']}"
                      f"   (the design pass's method)")
                print(f"  pool equation mix: {dict(r['eqs'])}")
                if r['area']:
                    print(f"  own-0x0b walkable (all areas) = {r['area']:.0f} sq u")
        return 0

    print('=== blood cave (this mod\'s own content), sorted by EFFECTIVE ===')
    for r in sorted(rows, key=lambda r: -r['wf']):
        if 'xbloodcave' in r['fname'].lower():
            print(f"  {r['base']:38s} proxies={r['n']:3d}  worst EFFECTIVE={r['wf']:7.1f}"
                  f"  raw EXACT={r['we']:4d}  raw CENTRED={r['wc']:4d}")

    cohort = [r for r in rows
              if any(h in r['fname'].lower() for h in COHORT_HINTS)
              and 'xbloodcave' not in r['fname'].lower()
              and r['n'] >= MIN_PROXIES]
    ex = sorted(r['we'] for r in cohort)
    ef = sorted(r['wf'] for r in cohort)
    ce = sorted(r['wc'] for r in cohort)

    def pct(v, q):
        return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]
    print(f"\n=== base-game cave/crypt/tomb cohort (n={len(cohort)}, >= {MIN_PROXIES} proxies) ===")
    print(f"  EFFECTIVE (the comparable unit): min {ef[0]:.1f}  p25 {pct(ef,.25):.1f}  "
          f"MEDIAN {pct(ef,.5):.1f}  p75 {pct(ef,.75):.1f}  p90 {pct(ef,.9):.1f}  "
          f"max {ef[-1]:.1f}")
    print(f"  raw worst-screen EXACT  : min {ex[0]}  p25 {pct(ex,.25)}  MEDIAN {pct(ex,.5)}  "
          f"p75 {pct(ex,.75)}  p90 {pct(ex,.9)}  max {ex[-1]}")
    print(f"  raw worst-screen CENTRED: min {ce[0]}  p25 {pct(ce,.25)}  MEDIAN {pct(ce,.5)}  "
          f"p75 {pct(ce,.75)}  p90 {pct(ce,.9)}  max {ce[-1]}")
    print(f"  mean EXACT/CENTRED ratio: "
          f"{statistics.mean(r['we'] / r['wc'] for r in cohort if r['wc']):.2f}x")
    cmix = Counter()
    for r in cohort:
        cmix.update(r['eqs'])
    print(f"  cohort pool equation mix : {dict(cmix)}")
    bmix = Counter()
    for r in rows:
        if 'xbloodcave' in r['fname'].lower():
            bmix.update(r['eqs'])
    print(f"  blood-cave equation mix  : {dict(bmix)}")
    print(f"  ⚠️ RAW numbers are NOT comparable across those two mixes - "
          f"_01 is {3.60025:.5f}x and _02 is {1.357143:.6f}x at {NPLAYERS} player.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
