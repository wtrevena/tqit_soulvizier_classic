# b44 LANDING CLEARANCE - RCA + permanent gate + cross-wave audit

> **Bug (Will, 2026-07-13):** *"When you teleport me to these places from the portal hub you teleport
> me inside of the chest and I cant move or fight the guys and I instantly get killed... i cant move
> and i die."*
>
> **Trust level: RCA + SURVEY + GATE.** Read-only against the DEPLOYED DEV map
> (`.../SoulvizierClassicDEV/Resources/Levels.arc` md5 **841c56cd**, the TESTHUB Will is playing;
> Quests.arc md5 838bdc3a). No map/DB build. This lane owns `tools/debug/gate_landing_clearance.py`
> + these reports only; it does NOT write to the b39/b41/b42 worktrees.

## 0. TL;DR

- **Root cause CONFIRMED.** The v1 Helos traveler-hub's five IT-superboss destinations teleport the
  player **0.00-0.32u on top of the boss set-piece** (`q_<boss>_lone` proxy). The proxy's collision
  pins the player in place; the boss then kills him instantly. This is a whole **class** of bug -
  LANDING-vs-PLACED-ENTITY collision - that no prior gate checked (`survey_uberboss_spots.py` checks
  navmesh walkability + clearance but NOT occupancy by a placed 0x05 entity, so an on-mesh spot that
  sits on the boss passes every prior gate).
- **The "chest":** at the 5 boss undergrounds the current-map collider is the boss proxy itself (+ its
  tomb set-dressing), not a literal chest. The co-located reward containers arrive with b42
  (3-chests-per-boss) which would only compound it. Mechanism is identical either way: land on a
  placed entity -> pinned -> dead.
- **Permanent gate authored:** `tools/debug/gate_landing_clearance.py` - on-mesh AND per-class
  clearance from every collidable placed entity, containers largest margin; accepts EXTRA planned
  placements so a wave can gate BEFORE building; `--nudge` emits the closest clear coord. Wired into
  the **travel-invariants family** in `docs/PLAYBOOK.md` §12.
- **Cross-wave audit:** the incoming **b39 hub-v2** set (boss landings retargeted to area ENTRANCES)
  FIXES all 5 deadly landings (they now PASS). Against current + b41 + b42-model placements, only **2**
  v2 landings still collide (devourer, sparta) - concrete nudges emitted in
  `docs/reports/b44_landing_nudges.md`.

## 1. RCA - the deadly landings TODAY (deployed map 841c56cd, v1 wiring)

Landing coords come from `build_quest_files.HELOS_HUB_TRAVEL` (world signed-int = grid_corner +
level-local). For each landing the gate resolves the destination level by (x,z) box containment,
converts to level-local (`local = world - corner`), and measures the distance to every placed 0x05
instance (authoritative flag-aware walk, base 72 for v0x11/v0x0f else 56, section-end-verified).

### 1.1 DEADLY - player pinned on a boss set-piece (THE bug Will hit)

| landing | world (x,y,z) | dest level (ver) | local (x,z) | nearest placed entity | dist | on-mesh |
|---|---|---|---|---|---|---|
| **dorus** | (312,1,-8462) | Medea_TempleUG_Tomb01 (v0e) | (52.0,60.0) | `q_dorus_lone.dbr` (boss proxy) | **0.00u** | 100% main-comp |
| **tantalus** | (-342,-15,-10095) | Styx_SwampBorder_01 (v0f) | (54.0,114.3) | `q_tantalus_lone.dbr` | **0.30u** | 100% main-comp |
| **charon** | (-336,-7,-9650) | Styx_RiverEdge_01 (v11) | (188.0,47.0) | `q_goldenbough_lone.dbr` | **0.14u** | 100% main-comp |
| **mnemophage** | (170,-10,-11438) | Judgment_TempleUG_Mnemosyne01 (v11) | (43.0,71.0) | `q_mnemophage_lone.dbr` | **0.00u** | 100% main-comp |
| **ephialtes** | (-1828,3,-13285) | Judgment_StoneCity_Exit01 (v11) | (16.0,35.0) | `q_ephialtes_lone.dbr` | **0.32u** | 100% main-comp |

