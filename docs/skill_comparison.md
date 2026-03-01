# Soulvizier Skill Archaeology: v0.4.1 Beta → v0.9 → v0.98i

A comprehensive comparison of skills across all Soulvizier versions, identifying
removed mechanics, renamed skills, cut content, and orphaned experiments that
could be restored or adapted for SoulvizierClassic.

## Overview

| Version | Total Skills (in trees) | SV Custom | Orphaned DRX records |
|---------|------------------------|-----------|---------------------|
| 0.4.1 beta (Feb 2012) | 200 | 200 | 478 |
| 0.9 (later build) | 200 | 200 | 491 |
| 0.98i (final) | 200 | 200 | 616 |

All three versions have exactly 200 skills across 8 masteries (25 per mastery).
The skill count never changed — only the content of individual slots was swapped.

---

## THE BIG FIND: The Lost Dream Mastery

The most significant discovery is that **SV 0.4.1 contained a complete custom Dream mastery**
(`drxdreammastery.dbr` / `drxdreamskilltree.dbr`). This was a wholly original psionic/dream-themed
mastery that was later scrapped. Its skill records still exist as orphans in ALL versions
(even 0.98i). The entire skill tree was:

| Skill | Class | Tier | Max | Description |
|-------|-------|------|-----|-------------|
| **Dream Mastery** | Mastery | — | 72 | "Expand your consciousness to draw more deeply from the power of the dream realm and exert your will upon physical reality." |
| **Distortion Wave** | AttackWave | 1 | 12 | A wave of force with chaotic ripples that damages body and mind. 5s cooldown. |
| **Psionic Touch** | WeaponPool_ChargedFinale | 1 | 12 | Escalating charge melee: psionic energy in your weapons creates bone-shattering resonance. Apply to left mouse button. |
| **Sands of Sleep** | AttackChain | 1 | 8 | Chain-targeting sleep — renders enemies immobile for a duration or until attacked. |
| **Premonition** | Passive | 1 | 6 | Precognitive sense lets you stay one step ahead, boosting dodge/defense. |
| **Trance of Empathy** | BuffRadiusToggled | 2 | 12 | Toggle aura: enemies share the damage they inflict via telepathic link; siphons life. |
| **Psionic Artery** | Modifier (Psionic Touch) | 2 | 6 | Harmonize with psionic resonance to greatly increase life/energy channeling effects. |
| **Chaotic Resonance** | Modifier (Distortion Wave) | 3 | 8 | Amplifies physical distortion to shatter armor and break bones. |
| **Distortion Field** | PassiveOnHitBuffSelf | 3 | 6 | Psionic field bends reality, negating damage and dealing retaliatory damage. 30s internal cooldown. |
| **Psionic Blast** | AttackWave | 3 | 12 | Massive wave of force with chaotic ripples. 15s cooldown, 75 mana. |
| **Troubled Dreams** | Modifier (Sands of Sleep) | 3 | 8 | Sleeping enemies are tormented, eroding their constitution. |
| **Lucid Dream** (Psionic Touch mod) | Modifier | 3 | 8 | Enhanced dream control boosts Psionic Touch effects. |
| **Trance of Convalescence** | BuffRadiusToggled | 4 | 12 | Toggle aura: increased life recovery and damage absorption for party. |
| **Nightmare** | SpawnPet | 4 | 16 | Summons a nightmarish entity from the dream world. 60s cooldown, 150 mana. |
| **Psionic Burn** | 2nd:AttackRadius (Psionic Touch) | 4 | 8 | Psionic energy ignites inside the target and explodes outward to adjacent targets. |
| **Distort Reality** | AttackRadius | 5 | 12 | Tears the fabric of reality in a radius causing severe damage. 16s cooldown, 100 mana. |
| **Psionic Immolation** | Modifier (Distortion Wave) | 5 | 12 | Psionic energies ignite into electrical burn over a short duration. |
| **Temporal Flux** | Passive | 5 | 6 | Subtle acceleration of time — permanent movement speed increase. |
| **Phantom Strike** | AttackWeaponBlink | 5 | 12 | Vanish from waking world and reappear before a target with monstrous attack. *(Later moved to Occult as Nether Strike)* |
| **Trance of Wrath** | BuffAttackRadiusToggled | 6 | 12 | Toggle aura: waves of negative psionic energy disrupt thoughts and burn through physical being. |
| **Dream Stealer** | Modifier (Phantom Strike) | 6 | 8 | Rip the very dreams from enemies' minds, stealing their power. |
| **Hypnotic Gaze** | DispelMagic (Nightmare pet) | 6 | 16 | The Nightmare's hypnotic eye dominates lesser minds, controlling their actions. |
| **Lucid Dream** (passive) | Passive | 7 | 8 | Enhanced dream abilities across the board. |
| **Temporal Rift** | Modifier (Distort Reality) | 7 | 12 | Psionic surge that causes massive damage and temporarily freezes enemies in time. |
| **Phantasm** | AttackProjectileSpawnPet | 7 | 16 | Summon a phantasm that deranges minds and disturbs the fabric of reality. 180s cooldown, 300 mana. |

