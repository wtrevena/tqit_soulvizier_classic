# SPARTA CRYPT L2 ENTRANCE (invented) + BUILD23 SCREENSHOT CORRECTIONS - implementer log

> Max-effort implementer wave (Will's task #24), built ON build24 (commit `dac8926`,
> deployed `local/Levels_merged.arc` = 688,687,606 B). Reuses the proven A1 maze03 portal
> machinery (SV 0x14 GridEntranceDynamic binding [mouth+exit+dest], v0x0f/v11 inject paths,
> on-mesh verification via `ctx()`/`on_mesh()` against the merged `0x0b`). Written continuously.
>
> Baseline snapshot for collateral diffs: `local/Levels_merged.build24-baseline.arc` (byte-copy
> of the deployed build24, md5 `12664ac8...`). Python:
> `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe` (`PYTHONIOENCODING=utf-8`).
>
> Companion docs: `ENTRANCES_POLISH_LOG.md` (the A1 machinery I reuse), `SV_AREAS_CAMPAIGN_LOG.md`
> (Wave 5 Sparta DROP analysis - the reason this entrance is INVENTED, not restored),
> `DROPPED_CONTENT_AUDIT.md` (SV occult-scene exemplars for B).

---

## SCOPE (from the brief)

- **WORKSTREAM A - INVENT a Sparta Crypt L2 entrance.** SpartaCryptLevel2 never had one in SV
  (Wave 5 proved: zero inbound binders in pristine SV either). Place an ALWAYS-OPEN GridEntrance
  mouth pair inside the base-game Athens-battlefield crypt dungeon, 0x14-bound to
  SpartaCryptLevel2's MERGED GUID, landing on-mesh, + a reciprocal return portal inside
  SpartaCryptLevel2 back to the crypt. Mirror A1 exactly.
- **WORKSTREAM B - corrections** (Will's build23 screenshots):
  - B1 WAGON OVERLAP: the Hades wagon at HVBorder04 sits ON TOP of the occultist merchant.
  - B2 ONE CARAVAN SCENE: compose wagon + horse + caravan driver together, non-overlapping.
  - B3 PURPLE AESTHETICS VERIFY: does the restored scene include SV's purple occultist visuals?
  - B4 FINAL LAYOUT GATE: fountain + caravan + sprites + occultist + wagon all non-overlapping.

CONSTRAINTS: map tooling only. No DB scripts, no donors, no Quests.arc. No deploy/commit/Workshop.
Skip-not-break per item. Leave `fix_mc_output.py`/`hybrid_merge.py` alone.

---

## RECON PHASE - measured facts (build24 merged map + SV upstream)

Recon script (read-only): `tools/debug/recon_sparta_and_corrections.py`.

### A - the Athens crypt host + SpartaCryptLevel2 + the native GridEntrance exemplar

**Athens underground crypt chain (base-game, all have real Editor-baked navmeshes):**
| Level | ver | corner | GUID | 0x05 | mesh (largest comp) |
|-------|-----|--------|------|-----:|---------------------|
| `Athens/Underground/Entrance01.lvl` | v0e | (-6232,44,-3166) | `e2937b95ff4dd29a4db726b16c0ecb1f` | 30 | 18,747 (single comp) |
| `Athens/Underground/CataCube02_Floor0.lvl` | v0e | (-6274,0,-3798) | `07c17eebf14af0f7b7e7d98b6a62ff5d` | 118 | 79,418 |
| `Athens/Underground/CataCube02_Floor4.lvl` | v0e | (-6595,0,-3520) | `c66669372a4fa6a1a44248817ef0d608` | 276 | 209,008 |
| `Athens/Underground/CataCube02_Floor5.lvl` | v0f | (-6593,0,-3882) | `cbaa27d2574e8bf054b0b4b3328cb9c7` | 249 | 208,654 |
| `Athens/Underground/CataCube02_Floor06.lvl` | v0e | (-6288,0,-3500) | `f92ce7acc449c58b0b2718856e611f3e` | 125 | 101,509 |
| `Athens/Underground/CataCube02_FloorLast.lvl` | v0f | (-6612,0,-3218) | `817574a8674093619ebf6581db63274c` | 190 | 123,720 |

This IS the Athens battlefields crypt (the "Athens Catacombs" dungeon reached before/around
Athens city). `CataCube02_FloorLast` = the deepest chamber (the natural "deepest crypt-like"
spot the brief asks for). All have baked navmeshes -> on-mesh landing is verifiable.

**SpartaCryptLevel2 (the donor interior, real navmesh since build23):** at
`Levels/World/Greece/MiniDungeons/SpartaCryptLevel2.lvl` (recon ctx() path-guess missed it -
it is under MiniDungeons/, not sparta/; re-probing next). Wave-1 facts: 1570 verts / 2746 tris /
39 obstacles, single-GUID isolated island, corner == SV corner (no grid shift), donor 75,506 B
injected + gated (own-floor 95.7%, main comp 100% 2 comps). MERGED GUID + walkable centroid =
being measured in step A-recon-2.

**NATIVE GridEntrance exemplar (HV01 cave mouth -> Random09A), the pairing template:**
- HV01 inst[30] = `SilkRdDngEntrance_C01_Ext.dbr` (a GridEntrance) at world (-120,-102,2200).
- Its **0x14[idx=30] is 60 bytes**: `[12-byte prefix (2,0,1)] + [48-byte binding]`:
  - prefix = `02000000 00000000 01000000` (the SAME 12-byte (2,0,1) NpcCaravan-style prefix)
  - mouth_uid = `cfb4da3a694905fc2d76e299157378 82`  (bytes [12:28])
  - exit_uid  = `89328d35e24a56be5527218310 35ed62`  (bytes [28:44])
  - dest_guid = `d840e7ae4a42c504453f13a47940bc55`   (bytes [44:60])
- Random09A merged GUID = `d840e7ae4a42c504453f13a47940bc55` EXACTLY == the dest_guid.

> KEY FORMAT NOTE: the native GridEntrance 0x14 = a 60-byte record = 12-byte header + 48-byte
> (mouth+exit+dest). A1's maze03 injected a bare 48-byte payload (GridEntranceDynamic, quest-
> opened). For an ALWAYS-OPEN static GridEntrance mouth pair (the blood-cave/HV01 pattern Will
> wants), the faithful shape is the 60-byte native record. This is the load-bearing format
> decision for Workstream A - verifying against both the maze03 injected record and the native
> HV01 record before authoring.

