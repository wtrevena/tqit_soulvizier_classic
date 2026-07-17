# SV 0.98i Mastery Trees - Ground Truth (machine-verified)

**Author:** SV MASTERY GROUND-TRUTH EXTRACTION lane (read-only recon). **Method:** pure-Python `arz_patcher` / `arc_patcher` / `tex_decode` replay; no game, no build.

**Authority (tree layout):** `upstream/soulvizier_098i/Database/database.arz` (SV 0.98i, 51,186 records).  
**Names:** `upstream/soulvizier_098i/Resources/Text_EN.arc` (14,657 tags).  
**Vanilla reference (emblem circle):** base-game TQAE `database.arz` + `InGameUI.arc`.  
**Deviation base:** `local/baseline_build41.arz` (md5 eb8bc377 - what the parallel revert restores).  
**Emblem current state:** `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (shipped build).

Machine-readable companion: **`tools/sv_mastery_ground_truth.json`** (every field, per skill, per mastery).

> Derived **only** from SV 0.98i's OWN records. The vanilla-6-tier invariants in `mastery_ui_invariants.md` were NOT assumed - SV's 7-row ladder is re-derived below and happens to extend the same 62 px pitch to a 7th row.

---

## 0. Two framing facts the fix lane MUST read first

**(A) SV098 Occult is the reskinned base ROGUE mastery.** SV 0.98i "Occult" = the base-game Rogue tree with DRX display-name reskins (Poison Gas Bomb -> "Poisonous Gas", Open Wound -> "Dark Invigoration", Anatomy -> "Shadow Lore", Lay Trap -> "Breach", Blade Honing -> "Shadow Link", Calculated Strike Lucky Hit -> "Blade Fury", ...). It has **no** Darklings / Dark Aperture / Toxic Concoction / Shadow Stalker - those are **SVAERA-era** skills that Will's build41 overlay ADDED. So Will's Occult anchors describe a MIX of SV098 ground truth and his build41 overlay (see section 5).

**(B) build41 is a SUPERSET of SV098 in ALL 9 masteries.** build41 (the revert target) is a SUPERSET of SV098 in ALL 9 masteries: it ADDS coherent, intentional restored skills to every tree (Meteor, Force of Nature, Skeletal Soldier, Sands of Sleep, Distortion Wave, Cleave, Cold Aura, Bone Fiend, etc.) and REMOVES nothing. SV098's placed trees (20 skills each, 24 for Dream) are a SUBSET. 'Match SV098 exactly' therefore must NOT mean blanket roster deletion - that would gut the mod's whole legacy-skill restoration. Use SV098 as the authority for LAWS (7-row geometry, isCircular shape encoding, connOn/Off connector mechanism) and for the placement/shape/connector of SV-shared skills; treat build41 additions as intentional and re-fit them to SV's laws.

---

## 1. Row geometry (SV's OWN ladder) + column lattice

Every distinct `bitmapPositionY` in SV098 maps to exactly ONE `skillTier` (0 violations across all 9 masteries). SV uses **7 rows** - the vanilla 6-row `62 px` ladder extended by a 7th row at `Y=31`.

| tier (row) | `bitmapPositionY` | point threshold |
|---|---|---|
| 1 | 403 | 1 |
| 2 | 341 | 4 |
| 3 | 279 | 10 |
| 4 | 217 | 16 |
| 5 | 155 | 24 |
| 6 | 93 | 32 |
| 7 | 31 | 40 |

`Y = 465 - 62*tier` (row pitch = 62 px). Point thresholds = the mastery level required to UNLOCK each tier row: **1 / 4 / 10 / 16 / 24 / 32 / 40**. (`skillMasteryLevelRequired` is a per-skill gate that varies WITHIN a row and must NOT be used to derive the row - the row is `skillTier`/`Y`.)

**Columns:** `bitmapPositionX in {128, 228, 328, 428, 528, 628}` = columns 1-6, pitch 100 px, first at 128. **Mastery button** sits off-grid at (29, 459), `isCircular=1`.

---

## 2. Frame shape (circle vs square) - the encoding

The skill BUTTON record (skillNN.dbr) field `isCircular`: 1 = round frame (passive / proc / augment / summon skills), 0 = square frame (actively-cast skills). Set explicitly per button; NOT mechanically tied to base-vs-modifier record-name status (e.g. Blade Fury is a name-modifier of Calculated Strike yet is square).

- **circle** = `isCircular=1` (round frame) - passives, procs, augments/modifiers, summons.
- **square** = `isCircular=0` (square frame) - actively-cast skills.

The field lives on the **button** record (`skillNN.dbr`), not the skill record. It is set by hand, so a record that is a name-modifier can still be a square (e.g. SV098 **Blade Fury** = `DRXCalculatedStrike_LuckyHit`, a modifier by name, but `isCircular=0` = square) and a base can be a circle. Do not infer shape from base/modifier status - read `isCircular`.

---

## 3. Connection mechanism (record-driven bars, NOT baked art)

A connector is a RUNTIME vertical bar built from the SKILL record's parallel string arrays skillConnectionOn (invested) / skillConnectionOff (planning), ALWAYS equal length. skillConnectionSpacing=62 = one row pitch. The bar sits on the family BASE (bottom, largest Y) and draws UPWARD; tiles bottom->top are SkillBarBottom / (Middle=empty row | Connect=occupied row) / SkillBarTop. A straight bar stays in the same column; a `_right` bar (SkillBar*On01_right.tex, shipped by SV) rises up-and-right into the column to the right (x+100). Leaf/standalone skills carry no bar (empty arrays).

- **Baked into the background `.tex`?** **NO.** Decoded SV/base <Class>SkillBackground01.tex panes carry ONLY the 6-7 tier shelf grooves + frame + the two mastery-art holes (circle emblem + panel); ZERO baked skill-to-skill connector lines. Connectors are 100% record-driven.
- **`_right` variant in SV098?** YES - SV 0.98i itself references `SkillBar{Bottom,Middle,Top}On01_right.tex` (e.g. Occult Shadow Grasp and Nether Strike), so the diagonal riser is NOT a mod-only asset.

Bar tile alphabet used in the trees below: `B`=Bottom `M`=Middle(empty row) `C`=Connect(occupied row) `T`=Top; a trailing `R` = the `_right` (up-and-right) variant. Bar length = number of tiles = rows spanned from the base upward.

---

## 4. The top-right circle ("black disc") - RCA + exact fix

**Element:** top-right circular mastery portrait on the skill-TREE pane.

**Mechanism.** The <Class>SkillBackground01.tex pane background (919x540) has a black CIRCULAR HOLE in its top-right corner (decoded from base InGameUI.arc). panectrl.dbr::skillPaneMasteryBitmap -> masterybitmap.dbr draws the round 175x175 mastery portrait ON TOP of that hole at pane-local (718,31). If the portrait record fails to render, the black hole shows through = 'black disc'.

**Root cause.** The engine's skillPaneMasteryBitmap slot (like skillPaneBaseBitmap) reads a BitmapUIAware widget's PLURAL bitmapNames array. A BitmapSingle record's singular bitmapName is ignored by that slot -> emblem never draws -> the background's black circular hole is exposed = the black disc. Same bug class b60 already proved+fixed for the pane backgrounds; the emblem was left out.

- Vanilla: masterybitmap.dbr = BitmapUIAware.tpl, bitmapNames=[<Panel01>,<Panel01>] (the panel listed twice), bitmapPositionsX=[718,748], bitmapPositionsY=[31,31]. Renders.
- SV098: masterybitmap.dbr CONVERTED to BitmapSingle.tpl with a SINGULAR bitmapName (m5 -> DRXtextures\masterybackdrops\newstealthpanel01.tex, others -> base panel).
- Our build: masterybitmap.dbr is STILL BitmapSingle.tpl in the shipped work arz for ALL 9 masteries. The b60 mastery_bg_render fix converted the pane BACKGROUND records (skillpanebasebitmap + skillpanereallocationbitmap) BitmapSingle->BitmapUIAware so the grid renders, but it NEVER touched masterybitmap.dbr (the emblem).

**Exact fix (per mastery).** For each mastery's masterybitmap.dbr: templateName -> BitmapUIAware.tpl; FileDescription -> BitmapUIAware; bitmapNames -> [<current bitmapName>, <same>]; bitmapPositionsX -> [718,748]; bitmapPositionsY -> [31,31]; drop singular bitmapName/bitmapPositionX/bitmapPositionY. Keep the existing texture (all resolve).

| mastery | current `masterybitmap.dbr` template | texture (resolves) |
|---|---|---|
| Warfare | BitmapSingle.tpl | `InGameUI\Skills\WarfarePanel01.tex` |
| Defense | BitmapSingle.tpl | `InGameUI\Skills\DefensePanel01.tex` |
| Earth | BitmapSingle.tpl | `InGameUI\Skills\EarthPanel01.tex` |
| Storm | BitmapSingle.tpl | `InGameUI\Skills\StormPanel01.tex` |
| Occult | BitmapSingle.tpl | `DRXtextures\masterybackdrops\newstealthpanel01.tex` |
| Hunting | BitmapSingle.tpl | `InGameUI\Skills\HuntingPanel01.tex` |
| Spirit | BitmapSingle.tpl | `InGameUI\Skills\SpiritPanel01.tex` |
| Nature | BitmapSingle.tpl | `InGameUI\Skills\NaturePanel01.tex` |
| Dream | BitmapSingle.tpl | `XPack\UI\Skills\DreamPanel01.tex` |

All 9 textures already resolve in the shipped arcs (base `InGameUI.arc` for m1-4/6-8, `DRXtextures.arc` for m5's `newstealthpanel01.tex`, base XPack for m9's `DreamPanel01.tex`); the ONLY change needed is the record STRUCTURE (BitmapSingle -> BitmapUIAware), mirroring the already-shipped b60 `mastery_bg_render` background fix but applied to the emblem slot it missed. Emblem geometry is `bitmapPositionsX=[718,748]`, `bitmapPositionsY=[31,31]` (NOT `[0,0]` like the pane background).

---

## 5. Anchor validation (Will's memory of SV Occult)

| # | anchor | verdict |
|---|---|---|
| 1 | Smoke Screen is standalone, connects to NOTHING, never near Breach | **CONFIRMED** |
| 2 | Breach connects to Shadow Grasp directly | **CONFIRMED** |
| 3 | Toxic Concoction - Poisonous Gas - Aphotic Ichor form a connected chain | **CONTRADICTED (SV098) / build41-overlay** |
| 4 | Poisonous Gas is a circle | **CONFIRMED (SV098) / build41 REGRESSED** |
| 5 | Dark Invigoration sits in Shadow Link's column, connected at the 16-point row | **PARTIAL: position CONFIRMED, 'connected' CONTRADICTED (SV098)** |
| 6 | Darklings + Dark Aperture are NOT in Shadow Link's column | **CONTRADICTED by build41 (candidate fix)** |
| 7 | Dark Aperture is a circle augmenting Darklings | **CONFIRMED (build41 overlay)** |
| 8 | Blade Fury is a square | **CONFIRMED (SV098) / build41 REGRESSED** |

1. SV098: Smoke Screen c1t3 square, bar_len=0 (no connector); Breach c4t3 (different column). 
2. SV098: Breach c4t3 straight bar len=3 -> ['drxlaytrap_rapidconstruction'] (t4 empty between = 'directly').
3. SV098: Toxic Concoction (drx_scrap) is ABSENT from Occult; Poisonous Gas c1t5 and Aphotic Ichor c1t7 sit in col1 but carry NO connector bars (unconnected in SV098). The chain exists only in build41, where Will's overlay ADDED Toxic Concoction at c1t4 - this anchor describes the build41 INTENDED overlay, not SV098 ground truth.
4. SV098: Poisonous Gas isCircular=1 (circle). build41 FLIPPED it to SQUARE (isCircular=0) - a real bug to fix.
5. SV098: Shadow Link (drxbladehoning) c3t2 and Dark Invigoration (drxopenwound) c3t4 share column 3; Dark Invigoration is at tier 4 = the 16-point row. BUT SV098 column 3 has NO connector bars, so nothing draws a connection there. In build41 the overlay inserts Darklings (c3t3) + Dark Aperture (c3t5) into this column - see anchor 6.
6. SV098: Darklings and Dark Aperture do NOT EXIST in Occult (SVAERA skills). build41's overlay PLACED them in column 3 (Darklings c3t3, Dark Aperture c3t5) = Shadow Link's column - which this anchor forbids. FIX-LANE ACTION: move the Darklings/Dark Aperture family OUT of column 3 into its own column (keeping the two together, Dark Aperture above Darklings).
7. SV098: both absent. build41: Dark Aperture (drxdarklings_darkaperture) isCircular=1 (circle), record name is a modifier of Darklings (drxdarklings). Augment relation + circle shape correct.
8. SV098: Blade Fury isCircular=0 (square). build41 FLIPPED it to CIRCLE (isCircular=1) - a real bug to fix.

---

## 6. Per-mastery SV098 trees (ASCII grid + skill table + connections)

Grid: columns 1-6 left->right, tier 7 (top of screen) down to tier 1. `[name]`=square, `(name)`=circle. A `*` after a name = the skill carries a connector bar (see the connection list).

### m1 Warfare - `Warfare Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 .             .             .             (Ardor)       .             [Ancestral Hor]
t6 (Tumult)      (Counter Attac)(drxbattlestan).             .             (Doom Bond)
t5 .             .             .             .             .             .
t4 (Cross Cut)   (Crushing Blow).             .             (Lacerate)    [Lineal Chains]*
t3 (Hew)         .             [Battle Standa]*.             .             [War Horn]
t2 (Parry)       (Battle Rage)*.             (Ignore Pain) [War Dance]*  .
t1 (Dual Wield)* .             .             [Onslaught]*  .             (Weapon Traini)
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t1 | Dual Wield | circle | 0 | BasicAttack | `drxdualweapontraining` |
| c1 t2 | Parry | circle | 0 | Passive | `drxdodge attack` |
| c1 t3 | Hew | circle | 0 | BasicAttack | `drxdualwieldtechnique_jumpslash` |
| c1 t4 | Cross Cut | circle | 24 | BasicAttack | `drxdualwieldtechnique_crosscut` |
| c1 t6 | Tumult | circle | 30 | BasicAttack | `drxdualwieldtechnique_tumult` |
| c2 t2 | Battle Rage | circle | 0 | PassiveOnHitBuffSelf | `drxbattlerage` |
| c2 t4 | Crushing Blow | circle | 10 | Modifier | `drxbattlerage_crushingblow` |
| c2 t6 | Counter Attack | circle | 15 | Modifier | `drxbattlerage_counterattack` |
| c3 t3 | Battle Standard | square | 0 | SpawnPet | `drxbattlestandard` |
| c3 t6 | *(drxbattlestandard_petmodifier_triumph) | circle | None | PetModifier | `drxbattlestandard_petmodifier_triumph` |
| c4 t1 | Onslaught | square | 1 | ChargedLinear | `drxonslaught` |
| c4 t2 | Ignore Pain | circle | 0 | Modifier | `drxonslaught_ignorepain` |
| c4 t7 | Ardor | circle | 0 | Modifier | `drxonslaught_ardor` |
| c5 t2 | War Dance | square | 15 | AttackWeaponCharge | `drxwarwind` |
| c5 t4 | Lacerate | circle | 25 | Modifier | `drxwarwind_lacerate` |
| c6 t1 | Weapon Training | circle | 1 | Passive | `drxweapontraining` |
| c6 t3 | War Horn | square | 5 | AttackRadius | `drxwarhorn` |
| c6 t4 | Lineal Chains | square | 0 | AttackChain | `drxonslaught_hamstring` |
| c6 t6 | Doom Bond | circle | 0 | AttackRadius | `drxwarhorn_doomhorn` |
| c6 t7 | Ancestral Horn | square | 30 | SpawnPet | `drxancestralhorn` |

