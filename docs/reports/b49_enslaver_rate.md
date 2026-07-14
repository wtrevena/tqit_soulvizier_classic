# b49 - ENSLAVER BREADTH RCA (roaming smear, not rate)

Branch `feat/b49-enslaver-rate` (base `d11d3c0`, current main w/ `_EN_SWEEP_K=600`).
**RCA + BREADTH-CUT FIX (round 1) both DONE** (fix in the section directly below; RCA analysis
follows it). Ground truth = `baseline_build38.arz`
(MD5 `fcd5dcab40359aa94b421dd8cef4b81e`, == the DEV/Steam arz Will plays), probed with
`tools/arz_patcher.ArzDatabase`. K comparison cross-checked against the base game
`database.arz`.

## Will's evidence + directive (2026-07-13)
> "seeing him ALL OVER THE PLACE, not just in fixed places" ... "no we dont need the 4x rate
> cut on top." Fix = **BREADTH ONLY**: put him in FAR fewer pools. Do NOT change the rate
> (`_EN_SWEEP_K` stays 600, per-pool p <= 1/24000 unchanged).

Target monster = `um_toxeus_enslaver_99` (the roaming black Skeleton-Lord "Enslaver of Souls").

---

## IMPLEMENTATION (round 1, this branch) - BREADTH CUT DONE + verified (no heavy build)

