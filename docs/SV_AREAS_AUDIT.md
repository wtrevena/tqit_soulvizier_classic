# SV-ONLY AREAS AUDIT - the remaining 16 non-blood-cave levels

> Complete, byte-level audit of every Soulvizier-only area still unfixed after the
> blood-cave (xBloodCave) cluster was solved. Produced 2026-07-05 against the deployed
> merged map. This is a decision-grade plan: what each area is, whether its navmesh can
> be generated, whether it is placed legally, how it was reached in classic SV, what is
> BROKEN in the merged map, and the exact ordered work to fix it. Companion:
> `docs/MODDING_PLAYBOOK.md` (mechanisms + recipes), `CLAUDE.md` (status board).
>
> Every claim below is backed by a parse of the shipped map (`local/Levels_merged.arc`
> == deployed `CustomMaps/.../Levels.arc`, both 683,966,024 B), the pristine upstream
> `sv_world01.map` (Soulvizier 0.98i), and the pristine `svaera_world01.map` (SVAERA
> base). Audit scripts: session scratchpad `sv_audit_01..18_*.py`.

---

## 0. Scope and method

The merged map carries **46 SV-only levels** (levels present in SV's index but not in
SVAERA's; the merge appends them after all SVAERA levels). Accounting:

- **30 = the xBloodCave cluster** - HANDLED (23 real generated navmeshes + 7 ocean
  stubs; walk-in entrance via the Random09A blob-swap cave mouth). Not re-audited here.
- **16 = the remaining SV-only areas** - THIS AUDIT. Enumerated from the merged LEVELS
  index (idx 2235-2245 + 2276-2280) by excluding `xbloodcave` paths.
- (idx 2281 = the harmless append-clone diagnostic; ignored.)

All 16 are `LVL v0x0e`, carry the **148-byte dead stub `0x0b`** (invisible wall), and
have `0x0a` already stripped in the merged map (the merge strips it). Their real `0x0a`
donor geometry survives in the pristine upstream SV world.

**Key structural fact that shapes everything below:** none of these 16 levels were
grid-shifted. They sit at their **SV-original grid positions**, which the audit proves
are **XZ-area-disjoint from every other level in the merged map** (0 overlaps at any
Y). So the DISJOINT placement rule is already satisfied for all 16 - **no GRID_SHIFT is
needed for any of them.** The blood-cave-style placement work does NOT recur here.

The problem is therefore two-dimensional, and it is the SAME two axes for every area:

1. **Navmesh** - all 16 carry the dead stub. 15 have real `0x0a` geometry from which our
   offline pipeline can generate a valid `0x0b`; 1 (coldtombs) has no walkable geometry.
2. **Entrance** - every one of these areas is an ISOLATED island (none edge-abuts a live
   AE level). In classic SV they were reached by quest teleports and by portal/warp
   records embedded in **shared surface levels**. The merge kept SVAERA's version of
   those shared levels, which **do not carry the SV portal/warp records** - so almost
   every entrance is BROKEN, the exact same failure class as the lost Random09A doorway.

---

## 1. Executive summary table

| Cluster | Levels | Merged idx | Navmesh feasible | Placement OK (disjoint) | Entrance state | Effort |
|---------|-------:|-----------|------------------|-------------------------|----------------|--------|
| **Secret Place** (rogue forest / widow letter) | 11 | 2235-2245 | YES (10 gen + behindthesp) | YES (0 overlaps; internal seams abut) | **QUEST-FRAGILE + BROKEN entry**: urder.qst teleports land ON-MESH and are self-contained, but the initial way IN (Rhodes `scrabledeggs_floor06` 0x06 portal -> behindthesp) was LOST when that shared level was AE-replaced | **L** |
| **Uber Dungeon** | 1 (crypt_floor1) | 2280 | YES | YES | **BROKEN-lost-in-shared-level**: entry was a `portal_olympianarena1` DynGridEntrance + 0x14 binding in `maze03` (AE-shared); both records absent in AE maze03. Return NPC is injected but nothing gets you in | **M** |
| **Boss Arena** | 1 (boss_arena) | 2279 | YES | YES | **BROKEN-lost-in-shared-level**: same `portal_olympianarena1` in `maze03` (shared with uber); bossarena.qst opens it but the DynGridEntrance record + binding are gone with AE maze03 | **M** |
| **Garden of Merchants** | 1 (gardenofmerchants) | 2276 | YES | YES | **BROKEN-lost-in-shared-level**: `portmebiznitch`/`imhere` warp records were in `startingfarmland06d` + `hiddenvalleyborder04` (both AE-shared); absent in AE versions. Destination shrine (teleportshrine_gom) survives inside GoM | **M** |
| **Sparta Crypt L2** | 1 (spartacryptlevel2) | 2278 | YES | YES | **BROKEN/UNKNOWN**: one-way 0x06 link sparta-L2 -> `spartaoptcata01` (AE-shared, KEPT), but AE spartaoptcata01 does NOT bind sparta-L2 back; no binder in SV world either | **S-M** |
| **Cold Tombs** | 1 (coldtombs) | 2277 | **NO** (no 0x0a; only 2 placed records) | YES | **NONE / vestigial**: near-empty stub (1 skeleton + 1 light), no navmesh, no links, no binder anywhere | **S (stub only)** |

Totals: **16 levels, 6 clusters. 15/16 navmesh-generatable, 16/16 placement-clean, 0/6
clusters have a working entrance in the shipped map.** Content (DB records) is 100%
resolved for all 16 (0 missing).

**Navmesh generation is proven, not just feasible:** a batch smoke-run of the offline
pipeline (`gen_rec02.generate` from the pristine SV `0x0a`) produced a valid non-empty
`0x0b` for all 15 feasible levels (coldtombs correctly skipped, no geometry). Walkable-cell
counts confirm real geometry in every area: boss_arena 1,630,729 cells (441 tiles),
gardenofmerchants 1,586,195 (441), crypt_floor1 454,487 (199), rogueencampment 493,175
(143), pillagedvillage 385,835, secretforest2 307,286, darkforestenter 294,719, tfinale
224,080, spartacryptlevel2 78,647, down to behindthesp 31,626 (11). **15/15 generated OK.**
So Wave 0 (navmesh generation) is a mechanical, de-risked extension of the blood-cave
pipeline.

**The headline for Will:** the navmesh side is easy and mechanical (extend the existing
`gen_bc_navmeshes.py` batch; all GUIDs already resolve, no remap, no shift). The hard,
decision-bearing part is the ENTRANCES: five of six areas lost their entry when a shared
surface level was replaced by SVAERA's version. Each needs either an engine-native
restoration (re-inject the lost portal/warp + 0x14 binding into the SVAERA shared level -
a blob patch, the Random09A lesson applied) or a quest-teleport re-point (fragile, per
the playbook warning). See Section 9 for the decision.

---

## 2. Cluster: SECRET PLACE (11 levels, idx 2235-2245)

The largest and highest-player-value cluster: a self-contained rogue-forest zone (the
"widow letter" / "murder boss" questline; SV's `xurder` "portaldudes" area, full of
Diablo-homage NPCs named `warriv`, `portal to act 1`).

### 2.1 Identity

| idx | file | GUID (first 8B) | corner (x,y,z) | footprint XZ | 0x0a size | placed-DBR |
|----:|------|-----------------|----------------|--------------|----------:|-----------:|
| 2235 | `xpack/levels/secret_place/behindthesp.lvl` | 82535f98c4441d6c | (-2199,0,-6182) | X[-2199,-2079] Z[-6182,-6062] | 23,360 | 8 |
| 2236 | `secret_place/darkforestenter.lvl` | 1397c8e754491051 | (-2420,0,-5820) | X[-2420,-2292] Z[-5820,-5692] | 879,459 | 25 |
| 2237 | `secret_place/woodscorner.lvl` | a777ad7fd94366de | (-2548,0,-5820) | X[-2548,-2420] Z[-5820,-5692] | 772,224 | 37 |
| 2238 | `secret_place/secretforest2.lvl` | bec899edbb4fc4af | (-2548,0,-5948) | X[-2548,-2420] Z[-5948,-5820] | 1,005,630 | 66 |
| 2239 | `secret_place/pillagedvillage.lvl` | 74508bdf3c40bc83 | (-2676,0,-5948) | X[-2676,-2548] Z[-5948,-5820] | 781,151 | 97 |
| 2240 | `secret_place/forestobsidiantransition.lvl` | 83436915a541dcfa | (-2839,0,-5928) | X[-2839,-2753] Z[-5928,-5848] | 98,322 | 33 |
| 2241 | `secret_place/rogueencampment.lvl` | f31e50a12e45ca1d | (-3216,0,-5547) | X[-3216,-3088] Z[-5547,-5419] | 648,366 | 89 |
| 2242 | `secret_place/rogue encampment forest entrance.lvl` | f6ff99150049d744 | (-3088,0,-5547) | X[-3088,-3024] Z[-5547,-5419] | 17,774 | 2 |
| 2243 | `secret_place/rogueencampmentforestfiller.lvl` | 9cdd35688546c246 | (-3216,2,-5419) | X[-3216,-3088] Z[-5419,-5355] | 15,238 | 1 |
| 2244 | `secret_place/tfinale.lvl` | 16559b5f31441fd1 | (-3623,0,-5635) | X[-3623,-3383] Z[-5635,-5395] | 616,065 | 28 |
| 2245 | `secret_place/murderbossroom.lvl` | 2817751af2482850 | (-3592,0,-5955) | X[-3592,-3472] Z[-5955,-5811] | 126,889 | 12 |

All v0x0e, all own-GUID resolves in the merged world, 100% of placed records resolve
(base+mod DB). The zone occupies its own grid region around X[-2000..-3600] Z[-5300..
-6200], fully disjoint from the AE world.

### 2.2 Navmesh state + feasibility

All 11 carry the 148-byte dead stub. All 11 have real `0x0a` geometry upstream (sizes
above). **Generation is proven**: the audit generated valid `0x0b` sections for
darkforestenter / rogueencampment / tfinale and confirmed the urder teleport coords land
on walkable cells (Section 2.4). The internal cluster has three connected sub-groups that
edge-abut (grid-seam walking, SCALE=2, shared_len 128 = a full 64-tile edge):

- **Forest chain**: `darkforestenter <-x-> woodscorner <-z-> secretforest2 <-x-> pillagedvillage`
- **Rogue camp**: `rogueencampment <-x-> "rogue encampment forest entrance"`, `rogueencampment <-z-> rogueencampmentforestfiller`
- **Portal-linked (not grid-abut)**: behindthesp (entry lobby), forestobsidiantransition,
  tfinale, murderbossroom are reached by quest teleport / 0x06 portal links, not seams:
  - `forestobsidiantransition -> pillagedvillage` (0x06 link, resolves)
  - `tfinale <-> murderbossroom` (mutual 0x06 links, resolve)

**Neighbor-GUID map for generation (all resolve in merged - no remap needed):**

```
behindthesp                 own 82535f98  neighbors: []            (portal room)
darkforestenter             own 1397c8e7  neighbors: [woodscorner]
woodscorner                 own a777ad7f  neighbors: [darkforestenter, secretforest2]
secretforest2               own bec899ed  neighbors: [woodscorner, pillagedvillage]
pillagedvillage             own 74508bdf  neighbors: [secretforest2]
forestobsidiantransition    own 83436915  neighbors: []
rogueencampment             own f31e50a1  neighbors: [rogue-enc-forest-entrance, rogueencampmentfiller]
rogue enc forest entrance   own f6ff9915  neighbors: [rogueencampment]
rogueencampmentfiller       own 9cdd3568  neighbors: [rogueencampment]
tfinale                     own 16559b5f  neighbors: []
murderbossroom              own 2817751a  neighbors: []
```

Each level's `0x0b` GUID list = own GUID first + its abutting neighbor GUIDs. Because ALL
are SV-only and kept their SV GUIDs, and their neighbors are also kept, every GUID
already resolves - unlike the blood cave, which needed SV->AE remaps. This is the
simplest possible generation case.

### 2.3 Entrance chain - QUEST-FRAGILE internal, BROKEN entry

`urder.qst` (ported, present in `Quests.arc`) is the **secret-place questline**, not the
uber dungeon (despite the memory note). It contains 3 `Action_BoatDialog` teleports:

| coord (raw world) | lands in | driving NPC |
|-------------------|----------|-------------|
| (-2317,0,-5765) | darkforestenter (ENTRY) | `records/drxmap/xurder/portaldudes/portal to act 1.dbr` |
| (-3103,0,-5457) | rogueencampment | `.../portal to hallway.dbr` |
| (-3419,2,-5443) | tfinale | `.../warriv.dbr` |

All three teleport NPCs + the trigger creatures (zilla01-03) are placed in **KEPT SV-only
target levels** (behindthesp, forestobsidiantransition, rogueencampment, tfinale). So the
internal teleport chain is fully self-contained and depends on NO shared level.

**BUT: the way the player first ENTERS the cluster is BROKEN.** `portal to act 1` +
`trg_portal_to_act_1` live in **behindthesp**, whose only inbound link in SV is a `0x06`
portal from `xpack/levels/area01_rhodes/undergrounds/scrabledeggs_floor06.lvl`
(behindthesp GUID at 0x06 offset 891). scrabledeggs_floor06 is an **AE-SHARED** Rhodes
underground level; the merge kept SVAERA's version, and **the AE version does NOT bind
behindthesp** (0x14=absent, 0x06=absent - byte-confirmed). behindthesp is an Egypt-
Rhakotis-library-dressed side room (its 8 records: horus statue, urn, thoth-baboon
statue, lights, the portal NPC+trigger). It sits at X[-2199,-2079] ~123u from
scrabledeggs X[-1956,-1824] - so the SV connection was a PORTAL, not a grid seam.

**Classification: QUEST-FRAGILE (internal, works once entered) + BROKEN-lost-in-shared-
level (the entry portal into behindthesp).**

### 2.4 On-mesh verification (byte-proven)

Generating the `0x0b` from the pristine SV `0x0a` and mapping each urder coord to a
navmesh cell (origin = center - dims, +16 pad):

```
darkforestenter  coord (-2317,0,-5765) -> cell (595,355)  ON-MESH  (294,719 walkable cells)
rogueencampment  coord (-3103,0,-5457) -> cell (645,530)  ON-MESH  (493,175 walkable cells)
tfinale          coord (-3419,2,-5443) -> cell (1100,1040) ON-MESH  (224,080 walkable cells)
```

So once navmeshes are generated, the urder teleport chain is walkable end-to-end. The
teleport coords are safe (they were authored for these exact SV-original positions, which
the merge preserves unshifted).

### 2.5 Content sanity

All placed records resolve (behindthesp 8/8, darkforestenter 25/25, ... pillagedvillage
97/97, etc; 0 missing across the cluster). Art is DRX + base scenery, all present.

---

## 3. Cluster: UBER DUNGEON (crypt_floor1, idx 2280)

### 3.1 Identity
`levels/world/uberdungeon/crypt_floor1.lvl`, GUID `dbc245c358434e0b...`, corner
(-2578,0,-2682), footprint X[-2578,-2258] Z[-2682,-2362], v0x0e, `0x0a` size 782,439,
32 placed records (Athens-catacomb-set dungeon). Disjoint from all levels.

### 3.2 Navmesh
Dead stub now; real `0x0a` upstream -> generatable. own GUID resolves; it has no
grid-abut neighbor (a self-contained interior), so its `0x0b` GUID list = just its own
GUID (plus optionally the surface level it returns to, once that is decided).

### 3.3 Entrance - BROKEN-lost-in-shared-level
- crypt_floor1's `0x05` places `portal_olympianarena2.dbr` (the arena/dungeon portal) and
  `portal_uberdungeon_return.dbr` (the return NPC, injected by `INJECT_SPECS`).
- The ENTRY was a **DynGridEntrance** in `maze03` (Knossos underground, an AE-SHARED
  level): SV maze03 places `records/quests/portal_olympianarena1.dbr` AND carries a 48-byte
  `0x14` record #11 whose payload holds crypt_floor1's GUID at offset 32
  (`58941143...` UniqueId @0, `6e513e90...` UniqueId @16, `dbc245c3...` = crypt_floor1 @32).
- **AE maze03 has ONLY the crypt-creature proxies; it does NOT place `portal_olympianarena1`
  and does NOT carry the crypt_floor1 binding** (byte-confirmed). So the uber-dungeon
  entrance was LOST when maze03 was replaced by SVAERA's version.
- `portal_uberdungeon_entrance.dbr` is placed NOWHERE in the merged map. The return exists
  but nothing gets the player IN.

**Classification: BROKEN-lost-in-shared-level.** Note the uber dungeon and boss arena
SHARE the maze03 `portal_olympianarena1` entrance record - restoring maze03 fixes both.

### 3.4 Content: 32/32 records resolve.

---

## 4. Cluster: BOSS ARENA (boss_arena, idx 2279)

### 4.1 Identity
`levels/world/bossarena/boss_arena.lvl`, GUID `6112638db5442534...`, corner (-561,0,-3642),
footprint X[-561,-305] Z[-3642,-3386], v0x0e, `0x0a` size 76,641, 12 placed records
(a 256x256 arena). Disjoint from all levels.

### 4.2 Navmesh
Dead stub; real `0x0a` upstream -> generatable. Self-contained (no grid neighbor); GUID
list = own GUID.

### 4.3 Entrance - BROKEN-lost-in-shared-level
`bossarena.qst` (ported) is a clean quest: on level load it runs `Action_ShowNpc` +
`Action_OpenDynGridEntrance` + `Action_UnlockFixedItem` on
`records/quests/portal_olympianarena1.dbr`, with an `Condition_EnterVolume` on
`portal_olympianarena.dbr`. **The DynGridEntrance it opens (`portal_olympianarena1`) is
the SAME record that lived in maze03 and was lost with the AE replacement.** The quest
fires but there is no grid entrance to open, and no `0x14` binding to boss_arena survives
anywhere in the merged map (byte-confirmed: 0 binders).

**Classification: BROKEN-lost-in-shared-level (shares the maze03 loss with uber dungeon).**

### 4.4 Content: 12/12 records resolve.

---

## 5. Cluster: GARDEN OF MERCHANTS (gardenofmerchants, idx 2276)

### 5.1 Identity
`levels/world/olympus/gardenofmerchants.lvl`, GUID `15f9d3d7214d56d4...`, corner
(1043,0,-4074), footprint X[1043,1299] Z[-4074,-3818], v0x0e, `0x0a` size 420,174,
**172 placed records** (the richest area - a full merchant hub). Disjoint from all levels.

### 5.2 Navmesh
Dead stub; real `0x0a` upstream -> generatable. Self-contained isolated hub (no grid
neighbor); GUID list = own GUID.

### 5.3 Entrance - BROKEN-lost-in-shared-level
This is the classic SV "portmebiznitch / imhere" warp hub. In SV:
- `portmebiznitch.dbr` + `imhere.dbr` (the warp trigger + destination marker) were placed
  in `startingfarmland06d.lvl` (Greece) AND `hiddenvalleyborder04.lvl` (Orient) - **both
  AE-SHARED**.
- **Both AE versions lack these records** (byte-confirmed: SV=present, AE=absent for
  portmebiznitch + imhere in startingfarmland06d, and portmebiznitch in
  hiddenvalleyborder04). So the entry warp is LOST.
- The DESTINATION-side `teleportshrine_gom.dbr` (StrategicMovementTeleportShrine) survives
  inside gardenofmerchants.lvl itself (for the trip back), but the player can never reach
  it because the entry warp is gone.

**Classification: BROKEN-lost-in-shared-level (the widest loss - two shared levels).**

### 5.4 Content: 172/172 records resolve.

---

## 6. Cluster: SPARTA CRYPT L2 (spartacryptlevel2, idx 2278)

### 6.1 Identity
`levels/world/greece/minidungeons/spartacryptlevel2.lvl`, GUID `797c78594040cba4...`,
corner (-5644,0,-1451), footprint X[-5644,-5564] Z[-1451,-1371], v0x0e, `0x0a` size
134,234, 27 placed records. Disjoint from all levels.

### 6.2 Navmesh
Dead stub; real `0x0a` upstream -> generatable. Self-contained; GUID list = own GUID
(its 0x06 link to spartaoptcata01 is one-way and does not need to be in the GUID list).

### 6.3 Entrance - BROKEN / UNKNOWN
- sparta-L2's `0x06` links TO `spartaoptcata01.lvl` (`levels/world/greece/minidungeons/`,
  AE-SHARED, KEPT in the merge). But the AE spartaoptcata01 does **not** bind sparta-L2
  back (0x14=absent, 0x06=absent - byte-confirmed).
