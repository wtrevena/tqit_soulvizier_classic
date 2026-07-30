# b101 - R-99: the apex orb covers EVERY Toxeus variant (all-Toxeus roster + roster-derived gate)

Branch `feat/toxeus-apex-roster`. Ruling: **R-99** (`docs/WILL_RULINGS.md`), ratified by Will
2026-07-29, now IMPLEMENTED. Owner module `tools/patches/uber_apex_orb.py` (the R-72/R-75 owner, its
roster EXTENDED - not a new module).

**NOT DEPLOYED. Nothing was written to any `CustomMaps\*` target, no Steam action, no TQ or Steam
process was launched or killed.** The orchestrator owns every deploy and every upload.

---

## 1. What Will asked for, and what was actually wrong

R-99, verbatim: *"i didnt tell you to increase the drop of all the champions, just the toxeus variants
(all variants we made and didnt make) and leinth"*, and on the two judgement calls the first pass
raised: *"give all versions of toxeus the new apex orb, if some good items drop since someone got lucky
and found and killed the low-level Toxeus with no fixed spawn and they get some great items, so be
it"*.

The real gap: b94 wired the two FOUGHT champions onto the new apex tier `genericbossorb_05` from a
**hand-typed pair**, while b98 built the Endless Hunt in a parallel lane. Neither lane owned the
other's half of the roster, so **the third champion - the one Will has actually fought in play -
shipped with no `treasureProxyName` at all**, for two waves, and nobody noticed.

That is the defect this wave closes, and it is why the roster is now DERIVED from the database instead
of typed.

## 2. The change

`uber_apex_orb.toxeus_roster(db)` = every record whose path contains `toxeus` **and** whose
`templateName` is `Monster.tpl`. Both halves are load-bearing: the path token is what finds a variant a
future lane adds without telling this module; the `Monster.tpl` half is what keeps the nine `Pet.tpl`
Toxeus summon pets out, because `treasureProxyName` is a Monster.tpl loot field and writing one onto
`Pet.tpl` is the documented crash trap in `CLAUDE.md`.

The derived roster is cross-checked **two independent ways** so the predicate cannot rot:

1. **Pinned allow-list.** `ROSTER_PINNED` names all 8. The derived set is asserted EQUAL to it, so a
   new `um_toxeus_*` variant **reds the build** with a message telling the next lane to ratify it,
   rather than being silently dropped. That silence is the exact failure R-99 exists to close.
2. **Name-tag derivation.** The roster is re-derived from display tags, on ANY template except
   `Pet.tpl`, and the two derivations are diffed. Two base-game `am_assassin` records legitimately
   reuse `tagMonsterName190` and are pinned as known false positives; a THIRD tag-only hit reds.

`apply()` repoints exactly the derived roster. Five records had no `treasureProxyName` field at all, so
the write ADDS it (`DATA_TYPE_STRING`); the ones that already carried a string get a value-only write
(the cloned-record dtype trap). `um_toxeus_hunt_l_99` does not exist when this module runs - it is
authored later by `toxeus_hunt_endless` as a clone of the final Hunt - so `apply()` tolerates its
absence via `ROSTER_DEFERRED` while `verify()`, which runs over the FINAL merged db, requires it
present and on orb05.

Nothing about the orb's CALIBRE changed. R-99 is about who sits on the tier; "more items than the
normal champions" was already satisfied by orb05 (21.16 modelled expected items vs orb04's 5.70).

## 3. THE ROSTER TABLE, read back OUT of the built arz

Built arz `6a3a491db546b603c52132237c40aa63`, 55,475,226 B, 51,124 records.

| record | charLevel n/e/l | rank | `treasureProxyName` before | after |
|---|---|---|---|---|
| `um_toxeus_enslaver_99` (Enslaver of Souls) | 40/68/100 | Boss | `genericbossorb_05` | `genericbossorb_05` |
| `um_bloodtoxeus_99` (Devourer of Blood) | 40/68/100 | Boss | `genericbossorb_05` | `genericbossorb_05` |
| `um_toxeus_hunt_99` (**the Endless Hunt**) | 40/68/100 | Boss | **field absent** | `genericbossorb_05` |
| `um_toxeus_hunt_l_99` (endless variant) | 40/68/100 | Boss | **field absent** | `genericbossorb_05` |
| `um_toxeus_99` (SP Toxeus, inherited) | 33/66/99 | Hero | **field absent** | `genericbossorb_05` |
| `um_toxeus_21` (Athens, inherited) | 25/45/65 | Boss | `genericbossorb_01` | `genericbossorb_05` |
| `z_toxeus` (zzdev dummy) | 40/56/71 | Champion | **field absent** | `genericbossorb_05` |
| `old_z_toxeus` (zzdev dummy) | 40/56/71 | Champion | **field absent** | `genericbossorb_05` |

