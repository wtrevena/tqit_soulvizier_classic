#!/usr/bin/env python3
"""gate_doors_hub - RESURRECTED as a delegate (2026-08-13, R-246 native-device travel).

LINEAGE (three eras, all deliberate):
  1. build24/25: this gate verified the original invented door pairs + the 20-portal
     born-open TESTHUB hub (sub-gates placement/hubidentity/crosstalk + baseline diffs).
  2. 2026-07-12 P0: every authored walk-through portal was stripped ("yanked to the
     Garden"); this file became a tombstone delegating to the boat-dialog travel-law
     gate. Walk-through portals were BANNED.
  3. 2026-08-13 R-246: Will's "Native devices" ruling SUPERSEDES the mechanism half of
     that P0 - doors are BACK as the canonical travel devices (born-open GridEntrance
     pairs, zero quest rows), because the boat-row alternative corrupts the engine's
     stateful offer registry. The P0's PLACEMENT half survives: doors OFF every traffic
     lane, walked into deliberately - enforced by the successor's C-block.

The door world's invariants now live in ONE place:

    tools/gate_device_resolution.py   (D1-D7 bindings/uids/appended-host law,
                                       C1-C5 lane/clearance, Y1/ON terrain; negtests)

This file forwards to it so any battery calling gate_doors_hub gets the honest
current answer. The build25-era implementation stays in git history.

Usage: py tools/debug/gate_doors_hub.py [<canonical.arc> [<testhub.arc>]]
Exit 0 = PASS (all forwarded runs green).
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_LEGACY_SUBGATES = {'collateral', 'hubidentity', 'placement', 'c1', 'c3', 'c4',
                    'crosstalk', 'all'}


def main(argv):
    args = [a for a in argv[1:] if a not in _LEGACY_SUBGATES]
    if not args:
        print('usage: gate_doors_hub.py <canonical.arc> [<testhub.arc>]  '
              '(delegates to gate_device_resolution)')
        return 2
    print('=== gate_doors_hub (R-246): doors are back as native devices -> '
          'delegating to gate_device_resolution ===')
    gate = str(REPO / 'tools' / 'gate_device_resolution.py')
    rc = subprocess.call([sys.executable, gate, '--map', args[0]])
    if len(args) > 1:
        rc |= subprocess.call([sys.executable, gate, '--map', args[1], '--hub'])
    return rc


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
