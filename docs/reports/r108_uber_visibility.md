# R-108 wave, lane `feat/uber-visibility` - R-100 #7, R-100 #18, R-109

> **Branch** `feat/uber-visibility`, worktree `.claude/worktrees/visibility`.
> **Base** `main` @ `7efd107`, merged forward to `main` @ `9a12d17` mid-lane (see §6).
> **NOT DEPLOYED.** Nothing was written to any `CustomMaps\*` target, no Steam action, no TQ or
> Steam process launched or killed. The orchestrator owns every deploy.

Three items, all DB-only. `Levels.arc` and `Quests.arc` are untouched (zero map bytes, so the
Levels+Quests coupling does not apply). `Text.arc` IS coupled: this lane mints 3 new tags, so the
arz and Text must ship together.

| item | ruling | status |
|---|---|---|
| exclamation mark on every uber except the Devourer | R-100 #7 | IMPLEMENTED |
| the Guardians of the General must read as uber | R-100 #18 | IMPLEMENTED (one adjacent call flagged for Will) |
| tombstone XP recovery == XP lost | R-109 | IMPLEMENTED |

Full detail, with Will's words and every derivation, is appended to `docs/WILL_RULINGS.md` under the
R-100 section (`### R-100 #7 + #18 IMPLEMENTED`) and under R-109 (`### R-109 IMPLEMENTATION`). This
report is the wave record: what was measured, what was built, what was proved and what was not.

---

## 1. The one-line summary of each item

