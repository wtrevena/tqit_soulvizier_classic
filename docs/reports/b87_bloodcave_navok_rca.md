# b87 - Blood-Cave crash RCA: the runtime capture (navOK=0 co-residency), PROVEN

Branch: `fix/bloodcave-navok` (worktree). Base: main `19d0aac` (build47, LIVE on Steam + DEV).
Datum: the 2026-07-17 Frida probe caught the crash LIVE
(`local/crash_probe/probe_20260717_084445.log`) while Will played to his recurring crash spot
and killed a Blood Cult Disciple. This report supersedes the b86 chamber/fountain mapping
(which picked the wrong fountain) with the runtime ground truth, and proves the full chain end
to end on the binaries. Prior art: `b86_bloodcave_bisect.md` (bisect + entry chain, corrected
here), `b82_bloodcave_crash_rca.md` (native-dump EIP `0x20e270` forensics),
`docs/CAVE_ENTRY_CHAIN_TRACE.md` (the co-residency mechanism, disasm-proven),
`docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md` (ProcessRLTD ancestor chain).

## VERDICT (one line)
**The crash is the navmesh co-residency knife-edge, RUNTIME-PROVEN at
`new_secretdoor_transitionhallway` (the mid-cave respawn fountain `respawn_hadescave01`): its
3-GUID grid-seam navmesh fails ProcessRLTD's LIVE-residency gate when the chamber loads in
isolation (a save-load / death-respawn at the fountain), so the navmesh never loads (navOK=0)
and the region code null-derefs the absent navmesh.** It is NOT an unresolvable/missing GUID
(every listed GUID resolves in BOTH map variants - MAP-NAV-1's static check is correctly green;
the defect is the RESIDENCY half it cannot see). Steam is AFFECTED (byte-identical). The
`08c4c32f` GATE guid in the probe log is a red herring (a `Level+0x14` struct field, not a
navmesh dependency).

> **ROUND 2 (2026-07-17, post-vet).** The crash diagnosis above is unchanged and independently
> re-derived. Round 2 fixed the SHIPPED GATE, which round 1 had turned the map contract battery
> RED: the battery contract reused the BROAD b82 `BLOODCAVE_SUBSTRINGS` scope while the standalone
> gate used a narrow blood-cave pair, so the battery flagged `HiddenValley01` (a base-game Silk
> Road spawn hub whose navmesh is byte-identical to stock TQAE - a FALSE POSITIVE) and
> `RogueEncampment` (a real, un-whitelisted third SV-custom respawn chamber) and failed the gate.
> The fix replaces the fragile name scope with a name-free PROVENANCE invariant (own level GUID
> absent from stock TQAE Levels.arc = SV-custom), shared by both the gate and the battery via one
> classifier; excludes all 264 base/IT/XPack respawn+multi-GUID chambers (which ship and reload
> fine - so "respawn + multi-GUID" is NOT the crash law); flags exactly the THREE SV-custom
> respawn chambers (`new_secretdoor`, `drxBC3`, `RogueEncampment`); whitelists all three as OPEN
> DEBT; and the real map battery now runs GREEN on both variants. See sec 4, 6, 7.

---

## 1. THE PROBE EVIDENCE, READ VERBATIM (`rltd_crash_probe.js` semantics)

```
08:45:26 GATE  #1  load=?08c4c32f  edi=0x2fd2a020  guid=08c4c32f4c66dc5e60c8682be83be20a
08:45:26 ENTER #1  new_secretdoor_transitionhallway (guid=415c9c33...)
                   deps=[new_secretdoor_transitionhallway, drxbc_finale_transitionconnector, temple_entrance_clean]
                   co-resident-cluster=[new_secretdoor_transitionhallway]
         full-resident: 2257:new_secretdoor_transitionhallway(navOK=0)
08:45:32 process terminated. ENTER had NO LEAVE.
```

Reading each field against the hook (`scripts/crash_probe/rltd_crash_probe.js`):
- **GATE** hooks `Engine+0x1b4158` (`call ProcessRLTD`) and reads `og = [edi+0x14]`. That is a
  `Level`-struct field, NOT the navmesh container's own-GUID. `08c4c32f...` resolves against
  NEITHER the 2282-entry LEVELS index (`load=?`) NOR the navmesh GUID list (verified below).
  It is a transient/other struct field that merely looks GUID-shaped - a **red herring**.
