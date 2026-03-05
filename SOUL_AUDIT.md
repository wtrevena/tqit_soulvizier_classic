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
| **Toxeus the Murderer (SP)** | Hero | 33/66/99 | 9,324–13,986 | Secret Passage (`xpack/.../skeleton/um_toxeus_99`) | STR 419, DEX 599, INT 379. Skills: distort reality, lucid dream, lethal strike. **THE STRONGEST soul in the game.** Distinct from main Toxeus soul. See Toxeus Design below. |
| **Toxeus the Murderer (Main)** | Boss | 25/45/65 | 3,966–6,345 | Main game (`creature/monster/skeleton/um_toxeus_21`) | STR 319, DEX 439, INT 179. Skills: laytrap, battlerage, flashpowder, lethalstrike. Has existing soul (Flash Powder) — **overhaul to be one of the strongest souls in the game**, but weaker than SP variant. |
| **Leinth** | Boss | 47-50 / 62-65 / 74-76 | 32,481 | Secret Passage (`drxcreatures/bloodwitch/q_leinth_47/49/50`) | INT-focused caster (INT 451). Skills: blood boil, flesh eater, heatseeker projectile, summon uglies. 3 difficulty variants. Olympian blood witch. |
| **Murder Bunny** | Boss | 66/79/99 | 275,000 | Secret Passage (`drxcreatures/crowheroes/murderbunny`) | STR 220, DEX 510, INT 400. Ambush boss. 100% immune to freeze/petrify/sleep/stun/trap. Currently drops `zzz_munderizer.dbr` egg — need to add a soul ring alongside it. |
| **Secret Passage Hades** | Boss | 57/71/80 | ??? | Secret Passage (`drxcreatures/bloodwitch/boss_hades_54`) | Different from main Hades. Tag: xtagMonsterHades. Gets its own soul — **stronger than main Hades Form 3 soul** (SP is endgame content, higher level) but weaker than Toxeus. |
| **Cold Worm** | Boss | 30/50/65 | ??? | NOT YET IN GAME — test record (`records\test\boss_coldworm50.dbr`) | Insectoid. Uses CryptWorm mesh. Skills: shockwave, drop ceiling, lay eggs, summon bugs, poison gas. Drops HF Parts Recipe. **Add to Act 2 Egypt** (underground caves/tombs where cryptworm enemies already exist). Create soul after placement. |
| **Dagon** | Boss | 50/65/80 | ??? | NOT YET IN GAME — test record (`records\test\boss_dagon_66.dbr`) | Olympian, Ichthian mesh. Skills: tidal wave, summon water, mud storm, shadow star. Lovecraftian sea god. Drops Dagon relic. **Add wherever Ichthians spawn** — Greece Act 1 coastal areas and Orient Act 3 (Hanging Gardens through Jade Palace). Ichthians appear in both acts. Create soul after placement. |

### ~~Priority 2: Wire Existing Souls to Missing Variants~~ DONE

Implemented in `_wire_missing_boss_souls()` in `apply_svc_patches.py`.

| Monster | Variant | Soul | Drop Rate | Status |
|---------|---------|------|-----------|--------|
| Charon Form 1 | _41, _43 | boss_charon_soul | 66% | WIRED |
| Hydra | _60, _63 | hydra_soul | 25% | WIRED |
| Ormenos xpack | xpack _41 | ormenos_soul | 25% | WIRED |
| Yaoguai xpack | xpack _38 | yaoguai_soul | 25% | WIRED |

### ~~Priority 3: Fix Low Drop Rate Bosses~~ DONE

Implemented in `_fix_low_boss_soul_drop_rates()` in `apply_svc_patches.py`.

| Boss | Old Rate | New Rate | Records |
|------|----------|----------|---------|
| Typhon | 1.5% | 25% | 3 |
| Hades Form 3 | 1.5% | 25% | 3 |
| Megalesios | 2.0% | 25% | 3 |
| Ormenos | 3.0% | 25% | 3 + xpack |
| Cerberus | 3.5% | 25% | 3 |

