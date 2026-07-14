# b39 - New-boss skill-wiring RCA + fix

**Report:** boss-skill usage audit across every new boss, both combat surfaces.
**Branch:** `feat/b39-boss-skills` (module + probe commit `372c6e2`).
**Baseline audited:** `baseline_build38.arz` (== build38a DEV arz `6631f252`, 51,007 records).
**Fix:** `tools/patches/boss_skill_fix.py` (registry module) + `tools/debug/b39_boss_skill_audit.py` (read-only A/B probe).
**Heavy build:** none (dry-run replay only, per the standing "one heavy build at a time" law and Will actively playing).

---

## Will's report (2026-07-13, verbatim)

> "i think there are issues with the new bosses we created not having or not using
> skills, when you are fighting them and when they are summoned if you have their
> soul and it grants you the ability to summon them."

Two surfaces per boss: **(A)** the FOUGHT monster record, **(B)** the SOUL-SUMMONED PET form.

---

## TL;DR

- **Surface B (summoned pets): HEALTHY - no fix needed.** Every soul-summoned pet
  (built by `_build_boss_summon` + `_mirror_source_skill_kit`) carries its source
  boss's animation+skill kit with castable specials that all resolve, is permanent
  (TTL absent), and has a sane `petLimit`. 17 summon families audited, all pass.
- **Surface A (fought bosses): a level-0 skill-wiring defect on 9 bosses.** Uniform
  root cause: a builder set `skillName{i}` on a cloned donor **without** the matching
  `skillLevel{i}`, so the new skill inherited the donor's empty (**level 0**) slot.
  A boss then either **never casts** a level-0 special-attack (it "tries" at
  `chance>0` but the skill is disabled) or **never applies** a level-0 aura/passive.
  Plus Helepolis, whose signature **turret barrage was displaced** by the meteor nova.
- **Fix:** `boss_skill_fix.py` makes 25 field edits over 9 bosses (levels + Helepolis
  specials only - no clones, no souls, no pets, no damage/stat changes). Dry-run
  replay + `verify()` hook confirm **0 level-0 specials remain**; idempotent; pets
  untouched.

---

## Method

`tools/debug/b39_boss_skill_audit.py` loads a built `.arz` and dumps, per boss:

- **Surface A:** `monsterClassification`, `initialSkillName`, `attackSkillName`,
  every `skillName{N}`/`skillLevel{N}`, every `specialAttack[N]SkillName` +
  `Chance` + `Range`, whether each referenced skill **resolves**, the **level** of
  each special's referenced skill (cross-referenced from the skillName slots), and
  a flag for `LEVEL0-SPECIAL` (chance>0 but referenced skill at level 0),
  `NO-SKILLNAME-SLOT`, and dead core passives.
- **Surface B:** each summoned pet's AI slots (`attackSkillName` +
  `specialAttack1..5`), resolution, `petLimit` (from the summon skill), TTL.

7 known-good base/xpack donor bosses were dumped as **exemplars** to establish the
vanilla invariant.

### The vanilla invariant (proven over 7 exemplars)

`xhero_aorg_45`, `um_leveler_43`, `boss_charon_43`, `xhero_aberkios_43`,
`xsecrethero_wardenofsouls_48`, `um_khenti_31`, `am_deathstalker_55_ambush`:

- Active attack skills and `armor_passive` are **always level >= 1**; specials are
  in a `skillName` slot at a real level.
- The **only** skills that ship at **level 0** are `globalproperties_epic01`,
  `globalproperties_legendary01`/`_epic_boss`/`_legendary_boss`, and
  `all_hpscaling_passive` - the engine difficulty-scales those. **These are NOT
  defects and are left untouched.**

---

## Surface B - HEALTHY (no fix)

`_build_boss_summon` copies ONLY the source monster's animation + skill fields onto
a Lyia-pet baseline and calls `_mirror_source_skill_kit`, honoring every crash law
(never Monster.tpl equipment onto Pet.tpl; permanent = TTL removed). Audit result -
all pets carry the mirrored kit with castable specials, all resolve, TTL absent
(permanent), petLimit 1 (wyrmlings 6):

