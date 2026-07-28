# b93 - DEATH XP PENALTY -90% (R-70), round 1

**Branch** `feat/death-xp-penalty` (worktree `.claude/worktrees/death-xp`, base `main` @ `8c3445c`)
**Date** 2026-07-28
**Scope** DB only (arz + Text coupled pair). NO map rebuild; `Levels.arc` / `Quests.arc` untouched and hash-proven.

---

## 1. THE RULING

Will, 2026-07-27, verbatim:

> "also i want to drastically reduce the xp penalty for dying. at high levels the penalty is way
> too crazy, it needs to be cut by like 90%"

Appended to `docs/WILL_RULINGS.md` as **R-70**, opening a new "Global balance & progression"
section (decade 70-79), status IMPLEMENTED b93.

### Ledger reconciliation (standing law 1)

Ledger swept for `death`, `xp`, `experience`, `penalty` across all 54 rulings. **No prior ruling
touches the death penalty, XP gain, or the level curve.** R-70 overturns nothing.

| Ruling | Domain | Action taken |
|---|---|---|
| R-42 soul drop rates / R-48 Toxeus souls 100% | loot rates | Different axis entirely; no loot field written. |
| R-30 spacing law, R-3/R-49 chest guard | placement | No map, proxy, pool or placement touched. |
| R-50 process laws | this lane | Honoured: ledger appended verbatim same-turn; new surface ships with its gate; debt registered. |

---

## 2. RECON - finding the REAL mechanism (nothing assumed)

### 2.1 What the engine actually reads

`Game.dll` (the TQAE gameplay DLL) contains **exactly one** `*GameEngine.dbr` path literal in the
entire install. `TQ.exe` and `Editor.exe` contain none:

```
Game.dll   ->  "Records/XPack/Game/GameEngine.dbr"
```

Its string table carries, adjacent to the loader's own error message, the three fields that govern
XP loss on death plus the variables bound into the equation:

```
-=- GameEngine Equation load failure : deathPenaltyEquation
deathPenaltyEquation   deathPenaltyMin   deathPenaltyMax
currentPlayerLevel     gameDifficultyDV
averagePlayerLevel     averagePartyLevel      <- these two belong to the XP-GAIN equation
```

So the mechanism is: **XP lost on death = clamp(`deathPenaltyEquation`, `deathPenaltyMin`,
`deathPenaltyMax`)**, evaluated on `records\xpack\game\gameengine.dbr`.

**There is no flat-vs-percentage split and no per-difficulty variant record.** Difficulty enters
only through the single `gameDifficultyDV` term (0 Normal / 1 Epic / 2 Legendary) inside the one
equation. The penalty is therefore a pure function of level and difficulty, and is NOT a percentage
of the player's current XP - which is precisely why it feels mild early and brutal late: it is
**cubic in level**.

### 2.2 Six candidates, five dead - and how they were distinguished

A full-arz scan for `deathPenalty*`-bearing records returns **6 of 51,085**:

| Record | deathPenaltyEquation | Max | Verdict |
|---|---|---|---|
| `records\xpack\game\gameengine.dbr` | `(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)` | 500000 | **LIVE** - the Game.dll literal |
| `records\xpack\game\drxgameengine.dbr` | same | 500000 | dead (DRX authoring copy) |
| `records\xpack\game\copy of gameengine.dbr` | same | 500000 | dead (Iron Lore working copy) |
| `records\xpack\game\xxxgameengine.dbr` | same | 500000 | dead (Iron Lore working copy) |
| `records\game\gameengine.dbr` | same | 500000 | dead (pre-Immortal-Throne path) |
| `records\game\cost backup\gameengine.dbr` | `(currentPlayerLevel^2.95) * ((1+ (2 * gameDifficultyDV)) / 3)` | 500000 | dead - and a genuine **decoy**: a different, plausible-looking formula that would have been a silent in-game no-op |

**How the live one was distinguished (two independent lines of evidence):**

1. **Binary ground truth.** `Records/XPack/Game/GameEngine.dbr` is the only GameEngine path string in
   any shipped binary. Nothing constructs the non-xpack path.
2. **Shipped precedent.** `tools/patches/damage_display.py` (build38, shipped and in the deployed
   arz) fixed the missing floating-combat-text FontStyles by writing **this same record**. Base TQAE
   keeps `DamageNormalStyle` and friends ONLY on the xpack record - `records\game\gameengine.dbr`
   does not contain them at all - yet vanilla TQAE demonstrably renders damage numbers. The engine
   must therefore be reading the xpack record.

`records\game\old\gameengine.dbr` (20 fields) carries no `deathPenalty*` field at all and is not a
candidate.

