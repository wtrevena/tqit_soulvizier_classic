# WER evidence for the blood-cave crash (read this, crash-RCA agents)

## The two crashes (Will's session tonight)
- TQ.exe.12980.dmp @ 07-12 01:34  and  TQ.exe.47236.dmp @ 07-12 01:45 (C:\Users\willi\AppData\Local\CrashDumps\)
- BOTH: Exception 0xC0000005 (access violation), Fault Module = ntdll.dll 10.0.26100.8521
- DIFFERENT exception offsets: 000431e9 vs 00062a29 -> the fault surfaces inside ntdll heap paths,
  NOT at a stable game-code address = HEAP CORRUPTION signature (corruption happens earlier in game
  code, detonates later in the allocator). NOT the clean instant-fault profile of a simple dangling
  record ref (those typically fault in Engine.dll/Game.dll at a stable offset).
- The game's OWN crash handler wrote NO .dmp.txt either time (latest native report = 07-04) and
  log.xml is empty post-relaunch -> hard fault, no flush.

## Prior sibling
- TQ.exe.39852.dmp @ 07-09 20:14 - same family (WER report dbff5b75: ntdll, c0000005).
  So this crash CLASS predates tonight and is recurring/area-correlated, not introduced today.

## Ruled out
- LAA reversion: TQ.exe LARGE_ADDRESS_AWARE bit is SET, mtime 2026-07-04 22:56 (unchanged since
  the patch). Not address-space reversion.

## Implications for the RCA
- Weight the HEAP-CORRUPTING data classes highest: (a) Monster.tpl->Pet.tpl equipment/loot field
  copies (the documented crash law - if the hound-summoner's SUMMONED records or any pet in the
  cascade carries copied equipment fields, that is this signature); (b) clone_record/dtype-corrupted
  soul items rolled on death; (c) any record with malformed field arrays the parser tolerates but
  the engine heap-corrupts on.
- The 2x repro at ~10-min intervals in the same AREA (Will not certain it was the same monster)
  also fits corruption that accumulates from the area's spawns and detonates on a kill event.
- Minidumps are available for deeper analysis (python `minidump` lib or WinDbg) if the data audit
  does not converge: extract the faulting thread stack modules from TQ.exe.47236.dmp.

## 2026-07-12 afternoon RECURRENCE (post build36/arz 63ca7cf8, petLimit 8->4 mitigation live)
Both of today's afternoon crashes are CONFIRMED REAL FAULTS -- not deploy taskkill/Steam-restart
artifacts. Evidence: both produced a full "Application Error" (Event 1000) with an actual
exception code/module/offset AND a paired WER APPCRASH (Event 1001) with a completed ~15.7MB
.dmp -- taskkill/process termination does not generate these records at all. No taskkill/Steam
entries found in the System log in the surrounding 10h window.

### Crash #1 ("earlier this afternoon", the one Will first reported)
- TQ.exe.16080.dmp @ 07-12 16:41:08 (Application Error) / 16:41:09 (WER 1001), Report Id 58a144ea
- Faulting process 0x3ED0 (16080), started 16:12:41 -> ran ~28.5 min before faulting
- Exception 0xC0000005, Fault Module ntdll.dll 10.0.26100.8521, **offset 0x00062a29**
- Fault bucket hash `495110fc25acaa8bdf5d184bfc4c993e8ff2087` -- **IDENTICAL bucket/offset** to
  TQ.exe.47236.dmp (07-12 01:45 AM) and TQ.exe.39852.dmp (07-09 20:14). This exact signature has
  now recurred 3x across 3 separate sessions/days, always at the same ntdll offset.

### Crash #2 ("just crashed AGAIN, minutes ago", deeper in the blood cave)
- TQ.exe.24204.dmp @ 07-12 16:47:36 (Application Error) / 16:47:37 (WER 1001), Report Id d25e9c4e
- Faulting process 0x5E8C (24204), started 16:42:06 -> ran only ~5.5 min before faulting (i.e.
  Will relaunched ~58s after crash #1 and died again fast, deeper in/re-entering the cave)
- Exception 0xC0000005, Fault Module ntdll.dll 10.0.26100.8521, **offset 0x000431e9**
- Fault bucket hash `7e686f83287b09b777812ebf4060b6e5bda11f` -- **IDENTICAL bucket/offset** to
  TQ.exe.12980.dmp (07-12 01:34 AM). This signature has now recurred 2x, same day, 15h apart.

### Refined theory (supersedes "varying offsets" framing)
Windows' own crash-bucketing (module+offset hash) shows this is NOT a diffusely-varying heap-smash
signature -- it is **exactly two stable, independently-recurring fault addresses** inside
ntdll's heap allocator (0x00062a29 and 0x000431e9), each reproducing bit-for-bit across different
game sessions/days/machine states. That is still consistent with heap corruption detonating late
(both addresses are deep in ntdll, not game code, so the corruption itself still happens earlier
in Engine/Game code) -- but it means there are most likely **two distinct, deterministic
corruption-inducing code paths/data shapes** (not one chaotic one). The petLimit 8->4 mitigation
(disciple_summon_bloodbeast, build36/arz 63ca7cf8) did NOT stop either recurring signature --
both fired again today post-mitigation, so that fix did not address (or only partially addresses)
the true root cause(s). Prioritize isolating what differs between the two detonation sites (likely
two different heap block-size classes / free-list states being corrupted) rather than treating
this as one unified bug.

### Game's own crash handler / logs -- STILL failing to flush
- No native `TitanQuest_*.dmp.txt` was written today for EITHER crash (latest native report file
  in `My Games\Titan Quest - Immortal Throne\` remains 07-04 22:37) -- confirms the established
  "hard fault, no flush" pattern holds for both new crashes.
- `log.xml` was rewritten fresh/empty at 16:48:23 (i.e. on the post-crash-#2 relaunch), with no
  prior in-session content preserved -- no additional forensic signal available from game logs.

### Classification
- Crash #1 (16:41, offset 00062a29 family) = REAL FAULT, recurring signature (3rd occurrence).
- Crash #2 (16:47, offset 000431e9 family) = REAL FAULT, recurring signature (2nd occurrence,
  same-day repeat of the 01:34 AM crash). Neither is a deploy taskkill or Steam-restart artifact.
- RECURRENCE CONFIRMED post-mitigation: escalate per the staged-escalation plan -- petLimit
  8->4 alone did not resolve either known signature.