**Connections (record-driven bars):**

- **Battle Rage** (c2t2) straight bar len=5 -> Crushing Blow@c2t4, Counter Attack@c2t6
- **Onslaught** (c4t1) straight bar len=7 -> Ignore Pain@c4t2, Ardor@c4t7
- **Lineal Chains** (c6t4) straight bar len=3 -> Doom Bond@c6t6
- **Dual Wield** (c1t1) straight bar len=7 -> Parry@c1t2, Hew@c1t3, Cross Cut@c1t4, Tumult@c1t6
- **War Dance** (c5t2) straight bar len=4 -> Lacerate@c5t4
- **Battle Standard** (c3t3) straight bar len=4 -> drxbattlestandard_petmodifier_triumph@c3t6


### m2 Defense - `Defense Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 .             .             .             .             [Colossus Form](Pulverize)
t6 .             (Defensive Rea)(Disruption)  (Iron Will)   .             .
t5 .             .             .             .             (Defiance)    (Disable)
t4 .             (Resilience)  [Shield Charge]*(Focus)       .             .
t3 .             (Quick Recover)(Rend Armor)  .             (Inspiration) (Shield Smash)*
t2 .             (Adrenaline)* .             [drxbattleawar].             .
t1 (Concussive Bl)*.             [Batter]*     .             [drxrally]    (Armor Handlin)
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t1 | Concussive Blow | circle | 1 | Passive | `drxconcussiveblow` |
| c2 t2 | Adrenaline | circle | 0 | PassiveOnHitBuffSelf | `drxadrenaline` |
| c2 t3 | Quick Recovery | circle | 5 | Modifier | `drxquickrecovery` |
| c2 t4 | Resilience | circle | 0 | Modifier | `drxadrenaline_resilience` |
| c2 t6 | Defensive Reaction | circle | 0 | Modifier | `drxadrenaline_defensivereaction` |
| c3 t1 | Batter | square | 1 | AttackWeapon | `drxbatter` |
| c3 t3 | Rend Armor | circle | 15 | Modifier | `drxbatter_rendarmor` |
| c3 t4 | Shield Charge | square | 10 | AttackWeaponCharge | `drxshieldcharge` |
| c3 t6 | Disruption | circle | 0 | Modifier | `drxshieldcharge_disruption` |
| c4 t2 | *(drxbattleawareness) | square | None | BuffRadiusToggled | `drxbattleawareness` |
| c4 t4 | Focus | circle | 5 | Modifier | `drxbattleawareness_focus` |
| c4 t6 | Iron Will | circle | 0 | Modifier | `drxbattleawareness_ironwill` |
| c5 t1 | *(drxrally) | square | None | BuffRadius | `drxrally` |
| c5 t3 | Inspiration | circle | 0 | Modifier | `drxrally_inspiration` |
| c5 t5 | Defiance | circle | 30 | Modifier | `drxrally_defiance` |
| c5 t7 | Colossus Form | square | 0 | BuffSelfColossus | `drxcolossusform` |
| c6 t1 | Armor Handling | circle | 1 | Passive | `drxarmorhandling` |
| c6 t3 | Shield Smash | circle | 5 | BasicAttack | `drxweaponpool_shieldsmash` |
| c6 t5 | Disable | circle | 15 | BasicAttack | `drxweaponpool_disable` |
| c6 t7 | Pulverize | circle | 20 | BasicAttack | `drxweaponpool_pulverize` |

