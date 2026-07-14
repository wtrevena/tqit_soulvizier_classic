# b48 - SPARTA-MUTE RCA + 17-traveler audit + fix (2026-07-13)

Branch `feat/b48-sparta-mute` off `da918c5` (build38a-dev). NO heavy build. Read-only vs the
DEPLOYED DEV set that Will is clicking (SoulvizierClassicDEV: **Quests.arc `838bdc3a`**,
**Levels.arc `841c56cd`** TESTHUB, **arz `6631f252`**), cross-checked against the b39-hub-v2
source (READ-only) and the base game.

## THE BUG (Will, 2026-07-13)
Clicking the **Sparta Crypt** traveler in the demo/test hub does NOTHING - no dialog, no travel.
The MUTE class (distinct from the b44 land-in-chest class): the talk-confirm boat-dialog never
fires for this NPC.

## MECHANISM (nailed with evidence): BOAT-OFFER REGISTRY OVERFLOW from 7 DEAD offers

**The Sparta traveler is statically PERFECT.** Traced end to end in the deployed set:
- **arz**: `records\quests\svc_helos_trav_sparta.dbr` exists, `Class=Npc`, cloned from the proven
  boat-dialog donor `knossos_boatmantoegypt`. It differs from the (identical) sibling
  `svc_helos_trav_garden.dbr` by **exactly one field** (`description`) - byte-identical otherwise.
- **map**: placed **exactly once** in `StartingFarmland06D.lvl` (the Helos plaza) at local
  `(71.5, 0.6, 181.5)`. Not double-placed, not missing.
- **quests**: `sv_commonmechanics.qst` step 1 carries its `Condition_OnLevelLoad ->
  Action_BoatDialog(npc=svc_helos_trav_sparta, dest=(-5602,-2,-1409), tag=tagSVCHelosToSparta)`.
  Destination valid, tag resolves.

So the four naive suspects are RULED OUT for the outbound Sparta traveler: it is not warden-mute
(single placement), not a missing/bad record (byte-identical to a sibling), not an absent
NPC->dialog link (trigger present), not a bad destination. **Because all 11 dedicated
`svc_helos_trav_*` travelers are byte-identical clones registered the same way, the mute is a
CLASS defect - Sparta is simply the one Will clicked.**

**What actually mutes them: the engine's Action_BoatDialog offer registry is BOUNDED, and the hub
overflows it with DEAD offers.** Evidence:

1. **The deployed hub registers 30 `Action_BoatDialog` offers** across 20 NPCs, all in one always-
   loaded quest step (`sv_commonmechanics` step 1, the "Makes it so Quest Never Completes" refire
   step). They fire on EVERY level load.
2. **Base-game bounds (mined from all 261 base/xpack `.qst`):** the base game NEVER registers more
   than **2 `Action_BoatDialog` actions in one trigger** and never more than **~5 boat offers total
   anywhere**. It also proves the limiter is NOT a generic trigger cap: one base step (`quest that
   controls boss chest swap`) has **20 `Condition_OnLevelLoad` triggers that all fire**. So 20+
   OnLevelLoad triggers/step is fine - the limiter is specific to **boat-dialog offers**.
