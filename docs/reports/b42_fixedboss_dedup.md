# b42 - Fixed-placement boss DEDUP + chest standardization + Ephialtes/Mnemophage

Round 1 (branch `feat/b42-waking-dread`, base `da918c5` = build38a, arz 6631f252).
DB-only; no heavy build. Ground truth: scratchpad `baseline_build38.arz`
(md5 `fcd5dcab...`), MAIN `local/Levels_merged.arc` (md5 `60a62880`, canonical map).

Commits:
- `40e6877` DEDUP (proxyPoolEquation neutralize + fail-loud gate)
- `db2d409` CHEST (region-tune + de-hoard)
- `03708f0` EPHIALTES bigger + AOE, MNEMOPHAGE bigger

---

## 1. HEADLINE RCA - "two bosses side by side" (structural, 5th+ dup-class sighting)

**Root cause (empirically proven):** every mod lone-boss pool is a clone of
`q_leinth_lone`, which carries `proxyPoolEquation = records\proxies orient\
proxypoolequation_02.dbr`. That equation OVERRIDES the pool's literal spawn/champion
counts at spawn time with, per field:

```
poolValue * (0.91 + 0.497143*numberOfPlayers - 0.05*numberOfPlayers^2)   [FLOORED]
```

The pools carry NO separate `poolValue` field (verified) -> `poolValue` binds to the
field's own static value. For the "1 boss + 2 champion escorts" shape
(`spawnMax=3, championMax=2, championChance=100`) at **1 player** the factor is 1.357:

| field | static | effective = floor(static * 1.357) |
|---|---|---|
| spawnMax | 3 | **4** |
| championMax | 2 | **2** |

MAINS = spawn - champ = **4 - 2 = 2** -> **TWO identical bosses spawn side by side.**
This holds at EVERY player count 1..6 (always 2 mains), so it is deterministic /
structural, exactly matching Will's report (two Waking Dreads + two Mnemophages) and
his guess "all the monsters we placed we placed two side by side." Single-player is
enough to see it (Will plays single-player).

The `_svc_boss_pool` builders all reason "`spawnMax - championMax = 1` = the LAW" -
true of the LITERAL counts, but the inherited equation silently re-scales them via
the floor. The prior spawn-eligibility gate `_verify_mod_spawn_proxies_eligible`
computed the SAME literal math and only asserted `>= 1`, so it never caught this.

**Contrast - base game unique-boss pools** (`bosspool_03_cyclops`, `_06_alastor`,
`_07a_telkine`, `_24_hydra`, ...) carry **NO proxyPoolEquation** and use
`spawnMax=1 / championMax=1 / championChance=0.1` -> exactly 1 boss. That is the
canonical single-unique-boss shape.

**Second dup vector RULED OUT:** map placement survey over the canonical merged map
shows **each boss proxy is placed EXACTLY ONCE** (no double placement, no pre-existing
native copy our injection stacks on). So the dup is 100% the pool-count scaler.

### Structural fix (template level, one mechanism, fail-loud)
- `_svc_neutralize_pool_equation(db, pool)` - empties `proxyPoolEquation` so the engine
  uses the literal counts verbatim (mirrors base unique-boss pools) -> exactly
  `spawnMax - championMax` mains at every player count. Monster difficulty/level
  scaling is UNAFFECTED (that lives on the proxy's `difficultyEquationFile` /
  `difficultyLimitsFile`, not the pool).
- `_svc_boss_pool` now neutralizes its own clones (Tantalus/Charon/Mnemophage/Ephialtes).
- `_svc_lock_authored_pool_counts(db)` - finalization pass over the
  `_MOD_AUTHORED_SPAWN_PROXIES` registry, covering the hand-rolled pools too
  (Hemorrheus, Vashkarr, Dorus, Broodmother, Enslaver + Obsidian warbands, every yard).