Every charLevel matches R-99's own table, re-measured rather than copied. `charLevel` is ONE field
holding a 3-element array - reading only `[0]` reports a 40/68/100 boss as "40/-/-", which is how a
proof table starts lying; the tool reads the whole array.

`um_toxeus_21` was **not** quietly scaled down to a lesser tier. R-99 bans that explicitly and the ban
is honoured literally.

**The nearest adjacent record, and why it is NOT on this table** (asked for by the vet, because it is
the one exclusion a reader would most plausibly challenge). `um_enslaver_marauder_99` lives in the same
`records\creature\monster\shadowstalker\` folder as three roster champions, is a `Monster.tpl` record,
and carries no `treasureProxyName`. Excluding it is correct: its tag
`tagSVCMonsterEnslaverMarauder` resolves in `tools/apply_svc_patches.py:11373` to
`'{^r}Enslaved Shadow Marauder'`, and its own constant at `apply_svc_patches.py:11001` is commented
`# hostile Champion` - it is the Enslaver's **summoned minion**, a Champion-rank add, not a Toxeus
variant and not an uber encounter. It has no `toxeus` path token and wears none of the four roster
display tags, so both derivations independently agree it is out. Measured folder-by-folder across every
folder containing a roster record; nothing else in any of them is Toxeus-adjacent (the only other
`genericbossorb_*` carriers in those folders are `um_gorrahk_99` and `um_ilsevar_99` on orb04 and
`um_xaiweng_48` on orb03, all non-Toxeus and all untouched). Also documented in the module's
"WHAT IS DELIBERATELY NOT IN THE ROSTER" block, which previously covered only the `Pet.tpl` exclusion.

## 4. The gate: NEGATIVE 2 restated, not weakened

`verify()` used to hardcode exactly TWO champions, and planted `NEGATIVE 2` asserted that a **THIRD**
record on orb05 must FAIL as scope creep. That test encoded a COUNT of two champions, which is the
wrong invariant under R-99 - it would have redded the build the moment the ruling landed.

The invariant it protected is still real and is now stated as a **set equality, tested both ways**:

* every derived-roster record carries `treasureProxyName = genericbossorb_05`; **and**
* the set of orb05 carriers is EXACTLY that roster - nothing non-Toxeus may sit on the apex tier.

That second half is what keeps R-99's opening reassurance ("we did NOT raise all the champions") true,
and `NEGATIVE 2` still plants a non-Toxeus record on orb05 and still requires FAIL.

`verify()` also proves: the orb05 chain resolves end to end on all 3 difficulties; orb05's four calibre
knobs are >= Leinth's original chest's on every difficulty; **every** donor tier a roster record left
(orb04 AND orb01) survives, carries no Toxeus record and still serves its measured consumer floor; the
three fought champions keep their R-48/R-91 100% soul; all three of Leinth's chests are on the same
apex tables and level equation with her bespoke identity intact; and the six-loot-group no-nerf proof
is recomputed rather than asserted.

## 5. Proofs (commands + measured outputs, nothing estimated)

Environment for every build: `PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1
SVC_REQUIRE_GATES=1`, `py` launcher.

### 5.1 Full build, gates required

```
py tools/build_svc_database.py upstream/soulvizier_098i/Database/database.arz \
   upstream/soulvizier_0.9/Database/database.arz upstream/soulvizier_041/Database/database.arz \
   work/SoulvizierClassic/Database/SoulvizierClassic.arz \
   "C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"
```

**exit 0.** arz **`6a3a491db546b603c52132237c40aa63`**, 55,475,226 B, **51,124 records**, 45 registry
modules. Log `docs/reports/b101_logs/b101_r99_reproduce.log`. Key lines:

```
--- [37/45] uber_apex_orb  (uber apex orb - ONE apex drop calibre for the WHOLE Toxeus roster AND Leinth (R-72 + R-99)) ---
  R-99 roster DERIVED from the db (path contains 'toxeus' AND templateName is Monster.tpl): 7 record(s), == ROSTER_PINNED minus the 1 deferred clone(s)
  donor tier to protect: genericbossorb_01.dbr - 11 consumer(s), 10 of them NOT Toxeus and staying put
  donor tier to protect: genericbossorb_04.dbr - 21 consumer(s), 19 of them NOT Toxeus and staying put
  blast radius genericbossorb_01.dbr: 11 -> 10 consumer(s) (1 Toxeus left, 10 non-Toxeus untouched)
  blast radius genericbossorb_04.dbr: 21 -> 19 consumer(s) (2 Toxeus left, 19 non-Toxeus untouched)
    uber_apex_orb: modified 20 record(s), 0 tag(s)
  [uber_apex_orb] verify OK: the DERIVED Toxeus roster is 8 record(s) ... EVERY one is on
  genericbossorb_05, with the orb05 carrier set EXACTLY equal to it (no scope creep) ...
```

