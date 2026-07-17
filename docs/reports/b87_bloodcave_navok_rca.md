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
(navOK stays 0). Then the region/zone code that assumes a loaded navmesh dereferences the
absent one: the Jul-13 native dump faults at Engine RVA **`0x20e270`** (~0x196d0 past
ProcessRLTD, same subsystem), **EDI=0** (null), EDX=`0x400` (the near-null 0xc0000005 the WER
dumps show). The **Blood Cult Disciple kill is the incidental trigger** - a pathfinding/region
query against the un-loaded navmesh - not the cause: the DEEP_DUMP proved the build36 .arz
mitigation changed the dump signatures by ZERO (map-side, not DB/monster driven).

**Why it works everywhere else but crashes here:** the team's deliberate design (confirmed:
`gen_bc_navmeshes.py` lines 588-599) is MULTI-GUID navmeshes + reliance on grid-streaming
co-residency. That works for chambers you ARRIVE AT BY WALKING (walking co-streams the
neighbourhood - e.g. the proven-walkable Random09A entrance is itself multi-GUID, gc=2). It
breaks ONLY at a chamber that can load in ISOLATION - a respawn/save shrine - which is exactly
`new_secretdoor`. This is the CAVE_ENTRY_CHAIN_TRACE "residency knife-edge", now pinned to the
save/respawn class.

## 4. ONSET (why it recurs, unchanged since the cave became walkable)
`new_secretdoor`'s blob + its 0x0b + its LEVELS entry are byte-frozen build25->build47 (b86 sec
2 table). The `respawn_hadescave01` shrine is upstream DRX content. So the crash has recurred at
this exact spot continuously since the cave first became walkable (crash dumps from 07-05), is
NOT a regression from any content wave, and is not save-specific beyond "the save sits on the
fountain." `drxBC3` (idx 2253, gc=6) hosts the OTHER interior respawn shrine
(`respawn_hades_shrine01`) and is the identical latent class (see the gate + BACKLOG B87).

## 5. VARIANT SCOPE - STEAM AFFECTED (yes)
`new_secretdoor`'s blob, 0x0b, GUID list, and the `respawn_hadescave01` placement are
byte-identical between canonical (`Levels_merged.arc`, the Steam build47 payload) and TESTHUB.
The MAP-NAV-4 gate (sec 7) flags the identical 2 chambers on BOTH. The crash is not TESTHUB-only.

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
crash stop? do the west/east seams still walk?). If A walks clean, extend to `drxBC3` and it is
the shippable minimal fix; if A walls a seam, escalate to **C** (portals) for the two respawn
chambers. This round ships the RCA + gate + docs; the map change is the walk-test-gated next step.

## 7. GATE (permanent) + planted negative test
`tools/contracts/gate_navmesh_coresidency.py` + `MAP-NAV-4` in the map contract battery
(`contracts_map.py` `contract_navmesh_coresidency`, added to CONTRACTS + `_CONTRACT_FUNCS`).
Invariant: **every blood-cave chamber that hosts a `StrategicMovementRespawnShrine` (a save/
respawn point loadable in isolation) must carry a single-own-GUID navmesh** (guid_count == 1).
This is the RESIDENCY half MAP-NAV-1 structurally cannot see. Class-resolved from the arz (not a
name heuristic); run against BOTH variant arcs for runtime parity. Planted negative test
(`--negtest`): respawn+multi-GUID is FLAGGED, respawn+single-GUID CLEARS, no-shrine+multi-GUID
CLEARS. On build47 it flags exactly `new_secretdoor_transitionhallway` (gc=3) and `drxBC3`
(gc=6) on BOTH variants; these are whitelisted as OPEN DEBT (B87) pending the sec-6 walk-test
fix, so any NEW respawn+multi-GUID chamber fails loud while the battery stays green.

## 8. What only an in-game run can confirm (needs Will)
- That fix A (single-own-GUID `new_secretdoor`) STOPS the crash AND keeps the west/east seams
  walkable (the one thing static analysis cannot settle - the residency/streaming timing and the
  seam stitch behaviour are runtime).
- Which chamber the deeper cave crashes at NEXT, if any (drxBC3 respawn is the predicted latent).

## 9. Artifacts / repro (all under the worktree `local/` = gitignored scratch)
- `local/b87_navok.py` - decode new_secretdoor's 0x0b GUID list + resolve `08c4c32f`/`415c9c33`
  against BOTH variants; temple_entrance_clean variant scope.
- `local/b87_topology.py` - the grid-seam-row topology + reciprocal GUID lists.
- `local/b87_areatags.py` - per-GUID area-tag histogram (seams are live, not dead deps).
- `local/b87_overlap.py` - world-space walkable overlap at the seams (127u / 63u).
- `local/b87_scope.py` - every blood-cave chamber's GUID count + portal binding.
- `local/b87_shrines.py` / `local/b87_r09.py` - respawn-shrine placement + R09 is multi-GUID.
- `tools/contracts/gate_navmesh_coresidency.py --negtest` - the gate + planted negative test.
