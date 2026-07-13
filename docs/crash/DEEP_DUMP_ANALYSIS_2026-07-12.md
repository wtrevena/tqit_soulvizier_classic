# DEEP CRASH-DUMP ANALYSIS - blood-cave recurrence (build36, post-mitigation)

Analyst: deep crash-dump escalation pass, 2026-07-12. READ-ONLY.
Scope: all 7 TQ.exe family dumps in C:\Users\willi\AppData\Local\CrashDumps\, incl. the
2 NEW build36 dumps from today (16:41 / 16:47) = the recurrence trigger.

## TL;DR VERDICT
The recurring blood-cave crash is **heap corruption that detonates inside the engine's
navmesh-load path** - specifically `ProcessRLTD` (Engine.dll `0x101f4ba0`, the REC\x02
Recast-navmesh parser) called from the LVL-section `0x0b` load gate
(`0x101b4158`, "Error loading recast path mesh"). This fires while **streaming a deeper
blood-cave chamber**. It is **MAP-SIDE (Levels.arc navmesh path), not the .arz**, which is
exactly why the build36 DB mitigation (disciple_summon_bloodbeast petLimit 8->4) changed
NOTHING: the two build36 dumps are signature-identical to the pre-mitigation dumps.

The injected navmesh DATA is structurally clean (all 39 donors pass full FastLZ decompress
+ every REC\x02/dtTileCache invariant), so this is a **runtime** navmesh-load condition (prime
suspect: the repo's own documented grid-seam-chain co-residency knife-edge), not a malformed
blob. Root subsystem confidence HIGH; exact triggering chamber/tile not statically pinnable ->
Frida + Page-Heap plan in section 7.

---

## 1. THE 7 DUMPS - two signatures

| dump | time | build | exc | fault site | AV |
|------|------|-------|-----|-----------|-----|
| TQ.exe.34572 | 07-05 20:23 | pre | c0000005 | **heap 0x08540404** (not a module) | EXECUTE |
| TQ.exe.15412 | 07-05 21:11 | pre | c0000005 | **heap 0x03b90404** (not a module) | EXECUTE |
| TQ.exe.39852 | 07-09 20:14 | pre | c0000005 | ntdll+0x62a29 | READ @0x14 |
| TQ.exe.12980 | 07-12 01:34 | pre | c0000005 | ntdll+0x62a29 | READ @0x14 |
| TQ.exe.47236 | 07-12 01:45 | pre | c0000005 | ntdll+0x431e9 | READ @0x0 |
| **TQ.exe.16080** | **07-12 16:41** | **build36** | c0000005 | ntdll+0x62a29 | READ @0x14 |
| **TQ.exe.24204** | **07-12 16:47** | **build36** | c0000005 | ntdll+0x431e9 | READ @0x0 |

CRITICAL PARSING NOTE: TQ.exe is a **32-bit (x86) process** (Engine.dll = PE32, ImageBase
0x10000000). The prior WER_FINDINGS "varying ntdll offsets = heap corruption" read used a
64-bit context/stride and produced garbage registers. Re-parsed with CONTEXT_X86 (716-byte
context from the exception stream) + 4-byte stack stride, the picture is clean and the two
ntdll offsets are STABLE, not varying:
- Sig-B "0x14": ntdll+0x62a29, `Eax=0`, faulting insn `mov reg,[eax+0x14]` (3 dumps incl. 1 build36)
- Sig-B "0x0" : ntdll+0x431e9, `Ecx=Edx=Esi=Edi=0`, deref `[reg+0]` (2 dumps incl. 1 build36)
Both are the allocator dereferencing a **null/near-null pointer pulled from a corrupted heap
free-list / lookaside entry** = textbook delayed heap-corruption detonation. (Exact Rtl symbol
not resolved - WOW64 ntdll build not symbolized here - but the behavioral signature is
unambiguous: fault reading a tiny offset off a null base, inside ntdll, invoked from an
application alloc/free.)

Sig-A (07-05) is the SAME corruption manifesting differently: `Eax=Ecx=Edx=Ebx=0`, `Eip`
jumped to a heap address ending 0x0404 (a corrupted vtable/function pointer). Same root class
(smashed heap object), different leaf. The recurring, area-locked crash Will hits is Sig-B.

## 2. CROSS-DUMP CONVERGENCE (the whole case)
Re-scanned each faulting thread's stack at 4-byte stride. Every Sig-B dump - INCLUDING BOTH
build36 dumps - carries the identical live ancestor chain (frames are ABOVE Esp = live, not
stale), Engine.dll RVAs:

```
0x284ba0 (recursive worker, repeats many times = tree/loop dispatch)
  ... 0x2f64f0 / 0x657f0 / 0x68ee0 / 0x6a9fc ...
   -> 0x1b415d   RETURN ADDR into ProcessRLTD's caller  (the 0x0b nav-load gate)
   -> 0x2a1ba2   ProcessRLTD's SEH scope-table pointer  (pushed in its prologue)
   -> 0x1f4ff2   RETURN ADDR *inside* ProcessRLTD        (0x452 into 0x101f4ba0)
   -> ... TQ.exe object-method frames ... -> ntdll heap -> FAULT
```
Presence in all 5 Sig-B dumps: `0x1b415d`, `0x1f4ff2`, `0x2a1ba2`, `0x29a82b`, `0x68ee0`
= 5/5 each. This is not coincidence: `0x2a1ba2` is literally the value ProcessRLTD's prologue
pushes as its SEH handler (`0x101f4ba2: push 0x102a1ba2`), so seeing it on the stack PROVES
ProcessRLTD's frame is active; `0x1b415d` is ProcessRLTD's sole caller-return (documented).

## 3. WHAT THE FRAMES ARE (repo RE + capstone, VA-proven)
Cross-referenced docs/CAVE_ENTRY_CHAIN_TRACE.md + tools/analyze_createpathmesh.py, then
disassembled Engine.dll directly:

- **0x101b4158 = `call ProcessRLTD`**, inside the LVL-blob section dispatcher (`0x101b40e0`).
  Disasm shows it switches on section type `edx`: `cmp edx,0xb` -> the RLTD navmesh section ->
  `mov ecx,[edi+0x6a38]; call 0x101f4ba0`; on failure `push 0x102d8d94 "Error loading recast
  path mesh"`. `edi` = the Level being streamed. => the crash chain is the engine loading a
  level's `0x0b` navmesh during streaming.
- **0x101f4ba0 = ProcessRLTD**. Disasm confirms: parses `REC\x02` (checks 'RE','C',ver 2),
  reads the GUID list and runs the live-residency gate `cmp [reg+0x50 + idx*4],0` (matches the
  doc byte-for-byte), then **inits a `dtTileCache` (maxTiles 0x3e8) and loops EXACTLY 3 times**
  (the 3 dtTileCacheParams erosion sets), and per set loops over tiles doing:
  `size = tileHeader.field; buf = alloc(size)  [call [0x1036f01c]]; memcpy(buf, stream, size)
  [call 0x100fbb7a]; stream += size; dtTileCache::addTile(...)  [call 0x100ff4d0]`.
  => a per-tile size field from the parsed blob drives a raw alloc + memcpy with no bounds
  check. This is the heap surface. (Note: not the corrupter here, because the DATA is valid -
  see section 5 - but it is the allocator burst where corruption reliably detonates.)

## 4. WHY THE build36 MITIGATION DID NOTHING (the clincher)
build36 rebuilt the .arz (petLimit 8->4 on disciple_summon_bloodbeast; PLAN.md also shows
+83 records, 159 souls + 28 monsters CHANGED). The crash recurred with **byte-identical dump
signatures** (same two ntdll offsets, same ProcessRLTD ancestor chain). A DB-driven
monster/summon/loot corrupter would have shifted *something*. It did not. The fault lives in
the MAP navmesh-load path (Levels.arc), which build36 never touched. This also fits Will's
"progressing deeper into the blood cave" (= streaming successive chambers = successive
ProcessRLTD loads) and his uncertainty that it was the same monster (the "kill" is
area/streaming-incidental, or a death-spawned pet's pathing nudges the tile cache).

## 5. NAVMESH DATA IS CLEAN (rules out the trivial fix)
Ran `tools/rec02_format.parse_rec02(decompress=True)` (full FastLZ + all asserts: REC\x02
magic, version, payload_size==len-12, per-tile 'RLTD' magic + version, tx/ty match,
decompressed len==g*3, pos==len) over ALL 39 injected donors in local/editor_normalized/,
including the deep chambers past the first door (drxFirstRoom, drxBC2/3, drxBC_Connector1/2,
drxBC_Finale 548 tiles, drxFirstxistion_connection, drxBC_finale_transitionconnector).
**Result: 39/39 OK, 0 malformed.** So no grossly bad tile-size field. The corruption is a
RUNTIME navmesh-load condition, not static blob data.

## 6. WHAT CORRUPTS (ranked hypotheses; static analysis cannot fully separate them)
H1 (leading): **grid-seam-chain co-residency / tile-coordinate collision.** The blood cave is
a STATIC grid-seam CHAIN of ~30 levels (docs/CAVE_ENTRY_CHAIN_TRACE.md sec 7 "design note":
this has NO base-game precedent and sits on a "residency knife-edge"). Progressing deeper keeps
multiple chain chambers' navmeshes CO-RESIDENT. If two co-resident chambers' dtTileCache tiles
collide in tile space (tx,ty) because of the xBloodCave GRID_SHIFT packing, `dtTileCache::addTile`
/ the per-tile alloc loop can smash a neighbor's heap block -> detonates on the next allocator
touch (the next chamber's ProcessRLTD). Explains: map-side, depth-correlated, arz-independent,
data-structurally-clean.
H2 (secondary): **pre-existing heap corruption from a death/summon/loot event** that detonates
at the navmesh allocator burst. WEAKER: the invariant ProcessRLTD ancestor across all 5 dumps
argues the corrupter is IN the nav-load path (random pre-existing corruption would detonate
under VARYING ancestors), and the arz-mitigation no-op argues against a DB-driven corrupter.
The 6 summoned bloodhounds' dangling `dyingFxPak -> xrecords\...\fxpak_deathfx_burst.dbr`
(adv_out.txt) is a REAL data defect but was already refuted and does not match the map-side
detonation signature.

## 7. FIX PRESCRIPTION
Immediate decisive diagnosis (do this next session while Will reproduces):
1. **Full Page-Heap on TQ.exe** (gflags/Application Verifier: `gflags /p /enable TQ.exe /full`).
   This converts the delayed heap detonation into an IMMEDIATE fault at the exact corrupting
   WRITE, in the real culprit module - the single most decisive step for heap corruption.
   CAVEAT: full page-heap ~doubles allocations; on the LAA 32-bit process it may OOM - if so use
   size-filtered page heap (`/full /size <lo> <hi>`) or `/backward`, or PageHeap on Engine.dll
   allocations only.
2. **Frida ProcessRLTD ENTER/LEAVE + level id** (repo precedent: tools/debug/frida_test13.py,
   frida_probe.py already hook ProcessRLTD). Hook the caller gate `Engine+0x1b4158`: on enter
   read `edi` = Level*, log its ownGUID (`[Level+0x14]`, per frida_sweep) + name; wrap
   ProcessRLTD (`Engine+0x1f4ba0`) onEnter="ENTER guid=X payload=[edi+8]" onLeave="LEAVE al=..".
   The chamber whose navmesh load logs ENTER with **no LEAVE** at the crash = the corrupting
   load. Also hook the alloc wrapper (deref `[0x1036f01c]` at runtime) + per-tile memcpy
   (`Engine+0xfbb7a`) to log sizes, and the region-manager instance array `[[Engine+0x3743f0]
   +0x34]+0x50]` at entry to capture which neighbor chambers are co-resident (tests H1).

Map-side remedy once the chamber is named:
- If H1 confirmed: apply **CAVE_ENTRY_CHAIN_TRACE.md Fix B** - relocate the ENTIRE blood-cave
  cluster (preserving relative offsets) into XZ-disjoint empty world space with no edge-touch,
  so the cave streams as a self-contained unit and co-residency/tile packing is base-game-shaped;
  OR the robust alternative in that doc: stop chaining chambers by grid-seam and connect deep
  chambers with interior GridEntrance portals so at most 1-2 navmeshes are resident at once
  (removes the tile-collision surface). Change point: xBloodCave GRID_SHIFT in
  tools/svaera_plus_portals.py, then regenerate cluster donors + rebuild (heavy).
- Cheap parallel hardening: close the 6 bloodhound dangling `dyingFxPak` (adv_out.txt lines
  34-39) regardless - it is a real defect even if not this crash.

## 8. WHAT CHANGED vs prior WER_FINDINGS
- REFUTED: "varying ntdll offsets." They are STABLE (two fixed offsets); the "varying" was a
  64-bit mis-parse of a 32-bit process.
- UPGRADED: from "heap corruption, source unknown, weight monster-data classes" to
  "heap corruption detonating in the navmesh-load path (ProcessRLTD), map-side, depth/streaming
  -triggered" - proven by the invariant ProcessRLTD ancestor chain across all 5 Sig-B dumps
  (incl. both build36) + the arz-mitigation no-op + structurally-clean navmesh data.

## Appendix: key VAs (Engine.dll ImageBase 0x10000000)
- Section-dispatch / 0x0b nav-load gate: 0x101b40e0; `call ProcessRLTD` 0x101b4158 (ret 0x101b415d);
  fail-log "Error loading recast path mesh" 0x101b4166.
- ProcessRLTD 0x101f4ba0 (SEH push 0x102a1ba2 @0x101f4ba2; REC\x02 magic check 0x101f4c13;
  GUID residency gate 0x101f4d26; dtTileCache init call 0x101080c0 ret 0x101f4ff2; per-tile
  alloc `call [0x1036f01c]`; per-tile memcpy 0x100fbb7a; addTile 0x100ff4d0; 3-set loop bound
  `cmp eax,3` 0x101f517f).
- Region manager 0x103743f0 (+0x34 mgr, +0x50 live instance array, +0x70 GUID->idx map).
- Probes written this pass (scratchpad/crash_probes/): x86_probe.py (CONTEXT_X86 + 4-byte stack
  chain), disasm_cap.py (capstone), parse-rec02 validation run.
