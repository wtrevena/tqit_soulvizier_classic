# Mastery / Skill-Tree UI Invariants (vanilla ground truth)

**Author:** INVARIANT DERIVER, 2026-07-14. Branch `feat/mastery-ui-vet`.
**Law source (ground truth):** the **base-game** `database.arz`
(`C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz`,
74,013 records, read-only) + the base `InGameUI.arc` (skill-pane textures).
**Cross-reference:** build40 golden mod arz `SoulvizierClassic.arz` (md5 `b33c5a44`) is the
*subject* our fixes ship against; it is **not** used here as a law source. This document derives
the LAWS the mod must honor; it does **not** audit the mod (that is the next lane).
**Method:** pure-Python replay with `tools/arz_patcher.ArzDatabase` + `tools/arc_patcher.ArcArchive`
(no game, no heavy build). Every number below is reproducible from the probes described inline.

These are the two laws Will mandated (2026-07-14) plus the select-screen mechanics, each reduced to a
**field-level, machine-checkable invariant** an auditor can run against any arz.

> ### ⚠️ CORRECTION (2026-07-14, MASTERY UI AUDITOR - supersedes section 2 below)
> The build40 mod-audit lane found this document's **connector mechanism is wrong** and its **grid is
> one row short**. Corrected against the base game (see `docs/reports/mastery_ui_vet_audit.md` §1):
> 1. **The connector is a real skill-record field, NOT baked background art.** Every base/chain skill
>    carries `skillConnectionOn` = `InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex`,
>    `skillConnectionOff`, and `skillConnectionSpacing` = **62** (one row pitch). 43 vanilla skills set
>    it. Section 2a missed it because it searched textures for `connect` - the connector texture is
>    named `SkillBar**Bottom**On`, not `skillbarconnect` (that 15x62 asset is the mastery-level bar).
> 2. **Direction:** `skillConnectionOn` sits on the **base** (bottom of a chain, high Y) and the bar
>    draws **upward** to the modifier(s) stacked directly above in the same column. Modifiers carry no
>    connector. Not every base sets it (vanilla `rally`, `battleawareness` don't), so a *missing*
>    connector is not a defect. The mod adds a side variant `skillbarbottomon01_right.tex` for a
>    modifier that connects diagonally to an adjacent column.
> 3. Section 2b is still correct that `skillDependancy` is a gameplay prereq, not the visual link; the
>    error was concluding the lines are therefore baked art.
> 4. **GRID:** vanilla uses 6 rows (tiers 1-6, Y {403..93}). The **mod adds a 7th row Y=31 = tier 7**
>    (`Y = 465 - 62*tier`). The auditor ladder is `{403:1,341:2,279:3,217:4,155:5,93:6,31:7}`.
>
> The operative CONNECTOR-LAW check (section 2c positional rules) is unchanged and remains valid; only
> the *mechanism* description (2a) and the row set were wrong.
>
> **UPDATE (2026-07-14, TEXTURE DECODER):** the pixels are now decoded and confirm the correction.
> The 919x540 backgrounds bake only the 6 tier *shelves* (62 px pitch), **no connector lines**; the
> connector is the runtime `skillConnectionOn` bar, which reaches the **nearest occupied cell above**
> (same column for the straight `SkillBarBottomOn01.tex`, column-right for the DRX
> `SkillBarBottomOn01_right.tex`). The authoritative per-mastery CONNECTION MAP + the exact legal cells
> for the reflow live in **`docs/reports/mastery_connection_maps.md`** + `tools/mastery_connection_maps.json`
> (built by `tools/build_connection_maps.py`, decoded by `tools/tex_decode.py`). Section 2a's
> "lines baked into the background" wording is formally **refuted** there.

---

## 0. Record topology (how a mastery's UI is assembled)

Base game has **8 classic masteries** under `records\ingameui\player skills\mastery {1..8}\`
plus the **Dream** mastery (Ragnarok / XPack3) under `records\xpack\ui\skills\mastery 9\`.
Slot order is the base game's own: **1 Warfare, 2 Defense, 3 Earth, 4 Storm, 5 Rogue/Stealth,
6 Hunting, 7 Spirit, 8 Nature, 9 Dream.**

Each mastery folder holds exactly **26 records** (Dream mirrors the same set):

| record | template | role |
|---|---|---|
| `panectrl.dbr` | `SkillPaneCtrl.tpl` | the pane controller: lists the buttons + names the title/desc tags + the backgrounds |
| `mastery.dbr` | `SkillButton.tpl` | the mastery button (bottom-left node) |
| `masterybar.dbr` | `BarGraph.tpl` | the mastery-level progress bar (left edge) |
| `masterybitmap.dbr` | `BitmapUIAware.tpl` | decorative mastery art (right side of the pane) |
| `skill01.dbr` .. `skill20.dbr` | `SkillButton.tpl` | the 20 skill buttons |
| `skillpanebasebitmap.dbr` | `BitmapUIAware.tpl` | the **full-pane background** (`bitmapName` -> `<Class>SkillBackground01.tex`) |
| `skillpanereallocationbitmap.dbr` | `BitmapUIAware.tpl` | the reallocation-mode background |

`panectrl.dbr::tabSkillButtons` is the authoritative ordered button list:
`[Mastery.dbr, Skill01.dbr, ..., Skill20.dbr]` (21 entries). A button is placed **only** if it is in
this list; the `skillNN.dbr` file number is just a slot id, unrelated to tier or column.

**A `SkillButton.tpl` button record carries** (field inventory, base game):

| field | dtype | meaning |
|---|---|---|
| `skillName` | string | path to the gameplay skill record it represents |
| `bitmapPositionX` | int | **column** anchor (px, pane-local) |
| `bitmapPositionY` | int | **row / tier** anchor (px, pane-local) |
| `isCircular` | bool | frame shape (1 = round = passive/proc/modifier; 0 = square = cast active) |
| `bitmapNameUp/Down/InFocus` | string | the button frame border (round vs square family) |
| `skillOffsetX/Y` | int | icon inset inside the frame (always 4/4 in vanilla) |
| `soundNameDown` | string | click sound |

The **icon** lives on the *skill* record (`skillName` target), not the button:
`skillUpBitmapName` / `skillDownBitmapName`. Name/description live there too
(`skillDisplayName` -> a `tag...` , `skillBaseDescription` -> a `tag...`).

---

## 1. TIER LAW  - vertical row == mastery-tier == "how many points is needed"

> Will: *"every skill is on the right level vertically on the page based on how many points is
> needed for it."*

### The invariant (proven, zero exceptions)

A skill button's **`bitmapPositionY` places it in a fixed tier row**. The row<->tier map is a rigid
arithmetic ladder, **identical across all 8 classic masteries AND Dream**:

```
Y = 465 - 62 * tier          (row pitch = 62 px)

 tier 1  -> Y 403      tier 4 -> Y 217
 tier 2  -> Y 341      tier 5 -> Y 155
 tier 3  -> Y 279      tier 6 -> Y  93
 (mastery button: Y 459, the base row - see Exceptions)
```

The distinct skill-button Y values in vanilla are **exactly** `{403, 341, 279, 217, 155, 93}` and the
distinct X values are **exactly** `{128, 228, 328, 428, 528, 628}` (column pitch = 100 px, first
column at 128) - a fixed **6-column x 6-row grid**. No vanilla skill button sits off this grid.

**Proof.** Every base skill/modifier record carries a `skillTier` field (the tier index). Across
**all 9 masteries**, **142** buttons whose `skillName` target has `skillTier` set were checked against
the tier implied by their Y row: **0 violations** (126 in the 8 classic masteries + 16 in Dream). i.e.
every skill at Y=403 has `skillTier==1`, every skill at Y=341 has `skillTier==2`, ... every skill at
Y=93 has `skillTier==6`. Holds for Warfare, Defense, Earth, Storm, Rogue, Hunting, Spirit, Nature, and
Dream (mastery 9 uses the same grid and `xtag*` tags). Zero off-grid skill buttons across all 9.
*(reproduce: `py tools/derive_mastery_ui_invariants.py` -> `implied_tier(Y) == skillTier` sweep,
0/142.)*

### `skillTier` vs `skillMasteryLevelRequired` (do not conflate)

Two different fields live on the skill record:

- **`skillTier`** - the **row index** (1..6). This is the authoritative "vertical level" signal and is
  what must agree with `bitmapPositionY`. It is set on every "primary" skill and every named modifier.
- **`skillMasteryLevelRequired`** - the **per-skill mastery-level gate** (the actual number of points
  you must have in the mastery to put the FIRST point in *that specific* skill). It is **not** constant
  within a row and is **not** the row determinant. Example (Warfare tier-3 row, Y=279):
  `BattleRage_CrushingBlow` req=10, `WarWind` req=15, `BattleStandard` req=0 - same row, different gates.
  It broadly rises with tier (Warfare per-tier max req: 1, 5, 15, 24, 25, 30) but is not monotonic
  per-skill and must **not** be used to derive the row.

**Auditor's TIER-LAW check:** for every skill button, `implied_tier(bitmapPositionY)` (via the ladder
above) **must equal** the `skillName` target's `skillTier` (when `skillTier` is present and > 0). A
mismatch = a skill on the wrong vertical level = a TIER-LAW violation. *(This is exactly the class of
defect the Earth "Rupture" graft produced: a base skill sitting at Y=93/tier-6 above its own
modifiers.)*

Some buttons have **no `skillTier`** (toggled auras/buffs, pet-modifiers, chain/fork secondaries -
classes `Skill_Buff*`, `Skill_AttackBuff*`, `SkillSecondary_*`). They are still placed by Y onto a
valid grid row; the check simply skips the `skillTier` comparison for them and relies on the grid +
column rules.

---

## 2. CONNECTOR LAW - a drawn connection == a genuine base<->modifier augment

> Will: *"the only skills that should be connected together should be ones that genuinely augment one
> another."*

### 2a. What draws a connection (the mechanism)

**There is NO connection/dependency field on any UI record.** Exhaustive field dumps of `panectrl.dbr`,
`mastery.dbr`, and the `skillNN.dbr` buttons show the SkillButton schema is
`{skillName, bitmapPositionX/Y, isCircular, 3 border bitmaps, skillOffsetX/Y, soundNameDown}` - nothing
that references another button or draws a line.

**The visual connecting lines are baked into the per-mastery background art.** Evidence:

1. `skillpanebasebitmap.dbr::bitmapName` -> `<Class>SkillBackground01.tex`, which is a single
   **919 x 540** DDS (base `InGameUI.arc`) - i.e. the **entire skill pane** (skill grid occupies
   X 128..~692 / Y 93..~523; the decorative mastery art sits at X 718+; 919x540 covers both). The lines
   between skill slots are part of this one image.
2. There is **no skill-to-skill connector or "arrow" texture** anywhere in `InGameUI.arc`. The only
   `*connect*` assets are `icons\skills\skillbars\skillbarconnect{on,off}01.tex` - **15 x 62** tiles
   (62 px = one row pitch) that build the segmented **mastery-level bar** (`masterybar.dbr`), with
   on/off states for bar fill. The `arrow` textures are all quest / NPC / tutorial / compass art, none
   for the skill tree.
3. Consequently a connection is realized purely by a button sitting on the grid cell that the painted
   background wires to its neighbor. Move a skill off its intended cell and it either loses its line or
   lands on a line meant for a different skill -> the "wrong connections / arrows" Will reports.

*(Certainty note: the elimination is exhaustive - no connection record, no connector/arrow texture,
`skillDependancy` disproven below - so the lines are in the 919x540 background OR the "connection" is
pure visual grouping of a modifier stacked on its base. **Both readings yield the identical operational
invariant in 2c.** The one thing not eyeball-verified here is rendering the DDS to see the painted
lines; it does not change the invariant.)*

### 2b. `skillDependancy` is NOT the connector (proven negative)

The skill records DO have a `skillDependancy` field, but it is a **gameplay prerequisite, not the
visual link.** Across the 8 masteries only ~22 skills set it, and it points at *hidden weapon skills*
as often as at a visible base:

- `TakeDown`, `Marksmanship`, `TakeDown_Eviscerate`, `CalloftheHunt_Cunning`, `Ternion`,
  `Ternion_ArcaneLore` ... -> `WeaponSkill_DoubleDraw` (a hidden bow/spear weapon-requirement skill).
- `WeaponPool_Disable` -> `SingleWeaponSkill01`; `WeaponPool_Pulverize` -> `ShieldFightingSkill01`.
- `LightningBolt_ChainLightning` -> `LightningBolt`; `Regrowth_Dissemination` -> `Regrowth`
  (chain/secondary skills).

Crucially, the clearest **visual** modifiers have **no** `skillDependancy` at all:
`Onslaught_IgnorePain/Hamstring/Ardor`, `StormNimbus_HeartofFrost/StaticCharge`, and **all 16**
`SkillSecondary_PetModifier` pet-augments. So `skillDependancy` neither covers nor matches the drawn
augment lines. **Do not treat `skillDependancy` as the connector.** (It is a real gameplay gate and must
be preserved, but it is orthogonal to the CONNECTOR LAW.)

### 2c. The genuine-augment relationship (what a connection MUST mean)

In vanilla the augment relationship is encoded structurally and honored positionally:

- **Identity:** a skill is a *modifier/augment* of a base when its record name is `<base>_<suffix>`
  (e.g. `Onslaught_IgnorePain`, `VolcanicOrb_Immolation`, `Wolf_PetModifer_Maul`) and/or its `Class` is
  a modifier class (`Skill_Modifier`, `Skill_ProjectileModifier`, `SkillSecondary_*`). The `<base>`
  prefix is a real skill button in the same mastery.
- **Placement (proven, zero exceptions):** the modifier is placed in the **same X-column as its base**,
  at a **higher tier (lower Y)**. Sweeping all 9 masteries for modifier records whose base prefix is a
  present button: **75 of 75 sit in their base's exact column; 0 in a different column** (66 in the 8
  classic masteries + 9 in Dream). Modifier chains stack contiguously up a column above the base (e.g.
  Hunting spear column 428: Take Down -> Eviscerate -> Tempest -> Flayer).

**Auditor's CONNECTOR-LAW checks:**
1. **Every modifier is column-aligned with its base.** For each button whose skill is a modifier of a
   base skill present in the same mastery, `modifier.bitmapPositionX == base.bitmapPositionX` and
   `modifier tier > base tier`. Violation = a connection that will draw to the wrong place or not at all.
2. **No foreign interleave in a base's column.** Within a base's column, the cells between the base and
   its top modifier should not be occupied by an *unrelated* line's skill (that stray skill inherits a
   spurious painted connection). Violation = a spurious connection.
3. A pair that is **not** a genuine augment (different base prefix, non-modifier class, and no
   `skillDependancy` between them) must **not** be column-stacked as if it were - that is the "connected
   things that don't augment each other" Will forbids.

**Negative control (adjacent-but-unconnected):** vanilla routinely puts *independent* skills in the
same column with NO connection between them, and they are always the low rows of the column, never
interleaved into another line. e.g. Warfare column 128: `WeaponTraining` (tier1, standalone passive)
and `DualWeaponTraining` (tier2, an independent weapon-pool base) sit at the bottom, then the
`DualWieldTechnique_*` chain above - `WeaponTraining` is adjacent to but not connected to
`DualWeaponTraining`. This is legal precisely because neither is named `<other>_...` and the chain that
owns the connections (`DualWieldTechnique_*`) is contiguous above its own base. Adjacency alone never
implies a connection; the connection is the base+`_suffix` column stack.

---

## 3. SELECT-MASTERY SCREEN - which records/tags drive each slot

Two distinct surfaces, two distinct tag families. **Do not confuse them** (this is the root of backlog
B-MASTERY-LABEL-1: the Occult label bug is a `tagMasteryBrief0N` / `tagMasteryTitle0N` /
`tagSkillName0NN` collision, all three of which are wired below).

### 3a. The mastery-SELECT screen (choose-a-mastery)

Controller: `records\ingameui\player skills\select mastery\masterypane.dbr` (`MasteryPane.tpl`). Its
list fields are indexed by mastery slot N (1..8; the Dream/xpack pane extends to 9):

| field | per-slot target | drives |
|---|---|---|
| `masteryMasteryButtons[N]` | `select mastery\mastery{N}button.dbr` (`ButtonStatic.tpl`) | the clickable mastery **icon** - its `bitmapNameUp/Down/InFocus/Disabled` -> `<Class>Button{Up,Down,Over,Disabled}01.tex` |
| `masteryMasteryText[N]` | `select mastery\mastery{N}text.dbr` (`TextStaticString.tpl`) | the short **label** under the icon - its `textTag` -> **`tagMasteryBrief0N`** |
| `masteryMasterySelectedDescriptionTags[N]` | (inline tag) | the **description** shown when that mastery is selected -> **`tagMasteryDescription0N`** |
| `masteryMasterySelectedBitmapNames[N]` | (inline tex) | the large **preview panel** art -> `<Class>PanelLarge01.tex` |
| `masteryTabTitle` | (inline tag) | the screen title -> `tagSkillMasterySelect` |
| `masteryDefaultTextTag` | (inline tag) | default/idle description -> `tagMasteryMessage` |

So a mastery's select-screen identity = **`tagMasteryBrief0N` (label) + `tagMasteryDescription0N`
(description) + `<Class>Button*01.tex` (icon) + `<Class>PanelLarge01.tex` (preview).**

### 3b. The mastery-TREE screen (after selection: the skill pane)

Driven by that mastery's `panectrl.dbr`:

| field | drives |
|---|---|
| `skillTabTitle` | the pane title (top of the skill pane) -> **`tagMasteryTitle0N`** |
| `skillPaneDescriptionTag` | the pane's description tag -> **`tagMasteryDescription0N`** (shared with the select screen) |
| `skillPaneBaseBitmap` / `skillPaneBaseReallocationBitmap` | the pane backgrounds (`<Class>SkillBackground01` / `...ReallocationBackground01`) |
| `skillPaneMasteryBitmap` | the right-side decorative mastery art |
| `masteryBar` | the mastery-level bar record |

And the **mastery skill** record itself (e.g. `Records\Skills\Warfare\WarfareMastery.dbr`,
Class `Skill_Mastery`) supplies:

- `skillDisplayName` -> **`tagSkillName00N`** (the mastery NAME, e.g. "Warfare" - shown on the mastery
  button tooltip / pane).
- `skillBaseDescription` -> `tagSkillDescription00N`.
- `MasteryEnumeration` -> `Mastery<Class>` (engine mastery id).
- `skillUpBitmapName` / `skillDownBitmapName` -> `<Class>MasteryBtn{Up,Down}01.tex` (the in-tree mastery
  node icon).

**Takeaway for B-MASTERY-LABEL-1:** a single mastery's on-screen text is fed by **three independent
tags** - `tagMasteryBrief0N` (select label), `tagMasteryTitle0N` (tree title), `tagSkillName00N`
(mastery name) - each resolved from `Text.arc`. A duplicate/first-wins definition in the text pipeline
mislabels the mastery on whichever surface reads the shadowed tag. Any label fix must set all three
consistently and guard against duplicate tag emission.

---

## 4. EXCEPTIONS & edge cases (must be encoded in any gate)

1. **The mastery button** (`mastery.dbr`): at `(X=29, Y=459)`, `isCircular=1`, its skill's
   `skillTier=0`. X=29 is left of column-0 (128) and Y=459 is below tier-1 (403) - it is the special
   base node in the mastery-bar lane, **off** the 6x6 skill grid. Exclude it from TIER/grid/column
   checks.
2. **Tier-less skills** (toggled auras/buffs, pet-modifiers, chain/fork secondaries): no `skillTier`
   field. Still on a valid grid row; skip only the `skillTier==implied_tier` comparison for them.
3. **`skillMasteryLevelRequired` != tier.** It is a per-skill gate that varies within a row; never
   derive the row from it (see 1).
4. **Dream = mastery 9** lives under `records\xpack\ui\skills\mastery 9\` (not `...\mastery 9`) and uses
   `xtag*` / `xtagMastery*` tags; the select pane is the **xpack** `masterypane.dbr` with **9** buttons
   and `xtagMasteryDescription09` for slot 9. Same grid + same laws.
5. **File-number is not position.** `skillNN.dbr` numbering is arbitrary; a skill's row/column come only
   from its `bitmapPositionX/Y`. Never infer tier or column from the slot filename.
6. **Grid capacity.** 6 columns x 6 rows = 36 cells; a mastery uses up to 20 skill buttons, so columns
   are sparsely filled and gaps within a column are normal (a modifier chain may skip rows).

---

## 5. Reproduce

```
# base-game arz load + all sweeps (no game, no heavy build):
py <probe>.py     # probes in scratchpad: enumerate, rowmap, connector, dependancy,
                  # grid_select, final  (each prints the numbers cited above)
# key one-liners the gates will encode:
#   TIER:      implied_tier({403:1,341:2,279:3,217:4,155:5,93:6}[Y]) == skill.skillTier   (0/142 fail)
#   GRID:      X in {128,228,328,428,528,628} and Y in {403,341,279,217,155,93}           (mastery btn excepted)
#   CONNECTOR: for modifier `<base>_<suffix>`: button.X == base.X and modifier.tier > base.tier  (75/75)
#   SELECT:    masterypane.masteryMasteryText[N].textTag == tagMasteryBrief0{N};
#              masterypane.masteryMasterySelectedDescriptionTags[N] == tagMasteryDescription0{N}
```

**Confidence:** TIER LAW and CONNECTOR-column placement and SELECT-screen wiring are **empirically
proven** (0-exception sweeps over all 9 masteries, cited counts). The connector-lines-are-baked-art
conclusion is **strongly inferred** by exhaustive elimination (no record field, no connector/arrow
texture, `skillDependancy` disproven, single full-pane background) but not DDS-rendered here; the
operational invariant (2c) is identical under either reading, so no gate depends on that last step.
