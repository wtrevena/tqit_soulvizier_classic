# b99 CONTENT INTEGRATION WAVE (round 1) - four vetted lanes merged, built once, deployed once

**Branch:** `integration/content-wave` (from `main` @ `a0276ab`)
**Date:** 2026-07-29
**Scope:** DB-only. **No map rebuild.** `Levels.arc` and `Quests.arc` deliberately NOT deployed.

---

## 1. What was merged

| lane | branch | tip at merge | what it is |
|---|---|---|---|
| b93 | `feat/death-xp-penalty` | `5b30150` | on-death XP loss cut by exactly 90% (`deathPenaltyEquation` divisor 9 -> 90, `deathPenaltyMax` 500000 -> 50000 on `records\xpack\game\gameengine.dbr`) + the new `balance` contract domain |
| b95 | `feat/sargath-soul` | `dccbccf` | Sargoth Manbane's soul now summons him (R-51, the R-43 High-Priest second-builder pattern); new module `sargoth_soul_summon.py` + a 6th leg on the shared `enslaver_pet_fx._CHAIN` gate |
| b96 | `feat/vashkarr-soul` | `2012684` | Vashkarr spear-and-shield retune (pierce damage + penetration mirroring Spawn of Chi, run speed -8% -> +12/17/22%, damage up, elemental -8/-7/-6) + the `SOUL-IDENTITY-SHAPE` contract |
| b97 | `fix/soul-identity` | `e3f7c32` | 22 wrong-soul mismatches detached roster-wide + the permanent, list-free identity gate (round 2 also fixed the gate's own `\creature(s)\` scope blind spot) |

All four branched from `8c3445c`, i.e. **before** main's 2026-07-28 debt-wave integration, so every merge was a real three-way merge against newer content.

---

## 2. Conflicts, file by file

| file | conflict | resolution |
|---|---|---|
| `docs/BACKLOG.md` | 5 hunks across 3 merges (gate records prepended at the top; DEBT REGISTER blocks) | union, ordered **newest build first** (b97 build59 > b96 build57 > b93 build54 > b91). Nothing dropped. |
| `docs/WILL_RULINGS.md` | 3 hunks | union **plus a real content reconciliation** - see §3. |
| `tools/patches/__init__.py` | REGISTRY: `death_xp_penalty` auto-merged; `sargoth_soul_summon` auto-merged; `soul_identity` collided head-on with main's 4-module debt-wave block | **order DERIVED from the colliding constraints, not concatenated** - see §4. |
| `tools/build_svc_database.py` | `_require_gates` (debt wave) and `_load_sv098_name_tags` (b97) inserted at the same offset | union, both kept, PEP8 spacing restored, file re-parsed. |
| `tools/apply_svc_patches.py` | 3 lanes touched it | auto-merged cleanly (disjoint regions); verified by build. |

**CRLF hazard:** the repo's markdown is CRLF, so the conflict markers land as `'=======\r'` and a naive equality check misses them. Every sweep used a **strip-compare**. Final sweep: **586 files scanned, 0 leftover markers.** Both markdown files were re-normalised to pure CRLF after resolution (the union insert had introduced single LF-only lines).

---

## 3. The R-70 collision (three-way) - a real finding, not a merge artefact

`main` **already owned R-70 and R-71**, minted into the "Souls & items overflow decade 70-79" by the 2026-07-28 debt-wave integration. Both `feat/death-xp-penalty` and `feat/vashkarr-soul` branched before that and **each independently minted its own "R-70"** - three different rulings under one number, in a ledger whose whole purpose is unambiguous citation.

Resolved on the incumbent-keeps-the-number precedent set by `fix/debt-docs`' LEDGER HYGIENE PASS:

| ruling | was | now | why |
|---|---|---|---|
| main's tomb-guardian ruling | R-70 | **R-70** (unchanged) | incumbent |
| main's debt-db ruling | R-71 | **R-71** (unchanged) | incumbent |
| b96 Vashkarr | R-70 | **R-72** | stays in the Souls overflow decade; its duplicate `### Souls & items (overflow decade 70-79)` header and the now-redundant "decade is exhausted" blockquote were dropped (main's header note and R-71 already record that decision) and the ruling folded into the EXISTING `### Souls & items (continued)` section |
| b93 death-XP | R-70 | **R-80** | "Global balance & progression" takes a fresh reserved decade **80-89**, since 70-79 is Souls' overflow |

The renumber was propagated through **every citation**: 8 files, 38 occurrences (report bodies, `contracts_balance.py`, `contracts_souls.py`, `tests_balance_negative.py`, `tests_souls_negative.py`, `apply_svc_patches.py`, `tools/patches/__init__.py`, and both docs). The ledger's decade-reservation note now records the 80-89 reservation. Verified afterwards: `R-70 x5` (all main's), `R-71 x1`, `R-72 x2`, `R-80 x1`.

---

## 4. The registry collision - `soul_identity` vs the debt-wave block

`fix/soul-identity` registered `soul_identity` in the slot immediately before the no-op `visuals`, from a base that predates main's four debt-wave modules, which claim that same slot. The position was **derived from the two colliding constraints**:

* **`soul_identity`** requires "after EVERY soul-wiring + drop-rate module, so `apply()` sees the FINAL carrier set" -> it must follow `emberteeth_summon` (the last soul-wiring module), `sargoth_soul_summon` (b95, likewise) and `toxeus_souls_100` (the last `chanceToEquipFinger2` writer).
* **`uber_quest_markers`** declares that it "reads `chanceToEquipFinger2` ... so the roster is computed against FINAL rates". `soul_identity` is now the **last writer of that field** (it zeroes it on the 22 thieves), so the marker roster is computed against final rates only if `soul_identity` runs **before** it. Registering it after would leave `uber_quest_markers`' `apply()` deriving from stale pre-detachment rates while its `verify()` re-derives on the final db - the two could disagree.

Final order: `... sargoth_soul_summon, toxeus_souls_100, emberteeth_summon, soul_identity, coldworm_buffs, uber_quest_markers, fx_dangling_cleanup, visuals`. This is the only position satisfying both; `coldworm_buffs` and `fx_dangling_cleanup` are unmoved.

**Registry:** 40 modules, order hash `4072c4443e2589b68d1ec1d3dfe9fe246c326ab20b86046c546d155407879b02` (main: 37 modules, `368236bc454e...`).

**The interaction was then PROVEN inert, not assumed:**

| | baseline (main, no `soul_identity`) | integrated (`soul_identity` runs first) |
|---|---|---|
| `uber_quest_markers` roster | **25** placed-uber records (2 already marked, 23 newly marked, 27 retinue excluded, 1 SHARED left alone) | **25** placed-uber records (2 / 23 / 27 / 1) - **identical** |

None of the 22 detached records is a placed uber or a chain anchor, so no marker moved. The ordering is a permanent guarantee rather than a repair.

### The other cross-lane question: does b95's NEW summon wiring trip b97's mismatch detector?

**No.** `soul_identity` ran *after* `sargoth_soul_summon` and judged **929 live carriers across 616 distinct soul names**, convicting exactly the **22** records the b97 audit had classified - Sargoth's newly-wired soul family and Emberteeth's are untouched, and `[soul_identity] verify OK` on the final merged db. Symmetrically, `enslaver_pet_fx`'s chain gate went **4 -> 5 rostered families**, and `_negtest_sargoth_chain` plants six breaks in Sargoth's `item -> skill -> icon -> spawnObjects -> pet -> portrait` chain and the gate **fires on every one** (6/6 PASS).

---

## 5. Build (one build, coupled)

Built with `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, then `Text.arc` from the **build-emitted** `work/SoulvizierClassic/Database/uber_soul_tags.txt` (never a stale `local/` copy).

| artifact | bytes | md5 |
|---|---|---|
| `work/.../Database/SoulvizierClassic.arz` (51,093 records) | 55,443,197 | `f6cd8698b1578a389fd6a432c1f757cb` |
| `work/.../Database/uber_soul_tags.txt` (build-emitted) | 32,254 | `38ae5e6c839a8256c1b9f24f67cc2ff0` |
| `work/.../Resources/Text.arc` (from that manifest) | 88,733 | `4162a3e09ce2668e18ef42b040b319cc` |

**Baseline** rebuilt from `main` @ `a0276ab` with the identical environment:

| artifact | bytes | md5 |
|---|---|---|
| baseline `SoulvizierClassic.arz` (51,089 records) | 55,432,599 | `1650f6cbd83436a11d30465966d747ba` |
| baseline `Text.arc` | 88,715 | `cec3194e615fa4fb00488203a901eff3` |

The baseline reproduced **byte-identically** to the independently-built `SVC_b98_baseline.arz` already on disk - a free determinism proof.

**`Text.arc` tag-level delta vs baseline: ADDED 1 / REMOVED 0 / CHANGED 0** - exactly `tagSVCSummonSargoth = 'Summon Sargoth Manbane'`.

---

## 6. Record diff - every delta attributed

`py tools/debug/b99_record_diff.py <baseline.arz> <built.arz>` -> **exit 0**.

```
records  : baseline 51089 -> built 51093
ADDED 4 / REMOVED 0 / CHANGED 30
```

| lane | records | detail |
|---|---|---|
| b93 death-xp-penalty | 1 changed | `xpack\game\gameengine.dbr` [`deathPenaltyEquation`, `deathPenaltyMax`] |
| b95 sargoth-soul (new) | 4 added | `soulskills\pets\sargoth_{1,2,3}.dbr` + `soulskills\summon_sargoth.dbr` |
| b95 sargoth-soul (wiring) | 4 changed | the 3 SV-original `dragonian\sargoth_soul_{n,e,l}.dbr` **plus SV's shipped Dropbox artefact** `sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07).dbr` - the module wires 4, not 3 |
| b96 vashkarr-soul | 3 changed | `svc_uber\vashkarr_soul_{n,e,l}.dbr`, 11 fields each |
| b97 soul-identity | 22 changed | `chanceToEquipFinger2` -> 0, one field each |

**0 REMOVED, 0 unattributed.** The attribution gate rejects an added record that matches only a field-scoped rule, so a mis-bucketed delta fails the same way an unexplained one does.

---

## 7. Gates (real output)

**Registry selfcheck:** `patches-registry selfcheck OK: 40 module(s), order 4072c444...`

**Collision gate:** 92 records written by 2+ modules (baseline: 91). The single new pair is the one the b93 registry comment predicted as expected-and-benign:
`records\xpack\game\gameengine.dbr <- damage_display, death_xp_penalty` (disjoint field sets, neither reads the other's). **No third module on that record**, and `soul_identity` / `sargoth_soul_summon` caused **no collisions at all**.

**`validate_tags`: PASS** - all 358 referenced mod tags present in `Text.arc`; 2 pre-existing base/SV monster-name WARNs (backlog, non-blocking, unchanged).

**FULL contracts battery** (6 modules / 62 contracts), identical config over both arzs:

| module | baseline (main) | built (this wave) |
|---|---|---|
| balance | 3 viol (**3 P0**) FAIL | 0 viol OK |
| map | 5 (0/0/5) OK | 5 (0/0/5) OK |
| quests | 2 (0/0/2) OK | 2 (0/0/2) OK |
| resources | 4618 (0/0/4618) OK | 4618 (0/0/4618) OK |
| souls | 13 viol (**13 P1**) FAIL | 0 viol OK |
| summons | 112 (0/0/112) OK | 112 (0/0/112) OK |
| **TOTAL** | **4753 (3 P0, 13 P1, 4737 P2) - GATE: FAIL** | **4737 (0 P0, 0 P1, 4737 P2) - GATE: PASS** |

Set-level comparison of the two violation sets (not just the counts):

```
ONLY-IN-BASELINE (cleared by this wave): 16
   [P0] BAL-DEATHXP-1 x2, BAL-DEATHXP-2 x1   records\xpack\game\gameengine.dbr
   [P1] SOUL-IDENTITY-SHAPE x13              vashkarr_soul_{n,e,l}.dbr
