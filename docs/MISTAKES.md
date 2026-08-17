# MISTAKES.md - standing error log (Will's order, 2026-08-15: "everytime you make a mistake or error log it there going forward and never forget to do this")

> PROTOCOL: every mistake or error by the orchestrator OR any agent gets logged here IN THE
> SAME TURN it is discovered - what happened, the cost, the root cause, and the guard that now
> prevents it (a gate, a law, a brief clause; "none yet" is allowed but must be justified).
> Newest first. Never delete entries. Honest severity: a mistake caught before damage is still
> a mistake. This file is part of the mandatory successor read order.

## 2026-08-16

- **2026-08-16 | build101 ship operator, my own: TWO MORE battery rows exited non-zero purely
  because I gave them the wrong ARGV, and one of them is a gate this very lane put at risk** -
  (a) `validate_render_chain.py <arz>` exited **2**; it requires
  `<mod.arz> <mod_resources_dir> <game_dir>` and deliberately returns 2 rather than a PASS it
  cannot justify (its own `B-GATE-HARDEN-1` hardening). Re-run with all three: **exit 0, RESULT
  PASS, 269 pets / 3,089 art refs, 22 upstream WARNs**, and the mod-authored
  `svc_enslaver_shroudrig01.msh` resolves without a single row. (b) `validate_summon_pets.py
  <arz>` exited **1** with 72 "rig pairing NOT proven" lines; run WITHOUT the base and upstream
  `.arz` arguments it cannot tell an upstream-proven SV pet from a real defect, so it promotes
  134 known-upstream warnings into STRICT failures. **The authoritative run is the one inside
  the build, which passes all three paths: `STRICT failures : 0`, 293 soul-summon chains, 268
  pets, 134 upstream warnings, non-blocking.** **Cost: none realised, but the second one was
  nearly expensive in a different way** - R-257 explicitly narrowed `B-SUMMON-1`'s witness set
  for the three Enslaver pet tiers down to a single record, so a red from THIS gate on THIS
  ship is exactly the shape that would have been ours. **I did not wave it through: a control
  run of the same wrong invocation against the shipped build100 arz returns the IDENTICAL 72
  not-proven / 210 BROKEN counts with a set-diff of ZERO in both directions, and ZERO enslaver
  rows appear under either invocation** - so the red is pre-existing, unchanged, and provably
  not this lane's, and the "RIG PAIRING UNVOUCHED" arm did not bite. **Root cause: I wrote a
  battery of 30 rows from memory of what each gate takes instead of reading each one's usage
  line first, in a repo where several gates take multiple anchors on purpose.** **Guard: the
  battery script now carries the corrected argv for both; and the standing rule this repo
  already had is the one that saved it - print full argv beside every exit code, and read every
  non-zero exit in the log before writing it anywhere. Two of three bad rows in this battery
  were caught by that rule alone.**

- **2026-08-16 | build101 ship operator, my own: I put a FLAG THAT DOES NOT EXIST in the
  anti-inert row of the gate battery, and it exited 0 with no output** - the battery ran
  `py tools/patches/enslaver_shroud.py --verify local/build100_shipped_6b89bb5d.arz` as the
  ANTI-INERT control, the one row whose whole job is to prove the gate can still FAIL on the
  bytes that shipped and did not render. That module's `__main__` accepts `--negtest` and
  `--selftest` and nothing else, so an unknown flag is silently ignored: the script did
  nothing, printed nothing, and returned **0**. Written up unread, that row would have said
  "anti-inert control PASS" about a command that never loaded an arz. **Cost: none realised** -
  the battery prints its full argv beside every exit code (the 2026-08-15 `validate_tags`
  guard) and a zero-output row under a heading that promised a FAILURE is self-evidently
  wrong, so it was caught on the first read. **Root cause: I assumed a CLI surface instead of
  reading the 8-line `__main__` block, and an exit code of 0 was allowed to mean "passed" when
  it actually meant "did nothing".** This is the *same shape* as the b100 `--hub` and
  `lookout_uber --negtest` operator errors logged one day earlier, and the b99 entry about
  banking an exit code as a gate row. **Guard: the control is now a real driver,
  `tools/debug/b101_anti_inert.py`, which loads the arz, calls `verify()` and asserts the
  DIRECTION of the result - `--expect-green` or, by default, RED - so "did nothing" can no
  longer be mistaken for either verdict. Run both ways this ship: RED with 17 problems on the
  shipped `6b89bb5d`, GREEN on `9712f58f`. A gate row is only evidence if the run that produced
  it printed something that could have been bad.**