- In the pristine SV world, **NOTHING binds sparta-L2** either (no 0x14, no 0x06 from any
  level). Its only relationship is the one-way outbound link.
- So sparta-L2 was likely an unreachable/cut level in SV, or reached by a stair the AE
  spartaoptcata01 lacks. It DOES have real content (27 records) + geometry.

**Classification: BROKEN / UNKNOWN.** Lowest confidence; needs a decision on whether it is
worth wiring at all (Section 9). It is a 40x40-tile mini-crypt, minor value.

### 6.4 Content: 27/27 records resolve.

---

## 7. Cluster: COLD TOMBS (coldtombs, idx 2277)

### 7.1 Identity
`levels/world/egypt/minidungeons/coldtombs.lvl`, GUID `1e49b21c2545421b...`, corner
(-4283,-5,3123), footprint X[-4283,-3771] Z[3123,3635] (a large 256x256 declared box),
v0x0e, **NO `0x0a`**, **only 2 placed records** (`am_minion_01.dbr` skeleton +
`5mlight_dyn_orange.dbr` light). Disjoint from all levels.

### 7.2 Navmesh - NOT feasible (and not needed)
No `0x0a` walkable geometry exists upstream. This level is effectively **empty/vestigial**
- a near-blank declared box with one monster and one light, no terrain mesh, no links, no
  binder anywhere in SV or the merged map. It is the direct analogue of the 7 ocean-scenery
  levels in the blood-cave cluster: **keep the 148-byte stub** (build stays green, no
  invisible-wall problem because there is nothing to walk into).

