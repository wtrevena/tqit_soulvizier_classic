# Cave-Graft Completeness Audit (adversarial, derive-from-bytes)

Date: 2026-07-05. Auditor: independent completeness audit (Fable-max), separate from all
prior implement/vet agents. Mandate: assume the blood-cave walk-in graft is INCOMPLETE,
derive what a working cave mouth->destination REQUIRES from the game's own working data,
and verify the deployed build against every derived requirement.

## 0. Verdict in one paragraph

The graft itself is byte-complete: every property that the engine reads on the
mouth->destination path was verified against 297 working destination caves, 345 working
mouth records, and 2214 shipping navmeshes, and the deployed Random09A swap conforms to
the working population on all of them (within the variance the base game itself ships).
The two in-game failures are therefore NOT explained by any missing/stale byte in the
destination level, and the leading placement theory behind the staged third relocation
(destination must be far from the surface) is REFUTED by the game's own data: pristine
SVAERA ships working mouths whose destinations are 69 to 120 world-units away, including
one at 69u with dy=0. The audit found four CONFIRMED defects elsewhere (SD section
regression, GROUPS regression, append-clone GUID defect, and a live donor-dir/GRID_SHIFT
desync that the size-only verifier cannot catch), plus a short ranked list of remaining
blocker candidates with a decisive discriminating experiment for the top one.

## 1. What was audited (exact build identity)

- Deployed map: `C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal
  Throne/CustomMaps/SoulvizierClassic/Resources/Levels.arc`, 683,966,038 B, mtime
  2026-07-05 13:22. world01.map decompressed = 2,085,541,717 B, 2282 levels.
  This is the GRID_SHIFT (1583,0,968) build: swapped Random09A at index 703, corner
  (-278,18,2181), AE GUID d840e7ae4a42c504453f13a47940bc55 kept, blob 129,450 B.
- Pristine SVAERA: `reference_mods/SVAERA_customquest/Resources/Levels.arc`
  (world01.map 2,009,183,713 B, 2235 levels). Random09A idx 703, corner (-923,0,625),
  blob 105,564 B.
- Upstream SV 0.98i: `upstream/soulvizier_098i/Resources/Levels.arc` (world01.map
  929,978,080 B, 1004 levels). Random09A idx 977, corner (-1861,18,1213), GUID
  fba9390d3c447c7ed101c2b11cf65111, blob 285,795 B.
- Analysis scripts: session scratchpad `audit/ax_*.py` (extractor, blob dissector,
  navmesh comparator, exemplar derivation, whole-map invariant sweep).

## 2. Derived requirements: what a WORKING cave destination actually has

Derived from every mouth pair in pristine SVAERA (345 0x14 GUID-bearing mouth records,
297 unique destination levels), not from any prior agent's notes.

### 2.1 The mouth binding (surface side)
- The surface level's 0x14 section carries one record per placed 0x05 instance; the
  cave-mouth record attaches to the GridEntrance ENTITY instance (record index == 0x05
  instance index).
- v0x11 record payload = 60 B: 12-byte prefix (2,0,1) + mouthPortalUniqueId GUID @12 +
  exitPortalUniqueId GUID @28 + destination level GUID @44.
- v0x0e record payload = 48 B: the same three GUIDs at 0/16/32 with no prefix. The TQAE
  engine supports BOTH: the pristine SVAERA map ships 50 such v0x0e mouth records.
- The mouth entity's position is LEVEL-LOCAL (HiddenValley01 inst#30
  `SilkRdDngEntrance_C01_Ext.dbr` at local (14,18,26); world = corner + local =
  (-120,-102,2200)).

### 2.2 The destination level (what the engine needs inside the blob)
Statistics over the 297 working destinations:
- Level format: v0x0e 121, v0x11 108, v0x0f 68. All three work as destinations.
- 0x14 section: 188/297 have ZERO records (empty 0x14 is the NORM for pure caves).
  No destination carries a reciprocal 0x14 GUID record. The reverse binding does NOT
  live in 0x14.
