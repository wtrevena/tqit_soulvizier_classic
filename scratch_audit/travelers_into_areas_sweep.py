"""TRAVELERS-INTO-AREAS reachability sweep (read-only).

For every placed in-world return NPC (svc_area_return_* + svc_testhub_return_*) in the
deployed TESTHUB map, ground-truth whether the area it sits at gates a SEPARATE deeper
SV level that is currently sealed / Helos-hub-only (=> needs an "enter" offer) vs a
same-level walk-to-the-boss area (=> no offer). Inbound reachability is measured the same
way the athens RCA measured the crypt: count how many OTHER levels' 0x14 portal payloads
reference the candidate area's level GUID (0 => sealed; only the Helos boat-dialog reaches).

Usage: py scratch_audit/travelers_into_areas_sweep.py
"""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
from contracts_map import parse_blob_sections

VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}
# local/ is gitignored (not copied into the worktree); read the shared main-repo map.
MAP = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged_TESTHUB.arc")

# in-world return NPC -> (host-level fname substring, the deeper area it *might* gate).
# "same-level" means the boss/content walks in the SAME host level (no separate sealed level).
RETURN_NPCS = {
    "svc_area_return_sparta":     ("catacube02_floorlast", "spartacryptlevel2"),
    "svc_area_return_uber":       ("maze03",               "uberdungeon/crypt_floor1"),
    "svc_area_return_dorus":      ("medea_templeug_tomb03", "SAME-LEVEL (Kroisos in Tomb03)"),
    "svc_area_return_tantalus":   ("styx_swampborder_01",  "SAME-LEVEL (Tantalus)"),
    "svc_area_return_charon":     ("styx_riveredge_01",    "SAME-LEVEL/continent (Golden Bough)"),
    "svc_area_return_mnemophage": ("mnemosyne01",          "SAME-LEVEL (Mnemophage)"),
    "svc_area_return_ephialtes":  ("stonecity_exit01",     "SAME-LEVEL (Ephialtes)"),
    "svc_area_return_warband":    ("drxfirstxistion_connection", "SAME-LEVEL (Enslaver)"),
    "svc_area_return_devourer":   ("drxbc2",               "SAME-LEVEL (Toxeus Devourer)"),
    "svc_area_return_vashkarr":   ("random05a",            "SAME-LEVEL (Vashkarr)"),
    "svc_area_return_obsidian":   ("tombobs02",            "SAME-LEVEL (roulette wardens+brood)"),
    "svc_testhub_return_garden":  ("gardenofmerchants",    "DESTINATION (garden interior)"),
    "svc_testhub_return_secret":  ("darkforestenter",      "murderbossroom (crow bosses)"),
    "svc_testhub_return_uber":    ("uberdungeon/crypt_floor1", "IS the deep area (stranded interior)"),
    "svc_testhub_return_sparta":  ("spartacryptlevel2",    "IS the deep area (stranded interior)"),
    "svc_testhub_return_bossarena": ("boss_arena",         "SAME-LEVEL (arena dais)"),
}

# candidate "deeper areas" to measure inbound reachability for (by fname substring).
CANDIDATES = ["spartacryptlevel2", "uberdungeon/crypt_floor1", "murderbossroom",
              "gardenofmerchants", "darkforestenter", "maze03",
              "catacube02_floorlast"]


def load_world(path):
    import survey_uberboss_spots as S
    return S.load_world(path)


def main():
    print(f"MAP: {MAP}")
    data, levels = load_world(str(MAP))
    print(f"levels in index: {len(levels)}\n")

    by_sub = {}          # fname substring lookup -> level dict (first match)
    guid_of = {}         # fname-lower -> guid bytes
    fname_of_guid = {}   # guid hex -> fname
    for lv in levels:
        fn = lv['fname'].replace('\\', '/').lower()
        guid_of[fn] = lv['guid']
        fname_of_guid[lv['guid'].hex()] = lv['fname']

    def find_level(sub):
        for lv in levels:
            if sub in lv['fname'].replace('\\', '/').lower():
                return lv
        return None

    # ---- Part A: resolve candidate GUIDs + count INBOUND 0x14 references map-wide ----
    print("=" * 96)
    print("PART A - INBOUND PORTAL REACHABILITY (how many OTHER levels' 0x14 payloads name the area GUID)")
    print("=" * 96)
    cand_guid = {}
    for sub in CANDIDATES:
        lv = find_level(sub)
        if lv is None:
            print(f"  [{sub:32s}] *** NOT IN INDEX ***")
            continue
        cand_guid[sub] = lv['guid']
        print(f"  [{sub:32s}] guid={lv['guid'].hex()} corner={lv['corner']}")
    print()

    # scan every level's 0x14 payloads for each candidate guid (exclude the level itself)
    inbound = {sub: [] for sub in cand_guid}
    for lv in levels:
        fn = lv['fname'].replace('\\', '/')
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        for t, d in parse_blob_sections(blob):
            if t != 0x14:
                continue
            for sub, g in cand_guid.items():
                if g == lv['guid']:
                    continue  # a level referencing its own guid isn't an inbound portal
                if g in d:
                    inbound[sub].append(fn)
    for sub in cand_guid:
        locs = inbound[sub]
        verdict = "SEALED (0 inbound portals)" if not locs else f"reachable via {len(locs)} inbound portal-level(s)"
        print(f"  [{sub:32s}] {verdict}")
        for fn in locs:
            print(f"        <- {fn}")
    print()

    # ---- Part B: per return-NPC verdict ----
    print("=" * 96)
    print("PART B - PER RETURN-NPC: does it gate a SEPARATE SEALED/hub-only level? (enter-offer needed?)")
    print("=" * 96)
    for npc, (host_sub, target) in RETURN_NPCS.items():
        host = find_level(host_sub)
        host_fn = host['fname'] if host else "*** host not found ***"
        # is target a separate level from host?
        sep = None
        if target.startswith(("spartacryptlevel2", "uberdungeon", "murderbossroom")):
            tsub = target.split()[0]
            tlv = find_level(tsub)
            if tlv is not None:
                inb = len(inbound.get(tsub, []))
                sep = f"target level {tlv['fname']}: inbound_portals={inb}"
        need = "ENTER-OFFER" if target.startswith(("spartacryptlevel2", "uberdungeon")) else "-"
        print(f"\n  {npc}")
        print(f"      host       : {host_fn}")
        print(f"      target area: {target}")
        if sep:
            print(f"      separation : {sep}")
        print(f"      -> {need}")


if __name__ == "__main__":
    main()