**Connections (record-driven bars):**

- **Shield Charge** (c3t4) straight bar len=3 -> Disruption@c3t6
- **Adrenaline** (c2t2) straight bar len=5 -> Quick Recovery@c2t3, Resilience@c2t4, Defensive Reaction@c2t6
- **Shield Smash** (c6t3) right bar len=5 -> (void - bar tops on an empty cell)
- **Batter** (c3t1) straight bar len=3 -> Rend Armor@c3t3
- **Concussive Blow** (c1t1) straight bar len=7 -> (void - bar tops on an empty cell)


### m3 Earth - `Earth Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 (Volatility)  .             .             .             .             .
t6 .             (Molten Rock) (drxcoredwelle).             .             [Eruption]*
t5 .             .             (drxcoredwelle).             (Flare)       (Fragmentation)
t4 (Stone Skin)  [Stone Form]* (drxcoredwelle).             .             (Conflagration)
t3 .             .             [Core Dweller]*(Soften Metal)(Barrage)     .
t2 (Brimstone)   [drxheatshield].             .             .             [Volcanic Orb]*
t1 [drxfireenchan].             .             [Ring of Flame]*[Rupture]*    .
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t1 | *(drxfireenchantment) | square | None | BuffRadiusToggled | `drxfireenchantment` |
| c1 t2 | Brimstone | circle | 0 | Modifier | `drxfireenchantment_brimstone` |
| c1 t4 | Stone Skin | circle | 0 | Modifier | `drxfireenchantment_stoneskin` |
| c1 t7 | Volatility | circle | 0 | Passive | `drxvolatility` |
| c2 t2 | *(drxheatshield) | square | None | BuffOther | `drxheatshield` |
| c2 t4 | Stone Form | square | 5 | BuffSelfImmobilize | `drxstoneformbuffself` |
| c2 t6 | Molten Rock | circle | 15 | Modifier | `drxstoneform_moltenrock` |
| c3 t3 | Core Dweller | square | 10 | SpawnPet | `drxcoredweller` |
| c3 t4 | *(drxcoredweller_petmodifier_innerfire) | circle | None | PetModifier | `drxcoredweller_petmodifier_innerfire` |
| c3 t5 | *(drxcoredweller_petmodifier_wildfire) | circle | None | PetModifier | `drxcoredweller_petmodifier_wildfire` |
| c3 t6 | *(drxcoredweller_petmodifier_metamorphosis) | circle | None | PetModifier | `drxcoredweller_petmodifier_metamorphosis` |
| c4 t1 | Ring of Flame | square | 10 | BuffAttackRadiusToggled | `drxringofflame` |
| c4 t3 | Soften Metal | circle | 0 | Modifier | `drxringofflame_softenmetal` |
| c5 t1 | Rupture | square | 1 | AttackWeaponRangedSpread | `drxflamesurge` |
| c5 t3 | Barrage | circle | 0 | Modifier | `drxflamesurge_barrage` |
| c5 t5 | Flare | circle | 15 | Modifier | `drxflamesurge_flamearch` |
| c6 t2 | Volcanic Orb | square | 1 | AttackProjectile | `drxvolcanicorb` |
| c6 t4 | Conflagration | circle | 10 | ProjectileModifier | `drxvolcanicorb_immolation` |
| c6 t5 | Fragmentation | circle | 0 | ProjectileModifier | `drxvolcanicorb_fragmentation` |
| c6 t6 | Eruption | square | 0 | AttackProjectileAreaEffect | `drxeruption` |

**Connections (record-driven bars):**