### A - MECHANISM DECISION (the load-bearing finding that shapes Workstream A)

I surveyed EVERY cross-level portal in the merged map (`tools/debug/survey_gridentrance.py`,
`recon_gridpair.py`) to settle which mechanism is BUILDABLE in map-tooling-only scope:

**Two distinct cross-level portal mechanisms exist in TQAE:**

1. **Static `GridEntrance` (the blood-cave / HV01 cave-mouth pattern) = 0x14 + 0x06 PAIR.**
   - Source level: a `GridEntrance`-class record instance + a **60-byte 0x14** binding
     `(2,0,1) prefix + mouth_uid + exit_uid + dest_guid`.
   - Destination level: a reciprocal **0x06 GridSystem portal descriptor** carrying
     `exit_uid + mouth_uid + dest_guid` (byte-decoded on Random09A: the 0x06 tail is
     `...02000000 40000000 01000000 <exit_uid> <mouth_uid> <src_guid> 08000000 00000000 02000000`).
   - PROOF this is a PAIR, not 0x14-alone: of 295 resolvable static-GridEntrance 60-byte
     bindings in the map, **294 have the reciprocal 0x06 back-ref on the destination; only 1
     lacks it.** So a static GridEntrance needs BOTH sides -> it needs 0x06 GridSystem authoring
     (increment the descriptor count + splice a descriptor into an EXISTING 0x06 that already
     holds other descriptors). That 0x06 GridSystem-pair authoring is the exact tooling the
     SV-areas campaign proved is NOT built in this project (only the 0x14 append was newly built,
     for A1). => **STATIC GRIDENTRANCE IS NOT BUILDABLE in scope** (the brief's assumed
     "always-open GridEntrance mouth" mechanism has a 0x06 dependency that recon surfaced).