**#7** - measured first, and the measurement changed the job. The placed-uber roster on `main` was
**26 records, ALL 26 already marked**. b91 had shipped "mark all placed ubers" and it was never
deployed (R-100's own un-run-deploy note). So the only code #7 needed was the **exception**: the
Devourer ships marked and must not be. `apply()` now writes `DisplayAsQuestItem = 0` on him and the
gate asserts the 0, so a later writer cannot put it back. Roster 26 -> 25 + 1 exempt.

**#18** - Will is right on all six counts and two of them are outright bugs: the guards shipped at
`scale 1.45`, **smaller than the 1.5 warden they were cloned from**, and with a kit inherited
**verbatim** from that warden (`four_generals` added zero skills, so all six fought identically to
the trash beside them). Retuned to the amgoz1 bar: 12 distinct signature skills, two per guard,
each chosen from the epithet `four_generals` had already written into its name; `scale 2.0`; HP
derived as 45% of the general each pair guards; themed resists; `genericbossorb_03`; one
Champion-locked hoard per pair.

**#R-109** - the mechanism was found in the shipped `Game.dll`, and it **inverts the ruling's
premise in the player's favour**: the grave stores the amount ACTUALLY lost, so b93 scaled the
recovery in lockstep and the feared free-XP loop never existed. The real defect was the opposite -
recovery was 0.5x the loss, i.e. the player was punished twice, which is exactly what R-109's gate
clause forbids. One field (`RedemptionMultiplier` 0.5 -> 1.0) makes it an equality, and it stays
**derived**: retune the penalty and the marker follows with no edit.

---

## 2. What was NOT done, exhaustively

Nothing here is "triaged"; each line is either a Will decision or an unproven claim.

1. **Guardian exclamation marks - WILL DECISION.** #18 calls the six "the uber bosses we added"
   while #7 asks for markers on "all the uber bosses we made". `uber_quest_markers` rule A marks
   placed encounters that pay a SOUL; the guards pay none, and three markers per war-council room
   (general + two guards) is the map spam rule A exists to prevent. **They ship UNMARKED.** If Will
   wants them marked it is one line: a pinned extra set in `uber_quest_markers`. **Not guessed.**
2. **Guardian pair-internal silhouette - NOT DONE.** The two guards of each pair still share one
   `mesh` (`machae01b.msh` etc). Differentiating them is a mesh swap, the exact class of change
   `fix/green-mesh-swap` is in flight on and which needs an in-game check. Per-guard ambient aura FX
   (`charFxPakRunningNames`) was considered and **rejected**: the shipped candidates
   (`svc_black_poison_charfxpak`, `svc_ashsmoke_charfxpak`) are audited by the `black_poison` lane's
   own gate. The "stop being a lookalike" win here comes from `scale 2.0` + 12 distinct attack FX.
3. **NOTHING IN THIS LANE IS PROVEN IN GAME.** No TQ launch, no deploy. Specifically unproven:
   the exclamation mark actually disappearing from the Devourer's head/minimap; the guardians
   reading as uber to a player; the guardian chests actually opening on a Champion lock; the twelve
   signature skills actually firing (slot/anim wiring is validated by the build's own gates, not by
   a fight); and a character dying and recovering the full XP from a marker.
4. **`amgoz1_design_voice.md` IS STILL ABSENT** from this repo. Checked
   `git log --all --diff-filter=A -- "*amgoz*design*"` (empty) and a tree-wide `find` (no match; the
   only `amgoz` hits are upstream `.dbr` conflicted copies). The bar was reconstructed from
   CLAUDE.md/BACKLOG.md and shipped SV content, the same fallback `uber_orphan_weapons.py` recorded
   in b66. It should be authored.
5. **The Guardians' 6 records now carry a `treasureProxyName` while `um_enslaver_marauder_99` is
   deliberately orb-less** ("The Enslaver MARAUDERS stay orb-less (Champion, dropItems 0)" in
   `apply_svc_patches`). That is a real precedent tension. It is resolved in favour of Will's
   explicit #18 ask ("dont drop any orbs or anything"), and the guards' `dropItems` is measured `1`
   (the marauders' is `0`), so the two cases genuinely differ. Recorded, not hidden.
6. **The R-100 batch's other 16 items are other lanes'** (#1/#12/#13 `feat/devourer-kit`, #2
   `fix/quest-item-leaks`, #8/#16 `fix/uber-placement`, #19 `feat/soul-economy`, and so on). This
   lane touched none of them.

---

## 2b. One defect this lane produced and the build caught - worth generalising

The first full gated build **failed loud, exit 1**, on this lane's own code:

```
--- [15/47] death_xp_penalty  (Death XP penalty -90% (R-80)) ---
    death_xp_penalty: applied -> divisor 9->90, cap 500000->50000 ...
patches-registry: REGISTRY entry 'tombstone_xp_recovery' failed to import
(tools/patches/tombstone_xp_recovery.py): ModuleNotFoundError("No module named 'death_xp_penalty'")
```

`tombstone_xp_recovery` imports its sibling `death_xp_penalty` to reuse the R-80 penalty model.
`death_xp_penalty` lives in `patches/`, not `tools/`, and the registry loads modules as
`patches.<name>` (`importlib.import_module('%s.%s' % (__name__, name))`). So a **bare**
`import death_xp_penalty` resolves in CLI mode - where `patches/` is the script directory, which is
why `--negtest` and `--table` both passed 7/7 first time - and then dies inside the real build.

Two things worth keeping:
1. **A patch module importing a SIBLING patch module must import it package-relatively.** Only
   `tools/` is on `sys.path`; `tools/patches/` is not. The one existing cross-patch import in the
   tree (`_probe_legion_soul_stages.py`) uses `from patches import ...`, consistent with this.
   `general_guardians` is unaffected - it imports `apply_svc_patches`, which IS in `tools/`.
2. **The fail-loud registry did its job**, and that is the reason this is a footnote rather than a
   shipped no-op: `_load_module` raises `SystemExit` on any import failure, so a module that
   silently did nothing could not reach an artifact. A module CLI passing is not evidence the module
   runs in the build.

---

## 3. Files

| file | what |
|---|---|
| `tools/patches/tombstone_xp_recovery.py` | NEW. R-109. One field, the equality gate, 7 planted negatives. |
| `tools/debug/probe_tombstone_xp.py` | NEW, read-only. Reproduces the `Game.dll` mechanism proof. |
| `tools/patches/general_guardians.py` | NEW. R-100 #18. Retunes the six guards + three pair proxies, adds 27 hoard records, 14 planted negatives. |
| `tools/patches/uber_quest_markers.py` | R-100 #7 exemption + its gate; negtest 4 -> 8 plants. |
| `tools/patches/__init__.py` | registers the two new modules; records the ordering constraints. |
| `docs/WILL_RULINGS.md` | R-109 implementation block; R-100 #7 + #18 implementation block. |
| `docs/BACKLOG.md` | gate record + debt register entries. |

---

## 4. Proofs - commands this lane RAN, with their measured outputs

Environment for every build: `PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1
SVC_REQUIRE_GATES=1`, `py` launcher. Logs under `docs/reports/r108_logs/`.

### 4.1 The baseline, built from `main` in this environment

```
git worktree add .claude/worktrees/visibility -b feat/uber-visibility main    # main @ 7efd107
py tools/build_svc_database.py upstream/soulvizier_098i/Database/database.arz \
   upstream/soulvizier_0.9/Database/database.arz upstream/soulvizier_041/Database/database.arz \
   work/SoulvizierClassic/Database/SoulvizierClassic.arz \
   "C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"
```
**exit 0**, md5 `6a3a491db546b603c52132237c40aa63`, 55,475,226 B, 51,124 records, 45 modules.
Kept at `local/baseline_main_7efd107.arz`.

`main` then advanced to `9a12d17` (where R-109 was authored) and this branch merged it.
`git diff 7efd107 9a12d17 --numstat` -> `43 0 docs/WILL_RULINGS.md`,
`263 0 docs/wip_workflows/R-108_batch_implementation_wave.js`,
`1 1 docs/wip_workflows/R-99_all_toxeus_apex_orb.js` - docs only, so the baseline stands for both.

### 4.2 The lane build

Same command on `feat/uber-visibility`: **exit 0**, md5 `b55515970be41c2542208e84a8705640`,
55,485,062 B, **51,151** records, **47** modules. Log `r108_logs/r108_build.log`.
(The FIRST attempt exited **1** on the sibling-import bug in §2b; that is the incident, not a
footnote.)

### 4.3 Record diff - the brief's hard requirement

```
py tools/debug/r108_visibility_record_diff.py local/baseline_main_7efd107.arz \
   work/SoulvizierClassic/Database/SoulvizierClassic.arz
```
```
records  : baseline 51124 -> built 51151
ADDED 27 / REMOVED 0 / CHANGED 11
RESULT: PASS - 0 REMOVED, 27 ADDED (all 27 declared guard-hoard records), 11 CHANGED and every one
attributes to R-100 #7, R-100 #18 or R-109. Zero unattributed changes.
```
The 11 changed = 6 guards (20 fields each, all inside the declared retune set) + 3 guard-pair
proxies (accessory slots only) + `um_bloodtoxeus_99.DisplayAsQuestItem 1 -> 0` +
`gameengine.RedemptionMultiplier 0.5 -> 1.0`. Zero-delta claims re-checked: the other 25 roster
members 0 moved, the 5 dead `gameengine` lookalikes 0 moved, the R-80 penalty fields 0 moved.

**The diff tool has its own planted negative.** Diffing the baseline against ITSELF reports
`0 ADDED / 0 REMOVED / 0 CHANGED` and **exits 1** with all five expected delta classes MISSING -
because a diff that finds no unexpected change and also no expected change is a false green, which
is exactly what the sibling-import failure would have produced.

### 4.4 Gates - 29/29, re-run against the BUILT arz (`r108_logs/r108_negtests.log`)

| gate | plants | result |
|---|---|---|
| `py tools/patches/tombstone_xp_recovery.py --negtest <built arz>` | 7 | PASS 7/7 |
| `py tools/patches/uber_quest_markers.py --negtest <built arz>` | 8 | PASS 8/8 |
| `py tools/patches/general_guardians.py --negtest <built arz>` | 14 | PASS 14/14 |

The single most important row, because it is what makes R-109 "derived, not hardcoded":
`penalty RETUNED (divisor 90 -> 45, cap -> 123456) still passes untouched   expected=ACCEPT
got=ACCEPT`.

### 4.5 R-109's before/after, both ways (`r108_logs/r109_before_after_table.txt`)

`py tools/patches/tombstone_xp_recovery.py --table <arz>`. Ratio recovered/lost **0.5000 -> 1.0000**
on all three difficulties. L100 Legendary: lose 50,000, recover **50,000** (was 25,000). L85
Legendary: lose 47,765, recover **47,765** (was 23,882). L10 Normal: lose 11, recover **11** (was 5).

### 4.6 Independent read of the BUILT arz (no lane code in the loop)

The module `verify()`s above are this lane's own code checking this lane's own work, so the shipped
values were also read straight out of the built arz with a bare `ArzDatabase`:

```
svc_general_a_guard1  rank=Champion scale=2.0 life=[9110,11387,13665] orb=genericbossorb_03 regen=5.0
      added skills: minotaur_onslaught | gigantes_groundbreaker
svc_general_a_guard2  ... added skills: empusa_spirit_lifedrainnova | hero_slowspiritbolt_ring
svc_general_b_guard1  ... added skills: hero_vomitbile | empusavenomancer_venombolt
svc_general_b_guard2  ... added skills: empusa_venom_venomcloud | hero_poisonwave
svc_general_c_guard1  ... added skills: empusa_pyro_pillarofflame | hero_flamewave
svc_general_c_guard2  ... added skills: gigantes_shieldcharge | hero_bouncingfire_ring
  q_general_{a,b,c}_guardpair -> accessory1 = svc_general{a,b,c}guardhoard_pool_01
  svc_general{a,b,c}guardhoard_01  locked=1  LockedClassification=Champion  desc=tagSVCChestGeneral{A,B,C}Guard

um_bloodtoxeus_99      DisplayAsQuestItem = 0     <- R-100 #7, the Devourer stays hard to find
um_toxeus_enslaver_99  DisplayAsQuestItem = 1
um_toxeus_hunt_99      DisplayAsQuestItem = 1
um_toxeus_hunt_l_99    DisplayAsQuestItem = 1     <- the variants Will asked for, all marked

RedemptionMultiplier = 1.0
deathPenaltyEquation = (currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)   max = 50000
```

All six guards are Champion (R-106 untouched), all twelve signature skills are distinct and land on
the guard whose epithet asks for them, and the R-80 penalty is byte-intact beside the R-109 field.

### 4.7b The mechanism proof

`py tools/debug/probe_tombstone_xp.py --disasm` (read-only; opens the stock Steam `Game.dll`, walks
the PE export table, disassembles the five functions and the loader site). The symbol table and the
decisive instructions are transcribed in `docs/WILL_RULINGS.md` R-109.

### 4.7 Reproducibility, and what changed after the artifact was built

A confirming rebuild was run after the two gate/assert hardenings that landed in `6e11e0a`
(`general_guardians`' free-slot assert made idempotent; `tombstone_xp_recovery.verify` rejecting
`deathPenaltyMax <= 0` instead of dividing by it). Result recorded in the `build72-dev` gate record
in `docs/BACKLOG.md`.

Everything committed to `tools/` AFTER `6e11e0a` is docstring text, and that is **measured, not
asserted** - the two files' ASTs with docstrings stripped are identical to their `6e11e0a` versions:

```
py -c "<ast.parse + strip module/def/class docstrings + ast.dump, vs git show 6e11e0a:<file>>"
  tombstone_xp_recovery.py   AST (docstrings stripped) identical to 6e11e0a: True
  uber_quest_markers.py      AST (docstrings stripped) identical to 6e11e0a: True
  -> PASS - every post-build tools change is docstring-only
```

The two later text commits are corrections this lane made against itself rather than polish:
`7b3ecc0` narrowed an overstated "apply() writes 0" claim (true of the baseline arz, not of a fresh
build, where the module honestly prints `0 newly unmarked`), and `cf63311` separated what the
`Game.dll` disassembly MEASURES from what it lets us infer - the "a death cannot de-level you"
reading of the XP helper at `0x1017d620` is an interpretation, since the binary carries no field
names for those offsets, and R-109 does not rest on it.

---

## 5. INDEPENDENT RE-VERIFICATION (2026-07-30, second pass over the finished lane)

Everything in §4 was re-run from scratch by a second pass that trusted none of it. Four things were
checked that §4 did not cover, and one new measurement came out of it.

### 5.1 Determinism: the artifact reproduces BYTE-IDENTICALLY from committed HEAD

```
git merge main --no-edit                     # c2878b2, docs-only catch-up
py tools/build_svc_database.py <4 inputs> local/verify_rebuild.arz <base arz>
md5sum local/verify_rebuild.arz
  b55515970be41c2542208e84a8705640      <- IDENTICAL to §4.2's artifact
```

**That run exited 1, and the exit-1 is the HARNESS's fault, not the lane's** - worth recording
because it is an easy trap for the next agent. Building to `local/` instead of the `work/` layout
means the A9 render-chain gate has no `Resources/` dir beside the output, and under
`SVC_REQUIRE_GATES=1` a gate that *cannot run* is a build failure by design (B-GATE-HARDEN-1). The
build says so itself and names the remedy. Re-run into the proper `work/` layout:

```
py tools/build_svc_database.py <4 inputs> \
   work/SoulvizierClassic/Database/SoulvizierClassic.arz <base arz>
EXIT=0
b55515970be41c2542208e84a8705640 *work/SoulvizierClassic/Database/SoulvizierClassic.arz
```

**exit 0, same md5, with the FULL gate battery actually running** - the A9 render-chain gate present
(`SUMMON-PET RENDER-CHAIN VALIDATOR (A9 + D5 mesh-shader closure)`), 23 registry `verify OK` lines
including all 3 of this lane's. So the artifact is now reproduced byte-identically **three** times
(§4.2, §4.7, §5.1) and once with every gate live. Since the md5 is identical, §4.3's record-diff
result carries over unchanged by construction.

Lesson for the next agent: `SVC_REQUIRE_GATES=1` + a scratch output path = a red build that says
nothing about the code.

### 5.2 All 29 planted negatives re-run against the BUILT arz, by a second pass

`tombstone_xp_recovery` **7/7**, `uber_quest_markers` **8/8**, `general_guardians` **14/14**.
R-109's two-sided requirement is explicitly satisfied: `multiplier 2.0` (recovery ABOVE the loss)
**REJECT**, `multiplier 0.5` (recovery BELOW the loss - the pre-R-109 shipped value) **REJECT**,
`multiplier 0.1` (the hardcoded-10% form the ruling rejects) **REJECT**, and the derived-ness plant
`penalty RETUNED divisor 90 -> 45, cap -> 123456` **ACCEPT with no edit here**.

### 5.3 SHARED-RECORD LAW, audited independently rather than taken on trust

The brief names two records this project has already been bitten on. Measured baseline -> built:

| record | carriers | edited by this lane? |
|---|---|---|
| `genericbossorb_03` (the orb the Guardians now pay) | **12** (6 pre-existing + the 6 new guards) | **NO - byte-identical** |
| `genericbossorb_04` (the 21-consumer trap) | 19 | **NO - byte-identical** |
| `genericbossorb_02`, `genericbossorb_05` | 5, 8 | **NO - byte-identical** |
| `records\xpack\game\gameengine.dbr` | 1 (Game.dll literal) | yes - **exactly one field**, `RedemptionMultiplier [0.5] -> [1.0]` |

So the lane POINTED AT the shared orb and never edited it, which is the law's required shape, and the
one record it did edit moved one field.

### 5.4 The `main` baseline claim re-measured

`py tools/patches/uber_quest_markers.py --analyze local/baseline_main_7efd107.arz` ->
roster 25 / already marked 25 / **exempt 1** / would-be-newly-marked **0**. Confirms §1's headline:
b91 had already marked all 26 and the only code #7 needed was the exemption.

### 5.5 `amgoz1_design_voice.md` - absence CONFIRMED, and it never existed

`git log --all --oneline --diff-filter=A -- "*amgoz*"` -> **empty**; `git ls-files | grep -i amgoz`
-> **empty**. The file has never been added on any branch in this repo's history. §2 item 4 stands
and is understated: it is not "missing", it was never authored.

### 5.6 NEW MEASUREMENT - the derived-rule idea for the Guardian markers does NOT close

§2 item 1 leaves "do the Guardians get markers?" to Will. The natural follow-up ("then at least
derive it instead of hand-listing") was measured and **fails**: marking any placed monster that
carries a dedicated `genericbossorb_*` captures **7** records, not 6 - the 6 Guardians plus
`svc_obs_escort_permean.dbr`, an escort add that must stay unmarked. Rank cannot separate them
either (all 27 excluded adds are `champion`). Recorded in `WILL_RULINGS.md` beside the open question
so the next lane does not re-derive a rule that does not close. **The answer to WHETHER is still
Will's; this only settles that the HOW must be a pinned set, symmetric with `MARKER_EXEMPT`.**
