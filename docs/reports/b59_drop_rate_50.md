# b59 - Soul drop-rate cut for randomly spawning monsters (66% -> 50%)

**Lane:** `feat/soul-drop-50` (DROP-RATE, round 1)
**Date:** 2026-07-14
**Directive (Will, verbatim):** "Cut all soul drop rates for randomly spawning monsters to 50% from current 66%."
**Ground-truth baseline:** build40 GOLDEN arz `b33c5a447f3a8ca652c14f78d4ad1dd4` (55,351,206 B, 51,029 records).
**Method:** dry-run replay + classifier verification vs golden (NO heavy build). Gate: `tools/verify_soul_drop_rates.py --gate` -> EXIT 0.

---

## 1. Where the 66 lives (ground truth)

The release soul-drop model is set in TWO places, both `chanceToEquipFinger2` on the monster record:

1. **`tools/build_svc_database.py::wire_souls_to_monsters(db)`** (sole functional call at line ~3414,
   BEFORE `apply_all_extended_patches`). Historically it gave the whole non-boss **Hero/Quest class a
   single `rare_chance=66`** and **farmable act Boss = 25**. This is the class Will's directive targets.
2. **`tools/apply_svc_patches.py` modules** author the apex PLACED ubers (Vashkarr, Broodmother,
   Enslaver, Tantalus, Blood Toxeus, the Four Generals, Hades Marshal, ...) AFTER wire_souls, each
   setting its own 66 / 25 / 0. wire_souls never rates these (they are created later), so this change
   does NOT touch them.

`apply_svc_patches._force_100_pct_soul_drops(db)` overrides `chanceToEquipFinger2 -> 100` in **TESTING**
mode, but ONLY on records already `has_soul AND chance>0` (the yeti-fix gate). RELEASE (repo default,
`SVC_RELEASE_DROPS=1` / no override) keeps the tuned 66/25 rates. The Steam/public build ships RELEASE.

---

## 2. The split rule (roster-derived, no hardcoded names)

Will's 66-class is split by **spawn provenance read from the db roster** (`soul_spawn_provenance_sets`),
resolved by `soul_drop_rate()` in precedence order:

| Precedence | Class | Rate | Source of truth |
|---|---|---|---|
| 0 | `_SOUL_PLACED_OVERRIDE` / `_SOUL_RANDOM_OVERRIDE` | 66 / 50 | **Will's per-record veto** (empty by default) |
| 1 | FARMABLE ACT BOSS (Boss-class, non-`um_`) | **25** UNCHANGED | `monsterClassification==Boss` and not `um_`/`boss_` path |
| 2 | QUEST / story boss (`monsterClassification==Quest`) | **66** UNCHANGED | classification |
| 3 | PLACED uber (in a `records\drxmap\proxy*` placement record) | **66** UNCHANGED | placement roster |
| 4 | **RANDOM roaming hero** (in a base-game `records\proxies*` `name*/nameChampion*` slot) | **50** ← Will's cut | population-pool roster |
| 5 | unreferenced (dead/placed-in-level, not proven random) | **66** UNCHANGED (safe default) | fall-through |

**RANDOM = the roaming hero roster**: the SV uber tier (`um_camelbane`, `um_morth`, ...) plus the plain
hero roster (`hero_*`, `us_*`, `u_*`) that spawn via random hero slots in the base-game population pools
under `records\proxies {egypt,greek,orient,boss,custom,quest}\pools\*`. **PLACED = dedicated
encounters** (quest/story bosses + apex ubers behind `q_*_lone` / warband placement proxies) - untouched.

**Why this is faithful and safe:** a monster that spawns randomly MUST be referenced by a spawn pool
(that is the only random-spawn mechanism). So "not in a random pool" == placed-in-level or
dead/unreferenced, both of which keep 66. A placed or quest encounter is therefore **never over-cut**;
the only under-cut is dead records, where the drop is moot.

---

## 3. FULL before/after release rate table by monster class (dry-run replay vs golden b33c5a44)

Delta model = `50 iff (golden==66 AND classifier==RANDOM) else golden`. This is exactly what
`wire_souls_to_monsters` emits for the records it owns; module-authored apex bosses keep their golden
value (they are not RANDOM-class). 1,280 soul-droppers total; **377 records change 66 -> 50, nothing else moves.**

