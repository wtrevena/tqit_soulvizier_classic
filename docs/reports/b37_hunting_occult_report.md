# B37 Hunting/Occult Improvement Wave - Implementer Report (round 1)

**Branch:** `feat/b37-hunting-occult` off `main` (32a4967) - **no push**
**Date:** 2026-07-12
**Scope bible:** `docs/HUNTING_IMPROVEMENT_SUGGESTIONS.md` + `docs/OCCULT_IMPROVEMENT_SUGGESTIONS.md` (both checker-verified) + Will's verbatim approvals.
**Status:** COMPLETE - full build green, all gates PASS, golden gate PASS with exactly this wave's waivers (negative-tested), every change verified in the built arz + Text.arc (27/27).

---

## What shipped (H1-H7)

All DB edits live in the registry-contract module **`tools/patches/hunting_occult_improvements.py`**
(`MODULE_NAME` + `apply(db, tags)`). Text (renamed/new/corrected descriptions) lives in
`build_text_arc.OCCULT_FIX_TAGS` (the golden-safe single-definition fix block). Golden drift is
waived per-field/tag in `tools/occult_hunting_golden.json` with justification
`Will-authorized H/O improvement wave 2026-07-12`.

### H1 - FIX EVERYTHING BROKEN
Every bug-class/broken-item the two docs graded as a defect (not the taste/BOLD redesigns):

- **Rapid Construction charm-resist artifact (Hunting S1).** `drxmonsterlure_rapidconstruction.dbr`
  carried `defensiveConvert = [-3.6 .. -19.8]`, byte-identical to its own `skillCooldownTime` ladder -
  the classic SV copy-paste defect that silently bled up to **-19.8% charm/conversion resistance** for
  investing in a cooldown modifier. **Zeroed** the array (encode-safe removal; the module asserts
  `defensiveConvert == skillCooldownTime` first and fails loud if that ever drifts). Cooldown + mana-cost
  reduction untouched.
- **Two "Eviscerate" nodes with blank tooltips (Hunting S2).** Both `drxspear_tempest` and
  `drxtakedown_eviscerate` set `skillDisplayName = tagSkillName090` and neither had a
  `skillBaseDescription` -> two adjacent panel nodes both labelled "Eviscerate", both tooltip-less. Fixed
  under H2/H3.
- **Two garbled Hunting descriptions (Hunting S3).** `tagSkillDescription171` (Scatter Shot Arrows) and
  `tagSkillDescription172` (Gouge) described a "Quillvine grove" energy aura and "Quillvines firing barbs"
  - SV authoring errors describing the wrong skill entirely. Rewritten under H3.
- **Nether Strike bow tooltip (Occult S5).** Fixed under H6.
- The two **inaccurate tooltips that hide synergies** are H6; the two **missing descriptions** are H2/H3.

**Completeness scan:** I enumerated every mastery-5 (Occult) and mastery-6 (Hunting) tree skill and
checked each `skillBaseDescription` resolves to non-empty text. **The only two skills mod-wide with a
missing/blank description are the two Eviscerate nodes** (both fixed). No other missing or
tag-undefined descriptions exist in either tree. The only inaccurate descriptions the docs enumerated
are 171/172 (both fixed).

### H2 - EVISCERATE DEDUP (with Will's square/circle detail)
The two same-named skills, disambiguated by the UI button `isCircular` flag (read from the built arz):

| Record | UI button | `isCircular` | Role | Result |
|---|---|:---:|---|---|
| `drxtakedown_eviscerate` | mastery 6 skill18 (428,341) | **0 = SQUARE** | 3-target/200deg spear bleed **cleave** = the attack | keeps **"Eviscerate"** (`tagSkillName090`); gained its missing description |
| `drxspear_tempest` | mastery 6 skill22 (428,279) | **1 = CIRCLE** | 300deg/12-target **fear+confuse+slow** spin, -66% damage = a control/debuff move ("more like a buff") | renamed **"Tempest"** (`tagSVCTempestNAME`); gained a description that reads as the control it is |

This matches Will's note exactly: the square-icon one is the attack (keeps the primary name), the
circle-icon one behaves like a buff, so its rename reads as the wide crowd-control spin it is. It also
resolves the spear column: **Take Down -> Eviscerate (bleed cleave) -> Tempest (CC spin) -> Flayer
(`drxtempest_expose`, the modifier that turns the spin into damage)**.

### H3 - DESCRIPTIONS (all missing + all inaccurate, both trees)
- New: `tagSVCTempestDESC` (the Tempest control spin) and `tagSVCEviscerateDESC` (the Eviscerate bleed
  cleave) - the two previously-blank tooltips.
