# b39 - New-boss skill-wiring RCA + fix (round 2)

**Report:** boss-skill usage audit across every new boss, both combat surfaces.
**Branch:** `feat/b39-boss-skills` (module `boss_skill_fix.py`; commits `177c3aa` + `e057e39`).
**Baseline audited:** `baseline_build38.arz` = **build38-DEV** arz `fcd5dcab40359aa94b421dd8cef4b81e`
(55,339,563 B, 51,007 records). See "Baseline provenance" below - this is build38-dev, NOT
build38a; the delta between them is provably disjoint from every boss touched here.
**Fix:** `tools/patches/boss_skill_fix.py` (registry module) + `tools/debug/b39_boss_skill_audit.py`
(read-only A/B probe) + `tools/debug/b39_boss_skill_replay.py` (dry-run + fail-loud proof).
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
  (`_build_boss_summon` + `_mirror_source_skill_kit`) carries its source boss's
  animation+skill kit with castable specials that all resolve, is permanent (TTL
  absent) with a sane `petLimit`. 17 summon families audited, all pass.
- **Surface A (fought bosses): a level-0 skill-wiring defect on 10 apex bosses.**
  Uniform root cause: a builder set `skillName{i}` on a cloned donor **without** the
  matching `skillLevel{i}`, so the new skill inherited the donor's empty (**level 0**)
  slot. Plus Helepolis, whose signature **turret barrage was displaced** by a meteor nova.
- **Fix:** `boss_skill_fix.py` makes **27 field edits over 10 bosses** at **per-skill
  donor-matched levels** (skill levels + Helepolis's turret slot only - no clones, no
  souls, no pets, no damage/stat changes). A **roster-derived, fail-loud `verify()`**
  scans every `um_*_99` apex boss and refuses to ship any chance>0 level-0 special, so a
  missed/new boss can no longer slip through. Dry-run replay confirms 0 level-0 specials
  remain across the whole roster; idempotent; pets untouched.

---

## Round-2 corrections (this round fixes the round-1 module's own gaps)

| Vet finding | Correction in this round |
|---|---|
| **CRITICAL - missed `um_voranthys_99`** | Added. It was the single worst-affected boss (whole kit at level 0): 4 chance>0 level-0 specials + 2 dead passives, all now wired. |
| **HIGH - hardcoded 9-boss list; a miss can't be caught** | `verify()` is now **roster-derived**: it scans every `um_*_99` monster record and fails loud on ANY chance>0 level-0 special (and names any boss not in the fix table). A negative test proves an uncovered planted defect is caught. |
| **MEDIUM - blanket `_LVL_SPECIAL=4` not evidence-based** | Every enabled skill now takes its **donor level** (the level the skill sits at on the boss that natively uses it), cited per skill. The "vanilla invariant" claim is corrected below - vanilla DOES ship level-0 AttackProjectile specials, so the fail-loud scan is scoped to `um_*_99` (mod-only). |
| **LOW - baseline mislabeled** | Corrected: the file is build38-**dev** `fcd5dcab`, not build38a `6631f252`. Delta is disjoint (see below); flagged for re-verify vs the true build38a on the next heavy build. |

---

## Method