- **Volcanic Orb** (c6t2) straight bar len=4 -> Conflagration@c6t4, Fragmentation@c6t5
- **Eruption** (c6t6) straight bar len=2 -> (void - bar tops on an empty cell)
- **Ring of Flame** (c4t1) straight bar len=3 -> Soften Metal@c4t3
- **Core Dweller** (c3t3) straight bar len=4 -> drxcoredweller_petmodifier_innerfire@c3t4, drxcoredweller_petmodifier_wildfire@c3t5, drxcoredweller_petmodifier_metamorphosis@c3t6
- **Stone Form** (c2t4) straight bar len=3 -> Molten Rock@c2t6
- **Rupture** (c5t1) straight bar len=5 -> Barrage@c5t3, Flare@c5t5


### m4 Storm - `Storm Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 (drxstormwisp_)(Chain Lightni).             .             (Torrent)     .
t6 .             .             (Thunder Cloud)(Ice Burst)   .             (Energy Resona)
t5 [Storm Wisp]* .             .             .             .             [drxenergyshie]
t4 (Electrical Co)[Lightning Bol]*[Squall]*     .             .             .
t3 .             (Concussive Bl).             [Flash Freeze]*(Velocity)    .
t2 .             .             [Storm Surge] [drxfreezingbl].             (Heart of Fros)
t1 [Storm Nimbus]*[Thunderball]*.             .             [Ice Shard]*  .
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t1 | Storm Nimbus | square | 0 | BuffSelfToggled | `drxstormnimbus` |
| c1 t4 | Electrical Conduit | circle | 0 | Modifier | `drxstormnimbus_staticcharge` |
| c1 t5 | Storm Wisp | square | 20 | SpawnPet | `drxstormwispsummoning` |
| c1 t7 | *(drxstormwisp_petmodifier_eyeofthestorm) | circle | None | PetModifier | `drxstormwisp_petmodifier_eyeofthestorm` |
| c2 t1 | Thunderball | square | 0 | AttackProjectileAreaEffect | `drxthunderball` |
| c2 t3 | Concussive Blast | circle | 0 | ProjectileModifier | `drxthunderball_concussiveblast` |
| c2 t4 | Lightning Bolt | square | 0 | AttackRadiusLightning | `drxlightningbolt` |
| c2 t7 | Chain Lightning | circle | 0 | ChainLightning | `drxlightningbolt_chainlightning` |
| c3 t2 | Storm Surge | square | 0 | OnHitAttackRadius | `drxstormsurge` |
| c3 t4 | Squall | square | 0 | AttackProjectileAreaEffect | `drxsquall` |
| c3 t6 | Thunder Clouds | circle | 0 | ProjectileModifier | `drxsquall_obscuredvisibility` |
| c4 t2 | *(drxfreezingblast) | square | None | AttackProjectileDebuf | `drxfreezingblast` |
| c4 t3 | Flash Freeze | square | 5 | BuffSelfImmobilize | `drxspellbreaker` |
| c4 t6 | Ice Burst | circle | 5 | AttackRadius | `drxspellbreaker_spellshock` |
| c5 t1 | Ice Shard | square | 1 | AttackProjectileBurst | `drxiceshard` |
| c5 t3 | Velocity | circle | 0 | Modifier | `drxiceshard_velocity` |
| c5 t7 | Torrent | circle | 0 | Modifier | `drxiceshard_torrent` |
| c6 t2 | Heart of Frost | circle | 0 | Modifier | `drxstormnimbus_heartoffrost` |
| c6 t5 | *(drxenergyshield) | square | None | BuffOther | `drxenergyshield` |
| c6 t6 | Energy Resonance | circle | 25 | Modifier | `drxenergyshield_reflection` |

**Connections (record-driven bars):**

- **Ice Shard** (c5t1) straight bar len=7 -> Velocity@c5t3, Torrent@c5t7
- **Storm Nimbus** (c1t1) straight bar len=4 -> Electrical Conduit@c1t4
- **Lightning Bolt** (c2t4) straight bar len=4 -> Chain Lightning@c2t7
- **Storm Wisp** (c1t5) straight bar len=3 -> drxstormwisp_petmodifier_eyeofthestorm@c1t7
- **Squall** (c3t4) straight bar len=3 -> Thunder Clouds@c3t6
- **Flash Freeze** (c4t3) straight bar len=4 -> Ice Burst@c4t6
- **Thunderball** (c2t1) straight bar len=3 -> Concussive Blast@c2t3


### m5 Occult - `Occult Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 (Aphotic Ichor).             .             .             (Dark Vapors) .
t6 .             (Toxin Distill)(Shadow Lore) .             .             (Flurry of Kni)
t5 (Poisonous Gas)(Mandrake)    .             (Shadow Grasp)*[Nether Strike]*.
t4 .             .             (Dark Invigora).             .             [Throwing Knif]*
t3 [Smoke Screen](Nightshade)  .             [Breach]*     [Blade Fury]  .
t2 [Flash Powder].             [Shadow Link] .             .             .
t1 .             [Envenom Weapo]*.             .             [Calculated St]*(Agility)*
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t2 | Flash Powder | square | 0 | AttackRadius | `drxflashpowder` |
| c1 t3 | Smoke Screen | square | 0 | AttackProjectileSpawnPet | `drxlaytrap_petmodifier_multishotbolttrap` |
| c1 t5 | Poisonous Gas | circle | 0 | ProjectileModifier | `drxpoisongasbomb` |
| c1 t7 | Aphotic Ichor | circle | 0 | ProjectileModifier | `drxpoisongasbomb_shrapnel` |
| c2 t1 | Envenom Weapon | square | 1 | BuffSelfToggled | `drxenvenomweapon` |
| c2 t3 | Nightshade | circle | 0 | Modifier | `drxenvenomweapon_neurotoxin` |
| c2 t5 | Mandrake | circle | 0 | Modifier | `drxenvenomweapon_delirium` |
| c2 t6 | Toxin Distillation | circle | 0 | Modifier | `drxtoxindistillation` |
| c3 t2 | Shadow Link | square | None | BuffRadiusToggled | `drxbladehoning` |
| c3 t4 | Dark Invigoration | circle | 0 | Modifier | `drxopenwound` |
| c3 t6 | Shadow Lore | circle | 0 | Modifier | `drxanatomy` |
| c4 t3 | Breach | square | 0 | AttackProjectileAreaEffect | `drxlaytrap` |
| c4 t5 | Shadow Grasp | circle | 24 | ProjectileModifier | `drxlaytrap_rapidconstruction` |
| c5 t1 | Calculated Strike | square | 1 | AttackWeaponCharge | `drxcalculatedstrike` |
| c5 t3 | Blade Fury | square | 0 | BasicAttack | `drxcalculatedstrike_luckyhit` |
| c5 t5 | Nether Strike | square | 10 | AttackWeaponBlink | `drxlethalstrike` |
| c5 t7 | Dark Vapors | circle | 10 | Modifier | `drxlethalstrike_mortalwound` |
| c6 t1 | Agility | circle | 0 | Passive | `drxdisarmtraps` |
| c6 t4 | Throwing Knife | square | 5 | AttackProjectileBurst | `drxthrowingknife` |
| c6 t6 | Flurry of Knives | circle | 0 | Modifier | `drxthrowingknife_flurryofknives` |

**Connections (record-driven bars):**