ONLY-IN-BUILT (introduced by this wave): 0
```

So the pre-existing P2 debt is the **byte-identical set** on both sides (4737 = 4737, zero only-in-either), and the wave **clears 16 blocking violations and introduces none**. The 3 P0 / 13 P1 on the baseline are simply b93's and b96's own contracts firing on a `main` that does not yet contain their fixes.

**Negative-test suites:**

| suite | result |
|---|---|
| `tests_balance_negative` | **26/26 PASS** |
| `tests_souls_negative` | **21/21 PASS** |
| `tests_soul_identity_negative` | **ALL ASSERTIONS HELD** (incl. T6 out-of-`\creature(s)\`-scope and T7 pet-not-a-carrier) |
| `tests_quests_negative` | **19/19 PASS** |
| `tests_resources_negative` | **ALL CONTRACTS FIRED** |
| `_negtest_sargoth_chain` | **6/6 PASS** (all six planted chain breaks fire) |
| `tests_summons_negative` | 11/13 - `SUMMON-PET-NAKED` and `MONSTER-SPAWN-ELIGIBILITY` report `FAIL(no real fire)` |

The two `tests_summons_negative` failures are **PRE-EXISTING and PROVEN so**: the identical run against the **baseline** `main` arz produces the identical two failures. Unchanged by this wave.

**Module `verify()` hooks on the final merged db** - all green, including:
* `death_xp_penalty.verify OK` - divisor 90 + max 50000 + min 0, dtypes STR/INT intact, uniform **-90.0%** over L1-1000 x N/E/L, all 5 dead lookalikes byte-equal to vanilla.
* `[sargoth_soul_summon] verify OK` - all 3 tiers grant `summon_sargoth` manual-cast at levels 1/2/3, 3 permanent named Beastman pets from `hero_tarthon_na'arak_37`.
* `[soul_identity] verify OK` - no creature drops another named creature's soul, on the FINAL merged db.
* `uber_quest_markers verify OK` - 25/25 placed-uber records carry `DisplayAsQuestItem=1`.

