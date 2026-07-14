# b40 - Mastery skill-tree BLACK BACKGROUND: deep RCA + fix

Lane: `feat/b40-mastery-bg`. Author: MASTERY-BACKGROUND DEEP-RCA implementer, 2026-07-13.
Ground truth: `scratchpad/baseline_build38.arz` (the LIVE build38a-dev DB, arz `6631f252`),
the base-game `Database/database.arz` + `Resources/*.arc`, the DEPLOYED DEV `Resources/*.arc`
(`CustomMaps/SoulvizierClassicDEV`), and `upstream/soulvizier_098i`. No heavy build; all
findings are read-only probes + a dry-run registry replay.

## Will's report (THIRD filing, verbatim intent)

> The mastery skill-tree screens STILL have a BLACK background. There should be the
> original SV background IMAGE behind the skill nodes (his Occult Mastery screenshot: pure
> black behind the purple skill web). b37 `hunting_occult_ui` and b38 `mastery_ui_audit`
> both claimed to fix this by repointing background bitmap fields, yet it STILL renders
> black in build38a-dev.

## TL;DR - the true mechanism

The AE engine renders the skill-pane backdrop **only from a `BitmapUIAware` record's PLURAL
`bitmapNames` array**. Our mastery-pane background records are the older SV/TQ-IT `BitmapSingle`
template (singular `bitmapName`), which the AE skill-pane renderer does **not** display in that
slot -> the pane is BLACK **regardless of what the bitmap field points at**. The b37/b38 fix only
rewrote the *value* of `bitmapName` on the wrong-template record, so it could never work. The fix
is to convert the records to the base-game `BitmapUIAware` shape.

## Why the two prior fixes failed (the same class of fix, twice)

Both b37 `hunting_occult_ui` (masteries 1-8) and b38 `mastery_ui_audit` (Dream) did:

```
db.set_field(skillpanebasebitmap.dbr, "bitmapName", r"InGameUI\Skills\<Class>SkillBackground01.tex")
```

i.e. they changed the *texture the record points at*, on a `BitmapSingle` record, leaving the
template untouched. That is a no-op against the real mechanism (below).

## Evidence chain

### 1. The reference chain (how the backdrop is wired)

`SkillPaneCtrl.tpl` (the per-mastery `panectrl.dbr`) has the slot fields that name the backdrop
records (base-game `mastery 1\panectrl.dbr`):

```
skillPaneBaseBitmap             = Records\InGameUI\Player Skills\Mastery 1\SkillPaneBaseBitmap.dbr
skillPaneBaseReallocationBitmap = Records\InGameUI\Player Skills\Mastery 1\SkillPaneReallocationBitmap.dbr
skillPaneMasteryBitmap          = Records\InGameUI\Player Skills\Mastery 1\MasteryBitmap.dbr
```

Our DB's `panectrl.dbr` chain is intact (verified: `skillPaneBaseBitmap` resolves to our
`skillpanebasebitmap.dbr` for all 8 masteries). So the pane finds the record. The record itself
is the problem.

### 2. The record diverges from the working base game (BASE vs OURS)

`records\ingameui\player skills\mastery 1\skillpanebasebitmap.dbr`:

| | template | field shape | value |
|---|---|---|---|
| **BASE (works)** | `BitmapUIAware.tpl` | `bitmapNames` (2 entries) | `[InGameUI\Skills\WarfareSkillBackground01.tex, InGameUI\Controller\Skills\WarfareSkillBackground01.tex]` |
| **OURS (black)** | `BitmapSingle.tpl` | `bitmapName` (1 entry) | `InGameUI\Skills\WarfareSkillBackground01.tex` (the b37 repoint) |
| **SV 0.98i (origin)** | `BitmapSingle.tpl` | `bitmapName` (1 entry) | `SkillsPanel\skillbackgrounddiablo.tex` (never packaged) |

This holds for **all 9 masteries** (1-8 + Dream). Template-usage counts: **BASE has 54
`BitmapUIAware` records; OURS has ZERO** (`BitmapSingle` only). SV 0.98i is a TQ-Immortal-Throne-era
mod that predates AE's `BitmapUIAware`; our DB inherits its `BitmapSingle` skill-pane records
verbatim. `BitmapUIAware`'s second `bitmapNames` entry is the AE controller-UI variant
(`InGameUI\Controller\Skills\...`) - the exact AE feature `BitmapSingle` lacks.

### 3. DECISIVE: same resolvable texture, different template -> black

- The b37/b38 fix already points our `BitmapSingle` record at **`InGameUI\Skills\WarfareSkillBackground01.tex`** - the *exact* texture the working base game uses (confirmed in `baseline_build38.arz`).
- That texture **provably resolves at runtime**: it exists in base `InGameUI.arc` as `skills/warfareskillbackground01.tex` (1,985,181 B), and base `InGameUI.arc` **is in the custom-quest resource path** - our mod ships **no** `InGameUI.arc`, yet in-game skill **icons**, which live ONLY in base `InGameUI.arc` (`icons/skills/...`), render fine. So the resource path reaches base `InGameUI.arc`.
- Yet build38a-dev renders **black**.

Same texture path + `BitmapSingle` => black; same texture path + `BitmapUIAware` (base) => renders.
The **only** differentiator is the template + field shape - which the value-repoint never touched.
This eliminates "missing/unresolvable texture" and "wrong texture value" as causes and pins the
mechanism to the **template**.

### 4. What the texture is NOT

