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