**Classification: NONE / vestigial.** No entrance ever existed. Leave stubbed.

### 7.3 Content: 2/2 records resolve.

---

## 8. The systematic fix program (waves)

Ordered easiest-first, with each area's work mapped to playbook recipes. Navmesh work is
mechanical and low-risk; entrance work carries the decisions.

### WAVE 0 - Navmesh generation for the 15 feasible levels (LOW risk, do first)

This is a pure extension of the proven blood-cave pipeline and unblocks walkability for
every area at once. Because all own + neighbor GUIDs already resolve in the merged world,
there is **no GUID remap and no GRID_SHIFT** - the simplest donor case in the project.

1. Extend `tools/gen_bc_navmeshes.py`'s batch to include the 15 levels (all except
   coldtombs). For each, own-GUID = its existing SV GUID (already the merged GUID; NO
   `OWN_GUID_OVERRIDE` needed), neighbor GUIDs = the abutting-cluster neighbors from the
   map in Section 2.2 (only the secret-place chain levels have neighbors; the 5 isolated
   interiors list just their own GUID). No `GRID_SHIFT` entry (these levels are unshifted;
   the container center = their real grid corner + half-extents, computed directly).
2. Run `py tools/gen_bc_navmeshes.py` (writes `local/editor_normalized/<basename>.0b.bin`).
   The driver self-verifies round-trip identity, 3 sets, resolvable GUIDs.