- **Envenom Weapon** (c2t1) straight bar len=6 -> Nightshade@c2t3, Mandrake@c2t5, Toxin Distillation@c2t6
- **Calculated Strike** (c5t1) straight bar len=5 -> Blade Fury@c5t3, Nether Strike@c5t5
- **Throwing Knife** (c6t4) straight bar len=3 -> Flurry of Knives@c6t6
- **Agility** (c6t1) straight bar len=2 -> (void - bar tops on an empty cell)
- **Breach** (c4t3) straight bar len=3 -> Shadow Grasp@c4t5
- **Shadow Grasp** (c4t5) right bar len=2 -> (void - bar tops on an empty cell)
- **Nether Strike** (c5t5) right bar len=3 -> Flurry of Knives@c6t6


### m6 Hunting - `Hunting Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 (Flush Out)   .             (Volley)      .             .             (drxmonsterlur)
t6 .             .             (Scatter Shot ).             .             .
t5 [drxstudyprey](Exploit Weakn).             .             (Trail Blazing).
t4 .             .             (Puncture Shot).             (Find Cover)  [Lay Trap]*
t3 (Barbed Nettin)[drxcalloftheh].             .             .             .
t2 .             .             [Marksmanship]*[Eviscerate]* [drxartofthehu](Herbalism)
t1 [drxensnare]  .             (Gouge)       [Take Down]   .             (Wood Lore)*
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t1 | *(drxensnare) | square | None | AttackProjectileDebuf | `drxensnare` |
| c1 t3 | Barbed Netting | circle | 24 | Modifier | `drxensnare_barbednetting` |
| c1 t5 | *(drxstudyprey) | square | None | AttackBuffRadius | `drxstudyprey` |
| c1 t7 | Flush Out | circle | 0 | Modifier | `drxstudyprey_flushout` |
| c2 t3 | *(drxcallofthehunt) | square | None | BuffRadius | `drxcallofthehunt` |
| c2 t5 | Exploit Weakness | circle | 1 | Modifier | `drxcallofthehunt_cunning` |
| c3 t1 | Gouge | circle | 5 | BasicAttack | `drxweaponskill_gouge` |
| c3 t2 | Marksmanship | square | 1 | BasicAttack | `drxmarksmanship` |
| c3 t4 | Puncture Shot Arrows | circle | 10 | Modifier | `drxmarksmanship_punctureshotarrows` |
| c3 t6 | Scatter Shot Arrows | circle | 25 | ProjectileModifier | `drxmarksmanship_scattershotarrows` |
| c3 t7 | Volley | circle | 25 | BasicAttack | `drxweaponskill_volley` |
| c4 t1 | Take Down | square | 1 | AttackWeaponCharge | `drxtakedown` |
| c4 t2 | Eviscerate | square | 1 | AttackWeapon | `drxtakedown_eviscerate` |
| c5 t2 | *(drxartofthehunt) | square | None | BuffRadiusToggled | `drxartofthehunt` |
| c5 t4 | Find Cover | circle | 0 | Modifier | `drxartofthehunt_findcover` |
| c5 t5 | Trail Blazing | circle | 0 | Modifier | `drxartofthehunt_trailblazing` |
| c6 t1 | Wood Lore | circle | 1 | Passive | `drxwoodlore` |
| c6 t2 | Herbalism | circle | 5 | Passive | `drxherbalism` |
| c6 t4 | Lay Trap | square | 10 | AttackProjectileSpawnPet | `drxmonsterlure` |
| c6 t7 | *(drxmonsterlure_petmodifier_detonate) | circle | None | PetModifier | `drxmonsterlure_petmodifier_detonate` |

**Connections (record-driven bars):**

- **Wood Lore** (c6t1) straight bar len=2 -> Herbalism@c6t2
- **Marksmanship** (c3t2) straight bar len=5 -> Puncture Shot Arrows@c3t4, Scatter Shot Arrows@c3t6
- **Eviscerate** (c4t2) straight bar len=5 -> (void - bar tops on an empty cell)
- **Lay Trap** (c6t4) straight bar len=4 -> drxmonsterlure_petmodifier_detonate@c6t7


### m7 Spirit - `Spirit Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 .             .             [Outsider]    (Unearthly Pow)(drxwraithlord).
t6 (Death Ward)  [Acid Rain]   .             .             (drxwraithlord).
t5 .             .             (Necrosis)    .             [Liche King]* .
t4 (Arcane Lore) (Wither)      .             [drxdarkcovena].             .
t3 .             (Diffusion)   (Ravages of Ti).             (drxlifedrain)(Mortal Condui)
t2 [Ternion Attac]*.             [drxspiritward].             .             .
t1 .             [drxdeathchill].             [Vision of Dea].             [Bone Spire]*
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t2 | Ternion Attack | square | 1 | AttackWeaponRangedSpread | `drxternion` |
| c1 t4 | Arcane Lore | circle | 10 | ProjectileModifier | `drxternion_arcanelore` |
| c1 t6 | Death Ward | circle | 0 | PassiveOnLifeBuffSelf | `drxdeathward` |
| c2 t1 | *(drxdeathchillaura) | square | None | BuffRadiusToggled | `drxdeathchillaura` |
| c2 t3 | Diffusion | circle | 0 | Modifier | `drxspiritward_spiritbane` |
| c2 t4 | Wither | circle | 0 | Modifier | `drxwraithlord_petmodifier_arcaneblast` |
| c2 t6 | Acid Rain | square | 0 | AttackProjectileAreaEffect | `drxcircleofpower` |
| c3 t2 | *(drxspiritward) | square | None | BuffRadiusToggled | `drxspiritward` |
| c3 t3 | Ravages of Time | circle | 0 | Modifier | `drxdeathchillaura_ravagesoftime` |
| c3 t5 | Necrosis | circle | 0 | Modifier | `drxdeathchillaura_necrosis` |
| c3 t7 | Outsider | square | 0 | SpawnPet | `drxoutsidersummons` |
| c4 t1 | Vision of Death | square | 5 | AttackRadius | `drxvisionofdeath` |
| c4 t4 | *(drxdarkcovenant) | square | None | BuffRadius | `drxdarkcovenant` |
| c4 t7 | Unearthly Power | circle | 0 | Modifier | `drxdarkcovenant_unearthlypower` |
| c5 t3 | *(drxlifedrain) | circle | None | PetModifier | `drxlifedrain` |
| c5 t5 | Liche King | square | 15 | SpawnPet | `drxwraithlordsummons` |
| c5 t6 | *(drxwraithlord_petmodifier_deathnova) | circle | None | PetModifier | `drxwraithlord_petmodifier_deathnova` |
| c5 t7 | *(drxwraithlord_petmodifier_wraithshell) | circle | None | PetModifier | `drxwraithlord_petmodifier_wraithshell` |
| c6 t1 | Bone Spire | square | 0 | AttackProjectileBurst | `drxenslavespirit` |
| c6 t3 | Mortal Conduit | circle | 0 | Modifier | `drxlifedrain_cascade` |

**Connections (record-driven bars):**

- **Bone Spire** (c6t1) straight bar len=5 -> Mortal Conduit@c6t3
- **Ternion Attack** (c1t2) straight bar len=3 -> Arcane Lore@c1t4
- **Liche King** (c5t5) right bar len=3 -> (void - bar tops on an empty cell)