2. **`GridEntranceDynamic` + `GridExitOneWay` (the A1 maze03 pattern) = PURE 0x14, NO 0x06.**
   - Source: `GridEntranceDynamic` instance + a **48-byte 0x14** `mouth+exit+dest`.
   - Landing: `GridExitOneWay` instance + a **48-byte 0x14** `mouth(==src.exit)+zeros`.
   - PROOF it is pure-0x14: A1's crypt_floor1 landing has a 0x06 section (19,733 B) that does
     NOT reference maze03's GUID (byte-checked). The teleport fires entirely off the 48-byte
     0x14 bindings. This is the ONLY newly-built, gate-proven cross-level append in the project.
   - The catch: `GridEntranceDynamic` (visibilityMode=NeverVisible) is OPENED by a quest
     `Action_OpenDynGridEntrance(dynGridEntranceName=<record>)`. I cannot add a Quests.arc entry.

**THE UNLOCK (no Quests.arc change needed):** `bossarena.qst` (already in the deployed
Quests.arc since build22) fires **`Condition_OnLevelLoad`** (LEVEL-AGNOSTIC - no bound level)
-> `Action_ShowNpc` + **`Action_OpenDynGridEntrance(records/quests/portal_olympianarena1.dbr)`**
+ `Action_UnlockFixedItem`, ALL keyed BY RECORD NAME. So on EVERY level load the engine opens
every instance of `portal_olympianarena1.dbr` in the loaded level, and **each instance
teleports via ITS OWN 48-byte 0x14 binding.** This is EXACTLY how A1 works. Therefore:

> **WORKSTREAM A DESIGN (mirrors A1 exactly, buildable, no Quests.arc change):** place a SECOND
> instance of `portal_olympianarena1.dbr` (GridEntranceDynamic) in the Athens crypt host with a
> 48-byte 0x14 binding to SpartaCryptLevel2 (mouth_A + exit_A + dest=SpartaCryptLevel2 GUID), and
> a matching `portal_olympianarena2.dbr` (GridExitOneWay) landing inside SpartaCryptLevel2 with a
> 48-byte 0x14 (mouth==exit_A). For the RECIPROCAL RETURN: a second `portal_olympianarena1.dbr`
> inside SpartaCryptLevel2 (0x14: mouth_B + exit_B + dest=crypt-host GUID) + a
> `portal_olympianarena2.dbr` landing back in the Athens crypt host (0x14: mouth==exit_B). The
> bossarena.qst OnLevelLoad opens BOTH GridEntranceDynamic instances (by record name) wherever
> the player is. Fresh, unique mouth/exit UIDs are minted for each pair (collision-checked
> against the whole map). This is the A1 machinery verbatim, just a new coord + new UID pair +
> new dest GUID. NO 0x06 authoring, NO Quests.arc, NO new records.

**CHOSEN HOST + LANDING SPOTS:**
- **Crypt host = `CataCube02_FloorLast.lvl`** (v0x0f, corner (-6612,0,-3218), GUID
  `817574a8674093619ebf6581db63274c`) - the DEEPEST Athens catacomb chamber, thematically an
  exact match for SpartaCryptLevel2 (both use the `AthensCatacomb_*` set: sarcophagi, urns,
  skeletons). It is v0x0f like maze03 (the proven A1 host version) with 0 existing 0x14 entries
  (clean append) and a real baked navmesh (123,720-cell largest comp). It has `stairsdown01`
  (inst[72] @ world (-6581.5,1,-3182.5)) and `stairsup01` (inst[189] @ (-6523.4,1,-3142.2)) -
  natural crypt landmarks to place the portal beside. Roomy on-mesh centroid @ world
  (-6573.7,1.2,-3158.3) = local (38.1,1.2,59.9), openNbr 8/8.
- **SpartaCryptLevel2** (v0x0e, corner (-5644,0,-1451), MERGED GUID `797c78594040cba419340c990e6903c4`,
  real navmesh 75,244-cell comp) - roomy on-mesh centroid @ world (-5601.9,-1.6,-1414.7) =
  local (42.3,-1.6,36.3), openNbr 8/8. Its 0x06 already links OUT to SpartaOptCata01 (untouched).

**CAVEAT (walk-test-flagged):** reusing `portal_olympianarena1/2.dbr` means the Sparta portal
renders with the Olympian-arena portal mesh (`TJ_JudgementRoom_PortalObject`) - visually the same
object as the Uber Dungeon entrance, not a bespoke crypt door. This is the price of the
no-Quests.arc constraint (the only globally-opened GridEntranceDynamic record is that one). It is
mechanically correct (each instance teleports via its own 0x14) and thematically acceptable (a
glowing portal in a crypt). Documented for Will.

