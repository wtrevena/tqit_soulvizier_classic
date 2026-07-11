# build36 MAP WAVE report (rounds 1-3)

> **ROUND 3 (vet fixes) applied 2026-07-11 - see the `## ROUND 3` section below.** Headline: the R3
> vet found FOUR report/narrative errors (no artifact defects): (1) M1 yard count was wrongly
> "corrected" to 9 in R2 - the real built count is **10** (re-verified: 10 proxies, min pairwise
> **32.25u**); (2) the M3 body text still said the rejected 86.0 draft - the shipped + correct coord
> is **64.5**; (3) the "16u frame error in all 5 specs" narrative is inaccurate - 4 of 5 spec-primary
> coords are ON-mesh (d<=0.5u), just near-wall/low-clearance, and only M8's is genuinely off-mesh
> (~7.2u); (4) det-2x is SATISFIABLE now and is **CLOSED PASS** (both variants rebuild byte-for-byte
> from the worktree source). The MAP ARTIFACTS ARE UNCHANGED from R1/R2 (R3 touched only this report +
> a new read-only probe `tools/debug/build36_map_probe.py`; a full det-2x rebuild reproduced both
> R2 artifacts byte-identically, MD5s in `## ROUND 3`).

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
| M4 | Dorus, the Drowned King | Medea_TempleUG_Tomb01 [784] | v0e | (260,0,-8522) | (49.0, 1.2, 63.0) | (309,-8459) | 97/95/94% @4.0 | `xpack/levels/area02_medea/undergrounds/medea_templeug_tomb01.lvl` |
| M5 | Tantalus, the Insatiable | Styx_SwampBorder_01 [755] | v0f | (-396,0,-10209) | (50.0, -15.2, 116.0) | (-346,-10093) | 96/94/92% @3.5 | `xpack/levels/area04_styx/styx_swampborder_01.lvl` |
| M6 | Charon at the Golden Bough | Styx_RiverEdge_01 | v11 | (-524,0,-9697) | (185.0, -7.0, 48.0) | (-339,-9649) | 100/100/100% @3.5 | `xpack/levels/area04_styx/styx_riveredge_01.lvl` |
| M7 | The Mnemophage | Judgment_TempleUG_Mnemosyne01 [801] | v11 | (127,-13,-11509) | (43.0, 3.0, 71.0) | (170,-11438) | 97/97/94% @3.5 | `xpack/levels/area05_judgment/undergrounds/judgment_templeug_mnemosyne01.lvl` |
| M8 | Ephialtes, the Dread | Judgment_StoneCity_Exit01 [931] | v11 | (-1844,0,-13320) | (22.0, 3.2, 45.0) | (-1822,-13275) | 100/100/100% @3.5 | `xpack/levels/area05_judgment/undergrounds/judgment_stonecity_exit01.lvl` |