- **ENTER** hooks `ProcessRLTD` (`Engine+0x1f4ba0`) and reads the REC\x02 container's own-GUID
  at `rec+16` = `415c9c33...` = `new_secretdoor_transitionhallway` (idx 2257). THIS is the
  authoritative chamber identity, and its `deps` = the navmesh's full GUID list.
- **ENTER with no LEAVE** = ProcessRLTD's frame was still active at the crash (matches the
  DEEP_DUMP ancestor chain: SEH `0x2a1ba2`, return `0x1b415d` on the faulting stack).
- **navOK=0** = `[Level+0x6a48]` (the navmesh-loaded-OK flag) is 0 for the resident chamber:
  the navmesh did not load.
- **co-resident-cluster=[new_secretdoor] alone** = at the load instant, NEITHER grid neighbour
  (`drxbc_finale_transitionconnector`, `temple_entrance_clean`) was stream-resident.

## 2. GROUND TRUTH from the deployed maps (`local/b87_navok.py`, both variants)

`new_secretdoor_transitionhallway` (idx 2257) 0x0b navmesh, IDENTICAL in canonical
(`Levels_merged.arc` 17bed65f) and TESTHUB (`Levels_merged_TESTHUB.arc` 42d83885):

```
LEVELS-index own GUID : 415c9c33294d180eaedc97b840fcf255   (== REC container own-guid)
navmesh GUID list (3) : [0] 415c9c33.. -> new_secretdoor_transitionhallway (idx 2257) OWN
                        [1] a2989bc9.. -> drxbc_finale_transitionconnector  (idx 2251)
                        [2] 4b4561e1.. -> temple_entrance_clean             (idx 2275)
GATE guid 08c4c32f in the navmesh GUID list?  FALSE
```

Every listed GUID **resolves** in the LEVELS index of BOTH variants. So the b-hypothesis
("`08c4c32f` is a navmesh GUID absent from the index -> the whole navmesh is rejected") is
**REFUTED**: `08c4c32f` is not in the list, and all three real GUIDs resolve. The
`temple_entrance_clean`-only-in-TESTHUB hypothesis is likewise **REFUTED** - it is present at
idx 2275 with the same GUID in BOTH variants (so the canonical/Steam map carries the identical
crash chain). MAP-NAV-1 (static GUID resolution) is correctly GREEN.

**The three listed GUIDs are REAL reciprocal walkable seams**, not dead deps
(`local/b87_areatags.py` + `local/b87_topology.py`): the chambers form a contiguous grid-seam
row at Z[3425,3545]:
```
drxbc_connector2 -- drxbc_finale_transitionconnector -- new_secretdoor -- temple_entrance_clean
   [4692,4812]           [4812,4932]                    [4932,5052]        [5052,5172]
```
`new_secretdoor`'s navmesh cells: 78% own, 8.4% tagged the west connector, 13.2% tagged the
east temple (21,062 handoff cells); `temple`'s navmesh tags 53% of its cells back to
`new_secretdoor`. Walkable footprints OVERLAP 127u (west) and 63u (east). These are genuine
cross-level seam handoffs (docs/CROSS_LEVEL_STITCH_RE.md), so they cannot simply be stripped.

## 3. THE MECHANISM (disasm-proven, end to end)

The engine's navmesh-load gate `ProcessRLTD` (`Engine+0x1f4ba0`, from the `0x0b` section gate
`Engine+0x1b4158`) runs, for EVERY GUID in the navmesh's list, a TWO-part check
(docs/CAVE_ENTRY_CHAIN_TRACE.md sec 3, byte-proven):
```
0x101f4d0b  find GUID in the world GUID->index map [reg+0x70]   ; not found -> FAIL
0x101f4d26  cmp [reg+0x50 + idx*4], 0                           ; region instance NOT resident -> FAIL
```
`[reg+0x50]` is a LIVE `vector<Region*>` indexed by level index, **null until that level is
stream-resident**. GUID-in-the-map (static, what MAP-NAV-1 checks) is necessary but NOT
sufficient; the neighbour level must be RESIDENT.

