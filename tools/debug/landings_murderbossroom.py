#!/usr/bin/env python3
"""MURDERBOSSROOM-NPC: the verified landing + planned-placement fixture (2026-07-28).

Committed so the survey that unblocked `MURDERBOSSROOM-NPC` is REPRODUCIBLE, and so the
wave that finally wires the feature gates the exact same coords it ships. Feed it to
`tools/debug/gate_landing_clearance.py` as BOTH the landing set and the planned-placement
set (it exposes `LANDINGS` and `SPECS`):

    py tools/debug/gate_landing_clearance.py \
        --map local/Levels_merged.arc \
        --wiring tools/debug/landings_murderbossroom.py \
        --placements tools/debug/landings_murderbossroom.py

Result on the canonical build (`local/Levels_merged.arc`, 2026-07-28) - GATE G-LAND: PASS:

    [PASS] enter_murderbossroom world=(-3538, 3, -5937) tag=tagSVCEnterMurderBossRoom
        -> XPack/Levels/Secret_Place/murderbossroom.lvl v0x0e local=(54.0,18.0) (+1 planned)
        nav: N:d=0.14/clr=100%  E:d=0.14/clr=100%  L:d=0.14/clr=100%  comp#1/80608  on-mesh
          d=  3.61u  npc    svc_area_return_murder.dbr  local=(51.0,16.0) [PLANNED]
          d=  6.00u  prop   tj_archway01.dbr            local=(54.0,24.0)
          d=  7.24u  prop   tj_urngrounded01.dbr        local=(53.9,10.8)
          d= 16.00u  other  murderbunny.dbr             local=(54.0,34.0)
        => clear + on-mesh

LEVEL FACTS (canonical build): `XPack/Levels/Secret_Place/murderbossroom.lvl`, v0x0e SV-only,
blob 111,817 B, grid corner (-3592, 0, -5955), 0x05 = 16 instances, 0x14 count = 0,
0x0b = 70,910 B. The navmesh is cs=0.2 with 80,608 walkable cells in EXACTLY ONE connected
component in all 3 tilesets, so there is no reachability-partition risk. The level is a single
N-S corridor on the x~48-60 band: urn + zzz_theunderlord egg at local z=10.8, archway +
tj_portcullis02 at z=24, the murderbunny crow boss at z=34, the trg_portcullis01 trigger at
z=55, archway + tj_portcullis01 at z=72, statues at z=79-91.

WHY THESE COORDS: the pair is 3.61u apart, reproducing the proven svc_testhub_return_sparta /
_uber "~3u off the landing so the player sees the return NPC on arrival" pattern, and both sit
16-18u from the murderbunny set-piece - deliberately OUTSIDE it (the b44 deadly-landing lesson:
an on-mesh landing on top of a boss/container pins the player and kills him).

SCOPE: this file is a GATE FIXTURE only. It places nothing and wires nothing. The feature is
still OPEN - see docs/reports/b62_travelers_into_areas.md "UPDATE 2026-07-28" for the remaining
DB + Text + map + quest steps, the WARDEN LAW constraint (the new boat-dialog record must be
placed exactly once), and the hard rule that the map placement and the enter-offer must ship in
the SAME commit (the P0-A "no way back" class).
"""

# Only ONE teleport landing exists here (the enter-offer's arrival point). The return leg
# lands back at the darkforestenter ORIGIN (-2396, 2, -5790), an already-gated coord, so it
# is not re-listed. The interior NPC is a PLACEMENT, not a landing (listing it as a landing
# would only measure its distance to itself).
LANDINGS = [
    ('enter_murderbossroom', (-3538, 3, -5937), 'tagSVCEnterMurderBossRoom'),
]

# The paired interior return NPC as a PLANNED 0x05 placement (level-LOCAL coords), so the
# gate proves the landing stays clear of the NPC the wiring wave is about to add.
SPECS = {
    'xpack/levels/secret_place/murderbossroom.lvl': [
        (r'records\quests\svc_area_return_murder.dbr', 51.0, 3.0, 16.0),
    ],
}