(The apply-time roster is 7 and the verify-time roster is 8 by design - the Legendary endless variant
is cloned into existence later in the registry and inherits the orb.)

### 5.2 The baseline, built from `main` in the same environment

Built TWICE, from two different `main` commits, with the identical command and env - and both give the
same bytes:

| baseline build | `main` commit | result |
|---|---|---|
| round 1 | `e014ef8` (the briefed base) | **exit 0**, `aea688b23acefe1b48ae31a0df4cc423`, 55,475,172 B, 51,124 records, 45 modules |
| round 2 | `b376b61` (the NEWEST tip, 3 advances later) | **exit 0**, `aea688b23acefe1b48ae31a0df4cc423`, 55,475,172 B, 51,124 records |

```
git worktree add --detach .claude/worktrees/r2-baseline b376b61
# Resources/ hardlinked in so the A9 render-chain gate can actually RUN
PYTHONIOENCODING=utf-8 PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 SVC_REQUIRE_GATES=1 \
  py tools/build_svc_database.py …   ->  EXIT=0
md5sum work/SoulvizierClassic/Database/SoulvizierClassic.arz
   ->  aea688b23acefe1b48ae31a0df4cc423
```

That second build is the stronger claim: it turns "main's advances are docs-only, so they cannot change
the arz" from a file-list argument into an **empirical result**. The round-2 baseline is also **fully
gated to exit 0** (the A9 render-chain gate needs a `Resources/` directory beside the output, so the
hardlink step above is what lets it run rather than skip). This md5 additionally **reproduces the value
the B100 gate record published**, corroborating that build's determinism and this environment.

The baseline log also prints the pre-R-99 donor-tier state verbatim, which is what the module's
`DONOR_TIER_FLOORS` comment now cites: `scope proof: orb04 chain byte-unchanged; consumers 21 -> 19 (the
2 champions moved to orb05)`.

> ⚠️ **ROUND 1's TWO "BASELINE" ARTIFACTS WERE STALE AND ARE NOW GONE FROM THE BRANCH.**
> `local_baseline_build.log` (arz `967b1f97137bf6479c18c08e9dd6ffc4`) and `local_r99_build.log` (arz
> `f99d5c83a60cb3136eff62622b999550`) were both **44-module builds made BEFORE the merge of `main` @
> `e014ef8` at 12:57** - provable from the log itself, which reads `--- [37/44] uber_apex_orb` and never
> reaches `weapon_gate_truth`, versus `[37/45]` and `[44/45] weapon_gate_truth` in the real one. So
> neither was a baseline of the tip, and `f99d5c83…` must never be shipped. Round 2 dropped them (and
> two redundant intermediate rebuild logs) from the branch rather than keeping four stale logs at the
> repo root under authoritative-looking names, and renamed the two matching stale `local/*.arz` on disk
> to `local/STALE_DO_NOT_SHIP_*`. The one surviving log is
> `docs/reports/b101_logs/b101_r99_reproduce.log`, the 45-module log of the shipped bytes.
> **`967b1f97…` is NOT the measurement basis for anything in this lane;** round 2 re-cited the tip
> baseline in `tools/patches/uber_apex_orb.py` and `tools/debug/b101_r99_record_diff.py`.

### 5.3 Record-diff: zero unattributed changes

```
py tools/debug/b101_r99_record_diff.py <baseline aea688b2....arz> work/SoulvizierClassic/Database/SoulvizierClassic.arz
```

**exit 0:**

```
  records  : baseline 51124 -> built 51124
  ADDED 0 / REMOVED 0 / CHANGED 6
--- ATTRIBUTED TO R-99 (roster treasureProxyName) : 6 record(s) ---
  um_toxeus_hunt_99.dbr    FIELD ABSENT          -> genericbossorb_05.dbr
  um_toxeus_hunt_l_99.dbr  FIELD ABSENT          -> genericbossorb_05.dbr
  um_toxeus_21.dbr         genericbossorb_01.dbr -> genericbossorb_05.dbr
  um_toxeus_99.dbr         FIELD ABSENT          -> genericbossorb_05.dbr
  old_z_toxeus.dbr         FIELD ABSENT          -> genericbossorb_05.dbr
  z_toxeus.dbr             FIELD ABSENT          -> genericbossorb_05.dbr
--- ROSTER RECORDS WITH ZERO DELTA (already on orb05 before R-99) : 2 ---
RESULT: PASS - 0 ADDED, 0 REMOVED, 6 CHANGED and every one of them is a DERIVED Toxeus roster
record whose ONLY moved field is treasureProxyName -> genericbossorb_05. Zero unattributed changes.
```

**0 REMOVED** is the load-bearing half for the neighbouring lanes. Round 2 also enumerated them BY NAME
rather than leaving it to the aggregate (set-difference over all 51,124 record names, baseline vs built):