Additional low-rate records (legacy, not critical):
- 39 Champion/Common records at 0.5% (legacy SV data — `champion_*` and `mythical_*` prefixed)
- 13 records at 0.3% (pet/summon minions — intentionally low)
- 42 Hero-classified maenad records at 2.0% (in `soul\test\` paths — test data)
- 2 test records at 5.0% (`records\test\um_calybe_20.dbr`, `records\test\um_lyialeafsong_18.dbr`)

### Priority 4: Secret Passage Monster Souls

**Developer-Named Skeletons (15 records — need souls):**

These are skeleton monsters named after game developers that spawn in the Secret Passage alongside Toxeus the Murderer. Located at `records\xpack\creatures\monster\zzdev\`:

| # | Record | Name |
|---|--------|------|
| 1 | `z_arthur.dbr` | Arthur |
| 2 | `z_ben.dbr` | Ben |
| 3 | `z_chooch.dbr` | Chooch |
| 4 | `z_cory.dbr` | Cory |
| 5 | `z_dave.dbr` | Dave |
| 6 | `z_david.dbr` | David |
| 7 | `z_frazier.dbr` | Frazier |
| 8 | `z_josh.dbr` | Josh |
| 9 | `z_morgan.dbr` | Morgan |
| 10 | `z_nate.dbr` | Nate |
| 11 | `z_parnell.dbr` | Parnell |
| 12 | `z_scott.dbr` | Scott |
| 13 | `z_shawn.dbr` | Shawn |
| 14 | `z_tom.dbr` | Tom |
| 15 | `z_~v~.dbr` | ~v~ |

Also in zzdev: `n_emgiec.dbr`, `n_mega.dbr`, `n_vio.dbr` — need investigation.

These are the monsters the user wants souls for. They spawn in the same area as Toxeus and are the key Secret Passage encounters.

**Blood Cave monsters (drxcreatures/) — do NOT need souls:**
The 37 champion records (Sileni, Malefice, Blood Cult, etc.) and 34 quest records (Crow Heroes) in drxcreatures/ are Blood Cave creatures, separate from the Secret Passage proper. These do not need souls per user directive.

**Boss-class (need hand-crafted souls — see Priority 1):**
- Leinth (3 variants)
- Murder Bunny
- Secret Passage Hades
- SP Toxeus (Hero-class but functions as boss)

**Hero-class in secret passage:**
- Warden of Souls (`xsecrethero_wardenofsouls`) — Lv 48, Life element, Tank role. **Already has a soul** (tagSoulSVC9141). No action needed.

### Priority 5: Toxeus Soul Design

**Standing Directive**: Toxeus the Murderer must have the STRONGEST soul of any monster.

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

#### Design Decision: CONFIRMED — Option C (Two Distinct Souls)

1. **Main Toxeus soul** (`um_toxeus_21`): Overhaul existing soul to be **one of the strongest** in the game. Melee/rogue themed — lethal strike, traps, physical/pierce damage. Should rival Rakanizeus/Boneash power level but with a different niche.

2. **SP Toxeus soul** (`um_toxeus_99`): Create entirely new soul — **THE strongest soul in the game (Tier 1).** Dream/nightmare themed — distort reality, lucid dream. Should have:
   - Highest stat bonuses of any soul
   - Unique powerful proc or summon
   - Stats that reflect the nightmare/dream theme (INT + DEX hybrid)
   - Drop rate: 66% (Hero classification)

#### Current Hades Soul Stats (for power reference)

The existing main Hades soul (Legendary tier, iLvl 78) has:
- +193 DA, +314 HP, +415 MP, +53% cast speed
- +56% mana burn ratio, +19% protection
- +63% life modifier, 16% current life damage
- +90% bleeding, +79% cold modifier, +87% life modifier on DoTs
- Granted Skill: hades_star (Lv 5 autocast on hit)
- Augments: +6 to Spirit mastery, +6 to Stealth mastery
- 23% CDR, 45% projectile speed
- Penalties: -22% fire res, -28% lightning res

SP Hades soul should exceed these stats. SP Toxeus soul should exceed SP Hades.

### Priority 6: Add Test Bosses to Game World

| Boss | Placement | Status |
|------|-----------|--------|
| **Cold Worm** | Act 2 Egypt underground caves/tombs | PENDING — need to find cryptworm spawn pools and add Cold Worm as rare champion spawn |
| **Dagon** | All 23 Ichthian spawn pools (Greece coastal + Orient) | **DONE** — added as rare champion spawn (weight=2) via `_add_dagon_to_ichthian_pools()` in `apply_svc_patches.py`. Pools with 0% champion chance bumped to 15%. |

### Priority 7: Investigate & Decide

| Monster | Status | Notes |
|---------|--------|-------|
| **Graeae** | No action needed | Already in game — spawn in **Medea's Swamp** (IT expansion quest "Medea's Price", zone xq02). Three sisters (Deino Lv35-39, Enyo Lv37-40, Pemphredo Lv36-40) all have uber souls. The "01_graeae" folder is boss set numbering (01-05), not act numbering. |
| **Hades Forms 1 & 2** | Do NOT wire | Form 1 and 2 die during the fight → Form 3 spawns. Only Form 3 drops a soul. |
| **xq03_charonsoundrat** | Ignore | Quest trigger entity, not a real boss. |
| **Charon Form 2** | Already wired | All 3 Form 2 variants (39/41/43) have SV souls at 25%. |

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

### Issue #7: Major Bosses with Sub-25% Soul Drop Rates

Our patch script (`apply_svc_patches.py`) pushes soul drop rates to 66% (heroes/quest) or 25% (bosses), but these major bosses have much lower rates from the original SV database that our script doesn't catch:

| Boss | Classification | Current Rate | Target Rate | Variants |
|------|---------------|-------------|-------------|----------|
| **Typhon** | Boss | 1.5% | 25% | boss_titan_typhon_42/45/48 |
| **Hades Form 3** | Boss | 1.5% | 25% | boss_hadesform3_50/52/54 |
| **Megalesios** (Greek Telkine) | Boss | 2.0% | 25% | boss_greektelkine_megalesios_21/24/27 |
| **Ormenos** (China Telkine) | Boss | 3.0% | 25% | boss_chinatelkine_ormenos_38/41/44 + xpack variant |
| **Cerberus** | Boss | 3.5% | 25% | boss_cerberus_40/42/44 |

Note: Aktaios (Egypt Telkine) is already at 25% — the other two Telkines should match.

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

1. **Toxeus the Murderer must have the STRONGEST soul of any monster** — SP Toxeus soul outclasses everything. Main Toxeus soul is one of the strongest but weaker than SP.
2. **Hades Forms 1 & 2 do NOT get souls** — only Form 3 (the final form) drops a soul.
3. **All secret passage monsters should have souls** — Boss, Quest, Champion, and Hero classes all get souls in this endgame area.
4. **Soul power hierarchy (flexible, not rigid)**:
   - **Tier 1 (Ultimate)**: SP Toxeus — the single strongest soul
   - **Tier 2 (Elite endgame)**: SP Hades, Murder Bunny, uber bosses at end of Blood Cave / Secret Passage — roughly on par with each other
   - **Tier 3 (Top-tier)**: Main Toxeus and other strong boss souls — powerful but not dominating Tier 2
   - Other boss souls can be strong and have outliers, but shouldn't absolutely dominate the souls listed above
5. **Drop rate standards**: Fixed-location bosses = 25%, Heroes/Quest = 66%.
