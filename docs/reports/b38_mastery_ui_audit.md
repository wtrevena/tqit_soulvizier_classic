# b38 - Mastery UI + Skill-Layout Audit

Lane: `feat/b38-mastery-ui` (base `d6ed889`, the merged b37 state).
Author: MASTERY UI + SKILL LAYOUT AUDIT implementer, 2026-07-13.
Ground truth: `baseline_build36.arz` (LIVE build36a canonical arz, md5 `63ca7cf8`) +
the b37 code state in this worktree. NO heavy build was run; all findings are from
read-only replays of the registry modules against a copy of the baseline arz and
`.tex` resolution against the shipped mod arcs UNION the base-game arcs.

## Will's report (2026-07-13, verbatim intent)

> In EARTH mastery two skills have NO icons and are OUT OF PLACE at the start of the
> Rupture chain; the Rupture chain should start lower and those two icons must be
> added into it. All skills and icons FUNCTION but many are in the WRONG PLACE. Also
> RUPTURE APPEARS TWICE in the Earth tree. There are likely issues like this across
> ALL masteries. Also MANY mastery screens have a BLACK BACKGROUND (multiple Steam
> users report this too; the b37 hunting_occult_ui module already fixed backgrounds
> for Hunting + Occult).

Every symptom is confirmed with a concrete root cause below.

## Method / resolution model (how "does the icon/background resolve?" was decided)

A TQ resource path resolves by its leading path component(s):
- **1-component** `Arc\internal\file.tex` -> `Arc.arc` (a shipped mod arc, verified
  entry-present; or a base-game arc at the Resources root, prefix trusted).
- **2-component DLC** `DLCfolder\Arc\internal\file.tex` -> `DLCfolder/Arc.arc`
  (e.g. `XPack3\UI\icons\skills\firenova_up.tex` -> base `XPack3/UI.arc`). This model
  was proven empirically (the exact internal entry exists in the base DLC arc).

A path is BROKEN iff its leading component(s) match neither a shipped mod arc nor a
base-game arc. This is what flags `_DRX_Textures\...` (SVAERA ships a `_DRX_Textures`
arc; this mod ships `DRXtextures.arc`, a different arc, and the referenced basenames
exist in NO shipped or base arc) and `SkillsPanel\...` (no such arc anywhere).

## Root causes (five defect classes)

### RC-1 - BROKEN GRAFT ICONS (`_DRX_Textures\`) - 8 skills, 5 masteries
The build36 LANE-B SVAERA graft (`build_svc_database.py::graft_svaera_mastery_skills`)
imported 14 player skills. Seven point their icon bitmaps at
`_DRX_Textures\InGameUI\icons\skills\...` - an arc SVAERA ships but this mod does not
(we ship `DRXtextures.arc`). An eighth grafted skill (`drx_nymph_petmodifier_rootwave`
= Nature "Sylvan Protection") shipped with NO `skillUpBitmapName` field at all. Result:
8 iconless skill buttons. The other graft members already point at base DLC arcs
(`XPack3\UI\...`) which resolve fine, so the author simply used the wrong prefix on the
SVAERA-custom icons. **These are exactly Will's "two skills have NO icons" (the Earth
pair `drxrupture_burning` + `drxrupture_flare`) plus five more across masteries.**

### RC-2 - DUPLICATE "Rupture" / "Flare" (Earth) - the "appears twice" bug
Proven across databases (drxflamesurge = Earth "Flame Surge" line):

| record | 098i | sv0.9 | build36 | base AE |
|---|---|---|---|---|
| `drxflamesurge` | tagRuptureNAME | tagRuptureNAME | tagRuptureNAME | tagSkillName113 "Flame Surge" |
| `drxflamesurge_flamearch` | tagFlareNAME | tagFlareNAME | tagFlareNAME | tagSkillName103 "Flame Arch" |

SV 0.98i (amgoz1, the untouchable design bible) **deliberately** renamed the base
game's Earth "Flame Surge" line to display **"Rupture"** (`drxflamesurge`, a STAFF
skill: RangedOneHand=1) and **"Flare"** (`drxflamesurge_flamearch`). The build36 graft
then ADDED a second, BOW-variant Rupture line - `drxrupture` (Bow=1) + `drxrupture_burning`
+ `drxrupture_flare` - reusing `tagRuptureNAME` / `tagFlareNAME`. -> two "Rupture" and
two "Flare" on the Earth screen. **The correctly-wired, live, bible-canonical Rupture is
`drxflamesurge`** (staff, in 098i, its staff tooltip matches); it is SV-original and is
left UNTOUCHED. The duplicate is the graft (build36 addition, editable).

