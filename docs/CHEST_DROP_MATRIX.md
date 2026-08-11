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

The 36 reagents you cannot get from a chest split as: 20 monster-specific green (Monster Infrequent)
items, 6 that are base-game "divine artifacts" you have to craft in their own right, 8 ordinary
uniques that only sit on base-game level-banded tables, and 2 DRX randomizer amulets. Section 6
breaks all of this down item by item.

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
| **Thrown / one-hand ranged** | **0** | 5 in the mod arz | **Nothing in the mod can pay this class at all.** Of the 5 in the mod's own arz, four are craft-only (**Charon's Toll**, **Hati**, **The Last Word**, **Sanguine Orbit**) and one is a DRX wand on its own randomizer. The base game adds many more (Ragnarok/Atlantis one-hand-ranged), but there is **no "unique one-hand-ranged" loot table anywhere in the mod or the base database** for the aggregate master to name; the only 12 base tables for the class are monster drops (monkeyman, potamoi warrior). **This is a real gap, not a design choice.** See "Known gaps" below. |

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

1. **Thrown / one-hand-ranged weapons cannot drop from any mod chest.** Five legendary records exist
   in the mod arz and none are reachable; four are craft-only anyway, so the practical loss is one
   DRX wand plus the whole Ragnarok/Atlantis one-hand-ranged range that the base game adds. Closing
   it means **authoring** a unique one-hand-ranged loot table, because no such table exists in the
   mod or the base database today (checked: 12 base tables carry `1hranged`, all of them
   monster-specific).
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

## 6. DROP SOURCES: if not a chest, then who?

> Follow-up asks (Will, 2026-08-10). Same source of truth as the rest of this document, plus the
> base-game `database.arz` (74,013 records) where the mod overlays rather than replaces it.

### 6.1 Runbreaker: the Endless Hunt

| | |
|---|---|
| **Who drops it** | **The Endless Hunt** (`um_toxeus_hunt_99` roaming, `um_toxeus_hunt_l_99` the fixed encounter). Boss classification, character level 40 / 68 / 100. |
| **Is it guaranteed?** | **YES, 100%, every kill, either variant.** The right-hand slot fires at `chanceToEquipRightHand = 100`, its only member is `runbreaker_guaranteed_{n,e,l}` at weight 100, and that table holds exactly one item at weight 100. Nothing competes with it. |
| **Which difficulties** | **All three.** There is a Runbreaker per difficulty (`runbreaker_guaranteed_n` / `_e` / `_l`), so a Normal-difficulty kill pays the Normal Runbreaker and so on. `svc_l_runbreaker` (the one section 3 lists as unreachable from chests) is the Legendary one. |
| **Where he spawns** | Two mechanisms. **(A) Roaming:** he is a member of 346 base proxy pools referenced by 540 proxies across every Immortal Throne area, Rhodes (70 proxies), Medea's Grove (76), Epirus (55), Styx (78), Plains of Judgement (79), Tower of Judgement (49), Elysian Fields (82) and Hades Palace (49). He was never Hades-confined and was never difficulty-gated; the old "Hades-only" belief traced to a mislabelled code comment. **(B) The fixed encounter**, which is the one that carries the never-give-up "endless pursuit" behaviour Will asked to be Legendary-flavoured (R-90). |
| **How often** | R-96 set the roam rate to **roughly one sighting per act**. Before that he was about 1 in 67,000 per spawn roll, which is why he seemed not to exist on Normal. |
| **Also on his corpse** | His own soul (`toxeus_hunt_soul_*`, 100%) and the guaranteed Rite drop (`svc_rite_guaranteed`, 100%). |
| **Detail** | `docs/reports/b98_endless_hunt.md`, sections 6 and 12. |

### 6.2 Vein-Render and the Crimson Verdict

**Who drops it: Blood Toxeus** (`um_bloodtoxeus_99`, the Devourer / Hemorrheus superboss), the
deliberate ambush "with his guys next to the tattered parchment" in the blood-cave secret-door
transition hallway. Boss classification, level 40 / 68 / 100, present on all three difficulties with
a per-difficulty set (`crimsonverdict_guaranteed_n` / `_e` / `_l`).

