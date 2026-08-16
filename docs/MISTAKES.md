# MISTAKES.md - standing error log (Will's order, 2026-08-15: "everytime you make a mistake or error log it there going forward and never forget to do this")

> PROTOCOL: every mistake or error by the orchestrator OR any agent gets logged here IN THE
> SAME TURN it is discovered - what happened, the cost, the root cause, and the guard that now
> prevents it (a gate, a law, a brief clause; "none yet" is allowed but must be justified).
> Newest first. Never delete entries. Honest severity: a mistake caught before damage is still
> a mistake. This file is part of the mandatory successor read order.

## 2026-08-15

- **2026-08-15 | R-256 lookout-uber lane: I called a LIVE base-game encounter "a faceless
  boss proxy" in three shipped documents, without ever opening the record** - the lane
  wrote, in `tools/patches/lookout_uber.py`, in `tools/build_section_surgery.py` (twice)
  and in `docs/BACKLOG.md`, that the base game "already stands a boss proxy on that shelf
  ... and it has never had a face". `Records/Proxies Boss/LE_New/08_RhakotisLookout.dbr`
  is a live encounter: `pool1 = duneraider_01_general02` (1-3 sandvipers, championChance
  55.0 / championMax 1 from two mounted marauders and five named heroes) with
  `accessory1/Epic1/Legendary1 = {normal,epic,legendary}_goldenchest_02`. **Cost: caught
  by the round-1 vet before any build; zero shipped damage.** But the WORST part had
  already reached a Will-facing page: `WILL_TEST_GUIDE.md` stated the PASS criterion as
  "there is **exactly one** chest", and a player who clears that terrace sees two. That
  wording would have manufactured a false FAIL report from Will on content that is
  working correctly - the most expensive kind of documentation bug this project has,
  because it burns HIS time and his trust in the guide. **Root cause: inferring a
  record's behaviour from its NAME and its role in the level ("a boss proxy with no boss
  in this mod must be a marker") instead of reading it**, compounded by treating an
  absent `chanceToRun` as a disable when 3,650 of the base game's 5,393 `Class=Proxy`
  records omit it. **Guard:** any claim about what base-game content DOES is now read out
  of `database.arz` and quoted field-by-field in the same commit that makes the claim
  (this round's commit does exactly that); and every Will-facing PASS criterion is
  written from the measured end state of the AREA, never from the list of what our own
  lane placed into it. The decision that follows (leave vanilla's camp and chest alone -
  base-game deletion is WILL-VETO) is now stated in all four places instead of implied.

- **2026-08-15 | the same lane sent Will to look for an area banner at a spot where that
  banner does not exist** - `WILL_TEST_GUIDE.md` step 1 told him the top-right banner
  "says **Lookout Cave** the moment you are in the right place" at the Rhakotis03
  entrance. Measured with the placement gate's own `level_regions()` over all 2,282
  levels: rhakotis03 binds *City of Rhakotis / Rhakotis Slums / Rhakotis Library*, both
  cave rooms bind NOTHING, and `Lookout Cave` is bound by exactly one level in the whole
  world - rhakotis05, the shelf on the FAR side. Following the guide, Will looks for a
  banner at the entrance, does not see it, and concludes he is at the wrong cave. Cost:
  caught by the round-1 vet, nothing shipped. **Root cause: the lane proved a fact for
  the GATE (ORACLE 1: exactly one level binds the region) and then re-used it in the
  player instructions in the opposite direction** - "only rhakotis05 has it" is precisely
  why the entrance does not. **Guard:** navigation steps in WILL_TEST_GUIDE now name the
  measured region of each level the player actually stands on, in walking order, and the
  banner is presented as the CONFIRMATION at the far side rather than as the wayfinding
  cue. Two smaller drifts from the same round, both fixed here: a nest-prop distance
  comment carried the previous line's value (7.81u where the computed answer is 8.20u),
  and `BACKLOG.md` said the negtest plants 17 defects when it planted 24 (now 26). While
  rewriting the guide this pass I also typed "about 11 units in front of you" for a
  distance that is 16.55u from the cave mouth - self-caught and corrected before commit,
  logged here because the rule is every error, not every expensive one.

- **2026-08-15 | R-256 lookout-uber lane: the first negative test was written with a
  per-plant `copy.deepcopy(db)` and wedged the machine** - `_negtest` deep-copied the
  whole built database (51,331 records x ~618 fields) once per planted defect, 17 times.
  The process reached **744 seconds of CPU and >2 GB resident** on the FIRST copy, had to
  be force-killed, and produced nothing. **Cost: ~13 minutes of wall clock and one
  abandoned background job**; caught by the lane itself before anything shipped, but it
  burned time in a session that had real work queued. **Root cause: reaching for
  isolation-by-copy on an object whose size was already known from the same session's own
  probes** - this lane had printed "51,331 records" three times before writing that line.
  **Guard:** the negtest now MUTATES AND RESTORES a single field per plant (`_break()`
  returns an `undo()` that puts the exact prior values back, or deletes the field if it
  did not exist), and it re-runs `verify()` after every undo so a leaked mutation fails
  the test rather than silently poisoning the next plant. Same coverage - 24 planted
  defects, all red - in about a minute (26 after vet round 2 added the two R-251-volume
  plants). Anyone writing a future module negtest against a built `.arz` should copy that
  shape, never `deepcopy`.

- **2026-08-15 | the build99 ship operator ran `validate_tags` with NO arguments and
  banked the result as a gate row** - the b99 gate battery script called
  `py tools/validate_tags.py` bare; the tool printed its usage line and exited **2**, and
  that `EXIT=2` landed in the battery summary next to twelve real PASSes. Cost: none
  realised, caught on the same turn by reading the log rather than the summary, and the
  gate then ran correctly (`RESULT: PASS`, 394 mod tags, 455/455 authoritative, 0 new).
  But the failure shape is the dangerous one: a gate that never looked at the artifact
  produced a non-zero exit that could have been recorded as "red, investigate" or, worse,
  waved through as a known warning. Root cause: the battery was written from a list of
  gate NAMES instead of from each gate's documented invocation (this one needs four
  positional paths, per `scripts/bootstrap_working_mod.ps1` step 4b). **Guard:** the ship
  procedure's gate battery must print each gate's full argv next to its exit code (the
  b99 script does) and any non-zero exit is read in the log before it is written into a
  record; a usage line in a gate's output is a red flag that the gate did not run at all.