```
REMOVED (in baseline, gone from built): 0
ADDED   (in built, absent from baseline): 0
b98 Endless Hunt (token 'toxeus_hunt') : 9 records in built, all present in baseline too: True
   controller_toxeus_hunt_endless, um_toxeus_hunt_99, um_toxeus_hunt_l_99,
   q_toxeus_hunt_lone (proxy + 2 pools), toxeus_hunt_soul_{n,e,l}
b99 Sargoth      (token 'sargoth')     : 8 records in built, all present in baseline too: True
   summon_sargoth, sargoth_{1,2,3} pets, sargoth_soul_{n,e,l} (+1 upstream conflicted copy)
b94 Leinth       (token 'leinth')      : 79 records in built, all present in baseline too: True
   including all 3 of her original loot tables (loottable_leinth_29-31 / 49-51 / 63-65),
   which R-72 requires be PRESERVED rather than replaced
```

The attribution rule is strict in both directions - any added record, any removed record, any other
changed field, or a roster record landing on anything other than orb05, exits 1.

### 5.4 `genericbossorb_04` BYTE-UNCHANGED, and its 19 other consumers

```
py tools/debug/b101_r99_proof_table.py <built.arz> <baseline.arz>
```

```
[2] DONOR TIER genericbossorb_04 (R-47 shared generic apex orb)
    chain records compared field-by-field vs baseline: 10
    BYTE-UNCHANGED: all 10 record(s) identical to the baseline (every field, every value, every dtype)
    consumers: baseline 19 -> built 19 ; Toxeus record(s) still on it: 0
    lost  : none
    gained: none
```

All 19 named and still on it: `um_sarkoth_99`, `um_vashkarr_99`, `um_bloodcrow_50`, `um_voranthys_99`,
`um_broodmother_99`, `um_gorrahk_99`, `um_ilsevar_99`, `boss_dagon_66`, `um_ephialtes_99`,
`um_mnemophage_core_99`, `um_antaeus_49`, `um_polisgaoler_unbound_99`, `um_deeptresher_47`,
`um_meglograi_48`, `bloodcrow_soul`, `um_dorus_99`, `um_tantalus_unbound_99`,
`svc_um_hadesmarshal_80`, `um_helepolis_99`. The 10 records compared are the proxy plus its 3 pools,
3 chests and 3 loot tables - the whole donor chain a clone could have written back into.

The **second** donor tier is protected identically, which R-99 newly requires because `um_toxeus_21`
leaves it:

```
[3] DONOR TIER genericbossorb_01 (um_toxeus_21's old tier)
    BYTE-UNCHANGED: all 1 record(s) identical to the baseline
    consumers: baseline 11 -> built 10 ; Toxeus record(s) still on it: 0
    lost  : ['um_toxeus_21.dbr']    gained: none
```

Its other 10 (`um_elephantsnatcher_17`, `us_mormo_16`, `um_kaublasia_19`, `um_calybe_20` x2,
`um_rakanizeus_17` x2, `um_melalos_19` x3) stay exactly where they were.

### 5.5 R-48 / R-91 independence, proven not asserted

`chanceToEquipFinger2` on all 8 roster records is bit-identical to the baseline:

| record | built | baseline | soul |
|---|---|---|---|
| `um_toxeus_enslaver_99` | 100.0 | 100.0 | `enslaver_soul_n` |
| `um_toxeus_hunt_99` | 100.0 | 100.0 | `toxeus_hunt_soul_n` |
| `um_toxeus_hunt_l_99` | 100.0 | 100.0 | `toxeus_hunt_soul_n` |
| `um_bloodtoxeus_99` | 100.0 | 100.0 | `blood_toxeus_soul_n` |
| `um_toxeus_99` | 66.0 | 66.0 | `sp_toxeus_soul_n` |
| `um_toxeus_21` | 50.0 | 50.0 | `toxeus_soul_n` |
| `z_toxeus` / `old_z_toxeus` | 0.0 | 0.0 | `finger_n01b` |

Souls are Finger2 EQUIPMENT and orbs are `treasureProxyName` - independent mechanisms. `apply()` also
snapshots the three soul fields on every roster record before its own writes and fails loud on any
movement, so the guard covers rates it does not know the value of.

> ⚠️ **TWO OF THESE NUMBERS ARE ABOUT TO MOVE, and that is fine.** `main` landed **R-105** while this
> lane ran: soul rates of 66% and 50% both go to 33% across 734 creatures, which covers
> `um_toxeus_99` (66.0) and `um_toxeus_21` (50.0) above. **The gate needs no change** - the R-48/R-91
> guard is a before/after DIFF inside one build so it tolerates any rate, and `verify()` asserts the
> literal 100.0 only on the three FOUGHT champions, which is exactly R-105's carve-out. What goes stale
> is this table: it is a point-in-time measurement of the pre-R-105 db. Whoever implements R-105 should
> re-run the proof table and update it in the same commit (`BL-b101-DEBT-7`).

