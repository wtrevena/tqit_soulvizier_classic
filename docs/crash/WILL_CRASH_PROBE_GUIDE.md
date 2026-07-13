# WILL CRASH PROBE GUIDE - pin the blood-cave crash chamber

**Goal:** the next time the blood cave crashes, this captures **exactly which chamber's
navmesh load detonated** (and which neighbour chambers were co-resident) in ONE command.
No system changes, no gflags, no registry edits. It only watches; it never touches the game.

Background dossier (why this works): `docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md`. The crash is
heap corruption that detonates inside the engine's navmesh-load path (`ProcessRLTD`, the
`REC\x02` Recast parser) while streaming a deeper blood-cave chamber. The probe hooks that exact
path and prints the load that entered but never returned = the corrupting chamber.

---

## THE ONE COMMAND

Open **Windows PowerShell** and run:

```powershell
cd C:\Users\willi\repos\tqit_soulvizier_classic\.claude\worktrees\crash-probe
$env:PYTHONIOENCODING = 'utf-8'
py scripts\crash_probe\run_crash_probe.py
```

That is it. It will wait for `TQ.exe`, attach read-only, and print `>>> agent loaded`.

You can start it **before or after** launching the game - it polls for `TQ.exe` for up to 60
minutes and attaches the moment it appears. (Launching TQ yourself is fine; the probe only ever
**attaches** to a running game. It never starts or closes TQ, and it never restarts Steam.)

---

## WHAT YOU DO IN-GAME

1. Launch **Titan Quest AE -> Play Custom Quest -> `SoulvizierClassicDEV`** (the DEV entry) and
   load your blood-cave character, same as always.
2. Once the probe prints `>>> agent loaded`, **progress DEEPER into the blood cave** - walk from
   chamber to chamber the way you do when it crashes. Each chamber you stream is one navmesh load
   the probe is watching.
3. Keep going until **it crashes** or until about **15 minutes** have passed (whichever first).
   If it crashes, you are done - the terminal will already have the answer (see below).

You do not need to do anything special when it crashes. The moment `TQ.exe` dies, the probe
notices, prints the suspect chamber, and saves the log.

---

## WHAT GETS CAPTURED

A timestamped log at:

```
C:\Users\willi\repos\tqit_soulvizier_classic\.claude\worktrees\crash-probe\local\crash_probes\crash_probe_YYYYMMDD_HHMMSS.log
```

For every navmesh load the engine performs, it records:

- `GATE  #N  load=<chamber>` - the engine is about to load that chamber's navmesh.
- `ENTER #N  <chamber>  deps=[...]  co-resident-cluster=[...]` - the navmesh parse started, with
  the neighbour blood-cave chambers that were **co-resident** at that instant (this is the datum
  that tests the leading "co-residency / tile-collision" theory).
- `LEAVE #N  <chamber>  OK/REJECTED  alloc=... memcpy=...` - the parse finished cleanly.

**The decisive line on a crash** is an `ENTER` with **no matching `LEAVE`**. When the game dies the
probe prints a banner like:

```
==============================================================================
SESSION DETACHED (reason=process-terminated). 1 navmesh load(s) had ENTER with NO LEAVE:
  ENTER #37 drxbc_finale  (guid=...)  deps=[...]  <<<<<< PRIME CRASH SUSPECT
      alloc=512(min=..,max=..,sum=..)
      co-resident chambers at load: ['drxbc3', 'drxbc_connector2', ...]
VERDICT: the ENTER-with-no-LEAVE chamber above is the load that crashed ...
==============================================================================
```

That `PRIME CRASH SUSPECT` chamber + the `co-resident` list is the whole answer.

---

## HOW TO STOP

- **If it crashed:** nothing to do - the probe already printed the suspect and saved the log.
- **To stop early / it did not crash:** press **Ctrl+C** in the PowerShell window. The game keeps
  running untouched; the probe just detaches and saves whatever it captured.

---

## WHAT WE DO WITH THE LOG

