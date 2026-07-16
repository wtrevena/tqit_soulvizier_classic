# Mastery Skill-Tree CONNECTION MAPS (texture-decoded ground truth)

**Author:** TEXTURE DECODER, 2026-07-14. Branch `feat/mastery-ui-vet`.
**Subject arz:** build40 golden `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
(md5 `b33c5a44...`, 51,029 records) - the arz the next integration build ships against.
**Law source:** base-game `database.arz` (74,013 records) + base `InGameUI.arc` +
mod `work/SoulvizierClassic/Resources/DRXtextures.arc` (all read-only).
**Method:** pure-Python `.tex` decode (`tools/tex_decode.py`) + arz replay
(`tools/build_connection_maps.py`, which reuses `audit_mastery_ui.py`'s exact
family/genuine math - one source of truth with `gate_mastery_ui.py`). No game, no heavy build.
**Deliverables:** this file + machine-readable `tools/mastery_connection_maps.json`.

---

## 0. HEADLINE - the "connector lines are baked into the background art" theory is FALSE

The mandate (and `mastery_ui_invariants.md` §2a) assumed the base<->modifier connector lines
are **pixels painted into each `<Class>SkillBackground01.tex`**, so the reflow had to keep buttons
on the cells the art wires together. **Decoding the actual pixels disproves this.** All 9 effective
pane backgrounds are **uncompressed 32-bit BGRA, 919x540** images that contain **only**:

- **6 horizontal "tier shelf" grooves** at image-y **`{397, 335, 273, 211, 149, 87}`** - a **62 px
  pitch**, each sitting 6 px below a button-anchor row `Y = 465 - 62*tier` (tiers 1-6 -> Y
  `{403,341,279,217,155,93}`). i.e. the art bakes the **tier ladder**, independently confirming the
  TIER LAW's 62 px grid.
- the ornamental frame, the left mastery-bar lane, and the two mastery-art holes (circle + panel).

There are **ZERO vertical skill-to-skill lines in any background.** (Rendered proof is reproducible:
`py tools/tex_decode.py "<game>\Resources\InGameUI.arc" skills/warfareskillbackground01.tex out.png`.)

**So a connection is NOT a fixed property of the background - it is drawn at RUNTIME and FOLLOWS the
buttons.** This confirms `mastery_ui_vet_audit.md` §1's correction and refutes `invariants.md` §2a.
The operational consequence changes how the reflow must be reasoned about (section 4).

---

## 1. What actually draws a connector (decoded mechanism)

A connector is a **runtime bar** drawn from the skill-record field **`skillConnectionOn`** (with
`skillConnectionOff` for the un-owned state and `skillConnectionSpacing` = **62** = one tier pitch).
Two textures are referenced by the golden arz (enumerated from every mastery's skill records):

| variant | field value | arc | decoded size / format | shape |
|---|---|---|---|---|
| straight **[C]** (58 uses) | `InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex` | base `InGameUI.arc` | **15x62**, uncompressed 32-bit BGRA | vertical riser (an "L") along the left, in the **same column** |
| diagonal **[R]** (6 uses) | `DRXtextures\Skill Icons\SkillBarBottomOn01_right.tex` | mod `DRXtextures.arc` | **80x62**, uncompressed 32-bit BGRA | mirror "L": riser on the **right** edge (~80 px right) -> the **column to the right** |

`skillConnectionSpacing = 62` is the **render tile pitch** (the bar art repeats every 62 px), **NOT
the reach.** 58 + 6 = **64** connectors total across the 9 masteries - exactly the edge count below.

### The REACH RULE (proven on the clean base game)

A skill **S** carrying `skillConnectionOn` draws its bar **upward** (toward lower Y / higher tier) to
the **NEAREST OCCUPIED cell above S** - spanning any empty gap - in:

- the **same column** for the straight `[C]` variant, and
- the **column to the right** for the diagonal `[R]` variant.

The pair the player sees connected is `(S, that nearest-occupied-above cell)`. Proof: on the vanilla
base game there are **43** `skillConnectionOn` skills; under this rule **every one** lands on a genuine
augment (0 real spurious - see §3). If the rule were "exactly +1 row," 25 of the 43 would point at an
empty cell, which the clean base game never does.

**=> The connection a player sees is fully computable from the arz** (button X/Y + which skills carry
`skillConnectionOn` + the variant). **No screenshot is required** - which is what settles the
side-connector waivers (section 5).

---

## 2. Effective texture per mastery (which file each pane actually loads)

Read from the golden arz (`skillpanebasebitmap.dbr::bitmapName`). The mod ships **no** `InGameUI.arc`,
so every pane background resolves from the **base game**; only the right-side mastery *panel* art is
DRX-skinned (and is irrelevant to connectors). Occult reuses the Stealth pane; Dream shares Spirit's.

| m | mastery | effective `SkillBackground01` (base `InGameUI.arc`) | note |
|---|---|---|---|
| 1 | Warfare | `InGameUI\Skills\WarfareSkillBackground01.tex` | |
| 2 | Defense | `InGameUI\Skills\DefenseSkillBackground01.tex` | |
| 3 | Earth | `InGameUI\Skills\EarthSkillBackground01.tex` | |
| 4 | Storm | `InGameUI\Skills\StormSkillBackground01.tex` | |
| 5 | Occult | `InGameUI\Skills\StealthSkillBackground01.tex` | select-pane panel art DRX-skinned (`DRXtextures\masterybackdrops\newstealthpanel01.tex`) |
| 6 | Hunting | `InGameUI\Skills\HuntingSkillBackground01.tex` | |
| 7 | Spirit | `InGameUI\Skills\SpiritSkillBackground01.tex` | |
| 8 | Nature | `InGameUI\Skills\NatureSkillBackground01.tex` | |
| 9 | Dream | `InGameUI\Skills\SpiritSkillBackground01.tex` | shares Spirit's pane |

All 8 distinct backgrounds carry the identical 6-shelf/62-px tier ladder and **no** baked connectors.

### The `.tex` format (reverse-engineered, so this is reproducible)

```
[3]  b"TEX"
[1]  version byte (0x01 small icons, 0x02 large panes)
[4]  flags/reserved (0)
[1]  version-2 only: one extra byte
[4]  payload size (LE)
[.]  payload = DDS: 4-byte magic ("DDS"+one byte, not the std 0x20 space)
     + standard 124-byte DDS_HEADER + pixel data
