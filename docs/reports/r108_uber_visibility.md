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

> **🛑 ROUND-2 CORRECTION (2026-08-05).** Round 1 wired twelve skills; **four of them could not
> fire**, and this report said so nowhere. The machae animation table
> (`anm_machae.dbr`, bound by all six via `charAnimationTableName`) declares exactly four clips -
> `HeavyShot / Slam / Strike / ThunderClap` - and `hero_vomitbile` ('Belch'),
> `empusavenomancer_venombolt` ('Belch'), `hero_flamewave` ('ShadowScythe') and
> `gigantes_shieldcharge` ('Charge') all name something else, so `SkillManager::StartSkill` aborted
> them silently (the b42 mechanism). The inherited slot-1 `shieldcharge` ('ShieldCharge') was dead
> the same way on all six. **20 dead cast slots; Bhikru the Bilespitter had ZERO castable specials
> of any kind.** Round 2 clones each of those five into `records\skills\svc\` with a blanked
> `skillSpecialAnimationName` and repoints the guards, and `verify()` now enforces the invariant
> per creature. Accurate statement now: **12 distinct signature skills, 8 pointed at the shipped
> record and 4 riding a blank-anim clone, plus a fifth clone for the slot-1 special on all six -
> and every one of them can fire.** Full detail in `docs/WILL_RULINGS.md` (R-100 #18, round-2
> correction block).

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
   own gate. The "stop being a lookalike" win here comes from `scale 2.0` + 12 distinct attack FX
   (round 1 claimed that win while 4 of the 12 were mechanically dead; see the round-2 correction
   above - the claim only became true after round 2's blank-anim clones).
3. **NOTHING IN THIS LANE IS PROVEN IN GAME.** No TQ launch, no deploy. Specifically unproven:
   the exclamation mark actually disappearing from the Devourer's head/minimap; the guardians
   reading as uber to a player; the guardian chests actually opening on a Champion lock; the twelve
   signature skills actually firing (round 2 now proves, from the built `.arz`, that no skill names
   a clip the machae rig lacks - which is the mechanism that WAS killing four of them; the remaining
   unproven part is only the in-fight cast, not the animation binding); and a character dying and
   recovering the full XP from a marker.
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
| `tools/patches/general_guardians.py` | NEW. R-100 #18. Retunes the six guards + three pair proxies, adds 27 hoard records **+ 5 blank-anim skill clones (round 2)**, **22** planted negatives, and the castability invariant. |
| `tools/debug/r108_visibility_record_diff.py` | round 2: knows the 5 clones (derived, required) and proves the 5 DONORS did not move. |
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

⚠️ **ROUND-1 NUMBERS. The `general_guardians` row is superseded by section 7:** those 14 plants all
passed while four of the twelve signature skills could not fire, which is the whole point of the
round-2 correction. Round 2's suite is **22**, PASS 22/22 on both the baseline and the built arz.

| gate | plants | result |
|---|---|---|
| `py tools/patches/tombstone_xp_recovery.py --negtest <built arz>` | 7 | PASS 7/7 |
| `py tools/patches/uber_quest_markers.py --negtest <built arz>` | 8 | PASS 8/8 |
| `py tools/patches/general_guardians.py --negtest <built arz>` | 14 (round 1) -> **22 (round 2)** | round 1 PASS 14/14, **round 2 PASS 22/22** |

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

`tombstone_xp_recovery` **7/7**, `uber_quest_markers` **8/8**, `general_guardians` **14/14** (round-1
number; **round 2 is 22/22** - see section 7, and note that this 14/14 is precisely the false green
the round-2 correction exists to explain).
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

### 5.7 A REAL GAP THIS PASS FOUND AND CLOSED: `Text.arc` was never rebuilt

§Header of this report states the arz+Text coupling ("this lane mints 3 new tags, so the arz and
Text must ship together"). **The coupling was stated but not executed.** Measured: the staged
`work/SoulvizierClassic/Resources/Text.arc` was dated *before* this lane's own DB build
(md5 `f51c62ffd2a0fcddfab00bad498c04dd`), so the three chest-name tags existed in the arz and in the
build's tag sink (`work/SoulvizierClassic/Database/uber_soul_tags.txt` lines 410-412) but **not in
any shipped Text.arc**. Deploying that pair would have shown the player three raw
`tagSVCChestGeneral*Guard` strings on the Guardians' chests - exactly the orphaned-tag defect class
`validate_tags` exists to prevent, arriving through the one door it does not watch (a *stale* Text
artifact rather than a missing tag).

Built:

```
py tools/build_text_arc.py upstream/soulvizier_098i/Resources/Text_EN.arc \
   work/SoulvizierClassic/Resources/Text.arc \
   work/SoulvizierClassic/Database/uber_soul_tags.txt \
   "<TQAE>/Text/Text_EN.arc"