### 5.6 Planted negatives: 29/29

```
py tools/debug/negtest_uber_apex_orb.py work/SoulvizierClassic/Database/SoulvizierClassic.arz
```

**`29/29 subtests behaved as specified`, exit 0, 0 skipped.** 1 positive on the real arz; negatives
1-14 (champion back on orb04, non-Toxeus on orb05, the four calibre knobs, a broken chain link, R-48
collateral damage, donor-chain tamper, and the six Leinth guards); **negatives 15-22, one per derived
roster record, each losing its orb** - generated from the roster so a future variant gets its own
negative automatically; R1/R2 (roster-pin drift in both directions); R3 (the second derivation fires);
R4 (the false-positive pin proven load-bearing); R5 (orb01 stripped below its floor); and a final
positive proving every mutation was restored.

### 5.7 The gate reds the pre-R-99 baseline

Running the new `verify()` against the pre-R-99 arz fires with **exactly the 6 gaps R-99 enumerated**
(hunt, hunt_l, `um_toxeus_99`, `um_toxeus_21`, `z_toxeus`, `old_z_toxeus`) plus
`genericbossorb_01.dbr STILL carries Toxeus record(s) ['um_toxeus_21.dbr']`. A gate that cannot fail on
the state it was written to detect is not a gate.

### 5.8 Byte-identity: FOUR identical builds

The arz was built from scratch four times with the identical command and env, and every one returned
**exit 0** with md5 **`6a3a491db546b603c52132237c40aa63`**, 55,475,226 B:

| build | after what | log |
|---|---|---|
| 1 | the round-1 code, rebuilt from scratch by this round rather than trusted | `docs/reports/b101_logs/b101_r99_reproduce.log` (kept) |
| 2 | the verify-side fixes of steps 6/7/10 (proving the gate hardening moved no shipped byte) | dropped in round 2 as a redundant intermediate |
| 3 | merging `main` @ `31f3432` (proving the mid-lane base move moved no shipped byte) | dropped in round 2 as a redundant intermediate |
| 4 | **round 2's confirming rebuild** after the vet's doc/comment corrections, incl. merging `main` @ `b376b61` | `docs/reports/b101_logs/b101_r2_confirm_rebuild.log` |

Build 4 exists because round 2 edited comments inside `tools/patches/uber_apex_orb.py` (rescoping the
name-tag claim, citing the `dropItems` evidence, documenting the marauder exclusion, re-citing the
baseline md5). Per this repo's own discipline a comment edit inside a build module gets one confirming
rebuild rather than an assurance that comments cannot matter.

### 5.9 The base moved mid-lane; merged and re-proved

Briefed base was `main` @ `e014ef8`. `main` then advanced **three times** while the lane ran:
`31f3432` (R-102/R-103 Enslaver green-glow), `1897557` (R-103 amendment / R-104 / R-105) and, during
round 2, `b376b61` (R-106 / R-106 amendment / R-107). Each advance was merged and re-proved.

Every advance is **docs plus `tools/debug/probe_*.py` and nothing else**, measured over the whole span:

```
git diff e014ef8..b376b61 --name-only | grep -vE '^docs/|^tools/debug/'   ->  (empty)
grep -rnE "^\s*(from|import)\s+.*debug" tools/*.py tools/patches/*.py tools/contracts/*.py
   ->  only tools/patches/emberteeth_summon.py:238, which imports apply_svc_patches
       and merely says "debugging" in its comment - no build-tree module imports
       anything from tools/debug/
```

So `main`'s advances cannot change the arz, the baseline `aea688b23acefe1b48ae31a0df4cc423` remains the
correct comparison point, and the post-merge rebuilds confirm it with the same md5 every time.

Every merge of that file was resolved by keeping BOTH sides and then VERIFIED instead of trusted. After
the final merge of `main` @ `b376b61` (a clean auto-merge, no conflict at all): with line endings
normalised, the only two lines of `main`'s ledger absent from the result are the R-99 `PENDING` heading
and the `**STATUS:** RATIFIED` line - both deliberately superseded by the IMPLEMENTED block - with 107
lines added, 0 conflict markers, R-100's verbatim batch present and `main`'s newest R-106/R-107 present.
Confirming a merge of that file by diffing it against `main` afterwards should be standard practice on
this repo.

> 🛑 **RETRACTION.** Round 1 of this report asserted here that "the merge conflict was the same trap
> that already destroyed 101 lines on this branch". **That is false and is withdrawn** - see section 7.
> No lines were ever destroyed on this branch.

> A note on why the CRLF detail matters: the first attempt to verify the resolution compared
> `git show main:docs/WILL_RULINGS.md` (LF, as stored) against the working file (CRLF) and reported all
> 1,867 lines as missing. That is a false alarm from the comparison method, not a real loss, and it is
> recorded because a lane that panicked at it might "fix" the file and cause the very loss it feared.

