#!/usr/bin/env python3
"""NEGTEST b63 SILENT-WARDEN - prove the new build-time laws actually BITE.

Will (2026-08-10): "when I click on the guy who travels you to the spartan crypt (warden of the
spartan crypt) nothing happens, no dialog box comes up, nothing." The Warden shipped mute to
Steam on 2026-08-06 while EVERY existing gate was green, so the b63 wave added guards. A guard
that has never been shown to fail is not evidence of anything - this file plants each defect and
asserts the guard goes RED.

Covers the guards that live OUTSIDE gate_traveler_responds (which has its own --negtest):
  N1 build_quest_files._assert_enter_offers_are_second_entries
       -> an enter-offer whose NPC owns no HELOS_HUB_TRAVEL route must raise (the shipped bug).
  N2 build_quest_files._HUB_PLUS_ENTER_TRIGGERS
       -> the count-conservation constant matches the live tables (moving a row between the two
          tables must not add or drop a trigger).
  N3 gate_travel_npc_invariants T5c "DESCEND ONLY" (R-170 AMENDMENT, Will 2026-08-06)
       -> giving the Warden a second route, or the shared "Helos (Return)" port, must FAIL.
  N4 gate_travel_npc_invariants T5c sole-source law
       -> an enter-offer that is an NPC's only route must FAIL.
  N5 gate_landing_clearance.check_boat_npc_landing_separation
       -> a boat NPC sitting ON a boat landing must FAIL, with NO per-record exemption; and a
          confirmed-working separation must PASS (guards against a false-positive threshold).

Read-only, build-free, no .arc needed. Exit 0 = every planted defect was caught.
Usage: py tools/debug/negtest_warden_dialog.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

import build_quest_files as bqf          # noqa: E402
import apply_svc_patches as asp          # noqa: E402

RESULTS = []


def check(label, ok, detail=''):
    RESULTS.append((label, ok, detail))
    print(f'  [{"RED  OK" if ok else "GREEN  MISS"}] {label}' + (f'  {detail}' if detail else ''))


def n1_sole_source_assert():
    """Plant the EXACT shipped bug: an enter-offer NPC with no HELOS_HUB_TRAVEL route."""
    saved = list(bqf.TRAVELER_ENTER_OFFERS)
    try:
        bqf.TRAVELER_ENTER_OFFERS[:] = saved + [
            (r'records\quests\svc_warden_sparta_crypt.dbr', (-5596, -2, -1410),
             'tagSVCEnterSpartaCrypt')]
        # simulate the pre-b63 world: the Warden owns no hub row
        hub_saved = list(bqf.HELOS_HUB_TRAVEL)
        bqf.HELOS_HUB_TRAVEL[:] = [r for r in hub_saved
                                   if 'svc_warden_sparta' not in r[0].lower()]
        try:
            bqf._assert_enter_offers_are_second_entries()
            check('N1 sole-sourced enter-offer (THE shipped bug) raises', False,
                  'assertion did NOT fire')
        except ValueError as e:
            check('N1 sole-sourced enter-offer (THE shipped bug) raises', True,
                  f'-> {str(e)[:70]}...')
        finally:
            bqf.HELOS_HUB_TRAVEL[:] = hub_saved
    finally:
        bqf.TRAVELER_ENTER_OFFERS[:] = saved
    # positive control: the real tables must PASS
    try:
        bqf._assert_enter_offers_are_second_entries()
        check('N1 positive control: live tables pass the sole-source law', True)
    except ValueError as e:
        check('N1 positive control: live tables pass the sole-source law', False, str(e))


def n2_count_conservation():
    total = len(bqf.HELOS_HUB_TRAVEL) + len(bqf.TRAVELER_ENTER_OFFERS)
    ok = total == bqf._HUB_PLUS_ENTER_TRIGGERS
    check('N2 count conservation constant matches live tables', ok,
          f'hub={len(bqf.HELOS_HUB_TRAVEL)} + enter={len(bqf.TRAVELER_ENTER_OFFERS)} '
          f'= {total} (want {bqf._HUB_PLUS_ENTER_TRIGGERS})')


def _run_invariants():
    """Run the spec battery in-process and return its fail list."""
    import importlib
    import gate_travel_npc_invariants as g
    importlib.reload(g)
    fails = []
    g.check_specs(fails)
    return fails


def n3_descend_only():
    """R-170 AMENDMENT: the Warden's menu is DESCEND ONLY."""
    warden = r'records\quests\svc_warden_sparta_crypt.dbr'
    saved = list(bqf.HELOS_HUB_TRAVEL)

    # (a) a SECOND route on the Warden
    try:
        bqf.HELOS_HUB_TRAVEL[:] = saved + [(warden, (-5980, 1, 909), 'tagSVCAreaReturnToHelos')]
        fails = _run_invariants()
        hit = any('DESCEND ONLY' in f or 'EXACTLY ONE boat route' in f
                  or 'Helos (Return)' in f for f in fails)
        check('N3a Warden given a 2nd route -> T5c FAIL', hit,
              f'({len(fails)} fail(s))')
    finally:
        bqf.HELOS_HUB_TRAVEL[:] = saved

    # (b) the Warden's single route relabelled to the shared Helos-return port
    try:
        bqf.HELOS_HUB_TRAVEL[:] = [
            (n, x, ('tagSVCAreaReturnToHelos' if 'svc_warden_sparta' in n.lower() else t))
            for (n, x, t) in saved]
        fails = _run_invariants()
        hit = any('Descend into the Sparta Crypt' in f or 'DESCEND ONLY' in f for f in fails)
        check('N3b Warden route relabelled to "Helos (Return)" -> T5c FAIL', hit,
              f'({len(fails)} fail(s))')
    finally:
        bqf.HELOS_HUB_TRAVEL[:] = saved


