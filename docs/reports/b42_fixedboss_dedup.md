# b42 - Fixed-placement boss DEDUP + 3-majestic-chest replacement + Ephialtes/Mnemophage

Branch `feat/b42-waking-dread`, base `da918c5` (build38a, arz `6631f252` deployed).
DB-only + map-injection DRY-RUN; NO heavy build. Ground truth:
scratchpad `baseline_build38.arz` (md5 `fcd5dcab`), MAIN `local/Levels_merged.arc`
(md5 `60a62880`, canonical map). Base-game DB `database.arz` + `Toolset/Templates.arc`
for the mechanism proofs.

Round-1 commits: `40e6877` (dedup), `db2d409` (chest region-tune), `03708f0`
(Ephialtes/Mnemophage), `4b3f2d7` (report).
Round-2 commits (this pass, fixing the round-1 vet):
- `61ff15b` DB side - Ephialtes nova castable + chests become 3 world-placed
- `893ceac` map side - world-place 3 majestic chests per fixed uber (INJECT_SPECS)

---

## 0. Round-2 vet fixes (what changed and why)

| vet finding | verdict | round-2 fix |
|---|---|---|
| **HIGH** 3-chest deliverable not delivered (each boss still carried its 1 old chest) | FIXED + PROVEN | boss accessory chest removed on all 4 fixed ubers; **3 world-placed majestic chests each**, produced as a real map-injection DRY-RUN (below) |
| **HIGH** Ephialtes nova castability unproven; report evidence false | FIXED | `skillSpecialAnimationName` cleared -> casts on the default clip like the proven `epiales_poisonorb`; false "Mnemophage casts it" claim removed |
| **MED** size-clip headroom not verifiable offline | FLAGGED as a PROMOTE BLOCKER (sec 4b) - Will's in-game check |
| **LOW** report imprecisions (esti singular; bloodtoxeus mislabelled) | FIXED (sec 6) |

---

## 1. HEADLINE RCA - "two bosses side by side" (unchanged from round 1, correct)

**Root cause (empirically proven):** every mod lone-boss pool is a clone of
`q_leinth_lone`, which carries `proxyPoolEquation = ...\proxypoolequation_02.dbr`. That
equation OVERRIDES the pool's literal spawn/champion counts at spawn time, per field:
`poolValue * (0.91 + 0.497143*numPlayers - 0.05*numPlayers^2)` [FLOORED]. The pools
carry no separate `poolValue`, so `poolValue` binds to the field's own static value. For
the "1 boss + 2 champion escorts" shape (`spawnMax=3, championMax=2, championChance=100`)
at 1 player the factor is 1.357: `spawnMax 3->floor(4.07)=4`, `championMax 2->2` ->
MAINS = spawn - champ = **4 - 2 = 2** = two identical bosses side by side. Deterministic
at every player count (Will plays single-player). Base unique-boss pools
(`bosspool_03_cyclops`, ...) carry NO equation and use `1/1/0.1` -> exactly 1.

**Structural fix (template level, fail-loud):** `_svc_neutralize_pool_equation` empties
`proxyPoolEquation` so the literal counts hold; `_svc_boss_pool` self-neutralizes;
`_svc_lock_authored_pool_counts` sweeps the `_MOD_AUTHORED_SPAWN_PROXIES` registry;
`_verify_mod_spawn_proxies_eligible` is now a HARD gate (any authored pool still
carrying the equation breaks the build). Dedup replay: 16 authored pools go 2-mains ->
1-literal-main; SV-original creature pools untouched; gate raises on a doubling pool and
passes clean. **Re-verified regress-clean this round** (my chest/nova edits did not touch
the dedup path).

---

## 2. Per-boss single-instance audit (1 map placement x 1 main per pool)

| Boss (host) | map placements | pool shape | mains@1P before | after |
|---|---|---|---|---|
| Ephialtes / Waking Dread (Judgment_StoneCity_Exit01) | 1 | 3/2, eq | **2** | **1** |
| Mnemophage (Judgment_TempleUG_Mnemosyne01) | 1 | 3/2, eq | **2** | **1** |
| Tantalus (Styx_SwampBorder_01) | 1 | 3/2, eq | **2** | **1** |
| Charon / Golden Bough (Styx_RiverEdge_01) | 1 | 3/2, eq | **2** | **1** |
| Dorus / Drowned King (Medea_TempleUG_Tomb01) | 1 | 3/2, eq | **2** | **1** |
| Vashkarr / Broodmother / Enslaver / Obsidian x4 | 1 each | eq | 2 (or 2@2P+) | **1** |
| Devourer / Blood-Toxeus | see note | championMax=1 add on `egg_blooddragon` | 1 @1P | unchanged |