### RC-3 - INTERLEAVED / INVERTED Earth Rupture chain - the "wrong place" bug
The graft crammed firenova/rupture/burning/flare into the free cells of Earth UI column
x=428, INTERLEAVING them with the pre-existing Ring-of-Flame chain (`ringofflame`,
`softenmetal`) + Spontaneous Combustion, with the base skill (`drxrupture`) sitting HIGH
(y=93) ABOVE its own modifiers (an inverted chain). 098i's column 428 was a clean
Ring-of-Flame layout; the graft filled its gaps badly.

### RC-4 - BLACK BACKGROUND - universal (all 9 masteries)
Every mastery's `skillpanebasebitmap` / `skillpanereallocationbitmap` points at
`SkillsPanel\skillbackgrounddiablo.tex` - an arc that resolves NOWHERE (18 records).
The b37 `hunting_occult_ui` module already repoints masteries 1-8 to
`InGameUI\Skills\<Class>SkillBackground01.tex` (all 16 confirmed present). The residual
black screen is the DREAM mastery (xpack mastery 9), which `hunting_occult_ui` does not
cover.

### RC-5 - pre-existing structural defects (documented, NOT fixed here)
Two defects fall outside a safe UI pass and are reported for their owners:
- **Storm UI slot25 -> `drxspellbreaker_spellshock2.dbr`** is a dead reference: the
  skill has NEVER existed in any source, and the slot is present VERBATIM in 098i
  (SV-original). Repointing would duplicate slot14 (which already holds the real
  `_spellshock`) or invent a skill; it needs Will's design call.
- **Hunting slot18 (`drxtakedown_eviscerate`) and slot22 (`drxspear_tempest`) both
  display `tagSkillName090`** - a duplicate name in the GOLDEN-tracked Hunting tree
  (Will's hand-tuned mastery; the `occult_hunting_golden.json` A7 gate covers masteries
  5/6). It is pre-existing in build36. This belongs to the hunting_occult lane (b37's
  `hunting_occult_improvements` does an Eviscerate rename - that lane should confirm
  whether its rename already resolves this, and apply a golden waiver if a UI edit is
  needed). It is intentionally OUT of scope for `mastery_ui_audit` (disjoint from the
  golden masteries).

## Per-mastery defect table (baseline build36 + b37 code state)

