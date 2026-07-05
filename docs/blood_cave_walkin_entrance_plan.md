# Blood-Cave Walk-In Entrance - Implementation-Ready Plan

Replace the broken boat-dialog/quest teleport with the ENGINE-NATIVE walk-in path
that classic Soulvizier used. Every load-bearing claim below is byte-verified against
`reference_mods/SVAERA_customquest/Resources/Levels.arc` (the merge base) and
`upstream/soulvizier_098i/Resources/Levels.arc` (SV). Do NOT run the multi-GB build to
follow this plan; the analysis is done.

---

## CORRECTION (2026-07-05) - the "overlap-at-different-Y is safe" assumption was WRONG for the transition DESTINATION

Section 3 concluded that Random09A's XZ-overlap with three live surface levels
(HighAltituedBorder01, HiddenValley01, HiddenValleyBorder05) was cosmetic, citing 12
shipping precedents that overlap in XZ at large |dY|. That reasoning is correct for
generic level pairs, but it does NOT hold for a cave that is the DESTINATION of a
surface->cave transition. In-game, the player reached the HiddenValley01 cave mouth
but hit an invisible wall AT the opening (the transition was refused).

Diagnosis (Engine.dll disassembly + working-cave survey, medium-high confidence):
TQAE cave mouths are portal coordinate-bridges (`GetConnectedRegion` resolves the
destination by RegionId GUID; no surface<->interior adjacency is needed), and every
WORKING base-game cave interior is parked fully DISJOINT from any surface region
(~1700u away; edge-touch with zero area is fine). The relocated Random09A at corner
`(-198,18,2135)` was the ONLY cave in the merged map whose 80x80 footprint
AREA-overlapped live surface levels (HighAltituedBorder01 5120 sq u, HiddenValley01
656, HiddenValleyBorder05 624). That unique co-residency is the diagnosed cause of
the refused transition. The surface `0x14` mouth binding, reciprocal `0x06` pairing,
and the generated `0x0b` navmesh were all byte-verified INTACT and are not the fault.

New placement (implemented): shift the ENTIRE xBloodCave cluster AND Random09A by the
same new total shift **`GRID_SHIFT = (1583, 0, 968)`** (the old `(1663,0,922)` plus an
extra `dx=-80, dz=+46`). Random09A's footprint becomes corner **`(-278, 18, 2181)`**,
X[-278,-198] Z[2181,2261], which has **zero area overlap with every non-cluster level**
(it only edge-touches HighAltituedBorder01 at x=-198, zero area, which working caves do
too). Because Random09A and xPassageTransitionStart move together, their navmeshes stay
aligned: the R09<->xPTS walkable grid-seam intersection is shift-invariant at **~73.4
world-u** (>> the ~4u needed for the tunnel hand-off). Both `GRID_SHIFT` keys carry the
identical delta; `gen_bc_navmeshes.py` imports the dict, so the donors follow. The
Section 2/3 "abut at x=-198 / (1663,0,922)" numbers below are SUPERSEDED by this block;
read them as the historical placement, not the shipped one.

---

## 0. TL;DR - the mechanism, proven

TQAE has **no portal entity** for surface->cave. The cave "mouth" is a `GridEntrance`
actor = **pure terrain-mesh art with zero destination fields** (all 153 base-game
`GridEntrance` records carry only `mesh`/`scale`/render flags). The surface->cave LINK is
the destination level's **16-byte GUID stored in the placing level's `0x14` metadata**,
next to that entrance entity. The engine streams in the GUID-named level when the player
walks onto the mouth tile. 150 base surface levels use exactly this pattern.

For the Silk Road cave specifically (byte-proven):
- `HiddenValley01` (the level the player is already at) places
  `Records/Underground/NaturalCave/Orient/SilkRoad/SilkRdDngEntrance_C01_Ext.dbr`
  (Class `GridEntrance`) at **local (14,18,26)** as instance #30 in its `0x05` list.
- `HiddenValley01`'s `0x14` record #30 (60-byte payload) carries **Random09A's GUID**
  at payload offset 44 (`d840e7ae4a42c504453f13a47940bc55`). That is the destination link.
