# SoulvizierClassic - Soul Audit Report

## High-Level Summary

| Category | Count |
|----------|-------|
| Existing SV soul types | 732 |
| New uber soul types (created by us) | 140 |
| Total monsters with soul references | 1,237 |
| Active droppers (equip chance > 0) | 848 |
| Inactive (soul ref but no equip chance) | 389 |

### Drop Rate Distribution

| Drop Rate | # Monsters | Description |
|-----------|-----------|-------------|
| 66% | 753 | Heroes, Quest monsters, uber encounters |
| 25% | 67 | Farmable act bosses (fixed-location) |
| 0.5% | 26 | Pre-existing SV champion data (legacy) |
| 0.35% | 2 | Pre-existing SV data (legacy) |

### Active Droppers by Classification

| Classification | Active Droppers | Inactive (no drops) | Notes |
|---------------|----------------|--------------------|-|
| Hero | 589 | 1 | Correct - these should drop |
| Boss | 117 | 1 | Correct - these should drop |
| Quest | 109 | 0 | Correct - these should drop |
| Champion | 21 | 149 | **Issue**: 21 Champions are dropping (see Issue #2) |
| Common | 10 | 153 | **Issue**: 10 Commons are dropping (see Issue #3) |
| (none) | 2 | 85 | **Issue**: 2 unclassified are dropping (see Issue #3) |

---

## TO-DO: Soul Work Needed

### Priority 1: Hand-Craft New Souls

These bosses have NO soul items at all — souls must be designed from scratch in `SOUL_OVERHAULS`.

| Monster | Class | Levels | HP | Location | Design Notes |
|---------|-------|--------|-----|----------|-------------|
| **Toxeus the Murderer (SP)** | Hero | 33/66/99 | 9,324–13,986 | Secret Passage (`xpack/.../skeleton/um_toxeus_99`) | STR 419, DEX 599, INT 379. Skills: distort reality, lucid dream, lethal strike. **MUST be the STRONGEST soul of any monster.** See Toxeus Comparison below. |
| **Leinth** | Boss | 47-50 / 62-65 / 74-76 | 32,481 | Secret Passage (`drxcreatures/bloodwitch/q_leinth_47/49/50`) | INT-focused caster (INT 451). Skills: blood boil, flesh eater, heatseeker projectile, summon uglies. 3 difficulty variants. Olympian blood witch. |
| **Murder Bunny** | Boss | 66/79/99 | 275,000 | Secret Passage (`drxcreatures/crowheroes/murderbunny`) | STR 220, DEX 510, INT 400. Ambush boss. 100% immune to freeze/petrify/sleep/stun/trap. Currently drops `zzz_munderizer.dbr` egg — need to add a soul ring alongside it. |
| **Secret Passage Hades** | Boss | 57/71/80 | ??? | Secret Passage (`drxcreatures/bloodwitch/boss_hades_54`) | Different from main Hades. Tag: xtagMonsterHades. Needs investigation — may share soul with main Hades Form 3 or need its own. |

### Priority 2: Wire Existing Souls to Missing Variants

These bosses have soul items created but some difficulty/location variants are missing the wiring.

| Monster | Missing Variant | Existing Soul Source | Action |
|---------|----------------|---------------------|--------|
| **Charon (Form 1)** | `boss_charon_41.dbr`, `boss_charon_43.dbr` | `svc_uber/boss_charon_soul_*.dbr` (66% on `_39`) | Wire same uber soul to _41 and _43 at 66% |
| **Hydra** | `boss_hydra_60.dbr`, `boss_hydra_63.dbr` | `hydra_soul_*.dbr` (25% on `_66`) | Wire same soul to _60 and _63 at 25% |
| **Ormenos (xpack)** | `xpack/.../boss_chinatelkine_ormenos_41.dbr` | `ormenos_soul_*.dbr` (3% on regular variants) | Wire same soul to xpack variant at 3% |
| **Yaoguai (xpack)** | `xpack/.../boss_daemonbull_yaoguai_38.dbr` | `yaoguai_soul_*.dbr` (25% on regular variants) | Wire same soul to xpack variant at 25% |

### Priority 3: Secret Passage Monster Souls

The Secret Passage (`drxcreatures/`) contains many unique monsters that need souls. Below is the full inventory by classification.

**Boss-class (need hand-crafted souls):**
- Leinth (3 variants) — see Priority 1
- Murder Bunny — see Priority 1
- Secret Passage Hades — see Priority 1

**Quest-class (34 records — need uber-style auto-generated souls):**
These are the "crow heroes" and other unique secret passage encounters. Notable monsters:
- Gorgus, Jabarto, Kaets, Kreeloo, Zilla — crow hero quest monsters
- Spirit Callers — bloodabomination spirit casters
- D2-themed NPCs — various quest encounters
- Need full inventory extraction to identify all unique monster types vs difficulty variants

**Champion-class (37 records — decide if they should get souls):**
- Bastien variants (crow heroes)
- Blood abominations (bladedancer, spearrunner, ravager)
- Blood harpies, blood hounds, blood dragons
- The Slasher
- Decision needed: Do Champions in the secret passage deserve souls given their special nature?

**Hero-class monsters in secret passage:**
- Warden of Souls (`xsecrethero_wardenofsouls`) — Lv 48, Life element, Tank role. **Already has a soul** (tagSoulSVC9141).

### Priority 4: Toxeus Soul Design

#### Toxeus Variant Comparison

| Stat | um_toxeus_21 (Main) | um_toxeus_99 (Secret Passage) |
|------|--------------------|-----------------------------|
| Classification | **Boss** | **Hero** |
| Levels | 25 / 45 / 65 | 33 / 66 / 99 |
| HP | 3,966 – 6,345 | 9,324 – 13,986 |
| STR | 319 | 419 |
| DEX | 439 | 599 |
| INT | 179 | 379 |
| Key Skills | laytrap_multitrap, battlerage, flashpowder, lethalstrike | toxeus_distortreality, luciddream, luciddream_temporalflux, lethalstrike |
| Current Soul | YES — 66% drop, Flash Powder skill | NO — drops common ring loot |
| Soul Path | `skeleton/toxeus_soul_*.dbr` | None |

**Design Decision Needed:**
- The Secret Passage Toxeus (um_toxeus_99) is significantly stronger and higher level
- The main game Toxeus already has a soul with Flash Powder
- Options:
  - A) Create a separate, **much stronger** soul for SP Toxeus (must be strongest in the game per directive)
  - B) Upgrade the existing Toxeus soul to be the strongest and have both variants drop it
  - C) Keep the existing soul on main Toxeus, create a new "Soul of Toxeus the Murderer" for SP variant that is the strongest soul