### B - the occultist scene (build24 HVBorder04 + SV originals)

**B1 WAGON OVERLAP - CONFIRMED (the screenshot bug):** in build24 HVBorder04:
- occultist merchant `Merchant_HiddenValley_General` (inst[16]) @ world **(-98.3,-102.4,2326.3)**
- Hades wagon `merchant_hades_merchantwagon01` (inst[37]) @ world **(-97.8,-102.4,2328.5)**
- **distance = sqrt(0.5^2 + 2.2^2) = 2.26u** in XZ -> the wagon is ~2.3u from the merchant = ON
  TOP of him (no clickable clearance). This is exactly Will's screenshot. MUST reposition to >=4u.

**B2 caravan scene pieces (current build24 positions):**
- wagon `merchant_hades_merchantwagon01` @ HVBorder04 world (-97.8,-102.4,2328.5)
- horse `Horse02` (inst[17]) @ HVBorder04 world (-99.6,-102.4,2321.8)
- caravan driver `silkroad_villager1` (inst[20]) @ HVBorder04 world (-94.9,-102.4,2331.9)
- the FUNCTIONAL Super-Caravan `caravan_silkroad` (inst[206]) @ HV01 world **(-92.3,-102.2,2317.1)**
  (moved by build24 B3 to the north end, next to the moved fountain)
- respawn fountain `respawntempleorient01` (HV01 inst[205]) @ world (-98.3,-102.4,2317.1)
  flags=1 uid=`feeb4bc6ce4e08c0e279b3824244aeeb`

> NOTE on "caravan driver": the brief says build24 moved the caravan driver to HV01's north
> end. GROUND TRUTH: build24 moved `caravan_silkroad` (the Super-Caravan NpcCaravan) + the
> fountain to HV01 north (-92.3/-98.3, 2317). The `silkroad_villager1` "driver" NPC is STILL at
> HVBorder04 (-94.9,2331.9), part of the occultist merchant scene there. So there are TWO
> "caravan" things: (a) the HV01 functional Super-Caravan cart (moved north), (b) the HVBorder04
> wagon+horse+villager1 occultist-merchant dressing scene. The brief's B2 "one caravan scene" =
> compose the HVBorder04 wagon+horse+villager1 coherently (they belong to the occultist merchant),
> non-overlapping, driver functional. The HV01 Super-Caravan is a separate, already-placed cart.

**B3 PURPLE AESTHETICS - build24 ALREADY restored the purple scene at HVBorder04:**
build24 injected (inst 42-45): `10mlight_dyn_purple` x2 @ (-87.0,2331.6)+(-92.9,2314.4);
`10mlight_dyn_red` x2. SV's Border04 original (recon) had EXACTLY these 2 purple + 2 red dynamic
lights (SV inst 0-3) at the SAME coords -> **build24 B1 covers the Border04 purple lights.**

**The OTHER occultist site (Greece, DelphiLowlands04 - the occultist TENT):** SV originals show
the occultist there was lit by `10mlight_statnl_blue` + `5mlight_dyn_green` (NOT purple) +
`fog_occult_fx01` around `merchant_delphi_occulttent01`. No purple-specific emitter at the Greece
occultist. So the "purple = special occultist" motif is the Border04 dynamic purple lights.

**B3 GATE RESULT (gate_b3_purple.py) = PASS, NO ACTION:** build24 ALREADY restored every SV
occult+purple emitter at the entrance occultist site, byte-coordinate-matched to SV:
`10mlight_dyn_purple` x2 @ (-92.9,-97.5,2314.4)+(-87.0,-97.5,2331.6) [SV-exact], `10mlight_dyn_red`
x2, `5mlight_stat_blue` x2, `fog_occult` x2, `occultistaura_fx01` (=`DRXeffects\other\occult_aura.pfx`,
Class EffectEntity) @ (-93.0,-102.5,2324.0) [SV-exact], woodpyre, anouranfirepit, totem x2,
disciple_aura x2. The purple "special occultist" look = the `10mLight_dyn_Purple.pfx` dynamic lights
+ the occult-aura pfx, all present. Greece occultist has NO purple emitter to port. So **B3 = already
satisfied by build24; no double-injection.**

---

## DESIGN DECISIONS (locked before implementation)

Planner: `tools/debug/plan_sparta_portals.py` (A), `tools/debug/plan_b_corrections.py` (B).