- Rewritten: `tagSkillDescription171` Scatter Shot Arrows (fragmenting arrows + pierce + bleed, ^y(Bow))
  and `tagSkillDescription172` Gouge (barbed strike, deeper pierce + heavy bleed, ^y(Spear or Bow)) -
  no more "Quillvine grove."
- amgoz1 register (plain, grounded, weapon note in `^y(...)`), no em dashes.

### H4 - HUNTING MANA POOL (cap 160)
`drxhuntingmastery.dbr` `characterMana` `0` -> a 40-entry ladder `[4, 8, ..., 160]` (4 per mastery
level, **exactly 160 at ML40** - the same length convention as the bar's `characterLife`/`characterDexterity`
ladders). Small early value (4), no Intelligence added (Hunting stays pure DEX/STR), and the +100
mastery HP that pays for the 0-mana identity is deliberately left intact per the doc.

### H5 - DARKLINGS UPLIFT (Occult, Will-approved)
The pet boom skills are **not** golden-tracked (verified 0 hits in `occult_hunting_golden.json`), so (a)
and (c) needed no waiver; only `drxdarklings.petLimit` (b) is golden.

- **(a) blast/explosion damage** on `drx_petskill_boom.dbr` (the real `dyingSkill` payload, which had a
  life-drain DoT but **no burst**): added an `offensivePhysicalMin/Max` blast ladder scaling to
  **520-760** at tier 20, and boosted the existing life-drain DoT (`offensiveSlowLifeMin`, top 166 ->
  310). Mirrored onto `drx_petskill_boom_display` so the tooltip shows the real numbers. The chain-lightning
  synergy arcs the boom's damage, so it scales automatically.
- **(b) count to 4 at the top tier:** `petLimit [1..3]` -> `[..., 3, 3, 4, 4, 4, 4, 4]` (4 from L16, the
  base-tree max, through the L20 ultimate).
- **(c) petrify-on-death duration scales at high levels:** `offensivePetrifyMin` flat `1.0` -> a 20-entry
  ladder `1.0 (low tiers) .. 4.0` at tier 20 (mirrored on the display boom).