These are exactly the **build36 boss SPEC-PRIMARY spots** (`survey_uberboss_spots.BOSS_SPOTS`): the v1
hub reused the boss placement coord as the landing coord. Every one is on-mesh 100% clear (that is why
it shipped) - the missing check is that a placed `q_<boss>_lone` proxy already occupies the spot. The
proxy spawns the boss AT that cell; the player teleports into the same cell, cannot separate from the
body, and is killed. (b45/b47, separate waves, are independently relocating the Tantalus/Dorus
encounters - consistent with this finding.)

### 1.2 FAIL - secondary tight spot

| landing | world | dest level | local | nearest | dist | note |
|---|---|---|---|---|---|---|
| **sparta** | (-5602,-2,-1409) | SpartaCryptLevel2 (v0e) | (42.0,42.0) | `greece_sarcophagia02_02.dbr` (solid sarcophagus) | **2.38u** | on-mesh; 2.38u < the 4.0u container margin - a crampable spot even without a boss |

### 1.3 PASS (11) - clear today

garden, secret, uber, bossarena, warband + all 6 returns. Two informational NOTES:
- **uber** lands **0.09u** from `portal_olympianarena2.dbr` - a portal PAD (non-colliding: you stand
  on it), so it does not pin. Flagged as a note to verify in-game it does not re-trigger travel.