Legend: BG = black background (records); ICON = iconless skill (`_DRX_Textures\` or
empty); DUP = duplicate display-name; MISSING = UI slot -> nonexistent skill.
"Owner" = which module fixes it in b38.

| Mastery | BG | ICON (skill) | DUP | MISSING | Owner |
|---|---|---|---|---|---|
| 1 Warfare | 2 | 1 `drx_clubslam_fissure` | - | - | ho-ui (bg); **mastery_ui_audit** (icon) |
| 2 Defense | 2 | 1 `drx_activeblock` | - | - | ho-ui (bg); **mastery_ui_audit** (icon) |
| 3 Earth | 2 | 3 `drx_firenova`, `drxrupture_burning`, `drxrupture_flare` | 2 Rupture, Flare | - | ho-ui (bg); **mastery_ui_audit** (icons + de-dup + reflow) |
| 4 Storm | 2 | 1 `drxfrostnova` | - | 1 slot25 (SV-original dead ref) | ho-ui (bg); **mastery_ui_audit** (icon); *unfixed: slot25* |
| 5 Occult | 2 | - | - | - | ho-ui (bg) |
| 6 Hunting | 2 | - | 1 tempest/eviscerate (golden) | - | ho-ui (bg); *unfixed: dup -> hunting_occult lane* |
| 7 Spirit | 2 | - | - | - | ho-ui (bg) |
| 8 Nature | 2 | 1 `drx_nymph_petmodifier_rootwave` (empty icon) | - | - | ho-ui (bg); **mastery_ui_audit** (icon) |
| 9 Dream (xpack) | 2 | 1 `drx_summoncopy` | - | - | **mastery_ui_audit** (bg + icon) |

Note: Spirit slot25/27/28/29 (SandsOfSleep, DistortionWave chain) and the whole Dream
skill roster use `XPack\UI\Icons\Skills\...` / `XPack3\UI\...` paths, which RESOLVE via
the 2-component DLC model - they are NOT defects (an earlier naive audit false-flagged
them; corrected).

## The fix (`tools/patches/mastery_ui_audit.py`, registered after `hunting_occult_ui`)

All edits are on GRAFT skill records (build36 additions, editable), UI-button records
(F5 UI-defect-fix precedent; Earth is NOT golden-tracked), and the Dream background
records. ZERO SV-original skill-design edits.

1. **8 icon repoints** -> resolving equivalents (the exact base-game icon where it
   exists: `firenova`/`activeblock`/`dreamimage` from base `XPack3\UI`; thematically
   matched base InGameUI icons for the rest; the base Sylvan Nymph icon for rootwave).
2. **Earth de-dup** (graft records only): `drxrupture` -> "Flame Surge" (tagSkillName113
   + tagSkillDescription113 + FlameSurge icon); `drxrupture_flare` -> "Flame Arch"
   (tagSkillName103 + tagSkillDescription103 + FlameArch icon). Both base-game name/desc
   tags were FREED by SV's own rename (unused in the mod) and resolve at runtime;
   `validate_tags` does not require base-game tags in Text.arc (identical to the graft
   already using `x3tagSkillEarthFireNova` + `tagSkillName185`). The SV-canonical
   `drxflamesurge` "Rupture" / `drxflamesurge_flamearch` "Flare" stay untouched -> exactly
   ONE Rupture and ONE Flare remain. Earth graft chain now reads
   **Flame Surge / Burning Bolts / Flame Arch / Fire Nova** - zero collisions.
3. **Earth column-428 reflow** (UI-button positions only): Ring-of-Flame (y=403,341) +
   graft chain `rupture(279) -> burning(217) -> flare(155)` contiguous with the base
   LOWER, then the two standalones on top (spontaneous 93, firenova 31). Fail-loud if a
   slot no longer holds its expected skill.
4. **Dream (xpack m9) background** -> resolving `InGameUI\Skills\SpiritSkillBackground01`
   (best-effort: no dedicated Dream backdrop ships; strictly better than the black pane;
   masteries 1-8 handled by `hunting_occult_ui`).

## Dry-run verification (no heavy build)

Replayed `hunting_occult_ui` + `mastery_ui_audit` against a COPY of `baseline_build36.arz`
and re-ran the full audit (`scratchpad/dry_run_verify.py`):

- **Module-owned defects (ICON / BG / POS-collision) remaining: 0** across all 9 masteries.
- **Earth Rupture/Flare duplicate-display remaining: 0.**
- **Earth column-428 post-reflow: 7 distinct cells, collision=False**, chain layout:
  `ringofflame(403) softenmetal(341) | rupture=Flame Surge(279) burning=Burning Bolts(217)
  flare=Flame Arch(155) | spontaneous(93) firenova(31)`.
- Residuals, both correctly out of module scope: Storm slot25 MISSING (SV-original dead
  ref) + Hunting tempest/eviscerate DUP (golden-tracked, hunting_occult lane).
- Gates: `py_compile` OK; `tools/patches/_check_registry.py` OK (10 modules).

## Residual / follow-up items for Will (need his call or another lane)

1. **Storm slot25** dead reference (`drxspellbreaker_spellshock2`) - SV-original; decide
   the intended skill or accept the harmless phantom button.
2. **Hunting tempest/eviscerate** both show `tagSkillName090` - golden-tracked; the
   hunting_occult lane should confirm whether b37's Eviscerate rename fixes it and, if a
   UI edit is needed, add a golden waiver.
3. **Nature "Sylvan Protection"** (`drx_nymph_petmodifier_rootwave`) also has an EMPTY
   `skillDisplayName` (no name text). This pass gives it a resolving icon; the display-tag
   repair is left for a targeted follow-up (needs the exact x3 Sylvan Protection tag; the
   graft comment says these x3 tags resolve at runtime).
4. **Earth naming** is a judgment call worth Will's eyeball in-game: the graft line is now
   "Flame Surge / Burning Bolts / Flame Arch / Fire Nova" (distinct from SV's
   "Rupture / Barrage / Flare"). If Will instead wants the graft line to BE the visible
   "Rupture" and SV's `drxflamesurge` line renamed, that requires touching an SV-original
   and is a separate, explicitly-authorized decision.
5. **Earth reflow** was designed to TQ's universal chain convention (base at bottom,
   modifiers stacking up, chains contiguous) but was NOT visually verified in-game (the
   build machine is owned by another workflow this session). Worth a screenshot check.
