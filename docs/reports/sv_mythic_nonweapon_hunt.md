# SV MYTHIC NON-WEAPON HUNT (2026-07-15)

> Read-only recon. Method: decoded `.arz` record tables + field data directly with
> `tools/arz_patcher.py` (`ArzDatabase.from_arz` / `get_fields`) and `.arc` text archives with
> `tools/arc_patcher.py` (`ArcArchive.get_text`) - no raw `grep` on compressed binaries. Five
> database sources loaded in full: `soulvizier_098i` (51,186 records), `soulvizier_0.9` (48,722),
> `soulvizier_041` (46,443), the live **SVAERA** Workshop install `2076433374\SVAERA_customquest`
> (110,495 records), and our built `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
> (51,023, "OURS"). Three Text sources decoded for display-name resolution: SV 0.98i's
> `Resources/Text_EN.arc` (14,657 tags), SVAERA's `Resources/Text.arc` (27,524 tags), and our
> built `Resources/Text.arc` (4,431 tags). **Note:** `soulvizier_0.9` and `soulvizier_041` ship
> **no** `Resources/Text_EN.arc` at all (Database-only upstream snapshots) - display-name search
> for those two sources is necessarily record-name/`FileDescription`-only.

## TL;DR

| Hunt | Verdict |
|---|---|
| (1) Paragon of Violence | **FOUND, and already shipping in our build.** Amulet, `records\drxitem\supra\neck_melee.dbr`, `itemClassification=Legendary`, DRX "supra" (Mythic Formula) craftable. |
| (2) Mythic straw/storm hat | **FOUND, and already shipping in our build.** Head armor, `records\drxitem\supra\ar_hunter_helm.dbr` ("Galefury"), `itemClassification=Legendary`, `defensiveProtection=400.0`, oriental-villager conical-hat mesh, grants a toggled storm-nimbus aura. Also DRX "supra" (Mythic Formula) craftable. |
| (3) Other mythic non-weapon gaps | **A real, already-partially-scoped vein exists in SVAERA**, not in the DRX "supra" tier (that tier is 100% complete/0-gap - see below) but in SVAERA's own ~30k-record additive layer: 5 item-**set** groupings entirely absent (member items already present as standalone uniques) + a curated bundle of ~10+ Greek/Egyptian Legendary amulets/rings gated by an art-archive lever. Independently re-verified below; matches the existing `docs/BACKLOG.md` SVAERA-ADOPT recon and `docs/reports/svaera_goodies_audit.md`. |

Will's memory is **not** from a different mod - both items he named are real, both are in the
**DRX "supra"** tier (the `records\drxitem\supra\*` "red-name" Mythic-Formula-craftable set
documented in `docs/UBER_WEAPONS_AUDIT.md`), and both are **already live in the shipped build**.

---

## Hunt 1: "Paragon of Violence" (mythic craftable amulet)

### Search performed

- Record **names** containing `paragon` (case-insensitive) across all 5 `.arz` sources: **0 hits
  everywhere** (the record itself is filed under a generic path, not a "paragon"-named file).
- `FileDescription` field (the artist/editor-only plain-text comment, independent of the
  localized tag) containing `paragon`: **0 hits in 098i/0.9/041/OURS, 2 hits in SVAERA**:
  - `records\item\formulas\forged\my_amu_001_formula.dbr` -> `"Mythic Formula - Melee - Paragon of Violence"`
  - `records\item\formulaitems\amulet\my_amu_001.dbr` -> `"Melee - Paragon of Violence"`
  (SVAERA's own re-templated duplicate of the same conceptual item under a different path -
  see "SVAERA re-templates everything" note below.)
- Text **tag values** containing `paragon` across all 3 decoded Text sources: **2 hits each** in
  098i, SVAERA, and OURS - identical in all three:
  - `tagneck_melee = ^rParagon of Violence`
  - `tagRecipe_neck_melee = ^rMythic Formula - Paragon of Violence`

The tag being present verbatim in **098i's own upstream Text_EN.arc** proves this is original SV
0.98i content (DRX-authored), not a SVAERA invention.

### Ground truth (decoded directly from `work/SoulvizierClassic/Database/SoulvizierClassic.arz`)

| Field | Value |
|---|---|
| Record | `records\drxitem\supra\neck_melee.dbr` |
| Class / item slot | `ArmorJewelry_Amulet` (neck) |
| `itemNameTag` | `tagneck_melee` -> **"^rParagon of Violence"** (red-name unique) |
| `itemClassification` | **Legendary** |
| `itemLevel` / `levelRequirement` | 65 / 65 |
| `mesh` | `DRX\meshes\supra\neck_melee.msh` |
| `augmentAllLevel` | 2 |
| `numRelicSlots` | 1 (TQAE-era socket the mod adds to every supra item) |

**Is there a formula?** Yes - two: `records\drxitem\supra\recipes\neck_melee_formula.dbr` and its
duplicate `zrecipes\neck_melee_formula.dbr`, both `Class=ItemArtifactFormula`,
`artifactName -> records\drxitem\supra\neck_melee.dbr`, `description -> tagRecipe_neck_melee`
("^rMythic Formula - Paragon of Violence"). The formula is also placed as a lootable drop entry
(`records\xpack\item\loottables\arcaneformulae\supra.dbr` / `supra_special.dbr`, `lootName11`).

**Present in ours?** **Yes**, confirmed directly in the built `.arz` (record, name tag, and both
formula copies all present and resolving). This matches the existing audit in
`docs/UBER_WEAPONS_AUDIT.md` ("Paragon of Violence (amulet) - detail", 2026-07-07): craftable
end-to-end, stats byte-identical to SV 0.98i, only the (harmless, inherited, SV-098i-identical)
`*BMP.tex` normal-map reference and the deliberate `numRelicSlots=1` addition differ.

**Verdict: FOUND. Present and fully functional in the shipped mod.** Will's memory is accurate;
it's just filed as `neck_melee.dbr`, not a record literally named "paragon".

---

## Hunt 2: mythic straw/storm hat (large round hat, storm aura, ~400 armor)

### Search method

Enumerated every record whose **record type** (the `.dbr`'s `Class` line) contains `head` AND
(`armor` or `protective`) across all 5 sources - 470 (098i) / 462 (0.9) / 451 (041) / 1,561
(SVAERA, because it also carries the xpack2/3/4 Norse/Chinese/Egyptian-DLC rosters) / 476 (OURS)
head-armor records - then filtered for: `itemClassification` in {Legendary, Epic}, a granted
`itemSkillName`/`itemSkillAutoController` whose path or resolved skill record contains a
storm/lightning/nimbus/tempest word, or a mesh/`FileDescription`/name containing
straw/coolie/paddy/conical/sombrero.

### The match

**`records\drxitem\supra\ar_hunter_helm.dbr`** ("Galefury"), present in **all 5 sources**
(098i/0.9/041/SVAERA/OURS - it is original SV 0.98i DRX content, like Paragon):

| Field | Value |
|---|---|
| Class | `ArmorProtective_Head` |
| `itemClassification` | **Legendary** |
| `defensiveProtection` | **400.0** - matches Will's "~400 armor" memory almost exactly |
| `mesh` (male) | `Creatures\npc\neworient\props\ortvillagerm_hat04.msh` |
| `armorFemaleMesh` | `Creatures\npc\neworient\props\ortvillagerf_hat01.msh` |
| `itemNameTag` | `tagar_hunter_helm` -> "Galefury" |
| `itemSkillName` | `records\drxitem\supra\skills\hunter_helm_galefury.dbr` |
| `itemSkillAutoController` | `hunter_helm_autocast.dbr` (`triggerType=OnEquip`, `chanceToRun=100`, `targetType=Self` - i.e. **always-on while worn**) |

The mesh path `Creatures\npc\neworient\props\ortvillagerm_hat04.msh` is a prop from the "New
Orient" (Chinese/East-Asian countryside) NPC set - confirmed by cross-reference: the only other
record in the built `.arz` referencing the sibling `OrtVillagerF_A.tex` texture is
`records\creature\npc\speaking\orient\greatwall_villager2.dbr` (a Great Wall villager NPC). These
"villager hat" props are the peasant/farmer conical hats worn by that NPC family - i.e. exactly
the **large round (conical/coolie-style) straw-farmer hat** silhouette Will remembers, repurposed
by DRX as a craftable helm mesh. No 3D viewer was available to render it, but the mesh's origin
(rural East-Asian villager prop, "round hat" naming pattern `_hat01`/`_hat04`) is strong
corroborating evidence.

The granted skill, `hunter_helm_galefury.dbr` (`Class=Skill_BuffAttackRadiusToggled` - a **toggled
AoE proc aura**, `skillTargetRadius=8` around the player), is exactly the "storm around you"
mechanic Will described:

| Field | Value |
|---|---|
| `skillActivatedAuraName` | `records\drxeffects\item\hunter_helm_galefury_fx.dbr` (the visible aura VFX while toggled on) |
| `offensiveLightningMin` / `offensiveLightningChance` | 188.0 / 7.0% |
| `offensiveColdMin` | 45.0 |
| `offensiveFumbleMin` / `offensiveSlowRunSpeedMin` | 36.0 / 22.0 (debuffs on nearby enemies) |
| `skillHitSound` | `records\sounds\soundpak\spells\storm\chainlightningthitpak.dbr` - **literally the game's own "storm" sound-bank folder** |
| `skillUpBitmapName` / `skillDownBitmapName` | `DRXtextures\items\supra\ar_hunter_helm_stormicon.tex` - **the skill icon's own filename is "stormicon"** |
| `skillDisplayName` | `tagGalefurySkillNAME` |

**Craftable?** Yes, same Mythic-Formula supra mechanism as Paragon:
`records\drxitem\supra\recipes\ar_hunter_helm_formula.dbr` (`ItemArtifactFormula`,
`artifactName -> ar_hunter_helm.dbr`), also placed as a formula drop
(`arcaneformulae\supra.dbr`/`supra_special.dbr`, `lootName24`/`lootName25`).

**Present in ours?** **Yes**, confirmed directly in the built `.arz` - full record dump above is
from `work/SoulvizierClassic/Database/SoulvizierClassic.arz` itself.

### Note - SVAERA ships its own rebalanced parallel copy

SVAERA additionally carries `records\item\formulaitems\head\my_head_002.dbr`
(`FileDescription="Hunter - Galefury"`, same `itemNameTag=tagar_hunter_helm`, same mesh) but
**re-tuned**: `defensiveProtection` pumped to **772.0** and the granted skill swapped to
`records\all_sv\skills\item\aura\bart_stormsoul.dbr` (an even more literally-named "storm soul"
aura). This is SVAERA's documented pattern of re-templating/rebalancing nearly every shared
record (see `docs/BACKLOG.md` SVAERA-ADOPT note: "SVAERA re-templated + rebalanced ~every common
record... the 'Steam fork with nerfs/buffs'"), not a distinct item - our build correctly keeps the
SV-0.98i-faithful 400-armor version, not SVAERA's power-crept 772-armor one.

One other head item surfaced by the storm-skill filter but ruled out as **not** Will's item:
`records\xpack\item\equipmentarmor\helm\um_n_001.dbr` ("Wizard Hat", present in all sources incl.
ours) grants a plain `Lightning.dbr` proc, but it is **Epic**-tier at only **72 armor** - far short
of "~400 armor" and not straw/round-hat-shaped (a pointy wizard hat mesh). Not a match.

**Verdict: FOUND. Present and fully functional in the shipped mod as "Galefury".** This is almost
certainly the item Will remembers - the 400 armor figure, the always-on storm/lightning aura, the
craftable-uber status, and the round countryside-hat mesh all line up. If Will specifically
recalls a *literal* "straw hat" cosmetic label (vs. "Galefury"), that is a naming/flavor-text
question, not a content-gap - the item, stats, mesh, and mechanic all already exist and ship.

---

## Hunt 3: other mythic-tier non-weapon items present upstream/SVAERA but absent from ours

### The DRX "supra" tier itself: zero gaps

The `records\drxitem\supra\*` Mythic-Formula tier (10 weapons/shields, **9 armor pieces**, **4
jewelry**, 2 artifacts = 25 craftable results total) is the actual "mythic craftable" system Will
is remembering. Independently re-confirmed by this hunt (all 9 armor + 4 jewelry supra items
enumerated by the head/jewelry scans above are present in `OURS` with matching
`itemNameTag`s: `ar_hunter_helm`, `ar_caster_helm`, `ar_melee_helm`, `neck_melee`, plus the
already-audited `neck_caster`/`ring_melee`/`ring_caster`/torso/arms/legs pairs) - this matches
`docs/UBER_WEAPONS_AUDIT.md`'s conclusion of **25/25 formula->result->fx chains complete**, so
there is no supra-tier non-weapon gap to report.

### The real gap: SVAERA's own additive Legendary jewelry/armor roster

Filtering every `ArmorJewelry_Amulet`/`ArmorJewelry_Ring` record with `itemClassification=Legendary`
in each upstream source against an exact-path presence check in `OURS`:

- **098i vs OURS: 0 gaps** - independent proof our build already carries 100% of SV 0.98i's own
  Legendary amulets/rings (matches the SVAERA-ADOPT recon's "clean proof our overlay covers 100%
  of SV 0.98i").
- **SVAERA vs OURS: 33 Legendary amulet/ring records absent by exact path.** Triaging that list:
  - **~14 are false positives**: SVAERA's own re-templated duplicates of items we already have
    under the DRX path (e.g. `formulaitems\amulet\my_amu_001.dbr` = SVAERA's copy of our
    `drxitem\supra\neck_melee.dbr` "Paragon of Violence"; same pattern for Void Prism, Band of the
    Elder Savage, Ananke's Ring) - **not a real gap**.
  - **~15 are explicitly out of classic-mod scope** per `docs/BACKLOG.md`'s SVAERA-ADOPT
    "DELIBERATELY-SKIP" list: Norse/Chinese-pantheon items (Freyr's Glory, Sif's Gold, Ao Shun's
    Essence of Winter, Niu Mo Wang, Zhuanxu's Sovereignty, Xihe's Suns, Fjalar's Warn, Coeus'
    Power, Hel's Gloom, Xuannu's Longevity...) and `hcdungeon\` (xpack4 Hardcore-Dungeon-only)
    items - both families are xpack2/3/4 DLC content this Classic-scoped mod intentionally
    excludes.
  - **~10 are genuine, still-open gap candidates** - Greek/Egyptian-themed Legendary amulets/rings
    with no xpack2/3/4 coupling, several of which are **already named** in the existing
    `docs/reports/svaera_goodies_audit.md` "Tier 2" curated-legendary bundle (gated by the
    `_DRX_Meshes.arc` 858KB-gutted-vs-430MB-full art lever):
    - `records\item\equipmentring\u_mod_symbolofhathor.dbr` - **Symbol of Hathor** (ring)
    - `records\item\equipmentamulet\u_mod_pearlofmnemosyne.dbr` - **Pearl of Mnemosyne** (amulet)
    - `records\item\equipmentamulet\u_mod_vengeanceofsekhmet.dbr` - **Vengeance of Sekhmet** (amulet)
    - plus not-yet-individually-catalogued siblings: `u_mod_akersguard.dbr` (Aker's Guard, amulet),
      `u_mod_chlorisgrowth.dbr` (Chloris' Growth, amulet), `u_mod_nutscelestialarch.dbr` (Nut's
      Celestial Arch, amulet), `u_mod_phaethonsfall.dbr` (Phaethon's Fall, amulet),
      `u_mod_asteriasoracle.dbr` (Asteria's Oracle, amulet), `u_mod_coeuspower.dbr` (Coeus' Power,
      ring - Greek Titan, keep despite "Coeus" sounding exotic), `u_mod_meteoriccatalyst.dbr`
      (Meteoric Catalyst, ring, grants a meteor-shower proc)
    - two lower-tier (non-"u_mod", regular-formula, not supra) Egyptian amulets also absent:
      `records\item\formulaitems\amulet\f_amu_003.dbr` ("Eye of Maat") and
      `f_amu_004.dbr` ("Mindstone")

- **Independent re-verification of the already-documented "5 sets" finding** (BACKLOG
  SVAERA-ADOPT): confirmed directly - `records\item\sets\drxset049/051/052/053/058.dbr` all exist
  in SVAERA and are **absent** from OURS, while a spot-check of a member item
  (`u_l_hector'sflashinghelm.dbr`, part of `drxset051` "Hector's Bronze Armor") shows it **is**
  present in `OURS` as a standalone item (`itemClassification=Legendary`, upgraded from SVAERA's
  `Epic`) with `itemSetName=None` (SVAERA's copy has `itemSetName=Records\Item\Sets\DRXset051.dbr`
  set). This exactly matches the BACKLOG's "13 member items already ship as standalone uniques,
  only the 5 set-grouping records are missing" finding - independently reproduced here, not just
  cited.

