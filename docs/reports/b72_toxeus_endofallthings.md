# b72 - TOXEUS, END OF ALL THINGS (Will ruled 2026-07-16)

Implementer round 1. Branch `feat/toxeus-undivided` (worktree, off post-build45 main
`33d25d6`). Module `tools/patches/toxeus_endofallthings.py` (registered in the REGISTRY
after `enslaver_pet_fx`, before `visuals`).

- Reference arz (baseline): build45 `917d9047d2281284f5fd5e9a163b9c5c` (read-only).
- Scratch arz (this feature): **`a6b896bd8d05673b8cfc37eecd6cfb4a`** (deterministic:
  built twice, identical md5 -> idempotent).
- Record-diff vs build45: **exactly 16 NEW records, 0 removed, 0 modified existing**
  (the feature and nothing else).

## What ships

A single supra-tier **soul ring**, `Soul of Toxeus, End of All Things` (`{^F}` magenta),
crafted at the uber-forge from the **LEGENDARY (`_l`) tier of the three Toxeus souls**
(green-Greece base + Enslaver + Devourer). It grants **Summon Toxeus, End of All Things**
- ONE permanent, 1-at-a-time pet (`Toxeus the Murderer, End of All Things`), the
apotheosis of the Toxeus line. The pet is cloned from the PROVEN permanent Devourer pet
(`bloodtoxeus_1..3`, RevenantPoison skeleton, crimson skin, no TTL); only
animation/skill/FX/stat fields are edited (PET SAFETY LAW), zero Monster.tpl->Pet.tpl
loot-field copy, bare-clone dtype-safe overrides.

## Kit table (ruled item -> what shipped -> exact records)

| # | Ruling | Implementation | Records |
|---|--------|----------------|---------|
| 1 | Unlimited energy | huge `characterMana` 999999 + `characterManaRegen` 9999 on each pet (crash-safe Character stat fields; chosen over zeroing SHARED skill costs) | pet fields on `toxeus_eoat_1..3` |
| 2 | Nether Strike max, 0.5s cd | clone of the Enslaver-proven `netherstrike` (pet-usable lineage), `skillCooldownTime` 1.0->0.5, fired at max slot level 12 | `svc_eoat_netherstrike.dbr` |
| 3 | Max Smoke Screen (Occult) | reuse of the shipped Occult pet smoke-screen skill at level 16 | `drx_smokescreen_petskill_default.dbr` (reused) |
| 4 | Max skill granted by Galefury | decoded `ar_hunter_helm` (the b66 storm straw-hat "Galefury") `itemSkillName` = **`hunter_helm_galefury`**, a `Skill_BuffAttackRadiusToggled` storm-gale weapon aura; given at its max level 1 | `hunter_helm_galefury.dbr` (reused) |
| 5 | Tears of Blood (Arcane Formula - Blood of Ares) | located Blood-of-Ares granted skill = `e_da_bloodofares_tearsofblood` (a bleed/fire AoE nova); cloned, cd 120->3.0. **FEASIBILITY: not a true on-hit retaliation trigger** (that is an ITEM autocaster a pet cannot carry) - it fires reactively as a frequent 3.0s-cd specialAttack | `svc_eoat_tearsofblood.dbr` |
| 6 | Murderer's Edge; NO green poison, use Devourer's BLACK poison | high `characterOffensiveAbility` 2600 + a passive (offensivePhysical/crit/OA) + weapon buff = the Devourer's OWN `bloodtoxeus_envenomweapon`. **FEASIBILITY: the Devourer has NO literally-black poison; this is his signature CRIMSON blood-envenom** (the closest dark-poison asset in his lineage) - honestly crimson, not black | `svc_eoat_murderersedge.dbr` + `bloodtoxeus_envenomweapon.dbr` (reused as `buffSelfSkillName`) |
| 7 | Entropy aura (vitality-decay + RR radius) | clone of the shadowlink weapon-enchantment toggled radius aura -> a fresh buff payload (elemental-resistance reduction + slow-life-leach vitality decay), radius 36 (b57 party convention). **FEASIBILITY: the shipped shadowlink buff payload is zeroed, so the debuff magnitudes are authored fresh - a tuning surface** | `svc_eoat_entropyaura.dbr` + `svc_eoat_entropybuff.dbr` |
| 8 | Blood Feast (deep leech + blood nova) | high `offensiveLifeLeech` 200-300 on strikes + the Devourer's OWN `melinoe_bloodboil` (BloodBoil AoE) + `lifedrain`, all from the Devourer's proven kit | `melinoe_bloodboil.dbr`, `lifedrain.dbr` (reused) |
| 9 | "There is room in me" (blood-cave tall casters that summon hounds) | identified the family = **`c_disciple_42`** (Blood-Witch Disciple, the tall caster whose `disciple_summon_bloodbeast` spawns `c_bloodhound_40`); the pet's `svc_eoat_thralls` summons 3 disciple thralls that carry that hound-summon. **FEASIBILITY FLAG #1 (Will-mandated): this is a 3-DEEP chain** (pet -> disciple pets -> hound sub-summons); proven depth is 2 (Enslaver -> marauders). The disciples are wired at the proven depth-2 and the hound summon is ATTACHED for the depth-3 attempt, but **whether a PET's own spawn-pet skill fires while it is itself a pet is engine-UNVERIFIED** - needs Will's in-game confirmation. Documented fallback if depth-3 is dead: have the EoAT pet summon a few bloodhound pets DIRECTLY alongside the disciples (both depth-2, provably safe) | `svc_eoat_thralls.dbr`, `eoat_disciple_1..3.dbr`, `disciple_summon_bloodbeast.dbr` |
| 10 | "The Ending" ultimate (Light-of-Helios screen flash) | located Manetho's `sungaze` (`Skill_AttackProjectileAreaEffect`, projectile `aktaois_lightofra01` = the light-of-Ra screen flash). Cloned, long cd 60s. **The donor ships ZERO damage and a `SunGaze` skillSpecialAnimationName the RevenantPoison skeleton rig lacks (uncastable per the b52 Ephialtes-nova lesson)** - so the clone CLEARS the special anim (the flash rides on the projectile record, not the animation) and AUTHORS real cataclysm damage (physical 2400-3600 + vitality 1800-2600) at explosion radius 8 | `svc_eoat_ending.dbr` |
| 11 | Arrat's Corruption AOE | located the monster = **`um_ararat_36`** ("Arrat/Ararat the Corruptor", spider family; his `skillName2` `ararat_corruption`). Signature = a `Skill_AttackRadius` debuff nova: **mana-burn (`offensiveManaBurnDamageRatio` 50) + attack-speed slow + shortened target life/mana-leach windows**. The shipped SOULSKILLS variant is already pet-castable (mana 0, cd 30) so it is reused verbatim in the kit + specialAttack table at max level 20 | `records\skills\soulskills\ararat_corruption.dbr` (reused) |