### A - Sparta Crypt L2 entrance (INVENTED, mirrors A1 exactly, pure-0x14, no Quests.arc)

Reuse `portal_olympianarena1.dbr` (GridEntranceDynamic, opened globally by the existing
bossarena.qst OnLevelLoad by record name) + `portal_olympianarena2.dbr` (GridExitOneWay landing),
each instance carrying its OWN 48-byte 0x14 binding (exactly the A1 mechanism). Four instances:

| # | record | host level | local coord | 0x14 (48B) mouth+exit+dest |
|---|--------|-----------|-------------|-----------------------------|
| P1 | portal_olympianarena1 (entrance) | CataCube02_FloorLast (v0f) | (29.10,1.20,41.30) | M1 + X1 + SC2guid |
| P2 | portal_olympianarena2 (landing) | SpartaCryptLevel2 (v0e) | (48.90,-1.60,34.70) | X1 + zeros(32) |
| P3 | portal_olympianarena1 (return entrance) | SpartaCryptLevel2 (v0e) | (50.30,-1.60,26.70) | M2 + X2 + HOSTguid |
| P4 | portal_olympianarena2 (return landing) | CataCube02_FloorLast (v0f) | (39.70,1.20,67.50) | X2 + zeros(32) |

- **Minted map-unique UIDs** (collision-checked vs 157,524 known map UIDs, `plan_sparta_portals.py`):
  - M1 (inbound mouth) = `efbf54c99a6b2bc7b64f04cd0ce8d0db`
  - X1 (inbound exit)  = `d76121ad4419c6d4dcab9301e18f0dca`
  - M2 (return mouth)  = `e8d88f28dbfe1c3fa79ae1aacc435010`
  - X2 (return exit)   = `6babdaaf344cc5476258f8e7ce8925f3`
  - SC2guid = `797c78594040cba419340c990e6903c4` ; HOSTguid = `817574a8674093619ebf6581db63274c`
- **UID pairing (mirrors A1):** P1.exit(X1) == P2.mouth(X1) EXACTLY; P3.exit(X2) == P4.mouth(X2)
  EXACTLY (the GridEntrance<->GridExit pairs). P1.dest == SC2 merged GUID; P3.dest == HOST GUID.
- **On-mesh (all openNbr 8/8, standoff-safe from loot/skeleton/stairs proxies):** P1 on-mesh 0.14u
  near stairsdown (the descend-deeper landmark), 6u standoff; P2 on-mesh @ SC2 centroid, 6u; P3 8.1u
  from P2 (arrival + return portal in the same chamber = a portal room); P4 on-mesh, 8u standoff, 28u
  from P1. HOST is v0x0f (same as maze03, proven A1 host) with 0 existing 0x14 (clean append);
  SC2 is v0x0e (inject_into_0x05 path, 56-byte record, 0x14 append needs an existing 0x14 section...
  BUT SC2 has 0 0x14 entries and no 0x14 section - HANDLING NOTE below).
- **v0x0e 0x14 append handling:** SpartaCryptLevel2 (v0e) currently has NO 0x14 section (0 entries).
  The step-7 0x14 append only fires `if s['type']==0x14`. For P2/P3 to get their bindings, SC2 needs
  a 0x14 section CREATED. maze03 (A1) worked because it already had a 0x14 section (size 0). So for
  SC2 the tooling must CREATE a 0x14 section (with just the 2 injected bindings) when injecting a
  spec with x14_payload into a v0e SV-shared level that lacks one. This is the one tooling gap to
  fill for Workstream A (documented in the tooling section). CataCube02_FloorLast also has 0 0x14 -
  same handling. Both are SHARED levels (kept AE copy) routed through the step-6 AE-inject path, so
  the fix is in svaera_plus_portals step-6/7.

**CAVEAT (walk-test):** the Sparta portals render with the Olympian-portal mesh (same visual as the
Uber Dungeon entrance) - the price of the no-Quests.arc constraint (only that record is globally
opened). Mechanically correct (each instance teleports via its own 0x14).

### B - corrections (all HVBorder04, one 0x05 blob)

