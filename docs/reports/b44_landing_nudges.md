# b44 LANDING NUDGE SPECS - for the consolidated-build integrator

> **Trust level: SURVEY + GATE (apply during consolidated build).** Read-only recon. This file
> emits concrete nudged coords for the ONLY two incoming **b39 hub-v2** landings that still collide
> with a placed 0x05 entity once b41 (map-pass) + b42 (3-chests-per-boss) placements exist. The b44
> lane does NOT write to the b39 / b41 / b42 worktrees - the integrator applies these when merging
> `feat/b39-hub-v2` `HELOS_HUB_TRAVEL`.

Source of truth: `tools/debug/gate_landing_clearance.py --wiring v2 --placements b41b42 --nudge`
against the deployed DEV map (`Levels.arc` md5 841c56cd). Every nudged coord was re-surveyed
on-mesh (all 3 tilesets 100%) and cleared of every collidable entity by its class margin.

## The v2 set is otherwise CLEAN

All 5 formerly-DEADLY boss landings (dorus/tantalus/charon/mnemophage/ephialtes) that pin+kill the
player TODAY are already fixed by the b39-v2 retarget to area ENTRANCES (they now PASS, 20-130u off
their bosses). The b41 Toxeus ambush (`q_bloodtoxeus_ambush` in drxFirstRoom, local 100,50) is 236u
from the v2 warband landing (local 200,264) - clear. The b42 3-chests-per-boss model rings each build36
boss at r=5u; the nearest v2 landing (mnemophage entrance) is ~15u from a modeled chest - clear. Only
the two below need a nudge.

## NUDGE 1 - devourer  (DEADLY today in the v2 set)

- **Destination level:** `Levels/World/xBloodCave/drxbc2*` (blood-cave chamber, ~92u off Toxeus).
- **Current v2 coord:** world `(5345, 1, 3010)` -> lands **0.58u** from `burstvessle_01.dbr` (a DRX
  destructible blood-vessel = solid collision until killed) -> player pinned.
- **NUDGE TO:** world **`(5347, 1, 3008)`**  (a 3.0u shift, same Y).
  - re-surveyed: on-mesh Normal/Epic/Legendary = 100%/100%/100%, main component.
  - nearest collider after nudge: 2.57u to `burstvessle_01` (>= the 2.5u solid-prop margin). Still
    "amid the demon/hound packs" as intended. Re-run the gate on the BUILT map and widen a touch if
    the built-map vessel position differs.

## NUDGE 2 - sparta  (FAIL today in the v2 set)

- **Destination level:** Athens catacomb `catacube02_floorlast` (deepest catacomb, the Sparta-Crypt
  DOOR retarget), amid beastmen.
- **Current v2 coord:** world `(-6588, 1, -3180)` -> lands **2.72u** from `AG_Beastmen_Gorgon_02N.dbr`
  (a live gorgon monster) -> spawns nearly on top of a mob (< the 3.0u monster margin).
- **NUDGE TO:** world **`(-6587, 1, -3180)`**  (a 1.0u shift, same Y).
  - re-surveyed: on-mesh 100%/100%/100%, main component.
  - nearest collider after nudge: 3.72u to the gorgon (>= 3.0u monster margin). Still lands the
    player into the beastman fight, just not on a body.

## Apply + verify

After applying both to `feat/b39-hub-v2` `HELOS_HUB_TRAVEL` and rebuilding the map, gate the BUILT map:

```
py tools/debug/gate_landing_clearance.py --map local/Levels_merged.arc --wiring v2 --placements b41b42
```

Expect **GATE G-LAND: PASS** (0 DEADLY / 0 FAIL). If b42 authors real 3-chest coords, replace the
model: `--placements <b42_specs.py>` (a `SPECS = {level_key: [(dbr,x,y,z), ...]}` file, LEVEL-LOCAL).
