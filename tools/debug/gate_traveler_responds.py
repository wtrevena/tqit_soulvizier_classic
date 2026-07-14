#!/usr/bin/env python3
"""gate_traveler_responds.py - PERMANENT travel-invariant gate (b48, 2026-07-13).

Asserts that EVERY Helos-hub traveler NPC actually RESPONDS: it has a bound, fire-able
talk-dialog (Action_BoatDialog) trigger with a valid destination, is placed exactly once,
and the total boat-offer pressure stays within the engine's registry budget. Catches the
b48 "SPARTA-MUTE" class (clicking a hub traveler does NOTHING) and its siblings.

WHY (RCA, docs/reports/b48_sparta_mute.md): Action_BoatDialog offers register into a
BOUNDED engine registry, in the order the always-loaded sv_commonmechanics OnLevelLoad
triggers fire. The base game never registers more than ~5 boat offers anywhere; the SVC
hub registered 30. Offers that (a) target an UNPLACED npc [dead weight / poison], (b)
name a record placed in >1 level [warden law: only one entity binds], or (c) push the
per-load registry past its capacity, silently fail to attach -> the NPC is placed-but-MUTE.

INVARIANTS (hard FAIL):
  G1 NO DEAD OFFER   - every boat-offer target NPC is placed >= 1x (else the offer is dead
                       weight that poisons/overflows the registry; e.g. svc_testhub_master).
  G2 NO WARDEN-MUTE  - every boat-offer target NPC is placed in EXACTLY ONE level (a record
                       in >1 level binds to one entity, the rest go mute; e.g.
                       svc_testhub_return placed 5x).
  G3 NO ORPHAN NPC   - every PLACED hub NPC has >= 1 boat offer (placed-but-triggerless =
                       clickable-but-silent; e.g. svc_testhub_master_cave).
  G4 DEST VALID      - every offer's destination is non-zero and its NPC record exists in arz.
INVARIANT (WARN, tune to FAIL once the runtime cap is pinned - Will test):
  G5 OFFER BUDGET    - total registered boat offers <= BUDGET_TOTAL, and the max offers that
                       ATTACH in any single level <= BUDGET_PER_LEVEL. The overflow is the
                       Sparta root cause; base game stays < ~5.

Runs against BUILT/DEPLOYED arcs (authoritative). Default = the deployed DEV set. The build
gate should point --arz/--quests/--levels at the freshly-built TESTHUB artifacts.

Exit 0 = PASS (0 hard fails), 1 = FAIL. Wire into the travel-invariants gate family
(alongside gate_travel_npc_invariants.py) so no future hub build ships a mute traveler.
"""
import sys, os, struct, argparse
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
import qst_format as qf
from arc_patcher import ArcArchive
from arz_patcher import ArzDatabase
import survey_uberboss_spots as S
from contracts_map import parse_blob_sections

BS = chr(92)
VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}
# NPC path substrings that identify a hub travel NPC (offer target / placement).
HUB_KW = ('svc_helos_trav_', 'svc_area_return_', 'svc_testhub_master', 'svc_testhub_return',
          'portal_master_helos')
# Engine boat-offer budget. base game < ~5; deployed hub = 30 (overflowed). These are
# CONSERVATIVE placeholders pending Will's in-game confirmation of the true cap; once pinned,
# flip G5 to a hard FAIL and set the real number. (Env override: SVC_BOAT_BUDGET_TOTAL/_LEVEL.)
BUDGET_TOTAL = int(os.environ.get("SVC_BOAT_BUDGET_TOTAL", "16"))
BUDGET_PER_LEVEL = int(os.environ.get("SVC_BOAT_BUDGET_LEVEL", "12"))

DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV")
DEF_ARZ = DEV / "Database" / "SoulvizierClassicDEV.arz"
DEF_QUESTS = DEV / "Resources" / "Quests.arc"
DEF_LEVELS = DEV / "Resources" / "Levels.arc"

def s32(v):
    return struct.unpack("<i", struct.pack("<I", v))[0] if isinstance(v, int) else v

def _blocks(items):
    return [it[1] for it in items if it[0] == "block"]

def quest_offers(quests_arc):
    """[(npc_lower, x, y, z, tag)] in engine registration order, from sv_commonmechanics.qst."""
    arc = ArcArchive.from_file(quests_arc)
    data = arc.get_file("sv_commonmechanics.qst")
    if data is None:
        raise SystemExit("gate_traveler_responds: sv_commonmechanics.qst not in " + str(quests_arc))
    tree = qf.parse(data)
    sbl = _blocks(tree[1])
    offers = []
    def action_entries(cont):
        out = []; pend = None
        for it in cont:
            if it[0] == "field" and it[1] == "actionClassName":
                pend = it[2][1]
            elif it[0] == "block" and pend is not None:
                d = {x[1]: x[2][1] for x in it[1] if x[0] == "field"}
                out.append((pend, d)); pend = None
        return out
    n = len(sbl) // 3
    for s in range(n):
        cont = sbl[3*s + 1]
        cbl = _blocks(cont)
        i = 0
        while i + 2 < len(cbl) + 1 and i + 2 <= len(cbl):
            act = cbl[i+2] if i+2 < len(cbl) else None
            if act is None:
                break
            for an, ad in action_entries(act):
                if an == "Action_BoatDialog":
                    offers.append((ad.get("npc", "").lower(), s32(ad.get("x", 0)),
                                   s32(ad.get("y", 0)), s32(ad.get("z", 0)), ad.get("tag", "")))
            i += 3
    return offers