**Pet skills for Nightmare:**
- **Psionic Beam**: Beam of psionic energy surging into enemies
- **Dream Surge**: Expanding ring of dream-world energy
- **Hypnotic Gaze**: Mind control / confusion on lesser enemies

**Pet skills for Phantasm:**
- **Psionic Beam**: Channeled psionic damage
- **Distort Reality**: AoE reality-tearing wave

### Why it was cut
The Dream mastery slot (mastery 9 in TQIT) was needed for compatibility with the base game's
Dream class. Rather than conflict with existing Dream characters, the unique skills from this
tree were scattered into other masteries or simply abandoned.

### Restoration potential: ★★★★★
This is an entire coherent mastery with deep theming. Key candidates for individual skill
restoration into existing masteries:

- **Psionic Touch** → Could fit in Spirit as an alternative weapon proc
- **Distortion Wave / Psionic Blast** → Wave attacks would be unique in any mastery
- **Sands of Sleep** → Chain-targeting sleep is mechanically unique in SV
- **Trance of Empathy/Wrath** → Toggle auras with interesting trade-offs
- **Nightmare** (pet) → A mind-controlling pet with hypnotic gaze

---

## Replaced Skills: What Changed Between Versions

### Rogue/Occult

#### ★★★★★ Darklings → Breach (Tier 3)
**0.4.1**: `Skill_AttackProjectileSpawnPet` — *"Through a tenuous opening to the shadow realm,
the Occultist can draw out and coalesce darker energies into a shadow demon and hurl it at
enemies."* You'd throw shadow demons that would run at enemies and **DETONATE** causing AoE
damage. Multiple records show scaling detonation damage (`drx_petskill_boomb_01` through `_09`).

**0.98i**: `Skill_AttackProjectileAreaEffect` — "Breach" is just a generic AoE projectile.

**Verdict**: The Darklings mechanic (throw-able exploding summons) was one of the most iconic
and unique skills in early SV. Strongly recommend restoring. The pet records, detonation skills,
and boomer creature records all still exist in the database as orphans.

#### Maculate Wound → Dark Invigoration (Tier 4)
**0.4.1**: "Add a chance that weapon attacks will open a dark wound on the enemy, exposing their
physical weakness." Debuff-focused modifier.

**0.98i**: "Dark Invigoration" — different mechanic entirely.

#### Breach → Shadow Grasp (Tier 5)
**0.4.1**: "Breach" was originally a modifier at tier 5 — "The Occultist pries open an aperture
to the shadow realm, allowing dark energies to pool more freely."

**0.98i**: Became "Shadow Grasp", a projectile modifier. The "Breach" name was recycled for the
skill that replaced Darklings.

### Warfare

#### Hamstring → Lineal Chains (Tier 4)
**0.4.1**: `Skill_Modifier` — "An attack aimed at the enemy's legs reduces their ability to run
and increases the duration of effects that slow movement speed."

**0.98i**: `Skill_AttackChain` — Complete mechanical overhaul from a slow debuff to a chain attack.

**Restoration potential: ★★★** — Hamstring was a classic debuff mechanic. Could be added as a
modifier to an existing attack.

#### Doom Horn → Doom Bond (Tier 6)
**0.4.1**: `Skill_Modifier` — "Your War Horn heralds the doom of your enemies, shattering their
nerves and reducing their ability to fight."

**0.98i**: `SkillSecondary_AttackRadius` — Changed from a war horn debuff modifier to an AoE.

### Hunting

