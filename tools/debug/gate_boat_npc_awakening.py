"""gate_boat_npc_awakening.py - TRAVEL-INVARIANTS FAMILY (b88 -> R-246 rewrite)

POST-RIP CONTRACT (R-246 native-device travel, 2026-08-13). The three SVC boat generators
this gate originally covered (_add_helos_traveler_hub_travel / _add_testhub_portal_travel /
_add_traveler_enter_offers) are RIPPED - their 35 armed rows were the stateful boat-registry
corruption source (docs/WILL_RULINGS.md R-246). This gate now asserts, on the FINAL built
sv_commonmechanics.qst bytes:

  R0 - THE RIP HOLDS: zero triggers whose displayTag carries a ripped-generator prefix
       ('SVC: Helos Traveler Hub' / 'SVC: TESTHUB Return NPC' / 'SVC: Traveler Enter-Offer').
       Any such trigger is the ripped bug class returning and fails loud.
  A1-A5 - ANY OTHER SVC boat trigger that appears in this quest (a future addition) must be
       a co-resident whitelisted one (Almyros 'SVC: Helos Portal-Master', reported not
       faulted) OR lead with the upstream-authentic awakening pair Action_ShowNpc +
       Action_UpdateNPCDialog("Dialog Needed") on its own single NPC - the b88 law that a
       remote boat NPC without the pair renders unclickable (Will's mute-Warden bug, twice).

The awakening RECIPE stays in build_quest_files._npc_awaken_actions (retained, uncalled) as
the R-246 visibility fallback shape.

Read-only. Defaults to the deployed work/ Quests.arc; --quests gates a freshly-built one.

Usage:
  py tools/debug/gate_boat_npc_awakening.py --quests <arc> [--arz <arz>] [--negtest]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive          # noqa: E402
import qst_format                           # noqa: E402

HOST_QUEST = 'sv_commonmechanics.qst'
AWAKEN = ('Action_ShowNpc', 'Action_UpdateNPCDialog')
DIALOG_NEEDED = r'records\dialog\story\dialog needed.dbr'
# R-246: displayTag prefixes of the RIPPED generators - presence == violation.
RIPPED_PREFIXES = ('SVC: Helos Traveler Hub', 'SVC: TESTHUB Return NPC',
                   'SVC: Traveler Enter-Offer')
# Co-resident, Will-ratified talk menu (R-246: "Almyros keeps his ... talk menu"; R-249
# 2026-08-14 trimmed it to Garden ONLY - Secret + Uber removed from the Steam build).
OUT_OF_SCOPE_PREFIXES = ('SVC: Helos Portal-Master',)


def norm(s):
    return s.replace('/', '\\').lower() if isinstance(s, str) else s


def _blocks(items):
    return [i for i, it in enumerate(items) if it[0] == 'block']


def _fld(items, key):
    for it in items:
        if it[0] == 'field' and it[1] == key:
            return it[2][1]
    return None


def _quest_bytes(arc, basename):
    bl = basename.lower()
    for e in arc.entries:
        if e.entry_type == 3 and (e.name.lower() == bl
                                  or e.name.lower().endswith('\\' + bl)
                                  or e.name.lower().endswith('/' + bl)):
            return arc.decompress(e)
    raise SystemExit(f'gate_boat_npc_awakening: {basename} not in the archive')


def collect(tree):
    """[(displayTag, cond, actionCount, [(class, {field: value})...], stepname)]."""
    steps = tree[1]
    pos = _blocks(steps)
    rows = []
    for sd, tc, _sn in [pos[i:i + 3] for i in range(0, len(pos), 3)]:
        items = steps[tc][1]
        tp = _blocks(items)
        for (h, c, a) in [tp[i:i + 3] for i in range(0, len(tp), 3)]:
            acts = list(items[a][1])
            blocks = []
            i = 0
            while i < len(acts):
                it = acts[i]
                if it[0] == 'field' and it[1] == 'actionClassName':
                    blk = acts[i + 1]
                    blocks.append((it[2][1],
                                   {x[1]: x[2][1] for x in blk[1] if x[0] == 'field'}))
                    i += 2
                    continue
                i += 1
            if not blocks:
                continue
            rows.append((_fld(items[h][1], 'displayTag'),
                         _fld(items[c][1], 'conditionClassName'),
                         _fld(acts, 'actionCount'), blocks,
                         _fld(steps[sd][1], 'name')))
    return rows


def check(data, arz_names=None, verbose=True):
    """Return a list of violation strings (empty == PASS)."""
    viols = []
    rows = collect(qst_format.parse(data))
    in_scope = out_scope = 0

    for disp, cond, acount, blocks, stepname in rows:
        classes = [c for c, _f in blocks]
        # R0 - the rip holds regardless of action classes
        if disp and disp.startswith(RIPPED_PREFIXES):
            viols.append(f'R0 {disp!r} (step {stepname!r}): a RIPPED-generator trigger is '
                         f'back in the built quest - the R-246 boat-row bug class returning')
            continue
        if 'Action_BoatDialog' not in classes:
            continue
        if disp and disp.startswith(OUT_OF_SCOPE_PREFIXES):
            out_scope += 1
            if verbose:
                print(f'  [SKIP ] {disp!r}: co-resident ruled menu (Almyros) -> {classes}')
            continue
        if not (disp and disp.startswith('SVC:')):
            continue  # upstream-authentic trigger, frozen by gate_boatdialog_budget
        in_scope += 1

        # A1 - the awakening pair leads
        if tuple(classes[:2]) != AWAKEN:
            viols.append(f'A1 {disp!r}: actions {classes} do not START with '
                         f'{list(AWAKEN)} - the NPC renders but cannot be clicked')
            continue
        if any(c not in ('Action_BoatDialog',) for c in classes[2:]):
            viols.append(f'A1 {disp!r}: actions after the awakening pair are {classes[2:]}, '
                         f'expected Action_BoatDialog only')

        # A2 - one NPC per trigger, shared by all action classes
        npcs = {norm(f.get('npc')) for _c, f in blocks}
        if len(npcs) != 1 or None in npcs:
            viols.append(f'A2 {disp!r}: actions target {sorted(npcs)}; a boat trigger must '
                         f'awaken and offer travel on exactly ONE npc record')
            continue
        npc = next(iter(npcs))

        # A3 - the pak that makes an NPC clickable
        dlg = norm(blocks[1][1].get('dialogFile'))
        if dlg != DIALOG_NEEDED:
            viols.append(f'A3 {disp!r}: Action_UpdateNPCDialog.dialogFile is {dlg!r}, '
                         f'expected {DIALOG_NEEDED!r}')
        elif arz_names is not None and DIALOG_NEEDED not in arz_names:
            viols.append(f'A3 {disp!r}: the "Dialog Needed" DialogPak is NOT in the shipped '
                         f'.arz; UpdateNPCDialog would resolve to nothing')

        # A4 - the count the engine reads must match the actions actually present
        if acount != len(classes):
            viols.append(f'A4 {disp!r}: actionCount {acount} != {len(classes)} emitted '
                         f'actions')

        # A5 - the NPC record itself must resolve
        if arz_names is not None and npc not in arz_names:
            viols.append(f'A5 {disp!r}: npc record {npc!r} is not in the shipped .arz')

        if verbose:
            print(f'  [OK   ] {disp!r}: {classes} npc={npc.rsplit(chr(92), 1)[-1]}')

    if verbose:
        print(f'\n  R-246 post-rip: ripped-prefix triggers found: 0 (R0 clean)   '
              f'new in-scope SVC boat triggers: {in_scope}   co-resident reported: {out_scope}')
    return viols


# ── planted-defect suite ────────────────────────────────────────────────────
def _plant_trigger(data, display, npc, with_pair):
    """Append a boat trigger (optionally without the awakening pair) to the refire step."""
    import build_quest_files as bqf
    tree = qst_format.parse(data)
    steps = tree[1]
    pos = _blocks(steps)
    for sd, tc, _sn in [pos[i:i + 3] for i in range(0, len(pos), 3)]:
        if _fld(steps[sd][1], 'name') != bqf.HELOS_PORTAL_HOST_STEP:
            continue
        items = list(steps[tc][1])
        for j, it in enumerate(items):
            if it[0] == 'field' and it[1] == 'max':
                items[j] = ('field', 'max', ('int', it[2][1] + 1))
                break
        header = ('block', [
            ('field', 'displayTag', ('str', display)),
            ('field', 'displayBitmap', ('int_or_empty', 0)),
            ('field', 'comments', ('int_or_empty', 0)),
            ('field', 'isActive', ('int', 0)),
        ])
        conditions = ('block', [
            ('field', 'conditionCount', ('int', 1)),
            ('field', 'conditionClassName', ('str', 'Condition_OnLevelLoad')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'isNot', ('int', 0)),
                ('field', 'isResettable', ('int', 1)),
                ('field', 'isQuestCritical', ('int', 1)),
            ]),
        ])
        boat = [
            ('field', 'actionClassName', ('str', 'Action_BoatDialog')),
            ('block', [
                ('field', 'comments', ('int_or_empty', 0)),
                ('field', 'delayTime', ('int', 0)),
                ('field', 'npc', ('str', npc)),
                ('field', 'onOff', ('int', 1)),
                ('field', 'x', ('int', 1)),
                ('field', 'y', ('int', 2)),
                ('field', 'z', ('int', 3)),
                ('field', 'tag', ('str', 'tagPlanted')),
            ]),
        ]
        pre = bqf._npc_awaken_actions(npc) if with_pair else []
        n_actions = (2 if with_pair else 0) + 1
        actions = ('block', [('field', 'actionCount', ('int', n_actions))] + pre + boat)
        items.extend([header, conditions, actions])
        steps[tc] = ('block', items)
        return qst_format.serialize(tree)
    raise SystemExit('negtest: refire step not found to mutate')


def negtest(data):
    print('\n=== PLANTED-DEFECT SUITE (R-246) ===')
    ok = True
    base = check(data, verbose=False)
    if base:
        print(f'  [FAIL] positive control: the unmutated arc reds -> {base}')
        ok = False
    else:
        print('  [GREEN OK] positive control: the unmutated arc passes')
    cases = [
        ('SVC: Helos Traveler Hub 00', r'records\quests\svc_warden_sparta_crypt.dbr',
         True, True, 'a resurrected RIPPED hub trigger (R0)'),
        ('SVC: TESTHUB Return NPC (planted)', r'records\quests\svc_testhub_return_uber.dbr',
         True, True, 'a resurrected RIPPED testhub trigger (R0)'),
        ('SVC: Planted Remote Traveler', r'records\quests\svc_area_return_dorus.dbr',
         False, True, 'a NEW remote SVC boat trigger WITHOUT the awakening pair (A1)'),
        ('SVC: Planted Remote Traveler OK', r'records\quests\svc_area_return_dorus.dbr',
         True, False, 'a NEW remote SVC boat trigger WITH the pair (must stay green here)'),
    ]
    for display, npc, with_pair, want_red, why in cases:
        v = check(_plant_trigger(data, display, npc, with_pair), verbose=False)
        red = bool(v)
        if red == want_red:
            state = 'RED   OK' if want_red else 'GREEN OK'
            print(f'  [{state}] {why}' + (f' -> {v[0][:90]}' if v else ''))
        else:
            print(f'  [FAIL] {why} -> {"not caught" if want_red else v}')
            ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quests', default=r'work\SoulvizierClassic\Resources\Quests.arc')
    ap.add_argument('--arz', default=None)
    ap.add_argument('--negtest', action='store_true')
    args = ap.parse_args()

    print('gate_boat_npc_awakening (R-246): the boat-row rip holds + any future SVC boat '
          'trigger is awakened')
    print(f'  quests: {args.quests}')
    arc = ArcArchive.from_file(Path(args.quests))
    data = _quest_bytes(arc, HOST_QUEST)

    arz_names = None
    if args.arz:
        from arz_patcher import ArzDatabase
        db = ArzDatabase.from_arz(Path(args.arz))
        arz_names = {n.lower() for n in db.record_names()}
        print(f'  arz   : {args.arz} ({len(arz_names)} records)')
    print('=' * 96)

    viols = check(data, arz_names)
    neg_ok = negtest(data) if args.negtest else True

    print('=' * 96)
    if viols:
        print(f'GATE FAIL: {len(viols)} violation(s):')
        for v in viols:
            print(f'  - {v}')
        return 1
    if not neg_ok:
        print('GATE FAIL: the planted-defect suite did not behave (the gate is inert)')
        return 1
    print('GATE PASS: the R-246 rip holds (zero ripped-generator triggers) and every '
          'other SVC boat trigger is either the ruled Almyros menu or properly awakened.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