### 2.3 Provenance - is the current value ours?

Read from five independent `.arz` files:

| Source | deathPenaltyEquation | Max | Min |
|---|---|---|---|
| base TQAE `database.arz` | `... / 9)` | 500000 | 0 |
| SV 0.98i (our build base) | `... / 9)` | 500000 | 0 |
| SV 0.9 | `... / 9)` | 500000 | 0 |
| SV 0.41 | `... / 9)` | 500000 | 0 |
| **deployed DEV arz `1c27d5fa`** | `... / 9)` | 500000 | 0 |

**Pure vanilla TQAE, byte-identical everywhere.** No upstream (amgoz1 / soa / Dragonlord) touched
it and no tool in this pipeline ever wrote a `deathPenalty*` field (grep over `tools/**` before this
lane: zero writers). So the "way too crazy" penalty Will hit is Iron Lore's original tuning, meeting
SV's flattened XP curve and raised level cap.

### 2.4 Registry co-writer check (last-writer-wins, the b90 lesson)

`records\xpack\game\gameengine.dbr` already has ONE registry writer: `damage_display`. Their field
sets are **disjoint** (`Damage*Style` / `Healing*Style` / `PlayerImpairmentStyle` vs
`deathPenalty*`) and neither reads the other's fields, so order between them is immaterial. The new
module is registered immediately after `damage_display` so the expected S4b collision WARN names
exactly that pair; a WARN naming any THIRD module on this record is a real finding.

---

## 3. THE CHANGE

`tools/patches/death_xp_penalty.py`, registry position 15 of 34 (right after `damage_display`).

| Field | dtype | BEFORE | AFTER |
|---|---|---|---|
| `deathPenaltyEquation` | STR | `(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)` | `(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)` |
| `deathPenaltyMax` | INT | `500000` | `50000` |
| `deathPenaltyMin` | INT | `0` | `0` (**UNTOUCHED** - 0 x 0.1 is still 0) |

**Why `9 -> 90` and not a new `* 0.1` factor.** It is exactly x0.1 while adding no new token,
operator or nesting for the engine's equation parser to accept. That parser is a narrower code path
than the item-equation evaluator (docs/MULTIPLAYER_COMPAT.md M1 documents the spawn evaluator
outright rejecting `/`), so the minimal-syntax edit is the safe one. It also leaves the difficulty
term untouched, so Normal : Epic : Legendary keep their vanilla 1 : 4 : 7 weighting.

**Why the cap moves in lockstep.** The penalty is cubic, so the OLD `deathPenaltyMax = 500000`
already bit above ~L86 on Legendary: every death past that point cost a flat 500,000 XP regardless
of level. Scaling only the equation would have delivered **less than the ruled 90% exactly in the
high-level regime Will named**:

| | L90 Legendary | L100 Legendary | L120 Legendary |
|---|---|---|---|
| equation-only scaling | -88.7% | **-84.4%** | **-73.1%** |
| equation + cap scaling (shipped) | **-90.0%** | **-90.0%** | **-90.0%** |

Scaling both makes the reduction exactly 90.0% at every level on every difficulty, and keeps the
cap doing its job (this mod ships `maxPlayerLevel = 1000`).

**Why uniform rather than reshaped.** Will asked for "cut by like 90%" and named high levels as
where it hurts. Because the penalty is cubic, a uniform x0.1 already delivers by far the largest
ABSOLUTE relief exactly there (L85 Legendary: -429,888 XP per death; L20 Legendary: -5,600 XP),
while staying literally faithful to the number he gave and leaving the curve's SHAPE - the thing
Iron Lore tuned - untouched. A shape change (e.g. lowering the exponent) would have been a second,
unrequested design decision.

---

## 4. WORKED EXAMPLE - what it costs to die, before and after

**Inputs, all read from the shipped arz (nothing invented):**

- XP curve (`records\creature\pc\playerlevels.dbr`, the record `malepc01`/`femalepc01` point their
  `levelFileName` at): `experienceLevelEquation = ((1.2 ^ playerLevel) * ((1 + (playerLevel / 0.8)) * (0.0 * playerLevel))) + (65 * ((playerLevel + 1) ^3.25)`.
  SV zeroed vanilla's exponential term with the literal `0.0 * playerLevel` factor, so the live
  curve is **E(L) = 65 x (L+1)^3.25** and `maxPlayerLevel = 1000` (vanilla: exponential term live,
  cap 85). "Level band" below = E(L) - E(L-1), the XP inside the L -> L+1 band.