- **Recommendation: Option C** — two distinct souls, with the SP version being the ultimate soul

### Priority 5: Investigate & Decide

| Monster | Status | Question |
|---------|--------|----------|
| **Cold Worm** | Test record (`records\test\boss_coldworm50.dbr`) | Does NOT spawn in-game. No spawn proxies found. Insectoid boss, Lv 30/50/65. Has full skill set (shockwave, drop ceiling, lay eggs, summon bugs, poison gas). Should we add it to the game + create a soul? |
| **Dagon** | Test record (`records\test\boss_dagon_66.dbr`) | Does NOT spawn in-game. No spawn proxies found. Olympian boss, Lv 50/65/80. Has skills (shadow star, summon water, tidal wave, mud storm). Should we add it to the game + create a soul? |
| **Graeae** | Already implemented | The Graeae are the three sisters: Deino (Lv 38), Enyo (Lv 38), Pemphredo (Lv 39). All lightning/tank bosses. **Already have uber souls** (tagSoulSVC9039/9040/9041). No action needed. |
| **Hades Forms 1 & 2** | Confirmed: do NOT wire | Form 1 and 2 die during the fight → Form 3 spawns. Only Form 3 should drop a soul. Current wiring is correct. |
| **xq03_charonsoundrat** | Quest trigger entity | Lv 6/36/56. NOT a real boss — it's a sound/quest scripting trigger. Ignore. |
| **Charon Form 2** | Already wired | All 3 Form 2 variants (39/41/43) have SV souls at 25%. No action needed. |
| **SP Hades variant** | Needs investigation | `drxcreatures/bloodwitch/boss_hades_54.dbr` — is this a distinct fight from main Hades? Levels 57/71/80. Should it share the Form 3 soul or get its own? |

---

## Completed Work

### Soul Overhauls (in apply_svc_patches.py)

