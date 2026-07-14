# b40 Occult tree relayout - INDEPENDENT ADVERSARIAL VET

**Verdict: GO.** Branch `feat/b40-occult-tree` @ `7e84de7`. Verified against `baseline_build38.arz`
(== live build38a arz `6631f252`) by independent replay in the worktree (no heavy build).

## The 4 required checks

1. **RCA captures Will's col3 crossing (2&4 vs 1-3-5): CONFIRMED.** My own baseline probe +
   connector-overlap detector found the single same-column crossing in mastery 5 is exactly
   col3 (X=328): `darklings`(pos2, y279) -> `darkaperture`(pos4, y155) interleaved with
   `openwound`(pos3, y217) -> `anatomy`(pos5, y93), plus standalone `bladehoning`(pos1, y341).
   The darklings span [155..279] and anatomy span [93..217] overlap -> the two arrows cross.
   That is Will's "2&4 vs 1-3-5" verbatim. Mechanism proven: connectors are the skill records'
   `skillConnectionOn` (straight `SkillBar{Bottom,Middle,Top}On01` on bases, `_right` on side
   modifiers), spacing 62 = one row; a chain reads clean when no unrelated skill sits in a
   parent->child vertical span.

2. **AFTER fix: no shared cell, none off-panel, arrows read cleanly: CONFIRMED.** Driving the real
   module: 0 cell collisions, 0 off-panel (every X in {128,328,428}, every Y in the 7-row set),
   exactly 8 buttons moved. AFTER overlap detector = NONE; no parent->child span contains an
   unrelated skill in any column. col3 becomes two separated blocks (darklings@403+darkaperture@341
   at the bottom, empty divider 279, openwound@217+anatomy@93) - crossing resolved, no new crossing
   introduced in col1/col3/col4. multishot reunited into col4 @ (428,403) below its laytrap column
   through an empty divider row (341); no col4 collision.

3. **ONLY UI position fields changed: CONFIRMED.** Independent raw field-diff (baseline -> HO.apply):
   9 fields changed, ALL `bitmapPositionX/Y` on the 8 slots, 0 non-position, and 0 `records\skills\`
   fields touched (no skill level/effect/dependency/connector/shape change). Read-back from the
   dry-run arz: all 8 slots INT dtype (DATA_TYPE_INT=0) with exact target values (no INT/FLOAT
   corruption). Golden freeze guard: 44 drifts / 44 waived / **0 HARD** ; the 9 new waiver keys are
   byte-exact and all present in `owner_approved_overrides`.

4. **Composes with mastery_ui_audit: CONFIRMED.** MUI's only `bitmapPosition` writes are `_UI % (3, ...)`
   = mastery 3 (Earth) exclusively; it never writes mastery 5. Replaying BOTH in registry order gives
   a coherent state with disjoint record sets (no write-fight). py_compile PASS; `_check_registry`
   PASS (11 modules).

## Non-blocking notes (none affect the GO)

- **Doc-accuracy (LOW):** RCA + code comments frame col1 as a "Flash Powder chain
  flashpowder->poisongasbomb->shrapnel". Real dep graph: `flashpowder` is standalone (no dep, no
  connector), `poisongasbomb` is a standalone base whose only child is `shrapnel`. The col1 rework is
  still sound - it fixes real defects (scrap's orphan straight-connector that pointed at the unrelated
  poisongasbomb; multishot orphaned from its col4 parent) and introduces no crossing - but the
  "3-node chain" rationale is imprecise. col1 was not Will's flagged column; the change is a safe
  proactive cleanup.
- **INFO:** `_right` connector stubs on `darkaperture`/`rapidconstruction` still point up-right toward
  an adjacent (empty) column. Pre-existing, disclosed in the RCA, and consistent with the
  Will-accepted clean col5 (which also carries a `_right` on lethalstrike). Not a tree-crossing;
  correctly left untouched by a position-only pass.
- **INFO:** scrap's orphan up-connector now renders into the panel header (top row) instead of falsely
  at poisongasbomb - neutral-to-better; cannot be removed position-only.
- **INFO:** an in-game screenshot by Will is the standard final confirmation for a UI layout change
  (the grid math is fully proven here), matching how b38 mastery_ui_audit shipped.