- 0x06 (GridSystem section) is the destination-side binding. Layout (Random09A, 809 B):
  header (1,2,1,0x2d1) + gridsystem DBR string (`Records/Underground/NaturalCave/
  Orient/SilkRoad/SilkRoadCave.dbr`) + grid dims (10,1,10) + fine flag grid
  ((2w+1)x(2h+1) bytes) + per-cell u16 grid (w*h) + PORTAL-LINK TRAILER.
  Trailer (72 B for one link; 201/297 destinations have exactly this): prefix (2,64,1),
  then exitPortalUniqueId + mouthPortalUniqueId + SURFACE level GUID, then (K,0,M)
  where (K,M) = the door grid cell (col,row). Validated on two independent pairs:
  Random09A (K=8,M=2 -> local x[64,72] z[16,24], walkable in its navmesh) and
  RandomIce03D (K=5,M=6 -> local x[43,52] z[48,56], walkable, 1074 cells).
- 0x05 entity positions are LEVEL-LOCAL, byte-proven: AE Random09A (corner -923,0,625)
  and SV Random09A (corner -1861,18,1213) carry shared entities at IDENTICAL float
  positions (e.g. rootcluster01 (42.80,1.00,51.89), fungiwall03 (17.11,0.13,8.49),
  cavewater02trickling (13.92,1.00,15.06)). There is NO door/portal/entrance ENTITY in
  a destination cave; the exit portal is grid-derived (0x06 trailer + door cell).
- NO absolute world coordinate exists anywhere in a destination blob outside the 0x0b
  header center: 0x06 contains no floats at all (grids + GUIDs only); 0x09 (present in
  52/297 destinations) is (id,2,0,0,0,0), non-positional; 0x17 contains resource hashes
  (16-byte values that match NO level GUID), byte-identical between SV-original and
  deployed-shifted copies of the same level.
- Navmesh 0x0b: present in ALL 297 (and in 2214/2235 SVAERA levels); 0x0a absent in all.
  GUID list = own GUID + spatially adjacent geometry neighbors ONLY. The working
  Random09A's list = {own} alone; HiddenValley01's = {own + 6 abutting surface levels}.
  The portal-connected region is NOT in the navmesh GUID list on either side (the
  pristine HV01 list does NOT contain Random09A). Every GUID in every list must resolve
  in the world index (pristine map: 0 unresolved out of 2214 levels).
- Navmesh geometry convention: center = corner + (ints[3], y, ints[5]), dims =
  (ints[3]+16, y, ints[5]+16). This is SOFT: the pristine map ships 124 center
  deviations, 73 dims deviations, boxes up to +-64u off (pyramids, HangingGardensTop01
  +-25u, DelphiBeach02Border01 588u off and missing its own GUID entirely). The engine
  tolerates all of it.
- Walkable area classes: working destinations use classes 1,2,3 freely; RandomIce03D's
  door cell is 100 percent class 2. Working destination meshes do NOT touch the level
  perimeter (AE Random09A walkable extent local x[3.6,71.4] z[3.2,60.6]; margin >= 3.2u
  on all sides); the landing is interior, at the door cell.
- Section order: (0x05,0x14,0x06,0x0b,0x17) for 245/297, (0x05,0x14,0x06,0x09,0x0b,0x17)
  for the 52 with 0x09. No other order or extra section type occurs.
- Index entry: ints[0..5] level dims (ints[3]/ints[5] = XZ half-extents in world units),
  ints[6..8] grid corner, ints[9..12] GUID. A destination needs no SD zone entry
  (Random09A has none in EITHER pristine map) and no GROUPS membership by level GUID.

### 2.3 Mouth->destination geometry (the placement requirement that is NOT one)
Footprint AABB distance surface->destination across all 345 working pairs:
min 69.0u (SuebiLakelands01 -> SubeiLakelands03_Cave, dy=0), p5 143u, median 518u,
max 14996u, zero pairs with footprint overlap. Working pairs at 75u, 84u, 91u, 98u,
103u, 105u, 112u, 120u exist, several with dy 0..36. Conclusion: destinations do NOT
need to be parked far away; they only avoid FOOTPRINT OVERLAP. dy separation is not
required either.

## 3. Compliance table: deployed swapped Random09A vs every derived requirement

Status: OK = byte-verified conformant. MISMATCH/MISS/STALE = deviation (severity noted).

