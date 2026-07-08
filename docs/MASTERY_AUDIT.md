# MASTERY_AUDIT.md - Workstream M (all 10 loaded masteries + 2 base DLC)

> Audit date: 2026-07-07. Authority = **Soulvizier 0.98i** upstream DB
> (`upstream/soulvizier_098i/Database/database.arz`). Target = the shipped/built
> `work/SoulvizierClassic/Database/SoulvizierClassic.arz`. Icons resolved against
> the deployed `work/SoulvizierClassic/Resources/*.arc` + base-game arcs; tags
> against the deployed `Text.arc` overlaid on base `Text_EN.arc`.
> Tooling: `scratch_audit/auditlib.py` + `scratch_audit/mastery/m*.py` (read-only).

## TL;DR verdict

**Zero port defects found. FIX-NEEDED = 0 across all 12 masteries.** Every
mastery skill (tree-listed AND every buff/pet/modifier/projectile reachable
through the skill graph - 682 skill-graph nodes total) has an icon that resolves
in a shipped arc, a display/description tag that resolves in Text.arc, and every
skill-wiring reference (`buffSkillName`/`petSkillName`/`spawnObjects`/
`skillDependancy`/projectile) resolves to a real record. Every mastery-panel UI
asset (panel backdrop, skill bar, mastery-tab button) resolves.

The icons/classifications Will remembered as "wrong" were **already corrected by
prior campaigns** and are healthy in the current build. The evidence tables below
document that state and separate the (few) shipped-vs-SV differences into their
two legitimate causes:

1. **SVAERA-era port fixes** - `fix_broken_mastery_skills` copies a delegating
   skill's display (icon/name/desc) from its `buffSkillName`/`petSkillName` child
   onto the skill record itself, because AE reads display from the record for
   non-delegating classes. This is why a skill can show a direct icon where SV
   0.98i left the field blank and delegated. In **every** such case the injected
   value **equals** SV's effective (chain-resolved) display, so it is faithful.
2. **Deliberate legacy-skill restorations** (`restore_legacy_skills`, Patch 11) -
   documented content changes that add SV 0.4.1-era skills and swap two Nature
   skills. All added/changed records carry fully-resolving icons + tags.

## Method (how "faithful" was decided)

For each mastery the game actually loads (from `xpack\creatures\pc\malepc01.dbr`
+ `femalepc01.dbr` `skillTree1..12`), for every skill in the tree and every skill
reachable from it:

- **(a) ICON** - `skillUpBitmapName`/`skillDownBitmapName`, resolved as the engine
  does: first path component = archive name, looked up across mod + base arcs.
  Compared against SV's **effective** icon (record, else one/two hops through
  `buffSkillName`/`petSkillName`).
- **(b) CLASSIFICATION / PLACEMENT** - `skillTier`, `skillMasteryLevelRequired`,
  `skillUltimateLevel`, and the UI-panel slot position (`bitmapPositionX/Y`,
  `isCircular`) from `records\ingameui\player skills\mastery N\skillNN.dbr`. The
  UI-panel number for each tree was derived **empirically** (which panel's slots
  reference that tree's skills) for both BUILT and SV, and required to agree.
- **(c) TAGS** - `skillDisplayName`/`skillBaseDescription` resolve in `Text.arc`.
- **(d) REFS** - `buffSkillName`/`petSkillName`/`petBurstSpawn`/`spawnObjects`/
  `skillDependancy`/projectile refs resolve to a real record (BUILT or BASE).
- **(e) TREE / PANEL** - tree membership + order, and every panel UI asset.

A row is a **PORT DEFECT (fixable)** only when something is OBJECTIVELY DEAD (icon
resolves in no arc / tag absent from Text.arc / ref resolves to nothing). A row
that merely DIFFERS from SV but fully resolves is an intentional SVAERA change and
is reported as informational, never "fixed".

### Protected trees (Will's rule)
**Occult (slot 5 / stealth) and Hunting (slot 6)** contain Will's deliberate
hand-tuning. Their shipped-vs-SV differences are presumed INTENTIONAL and are
listed as **informational only ("Will's hand-tuning - preserved")**. Only
objectively-dead references would be fixable there - and there are none.

---

## Mastery-to-slot map (authoritative wiring)

Loaded from `records\xpack\creatures\pc\{male,female}pc01.dbr`. Note the UI-panel
numbers are NOT in slot order (this matches SV 0.98i - Nature and Spirit are
swapped between panels 7/8 in both):

| PC slot | Mastery | Canonical SkillTree (BUILT) | UI panel | Source |
|--------:|---------|------------------------------|:-------:|--------|
| 1  | Warfare    | `records\skills\warfare\drxwarfareskilltree.dbr`       | 1 | mod (SV DRX) |
| 2  | Defense    | `records\skills\defensive\drxdefensiveskilltree.dbr`   | 2 | mod (SV DRX) |
| 3  | Earth      | `records\skills\earth\drxearthskilltree.dbr`           | 3 | mod (SV DRX) |
| 4  | Storm      | `records\skills\storm\drxstormskilltree.dbr`           | 4 | mod (SV DRX) |
| 5  | **Occult** | `records\skills\stealth\drxstealthskilltree.dbr`       | 5 | **PROTECTED** |
| 6  | **Hunting**| `records\skills\hunting\drxhuntingskilltree.dbr`       | 6 | **PROTECTED** |
| 7  | Nature     | `records\skills\nature\drxnatureskilltree.dbr`         | 8 | mod (SV DRX) |
| 8  | Spirit     | `records\skills\spirit\drxspiritskilltree.dbr`         | 7 | mod (SV DRX) |
| 9  | (Quest Reward - not a mastery) | `records\quests\rewards\questrewardskilltree.dbr` | - | base |
| 10 | Dream      | `records\xpack\skills\dream\drxdreamskilltree.dbr`     | base xpack | mod (SV DRX) |
| 11 | RuneMaster | `Records\XPack2\skills\RuneMaster\RuneMaster_SkillTree.dbr` | base xpack2 | base DLC |
| 12 | Neidan     | `records\XPack4\Skills\Neidan\neidanskilltree.dbr`     | base xpack4 | base DLC |

Occult's `Skill_Mastery` display name is `tagOccultMasteryNAME` (SV renamed the
vanilla Rogue/Stealth mastery to "Occult"), confirming slot 5 = Occult.