### H6 - TOOLTIP SYNERGY FIXES
- **Nether Strike works with bows.** `drxlethalstrike.dbr` sets `Bow = 1` (plus all melee) but
  `tagDRXlethalstrikeDESC` read `^y(All Melee Weapons)`, hiding the bow blink-shot. Corrected to
  `^y(All Melee Weapons or Bow)` (amgoz's body copy kept verbatim).
- **Dagger flags - verified a non-issue, intentionally unchanged.** Ground truth from the built arz:
  `Dagger = 1` is set by **zero** skills mod-wide - TQAE has no separate Dagger skill weapon-requirement
  field; daggers satisfy the `Sword` flag, which **both** Calculated Strike (`drxcalculatedstrike`:
  Sword/Axe/Spear) and its Blade Fury proc (`drxcalculatedstrike_luckyhit`: Sword/Axe) already set. Their
  tooltips already read `^y(Sword/Dagger/Axe...)`, so daggers already trigger them and the tooltip already
  advertises it - nothing is hidden and there is no flag to add. Changing accurate text (or adding a
  non-existent field) would be wrong, so it is left as-is. Nether Strike was the only genuinely hidden
  synergy.

**NETHER STRIKE TELEPORT ANSWER (Will's question):** **Yes - the player teleports.**
`drxlethalstrike` is class `Skill_AttackWeaponBlink`. The blink (a short-range teleport from the
attacker to the target, shown by its paired `drx_nether_strike_source_fx_pak` -> `..._target_fx_pak`
effects and the "speed through the shadow realm unseen" flavor) is intrinsic to the skill class, not to
the equipped weapon. The `Bow = 1` flag only makes the skill castable with a bow; when a bow Hunter
triggers it, the same blink fires - **the player is teleported to the target** and then strikes. It is a
genuine gap-closing blink-shot for bow builds, which is exactly the synergy the old "melee-only" tooltip
concealed. (In-game expectation: casting Nether Strike with a bow yanks you into melee range of the
target.)

### H7 - COORDINATION
This wave touches **skills + text only**. It does **not** touch any `ingameui` / panel / `panectrl`
records - the H/O UI-fix wave (panel backgrounds / button shapes / alignment, task #76) owns those, so
there is no collision. Confirmed: the golden gate reports `0 other` drift beyond this wave's waived
skill/text keys.

---

## Gates (all green)

| Gate | Result |
|---|---|
| Player-skill anim castability (Mastery W1) | PASS (46 tree skills; 1 inert modifier note) |
| Summon-pet render-chain (A9 + D5) | PASS (28 upstream WARN) |
| Container loot contract | PASS |
| Soul-summon-identity (F2) | OK (17 families) |
| contracts_summons (F2 lane) | OK - 13 contracts, 112 P2, **0 P0 / 0 P1** (all 112 P2 are pre-existing upstream MONSTER-MESH/MONSTER-SKILLS-LOOT on ported monsters, none from this wave) |
| **Golden freeze guard (arz-only, DB build)** | **PASS** - 11 waived, 0 other |
| Duplicate-tag gate (Text build) | OK - no conflicting definitions |
| **Golden freeze guard (arz + Text)** | **PASS** - 17 waived, **0 other** |
| **validate_tags** | **PASS** - all 263 referenced mod tags present |
| **Golden NEGATIVE test** (mandatory) | **PASS** - mutating an unrelated golden field (`drxstealthmastery::characterLife`) makes the gate FAIL LOUD (rc=1) while keeping all 17 legit waivers -> the gate is live, the waivers are scoped |
| Built-artifact verification (arz + Text) | **27/27** checks pass |

**Golden waivers added (12; 6 field + 6 tag), justification `Will-authorized H/O improvement wave 2026-07-12`:**
`field::...drxmonsterlure_rapidconstruction.dbr::defensiveConvert`,
`field::...drxspear_tempest.dbr::skillDisplayName`,
`field::...drxspear_tempest.dbr::skillBaseDescription`,
`field::...drxtakedown_eviscerate.dbr::skillBaseDescription`,
`field::...drxhuntingmastery.dbr::characterMana`,
`field::...drxdarklings.dbr::petLimit`,
`tag::tagSVCTempestNAME`, `tag::tagSVCTempestDESC`, `tag::tagSVCEviscerateDESC`,
`tag::tagSkillDescription171`, `tag::tagSkillDescription172`, `tag::tagDRXlethalstrikeDESC`.
(The 5 pre-existing F5 Flash Powder waivers are untouched.)

---

## Files changed (this wave owns only these)

- **`tools/patches/hunting_occult_improvements.py`** (new) - the H/O DB module (H1, H2, H4, H5), fail-loud.
- **`tools/apply_svc_patches.py`** - 2-line interim wiring: `from patches.hunting_occult_improvements import apply; apply(db, tags)` right after `_apply_flashpowder_rework`. **Registry reconciliation:** see below.
- **`tools/build_text_arc.py`** - 6 tags added to `OCCULT_FIX_TAGS` (H2/H3/H6 text), clearly blocked.
- **`tools/occult_hunting_golden.json`** - 12 `owner_approved_overrides` entries.
- Probes under `scratchpad/ho_probes/` (recon + smoke + negative + verification). `local/b37/` build outputs are gitignored.

---

## Coordination note: the patches registry landed during this wave

`feat/patches-registry` (task #74) completed while this was in flight. This module was written to its
contract (`MODULE_NAME` + `apply(db, tags)`) at the registry path on purpose, so the reconciliation at
integration is trivial and mechanical:

1. When `feat/patches-registry` is merged into this branch (or vice-versa), **remove the 2-line interim
   call** in `apply_svc_patches.py` (it is clearly commented `... until the registry ... lands`) and let
   the registry discover/run `tools/patches/hunting_occult_improvements.py`.
2. If the registry uses an explicit ordered manifest, add `hunting_occult_improvements` to it. The
   registry's "gates run last over everything" is compatible - this module makes no gate calls itself.
3. **Do not leave both the interim call and the registry active** - the module would apply twice; its
   fail-loud guards (they assert the pre-edit SV values) would then abort the build on the second pass,
   which is the intended safety net but not a shippable state.

I kept this branch self-contained + gate-green off `main` rather than merging the registry mid-flight
(which would have required a full rebuild + re-gate under the current heavy machine contention and risked
the verified state). The branch is a complete, buildable, gate-green deliverable; the registry merge is a
clean integration step.

## Build reproduction

```
# DB (SVC_RELEASE_DROPS default = tuned rates):
py tools/build_svc_database.py upstream/soulvizier_098i/Database/database.arz \
   upstream/soulvizier_0.9/Database/database.arz upstream/soulvizier_041/Database/database.arz \
   <out>/Database/SoulvizierClassic.arz "<TQAE>/Database/database.arz"
# Text:
py tools/build_text_arc.py upstream/soulvizier_098i/Resources/Text_EN.arc \
   <out>/Resources/Text.arc <out>/Database/uber_soul_tags.txt
```
Populate `<out>/../Resources` with hardlinks to `work/SoulvizierClassic/Resources/*.arc` first (A9) so
the render-chain + summons-contract gates run rather than skip.