**B1+B2 ONE CARAVAN SCENE (move wagon off the merchant, compose wagon+horse+villager1 together):**
keep the occultist merchant FIXED @ world (-98.3,-102.4,2326.3); MOVE the 3 caravan pieces to a
parked-caravan cluster on the WEST side of the occult camp (away from the merchant), all on-mesh,
merchant clickable:
| piece | build24 world | NEW world | NEW local (B04 corner -134,-104,2302) | d_merchant |
|-------|---------------|-----------|----------------------------------------|-----------:|
| wagon `merchant_hades_merchantwagon01` | (-97.8,-102.4,2328.5) [2.32u ON merchant] | (-111.0,-102.4,2322.0) | (23.00,1.62,20.00) | **13.4u** |
| horse `Horse02` | (-99.6,-102.4,2321.8) | (-108.0,-102.4,2319.0) | (26.00,1.62,17.00) | 12.2u |
| driver `silkroad_villager1` | (-94.9,-102.4,2331.9) | (-108.5,-102.4,2324.5) | (25.50,1.62,22.50) | 10.4u |
- wagon on-mesh 0.14u, horse 0.14u, villager 1.00u. Scene internally coherent: horse hitched
  ~4.2u in front (south) of the wagon, driver ~3.5u by the wagon (north side, clickable). Clear of
  the occult camp props (wagon 7.1u from the pyre/pit). The wagon keeps its SV yaw rotation; horse +
  villager keep their native rotations (carried from build24 - study their current rot bytes to
  preserve them).
- These are MOVES (change the existing INJECT_SPECS coords for wagon; horse02 + villager1 are NOT
  currently in INJECT_SPECS - they are native SVAERA Border04 records). **IMPORTANT:** horse02 +
  villager1 are NATIVE records in the SVAERA Border04 0x05 (inst[17],[20]); to move them I must
  EDIT their existing instance coords in-place (not append), OR the scene stays split. Handling:
  add an in-place 0x05 coord-override path (move an EXISTING native instance) - a new tooling
  capability. (The wagon is an INJECTED record so its move is just a coord change.)

**B3 = no action (build24 already restored the purple occult scene; gate PASS above).**

**B4 FINAL LAYOUT GATE (recomputed on proposed positions):** merchant clear (>=10.4u from every
scene piece, was 2.32u); scene pieces >=3.5u apart (wagon-horse 4.2u, wagon-villager 3.5u,
horse-villager 5.5u); sprites (pitspawner) 18.0u from merchant, 24.4u from fountain, 21.2u from
caravan; occultistaura 5.7u from merchant (SV-exact, the per-occultist FX). Fountain (HV01) is
128u north in a different level - re-verified >=25u from all hostiles (build24 B3, unchanged).

---

## TOOLING CHANGES (map tooling only)

- `tools/build_section_surgery.py`:
  - **SPARTA_* constants + 4 INJECT_SPECS portal entries** (2 in CataCube02_FloorLast, 2 in
    SpartaCryptLevel2) reusing `portal_olympianarena1/2.dbr` with minted 48-byte 0x14 bindings.
  - **`inject_into_sv_only_blob` extended** to append per-instance 0x14 bindings for specs with
    an `x14_payload` (needed for SpartaCryptLevel2's P2/P3 - the first time an SV-only level gets
    a 0x14 binding; the A1 maze03 case was a SHARED level). Append-only + hard collision assert
    (mirrors the shared-level step-7); creates a 0x14 section if absent (defensive; SC2 already
    has an empty one). Backward-compatible: specs without x14_payload append nothing (Hemorrheus
    proxy / widow trio / finalletter unchanged).
  - **`move_0x05_instances` (NEW)** + **`MOVE_SPECS` registry**: rewrites ONLY the 12 position
    bytes of EXISTING native instances (rotation/flags/string-index/UniqueId/pad preserved
    byte-for-byte), matched by dbr + optional `from_xyz`, with a hard zero-match assert. Used to
    move the native Border04 Horse02 + silkroad_villager1 for the caravan scene (B2).