- `_verify_mod_spawn_proxies_eligible` - **new fail-loud check (C):** any authored pool
  still carrying `proxyPoolEquation` breaks the build. This makes the existing literal
  `spawnMax-championMax` math SOUND (nothing re-scales it at runtime).
- Registered `q_vashkarr_lone` (was unregistered -> doubled unnoticed like the rest).

**Dry-run replay (`scratchpad/b42/replay_dedup.py` vs a baseline copy):** 16 authored
boss/warband/yard pools go from equation-present / 2-mains to equation-empty /
1-literal-main; SV-original creature pools (`bw_*`, `hound_*`, `egg_blooddragon`,
`demon_01_*`, `q_leinth_lone`) are UNTOUCHED (still carry the equation - the fix is
surgically scoped); the strengthened gate RAISES on a doubling pool and PASSES clean.

---

## 2. Per-boss single-instance audit (mechanism, before -> after)

"Exactly ONE instance" = 1 map placement (survey) x 1 main per pool (pool replay).

| Boss (host level) | placements in canonical map | pool shape | mains@1P before | after |
|---|---|---|---|---|
| Ephialtes / Waking Dread (Judgment_StoneCity_Exit01) | 1 | 3/2, eq | **2** | **1** |
| Mnemophage (Judgment_TempleUG_Mnemosyne01) | 1 | 3/2, eq | **2** | **1** |
| Tantalus (Styx_SwampBorder_01) | 1 | 3/2, eq | **2** | **1** |
| Charon / Golden Bough (Styx_RiverEdge_01) | 1 | 3/2, eq | **2** | **1** |
| Dorus / Drowned King (Medea_TempleUG_Tomb01) | 1 | 3/2, eq | **2** | **1** |
| Vashkarr (Orient/Random05A) | 1 | 3/2, eq | **2** | **1** |
| Broodmother (TyphonUG/TombObs02) | 1 | 3/2, eq | **2** | **1** |
| Enslaver warband (drxFirstxistion_connection) | 1 | 5/4, eq | 1 @1P, **2 @2P+** | **1 leader** |
| Obsidian roulette x4 (TombObs01/02) | 1 each | 6/5 warband, eq | **2** | **1 guardian** |
| Devourer / Hemorrheus / Blood-Toxeus | see note | championMax=1 add | 1 @1P (**2 @4P+**) | unchanged* |

