r"""PLANTED NEGATIVE TEST for SVC_REQUIRE_GATES (B-GATE-HARDEN-1).

THE DEFECT CLASS
----------------
`build_svc_database.py` runs three checks that need the work/ layout (the game dir AND
the mod's staged `Resources` beside the output .arz):
  * A5  Act-5 leak fix        - needs the base DB to import 4 portal records
  * A9  render-chain contract - needs the art arcs to resolve pet mesh/texture/icons
  * F2  summons contract lane - needs both to run the contract battery
Historically each of these printed `WARNING: ... SKIPPED` and carried on. That is
correct for a scratch / determinism rebuild that deliberately writes to a temp dir, but
it means a MIS-PATHED work build silently ships UNGATED - the same blind spot that let
the b89 malformed 148-byte navmesh stub survive every gate for 20+ builds.

`SVC_REQUIRE_GATES=1` (set by `scripts/bootstrap_working_mod.ps1`, the gate of record)
turns each of those skips into a hard build failure.

WHAT THIS TEST PLANTS
---------------------
The exact "gate cannot run" condition, both ways, without running a ~15-minute build:
  1. flag OFF -> `_gate_unavailable` WARNs and returns (historical behaviour preserved)
  2. flag ON  -> `_gate_unavailable` raises SystemExit (the build dies)
  3. `_require_gates` accepts 1/true/yes/on case-insensitively and nothing else
  4. `validate_render_chain.validate` returns 2 (never 0) when its input dirs are
     unusable - the second line of defence for direct CLI invocations that bypass
     build_svc_database's caller-side skip decision entirely

Run:  py tools/debug/negtest_require_gates.py
Exits 0 iff every case behaves; else 1.
"""
import os
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))


def _set_flag(val):
    if val is None:
        os.environ.pop('SVC_REQUIRE_GATES', None)
    else:
        os.environ['SVC_REQUIRE_GATES'] = val


def main():
    import build_svc_database as B
    import validate_render_chain as R

    ok = True
    print('=== SVC_REQUIRE_GATES planted negative test (B-GATE-HARDEN-1) ===')

    # --- 1. flag OFF: a gate that cannot run must WARN and continue (unchanged) ----
    _set_flag(None)
    try:
        B._gate_unavailable('A9 render-chain', 'planted: no Resources dir', 'stage them')
        hit = True
    except SystemExit as ex:
        hit = False
        print(f'    unexpected SystemExit: {ex}')
    print(f'  1 flag OFF -> WARN + continue: {"correct" if hit else "BUG (build died)"}')
    ok &= hit

    # --- 2. flag ON: the same condition must KILL the build ------------------------
    _set_flag('1')
    try:
        B._gate_unavailable('A9 render-chain', 'planted: no Resources dir', 'stage them')
        hit = False
        print('    no SystemExit raised')
    except SystemExit as ex:
        msg = str(ex)
        hit = 'A9 render-chain' in msg and 'SVC_REQUIRE_GATES' in msg
        if not hit:
            print(f'    SystemExit raised but message is unhelpful: {msg[:160]}')
    print(f'  2 flag ON  -> build FAILS loud: '
          f'{"correct" if hit else "BUG (a mis-pathed build would ship ungated)"}')
    ok &= hit

    # --- 3. the flag parser accepts the documented spellings and nothing else ------
    truthy = ['1', 'true', 'TRUE', 'Yes', 'on', ' 1 ']
    falsy = [None, '', '0', 'false', 'no', 'off', 'maybe', '2']
    bad = []
    for v in truthy:
        _set_flag(v)
        if not B._require_gates():
            bad.append(('should be ON', repr(v)))
    for v in falsy:
        _set_flag(v)
        if B._require_gates():
            bad.append(('should be OFF', repr(v)))
    hit = not bad
    print(f'  3 flag parsing ({len(truthy)} truthy / {len(falsy)} falsy): '
          f'{"correct" if hit else "BUG " + str(bad)}')
    ok &= hit

    # --- 4. the validator itself never PASSES on unusable inputs ------------------
    rc_missing = R.validate('(unused - inputs are checked first)',
                            r'C:/zzz_planted_missing_resources',
                            r'C:/zzz_planted_missing_game')
    hit = rc_missing == 2
    print(f'  4 validate_render_chain on missing dirs -> rc={rc_missing} '
          f'{"(correct: 2 = load error, never 0)" if hit else "(BUG: must not be 0/PASS)"}')
    ok &= hit

    _set_flag(None)
    print('  NEGTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
