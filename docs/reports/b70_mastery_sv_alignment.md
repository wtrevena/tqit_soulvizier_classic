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
| 9 | Dark Invigoration should be connected at the 16 row | `drxopenwound` m5 skill07 (c3t4) | **fixed-here (D)**: added straight bar Shadow Link(c3t2)->Dark Invigoration(c3t4). WILL-INTENT visual wire | WILL directive 2026-07-16 |
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

### D. Dark Invigoration connector (WILL-INTENT wire)
Dark Invigoration (`drxopenwound`, c3t4/y217) stays put (already correct). Added a straight
`[Bottom,Middle,Top]` bar to **Shadow Link (`drxbladehoning`, c3t2/y341)** so its bar draws UP
through the now-vacated c3t3 to Dark Invigoration at c3t4 (the 16-point row). Per the conn model the
LOWER skill owns the bar and draws upward, so the bar lives on Shadow Link.
**GAMEPLAY-RELATION FINDING (flagged):** `drxopenwound` has NO
`skillDependancy`/`buffSkillName`/modifier reference to `drxbladehoning` (its only skill-ref is a
`charFxPakSelfNames` effect). SV098 col3 is bare (no bars in any SV). So this connector is a **purely
VISUAL Will-intent wire** - there is no underlying gameplay augment relation between Dark Invigoration
and Shadow Link. Wired per Will's directive; flagged so Will knows the visual implies a relation the
mechanics do not have.

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

## Verification (all GREEN)
- `py_compile` (module + hunting_occult_ui + __init__) + registry selfcheck (26 modules) + golden JSON valid.
- Dry-run replay (module applied to build44 arz): record-diff = **17 modified records, ALL UI/connector
  fields, ZERO gameplay/stat deltas**; every delta maps to a fix-list item (9 emblems + 4 shapes + 2
  family positions + 2 Dark-Aperture-conn + 2 Shadow-Link-conn = 21 field-groups on 17 records).
- A7 golden freeze gate: **PASS (74 waived, 0 hard)** via the exact build code path.
- `verify()` negative test: flipping Poisonous Gas back to square -> `verify()` FAILS as required.
- Full DB build + in-build gate battery: see BUILD45 gate record in BACKLOG (arz md5 recorded there).