*Devourer note: `q_bloodtoxeus_lone` is UNPLACED (0x in the map) - the M15 wave rewired
Toxeus to be a `championMax=1` add on the SV-original `egg_blooddragon` pool near the
esti chest. That yields exactly ONE Devourer in single-player (Will's experience) and
only floors to 2 at 4+ players. Its pool is SV-original (touching its equation also
re-scales the blood-dragon count), so it is left as-is per the SV-design law and
flagged for Will's call. Not part of the visible "two side by side" bug.

**Unplaced future bosses (other registry modules, NOT touched here):** the
four_generals (`q_hadesmarshal_lone`), `q_diadochi_lone`, `svc_neferkha_lone`, and the
polis pools (`q_polis_*`, `q_polisgaoler_lone`) carry the SAME `[2,2,2,2,2,2]` latent
dup, but are UNPLACED (0x in the canonical map) and live in separate modules
(`tools/patches/{four_generals,diadochi,neferkha,polis_vault}.py`) owned by other
waves. They will double when placed. **Recommendation:** the owning waves apply the
same `_svc_neutralize_pool_equation` (or register in `_MOD_AUTHORED_SPAWN_PROXIES` so
the new gate covers them). Flagged, not changed, to avoid cross-lane concurrency edits.

---

## 3. Chest standardization (Will: "reduce the chests, replace with 3 large majestic chests, region-tuned")

**Current state (recon):** the placed ubers with a bespoke hoard chest -
Tantalus, Charon, Ephialtes, Dorus, and the Obsidian roulette - each drop a chest
(`FixedItemContainer`, large-majestic mesh `container_hpalace_chestlg01`, Boss-locked)
whose loot is a **GUARANTEED unique 1h (`unique_1h_n01` @ 100%)** + tier-01
(Act1/Greece) statics REGARDLESS of the boss's region -> both OVER-GOOD and
UNDER-LEVELED at a Styx/Judgment/Orient boss. Mnemophage/Vashkarr/Broodmother/Enslaver
carry no chest.

**How the base game tunes majestic/boss chests by region (the brief's investigation):**
the base `bosschest<NN>_<boss>_<difficulty>` family encodes the level tier in the loot
table name: `records\item\containers\defaultloot\boss_default_<lo>-<hi>` spanning L01-L65
in 2-level steps. Higher bracket = later act. The Cyclops chest (`bosschest03_cyclops`,
mesh `ChestBoss01`) uses `boss_default_07-09 / 35-37 / 53-55` (its Act1 per-difficulty
levels) - a NORMAL boss chest, the FORM/rarity reference. The literal "majestic chest"
records are `hero_majesticchest_container_rare` / `_egypt_container_infrequent` (xpack4,
`ChestBoss01` mesh) - base large boss chests, Hero-locked.

**Fix (`_svc_standardize_boss_chests`, finalization pass):** repoint all 15 bespoke
hoard chests' loot to the region/level-appropriate base `boss_default_<bracket>` per
difficulty tier (N/E/L = chest `_01/_02/_03` = the proxy's `accessory1/Epic1/Legendary1`),
capped at the L63-65 top tier. Cyclops-grade, no guaranteed-unique. Kept the
large-majestic mesh + Boss-lock. Fail-loud if a base table is missing.

| chest set (region) | N | E | L |
|---|---|---|---|
| svc_tantalushoard (Styx, Act4) | boss_default_51-53 | 63-65 | 63-65 |
| svc_charonhoard (Styx, Act4) | 47-49 | 63-65 | 63-65 |
| svc_ephialteshoard (Judgment, Act5) | 57-59 | 63-65 | 63-65 |
| svc_dorushoard (Medea tomb, Act2) | 41-43 | 57-59 | 63-65 |
| svc_obsidianhoard (Obsidian Halls, Act3/Orient) | 39-41 | 57-59 | 63-65 |

Region differentiation proven (Dorus N=`41-43` != Ephialtes N=`57-59`). The bespoke
`svc_*hoard_loot_*` tables are left unreferenced (harmless; the API has no field delete).

**HARD EXCLUSION honored:** the Devourer/Blood-Toxeus "esti" chest is
`hidden_bloodcave_chest` (spawned via `proxy_hidden_bloodcave_chest` in `drxBC2` -
the waterfall chamber). It is NOT in `_SVC_CHEST_STD` and is proven byte-untouched in
the replay (`scratchpad/b42/replay_chests.py`).

### 3a. The literal "THREE chests" count - MECHANISM HAND-OFF TO THE MAP LANE
The reward mechanism the current chest uses HARD-CAPS at ONE chest per difficulty tier
(proven from `Templates.arc`): `Proxy.tpl` exposes only `accessory1 / accessoryEpic1 /
accessoryLegendary1`, and `ProxyAccessoryPool` is a single `fixedItemChance` roll +
weighted pick (`fixedItemName1..10`, NO spawn count). So Will's literal "3 chests"
CANNOT come from the accessory mechanism - it requires **world-placement** (0x05
entities / chest-spawner proxies), which is the map lane's domain and is under active
b41 concurrency. This round delivers the reduced, region-tuned chest CONTENT; the
count is handed off with a ready spec:

> **World-placement spec (per chest-bearing boss):** place 2 additional
> `hero_majesticchest`-style FixedItemContainers (mesh `ChestBoss01` or the current
> `container_hpalace_chestlg01`), Boss-locked, loot = the same region `boss_default_<L>`
> bracket, at ~2-3u offsets from the boss's known INJECT_SPECS coord (already on-mesh),
> so total = 1 accessory + 2 world = 3. Boss coords: Ephialtes (15.9,3.2,34.7),
> Mnemophage (43.0,3.0,71.0), Tantalus (54,-15.2,114.3), Charon (187.9,-7,46.9),
> Dorus (52,1.2,60). Dry-run map-injection into a copy of `Levels_merged.arc` +
> on-mesh survey before landing.

**SCOPE flags:** the POLIS VAULT cage (Will's own 5-majestic-chest vault, unplaced;
b41 places it) is LEFT ALONE - flag for Will's call. Boss LOOT-TABLE drops (the b40
Enslaver tiered loot) are NOT chests - left alone.

---

## 4. Ephialtes BIGGER + real AOE damage; Mnemophage BIGGER

**RCA:** Ephialtes's whole "fear kit" (`ixion_cry`, `Dreamstorm`, `drxvisionofdeath`)
is pure fear/confusion/sleep with **ZERO offensive damage** - his "fear nova" feared
but never hurt. (`ephialtes_flamewave` is a fire-SLOW, also no damage.)

Fix (in the OWNING builder `_create_dreadhalls_uberboss`):
- **HIS Dread Nova:** clone the proven `ondeath_voidnova` (Skill_AttackProjectileRing,
  life+physical `[30..600]` by level, 24 `nightstalker_shadowbolt` projectiles in a
  360-deg ring - already nightmare-themed) into `ephialtes_dread_nova.dbr`,
  byte-identical to the donor (clone-shape invariant safe). Added to his kit at level
  `[12/16/20]` and set as the PRIMARY `specialAttack @ 50%` -> real castable AOE damage
  **720 / 960 / 1200** (life+phys) per bolt at N/E/L. The Mnemophage casts the same
  donor live, so it is AI-castable (the "ondeath" name is legacy; no death trigger).
  Fear roar + dread pulse stay in the rotation @40% so his fear identity is intact.
- **BIGGER:** Ephialtes scale `2.2 -> 2.7`, Mnemophage shell `2.5 -> 2.9` (actorHeight
  bumped to 2.4). **HEADROOM:** the exact clip-free max needs Will's in-game check
  (Dread Halls vault ceiling / Mnemosyne glyph ring) - I cannot measure ceiling height
  offline (navmesh is floor-only). Flagged, not assumed; conservative under the
  vashkarr scale-3.0 clip-flag precedent.
- Mnemophage (4b): its kit ALREADY carries `void-nova` + `energy-drain` (real AOE
  damage) - no boss-skill treatment needed beyond the size bump.

**Dry-run replay (`scratchpad/b42/replay_ep_mn.py`, real builders vs a baseline copy):**
Ephialtes 2.7 + nova wired as primary special @50% with 720/960/1200 dmg; Mnemophage
2.9 with void-nova + energy-drain present. PASS.

---

## 5. Verification summary (no heavy build)

- `py_compile tools/apply_svc_patches.py` - OK
- `tools/patches/_check_registry.py` - OK (11 modules, order unchanged)
- DEDUP replay - PASS (16 pools 2->1 main; SV originals untouched; gate neg/pos)
- CHEST replay - PASS (15 chests region-repointed; esti untouched; region-differentiated)
- EP/MN replay - PASS (scales up; dread nova castable + damaging; Mnemophage AOE intact)
- Map placement survey - each audited proxy placed EXACTLY once (no double-placement)
- Map NOT edited -> QUESTS 256-parity + navmesh trivially preserved
- No SV-original design record touched (dedup control group + esti chest proven)

## 6. Open items for the vet / next round
1. Land the 3-chest world-placement (spec in 3a) via the map lane, dry-run verified.
2. Apply the equation neutralization to the unplaced other-module bosses
   (four_generals/diadochi/neferkha/polis) before they are placed.
3. Will in-game: confirm the boss scale-ups do not clip the Dread Halls vault /
   Mnemosyne glyph ceilings; confirm Ephialtes casts the Dread Nova and it damages.
4. Full DB build + record-diff vs baseline (integration step; owned by the build lane).