## 6. THE ZZDEV PAIR - the finding R-99 demanded, and it is not the expected one

R-99: *"First VERIFY whether either is actually placed anywhere; if they are unreachable dev leftovers
the wiring is inert, which is a fine outcome - but record the placement finding either way."*

Measured with `tools/debug/b101_toxeus_placement_census.py` against the shipped `Levels.arc`
`fc0adcc0713839a685b32d6e122653be`: **2,282 levels walked, 0 unparsed `0x05` sections, 17,348 distinct
placed paths, 491,885 instances indexed** (the index was validated before any conclusion was drawn from
it - a census that silently indexes nothing would report everything as inert).

> ⚠️ **THE FIRST ANSWER WAS WRONG, AND THE CORRECTION MATTERS.** The first census walked ONE hop and
> concluded `z_arthur` had 0 placements and the chain was unreachable. Placement in this map is a
> **two-hop** chain - a placed `0x05` **proxy** draws a **pool**, and the pool names the monster - so a
> one-hop check reported "the SPAWNER is placed in 0 level(s)" for *every champion*, which reads as
> unreachable and is false. The census now walks breadth-first UP the reference graph to 3 hops and
> prints the whole chain top-down.

| record | verdict |
|---|---|
| `um_toxeus_enslaver_99` | REACHABLE at hop 2 - placed `ug_undead_skeleton_02n` x23 `.pool1` -> `undead_02_skeletonbat03` `.name1` |
| `um_toxeus_hunt_99` | REACHABLE at hop 2 - placed `demon_melinoe_01n` x19 `.pool1` -> `melinoe_01_general02` `.name3` |
| `um_toxeus_hunt_l_99` | REACHABLE at hop 2 - placed `q_toxeus_hunt_lone` x1 (`HadesPalace_Floor04_04.lvl`) `.poolLegendary1` -> `q_toxeus_hunt_lone_endless` `.name1` |
| `um_toxeus_21` | REACHABLE at hop 2 - placed `ug_undead_ghostskeleton_03t` x5 `.poolEpic4` -> `el_skeleton_03_ranged05` `.nameChampion7` |
| `um_bloodtoxeus_99` | REACHABLE at hop 2 - placed `egg_blooddragon_pack` x1 (`xBloodCave/drxBC2.lvl`) `.pool1` -> `egg_blooddragon` `.name1` |
| `um_toxeus_99` | **INERT** - 0 static, 0 db referrers, no placed ancestor within 3 hops |
| `old_z_toxeus` | **INERT** - 0 static, 0 db referrers, no placed ancestor within 3 hops |
| `z_toxeus` | **REACHABLE at hop 1** - placed `z_arthur` x1 `.actorToSpawnOnDeath` |

**`z_arthur` IS statically placed**: exactly ONE `0x05` instance in
`XPack\Levels\Area01_Rhodes\Undergrounds\ScrabledEggs_Floor06.lvl`. It is a `Monster.tpl`,
`monsterClassification = Quest`, charLevel 40/56/71 record (`FileDescription = "Satyr"`) whose
`actorToSpawnOnDeath` is `z_toxeus`.

So the honest summary is **"one of the two is inert, the other is live-but-obscure"**, not "both
inert": killing that one placed `z_arthur` spawns a Champion-rank Act-1 dev dummy that now drops the
Act-4 apex orb. **Will's words pre-authorise exactly this** ("if some good items drop since someone got
lucky ... so be it") and he explicitly included them, so it is RECORDED, not reversed - but it is a live
consequence rather than a no-op and he should know.

**Honest limit:** static placement proves the record is IN the level. It does not prove a player can
walk to that spot, or that the engine spawns it there. Player reachability is launch-gated and is
registered as debt, not claimed.

Both carry `dropItems = 0`, so neither drops equipped gear. The orb is the separate
`treasureProxyName` mechanism, and the vet correctly flagged that round 1 merely ASSERTED it would
still fire. The evidence exists in the shipped db and is now cited instead. Scanning all 51,124
records, **exactly FIVE `Monster.tpl` records combine `dropItems == 0` with a `treasureProxyName`**
(63 carry a proxy in total):

| record | dropItems | treasureProxyName |
|---|---|---|
| `records\drxcreatures\bloodwitch\q_leinth_47.dbr` | 0 | `bosschestproxy_leinth.dbr` |
| `records\drxcreatures\bloodwitch\q_leinth_49.dbr` | 0 | `bosschestproxy_leinth.dbr` |
| `records\drxcreatures\bloodwitch\q_leinth_50.dbr` | 0 | `bosschestproxy_leinth.dbr` |
| `records\xpack\creatures\monster\zzdev\old_z_toxeus.dbr` | 0 | `genericbossorb_05.dbr` |
| `records\xpack\creatures\monster\zzdev\z_toxeus.dbr` | 0 | `genericbossorb_05.dbr` |

