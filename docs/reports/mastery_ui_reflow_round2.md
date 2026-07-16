# Mastery / Skill-Tree UI REFLOW - round 2 (law-compliant, all 9 masteries)

**Author:** REFLOW IMPLEMENTER (round 1 of the vet loop), 2026-07-14. Branch `feat/mastery-ui-vet`.
**Baseline (dry-run replay subject):** build40 golden `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
(md5 `b33c5a44...`, 51,029 records).
**Laws:** TIER (button row == skillTier) + CONNECTOR (only genuine augments connected: the
`skillConnectionOn` bar draws UP to the NEAREST occupied cell above - same column for the straight
`SkillBarBottomOn01.tex`, column-right for the DRX `_right.tex`). Ground truth:
`mastery_connection_maps.md` + `mastery_ui_vet_audit.md` + `mastery_ui_invariants.md`.

## 0. Headline

The round-1 audit found **66 findings** and the round-1 fixer cleared 8, **waiving 58**. This round
clears the rest: after the reflow the gate reports **18 findings, of which 17 are waived and 1 was a
bug I then fixed -> 0 unwaived**. Every wrong/crossed arrow Will reported (the CONNECTOR LAW - his
actual complaint) is gone: **0 unwaived CONN, INTERLEAVE or OFFCOL across all 9 masteries.** The 17
surviving waivers are each an IRREDUCIBLE tier collision / graft-broken skillTier / missing-record
phantom that has no law-compliant placement on the fixed 6-column x 7-row grid, with a one-sentence
reason in `tools/mastery_ui_waivers.json`.

| dimension | round-1 | round-2 |
|---|---:|---:|
| unwaived CONN (wrong arrows) | many | **0** |
| unwaived INTERLEAVE (crossed trees) | many | **0** |
| unwaived OFFCOL (stranded modifiers) | many | **0** |
| unwaived TIER | 0 (all waived) | **0** |
| **total waivers** | **58** | **17** |

Verification: a dry-run replay of the ACTUAL registry modules onto the build40 golden shows the
record-diff is **UI-only** (every changed field is `bitmapPositionX/Y` or `skillConnectionOn`, on a
mastery-UI or skill record - zero gameplay-value drift), `gate_mastery_ui` **PASS** (17 waived, 0
unwaived, 0 stale), and the A7 Occult/Hunting golden freeze **PASS** (all golden drift covered by
owner_approved_overrides).

## 1. What changed, per mastery (all UI-only: button position + visual connector)

Non-golden masteries are owned by `tools/patches/mastery_ui_vet.py`; golden Occult (5) + Hunting (6)
by `tools/patches/hunting_occult_ui.py` (with `occult_hunting_golden.json` owner_approved_overrides).

- **m1 Warfare** - reunited Onslaught Hamstring into Onslaught's column (r1); de-interleaved col3's
  three grafted families (Club Slam, Battle Standard, Ancestral Mod) into clean non-crossing blocks;
  Battle Standard's bar now reaches its own Triumph pet-modifier (was pointing at Club Slam Fissure);
  Ancestral Mod moved to its tier-7 row (fixes TIER).
- **m2 Defense** - Quick Recovery + Summon Phalanx relocated (r1); dropped 3 spurious base connectors
  (Concussive Blow, Axe Training, Weapon Pool Shield Smash) that had no modifier to draw to.
- **m3 Earth** - NO position change. The b38 contiguous Rupture packing is Will's explicit 2026-07-13
  "start lower" ask; its arrows are already correct. The 5 TIER findings are waived (col4 crams 4
  grafted families with tier collisions and no free column can hold a tier-correct grafted Rupture
  family without displacing the intact Ring of Flame family).
- **m4 Storm** - reunited Storm Nimbus Heart of Frost into col1; moved the two grafted standalones
  (Frost Nova, Lightning Dash) + the phantom Spell Shock 2 out of the Spellbreaker/Storm Nimbus spans
  so Cold Aura reaches its Synergy and Spellbreaker reaches its Spell Shock.
- **m5 Occult [GOLDEN]** - the crossed tree Will reported 2026-07-13, re-derived to the laws: reunited
  the orphaned Lay Trap pet-branch (Multishot Bolt Trap) into Lay Trap's column; moved Open Wound out
  of the Darklings->Darkaperture span so Darklings' bar reaches its own Darkaperture; dropped 3 spurious
  base/leaf connectors; flipped Lethal Strike's mis-pointed `[R]` side-connector to straight (it reaches
  its own Mortal Wound).
- **m6 Hunting [GOLDEN]** - moved Take Down's connector from the Eviscerate modifier onto the Take Down
  base (vanilla pattern), so the arrow reads Take Down->Eviscerate instead of the spurious
  Eviscerate->Tempest.
- **m7 Spirit** - the worst tree, holistic de-interleave: returned Death Chill Aura / Life Drain /
  Wraith Lord / Spirit Ward modifiers to their base columns; split the interleaved Ternion + Sands of
  Sleep families into separate columns; tier-corrected the Distortion Wave chain; flipped Wraith Lord's
  `[R]` connector to straight; dropped 3 spurious summon connectors. 19 findings -> 2 waivers.
- **m8 Nature** - reunited the Sylvan Nymph pet-modifier (Sylvan Protection) into the nymph column;
  dropped Sprite's spurious base connector.
- **m9 Dream** - Distortion Field out of the Lucid Dream span (r1).

## 2. Detector improvement (mandate item 3)

`audit_mastery_ui.canon()` now strips the `buffself` self-cast suffix (like it already strips
`summons`/`summoning`), so `stoneformbuffself` shares a family root with `stoneform_moltenrock`. This
settles the documented Earth Stone-Form CONNECTOR false-positive **in the detector** (the connector is
CORRECT - both are Stone Form) rather than by a position move or a waiver. `stoneformbuffself` is the
ONLY skill ending in `buffself` across all 9 masteries, so the change is surgical (no over-linking).

## 3. Golden overrides + WILL VETO

Every m5/m6 field the reflow touches is a Will-authorized `owner_approved_overrides` entry in
`tools/occult_hunting_golden.json` (9 new keys: 3 Occult positions, 4 Occult connectors, 2 Hunting
connectors), plus a top-level `_WILL_VETO_2026_07_14` section recording the authorization: Will's
2026-07-14 mastery-fix mandate authorizes these UI-only fixes; the golden freeze exists to prevent
SILENT reversion of his tuning, not to block his own vetted fixes; each edit is enumerated so the gate
stays honest and any OTHER drift still fails the build. **Standing UI-on-device rule: these still need
Will's in-game screenshot before promote.**

## 4. The 17 surviving waivers (each: why no law-compliant placement exists)

All arrows are correct; these are residual TIER collisions / graft-broken tiers / a missing-record
phantom. Full one-line reasons in `tools/mastery_ui_waivers.json`.

- **Earth (5 TIER)** - the b38 contiguous Rupture packing (Will's explicit ask); col4 has more grafted
  families than distinct tiers, and no free column exists for a tier-correct Rupture placement.
- **Storm (3 TIER + 1 ICON + 1 OFFCOL)** - Heart of Frost is Storm Nimbus's 2nd tier-2 modifier (no
  2nd tier-2 cell in a column); Frost Nova / Lightning Dash are graft standalones with no free
  tier-5/6 cell outside a family span; Spell Shock 2 is a phantom (its skill record never existed) -
  removal is blocked by the panel auto-discovery gap-break and is Will's delete-vs-repoint call.
- **Spirit (2 TIER)** - Life Drain Cascade is Life Drain's 2nd tier-3 member; Soul Siphon Totem is
  tier2 but every tier-2 cell is a family base or inside a span.
- **Warfare (3 TIER)** - Club Slam (tier2) + its sole modifier Fissure (tier7) cannot be both
  tier-correct AND adjacent-connected (adjacency wins, so the arrow reads); the standalone graft
  Hamstring (tier4) has no free tier-4 cell.
- **Occult [GOLDEN] (1 TIER + 1 CONN)** - Multishot Bolt Trap is Lay Trap's 2nd tier-3 member; the
  Shadow Stalker summon's bar reaches Greater Power (its genuine pet-upgrade) which the `_`-prefix
  detector cannot link by name (a false-positive we keep the correct connection for).

## 5. Round-2 candidates for Will (would shrink the waivers toward zero)

These need Will's DATA/DESIGN decision (out of scope for a UI-position pass):

1. **Storm Spell Shock 2** - delete the phantom button (needs a panel-list surgery that avoids the
   `fix_mastery_panel_buttons` gap-break) or repoint it to a real skill. Clears 2 waivers (ICON+OFFCOL).
2. **Warfare `drxhamstring`** (standalone, tier4) - looks like a redundant duplicate of the real
   Onslaught Hamstring modifier. If Will confirms it is a dead graft, deleting it clears 1 waiver.
3. **Graft-broken skillTiers** (Club Slam base tier2 / mod tier7; Frost Nova tier6; Lightning Dash
   tier5) - if Will authorises editing the `skillTier` field (a tree-tier value, currently treated as
   off-limits by this UI-only pass), each could be placed tier-correct, clearing several TIER waivers.
4. **Shadow Stalker -> Greater Power** - confirm Greater Power is the Shadow Stalker pet's modifier;
   if so a targeted detector rule (summon -> generic pet-modifier directly above) clears 1 waiver.

## 6. Reproduce

```
# design harness (in-memory, no write): apply a plan, report gate findings + grid
py <scratch>/reflow_test.py [mastery...]

