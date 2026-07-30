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

    # ── one hop of TRANSITIVE reachability for anything that looked inert ────
    print('\n--- transitive check: is the SPAWNER of an "inert" record placed? ---')
    any_transitive = False
    for rec, (n_static, n_refs, _v) in findings.items():
        if n_static:
            continue
        for parent, field in sorted(set(refs.get(rec, []))):
            if field not in _SPAWN_FIELDS:
                continue
            p_static = static_hits(parent)
            any_transitive = True
            print('  %s <- %s .%s : the SPAWNER is placed in %d level(s) (%d instance(s))'
                  % (rec.rsplit('\\', 1)[-1], parent.rsplit('\\', 1)[-1], field,
                     len(p_static), sum(p_static.values())))
            for lvl, c in sorted(p_static.items())[:4]:
                print('        %s x%d' % (lvl, c))
    if not any_transitive:
        print('  (nothing to check - every roster record is either placed or pooled)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
