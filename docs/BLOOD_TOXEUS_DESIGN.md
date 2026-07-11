# BLOOD TOXEUS - design spec for a new bleeding/vitality superboss + soul + set

> RENAME NOTE (Will 2026-07-07): the boss now ships as **"Toxeus the Murderer, Devourer of Blood"** (display tag `tagMonsterHemorrheus`) and his soul as **"{^F}Devourer of Blood Soul"** (`tagSVCSoulHemorrhage`); his visual uses the GREEN Athens Toxeus mesh `RevenantPoison.msh` (was `revenantstorm.msh`) with the crimson skin. The name "Hemorrheus / the Red Verdict" in the body below is superseded for DISPLAY but kept as the internal codename; record paths, tag keys, and set/item names are unchanged.

> A complete, DB-grounded design for a NEW Toxeus-family superboss who deals massive
> bleeding + vitality damage, out-classes the green Athens Toxeus, drops a bespoke bleeding
> item set + a boss soul, and stands guard beyond the exploding-blood-wall secret area.
> Every record referenced below either EXISTS in the built `.arz`
> (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, 50,327 records, re-read 2026-07-06 for the
> post-critique revision) or is a NEW record derived from a named existing one via the established
> builder patterns. All field-placement claims were re-checked by a per-category (item/set/soul/skill)
> field-validity audit; see the REVISION LOG in Section 9.
> Held to the taste bar in `docs/BOSS_SOULS_DESIGN.md` (SP Toxeus / Main Toxeus / Leinth are
> the exemplars). Companions: `docs/SOULS_COMPLETENESS_AUDIT.md`, `docs/BLOODCAVE_QUESTS_RCA.md`
> (the secret-area wiring), `docs/AREA_WIRING_RECIPE.md` Phase D (entity injection),
> `CLAUDE.md` "Key technical lessons". No em dashes by house style.

---

## 0. TL;DR (for Will)

- **Winning name:** **HEMORRHEUS, the Red Verdict** (aka "Blood Toxeus"; full name-slate + lore
  in Section 1). A crimson revenant of Toxeus flayed and reborn in the blood-cult's cauldron.