# faithful dry-run replay of the real modules + both gates + UI-only diff proof
py <scratch>/dryrun_replay.py       # exit 0 = UI-only diff PASS + gate PASS + A7 golden PASS

# the permanent gate on any arz
py tools/gate_mastery_ui.py [arz]   # 17 waived, 0 unwaived, 0 stale
```

**Confidence.** The reflow is validated by a dry-run replay of the ACTUAL `mastery_ui_vet.py` +
`hunting_occult_ui.py` modules onto the build40 golden: UI-only record-diff, `gate_mastery_ui` PASS,
A7 golden PASS. The connector mechanism (nearest-occupied-above) is the texture-decoded, base-game-
validated rule from `mastery_connection_maps.md`. The one thing not confirmable in this environment is
the in-game pixel render (TQ is not runnable here) - Will's screenshot pass is the final check, per the
standing UI-on-device rule.

## 7. Round 3 (2026-07-15): connOn/connOff ARRAY fix (round-1 vet HIGH)

The round-1 vet loop caught a real defect in round 2's connector edits: both `mastery_ui_vet.py` and
`hunting_occult_ui.py` wrote a single-element `skillConnectionOn` string (`db.set_field(srec,
"skillConnectionOn", "" if action == 'drop' else _STRAIGHT)`) and never touched the paired
`skillConnectionOff` array at all. Two real bugs followed: (1) `'drop'` cleared `skillConnectionOn`
but left a STALE multi-tile `skillConnectionOff` in place, so the dimmed (un-invested) planning tree
still drew a bar the invested tree no longer had; (2) `'straight'` wrote a single `BottomOn01` tile
regardless of how many rows the bar needed to span, so any bar longer than one tile under-drew.

**Ground truth** (`tools/mastery_conn_model.py`, decoded from vanilla): a skill-tree connector is a
PARALLEL PAIR of texture arrays, `skillConnectionOn` (invested) and `skillConnectionOff` (dimmed
planning view) - both always the same length. The array spans tier-rows from the family's own BASE
(bottom) to its own TOP member (inclusive); the bottom/top tiles are fixed (`SkillBar{Bottom,Top}
{On,Off}01.tex`); every tile in between is `SkillBarConnect{On,Off}01.tex` if that row is OCCUPIED by
ANY skill in the column (family or not - proven on 2 independent multi-gap vanilla bars, Warfare's
`dualweapontraining`->`dualwieldtechnique_tumult` and Occult's `envenomweapon`->`envenomweapon_
delirium`, the latter drawing a CONNECT tile over the wholly-unrelated `toxindistillation` sitting
mid-span) or `SkillBarMiddle{On,Off}01.tex` if the row is truly empty. `validate(db, label)` self-checks
this rule against every bar-carrying skill in a database; on the base game it reproduces 42/43 authored
bars exactly - the sole residual (`dualweapontraining`) is a vanilla, mod-untouched Warfare chain whose
SPAN crosses a naming boundary the family-root detector can't bridge (`dualweapontraining` vs
`dualwieldtechnique_*`); confirmed absent from every basename either module's reflow touches, so it does
not affect the fix below (documented limitation, not a build-blocking defect).

**Fix**: `mastery_conn_model.rebuild_into(db, slot, seed_skills, drops)` is the single writer both
`mastery_ui_vet.apply()` and `hunting_occult_ui.apply()` now call after their position moves. For every
TOUCHED family (any moved skill + any skill named in a `'straight'`/`'drop'` connector edit) that HAD an
authored bar in the baseline, it recomputes the geometry-correct `(skillConnectionOn, skillConnectionOff)`
pair for the family's base and clears both arrays on every other member; `'drop'`-listed standalone/leaf
skills are force-cleared on both arrays regardless. Families with no baseline bar are left untouched (no
connector is spuriously invented, e.g. Hunting's `studyprey`). Parity (`len(on) == len(off)`) holds by
construction.

One real, previously-invisible bug surfaced by the correct rebuild: Occult's Lay Trap base
(`drxlaytrap.dbr`) never carried a bar at all in round 2, even after Multishot Bolt Trap
(`drxlaytrap_petmodifier_multishotbolttrap`) was reunited into its column - the modifier sat in the
right cell with nothing visually connecting it. The family-level rebuild now correctly draws Lay Trap's
own 3-tile bar up to it. 2 new `owner_approved_overrides` cover this (`drxlaytrap.dbr::skillConnectionOn/
Off`); the other 6 new overrides are the `skillConnectionOff` parity companions of round 2's existing
`skillConnectionOn` golden entries (58 total, up from 50).

**Gate extended** (`tools/gate_mastery_ui.py`): two new finding categories reuse
`mastery_conn_model.find_defects()`, pure geometry, no family assumption -
- `CONNPARITY` - `skillConnectionOn`/`Off` must be equal length, or both `<= 1` (the vanilla "no bar"
  state, which permits a single vestigial `SkillBarBottomOff01` leftover);
- `CONNSPAN` - a drawn bar's TOP tile must land exactly on an occupied cell in the target column
  (same column for a straight bar, `x+100` for a DRX `_right` bar) - catches under/over-draws.

Both run across all 9 masteries on every gate invocation (build-time and standalone); the mastery-UI
waiver ledger is UNCHANGED at 17 entries (TIER/CONN/OFFCOL/ICON) because 0 CONNPARITY/CONNSPAN
findings exist post-fix.

**Verify** (dry-run replay of the current `mastery_ui_vet.py` + `hunting_occult_ui.py` directly onto
`local/baseline_build40.arz`, md5 `b33c5a44...`):
- record-diff vs baseline: 53 records changed, every touched field is `bitmapPositionX`,
  `bitmapPositionY`, `skillConnectionOn` or `skillConnectionOff` - UI-only, 0 gameplay drift.
- `mastery_conn_model.find_defects()` on the replayed state: **0 CONNPARITY/CONNSPAN defects**.
- `gate_mastery_ui.validate()` on the written arz: **PASS** (17 waived, 0 unwaived, 0 stale) - identical
  waiver profile to round 2, now additionally proving the connector-array invariants.
- `validate_mastery_golden` (A7): **PASS** (52 waived, 0 other) after the 8 new
  `owner_approved_overrides` above.
- Negative test 1 (off-grid button, `bitmapPositionX=977` on a real `mastery 1/skill01.dbr`): gate
  FAILS (1 unwaived GRID finding) - caught.
- Negative test 2 (broken parity: double a bar-carrying skill's `skillConnectionOff` so it no longer
  matches `skillConnectionOn`'s length): gate FAILS (1 unwaived CONNPARITY finding,
  `drxbattlerage skillConnectionOn len=5 != skillConnectionOff len=10`) - caught. This is the exact
  defect class the round-1 vet flagged; the new gate now blocks it structurally, not just for this
  wave's edits.
- `py_compile` on every changed file: OK. `tools/patches/_check_registry.py`: OK (14 modules, order
  hash `211fd8fe...` unchanged - no registry reordering).

Files: `tools/mastery_conn_model.py` (new - the connOn/connOff geometry model + `find_defects`),
`tools/audit_mastery_ui.py` (`DB.from_db()` classmethod so the model can wrap an in-flight
`ArzDatabase` mid-`apply()`; `first()` treats an empty list as "no value" instead of raising),
`tools/gate_mastery_ui.py` (wires in `find_defects`), `tools/patches/mastery_ui_vet.py` +
`tools/patches/hunting_occult_ui.py` (call `rebuild_into` instead of writing a bare string),
`tools/occult_hunting_golden.json` (+8 overrides). NOT yet integration-built; still needs Will's
in-game screenshot before promote (standing UI-on-device rule) - this round changes ONLY the
connector-array correctness, not the visual layout round 2 already showed him conceptually.
