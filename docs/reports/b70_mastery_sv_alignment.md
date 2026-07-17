# b70 - BUILD45 Mastery SV-Alignment (Occult/Hunting/emblem)

**Branch:** `feat/mastery-sv-fix` (worktree `mastery-sv-fix`, off build44 `78bd65c`, arz `439a9279`).
**Module:** `tools/patches/mastery_sv_alignment.py` (apply + verify), registered LAST content module
(before `visuals`) so it is the ratified last writer on every Occult(m5)/Hunting(m6)/emblem UI field.
**Upstream fix-in-place:** `tools/patches/hunting_occult_ui.py` (4 shape assignments flipped, BL-103).
**Golden:** `tools/occult_hunting_golden.json` (+22 owner_approved_overrides; A7 gate GREEN, 74 waived / 0 hard).

**Authority (read-only, both committed):** `tools/sv_mastery_ground_truth.json`,
`tools/sv_pre098i_occult_ground_truth.json`, `docs/reports/sv_mastery_ground_truth.md` (incl. sec 8).
SV098 source verified directly: `upstream/soulvizier_098i/Database/database.arz` (md5 `11773cdc`).

---

## WILL-COMPLAINT -> RESOLUTION table (every item from his build43 screenshot message)

| # | Will complaint (build43 screenshot) | Skill / record | Resolution | Authority |
|---|---|---|---|---|
| 1 | Yellow circles that should be squares (shape law) | see per-skill rows below | fixed-here (A) | SV098 GT + Will 2026-07-16 |
| 2 | Pink arrows / connectors wrong | Darklings, Dark Aperture, Shadow Link | fixed-here (C,D) | pre-098i GT 8.4/8.5 + Will |
| 3 | Poisonous Gas is a circle (was square) | `drxpoisongasbomb` m5 skill13 | **fixed-here**: SQUARE -> CIRCLE (isCircular 0->1) | SV098 GT anchor 4 + Will |
| 4 | Blade Fury should be a square (was circle) | `drxcalculatedstrike_luckyhit` m5 skill06 | **fixed-here**: CIRCLE -> SQUARE | SV098 GT anchor 8 + Will "standalone skill you can call" |
| 5 | Smoke Screen shape wrong | `drxlaytrap_petmodifier_multishotbolttrap` m5 skill18 | **fixed-here**: CIRCLE -> SQUARE | SV098 GT (c1t3 square standalone) |
| 6 | Eviscerate should be a square | `drxtakedown_eviscerate` m6 skill18 | **fixed-here**: CIRCLE -> SQUARE | WILL RULING 2026-07-16 verbatim |
| 7 | Dark Aperture should be a circle | `drxdarklings_darkaperture` m5 skill26 | verified-already-correct (isCircular=1 in build44) + moved column (C) | pre-098i GT 8.3 + Will |
| 8 | Darklings + Dark Aperture in Shadow Link's column | m5 skill25/skill26 | **fixed-here (C)**: moved col3 -> col6 (t3/t5), canonical base@t3/augment@t5; Dark Aperture stray `_right` bar cleared | pre-098i GT 8.5/8.6 + Will |
| 9 | Dark Invigoration should augment Shadow Link | `drxopenwound` m5 skill07 (c3t4) | **PROVEN-ALREADY-TRUE + hardened (D)**: the LIVE occult SkillTree already binds drxopenwound@7 to drxbladehoning@6 by tree-order (TQ's real modifier mechanism); apply() now asserts it fail-loud + verify() re-asserts at mechanism level; build45 UI wire kept. build45's "no gameplay relation" was a VET ERROR (checked record fields, not the SkillTree). Zero arz change. | WILL ruling 2026-07-16 + vanilla TQAE mechanism |
| 10 | Breach / Shadow Grasp | `drxlaytrap`(Breach c4t3) / `drxlaytrap_rapidconstruction`(Shadow Grasp c4t5) | verified-already-correct (build44 = SV098: c4t3 straight bar to c4t5) | SV098 GT m5 |
| 11 | Toxic Concoction - Poisonous Gas - Aphotic Ichor chain | `drx_scrap` c1t4 straight len4 bar up through PoisonGas to Aphotic Ichor | verified-already-correct (build44 byte-matches pre-098i GT) | pre-098i GT 8.4 |
| 12 | Row misalignment | (row geometry Y=465-62*tier) | verified-already-correct: build44 = build41 layout; all buttons grid-valid on the 7-row lattice; the perceived misalignment was downstream of the shape bug (main node drawn as an undersized circle) - resolved by the shape flips (A) | SV098 GT sec 1 |
| 13 | Emblem circle (black disc top-right of every skill window) | `masterybitmap.dbr` x9 | **fixed-here (B)**: BitmapSingle -> BitmapUIAware (bitmapNames=[tex,tex], positions [718,748]/[31,31]) so the portrait renders over the pane's black hole | SV098 GT emblem RCA sec 4 (mirrors proven b60 pane fix) |
| 14 | Earth Soften Metal row | `drxringofflame_softenmetal` m3 skill10 | **verified-already-correct / documented no-op** (see Item E below) | SV098 GT + build41 occupancy |

Legend: fixed-here = changed by this module; verified-already-correct = build44 already matches ground truth; WILL-CONFIRM = flagged, unchanged.

---

## Per-item detail

### A. Shapes (isCircular on the ingameui button record)
All four fixed UPSTREAM in `hunting_occult_ui.py` (BL-103 fix-upstream: Will's 2026-07-16 rulings
supersede his 2026-07-12 shape law for these skills) AND re-asserted + verify()'d by the b70 module
as the ratified last writer. **The golden baseline had already frozen the SV-correct shapes**
(Poisonous Gas circle; Blade Fury/Smoke Screen/Eviscerate square); hunting_occult_ui's 2026-07-12
law drifted them (waived). Reverting to the golden value therefore produces **ZERO net golden drift**.

| skill | button | build44 | -> b70 | golden baseline |
|---|---|---|---|---|
| Poisonous Gas | m5 skill13 | square (0) | **circle (1)** | circle (match) |
| Blade Fury | m5 skill06 | circle (1) | **square (0)** | square (match) |
| Smoke Screen | m5 skill18 | circle (1) | **square (0)** | square (match) |
| Eviscerate | m6 skill18 | circle (1) | **square (0)** | square (match) |

### B. Emblem circle x9
Each mastery's `masterybitmap.dbr`: `templateName` BitmapSingle -> BitmapUIAware, `FileDescription`
-> BitmapUIAware, `bitmapNames`=[current tex, same], `bitmapPositionsX`=[718,748],
`bitmapPositionsY`=[31,31], singular `bitmapName`/`bitmapPositionX`/`bitmapPositionY` dropped. The
`skillPaneMasteryBitmap` slot reads the PLURAL `bitmapNames` (like `skillPaneBaseBitmap`); a
BitmapSingle's singular `bitmapName` is ignored so the pane's black circular hole showed through as a
black disc. **All 9 emblem textures re-verified to resolve in the shipped arcs** (8 base InGameUI, m5
`DRXtextures\masterybackdrops\newstealthpanel01.tex` in mod arc, m9 XPack) - b60-pattern resolver in
`verify()` reported 18/18 (2 refs x 9). Only m5+m6 are golden-tracked (16 waivers); m1-4/7/8/9 are not.

### C. Occult family placement (Darklings + Dark Aperture)
build44: Darklings (skill25) c3t3, Dark Aperture (skill26) c3t5 - Shadow Link's column, interleaving
Dark Invigoration at c3t4. Moved to **column 6** (the ONLY build44 m5 column with BOTH t3 (y279) and
t5 (y155) free - occupancy map below), preserving the canonical pre-098i base@t3 / augment@t5 pattern
(Dark Aperture directly above Darklings; its req 24 == t5). Darklings keeps its canonical straight
`[Bottom,Middle,Top]` bar (re-asserted, byte-identical to golden). **Dark Aperture's stray inherited
`_right` (BRTR) bar CLEARED** (pre-098i GT flags it an artifact topping on void; the augment link is
drawn by Darklings' own bar). UI fields only; zero effect/stat/dependency change.

**build44 m5 occupancy (why column 6):**
```
      c1(128)  c2(228)  c3(328)  c4(428)  c5(528)  c6(628)
t7    PGas_sh   .        .        Channel  Lethal_m  .
t6    .         Toxin    ShLore   Stalker  .         Flurry
t5    PoisGas   Mandrk   [DkAp]   ShGrasp  Nether    ...FREE...   <- Dark Aperture -> here
t4    Scrap     .        DkInvig  .        .         ThrowKnife
t3    Smoke     Night    [Dklg]   Breach   BladeFury ...FREE...   <- Darklings -> here
t2    Flash     .        ShLink   .        .         BladeMastery
t1    .         Envenom  .        .        CalcStr   Agility
```
Only c6 has t3 AND t5 free. **RESIDUAL (WILL-CONFIRM):** c6 t4 holds the CANONICAL SV098 Throwing
Knife (`drxthrowingknife`, c6t4, immovable without a golden waiver), so Darklings' straight bar
passes BEHIND it as an empty-row (Middle) passthrough tile - NOT a Connect nub, so Throwing Knife is
not drawn "into" the chain, but the bar visually overlaps its button. A fully "t4 EMPTY" canonical
column is impossible without either relocating the canonical Throwing Knife (needs Will's ruling) or
a holistic m5 reflow (the build42 reflow that "wrecked the trees" was reverted in build44). This is
the best available column and resolves Will's stated complaint (family OUT of Shadow Link's column).

### C2. Occult COLUMN-6 RESTACK (Will ruling 2026-07-16) - SUPERSEDES the item-C residual

> **Will (2026-07-16, verbatim):** *"lets have darklings be in the same lane as throwing knife, but we
> will have darklings unlock at 10, dark aperture unlock at 16, and then above it we will have throwing
> knife at 24 and the augment to throwing knife at 32 so we wont have lines behind one another."*

The item-C round-1 move put Darklings@t3 + Dark Aperture@t5 into column 6, which already held Throwing
Knife@t4 and Flurry@t6. That INTERLEAVED two 2-tier bars: Darklings' t3->t5 bar crossed Throwing
Knife's button @t4, and Throwing Knife's t4->t6 bar crossed Dark Aperture's button @t5 (the "lines
behind one another" Will called out). Will's fix restacks column 6 (X=628) into a clean
bottom-to-top ladder so each augment sits DIRECTLY above its base and every bar is a 1-tier adjacent
segment:

```
      col 6 (x=628)          BEFORE (build45, interleaved)   AFTER (C2 restack, Will 07-16)
 t6 (y93)   Flurry              Flurry            unlock 32   Flurry            unlock 32  STAYS
 t5 (y155)  ...                 Dark Aperture     unlock 24   Throwing Knife    unlock 24  UP from t4
 t4 (y217)  ...                 Throwing Knife    unlock 16   Dark Aperture     unlock 16  DOWN from t5
 t3 (y279)  ...                 Darklings         unlock 10   Darklings         unlock 10  STAYS
```

Bars become adjacent and parallel-free: **Darklings -> Dark Aperture** spans t3->t4; **Throwing Knife
-> Flurry** spans t5->t6. ZERO crossings.

**What changed (record-diff vs build45 scratch `a659594e`, 5 records):**
| record | field | build45 | -> C2 | why |
|---|---|---|---|---|
| `mastery 5\skill26.dbr` (Dark Aperture button) | bitmapPositionY | 155 (t5) | **217 (t4)** | moves down one row |
| `mastery 5\skill10.dbr` (Throwing Knife button) | bitmapPositionY | 217 (t4) | **155 (t5)** | moves up one row |
| `drxdarklings.dbr` | skillConnectionOn/Off | len3 `[Bottom,Middle,Top]` | **len2 `[Bottom,Top]`** | 2-tier bar -> 1-tier adjacent |
| `drxthrowingknife.dbr` | skillConnectionOn/Off | len3 `[Bottom,Middle,Top]` | **len2 `[Bottom,Top]`** | 2-tier bar -> 1-tier adjacent |
| `drxthrowingknife.dbr` | skillTier | 4 | **5** | new row t5 (TIER LAW) |
| `drxthrowingknife.dbr` | skillMasteryLevelRequired | 5 | **24** | unlock gate == t5 threshold (Will "at 24") |
| `drxdarklings_darkaperture.dbr` | skillTier | 5 | **4** | new row t4 (TIER LAW) |
| `drxdarklings_darkaperture.dbr` | skillMasteryLevelRequired | 24 | **16** | unlock gate == t4 threshold (Will "at 16") |

Darklings (tier 3, gate 10 via req 0 -> tier default) and Flurry (tier 6, gate 32) were already
correct - verified fail-loud, not written. The len2 `[Bottom,Top]` bar is byte-identical to the
vanilla Shadow-Stalker -> Channel adjacent bar (probed from the live occult tree).

**TIER LAW confirmed empirically** (not assumed): `skillTier` == the button's row across all 27
column-6 lattice skills AND 142 vanilla mastery buttons (0 violations). The row<->unlock ladder is
`tier {1:1, 2:4, 3:10, 4:16, 5:24, 6:32, 7:40}`. So t3=unlock 10, t4=16, t5=24, t6=32 - exactly the
numbers Will named.

**GATE MECHANISM (why BOTH `skillTier` and `skillMasteryLevelRequired` are written).** `skillTier` is
the effective mastery-investment gate; `skillMasteryLevelRequired` is at most a `max()`-gate. Proof
that req is NOT the sole gate: vanilla player modifiers sit FAR below their base tier -
`rainoffire_brimstone` tier6(thr32)/req15, `dream_slowtime` tier7(thr40)/req16, `nature_wildhunt`
tier7/req1 - a modifier physically cannot unlock before its base, so the engine must gate on
`skillTier`, not req. But Dark Aperture's leftover req=24 (== its OLD t5 threshold) could still bind
it at 24 under `max()`-semantics, contradicting Will's "unlock at 16." Setting **both** fields ==
the new-row threshold makes the unlock unambiguous under skillTier-only, `max()`, or req-only
semantics alike (this is also how 206 vanilla skills set req == tier threshold). This is required to
honor Will's explicit unlock numbers - it is not scope creep. (The build45 record-diff shape "skillTier
only" did not anticipate the leftover req; leaving it would leave Dark Aperture gated at 24.)

**MECHANISM LAW (modifier binding) - untouched + proven intact.** The engine binds a `Skill_Modifier`
to its base PURELY by the mastery SkillTree's numeric `skillName{N}` ORDER (nearest preceding
non-modifier; item D). This restack changes ONLY UI button positions + the skill records' skillTier /
gate / connector fields - it does **NOT** reorder or renumber ANY `drxstealthskilltree.dbr` slot. The
live occult tree still orders `drxdarklings@26 -> drxdarklings_darkaperture@27` and `drxthrowingknife@9
-> drxthrowingknife_flurryofknives@10`, so **Dark Aperture still augments Darklings and Flurry still
augments Throwing Knife** after the restack (apply() asserts + verify() re-asserts both bindings at
mechanism level; a SkillTree reorder would fail the build). No skill has a `skillDependancy` /
`buffSkillName` / `petSkillName` pointing at either moved skill (swept: 0 external refs), so the moves
have no downstream wiring impact. Save-safe: mastery-tier gates resolve live from the record at load;
no persisted per-character state encodes a skill's row.

**Golden (A7):** +10 owner_approved_overrides, each citing Will's 2026-07-16 ruling verbatim - 2 button
`bitmapPositionY`, 2 `drxdarklings` connectors, `drxthrowingknife` {connOn, connOff, skillTier,
skillMasteryLevelRequired}, `drxdarklings_darkaperture` {skillTier, skillMasteryLevelRequired}. (Dark
Aperture's connectors were already waived in item C round 1; they stay cleared.)

**Verification (C2 round):** py_compile + registry selfcheck (26 modules) OK; dry-run replay vs
`a659594e` = EXACTLY the 5-record restack above (2 button Y + 2x len2 connector pairs + 2 skillTier +
2 gate), ZERO other deltas; verify() PASS incl. the mechanism-level binding assertions + TIER-LAW +
adjacent-bar checks; three NEGATIVE tests FAIL as required (plant a len3 crossing bar on Throwing
Knife; over-gate Dark Aperture to 24 on t4; misrow the Throwing Knife button to t4). Full scratch
build EXIT 0 (26 registry verifies OK), arz md5 `a7d46b532a5dcf4732e7f951ee695f2d`; A7 golden gate PASS
(84 waived / 0 hard); record-diff vs `a659594e` = 0/0/5 (exactly this restack, ZERO other deltas);
contracts souls+summons GATE PASS; validate_tags PASS. See the C2 gate record in BACKLOG.

### D. Dark Invigoration = TRUE modifier of Shadow Link (Will ruling 2026-07-16)
> **Will (2026-07-16, verbatim):** *"so how does dark invigoration work? I think it should augment
> shadow link."* Build45 drew the visual connector but the vet concluded "no gameplay relation exists."
> This round proves that conclusion was **WRONG** and that the augment is **already real**.

**THE MECHANISM (proven from vanilla TQAE `database.arz`, make-or-break step).** The engine binds a
`Skill_Modifier` to its base skill **purely by the mastery SkillTree record's numeric `skillName{N}`
ordering** - a modifier attaches to the **nearest lower-indexed non-modifier** skill. There is **no
back-reference anywhere else**: not on the modifier record, not on the base record, not on the UI
button. Proof by elimination + genuine pairs:

- Vanilla **Heart of Frost** (`stormnimbus_heartoffrost`) and **Static Charge**
  (`stormnimbus_staticcharge`) - the canonical toggled-aura modifiers - carry **zero** reference to
  Storm Nimbus (dumped every field: only their own icons/stats; no `skillDependancy`, no `buffSkillName`
  pointing at the base). Storm Nimbus carries no reference to them. Their UI buttons
  (`mastery 4/skill05,06`) carry only their own `skillName` + position. **The ONLY datum linking them
  to Storm Nimbus is `stormskilltree.dbr` slot order: StormNimbus@8 -> HeartofFrost@9 -> StaticCharge@10.**
  Since the game demonstrably links them, tree-order is the mechanism (nothing else could be).
- Confirmed on **6+ vanilla base+modifier groups across 3 masteries**: Warfare `WarWind@3 ->
  WarWind_Lacerate@4`, `Onslaught@10 -> IgnorePain/Hamstring/Ardor@11-13` (3 modifiers, all bind to
  Onslaught - proving "nearest **preceding non-modifier**", since @12/@13's immediate predecessor is
  itself a modifier), `BattleRage@14 -> CrushingBlow/CounterAttack@15-16`; Defense `Rally@6 ->
  Inspiration/Defiance@7-8`, and **decisively `BattleAwareness@13 (Skill_BuffRadiusToggled - Shadow
  Link's EXACT class) -> Focus/IronWill@14-15`** (a toggled aura modified by `Skill_Modifier`s - the
  precise vanilla precedent for Shadow Link). Negative: mastery/passive skills (`WeaponTraining`,
  `Skill_Mastery`) are non-modifiers and bind nothing.

**CURRENT-BINDING FINDING (corrects the build45 vet).** The **LIVE** occult SkillTree
`records\skills\stealth\drxstealthskilltree.dbr` (referenced by both PCs' `skillTree5` field =
`records\xpack\creatures\pc\{male,female}pc01.dbr` = mastery 5) already orders:

```
  6  drxbladehoning.dbr   Skill_BuffRadiusToggled   (Shadow Link  - BASE, valid modifier base)
  7  drxopenwound.dbr     Skill_Modifier            (Dark Invigoration - MODIFIER)  <- binds to @6
  8  drxanatomy.dbr       Skill_Modifier            (Shadow Lore  - MODIFIER)       <- binds to @6
```

So **Dark Invigoration ALREADY binds to (augments) Shadow Link** - exactly like StormNimbus@8 ->
HeartofFrost@9 -> StaticCharge@10. Its `offensiveLifeMin` (flat vitality/Life damage 3..42) +
`offensiveSlowBleeding` (bleed DoT) fold into the character while Shadow Link's toggled aura is up, the
**same way** Heart of Frost's `offensiveColdModifier` folds in while Storm Nimbus is toggled - and it
pairs thematically with Shadow Link's aura (a `-Vitality Resistance` debuff on nearby enemies, b57).
**It is functional, not dead weight.** The build45 "no gameplay relation exists" line checked record
cross-references (`skillDependancy`/`buffSkillName`), which is **not** TQ's modifier-binding surface -
a vet error.

**What this round changes.** *Nothing in the arz* (the augment was already present in build44 AND
build45 - the scratch rebuild is **byte-identical, md5 `a659594e`**). Mirroring Heart of Frost requires
**only** tree-order + the UI shape - adding any record-level field would **deviate** from the vanilla
shape, so no new golden override is needed. This round: (1) `apply()` now **asserts** the tree-order
binding **fail-loud** (the module is the ratified GUARANTOR - a future reshuffle that put a non-modifier
between Shadow Link and Dark Invigoration would fail the build); (2) `verify()` re-asserts it at
**mechanism level** (walks the live SkillTree, proves `nearest-preceding-non-modifier(drxopenwound) ==
drxbladehoning`) + negative test; (3) the build45 UI wire is **kept** - it now correctly depicts the
real augment.

**UI shape (kept from build45, already the vanilla Storm Nimbus column shape).** All in **column 3**:
Shadow Link (skill09, t2/y341, **square** base) -> Dark Invigoration (skill07, t4/y217, **circle**
modifier) -> Shadow Lore (skill08, t6/y93, **circle** modifier), Shadow Link owning the straight
`[Bottom,Middle,Top]` bar drawing UP. Identical stacked base-square + modifier-circles + bar as vanilla
StormNimbus/HeartofFrost/StaticCharge.

**Doubled-namespace resolution.** A twin SkillTree exists at
`records\skills\skills\stealth\drxstealthskilltree.dbr` but is referenced by **no PC/record** (dead
orphan; ends at slot 25, lacks the Darklings entries). Gameplay reads the **live** stealth tree only,
so there is **no live/dead split** - the binding holds on the record the mastery actually uses. The
twin is left untouched (editing it would be inert); its order happens to match anyway.

### E. Earth Soften Metal - NO-OP (documented)
The task brief's literal target is "c4t3 -> c4t2 (SV=c4t2)". **Direct read of SV098
(`upstream/soulvizier_098i`) shows Soften Metal (`drxringofflame_softenmetal`) at c4 tier3 (x428,
y279)** - i.e. SV098 = c4t3, NOT c4t2 (the brief's "SV=c4t2" is a transcription inversion; GT 7a
also reads "SV c4t3 -> build41 c4t2"). build44 has it at **c4t2 (x428, y341)** already. So:
- Under the brief's LITERAL target (c4t2): already satisfied -> verified-already-correct, no change.
- Under SV098 ground truth (c4t3): the move is BLOCKED - build44's c4t3 is occupied by build41's
  INTENTIONAL restored **Flame Surge line** (`drxrupture`, a build41-new addition per pre-098i GT
  broader_sweep m3; c4 now holds RingofFlame t1 / SoftenMetal t2 / Flame Surge t3 / Rupture_burning
  t4 / Rupture_flare t5 / Spont.Combustion t6 / FireNova t7). Moving Soften Metal to c4t3 would
  collide with restored content ("additions are NOT deviations"). Soften Metal's c4t2 rest position
  is a necessary consequence of the Flame Surge restoration, not a bug.
**Decision: NOT changed** (either reading yields no-op). Flagged for Will if he wants a holistic
Earth col-4 reflow to restore the exact SV c4t3 slot at the cost of moving the Flame Surge line.

### F. Verify-only chains (build44 already correct)
- **Toxic Concoction** (`drx_scrap`, c1t4): straight len4 `[Bottom,Connect,Middle,Top]` bar UP through
  Poisonous Gas (c1t5, CONNECT tile) to Aphotic Ichor (c1t7) - byte-matches pre-098i GT 8.4. Unchanged.
- **Shadow Stalker** (`drx_summon_shadow_stalker`, c4t6): straight len2 bar to Channel (c4t7). Unchanged.
`verify()` re-asserts both on the final arz.

### G. Roster-wide canonical audit (report-only)
Per SV098 GT section 7b, the ONLY shape/move deviations of ground-truthed skills vs SV are items
A-E. Every other build44-vs-SV098 difference is an intentional build41 legacy-skill restoration
(Meteor, Force of Nature, Skeletal Soldier, Sands of Sleep, Distortion Wave, Cleave, Cold Aura, Bone
Fiend, Flame Surge, ...) - additions, NOT deviations. **No further unambiguous non-golden GT mismatch
was found.** The occupancy sweep of m5 (above) and m3 (Item E) confirmed no stray position/shape drift
of a ground-truthed skill beyond A-E. Nothing ambiguous required a WILL-CONFIRM change; all judgment
calls (Item C residual, Item D gameplay-relation, Item E) are documented above rather than silently changed.

---

## Golden overrides added (22 new, all Occult m5 / Hunting m6, A7-sanctioned)
- **16x** `field::...mastery {5,6}\masterybitmap.dbr::{templateName,FileDescription,bitmapName,bitmapNames,bitmapPositionX,bitmapPositionY,bitmapPositionsX,bitmapPositionsY}` - Item B emblem conversion (SV098 GT sec 4).
- **2x** `field::...mastery 5\skill{25,26}.dbr::bitmapPositionX` (328->628) - Item C family move (pre-098i GT 8.5).
- **2x** `field::...drxdarklings_darkaperture.dbr::skillConnection{On,Off}` (_right bar -> cleared) - Item C (pre-098i GT).
- **2x** `field::...drxbladehoning.dbr::skillConnection{On,Off}` (straight wire added) - Item D (WILL directive 2026-07-16).
Item-A shape fields need NO new override (they revert to the frozen golden baseline = zero drift).
**Item-D true-augment round (2026-07-16) adds NO new override**: the gameplay binding is SkillTree
tree-order (already present, zero arz change); mirroring Heart of Frost requires only tree-order + the
already-waived UI wire, so there is no new golden-frozen field to sanction.

## Verification (all GREEN)
- `py_compile` (module + hunting_occult_ui + __init__) + registry selfcheck (26 modules) + golden JSON valid.
- Dry-run replay (module applied to build44 arz): record-diff = **17 modified records, ALL UI/connector
  fields, ZERO gameplay/stat deltas**; every delta maps to a fix-list item (9 emblems + 4 shapes + 2
  family positions + 2 Dark-Aperture-conn + 2 Shadow-Link-conn = 21 field-groups on 17 records).
- A7 golden freeze gate: **PASS (74 waived, 0 hard)** via the exact build code path.
- `verify()` negative test: flipping Poisonous Gas back to square -> `verify()` FAILS as required.
- Full DB build + in-build gate battery: see BUILD45 gate record in BACKLOG (arz md5 recorded there).

### Item-D true-augment verification round (2026-07-16, `feat/mastery-sv-fix`)
- **Mechanism proof:** decoded vanilla TQAE `database.arz` - Storm Nimbus/Heart of Frost/Static Charge
  (toggled-aura precedent) + Warfare (WarWind, Onslaught x3, BattleRage) + Defense (Rally,
  **BattleAwareness = Skill_BuffRadiusToggled + Focus/IronWill**) - proving modifier<->base binding is
  the SkillTree numeric `skillName{N}` order (nearest preceding non-modifier), with zero record/UI
  back-reference. Negative: `Skill_Mastery`/`Skill_Passive` bind nothing.
- **Current binding:** live occult tree `drxstealthskilltree.dbr` (PC `skillTree5`) already orders
  drxbladehoning@6 -> drxopenwound@7 -> drxanatomy@8; `_modifier_binding_base(occult, drxopenwound) ==
  drxbladehoning.dbr`. Dead twin `...skills\skills\stealth\...` referenced by nobody.
- **apply() assertion** (fail-loud tree-order guarantor) + **verify() mechanism-level assertion** pass
  on the final assembled arz during the full build (registry verify `mastery_sv_alignment` OK).
- **Negative test:** planting a non-modifier into base slot 6 -> `verify()` FAILS with the exact
  `[D] ... tree-order binding base=... want drxbladehoning.dbr` message.
- **Full scratch DB build** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`) EXIT 0, all 26 registry verifies
  OK, A7 golden gate **PASS (74 waived, 0 hard)**, arz md5 **`a659594ed85f8f5609bcab57fa7b757b`**
  (BYTE-IDENTICAL to build45 -> the true augment was already present; this round is verify + docs only).
- **record-diff vs build45 scratch `a659594e`** = **0 ADDED / 0 REMOVED / 0 MODIFIED** (exactly this
  change: nothing in the arz).
- **contracts** (souls+summons, full resources+Text.arc) **GATE PASS** (0 P0 / 0 P1 / 112 P2, no new;
  map/quests unchanged - DB-only wave). **validate_tags PASS** (2 pre-existing base monster-name WARNs,
  non-blocking).