**Design decision:** BREADTH ONLY, rate untouched (Will: "no we dont need the 4x rate cut on
top"). Restrict the roaming sweep to the Enslaver's own lineage - the **`undead` family pools**
- so he stops being a universal smear and becomes a thematic haunt of the dead. `_EN_SWEEP_K`
stays **600**, weight stays 1, limit stays 1, `_EN_SWEEP_CEIL`/`_EN_SWEEP_MAX_P` untouched.

**Files changed (2; DB-lane only, no map/quest/navmesh touch):**

1. **`tools/apply_svc_patches.py`** - the Enslaver roaming sweep now rides ONLY `undead`-family
   pools. New `_EN_SWEEP_FAMILIES = ('undead',)` + `_en_pool_family()` helper; `eligible()`
   gains a one-line family filter (`\pools\<family>\` == undead); `_verify_roaming_sweep()`
   gains a per-pool family assertion **and a pool-count BAND** (`_EN_SWEEP_MIN_POOLS=200` ..
   `_EN_SWEEP_MAX_POOLS=400`, replacing the now-stale `< 500` floor) so the gate FAILS LOUD if
   the restrict silently no-ops (`> 400` = the smear came back) or over-narrows (`< 200`).
   **Result: 1224 -> 273 swept pools (Act1 91 / Act2 64 / Act3 55 / Act4 63), a 78% cut.**

2. **`tools/patches/toxeus_suite.py`** - the co-swept Hunter (`um_toxeus_hunt_99`,
   `_sweep_inject_legendary_stalker`) made **self-sufficient to PREVENT COLLATERAL**. The Hunter
   appended itself at weight 1 only where a pool's wtotal was already `>= 2399` - which it got
   for free from the Enslaver sweep having x600'd EVERY Hades pool. Cutting the Enslaver to
   undead-only would have collapsed the Hunter **345 -> 63** Hades pools (measured). Fix: when
   the Enslaver is ABSENT from an eligible Hades pool, the Hunter now applies the SAME x600
   itself (same floor), so it keeps its FULL 345-pool Hades breadth + identical 1/24000 rarity.
   Behavior-neutral (a uniform scale preserves relative spawn odds); the x600 just moves from
   the Enslaver sweep to the Hunter sweep. **Net arz change vs build38 = ONLY the Enslaver
   leaving the 951 non-undead pools; the Hunter is byte-set-preserved.**

**Verification** - dry-run replay on an in-memory COPY of `baseline_build38.arz` (disk arz
untouched), executing the **REAL modified sweeps + both fail-loud gates**
(`scratchpad/b49_dryrun2.py`; reconstructs the gate-time pre-sweep DB by reversing the x600 +
stripping both rares, then re-runs the production code):

| check | result |
|---|---|
| Enslaver breadth | `pools_before=1224 -> pools_after=273` (91/64/55/63) |
| Enslaver gate `_verify_roaming_sweep` | **PASSED**; every touched pool undead / weight 1 / limit 1 / p_slot <= 1/24000 |
| Hunter breadth | `345 -> 345, preserved=YES (added=0, lost=0)`; 282 self-x600'd |
| Hunter gate `_verify_legendary_stalker_sweep` | **PASSED** |
| scoped diff | 63 undead Hades = both rares; 282 non-undead Hades = Hunter+x600, NO enslaver; 669 de-listed non-Hades = 0 enslaver + 0 residual x600 (fully reverted) |
| structural | enslaver + hunter both weight=1 / limit=1 (0 violations) |
| rate | `_EN_SWEEP_K = 600` UNCHANGED (asserted); CEIL/MAX_P untouched |
| static warband | `q_enslaver_warband` (placed in blood cave) + yard whitelist untouched |
| gates | `py -m py_compile` both files OK; `tools/patches/_check_registry.py` OK (11 modules) |

**AGGREGATE (undead-273, K=600):** roaming ~0.03-0.11 sightings/act on a thorough clear
(Act3 lowest ~0.01-0.03) - a rare thematic surprise among the dead, **below once/act BY
DESIGN** (a weight-1 / K=600 member in few pools is mathematically rare; Will forbade a rate
change). The dependable per-encounter beat is the PLACED warband set-piece, not the roam.

**Knob if Will wants him even rarer / in fewer haunts after a real test:** tighten
`_EN_SWEEP_FAMILIES` or add a per-act zone cap (RCA Option B -> ~20-40 pools) and lower
`_EN_SWEEP_MIN_POOLS` to match. One-line change; the gate band self-documents the target.

> ⚠️ **PERSISTED-SAVE - Will MUST test on a FRESH Custom-Quest char or a never-visited area.**
> His `_Toxeus` baked build36a-rate (K=60, 10x) Enslavers into every explored zone; NO arz or
> code can rewrite those. Re-walking old Greece/Egypt will STILL show the old smear and is NOT
> a valid test of this fix. See section 6 for the decisive in-game test.

---

## TL;DR / VERDICT

1. **BREADTH is the driver, and it is extreme.** The roaming sweep put the Enslaver into
   **1224 of 1433 eligible hostile trash pools = 85.6% of the game's entire trash bestiary**,
   reachable through **2127 distinct spawn-definition proxies** spread across all four acts
   (Act1 454, Act2 550, Act3 582, Act4 539 proxies). He can roll out of ~6 of every 7 trash
   packs in the game. That is the literal definition of "all over the place, not in fixed
   places," and it is what destroys memorability, **independent of how rare each roll is.**

2. **The RATE is already on target; it is NOT the problem.** At the current K=600, a thorough
   fresh-character traversal yields **~0.5-0.6 Enslaver sightings per act** (lighter play
   ~0.1-0.3). That is exactly the b38 "about once an act" goal, already met. The "many / all
   over" Will still sees is **(a)** his persisted save (explored at the old build36a K=60 rate
   = ~6/act, baked in) and **(b)** the 85.6% smear making even a once-per-act rate feel
   omnipresent because there is no place he canNOT appear. Will is correct not to cut the rate.

3. **The per-pool reduction is genuinely and uniformly applied.** Every one of the 1224 swept
   pools carries him at `weight=1` + `limit=1` in a MAIN name slot; **zero** are champion,
   guaranteed, over-weight, or over the 1/24000 p-ceiling. The only 3 non-weight-1 pools are
   the intended hand-authored set-pieces (yard, warband, Neferkha's court).

4. **Persisted-save contribution is HIGHLY plausible and unfixable by any arz change.** Only a
   fresh character (or a never-visited area) reflects the new breadth. Distinguish in-game by
   rolling a new Custom Quest char.

5. **Breadth target:** cut the roaming sweep from 1224 pools to a curated thematic remnant.
   Headline recommendation: **restrict the sweep to the Enslaver's own lineage (the `undead`
   family) => ~273 pools (78% cut)**, or tighter to **one signature haunt per act => ~20-40
   pools (>96% cut)** for true "few deliberate places." Reliable **~once-per-act comes from the
   PLACED warband set-piece, not the sweep** (see the math in section 6): a weight-1/K=600
   roaming member in few pools is mathematically a rare surprise, never a dependable per-act
   encounter. Keep + lean on the static warband for the guaranteed memorable beat.

---

## 1. BREADTH enumeration (the decisive numbers)

`proxypool.tpl` records in the arz: **1845**. Eligible hostile trash pools (allow-prefix, non
boss/quest/hero marker, all resolvable members Class=Monster): **1433**.

| Act (allow-prefix) | Enslaver pools | proxies that can spawn him | proxy->pool edges |
|---|---|---|---|
| Act 1 Greek (`proxies greek\`) | **363** | 454 | 1090 |
| Act 2 Egypt (`proxies egypt\pools`) | **225** (224 swept + Neferkha court) | 550 | 1017 |
| Act 3 Orient (`proxies orient\pools`) | **292** | 582 | 1145 |
| Act 4 Hades (`xpack\proxieshades`) | **345** | 539 | 982 |
| dedicated (drxmap yard + warband) | 2 | 2 | 2 |
| **TOTAL enslaver-bearing** | **1227** | **2127 distinct** | 4236 |

- **1224** of these are ROAMING-SWEPT (eligible pools that also pass the sweep's original
  weight-total >= 40 floor). **85.6% of all 1433 eligible trash pools.**
- **209** eligible pools were NOT swept - **100% of them because they fall below the
  orig-wtotal < 40 floor** (e.g. `deserthag_01_general01` at wtotal 30 was skipped while its
  sibling `deserthag_01_general02` at 60 was swept). Zero unexplained gaps: the sweep's own
  eligibility is exactly `allow-prefix AND non-marker AND monster-only AND orig-wtotal>=40 AND
  free-slot`.
- proxies-per-pool: mean 3.45, median 2, max 84. Each pool is a spawn definition referenced by
  several placed proxies, so the placed-spawn-point count is a multiple of the pool count.

**Interpretation:** breadth is not "a few pools too many," it is essentially the WHOLE hostile
world. There is no act, no region, and almost no enemy family he is absent from (see the
family table in section 7). Being present in 2127 spawn definitions is the structural cause of
"all over the place," and it is a fact, not a probability estimate.

## 2. Per-pool reduction: genuinely applied (K=600, weight 1, limit 1)

Cross-checked two swept pools against the base game `database.arz` to confirm the ×K scaling
actually landed:

| pool | base-game member weight | build38 member weight | ratio |
|---|---|---|---|
| `proxies egypt\pools\beast\deserthag_01_general02` | 10 | 6000 | **600** |
| `xpack\proxieshades\pools\beast\hydradon_01_general01` | 30 | 18000 | **600** |

`K=600 CONFIRMED`. Enslaver appended at `weight=1`, `limit=1`, in the first free name slot;
p_slot = 1/(600*W_orig + 1).

Per-act p_slot (from the actual scaled weights, the real number, not the ceiling):

| Act | pools | p_slot median | p_slot range (max=most common) | spawnMax mean |
|---|---|---|---|---|
| Act1 Greek | 363 | 1.11e-5 (1/90k) | 3.33e-5 (1/30k) .. 3.9e-6 | 4.46 |
| Act2 Egypt | 225 | 1.19e-5 (1/84k) | 4.17e-5 (1/24k) .. 2.8e-6 | 3.92 |
| Act3 Orient | 292 | 3.70e-6 (1/270k) | 4.17e-5 (1/24k) .. 2.8e-6 | 4.50 |
| Act4 Hades | 345 | 1.51e-5 (1/66k) | 2.78e-5 (1/36k) .. 1.5e-6 | 4.08 |

The worst (most common) p_slot anywhere is exactly **1/24000** (the ceiling); nothing exceeds
it. Reduction is uniform and correct.

## 3. Anomaly scan (weight!=1 / champion / guaranteed): ZERO real anomalies

Scanned all 1227 enslaver-bearing pools:
- **champion-slot enslaver: 0.**
- **weight != 1: 2** - both intended (`q_enslaver_warband` w=100, `q_yard_enslaver` w=100).
- **limit != 1: 2** - the same two dedicated pools.
- **p_slot over 1/24000: 2** - the same two (p=1/300, the deliberate boss encounters).
- **outside the allow-prefix: 2** - the same two (drxmap dedicated pools, whitelisted).

Three enslaver pools fall OUTSIDE the roaming set (fail the sweep's own eligibility, so they
are deliberate placements, not smear):
1. `records\drxmap\proxy\pools\q_enslaver_warband.dbr` - the static warband set-piece
   (leader w=100 + 4 marauder champions). **Keep (Will's law).**
2. `records\drxmap\proxy\pools\q_yard_enslaver.dbr` - the TESTHUB test-yard (w=100, inert on
   canonical). Whitelisted.
3. `records\proxies egypt\pools\svc_neferkha_court.dbr` - hand-authored Egypt set-piece
   (Neferkha's frost court); Enslaver at weight 1 / limit 1, p=1/354001 (one pool, inert as a
   breadth contributor). Excluded from the sweep by the `svc_` basename rule; present via the
   Neferkha module's authored roster. Harmless, but the breadth-fix agent should be aware it
   exists so a curated selector does not accidentally double-count or strip it.

**Conclusion: the reduction knobs (K, weight, limit, floor) are all working exactly as b38
designed. There is no rate/structural defect to fix. The remaining problem is purely breadth
+ the persisted save.**

## 4. Second roaming rare found (adjacent, out of scope)

`um_toxeus_hunt_99` ("the Endless Hunt", the Hades stalker) is co-swept at weight 1 into **all
345 Act-4 Hades pools** (100% of them) via the same idiom. b38 lists it as out of scope. Flag
only: if Will later reports the Hunter "everywhere in Hades," it is the identical breadth
pattern and the same fix template applies. Not touched here.

## 5. AGGREGATE rate: ~once/act at K=600 (already on target), calibrated to Will

Model (transparent, since the 685 MB Levels.arc placement count is out of scope for a
read-only lane): expected sightings crossing an act
= SUM over enslaver pools of [ triggers(pool) x E[mains] x p_slot(pool) ].
E[mains] ~ 3 (spawnMin..spawnMax midpoint minus champions). `triggers(pool)` = spawn points
that fire the pool x re-rolls; anchored below to Will's own report.

**Calibration to Will (build36a, K=60):** "~6 Enslavers crossing Act 1 to Medusa" (b38 also
states ~6/act at build36a). Act 1 has 363 enslaver pools, build36a mean p_slot ~1.25e-4. To
produce 6 sightings needs ~44 trigger-draws per pool across an Act-1 clear - consistent with a
thoroughly-cleared act (each pool's placements + area re-entries).

**Same play pattern at the current K=600 (10x rarer):**

| Act | K=600 (fresh char) | build36a K=60 (Will's history) |
|---|---|---|
| Act1 Greek | ~0.14 (light) .. 0.55 (thorough) | ~1.4 .. 5.5 |
| Act2 Egypt | ~0.12 .. 0.46 | ~1.2 .. 4.6 |
| Act3 Orient | ~0.07 .. 0.29 | ~0.7 .. 2.9 |
| Act4 Hades | ~0.15 .. 0.61 | ~0.8 .. 6.1 |

**Decisive answer: at the current K=600 the aggregate is ~once per act (~0.5-0.6 on a thorough
traversal), NOT many.** The b38 frequency fix already hit its "about once an act" target. The
"many / all over the place" Will reports post-fix is **not** the live spawn rate; it is the
build36a persisted save (~6/act baked, section 6) plus the 85.6%-pool smear (a once-per-act
rate distributed over 2127 spawn points reads as "he's everywhere and never special").

**Consequence for the fix:** because the live rate is already ~once/act, cutting breadth at the
UNCHANGED K=600/weight-1 makes the ROAMING component *rarer* than once/act (fewer pools => fewer
chances; the per-pool p is fixed tiny by Will's no-rate-change rule). So the reliable
"~once per act in a deliberate place" must be carried by the **placed warband set-piece**, with
the curated roaming remnant acting as a rare thematic surprise on top. This is not a
limitation to apologize for - it is the correct division of labor: placements give
predictability, the sweep gives rare flavor.

## 6. PERSISTED-SAVE assessment (plausibility: HIGH) + how Will distinguishes

TQ bakes generated monster instances per visited area into the character's world state (same
mechanism CLAUDE.md notes for baked item properties; the engine seeds and persists a level's
spawns on first visit and does not re-roll explored/recent areas). Will's long-running
`_Toxeus` explored the world while build36a (K=60, **10x** the current rate, ~6/act) was
deployed, so **every area he has already visited has old-rate Enslavers frozen into his save.**
The current K=600 arz only governs areas generated AFTER it was installed = new/unvisited
zones or a fresh character. **No code, no arz, no map edit can rewrite the spawns already baked
into his save's visited areas.**

This very plausibly explains the bulk of "all over the place": he is walking back through a
world that was populated at 10x the current rate. It compounds with the breadth smear (an
old-rate Enslaver could have been baked into almost any pack, since 85.6% of pools carried
him).

**How Will distinguishes it in-game (decisive test):**
- **Roll a NEW Custom Quest character** and traverse an act cleanly. New areas generate from
  the current arz. If the fresh char sees him rarely/never in trash while the old `_Toxeus`
  still sees him in already-explored zones, the delta IS the persisted save.
- Or on the existing char, reach a **genuinely never-before-visited** area and watch only that
  virgin zone.
- Do NOT judge the fix by re-walking `_Toxeus` through old Greece/Egypt; that is reading stale
  bakes, not the new arz.

## 7. VERDICT + breadth target (K=600 unchanged, weight/limit unchanged)

Cut the roaming sweep from **1224 pools** to a curated thematic remnant so the Enslaver stops
being a universal smear and becomes tied to a few haunts. Per-act enemy-family counts (to pick
from):

| family | Act1 | Act2 | Act3 | Act4 |
|---|---|---|---|---|
| undead | 91 | 64 | 55 | 63 |
| beastmen | 113 | 57 | 132 | 72 |
| beasts | 57 | 27 | 12 | 18 |
| insects | 41 | 30 | 15 | 18 |
| demons | 20 | 12 | 34 | 133 |
| traps/device | 21 | 20 | 15 | 18 |
| other | 20 | 15 | 29 | 23 |

Recommended options (pick per Will's taste for how often the roaming form should still appear):

- **Option A - lineage restrict (HEADLINE, low-effort, low-risk): sweep only the `undead`
  family.** => **~273 pools (Act1 91 / Act2 64 / Act3 55 / Act4 63), a 78% cut.** Trivial to
  implement: add a family filter to the sweep's eligibility (require `\undead\` in the pool
  path). Thematically exact - a black Skeleton-Lord "Enslaver of Souls" on the
  RevenantPoison/Blood-Toxeus rig belongs among the dead. Roaming aggregate falls to ~0.1-0.15
  /act (once per ~7-10 acts): present, thematic, no longer omnipresent.
- **Option B - few deliberate haunts (best matches "FEW deliberate places"): sweep one signature
  undead/shadow cluster per act** (one enemy-family's pool group in one late zone; a cluster is
  ~5-12 pools). => **~20-40 pools total (>96% cut).** He becomes a named haunt ("the Enslaver
  walks the necropolis of Act N"). Roaming aggregate ~0.01-0.03/act (a rare surprise); the
  **placed warband carries the dependable per-act encounter.**
- **Do NOT** try to hit a hard "once per act" from the sweep alone at fewer pools - it is
  mathematically impossible at K=600/weight-1 (section 5). Anchor once-per-act on placements.

**Keep intact (Will's laws + b38):** the static warband set-piece (`q_enslaver_warband`); the
structural `limit=1` no-double cap; `_EN_SWEEP_K=600` (do NOT touch the rate); the registry
contract + fail-loud sweep gate (it will need its floor/`>=500 pools` assertion relaxed to the
new curated count when the breadth is cut); the amgoz1 identity bar.

Suggested implementation surface for the fix lane (not done here): the sweep's `eligible()` in
`tools/apply_svc_patches.py` (~line 10530) - add the family/zone filter; and
`_verify_roaming_sweep` (~line 10708) - lower the `< 500 pools` regression floor to the new
target (e.g. `< 200` for Option A, or an exact expected count for Option B). The proxy graph,
warband, yard, and Neferkha court need no change.

---

## Gates
- `pools_total`: **1227 enslaver-bearing** (1224 roaming-swept = 85.6% of 1433 eligible trash
  pools; + 3 deliberate: yard, warband, Neferkha court). 2127 distinct spawn proxies.
- `aggregate_per_act`: **~0.5-0.6/act at the current K=600 (thorough fresh traversal) = the b38
  "once an act" target already met.** build36a was ~1-6/act. The perceived "many/all over" is
  the persisted build36a save + the 85.6%-pool smear, NOT the live rate. => once/act, not many.
- `persisted_save_plausible`: **HIGH.** TQ bakes per-visited-area spawns; `_Toxeus` was
  explored at build36a (10x); only a fresh char / virgin area reflects the arz. Unfixable by
  any arz/map/code change.
- `breadth_target`: **1224 -> ~273 (undead-family restrict, headline) or ~20-40 (one haunt per
  act, "few deliberate places")**, at UNCHANGED K=600/weight-1/limit-1; reliable once-per-act
  anchored on the placed warband, not the sweep.

Verification scripts (scratchpad, reproducible): `probe_breadth.py`, `probe_aggregate.py`,
`probe_families.py`, `probe_gap.py`, `probe_dump_pool.py`.
