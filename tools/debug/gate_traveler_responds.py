#!/usr/bin/env python3
"""RETIRED GATE (2026-08-13, R-246 native-device travel): the b48 mute-traveler battery.

WHAT IT GUARDED: every hub boat-dialog traveler NPC must RESPOND in-game (no mute
clickable traveler ships). Its collision model (1 route : 1 NPC; same-level tag/dest
collisions mute the later registrant) was proven correct on the deployed bytes - and
then R-246 proved the deeper mechanism: the blanket OnLevelLoad refire step arming 39
BoatDialog rows corrupts the engine's STATEFUL boat-offer registry (cross-bound rows
execute other rows, labels included; cross-bound NPCs go fully mute - the Warden).
No per-row collision check can make that arming pattern safe.

R-246 therefore RIPPED the entire hub row world this gate audited (14 svc_helos_trav_*
+ 10 svc_area_return_* + warden + testhub rig rows). The surviving armed roster is
frozen BY NAME, budgeted per step, and reuse-banned by the successor gate:

    tools/gate_boatdialog_budget.py   (on the BUILT Quests.arc; negtests N1-N3)

This file is retired IN PLACE (honest filename for any battery that still calls it)
and DELEGATES to the successor. The 646-line b48 implementation is preserved in git
history (tag: the pre-R-246 f9f213b lineage) if the collision logic is ever needed.

Usage: py tools/debug/gate_traveler_responds.py [<Quests.arc> [<Levels.arc>]]
Defaults: work/SoulvizierClassic/Resources/Quests.arc. Exit 0 = PASS.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main(argv):
    quests = argv[1] if len(argv) > 1 else str(
        REPO / 'work/SoulvizierClassic/Resources/Quests.arc')
    print('=== gate_traveler_responds RETIRED (R-246: the hub boat-row world it '
          'audited was ripped) -> delegating to gate_boatdialog_budget ===')
    cmd = [sys.executable, str(REPO / 'tools' / 'gate_boatdialog_budget.py'),
           '--quests', quests]
    if len(argv) > 2:
        cmd += ['--map', argv[2]]
    return subprocess.call(cmd)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