- **2026-08-16 | R-257 ROUND 1 SHIPPED A MODULE WHOSE STATIC GATES WERE ALL GREEN WHILE THE
  COLD BUILD WAS DEAD** - the lane put the Enslaver family on a MOD-AUTHORED mesh that exists
  in exactly one archive, and staged that archive in bootstrap Step 2e, *after* the Step 1
  database build. THREE fail-loud gates inside that build read it (`enslaver_shroud` M2,
  `validate_render_chain` A9, `champion_mesh.verify`), so the build aborted before a single
  record was touched. **The blast radius was worse than a stop:** bootstrap Step 1 caught the
  non-zero exit and copied the RAW upstream SV 0.98i database over the mod database, then
  carried on into Text/Quests/deploy - a "mod" with none of the mod in it, announced by one
  yellow line. **Cost: the vet round; a ship would have produced either a dead build or an
  unpatched database.** **Root cause: the lane treated a new BUILD-TIME dependency as
  DEPLOY-side discipline** and wrote that framing into five documents. It verified its records
  and its asset and never ran the thing that has to assemble them. **Guards, all three
  because one was not enough:** (1) `build_svc_database._preflight_mod_creatures_arc()` -
  the DATABASE owns the precondition and restages the archive itself, because the ship runbook
  drives that script directly and has never run the bootstrap; (2) bootstrap Step 0e stages it
  before Step 1 and a fired gate now STOPS the bootstrap
  (`SVC_ALLOW_UPSTREAM_FALLBACK=1` to override deliberately); (3)
  `tools/debug/r257_cold_order_control.py`, five runs, re-runnable against any checkout.
  **Standing lesson: a lane that changes what a build REQUIRES must run the build's own
  entrypoint. `--negtest` green is not "the build works", and "the ship lane owns the cold
  build" is not a gate.**