Map placement survey confirms each proxy is placed EXACTLY once (no double-placement, no
pre-existing native copy stacked on). Unplaced future bosses (four_generals / diadochi /
neferkha / polis) carry the same latent dup but are 0x in the canonical map and live in
other lanes' modules - flagged, not changed (cross-lane concurrency).

---

## 3. CHEST: 3 large majestic chests per fixed uber (DELIVERED this round)

Will 2026-07-13: *"for all the monsters we placed we need to reduce the chests, replace
the current chest with three large magestic chests."* + region-tuning + the Blood-Toxeus
exclusion.

### 3.1 Why the count needs world-placement (mechanism, proven from Templates.arc)
The current chest is a **boss accessory**: each boss proxy sets
`accessory1/accessoryEpic1/accessoryLegendary1 -> ProxyAccessoryPool -> FixedItemContainer`,
so the chest spawns WITH the boss (difficulty-selected). That mechanism **hard-caps at
ONE chest per difficulty**:
- `proxy.tpl` defines exactly `accessory1`, `accessoryEpic1`, `accessoryLegendary1` and
  **no `accessory2..N`** (read from `Toolset/Templates.arc`; confirmed by scanning 3100
  base proxy records - the highest accessory slot ever populated is `1`).
- `ProxyAccessoryPool.tpl` is `fixedItemChance` + `fixedItemName1..10`/`fixedItemWeight1..10`
  = a single weighted pick, **no spawn-count field**.

So "three chests" cannot come from the accessory mechanism - it needs **world placement**
(0x05 map entities). This matches the round-1 vet's independent conclusion.

### 3.2 The world-placement pattern (the mod's own proven "esti" chest)
`proxy_hidden_bloodcave_chest` (the Blood-Toxeus / esti chest) is itself a bare
`Class=Proxy` **placed as a 0x05 world entity in `drxBC2`** whose
`accessory1/Epic1/Legendary1 -> pool_hidden_01/02/03 -> hidden_bloodcave_chest_01/02/03`
spawn the difficulty-appropriate `FixedItemContainer`. That IS a difficulty-aware
world-chest placer, proven live in-game. So:

- **DB** (`_svc_build_world_chest_proxy`): clone that proxy into a standalone
  `records\drxmap\proxy\svc_<boss>_chest.dbr` per fixed uber, wiring the boss's OWN
  region-tuned hoard pools (`svc_<boss>hoard_pool_{01,02,03}`) as its accessory tiers.
  The 4 fixed ubers' boss proxies now have **empty** accessory slots (the bespoke chest
  no longer spawns WITH the boss). Fail-loud gate `_svc_verify_world_chests` asserts both.
- **MAP** (`UBER_CHEST_SPECS` in `build_section_surgery.py`): place that proxy **3x** in a
  r=2.6u triangle around the boss spawn, APPENDED to the boss's host-level INJECT_SPECS
  list. Result = exactly 3 region-tuned majestic chests at each encounter.

### 3.3 Region tuning (unchanged content, now on the world chests)
`_svc_standardize_boss_chests` repoints each reused chest's `tables` to the base game's
region/level-banded boss loot (`boss_default_<lo>-<hi>`) - the Cyclops chest FORM (a
normal boss chest, **not** the old guaranteed-`unique_1h` hoard nor an Act1/Greece n01
chest). Difficulty tier -> chest `_01/_02/_03`; region -> the boss's charLevel bracket,
capped at the game's top boss tier `63-65`. Large-majestic mesh (`container_hpalace_chestlg01`)
+ Boss-lock kept. **Replay-verified region-differentiated:**

| chest set (region) | N | E | L |
|---|---|---|---|
| svc_tantalushoard (Styx, Act4/Hades) | boss_default_51-53 | 63-65 | 63-65 |
| svc_charonhoard (Styx, Act4/Hades) | 47-49 | 63-65 | 63-65 |
| svc_ephialteshoard (Dread Halls, Act5/Judgment) | 57-59 | 63-65 | 63-65 |
| svc_dorushoard (Medea tomb, Act2) | 41-43 | 57-59 | 63-65 |

(Dorus N=41-43 != Ephialtes N=57-59 proves region separation. The old bespoke
guaranteed-unique loot tables are left unreferenced - the API has no field delete.)