Plus the summon plumbing: `summon_toxeus_eoat.dbr` (petLimit 1, permanent, licheking icon), the
soul ring `soul_of_toxeus_endofallthings.dbr`, and the uber formula
`svc_toxeus_eoat_formula.dbr`.

## Feasibility flags (honest)

- **FLAG #1 (depth-3 thrall chain):** the "there is room in me" chain is 3-deep (pet ->
  disciple pets -> hound summons). Depth-2 is proven; depth-3 (a pet's own spawn skill
  firing while it is a pet) is UNVERIFIED. Shipped at depth-2 with the hound summon
  attached for the depth-3 attempt; needs Will's in-game check. Fallback documented.
- **FLAG #2 (equipment - engine + shipping gate HARD-RESIST):** the ruled supra pieces
  (blood spear, uber shield, Paragon of Violence, melee armor) are all player-tier
  Legendary UNIQUES. A DB-wide audit proved ZERO of 25,000+ working monster/pet equip
  slots auto-equip such a unique (the pet spawns NAKED), and the shipping **B-SUMMON-1
  gate FAILS THE BUILD** if a pet direct-equips one. This was proven empirically here: an
  initial attempt to equip the 8 pieces via `_set_pet_equipment` tripped B-SUMMON-1 on
  the written arz and blocked the build. **There is no supported path to wear a specific
  player unique on a pet on this engine.** Resolution: the pet wears NONE of them (keeps
  the Devourer's proven loot-table loadout for visible gear + mobility); its supra-tier
  power is delivered by its DIRECT stat block. See the equipment render table.
- **FLAG #3 (crimson, not literally black poison):** ruling 6 asks for the Devourer's
  black poison. The Devourer has no literally-black poison asset; his signature is the
  CRIMSON `bloodtoxeus_envenomweapon`. Shipped that (his own dark blood-envenom), reported
  honestly as crimson.
- **FLAG #4 (Tears of Blood is not a true retaliation trigger):** a true on-taking-damage
  trigger is an item autocaster a pet cannot carry; shipped as a frequent reactive
  specialAttack (3.0s cd) instead.
- **Tuning surfaces (flagged for vet, not blockers):** entropy-aura debuff magnitudes
  (authored fresh over a zeroed donor payload); The Ending damage numbers; the specialAttack
  firing chances.

## Stat ceiling (which Toxeus champion is strongest + the ceiling math)

Decoded the fought Toxeus champions in build45:

| Champion | Record | Legendary life | handHitMax | STR/DEX | scale |
|----------|--------|---------------:|-----------:|---------|------:|
| Enslaver (uber) | `um_toxeus_enslaver_99` | **60,000** | **500** | 560/720 | 2.4 |
| Enslaved Marauder | `um_enslaver_marauder_99` | 18,000 | 380 | - | 2.0 |
| Endless-Hunt stalker | `um_toxeus_hunt_99` | 30,000 | 280 | - | 1.9 |
| Ararat (corruptor) | `um_ararat_36` | 13,355 | 183 | 183/289 | 1.0 |

**Strongest = the Enslaver** (60,000 Legendary life, 500 handHit, STR 560 / DEX 720). That
is the ceiling. EoAT Legendary pet **exceeds it on every axis**: life **82,000** > 60,000,
handHitMax **620** > 500, STR **640** > 560, DEX **800** > 720, plus OA 2,600 (Enslaver
uses 0 / mastery). Per-tier life `[45000, 62000, 82000]` (Normal/Epic/Legendary).

## Equipment render table (honest)

| Slot | Ruled piece | Record | Outcome |
|------|-------------|--------|---------|
| Weapon (RightHand) | Blood Spear (The Last Emperor) | `supra\wep_spear` | **SKIPPED** - Legendary unique, B-SUMMON-1 forbids; renders naked |
| Offhand (LeftHand) | Uber Shield (Agathodaemon) | `supra\wep_shield` | **SKIPPED** - same; also 2H spear precludes a shield |
| Neck | Paragon of Violence | `supra\neck_melee` | **SKIPPED** - same |
| Ring | supra melee ring | `supra\ring_melee` | **SKIPPED** - same |
| Head/Torso/Arms/Legs | supra melee armor | `supra\ar_melee_*` | **SKIPPED** - same |

None of the 8 ruled supra pieces can be worn by a summoned pet on this engine (see FLAG #2).
The pet keeps the Devourer's proven visible loadout; its power is baked as direct stats.

## Visual identity (ratified, b71 law)

Ash-pale/bone RevenantPoison skeleton mesh + crimson skin (`newskeleton_crimson.tex`,
inherited from the Devourer), scale 2.25. ONE consistent identity across the summon-skill
button icon (`lichekingup`/`down`) and the pet-bar portrait (`licheking_party_up`/`red`) -
the apocalyptic-lich family the Devourer already uses (arc-proven; every tex resolves in the
shipped arcs, contracts_resources green). Per-skill fragment colors ride each kit skill's own
FX (crimson blood nova, dark thralls, light-of-Ra flash). ZERO green residue
(heartofoak/regrowth/natureswrath stripped; base envenom replaced by crimson) - the b71
enslaver chain gate walks the EoAT chain and confirms it.

## Flavor text (Will's veto surface)

- Soul name: `{^F}Soul of Toxeus, End of All Things`
- Pet name: `Toxeus the Murderer, End of All Things` (auto-whitened by the b50 pet-name
  standard to the plain-white pet-bar sibling, matching the bloodtoxeus/enslaver convention)
- Soul description: *"The last shape the first murderer wears: not the poisoner of Greece,
  not the drowned Devourer, not the Enslaver of the dead, but all of them at once and none
  of them held back. When the three souls are made one, the debt he came to collect is every
  heartbeat there is. Summon what is left when there is nothing left to end."*
- Apocalyptic flavor line: *"He was the end of one man in an alley. Now he is the end of the
  alley, the city, the road out of it, and the last witness who might have told the tale."*
- Formula: `Rite of the Undivided`
- Thrall: `Blood-Witch Thrall`

## THE ONE OPEN WILL DECISION - formula acquisition

The uber formula `svc_toxeus_eoat_formula.dbr` (the "Rite of the Undivided") is authored and
**craftable** (reagent affix constraints cleared so the 3 plain Legendary souls qualify by
base; random artifact bonus cleared so the soul is deterministic). What is NOT wired is **how
the player OBTAINS the formula item itself** - this is the one design decision reserved for Will.

**Recommended (thematic) option:** drop the Rite from the **Devourer superboss
(Hemorrheus / Toxeus the Murderer, Devourer of Blood)** beyond the secret waterfall chamber -
the final Toxeus the player fights - as a guaranteed/high-chance Boss-locked drop. Thematically
the last Toxeus the player defeats hands over the rite to fuse all three. Alternatives: (a) a
fixed drop from the Enslaver; (b) the uber-forge NPC sells/teaches it once all three Legendary
Toxeus souls are in inventory; (c) a hidden chest in the Uber Dungeon.

Round 1 leaves the formula craft-ready but its drop UNWIRED, pending Will's ruling.

## Verification (all green)

- Full scratch DB build EXIT=0; deterministic (md5 `a6b896bd`, identical on rebuild).
- All 27 registry-module verifies green, including `enslaver_pet_fx.verify` (its b71
  anti-oscillation chain gate now walks the EoAT chain: soul->summon->icon->pets->portrait->
  zero-green->disciple sub-summon) and `toxeus_endofallthings.verify`.
- Record-diff vs build45: 16 new records, 0 removed, 0 modified existing (A7 + everything
  else untouched).
- B-SUMMON-1 summon-pet validator: **0 strict failures** (after removing the supra-unique
  equips).
- Text.arc built + `validate_tags` PASS (all 8 EoAT tags resolve, incl the whitened
  `tagMonsterToxeusEoATPet`).
- Contracts souls/summons/resources: **0 P0 / 0 P1** (4904 P2 all pre-existing base/SV;
  zero EoAT records in any violation).
- Negative test (in-process): baseline verify PASSES; 4/4 planted defects (Ararat removed,
  formula affix replanted, wrong pet name, supra-unique leak) CAUGHT.
