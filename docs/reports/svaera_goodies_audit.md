# SVAERA Goodies Audit - what SVAERA has that we don't

> **Status:** APPROVED-CONCEPT recon (awaiting Will's picks). Read-only analysis; no
> gameplay records changed. Author: SVAERA Goodies Auditor, 2026-07-14.
> Backlog anchor: **SVAERA-ADOPT** (docs/BACKLOG.md).
> Reproduce: `scratch_audit/svaera_goodies/*.py` (p1_namediff → survey → deep → verify → verify2 → divergence).

## TL;DR

SVAERA (Soulvizier **AERA**, the modern Steam TQAE port, Workshop `2076433374`) carries
**110,495 DB records** vs our effective **92,259**. **30,714** SVAERA records are absent from our
effective DB, and **all 30,714 are SVAERA-authored-new** (0 are SV098 content we dropped - a clean
proof that our overlay already covers 100% of SV 0.98i). Most of that 30k is noise for a *classic*
mod (Ragnarok/Atlantis/Eternal-Embers DLC content, the AERA loot/formula economy, dyes, and
SVAERA's own souls/caravan/endgame systems). But buried in it is a **genuinely good, low-conflict
vein**: a set of **hand-authored Greek & Egyptian item sets and named uniques whose art we ALREADY
ship**, plus a small **Artemis-themed monster pack**.

**Headline adopt (S effort, zero art coupling, verified droppable):** five thematic sets -
**Thoth's Favor, Hector's Bronze Armor, Robes of the Pythia, Patroclus' Disguise, Might of
Hephaestus** = 13 legendary/epic items - are byte-present + functional in SVAERA, use only art in
arcs we already ship (`drx.arc` / `DRXtextures.arc` / base `Items.arc`), and are absent from ours.
They can be grafted with the **existing** `_graft_import_closure()` + Text-tag port + one loot-source
wire. No map work, no new art arc.

**On divergence (finding 2):** SVAERA re-templated and re-balanced essentially *every* common
record (monsters 120/120 sampled diverge from BOTH base and SV098; weapons 120/120; every mastery
100%). This is a wholesale AERA rebalance/re-port, not a set of surgical fixes - **skip as a class**
per the amgoz1 classic bible and Will's mastery hand-tuning rule. The value is in **additive new
content**, not overrides.

---

## 1. Method & sources

| Source | Path | Records |
|---|---|---|
| **SVAERA** | `…workshop\content\475150\2076433374\SVAERA_customquest\Database\SVAERA_customquest.arz` | 110,495 |
| **OURS** (overlay) | `work/SoulvizierClassic/Database/SoulvizierClassic.arz` | 51,029 |
| **SV098** | `upstream/soulvizier_098i/Database/database.arz` | 51,186 |
| **BASE** (TQAE stock) | `…Titan Quest Anniversary Edition\Database\database.arz` | 74,013 |
| Effective-ours = OURS ∪ BASE | | 92,259 |

> ⚠️ **Source correction (worth fixing in `docs/reference_mods.md`):** that doc says SVAERA's
> "Database: SVAERA_customquest.arz (0 MB)" and the in-repo `reference_mods/SVAERA_customquest/`
> only carries `Levels.arc` + `Quests.arc` - **no Database arz**. The real SVAERA database is
> **67.8 MB / 110,495 records** and lives in the live Steam workshop install (path above). This
> audit read the workshop install directly. The build's own graft already resolves it via
> `restore_dropped_npcs.find_svaera_arz()`.

"Absent from ours" = SVAERA record name not in (OURS ∪ BASE), normalized case/slash. "SVAERA-authored"
= diverges from base game (their overlay footprint). Provenance for a divergence = compare SVAERA
vs SV098 (equal ⇒ SV-inherited; differs ⇒ SVAERA-authored). Art coupling resolved by indexing arc
TOCs (our shipped Resources + base-game Resources + SVAERA's own arcs) and classifying each
record's `bitmap`/`mesh` as SHIPPED vs SVAERA-only-arc. Functionality = incoming `.dbr` reference
count across the whole SVAERA arz (loot tables, set records, spawn proxies) - cut content has 0.

---

## 2. Finding (1): records present in SVAERA, absent from ours

**30,714 absent - 100% SVAERA-authored-new, 0 SV098-dropped.** Top families (full list:
`scratch_audit/svaera_goodies/p1_buckets.txt`):

| count | family | what it is | verdict |
|---:|---|---|---|
| 11,364 | `item\formulas` | AERA artifact/enchant reroll-formula economy | SKIP (economy) |
| 2,903 | `item\loottables` | loot plumbing for their roster | partial (needed by adopts) |
| 2,463 | `skills\monster skills` | skills for their new/rebalanced monsters | SKIP (coupled) |
| 2,360 | `item\lootmagicalaffixes` | affix plumbing (rebalance) | SKIP |
| 1,532 | `all_sv\item` | **561 are `OneShot_Dye`**, rest loot/formula | SKIP (dye system + plumbing) |
| 843 | `item\equipmentring` | **incl. `\soul\*` region-drop souls** + real rings | MIXED (souls SKIP; rings partial) |
| 769 | `all_sv\skills` | monster/pet/item skills, 36% xpack-coupled | SKIP (coupled) |
| 543 | `item\merchants` | merchant tables (economy) | SKIP |
| ~2,500 | `xpack2\* / xpack3\* / xpack4\*` | **Ragnarok / Atlantis / Eternal-Embers DLC** | **SKIP (not classic, DLC art)** |
| 455 | `item\equipmentweapon` | 302 staves + weapons (many u_mod uniques) | ADOPT (curated) |
| 260 | `creature\npc` | **199 dye merchants + 54 `NpcItemUpgrader`** | ADOPT (upgrader) / SKIP (dye) |
| 232 | `sv_ew\*` | **Artemis "extra wildlife" bestiary** (moonwolf, oceanids) | **ADOPT** |
| 210 | `skills\soulskills` | SVAERA's own soul-pet/skill system | SKIP (conflicts w/ ours) |
| 194 | `item\petbonus` | pet set-bonus records | partial (coupled to items) |
| 108 | `game\svic` | item-cost economy tiers | SKIP (economy) |
| 39 | `item\sets` | **DRX/new item sets** (mixed theme, some xpack) | **ADOPT (Greek/Egyptian)** |
| 42 | `effects\weaponenchantments` | blood-themed weapon FX | ADOPT (Toxeus theme) |

Everything absent is additive; nothing we already have is at risk from *adding* these.

---

## 3. Finding (2): where SVAERA diverges from BOTH base and SV098

Sampled 13 content families over records common to all three DBs
(`scratch_audit/svaera_goodies/divergence.py`):

| family | common | sampled | diverge-from-BOTH | ==SV098 |
|---|---:|---:|---:|---:|
| creature\monster | 1,938 | 120 | **120** | 0 |
| item\equipmentweapon | 1,832 | 120 | **120** | 0 |
| item\equipmentring | 199 | 120 | **120** | 0 |
| item\equipmentarmor | 799 | 120 | **120** | 0 |
| skills\nature / stealth / warfare / hunting / earth / storm / spirit | - | all | **100%** | 0 |
| item\loottables | 2,232 | 120 | **120** | 0 |

**Conclusion: SVAERA is a total re-template + rebalance.** The #1 divergent field on monsters is
`templateName` (120/120 - every monster re-pathed for AE), and weapons diverge across *hundreds* of
stat fields (`retaliationSlow*`, `offensive*`, `defensive*`, `characterStrength`…). This is the
"Steam fork with nerfs" (per `docs/reference_mods.md`). There is **no clean surgical-fix subset** to
lift - the AE-compat fixes are welded to the rebalance and the template churn. **Deliberately skip
the entire override class.** (The one lead worth a separate spike is MP spawn-scaling: SVAERA is
AE-native so its monster `templateName`/spawn-equation forms parse in AE where our CLAUDE.md notes
SV's `RunEquation` MP formulas silently fail - but that is an MP-compat investigation, not a
content adopt, and would mean importing SVAERA's monster templates wholesale.)

---

## 4. Finding (3): SVAERA-unique CONTENT by category

- **New items / weapons / sets** - the rich vein. **6,625 named uniques** resolve a real name tag
  and are absent from ours (146 Legendary, 3,077 Epic, 350 Rare, …). Themes span Greek, Egyptian,
  Norse, and Chinese - the **Greek + Egyptian** subset is classic-fitting (acts 1-4); Norse/Chinese
  are Ragnarok/Atlantis/EE flavor = skip. **39 item sets**; the non-xpack Greek/Egyptian ones are
  excellent (§5). Art for the `u_l_/u_e_` "drx" items is largely in `drx.arc`/`DRXtextures.arc`
  (shipped); the `u_mod_*` items' art is in `_DRX_Meshes.arc` / `_DRX_Textures.arc` - see the art
  lever (§7).
- **New monsters / heroes** - small but on-theme: the **`sv_ew` Artemis bestiary** (Moon Wolf ~
  Hound of Artemis; Artemisian Oceanid nymph line: Moon Maiden / Beast Tamer / Huntmistress). Only
  5/232 xpack-coupled. Art is in `N66_Mods.arc` (not currently shipped). The larger new-monster
  count is `all_sv\creature\monster\fireimp\*` = Ragnarok chaos-imps (xpack, skip). No standalone
  `creature\hero` namespace - heroes are Monster-class variants inside the packs above.
- **New skills** - `skills\soulskills` (210) is SVAERA's *own* soul architecture; `all_sv\skills`
  and `skills\item skills` are mostly monster/pet/item-proc support. These are coupled to SVAERA's
  systems and would conflict with our curated souls - skip except where pulled in as a graft
  dependency of an adopted item.
- **Souls-system changes** - SVAERA reworked souls into region/act "anysoul" drops
  (`item\equipmentring\soul\01_act0N_anysoul` = Normal/Epic/Legendary × Greece/Egypt/Orient/Olympus/
  Atlantis/Hades/North). This is a *different* souls model from ours (our centerpiece, hand-tuned).
  **Skip** - do not cross the streams.
- **QoL / fix records** - `NpcItemUpgrader` "free upgrader" NPCs in every Greek/Egyptian town (54),
  and blood-themed `weaponenchantments` FX (42). The resource arc literally named "A Few Bug
  Fixes.arc" is a *resource* archive (not DB), so its fixes are art/anim, not gameplay records; the
  DB-level "fixes" are inseparable from the §3 rebalance.

---

## 5. ADOPT-CANDIDATE shortlist (the curated good stuff)

Effort: **S** = DB records + Text tags + one loot wire (no art, no map). **M** = adds an art
extraction (a few `_DRX_Meshes` icons or `N66_Mods` meshes) or a small system. **L** = new art arc
+ map placement. Adoption vehicle for all item candidates: the **existing**
`build_svc_database.py::_graft_import_closure(db, svaera_db, base_names, roots)` (recursively imports
the SVAERA closure, skips anything resolving at runtime, fail-loud on dangling) + Text-tag port +
adding the item to a SVC loot source (a boss chest, Toxeus drop, or a SVC loot table).

### Tier 1 - clean thematic sets (art already shipped, verified droppable) - **S each**

| # | Candidate | Members (quality) | Theme | Coupling |
|---|---|---|---|---|
| 1 | **Thoth's Favor** (`drxset049`) | Thoth's Mark (ring), Thoth's Shadow (armor) - 2× **Legendary** | Egyptian | art SHIPPED; 2 tags |
| 2 | **Hector's Bronze Armor** (`drxset051`) | Flashing Helm, Shimmering Shield, Spear - 3× **Epic** | Greek / Trojan | art SHIPPED; 3 tags |
| 3 | **Robes of the Pythia** (`drxset052`) | Vestment, Clasps - 2× **Epic** | Greek / Delphi oracle | art SHIPPED; 2 tags |
| 4 | **Patroclus' Disguise** (`drxset053`) | Armor / Spear / Shield of Achilles - 3× **Legendary** | Greek / Trojan | art SHIPPED; 3 tags |
| 5 | **Might of Hephaestus** (`drxset058`) | Hand, Molten Shield, Seal - 3× **Legendary** | Greek / smith-god | art SHIPPED; 3 tags |

### Tier 2 - flavorful, modest art coupling

| # | Candidate | What | Effort | Coupling |
|---|---|---|---|---|
| 6 | **The Hunting Paradox** (`newset002`) | Claws of Laelaps + Legs of the Teumessian Fox (the hound that always catches + the fox never caught - the divine paradox; peak amgoz1 flavor) | **M** | world meshes SHIPPED; **2 icons** from full `_DRX_Meshes.arc` |
| 7 | **The Elephantine Triad** (`newset005`) | Khnum / Anuket / Satis (Egyptian Elephantine gods, act 2) | **M** | icons from `_DRX_Meshes`; 1 member greave mesh is an **xpack3** asset (reskin or skip that piece) |
| 8 | **Greek/Egyptian legendary uniques bundle** | Curated subset of the 146 legendaries: Meteorite, Scepter of Lamashtu, Stormcrack, Nature's Revenge, Sickle of Kronos, Crown of Life & Death (Osiris' Atef), Vengeance of Sekhmet, Symbol of Hathor, Pearl of Mnemosyne… (filter OUT Norse/Chinese: Sif, Freyr, Sleipnir, Ao Shun, Nuwa) | **M** | art in `_DRX_Meshes`/`_DRX_Textures` - the §7 lever unlocks the whole roster at once |

### Tier 3 - new monsters (Artemis pack)

| # | Candidate | What | Effort | Coupling |
|---|---|---|---|---|
| 9 | **sv_ew Artemis bestiary** | Moon Wolf ~ Hound of Artemis (spawned pet/creature) + Artemisian Oceanid nymph line (Moon Maiden / Beast Tamer / Huntmistress, Champion-rank). Strong monster-identity fit (Artemis' hunt) | **M-L** | meshes in `N66_Mods.arc` + skins in `SV_NewSkins.arc` (neither shipped); needs map/proxy placement in a Greek hunt-themed area |

### Tier 4 - QoL / theming

| # | Candidate | What | Effort | Coupling |
|---|---|---|---|---|
| 10 | **NpcItemUpgrader "free upgrader"** | Town NPCs (Athens/Delphi/Knossos/Megara/Sparta/Memphis…) that upgrade items - QoL beginner-friendly service (engine template is base-game) | **M** | needs the upgrade-table records + map placement; confirm exact mechanic before committing |
| 11 | **Blood weapon-enchant FX pack** | `bloodweapon_fx`, `bloodpact_weaponenchantment`, arrowblood - on-theme FX for future Toxeus/blood-cave uniques | **S** | FX-only; low standalone value (needs a skill/item consumer) |

**Recommended first wave:** candidates **1-5** (13 items, zero art work, all verified) as a single
"SVAERA Heroes of Troy & the Gods" set-drop pack, wired into existing SVC boss chests. Then the §7
art lever to open Tier 2.

---

## 6. Verified end-to-end (8 candidates - exceeds the 5 required)

`scratch_audit/svaera_goodies/verify.py` + `verify2.py`. Each: truly absent from ours? present +
well-formed + name resolves in SVAERA? incoming references (functional vs cut)? art shipped?

| candidate | absent? | name resolves | refs (functional) | art | verdict |
|---|:--:|---|---:|---|---|
| Hector's Bronze Armor set | ✅ | "Hector's Bronze Armor" | set×3; members 69/70/71 loot refs | all **SHIPPED** | **ADOPT-CLEAN** |
| Patroclus' Disguise set | ✅ | "Patroclus' Disguise" | set×3; members 67/68/70 | all **SHIPPED** | **ADOPT-CLEAN** |
| Might of Hephaestus set | ✅ | "Might of Hephaestus" | set×3; members 68/69/70 | all **SHIPPED** | **ADOPT-CLEAN** |
| Robes of the Pythia set | ✅ | "Robes of the Pythia" | members droppable | all **SHIPPED** | **ADOPT-CLEAN** |
| Thoth's Favor set | ✅ | "Thoth's Favor" | members droppable | all **SHIPPED** | **ADOPT-CLEAN** |
| The Hunting Paradox set | ✅ | "The Hunting Paradox" | members 60/60 | meshes shipped, **2 icons in `_DRX_Meshes`** | ADOPT (M) |
| Artemisian Oceanid (Moon Maiden) | ✅ | "{^y}Artemisian Oceanid ~ Moon Maiden" | referenced (name2 + proxy) | mesh **`N66_Mods` (unshipped)** | ADOPT (M-L) |
| Moon Wolf (Hound of Artemis) | ✅ | "{^y}Moon Wolf ~ Hound of Artemis" | 1 `spawnObjects` ref (summoned) | mesh **`N66_Mods` (unshipped)** | ADOPT (M-L) |
| Meteorite (legendary mace) | ✅ | "Meteorite" | 59 refs (reagent+loot) | art in **`_DRX_Meshes` (gutted)** | ADOPT via §7 lever |

None of the eight are cut content: every set member and monster carries a resolving name and real
incoming references (loot tables / spawn proxies).

---

## 7. The `_DRX_Meshes.arc` art lever (key enabler)

Our build ships a **gutted** `_DRX_Meshes.arc` (858 KB) and `_DRX_Textures.arc` (14 KB) vs SVAERA's
**430 MB / 30.8 MB**. That single gutting is what blocks the entire `u_mod_*` unique roster
(~146 legendary + ~3,077 epic) and several sets - their inventory icons and world meshes live there.
The `drx.arc` (62 MB) + `DRXtextures.arc` (223 MB) we *do* ship, which is why the `drxset0**` sets
(Tier 1) are free.

**Decision to put to Will:** ship a fuller `_DRX_Meshes.arc`/`_DRX_Textures.arc` (or an
extracted-subset arc containing only the icons/meshes the adopted items reference). This is a
one-time size/packaging decision that converts Tier-2/uniques from "M each" to "S each." Given the
mod is already ~1.1 GB with DRX kept, a targeted subset arc is the proportionate choice.

---

## 8. DELIBERATELY-SKIP families (with reason)

| family / system | records | why skip |
|---|---:|---|
| `xpack2\* / xpack3\* / xpack4\*` (Ragnarok / Atlantis / Eternal Embers) | ~2,500 | Not classic; needs DLC art; off-concept |
| `item\formulas` + artifact-reroll economy | 11,364 | AERA crafting economy, contradicts classic loot |
| §3 stat overrides (monsters / weapons / armor / masteries / loot) | ~all common | Wholesale AERA rebalance; contradicts amgoz1 classic + Will's mastery hand-tuning |
| `item\equipmentring\soul\*` + `skills\soulskills` | ~420 | SVAERA's own souls model; conflicts with our curated souls (the centerpiece) |
| `OneShot_Dye` dyes + dye merchants | ~760 | Cosmetic system, UI/merchant coupling, not classic-critical |
| `mod_allcaravans\*` | ~308 | We already have Super Caravan |
| `sv_endgame\*` crystal-hub portals/scenery | 21 | AERA endgame; needs the custom hub level (map-coupled) |
| `item\artifacts\n_mercscroll_*` mercenary system | ~60 | Whole summon-merc system, xpack-coupled |
| `game\svic` item-cost tiers, `item\merchants` | ~650 | Economy plumbing / rebalance |

---

## 9. Coupling & integration checklist (for whichever picks Will approves)

1. **DB graft** - add roots to a new graft list and call `_graft_import_closure(db, svaera_db,
   base_names, roots)` (already loaded when `SVC_GRAFT_SVAERA=1`, default ON). It pulls each item +
   its skill/proc/FX closure, storing under SVAERA canonical names, never overwriting ours.
2. **Text tags** - port the resolved name/desc tags (`tagSetNameLE*`, `tagNewUnique*`, `tagNewSet*`,
   `tagMonster*`, etc.) from SVAERA `Text.arc` into `build_text_arc.py`; the existing tag-resolution
   build gate will fail loud on any missing one.
3. **Loot source** - the SVAERA loot tables that reference these items are *not* ours; wire adopted
   items into an SVC drop (boss chest / Toxeus / a new SVC loot table) so they are obtainable.
4. **Art** - Tier 1 = none. Tier 2/uniques = §7 lever. Tier 3 monsters = add `N66_Mods` meshes +
   `SV_NewSkins` textures as a packaged arc, then map/proxy placement (map lane).
5. **Permission** - precedent exists: the SVAERA mastery graft (docs/BACKLOG.md, 2026-07-10) records
   **soa's verbal permission** to use SVAERA content additively. Confirm it covers items/monsters
   before shipping.
6. **Gates** - dry-run graft replay vs the current baseline arz (record-diff = only the intended
   additions), `validate_tags` green, contracts (souls/summons/resources) unaffected, map untouched
   for Tier 1-2.

---

## Appendix - reproduction

```
cd tqit_soulvizier_classic
py scratch_audit/svaera_goodies/p1_namediff.py    # name-set diff -> p1_buckets.txt, p1_names.json
py scratch_audit/svaera_goodies/survey.py         # family survey -> survey_out.txt
py scratch_audit/svaera_goodies/deep.py           # bestiary/uniques/sets/upgrader -> deep_out.txt
py scratch_audit/svaera_goodies/verify.py         # 8-candidate end-to-end (refs + art)
py scratch_audit/svaera_goodies/verify2.py        # remaining sets + uniques art
py scratch_audit/svaera_goodies/divergence.py     # finding (2) sampling
```

Numbers: SVAERA 110,495 · absent-from-ours 30,714 (100% SVAERA-authored-new) · SVAERA overlay
beyond base 39,502 · families triaged 22 · adopt candidates 11 · skip families 9 · verified 8.