def _all_instances(blob, base):
    for t, d in parse_blob_sections(blob):
        if t != 0x05:
            continue
        pos = 0
        nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
        strings = []
        for _ in range(nstr):
            ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
            strings.append(d[pos:pos+ln]); pos += ln
        ninst = struct.unpack_from('<I', d, pos)[0]; pos += 4
        out = []
        for _ in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            dbr = (strings[sid] if sid < len(strings) else b'?').decode('latin1')
            out.append(dbr.lower())
            pos += base + (16 if flags != 0 else 0)
        return out
    return []

def map_placements(levels_arc):
    """npc_lower -> [level_name] for every hub-NPC 0x05 placement."""
    data, levels = S.load_world(levels_arc)
    placed = defaultdict(list)
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        base = VER_BASE.get(blob[3], 72)
        try:
            insts = _all_instances(blob, base)
        except Exception:
            continue
        seen_here = set()
        for dbr in insts:
            if any(kw in dbr for kw in HUB_KW):
                placed[dbr].append(lv['fname'])
    return placed

def norm(p):
    return p.replace('/', BS).lower()

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--arz', default=str(DEF_ARZ))
    ap.add_argument('--quests', default=str(DEF_QUESTS))
    ap.add_argument('--levels', default=str(DEF_LEVELS))
    args = ap.parse_args(argv)

    offers = quest_offers(Path(args.quests))
    placed = map_placements(Path(args.levels))
    arz_names = set(n.lower() for n in ArzDatabase.from_arz(Path(args.arz)).record_names())

    # offer target NPCs (distinct) + per-level attach count
    offer_npcs = {}
    for idx, (npc, x, y, z, tag) in enumerate(offers):
        offer_npcs.setdefault(npc, []).append((idx, x, y, z, tag))
    # per-level attach = for each level, how many offer NPCs are placed there
    level_attach = defaultdict(int)
    for npc, levs in placed.items():
        if npc in offer_npcs:
            for lv in set(levs):
                level_attach[lv] += 1

    fails = []
    warns = []
    print("=" * 96)
    print(f"gate_traveler_responds: {len(offers)} boat offers, {len(offer_npcs)} distinct offer NPCs, "
          f"{len(placed)} placed hub NPCs")
    print("=" * 96)

    # G1 NO DEAD OFFER
    dead = [npc for npc in offer_npcs if not placed.get(npc)]
    for npc in dead:
        fails.append(f"G1 DEAD-OFFER: {npc.split(BS)[-1]} receives {len(offer_npcs[npc])} boat offer(s) "
                     f"but is placed in NO level -> dead weight (poisons/overflows the registry)")
    print(f"  G1 no-dead-offer: {len(dead)} dead offer NPC(s)" + (" FAIL" if dead else " ok"))

    # G2 NO WARDEN-MUTE
    warden = [(npc, sorted(set(placed[npc]))) for npc in offer_npcs
              if len(set(placed.get(npc, []))) > 1]
    for npc, levs in warden:
        fails.append(f"G2 WARDEN-MUTE: {npc.split(BS)[-1]} placed in {len(levs)} levels "
                     f"{[l.split(BS)[-1] for l in levs]} -> only ONE binds, the rest are mute")
    print(f"  G2 no-warden-mute: {len(warden)} multi-level offer NPC(s)" + (" FAIL" if warden else " ok"))

    # G3 NO ORPHAN PLACEMENT
    orphan = [npc for npc in placed if npc not in offer_npcs]
    for npc in orphan:
        fails.append(f"G3 ORPHAN-PLACEMENT: {npc.split(BS)[-1]} placed "
                     f"{[l.split(BS)[-1] for l in placed[npc]]} but has NO boat offer -> "
                     f"clickable-but-silent (mute)")
    print(f"  G3 no-orphan: {len(orphan)} placed-but-triggerless NPC(s)" + (" FAIL" if orphan else " ok"))

    # G4 DEST VALID + record exists
    badd = 0
    for npc, offs in offer_npcs.items():
        if npc not in arz_names:
            fails.append(f"G4 NO-ARZ: offer target {npc.split(BS)[-1]} has no record in the arz")
            badd += 1
        for (idx, x, y, z, tag) in offs:
            if (x, y, z) == (0, 0, 0):
                fails.append(f"G4 BAD-DEST: {npc.split(BS)[-1]} offer '{tag}' -> (0,0,0)")
                badd += 1
    print(f"  G4 dest-valid + arz: {badd} bad" + (" FAIL" if badd else " ok"))

    # G5 OFFER BUDGET (WARN)
    total = len(offers)
    worst_lv = max(level_attach.items(), key=lambda kv: kv[1]) if level_attach else ("-", 0)
    over_total = total > BUDGET_TOTAL
    over_level = worst_lv[1] > BUDGET_PER_LEVEL
    if over_total:
        warns.append(f"G5 BUDGET(total): {total} boat offers registered > budget {BUDGET_TOTAL} "
                     f"(base game < ~5). Offers past the engine cap silently go mute.")
    if over_level:
        warns.append(f"G5 BUDGET(per-level): {worst_lv[1]} offers attach in "
                     f"{worst_lv[0].split(BS)[-1]} > budget {BUDGET_PER_LEVEL}.")
    print(f"  G5 offer-budget: total={total} (budget {BUDGET_TOTAL}); "
          f"worst level attach={worst_lv[1]} in {worst_lv[0].split(BS)[-1]} (budget {BUDGET_PER_LEVEL})"
          + ("  WARN" if (over_total or over_level) else "  ok"))

    print("=" * 96)
    if warns:
        print("WARNINGS (G5 - tune to hard-fail once the runtime cap is pinned):")
        for w in warns:
            print("  ! " + w)
    if fails:
        print(f"FAIL ({len(fails)} hard invariant violation(s)):")
        for f in fails:
            print("  X " + f)
        return 1
    print("PASS: every hub traveler has a bound, single-placed, valid-destination talk-dialog.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
