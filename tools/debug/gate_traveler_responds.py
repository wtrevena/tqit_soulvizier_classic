"""gate_traveler_responds.py - TRAVEL-INVARIANTS FAMILY (b48 SPARTA-MUTE, round 3)

Asserts every hub boat-dialog traveler NPC will actually RESPOND in-game (the talk-confirm
boat dialog fires) - no MUTE traveler can ship. Wired into the travel-invariants battery
(gate_travel_npc_invariants.py) via the build-free facts_from_specs() path, so no future hub
build can ship a mute/orphan/warden/beyond-window traveler.

ROOT MECHANISM (proven b48 round 2, from the deployed set 838bdc3a/841c56cd + the base-game
Quests.arc): the TQAE boat-dialog system is strictly **1 route : 1 NPC**. EVERY base-game / SV
boat NPC owns a UNIQUE (npc, tag, dest) triple - across all 9 base/SV boat NPCs (Athens/Knossos/
Rhakotis boatmen, the olympus & urder portal-masters, the blood-cave vortex) NO tag and NO dest
is ever shared between two NPCs. When two PLACED NPCs in the SAME level offer the same route
(same tag OR same dest), only the first-registered one binds it; the later one goes MUTE. That is
Will's Sparta bug: in the Helos plaza `portal_master_helos` (Almyros, trig1) and the dedicated
`svc_helos_trav_sparta` (trig6) both offer tag `tagSVCHelosToSparta` -> Almyros binds, the
dedicated Sparta traveler is silent. The 6 unique-route dedicated travelers own their routes alone
-> they DO fire (Will hit them = the b44 land-in-chest class).

MODEL (why an UNPLACED NPC is never faulted): ownership is PER-LEVEL, proven by the ground truth -
the 6 area returns share tag AND dest but sit in different levels and all work; Boss Arena works
though the UNPLACED svc_testhub_master offers it earlier. So an unplaced NPC's OnLevelLoad boat
offers simply no-op (no entity to attach to) and can never mute anything or be clicked. The gate
faults only NPCs a player can actually CLICK (placed) that then do NOTHING. (This is the round-1
error corrected: round-1 failed on unplaced 'dead offers', which are harmless.)

HARD INVARIANTS (any failure => exit 1; no MUTE clickable traveler ships) - every PLACED hub NPC:
  G-COLLISION  must OWN >=1 of its routes in its level - i.e. no earlier-registered NPC present in
               the SAME level already binds that route (tag or dest). Losing every route = MUTE.
                                                                          [THE Sparta bug]
  G-WARDEN     its record must be placed in exactly 1 level (a record binds ONE entity; extra
               placements are MUTE - documented project "warden law"; give each its own record).
  G-ORPHAN     must register >=1 boat route (a placed NPC with no route does NOTHING when clicked).
  G-DEST       every route destination is non-zero (a real teleport target).

b63 SILENT-WARDEN ADDITIONS (Will 2026-08-10: "when I click on the guy who travels you to the
spartan crypt (warden of the spartan crypt) nothing happens, no dialog box comes up, nothing").
The four invariants above were ALL GREEN on the build that shipped that mute Warden to Steam, so
they were not sufficient. Two more, both fail-loud:

  G-SOLE-SOURCE   no PLACED hub boat NPC may draw its ENTIRE route set from TRAVELER_ENTER_OFFERS.
                  Enter-offers are a SECOND menu entry bolted onto an NPC that already owns a
                  HELOS_HUB_TRAVEL / per-area-return route; they are appended LAST to the host step
                  and the class has never been confirmed in-game. The Warden of the Spartan Crypt
                  was the only placed NPC in the mod whose whole menu came from one, and it opened
                  no dialog at all. Sole-sourcing an unproven trigger class is now a build error.

  G-DIALOG-CHAIN  the brief's "no silent traveler can ever ship again" gate. For EVERY placed
                  traveler NPC, all three links of the talk chain must RESOLVE:
                    (1) RECORD  - the .dbr is minted by the arz builder (apply_svc_patches roster),
                                  so the shipped .arz really contains the NPC record;
                    (2) QUEST   - it registers >=1 Action_BoatDialog route, and that route lives in
                                  the always-loaded host quest sv_commonmechanics.qst (never in some
                                  new quest that would need a fresh QUESTS registration);
                    (3) WINDOW  - that host quest sits INSIDE the engine's proven ~256-entry QUESTS
                                  load window. Proven build-free because the host quest IS
                                  svaera_plus_portals.QUEST_INSERT_ANCHOR, the anchor the map's
                                  QUESTS rebuild splices the SV questlines after and asserts is
                                  in-window; proven directly when a built Levels.arc is passed
                                  (--levels), by reading the map's QUESTS section and checking the
                                  host quest's actual index. A break in ANY link = a clickable NPC
                                  that says nothing, which is precisely Will's bug.

Read-only. Defaults to the DEPLOYED DEV set; override with --quests / --levels to gate a
freshly-built pair (wire into the build after Quests+TESTHUB-Levels are built).

Usage:
  py tools/debug/gate_traveler_responds.py                 # gate the deployed DEV set
  py tools/debug/gate_traveler_responds.py --quests Q.arc --levels L.arc   # gate a freshly-built pair
  py tools/debug/gate_traveler_responds.py --specs         # BUILD-FREE: gate the TESTHUB tooling tables
  py tools/debug/gate_traveler_responds.py --specs --canonical             # build-free canonical build
"""
import sys, struct, argparse
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
import qst_format as qf
# NOTE: the arc-loading deps (arc_patcher / survey_uberboss_spots / contracts_map) are imported
# lazily INSIDE load_routes / load_placements / _instances so the build-free facts_from_specs()
# path (used to wire this gate into gate_travel_npc_invariants) stays a lightweight import.

