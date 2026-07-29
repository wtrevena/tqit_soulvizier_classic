# b100 - Sanctuary of the Bloodborn: THE POPULATION (implementation, round 1)

> **Will's report, verbatim:** the Sanctuary of the Bloodborn has *"large walkable areas with no
> enemies placed"*, and *"the minimap doesn't render them"* - he added the minimap *"isnt a huge
> issue"*. Priority order is therefore EMPTY SPACE first, minimap second. This lane ships the
> population (**R-110**) and files the minimap with its measured mechanism (**R-111**, PENDING).
>
> **Rulings decade: R-110..R-119**, re-checked free this turn against `main` and every in-flight
> branch. The claimed set across all branches is R-1..R-51, R-60/61, R-70..R-76, R-80..R-86,
> R-90..R-98, R-100..R-102 (`fix/blade-mastery-truth`). Decade freeness is a RACE under parallel
> lanes - the next agent must re-run the check, not trust this line.
>
> **NOT DEPLOYED. NOTHING WAS WRITTEN TO `CustomMaps`. TQ AND STEAM WERE NEVER LAUNCHED.**
> The orchestrator owns every deploy and every Steam upload.

---

## 0. TL;DR

| | |
|---|---|
| **What shipped** | 14 monster proxies placed into `Levels/World/xBloodCave/drxBC3.lvl`, the one level carrying the "Sanctuary of the Bloodborn" region label. Four bands climbing the cult's hierarchy along the player's actual one-way walk. |
| **Cost** | **Zero new creatures, records, pools or text tags.** Every proxy is drawn from a pool this cave already ships, so the lane is MAP-ONLY and drags in no `arz`+`Text` coupling. `Quests.arc` rebuilt anyway (Levels+Quests deploy together) and comes out **byte-identical** to the deployed canonical. |
| **Blast radius** | **1 level blob of 2,282** differs, and inside it **one section (0x05)**. The `0x0b` navmesh is byte-identical. All 281 pre-existing instances are byte-preserved. |
| **Density** | worst exact 60x60 screen box **24 -> 36** spawnMax, under the gated cap of 42 (= the sparsest already-shipping blood-cave sibling, and the base-game cave/crypt/tomb p90). |
| **New gate** | `MAP-SANCTUARY-1` - 13 invariants, **8/8 planted negatives caught**. |
| **Design corrections** | The design pass's band AXIS, its Y model, its density measurement and one of its evidence claims were each wrong. Section 3. |
| **Not done** | No in-game check (no agent here may launch TQ). Ocean ring untouched (WILL_DECISION-1). Minimap not fixed (R-111). Section 8. |

---

## 1. WHAT WAS BUILT

### 1.1 The place, and therefore the design

`drxBC3` is a Hades-palace stone walkway over a pit - 214 `Decoration` instances of
`bossroomdress/setdress/hp_*` pillars and pit formations, `bloodcave/bridges/*`, six distinct
`skeletalremainsbossroom*`, 42 `map_formation_ambient`, 11 `fountainsplash03`, 10 clouds and one
`riversmall` sound object - next door to `bossfight.lvl`, which binds "Palace of Hades ~ Outer
Court". The player arrives by a one-way `GridExitOneWay` at the north-east corner beside a respawn
shrine, and leaves by **walking west** into `drxBC_Finale`. There is no return portal.

So it is a **processional**, and the population has to read as a **congregation at rite**, not a
patrol. An evenly-spaced patrol is exactly the generic filler the amgoz1 bar forbids. The player
walks up the aisle and the cult's own hierarchy escalates in front of him.

### 1.2 The four bands

Every proxy is a pool that **already ships in this cave**, so the Sanctuary reads as the same cult
at its centre rather than as a new bestiary.

