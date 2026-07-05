# Navmesh coverage / connectivity fix: the xPTS -> BC_initialpathway wall

Deepest-tier navmesh-generation analysis, 2026-07-05. Read-only investigation over the
deployed build Will walk-tested today (deployed `CustomMaps/.../Levels.arc` of
2026-07-05 15:20, 2282 levels; its R09A / xPassageTransitionStart / BC_initialpathway
`0x0b` sections are byte-identical, sha1-verified, to `local/editor_normalized/*.0b.bin`
regenerated 15:13-15:17, so everything below analyzes exactly the bytes that were
in-game). `tools/gen_rec02.py` was never modified (all what-if numbers come from
importing its functions and re-running them in memory; the donor cell sets reproduce
byte-exactly, see Section 3).

In-game state this explains (Will, 2026-07-05): entrance mouth PERFECT, Random09A ->
xPassageTransitionStart seam crossing WORKS, and an invisible wall + stuck at the
xPassageTransitionStart -> BC_initialpathway transition.

---

## 0. Verdict (read this first)

**The wall at xPTS -> BC_initialpathway is NOT a navmesh-geometry defect. The seam
geometry is measurably the best in the whole chain (Section 2). The wall is the
navmesh LOAD gate recurring one hop deeper than the mouth bug that was just fixed:
BC_initialpathway's `0x0b` GUID list is `[own, drxFirstxistion_connection, xPTS]`,
and ProcessRLTD (VA 0x101f4ba0) refuses to load the WHOLE navmesh unless EVERY listed
GUID's level is RESIDENT at load time, with no retry. When the player crosses into
xPTS and BC streams in, `drxFirstxistion_connection` (2+ grid-hops beyond the player,
touching only BC and drxFirstRoom) is at/behind the streaming frontier, the gate
fails, `Level+0x6a48` stays 0, and the pathfinder linker skips every link into BC =
invisible wall exactly at that seam** (mechanism chain disasm-proven in
`docs/CAVE_ENTRY_CHAIN_TRACE.md` sections 2-3; this is the same mechanism that walled
the mouth before the cluster relocation, now firing at the first seam whose
destination lists a GUID the mouth-stream neighborhood cannot satisfy).

**The one exact fix: trim every blood-cave donor's GUID list to `[own GUID]` alone,
except the two walk-proven donors (Random09A, xPassageTransitionStart) which stay
byte-identical.** One small edit in `tools/gen_bc_navmeshes.py` (Section 5), donor
regen, re-merge, deploy. 251 of 2214 real base-game navmeshes ship single-GUID
(including AE-Random09A itself), so the shape is engine-proven; the GUID list's only
RE-proven consumer is the residency gate, and grid seams carry no other cross-level
link data (Section 4), so shrinking the list cannot break seam handoff but removes
every present and future residency wall in the cluster, in both walk directions.

Everything else measured (coverage, erosion, connectivity, cons bytes, area id,
spatial alignment) is healthy; numbers below. Erosion needs NO change.

---

## 1. Coverage and alignment: the generator is NOT under-covering, and there is NO offset

True walkable floor = the pristine SV `0x0a` tok mesh (extracted from upstream
`world01.map`), rasterized with the exact `gen_rec02` functions. Donor = the deployed
`0x0b` walkable cells (`area != 0`, `height != 0xff`), tile-unpacked to the global
grid.

| level | tok 2D area | raster cells (% of tok) | after ERODE_CELLS=2 (% of tok) | donor == re-derived erode2? |
|---|---|---|---|---|
| Random09A (SV blob) | 3,022 u2 | 77,074 = 102.0% | 72,673 = **96.2%** | YES, exact |
| xPassageTransitionStart | 2,915 u2 | 74,982 = 102.9% | 69,021 = **94.7%** | YES, exact |
| BC_initialpathway | 1,575 u2 | 40,410 = 102.6% | 37,191 = **94.5%** | YES, exact |

(raster > 100% because a cell is marked when ANY part of a triangle overlaps it, a
conservative superset; erosion then insets by walkableRadius.)

Calibration against a real Editor bake of the SAME cave (SVAERA's baked Random09A
`0x0b`, extracted from the reference arc): our generated R09A donor covers **99.5% of
the baked mesh's walkable cells at cell shift (0,0)**; the cross-correlation surface
over +-15 cells is a flat plateau centered on zero (62.3% raw match at (0,0), (+-1,+-1)
all within noise; the mismatch tail is SV's added west tunnel plus our slightly more
generous erosion). **There is no spatial (dx,dz) offset between our navmesh frame and
the Editor's.** The earlier "walk into the wall" report is fully explained by the
previous flaky build; the current frame chain (tok corner-relative -> container
center-dims -> engine placement) is proven correct in-game by today's successful mouth
and R09<->xPTS crossing. The known (8,7,8) drift of the SV `0x0a` container center vs
the LEVELS-index center is real but harmless: the grid origin `center - dims` stays
exactly `index_corner - 16` on x/z, matching the baked convention, because the SV
`dims` carry the same +8 slack as the center.

