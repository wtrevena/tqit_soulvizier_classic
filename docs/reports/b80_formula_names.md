# B80 - Formula Name Audit (round 1)

> Will's report (2026-07-16, verbatim): "Also Mythic Formula - Crystalline Mask is the
> formula name for the formula which makes Galefury. the Mythic Formula has the wrong
> name." Ledger: `docs/WILL_RULINGS.md` R-41. Branch `fix/formula-names`, worktree
> `.claude/worktrees/formula-names`, base `main` 33d25d6 (then fast-forwarded to
> `5f139c3` to pick up the WILL_RULINGS ledger commit, no code conflict). Reference arz:
> build45 `work/SoulvizierClassic/Database/SoulvizierClassic.arz` md5
> `917d9047d2281284f5fd5e9a163b9c5c` (read-only).

## TL;DR

One genuine bug, found and fixed: `records\drxitem\supra\recipes\ar_hunter_helm_
formula.dbr` (the Mythic Formula that crafts Galefury) had its `description` field
pointed at `tagRecipe_ar_caster_helm` - the tag `ar_caster_helm_formula.dbr` (both its
`recipes\` and `zrecipes\` copies) legitimately uses for the real Crystalline Mask
formula. Fixed by repointing the field to `tagRecipe_ar_helm_fix` - a tag SV 0.98i's
own `Text_EN.arc` already ships, correctly worded ("^rMythic Formula - Galefury"), that
had simply never been wired to any record. Zero Text-pipeline change needed.

A full sweep of every one of the mod's 245 `ItemArtifactFormula` records (42 obtainable
+ 203 orphaned/unreachable shells) found **exactly this one** name-text mismatch - no
others, wired or unwired. A structural gate (DB-build `verify()`, no Text.arc
dependency) and a full text-resolved standalone validator (build-pipeline gate, wired
into `bootstrap_working_mod.ps1`) both now guard against a regression or a future
recurrence of the same bug class. Both gates were negative-tested against a
freshly-planted synthetic mismatch and against the raw pre-fix bug itself.

## The named instance - root cause

`ar_hunter_helm.dbr` ("Galefury", a Protective_Head DRX supra item, verified in
`docs/reports/sv_mythic_nonweapon_hunt.md` and `docs/UBER_WEAPONS_AUDIT.md` line 97/105
- the latter had already NOTICED this exact label quirk on 2026-07-07 but concluded
"not a functional defect... matches SV 0.98i" without checking whether SV itself had
already authored the fix) is crafted by `records\drxitem\supra\recipes\ar_hunter_helm_
formula.dbr`. That formula's `description` field:

| Field | Before | After |
|---|---|---|
| `description` | `tagRecipe_ar_caster_helm` -> `^rMythic Formula - Cystalline Mask` | `tagRecipe_ar_helm_fix` -> `^rMythic Formula - Galefury` |

`tagRecipe_ar_caster_helm` is the tag `ar_caster_helm_formula.dbr` (both `recipes\` and
`zrecipes\` copies, which craft the real Crystalline Mask, `ar_caster_helm.dbr`)
legitimately use - confirmed by decoding all three records directly (`local/tmp_extract/
records/drxitem/supra/{recipes,zrecipes}/ar_caster_helm_formula.dbr`, both `description=
tagRecipe_ar_caster_helm`). So `ar_hunter_helm_formula.dbr` was simply pointed at the
WRONG (but real, resolving) tag - a donor/copy-paste tag never repointed to its own
identity, exactly the bug class the task brief hypothesized (though NOT from the b66
wave - see "Not a b66 defect" below).

**The fix already existed, unused.** SV 0.98i's own `upstream/soulvizier_098i/Resources/
Text_EN.arc` (`xuniqueequipment.txt`) ships a SECOND recipe tag:

```
tagRecipe_ar_helm_fix=^rMythic Formula - Galefury
```

byte-verified directly against the upstream arc (not inferred). This tag is genuinely
orphaned - a repo-wide grep of every `.py`/`.dbr` for `tagRecipe_ar_helm_fix` finds
**zero references** anywhere in the codebase, before this fix. It already flows into
the shipped `Text.arc` today (it is one of the SV098i per-file tags `build_text_arc.py`
emits unconditionally for every entry in `xuniqueequipment.txt`, referenced or not) -
confirmed present, byte-identical, in the currently-committed `local/Text.arc`
(`tagRecipe_ar_helm_fix=^rMythic Formula - Galefury`).

**Fix:** repoint `ar_hunter_helm_formula.dbr`'s `description` from `tagRecipe_ar_
caster_helm` to `tagRecipe_ar_helm_fix`. Zero Text-pipeline change required - the
correct tag text already ships. Per the standing "re-point over edit-a-shared-tag"
preference, `tagRecipe_ar_caster_helm` itself is left untouched (it must keep saying
"Crystalline Mask" for the two records that legitimately use it).

### Not a b66 defect

The task brief's working hypothesis was that the b66 uber-formula wave's 24 reused
`zrecipes\` shells were the likely bug class. Verified false for this instance:
`ar_hunter_helm_formula.dbr` lives ONLY in `recipes\` (no `zrecipes\` copy exists for
it), it is part of the ORIGINAL 25 pre-existing craftables (Galefury/`ar_hunter_helm`
predates b66 entirely - it is not among b66's 14 new weapons), and b66's own module
(`tools/patches/uber_orphan_weapons.py`) never touches `ar_hunter_helm_formula.dbr` or
`ar_hunter_helm.dbr` (grep-verified). This is inherited SV 0.98i/DRX authoring debt,
not a port or b66 regression.

### Tag-sharing analysis (why re-point, not edit)

| Formula record | `description` tag | Crafts |
|---|---|---|
| `recipes\ar_caster_helm_formula.dbr` | `tagRecipe_ar_caster_helm` | `ar_caster_helm.dbr` (Crystalline Mask) - legitimate |
| `zrecipes\ar_caster_helm_formula.dbr` | `tagRecipe_ar_caster_helm` | `ar_caster_helm.dbr` (Crystalline Mask) - legitimate |
| `recipes\ar_hunter_helm_formula.dbr` | `tagRecipe_ar_caster_helm` (BEFORE) | `ar_hunter_helm.dbr` (Galefury) - **the bug** |

`tagRecipe_ar_caster_helm` is shared by 3 formulas, 2 of which craft the identical
result (the recipes\\/zrecipes\\ twin pattern used throughout the supra tier) and one
(the bug) which crafts a DIFFERENT result. Editing the shared tag's text would have
broken the two legitimate Crystalline Mask formulas; re-pointing the buggy formula onto
its own tag (which, as it happens, already existed correctly) is the only fix that
touches nothing else. This "shared tag whose sharers craft different results" pattern
is exactly what the new structural gate (below) checks for.

## Full-catalog sweep

Swept **every** `ItemArtifactFormula` record in the reference arz (245 total) via a
scratch script that: (1) finds every formula wired into `supra.dbr` / `supra_special.
dbr`'s `lootNameN` slots (the 42 obtainable/craftable ones - 28 pre-existing +
14 added by b66), (2) reconstructs the exact tag-resolution map the build produces
(SV098i `Text_EN.arc` per-file pass + `uber_soul_tags.txt` + the `build_text_arc.py`
fix-block, i.e. the same inputs `build_text_arc.build_modstrings()` uses - no separate
Text.arc build needed for the sweep), (3) for each formula, resolves `description` ->
formula display text and `artifactName` -> result record -> `itemNameTag` -> result
display text, strips the formula-type prefix (`"<Mythic|Arcane> Formula - "`) and any
leading `^X` color code from both sides, and compares the remaining name text.

### The convention (derived empirically, not assumed)

Two self-consistent sub-conventions coexist in the catalog - the bug-hunt only cares
about the NAME TEXT after the dash matching the result's own name, not which of these
two styles is used:

| Family | Formula text pattern | Result text pattern | Count |
|---|---|---|---|
| Original 25 `recipes\` formulas | `^rMythic Formula - <Name>` | `^r<Name>` (matching color) | 24 correct (+1 bug) |
| b66 `zrecipes\` non-thrown (10) | `Mythic Formula - <Name>` (no color) | `<Name>` (no color) | 10/10 correct |
| b66 `zrecipes\` thrown family (4: Charon's Toll, Hati, Last Word, Sanguine Orbit) | `Arcane Formula - <Name>` (no color) | `<Name>` (no color) | 4/4 correct |

(A naive "must be `^rMythic Formula - X`" check against ALL 42 would have produced 17
false positives on the b66 family purely from the color/prefix-word style difference -
caught and corrected before finalizing the sweep logic; see the `formula_name_clean`
vs `result_clean` comparison in `tools/validate_formula_names.py`.)

### Results

| Metric | Count |
|---|---|
| Total `ItemArtifactFormula` records in the mod | 245 |
| Obtainable (wired into `supra.dbr`/`supra_special.dbr`) | 42 |
| Unwired/orphaned shells (unreachable, e.g. spare `zrecipes\` dups, base-game Arcane Formula families) | 203 |
| N/A - result has no fixed `itemNameTag` (`artifact_plus2.dbr`, `artifact_mortoksskull.dbr` - `ItemArtifactSupra` class artifacts whose only identity IS the formula name) | 2 |
| Checkable obtainable formulas | 40 |
| **Mismatches found (obtainable)** | **1** (Galefury/Crystalline Mask - fixed) |
| **Mismatches found (unwired/orphan)** | **0** |

Also verified: every `Mythic Formula -`/`Arcane Formula -` (dash-separated, this
mod's DRX-supra convention) tag in the entire built modstrings (124 tag hits) belongs
to one of the 42 obtainable + 1 orphaned-but-correct (`tagRecipe_ar_helm_fix`) +
1 unrelated chest-reward fragment (`tagSQECFullText`, a generic "Rewarded: Mythic
Formula" template string, not a specific formula name). The base game's own 75
`xtagFormulaDescription0NN = Arcane Formula ~ <Name>` tags (tilde separator, native TQ
Artifact system, untouched by this mod) are a separate, pre-existing, out-of-scope
family - confirmed correct by construction (base-game content) and excluded from the
mod's naming-convention gate.

### WILL-CONFIRM list

**Empty.** Every mismatch found (there was exactly one) was an unambiguous bug (a
formula pointed at a tag belonging to a different result, with SV 0.98i's own text
already carrying the correct, unused fix) - not a case where SV/amgoz1 deliberately
named a formula differently from its result. No item needs Will's design call.

## Fix implementation

- **`tools/patches/formula_names.py`** (new registry module, `MODULE_NAME = "B80: ..."`,
  registered in `tools/patches/__init__.py` REGISTRY right after `uber_orphan_weapons`
  - same supra-formula-name domain, disjoint record (touches only the pre-existing
  `recipes\ar_hunter_helm_formula.dbr`, never any b66 `zrecipes\` record)):
  - `apply(db, tags)`: repoints the one field. Idempotent (no-op if already fixed) and
    fail-loud (`SystemExit`) if the field holds any value other than the known-wrong or
    known-fixed string - never blind-overwrites.
  - `verify(db, tags)` (**the GATE**, runs post-finalization over the FINAL assembled
    db, per the registry contract): (a) regression guard - the known-wrong tag must be
    gone; (b) `find_tag_sharing_offenders()` - every `records\drxitem\supra\*`
    formula's `description` tag, when shared by 2+ formulas, must be shared ONLY by
    formulas crafting the SAME `artifactName`. A tag shared across formulas crafting
    DIFFERENT results is exactly this bug class and fails the build loud. Pure db-field
    check, no Text.arc dependency (works reliably at DB-build `verify()` time, before
    Text.arc exists). Scoped to `records\drxitem\supra\` specifically (not a mod-wide
    check) because the identical "shared generic tag" pattern is legitimate base-game
    design elsewhere (e.g. the 12 tiered lesser-experience-potion formulas share one
    generic tag by design; the base game's own `xtagFormulaDescription*` Arcane Formula
    family is a different, untouched namespace) - scoping to supra keeps the gate
    false-positive-free (verified: the unscoped version below flags 4 false positives
    from base-game content; the supra-scoped version flags exactly 1, the real bug).
    `TAG_SHARING_WAIVERS = {}` - empty (no SV-intended exception exists today; documented
    for a future genuine case).

- **`tools/validate_formula_names.py`** (new standalone build-time validator, matching
  `tools/validate_tags.py`'s pattern): the full TEXT-RESOLVED sweep (the convention
  described above) run against the WRITTEN `.arz` + built `Text.arc`. Catches what the
  structural gate cannot (a hand-typo'd BRAND-NEW tag with no sharing involved).
  `NAME_TEXT_WAIVERS = {}` (empty), `NO_FIXED_NAME_RESULTS` = the 2 `ItemArtifactSupra`
  artifacts. `Usage: py tools/validate_formula_names.py <final.arz> <final_text.arc>`,
  exit 0/1/2.

- **`scripts/bootstrap_working_mod.ps1`**: new Step 4b-2, wired immediately after the
  existing `validate_tags.py` gate (Step 4b) - runs `validate_formula_names.py` against
  the staged `.arz`/`Text.arc` and fails the bootstrap loudly on any mismatch.

- **`tools/debug/negtest_formula_names.py`** (matching the `negtest_container_shape.py`
  convention): 4 subtests against `formula_names.py` - positive-2 (raw pre-fix arz must
  FAIL `verify()`), positive-1 (post-`apply()` must PASS), positive-3 (idempotent
  re-`apply()` still PASSes), negative-1 (a FRESH synthetic mismatch, independent of the
  real bug - `ar_melee_helm_formula.dbr`'s description repointed onto `ar_caster_legs_
  formula`'s tag - must be caught by `find_tag_sharing_offenders()`). All 4 behaved as
  specified.

## Verification

**Fast gates:** `py -m py_compile` on all 4 changed/new files - PASS.
`py tools/patches/_check_registry.py` - PASS (27 modules, order hash
`15fe74154afe6f8f2518a376dc69a789e8244eb086cbfdfd250f779b99d365ca`).

**Negative test** (`tools/debug/negtest_formula_names.py` against the reference arz):
all 4 subtests OK -
```
[OK] positive 2 (raw pre-fix state): got=FAIL expected=FAIL
[OK] positive 1 (post-fix): got=PASS expected=PASS
[OK] positive 3 (idempotent re-apply): got=PASS expected=PASS
[OK] negative 1 (planted mismatch): got=FAIL expected=FAIL
ALL SUBTESTS BEHAVED AS SPECIFIED.
```
A second, independent negative test against the standalone TEXT-based validator
(`tools/validate_formula_names.py`) - mutate a written copy of the FIXED arz to plant a
fresh mismatch (`ar_melee_helm_formula.dbr` -> `ar_caster_legs_formula`'s tag), write
to disk, re-run `check()` against it and the real Text.arc: correctly reported
`rc=1` / "formula says '^rMythic Formula - Leggings of the Cosmos' but result
(`ar_melee_helm.dbr`) is named '^rTitan Crest'".

**Full scratch build** (`py tools/build_svc_database.py` with all 3 upstream sources +
base game database, output to `.claude/worktrees/formula-names/local/scratch_build/`,
never touching the read-only reference or `work/`): completed clean, `EXIT=0`, no
`Traceback`/`SystemExit`/`ERROR` anywhere in the log. `formula_names` ran as module
25/27 in the registry: `apply()` "modified 1 record(s), 0 tag(s)"; post-finalization
`verify()` "[B80] supra formula-name tag-sharing gate: PASS (no cross-result tag
sharing)".

New arz: `9e3c1ad0d5c5d3ba2552fe097f54e02c` (vs reference `917d9047d2281284f5fd5e9a163b
9c5c`).

**Record-diff vs the reference arz** (`tools/record_diff.py`, `--fields`):
```
ADDED   : 0
REMOVED : 0
MODIFIED: 1
  ~ records\drxitem\supra\recipes\ar_hunter_helm_formula.dbr  (1 field(s))
      description: ['tagRecipe_ar_caster_helm'] -> ['tagRecipe_ar_helm_fix']
```
Exactly the intended name-tag re-point. Zero strays.

**Text.arc build** (`py tools/build_text_arc.py`, i18n de-clobber enabled against the
Steam base `Text_EN.arc`): completed clean; A7 golden freeze guard PASS ("Occult/Hunting
golden state intact", 90 waived - all pre-existing, none touching formula names).

**`validate_tags.py`** (against the new arz + Text.arc): `RESULT: PASS` - 347 mod-owned
referenced tags all present; the 2 pre-existing base/SV `tagNewMonster*` WARNs are
unrelated backlog noise, not introduced here.

**`validate_formula_names.py`** (the new B80 standalone gate, against the new arz +
Text.arc): `Checked 40 obtainable formula(s) (42 wired total, 2 N/A - no fixed result
name) / All obtainable formula names match their results. PASS`.

**A7 golden freeze guard**: PASS at both the DB-build stage and the Text-build stage
(84 then 90 waived drifts respectively, all pre-existing owner-approved waivers from
other waves - zero new/unwaived drift).

**Chain gate** (the enslaver-chain anti-oscillation guard in `enslaver_pet_fx.verify()`)
and every other registry module's `verify()` hook: all ran clean as part of the full
registry post-finalization verify phase (`verify hooks OK: mastery_bg_render,
oh_pane_art, skill_quality, toxeus_suite, ..., uber_orphan_weapons, formula_names,
mastery_sv_alignment`) - no `SystemExit` anywhere.

**Contracts (souls/summons/resources)**: run twice with identical inputs except the
`.arz` (reference vs the fixed scratch build), both against the same staged Text.arc/
Levels.arc/Quests.arc/Resources - **byte-identical violation set both times**
(`4904 violations (0 P0, 1252 P1, 3652 P2)`), proving this change introduces ZERO
delta to the contract suite. The suite's own current FAIL state (1252 P1) is a
**pre-existing condition** unrelated to this fix (map/quests contracts were not
re-run - this wave never touches `Levels.arc`/`Quests.arc`; the 1252 P1 in souls/
summons/resources predates this branch and does not match the P1=0 the BACKLOG's
build45 gate record claims for the same reference arz, likely artifact-snapshot
staleness between when that record was written and when `work/SoulvizierClassic/
Resources/{Text.arc,Levels.arc}` were last regenerated - flagged to BACKLOG DEBT below,
out of scope to chase down for a formula-name-focused wave). Map contracts were not
re-run for the same reason (zero map/quest files touched by this branch).

**Idempotent**: proven by the negative test's positive-3 subtest (`apply()` called
twice on the same db; second call is a no-op, `verify()` still PASSes) and separately
by the full scratch build itself running `formula_names.apply()` exactly once per the
registry contract with no double-application hazard.

## Files touched

- `tools/patches/formula_names.py` (new)
- `tools/patches/__init__.py` (REGISTRY: appended `formula_names` after `uber_orphan_weapons`)
- `tools/validate_formula_names.py` (new)
- `tools/debug/negtest_formula_names.py` (new)
- `scripts/bootstrap_working_mod.ps1` (new Step 4b-2 gate wiring)
- `docs/reports/b80_formula_names.md` (this report)
- `docs/BACKLOG.md` (status entry + BACKLOG DEBT item for the contracts staleness flag)
- `docs/WILL_RULINGS.md` (R-41 -> IMPLEMENTED)

## Mismatch table (compact)

| Formula | Crafts | Old name | New name |
|---|---|---|---|
| `records\drxitem\supra\recipes\ar_hunter_helm_formula.dbr` | Galefury (`ar_hunter_helm.dbr`) | `^rMythic Formula - Cystalline Mask` (shared with the real Crystalline Mask formula) | `^rMythic Formula - Galefury` (own, previously-orphaned SV098i tag `tagRecipe_ar_helm_fix`) |

## BACKLOG DEBT (per WILL_RULINGS law #4)

- Contracts suite (souls/summons/resources) currently shows 1252 P1 against the
  reference `work/SoulvizierClassic/Resources/{Text.arc,Levels.arc,Quests.arc}` tree,
  vs the 0 P1 the BACKLOG's BUILD45 GATE RECORD claims for arz `917d9047`. Likely
  cause: the staged `Text.arc`/`Levels.arc` under `work/SoulvizierClassic/Resources/`
  are stale relative to when that gate record was written (mtimes: `Text.arc` Jul-16
  01:59, `Levels.arc` Jul-16 09:09, vs the reference arz's Jul-16 19:47 - hours of other
  waves may have landed on the arz without a matching Resources restage). Not caused by
  and not fixed by this branch (proven: byte-identical violation set on the SAME
  Resources tree with vs without this fix applied). Needs a fresh full bootstrap +
  restage + re-run of `run_contracts.py` by whichever lane owns the next full
  integration, to re-establish ground truth.
