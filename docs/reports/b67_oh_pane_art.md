# b67 OCCULT/HUNTING PANE ART - round 1 (ships build43)

Will's directive (verbatim): "Go ahead and fix the occultist and hunting
mastery black-background fixes. You may need to go into SV files to find the
appropriate background image for the occult mastery skill selection page."

Context: b60 (`tools/patches/mastery_bg_render.py`, shipped build42) fixed the
mastery-pane RENDER MECHANISM for all 9 live masteries (`BitmapSingle` ->
the vanilla `BitmapUIAware` widget the pane slot actually reads) - the panes
stopped being literally black. b60 was explicit that it was a pure structure
upgrade and deliberately did **not** "second-guess the texture CHOICE the
earlier waves made." This wave (b67) is that follow-up: pick the *right*
texture for Occult, verify Hunting needs nothing, and check the select-mastery
screen the b60 report flagged as unexamined.

**One-line verdict:** Occult's tree-pane background was still the vanilla
Rogue/Stealth backdrop (tan parchment, no occult identity) even though it now
*rendered*. Hunting's tree-pane background was already correct (native,
unchanged identity - Hunting was never reskinned by SV). The select-mastery
screen (the "pick a mastery" screen, separate from the tree-pane "skill
selection" screen) inherits 100% vanilla art from the base game and had never
been touched by any prior wave; SV/DRX shipped a bespoke Occult witch portrait
for it that was never wired.

---

## 1. Ground truth: what does the b60-fixed build actually show today?

Read directly from the build42 golden arz (`work/SoulvizierClassic/Database/
SoulvizierClassic.arz`, md5 `f8ef904d`, verified at the top of this session):

| slot | field | value (post-b60) |
|---|---|---|
| Occult (m5) `skillpanebasebitmap.dbr` | `bitmapNames` | `[InGameUI\Skills\StealthSkillBackground01.tex, InGameUI\Controller\Skills\StealthSkillBackground01.tex]` |
| Occult (m5) `masterybitmap.dbr` (decorative circle) | `bitmapName` | `DRXtextures\masterybackdrops\newstealthpanel01.tex` |
| Occult (m5) `skillpanereallocationbitmap.dbr` | `bitmapNames` | `[InGameUI\Skills\StealthSkillReallocationBackground01.tex, ...Controller...]` |
| Hunting (m6) `skillpanebasebitmap.dbr` | `bitmapNames` | `[InGameUI\Skills\HuntingSkillBackground01.tex, InGameUI\Controller\Skills\HuntingSkillBackground01.tex]` |
| Hunting (m6) `masterybitmap.dbr` | `bitmapName` | `InGameUI\Skills\HuntingPanel01.tex` |

Both structurally render fine (b60's fix); Occult's *choice* is the base
game's own Rogue backdrop (a tan/khaki parchment texture, identical in mood to
Hunting's own backdrop - see decode below) with **no occult identity**, while
Hunting's choice is correct because Hunting was never renamed/reskinned by SV
(mastery 6 in the base game literally *is* Hunting; SV built Occult on the
Rogue/Stealth slot [mastery 5], not Hunting's).

Decoded (`tools/tex_decode.py`) side by side:
- `InGameUI\Skills\StealthSkillBackground01.tex` (919x540, base game): a
  weathered tan/khaki stone-tablet pane with a plain round cutout (top right)
  and square cutout (bottom right) - completely mastery-neutral parchment
  art, no green, no purple, nothing occult.
- `InGameUI\Skills\HuntingSkillBackground01.tex` (919x540, base game):
  visually near-identical tan/khaki tablet (both masteries share the same
  "outdoors/leather" family in vanilla TQ) - correct for Hunting, confirms no
  defect there.

## 2. SOURCE HUNT

### 2a. SV 0.98i's own database (upstream/soulvizier_098i/Database/database.arz)

Checked FIRST per the directive. SV 0.98i's own `mastery 5\
skillpanebasebitmap.dbr` / `mastery 6\skillpanebasebitmap.dbr` still point at
the dead `SkillsPanel\skillbackgrounddiablo.tex` (no arc anywhere - not
SVTextures.arc, not DiabloTextures.arc, not drx.arc - ships that file; same
dead reference the b37/b60 waves fixed in our own build). **SV 0.98i itself
never shipped a working Occult (or Hunting) tree-pane background** - there is
no "restore the lost SV art" path for this slot; b60's base-game repoint is
the only route that renders at all, and picking the occult-appropriate
texture is squarely this wave's job, per Will's directive.

SV 0.98i's own **select-mastery** screen records (`records\ingameui\...\
select mastery\masterypane.dbr` and the `xpack\...` 9-mastery sibling) also
point Occult's slot at the plain vanilla `StealthPanelLarge01.tex` /
`stealthpanelmedium01.tex` - SV never reskinned that screen either. So every
piece of bespoke Occult art found below was authored **without ever being
wired into any record**, in SV 0.98i itself and in every build of ours since.

### 2b. `DRXtextures.arc` (`work/SoulvizierClassic/Resources/DRXtextures.arc`, 1464 entries)

A `masterybackdrops\` folder (7 entries) carries pane-art assets. Decoded with
`tools/tex_decode.py` (all uncompressed 32-bit BGRA .tex, per its header
convention):

| file | size | description | verdict |
|---|---|---|---|
| `newstealthpanel01.tex` | 175x175 | pale-skinned witch, dark hood, occult rune/moon-phase circle behind her head, purple/black palette | **ALREADY WIRED** - this IS Occult's current decorative `masterybitmap.dbr` art (both in SV 0.98i's own DB and ours). Confirms SV/DRX designed a distinct Occult identity for this slot. |
| `occultpanellarge.tex` | 250x250 | the SAME witch portrait, larger crop | **NEVER WIRED anywhere** (0 references, SV 0.98i or ours). An exact size match for the base game's older 8-mastery `select mastery\masterypane.dbr` "PanelLarge" class (also 250x250). Clearly the bespoke Occult SELECT-SCREEN preview asset SV/DRX built but never hooked up. **WIRED this wave** (see Part 4). |
| `standardskillbackground_joanna_ver_dark.tex` | 919x540 | dark grey/teal weathered stone tablet, PURPLE accent square in the bottom-right "selected tier" slot, empty round cutout top-right (matches the masterybitmap circle position) - no baked-in decorative content of its own | **NEVER WIRED anywhere** (0 references). Exactly the tree-pane BACKGROUND class size. A generic, mastery-agnostic "dark skin" alternate - the filename's "Joanna" is a DRX texture-artist credit. **CHOSEN for Occult's tree-pane background this wave** (see Part 3) - dark/moody, and its purple accent harmonizes with the witch portrait already drawn over it. |
| `stealthpanel02.tex` | 226x226 | the vanilla Rogue dagger-and-satyr portrait (same art as base `xpack\UI.arc`'s `stealthpanelmedium01.tex`) with an added purple lightning-FX overlay | REJECTED - not occult-themed (still literally the Rogue class portrait), and the wrong size class for the tree-pane background. |
| `stealthpanelbig.tex` | 226x226 | pixel-identical composition to `stealthpanel02.tex` | REJECTED, same reasons. |
| `spiritskillbackground01.tex` | 919x540 | a byte-for-byte visual copy of the base game's own plain green Spirit tree-pane background | REJECTED - not occult-themed, and it's the wrong mastery's identity entirely (a redundant DRX re-package of Spirit, not an Occult asset). |
| `drx_spiritskillbackground01.tex` | 919x540 | dark teal/grey cracked stone with a GHOSTLY green apparition figure BAKED INTO the circle cutout, purple accent square | REJECTED - this is a Dream/spectral-themed asset (ghost, not witch); using it for Occult would visually collide with the witch portrait already drawn over the same circle by `masterybitmap.dbr` (two conflicting figures fighting for the same slot). Likely an unused DRX asset for a different mastery/mod entirely. |

Also swept and confirmed **absent** (documented per the directive's "if SV
shipped no bespoke art, keep vanilla + document" clause): any bespoke
Occult/Hunting select-screen BUTTON icon (`stealthbutton*`/`occultbutton*`/
`huntingbutton*` - 0 hits) and any bespoke mastery-level-BAR art
(`stealthbar*`/`occultbar*`/`huntingbar*`/`masterybar*` - 0 hits, other than
the unrelated connector-bar tile family already handled by other waves). Both
stay vanilla by design, not by oversight.

### 2c. `SVTextures.arc`, `drx.arc`, `_DRX_Textures.arc`, `DiabloTextures.arc`, `HexTextures.arc`

Swept for `occult`/`hunting`/`stealth`/`mastery`/`panel`/`skillbackground`.
`SVTextures.arc`: 0 hits on all keywords. `drx.arc`: only
`meshes/occultbanner.msh` (a 3D banner mesh, unrelated to the 2D pane UI).
`DiabloTextures.arc` (the arc the dead `SkillsPanel\skillbackgrounddiablo.tex`
reference implies should exist): contains only HUD/inventory-bar reskins
(health/mana bars, bag sorting, toolbars) - confirms the dead reference is a
genuinely missing asset, not a naming mismatch; nothing to recover there.

---

## 3. THE FIX - Occult tree-pane background (`tools/patches/oh_pane_art.py`)

`records\ingameui\player skills\mastery 5\skillpanebasebitmap.dbr` ::
`bitmapNames[0]` (mouse/keyboard mode - the texture the b60 `BitmapUIAware`
slot actually reads): `InGameUI\Skills\StealthSkillBackground01.tex` ->
`DRXtextures\masterybackdrops\standardskillbackground_joanna_ver_dark.tex`.

`bitmapNames[1]` (the `InGameUI\Controller\Skills\...` gamepad-mode sibling)
is **left at the vanilla `StealthSkillBackground01.tex` controller texture**
- residual, see below.

Module also **proves** (not just leaves alone) three siblings stay exactly
the b60-shipped vanilla state: Occult's reallocation pane, and Hunting's base
+ reallocation panes. If a future wave collides with any of the four, this
module's `apply()` fails loud immediately rather than silently drifting.

### Residual: controller-mode canvas size mismatch (flagged for Will)

`standardskillbackground_joanna_ver_dark.tex` is 919x540 (the mouse-mode
canvas). The base game's own controller-mode canvas for this slot is 980x540
(61px wider, confirmed via `Controller\Skills\StealthSkillBackground01.tex` -
TQAE added gamepad support and widened the canvas for button-prompt icons).
No DRX/SV asset exists at 980x540, and this module never authors new art
(per the directive), so **gamepad play keeps the vanilla tan backdrop** for
Occult (still renders correctly via b60's fix - just not reskinned) rather
than stretching/padding the 919-wide asset into a 980-wide slot. Mouse/
keyboard play (the overwhelming majority of Steam Workshop TQ play) gets the
full fix. If Will wants gamepad parity, the options are: (a) accept a
stretched/letterboxed variant of the existing asset (technical adaptation,
not new art), or (b) source/author a wider variant - both out of round-1
scope.

### Why not touch the reallocation pane?

The base game's reallocation-mode background is a mastery-INDEPENDENT visual
motif (a blue magic-swirl orb over grey stone - "you are reallocating skill
points", not "you are in the Occult mastery") - every one of the 8 classic
masteries + Dream uses the identical blue-swirl idiom regardless of theme,
confirmed by decoding `StealthSkillReallocationBackground01.tex` (919x540,
blue lightning-orb top-right, grey stone). No DRX/SV asset exists for an
occult-flavored reallocation variant, and inventing one would break the
consistent cross-mastery "you're in respec mode" signal for a screen most
players see only a handful of times per character. Leaving it vanilla is the
correct call, not a gap.

---

## 4. THE FIX - Occult select-mastery-screen preview art (`build_svc_database.
import_occult_select_mastery_art`)

Distinct record family from the tree-pane fix above: the "select mastery"
screen (choose-a-mastery, shown at character creation and each time you add a
new mastery) is driven by a SEPARATE `MasteryPane.tpl` record whose
`masteryMasterySelectedBitmapNames` array holds one preview-art path per
mastery slot, set directly (not composed from sub-widgets). **0 of these
records existed anywhere in our mod's arz before this wave** - the whole
screen was 100% inherited, unmodified, from the base game's own
`database.arz` (this is why `mastery_bg_render`'s b60 gate never touched it:
its documented scope is the tree-pane family only).

TQAE ships **four** DLC-tier copies of this screen (`records\ingameui\...`
[8 masteries, base], `records\xpack\...` [9, +Dream], `records\xpack2\...`
[10, +Rune], `records\xpack4\...` [11, +Alchemy]) - which one the engine
actually renders for a given Custom Quest is not independently provable from
the DB alone (no engine doc or existing gate pins it, and AE bundles all four
DLCs by default). **All four are repointed identically** for safety: a
harmless no-op on any tier the engine does not render, correct on whichever
it does.

Implementation: `records\<tier>\...\select mastery\masterypane.dbr` is
imported **wholesale** from the base game (`_import_base_game_record`,
already used elsewhere in `build_svc_database.py` for the same "reach into
base_db while it's still loaded" pattern - e.g. `apply_mastery_wave2_boosts`,
`expand_caravan`) so every OTHER mastery's array entry stays byte-identical
to vanilla; then the single Stealth/Occult array entry (found by matching
`"stealthpanel"` case-insensitively, fail-loud if not exactly one match) is
repointed to `DRXtextures\masterybackdrops\occultpanellarge.tex`. Runs in
`main()`'s existing base_db-alive window (before `del base_db`), not as a
`tools/patches/` registry module, because creating a brand-new record
requires `base_db` (registry modules only receive `(db, tags)`).

### Size-mismatch residual (flagged for Will)

`occultpanellarge.tex` is 250x250 - an *exact* match for the oldest
`ingameui` tier's "PanelLarge01" class (also 250x250) but ~24px larger than
the `xpack`/`xpack2`/`xpack4` tiers' "PanelMedium01" class (226x226,
confirmed via `xpack\UI.arc`'s `stealthpanelmedium01.tex` - the texture that
actually renders on today's screen, decoded and shown below). The widget is a
plain top-left-anchored bitmap with no stretch-to-fit field (confirmed via
`selectedmasterybitmap.dbr`'s field list: only `bitmapPositionX/Y`, no
width/height), so on the three PanelMedium tiers the art will render ~24px
wider/taller than the vanilla footprint - a modest, low-risk cosmetic overflow
onto the pane's own background (the nearest positioned button/text sits well
clear per the base game's own field values, e.g. the button center in the
xpack2 tier is at `(648, 372)` against the image's `(348, 47)`-anchored
`348+250=598 / 47+250=297` bounding box). **Per this repo's standing UI-on-
device convention** (every prior mastery-UI wave flags in-game confirmation
before promote), this needs Will's in-game screenshot before the fix is
considered fully verified - it is a genuinely new, never-before-touched
record family with no existing render gate, so "resolves in the arc" is
provable today but pixel-perfect fit is not.

Decoded for reference: the vanilla art that plays on the ACTIVE (xpack-tier)
select-mastery screen today, `xpack\UI.arc`'s `stealthpanelmedium01.tex`
(226x226): a Rogue character beside a satyr/faun figure, purple-toned
lighting - already moodier than the tree-pane's tan parchment, but still
visibly the *Rogue* class portrait, not occult witch iconography.
`occultpanellarge.tex` (250x250): the witch portrait described above -
clearly on-theme once wired.

---

## 5. Hunting (mastery 6) - verified, no defect, no action

Checked every art slot Will's directive named:
- Tree-pane background: `InGameUI\Skills\HuntingSkillBackground01.tex` -
  native, base-game Hunting art, unchanged identity (Hunting was never
  reskinned by SV/DRX - it stays "Hunting" in-game). Correct as-is.
- Decorative `masterybitmap.dbr`: `InGameUI\Skills\HuntingPanel01.tex` -
  native, correct.
- Reallocation pane: vanilla `HuntingSkillReallocationBackground01.tex` -
  correct (same universal blue-swirl motif as every other mastery).
- Select-mastery-screen preview + button: vanilla Hunting assets throughout
  every DLC tier - correct (native identity, nothing to repoint).
- Mastery-level bar: vanilla `HuntingSkillBar01.tex` - no bespoke DRX asset
  exists (0 hits), correct as shipped.

No fix needed or made; `tools/patches/oh_pane_art.py`'s `apply()`/`verify()`
both actively PROVE Hunting's 2 pane records stay byte-identical to the
b60-shipped vanilla state (regression guard, not just a documentation claim).

---

## 6. Verification (dry-run replay, no heavy build)

All checks ran against the **build42 golden arz**
(`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, md5 `f8ef904d`,
matches the task brief) and the real TQAE `database.arz` (`base_db`,
74,013 records) - no DB rebuild, no map/Text/Quests build.

1. **Isolated apply()+verify()** - loaded the golden arz + base game arz into
   memory; called `build_svc_database.import_occult_select_mastery_art(db,
   base_db)` then `oh_pane_art.apply(db, {})` + `oh_pane_art.verify(db, {})`
   directly (no full registry run). All completed without raising.
2. **Intended-only delta** - diffed `db._modified` before/after: **exactly 5
   records touched** - `mastery 5\skillpanebasebitmap.dbr` (tree-pane fix)
   plus the 4 `select mastery\masterypane.dbr` tiers (select-screen fix).
   Zero unexpected touches.
3. **Resolves-in-arc** - every `.tex` bitmap ref on all 5 touched records (40
   refs total: the 2 changed + 38 untouched siblings across the 4 masterypane
   arrays) resolves via the SAME archive rule `gate_mastery_bg_render.py`
   uses (mod Resources first, else base Resources, XPack-scoped separately):
   **40/40 resolve**, including the 2 new DRX refs (both `MOD:DRXtextures.
   arc`) and every untouched vanilla entry (proving the wholesale import
   didn't corrupt any sibling mastery's art).
4. **Positive test** - wrote the patched in-memory db to a throwaway `.arz`
   and re-ran `tools/gate_mastery_bg_render.py` as a real subprocess (the b60
   gate, scope unchanged - it does not cover the select-mastery family, only
   the tree-pane one): `RESULT: PASS - all 848 pane/chrome bitmap refs
   resolve; 18 panes are BitmapUIAware w/ bitmapNames`, exit 0. Proves the
   tree-pane fix didn't regress b60's structural invariant.
5. **A7 golden guard** (`tools/validate_mastery_golden.py`, real subprocess)
   on the patched arz: `RESULT: PASS - Occult/Hunting golden state intact
   (83 waived, 0 other)` - the new `bitmapNames` value is covered by the
   updated `owner_approved_overrides` entry (see below); no other drift.
6. **Negative test** - re-ran the SAME guard against a temp copy of
   `occult_hunting_golden.json` with the override key deleted:
   `RESULT: FAIL - 1 unapproved drift(s)` naming exactly
   `field::records\ingameui\player skills\mastery 5\skillpanebasebitmap.dbr::
   bitmapNames`, exit 1. Proves the golden-guard edit is load-bearing (the
   gate genuinely catches this change), not a tautology.

`py_compile` clean on all 3 changed/added Python files;
`tools/patches/_check_registry.py` selfcheck green (26 modules, order hash
`1f0987c0...`); `occult_hunting_golden.json` re-parses as valid JSON.

### A7 golden override

`field::records\ingameui\player skills\mastery 5\skillpanebasebitmap.dbr::
bitmapNames` already existed in `owner_approved_overrides` (from the b60
wave's structural change); its justification string was **extended** (not
duplicated - JSON keys are unique) to also cite this wave's texture-choice
change, Will's verbatim directive, and this report, per the task's "add
sanctioned entries proactively" instruction. No other golden key needed
touching - the select-mastery `masterypane.dbr` family is OUTSIDE the A7
guard's captured scope entirely (it only watches `records\ingameui\player
skills\mastery {5,6}\` + 2 named `xpack`/`xpack3` panectrl overrides; "select
mastery" is a sibling directory, never a descendant of "mastery 5\").

---

## 7. Ship coupling + open items for Will

**DB-only fix** (records + one new-but-idempotent base-game import; no Text
tag, no map/Quests change). Ships in the next DB build as build43.

**Flagged for Will's veto/in-game screenshot** (per this repo's standing
UI-on-device rule):
1. Is `standardskillbackground_joanna_ver_dark.tex` the right feel for
   Occult's tree-pane background? (dark grey/teal stone, purple accent -
   the only 919x540 unused asset in the DRX archive that isn't already a
   different mastery's redundant copy or a conflicting Dream/ghost asset.)
2. Is wiring `occultpanellarge.tex` (the witch portrait) into the
   select-mastery preview slot across all 4 DLC tiers the right call, given
   the ~24px oversize on 3 of the 4 tiers (modest, low-risk per the position
   math above, but unverified in-game)?
3. Controller-mode Occult tree-pane background stays vanilla tan (no 980x540
   DRX asset exists) - acceptable, or worth a follow-up?
