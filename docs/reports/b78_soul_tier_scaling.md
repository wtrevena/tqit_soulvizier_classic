# b78 - Soul tier scaling (Blood Cult High Priest) + roster sweep + strict-progress gate

> Branch `fix/soul-tiers` (off `main` 33d25d6, golden arz md5 `917d9047`). Lane scope: SOUL ITEM
> records + their granted-skill scaling ONLY. Did NOT touch um_toxeus_* champions, EoAT records,
> boss-summon pet FX/portraits, map placement, or the Cold Worm family (its own lane). No em dashes.

## TL;DR

Will (2026-07-16, verbatim): *"Also for Blood Cult - High Priest Soul, i think his epic soul is the
same as the normal one i dont know if we scaled the soul across normal epic and legendary difficulty."*

**Ground truth: the Blood Cult High Priest soul is correctly scaled across all three difficulties,
and so is every other soul family in the mod.** The roster-wide sweep found **0 flat-tier families,
0 wrong-tier loot triples, and 0 real missing tiers**. Will's specific observation is a false alarm
(most likely a save-bake + shared-name perception artifact, explained below). Because nothing is
broken, this wave makes **no data change** to any record; its value is **closing the gate blind spot**
that would let a genuinely-flat epic slip through in the future - Will's exact concern, made
permanent. `flat_tier_count = 0` (families that needed a scaling fix).

## 1. Blood Cult High Priest RCA (`svc_uber\bwpriest_soul_{n,e,l}`)

The soul family is `records\item\equipmentring\soul\svc_uber\bwpriest_soul_{n,e,l}.dbr`
(name tag `tagSVCSoulBWHighPriest`, "Blood Cult High Priest Soul"). Decoded all three tiers from the
golden arz (`917d9047`):

| field | Normal (_n) | Epic (_e) | Legendary (_l) |
|---|---|---|---|
| augmentSkillLevel1 (drxdarkcovenant) | 2 | **3** | **4** |
| augmentSkillLevel2 (drxdeathchillaura) | 2 | **3** | **4** |
| itemSkillLevel (summon_bwpriest) | 1 | **2** | **3** |
| characterIntelligenceModifier | 6 | **9** | **12** |
| characterLifeModifier | 10 | **14** | **19** |
| characterManaRegenModifier | 12 | **18** | **24** |
| characterSpellCastSpeedModifier | 14 | **20** | **28** |
| defensiveLife | 18 | **26** | **34** |
| offensiveLifeMin / Max | 25 / 40 | **38 / 58** | **55 / 82** |
| offensiveLifeLeechMin | 20 | **30** | **42** |
| itemLevel / levelRequirement | 39 / 34 | 56 / 51 | 71 / 66 |

Both **surfaces the coldworm class bug lives on** are healthy here:

1. **Soul ITEM records** strictly increase every scaled stat + augment + granted-skill level from
   Normal to Epic to Legendary (table above). The Epic is NOT identical to the Normal.
2. **Per-difficulty loot triple** is correct. The only DB reference to this soul is the monster
   `records\drxcreatures\bloodwitch\c_disciple_miniboss.dbr`, field `lootFinger2Item1` =
   `[bwpriest_soul_n, bwpriest_soul_e, bwpriest_soul_l]` - index 0 (Normal) drops `_n`, index 1
   (Epic) drops `_e`, index 2 (Legendary) drops `_l`. No wrong-tier drop.
3. The granted summon **scales too**: `summon_bwpriest.dbr` is `skillMaxLevel 3` with three distinct
   pet tiers (`bwpriest_1/2/3`), so `itemSkillLevel 1/2/3` summons a progressively stronger priest.

**Why Will perceived "epic same as normal":** the item NAME tag and DESCRIPTION tag are byte-identical
across all three tiers (`tagSVCSoulBWHighPriest` / `tagSVCSoulBWHighPriestDESC`), and the granted
summon shows the same skill display name at every tier. So the tooltip *reads* the same even though
the underlying stats/summon differ. Compounding it: **TQ bakes item stats into the save at pickup**,
so a soul Will already holds keeps whatever tier it was picked up as; two souls that were both picked
up on the same difficulty would of course be identical. **Test instruction:** drop a FRESH Epic (kill
the Blood Cult High Priest / c_disciple_miniboss on Epic) and compare its Intelligence / Life / Health
Leech to a Normal-difficulty drop - they differ per the table. Existing baked souls will not change.

## 2. Roster sweep (every soul family, golden `917d9047`)

Tools (committed): `tools/debug/soul_tier_sweep.py` (families, flat, missing, wrong-loot),
`tools/debug/soul_flat_classify.py` (full-field diff + SV098 cross-check + obtainability),
`tools/debug/soul_strict_progress.py` (strict-progress pass/fail over all full-3-tier families).

| metric | count | verdict |
|---|---|---|
| soul-ring tier families total | 775 | - |
| full-3-tier families | 706 | all present |
| **FLAT** (epic byte-identical to normal on all scaled dims) | **0** | none |
| **strict-progress PASS** (some scaled field up n->e AND e->l) | **706 / 706** | clean |
| **WRONG-TIER LOOT** (difficulty triple points at a lower tier) | **0** | none |
| real MISSING tiers (a droppable soul lacking _e or _l) | **0** | none |