**Verdict for Hunt 3:** no non-weapon gap exists in the DRX "supra" Mythic tier itself (0/0). The
genuine non-weapon gap is a **pre-scoped, pre-approved-concept vein** in SVAERA's separate
additive content (5 item-set groupings + ~10 Greek/Egyptian Legendary amulets/rings), already
recon'd and awaiting Will's picks per `docs/BACKLOG.md` SVAERA-ADOPT and
`docs/reports/svaera_goodies_audit.md` - this hunt independently reproduces and corroborates that
prior recon rather than finding a new, previously-unknown vein.

---

## Sources consulted

- `docs/UBER_WEAPONS_AUDIT.md` (existing audit; both Paragon and the supra tier were previously
  verified 2026-07-07 - this hunt independently re-derived the same facts from the raw `.arz`
  rather than trusting the doc, then cross-checked against it).
- `docs/BACKLOG.md` SVAERA-ADOPT recon block (2026-07-14) and `docs/reports/svaera_goodies_audit.md`
  for the Hunt-3 gap-candidate cross-reference.
- Direct `.arz`/`.arc` decode of: `upstream/soulvizier_098i/{Database/database.arz,
  Resources/Text_EN.arc}`, `upstream/soulvizier_0.9/Database/database.arz`,
  `upstream/soulvizier_041/Database/database.arz`, the live SVAERA Workshop install
  `C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\`
  (`Database/SVAERA_customquest.arz` + `Resources/Text.arc`), and
  `work/SoulvizierClassic/{Database/SoulvizierClassic.arz, Resources/Text.arc}`.
