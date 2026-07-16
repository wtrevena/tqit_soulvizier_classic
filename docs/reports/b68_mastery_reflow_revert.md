# b68 MASTERY REFLOW REVERT (2026-07-16)

Will played build43 and reported the build42 mastery reflow introduced huge skill-tree errors
(skills moved to wrong rows/columns, wrong connections, circle/square frame flips). His directive
(verbatim intent): revert the reflow. This wave surgically reverts the reflow while keeping the two
Will-mandated waves that shipped on top of it (b60 pane-render fix, b67 pane-art fix) and every
other unrelated build42/43 content change (drop rates, souls quality, legion stages, thrown
restore, aura-radius widening, uber orphan weapons, turtleshell relics, SVAERA sets, double-soul
rulings).

## What shipped the reflow (reverted)

Merge commit `395ccf9` ("Merge branch 'feat/mastery-ui-vet' into integration/build42") introduced:
- `tools/patches/mastery_ui_vet.py` - reflows the 6 non-golden masteries (Warfare/Defense/Storm/
  Spirit/Nature/Dream). **DELETED.**
- ~127-line rewrite of `tools/patches/hunting_occult_ui.py` - reflowed Will's hand-tuned golden
  Occult+Hunting trees (the worst damage). **REVERTED to the build41 version** (`git checkout
  build41 -- tools/patches/hunting_occult_ui.py`; verified nothing else touched this file between
  build41 and HEAD).
- ~20-line change to `tools/occult_hunting_golden.json` sanctioning the reflow's own moves.
  **REVERTED the BODY to build41** (`git checkout build41 -- tools/occult_hunting_golden.json`),
  then **gate-driven reconstruction** of `owner_approved_overrides` (see below) to re-admit the two
  Will-mandated waves that landed after build41 and before the reflow merge.
- `tools/gate_mastery_ui.py` + `tools/mastery_ui_waivers.json` + a gate-wiring block in
  `tools/build_svc_database.py` (~24 lines, the "Mastery/skill-tree UI law gate", between the A7
  golden-freeze gate and the F2 contract gate). **DELETED / REMOVED.** The `mastery_ui_vet` entry
  (+ its comment block) was removed from the `REGISTRY` list in `tools/patches/__init__.py`.
- Inert analysis scripts (`audit_mastery_ui.py`, `build_connection_maps.py`,
  `derive_mastery_ui_invariants.py`, `mastery_conn_model.py`, `mastery_connection_maps.json`,
  `tex_decode.py`) + docs/reports. **KEPT** (harmless, reused by later/kept waves - `oh_pane_art.py`
  and `mastery_bg_render.py` both cite this decode work).

Zero remaining live-code references to `gate_mastery_ui` / `mastery_ui_vet` / `mastery_ui_waivers`
(grepped `*.py` repo-wide; only comment mentions in kept analysis scripts, which is fine).
`tools/patches/_check_registry.py` passes: 25 modules, order hash `d057be188237...`.

## What was explicitly kept (Will wants these)

