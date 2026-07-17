# WILL CRASH PROBE GUIDE - pin the blood-cave crash chamber

**Goal:** the next time the blood cave crashes, this captures **exactly which chamber's
navmesh load detonated** (and which neighbour chambers were co-resident) from ONE
double-click. No system changes, no gflags, no registry edits. It only watches; it never
touches the game.

The crash is a deterministic `0xc0000005` near-null read inside the engine's navmesh-load
subsystem (`ProcessRLTD`, the `REC\x02` Recast parser; crash EIP is ~`0x196d0` past its
entry), triggered right after the first respawn fountain, behind the first door. The probe
hooks that exact path and prints the load that entered but never returned = the corrupting
chamber. Background: `docs/reports/b82_bloodcave_crash_rca.md` and
`docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md`.

---

## THE ONE DOUBLE-CLICK

Open the repo `scripts` folder and **double-click**:

```
scripts\RUN_CRASH_PROBE.bat
```

That is it. A console window opens, sets everything up, and starts waiting for `TQ.exe`.
You can double-click it **before or after** launching the game - it polls for `TQ.exe` for
up to 60 minutes and attaches the moment it appears. The window stays open the whole time
(and stays open after a crash, so you can copy the log path).

*(Prefer the terminal? `py scripts\crash_probe\run_crash_probe.py` does the same thing;
the .bat just wraps it with the right environment and a keep-open pause.)*

---

## WHAT YOU DO (the whole flow)

1. **Double-click** `scripts\RUN_CRASH_PROBE.bat`. Leave the window open; it prints
   `Waiting for TQ.exe`.
2. **Launch Titan Quest via Steam** as normal.
3. In the menu pick **Play Custom Quest -> `SoulvizierClassicDEV`** (the DEV entry) and load
   your blood-cave character.
4. When the probe window prints **`ATTACHED - play to the crash area now`**, walk to the
   blood cave and **through the first door past the first respawn fountain** - the spot that
   always crashes.
5. When it crashes, the window prints **`*** CRASH CAPTURED ***`**, the last 15 log lines,
   and a **FULL LOG** path.
6. **Send me (Claude) that FULL LOG path** and I will name the crashing chamber.

You do not need to do anything special at the moment of the crash. The instant `TQ.exe`
dies, the probe notices, prints the suspect chamber, saves the log, and keeps the window
open.

---

## WHERE THE LOG IS

A timestamped log is written to:

```
C:\Users\willi\repos\tqit_soulvizier_classic\local\crash_probe\probe_YYYYMMDD_HHMMSS.log
```

The probe prints this exact path when it starts and again after a crash.

---

## WHAT GETS CAPTURED

For every navmesh load the engine performs, it records:

- `GATE  #N  load=<chamber>` - the engine is about to load that chamber's navmesh.
- `ENTER #N  <chamber>  deps=[...]  co-resident-cluster=[...]` - the navmesh parse started,
  with the neighbour blood-cave chambers that were **co-resident** at that instant (this is
  the datum that tests the leading co-residency / tile-collision theory).
- `LEAVE #N  <chamber>  OK/REJECTED  alloc=... ` - the parse finished cleanly.

**The decisive line on a crash** is an `ENTER` with **no matching `LEAVE`**. When the game
dies the probe prints a banner like:

```
==============================================================================
SESSION DETACHED (reason=process-terminated). 1 navmesh load(s) had ENTER with NO LEAVE:
  ENTER #37 drxbc_finale  (guid=...)  deps=[...]  <<<<<< PRIME CRASH SUSPECT
      alloc=512(min=..,max=..,sum=..)
      co-resident chambers at load: ['drxbc3', 'drxbc_connector2', ...]
VERDICT: the ENTER-with-no-LEAVE chamber above is the load that crashed ...
==============================================================================

*** CRASH CAPTURED ***
--- last 15 log lines ---
...
FULL LOG: C:\Users\willi\repos\tqit_soulvizier_classic\local\crash_probe\probe_YYYYMMDD_HHMMSS.log
```

