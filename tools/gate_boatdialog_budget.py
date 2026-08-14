#!/usr/bin/env python3
"""GATE - MAX_ARMED_BOATDIALOG BUDGET + NO-CHURN (R-246 rip; R-248 restored roster).

THE BUG CLASS THIS GATE KILLS (hunt wf device-travel, h2/h3/h4 artifacts): the
sv_commonmechanics refire step armed 39 Action_BoatDialog rows on ONE blanket
Condition_OnLevelLoad step re-fired on EVERY level load; 15 rows shared one
tag+dest and 17 NPCs were remote. The engine's boat-offer registry is STATEFUL:
under that arming pattern clicks execute OTHER rows (label included - Will:
"labels were wrong too") and cross-bound NPCs go fully mute (the Warden). The
base-game census envelope is: max 2 BoatDialog rows armed per step EVER, zero
tag reuse, zero dest reuse, one-shot arming. R-246 ripped the row tables; the
devices that replaced them were themselves in-game refuted (R-248), so the
traveler ROWS return - restored in the base-game-faithful shape: dedicated
ONE-SHOT steps (Condition_OnLevelLoad isResettable=0), <=3 rows/step, one
trigger per NPC. The corruption's CHURN term (every-load re-registration) is
structurally banned by check (e); this gate freezes the whole roster by name.

CHECKS (on a BUILT Quests.arc):
  (a) BUDGET   - per (quest, step): armed SVC BoatDialog rows <= PER_STEP_BUDGET
                 (3; the quest-7/8 pair shape at 2 is preferred). The
                 sv_commonmechanics REFIRE step arms exactly ALMYROS_ALLOWED (1
                 since R-249: Garden only; was 3 before Secret + Uber removed)
                 Almyros rows and ZERO other SVC rows (the Will-ratified
                 grandfathered exception; any other SVC row there is the ripped
                 churn class returning). SV-native steps already >budget are
                 RECORDED AS PRECEDENT (printed), never touched.
  (b) ROSTER   - the global armed row set == the explicit BY-NAME whitelist
                 below (quest, npc, tag, dest per row): ROSTER (canonical 24)
                 or + ROSTER_TESTHUB_EXTRA (--hub, 49). ANY new row fails loud.
  (c) NO REUSE - zero tag reuse and zero dest-coord reuse across the SVC
                 MENU-AUTHORED rows (Almyros + the Olympus herald), plus LABEL
                 INTEGRITY over ALL SVC rows: one tag -> exactly one dest
                 (the mislabel class Will hit: "labels were wrong too").
  (d) PLACED   - every SVC-authored/traveler BoatDialog npc record armed in the
                 arc is placed >=1x in the matching map variant
                 (armed-but-unplaced rows never reach a player).
  (e) NO CHURN (R-248) - every trigger arming an SVC row carries ONLY
                 isResettable=0 conditions (ONE-SHOT arming), EXCEPT the named
                 Almyros refire trigger. A travel row on a re-firing step is
                 the proven stateful-registry corruption source and fails loud.

Usage:
  py tools/gate_boatdialog_budget.py --quests <Quests.arc> [--map <Levels.arc>] [--hub]
  py tools/gate_boatdialog_budget.py --quests <arc> --census   # report only
  py tools/gate_boatdialog_budget.py --quests <arc> [--hub] --negtest  # planted defects
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

# ── The Will-ratified budget (R-246 envelope; R-248 restored steps) ─────────────
PER_STEP_BUDGET = 3          # R-248: <=2 preferred (quest-7/8 pairing), <=3 allowed
ALMYROS_ALLOWED = 1          # R-249 (2026-08-14): Garden ONLY (Secret + Uber removed from Steam);
#                              was 3 under R-246 ("Almyros keeps his 3-route talk menu")
ALMYROS_QUEST = 'sv_commonmechanics.qst'
ALMYROS_STEP = ('Makes it so Quest Never Completes -- '
                'Allows for refiring on triggers')
ALMYROS_NPC = r'records\quests\portal_master_helos.dbr'
# (e) NO-CHURN exemption #2: the Olympus->Rhodes herald (the R-248 mechanism-(B)
# exemplar chain, in-game proven - Will's own R-248 words name this portal working).
# His single row rides the Q3 trigger: Condition_KillAllCreaturesFromProxy
# isResettable=1 + canReFire - EVENT-GATED re-arming on repeat Typhon kills, the
# urder 'PortalDude Control' precedent class, NOT the blanket level-load churn the
# rip killed. Shipped since build31; never touch (WILL_RULINGS R-248 route 8).
HERALD_NPC = r'records\quests\portal_master_olympus.dbr'
# (c2) LABEL-INTEGRITY exemption: EMPTY since R-249 (2026-08-14). The ONE entry it
# held was the b62 DELIBERATE cross-build divergence for tagSVCHelosToUber (Almyros's
# canonical row landed INSIDE crypt_floor1 while the TESTHUB launcher's same tag lands
# at the maze03 DOOR). R-249 REMOVED Almyros's Uber row from the Steam build, so
# tagSVCHelosToUber now points at exactly ONE dest (the TESTHUB maze03 door) and needs
# no allowance; the divergence is dissolved. Any tag armed with >1 dest now fails loud.
C2_ALLOWED = {}

# SVC-authored boat NPCs (checks (c)+(d) scope). Everything else in the arc is
# upstream-authentic (SV-native / base) and is frozen by the roster whitelist
# alone.
SVC_AUTHORED_NPCS = {
    r'records\quests\portal_master_helos.dbr',    # Almyros (Will's talk menu)
    r'records\quests\portal_master_olympus.dbr',  # Olympus->Rhodes herald
}
# R-248 restored traveler NPCs (one-shot-armed rows; checks (a)/(d)/(e) + label
# integrity). Kept apart from SVC_AUTHORED_NPCS so check (c)'s strict zero-reuse
# stays scoped to the talk menus (the traveler world legitimately shares the
# Helos-return tag+dest across NPCs in DIFFERENT levels - the shipped, Will-walked
# pre-R-246 shape; same-level route collisions are prevented map-side by the b48
# Almyros de-dup in build_section_surgery.merge_hub_into_inject_specs).
SVC_TRAVELER_NPCS = (
    {r'records\quests\svc_area_return_uber.dbr',
     r'records\quests\svc_warden_sparta_crypt.dbr'}
    | {r'records\quests\svc_testhub_return_%s.dbr' % s for s in
       ('garden', 'secret', 'uber', 'sparta', 'bossarena')}
    | {r'records\quests\svc_helos_trav_%s.dbr' % s for s in
       ('garden', 'secret', 'sparta', 'uber', 'bossarena', 'warband', 'dorus',
        'tantalus', 'charon', 'mnemophage', 'ephialtes', 'devourer', 'vashkarr',
        'obsidian')}
    | {r'records\quests\svc_area_return_%s.dbr' % s for s in
       ('warband', 'dorus', 'tantalus', 'charon', 'mnemophage', 'ephialtes',
        'devourer', 'vashkarr', 'obsidian')}
)
# NPCs whose placements exist only on the TESTHUB map variant (check (d) scoping).
SVC_HUB_ONLY_NPCS = (
    {r'records\quests\svc_testhub_return_bossarena.dbr'}
    | {p for p in SVC_TRAVELER_NPCS if 'svc_helos_trav_' in p}
    | {p for p in SVC_TRAVELER_NPCS
       if 'svc_area_return_' in p and not p.endswith('svc_area_return_uber.dbr')}
)


def _svc_all_lc():
    return {p.replace('/', BS).lower() for p in (SVC_AUTHORED_NPCS | SVC_TRAVELER_NPCS)}

# ── (b) THE GLOBAL ARMED ROSTER, BY NAME ────────────────────────────────────────
# One entry per armed Action_BoatDialog row that may exist in the built arc:
#   (quest_lc, npc_lc, tag, (x, y, z))
# Derived from the post-R-246-rip census (this file's --census on the built arc)
# and cross-checked against the pre-rip census: the ONLY SVC-authored survivors
# are Almyros's 1 row (Garden only; Secret + Uber removed by R-249 2026-08-14) +
# the herald's 1; the other 12 are upstream-authentic (urder 3, Leinth vortex 5,
# base knossos 2 + greece-to-egypt 2). If corruption ever recurs on Steam, the
# residual suspect list is IN THIS ORDER: vortex 5 (shared-step), urder 3 (see
# docs/BACKLOG.md R-246 lane record).
def _r(quest, npc, tag, xyz):
    return (quest.lower(), npc.replace('/', BS).lower(), tag, xyz)


ROSTER = [
    # SVC-authored: Almyros the Wayfarer, the ruled talk menu (R-246), now GARDEN ONLY
    # (R-249 2026-08-14 removed his Secret Place + Uber Dungeon rows from the Steam build;
    # both tags stay minted on the TESTHUB launchers svc_helos_trav_secret/_uber below).
    _r('sv_commonmechanics.qst', ALMYROS_NPC, 'tagSVCHelosToGarden', (1173, -39, -4001)),
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
    # ── R-248 RESTORED CANONICAL ROWS (10; one-shot armed on dedicated steps) ──
    # Independent by-name copy of build_quest_files.R248_CANONICAL_STEPS - the two are
    # cross-checked by construction: a generator/table edit that does not also land here
    # fails check (b) loud. Dest literals are the R-245-addendum/gate-frozen values,
    # floorCal-verified 2026-08-14 (see the R248 block in build_quest_files).
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_uber.dbr',
       'tagSVCEnterUberDungeon', (-2438, 10, -2457)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_uber.dbr',
       'tagSVCReturnToLabyrinthDoor', (-7793, 1, -3793)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_uber.dbr',
       'tagSVCTestHubToHelos', (-5974, 1, 911)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_warden_sparta_crypt.dbr',
       'tagSVCEnterSpartaCrypt', (-5596, 1, -1410)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_sparta.dbr',
       'tagSVCReturnToAthensCatacomb', (-6587, 1, -3180)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_sparta.dbr',
       'tagSVCTestHubToHelos', (-5974, 1, 911)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_garden.dbr',
       'tagSVCTestHubToHelos', (-5974, 1, 911)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_garden.dbr',
       'tagSVCTestHubToBloodCave', (6018, 19, 3293)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_secret.dbr',
       'tagSVCTestHubToHelos', (-5974, 1, 911)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_secret.dbr',
       'tagSVCTestHubToBloodCave', (6018, 19, 3293)),
]

# ── R-248 TESTHUB EXTRA ROWS (25; armed ONLY in the SVC_TEST_HUB=1 Quests variant,
# LOCAL-ONLY until the Frida boat-registry capacity probe). Gate with --hub.
_HELOS = (-5974, 1, 911)
ROSTER_TESTHUB_EXTRA = [
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_garden.dbr',
       'tagSVCHelosToGarden', (1173, -39, -4001)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_secret.dbr',
       'tagSVCHelosToSecret', (-2396, 2, -5790)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_sparta.dbr',
       'tagSVCHelosToSparta', (-6587, 1, -3180)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_uber.dbr',
       'tagSVCHelosToUber', (-7793, 1, -3793)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_bossarena.dbr',
       'tagSVCTestHubToBossArena', (-429, 28, -3538)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_bossarena.dbr',
       'tagSVCTestHubToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_testhub_return_bossarena.dbr',
       'tagSVCTestHubToBloodCave', (6018, 19, 3293)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_warband.dbr',
       'tagSVCHelosToWarband', (5699, 1, 3315)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_warband.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_dorus.dbr',
       'tagSVCHelosToDorus', (428, 1, -8113)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_dorus.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_tantalus.dbr',
       'tagSVCHelosToTantalus', (-346, -9, -10131)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_tantalus.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_charon.dbr',
       'tagSVCHelosToCharon', (-484, -12, -9587)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_charon.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_mnemophage.dbr',
       'tagSVCHelosToMnemophage', (169, -10, -11418)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_mnemophage.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_ephialtes.dbr',
       'tagSVCHelosToEphialtes', (-1756, 3, -13198)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_ephialtes.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_devourer.dbr',
       'tagSVCHelosToDevourer', (5349, 1, 3009)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_devourer.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_vashkarr.dbr',
       'tagSVCHelosToVashkarr', (-227, 1, 146)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_vashkarr.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
    _r('sv_commonmechanics.qst', r'records\quests\svc_helos_trav_obsidian.dbr',
       'tagSVCHelosToObsidian', (-1827, -74, -462)),
    _r('sv_commonmechanics.qst', r'records\quests\svc_area_return_obsidian.dbr',
       'tagSVCAreaReturnToHelos', _HELOS),
]
assert len(ROSTER) == 24, f'canonical roster must be 24 rows, is {len(ROSTER)}'
assert len(ROSTER_TESTHUB_EXTRA) == 25, \
    f'TESTHUB extra roster must be 25 rows, is {len(ROSTER_TESTHUB_EXTRA)}'


def _s32(v):
    return v - 0x100000000 if v >= 0x80000000 else v


def field_val(items, key):
    for it in items:
        if isinstance(it, tuple) and it[0] == 'field' and it[1] == key:
            return it[2][1]
    return None


def _collect_resettables(items, out):
    """Recursively collect every isResettable field value under a conditions block."""
    for it in items:
        if isinstance(it, tuple) and it[0] == 'field' and it[1] == 'isResettable':
            out.append(it[2][1])
        elif isinstance(it, tuple) and it[0] == 'block':
            _collect_resettables(it[1], out)


def iter_boat_rows(qst_bytes):
    """Yield (step_name, trigger_display, npc, tag, (x,y,z), resettables) for every
    Action_BoatDialog row in the quest. resettables = tuple of every isResettable
    value among the row's trigger CONDITIONS (check (e): all 0 == one-shot arming)."""
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
            header, conds, actions = blocks[t], blocks[t + 1], blocks[t + 2]
            display = field_val(header[1], 'displayTag')
            resettables = []
            _collect_resettables(conds[1], resettables)
            resettables = tuple(resettables)
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
                    yield (step_name, display, npc, tag, (x, y, z), resettables)
                i += 1