---

## Per-mastery PASS/FIXED tables

Legend: **icon/tag** columns = does the shipped value resolve (Y). **vsSV** =
difference from the SV 0.98i authority (empty = identical effective value).
**verdict**: PASS = matches SV + all resolves; DIFF/ADDED = intentional SVAERA
change (all assets resolve); PRESERVED = protected-tree hand-tuning kept.

### SLOT 1 - Warfare  [MOD]  (BUILT 26 / SV 25)  -> **PASS=25, ADDED=1, FIX=0**

25 SV skills: all icons resolve, all tags resolve, tiers/positions match SV. 1
added record:

| idx | skill | icon | tag | vsSV | verdict |
|----:|-------|:----:|:---:|------|---------|
| 26 | `drxhamstring.dbr` | Y | Y (`tagSkillName011` "Hamstring") | ADDED | ADDED (Patch 11.D legacy restore) |

`drxhamstring.dbr` = `Skill_Modifier`, icon `InGameUI\Icons\Skills\Warfare\HamstringUp01.tex`
(InGameUI.arc), `skillDependancy -> drxonslaught_ignorepain.dbr` (resolves).

### SLOT 2 - Defense  [MOD]  (BUILT 25 / SV 25)  -> **PASS=25, FIX=0**
All 25 skills PASS - every icon/tag/ref resolves and matches SV effective display.

### SLOT 3 - Earth  [MOD]  (BUILT 25 / SV 25)  -> **PASS=25, FIX=0**
All 25 skills PASS.

### SLOT 4 - Storm  [MOD]  (BUILT 25 / SV 25)  -> **PASS=25, FIX=0**
All 25 skills PASS.

### SLOT 5 - Occult  [PROTECTED - Will's hand-tuning, preserved]  (BUILT 27 / SV 25)
**PASS=25, PRESERVED=2 (added Darklings), FIX=0.** SV-diffs informational only.

| idx | skill | icon | tag | vsSV | note (preserved) |
|----:|-------|:----:|:---:|------|------|
| 26 | `drxdarklings.dbr` | Y | Y (`tagirregulardemonNAME` "Darklings") | ADDED | Patch 11.A restore; `Skill_AttackProjectileSpawnPet`, 20 shadow-demon pets + projectile all resolve |
| 27 | `drxdarklings_darkaperture.dbr` | Y | Y (`tagDarkApertureNAME` "Dark Aperture") | ADDED | Patch 11.A modifier; icons `DRXtextures\skill icons\stealth\breach*.tex` resolve |

Informational description fills (added by `MOD_DESC_FIX_TAGS`, both resolve):
`drxlaytrap.dbr` (Breach) `skillBaseDescription = tagbreachDESC`;
`drxlaytrap_rapidconstruction.dbr` `skillBaseDescription = tagNewSkill321DESC`.
No values, tiers, positions, classifications, or icons in the Occult tree were
changed by this audit.

### SLOT 6 - Hunting  [PROTECTED - Will's hand-tuning, preserved]  (BUILT 25 / SV 25)
**PASS=25, FIX=0.** No shipped-vs-SV differences detected at all; every icon/tag/
ref resolves. Nothing changed by this audit.

### SLOT 7 - Nature  [MOD]  (BUILT 25 / SV 25)  -> **PASS=23, DIFF=2 (intentional), FIX=0**

Two skills intentionally reworked by Patch 11.B (Elemental Flurry->Thorn Sprites,
Dissemination->Fabrical Tear). Both BUILT icons + tags resolve; kept as intended:

| idx | skill | BUILT icon (resolves) | BUILT name tag | SV had | verdict |
|----:|-------|-----------------------|----------------|--------|---------|
| 23 | `drxsprite_summons.dbr` | `DRXtextures\skill icons\nature\spriteup.tex` | `tagThornSpritesNAME` "Thorn Sprites" | `summonmaenadarcherup.tex` / `tagNewSkill335` | DIFF (Patch 11.B, intentional) |
| 24 | `drxrenewal.dbr` | `DRXtextures\skill icons\nature\sprite_synergyup.tex` | `tagFabricalDischargeNAME` "Fabrical Tear" | `DisseminationUp01.tex` / `tagSkillName073` | DIFF (Patch 11.B, intentional); `skillUltimateLevel` 16->12 |

Other 23 Nature skills PASS.

### SLOT 8 - Spirit  [MOD]  (BUILT 30 / SV 25)  -> **PASS=25, ADDED=5, FIX=0**

5 Dream-mastery skills grafted into Spirit by Patch 11.C. All icons + tags resolve:

| idx | skill | icon | name tag | verdict |
|----:|-------|:----:|----------|---------|
| 26 | `drxsandsofsleep.dbr` | Y | `xtagSkillDreamName015` "Sands of Sleep" | ADDED (11.C) |
| 27 | `drxsandsofsleep_troubleddreams.dbr` | Y | `tagTroubledDreamsNAME` "Troubled Dreams" | ADDED (11.C) |
| 28 | `drxdistortionwave.dbr` | Y | `xtagSkillDreamName004` "Distortion Wave" | ADDED (11.C) |
| 29 | `drxdistortionwave_chaoticresonance.dbr` | Y | `xtagSkillDreamName005` "Chaotic Resonance" | ADDED (11.C) |
| 30 | `drxdistortionwave_psionicimmolation.dbr` | Y | `xtagSkillDreamName018` "Psionic Immolation" | ADDED (11.C) |

Other 25 Spirit skills PASS.

### SLOT 10 - Dream  [MOD]  (BUILT 25 / SV 25)  -> **PASS=25, FIX=0**
All 25 skills PASS. Dream has no `mastery N` ingameui panel (it is an Immortal
Throne mastery); its mastery-tab button `drxdreammastery.dbr` uses
`XPack\UI\Skills\DreamMasteryBtnUp01.tex` (UI.arc, resolves).

### SLOT 11 - RuneMaster  [BASE DLC]  (25 skills, from base game)
Referenced by the PC records but the tree + all skills live in the base-game DB
(`Records\XPack2\...`). Not SV-authored; the mod does not modify it. All 25 tree
entries + icons resolve from base. Structurally sound (informational - out of the
SV-faithful scope).

### SLOT 12 - Neidan  [BASE DLC]  (28 skills, from base game)
Same as RuneMaster: base-game DLC (`records\XPack4\...`), unmodified by the mod,
all 28 entries + icons resolve. Informational.

---

## OCCULT / HUNTING dead-ref fixes

Per Will's protection rule, the only fixable items in the Occult and Hunting trees
are references that are OBJECTIVELY DEAD (resolve to nothing in arz+arcs+Text).

**NONE FOUND.** Every icon, tag, and skill-wiring reference in both the Occult
(slot 5) and Hunting (slot 6) trees - across their full transitive skill graphs
(86 and 52 nodes respectively) - resolves. No changes were made to either tree.

---

## Gate results (Workstream M)

- **Tree-listed skill resolution:** 0 dangling `skillNameN` entries across all 12
  trees (Warfare 26, Defense 25, Earth 25, Storm 25, Occult 27, Hunting 25,
  Nature 25, Spirit 30, Dream 25, RuneMaster 25, Neidan 28).
- **Full transitive skill graph:** 682 reachable skill-type nodes; **0 dead
  icons, 0 dead tags, 0 dead skill-wiring edges** (buff/pet/modifier/projectile/
  dependancy). (283 dead refs initially reported were 100% pet/summon
  `loot*Item*` equipment refs on summoned CREATURE records - out of mastery-skill
  scope and gated by the souls workstream; every actual skill-graph edge resolves.)
- **Mod-created legacy-restore records (8):** all icons + tags + spawn/dependancy/
  projectile refs resolve (see SLOT 1/5/8 tables).
- **Mastery panel UI chrome:** every `masterybitmap`/`masterybar`/mastery-tab
  button texture resolves for all 8 classic panels + Dream.
- **UI-panel binding vs SV:** all 8 classic + Occult match SV's tree->panel
  mapping exactly (Nature->8, Spirit->7 as in SV).

**No mastery changes were made to the build.** Workstream M found zero port
defects, so no code was changed for it. The only build change in this session is
the Workstream-U supra dead-ref repair (`_repair_supra_dead_refs`), which does not
touch any skill/mastery record; the fixed-build regression confirms 0 drx
mastery-tree danglers and byte-identical mastery skill fields. The three build
invariants (soul leaks / soul augments / tags) and `validate_tags` are green on
the fixed build.