| band | route distance | ADD | why this creature, here |
|---|---|---|---|
| **1. The Outer Court** | 0-120 u | 2 x `bw_acolyte_lone` | The arrival breath. Two novices kneel alone at the edge of the rite, too rapt to have noticed you. Lone acolytes are the weakest thing in the cult, and this is the one place in the mod where that reads as *devotion* rather than as filler. |
| **2. The Congregation** | 120-265 u | 2 x `zparty_witchfest_2099`, 2 x `bw_acolyte_clutch` | The rite in full voice. `zparty_witchfest_2099` is *already* the Sanctuary's signature proxy (4 placed here, 28 in `drxBC_Finale`) - the witchfest **is** the ceremony, and "witchfest" is amgoz1's own word for what happens on this walkway. Acolyte clutches turn it into a body of worshippers. |
| **3. The Clergy** | 265-460 u | 2 x `bw_priest_houndmaster`, 1 x `bw_priest_lone`, 1 x `hound_01_pack` | Between the congregation and the god stand the priests, and priests here come leashed to bloodhounds. `bw_priest_houndmaster` is the only proxy in this cave that pairs a caster with beasts, which gives the middle of the walk its own combat texture (chase + caster) instead of another melee wave. |
| **4. The Threshold** | 460-691 u | 2 x `abom_dancer_spear_mix`, 1 x `abom_ravager_lone`, 1 x `q_shaman_lone` | The door-wardens, down on the floor of the pit the whole walkway crosses, in front of the west door. The abominations are the cult's flesh-craft - what the Bloodborn **make**, not what they recruit - so they belong at the holy of holies, and they already guard the adjacent connectors. One `q_shaman_lone` gives the band a named face, echoing the shaman standing in `yet_another_fucking_connector`. |

