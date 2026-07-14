# b40 - Occult Mastery Tree Relayout (RCA + fix)

**Wave:** b40-occult-tree | **Branch:** feat/b40-occult-tree | **Date:** 2026-07-13
**Owner report (Will, 2026-07-13, Occult Mastery screenshot):** the connector ARROWS still read
wrong in some Occult skills, "likely because there is not enough horizontal space." Specifically in
the THIRD column the bottom/middle/top skills read as one tree while the 2nd and 4th read as a
separate tree, so the dependency lines cross and confuse. He suggested MOVING those skills to another
column on the right (spread them out) so the arrows read correctly. (The b38 mastery_ui_audit fixed
Earth's column; Occult still had this crossed-tree problem.)

Ground truth: `baseline_build38.arz` (== build38a arz `6631f252`, LIVE on Steam / deployed to
`SoulvizierClassicDEV`). All evidence below is read out of that arz. No skill VALUE/effect/dependency
semantics were changed - the fix moves UI button grid slots only.

---

## 1. How the panel + connectors actually work (proven from the arz)

**The skill panel is a FIXED grid, identical on all 8 base masteries** (probed every
`records\ingameui\player skills\mastery N\skillNN.dbr`):

- Columns (bitmapPositionX): **128, 228, 328, 428, 528, 628** (6 columns). NO base mastery uses
  X > 628. There is **no 7th column** - the per-class background art (`baseskillpane.dbr` +
  `<Class>SkillBackground01.tex`) is sized for exactly 6 columns, so a literal "column on the right"
  at X=728 would sit off-panel/on the border. The fix therefore de-interleaves **within** the 6x7
  grid and uses the empty cells to space chains out (Will's intent, achieved without an off-panel
  node).
- Rows (bitmapPositionY): **31, 93, 155, 217, 279, 341, 403** (7 rows). **Higher Y = lower on
  screen**, so a chain's base skill sits at the bottom (Y=403) and its upgrades stack upward (toward
  Y=31). This matches the Earth reflow convention in `mastery_ui_audit` ("base lower/high-y,
  modifiers stack up").

**Connector reading.** A column reads as a clean tree when each dependency chain occupies a
CONTIGUOUS vertical run (no unrelated skill between a parent and its child) and independent chains
are separated by at least one EMPTY row. The proof-by-example is Will's own **column 6 (X=628)**,
which he did NOT flag: `disarmtraps (403) + dual_blade (341)` [base+child pair], empty row 279,
`throwingknife (217) + flurry (93)` [base+child pair]. Two clean pairs, one empty divider. That is
the template the fix reuses.

`skillConnectionOn` bitmaps corroborate but do not by themselves fix the read: bases/mid-chain nodes
carry `SkillBarBottomOn01.tex` (straight); side-branch modifiers carry
`skillbarbottomon01_right.tex` (`_right`, e.g. darkaperture, rapidconstruction, lethalstrike); leaf
modifiers/standalones carry none. These are on the skill records and are golden-tracked design; this
wave does NOT touch them (position-only mandate). The `_right` stubs are left as-is (a minor cosmetic
detail), because the readability defect Will reported is entirely about which skills group together
vertically, and that is 100% controlled by the grid slot.

---

## 2. The dependency forest (26 Occult skills, 10 root chains)

| Chain | Members (base -> upgrades) | Current column |
|---|---|---|
| A Envenom Weapon | envenomweapon -> neurotoxin -> delirium -> toxindistillation | X=228 (clean) |
| B Calculated Strike | calculatedstrike -> luckyhit -> lethalstrike -> mortalwound | X=528 (clean) |
| C Open Wound | openwound -> anatomy | X=328 (interleaved) |
| D Throwing Knife | throwingknife -> flurryofknives | X=628 (clean, top pair) |
| E Flash Powder | flashpowder -> poisongasbomb -> shrapnel | X=128 (interleaved) |
| F Disarm Traps | disarmtraps -> dual_blade | X=628 (clean, bottom pair) |
| G Lay Trap | laytrap -> rapidconstruction -> summon_shadow_stalker -> greaterpower; **+ multishotbolttrap (pet-branch)** | X=428 (+ orphan in X=128) |
| H Scrap | drx_scrap (standalone AttackProjectile) | X=128 (crammed) |
| I Blade Honing | drxbladehoning (standalone toggle buff) | X=328 (crammed) |
| J Darklings | darklings -> darkaperture | X=328 (interleaved) |

Dependencies proven via `skillDependancy` fields + name-prefix modifiers (e.g.
`anatomy.skillDependancy = openwound`, `darkaperture` modifies `darklings`,
`shrapnel.skillDependancy = poisongasbomb`, `dual_blade.skillDependancy = disarmtraps`,
`summon_shadow_stalker.skillDependancy = rapidconstruction`).

---

## 3. The crossed-tree defects

### Column 3 (X=328) - Will's explicit report
Occupied bottom->top: `bladehoning (341)`, `darklings (279)`, `openwound (217)`, `darkaperture
(155)`, `anatomy (93)`. Two independent 2-node chains are **interleaved at alternating rows**:
- Darklings (J): darklings (pos 2) -> darkaperture (pos 4) -- "the 2nd and 4th connected to each
  other."
- Open Wound (C): openwound (pos 3) -> anatomy (pos 5); plus standalone Blade Honing (pos 1) -- the
  "bottom, middle, top" (positions 1-3-5) Will perceives as the other tree.

The darklings connector (2->4) and the openwound connector (3->5) span overlapping row ranges, so
they **cross** and the column is unreadable. Exactly Will's description.

### Column 1 (X=128) - the same defect (also fixed)
Occupied bottom->top: `flashpowder (341)`, `multishotbolttrap (279)`, `scrap (217)`, `poisongasbomb
(155)`, `shrapnel (31)`. The Flash Powder chain (flashpowder -> poisongasbomb -> shrapnel) is
interleaved with standalone **Scrap** and with an **orphaned Lay Trap pet-branch**
(multishotbolttrap) whose parent Lay Trap lives in column 4. Scrap even carries a straight
up-connector that currently points at the unrelated poisongasbomb.

Columns 2 (Envenom), 5 (Calculated Strike), 6 (Disarm/Throwing Knife) already read clean and are left
untouched.

---

## 4. The fix (8 buttons moved; positions only)

De-interleave into contiguous, non-crossing runs mirroring the clean col6 pattern, and reunite the
orphan. Implemented in `tools/patches/hunting_occult_ui.py` (the module that already owns Occult UI
and explicitly deferred this alignment follow-up) as `_OCCULT_REFLOW`, applied after the shape fixes;
each slot is asserted to still hold its expected skill (fail-loud on upstream drift) before its
`bitmapPositionX/Y` is set (dtype 0 = INT, matching the Earth reflow).

| slot | skill | old (x,y) | new (x,y) | role |
|---|---|---|---|---|
| skill12 | drxflashpowder | 128,341 | **128,403** | Flash Powder base -> bottom |
| skill13 | drxpoisongasbomb | 128,155 | **128,279** | chain node |
| skill14 | drxpoisongasbomb_shrapnel | 128,31 | **128,155** | chain leaf |
| skill21 | drx_scrap | 128,217 | **128,31** | standalone, isolated at top |
| skill18 | drxlaytrap_petmodifier_multishotbolttrap | 128,279 | **428,403** | reunited into Lay Trap col (X change) |
| skill25 | drxdarklings | 328,279 | **328,403** | Darklings base -> bottom |
| skill26 | drxdarklings_darkaperture | 328,155 | **328,341** | branch, adjacent to base |
| skill09 | drxbladehoning | 328,341 | **328,31** | standalone, isolated at top |

`openwound (skill07 @328,217)` and `anatomy (skill08 @328,93)` keep their exact cells (unmoved -> no
drift). The Lay Trap main chain and all of columns 2/5/6 are byte-identical.

### Resulting grid (verified in-memory + via a written dry-run arz)
```
        X=128         X=228        X=328         X=428          X=528        X=628
Y=31    scrap         -            bladehoning   greaterpower   mortalwound  -
Y=93    -             toxindist    anatomy       summon_stalker -            flurry
Y=155   shrapnel      delirium     -             rapidconstr    lethalstrike -
Y=217   -             -            openwound     -              -            throwingknife
Y=279   poisongas     neurotoxin   -             laytrap        luckyhit     -
Y=341   -             -            darkaperture  -              -            dual_blade
Y=403   flashpowder   envenom      darklings     multishot      calcstrike   disarmtraps
```
- **Col1 (E+H):** Flash Powder chain contiguous (403->279->155), Scrap isolated at top (empty row 93
  below it). No foreign skill between chain members.
- **Col3 (J+C):** two clean base+child pairs like col6 - darklings(403)+darkaperture(341), empty
  divider row 279, openwound(217)+anatomy(93); Blade Honing isolated at top (31). The darklings and
  openwound arrows no longer cross.
- **Col4 (G):** multishotbolttrap reunited at the bottom (403), isolated by the empty row 341 below
  Lay Trap (279); Lay Trap main chain unchanged.

---

## 5. Verification (dry-run, no heavy build)

`scratchpad/replay_occult_tree.py` applies `hunting_occult_ui` **and** `mastery_ui_audit` to a copy of
`baseline_build38.arz`, enumerates the grid, writes a dry-run arz, and runs the REAL golden gate:

- **new records added: 0** (UI position-only).
- **cell collisions: 0** - every skill in a distinct on-panel cell.
- **off-panel nodes: 0** - every X in {128..628}, every Y in {31..403}.
- **buttons moved: 8** - exactly the table above.
- **Composition with `mastery_ui_audit`:** both modules apply cleanly to the same db; the Occult
  position writes are disjoint from the Earth (mastery 3) reflow writes - **no write-fight**.
- **Golden freeze guard (`validate_mastery_golden`): PASS** - "Occult/Hunting golden state intact
  (44 waived, 0 other)". The 9 new drift keys are all `mastery 5 skillNN bitmapPositionX/Y` and were
  added to `owner_approved_overrides` (the harness proved the "non-reflow HARD drift" set is EMPTY:
  Hunting mastery 6 and every Occult skill VALUE are untouched).

### Fast gates
- `py -m py_compile tools/patches/hunting_occult_ui.py` -> OK
- `py tools/patches/_check_registry.py` -> OK (11 modules)
- `json.load(occult_hunting_golden.json)` -> valid, 50 overrides; `git diff` = 9 added lines, 0
  removed (clean, sort-order preserved).

---

## 6. Scope / notes
- **Position fields ONLY** (`bitmapPositionX/Y`). No skill levels, effects, dependencies, shapes,
  icons, connectors, or Text tags changed. Will's F5 Flash Powder rework, H5b Darklings petLimit=4,
  and all hand-tuning remain intact (visible as pre-existing golden waivers, untouched).
- **`_right` connector stubs** on darkaperture/rapidconstruction (they point up-right toward an
  adjacent column) are pre-existing cosmetic decoration and out of scope for a position-only pass;
  the primary crossed-tree read is fixed by the reflow. If Will wants the stubs squared off later,
  that is a `skillConnectionOn` edit + its own golden waiver.
- **In-game confirmation** is the only remaining check - the panel renders exactly one way and cannot
  be screenshotted here (TQ is running Will's live game). The dry-run proves the grid math; Will's
  screenshot pass confirms the pixels.