- The base game's Random09A is a tiny isolated Silk-Road cave island (corner (-923,0,625)).
- **Soulvizier hijacked this cave**: SV's Random09A (285,795 B vs AE's 105,564 B) adds a
  WEST tunnel + blood-cave dressing, and re-points its own `0x0a` grid-edge so its only
  neighbor is `xPassageTransitionStart`. Chain (all `0x0a` grid edges, verified):
  `Random09A --west--> xPassageTransitionStart --> BC_initialpathway --> drxFirstxistion_connection --> drxFirstRoom --> cave`.
- The return exit is reciprocal: SV-Random09A embeds `HiddenValley01`'s GUID in its `0x06`
  section (kept intact by the swap; only `0x0a` is stripped).

This is exactly what Will remembers: enter the normal Silk Road cave, take the added
left/west tunnel into the blood cave. No quest system, no dialog, no teleport.

**RECOMMENDATION: Option B (relocated SV-Random09A blob swap) is PRIMARY.** It is the
authentic SV mechanism, engine-native, quest-independent, and (proven below) collision-safe
and navmesh-feasible. The `GridEntrance`-injection-into-HiddenValley01 idea (old option (a))
is NOT a separate mechanism - the `GridEntrance` mouth ALREADY exists in HiddenValley01 and
ALREADY points at Random09A's GUID; there is nothing to add on the surface side. Option (a)
therefore collapses into Option B. It is retained only as a fallback lever (Section 8) if the
walk test shows the mouth binding was lost.

---

## 1. Mechanism comparison

| Option | Verdict |
|---|---|
| **(B) Relocated SV-Random09A blob swap** (PRIMARY) | Swap SVAERA's Random09A blob for SV's (both LVL v0x0e -> the v0e/v11 format-crash mode does NOT apply), positioned so its WEST edge abuts the shifted xPassageTransitionStart. Keep AE's GUID in the LEVELS index. Authentic, engine-native, quest-free. All load-bearing facts verified GO. |
| **(a) Inject a GridEntrance cave-mouth into HiddenValley01** | NOT NEEDED / NOT A WARP. `GridEntrance` has no target field; the mouth+GUID-binding already exist in HiddenValley01 pointing at Random09A. Nothing to inject on the surface. Kept only as a fallback to RE-CREATE the `0x14` GUID binding if it turns out damaged (Section 8). |
| **(c) Grid-adjacency connector without the swap** | Infeasible cleanly: the player enters Random09A by GUID (the mouth), not by walking a surface grid edge, so a bare connector never gets reached. You must occupy the Random09A slot. That IS Option B. |

---

## 2. Exact implementation (Option B)

### 2.1 What changes, in one sentence
In the merged LEVELS index, the `Random09A` entry keeps SVAERA's **GUID, filename, and
DATA2/bitmap wiring**, but its **blob pointer + ints_raw grid corner** become SV's blob
(with its west tunnel) shifted by `(1663,0,922)`, and its `0x0a` is replaced by a
freshly generated `0x0b` navmesh (own-GUID = AE's GUID, neighbor = xPassageTransitionStart).

### 2.2 Coordinates (SCALE = 2 world-units/tile, verified)
- SCALE proof: `HiddenValley01` corner (-134,2174), 64 tiles wide; its east neighbor
  `hiddenvalleyborder01` corner (-6,2174) => dCornerX=128 = 64*2. Both axes confirmed.
- SV-Random09A dims: 40x40 tiles => 80x80 world units.
- **Placement (Option A shift, uniform with the rest of xBloodCave): corner
  `(-198, 18, 2135)`**, spanning **X[-198,-118] Z[2135,2215] Y=18**.
  - Its WEST edge x=-198 exactly meets shifted-xPTS EAST edge x=-198, Z overlap = 80 (full
    tile width). ABUT confirmed.
  - This is the SAME `(1663,0,922)` shift already applied to the xBloodCave cluster, so
    it is the single-source-of-truth GRID_SHIFT with a new pattern key (below).

### 2.3 GUID strategy (decisive)
Keep **AE-Random09A's GUID** in the merged LEVELS index for the Random09A slot. Then:
1. `HiddenValley01`'s cave-mouth `0x14` binding (points at AE's GUID) still resolves ->
   player still enters. No change to HiddenValley01 at all.
2. `xPassageTransitionStart`'s already-generated `0x0b` lists AE-Random09A's GUID as its
   neighbor (gen_bc_navmeshes.resolve_guids remapped SV->AE). Keeping AE's GUID means
   **xPTS needs NO navmesh regen**.