| Class bucket | before -> after | count | changed? |
|---|---|---|---|
| **RANDOM_HERO(50)** | 66.0% -> **50.0%** | **377** | **CHANGED (Will's cut)** |
| RANDOM_HERO(50) | 0.0% -> 0.0% | 316 | gated stays 0 |
| QUEST(66) | 66.0% -> 66.0% | 98 | unchanged |
| PLACED_UBER(66) | 66.0% -> 66.0% | 15 | unchanged |
| PLACED_UBER(66) | 25.0% -> 25.0% | 1 | unchanged |
| PLACED_UBER(66) | 0.0% -> 0.0% | 4 | gated stays 0 |
| FARMABLE_BOSS(25) | 25.0% -> 25.0% | 111 | unchanged |
| FARMABLE_BOSS(25) | 10.0% -> 10.0% | 12 | unchanged |
| FARMABLE_BOSS(25) | 66.0% -> 66.0% | 5 | unchanged (module-set Boss@66) |
| UNREFERENCED(66) | 66.0% -> 66.0% | 234 | unchanged (safe default) |
| UNREFERENCED(66) | 25.0% -> 25.0% | 1 | unchanged |
| UNREFERENCED(66) | 0.0% -> 0.0% | 106 | gated stays 0 |
| **TOTAL** | | **1280** | **377 changed** |

**dry_run_diff:** exactly **377 records 66 -> 50**; 0 records changed in any other class or direction.

The 377 cut records are the roaming roster: **270 `um_`** (SV uber tier), **48 `hero_`**, **32 `us_`**,
**4 `u_`**, plus a few `am_`/`qm_`/other. Spot-checked cuts: `um_camelbane_32`, `um_morth_18`,
`um_crowboar_09`, `hero_grom_28`, `u_bloodwing_12` -> all 50.

---

## 4. Build-order stability (the golden replay is faithful to the real build)

`wire_souls_to_monsters` runs on the RAW merged db (before modules). `apply_svc_patches` later CREATES
5 `svc_`-named proxy pools (e.g. `svc_wyrmhorde_*`). Concern: could a record be cut only because a
module pool that does not exist at wire-time classifies it RANDOM?

**Proven NO.** All **383** soul-droppers @66 sitting in a random proxy pool are referenced by **>=1
BASE-GAME pool** (present at wire_souls call-time); **0** are referenced only by module-authored (`svc_`)
pools. So the actual build cuts exactly the same set the golden replay predicts. (383 in-pool candidates
-> 377 after PLACED/QUEST/BOSS precedence keeps 6 at 66.)

---

## 5. Testing mode unchanged + survives finalization (both modes)

Ran the REAL `apply_svc_patches._force_100_pct_soul_drops` over BOTH the golden (release-before) and the
golden+delta (release-after) states:

- **854** soul-droppers -> **100** in testing (identical set in both states, since 50 and 66 are both `>0`).
- **426** gated-off (`chance==0`, incl. the Legion lane's ZEROED stages) stay **0** in both modes - the
  `chance>0` forcer gate the Legion fix depends on is intact.
- `chanceToEquipFinger2` is **identical on every creature** after the forcer in both states => the split
  is **release-only**; TESTING is byte-unchanged. **survives_finalization: PROVEN.**

---

## 6. Notable / sensitive records the rule cuts (⚠️ flagged for Will's veto)

These sit in base-game random pools, so by Will's own rule they ARE randomly spawning and go to 50. To
spare any one, add its basename to `_SOUL_PLACED_OVERRIDE` in `build_svc_database.py` (one line):

- **`um_legion_28`** -> 50. Directive EXPLICITLY OKs this (spawns via random eurynomus champion pools).
  The `feat/legion-soul-stages` lane owns Legion per-record; its ZEROED stages stay 0 in both modes.
- **`um_toxeus_21`** ("Main / green Athens Toxeus") -> 50. A module boosts its SOUL ITEM stats but NOT
  its drop chance, so wire_souls still owns the rate. The apex superboss `um_bloodtoxeus_99` is
  module-owned and **stays 25 (untouched)**.
- **`qm_aniketos_9/10/11`** -> 50. Aniketos is map-injected AND in random pools.

The named PLACED apex ubers are all correctly KEPT: `um_vashkarr_99`=66, `um_broodmother_99`=66,
`um_toxeus_enslaver_99`=66, `um_bloodtoxeus_99`=25, `um_tantalus_99`=0(gated), `svc_um_hadesmarshal_80`=66,
Four Generals quest hero `xsq27_namedhero_a_machae_45`=66. **ZERO placed apex uber over-cut.**

---

## 7. Gates

- **contracts:** `run_contracts.py --only souls` (full context, main tree) => **GATE PASS, 0 violations**
  (10 contracts). This change touches only monster `chanceToEquipFinger2` floats, not soul items /
  meshes / skills, so souls/summons/resources domains are unaffected. (Running against a bare arz with
  no base-game DB / resource arcs reports spurious mesh/skill "unresolved" noise - environment, not this change.)
- **verify gate:** `py tools/verify_soul_drop_rates.py <golden> --gate` => **EXIT 0** (rate table +
  invariants + testing survival + 13 spot tests).
- **negative test:** override-veto negtest in the verify gate => 5/5 flips correct + override sets empty
  by default (shipped rates == pure roster verdict). Proves `_SOUL_PLACED_OVERRIDE`/`_SOUL_RANDOM_OVERRIDE`
  win over every roster branch (incl. the Boss/25 gate) and are a strict no-op when empty.
- **py_compile:** `build_svc_database.py` + `verify_soul_drop_rates.py` OK.
- **caller wiring:** sole call `wire_souls_to_monsters(db)` uses defaults `random_chance=50, placed_chance=66,
  boss_chance=25`; no caller passes the legacy `rare_chance` (which would collapse the split to a single rate).

---

## 8. Files changed

- `tools/build_svc_database.py` - split helpers (`soul_spawn_provenance_sets`, `soul_drop_rate`,
  `_soul_is_farmable_boss`, `_soul_record_basename`), `wire_souls_to_monsters` signature
  `random_chance=50/placed_chance=66/boss_chance=25` (+ `rare_chance` back-compat), per-record veto knobs
  `_SOUL_PLACED_OVERRIDE`/`_SOUL_RANDOM_OVERRIDE` (empty), prominent split-rule + veto documentation.
- `tools/verify_soul_drop_rates.py` - dry-run replay gate: rate table, invariants, real-forcer
  testing-survival proof, spot tests, override negative test.
- `docs/reports/b59_drop_rate_50.md` - this report.

---

## 9. Residual / for the vet

- The split is **release-only** and **build-order-stable** as proven above; the true finalization test
  is a real DB build (`py tools/build_svc_database.py ...`) in BOTH modes with a record-diff vs golden,
  expecting **exactly the 377 records** at 50 (release) and all soul-droppers at 100 (testing). Deferred
  here per the concurrency constraint (no heavy builds); recommended at the merge/integration gate.
- Cross-lane: `feat/legion-soul-stages` (zeroed 3 Legion stages) and `feat/souls-quality` edit per-record
  fields; this change is the RATE constant/wiring only. No record collision (Legion zeroed stages stay 0
  under this split; souls-quality edits soul-item stats, not monster drop chance).

---

## 10. ROUND 2 - vet NO-GO fix (2026-07-15/16, `create_uber_souls.py` + post-wire writers)

**Vet finding (round 1 NO-GO):** the dry-run replay above only modeled `wire_souls_to_monsters`' own
delta. It could not see `create_uber_souls.py` (called AFTER `wire_souls_to_monsters`, BEFORE
`apply_all_extended_patches`), which creates brand-new souls for uber/hero monsters that had none at
wire-time and unconditionally hardcoded `chanceToEquipFinger2=66.0` - silently re-widening 21 of the 377
intended cuts (`um_crowboar_09`, `um_xix_36`, `um_frost_32`, `hero_junshan_39`, ... ). Same bug class in
every other post-wire soul-rate writer in `apply_svc_patches.py` (`_wire_missing_boss_souls`,
`_create_soul`, `_wire_soul_to_monster`, COLDWORM, Leinth - all default `chance=66.0`).

**Fix, part A (single choke point):** `apply_svc_patches._soul_release_rate(db, record_name, chance)` -
every soul-wiring helper in `apply_svc_patches.py` and `create_uber_souls.py` now routes its
PLACED-default chance through this ONE function (imports `build_svc_database.soul_drop_rate` +
`soul_spawn_provenance_sets` - the same single source of truth the gate uses). Only `chance==66.0` (the
PLACED/dedicated default) is ever routed through the classifier; 25.0/0.0/overrides pass straight
through untouched.

**Fix, part B (rewritten gate, LAST-WRITER semantics):** `verify_soul_drop_rates.py` no longer replays
one function's model - it loads a REAL BUILT arz (asserted via `_require_real_build`, which fails loud
on a bare golden/upstream arz lacking `create_uber_souls.py`'s exclusive output dir) and checks the
FINAL, ACTUAL `chanceToEquipFinger2` on every soul-dropping creature against `soul_drop_rate()`,
whichever writer ran last. A negative test plants a post-wire 50->66 stomp on a live record and proves
the gate still catches it (this is the exact regression class the rewrite exists to close).
`_KNOWN_EXCEPTIONS` visibly waives ~15 pre-existing hand-tunings that predate and are orthogonal to this
directive (Pharaoh's Honor Guard @10%, `svc_um_hadesmarshal_80`/`um_bloodtoxeus_99`/`um_toxeus_hunt_99`
module-owned rates, `boss_satyrshaman_55`/`boss_charon_41`/`boss_charon_43` module-set Boss@66) - printed
but never silently absorbed into a passing count.

**Two FURTHER bugs found and fixed while finishing the routing (this session, round 2 continuation),
both caught only by the real-arz gate above, never by a replay:**

1. **Routing-order bug** in `_place_orphan_monsters`, `_wire_difficulty_variants`, and the Blood Sisters
   loop of `_wire_it_expansion_orphans`: each called `_add_monster_to_pools` (which is what proves a
   record RANDOM, by writing its `nameChampionN` slot into a `records\proxies*` population pool) AFTER
   the soul-creation/wiring call that reads pool membership - so the classifier always saw the record in
   NO pool yet and defaulted it to PLACED(66), a second instance of the round-1 bug class via ordering
   instead of a hardcoded value. Proven with a standalone probe (`soul_spawn_provenance_sets` before/after
   a live `_add_monster_to_pools` call on `um_inkeyes2_45`/`hero_bloodsistersafiya_34`/`um_rong_40`:
   `in random` flips `False -> True`). Fixed by moving every `_add_monster_to_pools` call to run BEFORE
   the soul-rate write in all three functions, and by re-deriving the rate (guarded to only correct an
   already-ENABLED value, never un-gating a deliberately-zeroed record) even when the soul PRE-EXISTED
   (the `if not _has_soul` gate meant a record wired earlier in the pipeline - e.g. `um_frost_36`, wired
   66% by the A6 Limos Lifeeater patch long before ever being pooled - never got its rate reconsidered).
2. **Blank-classification bug** in `_soul_release_rate` itself: it passed `classification=''` to
   `soul_drop_rate()` instead of the record's real, current `monsterClassification`. `soul_drop_rate`'s
   own precedence puts a `Quest` classification AHEAD of pool membership (a quest-tied encounter stays
   PLACED even if it happens to sit in a shared pool) - passing blank skipped that branch, so a
   Quest-classified, pool-referenced record could be wrongly cut to RANDOM(50). Caught 3 records: the
   zzdev Neanderthal warband souls `n_mega`/`n_emgiec`/`n_vio` (Quest-classified, incidentally in a
   'neanderthal' pool via `_create_neanderthal_warband_monsters`). Fixed by reading the record's real
   classification via `db.get_field_value(record_name, 'monsterClassification')`.
3. **Farmable-boss variant edge case:** `_wire_difficulty_variants`'s `boss_terracottamage_bandari_40`
   entry is Boss-classified + `boss_`-pathed (a farmable Act boss per `_soul_is_farmable_boss`, real rate
   25%), not a roaming Hero - the RANDOM-only `_soul_release_rate` wrapper (which pins `boss_chance` to
   the passed-in 66 default so a coincidental path match is a no-op) can never resolve it to 25. Fixed by
   having `_wire_difficulty_variants` call the FULL classifier directly (`soul_drop_rate` with the real
   `boss_chance=25/random_chance=50/placed_chance=66`) instead of the conservative wrapper, for every
   variant it wires - correct for both this Boss/25 case and the 8 Hero/RANDOM(50) siblings (unaffected,
   verified below).

**THE DECISIVE VERIFICATION (2026-07-16):** one real full DB build to scratch output (never touched
`work/`), `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, from the upstream sources + the real Steam base game
install:
```
py tools/build_svc_database.py <sv098i> <sv09> <sv041> <scratch>/Database/SoulvizierClassic.arz <base game database.arz>
```
Result: **55,351,210 B, md5 `fd538e0c5f80e5a5212d70d544bb29d3`.**
`py tools/verify_soul_drop_rates.py <built.arz> --gate` -> **EXIT 0**:
- **0 unwaived LAST-WRITER mismatches** (18 pre-existing exceptions visibly waived, matching
  `_KNOWN_EXCEPTIONS` exactly).
- **RANDOM_HERO records actually shipping at 50%: 377** - the EXACT intended count from section 3 above,
  now true of the real build's OUTPUT (not a replayed model).
- **TESTING mode (real forcer over the real arz): 854 enabled soul-droppers -> 100, 426 gated stay 0: OK**
  - byte-identical proof the release/testing knobs stay independent.
- 16/16 negative/spot tests + override-veto negtest (5/5) + the planted post-wire-stomp negative test all
  **OK** (the stomp negtest is the proof the gate catches the round-1 regression class on THIS arz).
- **souls contract**: `run_contracts.py --only souls --arz <built.arz>` -> **GATE PASS, 0 violations**
  (10 contracts).

**Record-diff, isolating THIS SESSION's fix (before this session's routing/classification/bandari fixes
vs the final decisive build, both built from the identical upstream+base inputs):** exactly **16
records** changed, **every one a single-field `chanceToEquipFinger2` change, nothing else**:
- **13 corrected 66 -> 50** (previously-mis-timed RANDOM roamers, bug #1 above): `um_phagia_34`,
  `um_phagia_44`, `um_dapoyan_42`, `um_indrajit_42`, `um_vidja_43`, `um_frost_36`, `um_rong_40`,
  `um_vuji_41`, `um_yama_38`, `um_inkeyes2_45`, `um_rocksting_29`, `hero_sehr'tunkah_30`,
  `hero_sehr'tunkah_36`.
- **3 corrected 50 -> 66** (bug #2 above, the blank-classification regression): `n_mega`, `n_emgiec`,
  `n_vio`.
- `boss_terracottamage_bandari_40` (bug #3) confirmed **unchanged end-to-end at 25%** in both the
  before-this-session and final builds (a transient regression appeared and was fixed WITHIN this
  session's own intermediate builds, never in a build anyone else saw).

**Record-diff vs the last pre-b59 baseline (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
md5 `eb8bc377...`, build41, predates the entire soul-drop-50 feature):** 539 modified + 6 added. Of the
539, **380 touch ONLY `chanceToEquipFinger2`** (the 377 intended RANDOM cuts plus a small number of
farmable/placed records whose rate is set by this same feature's code paths but whose value coincides
with their pre-existing rate under the naive path heuristic - not a regression, see section 6/`_KNOWN_
EXCEPTIONS`); the remaining ~159 modified records + 6 added touch UNRELATED fields entirely (`bitmap`,
`itemSkillAutoController`, `skillUpBitmapName`/`skillDownBitmapName`, granted-skill/FX fields, new
`um_tombguardian_soul_*`/`q_bloodtoxeus_lone_50` records) - build41 predates several other,
already-merged content waves (Tomb Guardian de-soul, Toxeus encounter suite, mastery UI/damage-display
fixes, etc.), so this comparison is a general content diff, not an isolated soul-drop-50 diff; the
isolated diff above (16 records, all `chanceToEquipFinger2`) is the one that actually bounds THIS
session's change.

**Files touched this round:** `tools/create_uber_souls.py` (routes through the shared split),
`tools/apply_svc_patches.py` (`_soul_release_rate` choke point + real-classification fix + every
soul-wiring helper routed + the 3 pool-ordering fixes + the difficulty-variant full-classifier fix),
`tools/verify_soul_drop_rates.py` (LAST-WRITER rewrite + `_KNOWN_EXCEPTIONS` + stomp negative test).
