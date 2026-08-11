# CHEST_DROP_MATRIX.md - what the chests can and cannot drop

> **Will's questions (2026-08-10):** *"so what did you change for the chests? do the chests drop
> the potions to craft uber weapons? what legendary items can they drop and which ones can they
> not? what legendary armor and other equipment can they drop and what can they not? how does
> this generalize across the game?"*
>
> **Every number below was parsed out of the arz that is live on DEV and on Steam right now**
> (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, md5 `16994072e1cb244af9f4d759309162cb`,
> 55,549,261 bytes, 51,234 records, build76/77 era). Nothing here is copied from an older report.
> The R-180 gate was re-run against this exact file and passes: 51 chest tables, all 6 weapon
> classes, pools n 181 / e 111-116 / l 308. Those figures match the R-180 build record exactly.

---

## 1. What changed for the chests (R-180, short version)

Before, **every** chest in the mod shared one collapsed weapon row. It was a copy of the DRX
blood-cave donor table, and that donor's "unique weapon" entry (`unique_1h_*01`) has exactly three
children: **axe, club, sword**. The donor patched around two of the missing classes by naming bow
and staff directly, and forgot the third: **spear**. So a legendary spear was not unlucky, it was
impossible. Twenty-four legendary spears sat in the database that no chest in the mod could ever
pay. On top of that, only the one guaranteed slot fired reliably, so every chest handed you the
same kind of thing every time.

Three things were changed, all additive (nothing was removed, no drop chance was lowered, the
guaranteed slot is still 100%):

| Change | Before | After |
|---|---|---|
| **All six weapon classes reachable.** A new aggregate table `svc_unique_weapons_{n,e,l}01` names unique 1H **+ spear + bow + staff** plus the base game's three act-level masters. It goes into the one free member slot of the weapon row, and the guaranteed weapon slot is re-aimed onto it at the same weight. | axe / mace / sword only | axe, mace, sword, **spear**, bow, staff |
| **More slots actually fire.** Weapon row 14% -> 40%, shield row 14% -> 30%. | ~1.13 non-guaranteed items per open | ~1.55 per open (+37%), plus the guaranteed one |
| **The six cage chests stop mirroring each other.** Each placed chest now picks one of three **themes** at spawn (50/25/25), so it rolls a different character on a later playthrough. | one pool, two near-identical records | 18 themed containers, no two field-identical |

The themes, read straight out of the shipped records:

| Chest | Theme (weight) | Guaranteed slot names |
|---|---|---|
| Cage chest 01 | **martial** (50) | broad master + **spear** + unique 1H |
| Cage chest 01 | **hunter** (25) | broad master + **bow** + **spear** |
| Cage chest 01 | **warden** (25) | broad master + **shield** + **torso armour** |
| Cage chest 03 | **apex** (50) | relic + broad master |
| Cage chest 03 | **adept** (25) | relic + broad master + **staff** |
| Cage chest 03 | **sovereign** (25) | relic + broad master + **amulet** + **ring** |

**Important nuance:** the theme changes *what you are likely to get*, not *what is possible*. All
three variants of a given chest and difficulty reach the exact same pool (308 legendary items on
Legendary). The theme biases the guaranteed slot.

Measured pool sizes, per chest, per difficulty:

| Difficulty | Item grade the chest pays | Distinct items reachable | Was, before R-180 |
|---|---|---:|---:|
| Normal | Epic | **181** | 99 |
| Epic | Legendary | **111** (red-uber orb chests: 116) | 90 |
| Legendary | Legendary | **308** | 258 |

---

## 2. "The potions to craft uber weapons"

### Short answer

**There is no potion anywhere in the uber-craft chain.** Nothing you drink or throw is ever a craft
component in this mod. What the uber craftables actually need is:

1. a **Mythic Formula** (a scroll, the recipe), and
2. **three reagent items** (existing weapons / armour / jewellery / artifacts you have to find).

Taking the question as "can I farm the chests for the stuff that makes the uber weapons", the
answer is:

| Craft component | Do the chests drop it? |
|---|---|
| **Mythic Formulas** (the recipes) | **YES. All 42 of them, from every Epic-tier and Legendary-tier mod chest and boss hoard.** Zero from Normal-tier chests. |
| **Reagents** | **Partly. 42 of the 78 distinct reagents drop from a Legendary-tier chest; 19 from an Epic-tier chest; 0 from Normal.** |
| **The finished uber weapon itself** | **NEVER, by design.** All 42 are craft-only; no chest, hoard or monster in the game drops one. |
| Ordinary potions and scrolls | Yes, incidentally. Each chest reaches 9 mana-potion records, 1 health-potion record and 9 to 12 spell scrolls. |
| **Relics** (Essence / Embodiment / Incarnation) | Yes, 17 per chest, and always the right tier for the difficulty. |
| **Charms** | **NEVER.** 122 charm records exist; not one is reachable from any mod chest at any difficulty. |
| **Artifacts** (the equippable ones) | **NEVER.** 292 artifact records; 0 reachable. 80 of them are craft-only, the rest sit on base-game tables. Merc scrolls and spell scrolls (also technically "artifacts") do drop. |