- **2026-08-16 | THE SAME LANE'S `--negtest` COULD NOT SEE ITS OWN P0s, AND MISTAKES.md HAD
  LOGGED THAT EXACT SHAPE THE DAY BEFORE** - all 29 round-1 plants ran against a dict stub
  with `_RIG_ASSET_OVERRIDE` injected, so `rig_asset_state()` - the function that walks the
  staged archives and decides the build's fate - was executed by NO plant. The two plants that
  "exercised" it injected a synthetic `('FAIL', ...)` tuple, i.e. they tested the reporting,
  not the deciding. **Root cause: a negative test that stubs the very function under test
  proves only that the caller forwards a stub.** The R-256 entry directly above this one had
  logged the same shape ("`--negtest` runs this module STANDALONE against an already-built
  arz ... and never the shared gates the module opts into") and this lane cited that entry
  elsewhere while reproducing its blind spot. **Guard: `--negtest` is now 37/37, six of them
  UNSTUBBED against real archives written to a temp tree** (no rig, stale rig, torn rig,
  missing anchor dir, and a good anchor beside a stale scratch tree). Both P0s are catchable
  by the command alone. **Standing lesson: for every gate a module owns, at least one negtest
  arm must run the REAL function against REAL inputs; a stub may stand in for the environment,
  never for the decision.**

- **2026-08-16 | A GATE ASKED A SEARCH PATH A SHIP QUESTION** - round 1's M2 arm required the
  rig in EVERY `mesh_assets.mod_resource_dirs()` hit. That function is a search path
  (`work/*/Resources` + `local/*/Resources`) whose whole purpose is to never false-fail a
  lookup; using it to ask "does the archive we SHIP carry X?" meant any stale scratch tree
  could red-lock a build whose own shipped archive was perfect, with no way for an operator to
  clear it by rebuilding the right file. **Root cause: two different questions - "can this
  resolve anywhere?" and "is this in the artifact?" - were answered from one list.** **Guard:
  `mesh_assets.shipping_resource_dir()` / `set_shipping_resource_dir()`; `build_svc_database`
  declares the anchor once (`output.parent.parent/Resources`, the one
  `validate_render_chain` has always used) and asset gates ask for it by name.** **Also
  logged, because it is a measurement error in the VET round and the record must be honest:
  the finding described "five stale det-2x scratch archives"; measured, all five
  `local/b9*_run2/Resources` are JUNCTIONS to `work/SoulvizierClassic/Resources` and the six
  paths are ONE file (same md5, same size). The defect and the fix stand; the count did not.
  `mod_resource_dirs()` now de-duplicates by real path so no future reader repeats it.**

- **2026-08-16 | THE FIFTH FILING. R-255's headline statistic was MIS-SCOPED, and that one
  mis-scope is what made a mechanism with no rendering exemplar look precedented enough to
  ship** - R-255's ruling table justified the b99 always-on channels with *"838 Monsters +
  **90 Pets**; **153** point it at a `Skill_BuffSelfToggled` exactly like ours"*. Re-measured
  this round against the vanilla `database.arz`: the two halves come from DIFFERENT POOLS.
  **All 153 `Skill_BuffSelfToggled` carriers are MONSTERS.** Across all 341 vanilla Pets,
  `initialSkillName` reaches a `Skill_BuffSelfToggled` **zero** times and a
  `charFxPakSelfNames` **zero** times; `buffSelfSkillName` reaches a `charFxPakSelfNames`
  exactly 20 times, every one a Neidan Terracotta pet on a WEAPON-HAND pak. The exact b99
  shape - Pet + always-on channel + `Skill_BuffSelfToggled` + body-attach CharFxPak - occurs
  **ZERO times in shipping data**, and the specific effect (`ShadowStalker_Smoke.dbr`) is a
  `deathEffect` in all 13 of its base-game references and is named by no CharFxPak anywhere.
  Written honestly, that table would have read "no pet precedent exists for this shape" and
  the round could not have been approved. **Cost: a full ship (build99, DEV + Steam), a
  ruling, a CLOSED backlog entry, and Will filing the same sentence a FIFTH time with a
  screenshot.** **Root cause, and it is the same class as b93's slot ceiling one round
  earlier: a statistic was computed over the union of two populations and then quoted as if
  it described the one that mattered.** b93 measured the mod's own overflow and read it as
  headroom; b99 measured Monsters and read it as Pets. Both were instrument errors dressed as
  evidence, and both passed a gate because the gate checked the RECORD CHAIN rather than
  whether anything with that shape had ever been seen to render. **Guard: R-257's EXEMPLAR
  STANDARD** - a rendering fix must name a specific creature that VISIBLY displays the effect
  through that exact mechanism, and replicate it byte for byte; where no exemplar exists, say
  so and take the one that does. `enslaver_shroud.verify()` now derives coverage from each
  wearer's `.msh` binary, and the census that would have caught this is written into the
  module docstring per pool, never as a union.

- **2026-08-16 | b99 shipped a confidence its own open debt contradicted** - `BL-R250-DEBT-1`
  ("nobody has seen this render") was carried forward and stated plainly, and in the same
  breath R-255's gate line printed *"the WHOLE Enslaver household smokes"* and BACKLOG
  recorded the item CLOSED. Both cannot be true. **The gate sentence is what a successor
  reads**, and it asserted the outcome (smokes) rather than the checked property (the shroud
  is named on two declared channels) - so the honest debt was decoration on a claim the
  headline had already made. It is the second time in a row this feature shipped that way:
  b93/R-250 did the same with "the family has the family FX". **Cost: a fifth filing landed
  on a lane whose own paperwork said the work was done, and the RCA for it had to start by
  disproving the repo's own record.** **Root cause: gate prose written as a claim about the
  GAME when the gate only ever measured the DATABASE.** **Guard: R-257 splits the verify()
  banner in two, explicitly - "WHAT IS CLAIMED: these records reach the screen by the SAME
  mechanism, through the SAME attach point, with a BYTE-IDENTICAL block, as records Will
  confirmed by eye" / "WHAT IS NOT CLAIMED: that anyone has SEEN this build render". The
  ruling, the test note and the module docstring all repeat the split verbatim, and the
  BACKLOG item stays OPEN until Will says it smokes.**

- **2026-08-16 | R-257 lane, my own: a one-word count update added a UTF-8 BOM to four files,
  including `tools/patches/__init__.py`** - bumping "27/27" to "29/29" across the ledger, BACKLOG,
  handoff and the registry was done with a PowerShell `Get-Content -Raw` / `Set-Content -Encoding
  utf8` round-trip. **In Windows PowerShell 5.1 `-Encoding utf8` means UTF-8 WITH BOM**, so all
  four files gained `EF BB BF` at byte 0 - a change to line 1 of the design ledger and of a Python
  module, in a commit whose stated content was a number. **Cost: none realised** - `git diff -U0`
  was read before committing, the BOM showed up as a line-1 hunk in three of the four, and all
  four were stripped with an explicit `read_bytes()`/`write_bytes()` pass. It also silently did
  NOT apply to the one line it was aimed at in `WILL_RULINGS.md` (a spacing mismatch), so the
  edit's only committed effect would have been the BOMs. **Root cause: a bulk text substitution
  used for a change small enough to make with a targeted edit - the round-trip rewrites the whole
  file, so its blast radius is the file, not the match.** **Guard: count/number updates in this
  lane go through targeted edits; when a bulk rewrite really is warranted, it is done in Python
  with explicit `encoding='utf-8'` and no BOM, and `git diff -U0` is read for line-1 hunks before
  the commit.**

- **2026-08-16 | R-257 lane, my own: I guarded a function I had just invented with `hasattr`,
  which would have made a typo fall back silently** - the first draft of
  `enslaver_shroud._PINNED_SMOKE_RIGS` read `_rig._norm_ref(SHROUD_RIG) if hasattr(_rig,
  '_norm_ref') else SHROUD_RIG.replace('/','\\').lower()`. `build_shroud_rig` has no
  `_norm_ref` and never did - I wrote the call and the fallback in the same line. **Cost:
  none realised, caught by reading back the file before the first run.** But the shape is the
  dangerous one: with the `hasattr`, a misspelled helper is not an `AttributeError`, it is a
  silent second code path - in a constant that decides which rigs count as smoking when the
  archives are unreadable. **Root cause: defensive-coding reflex applied to my OWN new API,
  where the only thing it can defend against is my own typo.** **Guard: the line is now a
  plain expression with no fallback; `hasattr` guards belong on foreign/optional interfaces,
  never on a function this lane authors in the same commit.** Same turn, a smaller one: a
  multi-paragraph commit message was passed to `git commit -m` through a PowerShell
  here-string and the parser split it into pathspecs, producing eight confusing `error:
  pathspec ... did not match` lines against a clean tree. Nothing was committed and nothing
  was lost, but the error text reads like a missing-file problem rather than a quoting one.
  Every commit message in this lane after that went through a file and `git commit -F`.

- **2026-08-16 | the same operator pointed `lookout_uber --negtest` at the arz that already
  contained the lane** - the b100 gate battery ran `--negtest work\...\SoulvizierClassic.arz`,
  i.e. the freshly built b100 database. The module opens by asserting it is
  `um_ushkaret_99.dbr`'s FIRST author, so it exited 1 with *"ALREADY exists ... Another lane
  now owns it"* before a single plant ran. **Cost: none realised** - the gate was re-run
  against the pre-lane build99 arz `1113f2c6`, which is the input the lane itself used and
  the only input the harness is defined over. Root cause: the battery was written with one
  `$arz` variable bound to "the artifact under test", and a negtest harness is not a checker
  of an artifact - it is a checker of a MODULE, and it needs the module's *pre-state*. **The
  dangerous shape is that this exit 1 is indistinguishable at the summary line from a real
  red**, and on a worse day it would have been read as "the lane's own gate fails on the
  shipped bytes" and blocked a good ship, or waved through as noise. **Guard:** the battery
  prints each gate's full argv beside its exit code (the 2026-08-15 guard), which is exactly
  how this was caught in one read; and the standing rule is now explicit - a `--negtest` arm
  takes the BASELINE artifact, never the artifact the wave produced.

- **2026-08-16 | the build100 ship operator launched a heavy multi-GB map build by asking a
  script for `--help`** - `py tools/svaera_plus_portals.py --help` was run to discover the
  canonical-vs-TESTHUB invocation. That script takes **no argparse at all**: `main()` ignores
  argv entirely and goes straight to loading both 680 MB `Levels.arc` inputs, so the "help
  request" was a full canonical map merge. It ran for the tool's 120s timeout and was killed
  mid-merge. **Cost: none realised** - the merge writes its output only at the very end, so
  `local/Levels_merged.arc` was verified still to be the build97 artifact (688,690,816 B,
  timestamp 2026-08-15 02:05:00, untouched), no partial file was produced, and no stray python
  survived. But the failure shape is a real hazard on this repo's laws: it started a SECOND
  heavy build while another lane's `pytest -n 8` was saturating all eight cores (measured 72.8
  CPU-seconds per 10s wall across its workers), which is exactly the "one heavy build at a
  time" law, and had it been the TESTHUB variant it would have raced the file the DEV surface
  is deployed from. **Root cause: `--help` was treated as universally safe rather than as an
  invocation of the program.** In a repo whose entry points are multi-GB batch jobs, an unknown
  flag is not a query - it is a run. **Guard:** discover a build script's flags by READING it
  (`os.environ.get('SVC_TEST_HUB')` was three lines away in the source, and the answer was an
  env var, never a flag), or run it under an explicit short timeout in a scratch `SVC_OUT_DIR`;
  never probe a `tools/` entry point with a flag it may ignore. This ship's map builds were all
  launched detached with an explicit `SVC_OUT_DIR` after the competing lane's suite had exited.