The **10 existing proxies are kept and reused as the skeleton of bands 1-3**. Nothing is moved,
re-pointed or deleted (RETIREMENT PROTOCOL: they are amgoz1's design of record).

### 1.3 Where it lives in the pipeline

- `tools/build_section_surgery.py` -> `SANCTUARY_SPECS` / `SANCTUARY_HOST_KEY`, folded into
  `INJECT_SPECS` collision-guarded. This is the repo's established map-side placement mechanism -
  the same `inject_into_sv_only_blob` 56-byte v0x0e path the widow letter, the Enslaver warband and
  the b79 parchment Toxeus already use in this cave.
- **No `tools/patches/` registry module.** The registry is the DB-side mechanism and this lane
  makes no DB change; adding an empty module would be a lie about the lane's scope.
- Byte shape: **identity rotation, `flags=0`, no `0x14`** - measured to be exactly the shape of all
  ten proxies amgoz1 placed in this level himself (every drxBC3 proxy reads identity / flags=0).

---

## 2. THE COORDINATES ARE DERIVED, NOT AUTHORED

`tools/debug/b100_derive_sanctuary.py` re-derives the exact list in `SANCTUARY_SPECS` from a built
map. Deterministic farthest-point insertion: **no RNG**, and the tie-break key
`(min Chebyshev distance, -route distance, -gcx, -gcz)` is a total order over distinct cells, so the
result reproduces byte-for-byte on any machine and any Python build.

Ten hard filters, each of which the gate re-proves against the FINAL MERGED map:

| | filter | why |
|---|---|---|
| F1 | on a walkable navmesh cell whose `areas` owner byte is drxBC3's own GUID index | that byte is the 1-based index into the mesh's GUID list naming the level that OWNS the cell, so it is a *mechanism-derived* "inside its own ground" - it replaces the design's hand-typed footprint box, and the two agree exactly at 23,994 sq u |
| F2 | walkable in **all three** tilesets | the engine requires all 3 (Normal/Epic/Legendary); a one-tileset spot spawns monsters that cannot path on the other two difficulties |
| F3 | in the arrival portal's connected component (engine climb model, 1.0 u) | never on an isolated navmesh island |
| F4 | at most 60 u of detour over the shortest arrival -> west-door path | it is a processional; nothing may sit in a pocket the player never enters |
| F5 | >= 20 u (Chebyshev) from the arrival portal AND the respawn shrine | **the b44 landing-clearance precedent** - the player must never materialise inside a pack |
| F6 | >= 90% of a 3.0 u disc walkable | the pack needs room to materialise |
| F7 | >= 3.0 u from every placed `0x05` instance | never inside a pillar or a bone pile |
| F8 | >= 10 u inside drxBC3's own footprint edge | the b44 class applied to a **walk-in seam**: the player crosses x=4186 into `drxBC_Finale` and must not arrive inside a pack. Without it the derivation put an 8-spawn `abom_dancer_spear_mix` at world x=4186.5, i.e. **0.5 u from the exit door** |
| F9 | >= 16 u (Chebyshev) from every other monster proxy, old or new | **R-30's spacing law**, verbatim: *"you need to space these monsters out instead of putting them all on top of one another"* |
| F10 | the worst axis-aligned 60x60 box anywhere sums <= 42 spawnMax | the density ceiling, enforced DURING selection rather than reported afterwards |

Reproduce:

```
PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 py tools/debug/b100_derive_sanctuary.py --map <Levels.arc>
```

---

## 3. WHERE THE DESIGN WAS WRONG

The brief said to treat the design as a proposal. Four of its claims did not survive measurement.
Its **intent** and its **creature rosters** are kept verbatim; what changed is the engineering
underneath them.

### 3.1 X is not the walk (the band axis)

The design banded by world-X on the premise that the player *"walks strictly WESTWARD"*. Measured
geodesically on the navmesh, the processional is **690.6 u** and **X is not monotonic along it**:

```
   +  0.0u  world(4410.7,  2.0, 3088.9)   the arrival portal
   + 45.0u  world(4393.9, -0.4, 3060.7)   descending the ramp
   +120.0u  world(4356.5,-10.0, 3023.1)   running WEST on the -10 tier
   +240.0u  world(4289.9,-10.0, 3043.3)   ... turns back EAST-ish and drops
   +270.0u  world(4293.1,-22.0, 3016.5)   the -22 tier
   +330.0u  world(4305.7,-22.0, 2969.1)   running SOUTH  (X has gone UP again)
   +450.0u  world(4266.7,-32.4, 2888.5)   dropping to the pit floor
   +600.0u  world(4210.1,-34.0, 2981.5)   running NORTH on the pit floor
   +690.6u  world(4186.9,-34.0, 3048.7)   the west door into drxBC_Finale
```

X runs 4411 -> 4290 -> **4306** -> 4210 -> 4187. A band defined on X therefore does not correspond
to any stretch of the player's walk. Bands are now **geodesic route distance from the arrival
portal**, which is what the design's own words "along the one-way walk" actually mean. Two of the
three band boundaries (265 u, 460 u) are the **measured** tier transitions; the first (120 u) is a
stated design choice - the length of the arrival breath - and it is forced to start after the ramp
anyway, because F5's 20 u clearance around the two anchors excludes the entire 538 sq u arrival
platform (a 20 u disc is 1,257 sq u).

### 3.2 The design never computed a Y at all

`tools/debug/b100_plan.py` collapsed the level to a flat XZ set. The level **descends four
elevation tiers**:

| world Y | own walkable ground | what it is |
|---:|---:|---|
| +2 | 539 sq u | the arrival platform |
| -10 | 9,600 sq u | the upper walkway |
| -22 | 10,566 sq u | the middle walkway |
| -34 | 2,971 sq u | the pit floor - **and where the west door is**: all 36,937 west-seam cells read Y=-34 |

An X-banded, Y-less placement can therefore put a proxy at the right XZ and the wrong elevation,
i.e. buried or hovering. Y is now read from the navmesh cell as `org_y + (hmin + heights[i]) * ch`,
verified against all ten shipped drxBC3 proxies at **max |dY| = 0.02 u**, and gated (G4) at
<= 0.25 u. Measured on the shipped placements: **max dY 0.005 u**.

A second frame trap sits behind this one: the mesh grid origin is `center - dims` =
world **(4128,-60,2798)**, which is **not** the level corner **(4186,-37,2869)**. drxBC3's navmesh
is padded and also rasterizes five neighbour levels, so the assumption
`tools/debug/survey_uberboss_spots.py` makes (`org == corner`) is false here by (58, 71). The
derivation reads the frame out of the container instead of assuming it.

### 3.3 The density numbers were measured with a weaker box

The design summed `spawnMax` in a 60x60 box **centred on a proxy**. The worst box generally is not
centred on any point. In this very level the two shipped `zparty_witchfest_2099` proxies at
(4288.6,3074.9) and (4344.4,3044.1) are 55.8 u apart in x and 30.8 u in z, so no box centred on
either contains the other - the design read **12** - but the box with its low corner at
(4288.6,3044.1) contains both, so the true answer is **24**. Every comparator the design quoted
carries the same undercount, which means its headline ("the proposal sits at the base-game median")
compared a number against a differently-measured number.

`tools/debug/b100_density_census.py` recomputes both, side by side, over the whole map with the
exact box (an optimal axis-aligned box can be slid until its low corner is pinned by a point on each
axis, so enumerating point pairs is exhaustive, not a sample):

```
=== blood cave ===
  drxBC2                            proxies=21   worst EXACT= 81   CENTRED= 72
  drxFirstRoom                      proxies=53   worst EXACT= 69   CENTRED= 51
  drxBC_Finale                      proxies=31   worst EXACT= 60   CENTRED= 60
  drxBC_Connector2                  proxies=14   worst EXACT= 47   CENTRED= 23
  drxBC_finale_transitionconnector  proxies= 8   worst EXACT= 43   CENTRED= 35
  yet_another_fucking_connector     proxies=17   worst EXACT= 42   CENTRED= 39
  drxBC3                            proxies=10   worst EXACT= 24   CENTRED= 12
=== base-game cave/crypt/tomb cohort (n=80, >= 5 proxies with a live pool) ===
  worst-screen EXACT  : min 9  p25 19  MEDIAN 26  p75 35  p90 44  max 78
  worst-screen CENTRED: min 4  p25 13  MEDIAN 20  p75 28  p90 38  max 71
  mean EXACT/CENTRED ratio: 1.39x
```

(Cohort definition differs from the design's n=147: this one requires >= 5 placed proxies whose
pool has a non-zero `spawnMax`, and does **not** additionally require > 3,000 sq u, which would
mean decoding 2,282 navmeshes. Like-for-like within itself, which is the point.)

**The density cap is therefore derived, not chosen:** `SCREEN_CAP = 42` = the sparsest
already-shipping blood-cave level that carries real content, which is also the base-game
cave/crypt/tomb p90 (44). Result **24 -> 36**: the Sanctuary lands inside its own family and stays
the sparsest walkable level in the blood cave, which is what a processional should be.

### 3.4 The design's rule 2 is unsatisfiable, and was the wrong invariant anyway

Design rule 2: *"two 'party' proxies (spawnMax>=6) never within 34u of each other on both axes, any
other pair never within 16u - this is what holds the screen load down."* Measured: the roster
contains **seven** `spawnMax>=6` proxies and the level already ships **five** more, against **258
sq u** of party-eligible ground in band 2 once the placements also have to be reachable, on the
processional, clear of the props and clear of the arrival anchors - while a 34 u Chebyshev exclusion
removes up to 68x68 = 4,624 sq u per proxy. The derivation fails outright with rule 2 in force.

It was only ever a *sufficient condition* for a density cap, so the cap is now gated **directly**
(F10/G9), with R-30's 16 u floor kept universally (F9/G8). That is both buildable and a stronger
claim: the thing Will cares about is bounded and measured, not approximated by a spacing proxy.

### 3.5 One evidence claim in the design report is false as written

The design says *"every `pool1` resolves as Class `ProxyPool`"*. Measured: a ProxyPool record carries
**no `Class` field at all** - all 61 records under `records\drxmap\proxy\pools\` return `''` - and
its identity is the **template**, `database\Templates\ProxyPool.tpl`. The pools themselves are
perfectly fine; the cited evidence was not. The gate checks the template.

---

## 4. THE GATE (`MAP-SANCTUARY-1`)

CLAUDE.md process law #4: a lane creating a new player-visible content class ships its invariant
gate with it. `tools/gate_sanctuary_population.py` runs against a **built** `Levels.arc` (never the
source blob - the pre-merge blob is not where the grid shift and the injections have landed).

```
py tools/gate_sanctuary_population.py --map <new.arc> --baseline <baseline.arc> --arz <arz>

  G1   roster: the 14 declared proxies are placed                     PASS  295 instances total, tail 14 match (0 missing, 0 unexpected)
  G1b  roster: new instances are flags=0 / no UniqueId                PASS  0 flagged
  G2   on-mesh: on drxBC3's OWN walkable ground                       PASS  14/14
  G3   on-mesh in ALL 3 tilesets (N/E/L)                              PASS  14/14
  G4   floor: |Y - navmesh cell Y| <= 0.25 u                          PASS  max dY 0.005 u
  G5   reachable from the arrival portal                              PASS  14/14 in the arrival component
  G6   on the processional (detour <= 60 u)                           PASS  route 690.6 u; max detour 60.0 u
  G7   landing clearance (anchors / level edge / props)               PASS  nearest anchor 20.1 u, edge 12.1 u, prop 3.7 u
  G8   spacing: every NEW proxy >= 16 u from every other (R-30)       PASS  24 monster proxies; closest new-involving pair 21.5 u
  G8b  spacing: no UNWAIVED inherited violation                       PASS  1 inherited, 0 unwaived
  G9   density: worst 60x60 box <= 42 spawnMax                        PASS  worst 36 at world(4318,3019); total spawnMax 140 over 24 proxies
  G11  pools: every placed proxy resolves to a live, BOUNDED pool     PASS  14/14
  G10  navmesh: 0x0b byte-identical to baseline + well formed (b89)   PASS  857,212 B, identical=True, 3 tilesets x [383,383,383] tiles
  G12  scope: the ocean ring is untouched (WILL_DECISION-1)           PASS  0 proxies on all four ocean tiles

GATE MAP-SANCTUARY-1: PASS
```

### 4.1 Planted negatives - a gate nobody has watched FAIL is not a gate

```
py tools/gate_sanctuary_population.py --negtest --map <arc> --arz <arz>

  baseline (unmodified placements): 0 failing -> OK, the gate is green before we break it
  plant [G1] drop one proxy from the roster                                  -> CAUGHT by ['G1']
  plant [G1] move a proxy 5 u off its declared coord                         -> CAUGHT by ['G1', 'G8']
  plant [G2] push a proxy onto the padded neighbour strip outside drxBC3     -> CAUGHT by ['G1','G2','G3','G4','G5','G6','G7']
  plant [G4] keep the XZ but flatten Y to the top tier                       -> CAUGHT by ['G1', 'G4', 'G7']
  plant [G7] drop a pack on the arrival portal (the b44 landing-pileup)      -> CAUGHT by ['G1', 'G7']
  plant [G7] drop a pack 0.5 u from the west door seam (walk-in variant)     -> CAUGHT by ['G1','G2','G3','G4','G5','G6','G7']
  plant [G8] stack two proxies on top of one another (R-30's own words)      -> CAUGHT by ['G1', 'G8']
  plant [G9] pile the whole congregation into one screen box                 -> CAUGHT by ['G1'..'G9']

NEGTEST: 8/8 plants caught -> PASS
```

**The negatives earned their keep immediately.** The first cut of the gate had two real bugs that
the plants exposed: G7 measured each new proxy's distance to *itself* (the prop list was read from
the post-injection map), and G8/G9 read the built map instead of the declaration, so no plant could
ever bite them. Both are fixed; that is why the plants exist.

### 4.2 One thing the gate found that is NOT ours to fix

amgoz1's own shipped placements already violate R-30's spacing law: `bw_seductress_lone` at world
(4314.8,2882.1) and `bw_priest_houndmaster` at (4316.6,2889.5) are **7.4 u apart**. Moving either
is a design change to shipped upstream content and defaults to **WILL-VETO** under the RETIREMENT
PROTOCOL, so the pair is waived **by name** in an allow-LIST (G8b) - any *other* inherited
violation, and anything involving one of our placements, still fails - and registered as
`BL-b100-DEBT-7`.

---

## 5. VERIFICATION - EVERY NUMBER, WITH THE COMMAND

### 5.1 Dry run into a COPY, before any real build

```
py tools/debug/b100_dryrun_inject.py --map local/b100_base/Levels_merged.arc

  level : levels/world/xbloodcave/drxbc3.lvl  blob v0x0e  1,113,386 B  md5 e11798cadb1984f92ecf2f48200e69c9
  patched blob: 1,114,441 B  md5 a4a81f3aca0baeb8cdc9593e09952048  delta +1,055 B

  0x05 placed instances    18,778 B ->  19,833 B   CHANGED (+1,055 B)
  0x06 grid descriptors    10,000 B ->  10,000 B   IDENTICAL
  0x09 terrain             73,410 B ->  73,410 B   IDENTICAL
  0x0b REC\x02 navmesh    857,212 B -> 857,212 B   IDENTICAL
  0x14 instance bindings       56 B ->      56 B   IDENTICAL
  0x17 REGION list        153,878 B -> 153,878 B   IDENTICAL

  PASS: exactly one section changed and it is 0x05.
  PASS: 0x0b navmesh byte-identical (857,212 B, md5 06f783d00edc7c23866b0fe2b368bbb0).
  0x05 instances: 281 -> 295  (expected +14)
  PASS: all 281 pre-existing instances byte-preserved (ADD-ONLY, retirement protocol).
  DRY RUN: PASS
```

### 5.2 Whole-map diff against a real baseline built in the same environment

Baseline = this branch's merge-base tree (`4f0299c`, verified to touch **no build-path file**
relative to it), built with the identical command and environment into an isolated
`SVC_OUT_DIR`, so the diff isolates exactly this lane's change.

```
py tools/debug/b100_map_diff.py --a local/b100_base/Levels_merged.arc --b local/b100_new/Levels_merged.arc

  levels: 2282 vs 2282
  level blobs differing: 1
    [2253] Levels/World/xBloodCave/drxBC3.lvl  1,113,386 -> 1,114,441 B  sections changed: ['0x5']
            0x05: 18,778 -> 19,833 B
            0x0b navmesh IDENTICAL (857,212 B, md5 06f783d00edc7c23866b0fe2b368bbb0)
  TOP-LEVEL SECTION ATTRIBUTION
    identity (fname + ints_raw: tile dims / grid corner / GUID): 2282/2282 unchanged
    data_length changed on 0 level(s) other than the declared one
    data_offset shifted on 28 level(s) (the expected ripple after a +1055 B blob)
    0x01 change is ENTIRELY the offset ripple - attributed.
  MAP DIFF: PASS - every change attributed
```

### 5.3 Artifacts produced

_(filled in by section 5.4 below - md5s of the artifacts this lane actually built)_

---

## 6. THE MINIMAP (R-111, PENDING, NOT FIXED HERE)

Checked, and it is **NOT the b46 mechanism**, so per the brief it is filed as debt with the
mechanism rather than fixed on this commit. b46's two proven mechanisms are each SATISFIED here:
drxBC3's `0x17` REGION list is populated and resolves (the banner is correct), and its zone pointer
`records/ingameui/teleportmap/zones/orient/easternsilkroad.dbr` is valid (b46's `crypt_floor1` had
`dbr = ''`). The bitmap exists and is not blank.

The actual mechanism, measured: `tools/svaera_plus_portals.py` sets
`GRID_SHIFT = {'xbloodcave': (7840, 0, 2030)}` to relocate the cluster into empty map space with
"3001.8u clearance", and a level's minimap TGA composites onto its **zone's** page at the level's own
grid corner. Of the 79 levels sharing the `easternsilkroad` page, the 48 native tiles span
X[-1412,440] Z[-1764,2302] and the 31 blood-cave tiles span X[3426,5979] Z[2629,3425] - a measured
**2,986 u** gap. The very clearance that made the relocation safe for the world grid is what puts
the cluster off its own minimap page.

Fix direction (**not built**): a dedicated
`records/ingameui/teleportmap/zones/orient/bloodcave.dbr` with its own `ZoneNameTag` and
`ArrowLocation`/`WindowLocation` - SV's own precedent (amgoz1 authored `olympus_gom.dbr` for one
relocated area rather than reusing `olympus.dbr`). That is a **coupled `arz`+`Text`+`Levels`**
change (new DB record, new text tag, LEVELS-entry `dbr` override for ~31 levels), materially more
expensive than the population work. `BL-b100-DEBT-3`.

---

## 7. PLAYER-SURFACE CHECKLIST (CLAUDE.md law #3)

The lane creates no record, so every player-visible surface it exposes belongs to content that
already ships and is already fought elsewhere in this same cave.

_(measured table filled in by section 7.1)_

---

## 8. WHAT IS **NOT** DONE

Exhaustive; a triaged item is not a done item.

1. **NO IN-GAME CHECK.** Nobody has walked the Sanctuary with this population in it. No agent in
   this lane may launch TQ or Steam. Every claim here is a claim about bytes and geometry, not
   about feel. The density figures in particular are `spawnMax` sums - the worst case the DATA
   permits - and actual concurrent load depends on player pathing and aggro.
2. **NOT DEPLOYED.** Nothing was written to `CustomMaps`. `Levels.arc` and `Quests.arc` are COUPLED
   and must ship in the same deploy.
3. **THE OCEAN RING IS UNTOUCHED** - `WILL_DECISION-1`, 42,199 sq u of walkable, Sanctuary-lit,
   banner-inheriting ground with zero enemies behind a measured 107.2 u opening. Not ours to take.
4. **THE MINIMAP IS NOT FIXED** - R-111 / `BL-b100-DEBT-3`.
5. **DENSITY IS UNRATIFIED** - `WILL_DECISION-2`. 24 -> 36 worst-screen is a derived cap, not Will's
   ruling.
6. **`docs/amgoz1_design_voice.md` STILL DOES NOT EXIST** - `WILL_DECISION-4`. The creative bar this
   content is held to remains reconstructed from R-15, `docs/BLOOD_TOXEUS_DESIGN.md` and
   `docs/BOSS_SOULS_DESIGN.md`, and that reconstruction is unratified.
7. **THE INHERITED 7.4 u SPACING VIOLATION IS WAIVED, NOT FIXED** - `BL-b100-DEBT-7`.
8. **`SCREEN_CAP`, `CORRIDOR_SLACK`, `EDGE_CLEAR` AND THE 120 u BAND-1 BOUNDARY ARE ENGINEERING
   CHOICES**, three of them derived from measurement and one (120 u) stated as taste. All four are
   one-line edits in `b100_derive_sanctuary.py`, after which the coords must be re-derived and the
   gate re-run.