3. **7 of the 30 offers are DEAD.** `svc_testhub_master` (registrations **#4-#10**, 7 ports) targets
   an NPC that is **placed in NO level** (the map places `svc_testhub_master_cave` instead - a
   long-standing warden-split miss). The build's own comment assumed unplaced offers are a harmless
   "no-op" (`build_quest_files.py` `_add_testhub_portal_travel`), but they still **register into the
   bounded offer table** ahead of the real travelers.
4. **The dedicated travelers register AFTER the dead block.** Registration order:
   `portal_master_helos` #0-3 (WORKS - Will's confirmed canonical "Almyros the Wayfarer"), dead
   `svc_testhub_master` #4-10, `svc_testhub_return` #11-12, then `garden` #13, `secret` #14,
   **`sparta` #15**, `uber` #16 ... So by the time Sparta registers, **15 offers are ahead of it**
   (4 working + 7 dead + 2 + garden + secret). If the cap counted only offers that ATTACH in Helos,
   Sparta (the 7th attach) would work; since it is mute, the cap counts **fired** offers (dead ones
   included), and Sparta is past it.

This is the same "engine only honors the first ~N of an over-long list" family as the documented
QUESTS 256-window / letter-quest load-window - here applied to the boat-offer registry, poisoned by
the 7 dead `svc_testhub_master` registrations.

## AUDIT - all 20 hub boat NPCs in the deployed set (registration order)

| reg# | NPC record | in arz | placed | level(s) | dest | verdict |
|---|---|---|---|---|---|---|
| 0-3 | portal_master_helos | Y | x1 | StartingFarmland06D | Garden/Secret/Uber/Sparta | **WORKS** (canonical Almyros; Will-confirmed) |
| 4-10 | **svc_testhub_master** | Y | **x0** | - | 7 ports | **DEAD** - unplaced; 7 offers poison/overflow the registry (**G1**) |
| 11-12 | **svc_testhub_return** | Y | **x5** | Garden/Secret/Uber/Sparta/BossArena | Helos/BloodCave | **WARDEN-MUTE** - one record in 5 levels; 4 of 5 returns silent (**G2**) |
| 13 | svc_helos_trav_garden | Y | x1 | StartingFarmland06D | (1173,-39,-4001) | statically ok; **MUTE via overflow** |
| 14 | svc_helos_trav_secret | Y | x1 | StartingFarmland06D | (-2396,2,-5790) | statically ok; **MUTE via overflow** |
| **15** | **svc_helos_trav_sparta** | Y | x1 | StartingFarmland06D | (-5602,-2,-1409) | statically ok; **MUTE via overflow (Will's report)** |
| 16 | svc_helos_trav_uber | Y | x1 | StartingFarmland06D | (-2438,10,-2450) | statically ok; **MUTE via overflow** |
| 17 | svc_helos_trav_bossarena | Y | x1 | StartingFarmland06D | (-433,0,-3602) | statically ok; **MUTE via overflow** |
| 18 | svc_helos_trav_warband | Y | x1 | StartingFarmland06D | (5680,1,3285) | statically ok; **MUTE via overflow** |
| 19 | svc_helos_trav_dorus | Y | x1 | StartingFarmland06D | (312,1,-8462) | statically ok; **MUTE via overflow** |
| 20 | svc_helos_trav_tantalus | Y | x1 | StartingFarmland06D | (-342,-15,-10095) | statically ok; **MUTE via overflow** |
| 21 | svc_helos_trav_charon | Y | x1 | StartingFarmland06D | (-336,-7,-9650) | statically ok; **MUTE via overflow** |
| 22 | svc_helos_trav_mnemophage | Y | x1 | StartingFarmland06D | (170,-10,-11438) | statically ok; **MUTE via overflow** |
| 23 | svc_helos_trav_ephialtes | Y | x1 | StartingFarmland06D | (-1828,3,-13285) | statically ok; **MUTE via overflow** |
| 24 | svc_area_return_dorus | Y | x1 | Medea_TempleUG_Tomb01 | Helos | ok (distinct, single) - own level, low pressure |
| 25 | svc_area_return_tantalus | Y | x1 | Styx_SwampBorder_01 | Helos | ok (distinct, single) |
| 26 | svc_area_return_charon | Y | x1 | Styx_RiverEdge_01 | Helos | ok (distinct, single) |
| 27 | svc_area_return_mnemophage | Y | x1 | Judgment_TempleUG_Mnemosyne01 | Helos | ok (distinct, single) |
| 28 | svc_area_return_ephialtes | Y | x1 | Judgment_StoneCity_Exit01 | Helos | ok (distinct, single) |
| 29 | svc_area_return_warband | Y | x1 | drxFirstxistion_connection | Helos | ok (distinct, single) |
| - | **svc_testhub_master_cave** | Y | x1 | Random09A | (no offer) | **ORPHAN-MUTE** - placed, NO trigger targets it (**G3**) |

**Mute inventory:** (1) all **11 dedicated outbound travelers** (Garden/Secret/**Sparta**/Uber/
BossArena/Warband/Dorus/Tantalus/Charon/Mnemophage/Ephialtes) via the boat-offer overflow driven
by the 7 dead `svc_testhub_master` offers; (2) the **4-of-5 established returns**
(Garden/Secret/Uber/Sparta/BossArena) via the `svc_testhub_return` warden-split (one record placed
5x); (3) the **blood-cave hub** (`svc_testhub_master_cave`, placed but triggerless). The 6 new-area
returns (distinct records, single placement, own level) are the only healthy travel NPCs besides
the canonical `portal_master_helos`.

## FIX

Every fix keeps the **TRAVEL LAW** talk-confirm boat-dialog pattern; it just makes the offers
actually register + bind. The complete fix spans three lanes (see `b48_sparta_mute_fix.md` for the
exact patch spec b39 applies).

**Implemented here (quest lane, `tools/build_quest_files.py`, dry-run verified):**
- **DROP the dead `svc_testhub_master` 7-port trigger** (`_add_testhub_portal_travel`). Its NPC is
  placed nowhere, so the 7 offers were pure dead weight ahead of the travelers. Removing them cuts
  the registry from **30 -> 23** offers and moves **Sparta from registration #15 to #8**. Dry-run
  (`tools/debug/b48_dryrun_fix.py`) PASS: chain round-trips stably, `svc_testhub_master` referenced
  0x, `svc_testhub_return` 2x, all 11 travelers + 6 returns present, total 23.

**Specced for b39 (map + arz lanes - b39 owns the hub and is retargeting it):**
- **G2 warden-split the returns:** replace the single `svc_testhub_return` (placed 5x) with 5
  distinct per-area return records (Garden/Secret/Uber/Sparta/BossArena), one placement each - the
  precedent b37 already used for the 6 new-area returns.
- **G3 wire (or retire) `svc_testhub_master_cave`:** give the placed blood-cave hub its own
  boat-dialog trigger, or drop the placement.
- **Reduce the Helos concurrent-offer pressure:** the TESTHUB Helos plaza places
  `portal_master_helos` (4 offers) AND the 4 dedicated Garden/Secret/Uber/Sparta travelers - the
  SAME areas twice. Pick one model (recommended: keep `portal_master_helos` CANONICAL for Steam,
  and DE-DUP it from the TESTHUB Helos placement so the plaza carries only the 11 one-per-area
  dedicated travelers = Will's "one person each").

**Residual (needs Will's in-game confirm):** the exact engine boat-offer cap is not statically
knowable. Removing the 7 dead offers + de-duping portal_master brings the worst-level (Helos)
concurrent offers to **~11** (down from 12 attaching / 30 firing). If a runtime test shows 11 still
overflows, the structural fix is base-game practice: scope each area's boat offer to a per-area
quest / `Condition_EnterVolume` instead of cramming all 30 into always-loaded `sv_commonmechanics`.

## GATE (permanent): `tools/debug/gate_traveler_responds.py`

Wired into the travel-invariants family. Asserts, against the built/deployed arcs (default = the
DEV set): **G1** every boat-offer NPC is placed >=1x (no dead offer), **G2** every offer NPC placed
in exactly 1 level (no warden-mute), **G3** every placed hub NPC has an offer (no orphan), **G4**
destinations non-zero + record in arz, **G5 (warn)** total offers + worst-level attach vs a
budget. Run against the deployed set it FAILS on exactly the three concrete mutes (G1
svc_testhub_master, G2 svc_testhub_return, G3 svc_testhub_master_cave) and warns on the 30-offer
overflow - i.e. it would have caught this before ship.

## Evidence tooling (all read-only, `tools/debug/`)
`b48_definitive.py` (30 offers by NPC + order), `b48_placements.py` (per-record placement counts),
`b48_arz_records.py` (record identity: sparta==garden except description), `b48_basegame_bounds.py`
(base-game 2 actions/trigger, 20 OnLevelLoad/step, ~5 boat offers max), `b48_audit_table.py` (the
combined cross-reference), `b48_dryrun_fix.py` (fix dry-run), `gate_traveler_responds.py` (gate).
