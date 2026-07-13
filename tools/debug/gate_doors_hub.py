#!/usr/bin/env python3
"""RETIRED GATE (2026-07-13): the doors+hub walk-through-portal battery.

Every travel mechanism this gate verified - the A1 Garden / A2 Secret Place / Sparta Crypt / Uber
Dungeon walk-through GridEntrance "doors" and the 20-portal born-open TESTHUB hub - was REMOVED by
the 2026-07-12 P0 hotfix (commit 0f08297). Walk-through / proximity teleport portals are now BANNED
everywhere we author; all cross-area travel is talk-to-an-NPC boat-dialog (Model C). So this gate's
portal sub-gates (`placement`, `hubidentity`, `crosstalk`) assert content that intentionally no
longer exists, and its baseline-diff sub-gates (`collateral`, `c1`, `c3`, `c4`) compared the
build25 map against long-superseded baselines (that one-time fountain-respawn / caravan / smoke
verification shipped in build24-26 and is covered by the standing contract-suite collateral gates).

It is retired in place (filename kept so any gate battery that still calls it gets an HONEST
result) and DELEGATES to the post-P0 travel-law gate:

    tools/debug/gate_travel_npc_invariants.py

which asserts: 0 authored walk-through portals (canonical + TESTHUB), the build37 Helos traveler
hub warden-clean (17 records, 0 canonical / 1 TESTHUB each), the retired Helos master, the canonical
NPC travelers, and full map/quests/arz cross-file agreement. The original 453-line implementation is
preserved in git history (before this commit) if the pre-P0 portal logic is ever needed.

Usage: py tools/debug/gate_doors_hub.py [<canonical.arc> [<testhub.arc>]]   (args forwarded)
Exit 0 = PASS, non-zero = FAIL.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate_travel_npc_invariants as G

_RETIRED_SUBGATES = {'collateral', 'hubidentity', 'placement', 'c1', 'c3', 'c4', 'crosstalk', 'all'}


def main(argv):
    print('=== gate_doors_hub RETIRED (walk-through portals removed 2026-07-12) -> '
          'delegating to gate_travel_npc_invariants ===')
    # Drop a legacy sub-gate name if present (e.g. "gate_doors_hub.py placement"); forward .arc paths.
    args = [a for a in argv[1:] if a not in _RETIRED_SUBGATES]
    return G.main([argv[0]] + args)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
