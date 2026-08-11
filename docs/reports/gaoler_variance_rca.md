# Alkyoneus the Soul-Gaoler: "unkillable, then killable" RCA

> **REPORT ONLY. NO FIX, NO BUILD, NO DEPLOY.** The planned nerf is cancelled; this document
> exists to answer Will's question with receipts, not to change anything.
> Written 2026-08-11 against the LIVE artifact `local/build83_run1_44499f56.arz`
> (= `work/SoulvizierClassic/database/SoulvizierClassic.arz`, md5 `44499f56...`, 51,253 records,
> the build83 bytes shipped to DEV and Steam on 2026-08-11).

**Will's report:** Alkyoneus the Soul-Gaoler (Prison of Souls, Hades Palace floor 4, two forms
including the Unbound Gaoler) was unkillable on Epic, then died on the second attempt.
*"idk what happened maybe he had better gear on or something."*

---

## THE THREE ANSWERS, UP FRONT

1. **DID HIS RECORDS CHANGE? No. UNCHANGED.** Across 30 preserved arz baselines spanning
   2026-07-09 to the live build83, an exhaustive **unfiltered** field diff of both Gaoler records
   (1,047 and 1,048 fields each) found **three** changes, and **none of them is a combat stat**:
   a soul DROP-rate cut (66 -> 25, a nerf to loot, not a buff to him), and the Warden key pointer
   cleared on both forms. Life, level band, attributes, all five resistances, all ten skill
   name/level pairs, every specialAttack wiring, every equipment table pointer and every
   equip-chance except the soul slot are **byte-identical from the day he was authored to today**.
   He was never buffed. He was never nerfed in combat either.

2. **GEAR-ROLL VARIANCE: far too small to explain it, and the smallest of the peer set bar one.**
   His four worn armour slots are **fixed monster items with no affix randomiser at all**. On Epic
   his worn armour is **1268 every single spawn**, best case 1308 (+3.2%), and that best case needs
   four independent 0.398% rolls (p = 2.5e-10). Compare **Tantalus: 132 to 1467 armour, a +1011%
   swing across five randomised, affix-bearing slots**. The Gaoler is the *least* random uber in the
   set except Charon, who wears nothing.
   **The one exception worth naming:** a 0.398%-per-form torso roll grants **+65 pierce resistance**
   on top of his base 45, i.e. **110% = total pierce immunity**. That is the single roll in his whole
   table that could hard-wall a spear/pierce build. 0.795% across both forms. Real, rare, and the
   only variance in the record that is specific to Will.

3. **VERDICT: it was almost certainly not the boss.** The leading explanation is the encounter's
   *fixed* shape meeting a first-time player: **two forms totalling 35,000 HP on Epic**, where killing
   form 1 spawns a **fresh, full-health** Unbound Gaoler; a **six-strong guard horde** in a sealed
   cell that also feeds his life-drain cascade; a **25% racial damage reduction against 79.8% of the
   mod's summonable pets**; **45% pierce and 30% physical resistance** against a spear build; and
   **600 HP of life-leech every six seconds plus 200 per chained target**. Second attempt: he knew
   there were two bars, and (his own hypothesis) he was better geared. **No action warranted.** One
   OPTIONAL Will-decision is recorded in section 5 and is explicitly not implemented.

---

## 1. METHOD AND EVIDENCE BASE

Two records are in scope, both authored by `tools/patches/polis_vault.py`:

| form | record | role |
|---|---|---|
| 1 (bound) | `records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr` | the Soul-Gaoler; `actorToSpawnOnDeath` -> form 2 |
| 2 (Unbound Gaoler) | `records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr` | the terminal form; carries the soul |

**Baselines diffed (30, oldest to newest).** Every preserved arz in `local/` and
`local/db_backups/` that could contain him:

```
2026-07-09 pre-build30.2   2026-07-09 pre-q3          2026-07-11 build36 map R5
2026-07-14 DEV2 deployed   2026-07-15 build40         2026-07-16 build41
2026-07-16 build43         2026-07-17 build47         2026-07-27 pre-b90
2026-07-28 pre-b91         2026-07-28 pre-b93         2026-07-28 pre-b94
2026-07-28 pre-b94r2       2026-07-28 pre-b99         2026-07-29 pre-b94r3
2026-07-29 pre-b102        2026-07-29 pre-967b1f97    2026-07-30 pre-b104
2026-08-06 pre-ab02f16e    2026-08-06 pre-relictier   2026-08-09 pre-9c190b99
2026-08-10 build75 R180    2026-08-10 build76 ship    2026-08-10 build77 ship
2026-08-10 build78 ship    2026-08-10 build79 ship    2026-08-11 build80 ship
2026-08-11 build81 ship    2026-08-11 build82 run1    2026-08-11 build83 LIVE
```

