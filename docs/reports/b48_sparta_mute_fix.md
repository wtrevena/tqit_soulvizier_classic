# b48 SPARTA-MUTE - PATCH SPEC for the hub (apply onto `main`, post-b39-merge)

Exact edits to make every mute hub traveler RESPOND. RCA + evidence: `b48_sparta_mute.md`.
Integration target is **`main`** (b39-hub-v2 is already merged: commit 87b0cae; the collision is
still LIVE there - `_add_helos_portal_travel` still offers garden/secret/uber/sparta and the
dedicated travelers keep the same tags). Do not edit b39's worktree.

**Root cause (one line):** in the TESTHUB Helos plaza, the canonical Almyros (`portal_master_helos`,
boat trigger #1) and the dedicated `svc_helos_trav_{garden,secret,uber,sparta}` offer the SAME route
(tag AND dest) in the SAME level; the engine is 1-route-1-NPC-per-level, so Almyros binds and the 4
dedicated travelers go placed-but-MUTE. (Base game never shares a route across two NPCs.)

---

## 1. PRIMARY - de-dup Almyros from the TESTHUB plaza  [ALREADY IMPLEMENTED on feat/b48-sparta-mute]

`tools/build_section_surgery.py`, function `merge_hub_into_inject_specs` (BYTE-IDENTICAL in `main`
and this branch - cherry-pick the diff directly). When folding the hub extras into `HELOS_HOST_KEY`,
filter `PORTAL_MASTER_SPEC` (any spec whose npc == `PORTAL_MASTER_NPC_DBR`) out of the base list
before appending the dedicated travelers; raise if it is not found (fail-loud). Result: the TESTHUB
plaza carries ONLY the dedicated "one person each" travelers, each route-unique.

- Steam/canonical is byte-unchanged (this path runs only under `SVC_TEST_HUB=1`; the canonical
  `INJECT_SPECS[startingfarmland06d] = [PORTAL_MASTER_SPEC]` is untouched, so Almyros remains
  Helos's sole cross-area mechanism on Steam).
- Key-agnostic: after de-dup NO two plaza NPCs share a tag OR a dest, so all 4 outbound mutes are
  fixed whether the engine keys routes by tag or by dest. (Note: b39 already retargeted sparta/uber
  to distinct dests but KEPT garden/secret dests == Almyros, and KEPT all 4 tags == Almyros - so a
  tag- OR dest-key would still mute at least garden/secret without this de-dup.)
- Proof: `merge_hub_into_inject_specs(INJECT_SPECS)[HELOS_HOST_KEY]` -> 11 (b39: 14) dedicated
  travelers, 0 Almyros.

## 2. KEEP - drop the UNPLACED `svc_testhub_master` trigger  [already on this branch]
`tools/build_quest_files.py` `_add_testhub_portal_travel`: keep only the return trigger; the 7-port
`svc_testhub_master` trigger stays dropped. Cleanup (harmless no-op offers under per-level
ownership), not the load-bearing fix. Verify `main` also carries this drop; if not, port it.

## 3. SECONDARY (map + arz + quests) - warden-split the returns
`svc_testhub_return` is placed in 5 levels (one record -> only 1 return NPC binds; the other 4 are
MUTE). Split into 5 distinct per-area return records, exactly mirroring the 6 existing
`svc_area_return_*` records. Each offers the SAME 2 routes as `svc_testhub_return`
(`tagSVCTestHubToHelos` dest (-5980,1,909); `tagSVCTestHubToBloodCave` dest (6018,19,3293)).

New records + placements (swap the `svc_testhub_return` placement in each level for its own record):

| new record | level | placement (local x,y,z of the current svc_testhub_return) |
|---|---|---|
| `svc_area_return_garden.dbr`    | GardenofMerchants.lvl | (133.0, -39.0, 73.0) |
| `svc_area_return_secret.dbr`    | DarkForestEnter.lvl   | (27.0, 1.0, 30.0) |
| `svc_area_return_uber.dbr`      | crypt_floor1.lvl      | (140.0, 10.0, 229.0) |
| `svc_area_return_sparta.dbr`    | SpartaCryptLevel2.lvl | (45.0, -1.6, 42.0) |
| `svc_area_return_bossarena.dbr` | boss_arena.lvl        | (131.0, 0.0, 40.0) |

- `apply_svc_patches.py`: clone each new record from the same donor as the existing returns (the
  Knossos boatman / `svc_testhub_return`); add to `HELOS_HUB_RETURNS`. Reuse `tagSVCAreaReturnToHelos`
  label (already in Text.arc).
- `build_quest_files.py`: add 5 boat triggers to `HELOS_HUB_TRAVEL` (one per new record), each
  carrying the 2 return routes (or model as single Helos-return offers if BloodCave is not wanted
  from these areas).
- `build_section_surgery.py`: in the 5 levels, replace the `svc_testhub_return` spec with the new
  per-area record (via `remove_0x05_instances_by_dbr` + the new spec, or edit the per-level spec).
- Because each new record is placed exactly once, G-WARDEN clears.

## 4. SECONDARY (map) - wire or retire `svc_testhub_master_cave`
It is placed in `Random09A.lvl` with NO boat trigger targeting it (orphan; clicking it does nothing).
Either (a) add a boat trigger for it in `build_quest_files.py` (give it a real destination + tag), or
(b) drop its placement from `build_section_surgery.py`. Recommended: (a) if the blood-cave hub is
still wanted, else (b).

## 5. GATE - wire `tools/debug/gate_traveler_responds.py` into the build
Add to the travel-invariants / deploy gate battery, run AFTER the TESTHUB Levels + Quests are built:
```
py tools/debug/gate_traveler_responds.py --quests <built Quests.arc> --levels <built TESTHUB Levels.arc>
```
Exit 1 blocks the ship. (Standalone; complements the pre-build `gate_travel_npc_invariants.py`.)
Also update `gate_travel_npc_invariants.py` **T4** - it currently ASSERTS `svc_testhub_return` placed
**x4** canonically, i.e. it enshrines the warden-mute. After §3 it must instead assert the 5 distinct
per-area return records placed 1x each (and drop the `svc_testhub_return` x4 assertion).

## 6. Verification already done on `feat/b48-sparta-mute` (no heavy build)
- `merge_hub_into_inject_specs` de-dup: plaza = 11 dedicated travelers, 0 Almyros.
- `gate_traveler_responds.py` on the deployed set: FAIL (G-COLLISION sparta+3, G-WARDEN return, G-ORPHAN cave).
- `b48_dryrun_responds.py`: full fix applied to deployed facts -> **GATE PASS**.
- `gate_travel_npc_invariants.py` still PASS after the de-dup (canonical untouched).
- `py_compile` all changed files OK.

## 7. In-game confirm (after the coupled arz+Text+Quests+TESTHUB-Levels rebuild + DEV deploy)
Restart Steam+TQ, verify the deployed Quests/Levels md5 changed, then at the Helos plaza click the
**Sparta Crypt** traveler -> the talk-confirm boat dialog should now fire and travel. Spot-check
garden/secret/uber (the other 3 formerly-mute) + a couple returns.