#### Spear Tempest → Eviscerate (Tier 3, slot renamed)
The slot that was "Spear Tempest" in 0.4.1 became a second "Eviscerate" in 0.98i. The original
Spear Tempest ("Execute a whirling multi-hit attack so fast and complex that enemies are caught
off guard. Spear Required") was moved to a different slot as an orphan/SV-added skill.

### Nature

#### ★★★★ Thorn Sprites → Elemental Flurry (Tier 1)
**0.4.1**: `Skill_AttackProjectileSpawnPet` — *"Allows the Wanderer to throw a clutch of
mischievous thorn sprites at enemies. Although they do little damage on their own, when
enough of them swarm an enemy they can inflict a nasty sting."* Summoned small sprite creatures.

**0.98i**: `Skill_AttackWeaponRangedSpread` — A generic ranged spread attack.

**Restoration potential: ★★★★** — Throwable swarming sprites was highly thematic for Nature.
The creature records and sprite summon records still exist.

#### Briar Ward → Quill Ward
Simple rename; mechanics preserved (DefensiveWall class unchanged).

#### Fabrical Tear → Dissemination (Tier 3)
**0.4.1**: `Skill_ProjectileModifier` — "Learn to call the thorn sprites with greater insistence,
causing them to spawn violently, discharging elemental energy on spawning."

**0.98i**: `SkillSecondary_AttackRadius` — Changed class and mechanic entirely when Thorn Sprites
was replaced.

### Spirit

#### Spirit Lure class change
**0.4.1**: `Skill_SpawnPet` — "Create a nefarious totem near the caster that lures monsters
toward it and drains their life."

**0.98i**: `Skill_AttackProjectileSpawnPet` — Changed to a projectile-delivered pet.

---

## Notable Orphaned Skills (Cut Content)

These DRX records exist in the databases but were never wired into any skill tree.
Many are iterative experiments, but some are fully developed and thematic.

### High-Priority Restoration Candidates

| Skill | Class | Found In | Description | Potential Home |
|-------|-------|----------|-------------|----------------|
| **Darklings** | SpawnPet | 0.4.1+ | Throw exploding shadow demons | Rogue/Occult (restore to Breach slot or new) |
| **Sands of Sleep** | AttackChain | 0.4.1+ | Chain sleep — immobilize groups | Spirit or Nature |
| **Distortion Wave** | AttackWave | 0.4.1+ | Psionic force wave, body+mind damage | Spirit |
| **Psionic Touch** | WeaponPool_ChargedFinale | 0.4.1+ | Escalating charge melee with psionic energy | Spirit or Warfare |
| **Nightmare** | SpawnPet | 0.4.1+ | Dream-world horror pet with Hypnotic Gaze | Spirit |
| **Thorn Sprites** | AttackProjectileSpawnPet | 0.4.1+ | Swarm of throwable nature sprites | Nature |
| **Phantasm** | AttackProjectileSpawnPet | 0.4.1+ | Temporary phantasm that warps reality | Spirit |
| **Distort Reality** | AttackRadius | 0.4.1+ | Tears fabric of reality in AoE | Spirit |
| **Trance of Wrath** | BuffAttackRadiusToggled | 0.4.1+ | Psionic damage aura toggle | Spirit |
| **Trance of Empathy** | BuffRadiusToggled | 0.4.1+ | Damage reflection aura toggle | Defense or Spirit |
| **Hamstring** | Modifier | 0.4.1+ | Slow enemies, increase slow duration | Warfare or Hunting |
| **Dream Stealer** | Modifier | 0.4.1+ | Steal power by ripping dreams from minds | Spirit modifier for Nether Strike |

### Lower Priority / Experimental

| Skill | Class | Description |
|-------|-------|-------------|
| **Psionic Blast** | AttackWave | Larger version of Distortion Wave (15s CD, 75 mana) |
| **Psionic Burn** | 2nd:AttackRadius | Psionic explosion from Psionic Touch target |
| **Psionic Immolation** | Modifier | Electrical burn modifier for Distortion Wave |
| **Temporal Flux** | Passive | Permanent movement speed boost |
| **Temporal Rift** | Modifier | Freeze enemies in time + massive damage |
| **Premonition** | Passive | Precognitive dodge/defense boost |
| **Troubled Dreams** | Modifier | Sleeping enemies take DoT + constitution loss |
| **Chaotic Resonance** | Modifier | Armor-shattering amplifier for Distortion Wave |
| **Lucid Dream** | Passive | General dream-ability enhancer |
| **Dream Surge** | AttackProjectileRing | Expanding ring of dream energy (Nightmare pet) |
| **Hypnotic Gaze** | DispelMagic | Mind control on weaker enemies |
| **Mind Breaker** (orphaned variant) | DispelMagic | Psionic pulse that dispels hostile enchantments |
| **^BGIMME MANA** | PassiveOnLifeBuffSelf | Dev debug skill (lol) |

### Interesting "Detonate" Variants

The Darklings detonation system had **9 scaling variants** (`drx_petskill_boomb_01` through
`drx_petskill_boomb_09`), a small variant (`drx_petskill_lil_boom`), and a display-only
version for the skill UI. This was a well-developed system, not a prototype.

---

## Per-Mastery Skill Lists (All Versions)

### 1. Warfare (25 skills)

| # | Skill | Class | Tier | Max | Changed? |
|---|-------|-------|------|-----|----------|
| 1 | Warfare Mastery | Mastery | 0 | 72 | Stable |
| 2 | *pet mod: Glory* | PetModifier | — | — | Stable |
| 3 | *pet mod: Triumph* | PetModifier | — | — | Stable |
| 4 | Dual Wield | WPAttack_BasicAttack | 1 | 6 | Stable |
| 5 | Onslaught | WeaponPool_ChargedLinear | 1 | 8 | Stable |
| 6 | Weapon Training | Passive | 1 | 6 | Stable |
| 7 | War Dance | AttackWeaponCharge | 2 | 8 | Stable |
| 8 | Parry | Passive | 2 | 8 | Stable |
| 9 | Ignore Pain | Modifier | 2 | 6 | Stable |
| 10 | Battle Rage | PassiveOnHitBuffSelf | 2 | 12 | Stable |
| 11 | Hew | WPAttack_BasicAttack | 3 | 6 | Stable |
| 12 | War Horn | AttackRadius | 3 | 10 | Stable |
| 13 | Battle Standard | SpawnPet | 3 | 10 | Stable |
| 14 | Lacerate | Modifier | 4 | 8 | Stable |
| 15 | Cross Cut | WPAttack_BasicAttack | 4 | 6 | Stable |
| 16 | Crushing Blow | Modifier | 4 | 8 | Stable |
| 17 | **Hamstring → Lineal Chains** | Modifier → AttackChain | 4 | 6 | **REWORKED** |
| 18 | Finesse | Modifier | 5 | 8 | Stable |
| 19 | Heart of War | Modifier | 5 | 6 | Stable |
| 20 | Tumult | WPAttack_BasicAttack | 6 | 6 | Stable |
| 21 | Counter Attack | Modifier | 6 | 8 | Stable |
| 22 | **Doom Horn → Doom Bond** | Modifier → 2nd:AttackRadius | 6 | 6 | **REWORKED** |
| 23 | Double Helix | WPAttack_BasicAttack | 7 | 6 | Stable |
| 24 | Ardor | Modifier | 7 | 6 | Stable |
| 25 | Ancestral Horn | SpawnPet | 7 | 16 | Stable |

### 2. Defense (25 skills) — All stable across versions

### 3. Earth (25 skills) — All stable across versions

### 4. Storm (25 skills) — All stable across versions

### 5. Rogue/Occult (25 skills)

| # | Skill | Class | Tier | Max | Changed? |
|---|-------|-------|------|-----|----------|
| 1 | Occult Mastery | Mastery | — | 72 | Stable |
| 2 | *buff: Blade Honing* | BuffRadiusToggled | — | — | Stable |
| 3 | *pet mod: Greater Power* | PetModifier | — | — | Stable |
| 4 | Envenom Weapon | BuffSelfToggled | 1 | 12 | Stable |
| 5 | Calculated Strike | AttackWeaponCharge | 1 | 8 | Stable |
| 6 | Agility | Passive | 1 | 6 | Stable |
| 7 | Flash Powder | AttackRadius | 2 | 8 | Stable |
| 8 | Blade Mastery | Passive | 2 | 8 | Stable |
| 9 | Nightshade | Modifier | 3 | 8 | Stable |
| 10 | Blade Fury | AttackWeaponCharge → WPAttack_BasicAttack | 3 | 8 | Class changed |
| 11 | **Darklings → Breach** | AttackProjectileSpawnPet → AttackProjectileAreaEffect | 3 | 12 | **REWORKED** ★ |
| 12 | Smoke Screen | AttackProjectileSpawnPet | 3 | 8 | Stable |
| 13 | **Maculate Wound → Dark Invigoration** | Modifier | 4 | 8 | Renamed |
| 14 | Throwing Knife | AttackProjectileBurst | 4 | 12 | Stable |
| 15 | Toxic Concoction | AttackProjectile | 4 | 8 | Stable |
| 16 | Mandrake | Modifier | 5 | 8 | Stable |
| 17 | Nether Strike | AttackWeaponBlink | 5 | 12 | Stable (was Phantom Strike in Dream mastery) |
| 18 | Poisonous Gas | ProjectileModifier | 5 | 8 | Stable |
| 19 | **Breach → Shadow Grasp** | Modifier → ProjectileModifier | 5 | 12 | **REWORKED** |
| 20 | Toxin Distillation | Modifier | 6 | 12 | Stable |
| 21 | Shadow Lore | Modifier | 6 | 8 | Stable |
| 22 | Flurry of Knives | Modifier | 6 | 6 | Stable |
| 23 | Shadow Stalker | SpawnPet | 6 | 16 | Stable |
| 24 | Dark Vapors | Modifier | 7 | 8 | Stable |
| 25 | Aphotic Ichor | ProjectileModifier | 7 | 12 | Stable |

### 6. Hunting (25 skills)

| # | Skill | Tier | Changed? |
|---|-------|------|----------|
| 1-24 | (mostly stable) | — | — |
| Notable: | **Spear Tempest → Eviscerate** (tier 3) | 3 | Renamed/reslotted |

### 7. Nature (25 skills)

| # | Skill | Class | Tier | Changed? |
|---|-------|-------|------|----------|
| 1 | **Thorn Sprites → Elemental Flurry** | SpawnPet → WeaponRangedSpread | 1 | **REWORKED** ★ |
| 5 | **Briar Ward → Quill Ward** | DefensiveWall | 3 | Renamed only |
| 6 | **Fabrical Tear → Dissemination** | ProjectileModifier → 2nd:AttackRadius | 3 | **REWORKED** |

### 8. Spirit (25 skills)

| # | Skill | Changed? |
|---|-------|----------|
| All | Stable | Spirit Lure class changed (SpawnPet → AttackProjectileSpawnPet) |

---

## Restoration Recommendations

### Tier 1: Bring Back ASAP

1. **Darklings** (Rogue/Occult) — Replace "Breach" with the original Darklings mechanic.
   Throw shadow demons that sprint at enemies and detonate for AoE damage. The
   detonation records exist with 9 damage scaling tiers. This was the most memorable
   skill in early SV and its loss made Occult feel more generic.

2. **Thorn Sprites** (Nature) — Replace "Elemental Flurry" or add alongside it.
   Throwable swarming nature sprites. Unique summoner-flavored attack for Nature that
   reinforces the pet/summon identity.

### Tier 2: Strong Candidates for New Skills

3. **Sands of Sleep** — Chain-targeting sleep CC is mechanically unique. No other skill
   in SV does group crowd control via chain targeting. Could fit in Spirit or Nature.

4. **Distortion Wave** — A psionic force wave dealing physical + mental damage. Wave
   attacks are rare in SV. Could work as a Spirit addition or Warfare tier 5+ skill.

5. **Trance of Empathy** — Damage reflection aura toggle. Very interesting party mechanic.
   Could fit Defense (defensive theme) or Spirit (psionic theme).

6. **Nightmare** (pet) — A mind-controlling horror from the dream world. Spirit already
   has 3 summons, so this might be better as a rework of an existing Spirit pet modifier.

### Tier 3: Consider for Flavor

7. **Hamstring** (original Warfare modifier) — Classic debuff that was replaced by a
   chain attack. Could be added as an additional modifier to Take Down or War Dance.

8. **Dream Stealer** — "Rip dreams from enemies' minds" is too cool flavor-wise to leave
   on the cutting room floor. Could be a modifier for Nether Strike in Occult.

9. **Psionic Touch** — Escalating charge weapon pool skill. Unique mechanic where each
   hit builds power. Could enhance Spirit's melee viability.

10. **Temporal Flux** — Permanent movement speed passive. Simple but broadly useful.
    Could fit anywhere that has a passive slot available.

### Skills to Leave Cut

- **Phantasm** — 180s cooldown and 300 mana makes this an "ultimate" skill that doesn't
  fit the existing tree structure well.
- **Distort Reality** — Already similar to existing AoE skills (Vision of Death, etc.)
- **Most Dream mastery modifiers** — Too coupled to other Dream skills to work standalone.
- **^BGIMME MANA** — Obviously a dev debug skill. (But it's funny.)
