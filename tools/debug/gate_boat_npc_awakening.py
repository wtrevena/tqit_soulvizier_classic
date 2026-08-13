"""gate_boat_npc_awakening.py - TRAVEL-INVARIANTS FAMILY (b88 WARDEN AWAKENING)

Asserts every SVC-generated boat-dialog trigger AWAKENS its NPC before offering travel:
`Action_ShowNpc` + `Action_UpdateNPCDialog("Dialog Needed")` must come FIRST, ahead of the
Action_BoatDialog(s). A boat NPC without that pair renders in the world and is UNCLICKABLE -
Will's bug, VERBATIM: "when I click on the guy who travels you to the spartan crypt (warden of
the spartan crypt) nothing happens, no dialog box comes up, nothing."

WHY THIS GATE EXISTS AND THE FIVE OLDER ONES WERE NOT ENOUGH. gate_traveler_responds' six
invariants (G-COLLISION / G-WARDEN / G-ORPHAN / G-DEST / G-SOLE-SOURCE / G-DIALOG-CHAIN) were
ALL GREEN on the build that shipped the mute Warden to Steam, twice: they check that a route
EXISTS, is UNIQUE in its level, has a real destination and lives in an in-window quest. None of
them looks at the ACTION SET, which is where the defect actually lives. b63 then "fixed" the bug
by moving the Warden's registration slot and every gate stayed green, because the slot was never
the problem.

THE REFERENCE SHAPE IS UPSTREAM-AUTHENTIC, NOT INVENTED. The Leinth exit vortex "Ioannes"
(records/drxmap/bloodcave/portals/vortexportal_exit.dbr, remote bossfight.lvl, teleports the
player out) ships [OpenDoor,] ShowNpc + UpdateNPCDialog + BoatDialog in the upstream SV XPack
bytes this repo ports byte-for-byte, and it is the ONE remote-level travel NPC in the mod known
to bind. build_svc_database._import_dialog_needed states the engine rationale: the "Dialog
Needed" DialogPak "makes NPCs clickable when assigned via Action_UpdateNPCDialog. Without it,
NPCs render but have no yellow icon and can't be clicked."

SCOPE. Every trigger the three SVC boat generators emit - _add_helos_traveler_hub_travel
(HELOS_HUB_TRAVEL, incl. the Warden), _add_testhub_portal_travel (TESTHUB_AREA_RETURN_NPCS) and
_add_traveler_enter_offers (TRAVELER_ENTER_OFFERS). The NPC roster is DERIVED from those tables
at run time, so adding a traveler without the awakening pair reds this gate instead of silently
shipping a mute NPC. The base-game/SVAERA-authored `portal_master_helos` trigger emitted by
_add_helos_portal_travel is deliberately OUT of scope: it is co-resident in the Helos plaza and
predates this rig; it is REPORTED, never faulted.

Read-only. Defaults to the deployed work/ Quests.arc; --quests gates a freshly-built one.

Usage:
  py tools/debug/gate_boat_npc_awakening.py
  py tools/debug/gate_boat_npc_awakening.py --quests local/Quests_run1.arc
  py tools/debug/gate_boat_npc_awakening.py --quests <arc> --arz <arz>   # + record resolution
  py tools/debug/gate_boat_npc_awakening.py --quests <arc> --negtest     # planted-defect suite
"""
import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive          # noqa: E402
import qst_format                           # noqa: E402
import build_quest_files as bqf             # noqa: E402

HOST_QUEST = 'sv_commonmechanics.qst'
AWAKEN = ('Action_ShowNpc', 'Action_UpdateNPCDialog')
DIALOG_NEEDED = r'records\dialog\story\dialog needed.dbr'
# displayTag prefixes of the three SVC generators (build_quest_files).
SVC_TRIGGER_PREFIXES = ('SVC: Helos Traveler Hub', 'SVC: TESTHUB Return NPC',
                        'SVC: Traveler Enter-Offer')
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