| Summon soul | source | pet AI slots (castable) |
|---|---|---|
| Menoetes / Marshal | svc_um_hadesmarshal_80 | 5 (hadesbolt/spiritbolt/groundbreaker/lifedrain) |
| Neferkha | um_neferkha_99 | 4 (iceshard x2 / freezingbreath) |
| Enslaver (pet-of-pet) | um_toxeus_enslaver_99 | 6 (petmarauders/nether/bladestorm/flash/lethal) |
| Devourer / Blood Toxeus | um_bloodtoxeus_99 | 5 (bloodboil/flash/bladestorm/lifedrain) |
| Tantalus shade | xhero_aberkios_43 | 4 (spidersummon/thunderball/lightningsurge) |
| Charon oarsman | charon_minion_30 | 2 (oarsman lifedrain) |
| Mnemophage phantasm | (epiales) | 3 (poisonorb/venombolt) |
| Broodmother | um_broodmother_99 | 4 (wyrmlings/necrobolt/firebreath) |
| Broodmother wyrmling | (wyrm) | 2 (firebreath) |
| Kravmoloch warden | um_gorrahk_99 | 4 (bladestorm/groundsmash/roar) |
| Voranthys | um_sepulchralwyrm_31 | 2 (freezebreath) |
| Eater of Days / Pygmalion / Sarpedon / Long Nu / Meritamen | (various) | 4-6 each |

