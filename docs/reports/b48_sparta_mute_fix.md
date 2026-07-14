# b48 SPARTA-MUTE - integration guide (apply onto `main`, post-b39-merge)

The full fix is **IMPLEMENTED on `feat/b48-sparta-mute`** (round 3), not just spec'd. This doc is the
**integrator's guide**: what the branch changes, how it cherry-picks onto `main`, and the two things
the integrator must do that b48 could not (canonical map rebuild + reconcile main's 14-traveler
roster). RCA + evidence: `b48_sparta_mute.md`.

**Root cause (one line):** two independent mute classes in the Helos hub -
1. *Route collision* - in the TESTHUB plaza the canonical Almyros (`portal_master_helos`, boat trig1)
   and the dedicated `svc_helos_trav_{garden,secret,uber,sparta}` offer the SAME route (tag AND dest)
   in the SAME level; the engine is 1-route-1-NPC-per-level, so Almyros binds and the 4 dedicated
   travelers go MUTE (Will's Sparta report).
2. *Warden* - `svc_testhub_return` is one record placed in 5 levels; a boat-dialog record binds ONE
   entity, so 4 of the 5 established-area returns are MUTE. Plus `svc_testhub_master_cave` is placed
   with no trigger (orphan).

---

## What b48 changes (all IMPLEMENTED on the branch; cherry-pick the diff)

1. **PRIMARY - de-dup Almyros from the TESTHUB plaza** [round 2]
   `tools/build_section_surgery.py merge_hub_into_inject_specs`: when folding the hub into
   `HELOS_HOST_KEY`, filter out `PORTAL_MASTER_SPEC` (fail-loud if absent). TESTHUB-only; canonical
   byte-unchanged (Almyros stays Helos's sole cross-area mechanism on Steam). Fixes the 4 outbound
   G-COLLISIONs. This function is byte-identical in `main` and b48 (verify, then cherry-pick).

2. **WARDEN-SPLIT the returns** [round 3, IMPLEMENTED]
   The single `svc_testhub_return` -> 5 DISTINCT per-area records `svc_testhub_return_{garden,secret,
   uber,sparta,bossarena}`, each a byte-clone of the original (Nostos identity `tagSVCNpcTestHubReturn`
   / `tagSVCTestHubReturnChat` + 2-port menu `TESTHUB_RETURN_DESTS` = Helos + Blood Cave; all reused
   tags, **zero new Text**), each placed exactly once.
   - `tools/apply_svc_patches.py`: `TESTHUB_AREA_RETURN_NPCS` + a creation loop in
     `_create_testhub_portal_npcs` (clones the Knossos-boatman donor). `svc_testhub_return` record is
     KEPT in the arz but retired (unplaced + untriggered = inert).
   - `tools/build_quest_files.py`: `_add_testhub_portal_travel` now emits one 2-port trigger per
     record (max +5; fail-loud deltas: each record +2 refs, `svc_testhub_return` +0, each dest tag
     +5). Stale round-1 "boat-offer overflow/cap" docstring corrected to the round-2/3 RCA.
   - `tools/build_section_surgery.py`: Garden/Secret/Uber/Sparta placements in **base INJECT_SPECS**
     swap `SVC_RETURN_NPC_DBR` -> the 4 per-area records (`SVC_RETURN_{GARDEN,SECRET,UBER,SPARTA}_DBR`);
     Boss Arena in `build_hub_extra_specs` swaps `SVC_TESTHUB_RETURN_DBR` -> `SVC_RETURN_BOSSARENA_DBR`.
   - **CANONICAL IMPACT:** Garden/Secret/Uber/Sparta returns are canonical (base INJECT_SPECS), so
     this changes the canonical `Levels.arc` (4 records swapped) + `Quests.arc` (5 return triggers).
     This is a deliberate bugfix - the warden-mute shipped 3 mute returns to Steam. Boss Arena's
     return stays TESTHUB-only.

3. **RETIRE the orphan cave master** [round 3, IMPLEMENTED]
   `tools/build_section_surgery.py build_hub_extra_specs`: the `R09_LVL_KEY` (`svc_testhub_master_cave`
   at (32,1,45)) placement is dropped -> the swap path injects 0 rig NPCs. Fixes G-ORPHAN. TESTHUB-only.
   *Alternative if a blood-cave-mouth hub is wanted:* WIRE `svc_testhub_master_cave` its own boat
   trigger (it is the sole boat NPC in random09a -> collision-free) with a dest menu, instead of
   retiring. b48 chose retire (lowest risk; the mute orphan did nothing anyway; the Helos plaza has
   the full "one person each" hub).

4. **GATE wired** [round 3]
   `tools/debug/gate_traveler_responds.py` gains a build-free `facts_from_specs()` and is invoked by
   `tools/debug/gate_travel_npc_invariants.py check_responds()`. Also updated in that battery:
   T3 (cave master 0 placements - checked against the raw `build_hub_extra_specs`, NOT the merged
   specs, since merge excludes R09), T4 (svc_testhub_return x0; the 5 per-area returns x1 each),
   T5b (the 5 records agree across arz/quests/map). `gate_testhub_portal_rig.py` check A/B updated.

---

## Integrator TO-DO on `main` (the two things b48 could not do)

### A. Canonical map + Quests rebuild + QA (because the return-split touches canonical)
After cherry-picking, rebuild BOTH the canonical and TESTHUB `Levels.arc` + the `Quests.arc`, and gate:
```
py tools/debug/gate_travel_npc_invariants.py                       # build-free: T1-T5b + RESPONDS
py tools/debug/gate_traveler_responds.py --specs                   # build-free TESTHUB
py tools/debug/gate_traveler_responds.py --specs --canonical       # build-free canonical/Steam
# then, post-build:
py tools/debug/gate_traveler_responds.py --quests <TESTHUB Quests.arc> --levels <TESTHUB Levels.arc>
py tools/debug/gate_testhub_portal_rig.py                          # needs local/Levels_merged.arc + arz
```
In-game confirm (restart Steam+TQ, verify md5s changed): at the Helos plaza click **Sparta Crypt** ->
the boat dialog fires and travels; spot-check garden/secret/uber outbound + the 5 area returns.

### B. Reconcile main's 14-traveler roster (b48 base = 11)
b48 is based on `da918c5`, which PREDATES b39-hub-v2's merge. The deployed DEV set Will is clicking =
b48's **11** dedicated plaza travelers; **main/b39 yields 14** (b39 added Dorus/Tantalus/Charon/... as
separate dedicated travelers). The de-dup (`merge_hub_into_inject_specs`) is byte-identical between
`da918c5` and `main`, so the PRIMARY diff cherry-picks cleanly, but on main the integrator must:
- **Re-verify route-uniqueness across main's 14-traveler roster after the de-dup.** The b39 hub kept
  `garden`/`secret` dests == Almyros and all 4 tags == Almyros, so a tag- OR dest-keyed engine would
  still mute at least garden/secret without the de-dup - the de-dup covers it, but re-run
  `gate_traveler_responds --specs` on main to confirm no NEW collision among the 14.
- **Apply the warden-split (item 2) + cave-retire (item 3) on main's map lane**, not b48's copies -
  the record/trigger/placement edits are the same, but main's `build_section_surgery` return
  placements may already differ; port the SWAP (svc_testhub_return -> per-area records), don't
  blindly overwrite.

---

## Verification already done on `feat/b48-sparta-mute` (no heavy build)
- Deployed DEV set (BEFORE): `gate_traveler_responds` FAIL - Sparta collision + 3 siblings, warden
  (svc_testhub_return x5), orphan (cave). `b48_dryrun_responds.py`: FAIL -> PASS via the REAL tables.
- `gate_traveler_responds --specs` (TESTHUB) + `--specs --canonical` (Steam): both PASS.
- `gate_travel_npc_invariants.py` full battery (T1-T5b + RESPONDS): PASS.
- Real `.qst` chain round-trips byte-stably on the clean SVAERA `sv_commonmechanics.qst`; deltas pass;
  final quest wires the 5 per-area returns (2-port) and 0 refs to svc_testhub_return/svc_testhub_master.
- The 5 new arz record names are net-new (no `has_record` collision); donor present. Negative test:
  the gate catches a re-added cave orphan + a double-placed return, passes the clean baseline.
- `py_compile` all changed files OK.