`new_secretdoor_transitionhallway` hosts `respawn_hadescave01.dbr`
(class `StrategicMovementRespawnShrine`, verified in `baseline_build47.arz`) = a SAVE/RESPAWN
point. Will's `_Toxeus` save sits at this fountain. On a fresh save-load or a death-respawn the
engine instantiates ONLY the player's current level - `new_secretdoor` - before grid-neighbour
streaming populates. So when `new_secretdoor`'s navmesh loads, `[reg+0x50][2251]`
(drxbc_finale_transitionconnector) and `[reg+0x50][2275]` (temple_entrance_clean) are still
null. The residency gate cannot complete -> ProcessRLTD does not set `[Level+0x6a48]`
(navOK stays 0), and the fault occurs INSIDE ProcessRLTD's own load call-tree, not after a
clean return: the DEEP_DUMP shows ProcessRLTD's frame still LIVE at the fault (its internal
return `0x1f4ff2`, past the `dtTileCache` init, is on the faulting stack; ENTER-with-no-LEAVE
in the probe confirms it never returned). The Jul-13 native dump faults at Engine RVA
**`0x20e270`** (~0x196d0 past the ProcessRLTD entry, same subsystem). The faulting instruction
(disassembled from `Engine.dll.original`, `local/vet_disasm.py`) is
`mov eax, dword ptr [ebx + edi*4]` with **EDI=0**, so the near-null base is **EBX** (an absent
navmesh/array pointer being indexed at [0]), not EDX - the `0x400` seen in the WER register
dump is incidental, not the faulting address. The **Blood Cult Disciple kill is the incidental
trigger** - a pathfinding/region query against the un-loaded navmesh - not the cause: the
DEEP_DUMP proved the build36 .arz mitigation changed the dump signatures by ZERO (map-side, not
DB/monster driven).

**Why it works everywhere else but crashes here (the true discriminator - NOT a universal law):**
"respawn + multi-GUID navmesh" is NOT itself the crash condition. The stock game ships **264
respawn chambers with multi-GUID navmeshes** (e.g. `DelphiTownStart` gc=12, `256x256MemphisCityArea`
gc=13, Utgard/Muspelheim/Jotunheim) that save and reload fine (`local/vet_basegame.py` /
`local/vet_provenance.py`). They are safe because a base region keeps its navmesh-neighbour levels
**CO-RESIDENT (region-packed)**, so ProcessRLTD's live-residency gate completes even on an isolated
respawn. The SV blood-cave / secret-place chambers are the opposite: grid-shifted into empty world
space (`gen_bc_navmeshes.py` `GRID_SHIFT`), with OFFLINE-generated multi-GUID navmeshes whose seam
neighbours are NOT co-resident on isolated load. So the crash-relevant property is the SV-custom
**co-residency structure**, not the respawn+multiGUID pair; single-own-GUID is a SUFFICIENT fix for
these chambers, not a proven-necessary universal invariant. This also works for chambers you ARRIVE
AT BY WALKING (walking co-streams the neighbourhood - the proven-walkable Random09A entrance is
itself multi-GUID, gc=2). It breaks ONLY at an SV-custom chamber that can load in ISOLATION - a
respawn/save shrine - which is exactly `new_secretdoor`. This is the CAVE_ENTRY_CHAIN_TRACE
"residency knife-edge", now pinned to the SV-custom save/respawn class.

## 4. ONSET (why it recurs, unchanged since the cave became walkable)
`new_secretdoor`'s blob + its 0x0b + its LEVELS entry are byte-frozen build25->build47 (b86 sec
2 table). The `respawn_hadescave01` shrine is upstream DRX content. So the crash has recurred at
this exact spot continuously since the cave first became walkable (crash dumps from 07-05), is
NOT a regression from any content wave, and is not save-specific beyond "the save sits on the
fountain." `drxBC3` (idx 2253, gc=6) hosts the OTHER interior respawn shrine
(`respawn_hades_shrine01`) and is the identical latent class (see the gate + BACKLOG B87).

**Same-class latent chambers (the complete set, `local/vet_provenance.py`).** The gate's
provenance scan (sec 7) surfaces exactly THREE SV-custom respawn+multi-GUID chambers on both
variants - the proven crash plus two latents:
- `new_secretdoor_transitionhallway` (gc=3, `respawn_hadescave01`) - the PROVEN crash spot.
- `drxBC3` (gc=6, `respawn_hades_shrine01`) - blood-cave interior latent.
- `XPack\Levels\Secret_Place\RogueEncampment.lvl` (gc=3, `respawntempleorient01`) - the Secret
  Place / Duister latent (round-2 addition). Its multi-GUID navmesh is produced by OUR pipeline's
  `SECRET_PLACE` cluster (`gen_bc_navmeshes.py`, neighbours `Rogue Encampment Forest Entrance` +
  `RogueEncampmentForestFiller`), it is NOT a stock level (own GUID `f31e50a1` absent from stock
  TQAE Levels.arc), and the Duister area is reachable (a rift-shrine return is wired in
  `svaera_plus_portals.py` step 2c), so its respawn temple can load in isolation exactly like the
  blood-cave chambers. Whether a save actually rests on it (and thus whether it crashes in
  practice) is a runtime/walk question, same epistemics as `drxBC3`; DEBT-registered pending Will.