```

The skill-UI textures are all uncompressed 32-bit BGRA (DDPF 0x40, bitcount 32, fourCC 0, masks
blank -> DirectX A8R8G8B8). Proven by exact size math (919*540*4 == payload-128). The DDS start is
located robustly by finding `b"DDS"` followed 4 bytes later by dwSize==124. `tools/tex_decode.py`
decodes any such `.tex` to RGBA (numpy) and can dump a PNG.

---

## 3. Validation (base game = ground truth)

`py tools/build_connection_maps.py --validate` (exit 0 = PASS):

**5+ known-genuine vanilla pairs - each MUST be a drawn, genuine edge:**

| mastery | base | -> modifier | drawn? | genuine? |
|---|---|---|---|---|
| Warfare | `onslaught` | `onslaught_ignorepain` | yes | yes |
| Warfare | `battlerage` | `battlerage_crushingblow` | yes | yes |
| Warfare | `warwind` | `warwind_lacerate` | yes | yes |
| Warfare | `warhorn` | `warhorn_doomhorn` | yes | yes |
| Warfare | `battlestandard` | `battlestandard_petmodifier_triumph` | yes | yes |
| Warfare | `dualweapontraining` | `dualwieldtechnique_jumpslash` | yes | yes (via `skillDependancy`) |
| Hunting | `marksmanship` | `marksmanship_punctureshotarrows` | yes | yes |
| Hunting | `takedown` | `takedown_eviscerate` | yes | yes |
| Hunting | `monsterlure` | `monsterlure_petmodifier_detonate` | yes | yes |

**Negative control - MUST NOT be a connected pair:** Warfare col 1 `weapontraining` <-> `dualweapontraining`
-> **not connected** (PASS). `weapontraining` carries no connector; `dualweapontraining`'s bar draws
*up* into its own Dual-Wield chain, never *down* to `weapontraining`. Adjacency != connection.

**Base-game global cleanliness:** 43 connectors, **0 real spurious.** (The tool flags 1 -
`stoneformbuffself -> stoneform_moltenrock` - but that is a genuine Stone Form connection; it is a
naming-alias false-positive in the shared `genuine()` heuristic, not a defect. Same FP appears in the
gold audit; see §6.)

---

## 4. The authoritative CONNECTION MAP (golden arz)

Full machine-readable data: **`tools/mastery_connection_maps.json`** (per mastery: occupied cells,
every connector edge with `src_cell`/`tgt_cell` in `[col, row]`, variant, and genuine flag). Summary:

| m | mastery | connectors | genuine | spurious | void |
|---|---|---:|---:|---:|---:|
| 1 | Warfare | 7 | 4 | 2 | 1 |
| 2 | Defense | 7 | 3 | 3 | 1 |
| 3 | Earth | 7 | 6 | 1\* | 0 |
| 4 | Storm | 8 | 6 | 2 | 0 |
| 5 | Occult **[GOLDEN]** | 11 | 5 | 6 | 0 |
| 6 | Hunting **[GOLDEN]** | 4 | 3 | 1 | 0 |
| 7 | Spirit | 7 | 1 | 5 | 1 |
| 8 | Nature | 5 | 4 | 1 | 0 |
| 9 | Dream | 8 | 8 | 0 | 0 |
| | **total** | **64** | **40** | **21** | **3** |

`\*` Earth's 1 "spurious" is the `stoneformbuffself->stoneform_moltenrock` naming-alias FP (genuine).
So the actionable defect set is **20 spurious + 3 void = 23 wrong-arrows**, which matches
`mastery_ui_vet_audit.md` §3's independently-derived count of 23 exactly.

### The reflow-designer RULE (this replaces screenshots)

Because connectors follow the buttons, a layout is **correct** iff:

1. **Every skill S with `skillConnectionOn` has its nearest-occupied-above (in the connector's
   direction: straight = same column, `_right` = column to the right) be a GENUINE augment of S**
   (same `<base>_<suffix>` / summon-pet family, or a `skillDependancy` pair), and
2. **every intended base->modifier family is realized** - the base carries the connector and its
   modifier chain occupies the cells directly above with **no foreign skill trapped between** the base
   and its top modifier in that column.

Equivalently, the **legal cell** for a genuine modifier is the **next occupied cell up** from its base
(same column for a straight connector, up-and-right for a `_right` connector). Put a non-augmenting
skill on that cell, or strand the real modifier behind a foreign skill, and you get a wrong arrow.

### The 24 non-genuine edges (the exact wrong-arrows to clear)

Straight `[C]` unless marked `[R]`; `void` = the bar draws into empty space / off-grid.

**Warfare (m1):** `drx_clubslam`(c3,t7) -> **void** (nothing above tier 7); `drxbattlestandard`(c3,t3)
-> `drx_clubslam_fissure`(c3,t4); `drxonslaught_hamstring`(c6,t4) -> `drxwarhorn_doomhorn`(c6,t6).
**Defense (m2):** `[R]`​`drxaxepassive`(c1,t2) -> `drxquickrecovery`(c2,t3); `drxconcussiveblow`(c1,t1)
-> `drxaxepassive`(c1,t2); `drxadrenaline`(c2,t2) -> `drxquickrecovery`(c2,t3);
`[R]`​`drxweaponpool_shieldsmash`(c6,t3) -> **void** (col 6 is rightmost; `_right` points off-grid).
**Earth (m3):** `drxstoneformbuffself`(c2,t4) -> `drxstoneform_moltenrock`(c2,t6) - *FP, genuine*.
**Storm (m4):** `drxspellbreaker`(c4,t3) -> `drxfrostnova`(c4,t5); `drxcoldaura`(c6,t1) ->
`drxstormnimbus_heartoffrost`(c6,t2).
**Occult (m5) [GOLDEN]:** `drx_scrap`(c1,t4) -> `drxpoisongasbomb`(c1,t5);
`[R]`​`drxdarklings_darkaperture`(c3,t5) -> `drx_summon_shadow_stalker`(c4,t6); `drxdarklings`(c3,t3)
-> `drxopenwound`(c3,t4) *(Will's reported crossed tree)*; `drx_summon_shadow_stalker`(c4,t6) ->
`drx_petmodifier_greaterpower`(c4,t7); `[R]`​`drxlaytrap_rapidconstruction`(c4,t5) ->
`drxlethalstrike_mortalwound`(c5,t7); `[R]`​`drxlethalstrike`(c5,t5) ->
`drxthrowingknife_flurryofknives`(c6,t6).
**Hunting (m6) [GOLDEN]:** `drxtakedown_eviscerate`(c4,t2) -> `drxspear_tempest`(c4,t3).
**Spirit (m7):** `drxternion`(c1,t2) -> `drxsandsofsleep_troubleddreams`(c1,t3);
`drxsandsofsleep`(c1,t1) -> `drxternion`(c1,t2); `drxdistortionwave`(c3,t1) -> `drxspiritward`(c3,t2);
`[R]`​`drxwraithlordsummons`(c5,t5) -> **void** (nothing in col 6 above); `drxskellysummons`(c5,t1) ->
`drxlifedrain`(c5,t3); `drxenslavespirit`(c6,t1) -> `drxlifedrain_cascade`(c6,t3).
**Nature (m8):** `drxsprite_summons`(c5,t1) -> `drxrenewal`(c5,t3).
**Dream (m9):** none - all 8 connectors genuine.

---

## 5. The `_right` [R] side-connector waivers - SETTLED (no screenshot)

The golden arz has **exactly 6** `_right` connectors (ground truth: 6 `SkillBarBottomOn01_right.tex`
references). The decoded geometry (riser on the right edge => column to the right) + button positions
resolve all 6 definitively:

| mastery | skill (cell) | `[R]` bar lands on | verdict |
|---|---|---|---|
| Defense | `drxaxepassive` (c1,t2) | `drxquickrecovery` (c2,t3) | **spurious** (unrelated) |
| Defense | `drxweaponpool_shieldsmash` (c6,t3) | nothing (col 7 off-grid) | **void** - points off the grid |
| Occult | `drxdarklings_darkaperture` (c3,t5) | `drx_summon_shadow_stalker` (c4,t6) | **spurious** |
| Occult | `drxlaytrap_rapidconstruction` (c4,t5) | `drxlethalstrike_mortalwound` (c5,t7) | **spurious** |
| Occult | `drxlethalstrike` (c5,t5) | `drxthrowingknife_flurryofknives` (c6,t6) | **spurious** |
| Spirit | `drxwraithlordsummons` (c5,t5) | nothing in col 6 above | **void** |

**None of the 6 lands on a genuine augment** (4 hit an unrelated skill, 2 draw off-grid/into space).
The vet audit's "9 side [R]" was an over-count that conflated `_right` connectors with `[R]`-adjacent
OFF-COLUMN findings; the decode fixes the number at **6** and resolves each. The fix for a `_right`
connector is either (a) place the base's genuine diagonal augment on the up-and-right cell, or
(b) drop the `_right` connector (repoint `skillConnectionOn` to the straight/`off` variant) - a
`skillConnectionOn` edit, not necessarily a move.

---

## 6. Reconciliation with the two prior docs

- **`mastery_ui_invariants.md` §2a ("lines baked into the 919x540 background") - REFUTED** by the pixel
  decode. The background bakes the tier *shelves* (6 rows, 62 px), not connectors. Everything else in
  that doc (TIER ladder, column-stack placement, select-screen wiring) stands; only the connector
  *mechanism* sentence is wrong. (§2b was already right that `skillDependancy` is not the visual link.)
- **`mastery_ui_vet_audit.md` §1 ("connector is the `skillConnectionOn` field") - CONFIRMED** by the
  decode, and its 23-spurious count reproduced exactly by an independent method. Refinements this decode
  adds: (i) the reach is *nearest-occupied-above*, not +1 row; (ii) 3 of the 23 are **void** (bar into
  empty space / off-grid), not merely mis-targeted; (iii) there are exactly **6** `_right` connectors
  (not 9), all now resolved; (iv) the `stoneformbuffself->stoneform_moltenrock` flag is a shared
  `genuine()` naming-alias **false-positive** (Stone Form is one family) - it is not a real wrong-arrow
  and should be excluded from the fix list (a candidate `genuine()` refinement for a later round).

---

## 7. Reproduce

```
# decode any TQ .tex to a PNG (or just print its dims/format):
py tools/tex_decode.py "<game>\Resources\InGameUI.arc" skills/warfareskillbackground01.tex bg.png
py tools/tex_decode.py work/SoulvizierClassic/Resources/DRXtextures.arc "skill icons/skillbarbottomon01_right.tex" r.png

# emit the machine-readable connection map (tools/mastery_connection_maps.json):
py tools/build_connection_maps.py

# validate the mechanism on the vanilla base game (genuine pairs + negative control):
py tools/build_connection_maps.py --validate      # exit 0 = PASS
```

**Confidence.** The `.tex` decode (format, dims, no-baked-connectors), the connector-texture geometry
(straight same-column / `_right` column-right), and the reach rule are **empirically proven** (exact
size math, pixel inspection, 0-real-spurious base-game validation with the named genuine pairs +
negative control). The golden connection map is a mechanical read of the arz and reproduces the gold
audit's 23 wrong-arrows. The single not-run-in-engine step is watching the bar render across a gap;
the base-game 43/43-genuine result makes the nearest-occupied-above reach rule high-confidence.