**The set has four pieces**, and they are the four members of that one table, at equal weight:

| Piece | Slot | Record |
|---|---|---|
| **Vein-Render** | sword | `svc_l_veinrender` |
| **Cowl of the Red Verdict** | head | `svc_l_crimsonverdict` (helm) |
| **Sanguine Shroud** | torso | `svc_l_crimsonverdict` (armor) |
| **Hemorrhage Bindings** | arms | `svc_l_crimsonverdict` (armband) |

**Completion mechanics: one random piece per kill, so you farm him four-plus times.** His right-hand
slot fires 100% of the time and picks between the Crimson Verdict table (weight 100) and a plain
legendary sword table (weight 19). So **about 84% of kills pay a set piece**, and the piece is a
uniform 1-in-4, giving **roughly 21% per specific piece per kill**. Nothing tracks which pieces you
already hold, so duplicates happen.

The set bonuses scale with pieces worn (2 / 3 / 4), from the `svc_crimsonverdict` ItemSet record:

| Pieces | Bonus |
|---|---|
| 2 | +8% attack speed, +150 life, +6% life, +15% life leech, +15% offensive life, +25% bleed damage |
| 3 | +12% attack speed, +300 life, +10% life, +25% leech, +25% offensive life, +45% bleed, +20% bleed duration |
| 4 | +18% attack speed, +600 life, +15% life, +40% leech, +40% offensive life, +75% bleed, +40% bleed duration, plus 120 bleed retaliation over 3s |

### 6.3 The three hand-placed uber rewards

All three are **direct item references in the boss's Misc4 slot, at 100%, with no competing member**,
so each is a **guaranteed drop on every kill, on every difficulty**. They are deliberately absent
from every loot table, which is exactly why sections 3 and 4 list them as chest-unreachable.

| Item | Boss | Where | Guaranteed? | Per-difficulty? |
|---|---|---|---|---|
| **The Golden Bough** (amulet) | **Charon the Ferryman, second form** (`um_charonform2_ferryman_99`), levels 48 / 72 / 100 | the ferryman boss fight; he also drops his own named "essence" boss chest | **100%, every kill** | Yes, `svc_goldenbough_{n,e,l}` |
| **Lethe's Draught** (amulet) | **The Mnemophage** (`um_mnemophage_99`), levels 46 / 68 / 100 | Lower City of Lost Souls; his own "Mnemophage's Lethe-Hoard" chest sits nearby | **100%, every kill** | **No.** One single record serves all three difficulties |
| **Mask of the Waking Dread** (helm) | **Ephialtes** (`um_ephialtes_99`), levels 58 / 78 / 97 | Dread Halls terminal vault, the back corner | **100%, every kill** | Yes, `svc_maskofdread_{n,e,l}` |

Each of the three also drops his own soul at 33% and the usual relic / arcane-formula rows.

### 6.4 Reagent enumeration for a fix wave

Of the **78 distinct uber-craft reagents**, **42 are already droppable from a legendary-tier mod
chest**. The 36 that are not split cleanly into "leave it alone" and "fix it":

| Bucket | Count | Verdict |
|---|---:|---|
| **MI / green (Monster Infrequent)** | **20** | **Leave alone.** Monster-specific by design; that is the whole point of the class. None is chest-reachable and none should be. |
| **Base-game "divine artifacts"** | **6** | **Leave alone.** They sit on **zero** loot tables in the mod *or* the base game: they are themselves crafted at the Enchanter. Two uber recipes are deliberately craft-a-craft chains. |
| **Ordinary uniques on base tables** | **8** | **Fix-wave candidates.** Ordinary legendary uniques that any level-banded base table can pay but no mod chest can. |
| **DRX randomizer amulets** | **2** | **Fix-wave candidates (low value).** `sandbox\chris\*` records reachable only through the DRX `u_l_nephriteammy` / `u_l_saphireammy` randomizers. |

