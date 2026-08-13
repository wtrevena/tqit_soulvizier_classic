#!/usr/bin/env python3
"""GATE - MAX_ARMED_BOATDIALOG BUDGET (R-246 native-device travel, 2026-08-13).

THE BUG CLASS THIS GATE KILLS (hunt wf device-travel, h2/h3/h4 artifacts): the
sv_commonmechanics refire step armed 39 Action_BoatDialog rows on ONE blanket
Condition_OnLevelLoad step re-fired on EVERY level load; 15 rows shared one
tag+dest and 17 NPCs were remote. The engine's boat-offer registry is STATEFUL:
under that arming pattern clicks execute OTHER rows (label included - Will:
"labels were wrong too") and cross-bound NPCs go fully mute (the Warden). The
base-game census envelope is: max 2 BoatDialog rows armed per step EVER, zero
tag reuse, zero dest reuse, one-shot arming. R-246 rips the row tables and
moves travel to engine-native devices; this gate FREEZES the surviving roster.

CHECKS (on a BUILT Quests.arc):
  (a) BUDGET   - per (quest, step): armed BoatDialog rows <= PER_STEP_BUDGET (2)
                 EXCEPT the named Almyros trigger on the sv_commonmechanics
                 refire step, allowed exactly ALMYROS_ALLOWED (3, Will-ratified
                 R-246: "Almyros keeps his 3-route talk menu"). SV-native steps
                 already >2 are RECORDED AS PRECEDENT (printed), never touched:
                 they ship in the upstream bytes this repo ports verbatim.
  (b) ROSTER   - the global armed row set == the explicit BY-NAME whitelist
                 below (quest, npc, tag, dest per row). ANY new row fails loud.
  (c) NO REUSE - zero tag reuse and zero dest-coord reuse across SVC-AUTHORED
                 rows (the corruption precondition).
  (d) PLACED   - every SVC-authored BoatDialog npc record is placed >=1x in the
                 canonical map (armed-but-unplaced rows never reach Steam).

Usage:
  py tools/gate_boatdialog_budget.py --quests <Quests.arc> [--map <Levels.arc>]
  py tools/gate_boatdialog_budget.py --quests <arc> --census   # report only
  py tools/gate_boatdialog_budget.py --quests <arc> --negtest  # planted defects
Exit 0 = PASS. Read-only.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_patcher import ArcArchive     # noqa: E402
import qst_format                      # noqa: E402

BS = chr(92)

# ── The Will-ratified budget (R-246) ────────────────────────────────────────────
PER_STEP_BUDGET = 2          # base-game census envelope: max armed rows per step
ALMYROS_ALLOWED = 3          # R-246: "Almyros keeps his 3-route talk menu"
ALMYROS_QUEST = 'sv_commonmechanics.qst'
ALMYROS_STEP = ('Makes it so Quest Never Completes -- '
                'Allows for refiring on triggers')
ALMYROS_NPC = r'records\quests\portal_master_helos.dbr'

# SVC-authored boat NPCs (checks (c)+(d) scope). Everything else in the arc is
# upstream-authentic (SV-native / base) and is frozen by the roster whitelist
# alone.
SVC_AUTHORED_NPCS = {
    r'records\quests\portal_master_helos.dbr',    # Almyros (Will's talk menu)
    r'records\quests\portal_master_olympus.dbr',  # Olympus->Rhodes herald
}

# ── (b) THE GLOBAL ARMED ROSTER, BY NAME ────────────────────────────────────────
# One entry per armed Action_BoatDialog row that may exist in the built arc:
#   (quest_lc, npc_lc, tag, (x, y, z))
# Derived from the post-R-246-rip census (this file's --census on the built arc)
# and cross-checked against the pre-rip census: the ONLY SVC-authored survivors
# are Almyros's 3 rows + the herald's 1; the other 12 are upstream-authentic
# (urder 3, Leinth vortex 5, base knossos 2 + greece-to-egypt 2). If corruption
# ever recurs on Steam, the residual suspect list is IN THIS ORDER: vortex 5
# (shared-step), urder 3 (see docs/BACKLOG.md R-246 lane record).
def _r(quest, npc, tag, xyz):
    return (quest.lower(), npc.replace('/', BS).lower(), tag, xyz)


ROSTER = [
    # SVC-authored: Almyros the Wayfarer, the ONE ruled talk menu (R-246).
    _r('sv_commonmechanics.qst', ALMYROS_NPC, 'tagSVCHelosToGarden', (1173, -39, -4001)),
    _r('sv_commonmechanics.qst', ALMYROS_NPC, 'tagSVCHelosToSecret', (-2396, 2, -5790)),
    _r('sv_commonmechanics.qst', ALMYROS_NPC, 'tagSVCHelosToUber', (-2438, 10, -2457)),
    # SVC-authored: the Olympus->Rhodes herald (base-exemplar-mirroring, 1 row).
    _r('quest that controls bosses and their doors.qst',
       r'records\quests\portal_master_olympus.dbr', 'tagSVCOlympusRhodesTravel', (700, 41, -6466)),
    # SV-native: urder's 3 portal-dudes (urder.qst step 'PortalDude Control';
    # upstream-authentic bytes, one row per distinct NPC record).
    _r('urder.qst', r'records\drxmap\xurder\portaldudes\portal to act 1.dbr',
       'tagSecretForestPortal', (-2317, 0, -5765)),
    _r('urder.qst', r'records\drxmap\xurder\portaldudes\portal to hallway.dbr',
       'tagRogueEncampmentTravel', (-3103, 0, -5457)),
    _r('urder.qst', r'records\drxmap\xurder\portaldudes\warriv.dbr',
       'tagJoLandTravel', (-3419, 2, -5443)),
    # SV-native: the Leinth exit vortex "Ioannes" - FIVE identical rows on ONE
    # step ('Boss Room Crystal Gate'), same npc+tag+dest. This is the recorded
    # SV-NATIVE >2-per-step + tag/dest-reuse PRECEDENT (upstream-authentic; the
    # #1 suspect if registry corruption ever recurs post-rip).
    *([_r('open_bloodcave_portal.qst',
          r'records\drxmap\bloodcave\portals\vortexportal_exit.dbr',
          'tagReturnFromLeinthBattle', (-90, -103, 2321))] * 5),
    # Base-game: quest 7 (Athens<->Knossos boatmen, 2 rows).
    _r('quest 7 - knossos.qst',
       r'Records\Creature\NPC\Speaking\Greece\Athens_BoatmanToKnossos.dbr',
       'tagAthensBoatToKnossos', (-9136, -125, -1822)),
    _r('quest 7 - knossos.qst',
       r'Records\Creature\NPC\Speaking\Greece\Knossos_BoatmanBackToAthens.dbr',
       'tagKnossosBoatToAthens', (-7116, 0, -1802)),
    # Base-game: quest 8 part i (Knossos<->Rhakotis boatmen, 2 rows).
    _r('quest 8 part i - greece to egypt.qst',
       r'Records\Creature\NPC\Speaking\Greece\Knossos_BoatmanToEgypt.dbr',
       'tagKnossosBoatToRhakotis', (-1966, 13, 4423)),
    _r('quest 8 part i - greece to egypt.qst',
       r'Records\Creature\NPC\Speaking\Egypt\Rhakotis_BoatmanBackToKnossos.dbr',
       'tagRhakotisBoatToKnossos', (-9976, 1, -1673)),
]


def _s32(v):
    return v - 0x100000000 if v >= 0x80000000 else v


def field_val(items, key):
    for it in items:
        if isinstance(it, tuple) and it[0] == 'field' and it[1] == key:
            return it[2][1]
    return None


def iter_boat_rows(qst_bytes):
    """Yield (step_name, trigger_display, npc, tag, (x,y,z)) for every
    Action_BoatDialog row in the quest."""
    tree = qst_format.parse(qst_bytes)
    steps_container = tree[1]
    positions = [i for i, it in enumerate(steps_container) if it[0] == 'block']
    step_triples = [positions[i:i + 3] for i in range(0, len(positions), 3)]
    for stepdef_pos, trigcont_pos, _sent in step_triples:
        stepdef = steps_container[stepdef_pos][1]
        step_name = field_val(stepdef, 'name')
        trigcont = steps_container[trigcont_pos][1]
        blocks = [it for it in trigcont if isinstance(it, tuple) and it[0] == 'block']
        # triggers come in triples [header, conditions, actions]
        for t in range(0, len(blocks) - 2, 3):
            header, _conds, actions = blocks[t], blocks[t + 1], blocks[t + 2]
            display = field_val(header[1], 'displayTag')
            items = actions[1]
            i = 0
            while i < len(items):
                it = items[i]
                if (isinstance(it, tuple) and it[0] == 'field'
                        and it[1] == 'actionClassName' and it[2][1] == 'Action_BoatDialog'):
                    body = items[i + 1][1] if (i + 1 < len(items)
                                               and isinstance(items[i + 1], tuple)
                                               and items[i + 1][0] == 'block') else []
                    npc = field_val(body, 'npc') or ''
                    tag = field_val(body, 'tag') or ''
                    x = _s32(field_val(body, 'x') or 0)
                    y = _s32(field_val(body, 'y') or 0)
                    z = _s32(field_val(body, 'z') or 0)
                    yield (step_name, display, npc, tag, (x, y, z))
                i += 1


def census(arc_path, verbose=True):
    """Return list of (quest_name, step, display, npc, tag, dest) rows."""
    arc = ArcArchive.from_file(Path(arc_path))
    rows = []
    for e in arc.entries:
        if e.entry_type != 3 or not e.name.lower().endswith('.qst'):
            continue
        data = arc.get_file(e.name)
        if data is None or b'Action_BoatDialog' not in data:
            continue
        try:
            for (step, disp, npc, tag, dest) in iter_boat_rows(data):
                rows.append((e.name, step, disp, npc, tag, dest))
        except Exception as ex:  # parse failure = gate failure, never silence
            raise SystemExit(f'BUDGET GATE: {e.name} failed to parse: {ex}')
    if verbose:
        from collections import Counter
        per_step = Counter((q, s) for q, s, _d, _n, _t, _xyz in rows)
        print(f'--- BoatDialog census: {len(rows)} armed rows in {arc_path} ---')
        for (q, s), n in sorted(per_step.items()):
            print(f'  {n:3d} rows  {q}  step={s!r}')
        for q, s, d, n, t, xyz in rows:
            print(f'    {q} | {d} | {n.split(BS)[-1]} | {t} | {xyz}')
    return rows


def scan_map_placed(map_path, npc_paths):
    """Return {npc_lc: instance_count} across every level 0x05 in the map."""
    from merge_levels_binary import parse_sections
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'contracts'))
    from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS
    arc = ArcArchive.from_file(Path(map_path))
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    secs = {s['type']: s for s in parse_sections(data)}
    lsec = secs[SEC_LEVELS]
    levels = parse_level_index(data[lsec['data_offset']:lsec['data_offset'] + lsec['size']])
    want = {p.replace('/', BS).lower() for p in npc_paths}
    counts = {p: 0 for p in want}
    basenames = [p.split(BS)[-1].encode() for p in want]
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if not any(b in blob for b in basenames):
            continue
        for t, d in parse_blob_sections(blob):
            if t != 0x05:
                continue
            pos = 0
            nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
            strings = []
            for _ in range(nstr):
                ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
                strings.append(d[pos:pos + ln]); pos += ln
            ninst = struct.unpack_from('<I', d, pos)[0]; pos += 4
            base = 72 if blob[3] in (0x11, 0x0f) else 56
            for _ in range(ninst):
                sid = struct.unpack_from('<I', d, pos)[0]
                flags = struct.unpack_from('<I', d, pos + 52)[0]
                s = (strings[sid] if sid < len(strings) else b'').replace(b'/', BS.encode()).lower()
                s = s.decode('ascii', 'replace')
                if s in counts:
                    counts[s] += 1
                pos += base + (16 if flags != 0 else 0)
    return counts


def run_gate(quests_arc, map_arc=None, verbose=True):
    rows = census(quests_arc, verbose=verbose)
    violations = []

    # (a) BUDGET per (quest, step)
    from collections import Counter, defaultdict
    per_step = defaultdict(list)
    for q, s, d, n, t, xyz in rows:
        per_step[(q.lower(), s)].append((d, n, t, xyz))
    for (q, s), rr in sorted(per_step.items()):
        is_almyros_step = q.endswith(ALMYROS_QUEST) and s == ALMYROS_STEP
        svc_rows = [r for r in rr if r[1].replace('/', BS).lower() in
                    {p.lower() for p in SVC_AUTHORED_NPCS}]
        native_rows = [r for r in rr if r not in svc_rows]
        if is_almyros_step:
            alm = [r for r in svc_rows if r[1].replace('/', BS).lower() == ALMYROS_NPC.lower()]
            other_svc = [r for r in svc_rows if r not in alm]
            if len(alm) != ALMYROS_ALLOWED:
                violations.append(
                    f'(a) refire step arms {len(alm)} Almyros rows, must be exactly '
                    f'{ALMYROS_ALLOWED} (R-246 ruled menu)')
            if other_svc:
                violations.append(
                    f'(a) refire step arms {len(other_svc)} NON-Almyros SVC rows '
                    f'({[r[2] for r in other_svc]}) - the ripped bug class returning')
        else:
            if len(svc_rows) > PER_STEP_BUDGET:
                violations.append(
                    f'(a) {q} step {s!r} arms {len(svc_rows)} SVC rows > budget '
                    f'{PER_STEP_BUDGET}')
        if len(native_rows) > PER_STEP_BUDGET and verbose:
            print(f'  PRECEDENT (recorded, not touched): {q} step {s!r} arms '
                  f'{len(native_rows)} SV-native rows (upstream-authentic)')

    # (b) ROSTER by name
    want = Counter((q, n, t, xyz) for q, n, t, xyz in ROSTER)
    have = Counter((q.lower(), n.replace('/', BS).lower(), t, xyz)
                   for q, _s, _d, n, t, xyz in rows)
    for key in have - want:
        q, n, t, xyz = key
        violations.append(f'(b) UNWHITELISTED armed row: {q} | {n.split(BS)[-1]} | {t} | {xyz}')
    for key in want - have:
        q, n, t, xyz = key
        violations.append(f'(b) MISSING whitelisted row: {q} | {n.split(BS)[-1]} | {t} | {xyz}')

    # (c) zero tag/dest reuse across SVC-authored rows
    svc = [(q, n, t, xyz) for q, _s, _d, n, t, xyz in rows
           if n.replace('/', BS).lower() in {p.lower() for p in SVC_AUTHORED_NPCS}]
    tags = Counter(t for _q, _n, t, _xyz in svc)
    dests = Counter(xyz for _q, _n, _t, xyz in svc)
    for t, c in tags.items():
        if c > 1:
            violations.append(f'(c) SVC tag reuse: {t} on {c} armed rows')
    for xyz, c in dests.items():
        if c > 1:
            violations.append(f'(c) SVC dest reuse: {xyz} on {c} armed rows')

    # (d) placed >= 1x in the canonical map
    if map_arc:
        counts = scan_map_placed(map_arc, {n for _q, n, _t, _xyz in
                                           ((r[0], r[3], r[4], r[5]) for r in rows)
                                           if n.replace('/', BS).lower() in
                                           {p.lower() for p in SVC_AUTHORED_NPCS}}
                                 or SVC_AUTHORED_NPCS)
        for npc, c in sorted(counts.items()):
            if verbose:
                print(f'  placed-check: {npc.split(BS)[-1]} x{c} in canonical map')
            if c < 1:
                violations.append(f'(d) SVC boat NPC {npc} armed but placed 0x in canonical map')

    if violations:
        print(f'BOATDIALOG BUDGET GATE: {len(violations)} VIOLATION(S)')
        for v in violations:
            print(f'  FAIL {v}')
        return False
    print(f'BOATDIALOG BUDGET GATE: PASS ({len(rows)} armed rows == frozen roster of '
          f'{len(ROSTER)}; Almyros exactly {ALMYROS_ALLOWED}; zero SVC tag/dest reuse)')
    return True


def negtest(quests_arc):
    """Planted defects must each RED the gate (never touches the input file)."""
    import copy as _copy
    arc = ArcArchive.from_file(Path(quests_arc))
    base_rows = census(quests_arc, verbose=False)
    ok = True

    # N1: duplicate-tag row (simulate a new armed row cloning an Almyros tag)
    rows = list(base_rows) + [('Quests/sv_commonmechanics.qst', ALMYROS_STEP,
                               'PLANTED', ALMYROS_NPC, 'tagSVCHelosToGarden', (1, 2, 3))]
    import gate_boatdialog_budget as self_mod  # noqa
    if _rows_pass(rows):
        print('  NEGTEST N1 (duplicate tag + unwhitelisted row) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N1 (duplicate tag + unwhitelisted row) correctly RED')

    # N2: missing whitelisted row (drop one Almyros route)
    rows = [r for r in base_rows if r[4] != 'tagSVCHelosToGarden']
    if _rows_pass(rows):
        print('  NEGTEST N2 (missing roster row) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N2 (missing roster row) correctly RED')

    # N3: budget overflow (4 SVC rows on one non-Almyros step)
    rows = list(base_rows) + [
        ('Quests/urder.qst', 'someStep', 'PLANTED', ALMYROS_NPC, f'tagP{i}', (i, i, i))
        for i in range(4)]
    if _rows_pass(rows):
        print('  NEGTEST N3 (per-step budget overflow) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N3 (per-step budget overflow) correctly RED')
    return ok


def _rows_pass(rows):
    """Run checks (a)-(c) on a synthetic row list (negtest helper)."""
    from collections import Counter, defaultdict
    violations = []
    per_step = defaultdict(list)
    for q, s, d, n, t, xyz in rows:
        per_step[(q.lower(), s)].append((d, n, t, xyz))
    for (q, s), rr in per_step.items():
        svc_rows = [r for r in rr if r[1].replace('/', BS).lower() in
                    {p.lower() for p in SVC_AUTHORED_NPCS}]
        if q.endswith(ALMYROS_QUEST) and s == ALMYROS_STEP:
            alm = [r for r in svc_rows if r[1].replace('/', BS).lower() == ALMYROS_NPC.lower()]
            if len(alm) != ALMYROS_ALLOWED or len(svc_rows) != len(alm):
                violations.append('a')
        elif len(svc_rows) > PER_STEP_BUDGET:
            violations.append('a')
    want = Counter((q, n, t, xyz) for q, n, t, xyz in ROSTER)
    have = Counter((q.lower(), n.replace('/', BS).lower(), t, xyz)
                   for q, _s, _d, n, t, xyz in rows)
    if (have - want) or (want - have):
        violations.append('b')
    svc = [(t, xyz) for q, _s, _d, n, t, xyz in rows
           if n.replace('/', BS).lower() in {p.lower() for p in SVC_AUTHORED_NPCS}]
    if any(c > 1 for c in Counter(t for t, _ in svc).values()):
        violations.append('c')
    if any(c > 1 for c in Counter(x for _, x in svc).values()):
        violations.append('c')
    return not violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quests', required=True)
    ap.add_argument('--map', dest='map_arc')
    ap.add_argument('--census', action='store_true')
    ap.add_argument('--negtest', action='store_true')
    args = ap.parse_args()
    if args.census:
        census(args.quests, verbose=True)
        return
    if args.negtest:
        sys.exit(0 if negtest(args.quests) else 1)
    ok = run_gate(args.quests, args.map_arc)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