- `tools/svaera_plus_portals.py`:
  - imports `MOVE_SPECS` + `move_0x05_instances`; step-6 applies MOVE_SPECS in-place (before the
    INJECT append) for shared v0x11/v0x0f levels.
  - (No change to the SV-only step-6b call site: `inject_into_sv_only_blob` now handles 0x14
    internally, so SpartaCryptLevel2's bindings flow through the existing call.)
- NEW read-only recon + gate scripts under `tools/debug/`: `recon_sparta_and_corrections.py`,
  `recon_sparta_deep.py`, `recon_gridpair.py`, `survey_gridentrance.py`, `plan_sparta_portals.py`,
  `plan_b_corrections.py`, `plan_b_wagononly.py`, `check_purple_dbrs.py`, `gate_b3_purple.py`,
  `gate_sparta_collateral.py`, `gate_sparta_placement.py`, `gate_sparta_byteparity.py`,
  `gate_sparta_reach.py`, `gate_portal_records_global.py`.
- Did NOT touch: DB scripts, navmesh generation, donors, Quests.arc. Left `fix_mc_output.py` /
  `hybrid_merge.py` alone (stale working-tree files, per the brief).

---

## IMPLEMENTATION COMPLETE - GATE RESULTS (map: local/Levels_merged.arc 688,685,020 B)

Baseline for diffs: `local/Levels_merged.build24-baseline.arc` (byte-copy of deployed build24).

### GATE RESULTS (verbatim)

- **Collateral (gate_sparta_collateral.py): PASS.** QUESTS/GROUPS/SD IDENTICAL; EXACTLY 3 blobs
  changed - CataCube02_FloorLast (244668->245012, +344 = P1+P4 records + 2x0x14), HVBorder04
  (224876->224876, SAME size = the in-place moves + wagon coord change add zero bytes),
  SpartaCryptLevel2 (85971->86283, +312 = P2+P3 + 2x0x14). 0 bad magic, 0 malformed / 2282
  levels, **0 navmeshes (0x0b) changed** (blood-cave + all SV-area meshes untouched). maze03 (A1)
  + hiddenvalley01 (B3 fountain) NOT in the changed list.
- **Placement (gate_sparta_placement.py): PASS.**
  - A: all 4 portals present at intended local coords, flags=0 + identity rot, **on-mesh
    ~0.000u** (P1 (29.10,1.20,41.30), P4 (39.70,1.20,67.50), P2 (48.90,-1.60,34.70), P3
    (50.30,-1.60,26.70)); all 48-byte 0x14 bindings resolve: P1.mouth=M1/exit=X1/dest=SC2 GUID;
    P2.mouth=X1(==P1.exit)/zeros; P3.mouth=M2/exit=X2/dest=HOST GUID; P4.mouth=X2(==P3.exit)/zeros.
  - B: wagon 13.4u from merchant (was 2.32u), on-mesh 0.14u; horse (-108.0,2319.0) on-mesh 0.14u;
    villager (-108.5,2324.5) on-mesh 1.00u (clickable); wagon-horse 4.2u, wagon-villager 3.5u;
    sprites 18.0u from merchant; all B4 mutual distances pass.
- **Byte-parity (gate_sparta_byteparity.py): PASS.** Injected portals = A1 exemplar shape (flags=0,
  identity rot, size 72 in v0f host / 56 in v0e SC2). Moved horse02 + villager1: rotation + flags +
  string-index BYTE-IDENTICAL to build24; **ONLY the 12 position bytes changed**. All DBRs resolve
  in the arz (portals via base arz GridEntranceDynamic/GridExitOneWay; horse/villager base arz).
- **Reachability (gate_sparta_reach.py): PASS.** All 4 portals in the LARGEST walkable component
  (crypt 123,720 cells; SC2 75,244 cells), 0.00u to nearest cell. P1+P4 share the crypt's main
  component; P2+P3 share SC2's main component (so the return portal is reachable from arrival).
- **Global portal-record integrity (gate_portal_records_global.py): PASS.** Reusing
  portal_olympianarena1/2 for Sparta did NOT break A1: maze03[447]->crypt_floor1 intact, its exit
  pairs crypt_floor1[192] landing exactly. The 3 entrance mouth/exit UID pairs (A1 / Sparta-in /
  Sparta-return) are ALL DISTINCT (no portal cross-talk); each GridExitOneWay landing has a unique
  mouth pairing exactly one entrance's exit.
- **A1 + B3-fountain UNTOUCHED:** maze03 blob + hiddenvalley01 blob BYTE-IDENTICAL vs build24;
  fountain UID feeb4bc6.. flags=1 intact; A1 portal still at idx 447.
- **Blood-cave regression: verify_merged_bc_navmeshes 24/24 PASS + entrance_landing --check-merged
  G2 PASS** (508 cells, dY +0.00u, donor + merged).
- **Opener present:** bossarena.qst in deployed Quests.arc, Condition_OnLevelLoad + opens
  portal_olympianarena1 by name -> the Sparta GridEntranceDynamic instances WILL be opened, no
  Quests.arc change.
- **Athens crypt HOST reachable in normal play:** AthensCity04 (overworld) -GridEntrance->
  Entrance01 -> Floor5 -> Floor4 -> **CataCube02_FloorLast** (+ Floor0 path). A legitimate
  reachable Athens Catacombs dungeon (thematic match: both use the AthensCatacomb set).

### THE ONLY THINGS NO OFFLINE GATE SETTLES (WALK-TEST-PENDING)
- **A**: whether the GridEntranceDynamic actually teleports in-game (the quest-open + Grid pair
  chain is the same unrehearsed mechanism A1 flagged; A1 itself is still walk-test-pending). If
  the Sparta portal is visible but inert, the fallback is identical to A1's (re-check bossarena.qst
  OnLevelLoad binding).