### The uber-craft system as it stands today

The uber craftables are the DRX **"supra"** tier, the red-name items made at the Enchanter. There
are **42 of them now** (the 2026-07 audit found 25; the mod has since added 17 `svc_wep_*` ones),
built by 59 formula records. Every craftable has at least one chest-droppable formula.

Per craftable, how many of its three reagents you can farm from a Legendary-tier chest:

| Reagents from a chest | Craftables |
|---|---|
| **3 of 3** | Band of the Elder Savage |
| **2 of 3** | 31 craftables, including **Blood Whisper** (the bleed spear), **Paragon of Violence**, Shrike, Stormbringer, Omega, Agathodaemon, Darkflame Devourer, Titan Crest |
| **1 of 3** | Ares Endless Assault, Void Prism, Ananke's Ring |
| **0 of 3** | Ananke's Canvas, Mortok's Skull, The All-Seeing Eye, Charon's Toll, Hati, The Last Word, Sanguine Orbit |

Worked example, **Blood Whisper** (`drxitem\supra\wep_spear.dbr`, the 400-bleed spear):

| Piece | Where it comes from |
|---|---|
| Mythic Formula | **Chest-droppable** (Epic + Legendary tier chests) |
| Reagent 1, Peleus' Ashen Spear | **Chest-droppable** |
| Reagent 2, Queen Zenobia's Spear | **Chest-droppable** |
| Reagent 3, Ichthian melee spear | **Not from a chest.** It is a monster-only drop (`l_ichthianspear`), so you have to kill Ichthians for it. |

The 36 reagents you cannot get from a chest split as: 27 that live on other loot tables (mostly
monster-specific drops like the `mi_l_*` rare monster items, plus base-game level-banded unique
tables) and 9 with no loot table at all (six IT "divine artifact" reagents such as Ikon of Zeus and
Thoth's Glory, plus three Ragnarok-era one-hand-ranged records that this TQIT-era build never
wires up).

---

## 3. Legendary weapons: what the chests can and cannot pay

Read on a **Legendary-difficulty** chest. "Reach" means the chest can roll it; "in game" is how
many exist in the whole database.

