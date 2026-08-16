# MISTAKES.md - standing error log (Will's order, 2026-08-15: "everytime you make a mistake or error log it there going forward and never forget to do this")

> PROTOCOL: every mistake or error by the orchestrator OR any agent gets logged here IN THE
> SAME TURN it is discovered - what happened, the cost, the root cause, and the guard that now
> prevents it (a gate, a law, a brief clause; "none yet" is allowed but must be justified).
> Newest first. Never delete entries. Honest severity: a mistake caught before damage is still
> a mistake. This file is part of the mandatory successor read order.

## Seed entries (known mistakes from the 2026-07-12 .. 2026-08-15 sessions, logged retroactively)

- **2026-08-14 | R-249 TESTHUB Quests built but never deployed to DEV** - the Warden-popup fix
  shipped to Steam while Will's DEV surface silently kept the pre-fix quest arc; his A/B test
  was impossible and nothing in any doc recorded the gap. Cost: a wasted test request to Will.
  Cause: the lane's deploy step treated the TESTHUB artifact as optional. Guard: the b94-dev
  parity ship + deploy records now hash BOTH surfaces; triage waves hash live DEV files
  against build records (that is how this was caught).

- **2026-08-11..15 | ship/wait briefs referencing dead prerequisites** - the b86 and b90 ship
  briefs required waiting for "b85", a build that was cancelled after Will retracted the Gaoler
  report; the b86 ship correctly blocked forever until the brief was hand-corrected. Cost: one
  blocked lane + an orchestrator round-trip. Cause: briefs baked in a queue snapshot instead of
  discovering the queue from records. Guard: later ship briefs instruct agents to trust
  BACKLOG/git for lane state ("the machine-crash resume may have reordered landings, trust the
  records not the plan"); gate_already_shipped (2026-08-15) makes stale-queue re-ships impossible.

- **2026-08-11 | orchestrator script-editing corrupted workflow briefs 3x** - python heredoc
  edits resolved backslash-u escape sequences into raw apostrophes inside single-quoted JS
  strings, breaking the supra-wave script twice (parse errors) and costing three relaunches.
  A CRLF rewrite also broke one script (control-character rejection). Cause: editing JS string
  literals through two escaping layers. Guard: inserted brief text is now written
  apostrophe-free and files are always rewritten with LF; lesson recorded on the memory board.

- **2026-08-10/11 | overcorrection shipped, twice** - (a) R-180 fixed chest class-collapse but
  over-weighted spears (Will hit a 27%-likely 4x-same-spear run and filed "you overcorrected");
  (b) the b81 craft wave's first merge passed every gate while paying 1.3 craft-only supra
  thrown per cage run and was discarded only because the lane re-measured. Cause: fixing breadth
  without distribution/economy targets. Guard: the distribution gate family (max item/class
  expected-share thresholds) + the "gates green is not numbers sane" measurement discipline.

- **2026-08-10 | volume-trim brief written on a false premise** - the orchestrator's b84 brief
  claimed "TESTHUB keeps rich tables" when the 4 testhub farm chests shared the canonical
  records; a naive trim would have gutted Will's farm surface. Caught by the drop-matrix
  auditor before implementation. Cause: orchestrator asserted repo facts from stale memory.
  Guard: every brief now carries the STALENESS clause (trust the repo, not the brief), and the
  b84 lane was required to prove the record split from both map variants.

- **2026-07-12 | broken JSON committed to main** - the orchestrator hand-merged
  occult_hunting_golden.json, mis-resolved the conflict, and the merge commit (e686130) landed
  with conflict markers still inside; main was unbuildable until a lane repaired it. Cost: a
  broken main across a throttle boundary. Cause: hand-editing a 174k-line JSON under token
  pressure, then committing before the json.load check ran (the check and the commit were
  chained so the commit survived the failed check). Guard: validation must run BEFORE any
  commit in the same command chain, never after; merge resolutions belong to agents with vets.

- **2026-07-12 | accidental `git add -A` swept 16 worktree gitlinks into a docs commit** -
  polluted main with embedded-repo pointers; required a soft-reset re-commit. Guard: docs
  commits enumerate files explicitly; the vet checklist includes "no worktree gitlinks staged".

- **2026-07-12 | walk-through portals authored at all** - the Helos->Garden proximity teleport
  (and 16 siblings) shipped in earlier waves and trapped players on Steam; the orchestrator's
  first traveler-hub brief would have replicated the pattern had Will not stated the travel law
  mid-flight. Guard: TRAVEL LAW (NPC talk-confirm only) in every brief + the zero-walk-throughs
  gate; the hub wave was stopped and relaunched under the law.

- **2026-07-12 | ship gates lacked a QUESTS-section parity check** - the build36a hotfix ship
  brief gated blob-diffs and navmeshes but not the QUESTS registry; when Will then reported
  "all quests blocked", the gap meant the map could not be ruled out cheaply and a full RCA
  workflow ran (verdict: save-side, map was innocent - but the gate hole was real). Guard: the
  QUESTS parity gate exists and map waves must keep it green.
