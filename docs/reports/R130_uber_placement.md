# R-130 - R-100 #8/#9/#10/#14/#16/#16b: placement, chests, and the walking-path law

> Lane: `fix/uber-placement` (worktree `.claude/worktrees/map-placement`). MAP + LOOT.
> Ruling of record: **R-130** in `docs/WILL_RULINGS.md`. Baseline for every diff below:
> a map built from `main` in this same environment (see sec 6).

---

## 1. Headline

| # | item | status |
|---|---|---|
| 8 | Tantalus outside the Den of Tantalus | **FIXED + GATED.** Root cause proven; he is now inside the den, which is a CAVE, not the outdoor level |
| 9 | Tantalus has 3 chests, wants 1 | **FIXED**, scoped as a class |
| 10 | Soul of the Unferried also has 3 | **FIXED** by the same class change (it is the same b42 mechanism) |
| 14 | Lower City of Lost Souls uber: no chest, trash orb | **CHEST HALF FIXED + GATED** (round 2, R-131). Orb half: measured, and the measurement inverts the premise - **PENDING Will decision**, see sec 8 |
| 16 | Destroyer of Cities: no chest, stands in the walking path | **BOTH HALVES FIXED.** Path in round 1; **chest in round 2 (R-131)**, riding the relocated boss so it is off-path by construction |
| 16b | STANDING RULE + audit every existing placement | **RULE DEFINED, GATED, FULL AUDIT DELIVERED** (sec 5) |

---

## 2. #8 - why the b45 fix "did not hold": it held, and implemented the wrong target

The brief required finding out why the completed b45 task did not stick before re-placing.
**It did stick.** Measured on the deployed DEV map (`Levels.arc` md5 `943d0ab9516d332db79bd7f9fd2d3ffe`):

```
[755] XPack\Levels\Area04_Styx\Styx_SwampBorder_01.lvl  corner=(-396,0,-10209)
   #71  records\drxmap\proxy\q_tantalus_lone.dbr    local=(34.00,-13.40,106.00)
```

That is exactly b45's coordinate, not the pre-b45 `(54,-15.2,114.3)`. The fix shipped.

**The Den of Tantalus is not that level.** Three independent proofs:

