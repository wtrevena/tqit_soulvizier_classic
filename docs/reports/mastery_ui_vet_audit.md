# Mastery / Skill-Tree UI Vet Audit (build40 golden arz)

**Author:** MASTERY UI AUDITOR, 2026-07-14. Branch `feat/mastery-ui-vet`.
**Subject:** build40 golden `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
(md5 `b33c5a44...`, 51,029 records) - the arz the next integration build ships against.
**Law source:** base-game `database.arz` (74,013 records, read-only) = vanilla ground truth.
**Method:** read-only replay with `tools/audit_mastery_ui.py` (committed) + `tools/build_text_arc.py`
text-pipeline dry-run. No game, no heavy build. Every count below is reproducible:
`py tools/audit_mastery_ui.py` (findings) and `py tools/audit_mastery_ui.py --table` (per-skill tables).

Will's mandate (2026-07-14, verbatim): **TIER LAW** - *"every skill is on the right level vertically
on the page based on how many points is needed for it"*; **CONNECTOR LAW** - *"the only skills that
should be connected together should be ones that genuinely augment one another"*; plus find + fix all
other imperfections across every mastery tree AND the mastery/skill select screens.

---

## 0. Executive summary + the ONE decision Will must make

| dimension | count | verdict |
|---|---:|---|
| TIER violations (row != skillTier) | 14 | real; concentrated in the b38 Earth reflow + graft skills |
| CONNECTOR - spurious drawn connector ([C]/[R] lands on non-relative) | 23 | the "wrong arrows" Will sees; 14 straight [C] + 9 side [R] |
| INTERLEAVE (crossed trees - foreign family trapped in a column) | 19 | underlying cause of the wrong arrows |
| OFF-COLUMN (modifier stranded in a different column from its base) | 9 | Spirit/Storm/Occult graft misplacements |
| GRID off-grid | 0 | clean |
| DUPLICATE cell (overlap) | 0 | clean |
| ICON broken/missing | 1 | `drxspellbreaker_spellshock2` dead-ref (known SV-original, b38-deferred) |
| DUPLICATE display-name (arz) | 0 | clean (Earth Rupture de-dup HELD) |
| Empty display-name | 0 | clean |
| SELECT-screen tag defects | 0 | Rogue-label bug FIXED + held; 0 sibling victims (text gate GREEN) |

**THE DECISION (single most important finding):** in the heavily-grafted masteries (Earth, Occult,
Spirit - and to a lesser degree Storm, Nature, Dream) **the TIER LAW and the CONNECTOR LAW are in
direct tension and cannot both be fully satisfied on the current 6-column grid.** The SVAERA/DRX
graft added extra skills - including *multiple modifiers of the same tier* for one base (e.g. Storm
`stormnimbus` has TWO tier-2 modifiers; Occult column 3 has two 2-node families that must occupy
tiers 3-6) - and only 6 columns exist. Strict `row == skillTier` (TIER LAW) then forces independent
families to interleave (violating the CONNECTOR LAW); de-interleaving forces skills off their tier row
(violating the TIER LAW). Vanilla never hit this because every mastery had exactly one family per
column region. **Will must choose the trade-off per mastery** (accept off-tier contiguity for readable
arrows, OR accept interleaved arrows for correct tiers, OR authorise relocating/dropping specific
graft skills so both laws hold). This audit gives the exact data + a recommended per-mastery layout,
but the choice is a design call and each fix touches Will's hand-tuned trees (Occult/Hunting are golden
+ every mastery needs his in-game screenshot per the standing UI-on-device rule), so the fixes are
delivered as an **exact spec** for the integration wave's implement->vet loop, not auto-shipped here.

---

## 1. CORRECTION to the derived invariants (important - future lanes rely on this)

`docs/reports/mastery_ui_invariants.md` (this branch, earlier commit) concluded the connector lines
are **baked into the per-mastery background art** and that `skillDependancy` is the only dependency
field. **Both are wrong.** Ground-truth field dumps of the base game prove:

- **The connector is a real skill-record field.** Every base/chain skill carries
  `skillConnectionOn` = `InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex`,
  `skillConnectionOff` = `...SkillBarBottomOff01.tex`, and `skillConnectionSpacing` = **62** (exactly
  one row pitch). 43 vanilla skills set it. The earlier probe missed it because it searched textures
  for the substring `connect` - the connector texture is named `SkillBar**Bottom**On`, not
  `skillbarconnect` (that 15x62 asset is the separate mastery-level *bar*).
- **Direction + placement (proven on the base game):** `skillConnectionOn` is set on the **base**
  skill (bottom of a chain, high Y) and the connector bar draws **upward** (toward lower Y) to the
  modifier(s) stacked directly above it in the same column. Modifiers themselves carry no connector.
  Example: Warfare `onslaught` (y403, tier1) has `skillConnectionOn`; `onslaught_ignorepain` sits at
  y341 directly above; the bar joins them. Not every base sets it (vanilla `rally`, `battleawareness`
  have modifiers but no connector), so **"missing connector" is NOT a defect signal by itself.**
- The mod (DRX) adds a **side variant** `skillbarbottomon01_right.tex` (`[R]` in the tables) for a
  modifier that connects diagonally to an adjacent column.
- `skillDependancy` is a gameplay prerequisite (points at hidden weapon skills), NOT the visual link -
  the earlier doc was right about that, wrong to then conclude the lines are baked art.

**Operative CONNECTOR LAW check (used here):** a skill whose `skillConnectionOn` is set draws a bar to
the nearest occupied cell in its connector's direction; that neighbour MUST be a genuine augment
relative (same `<base>_<suffix>` family, summon/pet-modifier family, or `skillDependancy` pair). A bar
landing on an unrelated skill = a wrong/crossed arrow (Will's complaint). The positional consequence:
each family must occupy a contiguous or gap-separated run in ONE column with no foreign skill trapped
between its members.

**GRID correction:** vanilla uses 6 rows (Y {403,341,279,217,155,93} = tiers 1-6). The **mod adds a
7th row Y=31 = tier 7** (`Y = 465 - 62*tier`, tier 7 -> 31) for grafted skills. The 6-column pitch
(X {128,228,328,428,528,628}) is unchanged. The TIER ladder the auditor uses is therefore
`{403:1, 341:2, 279:3, 217:4, 155:5, 93:6, 31:7}`.

`mastery_ui_invariants.md` has been amended in this commit to reflect all of the above.

---

## 2. TIER LAW audit (row must equal skillTier)

`skillMasteryLevelRequired` ("points needed") is NOT the row key: its bands **overlap** across tiers
(vanilla req=10 appears in tiers 2,3,4), so it cannot determine a row. `skillTier` IS the row key
(vanilla: `implied_tier(Y) == skillTier` holds 142/142, zero exceptions) and is the faithful reading
of "how many points is needed" - the tier band. So the TIER-LAW check is `row(Y) == skillTier`.

**14 violations** (skill placed on a row that disagrees with its own `skillTier`):

| mastery | skill | at row | skillTier | note |
|---|---|---:|---:|---|
| Earth | `drxrupture` | 3 | **1** | b38 reflow packed the chain contiguously; base belongs at row 1 |
| Earth | `drxrupture_burning` | 4 | **3** | b38 reflow |
| Earth | `drxspontaneouscombustion` | 6 | **5** | b38 reflow |
| Earth | `drx_firenova` | 7 | **6** | b38 reflow |
| Earth | `drxringofflame_softenmetal` | 2 | **3** | b38 reflow shifted it up one row |
| Storm | `drx_lightningdash` | 7 | **5** | graft placement |
| Storm | `drxfrostnova` | 5 | **6** | graft placement |
| Spirit | `drxdistortionwave_chaoticresonance` | 4 | **3** | graft placement |
| Spirit | `drxdistortionwave_psionicimmolation` | 6 | **5** | graft placement |
| Warfare | `drx_clubslam` | 7 | **2** | see caveat |
| Warfare | `drx_clubslam_fissure` | 4 | **7** | see caveat |
| Warfare | `drx_ancestralmod` | 2 | **7** | see caveat |
| Warfare | `drxhamstring` | 3 | **4** | graft placement |
| Defense | `drx_summonphalanx` | 5 | **7** | see caveat |

**Caveat - some `skillTier` values are themselves unreliable (graft).** The Warfare `clubslam` family
has a tier-2 base above tier-7 modifiers - structurally impossible in vanilla semantics (a modifier is
always >= its base's tier). So for `clubslam`/`fissure`/`ancestralmod`/`summonphalanx` the fix is NOT
"move to the skillTier row" (the tier field is wrong); Will/design must set the intended tier first.
For the Earth chain and the Storm/Spirit graft skills, `skillTier` is sensible and the *position* is
the error.

**The Earth 5-violation cluster is the shipped b38 reflow.** `tools/patches/mastery_ui_audit.py`
`_EARTH_REFLOW` deliberately packed Rupture `rupture(row3)->burning(row4)->flare(row5)` + standalones
`spontaneous(row6)/firenova(row7)` **contiguously** to satisfy Will's earlier ask ("the Rupture chain
should start lower"). That contiguity is exactly what breaks `row==skillTier` now. **This is the
clearest instance of the TIER-vs-earlier-ask tension and needs Will's reconciliation** (see section 0).

---

## 3. CONNECTOR LAW audit (drawn connectors must join genuine augments)

**23 spurious drawn connectors** - a skill's `skillConnectionOn` bar draws to a non-relative. These
are the "wrong arrows." 14 are straight `[C]` (high confidence - the bar draws straight up at the
nearest occupied cell, which is unrelated); 9 are side `[R]` (medium - the diagonal target is
unclear without a screenshot). The full list (from `audit_mastery_ui.py`):

**Straight `[C]` pointing up at an unrelated skill (high confidence wrong-arrow):**

| mastery | connector base | draws up to (unrelated) | root cause |
|---|---|---|---|
| Warfare | `drxonslaught_hamstring` | `drxwarhorn_doomhorn` | hamstring is OFF-COLUMN (col 628, base `onslaught` col 428) |
| Warfare | `drxbattlestandard` | `drx_clubslam_fissure` | grafted clubslam crammed into battlestandard's column |
| Defense | `drxadrenaline` | `drxquickrecovery` | quickrecovery parked inside adrenaline's chain span |
| Defense | `drxconcussiveblow` | `drxaxepassive` | axepassive trapped in concussiveblow's span |
| Earth | `drxstoneformbuffself` | `drxstoneform_moltenrock` | moltenrock is a stoneform (not stoneformbuffself) sibling; family split |
| Storm | `drxspellbreaker` | `drxfrostnova` | frostnova (own family) trapped in spellbreaker's column |
| Storm | `drxcoldaura` | `drxstormnimbus_heartoffrost` | heartoffrost is OFF-COLUMN (stormnimbus base col 128) |
| Occult* | `drx_scrap` | `drxpoisongasbomb` | scrap parked above the flashpowder chain |
| Occult* | `drx_summon_shadow_stalker` | `drx_petmodifier_greaterpower` | greaterpower sits above shadow_stalker |
| Occult* | `drxdarklings` | `drxopenwound` | **Will's reported Occult crossed-tree** (darklings/openwound interleave) |
| Hunting* | `drxtakedown_eviscerate` | `drxspear_tempest` | eviscerate carries [C] up at tempest (golden hand-tuned area) |
| Spirit | `drxenslavespirit` | `drxlifedrain_cascade` | lifedrain_cascade OFF-COLUMN |
| Spirit | `drxternion` | `drxsandsofsleep_troubleddreams` | ternion + sandsofsleep families interleaved in col 128 |
| Spirit | `drxskellysummons` | `drxlifedrain` | lifedrain parked above skellysummons |
| Spirit | `drxsandsofsleep` | `drxternion` | ternion trapped in sandsofsleep span |
| Spirit | `drxdistortionwave` | `drxspiritward` | col 328 is a 4-family pileup |
| Nature | `drxsprite_summons` | `drxrenewal` | renewal parked above sprite_summons |

(*golden-tracked mastery - Occult m5, Hunting m6.)

**Side `[R]` with no relative in the adjacent column (needs screenshot confirm):** Defense
`drxweaponpool_shieldsmash`, Defense `drxaxepassive`, Occult `drxlaytrap_rapidconstruction`, Occult
`drxlethalstrike`, Occult `drxdarklings_darkaperture`, Spirit `drxwraithlordsummons`. `[R]` implies a
diagonal connector to a base one column right; where that base is absent/left, the arrow reads wrong.

**19 interleaves** underlie these (a foreign family member trapped between two members of another
family in the same column). The worst is **Spirit column 328** (6 interleaves: `distortionwave`,
`deathchillaura`, `spiritward`, `outsidersummons` all pile into one column with `deathchillaura`'s
base stranded in col 228). Full interleave list in `audit_mastery_ui.py` output.

**9 off-column modifiers** (base present but in a different column - the arrow can never draw
correctly): Warfare `onslaught_hamstring`; Storm `stormnimbus_heartoffrost`, `spellbreaker_spellshock2`;
Occult `laytrap_petmodifier_multishotbolttrap`; Spirit `spiritward_spiritbane`,
`deathchillaura_ravagesoftime`, `deathchillaura_necrosis`, `lifedrain_cascade`,
`wraithlord_petmodifier_arcaneblast`.

---

## 4. Prior-fixes-HELD verification (Will's past fixed reports)

| prior fix | status in build40 | evidence |
|---|---|---|
| Earth "Rupture" appeared twice | **HELD** | `drxflamesurge`=tagRuptureNAME (the one Rupture), `drxrupture`=tagSkillName113 "Flame Surge", `drxrupture_flare`=tagSkillName103 "Flame Arch"; 0 duplicate display-names arz-wide |
| icon-less / misplaced-icon skills | **HELD** | all 8 b38 icon repoints resolve (clubslam_fissure->OnslaughtUp, activeblock->activeblock_up, firenova->firenova_up, rupture_burning->BarrageUp, rupture_flare->FlameArchUp, frostnova->FreezeUp, summoncopy->dreamimage_up, nymph_rootwave->SilvanNymphUp) |
| black skill-pane backgrounds | **HELD** | all 9 masteries point at `InGameUI\Skills\<Class>SkillBackground01.tex` (Dream->Spirit backdrop); no `SkillsPanel\skillbackgrounddiablo` left |
| Rogue-label on Occult select (B-MASTERY-LABEL-1) | **HELD** | text dry-run: duplicate-tag gate GREEN (0 conflicts), `tagMasteryBrief05`='Occult' (single def), `tagSkillName050`='Occult Mastery'; **0 sibling duplicate-tag victims** across all masteries |
| b40 Occult tree reflow | **NOT SHIPPED** | commit `ab55ca3` lives only on unmerged branch `feat/b40-occult-tree`; `hunting_occult_ui.py` in main has NO `_OCCULT_REFLOW`; **the Occult crossed-tree Will reported 2026-07-13 is STILL PRESENT in build40** (darklings/openwound interleave + scrap spurious connector, section 3) |

**The one prior "fix" that did not hold is the b40 Occult reflow - it was designed, committed, and
vetted GO on its branch but never merged into a build.** Re-landing it is a candidate P1, BUT the b40
design used contiguity (would introduce fresh TIER violations under the 2026-07-14 mandate), so it
should be re-derived to the TIER-vs-CONNECTOR decision in section 0, not ported verbatim.

Also still-open from b38 (correctly deferred, re-confirmed present): **Storm `drxspellbreaker_spellshock2`**
(UI slot 25 -> a skill record that has never existed in any source; SV-original dead reference). It
renders as a phantom/iconless button and shows as ICON + OFF-COLUMN + INTERLEAVE noise. Needs Will's
call: delete the button from `panectrl.dbr::tabSkillButtons` (+ the `skill25.dbr` record) or point it
at a real skill.

---

## 5. SELECT-MASTERY + TREE-pane screens

Wiring (verified against the gold arz): the mod does NOT override the base `masterypane.dbr` /
`mastery{N}text.dbr` records - it inherits them (they reference `tagMasteryBrief0N` for the select
label and `tagMasteryDescription0N` for the blurb) and renames masteries purely through **text-tag
overrides** in `modStrings.txt`. The per-mastery TREE-pane title/desc come from that mastery's
`panectrl.dbr` (`skillTabTitle` / `skillPaneDescriptionTag`).

- **Every mastery resolves to the correct name.** Warfare/Defense/Earth/Storm/Hunting/Spirit/Nature keep
  the base names; **Occult** is renamed from the base "Rogue/Stealth" via `tagMasteryBrief05`='Occult',
  `tagMasteryTitle05`='Occult Mastery', `tagSkillName050`='Occult Mastery', and the mod's own
  `tagOccultMasteryNAME`='Occult Mastery' (tree pane + `drxstealthmastery.skillDisplayName`).
- **The Rogue-label duplicate-tag bug is fixed and held** (section 4); the `check_duplicate_tags`
  fail-loud gate + `OCCULT_FIX_TAGS` single-definition block in `build_text_arc.py` prevent regression,
  and the assembled `modStrings.txt` has **zero conflicting duplicate tags** - so there are no sibling
  victims lurking on the other masteries.
- **Two minor flagged items (not defects, need Will's wording):**
  1. Occult's select-screen description `tagMasteryDescription05` is a *draft* ("The Occultist tempers
     an assassin's craft...") explicitly marked **needs Will's sign-off** in `build_text_arc.py`; and it
     differs from the tree-pane description `tagOccultTitleDESC` ("With cunning, agility, and dark
     trickery, the Occultist excels..."). Two different Occult blurbs on two surfaces - reconcile the copy.
  2. Spirit's tree-pane desc `tagSpiritDESC` reads "The Necromancer prefers to summon the undead..." -
     intentional mod flavor; confirm it matches the intended Spirit identity.

No missing icons, wrong panes, or mis-wired titles were found on the select or tree screens.

---

## 6. Per-mastery verdict (full per-skill tables: `py tools/audit_mastery_ui.py --table`)

| m | mastery | TIER | CONN | ILV | OFFCOL | headline defect |
|---|---|---:|---:|---:|---:|---|
| 1 | Warfare | 4 | 2 | 4 | 1 | grafted `clubslam` family crammed into `battlestandard`'s column 328; `onslaught_hamstring` stranded in col 628 |
| 2 | Defense | 1 | 4 | 3 | 0 | `quickrecovery`/`axepassive`/`summonphalanx` parked inside other families' spans |
| 3 | Earth | 5 | 1 | 0 | 0 | **b38 Rupture reflow now violates TIER LAW** (col 428 holds 4 families) |
| 4 | Storm | 2 | 2 | 3 | 2 | `stormnimbus` split across col 128 + 628 (two tier-2 mods); dead-ref `spellshock2`; `frostnova`/`lightningdash` off-tier |
| 5 | Occult **[GOLDEN]** | 0 | 6 | 2 | 1 | **Will-reported crossed trees** (col 328 darklings/openwound; col 128 flashpowder/scrap/multishot) - b40 fix never shipped |
| 6 | Hunting **[GOLDEN]** | 0 | 1 | 0 | 0 | `takedown_eviscerate` [C] points at `spear_tempest` (hand-tuned area) |
| 7 | Spirit | 2 | 6 | 6 | 5 | **worst tree** - col 328 is a 4-family pileup; `deathchillaura` base col 228 but both mods col 328; `lifedrain` mods off-column |
| 8 | Nature | 0 | 1 | 1 | 0 | `nymph_petmodifier_rootwave` parked in `briarward`'s column; `sprite_summons`->`renewal` |
| 9 | Dream | 0 | 0 | 1 | 0 | `distortionfield` trapped inside the `luciddream` chain (col 228) |

Cleanest: Hunting (golden, only the eviscerate [C]) and Dream (one interleave). Worst: **Spirit**, then
**Occult** (the reported one) and **Earth** (the shipped-reflow tension).

---

## 7. Prioritized FIX LIST (exact records + target values)

All edits are UI-button records `records\ingameui\player skills\mastery N\skillNN.dbr`
(`bitmapPositionX`/`bitmapPositionY`, dtype 0 INT) or the connector field `skillConnectionOn` on the
skill record - no skill VALUE/effect/dependency change. Masteries 5 (Occult) + 6 (Hunting) are
golden-tracked: any position/shape edit needs a matching `owner_approved_overrides` entry in
`tools/occult_hunting_golden.json` (deliberately, with justification). Every mastery needs Will's
in-game screenshot before promote (standing UI-on-device rule).

### P0 - Will's decision gate (blocks the layout fixes)
- **Reconcile TIER LAW vs CONNECTOR LAW per overcrowded mastery** (Earth/Occult/Spirit - section 0).
  Concretely, pick per mastery: (a) *tiers-strict* - every skill at `row==skillTier`, accept that same-
  tier families share rows and some arrows interleave; (b) *arrows-clean* - keep the b38/b40 contiguous
  packing, accept off-tier rows; or (c) *relocate/drop* specific graft skills so both hold. This audit
  recommends **(c) for Spirit** (it has genuine room once `deathchillaura`/`lifedrain` mods return to
  their base columns) and **(a) or a hybrid for Earth/Occult**. Nothing below can be finalised until
  this is chosen.

### P1 - reported + high-confidence wrong arrows
1. **Occult crossed trees (col 328 + col 128)** - re-derive the b40 reflow to the P0 decision.
   Target (tiers-strict, moves `openwound`+`anatomy` to free cells so `darklings`/`openwound` stop
   interleaving; requires the P0 column-budget choice): records `mastery 5\skill07.dbr` (openwound),
   `skill08.dbr` (anatomy), `skill25/26.dbr` (darklings/darkaperture), `skill09.dbr` (bladehoning),
   `skill12/13/14.dbr` (flashpowder chain), `skill21.dbr` (scrap), `skill18.dbr` (multishotbolttrap ->
   back to col 428 with its `laytrap` base). Golden waivers required. (The unmerged
   `feat/b40-occult-tree` `_OCCULT_REFLOW` is a ready starting point but is contiguity-based.)
2. **Spirit col 328 pileup** - return `deathchillaura` modifiers to their base column (228):
   `mastery 7\skill08.dbr` (`deathchillaura_necrosis`) and `skill07.dbr` (`deathchillaura_ravagesoftime`)
   -> col 228 at their tier rows (necrosis tier5 y155, ravagesoftime tier3 y279 - both free in col 228);
   return `spiritward_spiritbane` (`skill02.dbr`) to col 328 with base `spiritward`; keep the
   `distortionwave` chain alone in col 328. Fixes 3 OFFCOL + several interleaves + 2 spurious [C] at once.
3. **Spirit `lifedrain` family** - `lifedrain_cascade` (`mastery 7\skill12.dbr`) is in col 628 but base
   `lifedrain` is col 528; move it to col 528 at tier 3 (y279 - currently free there) so `enslavespirit`
   and `skellysummons` stop drawing [C] at stranded lifedrain nodes.
4. **Storm `stormnimbus_heartoffrost`** (`mastery 4\skill05.dbr`, col 628 y341) - base `stormnimbus`
   col 128. This is the "two tier-2 modifiers" case (P0): either move to col 128 (needs the P0 budget)
   or give it a proper `[R]` side-connector toward col 128 - a `skillConnectionOn` edit, not a move.

### P2 - off-tier graft skills (fix once P0 tier decision is set)
- Storm `drxfrostnova` (skillTier 6) `mastery 4\skill27.dbr` y155 -> y93; `drx_lightningdash` (tier 5)
  `skill26.dbr` y31 -> y155 - both currently blocked by column occupancy (P0).
- Spirit `distortionwave` modifiers `skill28/29.dbr` -> their skillTier rows once col 328 is thinned (P1.2).
- Earth Rupture chain `mastery 3\skill26/27/28/23/25/10.dbr` -> per the P0 Earth decision.

### P3 - needs Will's design/data input
- Warfare `clubslam`/`fissure`/`ancestralmod` + Defense `summonphalanx`: `skillTier` values are
  graft-inconsistent (tier-2 base above tier-7 mods). Set the intended tiers first, then place.
- Storm dead-ref `drxspellbreaker_spellshock2` (`mastery 4\skill25.dbr` + missing skill record): delete
  from `panectrl.dbr::tabSkillButtons` or repoint to a real skill.
- Occult select-description wording (`tagMasteryDescription05`) - Will's veto pending; reconcile with
  `tagOccultTitleDESC`.
- Nature `drx_nymph_petmodifier_rootwave` (Sylvan Protection) - parked in `briarward`'s column; its
  base is `sylvannymphsummons` (col 528) but the name doesn't prefix-match. Confirm intent, then either
  move to col 528 or leave as an intentional standalone.

---

## 8. Reproduce

```
py tools/audit_mastery_ui.py            # per-mastery findings + SUMMARY (TIER/CONN/INTERLEAVE/...)
py tools/audit_mastery_ui.py --table    # full per-skill tables (row, tier, req, connector, family, verdict)
# text-pipeline dry-run (Rogue-label + sibling duplicate-tag victims):
py -c "see scratchpad; build_text_arc.build_modstrings + check_duplicate_tags -> 0 conflicts"
```

**Confidence.** TIER, INTERLEAVE, OFF-COLUMN, ICON, DUP-NAME, and SELECT-screen findings are
empirically proven against the build40 arz + text dry-run (0-exception sweeps, cited counts). The
spurious-connector `[C]` findings are high-confidence (the bar's straight-up target is the nearest
occupied cell, and it is a non-relative), but the exact pixel rendering across gaps and the `[R]`
diagonal targets are not visually confirmable here (TQ is not runnable in this environment) - Will's
screenshot pass is the final check, per the standing UI-on-device rule. No fix is auto-shipped: the P0
TIER-vs-CONNECTOR decision is Will's, and every touched tree needs his eye.