3. In `tools/svaera_plus_portals.py` the existing tier-1 injector already picks up any
   `<basename>.0b.bin` in the donor dir via `find_pre_positioned_donor` +
   `inject_rec02_into_blob(pre_positioned=True)` - so once the donors exist, the merge
   injects them VERBATIM and strips `0x0a`. No new inject code is required.
4. Extend `tools/verify_merged_bc_navmeshes.py`'s level list to cover the 15 so the hard
   gate proves each `0x0b` landed at donor size with `0x0a` stripped. Keep coldtombs on
   the stub list (like the 7 ocean levels).
5. Coldtombs: no action (keep the 148-byte stub by design).

Effort: **M** (mostly data entry of the 15 basenames + neighbor GUIDs; the machinery is
built). Dependency: none. This wave makes every area WALKABLE the moment its entrance is
reached, and makes all the quest-teleport landings on-mesh (verified for secret place).

### WAVE 1 - Secret Place entry restoration + questline (HIGH value, MEDIUM-HIGH effort)

After Wave 0, the internal urder.qst teleport chain works (coords proven on-mesh). Two
gaps remain:

1. **Restore the entry portal into behindthesp** (the lost `scrabledeggs_floor06 -> behindthesp`
   0x06 link). Options, in playbook-preferred order:
   - **(preferred, engine-native) Re-inject the SV portal binding into the SVAERA
     `scrabledeggs_floor06`** blob: add behindthesp's GUID back as the destination via the
     same blob-patch technique used for Random09A (patch the shared level's 0x06/0x14 so
     the portal resolves). This is a **Will decision** (blob-patching a shared AE level).
   - **(alternative, quest) Add an `Action_BoatDialog` to a small custom quest** that
     teleports the player into behindthesp (or straight to darkforestenter) from a trigger
     placed in a live Rhodes/Egypt level. Fragile per the playbook; avoid for a persistent
     area unless the blob-patch proves hard.