Hand the log (or just paste the `PRIME CRASH SUSPECT` banner) to the fix agent. With the exact
chamber named, the map-side remedy in `docs/CAVE_ENTRY_CHAIN_TRACE.md` (Fix B: relocate the
cluster into disjoint world space, or connect deep chambers by interior portals so at most 1-2
navmeshes are resident at once) can be aimed precisely, and the co-resident set confirms or refutes
the tile-collision theory. If the crash turns out **not** to be inside a navmesh load, the banner
says so and lists the last chambers loaded, which is still a strong lead.

---

## OPTIONS (usually leave the defaults)

```
py scripts\crash_probe\run_crash_probe.py [--tier chambers|allocs|full] [--no-gate] [--self-test]
```

- `--tier allocs` (default) - captures chamber identity, co-residency, and per-tile **allocation**
  sizes. This is the recommended run.
- `--tier chambers` - lightest and most timing-faithful (chamber identity + co-residency only). Use
  this if you want the least possible perturbation of the crash timing.
- `--tier full` - also logs per-tile **memcpy** sizes. `memcpy` is the hottest path in the engine,
  so this adds the most overhead; use it only if the alloc + chamber signal was not enough.
- `--no-gate` - skips the one mid-function hook (`Engine+0x1b4158`). Only needed in the unlikely
  case that hook seems to disturb the game; `ProcessRLTD` enter/leave still names the chamber.
- `--self-test` - offline check: parses the deployed map and renders the agent, then exits. **Does
  not attach to anything.** Good for confirming the tooling before a play session.

The probe auto-finds the deployed DEV map
(`...\CustomMaps\SoulvizierClassicDEV\Resources\Levels.arc`, currently build36a, MD5
`60a628807c1746e7bbde14946de62107`) to translate GUIDs and indices into chamber names. Override
with `--map "<path>"` if needed.

---

## SAFETY (why this is harmless)

- **Read-only.** Every hook only reads registers/memory and logs. Nothing in the game is patched,
  no memory is written, no allocation is freed.
- **Attach-only.** It attaches to an already running `TQ.exe` and detaches cleanly. Frida
  attach/detach does **not** terminate the target - your game is never killed, and Steam is never
  restarted.
- **No system changes.** No Page-Heap, no gflags, no Image-File-Execution-Options, no registry or
  security-setting edits. (Those would need your explicit approval and are deliberately not used
  here.)

---

## TOOLING NOTES

- **Frida:** `frida 17.15.3` (Python module; verify with `py -c "import frida; print(frida.__version__)"`).
  `frida-tools 14.10.4` is also installed but the runner does **not** use it - it needs only the
  `frida` module. If Frida is ever missing: `py -m pip install --user frida`.
- **32-bit target / cross-bitness:** `TQ.exe` is a **32-bit (x86)** process; the `Engine.dll` VAs in
  the agent assume the 32-bit image (preferred base `0x10000000`). Your Python is 64-bit. Frida
  handles this automatically: it injects a matching **32-bit** agent into the 32-bit target, so
  inside the agent all pointers and module addresses are 32-bit and the RVA arithmetic is correct.
  On attach the probe prints `arch=ia32` and `cross-bitness OK`. **Caveat to watch:** if that line
  instead says `arch=x64` or a base far from `0x1...`, something is off (wrong process, or a 64-bit
  build) - stop and re-check, because the hardcoded RVAs would then be wrong. This cross-bitness
  path is the one thing that can only be fully confirmed on a live attach.
- The agent resolves `Engine.dll`'s **runtime** base at attach and adds RVAs
  (`RVA = documented_VA - 0x10000000`); it never assumes the DLL loaded at its preferred base, so
  ASLR is handled.

---

## TROUBLESHOOTING

- *"still waiting for TQ.exe"* - the game is not running yet, or is on a different account. Launch
  it; the probe attaches automatically.
- *`arch` is not `ia32`* - see the cross-bitness caveat above.
- *No `GATE`/`ENTER` lines while you walk around* - navmesh loads only fire when a **new** area
  streams in. Walk into chambers you have not been in this session (or walk out and back). Loading a
  save near the deep cave, then descending, is the surest trigger.
- *Want to prove the tooling works without playing* - run with `--self-test`.
