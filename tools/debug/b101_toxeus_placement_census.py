#!/usr/bin/env python3
r"""b101 (R-99): PLACEMENT CENSUS for the whole Toxeus monster roster.

R-99 orders every Toxeus creature record onto the apex orb `genericbossorb_05`,
including the two Iron Lore `zzdev` dev dummies, and explicitly requires the
placement question to be ANSWERED rather than assumed:

    "First VERIFY whether either is actually placed anywhere; if they are
     unreachable dev leftovers the wiring is inert, which is a fine outcome -
     but record the placement finding either way. RETIREMENT PROTOCOL: do not
     delete or retire them; code-unreferenced is not proof of dead."

This tool answers it on BOTH reachability axes, because either one alone is a
false negative:

  1. STATIC placement - a `0x05` instance of the record in the shipped
     `Levels.arc` (the same walk `tools/debug/census_placements.py` uses, via the
     canonical version-aware `contracts_map.parse_0x05`).
  2. DYNAMIC reachability - a DB referrer: a ProxyPool `nameN` / `nameChampionN`
     slot, a `q_*` proxy, or an `actorToSpawnOnDeath` chain. A record with zero
     static placements can still be the most-met monster in the game (the Endless
     Hunt is in 346 pools and statically placed once), and a record with zero
     pool slots can still spawn if something placed spawns it on death (which is
     exactly how `z_toxeus` works).

Both axes are walked TRANSITIVELY for the spawn-on-death / proxy chain, so
"z_toxeus is placed nowhere" is only reported after checking whether the thing
that spawns it is placed.

Usage:
  py tools/debug/b101_toxeus_placement_census.py <built.arz> <Levels.arc>

Exit 0 always - this is a MEASUREMENT tool, not a gate. The gate that enforces
the roster is uber_apex_orb.verify().
"""
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'contracts'))

from arz_patcher import ArzDatabase                      # noqa: E402
from arc_patcher import ArcArchive                       # noqa: E402
from merge_levels_binary import parse_sections           # noqa: E402
from contracts_map import (parse_level_index, parse_0x05, SEC_LEVELS)  # noqa: E402

# the chain fields that make a record reachable without being placed itself
_SPAWN_FIELDS = ('actorToSpawnOnDeath', 'name1', 'name2', 'name3', 'name4',
                 'name5', 'name6', 'name7', 'name8', 'name9', 'name10')

# How far UP the reference graph to walk looking for a statically placed ancestor.
# 3 is enough for this map's deepest measured chain (placed proxy -> pool ->
# monster = 2) with one hop of headroom; each hop costs one whole-db field scan.
_MAX_HOPS = 3


def _norm(s):
    return str(s).replace('/', '\\').lower()