**The 20 MI/green reagents** (all `mi_*`, all classification Rare, **0 chest-reachable**). Will's two
examples are both here: **Ismene's Helm** is `xpack\item\equipmentarmor\helm\mi_l_lamiamelee.dbr`, and
the supra spear's green component is the **Ichthian Harpoon**, `mi_l_ichthianmelee.dbr`.

> Animus, Bandari's Helm, Bai Hu's Mantle, Bracers of the Minotaur, Brigand's Bow, Deathweaver's
> Legtip, Ethereal Leggings, Exotic Carapace, Head Hunter's Axe, **Ichthian Harpoon**, **Ismene's
> Helm**, Prowler's Legguards, Sabertooth, Scepter of the Liche King, Shaman's Coil, Staff of the
> Magi, The Night Mistress's Clutch, Warlord's Coat, Atouk, plus **Machae**
> (`xpack2\...\1hranged\mi_l_machae.dbr`, which lives in the base game database rather than the mod's).

**The 10 ordinary reagents that are NOT chest-droppable** (the actual fix-wave list):

| Reagent | Slot | Today it drops from |
|---|---|---|
| Blessing of the Gods | amulet | base `amulet_e01` / `amulet_l01` |
| Thoth's Mark | ring | base `finger_e02` / `finger_l02` |
| Black Pearl Ring | ring | base `u_l_blackpearlring` randomizer |
| Wyrmskin Harness | torso | base `melee_l03` |
| Raiment of Logos | torso | base `caster_e02` / `caster_e03` |
| Mantle of Amun-Ra | torso | base `caster_l02` |
| Nephrite Talisman | amulet | DRX `u_l_nephriteammy` randomizer |
| Saphire Amulet | amulet | DRX `u_l_saphireammy` randomizer |
| `xpack2 ... u_e_06` (one-hand ranged) | thrown | base `roh_08` / `roh_09` |
| `xpack2 ... u_l_08` (one-hand ranged) | thrown | base `roh_14` / `roh_15` |

### 6.5 The seven craftables with no chest-droppable reagent, classified

| Craftable | Its three reagents | Verdict |
|---|---|---|
| **Ananke's Canvas** (caster torso) | Bai Hu's Mantle **(MI)**, Raiment of Logos **(ordinary)**, Mantle of Amun-Ra **(ordinary)** | **2 must become chest-droppable.** The MI one stays monster-farmed. |
| **Mortok's Skull** (artifact) | Crescent Moon of Artemis, Ikon of Zeus, Thoth's Glory, all **divine artifacts** | **No fix needed.** All three are themselves craftables; this recipe is a craft-a-craft by base-game design. |
| **The All-Seeing Eye** (artifact) | Demeter's Bounty, Golden Eye of Sun Wukong, Marduk's Tablet of Destiny, all **divine artifacts** | **No fix needed**, same reason. |
| **Charon's Toll** (thrown) | Machae **(MI)**, `u_e_06` **(ordinary)**, `u_l_08` **(ordinary)** | **2 must become chest-droppable**, and they are the same pair for all four thrown recipes. |
| **Hati** (thrown) | identical trio | as above |
| **The Last Word** (thrown) | identical trio | as above |
| **Sanguine Orbit** (thrown) | identical trio | as above |

**Correction to an earlier reading.** The three `xpack2\item\equipmentweapons\1hranged\*` reagents are
**not missing**. They are absent from the *mod's* arz but present in the base game database and named
by base loot tables (`li_roh_machae`, `ranged_roh`, `roh_08/09/14/15`), and the game resolves against
the merged database. So all four thrown uber weapons **are** craftable today; their reagents just
have to be farmed from base Ragnarok content rather than from a chest.

**Practical shape of a fix wave.** Eight of the ten fixable reagents are ordinary torso / amulet /
ring uniques, so making them chest-droppable is a matter of the relevant themed rows naming the base
unique families they already almost reach. The two thrown reagents are blocked behind the same gap as
"Known gaps" item 1: there is no unique one-hand-ranged loot table anywhere to name, so that half of
the wave has to author one.

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