- **Power:** measurably stronger than BOTH Athens Toxeus (`um_toxeus_21`, Boss, Lv 25/45/65,
  3966/5156/6346 HP) and the SP super-variant (`um_toxeus_99`, Hero, Lv 33/66/99,
  9324/11655/13986 HP). Hemorrheus is **Lv 40/68/**`**100**` with **13000/18000/24000 HP** and
  a real bleed/vitality resist wall neither Toxeus has. He sits ABOVE SP Toxeus (Will asked for
  "stronger than the ATHENS one"; going past the SP variant too makes him the hardest Toxeus in
  the mod, which fits a hidden end-of-secret-area guardian). Full target table + baseline in
  Section 7.
- **Kit (data-only, blood-themed):** a Blood Boil hemorrhage-nova aura, a bladestorm that
  bleeds, a life-drain strike, a self-heal blood-pact, and a phase add-wave of exploding blood
  sprites + blood-demon champions (all EXISTING records). Section 2.
- **Loot:** the **"Crimson Verdict"** 4-piece bleeding set (weapon + 3 armor) as a single-tier
  LEGENDARY set with an escalating set bonus (the SV-correct encoding; N/E pieces are authored as strong
  standalone bleed gear, or a 3-set n/e/l variant per §3.1b), a guaranteed set-piece drop, a high-roll
  bleed affix table, and **his soul**. Sections 3-4.
- **Soul:** `{^F}Soul of Hemorrhage` (three tiers, Blood Boil proc + bleed/vitality suite +
  two bleed augments), built with the bare-`_ensure_record` `_create_soul` pattern. Section 4.
- **Placement:** PRIMARY = beyond the mega chest, in the secret hallway
  `new_secretdoor_transitionhallway` (rhymes with the exploding-blood-wall entry). FALLBACK =
  the Leinth finale room `bossfight`. Both verified on-mesh; exact spawn mechanism mirrored from
  the existing `q_leinth_lone` proxy. Section 5.
- **Implementation:** DB records via a new `_create_blood_toxeus()` in `apply_svc_patches.py`;
  map spawn via one `INJECT_SPECS` entry in `build_section_surgery.py`; tags into
  `uber_soul_tags.txt`. Section 6.

---

## 1. IDENTITY

### 1.1 Name candidates (crazier than "Blood Toxeus")

| Candidate | Read | Why |
|---|---|---|
| **HEMORRHEUS, the Red Verdict** ★ WINNER | "hem-OR-ree-us" | Greek-root pun (haemorrhage) that still scans as a TQ boss name and rhymes with "Toxeus". "The Red Verdict" makes him feel like a sentence carried out, not just a palette-swap. |
| Toxeus Sanguine, the Flayed Murderer | | Keeps the Toxeus name front-and-center; "Flayed" sells the skinless-crimson look and the cult-reforged lore. |
| The Crimson Assize / "Blood Toxeus" | | "Assize" = an old word for a court's judgement; leans hard into the murderer-executioner theme. Kept as the in-game subtitle. |
| Vorrhaghar the Exsanguinator | | Fully off-canon "crazier" option; strong but reads less like a Toxeus and more like a generic demon, so it loses the "a NEW Toxeus" brief. |

**Pick: HEMORRHEUS, the Red Verdict.** In-game display name (see tags, Section 6):
`{^r}Hemorrheus, the Red Verdict` (the `{^r}` gives boss-red text; the existing Toxeus tag
`tagMonsterName190` = "Toxeus the Murderer" is NOT reused so both bosses read distinctly on the
minimap and in the death banner).

### 1.2 Lore (one paragraph)

> When Toxeus the Murderer was cut down in the Athens catacombs, his corpse did not stay buried.
> The Blood Witch cult dragged what was left of him into the cauldron beneath the waterfall
> sanctuary and boiled the poison out of his marrow, refilling every dry vein with the blood of
> the drowned. What rose was not the green assassin the heroes remember. Hemorrheus wears his old
> speed and his old blades, but where Toxeus dealt a clean, quiet kill, the Red Verdict opens
> every wound at once and drinks. His bladestorm throws a red mist; his very presence makes the
> living bleed. The cult left him at the deepest door, past the exploding sacs of their unborn,
> as the last sentence anyone who reaches the sanctuary's heart will ever hear read aloud.

### 1.3 Visual build (EXISTING assets only, no new art)

Verified against the DB (records that already ship using these exact strings):

- **Mesh:** `Creatures\Monster\skeleton\revenantstorm.msh` - the same revenant rig SP Toxeus
  (`um_toxeus_99`) uses; confirmed present (3 records reference it, incl. `z_toxeus`,
  `cm_revenantstorm_17`).
- **Base texture:** `Creatures\monster\skeleton\newskeleton_crimson.tex` - a crimson/blood-red
  skeleton skin, confirmed present and used by **13+ records** (`um_bonefletcher_28`,
  `z_toxeus`, the crimson undead-brother rumor line, etc.). This is what makes him read as the
  BLOOD Toxeus at a glance while staying palette-consistent with the Toxeus family (Athens =
  `newskeleton_grean.tex` green; SP = `newskeleton_crimson.tex` crimson already). Hemorrheus
  takes the crimson skin at a larger scale so he is visibly the bigger, redder Toxeus.
- **Scale / height:** `scale = 2.1` (green Toxeus is 1.65, SP Toxeus is 1.65; Hemorrheus is
  noticeably larger, a physical step up), `actorHeight = 2.0`.
- **Proxy visual** (for the placed proxy, mirroring `q_leinth_lone`'s STRUCTURE): mesh
  `Creatures\Monster\skeleton\revenantstorm.msh`, `baseTexture = Creatures\proxyu_boss.tex`
  (the boss-proxy skin the game uses on all boss proxies; confirmed on `q_leinth_lone`),
  `scale = 2.1`, `placementExtents = 3.5`.
  - **Deliberate divergence from the donor (flagged, intentional):** the `q_leinth_lone` proxy record
    itself is DB-verified as `scale = 4.0` + `mesh = DRX\meshes\bloodwitch_leinth.msh` (Leinth's own
    witch model). We intentionally use `revenantstorm.msh` + `scale = 2.1` instead so the proxy's
    map-preview silhouette matches the Toxeus-family revenant Hemorrheus actually is, not Leinth. This
    is a design choice, not a copy error: the proxy's own mesh/scale is just the preview placeholder;
    what actually spawns is the `um_bloodtoxeus_*` MONSTER (§5.2 / §7), whose mesh/scale/texture are set
    on the monster record. Only the `baseTexture = proxyu_boss.tex` and `placementExtents = 3.5` are
    copied verbatim from the donor.

No `.msh`/`.tex`/`.anm` file is created. Everything above is an existing asset already resolved
by shipped records, so it is guaranteed present in the arcs at runtime.

---

## 2. SKILL KIT (the creative core)

Design grammar (per `BOSS_SOULS_DESIGN.md` Section 1.2): signature-first, thematically coherent,
data-only. Every skill below is an EXISTING record placed on the new monster's `skillName*`
fields (exactly how `um_toxeus_21` / `um_toxeus_99` carry their kits). Nothing new is authored
for the monster's kit; the only NEW skill records in this whole design are the summon skill +
pet records for the SOUL (Section 4), which follow the Lyia-clone rule.

Hemorrheus's fantasy = **"makes everything bleed, then drinks it"**. The kit layers a
hemorrhage aura, a bleeding bladestorm, a life-drain, a self-heal, and a summon phase.

### 2.1 Signature + core attack skills (all verified present)

| Slot | Record (EXISTS) | Class | Role in the fight |
|---|---|---|---|
| Signature nova | `records\skills\soulskills\melinoe_bloodboil.dbr` | `Skill_AttackRadius` | **Blood Boil** - an 8u-radius blood detonation. DB-measured payload: `offensiveLifeMin` 246-605 (per level), `offensiveSlowBleedingMin` 148-328, `offensiveSlowBleedingDurationMin` 2.0, `offensiveLifeLeechMin` 100. This IS the hemorrhage-nova; it life-leeches everything it bleeds. Leinth's own signature, reused - blood-cult-coherent. |
| Bleeding bladestorm | `records\skills\monster skills\attack_radius\toxeus_bladestorm.dbr` | `Skill_AttackProjectileRing` | Toxeus's ACTUAL bladestorm (carried by `um_toxeus_21`). Keeps the Toxeus melee identity; the bleed comes from his envenom/weapon buff below + the set-thematic red mist. |
| Envenom -> blood weapon | `records\skills\monster skills\buff_self\toxeus_envenomweapon.dbr` | `Skill_BuffSelfToggled` | Toxeus's weapon buff. On Hemorrheus it reads as "blood-slick blades" (the same toggle green Toxeus uses; re-skinned by context, not by a new record). |
| Life drain | `records\skills\spirit\lifedrain.dbr` | `Skill_AttackSpellChaos` | A ranged **Life Leech** drain (the established soul-usable/monster life drain, used by `elephantsnatcher`/`sandwraith` souls). Hemorrheus's "drinks it" beat. |
| Flash-powder blink | `records\skills\stealth\flashpowder.dbr` | `Skill_AttackRadius` | Toxeus's signature escape/reposition (on `um_toxeus_21`). Keeps him mobile and assassin-like between blood novas. |
| Lethal strike | `records\skills\stealth\lethalstrike.dbr` + `records\skills\stealth\lethalstrike_mortalwound.dbr` + `records\skills\stealth\openwound.dbr` | `Skill_AttackWeapon` / `Skill_Passive` | Toxeus's crit package (all three on `um_toxeus_21`). `openwound` (DB-verified Class = `Skill_Passive`, corrected from the earlier "modifier" label) is his bleeding-on-crit passive - on-theme and already paired with his attack. (The SOUL's on-theme bleed AUGMENT correctly uses the real `Skill_Modifier` record `drxopenwound`, §4.1 - a different record from this monster-kit `openwound` passive.) |

### 2.2 Phase / spawn mechanic (the "exploding blood things as adds")

Will asked for exploding blood things as adds to rhyme with the secret-wall fight. Both add
sources are EXISTING records:

- **Blood-demon champions:** `records\drxcreatures\blooddemon\b_med_blooddemon_3{0,1,2}.dbr`
  (`Monster`, mesh `DRX\meshes\blooddemon01.msh`, ~1081/1161/1241 HP, Lv 30-32/50-52/65-67).
  These are the SAME champions the exploding-wall guard pool (`q_highpriest_lone`) and the Leinth
  pool spawn, so reusing them keeps the sanctuary visually consistent.
- **Exploding blood sprites ("lildudes"):** `records\drxmap\pitsprites\t1_lildude_0{1,2,3}.dbr`
  (`Monster`) driven by `records\drxmap\pitsprites\t1_skill_pitspawner_summonlildude_0{1,2,3}.dbr`
  (`Skill_SpawnPetMonster`) - the literal exploding blood sacs from the DelphiLowlands
  blood-pit scene (`DROPPED_CONTENT_AUDIT` calls these the "exploding sprites"). They boom on
  contact (`lildude_boom_soundpak`).

**Two data-only ways to wire the phase (pick one at build time):**

- **(A) Proxy-pool boss + champion escort (SIMPLEST, recommended).** Hemorrheus is placed via a Proxy
  whose `ProxyPool` (like `q_leinth_lone`'s pool) carries `nameChampion1-3 = b_med_blooddemon_3{0,1,2}`.
  > ⚠️ **CORRECTED 2026-07-07 (the field semantics below were BACKWARDS in the original plan and shipped
  > a no-spawn boss).** `championChance` is NOT "the chance an add-wave appears on top of the boss." In
  > the TQ proxy resolver, **`championChance` is the PER-SPAWN probability that a spawn slot is filled by
  > a `nameChampionN` monster (blood demon) INSTEAD of a main-pool `nameN` monster (Hemorrheus).**
  > Champions REPLACE main spawns; they are not additive. `championMin/Max` cap how many of the
  > `spawnMin..spawnMax` slots become champions. So the original tuning
  > (`spawnMin=spawnMax=1, championChance=100, championMin=1`) meant the **single** spawn slot was ALWAYS
  > converted to a blood demon and the boss got **zero** slots -> Hemorrheus never spawned, only the
  > blood demons did (exactly Will's TESTHUB report). DB-proof: **every one of the 30 base-game boss
  > pools** (`bosspool_02_nessus` .. `bosspool_24_hydra`) ships `championChance = 0.1` + `spawnMax = 1`
  > precisely so the boss (the main) always spawns; `q_bloodtoxeus_lone` was the ONLY Boss-main pool in
  > the game set to `championChance = 100`.
  >
  > **CORRECT recipe (copies the shipped `xsq22_wave2_odontotyrranusandmelinoe_pool` /
  > `xsq17_keres_escortparty_pool` "boss + guaranteed champion escort" pattern):** give the pool
  > **`spawnMin = spawnMax = 3`, `championChance = 100.0`, `championMin = 2`, `championMax = 2`**, with
  > `name1-3 = um_bloodtoxeus_99` and `nameChampion1-3 = b_med_blooddemon_3{0,1,2}`. The `championMax = 2`
  > cap leaves `3 - 2 = 1` main-pool slot -> **exactly 1 Hemorrheus + exactly 2 blood-demon adds**, every
  > spawn, on all three difficulties. (`championMax` reliably leaving `spawnMax - championMax` mains is
  > proven by `duneraider_03_general03` and the two xsq pools above, all shipped/working encounters.) A
  > fail-loud build invariant (`_verify_mod_spawn_proxies_eligible`, §6.4) now asserts
  > `spawnMax - championMax >= 1` for every mod-authored spawn proxy so a crowded-out boss can never ship.
- **(B) On-death / on-hit sprite burst (more dramatic).** Add
  `records\drxmap\pitsprites\t1_skill_pitspawner_summonlildude_02.dbr` (`Skill_SpawnPetMonster`,
  EXISTS) to Hemorrheus's `skillName*` list with an on-low-health or on-death controller
  (`records\xpack\ai controllers\autocast_items\basetemplates\base_atself_lowhealth.dbr` =
  `_AC_LOW_HEALTH`, EXISTS) so that at a phase threshold he vomits a ring of exploding blood
  sprites. Fully data-only (a `skillName` + an existing controller, exactly how bosses trigger
  ondeath skills like `ondeath_necronova`).

Recommendation: ship **(A)** for the guaranteed guard, and add **(B)**'s single
`skill_pitspawner_summonlildude` skill for the low-health blood-sprite burst, giving a real
two-phase feel with no new records.

### 2.3 Scaling / defensive passives (reuse the Toxeus/boss templates)

Carry the same passives the Toxeus family and blood-cave bosses use, all EXISTING:
`records\skills\monster skills\passive_buffs\hero_scaling.dbr` (level scaling),
`records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr` (Toxeus's own
difficulty passive), `records\skills\monster skills\defense\armor_passive.dbr`,
`records\skills\boss skills\boss_conversionimmunity.dbr` (boss immunity bundle - immunity to
convert/taunt/fear/petrify + %life resist + life-leech resist; Leinth carries this), and
`records\drxcreatures\bloodwitch\skills\zpassive_resists_bleedvitleechconvert_x10plvl.dbr` (the
blood-witch bleed/vit/leech resist-per-level passive Leinth uses - thematically perfect for a
blood boss and it gives him the bleed wall neither Toxeus has).

---

## 3. THE BLEEDING ITEM SET - "Crimson Verdict"

A named 4-piece set: **weapon + helm + torso + armband**, blood/vitality/bleed themed, in Will's
dense-bespoke-affix style, with a per-piece-count escalating set bonus. Encoding verified against
real SV sets (`records\item\sets\set004.dbr` etc.): a set record carries `setMembers` (member
paths) + `setName` (tag), and the **set bonus stats are stored as per-count arrays directly on
the set record** (e.g. `set004.characterLife = [0, 42, 45, 45, 100]` = [1pc,2pc,3pc,4pc,5pc]).
The 4-piece set uses 4-element arrays `[1pc, 2pc, 3pc, 4pc]`.

### 3.1 Set structure - SINGLE-TIER (decision + evidence)

**Encoding decision (was a defect; now fixed).** Every set record in the built DB binds items of a
SINGLE difficulty tier - DB-verified across all 142 set records: each set's `setMembers` are purely
`n`, purely `e`, or purely `l` (`set002` = 5x `us_e_legendoffuxi`, `set004` = 5x `us_n_obsidianarmor`,
`set012` = 5x `us_l_alexander'spanoply`; the lone apparent exception `drxset026` is a 3-piece upstream
oddity, not a designed cross-difficulty set). **There is NO set record that spans n/e/l**, and there
is no `xxx_{n,e,l}.dbr` set-file trio anywhere. An item points at exactly one set via its `itemSetName`
(verified: `us_n_obsidianarmor` armor pieces -> `drxset004.dbr`), and only members of THAT set's own
tier count toward its bonus. So a single set record listing "one canonical tier's members" would make
ONLY that tier's pieces trigger the bonus; the other two tiers' pieces never would. The earlier draft
plan (one `svc_crimsonverdict` set, members "resolving across difficulties") does not match how the
engine/DB actually works and is dropped.

**Chosen approach: Crimson Verdict is a single-tier LEGENDARY set (the L pieces).** This matches every
shipped set exactly (one tier per set record) and puts the build-defining 4-piece bonus where set play
matters most - endgame Legendary. The N and E pieces (§3.2) are still authored as strong standalone
bleed items but carry NO `itemSetName` (they are not set members). See §3.1b for the documented
alternative (three set records) if Will wants the set to complete on all three difficulties.

- **Path (collision-free):** `records\item\sets\svc_crimsonverdict.dbr`
  (template `database\Templates\ItemSet.tpl`, matching every set004-style record).
- **`setName` tag:** `tagSVCSetCrimsonVerdict = The Crimson Verdict`.
- **`setMembers`** = the 4 LEGENDARY (`svc_l_*`) member paths from §3.2 (single tier, exactly as
  `set012` lists its 6 `us_l_alexander'spanoply` members).
- **Per-count set BONUS** (the escalating "bleed conductor"), 4-element arrays
  `[idx0 = 1pc = nothing, idx1 = 2pc, idx2 = 3pc, idx3 = 4pc]`. **Every field below was DB-verified as
  actually carried by real ItemSet records** (all appear on 142/142 sets except where noted), so none
  ship inert:

```
characterLifeModifier                = [0, 6, 10, 15]        # % life          (valid on sets)
offensiveSlowBleedingModifier        = [0, 25, 45, 75]       # % bleed damage - the payoff (valid on sets)
offensiveSlowBleedingDurationModifier= [0, 0, 20, 40]        # % bleed duration (valid on sets)
offensiveLifeLeechMin                = [0, 15, 25, 40]       # ADCtH / vitality leech (valid on sets: 12 sets carry it)
offensiveLifeModifier                = [0, 15, 25, 40]       # % vitality damage (valid on sets)
characterAttackSpeedModifier         = [0, 8, 12, 18]        # keep the bleed stacks coming (valid on sets)
characterLife                        = [0, 150, 300, 600]    # flat +life  (REPLACES skillLifeBonus - see note)
# 4-piece capstone flavor: a small chance-of-bleed retaliation so wearers "bleed back"
retaliationSlowBleedingMin           = [0, 0, 0, 120]        # (valid on sets: 142 sets carry the field)
retaliationSlowBleedingDurationMin   = [0, 0, 0, 3]          # (valid on sets)
```

> **Two dead-field corrections applied (both DB-proven, both were shipping inert in the earlier draft):**
> - **`skillLifeBonus` is a SKILL-ONLY field.** DB scan: of every record carrying it, **0 are
>   equipment items, 0 are sets, 0 are souls; all 107 are Skill_* records** (Skill_GiveBonus,
>   SkillBuff_Passive, etc.). It is NOT on the 603-field ItemSet schema. The earlier `skillLifeBonus`
>   set-bonus line would have done nothing. Replaced here with **`characterLife`** (flat life, verified
>   present on 142 set records + 6171 items) for the same "flat +life" intent.
>   (Set-record counting note: 143 records carry the ItemSet Class/template; 142 of them live under the
>   `records\item\...\sets\` path. Schema/"0 of" claims use the 143 class total; per-field presence
>   counts use the 142 path total. Both gates agree on every conclusion here.)
> - **`defensiveBleeding` is NOT an ItemSet field** (0 of 143 ItemSet records carry it; absent from the
>   603-field set schema). The earlier `[0,20,35,60]` set bleed-resist line was inert and is
>   **removed from the set bonus.** `defensiveBleeding` IS valid on individual item pieces (verified:
>   `u_l_painweaver` bow = `defensiveBleeding 55`; 67 items + 69 souls carry it), so it stays on the
>   §3.2 armor pieces and on the §4.2 soul, where it works. The boss's own bleed WALL (§7) is
>   unaffected - that comes from the `zpassive_resists_bleedvitleechconvert` passive, not from a set.

### 3.1b Alternative - three per-difficulty set records (only if Will wants n/e/l set completion)

If the set should complete on Normal and Epic too, author **three** set records
`svc_crimsonverdict_{n,e,l}.dbr`, each listing its OWN tier's 4 members, and point each item's
`itemSetName` at its own tier's set (`svc_n_veinrender.itemSetName = ...\svc_crimsonverdict_n.dbr`,
etc.). Give each the same bonus arrays scaled per tier (N ~0.55x, E ~0.78x, L = the block above). This
is the only correct way to get a cross-difficulty 4-piece; the single-tier-L set above is the
recommendation (simpler, matches every shipped set, endgame is where the bonus matters). Whichever is
built, the set BONUS field list is the corrected one in §3.1 (no `skillLifeBonus`, no set-level
`defensiveBleeding`).

### 3.2 The 4 members (L pieces = the set; N/E = standalone bleed gear; dense bespoke affixes)

Each member is a NEW item record derived by `_ensure_record` from a matching EXISTING base item
of the right slot/class (so the mesh, template, and base fields are correct), then over-statted.
Names use `{^r}` for the set-red. Three tiers per piece (`n`/`e`/`l`) tracking Hemorrheus's
40/68/100 level band; `levelRequirement = itemLevel - 5`. Below shows the **L-tier** stat block
(N = ~0.55x, E = ~0.78x, monotone) in the exemplar density (~12-16 affixes/piece).

**Set-membership (corrected).** Only the **L (`svc_l_*`) pieces are set members** of
`svc_crimsonverdict.dbr` (the single-tier decision in §3.1); each L piece sets
`itemSetName = records\item\sets\svc_crimsonverdict.dbr` (verified real: `us_n_obsidianarmor` pieces
carry `itemSetName -> ...\drxset004.dbr` in exactly this way). The **N and E pieces carry NO
`itemSetName`** - they are strong standalone bleed items, not set members (a mid-difficulty bridge to
the endgame set). (If §3.1b's three-set alternative is chosen instead, each tier's pieces point at
their own `svc_crimsonverdict_{n,e,l}.dbr`.) The earlier draft's aside that "SV set members already
ship as n/e/l variants (e.g. set002 `us_e_legendoffuxi`)" was a MISREAD and is removed: `set002`'s 5
members are ALL epic (`us_e_legendoffuxi`), a single-tier (epic) set like every other - not a
cross-tier family.

Derive-from bases (all confirmed present, correct slot/class - DB-verified 2026-07-06):

| Member | Slot | Derive from (EXISTS, class) | L-tier path (set member) | N/E paths (standalone) | Name tag |
|---|---|---|---|---|---|
| **Vein-Render** | 1H Sword | `records\xpack\item\equipmentweapons\sword\mi_l_melinoe.dbr` (`WeaponMelee_Sword`) | `records\item\equipmentweapon\sword\svc_l_veinrender.dbr` | `svc_n_veinrender`, `svc_e_veinrender` | `tagSVCwpnVeinRender` |
| **Cowl of the Red Verdict** | Helm | `records\xpack\item\equipmentarmor\helm\mi_l_melinoemage.dbr` (`ArmorProtective_Head`) | `records\item\equipmenthelm\svc_l_crimsonverdict.dbr` | `svc_n_`, `svc_e_crimsonverdict` | `tagSVChlmCrimsonVerdict` |
| **Sanguine Shroud** | Torso | `records\xpack\item\equipmentarmor\torso\mi_l_melinoemage.dbr` (`ArmorProtective_UpperBody`) | `records\item\equipmentarmor\svc_l_crimsonverdict.dbr` | `svc_n_`, `svc_e_crimsonverdict` | `tagSVCtorCrimsonVerdict` |
| **Hemorrhage Bindings** | Armband | `records\xpack\item\equipmentarmor\armband\mi_l_melinoemage.dbr` (`ArmorProtective_Forearm`) | `records\item\equipmentarmband\svc_l_crimsonverdict.dbr` | `svc_n_`, `svc_e_crimsonverdict` | `tagSVCarmCrimsonVerdict` |

(All `mi_{n,e,l}_melinoe` and `mi_{n,e,l}_melinoemage` bases exist at the correct classes across all
three tiers, so each tier can derive from its own base.)

**Vein-Render (L-tier sword) - the bleed weapon:** (`itemSetName` only on the L member; N/E omit it)
```
itemLevel=95  levelRequirement=90  itemSetName=svc_crimsonverdict  itemNameTag=tagSVCwpnVeinRender
offensivePhysicalMin=95   offensivePhysicalMax=150   offensivePhysicalModifier=40
offensiveSlowBleedingMin=180  offensiveSlowBleedingDurationMin=3   offensiveSlowBleedingModifier=60
offensiveLifeMin=70  offensiveLifeMax=110  offensiveLifeModifier=35        # vitality
offensiveLifeLeechMin=45                                                   # ADCtH
offensivePierceRatioModifier=25
offensivePercentCurrentLifeMin=6
characterAttackSpeedModifier=16
characterDexterityModifier=12  characterStrengthModifier=8
characterLife=250          # was skillLifeBonus (skill-only, inert on items) -> characterLife (valid on items)
```

**Cowl of the Red Verdict (L helm):** (`itemSetName` only on the L member; all fields item-valid)
```
itemLevel=95 lr=90  itemSetName=svc_crimsonverdict  itemNameTag=tagSVChlmCrimsonVerdict
characterLife=400  characterLifeModifier=12  defensiveBleeding=40  defensiveLife=25
offensiveSlowBleedingModifier=30  offensiveLifeLeechMin=20
characterOffensiveAbility=90  characterDefensiveAbility=60
defensivePhysical=180
```

**Sanguine Shroud (L torso):** (`itemSetName` only on the L member)
```
itemLevel=95 lr=90  itemSetName=svc_crimsonverdict  itemNameTag=tagSVCtorCrimsonVerdict
characterLife=850  characterLifeModifier=15  defensiveBleeding=45  defensiveLife=45
defensivePhysical=260  characterLifeRegen=12  characterDefensiveAbility=70
```
> Corrections vs the earlier draft, both DB-proven: `skillLifeBonus=300` (skill-only, inert on items)
> was folded into `characterLife` (550 -> 850); `defensiveLifeLeech=30` was DROPPED - it is inert on
> armor (0 equipment items in the DB carry `defensiveLifeLeech`; the only 3 records with it are
> ring-slot souls, e.g. the Limos soul), so the "resist being leeched" intent is carried instead by the
> already-valid `defensiveBleeding=45` + a bumped `defensiveLife=45`. (`defensiveLifeLeech` remains
> valid on the SOUL in §4.2, which is a ring/jewelry record like those 3 precedents.)

**Hemorrhage Bindings (L armband):** (`itemSetName` only on the L member; all fields item-valid)
```
itemLevel=95 lr=90  itemSetName=svc_crimsonverdict  itemNameTag=tagSVCarmCrimsonVerdict
offensiveSlowBleedingMin=140  offensiveSlowBleedingDurationMin=3  offensiveSlowBleedingModifier=45
offensiveLifeLeechMin=25  offensiveLifeModifier=25
characterAttackSpeedModifier=12  characterOffensiveAbility=70
defensiveBleeding=30  defensivePhysical=140
```

> Every affix on all four pieces above was DB-verified valid on equipment items (`offensiveSlowBleeding*`,
> `offensiveLife*`, `offensiveLifeLeechMin`, `offensivePierceRatioModifier`, `offensivePercentCurrentLifeMin`,
> `characterLife/Modifier`, `characterAttackSpeedModifier`, `defensiveBleeding` [67 items], `defensiveLife`,
> `defensivePhysical`, `characterLifeRegen`, `characterOffensive/DefensiveAbility`, `characterDexterity/StrengthModifier`).
> The only two invalid placements from the earlier draft (`skillLifeBonus`, `defensiveLifeLeech`) were on
> the sword + torso and are fixed above.

Design intent: individually strong bleed/vitality pieces; the L set bonus (Section 3.1) turns the
four Legendary pieces into a build-defining bleed engine (up to +75% bleed damage, +40% duration,
+40% vitality, big leech, +600 flat life) that plays directly into the soul's Blood Boil and the
boss's own theme. All three tiers are authored as gear; only the L pieces form the set (§3.1 decision),
so N/E are strong standalone bleed items that bridge to the endgame set.

### 3.3 Loot table (guaranteed set piece + high bleed rolls + the soul)

Hemorrheus's monster record gets, in Will's "guaranteed + high-chance" style:

- **The soul** on Finger2 (the standard soul slot):
  `lootFinger2Item1 = [blood_toxeus_soul_n, _e, _l]`, `chanceToEquipFinger2 = 100.0`
  (superboss guaranteed-drop for testing; the release pass `SVC_RELEASE_DROPS` retunes to
  66/25 like every other hand-crafted soul).
- **A guaranteed Crimson Verdict set piece.** Add a fixed-weight loot table
  `records\item\loottables\svc\crimsonverdict_guaranteed.dbr`
  (`LootItemTable_FixedWeight`) whose members are the 4 set pieces at the matching difficulty tier
  (weight 100 each -> always drops one of the four). Use `supra_special.dbr` purely as a **structural
  SHAPE donor** - it is DB-verified at `records\xpack\item\loottables\arcaneformulae\supra_special.dbr`,
  is exactly this class (`LootItemTable_FixedWeight`), and lists 25 weight-100 `lootName*` entries, so
  it is a perfect clone template for the fixed-weight pattern. NOTE (corrected): its CONTENTS are the 25
  Supra CRAFTING FORMULAE (`records\drxitem\supra\recipes\ar_*_formula.dbr` ...), and it is the arcane-
  formulae reward table, NOT the blood-cave mega-chest's own reward - the earlier "the mega-chest's
  `supra_special`" attribution was wrong (per `BLOODCAVE_QUESTS_RCA` the mega chest is
  `proxy_hidden_bloodcave_chest` -> `hidden_bloodcave_chest_0{1,2,3}` which then GIVES `supra_special`).
  Take only its shape. Wire the new table onto a guaranteed loot slot on the monster (e.g. `lootName1` /
  a dedicated `bonusLootName` with chance 100), mirroring how quest bosses attach a guaranteed table.
- **High bleed-affix drops.** Point one of the monster's random loot slots at
  `records\item\loottables\svc\bleed_affix_high.dbr` (new `LootRandomizer`-style table that
  references existing bleed suffixes/prefixes, e.g. the affixes on
  `u_n_tendonripper`/`u_l_nemesis'recurve` families that already carry
  `offensiveSlowBleedingMin`), giving a high chance of extra bleed-rolled gear on top of the set.

(All loot-table classes and the `supra_special` template are confirmed present;
`offensiveSlowBleeding*`-bearing items already exist to source the affix pool.)

---

## 4. HIS SOUL - `{^F}Soul of Hemorrhage`

A `BOSS_SOULS_DESIGN`-style entry: SKILL grant (his signature Blood Boil hemorrhage-nova), three
tiers, built with the **bare `_ensure_record`** `_create_soul` pattern (NEVER `clone_record`),
`{^F}` name prefix, per-tier icon, drop via `chanceToEquipFinger2`. Grant type rationale: like
SP Toxeus and Leinth, Hemorrheus is defined by one devastating ABILITY (the blood nova that
bleeds + leeches), so the soul grants the MOVE, not a summon. (A summon-of-himself alternative is
noted at the end for completeness, but skill-grant is the recommendation.)

### 4.1 Records + wiring

- **Builder:** new `_create_blood_toxeus_soul(db)` mirroring `_create_leinth_soul`
  (`apply_svc_patches.py:1676`), calling
  `_create_soul(db, 'blood_toxeus', 'tagSVCSoulHemorrhage', tiers, MONSTER, 100.0)`.
- **Soul paths (auto, collision-free):**
  `records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_{n,e,l}.dbr`.
- **Proc:** `records\skills\soulskills\melinoe_bloodboil.dbr` (`Skill_AttackRadius`, VERIFIED)
  as `itemSkillName`, controller
  `records\xpack\ai controllers\autocast_items\basetemplates\base_atself_onanyhit.dbr`
  (`_AC_ON_HIT`, VERIFIED) - Blood Boil detonates on the wearer's hits. This is the identical
  proc class Leinth's soul grants, so the on-hit controller is battle-tested for it.
- **Augment 1 (bleed):** `records\skills\stealth\drxopenwound.dbr` (`Skill_Modifier`, VERIFIED;
  Open Wound = the bleeding-on-attack modifier - the single most on-theme bleed augment in the
  game). Hardcode the verified path (per `BOSS_SOULS_DESIGN` Section 0: never a `_SK_*` that
  might dangle; `drxopenwound` resolves).
- **Augment 2 (vitality/decay):**
  `records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr` (`Skill_Modifier`, VERIFIED - the
  REAL "ravages of time" record; the intuitive `drxravagesoftime`/`_SK_RAVAGES_OF_TIME` path
  **DANGLES**, confirmed MISS in this DB, so it is NOT used). Gives the soul a life/decay bite
  that reads as the blood-boil's rot.
  - Alt augment-2 if a pure-bleed feel is wanted: `records\skills\stealth\drxanatomy.dbr`
    (`Skill_Modifier`, VERIFIED - Anatomy = +% vitality damage), also perfect. Author with
    `drxdeathchillaura_ravagesoftime` as primary; `drxanatomy` is the documented swap.

### 4.2 Three-tier stat block (Will's exemplar density, ~24 fields/tier)

Modeled on the Leinth soul (blood/life/bleed caster) but stronger, since this is the hardest
Toxeus's soul. `bitmap` set per tier (n/e/l) per the `BOSS_SOULS_DESIGN` one-line-per-tier icon
convention. itemLevel tracks Hemorrheus's 40/68/100 charLevel; `levelRequirement = itemLevel-5`.

```
diff=n  itemLevel=40  levelRequirement=35   bitmap=SVItems\jewelry\soul_n_icon.tex
  itemSkillName            = records\skills\soulskills\melinoe_bloodboil.dbr
  itemSkillLevel=4   itemSkillAutoController = _AC_ON_HIT (base_atself_onanyhit.dbr)
  augmentSkillName1 = records\skills\stealth\drxopenwound.dbr                 augmentSkillLevel1=3
  augmentSkillName2 = records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr augmentSkillLevel2=2
  offensiveLifeMin=45  offensiveLifeMax=70   offensiveLifeModifier=25          (vitality)
  offensiveSlowBleedingMin=70  offensiveSlowBleedingDurationMin=3  offensiveSlowBleedingModifier=35
  offensiveLifeLeechMin=35     offensivePercentCurrentLifeMin=4
  offensivePhysicalMin=35 offensivePhysicalMax=55  offensivePhysicalModifier=20   (Toxeus blades)
  offensivePierceRatioModifier=15
  characterAttackSpeedModifier=12  characterTotalSpeedModifier=8  characterRunSpeedModifier=10
  characterDodgePercent=8                                                       (assassin)
  characterLifeModifier=10  characterStrengthModifier=6  characterDexterityModifier=8
  defensiveLife=18  defensiveBleeding=20   defensiveLifeLeech=20
diff=e  itemLevel=68  levelRequirement=63   bitmap=SVItems\jewelry\soul_e_icon.tex
  (skill lv 6, augments 4/3, all offensive x~1.4: bleedMin 120 / lifeMin-Max 65-100 /
   physMin-Max 60-90; bleedModifier 50; leech 55; dodge 11; %-mods life 14 / str 8 / dex 11;
   defensiveBleeding 28; attack speed 16)
diff=l  itemLevel=100 levelRequirement=95   bitmap=SVItems\jewelry\soul_l_icon.tex
  (skill lv 8, augments 5/4, offensive x~1.9: bleedMin 190 dur 3 / lifeMin-Max 95-150 /
   physMin-Max 100-160; bleedModifier 75; leech 90; %-currentLife 8; dodge 14;
   %-mods life 20 / str 12 / dex 14 / OA 12; defensiveBleeding 40 / defensiveLifeLeech 30;
   attack speed 20 / total speed 16 / run 20)
```

> Field-validity note (this is a SOUL, i.e. a ring/jewelry `ArmorJewelry_Ring` record): `defensiveLifeLeech`
> is VALID here (the only 3 DB records carrying it are ring-slot souls, e.g. the shipped Limos soul), so
> its use on this soul is deliberate and correct - unlike on the §3.2 armor pieces, where it was inert and
> dropped. `defensiveBleeding` is likewise valid on souls (69 soul records carry it). Every other field in
> this block is valid on souls (each field's SOUL-count in the §8 field-validity ledger is > 0).

Tags: `tagSVCSoulHemorrhage = {^F}Soul of Hemorrhage` +
`tagSVCSoulHemorrhageDESC = Toxeus, boiled down and refilled with the blood of the drowned. His
soul makes your every strike burst into a red mist that opens all wounds at once and drinks them
dry.` (Section 6 lists all tags.)

### 4.3 Summon-of-himself alternative (if Will prefers a pet over the proc)

Clone 3 pet records from Lyia Leafsong (`lyialeafsong_{1,2,3}`, the ONLY safe pet baseline;
`summon_lyia` for permanence with `spawnObjectsTimeToLive = []`), mesh
`Creatures\Monster\skeleton\revenantstorm.msh`, texture `newskeleton_crimson.tex`, race Undead,
sword/armband/ring loadout via `_set_pet_equipment` (hardcoded paths, NEVER a Monster.tpl->Pet.tpl
copy), summon skill `records\skills\soulskills\summon_bloodtoxeus.dbr` (new, collision-free).
Follows `_create_boneash_pet_skill` exactly. Skill-grant (4.1-4.2) is the recommendation because
a blood-nova-on-hit is more legible and build-defining than a summoned assassin, and it matches
how the two other Toxeus souls (SP + Main) both grant MOVES, not pets.

---

## 5. PLACEMENT (with mechanism evidence)

### 5.1 Options considered (all navmesh-verified on the deployed donors)

Measured against the generated `0x0b` donors in `local/editor_normalized/` with
`tools/debug/navlib.py` (each point's distance to the nearest walkable cell; `<2.0u` = ON-MESH):

| Option | Level (donor) | Candidate spawn (world) | On-mesh? | Fit |
|---|---|---|---|---|
| **(a) PRIMARY - beyond the mega chest** | `new_secretdoor_transitionhallway` | centroid `(4999.9, 4.0, 3467.1)`; exit-portal landing `(5047.0, 4.0, 3467.0)` = 0.14u | **ON-MESH** (largest comp 170,337 cells) | The secret hallway the `xprtl_bc2et_01` portal streams you into AFTER the exploding-blood-wall + mega chest. A guardian past the deepest door - exactly Will's ask. |
| (b) FALLBACK - Leinth finale room | `bossfight` | centroid `(3479.3, 3.4, 3177.9)`; Leinth spot `(3480, 3.0, 3165)` = 1.2u | ON-MESH (single comp, 82,703 cells) | The existing SV finale boss room. Co-locating him with Leinth is thematically tight (both blood-cult bosses) but crowds one room; kept as the safe fallback. |
| (c) mega-chest room itself | `drxBC2` | mega chest `(5284.1, 1.0, 3092.1)` = 0.00u | ON-MESH | Rejected: putting him on top of the reward chest muddies the reward beat; better he guards the room AFTER it. |

**Pick: (a)** - place Hemorrheus in `new_secretdoor_transitionhallway`, the room the secret
portal opens into. Rhymes with the exploding-blood-wall entrance, sits past the mega chest, and
is a large single walkable component with room for a boss fight + adds.

### 5.2 Exact spawn mechanism (copied from an existing boss placement)

Evidence: the Leinth finale boss is placed in `bossfight.lvl` as a single **0x05 instance of a
`Proxy` record**, flags=0, identity rotation, at SV-local coords. Parsed from the SV blob
(`local/decompiled_sv/Levels/World/xBloodCave/bossfight.lvl`, via
`build_section_surgery.parse_blob_sections`):

```
[ 4] (20.89, 2.75, 67.82) f=0  records\drxmap\proxy\q_leinth_lone.dbr      <- the boss
[ 2] (30.30, 2.76, 66.11) f=0  records\drxcreatures\theregulator\theregulator.dbr
```

`q_leinth_lone` is a `Proxy` (template `Proxy.tpl`) with `pool1 -> a ProxyPool` whose
`name1/2/3` = the 3 Leinth level variants and `nameChampion1-3` = blood demons. **Mirror its
STRUCTURE** (two deliberate field overrides, called out below). Two NEW records + one map injection:

1. **NEW proxy** `records\drxmap\proxy\q_bloodtoxeus_lone.dbr` (template `Proxy.tpl`), field-shape
   from `q_leinth_lone`: `Class=Proxy`, `baseTexture=Creatures\proxyu_boss.tex` (verbatim from donor),
   `placementExtents=3.5` (verbatim), `difficultyEquationFile=records\proxies orient\difficulty_04.dbr`
   (verbatim), `weight1=10` (verbatim), `pool1=records\drxmap\proxy\pools\q_bloodtoxeus_lone.dbr`.
   **THREE deliberate overrides vs the donor (DB-verified donor values shown):** (i) `mesh` = donor's
   `DRX\meshes\bloodwitch_leinth.msh` -> the Athens-Toxeus rig (`Creatures\Monster\Skeleton\RevenantPoison.msh`,
   Toxeus-family preview silhouette, not Leinth) and (ii) `scale` = donor's **`4.0`** -> **`2.1`**
   (Hemorrheus's size) - both preview-only (§1.3; the real spawned model is on the monster); and
   (iii) **`difficultyLimitsFile`** = donor's **`limit_area002`** -> a NEW no-cap boss limit
   **`records\proxies orient\limit_bloodtoxeus.dbr`** (windows `N/E/L = [1 .. 110]`, cloned from
   `records\proxies boss\herolimit_all.dbr`'s ProxyLimits.tpl shape).
   > **Why the limit override (CORRECTED 2026-07-07):** `limit_area002` is an area-TRASH limit whose
   > player-level windows (N[23-26] E[38-51] L[60-65]) top out BELOW Hemorrheus's `charLevel [40,68,100]`
   > on **every** difficulty. Exceeding a limit window does NOT prevent a monster from spawning (Hades
   > `charLevel[57,71,80]` via `bosslimit_all` max 75, Murder Bunny L99, and 120 monsters with L>75 all
   > spawn) - it **scales the monster's effective level DOWN toward the window**. So keeping
   > `limit_area002` would dilute the level-100 superboss to a ~65-level fight on Legendary. He is the
   > single highest-level monster in the game (L=100), above EVERY shipped limit file's max (75), so a
   > fresh no-cap file whose window CONTAINS [40,68,100] is required to fight him at his authored level.
   > (This is the "boss/no-cap limits file" the working superboss precedent uses; it is a balance/level
   > correction - the *spawn* blocker was the champion-crowd-out in item 2, not this limit.)
2. **NEW proxy pool** `records\drxmap\proxy\pools\q_bloodtoxeus_lone.dbr` (template
   `ProxyPool.tpl`), copied from `pools\q_leinth_lone.dbr` with `name1/2/3 = um_bloodtoxeus_99`
   (one record, `charLevel [40,68,100]`) and `nameChampion1-3 = b_med_blooddemon_3{0,1,2}`,
   `proxyPoolEquation=records\proxies orient\proxypoolequation_02.dbr`.
   **Boss + escort tuning (the FIX for the no-spawn bug, per the CORRECTED §2.2A):** set
   **`spawnMin=spawnMax=3, championChance=100.0, championMin=2, championMax=2`** (keep
   `weightChampion1-3=34/33/33`). This is the shipped `xsq22_wave2`/`xsq17` "boss + guaranteed champion
   escort" recipe: the `championMax=2` cap leaves `3-2=1` main-pool slot -> **exactly 1 Hemorrheus + 2
   blood-demon adds** every spawn, on N/E/L. (The ORIGINAL `spawnMin=spawnMax=1, championChance=100,
   championMin=1` converted the single spawn slot to a champion 100% of the time -> the boss got 0 slots
   and never spawned; only the blood demons did. See §2.2A for the corrected `championChance` semantics.)
3. **NEW monster** `records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr` (+ the level
   variants) - see Section 7 for the stat targets; derive by `_ensure_record` from
   `um_toxeus_99` (the closest existing kin) then override level/HP/res: this record uses
   `Monster.tpl`, so it is NOT a pet and the Monster.tpl->Pet.tpl crash rule does not apply.

**INJECT_SPECS entry** (append to `INJECT_SPECS` in `tools/build_section_surgery.py`). This is an
SV-only level -> it goes through the `inject_into_sv_only_blob` -> `inject_into_0x05` (v0x0e)
path, a plain 4-tuple `(dbr_bytes, x, y, z)`, flags=0, identity rotation - the exact shape
`q_leinth_lone` has:

```python
# Blood Toxeus (Hemorrheus) superboss guarding the secret hallway past the mega chest.
# Placed as a Proxy 0x05 instance, flags=0, identity rot - byte-shape identical to how
# SV places q_leinth_lone in bossfight.lvl. Coord is SV-LOCAL for new_secretdoor
# (the xBloodCave GRID_SHIFT is applied by the merge, NOT here; the donor navmesh was
# generated post-shift and the local point below maps to the on-mesh world centroid
# (4999.9,4.0,3467.1) verified with navlib).
Q_BLOODTOXEUS_LONE_DBR = b'records\\drxmap\\proxy\\q_bloodtoxeus_lone.dbr'
'levels/world/xbloodcave/new_secretdoor_transitionhallway.lvl': [
    (Q_BLOODTOXEUS_LONE_DBR, <local_x>, <local_y>, <local_z>),
],
```

**Coord note (must resolve at implementation):** the world centroid `(4999.9, 4.0, 3467.1)` is
POST-`GRID_SHIFT`. The `xbloodcave` shift is **`(7840, 0, 2030)`** in `svaera_plus_portals.GRID_SHIFT`
(DB/source-verified 2026-07-06; the source comment records it "was (1583,0,968); relocated to empty
map space"). NOTE: `CLAUDE.md` still cites an older `(1663,0,922)` for this shift - that value is
STALE; trust the live `svaera_plus_portals.GRID_SHIFT` (`(7840,0,2030)`), which the placement math and
the on-mesh centroid above were both derived against.
`inject_into_sv_only_blob` writes into the SV-only blob's own local 0x05 frame, so the injected
coord must be the SV-LOCAL value = `world_centroid - level_origin`, where the level's grid corner
comes from its `0x01` ints_raw (idx 6,7,8). Compute it at build time exactly as the widow/wagon
specs did (they carry SV-LOCAL coords; those levels were not grid-shifted, whereas this one is,
so subtract the level origin of the SHIFTED `new_secretdoor` index entry). A one-liner in the
implementer's script: `local = world_centroid - shifted_origin(new_secretdoor)`; then verify the
placed point round-trips back on-mesh with `navlib.Mesh(...).gx/gz`. Do NOT hardcode a guessed
local coord - derive it from the same origin the donor was generated against.

### 5.3 Reachability + gating

`new_secretdoor_transitionhallway` is reached ONLY via the quest-opened `xprtl_bc2et_01`
`GridEntranceDynamic` (opened by `open_bloodcave_portal.qst` after killing `q_highpriest_lone`
and entering `trg_open_waterdoor`; `BLOODCAVE_QUESTS_RCA` confirms the `0x14` binding resolves and
the hallway navmesh is REAL). So Hemorrheus is naturally gated behind the whole
exploding-blood-wall + mega-chest sequence with no extra quest work - killing the blood-creature
wall is already his "unlock". This is the ideal optional-superboss gating and needs no new quest.

---

## 6. IMPLEMENTATION MAP

### 6.1 DB records -> `apply_svc_patches.py` (built into `SoulvizierClassic.arz`)

Add these functions (call them from the same place the other soul builders are called, and add
the set/loot/monster/proxy builders alongside), all using `_ensure_record` (never `clone_record`
for souls; `Monster`/`Proxy`/`ItemSet`/item records may use `_ensure_record` + `set_field`):

| New builder | Creates | Derives from (EXISTS) | Notes |
|---|---|---|---|
| `_create_blood_toxeus_monster(db)` | `um_bloodtoxeus_{40,68,100}.dbr` (3 level variants, or one record with `charLevel=[40,68,100]` like `um_toxeus_21` does) at `records\xpack\creatures\monster\skeleton\` | `um_toxeus_99` | override level/HP/resist/mesh-texture/scale + `skillName*` kit (Section 2); wire loot (Section 3.3). |
| `_create_blood_toxeus_proxy(db)` | `q_bloodtoxeus_lone.dbr` + `pools\q_bloodtoxeus_lone.dbr` | `q_leinth_lone` + its pool | copy proxy fields; override `mesh`->revenantstorm + `scale`->2.1; pool `name1/2/3` = new monster; **override `championChance`->100 + `championMin`->1 + `championMax`->2** (donor is 0/0/0, §2.2A/§5.2). |
| `_create_crimsonverdict_set(db)` | `sets\svc_crimsonverdict.dbr` (single-tier L) + 12 item records (4 `svc_l_*` set members + 8 `svc_{n,e}_*` standalone) | `set004`/`set012` (single-tier set shape) + the `mi_{n,e,l}_melinoe*` items (member bases) | set-bonus per-count arrays (§3.1, NO `skillLifeBonus`/set-`defensiveBleeding`); ONLY the 4 `svc_l_*` members set `itemSetName`; N/E omit it. (Or 3 sets per §3.1b.) |
| `_create_crimsonverdict_loot(db)` | `loottables\svc\crimsonverdict_guaranteed.dbr` + `bleed_affix_high.dbr` | `supra_special.dbr` (FixedWeight SHAPE only - NOT its formulae contents) | guaranteed set-piece + high bleed table. |
| `_create_blood_toxeus_soul(db)` | `svc_uber\blood_toxeus_soul_{n,e,l}.dbr` | `_create_leinth_soul` pattern via `_create_soul` | Section 4; wires the soul onto the monster's Finger2. |

Order: monster before proxy/pool (pool references the monster), set before loot (loot references
members), soul last (wires to monster). Follow the existing convention of updating `BACKLOG` +
`CLAUDE.md` + this doc's status per the repo rules.

### 6.2 Map spawn -> `build_section_surgery.py`

- Add the `Q_BLOODTOXEUS_LONE_DBR` constant + the `new_secretdoor_transitionhallway.lvl`
  `INJECT_SPECS` entry (Section 5.2), 4-tuple, flags=0.
- Rebuild the merged map (`tools/svaera_plus_portals.py`) so the injection lands in the SV-only
  blob's 0x05; the donor navmesh for `new_secretdoor` is unchanged (we add an entity, not
  geometry), so no navmesh regen is needed. Verify the injected instance count bumps by 1 and
  the coord round-trips on-mesh.

### 6.3 Tags -> `Text.arc`

Author every new tag into the root `uber_soul_tags.txt` (the `uber_tags_path` source of truth
that `build_text_arc.py:collect_mod_authored_tags` unions in; gated by `tools/validate_tags.py`).
Consolidated list to paste:

```
tagMonsterHemorrheus={^r}Hemorrheus, the Red Verdict
tagSVCSoulHemorrhage={^F}Soul of Hemorrhage
tagSVCSoulHemorrhageDESC=Toxeus, boiled down and refilled with the blood of the drowned. His soul makes your every strike burst into a red mist that opens all wounds at once and drinks them dry.
tagSVCSetCrimsonVerdict=The Crimson Verdict
tagSVCwpnVeinRender={^r}Vein-Render
tagSVChlmCrimsonVerdict={^r}Cowl of the Red Verdict
tagSVCtorCrimsonVerdict={^r}Sanguine Shroud
tagSVCarmCrimsonVerdict={^r}Hemorrhage Bindings
```

(If the summon alternative in 4.3 is built, also add `tagSVCSummonHemorrhage={^F}Summon Hemorrheus`
+ its DESC.) The monster's `description` field = `tagMonsterHemorrheus`.

### 6.4 Validation gates (all must pass before deploy)

- `tools/validate_tags.py` PASS (every new name/desc tag resolves in `Text.arc`).
- DB build (`tools/build_svc_database.py`) succeeds; re-open the built `.arz` and assert:
  every new record present; `blood_toxeus_soul_*` grant `melinoe_bloodboil` + the two verified
  augments resolve (no dangling augment - re-check `drxopenwound` + `drxdeathchillaura_ravagesoftime`
  resolve, per `BOSS_SOULS_DESIGN` Section 0's augment-path trap); the monster's `lootFinger2Item1`
  points at the 3 soul paths; the set's `setMembers` all resolve and each member's `itemSetName`
  points back at the set.
- **DEAD-FIELD GUARD (added after the field-validity audit; assert against the built `.arz`):**
  (a) NO `svc_*` equipment item or the `svc_crimsonverdict` set record carries `skillLifeBonus`
  (skill-only field; would ship inert) - use `characterLife` instead;
  (b) NO `svc_*` equipment ITEM carries `defensiveLifeLeech` (inert on armor; 0 valid item records in
  the DB) - it is allowed ONLY on the soul (`blood_toxeus_soul_*`, a ring/jewelry record);
  (c) the `svc_crimsonverdict` SET record carries NO `defensiveBleeding` (not an ItemSet field) -
  set-level bleed-resist must not be authored; per-piece `defensiveBleeding` is fine;
  (d) every field written on the set BONUS is one DB-verified as carried by real ItemSet records
  (the §3.1 list). A 6-line assertion script over the built `.arz` catches all four.
- **SPAWN-ELIGIBILITY GUARD (fail-loud, `_verify_mod_spawn_proxies_eligible`; replaces the earlier
  "CHAMPION-POOL GUARD" which was itself wrong - it asserted `championChance > 0`, the exact setting that
  crowded the boss out):** for every mod-authored spawn proxy assert BOTH: (a) **champion-crowd-out** -
  guaranteed main slots `= spawnMax - championMax` (when `championChance > 0`) must be **>= 1**, so the
  boss (`name1-3`) always claims a spawn slot and is never fully replaced by `nameChampion*` adds
  (the 2026-07-07 no-spawn root cause: `spawnMax=1, championChance=100, championMax=2 -> -1 main slots`);
  and (b) **limit-window containment** - the main monster's `charLevel` must be `<= difficultyLimitsFile`
  window max (and `>= min`) on **N/E/L**, so the boss is never scaled below his authored level
  (`um_bloodtoxeus_99` [40,68,100] vs `limit_bloodtoxeus` [1..110] passes all three). Negative-tested:
  the gate fails loud on the old `championChance=100/spawnMax=1` + `limit_area002` config with 4 problems.
- Map: `new_secretdoor_transitionhallway` 0x05 instance count = baseline+1; injected local coord
  maps to a walkable cell (`navlib.Mesh(...).gx/gz` in `.cells`); donor `0x0b` byte-identical
  (unchanged) via `tools/verify_merged_bc_navmeshes.py`.
- In-game (the one thing static checks cannot replace, per `AREA_WIRING_RECIPE` Phase E): fresh
  Custom Quest character, run the exploding-blood-wall sequence (kill `q_highpriest_lone` ->
  `trg_open_waterdoor` -> `xprtl_bc2et_01` portal -> secret hallway), confirm Hemorrheus spawns,
  fights with Blood Boil + adds, and drops the soul + a Crimson Verdict piece.

---

## 7. POWER BASELINE + TARGETS (quantified from the DB)

Measured directly from the built `.arz` (2026-07-06):

| Metric | Athens Toxeus `um_toxeus_21` (Boss) | SP Toxeus `um_toxeus_99` (Hero) | **HEMORRHEUS target** |
|---|---|---|---|
| Levels (N/E/L) | 25 / 45 / 65 | 33 / 66 / 99 | **40 / 68 / 100** |
| Life (N/E/L) | 3966 / 5156 / 6346 | 9324 / 11655 / 13986 | **13000 / 18000 / 24000** |
| Strength | 319 | 419 | **480** |
| Dexterity | 439 | 599 | **660** |
| Intelligence | 179 | 379 | **420** |
| Life regen | 3 | 5 | **10** (blood-drinker) |
| Hand dmg min-max | 31-73 | 31-73 | **60-120** (bigger blades) |
| Resist: Life% | 100 | 100 | **100** |
| Resist: Poison | 100 | 100 | **80** (blood, not poison - a deliberate, slightly lower pin so he is NOT just green Toxeus; his identity is bleed) |
| Resist: Pierce | 50 | 60 | **70** |
| Resist: Bleeding | (none) | (none) | **80** (his signature wall - neither Toxeus resists bleed; Hemorrheus does, via the blood-witch `zpassive_resists_bleedvitleechconvert` passive) |
| Signature damage | phys + poison envenom + bladestorm | phys + electrocution (Distort Reality) + Dream | **phys + BLEED + VITALITY + life-leech** (Blood Boil nova + bleeding bladestorm + life drain) |
| Own soul | `toxeus_soul_*` (Main, Tier 3) | `sp_toxeus_soul_*` (Tier 1, "strongest in game") | `blood_toxeus_soul_*` (new; itemLevel 40/68/100) |

**Out-classing is explicit and multi-axis:** Hemorrheus beats the Athens Toxeus on level (+15
N-tier), life (**~3.3x** at N, **~3.8x** at L), all three attributes, hand damage, and pierce
resist, AND adds an entire bleed/vitality damage identity + a bleed-resistance wall the Athens
boss lacks. He also edges past the SP super-variant (higher N-tier level 40 vs 33, higher L HP
24000 vs 13986, higher attributes, +bleed wall), positioning him as the **hardest Toxeus in the
mod** - justified because he is a HIDDEN end-of-secret-area guardian (gated behind the whole
exploding-blood-wall + mega-chest run), the natural place for the toughest fight. His soul is
tuned to sit alongside SP Toxeus's Tier-1 soul in raw power but with a distinct bleed/vitality
profile (Blood Boil + Open Wound + Ravages of Time) rather than SP's electrocution/Dream profile,
so it is a genuine new build-defining option, not a strictly-better clone.

---

## 8. Record-existence ledger (what was DB-verified for this design)

EXISTS (verified in the built `.arz`, 2026-07-06) - full paths, corrected:
- Monsters/proxies:
  - **Athens Toxeus** `records\creature\monster\skeleton\um_toxeus_21.dbr` (`Monster`) - NOTE the real
    path is under **`creature\`, NOT `xpack\`** (the earlier ledger implied an xpack neighbourhood; that
    was imprecise). This is the baseline the boss must out-class; the NEW monster still DERIVES from
    `um_toxeus_99`, which IS under xpack, so nothing about the build breaks.
  - **SP Toxeus** `records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr` (`Monster`, under xpack).
  - `q_leinth_lone` (+ its `ProxyPool`), `q_highpriest_lone` (+ pool), `c_disciple_miniboss`,
    `b_med_blooddemon_3{0,1,2}`, `t1_lildude_0{1,2,3}`, `t1_skill_pitspawner_summonlildude_0{1,2,3}`.
- Skills/procs: `melinoe_bloodboil` (Skill_AttackRadius), `lifedrain` (Skill_AttackSpellChaos),
  `toxeus_bladestorm`, `toxeus_envenomweapon`, `flashpowder`, `lethalstrike`(+mortalwound,
  openwound), `drxopenwound`, `drxanatomy`, `drxdeathchillaura_ravagesoftime`, `drxenvenomweapon`,
  `drxlethalstrike`, `drxdarkcovenant`, `xpack\...\drxphantomstrike`, `xpack\...\drxdistortionwave`,
  `zpassive_resists_bleedvitleechconvert_x10plvl`, `boss_conversionimmunity`, `hero_scaling`,
  `toxeus_passiveproperties`, `summon_lyia`, `lyialeafsong_{1,2,3}`.
- Controllers: `_AC_ON_HIT` (base_atself_onanyhit), `_AC_ON_ATTACK`, `_AC_LOW_HEALTH`.
- Assets (referenced by shipped records, so resolve in the arcs): mesh `revenantstorm.msh`;
  texture `newskeleton_crimson.tex`; `Creatures\proxyu_boss.tex`.
- Item/set infra: `set004` (+ the whole `sets\` catalog, DB-verified **142 set records** total),
  `records\xpack\item\loottables\arcaneformulae\supra_special.dbr` (`LootItemTable_FixedWeight`, 25
  weight-100 `lootName*` entries = the 25 Supra CRAFTING FORMULAE; used ONLY as a fixed-weight SHAPE
  donor - it is NOT the mega-chest's own reward table, corrected from the earlier label), the
  `mi_{n,e,l}_melinoe` (sword/spear) + `mi_{n,e,l}_melinoemage` (helm/torso/armband/greaves) bases.
- **Field-validity (DB-audited by category - the load-bearing correction of this revision):**
  - Valid on ITEMS + SETS + SOULS (safe everywhere used): `offensiveSlowBleedingMin/Modifier`,
    `offensiveSlowBleedingDurationMin/Modifier`, `offensiveLifeMin/Max/Modifier`, `offensiveLifeLeechMin`,
    `offensivePierceRatioModifier`, `offensivePercentCurrentLifeMin`, `characterLife/Modifier`,
    `characterAttackSpeedModifier`, `characterStrength/Dexterity/Intelligence/ManaModifier`,
    `characterOffensive/DefensiveAbility`, `characterLifeRegen`, `defensiveLife`, `defensivePhysical`,
    `retaliationSlowBleedingMin/DurationMin`, `itemSetName`, `setMembers`, `setName`.
  - Valid on ITEMS + SOULS but NOT sets: `defensiveBleeding` (67 items, 69 souls, **0 sets**).
  - Valid on SOULS (ring/jewelry) but NOT armor/weapon items: `defensiveLifeLeech` (**0 items**, 3
    ring-slot soul records only, e.g. the Limos soul).
  - **SKILL-ONLY (inert on ALL gear - never author on items/sets/souls):** `skillLifeBonus` (0 items,
    0 sets, 0 souls, 107 Skill_* records). Replaced by `characterLife` everywhere it was used.

DANGLING / DO NOT USE (verified MISS - matches `BOSS_SOULS_DESIGN` Section 0):
- `records\skills\dream\drxravagesoftime.dbr` (use `spirit\drxdeathchillaura_ravagesoftime`).
- `records\skills\dream\drxphantomstrike.dbr` (use `xpack\skills\dream\drxphantomstrike`).
- `records\skills\spirit\drxxsanguine.dbr` (no such record; not used).

NEW (created by this design; all collision-checked free):
- `um_bloodtoxeus_*` monster(s), `q_bloodtoxeus_lone` proxy + pool,
  `sets\svc_crimsonverdict` (single-tier L set) + 12 item records (4 `svc_l_*` = set members with
  `itemSetName`; 8 `svc_{n,e}_*` = standalone bleed pieces, no `itemSetName`) - OR, if §3.1b is chosen,
  3 set records `svc_crimsonverdict_{n,e,l}` + 12 members each pointing at their own tier's set,
  2 loot tables, `svc_uber\blood_toxeus_soul_{n,e,l}` + (optional) `summon_bloodtoxeus` + pets, and
  the 8 tags.

---

## 9. INDEPENDENT CRITIC VERDICT + REVISION LOG (max-effort review, 2026-07-06)

An adversarial pass re-derived every load-bearing claim from the built `.arz`
(`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, **50,327 records**) and the deployed donor
navmeshes. **Overall: the design is feasible and implementable, the power math is sound, and the
placement is navmesh-verified. No blocker-severity defect was found; the issues were wrong stat-field
placements (silently inert in-game) + several path/label inaccuracies.** **All critique issues are now
RESOLVED in this revision** (see the REVISION LOG below); §§1-8 above already carry the fixes. Detail:

### Confirmed correct (high-value)
- **Power baseline (§7): numerically exact.** `um_toxeus_21` (Athens, Boss) = Lv[25,45,65],
  Life[3966,5156,6346], STR/DEX/INT 319/439/179, regen 3, hand 31-73, poison 100, pierce 50, life
  100, **no bleed resist** - all verified. `um_toxeus_99` (SP, Hero) = Lv[33,66,99],
  Life[9324,11655,13986], 419/599/379, pierce 60 - verified. Classifications (Boss / Hero) correct.
  Hemorrheus at 13000-24000 HP is sane: 329 of 4547 DB monsters already exceed 13k and Murder Bunny
  (an existing uber-soul boss) is 275k, so he is measurably above both Toxeus yet nowhere near
  unkillable-sponge territory.
- **Signature payload (§2.1): exact.** `melinoe_bloodboil` = `Skill_AttackRadius`,
  `offensiveLifeMin`[246..605], `offensiveSlowBleedingMin`[148..328], bleed dur 2.0, life-leech 100,
  radius 8.0 - all as cited.
- **Placement (§5): navmesh-verified.** `new_secretdoor_transitionhallway.lvl.0b.bin` donor: 170,373
  cells, **largest component 170,337 (matches doc to the cell)**; centroid (4999.9,4.0,3467.1) =
  **0.0u on-mesh**; exit-portal landing (5047.0,4.0,3467.0) = **0.14u on-mesh**. `bossfight.lvl` 0x05
  really lists `q_leinth_lone.dbr` (index 4) + `theregulator.dbr` (index 2) as the doc states; it is
  a `Proxy` (template `Proxy.tpl`) with `pool1 -> ProxyPool` (`name1/2/3` = Leinth variants,
  `nameChampion1-3` = blood demons). `GRID_SHIFT['xbloodcave'] = (7840,0,2030)` matches the live
  source. The SV-local-vs-world coord caveat in §5.2 is correct and the right call (derive at build).
- **Crash-rule / augment discipline: sound.** `drxopenwound` (Skill_Modifier) and
  `drxdeathchillaura_ravagesoftime` (Skill_Modifier, `spirit\`) both resolve; the dangling
  `drxravagesoftime` / `drxphantomstrike(skills\dream)` / `drxxsanguine` all confirmed MISS. The
  shipped SP-Toxeus soul's `augmentSkillName2 = skills\dream\drxdistortionwave.dbr` confirmed
  **dangling (resolves=False)** - the doc's warning is accurate and it correctly avoids that trap.
  `_create_soul` (`apply_svc_patches.py:1337`) really writes to `_SOUL_DIR = ...\svc_uber` and wires
  `lootFinger2Item1` + `chanceToEquipFinger2` + `chanceToEquipFinger2Item1=100` on the monster,
  exactly as §3.3/§4.1/§6.1 assume. Leinth soul exemplar confirmed at `svc_uber\leinth_soul_*`
  (bloodboil proc + `base_atself_onanyhit`). Chimera/Hydra no-controller summon precedent confirmed
  (`soul\chimera\chimera_soul_*`, controller=None).
- **Derive-from bases: all present, all tiers.** `mi_{n,e,l}_melinoe` (sword, WeaponMelee_Sword) and
  `mi_{n,e,l}_melinoemage` (helm/torso/armband, ArmorProtective_Head/UpperBody/Forearm) ALL exist
  across n/e/l. `set004` set-bonus-as-per-count-array encoding confirmed (`characterLife =
  [0,42,45,45,100]`). `itemSetName` back-link confirmed real on set members (points at `sets\drxset*`).
  Blood demons, pit-sprites (`t1_lildude_*`, `t1_skill_pitspawner_summonlildude_*` =
  Skill_SpawnPetMonster, petBurstSpawn=1, petLimit=3, spawns `t1_lildude_*`), all controllers, art
  strings (`revenantstorm.msh`, `newskeleton_crimson.tex`, `proxyu_boss.tex`), and all 11 NEW record
  paths (collision-free) verified.

### REVISION LOG - every critique issue addressed (each re-verified against the built `.arz`)

**[major] Issue 1 - three fields on classes that do not support them -> RESOLVED (plus a 4th caught).**
Re-ran a per-category field-validity audit over all 50,327 records (classifying every record as
ITEM / SET / SOUL / SKILL and counting which carry each field):
- **`skillLifeBonus` is SKILL-ONLY** - DB-proven **0 items, 0 sets, 0 souls, 107 Skill_* records** (the
  4 non-`\skills\`-path hits are also all Skill_* classes: a `test_shadowstalker` Skill_GiveBonus + 3
  `drxdishonorguard` Skill_BuffSelfDuration). FIXED: replaced with **`characterLife`** on the §3.1 set
  bonus (`[0,150,300,600]`), the Vein-Render weapon (250), and the Sanguine Shroud torso (folded into
  `characterLife 850`). `characterLife` verified on 6171 items + 142 sets.
- **`defensiveBleeding` is not an ItemSet field** - DB-proven **0 of 143 set records** carry it; absent
  from the 603-field set union. FIXED: DROPPED from the §3.1 set bonus. It stays on the §3.2 armor
  pieces + the §4.2 soul, where it is valid (67 items + 69 souls carry it; `u_l_painweaver`=55 confirmed).
- **NEW find the critique missed - `defensiveLifeLeech` is inert on armor.** DB-proven **0 equipment
  items** carry it; the only 3 records are ring-slot souls (incl. the Limos soul). The earlier draft put
  `defensiveLifeLeech=30` on the Sanguine Shroud TORSO (§3.2) - that would ship inert. FIXED: dropped
  from the torso (the "resist leech" intent carried by the valid `defensiveBleeding`+`defensiveLife`);
  KEPT on the §4.2 soul, which is a ring/jewelry record like the 3 valid precedents.
- The boss's own bleed WALL (§7) was never at risk (it is the `zpassive_resists_bleedvitleechconvert`
  passive, not a set). Every field remaining on the §3.1 set bonus was individually confirmed present on
  real ItemSet records (142/142 for most; 12/142 for `offensiveLifeLeechMin`).

**[major] Issue 2 - cross-difficulty SET encoding is not how SV sets work -> RESOLVED.** Re-verified all
142 set records: each is purely single-tier (`set002`=5x epic `us_e_legendoffuxi`; `set004`=5x `us_n_`;
`set012`=5x `us_l_`); the lone `drxset026` e/l 3-piece is an upstream oddity, and there is NO
`xxx_{n,e,l}.dbr` set trio. FIXED: §3.1 now commits to a **single-tier Legendary set** (the `svc_l_*`
pieces only; N/E are standalone bleed gear with no `itemSetName`), matching every shipped set; §3.1b
documents the three-set (`svc_crimsonverdict_{n,e,l}`) alternative if Will wants n/e/l completion. The
"SV set members already ship as n/e/l variants (e.g. set002 `us_e_legendoffuxi`)" misread is removed
(set002 is all-epic, single-tier).

**[minor] Issue 3 - ledger path errors + mislabels -> RESOLVED.**
- Athens Toxeus real path is `records\creature\monster\skeleton\um_toxeus_21.dbr` (NOT under `xpack`) -
  §8 corrected; still derives the new monster from `um_toxeus_99` (which IS xpack), so nothing breaks.
- `supra_special` is `records\xpack\item\loottables\arcaneformulae\supra_special.dbr`, a
  `LootItemTable_FixedWeight` of 25 Supra CRAFTING FORMULAE (verified contents = `...\supra\recipes\ar_*`);
  it is NOT the mega-chest reward table. §3.3/§6.1/§8 corrected to use it ONLY as a fixed-weight SHAPE donor.
- `openwound` is Class `Skill_Passive` (not "modifier"); §2.1 corrected. The SOUL augment correctly uses
  the real `Skill_Modifier` record `drxopenwound` (a different record) - unchanged.

**[minor] Issue 4 - proxy champion adds need explicit pool tuning (not just weights) -> RESOLVED.** Both
donor pools `pools\q_leinth_lone` and `pools\q_highpriest_lone` are DB-verified as
`championChance=0.0, championMin=0, championMax=0` (champions never spawn despite `nameChampion1-3`
being set). §2.2A + §5.2 now require the new pool to set **`championChance=100.0, championMin=1,
championMax=2`** in addition to `weightChampion1-3`, and a validation gate (§6.4) asserts
`championChance>0 AND championMax>=1`. The critique's flagged proxy divergence (donor proxy `scale=4.0`
+ `mesh=bloodwitch_leinth` vs the doc's `scale=2.1` + `revenantstorm`) is now explicitly documented as a
deliberate preview-only choice in §1.3 + §5.2 (the real model is on the spawned monster, not the proxy).

**Bonus factual fix:** the doc's `GRID_SHIFT['xbloodcave'] = (7840,0,2030)` was re-confirmed against
live `svaera_plus_portals.py` (source comment: "was (1583,0,968)"); a note now flags that `CLAUDE.md`'s
older `(1663,0,922)` for this shift is STALE, so the implementer trusts the doc's (correct) value.

### Taste (unchanged - the fixes are field-plumbing, the creative core stands)
Meets the BOSS_SOULS_DESIGN bar: signature-first (Blood Boil hemorrhage-nova), two on-theme augments
(Open Wound + Ravages of Time), a full bleed/vitality/leech offensive suite, %-mods, a themed defensive
line, and real flavor callbacks (drinks-what-it-bleeds leech, exploding-blood-sprite low-health phase
that rhymes with the secret-wall fight, bleed wall neither Toxeus has). It is a genuine blood-CREATIVE
kit built from real records, not a stat-stick reskin. With the dead-field placements corrected and the
set encoding pinned to how SV sets actually work, the set now delivers its full stated bonus in-game and
there is no remaining gap between the vision and what applies.