Three of the five are Leinth, whose bespoke chest is a **shipped, gate-proven, player-facing drop**
that this very module protects with fourteen planted negatives. So a `dropItems = 0` record
demonstrably still gets its treasure proxy honoured in this mod's own live content - the two
mechanisms are independent by precedent, not by assumption. **Honest limit:** that is DB-side
corroboration, NOT an in-game observation; nothing in this lane was launched, and whether the orb
visibly drops on kill stays launch-gated (`BL-b101-DEBT-3`/`-5`). This matters for severity: if
`dropItems = 0` also suppressed the proxy, `z_toxeus`'s apex orb would be inert and `BL-b101-DEBT-2`
would be moot.

**Neither is deleted, retired, blanked or renamed** - RETIREMENT PROTOCOL, and this is a
Will-ratified inclusion, not a cleanup.

## 7. Defects in this lane's own work - ONE real (fixed), ONE misdiagnosed (retracted)

1. **The name-tag cross-check was hollow.** Running the harness (rather than trusting it) returned
   **28/29** with `negative R3 ... gate=PASS (expected FAIL)`. Root cause was a real gate hole: the
   second derivation filtered on `Monster.tpl`, but R3's donor `boss_titan_typhon_42` is
   `Typhon2.tpl` - so a boss on a **bespoke template** could wear a Toxeus champion's display tag,
   sit outside the `toxeus` path namespace, and both derivations would miss it. Every uber boss this
   mod mints could be authored that way. Fixed by widening the scan to every template except
   `Pet.tpl`, after MEASURING that the widening adds zero hits in the live db (the only carriers of
   the four roster tags are the 8 roster records plus the 2 pinned `am_assassin` false positives).
   `Pet.tpl` stays excluded with the reason written down: the nine Toxeus summons are out of roster
   scope by design and carry their own measured `*Pet` tags, so naming a summon after its master must
   not red the build. Harness now 29/29.

   ⚠️ **AND THE EXACT RESIDUAL BOUND, which round 1 overstated** (vet finding, reproduced in round 2).
   Round 1 wrote that this derivation "would catch a Toxeus authored OUTSIDE the `toxeus` path
   namespace". It only catches one that **also reuses one of the four roster display tags**, because
   the tag set is built FROM the path-derived roster. Measured against the built arz by planting both
   distinguishable cases (a clone outside the namespace, on `genericbossorb_04`, i.e. a Toxeus NOT on
   the apex orb):

   | planted record | `description` | gate |
   |---|---|---|
   | `…questbosses\um_murderer_r2bound_99.dbr` | `tagMonsterHemorrheus` (a roster tag) | **FAIL** - caught |
   | `…questbosses\um_murderer_r2bound_99.dbr` | `tagSVCMonsterToxeusR2Bound` (brand new) | **PASS** - blind |

   Cleanup was asserted between the two cases (the record removed from `_raw_records` and the gate
   re-run to `PASS`, with the orb04 consumer count seen moving `19 -> 20 -> 19`), so neither result is
   an artifact of the other. **The blind spot is empty today**, checked three independent ways over all
   51,124 records: 0 records outside the namespace carry a `*toxeus*` `controller`, 0 wear a `*toxeus*`
   soul in any `lootFinger2Item*` slot, and 0 point at `genericbossorb_05`. So this is a bound on the
   GATE, not a defect in the shipped bytes. Rescoped at both claim sites in
   `tools/patches/uber_apex_orb.py` and registered as `BL-b101-DEBT-8`.