| # | Requirement (from working data) | Deployed status | Byte evidence |
|---|---|---|---|
| 1 | Surface mouth record intact, references dest GUID | OK | HV01 blob deployed == pristine (695,598 B, all section sizes identical); rec#30 payload 60 B: prefix (2,0,1) + cfb4da3a...@12 + 89328d35...@28 + d840e7ae...@44 -> idx 703 |
| 2 | Mouth entity present, local coords | OK | inst#30 SilkRdDngEntrance_C01_Ext.dbr at (14,18,26), world (-120,-102,2200) |
| 3 | Dest registered in index under the GUID the mouth references | OK | idx 703 GUID d840e7ae..., fname/dbr AE's, corner (-278,18,2181) |
| 4 | Index dims correct for the blob | OK | ints[0..5] = (40,-1,40,40,10,40) IDENTICAL in AE, SV, deployed entries |
| 5 | Dest 0x06 portal-link trailer: exit+mouth ids + surface GUID + door cell | OK | deployed 0x06 rel 749=89328d35(exit), 765=cfb4da3a(mouth), 781=ce93e328(HV01 GUID), suffix (8,0,2)=door cell (8,2); trailer byte-identical to pristine AE R09 AND to upstream SV R09 |
| 6 | Door cell walkable in dest navmesh | OK | cell (8,2) = local x[64,72] z[16,24]: 508 walkable cells in deployed mesh (396 in pristine), cons low-nibble mostly 15 (full 4-dir), floor 1.0u above corner (pristine 1.2u) |
| 7 | Door cell area class legal | OK | ours class 2; working RandomIce03D door = 100 pct class 2 (1074 cells) |
| 8 | No stale absolute coords anywhere in blob | OK | 0x05 local (proof in 2.2); 0x06 no floats; 0x09 = (-17970263,2,0,0,0,0) identical SV vs deployed; 0x17 identical SV vs deployed (40,033 B) |
| 9 | 0x0a stripped, 0x0b present | OK | deployed sections (0x05,0x14,0x06,0x09,0x0b,0x17); 0x0a absent in ALL 47 SV-derived levels (map-wide sweep) |
| 10 | Section order matches a working pattern | OK | matches the 52-exemplar 0x09 variant exactly |
| 11 | v0x0e + empty 0x14 legal for a destination | OK | 121/297 working dests are v0x0e; 188/297 have empty 0x14; the engine also reads 50 v0x0e 48-B mouth records in the pristine map |
| 12 | Navmesh GUID list resolves; own GUID = index GUID | OK | deployed R09 0x0b guids = {d840e7ae (own, = index), 2d2acbf5 (xPTS, resolves)}; map-wide sweep: 0 unresolved GUIDs across all 2261 deployed navmeshes |
| 13 | Navmesh center/dims consistent with DEPLOYED corner | OK | center (-230,24,2229) = corner + (48,6,48); internally consistent with (1583,0,968) build |
| 14 | Navmesh box within engine tolerance | OK (deviation inside shipping variance) | ours overshoots footprint+16 by +16 east/north; pristine ships 38 levels >2u off incl +-32..64u and one 588u outlier |
| 15 | Walkable coverage >= pristine at the vanilla cave area | OK | 45,148/45,384 pristine cells covered (99.5 pct); the 236 missing cells are one dressing patch at local x[3.6,10.4] z[12.6,17.4], far from door (8,2) and from the west seam; matches SV's own 0x0a (SV shipped it) |
| 16 | West tunnel seam to xPTS aligned | OK | xPTS corner (-438,18,2181): east edge -438+160 = -278 = R09 west edge; R09 walkable extends to local x -7.6 (past the seam); xPTS mesh box spans x[-453,-245] covering it |
| 17 | Dest minimap/DATA2 entry valid | OK-STALE (cosmetic) | deployed keeps AE's 76,844 B minimap TGA (head byte-identical, offset shifted correctly): shows the tunnel-less AE layout in-game |
| 18 | SD zone entry parity | OK for R09 (none needed) | 'andom09' occurs 0 times in pristine SD and 0 in deployed SD; but see CONFIRMED GAP 1 for the map-wide SD regression |
| 19 | Placement: no footprint overlap | OK | 0 overlap at (1583,0,968); nearest surface level 64u |
| 20 | Placement: distance to surface within working range | MISMATCH (marginal, 5u below the working minimum) | ours 64.0u vs working min 69.0u (dy: ours 138 vs that exemplar's 0). NOT a categorical anomaly; see refutation 4.1 |

Everything the engine reads on the mouth->destination path is present, correct, and
self-consistent in the deployed bytes.

## 4. REFUTED prior theories (byte evidence)

### 4.1 "Destination must be far from the surface / co-residency breaks streaming" - REFUTED
The working data directly contradicts it: 345 working pairs include destinations at
69/75/84/91/98/103/105/112/120u from their surface mouths, several at dy=0 (same height
band, guaranteed tile co-residency). Median is 518u, not 700+. The (1663) failure had
footprint OVERLAP (a real anomaly, 0/345 working pairs overlap); the (1583) failure had
NO overlap and 64u distance, within a hair of shipping precedent (69u) while separated
by 138u vertically. The staged THIRD relocation (GRID_SHIFT (7840,0,2030), R09 corner
(5979,18,3243)) is built on the far-parking premise; if the wall is position-independent
(as the two failures at different placements and this audit both suggest), a 3000u park
will not fix it. Do not treat build 3 as "the fix"; treat it as one more experiment.

### 4.2 "Stale position-baked data inside the relocated blob" - REFUTED (byte-proven local)
Coordinator-priority lead, checked exhaustively: every structure in the blob is
level-local or position-free. Proof method: the SAME level content sits at corner
(-923,0,625) in SVAERA, (-1861,18,1213) in SV, (-278,18,2181) deployed; shared 0x05
entities have IDENTICAL float positions in all copies; 0x06/0x09/0x17 are byte-identical
between the SV-original and deployed-relocated copies (only the navmesh header center,
which the pipeline DOES rewrite, is world-anchored). Nothing inside the blob needed
shifting; nothing is stale. The same holds for xPassageTransitionStart and
BC_initialpathway (checked byte-for-byte vs upstream).

### 4.3 "The reciprocal exit portal was lost in the swap" - REFUTED
The destination-side binding lives in the 0x06 trailer, not 0x14, and it survived
verbatim: exit id 89328d35..., mouth id cfb4da3a..., HiddenValley01 GUID ce93e328...,
door cell (8,2), at identical section-relative offsets 749/765/781 in pristine AE,
upstream SV, and deployed. The portal UniqueIds are identical across both mods (base-game
inheritance), so keeping AE's GUID while taking SV's blob leaves the pairing coherent.

### 4.4 "The navmesh GUID list must include the portal-linked region" - REFUTED
Pristine working HV01's 0x0b GUID list does NOT contain Random09A; pristine Random09A's
list is {own} only. Navmesh GUID lists are spatial-geometry neighbors, not portal links.
Our {own + xPTS} list is the correct expression of the new tunnel adjacency.

### 4.5 "area=2 / box padding / 0x09 / v0x0e / empty 0x14 are illegal" - ALL REFUTED
Each pattern exists in shipping working destinations (see table rows 7, 11, 14 and
section 2.2 statistics).

## 5. CONFIRMED gaps (byte-proven, ranked by blast radius)

### GAP 1 (P1, map-wide): SD section wholesale-replaced with SV's
Deployed SD = 116,299 B, version 6, ~213 zone records == upstream SV's SD byte-for-byte.
Pristine SVAERA SD = 227,893 B, version 7, ~387 records (first records include
MarshlandLightandFog, X4CulticLair1 = XPack4/Ragnarok-era zones). The merge
(`svaera_plus_portals.py` step 3: "SD: SV's") replaces SVAERA's SD wholesale, silently
dropping every zone definition SVAERA added over the TQIT-era world (XPack3/XPack4 zone
defs and any SVAERA-specific ones). HiddenValley01 has an entry in both (v6 and v7), and
Random09A correctly has none, so this is unlikely to be the mouth wall, but it is a real
regression for Atlantis/Ragnarok/EE-era areas. Fix: merge SD = SVAERA records + SV-only
additions (mirror the GROUPS approach but SVAERA-first), or at minimum diff the two SDs
record-by-record before shipping.

### GAP 2 (P1, live foot-gun): donor dir vs GRID_SHIFT desync, and the verifier cannot see it
At audit time: repo HEAD `svaera_plus_portals.py` line 103 has GRID_SHIFT (1583,0,968),
but ALL 24 `local/editor_normalized/*.0b.bin` donors (mtimes 2026-07-05 13:47-13:51,
AFTER the 13:22 deploy) carry THIRD-shift centers, e.g. Random09A.lvl.0b.bin center
(6027,24,3291) = corner (5979,18,3243)+(48,6,48) for the staged (7840,0,2030) world.
A rebuild at HEAD right now would inject navmeshes centered ~6257u east / ~1062u north
of their levels, reproducing the invisible-wall class map-wide. And
`tools/verify_merged_bc_navmeshes.py` compares SIZE ONLY ("0x0b size == donor size"):
all 24 donor-vs-deployed pairs differ ONLY in the 12-byte center, so sizes match and the
gate PASSES on a fully desynced build. My hash sweep: 24/24 sha256 mismatches at equal
sizes between the deployed map's sections and the current donor files. Fix: (a) never
regenerate donors and edit GRID_SHIFT in separate steps without rebuilding; (b) extend
the verifier to assert center == index_corner + (center-corner convention) per level and
ideally compare content hashes, not sizes.

### GAP 3 (P2): GROUPS regression from SV-first merge
Merged GROUPS = SV's 889-record set first + SVAERA-only appended (deployed: 893).
For every group name present in both, SV's TQIT-era version wins and SVAERA's is dropped.
Concrete divergence: group `Shrine_Respawn_Orient` in deployed embeds HiddenValley01's
LEVEL GUID (from SV's data); pristine SVAERA's version does not. GROUPS raw data is
entity-proxy GUID lists (position-independent), so this does not move anything, but
SVAERA-era changes to shared groups (respawn shrines, unified proxies) are silently
reverted to TQIT-era content. Same structural fix as GAP 1: SVAERA-first for shared names.

### GAP 4 (P2): the diagnostic append-clone ships broken and is not inert
Deployed idx 2281 = byte-clone of ArcadiaDungeonPassage (idx 973) at +80u X with a
synthetic index GUID (7F000001..7F000004). Its 0x0b still carries the DONOR's GUID list,
so: (a) the clone's navmesh own-GUID != its index GUID (the only other level in either
map with that defect is DelphiBeach02Border01, a known-broken base-game oddity);
(b) TWO levels now claim navmesh identity for GUID d(973) 80u apart. The clone was a
registration experiment and is documented as "harmless"; the bytes say it is at best
unclean and at worst a nav corruption near ArcadiaDungeonPassage. Fix: drop the clone
from the build (delete step 7d) at the next rebuild.

### GAP 5 (P3, cosmetic): Random09A minimap is AE's
BITMAPS idx 703 still points at AE's 76,844 B TGA (no west tunnel drawn). Replace with a
regenerated TGA or SV's minimap entry if cosmetically desired.

## 6. Remaining blocker candidates for the invisible wall (ranked)

The byte audit clears the graft, so the wall must come from something bytes cannot fully
prove. Ranked by evidence and testability:

### Candidate 1 (SUSPECTED, structural): the GENERATED navmesh is not usable for the cross-region link even though it parses
Every working mouth destination in the game has an EDITOR-BAKED navmesh. Ours is the
only destination with a Python-generated one. Static disassembly says ProcessRLTD
accepts it (GUID gate, params, addTile), but "accepted at load" does not prove "usable
by PathFinder's cross-region linker" (poly generation from our layers, region/poly
connectivity, query filters). This is the sole component in the whole chain with zero
shipping precedent, and it was present in BOTH failed placements.
DISCRIMINATING EXPERIMENT (cheap, decisive): rebuild once with the PRISTINE AE Random09A
0x0b transplanted into the swapped blob instead of the generated donor: copy pristine
`Random09A.lvl` (the 105,564 B AE blob) into `local/editor_normalized/` as the tier-2
`.lvl` donor and REMOVE `Random09A.lvl.0b.bin` (tier-1 outranks tier-2). transplant_rec02
repositions the header center to the shifted corner; the AE mesh's GUID list is {own}
which resolves; mesh data is level-local (byte-proven above). The tunnel area will be
unwalkable (AE mesh has no tunnel cells), but the MOUTH test becomes pure:
- mouth opens with AE mesh -> the generated mesh is the blocker; iterate on generator
  fidelity (poly/region formation), not on placement.