- XP per kill (`experienceEquation` on the live gameengine):
  `((monsterLevel*15)+((monsterLevel-averagePlayerLevel)*(averagePlayerLevel/3.5)))*(1+(monsterExperience/100))`.
  For a solo player fighting a same-level monster this is `15 x L x (1 + experiencePoints/100)`.
  Measured `experiencePoints` medians in the shipped arz: **Common 0** (2747 records), **Champion 75**
  (999), **Hero 500** (666), **Boss 750** (234).

| Level | Difficulty | Level band XP | **BEFORE** XP lost | % of band | trash kills | hero kills | boss kills | **AFTER** XP lost | % of band | trash | hero | boss |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | Normal | 874,181 | 7,111 | 0.8% | 12 | 2 | 1 | **711** | 0.1% | 1 | 0 | 0 |
| 40 | Epic | 874,181 | 28,444 | 3.3% | 47 | 8 | 6 | **2,844** | 0.3% | 5 | 1 | 1 |
| 40 | Legendary | 874,181 | 49,778 | 5.7% | 83 | 14 | 10 | **4,978** | 0.6% | 8 | 1 | 1 |
| 60 | Normal | 2,156,553 | 24,000 | 1.1% | 27 | 4 | 3 | **2,400** | 0.1% | 3 | 0 | 0 |
| 60 | Epic | 2,156,553 | 96,000 | 4.5% | 107 | 18 | 13 | **9,600** | 0.4% | 11 | 2 | 1 |
| 60 | Legendary | 2,156,553 | 168,000 | 7.8% | 187 | 31 | 22 | **16,800** | 0.8% | 19 | 3 | 2 |
| 85 | Normal | 4,695,993 | 68,236 | 1.5% | 54 | 9 | 6 | **6,824** | 0.1% | 5 | 1 | 1 |
| 85 | Epic | 4,695,993 | 272,944 | 5.8% | 214 | 36 | 25 | **27,294** | 0.6% | 21 | 4 | 3 |
| 85 | Legendary | 4,695,993 | **477,653** | **10.2%** | **375** | 62 | 44 | **47,765** | **1.0%** | **37** | 6 | 4 |

Beyond L86 on Legendary the old cap flattened everything to a constant:

| Level (Legendary) | uncapped equation | BEFORE (capped) | AFTER | cut |
|---|---|---|---|---|
| 90 | 567,000 | 500,000 | 50,000 | 90.0% |
| 100 | 777,778 | 500,000 | 50,000 | 90.0% |
| 120 | 1,344,000 | 500,000 | 50,000 | 90.0% |

**The headline, in Will's terms.** At level 85 on Legendary a death used to cost about **10% of a
level - roughly 375 same-level trash kills, or 44 boss kills, to earn back**. It now costs **1% of a
level: about 37 trash kills, or 4 boss kills.** At level 40 on Legendary it drops from 83 trash
kills to 8. The relief scales with the pain: -429,888 XP per death at L85 Legendary versus -5,600
XP at L20 Legendary.

**Honest caveats on the kill counts.** (a) They assume a solo player and a monster at the player's
own level; the `(monsterLevel - averagePlayerLevel)` term shifts them when the monster is
over/under-levelled. (b) They ignore area XP bonuses and party-size effects. (c) The
`experienceLevelEquation` string as shipped by SV has an unbalanced parenthesis (one `)` short) -
inherited verbatim from SV 0.98i, untouched by this lane and NOT in scope here, but registered as
open debt below because if the engine's parser rejects it the effective curve is whatever the
fallback is, and the "% of band" column would move (the XP-LOST column would not: it comes from a
different, well-formed equation). Every XP-lost number above is exact regardless.

---

## 5. SCOPE PROOF

**Record-diff (`tools/debug/b93_record_diff.py`, baseline `local/baseline_b93.arz` = the deployed
`1c27d5fa` reproduced byte-for-byte from `main`, versus the b93 build):**

```
records: baseline=51085 built=51085  added=0 removed=0
changed records: 1
  [INTENDED] records\xpack\game\gameengine.dbr
      deathPenaltyEquation     (2, ['...(1+ (3 * gameDifficultyDV)) / 9)'])  ->  (2, ['... / 90)'])
      deathPenaltyMax          (0, [500000])  ->  (0, [50000])
RESULT: PASS - diff == the b93 intent exactly
```

**One record, two fields, zero added, zero removed.** dtypes preserved (STR stays 2, INT stays 0).

Layered scope proofs inside `apply()`, all fail-loud:
- pre-state assertion (must be the exact vanilla pair, or already-ruled = idempotent no-op);
- dtype before/after equality on both fields;
- field-set equality on the record + "exactly these two fields moved" + explicit
  `experienceEquation` / `transferCostEquation` non-movement;
