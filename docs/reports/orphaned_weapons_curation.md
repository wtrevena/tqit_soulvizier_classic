# Orphaned-Weapon Curation - raw material for new uber forge formulas

> Audit date: 2026-07-14. Task (Will, verbatim): *"are there any cool orphaned weapon
> records that we could use to make new uber weapons behind? some uber forge formula
> weapons. add this to the backlog."*
>
> Ground truth = the effective DB: `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
> (BUILT) overlaid on the base game `database.arz` (BASE); names via `work/.../Text.arc`
> over base `Text_EN`. Read-only analysis. Tooling: `scratch_audit/auditlib` (overlay-aware
> arz/arc reader) + audit scripts archived in the session scratchpad.

---

## TL;DR

- **4,360** weapon-class records exist in the effective DB (Sword / Axe / Mace / Spear /
  Bow / Thrown / Staff / Shield). Of those: **3,007 OBTAINABLE**, **1,069 ORPHANED**
  (1,054 referenced by *nothing*, 15 referenced only by dead records), **284** excluded as
  template/test/placeholder junk. (3007 + 1069 + 284 = 4360.)
- The orphan pool is real and large, but most of it is low-value (base "old/" placeholder
  gear, monster-infrequent commons, AE-reorg duplicate shells). The **cool** orphans - proper
  display name, distinctive art and/or a granted skill, strong lore - number a few dozen.
- **14 curated candidates** (plus an 8-item Greek-axe bench) are ranked below with a pitch,
  record path, tier/level, what makes them special, and a per-candidate supra-pattern design
  sketch. **Spear and Shield have NO quality orphan** (honest gap: Blood Whisper already fills
  the supra spear slot; the only "orphan shield" is a formula-blank stub).
- **The supra system is already SVC-extended** exactly the way this feature wants: three new
  `svc_thrown_*` formulas (Charon's Toll, The Last Word, Sanguine Orbit) are wired into
  `supra.dbr` + `supra_special.dbr` and their `svc_wep_*` results are obtainable. That is the
  proven in-repo template. The **24 orphaned `zrecipes\` duplicate formulas** are ready-made
  reuse vehicles.
- **Verification:** 5 orphan classifications proven end-to-end across **three independent
  reference vectors** (a second arz decoder over BUILT *and* BASE, a decompressed Quests.arc
  reward scan, a raw Levels.arc token scan) - all agree: **0 references**.

---

## Method

**Effective world model.** For every record path present in BUILT or BASE, the effective
fields come from BUILT if it defines that path, else BASE (BUILT overrides BASE per-record;
BASE supplies the rest). Union = **92,259** records.

**Reference graph.** Every field value of every effective record was scanned; any value that
normalises to a known `.dbr` record path is an outgoing reference edge. This yields, per
record, the set of records that reference it (`referenced_by`).

**Obtainability (reachability).** Drop-anchors ("roots") = every creature/monster/npc/guard/
merchant (by Class **or** by `records\...creature[s]\...` path, incl. every xpack), every
container/chest (`FixedItemContainer`/`ItemContainer`/`*Chest*`), every `ItemArtifactFormula`,
and every record carrying fixed-equipment loot fields (`lootRightHandItem1`, `chestArmorName`,
…). A weapon is **OBTAINABLE** if it is reachable from any root through reference edges
(loot tables incl. nested/fixed-weight members, merchant inventories, formula results, monster
equipment, chest/container tables). Root seeding was deliberately **wide** (bias toward
obtainable) so the orphan list can never contain a false positive.

**Classification.**
- **OBTAINABLE** - reachable from a root.
- **ORPHAN_HARD** - **zero** external records reference the weapon's path. Cannot be pointed to
  by any mechanism the DB can express. *This class is invariant to root choice* (it held at
  ~1,054 across three separate root definitions), which is why it is the trustworthy base for
  curation.
- **ORPHAN_UNREACH** - referenced, but only by records that are themselves not reachable from
  any root (e.g. a loot table nothing invokes). Genuine orphans, but a smaller/edge set (15).
- **JUNK** - an orphan with no resolvable display name **and** zero base damage, or a
  test/dev-cheat/placeholder path marker.

**Two reachability bugs were found and fixed during the audit** (documented here because they
are exactly the "missed reference poisons the list" trap): (1) `FixedItemContainer`s (e.g. the
Jade Emperor's electrum orbs) had to be seeded as roots - without them, Starbow *et al.* were
wrongly flagged; (2) many creatures live under `records\xpackN\creatures\...` or carry custom
Class strings (`Ormenos`, `Npc`, `Guard`), so roots must be seeded by creature **path**, not
just `Class == Monster*`. After the fix, false ORPHAN_UNREACH collapsed from 169 to 15.

---

## Ground-truth counts (gate record)

| Metric | Value |
|---|---:|
| Weapon-class records (effective DB) | **4,360** |
| OBTAINABLE | 3,007 |
| ORPHANED (HARD 1,054 + UNREACH 15) | **1,069** |
| JUNK excluded (placeholder/test/zero-stat-unnamed) | 284 |
| Named orphans (have a real display name) | 442 |
| Named orphan Epic/Legendary | 79 |
| Curated candidates | 14 (+8 axe bench) |
| Sample verified end-to-end (independent) | 5 |

Weapon-class breakdown (effective DB): Axe 517, Staff 503, Shield 475, Sword 443, Mace 407,
Bow 316, Spear 298, Thrown (RangedOneHand) 13. Orphan-hard **named** origin split:
base/IT 344, xpack1 7, xpack2 6, DRX 6, xpack4 3, xpack3 1.

---

## Verification (sample of 5, three independent vectors)

For 5 candidates spanning namespaces, three *independent* methods (different code paths than
the primary `auditlib` scan) all confirm **zero references**:

1. **Second arz decoder** (`tools/arz_extract.decode_record_data`) run over **BUILT and BASE**
   - scans every field value of all 51,029 + 74,013 records.
2. **Quests.arc** (110 entries) fully **decompressed** and searched - and a sanity sweep shows
   Quests.arc references **zero** `equipmentweapon` paths at all (the mod grants no weapons by
   quest), so the "quest reward" vector is empty for weapons.
3. **Levels.arc** raw token scan for the distinctive mesh/record tokens.

| Sample record | 2nd arz decoder (BUILT/BASE) | Quests.arc | Levels.arc tokens |
|---|:--:|:--:|:--:|
| `records\item\equipmentweapon\sword\u_n_ripulsar.dbr` | 0 / 0 | absent | 0 |
| `records\xpack\item\equipmentweapons\sword\u_n_aquimae.dbr` | 0 / 0 | absent | 0 |
| `records\drxitem\eggs\zzz_munderizer.dbr` | 0 / 0 | absent | 0 |
| `records\xpack2\item\equipmentweapons\1hranged\u_l_10.dbr` (Hati) | 0 / 0 | absent | 0 |
| `records\xpack3\items\equipmentweapon\club\z_swordfish.dbr` | 0 / 0 | absent | 0 |

All 14 curated candidates were additionally confirmed absent from the decompressed Quests.arc.

**Scope note.** "Obtainable" here is DB-reference-graph obtainability (loot/merchant/formula/
container/equipment). Some base-game loot is assigned by xpack **map/quest scripts** to loot
tables that have zero arz references (e.g. Eternal Embers "starting_china" tables); such items
are conservatively classed OBTAINABLE and kept **off** the orphan list, since this custom-quest
world may or may not stream that content. The curated list is drawn from ORPHAN_HARD (zero
references anywhere), which is safe regardless.

---

## The existing supra pattern (proven template to clone)

The uber craftables are the DRX **"supra"** tier: `records\drxitem\supra\*`, Legendary class,
lvl-65 requirement, crafted at the Enchanter from a **Mythic Formula + 3 reagents**. Verified
wiring:

- **Result item:** `records\drxitem\supra\<name>.dbr` (or `svc_wep_<name>.dbr` for SVC
  additions) - Legendary, `numRelicSlots=1`, bespoke or shared mesh + UI bitmap, usually an
  `itemSkillName` proc and a `weaponTrail`.
- **Formula:** `records\drxitem\supra\recipes\<name>_formula.dbr` (or `zrecipes\...`),
  `Class = ItemArtifactFormula`: `description` = recipe-name tag ("Mythic Formula - <name>"),
  `artifactName` = the result, `artifactBonusTableName`, formula art (`xrecipe` skin /
  `Recipe01.msh`), `reagent1/2/3BaseName` = **3 real items, typically 2 Legendary + 1 Rare,
  thematically matched** to the result (e.g. Blood Whisper = Peleus' Ashen Spear + Queen
  Zenobia's Spear + an Ichthian spear).
- **Drop:** the formula is listed as a `lootNameN` in **both**
  `records\xpack\item\loottables\arcaneformulae\supra.dbr` **and** `...\supra_special.dbr`
  (LootItemTable_FixedWeight). These two tables currently carry **28** formula members = the
  25 `recipes\` set + **3 already-added `svc_thrown_*` SVC formulas**.

**SVC has already used this exact path** to add three thrown ubers -
`svc_thrown_charonstoll` -> **Charon's Toll**, `svc_thrown_lastword` -> **The Last Word**,
`svc_thrown_sanguineorbit` -> **Sanguine Orbit** (all `WeaponHunting_RangedOneHand`, all
OBTAINABLE). New candidates should follow the same `svc_wep_<name>` / `svc_<class>_<name>_formula`
convention and join both drop tables.

**Reuse vehicles - 24 orphaned `zrecipes\` formulas.** The `zrecipes\` folder holds 27
formulas; only the 3 `svc_thrown_*` are in a drop table. The other **24 are duplicate
`ItemArtifactFormula` records** whose `artifactName` points at the already-live `recipes\`
results (e.g. `zrecipes\wep_axe_formula -> wep_axe.dbr`) and which **nothing references**.
Each is a clean, pre-built formula shell: repoint its `artifactName` + `reagent*BaseName` +
`description` at a new orphan result and add it to the two drop tables - no new formula record
needed, and the canonical `recipes\` formula still crafts the original. (Prior memory called
this "10 zrecipes"; the ground-truth count is **24**.)

---

## Curated candidates (14) - ranked

Legend: **twins** = number of *obtainable* weapons that share this display name (0 = the
identity is fully free; 1-2 = the name also lives on a droppable item - the orphan record is
still unreferenced and safe to repurpose, but rename the uber or position it as an "ascended"
version). "Art" = mesh: **bespoke** (its own model) vs **shared** (a Default recolor - give the
supra a bespoke DRX skin/trail like Blood Whisper's crimson trail to distinguish it).

| # | Name | Class | Record | Tier / Lvl | Art | Twins | Why it's cool |
|--:|------|-------|--------|-----------|-----|:-----:|---------------|
| 1 | **Ripulsar** | Sword | `records\item\equipmentweapon\sword\u_n_ripulsar.dbr` | Epic / 17 | bespoke `ripulsarmesh` +own skin/icon | 0 | Mod-authored (MOD name tag) DRX unique, fully bespoke art, fast, grants a mastery skill. A genuinely lost SV/DRX blade. |
| 2 | **Aquimae** | Sword | `records\xpack\item\equipmentweapons\sword\u_n_aquimae.dbr` | Epic / 33 | bespoke `aquimaemesh` +own skin/icon | 0 | Mod-authored DRX unique, bespoke art, life-leech. Twin of Ripulsar as a "lost DRX pair." |
| 3 | **Helona** | Staff | `records\xpack\item\equipmentweapons\staff\u_n_helona.dbr` | Epic / 33 | bespoke `helonamesh` | 1 | Mod-authored caster staff that **grants a summon** (`helona_summon`). A staff uber with a unique pet proc. |
| 4 | **Hati** | Thrown | `records\xpack2\item\equipmentweapons\1hranged\u_l_10.dbr` | Legendary / 79 | bespoke Aesir throwing-axe | 0 | The Norse wolf that devours the moon. Already L79 / 184-196 phys. Joins the 3 existing SVC thrown ubers as a 4th. |
| 5 | **Sword Fish** | Mace | `records\xpack3\items\equipmentweapon\club\z_swordfish.dbr` | Legendary / 70 | bespoke dead-fish model | 0 | The joke-tier secret uber: a literal floating fish you club things with. Perfect "hidden Easter egg behind a formula." |
| 6 | **Phoenix** | Axe | `records\equipmentweapon\axe\u_l_phoenix.dbr` | Legendary / 59 | shared `RAxe16A` | 1 | The only orphan Greek axe with a **live granted skill** (Heat Shield) + fire damage. Natural fire/rebirth uber. |
| 7 | **Erysichthon's Hunger** | Axe | `records\equipmentweapon\axe\u_l_erysichthon'shunger.dbr` | Legendary / 59 | shared `RAxe13A` | 1 | The man cursed with insatiable hunger - a perfect life/mana-devour uber theme. |
| 8 | **Scylla** | Axe | `records\equipmentweapon\axe\us_l_baneofmessia01.dbr` | Legendary / 59 | shared `RAxe01C` | 1 | Half of a matched sea-terror **pair** (with Charybdis) - craft them as a themed dual set. |
| 9 | **Charybdis** | Axe | `records\equipmentweapon\axe\us_l_baneofmessia02.dbr` | Legendary / 59 | shared `RAxe14B` | 1 | The devouring whirlpool - the other half of the Scylla pair. |
| 10 | **The Furies** | Axe | `records\equipmentweapon\axe\u_l_thefuries.dbr` | Legendary / 59 | shared `RAxe14C` | 1 | The Erinyes of vengeance - bleed/retaliation uber identity. |
| 11 | **Heartpierce** | Sword | `records\drxitem\eggs\zzz_unholykatana.dbr` | Epic / 8 | shared `RSword03B` | 1 | DRX Easter-egg "unholy katana": 30% pierce + bleed, very fast. A cursed-bleeder uber. |
| 12 | **Doom Herald** | Mace | `records\drxitem\eggs\zzz_bamfhammer.dbr` | Epic / 36 | shared `RClub09C` | 1 | DRX Easter-egg warhammer ("bamfhammer") - a demonic herald's maul. |
| 13 | **The Munderizer** | Staff | `records\drxitem\eggs\zzz_munderizer.dbr` | Rare / 45 | bespoke skin (magenta `^f` name) | 0 | The DRX homage to Munderbunny (SV's host). Its own magenta name + skin - the ultimate lore-insider secret uber. |
| 14 | **Di Jun's Pride** | Bow | `records\xpack4\item\equipmentweapon\bow\unique_suns_bow.dbr` | Legendary / 70 | bespoke sun-bow (`houyibow`) | 2 | A solar deity's bow, 336-384 phys. Fills the bow slot beyond Stormbringer. (Name is live on 2 bows - give the uber a fresh solar name.) |

### Greek-axe bench (8 more, identical ORPHAN_HARD pattern: Legendary, L50-59, shared mesh, 1 twin)

All at `records\equipmentweapon\axe\`: **Acheron's Touch** (`u_l_acheron'stouch`),
**Axe of Tereus** (`u_l_axeoftereus`), **Persephone's Caress** (`u_l_persephone'scaress`),
**Torment** (`u_e_torment`), **Shai'tan** (`u_e_shai'tan`), **Atropos' Assistant**
(`u_e_atropos'assistant`), **Enkidu's Stand** (`u_e_enkidu'sstand`), **Theogenes' Onslaught**
(`u_e_theogenes'onslaught`). These are the SV/TQIT-era classic uniques orphaned by the AE
item-tree reorg (their live twins sit at `records\item\equipmentweapon\axe\...`). Rich Greek
identities, shared meshes - ideal if Will wants an all-axe "Wrath of the Underworld" formula set.

---

## Per-candidate design sketch (supra pattern)

General recipe for **every** candidate (clone the proven `svc_thrown_*` path):

1. **Result** `records\drxitem\supra\svc_wep_<name>.dbr`: buff to the supra envelope - lvl-65
   requirement, Legendary, `numRelicSlots=1`, supra-tier damage (~245-400 phys, or the
   elemental/pierce/bleed equivalent), a granted `itemSkillName` proc themed to identity, and a
   `weaponTrail`. **Keep the orphan's mesh/skin/bitmap** (its art is the point); for shared-mesh
   picks add a bespoke DRX trail/tint. Items already at supra strength (Hati, Sword Fish,
   Di Jun's Pride at L70-79) can be used largely as-is with a lvl-65 parity pass.
2. **Formula** `records\drxitem\supra\zrecipes\svc_<class>_<name>_formula.dbr` **or reuse one of
   the 24 orphan `zrecipes\` shells**: `description` = new tag `tagRecipe_svc_<name>`
   ("Mythic Formula - <name>"), `artifactName` = the result, reuse a supra `artifactBonusTableName`
   + formula art, `reagent1/2/3BaseName` = 2 Legendary + 1 Rare (below).
3. **Drop:** add the formula as a new `lootNameN` in **both** `supra.dbr` and `supra_special.dbr`.
4. **Text:** add `tagRecipe_svc_<name>` (+ any new item name tag) via the tag manifest;
   `validate_tags` gate must stay green (arz + Text.arc ship together).

Per-candidate reagent themes (2 Legendary + 1 Rare, thematically matched; exact records chosen +
resolve-checked at implementation, as the existing supra formulas do):

- **Ripulsar / Aquimae** (lost DRX blades) - 2 Legendary swords of speed/bleed + 1 Rare blade.
- **Helona** (summoning staff) - 2 Legendary summoner/vitality staves + 1 Rare pet-boosting charm.
- **Hati** (Norse wolf) - 2 Legendary Ragnarok/beast items (wolf/Fenrir/Aesir themed) + 1 Rare pelt/fang.
- **Sword Fish** (novelty) - lean into the joke: 2 Legendary "sea"/aquatic uniques + 1 Rare fish/net charm.
- **Phoenix** (fire/rebirth) - 2 Legendary fire uniques (a fire heart/relic + a flame blade) + 1 Rare ember charm.
- **Erysichthon's Hunger** (curse of hunger) - 2 Legendary life-drain/vampiric items + 1 Rare famine relic.
- **Scylla + Charybdis** (paired sea-terrors) - cross-reagent them: each takes the other's tier-down form + 2 Legendary Poseidon/deep-sea uniques.
- **The Furies** (vengeance/bleed) - 2 Legendary bleed/retaliation uniques + 1 Rare underworld charm.
- **Heartpierce / Doom Herald** (DRX cursed eggs) - 2 Legendary demonic/DRX uniques + 1 Rare cursed relic.
- **The Munderizer** (insider egg) - 2 Legendary caster staves + 1 Rare joke/egg reagent (keep it silly).
- **Di Jun's Pride** (solar bow) - 2 Legendary sun/light uniques + 1 Rare radiant charm.

---

## Honest gaps

- **Spear:** no quality orphan. The supra spear (**Blood Whisper**) already exists and is
  obtainable; the only orphan spears are junk/placeholder. If Will wants a second spear uber it
  must be authored fresh (or reskinned from a non-spear), not sourced from an orphan.
- **Shield:** no quality orphan. The single "orphan shield" (`{^O}The Scorcher`) is a
  `formulaitems\blank_orb` stub, not a real shield. A new shield uber must be authored fresh.
- **Bow:** thin - only **Di Jun's Pride** rises above monster-common tier, and its name is live
  on two droppable bows (rename recommended).

---

## Reproduce

Session scratchpad scripts (read-only, `py` launcher, `PYTHONIOENCODING=utf-8`):
`orphan_weapon_audit.py` / `audit_v2.py` (graph + classification, writes
`weapon_audit_v3.json`), `hunt.py` / `bytype.py` / `final_data.py` (curation views),
`verify_independent.py` + `quests_scan.py` (independent verification), `supra.py` / `supra2.py`
(supra wiring). All load `scratch_audit/__pycache__/auditlib` against `PATHS['BUILT']` +
`PATHS['BASE']`.