- `tools/patches/mastery_bg_render.py` + `tools/gate_mastery_bg_render.py` (b60, commit `a04532f`
  in this repo's history / `6a14525` sanctioned its golden overrides) - fixed the literal BLACK pane
  RENDER bug (`BitmapSingle` -> vanilla `BitmapUIAware` + controller sibling) for all 9 masteries.
- `tools/patches/oh_pane_art.py` (b67, commit `5a1ed63`) - repoints Occult's tree-pane background
  texture from the vanilla tan Stealth backdrop to the bespoke DRX dark tablet.

Both still run in the registry (`mastery_bg_render`, `oh_pane_art`), both still have their own
fail-loud `verify()` hooks, and both passed on this build (`verify hooks OK: ... mastery_bg_render,
oh_pane_art, ...`).

## Gate-driven override reconstruction

Rebuilding immediately after the two file reverts, the A7 golden-freeze gate FAILED exactly as
planned, listing 31 unapproved drifts (`RESULT: FAIL - 31 unapproved drift(s)`). Cross-checked
against `git show` of the two sanctioning commits:

- **28 keys** = the b60 bg-render fields (`FileDescription`, `bitmapNames`, `bitmapPositionX/Y`,
  `bitmapPositionsX/Y`, `templateName` x 2 records [`skillpanebasebitmap.dbr` /
  `skillpanereallocationbitmap.dbr`] x 2 masteries [Occult=5, Hunting=6] = 28), extracted verbatim
  from commit `6a14525`. One of the 28 (`mastery 5 skillpanebasebitmap.dbr::bitmapNames`) carries an
  EXTENDED justification (verbatim from `5a1ed63`) documenting the b67 follow-up drift on the same
  field - b67 does not touch any field outside this 28-key set (confirmed by reading
  `tools/patches/oh_pane_art.py` directly: it only ever writes `bitmapNames` on
  `mastery 5\skillpanebasebitmap.dbr`).
- **3 keys were NOT in either sanctioning commit** - a genuine gap in the revert plan, not reflow
  residue: `drxartofthehuntbuff.dbr::skillTargetRadius`, `drxcallofthehuntbuff.dbr::
  skillTargetRadius`, `drxbladehoningbuff.dbr::skillTargetRadius`. These are the 3 Occult/Hunting
  golden-tracked auras widened by the separate, unrelated **BL-AURA-RADIUS** wave (b57, commit
  `c567d9e`, "widen 80 friendly-aura radii to 36u"), which landed AFTER build41 but BEFORE the
  reflow merge and added its own 3-key sanction to `owner_approved_overrides` at the time. Blanket-
  reverting the whole golden.json file to build41 collaterally deleted that unrelated, still-active
  feature's sanction (aura_radius is untouched by this revert and still runs in the registry).
  Restored verbatim from `c567d9e`.

All 31 keys were re-added to `owner_approved_overrides` (JSON-diffed against a byte-identical
round-trip re-serialization of the untouched parts of the file to confirm the edit touched ONLY
this section - `git diff --stat` confirms exactly 31 insertions, 0 deletions, 0 elsewhere). No
drifted key was found outside these two known-good sets - there was no reflow residue left to
waive or fix.

Rebuilt: **A7 PASS** (`RESULT: PASS - Occult/Hunting golden state intact`, 66 waived DB-only / 72
waived once Text.arc's 6 tag-level overrides are included, 0 other both times).

## Build artifacts (scratch, `.claude/worktrees/mastery-revert/local/revert_build/`)

- `Database/SoulvizierClassic.arz` - md5 **`439a9279a7c5cf94b02074fd00981dd2`**, 55,382,418 bytes,
  51,058 records. `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, 5-arg build form.
- `Resources/Text.arc` - md5 **`3e576581ec65552ca1171bab889a0b62`**, 88,268 bytes - **byte-identical**
  to the current build43 `work/SoulvizierClassic/Resources/Text.arc` (same md5). Expected: the merge
  touched no text files. `validate_tags`-equivalent duplicate-tag gate + the A7 tag-drift check both
  PASS.
- SUMMON PET VALIDATOR (B-SUMMON-1): STRICT failures 0 (134 pre-existing upstream-proven warnings,
  unchanged class from every prior build).
- `_check_registry.py`: 25 modules OK.
- Contracts suite (`souls,summons,resources`): **GATE PASS**, 0 P0/0 P1, 4903 P2 (pre-existing
  tracked minor gaps - same class documented in the 155-item MINOR-GAP list and prior build gate
  records; nothing new).

## Proof diff (a): new arz vs build43 (main repo `work/.../SoulvizierClassic.arz`, md5 `e6ec1459`)

`tools/record_diff.py --fields`: **56 modified, 0 added, 0 removed.** Every single modified record
is `records\ingameui\player skills\...` and every single modified field is `bitmapPositionX`,
`bitmapPositionY`, `skillConnectionOn`, or `skillConnectionOff` - i.e. exactly button
position/connector fields reverting to build41 layout across masteries 1/2/4/5/7/8/9 (the 6 non-
golden reflowed masteries + the golden Occult button `skill18` connector + assorted non-mastery
skill records whose connector arrays the reflow's connector-rebuild touched in passing). **Zero
non-UI deltas.**

## Proof diff (b): new arz vs build41 baseline (`local/baseline_build41.arz`, md5 `eb8bc377`)

`tools/record_diff.py`: 41 added / 6 removed / 509 modified.

- **`ingameui\player skills\...` records: 20 modified + 1 added.** Every one of the 21 is fully
  accounted for by the two KEPT waves: the 18 `skillpanebasebitmap.dbr` / `
  skillpanereallocationbitmap.dbr` pane-structure records (b60's `BitmapSingle`->`BitmapUIAware`
  conversion, `bitmapName`->`bitmapNames`, position->positions, templateName; Occult's base pane
  additionally carries b67's DRX-tablet texture repoint), the 2 `mastery base` chrome records (undo
  buttons / cost-per-point / current-gold bitmaps, also b60), and the 1 ADDED record (`records\
  ingameui\player skills\select mastery\masterypane.dbr`) is b67's separate
  `import_occult_select_mastery_art()` call (confirmed by `git log` - the function was added in the
  same `5a1ed63` commit) repointing the select-mastery-screen Occult preview art on all 4 DLC tiers;
  the base `ingameui` copy is one of those 4. **Zero position/connector deltas** on any `ingameui`
  record beyond these two kept waves.
- **41 added / 6 removed / remaining ~489 modified** are the documented build42-59 content wave:
  389 `creature\monster\...` records (the drop-rate 66->50 last-writer change), the 3 aura-radius
  keys discussed above (+2 more non-golden-tracked stealth pet buffs also widened by the same b57
  wave), legion soul-stage fixes, enslaver-pet-fx, thrown-wielder restores, souls-quality tier
  fixes, uber-orphan-weapon supra formulas (the 41 ADDED `drxitem\supra\...` + `zrecipes\...`
  records), the Toxeus Legendary-stalker pool, turtleshell relics (Reveler's Ruse), the 5 re-linked
  SVAERA sets, and the double-soul-rulings retire (the 6 REMOVED `svc_uber\{lilluedchild,
  possessedboar}_soul_{e,l,n}.dbr` records). No surprise record was found in either diff; nothing
  needed resolving beyond the 3-key aura_radius override gap already covered above.

## PERSISTING DEFECTS (predate build42; this revert does NOT touch them)

Two items from Will's build43 complaint plausibly overlap with pre-existing, INTENTIONAL behavior
that already shipped in build41 (build37-era, commit `db9bc6f` "apply Will's SHAPE LAW to H/O
buttons + revert 3 passives to CIRCLE") and is unchanged by this revert:

- **Poisonous Gas (Occult, `drxpoisongasbomb`, UI `mastery 5\skill13`)** is drawn as a **SQUARE**
  (cast active, per Will's 2026-07-12 SHAPE LAW: "circles [are] a passive... a square is an
  activate"). This is Will's own explicit, standing rule, not reflow damage - build41 already drew
  it this way and the restored `hunting_occult_ui.py` still does.
- **Blade Fury (Occult, `drxcalculatedstrike_luckyhit`, UI `mastery 5\skill06`, tag
  `tagDRXcalculatedstrike_luckyhitNAME`)** is drawn as a **CIRCLE** (a modifier of Calculated
  Strike, per the same law). Also build41-original, also unchanged by this revert.

If Will's "circle/square frame flips" complaint on build43 includes either of these two skills
specifically, that is NOT something build42's reflow introduced and NOT something this revert
fixes or can fix - it is Will's own 2026-07-12 shape-law ruling, already baked into the build41
state this revert restores. Any OTHER circle/square flip Will saw (on any of the other 7
masteries, or on connector routing rather than shape) WAS reflow-introduced and IS fixed by this
revert (see proof diff (a) - every reflow-introduced position/connector delta reverts cleanly to
build41 values, 0 residue).

No other pre-build42 defect was identified in scope for this wave; a full independent skill-tree
audit was out of scope (this wave is a revert, not a fresh audit).

## Files touched

- `tools/patches/hunting_occult_ui.py` - reverted to build41.
- `tools/occult_hunting_golden.json` - body reverted to build41 + 31 overrides gate-reconstructed
  (28 b60/b67 + 3 aura_radius).
- `tools/patches/mastery_ui_vet.py`, `tools/gate_mastery_ui.py`, `tools/mastery_ui_waivers.json` -
  deleted.
- `tools/patches/__init__.py` - removed the `mastery_ui_vet` REGISTRY entry + comment.
- `tools/build_svc_database.py` - removed the "Mastery/skill-tree UI law gate" wiring block (import
  + validate call + SystemExit + explanatory comment); the A7 golden-freeze gate above it and the F2
  contract gate below it are untouched.