- `db._modified` delta ⊆ {the one record};
- all five dead lookalikes still carry their own values.

`verify()` (runs after the WHOLE gate battery, on the FINAL merged arz) re-asserts the three field
values + both dtypes, re-derives the reduction numerically over **L1..1000 x N/E/L** (worst ratio
deviation from 0.10 must be < 1e-9), and re-checks the five lookalikes.

---

## 6. GATE (no-new-surface law)

New contract domain **`tools/contracts/contracts_balance.py`** (auto-discovered by
`run_contracts.py` as domain `balance`), with `whitelist_balance.txt` (empty - no suppressions):

| Contract | Sev | Asserts |
|---|---|---|
| `BAL-DEATHXP-1` | P0 | the engine-loaded xpack gameengine carries the ruled equation / max 50000 / min 0, dtypes STR+INT intact |
| `BAL-DEATHXP-2` | P0 | clamp(shipped) == 0.10 x clamp(vanilla) at every level 1..maxPlayerLevel on N/E/L - catches the "divisor fixed, cap forgotten" regression |
| `BAL-DEATHXP-3` | P1 | the 5 non-engine-loaded lookalikes still carry their own vanilla values (catches the wrong-record fix) |
| `BAL-XPGAIN-1` | P1 | `experienceEquation`, `experienceLevelEquation` and `maxPlayerLevel` unmoved - this lane may not touch XP gain or the curve |

**Planted negative tests** (`tools/contracts/tests_balance_negative.py`, **26/26 PASS**): divisor
reverted to `/ 9`; cap reverted to 500000; floor lifted off 0; INT->FLOAT and STR->INT dtype
corruption; the live record deleted; **the cap left at 500000 while the divisor is scaled** (and an
assertion that the evidence names a level >= 80, not level 1); an over-cut to `/ 900`; the equation
shape made unverifiable; the ruled value mirrored into a dead lookalike; a lookalike cap edited; XP
gain buffed; the level curve flattened; the level cap moved. Plus a cross-check that every constant
in the gate equals the corresponding constant in the build module, so the two can never drift.

**Real-world negative proof:** the same contract run against the **pre-change deployed arz**
(`SoulvizierClassicDEV.arz` `1c27d5fa`) exits 1 with 3 P0 (`BAL-DEATHXP-1` x2 + `BAL-DEATHXP-2`);
against the b93 build it PASSES with 0 violations.

---

## 7. MULTIPLAYER

`records\xpack\game\gameengine.dbr` is a **DATABASE record, therefore SHARED** - it is not
client-side-only state. Per docs/MULTIPLAYER_COMPAT.md "Determinism statement", every player must
ship the byte-identical `.arz`, so both players must re-sync the new artifact before co-op (the arz
hash changes; that is the normal per-build requirement, not a new one).

Behaviourally it is MP-neutral:
- the equation binds only `currentPlayerLevel` and `gameDifficultyDV` - **no party-size or
  `averagePartyLevel` term**, so a 2-6 player session loses the same XP per death as solo;
- it is not a proxy/spawn equation, so the M1 `/`-rejection hazard does not apply (M1 is scoped to
  the spawn evaluator; this string already contained a `/` in vanilla and has always parsed on the
  item/gameengine evaluator);
- no new record, no new entity, nothing host-authoritative.

**FLAGGED, not blocking:** MULTIPLAYER_COMPAT.md's quoted "current expected database hash" is
already stale (it names build27); it should be refreshed on the next MP-facing pass rather than by
this lane. Registered as debt below.

---

## 8. BUILD RESULT

| artifact | md5 |
|---|---|
| built arz (b93) | `de589633d06a62d92afcd29b8701b74c` (55,424,420 B) |
| baseline arz (rebuilt from `main` @ `8c3445c`; **== the deployed `1c27d5fa` byte-for-byte**) | `1c27d5fa650b5c076696db4ad379672f` (55,424,142 B) |
| `Text.arc` (rebuilt from the BUILD-EMITTED `uber_soul_tags.txt`) | `fcca49277b9d31ed451e4a6843898843` - **unchanged** |
| `uber_soul_tags.txt` (build-emitted) | `49b6d85ba15236aa5df60f610e3a7bf0` |
| `Levels.arc` BEFORE == AFTER | `fc0adcc0713839a685b32d6e122653be` (work tree) / `943d0ab9516d332db79bd7f9fd2d3ffe` (DEV) |
| `Quests.arc` BEFORE == AFTER | `5e664c7b190965fd69f6ff15d77d85e4` |

