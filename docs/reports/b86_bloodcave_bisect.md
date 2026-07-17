# b86 - Blood Cave crash BISECT (round 1, chamber-named)

Branch: `fix/bloodcave-bisect` (worktree). Base: main `07db9dc` = build47 (LIVE on Steam + DEV).
Datum this round (Will, 2026-07-17, verbatim): *"the game crashes in the area immediately after
the first respawn fountain inside the blood cave, the one that is right behind the first door
that you open."* Prior: `docs/reports/b82_bloodcave_crash_rca.md` (3 WER dumps 0xc0000005 near-null
READ in Engine.dll navmesh-load region; NO broken record chain; MAP-STRUCTURAL).

## VERDICT (one line)
**NO structural delta exists at the chamber across the good->bad window.** The crash chambers are
BYTE-FROZEN from build25 (Jul 7) through build47 (live), every navmesh neighbor GUID resolves, and
the prime b46-minimap-wave hypothesis is refuted three independent ways. The crash is the
long-standing map-structural navmesh-streaming condition (b82's H1), present since the cave first
became walkable (crash dumps from 07-05), NOT a regression from any content wave. Per the brief, no
speculative fix is shipped; the residual is the Frida/Page-Heap probe run, now aimable at the named
chamber. Delivered this round: exact chamber mapping (the new datum enabled it), the good->bad
timeline table, the three-way refutation, the b79-encounter interaction, variant scope (Steam
AFFECTED), and one permanent hardening gate (MAP-ZONE-1) + planted negative test.

---

## 1. CHAMBER MAPPING (the new datum)

The blood-cave entry streaming chain, from the surface camp inward (level-blob GUID links decoded
from each blob's 0x0b navmesh GUID list in the live build47 map; `local/b86_probe.py`):

```
HiddenValley01 (Silk Road surface; THE respawn fountain feeb4bc6 + caravan camp at the cave mouth)
  --[SilkRdDngEntrance cave mouth GridEntrance = "the first door you open"]-->
Random09A            (idx 703, west tunnel; own d840e7ae, neighbor xPTS)
  --> xPassageTransitionStart (idx 2261; own 2d2acbf5, neighbors bc_initialpathway + Random09A)
  --> BC_initialpathway       (idx 2246; own e39fcb11, neighbors drxFirstxistion_connection + xPTS)
  --> drxFirstRoom            (idx 2248; own 170d3701; the big 1.49MB ambush chamber)
      + drxFirstxistion_connection (idx 2247; the parchment + widow letter + b79 encounter)
  --> drxBC_Connector1 -> drxBC2 -> ... deeper
```

**Chamber identification.** The blood-cave cluster actually places THREE functional respawn shrines
(all Class=`StrategicMovementRespawnShrine`, verified against `local/baseline_build47.arz`):
`respawntempleorient01` (uid `feeb4bc6`) in the HiddenValley01 cave-mouth camp;
`records\drxmap\bloodcave\respawn_hades_shrine01.dbr` deep in drxbc3; and
`records\drxmap\bloodcave\respawn_hadescave01.dbr` mid-cave in new_secretdoor_transitionhallway.
(An earlier draft claimed feeb4bc6 was the ONLY one - that was wrong; corrected here.) The referent
is nonetheless `feeb4bc6`, established by GEOGRAPHY + Will's phrase "right behind the first door,"
NOT by uniqueness: the "first door you open" is the native SilkRdDngEntrance cave mouth in
HiddenValley01, whose 60-byte GridEntrance `0x14` payload holds Random09A's GUID `d840e7ae` as its
destination RegionId (byte-proven), and the SilkRdDngEntrance_C01_Ext door sits at `0x05` idx 20.
The two deep fountains do NOT fit "right behind the first door" (grid corners drxbc3 X~4186 and
new_secretdoor X~4932, vs the first-chambers X~5500-5819), so they are ruled out as the referent.
So **"the area immediately after the fountain, behind the first door" = the first interior chambers
streamed on cave entry: Random09A -> xPassageTransitionStart -> BC_initialpathway -> drxFirstRoom**
(with drxFirstxistion_connection co-resident). This is exactly the "streaming a deeper blood-cave
chamber past the first door" region the b82/DEEP_DUMP forensics pinned as the ProcessRLTD crash site
- Will's words and the dump forensics converge on the same chambers. RESIDUAL: which of these four
first-chain blobs is the exact detonating load is what the runtime probe (sec 5) resolves. `docs/LETTER_SPAWN_DIAGNOSIS.md` independently records that Will's `_Toxeus` char "has
walked the blood cave before," consistent with an intermittent streaming-order heap detonation
(sometimes he crosses, sometimes it crashes) rather than a hard per-record wall.

**b79 interaction (drxFirstRoom + drxFirstxistion_connection).** These are the exact 2 blobs build47's
b79 relocation changed. b79 moved the 33% Blood-Toxeus ambush from drxFirstRoom (@100,1,50) to
drxFirstxistion_connection (spawn @36.0,10.005,19.5), next to the parchment. drxFirstxistion_connection
is a direct navmesh neighbor of BOTH bc_initialpathway and drxFirstRoom (GUID links above), so the
relocated encounter DOES sit inside the crash streaming chain. BUT: (a) the crashes PREDATE b79 by
over a week (dumps from 07-05; b79 landed build47 on 07-16), so b79 is not the cause; (b) the blob
diff (sec 2) shows drxFirstxistion_connection changed ONLY at build47 (b79), while the actual crash
chambers bc_initialpathway/drxFirstRoom are byte-frozen build25->build47; (c) the encounter is a DB
0x05 spawn - it does not alter navmesh co-residency and cannot cause the ProcessRLTD heap condition.
The only residual note for the fix-lane: the new content sits in a chamber the player may crash on
reaching, so it rides along automatically when the structural crash fix (cluster relocation) lands;
no separate action needed.

## 2. THE GOOD->BAD TIMELINE (the bisect)

Crash-dump inventory (`docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md`), oldest first, vs the crash
chamber blob md5 (first 10 hex) at each map baseline (`local/b86_probe.py`, `local/b86_early.py`):

| date / dump | build era | crash? | bc_initialpathway | drxFirstRoom | Random09A | xPTS |
|-------------|-----------|--------|-------------------|--------------|-----------|------|
| 07-05 20:23 / .34572 | pre-build19 | YES (Sig-A) | (build19) 296606d4f7 | a1ab51dfaa | f4f3344c07 | 974658c301 |
| 07-05 21:11 / .15412 | pre-build19 | YES (Sig-A) | " | " | " | " |
| 07-09 20:14 / .39852 | ~build30 | YES (Sig-B) | **5723d9ba1e** | **35b79ece61** | **1b76f73965** | **560bafea82** |
| 07-12 01:34 / .12980 | pre-b36 | YES (Sig-B) | 5723d9ba1e | 35b79ece61 | 1b76f73965 | 560bafea82 |
| 07-12 01:45 / .47236 | pre-b36 | YES (Sig-B) | 5723d9ba1e | 35b79ece61 | 1b76f73965 | 560bafea82 |
| 07-12 16:41 / .16080 | build36 | YES (Sig-B) | 5723d9ba1e | 35b79ece61 | 1b76f73965 | 560bafea82 |
| 07-12 16:47 / .24204 | build36 | YES (Sig-B) | 5723d9ba1e | 35b79ece61 | 1b76f73965 | 560bafea82 |
| 07-13 native dmp | build41 | YES | 5723d9ba1e | 35b79ece61 | 1b76f73965 | 560bafea82 |
| build47 (live) | build47 | Will 07-17 | 5723d9ba1e | 35b79ece61 | 1b76f73965 | 560bafea82 |

Baseline sweep (build19 / 25 / 26 / 30 / 34 / 35 / 47-canonical / 47-TESTHUB): the four crash
chambers are **byte-identical from build25 (Jul 7) through build47 (live)** - a single frozen hash
each. Only build19 (before the build20 rocks-carve + global-lattice navmesh regeneration) differs.
There is NO build at which these blobs changed while a crash appeared or disappeared: the cave has
crashed in this region continuously since it first became walkable, across ~7 distinct map builds,
with the chamber bytes unchanged.

**MY PRIME HYPOTHESIS (b46 minimap/region wave introduced a null-derefed reference) is REFUTED,
three independent ways:**
1. **Timeline.** b46 landed ~Jul 13 (b46r3 dated 2026-07-13). The crash dumps start 07-05 and recur
   through pre-b36/build36 (all before b46). A wave cannot cause a crash that predates it by a week.
2. **The b46 table contains ZERO blood-cave levels.** `LEVEL_ZONE_DBR_OVERRIDES` targets are
   uberdungeon/crypt_floor1, spartacryptlevel2, gardenofmerchants and the 11 secret_place levels;
   `SV_0X17_REGION_LABELS` targets only crypt_floor1. None is a crash chamber. Every crash chamber
   carries the untouched `easternsilkroad.dbr` zone dbr and an unmodified 0x17.
3. **Bytes + GUID resolution.** The crash chamber blobs are byte-identical across the b46 boundary
   (build34/35 -> build47), and every navmesh neighbor GUID in every crash chamber RESOLVES in the
   LEVELS index (0 unresolved; the ProcessRLTD GUID-gate input is clean). The specific b46 failure
   mode the hypothesis feared - an unresolvable neighbor GUID rejecting the 0x0b - does not exist.

## 3. CANDIDATE MECHANISM TESTED AND RULED OUT STATICALLY (honest)
b82's leading H1 is grid-seam co-residency / tile-coordinate collision. I tested a concrete static
fingerprint: do the crash chain's co-resident navmeshes overlap in XZ world space?
(`local/b86_overlap.py`.) They do - every neighbor-linked pair overlaps 64-192u. BUT the CONTROL
(`local/b86_control.py`) refutes overlap-as-fingerprint: base-game co-resident cave navmesh pairs
overlap 32-160u in **314 of 314** pairs (0 edge-abut, 0 disjoint). Navmesh-box XZ overlap is just
padded-box abutment and is completely normal; our chain sits inside the base-game distribution. So
H1 is NOT statically distinguishable from a base-game cave - it is a runtime tile-packing / streaming
condition, exactly as b82 concluded. No static offender survives.

## 4. VARIANT SCOPE - STEAM AFFECTED (yes)
The crash chambers (Random09A, xPTS, BC_initialpathway, drxFirstRoom, drxBC_Connector1, drxBC_Finale)
are BYTE-IDENTICAL between the canonical build47 map (`local/Levels_merged.arc`, 17bed65f) and the
TESTHUB variant (`local/Levels_merged_TESTHUB.arc`) - same hash in both columns. Only
drxFirstxistion_connection differs (the TESTHUB letter/hub variant). The canonical map = the Steam
build47 payload carries the identical crash chain. **Steam is AFFECTED (P0 public).** The defect is
not TESTHUB-only.

NOTE (build25->build47 entity-section deltas near the chain, NOT crash-relevant): drxFirstxistion_connection
changed via b79 (parchment relocation), and `new_secretdoor_transitionhallway.lvl` also changed its
`0x05` entity section over this span (it hosts the mid-cave respawn_hadescave01 shrine). BOTH keep a
byte-identical `0x0b` navmesh (new_secretdoor = c4cc1e6e) with all GUIDs resolving, so neither bears on
the streaming crash - noted only for completeness so the "only drxfirstxistion changed" wording is not
read as exhaustive.

## 5. FIX / RESIDUAL
No structural delta was found at the chamber, so per the brief NO speculative fix is shipped. The
decisive next step is a runtime probe on the now-named chamber. TURNKEY KIT (07-17, shipped on main
8adbf79/6e88388): Will double-clicks `scripts/RUN_CRASH_PROBE.bat` -> it waits for TQ.exe, auto-attaches,
and logs each streamed level to `local/crash_probe/probe_*.log`; on crash the last ENTER-without-LEAVE
names the corrupting chamber. Kit files: `scripts/crash_probe/run_crash_probe.py` +
`scripts/crash_probe/rltd_crash_probe.js` + guide `docs/crash/WILL_CRASH_PROBE_GUIDE.md` (the older
low-level harnesses `tools/debug/frida_test13.py` / `frida_probe.py` remain for manual/disasm work).
What the hook does, aimed at the named chain:
1. Hook the 0x0b nav-load gate `Engine+0x1b4158`: on enter read `edi`=Level*, log its GUID + name.
   Wrap ProcessRLTD `Engine+0x1f4ba0` ENTER/LEAVE. Snapshot the region-manager live-instance array
   `[[Engine+0x3743f0]+0x34]+0x50]` at entry. Walk from the HiddenValley01 camp fountain into the
   cave; the chamber that logs ENTER with no LEAVE at the crash = the corrupting load, and the
   co-resident array names its neighbors (tests H1 directly). Expected suspects, in stream order:
   Random09A, xPassageTransitionStart, BC_initialpathway, drxFirstRoom.
2. Full Page-Heap on TQ.exe (`gflags /p /enable TQ.exe /full`, size-filtered if the 32-bit LAA
   process OOMs) converts the delayed heap detonation into an immediate fault at the corrupting write.
If H1 is confirmed, the map-side remedy is `docs/CAVE_ENTRY_CHAIN_TRACE.md` Fix B (relocate the whole
blood-cave cluster into XZ-disjoint empty world space, or connect deep chambers with interior
GridEntrance portals so at most 1-2 navmeshes are co-resident) - a heavy map-structural rebuild that
coordinates with the map lane and automatically carries the b79 encounter along.

## 6. GATE (permanent) + negative test
Added `MAP-ZONE-1` to the map contract battery (`tools/contracts/contracts_map.py`,
`contract_zone_overrides` + CONTRACTS entry + `_CONTRACT_FUNCS`): every b46 LEVELS-entry
teleport-map zone `dbr` override target (read LIVE from
`svaera_plus_portals.LEVEL_ZONE_DBR_OVERRIDES`, no drift) must EXIST in the arz union. This closes
the exact zone-override-resolution gap the crash hypothesis feared (a LEVELS zone dbr pointing at an
absent record -> minimap composites against a null zone). This complements the pre-existing
`MAP-NAV-1` (already gates: every navmesh GUID resolves in the LEVELS index - the ProcessRLTD
GUID-gate class - and is GREEN on build47, itself an independent confirmation that the
unresolvable-neighbor-GUID crash class is ruled out). MAP-ZONE-1 is GREEN on build47 (4/4 targets
resolve: delphi/knossos/sparta/olympus). Planted negative test (`local/b86_gate_test.py`): a
fabricated non-existent zone dbr is correctly flagged while the 4 real targets stay clean. Full map
battery run: MAP-ZONE-1 = 0 violations (the 4 unrelated MAP-PORTAL/MAP-SD violations are older-Text
artifact-mismatch noise from `Text_deployed_prev.arc`, not introduced here).

## 7. Artifacts / repro
- `local/b86_probe.py` - chamber navmesh GUID resolution + blob-hash diff across baselines.
- `local/b86_early.py` - build19/25/26/30/34/47 chamber freeze proof.
- `local/b86_overlap.py` + `local/b86_control.py` - H1 XZ-overlap test + base-game control (refuted).
- `local/b86_gate_test.py` - MAP-ZONE-1 green + planted negative test.
(All under the worktree `local/` = gitignored scratch.)