3. SV-Random09A's blob is GUID-agnostic once `0x0a` is stripped: its own SV GUID appears
   ONLY in `0x0a` (count=1; stripped). Sections `0x05/0x06/0x09/0x14/0x17` carry zero
   own-GUID bytes, so the index carrying AE's GUID creates no internal mismatch.
4. The `0x06` reciprocal return-link embeds `HiddenValley01`'s GUID, which is IDENTICAL in
   SV and AE (shared level, same GUID `ce93e328...`), so the cave->surface return resolves.

### 2.4 Destination spawn
There is no named spawn-proxy record. The player materializes at Random09A's grid-entrance
tile geometry (editor-placed terrain), same for AE and SV blobs. The swap does not change
where the player arrives; SV simply added the west tunnel leading onward. No proxy to add.

### 2.5 Quest wiring
NONE. Remove the boat-dialog portal entirely (Section 6.4). No one-line Action is required.

---

## 3. Collision check (math shown)

Footprint = corner + (tile_dims * 2). Overlap = positive area on both X and Z.

Shifted SV-Random09A **X[-198,-118] Z[2135,2215] Y=18** vs every SVAERA level:
- **Abuts** shifted xPassageTransitionStart (X[-358,-198] Z[2135,2263]) on its west edge,
  Zov=80. This is the intended connection. GO.
- **XZ-overlaps 3 surface levels**, all at large |dy| (cave Y=18 vs surface ~Y=-100):
  - `highaltituedborder01` X[-198,-134] Z[2135,2263] Y=-98 (dy=116)
  - `hiddenvalley01` X[-134,-6] Z[2174,2302] Y=-120 (dy=138)
  - `hiddenvalleyborder05` X[-134,-6] Z[2110,2174] Y=-104 (dy=122)

**Is XZ-overlap-at-different-Y safe? YES, proven from shipping data.** The pristine SVAERA
map contains **117 XZ-overlapping level pairs, 12 of them at |dy|>40** (e.g.
`upperhalls01`/`dhbackdrop01`, `mines02`/`dhbackdrop03`, `tombnat04`/`transitionpiece02`).
The engine streams by GUID/grid-edge, not by world-XZ occupancy, so overlap at a different Y
is cosmetic. Critically, SV-Random09A's ONLY grid neighbor is xPTS (not any surface level),
so no gameplay path is created between the overlapping levels - the player cannot walk from
HiddenValley01 into the cave except through the GridEntrance mouth.

**Zero-overlap alternative (documented, NOT recommended): Option-B-Z** = shift `(1663,0,850)`
-> corner (-198,18,2063), still abuts xPTS but Zov drops to 8 (too thin for a reliable
walkable tunnel) and still overlaps 2 borders (1040 sq units). Not worth it; use the uniform
`(1663,0,922)` shift.

---

## 4. Navmesh

Levels needing a `0x0b` (re)generation for the entrance path:
- `xPassageTransitionStart`, `BC_initialpathway`, and the rest of the xBloodCave chain:
  **already generated** (`local/editor_normalized/*.0b.bin`, 23 donors). **No change.**
- **`Random09A` is NEW work.** It currently ships `0x0a` only. Generation is proven
  feasible: `extract_mesh` OK, `generate()` -> **37 tiles**, base center (-1813,24,1261).
  With own-GUID forced to AE-Random09A and neighbor xPTS, `resolve_guids` yields exactly
  `[AE-Random09A, xPassageTransitionStart]`, **0 dropped**, shifted center **(-150,24,2183)**,
  78,918-byte `0x0b`, 3 sets, byte-exact round-trip. GO.

`tools/gen_bc_navmeshes.py` produces it, but the driver currently iterates ONLY xBloodCave
levels and derives own-GUID from the level's own ints_raw. Two precise changes (Section 6.3):
(1) add Random09A (from Orient/Underground, upstream SV) to the batch; (2) pass AE-Random09A's
GUID as the `own_guid` so the donor's own GUID matches the kept index GUID.
Output donor: `local/editor_normalized/Random09A.lvl.0b.bin`.

---

## 5. GUID resolution in the merged world

- `merged_guids` (gen_bc_navmeshes.build_merged_guid_map) = every SVAERA GUID + every
  SV-only GUID. AE-Random09A's GUID is already in it (it is a SVAERA level we keep).