### 3.4 Per-boss chest placement (map-injection dry-run, level-local coords)
Boss centre from UBERBOSS_SPECS; chests at A(+2.6,0) B(-1.8,+1.8) C(-1.8,-1.8):

| Boss | host level | chest A | chest B | chest C |
|---|---|---|---|---|
| Ephialtes | Judgment_StoneCity_Exit01 (v11) | (18.5,3.2,34.7) | (14.1,3.2,36.5) | (14.1,3.2,32.9) |
| Tantalus | Styx_SwampBorder_01 (v0f) | (56.6,-15.2,114.3) | (52.2,-15.2,116.1) | (52.2,-15.2,112.5) |
| Charon | Styx_RiverEdge_01 (v11) | (190.5,-7.0,46.9) | (186.1,-7.0,48.7) | (186.1,-7.0,45.1) |
| Dorus | Medea_TempleUG_Tomb01 (v0e) | (54.6,1.2,60.0) | (50.2,1.2,61.8) | (50.2,1.2,58.2) |

All 12 spots surveyed on the DEPLOYED map: clr **100% in all 3 tilesets, comp#1 (main
walkable component), d<=0.14u** (inside the boss's proven-clear 3.5u ring; 3.6-4.8u apart
so 3 distinct chests). flags=0, identity rot, no 0x14.

### 3.5 HARD EXCLUSION - Blood-Toxeus / Devourer chest stays 100% original
Positively identified: the Devourer (`um_bloodtoxeus_99` / Hemorrheus) guards the
blood-cave waterfall chamber chest = **`hidden_bloodcave_chest_{01,02,03}`** (+ their
`loottable_hidden_bloodcave_{01,02,03}`), world-placed via `proxy_hidden_bloodcave_chest`
in `drxBC2` (this is the "esti's chest" of Will's memory; description tag
`tagHiddenChestNAME`). It is NOT in `_SVC_CHEST_STD` and NOT in the world-chest set; the
replay proves all **6 records byte-identical before/after** every finalizer.

### 3.6 Scope decisions (flagged for Will)
- **Obsidian roulette** (4 corners, chanceToRun=25 each = a rare 25% treasure mini-event
  in the set-piece tombs owned by other lanes): kept as ONE already-de-hoarded region-tuned
  Cyclops-grade accessory chest per corner. 4 corners x 3 = 12 chests would be clutter, and
  it is a random mini-event, not a fixed uber Will fought. **Your call** if you want it on
  the 3-chest treatment too.
- **Mnemophage** carries no chest by design (round-1 spec differentiator). Will's order was
  "replace THE current chest"; there is none to replace. **Your call** if the Mnemophage
  should also get 3 majestic chests.
- **Polis vault** (Will's own 5-majestic-chest vault, unplaced; b41 places it) LEFT ALONE.
- Boss LOOT-TABLE drops (b40 Enslaver tiered loot) are NOT chests - left alone.

---

## 4. Ephialtes BIGGER + real, CASTABLE AOE; Mnemophage BIGGER

**RCA:** Ephialtes's whole fear kit (`ixion_cry`, `Dreamstorm`, `drxvisionofdeath`) is
pure fear/confusion/sleep with ZERO damage - his "fear nova" feared but never hurt.

**HIS Dread Nova (real AOE damage):** clone `ondeath_voidnova`
(`Skill_AttackProjectileRing`, life+physical `[30..600]` by level, 24 `nightstalker_
shadowbolt` bolts in a 360-deg ring) -> `ephialtes_dread_nova`, added to his kit at
`[12/16/20]` and set as PRIMARY `specialAttack @50%` -> **720 / 960 / 1200** (life+phys)
per bolt at N/E/L.

**CASTABILITY (round-2 vet HIGH fix):** the donor carries `skillSpecialAnimationName='Nova'`.
When a special is cast via `specialAttackN` the engine's StartSkill aborts silently if the
caster's mesh lacks that special clip (this project's own crash-law RE). The Ephialtes boss
rides the **Epiales01** mesh (epiales_overlord skin), which has **no 'Nova' clip** -> the
round-1 nova was a **silent no-op**. The proven-castable epiales ring is `epiales_poisonorb`
(same `Skill_AttackProjectileRing`, cast live as a `specialAttackSkillName` by every
epiales-mesh monster: `as_nightmare` / `as_phantasm` / `um_vaekas` / `toxic_phantasm`) and
it carries **no** `skillSpecialAnimationName` -> it casts on the mesh's default attack clip.
**Fix: clear `skillSpecialAnimationName=''`** on our clone so it casts exactly like
`epiales_poisonorb`, keeping the voidnova damage + 24-bolt shape. (The round-1 report's
"Mnemophage casts the same donor live" claim was FALSE - `um_mnemophage_99` carries
`ondeath_voidnova` only in an on-death/passive slot, never a `specialAttackN`. Corrected.)
Fear roar + dread pulse stay @40% so his fear identity is intact.