- mouth still walled with a byte-pristine Editor mesh in the destination -> the
  destination is fully exonerated; move to Candidates 2/3.

### Candidate 2 (SUSPECTED, protocol): save-state contamination
Both failed walk tests reused an existing character. This mod's own docs forbid
character "bouncing", and the quest-portal era already demonstrated save-baked state
overriding rebuilt content (dialog state persisted across rebuilds). A FRESH Custom
Quest character has never tested the mouth. Zero-cost falsification: retest with a brand
new character before any further rebuild. If the mouth opens fresh, the wall was save
state, not bytes.

### Candidate 3 (SUSPECTED, engine-internal): GridEntrance IsOpen ([portal+0xfc]) auto-open path
Still untraced in Engine.dll (acknowledged gap in the prior diagnosis). Mitigating
evidence: HiddenValley01 is byte-identical to pristine SVAERA where the same mouth works
on the same engine, so the surface-side data cannot encode "closed". If Candidates 1-2
are falsified, this is the next disassembly target: what flips IsOpen for a plain
GridEntrance at load, and does it inspect the DESTINATION region state (which would
point back at the generated navmesh or at region streaming).

### Candidate 4 (WEAK): 64u proximity is 5u below the closest working precedent
Only if Candidates 1-3 all fail: nudge R09 5-10u so the gap is >= 69u with dy separation
unchanged. Do NOT jump to the 3000u park; it has no evidentiary basis (section 4.1).