- **2026-08-16 | R-256 lookout-uber lane: I registered three clones into a shared fail-loud gate,
  violated it 22 ways, and wrote in the module's own docstring that the invariant held** - the
  lane appends `(character_vampiricbuff -> svc_ushkaret_larderbuff)`,
  `(character_vampiriaura -> svc_ushkaret_larder)` and `(summon_swarm -> svc_ushkaret_skyburial)`
  to `apply_svc_patches._BOSS_KIT_CLONES`, and `_verify_boss_kit_clone_shape` runs
  **UNCONDITIONALLY** in `run_registry_gates()`, which `build_svc_database.py` calls immediately
  after `run_registry()`. Measured by the vet - load the shipped arz, `L.apply(db,{})`, call the
  real gate: **`SystemExit: Boss-kit clone-shape invariant FAILED: 22 problem(s)`**. `summon_swarm`
  carries no `spawnObjectsTimeToLive` and no `FileDescription` and holds TWENTY `spawnObjects`
  refs, so the clone ADDED two zero-precedent fields and left 19 donor `.dbr` slots reading empty;
  `character_vampiricbuff` (619 fields) carries no `FileDescription` either. Step 1 of the module
  said, verbatim, *"Both are single-purpose clones with only EXISTING fields overridden, so the
  boss-kit clone-shape invariant holds"*, and **R-256 carried that sentence forward into the design
  law**. **Cost: the cold build was DEAD - not degraded, dead - and three green vet rounds did not
  see it.** **Root cause, and it is the sharper half: `--negtest` runs this module STANDALONE
  against an already-built arz, so it exercises `apply()` + `verify()` and never the shared gates
  the module opts into. That is exactly what `BL-R256-DEBT-5` said ("the module has still never run
  inside a real COLD BUILD") - the lane registered the debt and then treated it as paperwork.**
  A second root cause: round 3 fixed the b76 TTL defect by ADDING a field, without checking whether
  adding a field was legal for a record it had put under a shape gate; the fix for one finding
  created the P0. **Guard:** the flock now clones `melalos_zombie_summon3`, the one base-data
  monster spawn skill carrying BOTH b76 bounds natively, so the clone's shape is a strict SUBSET of
  its donor's and the invariant holds by construction; and new gate arm **V16 re-runs the REAL
  `_verify_boss_kit_clone_shape` function over this lane's own three pairs inside `verify()`**, with
  two negtest plants. **Standing lesson, written into R-256: a module that registers itself into a
  shared fail-loud gate must RUN that gate in its own `verify()`. Registering into a gate you never
  execute is indistinguishable from not being covered, and it converts your defect into someone
  else's build failure.**

- **2026-08-16 | the same lane wired its signature mechanic into a slot the engine does not read
  for it, one day after R-255 was filed for that exact error** - `um_corpsewake_28` drives its
  vampiric aura through **two** fields, `skillName5` AND `buffSelfSkillName`. The lane repointed
  only `skillName5` to the authored `svc_ushkaret_larder`, so the shipped boss named OUR aura in a
  kit slot and the **stock, shared, 6-carrier `character_vampiriaura`** in the channel the AI
  actually self-buffs from. Either the player got the plain 8.0-radius aura and every authored
  value (radius 14.0, the raised leech ladders) was dead config, or the AI refused a skill absent
  from its kit and nothing fired at all. THE LARDER is the boss's name, its soul, its lore and its
  only counterplay, and R-256, the module docstring and `WILL_TEST_GUIDE.md` all described a
  mechanic that could not reach the player. **The lane cited R-255 twice as a lesson it respected
  while making the same class of error**, and `enslaver_shroud._ALWAYS_ON_FIELDS` - the codified
  list of the two channels the skill manager reads without combat-AI selection - had been in the
  repo for one day. **Cost: caught by the round-4 vet, nothing built or shipped.** **Root cause:
  repointing the reference I went looking for instead of diffing EVERY field on the donor that
  named the record I was replacing.** **Guard:** both always-on channels now name the authored
  aura, and gate arm **V14** reds if either is ever left on the donor's stock record (2 plants, the
  first of which is the exact round-3 state). Standing lesson: when you replace a donor's skill,
  grep the donor for EVERY field holding that skill's path, not just the slot you meant to change.