Proxy DBRs placed (one per boss): `q_dorus_lone`, `q_tantalus_lone`, `q_goldenbough_lone`,
`q_mnemophage_lone`, `q_ephialtes_lone` (all under `records\drxmap\proxy\`). Each boss's hoard chest
rides the proxy's DB-side accessory pool (spawns WITH the boss) - no separate chest placement.

### Re-survey findings (why the nudges) - R3-corrected root cause
Every spec MANDATED a re-survey + nudge on the built mesh. The survey frame was VALIDATED by
`--calibrate` (native floor-level instances read on-mesh d~0.0-0.1u; wall/rock decor reads off-mesh as
expected). **R3 CORRECTION of the root-cause narrative:** the nudges are NOT fixing a "16u frame
error" (see the corrected curiosity #1 in `## ROUND 3`). Re-surveyed on the built canonical map
(`survey_uberboss_spots.py --bosses`), 4 of the 5 spec-primary coords land ON-mesh in the validated
frame (d<=0.5u); they were nudged because they sit NEAR A WALL with a LOW clearance disc, not because
they were off-mesh. Only M8's spec coord is genuinely off-mesh. Verified d/clearance, spec-primary ->
shipped FINAL (N/E/L clr @ proxy placementExtents):

- **M4 Dorus**: spec (52,60) is ON-mesh (d=0.14u) but near a wall - clr 57/53/45%. Nudged +4.2u to
  the FINAL (49,63) = d=0.14u, clr 97/95/94%, comp#1.
- **M5 Tantalus**: spec (54,114.3) is ON-mesh (d=0.10/0.30/0.50u) but near a wall - clr 43/35/26%
  (NOT "off-mesh" as R1/R2 mislabeled it). Nudged +4.5u to the FINAL (50,116) = d=0.14u, clr
  96/94/92%, comp#1.
- **M6 Charon**: draft forecourt (187.9,46.9) read low-clearance (61/57/53%). Nudged +3.2u to the
  FINAL forecourt (185,48) = d=0.14u, clr 100/100/100%, comp#1. RE-SURVEY FINDING: the
  design-preferred SUMMIT is ALSO viable - (219,14) = d=0.14u, clr 99/97/96%, comp#1 - contradicting
  the spec's "summit too tight (2.8u)" claim. Kept the forecourt as the safe primary this wave;
  recorded the summit as a viable A/B alternate (commented in code).
- **M7 Mnemophage**: spec (43,71) is already clean (d=0.14u, clr 97/97/94%, comp#1). UNCHANGED (the
  one the draft nailed - it needed no nudge; the task-prompt's M7 coord `(54,-15.2,114.3)` is a
  copy-paste of M5's local coord, so the real `mnemosyne_uberboss_spec.md` PRIMARY was followed).
- **M8 Ephialtes**: spec (15.9,34.7) is the ONLY genuinely off-mesh spec coord - d=7.21/7.47/7.66u,
  clr 0%, comp=NONE (~7.2u past the mesh edge, NOT the claimed 16u). Nudged +11.7u NE to the FINAL
  (22,45) = d=0.14u, clr 100/100/100%, comp#1, still ~110u from the NE arrival stairs = the "back
  corner" per Will's order.

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
- Helos host (`startingfarmland06d`): `svc_testhub_master_helos.dbr` at local **(64.5, 0.8, 189.5)**
  (NUDGED ~12u WEST of the canonical Almyros NPC at (76.5,0.6,189.5) for H5 click-occlusion insurance;
  the code + the gate row have always used 64.5 - this M3 body text formerly said the REJECTED 86.0
  draft, corrected in R3). Re-surveyed on the built TESTHUB: FINAL (64.5) reads d=0.00u/clr=100% in all
  3 tilesets (comp#1); the abandoned 86.0 draft read clr 10-17% in a mesh gap.
- Blood-cave mouth (`random09a` SV swap blob, applied via the swap path): `svc_testhub_master_cave.dbr`
  at local (32.0, 1.0, 45.0) (coords unchanged).
- STOPPED placing the shared `svc_testhub_master` (constant kept for reference).

DB lane owns the two split records (`_helos` / `_cave`); the quests lane owns the 3 triggers
(helos 7 ports, cave 7 ports, return 2 ports). Canonical `Levels.arc` stays byte-identical (rig is
TESTHUB-only). Warden spot on-mesh re-survey: see gates below.

---

## M1 YARD RESPACE (TESTHUB HV01, de-crowd)

Will: "pets too crowded... they all spawn on top of each other, i am dying." The old build33/35 yard
packed its groups into tight clusters (min 6.1u; the 4 Obsidian within ~6-11u). RESPACED to spread
all **10** groups across HiddenValley01's walkable valley. **R3 CORRECTION: the count is 10, NOT the
9 that R2 wrongly "corrected" to.** Re-parsed directly from the BUILT TESTHUB HV01 0x05
(`build36_map_probe.py yard`) - the 10 placed yard proxies are:

| # | proxy (`records\drxmap\proxy\...`) | local (x, y, z) |
|---|------|------|
| 0 | `q_yard_enslaver` | (33.0, 15.9, 41.0) |
| 1 | `q_yard_marauders` | (71.0, 13.5, 31.0) |
| 2 | `q_vashkarr_lone` (Vashkarr reuses its lone proxy) | (101.0, -1.5, 43.0) |
| 3 | `q_yard_dorus` (NEW build36, Drowned King) | (65.0, -10.0, 63.0) |
| 4 | `q_yard_obs_sarkoth` | (63.0, 9.9, 97.0) |
| 5 | `q_yard_obs_gorrahk` | (127.0, -2.3, 93.0) |
| 6 | `q_yard_obs_voranthys` | (157.0, -0.4, 111.0) |
| 7 | `q_yard_broodmother` | (107.0, 1.4, 123.0) |
| 8 | `q_yard_obs_ilsevar` | (71.0, 0.0, 129.0) |
| 9 | `q_yard_wyrm` | (55.0, 17.6, 157.0) |

- **10 groups** = the 9 build35 residents (enslaver, marauders, vashkarr, 4 obsidian, broodmother,
  wyrm) + the NEW `q_yard_dorus`. The TESTHUB HV01 0x05 grew 231 -> 232 (+1 = dorus) vs build35 (blob
  -diff), 0x0b navmesh byte-identical.
- **min pairwise (x,z) = 32.25u** (between `q_yard_obs_ilsevar` and `q_yard_wyrm`; was 6.1u) - a ~5x
  de-crowd. (R2 prose said "32.2u"; the precise measured value is 32.25u.)
- Every spot on-mesh in all 3 tilesets, clr@2.5 >= 91%, and in the SAME walkable component as the
  cave-mouth/camp (flood-fill verified reachable on foot).
- Lane A created `q_yard_dorus` (+ its pool = 1 um_dorus_99 king + 2 royal-guard escorts @100%);
  Vashkarr has no `q_yard_vashkarr` - the yard reuses its `q_vashkarr_lone` proxy.

**NOT DELIVERED TO THE >=60u ASK (needs Will's decision - see OPEN ITEMS #1).** The task asked for
>=60u; the shipped spacing is 32.25u. HV01's walkable footprint is a winding valley (only ~23% of its
bounding box is floor, ~4,470 sq-units). Hex-packing even 10 discs at 60u needs ~31,000+ sq-units, so
60u is geometrically IMPOSSIBLE for 10 groups here; the practical on-mesh ceiling is ~45u for the
points alone and ~32u once reachability + a clear spawn disc are enforced. 32.25u already separates
every group by ~a screen-width, which resolves the "all on top of each other" complaint. This is
TESTHUB-only (never uploaded), so there is NO shipped-artifact impact either way, but per DONE-means-
DONE it is not the literal spec. Options for Will: **(a) accept 32.25u** (recommended); **(b) reduce
to ~4-5 groups** so 60u fits (loses yard coverage); **(c) relocate the yard to a larger FLAT host**
(e.g. a Hades plain) where 60u fits all 10.

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
| det-2x (rebuild -> md5 match) | **R3: PASS (CLOSED, no longer deferred).** The build reads inputs from HARD-CODED main-repo absolute paths (`svaera_plus_portals.py:582/583` SVAERA+SV inputs; `:594` output), so running the WORKTREE code reproduces both variants byte-for-byte from the branch source. Rebuilt both from the worktree (natural, differing hash seeds - NOT PYTHONHASHSEED-pinned, so this also proves seed-independence): canonical MD5 `7b620a47f642b1fc4ec419b237291b18` == the pre-existing R2 artifact; TESTHUB MD5 `7b50fb3ac022d7602e85e6281da20a51` == the pre-existing R2 artifact. Two independent builds per variant, byte-identical. |
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

### P2 (OPEN - Will's decision) - M1 yard 32.25u vs the >=60u ask
> ⚠️ **R3 CORRECTION: this R2 paragraph's "9" count was WRONG.** The R3 vet caught it; re-parsed
> directly from the built TESTHUB HV01 0x05 the count is **10**, not 9 (R1 had 10 right; R2 mis-
> "corrected" to 9). The 0x05 grew from 231 (build35, 9 residents) to 232 (build36, +1 = the new
> `q_yard_dorus`) = 10. See the corrected M1 section above and `## ROUND 3`.

Re-verified on the built TESTHUB HV01 (R3): **10** group proxies (the 9 build35 residents + the new
`q_yard_dorus`), **min pairwise 32.25u** (between `q_yard_obs_ilsevar` and `q_yard_wyrm`) - a ~5x
de-crowd from build35's 6.1u. 60u is geometrically infeasible here (HV01's walkable valley is ~4,470
sq-units; hex-packing even 10 discs at 60u needs ~31,000+). Per DONE-means-DONE this is NOT delivered
to the literal spec and needs Will's explicit call (see OPEN ITEMS #1).

### P3 (R3: CLOSED PASS - no longer deferred) - det-2x determinism
> ⚠️ **R3 UPDATE: det-2x is CLOSED PASS, not deferred.** The R3 vet noted the build's inputs+output
> are HARD-CODED main-repo absolute paths, so the worktree code reproduces both variants byte-for-byte.
> Rebuilt both from the worktree (natural, differing hash seeds): canonical `7b620a47...` and TESTHUB
> `7b50fb3a...` each == the pre-existing R2 artifact -> two independent seed-varying builds per variant,
> byte-identical. See the det-2x gate row + `## ROUND 3`.

### Curiosity findings - disposition
1. **16u frame error in all 5 boss specs**: ⚠️ **R3 CORRECTION - this characterization was WRONG.**
   Re-surveyed on the built map in the validated frame (native Almyros reads d=0.00), 4 of the 5
   spec-primary coords are ON-mesh (M4 (52,60) d=0.14; M5 (54,114.3) d=0.10-0.50; M7 (43,71) d=0.14;
   M6 forecourt draft on-mesh low-clearance) - they were nudged only because they sit NEAR A WALL with
   a low clearance disc (M4 57/53/45%, M5 43/35/26%), NOT because of a frame error. Only M8's spec
   coord (15.9,34.7) is genuinely off-mesh, and even that is ~7.2u (comp=NONE), NOT 16u. A 4u nudge
   could never fix a real 16u error; the true cause is near-wall low-clearance (M4/M5/M6) + one real
   off-mesh coord (M8). The nudges themselves are legitimate + verified on-mesh comp#1 - only the R1/R2
   root-cause narrative was inaccurate. Lesson (unchanged): survey the BUILT map in the navmesh-origin
   frame + nudge to a high-clearance cell; never trust the specs' own clear-disc ratings.
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

1. **M1 yard >=60u (Will's decision - NOT done to literal spec).** Delivered **32.25u (10 groups**,
   all on-mesh + main-component + clr>=91%), a ~5x de-crowd from 6.1u. 60u is geometrically infeasible
   in HV01 (~4,470 sq-units of floor; ~32u is the practical ceiling once reachability + a clear spawn
   disc are enforced for 10 discs). Options: **(a) accept 32.25u** (recommended - it puts each group ~a
   screen-width apart and resolves the "all on top of each other, i am dying" complaint); (b) reduce
   the yard to ~4-5 groups so 60u fits (loses yard coverage); (c) relocate the yard to a larger FLAT
   host (e.g. a Hades plain) where 60u fits all 10. TESTHUB-only; no ship impact either way.
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
6. **det-2x** - ✅ **CLOSED (R3): PASS** (both variants rebuild byte-identical from the worktree; MD5s
   in `## ROUND 3`). No longer a convergence to-do.
7. **Apex superbosses on the MAINLINE campaign path (confirm with Will).** All 5 apex bosses are placed
   in BASE-GAME Immortal-Throne levels the player traverses during normal progression (Medea tomb,
   Styx swampborder/riveredge, Judgment mnemosyne/stonecity), i.e. mandatory-path, not hidden optional
   areas. This matches each spec's intent (Den of Tantalus / Golden Bough shrine / Dread Halls / Cave
   of Mnemosyne / Great Hall of Propontis), and each is a Boss-classification + hoard chest. Worth a
   one-line Will confirm that apex bosses gating the mainline is desired (vs tucked into optional
   pockets). No code impact; placement is correct per the specs either way.
8. **Convergence delta-vet MUST re-run `contracts_map` after the DB records merge** to confirm
   placement<->record-path parity: the 4 MAP-REF-1 P1 (q_tantalus/q_goldenbough/q_mnemophage/
   q_ephialtes_lone) are the intended "placement inert until the DB lane creates the record" state and
   WILL clear once those arz records land (q_dorus_lone + the 10 yard proxies + the 2 warden-split
   records already resolve). This is the gating follow-up before any deploy.

## ROUND 3 (vet fixes) - 2026-07-11

The R2 vet returned 3 NO_GO P2/P3 report/narrative issues (1 P2 + 2 P3), 1 informational P3, and 6
curiosity findings. **All are report-only - the map artifacts are byte-identical to R1/R2** (det-2x
proved it). NO map-generation code changed this round; R3 added one read-only probe
(`tools/debug/build36_map_probe.py`) and corrected this report.

### Fixes applied
1. **(P2) M1 yard count 9 -> 10 (the false "independently re-verified: 9").** Re-parsed the built
   TESTHUB HV01 0x05 directly (`build36_map_probe.py yard`): **10** proxies (table in the M1 section),
   **min pairwise 32.25u** between `q_yard_obs_ilsevar` and `q_yard_wyrm`. build35 had 9 (0x05=231);
   build36 = 10 (0x05=232, +1 = `q_yard_dorus`). R1 had 10 right; R2 mis-"corrected" to 9. Corrected
   in the M1 section, the R2 P2 disposition, the OPEN ITEMS, and the header. (The artifact was always
   correctly spaced - only the prose was wrong.)
2. **(P3) M3 Helos warden coord 86.0 -> 64.5.** The M3 body text still quoted the REJECTED 86.0 draft;
   the code (`build_section_surgery.py:2157`) and the gate row have always used the correct 64.5.
   Re-surveyed on the built TESTHUB: 64.5 reads d=0.00/clr=100% all 3 tilesets (comp#1); the 86.0 draft
   reads clr 10-17% (a mesh gap). Corrected in the M3 section.
3. **(P3) "16u frame error in all 5 specs" narrative.** Re-surveyed on the built map: 4/5 spec-primary
   coords are ON-mesh (M4 d=0.14, M5 d=0.10-0.50, M7 d=0.14, M6 forecourt low-clr) - nudged for
   near-wall LOW CLEARANCE, not a frame error; only M8 (15.9,34.7) is genuinely off-mesh (~7.2u,
   comp=NONE, NOT 16u). Corrected in the re-survey-findings section + the R2 curiosity #1 disposition.
4. **(P3, informational) M2 blue-box correctly NOT actioned.** Confirmed no action required: the
   concrete M2 target (the old walk-through GridEntrance hub) is already removed (random09a +
   startingfarmland06d have 0 gridentrance/portal-hub 0x05 in the TESTHUB); the remaining
   portal_olympianarena/portal_master content panels are the B-PORTAL lane's give-them-mesh/FX scope,
   NOT blind removal. Left as OPEN ITEM #2 for Will to point at any specific in-game artifact.

### Determinism (curiosity #1 -> CLOSED PASS)
Confirmed the build reads inputs + writes output from HARD-CODED main-repo absolute paths
(`svaera_plus_portals.py:582-583` inputs, `:594` output), so the WORKTREE code reproduces both
variants byte-for-byte. Rebuilt both from the worktree with natural (differing) hash seeds (proving
seed-independence, not just PYTHONHASHSEED-pinned reproducibility):

| variant | pre-existing R2 artifact MD5 | fresh worktree rebuild MD5 | size (B) | result |
|---|---|---|---|---|
| canonical | `7b620a47f642b1fc4ec419b237291b18` | `7b620a47f642b1fc4ec419b237291b18` | 688,690,448 | **MATCH** |
| TESTHUB | `7b50fb3ac022d7602e85e6281da20a51` | `7b50fb3ac022d7602e85e6281da20a51` | 688,689,512 | **MATCH** |

Two independent builds per variant, byte-identical -> det-2x PASS, CLOSED (P3 no longer deferred).

### Full gate battery re-run (R3, on the freshly-rebuilt maps)

| Gate | Result |
|---|---|
| det-2x canonical (run1 == run2) | **PASS** `7b620a47...` |
| det-2x TESTHUB (run1 == run2) | **PASS** `7b50fb3a...` |
| verify_merged_bc_navmeshes (canonical) | **PASS 24/24** (0x0a stripped) |
| seam_lattice_check --gate (canonical) | **PASS** 24 aligned seams, 0 misaligned |
| entrance_landing_check --check-merged | **PASS** G2 (DONOR+MERGED both 508 cells, dY +0.00u) |
| Boss placement survey (built map, 3 tilesets) | **PASS** all 5 on-mesh comp#1: M4 97/95/94 · M5 96/94/92 · M6 100/100/100 · M7 97/97/94 · M8 100/100/100 (clr @ placementExtents; d<=0.14u) |
| contracts_map (canonical, my R2 door-scope fix) | **PASS** 7 viol / 0 P0 / **4 P1 = the expected MAP-REF-1** (q_goldenbough/q_tantalus/q_mnemophage/q_ephialtes not-yet-in-arz) + 3 pre-existing native portal P2s; **0 MAP-DOOR-1** (Tomb01 xsq06 doors correctly excluded) |
| contracts_map (TESTHUB) | **PASS** identical: 7 viol / 4 P1 (same MAP-REF-1); yard + warden-split records resolve |
| _negtest_map.py | **PASS 25/25** (incl. "REF-1 fires on unresolved SV placed record" + "REF-1 does NOT fire on non-SV base record (scope guard)") |
| Canonical blob-diff vs build35 | **PASS** EXACTLY 5 blobs (the 5 boss hosts), each 0x05 +1, EVERY 0x0b byte-identical, 0 added/removed |
| TESTHUB blob-diff vs build35-TESTHUB | **PASS** EXACTLY 8 blobs (5 boss hosts + HV01 yard 231->232 + 2 warden hosts 997/108 count-unchanged), all 0x0b byte-identical |
| Yard count/spacing (built TESTHUB) | **10** proxies, min pairwise **32.25u** |
| Warden Helos on-mesh (built TESTHUB) | **PASS** FINAL (64.5,189.5) = d=0.00/clr=100% all 3 tilesets, comp#1 |

### Curiosity findings - R3 disposition
1. **det-2x satisfiable now** -> CLOSED PASS (above). ✅
2. **All 5 boss proxies are `records\drxmap\proxy\q_*_lone`** (each injects `drxmap` into a BASE host
   blob) -> the R2 record-namespace door-scope fix is correctly BROAD (not just Tomb01). Confirmed:
   contracts_map on the built map fires 0 MAP-DOOR-1 across all 5 hosts (no xsq06-style false
   positives), and _negtest's scope-guard check passes. ✅ (verifies the R2 fix generalizes).
3. **Apex bosses on the mainline campaign path** -> OPEN ITEM #7 (one-line Will confirm; placement is
   correct per the specs either way).
4. **M7 task-prompt coord `(54,-15.2,114.3)` is a copy-paste of M5's local coord (typo).** The real
   `mnemosyne_uberboss_spec.md` PRIMARY `(43,3,71)` was followed and needs no nudge (d=0.14, clr
   97/97/94, comp#1). Not an implementer error; noted in the re-survey findings + M7 row.
5. **Two survey tools diverge sub-1u** (spec navlib vs `survey_uberboss_spots.py`) on the clearance
   metric, which is why the specs over-rated their primaries' clear discs. Both agree the FINAL
   placements land on-mesh comp#1 (what matters). The larger M8 divergence (~7u) is the one genuinely
   off-mesh spec coord, not a tool disagreement. Noted.
6. **4 MAP-REF-1 P1 = intended placement-inert state** -> OPEN ITEM #8 (convergence MUST re-run
   contracts_map after the DB records merge to confirm placement<->record-path parity before deploy).