## 7. Broader-job audit results (beyond the mouth)

- All 24 real BC navmeshes in the DEPLOYED map: GUID lists 100 percent resolvable, own
  GUIDs == index GUIDs, centers consistent with the deployed (1583,0,968) corners,
  7 ocean-scenery stubs (148 B) as designed, 0x0a stripped from all 47 SV-derived levels.
- R09<->xPTS seam: corner math exact (xPTS east edge -278 == R09 west edge); R09 walkable
  crosses the seam to local x -7.6; xPTS box covers it. Seam intact at this build.
- SV's interior mouth records survived the merge and resolve: xTempleTransitionHallway ->
  new_secretdoor_transitionhallway, yet_another_fucking_connector -> drxBC3,
  PillagedVillage -> ForestObsidianTransition (all 48-B v0x0e records). The blood cave
  interior depends on the same mouth mechanism working with generated destination meshes:
  whatever fixes the surface mouth validates these three too.
- Generated meshes are systematically MORE permissive than Editor bakes: deployed R09 has
  72,673 walkable cells vs pristine 45,384 for the same base cave (plus tunnel). Class 2
  everywhere, walkableRadius 0.4 in all three difficulty sets (Editor uses 0.4/0.6/0.8).
  Not wall-causing (over-permissiveness cannot block), but expect click-to-move into
  spots the Editor would forbid, and revisit before ship.