1. **Area banner** (the binding the game itself uses to paint the top-right area name;
   RE'd + proven across all 2282 levels in `b46_minimap_result.md`) - resolve each level's
   0x17 REGION guid against the world SD (0x18) and Text:
   * `Styx_SwampBorder_01` -> **"Stygian Marsh"** (`xtagRegionName33`)
   * `Styx_CaveUG_FrogCamp01/02/03` -> **"Den of Tantalus"** (`xtagRegionName80`)
2. **The door.** SwampBorder_01 instance #24 `ext_hc_cliffwall01.dbr` @ local (27,-13,115)
   carries a 48-byte 0x14 GridEntrance binding whose destination GUID `620fd291..` resolves
   to `Styx_CaveUG_FrogCamp01.lvl`. The den is a three-tile cave complex behind that mouth.
3. **The marker b45 optimised against.** `pj_denoftantalus.dbr` is `Class=AreaOfInterest`,
   `AreaDescription=xtagPOI12`, and `xtagPOI12 = "Den of Tantalus"` in the base game's
   `xui.txt`. It is a **signpost**, standing 2.8u in front of that cave mouth, outdoors.

So b45 moved the boss from 28.1u to 10.2u from an outdoor signpost. Ten units from a signpost
that stands in front of a cave puts you **right in front of the cave, outside it** - Will's
exact sentence. The metric was incapable of answering the question, not misapplied.

**The fix:** host changes to `Styx_CaveUG_FrogCamp02` (the den's treasure chamber), local
**(30.0, 1.0, 40.0)**.

| property | value | how measured |
|---|---|---|
| area banner | **Den of Tantalus** | `gate_uber_placement.py` ORACLE 1 |
| on-mesh | d=0.14u N/E/L, comp#1 / 89,831 cells | `survey_uberboss_spots.py` |
| clearance | clr@3.5 **100/100/100**, clr@6.0 **100/100/100** | same |
| floor Y | 1.0 | `navmesh_floor_y.py` reads 1.20; the navmesh quantises one `ch` step (0.2) high, and every native floor instance in the level is authored at 1.00 |
| collision | nearest functional native 9.33u, nearest anything 8.82u | >6u guard PASS |
| walking path | FrogCamp02 is a DEAD END - 1 gateway cluster, 0 through-routes | #16b satisfied by construction |
| depth | ~100u of walking from the gateway; 9.3u from the den's own golden hoard | BFS distance field |

The Helos **area-return NPC deliberately stays outside** in the marsh (it is the travel
landing). That is why `TANTALUS_OUTDOOR_HOST_KEY` survives as its own constant - without it
the relocation would have dragged the return NPC into the cave. This was caught and fixed
before the build.

---

## 3. #9/#10 - one chest, scoped as a class

Will reported Tantalus (3 chests) and the Unferried (3 chests). **The Unferried IS the
Charon / Golden Bough encounter**, so both reports are the single b42 round-2
`_chest_triangle` mechanism, not two coincidences.

`_chest_triangle` becomes `_chest_ring(..., count=UBER_CHEST_COUNT)` with
**`UBER_CHEST_COUNT = 1`**, applied to all four b42 fixed ubers (Ephialtes, Tantalus,
Charon/Unferried, Kroisos/Dorus). Fixing only the two he reached would have left the other
two carrying the identical three-identical-chests arrangement, i.e. a guaranteed repeat
report.

Safety properties:
* **Nothing retired.** No DB record is deleted or blanked. Every `svc_*_chest` proxy still
  exists and is still placed (once). The bosses still carry no accessory chest, and the
  region-tuned hoard chains are untouched.
* The surviving chest keeps the b42 triangle's own already-surveyed "A" offset, so **no new
  coordinate is invented** by this change.
* There is no build invariant asserting a count of 3 (checked: the "assert placed exactly 3x"
  language in `apply_svc_patches` is a comment, never implemented), so nothing reds.
* One constant reverses the whole thing.

---

## 4. #16 - the Helepolis off the walking path

Will's "machine uber boss destroyer of cities" is **The Helepolis, Taker of Cities**
(`q_diadochi_lone`), in `Elysian_Fields_03`.

| | old (b41) | new |
|---|---|---|
| local | (20.7, 4.0, 81.7) | **(70.0, 8.8, 80.0)** |
| distance to nearest shortest route | **0.0u** (literally on the line) | **18.9u** |
| on-path gateway pairs | (1,2) and (1,3) | **none** |
| clr@4.0 / clr@6.0 | - | 100/100/100 and 100/100/100 |
| on-mesh / component | - | d=0.14u, comp#1 / 242,100 |
| nearest native | - | 10.0u (decorative wall); nearest monster proxy 11.4u |

Floor Y 8.8 = the navmesh read (9.00) minus the level's own measured one-`ch`-step bias; the
old spot's authored 4.0 against a navmesh read of 4.20 confirms the same constant, and the
level's natives in that court are authored at 8.90/9.00.

**The one taste trade-off, flagged for Will:** the entire western half of that meadow is the
corridor (the best western candidate still measured 6.7u from a route, inside the 12u
engagement disc), so the fix costs him adjacency to the two native `xsq25` siege striders -
the Helepolis now stands ~45u east of them, in the walled court. If he would rather keep him
among his kin and accept the path adjacency, it is a coordinate change.

---

## 5. #16b - the standing rule, made measurable, and the FULL audit

### 5.1 The definition

`tools/debug/gate_uber_placement.py`. Gateways = tile-edge crossings + 0x06/0x14 door mouths,
clustered by 8-adjacency. Multi-source BFS gives, for each gateway pair, the exact
on-shortest-route set `{c : dA[c] + dB[c] <= dist(A,B) + slack}`. An encounter **BLOCKS** if
deleting its 6u footprint disconnects a pair; it is **ON-PATH** if its 12u engagement disc
touches a shortest route.

**The calibration is as load-bearing as the metric.** The raw ON-PATH test failed **15 of 20**
shipped placements. That cannot be right - Will named exactly one. The difference is the
LEVEL: in a tight dungeon corridor the level *is* the path and there is nowhere else to put
anything; in an open field there is. So ON-PATH only fails where **>= 25% of the level is
off-path** (an alternative demonstrably exists); below that it prints
`ON-PATH(UNAVOIDABLE)` and never gates. Planted negative N4 locks this behaviour in both
directions.

### 5.2 Full audit of EVERY existing placement (built map, post-fix)

**PASS (in area, off path):** Tantalus (now), Helepolis (now), Mnemophage, Kroisos/Dorus,
Vashkarr, Neferkha + 4 sarcophagi, generals A and C, the Endless Hunt, Aniketos, Broodmother
+ 6 eggs, roulette c and d, and every surviving `svc_*_chest`.

**ON-PATH(UNAVOIDABLE) - corridor levels, reported, never gated:** the whole Polis Daemonai
warden cage in `hadespalace_floor04_01` (Gaoler + Limos + bloodwitch + vindicator +
lieutenant), 22% off-path.

**AUDITED + ACCEPTED (on-path, NOT changed, registered as debt):** 9 placements. These are
listed in `ACCEPTED_ON_PATH` in the gate with a per-entry reason and printed on every run -
not hidden, not silently "fixed". Moving bosses Will has not complained about is how
regressions get introduced.

| placement | why it stands |
|---|---|
| `q_bloodtoxeus_ambush` | DELIBERATE AMBUSH - b79/Will: the Devourer must spawn "with his guys next to the tattered parchment". On-path is the design |
| `q_enslaver_warband` | same corridor ambush set-piece |
| `q_general_b_guardpair` | honor guard ~6u beside general B's own xsq27 proxy; adjacency IS the design |
| `q_hadesmarshal_lone` | Menoetes in the central hall; Will has fought him without complaint. **Will-call** |
| `q_ephialtes_lone` + chest | Dread Halls terminal vault, the "back corner" Will himself ordered. **Will-call** |
| `q_goldenbough_lone` + chest | Shrine of the Golden Bough forecourt, a destination shrine. **Will-call** |
| `q_obs_roulette_a` | roulette CORNER - a 25% mini-event prop, not an uber monster we place |

**RED, deliberately left red - a genuine new finding (`BL-R130-DEBT-3`):**
`q_obs_roulette_b` in `TombObs01` @ (220.8,89.6) reads **BLOCKS-ROUTE**: it sits at the mouth
of the narrow east corridor that is the only link between the level's two gateway clusters.
Honest bound on the claim: it corks at the default **6.0u** footprint and does **not** at
**4.0u** or below, so it is a marginal chokepoint and the verdict is sensitive to the radius
policy. A roulette corner is a dial + pool + chest, so its own body is small - the practical
question is whether the pack it spawns plugs the corridor in play. Out of this lane's scope
(a prop, not an uber Will reported); escalated rather than silently accepted or silently
moved.

---

## 6. Build + proof

```
BASELINE  main @ 9a12d17, built in this environment, isolated worktree
          md5 718abad63e7813dc78c4b169df969fd5   688,692,225 B
BRANCH    fix/uber-placement, SVC_OUT_DIR isolated
          md5 92b3b921de2033799b624e0941e37c7a   688,690,290 B
env       PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1 PYTHONIOENCODING=utf-8
```

`main` advanced from `7efd107` to `9a12d17` mid-lane; the only new commit touches
`docs/` + `docs/wip_workflows/`, no map tooling, so the map baseline is unaffected.

### Record-diff (`tools/debug/diff_maps_blobs.py`)

**6 levels differ, all `0x05`-only, and `navmesh (0x0b) changes: 0`** - the b89 blood-cave
crash class cannot have been touched. Every single delta is attributable:

```
medea_templeug_tomb03      256 -> 254   REMOVED 2x svc_dorus_chest        (#9/#10 class)
styx_riveredge_01          479 -> 477   REMOVED 2x svc_charon_chest       (#10)
styx_swampborder_01         75 ->  71   REMOVED q_tantalus_lone + 3x svc_tantalus_chest  (#8)
styx_caveug_frogcamp02     101 -> 103   ADDED   q_tantalus_lone (30,1,40) + 1x svc_tantalus_chest  (#8/#9)
judgment_stonecity_exit01  137 -> 135   REMOVED 2x svc_ephialtes_chest    (#9/#10 class)
elysian_fields_03          278 -> 278   MOVED   q_diadochi_lone (20.7,4,81.7) -> (70,8.8,80)  (#16)
```

Zero unattributed changes. On "0 REMOVED records": **no DB record is removed** - every
`svc_*_chest` proxy still exists and is still placed at least once. The 11 removed entries are
0x05 *placements*, which is precisely what #8/#9/#10 asked for.

### Gates

* `gate_uber_placement.py --only tantalus` on the built map: **GATE GREEN**, area reads
  "Den of Tantalus".
* `survey_uberboss_spots.py --bosses` on the built map: every shipped spot **OK**, including
  both new ones at ext 3.5/4.0 **and** the 6.0 escort ring.
* `gate_uber_placement.py --negtest`: **6/6 planted negatives behaved as specified** (sec 5.1).
* Full audit: 1 RED, deliberate, documented above.

### TESTHUB variant (what DEV actually deploys) - verified by a real build

`SVC_TEST_HUB=1` build, 0x05 read of the result:

```
[755] Styx_SwampBorder_01      n0x05 76 -> 72   boss + 3 chests gone, and
      #71 svc_area_return_tantalus.dbr  local (52.00,-12.00,80.00)   <- STILL OUTDOORS
[879] Styx_CaveUG_FrogCamp02   n0x05 103
      #101 q_tantalus_lone.dbr      local (30.00,1.00,40.00)
      #102 svc_tantalus_chest.dbr   local (32.60,1.00,40.00)
[776] Elysian_Fields_03        #277 q_diadochi_lone.dbr  local (70.00,8.80,80.00)
```

This is the check that mattered: relocating the boss must NOT drag the Helos travel-landing
return NPC into the cave with him. It does not - `TANTALUS_OUTDOOR_HOST_KEY` holds it in the
marsh, in both map variants.

(Note: calling `merge_hub_into_inject_specs()` outside the build flow raises a b48 Sparta-mute
`ValueError` about the canonical Almyros placement. That is PRE-EXISTING and not caused by this
lane - `main` raises the identical error on the identical call. The function needs build-time
state; the real build is the valid test, and it passes.)

---

## 7. ROUND 2 (R-131) - the two chest halves round 1 handed off, BUILT

> Round 1 closed with "#14 Mnemophage chest" and "#16 Helepolis chest" listed as NOT DONE,
> blocked on "a DB lane this map branch does not own". **That was a triage, and it was wrong.**
> `_svc_build_dedicated_hoard` and `_svc_build_world_chest_proxy` are the exact two helpers the
> other four fixed ubers already call, living in the same two files this lane already edits.
> Round 2 builds both. Ruling: **R-131** in `docs/WILL_RULINGS.md`.

### 7.1 What was built

| | the Mnemophage (#14) | the Helepolis (#16) |
|---|---|---|
| host / area banner | `Judgment_TempleUG_Mnemosyne01` -> **Lower City of Lost Souls** | `Elysian_Fields_03` -> **Delian Meadows** |
| boss charLevel N/E/L | [46, 68, 100] | [58, 80, 97] |
| `_SVC_CHEST_STD` bracket | `svc_mnemophagehoard` 45-47 / 63-65 / 63-65 | `svc_diadochihoard` 57-59 / 63-65 / 63-65 |
| chest display name | **"Mnemophage's Lethe-Hoard"** | **"Helepolis's Spoil-Hoard"** |
| world-chest proxy record | `records\drxmap\proxy\svc_mnemophage_chest.dbr` | `records\drxmap\proxy\svc_diadochi_chest.dbr` |
| placed at (level-local) | (45.6, 3.0, 71.0) | (72.6, 8.8, 80.0) |
| authored in | `apply_svc_patches._create_mnemophage_superboss` | `tools/patches/diadochi.py` |

Both use the b42 round-2 WORLD-CHEST pattern, not the boss-accessory one: the boss proxy's
`accessory1/Epic1/Legendary1` stay EMPTY and a standalone `Class=Proxy` container is placed by the
map lane at `UBER_CHEST_COUNT` (= 1, per R-130 #9/#10) on the same surveyed `+x` offset the other
four use. **No new mechanism, no new coordinate geometry.**

### 7.2 The three things that could have gone wrong, checked rather than assumed

1. **Bracket records exist.** `_svc_standardize_boss_chests` raises `SystemExit` on a missing
   `boss_default_<bracket>`. Enumerated from the built arz first: 32 brackets, `01-03` .. `63-65`
   in steps of 2. `45-47` and `57-59` are both present.
2. **Registry ordering.** `diadochi.py` runs in `run_registry`, which `build_svc_database.py`
   calls **before** `run_registry_gates` - and both `_svc_standardize_boss_chests` and
   `_svc_verify_world_chests` live inside that battery. So a hoard authored in a registry module
   IS region-tuned and IS covered by the invariant. (Had the order been the other way, the
   diadochi hoard would have shipped un-tuned and silently.)
3. **The new gate assertion is satisfiable.** `_SVC_FIXED_UBER_CHESTS` gains both prefixes, so
   `_svc_verify_world_chests` now asserts over SIX ubers that the boss proxy carries no accessory
   chest. Measured on the shipped arz beforehand: `accessory1`/`accessoryEpic1`/
   `accessoryLegendary1` are all `None` on `q_mnemophage_lone`, `q_diadochi_lone`, `q_tantalus_lone`
   and the donor `q_leinth_lone`.

### 7.3 The Helepolis chest rides the relocation - deliberately

His chest is centred on the **new** off-path spot (70, 8.8, 80), not the retired b41 one. A chest on
the old coordinate would have re-created exactly the defect #16 exists to fix: a reward the player
has to stand in the walking corridor to open. Because it rides the boss it is off-path by
construction - and the gate does not take that on trust, since it discovers chests from the map by
marker (`CHEST_MARKERS`) and audits both new chests for containment and path independently.

### 7.4 The FULL #16b audit, re-run on the round-2 map (with chests)

`py tools/debug/gate_uber_placement.py <map> --chests` on the built branch map
`34d2f275122458abc9d46d0969853345`:

```
placements : 47
VERDICT PASS : 46
VERDICT FAIL : 1
AUDITED + ACCEPTED on-path placements (9) - printed in full on every run
GATE RED: 1 placement(s) fail
   tombobs01.lvl   q_obs_roulette_b.dbr   BLOCKS-ROUTE,ON-MAIN-PATH
```

**The single RED is the round-1 finding, still deliberately red** (`BL-R130-DEBT-3`) - the
roulette-b chokepoint. It is NOT a regression from this round and it is NOT silently accepted.
Both new chests are inside the 46 PASS:

```
svc_mnemophage_chest.dbr  area "Lower City of Lost Souls" -> OK  off-path share 100%  blocks=none
svc_diadochi_chest.dbr    area "Delian Meadows"           -> OK  d(route)=19.3u        blocks=none
```

Note the gate defaults to bosses only; `--chests` is what widens it to chest placements, which is
why the audit must be run with that flag to be the complete #16b list.

### 7.5 Placement survey of the two NEW chest spots

Surveyed on map `fc0adcc0713839a685b32d6e122653be` at the chest proxy's own `placementExtents`
(1.0) **and at double it** (2.0):

```
judgment_templeug_mnemosyne01.lvl  (45.6, 71.0)  ext 1.0  N/E/L d=0.14 clr=100/100/100  comp#1/180,700
judgment_templeug_mnemosyne01.lvl  (45.6, 71.0)  ext 2.0  N/E/L d=0.14 clr=100/100/100  comp#1/180,700
elysian_fields_03.lvl              (72.6, 80.0)  ext 1.0  N/E/L d=0.14 clr=100/100/100  comp#1/242,100
elysian_fields_03.lvl              (72.6, 80.0)  ext 2.0  N/E/L d=0.14 clr=100/100/100  comp#1/242,100
```

Both are now permanent entries in the standing `survey_uberboss_spots.py --bosses` sweep, so a
future relocation of either boss cannot silently strand its chest.

---

## 8. #14's ORB - the measurement inverts the premise. **PENDING WILL DECISION.**

Round 1 recorded the orb half as "blocked by the `uber_apex_orb.verify()` roster gate". True, but
not the important reason. `treasureProxyName` on **every** placed fixed uber, read off the shipped
arz:

```
Tantalus (terminal)  um_tantalus_unbound_99      genericbossorb_04
Mnemophage (core)    um_mnemophage_core_99       genericbossorb_04   <- the "trash" orb
Ephialtes            um_ephialtes_99             genericbossorb_04
Kroisos / Dorus      um_dorus_99                 genericbossorb_04
Helepolis            um_helepolis_99             genericbossorb_04
Charon (ferryman)    um_charonform2_ferryman_99  bosschest02_charon  (own named essence)
Devourer (Toxeus)    um_bloodtoxeus_99           genericbossorb_05   (R-99 roster)
```

**The Mnemophage's orb is not worse than his peers' - it is identical to all four of them.** So
"his orb is trash" is a complaint about the **orb04 tier**, not a Mnemophage-specific defect. Which
means:

* moving **only** him to orb05 makes him a strict outlier above four equals for no stated reason,
  and reds the build (that `verify()` assertion is R-47/R-99's "not all champions" guarantee doing
  its job, not obstructing);
* moving **all five** is precisely what Will refused ONE DAY EARLIER in R-99, verbatim: *"i didnt
  tell you to increase the drop of all the champions, just the toxeus variants (all variants we
  made and didnt make) and leinth."*

Either move would override a ruling made yesterday, so neither is taken. **Recommendation:** the
Part 1 chest is the substantive answer to #14 - a Boss-locked region-tuned dedicated hoard is a far
bigger reward swing than the orb tier - so play it before re-tiering. If it still reads thin, the
option that fits every existing ruling is to mint ONE new mid tier for the five placed non-Toxeus
fixed ubers **as a class**, leaving orb05 exclusively Toxeus + Leinth and R-99 intact. Will's call.

---

## 9. NOT DONE (exhaustive, after round 2)

1. **#14 Mnemophage orb tier** - measured (sec 8), deliberately unchanged. **Open Will decision**,
   `BL-R131-DEBT-1`. Not a blocked task: a ruling-level choice with three costed options.
2. **In-game verification of everything this lane did** - **launch-gated.** Nobody has walked into
   the Den of Tantalus, the eastern Elysian court, the Mnemosyne chamber or opened either new
   chest on this build. Per the standing rule the test ping must carry a full Steam restart and a
   packaged-hash verify. Covers: both relocations, both new chests, and the 3->1 chest count.
3. **Neither new chest's LOOT has been observed** - the chain is proven to RESOLVE (build gates +
   region-tuning), never opened in game. `BL-R131-DEBT-2`.
4. **`q_obs_roulette_b` BLOCKS-ROUTE** - `BL-R130-DEBT-3`, unchanged. Will's call.
5. **Will's call on the 3->1 chest class** - he named two bosses, the rule was applied to four.
6. **Will's call on the 9 accepted on-path placements** (Menoetes, Ephialtes, Charon are the three
   worth a real decision) and on the Helepolis siege-strider adjacency trade-off (sec 4).
7. **The two new chest NAMES are unvetted by Will** - "Mnemophage's Lethe-Hoard" and "Helepolis's
   Spoil-Hoard" follow the shipped convention and the amgoz1 bar, but they are my wording.
8. **Deploy** - not performed. The orchestrator owns deploys; `Levels`+`Quests` stay coupled, as
   do `arz`+`Text` (both new chest tags are Text-side, so the arz and Text.arc MUST ship together
   or the chests show raw tag text).