## 5. VARIANT SCOPE - STEAM AFFECTED (yes)
`new_secretdoor`'s blob, 0x0b, GUID list, and the `respawn_hadescave01` placement are
byte-identical between canonical (`Levels_merged.arc`, the Steam build47 payload) and TESTHUB.
The MAP-NAV-4 gate (sec 7) flags the identical THREE SV-custom chambers on BOTH variants. The
crash is not TESTHUB-only.

## 6. THE FIX - a design tradeoff that needs Will's walk test (NOT blind-shipped)
The brief's suggested minimal fixes (add a missing level / fix a GUID / strip a dead dep) all
assumed an unresolvable/missing GUID - **ground truth refutes that premise** (sec 2). The real
defect is runtime co-residency, whose map-levers all trade crash-safety against seam
walkability, and the repo's own code + standing law say navmesh/streaming changes must be
walk-tested (build13 lattice, R09 swap). The candidates, ranked:

- **A. Single-own-GUID the respawn chambers** (retag the seam cells to own, drop the neighbour
  GUIDs): guarantees the navmesh loads in isolation (own GUID is always resident) -> crash gone.
  RISK: `gen_bc_navmeshes.py` explicitly documents single-GUID/own-tagged donors as the
  *invisible-wall* failure mode the team spent 11 fixes escaping. MITIGATION vs that failure:
  our seams retain 63-127u of walkable OVERLAP and the neighbour meshes stay multi-GUID (they
  provide the region flip from their side), so it is NOT the "stops-at-the-plane" case - but a
  seam wall is still possible and can only be confirmed by a walk. A wall is DEV-testable and
  strictly better than a hard crash, but could block progression if the walled seam is on the
  critical path. **Cheapest to build; must be walk-tested on DEV.**
- **B. Relocate the whole blood-cave cluster to XZ-disjoint empty world space**
  (CAVE_ENTRY_CHAIN_TRACE Fix B): the cave then streams as a self-contained unit so every
  neighbour is co-resident and BOTH the crash and the seams resolve. Heaviest (full ~2GB
  rebuild); the base-game-shaped remedy.
- **C. Interior GridEntrance portals between the deep chambers** (`inject_interior_portals.py`
  exists): connect chambers by position-independent portals so at most 1-2 navmeshes are
  co-resident. Medium; changes traversal feel (doors vs open seams).
- **D. Move the respawn shrine** out of a co-residency chamber into a self-contained one: removes
  the isolated-load trigger without touching navmeshes, but is a content/gameplay change and does
  not move an EXISTING save already sitting on the fountain.

Recommendation: build **A** for `new_secretdoor` on a DEV map and have Will walk-test (does the
crash stop? do the west/east seams still walk?). If A walks clean, extend to the two latents
`drxBC3` and `RogueEncampment` (each re-checked against its own seams) and it is the shippable
minimal fix; if A walls a seam, escalate to **C** (portals) for the affected respawn chambers.
This round ships the RCA + gate + docs; the map change is the walk-test-gated next step.

## 7. GATE (permanent) + planted negative test
`tools/contracts/gate_navmesh_coresidency.py` + `MAP-NAV-4` in the map contract battery
(`contracts_map.py` `contract_navmesh_coresidency`, in `CONTRACTS` + `_CONTRACT_FUNCS`). Both
call ONE shared classifier `contracts_map.scan_isolated_load_risk` so the standalone gate and the
battery can never drift apart (the round-1 defect: the gate used a NARROW blood-cave substring set
while the battery reused the BROAD b82 `BLOODCAVE_SUBSTRINGS`, so the battery flagged extra
chambers the whitelist did not cover and turned RED).