That `PRIME CRASH SUSPECT` chamber + the `co-resident` list is the whole answer. Chamber
names are already decoded from the deployed map's LEVELS index (GUID -> name), so the log
tail names the culprit with no further decoding.

---

## HOW TO STOP

- **If it crashed:** nothing to do - the probe already printed the suspect and saved the
  log. Close the window when you have copied the path.
- **To stop early / it did not crash:** press **Ctrl+C** in the probe window. The game keeps
  running untouched; the probe just detaches and saves whatever it captured. Windows may then
  ask `Terminate batch job (Y/N)?` - answer either way, the log is already saved by that point.

---

## OPTIONS (usually leave the defaults)

Everything after the .bat name is passed straight through, e.g.
`scripts\RUN_CRASH_PROBE.bat --tier chambers`:

- `--tier allocs` (default) - chamber identity, co-residency, and per-tile **allocation**
  sizes. The recommended run.
- `--tier chambers` - lightest and most timing-faithful (chamber identity + co-residency
  only). Use if you want the least possible perturbation of the crash timing.
- `--tier full` - also logs per-tile **memcpy** sizes (`memcpy` is the hottest path in the
  engine, so it adds the most overhead; use only if alloc + chamber signal was not enough).
- `--no-gate` - skips the one mid-function hook (`Engine+0x1b4158`); `ProcessRLTD`
  enter/leave still names the chamber. Only needed in the unlikely case that hook disturbs
  the game.
- `--self-test` - offline check: parses the deployed map and renders the agent, then exits.
  **Does not attach to anything.** Good for confirming the tooling before a play session.

The probe auto-finds the deployed DEV map
(`...\CustomMaps\SoulvizierClassicDEV\Resources\Levels.arc`) to translate GUIDs and indices
into chamber names. Override with `--map "<path>"` if needed.

---

## SAFETY (why this is harmless)

- **Read-only.** Every hook only reads registers/memory and logs. Nothing in the game is
  patched, no memory is written, no allocation is freed.
- **Attach-only.** It attaches to an already running `TQ.exe` and detaches cleanly. Frida
  attach/detach does **not** terminate the target - your game is never killed, and Steam is
  never restarted.
- **No system changes.** No Page-Heap, no gflags, no Image-File-Execution-Options, no
  registry or security-setting edits.

---

## TOOLING NOTES

- **Frida:** `frida 17.15.3` (Python module; verify with
  `py -c "import frida; print(frida.__version__)"`). If Frida is ever missing:
  `py -m pip install --user frida`.
- **32-bit target / cross-bitness:** `TQ.exe` is a **32-bit (x86)** process; the `Engine.dll`
  VAs in the agent assume the 32-bit image (preferred base `0x10000000`). Your Python is
  64-bit. Frida injects a matching **32-bit** agent into the 32-bit target, so inside the
  agent all pointers and module addresses are 32-bit and the RVA arithmetic is correct. On
  attach the probe prints `arch=ia32` and `cross-bitness OK`. **Caveat:** if that line instead
  says `arch=x64` or a base far from `0x1...`, something is off (wrong process) - stop and
  re-check, because the hardcoded RVAs would then be wrong.
- The agent resolves `Engine.dll`'s **runtime** base at attach and adds RVAs
  (`RVA = documented_VA - 0x10000000`), so ASLR is handled.

---

## TROUBLESHOOTING

- *"still waiting for TQ.exe"* - the game is not running yet, or is on a different account.
  Launch it via Steam; the probe attaches automatically.
- *`arch` is not `ia32`* - see the cross-bitness caveat above.
- *No `GATE`/`ENTER` lines while you walk around* - navmesh loads only fire when a **new**
  area streams in. Walk into chambers you have not been in this session (or walk out and
  back). Loading a save near the deep cave, then descending, is the surest trigger.
- *Want to prove the tooling works without playing* - run
  `scripts\RUN_CRASH_PROBE.bat --self-test`.