BS = chr(92)
VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}
DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Resources")
# The hub rig ONLY (every hub boat NPC registers in sv_commonmechanics). Deliberately EXCLUDES
# base-game/SV boatmen (athens/knossos/rhakotis/olympus/urder/vortex) - those register their
# routes in their own per-act quests (not this always-loaded host), are 1 route : 1 NPC by
# construction, and are out of scope for the hub-traveler-mute gate.
# PR-5 SPARTA POLISH (Will 2026-08-06): svc_warden_sparta (the dedicated "Warden of the Spartan
# Crypt" clone) is a hub boat NPC placed canonically at the Athens-catacomb Sparta-crypt entrance,
# so it must be tracked here (it owns the tagSVCEnterSpartaCrypt descend route). The keyword is the
# specific 'svc_warden_sparta' (not bare 'svc_warden') so it cannot accidentally match unrelated
# 'ss_warden_*' behemoth/boss records.
HUB_KW = ('svc_helos_trav', 'svc_area_return', 'svc_testhub', 'portal_master_helos',
          'svc_warden_sparta')
HOST_QST = "sv_commonmechanics.qst"

# b63: route provenance. Which generator emitted a route decides G-SOLE-SOURCE.
SRC_ENTER = 'enter_offer'     # build_quest_files._add_traveler_enter_offers (appended LAST)
SRC_HUB = 'hub'               # _add_helos_traveler_hub_travel (the Will-confirmed class)
SRC_PORTAL = 'portal'         # _add_helos_portal_travel (Almyros)
SRC_RETURN = 'testhub_return'  # _add_testhub_portal_travel (the 5 per-area returns)
# The displayTag prefix _add_traveler_enter_offers stamps on its triggers. This is how the
# arc-reading path recovers provenance from a BUILT Quests.arc (the spec path sets it directly).
ENTER_OFFER_DISPLAY_PREFIX = 'SVC: Traveler Enter-Offer'
HUB_DISPLAY_PREFIX = 'SVC: Helos Traveler Hub'


def s32(v):
    return struct.unpack("<i", struct.pack("<I", v))[0] if isinstance(v, int) else v


def _blocks(items):
    return [it[1] for it in items if it[0] == "block"]


def _fields(block_items):
    return [(it[1], it[2][1]) for it in block_items if it[0] == "field"]


def _entries(container_items):
    out, pend = [], None
    for it in container_items:
        if it[0] == "field" and it[1] in ("conditionClassName", "actionClassName"):
            pend = it[2][1]
        elif it[0] == "block":
            if pend is not None:
                out.append((pend, dict(_fields(it[1]))))
                pend = None
    return out