**BIGGER:** Ephialtes scale `2.2 -> 2.7`, Mnemophage shell `2.5 -> 2.9` (actorHeight 2.4).
Mnemophage kit already carries void-nova + energy-drain (real AOE) - only the size bump.

### 4b. Size-clip headroom = a PROMOTE BLOCKER for Will's in-game check
The "no ceiling/wall clip" requirement **cannot be verified offline** - the navmesh is
floor-only; there is no ceiling-height data without rendering. So neither the implementer
nor an offline vet can prove the scaled Ephialtes (2.7) fits the Dread Halls vault
(15.9,3.2,34.7) or the Mnemophage (2.9) fits the Mnemosyne glyph ring (43.0,3.0,71.0).
Per the mobile/on-device-gate philosophy, **a size change like this needs Will's real
in-game check before ship.** Conservative under the vashkarr scale-3.0 clip-flag precedent;
if either clips, drop that one scale ~0.2 and re-check. **Flagged, do not auto-promote.**

---

## 5. Verification (no heavy build)

- `py_compile tools/apply_svc_patches.py tools/build_section_surgery.py` - OK
- `tools/patches/_check_registry.py` - OK (11 modules, order hash unchanged)
- **CHEST+NOVA DB replay** (`scratchpad/b42/replay_r2_chests.py`, real builders vs a
  baseline copy) - PASS: nova `skillSpecialAnimationName=''` + damage intact; 4 world-chest
  proxies built + wired; 4 boss accessories cleared; 12 chests on the large-majestic mesh
  with region boss_default loot; esti 6 records byte-untouched; obsidian still 1 chest;
  fail-loud `_svc_verify_world_chests` passes.
- **MAP-INJECTION DRY-RUN** (`scratchpad/b42/mapinject_r2.py`, real inject funcs vs
  base-game + deployed host blobs; never touches the real map or main) - PASS: harness
  fidelity (boss-only inject reproduces the deployed 0x05 byte-for-byte on the v0f/v11
  hosts); full inject = exactly 1 boss + 3 chests per level (delta vs deployed = +3, clean
  parse to stream end); Dorus (v0e) every non-0x05 section incl the 0x0b **navmesh
  byte-identical** to base.
- **ON-MESH SURVEY** (`scratchpad/b42/survey_chests.py`) - all 12 chest spots clr 100% in
  all 3 tilesets, comp#1, d<=0.14u.
- **DEDUP replay** + **EP/MN replay** re-run regress-clean (scale 2.7/2.9; nova primary @50%
  720/960/1200; 16 pools 2->1; SV-originals incl `egg_blooddragon` untouched; gate neg/pos).
- **QUESTS 256-parity:** untouched by construction - my map change is 0x05-only (per-blob),
  and QUESTS(0x1b) is a world-level section built by `build_ordered_quest_list` (unmodified).
- No SV-original DESIGN record touched (dedup control group + esti chest proven byte-identical).

---

## 6. Corrections to the round-1 report (vet LOW)

- The esti chest is **`hidden_bloodcave_chest_{01,02,03}`** (+ `loottable_hidden_bloodcave_
  {01,02,03}`) - not a singular `hidden_bloodcave_chest`. All six proven byte-untouched.
- `q_bloodtoxeus_lone` is a **MOD** pool registered in `_MOD_AUTHORED_SPAWN_PROXIES` that the
  dedup fix DOES neutralize (eq -> ''); this is harmless because it is **UNPLACED** (0
  placements in the canonical map 0x05, verified). The SV-original genuinely left untouched
  near the Devourer is **`egg_blooddragon`** (dedup replay control: eqPresent=True).

---

## 7. Integration hand-off / open items

1. **Land the chests + boss-accessory removal into the canonical map** (the integration/map
   lane): re-run `svaera_plus_portals.py` so INJECT_SPECS places the 12 chest proxies, and a
   full DB build so `svc_<boss>_chest` + region-tuned chests are in the arz. A map<->record
   convergence contract should confirm every `records\drxmap\proxy\svc_<boss>_chest.dbr` is
   present in the built arz (they are, replay-confirmed).
