# tools/debug - runtime + static investigation kit for the map wall

Reusable, **read-only** probes that produced the "navmesh ruled out; it's the cross-level
walk-stitch" finding. Preserved from the session scratchpad so they survive. See
`docs/WALL_ATTEMPT_LEDGER.md` and `docs/WALL_INVESTIGATION_STATE.md` for what each proved.

Run with: `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe` and
`PYTHONIOENCODING=utf-8`. Frida is installed in that Python (`pip show frida` -> 17.x). The
Frida probes attach to the **running 32-bit TQ.exe** (launch the game first / they poll for it).
Log paths inside the scripts point at the session scratchpad - repoint if needed.

## Frida (need the game RUNNING)
- **frida_test13.py** - THE combined debugger. Hooks `ProcessRLTD` (navmesh loader) to log every
  cave navmesh load OK/REJECTED + deps, AND sweeps the region-manager table every 15s (resident
  regions, `navmeshOK` flag, dead byte, portal arrays). Auto-attaches. Start here for any walk test.
- **frida_sweep.py** - region-manager memory sweep only (global `Engine+0x3743f0` ->
  `[[G]+0x34]+0x50]` = `vector<Region*>` by level index; region: ownGUID@+0x14, Level*@+0x50
  [navmesh flag @Level+0x6a48], dead@+0x74, portals@+0x8c/+0x128; portal: destGUID@+0xdc,
  open@+0xfc, cachedDest@+0xd8).
- **frida_probe.py** - `ProcessRLTD` load hook only (OK/REJECTED + dependency GUID list).
- **frida_portals.py** - `FindCrossedPortal` hook (region portal dump on movement).
- **frida_disasm.py** - live `Instruction.parse` disassembler; use to GROUND struct offsets before
  trusting a sweep (edit the SITES dict with RVAs to dump).

## Static (no game needed)
- **seam_lattice_check.py `<map.arc>` [--gate]** - AE-vs-ours tile-lattice offset + boundary-crossing
  diff per seam. `--gate` exits nonzero unless every cluster seam is lattice-aligned (both axes).
- **scan_mouths.py** - scan `0x14`/`0x06` for cross-level GUID door-records (mouth bindings).
- **groups_probe.py** - dump GROUPS (0x11) structure + membership (proved GROUPS is not the stitch).
- **inspect_yeti.py `[arz]`** - dump yeti creature records' classification + soul drop chance
  (used to fix the normal-yeti soul-drop bug).

Engine.dll: `C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll`
(x86 PE32, ImageBase 0x10000000). Key RVAs in `docs/CAVE_ENTRY_CHAIN_TRACE.md`.