The baseline rebuild reproducing the deployed `1c27d5fa` **exactly** is this lane's determinism
proof: the only delta between `1c27d5fa` and `de589633` is the two intended fields (+278 bytes = the
longer equation string plus one new string-table entry, 143343 -> 143344 strings).

Gates: build exit 0, every fail-loud invariant green, `death_xp_penalty.verify OK`, `validate_tags`
PASS (417/417 authoritative), negative tests 26/26, contracts **0 P0 / 1252 P1 (pre-existing,
identical count on the baseline arz) / 3653 P2** with a violation-set diff of **0 new violations**.
Full detail: the BUILD54-DEV gate record in `docs/BACKLOG.md`.

---

## 9. DEPLOY - NOT PERFORMED (blocked on a concurrent lane)

At 13:29 the DEV entry held `1c27d5fa` - the ground truth this lane's baseline reproduces. At
**13:55:19, mid-build, a concurrent lane deployed a different arz to the same DEV entry**:
`5143ad1a44a9964c22578e00613f3e14` (55,424,139 B). Record-diff of that deployed arz against this
lane's baseline:

```
records: baseline=51085 built=51085  added=0 removed=0
changed records: 12   (all one field: mesh, RevenantPoison.msh -> Skeleton01.msh)
  um_toxeus_enslaver_99 / um_bloodtoxeus_99 / q_bloodtoxeus_ambush / q_bloodtoxeus_lone /
  q_enslaver_warband / q_yard_enslaver / bloodtoxeus_1..3 / toxeus_enslaver_1..3
```

That is a Toxeus mesh lane (`fix/green-diff`, "b92 GREEN GLOW root cause: the mesh attaches the
aura", is the likely owner). It is **entirely disjoint** from b93 (12 creature/pet/proxy `mesh`
fields versus 1 gameengine record), so a merged build carries both cleanly - but the b93 arz was
built from `main` and does not contain it, so copying `de589633` onto DEV would **silently revert all
12 mesh fields**. That is precisely the last-writer-wins clobber the b90 lesson and the standing code
discipline forbid, so **the deploy was deliberately not performed.**

Backups taken before anything was touched: `local/db_backups/SoulvizierClassicDEV_pre-b93_1c27d5fa.arz`
(the filename records the intent; the file actually captured the concurrent lane's `5143ad1a`, which
is the truthful pre-deploy state) and `local/db_backups/DEV_Text_pre-b93_fcca4927.arc`.

**Required next step (orchestrator):** merge `feat/death-xp-penalty` with the Toxeus-mesh branch, run
ONE rebuild off the merged tree, and do ONE coupled arz+Text deploy. Do not hand-patch either
artifact. `Text.arc` needs no change either way.

**Levels / Quests untouched proof** (re-hashed on the DEV entry after all b93 work):
`Resources/Levels.arc` = `943d0ab9516d332db79bd7f9fd2d3ffe`, `Resources/Quests.arc` =
`5e664c7b190965fd69f6ff15d77d85e4` - both identical to the values recorded at the start of the lane.
**TQ.exe was running throughout and was NOT killed** (standing ban). Will must kill TQ + Steam and
restart before any test.

---

## 10. OPEN DEBT

- **BL-b93-DEBT-1** IN-GAME CONFIRMATION IS LAUNCH-GATED. Nothing here has been observed in a
  running game. Will must kill TQ + Steam, restart, and die once on a high-level Legendary character
  to confirm the felt difference. (Standing restart-before-test law.)
- **BL-b93-DEBT-2 (P0)** THE DEV DEPLOY IS BLOCKED on merging this lane with the concurrent
  Toxeus-mesh lane (section 9).
- **BL-b93-DEBT-3** STEAM / CANONICAL NOT SHIPPED. This lane targets the DEV entry only.
- **BL-b93-DEBT-4** SV's `experienceLevelEquation` has an unbalanced parenthesis (inherited from SV
  0.98i, present in the deployed arz, untouched here). Someone should establish whether the engine's
  parser accepts it or falls back - it decides whether the shipped XP curve is really
  `65*(L+1)^3.25`. Does not affect any XP-LOST number in section 4.
- **BL-b93-DEBT-5** `docs/MULTIPLAYER_COMPAT.md` quotes a stale build27 arz hash in its determinism
  statement; refresh on the next MP pass.
- **BL-b93-DEBT-6** The five dead gameengine lookalikes are now gated as "must stay vanilla" but are
  otherwise unmanaged dead weight. A future cleanup pass could retire them - **subject to the
  retirement protocol** (Will-veto by default).
