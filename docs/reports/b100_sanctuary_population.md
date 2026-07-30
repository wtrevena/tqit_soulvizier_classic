# b100 - Sanctuary of the Bloodborn: THE POPULATION (implementation, round 2)

> **ROUND 2.** An independent vet returned **NO-GO** on round 1 with 13 findings (1 HIGH, 6
> MEDIUM, 6 LOW). Every one was **re-measured, not argued**. Outcomes: **11 confirmed and fixed**,
> **1 confirmed as a real defect whose supporting number was itself wrong** (the ocean-ring scope
> finding - the emptiness is real, the "1.76x / 36%" figures were not), and **1 partially wrong**
> (the zero-margin readings are inherent to a shared constant, not near-misses). Section 9 is the
> finding-by-finding ledger with the command that settled each. Round 1's own headline claims that
> did not survive: the `Quests.arc` deploy-safety claim (**false**), the base-game density
> comparison (**invalid units**), and the placement SHAPE (**the code produced the opposite of the
> recorded design intent**). All three are corrected in code, not just in prose.

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
| **Cost** | **Zero new creatures, records, pools or text tags.** Every proxy is drawn from a pool this cave already ships, so the lane is MAP-ONLY and drags in no `arz`+`Text` coupling. |
| **⚠️ Quests coupling** | `Quests.arc` IS rebuilt (Levels+Quests deploy together) but it is **NOT** byte-identical to the artifact currently deployed. MEASURED: deployed `bd0fb5f99d88fab74b81f27b7cb952b2` / 194,971 B vs this lane's `5e664c7b190965fd69f6ff15d77d85e4` / 194,926 B. **Round 1 claimed identity in four places and it was false.** The integrator must ship this lane's `Quests.arc` with the map. Section 5.3. |
| **Blast radius** | **1 level blob of 2,282** differs, and inside it **one section (0x05)**. The `0x0b` navmesh is byte-identical. All 281 pre-existing instances are byte-preserved (proven by digest AND by baseline byte-diff). |
| **Density** | worst exact 60x60 screen box **32.6 -> 51.6 EFFECTIVE entities**, under the gated cap of 57.0. Effective, not raw `spawnMax`: the pool's `proxyPoolEquation` multiplies it, and round 1's raw cross-family comparison mixed a 1.357143x family with a 3.60025x one. Corrected base-game cave/crypt/tomb cohort (n=80): median **90.0**, p90 **158.4**. |
| **Shape** | nearest-neighbour Chebyshev **min 16.0 / median 30.0 / max 62.2** - bimodal, groups clustered at the spacing floor with wide gaps between them, like amgoz1's own 7.4/41.9/55.2. Round 1's farthest-point mechanism gave 23.2/31.8/48.2, i.e. the evenly-spaced patrol the bar forbids. |
| **New gate** | `MAP-SANCTUARY-1` - **16 rows**, **16/16 planted negatives correct** (8 declaration + **8 map-side byte plants**), each checked against its target gate AND an allow-set. |
| **Design corrections** | The design pass's band AXIS, its Y model, its density measurement, one evidence claim, **its ocean-ring area (2.88x too large)** and **its seam width (5x too large)** were each wrong. Sections 3 and 9. |
| **Not done** | No in-game check (no agent here may launch TQ). Ocean ring untouched - **14,673 sq u of reachable empty ground, WILL_DECISION-1** (not 42,199; see 9.7). Minimap not fixed (R-111). Section 8. |

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

  G1   roster: the 14 declared proxies are placed          PASS  295 instances total, tail 14 match (0 missing, 0 unexpected)
  G1b  new instances flags=0 / IDENTITY ROTATION           PASS  0 flagged, 0 rotated
  G1c  RETIREMENT: 281 shipped byte-intact (digest) + 11   PASS  295 = 281 + 14; 11/11 shipped proxies in place;
       shipped Proxy placements at their shipped coords          head digest 78a536278d5dbdf23332e70750aa04d9 OK
  G1d  RETIREMENT: shipped instances BYTE-identical to     PASS  281 baseline instances, 0 differ (dbr + 36 rotation
       the baseline                                              bytes + 12 position bytes + flags + uid all equal)
  G2   on-mesh: on drxBC3's OWN walkable ground            PASS  14/14 on an own-area walkable cell
  G3   tilesets: all 3 agree cell-for-cell AND every       PASS  14/14 walkable in all 3; tilesets differing
       proxy walkable in each                                    from tileset 1: none
  G4   floor: |Y - navmesh cell Y| <= 0.25 u               PASS  max dY 0.005 u
  G5   reachable from the arrival portal                   PASS  14/14 in the arrival component
  G6   on the processional (detour <= 60 u)                PASS  route 690.6 u; max detour 60.0 u, MARGIN 0.0 u
  G7   landing clearance (anchors / edge / props)          PASS  nearest anchor 20.1 u (+0.1), edge 12.1 u (+2.1),
                                                                nearest prop 4.4 u (+1.4)
  G8   spacing: every NEW proxy >= 16 u from every other   PASS  24 monster proxies; closest new-involving pair 16.0 u
  G8b  no UNWAIVED inherited spacing violation             PASS  1 inherited, 0 unwaived
  G9   density: worst 60x60 box <= 57.0 EFFECTIVE          PASS  worst 51.6 (margin +5.4) at world(4374,3023);
                                                                total effective 190.0 over 24 proxies
  G11  pools: live, BOUNDED ProxyPool + parseable          PASS  14/14 resolve; no summon-refill loop (b76)
       spawn multiplier
  G10  navmesh: 0x0b byte-identical to baseline +          PASS  857,212 B, identical=True,
       well formed (b89)                                         3 tilesets x [383, 383, 383] tiles
  G12  scope: the ocean ring is untouched                  PASS  ocean_extension01 21 inst / 0 proxies; 02 0/0;
                                                                03 12 inst / 0 proxies; 04 0/0