2. **Will in-game (BLOCKER):** confirm the scaled Ephialtes/Mnemophage do not clip the vault /
   glyph-ring ceilings; confirm Ephialtes visibly casts the Dread Nova and it damages.
3. **Will's call:** Obsidian roulette + Mnemophage chest scope (sec 3.6).
4. Apply the equation neutralization to the unplaced other-module bosses before they are placed.

---

## 8. INDEPENDENT VET (round 2, adversarial) - VERDICT: GO (with 1 promote-blocker + scope flags)

Re-derived from scratchpad `baseline_build38.arz` (md5 `fcd5dcab`) with own probes (not the
implementer's scripts); MAIN + real map untouched; no heavy build. All CONFIRMED:

- **DEDUP RCA + fix (structural).** proxypoolequation_02 = poolValue*(0.91+0.497143*nP-0.05*nP^2)
  on all 4 count fields; every placed pool (ephialtes/mnemophage/tantalus/charon/dorus/vashkarr/
  broodmother/bloodtoxeus/obsidian) carries it @ 3/2/100 -> floor 4/2 = 2 mains @1P (reproduced).
  Neutralize -> literal 3-2 = 1. Every `_svc_boss_pool` neutralizes at creation; the registry sweep
  covers the direct-clone pools; Mnemophage is double-covered. Negative test PROVES the gate (C)
  raises on a re-injected equation (not blind). All placed bosses = 1.
- **CHEST.** 4 fixed ubers carried an over-good guaranteed-unique accessory chest; all 4 converted -
  boss accessory cleared (fresh-build sim -> [None,None,None]; fail-loud `_svc_verify_world_chests`
  PASSES) + exactly 3 world chests each (INJECT_SPECS boss@idx0 + 3; triangle centre == boss
  placement for all 4, r~2.6u inside the 3.5u ring). Region-tuning REAL: tables -> boss_default_
  <bracket> tracking each boss's per-difficulty charLevel (Dorus 41-43 != Ephialtes 57-59 != Tantalus
  51-53; E/L capped 63-65); boss_default tables exist + byte-distinct; large-majestic mesh + Boss-lock
  kept. Enumeration COMPLETE (Vashkarr/Broodmother/Mnemophage/Hemorrheus/Enslaver carry NO chest).
  DB<->map proxy paths match (no dangling refs). Loot TABLE records unchanged (only pointers repointed).
- **ESTI chest** (um_bloodtoxeus_99 -> hidden_bloodcave_chest_{01,02,03} via proxy_hidden_bloodcave_
  chest in drxBC2) POSITIVELY IDENTIFIED + PROVEN byte-untouched (not in _modified, bytes identical)
  AND out of map scope (change hits only judgment/styx/medea hosts). **Polis vault untouched.**
- **Ephialtes AOE** present (nova @ specialAttack 50%, kit lvl[12/16/20], 720/960/1200 life+phys
  reproduced) + castable (Epiales01 mesh; proven-castable epiales_poisonorb - cast live by
  as_nightmare_43 - carries NO skillSpecialAnimationName; clearing it on the clone = same default-clip
  cast) + crash-safe (monster skill, FX verbatim).
- **Scoped:** DB diff = intended records only (no HP/damage drift; SV-originals not neutralized -
  registry-scoped); map diff = 0x05-only -> QUESTS 256-parity preserved. py_compile OK; _check_registry
  OK (order 7c74a51f); commits clean (HEAD fa2dac4).

**PROMOTE-BLOCKER (sole unverified item):** Ephialtes (2.7/2.4) + Mnemophage (2.9/2.4) ceiling/wall
clip is NOT verifiable offline (navmesh is floor-only). Needs Will's in-game check at the Dread Halls
vault + Mnemosyne glyph ring; if either clips, drop scale ~0.2 and re-check. Correctly flagged (sec 4b).

**SCOPE (Will's call, not defects):** Obsidian roulette kept as 1 de-hoarded region-tuned chest per
corner (not 3); Mnemophage stays chestless. **LATENT (not this wave):** unplaced four_generals/
neferkha/polis share the equation dup - neutralize before placing. **Note:** integration lane still
builds the arz + lands the 12 chest proxies (dry-run proven); the vet did not re-run the navmesh
floor survey (chest centres coincide with already-on-mesh boss spots).