2. **widowletter.qst** (ported): it is the in-zone content questline (widow_ling NPC,
   finalletter item, trg_foundzhidan volume - all placed in KEPT SV-only levels
   drxmap/quest/*). It needs no map rebuild; confirm it fires once the zone is reachable.

Effort: **L** (the entry-restoration decision + implementation is the cost; the questline
itself is already ported). Dependency: Wave 0.

### WAVE 2 - Uber Dungeon + Boss Arena (shared fix, MEDIUM effort)

Both lost the SAME `portal_olympianarena1` DynGridEntrance in `maze03`. Fix once:

1. **Restore `portal_olympianarena1.dbr` + its 0x14 binding into the SVAERA `maze03`
   blob** (Knossos underground). Re-inject the SV record into maze03's `0x05` at the SV
   local position, and APPEND the 48-byte `0x14` binding record (UniqueIds @0/@16 +
   crypt_floor1 GUID @32) so the DynGridEntrance resolves. This is the **Will decision**
   (blob-patch a shared AE level). `bossarena.qst`'s `Action_OpenDynGridEntrance` +
   `portal_olympianarena.dbr` volume then have a real entrance to open.
2. Confirm boss_arena's own binding: boss_arena is entered by opening the arena portal;
   verify the arena's destination GUID is bound (may need a second 0x14 payload for the
   boss_arena GUID depending on how SV chained maze03 -> crypt_floor1 -> boss_arena;
   inspect maze03's SV 0x14 set + crypt_floor1's `portal_olympianarena2` chain during
   implementation).
3. Alternative if blob-patching maze03 is undesired: a quest `Action_BoatDialog` to an
   on-mesh cell in crypt_floor1 (derive the target from the generated `0x0b` origin;
   verify area!=0), then walk to boss_arena via the in-dungeon portal. Fragile.

Effort: **M**. Dependency: Wave 0 (crypt_floor1 + boss_arena navmeshes).

### WAVE 3 - Garden of Merchants (MEDIUM effort, widest shared-level touch)

1. **Restore the `portmebiznitch`/`imhere` warp** into the SVAERA `startingfarmland06d`
   (and/or `hiddenvalleyborder04`) blob: re-inject the SV warp trigger record(s) into the
   shared level's `0x05` at the SV local position, wired to teleport to GoM's shrine (the
   `teleportshrine_gom` destination inside GoM survives). This is the **Will decision**
   (blob-patch one or two shared AE levels). Prefer a single level (startingfarmland06d)
   to minimize the shared-level footprint.
2. Alternative: quest `Action_BoatDialog` / `StrategicMovementTeleportShrine` to an
   on-mesh GoM cell.

Effort: **M**. Dependency: Wave 0 (GoM navmesh).

### WAVE 4 - Sparta Crypt L2 (LOW value; decide whether to ship)

1. Determine intended entry (inspect the SV spartaoptcata01 blob vs AE for a lost stair/
   portal; the audit shows no binder existed in SV, so this may have been unreachable).
2. If shipping: either restore a binding in `spartaoptcata01` (blob-patch, Will decision)
   or add a quest teleport; then it is walkable (Wave 0 navmesh).
3. **Recommended: defer or drop** unless Will wants completeness - it is a minor 40x40
   mini-crypt with an ambiguous original entrance.

Effort: **S-M**. Dependency: Wave 0.

### WAVE 5 - Cold Tombs

No work. Keep the 148-byte stub (vestigial, no geometry, no entrance ever). Document as
intentionally-stubbed alongside the 7 ocean levels.

---

## 9. Decisions needed from Will

The navmesh work (Wave 0) needs no decision - it is mechanical and safe, and should
proceed. The entrance restorations all hinge on one architectural choice, because FIVE of
six areas lost their entry inside a **shared SVAERA surface level**:

1. **Entrance-restoration mechanism (the core decision).** For each lost entrance we can
   either:
   - **(A) Engine-native: blob-patch the SVAERA shared level** to re-inject the SV portal/
     warp record + its `0x14`/`0x06` binding (the Random09A lesson, generalized). This is
     robust and quest-free, matches how the blood-cave walk-in was ultimately fixed, and is
     the playbook's preferred path. Cost: we modify a handful of shared AE level blobs
     (maze03 for uber+boss; startingfarmland06d [+ hiddenvalleyborder04] for GoM;
     scrabledeggs_floor06 for secret place; optionally spartaoptcata01). Each is a
     surgical `0x05` append + a `0x14`/`0x06` binding patch - the same class of edit as the
     Random09A swap, and reversible.
   - **(B) Quest teleports** (`Action_BoatDialog` to on-mesh cells). Cheaper to build,
     needs no shared-level edit, but FRAGILE - the playbook documents that quest-driven
     entrances broke twice in this project (state bakes into saves; the 200x OnLevelLoad
     idiom). Not recommended for persistent-area entry.

   **Recommendation: (A) for all except possibly Sparta L2.** It is more work up front but
   matches the proven blood-cave outcome and avoids the save-state fragility.

2. **Scope of shipping.** Confirm which areas ship. Secret Place (11 levels, a full
   questline), Uber Dungeon, Boss Arena, and Garden of Merchants are high-value and worth
   the entrance work. **Sparta Crypt L2** (minor, ambiguous original entrance) and **Cold
   Tombs** (vestigial stub) can be deferred/dropped without player-visible loss. Decide
   whether to spend Wave 4 effort on Sparta L2.

3. **Shared-level blob patching approval.** Option (A) modifies SVAERA shared level blobs
   (maze03, startingfarmland06d, scrabledeggs_floor06, ...). This is the same technique as
   the accepted Random09A swap, but touches more shared levels. Confirm this is acceptable
   (it is Steam-clean - map data only, no DLL). Each patch keeps the AE GUID in the LEVELS
   index so no downstream GUID resolution breaks.

---

## 10. Appendix: what static analysis CANNOT confirm

Consistent with the blood-cave caveat, three things need an in-game walk test after
implementation:

- Grid-seam hand-off inside the secret-place forest chain (the generated navmeshes'
  walkable bands must overlap across each shared edge; the geometry suggests they do,
  but the engine hand-off is only provable in-game).
- That each restored DynGridEntrance / warp actually streams the player across (the
  `0x14` binding math is byte-verified against the Silk Road reference, but the transition
  is engine-side).
- End-to-end walkability of the larger interiors (crypt_floor1, GoM) after generation -
  the same "click-projection on flat spots" caveat as BC_initialpathway. Fallbacks are the
  playbook's navmesh area-flag / erosion levers.

Audit artifacts (session scratchpad, regenerable): `sv_audit_01_enum.py` (enumeration),
`_02_feasibility.py` (0x0a feasibility), `_03_placement.py` (disjoint scan),
`_04_adjacency.py` (edge graph), `_05..07` (SV-layout + link + entrance scans),
`_08..12` (quest teleports + on-mesh proof), `_13_content.py` (DB resolution),
`_14..18` (uber/boss/GoM/sparta/coldtombs + secret-place entry resolution).