Invariant (round 2): **every SV-CUSTOM level (own level GUID ABSENT from the stock base-game
Levels.arc index) that hosts a `StrategicMovementRespawnShrine` must carry a single-own-GUID
navmesh** (guid_count == 1). The provenance test is the true, name-free discriminator: it EXCLUDES
all 264 inherited base/IT/XPack respawn+multi-GUID chambers (region-packed, proven-safe - including
the byte-identical Silk Road `HiddenValley01` spawn hub that the round-1 broad scope false-flagged),
and surfaces exactly the SV-custom respawn chambers our navmesh pipeline generates. This is the
RESIDENCY half MAP-NAV-1 structurally cannot see; shrine class-resolved from the arz union (not a
name heuristic); provenance from the base game's `Resources/Levels.arc` (cfg `base_game_dir`, which
`run_contracts` supplies by default - the contract fails loud if it is unavailable rather than
passing blind); run against BOTH variant arcs for runtime parity.

Planted negative test (`--negtest`): SV-custom respawn+multi-GUID is FLAGGED, SV-custom
respawn+single-GUID CLEARS, SV-custom no-shrine+multi-GUID CLEARS, and **base-provenance
respawn+multi-GUID CLEARS** (the false-positive class round 2 fixed). On build47 the gate flags
exactly THREE SV-custom chambers on BOTH variants - `new_secretdoor_transitionhallway` (gc=3),
`drxBC3` (gc=6), and `RogueEncampment` (gc=3) - all whitelisted as OPEN DEBT (B87) pending the
sec-6 walk-test fix, so the real map battery (`py tools/contracts/run_contracts.py --only map`)
runs GREEN (0 non-whitelisted P0/P1 on both variants) while any NEW SV-custom respawn+multi-GUID
chamber fails loud.

## 8. What only an in-game run can confirm (needs Will)
- That fix A (single-own-GUID `new_secretdoor`) STOPS the crash AND keeps the west/east seams
  walkable (the one thing static analysis cannot settle - the residency/streaming timing and the
  seam stitch behaviour are runtime).
- Which chamber the deeper cave crashes at NEXT, if any (`drxBC3` respawn is the predicted latent).
- Whether the two static-only latents actually detonate in play: `drxBC3` (blood-cave interior)
  and `RogueEncampment` (Secret Place / Duister). Both are SV-custom respawn+multi-GUID chambers
  flagged by the gate; whether a save/respawn ever rests on either - and thus whether it crashes -
  is runtime, not statically decidable. Fix A extends to each if Will hits them.

## 9. Artifacts / repro (all under the worktree `local/` = gitignored scratch)
- `local/b87_navok.py` - decode new_secretdoor's 0x0b GUID list + resolve `08c4c32f`/`415c9c33`
  against BOTH variants; temple_entrance_clean variant scope.
- `local/b87_topology.py` - the grid-seam-row topology + reciprocal GUID lists.
- `local/b87_areatags.py` - per-GUID area-tag histogram (seams are live, not dead deps).
- `local/b87_overlap.py` - world-space walkable overlap at the seams (127u / 63u).
- `local/b87_scope.py` - every blood-cave chamber's GUID count + portal binding.
- `local/b87_shrines.py` / `local/b87_r09.py` - respawn-shrine placement + R09 is multi-GUID.
- `local/vet_disasm.py` - Engine.dll disasm: ProcessRLTD residency gate + fault-site
  `mov eax,[ebx+edi*4]` at RVA 0x20e270 (EDI=0, near-null base = EBX).
- `local/vet_basegame.py` - 264 base-game respawn+multi-GUID chambers ship+work; HiddenValley01
  navmesh byte-identical to stock (the round-1 false positive).
- `local/vet_provenance.py` - the provenance invariant yields EXACTLY the 3 SV-custom chambers
  (own GUID absent from stock TQAE) on both variants; base/XPack excluded name-free.
- `tools/contracts/gate_navmesh_coresidency.py --negtest` - the gate + planted negative test
  (incl. the base-provenance false-positive control, case D).

---

## 10. FIX A round 1 - IMPLEMENTED + SHIPPED TO DEV (2026-07-17, branch `fix/navok-mapfix`, `build48-dev`)

Fix A (sec 6) was built in the PIPELINE for `new_secretdoor_transitionhallway` ONLY this round -
one variable for Will's walk test. `drxBC3` + `RogueEncampment` stay registered debt (sec 4) until
fix A verifies in-game.