| Weapon class | Reach | In game | Cannot drop, and why |
|---|---:|---:|---|
| **Spear** | **22** | 24 | 2. **Blood Whisper** (craft-only) and **Runbreaker** (the Endless Hunt's guaranteed reward). |
| **Bow** | **21** | 23 | 2. **Stormbringer** and **Ten Suns' Wrath**, both craft-only. |
| **Mace / club** | **21** | 24 | 3. **Omega**, **The Doomcaller's Maul**, **Sword Fish**, all craft-only. |
| **Sword / dagger** | **21** | 28 | 7. Five craft-only (**Shrike**, **Crystal Tear of Nyx**, **Aquimae**, **The Unholy Heartpiercer**, **Ripulsar**), **Vein-Render** (guaranteed Crimson Verdict set drop), and one dev-dead base record (`u_ice`). |
| **Staff** | **20** | 25 | 5, and all five are craft-only: **Scepter of Kronos**, **Staff of the Cosmos**, **Soul Seekkor**, **Helona's Ascension**, **The Munderizer**. |
| **Shield** | **27** | 33 | 6. **Agathodaemon** (craft-only) plus 5 base-game uniques that only sit on the base level-banded shield tables (Zeno's Third Paradox, Chigon's Resolve, Venom Husk Shield, Sun Disc, Shield of the Korybantes). |
| **Axe** | **19** | 41 | 22, but only 8 of those matter. Six are craft-only (**Darkflame Devourer**, **Charybdis Unchained**, **Erysichthon's Undying Hunger**, **Wrath of the Furies**, **Phoenix Ascendant**, **Scylla Unbound**), one is a quest item (**Sickle of Kronos**), one drops off a mod bleed-affix table (Cerberus' Bite). **The other 14 are dead records** that no loot table, container or monster in the entire 51,234-record database names: 13 sit at `records\equipmentweapon\axe\` (note the missing `item\` folder level) and the fourteenth is a dead duplicate of the Sickle. They are inherited DRX/SV debt, not something R-180 excluded. |
| **Thrown / one-hand ranged** | **0** | 5 | **Nothing in the mod can pay this class at all.** Four are craft-only (**Charon's Toll**, **Hati**, **The Last Word**, **Sanguine Orbit**) and one is a DRX wand on its own randomizer. There is no "unique one-hand-ranged" loot table in this TQIT-era database for the aggregate master to name. **This is a real gap, not a design choice.** See "Known gaps" below. |

**Two-handed weapons are covered.** In Titan Quest a two-hander is not a separate item class; a 2H
sword is still `WeaponMelee_Sword` on `weapon_sword.tpl`. The base `all_{tier}0{1,2,3}` masters that
the new aggregate names include the two-handed families, so 2H is reachable everywhere 1H is.

**The pattern:** apart from the thrown class and the 14 dead axes, essentially every legendary
weapon a chest cannot pay is either **craft-only by design** (the 42 supra items) or a **named
signature drop** that is meant to come from a specific fight (Runbreaker from the Endless Hunt,
Vein-Render from the Crimson Verdict set).

---

## 4. Legendary armour and other equipment

Same Legendary-difficulty chest.

| Slot | Reach | In game | What it cannot drop, and why |
|---|---:|---:|---|
| **Torso** | **33** | 71 | Two craft-only (Ananke's Canvas, Ares Endless Assault), the Crimson Verdict torso (**Sanguine Shroud**, set-guaranteed), 6 dev-dead records, and 29 base-game uniques that live only on the base level-banded `melee_*` / `caster_*` tables. Torso is the widest slot in the game, so it also has the widest tail. |
| **Head** | **30** | 39 | Three craft-only (Cystalline Mask [sic, spelled that way in game], Titan Crest, Galefury), the Crimson Verdict helm (**Cowl of the Red Verdict**), **Mask of the Waking Dread** and Leinth's veil (both hand-placed, no loot table), 1 dev-dead, 2 base-only. |
| **Arms** | **28** | 37 | Two craft-only, the Crimson Verdict armband (**Hemorrhage Bindings**), 2 dev-dead, 4 base-only. |
| **Legs** | **28** | 33 | Two craft-only, 2 dev-dead, 1 base-only. |
| **Shield** | **27** | 33 | See the weapon table above. |
| **Amulet** | **18** | 26 | Two craft-only (**Paragon of Violence**, Void Prism), **The Golden Bough** and **Lethe's Draught** (hand-placed uber rewards, deliberately not on any table), 4 base-only. |
| **Ring** | **16** | 24 | Two craft-only (Ananke's Ring, Band of the Elder Savage), 6 base-only. |
| **Relic** | **17 per chest** | 292 | Always tier-matched: Essence-tier on Normal, Embodiment-tier on Epic, Incarnation-tier on Legendary. This is the R-100 / 2026-08-08 relic law and the gate re-proves it (33 branches, 0 leaks). |
| **Charm** | **0** | 122 | **No mod chest drops a charm on any difficulty.** The donor table's rows simply never named the charm families. Not a regression from R-180, but worth knowing. |
| **Artifact** | **0** | 292 | **No mod chest drops an equippable artifact.** 80 of the 292 are craft-only supra/DRX results; the rest are on their own base-game tables. Merc scrolls and spell scrolls do drop (41 records reachable from a Normal-tier chest, 9 from an Epic-tier one). |
| **Formula** | **4** legendary-grade **+ 42 uber** | 7 legendary-grade | The three legendary-grade formulae you cannot get are the base IT arcane formulae (Book of Dreams, Scroll of Oneiros, Shroud of Eternal Night), which sit on the base `act1_arcaneformulae` tables. |

**Full class breakdown of one legendary chest (308 items):** torso 33, head 30, arms 28, legs 28,
shield 27, spear 22, bow 21, mace 21, sword 21, staff 20, axe 19, amulet 18, ring 16, formula 4.

---

## 5. How it generalises across the game

R-180 was applied once, from one place, over **every chest table the mod owns plus the three DRX
donor tables that all of them were cloned from**. That is 51 mod tables + 3 donors = **54 tables**.
Nothing has to be remembered for a new chest: any future mod-owned chest table is in scope by
default and the build gate fails loud if it ships collapsed.

### Chests that inherit the fixed shared weapon row

| Chest / hoard | Records | Live? | Themes | Classes it can pay |
|---|---|---|---|---|
| **Polis Daemonai Warden's Vault-Cage** (Alkyoneus the Soul-Gaoler, `hadespalace_floor04_01`; the testhub cage) | 2 proxies (`svc_polisvault_chest_01`, `_03`), 6 physical chests, 18 themed containers, 21 loot tables | **Live** | martial / hunter / warden on chest 01; apex / adept / sovereign on chest 03 | all 6 weapon classes, all armour slots, jewellery, tier-correct relics, all 42 uber formulas |
| **General A / B / C guard hoards** (the three guard-pair hoards) | 9 containers -> 9 loot tables | **Live** | none (one table per difficulty) | same 6 weapon classes; tier-correct relics and uniques on Epic and Legendary since 2026-08-08 |
| **Red-uber "Mystical Orb" chests** (`genericboss05_chest_{normal,epic,legendary}`) and the **Leinth boss chest** | 6 containers -> 3 shared apex tables | **Live** | none | same 6 classes; slightly richer, 116 legendary-grade items on Epic and 24 relics |
| **Hidden blood-cave mega chest** (`hidden_bloodcave_chest_{01,02,03}`, the esti chest) | 3 containers -> the 3 DRX donor tables | **Live** | none | same 6 classes. Widening the donor itself means no future clone can re-inherit the old collapsed row |
| **Charon / Tantalus / Mnemophage / Ephialtes / Diadochi / Obsidian hoards** | 18 containers -> 18 loot tables | **Latent** | none | Their bespoke tables carry the full breadth and are tier-correct, **but the placed containers currently name the base game's `boss_default_NN-NN` tables instead**, so in-game they pay base level-banded boss loot. Fixing that is a wiring change, not a loot change. Recorded here so it is not mistaken for a drop bug. |

### Chests that do NOT inherit it

Everything else in the game, which is the large majority:

- **308 of the 360** `FixedItemLoot` tables in the database are base-game or DRX-owned and were
  not touched (the 3 blood-cave donors are the only exception, and they were widened on purpose).
- **1,719 of the 1,770** `FixedItemContainer` records are base-game and were not touched.

Those chests keep stock Titan Quest behaviour. They are **level-banded**, not difficulty-themed:
what a base chest pays is decided by the area or monster level band written into its own table name
(`boss_default_47-49`, `chest_*`, and so on), and their weapon rows name the base game's own
per-class tables. They were never subject to the "no legendary spears" defect in the first place,
because that defect came from the DRX donor, not from the base game. Changing them is out of scope
and would rebalance the whole campaign.

### Known gaps (honest list)

1. **Thrown / one-hand-ranged weapons cannot drop from any mod chest.** Five legendary records
   exist and none are reachable. Four are craft-only anyway, so the practical loss is one DRX wand,
   but the class is genuinely unpayable. Closing it needs a unique one-hand-ranged loot table to
   exist for the aggregate master to name.
2. **Charms never drop from mod chests** (0 of 122), on any difficulty.
3. **Equippable artifacts never drop from mod chests** (0 of 292).
4. **The six boss hoards listed as "latent" above are wired to `boss_default_*`,** so the breadth
   work does not currently reach them in game.
5. **`svc_obsidianhoard_loot_02` and `_03` reach the Normal-tier relic family as well as their own.**
   That is a downward leak only (a lower relic on a higher difficulty), which the tier law permits
   and the base game does routinely, and the table is latent anyway.
6. **`polisvault_02`, `_04` and `_05`** are spare chest tables with no placement; the cage places
   only chest 01 and chest 03.

---

## Appendix: how to re-derive every number here

```
py tools/gate_chest_loot_breadth.py work/SoulvizierClassic/Database/SoulvizierClassic.arz --verbose
py tools/debug/derive_gaoler_drops.py work/SoulvizierClassic/Database/SoulvizierClassic.arz
py tools/debug/negtest_chest_breadth.py work/SoulvizierClassic/Database/SoulvizierClassic.arz
py tools/gate_relic_difficulty_tiers.py work/SoulvizierClassic/Database/SoulvizierClassic.arz
```

The pool walk itself is `tools/svc_loot_breadth.py` (`Expander.leaves` chases a chest table down to
its leaf items; `Expander.pool` buckets them by item class). The reach-versus-universe figures in
sections 3 and 4 are that leaf set intersected with every record in the arz carrying
`itemClassification = Legendary`, and the "why" column is a reverse-reference index over every
`.dbr`-valued field in all 51,234 records: an item is craft-only when a formula names it as its
`artifactName`, monster-or-base when only other loot tables name it, and dead when nothing does.

Cross-check against the R-180 build record: **all figures agree** (181 / 111-116 / 308 pools,
legendary spears 0 -> 22, 51 tables audited, all 6 weapon classes). The only apparent difference is
that this document also quotes a 120-item figure for the union across *all* Epic-tier tables, which
is simply the per-table 111 plus the 5 extra the red-uber apex table adds; it is not a
contradiction of the 111-116 per-table range.
