# UBER_WEAPONS_AUDIT.md - Workstream U (DRX "supra" ultra-craftable set)

> Audit date: 2026-07-07. Authority = **Soulvizier 0.98i** upstream DB. Target =
> the built `work/SoulvizierClassic/Database/SoulvizierClassic.arz`. Resolution
> against the deployed `*.arc` + base-game arcs + `Text.arc`.
> Tooling: `scratch_audit/auditlib.py` + `scratch_audit/uber/u*.py` (read-only
> audit); fix implemented in `tools/apply_svc_patches.py` `_repair_supra_dead_refs`.

## What "uber/ultra craftable weapons" are in this mod

They are the DRX **"supra"** (supreme) tier: `records\drxitem\supra\*`. These are
the **red-name (`^r`) craftable uniques** Will remembers - each is made at the
Enchanter/Mystic from a **Mythic Formula** + 3 reagents. There are **25 distinct
craftable results** (10 weapons/shields, 9 armor pieces, 4 jewelry, 2 artifacts)
built by **49 `ItemArtifactFormula` records** (two folders: `recipes\` = 25,
`zrecipes\` = 24 - a full + a near-full duplicate set, both present in SV098 too).

The two items Will specifically recalls are both here and both craft end-to-end:
- **Blood Whisper** (`wep_spear.dbr`, `WeaponHunting_Spear`) - the bleeding spear:
  50% pierce ratio, 245-265 physical, **400 flat bleed over 3s**, plus a custom
  DRX crimson **weapon-trail** (`records\drxeffects\item\trail_wep_spear.dbr`) =
  the "blood-dripping" visual. All values byte-identical to SV 0.98i.
- **Paragon of Violence** (`neck_melee.dbr`, `ArmorJewelry_Amulet`) - the crafted
  red amulet. Byte-identical to SV 0.98i.

## TL;DR verdict

**The uber-craft feature is complete and faithful.** Every one of the 25
formula->result->fx chains resolves end-to-end: the formula exists, its recipe
name tag + formula visuals resolve, the RESULT item exists with resolving
mesh/skin/UI-bitmap, its item skills + procs + weapon-trail fx resolve, and
**all reagents across all 49 formulas resolve to real item records**. Every
result item's gameplay stats (damage, pierce, bleed, skills, procs) are
**byte-identical to SV 0.98i** (the only field diffs are (a) sound-path casing
that the port lowercased - functionally identical, and (b) `numRelicSlots=1`
which the mod deliberately adds to every supra item, a TQAE-era socketing
enhancement SV 0.98i predates).

**Port defects found: 0 (zero introduced by the port).** Every dead reference in
the supra set is **identical in SV 0.98i** (inherited DRX-author debt, not a port
regression).

**Objectively-dead references repaired (2 families, both with a valid existing
target): 24 references.** See "Fixes applied" below.

## Method

For every `ItemArtifactFormula` whose `artifactName` is a `records\drxitem\supra\*`
item, chase the whole chain:

- **Formula** - record exists; `description` (recipe name) tag resolves;
  `artifactFormulaBitmapName`/`baseTexture`/`mesh` resolve;
  `artifactBonusTableName` resolves.
- **Result** - `artifactName` resolves; `itemNameTag`/`itemText` resolve;
  `mesh`/`baseTexture`/`bitmap` resolve.
- **Result skills/procs/fx** - `itemSkillName`/`itemSkillAutoController`/
  `augmentSkillName*` resolve, and each of those skills' own fx/mesh/effect
  fields resolve. Every `*fx*`/`*effect*`/`weaponTrail`/`mesh` field on the
  result (the blood-drip visual hunt) resolves.
- **Reagents** - `reagent1/2/3BaseName` resolve to real item records (obtainable).
- **vs SV 0.98i** - full field-signature diff of every result; a diff that still
  fully resolves = intentional SVAERA change, never "fixed".

A reference is a **fixable defect** only when it resolves to NOTHING **and** the
obviously-intended target record exists (so the repair is unambiguous and cannot
trade one dead ref for another).

---

## Formula -> result -> fx chain table (all 25 craftables)

All rows: formula present (both `recipes\` + `zrecipes\`), recipe-name tag
resolves, result present, result name tag resolves, mesh/skin/bitmap resolve,
item-skill fx resolve, all 3 reagents resolve. `itemCostName` = **repaired** (was
the inherited stripped-separator dead ref; see Fixes).

| Result item | Class | Red name | Mythic Formula | Chain |
|-------------|-------|----------|----------------|:-----:|
| `wep_spear.dbr` | Hunting_Spear | **Blood Whisper** | Blood Whisper | OK (trail fx OK) |
| `wep_sword.dbr` | Melee_Sword | Shrike | Shrike | OK |
| `wep_dagger.dbr` | Melee_Sword | Crystal Tear of Nyx | Crystal Tear of Nyx | OK |
| `wep_axe.dbr` | Melee_Axe | Darkflame Devourer | Darkflame Devourer | OK |
| `wep_club.dbr` | Melee_Mace | Omega | Omega | OK |
| `wep_bow.dbr` | Hunting_Bow | Stormbringer | Stormbringer | OK |
| `wep_shield.dbr` | Armor_Shield | Agathodaemon | Agathodaemon | OK |
| `staff_ele.dbr` | Magical_Staff | Staff of the Cosmos | Staff of the Cosmos | OK |
| `staff_vit.dbr` | Magical_Staff | Soul Seekkor | Soul Seekkor | OK |
| `staff_dream.dbr` | Magical_Staff | Scepter of Kronos | Scepter of Kronos | OK |
| `ar_melee_helm.dbr` | Protective_Head | Titan Crest | Titan Crest | OK |
| `ar_melee_torso.dbr` | Protective_UpperBody | Ares Endless Assault | Ares Endless Assault | OK |
| `ar_melee_arms.dbr` | Protective_Forearm | Hephaestes' Gloves | Hephaestes' Gloves | OK |
| `ar_melee_legs.dbr` | Protective_LowerBody | Demonbone Greaves | Demonbone Greaves | OK |
| `ar_caster_helm.dbr` | Protective_Head | Cystalline Mask | Cystalline Mask | OK |
| `ar_caster_torso.dbr` | Protective_UpperBody | Ananke's Canvas | Ananke's Canvas | OK |
| `ar_caster_arms.dbr` | Protective_Forearm | Mercurial Gems | Mercurial Gems | OK |
| `ar_caster_legs.dbr` | Protective_LowerBody | Leggings of the Cosmos | Leggings of the Cosmos | OK |
| `ar_hunter_helm.dbr` | Protective_Head | Galefury | (labels as Cystalline Mask*) | OK (proc OK) |
| `neck_melee.dbr` | Jewelry_Amulet | **Paragon of Violence** | Paragon of Violence | OK (BMP†) |
| `neck_caster.dbr` | Jewelry_Amulet | Void Prism | Void Prism | OK (BMP†) |
| `ring_melee.dbr` | Jewelry_Ring | Band of the Elder Savage | Band of the Elder Savage | OK (BMP†) |
| `ring_caster.dbr` | Jewelry_Ring | Ananke's Ring | Ananke's Ring | OK (BMP†) |
| `artifact_mortoksskull.dbr` | ItemArtifact | (Mortok's Skull) | Mortok's Skull | OK |
| `artifact_plus2.dbr` | ItemArtifact | (The All-Seeing Eye) | The All-Seeing Eye | OK |

\* `ar_hunter_helm`'s `description` tag reuses the Cystalline Mask recipe-name
string (an inherited SV/DRX cosmetic label quirk - the formula record itself is
distinct and crafts the correct Galefury helm). Not a functional defect; matches
SV 0.98i.

† BMP = the item references an `*BMP.tex` **normal map** that does not exist in
any arc. This is identical in SV 0.98i and cosmetically inert (the engine skips
normal-mapping when the bump texture is absent - the item's base skin, mesh, and
UI bitmap all resolve and it renders + crafts correctly). **Deliberately left
unchanged** (see below).

### Blood Whisper (spear) - detail

| Field | Value | vs SV098 |
|-------|-------|:-------:|
| Class | `WeaponHunting_Spear` | = |
| name | `tagwep_spear` -> "^rBlood Whisper" | = |
| offensivePierceRatioMin | 50.0 | = |
| offensivePhysicalMin/Max | 245 / 265 | = |
| offensiveSlowBleedingMin | 400.0 | = |
| offensiveSlowBleedingDurationMin | 3.0 | = |
| mesh | `DRX\meshes\supra\wep_spear.msh` (OK) | = |
| **weaponTrail (blood-drip)** | `records\drxeffects\item\trail_wep_spear.dbr` (OK) | = |
| reagent1 | Peleus' Ashen Spear (u_l, OK) | = |
| reagent2 | Queen Zenobia's Spear (u_e, OK) | = |
| reagent3 | Ichthian melee spear (mi_l, OK) | = |
| itemCostName | **repaired** -> `records\game\itemcost_uniquelegendary_primary.dbr` | (SV also dead) |

### Paragon of Violence (amulet) - detail

Class `ArmorJewelry_Amulet`, `tagneck_melee` -> "^rParagon of Violence", all stats
byte-identical to SV098, `mesh`/`baseTexture`/`bitmap` resolve. Recipe "Mythic
Formula - Paragon of Violence" + reagents (Pendant of Immortal Rage u_l, Amulet of
Hygeia u_e, chrisamulet01) all resolve. `itemCostName` **repaired**; `*BMP.tex`
normal map deliberately preserved (see below).

---

## Fixes applied (SV-faithful dead-link repair)

Implemented in `tools/apply_svc_patches.py` as `_repair_supra_dead_refs(db)`
(exact-string, supra-scoped, idempotent), gated by the fail-loud
`_verify_no_supra_dead_refs(db)` invariant wired into `apply_all_extended_patches`
right after the Blood Toxeus wave. Neither fix changes any gameplay value, stat,
mesh, or SV-authored design - each only makes a dangling path resolve to the
record it obviously meant.

### Fix 1 - `itemCostName` stripped-separator (23 result items)

- **Before:** `recordsgameitemcost_uniquelegendary_primary.dbr` (no path
  separators -> resolves to nothing -> item falls back to a default buy/sell
  cost). Present on all 23 supra result items (every weapon/armor/jewelry;
  the 2 artifacts use the artifact cost path).
- **After:** `records\game\itemcost_uniquelegendary_primary.dbr` (the real
  base-game legendary-tier cost table; confirmed present in the .arz).
- **Evidence it is inherited, not a port defect:** the identical malformed string
  is in SV 0.98i for the same 23 records (the DRX source dropped the separators).
  It is the ONLY dead `itemCostName` in the entire 50k-record DB.

### Fix 2 - orphaned x-Galefury buff edge (1 reference)

- **Record:** `records\drxitem\supra\skills\xhunter_helm_galefury.dbr`
  (`Skill_BuffRadiusToggled`) - the xpack variant of the hunter-helm Galefury buff.
- **Before:** `buffSkillName = ...\hunter_helm_galefurybuff.dbr` (the NON-x buff,
  which does not exist).
- **After:** `...\xhunter_helm_galefurybuff.dbr` (the x-prefixed buff, which
  exists as `SkillBuff_Passive`).
- **Note:** the actual result item `ar_hunter_helm` uses the NON-x
  `hunter_helm_galefury` skill (a self-contained toggled buff with no
  `buffSkillName`), so the helm's own Galefury proc was never broken; this repair
  resolves the dangling edge on the orphaned x-variant so no dead skill ref
  remains in the supra set. Identical dead value in SV 0.98i.

### Deliberately NOT changed - `*BMP.tex` normal maps (10 references)

`neck_melee`, `neck_caster`, `ring_melee`, `ring_caster` each reference
`DRXtextures\items\supra\skins\<name>BMP.tex` in `bumpTexture` /
`armorMaleBumpTexture` / `armorFemaleBumpTexture`. **No such file exists in any
arc** (only the base `<name>.tex` skin does), so there is no valid target to point
at. These are byte-identical to SV 0.98i and cosmetically inert (missing normal
map = engine skips normal-mapping; item renders + crafts fine). Inventing a
texture would diverge from SV with no gameplay benefit, so they are preserved
as-is and documented here as inherited content debt.

---

## Gate results (Workstream U) - verified on the fixed rebuild

Fixed build: `SoulvizierClassic.arz` 54,528,917 B (baseline 54,528,890 B; +27 B
from the repaired path strings). All gates green:

**Build invariants (all three + validate_tags):**
- Build log: `Patch U: ... Total supra dead references repaired: 24 value(s) across
  24 record(s)`; `Soul-leak invariant OK`; `Soul-augment invariant OK`; no
  `SUPRA-REF OFFENDER`, no `MP-EQ OFFENDER`.
- `tools/validate_soul_augments.py` (fixed .arz): **PASS** - 50352 records, 2348
  souls, 4743 skill refs, **0 dangling**.
- `tools/validate_tags.py` (fixed .arz + Text.arc): **PASS** - 79 mod tags + 117
  authoritative tags all present.

**Fix verification (`scratch_audit/uber/u9_verify_fix.py`, fixed vs deployed):**
- G1 repaired: `itemCostName` repaired=23, still-dead=0; `galefurybuff`
  repaired=1, still-dead=0; both targets resolve. **PASS**
- G2 BMP preserved: 0 BMP fields changed. **PASS**
- G3 delta: record delta 0, string delta 0 (target string already existed).
- G4 no new danglers: dead .dbr refs 16422 (base) -> 16398 (fixed); **REMOVED 24,
  NEW introduced 0**. **PASS**
- G5 regression: spear/amulet/mastery/PC-tree fields byte-identical except the 2
  repaired. **PASS**
- Re-scan of fixed .arz (`u10`): itemCostName dead=0, galefurybuff dead=0,
  *BMP.tex dead=10 (preserved). **PASS**

**Determinism:** two independent fixed rebuilds are **byte-identical**
(md5 `4e1acb487b8e921ac874fd30e6666ae1`).

**Regression (`u11`, release build):** drop rates 66/25 with **no 100%**; Cold Worm
`tagD2Boss004` rename intact; SP Toxeus augments resolve; 0 drx mastery-tree
danglers. **ALL PASS**

**Summary:**
- Formula->result->fx chains audited: **25/25 complete**, all reagents resolve
  (49/49 formulas).
- Result stats vs SV 0.98i: **byte-identical** (only sound-casing + the
  deliberate `numRelicSlots=1` differ).
- Dead references: **0 introduced by the port**; **24 inherited-dead repaired**
  (Fix 1 x23 + Fix 2 x1); 10 inherited-dead BMP normal-maps deliberately preserved.
