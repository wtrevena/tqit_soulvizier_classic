"""b48 round 3 DRY-RUN: prove gate_traveler_responds goes FAIL (deployed) -> PASS (implemented fix).

No heavy build. BEFORE = the DEPLOYED DEV set's real route+placement facts (the set Will is clicking)
-> the gate FAILS on the Sparta in-level route collision + the svc_testhub_return warden + the
svc_testhub_master_cave orphan. AFTER = gate_traveler_responds.facts_from_specs(), which derives the
POST-FIX facts from the REAL tooling tables now on THIS branch:
  - merge_hub_into_inject_specs de-dups the canonical Almyros from the TESTHUB plaza   [round 2]
  - the 5 warden-split per-area return records + their 2-port triggers + placements    [round 3]
    (apply_svc_patches / build_quest_files / build_section_surgery)
  - the svc_testhub_master_cave orphan placement is retired                            [round 3]
Because AFTER reads the REAL code (not a hand-simulated split), a PASS here proves the SHIPPED tables
are mute-free. This is what gate_travel_npc_invariants.check_responds() runs in the battery.
"""
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
import gate_traveler_responds as G

DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Resources")


def main():
    print("#" * 96)
    print("# b48 round 3 dry-run: gate_traveler_responds FAIL (deployed) -> PASS (implemented fix)")
    print("#" * 96)

    # ---- BEFORE: the DEPLOYED ground truth (the exact set Will is clicking) ------------------
    routes = G.load_routes(DEP / "Quests.arc")
    placed = G.load_placements(DEP / "Levels.arc")
    before = G.evaluate(routes, placed)
    cls_before = sorted({c for c, _ in before})
    print(f"\n[BEFORE] deployed DEV set: GATE {'FAIL' if before else 'PASS'} "
          f"({len(before)} conditions across {cls_before})")
    assert before, "expected the deployed set to FAIL the gate"
    assert any(c == "G-COLLISION" and "sparta" in m.lower() for c, m in before), \
        "expected the deployed set to FAIL on the Sparta in-level route collision (Will's bug)"
    assert any(c == "G-WARDEN" and "svc_testhub_return" in m.lower() for c, m in before), \
        "expected the deployed set to FAIL on the svc_testhub_return warden (placed x5)"
    assert any(c == "G-ORPHAN" and "master_cave" in m.lower() for c, m in before), \
        "expected the deployed set to FAIL on the svc_testhub_master_cave orphan"
    for cls, msg in before:
        print(f"    {cls}: {msg[:108]}")
    print("  -> confirmed: FAILS on the Sparta collision + svc_testhub_return warden + cave orphan.")

    # ---- AFTER: the REAL implemented fix (facts spec-derived from THIS branch's tooling tables) ----
    routes2, placed2 = G.facts_from_specs(testhub=True)
    after = G.evaluate(routes2, placed2)
    print("\n" + "=" * 96)
    G.report(after, routes2, placed2,
             "(real tooling tables, build-free)", "(real tooling tables, build-free)")
    print("=" * 96)
    if after:
        print(f"\nDRY-RUN RESULT: STILL FAILING ({len(after)}) - fix incomplete.")
        return 1
    print("\nDRY-RUN RESULT: GATE PASS after the implemented fix. Every MUTE class resolved:")
    print("  G-COLLISION (garden/secret/sparta/uber outbound) -> DE-DUP the canonical Almyros from the")
    print("     TESTHUB plaza (merge_hub_into_inject_specs) so each dedicated traveler owns its route.")
    print("  G-WARDEN (svc_testhub_return x5 -> 4 mute returns) -> WARDEN-SPLIT into 5 distinct per-area")
    print("     records (svc_testhub_return_{garden,secret,uber,sparta,bossarena}), each placed once,")
    print("     each with its own 2-port trigger. [round 3, IMPLEMENTED in the arz/quests/map tooling]")
    print("  G-ORPHAN (svc_testhub_master_cave placed, no trigger) -> RETIRE the placement. [round 3]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