Baked-cave norms (AE-Random09A bake) vs our donor, for calibration: 45,384 cells /
1,815 u2 over 23 tiles, NINE connected components (759, 236, 14, 9, and single-cell
islands), 112 portal bits per tile, walkable area ids 1 and 2 both in normal use
base-game-wide. Ours: 72,673 cells over 37 tiles (bigger box + tunnel), TWO
components, 117 portal bits per tile, area id 1. Editor bakes are messier than our
output; islands are baked-normal.

## 2. The seams, cell by cell (the decisive measurement)

Seam profiles list, per 2u z-row, how far each mesh's walkable cells reach relative to
the shared index edge, the floor heights there, and the count of XZ-coincident
walkable cell pairs (overlap).

**BROKEN seam, xPTS (east) <-> BC_initialpathway (west) at x=5819, shared z
[3323,3371]** (door window z 3325..3343):

- BC's mesh crosses 19.9u EAST past the seam line (to x=5838.9): SV baked xPTS's
  floor geometry into BC's tok (BC's `0x0a` GUID list names xPTS as a contributor).
- xPTS's own westmost walkable cell is x=5819.5, i.e. it reaches the line but does
  not cross (SV never baked BC geometry into xPTS's tok; its `0x0a` lists only R09A).
- Overlap: 227-941 coincident walkable cells per 2u row across the whole door window.
- Height agreement: dy = **+0.0** on every row (both floors flat at world y 16.4).

**WORKING seam, R09A (east) <-> xPTS (west) at x=5979** (walked today): R09 crosses
7.5u west, xPTS crosses 19.9u east, overlap up to 941 cells/row, and dy = **+2.6
everywhere** (R09 floor 19.0, xPTS flat 16.4).

**Working BAKED surface seam, HiddenValley01 <-> HighAltituedBorder01 at x=-134**
(base game, walked by everyone): HV1 crosses only 0.7u; HAB01's entire 901-cell mesh
sits INSIDE HV1's box (16.3u past the line); the usable link band is a 58-cell strip
where dy=-0.2; elsewhere dy=+20 (cliff). One-sided crossing and tiny link bands are
baked-normal.

Conclusion: the broken seam has MORE overlap and PERFECT height agreement compared to
both working references. Geometry cannot be the wall. The only engine-visible
difference on the broken side is BC's navmesh GUID list (and see Section 4 residual).

## 3. Connectivity, islands, erosion audit (original brief items 2-3)

Connected components under the engine model (4-adjacency, both walkable,
|dh| <= CLIMB_CELLS=5, exactly dtBuildTileCacheRegions' isConnected):

| level | components (deployed, erode2) | erode1 | erode0 |
|---|---|---|---|
| Random09A | 2: [72,345 + 328] | 2: [74,442 + 410] | 2: [76,571 + 503] |
| xPassageTransitionStart | 2: [68,693 + 328] | 2 | 2 |
| BC_initialpathway | **1**: [37,191] | 1 | 1 |

- The 328-cell secondary components in R09A and xPTS are the SAME 4x4u pad at
  x[5979.5,5983.5] z[3251.5,3255.3], just inside R09's west edge: the cross-seam
  handoff strip, present in both meshes at each mesh's own floor height (19.0 vs
  16.4), disconnected intra-mesh by the 2.6u step. It exists at erosion 0 too, so it
  is geometry, not an erosion artifact, and the baked AE cave has nine such islands
  including single cells. Islands are NOT the stuck bug (that build is gone; today's
  build walks R09+xPTS fine).
- cons bytes: **0 mismatches** in all three meshes against the heights/areas adjacency
  model (intra-tile low nibble AND tile-border portal high nibble). Portal-bit density
  matches the Editor bake (117/tile vs 112/tile). Tile stitching is correct.
- Erosion sweep (regenerated in memory with the same functions, donor sets reproduce
  exactly): ERODE_CELLS 2 -> 1 -> 0 changes total coverage 94.5-96.2% -> 98.5-99.1% ->
  102-103% of tok area and NEVER changes the component count. Narrowest traverse
  corridor (max-min clearance path between high-clearance anchors in the east and
  west thirds of the main component):

| level | erode0 | erode1 | erode2 (deployed) |
|---|---|---|---|
| Random09A E->W | 26.6u | 26.2u | 25.8u |
| xPTS E->W (the passage squeeze) | 2.2u | 1.8u | **1.4u** |
| BC_initialpathway E->W | 7.0u | 6.6u | 6.2u |

The xPTS 1.4u pinch is the tightest spot in the chain and Will traversed it today, so
it is walkable (player radius 0.4). **Erosion needs no change (keep ERODE_CELLS=2,
walkableRadius parity with the engine params we declare).** If in-passage tightness
is ever re-reported, ERODE_CELLS=1 widens the pinch to 1.8u at zero connectivity cost
and stays under the raster's +2-3% wall-clipping slack; do not go to 0 (cells would
touch walls the engine believes walkable, 102% of tok).

