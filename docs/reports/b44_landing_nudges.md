# b44 LANDING NUDGE SPECS - for the consolidated-build integrator

> **Trust level: SURVEY + GATE (apply during consolidated build).** Read-only recon. This file
> emits concrete nudged coords for the ONLY two incoming **b39 hub-v2** landings that still collide
> with a placed 0x05 entity once b41 (map-pass) placements exist. The b44 lane does NOT write to the
> b39 / b41 / b42 worktrees - the integrator applies these when merging `feat/b39-hub-v2`
> `HELOS_HUB_TRAVEL`.

Source of truth: `tools/debug/gate_landing_clearance.py --wiring v2 --placements b41b42 --nudge`
against the deployed DEV map (`Levels.arc` md5 **841c56cd**).

> **Round 2 fix (2026-07-13).** The nudge search now walks the **INTEGER-world lattice** and validates
> clearance AT the exact integer coord it emits. Round 1 validated a FLOAT level-local point but emitted
> its ROUNDED coord, which could round back under a class margin (the devourer float optimum re-surveyed
> at 2.57u but its rounded coord was only **2.40u < the 2.5u prop min** - a nudge the gate itself rejects,
> shipped as "cleared"). The integer-lattice search closes that gap; each coord below is now the very
> point the gate validates, cleared by a class-min + 0.5u robustness buffer on fully-walkable footing.
> Applying BOTH nudges to the v2 set and re-gating vs b41b42 yields **GATE G-LAND: PASS = 25 landings,
> 0 DEADLY / 0 FAIL** (pre-verified against the deployed map).

## The v2 set is otherwise CLEAN

All 5 formerly-DEADLY boss landings (dorus/tantalus/charon/mnemophage/ephialtes) that pin+kill the
player TODAY are already fixed by the b39-v2 retarget to area ENTRANCES (they now PASS, 20-130u off
their bosses). The b41 Toxeus ambush (`q_bloodtoxeus_ambush` in drxFirstRoom, local 100,50) is 236u
from the v2 warband landing (local 200,264) - clear. **b42-waking-dread as built (@ 4b3f2d7) is
DB-only** (boss-pool dedup + existing-hoard loot tuning) and adds NO new map placements, hence no new
collision sources; a hypothetical "3 majestic chests per boss" ring (r=5u, modeled in the gate as a
conservative stress test, NOT b42's actual output) still leaves every v2 landing well clear (the
entrances are 20-130u off the bosses; nearest is the mnemophage entrance ~15u from a modeled chest).
Only the two below need a nudge.

## NUDGE 1 - devourer  (DEADLY today in the v2 set)

- **Destination level:** `Levels/World/xBloodCave/drxBC2.lvl` (blood-cave combat chamber, ~92u off Toxeus).
- **Current v2 coord:** world `(5345, 1, 3010)` = local (70,55) -> lands **0.58u** from `burstvessle_01.dbr`
  (a DRX destructible blood-vessel = solid collision until killed), dead-center in a dense burst-vessel
  cluster (6 vessels within ~1.7u) -> player pinned (DEADLY).
- **NUDGE TO:** world **`(5349, 1, 3009)`** = local (74,54)  (a 4.1u shift, same Y).
  - re-surveyed on-mesh Normal/Epic/Legendary = **100%/100%/100%**, main component.
  - **clears the vessel cluster:** nearest solid prop **3.16u** (`rock_hc_pitboulder04`, >= the 2.5u
    prop margin + buffer); nearest burst-vessel 3.52u; nearest unclassified pit decoration
    (`pitwedge01`) 2.83u (> the 1.5u pin distance). ROBUST.
  - Still lands the player in the drxBC2 chamber amid the demon/hound packs, just at the EDGE of the
    vessel field instead of inside it. Re-run the gate on the BUILT map and re-nudge if a built-map
    vessel position differs.

## NUDGE 2 - sparta  (FAIL today in the v2 set)

- **Destination level:** Athens catacomb `CataCube02_FloorLast` (deepest catacomb, the Sparta-Crypt
  DOOR retarget), amid beastmen.
- **Current v2 coord:** world `(-6588, 1, -3180)` = local (24,38) -> lands **2.72u** from
  `AG_Beastmen_Gorgon_02N.dbr` (a live gorgon; the gate classifies it **proxy** - its record path is
  under `\Proxies\`) -> spawns nearly on top of the mob (< the 3.0u proxy margin).
- **NUDGE TO:** world **`(-6587, 1, -3180)`** = local (25,38)  (a 1.0u shift, same Y).
  - re-surveyed on-mesh **100%/100%/100%**, main component.
  - nearest collider after nudge: **3.69u** to the gorgon (>= the 3.0u proxy margin). ROBUST. Still
    lands the player into the beastman fight, just not on a body.

## Apply + verify

Apply both to `feat/b39-hub-v2` `HELOS_HUB_TRAVEL`, rebuild the map, then gate the BUILT map:

```
py tools/debug/gate_landing_clearance.py --map local/Levels_merged.arc --wiring v2 --placements b41b42
```

Expect **GATE G-LAND: PASS** (0 DEADLY / 0 FAIL) - already pre-verified against the deployed map (the
v2 set with both nudges applied gates PASS=25). If a future wave ever authors real chests near a boss,
re-gate with `--placements <b42_specs.py>` (a `SPECS = {level_key: [(dbr,x,y,z), ...]}` file, LEVEL-LOCAL).