### Tooling debt found while running the battery (pre-existing, not this wave)

`contracts_resources._BASELINE` hardcodes an absolute path into a **dead session scratchpad**
(`.../55f6c1cb-.../scratchpad/contracts_baseline`). It is **byte-identical on `main`**, so this is pre-existing repo debt, but it means `tests_resources_negative` and `tests_summons_negative` cannot run unattended out of the box. Both were run here through a harness that rebinds the constant to the live build's artifacts; no repo file was changed. Registered as **BL-b99-DEBT-3**.

---

## 8. DEV drift - what was actually there (see BACKLOG gate record for the deploy hashes)

The DEV entry looked incoherent (four artifacts, three different timestamps). It is not: **every byte of it is `feat/leinth-wave` b94 round 2.** Round 1 deployed arz+Text+Quests at 15:07; round 2 rewrote only the arz at 18:56 because Text and Quests were byte-identical to round 1. That fully explains the mixed timestamps, and it is confirmed against that lane's own gate record, which names all four hashes.

**Nothing on DEV exists in no branch**, so this was not a STOP condition. `Quests.arc` is owned by the live `feat/leinth-wave` lane (its PART C Leinth exit-portal fix), so `Quests.arc` and `Levels.arc` were left untouched.

| | |
|---|---|
| **REMOVED from DEV** (all `feat/leinth-wave` b94, all on the branch) | 13 records (`svc_leinth_{choir_bloodborn,crimson_tithe,sanguine_mire}`, 7 `genericboss05*`/`genericbossorb_05` containers, 3 `svc_uberorb_apex_*01c` loot tables) + **75 field deltas** (`q_leinth_47/49/50` buffs, `leinth_summon_uglies` caps, 3 `bosschest_leinth_*` tables, `treasureProxyName` on the 2 Toxeus champions) |
| **RESTORED to DEV** (main's debt wave, which DEV predated) | 8 records + ~454 field deltas: `fx_dangling_cleanup` 353, `coldworm_buffs` 70, `uber_quest_markers` 23, `emberteeth_summon` 7 (+3 pets +summon skill), the F3 spear field, and `fix/green-diff` b92's 12 Toxeus `mesh` fields |
| **ADDED by this wave** | 4 records + 65 field deltas |

### A note on how that split was measured

Two earlier passes of the drift probe produced a misleading "215 records would revert". A DEV-vs-main
field delta has **two opposite causes** that value comparison alone cannot separate: DEV being
*behind* main (deploying **adds** the work) and DEV being *ahead* via leinth-wave (deploying
**removes** it). The figures above come from a third pass that classifies by **provenance** -
matching each delta against the field/record signatures the debt-wave modules own - with the actual
before/after values printed so the classification is auditable. A fourth pass that keyed purely on
value relationships reported "0 lost fields", which is also wrong, in the other direction: leinth's
field edits satisfy `main == built` and so fell into the catch-up bucket. The provenance
classification is the one to trust, and it is the one quoted here.

### Coupling proof

Keeping leinth-wave's `Quests.arc` on top of this arz is **safe**: every DB record the deployed
PART C drives is present in this build - `...\bloodcave\portals\vortexportal_exit.dbr`,
`...\bloodcave\triggers\door_bossroom_trap.dbr`, and 6 `q_leinth*` proxies. (An early probe flagged
`door_bossroom_trap` as dangling; that was **my probe's wrong path** - the record lives under
`triggers\`, and it is present in the deployed arz and in this build alike.) The 13 removed records
are loot tables and Leinth skill records referenced **only from the arz side**, and the arz is
replaced atomically, so the revert is self-consistent and creates no dangling reference.