def expected_npcs():
    """The SVC boat-NPC roster, DERIVED from the build tables (never hand-listed)."""
    out = set()
    for npc, _xyz, _tag in bqf.HELOS_HUB_TRAVEL:
        out.add(norm(npc))
    for npc in bqf.TESTHUB_AREA_RETURN_NPCS:
        out.add(norm(npc))
    for npc, _xyz, _tag in bqf.TRAVELER_ENTER_OFFERS:
        out.add(norm(npc))
    return out


def collect(tree):
    """[(displayTag, cond, [(class, {field: value})...])] for every trigger with actions."""
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
    want_npcs = expected_npcs()
    seen_npcs = set()
    in_scope = out_scope = 0

    for disp, cond, acount, blocks, stepname in rows:
        classes = [c for c, _f in blocks]
        if 'Action_BoatDialog' not in classes:
            continue
        if disp and disp.startswith(OUT_OF_SCOPE_PREFIXES):
            out_scope += 1
            if verbose:
                print(f'  [SKIP ] {disp!r}: out of scope (SVAERA-authored, co-resident) '
                      f'-> {classes}')
            continue
        if not (disp and disp.startswith(SVC_TRIGGER_PREFIXES)):
            # an SVC boat trigger that lost its displayTag lineage is itself a finding
            viols.append(f'A0 {disp!r} (step {stepname!r}) carries Action_BoatDialog but '
                         f'matches no known generator prefix; the roster cannot be gated')
            continue
        in_scope += 1

        # A1 - the awakening pair leads
        if tuple(classes[:2]) != AWAKEN:
            viols.append(f'A1 {disp!r}: actions {classes} do not START with '
                         f'{list(AWAKEN)} - the NPC renders but cannot be clicked')
            continue
        if any(c not in ('Action_BoatDialog',) for c in classes[2:]):
            viols.append(f'A1 {disp!r}: actions after the awakening pair are {classes[2:]}, '
                         f'expected Action_BoatDialog only')

        # A2 - one NPC per trigger, shared by all three action classes
        npcs = {norm(f.get('npc')) for _c, f in blocks}
        if len(npcs) != 1 or None in npcs:
            viols.append(f'A2 {disp!r}: actions target {sorted(npcs)}; a boat trigger must '
                         f'awaken and offer travel on exactly ONE npc record')
            continue
        npc = next(iter(npcs))
        seen_npcs.add(npc)

        # A3 - the pak that makes an NPC clickable
        dlg = norm(blocks[1][1].get('dialogFile'))
        if dlg != DIALOG_NEEDED:
            viols.append(f'A3 {disp!r}: Action_UpdateNPCDialog.dialogFile is {dlg!r}, '
                         f'expected {DIALOG_NEEDED!r}')
        elif arz_names is not None and DIALOG_NEEDED not in arz_names:
            viols.append(f'A3 {disp!r}: the "Dialog Needed" DialogPak {DIALOG_NEEDED!r} is '
                         f'NOT in the shipped .arz; UpdateNPCDialog would resolve to nothing')

        # A4 - the count the engine reads must match the actions actually present
        if acount != len(classes):
            viols.append(f'A4 {disp!r}: actionCount {acount} != {len(classes)} emitted '
                         f'actions')

        # A5 - the NPC record itself must resolve
        if arz_names is not None and npc not in arz_names:
            viols.append(f'A5 {disp!r}: npc record {npc!r} is not in the shipped .arz')

        if verbose:
            print(f'  [OK   ] {disp!r}: {classes} npc={npc.rsplit(chr(92), 1)[-1]}')

    # A6 - roster coverage: every table NPC must actually appear
    missing = sorted(want_npcs - seen_npcs)
    if missing:
        viols.append(f'A6 {len(missing)} SVC boat NPC(s) from the build tables have NO '
                     f'awakened trigger in the shipped quest: '
                     f'{[m.rsplit(chr(92), 1)[-1] for m in missing]}')
    if verbose:
        print(f'\n  in-scope SVC boat triggers: {in_scope}   out-of-scope reported: '
              f'{out_scope}   distinct NPCs awakened: {len(seen_npcs)}/{len(want_npcs)}')
    return viols


