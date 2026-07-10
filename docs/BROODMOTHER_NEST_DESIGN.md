# BROODMOTHER NEST - design (deferred wyrm set-piece) + Tartarus-gates / Atlantis recon

> **Trust level: DESIGN (sign-off-first).** No production records exist yet. This is a
> design spec + recon finding for a FUTURE implement wave, in amgoz1's voice, ready to hand
> to a DB-lane + map-lane pair the same way OBSIDIAN_ROULETTE_DESIGN.md was. Produced
> 2026-07-10 (post build32-ship). House style: no em dashes.
>
> **Context.** build32 Group G (N7) shipped the Sepulchral Wyrm Hordes: the 6 Act-3 tomb
> `ug_demon_wyrmsprite_0{1,2,3}{n,t}` encounters became escalating cold-wyrm hordes (tiers
> 4/8, 6/12, 8/16) that drop the Sepulchral Scale charm. The horde work deliberately
> DEFERRED a broodmother NEST set-piece to a later MAP wave (it needs a new host-level
> injection, not just a pool repoint). This doc is that deferred design. Everything below is
> re-verified against the shipped build32 artifacts this session: arz `9265619d`
> (`work/.../SoulvizierClassic.arz`), canonical map `d5259629`, base game
> `Database/database.arz` + `Resources/XPack3/Quests.arc`.
>
> **Taste anchors (Will's law, from HANDOFF and the memory board):** "crazier the better";
> NO artificial caps; souls follow the amgoz1 bible; the ONE summon is earned by great
> beasts; all refs must resolve; MANUAL-CAST law (a summon soul binds Skill_SpawnPet with
> NO itemSkillAutoController); the boss-kit clone-shape invariant; MP RunEquation caveat.

---

## 0. THE PITCH (one paragraph)

Deep in the Act-3 tombs where the wyrm hordes thicken, the player breaks into a hatchery: a
vaulted chamber ringed with pulsing egg clusters and one titanic mother wyrm coiled over the
brood. She is the source of the hordes. While she lives, the eggs never stop hatching, so the
fight is not "kill the adds then the boss", it is "kill the mother BEFORE the room fills",
because there is no cap on how many wyrmlings the nest can pour out. Kill her and the brood
that survives becomes loot: the guaranteed apex Sepulchral Scale plus, at a hunter's chance,
her own soul, the ONE summon of this set (she raises a wyrm of your own on the render-proven
Eater-of-Days rig). This is the climax the horde tiers were building toward.

---

## 1. LOCATION CANDIDATES (byte-verified host levels; site-survey pattern)

**Region is fixed by theme:** the sepulchral wyrms are native ONLY to the Act-3 Orient tomb
complex (namespace `records\creature\monster\sepulchralwyrm\...`; the horde proxies live in
`records\proxies orient\area007 - tomb\...`). The nest belongs in that same tomb chain, as
the deepest room, so it reads as the source of the hordes the player just fought up through.

Three tomb levels in that region are ALREADY byte-verified this build cycle to carry large,
flat, on-mesh floor (their 0x0b navmeshes were surveyed for build32a/b set-pieces), so they
are the concrete host candidates. The survey evidence (committed in the build32 map-lane
notes and `build_section_surgery.py`) already proves open space in each:

| Candidate host `.lvl` (map key) | Byte-verified open-floor evidence (this build cycle) | Role today |
|---|---|---|
| `levels/world/orient/typhonug/tombobs02.lvl` | Obsidian corners A@(50.4,143.6) + C@(200.4,97.6) surveyed **100% clearance in a 3.5u square, walkable in all 3 tilesets** (build32b); the level 0x0b is byte-identical across the M10 wire (parse-back gate). Wide multi-alcove hall. | Obsidian roulette corners A/C |
| `levels/world/orient/typhonug/tombobs01.lvl` | Obsidian corners B@(220.8,89.6) + D@(92.8,47.6) surveyed **100% clearance / all tilesets**; flat floor probe local Y ~1.2. | Obsidian roulette corners B/D |
| `levels/world/orient/underground/random05a.lvl` | Vashkarr host; the level's own 0x0b has **60,356 walkable set-0 cells** (survey-exact parity), on-mesh spot at (24.0,1.0,31.7) 95% clear in a 3.5u square. | Vashkarr + Majestic Chest |

**Recommended primary host: `tombobs02` (Obsidian Halls / TyphonUG).** It is the deepest,
largest Act-3 tomb hall, it is the SAME hall the Obsidian roulette already dresses (so the
"treasure-tomb climax" reading is coherent), and its floor is the most byte-proven open of the
three. A broodmother nest and the roulette coexist cleanly because the roulette corners are
25%-per-corner (usually empty) and the nest is one fixed placement far from all four corners.

**Fallbacks (ranked):** (a) `tombobs01` (its own large hall, corners B/D leave the center
open); (b) `random05a` (60k-cell cave, but Vashkarr + the native Hero_Djinn_BloodSisters
proxy already stack there, so a third boss is crowding); (c) a fresh survey of the other
`orient/typhonug/*` and `orient/underground/*` tomb blobs if a dedicated empty chamber is
wanted (the wyrmsprite hordes' own host levels, resolvable from the placed
`area007 - tomb` proxies, are the natural first look).

**SITE-SURVEY PROCEDURE the map lane runs at implement time (the exact M9/M10 pattern; do
NOT hardcode coords from this doc without re-surveying):**
1. Decompress the built canonical map once, get the host blob, load its 0x0b navmesh.
2. Pick a candidate nest-center in an OPEN part of the hall away from the roulette corners
   and native proxies (nest wants a big footprint: aim for a >= 8u-radius clear disc for the
   mother + the egg ring + the wyrmling churn).
3. For the mother spot AND each egg-cluster spot: probe on-mesh in ALL 3 tilesets (radius
   0.4/0.6/0.8), measure clearance % over a 3.5u/49-sample square; require walkable in every
   tileset and 100% clearance. If a spot is tight (walkable only at radius 0.4, < 100%),
   NUDGE +/-2.0 within the pocket until 100%/all-tilesets (Obsidian corner-D precedent), then
   re-probe. Record the floor Y from the navmesh; keep the spec's Y at the floor.
4. Feed the surveyed spots into `INJECT_SPECS` (section 6 table), rebuild both map variants,
   run the parse-back gate (0x05 instance-count delta == number of injected proxies, appended
   flags=0 exemplar-rot, every OTHER section incl. the 0x0b byte-identical), navmesh 24/24,
   groups-bindings 374/374, det-2x.

Because the nest is ONE encounter (a small cluster of proxy placements in one existing
level), it uses the proven v0e SVAERA-host injection branch (`svaera_plus_portals.py`,
first-lived M9, byte-clean on tombobs01/02 in M10). NO new level, NO navmesh generation, NO
0x14 (all placements are proxies/props, the q_leinth_lone exemplar byte-shape: flags=0,
identity rot, no 0x14).

---

## 2. THE ENCOUNTER (crazier the better, no artificial caps)

### 2a. THE BROODMOTHER (boss)

Derive from **`records\creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr`** (the DRX
"Eater of Days", `DRX\meshes\eaterofdaysmesh.msh`, the LARGEST wyrm rig in the pack). This rig
is already **render-verified AND summon-safe** in the shipped mod: build31 D13 ("Eater of
Days summon soul") built `summon_eaterofdays` + `pets\eaterofdays_{1,2,3}` on it and it
passed the D19 mobility + summon-pet STRICT gates. So the broodmother reuses a rig the mod
has ALREADY proven playable, both hostile and as a pet. (Alternative rig if a distinct
silhouette from the D13 pet is wanted: the `SepulchralWyrm01` proxy mesh, D5-render-verified
for Voranthys/Group F.)

Follow the `_create_vashkarr` boss recipe exactly (Monster.tpl clone -> free to add resist
fields; boss passives; a real scaling `attackSkillName`; specialAttack rotation):

| Field | Value | Rationale |
|---|---|---|
| `monsterClassification` | `Boss` | souls drop; sits with the region set-piece bosses |
| `charLevel` | `[40, 58, 74]` | the Obsidian-guardian / Ilsevar band (same Act-3 tomb region) |
| `characterLife` | `[22000, 30000, 40000]` | above Vashkarr (12/16.5/21k), below Ormenos (27-31k epic); a real apex wall so the "kill her before the room fills" tension lands |
| `scale` / `actorHeight` | `~1.9` / `~2.4` | visibly the mother; largest wyrm in the room |
| resist wall | `defensiveLife 100`, `defensivePierce 60`, `defensiveCold 80` (she IS the cold), `defensivePhysical 30` | boss durability; NOT overtuned into unkillable |
| kit `skillName*` | dragonliche/wyrm cold kit + `sepulchralwyrm_firebreath` + the BROOD-SUMMON (2c) + boss passives (`boss_conversionimmunity` clone, hero/boss scaling, globalproperties N/E/L) | anim-safe on the eaterofdays rig (D13 proved the rig casts + moves); all refs existence-checked at implement |
| `specialAttackSkillName` | the brood-summon | she summons OFTEN (specialAttackChance ~55) so the nest churns even without the static egg clusters |

### 2b. EGG CLUSTERS (the ring, continuous hatch)

The functional "egg cluster" is a **static hatch-spawner proxy** (the proven mechanism: a
`Proxy` with `chanceToRun=100` + `pool1` + a no-cap limits file, exactly the wyrm-horde and
Vashkarr shape). Place **4 to 6** of them in a ring around the mother:

- Each `q_broodnest_egg_{a..f}.dbr` (clone the `q_leinth_lone` proxy donor, as Vashkarr did):
  `chanceToRun = 100`, `pool1 = pools\demon\svc_broodnest_hatch.dbr`,
  `difficultyLimitsFile = limit_broodnest.dbr` (no-cap, herolimit_all clone).
- `svc_broodnest_hatch.dbr` (clone a firesprite/wyrmhorde pool): `name1..4 =`
  `um_sepulchralwyrm_common_31` (the Group-G common wyrmling, Common, no soul drop),
  `spawnMin/Max = 3/6` per cluster, `championChance 0` (the clusters are pure fodder; the
  champions come from the mother's wave).
- Ring of 6 clusters x (3..6 each) = a steady 18-36 wyrmlings refreshing as they die, with NO
  cap (no-cap limits file), on TOP of the mother's own wave. That is the "no artificial caps,
  crazier the better" brief satisfied structurally, not by a big number.

**Optional visual layer (render-verify item, flagged):** co-locate `Decoration` egg-sac props
(a sepulchral / spider-egg mesh from the DRX or base underground scenery arcs) at each cluster
so the ring READS as eggs, not just empty spawn points. This is cosmetic and MUST pass the
render-chain gate (mesh + texture resolve, 0 bad shaders); if no clean egg mesh resolves, ship
the nest functional without props and add them in a later polish pass. Do NOT block the
set-piece on the prop.

### 2c. THE MOTHER'S WAVE (uncapped brood-summon)

Her signature skill = a burst summon on the proven `yaoguai_summonshadowstalkers` clone
(Vashkarr's `_VK_MINION_SUMMON` pattern, registered with the boss-kit clone-shape invariant):

- `spawnObjects = [um_sepulchralwyrm_common_31]` (the wyrmlings), plus a second tier that
  rolls in the 4 CHAMPION worms `um_sepulchralwyrm_{31,34,37,40}` as "elder brood" at lower
  weight for spectacle.
- `petBurstSpawn = 4`, `skillCooldownTime ~5s`, **`petLimit = 24`** (deliberately huge = "no
  cap" in spirit; the engine still needs a finite petLimit, but 24 living mother-spawned worms
  plus the 6 static clusters is a genuinely full room). If the summon-pet gate objects to 24,
  fall back to the highest value it accepts; the static egg ring carries the density regardless.

**Escort (guaranteed lieutenants), via the proxy pool (2d):** 2 champion worms
(`um_sepulchralwyrm_40`) always flank the mother, so the fight opens hot.

### 2d. THE NEST PROXY + POOL (the mother placement)

The mother is placed by ONE lone-boss proxy (the Vashkarr `spawnMax=3 / championMin=Max=2`
shape = 1 boss + 2 guaranteed champion escorts):

```
q_broodmother_lone.dbr        (Proxy, clone q_leinth_lone donor)
  chanceToRun            = 100.0
  pool1                  = pools\demon\svc_broodmother_pool.dbr
  difficultyLimitsFile   = limit_broodnest.dbr        (no-cap, [1..110] contains L74)
  mesh                   = <eaterofdays preview silhouette>   (Vashkarr set a preview mesh)
  scale                  = 1.9

pools\demon\svc_broodmother_pool.dbr   (ProxyPool, clone q_leinth pool donor)
  name1=name2=name3      = um_broodmother_99            (the boss)
  spawnMin=spawnMax      = 3
  championChance         = 100.0 ; championMin=championMax = 2
  nameChampion1          = um_sepulchralwyrm_40         (elder-worm escort)
  nameChampion2          = um_sepulchralwyrm_40
  nameChampion3          = ''  ; weightChampion3 = 0    (clear the clone leftover, Vashkarr fix)
  weightChampion1=Champion2 = 50 / 50
```

Boss-guarantee accounting holds: `spawnMax(3) - championMax(2) = 1` guaranteed main = the
mother (the shipped LAW). Egg clusters (2b) are SEPARATE proxies, so the mother is never
crowded out of her own pool.

---

## 3. THE SOUL (amgoz1's voice, the ONE summon)

She is a great beast, so per Will's rule she EARNS the summon (Chimera/Hydra precedent; the
mod's own Voranthys/Eater-of-Days summon standardization). Name flat and iconic:

- **`{^F}Broodmother Soul`** (not "Soul of the Broodmother"). Tag into
  `work/SoulvizierClassic/Database/uber_soul_tags.txt`.
- **Grant = the ONE SUMMON:** manual-cast `summon_broodmother` via `_build_boss_summon` on the
  eaterofdays rig, D19-hardened (mobility assert + full manual-cast law: Skill_SpawnPet,
  itemSkillName set, **NO itemSkillAutoController**, absent shape not ''). The mod ALREADY has
  the exact donor chain shipped: `summon_eaterofdays` + `pets\eaterofdays_{1,2,3}` (build31
  D13). Cleanest path: build `summon_broodmother` + `pets\broodmother_{1,2,3}` as a fresh
  `_build_boss_summon` job (label it in the D13-family jobs list), OR, if Will prefers zero new
  summon records, point the Broodmother soul at the shipped `summon_eaterofdays` (same rig,
  same fantasy). Recommend a fresh `summon_broodmother` so her pet can carry a small brood-
  themed twist (a low-petLimit friendly wyrmling-spawn of its own, the pet-of-pet pattern the
  Enslaver soul already ships).
- **Exactly 2 skill augments** (thematic drx* player skills): `drxcoldaura` + `drxdeathchillaura`
  (the Dragon-Liche / Voranthys cold precedent). Optionally `+1 augmentMasteryName` to a cold
  or summoning tree if Will wants the Toxeus-style flourish.
- **One weird signature stat:** `defensiveFreeze = 100` (the Dragon-Liche weirdness, on-theme
  for the cold mother) or `offensiveFearMin = 2` (the brood makes the dead fear). Plus a dense
  idiosyncratic sheet: cold/vitality offense, life + life-regen, pet-bonus lines (she is a
  summoner soul), a slice of `characterDefensiveAbility`.
- **Drop:** 66% Finger2 (`SVC_RELEASE_DROPS` convention), per-tier icons, `validate_tags`
  gated. Only the MOTHER drops it (the champion escorts + wyrmlings are Common/no-soul).

---

## 4. LOOT HOOK (tie into Sepulchral Scale + the soul)

The nest is the apex of the wyrm-horde chain, so it is the guaranteed source of that chain's
charm at full tier, PLUS her soul:

1. **Guaranteed apex Sepulchral Scale (tier 03).** The Group-G charm `svc_sepulchralscale\03`
   (`_WH_CHARM['03']`, lvlReq 56, cold/frostburn/cold-slow/life + completion fear 3) currently
   drops at only 7% off the 4 champion worms. The broodmother drops the tier-03 scale at a
   HIGH guaranteed-ish chance (recommend a dedicated `lootMisc` slot at 100% via the tier-03
   loot table `svc_sepulchralscale\03_sepulchralscale`, the D10 wiring the horde already uses),
   so the nest is where a player reliably completes their Sepulchral Scale. This makes the
   horde charm feel like it was building toward the nest.
2. **The Broodmother soul (section 3)** at 66% Finger2.
3. **Optional apex charm upgrade (flag for Will):** a 4th/5th-tier "Broodmother's Scale"
   (Emberscale 5-shard pattern, one rung above tier-03: deeper cold + a small pet-bonus line,
   the summoner-mother flavor). Recommend HOLDING this unless Will wants a charm ladder past
   tier-03; the guaranteed tier-03 + the soul is already a strong double reward per the
   Obsidian-doc "chest + soul is already a double reward" judgment.

---

## 5. RECORD PLAN + INJECT SPEC (ready for an implement wave)

### 5a. DB lane (`apply_svc_patches.py`, new `_create_broodmother_nest(db, tags)`)

Orchestrate in the `_create_vashkarr` + `_create_wyrm_hordes` idiom (clone donors, override
existing fields only on kit clones, `_modified.add`, fail-loud on missing donors):

| # | Record (`records\...`) | Donor | Notes |
|---|---|---|---|
| 1 | `creature\monster\sepulchralwyrm\um_broodmother_99.dbr` | `...\um_eaterofdays_45.dbr` | Boss, band [40,58,74], HP [22k,30k,40k], scale 1.9, cold resist wall, kit + brood-summon |
| 2 | `skills\...\svc_broodnest_summon.dbr` | `yaoguai_summonshadowstalkers` | burst 4 / cd 5s / petLimit 24; spawnObjects = common wyrm (+ champion tier); boss-kit clone invariant |
| 3 | `...\svc_broodnest_hatch.dbr` (pool) | a `firesprite_0x_general06` pool | egg-cluster pool; name1..4 = `um_sepulchralwyrm_common_31`; spawn 3/6; champ 0 |
| 4 | `proxies orient\pools\demon\svc_broodmother_pool.dbr` | `q_leinth_lone` pool | 1 boss + 2 `um_sepulchralwyrm_40` champions; Vashkarr accounting |
| 5 | `drxmap\proxy\q_broodmother_lone.dbr` | `q_leinth_lone` proxy | chanceToRun 100, pool #4, no-cap limit, preview mesh |
| 6 | `drxmap\proxy\q_broodnest_egg_{a..f}.dbr` (4-6) | `q_leinth_lone` proxy | chanceToRun 100, pool1 = #3, no-cap limit |
| 7 | `proxies orient\limit_broodnest.dbr` | `proxies boss\herolimit_all.dbr` | no-cap, window contains L74 |
| 8 | `skills\soulskills\summon_broodmother.dbr` + `pets\broodmother_{1,2,3}.dbr` | via `_build_boss_summon` (D13 job) | manual-cast, D19 mobility + damage-sanity |
| 9 | `item\equipmentring\soul\sepulchralwyrm\broodmother_soul_{n,e,l}.dbr` | bare `_ensure_record` (never clone_record for souls) | grant #8, 2 cold augments, weird stat, 66% Finger2 |
| 10 | loot wiring | Group-G `svc_sepulchralscale\03` table | tier-03 scale at high chance on the mother's `lootMisc` |
| 11 | (optional) egg-sac `Decoration` props | DRX/base egg mesh | cosmetic; render-gate or drop |

New tags (Text.arc COUPLED with the arz): `tagSVCMonsterBroodmother`, `tagSVCSoulBroodmother`
+ desc, `tagSVCSummonBroodmother`, and the pet nameplate. `validate_tags` must pass (every
new arz name/desc tag present in Text.arc).

### 5b. Map lane (`build_section_surgery.py` INJECT_SPECS + `svaera_plus_portals.py` v0e branch)

MAP-REF-1 ordering: the DB records (esp. the `q_broodmother_lone` + `q_broodnest_egg_*`
proxies) MUST land in the arz FIRST; the map lane then injects placements. Spec shape (the
Vashkarr/Obsidian tuple; **coords are placeholders, the map lane SURVEYS them per section 1**):

```
BROODNEST_HOST_KEY = 'levels/world/orient/typhonug/tombobs02.lvl'   # recommended; survey to confirm
BROODNEST_SPECS = {
  BROODNEST_HOST_KEY: [
    (b'records\\drxmap\\proxy\\q_broodmother_lone.dbr',  MX, MY, MZ, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    (b'records\\drxmap\\proxy\\q_broodnest_egg_a.dbr',   AX, AY, AZ, {'rot': Q_LEINTH_EXEMPLAR_ROT}),
    ...  # 4-6 egg clusters in a ring around (MX,MY,MZ), each surveyed on-mesh/all-tilesets/100%
  ],
}
# merged into INJECT_SPECS collision-guarded (the Obsidian M10 merge precedent); v0e branch.
```

Deploy coupling: the arz + Text ship together (new tags); the map (Levels) ships with its
coupled Quests only if a Quests change is needed (none is: the nest is pure proxy placement,
no quest). Levels + arz are independent artifacts but the placements are inert until BOTH the
records (arz) and the placements (map) are present, so ship them in the same wave.

### 5c. Gates (fail-loud, the shipped set)

DB: summon-pet STRICT (the Broodmother soul manual-cast, NO controller; the pet mobile +
damage-sane), spawn-eligibility (`spawnMax - championMax >= 1` on the mother pool),
clone-shape invariant (the summon clone), soul-activation + soul-augment, `validate_tags`,
render-chain (the eaterofdays rig + any egg prop), golden-freeze (Occult/Hunting untouched),
contracts GATE (0 P0/0 P1), det-2x reproducible (same MD5 twice). MP: RunEquation spawn-scale
sanity on the new pools. Map: parse-back (host 0x05 count += number of injected proxies, all
appended flags=0 exemplar-rot, every other section incl. the 0x0b byte-identical), navmesh
24/24, groups-bindings 374/374, on-mesh re-verify of every surveyed spot, det-2x both variants.

### 5d. Risks / honest flags

- **Density vs framerate:** 6 clusters + a 24-petLimit wave in one room is a LOT of active
  actors; verify on Will's (slow) machine that the nest does not tank FPS. Tune cluster count /
  spawnMax down if needed; the design intent (uncapped churn) survives at 4 clusters + petLimit
  ~16 if 6/24 is too heavy.
- **petLimit ceiling:** the summon-pet gate may reject 24; use the highest accepted value.
- **Egg-prop mesh:** may not resolve cleanly; ship functional-without-props if so.
- **Coexistence with the Obsidian roulette in tombobs02:** place the mother far from all 4
  roulette corners (survey confirms separation); accepted that a jackpot roulette + the nest can
  co-fire (reads as "the tomb is alive"), matching the Obsidian-doc "the warden walks" stance.
- **MP:** RunEquation spawn-scaling is the standing caveat; the new pools inherit the same risk
  as every SV pool.

---

## 6. TARTARUS ARENA GATES / ATLANTIS-REACHABILITY RECON

> BACKLOG carried a conditional: "Tartarus arena gates dead IF Atlantis act reachable,
> verify." This section resolves the condition from map + quest bytes, analyzing the Atlantis
> transition the SAME way the IT-to-Scandia (Ragnarok) and IT-to-EE (Eternal Embers)
> neutralizations were analyzed. Evidence gathered this session against the base game
> `Resources/XPack3/Quests.arc` + the shipped mod `Quests.arc` (`work/.../Quests.arc`,
> 110 qst) + the committed audits `DEAD_CONTENT_AUDIT_2026-07-10.md` and `IT_ENDPOINT_AUDIT.md`.

### VERDICT: Atlantis is **REACHABLE for an Atlantis-DLC owner** (UNREACHABLE without the DLC). The 16 Tartarus arena gates are **DEAD** (no loaded opener in Custom Quest).

### 6a. How the two IT-endpoint caps work (the precedent)

The mod hard-caps the campaign at Hades by porting TWO base controller quests into its own
`Quests.arc` with ONE act-portal `Action_UnlockFixedItem` surgically removed each
(`build_quest_files.py`):
- **IT -> Ragnarok(Scandia):** `xquest_controlsbossdoors.qst` (idx 118). The post-Hades
  Persephone trigger fires three `Action_UnlockFixedItem`: `fixeditemtyphonportal` (KEPT),
  `portal_hadesscandia` (**REMOVED** = the Ragnarok act portal), `endportal_hades` (KEPT,
  the no-DLC credits portal). `_neutralize_bossdoors_it_to_scandia`.
- **IT -> Eternal Embers:** `x4_other_001_control_expansionportals.qst` (idx 232), the
  IT->EE `Action_UnlockFixedItem` removed. `_neutralize_expansionportals_it_to_ee`.

Both transitions are **post-Hades** (Persephone-after-Hades trigger). That is the key: the two
caps only touch transitions that fire FROM a Hades-end state.

### 6b. The Atlantis transition is Rhodes-side, and NOTHING caps it

Atlantis in TQAE is **not** a post-Hades act. It branches from **RHODES**, mid-Immortal-Throne,
which is on the mandatory spine (Olympus -> Rhodes via the xq00 fix -> Hades). Parsed from base
`XPack3/Quests.arc` `x3mq_atlantisadventure.qst` (byte-extracted this session), the entry chain
is entirely conditions that FIRE in Custom Quest and mechanisms the mod itself uses:

```
Condition_OnLevelLoad          -> Action_IlluminateNpc(x3mq_marinos_rhodes.dbr)   [Marinos lit at Rhodes]
Condition_ConversationStart    -> Action_BoatDialog(rhodes_boatmantogadir.dbr)    [Rhodes -> Gadir; "MapUnlockAtlantis"]
Condition_ConversationStart    -> Action_BoatDialog(gadir_boatmantomalta / ...toafrica / ...toatlantis)
```

Every gate here is CQ-satisfiable: `Condition_OnLevelLoad`, `Condition_ConversationStart`,
`Action_IlluminateNpc`, `Action_BoatDialog`. `Action_BoatDialog` is the EXACT data-driven
teleport the mod ships for its own Helos and Olympus portal-masters (proven to work in Custom
Quest). There is NO engine-internal campaign hook and NO locked-static-portal dependency in the
Atlantis entry. Critically:

- The mod's own `Quests.arc` ships only TWO DLC-controller quests, both the neutralized ones
  (`xquest_controlsbossdoors`, `x4_other_001_control_expansionportals`). It ships **zero**
  `x3mq_*` / Atlantis quests (verified: 0 matches). So `x3mq_atlantisadventure.qst` is inherited
  **byte-intact from the base XPack3 archive** via the map's 256-QUESTS registry. The mod has
  NOT capped the Rhodes->Atlantis boat chain the way it capped Scandia and EE.
- `DEAD_CONTENT_AUDIT_2026-07-10.md` (LANE A) already resolved the 256/256 loaded quests and
  named `xpack3tartarusportal` and `x3quest_controlsbossdoors` among the LOADED controllers;
  `IT_ENDPOINT_AUDIT.md` established the mod's DLC quest-identity set == vanilla minus 2 dev
  stubs (`x4_dev_001/002`). `x3mq_atlantisadventure` is a vanilla registry entry, not a dev
  stub, so it is in the load window.

**Therefore:** an Atlantis-DLC owner walking through Rhodes gets Marinos (OnLevelLoad),
boat-dialogs to Gadir/Malta/Africa/Atlantis, and reaches the Atlantis act exactly as in
vanilla. A non-DLC player has no Atlantis levels/NPCs/assets (the mod even ships empty 2048-byte
XPack3 stub `.arc`s), so Atlantis is UNREACHABLE for them and the arc ends at Hades as designed.
This is a genuine GAP relative to the "campaign ends at Hades for ALL DLC combos" standing rule:
that rule was proven for the post-Hades Ragnarok/EE transitions, but the **Rhodes-side Atlantis
boat chain was never in scope of the two IT-endpoint caps.**

### 6c. The Tartarus portal loads; the 16 arena gates do not

- **Tartarus ENTRY portal = loaded + CQ-satisfiable.** Base `xpack3tartarusportal.qst`
  (byte-parsed): `Condition_OnLevelLoad -> Action_IlluminateNpc(senechaloftartarus_gadir)`,
  then `Condition_ConversationStart + Condition_OwnsTriggerToken -> Action_UnlockFixedItem(
  records/xpack3/tartarus/portaltotartarus.dbr)` (and `...fromcorinth`). All CQ-firing
  conditions. So a DLC owner who reaches Atlantis/Gadir CAN open the Tartarus entry portal.
- **The 16 arena gates = DEAD.** `records\xpack3\scenery\atlantis\08tartarus\structure\
  infrastructure\tartarus_entrance_gate01.dbr` (FixedItemDoor, locked=1, solid collision) is
  placed 16 times (once per Tartarus arena). NO quest in ANY of the 6 arcs references it (the
  DEAD_CONTENT LANE A sweep verified this across mod + 5 base arcs). In vanilla these open via
  the Tartarus arena wave-clear ENGINE system, which is not driven by any loaded quest, so in
  Custom Quest the gates never open. Tartarus is enterable but dead-ends at the first arena gate.

### 6d. Recommended action

Two coherent options; recommend (1), consistent with Will's standing "campaign ends at Hades
for ALL DLC combos / DLC integration CANCELLED" policy:

1. **CAP the Rhodes->Atlantis entry, same surgical shape as the two existing caps
   (RECOMMENDED).** Port `x3mq_atlantisadventure.qst` into the mod `Quests.arc` with the FIRST
   boat step neutralized: remove the single `Action_BoatDialog(rhodes_boatmantogadir.dbr)` (or
   the whole INIT trigger's transition action) from the "Second Talk Marinos" step, so the
   Atlantis map-unlock never fires. Identity is already registered (Quests.arc-only change, no
   map rebuild, IF idx < 256 confirmed). Net: no DLC owner leaves Rhodes for Atlantis; the whole
   Atlantis + Tartarus branch (and its 16 dead gates) becomes moot-by-unreachability, exactly
   like the neutralized Scandia/EE acts. Fail-loud guard: removed == 1, the rest of the quest
   round-trips, Marinos' non-transition dialogue preserved. This closes the BACKLOG item
   without building any Tartarus content.
2. **MAKE Tartarus playable (only if Will WANTS the Atlantis endgame).** Add a Tartarus
   controller quest mirroring the Greek/xpack2 boss-door pattern:
   `Condition_KillAllCreaturesFromProxy(<per-arena wave proxy>) -> Action_UnlockFixedItem +
   Action_OpenDoor(tartarus_entrance_gate01)` per arena, registered inside the 256-window. This
   is a large, DLC-owner-only effort that also REOPENS a DLC act, contradicting the standing
   rule, so it needs explicit Will sign-off before any work.

### 6e. Cheap residual confirmations for the implement wave (do these first)

- Confirm `x3mq_atlantisadventure.qst`'s exact index in the shipped map's 256-QUESTS registry
  is < 256 (a targeted QUESTS-section parse; the audits already imply it, but option (1)'s
  "Quests.arc-only, no map rebuild" claim depends on it). If it is OUTSIDE the window, Atlantis
  is already unreachable and NO action is needed (verify Marinos never triggers).
- Confirm `x3mq_marinos_rhodes.dbr` is actually PLACED in a Rhodes level in our map (a
  case-insensitive 0x05 scan, the DEAD_CONTENT method). If Marinos is not placed (SVAERA may
  have dropped him), Atlantis is ALREADY unreachable and the finding downgrades to
  "UNREACHABLE, no action", making the 16 dead gates permanently moot.

---

## 7. OPEN DECISIONS FOR WILL (sign-off gates)

1. Location: `tombobs02` (recommended) vs `tombobs01` vs a fresh dedicated tomb chamber?
2. Broodmother rig: reuse the D13 Eater-of-Days rig (recommended, proven) vs a distinct
   SepulchralWyrm01 silhouette?
3. Egg-cluster count / density: 6 clusters + petLimit 24 (crazier) vs 4 + 16 (FPS-safe)?
4. Soul summon: fresh `summon_broodmother` with a pet-of-pet brood twist (recommended) vs
   reuse the shipped `summon_eaterofdays`?
5. Loot: guaranteed tier-03 Sepulchral Scale + soul (recommended) vs also add a 4th-tier
   "Broodmother's Scale" charm rung?
6. Egg-sac visual props: attempt (render-gate) vs ship functional-only?
7. **Tartarus/Atlantis (section 6d): cap the Rhodes->Atlantis entry (recommended, matches the
   IT-endpoint policy) vs build the Tartarus arena controller (reopens a DLC act, needs
   explicit approval) vs do nothing (leave Atlantis reachable + Tartarus dead-ending for DLC
   owners)?**