def census(arc_path, verbose=True):
    """Return list of (quest_name, step, display, npc, tag, dest, resettables) rows."""
    arc = ArcArchive.from_file(Path(arc_path))
    rows = []
    for e in arc.entries:
        if e.entry_type != 3 or not e.name.lower().endswith('.qst'):
            continue
        data = arc.get_file(e.name)
        if data is None or b'Action_BoatDialog' not in data:
            continue
        try:
            for (step, disp, npc, tag, dest, rst) in iter_boat_rows(data):
                rows.append((e.name, step, disp, npc, tag, dest, rst))
        except Exception as ex:  # parse failure = gate failure, never silence
            raise SystemExit(f'BUDGET GATE: {e.name} failed to parse: {ex}')
    if verbose:
        from collections import Counter
        per_step = Counter((q, s) for q, s, _d, _n, _t, _xyz, _r in rows)
        print(f'--- BoatDialog census: {len(rows)} armed rows in {arc_path} ---')
        for (q, s), n in sorted(per_step.items()):
            print(f'  {n:3d} rows  {q}  step={s!r}')
        for q, s, d, n, t, xyz, rst in rows:
            print(f'    {q} | {d} | {n.split(BS)[-1]} | {t} | {xyz} | reset={rst}')
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


def run_gate(quests_arc, map_arc=None, verbose=True, hub=False):
    rows = census(quests_arc, verbose=verbose)
    violations = []
    roster = list(ROSTER) + (list(ROSTER_TESTHUB_EXTRA) if hub else [])
    svc_all = _svc_all_lc()

    # (a) BUDGET per (quest, step) - over ALL SVC rows (authored + traveler)
    from collections import Counter, defaultdict
    per_step = defaultdict(list)
    for q, s, d, n, t, xyz, rst in rows:
        per_step[(q.lower(), s)].append((d, n, t, xyz))
    for (q, s), rr in sorted(per_step.items()):
        is_almyros_step = q.endswith(ALMYROS_QUEST) and s == ALMYROS_STEP
        svc_rows = [r for r in rr if r[1].replace('/', BS).lower() in svc_all]
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
                    f'({[r[2] for r in other_svc]}) - the ripped CHURN class returning '
                    f'(R-248: travel rows NEVER ride a re-firing step)')
        else:
            if len(svc_rows) > PER_STEP_BUDGET:
                violations.append(
                    f'(a) {q} step {s!r} arms {len(svc_rows)} SVC rows > budget '
                    f'{PER_STEP_BUDGET}')
        if len(native_rows) > PER_STEP_BUDGET and verbose:
            print(f'  PRECEDENT (recorded, not touched): {q} step {s!r} arms '
                  f'{len(native_rows)} SV-native rows (upstream-authentic)')

    # (b) ROSTER by name
    want = Counter((q, n, t, xyz) for q, n, t, xyz in roster)
    have = Counter((q.lower(), n.replace('/', BS).lower(), t, xyz)
                   for q, _s, _d, n, t, xyz, _r in rows)
    for key in have - want:
        q, n, t, xyz = key
        violations.append(f'(b) UNWHITELISTED armed row: {q} | {n.split(BS)[-1]} | {t} | {xyz}')
    for key in want - have:
        q, n, t, xyz = key
        violations.append(f'(b) MISSING whitelisted row: {q} | {n.split(BS)[-1]} | {t} | {xyz}')

    # (c) zero tag/dest reuse across the SVC MENU-AUTHORED rows (talk menus)
    svc = [(q, n, t, xyz) for q, _s, _d, n, t, xyz, _r in rows
           if n.replace('/', BS).lower() in {p.lower() for p in SVC_AUTHORED_NPCS}]
    tags = Counter(t for _q, _n, t, _xyz in svc)
    dests = Counter(xyz for _q, _n, _t, xyz in svc)
    for t, c in tags.items():
        if c > 1:
            violations.append(f'(c) SVC tag reuse: {t} on {c} armed rows')
    for xyz, c in dests.items():
        if c > 1:
            violations.append(f'(c) SVC dest reuse: {xyz} on {c} armed rows')
    # (c2) LABEL INTEGRITY over ALL SVC rows: one tag -> exactly one dest. (Two rows
    # may share a tag+dest across NPCs in different levels - the shipped traveler
    # shape - but the same LABEL must never point at two different places: the
    # mislabel class Will hit in the corruption era.)
    tag_dests = defaultdict(set)
    for q, _s, _d, n, t, xyz, _r in rows:
        if n.replace('/', BS).lower() in svc_all:
            tag_dests[t].add(xyz)
    for t, ds in sorted(tag_dests.items()):
        if len(ds) > 1 and ds != C2_ALLOWED.get(t):
            violations.append(f'(c2) LABEL INTEGRITY: tag {t} armed with {len(ds)} '
                              f'different dests {sorted(ds)}')

    # (d) placed >= 1x in the matching map variant
    if map_arc:
        armed_svc = {r[3].replace('/', BS).lower() for r in rows
                     if r[3].replace('/', BS).lower() in svc_all}
        hub_only = {p.replace('/', BS).lower() for p in SVC_HUB_ONLY_NPCS}
        if hub:
            # b48 de-dup: Almyros's PLACEMENT is dropped from the TESTHUB plaza so the
            # restored launchers (same tag+dest) are sole in-level route owners; his 3
            # armed rows are inert there (armed-but-unplaced no-op, the D3 precedent).
            expect_placed = armed_svc - {ALMYROS_NPC.replace('/', BS).lower()}
        else:
            expect_placed = armed_svc - hub_only
        counts = scan_map_placed(map_arc, expect_placed)
        for npc, c in sorted(counts.items()):
            if verbose:
                print(f'  placed-check: {npc.split(BS)[-1]} x{c} in '
                      f'{"TESTHUB" if hub else "canonical"} map')
            if c < 1:
                violations.append(f'(d) SVC boat NPC {npc} armed but placed 0x in the '
                                  f'{"TESTHUB" if hub else "canonical"} map')

    # (e) NO CHURN (R-248): every SVC-armed row rides a ONE-SHOT trigger
    for q, s, d, n, t, xyz, rst in rows:
        nl = n.replace('/', BS).lower()
        if nl not in svc_all:
            continue
        is_almyros_trigger = (q.lower().endswith(ALMYROS_QUEST) and s == ALMYROS_STEP
                              and nl == ALMYROS_NPC.lower())
        if is_almyros_trigger:
            continue  # Will-ratified refire exception #1 (the 3-route talk menu)
        if nl == HERALD_NPC.replace('/', BS).lower():
            continue  # exemption #2: event-gated Q3 kill trigger (see HERALD_NPC)
        if not rst or any(v != 0 for v in rst):
            violations.append(f'(e) NO-CHURN: {q} step {s!r} row {t} on '
                              f'{n.split(BS)[-1]} has isResettable={rst} - travel '
                              f'arming must be ONE-SHOT (isResettable=0)')

    if violations:
        print(f'BOATDIALOG BUDGET GATE ({"TESTHUB" if hub else "canonical"}): '
              f'{len(violations)} VIOLATION(S)')
        for v in violations:
            print(f'  FAIL {v}')
        return False
    print(f'BOATDIALOG BUDGET GATE ({"TESTHUB" if hub else "canonical"}): PASS '
          f'({len(rows)} armed rows == frozen roster of {len(roster)}; Almyros exactly '
          f'{ALMYROS_ALLOWED}; zero talk-menu reuse; label integrity; one-shot arming)')
    return True