2. 🛑 **WITHDRAWN - THIS "DEFECT" WAS A MISDIAGNOSIS, AND IT WAS THE VET'S ONE BLOCKING FINDING.**
   Round 1 claimed here that "this branch's merge `4748e93` silently deleted 101 lines of
   `docs/WILL_RULINGS.md` - the whole R-100 PLAY-SESSION BATCH, Will's verbatim 19-item play report",
   and wrote that accusation into the design law of record. **It never happened.** The independent vet
   caught it; round 2 reproduced every disproving command rather than taking the correction on trust:

   | command | output | what it proves |
   |---|---|---|
   | `git diff e014ef8 4748e93 --numstat -- docs/WILL_RULINGS.md` | *(empty)* | the merge result is byte-identical to the `main` it merged - it lost nothing |
   | `for c in d7c9aee e014ef8 4748e93 60a3bfb~1 60a3bfb 0c4e9a2; do git show $c:docs/WILL_RULINGS.md \| grep -c "PLAY-SESSION BATCH"; done` | `0 0 0 0 1 1` | the text did not exist on EITHER side of that merge |
   | `git log -1 --format="%h %ad %s" --date=iso 0c4e9a2` | `2026-07-29 18:18:15  R-100: capture Will's 19-item play-session batch VERBATIM` | the ruling was authored on `main`… |
   | `git log -1 --format="%h %ad %s" --date=iso 4748e93` | `2026-07-29 12:57:15  Merge branch 'main' …` | …**5h21m AFTER** the merge it was accused of destroying |
   | `git merge-base --is-ancestor 0c4e9a2 e014ef8` | exit `1` | R-100 was not reachable from the merged base |
   | `git diff 60a3bfb~1 60a3bfb --numstat` | `101 0 docs/WILL_RULINGS.md` | commit `60a3bfb` was an ADD of main's newer text, not a restore - its own subject line is wrong too |

   **ROOT CAUSE OF THE FALSE REPORT:** two-dot `git diff main..HEAD --numstat` renders a file that
   `main` added *after* the merge base as pure deletions on the branch side. Reproduced live in round 2:
   `git diff main..HEAD --numstat` reported `0 96 tools/debug/probe_blockers.py`, `0 86
   …probe_class_examples.py`, `0 101 …probe_soul_by_class.py` - three files `main` ADDED at `fc7a886`
   that this branch has never touched. **The real, transferable lesson: use three-dot `main...HEAD`,
   and check the accused commit's own `--numstat` against BOTH parents, before accusing any commit of
   losing anything.** Corrected in all four places it had been written (`docs/WILL_RULINGS.md` R-100
   annotation, `docs/BACKLOG.md` head note and gate record, and this report in two places) and
   registered as `BL-b101-DEBT-9`. A fabricated incident in the design law of record is itself a
   violation of CLAUDE.md law #1, which is why the vet made it blocking.

## 8. Wave-label and ruling-number collisions (flagged, not resolved)

* **`b100` was already taken** on `main` by `fix/blade-mastery-truth` (the WEAPON/HAND GATE HONESTY
  gate record) and, in parallel, by `feat/sanctuary-populate`'s recon doc. This lane is therefore
  **b101**, and round 1's `b100_toxeus_placement_census.py` plus its `b100_toxeus_apex_roster.md`
  docstring reference were renamed to `b101` rather than shipping a cross-reference to a filename
  another wave owns.
* **There are TWO live R-100s** in `docs/WILL_RULINGS.md`: blade-mastery's
  `R-100 ... IMPLEMENTED b100` and the play-session batch. Both same-day, both parallel lanes. This
  lane deliberately did NOT renumber either - reassigning another lane's ruling number from a third
  lane is the same class of silent cross-lane edit the ledger law exists to prevent. The file's own
  `fix/debt-docs` precedent (incumbent keeps the number) is the tie-breaker to apply; picking the
  incumbent between two same-day lanes is the orchestrator's call. `BL-b101-DEBT-1`.

## 9. Files

| file | what |
|---|---|
| `tools/patches/uber_apex_orb.py` | roster DERIVED + pinned + double-cross-checked; `verify()` re-authored as a set equality in both directions; blast-radius proof derived over every donor tier; docstring rewritten (it described a two-champion design) and its zzdev claim corrected |
| `tools/debug/negtest_uber_apex_orb.py` | NEGATIVE 2 restated as a set equality; negatives 15-22 one per roster record; R1-R5; skipped subtests printed and warned about |
| `tools/debug/b101_toxeus_placement_census.py` | the R-99 placement census; multi-hop reachability |
| `tools/debug/b101_r99_record_diff.py` | baseline-vs-built diff with strict roster attribution |
| `tools/debug/b101_r99_proof_table.py` | reads the roster table, donor tiers, soul wiring and orb05 chain back OUT of the built arz |
| `docs/WILL_RULINGS.md` | R-99 -> IMPLEMENTED with the measured result, plus a ROUND 2 block; R-100 collision flag; the RETRACTION of round 1's false merge-loss claim |
| `docs/BACKLOG.md` | BUILD69-DEV gate record + `BL-b101-DEBT-1..9` (round 2 adds `-8` derivation bound and `-9` the diff-reading process rule, and reorders `-6`/`-7`) |
| `docs/reports/b101_logs/b101_r99_reproduce.log` | the 45-module log of the shipped bytes (moved out of the repo root in round 2) |
| `docs/reports/b101_logs/b101_r2_confirm_rebuild.log` | round 2's confirming rebuild after the comment corrections |
| `.gitignore` | `/*.log` + `/local_*` so root build logs cannot be committed again (the `local_` prefix only LOOKED ignored) |

**Removed in round 2** (vet finding, artifact hygiene): `local_baseline_build.log`,
`local_r99_build.log`, `local_r99_postmerge.log`, `local_r99_rebuild.log` - 4 of the 5 root logs round 1
committed (12,341 lines total, none of them gitignored, `main` carries none). Two stale `local/*.arz`
were renamed on disk to `local/STALE_DO_NOT_SHIP_*`.