**Note:** the Kravmoloch WARDEN pet mirrors `um_gorrahk_99` (the summon source), not
the Kravmoloch boss; it displays its groundsmash/roar as pet specials because pet
kit levels are re-registered by `_register_pet_skill` (not inherited from the
source's level-0 slots), so the pet form is unaffected by the surface-A bug.

---

## Surface A - the defect (root cause)

Bosses built with `_svc_set_kit(...)` (which sets **both** `skillName{i}` **and**
`skillLevel{i}`) are correct: **Menoetes, Alkyoneus (both forms), the three generals
(Dysnomion/Makaria/Trophonios), Neferkha, Enslaver, Devourer, Tantalus (both forms),
Charon (both forms), Mnemophage (shell + core), Ephialtes** - all audit clean
(castable specials at real levels, 0 level-0 specials, 0 dead passives).

Bosses built by a **raw `skillName{i}` loop or `set_field` without `skillLevel{i}`**
(or that overwrote a special) inherited level-0 slots from their clone donor:

| Boss (record) | module/origin | defect |
|---|---|---|
| **Helepolis** `um_helepolis_99` | diadochi | meteor nova **overwrote** `specialAttackSkillName` (was `leveler_turretattack` @80% in the vanilla Leveler) -> the siege cannon never fires; meteor has **no skillName slot** (undefined level); `leveler_missile`/`siegewalker_firespit` shipped in skillName6/7 at **level 0** and unwired = dormant |
| **Dorus** `um_dorus_99` | monolith (Propontis) | `skillName5=svc_dorus_raisecourt` set w/o `skillLevel5` -> **raise-court @55% is level 0** = the King never raises his court |
| **Kravmoloch** `um_kravmoloch_99` | monolith (uplift) | clone of Gorrahk, base kit never re-leveled: `cyclops_groundsmash` (sa2 @45%) + `cyclops_terrifyingroar` (sa3 @35%) at **level 0**; `armor_passive`=0; `character_speedall`=0 |
| **Gorrahk** `um_gorrahk_99` | monolith (obsidian) | same as Kravmoloch (the donor): groundsmash+roar specials at level 0; `armor_passive`=0; `character_speedall`=0 |
| **Ilsevar** `um_ilsevar_99` | monolith (obsidian) | `halimedes_terrifyingroar` (sa4 @35%) at **level 0**; `drxdeathchillaura` aura at level 0 |
| **Toxeus Hunt** `um_toxeus_hunt_99` | toxeus_suite | `skillName{i}` loop w/o `skillLevel{i}`: `boss_conversionimmunity`/`hero_scaling`/`toxeus_passiveproperties` at **level 0** (boss is player-**convertible**) |
| **Vashkarr** `um_vashkarr_99` | monolith (obsidian) | `boss_conversionimmunity`=0 (convertible) + `boss_scaling`=0 |
| **Sarkoth** `um_sarkoth_99` | monolith (obsidian) | `boss_conversionimmunity`=0 (convertible) + `boss_scaling`=0 |
| **Broodmother** `um_broodmother_99` | monolith | `boss_scaling`=0 |

The **Helepolis** miss is the clearest match to "not using skills": the vanilla
Leveler fires `leveler_turretattack` at **80%** as its main special; the diadochi
module replaced that exact slot with the meteor, so the war engine only lobbed the
occasional meteor + spawned proxies and otherwise auto-attacked with its laser.

---

## The fix - `tools/patches/boss_skill_fix.py`

Field edits only (no clones/souls/pets). Levels anchored to the mod's own
well-built bosses (their specials sit at 2-4; boss passives/immunities at 1). **No
damage or stat field is touched.** 25 edits:

### 1. Helepolis - restore the siege battery
- give the meteor a real `skillName9` slot at level 4 (was `NO-SKILLNAME-SLOT`);
- enable `leveler_missile` (skillName6) + `siegewalker_firespit` (skillName7) 0 -> 4;
- **restore the turret** as `specialAttack3` (`leveler_turretattack` @55, AnyRange);
- wire `specialAttack4`=missile @35, `specialAttack5`=firespit @30.
- Result: **2 -> 5 castable specials** (turret/laser[auto-attack]/meteor/missile/firespit/proxy).

### 2. Level-0 special attacks -> enabled
- Dorus `svc_dorus_raisecourt` 0 -> **3** (summon level; Neferkha raisecourt precedent).
- Kravmoloch + Gorrahk `cyclops_groundsmash` 0 -> **4**, `cyclops_terrifyingroar` 0 -> **4**.
- Ilsevar `halimedes_terrifyingroar` 0 -> **4**.

### 3. Level-0 auras/passives -> enabled (minimal/standard level)
- Kravmoloch + Gorrahk `character_speedall` 0 -> **3** (self-aura).
- Ilsevar `drxdeathchillaura` 0 -> **3** (aura).
- Toxeus Hunt `boss_conversionimmunity`/`hero_scaling`/`toxeus_passiveproperties` 0 -> **1**.
- Vashkarr + Sarkoth `boss_conversionimmunity` 0 -> **1**, `boss_scaling` 0 -> **1**.
- Broodmother `boss_scaling` 0 -> **1**.
- Kravmoloch `armor_passive` 0 -> **74** (= charLevel), Gorrahk `armor_passive` 0 -> **40**
  (= normal-difficulty charLevel `[40,58,72]`) - they shipped with **zero** armor
  rating vs every sibling (Vashkarr 75, Broodmother 130, Dorus 62). Set to the
  conservative TQ-standard floor (the boss's own level); they keep their existing
  flat `defensivePhysical=35`.

### Deliberately LEFT (documented, not fixed)
- `globalproperties_epic01/legendary01/_boss` + `all_hpscaling_passive` at level 0
  = the vanilla difficulty-scaling convention (every exemplar ships them at 0).
- **Magnitude %-passives / vestigial non-special skills** at level 0 that are NOT
  wired to fire: `bladenova`, `attack_damagemodifier_02`, `deflectprojectiles_passive`,
  Vashkarr's `svc_vashkarr_summonhorde` + `shieldcharge` (likely deprecated by the C7
  dragonfire uplift), Ilsevar `lifedrain`. Enabling these would change damage/defense
  magnitude or add casts = a rebalance / behavior change, out of scope for a
  skill-usage repair.
- **Ephialtes** (`um_ephialtes_99`) - kit complete; WILL_DECISIONS: deliberately
  single-phase / no summon.
- **Toxeus Hunt's high inherited attack levels** (flashpowder 78, lifedrain 50,
  speedall 40, bladestorm 30): out-of-range monster skill levels clamp to the
  skill's max array entry, so they are **functional (max-power), not broken**;
  reducing them would be a nerf/rebalance. Only the Hunt's dead passives are fixed.