def negtest(quests_arc, hub=False):
    """Planted defects must each RED the gate (never touches the input file)."""
    base_rows = census(quests_arc, verbose=False)
    ok = True

    if not _rows_pass(base_rows, hub):
        print('  NEGTEST positive control FAILED (base arc rows do not pass a-c,e)')
        return False
    print('  [GREEN OK] positive control (built arc rows pass)')

    # N1: duplicate-tag row (simulate a new armed row cloning an Almyros tag)
    rows = list(base_rows) + [('Quests/sv_commonmechanics.qst', ALMYROS_STEP,
                               'PLANTED', ALMYROS_NPC, 'tagSVCHelosToGarden',
                               (1, 2, 3), (1,))]
    if _rows_pass(rows, hub):
        print('  NEGTEST N1 (duplicate tag + unwhitelisted row) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N1 (duplicate tag + unwhitelisted row) correctly RED')

    # N2: missing whitelisted row (drop one Almyros route)
    rows = [r for r in base_rows if r[4] != 'tagSVCHelosToGarden'
            or r[3].replace('/', BS).lower() != ALMYROS_NPC.lower()]
    if _rows_pass(rows, hub):
        print('  NEGTEST N2 (missing roster row) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N2 (missing roster row) correctly RED')

    # N3: budget overflow (4 SVC rows on one non-Almyros step)
    rows = list(base_rows) + [
        ('Quests/urder.qst', 'someStep', 'PLANTED', ALMYROS_NPC, f'tagP{i}',
         (i, i, i), (0,))
        for i in range(4)]
    if _rows_pass(rows, hub):
        print('  NEGTEST N3 (per-step budget overflow) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N3 (per-step budget overflow) correctly RED')

    # N4 (R-248, the planted CHURN row): a traveler row armed on the re-firing
    # Almyros step must RED via (a) AND (e) - the exact construction that corrupted.
    rows = list(base_rows) + [
        ('Quests/sv_commonmechanics.qst', ALMYROS_STEP, 'PLANTED CHURN',
         r'records\quests\svc_warden_sparta_crypt.dbr', 'tagSVCEnterSpartaCrypt',
         (-5596, 1, -1410), (1,))]
    if _rows_pass(rows, hub):
        print('  NEGTEST N4 (traveler row on the REFIRE step - churn) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N4 (traveler row on the REFIRE step - churn) correctly RED')

    # N5 (R-248, the flipped one-shot): a whitelisted traveler row whose trigger
    # condition is isResettable=1 must RED via (e) even though (b) is clean.
    rows = []
    flipped = False
    for r in base_rows:
        if (not flipped and r[4] == 'tagSVCEnterUberDungeon'
                and 'svc_area_return_uber' in r[3].lower()):
            rows.append(r[:6] + ((1,),))
            flipped = True
        else:
            rows.append(r)
    if not flipped:
        print('  NEGTEST N5 SKIPPED (no uber enter row in this arc?) - FAIL')
        ok = False
    elif _rows_pass(rows, hub):
        print('  NEGTEST N5 (one-shot flag flipped to refire) FAILED TO RED')
        ok = False
    else:
        print('  NEGTEST N5 (one-shot flag flipped to refire) correctly RED')
    return ok