## 4. Why the wall is the load gate, and the residual suspects

- ProcessRLTD's per-GUID gate (find in whole-map GUID map AND live instance array
  `[reg+0x50]` non-null) fail-closes the ENTIRE `0x0b` on one non-resident neighbor;
  `Level+0x6a48` stays 0; the cross-region linker at 0x101f3680 skips every link whose
  destination has `+0x6a48 == 0`. All disasm-proven in CAVE_ENTRY_CHAIN_TRACE.md.
- BC's list `[e39fcb11 own, 57d83343 drxFirstxistion, 2d2acbf5 xPTS]` is the FIRST in
  the walk order whose gate needs a level beyond the player's streaming neighborhood.
  R09's list is [own, xPTS] and xPTS's is [own, R09]: each other only, always resident
  at their load moments, which is exactly why those two load and their seam works.
- The deeper chain has the same defect at EVERY hop (drxFirstxistion lists
  drxFirstRoom; drxFirstRoom lists Connector1 + river_extension01; drxBC3 and
  drxBC_Finale list up to 8 and 12 levels including non-abutting ocean scenery).
  Fixing BC alone moves the wall one seam west. The fix must cover all 21 donors
  beyond xPTS.
- Grid seams carry no other cross-level link data: the `0x06` sections of R09A, xPTS,
  and BC embed NO neighbor GUIDs (byte-scanned; R09's 0x06 embeds only the
  HiddenValley01 portal-return trailer). Seam handoff therefore rides on the meshes'
  walkable overlap (which is why baked meshes carry neighbor-contributed geometry and
  why our measured overlap being perfect matters) plus both meshes being LOADED.
- Residual secondary anomaly, kept on the bench: BC's LEVELS-index first tile-dims
  triple is (39,4,24) vs second (40,4,24). Computed from the first triple, BC's east
  edge is x=5817, a 2u gap to xPTS's west edge 5819; from the second triple they abut
  exactly. Several SV levels share this first<second slack (bossfight 58 vs 61,
  drxFirstxistion z 39 vs 40, river extensions), while ALL 2235 base-game entries have
  x/z equal in both triples. The original SV game shipped these exact ints and its
  TQIT engine streamed and linked the chain fine, so this is unlikely to be the wall,
  but it is a one-line normalization if fix #1 proves insufficient (below).

## 5. THE FIX (exact, ranked, with expected effect)

### Fix 1 (apply now): gate-free GUID lists for the 21 donors beyond xPTS

`tools/gen_bc_navmeshes.py`, in `main()`, immediately after
`resolved, dropped = resolve_guids(guids_0a, own_guid, merged_guids, shared_remap)`
(currently line ~223), insert:

```python
        # Residency-gate hardening: ProcessRLTD (0x101f4ba0) refuses the WHOLE
        # navmesh unless EVERY listed GUID's level is RESIDENT at load time,
        # and a failed load is never retried (CAVE_ENTRY_CHAIN_TRACE.md sec 3).
        # Donors that list far-side neighbors therefore wall the first seam
        # whose neighbor sits beyond the streaming frontier (proven in-game at
        # xPTS -> BC_initialpathway, 2026-07-05). Ship every donor gate-free
        # with its own GUID alone, EXCEPT the walk-proven entrance pair which
        # stays byte-identical. Single-GUID meshes are base-game-normal
        # (251/2214, including AE-Random09A itself).
        KEEP_NEIGHBOR_GUIDS = {
            R09_KEY,
            'levels/world/xbloodcave/xpassagetransitionstart.lvl',
        }
        if key not in KEEP_NEIGHBOR_GUIDS:
            resolved = [resolved[0]]        # own GUID only (resolve_guids puts it first)
```

