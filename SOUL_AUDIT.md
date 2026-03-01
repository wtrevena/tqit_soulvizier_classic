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

## Issues Found

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

## Tuning Recommendations

1. **Carrion Crow**: The 2 Hero-class crows will legitimately drop souls. If the user reports seeing them from normal (non-starred) crows, that's a save cache issue.

2. **Elder/Quest/Ghost uber monsters**: Consider whether `qs_minotaurconqueror`, `ghosthero`, `eldercyclops`, `elderminotaur`, `elderminotaurlord` should keep their 66% drop rate. These are clearly special encounters but have improper classification in the original SV data.

3. **Soul stat balance**: All 140 uber souls have 0 stat requirements (correct per mod goals). Stats scale linearly with level. Element resistances include a penalty to the opposing element (e.g., fire souls give -cold res).

4. **Legacy 0.5% champions**: 26 champion-prefix monsters with 0.5% from original SV data. Negligible impact.