- **2026-08-15 | the same operator's first `git merge` was mangled by a PowerShell
  here-string** - `git merge --no-ff <lane> -m @'...'@; git log` was written with the
  here-string terminator on a line with a trailing `; git log`, so PowerShell did not
  treat the block as one argument and git received the message's words as refs
  (*"merge: the - not something we can merge"*). Cost: one wasted round-trip; git refused
  cleanly and nothing was staged, committed or half-merged. Root cause: composing a
  multi-line commit message inline in PowerShell, the same escaping-layers class as the
  2026-08-11 brief corruption above. **Guard:** every multi-line git message in this repo
  is written to a scratchpad file and passed with `-F <file>` (this ship's merge,
  checkpoint and gate-record commits all did).

- **2026-08-15 | R-250/b93 shipped the Enslaver's shroud into skill slots the engine
  does not read, and called it done** - the lane put `svc_enslaver_shroud` in
  `skillName19` on the wild boss and `skillName18` on all three soul-summon pet tiers.
  `Templates\TemplateBase\MonsterSkillManager.tpl` - the template `Monster.tpl` includes
  and `Pet.tpl` inherits - declares `skillName1..17` and nothing above it, and across all
  74,013 base-game records no Monster or Pet ever uses a higher slot. So the whole b93
  ship (arz `db314143`, DEV + Steam 2026-08-14) wrote four fields that nobody reads.
  **Cost: Will caught it in play** and filed the same request for a FOURTH time
  ("toxeus the murderer enslaver of souls summoned pets (when i summon them from their
  souls) still do not have the black smoke around them"), after three prior rounds had
  each reported the request as implemented. **Root cause: a measurement taken from the
  mod's own output instead of from the engine's declaration.** The lane wrote "ground
  truth: he uses skillName1..18 and the template reaches 23"; 23 is simply the highest
  slot THIS MOD had already overflowed into (`um_mnemophage_99`), so the lane measured
  its own earlier mistake and read it as headroom. This is the SAME instrument failure
  the module's own round-1 note documents (a blind reader's answer becoming design law) -
  repeated one round later, against a different binary. **Guard:** `_ENGINE_SKILL_SLOT_MAX
  = 17` with a DEAD SLOT gate that fails the build if the shroud is ever parked above it,
  and `--selftest` now re-derives the ceiling from `Templates.arc` every run, so the
  number can never again be a belief. The shroud moved to `initialSkillName` +
  `buffSelfSkillName`, the two always-on channels that template actually declares.

- **2026-08-15 | R-250/b93 scoped its parity claim to half the family** - the lane
  covered the wild boss and the three pet tiers his soul summons, and never looked at the
  marauders: neither the escorts the wild boss raises nor the pet-of-pet marauders the
  SUMMONED Enslaver raises. "The family has the family FX" was therefore never a checked
  claim, and the gate could not have caught a marauder without it. Cost: none realised
  (the marauders wear `ShadowStalker.msh` and were covered by accident, because that rig
  carries the shroud compiled in) - but it was luck, not a gate, and `champion_mesh`
  had already proved a mesh swap can silently remove exactly that coverage. Root cause:
  the roster was seeded from the summon skill and stopped there instead of walking what
  each member itself spawns. **Guard:** the roster is now a bounded WALK of the whole
  household (boss -> escorts -> pet tiers -> pet-of-pet), each member must satisfy one of
  two derived routes (MESH-embedded FX or the record-field shroud), and the negative test
  plants "strip one pet" - moving one pet-of-pet marauder onto an FX-free rig - and
  requires RED.

- **2026-08-15 | a duplicate `## R-254` heading is live on main** - `docs/WILL_RULINGS.md`
  carries R-254 twice: the death-penalty ruling (line ~8761) and Will's MISTAKES.md order
  (line ~8900). `gate_ruling_ids.py` passes because its A1 arm only counts headings in the
  dated `## R-<n> [date] STATUS` form, so the second, differently-shaped heading is
  invisible to the very gate written to make a ruling number denote one ruling. Cost: none
  yet; the number is ambiguous in every future reference. Found by this lane while
  allocating R-255; NOT fixed here (renumbering a ruling Will dictated is his call, and
  this lane's diff must stay reviewable). Registered as `BL-R255-DEBT-2`.

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