- **2026-08-16 | round 4, my own: I wrote two new gate arms that reddened a clean build, and only
  the negtest baseline caught it** - the first version of **V15** whitelisted slot 5 as
  "inheritable" but then compared the slot's CLONE (`svc_ushkaret_larder`) against the whitelisted
  ANCESTOR (`character_vampiriaura`), so it reported a legitimate inherited level as a defect; and
  the first version of **V17** asserted `dropItems` dtype on the BOSS, which is flipped BOOL -> INT
  **after** this module runs by the shared soul-wiring helper - measured roster-wide, 25 of the 53
  shipped `um_`/`svc_` Boss records already declare INT, Vashkarr/Neferkha/Mnemophage/Ephialtes
  among them. Shipped as written, V17 would have reddened the build for a defect in code this lane
  does not own. **Cost: none - `--negtest` aborts if the clean baseline does not pass `verify()`,
  so both were caught in the first run, before the commit.** **Root cause: writing an invariant
  from the vet's finding text without first measuring whether the rest of the roster satisfies it.**
  **Guard:** V15 now compares the DONOR's slot against the whitelisted ancestor (so a donor change
  still reds), V17 carries an explicit per-record field list with the exclusion and its measurement
  stated in the code, and the shared-helper dtype flip is registered as `BL-R256-DEBT-7` for its own
  lane rather than smuggled into this one. Standing lesson: a new gate arm gets the same both-ways
  treatment as a fix - prove it reds on the defect AND that it is green on everything already
  shipped. **Same round, same class, third instance:** after removing the module's three
  `set_field(..., I)` slips I also deleted `DATA_TYPE_FLOAT as F` from the import as "now unused",
  having grepped only for the `, F)` call shape - `F` is in fact used ~20 times inside
  `_soul_stats`, which returns `(dtype, value)` PAIRS for soul fields that are legitimately absent
  (souls are built with bare `_ensure_record()`, never `clone_record`). `NameError: name 'F' is not
  defined`, caught by the very next run. **Cost: one wasted 10-minute negtest, nothing committed.**
  The import now carries a comment stating exactly where an explicit dtype remains legitimate, so
  the next reader does not repeat the deletion. Lesson: grep for the NAME, not for one call shape.