### m8 Nature - `Nature Mastery` (20 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 .             .             .             .             (drxsylvannymp).
t6 (Permanence of).             (drxbriarward_).             .             (Susceptibilit)
t5 (Tranquility o).             .             (drxwolf_petmo)(drxsylvannymp).
t4 .             (Dissemination)(drxbriarward_).             [Sylvan Nymph]*(Fatigue)
t3 .             .             [Quill Ward]* (drxwolf_petmo)(Dissemination).
t2 [drxheartofoak](Accelerated G).             (drxwolf_petmo).             [drxplague]
t1 .             [Regrowth]*   .             [Call of the W]*.             .
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t2 | *(drxheartofoak) | square | None | BuffRadiusToggled | `drxheartofoak` |
| c1 t5 | Tranquility of Water | circle | 15 | Modifier | `drxheartofoak_tranquility` |
| c1 t6 | Permanence of Stone | circle | 15 | Modifier | `drxheartofoak_permanence` |
| c2 t1 | Regrowth | square | 1 | GiveBonus | `drxregrowth` |
| c2 t2 | Accelerated Growth | circle | 1 | Modifier | `drxregrowth_acceleratedgrowth` |
| c2 t4 | Dissemination | circle | 10 | ChainBonus | `drxregrowth_dissemination` |
| c3 t3 | Quill Ward | square | 0 | DefensiveWall | `drxbriarward` |
| c3 t4 | *(drxbriarward_petmodifier_stingingnettle) | circle | None | PetModifier | `drxbriarward_petmodifier_stingingnettle` |
| c3 t6 | *(drxbriarward_sanctuary) | circle | None | BuffRadius | `drxbriarward_sanctuary` |
| c4 t1 | Call of the Wild | square | 1 | SpawnPet | `drxwolfsummons` |
| c4 t2 | *(drxwolf_petmodifer_survivalinstinct) | circle | None | PetModifier | `drxwolf_petmodifer_survivalinstinct` |
| c4 t3 | *(drxwolf_petmodifer_maul) | circle | None | PetModifier | `drxwolf_petmodifer_maul` |
| c4 t5 | *(drxwolf_petmodifier_strengthofthepack) | circle | None | PetModifier | `drxwolf_petmodifier_strengthofthepack` |
| c5 t3 | Dissemination | circle | 0 | AttackRadius | `drxrenewal` |
| c5 t4 | Sylvan Nymph | square | 15 | AttackProjectileSpawnPet | `drxsylvannymphsummons` |
| c5 t5 | *(drxsylvannymph_petmodifier_nature'swrath) | circle | None | PetModifier | `drxsylvannymph_petmodifier_nature'swrath` |
| c5 t7 | *(drxsylvannymph_petmodifier_overgrowth) | circle | None | PetModifier | `drxsylvannymph_petmodifier_overgrowth` |
| c6 t2 | *(drxplague) | square | None | AttackBuff | `drxplague` |
| c6 t4 | Fatigue | circle | 18 | Modifier | `drxplague_fatigue` |
| c6 t6 | Susceptibility | circle | 18 | Modifier | `drxplague_susceptibility` |

**Connections (record-driven bars):**

- **Regrowth** (c2t1) straight bar len=4 -> Accelerated Growth@c2t2, Dissemination@c2t4
- **Quill Ward** (c3t3) straight bar len=4 -> drxbriarward_petmodifier_stingingnettle@c3t4, drxbriarward_sanctuary@c3t6
- **Call of the Wild** (c4t1) straight bar len=5 -> drxwolf_petmodifer_survivalinstinct@c4t2, drxwolf_petmodifer_maul@c4t3, drxwolf_petmodifier_strengthofthepack@c4t5
- **Sylvan Nymph** (c5t4) straight bar len=4 -> drxsylvannymph_petmodifier_nature'swrath@c5t5, drxsylvannymph_petmodifier_overgrowth@c5t7


### m9 Dream - `Dream Mastery` (24 placed skills)

```
        col1          col2          col3          col4          col5          col6
t7 .             (Lucid Dream) [Phantasm]    .             (Temporal Rift).
t6 [Trance of Wra].             (drxnightmare_)(Dream Stealer).             .
t5 .             (Temporal Flux).             .             [Distort Reali]*(Psionic Immol)
t4 [drxtranceofco].             [Nightmare]*  [Phantom Strik]*(Psionic Burn).
t3 .             (Distortion Fi)(Troubled Drea)(Inversion)   .             (Chaotic Reson)
t2 [drxtranceofem].             .             [Mind Breaker]*(Psionic Arter).
t1 .             (Premonition)*[Sands of Slee]*.             [Psionic Touch]*[Distortion Wa]*
```

| cell | skill | shape | tier-req | class | record |
|---|---|---|---|---|---|
| c1 t2 | *(drxtranceofempathy) | square | None | BuffRadiusToggled | `drxtranceofempathy` |
| c1 t4 | *(drxtranceofconvalescence) | square | None | BuffRadiusToggled | `drxtranceofconvalescence` |
| c1 t6 | Trance of Wrath | square | 0 | BuffAttackRadiusToggled | `drxtranceofwrath` |
| c2 t1 | Premonition | circle | 0 | Passive | `drxluciddream_premonition` |
| c2 t3 | Distortion Field | circle | 0 | PassiveOnHitBuffSelf | `drxdistortionfield` |
| c2 t5 | Temporal Flux | circle | 0 | Passive | `drxluciddream_temporalflux` |
| c2 t7 | Lucid Dream | circle | 0 | Passive | `drxluciddream` |
| c3 t1 | Sands of Sleep | square | 0 | AttackChain | `drxsandsofsleep` |
| c3 t3 | Troubled Dreams | circle | 0 | Modifier | `drxsandsofsleep_troubleddreams` |
| c3 t4 | Nightmare | square | 0 | SpawnPet | `drxnightmare` |
| c3 t6 | *(drxnightmare_petmodifier_dreamsurge) | circle | None | PetModifier | `drxnightmare_petmodifier_dreamsurge` |
| c3 t7 | Phantasm | square | 0 | AttackProjectileSpawnPet | `drxphantasm` |
| c4 t2 | Mind Breaker | square | 0 | DispelMagic | `drxspellbreaker` |
| c4 t3 | Inversion | circle | 0 | Modifier | `drxspellbreaker_spellshock` |
| c4 t4 | Phantom Strike | square | 0 | AttackWeaponBlink | `drxphantomstrike` |
| c4 t6 | Dream Stealer | circle | 0 | Modifier | `drxphantomstrike_dreamstealer` |
| c5 t1 | Psionic Touch | square | 0 | ChargedFinale | `drxpsionictouch` |
| c5 t2 | Psionic Artery | circle | 0 | Modifier | `drxpsionictouch_multihit` |
| c5 t4 | Psionic Burn | circle | 0 | AttackRadius | `drxpsionictouch_psionicburn` |
| c5 t5 | Distort Reality | square | 0 | AttackRadius | `drxdistortreality` |
| c5 t7 | Temporal Rift | circle | 0 | Modifier | `drxdistortreality_temporalrift` |
| c6 t1 | Distortion Wave | square | 1 | AttackWave | `drxdistortionwave` |
| c6 t3 | Chaotic Resonance | circle | 0 | Modifier | `drxdistortionwave_chaoticresonance` |
| c6 t5 | Psionic Immolation | circle | 0 | Modifier | `drxdistortionwave_psionicimmolation` |

**Connections (record-driven bars):**

- **Distortion Wave** (c6t1) straight bar len=5 -> Chaotic Resonance@c6t3, Psionic Immolation@c6t5
- **Nightmare** (c3t4) straight bar len=3 -> drxnightmare_petmodifier_dreamsurge@c3t6
- **Distort Reality** (c5t5) straight bar len=3 -> Temporal Rift@c5t7
- **Psionic Touch** (c5t1) straight bar len=4 -> Psionic Artery@c5t2, Psionic Burn@c5t4
- **Phantom Strike** (c4t4) straight bar len=3 -> Dream Stealer@c4t6
- **Sands of Sleep** (c3t1) straight bar len=3 -> Troubled Dreams@c3t3
- **Premonition** (c2t1) straight bar len=7 -> Distortion Field@c2t3, Temporal Flux@c2t5, Lucid Dream@c2t7
- **Mind Breaker** (c4t2) straight bar len=2 -> Inversion@c4t3


---

## 7. DEVIATIONS preview: SV098 ground truth vs build41 (the fix lane's work list)

> **CAUTION.** build41 (the revert target) is a SUPERSET of SV098 in ALL 9 masteries: it ADDS coherent, intentional restored skills to every tree (Meteor, Force of Nature, Skeletal Soldier, Sands of Sleep, Distortion Wave, Cleave, Cold Aura, Bone Fiend, etc.) and REMOVES nothing. SV098's placed trees (20 skills each, 24 for Dream) are a SUBSET. 'Match SV098 exactly' therefore must NOT mean blanket roster deletion - that would gut the mod's whole legacy-skill restoration. Use SV098 as the authority for LAWS (7-row geometry, isCircular shape encoding, connOn/Off connector mechanism) and for the placement/shape/connector of SV-shared skills; treat build41 additions as intentional and re-fit them to SV's laws.

> Occult(m5) + Hunting(m6) additions are Will's SVAERA overlay (Darklings, Dark Aperture, Toxic Concoction, Shadow Stalker, Channel, Blade Mastery / Tempest, Flayer, Cornered, Rapid Construction) - PRESERVE. The anchor-6 finding (Darklings+Dark Aperture wrongly in Shadow Link's column 3) IS a candidate fix within the overlay.

### 7a. Real fixes (shape flips - build41 contradicts SV098 AND Will's anchors)

| mastery | skill | fix |
|---|---|---|
| Occult | Blade Fury | restore SQUARE (build41 has circle) |
| Occult | Smoke Screen | restore SQUARE (build41 has circle) |
| Occult | Poisonous Gas | restore CIRCLE (build41 has square) |
| Hunting | Eviscerate | SV098 has SQUARE; build41 has circle (confirm intent - Hunting is hand-tuned) |
| Earth | Soften Metal (MOVE) | SV c4t3 -> build41 c4t2 |

### 7b. Per-mastery deviation counts (build41 vs SV098)

| mastery | total diffs | added-in-build41 (intentional restorations) | removed | shape/move fixes |
|---|---|---|---|---|
| m1 Warfare | 8 | 8 | 0 | 0 |
| m2 Defense | 6 | 6 | 0 | 0 |
| m3 Earth | 9 | 8 | 0 | 1 |
| m4 Storm | 7 | 7 | 0 | 0 |
| m5 Occult | 9 | 6 | 0 | 3 |
| m6 Hunting | 5 | 4 | 0 | 1 |
| m7 Spirit | 9 | 9 | 0 | 0 |
| m8 Nature | 6 | 6 | 0 | 0 |
| m9 Dream | 1 | 1 | 0 | 0 |

The **added** column is dominated by intentional Soulvizier legacy-skill restorations (Meteor, Force of Nature, Skeletal Soldier, Sands of Sleep, Distortion Wave, Cleave, Cold Aura, Bone Fiend, ...); those are **NOT** errors. The actionable regressions are the **shape/move fixes** column plus the emblem circle (section 4) and the Occult anchor-6 column placement (section 5).

Full per-skill diff lists are in `tools/sv_mastery_ground_truth.json` -> `deviations_vs_build41`.


---

## 8. PRE-0.98i SV OCCULT (Will correction 2026-07-16)

**Correction to sections 0/5/7.** Will confirmed that Darklings / Dark Aperture / Toxic
Concoction / Shadow Stalker were **NOT hand-authored** by him: they come from an **older SV**
(pre-0.98i). Ground-truth recon over `upstream/soulvizier_041/Database/database.arz` (md5
verify at runtime) and `upstream/soulvizier_0.9/Database/database.arz` proves it. Machine-readable
companion: **`tools/sv_pre098i_occult_ground_truth.json`**.

**Method note (supersedes the section-0/5 "absent from SV098" claim).** The authoritative list of
DISPLAYED skills in a mastery is the pane's **`panectrl.dbr::tabSkillButtons`** array, NOT the mere
existence of a `skillNN.dbr` button record. SV 0.41 / 0.9 / 0.98i all list `Mastery + Skill01..20`
(20 displayed); build41 lists `Skill01..26` (26). The 098i extraction counted only displayed
buttons - correct - but concluded the four were "absent". In fact **their button records exist in
all three SV versions** (`Skill21..24`), just OUTSIDE `tabSkillButtons` (latent/hidden). build41
re-enabled them by extending `tabSkillButtons`.

### 8.1 The lineage (proven)

- **Occult = mastery 5** (`records\ingameui\player skills\mastery 5`) in EVERY SV version; the
  DRX namespace (`drx*`) already exists in 0.41. **SV 0.41 and SV 0.9 are byte-identical** for all
  four skills (same positions, shapes, tiers, connectors) - so the source is **BOTH 0.41 and 0.9**.
- **Toxic Concoction** (`drx_scrap`, tag `tagScrapNAME`) and **Shadow Stalker**
  (`drx_summon_shadow_stalker`, tag `tagStalkerSummonsNAME`) exist as **hidden buttons** at their
  final positions in 0.41/0.9/0.98i. build41 only re-enabled them; **positions unchanged**.
- **Darklings** and **Dark Aperture** are build41 records (`drxdarklings`,
  `drxdarklings_darkaperture`) that **clone the older-SV `drxlaytrap` family identity**. In SV
  0.41/0.9, `drxlaytrap` (Class `AttackProjectileSpawnPet`, tag `tagirregulardemonNAME`, which 098i
  text resolves to **"Darklings"**) is the **"irregular-demon / Darklings" summon** displayed at
  **col4 tier3**, and `drxlaytrap_rapidconstruction` (Class `Modifier`, tag `tagbreachNAME`, circle,
  req24) is its augment at **col4 tier5**. **SV 0.98i REPURPOSED those same records** into
  **Breach** (`drxlaytrap` -> `AttackProjectileAreaEffect`, `tagbreachNAME`) and **Shadow Grasp**
  (`drxlaytrap_rapidconstruction` -> `ProjectileModifier`, `tagNewSkill321`). Will wanted BOTH the
  098i Breach/Shadow Grasp AND the old Darklings summon, so he re-recorded the old identity as new
  `drxdarklings*` records (same tags/shapes/tiers/connectors, byte-copied) - but **placed them in
  Shadow Link's column 3** instead of the family's own column.

### 8.2 Authoritative older-SV layout (SV 0.41 == SV 0.9) - Occult col3/col4 context

7-row grid **confirmed identical** to 098i (Y=465-62*tier; rows t1-7 Y={403,341,279,217,155,93,31};
cols {128,228,328,428,528,628}; thresholds 1/4/10/16/24/32/40). `(name)`=circle, `[name]`=square,
`*`=carries a connector bar. Names via 098i `Text_EN.arc` (older SV ships no Resources).

```
OLDER SV (0.41/0.9) DISPLAYED Occult - col3 & col4:
        col3 (328)              col4 (428)
t7 .                        (Channel)          <- drx_petmodifier_greaterpower  [HIDDEN in older SV]
t6 (Shadow Lore)            [Shadow Stalker]   <- drx_summon_shadow_stalker      [HIDDEN in older SV]
t5 .                        (Dark-Aperture-ancestor)*  <- drxlaytrap_rapidconstruction (tagbreachNAME, circle, req24, _right bar->void)
t4 (Dark Invigoration)      .                  <- (col4 t4 EMPTY)
t3 .                        [Darklings]*       <- drxlaytrap (tagirregulardemonNAME='Darklings', square, straight bar len3 up to t5)
t2 [Shadow Link]            .
t1 .                        .
```

The Darklings family = **column 4**: summon base at **t3**, augment modifier at **t5**, **t4 EMPTY**
between -> a clean straight 3-tile bar t3->t5. Column 3 is Shadow Link's clean passive column (t2/t4/t6).

### 8.3 The four skills - authoritative (row, col, shape, connects_to)

| skill | build41 record | older-SV source | row | col | shape | tier_req | connects_to |
|---|---|---|---|---|---|---|---|
| Toxic Concoction | `drx_scrap` | own hidden button (0.41/0.9/0.98i) | t4 | **1** | square | 0 | straight bar len4 UP through Poisonous Gas (t5) to **Aphotic Ichor** (c1t7) = the poison chain |
| Shadow Stalker | `drx_summon_shadow_stalker` | own hidden button (0.41/0.9/0.98i) | t6 | **4** | square | 0 | straight bar len2 UP to **Channel** (`drx_petmodifier_greaterpower`, c4t7) |
| Darklings | `drxdarklings` (<- `drxlaytrap`) | ancestor displayed 0.41/0.9 | t3 | **4** (authoritative) | square | 0 | straight bar len3 UP to its modifier at t5 (t4 empty) |
| Dark Aperture | `drxdarklings_darkaperture` (<- `drxlaytrap_rapidconstruction`) | ancestor displayed 0.41/0.9 | t5 | **4** (authoritative) | circle | 24 | augment ABOVE Darklings; drawn by Darklings' bar. Carries an inherited `_right` (BRTR) bar that tops on VOID (older-SV artifact) |

**Shapes - all four CONFIRMED against older SV (no shape flip needed for these four):** Toxic
Concoction square, Shadow Stalker square, Darklings square, Dark Aperture **circle** (matches Will's
"Dark Aperture augments Darklings = circle"). Connectors are **record-driven** (`skillConnectionOn`/
`Off` string arrays; byte-copied from the older-SV `drxlaytrap` family), NOT baked into the pane
`.tex` - consistent with section 3.

### 8.4 Connection graph (build41 Occult, the four + neighbours)

- **Toxic Concoction** (c1t4) `--straight len4-->` **Aphotic Ichor** (c1t7), passing a CONNECT tile
  over **Poisonous Gas** (c1t5). This reproduces Will's anchor-3 chain **Toxic Concoction - Poisonous
  Gas - Aphotic Ichor** and it is AUTHENTIC older-SV (the `drx_scrap` bar is identical in 0.41/0.9/098i).
- **Shadow Stalker** (c4t6) `--straight len2-->` **Channel** (c4t7, its pet modifier).
- **Darklings** (c3t3 in build41) `--straight len3-->` **Dark Aperture** (c3t5) - but the bar draws
  through **Dark Invigoration** (c3t4, FOREIGN) with a stale MIDDLE tile (should be CONNECT).
- **Dark Aperture** (c3t5) carries a spurious inherited **`_right` BRTR** bar pointing at (c4t6) =
  Shadow Stalker's cell - a cross-column artifact from its `drxlaytrap_rapidconstruction` clone origin
  (that record's `_right` bar historically tops on void). The real Darklings<->Dark Aperture link is
  drawn by Darklings' straight bar, so Dark Aperture's own bar should be CLEARED.

### 8.5 build41 vs authoritative - DEVIATION TABLE (the fix lane's Occult work list)

| # | skill | build41 (x,y,row,col,shape,conn) | authoritative older-SV | deviation |
|---|---|---|---|---|
| 1 | Toxic Concoction `drx_scrap` | (128,217) t4 c1 square, bar->AphoticIchor | (128,217) t4 c1 square, same | **NONE** (position/shape/connector byte-identical; only re-enabled in `tabSkillButtons`) |
| 2 | Shadow Stalker `drx_summon_shadow_stalker` | (428,93) t6 c4 square, bar->Channel | (428,93) t6 c4 square, same | **NONE** (byte-identical; re-enabled with Channel + Blade Mastery) |
| 3 | Darklings `drxdarklings` | (328,279) **t3 c3** square, straight bar | **t3 c4** (drxlaytrap slot), t4 empty | **WRONG COLUMN** (col3 = Shadow Link's) -> interleaves Shadow Link family; bar draws stale MIDDLE over occupied Dark Invigoration |
| 4 | Dark Aperture `drxdarklings_darkaperture` | (328,155) **t5 c3** circle req24, BRTR bar | **t5 c4**, circle req24 | **WRONG COLUMN** (with Darklings) + spurious inherited `_right` bar (clear it; augment link is Darklings' bar) |

**Deviation count for the four: 2** (Darklings + Dark Aperture; Toxic Concoction + Shadow Stalker are
clean). Both deviations are the SAME root cause: the Darklings family sits in Shadow Link's column 3.

### 8.6 Corrected Darklings-family column (answers section 5 anchor 6)

- **CONFIRMED:** build41 wrongly parked Darklings + Dark Aperture in **Shadow Link's column 3**.
- **CORRECTION to the 098i note** ("their own overlay column, no canonical layout"): the family HAS a
  canonical older-SV layout - **column 4**, summon-base at t3 + augment at t5 with t4 EMPTY (the
  `drxlaytrap` "Darklings" summon slot in SV 0.41/0.9).
- **Constraint for the fix lane:** build41's literal col4 is now occupied by the **repurposed SAME
  records** `drxlaytrap`=**Breach** (t3) + `drxlaytrap_rapidconstruction`=**Shadow Grasp** (t5), plus
  Shadow Stalker (t6) + Channel (t7). The family cannot literally return to col4. So: **move the
  Darklings family OUT of col3** into a clean column preserving **base@t3 / empty@t4 / augment@t5**
  (Dark Aperture directly above Darklings), and **drop Dark Aperture's stray `_right` bar**. No column
  in build41 m5 is perfectly free, so a small holistic m5 reflow is likely required (ties into the
  build42-reflow revert + Occult rebuild lane).

### 8.7 Broader sweep - other pre-0.98i-sourced content in build41 (lighter pass)

Per mastery: skills DISPLAYED in build41 but NOT displayed in SV 0.98i, classified by their SV 0.9
status. **"hidden_button" = a latent older-SV button re-enabled** (has canonical older-SV identity);
**"build41-new record" = no 0.9/0.41 record** (may still clone an older-SV identity, as Darklings does).
Full lists in `tools/sv_pre098i_occult_ground_truth.json -> broader_sweep`.

| mastery | added-in-b41 (not shown in 098i) | pre-0.98i-sourced (hidden older-SV button) | build41-new record |
|---|---|---|---|
| m1 Warfare | 8 | 4 | 4 |
| m2 Defense | 6 | 4 | 2 |
| m3 Earth | 8 | 4 | 4 |
| m4 Storm | 7 | 5 | 2 |
| m5 Occult | 6 | 4 (Toxic Concoction, Shadow Stalker, Channel, Blade Mastery) | 2 (Darklings, Dark Aperture) |
| m6 Hunting | 4 | 4 (Cornered, Rapid Construction, Tempest, Flayer) | 0 |
| m7 Spirit | 9 | 4 | 5 |
| m8 Nature | 6 | 4 | 2 |
| m9 Dream | 1 | 0 | 1 |

**Takeaway for the fix lane:** the "pre-0.98i-sourced" column is content with genuine older-SV ground
truth (their button records + positions exist in SV 0.9) - do NOT treat these as "Will overlay with no
canonical layout". Notably m6 Hunting's entire build41 addition set (Cornered, Rapid Construction,
Tempest, Flayer) is older-SV latent content, matching the standing "Occult + Hunting hand-tuning"
note. The "build41-new record" column still may clone older-SV identities (Darklings is the proven
case); it is not enumerated deeply here.
