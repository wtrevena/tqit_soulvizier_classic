# The xPTS -> BC_initialpathway wall: index-footprint gap (root cause + exact fix)

Deepest-tier navmesh analysis, 2026-07-05. Read-only over the deployed build Will
walk-tested today, and the follow-up deployed build with the gate-free GUID fix.

## 0. UPDATE / verdict correction (read this first)

The gate-free GUID-list fix (own-GUID-only deep donors) was deployed and CONFIRMED in
the map (BC_initialpathway guid_count=1), and **Will still walls at the exact same
xPTS -> BC_initialpathway spot.** So the ProcessRLTD residency gate was NOT the (sole)
cause of THIS seam. The GUID trim was still correct and worth keeping (it removes a
latent residency wall from every deeper seam, and single-GUID meshes are
base-game-normal), but it is not what fixes Will's wall.

**The real cause, measured in the deployed index: a 2-world-unit INDEX-FOOTPRINT GAP
at exactly this one seam.** BC_initialpathway's LEVELS-index content tile-dims are
`[39,4,24, 40,4,24]` (byte-verified from the SV source blob): the CONTENT triple
x-tiles = 39, so BC's footprint east edge = corner.x 5739 + 39*SCALE(2) = **5817**,
but xPassageTransitionStart's footprint west edge = **5819**. Every other TQAE level in
the game has the content triple equal to the box triple; BC is one of a handful of SV
levels that ship a content triple one tile short. The engine builds the cross-region
walk link only between levels whose index footprints EDGE-ABUT (share an edge, gap=0);
a 2u index gap blocks the link even though the two navmeshes' walkable CELLS overlap at
the seam. **This is the walls-for-a-2u-gap that the coordinator measured, and the data
below confirms it is the sole gap in the whole cluster and that the fix is safe.**

**THE ONE EXACT FIX (minimal, engine-correct, no navmesh regen): widen BC's index
content x-tiles 39 -> 40** so its east edge = 5819 = flush with xPTS. BC's box triple
is ALREADY 40 and BC's actual navmesh already covers the widened strip, so the fix is a
pure index-metadata edit (Section 4). Fix A over Fix B, decisively (Section 3).

## 1. THE decisive measurement: every cluster seam's index gap

For all 39 cluster level-pairs that SHOULD connect (each lists the other in its `0x0b`
GUID list, i.e. authored as neighbors) AND are near-abutting, I computed the
index-footprint gap = corner + content_tiles*SCALE(2):

- **38 of 39 seams are FLUSH (gap = 0).** Random09A<->xPTS (walks today), BC<->
  drxFirstxistion (walks), drxFirstxistion<->drxFirstRoom, drxFirstRoom<->Connector1
  / river_extension01, all downstream drxBC*/ocean seams: all gap=0.
- **EXACTLY ONE seam has a non-zero gap: BC_initialpathway <-> xPassageTransitionStart,
  x-gap = +2u** (BC.E=5817, xPTS.W=5819), over a 48u shared z-band. **This is Will's
  wall.** No other cluster seam that should connect has any gap.

That is a controlled experiment with n=39 and a perfect correlation: the one seam with
an index gap is the one, and the only one, that walls. Combined with the disasm-codified
rule (playbook Section 3: grid-seam link requires the footprints to abut AND both
navmeshes to have overlapping walkable cells at the shared edge), the mechanism is
established: **the linker keys on index-footprint adjacency; a 2u gap = no link.**

Why SV shipped these ints and it worked in the original game: SV's blood-cave was a
single continuous `0x0a` PathEngine mesh that spanned the gap, so the cross-level link
was not gated on per-level index abutment. Our port replaces that with per-level `0x0b`
Detour navmeshes, which the TQAE engine stitches by index-footprint adjacency. The 2u
index slack was harmless under `0x0a` and is fatal under per-level `0x0b`.

## 2. Fix A gives the engine walkable cells on BOTH sides of the flush seam

Widening the index does not move the navmesh (the mesh is level-local, indexed off
`center - dims`, independent of index tile-dims). So the only question is whether both
meshes already have walkable cells straddling the flush edge x=5819. Measured, door
z-band [3323,3371]:

| x-window | BC cells | xPTS cells | coincident |
|---|---|---|---|
| [5815,5817) (BC's current 39t edge) | 352 | 0 | 0 |
| [5817,5819) (BC's side of the flush seam) | **113** | 0 | 0 |
| [5819,5821) (xPTS's side / xPTS west edge) | 113 | **94** | 94 |
| [5821,5823) | 352 | 352 | 352 |

- BC's navmesh already extends to x=5842.7 (its mesh box east edge; box tile-dim is
  already 40). BC has **113 walkable cells in the x[5817,5819) strip** that a 40-tile
  index brings into the footprint.
- xPTS's westmost walkable cells sit at x=5819.5-5820.7 (its own west edge, 94 cells).
- After widen, BC's east tile-column strip [5817,5819) (113 cells) meets xPTS's west
  tile-column strip [5819,5821) (94 cells) at the flush plane 5819, with their z-bands
  overlapping on **12 of 13 door rows** (z 3333.7-3336.1). Both sides have walkable
  cells at the shared edge in overlapping z -> the hand-off condition is met.

Calibration against the WORKING R09<->xPTS seam (walks today, gap=0): it has dense
coincident cells straddling x=5979 (95 coincident at [5977,5979], 256 at [5979,5981]).
The widened BC seam reproduces the same shape (cells on both sides of the flush plane
in overlapping z). Coverage/erosion/cons of all three meshes are healthy (94.5-96.2%
of the true tok floor, 0 cons-byte mismatches, single/expected components) - full
numbers in Section 6; none of that is the wall.

## 3. Fix A vs Fix B - pick A

**Fix A (WIDEN BC index content x-tiles 39 -> 40): minimal and engine-correct.**
- No navmesh regeneration. The donor `.0b.bin` is byte-unchanged; it is injected
  verbatim (`pre_positioned=True`), and `inject_rec02_into_blob` never reads tile-dims.
- Does NOT trip the donor-freshness gate: `assert_donor_fresh` reads only the grid
  CORNER (ints[6],ints[8]) vs the donor center; widening ints[0] leaves the corner
  untouched, so the gate still passes (verified by reading the gate code).
- Makes the seam FLUSH (gap 0), NOT overlapping: BC(40t) x[5739,5819], xPTS
  x[5819,5979] -> shared edge at 5819, area overlap 0. Matches every working seam and
  keeps the interior XZ-disjoint rule.
- BC's OTHER seam is unaffected: widening moves only the EAST edge. BC's west edge stays
  at corner.x 5739, still flush with drxFirstxistion_connection (east=5739).
- The engine already agrees the terrain extends to 5819: BC's box triple ints[3] is
  ALREADY 40. Fix A just makes the CONTENT triple match the box triple, i.e. restores
  the base-game invariant (content == box on x/z for all 2235 AE levels).

**Fix B (SHIFT BC + its downstream sub-chain +2 in x): heavier, and it MISALIGNS
BC's working west seam.** Shifting BC +2 to abut xPTS at its real geometry would move
BC's west edge to 5741, opening a NEW 2u gap with drxFirstxistion (east 5739) - so you
would have to shift drxFirstxistion +2 too, and then drxFirstRoom, Connector1,
river_extension01, ... i.e. the entire sub-chain reachable from BC not through xPTS,
AND regenerate every shifted donor (positions change), AND re-run the freshness gate.
It cascades and needs a donor regen for no benefit over A. Reject B.

**Decision: Fix A.**

## 4. THE EXACT EDIT (Fix A)

Single source of truth for cluster placement is `shifted_ints_raw(lv)` in
`tools/svaera_plus_portals.py` (called for both the injected blob's `target_ints` in
step 7b and the merged LEVELS index entry in step 8, so patching it there keeps the two
in lock-step). BC's tile-dim x is `ints_raw[0]` at BYTE OFFSET 0 (13x int32; [0..5]
tile dims, [6,7,8] corner, [9..12] GUID).

In `tools/svaera_plus_portals.py`, in `shifted_ints_raw` (currently lines 122-137),
after the corner-shift `struct.pack_into('<iii', raw, 24, ...)` and before
`return bytes(raw)`, add a targeted content-triple normalization:

```python
        # Normalize the CONTENT tile triple to the BOX triple on x/z. A handful of
        # SV levels (BC_initialpathway [39,4,24 / 40,4,24], riverextension02, etc.)
        # ship a content x/z tile-dim one short of the box triple. Under SV's single
        # 0x0a PathEngine mesh that was harmless, but TQAE stitches the per-level
        # 0x0b navmeshes by INDEX-FOOTPRINT adjacency (corner + content_tiles*2), so
        # the 2u short edge leaves a 2u gap that blocks the cross-region walk link
        # (measured: BC.E=5817 vs xPTS.W=5819 = Will's wall, the ONLY non-zero gap in
        # the cluster). The box triple already reaches the correct edge and the
        # navmesh already covers it, so widening content->box is a pure metadata fix
        # (no donor regen; freshness gate checks only the corner). ints layout:
        # [0..2]=content tile x,y,z  [3..5]=box tile x,y,z.
        cx, cy, cz, bx, by, bz = struct.unpack_from('<6i', raw, 0)
        if (cx, cz) != (bx, bz):
            struct.pack_into('<2i', raw, 0, bx, cy)   # content x <- box x (offset 0)
            struct.pack_into('<i', raw, 8, bz)        # content z <- box z (offset 8)
```

This runs for every GRID_SHIFT-matched cluster level (all xBloodCave + Random09A). It
fixes BC (39->40 on x) and normalizes the other slack cluster levels (Section 5) to the
base-game invariant in the same pass, all on edges that are currently flush so it can
only help. Random09A and xPTS have equal content/box triples already, so they are
untouched (their walk-proven donors and index entries do not change).

Then rebuild the map (`py tools/svaera_plus_portals.py`) and deploy. No
`gen_bc_navmeshes.py` run needed. Verify post-build that BC's merged index east edge is
5819 (`corner.x 5739 + ints[0]*2`).

Narrower alternative if you want to touch ONLY BC: guard the block with
`if key.endswith('/bc_initialpathway.lvl')` instead of the general
`(cx,cz) != (bx,bz)`. The general form is safe and future-proofs the other slack
levels; the BC-only form is the strictly minimal change to clear the reported wall.

## 5. SANITY: other cluster seams that could wall later - all clear except this one

Cluster levels with content<box tile-dim slack: BC_initialpathway (39/40 x),
drxFirstxistion_connection (39/40 z), bossfight (58/61 x, 60/60 z),
river_extension01 (87/88 z), riverextension02 (39/40 x). For EACH, I checked its
listed-neighbor seams against the content-triple footprint:

- BC_initialpathway: **x-gap +2 to xPTS = the wall** (fixed by A); flush to
  drxFirstxistion.
- drxFirstxistion_connection: flush to BC (x) AND flush to drxFirstRoom (z). Its short
  edge (content z north = 3369) faces NOTHING (its neighbor seam to drxFirstRoom is on
  its SOUTH edge z=3291). No wall.
- bossfight: isolated (no listed navmesh neighbors); its short edges face nothing.
- river_extension01: flush to drxFirstRoom, drxBC2, drxBC_Connector1 (its short z-edge
  faces none of them at the short side). No wall.
- riverextension02: flush to drxBC2 (z); its xTempleTransitionHallway relation is a
  corner-touch (xov=0, zov=0), not a walk seam. No wall.

So today the 2u BC<->xPTS gap is the ONLY footprint gap between levels meant to connect
anywhere in the cluster (uber/boss/secret branches included - those are the drxBC3 /
drxBC_Finale / ocean sub-graph, all measured flush). Fix A's general form also
normalizes the other four slack levels for free, pre-empting any gap if their layout
ever shifts. **After Fix A, all 39 cluster seams are flush.**

## 6. Supporting geometry (unchanged from the first pass, confirms it is not the mesh)

- Coverage vs the true SV tok floor (rasterized with gen_rec02's own functions; donor
  cell sets reproduce byte-exactly): Random09A 96.2%, xPTS 94.7%, BC 94.5% after
  ERODE_CELLS=2. Our R09A donor covers 99.5% of the Editor-baked AE Random09A at cell
  shift (0,0); no (dx,dz) frame offset.
- Seam overlap richness at the BROKEN seam BEFORE the fix: 227-941 coincident walkable
  cells per 2u row across the door window, floor dy = +0.0 everywhere (both flat at
  y=16.4) - i.e. the meshes overlap perfectly; only the INDEX footprints did not abut.
- Connectivity: BC is a single connected component; the 328-cell secondary components
  in R09A/xPTS are the shared cross-seam handoff pad (baked AE caves carry up to 9
  islands). cons bytes: 0 mismatches in all three meshes (intra-tile + tile-border
  portals correct). Erosion never fragments; keep ERODE_CELLS=2.
- gen_rec02.py needs NO change and is untouched at HEAD (git diff clean). The fix is
  entirely in the LEVELS-index metadata, not the navmesh generator.

## 7. Confidence

- Mechanism (linker keys on index-footprint abutment; 2u gap blocks the link): HIGH.
  n=39 controlled correlation (the one gapped seam is the one wall), matches the
  disasm-codified grid-seam rule, and the gate-free GUID experiment already excluded
  the residency gate as this seam's cause.
- Fix A clearing the wall: HIGH. It makes the footprints flush (proven arithmetic:
  5739+40*2 = 5819 = xPTS.W) with walkable cells on both sides in overlapping z
  (measured), reproducing the working R09<->xPTS seam shape, without disturbing BC's
  working west seam or any donor.
- What only the walk test confirms: the link forming once the footprints abut. If it
  somehow still walls, the next suspect is the paired-portal / dstRegion branch in
  CAVE_ENTRY_CHAIN_TRACE.md, but the index gap is by far the strongest and simplest
  remaining cause and every geometric alternative is measured out.

## Appendix: the numbers to cite

```
Cluster seams meant to connect: 39 near-abutting listed pairs
  gap == 0 (flush):  38   [incl. R09<->xPTS and BC<->drxFirstxistion, both walk today]
  gap  > 0 (wall) :   1   ONLY BC_initialpathway.E=5817 <-> xPassageTransitionStart.W=5819  (+2u)

BC_initialpathway index ints (SV source, byte-verified): [39,4,24, 40,4,24]
  content x-tiles = 39 -> east edge 5739 + 39*2 = 5817  (2u short)
  box     x-tiles = 40 -> east edge 5739 + 40*2 = 5819  (already correct; = xPTS.W)
  FIX: content x-tiles 39 -> 40  =>  east edge 5819 = FLUSH with xPTS

Walkable cells at the flush seam (door z-band), after widen:
  BC   in [5817,5819): 113 cells   xPTS in [5819,5821): 94 cells   z-overlap: 12/13 rows
```