---

## Verification (dry-run replay, no heavy build)

`b39_replay.py` loads a copy of `baseline_build38.arz`, applies `boss_skill_fix.apply`,
runs its `verify()` hook, replays a 2nd time (idempotency), and re-audits:

```
boss_skill_fix: 25 edit(s), 0 miss(es)
boss_skill_fix.verify: OK (no level-0 special attacks on target bosses)
2nd apply SET edits: 0 (idempotent)

boss             BEFORE (cast/lvl0/dead)  AFTER (cast/lvl0/dead)
Helepolis        (2, 0, 0)                (5, 0, 0)
Dorus            (3, 1, 0)                (3, 0, 0)
Kravmoloch       (4, 2, 1)                (4, 0, 0)
Gorrahk          (3, 2, 1)                (3, 0, 0)
Ilsevar          (4, 1, 0)                (4, 0, 0)
Vashkarr         (2, 0, 2)                (2, 0, 0)
Sarkoth          (5, 0, 2)                (5, 0, 0)
Broodmother      (3, 0, 1)                (3, 0, 0)
Toxeus Hunt      (4, 0, 3)                (4, 0, 0)

Surface B pets unchanged (hadesmarshal_1=5, neferkha_1=4, bloodtoxeus_1=5 AI slots)
RESULT: PASS (0 level-0 specials remain on any target)
```

(`cast` = castable specials; `lvl0` = chance>0 specials referencing a level-0 skill;
`dead` = level-0 core passives. Helepolis 2->5 = the restored turret/missile/firespit.
The `cast` count is unchanged for Dorus/Kravmoloch/Gorrahk/Ilsevar because those
specials already resolved at chance>0 - they were counted as "castable" but silently
did nothing at level 0; the meaningful change is `lvl0` -> 0.)

Fast gates: `py -m py_compile` OK; `py tools/patches/_check_registry.py` OK
(**12 modules, order `4c688f58`**).

---

## Registry placement + gate notes

`REGISTRY` insertion: after `damage_display`, immediately **before `visuals`** (which
writes nothing and must stay last). This runs `boss_skill_fix` **last among content
modules**, so it sees the FINAL boss records from the monolith AND every boss-creating
registry module (`four_generals`, `diadochi`, `polis_vault`, `neferkha`, `toxeus_suite`).

Expected **S4b COLLISION warnings** (legal, later-wins): `um_helepolis_99` (diadochi)
and `um_toxeus_hunt_99` (toxeus_suite) are re-edited here. The monolith-created bosses
(Dorus/Kravmoloch/Gorrahk/Vashkarr/Sarkoth/Broodmother) predate the registry, so no
collision is logged for them. The module's `verify()` hook (post-finalization phase)
fails the build loud if any target boss still carries a `chance>0` level-0 special.

The full monolith gate battery (pet parity/gear/skill-kit, boss-kit clone-shape,
spawn-eligibility, soul gates, etc.) runs over these edits in the real DB build; the
module only edits existing monster fields (no clones/souls/pets/tags), so it is
gate-safe by construction. **Confirm on the next full `build_svc_database.py` run.**

---

## Open items for Will / vet

1. **Levels are conservative.** The enabled specials use level 3-4 and passives level
   1 (matching the mod's well-built bosses). If Menoetes-tier magnitude is wanted for
   Kravmoloch/Gorrahk groundsmash/roar, raise `_LVL_SPECIAL`. Toxeus Hunt's
   `toxeus_passiveproperties` is set to 1 (Devourer's value); the Enslaver uses 16 -
   raise if the Hunt should match its L100 sibling.
2. **`armor_passive`** on Kravmoloch/Gorrahk is set to the boss's normal-difficulty
   `charLevel` (74 / 40) as a conservative floor; they also keep flat
   `defensivePhysical=35`. Tune if a specific armor value is intended.
3. Vashkarr's vestigial `svc_vashkarr_summonhorde` (level 0, unwired) was left - if the
   Eldest is meant to still summon its horde alongside the C7 dragonfire kit, that is a
   separate design call (wire it as a special + level).