- **A (cosmetic)**: the Sparta portals render with the Olympian-portal mesh (same as the Uber
  Dungeon entrance) - the price of the no-Quests.arc constraint.

---

## WHAT WILL MUST WALK-TEST (per item; full TQ restart required, Custom Quest char)

### A - Sparta Crypt L2 entrance (Athens Catacombs, Act 1 Greece)
- From **Athens City** enter the **Athens Catacombs** (AthensCity04 has the cave mouth ->
  Entrance01) and descend the catacomb chain (Floor5 -> Floor4/Floor0) to the **deepest chamber,
  CataCube02_FloorLast**. Near the **stairs-down** landmark, look for an **Olympian-arena portal
  object** (same glowing portal visual as the Uber Dungeon entrance) at world (-6582.9,-3176.7).
  WALK INTO IT.
- EXPECTED: bossarena.qst's OnLevelLoad opens it (by record name) and it teleports you to
  **SpartaCryptLevel2** (an Athens-catacomb crypt, sarcophagi + skeletons), landing at the exit
  portal. A **return portal** stands ~8u away in the crypt - walk into it to return to the Athens
  crypt (landing ~28u from where you entered). OFFLINE-VERIFIED: both portals on-mesh in the main
  walkable floor, 0x14 bindings resolve to the correct merged GUIDs with byte-exact mouth/exit
  pairing, the crypt host is reachable in normal play, the opener quest is present. NEEDS EYES: the
  teleport actually firing (the GridEntranceDynamic + quest-open chain is unrehearsed - the same
  single uncertainty as A1's Uber Dungeon portal).

### B - HVBorder04 caravan scene (blood-cave entrance area, occultist merchant)
- At the **occultist merchant** (HiddenValleyBorder04, north of the Silk Road cave mouth), confirm
  the **Hades wagon is NO LONGER on top of the merchant** - the wagon + horse + caravan driver now
  sit as **one parked caravan ~13u WEST** of the merchant (on the open bench by the occult camp),
  and the merchant is freely clickable. The occult **purple/red lights + fog + aura + pyre + totems**
  still ring the merchant (unchanged from build24). The **exploding pit-sprites** are ~18u east.
- EXPECTED: purely a layout fix - nothing overlaps, the driver is talkable, the merchant is
  clickable, the scene reads as a coherent caravan beside the occultist. OFFLINE-VERIFIED: wagon
  13.4u from merchant (was 2.3u), caravan pieces on-mesh + coherent (3.5-4.2u apart), driver
  clickable (on-mesh 1.0u), sprites 18u from merchant, all B4 distances pass, purple scene present
  (B3 = build24 already restored it). NEEDS EYES: that the moved horse/driver/wagon look right on
  the terrain (they kept their SV rotations) and the driver's shop/functionality still opens.

## NOT DEPLOYED / NOT COMMITTED (per the brief)
The rebuilt map is `local/Levels_merged.arc` (688,685,020 B, deterministic md5 of world01.map
`5e534484...`). Deployed `work/.../Levels.arc` UNCHANGED (build24, 688,687,606 B). Quests.arc
UNCHANGED (A needs none; the opener bossarena.qst already ships). No deploy, no commit, no
Workshop - the main session owns those. Baseline for rollback/diff:
`local/Levels_merged.build24-baseline.arc`.