def n4_invariants_sole_source():
    """T5c's own copy of the sole-source law (independent of the import-time assert)."""
    saved_enter = list(bqf.TRAVELER_ENTER_OFFERS)
    saved_hub = list(bqf.HELOS_HUB_TRAVEL)
    try:
        bqf.TRAVELER_ENTER_OFFERS[:] = saved_enter + [
            (r'records\quests\svc_area_return_dorus.dbr', (1, 2, 3), 'tagSVCEnterSpartaCrypt')]
        bqf.HELOS_HUB_TRAVEL[:] = [r for r in saved_hub
                                   if 'svc_area_return_dorus' not in r[0].lower()]
        fails = _run_invariants()
        hit = any('sole route' in f or 'owns NO HELOS_HUB_TRAVEL route' in f for f in fails)
        check('N4 enter-offer as an NPC\'s only route -> T5c FAIL', hit, f'({len(fails)} fail(s))')
    finally:
        bqf.TRAVELER_ENTER_OFFERS[:] = saved_enter
        bqf.HELOS_HUB_TRAVEL[:] = saved_hub


def n5_landing_separation():
    """G-NPC-LANDING-SEP: exemption-free, and calibrated so proven-working spacing stays green."""
    import gate_landing_clearance as glc

    def fake_result(name, tag, dist, dbr):
        # near = [(dist, dbr, x, z, klass, is_extra)]
        return dict(name=name, tag=tag, world=(0, 0, 0), local=(0.0, 0.0),
                    near=[(dist, dbr, 0.0, 0.0, 'npc', False)])

    # (a) the shipped defect: a boat NPC exactly on a boat landing
    v, _m, _n = glc.check_boat_npc_landing_separation(
        [fake_result('sparta', 'tagSVCHelosToSparta', 0.00,
                     r'records\quests\svc_warden_sparta_crypt.dbr')])
    check('N5a boat NPC 0.00u from a landing -> FAIL', len(v) == 1,
          f'{len(v)} violation(s)')

    # (b) no per-record exemption: a DIFFERENT boat record at 0.00u must fail identically
    v, _m, _n = glc.check_boat_npc_landing_separation(
        [fake_result('uber', 'tagSVCEnterUberDungeon', 0.00,
                     r'records\quests\svc_area_return_uber.dbr')])
    check('N5b no per-record exemption (different record, same 0.00u) -> FAIL', len(v) == 1,
          f'{len(v)} violation(s)')

    # (c) FALSE-POSITIVE guard: the tightest CONFIRMED-WORKING separation must stay GREEN.
    # Measured on the deployed DEV map: svc_helos_trav_secret is 1.12u from the Helos plaza
    # return landing, where all 10 area returns drop the player and every traveler responds.
    v, _m, _n = glc.check_boat_npc_landing_separation(
        [fake_result('ret_dorus', 'tagSVCAreaReturnToHelos', 1.12,
                     r'records\quests\svc_helos_trav_secret.dbr')])
    check('N5c proven-working 1.12u Helos-plaza spacing stays PASS', len(v) == 0,
          f'{len(v)} violation(s) (want 0)')

    # (d) a non-boat record at 0.00u is NOT this gate's business (the pin check owns that)
    v, _m, _n = glc.check_boat_npc_landing_separation(
        [fake_result('x', 'tagX', 0.00, r'records\underground\greece\some_urn01.dbr')])
    check('N5d non-boat record is out of scope for this check', len(v) == 0,
          f'{len(v)} violation(s) (want 0)')


def main():
    print('=' * 96)
    print('negtest_warden_dialog (b63 SILENT-WARDEN) - planted-defect battery')
    print('=' * 96)
    n1_sole_source_assert()
    n2_count_conservation()
    n3_descend_only()
    n4_invariants_sole_source()
    n5_landing_separation()
    bad = [lbl for lbl, ok, _d in RESULTS if not ok]
    print('=' * 96)
    if bad:
        print(f'NEGTEST FAIL: {len(bad)} guard(s) did not bite:')
        for lbl in bad:
            print(f'  - {lbl}')
        return 1
    print(f'NEGTEST PASS: all {len(RESULTS)} checks behaved (every planted defect caught; '
          f'positive controls + the false-positive guard stayed green).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
