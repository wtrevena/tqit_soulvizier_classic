# b48 - SPARTA-MUTE RCA + 20-NPC audit + fix (2026-07-13, ROUND 2)

Branch `feat/b48-sparta-mute` off `da918c5`. NO heavy build (arc/qst parsing + record inspection +
dry-run only). Read-only vs the DEPLOYED DEV set Will is clicking (SoulvizierClassicDEV:
**Quests.arc `838bdc3a`**, **Levels.arc `841c56cd`** TESTHUB, **arz `6631f252`**), cross-checked
against the base-game boat quests in the same arc and the `feat/b39-hub-v2` source (READ-only).

> **Round 2 supersedes round 1.** The round-1 RCA (an "engine boat-offer registry OVERFLOW driven
> by 7 dead offers") was WRONG and is retracted - see §7. This round proves a different, simpler
> mechanism from ground truth, and the round-1 fix (drop the dead master) did NOT make Sparta fire.

## THE BUG (Will, 2026-07-13)
Clicking the **Sparta Crypt** traveler in the demo/test hub does NOTHING - no dialog, no travel.
The MUTE class (distinct from the b44 land-in-chest class): the talk-confirm boat-dialog never
fires for this NPC.

## 0. TL;DR

- **Root cause (PROVEN):** the TQAE boat-dialog system is strictly **1 route : 1 NPC, per level**.
  In the Helos plaza (`StartingFarmland06D`) the canonical Almyros (`portal_master_helos`, the FIRST
  boat trigger) offers a 4-destination menu **Garden / Secret / Uber / Sparta**, and the dedicated
  `svc_helos_trav_sparta` (a later trigger) offers the **byte-identical route** (same tag
  `tagSVCHelosToSparta` AND same dest). Two co-present NPCs, one route -> Almyros binds it, the
  dedicated Sparta traveler is **MUTE**. Same for garden/secret/uber. The 7 dedicated travelers with
  a **unique** route (bossarena/warband/dorus/tantalus/charon/mnemophage/ephialtes) own their route
  alone and **DO fire** - which is exactly the set Will saw teleport him (b44 "land-in-chest").
- **Fix (key-agnostic, no landing risk, Steam-safe):** in the **TESTHUB** plaza, DROP the redundant
  Almyros placement so the "one person each" dedicated travelers are the sole route owners. Almyros
  stays canonical (its sole role on Steam) - the canonical Levels.arc is byte-untouched.
- **This reconciles the b39/b48 contradiction the round-1 vet raised** (§3): NOT all 11 travelers
  work, NOT all 11 mute - the roster SPLITS by route uniqueness (7 fire, 4 mute).
- **Permanent gate authored** (`gate_traveler_responds.py`): asserts every PLACED hub NPC actually
  RESPONDS. FAILS on the deployed set precisely on the Sparta collision (+ 3 siblings + the return
  warden + the cave orphan); PASSES after the full fix (dry-run proven).

## 1. RCA - the proven mechanism

### 1.1 The base-game LAW (ground truth, `Quests.arc` 838bdc3a)
Every base/SV `Action_BoatDialog` NPC owns a **unique `(npc, tag, dest)` triple**. Across all 9
non-hub boat NPCs, **no tag and no dest is ever shared between two NPCs**:

| quest file | npc | tag | dest |
|---|---|---|---|
| quest 7 - knossos | Athens_BoatmanToKnossos | tagAthensBoatToKnossos | (-9136,-125,-1822) |
| quest 7 - knossos | Knossos_BoatmanBackToAthens | tagKnossosBoatToAthens | (-7116,0,-1802) |
| quest 8 part i | Knossos_BoatmanToEgypt | tagKnossosBoatToRhakotis | (-1966,13,4423) |
| quest 8 part i | Rhakotis_BoatmanBackToKnossos | tagRhakotisBoatToKnossos | (-9976,1,-1673) |
| controls bosses | portal_master_olympus | tagSVCOlympusRhodesTravel | (700,41,-6466) |
| urder | (3 portal dudes) | 3 distinct tags | 3 distinct dests |
| open_bloodcave_portal | vortexportal_exit | tagReturnFromLeinthBattle | (-90,-103,2321) |

The engine has **one slot per route**; the base game never places two boat NPCs in the same level at
all, let alone two offering the same route. **The hub violates this law.**

### 1.2 The hub's violation (deployed sv_commonmechanics step 1, 30 offers, 20 NPCs)
`portal_master_helos` (Almyros) is boat trigger **#1** (registers first) with 4 offers:
`tagSVCHelosToGarden/Secret/Uber/Sparta`. The dedicated `svc_helos_trav_{garden,secret,uber,sparta}`
(triggers #4-#7) re-offer the **byte-identical** tag AND dest. All 5 NPCs (Almyros + the 4) are
placed in **one** level (`StartingFarmland06D`, the plaza), verified in Levels.arc 841c56cd:

```
portal_master_helos.dbr        @ StartingFarmland06D (76.5, 0.6, 189.5)  offers garden/secret/uber/sparta
svc_helos_trav_sparta.dbr      @ StartingFarmland06D (71.5, 0.6, 181.5)  offers sparta  (SAME route as Almyros)
```

Almyros (first) binds `tagSVCHelosToSparta`; the dedicated Sparta traveler, present in the same
level with the same route, gets nothing -> **clicking it does nothing** (its ONLY route is already
owned). Its NPC record is byte-identical to the working `svc_helos_trav_garden` except the name tag,
its trigger is byte-identical to the working ones, its dest + tags resolve in Text.arc - it is
**statically perfect**; the mute is purely the same-level route collision.

### 1.3 Ownership is PER-LEVEL (why unplaced NPCs and cross-level shares are harmless)
Proven from the deployed set itself:
- The **6 area returns** (`svc_area_return_*`) share tag `tagSVCAreaReturnToHelos` AND dest
  `(-5980,1,909)` but sit in **6 different levels** - each is the sole boat NPC in its level and all
  **RESPOND**. Same route across levels is fine.
- **Boss Arena works** though the UNPLACED `svc_testhub_master` offers `tagSVCTestHubToBossArena`
  earlier (trigger #2): an unplaced NPC has no entity to attach to, so its OnLevelLoad offer is a
  pure no-op - it never claims the route. `svc_helos_trav_bossarena` is the sole PLACED offerer ->
  it owns bossarena -> responds.

So the invariant is: **within one level, if 2+ PRESENT NPCs offer the same route, the
first-registered binds it and the rest are mute.** Unplaced NPCs never participate.

## 2. The brief's four suspects, tested explicitly

| suspect | verdict | evidence |
|---|---|---|
| (i) **WARDEN-MUTE** (Sparta shares a record with another placed NPC) | **NO for outbound Sparta** | `svc_helos_trav_sparta` is placed exactly **1x** and its record is unique. (Warden IS real for the *returns* - see §4.) |
| (ii) **TRIGGER-COUNT CAP** (Sparta's OnLevelLoad beyond a fired window) | **NO** | Base-game proof: one step fires **20** `Condition_OnLevelLoad` triggers, all effective; Sparta is trigger #6 of 20 - well inside. Every trigger is byte-identical `Condition_OnLevelLoad(isNot=0,isQuestCritical=1)` + `onOff=1`. If it were a fired-window cap, the LATE unique-route travelers (dorus #10 ... ephialtes #14) would be the mute ones - but those are exactly the ones that WORK. The cap hypothesis predicts the OPPOSITE of reality. **Refuted.** |
| (iii) **bad/missing dialog record or NPC->dialog link** | **NO** | `svc_helos_trav_sparta.dbr` in arz = byte-identical to `svc_helos_trav_garden` except the `description` tag; `messageDialogTag=tagSVCHelosTravChat` (shared, resolves); `tagSVCHelosToSparta`="The Sparta Crypt" and `tagSVCNpcTravSparta` both present in Text.arc. |
| (iv) **NPC placed but its conversation record absent** | **NO** | record present, placement present, tag present - see (iii). |

The **real** discriminator is route-uniqueness vs collision (§1), which none of the four naive
suspects captures.

## 3. Reconciling the b39 "travelers WORKED" vs b48 "Sparta mute" contradiction (round-1 vet's key point)
`b39_hub_v2.md` (same day) says "the existing 11 Helos travelers teleported him straight to the
destination interior / onto the boss." b44 pins the ones Will actually **traveled** through (they put
him on a boss and killed him): **dorus, tantalus, charon, mnemophage, ephialtes**. Those five are
exactly **unique-route** travelers -> they own their route -> they fire. Will then clicked **Sparta**
(a route SHARED with Almyros) -> mute. So it is neither "all work" nor "all mute": the roster splits
**7 fire / 4 mute** by route uniqueness. The b39 "11 travelers teleported" was an over-generalization
from the unique-route ones Will happened to ride; the mute 4 (garden/secret/uber/sparta all share a
route with Almyros) were never actually confirmed to respond.

## 4. AUDIT - every hub boat NPC in the deployed set (does it RESPOND?)

| NPC | placed level(s) | # routes | verdict |
|---|---|---|---|
| portal_master_helos (Almyros) | StartingFarmland06D | 4 | **RESPONDS** (first owner; Will-confirmed) |
| svc_helos_trav_**garden** | StartingFarmland06D | 1 | **MUTE** - route bound first by Almyros (same level) |
| svc_helos_trav_**secret** | StartingFarmland06D | 1 | **MUTE** - route bound first by Almyros |
| svc_helos_trav_**sparta** | StartingFarmland06D | 1 | **MUTE** - route bound first by Almyros **(Will's report)** |
| svc_helos_trav_**uber** | StartingFarmland06D | 1 | **MUTE** - route bound first by Almyros |
| svc_helos_trav_bossarena | StartingFarmland06D | 1 | RESPONDS (unique route) |
| svc_helos_trav_warband | StartingFarmland06D | 1 | RESPONDS (unique route) |
| svc_helos_trav_dorus | StartingFarmland06D | 1 | RESPONDS (unique; b44 land-in-chest) |
| svc_helos_trav_tantalus | StartingFarmland06D | 1 | RESPONDS (unique; b44) |
| svc_helos_trav_charon | StartingFarmland06D | 1 | RESPONDS (unique; b44) |
| svc_helos_trav_mnemophage | StartingFarmland06D | 1 | RESPONDS (unique; b44) |
| svc_helos_trav_ephialtes | StartingFarmland06D | 1 | RESPONDS (unique; b44) |
| svc_area_return_dorus/tantalus/charon/mnemophage/ephialtes/warband | 6 distinct levels | 1 each | RESPONDS (distinct record, own level) |
| **svc_testhub_return** | Garden/Secret/Uber/Sparta/BossArena (**5 levels**) | 2 | **MUTE (WARDEN)** - one record placed 5x binds ONE entity; the other 4 returns are silent |
| **svc_testhub_master_cave** | Random09A | 0 | **MUTE (ORPHAN)** - placed but no boat offer targets it |
| svc_testhub_master | (unplaced) | 7 | harmless no-op (unplaced; never claims a route) |

**Mute inventory:** (1) 4 outbound travelers **garden/secret/sparta/uber** (in-level route collision
with Almyros); (2) 4-of-5 established **returns** (`svc_testhub_return` warden-split); (3) the
blood-cave hub **svc_testhub_master_cave** (orphan). The 7 unique-route outbound travelers + 6
new-area returns + Almyros all respond.

## 5. FIX (keeps the TRAVEL LAW talk-confirm pattern; just makes the offers unique-per-level)

**PRIMARY - de-dup Almyros from the TESTHUB plaza [IMPLEMENTED in this worktree].**
`tools/build_section_surgery.py` `merge_hub_into_inject_specs`: when folding the TESTHUB hub into
`HELOS_HOST_KEY`, drop `PORTAL_MASTER_SPEC` from the base so the plaza carries ONLY the dedicated
"one person each" travelers (each with a mutually-unique route). Fail-loud if Almyros is not present
to de-dup. **Canonical/Steam build byte-unchanged** (this path only runs under SVC_TEST_HUB=1;
Almyros stays canonical, its sole cross-area mechanism on Steam). Key-agnostic: after de-dup NO two
plaza NPCs share a tag OR a dest, so it fixes all 4 outbound mutes whether the engine keys routes by
tag or by dest. Verified: `merge_hub_into_inject_specs(INJECT_SPECS)[HELOS_HOST_KEY]` now yields the
11 dedicated travelers, **0** Almyros.

**KEPT (round-1, this worktree) - drop the UNPLACED `svc_testhub_master` trigger** in
`build_quest_files.py`. This is cleanup (its 7 offers are harmless no-ops under per-level ownership),
not the load-bearing fix; it keeps the rig tidy and removes the bossarena route-tag it shared.

**SECONDARY (map + arz lanes -> PATCH SPEC for the b39/main hub, see `b48_sparta_mute_fix.md`):**
- **Warden-split the returns:** replace `svc_testhub_return` (placed 5x) with 5 distinct per-area
  return records (Garden/Secret/Uber/Sparta/BossArena), one placement each - the exact precedent the
  6 new-area returns already use. Fixes the 4 mute returns.
- **Wire or retire `svc_testhub_master_cave`:** give the placed blood-cave hub its own boat trigger,
  or drop the placement. Fixes the orphan.

## 6. GATE (permanent): `tools/debug/gate_traveler_responds.py`

Post-build, arc-driven (defaults to the deployed DEV set; `--quests/--levels` to gate freshly-built
arcs). Every PLACED hub boat NPC must RESPOND:
- **G-COLLISION** - it owns >=1 of its routes in its level (no earlier same-level NPC already binds
  that tag/dest). **[THE Sparta bug]**
- **G-WARDEN** - its record is placed in exactly 1 level.
- **G-ORPHAN** - it registers >=1 route.
- **G-DEST** - destinations non-zero.

An UNPLACED NPC is never faulted (it is not clickable and its offers no-op) - the round-1 gate's
"dead offer" fault is corrected. Run against the deployed set it FAILS on exactly the concrete mutes:
G-COLLISION x4 (garden/secret/**sparta**/uber), G-WARDEN (svc_testhub_return x5), G-ORPHAN
(svc_testhub_master_cave). Wire into the travel-invariants family / deploy gate battery (run after
the TESTHUB Levels + Quests are built).

## 7. Verification (no heavy build)
- `py_compile` all changed files: OK.
- Gate on the DEPLOYED set: **FAIL**, exit 1 - G-COLLISION names `svc_helos_trav_sparta` MUTE
  (bound first by `portal_master_helos`), + 3 siblings + warden + orphan.
- `tools/debug/b48_dryrun_responds.py`: applies the full fix (de-dup via the REAL
  `merge_hub_into_inject_specs` + drop master + split returns + retire cave) to the deployed facts
  and re-runs `gate.evaluate` -> **GATE PASS** (every mute class resolved). Exit 0.
- Existing `gate_travel_npc_invariants.py` still **PASS** after the de-dup (it checks CANONICAL
  Almyros x1, which is untouched).

## 8. What round 1 got wrong / what is salvaged
- **RETRACTED:** the "bounded boat-offer registry OVERFLOW driven by 7 dead offers" mechanism. It was
  unfalsifiable, contradicted the base-game 20-OnLevelLoad-fire proof, and its fix (drop the dead
  master) leaves Almyros still binding Sparta's route -> Sparta STILL mute. The real culprit is the
  in-level route collision with **Almyros**, which round 1 never identified (it fixated on the dead
  master).
- **Also corrected:** the round-1 gate hard-failed on unplaced "dead offers" (harmless) and never
  hard-failed on the actual Sparta collision (it was a non-failing WARN). The rewritten gate fails on
  Sparta and passes post-fix.
- **SALVAGED (still accurate):** the 30-offer registration order, all placements, sparta==garden
  static identity, and the two secondary mute findings (svc_testhub_return warden, svc_testhub_master_cave
  orphan) - all re-confirmed and folded into the audit + fix here.

## Evidence tooling (read-only, `tools/debug/`)
`gate_traveler_responds.py` (the gate), `b48_dryrun_responds.py` (fix FAIL->PASS dry-run),
`b48_definitive.py` (30 offers in registration order), `b48_placements.py` (per-record placements),
`b48_arz_records.py` (sparta==garden identity + Text tags). Base-game 1:1:1 scan +
audit-table scripts in the session scratchpad.