The records are **absent** from the first three (pre-build37) and **present in all 27 from
2026-07-14 onward**, which matches their birth commit `e076e46` (2026-07-12, "build37 polis_vault").

**How the diff was run.** `tools/arz_patcher.py::ArzDatabase.from_arz` on each baseline; every field
of each record decoded and stringified; **no field filter of any kind** (animation, sound, mesh and
FX fields included, so nothing could hide behind an exclusion); plus a one-hop expansion that also
diffed all 72 records the two Gaolers point at (souls, skills, loot tables, AI controller, sound
paks). Runs were collapsed so a field only prints if its value ever moved.

**The 2026-07-12 to 2026-07-14 gap is closed in git, not the arz.** `git diff e076e46 HEAD --
tools/patches/polis_vault.py` shows **zero** changed lines among the stat constants. The bands
`_PG_BAND = [50, 72, 90]`, `_PG_LIFE1 = [15000, 20000, 27000]`, `_PG_LIFE2 = [11000, 15000, 20000]`,
the five `defensive*` literals and all ten `(skill, [n,e,l])` pairs are byte-identical in the birth
commit and at HEAD.

---

## 2. Q1: DID HIS RECORDS CHANGE?

### VERDICT: UNCHANGED in combat. Two loot-side deltas and nothing else.

Every change found, in the entire life of both records:

| record | field | from | to | first baseline showing the new value | authored by |
|---|---|---|---|---|---|
| `um_polisgaoler_unbound_99` | `chanceToEquipFinger2` | `66.0` | `25.0` | 2026-08-06 `pre-ab02f16e` (last old value 2026-07-30 `pre-b104`) | `933c330` 2026-07-30, R-105/106/107 soul-rate policy |
| `um_polisgaoler_99` | `perPartyMemberDropItemName` | `...\z_wardenofsoulskey.dbr` | *(empty)* | 2026-08-06 `pre-ab02f16e` | `b3f7926` 2026-07-30, R-101 quest items no longer farmable |
| `um_polisgaoler_unbound_99` | `perPartyMemberDropItemName` | `...\z_wardenofsoulskey.dbr` | *(empty)* | 2026-08-06 `pre-ab02f16e` | `b3f7926` (same) |

**Read plainly:**

- `chanceToEquipFinger2` is the **soul slot**, i.e. the soul DROP chance. 66 -> 25 makes the Soul of
  the Gaoler **rarer**. It is a loot nerf. It has **zero** effect on the boss in combat (the soul item
  contributes DA 57 and +18 vitality resistance when it rolls, and it rolls *less* often now).
- `perPartyMemberDropItemName` was the Warden of Souls key. R-101 removed the record entirely
  (`z_wardenofsoulskey.dbr` is present in every baseline up to `pre-b104` and absent from
  `pre-ab02f16e` onward). Drop-side only.

**Fields confirmed NEVER to have moved** (a representative slice of the 1,047 tracked; the full
sweep reports zero changes outside the table above):

```
charLevel                 [50, 72, 90]                      unchanged
characterLife  form1      [15000, 20000, 27000]             unchanged
characterLife  form2      [11000, 15000, 20000]             unchanged
characterStrength 550 / Dexterity 450 / Intelligence 350    unchanged
defensiveLife 70 / defensivePierce 45 / defensivePoison 40  unchanged
defensivePhysical 30 / defensiveBleeding 30                 unchanged
skillName1..10 + skillLevel1..10                            unchanged
specialAttack / 2 / 3 SkillName + Chance                    unchanged
chanceToEquip Head/Torso/LowerBody/Forearm/LeftHand/RightHand = 100  unchanged
chanceToEquipFinger1 1.0 / Misc1 15.0 / Misc2 7.0           unchanged
loot<Slot>Item<N> (every equipment table pointer)           unchanged
scale 3.5 / 3.8, characterRunSpeed, characterAttackSpeed    unchanged
monsterClassification Boss, characterRacialProfile Animal   unchanged
actorToSpawnOnDeath -> um_polisgaoler_unbound_99            unchanged
```