def load_static_index(arc_path):
    """{lowercased dbr path -> [(level, count)]} for every 0x05 instance."""
    arc = ArcArchive.from_file(Path(arc_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    idx = defaultdict(lambda: defaultdict(int))
    unparsed = []
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        try:
            _hdr, insts = parse_0x05(blob)
        except Exception as e:                    # reported, never silent
            unparsed.append((lv['fname'], repr(e)))
            continue
        for i in insts:
            dbr = i['dbr']
            if isinstance(dbr, bytes):
                dbr = dbr.decode('latin-1', 'replace')
            idx[_norm(dbr)][lv['fname']] += 1
    return idx, len(levels), unparsed


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    arz, arc = sys.argv[1], sys.argv[2]

    db = ArzDatabase.from_arz(Path(arz))

    # ── roster, derived exactly as uber_apex_orb derives it ──────────────────
    sys.path.insert(0, str(HERE.parent / 'patches'))
    from patches import uber_apex_orb as M                # noqa: E402
    roster = M.toxeus_roster(db)

    print('\n=== b101 Toxeus placement census ===')
    print('arz    : %s' % arz)
    print('map    : %s' % arc)
    print('roster : %d records (derived)' % len(roster))

    # ── DB referrers (dynamic reachability), one whole-db pass ───────────────
    want = {_norm(r): r for r in roster}
    refs = defaultdict(list)
    for n in db.record_names():
        ff = db.get_fields(n)
        if not ff:
            continue
        for k, tf in ff.items():
            base = k.split('###')[0]
            for val in tf.values:
                if isinstance(val, str) and _norm(val) in want:
                    refs[want[_norm(val)]].append((n, base))

    print('\nloading the map (this walks every level blob) ...')
    static, n_levels, unparsed = load_static_index(arc)
    print('  levels walked: %d ; unparsed 0x05 sections: %d' % (n_levels, len(unparsed)))
    for fn, err in unparsed[:10]:
        print('    UNPARSED %s : %s' % (fn, err))

    def static_hits(rec):
        return static.get(_norm(rec), {})

    print('\n%-64s %8s %8s  %s' % ('record', 'static', 'db-refs', 'verdict'))
    print('-' * 118)
    findings = {}
    for rec in roster:
        st = static_hits(rec)
        rr = sorted(set(refs.get(rec, [])))
        n_static = sum(st.values())
        if n_static and rr:
            verdict = 'REACHABLE (placed + pooled)'
        elif n_static:
            verdict = 'REACHABLE (statically placed)'
        elif rr:
            verdict = 'REACHABLE via %d db referrer(s)' % len(rr)
        else:
            verdict = 'NO placement, NO db referrer -> INERT'
        findings[rec] = (n_static, len(rr), verdict)
        print('%-64s %8d %8d  %s'
              % (rec.rsplit('\\', 1)[-1], n_static, len(rr), verdict))
        for lvl, c in sorted(st.items())[:6]:
            print('%68s%s x%d' % ('', lvl, c))
        for r, f in rr[:6]:
            print('%68s<- %s .%s' % ('', r.rsplit('\\', 1)[-1], f))
        if len(rr) > 6:
            print('%68s<- ... +%d more referrer(s)' % ('', len(rr) - 6))

    # ── MULTI-HOP reachability: walk UP until a PLACED ancestor is found ─────
    # WHY THIS IS NOT ONE HOP (measured, and it changes every champion's verdict).
    # This tool originally checked a single hop and printed "the SPAWNER is placed
    # in 0 level(s)" for every champion, which reads as "unreachable" and is FALSE.
    # The real placement graph in this map is TWO hops:
    #     records\drxmap\proxy\q_toxeus_hunt_lone.dbr        <- PLACED (0x05)
    #        -> records\drxmap\proxy\pools\q_toxeus_hunt_lone.dbr   (the pool)
    #           -> um_toxeus_hunt_99.dbr                            (.name1)
    # The monster's direct referrer is the POOL, which is never placed itself; the
    # PROXY one level above it is. So a 1-hop check under-reports by construction.
    # This walk is breadth-first UP the reference graph to _MAX_HOPS, stopping at
    # the first placed ancestor, and it prints the whole path so the claim is
    # auditable rather than a bare verdict.
    print('\n--- MULTI-HOP reachability: nearest PLACED ancestor (max %d hops) ---'
          % _MAX_HOPS)
    for rec in roster:
        if sum(static_hits(rec).values()):
            print('  %-26s PLACED DIRECTLY' % rec.rsplit('\\', 1)[-1])
            continue
        # frontier: {record -> path of (child, field) that led here}
        frontier = {rec: []}
        seen = {_norm(rec)}
        hit = None
        for hop in range(1, _MAX_HOPS + 1):
            parents = {}
            targets = {_norm(k): k for k in frontier}
            for n in db.record_names():
                ff = db.get_fields(n)
                if not ff:
                    continue
                for k, tf in ff.items():
                    base = k.split('###')[0]
                    for val in tf.values:
                        if isinstance(val, str) and _norm(val) in targets:
                            child = targets[_norm(val)]
                            if _norm(n) in seen:
                                continue
                            parents.setdefault(n, frontier[child] + [(child, base)])
            if not parents:
                break
            placed = sorted((p for p in parents if sum(static_hits(p).values())),
                            key=lambda p: -sum(static_hits(p).values()))
            if placed:
                hit = (placed[0], parents[placed[0]], hop)
                break
            seen |= {_norm(p) for p in parents}
            frontier = parents
        if hit:
            anc, path, hop = hit
            st = static_hits(anc)
            print('  %-26s REACHABLE at hop %d via PLACED %s (x%d in %s)'
                  % (rec.rsplit('\\', 1)[-1], hop, anc.rsplit('\\', 1)[-1],
                     sum(st.values()), sorted(st)[0]))
            # printed TOP-DOWN (placed ancestor first) so the chain reads the way
            # the engine walks it: what is placed -> what it draws -> the monster.
            chain = [anc] + [c for c, _f in reversed(path)]
            hops = [f for _c, f in reversed(path)]
            for i, node in enumerate(chain):
                arrow = '  .%s ->' % hops[i] if i < len(hops) else ''
                print('        %s%s%s'
                      % ('PLACED ' if i == 0 else '', node.rsplit('\\', 1)[-1], arrow))
        else:
            print('  %-26s NO placed ancestor within %d hops -> INERT in THIS map'
                  % (rec.rsplit('\\', 1)[-1], _MAX_HOPS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