def _rows_pass(rows, hub=False):
    """Run checks (a)-(c2),(e) on a synthetic row list (negtest helper)."""
    from collections import Counter, defaultdict
    violations = []
    svc_all = _svc_all_lc()
    roster = list(ROSTER) + (list(ROSTER_TESTHUB_EXTRA) if hub else [])
    per_step = defaultdict(list)
    for q, s, d, n, t, xyz, rst in rows:
        per_step[(q.lower(), s)].append((d, n, t, xyz))
    for (q, s), rr in per_step.items():
        svc_rows = [r for r in rr if r[1].replace('/', BS).lower() in svc_all]
        if q.endswith(ALMYROS_QUEST) and s == ALMYROS_STEP:
            alm = [r for r in svc_rows if r[1].replace('/', BS).lower() == ALMYROS_NPC.lower()]
            if len(alm) != ALMYROS_ALLOWED or len(svc_rows) != len(alm):
                violations.append('a')
        elif len(svc_rows) > PER_STEP_BUDGET:
            violations.append('a')
    want = Counter((q, n, t, xyz) for q, n, t, xyz in roster)
    have = Counter((q.lower(), n.replace('/', BS).lower(), t, xyz)
                   for q, _s, _d, n, t, xyz, _r in rows)
    if (have - want) or (want - have):
        violations.append('b')
    svc = [(t, xyz) for q, _s, _d, n, t, xyz, _r in rows
           if n.replace('/', BS).lower() in {p.lower() for p in SVC_AUTHORED_NPCS}]
    if any(c > 1 for c in Counter(t for t, _ in svc).values()):
        violations.append('c')
    if any(c > 1 for c in Counter(x for _, x in svc).values()):
        violations.append('c')
    tag_dests = defaultdict(set)
    for q, _s, _d, n, t, xyz, _r in rows:
        if n.replace('/', BS).lower() in svc_all:
            tag_dests[t].add(xyz)
    if any(len(ds) > 1 and ds != C2_ALLOWED.get(t)
           for t, ds in tag_dests.items()):
        violations.append('c2')
    for q, s, _d, n, t, _xyz, rst in rows:
        nl = n.replace('/', BS).lower()
        if nl not in svc_all:
            continue
        if (q.lower().endswith(ALMYROS_QUEST) and s == ALMYROS_STEP
                and nl == ALMYROS_NPC.lower()):
            continue
        if nl == HERALD_NPC.replace('/', BS).lower():
            continue
        if not rst or any(v != 0 for v in rst):
            violations.append('e')
    return not violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quests', required=True)
    ap.add_argument('--map', dest='map_arc')
    ap.add_argument('--hub', action='store_true',
                    help='gate the TESTHUB Quests variant (roster 51; map = TESTHUB)')
    ap.add_argument('--census', action='store_true')
    ap.add_argument('--negtest', action='store_true')
    args = ap.parse_args()
    if args.census:
        census(args.quests, verbose=True)
        return
    if args.negtest:
        sys.exit(0 if negtest(args.quests, hub=args.hub) else 1)
    ok = run_gate(args.quests, args.map_arc, hub=args.hub)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