- **returns** land at the Helos plaza **1.1-1.3u** from the outbound traveler NPCs (svc_helos_trav_*).
  NPCs are soft-collision (crowd, don't pin+kill), so this is a crowding NOTE, not a failure - the
  known "crowded plaza" already tracked (b37 CHORE d).

`GATE G-LAND: FAIL` (5 DEADLY + 1 FAIL) on the deployed map = the bug reproduced deterministically.

## 2. THE GATE - `tools/debug/gate_landing_clearance.py`

A permanent, reusable HARD gate in the **travel-invariants family** (alongside
`entrance_landing_check.py`). For every teleport landing it asserts BOTH:

1. **On-mesh** (reuses `survey_uberboss_spots` machinery via a precomputed integer cell-index set):
   within `cs*2.5` of a walkable cell in ALL 3 tilesets, on a non-tiny navmesh component. Calibrated
   so a landing on a large (non-island) region of a big overworld hub passes even when it is not the
   single largest component (avoids false CHECKs); low footing clearance is a NOTE, off-mesh / a
   `<500`-cell island is a CHECK.
2. **Clear of every collidable placed 0x05 entity** by a per-class center-to-center margin:

   | class | examples | min clear | rationale |
   |---|---|---|---|
   | container | chests, `*container*`, strongboxes, reward | **4.0u** | the reported bug; largest margin |
   | monster | `um_/am_/...`, creatures, heroes | 3.0u | a live body body-blocks + attacks |
   | proxy | `q_*_lone`, guardpair, warband, ambush, spawners | 3.0u | spawns a body AT the spot |
   | prop | walls, columns, sarcophagi, rocks, urns, tombs, DRX vessels/egg-sacs | 2.5u | solid collision |
   | npc | travelers, portal-masters, villagers, caravan | note only | soft collision (crowds, no pin) |
   | portal | portal/teleport/grid-entrance pads | note only | non-colliding (walk onto them) |
   | soft | lights, sound, FX, POI markers | ignored | non-colliding |

   A landing is **DEADLY** if a hard/unknown collider is within `PIN_DIST` = 1.5u (the player spawns
   inside the entity - Will's report), **FAIL** if a hard collider is within its (larger) class-min.

Key features:
- **Extra planned placements:** `--placements b41|b42|b41b42|<file>` folds LEVEL-LOCAL specs
  (`SPECS = {level_key: [(dbr,x,y,z), ...]}`) into the destination-level entity set, so a wave gates
  its landings against entities **not on the map yet**.
- **Landing sets:** `--wiring v1` (LIVE `build_quest_files.HELOS_HUB_TRAVEL`) | `v2` (b39 hub-v2,
  embedded w/ provenance) | `<file>` (a `LANDINGS = [(name,(x,y,z),tag)]` module).
- **`--nudge`:** for every DEADLY/FAIL landing, spiral-searches the closest on-mesh coord that clears
  all colliders and prints it (world = corner + nudged local).
- Read-only, exit 0 = all clear. Robust across the 2282-level index (dual-base 0x05 walk verified to
  the section end).

## 3. CROSS-WAVE AUDIT (read-only)

### 3.1 Current deployed map, v1 wiring
`--wiring v1` -> **5 DEADLY + 1 FAIL + 11 PASS** (Section 1). This is the bug in production today.

### 3.2 b39 hub-v2 landing set vs current + b41 + b42-model
`--wiring v2 --placements b41b42` -> **23 PASS + 1 DEADLY + 1 FAIL**.

- **All 5 boss landings now PASS.** The b39-v2 retarget moves them to area ENTRANCES 20-130u off the
  boss (dorus tomb entrance, Styx swamp/river stairs, Mnemosyne stairs, Dread-Halls stairs), clearing
  the `q_<boss>_lone` proxies. **The v2 hub fixes the reported bug.**
- **b41 (map-pass) interaction:** the only v2 landing sharing a level with a b41 placement is
  **warband -> drxFirstRoom**; b41 adds `q_bloodtoxeus_ambush` at local (100,50); warband v2 local
  (200,264) is **236u** away = clear. All other b41 placements (polis cage + 5 chests in
  HadesPalace_Floor04_01, Menoetes/guards, Helepolis in Elysian, Neferkha + 4 sarcophagi in
  ThebesOptTombA) are in levels **no** hub landing targets = no interaction.
- **b42 (3-chests-per-boss) model:** rings each build36 boss at r=5u (b42-waking-dread is an EMPTY
  branch at da918c5 - no real coords authored yet; modeled synthetically). Nearest to any v2 landing
  is the **mnemophage** entrance at ~15u from a modeled chest = clear. The v2 entrances are 20-130u
  off the bosses, so the incoming chests do not threaten them. When b42 authors real coords, re-gate
  with `--placements <b42_specs.py>`.
- **2 residual v2 collisions** (both NEW v2 destinations, not boss-reuse):

  | v2 landing | world | collides with | dist | nudge -> |
  |---|---|---|---|---|
  | **devourer** | (5345,1,3010) | `burstvessle_01.dbr` (DRX destructible, solid) | 0.58u (DEADLY) | **(5347,1,3008)** clears to 2.57u |
  | **sparta** | (-6588,1,-3180) | `AG_Beastmen_Gorgon_02N.dbr` (live gorgon) | 2.72u (FAIL) | **(-6587,1,-3180)** clears to 3.72u |

  Both nudged coords re-surveyed on-mesh 100%/100%/100%, main component. Full specs +
  apply/verify steps: `docs/reports/b44_landing_nudges.md` (for the consolidated-build integrator to
  apply to `feat/b39-hub-v2` `HELOS_HUB_TRAVEL`).

## 4. Reproduce

```
# the bug today (expect FAIL: 5 DEADLY + 1 FAIL):
py tools/debug/gate_landing_clearance.py \
  --map "<...>/SoulvizierClassicDEV/Resources/Levels.arc" --wiring v1

# the v2 fix + cross-wave audit + nudges (expect 2 residual, both nudgeable):
py tools/debug/gate_landing_clearance.py \
  --map "<...>/SoulvizierClassicDEV/Resources/Levels.arc" \
  --wiring v2 --placements b41b42 --nudge
```

## 5. Recommendation

1. **Ship the b39 hub-v2 retarget** - it is the fix for the 5 deadly boss landings.
2. **Apply the 2 nudges** (devourer, sparta) from `b44_landing_nudges.md` during the b39/b41 consolidated build.
3. **Gate the BUILT map** with `gate_landing_clearance.py --wiring v2 --placements b41b42` before deploy; require **GATE G-LAND: PASS**.
4. If shipping v1 in the interim is ever considered, note **sparta v1** (2.38u sarcophagus) is also a
   crampable spot; prefer the v2 sparta retarget.
