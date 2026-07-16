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
HUB_KW = ('svc_helos_trav', 'svc_area_return', 'svc_testhub', 'portal_master_helos')
HOST_QST = "sv_commonmechanics.qst"


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


def load_routes(quests_arc):
    """Ordered list of route dicts from sv_commonmechanics step 1, in registration order:
    {order, npc(lower), npc_short(lower), tag, dest(x,y,z)}."""
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
            for an, d in _entries(cbl[idx + 2]):
                if an == "Action_BoatDialog":
                    npc = d.get("npc", "")
                    routes.append(dict(
                        order=order, step=s,
                        npc=npc.lower(), npc_short=npc.split(BS)[-1].lower(),
                        tag=d.get("tag", ""),
                        dest=(s32(d.get("x", 0)), s32(d.get("y", 0)), s32(d.get("z", 0)))))
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

    def add(npc, dests):
        nonlocal order
        short = npc.replace('/', BS).split(BS)[-1].lower()
        for xyz, tag in dests:
            # DESTS tables already hold SIGNED world coords (the arc path stores them unsigned and
            # s32-decodes on read; here they are native signed, so use them as-is).
            routes.append(dict(order=order, step=0, npc=npc.lower(), npc_short=short,
                               tag=tag, dest=tuple(int(v) for v in xyz)))
            order += 1

    add(bqf.HELOS_PORTAL_NPC, bqf.HELOS_PORTAL_DESTS)               # Almyros 4-dest (trig 1)
    for npc in bqf.TESTHUB_AREA_RETURN_NPCS:                        # per-area returns (2 each)
        # b62 TRAVELERS-INTO-AREAS: sparta/uber override to return-to-origin; the rest keep the
        # shared Helos+BloodCave menu (see build_quest_files.TESTHUB_RETURN_DESTS_BY_NPC).
        dests = bqf.TESTHUB_RETURN_DESTS_BY_NPC.get(npc, bqf.TESTHUB_RETURN_DESTS)
        add(npc, dests)
    for npc, xyz, tag in bqf.HELOS_HUB_TRAVEL:                      # the 25-record hub (1 each)
        add(npc, [(xyz, tag)])
    for npc, xyz, tag in bqf.TRAVELER_ENTER_OFFERS:                 # b62 enter-offers (registered last)
        add(npc, [(xyz, tag)])

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

    return fails


def report(fails, routes, placed, quests, levels):
    routes_by_npc = defaultdict(list)
    for r in routes:
        routes_by_npc[r["npc_short"]].append(r)
    print("=" * 96)
    print("gate_traveler_responds - hub boat-dialog RESPONSE invariants")
    print(f"  quests: {quests}")
    print(f"  levels: {levels}")
    print(f"  boat NPCs with routes: {len(routes_by_npc)}   placed boat NPCs: {len(placed)}   "
          f"total routes: {len(routes)}")
    print("=" * 96)
    by_class = defaultdict(list)
    for cls, msg in fails:
        by_class[cls].append(msg)
    for cls in ["G-COLLISION", "G-WARDEN", "G-ORPHAN", "G-DEST"]:
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
              "(no mute, no orphan, no dead, no warden, valid dests).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quests", default=str(DEP / "Quests.arc"))
    ap.add_argument("--levels", default=str(DEP / "Levels.arc"))
    ap.add_argument("--specs", action="store_true",
                    help="build-free: derive routes+placements from the REAL tooling tables "
                         "(TESTHUB build) instead of reading built .arc files")
    ap.add_argument("--canonical", action="store_true",
                    help="with --specs: derive the CANONICAL build (INJECT_SPECS) not the TESTHUB one")
    args = ap.parse_args()
    if args.specs:
        routes, placed = facts_from_specs(testhub=not args.canonical)
        which = "canonical" if args.canonical else "TESTHUB"
        quests = levels = f"(spec-derived {which} tables, build-free)"
    else:
        routes = load_routes(Path(args.quests))
        placed = load_placements(Path(args.levels))
        quests, levels = args.quests, args.levels
    fails = evaluate(routes, placed)
    report(fails, routes, placed, quests, levels)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