- HiddenValley01, xPassageTransitionStart, BC_initialpathway deployed blobs verified
  against their sources (pristine byte-equality for HV01; SV byte-equality modulo the
  intended 0x0a->0x0b swap for the other two).

## 8. Reproduction notes

Scripts (session scratchpad, `audit/`): `ax_extract.py` (per-map index/blob/0x14-graph
extraction), `ax_blob.py` (section dissection + GUID scans + hexdump), `ax_navcmp.py`
(cross-map navmesh coverage diff in level-local space), `ax_exemplars.py` (the 297-dest
checklist derivation), `ax_invariant.py` + inline sweeps (whole-map 0x0b invariants,
donor hash comparison, mouth-pair distance stats). All read-only against the ARCs/maps.

Key hex anchors for future byte work on Random09A (deployed blob, idx 703):
- 0x06 section at blob offset 9642 (809 B); portal trailer at section-relative 737
  (prefix 02000000 40000000 01000000), exit GUID @749, mouth GUID @765, HV01 GUID @781,
  door cell + terminator (08000000 00000000 02000000) @797.
- 0x0b section at blob offset 10491 (78,918 B); guid_count @+12 = 2; own GUID @+16;
  xPTS GUID @+32; center (i32 x3) @+48 = (-230,24,2229); dims @+60 = (64,34,64).
