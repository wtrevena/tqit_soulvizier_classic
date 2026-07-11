# build36 MAP WAVE report (rounds 1-2)

> Branch `feat/build36-map-wave`. Owns `tools/svaera_plus_portals.py` + map tooling
> (`tools/build_section_surgery.py`) + `tools/debug/survey_uberboss_spots.py` +
> `tools/contracts/contracts_map.py` (the map contract gate). No push, no deploy.
> Baseline = the build35 canonical/TESTHUB maps (`local/Levels_merged*.build35-baseline.arc`,
> snapshotted this round). All coords LEVEL-LOCAL unless marked WORLD. No em dashes.

> **ROUND 2 (vet fixes) applied 2026-07-11 - see the `## ROUND 2` section below.** Headline:
> the vet found the R1 Dorus injection into Tomb01 caused a **contracts_map ship-gate regression**
> (4 undisclosed MAP-DOOR-1 P1 false positives on native xsq06 doors). FIXED at the root
> (record-namespace door scoping). The MAP ARTIFACTS ARE UNCHANGED from R1 (round 2 touched only the
> contract gate + the survey probe; blob-diff proves byte-identity). The R1 gate table's
> contracts_map row was inaccurate and is corrected below.

This round started from a prior killed round's uncommitted draft (UBERBOSS_SPECS + warden split
already in `build_section_surgery.py`, plus the survey probe). This round VETTED that draft against
the specs, RE-SURVEYED every boss spot on the built map (the specs mandate it), nudged the ones that
read near-wall/off-mesh, added M1 (yard respace) and resolved M2, then built + gated.

---

## PLACEMENTS TABLE (boss -> host level -> local coord -> INJECT_SPECS key)

All 5 boss proxies are CANONICAL (shipped, in both map variants), one `q_*_lone` proxy each,
flags=0, `Q_LEINTH_EXEMPLAR_ROT`, appended to the host's 0x05 via the version-correct inject branch.
The DB lane authors the `q_*_lone` records + pools + hoard chests against the same specs; the map
placement is inert until the arz merges (convergence delta-vet checks placement<->record-path parity).

| # | Boss | Host level (INJECT_SPECS key) | ver | grid corner (world) | FINAL local (x,y,z) | WORLD (x,z) | clr@ext (N/E/L) | INJECT_SPECS key |
|---|------|-------------------------------|-----|----------------------|---------------------|-------------|-----------------|------------------|
| M4 | Dorus, the Drowned King | Medea_TempleUG_Tomb01 [784] | v0e | (260,0,-8522) | (49.0, 1.2, 63.0) | (309,-8459) | 97/97/94% @4.0 | `xpack/levels/area02_medea/undergrounds/medea_templeug_tomb01.lvl` |
| M5 | Tantalus, the Insatiable | Styx_SwampBorder_01 [755] | v0f | (-396,0,-10209) | (50.0, -15.2, 116.0) | (-346,-10093) | 94/93/90% @3.5 | `xpack/levels/area04_styx/styx_swampborder_01.lvl` |
| M6 | Charon at the Golden Bough | Styx_RiverEdge_01 | v11 | (-524,0,-9697) | (185.0, -7.0, 48.0) | (-339,-9649) | 100/99/96% @3.5 | `xpack/levels/area04_styx/styx_riveredge_01.lvl` |
| M7 | The Mnemophage | Judgment_TempleUG_Mnemosyne01 [801] | v11 | (127,-13,-11509) | (43.0, 3.0, 71.0) | (170,-11438) | 97/97/94% @3.5 | `xpack/levels/area05_judgment/undergrounds/judgment_templeug_mnemosyne01.lvl` |
| M8 | Ephialtes, the Dread | Judgment_StoneCity_Exit01 [931] | v11 | (-1844,0,-13320) | (22.0, 3.2, 45.0) | (-1822,-13275) | 100/100/100% @3.5 | `xpack/levels/area05_judgment/undergrounds/judgment_stonecity_exit01.lvl` |

