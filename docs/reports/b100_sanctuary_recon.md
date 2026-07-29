# b100 - Sanctuary of the Bloodborn: RECON + DESIGN (read-only, pre-implementation)

> **Will's report, verbatim:** the Sanctuary of the Bloodborn has "large walkable areas with no
> enemies placed", and "the minimap doesn't render them". He added the minimap "isnt a huge issue".
> **Priority order is therefore EMPTY SPACE first, minimap second.** This doc does not invert that.
>
> **Rulings decade claimed: R-110..R-119.** Verified free by
> `git grep -ohE "\bR-[0-9]+\b" <every branch except this one>` -> the full claimed set is
> R-1..R-51, R-60/61, R-70..R-76, R-80..R-87, R-90..R-98, R-100..R-102 (plus the sentinel R-9999).
> **R-110..R-119 has zero hits on any branch.**
>
> ⚠️ **This claim MOVED mid-lane and the history is kept deliberately.** The decade was first taken as
> R-100..R-109, which was genuinely free at the time. While this lane ran, two other lanes advanced
> concurrently: `feat/leinth-wave` merged into `main` (adding **R-98** and taking the `build66-dev`
> tag), and a new branch **`fix/blade-mastery-truth`** appeared and claimed **R-100, R-101, R-102**.
> The re-check caught the collision and this lane yielded, moving to R-110. Anyone re-running the
> freshness check should re-run it rather than trusting this line: concurrent lanes make ruling-decade
> freeness a race.
>
> Nothing was appended to `docs/WILL_RULINGS.md` this turn: no new WILL decision was made, and the
> ledger takes Will's words verbatim only. Section 7 lists what will become R-110..R-113 once he rules.
>
> **GROUND TRUTH (built artifacts, not documents).** Every number below was measured against:
> - `work/SoulvizierClassic/Resources/Levels.arc` = **md5 `fc0adcc0713839a685b32d6e122653be`**,
>   688,691,547 B (hardlink-identical to `local/Levels_merged.arc`; `md5sum` on both).
>   Inner `world/world01.map`: 2,095,227,743 B, md5 `234a9f7cc2cb09a917803d9bca8e31ef`, 2282 levels.
> - coupled `work/SoulvizierClassic/Resources/Quests.arc` md5 `5e664c7b190965fd69f6ff15d77d85e4`
> - `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (51,085 records)
> - merge donor `upstream/soulvizier_098i/Resources/Levels.arc` md5 `0b575c9dcd95461ec4ef2dea351f7d36`
>   (296,098,872 B, 1004 levels) and merge base SVAERA `Levels.arc` md5 `a1e13e48b3de499df31a5ca4d919030d`
> - base game `.../Titan Quest Anniversary Edition/Database/database.arz`
>
> Readers used are the repo's own, no new parser was invented: `tools/contracts/contracts_map.py`
> (`Arc`, `Arz`, `parse_level_index`, `parse_blob_sections`, `parse_0x05`, `blob_0x05_base`),
> `tools/sd_format.py`, `tools/rec02_format.py`, `tools/build_section_surgery.py:parse_0x17_header`.
>
> **NOT DONE / NOT CLAIMED:** nothing deployed, nothing written to CustomMaps, no build run, TQ and
> Steam never launched. No implementation yet - this is the design gate that precedes it.

---

## 0. TL;DR

| question | answer |
|---|---|
| **What is the Sanctuary** | Exactly **one** level carries the region label: `Levels/World/xBloodCave/drxBC3.lvl` (idx 2253). But the player-perceived Sanctuary is **5 levels**: drxBC3 plus the navmesh-stitched, banner-inheriting `ocean_extension01/02/03/04`. |
| **Where is the empty space** | The 4 ocean tiles hold **0 monster proxies over 42,199 sq u** of walkable navmesh. Deduplicated, the reachable Sanctuary is **41,067 sq u with 10 monster proxies**; **92.9% of it has no proxy within 10u**, 75.7% none within 20u. |
| **Why** | **Cause (a): nothing was ever placed there.** (b), (c), (d) each disproven below - (d) by a placement-identical diff against pristine SV 0.98i. |
| **What should live there** | A **congregation, not a patrol**: 4 bands of the existing blood-cult hierarchy escalating west along the player's actual walk. 14 new proxies, all from pools that already ship. Section 4. |
| **Density safety** | Worst case **18** simultaneous entities in one screen (measured on derived placements), vs base-game median 14 / p90 70 / max 162, vs b76's "well over 100". Section 5. |
| **Minimap** | **DIFFERENT defect from b46.** b46 = *empty* zone `dbr`. Here the zone `dbr` is *valid* but the cluster was grid-shifted **2,986 u east** of every native tile on that zone's page, so the TGA composites off-page. Section 6. |

---

## 1. WHAT THE SANCTUARY IS, PHYSICALLY

### 1.1 The label binds to one level

Mechanism is b46 round 3 (`docs/reports/b46_minimap_result.md`), not re-derived here: the top-right
banner = the level blob's `0x17` **REGION** GUID list resolved against the world `SD (0x18)` REGION
records. Scanning all 2282 levels' `0x17` REGION lists against the SD:

```
SD REGION  name='BCXwalkway'  tag='tagBCXwalkway'  guid=5d2c6b44aaa319af364c018bdcae91d3
  levels binding this region: 1
    idx=2253  Levels/World/xBloodCave/drxBC3.lvl  corner=(4186,-37,2869)  blob=1,113,386 B