| Soul | Summon | Key Buffs | Status |
|------|--------|-----------|--------|
| **Rakanizeus** | Summons Rakanizeus pet | +45% run speed, +35% atk speed, +25% total speed, +15 pierce def, +200 HP, +100 MP, +40 STR/DEX, +50 OA, Storm Surge Lv5, Chain Lightning Lv4 | Done |
| **Boneash** | Summons Boneash pet | +35% cast speed, +150 MP, +50 INT, -4% life penalty, Volcanic Orb Lv5, Fire Enchantment Lv3 | Done |
| **Calybe** | Eclipse proc | Dual wield, +atk speed, +dodge, physical/bleed/pierce damage | Done |
| **Pharaoh's Honor Guard** | Summons Stone Construct | -9% movement penalty (movement only, not total speed) | Done |
| **Xerkos** | None | Dual weapon, lethal strike, +atk speed, stun, physical damage | Done |

### Drop Rate Changes

| Monster | Old Rate | New Rate |
|---------|----------|----------|
| Pharaoh's Honor Guard (12 variants) | 2.25% | 10% |

---

## Issues Found (from original audit)

### Issue #1: Carrion Crow Soul Still Dropping

The Carrion Crow soul has **2 Hero-class** Carrion Crow variants and **14 (none)-class** variants.

- The 14 (none)-class crows have been correctly disabled (no equip chance).
- The 2 Hero-class Carrion Crows **will still drop** the soul because they are Hero classification.
- If the user is encountering soul drops from **non-starred** (normal) crows, this may be a cached save issue. Starting a new character should resolve it.

### Issue #2: `create_uber_souls.py` Ignores Monster Classification

The uber soul creation script sets `chanceToEquipFinger2=66%` on ALL monsters it matches, regardless of classification. This causes Common/Champion/unclassified monsters to drop uber souls they shouldn't:

| Monster | Classification | Soul | Level | Should Drop? |
|---------|---------------|------|-------|-------------|
| `qs_minotaurconqueror` | Common | Soul of Qs Minotaurconqueror | 18 | Debatable - "qs" prefix = quest monster |
| `as_ghosthero` | Champion | Soul of Ghosthero | 32 | Debatable - name contains "hero" |
| `bm_eldercyclops` | Champion | Soul of Eldercyclops | 33 | Debatable - "elder" = special variant |
| `bm_elderminotaur` | (none) | Soul of Elderminotaur | 33 | Debatable - "elder" = special variant |
| `bm_elderminotaurlord` | (none) | Soul of Elderminotaurlord | 33 | Debatable - "elder" = special variant |

**Recommendation**: These are genuinely special encounters despite not being classified as Hero/Boss. Two options:
- A) Leave them dropping at 66% since they are clearly unique monsters
- B) Add a classification check in `create_uber_souls.py` to skip Common/Champion/none

### Issue #3: 26 Legacy Champion Droppers at 0.5%

These 26 monsters have `chanceToEquipFinger2=0.5%` from the **original SV database** (not set by us). They're prefixed `champion_` and are Common/Champion class:

Examples: `champion_archer_06`, `champion_berserker_08`, `champion_guardian_11`, `champion_hunter_mounted_09`, `champion_magi_08`

These are not our bug -- they were in the original SV data with very low equip chances for gear. The soul drop is a side effect of equipping the soul and then dying.

**Recommendation**: Could zero out their `chanceToEquipFinger2` if desired, but at 0.5% drop rate it's basically negligible.

### Issue #4: 1 Element Mismatch

| Soul | Soul Element | Actual Primary | Monster Damage |
|------|-------------|---------------|----------------|
| Soul of Spiderblackwidow | **poison** | **life** | life=60, poison=50 |

The Black Widow spider deals slightly more life (vitality) damage than poison. However, **poison is thematically correct** for a spider. The damage split is close (60 vs 50).

**Recommendation**: Keep as poison -- thematically appropriate.

### Issue #5: 68 Dormant Soul Types

68 soul types from original SV only exist on Common/Champion/none monsters and will never drop in AE. These include:

- Cave Bat Soul (18 Common monsters)
- Ravenous Boar Soul (8 Common + 2 Champion)
- Carrion Crow Soul (14 none-class)
- Maenad Stalker Soul (6 Common)
- Satyr Skirmisher Soul (6 Common)
- Noxious Zombie Soul (4 Common)
- Orthus Soul (8 none-class)
- Various Harpy, Satyr, Ichthian variants