### One-hop records: three cosmetic or Legendary-only deltas

The 72 records he references were diffed on the same terms. Only these moved:

| record | change | effect on the Epic fight |
|---|---|---|
| `polisgaoler_soul_e` / `_l` | `itemQualityTag` added at build77 (`tagSoulEpic` / `tagSoulLegendary`) | none; it renames the dropped soul |
| `xpack\...\finger\unique\finger_l01` | +2 craft-reagent rows at build81 | none on Epic; this is the **Legendary** table, and it sits behind a 1% ring slot |
| `xpack\...\weapons\mastertables\unique_1h_l01` | +1 craft-reagent row at build81 | none on Epic; **Legendary** table behind the 0.29% weapon branch |
| `xpack\...\arcaneformulae\01_act4_arcaneformulae` | +2 rows at build81 | none; Misc2 is a pure drop slot |
| `z_wardenofsoulskey` | record deleted, R-101 | none in combat |

If anything, the Legendary reagent rows make him marginally *weaker* on Legendary (a reagent
occupying a weapon branch is not a weapon). Nothing touches Epic.

**Conclusion for Q1: buffed = no, nerfed in combat = no, unchanged = yes.** Whatever happened to
Will on attempt 1 versus attempt 2, the database did not move between them, and it has not moved
since 2026-07-12 in any way that touches a fight.

---

## 3. Q2: GEAR-ROLL VARIANCE

### 3.1 What he can actually roll (both forms, identical except the soul slot)

A TQ monster fills a slot with probability `chanceToEquip<Slot>`, then picks among
`loot<Slot>Item<N>` by weight `chanceToEquip<Slot>Item<N>`. The table shape matters enormously:

- `LootMasterTable` / `LootItemTable_FixedWeight` -> `lootName<i>` + `lootWeight<i>`, resolving to a
  **fixed** item with fixed stats.
- `LootItemTable_DynWeight` -> `itemNames[]` **plus `prefixRandomizerName*` / `suffixRandomizerName*`**,
  which is what produces **randomly affixed** gear with large stat spread.

**The Gaoler's four armour slots are entirely in the first category.** Measured chain for the torso,
and the head, legs and arms are structurally identical:

```
torso\mastertables\e_gigantes02          LootMasterTable
  |- lootName1 w=1000  torso\monster\e_gigantes02    LootItemTable_FixedWeight
  |     `- m_e_gigantesmelee02   Common  armour 317   (no resists, no affix table)
  `- lootName2 w=4     torso\monster\ei_gigantes02   LootItemTable_FixedWeight
        `- mi_e_gigantesmelee02  Rare    armour 327, defensivePierce +65, DA +150