- The swap does NOT add a new level or GUID; it replaces a blob in-place, so the level count
  and GUID set are unchanged. ProcessRLTD's per-section GUID gate for:
  - HiddenValley01 mouth -> AE-Random09A GUID: resolves (unchanged).
  - xPTS `0x0b` neighbor -> AE-Random09A GUID: resolves (unchanged, no regen).
  - New Random09A `0x0b`: own=AE GUID (resolves), neighbor=xPTS GUID (resolves). 0 dropped.
- `shared_remap` already maps SV-Random09A GUID -> AE-Random09A GUID (differing-GUID shared
  level), so even neighbor references from other levels that named the SV GUID would remap.

---

## 6. Exact edits, file by file

### 6.1 `tools/svaera_plus_portals.py` - the blob swap (primary change)

**(a) Extend GRID_SHIFT** so Random09A shifts with the cluster (single source of truth):
```python
GRID_SHIFT = {
    'xbloodcave': (1663, 0, 922),
    'orient/underground/random09a': (1663, 0, 922),  # relocate the hijacked Silk Road cave
}                                                    # so its west edge abuts shifted xPTS
```
Note `shifted_ints_raw` / `grid_shift_for` match by substring, so key
`'orient/underground/random09a'` hits only Random09A (path is
`Levels/World/Orient/Underground/Random09A.lvl`).

**(b) Add a shared-level BLOB SWAP.** The live builder currently keeps SVAERA's blob for
every shared level (it only appends SV-only levels). Add an explicit swap for Random09A that
KEEPS AE's index identity (GUID, fname, DATA2/bitmap) but takes SV's blob + shifted corner +
generated `0x0b`. Concretely, in `main()` after `ae_levels`/`sv_levels` are parsed and before
the DATA section is compacted (step 8):

