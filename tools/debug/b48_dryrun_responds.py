"""b48 round-2 DRY-RUN: prove the full SPARTA-MUTE fix takes gate_traveler_responds FAIL -> PASS.

No heavy build. Loads the DEPLOYED route+placement facts, applies each fix transform (each mirrors
an exact code edit / patch-spec item), and re-runs the gate's pure evaluate() to show every mute
class resolved.

Fix parts proven:
  1. DE-DUP portal_master from the TESTHUB Helos plaza  [IMPLEMENTED: merge_hub_into_inject_specs]
     -> tied to the REAL code: calls merge_hub_into_inject_specs(INJECT_SPECS) and asserts
        portal_master_helos is gone from the plaza + the 11 dedicated travelers remain.
     -> fixes G-COLLISION (garden/secret/sparta/uber).
  2. DROP the UNPLACED svc_testhub_master trigger       [IMPLEMENTED: build_quest_files]
     -> cleanup (its 7 offers are harmless no-ops under per-level ownership; kept tidy).
  3. SPLIT svc_testhub_return into 5 distinct per-area records [PATCH SPEC for b39 map lane]
     -> fixes G-WARDEN.
  4. RETIRE svc_testhub_master_cave placement (or wire it)    [PATCH SPEC for b39 map lane]
     -> fixes G-ORPHAN.
"""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
import build_section_surgery as B
import gate_traveler_responds as G

DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Resources")
BS = chr(92)


def npc_short(spec):
    b = bytes(spec) if isinstance(spec, (bytes, bytearray)) else bytes(spec[0])
    return b.decode("latin1").replace("/", BS).split(BS)[-1].lower()


def main():
    print("#" * 96)
    print("# b48 round-2 dry-run: gate_traveler_responds FAIL -> PASS under the full fix")
    print("#" * 96)

    # ---- BEFORE: the deployed ground truth -------------------------------------------------
    routes = G.load_routes(DEP / "Quests.arc")
    placed = {k: set(v) for k, v in G.load_placements(DEP / "Levels.arc").items()}
    before = G.evaluate(routes, list_placed(placed))
    classes_before = sorted({c for c, _ in before})
    print(f"\n[BEFORE] deployed set: GATE {'FAIL' if before else 'PASS'} "
          f"({len(before)} conditions across {classes_before})")
    assert before, "expected the deployed set to FAIL the gate"
    assert any(c == "G-COLLISION" and "sparta" in m.lower() for c, m in before), \
        "expected the deployed set to FAIL specifically on the Sparta route-collision"
    print("  -> confirmed: FAILS on the Sparta in-level route collision (Will's bug).")

    # ---- FIX 1: de-dup portal_master (tie to the REAL merge_hub_into_inject_specs) ----------
    merged_plaza = B.merge_hub_into_inject_specs(B.INJECT_SPECS)[B.HELOS_HOST_KEY]
    plaza_names = [npc_short(s) for s in merged_plaza]
    assert not any("portal_master_helos" in n for n in plaza_names), \
        "merge_hub_into_inject_specs must drop portal_master from the TESTHUB plaza"
    assert sum(n.startswith("svc_helos_trav_") for n in plaza_names) >= 11, \
        "the 11 dedicated travelers must remain in the plaza"
    print(f"\n[FIX 1] merge_hub_into_inject_specs() -> plaza has {len(plaza_names)} NPCs, "
          f"portal_master_helos REMOVED, {sum(n.startswith('svc_helos_trav_') for n in plaza_names)} "
          f"dedicated travelers kept (REAL code).")
    # reflect in placement facts: portal_master no longer placed in the plaza level
    HELOS = "StartingFarmland06D.lvl"
    placed["portal_master_helos.dbr"].discard(HELOS)
    if not placed["portal_master_helos.dbr"]:
        del placed["portal_master_helos.dbr"]

    # ---- FIX 2: drop the dead svc_testhub_master offers (build_quest_files) -----------------
    routes = [r for r in routes if r["npc_short"] != "svc_testhub_master.dbr"]
    print("[FIX 2] dropped the 7 dead svc_testhub_master offers (build_quest_files).")

    # ---- FIX 3: split svc_testhub_return into 5 distinct per-area records (b39 patch spec) --
    # each SV-area gets its own return NPC (1 placement, carrying the 2 return routes), matching
    # the b37 precedent (the 6 new-area returns are already distinct). Level -> new record.
    SPLIT = {
        "GardenofMerchants.lvl":  "svc_area_return_garden.dbr",
        "DarkForestEnter.lvl":    "svc_area_return_secret.dbr",
        "crypt_floor1.lvl":       "svc_area_return_uber.dbr",
        "SpartaCryptLevel2.lvl":  "svc_area_return_sparta.dbr",
        "boss_arena.lvl":         "svc_area_return_bossarena.dbr",
    }
    ret_routes = [r for r in routes if r["npc_short"] == "svc_testhub_return.dbr"]
    old_levels = set(placed.pop("svc_testhub_return.dbr", set()))
    routes = [r for r in routes if r["npc_short"] != "svc_testhub_return.dbr"]
    order = max((r["order"] for r in routes), default=0)
    for lvl, newrec in SPLIT.items():
        placed[newrec] = {lvl}
        for rr in ret_routes:
            order += 1
            routes.append(dict(order=order, step=rr["step"], npc="records\\quests\\" + newrec,
                               npc_short=newrec, tag=rr["tag"], dest=rr["dest"]))
    assert old_levels == set(SPLIT), f"split must cover exactly the 5 return levels: {old_levels}"
    print(f"[FIX 3] split svc_testhub_return (was placed x{len(old_levels)}) into 5 distinct "
          f"per-area return records, 1 placement each.")

    # ---- FIX 4: retire the svc_testhub_master_cave orphan placement (b39 patch spec) --------
    placed.pop("svc_testhub_master_cave.dbr", None)
    print("[FIX 4] retired the svc_testhub_master_cave orphan placement.")

    # ---- AFTER: re-run the gate ------------------------------------------------------------
    after = G.evaluate(routes, list_placed(placed))
    print("\n" + "=" * 96)
    G.report(after, routes, {k: v for k, v in placed.items()}, "(fixed Quests)", "(fixed Levels)")
    print("=" * 96)
    if after:
        print(f"\nDRY-RUN RESULT: STILL FAILING ({len(after)}) - fix incomplete.")
        return 1
    print("\nDRY-RUN RESULT: GATE PASS after the full fix. Every MUTE class resolved:")
    print("  G-COLLISION (garden/secret/sparta/uber outbound) -> FIX 1 de-dup portal_master [PRIMARY]")
    print("  G-WARDEN (svc_testhub_return x5 -> 4 mute returns) -> FIX 3 split into 5 distinct records")
    print("  G-ORPHAN (svc_testhub_master_cave)                -> FIX 4 retire orphan placement")
    print("  (FIX 2 dropping the UNPLACED svc_testhub_master is cleanup - harmless no-op offers,")
    print("   not a mute cause under per-level ownership; removing them keeps the rig tidy.)")
    return 0


def list_placed(placed):
    """gate.evaluate expects {npc -> set(levels)}; pass a shallow copy with set values."""
    return {k: set(v) for k, v in placed.items()}


if __name__ == "__main__":
    raise SystemExit(main())