These worked in TQIT via `lootFinger2Chance` but are dormant in AE since we don't set `chanceToEquipFinger2` for Common/Champion/none monsters.

**Recommendation**: Leave dormant -- these are trash mob souls that shouldn't drop from regular encounters.

### Issue #6: 201 Orphaned Soul Items

201 soul item records exist in the database with no monster referencing them via `lootFinger2Item1`. These are likely:
- Difficulty variants (normal/epic/legendary) where only one variant gets referenced
- Removed or renamed monsters that no longer exist
- Developer test souls

**Recommendation**: No action needed. These don't affect gameplay since no monster drops them.

---

## New Uber Souls - Full Catalog (140)

### By Element

| Element | Count | Examples |
|---------|-------|---------|
| Physical | 38 | Cyclops Polyphemus, Minotaurlord, Scarabaeus, Elderminotaur, Trachius |
| Lightning | 27 | Xiao, Barroc, Drottuk, Deino, Enyo, Pemphredo, Queenchkra |
| Fire | 24 | Chimaera, Medusa, Aktaios, Talos, Hydra, Satyrshaman, Charon |
| Life | 22 | Necromancer Alastor, Sehr'tunkah, Ghosthero, Melinoe Bloodwitch |
| Poison | 17 | Gorgon Sstheno, Arachne, Scorposking, Spiderblackwidow |
| Cold | 12 | Gorgon Euryale, Gargantuan Yeti, Barmanu, Dragonliche |

### By Role

| Role | Count | Examples |
|------|-------|---------|
| Melee | 53 | Polyphemus, Minotaurlord, Chimaera, Talos, Hydra |
| Caster | 47 | Medusa, Aktaios, Dragonliche, Deino, Charon, Typhon |
| Tank | 30 | Grom, Cenonstormborn, Sehr'tunkah, Stonhide |
| Summoner | 4 | Ssark, Thetombkeeper, Nightsmistress, Spartacentaur |

### By Level Range

| Level Range | Count |
|------------|-------|
| 1-15 | 1 |
| 16-25 | 11 |
| 26-35 | 23 |
| 36-40 | 27 |
| 41-45 | 52 |
| 46-50 | 22 |
| 51-65 | 4 |

### Stat Scaling Examples

Souls scale with monster level. Here are examples at different tiers:

**Low-level (lvl 9) - Soul of Spartacentaur** (physical/melee)
- +5 Str, +30 HP, +1.0 HP/s, +3% atk spd
- 5-12 physical damage, +5% physical modifier

**Mid-level (lvl 33) - Soul of Xiao** (lightning/melee)
- +16 Str, +99 HP, +3.3 HP/s, +9% atk spd
- 10-26 physical, 10-40 lightning, +16% lightning modifier
- +16% lightning resistance

**High-level (lvl 45) - Soul of Titan Typhon** (fire/caster)
- +22 Int, +135 MP, +13% cast spd, +22% mana regen
- 18-45 fire, +22% fire modifier
- +22% fire res, -13% cold res

**Max-level (lvl 60) - Soul of Hydra** (fire/melee)
- +30 Str, +180 HP, +6.0 HP/s, +15% atk spd
- 18-48 physical, 24-60 fire, +30% fire modifier
- +30% fire res, -15% cold res

---

## Existing SV Souls - Key Stats

| Metric | Count |
|--------|-------|
| Active soul types (at least 1 monster drops) | 463 |
| Dormant soul types (Common/Champion only) | 68 |
| Orphaned soul types (no monster references) | 201 |

### Most-Dropped Existing Soul Types

| Soul | Active Monsters | Total Monsters |
|------|----------------|---------------|
| Satyr Firemagi | 10 | 17 |
| Sandwraith | 5 | 28 |
| Dark Satyr Elite Warrior | 2 | 13 |
| Maenad Vanguard | 2 | 23 |
| Maenad Huntress | 2 | 21 |
| Brush Harpy Crone | 3 | 6 |
| Carrion Crow | 2 | 16 |

---

## Standing Directives

1. **Toxeus the Murderer must have the STRONGEST soul of any monster** — the Secret Passage variant soul must outclass every other soul in the game.
2. **Hades Forms 1 & 2 do NOT get souls** — only Form 3 (the final form) drops a soul.
3. **All secret passage monsters should have souls** — unique area deserves unique rewards.