def _src_from_display(display):
    """b63: recover a route's emitting generator from its trigger displayTag (the only
    provenance a BUILT Quests.arc carries)."""
    if display.startswith(ENTER_OFFER_DISPLAY_PREFIX):
        return SRC_ENTER
    if display.startswith(HUB_DISPLAY_PREFIX):
        return SRC_HUB
    if 'Portal-Master' in display:
        return SRC_PORTAL
    if 'TESTHUB Return' in display:
        return SRC_RETURN
    return 'other'


def load_routes(quests_arc):
    """Ordered list of route dicts from sv_commonmechanics step 1, in registration order:
    {order, npc(lower), npc_short(lower), tag, dest(x,y,z), src, host}."""
    from arc_patcher import ArcArchive
    arc = ArcArchive.from_file(quests_arc)
    tree = qf.parse(arc.get_file(HOST_QST))
    sbl = _blocks(tree[1])
    routes = []
    order = 0
    for s in range(len(sbl) // 3):
        container = sbl[3 * s + 1]
        cbl = _blocks(container)
        idx = 0
        while idx + 2 < len(cbl):
            display = dict(_fields(cbl[idx])).get("displayTag", "")
            for an, d in _entries(cbl[idx + 2]):
                if an == "Action_BoatDialog":
                    npc = d.get("npc", "")
                    routes.append(dict(
                        order=order, step=s,
                        npc=npc.lower(), npc_short=npc.split(BS)[-1].lower(),
                        tag=d.get("tag", ""),
                        dest=(s32(d.get("x", 0)), s32(d.get("y", 0)), s32(d.get("z", 0))),
                        src=_src_from_display(display), host=HOST_QST))
                    order += 1
            idx += 3
    return routes


def _instances(blob, base):
    from contracts_map import parse_blob_sections
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
        out = []
        for _ in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            dbr = (strings[sid] if sid < len(strings) else b'?').decode('latin1')
            out.append(dbr)
            pos += base + (16 if flags != 0 else 0)
        return out
    return []


def load_placements(levels_arc):
    """{npc_short_lower -> set(level_fname_short)} for every boat-relevant placed NPC."""
    import survey_uberboss_spots as S
    data, levels = S.load_world(levels_arc)
    per = defaultdict(set)
    for lv in levels:
        fname = lv.get('fname', '?')
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        base = VER_BASE.get(blob[3], 72)
        try:
            insts = _instances(blob, base)
        except Exception:
            continue
        for dbr in insts:
            dl = dbr.lower()
            if any(kw in dl for kw in HUB_KW):
                per[dl.replace('/', BS).split(BS)[-1]].add(fname.replace('/', BS).split(BS)[-1])
    return per


def facts_from_specs(testhub=True):
    """BUILD-FREE (routes, placed) derived from the REAL tooling tables, so this gate can be wired
    into gate_travel_npc_invariants WITHOUT a 1.3GB map build. Routes come from the build_quest_files
    boat-dialog trigger tables in their sv_commonmechanics REGISTRATION ORDER (Almyros portal ->
    per-area returns -> the 17-record Helos hub); placements come from build_section_surgery's REAL
    specs (merge_hub_into_inject_specs(INJECT_SPECS) for the TESTHUB build, or INJECT_SPECS for
    canonical). Mirrors the arc-based load_routes/load_placements the deployed gate uses. Whatever the
    fix code does, this reflects it - so a PASS here proves the shipped tables are mute-free."""
    import build_quest_files as bqf
    import build_section_surgery as bss
    routes, order = [], 0

    def add(npc, dests, src):
        nonlocal order
        short = npc.replace('/', BS).split(BS)[-1].lower()
        for xyz, tag in dests:
            # DESTS tables already hold SIGNED world coords (the arc path stores them unsigned and
            # s32-decodes on read; here they are native signed, so use them as-is).
            routes.append(dict(order=order, step=0, npc=npc.lower(), npc_short=short,
                               tag=tag, dest=tuple(int(v) for v in xyz),
                               src=src, host=bqf.HELOS_PORTAL_HOST_QUEST))
            order += 1

    add(bqf.HELOS_PORTAL_NPC, bqf.HELOS_PORTAL_DESTS, SRC_PORTAL)   # Almyros 4-dest (trig 1)
    for npc in bqf.TESTHUB_AREA_RETURN_NPCS:                        # per-area returns (2 each)
        # b62 TRAVELERS-INTO-AREAS: sparta/uber override to return-to-origin; the rest keep the
        # shared Helos+BloodCave menu (see build_quest_files.TESTHUB_RETURN_DESTS_BY_NPC).
        dests = bqf.TESTHUB_RETURN_DESTS_BY_NPC.get(npc, bqf.TESTHUB_RETURN_DESTS)
        add(npc, dests, SRC_RETURN)
    for npc, xyz, tag in bqf.HELOS_HUB_TRAVEL:                      # the hub block (1 each)
        add(npc, [(xyz, tag)], SRC_HUB)
    for npc, xyz, tag in bqf.TRAVELER_ENTER_OFFERS:                 # b62 enter-offers (registered last)
        add(npc, [(xyz, tag)], SRC_ENTER)

    specs = dict(bss.merge_hub_into_inject_specs(bss.INJECT_SPECS) if testhub else bss.INJECT_SPECS)
    if testhub:
        # merge_hub_into_inject_specs EXCLUDES the R09 (random09a) swap key - svaera_plus_portals
        # applies build_hub_extra_specs()[R09_LVL_KEY] to the SV blood-cave swap blob instead. Fold
        # it in here so the build-free placement set matches what the arc-based gate sees for R09
        # (otherwise a re-added blood-cave-mouth NPC would be invisible to this gate).
        r09 = bss.build_hub_extra_specs().get(bss.R09_LVL_KEY, [])
        if r09:
            specs[bss.R09_LVL_KEY] = list(specs.get(bss.R09_LVL_KEY, [])) + list(r09)
    placed = defaultdict(set)
    for lvl, sl in specs.items():
        fn = lvl.replace('/', BS).split(BS)[-1].lower()
        for sp in sl:
            raw = bytes(sp) if isinstance(sp, (bytes, bytearray)) else bytes(sp[0])
            dl = raw.decode('latin1').lower()
            if any(kw in dl for kw in HUB_KW):
                placed[dl.replace('/', BS).split(BS)[-1]].add(fn)
    return routes, dict(placed)


def evaluate(routes, placed):
    """Pure invariant evaluation over route list + placement map. Returns list of (class, msg).
    Extracted so a dry-run can feed it the POST-FIX (routes, placed) and prove GATE PASS."""
    routes_by_npc = defaultdict(list)
    for r in routes:
        routes_by_npc[r["npc_short"]].append(r)

    fails = []
    order_of = {n: min(r["order"] for r in rs) for n, rs in routes_by_npc.items()}
    level_npcs = defaultdict(set)
    for n, lvs in placed.items():
        for L in lvs:
            level_npcs[L].add(n)

    def route_stolen(n, r, L):
        """A same-level, present, EARLIER-registered NPC that offers the same tag OR dest binds
        this route first (per-level 1-route-1-NPC ownership) -> r is MUTE for n."""
        for n2 in level_npcs[L]:
            if n2 == n or n2 not in routes_by_npc:
                continue
            if order_of[n2] >= order_of[n]:
                continue
            for r2 in routes_by_npc[n2]:
                if r2["tag"] == r["tag"] or r2["dest"] == r["dest"]:
                    return n2
        return None

    # Per-PLACED-NPC response check. An UNPLACED NPC with routes is NOT a clickable NPC, so it can
    # never be "mute" (its OnLevelLoad boat offers simply no-op with no entity to attach to); we do
    # not fault it (that was the round-1 error). We fault only NPCs a player can actually click.
    for n, lvs in sorted(placed.items()):
        my = routes_by_npc.get(n, [])
        if not my:
            fails.append(("G-ORPHAN", f"{n}: PLACED in {sorted(lvs)} but registers NO boat offer "
                                      f"-> a clickable NPC that does NOTHING when talked to."))
            continue
        if len(lvs) > 1:
            fails.append(("G-WARDEN", f"{n}: the SAME record is placed in {len(lvs)} levels "
                                      f"{sorted(lvs)} - one entity binds; the other {len(lvs)-1} "
                                      f"placements are MUTE (give each its own distinct record)."))
            continue
        L = next(iter(lvs))
        owned, stolen = [], []
        for r in my:
            thief = route_stolen(n, r, L)
            (stolen if thief else owned).append((r, thief))
        if not owned:
            r, thief = stolen[0]
            fails.append(("G-COLLISION",
                f"{L}: {n} is MUTE - its route (tag={r['tag']}, dest={r['dest']}) is already bound "
                f"by earlier-registered {thief} present in the SAME level. Talking to {n} does "
                f"nothing."))
        elif stolen:
            r, thief = stolen[0]
            fails.append(("G-COLLISION",
                f"{L}: {n} responds but loses menu entry tag={r['tag']} to earlier {thief} "
                f"(same-level route collision) - that destination is silently missing from "
                f"{n}'s menu."))

    # G-DEST: every route destination is a real teleport target
    for r in routes:
        if r["dest"] == (0, 0, 0):
            fails.append(("G-DEST", f"{r['npc_short']} tag={r['tag']}: destination is (0,0,0)."))

    # G-SOLE-SOURCE (b63): no PLACED NPC may have TRAVELER_ENTER_OFFERS as its only route source.
    # Enter-offers are appended LAST to the host step and the class has zero in-game confirmations;
    # they are only ever safe as a SECOND entry on an NPC that already owns a proven route. The
    # Warden of the Spartan Crypt shipped mute to Steam because it was sole-sourced this way.
    for n, lvs in sorted(placed.items()):
        my = routes_by_npc.get(n, [])
        if not my:
            continue                      # already reported by G-ORPHAN
        srcs = {r.get("src", "other") for r in my}
        if srcs == {SRC_ENTER}:
            tags = ", ".join(sorted(r["tag"] for r in my))
            fails.append(("G-SOLE-SOURCE",
                f"{n}: PLACED in {sorted(lvs)} and its ENTIRE menu ({tags}) comes from "
                f"TRAVELER_ENTER_OFFERS - the appended-last, never-in-game-confirmed trigger "
                f"class. An enter-offer may only be a SECOND entry on an NPC that already owns a "
                f"HELOS_HUB_TRAVEL / per-area-return route. Move this route into "
                f"HELOS_HUB_TRAVEL (this is the b63 silent-Warden bug)."))

    return fails


# ── b63 G-DIALOG-CHAIN ────────────────────────────────────────────────────────────────────────
# The full talk chain for every PLACED traveler: record -> quest -> loadable QUESTS window.
# ARZ_ROSTER_SOURCES documents WHERE each link is proven, so a reader can audit it without
# re-deriving the rosters.
def arz_record_roster():
    """Every NPC record the arz builder actually mints, normalized lowercase '\\' paths.
    A placed traveler whose record is NOT here would resolve to nothing in the shipped .arz."""
    import apply_svc_patches as asp
    roster = set()
    roster.add(_norm_rec(asp.PORTAL_MASTER_HELOS_NPC))          # Almyros
    for r in asp.TESTHUB_AREA_RETURN_NPCS:                      # 5 per-area returns
        roster.add(_norm_rec(r))
    for row in asp.HELOS_HUB_OUTBOUND:                          # 14 Helos travelers
        roster.add(_norm_rec(row[0]))
    for r in asp.HELOS_HUB_RETURNS:                             # 11 area returns (incl. the
        roster.add(_norm_rec(r))                                #   retired-but-kept Sparta donor)
    roster.add(_norm_rec(asp.WARDEN_SPARTA_CRYPT_DBR))          # the catacomb Warden clone
    return roster


def _norm_rec(p):
    p = p.decode('latin1') if isinstance(p, (bytes, bytearray)) else p
    return p.replace('/', BS).lower()


def host_quest_in_load_window(levels_arc=None):
    """(ok, detail) - is the travelers' host quest inside the engine's proven ~256-entry QUESTS
    load window? A quest registered past that window NEVER loads for any character (proven across
    5 custom-quest chars + vanilla saves; docs/QUEST_STATE_INJECT.md sec 2), so every boat trigger
    it carries would be dead and every traveler silent.

    BUILD-FREE proof: the host quest IS svaera_plus_portals.QUEST_INSERT_ANCHOR - the anchor the
    map's QUESTS rebuild splices the 4 SV questlines after, and which build_ordered_quest_list
    asserts stays in-window (`anchor_idx + 1 + k < 256`, plus `len(ordered) <= 256`). If the
    travelers' host quest ever stops being that anchor, this check goes red and the wave has to
    prove the new host's index by hand.
    BUILT-MAP proof (when levels_arc is given): read the map's QUESTS(0x1b) section and check the
    host quest's ACTUAL index."""
    import build_quest_files as bqf
    import svaera_plus_portals as spp
    host = bqf.HELOS_PORTAL_HOST_QUEST.lower()
    anchor = spp.QUEST_INSERT_ANCHOR.decode('latin1').replace('/', BS).lower()
    anchor_base = anchor.rsplit(BS, 1)[-1]
    if anchor_base != host:
        return False, (f'host quest {host!r} is NOT the QUESTS insert anchor {anchor_base!r} - '
                       f'its load-window index is unproven; prove it or move the triggers back '
                       f'onto the anchor quest')
    detail = f'host {host!r} == QUEST_INSERT_ANCHOR (spliced in-window by build_ordered_quest_list)'
    if levels_arc is None:
        return True, detail + ' [build-free]'
    try:
        idx, total = _quests_index_of(Path(levels_arc), host)
    except Exception as e:
        return True, detail + f' [built-map read skipped: {e}]'
    if idx is None:
        return False, f'host quest {host!r} is NOT registered in the map QUESTS section at all'
    if idx >= 256:
        return False, (f'host quest {host!r} is registered at QUESTS index {idx} of {total} - '
                       f'PAST the proven <=256 load window, so it never loads and every traveler '
                       f'it hosts is silent')
    return True, detail + f' [built map: index {idx} of {total}, in-window]'


def _quests_index_of(levels_arc, host_basename):
    """(index, total) of a quest basename in the built map's QUESTS(0x1b) section."""
    import struct as _struct
    from arc_patcher import ArcArchive
    from merge_levels_binary import parse_sections
    arc = ArcArchive.from_file(levels_arc)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = next(s for s in parse_sections(data) if s['type'] == 0x1b)
    d = data[sec['data_offset']:sec['data_offset'] + sec['size']]
    pos = 0
    n = _struct.unpack_from('<I', d, pos)[0]
    pos += 4
    for i in range(n):
        ln = _struct.unpack_from('<I', d, pos)[0]
        pos += 4
        name = d[pos:pos + ln].decode('latin1')
        pos += ln
        if name.replace('/', BS).lower().rsplit(BS, 1)[-1] == host_basename:
            return i, n
    return None, n


def evaluate_dialog_chain(routes, placed, levels_arc=None):
    """b63 G-DIALOG-CHAIN. For every PLACED traveler NPC prove all three links resolve:
    record (in the arz roster) -> quest (>=1 boat route, on the always-loaded host quest) ->
    window (that host quest inside the ~256-entry QUESTS load window).
    Returns [(class, msg)] exactly like evaluate()."""
    fails = []
    routes_by_npc = defaultdict(list)
    for r in routes:
        routes_by_npc[r["npc_short"]].append(r)
    roster = arz_record_roster()
    roster_short = {p.rsplit(BS, 1)[-1] for p in roster}

    for n, lvs in sorted(placed.items()):
        # LINK 1: RECORD - the .dbr the map places is actually minted into the shipped arz.
        if n not in roster_short:
            fails.append(("G-DIALOG-CHAIN",
                f"{n}: PLACED in {sorted(lvs)} but its record is minted by NO arz builder "
                f"(not in apply_svc_patches' NPC roster) - the shipped .arz has no such NPC, so "
                f"the placement resolves to nothing."))
            continue
        # LINK 2: QUEST - it owns >=1 boat route, and that route rides the always-loaded host.
        my = routes_by_npc.get(n, [])
        if not my:
            fails.append(("G-DIALOG-CHAIN",
                f"{n}: PLACED in {sorted(lvs)} with a real arz record but registers NO boat "
                f"route - clicking it opens nothing."))
            continue
        bad_host = sorted({r.get("host", "?") for r in my} - {HOST_QST})
        if bad_host:
            fails.append(("G-DIALOG-CHAIN",
                f"{n}: registers boat route(s) in {bad_host} instead of the always-loaded "
                f"{HOST_QST}. A new host quest needs its own QUESTS registration inside the "
                f"<=256 load window - prove it or move the triggers back onto {HOST_QST}."))

    # LINK 3: WINDOW - the host quest loads at all.
    ok, detail = host_quest_in_load_window(levels_arc)
    if not ok:
        fails.append(("G-DIALOG-CHAIN", f"QUESTS load window: {detail}"))
    return fails, detail


def report(fails, routes, placed, quests, levels, chain_detail=None):
    routes_by_npc = defaultdict(list)
    for r in routes:
        routes_by_npc[r["npc_short"]].append(r)
    print("=" * 96)
    print("gate_traveler_responds - hub boat-dialog RESPONSE invariants")
    print(f"  quests: {quests}")
    print(f"  levels: {levels}")
    print(f"  boat NPCs with routes: {len(routes_by_npc)}   placed boat NPCs: {len(placed)}   "
          f"total routes: {len(routes)}")
    n_enter = sum(1 for r in routes if r.get("src") == SRC_ENTER)
    print(f"  route sources: hub={sum(1 for r in routes if r.get('src') == SRC_HUB)}  "
          f"portal={sum(1 for r in routes if r.get('src') == SRC_PORTAL)}  "
          f"testhub_return={sum(1 for r in routes if r.get('src') == SRC_RETURN)}  "
          f"enter_offer={n_enter}")
    if chain_detail:
        print(f"  QUESTS load window: {chain_detail}")
    print("=" * 96)
    by_class = defaultdict(list)
    for cls, msg in fails:
        by_class[cls].append(msg)
    for cls in ["G-COLLISION", "G-WARDEN", "G-ORPHAN", "G-DEST",
                "G-SOLE-SOURCE", "G-DIALOG-CHAIN"]:
        msgs = by_class.get(cls, [])
        status = "PASS" if not msgs else f"FAIL ({len(msgs)})"
        print(f"\n[{status}] {cls}")
        for m in msgs:
            mark = "   <<<< SPARTA" if "sparta" in m.lower() else ""
            print(f"    - {m}{mark}")
    print("\n" + "=" * 96)
    if fails:
        print(f"GATE FAIL: {len(fails)} mute/invalid traveler condition(s) across "
              f"{len({c for c,_ in fails})} class(es).")
    else:
        print("GATE PASS: every placed hub traveler owns a bound, fire-able, unique route "
              "(no mute, no orphan, no dead, no warden, valid dests), draws it from a "
              "Will-confirmed trigger class, and its record -> quest -> load-window dialog "
              "chain fully resolves.")


def negtest():
    """b63 NEGATIVE TEST: plant each defect class into the spec-derived facts and prove the gate
    goes RED. A gate that has never been shown to fail is not evidence of anything. Exit 0 = every
    planted violation was caught AND the untouched baseline is green."""
    import copy
    ok = True

    def run(label, mutate, want_cls):
        nonlocal ok
        routes, placed = facts_from_specs(testhub=True)
        routes, placed = copy.deepcopy(routes), copy.deepcopy(placed)
        mutate(routes, placed)
        fails = evaluate(routes, placed)
        chain, _d = evaluate_dialog_chain(routes, placed)
        got = {c for c, _ in fails} | {c for c, _ in chain}
        hit = want_cls in got
        print(f"  [{'RED  OK' if hit else 'GREEN  MISS'}] {label:<58s} want={want_cls} got={sorted(got) or '(none)'}")
        ok = ok and hit

    print("=" * 96)
    print("gate_traveler_responds --negtest (b63): planted-violation battery")
    print("=" * 96)

    # POSITIVE CONTROL: untouched facts must be GREEN, else the negtest proves nothing.
    routes, placed = facts_from_specs(testhub=True)
    base = evaluate(routes, placed) + evaluate_dialog_chain(routes, placed)[0]
    print(f"  [{'GREEN OK' if not base else 'RED   MISS'}] positive control: untouched TESTHUB facts"
          f"{'' if not base else ' -> ' + str(base)}")
    ok = ok and not base

    def sole_source(routes, placed):
        """Re-create the EXACT shipped bug: the Warden's only route is an enter-offer."""
        for r in routes:
            if r["npc_short"] == "svc_warden_sparta_crypt.dbr":
                r["src"] = SRC_ENTER
    run("G-SOLE-SOURCE: Warden's whole menu is an enter-offer (THE b63 bug)",
        sole_source, "G-SOLE-SOURCE")

    def orphan_record(routes, placed):
        """A placed traveler whose record no arz builder mints."""
        placed["svc_helos_trav_ghost.dbr"] = {"startingfarmland06d.lvl"}
        routes.append(dict(order=999, step=0, npc=r"records\quests\svc_helos_trav_ghost.dbr",
                           npc_short="svc_helos_trav_ghost.dbr", tag="tagGhost",
                           dest=(1, 2, 3), src=SRC_HUB, host=HOST_QST))
    run("G-DIALOG-CHAIN link 1: placed NPC with no arz record",
        orphan_record, "G-DIALOG-CHAIN")

    def wrong_host(routes, placed):
        """A traveler whose route rides a quest other than the always-loaded host."""
        for r in routes:
            if r["npc_short"] == "svc_warden_sparta_crypt.dbr":
                r["host"] = "svc_brand_new_quest.qst"
    run("G-DIALOG-CHAIN link 2: route hosted on a non-always-loaded quest",
        wrong_host, "G-DIALOG-CHAIN")

    def no_route(routes, placed):
        """A placed traveler with a real record but zero boat routes."""
        keep = [r for r in routes if r["npc_short"] != "svc_warden_sparta_crypt.dbr"]
        routes[:] = keep
    run("G-ORPHAN: placed traveler registers no boat route at all",
        no_route, "G-ORPHAN")

    def double_place(routes, placed):
        placed["svc_warden_sparta_crypt.dbr"] = {"catacube02_floorlast.lvl", "maze03.lvl"}
    run("G-WARDEN: one record placed in two levels", double_place, "G-WARDEN")

    def steal(routes, placed):
        """An earlier-registered NPC in the SAME level binds the Warden's tag first."""
        routes.insert(0, dict(order=-1, step=0, npc=r"records\quests\svc_testhub_thief.dbr",
                              npc_short="svc_testhub_thief.dbr", tag="tagSVCEnterSpartaCrypt",
                              dest=(-5596, -2, -1410), src=SRC_HUB, host=HOST_QST))
        placed["svc_testhub_thief.dbr"] = {"catacube02_floorlast.lvl"}
    run("G-COLLISION: same-level earlier NPC steals the Warden's route", steal, "G-COLLISION")

    def zero_dest(routes, placed):
        for r in routes:
            if r["npc_short"] == "svc_warden_sparta_crypt.dbr":
                r["dest"] = (0, 0, 0)
    run("G-DEST: route destination is (0,0,0)", zero_dest, "G-DEST")

    print("=" * 96)
    print("NEGTEST PASS: every planted violation was caught and the baseline is green."
          if ok else "NEGTEST FAIL: at least one planted violation slipped through (see MISS).")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quests", default=str(DEP / "Quests.arc"))
    ap.add_argument("--levels", default=str(DEP / "Levels.arc"))
    ap.add_argument("--specs", action="store_true",
                    help="build-free: derive routes+placements from the REAL tooling tables "
                         "(TESTHUB build) instead of reading built .arc files")
    ap.add_argument("--canonical", action="store_true",
                    help="with --specs: derive the CANONICAL build (INJECT_SPECS) not the TESTHUB one")
    ap.add_argument("--negtest", action="store_true",
                    help="b63: plant each defect class and prove the gate goes RED")
    args = ap.parse_args()
    if args.negtest:
        return negtest()
    if args.specs:
        routes, placed = facts_from_specs(testhub=not args.canonical)
        which = "canonical" if args.canonical else "TESTHUB"
        quests = levels = f"(spec-derived {which} tables, build-free)"
        chain_fails, chain_detail = evaluate_dialog_chain(routes, placed)
    else:
        routes = load_routes(Path(args.quests))
        placed = load_placements(Path(args.levels))
        quests, levels = args.quests, args.levels
        chain_fails, chain_detail = evaluate_dialog_chain(routes, placed, levels_arc=args.levels)
    fails = evaluate(routes, placed) + chain_fails
    report(fails, routes, placed, quests, levels, chain_detail)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