**On the "28 flat" and "69 missing" first-pass numbers (corrected):** an initial sweep using a
curated stat-field subset flagged 28 "flat" families. Full-field diffing proved every one of them
scales on stat fields the subset omitted (e.g. `defensivePhysical` 6->9, `racialBonusPercentDamage`
50->55, `defensiveStun` 20->30) - and SV 0.98i (`11773cdc`, the design bible) ships all 28 scaled
too. They are HEALTHY; the 28 were a probe artifact, which is exactly why the shipped gate reasons
over the **full** numeric power vector, not a subset. The 69 "missing-tier" entries are all noise:
`*\soultemplate` base template records, `test\*` dev souls, `any*soul` / `any*herosoul` formula
meta-pool selectors (referenced by crafting formulas, a different system), and malformed
double-suffix duplicate artifacts (`brontes_soul_n__e`, `diseasedvulture_n_soul_e`) that shadow the
real, healthy `brontes_soul_{n,e,l}` / `diseasedvulture_soul_{n,e,l}` trios. None is a droppable soul
missing a difficulty tier.

## 3. Scaling formula (evidence)

No formula needed to be applied (no family required scaling), but for the record the mod's own
healthy convention - confirmed against SV 0.98i as the design bible and consistent across bwpriest,
bloodrunner, xix, and the generated svc_uber roster - is a per-tier step of roughly:

- granted-skill / augment **level**: `+1 per tier` (n -> e -> l), e.g. bwpriest augments 2/3/4,
  itemSkillLevel 1/2/3.
- **stat modifiers**: Epic ~= Normal x 1.4, Legendary ~= Normal x 1.9 (bwpriest Life 10/14/19,
  Int 6/9/12, leech 20/30/42). Exact ratios vary per family; the invariant the gate enforces is the
  weaker "strictly greater at each step", not a fixed multiplier (families legitimately vary, and
  some scale stats while holding augment levels flat - e.g. the satyr/boar soldier souls).

## 4. Gate tightening (the actual change this wave ships)

`tools/patches/souls_quality.py` gains a roster-wide STRICT-progress gate, wired into the existing
fail-loud `verify()` alongside the non-strict monotonicity gate (which still independently bars
inversions). New pieces:

- `_power_vec(db, rec)` - every numeric field except cosmetic / structural / requirement / tag /
  skill-NAME fields (`_POWER_IGNORE`). This is the "is Epic stronger" surface: stat modifiers +
  skill LEVELS. Full breadth is load-bearing - families that hold augment levels flat and scale only
  stats must still pass.
- `_tier_progresses(db, lo, hi)` - True iff some power field is strictly greater on `hi`. Skill-level
  fields only count when the paired granted-skill NAME is identical across the two tiers.
- `_flat_tier_violations(db, nm)` - every full-3-tier family must progress n->e AND e->l, unless
  waived. `_FLAT_TIER_WAIVER` is **EMPTY** (the sweep proved 706/706 progress; a future
  deliberately-flat soul goes here with justification, fail-loud forces the decision to be explicit).
- `verify()` raises `SystemExit` naming the flat family + tier step if any full-tier family fails to
  get stronger. This closes Will's exact blind spot: the old gate was non-strict (`n<=e<=l`), so a
  byte-identical Epic passed; the new gate demands strict progress.

**Negative test** (`py tools/patches/souls_quality.py --negtest`): plants a 3-tier family whose Epic
is a byte-identical clone of Normal (Legendary stronger) and asserts the gate flags the `n->e` step
and NOT the `e->l` step. **PASS.**

## 5. WILL-CONFIRM list

**None.** Every full-3-tier soul family strictly progresses on the golden arz; there is no
ambiguous-flatness family to adjudicate. If Will still sees an in-game Epic that looks identical to a
Normal, it will be a save-baked (pre-existing) item - drop a fresh one to confirm the new drop scales.

Two out-of-lane observations surfaced (not changed here):

1. **Malformed duplicate soul records** (`cyclops\{brontes,polyphemus,steropes}_soul_n_{,_e,_l}`,
   `vulture\{diseasedvulture,infectedvulture,vulturelord}_n_soul{,_e,_l}`) shadow the real healthy
   trios. They look like generation artifacts. Deleting records is destructive and outside a
   tier-scaling lane; flagged for a hygiene pass (confirm unreferenced first).
2. **Cold Worm family** = report-only per lane split. Not inspected/changed here.

## 6. Verification

- `py_compile tools/patches/souls_quality.py` - OK.
- `_flat_tier_violations` + `_monotonicity_violations` on golden `917d9047` - **0 / 0**.
- `soul_strict_progress.py` on golden - **706/706 PASS, 0 FAIL**.
- Negative test - **PASS** (planted epic==normal flags n->e only).
- Full scratch DB build with the new gate active - **EXIT 0**. The build runs
  `run_registry_verifies` (which calls `souls_quality.verify`, including the new strict gate) at
  `build_svc_database.py:3813`, BEFORE `write_arz` at :3854 - so the arz being written is proof the
  strict gate PASSED in-build. Output arz **md5 `917d9047d2281284f5fd5e9a163b9c5c`, 55,382,463 B =
  BYTE-IDENTICAL to the golden**. Record-diff vs `917d9047` = **ZERO** (a gate-only change makes no
  record edits; the built arz is bit-for-bit the golden).
- `contracts_souls.py` on the built arz - **2302 souls checked, 0 violations, EXIT 0**.
- B-SUMMON-1 / render-chain: the arz is byte-identical to build45 golden `917d9047`, which shipped
  green on the full build45 gate battery (BACKLOG build45 record); no new tier records were created,
  so there is no new summon to render.
- Untouched: A7 + chain gate, map, Quests, Levels, um_toxeus_*, EoAT, boss-summon FX (this wave edits
  only `tools/patches/souls_quality.py` + 3 read-only debug probes + docs).