Proxy DBRs placed (one per boss): `q_dorus_lone`, `q_tantalus_lone`, `q_goldenbough_lone`,
`q_mnemophage_lone`, `q_ephialtes_lone` (all under `records\drxmap\proxy\`). Each boss's hoard chest
rides the proxy's DB-side accessory pool (spawns WITH the boss) - no separate chest placement.

### Re-survey findings (why the nudges)
Every spec MANDATED a re-survey + nudge on the built mesh. The survey frame was VALIDATED by
`--calibrate` (native floor-level instances read on-mesh ~0.1u; wall/rock decor reads off-mesh as
expected). Results vs the draft's spec-primary coords:

- **M4 Dorus**: spec (52,60) reads clr@4.0 56/53/45% (near a wall). Nudged +4.2u to (49,63) = 97/97/94%.
- **M5 Tantalus**: spec (54,114.3) reads OFF-mesh (38/30/25%). Nudged +4.5u to (50,116) = 94/93/90%.
- **M6 Charon**: draft forecourt (187.9,46.9) reads 61/57/53%. Nudged +3.2u to (185,48) = 100/99/96%.
  RE-SURVEY FINDING: the design-preferred SUMMIT is ALSO viable after a +2.2u nudge - (219,14) =
  98/96/94% - contradicting the spec's "summit too tight (2.8u)" claim. Kept the forecourt as the
  safe primary this wave; recorded the summit as a viable A/B alternate (commented in code).
- **M7 Mnemophage**: spec (43,71) is already clean (97/97/94%). UNCHANGED (the one the draft nailed).
- **M8 Ephialtes**: spec (15.9,34.7) reads OFF-mesh (0% - ~7u past the mesh edge; the dreadhalls
  spec coord did not resolve in the validated grid-local frame). Nudged +11.7u NE to (22,45) =
  100/100/100%, still ~110u from the NE arrival stairs = the "back corner" per Will's order.

Collision guard: nearest solid feature to each nudged spot >= 6.6u (M5-M8); M4's nearest is a point
light at 1.4u (harmless emitter, no mesh). No boss spot overlaps a native quest object.

Injection dispatch (svaera_plus_portals.py AE-inject loop) routes by the host's ACTUAL blob version:
Tomb01 (v0e) -> base-56 `inject_into_sv_only_blob`; the other 4 (v0f/v11) -> base-72
`inject_into_0x05_v11`. Both branches proven by shipped precedents on the same versions (obsidian +
broodmother into tombobs01/02 v0e; maze03 v0f).

---

## M3 WARDEN SPLIT (TESTHUB map only)

Map-side of the build36 warden split (root cause: the single `svc_testhub_master` was placed in TWO
levels, so `Action_BoatDialog` bound its menu to one entity and the second placement went mute).
`build_hub_extra_specs`:
- Helos host (`startingfarmland06d`): `svc_testhub_master_helos.dbr` at local (86.0, 0.8, 189.5)
  (NUDGED ~9.5u E of the canonical Almyros NPC at (76.5,0.6,189.5) for H5 click-occlusion insurance).
- Blood-cave mouth (`random09a` SV swap blob, applied via the swap path): `svc_testhub_master_cave.dbr`
  at local (32.0, 1.0, 45.0) (coords unchanged).
- STOPPED placing the shared `svc_testhub_master` (constant kept for reference).

DB lane owns the two split records (`_helos` / `_cave`); the quests lane owns the 3 triggers
(helos 7 ports, cave 7 ports, return 2 ports). Canonical `Levels.arc` stays byte-identical (rig is
TESTHUB-only). Warden spot on-mesh re-survey: see gates below.

---

## M1 YARD RESPACE (TESTHUB HV01, de-crowd)

Will: "pets too crowded." The old yard packed 8 groups into tight clusters (min 6.1u; the 4 Obsidian
within ~6-11u). RESPACED to spread all **9** groups (8 build35 residents + the NEW `q_yard_dorus`)
across HiddenValley01's walkable valley [R2 correction: the count is 9, not the "10" first written]:

- min pairwise **32.2u** (was 6.1u) - a ~5x de-crowd.
- Every spot on-mesh in all 3 tilesets, clr@2.5 >= 91%, and in the SAME walkable component as the
  cave-mouth/camp (flood-fill verified reachable on foot).
- New yard proxy `q_yard_dorus` (Lane A created it) added for the Drowned King fight.

**GEOMETRIC LIMIT (open item for Will):** the task asked for >=60u, but HV01's walkable footprint is
a winding valley - only ~23% of its bounding box is floor. The absolute on-mesh ceiling for 9 spawn
spots is **~45u**, and **~32u** once reachability + a clear spawn disc are enforced.
60u is geometrically impossible here for this many groups. 32u already separates every group by
roughly a screen-width, which resolves the crowding. To reach a literal 60u we would need to either
(a) reduce the number of yard groups, or (b) move the yard to a larger FLAT host level (e.g. a Hades
plain). Flagged for Will's call.

---

## M2 BLUE-BOX REMOVAL (investigated; no distinct entity found in map scope)

The task asked to remove "debug/placeholder blue boxes" per a BACKLOG "visual-debris item." Exhaustive
search (BACKLOG, all docs, the live memory board, the whole repo, git log across branches, and a full
dump of every canonical + TESTHUB INJECT_SPECS placement) found **no distinct debug/placeholder
blue-box entity** to remove. What exists:

- The **retired born-open GridEntrance hub portals** (20 blue panels in the blood cave) - the classic
  "flat blue panel" artifact (B-PORTAL-1). These were already RETIRED in build34 and are **absent
  from a fresh build35/36** map (verified: Random09A has 0 `portal_olympianarena` refs in both
  variants). So if Will's blue boxes were those, this rebuild already removes them.
- The **canonical portal_olympianarena content doors** (Garden/Secret Place/Sparta/Uber, 14 refs) also
  render as blue panels (B-PORTAL-1), but they are CONTENT doors owned by the portal-fix lane
  (B-PORTAL-1/2/3 = give them proper mesh/FX + fix returns, NOT remove). Removing them would break
  those areas' access, and the memory board tracks "portal placement/returns/labels" as a SEPARATE
  map-lane item from "blue-box removal."

**Decision:** did NOT destructively remove any content on a guess. Flagged for the convergence
coordinator to confirm the exact M2 target with Will (see open items). If Will points at a specific
in-game blue box, a follow-up delta can remove it once identified.

---

## GATES (build36 vs build35)

Both variants rebuilt from the SVAERA base (re-populated `reference_mods` + `upstream` this round,
the gitignored inputs had been cleared). Canonical `local/Levels_merged.arc` = 688,690,448 B
(build35 was 688,689,377; +1,071 B = 5 boss proxies). TESTHUB rebuilt. Baselines snapshotted to
`local/Levels_merged*.build35-baseline.arc`.

| Gate | Result |
|---|---|
| Build validity (canonical) | **PASS** 2282 levels, 0 bad offsets / 0 bad magic / 0 zero ints |
| verify_merged_bc_navmeshes (canonical) | **PASS 24/24** real navmeshes present, 0x0a stripped |
| seam_lattice_check --gate (canonical) | **PASS** 24 aligned seams, 0 misaligned |
| entrance_landing_check --check-merged | **PASS** G2: DONOR + MERGED both 508 cells, dY +0.00u |
| Boss placement survey (BUILT map, 3 tilesets) | **PASS** M4 97/95/94% · M5 96/94/92% · M6 100/100/100% · M7 97/97/94% · M8 100/100/100% (clr@extents; all on-mesh d<=0.14u) |
| Canonical blob-diff vs build35 | **PASS** EXACTLY 5 blobs changed (the 5 boss hosts), each 0x05 +1, EVERY 0x0b byte-identical; QUESTS/GROUPS/SD/BITMAPS identical; 0 added / 0 removed |
| TESTHUB blob-diff vs build35-TESTHUB | **PASS** EXACTLY 8 blobs (5 boss hosts + HV01 yard 9->10 + 2 warden hosts), all 0x0b byte-identical |
| TESTHUB vs canonical (hub-only extras) | **PASS** canonical is a byte-prefix of TESTHUB minus the yard (HV01 +10) + rig (2 masters + 5 returns); all 0x0b identical -> canonical stays co-op-safe |
| contracts_map (BUILD36 map + arz) | ~~R1 CLAIM (INACCURATE, corrected R2):~~ R1 stated "0 P0; 4 P1 = MAP-REF-1 ... No typo'd/unexpected refs." That was WRONG: R1 build36 actually had **11 violations / 8 P1** (the 4 MAP-REF-1 PLUS 4 undisclosed MAP-DOOR-1 on Tomb01's native xsq06 lever/key doors, caused by the Dorus proxy putting `drxmap` in that base blob). **R2 FIXED** the contract's over-broad door scope. **POST-FIX build36 = 7 viol / 4 P1** (0 P0; the 4 P1 are EXACTLY the expected MAP-REF-1 `q_tantalus/q_goldenbough/q_mnemophage/q_ephialtes_lone`, not-yet-in-arz; `q_dorus_lone` resolves; 3 pre-existing base-game portal P2s not mine). BUILD35 baseline = 3 viol / 0 P1 (unchanged, regression-guarded). negtest `_negtest_map.py` = 25/25. See `## ROUND 2`. |
| Warden Helos on-mesh (M3) | **FIXED** the draft's 86.0 was a mesh gap (clr@3.0 10-17%); moved to (64.5,0.8,189.5) = clr@3.0 100% all 3 tilesets, 12u from Almyros. TESTHUB rebuilt + re-verified. |
| det-2x (rebuild -> md5 match) | DEFERRED to convergence (vet-aligned). R2 changed ONLY the contract gate + survey probe - NOT any map-generation code - so the maps are byte-for-byte the R1 artifacts (proven: blob-diff vs build35 shows only the 5/8 expected 0x05 proxy additions, EVERY 0x0b byte-identical). A true from-source det-2x (PYTHONHASHSEED=0, 2x) needs the full donor + reference_mods setup (gitignored, main-repo-only) and is best run once on the frozen map at convergence. |
| Read-only gate battery re-run (R2, vs the unchanged build36 map) | **verify_merged_bc_navmeshes PASS 24/24** (0x0a stripped); **seam_lattice_check --gate PASS** (24 aligned, 0 misaligned); **entrance_landing_check --check-merged PASS** (donor+merged both 508 cells, dY +0.00u); **contracts_map** POST-FIX (canonical + TESTHUB) = 4 P1 (the expected MAP-REF-1) only; **blob-diff** = 5 canonical / 8 TESTHUB blobs, all 0x0b byte-identical. |

The 4 MAP-REF-1 P1s are the ONLY blocking violations and they are the intended, documented "placement
inert until the DB lane creates the record" state - the convergence delta-vet re-checks after the DB
lane authors the Tantalus/Charon/Mnemophage/Ephialtes proxy records against the same specs.

## ROUND 2 (vet fixes) - 2026-07-11

The R1 vet returned 3 NO_GO issues (1 P1, 1 P2, 1 P3) + 4 curiosity findings. Disposition below.
NOTE: no map-generation code changed this round - only the contract gate + the survey probe - so the
map artifacts are byte-identical to R1 (proven by the blob-diff re-run above). No rebuild was needed.

### P1 (FIXED) - contracts_map MAP-DOOR-1 regression from the Dorus injection
- **Root cause (confirmed from bytes):** `contract_doors` (tools/contracts/contracts_map.py) decided a
  level was "our restored content" via a blob-wide `b'drxmap' in blob` flag (through `_is_our_content`).
  R1 appended the Dorus proxy `records\drxmap\proxy\q_dorus_lone.dbr` to the 0x05 of the BASE-game
  Immortal-Throne level `Medea_TempleUG_Tomb01`. That lone injected string put `drxmap` in an otherwise
  base blob, so the contract reclassified Tomb01 as ours and flagged its 4 NATIVE xsq06 lever/key doors
  (`records\xpack\quests\objects\xsq06_leverdoora/leverdoorb/keydoor_a/keydoor_b`, all locked=1,
  unlocked in-game by base-game lever/key mechanics the mod does not carry) as MAP-DOOR-1 P1. These
  are false positives that (a) turned a fail-loud ship-gate red, (b) persist independent of the DB lane
  (unlike the MAP-REF-1s), and (c) were NOT disclosed by the R1 report (which claimed the only 4 P1
  were MAP-REF-1). Reproduced: R1 build36 = 11 viol / 8 P1; build35 baseline = 3 viol / 0 P1.
- **Fix (root-cause, minimal, mirrors MAP-REF-1's scope guard):** scope MAP-DOOR-1 by the **door
  RECORD's SV namespace** (`records\drxmap\ / all_sv\ / \sv\ / svitems\`), not by the level blob's
  drxmap presence. A base-game / DLC door record is unlocked by its own base mechanic, so it is out of
  scope wherever placed. PROVEN safe: every genuine SV door record is SV-namespace
  (`records\drxmap\bloodcave\*` incl. B-TEMPLE-DOOR-1's `babtpl_waterfallroom_secretdoor` +
  `waterblocker`; `records\drxmap\xurder\*`), so record-scoping keeps the real temple-door class fully
  covered while being robust to ANY placed-proxy injection into a base host. The false-positive xsq06
  doors are `records\xpack\quests\objects\*` (base namespace) -> now correctly excluded.
- **Verification:** POST-FIX build36 (canonical AND TESTHUB) = 7 viol / **4 P1 = the 4 expected
  MAP-REF-1 only** (0 P0, 3 pre-existing native/DLC portal P2s). BUILD35 baseline = 3 viol / 0 P1
  (regression-guard: unchanged). `_negtest_map.py` = 25/25 (both DOOR-1 checks still pass: it fires on
  an unreferenced locked SV drxmap door, stays clean on a referenced one).

### Survey probe hardened (curiosity finding #2) - tools/debug/survey_uberboss_spots.py
Two blind spots closed, faithful to `navlib`'s engine model:
1. **Null-height holes:** `build_walk_cells` now requires `heights != 0xff` in addition to `areas != 0`
   (a cell over a 0xff null-height hole is not walkable). On these 5 hosts it removes 0 cells (so the
   R1 clearances are unchanged: M4 97/95/94, M5 96/94/92, etc.), but the probe can no longer report a
   hole as clear.
2. **Connected-component reachability:** added an absolute-height (`hmin+hs`, `|dh|<=5` climb, 4-adj)
   component model; each surveyed point now reports its nearest cell's component rank/size and a spot
   on an isolated island (rank>1) reads CHECK. Re-surveyed on the built map: **every PRIMARY boss spot
   + the warden Helos FINAL (64.5,189.5) read `comp#1`** (the main reachable component) - e.g. M6
   Golden Bough forecourt = comp#1/350496 (this directly confirms curiosity finding #4: the tiered
   Styx_RiverEdge temple is one component under the correct absolute-height model). The tool's strict
   binary CHECK on M4/M5/M7 PRIMARY is the pre-existing `clr>=95%`-on-all-3-tilesets threshold dipping
   to 94% on the more-eroded Legendary set - NOT a reachability problem (all comp#1, on-mesh d=0.14u);
   acceptable for a boss arena per the R1 human assessment.

### P2 (OPEN - Will's decision) - M1 yard 32.2u vs the >=60u ask
Independently re-verified on the built TESTHUB HV01: **9** `q_yard_*` group proxies (the 8 build35
residents + the new `q_yard_dorus`; R1/vet said "10" - the actual placed count is 9, and the TESTHUB
HV01 0x05 grew by exactly one instance, +113 B), **min pairwise 32.2u** (between `q_yard_obs_ilsevar`
and `q_yard_wyrm`) - a ~5x de-crowd from build35's 6.1u. 60u is geometrically infeasible here (HV01's
walkable valley is ~4,470 sq-units; hex-packing even 9 discs at 60u needs ~25,000+). Per DONE-means-
DONE this is NOT delivered to the literal spec and needs Will's explicit call (see OPEN ITEMS #1).

### P3 (DEFERRED to convergence) - det-2x determinism
Not run: R2 changed no map-generation code, so the maps are byte-identical to R1 (blob-diff proof
above). A from-source det-2x (PYTHONHASHSEED=0, 2 full builds, md5 match) needs the gitignored donor +
reference_mods inputs (main-repo only) and is best run once on the frozen map at convergence. Vet-aligned.

### Curiosity findings - disposition
1. **16u frame error in all 5 boss specs** (harmless; explains the wave): CONFIRMED as the reason 4 of
   5 spec-primary coords read off-mesh/near-wall, which is why R1 re-surveyed + nudged on the built
   mesh. Lesson (recorded here + carried in the probe docstring): never trust spec WORLD coords for
   these hosts; always survey the BUILT map in the navmesh-origin frame (the R1 re-survey did this).
2. **survey probe blind spots:** FIXED (above).
3. **`_is_our_content` blob-drxmap class (portals too):** the DOOR half is FIXED. The PORTAL half
   (`_collect_portals` uses the same blob flag to set the `ours` P0/P2 severity) did NOT misfire in
   build36 (the 3 native portal P2s are in non-boss-host levels; no host had a native portal to
   escalate). It is NOT a simple mirror of the door fix - a base-game GridEntrance record placed in a
   genuine SV level IS ours (must work), so dropping the blob signal there would UNDER-classify. Left
   for the map-contract-suite owner (task #30) to harden holistically; RECOMMENDED, not a current
   defect. Documented here so it is not lost.
4. **tiered-Hades absolute-height components:** addressed by the probe hardening (#2); the Golden Bough
   forecourt is confirmed in the main component (comp#1).

## OPEN ITEMS

1. **M1 yard >=60u (Will's decision - NOT done to literal spec).** Delivered 32.2u (9 groups, all
   on-mesh + main-component + clr>=91%), a ~5x de-crowd from 6.1u. 60u is geometrically infeasible in
   HV01 (~4,470 sq-units of floor; ~32u is the practical ceiling once reachability + a clear spawn disc
   are enforced). Options: **(a) accept 32.2u** (recommended - it puts each group ~a screen-width
   apart and resolves the "all on top of each other" complaint); (b) reduce the yard to ~4-5 groups so
   60u fits; (c) relocate the yard to a larger FLAT host (e.g. a Hades plain) where 60u fits all 9.
   TESTHUB-only; no ship impact either way.
2. **M2 blue-box** - no distinct debug/placeholder box exists in map scope; needs Will to identify
   the exact in-game artifact (the retired hub panels are already gone; the content portal panels are
   the B-PORTAL lane's job, not removal).
3. **M6 Charon summit A/B** - the re-survey found the design-preferred summit (219,14) viable at 98%
   AND in the main component (comp#1); a future in-game A/B could move Charon atop the shrine.
   Forecourt (comp#1/350496, 100% clr) shipped this wave.
4. **DB parity** - the 5 `q_*_lone` proxies + `q_yard_dorus` must exist in the merged arz; MAP-REF-1
   will flag them as not-yet-in-arz until the DB lane merges (EXPECTED this round; the 4 remaining P1
   resolve when Tantalus/Charon/Mnemophage/Ephialtes records land).
5. **Portal `_is_our_content` blob-drxmap hardening** (curiosity #3) - recommended for the map-contract
   -suite lane (task #30); not a current defect (did not misfire in build36).
6. **det-2x** - run PYTHONHASHSEED=0 2x on the frozen map at convergence (P3).