- Not a missing asset: `InGameUI\Skills\<Class>SkillBackground01.tex` (+ `Controller\Skills\` variant) for **every** class is present + non-empty in base `InGameUI.arc` (all 36 checked: 18 base bg + 18 reallocation, 1.9-2.1 MB each).
- Not the SV `SkillsPanel\skillbackgrounddiablo.tex`: that texture is in **no** shipped or base arc (the mod never packaged a `SkillsPanel.arc`; `DiabloTextures.arc` holds only HUD "diablo" art). So the original SV records were *already* broken on their own path even before the AE template issue - but shipping that texture would **not** have helped, because `BitmapSingle` still would not render.
- Not a per-mastery override problem: the `panectrl` chain is intact; every mastery's backdrop record is reachable.

## The fix - `tools/patches/mastery_bg_template.py`

Convert the **18 live mastery-pane background records** (masteries 1-8 base + reallocation, and
the Dream mastery `records\xpack\ui\skills\mastery 9\`) from `BitmapSingle` to the **base-game
`BitmapUIAware` shape**, reproducing the working base configuration exactly:

```
templateName     = database\Templates\InGameUI\BitmapUIAware.tpl
FileDescription  = BitmapUIAware
bitmapNames      = [InGameUI\Skills\<Class>SkillBackground01.tex,
                    InGameUI\Controller\Skills\<Class>SkillBackground01.tex]   (realloc = ...ReallocationBackground01)
bitmapPositionsX = [0, 0]
bitmapPositionsY = [0, 0]
```

(the singular `bitmapName` / `bitmapPositionX` / `bitmapPositionY` fields are dropped, so each record
byte-matches the base-game record). Per-mastery class: 1 Warfare, 2 Defense, 3 Earth, 4 Storm,
5 Stealth, 6 Hunting, 7 Spirit, 8 Nature; **Dream uses Nature's backdrop** (base-game convention).

This is a **template/field-shape** fix, a fundamentally different class from the twice-failed
value-repoint. `mastery_bg_template` is registered after `mastery_ui_audit` and is the **sole owner**
of the mastery-pane backgrounds: the b37/b38 background repoints are **removed** (from
`hunting_occult_ui` 5a and `mastery_ui_audit` `_DREAM_BG`), so there is no collision (verified).

### Why base-parity textures (not the DRX dark backdrops)

The mod ships `DRXtextures.arc` with a small `masterybackdrops/` set (`occultpanellarge.tex`,
`standardskillbackground_joanna_ver_dark.tex`, `spiritskillbackground01.tex`, stealth panels). Those
resolve too and could give a darker DRX look. This fix deliberately uses the **base-game per-mastery
backgrounds** because they are the *proven-working* configuration (correct dimensions, guaranteed
render, one authoritative backdrop per class), which is the safe answer to a P0 "it's black" on a
third filing. **Follow-up option for Will:** if he prefers the DRX dark aesthetic behind the purple
skill web, point `bitmapNames[0]` at `DRXtextures\masterybackdrops\standardskillbackground_joanna_ver_dark.tex`
(and `...occultpanellarge.tex` for Occult) - a one-line texture swap in this module once the template
mechanism is in place.

## Acceptance proof (no game run)

Dry-run replay (`scratchpad/b40_dryrun_verify.py`) applied `mastery_bg_template` to a copy of the
LIVE `baseline_build38.arz` and verified, for all 18 records:
- template == `BitmapUIAware.tpl`, FileDescription == `BitmapUIAware`, `bitmapNames` == 2 entries, stale singular `bitmapName` **gone**, `bitmapPositionsX/Y` == `[0,0]`;
- **every one of the 36 resulting texture paths RESOLVES + is NON-EMPTY in the shipped Resources** (DEV over base): all in base `InGameUI.arc`, `skills/*` 1,985,181 B, `controller/skills/*` 2,116,941 B. **0 unresolved.**

Registry coexistence (`scratchpad/b40_registry_coexist.py`) ran `hunting_occult_ui` +
`mastery_ui_audit` + `mastery_bg_template` under the real `run_registry` machinery:
**collision gate clean (no record written by 2+ modules)**; the two prior modules no longer touch
the backgrounds; `mastery_bg_template` converts all 18.

Gates: `py_compile` clean (no SyntaxWarning); `tools/patches/_check_registry.py` OK (12 modules);
`validate_mastery_golden.py` on the patched arz = **PASS** (63 waived, 0 hard drift). The 28 golden
drift keys are the pure template/field-shape conversion on the golden-tracked Occult/Hunting
skillpane records, recorded as `owner_approved_overrides` (Will's THIRD report authorizes the fix;
the F5 / b37-background waiver precedent).

## Deploy note

This is a **DB-only** fix (18 records in `SoulvizierClassic.arz`); no Text/Levels/Quests/Resources
change. The textures it references are base-game art already reachable at runtime - **nothing new
needs packaging**. It lands via a normal `build_svc_database.py` run (the b40 integration/build lane),
which executes the registry including `mastery_bg_template`.

## Files

- `tools/patches/mastery_bg_template.py` - the fix (new registry module).
- `tools/patches/__init__.py` - REGISTRY += `mastery_bg_template` (after `mastery_ui_audit`).
- `tools/patches/hunting_occult_ui.py` - removed the failed 5a background repoint (kept button shapes).
- `tools/patches/mastery_ui_audit.py` - removed the failed `_DREAM_BG` repoint (kept icons/de-dup/reflow).
- `tools/occult_hunting_golden.json` - +28 owner-approved overrides (Occult/Hunting bg template conversion).