```

`tagBCXwalkway` -> **"Sanctuary of the Bloodborn"** (already gate-locked by `MAP-SD-2` /
`RESTORED_ZONE_LABEL_EXPECT`; BACKLOG closed that on 2026-07-28).

`drxBC3.lvl`: LVL v0x0e, grid corner `(4186,-37,2869)`, tile dims `(120,20,120,120,28,120)` ->
declared footprint **X[4186,4426] Z[2869,3109]**, i.e. 240 x 240 world units.
Blob sections `0x05(18,778) 0x14(56) 0x06(10,000) 0x09(73,410) 0x0b(857,212) 0x17(153,878)`.

### 1.2 But the player-perceived Sanctuary is FIVE levels

`drxBC3`'s `0x0b` declares neighbours `drxBC_Finale, ocean_extension01, 02, 03, 04`. For those four
ocean tiles, **all three** of the following hold, measured:

1. **Their `0x17` REGION list is EMPTY.** By the b46 mechanism an empty REGION list means no region
   resolves and the banner **retains the previous region** - so walking out of drxBC3 onto them, the
   screen still reads **"Sanctuary of the Bloodborn"**.
2. **They carry the `Sanctuary` ENV preset** (SD env `d9bbaa21ca32128f3d4cf0ed5852b0e6`) - identical
   fog/lighting to drxBC3. They *look* like the Sanctuary.
3. **They are genuinely walkable from it.** Seam measurement (shared world columns carrying walkable
   cells on both sides within 0.6u of the shared grid line):

| seam | axis | line | shared columns | widest contiguous run |
|---|---|---|---:|---:|
| drxBC3 <-> ocean_extension02 (east) | x | 4426.0 | 536 | **107.2 u** |
| drxBC3 <-> ocean_extension01 (south) | z | 2869.0 | 238 | 20.8 u |
| drxBC3 <-> ocean_extension03 (north) | z | 3109.0 | 46 | 9.2 u |
| drxBC3 <-> ocean_extension04 | corner | - | cells coincide, closest approach **0.0 u** | - |
| drxBC3 <-> drxBC_Finale (west) | x | 4186.0 | 64 | 12.8 u |

A 107-unit-wide opening on the east seam is not a leak, it is an invitation. **This is what Will
walked into.**

### 1.3 How the player enters and leaves

Every entry/exit object in the cluster, resolved against the `.arz` by Class:

- **IN:** `yet_another_fucking_connector.lvl` holds `GridEntranceDynamic xprtl_et2fn_01.dbr` at world
  `(4573,4,3491)`, dressed with `medeagrove_columnportal01` + `map_portal_aura`, and armed by a
  `BoundingVolume` trigger **`trg_open_sanctuaryportal.dbr`** at `(4583,4,3492)`. ("et2fn" =
  extension-to-finale.)
- **ARRIVE:** drxBC3's paired `GridExitOneWay xprtl_et2fn_02.dbr` at world `(4411,2,3089)` - the
  **north-east corner** of the walkway. A `StrategicMovementRespawnShrine`
  (`respawn_hades_shrine01.dbr`, Hades-palace mesh, blue dynamic light) sits 4 units away at
  `(4388,2,3085)`.
- **OUT:** there is **no return portal**. The player leaves by **walking WEST** across the walkway
  into `drxBC_Finale` over the 12.8u seam at x=4186.

So the Sanctuary is a **one-way west-bound processional**: portal in at the NE corner, walk the
length of it, exit west into the finale. That geometry is what the population plan is built around.

### 1.4 Set dressing = what the place is

The 281 placed instances are 214 `Decoration`, 53 `EffectEntity`, 11 `Proxy`, 1 `SoundObject`,
1 respawn shrine, 1 grid exit. The decoration roster is unambiguous: `bossroomdress/setdress/hp_*`
(**h**ades **p**alace pit decorations, pillars, pillar tops, rock formations), `bloodcave/bridges/*`
(bridge tiles, `finale_pitstraight`, `finale_pitwedge`), `bloodcave/bones/*` (skeletal remains,
including 6 distinct `skeletalremainsbossroom*`), 42 x `map_formation_ambient`, 11 x
`fountainsplash03`, 10 x `cloud01/02`, and one `riversmall` sound object.

**It is a Hades-palace-styled stone walkway over a pit, strewn with bones, under drifting cloud,
with water sounding below.** The neighbouring `bossfight.lvl` binds the region
`Palace of Hades ~ Outer Court`, confirming the architectural language.

---

## 2. WHERE EXACTLY THE EMPTY SPACE IS (MEASURED)

### 2.1 Method

Walkable area is decoded from each level's `0x0b` REC\x02 navmesh (`tools/rec02_format.py`
`parse_rec02(decompress=True)`, tileset 0), counting cells where `height != 0xff and area != 0`.
Cell size 0.2 u -> **0.04 sq u per cell**. Placed proxies come from `0x05`.

**Coordinate correction that had to be pinned first (this is a real trap):** `0x05` instance
positions are **level-LOCAL** (drxBC3's span 0..239.3), while the `0x0b` navmesh is **WORLD**-space
(drxBC3's box X[4128,4512] Z[2798,3182]). `world = grid_corner + local`. Proven by an **on-mesh
gate**: under this offset **100% of monster proxies land on a walkable cell on every one of the 16
blood-cave levels that has any** (a naive no-offset comparison reported 100% of area "far from any
proxy" on every level, including the dense ones - an obviously false result that flagged the bug).

**Honest caveat:** the `0x0b` container is padded beyond the declared level footprint, so per-level
walkable areas **overlap at seams** and cannot simply be summed. Where a total is given it is a
**deduplicated union** on an exact integer 0.2u world lattice.

### 2.2 The Sanctuary complex, per level

| level | walkable (own `0x0b`) | monster proxies | sq u per proxy | 0x05 instances |
|---|---:|---:|---:|---:|
| **drxBC3** (the walkway itself) | 35,488 sq u | **10** | **3,549** | 281 |
| ocean_extension01 | 17,055 sq u | **0** | inf | 21 |
| ocean_extension02 | 9,649 sq u | **0** | inf | 0 |
| ocean_extension03 | 7,991 sq u | **0** | inf | 12 |
| ocean_extension04 | 7,504 sq u | **0** | inf | 0 |

Restricted to drxBC3's **own declared footprint** (X[4186,4426] Z[2869,3109], excluding navmesh pad):
**23,994 sq u** of walkable ground carrying those same 10 proxies = **2,399 sq u per proxy**.

### 2.3 The headline number

Deduplicated union of the five levels' walkable cells (47.1% raw overlap removed):

```
SUM (raw)   1,942,168 cells   77,687 sq u
UNION       1,026,665 cells   41,067 sq u      <-- player-reachable Sanctuary
monster proxies in the whole group: 10         -> 4,107 sq u per proxy
```

Distance from walkable ground to the nearest monster proxy, over that union:

| no proxy within | area | share of the reachable Sanctuary |
|---:|---:|---:|
| 10 u | 38,150 sq u | **92.9%** |
| 15 u | 34,861 sq u | 84.9% |
| 20 u | 31,069 sq u | **75.7%** |
| 25 u | 27,928 sq u | 68.0% |
| 30 u | 25,418 sq u | 61.9% |
| 50 u | 19,395 sq u | 47.2% |

**42,199 sq u of the complex (the four ocean tiles, before dedup) has zero monster proxies placed at
all.** That is the specific region Will would have walked through: step off the east side of the
walkway through the 107-unit-wide opening at x=4426, and there is nothing out there in any direction.

### 2.4 Calibration against the base game (measured, same method, same map)

147 base-game cave/crypt/tomb levels in this same canonical map with >=5 proxies and >3,000 sq u:

```
sq u per proxy:  min 121   p25 242   MEDIAN 395   p75 534   max 3,836
```

**drxBC3 at 3,549 sq u/proxy is the 2nd sparsest of the 147 - the sparsest 1.4% - and 9.0x the
median.** Only `TomLargeSection.lvl` (3,836) is sparser. Within the blood cave itself the contrast is
sharper still: `drxFirstRoom` 421, `drxBC2` 556, `yet_another_fucking_connector` 589,
`drxBC_Connector2` 918, `drxBC_Finale` 1,255.

**The emptiness is reproducible from the data and is not an artifact.** Will's report is confirmed.

---

## 3. WHY IT IS EMPTY

The four candidate causes, each tested. The b98 refutation is respected: `difficultyLimitsFile` only
scales player level and NEVER filters whether a proxy resolves, so the refuted b91 reasoning is not
reused anywhere below.

**(b) proxies placed but resolve to nothing - DISPROVEN.** All 10 monster proxies resolve in the
`.arz` as Class `Proxy`, every `pool1` resolves as Class `ProxyPool`, and every pool has live
`nameN` entries with non-zero weights and non-zero spawn counts:

| proxy | count | pool spawnMin/Max | championMin/Max | families in pool |
|---|---:|---|---|---|
| `zparty_witchfest_2099` | 4 | 6 / **12** | 1 / 3 | bloodwitch disciple + reaver + bloodhound; champions = seductress + large blooddemon |
| `bw_priest_houndmaster` | 3 | 1 / **3** | 2 / 2 | bloodwitch priest + hounds |
| `hound_01_pack` | 1 | 3 / **6** | 0 / 2 | bloodhound b_33/34/35, champ c_40/42/44 |
| `bw_reaver_lone` | 1 | 1 / 1 | 0 / 0 | d_reaver_40/41/42 |
| `bw_seductress_lone` | 1 | 1 / 1 | 0 / 0 | b_seductress_39/41/43 |

Weights are 150/150/150 on the primaries - nothing is weight-0. `proxyPoolEquation` is
`records\proxies orient\proxypoolequation_02.dbr` (present) on all of them. These proxies work.

**(c) spawn budget starves them - DISPROVEN for single-player.** Summed `spawnMax` over the whole
walkway is 65 across 10 proxies, and the measured worst-case 60x60 screen load is **12** entities.
Nothing is competing for a budget; there is simply almost nothing placed. (Known separate issue, out
of scope and unchanged: per `CLAUDE.md`, SV's `RunEquation` MP spawn-scaling formulas fail to parse
in AE, which silently reduces spawns in **multiplayer only**.)

**(d) a merge dropped them - DISPROVEN, definitively.** `0x05` census of our canonical map vs the
**pristine SV 0.98i merge donor**:

| level | OURS inst/proxy | SV 0.98i inst/proxy | verdict |
|---|---|---|---|
| drxBC3 | 281 / 10 | 281 / 10 | **IDENTICAL** |
| ocean_extension01 | 21 / 0 | 21 / 0 | IDENTICAL |
| ocean_extension02 | 0 / 0 | 0 / 0 | IDENTICAL |
| ocean_extension03 | 12 / 0 | 12 / 0 | IDENTICAL |
| ocean_extension04 | 0 / 0 | 0 / 0 | IDENTICAL |
| drxBC_Finale | 164 / 42 | 164 / 42 | IDENTICAL |
| drxFirstRoom | 2352 / 71 | 2352 / 71 | IDENTICAL |
| drxBC2 | 1815 / 26 | 1815 / 26 | IDENTICAL |

Per-proxy roster for drxBC3 also matches item-for-item (witchfest 4/4, houndmaster 3/3, reaver 1/1,
seductress 1/1, hound pack 1/1). **Our merge dropped nothing.**

### VERDICT: cause (a) - nothing was ever placed there.

amgoz1 shipped `drxBC3` with 10 proxies over 24k sq u of its own footprint, and shipped the four
surrounding ocean tiles with **zero**. Our pipeline preserved that faithfully. The emptiness is
**inherited upstream content debt, newly exposed** - exactly the b46 pattern, where an SV-original
gap only became visible once the area was actually reachable and being walked. It is not a
regression, and there is nothing to "restore"; this is a **content authoring** job.

---

## 4. WHAT SHOULD LIVE THERE

> WARNING. **The brief cites `docs/amgoz1_design_voice.md` as law. That file DOES NOT EXIST** - not in
> the worktree, not on `main`, and not anywhere in git history (`git log --all --diff-filter=A
> --name-only | grep -i amgoz` = 0 hits). It is referenced by `docs/BACKLOG.md` and
> `docs/WILL_RULINGS.md` (R-15) as a standing bar but was never written. Registered as debt
> (BL-DEBT-b100-5). The bar below is reconstructed from the surviving statements of it: BACKLOG
> "new content = amgoz1 creative bar", "monster-identity-driven, flavorful, never generic filler",
> R-15's creative-text veto, and the worked exemplars `docs/BLOOD_TOXEUS_DESIGN.md` and
> `docs/BOSS_SOULS_DESIGN.md`. **Flagged for Will as WILL_DECISION-4.**

### 4.1 The design idea

The Sanctuary is **the Bloodborn's own holy place**, and it is the last ground before the finale.
The mistake to avoid is a patrol pattern - evenly spaced packs that read as corridor filler. The
place has bones, pillars, a pit, and water below; it is a **processional**.

So: **a rite in progress, and the player walks up its aisle.** Population escalates strictly westward
along the one-way walk from the arrival portal `(4411,3089)` to the threshold at x=4186, moving up
the cult's own hierarchy - laity, congregation, clergy, then the flesh-crafted things that guard the
god's door. Every band is drawn from creatures that **already spawn in this cave complex**, so the
Sanctuary reads as the same cult at its centre rather than a new bestiary.

The existing 10 proxies are **kept and reused as the skeleton** of bands 1-3, not overwritten (the
retirement protocol applies: nothing is deleted).

### 4.2 The bands

Derived on-mesh from the measured walkable set of drxBC3's own footprint (23,994 sq u), each band
sized by its actual walkable area:

| band | x range | walkable | ADD | why this creature, here |
|---|---|---:|---|---|
| **1. The Outer Court** | 4380-4426 | 4,516 sq u | 2 x `bw_acolyte_lone` | The arrival breath. You step out of the portal beside a Hades respawn shrine; two novices kneel alone at the edge of the rite, too rapt to have noticed you. Lone acolytes are the weakest thing in the cult and this is the only place in the mod where that reads as *devotion* rather than as filler. |
| **2. The Congregation** | 4310-4380 | 8,871 sq u | 2 x `zparty_witchfest_2099`, 2 x `bw_acolyte_clutch` | The rite in full voice. `zparty_witchfest_2099` is *already* the Sanctuary's signature proxy (4 placed here, 28 in drxBC_Finale) - the witchfest IS the ceremony. Thickening it with acolyte clutches makes the congregation a body of worshippers, and the name (`witchfest`) is amgoz1's own word for what happens on this walkway. |
| **3. The Clergy** | 4245-4310 | 7,019 sq u | 2 x `bw_priest_houndmaster`, 1 x `bw_priest_lone`, 1 x `hound_01_pack` | Between the congregation and the god stand the priests, and priests here come leashed to bloodhounds. Houndmasters are the only proxy in the cave that pairs a caster with beasts, which gives the middle of the walkway its own combat texture (chase + caster) instead of another melee wave. |
| **4. The Threshold** | 4186-4245 | 3,588 sq u | 2 x `abom_dancer_spear_mix`, 1 x `abom_ravager_lone`, 1 x `q_shaman_lone` | The door-wardens. The abominations are the cult's flesh-craft - what the Bloodborn *make*, not what they recruit - so they belong at the holy of holies, and they already guard the adjacent connectors. One `q_shaman_lone` as named gatekeeper gives the band a face and an audible cast, echoing the shaman already standing in `yet_another_fucking_connector`. |

**Totals: 14 new proxies, all from pools that already ship in this mod. Zero new creatures, zero new
records, zero new pools.** This satisfies the brief's "prefer what exists" and keeps the lane
map-only (no `arz`/`Text` coupling, so no `arz`+Text deploy pair is dragged in).

### 4.3 Placement rules (the invariant the implementation must carry)

1. Every placement lands on a **walkable navmesh cell** of `drxBC3` inside its own footprint
   (X[4186,4426] Z[2869,3109]) - never on pad outside it, never on the ocean tiles unless Will rules
   otherwise (Section 7).
2. **Minimum separation:** two "party" proxies (`spawnMax >= 6`) may never sit within **34 u** of each
   other on both axes; any other pair within 16 u. This is what holds the screen load down (Section 5).
3. Nothing within **20 u** of the arrival point `(4411,2,3089)` or the respawn shrine `(4388,2,3085)`
   - the player must not materialise inside a pack. (This is the b44 landing-clearance precedent.)
4. Band boundaries are advisory for flavour; rules 1-3 are hard and gated.

A concrete, on-mesh, rule-satisfying placement set was derived and is saved as
`plan_placements.json` in the session scratchpad; it is regenerable and the implementation should
re-derive rather than hardcode.

### 4.4 The ocean ring is deliberately NOT populated by this plan

42,199 sq u of it, zero proxies, and the honest answer is that **the right fix is a Will call, not
mine** - see WILL_DECISION-1. Sprinkling trash across a blood-sea to fill area is exactly what the
amgoz1 bar forbids, and the alternative (making it non-walkable) is a navmesh edit, which is the b89
crash class. The recommendation is in Section 7.

---

## 5. DENSITY SAFETY

Measured on the derived placement set, summing pool `spawnMax` over every proxy whose position falls
inside a **60 x 60 world-unit box** (a conservative one-screen footprint), taking the worst box:

| | worst-case simultaneous entities in one screen |
|---|---:|
| Sanctuary walkway **today** | **12** |
| Sanctuary walkway **after this plan** | **18** (at world `(4268,2987)`) |
| base-game cave/crypt/tomb comparators (n=147) | median **14**, p90 **70**, max **162** (`Crypt01.lvl`) |
| blood cave siblings today | `drxBC2` 72, `drxFirstRoom` 60, `drxBC_Finale` 60, `yet_another_fucking_connector` 39 |
| **b76 chumbi-freeze precedent** | **"well over 100"** live entities, *and unbounded* |

**The proposal's worst case (18) sits at the base-game median (14), below every blood-cave sibling
already shipping, at ~26% of the base-game p90, at 11% of the measured base-game maximum, and under
one fifth of the b76 freeze figure.**

The b76 precedent also matters **qualitatively**, and this plan respects it: b76 froze not because
of a raw count but because stacked summoners with **no `spawnObjectsTimeToLive`** refilled their pet
caps forever, so the fight never reached steady state. **Every proxy in this plan is a finite
`ProxyPool` with a hard `spawnMax` and no summon-refill loop.** Total walkway `spawnMax` goes 65 ->
140, which is a bounded, one-shot population, not a generator.

Residual honesty: 60x60 is my chosen screen proxy and TQ's real camera footprint was **not measured**
(that needs the game running, which this lane may not do). The comparison is internally consistent
because every figure in the table above was computed with the same box on the same map.

---

## 6. THE MINIMAP (secondary, as Will scoped it)

### It is NOT the same defect as b46. Same *symptom family*, different *root cause*.

b46 proved two independent mechanisms. Checking each against the Sanctuary:

**Not the b46 label defect (`0x17` REGION empty).** `drxBC3`'s REGION list is **populated** and
resolves: regions `[?78a5b1b2, ?e70ad7db, BCXwalkway]` -> the banner reads "Sanctuary of the
Bloodborn" correctly. Nothing to fix on the label for drxBC3.

**Not a missing minimap bitmap.** The `BITMAPS(0x19)` layout is `[u32 a][u32 count]` then `count` x
`(u32 off, u32 len)` into `DATA2(0x1a)` - proven by exact tiling, `8 + 2282*8 == 18,264` == the
section size. 2275 of 2282 levels carry a bitmap, and every Sanctuary-complex level is one of them:
`drxBC3` 2,764,844 B, `ocean_extension01..05` 2,764,844 B each, `ocean_extensionx*` 1,555,244 B. The
payloads are **not blank**: non-zero-byte fraction is **99.99%** for drxBC3 and **~100%** for the
ocean tiles. The imagery exists and is drawn.

**Not the b46 zone defect either (empty zone `dbr`).** b46's `crypt_floor1` had `dbr = ''`. Every
blood-cave level including drxBC3 carries a **valid** zone pointer:
`records/ingameui/teleportmap/zones/orient/easternsilkroad.dbr`.

### The actual mechanism: the cluster was grid-shifted off its own zone page

`tools/svaera_plus_portals.py` sets `GRID_SHIFT = {'xbloodcave': (7840, 0, 2030)}` - the cluster was
deliberately "relocated to empty map space, 3001.8u clearance". Measuring the corners of all 79
levels that share the `easternsilkroad` zone page in the shipped map:

```
NATIVE (non-bloodcave) corners:  X[-1412, 440]   Z[-1764, 2302]   n=48
BLOODCAVE + Random09A corners:   X[ 3426, 5979]  Z[ 2629, 3425]   n=31
GAP: the nearest blood-cave tile sits 2,986 units EAST of the farthest native tile
```

Per b46 section 1a, a level's minimap TGA is composited onto its zone's page **at the level's own grid
corner**. The blood cave now sits ~3,000 units outside the drawn extent of the Eastern Silk Road
page it points at, so its bitmaps land far off-page and the player marker floats in un-composited
space. **The very clearance that made the relocation safe for the world grid is what puts the cluster
off its minimap page** - the 2,986 u measured gap is the 3,001.8 u clearance the shift was chosen for.

**Fix direction (not implemented, deliberately - Will scoped this secondary):** the b46 section 7
recipe already names the pattern and SV's own precedent for it (`olympus_gom.dbr`, a dedicated zone
authored for one relocated area). The blood cave wants **its own zone record** -
`records/ingameui/teleportmap/zones/orient/bloodcave.dbr` with a `ZoneNameTag` and
`ArrowLocation/WindowLocation` chosen for the shifted coordinates - rather than borrowing
`easternsilkroad`. That is a **coupled `arz` + `Text` + `Levels` change** (new DB record, new text
tag, `LEVELS`-entry `dbr` override for ~31 levels), which is materially more expensive than the
population work and should not ride the same commit. Registered as BL-DEBT-b100-3.

---

## 7. OPEN QUESTIONS - WILL_DECISION

**WILL_DECISION-1 (the big one): what should the four ocean tiles BE?**
42,199 sq u of walkable, zero-enemy, Sanctuary-lit ground with a 107-unit-wide opening off the
walkway. Three options, and this is taste, not engineering:
- **(i) Populate them lightly as the blood sea** - 3-4 `demon_01_cluster` / `zparty_demons_big`
  placements total (both already ship in this cluster), so something *climbs out of the blood* and
  exploring the shelves is rewarded rather than barren. **My recommendation.** Cheap, on-theme, zero
  navmesh risk, and it keeps the walkway the main road rather than turning the sea into a second one.
- **(ii) Close them off** so the walkway reads as a walkway over a void. This means editing navmesh
  walkability, which is **the b89 crash class** (a malformed navmesh container). I recommend against
  it.
- **(iii) Leave them empty** as deliberate negative space before the finale.

**WILL_DECISION-2: is 18 worst-case-per-screen the feel he wants?** The plan lands the Sanctuary at
1,000 sq u/proxy - still 2.5x sparser than the base-game median (395), because a processional should
breathe. If he wants it to feel *besieged*, band 2 takes 2-4 more party proxies and worst-case rises
toward ~40, still well inside base-game p90 (70). One-line change to the band table.

**WILL_DECISION-3: the minimap fix, now or later?** It is a coupled `arz`+`Text`+`Levels` change
(Section 6), much bigger than the population lane. He called it "not a huge issue"; my recommendation
is to ship the population first and schedule the zone record separately.

**WILL_DECISION-4: `docs/amgoz1_design_voice.md` does not exist** (Section 4). Every content brief in
this repo cites it as the creative bar. Either it should be written down from R-15 and the exemplars,
or briefs should stop citing a file that was never authored.

---

## 8. RISKS

1. **Navmesh (the b89 class) - the top risk, and this plan's main mitigation is to not touch it.**
   The b89 crash came from a malformed navmesh container. This plan is `0x05`-only: it adds placed
   instances and **changes no `0x0b` byte**. Any implementation must gate on
   `verify_merged_bc_navmeshes` and assert every `0x0b` is byte-identical pre/post. If WILL_DECISION-1
   option (ii) is chosen, that mitigation evaporates and the risk becomes severe.
2. **Off-mesh placements.** A proxy on a non-walkable cell spawns monsters that cannot path. Mitigated
   by the section 4.3 rule-1 on-mesh gate, which must run against the FINAL merged map, not the
   source blob.
3. **Landing pileup.** Spawning the player into a pack at `(4411,2,3089)` is the b44 defect class.
   Mitigated by section 4.3 rule 3; needs an explicit gate assertion, not just a placement convention.
4. **`0x05` stride.** The section stride is version-dependent (72 for blob v0x11/v0x0f, 56 otherwise);
   `drxBC3` is v0x0e -> 56. Hardcoding 72 silently desyncs the walk - this is the documented BUILD46
   census bug. Any tooling must go through `contracts_map.blob_0x05_base`.
5. **Deploy couplings.** Levels+Quests ship together; arz+Text ship together. The population lane is
   map-only and needs no `arz`/`Text`, but `Quests.arc` must still be rebuilt and staged with it.
6. **Retirement protocol.** The 10 existing proxies are design of record (they are the upstream
   Sanctuary). This plan **adds only**; nothing is moved or deleted.
7. **Density estimate is model-based, not observed.** Section 5's figures are `spawnMax` sums, i.e.
   the worst case the data permits; actual concurrent load depends on player pathing and aggro. Only
   an in-game check can confirm feel, and no agent here may launch TQ.
8. **`build66-dev` was already taken** - the next free tag is `build67-dev`.

---

## 9. REPRODUCTION

All probes are regenerable and live in the session scratchpad (read-only; they mutate nothing):
`sanc_recon1.py` (region -> level binding), `sanc_recon2.py` (0x05 census by Class),
`sanc_coord.py` (the local-vs-world coordinate proof), `sanc_recon4.py` (occupancy + on-mesh gate),
`sanc_recon5.py` (0x17 region / env / zone table + navmesh neighbours), `sanc_recon6.py`
(proxy -> pool resolution, entry/exit), `sanc_recon7.py` (BITMAPS + base-game density comparators),
`sanc_minimap.py`, `sanc_seam.py` (seam walkability), `sanc_union.py` (deduplicated union),
`sanc_upstream.py` (cause-(d) diff vs SV 0.98i), `sanc_plan.py` (band placement + density proof).

Run with `PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 py <script>`.

**Status: DESIGN COMPLETE, IMPLEMENTATION NOT STARTED.** No deploy, no build, no CustomMaps write,
TQ and Steam never launched.
