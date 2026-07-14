# b48 SPARTA-MUTE - PATCH SPEC for the hub branch (b39-hub-v2 integration)

Exact edits to make the mute hub travelers RESPOND. RCA + evidence: `b48_sparta_mute.md`.
b39-hub-v2 owns `build_quest_files.py` / `apply_svc_patches.py` / `build_section_surgery.py` and is
mid-retarget, so these are applied by the INTEGRATOR onto the hub branch (do not edit b39's worktree
directly). Item 1 is already implemented on `feat/b48-sparta-mute` as a reference diff.

Root cause (one line): the always-loaded `sv_commonmechanics` step registers **30 Action_BoatDialog
offers**; **7 are dead** (`svc_testhub_master`, unplaced) and sit AHEAD of the per-area travelers,
overflowing the engine's bounded boat-offer registry so every dedicated traveler (incl. Sparta) goes
placed-but-mute. Base game never exceeds ~5 boat offers.

> ⚠️ b39-hub-v2 goes the WRONG way for this bug: it grows the hub to 25 triggers (~38 offers),
> which makes the overflow WORSE. The fix is to REDUCE offers (kill dead + redundant), not add more.
> Consolidating triggers does NOT help - offer count = number of `Action_BoatDialog` actions,
> independent of how they are grouped into triggers.

---

## 1. QUESTS lane - DROP the dead `svc_testhub_master` trigger  [IMPLEMENTED on feat/b48-sparta-mute]

File `tools/build_quest_files.py`, `_add_testhub_portal_travel`:
- Bump the host step's trigger `max` by **+1** (not +2).
- Append ONLY the `svc_testhub_return` trigger; DELETE the `svc_testhub_master` `trigcont.extend(...)`.
- Change the master reference-count assert from `_delta(TESTHUB_MASTER_NPC) != len(...)` to
  `_delta(TESTHUB_MASTER_NPC) != 0` (assert it stays dead-inert).
- Drop `TESTHUB_MASTER_DESTS` from the tag-count `Counter` loop (use `TESTHUB_RETURN_DESTS` only).

Effect: 30 -> 23 offers; Sparta registration #15 -> #8. Dry-run `tools/debug/b48_dryrun_fix.py` PASS
(round-trip stable; master 0x, return 2x, 11 travelers + 6 returns present).
b39 note: this composes cleanly with b39's `_add_helos_traveler_hub_travel` growth - just keep the
master trigger dropped.

## 2. MAP + arz lane - WARDEN-SPLIT the shared `svc_testhub_return` (fixes 4 mute returns)

`svc_testhub_return.dbr` is placed in **5 levels** (Garden/Secret/Uber/Sparta/BossArena) - warden law
means only ONE binds; the other 4 area-returns are mute. Mirror the b37 precedent that already gives
the 6 NEW areas distinct returns:
- **arz** (`apply_svc_patches.py` `_create_helos_traveler_hub` or a sibling): clone the boatman donor
  into 5 distinct records `svc_area_return_garden/secret/uber/sparta/bossarena.dbr` (reuse the shared
  `tagSVCNpcAreaReturn` / `tagSVCAreaReturnChat` name/chat tags - shared TEXT is fine, only PLACEMENT
  must be single).
- **quests** (`build_quest_files.py` `_add_helos_traveler_hub_travel`): add one 1-port
  `Action_BoatDialog(-> Helos -5980,1,909, tag tagSVCAreaReturnToHelos)` trigger per new return record.
- **map** (`build_section_surgery.py`): replace the 5 `SVC_TESTHUB_RETURN_DBR` placements in
  Garden/Secret/Uber/Sparta/BossArena (INJECT_SPECS - they were "promoted to canonical" per the
  2026-07-12 P0) with the matching distinct record at the same coords. Retire the shared
  `svc_testhub_return` (or keep it ONLY for the single blood-cave return if still wanted).
- Update the existing `gate_travel_npc_invariants.py` **T4** - it currently ASSERTS
  `svc_testhub_return` in the 4 P0 areas, which is the warden-mute encoded as "expected". Change it to
  assert the distinct per-area returns (single placement each).

## 3. MAP lane - de-dup portal_master_helos from the TESTHUB Helos plaza (reduce concurrent pressure)

The TESTHUB Helos plaza places BOTH `portal_master_helos` (4 offers: Garden/Secret/Uber/Sparta) AND
the 4 dedicated `svc_helos_trav_{garden,secret,uber,sparta}` travelers - the same 4 areas twice, 15
attaching offers in Helos. Keep `portal_master_helos` in CANONICAL (it is Will's confirmed working
Steam travel), but do NOT place it in the TESTHUB plaza (the 11 dedicated travelers are "one person
each"). Net TESTHUB Helos concurrent offers: ~11 (down from 15 attach / 30 fire).
- `build_section_surgery.py`: `PORTAL_MASTER_SPEC` is in base `INJECT_SPECS[startingfarmland06d]`
  (canonical). Add a TESTHUB-only removal of that one spec in `merge_hub_into_inject_specs` (or place
  the dedicated 4 only in TESTHUB and leave portal_master canonical-only). Canonical Steam map
  UNCHANGED.

## 4. MAP + quests lane - the blood-cave hub (`svc_testhub_master_cave`) orphan

Placed in Random09A with NO trigger (the quest triggered the now-removed `svc_testhub_master`). Either
give `svc_testhub_master_cave` its own boat-dialog trigger (the 6 destinations reachable FROM the
blood cave) or drop the placement. Decide with the b39 return-rework.

## 5. GATE - wire `tools/debug/gate_traveler_responds.py` into the build

Add it to the travel-invariants gate family / `run_contracts` path, run against the freshly-built
TESTHUB arcs: `py tools/debug/gate_traveler_responds.py --arz <built.arz> --quests <built Quests.arc>
--levels <built TESTHUB Levels.arc>`. It hard-fails on G1 dead-offer / G2 warden-mute / G3 orphan and
warns on the G5 offer budget. After items 1-4 land, G1/G2/G3 go green.

## Residual / runtime confirm (Will)
The exact engine boat-offer cap is not statically knowable. Items 1+3 bring the worst-level (Helos)
concurrent offers to ~11 (from ~12 attach / 30 fire) and remove all dead/warden offers. If an in-game
test still shows mute travelers at ~11, the structural fix is base-game practice: scope each area's
offer to a per-area quest / `Condition_EnterVolume` rather than all-in-`sv_commonmechanics`. Restart
TQ + Steam and hash-verify the deploy landed before the test (standing rule).
