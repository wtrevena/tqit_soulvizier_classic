# Boss Souls Design Doc

> Design specification for completing every un-finished soul in Soulvizier Classic. Covers the
> 60-boss Table B in `docs/SOULS_COMPLETENESS_AUDIT.md` (9 already-crafted exemplars need no work; the
> other ~51 are wired-but-stat-only "never-completed" souls that get a completion pass), the 1 STUB
> (Limos Lifeeater), and every no-soul design target (Ainex headlining). Each entry gives the
> boss + record path, soul name + lore, grant type (summon vs skill) with rationale, the exact
> source records to derive from, a full N/E/L stat block in Will's exemplar style, icon, tag names,
> and which builder-function pattern to implement it with. Read
> `docs/SOULS_COMPLETENESS_AUDIT.md` first (the roster), then this. No em dashes by house style.

---

## 0. How to read this doc / the taste standard it matches

This doc was written by reverse-engineering the souls Will hand-authored with the most care in
`tools/apply_svc_patches.py`, then holding every new design to that depth. Section 1 quantifies that
standard. Sections 2 onward are the per-soul designs, grouped by faction/area. The 10 headliners
(Section 2) get full three-tier stat blocks and, where they summon, a full pet loadout spec. The
bulk rosters (Sections 3 onward) are specified densely but share per-faction stat templates to keep
the doc actionable.