```python
# --- Blood-cave walk-in: swap SVAERA's Random09A blob for SV's (west tunnel) ---
# Keep AE's GUID/fname/bitmap (index identity) so HiddenValley01's cave-mouth 0x14
# binding + xPTS's navmesh neighbor list still resolve. Take SV's blob (adds the west
# tunnel + the 0x0a edge to xPassageTransitionStart), shift its grid corner by
# GRID_SHIFT, strip 0x0a, inject the pre-positioned generated 0x0b (own-GUID = AE's).
R09_KEY = 'levels/world/orient/underground/random09a.lvl'
ae_r09_idx = ae_by_name[R09_KEY]
sv_r09_idx = sv_by_name[R09_KEY]
sv_r09 = sv_levels[sv_r09_idx]
sv_r09_blob = sv_data[sv_r09['data_offset']:sv_r09['data_offset'] + sv_r09['data_length']]

# Shifted grid corner, but carry AE's GUID (ints_raw[9..12]) so the index identity is AE's.
swapped_ints = bytearray(shifted_ints_raw(sv_r09))          # SV dims + shifted corner
swapped_ints[36:52] = ae_levels[ae_r09_idx]['ints_raw'][36:52]  # keep AE GUID
# Inject the pre-positioned generated 0x0b (Random09A.lvl.0b.bin) and strip 0x0a.
gen_0b, gen_path = find_pre_positioned_donor(sv_r09)        # basename Random09A.lvl -> .0b.bin
assert gen_0b is not None, 'Random09A.lvl.0b.bin donor missing - run gen_bc_navmeshes.py'
swapped_blob = inject_rec02_into_blob(sv_r09_blob, bytes(swapped_ints),
                                      donor_data=gen_0b, use_stub=False, pre_positioned=True)

# Overwrite the merged Random09A entry in-place (index identity stays AE's).
merged_levels[ae_r09_idx]['ints_raw'] = bytes(swapped_ints)
# Record the swapped blob so the DATA-compaction loop writes it instead of SVAERA's.
_r09_swap = (ae_r09_idx, swapped_blob)
```
Then, in the DATA-compaction loop over SVAERA levels (the `for i in range(len(ae_levels))`
block that fills `compacted_data`), use the swapped blob for that index:
```python
for i in range(len(ae_levels)):
    if i in ae_patched_blobs:
        blob = ae_patched_blobs[i]
    elif _r09_swap and i == _r09_swap[0]:
        blob = _r09_swap[1]                 # SV blob + shifted corner + generated 0x0b
    else:
        lv = ae_levels[i]
        blob = ae_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    merged_levels[i]['data_offset'] = data_start + len(compacted_data)
    merged_levels[i]['data_length'] = len(blob)
    compacted_data += blob
```
Leave `merged_bitmaps[ae_r09_idx]` (SVAERA's minimap TGA) untouched - it is cosmetic and
still valid. Do NOT append SV-Random09A as an extra level; it stays a single in-place swap so
the level count/GUID set are unchanged.

NOTE: The `build_section_surgery.py` `perform_section_surgery` "use_sv_blob" path (lines
~601-629) is dead in the live pipeline (only `build_section_surgery.main()` calls it, which
`svaera_plus_portals.py` does not use). Do NOT try to revive it - it neither keeps AE's GUID
nor injects the generated `0x0b`. The explicit swap above is the correct route.

### 6.2 `tools/build_section_surgery.py` - remove the HiddenValley01 portal NPC inject

In `INJECT_SPECS` delete the HiddenValley01 entrance-NPC injection (the walk-in path needs no
NPC on the surface):
```python
INJECT_SPECS = {
    'levels/world/uberdungeon/crypt_floor1.lvl': [ (RETURN_NPC_DBR, 140.0, 10.0, 215.0) ],
    # REMOVED: 'levels/world/orient/silkroad/hiddenvalley01.lvl': BLOODCAVE_ENTRANCE_NPC_DBR
    # REMOVED: 'levels/world/xbloodcave/bc_initialpathway.lvl':   BLOODCAVE_RETURN_NPC_DBR
}
```
(Leave the uber-dungeon crypt entry unless that portal is also being retired - out of scope
here.) No other change to this file; `inject_rec02_into_blob(..., pre_positioned=True)` already
handles the Random09A donor exactly as it does the xBloodCave donors.

### 6.3 `tools/gen_bc_navmeshes.py` - generate Random09A's donor

The batch currently = xBloodCave levels only, own-GUID from ints_raw. Add Random09A with the
AE-GUID override. Minimal, surgical:

**(a)** After building the xBloodCave list `bc`, append Random09A (from the SAME upstream SV
map already loaded as `sv_levels`) and record the GUID override:
```python
# Relocated Silk Road cave (blood-cave walk-in). Not under xBloodCave; add explicitly.
R09_KEY = 'levels/world/orient/underground/random09a.lvl'
sv_r09 = next(lv for lv in sv_levels
              if lv['fname'].replace('\\', '/').lower() == R09_KEY)
bc.append(sv_r09)
# Own-GUID override: the merge keeps SVAERA's Random09A GUID in the index, so the donor's
# own GUID must be AE's, not SV's.
ae_data2, ae_levels2 = _load_map(SVAERA_ARC)
AE_R09_GUID = next(lv['ints_raw'][36:52] for lv in ae_levels2
                   if lv['fname'].replace('\\', '/').lower() == R09_KEY)
OWN_GUID_OVERRIDE = {R09_KEY: AE_R09_GUID}
```
**(b)** In the per-level loop, use the override for `own_guid` and make `grid_shift_for` cover
Random09A (it reads `GRID_SHIFT`, so the 6.1(a) key addition already makes it shift). Replace:
```python
own_guid = lv['ints_raw'][36:52]
```
with:
```python
key = lv['fname'].replace('\\', '/').lower()
own_guid = OWN_GUID_OVERRIDE.get(key, lv['ints_raw'][36:52])
```
`resolve_guids(guids_0a, own_guid, merged_guids, shared_remap)` then puts AE's GUID first and
keeps xPTS; `grid_shift_for(fname)` returns (1663,0,922) for Random09A via the new GRID_SHIFT
key; output lands at `local/editor_normalized/Random09A.lvl.0b.bin`. (Verified: 37 tiles,
center (-150,24,2183), 0 dropped, round-trip OK.)

Run once: `py tools/gen_bc_navmeshes.py` (regenerates all donors incl. the new Random09A).

### 6.4 `tools/build_quest_files.py` - remove the dead portal teleport

Delete the blood-cave portal from the combined portal quest so no fragile OnLevelLoad/
BoatDialog step drives entry:
- Remove both blood-cave tuples from `PORTALS` (lines ~66-69), leaving only the uber-dungeon
  portal if that mechanism is still wanted; if `PORTALS` becomes empty, guard
  `_make_combined_portal_quest`/the `sv_commonmechanics` replacement so an empty quest is not
  written (or keep the uber-dungeon portal there).
- The blood-cave INTERIOR questline (`open_bloodcave_portal.qst`) and its
  `_neutralize_bloodcave_entry_step` stay AS-IS - they are the in-cave content, not the
  entrance, and still resolve (the neutralized `starting_storyteller` trigger was the OLD
  terrain-doorway NPC; the walk-in path does not reintroduce it).
- `BC_INITIAL_*` / `HIDDENVALLEY01_*` constants become unused once `PORTALS` drops them;
  delete them to avoid dead code.

### 6.5 `tools/build_svc_database.py` - drop the portal NPC records (optional cleanup)

`create_blood_cave_portal` (lines ~1293-1322) creates `portal_bloodcave_entrance/return.dbr`.
With the walk-in path these are unreferenced. Either delete the call at line 1411 (and the
function) or leave it - the records are harmless dead weight if nothing injects/quests them.
Recommended: delete the call + function for cleanliness. Do NOT touch
`create_uber_dungeon_portal` unless retiring that portal too.

### 6.6 No new DBR is required
Option B needs NO new cave-mouth DBR and NO new spawn-proxy DBR: the `GridEntrance`
(`SilkRdDngEntrance_C01_Ext.dbr`) already exists in the base game and is already placed +
GUID-bound in HiddenValley01. All 49 of SV-Random09A's placed entity records already resolve
(base game + built mod; 0 missing, verified), so the swap spawns no missing-record entities.

---

## 7. The one uncertainty only an in-game walk test resolves

Whether the regenerated `Random09A` `0x0b` navmesh makes the **west tunnel actually walkable
end-to-end** and the player can path from the Silk-Road cave entrance, through the tunnel,
across the grid seam into `xPassageTransitionStart`, and on into the blood cave - i.e. that
the offline-rasterized navmesh covers the tunnel corridor at the correct floor height and the
grid-edge hand-off streams cleanly. The GUID resolution, collision, abutment, blob format, and
navmesh generation are all statically verified; the click-to-move traversal across the newly
generated mesh + grid seam is the sole thing static analysis cannot confirm.

Fallback levers if the walk test shows a gap: (1) the documented navmesh area-flag flip /
erosion fallbacks (CLAUDE.md map section) applied to Random09A's donor; (2) verify the seam by
nudging the shift so xPTS and Random09A overlap by a tile rather than merely abut; (3) Section
8 mouth-rebind fallback if entry into Random09A itself fails.

---

## 8. Fallback: re-create the GridEntrance -> Random09A binding (only if entry fails)

If the walk test shows the player cannot even ENTER Random09A (the mouth binding got lost),
re-create it on the surface side (this is the salvaged "option (a)"):
- Confirm `HiddenValley01`'s `0x05` still has `SilkRdDngEntrance_C01_Ext.dbr` at local
  (14,18,26) and its `0x14` record still carries AE-Random09A's GUID at payload offset 44.
- If missing, inject the `GridEntrance` into `HiddenValley01`'s `0x05` at (14,18,26) and append
  a `0x14` record for that instance whose payload embeds AE-Random09A's GUID (mirror the base
  game's 60-byte record: `flags(2),0,1,<link GUID @28>,<Random09A GUID @44>`). This needs a new
  `0x14`-writer that appends a GUID-list payload rather than the default 20-byte payload.
- This is engine-native (same `GridEntrance` + `0x14`-GUID mechanism), still quest-free.

---

## Appendix: verification scripts (scratchpad)

All under the session scratchpad; re-runnable with `py`, `PYTHONIOENCODING=utf-8`:
- `check_dyngrid.py`, `parse_edges.py` - grid-edge chain + SV-vs-AE Random09A diff.
- `adjacency_full.py`, `scale_probe.py`, `collision_v2.py`, `placement_options.py` - SCALE=2,
  footprints, abutment, collision, placement options.
- `overlap_semantics.py` - 117 shipping XZ-overlaps (12 at |dy|>40) prove overlap-at-Y is safe.
- `surface_entrance_hunt.py`, `verify_0x14_link.py`, `spawn_proxy.py` - HiddenValley01 is the
  sole referrer; the `0x14` #30 GUID binding; no separate spawn proxy.
- `guid_embed.py`, `r09_gen_final.py`, `reciprocal_check.py`, `entity_sanity.py` - GUID
  strategy, navmesh gen with AE-GUID override (37 tiles, 0 dropped), `0x06` return link kept,
  all 49 entities resolve.