```

**No `prefixRandomizerName` or `suffixRandomizerName` anywhere in the armour chain.** His armour is
one of exactly two values per slot, and the second is a 4/1004 = **0.398%** roll.

Full Epic equipment map:

| slot | equip chance | Epic tables (weight -> share) | distinct outcomes | armour min..max |
|---|---|---|---|---|
| Head | 100% | `head\mastertables\e_gigantes02` (5000 -> 100%) | 2 | 317 .. 327 |
| Torso | 100% | `torso\mastertables\e_gigantes02` (5000 -> 100%) | 2 | 317 .. 327 |
| LowerBody | 100% | `legs\mastertables\e_gigantes02` (5000 -> 100%) | 2 | 317 .. 327 |
| Forearm | 100% | `arms\mastertables\e_gigantes02` (5000 -> 100%) | 2 | 317 .. 327 |
| LeftHand | 100% | `dyn_1h_e01b` (5000 -> 98.23%), `e_club_gigantes` (75 -> 1.47%), `unique_1h_e01` (15 -> 0.29%) | 13 | 0 (weapons carry no armour) |
| RightHand | 100% | same three | 13 | 0 |
| Finger1 | **1.0%** | `ring_e01b` (5000 -> 99.4%), `finger_e01` (30 -> 0.6%) | 7 | 0 .. 50 |
| Finger2 | 0% (F1) / **25%** (F2) | the soul | 1 | 0 (DA 57, +18 vitality res on F2) |
| Misc1 | 15% | health/mana potions | drop-only | 0 |
| Misc2 | 7% | act3/act4 relics + arcane formulae | drop-only | 0 |

### 3.2 The durability swing, per difficulty

| difficulty | worn armour, worst spawn | expected | best spawn | swing |
|---|---|---|---|---|
| Normal | **500** | 500 | 555 | +55 (11%) |
| **Epic** | **1268** | **1268** | **1358** | **+90 (7%)** |
| Legendary | **2420** | 2420 | 2550 | +130 (5%) |

"Best spawn" includes the 1%-chance Finger1 ring at its 50-armour maximum. **Armour-slot only, the
Epic range is 1268 to 1308, a 3.2% swing**, and reaching 1308 requires all four 0.398% rolls
simultaneously: **p = 2.5e-10**. The expected value equals the minimum to four significant figures.

Resistance rolls available from gear on Epic, each at 0.398% for its own slot:

| slot | rare MI variant | grants |
|---|---|---|
| Torso | `mi_e_gigantesmelee02` | **defensivePierce +65**, DA +150 |
| Forearm | `mi_e_gigantesmelee02` (arms) | defensiveLightning +65, DA +150 |
| LowerBody | `mi_e_gigantesmelee02` (legs) | defensiveFire +65, DA +150 |
| Head | `mi_e_gigantesmelee02` (head) | DA +150, no resistance |

P(at least one MI piece on a given form) = 1 - 0.99602^4 = **1.58%**.
Expected extra resistance from gear, summed over every slot: **fire +0.28, lightning +0.28, pierce
+0.26 percentage points.** That is the honest average contribution of his entire gear roll to his
resistances: about a quarter of one percent.

### 3.3 Peer comparison, Epic

| boss | worn armour worst..best | swing | armour slots with **affix randomisers** | shape |
|---|---|---|---|---|
| **Gaoler F1 / F2** | **1268 .. 1308** | **+40 (3.2%)** | **0** | 4 slots at 100%, all fixed monster items |
| Tantalus F1 / F2 | 132 .. 1467 | **+1335 (1011%)** | 5 | Torso 100%, Head/Legs/Arms 40% each, all `commondynamic` with prefix **and** suffix randomiser tables |
| Charon F1 / F2 | 0 .. 0 | 0 | 0 | wears no armour; all durability is record resistances |
| Ephialtes | 297 .. 753 | +456 (154%) | 1 | 297 fixed from `svc_maskofdread_e` (Misc4, 100%), plus a 1.6% rare-misc slot |
| *(donor)* Warden of Souls | 1268 .. 1308 | +40 (3.2%) | 0 | identical chain; the Gaoler inherited it unmodified |

Two things follow.

- **The Gaoler is the *least* variable armoured uber in the set.** Tantalus's swing is **33x** his in
  absolute armour and **316x** in relative terms, and the Tantalus figure is an *undercount* because
  it excludes the affix rolls his dynamic tables carry and the Gaoler's tables do not have.
- **His variance is not an outlier that needs bounding.** If anything he is the anomalously
  deterministic one.

### 3.4 Weapons: the one place he does roll randomly, and it is offence not defence

Both hands (100% equip each, dual wield) roll:

| branch | share | resolves to |
|---|---|---|
| `dyn_1h_e01b` | 98.23% | common dynamic axes / clubs / swords, **each behind prefix and suffix randomiser tables** (the club prefix table `cluba_e03` alone offers 22 weighted affixes) |
| `e_club_gigantes` | 1.47% | `mi_e_gigantes`, Rare monster club, 156-175 physical |
| `unique_1h_e01` | 0.29% | epic unique axes/clubs/swords |

So his **damage output** genuinely varies spawn to spawn via weapon affixes. This can plausibly make
him hit harder on one attempt than another. It does **not** make him harder to kill, and Will's
report was that he could not kill *him*, not that he kept dying to a damage spike.

### 3.5 Answer to Q2

**Is fight-to-fight gear variance big enough to explain "unkillable then killable"? No.** A 3.2%
armour swing at the p=2.5e-10 extreme, and a quarter-percentage-point average resistance
contribution, cannot flip an encounter from impossible to winnable.

**With one caveat, stated because it is the only variance in his table that is specific to Will's
build:** the torso MI grants `defensivePierce +65`. On top of his fixed base of 45 that is **110%
pierce resistance, i.e. total immunity to pierce damage**. Will's character is a spear user (R-107,
Will's own words, and the reason the Devourer walled him). Probability **0.398% per form, 0.795%
across the two-form encounter**. At roughly 1 in 126 it is not the likely story, but it is the one
mechanism by which "he had better gear on" would have been literally true, and it deserves to be on
the record rather than waved away.

---

## 4. Q3: VERDICT

### 4.1 What is actually hard about this fight, and all of it is FIXED

Measured on Epic from the live build83 record:

| wall | value | note |
|---|---|---|
| **Two forms** | form1 **20,000** HP, on death spawns form2 at a **full 15,000** | **35,000 raw HP** in two bars (26,000 Normal / 47,000 Legendary). `actorToSpawnOnDeath` means the second bar is a brand new actor at full health |
| Armour | **1268** every spawn | his record carries **no** `defensiveProtection`; `armor_passive` at his Epic level contributes **2** points. All of it is the four fixed gigantes pieces |
| Resistances | vitality **70%**, pierce **45%**, poison **40%**, physical **30%**, bleeding **30%** | never changed since authoring |
| Racial wall | `hero_scaling` L2 on Epic: **25% damage reduction** from attackers of race Undead / Beast / Magical / Beastman / Insectoid / Plant / Demon | **574 of 719 (79.8%)** of the mod's pet records carry one of those races. A pet-led attempt is quietly 25% weaker; a weapon-led attempt is not |
| His own race | `Animal` | only **18** creature records in the whole mod use it. The standard player "+% damage to <race>" bonuses do not name it, so almost no racial damage bonus applies to him |
| Self-heal | `hero_lifedrain` L6 = **600 life leech per cast**, 6s cooldown, 80% special-attack chance (85% on form 2) | plus `hero_lifedrain_cascade` L6 = **200 per chained target**, 66% spark chance |
| Crowd-fed sustain | every extra body in the cell is another cascade chain | the horde and the player's own pets **feed his healing** |
| Soft-CC immunity | `boss_conversionimmunity`: convert / confuse / fear / petrify / sleep / taunt / disruption all 100%; `defensivePercentCurrentLife` 96%; `defensiveSlowLifeLeach` 50% | %-current-life damage and life-leech-over-time builds are near-useless against him |
| Guard horde | 4 dedicated add proxies + 2 native `ss_warden_behemoth` in a sealed cell | `am_vindicator_45` (Champion), `xhero_polybotes_47` (Hero, 16,140 HP on Epic), `um_prox_47` (Hero), `as_bloodwitch_43` (Champion) |
| Spawn control | `limit_polisgaoler` min/max player level **1..110 on all three difficulties**, pool `spawnMin=spawnMax=1` | he always spawns, always exactly one, on every difficulty. No spawn lottery |

### 4.2 Most likely explanation, ranked

1. **The two-form structure met a first-time player.** 35,000 HP on Epic delivered as two bars, where
   emptying the first one produces a *fresh full-health* Unbound Gaoler at a different scale and with
   a heavier special-attack cadence (spirit-wave 65% -> 80%, slam 45% -> 55%). The first time that
   happens it reads as "I killed him and he came back, he is unkillable." The second time you know
   it is two bars and you pace the fight. This alone accounts for the reported experience without
   anything else changing.
2. **Encounter state, not boss state.** Six guarded adds in a sealed cell, and every one of them is
   also a `hero_lifedrain_cascade` chain target worth 200 HP back to the boss per chain. Whether the
   adds were up, whether the player fought at the door or in the middle, and whether pets were alive
   changes the effective difficulty by far more than any roll on his equipment table.
3. **A build-specific wall that is always there.** 45% pierce and 30% physical against a spear build;
   `Animal` race so racial damage bonuses do not fire; 25% racial reduction against ~80% of
   summonable pets. This is the same shape as R-107's Devourer finding (spear build into 70% pierce),
   and it means his *effective* difficulty for Will is well above his nominal difficulty. It does
   not vary between attempts, but it sets the level at which small changes flip the outcome.
4. **Will's own hypothesis, and it is a good one: his gear.** He farms the Gaoler cage chests, which
   were widened for armour at build80 and build83. A better-geared attempt 2 is entirely plausible
   and is the most ordinary explanation of all.
5. **The boss's own gear roll. Last, and quantified.** 1268 vs 1308 armour, expected extra resistance
   of a quarter of a percentage point. The **only** roll that could matter to him is the 0.795%
   torso-MI pierce immunity. It cannot be ruled out; it is not where the money is.

### 4.3 Is any action warranted?

**No. Nothing is warranted and nothing is recommended.** The records did not change, the variance is
the smallest in the peer set, the fight is behaving exactly as `polis_vault.py` authored it in
build37, and Will killed him. The cancelled nerf should stay cancelled.

---

## 5. OPTIONAL WILL-DECISION (NOT IMPLEMENTED, NOT RECOMMENDED)

Recorded only because section 3.5 turned it up and dropping a finding is against standing practice.

**OPTIONAL-1: bound the pierce-immunity roll.** If Will ever wants the one build-relevant roll
capped, the shape of the fix matters more than the number:

- The item is `records\xpack\item\equipmentarmor\torso\mi_e_gigantesmelee02.dbr`
  (`defensivePierce 65`, armour 327, DA 150). It is reachable only through
  `torso\monster\ei_gigantes02` <- `torso\mastertables\e_gigantes02`.
- **That master table is worn by 10 creature records**, including `am_dactyl_43/45`,
  `am_vindicator_41/43/45`, `xhero_polybotes_47`, `xhero_ephialtes_47` and the donor
  `xsecrethero_wardenofsouls_48`. Two of those (`am_vindicator_45`, `xhero_polybotes_47`) are the
  Gaoler's **own horde adds**.
- **Editing the item or the shared table would silently retune the eight non-Gaoler wearers.** That is
  exactly the failure mode R-107 PART 2 and the `genericbossorb_04` lesson exist to prevent.
- The **monster-local** options, if it is ever wanted, are: (a) lower his base `defensivePierce` so
  45 + 65 lands under 100, or (b) point his Torso slot at a private clone of the master table with
  the MI branch dropped. Either would need its own gate under the no-new-surface-without-a-gate law.

**OPTIONAL-2: an observation, not a request.** The 25% racial damage reduction that hits 79.8% of
summonable pets comes from stock `hero_scaling`, which is referenced by **766 records** across the
whole mod. It is not a Gaoler defect and **must not be edited in place** under any circumstances.
It is noted here purely so the next person reading "why do my pets feel useless on this boss" finds
the answer already measured.

---

## 6. WHAT THIS REPORT DOES NOT PROVE

- **No in-game telemetry exists.** Everything here is measured from the shipped database bytes and
  from git. It cannot tell you what was on screen during Will's two attempts.
- **The horde placement is taken from `polis_vault.py`'s documented contract** (one instance each of
  four add proxies plus two native `ss_warden_behemoth` at H1..H6). It was not re-derived from
  `Levels.arc` for this report.
- **Player-side state was not measured** (character level, gear, resistances, active pets on either
  attempt). Items 2 and 4 in the ranking are therefore reasoned, not measured, and are labelled as
  such.
- Difficulty totals are raw `characterLife` from the record. TQAE's global per-difficulty monster
  scaling is applied by the engine on top and is identical for every monster, so it does not affect
  any comparison drawn here.

## 7. HOW TO REPRODUCE

All numbers came from `tools/arz_patcher.py::ArzDatabase.from_arz` reading the arz files listed in
section 1 directly. The probes were written to the session scratchpad (ephemeral, not committed) and
do the following, each of which is a few dozen lines against that one API:

1. **Timeline diff.** Load every baseline, decode all fields of both Gaoler records with **no
   filter**, collapse identical consecutive values into runs, print any field with more than one run.
   Repeat with a one-hop expansion over every `.dbr` the records reference.
2. **Gear resolution.** For each `chanceToEquip<Slot>` read the matching `loot<Slot>Item<N>` (a
   3-element array indexed Normal / Epic / Legendary) and its weight, then resolve the table
   recursively, handling **both** table shapes: `lootName<i>`/`lootWeight<i>` for
   MasterTable/FixedWeight, and `itemNames[]` plus `prefixRandomizerName<i>` / `suffixRandomizerName<i>`
   for DynWeight. Missing the second shape makes a randomised boss look deterministic.
3. **Peer comparison.** Same routine over `um_tantalus_99/_unbound_99`,
   `um_charon_ferryman_99/um_charonform2_ferryman_99`, `um_ephialtes_99` and the donor.
4. **Racial census.** Count `characterRacialProfile` over every record under `\pets\` and over every
   creature record, and cross-reference against `hero_scaling`'s `racialBonusRace` list.