GATE MAP-SANCTUARY-1: PASS      (exit 0)
```

**16 rows, not 13.** Round 2 added `G1c`/`G1d` (the RETIREMENT PROTOCOL, which round 1 advertised but
did not check) and split `G3` into a real invariant instead of a tautology of `G2`.

**⚠️ THE TWO ZERO-ISH MARGINS ARE INHERENT, NOT NEAR-MISSES.** G6's max detour is exactly 60.0 u and
G7's nearest anchor is 20.1 u; the vet flagged both as zero-slack. Re-measured and explained: the
DERIVATION filters candidate cells on the *same* `CORRIDOR_SLACK` and `CLEAR_ANCHOR` constants the
gate checks, so it legitimately admits cells right up to the limit and the farthest-point anchor step
actively prefers them; and the navmesh lattice is 0.2 u, so the closest ADMISSIBLE cell to a 20.0 u
exclusion is 20.1 u. Any future change to either constant moves both sides at once. The gate now
prints the margins **and** this explanation so nobody reads 0.0 as a near-miss. What IS true and is
now registered as `BL-b100-DEBT-11`: "on the processional" permits up to 60 u of detour on a 690.6 u
route and two placements take all of it. That is a taste question about how far off the aisle a
worshipper may stand, and it is a one-line edit.

### 4.1 Planted negatives - a gate nobody has watched FAIL is not a gate

**ROUND 2 REWROTE THIS ENTIRELY, because the round-1 vet showed the plants were the weak point.**
Round 1 had 8 plants and **all eight mutated only the DECLARATION** while leaving the built map
correct. Three consequences, all demonstrated by the vet:

- the RETIREMENT PROTOCOL was **never exercised**, and four map-side negatives passed with every
  gate green;
- two b89-class navmesh negatives **aborted the gate with an uncaught `AssertionError`** instead of
  failing `G10` (fail-safe, since the exit code was still non-zero, but not the PASS/FAIL behaviour
  the gate advertised);
- because every declaration plant perturbs the roster, **every plant also tripped G1**, so "one
  plant per invariant" was not true and no plant isolated its target. Round 1's runner only checked
  that the target gate failed - never that unrelated gates did not.

There are now **two plant kinds**, and each plant declares **both** the gate it must trip **and** the
full set it is allowed to trip; the runner checks both directions.

- **DECL** plants mutate the declared placement list (the map stays correct).
- **MAP** plants rewrite drxBC3's **raw level blob** through a new `Sanctuary(blob_patch=...)` hook -
  real byte surgery on the level, which is what the vet did by hand. Verified independently that all
  eight actually change the bytes (e.g. the truncation plant takes the blob 1,114,441 -> 257,377 B).

```
py tools/gate_sanctuary_population.py --negtest --map local/b100_r2/Levels_merged.arc \
      --baseline local/b100_base/Levels_merged.arc --arz work/.../SoulvizierClassic.arz

  baseline (unmodified): 0 failing -> OK, the gate is green before we break it
  [DECL] must fail G1   drop one proxy from the roster                          -> CAUGHT by ['G1','G1c']
  [DECL] must fail G1   move a proxy 5 u off its declared coord                 -> CAUGHT by ['G1','G8']
  [DECL] must fail G2   push a proxy onto the padded neighbour strip            -> CAUGHT by ['G1','G2','G3','G4','G5','G6','G7']
  [DECL] must fail G4   flatten Y to the top tier (the design's missing axis)   -> CAUGHT by ['G1','G4','G7']
  [DECL] must fail G7   drop a pack on the arrival portal (b44 pileup class)    -> CAUGHT by ['G1','G7','G8']
  [DECL] must fail G7   drop a pack 0.5 u from the west door seam              -> CAUGHT by ['G1','G2','G3','G4','G5','G6','G7']
  [DECL] must fail G8   stack two proxies on top of one another (R-30)          -> CAUGHT by ['G1','G8']
  [DECL] must fail G9   pile the whole congregation into one screen box         -> CAUGHT by ['G1','G2'..'G9']
  [MAP]  must fail G1c  delete one of the 281 SHIPPED instances (a decoration)  -> CAUGHT by ['G1c','G1d']
  [MAP]  must fail G1c  delete one of amgoz1's TEN shipped MONSTER proxies      -> CAUGHT by ['G1c','G1d']
  [MAP]  must fail G1c  delete a shipped instance AND pad (count still 295)     -> CAUGHT by ['G1c','G1d']
  [MAP]  must fail G1c  teleport a shipped proxy 500 u off the level            -> CAUGHT by ['G1c','G1d']
  [MAP]  must fail G1b  give a NEW instance a non-identity rotation             -> CAUGHT by ['G1b']
  [MAP]  must fail G10  b89: flip one byte inside the 0x0b navmesh container    -> CAUGHT by ['G2'..'G11']
  [MAP]  must fail G10  b89: truncate the 0x0b container to a 148-byte stub     -> CAUGHT by ['G2'..'G11']
  [MAP]  must fail G3   make tileset 3 disagree with tileset 1                  -> CAUGHT by ['G3']

NEGTEST: 16/16 plants correct (8 declaration + 8 map-side); each had to fail its target
         gate AND stay inside its allow-set -> PASS
```

**Four of those sixteen are the vet's own negatives, reproduced as permanent regression tests.** The
subtlest - delete one shipped decoration and duplicate another so the instance count still reads 295
and the declared tail still matches perfectly - is caught by `G1c` **without a baseline map**, because
`G1c` now includes an md5 over the byte identity of all 281 shipped instances
(`78a536278d5dbdf23332e70750aa04d9`). A count check cannot see that edit, and the named-proxy check
cannot either when the deleted instance is one of the 270 decorations rather than one of the 11
proxies.

**Two allow-sets are deliberately wide, and that is disclosed rather than hidden.** The west-door-seam
plant and the pile plant also trip `G2`/`G3`/`G5`, because world x 4186.5 is on ground **owned by
`drxBC_Finale`**, not drxBC3, and the pile lands off-mesh for most of the 14. Those are genuine
consequences of the plant, not gate leakage, so they are listed in the allow-set with that reasoning
in the code.

**The negatives earned their keep in both rounds.** Round 1: they exposed that `G7` measured each new
proxy's distance to *itself* and that `G8`/`G9` read the built map instead of the declaration. Round
2: the map plants exposed that `G1c` as first written could not catch the delete-and-pad edit (which
is why the digest exists) and that `BSS.parse_blob_sections` returns `(sections, magic)` rather than
pairs - a bug in the plant helpers themselves, caught because the runner checks the converse.

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

### 5.3 Artifacts this lane actually built

All built in `.claude/worktrees/sanctuary-populate/` with `PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0
SVC_RELEASE_DROPS=1`. Nothing was written to `CustomMaps` and nothing outside this worktree was
modified.

| artifact | md5 | size | note |
|---|---|---:|---|
| `local/b100_r2/Levels_merged.arc` | `65063ae5fe89d75ef4a65ad46f1ea19d` | 688,692,862 B | **the round-2 deliverable** |
| `local/b100_r2b/Levels_merged.arc` | `65063ae5fe89d75ef4a65ad46f1ea19d` | 688,692,862 B | independent rebuild, **identical md5** - map-build determinism |
| `local/b100_base/Levels_merged.arc` | `718abad63e7813dc78c4b169df969fd5` | 688,692,225 B | baseline (merge-base `4f0299c` tree, same env) |
| `local/b100_new/Levels_merged.arc` | `48a51961bb3a36c39f82759845041f14` | 688,692,859 B | round-1 deliverable, SUPERSEDED (its placements were the even-spread set) |
| `work/SoulvizierClassic/Resources/Quests.arc` | `5e664c7b190965fd69f6ff15d77d85e4` | 194,926 B | COUPLED with Levels. **NOT the deployed bytes - see the drift table below.** |

#### ⚠️ THE `Quests.arc` DEPLOY-SAFETY CLAIM WAS FALSE (vet finding 1, HIGH)

Round 1 asserted, in four places (report sec 0, sec 5.3 table, sec 5.3 body, and the BUILD68-DEV
gate record), that the `Quests.arc` it built was *"byte-identical to the artifact already
deployed"*. The bytes on disk contradict it. There are **three distinct values** in play:

| role | md5 | size | written |
|---|---|---:|---|
| **DEPLOYED** `CustomMaps/SoulvizierClassicDEV/Resources/Quests.arc` | `bd0fb5f99d88fab74b81f27b7cb952b2` | 194,971 B | 2026-07-29 08:28 |
| **STAGED** (main checkout `work/`) and this lane's build | `5e664c7b190965fd69f6ff15d77d85e4` | 194,926 B | 2026-07-16 01:45 / this lane |
| b98's recorded ground truth (historical) | `35bfe3f39e8480408e3c22ea5473f796` | - | superseded 07-29 08:28 |

```
$ md5sum "/c/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassicDEV/Resources/Quests.arc" \
         work/SoulvizierClassic/Resources/Quests.arc
bd0fb5f99d88fab74b81f27b7cb952b2  .../CustomMaps/SoulvizierClassicDEV/Resources/Quests.arc   (194,971 B)
5e664c7b190965fd69f6ff15d77d85e4  work/SoulvizierClassic/Resources/Quests.arc                 (194,926 B)
```

"Identical to the CANONICAL STAGED copy" is true and is what round 1 actually measured; it is not
the same statement. This lane's own base commit `4f0299c` is the b98 addendum that recorded exactly
this drift (`git show 4f0299c | grep -i quests`), so the information was already in the tree.

**WHY IT MATTERS:** Levels+Quests are COUPLED, and `CLAUDE.md`'s standing warning is that shipping
the new map without the rebuilt `Quests.arc` yields **two widow letters** once the quest tracks. An
integrator reading "byte-identical to deployed" could reasonably conclude the Quests half needs no
attention. **It does:** the deployed Quests bytes differ from the staged/built ones, and this lane's
`Quests.arc` must be staged and deployed alongside the map. Registered as `BL-b100-DEBT-6`.

The `arz`/`Text.arc` cross-check DOES survive, and is worth keeping: the md5s this lane rebuilds
reproduce the b98 endless-hunt lane's recorded artifacts exactly
(`4378b617fefb2014e382bb5931e7d605` / `c33b6abe3d61559785ee00ab3280a765`, BUILD65-DEV gate record).
This branch is based on `4f0299c`, which is that lane's tip, and an independent build in a
different worktree on a different day reproduces both hashes to the byte - a determinism proof for
the DB/Text half of the pipeline and evidence this lane changed neither.

### 5.4 Every other gate, and its delta against the baseline

The point of running each of these on **both** maps is that an absolute verdict says nothing; a
zero delta does.

| gate | baseline | new | delta |
|---|---|---|---|
| `tools/verify_merged_bc_navmeshes.py` | 24/24 real navmeshes match donor, 7 ocean stubs valid | **24/24, 7 valid** | none |
| `tools/contracts/run_contracts.py --only map` (19 contracts) | 6 viol (0 P0, 0 P1, 6 P2), **GATE PASS** | 6 viol (0 P0, 0 P1, 6 P2), **GATE PASS** | **identical violation set, item for item** |
| `tools/contracts/gate_placed_record_resolution.py` | 346 missing placed refs, 397 seeds, 14,241 walked | 346 / 397 / 14,241 | **zero delta** - a PRE-EXISTING failure on `main`, not this lane's, and none of the 14 records this lane places is in the missing set |
| `tools/debug/gate_landing_clearance.py --wiring v1` | - | **PASS=27, GATE G-LAND PASS** | n/a (destination-set gate) |
| `tools/validate_tags.py` | - | **RESULT: PASS** - all 366 referenced mod tags present; 2 pre-existing base/SV monster-name warnings (backlog, non-blocking) | n/a (DB gate, DB unchanged) |
| `tools/gate_sanctuary_population.py` | (gate is new) | **PASS**, 8/8 planted negatives caught | n/a |

⚠️ **One measurement mistake worth recording:** the first `verify_merged_bc_navmeshes` run reported
`FAIL (1): new_secretdoor_transitionhallway`. That run used the wrong environment variable
(`SVC_MAP_ARC` instead of `SVC_MERGED_ARC`) and therefore read the **default** artifact -
main's `local/Levels_merged.arc`, a different and older build - not either of this lane's maps. Both
of this lane's maps read **24/24**. A verifier that silently falls back to a default path will
happily grade the wrong file.

### 5.5 RECORD DIFF against a real baseline built from `4f0299c` in the same environment

Not a document's hash - an actual second build. A detached worktree at `4f0299c` (this branch's
merge-base, and the `main` tip named in the brief) in the session scratchpad, with the same
interpreter, the same `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, the same upstream inputs and the same
staged resource arcs:

```
py tools/debug/b99_record_diff.py <baseline arz> <this branch's arz>

  records  : baseline 51108 -> built 51108
  ADDED 0 / REMOVED 0 / CHANGED 0
  RESULT: PASS
```

and, stronger than the record diff, the two arz files are **byte-identical**:

```
4378b617fefb2014e382bb5931e7d605  <scratchpad>/b100_baseline/work/.../SoulvizierClassic.arz   (built from 4f0299c)
4378b617fefb2014e382bb5931e7d605  .claude/worktrees/sanctuary-populate/work/.../SoulvizierClassic.arz
```

**Zero record changes, zero field changes, nothing to attribute** - which is the correct outcome for
a lane that touches no DB file. (`git diff 4f0299c HEAD -- tools/` confirms it by construction too:
the only pre-existing file this branch modifies is `tools/build_section_surgery.py`, which the DB
build does not import - it appears in `build_svc_database.py` and `apply_svc_patches.py` only inside
comments. Everything else this branch adds is a new file under `tools/debug/` or the new
`tools/gate_sanctuary_population.py`.)

### 5.6 Determinism of the derivation

```
PYTHONHASHSEED=0 -> local/b100_base/placements.json  md5 2d3cf483844086fe845ba48f4bab106e
PYTHONHASHSEED=1 -> local/b100_base/det_1.json       md5 2d3cf483844086fe845ba48f4bab106e
PYTHONHASHSEED=2 -> local/b100_base/det_2.json       md5 2d3cf483844086fe845ba48f4bab106e
```

Identical across three hash seeds, and the printed spec block is identical too (the only differing
line is the output filename). There is no RNG and no set-iteration-order dependence.

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
already ships and is already fought elsewhere in this same cave. Nothing is deferred, because there
is nothing new to defer: no new name, icon, portrait, race, sound, tooltip, drop or unlock exists.

```
py tools/debug/b100_player_surfaces.py <arz> <Text.arc> <Levels.arc>

  Text.arc tags loaded: 4491
  distinct creature records the 14 new encounters can spawn: 39
  ... every one is Class Monster, every name tag resolves in the mod's Text.arc, and
      every one ALREADY spawns in the blood cave - most of them in drxBC3 itself:
  01_bladedancer_35/36/37   tagAbomDW         5 levels incl. drxBC3
  02_spearrunner_37/38/39   tagAbomSpear      5 levels incl. drxBC3
  03_ravager_38/39/40       tagAbomBrute      4 levels incl. drxBC3
  04_spiritcaller_40/41/42  tagAbomShaman     2 levels incl. drxBC3
  a_acolyte_28/29/30        tagBWacolyte      6 levels incl. drxBC3
  a_small_blooddemon_25/26/27  tagBDLesser    4 levels incl. drxBC3
  b_med_blooddemon_30/31/32    tagBDMedium   11 levels incl. drxBC3
  c_large_blooddemon_38/39/40  tagBDLarge     4 levels incl. drxBC3
  b_bloodhound_33/34/35     tagBDHoundSmall   7 levels incl. drxBC3
  c_bloodhound_40/42/44     tagBDHoundLarge   7 levels incl. drxBC3
  b_seductress_39/41/43     tagBWseductress   6 levels incl. drxBC3
  c_disciple_39/41/42       tagBWdisciple     8 levels incl. drxBC3
  d_reaver_40/41/42         tagBWreaver       2 levels incl. drxBC3

  PLAYER-SURFACE CHECKLIST: PASS (0 problem record(s))
```

⚠️ The first cut of this probe hand-rolled a Text.arc reader and reported **39 false failures**,
because it split the UTF-16 `modstrings.txt` on `b'\n'` and produced 4,491 nonsense keys. Fixed by
using the repo's own `validate_tags.collect_text_arc_tags`. The repo's standing law about not
inventing a parser applies to probes too - this is the second time in this lane that ignoring it
produced a confident wrong answer (the first was the design pass's own flat-XZ coordinate model).

---

## 8. WHAT IS **NOT** DONE

Exhaustive; a triaged item is not a done item.

1. **NO IN-GAME CHECK.** Nobody has walked the Sanctuary with this population in it. No agent in
   this lane may launch TQ or Steam. Every claim here is a claim about bytes and geometry, not about
   feel. The density figures are **effective-entity sums over a chosen 60x60 u box** - the worst case
   the data permits with the documented spawn multiplier applied. TQ's real camera footprint was NOT
   measured, and actual concurrent load depends on player pathing and aggro.
2. **NOT DEPLOYED.** Nothing was written to `CustomMaps`.
3. ⚠️ **THE COUPLED `Quests.arc` IS NOT THE DEPLOYED ONE.** Deployed = `bd0fb5f99d88fab74b81f27b7cb952b2`
   / 194,971 B; this lane's build and the staged copy = `5e664c7b190965fd69f6ff15d77d85e4` / 194,926 B.
   Levels+Quests are COUPLED, so the integrator **must** stage and deploy this lane's `Quests.arc`
   with the map. Round 1 asserted these were identical, in four places, and that was false
   (`BL-b100-DEBT-8`, R-113).
4. **THE OCEAN RING IS UNTOUCHED** - `WILL_DECISION-1`. **CORRECTED FIGURES:** the four tiles hold
   **14,673 sq u** of their OWN walkable ground (01: 9,785 / 02: 3,299 / 03: 1,563 / 04: 25), not the
   42,199 sq u the design pass and the vet both quoted - that number counted padded neighbour strips.
   The widest own-area-to-own-area opening off drxBC3 is **21.4 u**, not 107.2 u. It IS genuinely
   reachable (b13 lattice offset **0.000 mod 12.8** at every drxBC3 ocean seam, with measured walkable
   crossings - the check the vet said it had not done). **So: this lane populates 23,994 sq u and
   leaves 14,673 sq u empty, i.e. it addresses 62.1% of the reachable own-area empty ground and
   Will's report is NOT fully resolved.** Which is exactly why it stays his call (R-114).
5. **THE MINIMAP IS NOT FIXED** - R-111 / `BL-b100-DEBT-3`. Mechanism measured and filed; it is a
   coupled `arz`+`Text`+`Levels` change and Will scoped it secondary.
6. **DENSITY IS UNRATIFIED** - `WILL_DECISION-2`. 32.6 -> 51.6 effective against a *derived* cap of
   57.0 is engineering, not Will's ruling. One-line knob: `SCREEN_CAP_EFF`.
7. **`docs/amgoz1_design_voice.md` STILL DOES NOT EXIST** - `WILL_DECISION-4`. Confirmed again this
   round: zero hits across all of git history. The creative bar this content is held to remains
   reconstructed from R-15, `docs/BLOOD_TOXEUS_DESIGN.md` and `docs/BOSS_SOULS_DESIGN.md`, and that
   reconstruction is unratified even though `CLAUDE.md`, `docs/BACKLOG.md` and every content brief
   cite the file as binding law.
8. **THE INHERITED 7.4 u SPACING VIOLATION IS WAIVED, NOT FIXED** - `BL-b100-DEBT-7`. amgoz1's own
   pair; moving it defaults to WILL-VETO.
9. **FIVE LOAD-BEARING CONSTANTS ARE CHOICES, NOT LAWS** (`BL-b100-DEBT-11`): `SEP_MIN = 16.0`,
   `SCREEN_CAP_EFF = 57.0`, `CORRIDOR_SLACK = 60.0`, `EDGE_CLEAR = 10.0`, and the 120 u band-1
   boundary. Round 1 attributed the 16 u to R-30; **R-30 fixes no distance** and its status is
   unchanged (**PENDING**). Two placements sit exactly on the `CORRIDOR_SLACK` limit - inherent, since
   the derivation filters on the same constant, but it does mean "on the processional" tolerates 60 u
   of detour on a 690.6 u route.
10. **THIS BRANCH IS NOT ON CURRENT `main` AND NEEDS AN INTEGRATION MERGE.** It branched from
    `4f0299c` as briefed; `main` has moved repeatedly during both rounds (now `ad0711b`).
    `docs/BACKLOG.md` and `docs/WILL_RULINGS.md` are the likely conflict points. The ruling decade is
    uncontested (R-110..R-114 here; `main` holds only R-100..R-102) but **re-run the check - it is a
    race**, and `build69-dev` was taken by another lane between round 1 and round 2, which is why this
    round takes `build70-dev`.
11. **`MAP-SANCTUARY-1` IS NOT WIRED INTO ANY AUTOMATIC RUNNER.** It is a standalone gate the
    integrator must invoke, like `gate_landing_clearance` and `verify_merged_bc_navmeshes`.
12. **`tools/contracts/gate_placed_record_resolution.py` FAILS ON `main` ALREADY** (346 missing placed
    record refs, base-game setdressing). Zero delta from this lane and none of its 14 records is in
    the missing set, but it is red before and after.
13. **15 MISALIGNED NAVMESH SEAMS EXIST ON THE SHIPPED MAP** - identical before and after this lane
    (`BL-b100-DEBT-10`). All involve `ocean_extensionx*` tiles plus `ocean_extension02|05` and
    `03|05`. Per b13 those seams do not stitch, so parts of the outer ocean ring may be unreachable.
    Not investigated; not this lane's.
14. **I OVERWROTE A SHARED GITIGNORED SCRATCH ARTIFACT** (`BL-b100-DEBT-9`). The first round-2 map
    build wrote the MAIN CHECKOUT's `local/Levels_merged.arc`, because
    `tools/svaera_plus_portals.py` hardcodes that directory as its default output. The staged
    canonical and the deployed copy were both verified untouched; the stray build is preserved as
    `local/Levels_merged.b100r2-STRAY-DO-NOT-DEPLOY.arc` so nothing can consume it via
    `-SyncLevels`, and every later build used `SVC_OUT_DIR`. Whatever a previous lane had left at
    that path is gone and unrecoverable. It was regenerable scratch and `CLAUDE.md` says never to
    trust it, but it was not mine to overwrite.
15. **THE `reference_mods/` CACHE IS EMPTY IN THE MAIN CHECKOUT**, so the Steam-Workshop fallback is
    now load-bearing for every `Quests.arc` build (`BL-b100-DEBT-8`). Repopulating it is a follow-up.

---

## 9. THE VET'S 13 FINDINGS, ONE BY ONE

Every finding was re-measured. Nothing here is a restatement of a round-1 claim.

| # | sev | finding | verdict | what changed |
|---|---|---|---|---|
| 1 | HIGH | `Quests.arc` "byte-identical to deployed" is false | **CONFIRMED** | Fixed in 4 report places + gate record + R-113. Deployed `bd0fb5f9…`/194,971 vs built `5e664c7b…`/194,926. Also uncovered and fixed a *silent stale-input bug* in `build_quest_files.py`. |
| 2 | MED | the gate does not enforce the RETIREMENT PROTOCOL it claims | **CONFIRMED** | New `G1c` (total + 11 named shipped proxies + 281-instance byte digest, baseline-free) and `G1d` (byte diff vs baseline). All four of the vet's map-side negatives are now permanent plants and all four are caught. |
| 3 | MED | density comparison mixes two pool multipliers | **CONFIRMED** | Density regated in EFFECTIVE entities (`SCREEN_CAP_EFF = 57.0`). Measured `_01` = 3.60025x, `_02` = 1.357143x; cohort corrected to median 90.0 / p90 158.4 / max 280.8. No placement moved. |
| 4 | MED | `SCREEN_CAP`'s own code comment contradicts the constant | **CONFIRMED** | The stale 24/18/70 and proxy-centred 23/72 text is gone; the block now documents the effective-unit derivation. |
| 5 | MED | R-110 records a shape the code produces the opposite of | **CONFIRMED** | Mechanism changed from farthest-point to group-clustered insertion. NN Chebyshev min 23.2/med 31.8 -> **min 16.0/med 30.0/max 62.2**. On rotation: **not a defect** - all 25 `Proxy` instances amgoz1 placed in drxBC3 are identity, so identity is the host level's own convention (measured; 228 of its 269 *non*-proxy instances ARE rotated). |
| 6 | MED | `--arz` default resolves to another lane's artifact from a worktree | **CONFIRMED** | Both defaults made `REPO`-relative in `b100_derive_sanctuary.py` and `b100_density_census.py`. |
| 7 | MED | scope: the ocean ring is 1.76x the populated area, ~36% addressed | **CONFIRMED DEFECT, WRONG NUMBERS** | The emptiness is real and stays `WILL_DECISION-1`. But 42,199 sq u is the ALL-AREA sum incl. navmesh pad; own-area is **14,673** = **0.61x** the populated area, so **62.1%** is addressed, not 36%. Seam opening **21.4 u**, not 107.2. And the b13 stitching the vet did not measure **is satisfied** (0.000 mod 12.8). R-114. |
| 8 | LOW | "8 plants, one per invariant, 8/8" is not accurate; no plant isolates its target | **CONFIRMED** | 16 plants across 2 kinds; each declares target + allow-set and the runner checks the converse. `--baseline` is now threaded into `--negtest` so G1d/G10 identity halves are exercised. |
| 9 | LOW | G3 is not independent; navmesh corruption crashes the gate | **CONFIRMED** | Tileset equality is RECORDED (`tileset_diffs`) not asserted; `Sanctuary(strict=False)` reports `nav_error`, so both b89 plants now produce a `G10` FAIL instead of an `AssertionError`. |
| 10 | LOW | two placements sit exactly on the G6 limit; G7 margin 0.1 u | **PARTIALLY WRONG** | The numbers are right; "no slack" is a misreading. The derivation filters on the *same* constants the gate checks, so admissible cells reach the limit by construction, and the 0.2 u navmesh lattice makes 20.1 u the closest admissible cell to a 20.0 u exclusion. Gate now prints margins **and** this explanation. The real residual (60 u of tolerated detour is a taste choice) is `BL-b100-DEBT-11`. |
| 11 | LOW | `SEP_MIN = 16.0` attributed to R-30, which sets no number | **CONFIRMED** | Attribution corrected in code and in the gate row text; added to the constants-not-laws list. R-30 stays PENDING, untouched. |
| 12 | LOW | minor tooling defects (dead expression, unused const, 8-slot loop, self-checked differ) | **CONFIRMED** | Dead `sum(1 for _ in ())` removed; `MIN_AREA` removed with a note on why the area half of the cohort filter never ran; pool slots now discovered from the record's own fields (`zparty_witchfest_2099` has a `name9`); the whole-map diff conclusion is independently corroborated by `verify_merged_bc_navmeshes` + the contract suite + G10's byte comparison. |
| 13 | LOW | two doc inaccuracies (band-2 tier comment, circular player-surface proof) | **CONFIRMED** | Band-2 comment now states the anchor sits at world Y **-14.40** on a ramp while the other three are at -10.00. Player-surface probe re-run against the **baseline** map (PASS, 0 problems, 39 records) and now **refuses** a post-change map unless `--allow-postchange` is passed. |

---

## 10. ENVIRONMENT NOTES FOR WHOEVER INTEGRATES THIS

- **Nothing was deployed.** `CustomMaps\SoulvizierClassicDEV` was last written at
  **2026-07-29 08:28** (`Quests.arc`) and **2026-07-27 16:48** (`Levels.arc`), both before this lane
  started. Its `Levels.arc` is 688,679,840 B and is NOT this lane's artifact.
- **The canonical staging artifacts are untouched.** Re-hashed at the end of the lane:
  `work/SoulvizierClassic/Resources/Levels.arc` = `fc0adcc0713839a685b32d6e122653be`, exactly the
  md5 the recon pinned; `work/.../Quests.arc` = `5e664c7b190965fd69f6ff15d77d85e4`; the DEPLOYED
  `Levels.arc` = `943d0ab9516d332db79bd7f9fd2d3ffe`. All three re-verified at the end of round 2.
- ⚠️ **ROUND-2 CORRECTION - round 1's claim that every build went via `SVC_OUT_DIR` "never to the
  shared `local/` default" DOES NOT HOLD FOR ROUND 2.** `tools/svaera_plus_portals.py` hardcodes
  its default output dir to `c:\Users\willi\repos\tqit_soulvizier_classic\local` - the MAIN
  CHECKOUT - and the first round-2 map build ran without `SVC_OUT_DIR`, so it **overwrote the main
  checkout's gitignored scratch `local/Levels_merged.arc`**. The staged canonical and the deployed
  copy were both verified untouched (hashes above). The stray build was renamed
  `local/Levels_merged.b100r2-STRAY-DO-NOT-DEPLOY.arc` - bytes preserved, zero data loss - so that
  `deploy_to_custommaps.ps1 -SyncLevels` cannot pick up an unvetted artifact, and there is now no
  bare `local/Levels_merged.arc` in the main checkout. Whatever a previous lane had left there is
  gone and unrecoverable; it was regenerable scratch that `CLAUDE.md` explicitly says never to
  trust, but it was not mine to overwrite. Every later build used `SVC_OUT_DIR`, and a second build
  into an isolated dir reproduced the deliverable's md5 exactly. `BL-b100-DEBT-9`.
- ⚠️ **CONCURRENT DRIFT, not this lane's:** `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
  in the MAIN checkout was rewritten at **11:16** during this session (55,475,124 B, md5
  `967b1f97137bf6479c18c08e9dd6ffc4`) by another lane. This lane's arz is a different file in a
  different worktree (`4378b617fefb2014e382bb5931e7d605`, 55,460,430 B, 12:18). Do not assume the
  main checkout's staged arz is anybody's ground truth right now.
- **Two gitignored caches had to be populated for a cold worktree build**, both read-only-ish and
  worth knowing about:
  1. `build_quest_files.py` hard-codes `upstream\soulvizier_098i\Resources\XPack\Quests.arc`
     relative to cwd (the SOURCE of the ported `.qst` files), and that file is **not** covered by
     `tools/check_build_inputs.py`. It is absent from every cache on this machine and had to be
     extracted from `third_party/soulvizier098i.zip` (`Resources/XPack/Quests.arc`, 222,487 B, md5
     `a1b8020b20f41ca5b7e4af916bebf039`; still present in this worktree, re-verified round 2).
     **Still worth adding to the preflight.**
  1b. ⚠️ **ROUND 2 FOUND AND FIXED A WORSE ONE, IN THE SAME FILE.** `build_quest_files.py` also
     needs SVAERA's **pristine `Quests.arc`** as the base it restores *before* patching, and it
     resolved that with a bare repo-relative `reference_mods\SVAERA_customquest\Resources\Quests.arc`
     guarded by `if svaera_quests.exists()`. `reference_mods/` is gitignored and **EMPTY in every
     fresh worktree AND in the main checkout**, so the restore SILENTLY DID NOTHING and the build
     went on to patch the ALREADY-PATCHED `work/.../Quests.arc` from the previous run. It surfaced
     only as `ValueError: expected exactly 1 reference to the Rhodes portal after the patch, found
     3` from `_add_typhon_rhodes_unlock`'s own survival assert - which means that assert block, whose
     docstring insists it is not orphaned, is the only thing standing between this repo and a
     DOUBLE-PATCHED `Quests.arc` shipped attached to a map. FIXED: `svaera_quests_arc` is now
     registered in `tools/check_build_inputs.py` with the same md5-pinned fallback chain as every
     other SVAERA input (`SVC_SVAERA_QUESTS_ARC` -> in-repo cache -> main checkout's cache -> Steam
     Workshop item 2076433374; pinned `b786666ccc7accf4b533adecc457ce81`, 194,578 B) and the restore
     always runs, failing loud on a miss. `Quests.arc` then rebuilds reproducibly to
     `5e664c7b190965fd69f6ff15d77d85e4` with the quest-record contract PASS over 107 records.
  2. The DB build's `mastery_sv_alignment.verify` resolves emblem textures against
     `work/SoulvizierClassic/Resources/*.arc`, so a worktree with an empty staging dir fails that
     verify with a misleading "emblem tex UNRESOLVED" rather than "your staging dir is empty". The
     art arcs were hardlinked in from the main checkout (no copy, no mutation of the source).
- **Shared git config was not mutated** (checked at the end: no `core.worktree`, `core.bare=false`
  as it already was, `user.name`/`user.email` unchanged and matching the branch's earlier commits).
  The temporary baseline worktree in the session scratchpad was removed with `git worktree remove`.