`tools/debug/b39_boss_skill_audit.py` loads a built `.arz` and dumps, per boss, Surface A
(`monsterClassification`, `initialSkillName`, `attackSkillName`, every `skillName{N}`/
`skillLevel{N}`, every `specialAttack[N]SkillName`+`Chance`+`Range`, resolve check, the
level of each special's referenced skill, and flags `LEVEL0-SPECIAL` / `NO-SKILLNAME-SLOT`
/ dead core passives) and Surface B (each summoned pet's AI slots + `petLimit` + TTL).
The roster + donor levels were independently re-derived directly from the arz.

### Level-0 semantics (corrected - the round-1 "vanilla invariant" was overstated)

The round-1 report asserted active attack skills are ALWAYS level>=1 in vanilla and that
any chance>0 level-0 special is a defect. **That is false and has vanilla false positives**
- an arz-wide sweep shows unmodified vanilla ships chance>0 level-0 `AttackProjectile[Ring]`
specials (`boss_dragonliche_57/60/63` dragonliche_freezingbreath@15%/buffetingwings@21%,
`spiderblackwidow01` venomnova@50%, `jg7_undeadbrother_mage_*` monster_thunderball@50%). The
correct, evidence-backed distinction is by skill **CLASS**:

- **Summon specials** (`Skill_SpawnPet` / `Skill_SpawnPetMonster` / `Skill_AttackProjectileSpawnPet`):
  a level-0 summon **never fires**. Proof: across the whole build38 arz, **ZERO** vanilla
  monster ships a chance>0 SpawnPet special at level 0 (min level = 1). Every level-0 SpawnPet
  special in the DB belongs to one of these `um_*_99` mod bosses. So a level-0 summon special
  is an **unambiguous "boss never summons" defect**.
- **AttackProjectile[Ring]** specials at level 0 **clamp to base magnitude and DO fire**, but
  the mod's donor/design level is higher; a boss firing its whole kit at base is the mis-built
  symptom. These are enabled to the donor magnitude (restoring the forgotten `skillLevel`), not
  a damage rebalance.
- **Passives / auras** at level 0 apply **no effect** (their bonus lives in per-level arrays;
  level 0 = nothing). `boss_conversionimmunity=0` is also a correctness bug (boss is convertible).

Because "chance>0 level-0 special" is not a universal defect signal, the fail-loud roster scan
is **scoped to the `um_*_99` mod apex-boss naming convention** (all mod-authored) so it never
trips on a vanilla record.

---

## Surface B - HEALTHY (no fix)

`_build_boss_summon` copies ONLY the source monster's animation + skill fields onto a Lyia-pet
baseline and calls `_mirror_source_skill_kit`, honoring every crash law (never Monster.tpl
equipment onto Pet.tpl; permanent = TTL removed). All pets carry the mirrored kit with castable
specials, all resolve, TTL absent (permanent), petLimit sane:

| Summon soul | source | pet AI slots (castable) |
|---|---|---|
| Menoetes / Marshal | svc_um_hadesmarshal_80 | 5 |
| Neferkha | um_neferkha_99 | 4 |
| Enslaver (pet-of-pet) | um_toxeus_enslaver_99 | 6 |
| Devourer / Blood Toxeus | um_bloodtoxeus_99 | 5 |
| Tantalus shade | xhero_aberkios_43 | 4 |
| Charon oarsman | charon_minion_30 | 2 |
| Mnemophage phantasm | (epiales) | 3 |
| Broodmother (+ wyrmling) | um_broodmother_99 | 4 (+2) |
| Kravmoloch warden | um_gorrahk_99 | 4 |
| Voranthys | um_sepulchralwyrm_31 | 2 |
| Eater of Days / Pygmalion / Sarpedon / Long Nu / Meritamen | (various) | 4-6 each |

**Note:** a pet's kit levels are re-registered by `_register_pet_skill`, NOT inherited from the
source boss's level-0 slots, so the surface-A bug never propagates into the summoned form. This
is why Will can see the fought boss "not use skills" while the summoned pet works.

---

## Surface A - the defect (full roster, roster-derived)

Bosses built with `_svc_set_kit(...)` (which sets **both** `skillName{i}` **and** `skillLevel{i}`)
audit clean: **Menoetes, Alkyoneus (both forms), the three generals (Dysnomion/Makaria/Trophonios),
Neferkha, Enslaver, Devourer, Tantalus (both forms), Charon (both forms), Mnemophage (shell+core),
Ephialtes**.

Bosses built by a **raw `skillName{i}` loop / `set_field` without `skillLevel{i}`** (or that
overwrote a special) inherited level-0 slots. Independently re-deriving the roster from the arz
finds **24 `um_*_99` monster records**; the **10** below carry the defect (round-1 fixed 9 and
**missed Voranthys**):

| Boss (record) | origin / donor | defect (level-0, chance>0 special OR dead passive) |
|---|---|---|
| **Voranthys** `questbosses\um_voranthys_99` | monolith (obsidian) / boss_dragonliche_57 | **WHOLE KIT level 0.** sa1 dragonliche_freezingbreath@70, sa2 alastor_summonskeletonwarrior@55, sa3 alastor_summonskeletonarcher@45, sa4 aktaios_summontombguardians@40 - all level 0 (3 are summons = never fire); boss_conversionimmunity=0 (convertible) + boss_scaling=0 |
| **Helepolis** `siegestrider\um_helepolis_99` | diadochi / um_leveler_43 | meteor nova **overwrote** `specialAttackSkillName` (donor = leveler_turretattack@80%) -> the siege cannon never fires; meteor itself is slotless (undefined level) |
| **Dorus** `lostsoul\um_dorus_99` | monolith (Propontis) | svc_dorus_raisecourt (sa3 @55) at level 0 = the King never raises his court |
| **Kravmoloch** `skeleton\um_kravmoloch_99` | monolith (uplift, clone of Gorrahk) | cyclops_groundsmash (sa2 @45) + cyclops_terrifyingroar (sa3 @35) at level 0; armor_passive=0; character_speedall aura=0 |
| **Gorrahk** `skeleton\um_gorrahk_99` | monolith (obsidian) | same as Kravmoloch: groundsmash+roar level 0; armor_passive=0; character_speedall=0 |
| **Ilsevar** `skeleton\um_ilsevar_99` | monolith (obsidian) | halimedes_terrifyingroar (sa4 @35) at level 0; drxdeathchillaura aura=0 |
| **Toxeus Hunt** `shadowstalker\um_toxeus_hunt_99` | toxeus_suite | boss_conversionimmunity / hero_scaling / toxeus_passiveproperties at level 0 (boss is convertible) |
| **Vashkarr** `dragonian\um_vashkarr_99` | monolith (obsidian) | boss_conversionimmunity=0 (convertible) + boss_scaling=0 |
| **Sarkoth** `abyssalliche\um_sarkoth_99` | monolith (obsidian) | boss_conversionimmunity=0 (convertible) + boss_scaling=0 |
| **Broodmother** `sepulchralwyrm\um_broodmother_99` | monolith | boss_scaling=0 |

The other 14 `um_*_99` (Neferkha, Enslaver, both Charon, Ephialtes, both Mnemophage, both Gaoler,
both Tantalus, Bloodtoxeus, Toxeus goat, enslaver_marauder) carry **no** chance>0 level-0 special.

---

## The fix - `tools/patches/boss_skill_fix.py`

Field edits only (no clones/souls/pets). **Every level is DONOR-MATCHED per skill** (the level the
skill sits at on the boss that natively/canonically uses it), never a blanket constant. **No damage
or stat field is touched.** 27 edits over 10 bosses:

### Level-0 specials the AI casts -> enabled at the donor level
| boss | skill | -> level | evidence (donor) |
|---|---|---|---|
| Voranthys | dragonliche_freezingbreath | 2 | um_neferkha_99 (cold-apex sibling; sole positive carrier) |
| Voranthys | alastor_summonskeletonwarrior | 2 | boss_necromancer_alastor_18 (native Alastor) |
| Voranthys | alastor_summonskeletonarcher | 2 | boss_necromancer_alastor_18 |
| Voranthys | aktaios_summontombguardians | 1 | boss_egypttelkine_aktaios_27 (native Aktaios) |
| Gorrahk / Kravmoloch | cyclops_groundsmash | 4 | the mod's OWN design magnitude (soul-grant tier 3/4/5, central) |
| Gorrahk / Kravmoloch | cyclops_terrifyingroar | 8 | bm_eldercyclops_33/36 (native elder cyclops; tier 8-10, low end) |
| Ilsevar | halimedes_terrifyingroar | 3 | um_vashkarr_99 (sibling apex; carries it @3) |
| Dorus | svc_dorus_raisecourt | 1 | its own `skillMaxLevel`=1 (1 is the only functional level) |

### Level-0 auras -> enabled
- Gorrahk / Kravmoloch `character_speedall` 0 -> **3** (um_vashkarr_99 carries it @3).
- Ilsevar `drxdeathchillaura` 0 -> **3** (standard aura-enable, matching the character_speedall precedent).

### Level-0 core passives -> enabled @1 (the standard boss-passive floor; a binary enable)
- Voranthys / Toxeus Hunt / Vashkarr / Sarkoth `boss_conversionimmunity` 0 -> **1** (also fixes convertibility).
- Voranthys / Vashkarr / Sarkoth / Broodmother `boss_scaling` 0 -> **1**.
- Toxeus Hunt `hero_scaling` 0 -> **1**, `toxeus_passiveproperties` 0 -> **1**.
- Gorrahk `armor_passive` 0 -> **40**, Kravmoloch `armor_passive` 0 -> **74** (= charLevel; they shipped
  with ZERO armor rating vs every sibling - Vashkarr 75, Ilsevar 39, Dorus 62; armor_passive is a
  defensive passive, not a damage field).

### Helepolis - restore the displaced siege cannon (donor-faithful, minimal)
- give the meteor (currently the slotless bare `specialAttackSkillName`) a real `skillName9` slot at
  its donor level **9** (xhero_ironskin_41), so it fires at intended magnitude;
- re-wire the **turret** (already level 5 in skillName1) into `specialAttack3` @ **80%** (the leveler
  donor's turret chance) - the cannon fires again. Result: 2 -> **3** castable specials.

### Deliberately LEFT (documented, NOT fixed)
- `globalproperties_epic01/legendary01/_boss` + `all_hpscaling_passive` at level 0 = the vanilla
  difficulty-scaling convention (every exemplar ships them at 0).
- Level-0 kit skills **not wired as an active special and not a boss passive/aura**: Voranthys
  sepulchralwyrm_firebreath / dragonliche_decomposition / dragonliche_buffetingwings / ondeath_spawnskeleton
  / ondeath_necronova; Gorrahk/Kravmoloch attack_damagemodifier_02 / bladenova; Ilsevar lifedrain;
  Vashkarr svc_vashkarr_summonhorde / shieldcharge / deflectprojectiles / lowhealth_berserkerrage01;
  Helepolis **leveler_missile** (mod-only, no donor) / **siegewalker_firespit**. These are dormant kit
  slots (a valid state); enabling them would ADD casts / death-spawns / defense the boss is not
  configured to use = a behavior change, out of scope for a skill-usage repair. The roster scan does
  not flag them (they carry no special).
- **Ephialtes** (WILL_DECISIONS: deliberately single-phase / no summon) - kit complete.
- **Toxeus Hunt's high inherited ATTACK levels** (flashpowder 78, lifedrain 50, ...) clamp to the
  skill's max array entry -> functional (max-power), not broken; only the Hunt's dead passives are enabled.

---

## Verification (dry-run replay, no heavy build)

`py tools/debug/b39_boss_skill_replay.py baseline_build38.arz` loads a copy, applies
`boss_skill_fix.apply`, runs its roster-derived `verify()`, proves idempotency, and re-audits:

```
boss_skill_fix: 27 edit(s), 0 miss(es)
boss_skill_fix.verify: OK (roster um_*_99 clean of level-0 specials; all enables survived finalization)
2nd apply SET edits: 0 (idempotent)

boss           BEFORE (cast/lvl0/dead)   AFTER (cast/lvl0/dead)
Helepolis      (2, 0, 0)                 (3, 0, 0)     <- turret restored
Voranthys      (4, 4, 2)                 (4, 0, 0)     <- 4 specials wired + 2 passives
Dorus          (3, 1, 0)                 (3, 0, 0)
Kravmoloch     (4, 2, 1)                 (4, 0, 0)
Gorrahk        (3, 2, 1)                 (3, 0, 0)
Ilsevar        (4, 1, 0)                 (4, 0, 0)
Vashkarr       (2, 0, 2)                 (2, 0, 0)
Sarkoth        (5, 0, 2)                 (5, 0, 0)
Broodmother    (3, 0, 1)                 (3, 0, 0)
Toxeus Hunt    (4, 0, 3)                 (4, 0, 0)

ROSTER-WIDE: um_*_99 scanned: 24 ; with chance>0 level-0 special: 0
SURFACE B pets untouched (hadesmarshal_1=5, neferkha_1=4, voranthys_1=2, bloodtoxeus_1=5 AI slots)
NEGATIVE TEST: PASS  (planted level-0 special on an UNCOVERED boss um_polisgaoler_99 -> verify() raises:
  "UNCOVERED apex boss(es) with a level-0 special (add to boss_skill_fix): um_polisgaoler_99.dbr")
RESULT: PASS
```

(`cast` = castable specials; `lvl0` = chance>0 specials referencing a level-0 skill; `dead` = level-0
core passives. The `cast` count is unchanged for Dorus/Kravmoloch/Gorrahk/Ilsevar because those
specials already resolved at chance>0 - they were counted "castable" but silently did nothing at
level 0; the meaningful change is `lvl0` + `dead` -> 0. The **negative test** is the round-2 proof
that a missed/new boss is now caught by the build itself, not a human list.)

Fast gates: `py -m py_compile` OK; `py tools/patches/_check_registry.py` OK (**12 modules, order `4c688f58`**).

---

## Baseline provenance (LOW finding)

`baseline_build38.arz` on disk is md5 `fcd5dcab40359aa94b421dd8cef4b81e` (55,339,563 B) = **build38-DEV**,
not build38a `6631f252` (55,340,923 B). Per `docs/BACKLOG.md` (BUILD38A GATE RECORD), build38a
SUPERSEDES build38-dev via a **DB-only** change: **345 `records\xpack\proxieshades\...` Hades stalker
spawn pools** each gaining `limitN=1` (Int) on the Hunt's name slot (+1,360 B; 0 ADDED / 0 REMOVED /
345 CHANGED, zero unexplained). That delta touches **only spawn-pool records** and is **provably
disjoint** from all 10 boss monster records this module edits, so the dry-run conclusions are
unaffected. **Action:** re-run `b39_boss_skill_replay.py` against the true build38a arz (or fold it
into the next full `build_svc_database.py`) as a belt-and-suspenders confirmation.

---

## Registry placement + gate notes

`REGISTRY` position: after `damage_display`, immediately **before `visuals`** (which writes nothing
and must stay last). This runs `boss_skill_fix` **last among content modules**, so it sees the FINAL
boss records from the monolith AND every boss-creating module (four_generals, diadochi, polis_vault,
neferkha, toxeus_suite).

Expected **S4b COLLISION warnings** (legal, later-wins): `um_helepolis_99` (diadochi) and
`um_toxeus_hunt_99` (toxeus_suite) are re-edited here. The monolith-created bosses predate the
registry, so no collision is logged for them. The FINALIZATION-phase **Ground Smash de-filler**
(`run_registry_gates` -> `_defiller_ground_smash`) touches only SOUL `equipmentring` `itemSkillName`
fields, never these monster `skillLevel` fields - **provably disjoint**, so it cannot re-zero a fix.

The module's `verify()` hook (post-finalization phase) is **roster-derived and fail-loud**: it aborts
the build if ANY `um_*_99` boss carries a chance>0 level-0 special (catching a missed/new boss or a
finalization regression) and re-asserts every enable this module made survived finalization. The full
monolith gate battery also runs over these edits; the module only edits existing monster fields (no
clones/souls/pets/tags), so it is gate-safe by construction. **Confirm on the next full
`build_svc_database.py` run.**

---

## Open items for Will / vet

1. **Levels are donor-matched + conservative.** Summon/aura/passive levels are the donor or the
   standard floor; the two cyclops attack specials use the elder-cyclops donor tier (roar 8) and the
   mod's own soul-grant tier (groundsmash 4). If a specific magnitude is wanted for any, it is a
   one-line table edit.
2. **`armor_passive`** on Gorrahk/Kravmoloch = charLevel (40/74) as a conservative floor (siblings
   vary 10-147); they keep their existing flat `defensivePhysical=35`.
3. **Helepolis leveler_missile / siegewalker_firespit** left dormant (missile has no donor at all;
   both are absent from the leveler donor). If the "Taker of Cities" is meant to barrage with them
   too, that is a deliberate design add (wire each as a special + donor level) - flagged, not done.
4. **Voranthys ondeath skills** (ondeath_spawnskeleton / ondeath_necronova) left at level 0 - a
   death-spawn/nova behavior add, out of scope for the "not using skills in combat" repair.