# ── planted-defect suite ────────────────────────────────────────────────────
def _mutate(data, kind):
    """Return quest bytes with one defect planted (the shapes that shipped mute)."""
    tree = qst_format.parse(data)
    steps = tree[1]
    pos = _blocks(steps)
    for sd, tc, _sn in [pos[i:i + 3] for i in range(0, len(pos), 3)]:
        items = list(steps[tc][1])
        tp = _blocks(items)
        for (h, c, a) in [tp[i:i + 3] for i in range(0, len(tp), 3)]:
            disp = _fld(items[h][1], 'displayTag')
            if disp != 'SVC: Helos Traveler Hub 00':      # the Warden
                continue
            acts = list(items[a][1])
            if kind == 'strip_pair':                     # the b63 shipped state
                kept = [acts[0]]
                i = 1
                while i < len(acts):
                    if acts[i][0] == 'field' and acts[i][1] == 'actionClassName':
                        if acts[i][2][1] == 'Action_BoatDialog':
                            kept.extend([acts[i], acts[i + 1]])
                        i += 2
                        continue
                    i += 1
                kept[0] = ('field', 'actionCount', ('int', 1))
                acts = kept
            elif kind == 'wrong_pak':
                blk = list(acts[4][1])
                for j, x in enumerate(blk):
                    if x[1] == 'dialogFile':
                        blk[j] = ('field', 'dialogFile',
                                  ('str', r'Records\Dialog\Story\Nonexistent.dbr'))
                acts[4] = ('block', blk)
            elif kind == 'pair_after_boat':               # ordering regression
                acts = [acts[0], acts[5], acts[6], acts[1], acts[2], acts[3], acts[4]]
            elif kind == 'npc_mismatch':
                blk = list(acts[2][1])
                for j, x in enumerate(blk):
                    if x[1] == 'npc':
                        blk[j] = ('field', 'npc',
                                  ('str', r'records\quests\svc_helos_trav_garden.dbr'))
                acts[2] = ('block', blk)
            elif kind == 'bad_count':
                acts[0] = ('field', 'actionCount', ('int', 1))
            items[a] = ('block', acts)
            steps[tc] = ('block', items)
            return qst_format.serialize(tree)
    raise SystemExit('negtest: the Warden trigger was not found to mutate')


def negtest(data):
    print('\n=== PLANTED-DEFECT SUITE ===')
    ok = True
    base = check(data, verbose=False)
    if base:
        print(f'  [FAIL] positive control: the unmutated arc reds -> {base}')
        ok = False
    else:
        print('  [GREEN OK] positive control: the unmutated arc passes')
    for kind, why in [
            ('strip_pair', 'BoatDialog alone (the exact b63 shipped state)'),
            ('wrong_pak', 'UpdateNPCDialog points at a non-"Dialog Needed" pak'),
            ('pair_after_boat', 'awakening pair emitted AFTER the BoatDialog'),
            ('npc_mismatch', 'ShowNpc awakens a DIFFERENT npc than the offer'),
            ('bad_count', 'actionCount understates the emitted actions')]:
        v = check(_mutate(data, kind), verbose=False)
        if v:
            print(f'  [RED   OK] {kind}: {why} -> {len(v)} violation(s): {v[0][:96]}')
        else:
            print(f'  [FAIL] {kind}: {why} -> NOT CAUGHT')
            ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quests', default=r'work\SoulvizierClassic\Resources\Quests.arc')
    ap.add_argument('--arz', default=None)
    ap.add_argument('--negtest', action='store_true')
    args = ap.parse_args()

    print('gate_boat_npc_awakening - every SVC boat NPC is AWAKENED before it is offered')
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
        print(f'GATE FAIL: {len(viols)} violation(s) - a boat NPC would render but not be '
              f'clickable:')
        for v in viols:
            print(f'  - {v}')
        return 1
    if not neg_ok:
        print('GATE FAIL: the planted-defect suite did not behave (the gate is inert)')
        return 1
    print('GATE PASS: every SVC boat-dialog trigger leads with Action_ShowNpc + '
          'Action_UpdateNPCDialog("Dialog Needed") on its own NPC, so no traveler can ship '
          'rendered-but-mute.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