## 2026-08-15

- **2026-08-15 | R-256 lookout-uber lane: I stamped a ruling number into 9 files and never
  wrote the ruling - which silently DISARMED the gate that exists to catch exactly that** -
  `docs/WILL_RULINGS.md` had **zero** occurrences of `R-256` while the lane carried 14 `R-256`
  stamps in `tools/` alone (plus BACKLOG, MISTAKES and WILL_TEST_GUIDE) and had opened five
  `BL-R256-DEBT-*` rows keyed to a ruling that did not exist. The obvious half is a
  rulings-ledger process-law-1 break: Will gave a verbatim design order and it was nowhere in
  the design law of record, so anyone following an `R-256:` code comment to the ledger found
  nothing. **The expensive half is mechanical and I did not see it until the vet did:**
  `tools/gate_ruling_ids.py` derives the numbers a branch ADDS from `## R-<n> [` **headings
  only** (`added = heading_ids(mine) - heading_ids(base)`) and its driver reads `if not added:`
  before A3 - so with no heading, `added` was empty and **both A2 (no base clash) and A3 (no
  parallel-lane clash) were skipped**. The lane ran that gate, saw PASS, and banked it as a
  green row; it had in fact checked nothing. That is the precise protection built after four
  lanes simultaneously claimed R-250 on 2026-08-14. **Cost: no live collision (a git-grep over
  all 166 local branches found R-256 only on `feat/lookout-uber`) and nothing shipped - but the
  guard was inert for a full round and the next lane reading the ledger tail would have
  allocated 256 for itself.** **Root cause: treating the ledger entry as the lane's closing
  paperwork rather than as the thing that ALLOCATES the number**, so the stamps went in first
  and the heading was to follow "at the end". **Guard, now standing and written into R-256
  itself: the ledger heading is written in the SAME commit as the first `R-<n>` stamp in
  `tools/`.** A number you have stamped but not defined is a number the collision gate cannot
  see. Verified re-armed: `--vs main --branches` now prints `this branch (feat/lookout-uber)
  adds [256]` over 166 branches and passes, where before it had nothing to add.