**Implementation (fix-upstream, BL-103 - every rebuild reproduces it, no hand-patched arc).**
`tools/gen_bc_navmeshes.py` `ClusterConfig` gains `own_guid_only_keys`; the blood-cave cluster lists
`levels/world/xbloodcave/new_secretdoor_transitionhallway.lvl`. In `run_cluster`, the FULL multi-GUID
donor is generated and self-verified UNCHANGED first (same neighbour raster, carve, Y-align,
cross-tag as any build47 donor), THEN - for a flagged level only - `collapse_to_own_guid()` sets the
container GUID list to `[own 415c9c33]` and retags every walkable cell to own (area id 1). Only the
container GUID list and the tile `areas` plane change; the tile heights and cons are carried
byte-for-byte and a cell stays walkable iff it was before, so the walkable footprint - including the
63-127u seam overlap that keeps the seam from being a stops-at-the-plane wall - is preserved exactly.
The neighbour meshes (`drxbc_finale_transitionconnector`, `temple_entrance_clean`) still list
`new_secretdoor`'s GUID from THEIR side, so the cross-level region flip is provided from the
neighbour. Whether the seam still WALKS is the runtime question this round defers to Will.

**Why this stops the crash (sec 3 mechanism):** ProcessRLTD's live-residency gate runs, for every
listed GUID, `cmp [reg+0x50 + idx*4], 0` (region must be stream-resident). With the list collapsed
to `[own]`, the only checked region is the chamber's own, which is by definition resident when the
chamber loads. So on an isolated save-load / respawn at `respawn_hadescave01` the navmesh now loads
(navOK=1) and the region code never null-derefs an absent navmesh.

**Proofs (green; artifacts under the worktree scratch, gitignored).**
- Donor blob-diff vs the build47 donors: EXACTLY `new_secretdoor` differs (158011 -> 157898 B);
  decoded gc 3 -> 1 (own `415c9c33`); heights + cons BYTE-IDENTICAL across all 192 tiles (3 sets x
  64); unwalkable-cell count identical; 103332 seam cells (area 2/3) retagged to own (1); walkable
  total preserved (479328 == 479328).
- Both variants rebuilt to scratch (canonical `Levels_merged.arc` md5 `0be919da...` 688,691,589 B;
  TESTHUB `Levels_merged_TESTHUB.arc` md5 `c1e814e4...` 688,679,775 B). Full section-diff vs build47
  (both variants): DATA(0x02) differs by exactly -113 B; LEVELS(0x01) is a PURE offset cascade (0
  metadata/GUID/corner changes; 24 `data_offset` pointers shifted -113 from idx 2258 onward);
  QUESTS(0x1b)/GROUPS/SD/BITMAPS/DATA2/0x10 all BYTE-IDENTICAL; exactly ONE level blob differs =
  `new_secretdoor` in each variant.
- `tools/verify_merged_bc_navmeshes.py`: 24/24 real navmeshes on BOTH variants (no count change -
  the chamber still has a donor, now single-GUID; its 0x0b in the map == the new donor bytes).
- `MAP-NAV-4` standalone gate + negtest PASS; on the fixed map it checks 4 SV-custom respawn chambers
  and flags EXACTLY 2 (`drxBC3` gc=6, `RogueEncampment` gc=3) - `new_secretdoor` CLEARS. Whitelist
  shrunk to those 2. Full `--only map` battery GREEN on both variants (0 P0/0 P1; 3 pre-existing
  base-game P2 portal-noise only).
- DEPLOYED to DEV: `SoulvizierClassicDEV/Resources/Levels.arc` = the TESTHUB variant, md5
  `c1e814e4...` == built artifact; arz/Text/Quests md5 IDENTICAL before+after (untouched). No Steam
  packaging (walk-test-gated).

**Pipeline isolation note:** `svaera_plus_portals.py` and `verify_merged_bc_navmeshes.py` gained
default-preserving env overrides (`SVC_OUT_DIR`, `SVC_MERGED_ARC`; `SVC_DONOR_DIR` already existed) so
a worktree fix-wave builds to a scratch dir without clobbering the live `local/` build47 artifact.

**What only Will's walk test can settle (sec 8, unchanged):** does the crash stop AND do the west
seam (to `drxbc_finale_transitionconnector`) and east seam (to `temple_entrance_clean`) still walk?
If a seam walls, escalate `new_secretdoor` to option C (interior GridEntrance portal). If clean,
extend fix A to `drxBC3` and `RogueEncampment`.