Then `py tools/gen_bc_navmeshes.py` (approx 213s; 21 donors change, R09A + xPTS stay
byte-identical), re-merge, deploy. The donor-freshness gate and the per-donor
self-verifies all still pass (center untouched, own GUID resolves, 3 sets).

Expected effect, from the measurements: BC's navmesh (and every deeper one) loads
unconditionally the instant its level streams in, `+0x6a48 = 1`, the linker stops
skipping it, and the xPTS -> BC seam links over the measured 941-cells/row dy=0.0
overlap, strictly better geometry than the R09 seam that already works. Fixes all 12+
downstream seams in the same stroke, in BOTH walk directions (own-only lists cannot
fail on re-approach after eviction, which is a latent directional failure mode of any
neighbor-listing policy in this engine).

Why it is safe: the GUID list's only reverse-engineered consumer is the load gate; the
portal linker resolves destinations by PORTAL GUIDs, not mesh lists; seams have no
other link data (Section 4); and the walk-proven R09A/xPTS donors do not change by a
single byte.

### Fix 2 (only if a specific seam still walls after fix 1): normalize the index tile dims

In the merge (`tools/svaera_plus_portals.py`, where relocated `ints_raw` corners are
already rewritten), also set `ints[0]=ints[3]`, `ints[2]=ints[5]` for the 24 cluster
entries (BC 39->40 etc.), removing the 2u footprint gap in case any TQAE edge-keyed
logic reads the content triple. Zero-risk normalization to the base-game invariant
(first triple == second on x/z for all 2235 AE levels).

### Fix 3 (only if both above fail): symmetric seam crossing for xPTS

Regenerate xPTS's donor with BC's tok rasterized into xPTS's padded grid (neighbor
geometry contribution, WITHOUT adding BC's GUID), so xPTS's mesh crosses the 5819
plane the way both sides of every other working seam do. Not indicated by current
data (the baked HV1/HAB01 seam works with the same one-sided crossing shape).

### Fix 4 (cosmetic/quality, not now): none needed for erosion or area id

ERODE_CELLS=2 keeps 94.5-96.2% of the true floor, never fragments, and beats the
Editor bake's coverage of the same cave; AREA_ID=1 matches base-game cave convention;
cons bytes are perfect. Keep gen_rec02.py exactly as is.

## 6. Confidence

- Wall mechanism (load gate, no retry, linker skip): HIGH. Disasm-proven end to end;
  predicts today's wall location exactly (first far-GUID gate in the walk order);
  every geometric alternative measured and eliminated (coverage 94-96%, zero offset,
  dy=0.0, overlap richer than two working references, cons perfect, BC
  single-component).
- Fix 1 clearing the seam: HIGH-MEDIUM. It provably makes every mesh load; the one
  runtime unknown static analysis cannot close is whether seam handoff has an
  additional undiscovered requirement (if so, next in line are fix 2, then fix 3,
  then the paired-portal branch at 0x101f37f2/0x101f3854 per the trace doc).
- What only the walk test can confirm: the seam link forming with BC's mesh loaded,
  and the deeper 12 seams behaving identically.

## Appendix: donor GUID lists as deployed (from the merged map, sha1-matched to local)

```
Random09A               [d840e7ae own(AE), 2d2acbf5 xPTS]                 KEEP
xPassageTransitionStart [2d2acbf5 own, d840e7ae R09A]                     KEEP
BC_initialpathway       [e39fcb11 own, 57d83343 FirstXistion, 2d2acbf5]   -> [own]
drxFirstxistion_conn.   [own, e39fcb11 BC, 170d3701 FirstRoom]            -> [own]
drxFirstRoom            [own, FirstXistion, Connector1, river_ext01]      -> [own]
drxBC_Connector1        [own, FirstRoom, drxBC2, river_ext01]             -> [own]
river_extension01       [own, FirstRoom, drxBC2, Connector1]              -> [own]
drxBC2                  [own, Connector1, river_ext01, riverext02, xTTH]  -> [own]
riverextension02        [own, drxBC2, xTempleTransitionHallway]           -> [own]
xTempleTransitionHallway[own, drxBC2, riverextension02]                   -> [own]
drxBC3                  [own + 7 (incl. non-abutting oceans)]             -> [own]
drxBC_Finale            [own + 11 (incl. non-abutting oceans)]            -> [own]
+ connectors/oceans with real meshes, same treatment; bossfight is
already single-GUID; the six 148-byte ocean stubs are untouched scenery.
```