EXIT=0    RESULT: PASS - 2 contracted tooltip(s) state the gate their records actually enforce
```

`Text.arc` md5 `f51c62ffd2a0fcddfab00bad498c04dd` (stale) -> **`67466b9bc1c83c000247deff98e46505`**
(89,331 B -> current), i18n de-clobber active against the base-game `Text_EN.arc`.

Proved present by a bare `ArcArchive` read of the built arc (no lane code in the loop):

```
PRESENT  tagSVCChestGeneralAGuard   in modstrings.txt  ->  Reaver's Spoil
PRESENT  tagSVCChestGeneralBGuard   in modstrings.txt  ->  The Bilespitter's Cache
PRESENT  tagSVCChestGeneralCGuard   in modstrings.txt  ->  Ember-Ward Reliquary
RESULT: PASS (3/3)
```

**DEPLOY COUPLING, now satisfiable:** ship `SoulvizierClassic.arz`
(`b55515970be41c2542208e84a8705640`) **together with** `Text.arc`
(`67466b9bc1c83c000247deff98e46505`). `Levels.arc` and `Quests.arc` are untouched by this lane
(`git diff --stat main...HEAD` over the map/quest tools is empty), so their coupling does not apply.

---

## 7. ROUND 2 (2026-08-05) - THE ONE NO-GO: FOUR SIGNATURE SKILLS COULD NOT FIRE

The round-1 independent vet returned NO-GO on exactly one thing, and it was right. R-100 #7 and
R-109 were reproduced and passed; nothing about them was touched here.

### 7.1 The defect, measured on ROUND 1's OWN artifact

`work/SoulvizierClassic/Database/SoulvizierClassic.arz` @ `b55515970be41c2542208e84a8705640`,
51,151 records. Every line below is a field read.

* All six Guardians bind
  `charAnimationTableName = records\xpack\creatures\monster\machae\anm\anm_machae.dbr`.
* That table declares **exactly four** `<row>SpecialAnimRef<N<=15>` clip names:
  `bow1='HeavyShot'`, `sHanded1='ThunderClap'`, `spear1='Slam'`, `spear2='Strike'`.
* Game.dll's `SkillManager::StartSkill` aborts a special SILENTLY when the caster's table has no clip
  for the skill's `skillSpecialAnimationName` - this repo's own crash-law RE, already applied once as
  the **b42 Ephialtes Dread Nova** fix in `tools/apply_svc_patches.py`.
* Therefore these **never fired**:

  | skill | clip it demanded | guard |
  |---|---|---|
  | `hero_vomitbile` | `Belch` | b1 Bhikru |
  | `empusavenomancer_venombolt` | `Belch` | b1 Bhikru (so BOTH of his two) |
  | `hero_flamewave` | `ShadowScythe` | c1 Kharzun |
  | `gigantes_shieldcharge` | `Charge` | c2 Voreth |
  | `shieldcharge` (INHERITED slot 1) | `ShieldCharge` | **all six**, on `skillName3` AND `specialAttackSkillName` |

* **20 dead cast slots. Bhikru the Bilespitter had ZERO castable specials of any kind** - Will's
  complaint was left literally true for one of the six.
* The three Machae generals are CLEAN on this invariant (no anim-carrying skill in any cast slot), so
  nothing about them changes.
* NEGATIVE CONTROL, so the measurement is not circular: the independent probe run against the
  PRE-LANE baseline (`local/baseline_main_7efd107.arz`, the guards exactly as `four_generals` built
  them) reports **156 cast slots inspected, 12 CANNOT FIRE, RESULT: FAIL** - it finds the 6 x 2
  inherited `shieldcharge` slots by itself. Log:
  `r108_logs/r108r2_castability_BASELINE_negative_control.log`.

### 7.2 The fix - the b42 recipe, five times, CLONE never edit

Each offender is CLONED into `records\skills\svc\` with `skillSpecialAnimationName` blanked, via the
monolith's own `_svc_clone_blank_anim` (which registers the pair in `_BOSS_KIT_CLONES`, so the
build's B-TOXEUS-2 clone-shape invariant gates them too). The guards are repointed at the clones; the
shipped records are never written. Blank-anim precedent counted per Class in this same build:
`Skill_AttackProjectileBurst` 102 shipped records already blank, `Skill_AttackProjectile` 156,
`Skill_AttackWave` 29, `Skill_AttackWeaponCharge` 5 (e.g. `coldtusk_charge`, `tykos_charge`).

**Why blank rather than repick a clip the rig HAS** (both options were on the table, per skill): the
four clips are per weapon ROW (`bow` / `sHanded` / `spear`) and the guards' weapon comes from a
100%-chance RightHand/LeftHand loot POOL, not a fixed weapon. A repick would be castable only for
some rolls. Blanking rides the default attack clip, which is row-independent.

### 7.3 PROVED ON THE BUILT ARZ - all twelve, plus the slot-1 special

Build: `PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1`, output
DELETED first, `work/` layout so the full gate battery is live. **EXIT 0**
(log `r108_logs/r108r2_build.log`).

| | arz | size | records | modules |
|---|---|---|---|---|
| round 1 | `b55515970be41c2542208e84a8705640` | 55,485,062 B | 51,151 | 47 |
| **round 2** | **`e77059427b53f009f55e56dbdca758c8`** | **55,491,436 B** | **51,156** | **47** |

Per-skill table generated FROM the artifact
(`tools/debug/r108r2_twelve_skill_table.py`, output `r108_logs/r108r2_twelve_skill_table.md`):
**12 of 12 CAN FIRE**, and all six slot-1 specials CAN FIRE. Bhikru went from 0 castable specials to
3. Independent probe over the same artifact (`tools/debug/r108r2_castability_probe.py`, a bare
`ArzDatabase` read with no lane code in the loop, cross-checking the 3 generals as well):
**180 cast slots inspected, 0 CANNOT FIRE, RESULT: PASS**.

The module's own in-build `verify()` line:

```
Guardians of the General read as uber (R-100 #18) verify OK: ... CASTABILITY: 78 cast slot(s)
across the six checked against their own anim table [heavyshot, slam, strike, thunderclap] -
0 name a clip the rig lacks; 5 blank-anim clones present, every shared donor byte-unedited.
```

SHARED-RECORD LAW, measured on the artifact rather than asserted - every donor still carries its
shipped clip name, every clone carries none, Class matches, and no donor lost a carrier:

```
donor hero_vomitbile.dbr             anim='Belch'        | clone ...vomitbile.dbr     anim=''  donor kept  4 non-guard carrier slots
donor empusavenomancer_venombolt.dbr anim='Belch'        | clone ...venombolt.dbr     anim=''  donor kept 39
donor hero_flamewave.dbr             anim='ShadowScythe' | clone ...flamewave.dbr     anim=''  donor kept  4
donor gigantes_shieldcharge.dbr      anim='Charge'       | clone ...embercharge.dbr   anim=''  donor kept  6
donor shieldcharge.dbr               anim='ShieldCharge' | clone ...shieldcharge.dbr  anim=''  donor kept 74
```

### 7.4 Record diff vs the baseline - zero unattributed

`py tools/debug/r108_visibility_record_diff.py local/baseline_main_7efd107.arz
work/SoulvizierClassic/Database/SoulvizierClassic.arz` -> **EXIT 0**
(`r108_logs/r108r2_record_diff.txt`):

```
records  : baseline 51124 -> built 51156
ADDED 32 / REMOVED 0 / CHANGED 11
RESULT: PASS - 0 REMOVED, 32 ADDED (27 declared guard-hoard records + 5 declared blank-anim
clones), 11 CHANGED and every one attributes to R-100 #7, R-100 #18 or R-109.
```

ZERO-DELTA claims re-checked: the other 25 roster members 0 moved, the 5 dead gameengine lookalikes
0 moved, the R-80 penalty fields 0 moved, and **the 5 clone DONORS 0 moved** - the shared-record law
proved by the diff itself, not only by `verify()`. NON-VACUITY: all six expected delta classes
present, so a build that silently stopped minting the clones is a NO-GO rather than a green.

### 7.5 The gate - the actual deliverable

`general_guardians.verify()` now asserts, for every guard and every `skillNameN` /
`specialAttack*SkillName` slot, that the named `skillSpecialAnimationName` is empty or present in
that creature's OWN resolved animation table. It runs in every build under `run_registry_verifies`.
Negative suite **14 -> 22, PASS 22/22** on both the baseline and the built arz:

* `'Belch'` planted on a clone - THE round-1 defect - **REJECT**
* a clip that exists nowhere in the db (`'NoSuchClip'`) - **REJECT**
* a guard repointed at the raw upstream donor (the round-1 wiring) - **REJECT**
* slot 1 left on the inherited dead `shieldcharge` - **REJECT**
* a shared donor edited in place instead of cloned - **REJECT**
* an unresolvable `charAnimationTableName` - **REJECT**
* MEMBERSHIP PAIR, same free slot on the same guard: a skill whose clip the rig HAS
  (`'ThunderClap'`) **ACCEPT**, one whose clip it LACKS (`'Belch'`) **REJECT** - so the rule is
  membership, not "the anim must be empty"

Standalone re-measurement: `py tools/patches/general_guardians.py --castability <arz>`.

**WHERE THIS GATE IS WEAKER THAN ITS SIBLING, stated rather than left to be found.**
`tools/patches/toxeus_hunt_encounter.py::_castability_violations` (b98 round 2) already ships a
per-weapon-ROW form for the three Toxeus champions: it derives which row the engine reads from the
Class of the item the caster is GUARANTEED in RightHand. This one uses the UNION form the R-100 #18
brief specifies, because the Guardians have no guaranteed weapon. It would therefore ACCEPT a future
repick to a clip only one row declares. It cannot bite the shipped state - the remedy here is
blanking, and `verify()` separately asserts all five clones carry no special anim - but a repo-wide
gate should use the b98 row-aware form. Registered as `BL-R108VIS-DEBT-7`, together with the fact
that between the two lanes exactly **9 monster records** (3 champions + 6 Guardians) are gated for
castability at all.

### 7.6 What round 2 did NOT do

* **No deploy, no Steam action, no TQ or Steam process launched or killed.** Nothing was written to
  any `CustomMaps\*` target.
* **No in-game test.** The animation half of "do the twelve skills fire" is now proved from the
  artifact; cast frequency, range/timeout feel, whether the FX read well and whether the pair fight
  is fun remain launch-gated (`BL-R108VIS-DEBT-2`, narrowed accordingly).
* **No repo-wide castability gate** (`BL-R108VIS-DEBT-7`, P1, with the fix shape written down).
* **R-100 #7 and R-109 were not touched.** In this build's diff they are still exactly one field
  each: `DisplayAsQuestItem 1 -> 0` on `um_bloodtoxeus_99`, `RedemptionMultiplier 0.5 -> 1.0` on
  `gameengine`.
* **Text.arc was NOT rebuilt** and did not need to be: round 2 mints no tag. The coupling partner
  recorded in section 6 (`67466b9bc1c83c000247deff98e46505`) still matches this arz's tag set;
  re-verify before shipping if anything else changes.
* **The guards still share a mesh within a pair** (`BL-R108VIS-DEBT-3`), still ship unmarked
  (`BL-R108VIS-DEBT-1`, a Will decision), and `amgoz1_design_voice.md` is still absent
  (`BL-R108VIS-DEBT-4`). Round 2 changed none of those.

### 7.7 Determinism: rebuilt at FINAL HEAD, byte-identical

The artifact section 7.3 measures was built at `628b281`. Everything committed after it in this
round is comment or documentation, so the arz must reproduce. Proved rather than argued - output
DELETED again, same command, same env, at the round-2 tip:

```
py tools/build_svc_database.py <4 inputs> work/SoulvizierClassic/Database/SoulvizierClassic.arz <base arz>
EXIT=0
e77059427b53f009f55e56dbdca758c8 *work/SoulvizierClassic/Database/SoulvizierClassic.arz   (build 2)
e77059427b53f009f55e56dbdca758c8 *local/r108r2_build1.arz                                 (build 1)
```

**Byte-identical.** Log `r108_logs/r108r2_build_confirm.log`. The one module edit made between the
two builds (`88581f2`, `7c8a71c`) is proved comment-only by stripped-AST equality
(`ast.dump(ast.parse(old)) == ast.dump(ast.parse(new))` -> `True`), so the identity is expected and
now measured.

⚠️ ONE HARNESS TRAP RECORDED, not swept: the FIRST attempt at this confirming rebuild exited **127**
with a zero-byte log - the backgrounded shell could not find `py` at all. It is an environment
flake, not a code failure (the very next run of `py --version` in the same worktree printed
`Python 3.12.10`), but a 127 with an empty log looks exactly like a build failure and would mislead
the next agent. Re-run verbatim: EXIT 0.
