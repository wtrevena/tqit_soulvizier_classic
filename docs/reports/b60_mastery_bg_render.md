# b60 MASTERY PANE BLACK-BACKGROUND - RCA + fix (ships build42)

Will (2026-07-14): "the mastery skill selection screens STILL have a black background."
Method directive (verbatim): "refer to how the mastery background images are rendered in
SVAERA or the base game and then see if we can use that to determine what is broken in our
build."

**One-line root cause:** the b37/b38 waves (`hunting_occult_ui.py`, `mastery_ui_audit.py`)
correctly repointed every mastery pane's *texture path* off the dead DRX `SkillsPanel\...diablo`
arc onto a real base-game `InGameUI\Skills\...` texture, but left the record's **widget class**
as `BitmapSingle.tpl` writing the singular `bitmapName` field. The vanilla pane-background slot
is `BitmapUIAware.tpl`, which reads the **plural** `bitmapNames` array instead. `bitmapName` is
never read by that slot, so the texture resolves in the arc (a static check would call it fine)
but the engine never requests it at runtime -> the pane draws nothing -> BLACK. This is the same
"resolves statically, wrong wiring" class as the graft-icon / boss-arena art families
(`tools/validate_render_chain.py`'s A9 contract).

---

## 1. Ground-truth extraction (Will's directive)

**SVAERA ships no `Database` at all** (`reference_mods/SVAERA_customquest/` contains only
`Resources/Levels.arc` + `Resources/Quests.arc` - verified by directory listing). A "Custom
Quest" mod of that shape inherits every DB record, including the mastery-UI panes, from the
**base game's own `Database/database.arz`** unmodified. So for this RCA, "SVAERA's render
chain" and "the base game's render chain" are **the same ground truth** - there is no SVAERA-
specific UI override to reconcile against.

### 1a. Base game (= SVAERA) render chain - all 9 live masteries, both panes

Read directly from `<TQAE install>/Database/database.arz` (18 records: masteries 1-8 under
`records\ingameui\player skills\mastery N\`, Dream/9 under `records\xpack\ui\skills\mastery 9\`,
each with `skillpanebasebitmap.dbr` + `skillpanereallocationbitmap.dbr`):

| field | value (every one of the 18 records) |
|---|---|
| `templateName` | `database\Templates\InGameUI\BitmapUIAware.tpl` |
| `bitmapName` (singular) | **absent** |
| `bitmapNames` (plural, 2-entry array) | `[ <Class>Skill(Reallocation)Background01.tex, InGameUI\Controller\Skills\<samename> ]` |

Concretely: mastery 1 (Warfare) base pane = `bitmapNames = [InGameUI\Skills\
WarfareSkillBackground01.tex, InGameUI\Controller\Skills\WarfareSkillBackground01.tex]`, and so
on for Defense/Earth/Storm/Stealth/Hunting/Spirit/Nature; Dream/9 in the base game re-uses the
Nature texture (`NatureSkillBackground01.tex` + its controller sibling) - a base-game texture
*choice*, not a structural difference (its record is BitmapUIAware like every other mastery).

The shared chrome (`records\ingameui\player skills\mastery base\`) in the base game points at
`InGameUI\Skills\{UndoBtn,UndoMasteryBtn}{Up,Down,Over,Disabled}01.tex` +
`InGameUI\Skills\{CostPerPoint,CurrentGold}01.tex` - all 10 texture refs verified present in the
base `Resources\InGameUI.arc` (1,812 entries).

### 1b. Our shipped build - same 18 pane records + 4 chrome records

Read from **both** `local/baseline_build40.arz` (deployed Steam build, md5 `b33c5a44`) and the
in-flight `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (build41-work, md5 `eb8bc377`)
- **identical result in both**, so this is a standing defect, not a build41 regression:

| field | value (every one of the 18 records, both arzs) |
|---|---|
| `templateName` | `database\Templates\InGameUI\BitmapSingle.tpl` |
| `bitmapName` (singular) | the correct base-game mouse texture (e.g. `InGameUI\Skills\WarfareSkillBackground01.tex`) - the b37/b38 fix DID land, on the wrong field |
| `bitmapNames` (plural) | **absent** |

The 4 chrome records (`undobutton.dbr`, `undomasteryselectionbutton.dbr`,
`costperpointnumberbitmap.dbr`, `playergoldnumberbitmap.dbr`) still point at
`SkillsPanel\{undobtn*,undomasterybtn*,costperpoint,currentgold}diablo01.tex` - and **no
`SkillsPanel.arc` exists anywhere** (verified: not shipped by the mod's `work/SoulvizierClassic/
Resources/`, not shipped by base game) - a completely dead reference, invisible/blank chrome
icons on top of the black pane.

### 1c. The differential = the break

1. **STRUCTURE (the black background itself):** our 18 pane records are `BitmapSingle.tpl` +
   `bitmapName`; vanilla is `BitmapUIAware.tpl` + `bitmapNames`. The pane-background widget slot
   (`panectrl.dbr::skillPaneBaseBitmap` / `...ReallocationBitmap`) only ever asks its bound
   widget for `bitmapNames[0]`; a `BitmapSingle` widget answers with nothing at that slot, so
   nothing draws. The texture resolving in the arc (which is all the old fix verified) is
   necessary but not sufficient.
2. **RESOLUTION (secondary, the chrome):** the 4 shared chrome records reference an arc
   (`SkillsPanel.arc`) that is shipped by neither the mod nor the base game - fully unresolvable,
   independent of the structure bug.

Both are fixed by this wave; (1) is the one that actually produces "black background."

---

## 2. The fix

`tools/patches/mastery_bg_render.py` (registered in `tools/patches/__init__.py` REGISTRY
immediately after `hunting_occult_ui` + `mastery_ui_audit`, since it upgrades the texture those
two waves set):

- **Pane restructure** (18 records: masteries 1-8 base+reallocation, Dream/9 base+reallocation):
  read the current singular `bitmapName` (fail-loud if absent/non-`InGameUI\` - guards against
  running before the earlier waves, or a future regression), derive its
  `InGameUI\Controller\Skills\...` sibling by inserting `Controller\` after the arc-name
  component, set `templateName -> BitmapUIAware.tpl`, `FileDescription -> "BitmapUIAware"`,
  `bitmapNames -> [mouse, controller]`, `bitmapPositionsX/Y -> [0, 0]`, and drop the now-unread
  singular `bitmapName`/`bitmapPositionX`/`bitmapPositionY` fields. Pure structure upgrade - it
  does **not** second-guess the texture *choice* the earlier waves made (e.g. Dream/9 currently
  uses the Spirit texture rather than base game's Nature reuse - that is untouched, out of
  scope, and it resolves fine either way).
- **Chrome repoint** (4 records): `bitmapNameUp/Down/InFocus/Disabled` on the two undo buttons,
  `bitmapName` on the two number-bitmaps -> their base-game `InGameUI\Skills\...` equivalents
  (fail-loud if a targeted field is absent, so an upstream shape change is never silently
  no-op'd).
- `verify(db, tags)` (post-finalization hook): re-asserts all 18 panes are `BitmapUIAware` with
  non-empty `bitmapNames`, and that **no** live pane/chrome record still references the dead
  `SkillsPanel\` arc anywhere in its fields. Fail-loud SystemExit on any survivor.

`tools/gate_mastery_bg_render.py` (standalone build-gate, mirrors
`tools/validate_render_chain.EngineArcResolver`'s engine-faithful archive rule - mod Resources
first, then base Resources, XPack-scoped separately): checks (A) every `.tex` bitmap field on
every live mastery-UI record resolves in the shipped arc set, and (B) all 18 pane records are
`BitmapUIAware` with non-empty `bitmapNames`. `usage: py tools/gate_mastery_bg_render.py <arz>
<mod_resources_dir> <game_dir>`; exit 0 = PASS, 1 = FAIL, 2 = load error.

### Scope (deliberately excluded, per the RCA)

- `records\xpack\ui\skills\mastery 9\11-15-06\...` - an ArtManager auto-backup subfolder, 0
  references from any live pane/panectrl - dead, unreachable by any player.
- `records\skills\scroll skills\masteries\earth\...` - a DRX dev-leftover mastery tree whose
  `panectrl` has 0 references - unreachable by any player.

Both still carry the old `SkillsPanel\...diablo` refs but are unreachable; repointing them would
be noise against a gate scoped to the 9 LIVE player masteries (1-8 + Dream/9) exactly as Will's
directive framed the ask (the screens players actually see).

---

## 3. Verification (dry-run replay, no heavy build - build41 map is building elsewhere)

All four checks below ran against the **current live golden**, `work/SoulvizierClassic/Database/
SoulvizierClassic.arz` (build41-work, md5 `eb8bc377`) - the same defect is independently
confirmed present in the shipped Steam build, `local/baseline_build40.arz` (md5 `b33c5a44`).

1. **Negative test** - `gate_mastery_bg_render.validate()` run against the **unmodified** golden
   arz: `RESULT: FAIL - 46 mastery-UI render defect(s)` (36 struct-fails = 18 records x 2 checks
   each [templateName + bitmapNames], + 10 UNRESOLVED = the 4 chrome records' dead `SkillsPanel`
   refs). Confirms the gate genuinely catches today's shipped defect - it is not a tautology.
2. **Isolated apply()+verify()** - loaded the golden arz into memory, called
   `mastery_bg_render.apply(db, tags)` then `.verify(db, tags)` directly (no full registry run,
   no DB rebuild). Both completed without raising; `apply()`'s own log confirms all 18 panes
   converted to `BitmapUIAware` and all 4 chrome records repointed.
3. **Intended-only delta** - diffed `db._modified` before/after: **exactly 22 records touched**
   (the 18 panes + 4 chrome), matching the expected set precisely - zero unexpected touches,
   zero missing.
4. **Positive test** - wrote the patched in-memory db to a throwaway `.arz` and re-ran
   `gate_mastery_bg_render.py` as a real subprocess against it: `RESULT: PASS - all 848
   pane/chrome bitmap refs resolve; 18 panes are BitmapUIAware w/ bitmapNames`, exit code 0.

No arc changes are needed (every mouse + controller texture the fix references already resolves
in the base game's `Resources\InGameUI.arc`, independently verified for all 18 pane pairs + all
10 chrome refs against the base arc's 1,812-entry name index) - so there is no append-only arc
diff to prove; the fix is DB-record-only.

`py_compile` clean on all 3 changed/added files; `tools/patches/_check_registry.py` selfcheck
green (14 modules, order hash `08f85000d1e6...`).

---

## 4. Ship coupling

DB-only fix (records + Text-free - no new tag needed, every texture reused verbatim). No map,
Quests, or Text change. Ships in the next DB build as part of build42; no coordination needed
with the concurrent build41 map wave.