- **2026-08-15 | the same lane shipped a boss summon with NO expiry - the exact defect class
  Will filed as a P0 game-freeze - and no gate could see it** - `svc_ushkaret_skyburial` was
  cloned from `records\skills\sv\gustleech\summon_swarm.dbr`, which measures petLimit 5,
  cooldown [7,6,5] and **no `spawnObjectsTimeToLive` field at all**. The lane repointed the
  spawn, RAISED petLimit to 6, set a cooldown - and never added the TTL. So Ushkaret's flock
  was **permanent**: minions never expired, the boss refilled the cap the instant one died, and
  the fight could never reach a steady state. That is verbatim what `tools/patches/summon_caps.py`
  exists to repair, quoting Will's own P0: *"so much lag with the monsters ... the game is
  frozen ... the infinite summon"*. **The trap that made it invisible: every b76 offender
  summon_caps fixed ALSO had a petLimit** (aktaios 9, alastor 8, undeadmelee01 5) - the
  concurrent cap was never what made them safe, the missing TTL was the defect - and
  `check_no_new_unbounded` only fires on records with **NEITHER** bound, so `petLimit 6`
  actively HID this record from the shared sweep. **Cost: caught by the round-2 vet, nothing
  built or shipped; mitigating that 6 commons is a small flock and 7 of 10 shipped uber
  SpawnPet skills sit in the same TTL-less state (registered as ambient debt, not fixed here).**
  **Root cause: assuming a clone inherits a safety field the donor never had, and reading the
  shared gate's NAME ("no new unbounded summons") instead of its PREDICATE.** **Guard:** the TTL
  is authored in the module at a value quoted from the artifact (20.0s = what all five
  `svc_`-authored summons in the shipped arz already carry, and one of the two values
  summon_caps restores), gate arm **V13** asserts BOTH bounds plus Commons-only spawning on the
  FINAL db, and **4 negtest plants** now bite - the first of which is the exact permanent state
  round 2 shipped in. Standing lesson: when a module clones a donor, diff the donor's SAFETY
  fields, not just its behaviour fields.

- **2026-08-15 | round 3, my own: I wrote a "QUESTS section untouched" verification that could
  only ever print True** - checking that the new map host is in no quest structure, I ran
  `'rhakotis05' in src.lower().split('LOOKOUT')[0][-0:]`. `[-0:]` is the WHOLE string, not an
  empty slice, so the expression tested something I had not intended and its output was
  meaningless either way; I printed it under the label `host named in any QUESTS/0x1b
  structure: True` and very nearly banked that as a gate row saying the opposite of what it
  read. **Cost: none - self-caught while reading the output, and replaced in the same turn with
  a real check** (grep `build_quest_files.py` / `svaera_plus_portals.py` / `qst_format.py` for
  the host and the record: zero hits, and quest structures hold `.qst` paths so a level fname
  cannot appear in one). **Root cause: writing a throwaway one-liner assertion inline and
  trusting its label instead of its logic.** **Guard: a verification that prints a boolean must
  be able to print BOTH values - if I cannot state the input that would make it False, it is
  not a check, it is a decoration.** Logged per R-254 because the rule is every error, not
  every expensive one. (Two harmless tool fumbles the same turn: a bash heredoc and a
  PowerShell here-string whose terminator was not at column 0, both failed loudly and cost one
  retry each.)

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
