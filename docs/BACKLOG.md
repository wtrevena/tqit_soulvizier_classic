# BACKLOG - Open issues (as of 2026-07-08, from Will's live TESTHUB play session)

## BUILD62-DEV GATE RECORD - b99 CONTENT INTEGRATION WAVE round 1: four vetted lanes merged, ONE build, ONE coupled deploy (2026-07-29, branch `integration/content-wave`, tag `build62-dev`)

> ⚠️ **TAG DEVIATION:** the brief asked for `build60-dev`. That tag, **and `build61-dev`**, were
> already claimed by the in-flight `feat/endless-hunt` lane (b98, `2537508` and `74438bf`) before
> this wave ran. This wave therefore took the next free tag, **`build62-dev`**.

**MERGED** (actual tips, re-read at merge time - not remembered shas):

| lane | branch | tip | merge commit |
|---|---|---|---|
| b93 death XP penalty -90% (R-80) | `feat/death-xp-penalty` | `5b30150` | `aa54b3f` |
| b95 Sargoth Manbane soul summons him (R-51) | `feat/sargath-soul` | `dccbccf` | `8b0809a` |
| b96 Vashkarr spear-and-shield retune (R-72) | `feat/vashkarr-soul` | `2012684` | `12e1380` |
| b97 soul-vs-monster identity, 22 thieves | `fix/soul-identity` | `e3f7c32` | `a80e3c0` |

All four branched from `8c3445c`, **before** main's 2026-07-28 debt-wave integration, so all four
were real three-way merges. Full detail: `docs/reports/b99_content_wave.md`.

**CONFLICTS, file by file:** `docs/BACKLOG.md` (5 hunks, union, newest-build-first);
`docs/WILL_RULINGS.md` (3 hunks, union **plus a genuine reconciliation**, below);
`tools/patches/__init__.py` (REGISTRY, order **derived** not concatenated, below);
`tools/build_svc_database.py` (`_require_gates` + `_load_sv098_name_tags` unioned, spacing restored,
re-parsed); `tools/apply_svc_patches.py` (auto-merged, disjoint regions).
**CRLF:** the markdown is CRLF, so markers land as `'=======\r'`; every sweep used a STRIP-compare.
Final sweep **586 files, 0 leftover markers**; both docs re-normalised to pure CRLF.

**🔢 THREE-WAY R-NUMBER COLLISION (a real finding).** `main` already owned **R-70 and R-71**
(Souls overflow decade 70-79, minted by the debt-wave integration). `feat/death-xp-penalty` and
`feat/vashkarr-soul` both predate that and **each independently minted its own "R-70"** - three
rulings, one number, in the ledger whose entire purpose is unambiguous citation. Resolved on the
`fix/debt-docs` LEDGER-HYGIENE precedent (incumbent keeps the number): main's R-70/R-71 unchanged;
**b96 Vashkarr R-70 -> R-72**, folded into the EXISTING `### Souls & items (continued)` section (its
duplicate overflow-decade header + now-redundant blockquote dropped); **b93 death-XP R-70 -> R-80**,
with "Global balance & progression" taking a fresh reserved decade **80-89**. Propagated through
**38 citations across 8 files** (both docs, both reports, `contracts_balance.py`, `contracts_souls.py`,
`tests_balance_negative.py`, `tests_souls_negative.py`, `apply_svc_patches.py`, `patches/__init__.py`).
Post-check: `R-70 x5` (all main's), `R-71 x1`, `R-72 x2`, `R-80 x1`.

**🧩 REGISTRY COLLISION - ORDER DERIVED FROM THE CONSTRAINTS.** `soul_identity` claimed the
pre-`visuals` slot that main's 4-module debt-wave block also claims. Position derived, not unioned:
`soul_identity` must run after every soul-wiring + drop-rate module (its own rule -> after
`emberteeth_summon`, `sargoth_soul_summon`, `toxeus_souls_100`), **and before `uber_quest_markers`**,
which declares it reads the FINAL `chanceToEquipFinger2` - a field `soul_identity` is now the last
writer of. Only that slot satisfies both. `coldworm_buffs` / `fx_dangling_cleanup` unmoved.
**REGISTRY: 40 modules, order `4072c4443e2589b68d1ec1d3dfe9fe246c326ab20b86046c546d155407879b02`**
(main: 37, `368236bc454e...`).

**⚠️ THE FOUR LANES' GATES ALL STILL PASS TOGETHER - proven, not asserted:**
* `uber_quest_markers` roster is **25 placed ubers (2 already marked / 23 newly marked / 27 retinue
  excluded / 1 SHARED left alone)** on the baseline **and identical on the integrated build** - none
  of the 22 detached records is a placed uber or chain anchor, so the ordering moved no marker.
* b97's roster-wide identity gate vs b95's **NEW** soul-summon wiring: `soul_identity` ran AFTER
  `sargoth_soul_summon`, judged **929 live carriers / 616 soul names**, and convicted exactly the
  **22** audited thieves. Sargoth's and Emberteeth's newly-wired families are untouched. The new
  summon does **not** trip the mismatch detector.
* b95's chain gate went **4 -> 5 rostered families**; `_negtest_sargoth_chain` plants 6 breaks in
  Sargoth's item->skill->icon->spawnObjects->pet->portrait chain and the gate **fires on all 6**.
* Collision gate: **92** records written by 2+ modules (baseline 91). The one new pair is the
  EXPECTED, documented-benign `gameengine.dbr <- damage_display, death_xp_penalty` (disjoint fields,
  no third module). `soul_identity` and `sargoth_soul_summon` caused **zero** collisions.

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`; `Text.arc` from the **BUILD-EMITTED**
`work/.../Database/uber_soul_tags.txt`, never a `local/` copy):

| artifact | bytes | md5 |
|---|---|---|
| built `SoulvizierClassic.arz` (51,093 recs) | 55,443,197 | `f6cd8698b1578a389fd6a432c1f757cb` |
| built `uber_soul_tags.txt` | 32,254 | `38ae5e6c839a8256c1b9f24f67cc2ff0` |
| built `Text.arc` | 88,733 | `4162a3e09ce2668e18ef42b040b319cc` |
| baseline arz rebuilt from `main` a0276ab (51,089 recs) | 55,432,599 | `1650f6cbd83436a11d30465966d747ba` |
| baseline `Text.arc` | 88,715 | `cec3194e615fa4fb00488203a901eff3` |

The baseline reproduced **byte-identically** to the independently-built `SVC_b98_baseline.arz`
already on disk - a free determinism proof. **`Text.arc` tag delta: ADDED 1 / REMOVED 0 / CHANGED 0**
(`tagSVCSummonSargoth = 'Summon Sargoth Manbane'`).

**RECORD DIFF vs the main baseline - `tools/debug/b99_record_diff.py`, exit 0:**
**ADDED 4 / REMOVED 0 / CHANGED 30**, every one attributed: b93 gameengine (1 changed, 2 fields);
b95 4 added (`pets\sargoth_{1,2,3}` + `summon_sargoth`) + 4 changed (the 3 SV soul tiers **plus SV's
shipped Dropbox artefact** `sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07).dbr` - the
module wires 4, not 3); b96 3 changed (11 fields each); b97 22 changed (`chanceToEquipFinger2` -> 0).
**0 unattributed.**

**GATES:**
* `validate_tags` **PASS** (358/358 mod tags resolve) - on the built pair **and re-run on the
  DEPLOYED pair**. 2 pre-existing base/SV monster-name WARNs, unchanged.
* **FULL contracts battery, 6 modules / 62 contracts, identical config both sides:**

| | baseline (`main`) | built (this wave) |
|---|---|---|
| balance | 3 viol (**3 P0**) FAIL | 0 OK |
| map / quests / resources / summons | 5 / 2 / 4618 / 112, all P2, OK | 5 / 2 / 4618 / 112, all P2, OK |
| souls | 13 viol (**13 P1**) FAIL | 0 OK |
| **TOTAL** | **4753 (3 P0, 13 P1, 4737 P2) GATE: FAIL** | **4737 (0 P0, 0 P1, 4737 P2) GATE: PASS** |

  Compared at **set level, not just counts**: `ONLY-IN-BASELINE 16` (the 3 `BAL-DEATHXP` P0s and 13
  `SOUL-IDENTITY-SHAPE` P1s - b93's and b96's own contracts firing on a `main` without their fixes),
  **`ONLY-IN-BUILT 0`**. The 4737 P2 pre-existing debt is the **byte-identical set** on both sides.
  So the pre-existing count is not merely "unchanged" - it is the same violations, and the wave
  clears 16 blocking ones while introducing none.
* **Negative tests:** `tests_balance_negative` **26/26**, `tests_souls_negative` **21/21**,
  `tests_soul_identity_negative` **ALL HELD**, `tests_quests_negative` **19/19**,
  `tests_resources_negative` **ALL FIRED**, `_negtest_sargoth_chain` **6/6** (also re-run green on
  the DEPLOYED bytes). `tests_summons_negative` 11/13 - `SUMMON-PET-NAKED` +
  `MONSTER-SPAWN-ELIGIBILITY` `FAIL(no real fire)`, **proven PRE-EXISTING** by the identical run
  against the baseline `main` arz producing the identical two failures.
* Every module `verify()` hook green on the FINAL merged db, including `death_xp_penalty` (uniform
  **-90.0%** over L1-1000 x N/E/L, 5 dead lookalikes byte-equal to vanilla), `sargoth_soul_summon`,
  `soul_identity`, and `uber_quest_markers` (25/25).

**DEPLOYED to DEV** (`CustomMaps\SoulvizierClassicDEV`), coupled **arz + Text ONLY**. TQ was not
running (Steam was; it does not lock mod files). Backups:
`local/db_backups/SoulvizierClassicDEV_pre-b99_9f98e3e8.arz`, `DEV_Text_pre-b99_9f98e3e8.arc`,
`DEV_uber_soul_tags_pre-b99_9f98e3e8.txt`.

| deployed artifact | before | after | verdict |
|---|---|---|---|
| `Database/SoulvizierClassicDEV.arz` | `9f98e3e88bca20f96bacc2fd6bb87b63` | `f6cd8698b1578a389fd6a432c1f757cb` | **== built** |
| `Resources/Text.arc` | `ed31ec8407e59710d4ad28d5532e75ae` | `4162a3e09ce2668e18ef42b040b319cc` | **== built** (coupled pair) |
| `Database/uber_soul_tags.txt` | `c89194fc6f3427cf25712ad8ee6af5fc` | `38ae5e6c839a8256c1b9f24f67cc2ff0` | **== built** |
| `Resources/Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | `943d0ab9516d332db79bd7f9fd2d3ffe` | **UNTOUCHED** |
| `Resources/Quests.arc` | `35bfe3f39e8480408e3c22ea5473f796` | `35bfe3f39e8480408e3c22ea5473f796` | **UNTOUCHED** (a live lane owns it) |

**UNTOUCHED-SIBLING PROOF:** every one of the **62 files** under the DEV entry was md5-hashed before
and after. Exactly **3** changed (the two coupled artifacts + the tag manifest that produced the
Text); the other **59 are byte-identical**, including `Levels.arc`, `Quests.arc`, both `Quests.arc`
side-backups, all 26 resource arcs and all 36 `XPack2/3/4` stubs.

---

### 🔎 DEV DRIFT RESOLUTION (the headline finding)

**The DEV entry was NOT incoherent.** Four artifacts with three timestamps looked like several lanes
had written different pieces; in fact **every byte of it was `feat/leinth-wave` b94 round 2**. Round 1
deployed arz+Text+Quests at 15:07; round 2 rewrote **only** the arz at 18:56 because Text and Quests
were byte-identical to round 1. Confirmed against that lane's own gate record, which names the exact
four hashes (`9f98e3e8` / `ed31ec84` / `35bfe3f3` / `943d0ab9`).

**Quests changed on DEV because `feat/leinth-wave` owns it** (its PART C, the Leinth post-kill exit
portal, is a `tools/build_quest_files.py` change). It is a **LIVE lane**, so `Quests.arc` **and**
`Levels.arc` were left alone, exactly as required.

**IS ANYTHING ON DEV IN NO BRANCH? NO.** Every DEV-only byte traces to `feat/leinth-wave` @ `8a863f6`,
which is intact in git. Nothing is unrecoverable, so this was not a STOP condition.

**WHAT THIS DEPLOY REMOVED FROM DEV (all of it b94, all of it on that branch):** 13 records
(`svc_leinth_{choir_bloodborn,crimson_tithe,sanguine_mire}`, the 7 `genericboss05*` / `genericbossorb_05`
containers, the 3 `svc_uberorb_apex_*01c` loot tables) plus **75 field-level deltas** (the
`q_leinth_47/49/50` buff set, `leinth_summon_uglies` pet caps, the 3 `bosschest_leinth_*` loot tables,
and `treasureProxyName` on the two Toxeus champions). **Restore in one copy** from
`local/db_backups/SoulvizierClassicDEV_pre-b99_9f98e3e8.arz`; the real fix is merge order - merge
`feat/leinth-wave` into the next integration round and rebuild once.

**WHAT THIS DEPLOY RESTORED TO DEV:** DEV's arz was built from `8c3445c` + leinth-wave and therefore
**predated main's whole debt wave**. Deploying brought it forward by **8 records and ~454 field
deltas** it was missing: `fx_dangling_cleanup` (353), `coldworm_buffs` (70), `uber_quest_markers` (23),
`emberteeth_summon` (7 + 3 pets + summon skill), the `fx_dangling_cleanup` F3 spear field, and
`fix/green-diff` b92's 12 Toxeus `mesh` fields (which leinth-wave's own deploy had reverted - see the
DEPLOY COLLISION note in the build55 record). Plus this wave's own 4 records / 65 field deltas.

**COUPLING PROOF (keeping leinth's `Quests.arc` on top of this arz is SAFE):** every DB record that
the deployed `Quests.arc` PART C drives is present in this build -
`records\drxmap\bloodcave\portals\vortexportal_exit.dbr` ✔,
`records\drxmap\bloodcave\triggers\door_bossroom_trap.dbr` ✔, and 6 `q_leinth*` proxies ✔. The 13
records this deploy removes are **loot tables and Leinth skill records referenced only from the arz
side** (`q_leinth_*.skillName*`, `treasureProxyName`), and the arz is replaced atomically, so the
revert is self-consistent and creates no dangling reference.

> ⚠️ **FOR WILL:** DEV now carries b93+b95+b96+b97 + the full debt wave + the green-glow fix, but
> **NOT** b94 (Leinth's apex orb / buffs / cult abilities). The Leinth **exit portal** (PART C) is
> still live because `Quests.arc` was not touched. **Kill TQ + Steam and restart before testing**
> (standing rule), and test souls on **freshly dropped** items - TQ bakes item properties at pickup.

---

## BUILD59-DEV GATE RECORD - b97 SOUL-vs-MONSTER IDENTITY AUDIT round 2 (2026-07-28, branch `fix/soul-identity`, tag `build59-dev`)

**SUPERSEDES the build58-dev record below.** Round 1 was correct in what it did and **incomplete in
what it looked at**; the vet returned NO-GO on completeness and was right.

**THE GAP:** both the audit and the shipped gate were scoped by `_is_creature()`, requiring the
record path to contain `\creature\` or `\creatures\`. **97 live soul carriers were never judged** -
all 25 of `records\drxcreatures\` (shipping DRX/Urder content), 51 in
`records\item\equipmentring\soul\test\`, 4 in `records\test\`, 10 pets, 5 skill-summons, 2 quest
proxies. The 850-row table contained **zero** drxcreatures rows, and the module's "roster-wide,
list-free, any future content module fails the build" claim was simply false for anything authored
outside `\creature(s)\`.

**WHAT WAS HIDING IN IT - a real 19th mismatch of exactly Will's reported class:**
`records\drxcreatures\xurder\d2npc\01_akara.dbr` displays **"Akara"** (`tagD2NPCakara`), is
`Quest`-classified, and dropped **"Kallixenia ~ Liche Queen Soul"** at **66%**, while the real
`Kallixenia ~ Liche Queen` (`xpack\...\abyssalliche\xsq02_lichequeen_36.dbr`) drops an
identically-named soul at the same 66%. **The wire is OURS** -
`apply_svc_patches._create_kallixenia_soul` hard-codes that monster while naming the soul after a
different creature; the function's own docstring shows the author believed the record *was*
Kallixenia. Three more (`soul\test\us_lysiaspellbreaker_15{,_e,_l}`, displaying "Nenea Sharpclaw"
while carrying Lysia Spellbreaker's soul) were hidden the same way.
**RECORDS TOUCHED: 18 -> 22.**

**THREE MORE DEFECTS FIXED IN THE SAME PASS:**
1. **Grouping keyed on the .dbr filename** - the gate repeated, internally, the very
   filename-is-identity mistake it exists to punish. It **merged** `soul\abyssalliche\kallixenia_*`
   with `soul\svc_uber\kallixenia_*` (two genuinely different items sharing a basename) and would
   **split** two items sharing a name. Grouping is now the soul's **DISPLAY NAME**; `_soul_family()`
   survives for reporting only and is directory-qualified. New **ITEM-DETACH GUARD** fails the build
   if any soul ITEM loses its last live carrier without a reviewed waiver.
2. **`apply()` judged PRE-F6 names.** `apply()` runs in `run_registry()`, *before*
   `run_registry_gates()` calls `_apply_soul_naming_standard()` (the documented "final authoritative
   override of the `tags` dict"); `verify()` runs *after*. So the two passes could disagree - and
   did: `tagSVCSoulKallixenia` is `{^F}Soul of Kallixenia` at apply() time and
   `{^F}Kallixenia ~ Liche Queen Soul` in the shipped `Text.arc`. `_display_tags()` now applies the
   same override so both passes judge the text the player sees.
3. **ARCHETYPE vs NAME-DRIFT was split by a row COUNT**, so three archetype rows were filed as "by
   design, just spelled differently" - **Cynisca, Princess of Sparta**, **Corpse Wake** and
   **Meritamen the Shadowcaller** - and report §3 contradicted §5b about Meritamen. The split is now
   data-derived (does a record owning that soul name exist, carrying the same item, gated dead?).
   All three are ARCHETYPE-SHARED; the true 1:1 drift **Wither Mound <-> Speckled Jim** moves to
   NAME-DRIFT. Two reproducibility nits also fixed: both entrypoints hard-defaulted to the gitignored
   `<repo>/upstream/...` (absent in a fresh worktree, so neither tool would run), and
   `--markdown out.md` leaked its value into the positional list and crashed the tool.

**EXPLICIT SCOPE DECISION (the vet asked):** **PETS ARE NOT CARRIERS** (record type `Pet` or a
`\pets\` path segment), nor are quest **spawn proxies** (`\proxies\`). A pet yields no loot to the
player; counting them is *harmful*, not merely useless - the 0.5% monster-scroll pet
`monsterscrolls\pets\maenad_sorceress_20.dbr` displays "Maenad ~ Sorceress" and would be crowned
rightful owner of the Maenad Sorceress Soul, convicting the real 50% **Boss** Meritamen. Verified
empirically. Excluding a record can only ever REMOVE a conviction, so the exclusion fails safe by
construction; `T7` locks it. **`records\test\` and `soul\test\` monsters DO count.**

**AUDIT SCOPE (round 2, roster-wide):** 929 records with a live soul drop; minus 3 pets + 2 proxies =
**926 JUDGED live carriers** (Hero 626 / Boss 174 / Quest 121 / Common 5), **615 distinct soul
NAMES**, 628 distinct monster display names, 9 skipped as unjudgeable (no `description` tag - never
convicted). Verdicts on the pre-fix ground truth: **MATCH 878 / MISMATCH 22 / ARCHETYPE-SHARED 14 /
NAME-DRIFT 12**. On the fixed build: 904 live rows, **MISMATCH 0**. 926 - 22 = 904, exact.
Full **926-row** table: `docs/reports/b97_soul_identity_table.md`.

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`; BUILD ONLY, **NOT deployed**):

| artifact | md5 |
|---|---|
| **ROUND-2 arz FOR THE ORCHESTRATOR** `work/b97r2/Database/SoulvizierClassic.arz` | **`41bc1d9e75df01ee538e2b25f8e0bb7f`** (55,424,077 B) |
| round-1 arz (`3785843`, superseded) | `fcc6fad38d9b8a0fd54a337e23e5ffa8` (55,424,089 B) |
| baseline arz (main `8c3445c`) | `1c27d5fa650b5c076696db4ad379672f` (55,424,142 B) |
| `Text.arc` | `fcca49277b9d31ed451e4a6843898843` - **byte-identical to round 1 AND baseline**, 0 tags authored |
| `uber_soul_tags.txt` | `49b6d85ba15236aa5df60f610e3a7bf0` - byte-identical to round 1 |

**GATES:** DB build **exit 0**; `[33/34] soul_identity -> modified 22 record(s), 0 tag(s)`; step-4
**`[soul_identity] verify OK`**. **RECORD-DIFF r2 vs r1: 0 added / 0 removed / 4 modified**, one
field each (`chanceToEquipFinger2` 66->0 and 2->0), **dtype 1 FLOAT preserved**; chained with round
1's proven 18 vs `main`, the total is **0 added / 0 removed / 22 modified, one field each**.
`validate_tags` **PASS** (356/356 mod tags; 2 pre-existing base-name WARNs). `verify_soul_drop_rates
--gate` **PASS** (832 enabled -> 100 / 446 gated stay 0 - *identical to round 1*, because all four
new records sit outside that gate's own `\creature(s)\` roster: **BL-b97-DEBT-10**). Contracts
`--only souls,summons` **0 P0 / 0 P1 / 112 P2 GATE PASS**, and the round-1 arz through the identical
invocation yields the **byte-identical violation set** (0 only-in-r1, 0 only-in-r2). Planted negative
test **ALL 21 ASSERTIONS HELD** (new: **T6** plants a thief OUTSIDE `\creature(s)\` on the real
`01_akara.dbr` and proves `verify()` fires - the permanent guard against re-narrowing the scope;
**T7** proves a pet convicts nobody). The same suite run against the **round-1** arz correctly
**FAILS T1**, naming Akara and the Lysia trio - machine-checked proof that round 1 shipped the gap.
Ruling spot-checks: R-48 Enslaver **100.0** / Devourer **100.0**, R-45 `um_tombguardian_26` **0.0**,
real Kallixenia still **66.0** with her soul intact, `01_akara` **0.0** with its loot ref intact.

**LEDGER:** `docs/WILL_RULINGS.md` **R-49a** carries a verbatim ROUND 2 AMENDMENT. No ruling
overturned.

**OPEN DEBT:** BL-b97-DEBT-1..11. **Headline WILL DECISION (new): BL-b97-DEBT-7** - zeroing Akara
leaves our bespoke `svc_uber\kallixenia_soul_{n,e,l}` with no carrier (item KEPT intact, name still
obtainable from the real Kallixenia). Three options in report §8 item 5; (b) is a one-field change
that makes Akara *be* Kallixenia, which is what our own code comment intends.

## BUILD58-DEV GATE RECORD - b97 SOUL-vs-MONSTER IDENTITY AUDIT round 1 (2026-07-28, branch `fix/soul-identity`, tag `build58-dev`) - SUPERSEDED by build59-dev above

**R-49a, Will 2026-07-27, verbatim:** "we also need to do an audit of the hero monsters vs the souls
that they drop since i can see that some of the heroes are dropping the wrong souls or souls for
other boss monsters i think" - **CONFIRMED, 18 records.**

DB-ONLY lane (arz + Text coupled pair). **NO map rebuild, NO deploy** (several lanes are editing the
arz concurrently; the orchestrator merges and deploys once). Full report + the 850-row table:
`docs/reports/b97_soul_identity_audit.md` + `docs/reports/b97_soul_identity_table.md`.

**AUDIT SCOPE:** 850 creature records with a LIVE soul drop (Hero 583 / Boss 166 / Quest 101),
591 distinct soul families, 605 distinct monster display names, all difficulty variants + ranks.
Verdicts: **MATCH 808 / MISMATCH 18 / SHARED-ARCHETYPE 13 / NAME-DRIFT 11**.

**ROOT CAUSE (two layers):** a monster's identity is its `description` tag, NOT its .dbr filename.
The base game reuses ONE hero filename across several named heroes -
`ratman\hero_wheedletongue_{39,41,43}` = Wheedletongue the Magnificent / **Fesil the Quick** /
**Sinnet Patchfur** (verified in the TQAE base arz) - and `wire_souls_to_monsters` matches by
FILENAME. SV 0.98i made the same assumption upstream; our build's "already had souls" branch then
ACTIVATED the mis-pairings SV shipped DEAD at chance 0 (**8 of 18 were 0.0 upstream, 9 were 5.0** and
got raised to 50, **1** had no SV/base precedent at all and is our own fuzzy wire). The pre-existing F1 gate `_verify_no_fuzzy_cross_wire` cannot see this:
it scores the soul name against the FILENAME (the wrong axis) and whitelists SV-authored pairings.
The 2026-07-05 yeti fix closed the RANK dimension; this closes the IDENTITY dimension.

**RECORDS TOUCHED (exactly 18, one field each - record-diff vs baseline: 0 added, 0 removed,
18 changed, every change `chanceToEquipFinger2 -> 0.0`):** Fesil the Quick + Sinnet Patchfur +
Blood-Eyes x2 (Wheedletongue soul), Errak Bonecarver + Sartt Soulrender (Kaalt Speartail), Korat
Bearkin (Grom), Raghd Bloatworm (Adara the Lovely), Prince Ch'kik't (Z'kar Flamespinner), Wahr'Ner
Shadowpaw + Nazur the Shrouded (Nephi'tek), Masai-yin + Xuannu the Twilight Matron (Syrinx), Morbi
(Venemurax), Mormo (Storm Crow), Daechalcos (Scarabaeus), Thelxiepeia Venomlip (Aquardia), Colossal
Scorpion (Rocksting). `lootFinger2Item1` deliberately KEPT on all 18 (detach the roll, keep the data
- the A4 Aphiastas-zero / R-45 tombguardian shape): reviewable and reversible.

**IMPLEMENTATION:** new registry module `tools/patches/soul_identity.py`, registered LAST among
content modules (after `toxeus_souls_100`, before `visuals`) so it sees the FINAL carrier set.
Registry order hash `86570c075c72a85ca5f63f018da7a0894371362e389b966c206df8752084253a` (34 modules).
THE RULE is data-derived, not a hand-list: *if some carrier of a soul identity-matches it, every
other carrier that does not is an identity thief; if NO carrier matches, nothing is touched.* The
second clause is why the by-design families are preserved **with no whitelist** and why orphaning a
soul is structurally impossible. Identity is judged on DISPLAY TEXT only; the .dbr filename is never
consulted. Supporting change: `build_svc_database.main()` stashes the display-name table (SV 0.98i
`Text_EN.arc` + `text_tags`/`legacy`/`thrown`/`graft`) on `apply_svc_patches._SV098I_NAME_TAGS`,
outside the prefix cache. A carrier whose monster OR soul name does not resolve is SKIPPED as
unjudgeable, never convicted (this guard alone spared `boss_charon_39` - an R-42/double-soul-ruling
record - in the first build, before the tag table was widened).

**GATES:** three in the module - `verify()` (step 4, over the FINAL merged db post gate-battery and
post drop-rate forcer; LIST-FREE: re-runs the rule and requires an empty answer - the permanent
regression gate), the REVIEW GATE (`apply()` asserts the rule's verdict equals the 18 rows a human
classified; content drift fails loud asking for review), and the ORPHAN GUARD (every affected family
must still have a live matching carrier or the build aborts). Planted negative test
`tools/contracts/tests_soul_identity_negative.py` (T1 clean-db passes, **T2 re-arms the REAL Fesil
the Quick mismatch and proves verify() FIRES**, T3 synthetic cross-wire fires, T4 archetype family
NOT flagged, T5 filename-is-not-identity). Reproducible audit tool `tools/audit_soul_identity.py`
shares the gate's identity function, so tool and gate can never disagree.

**LEDGER:** `docs/WILL_RULINGS.md` **R-49a** IMPLEMENTED b97. **No ruling overturned:** R-48's two
champions are SOLE carriers (untouched; this module's verify() re-proves both at 100.0), R-45 tomb
guardian still 0.0, R-42's 50/66/25 classifier NOT modified (all 18 zeroes carried as documented
per-name waivers in `tools/verify_soul_drop_rates.py` `_KNOWN_EXCEPTIONS`, the legion_soul_stages
shape), R-43 / R-44 / bloodtip / gustleech / legion double-soul chains untouched.

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`; BUILD ONLY, **NOT deployed** - the
orchestrator merges + deploys once):

| artifact | md5 |
|---|---|
| **built arz FOR THE ORCHESTRATOR** | **`fcc6fad38d9b8a0fd54a337e23e5ffa8`** (55,424,089 B) |
| baseline arz (main `8c3445c`) | `1c27d5fa650b5c076696db4ad379672f` (55,424,142 B) |
| `Text.arc` (rebuilt from build-emitted `uber_soul_tags.txt`) | `fcca49277b9d31ed451e4a6843898843` - **byte-identical to baseline**, 0 tags authored |
| `uber_soul_tags.txt` | **byte-identical to baseline** |

Two independent full builds produced the SAME arz md5 (determinism proof).

**GATES:** DB build **exit 0**; every fail-loud invariant green (soul-leak 0 / soul-augment /
soul-itemskill 1388 / F1 cross-wire / F2 summon-identity 21 families / F6 naming / spawn-eligibility /
A7 golden 84 waived 0 other / b77 unlock-alignment). Registry `[33/34] soul_identity -> modified 18
record(s), 0 tag(s)`, **0 unjudgeable carriers**; step-4 hook **`[soul_identity] verify OK`**.
`validate_tags` **PASS** (417/417 authoritative). `verify_soul_drop_rates --gate` **PASS** (exit 0;
testing-forcer survival **832 enabled -> 100 / 446 gated stay 0** vs baseline 850/428 = exactly the 18;
planted post-wire-stomp negtest still CAUGHT). Contracts `--only souls,summons`: **0 P0 / 0 P1 /
112 P2, GATE PASS**, and the baseline yields the **byte-identical violation set** (0 only-in-final,
0 only-in-baseline). **A9 render-chain PASS** (22 upstream WARNs) on the final build AND standalone on
the baseline arz - identical. Planted negative test **ALL 13 ASSERTIONS HELD**. Ruling spot-checks on
the final arz: R-48 Enslaver **100.0** / Devourer **100.0**; R-45 `um_tombguardian_26` **0.0**.

**OPEN DEBT:** BL-b97-DEBT-1..6 (see DEBT REGISTER). Headline: **18 creatures now drop no soul at
all** - inventing one for each is new content (amgoz1 creative bar) and is a WILL DECISION.
## BUILD57-DEV GATE RECORD - b96 Vashkarr spear-and-shield soul retune (2026-07-28, branch `feat/vashkarr-soul`, tag `build57-dev`)

**R-72, Will 2026-07-27, verbatim:** "Vashkarr, Eldest of the Ancients soul should get +% pierce
damage and =% penetration  since he is a spear and shield guy and the soul should give +% boost to
movement not have a penalty for speed, this guy should be fast. also he needs to do more damage. we
can have the penalty be something like -6-8% reduction in elemental damage or something like that"
plus, on field selection: "see spawn of chi soul for how to add +% penetration and pierce damage"

DB-ONLY lane. **NO map rebuild. NOT DEPLOYED** - several lanes are editing the arz concurrently, so
the orchestrator merges and deploys ONCE. Full report: `docs/reports/b96_vashkarr_soul.md`.

**SCOPE (exactly 3 records):** `records\item\equipmentring\soul\svc_uber\vashkarr_soul_{n,e,l}.dbr`.
Identified from the deployed arz by Text tag, not guessed: `tagSVCSoulVashkarr` =
`{^F}Vashkarr, Eldest of the Ancients Soul`. Dropped by `um_vashkarr_99` at 66% Finger2 (there are
no per-difficulty monster variants; difficulty scaling lives in the three item tiers).

**WILL'S PREMISE CONFIRMED:** all three tiers shipped `characterRunSpeedModifier = -8.0` (FLOAT), a
straight movement PENALTY, written by `_apply_b7_eldest_soul_rebalance` as an "ancient and heavy"
downside. No pierce field of any kind was present and `offensiveElementalModifier` was absent.

**AFTER, n/e/l:** `offensivePierceModifier` **40 / 58 / 78** (new) - `offensivePierceRatioModifier`
**35 / 50 / 65** (new) - `characterRunSpeedModifier` **+12 / +17 / +22** (was -8/-8/-8) -
`offensiveElementalModifier` **-8 / -7 / -6** (new). Damage raised: physical 78-124, physMod 46,
OA 110, attack speed 18, bleed 150, life-leech 30 at Legendary (n/e follow the existing 0.6/0.82
ramp). The FIRE package is held FLAT on purpose - nothing retired - so the soul's centre of gravity
moves off the elemental axis, which is the axis the new drawback taxes.

**FIELD PROVENANCE (every effect mirrored from a shipped donor, dtypes preserved, all FLOAT):**
`offensivePierceModifier` + `offensivePierceRatioModifier` <- **Spawn of Chi soul**
(`raptor\spawnofchi_soul_{n,e,l}`, tag `tagSoulName541`, 30/42/58 and 40/54/62), the donor Will
named; 46 shipped souls carry that exact pair. `characterRunSpeedModifier` positive <-
`vulture\sandbeak_soul` 20/26/29 (313 shipped souls carry a positive value).
`offensiveElementalModifier` negative <- `equipmentring\u_n_ringofzakalwe` (Epic RING, same
template/Class, ships -25% elemental / +25% physical: literally the same trade).

**MONOTONICITY, handled deliberately:** the drawback SHRINKS with rarity (-8 -> -7 -> -6), so every
tier stays inside Will's -6..-8% band AND the elemental field is itself monotonically increasing.
No tier is worse than the one below it on any power axis, `souls_quality._flat_tier_violations` is
helped rather than leaned on, and `_FLAT_TIER_WAIVER` stays EMPTY. A deepening penalty would have
passed the gate while being a real tier regression.

**LOAD-BEARING SECOND EDIT:** `_apply_b7_eldest_soul_rebalance` runs AFTER `_create_vashkarr` and
was the last writer on that field, so setting the bonus in the tier stats alone would have been
silently clobbered back to -8. Its -8% clause is now scoped to **GORRAHK ONLY**
(`RUNSPEED_DOWNSIDE = ('gorrahk',)`); Gorrahk's value is unchanged, and the physres-cap /
flat-armour / +25% HP half of that pass is untouched for both families (different Will ruling).

**GATE (no-new-surface law):** new **`SOUL-IDENTITY-SHAPE`** (P1) in
`tools/contracts/contracts_souls.py`, driven by a declarative `SOUL_IDENTITY_SHAPES` registry that
binds a ruling to an asserted field shape (fields present, sign/band, tier ordering) and runs
against the FINAL built arz, so a later pass cannot silently clobber a Will decision back out.
7 planted negative tests in `tests_souls_negative.py` case 11, headed by **11b, which reproduces
today's pre-R-72 shipped state (-8% run speed on all three tiers) and requires the contract to
FIRE**. **Real-world negative proof:** the same contract run over the pre-change baseline arz
yields exactly **13 P1, every one of them `SOUL-IDENTITY-SHAPE` on the three vashkarr records**
(4 tiers x absent field, plus 3 negative-run-speed bounds and 1 ordering break); every OTHER souls
contract is **0 P0 / 0 P1 / 0 P2** on that same run, so the lane's P1 delta is attributable in
full and nothing pre-existing regressed.

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, upstream from the main repo tree):

| artifact | md5 |
|---|---|
| baseline arz (worktree main HEAD `8c3445c`, pre-change) | `1c27d5fa650b5c076696db4ad379672f` |
| built arz (this lane) | **`b88871f25e28791e6ffa00deea223af3`** |
| built `Text.arc` (coupled pair, bytes UNCHANGED - no tag changed) | `fcca49277b9d31ed451e4a6843898843` |
| `uber_soul_tags.txt` (build-emitted) | `49b6d85ba15236aa5df60f610e3a7bf0` |

The baseline rebuild reproduced the md5 recorded for the b91 build **exactly**, which doubles as a
determinism + provenance proof of the whole DB build before a single field was changed.

**BUILT ARTIFACTS** (durable copies for the merged deploy; NOT deployed by this lane):
`local/lane_builds/b96_vashkarr_soul.arz` (55,424,191 B), `local/lane_builds/b96_vashkarr_Text.arc`,
`local/lane_builds/b96_vashkarr_uber_soul_tags.txt`. `Levels.arc` / `Quests.arc` never touched.

**RECORD-DIFF vs baseline: 0 added, 0 removed, 3 changed, 11 fields each** - exactly
`vashkarr_soul_{n,e,l}` and nothing else. `gorrahk_soul_{n,e,l}` do NOT appear, which is the
positive proof that scoping the B7 run-speed clause left Gorrahk byte-identical. All four new/
flipped fields land at **dtype 1 (FLOAT)**, matching their donors (no dtype corruption).

**GATES:** DB build **exit 0**, every fail-loud invariant green (soul-leak 0 leaks, soul-augment,
supra-ref, tags, spawn-eligibility, A9 render-chain, b77 unlock-alignment). **`souls_quality.verify`
OK** - roster tiers monotonic AND strictly progressing (b78 gate) across every soul family, with
`_FLAT_TIER_WAIVER` still EMPTY. **24 registry verify hooks ran, 0 failures**;
`_check_registry.py` OK (33 modules). A7 Occult/Hunting golden guard **PASS** (90 waived, 0 other).
`validate_tags` **PASS** (356/356 referenced, 417/417 authoritative; the 2 `tagNewMonster*` WARNs
are the documented pre-existing pair). Contracts `--only souls,summons` on the built arz:
**GATE PASS, 0 P0 / 0 P1 / 112 P2** (souls lane 0/0/0; the 112 summons P2 are pre-existing and
**identical in count on the baseline run**). `tests_souls_negative.py` **21/21 PASS**
(13 pre-existing + 8 new, headed by the planted pre-R-72 speed-penalty regression).

**LEDGER:** `docs/WILL_RULINGS.md` **R-72** appended VERBATIM, status IMPLEMENTED, in a new
reserved **Souls & items overflow decade 70-79** (the 40-49 decade is exhausted and the file
already carries two accidental duplicate numbers, R-13 and R-43; a third collision was avoided
deliberately).

**OPEN DEBT:** BL-b96-DEBT-1..5 (see DEBT REGISTER).

---
## BUILD54-DEV GATE RECORD - b93 death-XP penalty -90% (2026-07-28, branch `feat/death-xp-penalty`, tag `build54-dev`)

> DEPLOY NOT PERFORMED - the DEV entry was taken by a CONCURRENT lane mid-build. See "DEPLOY" below.
> Everything else (build, gates, record-diff, contracts, ledger, report) is GREEN and complete.

**R-80, Will 2026-07-27, verbatim:** "also i want to drastically reduce the xp penalty for dying. at
high levels the penalty is way too crazy, it needs to be cut by like 90%"

DB-ONLY lane (arz + Text coupled pair). **NO map rebuild** - `Levels.arc` + `Quests.arc` byte-identical
before vs after. Full report: `docs/reports/b93_death_xp_penalty.md`.

**MECHANISM (found in the deployed bytes, not assumed):** `Game.dll` hard-codes exactly ONE GameEngine
path in the whole install - the literal `Records/XPack/Game/GameEngine.dbr` (TQ.exe and Editor.exe
contain none) - and reads three fields off it: `deathPenaltyEquation`, `deathPenaltyMin`,
`deathPenaltyMax`, evaluated as `clamp(equation, min, max)`. Difficulty enters ONLY through the
`gameDifficultyDV` term (0/1/2) inside the one equation: there is no flat-vs-percentage split and no
per-difficulty variant record. **FIVE lookalike records carry `deathPenalty*` and the engine loads
none of them** (`xpack\game\drxgameengine`, `xpack\game\copy of gameengine`, `xpack\game\xxxgameengine`,
`game\gameengine`, `game\cost backup\gameengine` - the last carrying a DIFFERENT formula
`^2.95 * (1+2*DV)/3`, a decoy). Corroborated by shipped precedent: `damage_display` (b38) fixed the
combat-text FontStyles on this same xpack record because base TQAE keeps them only there.

**PROVENANCE:** the before-values are pure vanilla TQAE - byte-identical in base TQAE, SV 0.98i,
SV 0.9, SV 0.41 and the pre-change deployed arz `1c27d5fa`. No prior ruling and no pipeline writer
ever touched a `deathPenalty*` field.

**RECORDS TOUCHED (exactly 1, two fields - record-diff vs `local/baseline_b93.arz`: 0 added, 0 removed,
1 changed):**
- `records\xpack\game\gameengine.dbr`
  - `deathPenaltyEquation` (STR) `...(1+ (3 * gameDifficultyDV)) / 9)` -> `... / 90)` (exactly x0.1, no new parser token)
  - `deathPenaltyMax` (INT) `500000` -> `50000`
  - `deathPenaltyMin` (INT) `0` **UNTOUCHED**

The cap moves in lockstep because the penalty is cubic: the old 500000 cap already bit above ~L86 on
Legendary, so scaling the equation alone would have delivered only **-84.4% at L100 / -73.1% at L120**
- less than the ruled 90% in exactly the high-level regime Will named. Both scaled means **exactly
-90.0% at every level on every difficulty.**

**WORKED EXAMPLE** (shipped curve `E(L)=65*(L+1)^3.25`; kills = solo, same-level, `experiencePoints`
medians Common 0 / Hero 500 / Boss 750):

| L / difficulty | level band XP | BEFORE lost | % band | trash kills | AFTER lost | % band | trash kills |
|---|---|---|---|---|---|---|---|
| 40 Legendary | 874,181 | 49,778 | 5.7% | 83 | **4,978** | 0.6% | **8** |
| 60 Legendary | 2,156,553 | 168,000 | 7.8% | 187 | **16,800** | 0.8% | **19** |
| 85 Legendary | 4,695,993 | 477,653 | 10.2% | 375 | **47,765** | 1.0% | **37** |
| 85 Epic | 4,695,993 | 272,944 | 5.8% | 214 | **27,294** | 0.6% | **21** |
| 100 Legendary (old cap bit) | 6,755,778 | 500,000 | 7.4% | 333 | **50,000** | 0.7% | **33** |

**IMPLEMENTATION:** new registry module `tools/patches/death_xp_penalty.py`, registered at position
16/34 immediately after `damage_display` (the only other writer of that record; their field sets are
disjoint). Deterministic + idempotent; `apply()` carries five layered fail-loud scope proofs
(vanilla-or-already-ruled pre-state, dtype before/after, exactly-two-fields-moved on the record,
`db._modified` delta subset of {that record}, all five dead lookalikes unmoved); `verify()` re-asserts
the values + dtypes on the FINAL merged arz, re-derives the reduction numerically over **L1..1000 x
N/E/L** (worst ratio deviation < 1e-9) and re-checks the lookalikes. **S4b collision gate: 78 -> 79
records, the single new line being `records\xpack\game\gameengine.dbr  <-  damage_display,
death_xp_penalty`** - expected, documented in the REGISTRY comment, and diff-proven to be the ONLY
new collision.

**GATE (no-new-surface law):** new contract domain **`tools/contracts/contracts_balance.py`** (domain
`balance`, auto-discovered) with `whitelist_balance.txt` (no suppressions):
`BAL-DEATHXP-1` (P0, ruled values + STR/INT dtypes), `BAL-DEATHXP-2` (P0, the reduction really is
0.10x vanilla at every level 1..maxPlayerLevel on N/E/L - catches the "divisor fixed, cap forgotten"
regression), `BAL-DEATHXP-3` (P1, the 5 dead lookalikes untouched - catches the wrong-record fix),
`BAL-XPGAIN-1` (P1, XP gain + level curve + level cap unmoved). **26/26 planted negative tests PASS**
(`tools/contracts/tests_balance_negative.py`), incl. a cross-check that every gate constant equals
the build module's. **Real-world negative proof:** the same contract against the PRE-change arz exits
1 with 3 P0; against the b93 build: **0 violations**.

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`):

| artifact | md5 |
|---|---|
| `work/.../Database/SoulvizierClassic.arz` NEW | `de589633d06a62d92afcd29b8701b74c` (55,424,420 B) |
| `work/.../Resources/Text.arc` (rebuilt from the BUILD-EMITTED `uber_soul_tags.txt`; bytes unchanged, no tag changed) | `fcca49277b9d31ed451e4a6843898843` |
| `work/.../Database/uber_soul_tags.txt` (build-emitted) | `49b6d85ba15236aa5df60f610e3a7bf0` |
| `work/.../Resources/mod_authored_tags.txt` | `7836504539e3a4776b60a58c7cb1d0bb` |
| baseline arz (pre-change; rebuilt from `main` @ `8c3445c` and **== the deployed `1c27d5fa` byte-for-byte**) | `1c27d5fa650b5c076696db4ad379672f` |
| `work/.../Resources/Levels.arc` BEFORE == AFTER | `fc0adcc0713839a685b32d6e122653be` |
| `work/.../Resources/Quests.arc` BEFORE == AFTER | `5e664c7b190965fd69f6ff15d77d85e4` |

> The baseline rebuild reproducing the deployed `1c27d5fa` exactly is the determinism proof for this
> lane: the ONLY delta between `1c27d5fa` and `de589633` is the two intended fields.

**GATES:** DB build **exit 0**, every fail-loud invariant green (soul-leak / soul-augment / soul
item-skill activation / supra-ref / tags / spawn-eligibility 44 proxies / A7 Occult-Hunting golden 84
waived 0 other / A9 render-chain / F2 summons + soul-summon identity / F3 diversity / F6 naming / b77
unlock-alignment). Registry verify hook **`death_xp_penalty.verify OK`**. `validate_tags` **PASS**
(417/417 authoritative). `tests_balance_negative` **26/26 PASS**. Contracts
`--only balance,souls,summons,resources` on the b93 build: **0 P0 / 1252 P1 / 3653 P2**; on the
pre-change baseline arz: **3 P0 / 1252 P1 / 3653 P2**. Violation-set diff: **2 keys only-in-baseline
(the BAL-DEATHXP P0s), 0 only-in-built, 4905 common - i.e. ZERO new violations of any severity.** The
1252 P1 are the known pre-existing `contracts_resources` set (BL-b90-DEBT-1), **count identical on both
arz**, so they are provably untouched by this lane.

**DEPLOY: NOT PERFORMED (BLOCKED, needs orchestrator sequencing).** At 13:29 the DEV entry held
`1c27d5fa` (the documented ground truth, and what this lane's baseline reproduces). At **13:55:19,
mid-build, a CONCURRENT lane deployed a different arz to the same DEV entry**:
`SoulvizierClassicDEV.arz` = **`5143ad1a44a9964c22578e00613f3e14`** (55,424,139 B). Record-diff of that
deployed arz vs this lane's baseline shows **12 records changed, all one field**: `mesh`
`Creatures\Monster\Skeleton\RevenantPoison.msh` -> `Creatures\Monster\Skeleton\Skeleton01.msh` on
`um_toxeus_enslaver_99`, `um_bloodtoxeus_99`, 4 Toxeus proxies and 6 Toxeus soul-pets (a Toxeus mesh
lane; `fix/green-diff` "b92 GREEN GLOW root cause: the mesh attaches the aura" is the likely owner).

That change is **entirely DISJOINT from this lane** (12 creature/pet/proxy `mesh` fields vs 1
gameengine record), so a merged build carries both cleanly. But this lane's arz was built from `main`
and does NOT contain it, so **copying `de589633` onto DEV would silently revert all 12 mesh fields** -
exactly the last-writer-wins clobber the b90 lesson and the standing code discipline forbid. **The
deploy was therefore deliberately NOT performed.** Backups of the pre-existing DEV state were taken
first: `local/db_backups/SoulvizierClassicDEV_pre-b93_1c27d5fa.arz` (which actually captured the
concurrent lane's `5143ad1a` - the filename records the intent, the hash records the truth) and
`local/db_backups/DEV_Text_pre-b93_fcca4927.arc`.

**REQUIRED NEXT STEP (orchestrator):** merge `feat/death-xp-penalty` with the Toxeus-mesh branch, run
ONE rebuild off the merged tree, and do ONE coupled arz+Text deploy. Do not hand-patch either
artifact. `Text.arc` needs no change either way (byte-identical). `Levels.arc`
(`943d0ab9516d332db79bd7f9fd2d3ffe`) and `Quests.arc` (`5e664c7b190965fd69f6ff15d77d85e4`) on DEV are
UNTOUCHED by this lane and were re-hashed after all work to prove it. **TQ.exe was RUNNING throughout
(started 13:31) and was NOT killed** (standing ban); Will must kill TQ + Steam and restart before any
test.

**LEDGER:** `docs/WILL_RULINGS.md` **R-80** appended VERBATIM in a new "Global balance & progression"
section (decade 70-79), status IMPLEMENTED b93, with the exact before/after values recorded.

**OPEN DEBT:** BL-b93-DEBT-1..5 (see DEBT REGISTER): in-game confirmation launch-gated; Steam/canonical
not shipped; **the DEV deploy is blocked on the concurrent-lane merge above**; SV's
`experienceLevelEquation` ships with an unbalanced parenthesis (inherited, untouched, affects only the
"% of a level" framing, not the XP-lost numbers); MULTIPLAYER_COMPAT.md quotes a stale build27 arz hash.
## BUILD59-DEV GATE RECORD - b98 THE ENDLESS HUNT (2026-07-28, branch `feat/endless-hunt`, tag `build59-dev`)

**NOT DEPLOYED.** Five content branches are staged for ONE merged deploy; this lane deliberately did
not write to `CustomMaps\SoulvizierClassicDEV`. Artifacts for the orchestrator's merged deploy:
- arz `.claude/worktrees/endless-hunt/work/SoulvizierClassic/Database/SoulvizierClassic.arz`
  md5 **c366b4108be547b4a4acb181d1b0675c** (51,104 records)
- Text `.claude/worktrees/endless-hunt/work/text/Text.arc` md5 **ce4653d30f304a88e837b20e166639fc**
  (COUPLED - the arz references the new `tagSVCwpnRunbreaker`; never ship one without the other)
- `Levels.arc` / `Quests.arc` **untouched** - this is a DB-only lane, zero map bytes.

Rulings implemented: **R-80** (endless pursuit, Legendary only), **R-81** (his soul at 100%),
**R-82** (the Rite of the Undivided drops off him too), **R-83** (Runbreaker, his spear),
**R-84** (a kit that is his own, not the Enslaver's), **R-85** (the Enslaver's persistent black
shroud). Full text in `docs/WILL_RULINGS.md` (Toxeus OVERFLOW decade 80-89, allocated by this lane);
full report in `docs/reports/b98_endless_hunt.md`.

**RECORD DIFF vs a freshly-built `main` (a0276ab) baseline, same env - INTENDED ONLY:**
15 ADDED / 0 REMOVED / 4 MODIFIED. Added: the endless controller + variant monster + Legendary pool
(R-80), `svc_{n,e,l}_runbreaker` + `runbreaker_guaranteed_{n,e,l}` (R-83), 4 pursuit-kit skills
(R-84), the shroud skill + its CharFxPak (R-85). Modified: `um_toxeus_hunt_99` (30 fields),
`um_toxeus_enslaver_99` (2 - the shroud in a FREE slot 19), the fixed proxy (5) and its pool
(1 - FileDescription).

**GATES (all green):**
- registry selfcheck OK, 39 modules; every module `verify()` hook green.
- `validate_tags` **PASS** (358 mod-owned tags all resolve, incl. the new `tagSVCwpnRunbreaker`).
- `verify_soul_drop_rates` **PASS** (incl. its own planted-regression negative test).
- contract suite **PASS, 0 P0 / 0 P1**, identical to the `main` baseline run under identical inputs
  (both 0/0, 4,759 P2). NOTE FOR FUTURE LANES: run the suite with `--resource-arc-dir` pointing at a
  Resources dir that actually holds the asset arcs and `--upstream-dir` at a populated upstream cache.
  Without them the suite reports 102 P0 / ~460 P1 on `main` ITSELF - pure environment artifacts
  (unresolvable meshes because no arcs were loaded, and severity demotion because the provenance
  source could not load).
- 3 NEW planted negative tests, 14/14 plants caught:
  `py tools/patches/toxeus_hunt_encounter.py --negtest` (5/5),
  `py tools/patches/toxeus_hunt_endless.py --negtest` (5/5),
  `py tools/patches/enslaver_shroud.py --negtest` (6/6).

**TWO WRONG CLAIMS IN THE SHIPPED DOCS, CORRECTED IN PLACE (retirement protocol - wording only, no
record renamed or deleted):**
1. The "Hades-only roaming Hunt" is a MYTH, and it came from ONE comment.
   `toxeus_suite.py`'s `_LS_ALLOW_PREFIX = ('records\\xpack\\proxieshades',)` was annotated "Hades
   trash pools ONLY". That namespace is the WHOLE Immortal Throne proxy tree - the base game filed
   RHODES inside it as area001. The sweep reaches 540 proxies across area001 Rhodes (70), area002
   Medea's Grove (76), area003 Epirus (55), area004 Styx (78), area005 Plains of Judgement (79),
   area006 Tower of Judgement (49), area007 Elysian Fields (82), area008 Hades Palace (49). 365 of
   them define ONLY `poolN` (which resolves on all three difficulties) and ZERO define
   `poolLegendaryN`. **Will meeting the roaming Hunt in Rhodes on Epic was never a defect.** What kept
   him invisible on Normal is RARITY: weight 1 against pool totals of 36,001-660,001, median about
   1 in 66,667. Corrected in `toxeus_suite.py` (docstring + the prefix comment + the sweep docstring),
   in `build_section_surgery.py`'s placement comment, and in R-16's successor entries.
2. `distressCallGroup='Skeleton'` on a Demon-race ShadowStalker is NOT a clone leftover. All 28
   shipped ShadowStalker-mesh monsters are race=Demon AND group 'Skeleton'; there is no 'Demon' group
   in the DB at all. Left alone, with the census recorded.

**DEBT REGISTER (nothing silently deferred):**
- `BL-b98-DEBT-1` LAUNCH-GATED, PLAYER SURFACE: Maenad-spear-on-SHADOWSTALKER has no shipped
  instance. Nobody has SEEN Runbreaker swing. Will's in-game look decides; ranked fallbacks
  MedusaMinion_Spear then Machae_Spear, each a one-constant edit.
- `BL-b98-DEBT-2` BLOCKED ON ANOTHER LANE + WILL: the Enslaver's shroud cannot be claimed to read
  black while `RevenantPoison.msh` emits a mesh-embedded GREEN aura at his waist (b92, proven from
  asset bytes, NOT deployed, reachable only from tag `build53-dev`). Also Will question 7: give each
  champion a DIFFERENT aura-free mesh so removing the green also separates them visually? Not built
  here - it is the green-diff lane's scope and this lane never touched that worktree.
- `BL-b98-DEBT-3` NEEDS WILL: at MaxPursuitDistance 1000 / PursuitTime 100000 the Legendary Hunt
  effectively cannot be outrun to a town portal. Confirm that is the intent.
- `BL-b98-DEBT-4` NEEDS WILL: should `toxeus_hunt_soul_l` become a reagent of the End of All Things
  formula (a 4th, or replacing the base Greece Toxeus's)? Do not promise a 4th slot before checking
  whether `ItemArtifactFormula.tpl` declares `reagent4`; the shipped record uses only 1/2/3.
- `BL-b98-DEBT-5` WILL-VETO (rate change, deliberately NOT taken): the ROAMING Hunt is about 1 in
  67,000 per spawn roll. R-18 forbids the equivalent change on the Enslaver, so this lane treated it
  the same way and changed nothing. Target needed if Will wants him findable: "once a playthrough",
  "once per act", or leave him a rumour.
- `BL-b98-DEBT-6` WILL-VETO (R-39 drop-slot precedent, deliberately NOT taken): the Hunt's Finger1 /
  Misc1 / Misc2 / Misc3 loot tables are all WIRED but sit at 0% equip chance, so his ring, potions,
  relic and amulet can never drop. Compare the Enslaver: Finger1 100 / Misc1 100 / Misc2 18 /
  Misc3 50. Proposal: open them to Enslaver-comparable rates so a Boss-class champion pays out.
- `BL-b98-DEBT-7` WILL-VETO (tuning): the spear ships FAST (`CharacterAttackSpeedAverage`, 0.25) to
  match his identity rather than the supra donor's Slow. Two values, vetoable in place.
- `BL-b98-DEBT-8` NEEDS WILL (balance): on Normal he is charLevel 40 with 16,000 HP at run speed 1.8
  in a Rhodes band that clamps the player to 29-33. The shipped Hades Marshal is charLevel 50 /
  26,000 HP at run 0.85. Scale him down for Normal, or is a brutal ambush the point?
- `BL-b98-DEBT-9` STRUCTURAL LIMIT, reported not fixed: the roaming spawns cannot be difficulty-split
  (ProxyPool has no `nameEpicN`/`nameLegendaryN`, and the 345 pools are native and shared), so the
  roaming Legendary Hunt is still kiteable. Only the fixed Hades Palace encounter is endless. The
  alternative (a parallel ~345-proxy Legendary set) is large and invasive and was not taken.
- `BL-b90-DEBT-4` **CLOSED** by R-81.

## BUILD51-DEV GATE RECORD - b91 deep-chest Devourer guard, the 100% spawn round 2 (2026-07-28, branch `fix/devourer-chest`, tag `build51-dev`)

**R-49, Will 2026-07-27, verbatim (REPEAT of R-3):** "toxeus the murderer devourer of blood is not
spawning at the proper location next to his chest in the blood cave even though we said he should
have a 100% spawn rate there in the existing spawn pool that is there"

DB-ONLY lane (arz + Text coupled pair). **NO map rebuild** - `Levels.arc` + `Quests.arc` byte-identical
before vs after. Full report: `docs/reports/b91_devourer_chest_spawn.md`.

**ROOT CAUSE:** b79 fixed a FIELD inside the wrong SHAPE. The chain was intact in the deployed bytes
(chest x1 + guard proxy x1 in `drxBC2`, 4.20u apart; `championMin=1` present), but the Devourer sat in
the pool's CHAMPION slot. Of 1,845 shipped ProxyPools, **624 guarantee a boss by putting him in a MAIN
`nameN` slot** (every guaranteed boss in the game and in this mod, incl. `_BT_POOL` for this exact
monster), while all **90 Boss-in-champion pools are the base-game rare uber-monster lottery** (73 at
`championMin=0`; the 17 with `championMin>=1` always list non-boss champions alongside).
`egg_blooddragon` was the **only pool in 51,085 records making a Boss the SOLE champion entry**.
Second defect on the same chain: the guard proxy still carried `difficultyLimitsFile=limit_area002`
(`N[23-26] E[38-51] L[60-65]`), below his `charLevel [40,68,100]` on every difficulty. **The repo's own
`_verify_mod_spawn_proxies_eligible` gate already forbids both** - the chest guard was simply never
registered in `_MOD_AUTHORED_SPAWN_PROXIES`, so the gate never looked at it.

**RECORDS TOUCHED (exactly 2 - record-diff vs the deployed `c1a8fa2a`: 0 added, 0 removed, 2 changed):**
- `records\drxmap\proxy\pools\egg_blooddragon.dbr` (11 fields): `name1/2/3` -> `um_bloodtoxeus_99`
  (MAIN), `nameChampion1/2/3` -> `blooddragon01` (escorts), `weightChampion2/3`=100,
  `championMin` 1->3, `championMax` 1->3, `FileDescription`. `spawnMin/Max`=4 and
  `proxyPoolEquation=''` untouched -> **exactly 1 Devourer + 3 blood dragons every run, 1..6P.**
- `records\drxmap\proxy\egg_blooddragon_pack.dbr` (1 field): `difficultyLimitsFile`
  `limit_area002` -> `limit_bloodtoxeus` (`[1..110]` N/E/L).

Scope proof: that proxy is placed EXACTLY ONCE map-wide and is the ONLY proxy referencing that pool,
so both edits touch this one encounter. The encounter Will designed is unchanged (same native proxy,
same spot, same roster); only which slot the Devourer occupies changed.

**GATE (no-new-surface law):** new **`MAP-CHESTGUARD-1`** (P0) in `tools/contracts/contracts_map.py`
asserts the WHOLE chain on the shipped artifacts - chest placed once, guard placed once in the same
level within 12u, proxy->pool1->monster resolve, Devourer is a weighted MAIN, guaranteed mains =
`spawnMax - championMax` == exactly 1 with `championChance>0`, equation neutralized, limit window
contains his charLevel on N/E/L. 7 planted negative tests (`_negtest_map.py::test_chest_guard`,
suite **43/43 PASS**), including the exact champion-only shape that shipped. **Real-world negative
proof:** the same contract run against the pre-b91 DEPLOYED artifacts exits 1 with
`MAP-CHESTGUARD-1` P0 + 3x P1; against the b91 build it PASSES. The chest guard is also now
registered in `_MOD_AUTHORED_SPAWN_PROXIES` (44, was 43).

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`):

| artifact | md5 |
|---|---|
| `work/.../Database/SoulvizierClassic.arz` NEW | `1c27d5fa650b5c076696db4ad379672f` |
| `work/.../Resources/Text.arc` (rebuilt from the BUILD-EMITTED manifest; bytes unchanged) | `fcca49277b9d31ed451e4a6843898843` |
| `work/.../Database/uber_soul_tags.txt` (build-emitted) | `49b6d85ba15236aa5df60f610e3a7bf0` |
| baseline arz (pre-change = what was deployed) | `c1a8fa2aee5e6eb88b641b28d7dc6ae4` |
| `work/.../Resources/Levels.arc` BEFORE == AFTER | `fc0adcc0713839a685b32d6e122653be` |
| `work/.../Resources/Quests.arc` BEFORE == AFTER | `5e664c7b190965fd69f6ff15d77d85e4` |

**GATES:** DB build **exit 0**, every fail-loud invariant green (spawn-eligibility **44 proxies OK**,
Part D champion cap **<= 1 Toxeus per pool at 1..6P**, soul-leak / soul-augment / supra-ref / tags /
A7 golden 84 waived 0 other / A9 render-chain / b77 unlock-alignment). `validate_tags` **PASS**
(356/356 referenced, 417/417 authoritative). `_negtest_map.py` **43/43 PASS**. Contracts `--only map`
on the b91 build + the DEV map: **GATE PASS** (0 P0 / 0 P1 / 3 pre-existing portal P2).

**DEPLOYED to DEV** (`CustomMaps\SoulvizierClassicDEV`), coupled arz + Text pair only; backups
`local/db_backups/SoulvizierClassicDEV_pre-b91_c1a8fa2a.arz` + `local/b91_work_arz_prev.arz`:
- `Database/SoulvizierClassicDEV.arz` = `1c27d5fa650b5c076696db4ad379672f` (**== built**)
- `Resources/Text.arc` = `fcca49277b9d31ed451e4a6843898843` (**== built**, bytes unchanged, verified in place)
- `Resources/Levels.arc` = `943d0ab9516d332db79bd7f9fd2d3ffe` (**UNTOUCHED**, still build49 TESTHUB)
- `Resources/Quests.arc` = `5e664c7b190965fd69f6ff15d77d85e4` (**UNTOUCHED**)

Deployed-arz re-probe confirms the whole chain. TQ was NOT running at deploy time.
**Will must kill TQ + Steam and restart before testing** - and see the SAVE note: a chest room already
visited on a given character+difficulty can keep its previously resolved group, so test on a
difficulty (or character) that has not cleared that room yet. Report section 6 has the discriminator.

**LEDGER:** `docs/WILL_RULINGS.md` **R-3 PENDING -> IMPLEMENTED b91** (cause corrected), **R-49**
appended verbatim. Parchment axis (R-1/R-2/R-13) untouched and verified un-regressed
(`q_bloodtoxeus_ambush` still placed once at `drxFirstxistion_connection` 4u from `finalletter`).

**OPEN DEBT:** BL-b91-DEBT-1..4 (in-game confirmation launch-gated; Steam/canonical not shipped; the
guard's blood dragons now scale on the `[1..110]` window; a sweep is owed for other native proxies
carrying mod-authored spawns that are still unregistered).

## b91 DEBT-CLEARANCE LANE (domain `db`, 2026-07-28, branch `fix/debt-db`) - 5 items CLOSED

DB-ONLY lane (arz + Text COUPLED PAIR - the new `tagSVCSummonEmberteeth` means the arz must never
ship without the new Text.arc). **NO map rebuild, NO deploy, NO Steam.** Full report:
`docs/reports/b91_debt_db.md`. Registry order hash
`2675f461554ec2593dc1f8588f22d8644cd68581bd6722bc999f8d1998b31b10` (35 modules).

**RECORD-DIFF vs the pre-change baseline: 4 added / 0 removed / 184 modified, intended-only.**
Seven changed field names in total: `particleEffectName2` x177 + `particleEffectName3` x176 (= the
353 filed slots), `itemSkillName`/`itemSkillLevel` x3 each (the Emberteeth soul tiers),
`chanceToEquipFinger2` x2 (`um_legion_28c` + `um_possessedboar_spirit`, 66 -> 50),
`skillName1` x1 (the BL-103 Emberteeth repoint), `bumpTexture` x1 (wep_spear, finishes F3). The 4
added records are the 3 Emberteeth pets + his summon skill.

**BASELINE PROVENANCE / DETERMINISM PROOF:** the lane's baseline arz, rebuilt from this worktree at
`main` @ `89d3e52` before any change, came out at md5 `c1a8fa2aee5e6eb88b641b28d7dc6ae4` -
**byte-identical to the arz b90 shipped**. The whole pipeline reproduces exactly, so every diff is
attributable to this lane alone.

**DETERMINISM:** two independent full builds -> byte-identical arz `22cf6b6e7acb940e5a4698d079ab1955`.

**GATES:** registry OK (35 modules) | B-SUMMON-1 summon-pet validator PASS | A7 golden PASS (84
waived) | A9 render chain PASS | b77 unlock-alignment PASS | F2 summons contract GATE PASS (0 P0 /
0 P1 / 112 P2) | `validate_tags` PASS (357/357 referenced, 418/418 authoritative) |
`verify_soul_drop_rates --gate` PASS incl. a NEW planted-regression test for the R-42 closure.

**CONTRACT DELTA (the strictly-negative gate B-FX-DANGLING-1 required):** identical command over the
baseline vs the built arz - souls 0/0/0 both; summons 0 P0 / 0 P1 / 112 P2 both; **resources
4794 -> 4618 (1252 P1 -> 1157 P1, 3542 P2 -> 3461 P2)**; total **4906 -> 4730 (-176)**.
**0 P0 in both and not a single violation class went UP.** The residual
`contracts_resources` FAIL is the pre-existing volume already filed as BL-b90-DEBT-1 - this lane
reduced it, it did not cause it.

| artifact | md5 |
|---|---|
| `work/.../Database/SoulvizierClassic.arz` NEW | `22cf6b6e7acb940e5a4698d079ab1955` |
| `work/.../Resources/Text.arc` NEW (carries `tagSVCSummonEmberteeth`) | `cec3194e615fa4fb00488203a901eff3` |
| `work/.../Database/uber_soul_tags.txt` (build-emitted) | `db91b80c6c6f656ed7cb015781a81b92` |
| baseline arz (pre-change; == the b90 shipped arz) | `c1a8fa2aee5e6eb88b641b28d7dc6ae4` |
| `Resources/Quests.arc` BEFORE == AFTER | `5e664c7b190965fd69f6ff15d77d85e4` |

| item | verdict |
|---|---|
| **B-FX-DANGLING-1** | **CLOSED - FIXED.** New module `tools/patches/fx_dangling_cleanup.py` strips the 353 dangling `Records\SandBox\Chris\UnarmedProjectile_FX01.dbr` `particleEffectName2/3` slots off 177 records (incl. the player Earth mastery `drxflamesurge`/`drxvolcanicorb`). STRIP not repoint, on proven **base-game absence parity**: of the 69 records that also exist in the stock TQAE DB, **69/69** have `particleEffectName2` ABSENT and **68/68** have `particleEffectName3` ABSENT (0 carry the ref, 0 carry anything else). The BACKLOG's paired "strip the orphaned `particleEffectAttachPoint2/3`" sub-item is **CLOSED as REJECTED-BY-EVIDENCE**: the same 69 base records carry those attach points PRESENT while the name slots are absent, so orphaned attach points ARE the vanilla shape (731 exist arz-wide, inherited from the base game) - stripping them would deviate from parity, not restore it. The `wep_spear.dbr` `bumpTexture` sub-item is **CLOSED - FIXED** (finishes build30 F3's DRX-skin strip). Also supersedes F7a, which the B-SOUL-PROC-2 `pcsafe` clone step was silently undoing every build (BL-103 fix-upstream). |
| **BLOODHOUND-DYINGFX** | **CLOSED - ALREADY RESOLVED, no change needed.** All 6 summoned-bloodhound bodies (`b_bloodhound_33/34/35`, `c_bloodhound_40/42/44`) already carry `dyingFxPak = records\drxcreatures\bloodhound\effects\fxpak_deathfx_burst.dbr` - exactly the repoint target the P0-block HYGIENE line names - and it resolves. **0 dangling `dyingFxPak` refs roster-wide.** Instead of a no-op fix the lane ships the invariant the debt never had: `fx_dangling_cleanup.verify()` fails the build loud if any `dyingFxPak` stops resolving. ⚠️ **TRAP RECORDED:** a mod-arz-ONLY scan reports **7 false positives** here (4 `boss_daemonbull_yaoguai_*`, 3 `crowheroes\zilla*`); all resolve in the base-game DB. Any dangling-ref audit MUST resolve against the UNION of the mod arz and `<TQAE>\Database\database.arz`. |
| **SOUL-EMBERTEETH-SUMMON** | **CLOSED - BUILT.** See the QUEUED FEATURE section below (updated in place). |
| **LEGION-TERMINAL-50 (R-42 fold-in)** | **CLOSED - FIXED UPSTREAM.** `build_svc_database.soul_spawn_provenance_sets()` now closes both membership sets forward over the `actorToSpawnOnDeath` graph, so a death-transform stage inherits its chain HEAD's spawn provenance instead of falling through `soul_drop_rate()`'s PLACED safe-default. Roster-wide simulation over all 51,085 records: **exactly 2 LIVE movers** - `um_legion_28c` and `um_possessedboar_spirit`, both terminals of RANDOM chains = precisely the ruled class (7 other verdicts move but are inert at `chanceToEquipFinger2 = 0`). PLACED-chain terminals correctly stay 66 (`um_charonform2_ferryman_99`, `um_polisgaoler_unbound_99`, `um_tantalus_unbound_99`) and the two R-48 100% carve-outs are untouched. |
| **BL-ENSLAVER-SPAWNS** | **CLOSED - all 3 sub-fixes were ALREADY SHIPPED; the entry was simply never updated.** See the entry below (updated in place). Two genuinely-missing gates were added. |

**OPEN DEBT:** BL-b91-DEBT-7..10 (see DEBT REGISTER; filed as 1..4, renumbered by the debt-wave integration).
## BUILD50-DEV GATE RECORD - b90 Toxeus champion souls -> 100% drop (2026-07-27, branch `feat/toxeus-souls-100`, tag `build50-dev`)

**R-48, Will 2026-07-27, verbatim:** "increase the drop rate for the souls of toxeus the murderer,
enslaver of souls and toxeus the murderer, devourer of blood to 100%"

DB-ONLY lane (arz + Text coupled pair). **NO map rebuild** - `Levels.arc` + `Quests.arc` byte-identical
before vs after. Full report: `docs/reports/b90_toxeus_souls_100pct.md`.

**RECORDS TOUCHED (exactly 2, one field each - record-diff vs `local/baseline_build47.arz`: 0 added,
0 removed, 2 changed):**
- `records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr` `chanceToEquipFinger2` **66.0 -> 100.0**
- `records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr` `chanceToEquipFinger2` **25.0 -> 100.0**

**IMPLEMENTATION:** new registry module `tools/patches/toxeus_souls_100.py`, registered LAST among
content modules (before `visuals`) so it is the ratified final registry writer of that field on the
two champions. Deterministic + idempotent; `apply()` carries a roster-wide SCOPE PROOF (fails loud
unless exactly those 2 of 3629 creature records moved); `verify()` re-asserts 100 on the FINAL merged
arz in `run_registry_verifies()` and fails the build loud otherwise. Holds under
`SVC_RELEASE_DROPS=1` (what ships) - it does NOT rely on `_force_100_pct_soul_drops` (testing-only).
The shared classifier `soul_drop_rate()` and the Hero/Boss/Quest gate in `wire_souls_to_monsters` are
**untouched** (yeti Common/Champion lesson respected; both champions are `Boss`). Gate ground-truth
updated in `tools/verify_soul_drop_rates.py` (`_KNOWN_EXCEPTIONS` + spot tests, both -> 100.0 with the
R-48 rationale). Registry order hash `9bca0f20fd87c7dade8562c27914f73372e38aab13cb4c08dd93fba44d5624fe`
(33 modules).

**LEDGER:** `docs/WILL_RULINGS.md` R-48 IMPLEMENTED b90; **R-42** ("random 50 / placed 66 / boss 25")
marked PARTIALLY SUPERSEDED for these two records only - every other rate proven unchanged.

**BUILD HASHES** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`):

| artifact | md5 |
|---|---|
| `work/.../Database/SoulvizierClassic.arz` NEW | `c1a8fa2aee5e6eb88b641b28d7dc6ae4` |
| `work/.../Resources/Text.arc` (rebuilt from the BUILD-EMITTED `uber_soul_tags.txt`; bytes unchanged, no tag changed) | `fcca49277b9d31ed451e4a6843898843` |
| `work/.../Database/uber_soul_tags.txt` (build-emitted) | `49b6d85ba15236aa5df60f610e3a7bf0` |
| baseline arz (pre-change, `local/baseline_build47.arz`) | `5a3c016baae8f136b8b801ea871b71ba` |
| `work/.../Resources/Levels.arc` BEFORE == AFTER | `17bed65ff9299a3398131025b4bfcfb3` |
| `work/.../Resources/Quests.arc` BEFORE == AFTER | `5e664c7b190965fd69f6ff15d77d85e4` |

**GATES:** DB build exit 0, every fail-loud invariant green (soul-leak / soul-augment / supra-ref /
tags / spawn-eligibility / A7 golden 84 waived 0 other / A9 render-chain / b77 unlock-alignment / F2
summons contract). `validate_tags` **PASS** (356/356 referenced, 417/417 authoritative).
`verify_soul_drop_rates --gate` **PASS** (exit 0; spot tests both champions arz=100.0;
intended-diff-vs-golden 380 deltas / 380 documented / **0 UNINTENDED**; testing-forcer survival 850
enabled -> 100, **428 gated stay 0**; planted-stomp negtest CAUGHT). Registry verify hook
**`toxeus_souls_100 verify OK`**. Contracts `--only souls,summons,resources`: souls **0 P0/0 P1/0 P2**,
summons **0 P0/0 P1**, resources 1252 P1 **PRE-EXISTING** (identical violation set on the pre-change
baseline arz: 4904 both, 0 only-in-built, 0 only-in-baseline) - see BL-b90-DEBT-1.

**DEPLOYED to DEV** (`CustomMaps\SoulvizierClassicDEV`), coupled arz + Text pair only; backup
`local/db_backups/SoulvizierClassicDEV_pre-b90_5a3c016b.arz`:
- `Database/SoulvizierClassicDEV.arz` = `c1a8fa2aee5e6eb88b641b28d7dc6ae4` (**== built**)
- `Resources/Text.arc` = `fcca49277b9d31ed451e4a6843898843` (**== built**)
- `Resources/Levels.arc` = `943d0ab9516d332db79bd7f9fd2d3ffe` (**UNTOUCHED**, still build49)
- `Resources/Quests.arc` = `5e664c7b190965fd69f6ff15d77d85e4` (**UNTOUCHED**)

Deployed-arz re-probe: both champions cls=Boss chance=**100.0** with their 3 soul tiers;
`um_enslaver_marauder_99` still 0.0. **Will must kill TQ + Steam and restart before testing.**

**OPEN DEBT:** BL-b90-DEBT-1..4 (see DEBT REGISTER).

## BUILD49 GATE RECORD - b89 ocean_extension05 crash hotfix (2026-07-27, branch `fix/ocean05-hotfix`, tag `build49-dev`)

**P0, Will: "this area is literally right in the beginning of this section of the blood cave, we have
to fix this bug to make the blood cave even playable."** Two independent Frida sessions
(`probe_20260727_155800.log`, `probe_20260727_155845.log`) died at the SAME chamber -
`ocean_extension05` (idx 2266, guid `e11908536840dc7e50d5a88221b17b22`), ENTER inside ProcessRLTD
with NO LEAVE - at 5-loads-in-6s and at 11-loads-over-4min, with 10 vs 9 co-resident. Different pace,
different residency, same chamber: it is the section, not memory pressure.

**ROOT DEFECT:** its `0x0b` was the dead Approach-22 **148-byte stub**
(`build_section_surgery.build_minimal_rec02`, injected by `svaera_plus_portals` step 7b tier-3).
The stub was written against a WRONG format model - it read `+12` as `diff_count = 3
(Normal/Epic/Legendary)` when `+12` is `guid_count`, and it emitted ONE **44-byte** parameter block
(missing `maxTiles`+`maxObstacles`, which make `dtTileCacheParams` 52 B) + 4 stray zero uint32s
instead of the **three complete 56-byte tilesets** the engine parses. Consequences:
(1) a DEGENERATE GUID list `[own, own, own]` - the exact `deps` the probe printed;
(2) after consuming "set 1" the parser sits **4 bytes from the end of a 148-byte section** and still
needs sets 2 and 3, so it reads them out of the heap - garbage `numTiles`, then a tile loop walking
arbitrary `dataSize`. That is the ENTER-with-no-LEAVE.
"Cut" bought nothing: the engine streams by grid proximity and `ocean_extension05`'s 240x240 box
abuts `drxBC3`/`ocean_extension02`/`ocean_extension03`; the probe shows 01, 02, 03 streaming cleanly
immediately before 05 detonates.
**WHY EVERY GATE MISSED IT:** the stub's HEADER is impeccable (version 1, `payload_size` 136 == 148-12,
`guid_count` 3 in range, all GUIDs resolve - they are the level's own). `MAP-NAV-1` only parsed the
header; `verify_merged_bc_navmeshes` only compared SIZES and printed `ok ocean-stub`; `is_cut()`
exempted `ocean_extension*` from `MAP-NAV-3` anyway. Nothing had ever walked a container BODY.

**SWEEP (`tools/audit_navmesh_guid_lists.py`, new):** stock TQAE `Levels.arc` = 2235 levels,
**0 structurally invalid, 0 degenerate**, 251 own-only, 21 with NO `0x0b`. Our maps (deployed DEV,
canonical, TESTHUB - all three) = **8 structurally invalid == 8 degenerate**, and they are exactly
the 8 tier-3 (no-`0x0a`-geometry) levels: `ocean_extension05`, `ocean_extensionx01`, `x03`, `x04`,
`x05`, `x06`, `x07`, and **`coldtombs`** (Egypt/MiniDungeons - the same landmine parked elsewhere).
Will would have hit the next one minutes later. **ALL 8 FIXED.**

**CALL ON own-only (build47/48 fix A):** NOT the same defect class, left untouched. Stock ships
**251** own-only lists (`Crypt01`, `SlavePits`, `SerketCaves01`, `DevMaze01..14`, ...) - it is the
normal form for a self-contained interior - and `new_secretdoor_transitionhallway` (gc=1 since
build48, 157,898 B, 3 complete tilesets) ENTERs and LEAVEs cleanly (`al=1`) in probe session B.
`MAP-NAV-6` fires on SELF-DUPLICATION only and its negative test asserts silence on own-only.

**FIX CHOSEN = (c)** - emit what the engine actually parses. `build_minimal_rec02` now produces a
**structurally valid EMPTY** container: **224 B** = 16 hdr + 1x16 GUID (own, once) + 24 center/dims +
**3 complete tilesets** (52 B `dtTileCacheParams` + `int32 numTiles = 0`), `maxTiles = 2 *
ceil(2*dims_x/12.8) * ceil(2*dims_z/12.8)`, `maxObstacles = 128`; center/dims UNCHANGED so the
positioning gate is untouched. Every choice is copied from stock, not invented: stock ships **60**
all-sets-`numTiles==0` levels (240..304 B == `208 + 16*guid_count`, always 3 tilesets); the
`maxTiles` formula reproduces `Rhodes_OceanBorder_01`'s shipped 338 exactly; 166 stock meshes list an
empty-navmesh level as a neighbour. Option (b) "don't stream it" was RULED OUT (grid-proximity
streaming + Will is standing there + `ocean_extension01/02/03/04` and `x02/x08` carry REAL navmeshes
and are area-owners inside `drxBC3`/`drxBC_Finale`'s lists, so the family is NOT uniformly cut).
Pipeline-level (BL-103), deterministic, no hand-patched arc.

**NEW GATE (fails the build):**
- `MAP-NAV-5` (P0) - `0x0b` body must be exactly 3 complete tilesets, every tile record carrying the
  `RLTD` header magic, section ending cleanly. Backed by new `contracts_map.rec02_structure`.
- `MAP-NAV-6` (P0) - GUID list must not be self-duplicated.
Both apply to EVERY level including declared-cut ones. Neither whitelisted.
`verify_merged_bc_navmeshes` now walks structure (not just sizes), expects the 224-B container, and
FAILS instead of printing `?` on a wrong-size ocean section.
**PLANTED NEGATIVE TEST:** `_negtest_map.py` reconstructs the real 148-byte stub byte-for-byte
(`make_b89_stub`) and asserts it trips BOTH new gates at P0 **and** passes every pre-existing
`MAP-NAV-1` header check (the regression-proof that the old gates were blind), plus 2-/4-tileset,
trailing-junk, lying-`numTiles`, distinct-multi-GUID and own-only cases. Also repaired the harness
itself: `test_doors` pointed at a deleted session scratchpad path, so the whole file crashed for
everyone; it now resolves a live `Quests.arc` (or `SVC_QUESTS_ARC`) and skips loudly.

**PIPELINE UNBLOCK:** `svaera_plus_portals.main` + `gen_bc_navmeshes` had the two merge inputs
hard-coded to `reference_mods/` + `upstream/`; both caches were ABSENT on this machine, so the map
could not be rebuilt at all (bare `FileNotFoundError` deep in `ArcArchive`). Both now honour
`SVC_SVAERA_ARC` / `SVC_SV_ARC` (defaults unchanged) and fail loud naming the variable. SVAERA base
found at Steam Workshop item `2076433374`.

**PROOFS (all green):**
- **Donor reproduction:** all 39 `.0b.bin` regenerated at HEAD (`--cluster all`) come out
  byte-size-identical to the deployed build48 map's `0x0b` sections, incl. `new_secretdoor` 157,898 B
  (`COLLAPSED gc=3->1`). So the rebuild reproduces build48 and any map delta is this fix.
- **Blob-diff, new TESTHUB vs DEPLOYED build48 (`c1e814e4`): EXACTLY 8 level blobs changed**
  (`EXPECT-SET MATCH`), each `0x0b 148->224`, `struct TRUNCATED->OK`, `gc=3 distinct=1 -> gc=1`.
  `DATA` `+608` B exactly (8 x 76, the predicted delta); `LEVELS` same size (pure offset cascade);
  **QUESTS byte-identical**, as are GROUPS/SD/BITMAPS/DATA2/0x10.
- `verify_merged_bc_navmeshes`: **24/24 real (bytes+center) + 7 `ok ocean empty-container (valid)`**
  on BOTH variants, exit 0.
- `audit_navmesh_guid_lists` both variants: **0 structurally invalid / 0 degenerate / 0 unresolvable**;
  own-only 260 -> 268.
- Full map battery `--only map` BOTH variants: **GATE PASS (0 P0 / 0 P1)**; only the 3 pre-existing
  base-game P2 portal-noise items (XPack4 Dunes + Styx) build48 also had.
- **END-TO-END GATE PROOF:** the same battery against the CURRENTLY DEPLOYED (broken) map **FAILS**
  with **16 P0 = MAP-NAV-5 x8 + MAP-NAV-6 x8**, exit 1.
- `MAP-NAV-4` negtest PASS; on both rebuilt variants it flags **exactly the 2 whitelisted debt
  chambers** (`drxBC3`, `RogueEncampment`) - unchanged vs build48, no regression.
- `_negtest_map.py` **38/38 PASS**.
- **HASHES:** canonical `Levels_merged.arc` md5 `fc0adcc0713839a685b32d6e122653be` (688,691,547 B);
  TESTHUB `Levels_merged_TESTHUB.arc` md5 `943d0ab9516d332db79bd7f9fd2d3ffe` (688,679,840 B).
  Rollback copy of the live build48 DEV map: `local/build_b89/DEV_Levels_deployed_prev.arc`
  (`c1e814e4...`, 688,679,775 B).
**DEPLOY:** Will's **TQ.exe (pid 30076) was RUNNING** and holding `SoulvizierClassicDEV/Resources/
Levels.arc` exclusively open, and killing his game is never an option - so the copy could not land
in-session. Armed instead via the new `scripts/deploy_dev_levels.ps1 -WaitForTQ`: waits for TQ to
exit, re-checks after a settle (returns to waiting if the game reappears), copies to a temp IN the
target dir, md5-verifies it, then atomically replaces - an interrupted run can never leave a
half-written map - then verifies deployed==built and re-hashes siblings. DEV siblings before (this
lane changes none): arz `5a3c016b`, Text `fcca4927`, Quests `5e664c7b`. **NO Steam packaging**
(walk-test-gated; canonical carries the same defect - BL-b89-DEBT-2).
**REPORT:** `docs/reports/b89_ocean_ext05_hotfix.md`. Walk test: `docs/WILL_TEST_GUIDE.md` top section.

## B87 FIX A round 1 SHIPPED-TO-DEV (2026-07-17, branch `fix/navok-mapfix`, tag `build48-dev`)
**Fix A (single-own-GUID) implemented in the PIPELINE for `new_secretdoor_transitionhallway` ONLY
this round (one variable for Will's walk test).** Fix-upstream (BL-103): `gen_bc_navmeshes.py` gains
a per-cluster `own_guid_only_keys` config; the blood-cave cluster lists `new_secretdoor`. The FULL
multi-GUID donor is generated + self-verified UNCHANGED (identical geometry/carve/cross-tag), then its
GUID list is collapsed to `[own 415c9c33]` and every walkable cell retagged to own (area 1). Only the
container GUID list + the tile `areas` plane change; heights + cons are carried byte-for-byte and the
walkable footprint (incl. the 63-127u seam overlap) is preserved, so it loads in isolation (own GUID
always resident) - no navOK=0 null-deref. Every rebuild reproduces it; NOT a hand-patched arc.
**PROOFS (all green):**
- Donor blob-diff vs build47 donors: EXACTLY `new_secretdoor` differs (158011->157898 B); gc 3->1;
  heights+cons byte-identical across all 192 tiles; unwalkable-cell count identical; 103332 seam cells
  retagged own; walkable total preserved (479328==479328).
- Canonical + TESTHUB rebuilt to scratch. Section-diff vs build47 (both variants): DATA differs by
  exactly -113 B, LEVELS is a pure offset cascade (0 metadata/GUID/corner changes, 24 data_offset
  pointers shifted -113 from idx 2258), and QUESTS/GROUPS/SD/BITMAPS/DATA2/0x10 all BYTE-IDENTICAL;
  exactly ONE level blob differs = `new_secretdoor` in each variant.
- `verify_merged_bc_navmeshes` 24/24 on BOTH variants (count unchanged - new_secretdoor still has a
  donor, now single-GUID).
- `MAP-NAV-4` standalone gate + negtest: PASS; on the fixed map it now checks 4 SV-custom respawn
  chambers and flags **exactly 2** (`drxBC3` gc=6, `RogueEncampment` gc=3) - `new_secretdoor` CLEARS.
- Full map battery `--only map` on BOTH variants: GATE PASS (0 P0 / 0 P1; 3 pre-existing base-game P2
  portal-noise only - XPack4 Dunes + Styx). Whitelist shrinks to the 2 remaining debt chambers.
- **DEPLOYED to DEV** (`SoulvizierClassicDEV/Resources/Levels.arc` = the TESTHUB variant,
  md5 `c1e814e499fafcf02725549f918fa89b`, == built artifact); arz/Text/Quests md5 IDENTICAL
  before+after (arz `5a3c016b`, Text `fcca4927`, Quests `5e664c7b`). NO Steam packaging (walk-test-gated).
- **HASHES:** canonical `Levels_merged.arc` md5 `0be919da2a0aae17ec6186405384ff43` (688,691,589 B);
  TESTHUB `Levels_merged_TESTHUB.arc` md5 `c1e814e499fafcf02725549f918fa89b` (688,679,775 B);
  fix-A donor `new_secretdoor_transitionhallway.lvl.0b.bin` 157898 B (build47 donor was 158011 B,
  md5 `c4cc1e6e`).
**REMAINING DEBT (still whitelisted):** `drxBC3` + `RogueEncampment` - extend fix A to each only after
Will confirms new_secretdoor's walk test (crash gone AND west/east seams still walk). If A walls a
seam, escalate that chamber to option C (interior portals). Walk steps: `docs/WILL_TEST_GUIDE.md`
BLOOD-CAVE CRASH section. Report: `docs/reports/b87_bloodcave_navok_rca.md` sec 10 (fix-A addendum).

## B87 BLOOD-CAVE CRASH - RCA PROVEN via runtime probe (2026-07-17), branch `fix/bloodcave-navok`
**The 2026-07-17 Frida probe caught the crash LIVE and pinned it.** Crash chamber =
`new_secretdoor_transitionhallway` (idx 2257), the MID-CAVE respawn fountain
`respawn_hadescave01` - NOT the first-interior chambers b86 guessed (b86 picked the wrong
fountain; corrected in both docs). MECHANISM (proven on the binaries,
`docs/reports/b87_bloodcave_navok_rca.md`): the chamber's 3-GUID grid-seam navmesh
(own + drxbc_finale_transitionconnector + temple_entrance_clean, ALL resolving in BOTH variants,
all live reciprocal seams) fails ProcessRLTD's LIVE-residency gate (`Engine 0x101f4ba0`:
`[reg+0x50][idx]` must be a stream-RESIDENT region, not merely resolve in the GUID map) when the
chamber loads in ISOLATION - a save-load / death-respawn at the fountain instantiates only the
current level before its grid neighbours stream. navmesh load fails (navOK=0); the region code
null-derefs the absent navmesh (native dump EIP Engine RVA `0x20e270`, EDI=0). The Blood Cult
Disciple kill is the incidental query trigger (DEEP_DUMP proved the arz mitigation was a no-op =
map-side). The probe's `08c4c32f` GATE guid is a red herring (a `Level+0x14` field, not a navmesh
dep). MAP-NAV-1 (static GUID resolution) is correctly GREEN - this is the RESIDENCY half it cannot
see. STEAM AFFECTED (canonical == TESTHUB, byte-identical). Works everywhere else because the
design is deliberately multi-GUID + grid-stream co-residency (proven-walkable R09 entrance is
itself multi-GUID); it breaks ONLY at a respawn/save chamber that loads in isolation.
GATE SHIPPED (round 2, provenance-scoped): `MAP-NAV-4` (`tools/contracts/gate_navmesh_coresidency.py`
+ `contract_navmesh_coresidency` in the battery, both via ONE shared classifier
`contracts_map.scan_isolated_load_risk` so gate/battery can't drift). Invariant: every SV-CUSTOM
level (own GUID ABSENT from stock TQAE Levels.arc) hosting a `StrategicMovementRespawnShrine` must
have a single-own-GUID navmesh. Provenance is the true, name-free discriminator: it EXCLUDES all
264 base/IT/XPack respawn+multi-GUID chambers (region-packed, ship-and-work - so "respawn +
multiGUID" is NOT the crash law) including the byte-identical Silk Road `HiddenValley01` spawn hub.
Planted negtest (SV respawn+multiGUID FLAG, SV respawn+singleGUID CLEAR, no-shrine CLEAR, and
BASE respawn+multiGUID CLEAR = the false-positive control). Flags **exactly THREE** SV-custom
chambers on BOTH variants: `new_secretdoor` (gc=3), `drxBC3` (gc=6), `RogueEncampment` (gc=3).
The real map battery (`py tools/contracts/run_contracts.py --only map`) runs GREEN on both variants.
> ROUND-1 DEFECT FIXED: round 1 reused the BROAD b82 `BLOODCAVE_SUBSTRINGS` in the battery while
> the standalone gate used a narrow pair, so the battery flagged 4 chambers (adding the base-game
> `HiddenValley01` false positive + the un-whitelisted `RogueEncampment`) and turned the map battery
> RED on both variants - contradicting the round-1 "flags exactly 2 / battery green" claim.
**FIX = WILL DECISION + WALK TEST (map-structural, not blind-shipped):** the map-levers all trade
crash-safety against seam walkability and the repo law requires a walk test for navmesh/streaming
changes. Ranked: (A) single-own-GUID the respawn chambers (cheapest; RISK = the documented
invisible-wall failure mode, mitigated by 63-127u seam overlap + unchanged neighbour meshes;
DEV-walk-testable); (B) relocate the whole cluster to XZ-disjoint space (heavy, base-game-shaped);
(C) interior GridEntrance portals (`inject_interior_portals.py`); (D) move the respawn shrine.
Recommend building A for `new_secretdoor` on a DEV map for Will to walk-test (crash gone? seams
still walk?), extend to `drxBC3` + `RogueEncampment` if clean, escalate to C if A walls.
**DEBT (registered, whitelisted in `whitelist_map.txt` until each fix lands):**
`MAP-NAV-4 new_secretdoor_transitionhallway` (P0, the proven crash), `MAP-NAV-4 drxBC3` (P0,
same-class latent, respawn_hades_shrine01), and `MAP-NAV-4 XPack\Levels\Secret_Place\RogueEncampment.lvl`
(P0, same-class latent, respawntempleorient01, Secret Place / Duister; SECRET_PLACE navmesh cluster,
Duister reachable via wired rift return). REMOVE each whitelist entry when its sec-6 fix ships +
Will confirms the walk test.

## b86 BLOOD-CAVE CRASH BISECT (2026-07-17) - SUPERSEDED by B87 runtime capture (wrong fountain)
Will named the chamber: "the area immediately after the first respawn fountain inside the blood
cave, right behind the first door you open." Mapped it (docs/reports/b86_bloodcave_bisect.md): the
cave-entry streaming chain past the HiddenValley01 camp fountain + SilkRdDngEntrance mouth =
Random09A -> xPassageTransitionStart -> BC_initialpathway -> drxFirstRoom (drxFirstxistion_connection
co-resident). BISECT RESULT: those crash chambers are BYTE-FROZEN build25 (Jul 7) -> build47 (live)
while crash dumps span 07-05 -> build36 -> build41; every navmesh neighbor GUID resolves; the b46
minimap-wave hypothesis is REFUTED 3 ways (timeline predates b46 by a week; b46 zone/0x17 tables
contain ZERO blood-cave levels; chamber bytes identical across the b46 boundary). H1 (co-residency)
XZ-overlap fingerprint tested + RULED OUT vs base game (314/314 base cave pairs overlap identically).
STEAM AFFECTED (canonical == TESTHUB for the crash chambers) = P0 public. NO speculative fix shipped;
RESIDUAL = the Frida/Page-Heap probe (docs/crash/WILL_CRASH_PROBE_GUIDE.md) aimed at the named chain.
GATE added: MAP-ZONE-1 (every b46 zone-override dbr resolves) green + planted negative test.
b79 note: the relocated 33% Blood-Toxeus encounter (drxFirstxistion_connection @36,10,19.5) sits in
the crash chain but is NOT implicated (crash predates b79; DB spawn doesn't touch navmesh); it rides
along automatically when the structural cluster-relocation fix lands.

## DEBT REGISTER (open deferred/unproven/launch-gated items)

> Compiled by the b84 rulings-backfill sweep (round 1, 2026-07-16) of docs/reports/*.md, this file,
> WILL_TEST_GUIDE*.md, HANDOFF*.md, MULTIPLAYER_COMPAT.md, and CHANGELOG.md. One line each: item -
> source - owner/trigger. Verified against later reports where possible; items with no later
> resolution found are listed as OPEN. UNKNOWN-STATUS noted where the sweep could not confirm either
> way. Cross-reference docs/WILL_RULINGS.md for the ruling each item traces back to (R-numbers below).
> Do not silently drop an item off this list without checking it actually shipped (RETIREMENT
> PROTOCOL, CLAUDE.md law #2).

> 🧹 **2026-07-28 DOCS DEBT-CLEARANCE PASS (`fix/debt-docs`).** Six deferred items closed; the four
> that changed this register are marked inline below. Also in that pass, and recorded here because
> they change what a fix lane should trust:
> - **The BUILD31/BUILD32 TRAIN + STANDING PENDING WORK section is now headed by a STATUS SWEEP
>   table** (DOCBOARD-STALE-QUEUES). That whole queue read as unbuilt and was almost entirely
>   SHIPPED (build31/31g/32/32a/36) - every item re-probed against the shipped arz at VALUE level,
>   not report level. Only two things out of that queue are genuinely open: the boss-summon-soul
>   CANDIDATE list (a proposal awaiting Will's batch approval) and in-game re-verification of the Q4
>   dead-content one-liners. Read the table before scheduling anything from that section.
> - **`docs/WILL_RULINGS.md` had a ledger-hygiene pass:** 2 colliding R-numbers renumbered
>   (backfill R-13 -> R-19, backfill R-43 -> **R-70** in the new Souls overflow decade 70-79 - R-49
>   was already claimed by the parallel `fix/devourer-chest` lane on 2026-07-27), 6 stale PENDING
>   statuses flipped to IMPLEMENTED against the BUILD47 merge, and the remaining PENDINGs re-verified
>   and annotated. Nothing deleted.
> - **`contracts_map.CUT_LEVEL_MARKERS` -> `CUT_LEVELS`** (BL-b89-DEBT-3): the cut exemption is now
>   an exact-basename list of 8 levels instead of a substring tuple that swallowed 14.
> - **A duplicate debt id was resolved:** the second `BL-b89-DEBT-4` is now `BL-b89-DEBT-5`.

**b99 content integration wave (2026-07-29, build62-dev) - NEW**
- **BL-b99-DEBT-1 (P1, MERGE ORDER - owner: orchestrator):** `feat/leinth-wave` b94 is no longer on
  DEV (13 records + 75 field deltas, listed above). It is intact on the branch and in
  `local/db_backups/SoulvizierClassicDEV_pre-b99_9f98e3e8.arz`. Trigger: merge `feat/leinth-wave`
  into content-wave round 2 and rebuild once. Do **not** hand-patch.
- **BL-b99-DEBT-2 (P2, launch-gated):** none of the four lanes is IN-GAME confirmed on this merged
  build - the -90% death penalty, Sargoth's summon button, Vashkarr's retuned tooltip/movement, and
  the 22 detached drops. Owner/trigger: Will, after a full TQ + Steam restart, on freshly dropped souls.
- **BL-b99-DEBT-3 (P2, tooling debt, PRE-EXISTING):** `contracts_resources._BASELINE` hardcodes an
  absolute path into a **dead session scratchpad** (`.../55f6c1cb-.../scratchpad/contracts_baseline`),
  byte-identical on `main`. `tests_resources_negative` and `tests_summons_negative` therefore cannot
  run out of the box; both were run here through a harness that rebinds the constant. Owner/trigger:
  a tooling lane - make it an env var with a repo-relative default.
- **BL-b99-DEBT-4 (P2, PRE-EXISTING):** `tests_summons_negative` `SUMMON-PET-NAKED` and
  `MONSTER-SPAWN-ELIGIBILITY` report `FAIL(no real fire)` on **both** this build and the `main`
  baseline. The planted breaks no longer provoke their contracts. Owner/trigger: the summons contract
  owner - re-arm both planted negatives.
- **BL-b99-DEBT-5 (P2, tag hygiene):** `build60-dev`/`build61-dev` were taken by `feat/endless-hunt`
  while this wave was briefed for `build60-dev`; this wave shipped as `build62-dev`. Owner/trigger:
  whoever allocates build tags - the numbers are being claimed by parallel lanes without a registry.

**b97 soul-vs-monster identity audit (2026-07-28, build59-dev round 2) - NEW**
- **BL-b97-DEBT-1 (WILL DECISION, content):** the **22** detached creatures now drop **no soul at
  all** (Fesil the Quick, Sinnet Patchfur, Blood-Eyes, Errak Bonecarver, Sartt Soulrender, Korat
  Bearkin, Raghd Bloatworm, Prince Ch'kik't, Wahr'Ner Shadowpaw, Nazur the Shrouded, Masai-yin the
  Grovekeeper, Xuannu the Twilight Matron, Morbi, Mormo, Daechalcos, Thelxiepeia Venomlip, Colossal
  Scorpion, **Akara**, **Nenea Sharpclaw x3**). No soul was INVENTED for them - new content is a
  design call under the amgoz1 creative bar. Two are **Boss**-classified and most likely to be
  missed: **Xuannu the Twilight Matron** and **Blood-Eyes**. Owner/trigger: Will approves bespoke
  souls (or accepts them soulless).
- **BL-b97-DEBT-7 (ROUND 2, WILL DECISION, content):** zeroing **Akara** leaves our bespoke
  `records\item\equipmentring\soul\svc_uber\kallixenia_soul_{n,e,l}.dbr` (3-tier lich-queen caster
  soul: `lichequeen_soulstrike` proc + Death Chill/Ternion augments) with **no live carrier**, i.e.
  currently unobtainable. Nothing deleted - item records + loot ref intact (retirement protocol) and
  carried as the only entry in `soul_identity._ACCEPTED_ITEM_DETACH`; the *name* stays obtainable
  from the real Kallixenia. **(a)** leave it *(shipped)*; **(b)** set `01_akara.dbr`'s `description`
  to `xtagxQuestMonster01` so Akara IS Kallixenia (one field; the sibling decoration `x01_akara.dbr`
  already uses that tag, and `_create_kallixenia_soul`'s own docstring intends it) - cost: two
  creatures and two rings share one name; **(c)** author Akara his own soul and re-point the
  lich-queen soul. Owner/trigger: Will.
- **BL-b97-DEBT-8 (ROUND 2, P2, text/design):** three soul NAMES are each carried by **two distinct
  item families** - `{^F}Charon Soul` (`charon\charon` + `svc_uber\boss_charon`),
  `{^F}General Yrrt'ik Soul` (`formicid\generalyrrtik` + `svc_uber\rainbowbright`),
  `{^F}Plague Feast Soul` (`carrionbird\plaguefeast` + `svc_uber\nomnom`). Not identity theft (every
  carrier owns its name) so the gate leaves them alone, but the player sees two different rings with
  the same name. Owner/trigger: the naming lane.
- **BL-b97-DEBT-9 (ROUND 2, P2, data hygiene):** amgoz Dropbox conflict-copy creatures ship with LIVE
  66% soul drops and are counted in the by-design buckets (`copy of am_hero_29.dbr`,
  `um_speckledjim_45 (pcos modstridende kopi 2014-09-10).dbr`, `um_cyniga_17 (pcos ...)`,
  `um_liophotia_18 (pcos ...)`, `boss_gorgon_sstheno_22 (amgoz-qosmio's conflicted copy ...)`). One of
  them is half the reason Speckled Jim reads as a 2-row family. Owner/trigger: data-hygiene lane.
- **BL-b97-DEBT-10 (ROUND 2, P2, gate scope):** `tools/verify_soul_drop_rates.py::_is_creature` still
  has the `\creature(s)\`-only scope hole that b97r2 closed in the identity gate, so every
  `records\drxcreatures\` boss, `records\test\` and `soul\test\` monster is outside its roster (which
  is why the round-2 zeroes needed no new `_KNOWN_EXCEPTIONS` waivers). Widening it pulls every
  drxcreatures boss into the RANDOM/PLACED/BOSS classifier - its own wave. Owner/trigger: next
  drop-rate pass.
- **BL-b97-DEBT-11 (ROUND 2, P2, tooling):** `tools/audit_soul_identity.py` resolves SV's
  `Text_EN.arc` with a best-effort probe over several possible `check_build_inputs` function names,
  because that resolver exposes no stable public API. Give it a documented `resolve(name)` entry
  point and delete the probe. Owner/trigger: build-tooling lane.
- **BL-b97-DEBT-2 (P2, upstream):** `wire_souls_to_monsters`'s NEW-wire matcher still keys on the
  .dbr FILENAME. The b97 gate catches the consequence roster-wide, but the matcher itself is
  unchanged - fixing it would move records the F1 gate currently blesses and is its own wave.
  Owner/trigger: the next souls pass.
- **BL-b97-DEBT-3 (WILL DECISION, retirement protocol):** the Iron Lore **zzdev dev-dummy** creatures
  (`xpack\creatures\monster\zzdev\z_{arthur,ben,chooch,cory,dave,david,frazier,josh,morgan,nate,
  parnell,scott,shawn,tom,~v~}`) are Quest-classified at **66% soul drop**, and the build authored
  real soul items for three (`soul\svc_uber\z_ben_soul_{n,e,l}`, `z_tom_soul_{n,e,l}`, a `~V~` soul).
  They are identity-CORRECT so the gate does not touch them, and they are almost certainly
  unreachable - but "Ben Soul" ships in the roster. Zeroing the drops and/or retiring the items are
  both retirement-protocol calls (WILL-VETO by default) and the souls may sit in `svc_uber` formula
  chains. Recommend: zero the zzdev drops, leave the items. Owner/trigger: Will.
- **BL-b97-DEBT-4 (WILL DECISION, text-only):** NAME-DRIFT renames - cheapest real win is the
  **misspelling** `"The Etheral One Soul"` -> "The Ethereal One Soul"; also Crowboar -> Clazomenaeus,
  Grimshell -> Shriekbrood, Spinebone -> Skull Spine, Vilerotter -> Vile Crawl. Owner/trigger: Will
  picks (or "typos only").
- **BL-b97-DEBT-5 (P3, process):** the WILL_RULINGS **Souls decade (40-49) is EXHAUSTED** (R-49 went
  to b91), so this wave's ruling is filed as **R-49a**. The next soul ruling should continue the
  letter series or be allocated a fresh decade. Owner/trigger: whoever files the next soul ruling.
- **BL-b97-DEBT-6 (environment, not this lane):** the A9 render-chain gate SKIPS unless a populated
  `Resources/` sits beside the build output; a scratchpad build with an EMPTY `Resources/` makes it
  FAIL with ~197 bogus "unrenderable" refs. b97 ran it standalone against the real resource arcs on
  BOTH the baseline and the fixed arz: **PASS / PASS, 22 upstream WARNs each, identical**.
  Owner/trigger: consider making the gate distinguish "no Resources dir" from "empty Resources dir".

**b96 Vashkarr spear-and-shield soul retune (2026-07-28, build57-dev, R-72) - NEW**
- **BL-b96-DEBT-1 (P2, launch-gated):** the retune is **not in-game confirmed**. Only Will can see
  the tooltip and feel the movement change. Per the standing save lesson, TQ bakes item properties
  at pickup, so an already-held Vashkarr soul will NOT reflect this: **he must test on a FRESHLY
  dropped soul** (kill `um_vashkarr_99` again, 66% drop). Owner/trigger: Will's next test pass, after
  the orchestrator's merged deploy and a full TQ + Steam restart.
- **BL-b96-DEBT-2 (P2, unproven engine behaviour):** `offensiveElementalModifier` with a NEGATIVE
  value is carried by exactly **one** shipped item in the whole 51,085-record database
  (`u_n_ringofzakalwe`, -25.0). The field is unquestionably live (193 non-zero records, 114 items
  positive), but that a negative composite elemental modifier renders and applies as "-X% Elemental
  Damage" rather than being clamped at 0 is **inferred from the donor, not observed in game**. If
  Will's tooltip does not show the penalty, the fallback is per-element negative `offensiveFireModifier`
  (precedent: `ikaie_soul`, `coldtusk_soul`) at the cost of covering only fire. Owner/trigger: same
  test pass as DEBT-1.
- **BL-b96-DEBT-3 (P2, unproven semantics):** `offensivePierceRatioModifier` is asserted here to be
  the armour-bypass PENETRATION stat (rather than a second flavour of pierce damage). This follows
  Will's own named donor and 46 shipped souls, but the split between it and `offensivePierceModifier`
  has not been measured in game. Owner/trigger: same test pass.
- **BL-b96-DEBT-4 (P2, ledger gap found in passing):** `apply_svc_patches._apply_b7_eldest_soul_rebalance`
  implements an **unledgered Will decision** - its only record is the verbatim quote in its docstring
  ("crazy on normal, 74% physical damage resistance? doesnt that make you nearly unkillable by
  physical hits that arent piercing?"), never assigned an R-number. R-72 had to cite it by function
  name to describe what it supersedes. Owner/trigger: a rulings-backfill lane should assign it a
  number in the 70-79 decade. A broader sweep for other unledgered decisions living only in
  docstrings is likely worthwhile.
- **BL-b96-DEBT-5 (P3, dead write):** `_create_vashkarr` assigns `tags['tagSVCSoulVashkarr'] =
  '{^F}Soul of the Eldest'`, which the later F6 `_SOUL_NAME_STANDARD` pass unconditionally overwrites
  with `'{^F}Vashkarr, Eldest of the Ancients Soul'` (the value that actually ships and the one Will
  named). Harmless today but it is a silent ordering dependency: reordering the passes would rename
  the soul. Owner/trigger: tidy-up lane; deliberately NOT touched here (out of scope, and touching
  it risks the name Will used).

**b93 death-XP penalty -90% (2026-07-28, build54-dev) - NEW**
- **BL-b93-DEBT-1 (launch-gated):** the -90% death penalty is unproven IN-GAME. Owner/trigger: Will
  kills TQ + Steam, restarts, and dies once on a high-level Legendary character on DEV.
- **BL-b93-DEBT-2 (P0, BLOCKS THE DEPLOY):** the b93 arz `de589633d06a62d92afcd29b8701b74c` was NOT
  deployed. A concurrent lane wrote `5143ad1a44a9964c22578e00613f3e14` to the same DEV entry at
  13:55:19 (12 Toxeus `mesh` fields, `RevenantPoison.msh` -> `Skeleton01.msh`; likely
  `fix/green-diff` b92). The two changes are disjoint but the b93 build does not contain theirs, so
  deploying it would revert them. Owner/trigger: orchestrator merges `feat/death-xp-penalty` with
  the Toxeus-mesh branch, ONE rebuild, ONE coupled arz+Text deploy. Do not hand-patch.
- **BL-b93-DEBT-3 (not shipped):** Steam / canonical `CustomMaps\SoulvizierClassic` not touched by
  this lane; DEV only.
- **BL-b93-DEBT-4 (inherited, out of scope):** SV's `experienceLevelEquation` on
  `records\creature\pc\playerlevels.dbr` ships with an UNBALANCED parenthesis (one `)` short),
  inherited verbatim from SV 0.98i and present in every deployed arz. Nobody has established whether
  the engine's parser accepts it or silently falls back - which decides whether the live XP curve is
  really `65*(L+1)^3.25`. It affects only the "% of a level" framing in the b93 worked example, never
  the XP-LOST numbers (different, well-formed equation). Owner/trigger: a progression/XP lane.
- **BL-b93-DEBT-5 (doc hygiene):** `docs/MULTIPLAYER_COMPAT.md`'s determinism statement quotes a
  stale build27 arz hash. Owner/trigger: the next MP-facing pass.
- **BL-b93-DEBT-6 (cleanup candidate, WILL-VETO by default):** the five dead `deathPenalty*`-bearing
  gameengine lookalikes are now gated as "must stay vanilla" but remain unmanaged dead weight. Any
  retirement is subject to the RETIREMENT PROTOCOL.

**b91 Cold Worm buffs lane / R-39 (2026-07-28, branch `fix/debt-mixed`) - NEW**
- ~~**BL-b91-DEBT-1 (P1, BLOCKED - the one R-39 sub-item NOT delivered):** the exclamation-point map
  marker on placed ubers ... it is map-side ... needs `SVC_SVAERA_ARC`/`SVC_SV_ARC`.~~
  **✅ CLOSED 2026-07-28 (b91 round 2, same branch) - AND THE BLOCKER ITSELF WAS WRONG.**
  Only half of round 1's finding survives: (a) is TRUE - there is no "b63 mechanism" anywhere in
  this repo (the reports jump b62 -> b64; the only `b63` string is the workflow id
  `wf_87586bbf-b63`), so it genuinely had to be designed from ground truth. **(b) is FALSE.** The
  marker is **not** map-side: it is the DB-side Monster field **`DisplayAsQuestItem`**, present on
  **all 4,601 Monster records** and set to 1 on **124** of them - every base-game quest boss, every
  `xsq` named quest hero, the escort/rescue NPCs, the quest chests/doors/objects, and the whole
  `records\poi\**` `AreaOfInterest` map-marker namespace. It is **already LIVE in this mod on the
  very boss R-39 is about**: `records\test\boss_coldworm50.dbr` = 1 on `main`. Round 1 scanned only
  for `miniMapEntity`, found 0 Monster carriers, and generalised from that one field. (The
  secondary claim that the map arcs are unavailable is also stale - SVAERA is at Steam Workshop item
  `2076433374` and SV 0.98i's `Levels.arc` is in the `build36-map` worktree, per BL-b89-DEBT-5 - but
  nothing in this fix ever needed them.)
  **SHIPPED** as `tools/patches/uber_quest_markers.py` (registry module, apply+verify, after
  `coldworm_buffs`, before `visuals`). Roster is DERIVED, never hardcoded:
  `soul_spawn_provenance_sets()`'s `placed_members` (the same source of truth as the PLACED_UBER 66%
  soul rate, R-42), narrowed by **rule A** (it, or a form in its `actorToSpawnOnDeath` chain,
  actually pays a soul out) and widened by **rule B** (mark every DEDICATED chain form - one whose
  spawners are ALL in the roster). Both rules are derived from shipped content: the single placed
  uber already marked on `main` is `um_polisgaoler_99` AND its dedicated `um_polisgaoler_unbound_99`
  - exactly rule A + rule B. Rule B's exclusivity test is load-bearing: `as_ghosthero_32` is
  Neferkha's terminal form AND five ROAMING mummy heroes' (`um_tath_27`, `um_khenti_31`,
  `um_nebtaan_32`, `um_radementes_31`, `us_menkare_33`), so a naive whole-chain walk would spam the
  marker across the map. **Roster = 25 records (21 encounters + 4 dedicated forms), 23 newly
  marked**; 26 retinue/adds excluded - and independently corroborating the cut, all 26 excluded are
  rank=Champion while all 25 kept are Boss/Hero. Ships its own gate (every roster member marked, no
  SHARED form marked, 3 pre-existing anchors intact) + a 4-plant negative test
  (`py tools/patches/uber_quest_markers.py --negtest` -> PASS). ONE field, 0 new records, 0 tags,
  0 map bytes. **PROOF:** full DB build exit 0 under `SVC_RELEASE_DROPS=1 PYTHONHASHSEED=0`, whole
  gate battery green; `uber_quest_markers: modified 23 record(s), 0 tag(s)`; module verify over the
  final merged db = `25/25 ... 26 retinue/add records correctly unmarked; 1 shared transform form
  correctly left alone; 3 pre-existing anchors intact`; **record-diff vs the round-1 arz
  `461c54f95480f6c331f25ce7ab64c6f4` = 0 added / 0 removed / 23 modified, every one exactly
  `DisplayAsQuestItem: [0] -> [1]`, 1 field each, nothing else moved**; FOUR independent builds
  byte-identical at md5 `1526fbc4dbf3d5b21d551ef1fb9d3505` (55,424,905 B); registry selfcheck 35
  modules, order hash `0afd6ce08a6b...`. Report: `docs/reports/b91_coldworm_buffs.md` sec 9 (sec 7
  kept, marked SUPERSEDED, as the error record). **R-39 is now IMPLEMENTED, not PARTIAL.**
- **BL-b91-DEBT-2 (P0, WILL DECISION - found by the new roster drop-slot sweep, deliberately NOT
  fixed):** 4 records wire a soul at a real rate that **provably cannot drop**, because
  `dropItems=0` suppresses every equipped item on the record:
  `records\drxcreatures\bloodwitch\q_leinth_{47,49,50}.dbr` (Boss, `leinth_soul_{n,e,l}` @66) and
  `records\xpack\creatures\monster\karkinos\xhero_spinebreaker_42.dbr` (Hero, `spinebreaker_soul_*`
  @66). The signal is unambiguous - **881 of the 888 active soul droppers set `dropItems=1`**, 5 set
  0, 2 leave it absent. NOT fixed here because flipping it also releases Leinth's `lenithsveil`
  unique at 100% and Spinebreaker's rare-misc/parchment/potion tables: a real content change, which
  defaults to WILL-VETO. Owner/trigger: Will says yes/no; then a one-line module + wire
  `tools/sweep_soul_drop_slots.py --gate` into the build.
- **BL-b91-DEBT-3 (P2, open question):** `boss_titan_typhon_45` and `boss_daemonbull_yaoguai_38`
  carry a soul at chance>0 with `dropItems` **ABSENT** (inheriting the Monster.tpl default, which is
  not established in this repo). Either establish the template default or set it explicitly like the
  other 881. Owner/trigger: same lane as BL-b91-DEBT-2.
- **BL-b91-DEBT-4 (launch-gated):** the whole Cold Worm lane is unproven IN-GAME. The burrow
  (`giantkarkinos_flightofthekondor`) is the one **cross-rig graft** in the kit: it is bound to the
  worm's own `CryptWorm_AttGamma` dive animation via the repurposed ref4 `'Dive'` -> `'Kondor'`, which
  is correct by the anim-binding invariant but has no in-game precedent on this rig. Owner/trigger:
  Will, fresh character on DEV after a full Steam restart - does Cold Worm cast freezing blast / ice
  blasts / the burrow / the poison cloud, does the dive read as a burrow, and is the new speed
  profile (run 0.75 -> 1.8) fun rather than unfair?
  **EXTENDED 2026-07-28 (round 2, the marker):** also unproven in-game is the quest marker itself.
  `DisplayAsQuestItem` rendering is engine-side; it is proven live by 124 base-game carriers plus
  Cold Worm and Polis Gaoler inside this mod, so this is an EXISTING engine feature being extended
  rather than a new player surface being invented - but no agent has SEEN it (launching TQ was out
  of scope for the lane, and the player-surface checklist forbids claiming a visual from anything
  but an in-game-confirmed asset). Two questions for Will: (1) do the placed ubers now show the
  marker; (2) is **25 markers** the right density, or does it read as map clutter? If it is clutter,
  the roster narrows by editing rule A/B in one module - **no map rebuild** either way.
- **BL-b91-DEBT-5 (P2, hygiene):** `tools/sweep_soul_drop_slots.py` is shipped as a diagnostic, NOT
  wired into the build as a hard gate, precisely because it currently FAILs on the pre-existing
  content in BL-b91-DEBT-2/3. Wire it in as soon as those are ruled on. Owner/trigger: same lane.
- **BL-b91-DEBT-6 (P2, honest scope boundary of the new marker roster - round 2):**
  `uber_quest_markers`'s roster is the `records\drxmap\proxy*` PLACEMENT surface (via
  `soul_spawn_provenance_sets`). That is deliberate - it is the SAME definition of "placed" the
  PLACED_UBER 66% soul rate uses (R-42), so the two can never disagree - but it means an uber placed
  by any OTHER mechanism is outside the roster and would not be auto-marked. There is one such case
  today and it is already fine: **Cold Worm** (`records\test\boss_coldworm50.dbr`) is not proxy-placed
  and is not in the roster, but it already carries `DisplayAsQuestItem = 1` and the module asserts
  that as a pinned anchor. The residual risk is a FUTURE uber placed outside `drxmap\proxy*` being
  silently unmarked. Related known class: the drop-rate gate's own `UNREFERENCED(66)` bucket
  (`tools/verify_soul_drop_rates.py`), which is the same "pays a soul but no placement provenance"
  set. Owner/trigger: whoever widens the placement-provenance definition - widen it in
  `soul_spawn_provenance_sets` (one place, both consumers) rather than adding a second roster.

**b91 debt-clearance lane, domain `db` (2026-07-28, branch `fix/debt-db`) - NEW** *(these four were filed as BL-b91-DEBT-1..4; RENUMBERED to 7..10 by the debt-wave integration because the parallel `fix/debt-mixed` Cold Worm lane above had already claimed 1..6 for different items.)*
- **BL-b91-DEBT-7 (P3, new item):** 69 OTHER dangling FX `.dbr` refs across 24 distinct missing
  targets, measured while closing B-FX-DANGLING-1 (which named only the Chris ref). Several look
  like path typos that want a REPOINT, not a strip (a leading space, an `xxx` prefix, a `#`
  comment left as a value), so they are NOT one base-parity class. Full breakdown in the
  B-FX-DANGLING-2 entry above. Owner/trigger: its own small lane.
- **BL-b91-DEBT-8 (art call, WILL-CONFIRM):** the Emberteeth summon's PET-BAR PORTRAIT is the
  neutral summon-proxy - no `chimera_party_*` art ships. Same documented position as pygmalion /
  eaterofdays / xeiwang / mountainblade. A bespoke portrait is an art decision.
- **BL-b91-DEBT-9 (needs Will, playtest call):** the BL-ENSLAVER-SPAWNS marauder tankiness fix
  (`defensiveLife 100->40`, life `13k/18k/24k -> 10k/14k/18k`) landed AFTER Will's 2026-07-12
  report and has never been confirmed in-game. At 14000 Epic life the marauder is still the 99.9th
  percentile of the Champion roster, four spawn at once, and they drop nothing. b91 refused to
  invent a second cut on top of an unjudged fix. Owner/trigger: Will fights an Enslaver warband on
  DEV after a full Steam restart and says whether they are killable now.
- **BL-b91-DEBT-10 (launch-gated):** the Emberteeth summon is unproven IN-GAME - the button, its
  icon, the pet's mobility on the orthrus rig and the 3-tier scaling. Owner/trigger: Will, on a
  **FRESHLY DROPPED** soul (TQ bakes item properties at pickup, so a soul already in a bag will
  not carry the new grant).

**b90 Toxeus souls -> 100% (2026-07-27, build50-dev) - NEW**
- ~~**BL-b90-DEBT-1 (P1, NOT this lane):** `contracts_resources` reports **1252 P1** (`C-RES-DBR-1` 768,
  `C-RES-ASSET-1` 484). Proven PRE-EXISTING - the identical command over the pre-change baseline arz
  yields the byte-identical violation set (0 only-in-built, 0 only-in-baseline). This BACKLOG records
  the lane at **0 P0 / 1 P1** at an earlier date, so it regressed by ~1251 P1 BEFORE b90. Suspected
  environmental (see BL-b90-DEBT-2), not content. Owner/trigger: its own triage lane.~~
  **✅ CLOSED 2026-07-28 (branch `fix/debt-gate`). MERGED with its duplicate - the "BACKLOG DEBT (new,
  per WILL_RULINGS law #4)" block under the B80 gate record (~line 3808) filed the SAME 1252 P1
  independently. That block now points here; this is the single entry of record.**
  - **ROOT CAUSE (proven, and NOT the b80 stale-staging theory):** `contracts_resources.
    load_upstream_names()` returns an **empty set** when `upstream/soulvizier_098i/Database/
    database.arz` is absent, and `make_provenance` then falls through its last rule
    ("in neither upstream nor base => a mod invention") to **`'authored'` -> P1** for every
    SV-INHERITED subject. The severity CLASSIFIER degraded silently; no content moved.
  - **REPRODUCED EXACTLY, both directions, on one unchanged arz** (`work/.../SoulvizierClassic.arz`,
    `--only resources`, everything else identical, only `--upstream-dir` varied):

    | upstream_dir | total | P0 | P1 | P2 | gate |
    |---|---|---|---|---|---|
    | `upstream/` (present) | 4793 | 0 | **0** | 4793 | **PASS** |
    | `C:/nonexistent_upstream_repro` | 4793 | 0 | **1252** | 3541 | FAIL |

    Identical violation SET both runs - only the severity split moved, and the 1252 matches the
    b80 note's 1252 exactly. Note also that `upstream/` was EMPTY on this machine for the whole
    b80->b90 window and was only re-extracted on 2026-07-27 (BL-b90-DEBT-2), which is precisely
    when the phantom P1s appeared. The b80 hypothesis (stale `work/.../Resources/{Text,Levels}.arc`
    mtimes) is **refuted**: `C-RES-DBR-1` resolves against the arz + base arz only and never reads
    a staged Resources arc at all.
  - **FIX-UPSTREAM (BL-103), not a whitelist:** `make_provenance` now returns **`'unknown'`
    (-> P2)** instead of guessing `'authored'` when the provenance source was never loaded, and a
    new contract **`C-RES-INPUT-1`** raises **ONE loud P1** naming the missing input. A checker that
    cannot classify must say so, not guess. Mod-team-namespaced subjects (`AUTHORED_TOKENS`) stay
    `'authored'`/P1 with or without upstream - they are ours by name, no lookup needed.
  - **AFTER THE FIX** (same arz): upstream present -> **0 P0 / 0 P1 / 4793 P2, GATE PASS**;
    upstream absent -> **0 P0 / 1 P1 / 4793 P2, GATE FAIL** where the single P1 *is*
    `C-RES-INPUT-1` pointing at the missing arz. Failing for the right reason, with an actionable
    subject, instead of 1252 phantom content regressions.
  - **PLANTED NEGATIVE TEST:** `py tools/contracts/contracts_resources.py --negtest` - 5 cases
    (A healthy inputs classify sv/base/authored and a true invention is P1; B missing upstream
    yields `unknown`/P2, not the P1 phantom; C missing input raises exactly one `C-RES-INPUT-1` P1;
    D healthy input raises none; E namespaced subjects stay authored/P1 regardless). Self-contained,
    needs no artifacts. **PASS.**
  - **STAGE-FRESHNESS INSTRUMENTATION** added to `run_contracts.py` anyway (the b80 theory was
    wrong, but staleness was a real un-instrumented risk to the suite's ground truth): the report
    now prints a `stage freshness` panel comparing the staged `text_arc`/`levels_arc`/`quests_arc`
    mtimes against the `.arz` and names anything more than an hour behind. **Informational only** -
    it never changes the exit code, because a blocking rule would need a real coupling model
    (Levels+Quests ship together, arz+Text ship together) and mtimes alone would fire constantly on
    a healthy tree. On the current work/ tree it correctly flags Text -15.7h, Levels -16.7h,
    Quests -12.3d.
  - **RESIDUAL (not this lane):** the 4793 P2 are genuine inherited drx/sv/base third-party debt,
    unchanged in count and membership by this work. They are reported and never block. Whether any
    subset is worth fixing upstream is a separate content decision.
- ~~**BL-b90-DEBT-2 (P1, environment):** `upstream/` and `reference_mods/` were **EMPTY** on this machine,
  and `CustomMaps\SoulvizierClassic` (the canonical, non-DEV deploy) is **gone**. The DB build cannot
  run without `upstream/`, so b90 re-extracted **only the 4 files the build needs** from the archives
  still in `third_party/` (098i `Database/database.arz` md5 `11773cdc...` + `Resources/Text_EN.arc` md5
  `29505ac2...`; 0.9 `database.arz` md5 `b31951df...`; 0.41 `database.arz` md5 `056d6f4e...`). Correctness
  is proven by the record-diff (the rebuild reproduced `baseline_build47.arz` exactly apart from the 2
  intended fields). Owner/trigger: whoever next needs a MAP or Workshop build - decide whether the full
  `upstream/` + `reference_mods/` + canonical `CustomMaps\SoulvizierClassic` trees get restored.~~
  **✅ CLOSED 2026-07-28 (branch `fix/debt-tooling`). Closes BL-b89-DEBT-5 too (same defect, filed twice).**
  FIX-UPSTREAM: **ONE** preflight resolver, `tools/check_build_inputs.py`, owns every upstream build
  input. It was never really "the caches are empty" - it was that each entrypoint carried its own
  ad-hoc default path, so a missing input surfaced as a bare `FileNotFoundError` deep inside
  `ArzDatabase`/`ArcArchive`. Resolution ladder, first hit wins, per input:
  `$SVC_*` env var -> the in-repo cache -> **the MAIN checkout's cache** (gitignored caches never
  propagate into a linked worktree, and nearly every lane runs in one - this was the real gap) ->
  the install location (Steam TQAE / Workshop item `2076433374`) -> a sibling worktree -> a
  `third_party/` archive (reported as EXTRACTABLE; `--extract` unpacks `.zip`s). Every FALLBACK is
  md5-pinned (`EXPECTED_MD5`), so auto-resolution can never quietly feed the build a different
  upstream; a caller-supplied argv path that EXISTS is used as-is and unhashed, so existing
  invocations are byte-identical to the pre-preflight build. A miss fails LOUD once, naming the exact
  env var and every rung searched. Wired into `tools/build_svc_database.py` (sv098i+sv09 hard-fail;
  sv041 + base-game keep their previous OPTIONAL semantics and only warn) and
  `tools/svaera_plus_portals.py` (both merge inputs).
  **PROOFS** (all run from `.claude/worktrees/debt-tooling`, whose `upstream/` + `reference_mods/`
  are EMPTY and with NO `SVC_*` env var set):
  * `py tools/check_build_inputs.py --all --verify-hashes` -> **PASS (8 inputs resolvable)**; the 4 DB
    md5s match the b90-recorded prefixes exactly, plus SVAERA Levels `a1e13e48...`, SV 0.98i Levels
    `0b575c9d...`, SVAERA arz `7bad8804...`.
  * `py tools/check_build_inputs.py --selftest` -> **PASS**, 4 planted negatives + 1 positive
    (unresolvable input fails loud naming `$SVC_*`; a hash-mismatched fallback is REJECTED and the
    ladder keeps walking; an all-mismatched input fails instead of returning junk; an existing argv
    path is used as-is).
  * FULL DB BUILD from that worktree: `py tools/build_svc_database.py upstream/... work/.../SoulvizierClassic.arz "<TQAE>/database.arz"` -> **exit 0**, log opens with
    `PREFLIGHT: ... OK via main-checkout cache` for all three SV arzs; A7 golden gate PASS (84
    waived), unlock-alignment gate PASS.
  * FULL MAP MERGE from that worktree with `SVC_OUT_DIR` pointed at scratch -> exit 0; preflight
    resolved `SVAERA Levels.arc` via the Workshop item and `SV 0.98i Levels.arc` via the
    `build36-map` worktree cache, with no env vars set.
  * **OUTPUT-NEUTRALITY (the load-bearing proof):** both builds were re-run from the MAIN checkout
    (unmodified code, `SVC_*` set by hand) into scratch and compared byte-for-byte -
    map `Levels_merged.arc` md5 **`718abad63e7813dc78c4b169df969fd5`** (688,692,225 B) and arz
    `SoulvizierClassic.arz` md5 **`c1a8fa2aee5e6eb88b641b28d7dc6ae4`** (55,424,816 B) are
    **IDENTICAL** worktree-vs-main. The preflight changes what the build LOOKS UP, never what it
    builds.
  * `tools/contracts/run_contracts.py --only map` before vs after the `contracts_map` change:
    violation sets **IDENTICAL** (3 P2: MAP-PORTAL-1 x1, MAP-PORTAL-3 x2), GATE PASS both runs.
  DELIBERATELY NOT DONE (cheap-decision outcome): the full `upstream/` + `reference_mods/` trees were
  **not** re-extracted. Every input now resolves without them, `third_party/` still holds the
  archives, and re-extracting ~1.5 GB of gitignored duplicates buys nothing. Still open and NOT this
  lane: the missing canonical `CustomMaps\SoulvizierClassic` deploy dir (deploy-side, not build-side).
- **BL-b90-DEBT-3 (launch-gated):** the 100% drop is unproven IN-GAME. Owner/trigger: Will kills a
  Devourer and an Enslaver on DEV after a full Steam restart.
- ~~**BL-b90-DEBT-4 (open question):** the third Toxeus champion `um_toxeus_hunt_99` (Legendary Stalker)
  is still at **25%**. R-48 names only the Enslaver and the Devourer, so it was deliberately left alone.
  Owner/trigger: Will, if he wants the Stalker at 100 too.~~
  **✅ CLOSED 2026-07-28 by R-81 (b98, `feat/endless-hunt`, tag `build59-dev`).** Will wants him at
  100 too. `tools/patches/toxeus_souls_100.py` extended from two targets to three; the
  `verify_soul_drop_rates.py` waiver moves 25.0 -> 100.0 and the R-80 endless variant gets a matching
  waiver. That rate was the SOLE reason his soul appeared not to drop - the loot triple, the sub-roll
  weight, `dropItems` and all three soul records were already correct.

**b89 ocean_extension05 hotfix (2026-07-27, build49-dev) - NEW**
- ~~**BL-b89-DEBT-1 (P0-gated):** the 224-byte valid-EMPTY container is unproven IN-GAME.~~
  **✅ CLOSED 2026-07-27 - WILL CONFIRMED IN-GAME (verbatim): "the blood cave crash that was
  occurring is fixed, i was able to advance past that area".** The 224-byte stock-form empty
  container WORKS; the malformed-148-byte-stub root cause is CONFIRMED CORRECT and the build50
  Steam ship (item 3759792705) is VALIDATED. The fallback (no `0x0b` section at all + a strip-only
  path in `inject_rec02_into_blob`) is NOT needed and is retired unless a future ocean/empty
  chamber regresses. Source: `docs/reports/b89_ocean_ext05_hotfix.md` sec 5.
- ~~**BL-b89-DEBT-4A (P2, was "BL-b89-DEBT-4 - stale gate on a refuted premise"):** `MAP-NAV-4`
  (respawn-shrine + multi-GUID + SV-custom provenance) was authored from the **b87 theory that the
  2026-07-27 runtime captures REFUTED** (`navOK=0` is the normal in-progress state, not a rejection
  signal). Its two whitelisted "latent" chambers (`drxBC3`, `RogueEncampment`) were therefore
  flagged on a dead premise, and the REAL defect class (malformed container BODIES) is now gated
  properly by `MAP-NAV-5`/`MAP-NAV-6`.~~
  **✅ CLOSED 2026-07-28 (branch `fix/debt-gate`) - MAP-NAV-4 RE-SCOPED TO A P2 ADVISORY, WHITELIST
  ENTRIES REMOVED, FIX A RE-JUSTIFIED AND KEPT.** Chose re-scope over retirement (nothing deleted).
  - **RETIREMENT PROTOCOL, done first:** swept `docs/WILL_RULINGS.md` R-1..R-61 for any ruling
    naming MAP-NAV-4, isolated-load, co-residency, respawn-chamber navmeshes or `drxBC3` /
    `RogueEncampment` - **none**. No Will design intent is attached to this gate, so re-scoping it
    needs no ruling change; `WILL_RULINGS.md` is deliberately left untouched by this item.
  - **Severity demoted P0 -> P2** in `contracts_map.contract_navmesh_coresidency` (both the finding
    and the cannot-run guard) and in the `CONTRACTS` registry entry, whose `name`/`asserts`/
    `derived_from` now state the refutation instead of the dead crash law. `scan_isolated_load_risk`
    carries a boxed EVIDENCE STATUS header separating what is refuted (navOK=0 as a rejection
    signal; the "SV-custom multi-GUID respawn chamber crashes" inference) from what survives
    (ProcessRLTD's per-GUID residency check is still disasm-proven; `guid_count == 1` is
    stock-normal in 251 base levels AND runtime-proven on our map, so it is residency-proof by
    construction). It is now an honest **hardening preference**, not a demonstrated defect class.
  - **Both whitelist entries REMOVED** from `tools/contracts/whitelist_map.txt` (`drxBC3`,
    `XPack\Levels\Secret_Place\RogueEncampment.lvl`). They were suppressed as "latent P0 crashes" -
    the exact false claim this debt item flagged. A P2 never gates, so suppression was both
    unnecessary and a hiding place; the replacement comment block forbids re-adding MAP-NAV-4
    suppressions. Both chambers now appear in the battery as visible P2 advisories.
  - `gate_navmesh_coresidency.py` is now an **advisory reporter**: exits 0 by default, `--strict`
    restores fail-on-finding. Its negtest gained **case E** (the battery contract MUST emit P2 - a
    regression back to P0 fails the test) and **case F** (a cannot-run advisory must still report,
    at P2, never silently pass).
  - **build48 fix A (`new_secretdoor` collapsed to own-only): KEPT, re-justified on CURRENT
    evidence.** `guid_count == 1` is independently stock-normal (251 base levels) and runtime-proven
    on our own map - probe session B shows `new_secretdoor_transitionhallway` at gc=1 with a clean
    ENTER+LEAVE `al=1` (`docs/reports/b89_ocean_ext05_hotfix.md` sec 5). Its walkable footprint was
    preserved byte-for-byte, so reverting would churn the map (and the live DEV deploy) for no
    benefit. **Not reverted.**
  - `docs/reports/b87_bloodcave_navok_rca.md` gained a ⛔ REFUTED-PREMISE status header naming which
    sections are now historical and which conclusion survives; the body is preserved verbatim as the
    decision record.
  - **PROOF:** `gate_navmesh_coresidency.py --negtest` **PASS** (A/B/C/D scope + E/F severity).
    `_negtest_map.py` **38/38 PASS**. Standalone reporter on `work/.../Levels.arc` (build49
    canonical): 4 SV-custom respawn chambers checked, 2 advisories (`RogueEncampment` gc=3,
    `drxBC3` gc=6), **exit 0**. Full `--only map` battery: **0 P0 / 0 P1 / 5 P2, GATE PASS** - the
    2 now-unsuppressed MAP-NAV-4 advisories plus the 3 pre-existing base-game portal-noise P2s
    (XPack4 Dunes, Styx). No map rebuild: this item is contract-side only.
  - ~~Also review whether build48's fix A (`new_secretdoor` collapsed to own-only, shipped on the
    refuted theory) should stay.~~ **✅ BL-b89-DEBT-4B CLOSED 2026-07-28 (debt-map lane): KEEP, do
    not revert.** Decision + full rationale written into `docs/reports/b87_bloodcave_navok_rca.md`
    **sec 10a** and into `tools/gen_bc_navmeshes.py` at both sites (the `own_guid_only_keys` field
    docstring carries a "KEEP DECISION, DO NOT 'FIX' THIS AWAY" block; the `NEW_SECRETDOOR_KEY`
    comment carries a STATUS block marking the b87 premise SUPERSEDED). Wording of record:
    *retained as stock-normal, originally motivated by a since-refuted premise; harmless,
    walk-test-confirmed at build48/49.* Three reasons: (1) a single-own-GUID `0x0b` list is the
    shape 251 base-game levels ship and `MAP-NAV-6`'s negtest asserts it is compliant; (2) the
    sec-10 structural proofs stand independently of the motivating theory (192/192 tiles byte-
    identical heights+cons, walkable total preserved 479,328 == 479,328, seam overlap intact);
    (3) reverting costs a two-variant map rebuild plus a fresh walk test for zero player benefit.
    Sec 10's closing "If clean, extend fix A to drxBC3 and RogueEncampment" is **SUPERSEDED** - do
    not extend fix A on the b87 rationale. Documentation-only change, no map rebuild. Proofs:
    `_negtest_map.py` 49/49 PASS; `run_contracts.py --only map` = 0 P0 / 0 P1 / 3 P2 (pre-existing
    base-game portal noise), GATE PASS.
- **BL-DEBT-EMPTYLVL-1 (P2, NEW 2026-07-28, debt-map lane - donor-inherited, GATED, needs
  `SVC_SVAERA_ARC` to close):** **34 levels ship with their entire placed-entity set gone.** Found
  while re-verifying `RESPAWN-GREECEUG02`, whose "missing respawn shrine" turned out to be 1 of 257
  entities lost in a wholly depopulated level. A full vanilla-vs-ours census of all 2,282 shipped
  levels finds 34 that vanilla populates and our map ships with an **empty `0x05` placed-instance
  section** while the `0x0b` navmesh survives intact - geometry and walkability, zero monsters, props,
  containers or NPCs:
  - **XPack2 (3):** `hercynianforest03_cave` (vanilla 257), `primrosegrid01` (vanilla **1,778**),
    `delphiactorstemple` (24).
  - **XPack4 (31):** `devcave01-09/12/13`, `devmaze01-14`, `dathq01-06`.
  - **NOT systemic:** 268 of 287 shared XPack2 levels keep their entities (`birchforest01` 2,846,
    `suebilakelands02` 2,359, `jarnvidja02` 2,077, ...), so this is specific to those 34 donor blobs.
  - **NOT our regression:** the emptied set is **set-identical and blob-size-identical in every map
    we have ever built** - `build19-baseline`, `build30-canonical`, `Levels_deployed_prev` and the
    current `Levels_merged.arc` each carry exactly the same 34 levels at the same blob sizes, zero
    set difference. It is present from our earliest build, so it arrives with the SVAERA AE donor
    map rather than from any pipeline change of ours (the 3 XPack2 members also change version
    `LVL\x0e`/`\x0f` -> `LVL\x11`, the signature of a re-authored/re-saved donor blob).
  - **WHY IT IS ONLY *RECORDED*, NOT CLOSED:** proving the donor attribution directly requires
    diffing the SVAERA arc itself, and `SVC_SVAERA_ARC`/`SVC_SV_ARC` are **unset in this environment**
    (see BL-b89-DEBT-5 / BL-b90-DEBT-2). Everything provable without the donor arc is proved above.
  - **Owner/trigger:** a lane with `SVC_SVAERA_ARC` set confirms these 34 blobs are byte-identical to
    the SVAERA donor. If they are, this is an accepted upstream property and closes as WONTFIX
    (player impact is plausibly nil - XPack4 `devcave`/`devmaze`/`dathq` are developer/test level
    names and XPack2 is Ragnarok, which the campaign never enters - but `primrosegrid01` at 1,778
    entities deserves a look before that is assumed). If they are NOT, it is a real merge defect and
    becomes P1. **WILL-DECISION either way before anything is restored** - restoring donor-cut
    content is exactly what the RESPAWN-GREECEUG02 verdict declined to do.
  - **GATE SHIPPED (same commit):** `MAP-EMPTY-1` in `tools/contracts/contracts_map.py` freezes the
    inventory as `DONOR_DEPOPULATED_LEVELS` and fires **P1** on any level outside it that ships empty
    while vanilla populates it, so our build can never silently depopulate a level again. It fires
    **P2** if a frozen level regains its entities, so the inventory is re-frozen deliberately rather
    than drifting silently (retirement protocol: do NOT delete entries to make the gate green). Fails
    loud if the stock base map is unavailable. 8 planted negative tests in `_negtest_map.py`, incl.
    the two scope guards (frozen-level silence, and levels that are empty in vanilla too - 202 such
    border/filler levels exist and must never fire). Source:
    `docs/DEAD_CONTENT_AUDIT_2026-07-10.md` LANE B AMENDMENT 2026-07-28.
- **BL-b89-DEBT-2 (P1):** **Steam/canonical map is NOT shipped this wave.** The canonical
  `Levels_merged.arc` carries the same 8 malformed containers, so the LIVE Workshop build
  (item 3759792705) has the same latent crash. Rebuilt+verified here but deliberately NOT packaged or
  uploaded (walk-test-gated, same policy as build48). Owner/trigger: Will confirms the DEV walk test,
  then package+upload the canonical variant.
- ~~**BL-b89-DEBT-3 (P2):** `contracts_map.CUT_LEVEL_MARKERS` still marks the whole
  `ocean_extension*` family cut, but 6 of them (`01`-`04`, `x02`, `x08`) carry REAL generated
  navmeshes and are area-owners inside `drxBC3`/`drxBC_Finale`'s GUID lists - i.e. live walked-on
  content.~~ **✅ CLOSED 2026-07-28 (`fix/debt-docs`).** FIX AT THE CORRECT LAYER: the substring
  tuple `CUT_LEVEL_MARKERS = ('ocean_extension', 'coldtombs')` is replaced by an EXACT-BASENAME
  `CUT_LEVELS` frozenset of the 8 genuinely geometry-less levels (`ocean_extension05`,
  `ocean_extensionx01/x03/x04/x05/x06/x07`, `coldtombs`) plus a `level_basename()` helper, so a
  level can no longer be exempted by an accident of substring matching. `docs/CUT_CONTENT.md`
  rewritten: the 6 live levels are moved to a "NOT cut - live walked-on content" table with their
  real navmesh sizes / tile counts / owning meshes, and a standing warning that CUT exempts
  MAP-NAV-3 **only** (streaming is by grid proximity, so a cut level's container must still be
  structurally valid - the whole b89 lesson). **PROOF (no contract loses coverage):**
  (a) `_negtest_map.py` gains `test_cut_levels()` - 8 cut-TRUE + 6 live-FALSE assertions, a
  substring-regression assertion, and a PLANTED NEGATIVE proving MAP-NAV-3 now FIRES on a live
  `ocean_extension02` with no `0x0b` (pre-fix: silently exempt) while staying silent on a genuinely
  cut one. Suite: **53/53 checks PASS**. (b) exemption-delta probe over BOTH shipped variants
  (`local/Levels_merged.arc` + `local/Levels_merged_TESTHUB.arc`, 2282 levels each): exempted
  14 -> 8, all 6 moves are CUT -> NOT-CUT (coverage gained, never lost), and **0** of them would
  newly violate MAP-NAV-3 (every one has a `0x0b`). (c) `run_contracts --only map` on the canonical
  map: **0 P0 / 0 P1 / 3 P2**, byte-identical violation set to the pre-change baseline.
  Source: `docs/reports/b89_ocean_ext05_hotfix.md` sec 3-4.
- **BL-b90-DEBT-5 (P2, NEW 2026-07-28 - stale local artifact):** `local/Levels_merged_TESTHUB.arc`
  is dated **Jul 17 (pre-b89)** and still carries all **8 malformed 148-byte stubs**
  (`run_contracts --only map` against it: 16 P0 = MAP-NAV-5 x8 + MAP-NAV-6 x8). Only the canonical
  `local/Levels_merged.arc` (Jul 27) was refreshed by the b89 wave. Nothing ships from `local/`, so
  this is an artifact-hygiene issue, not a player-facing one - but any lane that reaches for the
  TESTHUB variant will gate-FAIL on b89 defects that are already fixed. Owner/trigger: the next map
  lane rebuilds it (needs `SVC_SVAERA_ARC`/`SVC_SV_ARC` per BL-b89-DEBT-5/BL-b90-DEBT-2).
  Found by: the BL-b89-DEBT-3 both-variants proof run.
- ~~**BL-b89-DEBT-5 (P2)** *(id corrected 2026-07-28 - this entry was filed as a SECOND
  `BL-b89-DEBT-4`, colliding with the MAP-NAV-4 entry above, which the `fix/debt-gate` lane
  renumbered to `BL-b89-DEBT-4A`/`-4B` when it closed it. The `fix/debt-docs` and `fix/debt-tooling`
  lanes each resolved the collision independently and in OPPOSITE directions; the debt-wave
  integration keeps 4A/4B = the MAP-NAV-4 item and 5 = this upstream-cache item.)*:
  `reference_mods/SVAERA_customquest/` and `upstream/soulvizier_098i/` are
  EMPTY in the main checkout; the merge only runs via the new `SVC_SVAERA_ARC`/`SVC_SV_ARC` overrides
  (SVAERA from Steam Workshop item `2076433374`, SV 0.98i from the `build36-map` worktree). Any lane
  that rebuilds the map needs those set. Owner/trigger: restore the caches or bake the fallbacks in.~~
  **✅ CLOSED 2026-07-28 (debt-tooling lane) - the fallbacks are BAKED IN.** Same fix as
  BL-b90-DEBT-2 below: `tools/check_build_inputs.py` resolves both merge inputs through the shared
  ladder and `tools/svaera_plus_portals.py` calls it at startup. Proof in the BL-b90-DEBT-2 entry.

**Toxeus / MP-compat**
- np-equation per-player expansion (rant scroll) unproven on a monster EQUIP slot (proven only for
  containers) - owner/trigger: live check at np=2, kill Blood Toxeus, confirm 2 scroll copies drop;
  fallback (corpse/chest with `toxeus_rant_perplayer`) already authored if it fails. Source: docs/
  MULTIPLAYER_COMPAT.md M4.3/M4.7.
- Legendary-only Toxeus stalker (Hydra fixed-placement pattern) - APPROVED + QUEUED (R-16), NOT
  scheduled/built. Source: docs/MULTIPLAYER_COMPAT.md M4.6-M4.7.
- Corridor full-strength (non-10s-cooldown) Blood-Toxeus Tears-of-Blood variant - OPEN Will decision
  (R-5). Source: docs/WILL_RULINGS.md R-5.
- ~~`svc_black_poison` skill (Devourer poison + End of All Things strike-buff asset) - PENDING
  build.~~ **CLOSED 2026-07-28 (ledger-hygiene pass):** SHIPPED as b83 on `feat/black-poison`, which
  the BUILD47 GATE RECORD (2026-07-17) merged to main; module `tools/patches/black_poison.py` is in
  the registry with a fail-loud verify(). Source: docs/WILL_RULINGS.md R-7;
  docs/reports/b83_black_poison_rite_drop.md.
- ~~Rite of the Undivided drop-pool wiring (ship wherever supra/uber formulas can drop) -
  PENDING.~~ **CLOSED 2026-07-28 (ledger-hygiene pass):** SHIPPED as b83 (both `supra.dbr` and
  `supra_special.dbr` pools + the guaranteed on-kill table for R-13), merged to main in the BUILD47
  GATE RECORD. Source: docs/WILL_RULINGS.md R-9/R-13; docs/reports/b83_black_poison_rite_drop.md.
  RESIDUAL (still open, different question): the 100% on-kill rate is flagged WILL-VETO in the b83
  report - the champions are repeat-killable, so Will may want a chance instead of a guarantee.
- dark_smoke Diadochi-generals/Helepolis green-render swap - pending Will's in-game black-confirm of
  the Enslaver (R-10). Source: docs/WILL_RULINGS.md R-10.
- Enslaver DISMISS + RE-SUMMON green-residue check - WILL-CONFIRM after a full Steam restart; if
  still green after re-summon, residue is asset/pfx-level, chased next round. Source: docs/BACKLOG.md
  ~line 2982; docs/reports/b71_enslaver_chain_rca.md.

**End of All Things (EoAT, feat/toxeus-undivided branch, not yet on main)**
- EoAT depth-3 thrall chain ("there is room in me": pet -> disciple pets -> hound sub-summons) -
  engine-UNVERIFIED whether a pet's own spawn-pet skill fires while itself a pet; shipped at proven
  depth-2 with the depth-3 attempt attached; needs Will's in-game confirmation. Fallback documented
  (disciples summon hounds directly, both depth-2). Source: `git show feat/toxeus-undivided:docs/
  reports/b72_toxeus_endofallthings.md` FLAG #1 (not yet merged to main).
- EoAT supra-stats bake option - the 8 ruled supra-tier equipment pieces cannot be worn by a summoned
  pet on this engine (proven: 0 of 25,000+ equip slots auto-equip a player unique; B-SUMMON-1 gate
  fails the build on direct-equip). Shipped as a DIRECT stat block instead of worn items; flagged in
  case Will wants a different resolution. Source: same report, FLAG #2.
- ~~disciple Neck-slot hygiene - named in a prior session's task tracker; NOT located in any
  committed doc or branch this sweep. UNKNOWN-STATUS.~~ **CLOSED 2026-07-28 (`fix/debt-docs`) as
  UNSUBSTANTIATED-BUT-PROBABLY-ALREADY-DONE.** Both findings recorded, neither silently dropped:
  **(1) No antecedent exists.** `git log --all -S` for "Neck-slot" / "neck slot" / "neckslot" /
  "disciple neck" returns exactly ONE commit across every ref: `103409d` "docs: rulings ledger
  backfill round 1 + BACKLOG debt register" - i.e. the commit that created THIS entry. The phrase has
  no origin anywhere in the repository's history; it entered via the backfill brief alone. A
  repo-wide grep confirms the only other "Neck" hits are the EoAT report's unrelated equip-slot table
  row ("Neck | Paragon of Violence | SKIPPED"). **(2) The only plausible referent is already
  shipped.** `tools/patches/toxeus_endofallthings.py:_build_disciple_thralls` (b72, on main via the
  BUILD47 GATE RECORD) zeroes EVERY equip slot on the EoAT disciple thralls - `RightHand`, `LeftHand`,
  `Head`, `Torso`, `Forearm`, `LowerBody`, `Finger1`, `Finger2` **and `Neck`** - under the comment
  "weaponless caster: clear every equip slot (no Monster.tpl field copy)". If the tracker line meant
  anything concrete, that is it, and it is done. **ACTION: none.** Re-file with a concrete symptom if
  a real defect ever surfaces; do not carry an unverifiable ghost in this register.

**Masteries / UI**
- Occult pane aesthetic (`standardskillbackground_joanna_ver_dark.tex`) + the wired-but-unconfirmed
  select-screen preview (`occultpanellarge.tex`) - flagged for Will's veto / in-game screenshot per
  the standing UI-on-device rule; not yet confirmed on-device. Source: docs/reports/b67_oh_pane_art.md
  sec "Flagged for Will's veto".
- Controller-mode Occult pane - the 919x540 chosen asset doesn't match the 980x540 gamepad-mode
  canvas; gamepad play keeps the vanilla tan backdrop (still renders, just not reskinned). Out of
  round-1 scope; needs a Will decision if gamepad parity matters (stretch existing asset vs. author a
  wider one). Source: docs/reports/b67_oh_pane_art.md sec "Residual: controller-mode canvas".
- Occult select-description wording (`tagMasteryDescription05`) vs `tagOccultTitleDESC` - Will's veto
  pending, unreconciled. Source: docs/reports/mastery_ui_reflow_round2.md.
- `drxlethalstrike` `_right` bar rises toward the empty c6t7 slot, passing Flurry - pre-existing,
  flagged for a future holistic m5 reflow pass (byte-identical since before b70, not a regression).
  Source: docs/BACKLOG.md ~line 3113.
- 10 bosses (pygmalion, eaterofdays, xeiwang, charon, hadesmarshal, mnemophage, mountainblade,
  neferkha, tantalus, voranthys) ship on the neutral `proxy_party` pet-bar portrait instead of a
  bespoke one - WILL-CONFIRM, a future art pass. Source: docs/reports/b71_enslaver_chain_rca.md.

**World / placement**
- B87 blood-cave isolated-load navmesh crash (MAP-NAV-4) - SV-custom respawn+multi-GUID chambers.
  `new_secretdoor_transitionhallway` (P0, Frida-probe-PROVEN crash) is **FIXED to DEV (build48-dev,
  fix A single-own-GUID)** and REMOVED from the whitelist - PENDING Will's in-game walk test (crash
  gone AND west/east seams still walk); if the walk test fails a seam, escalate it to option C.
  Still OPEN DEBT (whitelisted) until each is single-own-GUID'd + Will walk-tests: `drxBC3` (P0,
  latent, respawn_hades_shrine01), `XPack\Levels\Secret_Place\RogueEncampment.lvl` (P0, latent -
  Secret Place / Duister). Extend fix A to each only after new_secretdoor verifies in-game. The gate
  (`MAP-NAV-4`, provenance-scoped) fails loud on any NEW SV-custom respawn+multiGUID chamber.
  Source: B87 above + docs/reports/b87_bloodcave_navok_rca.md sec 6+10; WILL_RULINGS walk-test law.
- Lower-Olympus dead respawn shrine (`respawn_olympus_new.dbr`, `olympusfinal02`) - Will asked to
  REMOVE it [paraphrased; origin instruction not located in docs/ this sweep]; the de-place fix was
  coded but as of the 2026-07-10 dead-content audit was STILL live in the shipped map (needs a map
  rebuild + redeploy + re-verify). No later doc confirms this shipped - OPEN. Source: docs/
  DEAD_CONTENT_AUDIT_2026-07-10.md LANE B; docs/WILL_RULINGS.md R-35.
- `respawn_towerofjudgement01.dbr` dangling GROUPS-binding shrine (judgment_towerug_floor04) - needs
  a `REMOVE_DANGLING_SHRINE_SPECS` entry (only `olympusfinal02` is currently listed) or a GROUPS
  re-bind; MAJOR, mandatory-path-adjacent. Source: docs/DEAD_CONTENT_AUDIT_2026-07-10.md LANE B.
- ~~`respawntemplegreeceug02.dbr` missing respawn point (Hercynian Forest underground, Ragnarok act) -
  MINOR, lower confidence this is unintended vs a deliberate SVAERA cut.~~ **✅ CLOSED 2026-07-28
  (RESPAWN-GREECEUG02, debt-map lane): it IS a deliberate SVAERA cut, faithfully inherited - NOT
  restored, no `M13A_MUST_BIND` entry, no map rebuild.** Three-way byte probe of
  `HercynianForest03_Cave.lvl` + the `X2_CelticHeartland_respawners` GROUPS record: vanilla base =
  275,873 B blob, shrine PRESENT, **17** members; **SVAERA (our AE donor) = 276,839 B re-authored
  blob, shrine ABSENT, 16 members**; ours = **byte-identical to SVAERA** (276,839 B, absent, same 16
  members in the same order; missing uid is base's 17th, `0b42a827814a..`). The loss originates
  upstream in SVAERA, not in our merge - M13a takes SVAERA as base truth and only re-adds SV-EXTRA
  members, so it correctly inherited the cut. Restoring would mean inventing content SVAERA
  deliberately removed. Player impact is additionally nil: XPack2 = Ragnarok DLC, and the campaign
  ends at Hades for every DLC combo (DLC integration CANCELLED), so no SVC character ever enters
  that cave. The 07-10 audit's "the merge dropped both the instance and its binding" is REFUTED and
  corrected in place. Source: docs/DEAD_CONTENT_AUDIT_2026-07-10.md LANE B (now carries the
  RESOLVED block + the evidence table).
  **AMENDED 2026-07-28 (re-verification pass, verdict UNCHANGED and better supported):** the shrine
  is not a de-placed device in an otherwise normal cave - the level ships with an **empty `0x05`
  section entirely** (vanilla 257 placed instances + 50 `.dbr` strings; ours **0 instances, 1 `.dbr`
  string** in 276,839 B, navmesh byte-identical at 140,138 B, version `LVL\x0e` -> `LVL\x11`). The
  shrine is 1 of 257 entities lost, which rules out a targeted merge de-placement. This is a CLASS of
  34 donor-depopulated levels, now tracked as **BL-DEBT-EMPTYLVL-1** and guarded by the new
  **MAP-EMPTY-1** contract.
- murderbossroom (Secret Place crow bosses) has no placed NPC on either end - the ONLY one of the 3
  sealed SV areas still fully sealed (Sparta Crypt L2 + Uber Dungeon crypt_floor1 were wired); needs a
  map-lane NPC placement before the quest-lane enter-offer pattern can apply. Source: docs/
  reports/b62_travelers_into_areas.md; docs/BACKLOG.md ~line 2898 "OPEN WILL Qs".
  **STATUS 2026-07-28 (MURDERBOSSROOM-NPC, debt-map lane): MAP-SIDE BLOCKER RESOLVED, FEATURE NOT
  SHIPPED - still OPEN, now UNBLOCKED and fully specced.** The thing this item was actually stuck on
  (a navmesh-verified interior landing in a box-isolated level) now exists and is gated:
  - Surveyed `XPack/Levels/Secret_Place/murderbossroom.lvl` (v0x0e, corner `(-3592,0,-5955)`, 16
    `0x05` instances, `0x14`=0, `0x0b` 70,910 B): **80,608 walkable cells in exactly ONE component**
    across all 3 tilesets - no partition risk.
  - **LANDING = level-local `(54.0, 3.0, 18.0)` = world `(-3538, 3, -5937)`;
    interior RETURN NPC = level-local `(51.0, 3.0, 16.0)` = world `(-3541, 3, -5939)`**, 3.61u apart
    (the proven `svc_testhub_return_sparta`/`_uber` ~3u pattern) and **16-18u clear of the
    `murderbunny` crow boss** at local `(54,3,34)` - deliberately outside the set-piece per the b44
    deadly-landing lesson. Both on-mesh d=0.14u, clearance 100% at ext=3.0, component #1.
  - **`tools/debug/gate_landing_clearance.py` (G-LAND) = PASS**, run with the interior NPC supplied
    as a PLANNED placement so the landing is gated against an entity not yet on the map: nearest
    neighbours 3.61u (planned NPC) / 6.00u (archway prop) / 7.24u (urn) / 16.00u (the boss); every
    per-class threshold cleared, nothing inside the 1.5u PIN radius. `SUMMARY PASS=1`.
    **INDEPENDENTLY RE-RUN 2026-07-28** from the committed fixture against
    `local/Levels_merged.arc` (2,282 levels indexed): `GATE G-LAND: PASS`, `SUMMARY PASS=1`,
    `nav: N:d=0.14/clr=100% E:d=0.14/clr=100% L:d=0.14/clr=100% comp#1/80608 on-mesh`, neighbour
    ladder reproduced exactly (3.61u planned NPC, 6.00u archway + portcullis, 7.22u underlord egg,
    7.24u urn, 16.00u murderbunny, 37.00u trigger, 54.00u far archway) - `=> clear + on-mesh`.
  - **NOT shipped, and deliberately nothing half-wired:** no enter-offer exists without its paired
    return because neither was written. Remaining work is a cross-lane wave, enumerated step by step
    (DB record + 2 Text tags + 1 `INJECT_SPECS` line + the `TRAVELER_ENTER_OFFERS` entry + gates)
    in `docs/reports/b62_travelers_into_areas.md` under "UPDATE 2026-07-28". Hard constraints for
    whoever picks it up: **WARDEN LAW** (the new boat-dialog record must be placed exactly once),
    **the map placement and the enter-offer must land in the SAME commit** (P0-A "no way back"), and
    **Will's walk test gates the canonical/Steam ship**. Owner/trigger: a combined DB+map+quest wave.
- M1 (HV01) pet-test yard spacing: shipped at 32.25u vs the original >=60u ask - geometrically
  infeasible in HV01's ~4,470 sq-unit floor at 10 groups; Will's decision open between (a) accept
  32.25u [recommended], (b) cut group count to fit 60u, (c) relocate the yard to a larger host.
  Source: docs/reports/b41_map_pass_result.md OPEN ITEMS #1; docs/reports/b41_map_pass_plan.md.
- Obsidian-roulette apex charm (Emberscale-pattern "Obsidian Shard") - optional, NOT built; chest +
  soul already judged a sufficient double reward. Source: docs/OBSIDIAN_ROULETTE_DESIGN.md sec 5.
- b47 Dorus: rename to a distinct amgoz1-worthy identity + relocate near a Medea tomb/dungeon interior
  - RCA'd, not yet renamed/relocated per the report's own open items. Source: docs/reports/b47_dorus.md.
- ~~b51 Arachne's Shame / Fetid Lair spawn-chain RCA - identification + baseline diff + git-blame not
  yet fully closed out in a committed report this sweep found. UNKNOWN-STATUS.~~ **CLOSED 2026-07-28
  (`fix/debt-docs`).** The RCA WAS completed - it just never reached main. It lived on the unmerged
  branch `feat/b51-arachne` (commits `74f1eac` "b51 RCA: Arachne's Shame (Fetid Lair guaranteed hero)
  - chain INTACT, no systemic break" + `9a72610` "independent replay confirms Arachne's Shame E/L
  guarantee INTACT - no fix (banned rebalance)"), whose entire diff vs main is the single file
  `docs/reports/b51_arachnes_shame.md`. That report is now MERGED to this branch. **VERDICT:** the
  guaranteed Epic/Legendary chain (`jg06_arachnospool - poisonspring c` proxy ->
  `JG06_Arachnos_PoolB`, `spiderblackwidow01` at `spawnMin=spawnMax=1`, `HeroLimit_All`) is
  byte-functionally identical to classic SV 0.98i in BOTH the arz and the deployed map; all five
  brief hypotheses refuted; the sibling sweep over all 809 SV098 E/L proxies found **0** that lost a
  boss/hero/quest member. **NO FIX APPLIED and none warranted** - altering an intact guarantee would
  be a forbidden rebalance. RESIDUAL (a test, not a debt item): Will enters a Fetid Lair his Epic
  character has NOT yet visited (baked non-resetting Act-1 instance = the real explanation for her
  absence); if she still fails to appear there, escalate to a runtime spawn probe. Note the branch
  named `feat/b51-fetid-spider` carries NO b51 content - its tip is a build38a commit and it is
  already an ancestor of main; do not look for the fix there.
- Sparta Crypt L2 binder: no proven SV binding exists; if shipping, needs either a blob-patch restore
  or a quest teleport (Will decision) - recommended default is defer/drop unless Will wants
  completeness. Source: docs/WALL_INVESTIGATION_STATE.md (or equivalent Sparta-area report).

**Souls / items**
- Legion-terminal-stage 66%-vs-50% drop-rate reconciliation - queued for the NEXT souls pass (folds in
  with the 155 documented minor gaps + 79 drop-gated souls + Crowboar summon-controller polish).
  Source: docs/BACKLOG.md "WILL RULINGS 2026-07-16 (post-build42)".
- Legion DISTINCT-souls-per-stage canonical/orphan decision - 6 chains (possessedboar / hades /
  lillued / charon families) each drop TWO souls; Will must pick the canonical soul per chain and
  orphan the other (explicitly deferred as "design ruling required"). Source: docs/reports/
  b56_legion_soul_stages.md section (B). Owner: next souls pass. [added round-2 per vet]
- Shadow Link malus party-spread veto flag - the defensiveLife malus (-5/-8/-11/-14) now reaches the
  whole party at 36u; "Flagged so Will can veto if unintended". Source: docs/reports/b57_aura_radius.md.
  Owner: Will DEV pass. [added round-2 per vet]
- 36u party-wide aura balance note - b57's "Balance note (flag, do NOT nerf - Will decides)" on the
  widened radii remains an open Will decision. Source: docs/reports/b57_aura_radius.md. Owner: Will
  DEV pass. [added round-2 per vet]
- ~~Cold Worm buffs (3x life / +20% armor / kit / speed / 3-tier soul + loot-triple fix / roster
  drop-slot sweep)~~ - **CLOSED b91** (branch `fix/debt-mixed`, `tools/patches/coldworm_buffs.py`).
  RCA: Cold Worm's ENTIRE kit pointed at the `boss skills\d2custom\coldworm_*` + `Game\D2*` namespace,
  which exists in NEITHER the mod arz, NOR upstream SV 098i, NOR the base game - 8/8 active skill
  slots dead, the worst record in the whole DB (next-worst: 2/2). Every dead slot repointed at an
  EXISTING donor at that donor's own level (CryptWorm-rig `um_coldcreep_29` / `am_devourer_27` +
  nearest-tier insectoid bosses); life 3x; +20% armor via the `armor_passive` level (the only layer
  where monsters carry `defensiveProtection` - 0 non-zero carriers of the raw field DB-wide, and the
  passive's array is exactly linear); rig-proven speed profile incl. the 0.15-0.4 anim speeds and the
  0.3/0.1 rotation speeds. Ships a NEW invariant gate (an active skill slot must be CASTABLE: skill
  resolves AND its `skillSpecialAnimationName` is bound by an `unarmedSpecialAnimRef` - the
  monster-side twin of B-SOUL-PROC-2) with a planted negative test, plus
  `tools/sweep_soul_drop_slots.py`. The 3-tier soul + loot triple were already correct and are now
  asserted, not rewritten. Record-diff = EXACTLY 1 record / 70 intended-class fields; arz md5
  `461c54f95480f6c331f25ce7ab64c6f4`. ~~**The marker sub-item is NOT done** - see BL-b91-DEBT-1;
  R-39 stays PARTIAL.~~ **UPDATE 2026-07-28 (round 2): the marker sub-item IS done** -
  `tools/patches/uber_quest_markers.py` sets the DB-side Monster field `DisplayAsQuestItem=1` on the
  25-record derived placed-uber roster (23 newly marked). Round 1's "map-side, blocked" verdict was
  wrong: the field is on Monster.tpl and was already live on Cold Worm himself. **R-39 is
  IMPLEMENTED.** Report: `docs/reports/b91_coldworm_buffs.md` (sec 9; sec 7 SUPERSEDED).
- ~~Souls scaling gate across normal/epic/legendary (the "Blood Cult High Priest epic==normal"
  defect class) - PENDING, `fix/soul-tiers` branch.~~ **CLOSED 2026-07-28 (ledger-hygiene pass):**
  SHIPPED as b78 on `fix/soul-tiers`, merged to main in the BUILD47 GATE RECORD. The roster sweep
  found 0 flat-tier families / 0 wrong-tier loot triples / 0 real missing tiers (Will's observation
  was a save-bake artifact), so the deliverable is the permanent strict-progress gate, not a data
  change. Source: docs/WILL_RULINGS.md R-40; docs/reports/b78_soul_tier_scaling.md.
- ~~Formula display names matching what they craft (the "Mythic Formula - Crystalline Mask crafts
  Galefury" class) - PENDING, `fix/formula-names` branch.~~ **CLOSED 2026-07-28 (ledger-hygiene
  pass):** SHIPPED as b80, merged to main in the BUILD47 GATE RECORD; the 245-formula sweep found no
  other instance and the permanent gate (`tools/patches/formula_names.py` verify() +
  `tools/validate_formula_names.py`) is in the build. Source: docs/WILL_RULINGS.md R-41;
  docs/reports/b80_formula_names.md.
- Uber axe reagent trio reuses the same 2 Legendary reagents across the whole 5-member family (a
  resolving-but-undiversified choice) - flagged for Will's veto if he wants more variety; not built.
  Source: docs/reports/b66_uber_formulas.md.
- No quality orphan exists for a second Spear or a Shield uber - would need fresh authoring, not
  sourced from an orphan. Source: docs/reports/orphaned_weapons_curation.md "Honest gaps".

**Explicitly checked and EXCLUDED (resolved, not open debt)**
- Eviscerate shape / adjacent occult-column items - RESOLVED (R-21 square-shape fix b70; R-22 column-6
  restack b70, which the report states SUPERSEDES the earlier "needs Will's ruling" residual). Listed
  here only so a future sweep does not re-flag it as open.
- bloodtip/gustleech `itemSkillLevel` WILL-VETO - RESOLVED, ratified ship-as-is (R-45).
- Tomb Guardian soul leak - RESOLVED (R-70; filed by the b84 backfill as a colliding second "R-43", renumbered 2026-07-28 into the new Souls overflow decade 70-79 - R-49 was already claimed by the fix/devourer-chest lane).
- Rant-scroll creative-text veto - RESOLVED, cleared to ship (R-15).
> 🧊 **b76 CHUMBI VALLEY P0 FREEZE - RCA + FIX (round 1) ON `fix/chumbi-lag` (2026-07-16).** Will (P0):
> DEV "chumbi valley" frozen by "every boss you created all in one spot" + "the infinite summon of the
> skeleton dog guys tomb guardian ... the uber boss whos name has sepulcher in it." **RCA (two
> co-primary defects):** (1) PLACEMENT PILEUP = the TESTHUB-only **Monster Test Yard** (10 boss pools
> stacked in HiddenValley01 around the Rebirth Fountain + occultist = the death loop) - a QA cluster
> that grew one boss per wave (build33 7 -> build36 10); TESTHUB-ONLY (canonical places each boss on
> its own host, so only DEV freezes). (2) UNBOUNDED SUMMONS = `um_voranthys_99` (the "sepulcher" boss,
> fires `sepulchralwyrm_firebreath`) whose 3 summon skills (aktaios tomb guardians + alastor skeleton
> warrior/archer, enabled by b39 boss_skill_fix) carry a single-digit petLimit but **NO
> spawnObjectsTimeToLive** -> minions permanent, re-summoned forever. **FIX 1 (map):** removed the yard
> block from `build_section_surgery.build_hub_extra_specs()` (yard 10->0; TESTHUB HV01 now == canonical
> HV01; bosses disperse to their canonical homes). **FIX 2 (DB):** NEW registry module
> `tools/patches/summon_caps.py` additively restores the SV-convention TTL (tomb guardians 5.0 = SV
> shodema; skeletons 20.0 = four_generals) on the 4 unbounded boss-summon skills; petLimit untouched
> (already a single-digit concurrent cap). ⚠️ WILL-VETO on the TTL seconds. **CHEST:** HV01 has no
> static boss chest; the "Dead Adventurer's Chest" = the widowletter QUEST chest (quest-spawned, sealed
> by the widow buff), byte-untouched; the yard had no reward container - removing it clears the false
> association (bosses' canonical homes carry their own svc_*_chest majestic chests). **VERIFY:** DB
> scratch build EXIT 0 (`local/SoulvizierClassic_b76.arz` md5 `7fb879ac9c346280cdaf3610e7d53dad`,
> 55,382,493 B); record-diff vs build45 `917d9047` = EXACTLY 4 MODIFIED (single spawnObjectsTimeToLive
> each), 0 collateral; summon_caps.verify + --negtest PASS; summons contract violation set
> BYTE-IDENTICAL to reference (0 new/removed, 96 pre-existing whitelisted P0); registry selfcheck 27
> modules; map fix proven at spec level (yard gone from TESTHUB inject set). **NOT DEPLOYED** (Levels+
> Quests integration coupling; TESTHUB rebuild + blob-diff/navmesh-24 is the ship-operator gate). Class
> sweep: 8 truly-unbounded records are all base/dead/test (none placed-boss); round-2 = promote the
> sweep to a build gate + refresh stale `gate_build32_parseback.py`. Report:
> `docs/reports/b76_chumbi_freeze_rca.md`.

> 🩸 **b82 BLOOD-CAVE DETERMINISTIC CRASH - RCA round 2 (2026-07-16), branch `fix/bloodcave-crash`.**
> Will (P0): "some item in the blood cave is not wired right; every time I go to that same area the
> game crashes." **VERDICT (unchanged): no single broken-wiring offender found in this lane; forensics
> point at a MAP-STRUCTURAL Engine.dll navmesh-load condition, not a dangling item.** (1) The Jul-13
> native dump's `GAME::RegionId::Write / ZoneManager::~ZoneManager` labels are WRONG - the faulting EIP
> 0x5fe4e270 is inside Engine.dll (base 0x5fc40000, size 0x39b000): runtime RVA = 0x5fe4e270 - 0x5fc40000
> = **0x20e270** (equivalently preferred-image VA 0x1020e270 = default base 0x10000000 + RVA 0x20e270;
> round-1 mislabelled the preferred-VA as the RVA); ~0x196d0 past ProcessRLTD (RVA 0x1f4ba0). Game.dll
> (base 0x5f6a0000, size 0x591000) ends at 0x5fc31000, BELOW the fault, so the Game symbols are
> misattributed. Corroborates the prior WER `ProcessRLTD` co-residency RCA
> (docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md). (2) The parchment `numberOfPlayers*1` loot-equation
> suspect is REFUTED: RunEquation parse-fails are BENIGN (engine falls back; game logs confirm), they
> reduce spawns, not crash. (3) GATE `tools/contracts/gate_placed_record_resolution.py` rules out the
> placed-record **NON-EXISTENCE** class (narrowed from round-1's overstated "unresolvable asset"): **743
> globally-distinct** placed-record refs (1096 counting per-blob duplicates) across 44 blood-cave-cluster
> level blobs ALL EXIST in mod+base arz (PASS). NEW: transitive `--chain` walk (16,487 records, 13,627
> asset refs, 189 dangling child refs) proves every dangle is the engine-log-and-continue class (67
> skills / 6 effects / 40 loot / 12 disabled / 64 base; the lone SV dangle = cosmetic
> `effects\sv\refnat\spirit_arrow` projectileWeaponTrail, not the crash). WIRED into the map-contracts
> battery as **MAP-BCREF-1** (contracts_map.py, green). Negtest HARDENED to a real planted-blob
> end-to-end test. Concrete candidate fix-surfaces (q_bloodtoxeus proxies/pools/chest + Toxeus kit; boss
> placements/co-residency) RESERVED to `fix/bloodtoxeus-spawns` + `fix/chumbi-lag` -> HANDOFF, no edit.
> NO .arz/.map change (arz md5 917d9047 unchanged). Report: `docs/reports/b82_bloodcave_crash_rca.md`.
> **DEBT / NEXT ROUND (blocked on Will):** needs Will to name the exact chamber OR a Frida ProcessRLTD
> ENTER/LEAVE run (docs/crash/WILL_CRASH_PROBE_GUIDE.md) OR full Page-Heap on TQ.exe to pin the corrupting
> co-resident navmesh load; if H1 confirmed the remedy is CAVE_ENTRY_CHAIN_TRACE.md Fix B (map-structural
> cluster relocation, map lane).
> 🟢 **B81r2 PET IDENTITY PASS round 2 (vet NO-GO on round 1) - FIX COMPLETE + SCRATCH-VERIFIED,
> SUPERSEDES round 1 below.** Round-1 vet: the 57 `_build_boss_summon` pets were clean, but the
> round-1 report's "every summon's vox cry now matches its own body" claim was FALSE - a SECOND,
> older Lyia-cloning lineage (7 standalone `_create_X_pet_skill` builders: Boneash/Narok/Vort/
> Pharaoh's Honor Guard/Blood Witch High Priest/Lil'Lued/Rakanizeus, 21 pets) never got
> `_align_pet_identity` wired in. **FIX:** same proven mechanism, called from each of the 7
> builders' existing anim/skill-copy site (race was already correct in all 7; only
> distressCallGroup + sound paks were Maenad residue). Also audited (per vet's suggestion) the 3
> remaining upstream-native (non-our-code) SV 0.98i pet families: Aletha Darkclaw = genuinely
> Maenad (source IS a Maenad, byte-identical match, correctly untouched); Helike = live +
> player-reachable, new standalone `_align_helike_identity` call proves 0-diff (already correct -
> confirmed, not fixed) + now gated; Phagia = orphaned (summon_phagia has zero live grant path
> since build36's Meritamen repoint), registered as BACKLOG debt, not fixed (no player symptom).
> **GATE:** `enslaver_pet_fx.verify()` gains a second roster leg (`_SECOND_BUILDER_ROSTER`, 8
> families/24 pets incl. Helike) reusing the SAME `_race_and_voice_problems` unchanged; 2 new
> negative tests (plant Beastman race on Boneash / Maenad voxSound on Narok) FAIL as required (7/7
> total negatives green). Scratch md5 `e77846c3a43cadbfc5af0720ce0fa8ef` (idempotent x2);
> record-diff vs round-1 baseline `f639ba409562a334add231956637ac71` = **0 added / 0 removed / 21
> modified** (exactly the 7x3 fixed pets, `characterRacialProfile` untouched on all 21 - confirms
> race was already correct); B-SUMMON-1 STRICT 0 (279 chains/253 pets, run with base+upstream args
> - identical to round 1); contracts run identically both builds in this worktree (no `Resources/`
> dir here, so absolute counts are environmentally inflated/uncomparable to a live deploy, but the
> DELTA is what's asserted): IDENTICAL totals both runs (19168/96P0/7244P1/11828P2) => 0 new;
> A7 golden PASS (84 waived, unchanged). Report: `docs/reports/b81_pet_identity.md` (ROUND 2
> section appended). Will test: same as round 1, now covering the 7 additional families too.
>

> 🟢 **B81 PET IDENTITY PASS round 1 (Will 2026-07-16, "Toxeus...is a beastman not a skeleton",
> satisfies R-11) - FIX COMPLETE + SCRATCH-VERIFIED.** Branch `fix/runtime-green` (on top of b75
> `2a2139d`). Root cause: every `_build_boss_summon` pet is a Lyia Leafsong clone; Lyia's own
> donor lineage is MAENAD (`characterRacialProfile=Beastman`), so every un-overwritten identity
> field on every pet still reads Maenad regardless of the pet's true body (skeleton/demon/
> construct/etc). **FIX (upstream, all 19 families / 57 pets, incl. Devourer/Hades Marshal/
> Neferkha via the shared `_build_boss_summon`):** new `_align_pet_identity` copies
> `characterRacialProfile` + `distressCallGroup` + the 7 alert/criticalHit/death/rally/rampage/
> stun/vox sound-pak field-groups VERBATIM from each pet's OWN source monster field-by-field
> (source defines it -> copied; source lacks it -> Maenad residue STRIPPED, never left dangling);
> Meritamen correctly KEEPS her source's own "Maenad" distressCallGroup (source-faithful, not a
> hard-coded exception). Toxeus the Enslaver now reads Undead (Will's literal ask).
> **NOT touched (documented):** the pet-behavior AI controller (`controllerAggressive/Defensive
> = controller_maenadmerc_*` - a different field/contract than the source's MONSTER controller,
> swap risks behavior regressions) and dormant Maenad loot refs (equipment/loot-class, out of
> pet-field-law scope). **GATE:** `enslaver_pet_fx._verify_chain` extended with a race/voice leg
> for the 3 formally-gated families (pet race == own source race; no Maenad residue unless the
> source itself is Maenad); 2 new negative tests (plant Beastman race / plant Maenad voxSound)
> both FAIL the gate as required. Scratch md5 `f639ba409562a334add231956637ac71` (idempotent x2);
> record-diff vs the b75 baseline = **0 added / 0 removed / 57 modified**, 0 collateral;
> contracts IDENTICAL totals (0 P0/576 P1/10717 P2, 0 new); B-SUMMON-1 STRICT 0; A7 golden PASS
> (84 waived, unchanged). Report: `docs/reports/b81_pet_identity.md`. Will test: restart Steam,
> DISMISS + RE-SUMMON any already-active pet, check the character sheet race + listen for the
> voice on alert/death/stun.
>

> 🟢 **B75 RUNTIME-GREEN (Will 2026-07-16, 3rd "still green" report) - FIX COMPLETE + SCRATCH-VERIFIED.**
> Branch `fix/runtime-green`. RCA: the Enslaver's green is NOT a DB field/chain/skill (all three scans
> green-free) - it is the SHROUD ASSET. The boss + soul pets wore `svc_enslaver_darksmoke -> 343_dark_smoke
> (SVEffects/ambient/dark_smoke.pfx)`, which attaches to the WEAPON bones with NO `emitterType=Standard`
> (not a whole-body shroud) and whose `.pfx` reads GREEN - one layer BELOW the DB, the last blind spot after
> fields (b55) + chain (b71). **FIX:** boss `um_toxeus_enslaver_99` shroud -> the marauders' PROVEN-black
> `drxshadowcloakrunning_fx_pak` (emitterType=Standard, Will-confirmed black; the soul pets inherit it);
> dead `svc_enslaver_darksmoke_charfxpak` clone removed. **CLASS FIX:** new upstream
> `_strip_lyia_clone_green` in `_build_boss_summon` strips Lyia-clone green residue
> (envenom/heartofoak/regrowth/natureswrath/Lyia-arrow/maenad-skin) SOURCE-FAITHFULLY from EVERY boss
> summon (54 pets / 15 families) - anti-oscillation. **PROTECTED:** the Devourer `bloodtoxeus_1-3`
> (`protect_green=True`, Will "green stays" + EoAT lane owns its poison). **GATE:** `enslaver_pet_fx.verify`
> extended with a TRANSITIVE skill-list green sweep (leg 3) + negative-tested. Scratch md5 `baa76edb`
> (idempotent x2); record-diff vs build45 `917d9047` = 1 removed + 55 modified, all intended, 0 collateral;
> contracts 0 new P0/P1/P2; B-SUMMON + render-chain + validate_tags + A7 golden all PASS. **FLAGGED:**
> (a) diadochi generals use the same 343_dark_smoke shroud - may read green too (other lane);
> (b) EoAT lane to decide the Devourer pet's green->black poison. Report:
> `docs/reports/b75_runtime_green_rca.md`. Will test: restart Steam, DISMISS + RE-SUMMON the Enslaver.
>

> 🎯 **B85 - HIGH PRIEST SUMMON (R-43, Will 2026-07-16 verbatim: "the high priest soul should allow
> you to summon the high priest") - IMPLEMENTED, awaiting independent vet.** Branch `fix/soul-tiers`
> (extends b78 tip `50d4bdfc`). RCA: the granted summon spawned a Melinoe blade-dancer (Demon race,
> `discipleboss_bladedancer.dbr`) - the monster HE casts as his OWN combat summon
> (`discipleboss_summon_melinoe`, petLimit 18/burst 6) - never his own body (`c_disciple_miniboss.dbr`,
> God race, `disciple.msh`/`anm_seductress`/`snd_highpriest_vox/alertpak`). **FIX** (mirrors the b71
> Enslaver boss-pet + tamed-pet-of-pet pattern exactly): `bwpriest_1/2/3` rebuilt via
> `_build_boss_summon(source=c_disciple_miniboss)` = the High Priest himself, strictly tier-scaled
> (life 4800/6800/9000, charLevel 39/56/71); his real signature blade-dancer summon survives as a
> NEW tamed non-player-facing pet-of-pet (`bwpriest_attendant_1/2/3` +
> `svc_bwpriest_summonmelinoe.dbr`, petLimit 2/burst 1/mana 0 - inside the Enslaver's proven pet-of-pet
> depth, not the raw 18-pet swarm); the source's own AOE (`disciple_bloodrain`, flagged
> `isPetDisplayable=0` on ITS OWN record) is swept off, never granted to a pet; race/sounds copied
> explicitly (R-11 general law, not auto-applied by `_build_boss_summon`); Lyia-clone green residue
> stripped; granted-skill icon `bonefiendup` (a DUPLICATE of kravmoloch's icon) -> `bloodbathup`
> (distinct); pet-bar portrait -> neutral `proxy_party` (no bespoke art ships); 3 text tags rewritten
> + 3 minted. Soul RING records (`bwpriest_soul_{n,e,l}`) UNTOUCHED - byte-identical, b78's
> strict-progress gate still governs them. Family added to the b71 CHAIN gate roster
> (`enslaver_pet_fx._CHAIN`, NOT `_FAMILIES` - that list requires a shroud this family doesn't have).
> **Verified:** full scratch build EXIT 0, all 17 registry verifies green incl.
> `enslaver_pet_fx.verify` + `souls_quality.verify` ("b78 Blood Cult High Priest gate"); record-diff
> vs golden `917d9047` = intended-only (4 ADDED + 4 MODIFIED, 0 REMOVED, soul rings absent from the
> diff); `validate_summon_pets.py` PASS; `validate_tags.py` PASS (all 349 mod tags + 409 authoritative
> resolve); `run_contracts.py --only souls,summons` GATE PASS (0 P0/P1); 4/4 negative tests (Lyia
> portrait, green residue, re-pointed grant, x2 more) all CAUGHT by the chain gate; idempotent (2
> independent builds, arz md5 `47964fdd` both). Epic-spawns-epic answered with a 3-row stat table
> (docs/reports/b85_highpriest_summon.md sec 5). `docs/WILL_RULINGS.md` is absent on this branch's
> base (predates the ledger's creation on `main`); the R-43 status line to apply at merge time is in
> the report's \S9. Report: `docs/reports/b85_highpriest_summon.md`.
> 🎯 **b78 SOUL TIER SCALING (Will 2026-07-16, "Blood Cult High Priest epic == normal?") - RCA:
> FALSE ALARM, roster CLEAN, GATE TIGHTENED.** Branch `fix/soul-tiers`. RCA: `svc_uber\bwpriest_soul_
> {n,e,l}` is correctly scaled on every dimension (augments 2/3/4, itemSkillLevel 1/2/3 with 3 real
> summon pet tiers, Int 6/9/12, Life 10/14/19, leech 20/30/42) AND its loot triple on
> `c_disciple_miniboss.lootFinger2Item1` = `[_n,_e,_l]` drops the right tier per difficulty. Will's
> perception = the item NAME + DESC tags are byte-identical across tiers + TQ bakes item stats at
> pickup (drop a FRESH epic to see the scaling). ROSTER SWEEP over golden `917d9047`: 775 tier
> families, 706 full-3-tier, **0 flat, 0 wrong-tier-loot, 0 real missing tiers**;
> `soul_strict_progress.py` = **706/706 strictly progress**. The first-pass "28 flat / 69 missing" were
> probe artifacts (curated stat subset missed fields like defensivePhysical/racialBonusPercentDamage;
> SV098 ships all 28 scaled) + noise (soultemplate / test\ / any*soul formula pools / malformed
> double-suffix dupes). **CHANGE = GATE-ONLY (zero record edits):** `souls_quality.py` gains a
> roster-wide STRICT-progress gate (`_flat_tier_violations` + `_power_vec` + `_tier_progresses`, wired
> into `verify()`) - every full-3-tier family must get strictly stronger n->e AND e->l on some scaled
> stat/skill-level field, closing the old non-strict `n<=e<=l` blind spot (a byte-identical epic USED
> to pass). `_FLAT_TIER_WAIVER` EMPTY (nothing needs waiving). Negative test
> (`souls_quality.py --negtest`) plants epic==normal -> flags n->e -> PASS. `flat_tier_count=0`. WILL-
> CONFIRM: none. Out-of-lane flags: malformed cyclops/vulture duplicate soul records (hygiene);
> Cold Worm = its own lane. Report: `docs/reports/b78_soul_tier_scaling.md`.
> 🎯 **b77 MASTERY UNLOCK-ALIGNMENT FIX WAVE (round 1, Will 2026-07-16 greenlight) - IMPLEMENTED +
> FULL-BUILD VERIFIED GREEN, AWAITING VET + WILL DEV PASS.** Branch `fix/mastery-unlock`. Implements
> the confirmed b74 audit: every mastery button's real unlock gate (skillTier threshold) now matches
> the row it is drawn on. New registry module `tools/patches/mastery_unlock_alignment.py` (apply+verify,
> registered LAST among mastery-UI writers after `mastery_sv_alignment`) + permanent gate
> `tools/gate_unlock_alignment.py` (wired into `build_svc_database.py` after the A7 golden guard; 13
> SV-faithful REQ-EXCEEDS-ROW waivers; negative test passes). Fixes all 14 tier-drifts + the 1 broken
> button across m1/m2/m3/m4/m7 (Occult m5 + Hunting m6 golden UNTOUCHED). Scope: A Spirit Distortion-Wave
> GT-rows (shared Dream records -> FIX-ROW; Death Chill Aura mods relocated col3->col4); B Defense/Storm
> gate leans (summonphalanx t7->5, frostnova t6->5, lightningdash t5->7); C Warfare col3 restack
> (ClubSlam+Fissure adjacent bottom pair, Lasting Legacy ultimate @r7, Hamstring aligned in col4 r4) +
> ClubSlam off-grid-bar repair; D Earth col4 in-place re-tier (SoftenMetal t2 / Rupture-restored t3 /
> Burning t4 / SpontCombust t6 / FireNova t7) + 2 bar repairs; E Storm skill25 broken button RETIRED
> (dangling `drxspellbreaker_spellshock2`; sole variant already live as Inversion). **Build:** scratch
> DB build SUCCESS, **arz md5 `7718d5841810034e73e7c1dfdc68788a`** (vs build45 ref `917d9047`).
> **Verification:** A7 golden PASS (84 waived/0 other); unlock-alignment gate PASS (238 live buttons, 0
> drift, 13/13 waivers) + negtest PASS; record-diff vs 917d9047 = **exactly 22 records** (positions /
> skillTier / connOn-Off / 3 panectrls), 0 added/removed, NO gameplay stat fields, NO SkillTree records;
> 9 live SkillTree records slot-order identical (bindings intact); contracts souls/summons/resources
> **no new P0/P1** (baseline == wave: 0 P0 / 576 P1 / 10717 P2); validate_tags PASS; idempotent.
> Every judgment is a WILL-VETO line in `docs/reports/b77_unlock_alignment_fix.md` (the two ladder
> diagrams, the E decision, the waiver list) for Will's DEV visual pass. DB-only wave (no map/quest).
> 🖤 **b83 ROUND 2 (vet HIGH/MEDIUM/LOW RESOLVED).** The adversarial vet found the Devourer's
> player-summonable soul-pets `bloodtoxeus_1/2/3` still carried `buffSelfSkillName =
> records\skills\stealth\envenomweapon.dbr` (base GREEN, tint (0.25,1.0,0.25)) - a LIVE auto-self-buff
> that round 1's rewire (skillName3 only) missed, so the summoned Devourer still glowed green (defeats
> R-1 on the summon). **FIX:** `_rewire_devourer` now also repoints the 3 pets' `buffSelfSkillName`
> (base-green -> `svc_black_poison`), and `black_poison.verify` now asserts `buffSelfSkillName` on all
> 3 pets (fails on either crimson OR a surviving base-green envenom - the blind spot is closed, proven
> by a targeted negative test). MEDIUM: corrected the overstated "proven/confirmed-dark" 343_dark_smoke
> wording in the docstring + report to the honest BP-SMOKE-1 hedge (rule 3 - the particle render is NOT
> colour-confirmed; the tint is the load-bearing black). LOW: corrected the "~2%" supra-formula
> drop-weight to the decoded per-act table (weight 1-5 by act/difficulty). **ROUND-2 VERIFY:** changed
> arz md5 **`497073d10041a9d38e553a2ab708f206`**; diff vs round-1 changed = EXACTLY the 3 pets'
> `buffSelfSkillName` (nothing else); diff vs clean baseline = exactly 17 delta (intended-only);
> 29 registry verifies GREEN incl. extended `black_poison.verify`; contracts identical (0 new);
> negative tests PASS (incl. the new pet-buffSelf blind-spot test); idempotent (2nd build byte-identical).
>
> 🖤 **b83 BLACK POISON + RITE DROP (Will ruled 2026-07-16, R-1/R-9/R-13) - ROUND 1 IMPLEMENTED +
> FULLY VERIFIED.** Branch `feat/black-poison` (merge of vetted `feat/toxeus-champions` +
> `feat/toxeus-undivided`, merge `2f52507`). Report: `docs/reports/b83_black_poison_rite_drop.md`.
> **(R-1) BLACK POISON:** new registry module `tools/patches/black_poison.py` (slot before
> `toxeus_endofallthings`) builds `svc_black_poison` (envenom lineage, cloned from the Devourer's
> crimson `bloodtoxeus_envenomweapon`): weapon tint (0.1,0.1,0.1) = the shadow-enchant-proven darkest
> RENDERABLE tint (empirical model: tint is additive-emissive, (0,0,0)=no-tint on 195 records, so
> black-LIGHT is unreachable -> (0.1,0.1,0.1) is the darkest black, identical to shipped
> `hero_shadowenchantmentbuff`); dark-smoke weapon pak `svc_black_poison_charfxpak` (343_dark_smoke on
> R/L Hand); poison (90/5s) + added vitality-decay (60/5s). Rewired onto the Devourer poison surface
> (`um_bloodtoxeus_99` initialSkillName+skillName3; `bloodtoxeus_1/2/3` skillName3) + the EoAT pet buff
> (`toxeus_endofallthings._BLACK_POISON` const, flowing to 3 EoAT + 3 disciple pets). His crimson
> identity (skin/bloodboil/aura) untouched. **(R-9) RITE POOL:** the Rite formula added to
> `supra.dbr` + `supra_special.dbr` (b66 next-free-slot @ w100) -> drops wherever any supra weapon
> formula drops, at the rarest ~2% tier. **(R-13) RITE BOSS KILLS:** GUARANTEED 100% on-kill on BOTH
> Toxeus bosses via Misc4 (Enslaver free slot -> `svc_rite_guaranteed`; Devourer -> `svc_devourer_
> misc4_master` LootMasterTable yielding rant w100 + Rite w100, rant preserved); soul drops (Finger2)
> untouched. **CROSS-BRANCH FIX:** the first merged build crashed the shared record-index
> (`_RecordIndex._sync_names` append-only `name_lower` cache count-coincidence -> KeyError on
> `eoat_disciple_1`); fixed in `apply_svc_patches.py` (reconcile-on-count-change + self-healing lookup,
> ZERO output-record change). **VERIFY:** changed arz md5 `32e0f2f709de1ba6954c4a6362ecbf0c` (all
> gates + 29 registry verifies GREEN, golden guard PASS); clean baseline `532003ec...`; record-diff =
> exactly 17 records (4 added / 13 changed), zero collateral; contracts souls/summons/resources
> IDENTICAL clean-vs-changed (0 new violations); negative test PASS (green tint -> verify fails);
> idempotent (2nd build byte-identical). **DEBT (registered):** BP-SMOKE-1 (P2, Will in-game check -
> the 343_dark_smoke particle's final black-vs-green render per the rule-3 caution; tint-black is
> grounded + independent, one-line fallback); BP-RITE-VETO (100% on-kill on farmable roaming-rare
> bosses - confirm vs first-kill-only/reduced). Ready for independent vet.
> 🩸 **b79 BLOOD-TOXEUS SPAWN PATHS (Will 2026-07-16) - ROUND 2 (R-4 rename completed + report nits).**
> Branch `fix/bloodtoxeus-spawns` (off `feat/toxeus-champions` b73). Closes rulings R-1/R-2/R-3/R-4.
> **CHEST 100% RCA (R-3):** the "Esti's Hidden Chest" guard (drxBC2 `egg_blooddragon_pack`, 4.2u from
> chest) was re-architected at M15 to spawn Toxeus as the CHAMPION of `pools\egg_blooddragon.dbr` with
> `championChance=100 championMax=1` but `championMin` LEFT at 0. Because he is the champion (not a main),
> a zero floor does NOT guarantee him - the base game's proven guaranteed-escort pools (`xsq22_wave2`
> min=max=1, `xsq17_keres` min=max=2) all set championMin=championMax, whereas `arachnos_01_overseer04`
> (base, verified championChance=100 / championMin=0 / championMax=1 = the egg pool's exact shape minus
> the floor) still spawns its champion only SOMETIMES - the "occasional zone-trash champion" pattern (33
> base pools run championChance=100 with championMin=0; 148 guaranteed-escort pools set min==max). So the
> egg pool rolled 4 blood dragons + NO Devourer most runs. Born broken at M15 (2026-07-09); NOT the
> q_bloodtoxeus_lone_50 retirement (that was the parchment @50, never the chest chain). **FIX:**
> `apply_svc_patches.py` `_apply_m15_toxeus_group_joins` sets `championMin=1` ->
> exactly 1 Devourer + 3 dragons, 100%, every party size (proxyPoolEquation already neutralized). **PARCHMENT
> (R-1/R-2):** the single 33% `q_bloodtoxeus_ambush` (reuses `_BT_POOL` = Toxeus + 2 blood-demon guys)
> was placed in drxFirstRoom - a DIFFERENT room from the tattered parchment (finalletter @ drxFirstxistion_
> connection amid the native demon swarm). RELOCATED the placement (map lane, `build_section_surgery.py`)
> to drxFirstxistion_connection @ (36.0,10.005,19.5) next to the parchment; EXACTLY ONE 33% roll (moved,
> not added). **RENAMES (R-4, ROUND 2 COMPLETE):** `build_text_arc.py` tagSQECTitle + tagTitleTagTESTER ->
> "Toxeus the Murderer, Devourer of Blood's Stash"; tagHiddenChestNAME (only the 3 chest
> tiers use it) -> "Toxeus the Murderer, Devourer of Blood's Hidden Chest"; **round-2 added tagSQECFullText**
> (the reward-popup body, which round 1 missed - it still read "You found Esti's hidden chest.") ->
> "You found Toxeus the Murderer, Devourer of Blood's Hidden Chest." (suffix "^n^W&BRewarded : ^n&S^rMythic
> Formula" byte-preserved). Built-Text.arc sweep: ZERO "Esti" occurrences in the shipped modstrings.txt
> (the only "Esti" substring anywhere in the SV source is the unrelated base word "Estimated time left"
> in install.txt, which the build does not emit). **VERIFY:** base scratch arz `5a8947ff`, fix scratch arz `fcc8b46e`
> (unchanged - round 2 touched Text only), EXIT=0 (champion-cap gate + all registry verifies GREEN);
> record-diff base->fix = EXACTLY 1 record `pools\egg_blooddragon.dbr` championMin 0->1 (0 added/removed,
> nothing else); contracts = pre-existing baseline only (championMin = no new P0/P1); static INJECT_SPECS
> = exactly one ambush placement, relocated; Text.arc duplicate-tag gate + A7 golden + validate_tags GREEN
> (tagSQECFullText resolves as mod-owned). Report `docs/reports/b79_bloodtoxeus_spawns.md`.
> **DEBT:** full canonical+TESTHUB map build + blob-diff (drxfirstroom + drxfirstxistion only, navmesh
> 24/24 identity, QUESTS untouched) = integration-gate step. Parchment coord
> (36.0,10.005,19.5) sits 1.5u from a proven native on-mesh spawn; final on-mesh = Will's walk test.

> 🩸 **b73 TOXEUS CHAMPIONS KIT WAVE (Will 2026-07-16) - ROUND 1 IMPLEMENTED + SCRATCH-BUILD GREEN.**
> Branch `feat/toxeus-champions`. Registry module `tools/patches/toxeus_champion_kits.py` (apply+verify,
> slot 9/27, after `toxeus_suite`, before `boss_skill_fix`). Gives the FOUGHT Toxeus champions signature
> kits from EXISTING DB skills (no pets/souls/pools/map). **DEVOURER OF BLOOD** (`um_bloodtoxeus_99`):
> Tears of Blood (weak, 10s cd) = new `svc_devourer_tearsofblood` (clone of the Blood-of-Ares artifact
> skill, dmg cut + cd 120->10) REPLACING the off-identity `flashpowder` @ specialAttack2; + Blood Frenzy
> (`quak_bloodfrenzy` low-health passive). **ENSLAVER OF SOULS** (`um_toxeus_enslaver_99`): the 3 generic
> specials become Soul-Rip (new `svc_enslaver_soulrip`, healing soul-drain), Chains of Servitude (new
> `svc_enslaver_dominate` (+`_buff`), short confusion+fumble+slow), Unholy Dominion (`unholy_rally`
> ally-buff); `summonmarauders` + `lethalstrike` kept. **GROUND TRUTH:** the corridor ambush AND the deep
> waterfall boss share ONE record + ONE pool (`pools\q_bloodtoxeus_lone`), so both get the one (weak-10s)
> Tears; a distinct full-strength corridor version = a monster+pool split, deferred as WILL-VETO #1. All
> new skills have `specialAnim=None` (castable on the shared anm_skeleton01 skeleton rig - the
> Ephialtes/boss_skill_fix law). **VERIFY (scratch arz md5 `0218d8127b8d8e0c8faa19498412315a`, EXIT=0):**
> module verify GREEN; record-diff vs build45 (917d9047) CLEAN (only the 4 new skills + 2 champions,
> 0 removed); `_verify_toxeus_champion_cap` GREEN (no pool touched); boss_skill_fix roster scan GREEN;
> all 18 registry verify hooks GREEN; souls contract 0 viol; summons contract 96P0/556P2 = IDENTICAL to
> the build45 baseline (0 of my 6 records in any violation = zero new P0/P1); negative test ALL PASS
> (4 planted regressions caught). Report: `docs/reports/b73_toxeus_champion_kits.md` (WILL-VETO list of
> 8 items + weakening math + balance). Ready for vet/integration; Will DEV-tests the fights + FX colour.

> 🐉 **b72 TOXEUS, END OF ALL THINGS (Will ruled 2026-07-16) - IMPLEMENTER ROUND 1 COMPLETE + FULLY
> VERIFIED (awaits independent vet + the ONE open Will decision).** Branch `feat/toxeus-undivided`,
> module `tools/patches/toxeus_endofallthings.py` (REGISTRY, after `enslaver_pet_fx`, before
> `visuals`). A supra soul ring `{^F}Soul of Toxeus, End of All Things` crafted from the LEGENDARY tier
> of the 3 Toxeus souls (green-Greece + Enslaver + Devourer) summoning ONE permanent apotheosis pet
> `Toxeus the Murderer, End of All Things` (cloned from the proven Devourer pet). All 11 ruled kit items
> shipped: unlimited energy, max Nether Strike @0.5s, max Smoke Screen, the Galefury skill
> (`hunter_helm_galefury`), Tears of Blood (Blood-of-Ares nova @3s), Murderer's Edge + the Devourer's
> CRIMSON blood-poison (no literal black exists - flagged), Entropy aura, Blood Feast (leech +
> `melinoe_bloodboil`), "There is room in me" (Blood-Witch Disciple `c_disciple_42` thralls that summon
> bloodhounds - 3-DEEP chain flagged), "The Ending" (Manetho light-of-Ra flash + authored cataclysm
> damage; SunGaze anim cleared for castability), and Arrat's Corruption AOE (`um_ararat_36` mana-burn
> debuff nova). Stat ceiling = the Enslaver (60000 life / 500 handHit); EoAT Legendary EXCEEDS it
> (82000 / 620 / STR640 / DEX800). **TWO round-0-draft bugs fixed:** (a) formula was uncraftable (spear
> donor's reagent3 affix constraints left in -> a soul ring cannot match a weapon prefix; cleared them +
> the random artifact bonus so the 3 souls craft a deterministic soul); (b) equipment used invalid Pet
> slot field names AND direct player-unique pet-equip HARD-FAILS the B-SUMMON-1 shipping gate (uniques
> render naked on pets) -> supra pieces are NOT worn (kept the Devourer loadout), power baked as direct
> stats, all 8 pieces reported SKIPPED. **Scratch arz md5 `a6b896bd8d05673b8cfc37eecd6cfb4a`**
> (deterministic, built twice identical). Record-diff vs build45 (`917d9047`): exactly 16 NEW records, 0
> removed, 0 modified existing. Verification ALL GREEN: full build EXIT=0, all 27 registry verifies
> (incl the b71 enslaver chain gate now walking the EoAT chain), B-SUMMON-1 0 strict failures,
> validate_tags PASS, contracts souls/summons/resources 0 P0/0 P1 (no EoAT violation), negative test
> 4/4 caught. Report: `docs/reports/b72_toxeus_endofallthings.md`. **THE ONE OPEN WILL DECISION: how the
> player OBTAINS the `Rite of the Undivided` formula** (formula is craft-ready but its DROP is unwired;
> recommended = a Boss-locked drop from the Devourer superboss). FEASIBILITY FLAGS: depth-3 thrall chain
> (needs in-game confirm; fallback documented), crimson-not-black poison, Tears-of-Blood-as-specialAttack
> (not a true retaliation trigger), supra equipment engine-unsupported on pets.
>
> 🎯 **b59 SOUL DROP-RATE CUT 66->50 for RANDOMLY SPAWNING monsters (Will 2026-07-14) - ROUND 3 FIX
> COMPLETE + REAL-BUILD VERIFIED GREEN (2026-07-16).** Branch `feat/soul-drop-50`. **ROUND 3 (this
> session):** independent re-vet of the round-2 build (md5 `fd538e0c...`, byte-identical reproduction
> confirmed) found ONE more unintended regression of the SAME bug class: `boss_charon_39` (Charon Form 1
> donor) shipped at **25%** instead of its true, both-baselines-confirmed **66%** (build40 golden AND the
> build41 pre-b59 baseline both show 66) - the round-2 report's "0 records changed in any other class or
> direction" / "coincides with pre-existing rate, not a regression" claims were FALSE for this one record.
> **Root cause:** `create_uber_souls.py` mints `boss_charon_39`'s own soul via
> `MANUAL_OVERRIDES['boss_charon']` but its rate call (`soul_drop_rate(...)`, ~line 654) is NOT routed
> through the `_soul_release_rate` choke point (only `apply_svc_patches.py`'s helpers are, despite that
> function's docstring claiming create_uber_souls.py routes through it too) - so the naive `"\boss_"`
> path heuristic misclassifies this PLACED encounter as a farmable Act boss and cuts it to 25. The
> pre-existing Charon block in `_wire_missing_boss_souls` only ever re-asserted `_41`/`_43` to 66, never
> `_39` itself (never needed before, since pre-drop-50 `create_uber_souls` hardcoded 66 unconditionally).
> Swept all ~27 other `boss_`-prefixed `create_uber_souls.py` `MANUAL_OVERRIDES` entries against the
> golden: Charon is the ONLY regression (every genuine farmable-boss entry already has its real upstream
> soul wired before `create_uber_souls` runs, so its unpinned call never executes for them; the other 2
> `svc_uber`+`boss_`-path matches, Aithon/`bossarena.py` and Menoetes/`four_generals.py`, are later
> REGISTRY modules that correctly route `_create_soul(..., drop_rate=66.0)` through the pinned choke
> point regardless of any earlier miscalculation). **FIX:** re-assert `boss_charon_39` to 66 alongside
> `_41`/`_43` in the same block (unconditional, no `existing` guard); added the matching
> `_KNOWN_EXCEPTIONS` waiver. **GATE HARDENING (closes the MEDIUM finding mechanically):** new
> `_check_intended_diff_vs_golden()` in `verify_soul_drop_rates.py`, wired into `main()`, diffs the real
> built arz directly against the build40 golden and asserts every `chanceToEquipFinger2` delta is EITHER
> the intended 66->50 RANDOM cut OR a documented `_KNOWN_EXCEPTIONS` waiver - closes the "classifier
> itself produces the wrong value so LAST-WRITER never flags it" blind spot permanently, not just for
> Charon. **RE-VERIFICATION:** new decisive build (scratch, `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1
> SVC_NO_CACHE=1`) -> **55,351,216 B, md5 `e11ef4738f955fccadcde8353e3e2933`**.
> `verify_soul_drop_rates.py --gate` -> **EXIT 0, 0 unwaived mismatches** (19 documented, incl. the new
> `boss_charon_39` waiver), `boss_charon_39/_41/_43` all 66. **NEW hardening check:
> intended-diff-vs-golden = exactly 377 deltas, 377 intended, 0 UNINTENDED** (the literal proof the vet
> demanded). RANDOM_HERO@50 still exactly 377 (unchanged by this fix). TESTING mode unchanged (854->100,
> 426 gated stay 0). souls contract GATE PASS (0 viol). Cross-checked directly against build41
> (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, md5 `eb8bc377...`):
> `boss_charon_39/_41/_43` all read 66 there too. Report: `docs/reports/b59_drop_rate_50.md` section 11
> (+ corrections to sections 3/10). Ready for re-vet/integration.
>
> **ROUND 2 (superseded by round 3 above, kept for history):** Round-1 NO-GO (vet):
> `create_uber_souls.py` (called AFTER `wire_souls_to_monsters`) hardcoded `chanceToEquipFinger2=66.0`
> unconditionally for its brand-new souls, silently re-widening 21 of the 377 intended cuts - the dry-run
> replay gate couldn't see a DIFFERENT function clobbering wire_souls' output. **FIX:** every soul-wiring
> helper in `apply_svc_patches.py` + `create_uber_souls.py` now routes its PLACED-default chance through
> ONE choke point (`_soul_release_rate` -> `build_svc_database.soul_drop_rate()`/`soul_spawn_provenance_
> sets()`, the same single source of truth); `verify_soul_drop_rates.py` REWRITTEN to LAST-WRITER
> semantics (loads a REAL BUILT arz, checks the FINAL actual rate against the classifier, fails loud if
> pointed at a bare golden arz, `_KNOWN_EXCEPTIONS` visibly waives ~15 pre-existing hand-tunings, a
> planted post-wire-stomp negative test proves the gate catches the round-1 regression class). **Round-2
> continuation (this session) found + fixed 2 more instances of the SAME bug class, both invisible to any
> replay:** (1) `_place_orphan_monsters`/`_wire_difficulty_variants`/Blood-Sisters-loop called
> `_add_monster_to_pools` (which proves RANDOM) AFTER reading pool membership to set the rate - reordered
> to pool-first, and made the reassert unconditional (not just on newly-created souls) so a
> pre-existing-soul record (e.g. `um_frost_36`, wired by an earlier patch before ever being pooled) also
> gets reconsidered; (2) `_soul_release_rate` passed a blank classification instead of the record's real
> `monsterClassification`, so a `Quest`-classified pool-referenced record (the zzdev warband souls
> `n_mega`/`n_emgiec`/`n_vio`) could be wrongly cut to RANDOM(50) - fixed to read the real field; (3)
> `_wire_difficulty_variants`'s farmable-Boss variant (`boss_terracottamage_bandari_40`, real rate 25)
> now uses the FULL classifier (real boss/random/placed chances) instead of the RANDOM-only wrapper.
> **THE DECISIVE VERIFICATION:** one real full DB build (scratch output, `PYTHONHASHSEED=0
> SVC_RELEASE_DROPS=1`, upstream sources + real Steam base game) -> **55,351,210 B, md5
> `fd538e0c5f80e5a5212d70d544bb29d3`**. `verify_soul_drop_rates.py --gate` on that real arz -> **EXIT 0,
> 0 unwaived mismatches** (18 documented pre-existing waived), **RANDOM_HERO records shipping at 50%:
> 377** (the exact intended count, now true of the real OUTPUT not a model), **TESTING mode unchanged**
> (854 soul-droppers->100, 426 gated stay 0), all spot/override/stomp negative tests OK. **souls contract
> GATE PASS (0 viol).** Isolated record-diff of THIS session's fix (before-fix vs final build, same
> inputs): **exactly 16 records, all single-field `chanceToEquipFinger2`** - 13 corrected 66->50
> (`um_phagia_34/44`, `um_dapoyan_42`, `um_indrajit_42`, `um_vidja_43`, `um_frost_36`, `um_rong_40`,
> `um_vuji_41`, `um_yama_38`, `um_inkeyes2_45`, `um_rocksting_29`, `hero_sehr'tunkah_30/36`), 3 corrected
> 50->66 (`n_mega`/`n_emgiec`/`n_vio`), `boss_terracottamage_bandari_40` confirmed unchanged at 25
> end-to-end. ⚠️ **WILL-VETO knobs** `_SOUL_PLACED_OVERRIDE`/`_SOUL_RANDOM_OVERRIDE` (empty=pure roster
> verdict). ⚠️ **Sensitive cuts flagged for veto:** `um_legion_28` (directive OKs it), `um_toxeus_21`
> ("Main Toxeus"; superboss `um_bloodtoxeus_99` untouched at 25), `qm_aniketos_9/10/11`. Report:
> `docs/reports/b59_drop_rate_50.md` section 10 (superseded by round 3 above - see top of this entry).
> 🚪 **TRAVELERS-INTO-AREAS b62 SHIPPED (Will 2026-07-14 final design; quest/text-only, no map build) -
> report `docs/reports/b62_travelers_into_areas.md`.** Reachability sweep (read-only vs
> `local/Levels_merged_TESTHUB.arc`, Will's actual play surface right now per HANDOFF_LIVE_STATE) found
> exactly 3 truly SEALED SV areas: spartacryptlevel2 (Sparta Crypt), crypt_floor1 (Uber Dungeon), and
> the Secret Place's murderbossroom (crow bosses). **2 of 3 wired** (both already have a placed NPC on
> BOTH ends of the round trip): `svc_area_return_sparta`/`_uber` (outer, Athens catacomb / Maze03) each
> gained a SECOND boat-dialog trigger offering entry into their interior (new tags `tagSVCEnterSpartaCrypt`
> / `tagSVCEnterUberDungeon`, landings `(-5596,-2,-1410)` / `(-2438,10,-2450)`, both gate-verified on-mesh
> + collision-clear); `svc_testhub_return_sparta`/`_uber` (interior, already stranded there) had their
> destination list swapped from Helos+BloodCave to **origin** (the outer landing, primary) + Helos
> (secondary) - new tags `tagSVCReturnToAthensCatacomb` / `tagSVCReturnToLabyrinthDoor`. Zero new arz
> records, zero new map placements, zero new QUESTS registry entries (both ride the existing
> sv_commonmechanics host step). ⚠️ **CANONICAL NOTE:** the 2 interior return NPCs are ALREADY placed on
> canonical/Steam too (promoted during the build40 P0-A hotfix) and Quests.arc is NOT SVC_TEST_HUB-gated,
> so this return-to-origin change will also apply to canonical/Steam the next time canonical Quests.arc is
> shipped (a separate deliberate ship step) - judged a net improvement (more coherent than the vestigial
> Blood-Cave jump, still on-mesh/safe) but flagging since it touches shipped NPCs. **Investigated but
> DELIBERATELY DID NOT unify** the pre-existing Almyros/`portal_master_helos` divergent
> `tagSVCHelosToSparta`/`tagSVCHelosToUber` destinations (interior vs the hub traveler's outer door) -
> Almyros is canonical-only and IS the sole live canonical mechanism into these interiors today (no outer
> door exists there); redirecting him would have stranded canonical players (see report for the full
> analysis). **FOLLOW-UP QUEUED (not done): unseal murderbossroom** - it has NO placed NPC on either end
> (box-adjacency-proven isolated from the rest of Secret_Place), so an enter-offer without a paired return
> would repeat the 2026-07-12 P0 "no way back" bug; needs a map-lane NPC placement first, then the same
> quest-lane pattern applies. Gates extended: `gate_traveler_responds.facts_from_specs` (per-NPC dest
> override + enter-offer routes; `--specs` and `--specs --canonical` both PASS),
> `gate_travel_npc_invariants` (new T5c: 0 new records, 4 new tags resolve; full battery PASS),
> `gate_landing_clearance --wiring v1` (now also derives the 2 enter-offer landings live; 27/27 PASS
> against the TESTHUB map). Dry-run qst round-trip proof against the clean SVAERA
> `sv_commonmechanics.qst` in the report.
> 🧺 **B65 LOW-LIFT BATCH (round 1, 2026-07-15, `feat/lowlift-wave`, off main `c8883d6`) -
> 5/5 DONE, dry-run verified, NOT built/deployed.** Full detail: `docs/reports/b65_lowlift_wave.md`.
> **(1) SVAERA-ADOPT 5-set re-link** (`tools/patches/svaera_sets.py`): git-blame gate cleared (NOT
> an intentional strip - the 13 items ship straight from SV098i upstream, never had `itemSetName`;
> the 5 `drxset0{49,51,52,53,058}` grouping records are SVAERA's own invention, never grafted).
> Authored the 5 sets (SVAERA's exact bonus fields ported verbatim), minted `tagSetName049/051/
> 052/053/058` (our own numbering convention), re-linked `itemSetName` on the 13 shipped items.
> **(2) Two relics**: ground-truthed "the magenta turtle shell" = the proven Common `ItemCharm`
> Turtle Shell donor pattern (already cloned twice: D10 Emberscale, C5 Ereban Heartstone); "magenta"
> = the engine's Class=ItemCharm tooltip color, not a `{^F}` tag. Cloned it a third time for
> **"The Reveler's Ruse"** (Satyr Archer family `ar_archer_01-06`, bow-only, attack-speed+%pierce,
> `tools/patches/turtleshell_relics.py`). Dune Fiend **already has one** (Fiend Carapace, amgoz1
> SV098i-original) - verified FIRST per the backlog's own conditional; nothing new authored, a
> regression guard added instead. **(3) B-TOXEUS-STALKER-1**: Legendary-only fixed Endless Hunt
> (`tools/patches/toxeus_legendary_stalker.py`, the proven Hydra pool1/poolEpic1-empty +
> poolLegendary1 pattern, ground-truthed against `minobossproxy_aniketos`) reusing `um_toxeus_
> hunt_99` verbatim (same monster/soul as the roaming Hunt); map-placed in Hades Palace
> `hadespalace_floor04_04.lvl` local(38,45) (the least-crowded floor), surveyed on-mesh
> clr=100%/comp#1, dry-run-injected into a copy (navmesh byte-identical, +1 instance).
> **(4) Double-soul rulings**: Possessed Boar + Lillued fixed terminal-only (typo-twin dup /
> empty-husk soul retired, `tools/patches/double_soul_rulings.py`); Charon 39/41/43 + Hades 54
> left UNTOUCHED (byte-identical snapshot asserted); `legion_soul_stages`'s distinct-soul roster
> shrank 6->4 as designed. **(5) carrionlord**: `skill_quality.py`'s REASSIGN now sets
> controller=None directly (was ON_ATTACK, silently overridden later by souls_quality's manual-
> cast law) - both modules agree at the source now, zero collision, output byte-identical.
> Combined verification: aggregate record-diff +16/-6/~21 across the 4 DB modules; every module's
> `verify()` + the monolith's `_verify_mod_spawn_proxies_eligible` + `legion_soul_stages.verify()`
> all PASS on the combined db; `validate_soul_augments` exit 0 clean; `validate_summon_pets`'s
> BROKEN-entry list is byte-identical to the pristine golden baseline (0 new regressions, all
> pre-existing). `_check_registry.py` OK (20 modules). Rides the next integration build.
> 🖤 **B60 MASTERY PANE BLACK-BACKGROUND - FIXED (branch `fix/mastery-bg-render`, ships build42).**
> Will 2026-07-14: "the mastery skill selection screens STILL have a black background." RCA
> (per Will's directive: compare base game/SVAERA's render chain to ours - full detail
> `docs/reports/b60_mastery_bg_render.md`): the b37/b38 waves repointed each pane's *texture path*
> off the dead `SkillsPanel\...diablo` arc onto a real base-game `InGameUI\Skills\...tex`, but left
> the record's widget class as `BitmapSingle.tpl` (writes singular `bitmapName`) instead of vanilla's
> `BitmapUIAware.tpl` (reads plural `bitmapNames`) - the pane slot never reads `bitmapName`, so the
> texture resolves in the arc but nothing ever draws -> BLACK. Confirmed the SAME defect in both
> `local/baseline_build40.arz` (shipped Steam build) and the in-flight build41-work arz - a standing
> defect, not a regression. FIX: `tools/patches/mastery_bg_render.py` (registered after
> `hunting_occult_ui`+`mastery_ui_audit`) restructures all 18 live pane records (masteries 1-8 +
> Dream/9, base+reallocation) to `BitmapUIAware`+`bitmapNames=[mouse,controller]`, and repoints the
> 4 shared chrome records (undo buttons, cost/gold numbers) off the completely-unshipped
> `SkillsPanel.arc` onto their base-game `InGameUI\Skills\...` equivalents. New build-gate
> `tools/gate_mastery_bg_render.py` (resolution + BitmapUIAware structure, scoped to the 9 LIVE
> player masteries). Verified via isolated dry-run (no full DB/map build - build41 map building
> elsewhere): gate FAILS on the unmodified golden (46 defects, negative test), `apply()+verify()`
> touch EXACTLY the intended 22 records (18 pane + 4 chrome, zero collateral), gate PASSES on the
> patched copy (848/848 refs resolve, 18/18 panes BitmapUIAware). DB-record-only fix, no arc/Text/
> map change needed (every texture already resolves in base `InGameUI.arc`). Deliberately excluded
> (unreachable, still carry the dead ref): the `mastery 9\11-15-06\` ArtManager backup + the
> `scroll skills\masteries\earth\` DRX dev-leftover tree.
> 🏺 **SVAERA-ADOPT (APPROVED-CONCEPT recon, 2026-07-14, awaiting Will's picks).** Full audit of "what
> SVAERA has that we don't": `docs/reports/svaera_goodies_audit.md` (repro `scratch_audit/svaera_goodies/*.py`).
> SVAERA arz = **110,495 records** (live workshop install `2076433374`; NB the in-repo `reference_mods` copy has
> NO Database arz, only Levels/Quests - the `docs/reference_mods.md` "0 MB DB" line is wrong). **30,714** SVAERA
> records absent from our effective DB (OURS∪BASE=92,259); **all 30,714 are SVAERA-authored-new, 0 are SV098
> content we dropped** (clean proof our overlay covers 100% of SV 0.98i). **Finding (2) divergence = SKIP as a
> class:** SVAERA re-templated + rebalanced ~every common record (sampled monsters 120/120, weapons 120/120, every
> mastery 100% diverge from BOTH base and SV098 - the "Steam fork with nerfs"; no surgical-fix subset to lift;
> contradicts amgoz1 classic + Will's mastery hand-tuning). **The good vein is ADDITIVE content.**
> **HEADLINE ADOPT (S effort - ⚠️ CORRECTED by independent verifier 2026-07-14):** 5 thematic Greek/Egyptian
> sets - **Thoth's Favor** (`drxset049`), **Hector's Bronze Armor** (`drxset051`), **Robes of the Pythia**
> (`drxset052`), **Patroclus' Disguise** (`drxset053`), **Might of Hephaestus** (`drxset058`).
> **VERIFIER CORRECTION: the 13 member ITEMS are NOT absent - all 13 already ship in OUR mod, droppable via
> our loot tables, functioning as STANDALONE uniques** (itemSetName stripped; several re-tiered/re-tagged by
> our build, e.g. Hector pieces Epic->Legendary). Only the 5 SET-grouping records are absent. TRUE adoption
> recipe (smaller than originally stated): (a) add the 5 set records, (b) re-add itemSetName on the 13 shipped
> items (matches how our working sets drxset001/047 link), (c) port 5 set-name Text tags. NO item import, NO
> loot wire needed. ⚠️ OPEN QUESTION for Will/history: a PRIOR build deliberately stripped these set links
> (107 of SVAERA's 123 set records ARE in ours; these 5 + unused ones are the exceptions) - confirm the cut
> was not intentional + reconcile tiers (Hector Epic-in-SVAERA vs our Legendary) before shipping. **Tier 2 (M, flavorful):** The Hunting Paradox (`newset002`, Laelaps+Teumessian
> fox), The Elephantine Triad (`newset005`, Khnum/Anuket/Satis), curated Greek/Egyptian legendary uniques bundle
> (Meteorite, Scepter of Lamashtu, Stormcrack, Nature's Revenge, Sickle of Kronos, Osiris' Atef, Vengeance of
> Sekhmet, Symbol of Hathor - filter OUT Norse/Chinese) - gated by the **`_DRX_Meshes.arc` art lever** (we ship a
> GUTTED 858KB vs SVAERA's 430MB; un-gutting or a subset-arc unlocks ~146 Leg + ~3,077 Epic `u_mod_*` at once).
> **Tier 3 (M-L):** `sv_ew` Artemis bestiary (Moon Wolf ~ Hound of Artemis + Artemisian Oceanid nymphs) - fits
> amgoz1 monster-identity bible; art in unshipped `N66_Mods.arc`+`SV_NewSkins.arc` + needs map placement.
> **Tier 4 (QoL):** `NpcItemUpgrader` free-upgrade town NPCs (54); blood weapon-enchant FX (Toxeus theme).
> **DELIBERATELY-SKIP families:** all xpack2/3/4 (Ragnarok/Atlantis/EE DLC), `item\formulas` (11,364 economy),
> the §3 stat-override rebalance, SVAERA's own souls model (`\soul\*`+`soulskills`, conflicts with ours),
> `OneShot_Dye` dyes, `mod_allcaravans` (we have Super Caravan), `sv_endgame` crystal-hub, mercenary-scroll system,
> `game\svic` economy. **Permission precedent:** the SVAERA mastery graft (below, 2026-07-10) recorded soa's verbal
> OK for additive SVAERA use - confirm it covers items/monsters before ship. Verified 8/8 candidates end-to-end
> (truly absent + functional, not cut). **Recommended first wave: the 5 clean sets as one drop-pack.**
> 👑 **B56 LEGION SOUL-STAGES - one soul per death-transform encounter (2026-07-14, `feat/legion-soul-stages`,
> off main `f816ca6`).** Will: "the hero monster legion is dropping souls at multiple stages of his life as he
> dies and gets bigger." RCA (golden `b33c5a44`): **Legion is a 4-stage `actorToSpawnOnDeath` chain**
> (`um_legion_28 -> _28a -> _28b -> _28c`, all Hero L14) and **every stage** carries the identical soul drop
> (`chanceToEquipFinger2=66` + `legion_soul`) -> up to 4 souls per encounter; the 3 non-terminal stages even point
> _n at the broken "conflicted copy" path, only terminal `_28c` uses the clean `legion_soul_n.dbr`. Root cause:
> `wire_souls_to_monsters` arms every Hero stage independently (SV-original records; contradicts the uber-boss law
> = soul on FINAL form only). **FIX:** new registry module `tools/patches/legion_soul_stages.py` (after
> `boss_skill_fix`, before the no-op `visuals`): for any soul dropped by 2+ forward-reachable stages, keep the drop on the
> terminal-most stage and zero `chanceToEquipFinger2` on the shallower ones (loot refs kept inert, `_apply_aphiastas_
> finger2_zero` house pattern; dtype-safe). ORPHAN-PROOF (soul stays on a deeper stage). Runs before the drop-rate
> forcer (chance>0 gate) so the zeros survive release AND testing. `verify()` = no chain drops the SAME soul from
> >1 stage (fail-loud); negative test (re-arm `_28b`) trips it. **CLASS SWEEP:** 7 chains carry >=2 soul drops -
> ONLY Legion drops the SAME soul (FIXED); the other 6 drop 2 DISTINCT souls per encounter (possessedboar,
> base-Charon x3, base-Hades, lillued) and are **reported, NOT auto-fixed** (zeroing would orphan a distinct
> collectible / touch base-game story bosses = design ruling; see report). Inverse defect (empty chain): **0**.
> **VERIFY (dry-run replay vs golden, no heavy build):** record-diff = EXACTLY 3 records (`um_legion_28/_28a/_28b`
> Finger2 66->0), terminal + 6 distinct chains byte-identical, 51,029 records 0 add/remove; `verify()` PASS +
> idempotent + negative FAIL; `validate_soul_augments` golden==postapply PASS (0 dangling/0 inactive); contracts
> souls golden **0P0/0P1/0P2** == postapply **0P0/0P1/0P2**; py_compile + `_check_registry` (14 modules, order
> `fabf2d33cc81`). Report: `docs/reports/b56_legion_soul_stages.md`. NOT built/deployed; rides the next integration
> build (expected arz diff vs build40 golden = these 3 records only).
> 🩶 **SOULS FIX-WAVE-2 ROUND-2 (2026-07-14, `feat/souls-quality` @ souls_quality module, dry-run replay
> GREEN vs build40 GOLDEN arz `b33c5a44`; NOT built/deployed - ships in the next integration build).**
> Extends the `souls_quality` registry module (pos 13) per Will's directives + the round-1 vet feedback;
> all fixes proven by `tools/debug/souls_quality_replay.py` (**126 modified + 3 removed**, exact
> intended-only diff, field minimality, idempotent, **6 negative tests** incl. a roster-wide non-svc_uber
> one) + `validate_soul_augments` PASS + `validate_summon_pets` 3-arg PASS (byte-identical baseline vs
> patched) + targeted dangling-ref scan (0 residual refs) + `_check_registry` OK (14 modules, order
> `39d94e32`). **ROUND-2 = the crow-sweep HIGH + gate-scope MEDIUM from the round-1 vet (D3 below).**
> - **D1 RATIFIED - WILL-VETO CLEARED:** `bloodtip 5/7/9` + `gustleech 10/12/14` ship as-is (Will
>   verbatim). `_SV_INVERSION_FIX` block kept as the documented historical revert path.
> - **D2 Tomb Guardian (FIX 5):** `um_tombguardian_26` kept **Common** (NOT promoted, per Will); the
>   referenced-but-unobtainable `um_tombguardian_soul` DETACHED from its `lootFinger2Item1`, the 3 soul
>   records RETIRED, and the `tagSVCSoulTombguardian` tag dropped. 0 dangling refs. (Root cause:
>   `_place_orphan_monsters` wired it "against the Hero/Boss/Quest design"; future cleanup = skip soul
>   creation for deny-listed records, at which point FIX 5 no-ops.)
> - **D3 crow bug (FIX 4) - ROUND-2 WIDENED (resolves the round-1 vet HIGH+MEDIUM):** the crow reset every
>   attack because the ring auto-casts its permanent summon on-attack (`base_atenemy_onattack`) vs the Lyia
>   manual-cast (no-controller) convention. FIX = REMOVE `itemSkillAutoController`, now over a **ROSTER-
>   DERIVED 8-family / 24-ring set** computed vs the SV098 design bible (`_summon_controller_fix_records`),
>   NOT the round-1 svc_uber-only 4 families: **Category A** mod-only svc_uber `crowboar/glittertail/koroush/
>   nkac`; **Category B** SV-original rings the MOD gave a controller SV never shipped - `zombie\komara`
>   (Hero 66, OBTAINABLE), `zombie\melalos` (Boss 66, OBTAINABLE), `zombie\oythroneus` (gated),
>   `carrionbird\carrionlord` (skill_quality REASSIGN, gated). komara/melalos are the exact obtainable
>   same-bug rings round-1 MISSED (its "exactly 4 qualify / most drop-gated" claim was false). The **52
>   amgoz1 SV-original on-attack SWARM souls** (direflock, the skeleton/dead-raisers, nebtaan, senusnet,
>   menzus, bonelord, fenuku, frostmarrow, graklos, xiao, feira, aphiastas, ...) are amgoz DESIGN (SV
>   shipped the controller) -> LEFT INTACT, surfaced to Will. **carrionlord FLAGGED FOR WILL** (its
>   on-attack summon is a skill_quality reassignment; `_SUMMON_CONTROLLER_WAIVER` reverts it in one line if
>   it was meant as an on-attack crow-swarm). Shared summon SKILLS never touched; Pet.tpl-safe. Root causes
>   (follow-ups): `apply_svc_patches._AC_ON_ATTACK` on summons; `skill_quality` REASSIGN generic ON_ATTACK.
> - **D4 nymph icons:** `feat/b40-soul-icons` (`9db3f5f`) VERIFIED merges CLEANLY onto main (`git
>   merge-tree`, 0 conflicts, tree `c64ee9a`) -> **REQUIRED integration merge-set member** (fixes the 17
>   boss-summon skills sharing Lyia's nymph icon; disjoint from this module + FIX 4).
> - **D5 blatant-error sweep (155 MINOR-GAP):** only blatant DATA errors = the 2 icon classes (54 uniform
>   -> FIX 3 here; 17 nymph -> D4 branch), both covered. The 79 drop-gated + 5 formula-only + 2 pet-equip
>   dangles + 1 soulfeeder(false positive) = design decisions / upstream-faithful, LEFT documented.
> - `verify()` now fail-louds 4 classes (tier monotonicity roster-wide, svc_uber icon, **ROSTER-WIDE
>   no-mod-introduced-on-attack-controller on any permanent companion summon [SV098-derived, catches
>   non-svc_uber souls - the vet MEDIUM]**, tombguardian retired). One INTENDED cross-module collision:
>   skill_quality (pos 4) sets carrionlord's controller, souls_quality (pos 13) removes it (later-wins, S4b
>   WARN). Report: `docs/reports/souls_quality_fix.md` (+ audit round-2 corrections). **INTEGRATION MERGE
>   SET = feat/souls-quality + feat/b40-soul-icons** (both required; disjoint file sets, non-conflicting).
> 🗡️ **B64 THROWN-WIELDER RESTORE (2026-07-15, `feat/thrown-enemies`) - SUPERSEDES B58 below.**
> Will's design law: *"instead of us wiring them back into spawn pools and us deciding which pools
> to wire them into, cant we just restore them into the existing pools that they previously spawned
> in?"* + *"restore the ones that are in the expansions and then scale up them to match SV
> difficulty"* (DLC dependency confirmed acceptable). Independently re-derived the b58 "74 wielders"
> from scratch (b58's own probe scripts were session-ephemeral, never committed) via loot-table
> chase + a slot-1/3/5-identity filter (excludes ~49 incidental alternate-weapon monsters e.g.
> skeletons/dvergr) -> 75 records, minus 1 scripted non-wielder prop (`ss_porcusroh2_die.dbr`,
> zero pool membership anywhere) = **74, exactly reproducing b58**. Classified all 74:
> **(a) OVERLAY-DISARMED, restored in place, 10 records / 4 rigs** - Maenad02/DuneRaider01/
> TigerMan01 (b58's 3) PLUS **Machae{01,02,03}A.msh** (a b58 correction: filed as "DLC/unreachable"
> under the "xpack" no-digit Immortal Throne namespace without checking WHERE - ground truth: its
> own base `ProxyPool`s place it in Elysian Fields + Plains of Judgement, core reachable Hades-arc
> content, not a DLC bonus act). Restored the family's exact vanilla right(+left, dual duneraider)-
> hand equip/loot fields VERBATIM on the SAME overlay record (no clone, no new namespace, no new
> pool) - every one already sits in a real, unchanged base `ProxyPool` a real reachable level
> already places, so restoring the fields is the entire fix. **(b) POOL-MEMBERSHIP-LOST: NONE** -
> every DLC pool is `in_golden=False` (pure base pass-through), our mod never dropped a wielder from
> a pool. **(c) INTACT-BUT-UNREACHABLE: 64 records, NOT restored/placed** - Ragnarok Scandia/
> Corinthia/Germany/Asgard/Dvergr-Lands (46: aesir/troll/yerren/mercenary/celticbandit/greekbandit,
> incl. resolving b58's "Corinthia" residual - it's Ragnarok's OWN zone, nothing to do with reachable
> Greece) or Atlantis Outer-Atlantis (18: potamoi/monkeyman), both outside the standing IT-cap +
> A5-fix reachable set - reported with 3 options for Will, nothing invented. **SV-difficulty
> scaling**: ground-truthed Common-rank golden/base `characterLife` median = x1.20 (n=258 SV-touched
> monsters, wide per-monster spread 0.18-3.33x) vs Champion x1.26-1.30 (n=423); the 7 restored Common
> records (maenad/tigerman/machae) were verified UNTOUCHED since raw base AE (ratio 1.0, confirming
> the "under-tuned" premise) -> scaled x1.20 on `characterLife` (their only per-record stat field;
> OA/DA/STR/DEX/INT are template-inherited, absent on these records). The 3 Champion duneraider
> variants are ALREADY SV-scaled by a prior wave (golden/base ratio exactly 1.4x, all three,
> untouched by this module). Drop safety: exact vanilla N/E/L loot bands preserved; `chanceToEquip
> Finger2` verified 0.0 in base AND golden for all 10 (no soul leak). Orphan flagged:
> `am_assassin_15` is itself overlay-disarmed like its 21/27 siblings but has ZERO base ProxyPool
> membership anywhere (dead in vanilla TQ itself, not an SV regression) - restored for identity
> consistency, zero player-visible effect alone. **Module `tools/patches/thrown_restore.py`,
> REGISTERED** (unlike b58's `thrown_wielders.py`, which stays UNREGISTERED/kept-for-reference,
> docstring updated to point here) - in-place edits only, 0 new records (dry-run vs golden `eb8bc377`
> proves `db._modified` == exactly the 10 roster paths). Verified: `verify()`/`_negtest()` (8 broken
> shapes rejected) OK, `py_compile` + `_check_registry` (14 modules) clean, 0 collision risk
> (full-tree grep - only the unregistered old module also references these records, read-only as
> clone donors), contracts souls 0/0/0 clean (summons domain shows 652 PRE-EXISTING violations, 0 of
> which reference any roster record - confirmed by JSON search - caused by this worktree lacking the
> full `Resources/` art tree, not this module; map/resources/quests contracts need the 688MB Levels
> arc and were not run per the no-heavy-build constraint - this module makes zero map/Quests changes).
> Full per-wielder table + reachability options for Will = `docs/reports/b64_thrown_restore.md`.
> 🗡️ **B58 THROWN-WIELDER ARMING (2026-07-14, `feat/thrown-enemies`) - SUPERSEDED BY B64 ABOVE.**
> Kept for history (the invented-family approach; `tools/patches/thrown_wielders.py` stays
> unregistered). Original entry follows unchanged. Will's "we have throwing weapons but no
> enemy uses them" is CONFIRMED; 3-family arming built + fully verified, awaits Will's veto.** Verified read-only
> from golden arz `b33c5a44` + canonical Levels `9981085b` (+ stock TQAE / SVAERA cross-check): thrown weapons =
> `Class WeaponHunting_RangedOneHand` (191 recs, ALL xpack2/3/4 - a Ragnarok+ item class); **0 of the 74 monsters
> whose weapon slot resolves to a thrown weapon spawn in the reachable Act1-Hades+SV campaign** (per-level
> attribution; the sole campaign-namespace vector is a charLevel-37 Ragnarok Act-5 Corinthia slinger overlay our
> campaign never reaches). Throwing weapons DO drop as loot (the mod's `_restore_thrown_weapon_drops` - what Will
> sees), but no reachable enemy wields one.
> **ROOT CAUSE (ground-truth, corrects the first-pass audit): the base game DID ship genuine throwers on three
> REACHABLE-campaign rigs** - Maenad02 (`maenad\ar_archer_06`/`br_archer_10`, RIGHT=1h_ranged@100 / LEFT bow@0),
> DuneRaider01 (`duneraider\am_assassin_15`/`_21`, dual 1h_ranged@100), TigerMan01 (`tigerman\ar_archer_27`/`_33`,
> RIGHT=1h_ranged@100 / LEFT bow@0) - **but the SV/mod overlay DISARMS every one** (maenad/tigerman -> bow;
> duneraider -> melee) because the SV-classic roster predates thrown weapons. So the design gap is not "no rig
> exists" (the audit's HIGH-risk read of maenad); it is "the overlay disarmed the throwers that already existed."
> **FIX** `tools/patches/thrown_wielders.py` (registry module, **UNREGISTERED** so golden stays byte-identical):
> arms 3 identity-fit families x 2 tiers = **6 Common thrown-wielders** (Maenad Javelineer / Dune Raider Skirmisher
> / Tigerman Hunter) by cloning each family's base thrower (keeps mesh + full rangedOneHand/dualRanged anim block +
> ranged AI) then RE-AUTHORING the RIGHT hand with that family's exact VANILLA thrown block (static+monster+unique
> tiered N/E/L loot arrays at vanilla weights) + `chanceToEquipLeftHand=0` so the offhand bow/melee can't beat the
> throw. Drops banded to bow-wielders BY CONSTRUCTION (unique-thrown slot weight 4-5 = the same monster's bow-drop
> slot). +3 minority-flavor ProxyPools for the MAP lane. **Verification (dry-run vs golden b33c5a44 + adversarial
> vet): intended-only +9 record delta (6 monsters + 3 pools), 0 existing records mutated, all 6 = Common throwers
> on whitelisted rigs w/ anim block retained + no soul leak, base donors untouched, 0 INT/FLOAT round-trip
> corruption; `verify()` OK, `_negtest()` rejects 7 broken shapes (incl. left-hand-re-enabled), py_compile +
> `_check_registry` clean.** The veto artifact (verdict + evidence chain + armed-roster table + amgoz naming +
> open questions) = `docs/reports/b58_thrown_wielders.md`. **Rides the NEXT integration build** after Will vetoes
> the roster (report C) + the coupled MAP lane places the pool proxies among reachable Act-1/2/3 maenad/raider/
> tigerman packs at minority weight. Names are amgoz-pass + Will-veto pending (working copy).
> INTEGRATION PREREQ (reported): the monolith must import base donor `ar_slinger_37` into the overlay first (like
> `import_base_game_bosses`), since a registry `apply(db,tags)` only sees the mod overlay.
> ⚡ **BUILD-SPEED: PREFIX CACHE DEFAULT-ON (2026-07-14, main) - harness gate PASSED, default flipped.**
> `tools/verify_cache_determinism.py` ran on main @ `7c38c9e` (clean machine, no build contention, serial):
> **COLD** (SVC_PREFIX_CACHE=1 SVC_CACHE_REFRESH=1 SVC_RELEASE_DROPS=1 PYTHONHASHSEED=0, forced MISS+STORE)
> exit 0 in **209s**, arz md5 `b33c5a447f3a8ca652c14f78d4ad1dd4` == build40 GOLDEN (55,351,206 B), tags md5
> `fe855a77324e99cc37ea3326c0cdc2b2`. **WARM** (same env, no refresh) exit 0 in **134s**, log-proven HIT on the
> same snapshot, arz + tags md5s IDENTICAL. COLD == WARM == GOLDEN bit-for-bit; a HIT saves ~75s (36%).
> Graft-flip negative test: SVC_GRAFT_SVAERA=0 changed the key and forced a MISS (wrong-hit class proven
> guarded); the graft-OFF full build itself aborts in `mastery_ui_audit` on the absent graft record
> `records/skills/warfare/drx_clubslam_fissure.dbr` - a pre-existing graft-OFF/registry incompatibility, NOT a
> cache defect. On that PASS, `tools/prefix_cache.py enabled()` now defaults **ON**; opt out with
> `SVC_PREFIX_CACHE=0` (or off/false/no), `SVC_NO_CACHE=1` still hard-disables, `SVC_CACHE_REFRESH=1` still
> forces a fresh store. Key/fingerprint logic and the advisory miss-to-cold fallback are UNCHANGED - staleness
> is always a MISS (the key covers input arz md5s + prefix env flags + the whole tools/ source tree), so the
> flip cannot change output bytes, only time. NOTE: because tools/*.py content is in the key, committing or
> reverting any tools file changes future keys (safe MISS, one cold rebuild).
> ⚡ **BUILD-SPEED: RECORD-INDEX (2026-07-14, main) - biggest remaining DB win, BYTE-IDENTICAL.** The extended
> phase re-scanned all ~51k records on every `_add_monster_to_pools` call (~28 calls) and on the substring
> `_find_record`. New shared, mutation-invalidated `_RecordIndex` (in `apply_svc_patches.py`) computes the derived
> views once: `name_lower` (for `_find_record`), lowercased-value `blob` + `has_name` (for pool discovery), invalidated
> by a new zero-cost `ArzDatabase._mutation_listeners` hook (set_field/clone_record notify; empty for every other tool)
> plus structural new-record detection. Also **de-shadowed the dual `_find_record`**: the early exact-path resolver was
> DEAD (Python rebinds the later substring def at import, so every call already ran the substring/first-match version);
> removed it, kept the substring impl as the single canonical (byte-identical behavior). **PROOF (both full DB builds
> EXIT=0, SVC_RELEASE_DROPS=1, cache-refresh):** arz md5 `b33c5a447f3a8ca652c14f78d4ad1dd4` == build40 GOLDEN, bit-for-bit,
> before AND after. Text/Levels(canonical+TESTHUB)/Quests unaffected by construction (their tooling imports neither
> changed module). **DB build 330s -> 211s; extended phase 175.1s -> 50.6s (124.5s / 71% cut).** Equivalence unit-tested
> (`scratchpad/ridx_proto.py`, 25 seeds + 5 edge classes) and real-ArzDatabase integration-tested vs a reference copy of
> the original scans. Files: `tools/apply_svc_patches.py`, `tools/arz_patcher.py`.

> 🖤 **B55 ENSLAVER PET FX (branch `feat/enslaver-pet-fx`, dry-run vetted vs build40 golden `b33c5a44`; awaiting
> integration build). b55r2 (2026-07-14): sibling sweep corrected - added the missed Hades Marshal family; now 3
> families / 9 pets.** Will (2026-07-14): "toxeus the murderer enslaver of souls has green glow not black like we
> said ... this is when i summon him from his soul" + "his poison effect is still green, it is not the custom black
> one." **RCA (`docs/reports/b55_enslaver_pet_fx.md`):** b38 black-rigged the ENCOUNTER monster `um_toxeus_enslaver_99`
> (charcoal skin + `charFxPakRunningNames=svc_enslaver_darksmoke` + deleted its green weapon glow) - VERIFIED present in
> the golden arz. But the SOUL-SUMMON PET (`toxeus_enslaver_1..3`) + the friendly marauders it raises
> (`enslaver_marauder_1..3`) are built separately by `_build_boss_summon` (Lyia-clone base) and inherited Lyia's GREEN
> residue that no builder field-copy overwrites: `buffSelfSkillName=envenomweapon` (skillWeaponTintGreen=1.0 + green
> poison-weapon charFxPak = Will's "poison effect is still green"), `buffSelf2=heartofoak`, `healSkillName=regrowth_lyia`,
> `deathEffect=343_natureswrath` (+ marauder-only `specialAttackSkillName=sylvannymph nature'swrath`/`skillName8` +
> `baseTexture=maenad_lyia`), AND the pet was MISSING the boss's black-smoke shroud entirely. The shared boss/pet KIT
> skills (netherstrike/bladestorm/lifedrain/dream chain) are NOT green (encounter stays black - matches Will). **FIX:**
> registry module `tools/patches/enslaver_pet_fx.py` (pos 13, before `visuals`): strips the green residue (marker-
> matched) + inherits each pet's SOURCE-monster shroud (enslaver pets <- svc_enslaver_darksmoke, marauder pets <-
> drxshadowcloak, Hades Marshal pets <- hades2_shadowcloud); PET FX fields only, no clones/new records/textures.
> Added-shroud is crash-safe (string FX field, Pet.tpl superset of Monster.tpl, verbatim TypedField, no dtype) but has
> NO on-a-pet render precedent (0 of 51,029 golden records is a Pet w/ charFxPakRunningNames) -> non-green is guaranteed,
> black-SMOKE render to confirm in Will's test. **SIBLING SWEEP (corrected b55r2, ground truth):** EXACTLY 5 records
> carry a custom charFxPakRunningNames, ALL Monsters; EXACTLY 3 are `_build_boss_summon` soul sources whose pets kept the
> green rig = `um_toxeus_enslaver_99`/`um_enslaver_marauder_99`/`svc_um_hadesmarshal_80` (3 families / 9 pets). The other
> 2 shroud monsters have NO soul pet: `um_vashkarr_99` (STAT `_create_soul`, its summonhorde raises fodder not a
> vashkarr pet) + `boss_satyrshaman_55` (arena APEX, no soul). r1 asserted "exactly two ... and no other" - FALSE (missed
> Hades Marshal), corrected. Devourer `bloodtoxeus_1..3` (crimson) EXCLUDED - shares RevenantPoison mesh but its source
> `um_bloodtoxeus_99` has NO shroud (never retinted); its green poison is intentional and STAYS (Will). Broader ~77 pets
> (source never retinted) + the Maenad audio/AI/loot residue flagged for Will as a separate design call, NOT mass-fixed
> here. **ITEM vs PET:** FX rides on the PET records (live-resolved when the summon fires), NOT the soul ITEM - so Will's
> EXISTING Enslaver + Hades Marshal souls get the fix after a Steam restart; no fresh drop needed. **VERIFY (no heavy
> build):** dry-run replay vs golden = EXACTLY 9 pets modified, intended FX fields only, Devourer byte-identical; module
> `verify()` fail-loud (5 negatives on the Hades Marshal family all abort); summons + resources + souls contracts
> golden-vs-fixed = BYTE-IDENTICAL violation output (0 new violations; resources confirms the hades shroud ref resolves);
> py_compile + `_check_registry` (14 modules, order e64bc6e6 unchanged) green.
> 💠 **SOULS-QUALITY ROUND-1+2 (2026-07-14, `feat/souls-quality`, NOT yet integrated) - backlog #31.** New registry
> module `tools/patches/souls_quality.py` (position 13, after `boss_skill_fix`, before `visuals`) fixes the audit's
> (`docs/reports/souls_quality_audit.md`) real defects. **FIXED - ALL 5 tier inversions** (higher rarity strictly weaker
> than a lower rarity on the SAME skill), all raise-only: (P1, 3 mod-generated svc_uber) `crowboar`/`onyxspine`/
> `steamcrawler` `_soul_l` augment levels (+ crowboar's grant level) raised 1 -> 3 so n/e/l = **1/2/3** (matches healthy
> bloodrunner/xix); root cause = `_DIFF_SCALE` 0/0/1 + the B-SOUL-PROC-1 backstop bumping only n/e. (P1, round-2, 2
> SV-inherited that the round-0 audit MISSED - v1 detector only checked augment levels, never itemSkillLevel)
> `spider\bloodtip_soul` grant `bloodtip_devour` 5/**1**/9 -> **5/7/9** and `vulture\gustleech_soul` grant
> `leechstrike_soul` 10/**4**/**7** -> **10/12/14**; both obtainable Hero souls (66% finger2), grant NAMES preserved.
> (P2-b) svc_uber e/l per-tier icon law - 108 rings / **54 families** had `soul_n_icon` on Epic+Legendary; rewritten to
> `soul_e/soul_l_icon`. `verify()` is fail-loud + **ROSTER-WIDE** (tier monotonicity n<=e<=l on augment AND grant levels,
> same-skill-name-guarded, EVERY soul family - widened from round-1's svc_uber-only scope so the class can't recur
> anywhere; + svc_uber per-tier icon). **DISJOINT**: 0 of the 111 touched records hit Occult/Hunting/mastery/kallixenia/
> pharaoh/abyssalliche, 0 hit `corpsemanager` (skill_quality reassigns corpsemanager's GRANT to the `bloodtip_devour`
> *skill*, a different record from our `bloodtip_soul` *ring*). **⚠️ WILL VETO:** bloodtip/gustleech itemSkillLevel arrays
> are byte-identical to SV 0.98i - fixing them diverges from SV data (judged amgoz1 oversight: every OTHER field tiers
> upward correctly); revert `_SV_INVERSION_FIX` if SV numbers are sacrosanct. **VERIFY (no heavy build):** dry-run replay
> `tools/debug/souls_quality_replay.py` vs build40 GOLDEN `b33c5a44` = intended-only diff **exactly 111** (108 icons + 3
> new SV level records), field-minimal, all 5 families monotonic, verify OK, idempotent, **3 negative tests** PASS
> (svc_uber + NON-svc_uber inversion + wrong icon); patched-arz contracts `validate_soul_augments` PASS(0/0),
> `validate_summon_pets` 3-arg PASS (single-arg exit=1 is pre-existing noise, byte-identical baseline-vs-patched),
> `validate_tags` PASS-by-construction - all == baseline, zero regression; py_compile + `_check_registry` (14 modules,
> order `39d94e32`) OK. Audit re-graded DEFICIENT 3 -> 5; the audit probe's detector now catches itemSkillLevel-only
> inversions (`GRANT-LEVEL-TIER-INVERSION`). **NOT auto-applied (Will decisions):** P2-a Tomb Guardian obtainability
> (`um_tombguardian_26` = genuine COMMON 609-HP Anubis Hound, reclassifying to Hero is a balance change), P2-c nymph icons
> (integrate `feat/b40-soul-icons` 9db3f5f). **P2-d Soulfeeder pet = AUDIT FALSE POSITIVE** (bonepet20 already casts
> `bonescourge_spiritbreath`). Reports: `docs/reports/souls_quality_fix.md` + `souls_quality_audit.md`. Ships in a later
> integration build.

> 📐 **MASTERY-UI VET (FIXER round 1, 2026-07-14, `feat/mastery-ui-vet`).** Will's mandate (verbatim): "every
> skill on the right level vertically based on how many points is needed" (TIER LAW = row == skillTier) + "the
> only skills that should be connected together should be ones that genuinely augment one another" (CONNECTOR
> LAW). The build40 audit (`docs/reports/mastery_ui_vet_audit.md`) found **66 findings** (14 TIER, 23 CONN, 19
> INTERLEAVE, 9 OFFCOL, 1 ICON) across all 9 masteries. **SHIPPED this wave:** (1) a **PERMANENT fail-loud gate**
> `tools/gate_mastery_ui.py` (reuses `audit_mastery_ui` math; keys every finding) + waiver ledger
> `tools/mastery_ui_waivers.json`, **wired into the DB gate battery** right after the A7 golden guard - a NEW or
> regressed TIER/CONNECTOR/layout defect can never silently ship (negative test PASS: a fresh off-grid button
> fails the build). (2) A new registry module `tools/patches/mastery_ui_vet.py` (position after `mastery_ui_audit`,
> disjoint) with **4 clean, no-regression, non-golden relocations** clearing **8 of the 66** findings, dry-run
> replay-PROVEN vs build40 (`b33c5a44`): m1 `drxonslaught_hamstring` (628,217)->(428,217) [OFFCOL+INTERLEAVE+CONN];
> m2 `drxquickrecovery` (228,279)->(128,279) [INTERLEAVE+CONN]; m2 `drx_summonphalanx` (428,155)->(228,31)
> [TIER+INTERLEAVE]; m9 `drxdistortionfield` (228,279)->(128,279) [INTERLEAVE] - exactly 8 cleared, **0 new**.
> **The remaining 58 are WAIVED (each with a justification)** because they are genuinely Will-gated: the
> SVAERA/DRX graft added MORE families than the 6-column grid holds at tier-correct cells (Earth col428 = 4
> families with tier collisions + no free tier-1 column; Storm/Spirit full), some grafts have contradictory
> skillTiers (Warfare Club Slam = tier-2 base above tier-7 mods), Storm Nimbus has two tier-2 modifiers
> (same-tier collision), Storm has an SV-original dead-ref button (`drxspellbreaker_spellshock2`), Occult (m5)
> is Will's GOLDEN + the crossed-tree he reported 2026-07-13, Hunting (m6) is GOLDEN, and Spirit is a
> 4-family knot needing a holistic reflow. Each is a Will design-decision (per-mastery TIER-vs-CONNECTOR
> trade-off + in-game screenshot; golden moves also need `occult_hunting_golden.json` waivers). **No golden
> mastery touched** (A7 gate PASS, m5/m6 untouched). Verify: gate PASS on fixed arz (58 waived, 0 unwaived, 0
> stale) + FAIL on unfixed (8 unwaived) + negative test PASS; `_check_registry` OK (14 modules); py_compile OK;
> **arz/Text ship together** (deploy coupling). NOT yet integration-built (next wave rebuilds the arz).
>
> 📐 **MASTERY-UI REFLOW (round 2, 2026-07-14, `feat/mastery-ui-vet`, `docs/reports/mastery_ui_reflow_round2.md`).**
> Cleared the 58 waived findings: **every wrong/crossed arrow (the CONNECTOR LAW, Will's actual complaint) is
> gone - 0 unwaived CONN/INTERLEAVE/OFFCOL across all 9 masteries** - shrinking the waiver ledger **58 -> 17**
> (each surviving one an irreducible tier collision / graft-broken skillTier / missing-record phantom with a
> one-line "no law-compliant placement exists" reason). Non-golden reflow in `tools/patches/mastery_ui_vet.py`
> (m1/m2/m4/m7/m8/m9: ~30 button moves + 9 connector fixes - reunite off-column modifiers, split interleaved
> families, tier-correct chains, drop spurious base/leaf connectors, flip `[R]` side-connectors that pointed
> nowhere); golden reflow in `tools/patches/hunting_occult_ui.py` (m5 Occult crossed tree Will reported 07-13,
> re-derived to the laws + connection map; m6 Hunting connector moved from the Eviscerate modifier onto the Take
> Down base). **Detector fix:** `audit_mastery_ui.canon()` now strips `buffself` so `stoneformbuffself` links to
> `stoneform_moltenrock` - settles the Earth Stone-Form CONNECTOR false-positive in the detector (surgical: the
> ONLY skill ending in `buffself`). **Golden:** 9 new `owner_approved_overrides` in `occult_hunting_golden.json`
> (3 Occult positions + 4 Occult connectors + 2 Hunting connectors) + a `_WILL_VETO_2026_07_14` section (Will's
> mastery-fix mandate authorizes the UI-only fixes; freeze prevents SILENT reversion, not vetted fixes). **Verify
> (dry-run replay of the REAL modules onto build40 `b33c5a44`):** record-diff is **UI-only** (every changed field
> is `bitmapPositionX/Y` or `skillConnectionOn` on a mastery-UI/skill record - ZERO gameplay-value drift);
> `gate_mastery_ui` **PASS** (17 waived, 0 unwaived, 0 stale); A7 golden **PASS** (all drift covered); py_compile
> + `_check_registry` OK; negative test PASS. Earth NOT moved (its b38 contiguous Rupture packing is Will's
> explicit ask; arrows already correct, 5 TIER waived). **Round-2-for-Will candidates** (would shrink waivers
> toward zero, need his data/design call): delete the Storm Spell Shock 2 phantom (-2), confirm Warfare
> `drxhamstring` is a dead graft to delete (-1), authorise editing graft-broken `skillTier` values (-several).
> **arz/Text ship together**; NOT yet integration-built. **UI-on-device: needs Will's in-game screenshot before promote.**
>
> 📐 **MASTERY-UI CONNECTOR-ARRAY FIX (round 3, 2026-07-15, `feat/mastery-ui-vet`, addendum in
> `docs/reports/mastery_ui_reflow_round2.md` S7).** Round-1 vet caught a real HIGH: round 2's connector
> edits wrote a bare single-element `skillConnectionOn` string and never touched `skillConnectionOff` -
> `'drop'` left a STALE multi-tile dimmed bar behind, and `'straight'` under-drew any bar longer than one
> tile. **Ground-truthed the true mechanism** (`tools/mastery_conn_model.py`, new): `skillConnectionOn`/
> `Off` are a length-matched PAIR spanning a family's own base->top row; an in-between tile is CONNECT if
> that row is occupied by ANY skill in the column (family or not - proven on 2 vanilla multi-gap bars,
> including Occult's `envenomweapon` drawing a CONNECT tile over the unrelated `toxindistillation`) or
> MIDDLE if truly empty; `validate()` self-checks the rule at 42/43 vanilla bars (the 1 residual,
> Warfare's native `dualweapontraining` chain, is untouched by either module's reflow - documented, not a
> defect). **Fix:** `rebuild_into()` is now the single writer both `mastery_ui_vet.py` and
> `hunting_occult_ui.py` call after their position moves, reshaping every TOUCHED family's bar with
> matched connOn/connOff and clearing both arrays on non-base members and drop-listed leaves. Surfaced 1
> previously-invisible bug: Occult's Lay Trap base never actually drew the bar reaching its reunited
> Multishot Bolt Trap modifier in round 2 - now fixed (2 new golden overrides); the other 6 new overrides
> are the `skillConnectionOff` parity companions of round 2's existing entries (golden overrides 50 -> 58).
> **Gate extended:** `gate_mastery_ui.py` now also runs `mastery_conn_model.find_defects()` - CONNPARITY
> (on/off length mismatch) + CONNSPAN (a bar's top tile must land on an occupied cell) - pure geometry,
> 0 findings post-fix, waiver ledger UNCHANGED at 17. **Verify** (dry-run replay of the actual modules onto
> `local/baseline_build40.arz` b33c5a44): 53 records changed, UI-only (bitmapPosition/skillConnection* only);
> 0 CONNPARITY/CONNSPAN defects; `gate_mastery_ui` PASS (17/0/0); A7 golden PASS (52 waived, 0 other); 2
> negative tests (off-grid button; broken connOff parity on `drxbattlerage`) both correctly FAIL the gate;
> py_compile + `_check_registry` (14 modules) OK. NOT yet integration-built; still needs Will's in-game
> screenshot before promote (layout unchanged from round 2 - this wave is connector-array correctness only).
>
> 🗡️ **B39 BOSS-SKILL FIX (MERGED+BUILT+GATED in build39-dev, `feat/b39-boss-skills` @ `95edf55`).** Will
> (2026-07-13): the new bosses "not using skills when you fight them / when summoned". Audit (both surfaces):
> Surface B (soul-summoned pets) HEALTHY; Surface A (fought bosses) had a level-0 skill-wiring defect on **10
> apex bosses**. New registry module `tools/patches/boss_skill_fix.py` (position 11, after every boss-creating
> module, before `visuals`) makes 27 field edits at **per-skill donor-matched levels** (no clones/souls/pets, no
> damage rebalance): enables level-0 summon/attack specials, dead passives (boss_conversionimmunity/scaling/
> hero_scaling/toxeus_passiveproperties/armor_passive), auras, and restores Helepolis's displaced turret. `verify()`
> is **roster-derived + fail-loud** (scans every `um_*_99`, aborts on ANY chance>0 level-0 special + flags a boss
> not in the fix table) so a missed/new boss can't ship silently. Round-2 fixed the round-1 miss of
> **`um_voranthys_99`** (whole kit was level 0). Dry-run replay vs `baseline_build38.arz` (= build38-dev `fcd5dcab`):
> 27 edits, verify OK, idempotent, all 10 bosses clean, roster 0 leftovers, pets untouched, negative test PASS.
> Full RCA: `docs/reports/b39_boss_skills_rca.md`. **RE-VERIFIED in build39-dev** vs true build38a
> `6631f252`: 10 bosses CHANGED (32 skill-field diffs only - skillLevelN/skillNameN/specialAttack3*, 0 design drift),
> verify OK - see BUILD39-DEV GATE RECORD below.

> 🧩 **BUILD38 INTEGRATION (2026-07-13, main) - 5 GO-vetted lanes merged + integration fixes.** Merges (all
> clean, order hash `7ed29402a38d` -> `7c74a51f6ed8`, REGISTRY now 11 modules): `feat/b38-mastery-ui` @ `43611fc`,
> `feat/b38-damage` @ `ab5f5ac`, `feat/b38-enslaver-v2` @ `e2f87ef`, `feat/b38-language` @ `e22c62a`,
> `chore/b38-workshop-description` @ `475cfee`. Integration fixes commit `f1d53af` (+ reconcile `630bb9b`). NOT
> deployed; canonical build36a stays LIVE. **Full DB build + gate record DONE 2026-07-13 (see BUILD38-DEV GATE
> RECORD below): arz `fcd5dcab`, Text `dff9ad01`, all gates green, record-diff ZERO unexplained.** The Enslaver-residual
> stalker `limit=1` follow-up is now BUILT+VERIFIED (build38a, HEAD `2073fe6`): DEV-staged arz advances to `6631f252`
> (Text/Quests/map byte-identical); see BUILD38A GATE RECORD below.
> **FIXED this wave:**
> - **Mastery UI** (`mastery_ui_audit` module, after `hunting_occult_ui`): 8 graft icon repoints (7 `_DRX_Textures`
>   dead refs + 1 empty -> resolving XPack3/InGameUI arcs); Earth Rupture DE-DUP (graft `drxrupture`/`drxrupture_flare`
>   relabelled to the freed base tags `tagSkillName113` "Flame Surge" / `tagSkillName103` "Flame Arch"; SV `drxflamesurge`
>   stays the canonical Rupture) + Earth col-428 reflow (chains contiguous, base lower); Dream (xpack mastery 9)
>   background repointed off the black `skillbackgrounddiablo.tex` to the Spirit backdrop. **Nature "Sylvan Protection"
>   name wired in integration** (`drx_nymph_petmodifier_rootwave.skillDisplayName -> x3tagSkillNatureSylvanProtection`
>   + `...Desc`; base-game x3 tags, resolve at runtime, no Text.arc entry). Dry-run replay vs `baseline_build36.arz`:
>   15 records modified, 0 added, all asserts PASS.
> - **Damage numbers** (`damage_display` module, before `visuals`): bound the 7 missing AE floating-combat-text
>   FontStyle pointers (`DamageNormal/Elemental/OnPlayer/OverTime/Healing/HealingOnPlayer/PlayerImpairment`) on
>   `records\xpack\game\gameengine.dbr` (SV's pre-AE record lacked them -> only crits showed). Dry-run replay: 1
>   record, +7 STRING fields, 0 new records/tags, idempotent, verify() PASS.
> - **Enslaver v2** (`apply_svc_patches.py`): `_EN_SWEEP_K` 300 -> 600 (= /10 vs build36a K=60), ceiling 1/24000,
>   NEW per-slot `limit=1` = STRUCTURAL no-double (<=1 Enslaver per pool per trigger); fail-loud verify asserts it.
>   Reconciled with the `toxeus_suite` Hades-Hunt `_LS_MAX_P=1/2400` decoupling (both survive; stale x60/x300 +
>   1/12000 comments refreshed to x600 / 1/24000).
> - **Language** (`build_text_arc.py`): i18n de-clobber drops SV tags byte-identical to base-game Text_EN (they were
>   overriding non-English base text = the "cannot change language" Steam defect). **Integration hardened the
>   DIRECT-RUN path**: when `SVC_BASE_TEXT_EN` + 4th arg are both absent, `build_text_arc.py` now self-resolves the
>   base Text_EN.arc from the Steam install (doctor.sh discovery), warns loudly, falls back only if truly absent;
>   `SVC_NO_I18N_DECLOBBER=1` still the kill switch.
> - **Earthfury cd regression (Anapaest ruling)** FIXED in integration (`f1d53af`): player-cast `pcsafe\earthfury_ring`
>   was 16.0 in build37-dev vs 5.0 in build36a. TRACE-PROVEN root cause: `skill_quality` (registry module) re-runs the
>   castability wave during `run_registry`, minting the pcsafe clone from the still-16.0 plain BEFORE the deferred
>   `run_registry_gates` phase where A4 lowers it; the idempotent monolith wave then preserved the stale 16.0. A4
>   (`_apply_flashpowder_rework`) now also forces the pcsafe clone to 5.0 (guarded). Sole affected skill (Flame
>   Nova/Flash Powder have no special anim -> never pcsafe-cloned). **Confirming gate: next full DB build must show
>   `pcsafe\earthfury_ring` skillCooldownTime == 5.0.**
> - **Workshop description**: `docs/WORKSHOP_DESCRIPTION.bbcode` merged (already pushed LIVE to Steam as metadata-only).
> **RESIDUALS (open, recorded not fixed):**
> - **Storm UI slot25** -> `drxspellbreaker_spellshock2.dbr` is a PRE-EXISTING SV-ORIGINAL dead reference (present in
>   098i; the referenced skill never existed). DOCUMENTED, NOT TOUCHED - needs Will's design call (invent the skill,
>   repoint, or accept the harmless phantom button). SV-original, so out of a safe UI pass.
> - **Enslaver residual**: the `limit=1` cap is per-pool-per-trigger (structural). Two INDEPENDENT spawn points
>   surfacing an Enslaver close enough to fight together has no engine global cap; the /10 frequency cut makes it a
>   ~once-in-hundreds-of-acts event (also ~100x rarer cross-field). Endless-Hunt stalker (`toxeus_suite`) had the SAME
>   latent per-trigger-duplicate defect (Hades-only, rarer, UNSHIPPED b37) - **FIXED + BUILT+VERIFIED (build38a)**:
>   `_sweep_inject_legendary_stalker` now stamps per-slot `limit%d=_LS_SLOT_LIMIT`(=1) on the Hunt's name slot
>   (mirrors the Enslaver v2 cap) + `_verify_legendary_stalker_sweep` asserts weight==1 / limit==1 / p_slot<=1/2400
>   on EVERY stalker slot, fail-loud on any miss. Full DB build GREEN (build38a, HEAD `2073fe6`): the apply-time gate
>   asserted the cap LIVE on all 345/345 Hades pools; record-diff vs build38-dev = 345 CHANGED, each ONLY the Hunt slot
>   gaining `limit=1`, ZERO unexplained, 0 collateral. See BUILD38A GATE RECORD below.
> - **Language in-game spot-check = HARD pre-Steam gate**: the de-clobber restores ~93% localization by construction,
>   but an actual in-game language-switch test on a real non-English client MUST pass before any Steam push touching
>   Text.arc. Also FAILBOAT debug junk (4 rewording tags, English-VISIBLE today) recommended for a follow-up cleanup.
> - **Will tour checks** (in-game, cannot be gate-verified here): damage numbers appear on normal/elemental/DoT hits;
>   the 8 repointed mastery icons + Dream background render (no black pane, no missing icons); Earth Rupture chain
>   shows ONE Rupture with the reflowed layout. Screenshots requested.
>
> 🧪 **BUILD40 GATE RECORD (2026-07-14, main HEAD `32ea0e8` + this BACKLOG commit) - FULL coupled canonical + TESTHUB
> build GREEN; 12 b40-integ lanes (b41-b53 minus b51 docs-only) at `d8485fe` + the warden P1 fix at `32ea0e8`.** First
> build to ship the b41/b42/b43/b45/b46/b47 CANONICAL map changes + b48 established returns (canonical rebuild since
> build36a); DB carries b42 chests/nova + b43 arena/Aithon + b49 enslaver/hunt + b50 pet-white + b52 Dagon + b53 orb.
> Staged to `work/` + `local/`, NOT deployed; canonical Steam build36a stays LIVE; DEV deploy pending a TQ-exit window.
> **ARTIFACT MD5s:** arz `b33c5a447f3a8ca652c14f78d4ad1dd4` (55,351,206 B, 51,029 records = build39 51,015 + 14) -
> SUPERSEDES build39 `5bf7dac2`; Text.arc `c910da653f23ff84598b69833854d9db` (87,555 B) - SUPERSEDES `e1b73e05`;
> Quests.arc `37cf867f3550f5031dba5cb1cf31f30f` (194,801 B) - SUPERSEDES `7655f17e`; canonical Levels
> `9981085b78f1600cc0b31c3bec4cfd92` (688,691,745 B, `local/Levels_merged.arc`) - SUPERSEDES build36a `60a62880`
> (FIRST canonical rebuild since build36a); TESTHUB Levels `d4965d298ee308a4e31ffd39802ce404` (688,677,830 B,
> `local/Levels_merged_TESTHUB.arc`) - SUPERSEDES build39 `4fcc058c`. Baselines: `baseline_build39.arz` = build39 arz
> `5bf7dac2`; `baseline_canonical_b39.arc` = build36a canonical `60a62880`.
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): arz written (51,029 records); registry **13 modules order
> `b82195e9551a`** (was 12 `4c688f58`; +bossarena b43 at pos 9/13); RELEASE drops (66% Hero/Quest, 25% Boss);
> `run_registry_verifies` GREEN (4 verify hooks skill_quality + toxeus_suite + damage_display + boss_skill_fix all OK;
> boss_skill_fix roster `um_*_99` clean of level-0 specials, all enables survived finalization); golden Occult/Hunting
> PASS (35 waived). Collision gate: 2 records LATER-wins (legal registry semantics, logged), tags clean.
> **WARDEN P1 FIX (C-RES-DBR-1, `32ea0e8`):** `bossarena.py` scrubs `ember_satyr_warden_55.lootLowerBodyItem1` (the 3
> dangling `{N,E,L}_SatyrBrute` leg-loot refs, no explicit dtype per the cloned-record law). Fresh-arz probe: warden
> record **0 unresolved .dbr fields** (was 3); `contracts_resources` **1 P1 -> 0 P1**. Zero gameplay change (slot
> dropped nothing, same as the base donor).
> **RECORD-DIFF AUDIT** (`baseline_build39` `5bf7dac2` vs new `b33c5a44`): **14 ADDED / 0 REMOVED / 1035 MODIFIED, ZERO
> unexplained.** 14 ADDED = `ember_satyr_warden_55` (b43) + `svc_{charon,dorus,ephialtes,tantalus}_chest` (b42) +
> `aithon_embercrown_soul_{n,e,l}` (b43) + `svc_testhub_return_{bossarena,garden,secret,sparta,uber}` (b48) +
> `ephialtes_dread_nova` (b42). 1035 MODIFIED bucket 100% to lanes: **990** b49 undead+hades pool sweeps (273 enslaver +
> 345 hunt + breadth-restrict), **18** b50 pet-white nameplates, **13** b42/b43/b47 boss records, **6** b49
> shadowstalker rig, **3** b43 arena portals, **3** item/loot, **1** boss_skill_fix, **1** b52 dagon.
> **TEXT** i18n de-clobber ENABLED (17,541 base Text_EN tags): dropped **10,600** SV tags byte-identical to base;
> `validate_tags` PASS (all **321** referenced mod tags + **367** authoritative tags resolve in Text.arc; new b52 Dagon
> `tagSVCMonsterDagon`, b47 Kroisos, b43 Aithon tags resolve); golden A7 PASS (41 waived, 0 other); 2 pre-existing base
> monster-name WARN (`tagNewMonster66/46`, non-blocking backlog).
> **QUESTS** (`build_quest_files`, exit 0): quest-record contract PASS (**107** entry_type==3 records); **25** hub
> boat-dialog triggers + TESTHUB portal rig (7 hub + 2 return ports) appended to the always-loaded `sv_commonmechanics`
> refire step (registry law: no new QUESTS-section registration -> map 256-window parity intact).
> **CANONICAL MAP** (`SVC_TEST_HUB` unset -> `Levels_merged.arc`): mapdiff vs `baseline_canonical_b39` **PASS** - section
> order identical, QUESTS(0x1b) byte-identical (11,460 B, **256-window parity**), navmesh(0x0b) **0 changed**
> (byte-identical), 0 level add/remove, **18** intended blobs (b43 boss_arena, b47 Medea_TempleUG x2, b45 ThebesOptTombA,
> b41 HadesPalace/Styx/Judgment/Elysian/GardenofMerchants/DarkForestEnter, b48 established returns); 2282 levels, 0 bad
> offsets/magic/zero-ints. The b48 round-3 established returns (Garden/Secret/Uber/Sparta) are a deliberate CANONICAL
> warden-mute bugfix (see `docs/reports/b48_sparta_mute_fix.md`) - hence the canonical rebuild.
> **TESTHUB MAP** (`SVC_TEST_HUB=1` -> `Levels_merged_TESTHUB.arc`): mapdiff **PASS** - **27** changed blobs (18 canonical
> + 9 hub placements: HiddenValley01 Helos plaza + 8 return landings), QUESTS 256-parity byte-identical, navmesh 0
> changed, 0 add/remove; 2282 levels, 0 bad offsets/magic/zero-ints.
> **CONTRACTS:** resources/souls/summons **0 P0/0 P1** (4904 native P2: resources 4792, summons 112, souls 0) - warden
> `C-RES-DBR-1` P1 **GONE**; map vs canonical + map vs TESTHUB each **0 P0/0 P1** (3 native P2 = pre-existing base-game
> XPack portal reciprocity) - hub travelers + boss portals resolve in the new arz.
> **DEBUG GATES:** `gate_landing_clearance` HARD (TESTHUB v2 + b41b42) **25/25 PASS, 0 DEADLY/FAIL**;
> `gate_travel_npc_invariants` **T1-T6 PASS** (0 walk-throughs canon+TESTHUB; 25 hub records 0x canonical / 1x TESTHUB;
> 5 per-area returns; cross-file map==quests==arz 25+5 records; T6 scanned both fresh arcs); `gate_traveler_responds`
> **0 mute** (G-COLLISION/WARDEN/ORPHAN/DEST PASS; 30 placed NPCs / 31 routes). In-build enslaver roaming-sweep OK (273)
> + hunt stalker-sweep OK (345) + world-chest verify OK + collision legal.
> **NOT DEPLOYED:** staged to `work/` (arz/Text/Quests) + `local/` (canonical + TESTHUB Levels); DEV deploy pending a
> TQ-exit window; TESTHUB is local-only (never uploaded to Steam); canonical build36a untouched. Canonical rebuild + QA
> required for the b48 established-return canonical change before promote.
>
> 🧪 **BUILD39-DEV GATE RECORD (2026-07-13, main HEAD `87b0cae` + this BACKLOG commit) - FULL-REGISTRY DB + Text +
> Quests + TESTHUB-map build GREEN; both b39 DEV lanes integrated (boss-skill fix + Helos hub v2).** Merges:
> `feat/b39-boss-skills` @ `95edf55` (boss_skill_fix registry module, pos 11/12) + `feat/b39-hub-v2` @ `87b0cae`
> (8 new traveler NPC records + 25 quest triggers + TESTHUB placements + WILL_TEST_GUIDE); disjoint file sets,
> 0 conflicts. Staged to `work/` + `local/` TESTHUB, NOT deployed; canonical build36a stays LIVE; DEV deploy pending
> a TQ-exit window.
> **ARTIFACT MD5s:** arz `5bf7dac29beb75757178179c363af2cf` (55,354,147 B, 51,015 records = build38a 51,007 + 8 hub) -
> SUPERSEDES build38a `6631f252`; Text.arc `e1b73e050975b63521a30062c21e009b` (87,360 B) - SUPERSEDES `dff9ad01`;
> Quests.arc `7655f17e5a5f8bf13956ef456ca10595` (194,754 B) - SUPERSEDES `838bdc3a`; TESTHUB Levels
> `4fcc058c590ab0719e224940ba0b9266` (688,686,024 B, `local/Levels_merged_TESTHUB.arc`) - SUPERSEDES `841c56cd`.
> UNCHANGED (never rebuilt): canonical Levels `60a628807c1746e7bbde14946de62107` (688,682,781 B). Baseline for the
> diff: `baseline_build38a.arz` = build38a arz `6631f252`.
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0; registry **12 modules order `4c688f58d1aa`** (was 11
> `7c74a51f6ed8`; +boss_skill_fix at 11/12); RELEASE drops (66% Hero/Quest, 25% Boss); `run_registry_verifies` GREEN
> (verify hooks skill_quality + toxeus_suite + damage_display + **boss_skill_fix** OK; `boss_skill_fix.verify` OK:
> roster `um_*_99` clean of level-0 specials, all enables survived finalization); golden Occult/Hunting PASS (35
> waived). Collision gate: 2 records (`um_toxeus_hunt_99` <- toxeus_suite+boss_skill_fix, `um_helepolis_99` <-
> diadochi+boss_skill_fix) LATER-wins (legal registry semantics, logged) = boss_skill_fix repairs skill-wiring ON TOP
> of the boss-creating modules.
> **RECORD-DIFF AUDIT** (`baseline_build38a` `6631f252` vs new `5bf7dac2`): **8 ADDED / 0 REMOVED / 10 CHANGED, ZERO
> unexplained**, 0 forbidden clobbers. 8 ADDED = hub-v2 traveler NPCs `svc_helos_trav_{devourer,vashkarr,obsidian}` +
> `svc_area_return_{uber,sparta,devourer,vashkarr,obsidian}` (all `records\quests\svc_*`, mod namespace). 10 CHANGED =
> the enumerated bosses (voranthys/helepolis/dorus/kravmoloch/gorrahk/ilsevar/toxeus_hunt/vashkarr/sarkoth/
> broodmother_99); **32 field-diffs, every field in {skillLevelN, skillNameN, specialAttack3*}** (boss_skill_fix
> skill-wiring/animation) - **0 life/damage/cost/HP/design-value drift, 0 dtype-forbidden** (programmatic allowlist
> check: 0 fields outside the set, 0 forbidden-field hits).
> **TEXT** i18n de-clobber ENABLED (17,541 base Text_EN tags loaded): dropped **10,600** SV tags byte-identical to
> base-game Text_EN; `validate_tags` PASS (all **311** referenced mod tags resolve in Text.arc); golden A7 PASS (41
> waived, 0 other); duplicate-tag gate OK. New hub-v2 tags (`tagSVCHelosToUber`="The Uber Dungeon" + `tagSVCNpcTrav*`/
> `tagSVCHelosTo*` for devourer/vashkarr/obsidian) resolve.
> **QUESTS** (`build_quest_files`, exit 0): quest-record contract PASS (**107** entry_type==3 records loadable); Helos
> traveler hub = **25 per-area boat-dialog triggers** (14 outbound + 11 returns) appended to the always-loaded
> `sv_commonmechanics` refire step (registry law: no new QUESTS-section registration); 6 area quests round-trip OK.
> **TESTHUB MAP** (`SVC_TEST_HUB=1` -> `Levels_merged_TESTHUB.arc`, canonical untouched): world01.map QUESTS section
> **255 entries** (4 SV quests spliced in-window, widowletter idx 99 -> **256-window parity intact**); 25 hub NPCs into
> Helos (hiddenvalley01) + returns into boss landings (crypt_floor1/spartacryptlevel2/boss_arena/drxbc2/...); 2282
> levels, **0 bad offsets / 0 bad magic / 0 zero-ints**.
> **CONTRACTS:** souls/summons/resources 0 P0/0 P1 (**4905** native P2, == build38a); map (NEW arz + TESTHUB Levels
> `4fcc058c`) 0 P0/0 P1 (**3** native P2 = pre-existing base-game XPack portal reciprocity) - **hub travelers + boss
> portals resolve in the new arz**.
> **GATE_TRAVEL_NPC_INVARIANTS PASS:** T1 **0 walk-throughs** (canonical + TESTHUB, SV-native baseline=3); T2 **25 hub
> records 0x canonical / 1x TESTHUB** (warden law); T5 cross-file **map==quests==arz (25 records)** + 15 label tags
> resolve; canonical byte-pure.
> **NOT DEPLOYED:** staged to `work/` (arz/Text/Quests) + `local/Levels_merged_TESTHUB.arc`; DEV deploy pending a
> TQ-exit window (Will playing build38a-dev); TESTHUB is local-only (never uploaded to Steam), canonical Steam
> build36a untouched.
>
> 🧪 **BUILD38A GATE RECORD (2026-07-13, main HEAD `2073fe6`) - DB-ONLY rebuild of the Endless-Hunt stalker
> per-slot `limit=1` cap (two-in-one-trigger fix); the ONLY delta vs build38-dev is 345 Hades pools gaining the cap.**
> Staged to `work/`, NOT deployed; canonical build36a stays LIVE.
> **ARTIFACT MD5s:** arz `6631f25219be1b8f9874c95af68755c7` (55,340,923 B) - SUPERSEDES build38-dev arz `fcd5dcab`
> in DEV staging (+1,360 B = 345 added int fields). UNCHANGED + NOT REBUILT (the fix authors no tags/quests/map):
> Text.arc `dff9ad01ec1d81064f426d9456470eaf` (87,261 B), Quests.arc `838bdc3a` (194,581 B), canonical Levels
> `60a62880` (688,682,781 B), TESTHUB Levels `841c56cd` (688,688,154 B). Baseline for the diff: `baseline_build38.arz`
> = build38-dev arz `fcd5dcab`.
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0; registry 11 modules order `7c74a51f6ed8`; RELEASE drop
> rates (66% Hero/Quest, 25% Boss); `run_registry_verifies` GREEN (verify hooks skill_quality + toxeus_suite +
> damage_display OK); golden Occult/Hunting PASS (35 waived). **STALKER APPLY-TIME GATE LIVE PASS:**
> `_verify_legendary_stalker_sweep` asserted 345 eligible Hades trash pools carry the Hunt at weight 1 + per-slot
> limit 1 (p_slot <= 1/2400, <=1 Hunt/trigger); 0 non-Hades / boss / quest / hero leaks; band [40,68,100]. Enslaver
> sweep unchanged (1224 pools; its own `limit=1` already shipped in build38-dev).
> **RECORD-DIFF AUDIT** (build38-dev `fcd5dcab` vs new `6631f252`, 51,007 records both): 0 ADDED / 0 REMOVED /
> **345 CHANGED, ZERO unexplained**, 0 clobbers. EVERY delta = one Hades stalker pool (`records\xpack\proxieshades\...`)
> whose Hunt name slot gains exactly `limitN=1` (Int); 1 field/record, 0 other fields, 0 dtype changes, 0 collateral.
> Cross-verified against the new arz (strict audit): the `limitN` index IS the Hunt's name slot
> (`um_toxeus_hunt_99`) at weight 1 on all 345; the changed-set == the FULL set of Hunt-bearing pools (345); every
> Hunt pool now carries the cap, none missed.
> **VALIDATE_TAGS** PASS: all 308 referenced mod tags + 351 authoritative tags resolve in the UNCHANGED Text.arc (new
> arz authored 0 new tags -> no Text rebuild needed/done).
> **CONTRACTS:** souls/summons/resources 0 P0/0 P1 (4905 native P2); map (new arz + TESTHUB Levels `841c56cd`) 0 P0/0
> P1 (3 native P2 = pre-existing base-game XPack portal reciprocity) - hub NPCs resolve in the new arz.
> **UNTOUCHED:** DB-only pass wrote only the arz (+ its report/tags sidecars); Text `dff9ad01`, Quests `838bdc3a`,
> canonical + TESTHUB Levels byte-identical to build38-dev (never rebuilt).
>
> 🧪 **BUILD38-DEV GATE RECORD (2026-07-13, main HEAD `39a11707`) - FULL-REGISTRY DB BUILD GREEN + de-clobbered
> Text; DB+Text ONLY (map/Quests stay build37-dev).** First full heavy build of the b38 integration (mastery UI +
> damage display + enslaver-v2 + language de-clobber + earthfury fix). Everything staged to `work/`, NOT deployed;
> canonical build36a stays LIVE.
> **ARTIFACT MD5s:** arz `fcd5dcab40359aa94b421dd8cef4b81e` (55,339,563 B), Text.arc `dff9ad01ec1d81064f426d9456470eaf`
> (87,261 B). UNCHANGED (DB+Text-only pass, verified): Quests.arc `838bdc3a` (194,581 B), TESTHUB Levels `841c56cd`
> (688,688,154 B, `local/Levels_merged_TESTHUB.arc`), canonical Levels `60a62880` (688,682,781 B). NOTE: `work/`
> staged Levels = canonical `60a62880` (pre-existing staging; TESTHUB is local-only per standing rule). Baseline for
> the diff: `baseline_build37.arz` `56d6db22` (== build37-dev arz).
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0 in 346s; registry 11 modules order `7c74a51f6ed8`;
> RELEASE drop rates (66% Hero/Quest, 25% Boss); `run_registry_verifies` post-finalization phase GREEN (verify hooks
> skill_quality + toxeus_suite + damage_display OK); pet + container-shape + summon gates GREEN; golden Occult/Hunting
> PASS (35 waived in-build, 0 other).
> **RECORD-DIFF AUDIT** (baseline build37-dev vs new arz): 0 ADDED / 0 REMOVED / 1242 CHANGED, **ZERO unexplained**,
> 0 clobbers. Every delta maps to exactly one lane: **15 MASTERY** UI records (UI/display fields ONLY - 0 design-field,
> 0 dtype changes: 8 graft-icon repoints + Earth de-dup `drxrupture`->Flame Surge / `drxrupture_flare`->Flame Arch +
> Earth col-428 reflow 4 slots [bitmapPositionY] + Dream m9 bg 2 + Nature `drx_nymph_petmodifier_rootwave`
> skillDisplayName/Desc); **1 DAMAGE** `records\xpack\game\gameengine.dbr` (+7 FontStyle STRING fields, all ADDED);
> **1 EARTHFURY** `pcsafe\earthfury_ring` `skillCooldownTime` 16.0->5.0 (RESTORES build36a canonical 5.0, fixes the
> build37-dev regression flagged in that record's OBSERVATIONS); **1225 ENSLAVER** spawn-pool records =
> `_EN_SWEEP_K` 300->600 (existing main weights x2, e.g. 3000->6000) + NEW per-slot `limitN=1` (all 1225 additions == 1;
> `um_toxeus_enslaver_99` present in both builds). Mastery design-field changes: 0; dtype changes: 0.
> **TEXT** i18n de-clobber ENABLED (17,541 base Text_EN tags loaded): dropped **10,600** SV tags byte-identical to
> base-game Text_EN; 4,414 total tags emitted. `validate_tags` PASS (all 308 referenced mod tags + 351 authoritative
> resolve); golden A7 PASS (41 waived, 0 other); duplicate-tag gate OK. SANITY-DIFF vs baseline Text `8c7229db`: 10,600
> dropped / 0 added; **every dropped tag byte-identical to base Text_EN** (0 not-in-base, 0 value-mismatch); Nature
> `x3tagSkillNatureSylvanProtection`(+Desc) resolve in base-game Text_EN.
> **CONTRACTS:** souls/summons/resources 0 P0/0 P1 (4905 native P2); map (NEW arz + TESTHUB Levels `841c56cd`) 0 P0/0
> P1 (3 native P2 = pre-existing base-game XPack portal reciprocity) - **hub NPCs resolve in the new arz**.
> **QUESTS/LEVELS UNTOUCHED:** DB+Text-only pass wrote only the arz + Text.arc; Quests `838bdc3a` + TESTHUB Levels
> `841c56cd` byte-identical to build37-dev (never rebuilt).
>
> 🧪 **BUILD37-DEV GATE RECORD (2026-07-13, main HEAD `46bf0f2`) - FIRST FULL-REGISTRY DB BUILD GREEN + TESTHUB
> map + Text + Quests.** First full-registry build after the gate-fix (relocated `skill_quality` diversity gate to a
> post-finalization `run_registry_verifies` phase; 2 HC souls added to ALLOW). Everything staged to `work/` + `local/`,
> NOT deployed; canonical build36a stays LIVE.
> **ARTIFACT MD5s:** arz `56d6db22` (55,334,381 B), Text.arc `8c7229db` (377,150 B), Quests.arc `838bdc3a`
> (194,581 B), TESTHUB Levels `841c56cd` (688,688,154 B). Canonical `Levels_merged.arc` UNCHANGED `60a62880`
> (688,682,781 B; NOT rebuilt). Baseline for the diff: `baseline_build36.arz` `63ca7cf8` (== build36a canonical arz).
> **DB BUILD** (PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1): exit 0; registry 9 modules order `7ed29402a38d`; RELOCATED
> post-finalization diversity gate GREEN (8 family skills roster-locked; HC `ringoflightning`+`melinoe_bloodboil` now
> rostered); pet gates PET-STAT-MIRROR/PET-GEAR-PARITY GREEN; internal contracts 0 P0/0 P1 (112 native P2); golden
> Occult/Hunting PASS.
> **RECORD-DIFF AUDIT** (baseline vs new arz): 124 ADDED / 0 REMOVED / 1394 CHANGED, ZERO unexplained, 0 clobbers.
> ADDED = registry bosses (neferkha/toxeus_suite/polis_vault/diadochi/four_generals) + 17 Helos-hub quest records.
> CHANGED breakdown: 1224 spawn-pool records = BL-ENSLAVER-SPAWNS `_EN_SWEEP_K` 60->300 (existing weights x5) +
> toxeus_suite Endless-Hunt hades-only sweep (345 additive `um_toxeus_hunt_99` inserts at weight 1, old=None); 125
> souls = skill_quality de-filler/roster reassignment; 21 UI = hunting_occult_ui all-8-mastery shape law; 6 bloodhound
> `dyingFxPak` + enslaver smoke FX = lane-A; remainder = H/O improvement wave. (`um_toxeus_enslaver_99` present in
> both builds, unchanged.)
> **TEXT** golden A7 guard PASS (41 waived, 0 other); duplicate-tag gate OK; 351 uber tags added; `validate_tags`
> PASS (all 308 referenced mod tags + 351 authoritative tags resolve in Text.arc).
> **QUESTS** exactly 17 Helos-hub boat-dialog triggers appended to `sv_commonmechanics.qst`; entry-diff vs build36a
> `56acee66` = ONLY `sv_commonmechanics.qst` changed (107 entries, 0 added/removed); quest-record contract PASS
> (107 loadable); world01.map QUESTS section byte-identical canonical==TESTHUB (`226461e7`, 255 entries, NO new
> registration, 256-window intact).
> **TESTHUB MAP** (SVC_TEST_HUB=1 -> `Levels_merged_TESTHUB.arc`, canonical untouched): rig NPC into Random09A;
> walk-through de-place M2 72inst/33lvl; `gate_travel_npc_invariants` T1-T6 PASS (17 hub records map==quests==arz,
> each 1x TESTHUB / 0x canonical, 0 walk-throughs); contracts map 0 P0/0 P1 (3 native P2); contracts
> souls/summons/resources 0 P0/0 P1 (4911 native P2).
> **INPUTS RESTORED** (gitignored build deps absent on machine): `reference_mods/SVAERA_customquest/Resources/
> Quests.arc` (from SVAERA workshop item 2076433374, `b786666c`) + `upstream/soulvizier_098i/Resources/XPack/
> Quests.arc` (from in-repo `third_party/soulvizier098i.zip`, `a1b8020b`).
> **OBSERVATIONS (non-blocking, for the tuning lane):** (1) pcsafe `earthfury_ring` `skillCooldownTime` is 5.0 in
> build36a and 16.0 in this build (opposite the A4 "16->5" build-log narrative; sanctioned skill-domain change,
> worth a human glance). (2) stale "x60" comment in `toxeus_suite._sweep_inject_legendary_stalker` (the Enslaver
> monolith sweep is now x300, not x60; cosmetic).
> ⛴️ **BUILD36a P0 HOTFIX SHIPPED (2026-07-12) - walk-through travel portals REMOVED (Will TRAVEL LAW).**
> Fix for the LIVE Steam breakage (item 3759792705: "walk south in Helos -> teleported to Garden of Merchants,
> no way back"). Every walk-through/proximity teleport we authored is stripped from the canonical map; ALL
> cross-area travel is now NPC boat-dialog (Helos portal-master out; per-area `svc_testhub_return` NPC / SV rift
> shrine back). Fix commit `0f08297`, tag `build36a`. **Map tooling only** (`tools/build_section_surgery.py`);
> **arz/Text/Quests SHIP UNCHANGED from build36** (return NPC record + dialog already shipped inert). Canonical
> `Levels_merged.arc` md5 `60a628807c1746e7bbde14946de62107` (was `b42be44f`, 688,682,781 B); arz `63ca7cf8` /
> Text `2af4ce38` / Quests `56acee66` reused byte-identical. Blob-diff vs build36 = EXACTLY 9 changed level
> blobs (7 portal levels + crypt_floor1 + spartacryptlevel2), 0 added/removed. Gates GREEN: navmeshes 24/24,
> seam-lattice 24/0, entrance-landing PASS, map contracts 0 P0/0 P1 (3 native P2). **STEAM: SHIPPED 2026-07-12**
> (SteamCMD "Upload complete", item 3759792705, Visibility 0/public, cached login; push-gates F9+F7 PASS after the
> whitelist below). **DEV (SoulvizierClassicDEV): map STAGED to work/; the DEV `Resources/Levels.arc` copy is
> DEFERRED while TQ.exe is running** (Will actively playing) - copy `local/Levels_merged.arc` over the DEV
> `Resources/Levels.arc` when TQ exits; NEVER kill TQ.exe.
> - **Removal inventory (20 authored teleports):** 16 walk-through GridEntrance/GridExitOneWay/map_portal_aura
>   REMOVED from INJECT_SPECS (Helos H1/R2+swirl, HV01 G1/G4+swirl, Garden G2/G3/H2/R1+swirl, vista S1/S4,
>   Secret S2/S3, maze03->Uber, catacube->Sparta) + 4 native 0x06/0x05 return doors DISABLED (SC2 REWRITE_0X06,
>   crypt APPEND_0X06, crypt REMOVE_0X05 - SV-original untouched). KEPT: Helos + Olympus portal-master NPCs,
>   rift shrines teleportshrine_gom + teleportshrineorient01. PROMOTED TESTHUB->canonical: 4 svc_testhub_return
>   NPCs (Garden/Secret/Uber/Sparta).
> - ⚠️ **PUSH-GATE WHITELIST ADDED (SHIP OPERATOR, 2026-07-12):** `tools/contracts/whitelist_quests.txt` gained
>   ONE justified entry - `QST-DOOR-UNLOCK bossarena.qst :: records/quests/portal_olympianarena1.dbr`. Removing
>   the portal left bossarena.qst's `Action_UnlockFixedItem` naming a now-unplaced door (engine name-lookup
>   no-ops; harmless, travel is NPC-based). This is the intended consequence of the P0; the alternative (Quests
>   rebuild) is barred by the ship-unchanged constraint. **FOLLOW-UP:** a future Quests.arc rebuild should drop
>   the dead unlock action from bossarena.qst, then remove this whitelist line.
> - ⚠️ **DEBUG GATE FOLLOW-UPS (out of P0 scope, per the fix commit's GATE IMPACT):** the standalone
>   `tools/debug/gate_*.py` scripts that assert the removed portals (gate_doors_hub, gate_sparta_*,
>   gate_portal_*, gate_openness_collateral, gate_portal_records_global, compare_gridentrance_0x14) +
>   gate_testhub_inert (canonical now places 4 return NPCs) must be retired/updated before they are re-run.
>   Also rename Text tags tagSVCNpcTestHubReturn/tagSVCTestHubReturnChat to drop "(Test Rig)".

> 🛠️ **BUILD36 AMENDMENT (A1-A9) - DB IMPLEMENTED + GATED GREEN (2026-07-12, `feat/build36-amendment`,
> off main `32a4967`, HEAD `5526bef`).** Nine-item final DB pass; all in `tools/apply_svc_patches.py`
> (A5 also `tools/build_svc_database.py`; A5 doc corrections in `build_quest_files.py` +
> `docs/QUEST_STATE_INJECT.md` + `docs/MODDING_PLAYBOOK.md` graveyard). Built arz + Text; the map lane
> owns the deltas below. **Verified in the built arz + full gate battery GREEN** (5 invariants, 3 pet
> gates, golem button, B-SUMMON-1, C6 Dorus, F1/F2/F3/F6, A9 render-chain w/ real art, golden w/ 5
> flash-powder waivers, `_verify_boss_orbs` NEW + negative-test, naming gate negative-test, contracts
> souls 0/summons 0P1/resources only the pre-existing `anm_dreamcopy` P1).
> **A1 ENSLAVER WARBAND + B6 MARAUDER LAW** (`_create_enslaver_warband`, built between `_create_enslaver`
>   and the roaming sweep; whitelisted in `_EN_YARD_POOLS`): Option-A championChance set-piece
>   `q_enslaver_warband` pool/proxy = 1 leader + 4 "{^r}Enslaved Shadow Marauder" champions
>   (spawnMax=5/championMin=Max=4/championChance=100, chanceToRun=100, limit_obsidianbosses [1..110]);
>   name KEPT per Will. B6: marauder buffed to the DEPLOYED demon-Toxeus block ([13000,18000,24000],
>   str480/dex660/int420, scale2.0, resists Life100/Pierce80/Phys30, KEEP dmg300/380); summon petLimit
>   12->4 (WILL_DECISIONS); leader = 2.5x = [32500,45000,60000], dmg350/500, scale2.4, CC-immune;
>   friendly soul-pet marauders match the demon ladder.
> **A2 BOSS ORBS** (`_amend_boss_loot_orbs` + `_verify_boss_orbs`, after all uber builders): 12 boss
>   records get `treasureProxyName=genericbossorb_04` (J1 Enslaver ON + J2 breadth: Blood Toxeus,
>   Vashkarr, Broodmother, Dorus, 4 Obsidian wardens, Tantalus->`um_tantalus_unbound_99` TERMINAL,
>   Mnemophage->core, Ephialtes; Charon already inherits; marauders/heroes excluded). Marauder stays
>   orb-less.
> **A3 MAKARIA** Venom Cloud `skillCooldownTime` 25->8 (`makaria_venomcloud.dbr`, edit-shared).
> **A4 ANAPAEST** Earth Fury `skillCooldownTime` 16->5 on the PLAIN `earthfury_ring.dbr` pre-castability
>   -wave so the pcsafe clone inherits 5.0 (shared x4 bruiser souls).
> **A5 ACT-5 FIX C** (arz-only): `portal_hadesscandia` += RequireNoDLC=TQA2, IT->EE teleport +=TQX4,
>   `endportal_hades` UN-gated (Victory Portal revealed for DLC owners -> Epic), redundant 2nd portal
>   +=TQX4; `fixeditemtyphonportal` untouched. + doc corrections (quest identity = md5 of FULL registry
>   path).
> **A6 SOUL WIRES** (`_wire_missing_boss_souls`): `hellflower_soul` -> `us_hellflower_37` @66 (fresh);
>   `limoslifeater_soul` -> `um_frost_36` @66 (UNCONDITIONAL REPLACE of the thin `um_frost_soul` husk).
> **A7 21 HANDCRAFTED SOULS** (`_apply_dewired_hero_handcraft`, run FIRST in `apply_all_extended_patches`):
>   owned-override table, evocative names + signature grants + amgoz downsides + per-tier itemLevel.
> **A8 OBSIDIAN BALANCE (B1-B7)**: Voranthys (12/18/25k, scale2.5, freezingbreath signature + slot
>   reshuffle, pet breath+scale); escort soul-flood fix (soul-less clones of permean+bonehallow);
>   Ilsevar (10/15/21k, scale3.0, CC-immune, soul->manual-cast `ilsevar_drainnova` clone CD16, tier 3/5/8);
>   Sarkoth (13/20/28k, regen40/70/100, scale3.0, CC-immune, `svc_sarkoth_whelp` blooddragon summons);
>   TESTHUB yard chest -> golden poolchest tier; Vashkarr (shadow-shroud via charFxPakRunningNames on the
>   monster + defensiveStun100 + scale3.0 + Wrath-of-the-Eldest enrage, stacks on C7); B7 Eldest soul
>   physres 84/114.8/140 -> 30/45/60 + flat armor + HP + -8% runspeed (Gorrahk soul same).
> **A9 EVOCATIVE-NAME RESTORATION**: `_HAND_DESIGNED_SOUL_TAGS` extended (Anapaest -> "{^F}Soul of
>   Anapaest the Dishonored", etc.); the auto-transform in `_apply_soul_naming_standard` also exempts the
>   whitelist so evocative names win end-to-end; naming gate stays green (negative-tested).
> **MAP DELTAS (hand-off to the map lane, NOT touched here):** (1) A1 place `q_enslaver_warband` at one
>   walkable shadow-touched coord (5-monster footprint, extents ~4.0); (2) A8/B5 re-verify the
>   `q_vashkarr_lone` placement density at the new scale 3.0; (3) A8/B1-B3 in-game clipping/pathing
>   check on the 3x guardians in the TESTHUB yard + Obsidian Halls. A5 is arz-only (no map change).
> **Coupled ship set:** arz + Text.arc. NOT DEPLOYED (map deltas + Steam land in the coupled wave).

> 🩸🐉 **BUILD36 CONTENT WAVE (C1-C7) - DB IMPLEMENTED (2026-07-11, `feat/build36-content-wave`,
> round 1).** Four new uber bosses + the Ereban relic + Dorus amendments + uplift picks, all DB-side
> (arz + Text; map lane owns the C1-C4 placements, already landed). Branch is off `feat/build36-fix-wave`.
> All content in `tools/apply_svc_patches.py` (one appended `_create_*` section + dispatch hooks + the
> F6 hand-designed-soul whitelist). Baseline = fix-wave HEAD `182690e`.
> **C1 TANTALUS, THE INSATIABLE** (`_create_tantalus_uberboss`): 2 forms via `actorToSpawnOnDeath`
>   (Insatiable [15/20/27k]@[52,74,90] -> Hunger Unbound [9/12/16k]), WraithLord spawn/death FX, poison
>   shroud (`toxeus_envenomweapon` initialSkillName), widened Circle of Decay (r 4.5 clone), form-2
>   shade-wave summon (`svc_tantalus_raiseshades`, lost-soul spawns), 2 Famished-Shade escorts, no-cap
>   `limit_tantalus`, reused Obsidian hoard, **S2 ONE-SUMMON soul `{^F}Soul of the Insatiable`** (Famished
>   Shade on the wraith rig, amgoz hunger downside `characterLifeRegen -3/-4.5/-6.5`, FileDescription
>   Hades, 66% Finger2 on form2 ONLY), TESTHUB yard.
> **C2 CHARON, THE UNFERRIED (Golden Bough)** (`_create_goldenbough_boss`): genuine 2-phase (Unferried
>   [22/28/34k]@[48,72,100] Charon01 -> risen giant [24/30/36k] Charon02, actorHeight 2.0), deathchill
>   cold shroud added to an empty slot on both forms, **form-2 final-kill burst via an owner-approved
>   `deathEffect` on the monster clone** (the vet byte-truth: the form-2 donor carries no effect fields;
>   monster clones are not clone-shape-gated, so the add is safe), 2 oarsman escorts, no-cap
>   `limit_goldenbough`, hoard, **THE GOLDEN BOUGH** custom Legendary amulet (guaranteed on form2),
>   **S1 cold/vitality stat soul `{^F}Soul of the Unferried`** (melinoe_bloodboil grant + drxcoldaura +
>   ravagesoftime; S1 not S2 because the CharonGhost oarsman body != the Charon02 dropper body would trip
>   the fix-wave F2 identity gate - a verifier-wins call), NO-DLC (0 xpack2/3/4), yard.
> **C3 THE MNEMOPHAGE (Pools of Mnemosyne)** (`_create_mnemophage_superboss`): 2-phase shell
>   (**overmind.tex + scale 2.5 per the cross-spec law**, [14/19/25k]@[46,68,100], the 16-slot keep/add
>   psionic kit + energy-drain + on-death void-nova) -> core "the Unremembered" (voidlash skin, [7/9.5/
>   12.5k], scale 1.8, on-death necro-nova, no soul), psionic mindshroud (`hades2_shadowcloud`), 2
>   nightmare escorts, no chest (the differentiator), **Lethe's Draught** custom Legendary caster amulet
>   (field-validity-audited), **S2 phantasm summon soul `{^F}Soul of the Mnemophage`** (Epiales rig,
>   run-speed downside), yard. FEEDS on nightmares (Ephialtes sires them).
> **C4 EPHIALTES, THE WAKING DREAD (Dread Halls)** (`_create_dreadhalls_uberboss`): SINGLE-PHASE,
>   band [58,78,97]/HP [15/20/27k], **epiales_overlord.tex + scale 2.2** (cross-spec split from the
>   Mnemophage's overmind.tex + 2.5), fear spine on Skill_AttackRadius (ixion_cry Dread Roar + Dreamstorm
>   nova + Vision of Death) + takedown chase + on-death nova, Dread Shroud (`troubleddreams` FX), 2
>   nightmare escorts, no-cap `limit_ephialtes`, hoard, **Mask of the Waking Dread** custom helm (keeps
>   the donor's visionofdeath grant), **S1 dread-sower stat soul `{^F}Soul of the Waking Dread`**
>   (Dreamstorm fear-nova grant + the load-bearing `characterManaRegenModifier -40/-55/-70` downside).
>   Ephialtes OWNS the active fear nova; the Golden Bough soul keeps only a stat trickle.
> **C5 EREBAN HEARTSTONE** (`_create_ereban_heartstone`): 3-tier weapon+shield physical/earth relic off
>   em_brute_43/45 (10% lootMisc4), petrify-on-hit + defensivePetrify capstone @5/5, 6 donor ladders
>   zeroed. **The dtype traps handled explicitly**: petrify keys + lootMisc4 chance written as FLOAT
>   (absent-on-donor fields; an INT there reads ~0 and never procs/drops).
> **C6 DORUS AMENDMENTS** (`_apply_dorus_amendments`): hold-and-drown re-theme on the built um_dorus_99
>   (rottengrasp root + Dread-Pall dreadaura + coral tsunami + slow-decay-poison touch, casts anim-blanked
>   for the royalty rig) + themed soul grant (ichthian tidal strike + fear + run-speed downside).
> **C7 UPLIFT PICKS** (`_apply_content_uplift_picks`): Vashkarr dragonfire birthright (family breath +
>   terrifying roar + 16-jet firenova death + soul reflect/fear); Sepulchral Wyrm cold tide (4 frost
>   champions freezing-breath + shatter-on-death, repointed into svc_wyrmhorde_03); Broodmother death
>   crescendo (ondeath frostnova + last-brood + cold breath, anim-kept fire->cold); Obsidian **Keeper of
>   the Wheel** jackpot warden Kravmoloch (new Boss [16/22/30k]@L74 + call-the-table summon + 5th soul,
>   name5 @ weight 4 in q_obs_warband).
> **C8 TEXT**: every new name/desc/soul-flavor tag rides the tags dict -> uber_soul_tags.txt ->
>   build_text_arc.py; the 4 hand-designed uber-soul names are whitelisted in the F6 provenance gate
>   (`_HAND_DESIGNED_SOUL_TAGS`) so they KEEP their "{^F}Soul of X" flavor (Will's ruling).
> **CONTENT-WAVE GATES (all GREEN):** boss-kit clone-shape (14 pairs incl. the decay/shadewave/mindshroud/
>   dreadshroud/coldbreath/kravmoloch-summon clones), spawn-eligibility (25 mod-authored proxies incl. the
>   4 new boss + 4 yard proxies, spawnMax-championMax>=1 + L90/97/100 <= no-cap [1..110]), soul-leak (0 -
>   every form-1/core/escort clone has its inherited Finger2 soul cleared), soul-augment (all resolve),
>   the 3 A1 pet gates (stat-mirror/gear-parity/skill-kit, 15 families incl. tantalus/mnemophage summons),
>   F2 soul-summon-identity (tantalus/mnemophage summons match their dropper mesh), F6 naming (4 hand-
>   designed souls whitelisted; kravmoloch/dorus follow the standard). Donor-existence probe
>   (`tools/debug/probe_build36_content_donors.py`) GREEN for every content donor.
> **GATES (FULL REAL BUILD, GREEN after merging the fix wave `5e2e30b`):** the fix-wave round-1 merge
>   fixed the three blockers that were flagged pre-merge (F1 conflicted-copy `legion_soul` skip; F2
>   `_SUMMON_IDENTITY_ALLOW` voranthys; activation onyxspine/steamcrawler). Full arz build exit 0 ("Done."):
>   F1 cross-wire OK; spawn-eligibility OK (25 mod-authored proxies incl. the 4 new boss + 4 yard);
>   soul-leak 0 (every form-1/core/escort clone has its inherited Finger2 soul cleared); soul-augment OK;
>   soul item-skill activation OK (1400 souls; Kravmoloch soul made stat+augment to clear the F3 Ground-
>   Smash roster gate); F3 diversity OK; F2 identity OK (15 summon families incl. tantalus/mnemophage);
>   F6 naming OK (63 OURS-path souls + 2158 SV auto-whitelisted; the 6 hand-designed evocative souls in
>   `_HAND_DESIGNED_SOUL_TAGS`); boss-kit clone-shape OK (12 pairs); MP 44 eqs '/'-free; Occult/Hunting
>   golden PASS. **Text.arc built + validate_tags PASS** (250 referenced mod tags + 266 authoritative all
>   present). **validate_render_chain PASS** (every new skin/FX/mesh resolves; 28 upstream WARN). **Contracts
>   souls/summons/resources: 0 P0 / 0 ADDED P1** (souls 0/0, summons 0/0, resources 0 P0 + the SAME 1
>   pre-existing P1 the shipped work arz carries - `anm_dreamcopy`, 5 unresolved dream-pet anim clips, a
>   pre-existing mod-record bug NOT this wave, verified identical on the shipped arz). The 3 authored
>   resource P1s my clones briefly added (inherited base-only refs) were eliminated: Charon-escort
>   `skillName7` blanked, Dorus coral tsunami uses the raw upstream skill, Broodmother coldbreath dropped
>   (the crescendo keeps its frostnova + last-brood). Coupled ship set: arz + Text.arc. NOT DEPLOYED
>   (no map/quests/steam; the C1-C4 map placements land in the coupled map wave).


> 🛠️ **BUILD36 FIX WAVE - ROUND 1 (2026-07-11, `feat/build36-fix-wave`, branched off main `31a0bce`).**
> Seven live-test fixes (F1-F7) implemented + built + all gates green + negative-tested. Built (RELEASE)
> arz md5 `07de3349dcc5b854508a610aea23584b` (55,043,244 B), Text.arc md5 `b9ecb973ae84808dab46dc38a651c9ea`
> (372,752 B). NOT deployed. Items:
> - **F1 wrong-soul matcher (Cave of Whispers "white spider drops Ararat's soul" + Siege Strider drops
>   Leveler Soul).** `wire_souls_to_monsters` verifier-v7 rule: `qualifies=(score==100) or (score>0 and
>   type_bonus>0)`. Kills all 64 cross-wires + 8 flood pools. NEW fail-loud gate `_verify_no_fuzzy_cross_wire`
>   (snapshot SV pairings pre-wire -> flag any NEW Hero/Boss/Quest drop that is neither exact nor same-family,
>   skipping amgoz git-conflict-copy junk). **Side effect (spec §4-sanctioned house pattern):** de-wiring makes
>   `create_uber_souls` newly generate the named heroes' OWN identity souls (Phantom Weaver -> `shadowhero_soul`,
>   Spider Brooding -> `blinkfang_soul`), so they drop their own soul, not Ararat's; Thunder Crawl (`um_storm_16`)
>   drops nothing; the real owner `um_ararat_36` keeps `ararat_soul`.
> - **F2 Meritamen true summon.** D22 job in `_apply_group4_summons`: `phagia_soul_{n,e,l}` ("Meritamen the
>   Shadowcaller Soul") now grants `summon_meritamen` -> a `meritamen.msh` sand-spirit with the full kit incl.
>   the friendly `shadowstalker_summon3`. Real Phagia (`um_phagia_44` -> `maenadsorceress_soul`) untouched. NEW
>   REGISTRY-SCOPED gate `_verify_soul_summon_identity` (allow-set: `voranthys`, an intentional themed cross-mesh
>   summon). Fixed the wrong `BOSS_SOULS_DESIGN.md:895` row.
> - **F3 Ground Smash de-filler.** GS kept on its 6-soul roster (Brontes/Steropes/Polyphemus/Surryln/Sow/Gorrahk);
>   camelbane -> `myrto_tremor`; all other 25 fillers -> stat-only (never another over-shared filler). Anchored
>   soul-basename matcher (kills the `beast_soul`->`foulbeast_soul` bleed + mountain-satyr hijack). Restored
>   `foulbeast_soul` -> its SV `records\skills\sv\foulbeast\foulbeast_summon_soul.dbr` (present, no port).
>   Neutralized `_guess_element` physical->GS latent default (returns None -> stat-only). NEW fail-loud gate
>   `_verify_granted_skill_diversity` (hard-fail GS off-roster + ceiling 15; WARN-list the element fillers).
> - **F4 Shadow Stalker.** `skill_shadowzap` AoE petrify 2.0-4.0 + stun 0.8-2.0 + confuse 0.5-1.5 (chance valves
>   65/45/35); dead `specialAttack2` teleport slot cleared on all 20 tiers + resist floor (~8-29%). Occult
>   exception (not golden-tracked). Edit-in-place.
> - **F5 Bloodcrow Flame Nova + Flash Powder.** `firefragmentnova` cd 8->4; Occult `drxflashpowder` cd 15->6 +
>   pierce ladders + `offensiveProjectileFumbleMin` (len-12) + duration 8; `toxeus_flashpowder` cd 20->10;
>   enemy `um_droolbog_43` repointed to base `flashpowder`. Golden gate: 5 per-field `owner_approved_overrides`
>   (Will-authorized); NEGATIVE-TESTED (mutating `drxpoisongasbomb` still fails loud -> scoped waiver proven).
> - **F6 soul naming.** 54 curated OUR-soul renames to `{^F}<Monster> Soul` (+ Xeiwang/limoslifeater SV
>   RESTORES) + an auto-transform for uncovered OURS `Soul of X` (e.g. Blood Shaman). NEW **path-based**
>   provenance gate `_verify_soul_naming` (SV-original-path souls auto-whitelisted, the winning verifier
>   correction #3; SV soul paths captured in `build_svc_database`). SV-original names (e.g. Leveler Soul) untouched.
> - **F7 small items.** (a) Storm mastery-4 panel: Skill25 moved (128,217)->(128,279) off Skill06. (b) Rupture
>   tooltip "Staff Only" -> "Staff or Bow" via `build_text_arc` `TEXT_FIX_TAGS` (single-def, dup-gate-safe).
>   (c) SOUL DESC RENDERING: `_wire_soul_desc_itemtext` wires `itemText` -> the authored DESC tag on 114 souls
>   so amgoz-style flavor text renders. (d) Dayria: `dayria_wolfsummons` ADDED to `dayria_{1,2,3}` specialAttack3
>   + registered.
> - **F1-ripple reconciliations (owned-file, since `create_uber_souls`/`uber_soul_designs.py` are never-commit
>   strays):** B-SOUL-PROC-1 level backstop (create_uber_souls' `_DIFF_SCALE` floored SOUL_DESIGNS level-1 to 0
>   on n/e -> fixed 4 item-skill + 8 augment level-0 grants); MANUAL-CAST backstop (cleared the on-attack
>   controller on the newly-generated mod-authored `summon_mountainblade` chain); foulbeast pet naked-Finger2
>   equip slot zeroed; A4 Aphiastas-zero now gracefully skips the records F1 already de-wired at the root.
> - **GATES (all green):** 5 fail-loud DB invariants + 3 pet gates + RUNEMASTER-GOLEM-BUTTON + golem/soul
>   render validators + the 4 NEW fix-wave gates (F1 cross-wire, F2 summon-identity, F3 diversity, F6 naming) +
>   Occult/Hunting golden freeze (5 waived) + in-build summons contract (B-SUMMON-1 + F2 run_contracts) all
>   PASS. NEGATIVE-TESTED all 5 (F1/F2/F3/F6 seed->SystemExit; F5 golden scoped-waiver). Contracts (with
>   `--text-arc`): **souls 0 P0/0 P1/0 P2, summons 0 P0/0 P1, resources 0 P0/1 P1** (`C-RES-ASSET-1`
>   `anm_dreamcopy` = pre-existing DRX Dream-mastery asset debt, not F1-F7) + 4896 P2 pre-existing SV/DRX debt.
> - **NOTES / open (for Will / follow-up):** (1) the F1 house-pattern new souls (`shadowhero_soul` etc.) are
>   named by `create_uber_souls` from the record name (e.g. "Shadowhero Soul"), not the monster's display
>   ("Phantom Weaver") - a naming-polish item; if Will prefers the de-wired heroes to drop NOTHING instead,
>   that needs a `create_uber_souls` filter change (not-owned). (2) 7 orphan `{^F}Soul of X` tags remain in
>   Text.arc (no soul record references them -> never render; pre-existing dead strings). (3) F5's ~9 off-theme
>   flash-powder souls + the element-filler over-shares (lifedrain 20 / venomspray 14 / etc.) are WARN-listed
>   for the standing souls quality pass, not reassigned this wave.

> 🩸🔧 **BUILD36 LANE A - ROUND 2 (2026-07-11, `feat/build36-lane-a`).** The independent vet returned
> NO_GO on round 1 (1 P2 + 2 P3 + curiosity findings). ALL fixed this round (all in `apply_svc_patches.py`):
> - **A8 GOLEM PANEL (P2, the blocker) - FIXED.** Round 1's "A8 vetted correct, no code fix needed" was
>   WRONG: the golem's `skill23` SkillButton was ORPHANED - it sat in NO mastery-10 panectrl's
>   `tabSkillButtons`, so TQ (no auto-discovery) would never show the Rune Golem on the Runemaster tree.
>   `fix_mastery_panel_buttons` only covers ingameui masteries 1-8 and lives in the parallel-owned
>   `build_svc_database.py`; Lane B's Runemaster buffs edit only menhirwall/mines (NOT the panel). Fix:
>   `_rg_wire_runemaster_panel` reconstructs BOTH base-game mastery-10 panectrl overrides (xpack2 Ragnarok-
>   tier + xpack3 Atlantis-tier, from the verified base field set - base_db is freed + the SV-0.98i-rooted
>   working db never carried the Ragnarok UI) and APPENDS `Skill23` (additive, never renumbers). Covers
>   both DLC configs, the same multi-tier pattern fix_mastery_panel_buttons uses for M1-8. NEW fail-loud
>   gate `_verify_runemaster_golem_button` (Skill23 in BOTH panes + button->summon); negative-tested
>   (`tools/debug/rg_panel_gate_negtest.py` - passes wired, FAILS on dropped button / missing pane /
>   mis-pointed button; idempotent).
> - **PYGMALION PER-TIER (P3) - FIXED.** `_relocate_pet_buffslot_summon` registered the relocated summon
>   at a FLAT level 1, so `replicate.petLimit=3;4;5` indexed to 3 on all soul tiers. New `_tier_source_level`
>   registers the summon at the SOURCE's per-tier level (replicate `skillLevel8=1;2;3` -> the n/e/l pets
>   get 1/2/3 -> petLimit 3/4/5). Threaded `tier=i+1` through `_mirror_source_skill_kit`; the same helper
>   replaces the old raw-array `_source_skill_level` at the kit-registration call (a pet is ONE creature -
>   a level ARRAY on a pet record is meaningless; now always a per-tier scalar). Verified vs the real
>   Pygmalion source (`tools/debug/tier_level_check.py`).
> - **LATENT PET-SUMMON LOSS - HARDENED.** `_relocate_pet_buffslot_summon` used to DELETE the vacated buff
>   slot unconditionally, so a pet with all 5 special slots full + a buff-slot summon would silently LOSE
>   the summon (the skill-kit gate would not catch it). Now the buff slot is deleted ONLY when the summon
>   was relocated (or already fires from an AI slot); otherwise it is KEPT so the PET-SKILL-KIT gate flags
>   it loud. No real pet hits this (all 9 relocate), so zero behaviour change on the shipped set.
> - **BLOODTOXEUS COMMENT (P3) - FIXED.** Rewrote the misleading `_create_blood_toxeus_summon` comment: it
>   claimed an svc->common gear substitution that does not happen. BUILD-ORDER-verified reality: the summon
>   reads `um_bloodtoxeus_99` (a `um_toxeus_99` clone = COMMON gear) BEFORE `_wire_blood_toxeus_loot` swaps
>   the hands to svc, so the pet mirrors the common tables directly (the vet's finding; comment-only).
> - **A5 DORUS polish (curiosity) - ADDRESSED.** (1) Removed the duplicate `skillName6=boss_conversionimmunity`
>   (the donor already registers it at `skillName16`; boss keeps immunity). (2) Swapped soul augment2 from
>   the cold `drxdeathchillaura` to the vitality/decay `drxdeathchillaura_ravagesoftime` (Ravages of Time) -
>   matches the spec's "vitality/decay drx* mod" + his corpse-king vitality sheet; a proven soul augment
>   (Blood-Toxeus soul uses it, gate-green).
> - **TRIAGED (vet-blessed acceptable, flagged for Will):** Dorus soul granted-MOVE (`itemSkillName=None` -
>   the Vashkarr "really-good stat soul" precedent; adding an active is a design escalation needing its own
>   vet), Dorus heavy-melee `attackSkillName` (donor has none -> basic weapon melee + Thunder casts; a
>   special heavy-melee risks anim-castability), Pygmalion "make it crazy" uncapped replicate (kept faithful
>   native `petLimit=3;4;5` per spec "do NOT silently add"). A6 warden is DB-only BY DESIGN (map/quests wave
>   completes it - `docs/reports/build36_laneA_map_needs.md`).
> **GATES (round 2, all GREEN):** full arz rebuild MD5 `32de31a6` (round-1 was `590deb99`; changed by
> design), Text.arc `b89bfe3e` (371,990 B). Built to scratch `local/laneA_r2/` (main `work/` untouched).
> IN-BUILD: the 5 fail-loud invariants + boss-kit clone-shape (5 pairs) + spawn-eligibility (17 proxies)
> + Occult/Hunting golden-freeze + the 3 pet gates (12 families stat-mirror + gear-parity both ways, 201
> pets skill-kit) + the NEW `RUNEMASTER-GOLEM-BUTTON` gate (Skill23 in BOTH panes) all PASS. VERIFIED IN
> THE BUILT ARZ: xpack2 panectrl 23 buttons + xpack3 25, both carry Skill23 -> `_drx_runegolem`;
> pygmalion_1/2/3 replicate in specialAttack5 at skillLevel 1/2/3; Dorus soul aug2 = ravagesoftime (n/e/l),
> um_dorus_99 skillName6 empty (dedup) + skillName16 keeps conversionimmunity. EXTERNAL: golem render-chain
> validator PASS (168 refs), A9 soul render-chain PASS (233 pets/3032 refs, 22 upstream WARN), contracts
> souls+summons+resources **0 P0 / 0 P1** (4891 P2 = pre-existing SV/DRX debt), validate_tags PASS (148 mod
> + 203 authoritative), Text duplicate-tag gate OK. NEGATIVE-TESTED: the new golem gate
> (`tools/debug/rg_panel_gate_negtest.py` - green wired; FAILS on dropped button / missing pane /
> mis-pointed button; idempotent) + the 3 pet gates (`negtest_pet_gates.py`, 12 baseline violations). Det-2x
> deferred to the phase-2 vet per the one-build cap (pipeline deterministic by construction, PYTHONHASHSEED=0;
> the new code adds no sets/unordered-dict iteration). NOT DEPLOYED.
>
> 🩸 **BUILD36 LANE A - DB CONTENT WAVE (2026-07-11, `feat/build36-lane-a`, round 1).** Eight items,
> all DB-side (arz + Text), no map/quests/steam. Reference baseline = the ref build of main @88d2b03
> (`ref_88d2b03.arz` md5 `72eacf8a`); record_diff runs vs it.
> - **A1 PET BUILDER OVERHAUL** (`apply_svc_patches._build_boss_summon` + 3 new fail-loud gates):
>   (1) 12-STAT SOURCE MIRROR - every `_build_boss_summon` pet now mirrors the source monster's
>   `characterAttackSpeed/RunSpeed/SpellCastSpeed/Dexterity/Strength/Intelligence` (+ each Modifier);
>   the 30 boss-summon pets were stuck at the Lyia archer clone (atkSpd 0.5 / DEX 81 / STR 44 / INT 17
>   = 38-56% of the hostile swing rate, near-zero scaling). (2) `_mirror_source_skill_kit` - restores
>   the dropped `specialAttack2-5` boss combat kit (skips hostile `Skill_SpawnPetMonster`) + registers
>   it. (3) STRICT source GEAR MIRROR - `_mirror_source_loadout(strict=True)` auto-derives each pet's
>   loadout from its source (svc/unique source slots get a common substitute), and non-source slots are
>   zeroed, so a pet carries EXACTLY the source's gear (Will's law). bloodtoxeus keeps its weapon;
>   Xeiwang stays gearless; the enslaver skeleton/marauder get their weapons. (4) `_fix_sv_pet_summons`
>   global relocation of buff-slot friendly summons into AI-fired slots (fixes Pygmalion/Aquardia/Dayria
>   "never summons"). THREE NEW GATES wired into the build like the 5 invariants: **PET-STAT-MIRROR**
>   (`_verify_summon_pet_parity`), **PET-GEAR-PARITY** (`_verify_summon_pet_gear`, two-way), **PET-SKILL-KIT**
>   (`_verify_summon_pet_skill_kit`, no summon in a non-AI slot, no hostile spawner on a friendly pet).
>   Negative-tested: `tools/debug/negtest_pet_gates.py` fires all 3 on the e3810219 baseline (90 stat /
>   15 gear / 12 skill violations = bloodtoxeus/enslaver/Pygmalion et al), green after fix.
> - **A2 ENSLAVER REWORK** (`_create_enslaver`): the boss is now an ALL-BLACK SKELETON on the Blood-
>   Toxeus rig (clone um_toxeus_99 -> RevenantPoison.msh + NewSkeleton_Charcoal.tex + Undead; deleted the
>   inherited green `toxeus_envenomweapon` initialSkill; attackSkillName -> toxeus_attackskill). Super-
>   strong ShadowStalker-demon marauders [5000/8500/13000] + rapid many-summon (burst 6 / cd 2 /
>   petLimit 12, summon chance 70); friendly pet-of-pet + yard pack 10; soul renamed
>   `{^F}Toxeus the Murderer, Enslaver of Souls Soul`.
> - **A3 SANGUINE TITHE** (`_create_sanguine_tithe`): the mod's 3rd custom charm - a JEWELRY blood relic
>   (life leech + vitality + %-current-life bleed, GUARANTEED 5/5 leech) off the 9 Sileni combat bodies
>   (7% lootMisc4), Demon's-Blood-donor pattern (no new art); Sileni names -> green `{^G}` via
>   build_text_arc TEXT_FIX_TAGS.
> - **A4 APHIASTAS SOUL DROP -> 0** (`_apply_aphiastas_finger2_zero`): chanceToEquipFinger2=0 on the 7
>   Aphiastas keres records (souls-only Finger2 proven), loot refs + potion recipe kept; runs before the
>   drop-forcer so it holds in test AND release.
> - **A5 PROPONTIS SUPER BOSS "Dorus, the Drowned King"** (`_create_propontis_superboss`, DB side only):
>   Boss [41,57,71] HP 13.5/18.5/24k on the questline royalty rig, ThunderClap/ball + raise-court summon;
>   Common courtier fodder + Champion royal-guard escorts; lone pool/proxy; Boss-locked hoard (reuses the
>   Obsidian Hoard chest/pool); dense S1 stat soul; TESTHUB yard. **Map placement pending -> see
>   `docs/reports/build36_laneA_map_needs.md`** (host Medea_TempleUG_Tomb01, primary WORLD (312,1.2,-8462)).
> - **A6 WARDEN SPLIT-FIX** (DB side): added the 2 singly-placed master records
>   `svc_testhub_master_helos/_cave` (reuse the same tags, no Text change) so the double-placed hub NPC
>   (byte-proven H1 mute-but-visible) is retired. **Quests trigger + map placement pending -> same report.**
> - **A7 TEXT TAGS**: every new/changed name+desc tag rides the tags dict -> uber_soul_tags.txt ->
>   `build_text_arc.py`; the Sileni `{^G}` override went through TEXT_FIX_TAGS (single-definition) to
>   avoid the duplicate-tag gate. tags invariant must pass clean.
> - **A8 RUNE GOLEM VET+FINISH**: hostile review of the pre-vet graft (main @88d2b03) = CORRECT. "mastery
>   10" IS Runemaster (base slots 1-22 are Runemaster skills), skill23 is the correct free UI slot, the
>   golem's `Skill_DefensiveGround` class + `masteryLevelRequired=None` MATCH sibling `menhirwall`, prereq
>   repointed to vanilla, render closure resolves. `validate_render_chain_golem.py` PASSES with real args.
>   No code fix needed. Minor note (in-game only): skillMaxLevel 16 vs the 20-tier pet ladder is a faithful
>   SVAERA-snapshot artifact (tiers 17-20 vestigial, harmless).
> **GATES (all GREEN, verified this round):** full arz rebuild `590deb99` (50,652 recs, vs ref@88d2b03
> `72eacf8a`) - the 5 fail-loud invariants + boss-kit clone-shape (5 pairs) + spawn-eligibility (17
> proxies) + golden-freeze all PASS; the THREE NEW pet gates PASS (12 families stat-mirror + gear-parity
> both ways, 201 pets skill-kit); det pending (single build this round). `negtest_pet_gates.py` fires all
> 3 on the e3810219 baseline (90/15/12) + PASS on the build36 arz. `validate_render_chain_golem.py` PASS
> (real args). Text.arc rebuilt from restored SV source: duplicate-tag gate OK, `validate_tags` PASS (148
> mod refs + 203 authoritative). Contracts summons+resources **0 P0 / 0 P1** (4891 P2 = pre-existing
> SV/DRX debt). Coupled ship set on the eventual wave: arz + Text (+ Quests/Levels for the A5/A6 map wave).
> **OPEN (for Will / in-game vet):** eyeball bloodtoxeus/all-pet damage after the STR/INT raw-mirror
> (may over-tune); confirm the A2 all-black skeleton renders + summon cadence; the A5 map placement +
> A6 quests/map split are separate waves; A3 jewelry relic-slot scarcity QA (fallback = weapon+jewelry);
> A2 enslaver boss keeps full Hero loot (renders geared - clear the equip tables only if Will wants a
> lean rare). Full detail: the build36 specs + `docs/reports/build36_laneA_map_needs.md`. NOT DEPLOYED.

> 🕷️ **BROODMOTHER NEST - MAP LANE PLACED (build35, 2026-07-11; tag build35).** The map lane placed
> the DB lane's broodmother-nest proxies (arz `a947e98d` + Text `3fb65c20`, both already staged in
> `work/`), per `docs/BROODMOTHER_NEST_DESIGN.md`. **This is the FIRST canonical-map content change
> since build32b** (Will-approved; intended). NEW map MD5s (det-2x reproduced byte-identical, each
> built twice): canonical `local/Levels_merged.arc` = **`391b267461bbb7e75b0f965d6e298ff7`** (was
> build34 `d5259629`); TESTHUB `local/Levels_merged_TESTHUB.arc` = **`ea928648e2ede29abe00a6e87ff4900c`**
> (was build34 `8d30ec53`). arz/Text/Quests UNCHANGED by the map lane.
> **WHAT (map hooks, `tools/build_section_surgery.py` sole-owned; svaera_plus_portals.py untouched -
> tombobs02 already routes through the INJECT_SPECS v0e branch):**
>   (1) CANONICAL SET-PIECE = `BROODNEST_SPECS` (7 proxies) APPENDED to `INJECT_SPECS`'s existing
>       tombobs02 roulette list (order-preserving -> roulette keeps its indices). Host
>       `levels/world/orient/typhonug/tombobs02.lvl` (the doc's recommended primary, the deep Act-3
>       Obsidian Halls hall the roulette already dresses). Applies to BOTH variants (canonical uses
>       INJECT_SPECS; TESTHUB layers hub extras on top).
>   (2) TESTHUB YARD = `q_yard_broodmother` APPENDED (9th entry) to `build_hub_extra_specs()`'s HV01
>       list (SVC_TEST_HUB-gated -> canonical byte-unchanged in HV01).
> **PLACEMENT MANIFEST (host level; LOCAL x,y,z; nest center local (184,192), 6-egg ring r=10u,
> floor local Y 1.20; surveyed on-mesh in ALL 3 tilesets, 100% clearance at each record's real
> placementExtents [mother 3.5u, eggs 2.5u], nearest native > extents+2u):**
>   - `q_broodmother_lone`  tombobs02  L(184.0,1.2,192.0)  WORLD(-1794,-73.8,-298)  clr all-3-set 100%, nearestNative 14.4u
>   - `q_broodnest_egg_a`   tombobs02  L(184.0,1.2,202.0)   ring N
>   - `q_broodnest_egg_b`   tombobs02  L(175.3,1.2,197.0)   ring NW
>   - `q_broodnest_egg_c`   tombobs02  L(175.3,1.2,187.0)   ring SW
>   - `q_broodnest_egg_d`   tombobs02  L(184.0,1.2,182.0)   ring S
>   - `q_broodnest_egg_e`   tombobs02  L(192.7,1.2,187.0)   ring SE
>   - `q_broodnest_egg_f`   tombobs02  L(192.7,1.2,197.0)   ring NE
>   - `q_yard_broodmother`  hiddenvalley01 (TESTHUB)  L(89.0,6.6,100.0)  42.3u from nearest yard group (obs_ilsevar)
> **ROULETTE SEPARATION (Will's >=40u no-merge rule):** the nest sits 82.0u from the corner-C
> warband edge (placementExtents 4.0) and 128.2u from corner-A; min point-to-corner-centre dCornerA
> 132.2u / dCornerC 86.0u. World corner tombobs02 = (-1978,-75,-490). Corners A local (50.4,143.6),
> C (200.4,97.6). Far past 40u -> encounters cannot merge.
> **GATES (all GREEN, both variants):** parse-back (`gate_build32_parseback.py`, extended: M10
> tombobs02 now expects the 7 broodnest appended after the 2 roulette; MYARD now +9 incl
> q_yard_broodmother) PASS on canonical (M8+M9+M10) and TESTHUB (M8+M9+M10+MYARD+RIG); MAP-REF-1
> (`run_contracts.py --only map`, both maps vs arz `a947e98d`) 0 P0/0 P1 (3 P2 = pre-existing
> base-game XPack Act3/Styx portals, not the nest); navmesh 24/24 both; groups-bindings 374/374
> both; det-2x both byte-identical. **BLOB-DIFF proof:** canonical NEW vs build34 `d5259629` = EXACTLY
> 1 level changed (tombobs02, section 0x05 only, count 580->587 = +7 set-piece); TESTHUB NEW vs
> build34 `8d30ec53` = EXACTLY 2 levels (tombobs02 0x05 580->587 set-piece + hiddenvalley01 0x05
> 230->231 = +1 yard broodmother). Every other level+section byte-identical.
> **STAGING:** the new canonical `391b2674` is STAGED into `work/SoulvizierClassic/Resources/Levels.arc`
> (the coupled ship trio is now arz `a947e98d` + Text `3fb65c20` + Levels `391b2674`; ships on the NEXT
> Steam package after Will's DEV pass, per the QA-gated ship law). Packager TESTHUB-MD5 guard state OK
> (work Levels `391b2674` != TESTHUB `ea928648` -> no abort). **NOT DEPLOYED** (no dist/ write, no
> SteamCMD, no CustomMaps copy). Deploy coupling on the eventual wave: canonical Levels + arz + Text
> ship together (the set-piece is inert without the arz records/tags, already present).


> 🧭 **STANDING RULING - IMMORTAL-THRONE CAP (Will, 2026-07-10).** The campaign stays capped at
> **Immortal Throne (Hades)** for now. Do NOT make Atlantis or anything past IT reachable. Focus is
> fine-tuning the Greece-to-Hades game. The Tartarus-arena-gates fix and the Rhodes->Atlantis entry
> cap are **PARKED** under this ruling (see the build32-ship note's Tartarus/Atlantis recon block
> below, now marked PARKED). This joins the prior "campaign ends at Hades for ALL DLC combos" rule
> (HANDOFF_LIVE_STATE §6) - DLC integration remains CANCELLED; revisit only if Will later decides to
> add the post-IT areas. Quote (Will): "lets not make atlantis or anything past immortal throne
> reachable for now and we will fine tune immortal throne then if we want to add in the other areas
> later then we can."

> 🕷️ **BROODMOTHER NEST - DB LANE IMPLEMENTED (2026-07-10, Will 'proceed with the broodmother nest
> implementation'; 7 flagged decisions DELEGATED = take each doc recommendation, amgoz1 taste, NO
> artificial caps).** The deferred apex of the N7 sepulchral-wyrm-horde chain, per
> `docs/BROODMOTHER_NEST_DESIGN.md`. Baseline = graft-lane Group 0 arz `ef52a476`. NEW arz
> **`a947e98dd97d5cd4fe5eb8eded302b37`** (det-2x reproduced byte-identical). Text COUPLED + changed:
> `6c84d66d`->**`3fb65c20`** (6 new tags). Quests/Levels UNCHANGED. record_diff vs `ef52a476` = EXACTLY
> **25 ADDED + 0 MODIFIED + 0 REMOVED**, 0 collateral.
> **RECORDS (apply_svc_patches `_create_broodmother_nest`, hooked AFTER `_create_wyrm_hordes`):**
> boss `um_broodmother_99` (Eater-of-Days `um_eaterofdays_45` derivation - D13-render+summon-proven rig;
> Boss, band [40,58,74], HP [22k,30k,40k], scale 1.9/height 2.4, cold wall Life100/Pierce60/Cold80/
> Phys30; kept the eater's anim-safe wyrm kit + Hero->Boss passives + firebreath + the brood-summon);
> the UNCAPPED hostile brood-summon `svc_broodnest_summon` (yaoguai clone, boss-kit clone-shape gated;
> burst 4 / cd 5s / petLimit 24; spawns PURE common wyrmlings `um_sepulchralwyrm_common_31` - fodder
> churn, no scale-spam); egg-cluster hatch pool `svc_broodnest_hatch` (3-6 common, champ 0);
> `limit_broodnest` (herolimit_all clone bumped to [1..110]); lone-boss pool `svc_broodmother_pool`
> (spawnMax=3/championMin=Max=2 -> 1 guaranteed mother + 2 `um_sepulchralwyrm_40` elder-worm escorts;
> LAW holds); 1 lone proxy `q_broodmother_lone` + 6 egg proxies `q_broodnest_egg_{a..f}` (all
> chanceToRun=100, no-cap limit; map lane places them, recommended host tombobs02); the SOUL chain -
> fresh manual `summon_broodmother` + `broodmother_{1,2,3}` pets via `_build_boss_summon` (NO
> itemSkillAutoController; D19 mobility + damage-sanity STRICT) PLUS the pet-of-pet brood twist
> (`summon_broodmother_wyrmlings` + `broodmother_wyrmling_{1,2,3}` on the SepulchralWyrm01 rig,
> isPetDisplayable off, petLimit 6 - the friendly broodmother pet auto-raises FRIENDLY wyrmlings,
> Enslaver precedent); soul `broodmother_soul_{n,e,l}` (svc_uber dir; cold/vitality sheet, augments
> drxcoldaura+drxdeathchillaura, weird stat defensiveFreeze 100, 66% Finger2 ONLY on the mother);
> guaranteed apex loot = tier-03 Sepulchral Scale on the mother's dedicated Misc3 slot @100%; TESTHUB
> yard `q_yard_broodmother` pool+proxy (mother + 2 escorts @100%, q_yard_ namespace, REAL records).
> **7 DECISIONS TAKEN (all doc recommendations):** (1) host tombobs02 [MAP lane; DB provides proxies];
> (2) rig = Eater-of-Days (D13-proven); (3) density = 6 clusters + petLimit 24 [crazier / no caps];
> (4) fresh summon_broodmother WITH pet-of-pet friendly wyrmling brood; (5) guaranteed tier-03 scale +
> soul, NO 4th-tier charm rung; (6) egg-sac props = FUNCTIONAL-ONLY [design says don't block; map-lane
> cosmetic follow-up if a clean mesh resolves]; (7) Tartarus/Atlantis = PARKED per the IT-cap ruling
> above [no action]. Refinements noted: the brood-summon spawns pure common wyrmlings (not the scale-
> dropping champion worms) to avoid loot-spam - the 2 guaranteed champion escorts come from the pool;
> limit_broodnest is a herolimit_all clone bumped to [1..110] (build-order-independent) rather than a
> limit_obsidianbosses clone.
> **GATES (all GREEN):** record_diff exactly 25 ADDED/0 else; boss-kit clone-shape 4 pairs OK;
> spawn-eligibility 15 proxies OK (q_broodmother_lone + q_yard_broodmother registered; mother L74 <=
> limit 110; spawnMax-championMax=1); summon-pet STRICT 0 failures (manual-cast law + damage-sanity +
> D19 + clone-shape); soul-augment + activation OK; validate_tags PASS (134 referenced mod tags);
> render-chain (A9/D5) PASS (233 pets/3032 art refs - eaterofdaysmesh + SepulchralWyrm01 + all
> summons); Occult/Hunting golden (A7) PASS; MP spawn-equation '/'-free; soul-leak 0; negtest_roaming_
> yard ALL OK (broodmother pools don't carry the Enslaver -> no whitelist needed; positive/real-arz
> PASS); negtest_container_shape ALL OK; det-2x arz `a947e98d` + Text `3fb65c20` both byte-identical.
> **MAP HANDOFF (MAP-REF-1; arz `a947e98d` must land before placements):** inject the lone proxy
> `records\drxmap\proxy\q_broodmother_lone.dbr` (the mother + 2 escorts set-piece) + 6 egg-cluster
> proxies `records\drxmap\proxy\q_broodnest_egg_{a,b,c,d,e,f}.dbr` in an OPEN >=8u-radius disc of the
> recommended host `levels/world/orient/typhonug/tombobs02.lvl` (survey each on-mesh/all-tilesets/100%
> per the M9/M10 pattern; the 6 eggs ring the mother). YARD SPOT: inject
> `records\drxmap\proxy\q_yard_broodmother.dbr` in the TESTHUB monster yard (SVC_TEST_HUB-gated). All
> are flags=0/no-0x14 q_leinth_lone-shape proxies. Coupling on eventual deploy: arz + Text ship together
> (canonical Levels unchanged until the map lane injects). NOT DEPLOYED (no dist/, no SteamCMD; map
> tools untouched).

> 🎭 **SVAERA MASTERY GRAFT (DB lane, 2026-07-10, Will approved 'yes make them').** Implementing
> `docs/SVAERA_MASTERY_COMPARISON.md` additively (soa verbal permission recorded in
> `docs/PERMISSIONS.md`). **GROUP 0 (ANM-row completion) LANDED:** `build_svc_database`
> `_complete_pc_anim_melee_rows` restores the dropped vanilla melee anim clips
> (Hew/Ensnare/Crosscut/Barrage/ThunderClap) onto the FULL dHanded/sHanded/spear rows of
> anm_malepc01.dbr + anm_femalepc.dbr at indices >15 (byte-identical to base==SVAERA clips; 'Rest'
> preserved; add-only). Unblocks the 6 half-casting melee skills (Exploding Strikes/Hail of
> Axes/Arc Attack/Chi Realignment/Shen Pao/Smoke Cloud) and is the Warfare-Slam prerequisite.
> Paired guard: the soul pcsafe universal set (`apply_svc_patches._pc_universal_special_anims`) is
> bounded at index<=15 so the >15 additions never suppress a soul's pcsafe clone (no soul
> regression if the engine's SpecialAnimRef read cap is truly 15). record-diff vs c7da07f6 =
> EXACTLY the 2 anm tables. **IN-GAME CONFIRM STILL NEEDED (per doc + MASTERY_AUDIT):** whether the
> engine reads SpecialAnimRef>15 - a melee cast test confirms; if the 15-cap is real the additions
> are inert (no regression). Groups 1 (additive skill grafts) + 2 (permissions/ruling docs) status
> tracked in the DB-lane report.

> 🚪 **PORTAL TEST RIG - MAP LANE (Model C boat-dialog NPCs) LANDED (2026-07-10, autonomous map-lane).**
> Places the DB lane's 2 rig NPC records (arz `c7da07f6`) so the flag-gated LOCAL-ONLY travel rig is now
> LIVE on the TESTHUB entry. RESOLVES the map-lane PORTAL-RIG DEFERRAL (see the yard-map-lane note below).
> MAP artifacts: canonical `local/Levels_merged.arc` = **`d5259629`** (688,684,102 B; REPRODUCED
> byte-identical -> the rig is strictly TESTHUB-only); TESTHUB `local/Levels_merged_TESTHUB.arc` =
> **`8d30ec533b19e7775a819a6a9d3c19c7`** (688,689,898 B; det-2x reproduced byte-exact), was build33
> `37f58d29`. Text/Quests/arz UNCHANGED by the map lane (the DB lane's coupled `c7da07f6`/`6c84d66d`/
> `56acee66` ship with it).
> **WHAT (map hooks - `tools/build_section_surgery.py` + `tools/svaera_plus_portals.py`, sole-owned):**
>   (1) `build_hub_extra_specs()` extended with the 7 rig placements (+ the 8 build33 yard placements kept
>       INTACT): 2 `svc_testhub_master` hub NPCs + 5 `svc_testhub_return` NPCs, all flags=0 / no-0x14 /
>       identity-rot, folded into INJECT_SPECS ONLY when SVC_TEST_HUB=1 (append-only -> canonical byte-
>       unchanged).
>   (2) GridEntrance TEST HUB **RETIRED** (Will's order: Model C, NOT the born-open B-PORTAL-1/2/3 blue-pane
>       /walkway-force-teleport/dead-return portals): `merge_hub_into_inject_specs` no longer folds
>       `build_hub_inject_specs` (kept defined+unused for reference); the swap path applies
>       `build_hub_extra_specs()[R09_KEY]` to the SV blood-cave blob. R09_KEY is EXCLUDED from the normal
>       fold (random09a is rebuilt by the swap path). **SIDE EFFECT (a fix):** retiring reverts TESTHUB
>       random09a from the pre-existing build33 AE-silkroad-blob quirk (0x0b 58226, corner/geometry
>       mismatch) BACK to the canonical SV blood-cave swap blob (0x0b 115749 byte-identical to canonical)
>       + the hub master -> the "fewer instances random09a" gate quirk is now GONE (append-only prefix).
> **PLACEMENT MANIFEST (host level; LOCAL x,y,z; WORLD x,y,z; survey vs canonical 0x0b):**
>   - `svc_testhub_master`  startingfarmland06d (AE v0x11)   L(79.5,0.8,189.5)   W(-5968.5,1.8,917.5)  3u E of canonical Almyros, clr@3.0=100%, comp0
>   - `svc_testhub_master`  random09a (SV blood-cave swap)    L(32.0,1.0,45.0)    W(6011,19,3288)       8.6u from the boat-dialog Blood-Cave landing (6018,19,3293) = the dominant blood-cave arrival, clr@3.0=100%, comp0
>   - `svc_testhub_return`  gardenofmerchants (SV-only v0e)   L(133.0,-39.0,73.0) W(1176,-39,-4001)     3u E of landing, comp1 (= the Almyros landing comp), clr@3.0=100%
>   - `svc_testhub_return`  darkforestenter (SV-only v0e)     L(27.0,1.0,30.0)    W(-2393,1,-5790)      3u E of landing, comp0, clr@3.0=100%
>   - `svc_testhub_return`  crypt_floor1 (SV-only v0e)        L(140.0,10.0,229.0) W(-2438,10,-2453)     3u S of landing, single comp, clr@3.0=96%
>   - `svc_testhub_return`  spartacryptlevel2 (SV-only v0e)   L(45.0,-1.6,42.0)   W(-5599,-1.6,-1409)   3u E of landing, comp0, clr@3.0=100%
>   - `svc_testhub_return`  boss_arena (SV-only v0e)          L(131.0,0.0,40.0)   W(-430,0,-3602)       3u E of landing (~90u off volume_startolympianarena), comp0, clr@3.0=100%
> **GATES (all GREEN):** canonical md5 == `d5259629` (byte-identical to build33); parse-back
> M8+M9+M10+MYARD+**RIG** PASS (each rig host = canonical + 1 appended flags=0 NPC, EVERY other section
> incl 0x0b/0x06/0x14 byte-identical; extended `tools/debug/gate_build32_parseback.py` with the RIG
> section + testhub-aware M8); MAP-REF-1 (`run_contracts.py --only map`, TESTHUB vs new arz) 0 P0/0 P1
> (3 P2 = the pre-existing base-game XPack Act3/Styx portals); navmesh 24/24; groups-bindings 374/374
> 0 DEAD (both variants); entrance_landing PASS; det-2x TESTHUB byte-identical (`8d30ec53`). NOTE: the
> untracked, parked `gate_doors_hub.py hubidentity` FAILs ONLY because its hardcoded hub-level whitelist
> predates the Model C rig (flags startingfarmland06d/crypt_floor1 as UNEXPECTED); every level it checks
> shows the correct +1/+8 prefix, and the parse-back RIG section proves the prefix for all 7 hosts.
> **PACKAGER:** the TESTHUB-MD5 guard hashes BOTH files at RUNTIME (no hard-coded md5), so the TESTHUB md5
> change (`4fb76084`->`8d30ec53`) needs NO packager edit; work/ staging holds canonical `d5259629` (guard
> prints OK, would ABORT if `8d30ec53` were ever staged).
> **DEPLOY COUPLING:** TESTHUB `Levels.arc` (`8d30ec53`) + arz (`c7da07f6`) + Text (`6c84d66d`) + Quests
> (`56acee66`) ship together to the DEV entry; canonical `Levels.arc` UNCHANGED.

> 🚪 **PORTAL TEST RIG - DB LANE (Model C boat-dialog NPCs) IMPLEMENTED (2026-07-10, autonomous DB-lane).**
> UNBLOCKS the map-lane PORTAL-RIG DEFERRAL + the DB-lane GROUP 2 DEFERRAL below. Baseline = build33 arz
> `e3810219`. NEW arz `c7da07f6efb8b14c27cf4a628824d133` (det-2x reproduced byte-exact). Text + Quests
> are COUPLED and changed; Levels UNCHANGED (map lane owns placements): Text `346572bb`->`6c84d66d`,
> Quests `6ff23c29`->`56acee66`. Record-diff vs `e3810219` = EXACTLY **2 ADDED + 0 MODIFIED + 0 REMOVED**,
> 0 collateral.
> **RECORDS (apply_svc_patches `_create_testhub_portal_npcs`, hooked right after `_create_helos_portal_
> master`):** 2 NPCs cloned from the proven boat-dialog donor `records\creature\npc\speaking\greece\
> knossos_boatmantoegypt.dbr` (the Almyros/Keryx shape; GreekSailor02 mesh+baseTexture inherited
> BYTE-IDENTICAL -> render-safe per the D5 law):
>   `records\quests\svc_testhub_master.dbr` (HUB portal-master; map lane places it TWICE - Helos plaza +
>     blood-cave-mouth strip) and `records\quests\svc_testhub_return.dbr` (RETURN NPC; map lane places it
>     once inside each of the 5 SV areas). Added UNCONDITIONALLY, INERT on canonical (map places neither).
> **TRIGGERS (build_quest_files `_add_testhub_portal_travel`, CHAINED onto the Helos patch in the always-
> loaded `sv_commonmechanics.qst` refire step; registry law respected - NO new QUESTS registration):**
> one `Condition_OnLevelLoad` trigger per NPC (trigger `max` bumped +2), keyed on the DISTINCT rig records
> ONLY (never canonical Almyros - no leak): HUB (svc_testhub_master) = 7 `Action_BoatDialog` ports; RETURN
> (svc_testhub_return) = 2 ports. Fail-loud ref-delta checks (hub NPC +7, return NPC +2, per-tag deltas) +
> stable round-trip. Parse-back confirms 7+2 ports, exact SIGNED coords, Almyros untouched (4 ports, 0 leak).
> **DESTINATION TABLE (all 7 landing coords SURVEYED on-mesh against canonical d5259629 0x0b navmeshes):**
>   - Garden of Merchants ( 1173,-39,-4001) GardenofMerchants.lvl  tagSVCHelosToGarden  [Almyros table, re-verified]
>   - The Secret Place    (-2396,  2,-5790) DarkForestEnter.lvl    tagSVCHelosToSecret  [re-verified]
>   - The Uber Dungeon    (-2438, 10,-2450) crypt_floor1.lvl       tagSVCHelosToUber    [re-verified]
>   - The Sparta Crypt    (-5602, -2,-1409) SpartaCryptLevel2.lvl  tagSVCHelosToSparta  [re-verified]
>   - The Boss Arena      ( -433,  0,-3602) boss_arena.lvl         tagSVCTestHubToBossArena [NEW; 0x0b-surveyed on-mesh (largest comp 1.38M cells, floorY 0), **90u off volume_startolympianarena** so boss step-in stays player-controlled]
>   - The Blood Cave      ( 6018, 19, 3293) Random09A.lvl          tagSVCTestHubToBloodCave [NEW; **RE-DERIVED** - the spec's (-168,19,2162) is ~6200u STALE (Random09A now at corner (5979,18,3243)); this is proven-band local (29.9,1,26.9)+corner, 27.6u off the jo04 shrine ghost pool, largest comp, floorY 19]
>   - Helos (Return)      (-5980,  1,  909) StartingFarmland06D.lvl tagSVCTestHubToHelos  [NEW; surveyed on-mesh, floorY 0.6]
>   RETURN NPC menu = Helos (-5980,1,909) + Blood Cave (6018,19,3293).
> **TEXT (7 NEW tags via the tags dict -> uber_soul_tags.txt -> Text.arc; the 4 Almyros labels are
> REUSED):** tagSVCNpcTestHubMaster='Waypoint Warden (Test Rig)', tagSVCTestHubMasterChat,
> tagSVCNpcTestHubReturn='Return Warden (Test Rig)', tagSVCTestHubReturnChat, tagSVCTestHubToBossArena=
> 'The Boss Arena', tagSVCTestHubToBloodCave='The Blood Cave', tagSVCTestHubToHelos='Helos (Return)'.
> **STEAM-INERTNESS (explicit mechanism):** `Action_BoatDialog` attaches its menu to the NPC ENTITY in the
> loaded level; canonical places NEITHER rig NPC, so both triggers no-op there (D3 unplaced-record
> precedent + the Almyros shape). Proven by `tools/debug/gate_testhub_portal_rig.py` part B: canonical
> `local/Levels_merged.arc` = **0 master + 0 return** placements. (The rig NPC records + triggers + tags
> DO ship inside arz+Quests+Text but are inert on Steam - the sanctioned flag model.)
> **GATES GREEN:** record-diff = 2 ADDED/0 else; validate_tags PASS (129 mod refs + 185 authoritative);
> contracts quests/souls/summons/resources **0 P0/0 P1** (4891 P2 all pre-existing base/upstream);
> render-chain gate part A (mesh GreekSailor02.msh resolvable + 1 internal shader ok + baseTexture in
> base Creatures.arc; both rig NPCs share donor art); inertness gate part B (0 canonical placements);
> roaming-yard negtest ALL OK (sweep byte-unaffected, still 1224 pools + 1 yard whitelist); in-build
> summon-pet STRICT + A9 render + A7 Occult/Hunting golden + container-loot-shape PASS; det-2x
> byte-identical (arz/Text/Quests). **NOT DEPLOYED (no dist/, no SteamCMD; map tools untouched).**
> **COUPLING on eventual deploy:** arz + Quests + Text ship together (canonical Levels unchanged).
> **HANDOFF TO MAP LANE (to make the rig live on the TESTHUB entry):** extend `build_hub_extra_specs`
> (SVC_TEST_HUB-gated) to place svc_testhub_master at Helos (~local (79.5,0.6,189.5), a few u off canonical
> Almyros) AND at the blood-cave-mouth strip (random09a flank; the HV01 monster yard is a DIFFERENT level,
> so no 40u conflict with the Random09A landing), and svc_testhub_return once inside each of Garden/Secret/
> Uber/Sparta/BossArena a few u from that area's landing coord above. Recommend RETIRING the existing
> Random09A GridEntrance hub's 5 dest pairs (spec sec 8 #7) so Will never tests the known-dead
> appended-host returns. Refresh the packager's TESTHUB-MD5 guard (it hashes at runtime, no hard-coded md5).

> 🗺️ **MONSTER TEST YARD (MAP LANE) + PORTAL-RIG DEFERRAL (2026-07-10, autonomous map-lane).**
> Couples with the DB-lane yard note below (arz `e3810219`). MAP artifacts: canonical
> `local/Levels_merged.arc` = **`d5259629`** (REPRODUCED byte-identical -> the yard change is
> strictly TESTHUB-only); TESTHUB `local/Levels_merged_TESTHUB.arc` = **`37f58d29`**
> (688,649,020 B, det-2x reproduced), was build32b `4fb76084`. Text/Quests UNCHANGED
> (`346572bb`/`6ff23c29`).
> **WHAT (map hook):** `build_section_surgery.py::build_hub_extra_specs()` (was `{}`) now returns
> the 8 monster-yard proxy placements in HiddenValley01 (Silk Road), folded into INJECT_SPECS
> ONLY when `SVC_TEST_HUB=1` (append-only after HV01's 222 base instances -> canonical HV01 byte-
> unchanged; parse-back MYARD proves 222->230, every other section incl. 0x0b navmesh byte-
> identical). Each is a flags=0 / no-0x14 proxy (the q_vashkarr_lone byte-shape). SPOT B reuses
> the existing `q_vashkarr_lone.dbr` (already placed canonical at FotA; 2nd TESTHUB placement
> needs no new record). **FINAL COORDS (re-surveyed on-mesh + clearance vs the real HV01 0x0b
> navmesh; the C obsidian pocket was re-nudged since the raw spec coords hit walls/villager):**
> a down-valley gauntlet from the blood-cave mouth (local, HV01 corner (-134,-120,2174)):
> q_yard_enslaver (23.0,17.0,33.0), q_yard_marauders (31.9,16.2,26.9), q_vashkarr_lone
> (36.0,16.0,28.5), then the OBSIDIAN WARBAND cluster Z87-95 [q_yard_obs_sarkoth (42.0,15.2,91.0),
> q_yard_obs_gorrahk (36.0,15.2,90.0), q_yard_obs_voranthys (47.0,15.4,87.0), q_yard_obs_ilsevar
> (47.0,15.2,95.0), each own guardian + 5-elite warband, mutually >=6.1u, >=9.8u off the villager],
> then q_yard_wyrm (30.0,15.2,113.0) [dFount 30u]. ALL 8: on-mesh, on-largest-component, 100%
> clear at their placementExtents, flags=0.
> **STANDING DEV TEST PATTERN (how to enable/disable the yard AND the portal rig on the DEV entry):**
> BOTH the monster yard AND the Model C portal rig ride the SAME TESTHUB map. [UPDATED 2026-07-10 by the
> portal-rig map lane: the TESTHUB map is now `8d30ec53` (was 37f58d29) and the coupled DB set is arz
> `c7da07f6` + Text `6c84d66d` + Quests `56acee66` (was arz e3810219, no Text/Quests).]
> TO ENABLE: deploy `local/Levels_merged_TESTHUB.arc` (`8d30ec53`) as the DEV entry's
> `Resources/Levels.arc` + arz `c7da07f6` as `SoulvizierClassicDEV.arz` + Text `6c84d66d` as
> `Resources/Text.arc` + Quests `56acee66` as `Resources/Quests.arc` (the four ship as a coupled set).
> YARD: walk a Custom-Quest char into HiddenValley01, out the cave mouth -> Enslaver+marauders,
> Vashkarr+2 champs, the 4 Obsidian guardians+warbands, the wyrm horde (each @100%). PORTAL RIG: at
> Helos, click the "Waypoint Warden (Test Rig)" NPC ~3u E of Almyros -> 7 ports (Garden/Secret/Uber/
> Sparta/Boss Arena/Blood Cave/Helos); in the blood cave (arrive via any hub's "Blood Cave" port ->
> world (6018,19,3293)) the same Warden stands ~8.6u away; inside each SV area a "Return Warden (Test
> Rig)" stands ~3u from where you land -> 2 ports (Helos + Blood Cave). TO DISABLE (restore canonical,
> e.g. for a co-op-safe DEV): deploy `local/Levels_merged.arc` (`d5259629`) as the DEV
> `Resources/Levels.arc` (arz/Text/Quests unchanged; the yard + rig records go inert with no map
> placing them). The yard records ship in the
> shared arz UNCONDITIONALLY but are INERT on canonical/Steam (the packager's live TESTHUB-MD5 guard
> - which hashes `local/Levels_merged_TESTHUB.arc` at runtime, no hard-coded md5 - still ABORTS on
> 37f58d29, so the yard can never reach Workshop). Tune the fight by editing the REAL monster
> records in the arz (see the DB-lane tuning table); the yard follows 1:1.
> **GATES (all GREEN, map-lane):** canonical md5==d5259629; parse-back M8+M9+M10+**MYARD** PASS;
> MAP-REF-1 = 0 P0/0 P1 on TESTHUB vs the new arz (3 P2 = pre-existing base-game XPack Act3/Styx
> portals, not the yard); navmesh 24/24; groups-bindings 374/374 (0 DEAD); det-2x TESTHUB byte-
> identical; all 8 instances on-mesh in the single HV01 tileset. `gate_doors_hub hubidentity`: the
> HV01 yard append passes (canonical is a byte-exact prefix of the +8 hub HV01); its random09a
> "fewer instances" flag is PRE-EXISTING (random09a byte-identical to the shipped build32b TESTHUB
> 4fb76084; that gate is an untracked debug tool with a stale subset assumption for random09a).
> **PORTAL RIG (Helos + blood-cave-entrance hubs): RESOLVED 2026-07-10** (was DEFERRED this build).
> The 2 hub + 5 return Model C NPCs are now PLACED on the TESTHUB entry (TESTHUB map -> `8d30ec53`) and
> the GridEntrance hub is RETIRED - see the PORTAL TEST RIG - MAP LANE note at the TOP of this file for
> the placement manifest, gates, and the random09a-blob fix. [UPDATE 2026-07-10: the DB
> footprint now EXISTS - see the PORTAL TEST RIG - DB LANE note at the TOP of this file (arz c7da07f6,
> +2 NPC records svc_testhub_master/return, boat-dialog triggers, 7 tags). The map-only `build_hub_extra_
> specs` extension to PLACE the 2 hub + 5 return NPCs is now unblocked; the destination coords are surveyed.] The portal spec's settled
> mechanism (Model C BoatDialog portal-master, the ONLY one with working returns from appended
> SV-only areas) needs +2 NPC records (`svc_testhub_master`/`svc_testhub_return`), boat-dialog
> triggers in `sv_commonmechanics.qst`, and ~5-7 Text tags - all of which the DB lane explicitly
> DEFERRED (GROUP 2; verified ABSENT from arz e3810219). Placing those NPC records would fail
> MAP-REF-1. The only map-only alternative (born-open GridEntrance) ships exactly the B-PORTAL-1/2/3
> bugs (blue-pane render, walkway force-teleport, DEAD returns from every SV area) the design is
> RETIRING, so it is not a valid deliverable. Will ALREADY has working Helos->SV forward travel via
> the canonical Almyros/portal_master_helos BoatDialog NPC (4 dests), and the existing Random09A
> GridEntrance hub (5 dests, LEFT untouched) covers rough forward walk-testing. TO UNBLOCK: run a
> coordinated portal wave = DB lane builds the 2 NPC records + boat-dialog triggers + tags, THEN the
> map lane places the 2 hub NPCs + 5 return NPCs (Model C) per PORTAL spec sections 1-3. This is a
> map-only-code change here (`build_hub_extra_specs` extension) once those records exist.

> 🧪 **MONSTER TEST YARD (DB LANE) + WRAITHLORD RE-ENABLE (2026-07-10, autonomous DB-lane).**
> Baseline = shipped build32b arz `e27dd1cb`. NEW arz `e3810219379c6d1d809a470d889007ba`
> (det-2x reproduced byte-exact: build1==build2==build3-scratch). Text/Quests/Levels UNCHANGED
> (zero new tags -> Text stays `346572bb`, no coupling). Record-diff vs `e27dd1cb` = EXACTLY
> 13 ADDED + 20 MODIFIED + 0 REMOVED, 0 collateral.
> **GROUP 1 = TEST YARD (apply_svc_patches `_create_test_yard`, hooked between `_create_enslaver`
> and the roaming sweep):** 6 new ProxyPools + 7 new Proxies under `records\drxmap\proxy\` (the
> q_leinth_lone "lone" pattern), ALL pointing at the REAL shipped monster records (never clones),
> so tuning those records tunes the yard fight 1:1. Added UNCONDITIONALLY to the arz but INERT (the
> canonical/Steam map references none; ONLY the TESTHUB map's build_hub_extra_specs [MAP LANE] places
> the proxies). Records: `q_yard_enslaver` (pool name1-3=um_toxeus_enslaver_99 @100, spawn 1/champ 0
> -> boss @100%; he auto-bursts his own marauder summon petLimit8 in-fight), `q_yard_marauders`
> (name1-4=um_enslaver_marauder_99, spawn 3-4/champ 0 -> pack @100%), `q_yard_obs_{sarkoth,gorrahk,
> voranthys,ilsevar}` (name1-3=the ONE guardian, spawnMin=Max=6 + championMin=Max=5 -> 6-5=1
> guaranteed guardian + the 5-elite q_obs_warband set; each corner proxy also carries the
> svc_obsidianhoard_pool_0{1,2,3} accessory chest chain), `q_yard_wyrm` (proxy only; pool1 REUSES
> the shipped svc_wyrmhorde_03 -> 16-6=10 common wyrms + 4-6 champion worms). ALL proxies:
> chanceToRun=100, difficultyLimitsFile=**limit_obsidianbosses [1..110]** (REQUIRED: Enslaver L100 +
> Ilsevar L74 both exceed herolimit_all's 75 Legendary cap), difficulty_04, placementExtents 3.0
> (wyrm 2.5); preview mesh/scale copied from each real monster. **GATE WORK:** (a) precise yard
> whitelist in `_verify_roaming_sweep` (`_EN_YARD_POOLS` = the EXACT `q_yard_enslaver.dbr` pool path)
> excludes it from the swept-set derivation + a NEW bidirectional leak guard (every enslaver-bearing
> pool must be swept-OR-yard); still FAILS if the Enslaver appears >weight 1 in ANY non-yard pool.
> Negative test `tools/debug/negtest_roaming_yard.py` proves BOTH directions (weight-leak FAIL,
> pool-leak FAIL, whitelist-load-bearing FAIL, all with PASS restores) = ALL OK. (b) all 7 new yard
> proxies REGISTERED in `_MOD_AUTHORED_SPAWN_PROXIES` -> spawn-eligibility gate proves each spawns
> its main (13 total OK). **GATES GREEN:** roaming-sweep (1224 swept + 1 yard whitelisted),
> spawn-eligibility (13), boss-kit clone-shape (3, unchanged), container-loot, B-SUMMON-1, A9
> render-chain, A7 golden-freeze (Occult/Hunting intact), F2 summons-contract (0 P0/0 P1),
> validate_tags (127 mod tags resolve). **MAP-REF-1 for the map lane:** the 12 injectable proxy
> records = `records\drxmap\proxy\q_yard_{enslaver,marauders,obs_sarkoth,obs_gorrahk,obs_voranthys,
> obs_ilsevar,wyrm}.dbr` + REUSE the existing `q_vashkarr_lone.dbr` for SPOT B (no new record).
> **GROUP 3 = WRAITHLORD SKELLY RE-ENABLE (build_svc_database `apply_mastery_wave2_boosts`, Spirit
> section):** dropped the `xxx` disable prefix on wraithlord_01..20 skillName15/16 (drx_lichskill_
> skellysummon2/3), re-enabling the Liche King's signature skeleton summon (chain resolves:
> Skill_AttackProjectileSpawnPet -> drx_skelly_01..20, rev2skelly.msh). SURGICAL: skillLevel ladders
> UNTOUCHED (original ramp kept); the redundant soulblight double-slot (skillName4+14) KEPT (dropping
> a duplicate = a slot removal, forbidden without Will's per-item OK). Spirit is slot 8 = OUTSIDE the
> Occult(5)/Hunting(6) golden freeze. REVERTIBLE before the next Steam ship (re-add `xxx`) if his
> in-game pet-cap test shows the capstone over-summons.
> **GROUP 2 = PORTAL RIG DB: DEFERRED (not implemented).** [SUPERSEDED 2026-07-10: IMPLEMENTED in a
> dedicated portal wave - see the PORTAL TEST RIG - DB LANE note at the TOP of this file.] NOT map-only (Model C needs +2 NPC records
> + boat-dialog triggers in build_quest_files + ~5-7 Text tags), but it is a SEPARATE portal lane's
> feature (the yard spec reserves the portal strips for that lane); building its DB footprint in these
> shared files would collide. Also gated on the map lane's 0x0b survey of the Boss Arena landing coord
> (3 derived coords) + the keep-vs-remove GridEntrance-hub decision. A working portal-master (Almyros,
> 4 SV destinations) ALREADY ships canonical. Footprint handed off for a coordinated portal wave.
> **NOT DEPLOYED anywhere (DB lane; no dist/, no SteamCMD).** Coupling on eventual deploy: arz-only
> (no Text/Quests/Levels change from these two groups).

> 🚢 **BUILD32 SHIPPED TO STEAM + VERIFIED (2026-07-10, main session, tag `build32-ship` @ 3401852).**
> Payload fresh-download byte-verified 4/4: arz e27dd1cb / Text 346572bb / Levels d5259629
> (build32b) / Quests 6ff23c29. F9 dist==work 4/4 + F7 contracts on dist 0P0/0P1. Description
> sixth-update entry live (7954 chars). DEV entry = full coupled build32 set (arz redeployed as
> SoulvizierClassicDEV.arz). Steam killed + restarted per standing rule. LIVE CONTENT: Helos
> portal-master (Almyros, 4 destinations), Vashkarr @ FotA (post-fix 50/50 dragonian escorts),
> Obsidian Halls roulette (4 corners), Enslaver of Souls roaming rare, wyrm hordes + Sepulchral
> Scale, thrown weapons + 3 supra supers, Mastery Wave 2, Long Nu manual-summon fix.
> OPEN AFTER SHIP: Will's in-game acceptance (Sarkoth cast anims statically unprovable; blood-cave
> Toxeus group-spawn from b31 still pending his eyes); deferred queue = M13b SD restore,
> portal-master Phase 2, wraithlord re-enable, golden-freeze of the 7 tuned trees post-QA,
> broodmother nest set-piece, Tartarus-gates-if-Atlantis-reachable, hoard lockedSound cosmetic.
> **DESIGN LANDED (2026-07-10, sign-off-first): docs/BROODMOTHER_NEST_DESIGN.md** covers BOTH
> deferred items. (1) Broodmother nest: full amgoz1-voice design (eaterofdays rig boss @ [40,58,74]
> 22/30/40k HP, 4-6 no-cap egg-cluster spawner ring + uncapped brood-summon petLimit 24, ONE
> summon soul, guaranteed tier-03 Sepulchral Scale loot hook; host = Act-3 tomb tombobs02 per the
> byte-verified open-floor survey; record plan + INJECT_SPEC table + gates ready for an implement
> wave). (2) Tartarus/Atlantis RECON RESOLVED: Atlantis is REACHABLE for an Atlantis-DLC owner
> (Rhodes-side Marinos boat chain in base x3mq_atlantisadventure.qst = OnLevelLoad/ConversationStart/
> BoatDialog, all CQ-satisfiable, NOT touched by the IT->Scandia/IT->EE caps which are post-Hades
> only; UNREACHABLE without the DLC), Tartarus entry portal is unlock-loaded, but the 16
> tartarus_entrance_gate01 arena gates are DEAD (no loaded opener). RECOMMEND capping the
> Rhodes->Atlantis entry the same surgical way as Scandia/EE (Quests.arc-only if x3mq idx<256);
> cheap residual checks = confirm x3mq registry idx + Marinos placement at Rhodes.
> **PARKED 2026-07-10 by Will's Immortal-Throne-cap ruling (see the STANDING RULING at the TOP of
> this file):** the campaign stays capped at Immortal Throne (Hades); do NOT make Atlantis or
> anything past IT reachable for now. The Tartarus-arena-gates fix and the Rhodes->Atlantis cap are
> both PARKED under this ruling. Revisit only if Will decides to add the other areas later.

> 🛠️ **BUILD32 FINAL-CONTENT SESSION (2026-07-10, autonomous DB-lane) - GROUPS F/E/B:**
> Baseline = HEAD e3ab0a6 (arz 27e6742 / Text cf3cb227 / Quests 6ff23c29, det-2x).
> **GROUP B = TOXEUS THE MURDERER, ENSLAVER OF SOULS (BACKLOG Enslaver, Will approved).**
> apply_svc_patches `_create_enslaver` + `_sweep_inject_roaming_rare` + `_verify_roaming_sweep`.
> A ROAMING RARE mini-boss: `um_toxeus_enslaver_99` (`{^r}Toxeus the Murderer, Enslaver of Souls`)
> DERIVED from am_deathstalker_55_ambush (the ShadowStalker.msh rig, racialProfile Demon, table-LESS
> inline anim block incl. unarmedRunAnim -> rig-safe + summon-safe; the um_toxeus_99 SP-Toxeus
> lineage rides the KIT+name since the design mandates ShadowStalker.msh which um_toxeus_99 does not
> use). Boss @ scale 2.0, charLevel [40,68,100], life [13000,18000,24000], STR/DEX/INT 480/660/420,
> kit = netherstrike + toxeus_bladestorm + lifedrain + flashpowder + lethalstrike(+mortalwound) +
> character_speedall + hostile marauder-summon + boss passives (conversionimmunity/hero_scaling/
> toxeus_passiveproperties/armor_passive/globalproperties); defensive wall = defensiveLife 100 +
> defensivePierce 80 (NO bloodwitch bleed-wall zpassive, per design). `um_enslaver_marauder_99`
> (Champion, [40,68,100], ~2x hand dmg 190/232, runSpeed 1.7, drxshadowcloakrunning_fx via
> charFxPakRunningNames, own inline anim from the clone). Boss summons them via
> `svc_enslaver_summonmarauders` (yaoguai_summonshadowstalkers clone, Skill_SpawnPetMonster, burst 3 /
> 6s cd / petLimit 8; registered with the boss-kit clone-shape invariant). **THE SWEEP:** enumerate
> ProxyPool.tpl records, keep only act-trash pools (proxies orient/egypt/greek + xpack proxieshades)
> whose basename carries NO boss/quest/hero/summon/ambush marker, whose resolvable name members are
> ALL Class=Monster, that have a free name slot (<18), and whose x60 name-weight reaches >=2400;
> multiply existing name weights x60 and append the boss at weight 1 -> p_slot <= 1/2400 per
> main-slot. `_verify_roaming_sweep` (fail-loud) RE-DERIVES the touched set from the arz and proves:
> ONLY eligible pools touched (0 boss/quest/hero), enslaver at weight 1 with p_slot <= 1/2400 in
> each, boss+marauder charLevel == [40,68,100], summon skills resolve, >=500-pool floor. SOUL
> `enslaver_soul_{n,e,l}` = 66% Finger2 MANUAL summon (summon_toxeus_enslaver via _build_boss_summon
> on the boss rig) with a PET-OF-PET: the friendly Enslaver pet's every inherited HOSTILE-summon ref
> is swapped to a friendly `svc_enslaver_petmarauders` Skill_SpawnPet (built via a 2nd
> _build_boss_summon on the marauder rig) so it raises FRIENDLY marauders, never enemies; Occult
> augments drxanatomy + drxdarklings_darkaperture; weird signature stat defensiveDisruption.
> **ARTIFACTS: arz 9265619d, Text (6 new tags, coupled).** Record-diff vs 79daa74e (post-E) = 14
> ADDED (boss / marauder / 3 souls / hostile summon / 3 marauder pets / 3 enslaver pets / summon
> skill / friendly petmarauders skill) + 1224 MODIFIED (all eligible act-trash pools, x60 + append)
> + 0 REMOVED, 0 collateral. Gates GREEN: roaming-sweep gate PASS (1224 pools, 0 dedicated
> (basename) boss/quest/hero/escort/friendly pools touched; 19 general trash pools legitimately
> contain rare low-weight hero MEMBERS per vanilla - the roaming rare walks among area heroes),
> clone-shape PASS, spawn-eligibility PASS, soul-activation PASS (1406 souls), summon-pet STRICT
> PASS (manual-cast + D19 mobility on the ShadowStalker rig), render/golden PASS, validate_tags PASS
> (127 mod tags), contracts GATE PASS (0 P1, no B record flagged), STRICT 0.
> **GROUP E = N5 THROWN WEAPONS (BACKLOG N5, Will approved all designer recs).** Two halves,
> both run in build_svc_database.main() while base_db is alive (del'd before apply_all_extended):
> (1) `_restore_thrown_weapon_drops(db, base_db)` - the base game drops roh (ranged-one-hand =
> thrown) weapons from Act1-4 monsters via loot6Name5 (static_roh_NN @ w400) + loot6Name6
> (roh_NN @ band weight) on its defaultloot tables; SV DROPPED these in its overrides. Restore
> them VERBATIM (level-matched by the same-named base twin), only into an ACTIVE loot6 slot whose
> Name5/6 are EMPTY (never clobber SV; recon proved all 198 eligible twins have empty Name5/6 +
> live loot6Chance). Fail-loud count gate: restored == eligible-skipped and >= 150; got 198/198,
> skipped 0. (2) `_add_supra_thrown_weapons(db, base_db)` - 3 Legendary supra thrown weapons
> `svc_wep_{sanguineorbit,lastword,charonstoll}` built by copying the base roh uniques that carry
> the design meshes (u_l_03=chakramofthesun01 / us_l_donarsmight=mjolnir01 / u_n_12=fingerofcharon01),
> clearing the donor's native offensive stats, and retuning to wep_spear supra conventions
> (itemLevel/lvlReq 65, Legendary, itemcost_uniquelegendary_primary, DRX trail_wep_dagger,
> augmentAllLevel 1, numRelicSlots 1, hidePrefix/Suffix) + the u_l_05/09/08 projectiles + a fresh
> thematic stat block (Sanguine=phys/bleed/leech, LastWord=phys/lightning/stun + kept
> proj_chainlightning, Charon=phys/vitality/manaburn). 3 ItemArtifactFormula `svc_thrown_*_formula`
> cloned from wep_spear_formula (kept the big affix pools + 03_act4_offense bonus; reagents 1L u_l_08
> + 1E u_e_06 + 1MI mi_l_machae; 500k/10M costs) wired into supra.dbr lootName25-27 + supra_special
> lootName26-28 @ w100. D5 mesh re-scan: all 3 supers' meshes + projectiles + trail RESOLVE.
> **ARTIFACTS: arz 79daa74e, Text (6 new tags, coupled).** Record-diff vs 674f31b4 (post-F) = 6
> ADDED (3 supra weapons + 3 formulas) + 200 MODIFIED (198 defaultloot roh restore + supra.dbr +
> supra_special.dbr) + 0 REMOVED, 0 collateral. Gates GREEN: container loot-shape contract PASS
> (restored slots valid), summon-pet/render/golden PASS, validate_tags PASS (122 mod tags),
> contracts GATE PASS (0 P1, no E record flagged), STRICT 0.
> 
> **GROUP F = N6 OBSIDIAN HALLS TREASURE ROULETTE (docs/OBSIDIAN_ROULETTE_DESIGN.md,
> all decisions locked; map-unblocking - the map lane M10 waits on the q_obs_roulette
> records):** apply_svc_patches `_create_obsidian_roulette`. FOUR guardian bosses derived
> from region natives (rig/anim-safe): `um_sarkoth_99` (from uw_as_abyssalliche_flame_42,
> LicheKing02Flame caster; kit ormenos_droptelekinesis + arena_meteor + volcanicorb trio +
> ringofflame + iceshard/squall + drxspellbreaker + ondeath_frostnova; L40/58/72 HP
> 4.5/7/10.5k), `um_gorrahk_99` (from orient_cm_gildedskeleton_27, GoldenSkeleton01;
> bladestorm + cyclops_groundsmash + cyclops_terrifyingroar + dmg/speed buffs +
> ondeath bladenova 16-knife; HP 6.5/10/15k), `um_voranthys_99` (from boss_dragonliche_57,
> DragonLich01; sepulchralwyrm_firebreath + dragonliche freeze/decomp/buffetwings + alastor
> summonarcher/warrior + aktaios_summontombguardians + ondeath_spawnskeleton + ondeath_necronova;
> HP 5/8/12k), `um_ilsevar_99` (from cm_revenantstorm_17, RevenantStorm; phantomstrike +
> kika_phantomstrike + distortionwave[xpack] + lifedrain + drxdeathchillaura +
> halimedes_terrifyingroar + ondeath_detonate; L42/60/74 HP 5.5/8.5/13k). Shared warband pool
> `q_obs_warband` (spawnMin=Max=6, championChance=100, championMin=Max=5 -> 6-5=1 guaranteed
> main = RANDOM guardian [name1..4 w25], LAW holds; nameChampion1..6 = us_abyssalliche
> flame/frost/plague_42 + um_permean_35 + em_ravager_41 + um_bonehallow_37, equal w). FOUR
> corner proxies `q_obs_roulette_{a,b,c,d}` (chanceToRun=25, pool1=warband,
> accessory1/Epic1/Legendary1 = svc_obsidianhoard_pool_0{1,2,3}, difficulty_04,
> difficultyLimitsFile=limit_obsidianbosses [1..110] no-cap clone, placementExtents 4.0).
> THREE `svc_obsidianhoard_0{1,2,3}` FixedItemContainers (clone the blood-cave mega chest
> hidden_bloodcave_chest_0{1,2,3}: container_hpalace_chestlg01.msh scale 1.4, **LockedClassification
> =Boss/50** [donor was Champion/60], goldGeneratorChance=100, below-mega loot [numSpawn *2.4/*2.8
> vs mega *3.8/*4.1] + guaranteed epic/relic loot3 slot) + 3 loot tables + 3 ProxyAccessoryPools.
> FOUR amgoz1-voice souls (66% Finger2): Sarkoth = MANUAL pcsafe typhon_meteorstorm 2/3/4
> (drxvolcanicorb/stoneskin augs); Gorrahk = MANUAL pcsafe cyclops_groundsmash 3/4/5
> (drxconcussive/onslaught); Voranthys = THE ONE SUMMON (manual summon_voranthys via
> _build_boss_summon on SepulchralWyrm01 rig, D19 mobility + damage-sanity PASS; drxcoldaura/
> deathchill augs; weird stat defensiveFreeze=100); Ilsevar = lifedrain ON-ATTACK proc
> (base_atenemy_onattack - manual-cast law binds only Skill_SpawnPet; drxphantomstrike/
> drxdistortionwave xpack augs; weird stat offensiveFearMin=2). **ARTIFACTS: arz 674f31b4,
> Text (16 new tags, coupled).** Record-diff vs baseline 27e6742 = 35 ADDED (4 guardians / 3
> chests / 3 loot / 3 acc-pools / warband pool / 4 corner proxies / 12 souls / limit / 3
> voranthys pets / summon skill) + 0 MODIFIED + 0 REMOVED, 0 collateral. ALL GATES GREEN:
> summon-pet STRICT PASS (Voranthys manual-cast, no controller), render-chain A9 PASS, golden
> A7 PASS, spawn-eligibility PASS (all 4 corners: 6-5=1 main, L74<=110), clone-shape PASS,
> soul-augment + activation PASS, validate_tags PASS (116 mod tags), contracts GATE PASS (0
> P0/0 P1; the 3 hoard chests' only P2 = openFxPakName/lockedSound refs inherited VERBATIM from
> the mega-chest donor, resolve in-game via drx/base arcs). **MAP-REF-1 for M10:** the 4 corner
> proxy records = `records\drxmap\proxy\q_obs_roulette_{a,b,c,d}.dbr` (each pool1=q_obs_warband
> + accessory chest chain); wire the 4 INJECT_SPECS + shared v0e branch per the design section 6.
>
> 🛠️ **BUILD32 SESSION cont'd (2026-07-10, autonomous DB-lane) - GROUP A + D21 P1:**
> **D21 LONG NU P1 (Will, live Steam b31 - TWO reports, ONE root cause):** 'her soul
> summons ON ATTACK instead of like a summon' + 'she does no damage when summoned'.
> RCA (byte-decoded, arz 6eb3cd6f): her souls are the SV `palai_soul_{n,e,l}`
> (itemNameTag tagSoulName471), which carried an inherited on-attack proc controller
> `base_atenemy_onattack`; build31 set itemSkillName=summon_longnu but LEFT the
> controller, so the game re-cast the summon on EVERY player hit and, with the summon
> skill's petLimit=1, re-summoned/reset her each swing -> she never landed an attack.
> The stray controller is the SINGLE cause of BOTH reports. The pet itself is
> structurally sound (nonzero hand damage 70/110/160, full leveled fire kit
> firebreath/ringofflame/nova, aggressive controller) - verified field-by-field vs the
> working bloodtoxeus pet; NOT damage-dead. FIX (apply_svc_patches `_wire_summon_soul`):
> DELETE any inherited itemSkillAutoController (absent shape, never '' per B-TOXEUS-2) so
> every summon soul is a manual pet button; no-op for the D8/D9/D13/D14/D20 siblings
> (verified controller-free). Wiring resolves LIVE (D7 precedent) -> Will's existing Long
> Nu soul self-heals on the next build. NEW GATES in validate_summon_pets: (1) MANUAL-CAST
> LAW - a soul whose itemSkillName resolves to Skill_SpawnPet* must have NO
> itemSkillAutoController (negative-tested: FAILs on the b31 arz's 3 palai souls, PASS
> post-fix); (2) DAMAGE-SANITY - a summon pet must have nonzero hand damage OR an
> offensive skill OR a support kit (battle-standard totems correctly exempt).
> **GROUP A = Q2 HELOS PORTAL-MASTER (map-unblocking):** new NPC record
> `records\quests\portal_master_helos.dbr` (apply_svc_patches `_create_helos_portal_master`,
> cloned from knossos_boatmantoegypt = the proven boat-dialog Npc shape, name 'Almyros the
> Wayfarer') + a 4-destination boat-dialog trigger (build_quest_files `_add_helos_portal_travel`,
> appended to the always-loaded sv_commonmechanics refire step - registry law, no new
> registration; ONE trigger, FOUR Action_BoatDialog actions on the one npc, base quest-8
> precedent). Destinations (world coords from the map lane PORTAL_MASTER list): Garden of
> Merchants (1173,-39,-4001), The Secret Place (-2396,2,-5790), The Uber Dungeon
> (-2438,10,-2450), The Sparta Crypt (-5602,-2,-1409). 6 new tags (name/chat + 4 menu labels).
> **MAP-LANE COUPLING (MAP-REF-1 satisfied):** the record now lands in the arz -> wire
> `PORTAL_MASTER_SPEC_PENDING` into INJECT_SPECS at startingfarmland06d local
> (76.50,0.60,189.50) on the next map build. **ARTIFACTS: arz `fbd2c6d1`, Text `6fb34430`
> (coupled - 6 new tags), Quests `6ff23c29`.** Record-diff vs Group D 6eb3cd6f = 1 ADDED
> (portal_master_helos) + 3 MODIFIED (palai souls, 1 field each) + 0 REMOVED, 0 collateral.
> ALL GATES GREEN: summon-pet STRICT 0, render PASS, golden PASS, contracts GATE PASS,
> validate_tags PASS (100 mod tags resolve), Quests contract PASS (107). PRESERVED the
> shipped Q1/Q3 Typhon unlock + Olympus herald byte-intact (separate host quest).
> **GROUP C = VASHKARR, ELDEST OF THE ANCIENTS (N4-DB, map-unblocking):**
> apply_svc_patches `_create_vashkarr`. `um_vashkarr_99` (Boss, `{^r}Vashkarr, Eldest of
> the Ancients`) derived from bm_deathlance_32 (AncientDragonian01.msh, anim-safe dragonian
> family), charLevel [38,56,71], HP [12000,16500,21000], boss wall + dragonian melee kit +
> frequent horde summon + boss_conversionimmunity/boss_scaling. Minion horde =
> `svc_vashkarr_summonhorde` (yaoguai_summonshadowstalkers clone, burst 3 / cd 6s, petLimit
> 12) spawning `svc_vashkarr_fodder` (bm_ravager_31-derived Common, laddered [38,56,71]).
> 2 full-strength Champion escorts ALWAYS: `svc_vashkarr_lance` (ravager melee) +
> `svc_vashkarr_warlock` (bs_warlock_40 caster), laddered. Proxy `q_vashkarr_lone`
> (chanceToRun=100) + pool (spawnMax=3 / championChance=100 / championMin=Max=2 -> 1 boss +
> 2 champions; spawnMax-championMax>=1 law holds), difficultyLimitsFile=herolimit_all
> (no-cap, [1..75] contains the band). STAT-ONLY soul `vashkarr_soul_{n,e,l}` ({^F}Soul of
> the Eldest, dense fire/physical ladder + fireEnchant/onslaught augments, 66% Finger2). The
> minion-summon clone is registered with the boss-kit clone-shape invariant (OK, 2 pairs).
> **ARTIFACTS: arz `968c0b6c`, Text (5 new tags, coupled).** Record-diff vs Group A fbd2c6d1
> = 10 ADDED (boss/fodder/2 escorts/proxy/pool/3 souls/horde skill) + 0 MODIFIED + 0 REMOVED,
> 0 collateral. Gates GREEN: summon-pet STRICT 0, render PASS, golden PASS, contracts PASS,
> clone-shape invariant OK, validate_tags PASS (104 mod tags). **MAP-REF-1: records land ->
> map lane injects the Random05A placement + v0e routing (M9 spec in build_section_surgery).**
> **GROUP G = N7 WYRM HORDES + SEPULCHRAL SCALE (map-unblocking):** apply_svc_patches
> `_create_wyrm_hordes`. Transforms the 6 Act-3 tomb `ug_demon_wyrmsprite_0{1,2,3}{n,t}`
> encounters into escalating sepulchral wyrm hordes. `um_sepulchralwyrm_common_31` DERIVED
> (clone of the Champion _31 -> Common, no soul drop) fills the main pool slots. 3 NEW pools
> `svc_wyrmhorde_0{1,2,3}` (cloned from the firesprite pools; the SHARED firesprite pools are
> left untouched) sized 4/8, 6/12, 8/16; tier-03 adds champion config 100/4/6 with the 4
> champion worms (16-6=10 guaranteed mains, spawnMax-championMax>=1 holds). No-cap
> `limit_wyrmhorde` (herolimit_all clone) on all 6 repointed proxies. Sepulchral Scale charm
> `svc_sepulchralscale\0{1,2,3}` (Emberscale/D10 pattern: yeti-fur ARMOR charm clone -> cold /
> frostburn / cold-slow / life per-shard ladder + GUARANTEED completion fear 2/2/3, lvlReq
> 30/44/56, RelicAnimal01 art, yeti-fur working completion table kept) + 3 loot tables, wired
> at 7% on the 4 champion worms via free lootMisc4 (D10 mechanism). **ARTIFACTS: arz
> `27e67420`, Text `cf3cb227` (2 new tags, coupled).** Record-diff vs Group C 968c0b6c = 11
> ADDED (common wyrm/3 charms/3 loot tables/limit/3 pools) + 10 MODIFIED (4 champion worms'
> charm-drop wiring + 6 proxy pool/limit repoints) + 0 REMOVED, 0 collateral. Gates GREEN:
> summon-pet STRICT 0, render PASS, golden PASS, contracts PASS, validate_tags PASS (106).
> **MAP note:** the wyrmsprite proxies are ALREADY placed in the Act-3 tombs (native
> encounters); repointing their pools makes the hordes live with NO new map injection needed.
> **REMAINING build32 groups (full specs below; verified donor recon appended):** B Enslaver,
> E N5 thrown weapons, F N6 obsidian roulette.
>
> **DEFERRED B/E/F - VERIFIED DONOR RECON (2026-07-10, for a fast follow-up):**
> - **F Obsidian:** guardian bases are `as_abyssalliche_flame_42` / `uw_as_abyssalliche_flame_42`
>   (NOT us_abyssalliche), `boss_dragonliche_57` (Voranthys); the golden-skeleton melee monster
>   (Gorrahk) is referenced by the `records\proxies orient\pools\undead\goldenskeleton_*` POOLS
>   (resolve the monster record from a pool's name1). ondeath skills resolve at `records\skills\
>   monster skills\ondeath\skills\{bladenova,frostnova}.dbr` + `...\attack_radius\ondeath_
>   {frostnova,necronova}.dbr` + `...\monster skills\ondeath_spawnskeleton.dbr` (doubled
>   `skills\skills\` variants also exist - use the single-`skills\` path). `arena_meteor` =
>   `records\skills\monster skills\attack_radius\arena_meteor.dbr`; `ormenos_droptelekinesis`
>   OK; cyclops = `records\skills\boss skills\cyclops_terrifyingroar.dbr` + pcsafe
>   `cyclops_groundsmash`. The mega-chest mesh `container_hpalace_chestlg01.msh` sits on a
>   FixedItemContainer - derive from the blood-cave mega chest RECORD. No `limit_obsidianbosses`
>   exists yet (author a herolimit_all-clone no-cap). Voranthys summon = `_build_boss_summon`
>   on SepulchralWyrm01. The Vashkarr proxy/pool + wyrmhorde pool recipes are the exact
>   templates for F's shared warband pool + 4 corner proxies; chest chain = the D10 loot-table
>   + `_ensure_record` LootRandomizerTable pattern.
> - **E Thrown:** supra tables = `records\xpack\item\loottables\arcaneformulae\supra.dbr` +
>   `supra_special.dbr` (add slots 25-27 / 26-28 @w100). Formula template =
>   `records\drxitem\supra\zrecipes\wep_spear_formula.dbr` (ItemArtifactFormula: artifactName +
>   reagent1/2/3BaseName = 1L+1E+1MI). Thrown-weapon base records live under
>   `records\item\equipmentweapon\throwingknife\` (clone for the 3 supers; avoid the fenrirsbite
>   stray mesh). Loot-restore half needs base_db + a diff of the mod-overridden
>   `c_default_*/boss_default_*/bandari_default_*` tables vs the base twins' loot6Name5/6.
> - **B Enslaver:** boss donor = `records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr`
>   (xpack path, the SP Toxeus / ShadowStalker-kin). Summon-shadowstalker donor =
>   `yaoguai_summonshadowstalkers` (Vashkarr-proven clone). toxeus_bladestorm / flashpowder /
>   lethalstrike_mortalwound all resolve. The roaming sweep (`_sweep_inject_roaming_rare`) is
>   the hard kernel: eligibility filter must EXCLUDE boss/quest/hero/escort/friendly pools;
>   pair with a `_verify_roaming_sweep` fail-loud gate (only eligible pools touched, weight-1
>   name-append, 18-slot caps respected).

> 🗺️ **BUILD32a MAP LANE (2026-07-10): M8 + M9 WIRED, gated, DEV-deployed (coupled).**
> **M8 Helos portal-master:** `PORTAL_MASTER_SPEC` LIVE in INJECT_SPECS @ startingfarmland06d
> local (76.50,0.60,189.50) (v0x11 step-6/7 path, NPC byte-shape, no 0x14). Dialog rides the
> DB lane's Quests 6ff23c29 (sv_commonmechanics refire step; COUPLED map+Quests deploy).
> **M9 Vashkarr:** `VASHKARR_SPEC` LIVE @ random05a local (24.00,1.00,31.70) - **FIRST LIVE
> USE of the 5af756c v0e SVAERA-host branch, byte-proven clean**: parse-back gate
> (tools/debug/gate_build32_parseback.py) = random05a 0x05 59->60 instances, appended
> q_vashkarr_lone flags=0 exemplar-rot, flag-aware walk to exact section+blob end, ALL other
> sections byte-identical (incl. the 0x0b navmesh, 76,438 B); farmland06d 995->996, 0x14
> byte-identical. On-mesh RE-verify vs the level's own 0x0b: spot walkable in ALL 3 tilesets
> (radius 0.4/0.6/0.8), 100% clearance in the 3.5u square (survey said 95%), set0 walkable
> cells 60,356 = survey-exact parity. **Gates:** contracts GATE PASS 0 P0/0 P1 (MAP-REF-1=0
> vs arz 27e67420), navmesh 24/24, groups-bindings 374/374 0 dead, det-2x BOTH variants.
> **MD5s: canonical `1dad265e68614ab813b5f9a0aed10286`, TESTHUB `892f8f14bd605f67d2d323af2ced6d88`**
> (build31g baseline f1d31d23 preserved at local/Levels_merged.build31g-baseline.arc).
> Per-level delta vs build31g = EXACTLY 2 blobs: random05a (+1 0x05 instance) +
> startingfarmland06d (+1 0x05 instance). DEV deploy = all four coupled artifacts (Levels +
> Quests 6ff23c29 + arz 27e67420 as SoulvizierClassicDEV.arz + Text cf3cb227; the DEV arz was
> Group-D-stale with ZERO helos/vashkarr records - MAP-REF-1 ordering at DEV required the sync).
> ~~M10 Obsidian corners STILL PENDING~~ (superseded by build32b below). Walk-test:
> (1) Helos plaza - talk to Almyros the Wayfarer, all 4 destinations; (2) FotA cave (ToTomb02
> east of Chang'an) - Vashkarr + 2 champions guard the Majestic Chest, soul drops.

> 🗺️ **BUILD32b MAP LANE (2026-07-10): M10 WIRED - build32 map COMPLETE, ship candidate.**
> DB Group F landed (6c6c0cd, arz 9265619d...): all 4 corner proxy paths byte-verified vs the
> record table (records\drxmap\proxy\q_obs_roulette_{a,b,c,d} + pools\q_obs_warband + the
> obsidianhoard chest chains). `OBS_ROULETTE_SPECS` merged into INJECT_SPECS (collision-
> guarded), v0e branch (M9-proven). **Corner-D re-verify CONFIRMED THE SURVEY FLAG:** at
> (90.8,45.6) walkable only in the radius-0.4 tileset, 71% clearance -> **NUDGED +2.0/+2.0
> within the pocket to (92.8, 1.0, 47.6)**: walkable in ALL 3 tilesets, 100% clearance, same
> flat floor as corner B. A/B/C verified 100%/all-tilesets at the surveyed spots. Parse-back
> gate extended to M10 (57 checks, both variants): tombobs02 578->580 (A@(50.4,143.6) +
> C@(200.4,97.6)), tombobs01 408->410 (B@(220.8,89.6) + D@(92.8,47.6)), all appended flags=0
> exemplar-rot, every other section byte-identical (incl. both 0x0b navmeshes). **Gates:**
> contracts GATE PASS 0 P0/0 P1 (MAP-REF-1=0 vs arz 9265619d), navmesh 24/24, groups-bindings
> 374/374 0 dead, det-2x both variants. **SHIP-CANDIDATE MD5s: canonical
> `d5259629d16e1fa8e39e7a6d59b3e57e`, TESTHUB `4fb76084a275d65682ac38426055acf6`** (baselines
> preserved: build31g f1d31d23, build32a 1dad265e). Whole-map delta byte-proven: exactly 2
> blobs vs build32a (tombobs pair), exactly 4 vs build31g (the four M8/M9/M10 hosts). DEV
> deploy = full coupled build32 set (Levels d5259629 + Quests 6ff23c29 + arz 9265619d as
> SoulvizierClassicDEV.arz + Text 346572bb). Walk-test: Act-3 Obsidian Halls (TyphonUG) -
> each visit rolls the 4 corners at 25% each for a warband + hoard chest.

> 🛠️ **BUILD32 SESSION (2026-07-10, autonomous DB-lane, Will blanket sign-off) - SHIPPED GROUPS:**
> STEP 0 det-2x reproducibility of build31-ship VERIFIED (arz `fc393741` + Text `b7251fd7`
> BOTH reproduce byte-exact from a clean HEAD rebuild, x2 - no process breach).
> **Group D = MASTERY WAVE 2** (docs/MASTERY_AUDIT_2026-07-09.md S3 Wave 2 + PART III):
> Warfare (ancestralhorn/battlestandard uptime, spectralsoldier armband path, warwind feel),
> Nature (FoN 360->180, petBonus +30%% pet-dmg/+160 prot ML1-40, defensiveConvert malus cleared,
> wolf/sylvan dangling FX), Spirit (outsider 360->120+TTL60, deathward 300->180, bonepet
> spiritbreath 'xxx' re-enable + drxplaceholder cleared [skillName6 no-op KEPT], bonescourge FX),
> Dream (timefield cleared, phantasm uptime, psionicbeam x2, mana-ladder extensions, phantomstrike
> self-slow zeroed, phantasm loot dangler), RuneMaster (mastery Life 800->1160 + Mana 0->400,
> menhiraltar cd 240->120) + Neidan (mastery Life 900->1050, terracotta petLimit ->3, deathbomb
> 33->45%%, splash attached to shenpao) as base->mod overrides. **arz `fc393741` -> `6eb3cd6f`**;
> Text UNCHANGED (`b7251fd7`, zero new tags = arz-only, NO coupling); Quests/Levels untouched.
> Record-diff = 6 ADDED (RuneMaster/Neidan overrides) + 118 MODIFIED, **0 REMOVED, 0 unbucketed**
> (WARFARE 23/NATURE 26/SPIRIT 23/DREAM 46/RUNEMASTER 2/NEIDAN 4). ALL GATES GREEN: player-anim
> PASS (40 tree skills; splash's PhantomStrike correctly an inert modifier), summon-pets PASS,
> contracts GATE:PASS, render-chain PASS (22 upstream WARN), golden-freeze Occult/Hunting intact
> (0 waived). det-2x reproducible. **RuneMaster+Neidan castability CONFIRMED already fixed by
> Wave 1 B6** (Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/Hew ported; NOT re-implemented).
> **DEFERRED (in amgoz1's spirit, honest):** wraithlord skellysummon2/3 re-enable (pet-cap
> unverifiable without a walk-test); golden-freeze tree expansion to the 7 tuned trees (post-QA
> per audit S5 - freeze after Will's walk-test, regenerating the snapshot same step).
> **REMAINING build32 groups (specs intact below):** A Q2 Helos portal-master, B Enslaver,
> C Vashkarr, E N5 thrown weapons, F N6 obsidian roulette, G N7 wyrm hordes.

> 🌙 **BUILD31 OVERNIGHT RUN (2026-07-10, autonomous per Will) - SHIPPED GROUPS:**
> Group1 mastery fixes B1-B6 (06a9a24a) -> D19 immobile-summon fix + PET-MOBILITY gate
> (95e816d3) -> Q3 instant Rhodes unlock + token path + herald NPC (arz bd6ae869 / Quests
> 3db3764c) -> Q4 bossarena/widowletter/chimera (Quests 20ff9f30, arz 754c3279) -> M15 Toxeus
> group-joins (7a59919f) -> Group2 Def/Earth/Storm boosts (3c065e70) -> Group3 D11/D12/D15/
> D16/D17/D18 (arz 3656a83f + Text b622d0d7) -> Group4 D13/D14/D20/D21 summon souls
> (**FINAL arz 0de2ce56 + Text b622d0d7 + Quests 20ff9f30**). Every group: gates + bucketed
> record-diff + commit + DEV deploy. **DEFERRED to the next session (specs intact below):**
> Group5 Q2 Helos portal-master (herald pattern proven by Q3; M8 dest table in
> build_section_surgery), Group6 Enslaver, Group7 Vashkarr, N5 thrown weapons + N6 roulette +
> N7 wyrm hordes + Mastery Wave 2 (build32). ⚠️ N5/N7 design agent output files
> (tasks/ab8a4644fa12b0169.output, tasks/a4e3cbf48ea86eff4.output) were EMPTY (0 bytes) when
> forwarded - coordinator must re-send the full design texts before implementation (the
> coordinator-locked decision summaries are in the train queue entries below).
> **MAP-LANE COUPLINGS OUTSTANDING:** (1) Q3 herald placement: wire
> OLYMPUS_RHODES_NPC_SPEC_PENDING into INJECT_SPECS (record records\quests> portal_master_olympus.dbr is IN the arz now); (2) M15: repoint the parchment demon_01_cluster
> instance to demon_01_cluster_toxeus50.dbr + REMOVE both standalone q_bloodtoxeus proxies
> (drxBC2 + parchment) or double-spawns return; (3) Q4 testquesttoopendoors deregistration.


> This is the authoritative running list of everything still broken or unfinished.
> Ordered roughly by priority. Each item: symptom (what Will saw) → likely cause →
> fix approach → which lane/files. Read docs/HANDOFF_LIVE_STATE.md first for deploy state,
> then docs/PLAYBOOK.md for how to do each kind of change.

> 🚨 **STANDING RULE (Will, 2026-07-09): NEVER REMOVE SKILLS FROM MASTERIES.** Edit fields =
> preferred; add new skills/slots = allowed; REMOVE a skill/tree slot = forbidden without Will's
> explicit per-item approval (removal candidates go on a proposal list back to Will, never into
> a build); re-enabling disabled original content = encouraged; in-record dangling-ref cleanup =
> allowed field-editing, but when in doubt treat it as a removal and ask. Full operational text
> + the Wave 1/2 compliance sweep in the header of docs/MASTERY_AUDIT_2026-07-09.md.

## 🔴 P0 - visible/blocking, confirmed in-game 2026-07-08

### B-OLYMPUS-RHODES-1 - FIX SET COMPLETE (build31g map + Q3 arz/Quests), awaiting Will's walk-test
- **MAP HALF WIRED (build31g, commit d06f334, 2026-07-09 overnight):** the herald NPC
  (portal_master_olympus, cloned from the Knossos boatman) is PLACED at OlympusFinal02
  inst[205], local (305.80,90.20,490.80) = world (1155.80,90.20,-3190.20), 4u from the locked
  xq00 portal on the Typhon plateau (navmesh-verified). Q3 (36a6212) had already shipped the
  record (arz bd6ae869) + boat-dialog quest -> world (700,41,-6466) (Quests 3db3764c) + the
  INSTANT kill-unlock trigger on the engine portal. Player path after Typhon: talk to the
  herald -> Rhodes (guaranteed), or the xq00 portal if the engine honors the kill-unlock.
  Walk-test: kill Typhon, herald dialog -> Rhodes arrival at the base game's own target.
- ORIGINAL ENTRY (history):

### (historical) B-OLYMPUS-RHODES-1 (P0 CAMPAIGN BLOCKER): no working portal after Typhon (Olympus -> Rhodes/Hades)
- **Symptom (Will, fresh session):** killed Typhon at the Olympus summit, no working continuation
  portal to Rhodes; the campaign cannot progress past Olympus. Q1 lane added an
  Action_UnlockFixedItem on the "Olympus - Typhon Defeated" token (in "quest that controls bosses
  and their doors.qst" idx 68, loads fine) - STILL no portal on a genuinely fresh kill.
- **RCA (M7 + M12, byte-definitive):** the base post-Typhon portal `xq00_olympus_portaltorhodes`
  (FixedItemTeleport, `locked=1`, "Opened by Zeus after Typhon Killed") is present at OlympusFinal02
  instance [41]. Its destination is ENGINE-INTERNAL (not in the record, the 0x14 [generic 12B], the
  GROUPS, or the SD - verified in ours AND SVAERA). No quest in ANY arc (base + 5 XPack + SVAERA +
  ours) references it. **"Copy SVAERA" has NOTHING to copy:** instance [41] is BYTE-IDENTICAL across
  SVAERA / ours / base (rec_md5 `0975f9aa…`, flags=1, uid `24018446…`, 0x14 `2900…01000000`, pos
  (305.79,90.11,486.84)); SVAERA's DB is an empty 2KB stub so it uses base's `locked=1` record;
  SVAERA's quest 15 / boss-doors controller / init quest are all byte-identical to base; SVAERA's
  QUESTS registry is a subset of ours (DB-lane Q3: no IT main quest missing). So SVAERA is NOT
  born-open and has NO special portal wiring. (scratchpad inst41_diff.py / svaera_cmp.py / svaera_q.py)
- **FIX (chosen): the boat-dialog NPC (Model C).** A summit "portal master / Hermes" NPC ->
  Action_BoatDialog to the Rhodes arrival - a DATA-DRIVEN teleport that does not depend on the
  engine-internal FixedItemTeleport. Map-side spec READY (build_section_surgery.py
  OLYMPUS_RHODES_NPC_SPEC_PENDING): NPC at OlympusFinal02 local (305.80,90.20,490.80) = world
  (1155.80,90.20,-3190.20), 4u from the portal on the Typhon plateau, navmesh-verified on-mesh +
  100% clear + connected. Rhodes arrival = the base's OWN paired target
  `xq00_rhodes_olympusportaltarget` @ Rhodes_CityFinal_01 = WORLD **(700, 41, -6466)** (on-mesh).
  GATED on the DB lane (a8f5446a) authoring `records\quests\portal_master_olympus.dbr` + the
  boat-dialog quest (MAP-REF-1). Then wire the spec, rebuild both maps, gates, coupled map+Quests
  DEV deploy. Mesh `Credits_Portal.msh` + the portal anms DO resolve (base XPack Items.arc) - render
  is not the blocker; the dead engine destination is.

### B-MERGE-SD-GROUPS-1 (P1, map lane): GROUPS half FIXED (build31e M13a); SD half OPEN (M13b, needs sd_format RE)
- **M13a SHIPPED (build31e, 2026-07-10): the GROUPS restoration.** New merge in
  `svaera_plus_portals.py merge_groups_svaera_base`: SVAERA/base records (SVAERA order, verbatim)
  + SV-extra members appended per-record (4: the HV01 fountain, the SV maze respawn, JadeFigurine,
  1 SV Hades member; levelGUID-validated, 0 stale skips) + the 4 SV-only groups (New Group x2,
  DRXShrineTeleport_Duister, zRespawnSanctuary). RESTORED: Tower-of-Judgement floor-4 respawn
  (32703cac.., the Lane B mandatory-path dead shrine), teleportshrineolympus01 (3c007d48.., the
  Olympus rift stop - B-OLYMPUS-TELESHRINE-1 is thereby RESOLVED BETTER THAN FILED: restored, not
  removed), Shrine_Teleport_Orient 12th member, + base-correct member positions/GUIDs in 42 more
  same-name records (golden chests, unified proxies, the Q15/xQ00 portal-pairing [Any Entity]
  records). NEW fail-loud GATE `tools/verify_groups_bindings.py` (forward per-instance check:
  every placed StrategicMovement*Shrine uid must be GROUPS-bound; the gap contracts_map
  MAP-GROUPS-1 could not catch): **374/374 devices bound, 0 dead** on both variants + the 5
  Lane-B must-bind uids asserted in-build (M13A_MUST_BIND). Walk-test: ToJ floor-4 respawn +
  the Olympus rift shrine + HV01 fountain still binding.
- **M13b RE COMPLETE -> verdict NO-GO (2026-07-10, backlog lane).** Full SD(0x18) format RE +
  round-trip-proven parser landed: **`tools/sd_format.py`** (byte-identical round-trip on all 4
  maps: SV v6, ours v6, SVAERA v7, vanilla v7) + **`docs/SD_FORMAT_RE.md`** (RECIPE). Findings:
  SD = `[magic=2][version 6|7]` then a POSITION-ORDERED list sequence `[listTag][count][records]`
  (listTag is REUSED - 1=env&miniboss, 2=region&audio - so order, not tag, keys the schema).
  Lists: [0] env/fog, [1] region/zone-label (**the SV zone labels**), [2] audio, [3] miniboss, ...
  REGION schema (identical v6<->v7): `a=1 | nameLen+name | guid[16] | color1[4] | color2[4] |
  tagLen+dispTag | t1 | t2`. ENV schema: `a=1 | name | guid[16] | block(120 v6 / 148 v7) |
  [v7-only: effectPathLen+weatherDbrPath]`.
  **What the merge dropped (SV v6 vs SVAERA v7):** 252 region records ALL unreachable DLC/HC
  (X4=130, X2=96, X3=23, +3 HCDun) - campaign caps at Hades so none are entered; the 282 shared
  base-act regions are **byte-identical** v6<->v7. Meanwhile SV's SD carries the 9 SV-only zone
  labels (tagBCX x4, tagMZoneGoM, tagSPDarkForest, tagSPRogueEncampment, tagJoLandia, tagNewMZone1)
  + 17 SV-only env presets (BloodCave/Duister/UberDungeonLevel1/RogueEncampment/...) + SV audio/
  miniboss bindings - all for the RESTORED SV AREAS. **A v7 SD swap loses all of that to gain
  only unreachable DLC + ~10 cosmetic base-act fog presets.** No proven defect is SD-attributed.
  **CLOSE unless** someone wants the cosmetic fog polish: a targeted record-level merge keeping SV
  v6 as base + porting just the ~10 re-authored base-act fog env presets - blocked on the v6->v7
  env-block conversion (the +28 v7 bytes' field semantics), low priority. Region-record edits are
  trivial via sd_format.py; env porting is the only real cost. Full detail: `docs/SD_FORMAT_RE.md`.

### B-PORTAL-1: Portals are ugly flat blue panels / hard-to-see arrows
- **Symptom (Will, screenshots):** the born-open GridEntrance portals now APPEAR (build27 fix
  worked) but render as a **flat 2D blue rectangle** with a small light-blue triangle/arrow, not
  an attractive portal. In Duister (Secret Place) they're flat teal panels floating in the room.
- **Cause:** when we swapped GridEntranceDynamic → base GridEntrance for the born-open fix
  (commit portals-born-open / build27), we kept `mesh` but the base GridEntrance class renders its
  portal-plane placeholder (the blue panel) rather than a nice swirling FX. The dynamic class had
  the pretty visual tied to its open-animation; the static class shows the raw portal quad.
- **Fix approach:** give the portal records a proper portal MESH + FX. Options: (a) find a
  base-game always-open portal that looks good and copy its mesh/fx fields; (b) attach a portal
  particle effect (the Tower-of-Judgment `TJ_JudgementRoom_PortalObject` swirl, or a rift FX) as a
  separate decoration/effect entity co-located with each portal; (c) check if base GridEntrance has
  a `portalFxName`/`meshFxName` field that we left empty. MUST keep born-open + teleport working
  (don't revert to Dynamic). Files: tools/apply_svc_patches.py (the `_make_portals_born_open_*`
  block) for record fields, or tools/build_section_surgery.py to co-locate an FX entity.
- **Verify:** in-game only (visual). Static gate: portal record has a non-empty mesh/fx that resolves.

### B-PORTAL-2: Portal placed in the middle of the walkway (blocks passage)
- **Symptom:** the blue portal to the RHS of the respawn fountain sits **right in the path** -
  Will can't walk past it without being teleported. (Screenshot 1: the flat blue panel east of the
  fountain, on the only route.)
- **Cause:** hub/door portal placement coords chosen for on-mesh + distance-from-friendlies, but
  NOT for "off the natural walking path." A portal you can't avoid = forced teleport.
- **Fix approach:** relocate that portal (and audit all hub portals) OFF the main traffic lane -
  tuck them against a wall/edge so the player walks TO them deliberately. In the blood-cave first
  room the 5 hub portals should be a neat row along a wall, not blocking the tunnel. Files:
  `_HUB_CAVE_ENTRANCES` / `_HUB_CAVE_RETURNS` coords in tools/build_section_surgery.py; the door
  portal coords in the A1/A2/Sparta specs. Re-run gate_doors_hub after moving.
- **NOTE:** this is the TESTHUB hub portals AND possibly canonical doors - check both.
- **2026-07-08:** G1 (the fountain-camp Garden door, the offender Will hit) relocated ~12.4u off
  the walking lane by the map wave. NEW SAME-CLASS HAZARD found by audit: the Sparta door entrance
  P1 in catacube02_floorlast sits 6.0u from the stairsdown01 traffic funnel; relocate it too
  (in the wave). Vista S1 and maze03 A1 placements are fine.
- **✅ B-PORTAL-2-SPARTA CLOSED 2026-07-28 (debt-map lane): OBSOLETE - the hazard no longer exists,
  nothing to relocate, no map rebuild.** The 07-08 note is stale: it was written four days before
  the 2026-07-12 **P0 TRAVEL-LAW wave** ("no walk-through/proximity teleport anywhere we author"),
  which did not move that portal but **DELETED it**. `tools/build_section_surgery.py` now records
  the removal in the `INJECT_SPECS` comment block ("WORKSTREAM A: INVENTED Sparta Crypt L2
  walk-through entrance = REMOVED (P0, Will 2026-07-12) ... catacube (base AE v0f) reverts to no
  injection"), and its whole paired machinery is parked in `_RETIRED_REWRITE_0X06_SPECS` /
  `_RETIRED_APPEND_0X06_SPECS` / `_RETIRED_REMOVE_0X05_BY_0X14_UID_SPECS` (kept for the audit trail
  per the retirement protocol - **not deleted**). Sparta Crypt is now reached by the Helos
  portal-master NPC and left by the in-SC2 `svc_testhub_return` NPC (talk-to-travel, Will's
  approved pattern).
  **BYTE PROOF against both BUILT variants** (0x05 + 0x14 walk of the level blob in
  `local/Levels_merged.arc` and `local/Levels_merged_TESTHUB.arc`):
  `Levels/World/Greece/Athens/Underground/CataCube02_FloorLast.lvl` v0x0f carries
  **0x14 instance count = 0** in BOTH. A `GridEntrance` portal cannot teleport without a `0x14`
  binding (`GridEntrance::GetConnectedPortalId`/`GetConnectedRegionId`, `docs/DYNGRID_GATE_RCA.md`
  sec 4), so there is **no forced-teleport entity of any kind in that level** - the 6.0u-from-
  stairsdown01 hazard is physically absent, not merely mitigated. The only SVC entity that ever
  goes near that funnel is the TESTHUB-fold `svc_area_return_sparta` **talk** NPC, which requires
  a deliberate conversation and cannot teleport on proximity - a different (non-)class from Will's
  complaint ("I can't walk past it without being teleported"). Live map contracts re-run on the
  same artifacts: 0 P0 / 0 P1 / 3 P2 (pre-existing base-game portal noise), GATE PASS.
  **INDEPENDENTLY RE-VERIFIED 2026-07-28** (second pass, re-derived from the artifacts and hardened
  against a vacuous pass): `CataCube02_FloorLast.lvl` is blob version **v0x0f** in both variants with
  sections `[0x05, 0x06, 0x0b, 0x14, 0x17]` present; the `0x14` section **exists and parses** but
  holds **0 instance records**, while the same parser reads **190** (canonical) / **191** (TESTHUB)
  live `0x05` instances from the same blob. So the zero is a genuine empty binding table, not a
  parser failure on an unread blob - the distinction the original proof did not rule out.

### B-PORTAL-3: Return/back teleport doesn't work (one-way trip)
- **Symptom:** Will teleported to "Duister" (Secret Place) via the panel, could walk around, but
  **could not teleport back**. Also: "all the portals in Duister are broken."
- **Cause:** the return portal (GridExitOneWay landing → its own back-entrance) either wasn't
  swapped to born-open (only the OUTBOUND portal_olympianarena1 was swapped; the RETURN
  portal_olympianarena2 is GridExitOneWay - is IT visible/functional?), OR the Secret Place cluster's
  INTERNAL portals (SV's own darkforest transition portals) are DynGridEntrance that never open
  (same class bug, different records, explicitly out-of-scope in the born-open fix - see
  DYNGRID_GATE_RCA.md note 2). "All portals in Duister broken" strongly implies the 11-level Secret
  Place cluster's own inter-level portals need the same born-open treatment.
- **Fix approach:** (1) verify the return portal_olympianarena2 renders + teleports (GridExitOneWay
  semantics - does it need born-open too? it's a different class); (2) enumerate ALL DynGridEntrance
  portals in the Secret Place cluster (and every SV area) and apply the born-open swap to them too
  (generalize `_make_portals_born_open` beyond portal_olympianarena1 to ALL our-relevant
  DynGridEntrance records that should be always-open). Files: apply_svc_patches born-open block.
- **LIVE UPDATE 2026-07-08 (Will, public build):** the GARDEN OF MERCHANTS return portal is ALSO
  broken (outbound from the fountain camp teleported fine; the return in the Garden did nothing).
  With Duister's returns already confirmed broken, one-way returns are SYSTEMIC: verify and fix the
  returns of ALL FOUR portal areas (Garden, Secret Place, Uber Dungeon, Sparta Crypt). Outbound
  born-open entrances are CONFIRMED WORKING live (first public-build walk-in teleport verified).
- **ROOT-CAUSE DISCRIMINATOR (2026-07-08 byte-level diagnosis):** every 0x14 binding is CORRECT
  (60B prefixed entrances, 48B landings, pairing intact, dest GUIDs verified, no mis-wire). The
  live pattern: entrances hosted in ORIGINAL-INDEX levels fire (G1 in HV01, hub portals in swapped
  Random09A); entrances hosted in APPENDED SV-only levels never fire (G3 in the Garden, S3 + hub
  returns in darkforestenter). Invented return-entrances have zero native precedent (native
  bidirectional doors = one 0x14 mouth + one reciprocal 0x06 descriptor in the destination).
- **FIX RECIPES (handed to the 2026-07-08 map wave):** SPARTA = convert to a NATIVE two-way door by
  repurposing SC2's dangling 0x06 tail descriptor in place (exit d76121ad..., mouth efbf54c9...,
  src catacube GUID 817574a8..., door cell (6,0,4)); remove injected P2/P3/P4. UBER (A1) = DEFER
  (crypt_floor1 is a 2-layer grid; door-cell Y = layer index; needs layer RE first). GARDEN =
  no native map return possible (terrain level); SV's DESIGNED return is the rift shrine
  teleportshrine_gom, VERIFIED FULLY WIRED in our build (Will: walk-test rift travel from the
  Garden shrine). DUISTER = its teleportshrineorient01 shrine is INERT (flags=0, no uid, no GROUPS
  member); wiring it like the Garden shrine gives Duister the same SV-native rift return.
  Escalation if appended-host entrances must ever fire: Frida runtime session in the Garden.
- **Walk-test predictions:** maze03-hosted hub return WORKS; SC2/murderbossroom-hosted returns
  broken until the SC2 conversion; pillagedvillage -> forestobsidiantransition = control case.

### B-SUMMON-1: Summoned pets spawn NAKED / broken (no equipment, some immobile)
- **Symptom (Will):** "Summon Boneash" summons Boneash but he has **no weapon, no helmet, no
  chestplate, no greaves - nothing**. Earlier: the Blood-High-Priest soul's "Call the Blood
  Blade-Dancer" summon appeared as a **floating scythe, immobile** (bug F).
- **Cause:** the wave-created pets (and possibly the base Boneash) have incomplete equipment/visual
  wiring. Per CLAUDE.md lessons: pet equipment must be set via `_set_pet_equipment()` with hardcoded
  item paths - copying loot/equip fields from Monster.tpl → Pet.tpl CRASHES, so pets are authored
  bare and equipment is added back explicitly. If `_set_pet_equipment` wasn't called (or the item
  paths are wrong), the pet spawns naked. The floating-scythe = mesh/animation-table mismatch
  (the pet's mesh is a weapon-only rig, or charAnimationTable doesn't match the body mesh).
- **Fix approach:** THIS IS THE ENTITY CONTRACT SUITE'S JOB (spec in HANDOFF §4b, workflow
  wf_87586bbf-b63 was STOPPED on hold - RESUME it). It must: (1) for every summonable pet, verify
  mesh + charAnimationTable exist and are rig-compatible; (2) verify equipment is wired
  (`_set_pet_equipment` called with resolving paths) OR the pet is intentionally unarmed; (3) fail
  the build on any naked/floating/immobile pet. First fix Boneash + Blade-Dancer, then all wave pets.
  Files: tools/apply_svc_patches.py pet-creation blocks; reference the WORKING Lyia Leafsong pet.
- **Cross-check:** Will said "if this soul has this issue we probably have many others" - treat as
  systemic across ALL summon souls we created (bwpriest x3, lillued x3, and any other spawnObjects).
- **build28 (2026-07-08):** 12 broken pets repointed at their source monsters' loot-table
  loadouts (player uniques never auto-equip -> naked) + NEW validate_summon_pets gate. Verified
  present in the deployed arz (c4aa4d75); validator PASSes with upstream-only WARNs.
- **REPEAT-FILED (Will, live on build28): "summons are broken".** build29 findings, all fixed:
  (1) SOUL-GRANTED summon skills are gated by the SAME StartSkill anim abort as B-SOUL-PROC-2
  (see its RCA v2): a summon skill with a non-playable special anim NEVER SPAWNS its pet
  (strongbark_quillvines anim Roar x8 souls, barmanu_blizzard + gargantuanyeti_iceblast +
  nehebkau-class anim Summon x21 souls) - pcsafe clone + repoint like every other grant;
  (2) 25 soulskills pets (carrioncrow, peng, quillvine_03, skeleton_archer/soldier ladders)
  shipped with EMPTY monsterClassification while every working exemplar (Lyia, Boneash, base
  WraithLord) is Common - set to Common;
  (3) validate_summon_pets extended to cover the FULL chain from GRANTING ITEM to living pet:
  summon-skill castability (anim), itemSkillLevel vs spawnObjects ladder (warn), pet
  monsterClassification, plus the existing mesh/rig/equipment/controller/skill checks.
  Equipment-side (naked/floating) remains as build28 authored it; needs Will's walk verdict on
  freshly summoned pets (saved-item baking does not affect pets, they spawn from the DB).

### B-TOXEUS-1: Blood Toxeus shroud is still GREEN, not RED
- **Symptom (Will, screenshot 2):** the new Toxeus the Murderer, Devourer of Blood boss fights, but
  the **aura/shroud around him is GREEN** (the Athens-Toxeus poison shroud), not red.
- **Cause:** the rename+reskin (toxeus-devourer-rename) changed the MESH to the Athens rig +
  the crimson skin TEXTURE, but the SHROUD is a separate attached FX/skill (the Athens Toxeus has a
  green poison-cloud aura skill or a bound FX). We changed body color but not the aura FX color.
- **Fix approach:** find the aura/shroud FX on um_bloodtoxeus_99 (a skill in its skill list, or a
  charFX/bound-effect field) - it's inherited from the Athens Toxeus (green poison theme). Swap it
  to a red/blood-themed FX (there are red/blood FX in the DRX effects - trail_wep_spear uses blood;
  look for a red aura/cloud). Files: apply_svc_patches _create_blood_toxeus, the monster's FX/skill
  fields. Keep his Blood Boil kit; just recolor the ambient shroud.

## 🟠 P1 - confirmed broken, non-blocking

### B-SPRITE-1: Exploding sprites do not respawn (STILL - reconfirmed 2026-07-08)
- **Symptom:** the exploding sprites near the occultist pyre spawn once, then never again - Will
  stood on the volcano/pyre spawner for minutes, nothing new. (Was task #37A; STILL broken.)
- **Cause (hypothesis):** our placed t1_pitspawner cluster is missing the continuous-spawn config
  (spawn interval / max-alive / respawn-on-death fields) OR is a one-shot-per-level-load spawner
  vs the Greece exemplar's continuous one. Will's leave-and-return discriminator test was never
  reported back - needs it: leave the area + return; if 3 fresh sprites reappear = per-level-load
  refill (config gap); if none = spawner died with its brood (wrong record).
- **Fix approach:** diff our pit records vs the LIVE Greece occultist pit (which spawns
  continuously) field-by-field - spawn timing/limit/controller. Match Greece. Files:
  tools/build_section_surgery.py sprite/pit specs (the B2 block).

### B-TEMPLE-DOOR-1: "Temple Entrance - Locked ~ Sealed By Guardian" won't open
- **Symptom:** killing the guardian in front of the sealed temple door in the blood cave does NOT
  unseal it. (Was task #37C.)
- **DIAGNOSIS 2026-07-08 (byte-proven; 'never ported' REFUTED):** the full unlock chain is present
  and intact in build27. Doors = babtpl_waterfallroom_secretdoor.dbr + waterblocker.dbr
  (FixedItemDoor, locked=1, tagBloodCaveTempleEntrance; waterblocker carries the Sealed By Guardian
  hint tag) in drxbc2.lvl. Controller = open_bloodcave_portal.qst step 0 trigger 'Unlock Waterfall
  Door': Condition_KillAllCreaturesFromProxy(q_highpriest_lone, isResettable=1) ->
  Action_UnlockFixedItem on BOTH doors; ported byte-intact; quest registered at idx 97/256 (inside
  the load window since build22). Guardian proxy/pool/monsters all present under identical names
  (no soul-wave rename). Nothing to port, no slot to add, no rename.
- **Residual = RUNTIME** (quest adoption / proxy-death arming across region streaming; same
  reliability class as the widow-letter window bug). Will's original failing test predates the
  build22 window fix, so the door may ALREADY WORK. **DISCRIMINATOR (Will, on the fresh public-build
  character): in the blood cave waterfall room (drxBC2), kill the lone guardian miniboss in front of
  the Temple Entrance and see if it unlocks.** Unlocks = close this item (build22 fixed it). Still
  sealed = the proxy is not spawning its guardian (population wiring, sibling of B-SPRITE-1) or
  KillAllCreaturesFromProxy is not arming for an adopted control quest; investigate THAT, not the port.

### B-SMOKE-1: Region smoke density far below SV (STILL - reconfirmed)
- **Symptom:** some smoke present, but SV had FAR more, starting the moment you enter the section.
- **Cause:** the C4 atmosphere restore covered ENTITY emitters only; the REGION-WIDE ENVIRONMENT
  half (SD/0x18 or level 0x09 env params - volumetric fog) was never restored (vet hedge on record).
- **2026-07-08 REFUTATION:** the region-env transplant hypothesis is DEAD: the 0x09 env/fog record
  is byte-identical SV vs shipped for every affected level (the v1-vs-v2 divergence is a re-save
  framing marker, not content); SD/0x10 carry no fog delta. DO NOT transplant 0x09/0x17 (framing
  mismatch corrupts). Remaining levers: (a) map side = restore the still-dropped SV Delphi entities
  via INJECT_SPECS at SV-exact coords (delphilowlands02: t1_pitspawner_01 x2, t1_pitspawner_02,
  t1_lildude x6, soundobject_cageglow; delphilowlands04: cage_binding_fx01 + cage props + lildudes
  + vitstaffs; delphilowlands03: lildudes + vitstaffs) - in the 2026-07-08 map wave; (b) DB side =
  audit fog_occult_fx01/pit_fx01/pit_fx02/bugcloud_smallfx emission values vs SV-era - in the
  2026-07-08 DB wave (item 9). If both come back SV-faithful, the residual gap is engine-era
  rendering, not data.
- **✅ CLOSED PERMANENTLY 2026-07-28 (debt-map lane): BOTH levers came back SV-FAITHFUL. Verdict:
  the residual is engine-era rendering, not data.** No further data-side work; do not reopen this
  as a content bug, and (standing) do NOT transplant `0x09`/`0x17`.
  - **Lever (a) MAP SIDE = SHIPPED, and proven in the BUILT map (not just in the source specs).**
    `INJECT_SPECS` in `tools/build_section_surgery.py` carries every listed SV Delphi entity under
    explicit `--- B-SMOKE-1 (2026-07-08)` blocks at SV-exact float32 coords + rotations. Byte proof,
    comparing the **SVAERA donor** (pre-restore) against our **canonical build**
    (`local/Levels_merged.arc`), `0x05` instance counts + placed-record names:

    | level | SVAERA donor | ours | restored families present in ours |
    |---|---|---|---|
    | `DelphiLowlands02` | 145 inst, 0 marks | **164 inst (+19)** | pitspawner_01/02, lildude_01/02, bigobsidian, soundobject_cageglow, fog_occult_fx01, pit_fx01, pit_fx02, bugcloud_smallfx |
    | `DelphiLowlands03` | 29 inst, 0 marks | **36 inst (+7)** | lildude dress, vitstaff_01, bugcloud_smallfx |
    | `DelphiLowlands04` | 224 inst, 0 marks | **241 inst (+17)** | cage_binding_fx01, cage_medium, cage_small, soundobject_demoncage, lildude dress x3, vitstaff_01/05, fog_occult_fx01 |

  - **Lever (b) DB SIDE = SV-IDENTICAL.** Every one of the 4 FX records was diffed field-by-field
    between SV 0.98i's `database.arz` and our shipped `SoulvizierClassic.arz`:
    `records\drxmap\effects\fog_occult_fx01.dbr` (6 fields, **0 diffs**),
    `records\drxmap\effects\pit_fx01.dbr` (6 fields, **0 diffs**),
    `records\drxmap\effects\pit_fx02.dbr` (6 fields, **0 diffs**),
    `records\xpack\effects\particles\environment\bugcloud_smallfx.dbr` (5 fields, **0 diffs**).
    Nothing was down-tuned; there is no emission value left to raise.
  - **Lever (c) REGION ENV = already refuted above** (the `0x09` env/fog record is byte-identical
    SV vs shipped; the v1-vs-v2 divergence is a re-save framing marker).
  - All three data levers are therefore SV-exact: entities restored, FX records untouched, env
    identical. Any remaining perceived density gap is the TQAE renderer vs the TQIT-era renderer,
    which no data edit in this repo can change. Evidence scripts: session scratchpad
    `debtmap/smoke_map_proof.py` + `debtmap/smoke_fx_audit.py` (read-only).
  - **INDEPENDENTLY RE-VERIFIED 2026-07-28** (second pass, re-derived from the built map rather than
    trusted): the restored families are present in `local/Levels_merged.arc` with the exact per-record
    multiplicities `INJECT_SPECS` declares - `DelphiLowlands02` **164** `0x05` instances carrying
    pitspawner x3, lildude x6, bigobsidian x1, cageglow x1, fog_occult_fx01 x3, pit_fx01 x1,
    pit_fx02 x1, bugcloud_smallfx x1; `DelphiLowlands03` **36** instances carrying
    `drxmap/dress/t1_lildude_02` **x2**, `drxmap/dress/vitstaff_01` **x3**, bugcloud_smallfx x2;
    `DelphiLowlands04` **241** instances. Map lever confirmed shipped.

### B-TEXT-TAGS-1: 8 Blood Toxeus / Crimson Verdict tags render as raw strings in-game
- **Symptom:** on the PUBLIC item, Hemorrheus's name, the Crimson Verdict set name, its 4 set-piece
  item names, the Vein Render sword, and the Hemorrhage soul (name + description) display as raw tag
  strings (e.g. `tagSVCSetCrimsonVerdict`) instead of proper names. Verified: the deployed `Text.arc`
  is missing all 8 tags that shipped `.arz` records reference. Confirmed by `validate_tags` and
  enumerated in `docs/MULTIPLAYER_COMPAT.md` §M3.1 (+ the `docs/STEAM_RELEASE.md` pre-flight).
- **The 8 tags (each referenced by a deployed record, absent from `Text.arc`):**
  `tagMonsterHemorrheus`, `tagSVCSetCrimsonVerdict`, `tagSVCSoulHemorrhage`, `tagSVCSoulHemorrhageDESC`,
  `tagSVCarmCrimsonVerdict`, `tagSVChlmCrimsonVerdict`, `tagSVCtorCrimsonVerdict`, `tagSVCwpnVeinRender`.
- **Cause:** the known `build_text_arc.py` ↔ `build_svc_database.py` coupling gap - these tags postdate
  the `mod_authored_tags.txt` manifest, so the build's referenced-mod tag *gate* does not know it owns
  them and passes, yet they never got written into `Text.arc`. Not an MP/determinism/crash problem
  (name/description tags only), so friends-only co-op is unaffected - but it is visible to every public
  subscriber.
- **Fix approach:** add the 8 tags (and audit for siblings) so `build_text_arc.py` emits them, rebuild
  `Text.arc`. **COUPLED DEPLOY: arz + Text.arc must ship together** (tags changed). Then re-verify
  `validate_tags` has zero referenced-and-missing tags, redeploy locally + push the Workshop update.
  Files: `tools/build_text_arc.py`, the tag manifests (`work/.../Database/uber_soul_tags.txt` is the
  LIVE one), and whatever authored these records in `tools/apply_svc_patches.py`.

### B-SOUL-PROC-1: Soul-granted 'Activated on attack' skill never procs (NEW 2026-07-08, P1)
- **Symptom (Will, public build, co-op session, fresh level-5 Occultist):** the Crommyonian Sow
  Soul tooltip says "Grants Skill: Ground Smash (Activated on attack), Cooldown: 8 Seconds" but the
  skill NEVER activates when attacking.
- **Why the existing validator missed it:** validate_soul_augments only checks that
  itemSkillName / itemSkillAutoController REFERENCES RESOLVE; a proc needs the whole activation
  chain to be semantically right (controller Class + activation event + proc chance + the granted
  skill being an executable active skill with a valid animation on the wielder).
- **ROOT CAUSE FOUND (2026-07-08 recon, byte-verified): PORT REGRESSION, SYSTEMIC = 219 souls.**
  The souls set itemSkillName + itemSkillAutoController but omit itemSkillLevel, so the granted
  skill instantiates at level 0 = inactive (tooltip renders, controller has nothing castable).
  Base game sets itemSkillLevel on 876/876 granted-skill items; SV 0.98i on 941/941. A/B proof in
  our own arz: sstheno_soul (same controller + same skill class, level 4) works; gorgonguard_soul
  (SAME skill + SAME controller, level absent) is dead. 211 broken souls come from ONE function
  (apply_svc_patches _overhaul_generic_souls: OVERHAULS dict never includes itemSkillLevel) + 8
  hand-authored itemSkillLevel==0 (snaptooth/orythroneus/rocksting e/l + crowboar n/e).
- **Fix (spec'd, folded into the 2026-07-08 DB wave as item 7):** inject per-tier default
  itemSkillLevel (n/e/l = 1/2/3) in the overhaul apply loop when absent; bump the 8 zeros; extend
  the validator with semantic activation-chain checks (skill Class = Skill_*, itemSkillLevel >= 1,
  controller template = SkillAutoCastController.tpl with chanceToRun > 0 and triggerType set).
  Gate: broken chains 219 -> 0, previously-OK 1,152 souls byte-unchanged.
- **REPEAT-FILED (Will, live on build28, 2026-07-08): "the ground attack in the soul is still not
  working" / "souls skills are broken".** The build28 itemSkillLevel fix IS in the deployed arz
  (c4aa4d75: 1371/1371 granted-skill souls carry level >= 1, sow souls at 1/2/3) so the level fix
  was NECESSARY but NOT SUFFICIENT.
- **RCA v2 (B-SOUL-PROC-2, build29, disasm-proven):** Game.dll SkillManager::StartSkill (log
  string "Animation failed to start in SkillManager::StartSkill" va 0x1035c3b0, gate vcall at va
  0x102561d4) ABORTS the whole cast and returns false when the skill's skillSpecialAnimationName
  cannot start on the CASTER's animation table. Our shipped PC tables (SV's own, byte-identical
  port; anm_malepc01/anm_femalepc) define 32 special-anim names of which only TWO (AoE360,
  Colossus) exist in EVERY weapon row of both sexes. cyclops_groundsmash ("Ground Smash") carries
  anim ClubSlam, a Cyclops-rig animation in NO PC row: the proc can never fire for a player at any
  itemSkillLevel. 39 distinct soul-granted skills carry never-playable monster anims (ClubSlam
  x105 souls, Spit x55, Punch x36, BloodBoil x29, Summon x21, GroundPound, Bite, ...); dozens more
  (ThunderClap/Ensnare/CallOfTheHunt/...) play only with SOME weapon types. Working A/B from
  Will's own sessions: summon_boneash (NO special anim) fired; cyclops_groundsmash (ClubSlam)
  never did. Secondary defect, same chain: the basetemplates autocast controllers the souls
  inherit carry NO autoTargetRadius while every WORKING base-game Enemy/AttackEnemy controller
  carries 10-15 (the only base item using base_atenemy_onattack is the known-broken EE
  sihailongwang spear).
- **FIX (build29, SHIPPED in the wave):** apply_svc_patches _fix_granted_skill_castability:
  every soul-granted skill whose special anim is not universally playable is CLONED to
  records\skills\soulskills\pcsafe\ with the skillSpecialAnimationName field REMOVED entirely
  (exact base-parity: sampled base controller-cast grants carry the field ABSENT, never
  empty-string; wraithlordsummons + 172/204 base proc grants are anim-less) and the souls
  repointed; originals untouched so monsters/pets sharing them (melinoe_bloodboil = Blood
  Toxeus kit, spellbreaker, wraithlord deathnova) keep their animations. Enemy-targeted soul
  controllers lacking autoTargetRadius get 15.0 (base concrete-controller parity); Self/Ally
  controllers are deliberately untouched (base Self controllers use a wide 10-15 radius;
  forcing a small value could suppress self-buff auto-casts). Build29 counts: 60 skills cloned,
  442 soul grants repointed, 6 Enemy controllers given a radius. Invariant + the standalone
  validate_soul_augments now FAIL the build on any non-universal granted anim and any Enemy
  controller without a radius (negative-tested against the build28 arz, which they fail).
  NOTE for testing: TQ saves bake item properties at pickup, so souls already in a bag may keep
  dead grants; verify on FRESHLY DROPPED souls (the build29 starter chest's sow souls were the
  test vehicle; that slot is gone since build30 - use any boss/hero soul drop instead).
- **Same-gate siblings found (NOT fixed in build29, report-only):** player mastery skills with
  monster-only anims are equally uncastable and were already dead in SV (Earth drxmeteor anim
  MeteorShower; Medicine tree TelkineSummonSkeleton/TelekinesisStart; Storm spellbreaker anim
  Drain as a TREE skill). Fixing those changes mastery behavior; needs Will's call.

## 🟡 P2 - pending answers / smaller

### ✅ B-FX-DANGLING-1 (CLOSED b91, 2026-07-28): dangling Chris\UnarmedProjectile_FX01 particle refs
- **Symptom (as filed):** arz-wide, ~353 dangling refs to the nonexistent
  `Records\SandBox\Chris\UnarmedProjectile_FX01.dbr` in particleEffectNameN slots, incl. player
  Earth skills drxflamesurge/drxvolcanicorb. Cosmetic only (the engine skips the missing layer).
- **MEASURED:** the "~353" is **177 records x 353 field slots** (`particleEffectName2` 177 +
  `particleEffectName3` 176). The target exists nowhere in the UNION of the mod arz + the stock
  TQAE DB (0 of 92,311 names), though `records\sandbox\` itself ships 536 other records.
- **FIXED (b91)** by `tools/patches/fx_dangling_cleanup.py`: all 353 slots STRIPPED. Strip, not
  repoint, on **base-game absence parity** - of the 69 affected records that also exist in the
  stock DB, 69/69 have `particleEffectName2` ABSENT and 68/68 have `particleEffectName3` ABSENT.
  A repoint would invent a layer vanilla lacks; an empty-string ref is the B-TOXEUS-2
  loader-abort class.
- **`particleEffectAttachPoint2/3` sub-item: REJECTED-BY-EVIDENCE, deliberately NOT stripped.**
  Those same 69 base-game records carry the attach points PRESENT while the name slots are
  ABSENT, so an orphaned attach point IS the vanilla shape (731 exist arz-wide, inherited from
  the base game). Stripping them would deviate from parity. This also matches build30 F7a, which
  stripped only the name slots.
- **`wep_spear.dbr` bumpTexture sub-item: FIXED** - stripped, finishing build30 F3 (which
  repointed the mesh to base `RSpear14B.msh` and stripped the DRX `baseTexture` but left this
  sibling DRX skin field).
- **F7a superseded (BL-103):** the 3 `pcsafe` records F7a fixes are B-SOUL-PROC-2 CLONES that the
  clone step re-mints from their still-dangling PLAIN sources AFTER F7a runs - measured in the
  b91 round-1 build, where all 3 arrive carrying the ref again. F7a was a symptom patch the
  pipeline undid every build; the new sweep runs last over the final db and fixes the sources.
- **Gate:** `fx_dangling_cleanup.verify()` fails the build loud if any Chris ref survives.
- Report: `docs/reports/b91_debt_db.md` sec 1. **Residual (NEW ITEM):** 69 OTHER dangling FX
  `.dbr` refs to 24 distinct missing targets remain - see B-FX-DANGLING-2 below.

### B-FX-DANGLING-2 (NEW, opened b91 2026-07-28, P3): 69 other dangling FX .dbr refs
- Measured while closing B-FX-DANGLING-1 (which named only the Chris ref). 69 dangling slots
  across 24 distinct missing targets, by field: `particleEffectNames` 13, `targetFxPakName` 13,
  `particleEffectName1` 12, `skillBonusEffectName` 10, `warmUpEffectName` 8, `radiusEffectName` 7,
  `charFxPakSelfNames` 2, `waveEffectName`/`charFxPakOtherNames`/`warmupFxPakName`/
  `confusionDamageFxPak` 1 each.
- Top targets: `records\skills\nature\renewalfx.dbr` (10),
  `records\effects\combat\skill_charge_strike01.dbr` (8),
  `records\effects\combat\skill_lethal_strike01.dbr` (6),
  `records\effects\petfx\ summonpet_wisp_fxpak.dbr` (6 - note the stray LEADING SPACE in the
  path, likely the whole defect for that one), `records\effects\combat\skill_charge_trail01.dbr`
  (5), 4 `xxxrecords\...` typo-prefixed refs, 2 `records\sandbox\chris\fxpak02/03.dbr`, and one
  `# records\effects\default\buff04.dbr` (a commented-out ref left as a value).
- **NOT base-parity-provable as one class** the way the Chris slots were: several look like
  simple path typos that should be REPOINTED (the leading space, the `xxx` prefix, the `#`), not
  stripped. Each needs its own absent-vs-repoint call. Do NOT blanket-strip.
- Fix approach: reuse `tools/patches/fx_dangling_cleanup.py`'s mechanism, per-target decision
  table, base-parity check per record, record-diff intended-only.

### ~~B-GATE-HARDEN-1: build gates SKIP (not FAIL) outside the work/ layout (build30 delta vet)~~
- ~~The A9 render-chain + F2 summons-contract gates skip loudly when the game dir / staged
  Resources are absent (scratch determinism builds). Optional hardening: an env flag
  (SVC_REQUIRE_GATES=1 -> FAIL instead of SKIP) so a mis-pathed work build can never
  silently skip its gates. Also: persist stage-baseline arz copies (e.g. the D10 0e70ffe6
  baseline) under local/db_backups/ so intermediate record-diffs stay reproducible after
  session scratchpads are cleaned.~~
- **✅ CLOSED 2026-07-28 (branch `fix/debt-gate`). BOTH halves shipped.**
  - **HALF 1 - `SVC_REQUIRE_GATES`.** It had never been implemented (`grep SVC_REQUIRE_GATES tools/`
    returned nothing). Now: `build_svc_database._require_gates()` reads the flag (accepts
    `1/true/yes/on`, case-insensitive) and `_gate_unavailable(gate, reason, remedy)` is the single
    handler for "this gate cannot run here" - it prints the historical WARNING and continues when
    the flag is off (scratch / determinism rebuilds writing outside `work/` are unchanged), and
    raises `SystemExit` when it is on. Wired into **three** call sites, not two: **A9**
    render-chain, **F2** summons-contract, and **A5** Act-5 leak fix (`base_db is None` silently
    shipped an arz MISSING the post-Hades portal suppression - same blind-spot class, so it is
    covered rather than left as the next surprise).
  - **Second line of defence:** `validate_render_chain.validate()` now checks its OWN inputs and
    returns **2 (load error), never 0**, when `mod_resources` or `game_dir` is missing/unusable -
    so a direct CLI invocation that bypasses the caller's skip decision cannot produce a
    meaningless PASS either.
  - **Wired into the gate of record:** `scripts/bootstrap_working_mod.ps1` sets
    `SVC_REQUIRE_GATES=1` before invoking the build (respecting a pre-set value), because the
    work/-layout build is exactly the path that must never ship ungated. This is the blind spot
    that let the b89 malformed 148-byte navmesh stub survive every gate for 20+ builds.
  - **HALF 2 - stage-baseline persistence.** `build_svc_database._persist_stage_baseline()` runs
    immediately before `db.write_arz()` and copies the OUTGOING arz to
    `local/db_backups/<stem>_pre-<md5-8>.arz`. **Content-keyed**, so it is idempotent (rebuilding
    the same baseline twice writes one file) and self-labelling (the filename IS the hash a gate
    record cites). Every record-diff proof in this repo ("exactly 2 of 3629 records moved") needs
    the baseline it diffed against, and those had been living in session scratchpads that get
    cleaned - so a proof written last week could no longer be re-derived. `local/` is gitignored,
    so this costs the repo nothing. **Never fatal** (any error degrades to a printed note - a
    backup must not break a build); opt out with `SVC_NO_STAGE_BASELINE=1`.
  - **PLANTED NEGATIVE TEST** (new): `py tools/debug/negtest_require_gates.py` - **PASS**. Plants
    the exact "gate cannot run" condition both ways without a ~15-minute build: (1) flag OFF ->
    WARN + continue, historical behaviour preserved; (2) flag ON -> `SystemExit` naming the gate
    and the flag; (3) flag parsing, 6 truthy / 8 falsy spellings; (4)
    `validate_render_chain.validate` on missing dirs -> `rc=2`, never 0.
  - **PROOF (stage baseline):** direct exercise - first call persists
    `_smoke_stage_pre-99ebc56f.arz` with the md5 printed, second call is a no-op ("already
    persisted", same destination), a missing output (first-ever build) returns `None` cleanly, and
    `SVC_NO_STAGE_BASELINE=1` opts out. Smoke artifacts removed afterwards.
  - **NOT re-run this lane:** a full `build_svc_database.py` run (~15 min, and a parallel lane was
    actively rebuilding `work/.../SoulvizierClassic.arz` during this session - its size/mtime moved
    mid-lane). The changes are additive and confined to the skip branches plus a pre-write backup;
    both were exercised directly by the planted test above. The next real work/-layout build will
    exercise them end to end, and will now also drop its first stage baseline into
    `local/db_backups/`.

### B-AREA-NAME-1: Garden of Merchants minimap label reads 'Duister' (NEW 2026-07-08)
- **Symptom (Will, public build):** he teleported from the fountain camp into a garden/courtyard
  full of merchants (= the Garden of Merchants, destination wiring CORRECT), but the minimap/region
  name displayed 'Duister' (the Secret Place forest naming; Dutch for dark). The restored Garden
  level apparently carries a wrong display-name reference inherited during restoration.
- **Fix approach:** root-cause the level display-name mechanism (level blob field vs tag ref vs
  Text string); fix the Garden label and AUDIT ALL restored areas' labels (Uber Dungeon, Boss Arena,
  Sparta Crypt, Duister itself) for the same inherited-name defect. The 2026-07-08 map wave was told
  to investigate; if the fix is Text-side it rides the next arz+Text coupled push.
- **✅ CLOSED 2026-07-28 (debt-map lane). Root cause was TEXT-side, the fix is already shipped, and
  the audit + a class-wide gate now close it out.**
  - **MECHANISM (settled):** the minimap/zone banner label comes from the SD(`0x18`) REGION record's
    display TAG resolved through `Text.arc` - not from a level-blob field. SV 0.98i's own text
    shipped `tagMZoneGoM=Duister` (an upstream leftover: SV named the Garden region internally
    "Duister"), so the correctly-wired Garden region rendered the wrong string.
  - **FIX (upstream, BL-103, already live):** `tools/build_text_arc.py` `TEXT_FIX_TAGS` defines
    `tagMZoneGoM = 'Garden of Merchants'` as a single-definition override in the fix block. It is a
    pipeline edit, not a hand-patched arc, so every Text build reproduces it. No map rebuild is or
    was required (the SD region record itself was always correct).
  - **AUDIT (this lane, the part that was outstanding):** the full restored-area zone-label set was
    dumped from the SHIPPED SD region list with `tools/sd_format.py` (round-trip byte-identical
    `True` on `local/Levels_merged.arc`: SD v6, env=213, region=294) and resolved against the built
    `work/.../Text.arc` (4,481 mod tags) unioned with base `Text_EN.arc` (17,541 tags).
    **Result: 10/10 restored-area regions resolve, and every one names its OWN area. Zero SD display
    tags anywhere in the map fail to resolve (0 unresolved of 294 region records).** No sibling
    inherited the defect:
    `BCXcave/tagBCXcave -> 'Blood Cave'`, `BCXpassage -> 'Mysterious Passage'`,
    `BCXtemple -> 'Temple of Eternal Love'`, `BCXwalkway -> 'Sanctuary of the Bloodborn'`,
    `Duister/tagMZoneGoM -> 'Garden of Merchants'` (the fix, live), `Dark Forest -> 'Dark Forest'`,
    `tagSPRogueEncampment -> 'Rogue Encampment'`, `JoLandia -> 'Jolandia'`,
    `Olympian Arena/tagNewMZone1 -> 'Olympian Arena'`,
    `The Obsidian Halls/tagSVCRegionObsidianHalls -> 'The Obsidian Halls'`.
  - **GATE (the class gate this item owed):** `contracts_map.RESTORED_ZONE_LABEL_EXPECT` covered only
    `tagMZoneGoM`; it now registers **all 10** restored-area display tags, so `MAP-SD-2` asserts every
    restored SV area's region record resolves to a label naming that area. Negtest extended in
    `tools/contracts/_negtest_map.py`: one PLANTED defect per tag (each relabelled to "Duister", the
    exact bug Will hit) plus a clean-set assertion, with a fixture/oracle sync assert so a future
    added area cannot silently escape the gate.
  - **PROOFS:** `_negtest_map.py` **49/49 PASS** (10 new planted-defect checks + the clean-set check
    all green); `run_contracts.py --only map` against the live artifacts = 17 contracts, **0 P0 /
    0 P1 / 3 P2** (the 3 are pre-existing base-game `MAP-PORTAL-1`/`-3` noise, unchanged from the
    pre-change baseline run), **GATE: PASS**.
  - **INDEPENDENTLY RE-VERIFIED 2026-07-28** (second pass, claims re-derived from the artifacts
    rather than trusted): the shipped `Text.arc` (4,481 keys) resolves `tagMZoneGoM` = **"Garden of
    Merchants"**, and all **10/10** oracle tags resolve and name their own area under the same
    substring rule `MAP-SD-2` applies (`tagBCXcave`="Blood Cave", `tagBCXpassage`="Mysterious
    Passage", `tagBCXtemple`="Temple of Eternal Love", `tagBCXwalkway`="Sanctuary of the Bloodborn",
    `tagJoLandia`="Jolandia", `tagNewMZone1`="Olympian Arena", `tagSPDarkForest`="Dark Forest",
    `tagSPRogueEncampment`="Rogue Encampment", `tagSVCRegionObsidianHalls`="The Obsidian Halls"),
    0 unresolved. Residual `tagMPortalGoM` = **"Duister Portal"** confirmed still live and still a
    Will decision. Counts move to **57/57 negtest** and **18 contracts** after this lane added
    `MAP-EMPTY-1`; GATE still PASS at 0 P0 / 0 P1 / 3 P2.
  - **RESIDUAL, WILL DECISION (not shipped, evidence now complete):** the sibling tag
    `tagMPortalGoM` still reads **"Duister Portal"**. Arz-wide scan resolves it to exactly ONE record,
    `records\item\shrines\teleport\teleportshrine_gom.dbr` (Class `StrategicMovementTeleportShrine`,
    `description=tagMPortalGoM`) - the Garden of Merchants' own rift/teleport shrine (uid `e08e87ff`,
    bound to `DRXShrineTeleport_Duister`, healthy per the 07-10 Lane B audit). So the rift stop
    INSIDE the Garden of Merchants is labelled with the old area name. It is the same inherited-name
    defect class but a DIFFERENT player surface (a device name, not the area banner), it was
    explicitly "flagged for Will" by the original area-name audit and never ruled on, so this lane
    did NOT unilaterally rename it. One-line Text-side change if Will wants it (add
    `'tagMPortalGoM': 'Garden of Merchants Portal'` to `TEXT_FIX_TAGS`), Text-only, no map rebuild.

### B-TOXEUS-2 (P0, build29 RCA + FIX): Blood Toxeus stopped spawning on build28
- **Symptom (Will, TESTHUB, 2026-07-08):** the cave-mouth Blood Toxeus no longer spawns. Proxy
  q_bloodtoxeus_lone byte-verified present in the TESTHUB map; the SAME proxy+pool spawned him
  2026-07-07 on the build27 arz. Delta = the arz only.
- **RCA (byte-proven, build27-vs-build28 boss closure diff):** proxy + pool + monster stats are
  IDENTICAL; the ONLY closure delta is the B-TOXEUS-1 recolor: (1) new clone
  bloodtoxeus_envenomweapon set weaponEnchantment='' - an empty-string .dbr ref with ZERO
  precedent (base game 0 of 56 weaponEnchantment carriers; build27 0 of 56; enchantment-less
  base Skill_BuffSelfToggled records OMIT the field, 31 of 50); (2) new clone
  bloodtoxeus_summonlildude ADDED charFxPakSelfNames to a Skill_SpawnPetMonster - a field NO
  record of any Skill_SpawnPet* class carries in base or build27 (and the donor never had the
  green pak, so the recolor premise was wrong for this skill). Both zero-precedent field shapes
  are loader-abort suspects (unloadable monster = silent no-spawn). **The arz is shared, so the
  canonical secret-area Hemorrheus is equally dead on the PUBLIC build28 item = live P0.**
- **FIX (build29, Lane A):** the envenom clone DELETES the weaponEnchantment field (base-absence
  parity) and keeps the red leinth-aura pak (proven loadable in that exact field shape via
  leinth_aura_buff on a live-spawning boss); the lildude summon reverts to the shared donor
  record (boss skillName9/specialAttack5SkillName = exact build27 bytes; the clone is no longer
  created). Red-shroud intent KEPT (initialSkillName/skillName3 -> the envenom clone). NEW
  fail-loud invariant _verify_boss_kit_clone_shape (apply_svc_patches): a registered boss-kit
  clone must not add fields its donor lacks, must not blank a donor .dbr ref, and its refs must
  resolve. Negative-tested. Gate: boss + closure field-parity with build27 except the intended
  recolor deltas (verified in the build29 record diff). Will's walk test still decides.

### B-SUPRA-NOTIFY-1 (P3): supra formula grant is SILENT (placeholder tags)
- The Esfri chest quest grant (open_bloodcave_portal.qst, Hidden Chest Control) gives the supra
  formula via Action_GiveItem straight into the bag, but its notification uses SV's placeholder tags
  (tagTitleTagTESTER / tagLOCATIONTAGTESTER) so players get NO visible message and easily miss the
  reward. Inherited SV 0.98i debt, not a port regression. Fix: real notification text (Quests+Text
  coupling). See the 2026-07-08 Esfri recon in the resolved item below.
- **BUILD29 DISASM REFUTATION of the "chest tier-1" plan (LANE B COORDINATION, P0):** the closed
  RCA's mechanism claim ("set loot3Chance=100 on loottable_hidden_bloodcave_0{1,2,3} -> the chest
  always drops exactly 1 supra formula") is FALSE. Game.dll FixedItemContainerController disasm
  (0x10182120 / 0x10181530 / 0x10181da0): a chest spawns numSpawn items and picks ONE loot slot
  PER ITEM by roulette over the slots' chance values (chances are RELATIVE WEIGHTS, not
  independent gates). With the Esti tables' chances summing 113.2 and numSpawn ~18-20, a
  loot3Chance=100 slot would put a supra formula on ~47% of every draw = ~8-9 formulas per open,
  and can never guarantee exactly 1. The ONLY exactly-once mechanism is the EXISTING quest
  Action_GiveItem (Condition_UseFixedItem -> token + GiveItem) - i.e. SV's original design.
  **Lane A therefore left the Esti loot tables byte-identical to build28, and Lane B's
  _neutralize_esti_chest_supra (already written into tools/build_quest_files.py expecting the
  chest-side grant) MUST NOT SHIP - with it the player would get ZERO formulas ever. Keep the
  quest grant; the whole item then needs no change at all (notification tags already resolve).**
- **ALREADY RESOLVED Text-side (verified during build29):** build_text_arc
  QUEST_INTEGRATION_TAGS defines tagLOCATIONTAGTESTER = "The Blood Cave" and tagTitleTagTESTER =
  "Esti's Hidden Chest", so the popup renders real strings, not raw tags (the build29 attempt to
  redefine them tripped the duplicate-tag gate, proving the definitions live). Residual polish
  only: the quest still references the TESTER tag KEYS and "Esti's" is a probable "Esfri's" typo;
  wording pass for Will.

### B-TESTHUB-TOXEUS-1 (Will request 2026-07-08): remove cave-mouth Toxeus from TESTHUB
- The Blood Toxeus/Hemorrheus test spawn ~9.9u outside the blood-cave mouth (TESTHUB-only) BLOCKS
  Will from walking into the cave to test the hub portals. Remove it permanently from the TESTHUB
  injection (canonical never had it; the superboss lives in the waterfall chamber). Routed to the
  map wave; ships in a local interim TESTHUB test build for Will now + the vetted wave build.

### B-OLYMPUS-TELESHRINE-1 - RESOLVED BETTER THAN FILED (build31e M13a, 2026-07-10): shrine RESTORED
- The M13a GROUPS restoration re-bound teleportshrineolympus01 (uid 3c007d48...) into
  Shrine_Teleport_Hades as part of base parity - the Olympus rift shrine now WORKS instead of
  dangling (strictly better than the leave-as-is ruling; nothing removed, base-game behavior
  restored). Walk-verify with the M13 wave: activate the shrine at the Olympus summit approach
  and check it joins the rift/teleport network. History: it was dangling since the original
  merge (SV's TQIT-era Shrine_Teleport_Hades clobbered base's; the M6 recon, check_respawn.py).

### B-DB-HYGIENE-1 (P3): dead orphan record potionexp_test.dbr
- records/item/miscellaneous/oneshot/potionexp_test.dbr carries a corrupted NEGATIVE
  bonusExperiencePoints (int32 overflow of ~4e9) and has ZERO inbound references. Harmless dead
  test artifact from upstream; remove or exclude when convenient (the 2026-07-08 DB wave may
  already handle it as its hygiene item).

### B-DUISTER-EXPLORE: Secret Place ("Duister") first-visit findings incomplete
- Will reached Duister but died to Toxeus before touring the other areas. All 5 hub destinations
  (Knossos/Uber, Garden, Sparta, Secret Place, Murder Bunny) still need a full walk-test once the
  portals are pretty + return works. Duister's own portals all reported broken (see B-PORTAL-3).

### BUILD29 CONTRACT-SUITE DB FIXES (2026-07-08, shipped with the B-SOUL-PROC-2 wave)
Violations found by the finished entity contract suite (feat/contract-suite), fixed in
apply_svc_patches _fix_wave29_contract_items:
- SOUL-NAME-RESOLVES (8): satyrmagi_soul + satyrspiritcaller_soul {n,e,l} carried undefined
  placeholder tagSoul1 -> new tags tagSVCSoulSatyrMagi / tagSVCSoulSatyrSpiritcaller with real
  names; test\kyrashadowdancer_soul {e,l} carried bare tagSoulName -> repointed at the live
  tagSoulName323. (SV 0.98i upstream carries the SAME dangling tags - inherited debt, no
  original names existed to prefer. The test\kyra pair is dropped by ZERO monsters =
  unreachable dev items; tags fixed anyway per the brief. The live maenad kyra souls already
  used tagSoulName323 and are untouched.)
- SOUL-AUGMENT-LEVEL (4): crowboar_soul_n/e augmentSkillLevel1/2 == 0 -> n=1, e=2 (l untouched).
- MONSTER-SKILLS-LOOT (5, was reported as 10 refs): blood-cave bodies ancestralwarrior a-e
  skillName1 pointed at nonexistent Melee_Poison09-12_10.dbr -> repointed at the real
  attackmelee_poison09-12_10.dbr (same dir, SV renamed it).
- MONSTER-SPAWN-ELIGIBILITY (1): bw_priest_houndmaster pool spawnMax=2 with
  championMin=championMax=2 left 0 guaranteed main slots (champion crowd-out, Blood-Toxeus
  class) -> spawnMax=3.
- SUMMON-PET-CLASSIFICATION (25, was reported as 17): soulskills pets missing
  monsterClassification -> Common (see B-SUMMON-1 build29 note).
- B-SUPRA-NOTIFY-1 (2 tags): already resolved by build_text_arc QUEST_INTEGRATION_TAGS
  (see its entry); no change needed.
(68x MAP-REF-1 dropped dyer/Great-Wall NPCs = map lane, not this wave.)

## 🔵 STANDING PENDING WORK (from the master queue - not new bugs)

> ## ⚠️ STATUS SWEEP 2026-07-28 (`fix/debt-docs`, DOCBOARD-STALE-QUEUES) - **READ THIS BEFORE
> ## IMPLEMENTING ANYTHING BELOW.** The BUILD31/BUILD32 queue text below is the ORIGINAL 2026-07-09
> ## brief and still reads as an unbuilt work list. **It is not.** Almost the entire train shipped
> ## across build31/build31g/build32/build32a/build36. This block is the authoritative status; the
> ## prose below is kept verbatim as the DESIGN RECORD (what Will approved and why), per the
> ## retirement protocol - it is not deleted, it is superseded by this table.
>
> Method: every named record probed against the SHIPPED arz
> (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, 51,085 records, the build50-dev artifact)
> with `tools/arz_patcher.ArzDatabase`, cross-checked against the owning code in
> `tools/apply_svc_patches.py` / `build_svc_database.py` / `build_section_surgery.py` and the
> BUILD31-BUILD47 gate records. Values below are read out of the arz, not out of a report.
>
> | item | status | proof (from the SHIPPED arz / build path) |
> |---|---|---|
> | Q1 Typhon->Rhodes unlock | **SHIPPED build30.3** (+ KEEP decision 2026-07-28) | `_add_typhon_rhodes_unlock`; INERT in-game, kept as a byte-superset - see the Q3 archive block below |
> | MASTERY WAVE 1 (B1-B6) | **SHIPPED build31** | gate log below, arz `06a9a24a`, 28-record bucketed diff |
> | D19 Huo-ren immobile summon | **SHIPPED build31** | arz `95e816d3`; pet-mobility assert now permanent |
> | Q3 herald + kill-gated unlock | **SHIPPED build31 (DEV)** | `portal_master_olympus.dbr` PRESENT; `OLYMPUS_RHODES_NPC_SPEC` WIRED build31g |
> | **Q2 portal-master NPC** | **SHIPPED build32/32a** | `records\quests\portal_master_helos.dbr` PRESENT; `PORTAL_MASTER_SPEC` LIVE in INJECT_SPECS @ startingfarmland06d (76.50,0.60,189.50); dialog on the sv_commonmechanics refire step. All three artifacts landed. |
> | D11 Rally | **SHIPPED build31 (G3)** | `drxrallybuff.skillCooldownTime` = **30.0** (was 45) |
> | D12 Ichthian Myrmidon soul | **SHIPPED build31 (G3)** | `coastalichthianmyrmidon_soul_l.characterLife` = **650.0**; 13 myrmidon records present |
> | D13 Eater of Days summon | **SHIPPED build31 (Group 4)** | `eaterofdays_soul_l.itemSkillName` = `summon_eaterofdays.dbr`, level 3; pets `eaterofdays_1..3` |
> | D14 Pygmalion replicator summon | **SHIPPED build31 (Group 4)** | `pygmalion_soul_l.itemSkillName` = `summon_pygmalion.dbr`, level 3; pets `pygmalion_1..3` |
> | D15 reward-potion name colors | **SHIPPED (Text lane)** | `build_text_arc.TEXT_FIX_TAGS` carries all four `^M` overrides (`tagNewItem3/70/4/69`) |
> | **D16 Shadow Stalker overhaul** | **SHIPPED build31 (G3) + build36 (D16b)** | all 20 tiers: `skillName7` = `shadowstalker_distortionfield.dbr` (the suicide shadowstrike is GONE), `characterLife` **500 -> 2210** (was flat 297), hit **120-150 -> 386-492** (was flat 83-98). D16b added the AoE-petrify shadowzap. |
> | **D17 Core Dweller** | **SHIPPED build31 (G3)** | all 20 tiers x1.75 life: t1 **1367.1**, t20 **3937.5** (were 781 / 2250); str t1 **293.8**, t20 **531.2**; taunt kit untouched |
> | D18a/D18b Emberscale | **SHIPPED build31 (G3)** | `03_flameguardslayer.relicBitmap` = `AnimalPart13B_L.tex` (de-turtled), `offensiveFireModifier` `[8,16,24,32,40]`, burn `[14,28,42,56,70]`, armor-melt cleared |
> | D20 War-King Sarpedon summon | **SHIPPED build31 (Group 4)** | `sarpedon_soul_l.itemSkillName` = `summon_sarpedon.dbr`, level 3; `um_sarpedon_41` + pets 1..3 |
> | D21 Long Nu the Flame Mother | **SHIPPED build31 (Group 4)** | `summon_longnu.dbr` spawns `longnu_1/2/3` |
> | Enslaver (item 5) | **SHIPPED build31/32**, later refined | `um_toxeus_enslaver_99`; b49 breadth cut (build40), b71/b81 identity, R-48 100% soul (b90) |
> | N4-DB Vashkarr | **SHIPPED build32 + build32a map** | `um_vashkarr_99` + `svc_vashkarr_{fodder,lance,warlock}` + `svc_vashkarr_summonhorde` + `q_vashkarr_lone` (proxy AND pool) + `vashkarr_soul_{n,e,l}`; `VASHKARR_SPEC` LIVE @ random05a (24.00,1.00,31.70). No summon soul - correct, that was Will's ruling. |
> | N5 thrown weapons | **SHIPPED build32 (Group E)** | 4 `svc_thrown_*_formula` records; `_restore_thrown_weapon_drops` 198/198 restored |
> | N6-DB Obsidian roulette | **SHIPPED build32 (Group F)** | 68 records incl. `svc_obsidianhoard_01/02/03`, `um_sarkoth_99`, `um_ilsevar_99`; `voranthys_soul_l.itemSkillName` = `summon_voranthys.dbr` |
> | N7 sepulchral-wyrm hordes | **SHIPPED build32 (Group G)** | 25 sepulchralwyrm records + the Sepulchral Scale charm chain |
> | **MASTERY WAVE 2** | **SHIPPED build32 (Group D)** | `drxforceofnature` cd **180.0** (was 360), `drxoutsidersummons` cd **120.0** (was 360), `drxdeathward` cd **180.0** (was 300) - read out of the shipped arz |
> | FEATURE: throwing weapons in the campaign | **SHIPPED** - same work as N5 | duplicate entry of N5, not a second item |
> | DESCRIPTION CORRECTIONS | **SHIPPED** `02ce3e5` | see that entry above for the full closeout + the residuals fixed 2026-07-28 |
> | N2 Typhon-gate mesh swap | **CANCELLED** by Will (portal-master model C) | as the queue text already says |
>
> **STILL GENUINELY OPEN out of this queue (the short list a fix lane should actually work from):**
> - **Boss-summon-soul candidates remaining** - the ranked 578-soul candidate list below is a
>   PROPOSAL awaiting Will's batch approval, not a build queue. Standing ruling: only convert
>   summon-souls Will EXPLICITLY names. UNCHANGED, still open.
> - **Q4 dead-content one-liners** - the individual sub-items (bossarena EnterVolume, widowletter
>   honor-branch chest, chimera double-extension rename, q15 reconciliation) were folded into the
>   Quests rebuilds; each is implemented in `build_quest_files.py`
>   (`_fix_widowletter_chest_branch`, `_fix_chimera_chest_typo`, the volume rename) but this sweep
>   did NOT re-verify them in-game.
> - Everything on the DEBT REGISTER above, which is the maintained list.
>
> **CORRECTION to the triage that opened this item:** it cited "Emberteeth" as an example of a
> genuinely-unbuilt item that "greps to nothing". **That is wrong** - `um_emberteeth.dbr` plus
> `emberteeth_soul_{n,e,l}` are all PRESENT in the shipped arz. The genuinely-absent grep was
> "emberscale", and only because D18's records are named `svc_flameguard\0N_flameguardslayer.dbr`
> (the Emberscale charm is a turtle-shell-pattern clone, so the display name and the record path
> differ). Both are shipped.

### BUILD31 DB WAVE QUEUE (Will via coordinator, 2026-07-09; batch as one wave)
Train contents (commit-group order per coordinator 2026-07-09): (0) Q1 Typhon->Rhodes portal
unlock (URGENT, Quests.arc lane - SHIPPED as build30.3, live on Steam 2026-07-09; the unlock
event now lives in the shipped Quests.arc 631a2b4d - build ON it, keep it byte-intact in any
Quests rebuild + gate-assert its survival), (1) MASTERY WAVE 1 broken fixes B1-B6 + the new
player-skill-anim gate (**GATED + GREEN 2026-07-09**, arz 06a9a24a, commit afb30a0 - see the
gate log below), (D19) IMMOBILE HUO-REN SUMMON P1 - **DONE, gated, arz 95e816d3** (see item
below), (Q3+Q4 batch) Olympus herald NPC + kill-gated instant Rhodes unlock (M13a proxy
BossProxy_20_Typhon - verify the placed proxy record name) + Q4 dead-content one-liners
(bossarena EnterVolume volume -> volume_startolympianarena; widowletter honor-branch chest
alignment; chimera .dbr.dbr double-extension coordinated rename; q15 reconciliation per the
audit note - all ride ONE Quests.arc rebuild; Q4 item 4 testquest deregistration = MAP lane),
(2) Mastery Wave 1 Defense/Earth/Storm boosts + D16 Shadow Stalker
+ D17 Core Dweller, (3) D11 + D12 + D15 + **D18a Emberscale icon + D18b Emberscale effect
redesign**, (4) D13 + D14 + **D20 War King Sarpedon summon soul** + **D21 Long Nu the Flame
Mother summon soul (Will 2026-07-09: 'her soul needs to be able to summon her'; standard
recipe + the D19 mobility law from birth; find her records via 'Long Nu'/'Flame Mother' tags;
keep existing augments unless conflicting, report)**, (5) Enslaver (approved),
(6) N4-DB Vashkarr, (7) Q2 portal-master NPC (arz + Quests + Text coupled) - ✅ SHIPPED build32/32a, all three artifacts. N2 Typhon-gate mesh
swap = CANCELLED (Will chose the portal-master model C; existing walk-through portals stay
transitionally, retire in phase 2). BUILD32 additions (Will blanket sign-off 2026-07-09):
**N5 THROWING WEAPONS APPROVED** at ALL designer recommendations (faithful base drop weights
static_roh=400/roh=1/12 bosses; merchants DEFERRED; all 3 supers 'Sanguine Orbit' /
'The Last Word' / 'Charon's Toll'; formulas w100 supra slots 25-27 + supra_special 26-28,
reagents 1L+1E+1MI-thrown; design doc = tasks/ab8a4644fa12b0169.output;
_restore_thrown_weapon_drops faithful-copy + fail-loud gate, _add_supra_thrown_weapons clones
base thrown records - avoid the fenrirsbite stray mesh; D5 full-mesh scan must show the supers
resolve); **N7 sepulchral-wyrm hordes PRE-AUTHORIZED** (implement at designer recommendation
when the doc lands, no further sign-off).

> **GROUP 1 GATE LOG (2026-07-09, DB lane):** arz 06a9a24a (54,660,353 B) vs build30.2 baseline
> 3f605741. Record-diff = EXACTLY 28 records, all bucketed to B1-B6 (0 unbucketed): drxmeteor/
> drxthunderball/drxenslavespirit anim -> '' (B1/2/3); drxweaponpool_shieldsmash min 0->[12..61] +
> modifier 0->[20..50] (B4); nightmare_01..20 skillName1 repoint (lowercase resolving MasterMind
> path) + skillLevel1 min(tier,12) ramp (B5); anm_malepc01 + anm_femalepc gained row-matched
> SpecialAnim/Ref pairs for Taunt/Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/Hew into free
> idx<=14 (B6, pure additions); two Dream passives '0'->'' (hygiene). Gates ALL PASS: new
> player-skill-anim gate PASS on arz + NEGATIVE test FAILS correctly on the b30.2 baseline
> (Meteor/Thunderball/Bonespire + mp_taunt/hailofaxes/shenpao/breathattack/smokecloud);
> validate_soul_augments 0/0; validate_mastery_golden (Occult/Hunting) intact; validate_summon_pets
> PASS; validate_tags PASS; contracts souls+summons 0 P0/0 P1 (112 pre-existing upstream P2, not
> Group-1 records); det-2x rebuild both == committed 06a9a24a. No gate-code fixes needed.

### D19 FIXED (build31, arz 95e816d3, det-2x, gated): Huo-ren summon was IMMOBILE
- **Symptom (Will, live):** "I can summon Huo-ren the mountainblade... he is broken he doesnt move."
- **ROOT CAUSE (bone-level proof 2026-07-09; the suspected axes all EXONERATED - runSpeed 0.96,
  controller, classification all fine):** (1) the F2 loadout under-mirrored the source -
  um_mountainblade_43 equips RightHand=100 (1h_dyn) + LeftHand=100 (shield) + Torso, the pet got
  Torso ONLY -> WEAPONLESS -> engine uses the UNARMED anim row; (2) anm_dragonian defines NO
  unarmedRunAnim (base dragonians are never unarmed); (3) the source-copied unarmedRunAnim=
  CrocMan_Run.anm is FOREIGN-RIG: flameguardmesh shares 30/30 bone tokens with Dragonian01.msh,
  4 with CrocMan; CrocMan_Run binds 2/19 tracks -> unplayable. Live um_mountainblade/em_ravager
  move because their WEAPONED row falls back to the table's Dragonian_Run; the weaponless pet had
  no fallback -> immobile statue. (Evidence: scratchpad d19_*.py; bone test d19_bone_test.py.)
- **FIX (builder-level, feeds D13/D14/D20/D21/Voranthys/Enslaver from birth):** (a) D9 loadout now
  mirrors the source's hands (RightHand 1h_dyn trio + LeftHand shield trio + Torso) -> pet lives
  on the sHanded row = the exact configuration the LIVE source hero moves with; (b) D8 Xeiwang
  loadout=None premise REFUTED (um_xaiweng_48 equips RightHand/Torso/Forearm/LowerBody @100) ->
  full source-exact commondynamic mirror (also fixes his naked-hand B-SUMMON-1 class); (c) NEW
  fail-loud D19 PET-MOBILITY assert in _build_boss_summon (primary anim row must have TABLE
  RunAnim; stationary-rig tables exempt); (d) validate_summon_pets extended with the same law
  (h. LOCOMOTION: primary row weapon-derived - RightHand=weapon, LeftHand weapon-vs-shield via
  weight>0 loot tables, dual-wield -> dHanded; locomotion must come from the TABLE or a
  table-family override; foreign-family overrides do NOT count). NEGATIVE-TESTED: exactly
  mountainblade_1/2/3 FAIL pre-fix (bwpriest dual-wield correctly passes via dHanded); PASS
  post-fix. Record-diff vs Group-1 06a9a24a = EXACTLY 6 records (mountainblade_1/2/3 + xeiwang
  _1/2/3), every delta a chanceToEquip/loot field. det-2x = 95e816d3 both runs. Pets spawn fresh
  from the DB per cast -> retroactive for existing characters.
- **D7 Toxeus verified NOT in the immobile class** (unarmed but anm_skeleton01 covers
  unarmedRunAnim). His HAND slots left unchanged: the source's RightHand tables are SVC
  set/unique tables (crimsonverdict_guaranteed) = pet auto-equip risk; flag for a later pass.
Mastery specs = docs/MASTERY_AUDIT_2026-07-09.md (§2 broken fixes, §3 Wave 1; the no-removal
standing rule in its header is BINDING). Broken player skills outrank feature items.
Each group: gates + bucketed record-diff + commit; whole set -> independent delta-vet before
ship (coordinator dispatches); DEV-deploy for Will after major groups is fine (local only).
Will's standing ruling: only convert summon-souls he EXPLICITLY names.

- **Q1 IMPLEMENTED (2026-07-09): Olympus -> Rhodes portal unlock.** M7 RCA: the portal record
  (xq00_olympus_portaltorhodes, FixedItemTeleport locked=1 'Opened by Zeus after Typhon
  Killed') is unlocked by an engine-internal campaign hook that never fires in Custom Quest;
  no quest references it. FIX (tools/build_quest_files.py _add_typhon_rhodes_unlock): ONE
  trigger appended to the vanilla controller 'quest that controls bosses and their doors.qst'
  (already in-arc + registered + never completes + already evaluates this exact token):
  OnLevelLoad + OwnsTriggerToken('Olympus - Typhon Defeated') -> Action_UnlockFixedItem
  (canReFire=1; field shapes mirror the HOST file's own byte-verified idioms - no
  isQuestCritical2, no delayTime). Repeat-on-load = idempotent + retroactive for existing
  token-holders (Will's main). Rebuilt Quests.arc 631a2b4d; entry-diff vs shipped 846c43f3 =
  EXACTLY the host quest; quest-record contract PASS (107 records). SHIPPED as build30.3.
  **Q1 FAILED IN-GAME (Will, fresh session, 2026-07-09): Typhon killed, unlock event present,
  still NO portal.** Confirms M7's FixedItemTeleport-destination-is-engine-internal risk.

- **Q3 SHIPPED TO DEV (2026-07-09 night, Will escalation): instant kill unlock + token reload
  path + herald fallback, coupled arz bd6ae869 + Quests 3db3764c + Text 06c04985.**
  - **DB EXONERATED (the 'SV overrides an engine hook' hypothesis REFUTED, full-arz scan
    q3_engine_chain_hunt.py + q3_gameengine_removed.py):** ZERO records in OUR arz AND ZERO in
    BASE reference portaltorhodes/olympusportaltarget/typhontomb_portaltoolympus, any record
    type, any namespace. All 49 engine-namespace overrides (gameengine/combatequations/
    balance/itemcost/quests.dbr) diffed field-by-field vs base: every delta is SV/DRX
    balance/UI identity; quests.dbr byte-identical; NOTHING scene/portal/act/campaign-related.
    There is no data-side hook to restore - base opens xq00 from ENGINE CODE (end-of-campaign
    event) that never fires in Custom Quest.
  - **q15-vs-xq00 ANSWERED:** q15 (tomb->Olympus) works because base DATA unlocks it (quest
    15's own Action_UnlockFixedItem on the Typhon-proxy kill). xq00 has no unlocker in ANY
    data. The kill trigger makes xq00's chain structurally IDENTICAL to the proven q15 chain;
    M13a's GROUPS pairing restore (build31e) supplies the destination side.
  - **SHIPPED (one host-step append, 'quest that controls bosses and their doors.qst'):**
    (1) INSTANT: Condition_KillAllCreaturesFromProxy(Records\Proxies Boss\Boss\
    BossProxy_20_Typhon_Titan.dbr - byte-verified LIVE: quest 15 grants Will's token on this
    exact condition) -> Action_UnlockFixedItem(xq00, canReFire=1); (2) Q1 token+OnLevelLoad
    reload path KEPT (Will's main gets the portal on next Olympus entry, no re-kill);
    (3) HERALD fallback: Action_BoatDialog(records\quests\portal_master_olympus.dbr, onOff=1,
    x=700 y=41 z=-6466 = the base game's own xq00_rhodes_olympusportaltarget landing) gated on
    the token; NPC record cloned from knossos_boatmantoegypt (proven boat-dialog Npc shape,
    GreekSailor02 base art = render-safe), name 'Keryx, Herald of Olympus', 3 new tags
    (validate_tags PASS). **MAP LANE (a4207d65): the record name records\quests\
    portal_master_olympus.dbr + placement spec are now FINAL - wire
    OLYMPUS_RHODES_NPC_SPEC_PENDING into INJECT_SPECS on the next map build.**
  - Gates: quest-record contract PASS (107); Quests entry-diff vs shipped 631a2b4d = EXACTLY
    the host quest with exactly the new strings; arz record-diff vs D19 95e816d3 = EXACTLY
    +1 ADDED (the herald); golden freeze PASS on the pair; all arz internal gates green.
  - **WILL'S TEST (DEV): load main at Olympus summit -> the Rhodes portal should BE OPEN
    (token path fires on level load; M13a pairing gives it a destination). Fresh kill path:
    kill Typhon -> portal opens AT THE KILL, in view, no reload. The herald NPC appears at the
    summit only after the MAP lane wires the placement (next map build) - it is the fallback
    if the portal still teleports nowhere.**

- **Q3 archive (2026-07-09 day): Olympus->Rhodes = COPY SVAERA, not a quest. QUESTS-LANE
  VERDICT: NO restore needed.** Coordinator hypothesis (build22 dropped IT-act main
  quest registrations -> Rhodes campaign won't activate) is REFUTED by byte analysis
  (scratchpad q3_registry_diff.py / q3_content_diff.py / q3_portal_refs.py):
  - SVAERA registers 254 QUESTS entries; ours 256. **SVAERA-registered identities absent from
    our registry: 0.** Every SVAERA main quest (scripted scene_rhodes, xq03_theroadtohades,
    xq06_thethroneofhades, quest 10-15, all XPack2/3/4) is registered, cleanly shifted +4 by the
    build22 SV-quest insertion, all inside the 256 window (Rhodes/Hades at idx 108-138, far in).
  - Quest FILE presence: **0 SVAERA .qst files missing** from our Quests.arc (we ship all 100 +
    our 6). Only ONE file byte-differs from SVAERA: 'quest that controls bosses and their
    doors.qst' (+804B = our Q1 trigger APPENDED = byte-superset, all SVAERA behavior preserved).
    The 2 added endpoint-cap controllers (x4_other_001_control_expansionportals,
    xquest_controlsbossdoors) surgically remove ONLY the POST-Hades IT->EE / IT->Ragnarok
    EXPANSION portals - they do NOT touch Rhodes/Hades progression.
  - **NO quest in SVAERA OR the base game references xq00_olympus_portaltorhodes** (corroborates
    M7). SVAERA (a working Custom Quest that runs the full Rhodes/Hades campaign) drives the
    Olympus->Rhodes transition MAP-SIDE, not via a quest -> the fix belongs to the MAP LANE
    (a4207d65): make our OlympusFinal02 portal instance [41] born-open (locked=0) like SVAERA's,
    OR replicate SVAERA's placed transition. There is nothing for the Quests lane to author.
  - **Q1 unlock trigger recommendation:** it is the ONLY non-SVAERA-faithful edit in our
    Quests.arc and it is INERT (failed in-game). Once the map lane makes the portal born-open it
    is fully redundant. RECOMMEND reverting 'quest that controls bosses and their doors.qst' to
    byte-identical SVAERA (drop _add_typhon_rhodes_unlock) for fidelity; harmless if kept.
    ~~DECISION DEFERRED to coordinator + map-lane mechanism report.~~ If kept, it must remain a
    byte-superset (the survival gate-assert still holds).
  - ✅ **DECISION MADE 2026-07-28 (`fix/debt-docs`): KEEP.** Written into the code at
    `tools/build_quest_files.py:_add_typhon_rhodes_unlock` (a FIDELITY DECISION docstring block), so
    the survival gate-asserts now have a stated owner instead of guarding an undecided delta.
    Rationale: (1) it is a byte-SUPERSET, not a mutation - the only touched file is the
    already-registered, never-completing controller quest, +804 B of pure append, every SVAERA
    behaviour preserved verbatim; (2) reverting would NOT restore SVAERA fidelity, because Q3's
    kill-gated instant unlock builds on the SAME host step, SAME `Action_UnlockFixedItem`, SAME
    portal record - dropping Q1 only deletes the token + OnLevelLoad RELOAD path, i.e. the thing
    that gives an EXISTING Typhon-slayer (Will's main) the portal without re-killing the boss;
    (3) `canReFire=1` + OnLevelLoad makes it idempotent and retroactive, and an unlock on an
    engine-locked fixed item is a no-op - exactly the observed build30.3 outcome, so keeping it
    costs nothing at runtime; (4) reverting costs a Quests.arc rebuild + a coupled Levels+Quests
    redeploy for zero player-visible benefit. IF a future lane reverts it, it must delete the
    survival asserts with it and record the reversal in `docs/WILL_RULINGS.md`.
  - COUPLED SHIP: map(born-open portal) is the load-bearing change; arz/Quests/Text unchanged on
    the DB lane for Q3.
- ✅ **SHIPPED build32 (DB+Quests) + build32a (map M8)**: `records\quests\portal_master_helos.dbr` is
  in the arz, `PORTAL_MASTER_SPEC` is LIVE in `INJECT_SPECS` @ startingfarmland06d local
  (76.50,0.60,189.50), and the boat dialog rides the `sv_commonmechanics` refire step per the
  registry law (no new registration). Design record follows.
  **Q2 QUEUED: PORTAL-MASTER NPC for SV-area travel (Will chose model C; map lane M8b has the
  mechanism analysis).** DB+Quests+Text triple: (a) friendly quest-NPC record (base boatman
  class pattern, render-safe mesh per D5 law, amgoz1-voice name e.g. 'Almyros the Wayfarer' +
  'Portal Master' title tag); (b) boat-dialog quest offering the 4 SV destinations (Garden of
  Merchants / Secret Place / Uber Dungeon / Sparta Crypt), each -> Action_BoatDialog teleport
  to landing coords from the map lane (coordinate); QUESTS REGISTRY LAW: events append to an
  already-registered loaded quest (sv_commonmechanics = natural host), NO new registrations;
  verify action shapes against base boatman quests (quest 8 to-egypt, quest 7 knossos) via
  qst_format; (c) confirmation-dialog text tags (validate_tags). All three artifacts couple;
  map lane places the NPC after the record lands. Old boat-dialog failure predated B2 (quests
  now load); pilot walk-test proves it.
- ✅ **SHIPPED build31 (G3) + build36 (D16b)** - all 20 tiers: `skillName7` is now
  `shadowstalker_distortionfield.dbr` (the suicide shadowstrike is GONE), `characterLife` **500 ->
  2210** (was flat 297), hit **120-150 -> 386-492** (was flat 83-98); D16b added the AoE-petrify
  shadowzap. Design record follows.
  **D16 QUEUED (Will, verbatim: the swap skill 'is basically suicide... make him stronger,
  much stronger'): SHADOW STALKER OVERHAUL - EXPLICIT OCCULT-FREEZE EXCEPTION.** (1) find the
  Stalker's position-swap first ability (teleport-exchange into packs) in the Occult pet kit
  and REMOVE it from the PET kit (Will explicitly sanctioned; pet skill slot, not a player
  tree slot - the no-remove mastery law does not bind; substitute a better skill if one fits,
  report the choice); (2) substantially buff the pet ladder (life/damage/resists/speed, all
  tiers; benchmark = mastery-audit Part II, Stalker ~1440 HP reference; aggressive per Will);
  (3) validate_mastery_golden WILL fire: regenerate the golden baseline for EXACTLY the
  changed records/fields, commit documents the Will-ordered exception verbatim; gate keeps
  guarding all other Occult records. Pets spawn fresh per cast = retroactive for existing
  characters.
- ✅ **SHIPPED build31 (G3)** - all 20 `coredweller_NN` tiers at x1.75 life: t1 **1367.1**, t20
  **3937.5** (were 781 / 2250); strength t1 **293.8**, t20 **531.2**; taunt kit untouched, as ruled.
  Design record follows.
  **D17 QUEUED (Will: 'make the volcano guy much stronger in earth mastery'): CORE DWELLER.**
  The Earth magma golem (audit: 781/1940/2250 HP, STR 425, taunt+boulder+stonehand+wildfire).
  Buff substantially ON TOP of the Wave 1 Earth boosts: ~1.5-2x life, meaningful damage
  scaling, armor up, keep the taunt identity (Earth's ONLY pet vs Occult's 5-body package).
  Report before/after ladders. (Reading note: 'volcano guy' = the golem; if Will meant
  Volcanic Orb, the Wave 1 cd 4->1.5 boost already covers it - flagged in the report.)

### BUILD32 TRAIN (queued 2026-07-09; implement AFTER build31 ships)
> ⚠️ **EVERY ENTRY IN THIS TRAIN SHIPPED** (build31/31g/32/32a/36) - see the STATUS SWEEP table at
> the top of this section for the per-item arz proof. Kept verbatim as the design record.
- ✅ **SHIPPED build32 (Group F)** - 68 records incl. `svc_obsidianhoard_01/02/03`, `um_sarkoth_99`,
  `um_ilsevar_99`, `voranthys_soul_l` granting `summon_voranthys.dbr`. Design record follows.
  **N6-DB: Obsidian Halls treasure roulette - WILL SIGNED OFF (2026-07-09).** Full approved
  design + locked decisions: docs/OBSIDIAN_ROULETTE_DESIGN.md (chanceToRun 25.0/corner;
  Voranthys = the one summon-soul via _build_boss_summon on the SepulchralWyrm01 rig; all
  designer defaults incl. locked Boss-classification mega-chest, 5-elite warbands, no charm,
  Sarkoth soul = pcsafe typhon_meteorstorm 2/3/4). Scope per design section 6:
  _create_obsidian_roulette(db) = 4 guardians (derived natives, wild kits + ondeath skills all
  existence-verified), shared warband pool (spawnMin=Max=6, championChance=100, championMax=5),
  4 corner proxies w/ accessory tiers + no-cap limit clone [1..110], 3 svc_obsidianhoard chests
  (hpalace_chestlg01 mesh scale 1.4, goldGeneratorChance=100, guaranteed epic N /
  legendary-or-epic E/L) + 3 accessory pools + loot tables, 4 amgoz1-voice souls (66% Finger2;
  Ilsevar dream augments MUST use the xpack paths - the base-dream twins DANGLE), tags.
  NEW gates: accessory-chain-resolves + chest-lock-classification==Boss + ondeath resolution.
  In-game confirm item for Will's DEV pass: DropProjectileTelekinesis anim on the liche rig.
  MAP-REF-1 ordering: DB records land in the build32 arz BEFORE map lane M10 injects
  (4 INJECT_SPECS + shared v0e branch).
- ✅ **SHIPPED build32 (Group D)** - proven in the shipped arz: `drxforceofnature` cd 360 -> **180.0**,
  `drxoutsidersummons` cd 360 -> **120.0**, `drxdeathward` cd 300 -> **180.0**. Design record follows.
  **MASTERY WAVE 2** per docs/MASTERY_AUDIT_2026-07-09.md §3 Wave 2: Warfare (horn/standard
  uptime, armband path fix, optional warwind), Nature (force-of-nature 360->180, petBonus ML1-40
  ramp w/ overshoot check, defensiveConvert artifact zeroing, wolf FX hygiene), remaining Spirit
  (outsider 360->120 + TTL 60, deathward 300->180, bonepet xxx-spiritbreath re-enable +
  placeholder cleanup - skillName6 no-op = KEEP or EDIT, never remove, per the standing rule),
  remaining Dream (timefield dead-ref clear, phantasm uptime, psionic beam, mana-ladder
  extensions, phantomstrike self-slow = EDIT to zero/flip not remove, phantasm loot dangler),
  RuneMaster tunes (castability breakage may already be covered in build31 group 1 via the
  anim-table restoration - verify before re-implementing), Neidan tunes (mastery-bar stat-stick
  question = Will decision, splash modifier attachment = verify EE semantics first).
  ⚠️ Dream truncation note: §3 Wave 2 Dream items 2-6 numbers are reconstructed - pull the FULL
  Dream boosts block from Part III (the Dream lane's boosts array) for exact targets before
  writing. ⚠️ Golden-freeze expansion decision (doc §5): freeze the tuned trees AFTER each
  wave's QA, regenerating the snapshot in the same step.
- ✅ **SHIPPED build32 (DB) + build32a (map)** - `um_vashkarr_99`, `svc_vashkarr_{fodder,lance,warlock}`,
  `svc_vashkarr_summonhorde`, `q_vashkarr_lone` (proxy AND pool), `vashkarr_soul_{n,e,l}` (no summon,
  per Will's ruling); `VASHKARR_SPEC` LIVE @ random05a (24.00,1.00,31.70). Design record follows.
  **N4-DB: Forest of the Ancients cave boss - WILL SIGNED OFF w/ amendments (2026-07-09).**
  Full design = the FotA design agent's final report (coordinator-held). Placement: Random05A.lvl
  cave via ToTomb02 east of Chang'an; Majestic Chest at local (24.01,1.00,28.70) stays UNTOUCHED.
  Band/HP APPROVED: charLevel [38,56,71], HP [12000,16500,21000].
  WILL'S DECISIONS: identity = (B) `{^r}Vashkarr, Eldest of the Ancients`, ANCIENT DRAGONIAN
  warlord, mesh `Creatures\Monster\Dragonian\AncientDragonian01.msh`; derive the kit from the
  DRAGONIAN family for anim-safety (NOT the option-A djinn donor). Escort = FULL-STRENGTH
  dragonian lieutenants (pool spawnMax=3, championChance=100, championMax=2 - satisfies
  spawnMax-championMax>=1): Vashkarr + 2 serious dragonians ALWAYS. Minions ("he should also be
  able to spawn many minions very often") = frequent minion-summon on his kit: clone the
  yaoguai_summonshadowstalkers Skill_SpawnPetMonster pattern -> DRAGONIAN fodder, short cooldown,
  multiple per cast; exact numbers in the implementation sign-off. SOUL = NO SUMMON ("it can just
  be really good"): vashkarr_soul_{n,e,l} = dense aggressive STAT suite at the band, richer than
  the Narok/Vort suites, {^F} tag ('Soul of the Eldest' or similar), 66% drop via
  SVC_RELEASE_DROPS, validate_soul_augments green.
  RECON (build30.2 arz, verified on-disk): `AncientDragonian01.msh` SHIPS on 7 records
  (bm_deathlance_32/34/36 + bm_ravager_31/33/35/37, Common L31-37) = the anim-safety derivation
  base; variants AncientDragonianB01.msh (bs_warlock Champions L34/37/40), AncientDragonianC01.msh
  (br_frostscourge). ESCORT CANDIDATES at band: Champions bs_warlock_40 (ancient-B caster,
  visually kin), em_ravager_41 (flameguardmesh), savage_deathlance_39; dragonian Heroes
  um_mukashi_38 / um_bloodskinner_40 / um_wisang_43 / um_mountainblade_43 (CAVEAT: hero escorts
  each 66%-drop their own souls per kill and Mountainblade is already a summon-boss soul - decide
  if that double reward is intended; the visually-kin pick = bs_warlock + a deathlance/ravager-
  derived full-strength champion clone). CEILING NOTE: shipped dragonians top out at L43, so
  escorts + minions need charLevel [38,56,71] laddered clones for epic/legendary (the
  replicant_41 [41,58,71] pattern). MINION FODDER pick: bm_ravager / bm_deathlance derived (SAME
  ancient mesh = literally 'the Ancients'); proposed cadence for sign-off: burst 3 per cast,
  ~6 s cooldown, minion charLevel [38,56,71] (tune off the decoded donor - VERIFIED at
  records\skills\boss skills\yaoguai_summonshadowstalkers.dbr, plus a skills\skills\ alias).
  PROXY: q_vashkarr_lone (chanceToRun=100) staged in BOTH drxmap\proxy\ and drxmap\proxy\pools\
  per the verified q_bloodtoxeus_lone precedent; limit/difficulty donors ON DISK:
  records\proxies boss\herolimit_all.dbr (verified present); NOTE 'HeroDifficulty_01' does NOT
  exist as a record-name substring - on-disk difficulty donors are the difficulty_01..04
  families (records\proxies orient\, xpack\proxieshades\) + xpack bossdifficulty_01; pull the
  EXACT donor path from the design doc (donor-verbatim rule). Boss passives suite per design
  section 4 (boss_conversionimmunity, all_hpscaling, boss_scaling, globalproperties
  epic/legendary boss, monsterClassification=Boss). RENDER LAW on AncientDragonian01.msh + skin
  (EngineArcResolver). Records: um_vashkarr_99 (named path preferred) + proxy + pool + minion
  skill + soul + tags (validate_tags). MAP-SIDE DEPENDENCY: these records MUST land in the
  build31 arz BEFORE the map lane injects the placement (MAP-REF-1); the map lane adds the v0e
  routing case + INJECT_SPECS in its next wave. All gates + bucketed record-diff.
- ✅ **SHIPPED build31 (G3): D11 Rally** - `drxrallybuff.skillCooldownTime` 45 -> **30.0** in the
  shipped arz. (The coordinator's original brief was never committed to the repo; the implemented
  change is the record of what was done.)
- ✅ **SHIPPED build31 (G3): D12 Coastal Ichthian Myrmidon soul boost** - `coastalichthianmyrmidon_soul_l.characterLife` = **650.0** (life 250/450/650, OA 60/120/180, cold ladders).
- ✅ **SHIPPED (Text lane): D15 reward-potion name colors** - `tools/build_text_arc.TEXT_FIX_TAGS`
  carries all four `^M` overrides (`tagNewItem3`, `tagNewItem70`, `tagNewItem4`, `tagNewItem69`).
  Design record follows.
  **D15: reward-potion name colors** (Will: Fortitude + skill-point potions should be the same
  dark red as the experience potions). RECON COMPLETE - ready to implement, pure Text-side:
  the dark red is the leading **`^M` color code** in the tag VALUE (shipped Text.arc:
  `tagNewItem6=^MPotion of Experience`, shared by ALL 48 potionexp_NN records). The four
  uncolored tags, each used by EXACTLY ONE record (arz-wide reverse-scan done, zero sharing,
  so no recolor side effects): `tagNewItem3` = 'Lesser Potion of Fortitude' (potionattri_01),
  `tagNewItem70` = 'Potion of Fortitude' (potionattri_02), `tagNewItem4` = 'Lesser Potion of
  Learning' (potionskill_01), `tagNewItem69` = 'Potion of Learning' (potionskill_02).
  FIX: these are SV-upstream tags (SV Text_EN.arc via build_modstrings), so override through
  the sanctioned single-definition dict `TEXT_FIX_TAGS` in tools/build_text_arc.py (skipped
  during SV emission, duplicate-tag gate stays green): add the four keys with the same values
  prefixed `^M`. No arz change; itemText desc tags untouched; check_duplicate_tags +
  validate_tags must PASS; Text.arc ships coupled with the build31 arz push as always.
- ✅ **SHIPPED build31 (Group 4): D14** - `pygmalion_soul_l.itemSkillName` = `summon_pygmalion.dbr`
  (level 3), pets `pygmalion_1..3`. Design record follows.
  **D14: Phygmalian Replicator summon soul** (Will: "Phygmalian replicator soul should summon the
  soul" = the soul summons the Replicator). Records identified on the build30.2 arz (spelled
  PYGMALION in-data): monster `records\creature\monster\automatoi\um_pygmalion_41.dbr` (Hero,
  single tier, charLevel 41, tag tagNewHero262, mesh `Creatures\Monster\Automatoi\Automatoi01.msh`
  = base-game + texture `SVTextures/creatures/automatoi/pygmalion_body.tex` = SV arc; wears
  `defaultHeadPiece = ...\automatoi\pygmalion_headb.dbr` -> pet NEEDS _set_pet_equipment with
  that head piece per the F2 naked-pet law). Souls `...\soul\automatoi\pygmalion_soul_{n,e,l}.dbr`
  (tag tagSoulName583): augment swordtraining 3/4/5 + petBonusName petbonus_pygmalion_{n,e,l},
  NO itemSkillName proc -> the summon displaces nothing; KEEP augment + petBonus (petBonus buffs
  pets = direct synergy with the new summon).
  **SELF-REPLICATION - WILL'S RULING (2026-07-09, verbatim): "dont have the safe limits on the
  pygmalion replicator replicates make it crazy."** Faithful transplant of the monster's replicate
  kit; ADD NOTHING (no new petLimit, TTL, cooldown, or any artificial constraint). Both
  engineering checks RESOLVED from the decoded records (build30.2 arz):
  (1) NO RECURSION IN-DATA: `replicant_41.dbr`'s full kit is decoded (batter, shieldcharge +
  disruption, shieldsmash, lightning melee w/ slow, armor_passive, construct_resists,
  globalproperties) and it does NOT carry replicate (no skillName8, no buffSelfSkillName). The
  monster's faithful shape = ONE-GENERATION replication: copies do not copy. Ship exactly that.
  (2) ENGINE TOLERANCE MOOT: `replicate.dbr`'s OWN native fields already bound the population -
  petLimit = 3/4/5 (per skill level 1/2/3), skillCooldownTime = 9/8/7 s, petBurstSpawn = 1,
  skillManaCost = 75, skillMaxLevel = 3 (ladder 1/2/3 fits the F1 gate), NO
  spawnObjectsTimeToLive (replicants persist until killed). These are limits the MONSTER lives
  with = faithful = KEEP; nothing new is added per the ruling. No unbounded growth exists, no
  crash mechanism; nothing was silently limited.
  EXPECTED IN-GAME (sign-off numbers): the pet auto-casts Replicate every 9/8/7 s (same buffSelf
  wiring as the monster), building to the native cap of 3/4/5 PERMANENT replicants whose
  charLevel scales 41/58/71 with the skill level; each replicant is a full fighting construct.
  Legendary-tier screen state: the Pygmalion pet + 5 permanent L71 copies, all friendly
  (pet-side Skill_SpawnPet chain, Boneash precedent). `spawnObjects = replicant_41` with
  charLevel [41,58,71] = the ladder's power curve comes free from the skill itself.
  (`copy of replicate.dbr` = Skill_AktaiosMirage upstream junk; ignore.) Full D13 recipe +
  gates; the summon-skill ladder tiers map 1:1 onto replicate's existing 3 levels.
- ✅ **SHIPPED build31 (Group 4): D13** - `eaterofdays_soul_l.itemSkillName` = `summon_eaterofdays.dbr`
  (level 3), pets `eaterofdays_1..3`. Design record follows.
  **D13: Eater of Days summon soul** (Will: "The Eater of Days soul should let you summon him").
  Records identified on the build30.2 arz: monster
  `records\creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr` (Hero-classified, single tier
  L45, tag tagNewHero91, mesh `DRX\meshes\eaterofdaysmesh.msh`, texture
  `DRXTextures\creatures\sepulchralwyrm\sepulchralwyrm_eaterofdays.tex` - DRX arcs ship with the
  mod; render-chain gate must still verify mesh-internal shaders). Souls
  `...\soul\sepulchralwyrm\eaterofdays_soul_{n,e,l}.dbr` carry ONLY an augment
  (drxdeathchillaura 3/4/5), NO itemSkillName proc - the summon grant displaces nothing (keep
  the aura augment). Kit donor skill available: `eaterofdays_necrobolt` (attack_projectile).
  Standard D7/D8/D9 conversion: manual-cast Skill_SpawnPet ladder tiers 1/2/3, itemSkillLevel
  1/2/3 (F1 gate enforces <= skillMaxLevel), permanent pet via _build_boss_summon from the
  boss's OWN mesh/anim/skills, NO monster equipment/loot field copies (_set_pet_equipment
  hardcoded if armor is needed), 'Summon <full name>' tag + {^F} law + uber_soul_tags, gates:
  validate_summon_pets + render_chain + soul_augments + summons contract 0 P1 + bucketed
  record-diff.
- 🟡 **STILL OPEN (unchanged): Boss-summon-soul candidates remaining (for Will's batch approval)** -
  this is a PROPOSAL list, not a build queue; Will's standing ruling is that only EXPLICITLY named
  souls get converted.
  **Boss-summon-soul candidates remaining (for Will's batch approval):** regenerated ranked on
  the build30.2 arz via the real wiring join (lootFinger2Item1): 643 souls wired to monsters,
  61 already summon, 578 do not. Top Boss-class by level: dragonliche L63, manticore L56,
  darksatyrshaman L55, hades L54, bloodcrow + talos L50, antaeus L49, typhon + undeadtyphon +
  meglograi L48, palai + deeptresher L47, syrinx + polyphemus + wheedletongue + uber L45,
  ormenos + cerberus + maenadsorceress(no proc) L44, charon both forms L43, yaoguai L41,
  pemphredo + bandari L40, deino + enyo L39, gargantuanyeti L38, barmanu L37, scarabaeus +
  permean L35, sandwraithlord L34, aktaios L33, grimshell L33, nehebkau L30, sandwraith L29,
  megalesios L27, minotaurlord L26, medusa L24, alastor L24, euryale L23, sstheno + arachne L22,
  toxeus (Athens) L21, calybe L20, nessus L15; notable Hero-class: sp_toxeus L99 (the SP
  superboss), wardenofsouls L48, insenzia/torak/koios L47-48 (procless souls - clean adds).
  Regeneration script (re-runnable on any arz): session scratchpad `rank_summon_candidates.py`;
  full dump `summon_candidates_ranked.txt`.

- ✅ **SHIPPED build32 (Group E)** - this is the SAME work as N5, not a second item:
  `_restore_thrown_weapon_drops` restored 198/198 eligible base loot twins, and the 3 supra thrown
  weapons + their `svc_thrown_*_formula` records are in the shipped arz. Design record follows.
  **FEATURE (Will 2026-07-09): throwing weapons in the campaign.** The mod already requires
  Ragnarok (Runemaster mastery, XPack2 world levels), so throwing weapons are available engine-side;
  they never drop in Acts 1-4 because vanilla loot tables only place them in Act 5. Wire thrown
  weapons into the campaign loot tables (and consider a thrown-weapon soul or two). Will: "we dont
  even have the throwing objects in the game (although I wish we did)".
- ~~**DESCRIPTION CORRECTIONS for next metadata push (2026-07-09):** (1) known-issues still says the
  Uber Dungeon return is not wired ...; (2) requirements: state that MULTIPLAYER requires ALL
  expansions ... Also warn the Steam "get DLC" redirect lands in an empty cart.~~
  **✅ BOTH ALREADY SHIPPED - entry was STALE. Verified + closed 2026-07-28 (`fix/debt-docs`).**
  Commit `02ce3e5` ("Workshop description: MP requires all expansions (byte-verified: 288 XPack2 +
  258 XPack3 + 726 XPack4 levels indexed in the shipped world), empty-cart Steam bug warning, Uber
  return door now wired (stale known-issue), condense 07-08 entry for the 8000-char cap") applied
  both. Present in `docs/WORKSHOP_DESCRIPTION.bbcode` on main today: the requirements list carries
  the full MP all-DLC line INCLUDING the empty-cart warning, and the Uber Dungeon is described as
  HAVING a return door.
  **RESIDUALS FOUND AND FIXED IN THE SAME PASS** (description-as-code only - the metadata PUSH is
  still Will's/the orchestrator's step, NOT this lane's):
  - The return-route guidance (GoM/Secret Place shrine + Uber return door) was still sitting under
    the "Known issues / work in progress" heading even though it describes WORKING behaviour.
    Moved to the end of "Restored Soulvizier areas" as a "Getting back out" note.
  - Known-issue "Toxeus the Enslaver ... currently spawns far too often. A big reduction to his
    spawn rate is coming" is now WRONG on both halves. It is FIXED, and it was NOT fixed by a rate
    cut: Will's verbatim directive was "no we dont need the 4x rate cut on top" (R-18 STANDING:
    the weight-1/K=600 rarity is deliberate design), so b49 shipped a BREADTH cut instead
    (`_EN_SWEEP_FAMILIES = ('undead',)`, 1224 -> 273 pools), merged as `79478c2` into **build40**,
    which is the canonical build live on Workshop item 3759792705. Rewritten as a FIXED line that
    also stops promising a rate cut that will never happen.
  Char budget re-checked: 7,858 of Steam's 8,000 (142 headroom); BBCode tags balanced (5 list /
  7 h1 / 1 b, all closed).
  **DO NOT REMOVE on the next push:** the "rare crash deep in the Blood Cave" known-issue is STILL
  TRUE for the live Workshop build. Will confirmed the crash fixed IN-GAME on 2026-07-27, but that
  was the DEV map - per BL-b89-DEBT-2 the canonical `Levels_merged.arc` was deliberately NOT
  packaged or uploaded, so the LIVE item still carries the malformed containers. That line comes
  out only when the canonical map ships.
  **STILL TO AUDIT before the next push (not done here, no evidence gathered):** the remaining four
  known-issues - black mastery-page backgrounds, misplaced/missing mastery skill icons, damage
  numbers not displaying, language switching - each need a shipped-vs-live check of their own.

- Contract suite - **BUILT + committed** (`tools/contracts/`, branch `feat/contract-suite`). One
  unified 51-contract, 5-lane suite (souls/summons/resources/map/quests) that subsumes BOTH the
  planned entity + map contract suites; every contract has a negative test proving it fires. Run:
  `py tools/contracts/run_contracts.py --arz … --levels-arc local/Levels_merged.arc …` (full
  command in PLAYBOOK §12). Run it before every deploy; fail-loud (exit 1 on any non-whitelisted
  P0/P1). **Against the build29-in-flight artifacts it (correctly) FAILS with 108 P1** on real,
  unfixed defects - do NOT weaken the contracts; fix the records:
  - `SUMMON-PET-CLASSIFICATION` x17 (soulskills pets carrioncrow/peng/… have no
    monsterClassification) -> **B-SUMMON-1** (the DB wave owns this).
  - `MAP-REF-1` x68 (SV `all_sv\creature\npc\dyer\*` NPCs + a few `proxies greek\*` pools are placed
    in Greek/Egypt town levels but never compiled into the arz -> silently fail to spawn) ->
    dropped-SV content (#28 / `DROPPED_CONTENT_AUDIT.md`); restore the records OR, if the dyer
    feature is cut-by-design, list them in `whitelist_map.txt` + `CUT_CONTENT.md`.
  - `MONSTER-SKILLS-LOOT` x10 (drxmap blood-cave `bodies\ancestralwarrior*`/`body01` reference a
    missing `Melee_Poison09-12_10.dbr` skill) -> **NEW**; add the skill or clear the ref.
  - `SOUL-NAME-RESOLVES` x8 (satyrmagi/satyrspiritcaller/kyrashadowdancer souls carry placeholder
    name tags `tagSoul1`/`tagSoulName` that resolve nowhere) -> **B-TEXT-TAGS-1 class**, new souls.
  - `SOUL-AUGMENT-LEVEL` x4 (crowboar_soul_n/e `augmentSkillLevel1/2 == 0` = dead +0 augments) ->
    **B-SOUL-PROC-1 residual** (build29 fixed itemSkillLevel but not these augment levels).
  - `MONSTER-SPAWN-ELIGIBILITY` x1 (`bw_priest_houndmaster` pool: championChance=100/championMin=2/
    spawnMax=2 crowds out its named `c_disciple_39`) -> the Blood-Toxeus no-spawn class, **NEW**.
  Build29 progress the suite confirms vs the frozen build27 baseline: 338 -> 108 P1 (SOUL-PROC-
  ACTIVATION 219->0 = B-SOUL-PROC-1; SUMMON-PET-NAKED 6->0; C-RES-TAGDUP-1 5->0 = B-MASTERY-LABEL-1;
  B-TEXT-TAGS-1 Crimson-Verdict tags now resolve). B-TEMPLE-DOOR/B-PORTAL coverage is already in
  (MAP-DOOR-1, MAP-PORTAL-1/2/3).
- Occult/Hunting mastery UI recheck (#35) - **B-MASTERY-LABEL-1 FIXED + VERIFIED HELD (2026-07-14 vet).**
  Root cause (2026-07-08): the mastery SELECT screen showed 'Rogue' because modstrings.txt defined
  tagSkillName050 / tagMasteryBrief05 / tagMasteryTitle05 TWICE (SV's Rogue lines first; the engine
  keeps the FIRST) and tagMasteryDescription05 carried vanilla Rogue flavor. FIX SHIPPED in
  tools/build_text_arc.py: OCCULT_FIX_TAGS (single-definition block, keys skipped during per-file SV
  emission via _FIX_BLOCK_TAGS) sets tagMasteryBrief05='Occult' / tagMasteryTitle05 / tagSkillName050
  / tagMasteryDescription05, guarded by the fail-loud check_duplicate_tags gate. 2026-07-14 text
  dry-run RE-CONFIRMED: "Applied fix-block tags (11 Occult + 11 text)", "Duplicate-tag gate OK",
  tagMasteryBrief05='Occult' single-def, 0 sibling conflicts; gate_mastery_ui.py --text cross-check
  finds 0 SELECT-tag conflicts. ⚠️ **STILL FLAGGED FOR WILL:** the tagMasteryDescription05 Occult
  select-screen wording is a DRAFT explicitly marked "NEEDS WILL'S SIGN-OFF" (Occult is his hand-tuned
  mastery); it also differs from the tree-pane blurb tagOccultTitleDESC - reconcile the copy (audit sec 5).
  Other masteries unaffected (single definitions).
- Souls quality pass vs SV originals (#31).
- Toxeus encounter suite (#32): **SHIPPED build37** as registry module `tools/patches/toxeus_suite.py`
  (Parts A-D), gate-GREEN build37-40. (A) **~33%** single-spawn entrance ambush `q_bloodtoxeus_ambush` @
  drxFirstRoom (Will FINAL DESIGN 2026-07-14 retuned 15 -> 33; reuses `_BT_POOL` = 1 Toxeus + 2 blood-
  demon adds; map placement `B41_SPECS` item 5, on-mesh comp#1 Y=1.0) - the **ONLY** Blood-Toxeus chance
  in the entrance corridor; (B) per-player rant scroll on Blood Toxeus Misc4 @100% (`FixedItemLoot`
  `numSpawn='numberOfPlayers*1'`, AE-parse-safe item evaluator); (C) roaming "Endless Hunt" Hades-
  confined stalker (`um_toxeus_hunt_99`, ShadowStalker rig) + granted-MOVE soul; (D) fail-loud
  champion-count cap (<=1 Toxeus any party size). **6-player checklist DONE 2026-07-14 ->
  `docs/MULTIPLAYER_COMPAT.md` §M4**, incl. the Legendary-stalker feasibility VERDICT (roaming +
  strictly-Legendary-only pure-data-gate is NOT cleanly feasible -> shipped as the Hades-confined
  "effectively Legendary/endgame" approximation; a FIXED Hydra-pattern Legendary-only stalker is a
  clean Will OPTION - now APPROVED + QUEUED, see the next entry). **FINAL DESIGN (2026-07-14, Will:
  "retire the one we are adding and just update the 15% one to 33%"):** the never-wired ~50% parchment
  feature is RETIRED so the corridor has EXACTLY ONE Toxeus roll. The monolith no longer authors the
  derived parchment pool/proxy `demon_01_cluster_toxeus50` or its sibling `q_bloodtoxeus_lone_50`; the
  `_verify_toxeus_champion_cap` roster shrank 3 -> 2 (ambush `_BT_POOL` + deep-chest `egg_blooddragon`),
  gate still GREEN + still fail-loud (DB-replay verified: retired records ABSENT, only ambush
  `chanceToRun` changed 15 -> 33, egg/`_BT_POOL`/boss byte-identical; NEG tests fail on planted
  over-count + the pre-r2 double). NO MAP CHANGE this lane. **ROUND-2 (historical):** before the final
  design there were 3 Toxeus pools; the 2 M15 pools kept `proxyPoolEquation` (`proxypoolequation_02`)
  which floored `championMax=1` to 2 at 4-6P = a deep-chest double; `_apply_m15_toxeus_group_joins`
  neutralises the surviving `egg_blooddragon` pool. RESIDUALS (not blockers, no code owed): launch-gated
  live checks (ambush np>=2; scroll per-player Misc4 @np=2 else container fallback; Hunt co-op runaway;
  M1.5 np*np) under the restart-Steam law. **RANT-SCROLL creative-text VETO CLEARED** (Will 2026-07-14:
  "you are good to ship the rant scroll" - screed + scroll names ship as-is; only the Part C Endless
  Hunt name/desc remain under the standing amgoz1 sign-off). Parchment orphan RESOLVED (retired).
- **B-TOXEUS-STALKER-1 - Legendary-only Toxeus stalker (fixed placement, Hydra pattern) -
  IMPLEMENTED 2026-07-15 on `feat/lowlift-wave` (`tools/patches/toxeus_legendary_stalker.py` +
  `build_section_surgery.py` B65_TOXEUS_STALKER_SPECS; see `docs/reports/b65_lowlift_wave.md`
  item 3). Placed at Hades Palace `hadespalace_floor04_04.lvl` local(38,45); dry-run verified
  (DB spawn-eligibility gate + map injection into a copy, navmesh byte-identical); NOT yet built/
  deployed - rides the next integration build. Historical spec below.**
  Will greenlit a proper strictly-Legendary-only
  Toxeus stalker as a distinct FIXED encounter (verbatim: "lets add that to the backlog tho"). Ship it
  via the PROVEN base-game **Hydra pattern** (`docs/reports/el_boss_audit.md`): a Legendary-gated proxy
  whose pool has `pool1` EMPTY + `poolLegendary1 = <a single-member um_toxeus_hunt_99 pool>` so the
  stalker spawns **only on Legendary** - NOT the inert `limit_legendary_only` min-player-level artifact
  (difficultyLimitsFile scales level, it does NOT filter spawns; see M4.6). Recipe: clone
  `q_bloodtoxeus_lone` -> `q_toxeus_hunt_lone` (pool1 empty, poolLegendary1 = new single-member
  `um_toxeus_hunt_99` pool), place at ONE Hades/endgame spot (map INJECT_SPECS), register in
  `_MOD_AUTHORED_SPAWN_PROXIES`. Trades "roaming but anywhere" for "findable but fixed + truly
  Legendary-only". Held to the amgoz1 creative bar (name/lore). Coexists with the already-shipped
  roaming Endless Hunt (Part C). **NOT built** in the 2026-07-14 corridor lane. Owner: a future DB+map
  wave.
- Souls quality pass vs SV originals (#31) - **ROUND 1+2 FIXED on `feat/souls-quality`** (module
  `tools/patches/souls_quality.py`; all 5 roster tier inversions + svc_uber icons; roster-wide verify;
  see SOULS-QUALITY ROUND-1+2 record above + `docs/reports/souls_quality_fix.md`). Awaiting integration.
  Fixed: the 3 DEFICIENT svc_uber souls (crowboar/onyxspine/steamcrawler - Legendary weaker than Epic; L-tier
  augment/grant -> 3, now n/e/l=1/2/3) + the 54-family svc_uber e/l per-tier icon law (108 rings). Contracts +
  dry-run replay green; ships in a later integration build. RESIDUAL (Will decisions, not auto-applied): P2-a Tomb
  Guardian obtainability (reclassifying the Common um_tombguardian_26 to Hero is a pack-balance change), P2-c nymph
  icons (integrate `feat/b40-soul-icons` 9db3f5f), P3-a/b/c/d design+hygiene. P2-d Soulfeeder pet = AUDIT FALSE
  POSITIVE (pet already casts spiritbreath). No SV-drift/dead-augment/granted-skill defects existed to fix.
- Toxeus encounter suite: 10-25% canonical entrance spawn, rant scroll (MP per-player), Legendary
  stalker feasibility, 6-player checklist (#32).
- Comprehensive dropped-visuals restoration (#28).
- Cold Tombs (#36) - ON HOLD per Will.

## QUEUED FEATURE: NEW-HERO-PARNASSUS-HOUND (APPROVED by Will 2026-07-14, not yet scheduled)
Will (verbatim): "add a new uber hero to the back corner of the parnassus caves. he could be a
massive fire breathing dog one of the black hounds that breathe fire and he could have other
crazy skills too."
- **Identity:** a massive black hound of the fire-breathing hound family (use the base/SV black
  hound rig that already carries a breath attack as the donor; scale up per the Ephialtes/Mnemophage
  size precedent, watch ceiling clearance in the cave interior). Name/lore to the amgoz1 bar
  (amgoz1_design_voice.md): monster-identity-driven - a hound of Parnassus's depths, fire/ash
  themes; name flagged for Will veto.
- **Kit:** signature fire breath + 2-3 "crazy" donor-based skills at the amgoz1 bar (e.g. leaping
  pounce, ember howl/summon ash-pups, flame trail - designer picks proven-shape donors; boss_skill_fix
  discipline: skills must actually cast, donor-matched levels).
- **Placement:** the BACK CORNER (deepest dead-end) of the Parnassus Caves (Greece Act 1) -
  implementation surveys the level's 0x0b navmesh for the deepest on-mesh pocket with boss+adds
  clearance (survey_uberboss_spots.py), q_<boss>_lone single-spawn proxy (chance TBD by Will -
  default guaranteed like other placed ubers), landing-clearance + containment gates.
- **Rewards:** 3-tier soul ({^F} tags, per-tier icons, granted skill = his identity e.g. the fire
  breath); 3 region-tuned Majestic Chests per the b42 standard.
- **Standard lanes:** DB records via registry module; tags via manifest; INJECT_SPECS placement;
  full gate battery; Will fresh-char verify on DEV after ship.

## QUEUED FEATURE: NEW-RELIC-DIONYSUS-TRICKSTER (APPROVED by Will 2026-07-14, not yet scheduled)
Will (verbatim): "dionysus trickster archers should get a custom relic they drop like the magneta
turtle shell."
- **Pattern to follow (ground-truth it first):** the mod's magenta turtle shell custom relic -
  locate its records in the effective arz (relic/charm item class, shard vs complete mechanics,
  completion bonus table, {^F}/magenta name coloring, icon) and its DROP wiring (which monsters,
  which loot slot/table, what rate). Clone that exact shape - do not invent a new mechanism.
- **Identity:** a custom relic themed to the Dionysus trickster archers (wine/revelry/madness/
  trickery - e.g. intoxicating shot, maddening draught themes). Name + flavor + completion
  bonuses to the amgoz1 bar (amgoz1_design_voice.md); name flagged for Will veto.
- **Drop wiring:** dropped by the Dionysus trickster archer monster family (identify the exact
  records - the satyr trickster archers of the Dionysus cult area; wire ALL family variants/tiers
  N/E/L like the turtle-shell precedent, matching its rate).
- **Standard lanes:** DB records via registry module; tags via manifest ({^F} discipline);
  validate_tags + contracts green; dry-run replay intended-records-only; Will fresh-drop verify
  (TQ bakes item properties at pickup - test with a freshly dropped relic).

## QUEUED FEATURE: NEW-HERO-WARCAMP-SKELETON (APPROVED by Will 2026-07-14, not yet scheduled)
Will (verbatim): "add a new uber hero (new skeleton staged uber hero (kill him multiple times like
the legion monster) each time he respawns he gets bigger and stronger and new skills, give him 3
stages. this new uber hero will go in the back corner of the Upper War-Camp before Medusa."
- **Mechanism donor:** the Legion multi-stage death-transform chain - ground-truth it from
  docs/reports/b56_legion_soul_stages.md (the 2026-07-14 Legion lane mapped the exact stage-chain
  wiring) and clone that proven shape. THREE stages: each death spawns the next form.
- **Escalation per stage:** bigger (scale, mind interior ceiling-clip headroom per the
  Ephialtes/Mnemophage lesson), stronger (HP/damage stepped up), and NEW skills each stage
  (donor-based, proven-shape, boss_skill_fix discipline: must actually cast; stage 3 = the full
  crazy kit). Skeleton rig family; amgoz1-bar identity (a thrice-risen war-camp revenant class
  concept; name/lore flagged for Will veto).
- **SOUL LAW (hard):** soul drops ONLY on the FINAL (3rd) stage - must pass the
  legion_soul_stages verify gate (no chain with >1 soul-bearing stage). 3-tier soul, granted
  skill = his identity.
- **Placement:** the BACK CORNER of the Upper War-Camp (Greece, before Medusa/the Gorgons) -
  navmesh survey for the deepest on-mesh pocket with clearance for the LARGEST (stage 3) form,
  q_<boss>_lone single-spawn proxy, landing-clearance + containment gates; verify the stage
  respawns happen in place (the chain spawns at death location - confirm clearance holds).
- **Rewards:** 3-tier soul + 3 region-tuned Majestic Chests (b42 standard, Greece-tuned).
- **Standard lanes:** DB registry module; tags via manifest; INJECT_SPECS; full gate battery;
  Will fresh-char verify on DEV.

## B66 UBER FORMULA EXPANSION - round 2 FIXED+RE-VERIFIED (status: vet's HIGH/MEDIUM/3xLOW all resolved, awaiting Will's WILL-VETO review + DB build/deploy)
Round 1 of NEW-UBER-FORMULAS-FROM-ORPHANS: all 14 curated candidates below are BUILT (not
just designed) - `tools/patches/uber_orphan_weapons.py` (registry module) + donor data
`tools/patches/data/b66_orphan_donor_fields.json`. Full detail, per-weapon stat/reagent
tables, the WILL VETO naming section, the ROUND 2 CHANGELOG, and the Part-2 non-weapon gap
analysis (surprise finding: 16 non-weapon supra pieces across 7/8 equip slots ALREADY exist
and are ALREADY wired/obtainable; the one gap, Bracelet, has zero curatable orphans
anywhere in TQ and is SKIPPED per the efficiency law) are in
**`docs/reports/b66_uber_formulas.md`**.

Round 1 got an independent adversarial vet: NO-GO (one HIGH - Ten Suns' Wrath was ~2.3x its
bow sibling and the tier's single highest-damage weapon, contradicting the report's "none
exceed the strongest sibling" claim; one MEDIUM - donor combat stats weren't cleared before
the retune, so a grab-bag of orphan riders bled through uncontrolled; three LOW/nit - an
inaccurate "verbatim" donor-JSON claim, 2 swords a few % over the class band ceiling, a
hidePrefixName/hideSuffixName inconsistency on 2 weapons). **Round 2 fixes all 6**, re-runs
the same real dry-run harness against the same build41 baseline, and re-verifies clean:
- Ten Suns' Wrath retuned to tie (not exceed) its bow sibling (phys 145-160, was 340-390);
  measured tier-wide rank confirms it's no longer an outlier (sits at the bow/sword floor
  of 160, nowhere near the tier's actual top of 360).
- `_clear_inherited_combat_stats` added (mirrors the N5 template exactly) - wipes donor
  combat-stat bleed-through on all 14 before the retune; Aquimae/Furies' 2 riders that
  legitimately depended on an inherited `offensiveGlobalChance` now set it explicitly.
- Donor JSON's `dijunspride` entry restored to genuinely byte-verbatim; the sun-projectile
  retheme is now an explicit, documented override.
- Heartpierce/Ripulsar physical max trimmed to the documented 160 sword ceiling.
- Munderizer/Sword Fish `hidePrefixName`/`hideSuffixName` aligned to 1/1 (matches the other
  12 + every existing supra weapon).
- `verify()` hardened with 3 new regression guards (band cap, GlobalChance non-zero,
  hidePrefix/hideSuffix==1).
- **Verified (dry-run, no heavy build):** py_compile + `_check_registry.py` green (21
  modules, unchanged order hash); `patches.run_registry()` (real harness) over a fresh
  build41-baseline load (md5 confirmed `eb8bc377...`) -> still 21 new + 9 modified records
  (7 repointed zrecipes shells + both supra tables), 28 tags, zero collisions; `verify()`
  (real `run_registry_verifies` harness) green incl. the 3 new guards; direct field-probe
  confirms every flagged stray rider is now cleared while every intended stat is
  unaffected; resolves-in-arc (BUILT union BASE) green; supra dead-ref invariant green;
  container loot-shape gate green; negative test (missing clone donor) fails loud as
  expected.
- **NOT YET DONE:** a real DB build (`build_svc_database.py`) + Text.arc build + the full
  gate battery + Will's in-game fresh-drop verify (TQ bakes item props at pickup - test
  freshly crafted items) - deferred per "NO heavy builds" for this implementer round; next
  step for whoever picks this up.
- **Awaiting Will:** the WILL VETO section in the report (9 renamed twin-affected weapons +
  the Munderizer magenta-tag question) - ships as default if he doesn't object.
- **Deferred to round 3:** the 8-axe Greek bench, a fresh Spear/Shield uber, the supra
  Bracelet, diversifying the 5-way shared axe reagent trio.

## QUEUED FEATURE: NEW-UBER-FORMULAS-FROM-ORPHANS (status: approved-concept-by-Will-2026-07-14, awaiting his candidate selection)
Will (verbatim): "are there any cool orphaned weapon records that we could use to make new uber
weapons behind? some uber forge formula weapons. add this to the backlog." Full audit +
curated candidate detail + design sketch + reproduce steps: **`docs/reports/orphaned_weapons_curation.md`**.
- **Finding:** the effective DB holds 4,360 weapon records - 3,007 obtainable, **1,069 orphaned**
  (1,054 referenced by nothing; verified across 3 independent vectors), 284 junk. Plenty of "cool"
  orphans (proper name + distinctive art and/or granted skill + lore) to reskin into supra ubers.
- **Proven template (already in-repo):** SVC already added 3 thrown ubers this exact way -
  `svc_thrown_charonstoll/lastword/sanguineorbit` formulas -> `svc_wep_*` results, wired into BOTH
  `records\xpack\item\loottables\arcaneformulae\supra.dbr` + `supra_special.dbr`. Clone that path.
- **Per-candidate build (each pick):** buff/author the result at `records\drxitem\supra\svc_wep_<name>.dbr`
  (lvl-65 Legendary, `numRelicSlots=1`, supra-tier stats, identity-themed `itemSkillName` proc +
  `weaponTrail`; KEEP the orphan's mesh/skin/bitmap - add a bespoke DRX trail for shared-mesh picks,
  Blood Whisper style; picks already at L70-79 usable near as-is). Formula = new `zrecipes\svc_<class>_<name>_formula.dbr`
  OR **reuse one of the 24 orphaned `zrecipes\` duplicate formula shells** (repoint `artifactName` +
  reagents + `description`; the live `recipes\` twin still crafts the original). Recipe name to the
  amgoz1 bar (amgoz1_design_voice.md): **"Mythic Formula - <name>"**; reagents = **2 Legendary + 1 Rare
  thematically matched** to the weapon (per-candidate themes in the report). Add the formula to BOTH
  supra drop tables; add tags via manifest (validate_tags green; arz + Text.arc ship together).
- **Curated menu (14 + 8-axe bench; Will picks which to build - see report for pitches/paths/reagents):**
  Ripulsar & Aquimae (Sword, bespoke lost DRX blades, 0-twin); Helona (Staff, grants a summon);
  Hati (Thrown, Norse moon-wolf, bespoke, 0-twin); Sword Fish (Mace, the joke secret uber, 0-twin);
  Phoenix (Axe, has a live Heat Shield skill); Erysichthon's Hunger / The Furies (Axe, Greek lore);
  Scylla + Charybdis (paired sea-terror Axes); Heartpierce & Doom Herald (DRX cursed-egg Sword/Mace);
  The Munderizer (Staff, the Munderbunny insider egg, magenta name); Di Jun's Pride (Bow, solar,
  rename). Bench: 8 more Greek Legendary axes (Acheron's Touch, Axe of Tereus, Persephone's Caress,
  Torment, Shai'tan, Atropos' Assistant, Enkidu's Stand, Theogenes' Onslaught).
- **Honest gaps:** NO quality orphan Spear (Blood Whisper already the supra spear) or Shield - a new
  spear/shield uber must be authored fresh, not sourced from an orphan.
- **Twin caveat:** shared-mesh Greek axes + the DRX eggs have a live name-twin (droppable item of the
  same name) - the orphan RECORD is still unreferenced/safe, but rename the uber (or frame it as an
  "ascended" variant) and give it distinctive art. 0-twin picks (Ripulsar, Aquimae, Hati, Sword Fish,
  Munderizer) have a fully free identity.
- **Standard lanes:** DB records via registry module; tags via manifest ({^F}/{^r} discipline);
  dry-run replay intended-records-only vs baseline; validate_tags + supra dead-ref invariant green;
  Will fresh-drop verify on DEV (TQ bakes item props at pickup - test a freshly crafted item).

## ✅ SOUL-EMBERTEETH-SUMMON - BUILT b91 (2026-07-28, branch `fix/debt-db`)
Will (verbatim): "emberteeth soul should let you summon him."

**SHIPPED** in `tools/patches/emberteeth_summon.py`. Ground truth confirmed the feature was
genuinely unbuilt: `emberteeth_soul_{n,e,l}` (tag `tagSoulName331`, itemLevel 18/42/59) granted
**no skill at all** - a pure fire-stat ring. Source `records\creature\monster\orthrus\
um_emberteeth.dbr` = `Hero`, `charLevel [18,43,58]` (the lowest-level summon source in the
roster), race `Demon`, skin `brimstoneorthus01.tex`, soul drop 50% (RANDOM roamer, untouched).

What shipped: 3 permanent pets `...\soulskills\pets\emberteeth_{1,2,3}.dbr` + manual-cast button
`...\soulskills\summon_emberteeth.dbr`, built through the shared `_build_boss_summon` pipeline so
the pet IS Emberteeth (his own mesh/anim table/attack skill/attribute cadence/skill kit; race +
orthrus vox/alert/death/stun paks via the b81 `_align_pet_identity` law, R-11; gear mirrored
through the sanctioned `_set_pet_equipment` loot-table path, never Monster.tpl copies; D19
pet-mobility assert; permanent, no TTL). All 3 soul tiers wired at `itemSkillLevel` 1/2/3 so the
epic soul spawns the epic-tier pet (R-43 companion check), with any inherited
`itemSkillAutoController` stripped (pet BUTTON, never an on-attack proc - D21 / R-44).
**Every pre-existing fire benefit kept** - `apply()` snapshots 16 fields per tier and fails loud
if any moved. Soul name deliberately NOT renamed (a summon was asked for, not a rename).

Life band `[2400, 6000, 9500]` is **derived, not invented**: the shipped player-facing boss-summon
pets split into an uber cluster (~250-296 life/charLevel) and a lesser cluster (~119-167); a
mid-tier `tagNewHero` Hero takes the lesser one. Icon = `DRXtextures\skill icons\soul\
summonchimera{up,down}.tex` (fire-breathing multi-headed beast = closest on-identity glyph for a
two-headed brimstone orthrus), arc-verified present and verified UNCLAIMED by any other summon
(`apply()` fails loud on a collision - the b85 bwpriest lesson). Pet-bar portrait = neutral
summon-proxy (no `chimera_party_*` art ships) - never the Lyia nymph; a bespoke portrait is
registered as debt BL-b91-DEBT-2. Report: `docs/reports/b91_debt_db.md` sec 3.

**ORIGINAL SPEC (kept for the record):**
- **Ground-truth first:** locate Emberteeth (monster record + soul item family, all tiers) in the
  effective arz and document what the soul CURRENTLY grants (non-summon skill? augments only?) -
  then convert/extend so the soul summons Emberteeth himself.
- **Summon pattern:** clone a proven working summon-soul shape (post-crowboar-controller-fix
  references; Lyia Leafsong for permanence semantics). Pet = Emberteeth's own rig/kit scaled to
  pet balance, tiered N/E/L like other summon souls. HARD SAFETY LAWS: never copy Monster.tpl
  equipment/loot fields onto Pet.tpl (crash); animation/skill/FX fields only;
  spawnObjectsTimeToLive [] only if permanence is the design; no explicit dtype on set_field;
  bare _ensure_record for soul items, never clone_record.
- **Keep existing value:** if the soul currently grants useful augments/stats, ADD the summon
  alongside (the standard augments+summon stack) - do not strip visible benefits silently.
- **Standard lanes:** registry module; {^F} tag manifest; soul contracts + validate_summon_pets
  green; dry-run replay intended-records-only; Will fresh-drop verify (TQ bakes item properties
  at pickup - test with a freshly dropped soul).

## QUEUED FEATURES BATCH 2026-07-14b (ALL APPROVED by Will, not yet scheduled)
All follow the standard uber-hero lanes (amgoz1-bar identity + name for Will veto; donor-based
proven-shape kits that actually cast; navmesh survey + q_<boss>_lone single-spawn + landing/
containment gates; 3-tier {^F} soul + 3 region-tuned Majestic Chests; exclamation-point map
marker per the b63 mechanism; registry module + tag manifest + full gate battery):
1. **NEW-HERO-LOOKOUT-CAVE** - uber monster at the BACK of Lookout Cave (Egypt). Identity open
   (fit the cave's native population; designer proposes).
2. **NEW-HERO-HATHOR-CROC** - crocodile-man uber hero at the VERY END of the Hathor Basin cave
   (the back chest room with all the chests). Croc-man rig family; guard-of-the-hoard concept.
3. **NEW-HERO-NILE-SCORPION** (Will 2026-07-16: replaced the second crocodile - 'choose something
   we dont have an uber hero for yet') - an uber SCORPION (scorpos family, no uber scorpion exists
   in the roster; Egypt-native rig) in the Nile Floodplain at the spot where the 'Plight of the
   Nile Farmers' side quest completes (quest-collision safety per the Kroisos/King-Dorus lesson:
   NEAR the quest spot, never colliding with quest actors/kill credits). Alternates if the scorpos
   rig disappoints: giant scarab, plague swarm host.
4. **NEW-BOSS-BEGGARS-QUARTER-DEMON** - uber DEMON boss in the Beggars Quarter (ground-truth the
   exact level; demon identity to the amgoz1 bar).
5. **NEW-RELIC-DUNE-FIEND** - Dune Fiend monsters drop a unique relic IF THEY DON'T ALREADY
   (ground-truth first; if none, clone the magenta-turtle-shell pattern exactly like
   NEW-RELIC-DIONYSUS-TRICKSTER; desert/sand-terror identity).
6. **NEW-BOSS-ROAMING-GHOST** - an undead GHOST uber boss that can spawn ANYWHERE (roaming =
   the Endless Hunt trash-pool-sweep pattern with per-slot limit=1 + fail-loud verify, NOT
   unvetted proxy equations; rarity tuned like the Hunt's 1/2400 class; all-difficulty or
   tiered - designer proposes, Will vetoes).


## BUILD41 GATE RECORD (2026-07-14, integration/build41)
Contents: Aniketos E/L restore (map), Legion final-stage-only soul, Enslaver+HadesMarshal pet
black-rig (9 pets), ambush 33% + parchment retire, rant scroll (dial A), souls-quality wave
(5 tier inversions ratified, 106+ per-tier icons, crow manual-cast x8 families/24 rings,
Tomb Guardian de-souled Common), b40 nymph soul icons. md5s: arz eb8bc377 / Text e74672fd /
Quests 37cf867f (UNCHANGED from b40) / CANON Levels 3f05c227 / TESTHUB Levels 6490ddce.
Gates: registry 16 modules + all verify hooks OK; record-diff vs b40 = 162 modified + 6 removed
(intended-only); validate_tags PASS; navmesh verify PASS; contracts GATE PASS (0 P0/0 P1/4910 P2
pre-existing). Deployed DEV (TESTHUB). NOT pushed to Steam (Will's word required).

## APPROACH CHANGE: THROWN-WIELDERS (Will 2026-07-14, supersedes B58 invented families)
Will verbatim: "instead of us inventing guys who use thrown weapons, we should just restore the
ones that are in the expansions and then scale up them to match SV difficulty. We can hold this
in our backlog, but this is the approach we should take."
-> feat/thrown-enemies (3 invented families) SHELVED - do not register/ship.
-> QUEUED: THROWN-WIELDERS-RESTORE: port the 74 DLC thrown-wielders (b58 audit: xpack2/3/4
rosters, rigs already throw-proven) - curate identity-fit subset into campaign spawn pools,
re-tier charLevel/stats to SV-difficulty bands per act, drops banded per b58 findings.


## BUILD42 GATE RECORD (2026-07-16, integration/build42)
Contents: drop-rate 50% for 377 random-spawn heroes (last-writer gate), 72 auras widened (Shadow
Link 3->36), full 9-mastery reflow (tier+connector laws, 17 waivers), mastery pane render fix
(BitmapUIAware, 28 sanctioned golden overrides), travelers v3 (enter-offers into SV areas +
return-to-origin primary/Helos secondary; crypt unsealed), 10 thrown-wielders restored (SV-scaled),
5 SVAERA sets re-linked, Dionysus+DuneFiend relics, Legendary-only Toxeus stalker placed,
double-soul rulings (boar merge/lillued retire), 14 orphan-weapon uber formulas (7 shell reuses).
md5s: arz f8ef904d / Text 3e576581 / Quests 5e664c7b / CANON Levels 62868eec / TESTHUB 0c10343b.
Gates: A7 golden PASS (83 waived) / mastery-UI gate PASS (17 waived) / drop-rate last-writer gate
PASS / validate_tags PASS / navmesh PASS / contracts GATE PASS (0 P0/0 P1/4909 P2). Record-diff
vs build41: ~565 mod +37 add -6 rm, intended-only classes. Deterministic rebuild proof (arz
byte-identical across the two build42 DB runs). Deployed DEV. NOT pushed to Steam (Will's word).
OPEN WILL Qs: legion terminal 66-vs-50, Munderizer over-band, Shadow Link malus veto,
murderbossroom return NPC (map lane).


## WILL RULINGS 2026-07-16 (post-build42)
- LEGION TERMINAL @66: fine for now. QUEUED: fold 'death-transform terminals of RANDOM chains
  inherit the 50 rate' into the NEXT SOULS PASS (with the 155 documented minor gaps + 79
  drop-gated souls + crowboar summon controller polish).
- MUNDERIZER: over-band 350 life damage BLESSED as intentional (joke item, forgoes utility);
  keep; extend the verify() band-cap carve-out note.
- SHADOW LINK: large radius (36) KEPT incl. the malus spread; Will-approved final.


## COLD WORM BUFFS (Will 2026-07-16) - ✅ FULLY SHIPPED b91 (all 6 sub-items)
Cold Worm needs ~3x characterLife and +20% armor (defensiveProtection) ON TOP of the already-queued
kit (burrow/frost skills that actually cast), massive total-speed boost, exclamation-marker
mechanism -> all placed ubers, and the 3-tier soul + loot-triple fix + roster drop-slot sweep.
All Cold Worm items ship as ONE lane when resumed (worktree coldworm-markers has partials).

> **b91 (2026-07-28, branch `fix/debt-mixed`): 5 of 6 sub-items DONE + build-verified; the
> exclamation marker is BLOCKED and is NOT claimed (BL-b91-DEBT-1). R-39 = PARTIAL.**
> CORRECTION to this section's premise: the `coldworm-markers` worktree had **NO partials** -
> `feat/coldworm-uber-markers` @ `75110bd` is an ANCESTOR of `main` (0 ahead, clean tree, empty
> `main...` diff). The lane was abandoned before anything landed; b91 was built from ground truth.
> Owner: `tools/patches/coldworm_buffs.py` (registry module, apply+verify, after `boss_skill_fix`,
> before `visuals`). RCA: the ENTIRE kit referenced `boss skills\d2custom\coldworm_*` +
> `Game\D2*`, absent from the mod arz AND upstream SV 098i AND the base game - **8/8 active slots
> dead, the worst record in the DB**; so Cold Worm cast nothing, had no difficulty globals and was
> player-convertible. Fixed at the record layer with EXISTING donors at their own levels. "+20%
> armor (defensiveProtection)" applied as `armor_passive` level `[60,174,360] -> [72,209,432]`,
> because the raw field is inert on monsters (0 non-zero carriers DB-wide) and the passive's
> `defensiveProtection` array is exactly linear. Ships its own gate (active slots must be CASTABLE:
> resolve + `skillSpecialAnimationName` bound by an `unarmedSpecialAnimRef`) + planted negative test
> (`py tools/patches/coldworm_buffs.py --negtest` PASS) + `tools/sweep_soul_drop_slots.py`. The
> 3-tier soul + loot triple were ALREADY correct: asserted in verify(), not rewritten. Record-diff
> = **exactly 1 record / 70 intended-class fields**; arz md5 `461c54f95480f6c331f25ce7ab64c6f4`.
> NOT deployed, NOT packaged, NOT pushed to Steam. Open: BL-b91-DEBT-1..5. Report:
> `docs/reports/b91_coldworm_buffs.md`.

> **b91 ROUND 2 (2026-07-28, same branch): THE 6th SUB-ITEM SHIPPED. R-39 = IMPLEMENTED, and the
> round-1 "BLOCKED" verdict on the marker was itself WRONG.** The exclamation marker is NOT map-side:
> it is the DB-side Monster field **`DisplayAsQuestItem`** (present on all 4,601 Monster records,
> set to 1 on 124 - every base-game quest boss, every `xsq` named quest hero, the escort NPCs, the
> quest chests/doors/objects, and the whole `records\poi\**` AreaOfInterest map-marker namespace),
> and it was **already live in this mod on Cold Worm himself** (`records\test\boss_coldworm50.dbr`
> = 1 on `main`) - which is exactly the marker Will saw when he asked to "extend" it. Round 1
> scanned only `miniMapEntity` and generalised from that one field's absence. No `Levels.arc`
> build, no `SVC_SVAERA_ARC`/`SVC_SV_ARC`, zero map bytes. (Round 1's other blocker - "there is no
> b63 mechanism in this repo" - is TRUE and stands: it had to be found from ground truth.)
> Owner: `tools/patches/uber_quest_markers.py` (registry module, apply+verify, after
> `coldworm_buffs`, before `visuals`). Roster DERIVED, never hardcoded:
> `soul_spawn_provenance_sets()`'s `placed_members` (the same source of truth as the PLACED_UBER
> 66% soul rate, R-42), narrowed by RULE A (it, or a form in its `actorToSpawnOnDeath` chain,
> actually pays a soul out - excludes the boss RETINUE mechanically) and widened by RULE B (mark
> every DEDICATED chain form, i.e. one whose spawners are ALL in the roster). Both rules are
> derived from shipped content: the ONE placed uber already marked on `main` is `um_polisgaoler_99`
> AND its dedicated `um_polisgaoler_unbound_99` - literally rule A + rule B. Rule B's exclusivity
> test is load-bearing: `as_ghosthero_32` is Neferkha's terminal form AND five ROAMING mummy
> heroes', so a naive whole-chain walk would spam markers across the map.
> **Roster = 25 records (21 encounters + 4 dedicated forms), 23 newly marked; 26 retinue/adds
> excluded** - and every excluded record is rank=Champion while every kept one is Boss/Hero (two
> independent signals, same cut). Ships its own gate + a 4-plant negative test
> (`py tools/patches/uber_quest_markers.py --negtest` PASS). ONE field, 0 new records, 0 tags,
> 0 map bytes. Still NOT deployed, NOT packaged, NOT pushed to Steam. Launch-gated residual folded
> into BL-b91-DEBT-4 (nobody has SEEN the marker in-game; Will judges marker density).
> Report: `docs/reports/b91_coldworm_buffs.md` sec 9 (sec 7 kept, marked SUPERSEDED).

## b68 MASTERY REFLOW REVERT (Will 2026-07-16, build43 playtest)
Will played build43 and reported the build42 mastery reflow introduced huge skill-tree errors
(skills wrong rows/columns, wrong connections, circle/square frame flips). Directive: REVERT the
reflow. Surgically reverted `tools/patches/hunting_occult_ui.py` + the `occult_hunting_golden.json`
body to build41 (Will's hand-tuned state); deleted `mastery_ui_vet.py` / `gate_mastery_ui.py` /
`mastery_ui_waivers.json` + the mastery-UI-law gate wiring in `build_svc_database.py`; KEPT the two
Will-mandated waves that shipped on top (b60 `mastery_bg_render` pane-render fix, b67 `oh_pane_art`
pane-art fix) + every unrelated build42-59 content change. A7 golden-freeze gate-driven override
reconstruction: re-added the 28 b60/b67-sanctioned keys + 3 BL-AURA-RADIUS (b57) keys a blanket
build41 golden.json revert had collaterally wiped (unrelated feature, still active - see
docs/reports/b68_mastery_reflow_revert.md). arz md5 `439a9279a7c5cf94b02074fd00981dd2` (scratch
build); Text.arc byte-identical to build43 (`3e576581`). Proof diffs: vs build43 = 56 modified
records, 100% UI position/connector fields, 0 non-UI deltas; vs build41 = 41 add/6 rm/509 mod, the
21 `ingameui` deltas 100% accounted for by the 2 kept waves, the rest the known build42-59 content
wave (drop rates, souls quality, legion stages, thrown restore, aura radii, uber orphan weapons,
turtleshell relics, SVAERA sets, double-soul rulings) - zero surprise records either diff.
Contracts GATE PASS (0 P0/0 P1/4903 P2 pre-existing). PERSISTING (not reflow damage, Will's own
2026-07-12 SHAPE LAW, unchanged by this revert): Poisonous Gas (`drxpoisongasbomb`) stays SQUARE,
Blade Fury (`drxcalculatedstrike_luckyhit`) stays CIRCLE - if Will's build43 complaint names either
of those two specifically, that's pre-existing intentional shape-law behavior, not a bug. NOT yet
built to canonical map/Text.arc pair or deployed - DB-lane-only revert; full deploy needs the map
lane's own text/quests build to be re-run against this arz before shipping.

## BUILD44 GATE RECORD (2026-07-16, DEV-only; Steam HELD for Will's word)
Contents: the b68 mastery-reflow revert ONLY (merge `2408d9a` of fix/mastery-reflow-revert
`1b2676e`; all 9 trees back to build41 layout; b60/b67 pane fixes kept) + the b69 SV ground-truth
docs commit (`f16f4c5`, docs/tools data only, no build effect). Artifacts: arz
`439a9279a7c5cf94b02074fd00981dd2` (canonical work/ build reproduced the revert-lane scratch build
byte-identical = determinism proof, so the Opus vet's proof-diffs carry over); Text.arc UNCHANGED
from build43 (`3e576581`, validate_tags PASS vs the new arz); Levels (canonical `62868eec` /
TESTHUB variant) + Quests (`5e664c7b`) UNCHANGED from build43, not redeployed. Gates: A7 golden
freeze PASS (66 waived: build41's 35 + the 28 b60 + b67/aura keys the revert reconstructed),
summon validator PASS (0 strict), 16 module verifies OK, registry selfcheck 25 modules
(mastery_ui_vet removed), contracts GATE PASS 0 P0 / 0 P1 / 4909 P2 (pre-existing count,
no new). DEV deploy hash-verified: SoulvizierClassicDEV.arz == `439a9279` (TQ not running).
Known-persisting after revert (pre-b42 shape-law, queued for build45 vs SV ground truth +
Will rulings): Poisonous Gas square (should be circle), Blade Fury circle (should be square),
Smoke Screen shape, Eviscerate -> SQUARE (Will ruling 2026-07-16), emblem-circle black hole x9
(masterybitmap.dbr BitmapSingle->BitmapUIAware conversion), Earth Soften Metal row, Occult
pre-0.98i family placement (Darklings/Dark Aperture/Toxic Concoction/Shadow Stalker - Will
correction: sourced from SV 0.9/0.41, NOT hand-authored; extraction lane in flight).

## B71 - ENSLAVER CHAIN (Will P1 REPEAT "oscillating", 2026-07-16) - FIX_STAGED (branch fix/enslaver-chain)
RCA `docs/reports/b71_enslaver_chain_rca.md`. Ground truth build44 `439a9279`.
**RCA verdict:** the whole Enslaver chain (soul->skill->pets->marauders + Hades Marshal)
is BYTE-IDENTICAL build41(b55 GO)->build44; roster-wide chain diff = 0 icon changes /
0 spawnObjects changes. The feared "build42 regression" is REFUTED. Will's 3 symptoms are
longstanding state: (#2) b40's deliberate `stalkerup` skill icon; (#3) the Lyia
`StatusIcon` pet-bar residue b40 explicitly deferred; (#1 green) NOT reproducible from any
current DB field (the b55-fixed Enslaver/marauder pets carry zero green markers and are
field-identical to the confirmed-BLACK encounter monster; charcoal skin resolves; the
proven green source `envenomweapon` is absent). The prior gates missed it because b55's
verify asserted pet FX FIELDS in isolation (record-level), never the live chain.
**FIX (upstream, `apply_svc_patches._build_boss_summon`):** enslaver skill icon
stalker->`deathwalkersummonup`; NEW `_SUMMON_PET_PORTRAIT` map + `_set_summon_pet_portrait`
overwrites the Lyia pet-bar portrait on ALL 17 player-facing boss summons (enslaver ->
`deathwalker_party` = one skeleton identity across button+pet-bar; 6 more on-identity;
10 neutral `proxy_party`). Pet-of-pet marauders/wyrmlings untouched (`player_facing=False`,
Will 2026-07-16: they never display). Hades Marshal portrait Lyia->proxy (no hades party
portrait ships).
**CHAIN GATE (anti-oscillation):** `enslaver_pet_fx.verify()` extended with `_verify_chain`
walking soul->skill->icon->pets->portrait->green->marauder on the FINAL arz; 5 negatives
proven to fail (incl. re-pointed skill + Lyia portrait + green marauder).
**Verified:** full build EXIT 0, registry+chain-gate green, A7 golden intact (66 waived);
record-diff intended-only 52 records (51 portraits + 1 icon, 0 marauder/wyrmling collateral);
contracts GATE PASS 0 P0/P1; validate_tags PASS; idempotent (arz `f0a58c1c` x2).
**WILL-CONFIRM after restart:** (a) DISMISS + RE-SUMMON the Enslaver from the soul - if
still green, residue is asset/save-level (pfx or already-summoned permanent pet), chased
next round; (b) 10 bosses on neutral proxy portrait could get bespoke portraits (future
art); (c) the ~77-pet systemic Lyia green (24 families) remains b55's flagged design call.
NOT deployed/committed to main.
## B80 - FORMULA NAME AUDIT round 1 (Will 2026-07-16, R-41) - FIX_STAGED (branch fix/formula-names)

Report `docs/reports/b80_formula_names.md`. Will: "Mythic Formula - Crystalline Mask is
the formula name for the formula which makes Galefury. the Mythic Formula has the wrong
name." **Root cause:** `records\drxitem\supra\recipes\ar_hunter_helm_formula.dbr`
(crafts Galefury) had `description=tagRecipe_ar_caster_helm` - the tag the REAL
Crystalline Mask formula pair (`recipes\`+`zrecipes\ar_caster_helm_formula.dbr`)
legitimately uses. Inherited SV098i/DRX authoring debt, NOT a b66 defect (b66 never
touches this record; Galefury predates b66's 14 weapons). SV 0.98i's own `Text_EN.arc`
already ships the fix, unused: `tagRecipe_ar_helm_fix=^rMythic Formula - Galefury`
(orphaned, zero references anywhere before this fix). **Fix:** repoint the field to
that tag - zero Text-pipeline change, the shared donor tag left untouched (still
correctly used by the 2 real Crystalline Mask formulas).
**SWEEP:** all 245 `ItemArtifactFormula` records (42 obtainable + 203 orphaned shells)
checked name-text-vs-result; exactly this ONE mismatch found, wired or unwired. Two
self-consistent naming sub-conventions confirmed empirically (original 25 `^rMythic
Formula - <Name>` vs b66's 14 `zrecipes\` formulas' unprefixed `Mythic|Arcane Formula -
<Name>`) - convention check compares name TEXT only, not color/prefix style, to avoid
false positives. WILL-CONFIRM list: empty (the one mismatch was unambiguously a bug).
**GATE (new, permanent):** `tools/patches/formula_names.py` verify() - supra-scoped
structural check (no Text.arc dependency): any `records\drxitem\supra\*` formula
`description` tag shared by 2+ formulas crafting DIFFERENT results fails the build
loud. PLUS a standalone text-resolved sweep `tools/validate_formula_names.py` (matches
`validate_tags.py`'s pattern), wired into `bootstrap_working_mod.ps1` right after the
tag-validation step. Both negative-tested (planted mismatch + the real pre-fix bug)
via `tools/debug/negtest_formula_names.py` (4/4 subtests correct).
**Verified:** full scratch build EXIT 0 (arz `9e3c1ad0`); record-diff vs reference
`917d9047` = exactly 1 record / 1 field (`description` repoint), 0 added/removed/other;
`validate_tags.py` PASS; new `validate_formula_names.py` PASS (40 checked, 0
mismatches); A7 golden PASS at both DB+Text stages (84/90 waived, all pre-existing);
chain gate + every other registry verify() green; idempotent (proven). Contracts
(souls/summons/resources) run twice (reference arz vs fixed arz, identical staged
Text/Levels/Quests/Resources) - **byte-identical violation set both times** (4904;
0 P0/1252 P1/3652 P2), proving zero regression from this change. Map/quests contracts
not re-run (this branch touches zero map/quest files). NOT deployed/committed to main.

~~**BACKLOG DEBT (new, per WILL_RULINGS law #4):** the 1252 P1 above does not match the
0 P1 the B71/BUILD45 gate records above claim for a similar reference-arz snapshot.
Likely `work/SoulvizierClassic/Resources/{Text.arc,Levels.arc}` staleness (mtimes
01:59/09:09 Jul-16 vs the reference arz's 19:47 Jul-16 - hours of other waves may have
landed on the arz without a matching Resources restage). Not caused by, and unaffected
by, this branch (proven via the identical-before/after diff). Flagged for whichever
lane owns the next full integration: fresh bootstrap + restage + re-run
`run_contracts.py` to re-establish ground truth.~~
**✅ CLOSED 2026-07-28 - DUPLICATE of BL-b90-DEBT-1 (same 1252 P1, filed twice
independently). MERGED INTO BL-b90-DEBT-1 in the DEBT REGISTER; read it there.**
The staleness hypothesis above is **REFUTED**: `C-RES-DBR-1` resolves against the arz +
base arz only and never reads a staged Resources arc. The real cause was the missing
`upstream/soulvizier_098i/Database/database.arz`, which made `make_provenance` silently
reclassify every SV-inherited dangling ref from `sv`/P2 to `authored`/P1. Fixed upstream
(`'unknown'` -> P2 + the new fail-loud `C-RES-INPUT-1`); reproduced both directions on one
arz (upstream present 0 P1, absent 1252 P1, identical violation set).
## BUILD45 MASTERY SV-ALIGNMENT (b70, 2026-07-16, feat/mastery-sv-fix - status: implemented+self-verified, awaiting independent vet)

Fixes the residual Occult/Hunting mastery-tree defects Will enumerated from his build43 screenshot
plus everything the two SV ground-truth extractions prove wrong vs Soulvizier. ONE new registry
module `tools/patches/mastery_sv_alignment.py` (apply+verify), registered LAST content module (before
`visuals`) = ratified last writer on every Occult(m5)/Hunting(m6)/emblem UI field; the 4 shape flips
also fixed UPSTREAM in `hunting_occult_ui.py` (BL-103). Report: `docs/reports/b70_mastery_sv_alignment.md`.

FIXES (all UI fields, zero gameplay/stat delta): **A** shapes - Poisonous Gas SQUARE->CIRCLE, Blade
Fury CIRCLE->SQUARE, Smoke Screen CIRCLE->SQUARE (m5), Eviscerate CIRCLE->SQUARE (m6, Will ruling
2026-07-16); these REVERT to the golden baseline (SV098-correct) so zero net golden drift. **B**
emblem-circle x9: `masterybitmap.dbr` BitmapSingle->BitmapUIAware (bitmapNames=[tex,tex], pos
[718,748]/[31,31]) so the mastery portrait renders over the pane's black hole (SV098 GT sec 4; mirrors
b60 pane fix; all 9 textures resolve, 18/18). **C** Darklings (skill25) + Dark Aperture (skill26)
moved col3->col6 (t3/t5, only m5 column with both free), canonical base@t3/augment@t5; Dark Aperture
stray `_right` bar cleared (pre-098i GT 8.5). **D** Shadow Link (drxbladehoning c3t2) straight bar
UP to Dark Invigoration (c3t4) - WILL-INTENT visual wire (drxopenwound has NO gameplay ref to
drxbladehoning - flagged). **E** Earth Soften Metal: NO-OP (build44 already c4t2 = brief's literal
target; SV098's c4t3 is now occupied by build41's intentional Flame Surge restoration - documented).
**F** Toxic Concoction + Shadow Stalker chains: verify-only, build44 already correct. **G** roster
audit: report-only, no further unambiguous non-golden GT mismatch beyond A-E.

RESIDUALS / WILL-CONFIRM (flagged in report, unchanged): (1) Item C column-6 t4 holds the CANONICAL
SV098 Throwing Knife, so Darklings' bar passes behind it as an empty-row passthrough - a fully "t4
EMPTY" canonical column needs Will's ruling to move Throwing Knife or a holistic m5 reflow (the
build42 reflow that wrecked trees was reverted in build44). (2) ~~Item D wire is visual-only, no
mechanics relation~~ **SUPERSEDED 2026-07-16 (Item D true-augment round, below)**. (3) Item E: SV098
exact c4t3 slot restore would need a holistic Earth col-4 reflow displacing the Flame Surge line.

## BUILD45 ITEM-D TRUE-AUGMENT (b70, 2026-07-16, feat/mastery-sv-fix - status: implemented+self-verified, awaiting independent vet)

Will ruling 2026-07-16: *"so how does dark invigoration work? I think it should augment shadow link."*
FINDING (corrects the build45 vet): Dark Invigoration (drxopenwound) **ALREADY** augments Shadow Link
(drxbladehoning) - it is a true `Skill_Modifier` bound by the LIVE occult SkillTree
`records\skills\stealth\drxstealthskilltree.dbr` (PC `skillTree5`) tree-order **drxbladehoning@6 (base,
Skill_BuffRadiusToggled) -> drxopenwound@7 -> drxanatomy@8 (modifiers)**. TQ binds a Skill_Modifier to
its base **purely by SkillTree numeric order** (nearest preceding non-modifier); PROVEN from vanilla
TQAE (Storm Nimbus/Heart of Frost/Static Charge + Warfare WarWind/Onslaught/BattleRage + Defense
Rally/**BattleAwareness (Skill_BuffRadiusToggled) + Focus/IronWill**) - zero record/UI back-reference
exists in vanilla either. The build45 "no gameplay relation" line was a VET ERROR (it checked
skillDependancy/buffSkillName, not the SkillTree). Dark Invig's `offensiveLifeMin` (flat vitality dmg)
+ bleed fold into the character while Shadow Link's aura is toggled, mirroring Heart of Frost/Storm
Nimbus; pairs with Shadow Link's -VitRes enemy debuff. Functional, not dead weight.

CHANGE: `tools/patches/mastery_sv_alignment.py` item D upgraded visual-wire -> TRUE-augment: apply()
**asserts** the tree-order binding fail-loud (module = ratified guarantor); verify() re-asserts at
**mechanism level** (walks live SkillTree, `nearest-preceding-non-modifier(drxopenwound) ==
drxbladehoning`) + negative test. build45 UI wire (c3 column: Shadow Link t2 square / Dark Invig t4
circle / Shadow Lore t6 circle + upward bar = the vanilla Storm Nimbus column shape) KEPT. Doubled
namespace: the twin `records\skills\skills\stealth\drxstealthskilltree.dbr` is referenced by NO PC
(dead orphan) -> no live/dead split; binding holds on the live tree; twin untouched.

VERIFICATION: **ZERO arz change** - mirroring Heart of Frost needs only tree-order (already present) +
the already-waived UI wire, so NO new golden override. Full scratch build EXIT 0, in-build apply
assert + registry verify OK, A7 golden gate PASS (74 waived / 0 hard), arz md5
`a659594ed85f8f5609bcab57fa7b757b` **byte-identical to build45**; record-diff vs a659594e = **0/0/0**;
verify() negative test FAILS as required; contracts souls+summons GATE PASS (0 P0 / 0 P1 / 112 P2, no
new); validate_tags PASS. Report: `docs/reports/b70_mastery_sv_alignment.md` item D. NOT deployed
(awaiting vet + Will test).

GOLDEN: +22 owner_approved_overrides (16 emblem m5/m6, 2 family positions, 2 Dark-Aperture-conn-clear,
2 Shadow-Link-conn-wire), each citing 'b70 mastery SV-alignment build45' + the GT file/Will ruling.
A7 golden freeze gate GREEN (74 waived / 0 hard) via the standalone build code path.

VERIFICATION: py_compile OK; registry selfcheck 26 modules (order 2493977b); record-diff dry-run vs
build44 (`439a9279`) = EXACTLY 17 modified records, ALL UI/connector fields, ZERO gameplay/stat delta,
every delta maps to a fix-list item; verify() negative test (flip Poisonous Gas back to square) FAILS
as required; full scratch DB build EXIT 0, all 17 registry verifies OK (incl mastery_sv_alignment),
A7 golden gate GREEN, arz md5 `a659594ed85f8f5609bcab57fa7b757b` (deterministic PYTHONHASHSEED=0
SVC_RELEASE_DROPS=1). NOT deployed (awaiting vet + Will iPhone/desktop test).

## OCCULT COLUMN-6 RESTACK (b70 item C2, 2026-07-16, feat/mastery-sv-fix - status: implemented+self-verified, awaiting independent vet)

Will ruling 2026-07-16 (verbatim): *"lets have darklings be in the same lane as throwing knife, but we
will have darklings unlock at 10, dark aperture unlock at 16, and then above it we will have throwing
knife at 24 and the augment to throwing knife at 32 so we wont have lines behind one another."*
FIXES the build45 item-C interleave (Darklings' t3->t5 bar crossed ThrowingKnife@t4; ThrowingKnife's
t4->t6 bar crossed DarkAperture@t5). RESTACK col6 (x=628) as a clean ladder: Darklings t3 (unlock 10,
stays) / Dark Aperture t4 (unlock 16, moves DOWN from t5) / Throwing Knife t5 (unlock 24, moves UP
from t4) / Flurry t6 (unlock 32, stays). Both augment bars now 1-tier ADJACENT (Darklings->DarkAperture
t3->t4; ThrowingKnife->Flurry t5->t6), drawn as the vanilla Shadow-Stalker len2 `[Bottom,Top]` bar.
ZERO crossings.

CHANGE (`tools/patches/mastery_sv_alignment.py` item C->C2, apply()+verify()): 5-record restack -
`skill26` button y 155->217; `skill10` button y 217->155; `drxdarklings` connOn/Off len3->len2;
`drxthrowingknife` connOn/Off len3->len2 + skillTier 4->5 + skillMasteryLevelRequired 5->24;
`drxdarklings_darkaperture` skillTier 5->4 + skillMasteryLevelRequired 24->16. Darklings(t3,gate10) +
Flurry(t6,gate32) already correct - asserted, not written. BOTH skillTier AND skillMasteryLevelRequired
are set == the row threshold so the unlock matches Will's number under EVERY gate-semantics (proof:
vanilla modifiers rainoffire_brimstone t6/req15, dream_slowtime t7/req16, nature_wildhunt t7/req1 sit
below their base tier -> req is NOT the sole gate; skillTier is; but DarkAperture's leftover req=24
could bind under max() -> set both). TIER LAW confirmed empirically (skillTier==row across 27 col +
142 vanilla buttons, ladder {1,4,10,16,24,32,40}). MECHANISM LAW: SkillTree slot ORDER UNTOUCHED -
DarkAperture@27 still binds Darklings@26, Flurry@10 still binds ThrowingKnife@9 (apply() asserts +
verify() re-asserts both bindings; a reorder fails the build). 0 external skillDependancy/buffSkillName/
petSkillName refs to either moved skill. Save-safe (tier gates resolve live).

GOLDEN: +10 owner_approved_overrides (2 button y, 2 drxdarklings conn, 4 drxthrowingknife
{conn,conn,tier,gate}, 2 drxdarklings_darkaperture {tier,gate}), each citing the Will 2026-07-16 ruling
verbatim. Item-C round-1 Dark-Aperture-conn-clear overrides retained.

VERIFICATION: py_compile + registry selfcheck 26 (order 2493977b) OK; dry-run replay vs `a659594e` =
EXACTLY the 5-record restack (2 button y + 2x len2 conn pairs + 2 skillTier + 2 gate), ZERO other
deltas; verify() PASS incl mechanism-level bindings + TIER-LAW + adjacent-bar; 3 NEGATIVE tests FAIL as
required (len3 crossing bar on ThrowingKnife; DarkAperture over-gate 24 on t4; ThrowingKnife button
misrow t4). Full scratch build EXIT 0 (all 26 registry verifies OK incl mastery_sv_alignment), A7
golden gate GREEN (84 waived / 0 hard), arz md5 `a7d46b532a5dcf4732e7f951ee695f2d` (deterministic
PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1); record-diff vs a659594e = 0 ADDED / 0 REMOVED / 5 MODIFIED
(EXACTLY: skill10.y, skill26.y, drxdarklings connOn/Off, drxthrowingknife connOn/Off+skillTier+gate,
drxdarklings_darkaperture skillTier+gate - ZERO other deltas); contracts souls+summons GATE PASS (no
new P0/P1); validate_tags PASS (2 pre-existing base monster-name WARNs, non-blocking; 0 mod-tag miss).
Report: `docs/reports/b70_mastery_sv_alignment.md` item C2. NOT deployed (awaiting vet + Will test).

## B81 - PET IDENTITY PASS round 1 (Will 2026-07-16 "beastman not a skeleton", R-11) - FIX COMPLETE + SCRATCH-VERIFIED (branch fix/runtime-green, on top of b75)
RCA `docs/reports/b81_pet_identity.md`. Ground truth build45 `917d9047` (`characterRacialProfile`
decoded off 8 records incl. Lyia's own monster + pet record: skeletons/zombies=Undead, satyrs/
centaurs/maenads=Beastman, shadowstalker demons=Demon, automatoi=Construct, sandspirit=Magical).

**Root cause (3rd repeat-report against the SAME class in one day - portrait b71, Maenad sound/
controller residue flagged-not-fixed by the b55r2 vet, now race):** every `_build_boss_summon`
pet is a Lyia Leafsong clone; Lyia's OWN donor lineage is MAENAD
(`characterRacialProfile=Beastman`, `distressCallGroup=Maenad`, 7 Maenad sound paks), and none
of these fields is in `_SKILL_PREFIXES`, so `_update_existing_fields` never overwrites them -
they survive on EVERY pet as residue regardless of the pet's true body.

**FIX (upstream, BL-103, `_build_boss_summon`):** new `_align_pet_identity(db, path, source)`
runs for every pet the helper builds (19 families / 57 pets, confirmed by this build's
"PET-STAT-MIRROR/PET-GEAR-PARITY gate OK: 19 summon families" - the exact `_SUMMON_PET_BUILDS`
roster, incl. Devourer/Xeiwang/Mountainblade/EaterOfDays/Pygmalion/Sarpedon/LongNu/Meritamen/
Broodmother+Wyrmling/Voranthys/TantalusShade/CharonOarsman/Mnemophage/KravmolochWarden/
HadesMarshal/Neferkha via `four_generals.py`/`neferkha.py`'s shared call). Source-faithful
field-by-field: `characterRacialProfile` + `distressCallGroup` + the 7 alert/criticalHit/death/
rally/rampage/stun/vox sound-pak field-groups (+ their Chance/Delay siblings) copied VERBATIM
when the source defines that exact field, STRIPPED (not blanked) when it doesn't. Toxeus the
Enslaver -> **Undead** (Will's literal ask). Meritamen's real source itself carries
`distressCallGroup=Maenad` - correctly KEPT (source-faithful design, not a hard-coded
exception, proven by this edge case). Runs unconditionally (incl. `protect_green=True`
Devourer pets - race/voice identity is independent of the intentional-green-poison concern).

**NOT touched (documented, out of pass scope):** `controllerAggressive/Defensive =
controller_maenadmerc_{normal,defensive}` - the PET-BEHAVIOR AI controller (Pet.tpl contract,
distinct from the source MONSTER's single `controller` field the builder already correctly
repoints) - a swap risks AI/behavior regressions; dormant Maenad loot refs
(`lootFinger2Item1`/`lootMisc2Item6`, `dropItems=0`) - equipment/loot-class, forbidden by the
pet-field safety law.

**GATE (anti-oscillation):** `enslaver_pet_fx._verify_chain` extended with
`_race_and_voice_problems` for the 3 formally-gated families (Enslaver/Marauder/Hades Marshal):
pet race == own source race; no Maenad voice/distress residue unless the source itself is
Maenad. `_CHAIN` entries gained `source`/`sub_source` keys. 2 new negative tests
(`scratchpad/negtest_gate.py`): plant Beastman race on `toxeus_enslaver_1` -> FAILS; plant
Maenad `voxSound` on `enslaver_marauder_1` -> FAILS (both proven, alongside the 3 pre-existing
b71/b75 negatives + the clean-arz positive control, all still green).

**Verified:** full scratch build EXIT 0, 26/26 registry verifies OK, A7 golden PASS (84 waived,
unchanged); idempotent (arz md5 `f639ba409562a334add231956637ac71` x2); record-diff vs the b75
baseline `baa76edb` = **0 added / 0 removed / 57 modified**, 0 collateral (confirms A7/Map/
Quests/Text untouched); contracts (souls/summons/resources) IDENTICAL totals vs baseline
(`TOTAL: 11293 violations (0 P0, 576 P1, 10717 P2)` on both -> 0 new); B-SUMMON-1 STRICT
failures 0 (253 pets checked, 279 chains). NOT deployed (awaiting vet + Will test).

**WILL-CONFIRM after a full Steam restart** (DISMISS + RE-SUMMON any already-active pet):
character-sheet race now matches each pet's true body (Undead for the skeleton-sourced
summons, Demon for the demon-rig summons, Construct for Pygmalion, Magical for Meritamen); the
alert/hit/death/stun/vox voice now matches the body instead of a Maenad woman's cry coming out
of a skeleton. No visual/mesh/stat change.

**Scope note:** the main checkout (separate concurrent session) has since added
`docs/WILL_RULINGS.md` (`5f139c3`, not on this branch) recording this task verbatim as **R-11**.
This fix satisfies R-11 in full; whoever integrates this branch should mark R-11 IMPLEMENTED
with this commit's sha (not done here - out of this worktree's scope per its standing
no-reset/no-pull instruction).

## B81r2 - PET IDENTITY PASS round 2 (vet NO-GO on round 1) - FIX COMPLETE + SCRATCH-VERIFIED (branch fix/runtime-green, on top of B81 round 1)
RCA + full detail in `docs/reports/b81_pet_identity.md` ROUND 2 section (appended). Ground truth:
independently decoded the 7 second-lineage builders' own source monsters (already named in each
function for anim/skill copy) + a fresh full sweep of all 222 `records\skills\soulskills\pets\*`
records in the round-1 arz.

**Vet's finding:** round 1 verified clean but the report OVERCLAIMED completeness. A second, older
Lyia-cloning summon-pet lineage - 7 standalone builders in `apply_svc_patches.py`
(`_create_boneash_pet_skill`, `_create_boss_summon_from_source` for Narok+Vort,
`_create_pharaoh_guard_pet_skill`, `_create_bwpriest_pet_skill`, `_create_lillued_pet_skill`,
`_create_rakanizeus_pet_skill`; 21 pets) - clones Lyia the same way `_build_boss_summon` does but
never called `_align_pet_identity`. Race was already hand-corrected by the original authors in
all 7 cases (matches source); only `distressCallGroup` + the 7 sound-pak stems were Maenad
residue.

**FIX:** same round-1 `_align_pet_identity(db, path, source)` call, added at each of the 7
builders' existing anim/skill-copy site, against the source record each already names. Zero new
mechanism - the already-vetted round-1 function reached from 7 more call sites.

**Also audited (vet's suggested option (a)) the 3 remaining upstream-native (NOT built by any
function in this file) SV 0.98i pet families** found in the full sweep: **Aletha Darkclaw**
(7 records) - her own source `um_alethadarkclaw.dbr` IS literally a Maenad monster; pet already
matches byte-for-byte; correctly left untouched. **Helike** (live, player-reachable via
`helike_soul_{n,e,l}` -> `summon_helike`) - new standalone `_align_helike_identity(db)` call
(no shared builder exists for upstream-native content) proves **0 fields changed**: Helike was
ALREADY correctly sourced by the original SV 0.98i authors (her `distressCallGroup=Maenad` is
source-faithful - the source monster itself defines it, same shape as Meritamen) - confirmed
clean, not fixed, now permanently gated. **Phagia** (4 records) - confirmed ORPHANED: a full
`itemSkillName` sweep of the built arz found zero live grants of `summon_phagia` (build36's
Meritamen fix intentionally repointed the only souls that ever granted it); no player symptom;
left untouched, registered as BACKLOG debt (see below), not silently dropped.

**GATE (anti-oscillation):** new `_SECOND_BUILDER_ROSTER` in `enslaver_pet_fx.py` (8 families / 24
pets: the 7 fixed + Helike) + a new leg in `verify()` reusing the round-1
`_race_and_voice_problems` function unchanged. 2 new negative tests (plant Beastman race on
Boneash / plant Maenad voxSound on Narok) FAIL as required; all 5 round-1 negatives + the positive
control still pass (7/7 total green).

**Verified:** full scratch build EXIT 0, 17/17 registry verifies OK incl. the new gate leg
("second-lineage race/voice gate OK: 24 pets across 8 families, b81r2"); A7 golden PASS (84
waived, unchanged); idempotent (arz md5 `e77846c3a43cadbfc5af0720ce0fa8ef` x2); record-diff vs
the round-1 baseline `f639ba409562a334add231956637ac71` = **0 added / 0 removed / 21 modified**
(exactly the 7x3 fixed pets; `characterRacialProfile` absent from every one of the 21
changed-field lists, confirming race was already correct pre-fix - only distressCallGroup/sound
paks changed), 0 collateral anywhere else in the 51,057-record db; B-SUMMON-1 STRICT failures 0
(279 chains, 253 pets, run with base-game+upstream args - identical to round 1); contracts run
identically against both builds in this worktree (no `Resources/` dir here, so absolute
counts are environmentally inflated vs a live deploy - pre-existing, not introduced by this pass)
- **IDENTICAL totals both runs** (19168 violations, 96 P0, 7244 P1, 11828 P2) => **0 new**.
NOT deployed (awaiting vet + Will test).

**WILL-CONFIRM after a full Steam restart** (DISMISS + RE-SUMMON any already-active pet):
Boneash/Narok/Vort/Pharaoh's Honor Guard/Blood Witch High Priest/Lil'Lued/Rakanizeus now
alert/crit/death/rally/vox in their own voice instead of Lyia's Maenad-woman voice. Aletha
Darkclaw and Helike unchanged in-game (both audited correct). No visual/mesh/stat change.

**BACKLOG DEBT registered (per "NO NEW SURFACE WITHOUT A GATE + DEBT REGISTER"):** Phagia
(`phagia_{1,2,3,34}` + `summon_phagia.dbr`) is dead upstream content with zero live grant path
today - not fixed (no player symptom), not deleted (RETIREMENT PROTOCOL). If Will ever wants a
standalone Phagia summon restored, it needs its own soul/grant-wiring design decision.

## BUILD45 GATE RECORD (2026-07-16, DEV-only; STEAM BLOCKED until Will's in-game tree + summon check)
Contents: merges `ed1a197` (fix/enslaver-chain `831d9e7` = b71 skeleton identity + StatusIconRed
gate hardening) + `61d3459` (feat/mastery-sv-fix `16283c13` = b70 shapes/emblem/Darklings + DI
mechanism gate + col6 restack). Artifacts: arz `917d9047d2281284f5fd5e9a163b9c5c`; Text UNCHANGED
(`3e576581`); Levels/Quests UNCHANGED from build43. Registry 26 modules (+mastery_sv_alignment).
Gates: A7 PASS (84 waived incl col6 Will-ruling waivers), summon validators PASS, chain gate green,
contracts GATE PASS 0 P0/0 P1/4909 P2 (pre-existing count). Proof-diff vs build44 (439a9279):
72 modified / 0 added / 0 removed = exactly the union of the two vetted deltas (52 soulskills
portraits+icon, 15+1 mastery-UI emblem/shape/position, 4 stealth col6 tiers+connectors), zero
strays. NOTE: col6 restack surfaced that Throwing Knife's real unlock was 5 pts while drawn on the
16-row (pre-existing misalignment class) - now 24 pts matching its t5 row per Will's ruling.
DEV deploy hash-verified 917d9047 (TQ not running). Pre-existing flagged for future holistic m5
pass: drxlethalstrike _right bar rises toward empty c6t7 passing Flurry (byte-identical since
before b70). WILL TESTS on DEV: Occult/Hunting tree shapes (PoisonousGas circle, BladeFury/
SmokeScreen/Eviscerate squares), emblem circle filled x9, col6 ladder 10/16/24/32 no crossed bars,
DarkInvigoration bar to ShadowLink; ENSLAVER: DISMISS + RE-SUMMON -> black bodies, deathwalker
skill icon + pet-bar portraits (pets resolve DB at summon time).

## BUILD46 GATE RECORD (2026-07-16 night, DEV-only INTERIM ship; Steam untouched)
P0 unblock ship: main @ merge `4c8f128` (fix/chumbi-lag b76 only - the other GO branches integrate
in the next wave). Contents: Monster Test Yard REMOVED from the TESTHUB map builder (the 10-boss
QA cluster in HiddenValley01/"Chumbi Valley" around the Rebirth Fountain - the freeze + death-loop
root cause, TESTHUB-only so Steam was never affected) + sepulcher-chain summon TTLs restored
(aktaios_summontombguardians 5.0s, alastor skeleton warrior/archer + recursive undeadmelee 20.0s,
matching SV's own values; side effect: base Aktaios + Alastor bosses' minions now despawn -
disclosed, Will may veto values). Artifacts: arz `7fb879ac9c346280cdaf3610e7d53dad` (canonical
build reproduced the lane's vetted scratch byte-identical); TESTHUB Levels
`0925043a4c4c50a7bb76f02b7f73667b` (chumbi vet proved: exactly ONE level blob changed vs deployed,
navmesh 0x0b byte-identical, QUESTS byte-identical); canonical Levels UNCHANGED `62868eec` (yard
was TESTHUB-only); Text UNCHANGED `3e576581`; Quests UNCHANGED. Gates: A7 PASS (84 waived), summon
validator PASS, registry 27 modules, chain gates green (contracts = byte-identical inputs to the
lane's green run). DEV deploy hash-verified both artifacts (TQ not running). DEBT: promote the
uncapped-summon sweep to a carefully-scoped build gate (NOT petLimit-no-TTL blanket - 140 healthy
skills have that shape); placement spacing/clearance gate follow-through; ~~census_placements.py v0e
stride fix; stale gate_build32_parseback refresh~~ **-> both ✅ CLOSED 2026-07-28, see
BUILD46-TOOLING-DEBT below.**

### BUILD46-TOOLING-DEBT - ✅ CLOSED 2026-07-28 (branch `fix/debt-tooling`)
**(a) `tools/debug/census_placements.py` v0e stride.** The walker hardcoded `BASE = 72`. The 0x05
record stride is VERSION-dependent - 72 only for blob v0x11/v0x0f, **56 for v0x0e** - so on a v0e
level the walk desynced after the first record and ran off the section end; `main()` swallowed the
resulting `struct.error` in a bare `except: continue`, so those levels vanished from the census
without a word. MEASURED on `local/Levels_merged.arc` (2282 levels; 1417 v0x11 / 369 v0x0f / 496
v0x0e): **418 of the 496 v0x0e levels were silently dropped**, and the census reported **1705 custom
encounters across 282 levels instead of 3446 across 368** - it was hiding half the world's boss/proxy
placements, which is exactly the "wrong census is worse than none" failure the debt item names.
FIX-UPSTREAM: there is now ONE stride rule, `contracts_map.blob_0x05_base(blob)`, and
`contracts_map.parse_0x05` carries the instance `pos` so `census_placements.instances()` delegates to
it instead of keeping a second, wrong copy of the walk. The bare `except: continue` is replaced by an
explicit unparsed-levels report.
PROOFS:
* `py tools/debug/census_placements.py local/Levels_merged.arc --verify-stride` (NEW gate, with a
  PLANTED NEGATIVE) -> **PASS**: version-aware stride walks every 0x05 section to its EXACT end on
  all 2282 levels (v0x0e 496, v0x0f 369, v0x11 1417); the pre-fix hardcoded base-72 stride desyncs on
  **437 / 496** v0x0e levels and **0 / 369** v0x0f and **0 / 1417** v0x11 - i.e. the gate provably
  discriminates.
* before/after census on the same map: 282 levels / 1705 custom -> **368 levels / 3446 custom**.

**(b) `tools/debug/gate_build32_parseback.py`.** REFRESHED, not retired. It was broken three ways:
(i) it died at IMPORT time - it pulled `ArcArchive`/`parse_sections` through
`verify_groups_bindings`, which `from arz_lookup import load_arz`, and **`arz_lookup.py` was never
committed** (only a stale `.pyc` in `tools/debug/__pycache__/` survives). That also meant
`tools/verify_groups_bindings.py` itself could not run on any clean checkout - fixed upstream by
switching it to the committed `arz_converter.read_arz` (it now runs: **PASS**, 371 devices checked /
371 bound / 0 dead, 5/5 must-binds OK). (ii) M8 froze absolute counts and indices ("995 -> 996",
`insts[995]`); farmland06d is now **993** instances because b44/b46 removed
`portal_olympianarena1/2` + `map_portal_aura`, so the gate crashed with `IndexError`. (iii) The
`--testhub` MYARD block asserted the HiddenValley01 Monster Test Yard that **b76 removed** as the
chumbi-freeze P0 (`docs/reports/b76_chumbi_freeze_rca.md`, R-30/R-31), and the RIG block asserted the
build34 Model-C rig coords that the `svc_helos_trav_*` traveller hub superseded.
The frozen constants WERE the defect, so the gate is now DELTA-based (declared appended/removed sets,
matched on dbr basename + position) and STRUCTURAL (tail placement, flags=0, exact-end walk at the
version-derived stride, collateral byte-identity incl. the 0x0b navmesh). RETIREMENT PROTOCOL: no
record or placement was deleted - the two obsolete blocks were REPLACED by invariants that still
describe live design: MYARD is INVERTED into a b76 guard (TESTHUB HiddenValley01 must be
byte-identical to canonical, i.e. the yard must never come back), and RIG became a namespace/shape
invariant (every TESTHUB-only host = canonical PLUS tail-appended flags=0 NPCs in the
`records\quests\svc_` hub namespace) that does not rot when the hub roster changes. The one canonical
placement the TESTHUB build legitimately DROPS (the b48 SPARTA-MUTE Almyros de-dup) is declared
explicitly in `HUB_DECLARED_DROPS` rather than waived by loosening the check.
PROOFS:
* `--selftest` (4 planted negatives + 1 positive) -> **PASS**: an undeclared extra append, a silent
  removal, a moved pre-existing instance and a NON-tail insertion are each rejected; an honest tail
  append passes clean.
* canonical: `--map local/Levels_merged.arc --baseline ...build31g... --m10-baseline ...build32a...`
  -> **RESULT: PASS (M8 + M9 + M10 parse-back clean)**.
* TESTHUB: same plus `--testhub --canonical local/Levels_merged.arc` -> **RESULT: PASS (M8 + M9 +
  M10 + HV01-b76-guard + HUB parse-back clean)**, 133 checks, 0 FAIL, including
  `TESTHUB HiddenValley01 is byte-identical to canonical (no yard) (697207 -> 697207 bytes)`.

### ~~B76-R2-SUMMON-GATE: promote the uncapped-summon sweep from diagnostic to a build gate~~
- ~~`tools/patches/summon_caps.py` `sweep_uncapped`'s docstring literally said "DIAGNOSTIC (not a
  build gate)". `verify()` only re-asserted the 4 known sepulcher-chain targets, so a NEW unbounded
  fast summoner (the Chumbi-Valley freeze class Will hit as a P0) would ship unnoticed.~~
- **✅ CLOSED 2026-07-28 (branch `fix/debt-gate`). The sweep is now a scoped build gate.**
  - **WIRED INTO THE REGISTRY VERIFY HOOK.** `summon_caps.verify()` now asserts TWO invariants:
    (1) the original targeted one (the 4 sepulcher-chain skills carry a positive TTL in the final
    arz), and (2) the new CLASS one - no unbounded fast summoner anywhere in the arz that is not
    an evidenced waiver. `summon_caps` is registered in `tools/patches/__init__.py`, and
    `run_registry_verifies()` propagates a module `verify()`'s `SystemExit`, so this aborts the
    build. `sweep_uncapped`'s "DIAGNOSTIC (not a build gate)" docstring is gone.
  - **NOT A BLANKET petLimit-no-TTL RULE** (the build46 debt line's explicit constraint). The
    gated shape is the genuinely unbounded one: `Skill_*SpawnPet*` **AND** no positive `petLimit`
    **AND** no positive `spawnObjectsTimeToLive` **AND** cooldown < 10s. The ~140 healthy skills
    that carry a petLimit without a TTL are untouched - and that is now enforced by test, not just
    asserted (negtest D1).
  - **WAIVER seeded with EXACTLY the 8 records the sweep finds on the shipped arz** (2026-07-28
    re-run: still exactly 8, no drift since b76), each with per-record evidence in
    `_UNCAPPED_WAIVERS` - provenance, referencing records, and placement:

    | record | evidence |
    |---|---|
    | `records\skills\boss skills\telkine_projectilespawnpet.dbr` | **BASE-GAME** (in the stock database.arz); spawns the E3-demo `GoldenSkeleton`; 0 referencing records; not placed |
    | `records\skills\skills\boss skills\telkine_projectilespawnpet.dbr` | duplicate-path twin of the above (upstream `records\skills\skills\` namespace duplication); 0 refs; not placed |
    | `records\skills\nature\old\oldnaturemastery_animalcompanion.dbr` | **BASE-GAME**; `\old\` = the retired pre-release Nature mastery; 0 refs; not placed |
    | `records\skills\skills\nature\old\oldnaturemastery_animalcompanion.dbr` | duplicate-path twin of the above; 0 refs; not placed |
    | `records\events\summoning\01_skill_zombiemelee_swarm_a.dbr` | upstream event content (absent from the stock arz); ttl=0.0; 0 refs; not placed |
    | `records\events\summoning\01_skill_zombiemelee_swarm_a_1sec_cd.dbr` | upstream event content; the **only** waived record with a live reference (`01_spawner_zombiemelee_swarm_a.dbr` `buffSelfSkillName` + `skillName2`) - but a **whole-world-blob scan of the 2.09 GB `Levels.arc`** finds **0 hits** for the spawner, the skill, or the substring `zombiemelee_swarm`, so nothing shipped can instantiate it |
    | `records\skills\nature\copy (2) of drxregrowth.dbr` | DRX authoring leftover (the filename is literally "copy (2) of"); 0 refs; not placed |
    | `records\skills\earth\test\stoneform_spawn_bait.dbr` | `\test\` namespace bait record; 0 refs; not placed |

    Adding a waiver requires the same three pieces of evidence; the failure message says so.
  - **WAIVER HYGIENE:** a waived record the sweep no longer flags is reported as STALE and
    **never auto-removed** - RETIREMENT PROTOCOL applies to the evidence attached to a waiver just
    as it does to a record. Never fatal.
  - **PLANTED NEGATIVE TEST** (`py tools/patches/summon_caps.py --negtest`) - **PASS**, 14 checks.
    Half 1 (original classifier): uncapped fast summoner flagged, TTL-capped clears. Half 2 (the
    new gate): **A** a new unbounded fast summoner is an offender; **B** `verify()` raises
    `SystemExit` naming it (the gate actually kills the build, not just reports); **C/C2** a waived
    record does not trip it and `verify()` passes with only waived offenders present; **D1-D5** the
    false-positive guards - petLimit-without-TTL, a 60s-cooldown uncapped summoner, TTL-without-
    petLimit and a non-SpawnPet class are each NOT flagged, and a healthy db flags nothing at all;
    **E** absent waivers report stale, never fatal.
  - **PROOF ON THE SHIPPED ARZ:** `summon_caps.verify()` against
    `work/.../SoulvizierClassic.arz` -> `4 sepulcher-chain summon skills all carry a finite
    spawn-TTL` + `no new unbounded fast summoners (8 waived: base/dead/test, each evidenced)`,
    returns cleanly, **0 offenders / 0 stale**.

## BUILD47 GATE RECORD (2026-07-17, DEV-only; Steam untouched - Will's in-game pass required)
INTEGRATION WAVE 2: main merges fix/runtime-green (b75+b81 identity) + fix/soul-tiers (b78 gate +
b85 High Priest) + fix/mastery-unlock (b77) + fix/formula-names (b80) + feat/black-poison (b73
champions + b72 EoAT + b83 black poison/Rite drops) + fix/bloodtoxeus-spawns (b79). Cross-branch
collision caught by fail-loud verify + fixed: enslaver_pet_fx b81r2 gate roster still mapped
bwpriest pets to the blade-dancer (Demon) after R-43 rebuilt them from the High Priest (race God
per amgoz1's own c_disciple_miniboss) - roster repointed. CRLF-masked union-marker lesson: union
conflict resolution must strip markers with strip()-compare (CRLF files hid '=======\r'), and code
conflicts need hand reconciliation (enslaver_pet_fx verify print). Artifacts: arz
`5a3c016baae8f136b8b801ea871b71ba` (19 in-build verifies green incl the merged-state re-assert of
every lane's gate; A7 golden PASS; registry 32 modules); Text `fcca49277b9d31ed451e4a6843898843`
(renames + 417-tag file emitted by THIS build - lesson: never feed a stale uber_soul_tags.txt;
validate_tags PASS); canonical Levels `17bed65f` + TESTHUB `42d83885` (blob-diff BOTH variants =
exactly drxFirstRoom + drxFirstxistion_connection changed [the parchment encounter relocation],
QUESTS byte-identical, navmesh 24/24 both); Quests unchanged. Contracts GATE PASS 0 P0/0 P1
(4910 P2; +1 = the new formula record's known idiom slot). Record-diff vs build43 baseline:
28 added / 1 removed / 172 modified across the whole 44-47 arc. DEV deploy hash-verified all
three artifacts (TQ not running). baseline_build47.arz snapshotted.

## FIX-ROUND BATCHING NOTE
All the P0/P1 map items (B-PORTAL-1/2/3, B-SPRITE-1, B-SMOKE-1, B-TEMPLE-DOOR-1) share the map
lane → batch into one implement→vet wave, rebuild BOTH artifacts (canonical + TESTHUB), coupled
deploy. The DB items (B-SUMMON-1, B-TOXEUS-1) share apply_svc_patches → one DB wave. B-TEXT-TAGS-1
rides that DB wave (arz + Text.arc ship together). Portals touch BOTH lanes (record fields = DB;
placement = map) - coordinate.

## 🌐 WORKSHOP FEEDBACK (triage inbound player reports here)

The Workshop item (3759792705) is PUBLIC, so players will report problems via **Workshop comments**
and ratings on the item page. There is no automated inbox - Will (or an agent, if he pastes them in)
must read the comments periodically and triage each report INTO THIS BOARD:

1. Reproduce or map the report to an existing item (many will be B-PORTAL-* / B-SUMMON-1 / the raw
   tags B-TEXT-TAGS-1, already known). If it matches, note "also reported on Workshop" on that item.
2. If it is new, file it here with a `B-<AREA>-N` id, the player's description (verbatim), a
   reproduction/cause hypothesis, and the fix lane - same shape as the items above.
3. Distinguish **mod bugs** from **install/environment issues** (missing 4GB LAA patch, loaded a
   normal character into the Custom Quest, base-game version mismatch, subscribed-but-not-downloaded).
   Environment issues → answer in a Workshop reply + capture the FAQ in `docs/SHARE_AND_PLAY.md` /
   `docs/STEAM_RELEASE.md`; do not clutter the bug board with them.
4. When a fix ships, note the build/commit and (optionally) reply on the Workshop comment so the
   reporter knows it is addressed.

Standing watch items likely to draw comments until fixed: the 8 raw tags (B-TEXT-TAGS-1) are visible
to every subscriber right now; portals look rough (B-PORTAL-1). Prioritize those before a wider push.

## ✅ RESOLVED / VERIFIED

### M14 (build31e, 2026-07-10): dead-content-audit small items - dev quest de-registered + stray tombstone de-placed
- `testquesttoopendoors.qst` DE-REGISTERED from the QUESTS(0x1b) load window (was idx 101 - a
  leftover dev quest duplicating door unlocks on unverified conditions and burning a slot of the
  256 window). Registry is now 255 entries; boundary pair (hcdungeon_control + x2_StartQuest)
  intact; quest identity is name-keyed so the post-101 index shift is neutral; one slot FREED for
  future registrations (e.g. z_primrosecontroller if the Primrose secret is ever un-mooted). The
  .qst stays in the arcs harmlessly (never loads). `DEREGISTERED_NATIVE_BASENAMES` +
  fail-loud asserts in svaera_plus_portals.build_ordered_quest_list.
- The stray Atlantis `tombstone.dbr` (locked FixedItemQuestObject, dev placeholder description
  'Hogge', zero quest refs) DE-PLACED from Greek MonsterCave01B (was inst [58]).
  `REMOVE_STRAY_PROP_SPECS` in build_section_surgery.py; the only level blob the build31e wave
  changed (per-level byte-diff proof; M13a lives in the world GROUPS/QUESTS sections).

### B-STARTER-CHEST-1 + B-STARTER-CHEST-2: starter chest RESOLVED (build30.2, in-game verified 2026-07-09)
- **Symptoms:** (1) Will 2026-07-08: the chest should drop 12 inventory bags + 36 potions for co-op;
  (2) Will, live build30: opening the starter chest drops NOTHING (not even potions).
- **ROOT CAUSE (validated end-to-end via DEV A/B tests):** build28 (5af85d3) replaced the record's
  native RunEquation numSpawnMin/MaxEquation '3+(2*numberOfPlayers)' with the bare integer literal
  '48'. The engine evaluates the bare-literal form to 0 on this container -> numSpawn 0 -> the
  WHOLE chest dead (including the untouched potion slot) through b28/b29/b30. The chest had dropped
  bags since v1.0 (17257c8: loot2+loot3 = startingloot_sack at chance 100, native equation); every
  build27-era deployed arz (e.g. c4aa4d75) drops. The build30.1 "byte exoneration" compared
  build30-vs-build29 = broken-vs-broken, and its bare-literal precedent (boss_tartarus min/max='1',
  a different container) did not transfer. Decisive in-game datapoints: SV-original byte-restore
  (arz 39174e9c) = potions drop; equation-form fix (arz c959a372) = potions + bags drop ("that
  worked perfect" - Will 2026-07-09); the literal builds = nothing.
- **FIX (build30.2, grant_all_inventory_bags in tools/build_svc_database.py):** numSpawnMin==Max =
  '46+(2*numberOfPlayers)' (equation FORM, 48 solo, scales co-op like the original); ONE active
  slot loot1Chance=100 with dual tables Health_01-05All w108 : startingloot_sack w36 (3:1 ->
  E[36 potions + 12 bags]; multi-table slots = ubiquitous base FixedItemLoot precedent, e.g.
  defaultloot\hiddenchest_greece_00-15); loot2..6 restored to the record's NATIVE inert shape
  (chance 0, weights 0, NameN fields DELETED not blanked - an empty-string .dbr ref is the
  B-TOXEUS-2 zero-precedent loader-abort shape); NO soul (build29's sow slot stays removed).
- **LESSON (standing):** RunEquation-typed fields require equation-form values - bare integer
  literals can silently evaluate to 0. Byte precedent does not transfer between containers, and
  a byte-diff against another broken build proves nothing: in-game verification is MANDATORY for
  engine-facing constructs.

### A10 SUMMON-THE-BOSS SOULS: Narok the Rockskin + Vort the Red (build29, owner request)
- Both souls now GRANT A MANUAL-CAST SUMMON OF THEIR OWN BOSS (the Boneash-proven pattern:
  pets cloned from Lyia Leafsong's Pet.tpl baseline, rig/skills replaced with the SOURCE
  monster's own, loot-table equipment via _set_pet_equipment, permanent companion, no autocast
  controller). Narok = um_rockskin_42 (storm/spirit staff caster, Ternion + storm orbs); Vort =
  hero_tarthon_na'arak_40 (the record that DISPLAYS "Vort the Red" via tagMonsterName1139 - the
  SV filename mismatch is upstream). Summon skills records\skills\soulskills\summon_{narok,vort}
  .dbr: 250/300/350 energy, 180s recharge, 3-tier pet ladder, boss-name pet nameplates.
- NEEDS WILL SIGN-OFF (aggressive-but-sane per "way more powerful"): Narok pet life
  9500/14000/20000 (source floor 9.3-13.9k), INT 450 STR 250 DEX 200, dmg 60-90/90-140/130-200,
  scale 1.3; Vort pet life 18000/26000/36000 (source floor 17.8-26.8k), STR 450 DEX 350 INT 400,
  dmg 70-100/105-160/150-230, scale 1.55 (source). Soul lines: rockskin ternion augment 3/4/5 ->
  6 uniform, +250 life, mana penalty -80 -> +150, +25% cast, +25 fire res; vort concussive blast
  2/3/4 -> 5 uniform + NEW thunderball augment 4, +200 life/mana, +30% cast, +25 lightning res.
- Gated by: summon-pet chain validator, castability (no special anim), clone-shape rules,
  record-diff enumeration. Fail-loud: a missing source record now ABORTS the build (was a
  print-and-continue WARNING for all pet summons).

### A6 HUNTING BOLT TRAP = FOUND, ALREADY LIVE (build29 decode, REPORT-ONLY - no change made)
- Will's memory of "a custom-modded bolt trap in Hunting" is CORRECT and matches the SHIPPED
  build28 artifact: Hunting (mastery UI slot 6) slot 19 = records\skills\hunting\drxmonsterlure.dbr,
  display name "Lay Trap" (tagSkillName083), Class Skill_AttackProjectileSpawnPet, spawnObjects =
  the full 20-level bolt-trap pet ladder (records\skills\hunting\drxpet\bolttrap_01..20, mesh
  Effects\Hunting\TrapTikiCrossbow.msh, attack = bolttrap_defaultattackskill
  Skill_AttackProjectileBurst, petLimit 3-5, TTL 30s, monsterClassification Common, NO special
  anim = castable). SV 0.98i upstream had the same design but wired only levels 1-2 in
  spawnObjects; the shipped 20-level ladder is richer (hand-tuning). Modifier slots: 20 =
  drxmonsterlure_petmodifier_detonate, 21 = drxmonsterlure_rapidconstruction. Separately, the
  OCCULT tree (slot 5) carries drxlaytrap ("Breach") + drxlaytrap_petmodifier_multishotbolttrap.
  NOTHING to fix; tree untouched per the hand-tuning law.

### A9 SUMMON-PET RENDER-CHAIN VALIDATOR = LIVE (build29)
- tools/validate_render_chain.py, wired into build_svc_database post-write: every soul-granted
  summon pet's mesh + baseTexture + status icons and the summon skill's bar icons must resolve
  in the shipped arcs (mod Resources + game Resources[/XPack*]; TQ archive-name resolution incl.
  the XPack second-component convention). Mod-authored pet mesh/texture = FAIL (invisible-pet
  class of bug); icons + upstream records = WARN. build29: 203 pets / 2852 art refs checked,
  PASS with ~22 upstream WARNs (known cosmetic debt now visible: thunderballnova + some soul
  party icons, albinospider/formicid upstream meshes). Negative-tested (bogus mesh on a mod pet
  correctly fails the build). NOTE: the gate needs the standard work/ layout (a Resources dir
  beside the arz output + the game dir from the base-arz argument); an isolated rebuild to a
  scratch dir SKIPS it loudly instead of false-failing every mod art ref.

### A7 GOLDEN FREEZE GUARD = LIVE (build29)
- tools/occult_hunting_golden.json (generated from the build28 SHIPPED pair arz c4aa4d75 + Text
  38d6582a) freezes the owner's hand-tuned Occult (slot 5) + Hunting (slot 6) state: 125 records
  (UI slots/panectrl x3 priorities/positions + every tree skill + 1 hop of buff/pet delegation
  payloads) + 110 name/desc tag definition lists (per-file, in order - first-definition wins).
  Fail-loud gates: build_svc_database post-write (DB half) + build_text_arc post-write (full
  pair). ANY drift fails the build unless its printed key is added to owner_approved_overrides
  with Will's sign-off. Negative-tested (record-field, tag-value, and tree-membership mutations
  all caught). Validator: tools/validate_mastery_golden.py (also runs standalone).

### B-CHEST-1: Esfri's chest = WORKING AS DESIGNED, one-time per character (RESOLVED 2026-07-08)
- Exhaustive recon (shipped arz + Quests.arc + SV 0.98i upstream, byte-level): the chest
  (proxy_hidden_bloodcave_chest -> hidden_bloodcave_chest_0{1,2,3}, Champion-locked
  FixedItemContainer) drops random gear/gold from its own table; the SUPRA FORMULA comes from the
  QUEST ACTION on Condition_UseFixedItem: Action_BestowTriggerToken('OpenedHiddenChest') +
  Action_GiveItem(supra_special) = exactly ONE random supra formula (1 of 25) placed SILENTLY into
  the bag (placeholder notification tags, see B-SUPRA-NOTIFY-1). The token is permanent per
  character and a Disable Chest trigger kills the proxy on every later level load: NO re-open, ever,
  for that character (not a session-reset chest, by design). The 'entering the area grants a
  formula' memory is REFUTED for BOTH our build and SV upstream (quest logic byte-identical).
  Will action: check bags/caravan for an unnoticed supra recipe scroll; a NEW character can earn
  one again. Quest confirmed inside the load window (idx 97/256) in the shipped map.

### POTIONS VERIFIED DROPPING (2026-07-08, recon + adversarial verify, both PASS)
- Skill point (2), attribute point (2), and experience (48) potions are all present in the shipped
  arz, fully wired, and actively dropping: they ride the SAME live rare-misc loot slot as relics
  across ~1,956 creatures (all acts x N/E/L), deliberately rare (roughly 0.006% common to ~0.5%
  boss per kill for a specific skill/attr potion); exp potions are ALSO sold by Greece market mages
  and all three types are forge-craftable. Progression gating by act is intentional data. No fix
  needed; do not re-investigate. (Reproduce: audit scripts referenced in the 2026-07-08 session.)

## ✅ RESOLVED: deploy / packaging

### B-WORKSHOP-PKG-1: Workshop item shipped as two broken mods "database" + "resources" (FIXED 2026-07-08, commit 1851203, tag workshop-wrapper-fix)
- **Symptom:** subscribers to item 3759792705 saw TWO broken mods "database" and "resources"
  instead of one "SoulvizierClassic". Root cause: package_workshop.ps1 staged database/ and
  resources/ as direct children of the vdf contentfolder, and SteamCMD uploads the contentfolder's
  CONTENTS, so the item root had no SoulvizierClassic wrapper (TQAE treats each top-level folder of a
  workshop item as a mod name).
- **Fix:** package_workshop.ps1 now stages to dist/workshop/content/SoulvizierClassic/{database,
  resources} and upload_workshop.ps1 points the vdf contentfolder at dist/workshop/content (whose
  only child is SoulvizierClassic). The packager wipes the stale wrapperless staging each run,
  asserts the content root has exactly one child, adds a permanent fail-loud TESTHUB guard (aborts if
  the packaged Levels.arc MD5 equals local/Levels_merged_TESTHUB.arc), and prints the packaged
  Levels.arc size + MD5. Verified: canonical map A1BA5DB2F00FFA067A808753A2E1EAC5 (688,691,849 B)
  matches the published copy; 53-file package; item root = a single SoulvizierClassic folder.
  **Re-uploaded and verified LIVE (2026-07-08): a fresh steamcmd download of item 3759792705 shows the
  item root = a single SoulvizierClassic wrapper, so the "two mods" bug is resolved on the live item.**
  Scripts: scripts/package_workshop.ps1, scripts/upload_workshop.ps1.

## build36 content wave ROUND-3 GATE RECORD (2026-07-12 ~00:00, supersedes the round-1 block)
- Round-2 fixes all landed: Charon soul = S2 one-summon (ferryman allow entry); Kravmoloch soul
  grants its summon; dedicated per-boss hoards (Tantalus/Charon/Ephialtes; Mnemophage chestless);
  Dorus soul silent no-op FIXED (non-pcsafe source ref) + new _verify_dorus_soul_amendment gate.
- Round-3 fix: oarsman pet tiers clear the donor's dangling ALL_DamageScaling_Passive (bfca9a5)
  - the B-SUMMON-1 gate caught it on the written arz.
- BUILT: arz md5 f5df1f05786439f6ec51c0fcf92e76c6 (55,184,822 B) local/build36c/Database/;
  Text.arc md5 744b598100ef07cac3a3e023f77a1586.
- GATES: all inline fail-loud gates GREEN in-run (5 invariants, 3 pet gates, golem button,
  B-SUMMON-1, C6 Dorus gate, F1/F2[17 fam]/F3/F6[63+2158], clone-shape 12, spawn-eligibility 25,
  roaming sweep, player-skill anims). A9 render chain PASS standalone vs real art arcs (28
  upstream WARNs - the in-run FAIL was the missing-art environment artifact; Resources populated).
  Golden PASS (5 F5 waivers, 0 other). validate_tags PASS. Contracts: souls 0/0/0, summons 0 P0/P1
  (112 pre-existing P2), resources 0 P0 + ONLY the pre-existing anm_dreamcopy P1.
- Determinism: round-1 proved byte-identical independent rebuild; the convergence rebuild on main
  re-confirms for the final artifact.

## build36 CONVERGENCE GATE RECORD (2026-07-12, ready to deploy)
- Convergence: Vort red skin (FiretalonA x4) + crash mitigation (bloodbeast petLimit 8->4) +
  q_enslaver_warband placement (drxfirstxistion_connection, surveyed 100%).
- Record-diff vs amendment 1b4a8835: EXACTLY 5 changed (4 Vort baseTexture + 1 petLimit), 0 add/rm.
- arz md5 63ca7cf858e4f60f2f9bec8f9eb4ef8f; canonical Levels_merged.arc md5 b42be44f891775f110262da74d714b32; Text.arc md5 2af4ce386578ea144177a3227e07e048.
- Quests.arc UNCHANGED in build36 (comment-only build_quest_files.py diff; A5 is DB-record-level) ->
  reuse the deployed 194092 B Quests.arc (the pre-existing Rhodes-guard build failure is orthogonal).
- GATES: DB inline all green; Text golden intact (5 waivers); canonical blob-diff = exactly 1 blob
  (drxfirstxistion_connection, the warband); navmeshes 24/24 0x0a-stripped; contracts_map PASS
  (0 P0/P1, 4 MAP-REF-1 cleared, warband resolves, 3 pre-existing native-portal P2); contracts
  souls/summons/resources green (only pre-existing anm_dreamcopy P1).
- SHIP MAP = CANONICAL to both Steam + DEV (TESTHUB rebuild skipped - quota; canonical carries all
  content, WILL_TEST_GUIDE.md gives the canonical path to every boss).

## BL-AURA-RADIUS (Will 2026-07-12, design wave candidate for build38)
Increase the effect radius of ALL auras in the game so a player's aura bonuses reach their
pets in battle even when not standing adjacent, and reach allied players on screen in MP.
Scope: every aura-class skill across masteries + soul-granted auras + pet auras.
Design notes: TQ aura radius lives on the skill record (radius/targetRadius fields per
aura template); approach = audit all aura records -> propose per-aura radii (a flat
multiplier is the fallback; screen-scale ~= 30-45m world units) -> balance check vs
always-on party-wide uptime -> H/O golden-freeze waivers where trees are touched ->
implement as registry module (aura_radius.py) with a fail-loud audit gate listing every
touched aura + old->new radius. NOT started (quota); spec-first per the vet law.
> **AUDIT STAGE DONE 2026-07-14 (feat/aura-radius):** full template-driven enumeration of the
> effective DB (build40 golden `b33c5a44` over base) shipped as `docs/reports/b57_aura_radius.md`
> + machine roster `tools/aura_radius_roster.json` (generator `tools/audit_aura_radius.py`,
> read-only, re-runnable). 546 aura-class rows: 49 mastery / 66 soul-granted / 71 pet /
> 136 item-granted / 143 monster-only / 227 unreferenced dev copies; 86 rows carry NEGATIVE
> payload fields (aura-wide by template - widening spreads the malus; HOLD-flagged for Will).
> Player-reachable radii today span 0-23u; nothing reaches the 30-45u screen scale.
> Key mechanism: BuffRadiusToggled radius lives on the buffSkillName PAYLOAD record
> (Shadow Link payload drxbladehoningbuff = 3.0 vs vanilla bladehoningbuff 16.0, and it
> carries defensiveLife -5..-X, the malus Will asked about - CONFIRMED aura-wide, not
> self-only). 7 Hunting/Occult rows listed in the report's WILL VETO section.
> NEXT stage of this entry: the aura_radius.py module + H/O golden waivers + dry-run replay.
>
> **IMPLEMENTED-AWAITING-BUILD (round 1) 2026-07-14 (feat/aura-radius):** registry module
> `tools/patches/aura_radius.py` (runs after `boss_skill_fix`, before `visuals`) grows the RADIUS
> FIELD ONLY (`skillTargetRadius`) of **80 player-facing, positive-only friendly auras -> 36u**
> party screen-scale. No effect/damage/value touched. Roster-derived plan (546 rows):
> WIDENED 80, HELD 40 negative + 34 offensive (flag, Will decides), DEFERRED 13 base-only
> (need override-clone) + 4 field-creation (radius-0 self-buffs), SKIP 375 non-player.
> Pet-only target is 18u but 0 rows qualified this round (every positive pet aura also has a
> player-facing grant -> party 36u). H/O: 5 widened (Art of the Hunt, Call of the Hunt, Shadow
> Link, drx_demon_regen/cloak, shadowform), 2 held (Study Prey neg, Smoke Screen off). Shadow
> Link (Will's motivating case) widened 3->36 DESPITE its aura-wide defensiveLife malus, which
> now also reaches pets/MP allies within 36u - flagged in the report WILL VETO for Will's veto.
> Golden-freeze: 3 owner_approved_overrides waivers added to `tools/occult_hunting_golden.json`
> (drxartofthehuntbuff/drxcallofthehuntbuff 15->36, drxbladehoningbuff 3->36; radius field only).
> VERIFY (no heavy build): dry-run replay `tools/debug/b57_aura_radius_replay.py` PASS
> (80 modified, radius-only + intended-records-only diff, idempotent, verify() OK, negative test
> fails loud on Shadow Link); A7 golden gate PASS with the 3 waivers + correctly FAILS without
> them on exactly those 3 drifts; _check_registry 14 modules; py_compile green. Contracts/
> validate_tags structurally unaffected (0 records/tags/souls/summons added/removed).
> Report old->new table + held/deferred lists in `docs/reports/b57_aura_radius.md` (IMPLEMENTATION).
> Rides the next integration build. Round-2 candidates (Will-gated): the 74 HELD auras + the 17
> DEFERRED (base-only override-clone + field-creation scope decisions).
>
> **IMPLEMENTED-AWAITING-BUILD (round 2) 2026-07-14 (feat/aura-radius) - SUPERSEDES round 1:**
> adversarial vet caught that round 1 widened **8 offensive-payload records** as if friendly:
> a FRIENDLY-looking delivery (`Skill_BuffRadius`/`Toggled`) carrying an ENEMY-debuf payload
> (Class `SkillBuff_Debuf`) whose `skillTargetRadius` is DAMAGE/DEBUF reach (offensive fields are
> stored POSITIVE `offensiveXxxMin`, so the negative-detector missed them and the delivery class
> looked friendly). The 8: crushing vortex x3, earthquake (375 phys+stun), magebane (mana-burn),
> maddened-god aura (350 life), haronomi liferot SOUL DoT, ixion life-drain aura. Widening those
> enlarges combat power - a HOLD per the mandate. FIX: `aura_radius.py` `_payload_offensive`
> guard HOLDs any widen candidate whose edited payload Class is `SkillBuff_Debuf*`/
> `SkillBuff_Contageous` or carries `debufSkill=1` (checked live on the record being edited).
> New dispositions (546): **WIDENED 72** (down from 80; all 72 payloads are `SkillBuff_Passive`
> 70 + `SkillBuff_PassiveShield` 2, zero debuf), HELD 40 negative + **42 offensive** (34 delivery
> + 8 payload), DEFERRED 13 base-only + 4 field-creation, SKIP 375. The friendly
> `ixion_battlestandard_aurabuff` banner correctly STAYS widened (payload is `SkillBuff_Passive`,
> not a debuf). H/O UNCHANGED (none of the 8 are H/O): 5 widened + 2 held, same 3 golden waivers.
> VERIFY (dry-run replay vs golden `b33c5a44`): PASS - widen 72, radius-only + intended-records-only
> (72 modified, 0 added/removed, only `skillTargetRadius`), idempotent, `verify()` OK, negative test
> fails loud on Shadow Link; widen edit-class breakdown 70 Passive + 2 PassiveShield + 0 Debuf;
> `_check_registry` 14 modules; py_compile green (module + replay + audit). Roster regenerated
> (12 `proposal` fields updated to HOLD-offensive-PAYLOAD, ZERO structural drift vs the vetted
> round-1 roster); report `docs/reports/b57_aura_radius.md` rewritten (round 2, "positive-only"
> claim removed, the 8 moved into the HELD-offensive table with their offensive effect lists).
> Rides the next integration build.

## RCA RECORD 2026-07-12 evening: "quests blocked / doors closed" on _Toxeus = SAVE-SIDE, NOT a shipped bug
Byte-level verdict (Opus RCA + Sonnet log check, wf_2c9d497c): Steam AND DEV both carry pure
build36 (all 4 files == baselines; QUESTS registry 255 entries, zero add/remove/reorder vs
build33/34/35, door controllers inside the load window). NO regression shipped; NO build36b.
True cause: repeated crash-loop (ntdll 0xC0000005, SAME offset 0x00062a29 three times:
07-09 20:14, 07-12 01:34, 07-12 16:41 = genuine heap-corruption family, NOT our taskkill)
corrupting quest/door progress mid-save (backup folder shows 0-byte Quest.myw fingerprint).
RECOVERY (Will): (1) close TQ fully, restart Steam, ONE clean reload -> door controllers
re-evaluate tokens on level load, doors should reopen (save retains full 259-quest tree);
leave the crash area immediately, save in town. (2) If progress truly lost: restore
backups/characters/20260709_155432 (or local/save_backups/_Toxeus_2026-07-06_1.zip) with TQ
CLOSED, guarding against Steam Cloud overwrite. NEVER touch a live save.
STILL OPEN: the original Helos->Garden walk-through P0 (never shipped - the hotfix workflow
was stopped pre-implementation twice); relaunched as wf_6f65899d with TQ-session guards
(deploys wait for Will's game to exit rather than killing it). Crash deep-dump analysis
running separately (wf_20582269).

## P0 CRASH PINNED 2026-07-12 (supersedes the hound-summoner framing) - BL-NAVLOAD-HEAP
Deep minidump analysis (5 dumps, 32-bit re-decode): heap corruption detonates inside the
NAVMESH-LOAD path - ProcessRLTD (Engine 0x101f4ba0) streaming deeper blood-cave chambers;
identical ancestor chain in 5/5 dumps; two stable ntdll allocator offsets = delayed
detonation. MAP-SIDE (Levels.arc): the arz petLimit mitigation was provably a no-op (dumps
byte-identical across DB changes). All 39 injected navmeshes validate -> runtime condition;
leading trigger = grid-seam-chain co-residency / dtTileCache tile-coordinate collision
(CAVE_ENTRY_CHAIN_TRACE.md). Kill-events were coincidental timing.
FIX WAVE (next P0, heavy - after build37-dev + Will's tour): confirm first (Frida live-probe
names the culprit chamber, hooks documented in docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md;
or Page-Heap w/ Will's approval - registry change + OOM risk on 32-bit), then EITHER Fix B
cluster relocation to XZ-disjoint space (GRID_SHIFT + donor regen; entrance-seam risk at
Random09A/HiddenValley01 - preserve the abutment) OR interior GridEntrance transitions
between deep chambers (native streaming doors - NOT banned teleports - caps co-resident
navmeshes at 1-2). Player guidance meanwhile: save/portal-to-town often between chambers.
~~HYGIENE (separate, next DB build): 6 summoned-bloodhound dyingFxPak dangling refs ->
fxpak_deathfx_burst.dbr (real defect, NOT this crash).~~ **✅ CLOSED b91 (2026-07-28) - ALREADY
RESOLVED, no change was needed.** All 6 bodies (`b_bloodhound_33/34/35`, `c_bloodhound_40/42/44`)
already carry `dyingFxPak = records\drxcreatures\bloodhound\effects\fxpak_deathfx_burst.dbr` -
exactly this line's named target - and it resolves. **0 dangling `dyingFxPak` refs roster-wide.**
⚠️ The original report was almost certainly a MOD-ARZ-ONLY scan artefact: such a scan reports 7
false positives (4 `boss_daemonbull_yaoguai_*`, 3 `crowheroes\zilla*`) that all resolve in the
base-game DB. **Any dangling-ref audit MUST resolve against the UNION of the mod arz and
`<TQAE>\Database\database.arz`.** b91 ships the permanent invariant this debt never had:
`tools/patches/fx_dangling_cleanup.py` `verify()` fails the build loud if ANY record's
`dyingFxPak` stops resolving, and re-asserts the 6 bloodhound bodies specifically. See
`docs/reports/b91_debt_db.md` sec 2.

## BL-ENSLAVER-SMOKE (Will 2026-07-12, tour finding #1, P2 visual - ride the next DB build)
Toxeus the Murderer, Enslaver of Souls (black skeleton leader) renders a GREEN smoke aura;
Will: it must be BLACK. Fix: swap the shroud FX ref on the Enslaver monster record(s)
(wild roamer + warband leader variants; check the Devourer variant is unaffected) to the
proven dark/black smoke FX (the Long Nu-style dark_smoke chosen in WILL_DECISIONS for the
Helepolis). LAW: FX go on the monster record (charFxPakRunningNames-style), NEVER charFxPak
on SpawnPet skills (build28 crash trap). Verify in the built arz + A9 render chain; add to
Will's next tour list.

## ✅ CONFIRMED 2026-07-12: Victory Portal -> EPIC works in-game (Will: killed Hades, portal,
## spawned into Epic). A5/Act-5 fix fully closed - no further action.

## ✅ BL-ENSLAVER-SPAWNS - CLOSED b91 (2026-07-28). All 3 sub-fixes were ALREADY SHIPPED; the
## entry was simply never updated. Verified against the b90 golden arz + gated.

- **(1) DUPLICATE SPAWN - CLOSED, fixed by the b49 sweep.** Verified: **275** pool records name
  the Enslaver; **273 of 273** roaming pools carry him at `weight = 1` **and `limit = 1`** (the
  per-slot MAX-count cap = at most one per pool per trigger, structurally, at any party size
  regardless of `spawnMax` / draw-with-replacement). The other 2 are the whitelisted
  `q_enslaver_warband` / `q_yard_enslaver` set-piece pools (weight 100, multi-slot BY DESIGN).
  Breadth = the b49 `undead`-family restrict (273 pools, was ~1224); `_EN_SWEEP_K = 600` puts
  per-pool per-slot probability at `<= 1/24000`. The existing roaming-sweep gate already enforced
  weight/limit/probability/breadth/leak.
  **NEW GATE ADDED (the genuinely missing piece), `_verify_enslaver_roaming_sweep` check 3c -
  ADJACENCY ASSERTION:** `limitN` caps a **SLOT**, not a **RECORD**. If the Enslaver ever occupied
  TWO name slots of the same pool, each would independently honour `limit=1` and the pool could
  still surface him twice in one trigger - exactly Will's symptom, and invisible to every prior
  check (they all read a single `enl_idx`). Each swept pool must now name him **exactly once**
  across `name1..18` + `nameChampion1..18`.
  **Not DB-expressible:** two *independent proxies* placed near each other. Proxy placement lives
  in `Levels.arc`, and a multi-pool proxy picks exactly ONE pool per trigger (b38-proven), so pool
  reachability says nothing about spatial adjacency. Post-b49 probability ~1e-7 per adjacent pair.
- **(2) SPAWN RATE - CLOSED BY RULING R-18** (Will forbade a rate change on the roaming
  frequency). Untouched. No action is the correct action.
- **(3) MARAUDER TANKINESS - CLOSED, already fixed in `_create_enslaver`** with Will's report
  quoted in the code: `defensiveLife 100 -> 40` (the named root cause - FULL vitality immunity),
  `defensivePierce 80 -> 40`, `defensivePhysical 30 -> 12`, `characterLife 13k/18k/24k ->
  10k/14k/18k`, **DPS deliberately untouched** (`handHitDamage` 300/380 - "increase strength,
  never nerf"). Confirmed present in the shipped arz.
  **Roster measurement** (`um_enslaver_marauder_99`, Champion, `charLevel [40,68,100]`): his
  `armor_passive` ladder `78/226/468` is **level-appropriate and in-band** (78.9th / 78.5th /
  91.6th percentile of 881 Champions; compare `svc_vashkarr_lance` at `charLevel 38/56/71` ->
  `75/204/405`). The outlier is `characterLife` (**99.9th percentile** at Epic: 14000 vs Champion
  median 584 / p90 2512) - the one axis the fix already cut.
  **NEW GATE ADDED, `_verify_enslaver_roaming_sweep` check 0b:** nothing gated any of it, so a
  later wave could quietly restore the wall. CEILINGS on `defensiveLife`/`defensivePierce`/
  `defensivePhysical`/`characterLife` **and FLOORS** on `handHitDamageMin/Max`, so the two halves
  of Will's ruling cannot drift apart (no re-walling, and no paying for a cut by gutting threat).
- **⚠️ HONEST OPEN QUESTION -> BL-b91-DEBT-3 (needs Will, not code):** the sub-fix (3) change
  landed AFTER Will's 2026-07-12 report and has **never been confirmed in-game**. At 14000 Epic
  life he is still the 99.9th percentile Champion, four spawn at once, and they drop nothing.
  Whether that now reads as "a killable elite" or still "a sponge" is a **playtest call, not a
  data call** - b91 deliberately did NOT invent a second cut on top of a fix Will has not judged.
  The new ceilings make any future cut a one-line change.
- Report: `docs/reports/b91_debt_db.md` sec 5.

**ORIGINAL REPORT (kept for the record):**

## BL-ENSLAVER-SPAWNS (Will 2026-07-12, tour finding #2, P1 balance - post-tour fix round)
In EPIC's first combat area Will met TWO side-by-side "Toxeus the Murderer, Enslaver of
Souls", each with 4 Enslaved Shadow Marauders, and the marauders took ~0 damage.
THREE fixes, one wave:
(1) DUPLICATE SPAWN: the build36 roaming-rare sweep lets adjacent proxies both roll the
    Enslaver. Audit every proxy/pool he was added to; prevent side-by-side duplicates
    (spacing the pools he's in / removing him from adjacent proxies of the same area).
(2) SPAWN RATE: reduce (Will explicit). He should be a RARE encounter, not a doorstep
    greeter in the first Epic field. Consider act/area gating of the roam pools entirely.
(3) MARAUDER TANKINESS: "deployed-demon strength" law + Epic difficulty scaling = near-
    immune marauders. Rebalance so they are killable elites in Epic/Legendary (check
    armor/resist/absorption stacking per-difficulty; they drop nothing, so sponge = pure
    frustration). Keep their DPS threat; cut their effective-HP wall.
Verify vs the warband placement too (the static blood-cave warband keeps its 4 marauders;
these fixes target the ROAMING variant's pools + per-difficulty marauder defenses).