**Every design obeys the hard implementation constraints** (from `CLAUDE.md` "Key technical lessons"
and the audit's wiring recipe):

- **Souls are built with bare `_ensure_record` (never `clone_record`)** into
  `records\item\equipmentring\soul\svc_uber\<base>_soul_{n,e,l}.dbr`. Cloning brings stat values that
  corrupt saved items. `_create_soul(db, base, tag, tiers, monster, drop_rate)`
  (`apply_svc_patches.py:1325`) already does this correctly; use it for every skill-grant soul.
- **Permanent pets carry NO `spawnObjectsTimeToLive`** (set to `[]`). Achieved for free by cloning
  the summon skill from Lyia's `records\skills\soulskills\summon_lyia.dbr`.
- **NEVER copy equipment/loot fields Monster.tpl -> Pet.tpl** (crashes the game). Pet records are
  cloned from **Lyia Leafsong** (`records\skills\soulskills\pets\lyialeafsong_{1,2,3}.dbr`); only
  animation fields are copied (`_copy_animation_fields`) and only existing skill fields are updated
  (`_update_existing_fields`); equipment is set with `_set_pet_equipment` (hardcoded `[N,E,L]` item
  paths).
- **`{^F}` name-tag prefix** on every soul display name (pink/magenta text).
- **Augment-skill handles: write the EXACT verified path, never a `_SK_*` shorthand.** This is the
  single most dangerous authoring trap in the whole builder, and it was verified the hard way against
  the built `.arz` for this revision:
  - `_set_soul_fields` (`apply_svc_patches.py:192-196`) writes `augmentSkillName1/2` **verbatim** via
    `db.set_field` with **zero `_find_record` resolution and zero fuzzy matching**. A wrong augment
    path does **not** self-heal - it ships a dead augment (the soul silently grants nothing for that
    slot). `_find_record`'s fuzzy resolution is used only for the pet/summon builders, NOT for augment
    strings on souls. So the earlier advice to "lean on `_find_record` for augments" was wrong: it
    never runs on these fields.
  - Several `_SK_*` constants (`apply_svc_patches.py:1360-1393`) are themselves **dangling** in the
    built database (their literal string value points at a record that does not exist). DB-resolved
    2026-07-06, every constant this doc touches:

    | Constant | Value in source | Resolves? | Use THIS exact path instead |
    |---|---|---|---|
    | `_SK_CHAIN_LIGHTNING` | `records\skills\storm\drxchainlightning.dbr` | **DANGLING** (basename absent everywhere) | `records\skills\storm\drxlightningbolt_chainlightning.dbr` (Class `SkillSecondary_ChainLightning`) |
    | `_SK_RAVAGES_OF_TIME` | `records\skills\dream\drxravagesoftime.dbr` | **DANGLING** (basename absent everywhere) | `records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr` (Class `Skill_Modifier`; note `spirit`, not `dream`) |
    | `_SK_PHANTOM_STRIKE` | `records\skills\dream\drxphantomstrike.dbr` | **DANGLING** | `records\xpack\skills\dream\drxphantomstrike.dbr` (xpack) |
    | `_SK_STUDY_PREY` | `records\skills\stealth\drxstudyprey.dbr` | **DANGLING** | `records\skills\hunting\drxstudyprey.dbr` (hunting) |
    | `_SK_DISTORTION_WAVE` | `records\skills\dream\drxdistortionwave.dbr` | **DANGLING** | `records\xpack\skills\dream\drxdistortionwave.dbr` (xpack) |
    | `_SK_DUAL_WEAPON`, `_SK_ONSLAUGHT`, `_SK_TERNION`, `_SK_DEATH_CHILL`, `_SK_DARK_COVENANT`, `_SK_STORM_NIMBUS`, `_SK_SQUALL`, `_SK_COLD_AURA`, `_SK_PLAGUE`, `_SK_HEART_OF_OAK`, `_SK_WAR_HORN` | (their literal values) | **OK** | use the constant's value as-is |

    Implementation rule: **hardcode the verified string** for every augment in every per-soul spec
    below (the specs already do, post-revision). Do NOT reintroduce a `_SK_CHAIN_LIGHTNING` /
    `_SK_RAVAGES_OF_TIME` / `_SK_PHANTOM_STRIKE` / `_SK_STUDY_PREY` / `_SK_DISTORTION_WAVE` reference
    without first fixing the constant's value at the source (all five dangling constants should be
    repointed to the "use THIS" column, but that touches shipped code and is out of this doc's scope -
    see the note below). Until they are fixed, treat those five constant NAMES as poison.
  - **Pre-existing production bug (flagged separately, not this doc's to fix):** the shipped
    `_create_sp_toxeus_soul` assigns `augmentSkillName2 = _SK_DISTORTION_WAVE`, which dangles - so SP
    Toxeus ("THE strongest soul in the game") currently ships with a **dead Distortion Wave augment**.
    The real record is at `records\xpack\skills\dream\drxdistortionwave.dbr`. This is an existing
    live-code defect, independent of any new design here; it is called out so the implementer fixes
    the constant (which also un-breaks SP Toxeus) rather than copying the broken pattern.
  - All soulskill PROC records named as `itemSkillName` in this doc WERE DB-verified present
    2026-07-06 at their cited paths (Ainex `empusasoulcarver_spiritbolt`, Kallixenia
    `lichequeen_soulstrike`, Numberouane/Uber `barmanu_blizzard`, Kreeloo `thunderballnova`, Kaets
    `strongbark_quillvines`, Anapaest/Yerk `earthfury_ring`, Jiaco `nightstalker_shadowsurge`, Zilla
    `hero_bladetwirl2_ring`, Rainbowbright `battlestandard`, plus every `records\skills\soulskills\*`
    proc). Only augment PATHS had dangling cases, and they are all corrected in-line below.
- **Icon paths** `SVItems\jewelry\soul_{n,e,l}_icon.tex`. NOTE: the existing boilerplate
  (`_SOUL_BOILERPLATE`, `apply_svc_patches.py:1291`) hardcodes `soul_n_icon.tex` for all three tiers;
  only 3 icon files exist (n/e/l). Recommendation for these designs: per tier, set
  `bitmap = soul_n_icon.tex` (N), `soul_e_icon.tex` (E), `soul_l_icon.tex` (L) so tier reads at a
  glance. This is a one-line-per-tier override in the `stats` dict (`'bitmap': (S, ...)`) and is the
  only deviation from the current builder default any of these need.
- **Every tag must land in `Text.arc`.** New tags are authored into the root `uber_soul_tags.txt`
  (the `uber_tags_path` source of truth that `build_text_arc.py:collect_mod_authored_tags` unions
  into the manifest, gated by `tools/validate_tags.py`). Every tag named in this doc is listed in the
  consolidated tag manifest at the end (Section 9), ready to paste.
- **Drop rate** = `chanceToEquipFinger2` on the monster. `_create_soul` sets 66.0 by default when
  passed a `monster`. Keep 66% for Hero/Quest, matching every hand-crafted exemplar; the release
  drop-rate pass (`SVC_RELEASE_DROPS`) tunes later.

---

## 1. The taste standard (what Will's densest hand-crafted souls define)

Will's directive: "look at the handcrafted custom souls with the most detail that I made ... you can
see what I want." These are the souls he specified manually with the longest bespoke stat blocks,
custom pet loadouts, hand-picked skills, and custom lore. They are the depth bar for everything new.

### 1.1 The exemplars, ranked by manual density

| Soul | Fn (`apply_svc_patches.py`) | What makes it the standard | Stat-field count (per tier) |
|---|---|---|---|
| **SP Toxeus** ("THE strongest soul in the game", Tier 1) | `_create_sp_toxeus_soul:1409` | 30+ hand-set fields per tier: proc (Ring of Lightning on-hit) + 2 Dream augments (Phantom Strike, Distortion Wave; NOTE both augment CONSTANTS are dangling in the shipped code - see Section 0 - so the shipped Distortion Wave augment is currently DEAD) + a full offensive suite (phys/life/electrocution min-max, life-leech, %-current-life) + evasion (dodge, deflect, energy absorption, mana-burn) + assassin speed + 7 %-stat modifiers + reflect. Explicitly balanced because "the monster equips this soul too." itemLevel N/E/L = 33/66/**80** (the docstring says "33/66/99" but the shipped L tier is itemLevel 80, DB-verified). | **~31** |
| **Main Toxeus overhaul** (Tier 3) | `_overhaul_main_toxeus_soul:1543` | ~27 fields/tier. Bladestorm profile: massive phys + pierce + bleed + envenom (poison + total-speed slow) + speed/evasion + 6 %-mods + reflect + `racialBonusPercentDamage` vs Undead. Boosts the pre-existing soul in place (scan-and-set). | **~27** |
| **Rakanizeus** (summon, Tier-4 god-satyr) | `_create_rakanizeus_pet_skill:320` + `SOUL_OVERHAULS['rakanizeus_soul']:94` | The permanent-pet gold standard. Summons a 4500/6500/8500-HP satyr warrior with a fully hand-picked **N/E/L-tiered equipment loadout** (Om'ehns->Plissken->Eternal Darkness swords; Obsidian->Warrior's->Conqueror's armbands; Zakalwe->Adroit Loop->Mark of Ares rings), custom mesh/scale/controller/status-icons, per-level life/regen/damage arrays, plus a 14-field soul stat block (chain-lightning + storm-surge augments, run/attack/total speed, pierce). | pet: ~20 identity+stat fields; soul: **~14** |
| **Boneash** (summon, fire skeleton caster) | `_create_boneash_pet_skill:479` | Same permanent-pet depth: 3500/5000/6500-HP RevenantFire caster, staff/armband/ring loadout (Solaris->Blastos Fotia->Staff of Elysium etc.), INT 400, cast-speed 1.5, bonefiend status icons. | pet: ~20; soul: ~10 |
| **Murder Bunny** (Tier 2 uber) | `_create_murder_bunny_soul:1765` | ~22 fields/tier. Ground Smash proc + Onslaught/Lethal Strike augments + devastating phys/pierce (up to 280 max at L) + fire retaliation (his signature) + ambush speed/dodge. Level 66/79/99. | **~22** |
| **SP Hades** (Tier 2 shadow god) | `_create_sp_hades_soul:1861` | ~20 fields/tier. Blood Boil proc + Death Chill/Ternion augments + life/phys + %-current-life + life-leech + resistance-shred + dark-god %-mods + tri-elemental defense. | **~20** |
| **Leinth** (blood witch, 3 variants) | `_create_leinth_soul:1664` | Blood Boil proc + Dark Covenant/Plague augments + life/bleed + life-leech + caster %-mods + cast-speed + **her poison weakness carried onto the soul** (`defensivePoison: -8`), a signature flavor touch. Wired to all 3 Leinth records. | ~18 |
| **Dagon / Cold Worm / Neanderthal warband** | `_create_dagon_soul:1957`, `_create_coldworm_soul:1166`, `_create_neanderthal_warband_souls:2293` | Thematic, ~16-18 fields, faction sets. The warband is a **3-soul themed set** (tank / lightning-hacker / wizard) built together, the model for the Crow Heroes faction below. | ~16-18 |
| **Dev skeletons** (15 souls) | `_create_dev_skeleton_souls:2037` | Will's personal touch: 15 souls named for his friends (Arthur, Ben, Chooch, Cory, ...), each themed to that skeleton's mesh + skills via a compact `(proc, aug1, aug2, L-tier stats)` tuple, N/E auto-scaled 0.6x/0.8x. The pattern for cheaply-but-thematically finishing a big roster. | L tier hand-set, N/E scaled |

### 1.2 The rules those exemplars encode (the design grammar)

1. **Signature-first.** The single most iconic thing the boss does becomes either the granted proc
   (`itemSkillName` + `itemSkillAutoController`) or the summon. Toxeus -> his electrocuting Distortion
   Wave (as Ring of Lightning on-hit) + Phantom Strike augment. Leinth -> Blood Boil (her actual
   signature). Murder Bunny -> Ground Smash + his real fire retaliation.
2. **Two mastery augments** reinforce the fantasy (`augmentSkillName1/2` at levels ~2/3/4/5 scaling
   by tier), always real DRX mastery skills (`records\skills\<mastery>\drx*.dbr`). These let the soul
   "teach" the player the boss's build.
3. **A full offensive suite** matched to the damage type: flat min/max + a `*Modifier` %, plus the
   boss's control effect (bleed/poison/stun/slow/resistance-shred with duration).
4. **%-stat modifiers** (`characterLifeModifier`, `...ManaModifier`, `...StrengthModifier`, etc.)
   scale the soul with the character rather than flat-statting it, which is what makes the top souls
   feel build-defining.
5. **Tier scaling is monotone and roughly linear-to-1.5x** N->E->L on every field; itemLevel tracks
   the monster's own N/E/L `charLevel`; `levelRequirement = itemLevel - 5`.
6. **Flavor callbacks**: a boss's weakness or gimmick shows up on the soul (Leinth's poison
   weakness; Xiao's `characterLifeModifier: -30` glass-cannon; Calybe's `characterLife: -60`
   berserker cost). Souls are not pure power; they carry the monster's character.
7. **Summon vs skill**: iconic *monster* -> summon it (Rakanizeus, Boneash, Pharaoh Guard, and every
   base `summon_*` soul). Iconic *ability* -> grant the skill (Toxeus, Leinth, Murder Bunny). A boss
   whose whole identity is "the thing it summons/is" gets the pet; a boss defined by one devastating
   move gets the move.

Every design below is scored against this grammar and matches ~16-31 hand-set fields per tier for
headliners, ~12-18 for bulk-roster entries, with faction sets built together like the warband.

---

## 2. HEADLINERS (10) - full depth

These 10 are the marquee designs: unique bosses/heroes with no working soul, each getting a bespoke
three-tier stat block and (where a summon) a full pet loadout. Marked ★.

### 2.1 ★ Ainex, Queen of Crows (DESIGN TARGET #1)

- **Boss / record:** `records\xpack\creatures\monster\empusa\um_ainex_45.dbr` (tag `tagNewHero264`,
  "Staff"). Class Hero, race **Demon**, mesh `SVMesh\meshes\ainex.msh`, levels **45/59/71**,
  `chanceToEquipFinger2 = 100.0` already set.
- **THE GAP:** her monster record already references (DB-verified)
  `lootFinger2Item1 = [records/item/equipmentring/soul/empusa/ainex_soul_{n,e,l}.dbr]` with
  `chanceToEquipFinger2 = 100.0`, and the display tag **`tagSVCSoulAinex = {^F}Soul of Ainex` already
  exists** in `uber_soul_tags.txt`, but the three referenced soul records **do not exist anywhere in
  the built `.arz`** (audit-confirmed; my own scan found zero `ainex_soul*` records). So she drops a
  dangling reference = nothing. This is the single highest-priority soul in the mod.
- **HOW THE FIX WORKS (do not misread this):** the fix is NOT "create records at the `empusa\` path so
  the existing reference resolves." The recommended builder `_create_soul(db,'ainex',...)` writes the
  new records to `_SOUL_DIR = records\item\equipmentring\soul\svc_uber\ainex_soul_{n,e,l}.dbr` and
  **RE-POINTS** `lootFinger2Item1` on the monster to the `svc_uber\` paths
  (`apply_svc_patches.py:1348-1353`). The filename stem (`ainex_soul_{n,e,l}`) is preserved but the
  directory changes `empusa\` -> `svc_uber\`. Do NOT author the records under `empusa\`. (Confirmed the
  re-point mechanism in `_create_soul` at lines 1348-1353.)
- **Grant type: SKILL** (her signature ranged vitality bolt), with a secondary summon option noted.
  Rationale: Ainex is defined as a spectral spellcaster ("Staff", Demon, custom `ainex` hair/ambient
  FX). Her one iconic move is `empusasoulcarver_spiritbolt` (Ranged vitality Attack). Granting it as
  an on-hit proc makes the player fling her soul-carving bolts, which is cooler and more legible than
  summoning a generic empusa. Her defensive identity (very high dodge + projectile-dodge +
  elemental-resist-per-level) becomes the soul's evasion package, a rare and desirable profile.
- **Exact records to build/derive:**
  - Proc: `records\xpack\skills\monsterskills\activeattackprojectile\empusasoulcarver_spiritbolt.dbr`
    ([Skill_AttackProjectile], "Ranged vitality Attack") set as `itemSkillName`, controller
    `_AC_ON_HIT`. This is her own bolt; the reference `soulcarver_soul_*` already exists in the empusa
    folder and grants nothing similar, so this is a genuinely new grant.
  - Augment 1: `drxternion` (`records\skills\spirit\drxternion.dbr`, verified present) - triple
    vitality bolts, reinforcing the ranged-vitality caster fantasy.
  - Augment 2: `drxdeathchillaura` (`records\skills\spirit\drxdeathchillaura.dbr`, verified present) -
    crow-queen death aura.
- **Soul name + lore:** `{^F}Soul of Ainex` (tag exists). Add a description tag
  `tagSVCSoulAinexDESC = The Queen of Crows carves souls from the air with spectral bolts. Bound into
  this ring, her essence lends the bearer her uncanny evasion and the killing lance of her gaze.`
- **Stat block (Will's exemplar style; ~24 fields/tier):**

```
diff=n  itemLevel=45  levelRequirement=40   bitmap=soul_n_icon.tex
  itemSkillName            = empusasoulcarver_spiritbolt   itemSkillLevel=4   itemSkillAutoController=_AC_ON_HIT
  augmentSkillName1        = drxternion         augmentSkillLevel1=3
  augmentSkillName2        = drxdeathchillaura  augmentSkillLevel2=3
  offensiveLifeMin=45  offensiveLifeMax=70     offensiveLifeModifier=25       (vitality bolt)
  offensiveColdMin=25  offensiveColdMax=40                                    (death-chill flavor)
  offensiveLifeLeechMin=25                       offensivePercentCurrentLifeMin=4
  characterDodgePercent=14   characterDeflectProjectile=14                    (her signature evasion)
  defensiveElementalResistance=15                                            (her per-level ele resist)
  characterIntelligenceModifier=8  characterDexterityModifier=6
  characterManaModifier=10  characterLifeModifier=8  characterSpellCastSpeedModifier=18
  characterDefensiveAbilityModifier=6  defensiveLife=18
diff=e  itemLevel=59  levelRequirement=54   bitmap=soul_e_icon.tex   (all above x~1.4, skill lv 6/4/4, dodge 18/18, ele-res 20)
diff=l  itemLevel=71  levelRequirement=66   bitmap=soul_l_icon.tex   (x~1.9, skill lv 8/5/5, dodge 22/22, ele-res 25,
     offensiveLifeMin/Max 120/185, offensiveLifeModifier 55, %-mods INT 14 / mana 18 / life 16 / cast 40)
```

- **Icon:** `SVItems\jewelry\soul_{n,e,l}_icon.tex` per tier.
- **Tags:** `tagSVCSoulAinex` (exists), add `tagSVCSoulAinexDESC`.
- **Builder pattern:** `_create_soul(db, 'ainex', 'tagSVCSoulAinex', tiers, MONSTER, 66.0)` written as
  a new `_create_ainex_soul(db)` mirroring `_create_leinth_soul`. IMPORTANT: her monster currently
  points `lootFinger2Item1` at the `empusa\ainex_soul_*` path; `_create_soul` will re-point it at the
  new `svc_uber\ainex_soul_*` records and set drop 66% (drop is already 100%; 66% is the tuned target,
  leave `_create_soul`'s default). Alternatively keep her at 100% by passing `drop_rate=100.0` since
  the monster already declares 100 - designer's call; 66% recommended for parity with peers.
- **SUMMON alternative (if Will prefers a pet):** clone `empusa` pet from Lyia, mesh
  `SVMesh\meshes\ainex.msh`, race Demon, staff/armband/ring caster loadout as Boneash; proc becomes
  `summon_ainex`. Skill-grant is the recommendation for the reasons above.

### 2.2 ★ Blood Witch High Priest

- **Boss / record:** `records\drxcreatures\bloodwitch\c_disciple_miniboss.dbr` (tag `tagBWHighPriest`).
  Class Monster, **race God**, mesh `DRX\meshes\disciple.msh`, scale 2.5, levels **39/56/71**. No soul
  (NONE in the audit).
- **Grant type: SUMMON.** Rationale: his entire identity is a blood-summoner: his signature skill is
  `discipleboss_summon_melinoe` [Skill_SpawnPet] (summons a Melinoe blade-dancer synergy demon), plus
  a Shadowlink aura and blood-rain. A boss whose fantasy is "commands blood-demons" should let the
  player command one. The Melinoe blade-dancer is a far more iconic pet than any generic disciple.
- **Exact records to derive:**
  - Pet source monster: `records\drxcreatures\bloodwitch\skills\discipleboss_bladedancer.dbr` (what
    `discipleboss_summon_melinoe` spawns; a sword-armed Melinoe). Clone 3 pet records from Lyia,
    copy animations + skills from the bladedancer, mesh = the bladedancer's mesh (female PC / disciple
    blade-dancer), race God/Undead.
  - Summon skill: new `summon_bwpriest` (or `summon_melinoe`), cloned from `summon_lyia` for
    permanence; `spawnObjects` = the 3 new pet records.
  - **Equipment loadout (PINNED, Rakanizeus-depth - all 9 paths DB-verified present 2026-07-06).**
    Blood-priest blade-dancer = sword + armband + ring, blood/vitality/necro-themed, fed to
    `_set_pet_equipment(db, path, {...})` in the exact triplet shape Rakanizeus uses
    (`apply_svc_patches.py:377-402`; `chanceToEquip* = 100.0`, `chanceToEquip*Item1 = 5000`,
    `loot*Item1 = [N, E, L]`):

    ```
    _EQ = r'records\xpack\item\equipmentweapons\sword'
    _AB = r'records\item\equipmentarmband'
    _RG = r'records\item\equipmentring'
    # Sword (blade-dancer blade):  u_n_003 -> u_e_002 -> u_l_003
    'chanceToEquipLeftHand': 100.0, 'chanceToEquipLeftHandItem1': 5000,
    'lootLeftHandItem1': [ _EQ+r'\u_n_003.dbr', _EQ+r'\u_e_002.dbr', _EQ+r'\u_l_003.dbr' ],
    # Armband (necro/shadow):  Lazarus Armor -> Shadowguard -> Abyssal Armor
    'chanceToEquipForearm': 100.0, 'chanceToEquipForearmItem1': 5000,
    'lootForearmItem1': [ _AB+r'\us_n_lazarusarmor.dbr', _AB+r'\us_e_shadowguard.dbr', _AB+r'\us_l_abyssalarmor.dbr' ],
    # Ring (blood/priest):  Bloodstone -> Seal of the High Priest -> Black Pearl Ring
    'chanceToEquipFinger1': 100.0, 'chanceToEquipFinger1Item1': 5000,
    'lootFinger1Item1': [ _RG+r'\u_n_bloodstone.dbr', _RG+r'\u_e_sealofthehighpriest.dbr', _RG+r'\u_l_blackpearlring.dbr' ],
    ```
    (`u_e_sealofthehighpriest` is a literal thematic bullseye for this boss.) For the on-model blade
    VISUAL only, the disciple's own `records\drxcreatures\bloodwitch\skills\skilleffects\
    wep_bladedancersword0{1,2,3}.dbr` all exist and can be swapped in as the `lootLeftHandItem1`
    entries if the unique-sword meshes look wrong on the Melinoe rig; the unique swords above are the
    default (they carry real stats, matching the Rakanizeus philosophy).
- **Soul name + lore:** `{^F}Soul of the Blood High Priest`.
  `tagSVCSoulBWHighPriestDESC = High Priest of the Blood Witch cult, who tore living demons from the
  blood of his victims. His soul, released, calls forth a Melinoe blade-dancer to fight at your side
  until it is cut down.`
- **Pet stat spec (Rakanizeus-depth):** life `[4200, 6000, 8000]`, life_regen `[22, 40, 60]`, dmg_min
  `[55, 85, 120]`, dmg_max `[85, 130, 180]`, scale 1.4, `characterRacialProfile = God`, controller
  `controller_skelly_aggressive.dbr` (or the disciple controller), `dropItems=0`, `giveXP=0`,
  StatusIcon = a spirit/blood party icon.
- **Soul stat block (~14 fields, summon-soul shape - lighter than a skill soul since the pet is the
  payload):**

```
diff=n itemLevel=39 lr=34 bitmap=n:  itemSkillName=summon_bwpriest itemSkillLevel=1
   augmentSkillName1=drxdarkcovenant lv2   augmentSkillName2=drxdeathchillaura lv2
   characterLifeModifier=10 characterIntelligenceModifier=6 characterManaModifier=8
   offensiveLifeMin=25 offensiveLifeMax=40 offensiveLifeLeechMin=20
   defensiveLife=18 characterSpellCastSpeedModifier=14 characterManaRegenModifier=12
diff=e itemLevel=56 lr=51 bitmap=e:  itemSkillLevel=2, augments 3/3, values x1.4
diff=l itemLevel=71 lr=66 bitmap=l:  itemSkillLevel=3, augments 4/4, values x1.9
```

- **Tags:** `tagSVCSoulBWHighPriest`, `tagSVCSoulBWHighPriestDESC`, `tagSVCSummonBWHighPriest` (+DESC).
- **Builder pattern:** new `_create_bwpriest_pet_skill(db)` (clone the `_create_boneash_pet_skill`
  shape) + `_create_soul(db, 'bwpriest', 'tagSVCSoulBWHighPriest', tiers, MONSTER, 66.0)`.

### 2.3 ★ Limos Lifeeater (the STUB fix - only Table B boss lacking a functional soul)

- **Boss / record:** `records\creature\monster\limos\um_frost_36.dbr` (tag `tagMonsterName169`,
  "Uber hero"). Class **Boss**, race Demon, mesh `Creatures\Monster\Limos\Limos01.msh`, levels
  **36/54/69**, drop already 100%. Its 3 souls `limoslifeater_soul_{n,e,l}.dbr` EXIST but are pure
  STUBs (no skill, no augments, no stats).
- **Grant type: SKILL** (life-leech spell). Rationale: Limos ("famine/starvation" demon) has one
  signature: `limos_consumelife02` [Skill_AttackSpell] (Life Leech). His whole fantasy is devouring
  life. Grant a life-drain proc + a vitality/life-leech offensive suite. (No summon: the Limos body
  is a generic demon; the *hunger* is the identity.)
- **Exact records to derive:**
  - Proc: `_SS_LIFE_DRAIN` (`records\skills\spirit\lifedrain.dbr`, [Skill_AttackSpellChaos]) on-hit,
    the exact skill his soul theme demands (his `limos_consumelife02` is a self-cast spell not usable
    as an item proc; `lifedrain` is the established soul-usable life-drain, already used by
    `elephantsnatcher`/`sandwraith` souls).
  - Augment 1: `drxdarkcovenant` (`records\skills\spirit\drxdarkcovenant.dbr`) - pet/undead command
    flavor of the Limos swarm.
  - Augment 2: `drxdeathchillaura_ravagesoftime` (`records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr`,
    Class `Skill_Modifier`) - decay/aging, thematically "famine." (This is the real "ravages of time"
    record; the intuitive `_SK_RAVAGES_OF_TIME` / `drxravagesoftime` path DANGLES - see Section 0.)
- **THE FIX detail:** the 3 stub records already exist at
  `records\item\equipmentring\soul\limos\limoslifeater_soul_{n,e,l}.dbr`. Because souls must never be
  `clone_record`'d and these are already bare records, the cleanest fix is to `_set_soul_fields` the
  full stat block onto the existing three paths in place (like `_overhaul_main_toxeus_soul` does its
  scan-and-set), NOT to create new svc_uber records - this keeps the monster's existing
  `lootFinger2Item1` wiring intact.
- **Soul name + lore:** the 3 stub records currently carry `itemNameTag = tagSoulName79` (DB-verified,
  along with their existing `itemLevel = 44`); overwrite it with a proper
  `tagSVCSoulLimosLifeeater = {^F}Soul of the Lifeeater`.
  `...DESC = The Lifeeater knows only endless hunger. Its soul drains the vitality of all it touches,
  feeding the bearer on the lives of the slain.`
- **Stat block (~18 fields/tier), scaled to peer Limos souls (uber_soul at Lv45). NOTE: the stubs'
  existing `itemLevel` is 44 for all three tiers; the completion RE-SETS itemLevel per tier to track
  the monster's 36/54/69 charLevel as below:**

```
diff=n itemLevel=36 lr=31 bitmap=n:
   itemSkillName=lifedrain itemSkillLevel=3 itemSkillAutoController=_AC_ON_HIT
   augmentSkillName1=drxdarkcovenant lv2
   augmentSkillName2=drxdeathchillaura_ravagesoftime lv2   (NOT drxravagesoftime - that path dangles; see Section 0)
   offensiveLifeMin=35 offensiveLifeMax=55 offensiveLifeModifier=22
   offensiveLifeLeechMin=35 offensivePercentCurrentLifeMin=4
   offensiveTotalResistanceReductionAbsoluteMin=10 ...DurationMin=3
   characterLifeModifier=12 characterManaModifier=6 characterIntelligenceModifier=5
   defensiveLife=20 defensiveLifeLeech=25   characterLifeRegenModifier=15
diff=e itemLevel=54 lr=49 bitmap=e:  skill lv 5, augments 3/3, values x1.4
diff=l itemLevel=69 lr=64 bitmap=l:  skill lv 7, augments 4/4, values x1.9 (lifeMin/Max 95/150, leech 65)
```

- **Tags:** `tagSVCSoulLimosLifeeater` (+DESC).
- **Builder pattern:** new `_fix_limos_lifeeater_stub(db)` doing a scan-and-set over the 3 existing
  `limoslifeater_soul_*` records (mirror `_overhaul_main_toxeus_soul:1543`).

### 2.4 ★ Kallixenia (D2 NPC "Akara") - the Lich Queen

- **Boss / record:** `records\drxcreatures\xurder\d2npc\01_akara.dbr` (tag `tagD2NPCakara`,
  "Kallixenia -- staff - Spirit-based powers -- Death Effect: LichQueenNPCXform"). Race Magical, mesh
  `XPack\Creatures\npc\hades\hadpersephone.msh`, levels **36/54/69**. No soul.
- **Grant type: SKILL** (soul-orb rain). Rationale: she is a full lich-queen caster with a spectacular
  signature: `lichequeen_soulstrike` [Skill_DropProjectileTelekinesis] ("Soul Orbs from the sky which
  life leech"), plus `hero_lifedrain`, Circle of Decay, and a short-range spirit wave. Raining
  life-leeching soul orbs is far cooler as a player skill than summoning her. She anchors the D2 NPC
  trio (2.9, 2.10) as the caster of the three.
- **Exact records to derive:**
  - Proc: `records\skills\soulskills\lichequeen_soulstrike.dbr` [Skill_DropProjectileTelekinesis]
    (verified present in soulskills), controller **`_AC_ON_HIT`** (= `base_atself_onanyhit.dbr`). Use
    `_AC_ON_HIT`, NOT `_AC_ON_ATTACK`: the shipped `uber_soul` grants the identical-Class
    `barmanu_blizzard` [Skill_DropProjectileTelekinesis] with `_AC_ON_HIT`, so that is the
    battle-tested controller for a soul-cast sky-drop of this Class.
  - Augment 1: `drxdeathchillaura` (`records\skills\spirit\drxdeathchillaura.dbr`) - her cold+life
    circle of decay.
  - Augment 2: `drxternion` (`records\skills\spirit\drxternion.dbr`) - spirit-bolt caster identity.
- **Soul name + lore:** `{^F}Soul of Kallixenia`.
  `tagSVCSoulKallixeniaDESC = Kallixenia, the Lich Queen, rained soul-orbs from a poisoned sky. Her
  soul answers the call, drawing down a storm of life-stealing spirits upon the bearer's foes.`
- **Stat block (~20 fields/tier, caster profile):**

```
diff=n itemLevel=36 lr=31 bitmap=n:
   itemSkillName=lichequeen_soulstrike itemSkillLevel=3 itemSkillAutoController=_AC_ON_HIT   (match shipped uber_soul's DropProjectileTelekinesis pattern)
   augmentSkillName1=drxdeathchillaura lv2  augmentSkillName2=drxternion lv2
   offensiveLifeMin=40 offensiveLifeMax=62 offensiveLifeModifier=25
   offensiveColdMin=25 offensiveColdMax=40 offensiveLifeLeechMin=30
   characterIntelligenceModifier=8 characterManaModifier=12 characterLifeModifier=8
   characterSpellCastSpeedModifier=20 characterManaRegenModifier=15
   defensiveLife=20 defensiveCold=12 defensiveManaBurnRatio=20
diff=e itemLevel=54 lr=49 bitmap=e:  skill lv 5, augments 3/3, values x1.4, cast 32
diff=l itemLevel=69 lr=64 bitmap=l:  skill lv 7, augments 4/4, values x1.9, cast 46 (lifeMin/Max 105/165)
```

- **Tags:** `tagSVCSoulKallixenia` (+DESC).
- **Builder pattern:** `_create_soul(db, 'kallixenia', 'tagSVCSoulKallixenia', tiers, MONSTER, 66.0)`.

### 2.5 ★ Lil'Lued the Elder Djinn (Crow Heroes - "Big Lued")

- **Boss / record:** `records\drxcreatures\crowheroes\lillued_big.dbr` (tag `tagUrderBigLued`, "Hero -
  Blood Pact (Aura) / Djinn Blast / Elemental Chaos / Haste Aura"). Race Demon, mesh
  `Creatures\Monster\Djinn\ElderDjinn01.msh`, scale 2.7, levels **40/57/71**. No soul. The most
  visually striking Crow Hero (a giant Elder Djinn).
- **Grant type: SUMMON.** Rationale: an Elder Djinn is one of TQ's most desirable pet fantasies, and
  Lil'Lued's kit is aura+blast support (Blood Pact aura, Storm Nimbus, ranged life blast, +speed
  aura) - a perfect summonable ally that buffs the party while blasting. Summoning a towering djinn is
  cooler than granting one more lightning bolt.
- **Exact records to derive:**
  - Pet source monster: `lillued_big.dbr` itself (copy its animations + skills:
    `djinn_stormnimbus`, `djinn_rangedblast`, `bloodpact`, `character_speedall`). Clone pet from Lyia,
    mesh `Creatures\Monster\Djinn\ElderDjinn01.msh`, scale 2.7, race Demon.
  - Summon skill: `summon_lillued` cloned from `summon_lyia`.
  - **Equipment loadout (PINNED, Rakanizeus/Boneash-depth - all 9 paths DB-verified present
    2026-07-06).** Elder Djinn = storm caster, so copy the **Boneash staff loadout convention exactly**
    (`_create_boneash_pet_skill`, `apply_svc_patches.py:531-561`): a staff goes in the **`LeftHand`**
    slot, the staff dir is the SINGULAR `records\item\equipmentweapon\staff` (not `xpack\...\weapons`),
    and casters wear the `usm_*` caster armbands. Storm-themed picks:

    ```
    _ST = r'records\item\equipmentweapon\staff'
    _AB = r'records\item\equipmentarmband'
    _RG = r'records\item\equipmentring'
    # Staff (LeftHand, storm/lightning caster):  Fulminator -> Ilektrismos -> Morosnyx
    'chanceToEquipLeftHand': 100.0, 'chanceToEquipLeftHandItem1': 5000,
    'lootLeftHandItem1': [ _ST+r'\u_n_fulminator.dbr', _ST+r'\u_e_ilektrismos.dbr', _ST+r'\u_l_morosnyx.dbr' ],
    # Caster armband (storm):  Ronzer's Gift -> Raiment of the Storm -> Archmage's Regalia
    'chanceToEquipForearm': 100.0, 'chanceToEquipForearmItem1': 5000,
    'lootForearmItem1': [ _AB+r"\usm_n_ronzer'sgift.dbr", _AB+r'\usm_e_raimentofthestorm.dbr', _AB+r"\usm_l_archmage'sregalia.dbr" ],
    # Ring (storm):  Storm Eye -> Celestial Band -> Apollo's Will
    'chanceToEquipFinger1': 100.0, 'chanceToEquipFinger1Item1': 5000,
    'lootFinger1Item1': [ _RG+r'\u_n_stormeye.dbr', _RG+r'\u_e_celestialband.dbr', _RG+r"\u_l_apollo'swill.dbr" ],
    ```
    (`u_e_ilektrismos` [electricity], `usm_e_raimentofthestorm`, and `u_n_stormeye` are storm-thematic
    bullseyes; `usm_l` has only one option, `archmage'sregalia`.) If the ElderDjinn01 rig cannot hold a
    staff visually (djinn use innate `handHitDamage`), drop the staff triplet and keep armband + ring
    only (Boneash still equips its staff fine, so this is unlikely), but prefer the full 3-slot loadout
    to match the depth bar.
- **Soul name + lore:** `{^F}Soul of Lil'Lued the Elder Djinn`.
  `tagSVCSoulLilLuedDESC = Bound in a crow-cursed lamp, the Elder Djinn Lil'Lued rages against its
  imprisonment. Freed by the soul, it fights beside you wreathed in storm and blood-pact, hastening
  your step and blasting your enemies.`
- **Pet stat spec:** life `[4800, 6800, 9000]` (big djinn), regen `[25, 45, 65]`, dmg `[50/80, 75/120,
  105/165]`, scale 2.7, race Demon, cast-speed 1.4, StatusIcon = a storm/djinn party icon.
- **Soul stat block (~13 summon-soul fields):** augments `drxstormnimbus` + `drxsquall`, lightning
  offensive (`offensiveLightningMin/Max`), `characterTotalSpeedModifier` (his haste aura flavor),
  `characterLifeModifier`, `characterIntelligenceModifier`, `defensiveLightning`. N/E/L skill lv 1/2/3.
- **Tags:** `tagSVCSoulLilLued`, `...DESC`, `tagSVCSummonLilLued` (+DESC).
- **Builder pattern:** `_create_lillued_pet_skill(db)` (Boneash shape) + `_create_soul`.

### 2.6 ★ Zilla the Blade Dancer (Crow Heroes)

- **Boss / record:** `records\drxcreatures\crowheroes\zilla.dbr` (tag `tagUrderZilla`, "DW Swords").
  Race Demon, mesh `DRX\meshes\crowheroes\zilla.msh`, levels **45/60/73**. No soul. A signature Crow
  Hero (custom mesh + custom Zilla freeze passive + Frenzy aura).
- **Grant type: SKILL** (dual-blade freezing whirlwind). Rationale: Zilla is a dual-wield blade
  spinner whose signature is `hero_bladetwirl1/2_ring` [Skill_AttackProjectileRing] plus
  `zilla_freezepassive` (freeze-on-hit) and a Frenzy aura. Granting a spinning blade-ring that freezes
  is a spectacular, build-defining melee proc; a summon would just be a generic swordsman.
- **Exact records to derive:**
  - Proc: `hero_bladetwirl2_ring` at the DB-verified path
    `records\xpack\skills\monsterskills\activeattackradius\hero_bladetwirl2_ring.dbr` (Class
    `Skill_AttackProjectileRing`; `hero_bladetwirl1_ring` sits beside it) as on-attack proc. This IS
    his real blade whirl and it resolves. Fallback only if in-game testing shows it is not
    item-castable: `records\skills\soulskills\arachne_venomspray.dbr`-style ring.
  - Augment 1: `drxdualweapontraining` (`records\skills\warfare\drxdualweapontraining.dbr`).
  - Augment 2: `drxonslaught` (`records\skills\warfare\drxonslaught.dbr`) - his onslaught charged
    attack.
  - Cold flavor: add `offensiveColdMin/Max` + `offensiveFreeze*` (his freeze passive) to the stat
    block rather than a second cold augment, to keep it a warfare soul.
- **Soul name + lore:** `{^F}Soul of Zilla the Blade Dancer`.
  `tagSVCSoulZillaDESC = Zilla dances between two frost-forged blades, freezing all he cuts. His soul
  grants the whirling blade-storm and the killing cold of the Crow assassins.`
- **Stat block (~22 warfare/cold fields/tier):**

```
diff=n itemLevel=45 lr=40 bitmap=n:
   itemSkillName=<zilla bladetwirl ring> itemSkillLevel=4 itemSkillAutoController=_AC_ON_ATTACK
   augmentSkillName1=drxdualweapontraining lv3  augmentSkillName2=drxonslaught lv3
   offensivePhysicalMin=55 offensivePhysicalMax=80 offensivePhysicalModifier=30
   offensiveColdMin=30 offensiveColdMax=48   offensiveFreezeMin=0.5 offensiveFreezeMax=1.5 offensiveFreezeChance=15
   offensivePierceRatioModifier=15
   characterAttackSpeedModifier=14 characterTotalSpeedModifier=10 characterDodgePercent=10
   characterStrengthModifier=6 characterDexterityModifier=8 characterOffensiveAbilityModifier=6
   characterLifeModifier=10 defensiveCold=15
diff=e itemLevel=60 lr=55 bitmap=e:  skill lv 6, augments 4/4, values x1.4, freezeChance 18
diff=l itemLevel=73 lr=68 bitmap=l:  skill lv 8, augments 5/5, values x1.9, freezeChance 22 (phys 120/160)
```

- **Tags:** `tagSVCSoulZilla` (+DESC).
- **Builder pattern:** `_create_soul(db, 'zilla', 'tagSVCSoulZilla', tiers, MONSTER, 66.0)`.

### 2.7 ★ Numberouane the Frost King (Crow Heroes)

- **Boss / record:** `records\drxcreatures\crowheroes\numberouane.dbr` (tag `tagUrderNumberouane`,
  "DW Swords"). Race Undead, mesh `Creatures\pc\male\malepc01.msh`, levels **45/60/73**. No soul.
  Signature: `numberouane_skill_blizzard` [Skill_DropProjectileTelekinesis] "Frost Storm" +
  `numberouane_freezingbreath` + zilla freeze passive. A festive frost-themed hero ("HoHoHo" sound).
- **Grant type: SKILL** (blizzard). Rationale: his identity is a walking blizzard: dropping a frost
  storm from the sky is his one iconic move and reads beautifully as a soul proc (like Barmanu's
  blizzard soul, an established pattern). Cold caster/hybrid.
- **Exact records to derive:**
  - Proc: `barmanu_blizzard` (`records\skills\soulskills\barmanu_blizzard.dbr`,
    [Skill_DropProjectileTelekinesis], verified) as the soul-usable frost-storm (his own
    `numberouane_skill_blizzard` is a monster skill; `barmanu_blizzard` is the established
    soul-usable frost storm, already granted by the Barmanu and Uber souls). Controller **`_AC_ON_HIT`**
    (= `base_atself_onanyhit.dbr`) - NOT `_AC_ON_ATTACK`: the shipped `uber_soul` grants this exact
    record with `_AC_ON_HIT`, the proven pattern for this Class.
  - Augment 1: `drxcoldaura` (`records\skills\storm\drxcoldaura.dbr`).
  - Augment 2: `drxsquall` (`records\skills\storm\drxsquall.dbr`).
- **Soul name + lore:** `{^F}Soul of Numberouane`.
  `tagSVCSoulNumberouaneDESC = The Frost King of the Crow court buries his foes beneath endless
  blizzards. His soul calls down the frost-storm and armors the bearer against the cold he commands.`
- **Stat block (~18 cold fields/tier):** blizzard proc + cold-aura/squall augments, `offensiveColdMin/
  Max`, `offensiveSlowColdMin`+duration (his freezing breath slow), `characterColdModifier` style via
  `offensiveColdModifier`, `defensiveCold` high, `characterLifeModifier`, plus a little physical (DW
  swords) `offensivePhysicalMin/Max`. Scale 45/60/73 like Zilla.
- **Tags:** `tagSVCSoulNumberouane` (+DESC).
- **Builder pattern:** `_create_soul(db, 'numberouane', 'tagSVCSoulNumberouane', tiers, MONSTER, 66.0)`.

### 2.8 ★ Kreeloo the Telkine Ghost (Crow Heroes)

- **Boss / record:** `records\drxcreatures\crowheroes\kreeloo.dbr` (tag `tagUrderKreeloo`). Class
  **Megalesios** (a real telkine boss class!), race **Telkine**, mesh
  `Creatures\monster\telkine\telkineghost01.msh`, levels **21/44/60**. No soul. The richest kit of any
  Crow Hero: full Megalesios telkine skillset (summon Limos, spectral chaos blast, thunderball,
  mind-control blast, ranged energy blast).
- **Grant type: SKILL** (spectral chaos blast / thunderball). Rationale: Kreeloo is a telkine - a
  chaos-lightning god-caster. His `megalesios_thunderball` and `megalesios_spectralblast` are iconic.
  There is already a `thunderballnova` soul proc (used by the Megalesios boss soul), making him a
  natural chaos-caster soul. A summon would be redundant with his own summon-Limos gimmick.
- **Exact records to derive:**
  - Proc: `records\skills\soulskills\thunderballnova.dbr` [Skill_AttackProjectileRing] (the
    established telkine thunderball nova, granted by `megalesios_soul_*`), controller `_AC_ON_HIT`.
  - Augment 1: `drxlightningbolt_chainlightning` (`records\skills\storm\drxlightningbolt_chainlightning.dbr`,
    Class `SkillSecondary_ChainLightning`) - chain lightning. (NOT `drxchainlightning` - that path
    DANGLES; see Section 0.)
  - Augment 2: `drxstormnimbus` (`records\skills\storm\drxstormnimbus.dbr`) - telkine storm aura.
- **Soul name + lore:** `{^F}Soul of Kreeloo the Telkine`.
  `tagSVCSoulKreelooDESC = Kreeloo, ghost of a fallen Telkine, still crackles with the chaos-lightning
  of the god-kings. His soul looses spectral thunderballs and wraps the bearer in a telkine's storm.`
- **Stat block (~20 lightning-caster fields/tier), scaled to his low-to-mid levels 21/44/60:**

```
diff=n itemLevel=21 lr=16 bitmap=n:
   itemSkillName=thunderballnova itemSkillLevel=3 itemSkillAutoController=_AC_ON_HIT
   augmentSkillName1=drxlightningbolt_chainlightning lv2   (NOT drxchainlightning - dangles; Section 0)
   augmentSkillName2=drxstormnimbus lv2
   offensiveLightningMin=25 offensiveLightningMax=45 offensiveLightningModifier=25
   offensiveLifeMin=12 offensiveLifeMax=20   (his life energy blast)
   characterIntelligenceModifier=6 characterManaModifier=8 characterLifeModifier=6
   characterSpellCastSpeedModifier=14  defensiveLightning=15 defensiveLife=12
diff=e itemLevel=44 lr=39 bitmap=e:  skill lv 5, augments 3/3, values x1.5, cast 22
diff=l itemLevel=60 lr=55 bitmap=l:  skill lv 7, augments 4/3, values x2.2 (lightning 70/120), cast 30
```

- **Tags:** `tagSVCSoulKreeloo` (+DESC).
- **Builder pattern:** `_create_soul(db, 'kreeloo', 'tagSVCSoulKreeloo', tiers, MONSTER, 66.0)`.

### 2.9 ★ Kaets the Ascacophus (Crow Heroes) - plant summoner

- **Boss / record:** `records\drxcreatures\crowheroes\kaets.dbr` (tag `tagUrderKaets`). Race **Plant**,
  mesh `XPack\Creatures\Monster\Ascacophus\Ascacophus02.msh`, scale 1.8, levels **44/60/73**. No soul.
  Signature: `hero_quillvines` [Skill_SpawnPet] (summons quill-vines) + stump-stomp + bleed immunity.
- **Grant type: SUMMON.** Rationale: Kaets is literally a summoner - `hero_quillvines` spawns a squad
  of quill-vine plants. A plant that summons more plants is a delightful, distinctive pet fantasy
  (nature/plant summoner build), and the summon target already exists.
- **Exact records to derive:**
  - Summon: reuse `records\skills\soulskills\strongbark_quillvines.dbr` [Skill_SpawnPet, verified] as
    `itemSkillName` directly (a soul-usable quill-vine summon). **Grant it as a player-activated item
    skill with NO autocast controller** (leave `itemSkillAutoController` unset / empty) - this is the
    proven soul-summon pattern: the shipped `chimera_soul_*` and `hydra_soul_*` set
    `itemSkillName = summon_chimera / summon_hydra` with **no `itemSkillAutoController` at all**
    (DB-verified: controller = None). Do NOT use `_AC_ON_EQUIP` for a summon (autocast-on-equip of a
    SpawnPet is not the established pattern and risks odd re-summon behavior). Given quill-vines are a
    swarm, this avoids a bespoke pet build entirely.
  - Augment 1: `drxplague` (`records\skills\nature\drxplague.dbr`) - poison-plant theme.
  - Augment 2: `drxheartofoak` (`records\skills\nature\drxheartofoak.dbr`) - plant vitality.
- **Soul name + lore:** `{^F}Soul of Kaets the Thornheart`.
  `tagSVCSoulKaetsDESC = Kaets, the walking thornwood of the Crow court, seeds the earth with living
  quill-vines. Its soul lets the bearer raise a thicket of thrashing thorns to rend the enemy.`
- **Stat block (~16 nature-summoner fields/tier):** `itemSkillName = strongbark_quillvines`
  (itemSkillLevel 3/4/6), plague+heart-of-oak augments, `offensivePoisonMin/Max`+duration,
  `offensivePhysicalMin/Max` (stump stomp), `characterLifeModifier` high, `characterLifeRegenModifier`,
  `defensiveBleeding` (his bleed immunity), `defensivePoison`. Scale 44/60/73.
- **Tags:** `tagSVCSoulKaets` (+DESC).
- **Builder pattern:** `_create_soul(db, 'kaets', 'tagSVCSoulKaets', tiers, MONSTER, 66.0)` (skill
  soul; the summon is an existing soulskill so no pet build needed).

### 2.10 ★ Anapaest the Dishonor Guard (DRX Dishonor Guard boss)

- **Boss / record:** `records\drxcreatures\drxdishonorguard\anapaest_45.dbr` (tag `tagAnapaestNAME`,
  "1H + Shield"). Race Animal, mesh `DRX\meshes\anapaest.msh`, scale 2.8, levels **51/64/75** (highest
  non-uber levels in the design set). No soul. Signature: `gigantes_groundbreaker` [Skill_AttackWave]
  + `gigantes_kineticblast` [Skill_AttackRadius] + `gigantes_healthregenaura` - a towering gigantes
  tank with earth-shattering waves.
- **Grant type: SKILL** (ground-breaker wave). Rationale: Anapaest is a huge (scale 2.8) gigantes
  bruiser whose signature is smashing the ground. A ground-breaking shockwave + a regen aura augment
  makes a satisfying tank/warfare soul at the top of the level curve. (A summon would need a bespoke
  giant pet; the wave IS the boss.)
- **Exact records to derive:**
  - Proc: `earthfury_ring` (`records\skills\soulskills\earthfury_ring.dbr`, [Skill_AttackRadius], the
    soul-usable ground blast) as the ground-breaker proc, controller `_AC_ON_ATTACK` - OR
    `cyclops_groundsmash` for a heavier single hit. Prefer `earthfury_ring` for the AoE-wave flavor.
  - Augment 1: `drxonslaught` (`records\skills\warfare\drxonslaught.dbr`) - his charged melee
    escalation.
  - Augment 2: `drxwarhorn` (`records\skills\warfare\drxwarhorn.dbr`) or `drxbattlerage`
    (`records\skills\warfare\drxbattlerage.dbr`) - the regen/rally-aura flavor of his health-regen
    aura.
- **Soul name + lore:** `{^F}Soul of Anapaest the Dishonored`.
  `tagSVCSoulAnapaestDESC = Anapaest, a gigantes cast out for dishonor, shatters the earth with every
  blow. His soul grants the ground-breaking wave and the tireless regeneration of the giant-kind.`
- **Stat block (~22 tank/warfare fields/tier), scaled to Lv 51/64/75:**

```
diff=n itemLevel=51 lr=46 bitmap=n:
   itemSkillName=earthfury_ring itemSkillLevel=4 itemSkillAutoController=_AC_ON_ATTACK
   augmentSkillName1=drxonslaught lv3  augmentSkillName2=drxwarhorn lv3
   offensivePhysicalMin=70 offensivePhysicalMax=100 offensivePhysicalModifier=35
   offensiveSlowTotalSpeedMin=15 ...DurationMin=3   (ground-shake slow)
   characterStrengthModifier=8 characterLifeModifier=14 characterLifeRegen=6 characterLifeRegenModifier=20
   defensivePhysical=15 defensiveProtectionModifier=10 defensiveSlowLifeLeach=... (regen tank)
   characterOffensiveAbilityModifier=6 characterConstitutionModifier=... (life focus)
diff=e itemLevel=64 lr=59 bitmap=e:  skill lv 6, augments 4/4, values x1.4
diff=l itemLevel=75 lr=70 bitmap=l:  skill lv 8, augments 5/5, values x1.9 (phys 150/210, regen 12)
```

- **Tags:** `tagSVCSoulAnapaest` (+DESC).
- **Builder pattern:** `_create_soul(db, 'anapaest', 'tagSVCSoulAnapaest', tiers, MONSTER, 66.0)`.

---

## 3. The Crow Heroes faction (remaining) - a themed set

The Crow Heroes (`records\drxcreatures\crowheroes\`) are the "Urder" crow-court gauntlet. **Five** are
headliners above (Lil'Lued 2.5, Zilla 2.6, Numberouane 2.7, Kreeloo 2.8, Kaets 2.9). Of the remaining
9, the **five marquee members** (Gorgus, Jiaco, Yerk, Jabarto, Rainbowbright) get **full three-tier
stat blocks** in Section 3.1 below (promoted from recipe rows per the depth directive); the four
novelties (Less, Nomnom, Gitar3, Kir4, and the Lv8 child) stay at recipe-row depth because they are
low-level/joke souls. All are built together like the Neanderthal warband
(`_create_neanderthal_warband_souls`), Quest class, drop 66%, per-tier `bitmap` n/e/l, `_create_soul`.

The table below is the at-a-glance roster (grant + signature source records + name); the marquee five
then get full numeric blocks in 3.1.

| Boss / record | Tag | Levels | Grant | Signature source records | Soul name |
|---|---|---|---|---|---|
| **Gorgus** `crowheroes\gorgus.dbr` | `tagUrderGorgus` | 45/60/73 | SKILL (blade whirl + frenzy) | proc: `records\xpack\skills\monsterskills\activeattackradius\hero_bladetwirl2_ring.dbr` (verified; same as Zilla 2.6) on-attack; aug: `drxdualweapontraining` (`records\skills\warfare\`), `drxonslaught` (`records\skills\warfare\`). Beastman DW twin of Zilla | `{^F}Soul of Gorgus` |
| **Jiaco** `crowheroes\jiaco.dbr` | `tagJiaco` | 40/57/71 | SKILL (shadow surge + teleport strike) | proc: `nightstalker_shadowsurge` (soulskill exists) on-hit; aug: `drxlethalstrike`, `drxphantomstrike` (his `jiaco_skill_shadowstrike` is a teleport). Demon ninja | `{^F}Soul of Jiaco the Nightstalker` |
| **Yerk** `crowheroes\yerk.dbr` | `tagYerk` | 41/57/71 | SKILL (sleep + ground pound) | proc: `earthfury_ring` (ground pound) on-attack; aug: `drxbattlerage`, `drxconcussiveblow`. Add `offensiveSleepMin`+dur (his `yerk_skill_sleep` chain-sleep). Magical club-brute | `{^F}Soul of Yerk` |
| **Jabarto** `crowheroes\jabarto.dbr` | `tagUrderJabarto` | 18/42/58 | SKILL (storm-nimbus + spellbreak) | proc: `ringoflightning` on-hit; aug: `drxstormnimbus` (`records\skills\storm\drxstormnimbus.dbr`), `drxlightningbolt_chainlightning` (`records\skills\storm\drxlightningbolt_chainlightning.dbr` - NOT `drxchainlightning`, which dangles; Section 0). Add `offensiveLightningMin/Max`. Boarman storm-caster | `{^F}Soul of Jabarto` |
| **Rainbowbright** `crowheroes\rainbowbright.dbr` | `xtagMonsterFormicidHero03` | 46/61/74 | SUMMON (battle standard) | `records\skills\warfare\battlestandard.dbr` [Skill_SpawnPet, verified] - grant it directly as `itemSkillName` (like Kaets/quillvines). NOTE this is the GENERIC warfare Battle Standard, not a Rainbowbright-bespoke record (his own monster skill list points at it); acceptable because a rally-standard is exactly his fantasy, but if a unique standard is wanted, clone it to `svc_uber` and reskin. Insectoid axe+shield rally-captain. aug: `drxbattlerage` (`records\skills\warfare\drxbattlerage.dbr`), `drxwarhorn` (`records\skills\warfare\drxwarhorn.dbr`) | `{^F}Soul of Rainbowbright the Standard-Bearer` |
| **Less** `crowheroes\less.dbr` | `tagUrderLess` | 10/37/54 | SKILL (spell-shock igloo burst) | proc: `drxspellbreaker_spellshock` (his "IGLOO" ice burst) on-hit; aug: `drxringofflame`, `drxdeathchillaura`. Beast; low-level entry soul (scale from Lv10) | `{^F}Soul of Less` |
| **Nomnom** `crowheroes\nomnom.dbr` | `tagMonsterName171` | 13/39/56 | SKILL (plague bite) | proc: `poisonorbs` or `arachne_venomspray` on-attack; aug: `drxenvenomweapon`, `drxplague`. "Plague Feast" beast; poison-bite theme (`attackmelee_dot_poisonbite_01`) | `{^F}Soul of Nomnom` |
| **Gitar3** `crowheroes\gitar3.dbr` | `tagGitar3` | 1 | SKILL (reflect shrine aura) | Device (a rock-shrine turret!), Lv1 only. proc: `records\skills\soulskills\ringoflightning.dbr` (its `gitar3_skill` on-hit radius); aug: `records\skills\storm\drxenergyshield.dbr` (NOT `drxenergyarmor`, which dangles). A novelty low-level soul; reflect-themed (`gitar3_reflectpassive`) via `defensiveReflect` | `{^F}Soul of the Gitar Shrine` |
| **Kir4** `crowheroes\kir4.dbr` | `tagUrderKir4` | 20 | SKILL (bolt trap burst) | Device (a tiki crossbow trap), Lv20 only. proc: a projectile-burst (`manticore_quills`-style); aug: `drxstudyprey`, `drxcalculatedstrike`. Trap-hunter theme, pierce/ranged | `{^F}Soul of the Kir Trap` |
| **Lil'Lued (child)** `crowheroes\lillued.dbr` | `tagLilLued` | 8 | SKILL (minimal - novelty) | "Standing Child" Lv8, 1 skill only. A joke/novelty soul; give a tiny flat stat block + `oma_killskill`-flavor. LOW priority; can be a stat-only curiosity or skipped. Note: distinct from `lillued_big` (2.5) which shares no tag. | `{^F}Soul of Little Lued` |

### 3.1 Marquee Crow Heroes - full three-tier stat blocks

Promoted to headliner-adjacent depth (~16-20 fields/tier) per the "match that depth for every design"
directive. Every proc/augment path here is DB-verified (2026-07-06). Levels track each monster's
own N/E/L `charLevel`; `levelRequirement = itemLevel - 5`; per-tier `bitmap` n/e/l.

**Gorgus** (`tagUrderGorgus`, Beastman DW blade-twin of Zilla, Lv 45/60/73). Grant: SKILL, his blade
whirl. Cold/warfare like Zilla but a touch more raw-physical (beastman brute):

```
diff=n itemLevel=45 lr=40 bitmap=n:
   itemSkillName=records\xpack\skills\monsterskills\activeattackradius\hero_bladetwirl2_ring.dbr
     itemSkillLevel=4 itemSkillAutoController=_AC_ON_ATTACK
   augmentSkillName1=records\skills\warfare\drxdualweapontraining.dbr augmentSkillLevel1=3
   augmentSkillName2=records\skills\warfare\drxonslaught.dbr          augmentSkillLevel2=3
   offensivePhysicalMin=60 offensivePhysicalMax=88 offensivePhysicalModifier=32
   offensiveColdMin=22 offensiveColdMax=36
   offensivePierceRatioModifier=15
   characterAttackSpeedModifier=14 characterTotalSpeedModifier=8 characterDodgePercent=10
   characterStrengthModifier=8 characterDexterityModifier=6 characterOffensiveAbilityModifier=6
   characterLifeModifier=10 defensivePhysical=14
diff=e itemLevel=60 lr=55 bitmap=e:  skill lv6, augments 4/4, values x1.4
diff=l itemLevel=73 lr=68 bitmap=l:  skill lv8, augments 5/5, values x1.9 (phys 130/168)
```

**Jiaco the Nightstalker** (`tagJiaco`, Demon ninja, Lv 40/57/71). Grant: SKILL, his shadow surge.
Assassin/dream evasion profile (his `jiaco_skill_shadowstrike` is a teleport, so Phantom Strike is the
perfect augment):

```
diff=n itemLevel=40 lr=35 bitmap=n:
   itemSkillName=records\skills\soulskills\nightstalker_shadowsurge.dbr  (Class Skill_AttackRadius)
     itemSkillLevel=4 itemSkillAutoController=_AC_ON_ATTACK
   augmentSkillName1=records\skills\stealth\drxlethalstrike.dbr        augmentSkillLevel1=3
   augmentSkillName2=records\xpack\skills\dream\drxphantomstrike.dbr   augmentSkillLevel2=3
   offensivePhysicalMin=48 offensivePhysicalMax=72 offensivePhysicalModifier=28
   offensivePierceMin=28 offensivePierceMax=45 offensivePierceRatioModifier=18
   offensiveLifeLeechMin=20
   characterAttackSpeedModifier=16 characterRunSpeedModifier=10 characterDodgePercent=14 characterDeflectProjectile=12
   characterDexterityModifier=8 characterOffensiveAbilityModifier=8 characterLifeModifier=8
diff=e itemLevel=57 lr=52 bitmap=e:  skill lv6, augments 4/4, values x1.4, dodge 18
diff=l itemLevel=71 lr=66 bitmap=l:  skill lv8, augments 5/5, values x1.9, dodge 22 (phys 110/150, pierce 55/85)
```

**Yerk** (`tagYerk`, Magical club-brute, Lv 41/57/71). Grant: SKILL, his ground pound + chain-sleep
signature:

```
diff=n itemLevel=41 lr=36 bitmap=n:
   itemSkillName=records\skills\soulskills\earthfury_ring.dbr  (Class Skill_AttackRadius)
     itemSkillLevel=4 itemSkillAutoController=_AC_ON_ATTACK
   augmentSkillName1=records\skills\warfare\drxbattlerage.dbr       augmentSkillLevel1=3
   augmentSkillName2=records\skills\defensive\drxconcussiveblow.dbr augmentSkillLevel2=3
   offensivePhysicalMin=62 offensivePhysicalMax=92 offensivePhysicalModifier=34
   offensiveStunMin=1.0 offensiveStunMax=2.0        (club concussion)
   offensiveSleepMin=1.5 offensiveSleepMax=2.5      (his yerk_skill_sleep chain-sleep - signature)
   characterStrengthModifier=8 characterLifeModifier=12 characterConstitutionModifier=6
   characterOffensiveAbilityModifier=6 defensivePhysical=15 defensiveProtectionModifier=8
diff=e itemLevel=57 lr=52 bitmap=e:  skill lv6, augments 4/4, values x1.4, sleep 2.0/3.0
diff=l itemLevel=71 lr=66 bitmap=l:  skill lv8, augments 5/5, values x1.9, sleep 2.5/3.5 (phys 130/175)
```

**Jabarto** (`tagUrderJabarto`, Boarman storm-caster, Lv 18/42/58). Grant: SKILL, storm nimbus +
chain lightning. Lightning-caster, scaled from the low Lv18 N tier:

```
diff=n itemLevel=18 lr=13 bitmap=n:
   itemSkillName=records\skills\soulskills\ringoflightning.dbr  (Class Skill_BuffAttackRadiusToggled)
     itemSkillLevel=3 itemSkillAutoController=_AC_ON_HIT
   augmentSkillName1=records\skills\storm\drxstormnimbus.dbr                 augmentSkillLevel1=2
   augmentSkillName2=records\skills\storm\drxlightningbolt_chainlightning.dbr augmentSkillLevel2=2
     (NOT drxchainlightning - dangles; Section 0)
   offensiveLightningMin=20 offensiveLightningMax=40 offensiveLightningModifier=22
   characterIntelligenceModifier=6 characterManaModifier=8 characterLifeModifier=6
   characterSpellCastSpeedModifier=14 defensiveLightning=15
diff=e itemLevel=42 lr=37 bitmap=e:  skill lv5, augments 3/3, values x1.5, cast 22
diff=l itemLevel=58 lr=53 bitmap=l:  skill lv7, augments 4/4, values x2.2 (lightning 55/100), cast 30
```

**Rainbowbright the Standard-Bearer** (`xtagMonsterFormicidHero03`, Insectoid axe+shield rally-captain,
Lv 46/61/74). Grant: SUMMON (Battle Standard). Summon-soul shape (the standard is the payload); NO
autocast controller (activated item skill, like `chimera_soul`/`hydra_soul` which set no
`itemSkillAutoController`):

```
diff=n itemLevel=46 lr=41 bitmap=n:
   itemSkillName=records\skills\warfare\battlestandard.dbr  (Class Skill_SpawnPet; NO autocast controller)
     itemSkillLevel=1
   augmentSkillName1=records\skills\warfare\drxbattlerage.dbr augmentSkillLevel1=2
   augmentSkillName2=records\skills\defensive\drxrally.dbr    augmentSkillLevel2=2   (real rally aura - his captain fantasy)
   offensivePhysicalMin=30 offensivePhysicalMax=48 offensivePhysicalModifier=20
   characterStrengthModifier=8 characterLifeModifier=12 characterOffensiveAbilityModifier=8
   characterDefensiveAbilityModifier=6 defensivePhysical=14 defensiveProtectionModifier=8
diff=e itemLevel=61 lr=56 bitmap=e:  skill lv2, augments 3/3, values x1.4
diff=l itemLevel=74 lr=69 bitmap=l:  skill lv3, augments 4/4, values x1.9 (phys 68/95)
```

**Coverage note:** `crowheroes` also contains `bastien*`, `zilla01/02/03`, controllers, effects,
equipment, and skill records that are NOT fightable Hero/Boss/Quest monsters (they are variants,
props, or assets) and are correctly excluded. The fightable Crow Heroes needing souls are exactly the
14 above (5 headliners + 9 here), matching the audit's Crow-Heroes NONE rows.

**Builder pattern for Section 3:** one `_create_crow_heroes_souls(db)` function mirroring
`_create_neanderthal_warband_souls:2293`, building all 9 with per-monster tier tuples (the marquee 5
from their full 3.1 blocks, the 4 novelties from their recipe rows), calling `_create_soul` for each.
The 2 summon-style ones (Rainbowbright, plus Kaets which lives in 2.9) reuse existing soul-usable
SpawnPet skills, so no pet-from-Lyia build is required for the faction except the Lil'Lued Elder Djinn
headliner (2.5).

---

## 4. The Diablo 2 NPC trio (`records\drxcreatures\xurder\d2npc\`)

A cameo trio of walking D2 town NPCs turned into killable quest bosses. Kallixenia/"Akara" is a
headliner (2.4). The other two:

| Boss / record | Tag | Levels | Grant | Rationale + source records | Soul name |
|---|---|---|---|---|---|
| **Charsi** `d2npc\01_charsi.dbr` | `tagD2NPCcharsi` | 36/54/69 | SKILL (smith's calculated strike) | The D2 blacksmith. Signature `calculatedstrike` [Skill_WeaponPool_ChargedFinale] + `openwound`. SKILL: grant a heavy physical charged-strike proc (`demastia_strike` or `calybe_eclipse`-style) + aug `drxcalculatedstrike`, `drxdualweapontraining`. Physical bruiser-smith. | `{^F}Soul of Charsi the Smith` |
| **Gheed** `d2npc\01_gheed.dbr` | `tagD2NPCgheed` | 36/54/69 | SKILL (merchant's luck - utility) | The D2 caravan merchant; NO combat skills (only passives). A pure-stat/utility "lucky merchant" soul: no proc, no offensive suite, instead a distinctive UTILITY block: high `characterIncreasedExperience`... actually TQ souls can carry `characterDefensiveAbility`, big `characterLifeModifier/ManaModifier`, `%totalspeed`, `characterDodgePercent`, and (flavor) large flat `characterLife` - the "survive by running and luck" soul. This is the one intentionally NON-combat soul, mirroring how the audit flags Gheed as skill-less; give it charm/utility so it is still worth equipping. | `{^F}Soul of Gheed the Merchant` |

**Builder pattern:** fold into a `_create_d2npc_souls(db)` with Kallixenia (2.4), Charsi, Gheed.
Gheed's block deliberately omits `itemSkillName`/augments and leans on `characterTotalSpeedModifier`,
`characterDodgePercent`, `characterLifeModifier`, `characterManaModifier`, `defensiveProtection`, and
a large flat `characterLife`, tiered 36/54/69.

> The other `d2npc` records (`02_drognan`, `02_fara`, `03_ormus`, ...) are Act 2/3 NPCs that are NOT
> flagged as soul gaps in the audit (they are not in the Table A NONE list, i.e. not classified as
> killable Hero/Boss/Quest with a missing soul, or are non-combat props). Only the Act 1 trio
> (Akara/Charsi/Gheed) are the audit's `tagD2NPC*` NONE rows. If later audit passes flag the Act 2/3
> NPCs as killable, extend `_create_d2npc_souls` the same way.

---

## 5. The wired-but-stat-only "never-completed" souls (Table B)

**Count reconciliation (was loose in the prior draft):** Table B in the audit is **60 unique bosses**.
Of those, **9 already have a hand-crafted exemplar soul** (SP Toxeus, Main Toxeus, Rakanizeus,
Leinth, Murder Bunny, SP Hades main-Hades split, Cold Worm, Dagon, Calybe - each marked "already
complete" below) and so need NO work; the **remaining ~51** get the scan-and-set completion pass. The
"~40 never-completed / ~31 completions" figures used in the earlier draft understated the roster and
are corrected here to **60 total = 9 exemplars + ~51 completions**. (A few of the 51 are themed 3-soul
sets - the Graeae sisters, for instance - so the raw record count is higher.) Coverage is complete:
every one of the 60 Table B rows appears below, either as "already complete" or with a completion
delta.

These bosses ALREADY have a soul with a working proc/augments/stats (the audit lists each). Per Will's
directive they were "never completed" - they are functional but shallow versus the hand-crafted
exemplars. This section specifies the **completion pass**: bring each up to exemplar depth WITHOUT
changing its existing wiring, by scan-and-setting a richer stat block onto the existing
`<name>_soul_{n,e,l}` records (the `_overhaul_main_toxeus_soul` pattern - never `clone_record`,
never re-wire the monster).

For each, the audit already tells us the granted skill + current augments + current stats. The
completion recipe is uniform and mechanical, so it is given once here as a template, then per-boss
deltas follow.

### 5.1 The completion template (apply to every Table B soul)

Given an existing soul that grants skill `X` with augments `A1/A2` and a thin stat line, bring it to
depth by ADDING (scan-and-set, preserving the existing grant):

1. **Keep** its `itemSkillName = X` and both augments; **scale** their levels to the exemplar curve
   (proc 4/6/8, augments 3/4/5 by N/E/L) if currently lower.
2. **Add a full offensive suite** matched to the boss's damage type from its Table B skills: flat
   `offensive<Type>Min/Max` + `offensive<Type>Modifier`, plus its control effect
   (`offensiveSlow<X>Min`+`...DurationMin`, or `offensiveStun*`, or
   `offensiveTotalResistanceReductionAbsolute*`).
3. **Add %-stat modifiers**: the 3-4 that fit its archetype (`characterLifeModifier` always; then
   Str/Dex/Int + Offensive/DefensiveAbility as fits melee/caster).
4. **Add a defensive line** themed to the boss (its element resist; `defensiveLife`; for tanks
   `defensiveProtectionModifier`).
5. **Add a flavor callback** where the boss has one (a weakness as a small negative resist; a speed or
   dodge trait; a life penalty for glass-cannons).
6. **Tier-scale** every added field N/E/L at roughly 1x / 1.4x / 1.9x, itemLevel tracking the
   monster's `charLevel`.

Result: each Table B soul goes from ~2-5 meaningful fields to ~16-20, matching the bulk exemplars
(Leinth/Dagon/Cold Worm depth) while keeping its proven proc.

**WORKED EXAMPLE (so "completion" is concrete, not just a template).** Take **Cyclops Polyphemus**
(`tagMonsterName155`, Lv ~20/44/59). Its shipped `polyphemus_soul_{n,e,l}` currently carries (per the
audit) only: `itemSkillName = cyclops_groundsmash` + `characterLife 120/241/340` +
`offensivePhysicalMin 15/27/39` + `characterLifeModifier 10/12/14`. That is 4 meaningful fields. The
completion scan-and-sets the following ONTO those three existing records (keeping the groundsmash proc
and the existing fields), turning it into a full ~18-field club-bruiser soul. This is exactly the
numeric density every completion should reach:

```
# Polyphemus completion - values are the ADDITIONS/overrides per tier (N / E / L)
itemSkillLevel                = 4 / 6 / 8            (scale the kept cyclops_groundsmash proc)
itemSkillAutoController        = _AC_ON_ATTACK       (groundsmash is an attack proc)
augmentSkillName1 = records\skills\warfare\drxonslaught.dbr      level 3 / 4 / 5   (his club escalation)
augmentSkillName2 = records\skills\warfare\drxbattlerage.dbr     level 3 / 4 / 5   (giant's rage)
offensivePhysicalMax          = 60 / 95 / 135
offensivePhysicalModifier     = 30 / 42 / 60
offensiveStunMin              = 1.0 / 1.5 / 2.0      offensiveStunMax = 2.0 / 2.5 / 3.0   (club-slam stun - his signature)
offensivePierceRatioModifier  = 12 / 16 / 22
characterStrengthModifier     = 8 / 11 / 15
characterConstitutionModifier = 6 / 8 / 11
characterOffensiveAbilityModifier = 6 / 8 / 11
defensivePhysical             = 15 / 21 / 28
defensiveProtectionModifier   = 8 / 11 / 15
characterTotalSpeedModifier   = -4 / -4 / -3         (flavor callback: a lumbering cyclops is slightly slow)
# (existing characterLife 120/241/340, offensivePhysicalMin 15/27/39, characterLifeModifier 10/12/14 are KEPT)
```

Apply the identical shape to every completion row in 5.2, swapping the damage type/control effect to
match that boss's Table B skills (fire+burn for Yaoguai, cold+freeze for the yetis, lightning+cast for
the telkines, poison+slow for the spider/scorpos, etc.) and the flavor callback to that boss's gimmick.
The 5.2 rows give exactly those per-boss deltas (damage suite + %-mods + flavor); read each row as
"plug these into the worked-example skeleton at 1x / 1.4x / 1.9x tier scaling."

### 5.2 Per-boss completion deltas (grouped by area)

Grant column: **KEEP** = keep the existing proc/summon (it is already the iconic choice); the work is
the stat block. **Bold** = a recommendation to change the grant to something more iconic.

#### Quest-boss "main story" bosses (`records\creature\monster\questbosses\`)

| Boss (tag) | Existing grant (KEEP) | Damage suite to add | %-mods + flavor |
|---|---|---|---|
| Chimaera (`tagMonsterName004`) | summon_chimera (KEEP - iconic) | pet-focused: raise pet via `characterLifeModifier`, add `characterIncreasedProjectileNumber`-free small phys line | Str/Con; keep its `characterDexterity -20/-37` glass flavor; +`defensiveFire` |
| China Telkine Ormenos (`tagMonsterName122`) | ormenos_energyblast (KEEP) | cold+life `offensiveColdMin/Max` + `offensiveLifeMin/Max` + slow+dur | Int/Mana; cast-speed; +`defensiveCold` (huge current `characterMana` is the flavor - keep) |
| Cyclops Polyphemus (`tagMonsterName155`) | cyclops_groundsmash (KEEP) | massive phys `offensivePhysicalMin/Max` + stun (his club) + pierce | Str; `offensiveStun*`; +`defensivePhysical` |
| Yaoguai (`tagMonsterName1184`) | yaoguai_flamering (KEEP) | fire `offensiveFireMin/Max` + burn dot + phys (his charge) | Str/Int; `offensiveSlowBurning*`; +`defensiveFire` |
| Dragon Liche (`tagMonsterName1186`) | galeforce (KEEP) | cold `offensiveColdMin/Max` + freeze + %life (his decomposition) + resist-shred | Int/Mana; `offensiveFreeze*`; +`defensiveCold`; flavor: pet-steal is signature, add `characterManaModifier` high |
| Gargantuan Yeti (`tagMonsterName1182`) | yeti_freezingblast (KEEP) | cold + freeze | Str/Con; keep `characterDexterity -` flavor; +`defensiveCold` high |
| Euryale (`tagMonsterName143`) | drxregrowth (KEEP) | cold+life (ice enchant); its heal is the identity | Int/Dex; +`characterManaRegenModifier`; +`defensiveCold` |
| Medusa (`tagMonsterName145`) | medusa_petrify (KEEP - iconic petrify) | fire (fire enchant) + phys; petrify is the star | Int/Dex; `offensiveFreeze`(petrify-as-freeze flavor); regrowth heal add | 
| Sstheno (`tagMonsterName144`) | (augments only: envenom+spear) -> **ADD** `medusa_petrify`-family or `arachne_venomspray` proc | poison `offensiveSlowPoison*` + phys + pierce (spear) | Str/Dex/OA; poison focus |
| Greek Telkine Megalesios (`tagMonsterName120`) | thunderballnova (KEEP) | lightning `offensiveLightningMin/Max` + %life blast + disruption | Int/Mana; cast-speed; +`defensiveLightning` |
| Hydra (`tagMonsterName126`) | summon_hydra (KEEP - iconic) | pet-focused; small tri-breath flat line (fire/cold/poison) | Str/Con; keep flat life/phys; tri-elem defense |
| Manticore (`tagMonsterName1185`) | manticore_quills (KEEP) | phys+poison quills + pierce + disruption | Dex/Str; `offensiveSlowPoison*`; pierce |
| Minotaur Lord (`tagMonsterName286`) | (augments: dualweapon+onslaught) -> **ADD** `earthfury_ring` proc (his earthfury) | phys + fire (his fire bonus) + battle-rage speed | Str/OA; attack-speed; +`defensivePhysical` |
| Barmanu (`tagMonsterName1183`) | barmanu_blizzard (KEEP - iconic frost storm) | cold + stun (warshout) + phys (blunt) | Str/OA; `offensiveStun*`; +`defensiveCold` |
| Necromancer Alastor (`tagMonsterName110`) | (augments: deathchill+staff) -> **ADD** `lifedrain` or `melinoe_bloodboil` proc | cold+life + life/mana leech (his signatures) | Int/Mana; cast-speed; +`defensiveLife` |
| Pharaoh's Honor Guard (`tagMonsterName1180`) | summon_pharaohguard (KEEP - iconic) | pet-focused; his stomp as small phys line | Str/Con; `defensiveProtectionModifier`; movement-only penalty (existing) |
| Sandwraith Lord (`tagMonsterName060`) | sandsandstorm (KEEP) | phys + pierce (sandblast) + slow + resist-shred (sandstorm) | Str/OA; slow; +`defensivePierce` |
| Scarabaeus (`tagMonsterName043`) | scarabaeus_poisonspray (KEEP) | poison spray + %life; egg-summon flavor | Str/Con; `offensiveSlowPoison*`; +`defensivePoison` |
| Scorpos King Nehebkau (`tagMonsterName115`) | nehebkau_poisongasbomb (KEEP) | poison + phys sting + speed (his speed aura) | Str/Dex; `offensiveSlowPoison*`; total-speed |
| Spartacentaur Nessus (`tagMonsterName097`) | nessus_enduranceaura (KEEP - iconic aura) | phys + bleed (his bleed) + endurance | Str; `offensiveSlowBleeding*`; `defensiveProtection`; life-regen (aura flavor) |
| Spider Queen Arachne (`tagMonsterName114`) | arachne_venomspray (KEEP) | poison + %life; spider-summon flavor | Dex; `offensiveSlowPoison*`; total-speed (her speed buff); +`defensivePoison` |
| Talos (`tagMonsterName066`) | talos_flamethrower (KEEP) | fire + phys (fist) + stun (stomp) | Str; `offensiveStun*`; big `defensiveProtection` (bronze giant) |
| Terracotta Mage Bandari (`tagMonsterName123`) | drxstormnimbus (KEEP) | cold+lightning (energy blast/nimbus) + teleport flavor | Int/Mana; cast-speed; +`defensiveLightning` |
| Titan Typhon (`tagMonsterName382`) | typhon_meteorstorm (KEEP - iconic meteors) | fire meteors + phys + %life (his leech) | Str/Int; big life+mana; +`defensiveFire`; note: also carries a `hades_soul` variant (Typhon statue) - completion applies to `typhon_soul_*` | 
| Xiao (`tagMonsterName361`) | peng_summon (KEEP) | pet-focused; lightning-melee flavor small line | Dex; keep `characterLifeModifier -30` glass flavor; +`defensiveLightning` |

#### Hero "um_" bosses across creature folders (the rest of Table B)

Same completion template; grant kept, stat block deepened. Key ones (each keyed by its Table B row):

| Boss (tag) | Existing grant (KEEP) | Suite to add |
|---|---|---|
| Elephant Snatcher (`tagNewHero27`, bat) | lifedrain | phys + life-leech + frost-strike flavor; Str/Con |
| Grimshell (`tagNewHero63`, beetle) | stygianreaver_bolt | vitality bolt + %life; necro augments already good; Int |
| Dark Satyr Shaman (`tagMonsterName293`, arena) | (regrowth aug only) -> **ADD** `firefragmentnova` proc | fire (his flame surge/volcanic orb/meteor) + mana; Int/Mana |
| Stormbird Mormo (`tagNewHero316`, carrionbird) | (stormwisp aug only) -> **ADD** `ringoflightning` proc | lightning (etherealshock/ternion) + dodge (his dodge); Dex/Int |
| Permean (`tagNewHero236`, dragonlich) | permean_extinction (KEEP) | phys+fire (sandspire/breath) + slow; Str; pet-augment already good |
| Kaublasia (`tagNewHero179`, gorgon) | (bow+fire augs only) -> **ADD** `firefragmentnova` or `duneraider`-style flame proc | fire + phys; Dex/DA (its current bow/fire theme); +`defensiveFire` |
| Phagia (`tagNewHero182`, human) | summon_phagia (KEEP - iconic) | pet-focused; her maenad sorcery small lightning line; Int (note: also has a `maenadsorceress_soul` variant) |
| Uber Limos (`tagNewHero307`, limos) | barmanu_blizzard (KEEP) | cold + freeze (glacial assault/chilling air) + phys; Str/Int; big `defensiveCold` |
| Syrinx (`tagNewHero317`, naiad) | syrinx_chainleech (KEEP) | lightning/void + %life (void nova) + chain; Dex/Int; nymph-summon augment good |
| Wheedletongue (`tagNewHero321`, ratman) | (envenom+calc augs only) -> **ADD** `arachne_venomspray` or `poisonorbs` proc | poison + phys (throwing knife/takedown) + deathchill; Dex |
| Rakanizeus (`tagNewHero87`, satyr) | summon_rakanizeus (ALREADY the gold-standard exemplar - no change) | already complete (Section 1) |
| Palai (`tagNewHero181`, sepulchralwyrm) | palai_bigbolt (KEEP) | fire + phys (firebreath/nova/ring of flame) + retaliation-fire flavor; Str/Int; +`defensiveFire` |
| Toxeus main (`tagMonsterName190`, skeleton) | toxeus_flashpowder (ALREADY overhauled to Tier 3 - `_overhaul_main_toxeus_soul`) | already complete (Section 1) |
| Xaiweng (`tagNewHero196`, skeleton) | xeiwang_absorb (KEEP - heal/absorb) | fire (his fire strike/charge) + %life; Dex/Str; heal-flavor life-regen |
| Black Widow Arachne's Shame (`tagBlackWidow`, typhon) | arachneshame_rangedweb (KEEP) | poison + web-slow (debuf) + %life; Dex; +`defensivePoison` |
| Melalos (`tagNewHero177`, zombie) | summon_zombiesoldier (KEEP - iconic) | pet-focused; plague/rot small poison-vitality line; Int; dark-covenant/plague augs good |
| Hades main / SP Hades (`xtagMonsterHades`) | hades_star / (SP Hades = exemplar 1.1) | main `hades_soul` completion: shadow phys+life+resist-shred, ternion/bladehoning augs good; SP already complete |
| Leinth (`tagBWLeinth`) | melinoe_bloodboil (ALREADY the exemplar `_create_leinth_soul`) | already complete (Section 1) |
| Murder Bunny (`tagUrderMunder`) | cyclops_groundsmash (ALREADY exemplar `_create_murder_bunny_soul`) | already complete (Section 1) |
| Aktaios (`tagMonsterName121`) | firefragmentnova (KEEP) | fire nova + mana; volcanic-orb augs good; Int/Mana; small `defensivePhysical -` flavor |
| Cold Worm (`tagD2Boss004`) | (ALREADY exemplar `_create_coldworm_soul`) | already complete (Section 1) |
| Dagon (`tagD2Boss033`) | (ALREADY exemplar `_create_dagon_soul`) | already complete (Section 1) |
| Calybe (`tagNewHero200`) | calybe_eclipse (ALREADY hand-tuned `SOUL_OVERHAULS['calybe_soul']`) | already complete (Section 1) |
| Graeae Deino/Enyo/Pemphredo (`xtagMonsterGraeae1/2/3`) | deino_lightningclap / enyo_thunderstorm / pemphredo_thunderspark (KEEP) | lightning suite + %mana; the "three sisters" - build as a 3-soul set; Int/Mana; +`defensiveLightning`; flavor `characterStrength -` (they are frail crones) |
| Charon Form2 (`xtagMonsterCharon`) | charon_buffself / boss_charon (talos_flamethrower) (KEEP) | fire+phys (geyser/swoop) + mana; Int/Str |
| Cerberus (`xtagMonsterCerberus`) | cerberus_breathwave (KEEP) | poison/acid breath + phys bite + roar-slow; Str/Dex |
| Skeletal Typhon (`xtagMonsterSkeletalTyphon`) | skeletaltyphon_bonespire (KEEP) | phys bone + spirit + trap-debuf; Str/Int; enslave-spirit aug good |
| Antaeus (`tagNewHero228`, gigantes) | antaeus_chargedstrike (KEEP) | phys+poison charged + teleport flavor; Str; sword aug good |
| Deep Thresher (`tagNewHero188`, karkinos) | thresher_geyser (KEEP) | phys+fire geyser + bleed (shredder) + burrow flavor; Str/DA; big protection |
| Meglograi (`tagNewHero180`, keres) | meglograi_burst (KEEP - heal/burst) | phys+life (bat/attack) + blink flavor; Dex/Mana; heal life-regen |
| Blood Crow (`tagNewHero81`/`tagNewHero82`, lostsoul/test) | (fire+studyprey augs only) -> **ADD** `firefragmentnova` proc | fire enchant + deathchill + zombie-summon flavor; Int; keep `characterLifeModifier -` flavor |

> Every "already complete (Section 1)" row is one of Will's hand-crafted exemplars and needs no work.
> Every other row is a scan-and-set completion. Where the "Existing grant" is only augments (no proc),
> the **bold ADD** picks the single most iconic soul-usable proc from that boss's own Table B skill
> list, upgrading the soul from augment-only to signature-proc, which is the biggest quality jump.

### 5.3 Ancient Limos family (Olympus super-variants)

The Limos folder holds Olympus-only super-variants (`bm_ancientlifeeater_36`, `bm_ancientsoulstealer_
39`, `um_inemios_41`, `um_sybaris_41`, `um_venemurax`) that share Limos skills. They are Champion or
higher-level re-skins of the Lifeeater; per the mod's design (only Hero/Boss/Quest drop souls) the
**Champion `bm_ancient*` variants do NOT need their own souls** (they inherit the gate-off). The
Boss/Hero-classified ones (`um_inemios_41`, `um_sybaris_41`, `um_uber_45` already has `uber_soul`)
should, if flagged Boss/Hero, receive a **shared Ancient Limos soul** reusing the Limos Lifeeater
design (2.3) scaled up, OR their own thin completion. Recommendation: after fixing the base Lifeeater
stub (2.3), audit these for classification; wire any Hero/Boss ones to a scaled clone of the
Lifeeater stat block via `_create_soul(db, 'inemios'/'sybaris', ...)`. This is a follow-up, gated on
their actual `monsterClassification` (several are Champion = intentionally soul-less).

---

## 6. Other single-boss no-soul design targets

Remaining audit NONE rows that are real killable monsters (not utility props), specified at
bulk-roster depth. All Quest/Hero class, drop 66%, `_create_soul`.

| Boss / record | Tag | Levels | Grant + rationale | Source records | Soul name |
|---|---|---|---|---|---|
| **Blood Abomination Spiritcaller** `bloodabomination\04_spiritcaller_40.dbr` | `tagAbomShaman` | 40/56/71 | SKILL (shadow/leech caster). Olympian satyr-mage: `04_shadowbolt` + `alastor_lifeleech`/`_manaleech` + circle of decay. | proc: `lifedrain` on-attack; aug: `drxdarkcovenant`, `drxdeathchillaura`. cold+life+leech suite; Int/Mana | `{^F}Soul of the Blood Shaman` |
| **Fleshrender** `rumormonsters\orient\jo7_raptor_30.dbr` | `tagMonsterName317` | 30/33/.../69 | SKILL (rending bleed). Raptor hero. | proc: a bleed-heavy `furyclaw_saberslash` or `takedown`; aug: `drxbattlerage`, `drxlethalstrike`; phys+bleed+pierce; Str/Dex | `{^F}Soul of the Fleshrender` |
| **Ambush! Anklesickle** `tidecrawler\um_anklesickle_13_ambush.dbr` | `tagNewHero290` | 13/39/57 | SKILL (ambush strike). Tidecrawler. | proc: `poisonorbs`/pierce burst; aug: `drxenvenomweapon`, `drxstudyprey`; poison+pierce; Dex; low-level | `{^F}Soul of the Anklesickle` |
| **Egypt Monolith** `devices\darkobelisk\egypt_monolith_50.dbr` | `tagNewHero55` | 50/70/93 | SKILL (obelisk curse). Device (dark obelisk). | proc: `records\skills\soulskills\ringoflightning.dbr` (or a curse nova); aug: `records\skills\storm\drxlightningbolt.dbr` + `records\skills\spirit\drxdeathchillaura.dbr` (NOT `drxarcaneblast`, which dangles); lightning/vitality; Int; big `defensiveElementalResistance` (a stone monolith) | `{^F}Soul of the Dark Monolith` |
| **The Trap** `devices\firetrap\um_thetrap_25.dbr` | `tagNewHero62` | 25/45/68 | SKILL (fire burst). Device (fire trap). | proc: `firefragmentnova`; aug: `drxfireenchantment`, `drxringofflame`; fire + retaliation-fire; Str; novelty trap soul | `{^F}Soul of the Fire Trap` |

> The remaining Table A NONE rows are the three `records\test\outsider_hero_*` (dev-test heroes, Low
> severity, `NOT_WIRED_NO_REF`) and the `xsq*` escort/banner quest NPCs
> (`xsq22_killable_banner`, `xsq21_escortmessenger`, `xsq03_escortworker`, etc.). The escort NPCs are
> "does not attack monsters / can trigger BVs" quest actors - they are killable but are quest-flow
> props, not real fights, and per the audit's own N/A framing should NOT get souls (a soul on an
> escort NPC would be thematically nonsensical and is not what "boss souls" means). The `outsider_
> hero_*` test records can optionally receive a generic bow/melee/caster soul if Will wants the dev
> souls complete, but they are the lowest priority and are explicitly test scaffolding. Excluded from
> the design set with rationale, not silently dropped.

---

## 7. Coverage summary

| Category | Count | Where |
|---|---|---|
| **Headliner designs (full depth, ★)** | **10** | Section 2: Ainex, Blood Witch High Priest, Limos Lifeeater (stub fix), Kallixenia, Lil'Lued Elder Djinn, Zilla, Numberouane, Kreeloo, Kaets, Anapaest |
| Crow Heroes faction (remaining) | 9 (marquee 5 full blocks in 3.1 + 4 novelties) | Section 3 |
| D2 NPC trio (Charsi, Gheed; Akara is headliner 2.4) | 2 | Section 4 |
| Table B "never-completed" completion pass | **60 total** = 9 already-exemplar (no work) + ~51 scan-and-set completions | Section 5 |
| Other single-boss no-soul targets | 5 | Section 6 |
| Explicitly excluded with rationale (utility props, escort NPCs, dev-test) | 15 props + 3 escort + 3 test | Section 6 note + audit Table A |
| **New soul RECORDS to create (n/e/l each)** | **~26 monsters** (Sections 2.1-2.10 minus the in-place stub fix + Sections 3,4,6) | ~72-78 new `.dbr` soul records |
| **Table B souls to deepen in place** | **~51** | ~150+ records scan-and-set (some are 3-soul sets) |
| **New summon pets to build from Lyia** | **3** (Blood Witch High Priest, Lil'Lued Elder Djinn; + any Ainex-summon variant if chosen) | Section 2; the other summon-souls reuse existing soul-usable SpawnPet skills |

**Grant-type split across the new designs (Sections 2-4,6):** SUMMON = Blood Witch High Priest,
Lil'Lued, Kaets (existing SpawnPet skill), Rainbowbright (existing SpawnPet skill) = 4. SKILL = the
rest (Ainex, Limos, Kallixenia, Zilla, Numberouane, Kreeloo, Anapaest, Charsi, Gheed[utility],
Spiritcaller, Fleshrender, Anklesickle, Monolith, Trap, and all Crow Hero skill-souls) ~= 18. This
matches the exemplar ratio: summon the iconic *monsters* (djinn, blood-demon, plant swarm, war
standard), grant the iconic *ability* for everything defined by one devastating move.

---

## 8. Implementation checklist (per new soul)

1. Pick `base_name` (matches the record path stem, e.g. `ainex`, `zilla`).
2. Build `tiers = [ {diff,itemLevel,stats}, x3 ]` in the exemplar style (Section 1.2 grammar; per-tier
   `bitmap` n/e/l).
3. Call `_create_soul(db, base_name, tag, tiers, MONSTER_PATH, 66.0)` (bare `_ensure_record` under the
   hood, wires `lootFinger2Item1` + `chanceToEquipFinger2` on the monster).
4. **Skill souls:** ensure the `itemSkillName` proc record exists and is soul-usable (prefer an
   existing `records\skills\soulskills\*` proc; the ones named in this doc all exist per the DB probe);
   set `itemSkillAutoController` (`_AC_ON_HIT` / `_AC_ON_ATTACK` / `_AC_ON_EQUIP`); augments point at
   real `records\skills\<mastery>\drx*.dbr`.
5. **Summon souls:** build the pet set with a `_create_<name>_pet_skill(db)` cloned from
   `_create_boneash_pet_skill` (clone 3 pets from Lyia; copy animations + update skills from the
   source monster; `_set_pet_equipment` with hardcoded N/E/L item paths; `dropItems=0`, `giveXP=0`;
   clone the summon skill from `summon_lyia` for permanence; NO `spawnObjectsTimeToLive`; set
   `spawnObjects`, `isPetDisplayable=1`, `skillDisplayName`, `skillManaCost` 3-float array, up/down
   bitmaps). Point the soul's `itemSkillName` at the summon; set per-tier `itemSkillLevel` 1/2/3. For
   summon-souls that reuse an existing soul-usable SpawnPet (Kaets/Rainbowbright), skip the pet build
   and just set `itemSkillName` to that skill.
6. **Stub fix (Limos):** scan-and-set the stat block onto the existing 3 records; do NOT re-wire.
7. Register EVERY tag (`tagSVCSoul<Name>` + `...DESC` + any `tagSVCSummon<Name>` + `...DESC`) in
   `uber_soul_tags.txt` (Section 9), then rebuild so `validate_tags.py` passes.
8. Call the new `_create_*` fn from `apply_patches`/`main` (`apply_svc_patches.py:~4372`, beside the
   existing `_create_sp_toxeus_soul(db)` etc.).
9. Rebuild DB + Text; verify `validate_tags` PASS; test with a freshly dropped soul (saves bake item
   props at pickup).

---

## 9. Consolidated tag manifest (paste into `uber_soul_tags.txt`)

Display names use the `{^F}` prefix; `...DESC` are the lore lines. (Ainex's name tag already exists;
its DESC is new.) Fill the DESC text from each soul's lore line above.

```
// --- Headliner soul names ---
tagSVCSoulAinex={^F}Soul of Ainex                          (EXISTS - add DESC)
tagSVCSoulAinexDESC=<lore 2.1>
tagSVCSoulBWHighPriest={^F}Soul of the Blood High Priest
tagSVCSoulBWHighPriestDESC=<lore 2.2>
tagSVCSummonBWHighPriest=Call the Blood Blade-Dancer
tagSVCSummonBWHighPriestDESC=<lore 2.2 summon>
tagSVCSoulLimosLifeeater={^F}Soul of the Lifeeater
tagSVCSoulLimosLifeeaterDESC=<lore 2.3>
tagSVCSoulKallixenia={^F}Soul of Kallixenia
tagSVCSoulKallixeniaDESC=<lore 2.4>
tagSVCSoulLilLued={^F}Soul of Lil'Lued the Elder Djinn
tagSVCSoulLilLuedDESC=<lore 2.5>
tagSVCSummonLilLued=Free the Elder Djinn
tagSVCSummonLilLuedDESC=<lore 2.5 summon>
tagSVCSoulZilla={^F}Soul of Zilla the Blade Dancer
tagSVCSoulZillaDESC=<lore 2.6>
tagSVCSoulNumberouane={^F}Soul of Numberouane
tagSVCSoulNumberouaneDESC=<lore 2.7>
tagSVCSoulKreeloo={^F}Soul of Kreeloo the Telkine
tagSVCSoulKreelooDESC=<lore 2.8>
tagSVCSoulKaets={^F}Soul of Kaets the Thornheart
tagSVCSoulKaetsDESC=<lore 2.9>
tagSVCSoulAnapaest={^F}Soul of Anapaest the Dishonored
tagSVCSoulAnapaestDESC=<lore 2.10>
// --- Crow Heroes (remaining) ---
tagSVCSoulGorgus={^F}Soul of Gorgus
tagSVCSoulJiaco={^F}Soul of Jiaco the Nightstalker
tagSVCSoulYerk={^F}Soul of Yerk
tagSVCSoulJabarto={^F}Soul of Jabarto
tagSVCSoulRainbowbright={^F}Soul of Rainbowbright the Standard-Bearer
tagSVCSoulLess={^F}Soul of Less
tagSVCSoulNomnom={^F}Soul of Nomnom
tagSVCSoulGitar3={^F}Soul of the Gitar Shrine
tagSVCSoulKir4={^F}Soul of the Kir Trap
tagSVCSoulLilLuedChild={^F}Soul of Little Lued          (novelty - optional)
// (+ matching ...DESC for each)
// --- D2 NPC trio ---
tagSVCSoulCharsi={^F}Soul of Charsi the Smith
tagSVCSoulGheed={^F}Soul of Gheed the Merchant
// (+ ...DESC)
// --- Other single-boss targets ---
tagSVCSoulBloodShaman={^F}Soul of the Blood Shaman
tagSVCSoulFleshrender={^F}Soul of the Fleshrender
tagSVCSoulAnklesickle={^F}Soul of the Anklesickle
tagSVCSoulDarkMonolith={^F}Soul of the Dark Monolith
tagSVCSoulFireTrap={^F}Soul of the Fire Trap
// (+ ...DESC)
// --- Table B completion pass: names ALREADY EXIST (souls already wired);
//     no new name tags needed, only richer stats. ---
```

---

## 10. Appendix: exemplar field-count evidence (for the depth bar)

Direct from `tools/apply_svc_patches.py` (line refs), the per-tier hand-set field counts that define
"complete":

- `_create_sp_toxeus_soul` (1409): **~31** fields/tier (proc+2 augments + 9 offensive + 4 evasion + 3
  speed + 7 %-mods + 2 reflect/armor). The ceiling. itemLevel N/E/L = 33/66/**80** (DB-verified; the
  docstring's "33/66/99" is a code/comment mismatch - the L record is itemLevel 80). Caveat: its
  `augmentSkillName2 = _SK_DISTORTION_WAVE` dangles in the built `.arz` (real record at
  `records\xpack\skills\dream\drxdistortionwave.dbr`), so this "ceiling" soul currently ships one dead
  augment - a pre-existing bug, not a depth question.
- `_overhaul_main_toxeus_soul` (1543): **~27**/tier.
- `_create_murder_bunny_soul` (1765): **~22**/tier.
- `_create_sp_hades_soul` (1861): **~20**/tier.
- `_create_leinth_soul` (1664): **~18**/tier (incl. the `defensivePoison: -8` weakness callback).
- `_create_coldworm_soul` (1166) / `_create_dagon_soul` (1957): **~16-18**/tier.
- `_create_rakanizeus_pet_skill` (320): pet = ~20 identity/stat fields + full N/E/L equipment loadout
  (3 slots x 3 tiers) + custom mesh/controller/status-icons; soul = ~14 fields.

Design bar applied in this doc: **headliners 20-24 fields/tier** (matching Murder Bunny / SP Hades /
Ainex), **bulk-roster 14-18/tier** (matching Leinth / Cold Worm / the warband), **summon souls** a
lighter ~13-14 soul fields because the pet is the payload but WITH a full Rakanizeus-depth pet
loadout. Every new soul carries: 1 signature proc-or-summon + 2 mastery augments + a damage-typed
offensive suite + %-stat modifiers + a themed defensive line + a flavor callback. That is the taste
standard, matched.
