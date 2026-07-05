# THE CONTENT PLAYBOOK - Soulvizier Classic (Titan Quest Anniversary Edition)

> How the TQAE **content** layer actually works, and exactly what to do to add new
> items, souls, pets, quests, quest rewards, loot drops, and display text into this
> mod. This is the DB/records/text companion to `docs/MODDING_PLAYBOOK.md` (which
> covers the world/levels/navmesh/connections layer). Where this file says
> "level"/"navmesh"/"cave entrance", read the MODDING_PLAYBOOK; where it says
> "record"/"item"/"soul"/"quest reward"/"tag", read here.
>
> Written for a future session (or Will) starting from the repo with ZERO project
> memory. Every claim is grounded in a runnable tool or a real record sampled from
> the built database. Cited `path:line` references are to files in this repo.
> Where a `CLAUDE.md` "Key technical lesson" was terse, it is expanded here into
> concrete steps with real field names and paths.
>
> Companion docs: `docs/MODDING_PLAYBOOK.md` (world/levels/navmesh - READ FIRST for
> anything spatial), `CLAUDE.md` (status board + hard-won lessons index),
> `docs/CHANGELOG.md`. No em dashes anywhere by house style.

---

## 0. Orientation and conventions

- Python: use the `py` launcher (never `python`/`python3`). Set `PYTHONIOENCODING=utf-8`.
- Repo root: `C:/Users/willi/repos/tqit_soulvizier_classic`. Git remote `origin` =
  `github.com/wtrevena/tqit_soulvizier_classic`, branch `main`.
- The mod is a TQAE Custom Quest total conversion. It loads via TQAE main menu ->
  Play Custom Quest -> `SoulvizierClassic`. ALWAYS create a dedicated Custom Quest
  character to test; never load a mainline character into it (it corrupts them).
- Read-only tooling against the game: the Python tools decompress and rebuild
  archives; they never touch the live install except the deploy scripts.
- The built database currently holds **50,236 records** (`work/SoulvizierClassic/
  Database/SoulvizierClassic.arz`); the upstream SV 0.98i DB is the base it patches.

---

## 1. The content data model (the mental model)

TQ content lives in five kinds of container. Understand which one you are editing
before you touch anything.

| Container | Extension | Holds | Read/write tool |
|-----------|-----------|-------|-----------------|
| Database | `.arz` | compiled RECORDS (items, monsters, skills, loot tables, souls, pets, quests-rewards data) | `tools/arz_patcher.py` (`ArzDatabase`) |
| Asset archive | `.arc` | binary ASSETS: meshes `.msh`, textures `.tex`, sounds, and `.qst` quest files | `tools/arc_patcher.py` (`ArcArchive`) |
| Record source | `.dbr` | ArtManager TEXT source for one record (CRLF, `key,value,` lines) | loose files; compiled into `.arz` |
| Template | `.tpl` | the schema (field names + dtypes) a record conforms to | `<game>/Toolset/Templates.arc` (566 templates) |
| Text | `Text.arc` | display STRINGS keyed by tag (`modstrings.txt`, UTF-16LE) | `tools/build_text_arc.py` + `tools/arc_patcher.py` |

### 1.1 A record is `{ template, fields }`

Every record in the `.arz` has a **templateName** (which `.tpl` schema it follows,
e.g. `database\Templates\Jewelry_Ring.tpl`), a **Class** string (the engine class,
e.g. `ArmorJewelry_Ring`), and a bag of typed fields. There are exactly four field
dtypes (`tools/arz_patcher.py:15-18`):

```
DATA_TYPE_INT    = 0
DATA_TYPE_FLOAT  = 1
DATA_TYPE_STRING = 2
DATA_TYPE_BOOL   = 3
```

A field can be single- or multi-valued (arrays are common: tiered `[normal, epic,
legendary]` values, loot lists, skill lists). In code a field is a `TypedField`
(`arz_patcher.py:34`) with `.dtype` and `.values` (always a list).
`ArzDatabase.get_fields(rec)` returns an `OrderedDict[name -> TypedField]`; note keys
can carry a `###N` suffix for duplicate field names, so always compare on
`key.split('###')[0]` (this idiom is everywhere in the tools).

### 1.2 The mod DB is STACKED over the base game DB

In Custom Quest mode the game loads the base `<game>/Database/database.arz` FIRST,
then overlays the mod's `SoulvizierClassic.arz`. Consequences that drive everything:

- **Any base-game record resolves for free** even if it is absent from the mod DB.
  This is why the tools import base records rather than authoring them (Section 8.2):
  `_import_base_game_record` / `_import_boat_captain` / `_import_dialog_needed`
  (`build_svc_database.py:566,1201,1229`), and why a quest can reference a base NPC
  like `starting_storyteller.dbr` that the mod never defines.
- **The mod DB only needs the records it CHANGES or ADDS.** The build is
  minimal-touch: only modified records are decoded + re-encoded; everything else
  passes through as raw compressed bytes preserving the original exactly
  (`build_svc_database.py:1-14`).
- Lookups in a Custom Quest mod DB are **case-SENSITIVE** (TQIT was
  case-insensitive). SV records are stored lowercase but many were referenced with
  PascalCase; `fix_broken_mastery_skills` Phase 1 rewrites every `.dbr` reference to
  the exact stored path (`build_svc_database.py:837-873`). When you author a
  reference, match the stored case or it will silently fail to resolve.

### 1.3 Asset paths are archive-name-first

An asset path's FIRST path component is the `.arc` archive it lives in. Example:
`SVItems\jewelry\soul_n_icon.tex` resolves from `SVItems.arc`;
`drx\meshes\n_soulmesh.msh` from `drx.arc`; `Creatures\Monster\Skeleton\
RevenantFire.msh` from the base `Creatures`/xpack archives. If an icon shows as a
grey box or a mesh is invisible, the archive is missing or stripped (see the
`-LiteMode` trap, Section 11).

### 1.4 The build -> pack flow

One `scripts/bootstrap_working_mod.ps1` run assembles the whole mod under
`work/SoulvizierClassic/` in this order (verified against the script):

1. **DB**: `build_svc_database.py` produces `Database/SoulvizierClassic.arz` AND writes
   two sidecar files next to it: `uber_soul_tags.txt` (soul/legacy/extended tag list)
   and `uber_souls_report.md`.
2. **Assets**: copy upstream `.arc` files into `Resources/`, then STRIP the TQIT-era
   UI/engine archives + empties + PC-skin cosmetics, strip the whole `XPack/`
   subfolder, and write empty DLC-stub `.arc`s for XPack2/3/4 non-essential content
   (`bootstrap_working_mod.ps1:119-268`).
3. **Levels**: copy the merged `local/Levels_merged.arc` (or KEEP an existing
   `work/.../Levels.arc`; never clobber it with the SVAERA base). This is the
   MODDING_PLAYBOOK's territory.
4. **Text**: `build_text_arc.py` builds `Resources/Text.arc` (a single
   `modstrings.txt`) from SV 0.98i's `Text_EN.arc` + the Occult fixes + the
   `uber_soul_tags.txt` sidecar + `QUEST_INTEGRATION_TAGS`, then writes the
   `mod_authored_tags.txt` manifest, then `validate_tags.py` gates the build (fails
   loud if any mod tag the `.arz` references is missing from `Text.arc`).
5. **Quests**: `build_quest_files.py` restores the clean SVAERA `Quests.arc` and adds
   the ported SV area questlines at the archive root.
6. **Cleanup**: `dedupe_items_arc.py` removes files from `Items.arc` already present
   in `SVItems.arc`.

Deploy (`scripts/deploy_to_custommaps.ps1`) then copies `work/` into TQ's CustomMaps.
The exact commands are in Section 10.

---

## 2. The `.arz` record API (what the tools give you)

Everything below is `tools/arz_patcher.py`. You will use these five calls constantly.

- `db = ArzDatabase.from_arz(path)` - load a compiled DB.
- `db.has_record(path)` / `db.record_names()` - existence / iteration.
- `db.get_fields(rec) -> OrderedDict|None` - decode a record's fields.
- `db.get_field_value(rec, field)` - one field's first value (name-normalized).
- `db.set_field(rec, field, value, dtype=None)` - THE workhorse (details below).
- `db.clone_record(src, dst)` - deep-copy a record to a new path.
- `_ensure_record(db, path, template)` - create a BARE empty record with a template
  (defined identically in `apply_svc_patches.py:18` and `build_svc_database.py:500`;
  it seeds `_raw_records[path]=(id, b'')`, sets `_record_types[path]=template`, and an
  empty decoded cache).
- `db.write_arz(out)` - re-encode only the modified records, pass the rest through.

### 2.1 set_field and the dtype-preservation trap (the #1 content footgun)

`set_field` (`arz_patcher.py:221-258`) has two branches:

- If the field **already exists**, it overwrites `.values` and **keeps the existing
  dtype** UNLESS you pass an explicit `dtype`, in which case it FORCES that dtype.
- If the field is **new**, it INFERS the dtype from the Python value (`float ->
  FLOAT`, `str -> STRING`, `bool -> BOOL`, else `INT`).

**THE TRAP:** on a CLONED record, passing an explicit `dtype` that disagrees with how
the value is actually stored SILENTLY CORRUPTS the encoding. A FLOAT field written as
INT (or vice versa) re-encodes to a zeroed / garbage value, which for a pet manifests
as **the pet failing to spawn**. So:

- On a cloned/existing record, call `set_field(rec, name, value)` with **NO dtype** so
  the record's own dtype is preserved. This is exactly why `_set_pet_equipment`
  (`apply_svc_patches.py:303-317`) and `_update_existing_fields`
  (`apply_svc_patches.py:270-300`) deliberately omit dtype and only ever UPDATE
  existing fields.
- Pass an explicit dtype ONLY when you are AUTHORING a brand-new field on a
  freshly-`_ensure_record`ed record and you know the schema (the create paths in
  `create_uber_souls.py` and the loot-table builders do this correctly with
  `DATA_TYPE_STRING`/`INT`/`FLOAT`).
- To match a Python float to a FLOAT field, pass a real `float` (`5000.0`, not
  `5000`); to match an INT field pass an `int`. The inference in the new-field branch
  keys off the Python type.

### 2.2 clone_record and why it is BANNED for souls

`clone_record` (`arz_patcher.py:266-280`) deep-copies the source record's fields and
template to a new path. It is the right tool when you want a fully-populated record to
start from (a pet from Lyia; a portal NPC from the boat captain; a UI skill slot from
slot01). It is **the wrong tool for a soul**: cloning a soul drags along the source
soul's STAT values (character/offensive/defensive modifiers), and those baked stats
**corrupt saved items** because TQ bakes item properties at pickup (Section 11). For
souls, create a bare record with `_ensure_record` (or the direct
`_raw_records[...] = (id, b'')` + set the decoded cache pattern in
`create_uber_souls.py:614-619`) and set ONLY the fields you intend. This is the
`CLAUDE.md` rule "Never `clone_record` for souls" made concrete.

---

## 3. RECIPE: add a new ITEM (equipment / weapon / armor / jewelry)

An item is a record under `records\item\...` (or `records\drxitem\...`,
`records\xpack\item\...`) with an equipment template and a Class. Real example from
the built DB (a base bow):

```
records\item\equipmentweapon\bow\u_n_hornsofcyprus.dbr
  templateName = database\Templates\Weapon_Bow.tpl
  Class        = WeaponHunting_Bow
  bitmap       = Items\EquipmentWeapon\Bow\UIBitmaps\rbow01b.tex   (archive: Items)
  characterBaseAttackSpeedTag = CharacterAttackSpeedSlow
  ... hundreds of stat fields ...
```

### Steps

1. **Pick a template + Class.** The template defines the schema; the Class tells the
   engine what the item IS. Common equipment templates/classes the enchant pass
   recognizes (`build_svc_database.py:436-446`): templates `armor`, `weapon`,
   `shield`, `jewelry_ring`, `jewelry_amulet`, `jewelry_medal`, `itemrelic`;
   classes `armorprotective`, `armorjewelry`, `weaponmelee`, `weaponhunting`,
   `weaponmage`, `weaponstaff`, `shield`. Templates resolve automatically from
   `<game>/Toolset/Templates.arc` - you never place a `.tpl`.

   Full Class -> template map (verified against every record in the built
   `SoulvizierClassic.arz`, 50,236 records):

   | Class | Template | Notes |
   |-------|----------|-------|
   | `WeaponMelee_Sword` / `_Mace` / `_Axe` | `Weapon_Sword.tpl` / `Weapon_Mace.tpl` / `Weapon_Axe.tpl` | one-handed melee |
   | `WeaponMagical_Staff` | `Weapon_Staff.tpl` | two-handed caster weapon |
   | `WeaponHunting_Bow` / `_Spear` | `Weapon_Bow.tpl` / `Weapon_Spear.tpl` | ranged / polearm |
   | `ArmorProtective_Head` / `_UpperBody` / `_LowerBody` / `_Forearm` | `Armor_Head.tpl` / `Armor_UpperBody.tpl` / `Armor_LowerBody.tpl` / `Armor_Forearm.tpl` | body-slot armor |
   | `WeaponArmor_Shield` | `WeaponArmor_Shield.tpl` | off-hand shield |
   | `ArmorJewelry_Ring` / `_Amulet` / `_Bracelet` | `Jewelry_Ring.tpl` / `Jewelry_Amulet.tpl` / `Jewelry_Bracelet.tpl` | **souls are `ArmorJewelry_Ring`/`Jewelry_Ring.tpl`** (Section 5) |
   | `ItemRelic` | `ItemRelic.tpl` | relic-slot filler |
   | `ItemCharm` | `ItemCharm.tpl` | charm-slot filler |
   | `ItemArtifact` | `ItemArtifact.tpl` (or `ItemArtifactSupra.tpl`) | crafted artifact |
   | `ItemArtifactFormula` | `ItemArtifactFormula.tpl` | forge upgrade recipe (Section 10) |
   | `OneShot_Potion*` (e.g. `OneShot_PotionHealth`, `OneShot_PotionMana`) / `OneShot_Scroll` | matching `OneShot_*.tpl` | consumables |
   | `QuestItem` | `QuestItem.tpl` | quest-only, non-sellable item |

   Class is case-exact as written above; a couple of base-game records store
   `templateName` with a capitalized `Database\` vs lowercase `database\` drive
   prefix inconsistently - harmless, the engine resolves either.

2. **Create the record and set required fields.** Easiest path: `clone_record` an
   existing item of the same template and override with `set_field` (no dtype, to
   preserve the source's field dtypes), OR `_ensure_record(db, path, template)` then
   author each field with the correct explicit dtype. Minimum viable fields:
   `templateName` (STRING), `Class` (STRING), `bitmap` (STRING, the inventory icon),
   `mesh` (STRING, the world/ground mesh), plus the requirement fields
   (`levelRequirement`, `strengthRequirement`, `dexterityRequirement`,
   `intelligenceRequirement`) and `itemLevel`, and whatever stat modifiers define it
   (`offensivePhysicalMin/Max`, `characterStrengthModifier`, `defensiveProtection`,
   ...). Look at `_base_soul_fields` (`create_uber_souls.py:217-246`) for the exact
   boilerplate pattern of an item record built from scratch.

3. **Icon/mesh/texture path convention.** Archive-name-first (Section 1.3). If you add
   a new texture/mesh, it must live in an `.arc` the mod ships (add it to `SVItems.arc`
   /`drx.arc` etc.); if you reference a base-game asset, use its base path. A missing
   asset = grey box / invisible.

4. **Name and description tags.** `itemNameTag` (STRING) points at a `Text.arc` tag
   for the item's displayed name; `description`/`itemText` similarly. Author those
   strings into `Text.arc` (Section 8). Base items reuse base tags (e.g. the merc
   scroll's `description = tagMercScroll1` resolves from base text); NEW mod items need
   NEW mod tags that you add to the tag pipeline or the item shows the raw `tag...`
   string in-game and the `validate_tags.py` gate FAILS the build.

5. **Make it enchantable (relic slot).** `make_enchantable`
   (`build_svc_database.py:421-497`) sets `numRelicSlots = 1` on any equipment/soul
   with 0 slots (it skips `cannotPickUp==1` records and anything already >= 1 slot).
   If you author an item and want a relic slot, set `numRelicSlots` (INT) to 1
   yourself, or rely on this pass (it runs unconditionally in the build).

6. **Verify it resolves.** Rebuild the DB (Section 10) and confirm with a probe:
   `db.get_fields(<your path>)` returns the fields, `db.get_field_value(<path>,
   'itemNameTag')` is defined in `Text.arc`, and the referenced `bitmap`/`mesh`
   archives are shipped. Then it must actually DROP (Section 4) to be reachable.

---

## 4. RECIPE: add an item to LOOT (make it actually drop)

There are TWO drop mechanisms in play. Pick by what you are wiring.

### 4.1 Classic loot tables (chests, merchants, forge formulas, scroll pools)

A loot table is a record whose Class is a `LootItemTable_*`. The workhorse is
`LootItemTable_FixedWeight` (`database\Templates\LootItemTable_FixedWeight.tpl`): a
list of `lootName{i}` (STRING = item DBR path) paired with `lootWeight{i}` (INT =
relative weight; 0 disables the slot). Real example from the built DB:

```
records\item\loottables\mercscrolls\01_n_mercscrolls.dbr
  templateName = database\Templates\LootItemTable_FixedWeight.tpl
  Class        = LootItemTable_FixedWeight
  lootName1    = records/item/artifacts/n_mercscroll_euanthe.dbr
  lootWeight1  = 100
  lootName2    = records/item/artifacts/n_mercscroll_scyrna.dbr
  lootWeight2  = 100
  ...
```

To ADD an item to an existing table, find the highest existing `lootName{N}` slot and
write slot `N+1` (both `lootName` and `lootWeight`). This is exactly
`add_blood_mistress_to_loot` (`apply_svc_patches.py:2719-2762`): it scans
`forgeformulas`+`drop`+`loottable` tables, computes `max_slot`, and appends the
formula at `max_slot+1` with weight 50. To REPLACE a table's contents wholesale, write
`lootName{i}`/`lootWeight{i}=100` for i in 1..K and ZERO out `lootWeight{i}` for
i>K up through the template's slot count (30) so stale higher slots do not leak, as
`cascade_merc_scrolls` does (`apply_svc_patches.py:2705-2709`).

Loot tables are referenced BY OTHER records: a chest's `loot{n}Name{i}` +
`loot{n}Weight{i}` + `loot{n}Chance` fields (see `grant_all_inventory_bags`
wiring the tutorial chest, `build_svc_database.py:551-558`), a monster's loot slots,
or a forge-formula drop pool. `loot{n}Chance` (FLOAT %) gates whether slot group N
rolls at all; the `lootName`/`lootWeight` inside pick which item.

There is a second field-set site for the equip-drop mechanism worth knowing:
`_wire_soul_to_monster` (`apply_svc_patches.py:2841-2850`) is the general-purpose
helper version of `_set_soul_drop` (Section 4.2) - same four fields
(`lootFinger2Item1`, `chanceToEquipFinger2`, `chanceToEquipFinger2Item1`,
`dropItems`), used by the extended-patches pass when wiring souls the fuzzy matcher
missed.

**The four loot-table Classes, all verified present in the built DB (50,236-record
tally):**

| Class | Count in DB | Shape | Use |
|-------|-------------|-------|-----|
| `LootMasterTable` | 1,963 | table-of-tables: `lootName{i}`/`lootWeight{i}` where each `lootName{i}` points at ANOTHER loot table (not necessarily a direct item) | the top-level table a chest/merchant/monster references; fans out into category sub-tables |
| `LootItemTable_FixedWeight` | 3,431 | `lootName{i}`/`lootWeight{i}` = direct item DBR paths + fixed weights (the example above) | a fixed pool of specific items (scrolls, unique formulas, set pieces) |
| `LootItemTable_DynWeight` | 580 | `itemNames` (the candidate pool, one field with multiple values), `minItemLevelEquation`/`maxItemLevelEquation`/`targetLevelEquation` (string formulas evaluated at drop time, e.g. `"69 * 1"` / `"((8 + parentLevel) / 1.6) * (1+(averagePlayerLevel/625))"`), `prefixRandomizerChance`/`suffixRandomizerChance` (FLOAT, wires into the affix system below) | procedural drops: base-game gear tables that scale by area/player level and roll affixes |
| `LootRandomizerTable` | 1,239 | `randomizerName{i}` (points at a `LootRandomizer` affix record) + `randomizerWeight{i}` | a weighted pool of possible affixes for one slot (e.g. relic bonus pool `01_froststone.dbr`) |
| `LootRandomizer` | 2,406 | one single affix: `lootRandomizerName` (a **Text.arc tag**, e.g. `tagNewAffix1` - scanned by `validate_tags.py`, Section 9.4) + `lootRandomizerCost`/`lootRandomizerJitter` + the actual stat-modifier fields it grants | the leaf affix record referenced from a `LootRandomizerTable` |

Item sets, relics, charms, and monster-infrequents (MIs) are all just items placed in
`LootMasterTable`/`LootItemTable_FixedWeight` tables the same way as any item; there is
no special mechanism beyond the table + the item's own template. **Affixes
(prefix/suffix) are entirely base-game:** this mod authors NO new
`LootRandomizerTable`/`LootRandomizer` records (grepped across every `tools/*.py` build
pass - only a read-only diagnostic, `diagnose_loot_contents.py`, and the
`validate_tags.py` tag-scan touch those fields). New/ported items simply inherit
whatever `prefixRandomizerChance`/`suffixRandomizerChance` wiring their
`LootItemTable_DynWeight` parent already has; this mod's chosen customization lever is
enchanting via relic slots instead (Section 10).

### 4.1a Merchants (shop inventory)

A merchant is a record whose template is `database\Templates\Market.tpl` - note it has
**NO `Class` field** (verified: none of the 186 `Market.tpl` records in the built DB
carry one; `templateName` alone identifies it as a merchant). Real example from the
built DB (`records\item\merchants\greece\copy of 01_market_athens_mage.dbr`, a caster
merchant):

```
templateName             = database\Templates\Market.tpl
marketHelmTable1         = records/item/merchants/merchantloottables/head/caster_11-13.dbr
marketHelmTable2..4      = (progressively higher-level caster helm tables)
marketRingTable1..4      = records/item/merchants/merchantloottables/jewelry/ring_11-13.dbr ...
marketSwordTable1..4     = records/item/merchants/merchantloottables/weapons/1h_sword_07-09.dbr ...
marketStaffTable1..4, marketMaceTable1..4, marketScrollTable1..4, ...  (one per category)
marketNumHelmMin/Max     = 5 / 6              (how many items of this category roll)
marketNumRingMin/Max     = 14 / 18
marketPlayerLevel        = [13, 14, 16]       ([normal, epic, legendary] level tuning)
marketRefreshTimeMin/Max = 10.0 / 10.0        (hours before restock)
marketHealthPotion       = records/item/miscellaneous/oneshot/potionhealth_02.dbr
marketManaPotion         = records/item/miscellaneous/oneshot/potionmana_02.dbr
```

Each `market<Category>Table{1..4}` (Helm/Ring/Sword/Staff/Mace/Bow/Amulet/Bracelet/
Scroll/Shield/Spear/Axe/BodyArmor/Greaves/...) points at a per-category loot table -
almost always a `LootMasterTable` or `LootItemTable_*` (the same table Classes as
Section 4.1), which chain into the same base loot tables the rest of the game uses.
The 1/2/3/4 suffix is a difficulty/tier ladder (not strictly normal/epic/legendary -
some tiers repeat the same table, e.g. `marketHelmTable2`/`3` both point at
`caster_13-15.dbr` above), and `marketNum<Cat>Min/Max` caps how many roll per restock.

**To add an item to a shop:** add it to the loot table that the merchant's
`market<Category>Table{N}` points at (the append-at-`N+1` recipe, Section 4.1) - do
NOT edit the merchant record itself unless you are changing which table/category it
stocks or the roll counts.

### 4.2 The AE equip-drop mechanism (how SOULS drop) - IMPORTANT, not a loot table

Souls do NOT drop via a loot table. They ride the monster's EQUIPMENT slots. AE
resolves a monster's Finger2 slot as an equipped ring, and if `dropItems=1` the
equipped ring drops on death. Real example from the built DB:

```
records\creature\monster\questbosses\boss_chinatelkine_ormenos_38.dbr
  lootFinger2Item1          = [ormenos_soul_n.dbr, ormenos_soul_e.dbr, ormenos_soul_l.dbr]
  chanceToEquipFinger2      = 100.0   (FLOAT: overall % to equip/drop from Finger2)
  chanceToEquipFinger2Item1 = 100     (INT: weight for selecting lootFinger2Item1)
  dropItems                 = 1
  monsterClassification     = Boss
```

The three-element `lootFinger2Item1` array is the `[normal, epic, legendary]` soul
variant; the engine picks by current difficulty. The exact field-set writer is
`_set_soul_drop` (`build_svc_database.py:293-309`): it sets `chanceToEquipFinger2`
(FLOAT %), `chanceToEquipFinger2Item1=100` (INT), and ensures `dropItems=1`. This is
the AE-compatible replacement for TQIT's `lootFinger2Chance`, which AE ignores (see
the analysis tool `check_ae_loot_mechanism.py`).

**Which monsters get souls:** only `Hero`, `Boss`, or `Quest`
`monsterClassification` (never `Common`/`Champion`/`um_` minions);
`wire_souls_to_monsters` (`build_svc_database.py:248-418`) fuzzy-matches a soul name
to the monster's cleaned filename and wires the three variants. **Drop rate policy:**
farmable act bosses get 25%, everything else (heroes/quests/uber `um_` encounters)
gets 66% (`_is_farmable_boss`, `build_svc_database.py:273-291`). Some bosses the fuzzy
matcher misses are wired explicitly by name in `_wire_missing_boss_souls`
(`apply_svc_patches.py:825-...`, e.g. Ormenos/Aktaios/Megalesios/Typhon).

### 4.3 The 100%-drop TESTING flag vs release rates (release-blocker)

By DEFAULT the build FORCES every soul-carrying monster to a 100% drop rate for
testing. `_force_100_pct_soul_drops` (`apply_svc_patches.py:3391-3415`) overwrites
`chanceToEquipFinger2=100.0`, `chanceToEquipFinger2Item1=100`, `dropItems=1` on every
`creature` record whose `lootFinger2Item1` mentions a soul. It is called by
`apply_all_extended_patches(force_full_drops=...)` (`apply_svc_patches.py:4381-4384`),
which `build_svc_database.py:1428-1443` wires to the `SVC_RELEASE_DROPS` env var:

- **unset / `0` / `false` / anything unrecognized** -> `force_full_drops=True` ->
  **100% drops (TESTING)**. An unrecognized value WARNs loudly but still defaults to
  testing, so a typo cannot silently ship a release build with wrong rates.
- **`SVC_RELEASE_DROPS=1`** (or `true`/`yes`/`on`) -> `force_full_drops=False` -> the
  tuned **66% / 25%** rates are kept.

**RELEASE MUST set `SVC_RELEASE_DROPS=1`.** Shipping with 100% drops on is a known P0
(`CLAUDE.md` content gaps). Testing in-game is done with 100% on so souls are easy to
see.

---

## 5. RECIPE: add / modify a SOUL (this mod's signature item -> pet)

A soul is a jewelry ring item that, when equipped, grants an item skill (often a
summon) plus stat/skill augments. It is the mod's centerpiece. Two authoring paths.

### 5.1 The soul record shape (verified from the built DB)

A generated soul (`create_uber_souls.py`) looks like:

```
records\item\equipmentring\soul\svc_uber\possessedboar_soul_n.dbr
  templateName    = database\Templates\Jewelry_Ring.tpl
  Class           = ArmorJewelry_Ring
  bitmap          = SVItems\jewelry\soul_n_icon.tex      (archive: SVItems)
  mesh            = drx\meshes\n_soulmesh.msh            (archive: drx)
  itemCostName    = records/game/itemcost_soul.dbr
  numRelicSlots   = 1
  itemLevel       = 10
  levelRequirement= 5
  itemNameTag     = tagSoulSVC9000                       (Text.arc tag, {^F} prefixed)
  itemSkillName   = records\skills\soulskills\thunderballnova.dbr
  itemSkillLevel  = 1
  itemSkillAutoController = records\xpack\ai controllers\autocast_items\basetemplates\base_atenemy_onattack.dbr
  augmentSkillName1 = records\skills\storm\drxstormsurge.dbr
  augmentSkillLevel1 = 1
  characterStrength = 15
  offensiveLightningMin/Max = 6.0 / 9.6
  ...
```

Key facts, all verified:
- Template `database\Templates\Jewelry_Ring.tpl`, Class `ArmorJewelry_Ring`
  (`create_uber_souls.py:25-26`).
- Icon `SVItems\jewelry\soul_{n,e,l}_icon.tex`, mesh `drx\meshes\n_soulmesh.msh`
  (`create_uber_souls.py:27-28`). If a soul shows a grey box, its `bitmap` points at
  the broken `Items\miscellaneous\{n,e,l}_soul.tex` path; `fix_soul_bitmaps`
  (`build_svc_database.py:1325-1358`) rewrites those to the `SVItems` paths - it runs
  at the END of the build, so any soul you add is covered.
- The **name tag string** MUST be prefixed with `{^F}` for the pink/magenta soul
  color, e.g. `{^F}Possessedboar Soul` (`create_uber_souls.py:575`;
  `apply_svc_patches.py:4306-4347` for the hand-authored souls). The `{^F}` goes in
  the Text.arc VALUE, not in the field.
- `itemSkillName` = the granted-on-equip skill (a summon, a proc, a nova);
  `itemSkillAutoController` = the autocast controller that fires it (on-attack /
  on-hit / on-equip templates listed at `apply_svc_patches.py:30-36`).
  `augmentSkillName{1,2}` + `augmentSkillLevel{1,2}` = passive +levels to the player's
  own skills.

### 5.2 Authoring a NEW soul - the exact path (and the traps)

- Create the record BARE, never by cloning another soul (Section 2.2). Use
  `_ensure_record(db, path, 'database\\Templates\\Jewelry_Ring.tpl')` (or the direct
  seed pattern in `create_uber_souls.py:614-619`), then `set_field` each field with
  its correct explicit dtype (STRING for paths/tags, INT for levels, FLOAT for
  offensive min/max).
- Set the base boilerplate from `_base_soul_fields` (`create_uber_souls.py:217-246`):
  `templateName`, `Class`, `bitmap`, `mesh`, `itemCostName`, `dropSound*`,
  `itemClassification=Magical`, `numRelicSlots=1`, `itemLevel`, `levelRequirement`.
- Author THREE variants (`_soul_n`, `_soul_e`, `_soul_l`) scaled by difficulty. The
  generated pipeline scales stats N=60% / E=80% / L=100% and does NOT scale identity /
  skill / string / boolean fields (the `_NO_SCALE` set at
  `create_uber_souls.py:581-590`).
- Give it a NEW name tag. The generated pipeline uses `tagSoulSVC{counter}` starting
  at **9000** (`create_uber_souls.py:455,571`); hand-authored souls use
  `tagSVCSoul<Name>` (`apply_svc_patches.py:4306+`). Emit the `tag=value` (with `{^F}`
  in the value) so `build_text_arc.py` folds it into `Text.arc` and
  `validate_tags.py` passes. Missing tag => raw text in-game + build-gate FAIL.
- Wire it to a monster's drop (Section 4.2): set the monster's
  `lootFinger2Item1=[n,e,l]`, `chanceToEquipFinger2` (66 or 25), and
  `chanceToEquipFinger2Item1=100`, `dropItems=1`.
- If the soul's `itemSkillName` is a SUMMON, build the summon skill + pet (Section 6).

**Reference soul to copy field ideas from (NOT to clone):**
`records\item\equipmentring\soul\skeleton\boneash_soul_n.dbr` (the designated clone
source used by `create_uber_souls.py:33` for its RENDER fields only; it has all
template fields pre-populated so the icon/mesh render correctly). For a SUMMON soul's
pet, the reference is **Lyia Leafsong** (Section 6).

---

## 6. RECIPE: add a PET / summon

A soul summon = a `Skill_SpawnPet` skill that spawns one or more `Pet` records. Both
are DB records; the soul's `itemSkillName` points at the skill.

### 6.1 The Pet.tpl vs Monster.tpl crash rule (hard lesson, made concrete)

A pet MUST use `Database\Templates\Pet.tpl` (Class `Pet`), NOT a Monster template.
Copying ANY equipment or loot field FROM a Monster.tpl record INTO a Pet.tpl record
CRASHES the game - even merely changing the value of an existing shared field via a
dtype-overwriting copy. Only ANIMATION and SKILL fields are safe to copy from the
source monster. This is why the pet builders (`_create_rakanizeus_pet_skill` etc.,
`apply_svc_patches.py:320+`):

- CLONE the pet from **Lyia Leafsong** (`records\skills\soulskills\pets\
  lyialeafsong_{1,2,3}.dbr`), which is already a valid permanent `Pet` with full
  equipment/skills/all required Pet.tpl fields, so the clone inherits a correct Pet
  schema (`apply_svc_patches.py:331-335`).
- Copy ONLY animation fields (`_copy_animation_fields`, matches `Anim`/`anim` in the
  field name, `apply_svc_patches.py:217-261`) and ONLY UPDATE existing skill fields
  (`_update_existing_fields` with `_SKILL_PREFIXES`, never adding new fields,
  dtype-preserving, `apply_svc_patches.py:270-300`) from the real monster.
- Set equipment via `_set_pet_equipment` (`apply_svc_patches.py:303-317`) with
  HARDCODED item paths and NO dtype (preserving the cloned field dtypes), NEVER by
  copying the monster's equipment fields.

### 6.2 Permanent pets (the TTL trick)

A soul pet should be permanent (no despawn timer). The trick: the summon skill must
NOT carry a `spawnObjectsTimeToLive` field (equivalently, set it to `[]`). Verified:
the built `records\skills\soulskills\summon_rakanizeus.dbr` has `spawnObjects` (the 3
pet paths) but NO `spawnObjectsTimeToLive` at all. Because the summon is CLONED from
Lyia's already-permanent `summon_lyia.dbr` (`apply_svc_patches.py:444-452`), the
permanence is inherited for free. If you build a summon from scratch instead, ensure
you do not add a TTL field. This is the `CLAUDE.md` rule "remove `spawnObjectsTimeToLive`
(set to `[]`). Reference soul: Lyia Leafsong" made concrete.

### 6.3 The summon skill shape (verified)

```
records\skills\soulskills\summon_rakanizeus.dbr
  templateName    = database\Templates\Skill_SpawnPet.tpl
  Class           = Skill_SpawnPet
  isPetDisplayable= 1
  skillDisplayName= tagSVCSummonRakanizeus          (Text.arc tag)
  skillManaCost   = [300.0, 350.0, 400.0]           (per-level FLOAT array)
  spawnObjects    = [rakanizeus_1.dbr, _2.dbr, _3.dbr]
  skillUpBitmapName / skillDownBitmapName = DRXtextures\skill icons\scroll\...tex
  (NO spawnObjectsTimeToLive -> permanent)
```

### 6.4 Pet record shape (verified)

```
records\skills\soulskills\pets\rakanizeus_1.dbr
  templateName = Database\Templates\Pet.tpl
  Class        = Pet
  mesh/scale/charLevel/characterLife/... (identity + stats)
  chanceToEquipLeftHand = 100.0 ; chanceToEquipLeftHandItem1 = 5000 ; lootLeftHandItem1 = [N,E,L]
  chanceToEquipForearm  = 100.0 ; lootForearmItem1 = [...]
  chanceToEquipFinger1  = 100.0 ; lootFinger1Item1 = [...]
  dropItems    = 0    (pet gear does NOT drop when the pet dies)
  giveXP = 0 ; experiencePoints = 0
  StatusIcon / StatusIconRed = party-UI icons
  controller   = records\skills\spirit\drxpet\drxpet_controllers\controller_skelly_aggressive.dbr
```

### Steps to add a summon soul pet

1. Clone the 3 pet records from Lyia (`lyialeafsong_{1,2,3}.dbr`); copy animations +
   update skills from the real source monster; override identity (mesh, scale,
   description tag, `characterRacialProfile`, `controller`) and stats via `set_field`
   with NO dtype. Set `dropItems=0`, `giveXP=0`, `experiencePoints=0`.
2. Set equipment with `_set_pet_equipment` (hardcoded `[N,E,L]` item paths per slot,
   `chanceToEquip<Slot>=100.0`, `chanceToEquip<Slot>Item1=5000`).
3. Clone the summon skill from `summon_lyia.dbr` (inherits permanence); set
   `spawnObjects` = the 3 pet paths, `isPetDisplayable=1`, `skillDisplayName` (a mod
   tag), `skillManaCost` (3-element FLOAT array), the up/down bitmaps.
4. Point the soul's `itemSkillName` at the summon skill (and set per-variant
   `itemSkillLevel` N=1/E=2/L=3, `apply_svc_patches.py:465-473`).
5. Author the summon's display-name tag and the pet's `description` tag into `Text.arc`.

---

## 7. RECIPE: add a QUEST

`tools/qst_format.py` is a fully reverse-engineered `.qst` reader/writer/spec (89/89
byte-identical round-trip; full format spec at `tools/qst_format.py:1-97`). A `.qst`
is a binary file stored INSIDE `Quests.arc`, not a DB record.

### 7.1 The .qst tree

`parse(data)` returns a nested tree (`tools/qst_format.py:300-307`):
`('block', sub_items)` / `('field', key, ('int'|'str', val))`. High-level dataclasses
`Quest`/`QuestStep`/`Trigger`/`Condition`/`Action` + `build_quest()` let you author
one; `serialize()` round-trips a parsed tree. Structure (spec at file top):

```
Quest Header block:  title, reward fields (Section 8)
Steps container:     max = N steps
  per step:
    Step definition block: name, nextTaskDescription
    Trigger container block: max = M triggers
      per trigger: [trigger_header] [conditions] [actions]
    Sentinel trigger block (always present, no max)
```

A trigger fires its ACTIONS when its CONDITIONS are met. Trigger header fields:
`displayTag, displayBitmap, comments, isActive, bRatchet`.

**Parse quirk:** `parse()` renders every int32 as UNSIGNED. Normalize when comparing
signed values, e.g. negative teleport coords: `Action_BoatDialog`'s `x/y/z` are signed
int32 stored as uint32 two's-complement (`tools/qst_format.py:93-97,466-468`) - e.g. a
coordinate of `-2317` parses back as `0xFFFFF6F3` (4294964979 unsigned), not `-2317`;
compare against the two's-complement form or convert back before comparing. The
builder writes `x/y/z` as signed (`_build_action`, line 585-586); everything else in
`INT_FIELDS` (line 113-133) writes as raw uint32, and `delayTime`/`fadeTime` are IEEE
754 floats stored as uint32 bits. Two helpers exist for AUTHORING (not needed for
parsing, which always hands back the raw uint32): `signed_to_uint32(i)` (line 466-468,
two's-complement encode) for signed coordinate fields, and `float_to_uint32(f)` (line
461-463, IEEE 754 bit-reinterpret) for `delayTime`/`fadeTime`-style float fields.

### 7.2 The full condition + action vocabulary (the quest verbs)

Every CONDITION shares `comments, isNot, isResettable, isQuestCritical` (+
`isQuestCritical2` except `Condition_CounterState`). Condition classes and their extra
fields (`tools/qst_format.py:139-155`):

| Condition | Fields | Meaning |
|-----------|--------|---------|
| `Condition_AnimationCompleted` | characterRecord, idTag | an NPC finished an animation |
| `Condition_CharacterHasItem` | itemName | player holds an item |
| `Condition_ConversationStart` | personRecord | talked to an NPC |
| `Condition_CounterState` | name, mode, value | a named counter reached a state |
| `Condition_EnterVolume` | volumeRecord, entityRecord | entered a trigger volume |
| `Condition_ExitVolume` | volumeRecord | left a trigger volume |
| `Condition_GotToken` | tokenName | received a trigger token |
| `Condition_KillAllCreaturesFromProxy` | proxyRecord | cleared every spawn of a proxy |
| `Condition_KillCreature` | creatureRecord | killed a specific creature |
| `Condition_MoveCompleted` | characterRecord, idTag | an NPC finished a scripted move |
| `Condition_OnLevelLoad` | (none) | fires when the level streams in |
| `Condition_OnQuestComplete` | questFile | another quest finished |
| `Condition_OwnsTriggerToken` | tokenName | currently holds a token |
| `Condition_PickupItem` | itemRecord | picked up an item |
| `Condition_UseFixedItem` | itemRecord | used a fixed-world item |

Every ACTION shares `comments, delayTime`. Action classes and their extra fields
(`tools/qst_format.py:160-217`):

| Action | Fields |
|--------|--------|
| `Action_BestowTriggerToken` | tokenName |
| `Action_BoatDialog` | npc, onOff, x, y, z, tag  (teleports player to raw world x,y,z) |
| `Action_ClearMapMarker` | doSound |
| `Action_ClearNPCDialog` | npc |
| `Action_CloseDoor` | door, canReFire, bAlwaysClose |
| `Action_CompleteQuestNow` | questFile |
| `Action_CounterUpdate` | name, mode, value |
| `Action_DebugText` | debugText |
| `Action_DisableProxy` | proxy |
| `Action_DispenseItemFromNpc` | npc, item[0..2], canReFire, isPerPartyMember |
| `Action_FadeOutEventMusic` | timeInSecs |
| `Action_FireSkill` | skill, source, target, location, allowInterruptions, isQuestSkill, useActionTarget |
| `Action_GiveAttributePoints` | attributeAmount[0..2], region, locationTag, titleTag |
| `Action_GiveExp` | experiencePts[0..2], region, locationTag, titleTag |
| `Action_GiveItem` | item[0..2], num[0..2], region, locationTag, titleTag |
| `Action_GiveMoney` | moneyAmount[0..2], region, locationTag, titleTag |
| `Action_GiveSkillPoints` | skill, skillAmount[0..2], region, locationTag, titleTag |
| `Action_HideNpc` | npc, canReFire, fadeTime, fade |
| `Action_IlluminateNpc` | npc, type |
| `Action_KillCreature` | creatureRecord, canReFire |
| `Action_LoadEventMusic` | playlist |
| `Action_LockFixedItem` | fixedItem |
| `Action_NpcPlayAnimation` | npc, animation, allowInterruptions, looping, idTag |
| `Action_OpenDoor` | door, canReFire |
| `Action_OpenDynGridEntrance` | dynGridEntranceName, canReFire  (reveal a closed cave mouth) |
| `Action_OrientNPC` | npc, location, canReFire |
| `Action_Play3DSound` | entity, soundEffect |
| `Action_PlaySoundEffect` | soundEffect |
| `Action_RemoveItemFromInventory` | itemName |
| `Action_RemoveTriggerToken` | tokenName |
| `Action_ResetTrigger` | name |
| `Action_RunDelayedProxy` | proxy |
| `Action_ScreenShake` | amplitude, duration |
| `Action_SendTutorialEvent` | index |
| `Action_SetCharacterInvincible` | npc, invincible, canReFire |
| `Action_SetTimeOfDay` | timeOfDay, enableTimeProgression |
| `Action_ShowNpc` | npc, canReFire, fadeTime, fade |
| `Action_SpawnEntityAtLocation` | entity, location |
| `Action_TaskCreatureToLocation` | creature, location, fight, idTag, canReFire |
| `Action_UnlockFixedItem` | fixedItem, canReFire |
| `Action_UpdateDialogTab` | dialogPak |
| `Action_UpdateJournalEntry` | region, locationTag, titleTag, fullTextTag, doComplete, doSound |
| `Action_UpdateMapMarker` | bulletPointTag, descriptionTag, doComplete, doSound |
| `Action_UpdateNPCDialog` | npc, dialogFile  (makes an NPC clickable; needs Dialog Needed.dbr) |

Ready-made builders (`make_*`, `tools/qst_format.py:596-687`) cover the common ones:
`make_on_level_load_condition`, `make_kill_creature_condition`,
`make_kill_all_from_proxy_condition`, `make_enter_volume_condition`,
`make_character_has_item_condition`, `make_owns_trigger_token_condition`,
`make_show_npc_action`, `make_unlock_fixed_item_action`,
`make_open_dyn_grid_entrance_action`, `make_update_npc_dialog_action`,
`make_boat_dialog_action`, `make_spawn_entity_action`, `make_open_door_action`,
`make_bestow_token_action`.

**GAP: no reward-granting `make_*` helpers exist.** That is 6 condition helpers + 8
action helpers = 14 total (verified: `grep -c "^def make_" tools/qst_format.py` = 14),
and NONE of the 8 action helpers cover `Action_GiveItem`, `Action_GiveExp`,
`Action_GiveMoney`, `Action_GiveSkillPoints`, or `Action_GiveAttributePoints`.
Authoring a reward today means dropping to the raw form directly:
```python
Action('Action_GiveItem', fields={
    'item[0]': '<normal-tier item or LootMasterTable dbr>',
    'item[1]': '<epic-tier>', 'item[2]': '<legendary-tier>',
    'num[0]': '1', 'num[1]': '1', 'num[2]': '1',
    'region': '', 'locationTag': 'tagYourPopupLocation', 'titleTag': 'tagYourPopupTitle',
})
```
**Recommended future improvement:** add `make_give_item_action`,
`make_give_exp_action`, `make_give_money_action`, and
`make_give_skill_points_action` to `tools/qst_format.py` alongside the existing 14,
mirroring their signature style (keyword-only tiers with sane defaults, e.g.
`make_give_item_action(item_normal, item_epic=None, item_legendary=None, num=1, *,
region='', location_tag='', title_tag='', delay=0.0)`), so reward-granting triggers
stop needing the raw `Action(...)` form.

### 7.3 Port an existing questline (the cheap path) - PREFERRED

If the map's QUESTS section already registers the quest NAME and the level blobs
already place its trigger volumes / proxies / doors / portals, then adding the
questline is a **Quests.arc-only change with NO map rebuild**. This is how `urder`,
`widowletter`, `bossarena` were integrated (`build_quest_files.py:53-61`):

1. Copy the upstream `.qst` byte-for-byte from `upstream\soulvizier_098i\Resources\
   XPack\Quests.arc` and add it to the mod's `Quests.arc` at the **ARCHIVE ROOT**
   (basename only - the engine strips the folder prefix and resolves at root;
   `build_quest_files.py:47-52,209-224`, `arc.add_file(name, data)`). Assert it
   round-trips through `qst_format` before shipping (`_assert_roundtrip`, line 123).
2. Confirm every record + text tag the quest references resolves in the built `.arz`
   / `Text.arc`. If a referenced NPC/record was dropped by the merge, either restore
   the record (import from base, Section 8.2) or surgically neutralize just that
   trigger (7.5).
3. Rebuild `Quests.arc` via `build_quest_files.py`; it reopens the arc and verifies
   each added quest round-trips byte-exact (`build_quest_files.py:272-282`).

### 7.4 Author a NEW quest

Build a `Quest` object with `QuestStep`/`Trigger` + the `make_*` helpers,
`build_quest()` it, and `arc.add_file()` it into `Quests.arc` at the root (see the
`_make_combined_portal_quest` example, `build_quest_files.py:81-98`, and the self-test
that reconstructs `typhonportal.qst`/`bossarena.qst` byte-exact,
`qst_format.py:716-795`). A genuinely NEW quest NAME must ALSO be registered in the
map's QUESTS section and its trigger volumes/proxies placed in the level blobs - that
IS a map rebuild (MODDING_PLAYBOOK Section 6b). Reusing an already-registered name
avoids the rebuild.

### 7.5 Surgically neutralize a broken trigger

To drop ONE trigger that references a lost record without disturbing the rest of a
ported quest, follow `_neutralize_bloodcave_entry_step` (`build_quest_files.py:132-206`):
parse `tree = [header_block, steps_container]`; the steps container holds flat triples
per step `(stepdef, trigger_container, sentinel)`; a trigger container holds a `max`
field then flat triples per trigger `(trigger_header, conditions, actions)`; find the
trigger whose ACTIONS block mentions the dead record, DROP that triple, DECREMENT the
container's `max`, re-serialize, and assert the reference is gone and the file still
round-trips. This is exactly how the lost `starting_storyteller.dbr` trigger was
removed while keeping the rest of `open_bloodcave_portal.qst` byte-identical.

### 7.6 Fragility warnings (read before using a quest for movement)

- **Quest step STATE bakes into character saves.** Changing step structure can strand
  an existing save mid-quest.
- The `REPEAT_STEPS = 200` `OnLevelLoad` idiom (`build_quest_files.py:33`) broke
  in-game TWICE. Avoid it for anything load-bearing.
- **Do NOT use a quest to get the player into a persistent area.** Use the
  engine-native cave-mouth / grid-seam mechanisms (MODDING_PLAYBOOK Section 2). The
  entire blood-cave boat-dialog entrance was ripped out for this reason;
  `PORTALS = []` is now empty (`build_quest_files.py:37-44`) and
  `sv_commonmechanics.qst` is left as the clean SVAERA original. Reserve quest
  teleports (`Action_BoatDialog`) for genuine scripted events (a shrine warp, a boss
  arena), targeting an ON-MESH cell (MODDING_PLAYBOOK Section 7).

---

## 8. RECIPE: QUEST REWARDS

Quest rewards come in two forms: HEADER rewards (granted on quest completion) and
in-step `Action_Give*` rewards (granted when a trigger fires).

### 8.1 Header reward fields (Quest completion payout)

The Quest header block carries these reward fields (`tools/qst_format.py:31-44,
481-501`; dataclass `Quest`, line 442-458):

| Field | Type | Meaning |
|-------|------|---------|
| `rewardItemTag` | str | item(s) to grant, by tag (or `localRewardItemTag` for scripted scenes) |
| `rewardGold` | int | gold (or `localRewardGold`) |
| `rewardXP` | int | experience (or `localRewardXP`) |
| `rewardSkill` | int | skill points |
| `rewardAttr` | int | attribute points |
| `this->rewardItemTag[1]`, `this->rewardGold[1]`, `this->rewardXP[1]` | str/int/int | second reward set |
| `this->rewardItemTag[2]`, `this->rewardGold[2]`, `this->rewardXP[2]` | str/int/int | third reward set |

`Quest.use_local_rewards=True` switches the first set to the `localReward*` spellings
(used by scripted-scene quests). `build_quest()` writes all of these in the header
regardless (line 481-502), so a plain quest with all-zero rewards is valid.

### 8.2 In-step item/xp/money/skill/attribute rewards

Inside a trigger's ACTIONS you can grant on-the-fly with (all take a 3-element
`[normal, epic, legendary]` array + a `region`/`locationTag`/`titleTag` for the popup):
`Action_GiveItem` (item[0..2], num[0..2]), `Action_GiveExp` (experiencePts[0..2]),
`Action_GiveMoney` (moneyAmount[0..2]), `Action_GiveSkillPoints` (skill,
skillAmount[0..2]), `Action_GiveAttributePoints` (attributeAmount[0..2]). The
`locationTag`/`titleTag` are Text.arc tags shown in the reward popup - if they are raw
placeholders the popup shows the literal `tag...` string. Real example: the blood-cave
interior quest's hidden-chest `Action_GiveItem` left `locationTag`/`titleTag` as
`tagLOCATIONTAGTESTER`/`tagTitleTagTESTER` placeholders upstream; the build resolves
them to real strings via `QUEST_INTEGRATION_TAGS` (`build_text_arc.py:168-171`) so the
popup is not garbage.

### 8.3 How an ITEM reward resolves

`rewardItemTag` / `Action_GiveItem` item paths are DBR record paths (or item tags).
The referenced item record must resolve in the built `.arz` or the base game
(Section 1.2). To grant a NEW mod item as a reward, author the item (Section 3),
confirm it resolves, then reference it. To grant multiple items, use the multi-reward
header slots or several `Action_GiveItem` actions. Test by completing the quest on a
fresh Custom Quest character and confirming the item lands in inventory.

**`item[tier]` on `Action_GiveItem` points at a LootMasterTable, not a direct item.**
To grant a specific FIXED item (rather than a random roll), author a single-entry
`LootMasterTable` DBR with `lootName1=<your item dbr>` and `lootWeight1=100` (Section
4.1's table taxonomy), then point `item[0]`/`[1]`/`[2]` at that table's normal/epic/
legendary variant - this is the same "one-entry table = a guaranteed item" idiom the
base game uses for quest rewards. A permanent stat-buff reward (as opposed to an
item) is `Action_GiveSkillPoints` with `skill=<a Skill_Passive-class DBR>` and
`skillAmount[tier]=1` - it grants ranks in a passive skill rather than handing over
an item.

---

## 9. RECIPE: TEXT / TAGS (display strings)

All display text (item names, soul names, skill names/descriptions, quest journal +
reward popups) resolves through `Text.arc`, a single `modstrings.txt` overlaid on the
base game's own text.

### 9.1 How Text.arc is built

`build_text_arc.py` (`build_modstrings`, line 49-159): extracts every `tag=value`
line from SV 0.98i's `Text_EN.arc` (22 source `.txt` files, line 54-77),
deduplicates, appends the Occult mastery fixes (`OCCULT_FIX_TAGS`, line 28-33), the
soul tags from the `uber_soul_tags.txt` sidecar, and `QUEST_INTEGRATION_TAGS`, then
packs the result as `modstrings.txt` encoded **UTF-16LE with a BOM** into a
single-file `Text.arc` (line 265-269, `create_single_file_arc`). A tag line is
`key=value`; comments start with `//`.

### 9.2 Adding a new display string

- For SOULS, emit `tag=value` pairs from the soul-creation code; the build folds
  `uber_soul_tags.txt` (auto souls + legacy + extended tags) into `Text.arc`
  automatically (`build_svc_database.py:1456-1464` writes the sidecar;
  `build_text_arc.py:114-145` consumes it).
- For OTHER strings (a new item name, a skill description, a quest reward popup tag),
  add them where the build can see them: extend `OCCULT_FIX_TAGS` /
  `QUEST_INTEGRATION_TAGS` in `build_text_arc.py`, or (for skill-description fixes the
  DB wires) `MOD_DESC_FIX_TAGS` in `build_svc_database.py:38-41`. Every one of these is
  enumerated by `collect_mod_authored_tags` (`build_text_arc.py:198-234`) into the
  `mod_authored_tags.txt` manifest.
- **Color / control codes:** `{^F}` prefix = pink/magenta (the soul convention). Other
  `{^X}` codes color text similarly. Put the code in the tag VALUE, not the field.

### 9.3 Tag naming conventions (as used in this mod)

- `tagSoulSVC{9000+}` - auto-generated soul names (`create_uber_souls.py`).
- `tagSVCSoul<Name>` - hand-authored soul names (`apply_svc_patches.py`).
- `tagSVCSummon<Name>` / `...DESC` - summon-skill names/descriptions.
- `tagDarkAperture*` - restored legacy-skill tags (`build_svc_database.py`).
- `xtagMysteriousPortal` - custom portal NPC description.
- `tagD2Boss004` - a boss rename (Cold Worm).
- `tagSkillName050`, `tagNewSkill321DESC`, `tagbreachDESC` - Occult mastery + skill fixes.

### 9.4 The validate_tags build gate (do not skip)

`py tools/validate_tags.py <final.arz> <final_text.arc> [uber_soul_tags.txt]
[mod_authored_tags.txt]` fails loud (exit 1) if any MOD-OWNED name/description tag the
`.arz` references is missing from `Text.arc` (`tools/validate_tags.py`). "Mod-owned"
is decided by **written-set membership** in the `mod_authored_tags.txt` manifest that
`build_text_arc.py` writes next to `Text.arc` (falling back to a prefix allowlist if
the manifest is absent, `validate_tags.py:103-118`). This is deliberately
false-positive-free: base-game tags the `.arz` merely carries forward
(`tagNewMonster*`, `tagItem*`, ...) are NOT in the manifest and are never required.
The scanned tag fields are `itemNameTag, description, itemText, skillDisplayName,
skillBaseDescription, FileTextTag, lootRandomizerName, ActorName`
(`validate_tags.py:65-74`). The gate is wired into bootstrap Step 4b
(`bootstrap_working_mod.ps1:335-367`) and exits the build non-zero on any miss. It
exists specifically to kill the `tagSoulSVC9005`/`9006` orphan class (a soul roster
change that did not regenerate `Text.arc`).

---

## 10. RECIPE: ENCHANTING / affixes / sets

- **Enchanting (relic/charm slots):** an item is enchantable iff `numRelicSlots >= 1`.
  `make_enchantable` (`build_svc_database.py:421-497`) sets it to 1 on all
  equipment/soul records with 0 slots (skipping `cannotPickUp==1`). Epic/legendary
  enchant capability is baked entirely into the `.arz` this way - **the shipped mod has
  NO Game.dll dependency** (an old Game.dll hex-patch exists only as a local backup;
  `CLAUDE.md` lessons). To make a new item enchantable, set `numRelicSlots=1` or just
  let the pass do it.
- **Forge formulas (upgrade recipes):** class `ItemArtifactFormula`
  (`database\Templates\ItemArtifactFormula.tpl`). Real example:
  `records\item\formulas\n_mercupgrade_bloodmistress_formula.dbr` has
  `artifactName` (the crafted result) + `reagent1BaseName` / `reagent2BaseName` /
  `reagent3BaseName` (the required ingredients, e.g. scroll + bloodstone shard + a
  specific soul). Add a formula to loot the same way as any item (Section 4.1);
  `add_blood_mistress_to_loot` appends it to every forge-formula drop table.
- **Affixes (prefix/suffix) and item sets:** driven by base-game randomizer records +
  set records; this mod does NOT author new affix/set tables. If you need a new set,
  you would author a set record and reference its members; affixes are attached via
  the base `LootRandomizer` fields (`lootRandomizerName` is a scanned tag field).
  Enchanting via relic slots is this mod's chosen customization lever instead.

---

## 11. The content build -> verify -> deploy loop

Assume repo root, `py` launcher, `PYTHONIOENCODING=utf-8`.

1. **EDIT** the tools / records / quests / tag sources.

2. **BUILD the DB** (`.arz` + `uber_soul_tags.txt` + `uber_souls_report.md`). Five
   positional args (`CLAUDE.md` "Build & deploy commands"):
   ```
   py tools/build_svc_database.py \
     upstream/soulvizier_098i/Database/database.arz \
     upstream/soulvizier_0.9/Database/database.arz \
     upstream/soulvizier_041/Database/database.arz \
     work/SoulvizierClassic/Database/SoulvizierClassic.arz \
     "<TQAE install>/Database/database.arz"
   ```
   For a RELEASE build set `SVC_RELEASE_DROPS=1` first (tuned 66%/25% drops);
   otherwise it forces 100% testing drops (Section 4.3). Watch the build log for the
   `*** TESTING BUILD ***` vs `*** SVC_RELEASE_DROPS set ***` line.

3. **BUILD Text.arc + gate on tags** (usually via bootstrap, or directly):
   ```
   py tools/build_text_arc.py <SV Text_EN.arc> work/SoulvizierClassic/Resources/Text.arc \
        work/SoulvizierClassic/Database/uber_soul_tags.txt
   py tools/validate_tags.py work/SoulvizierClassic/Database/SoulvizierClassic.arz \
        work/SoulvizierClassic/Resources/Text.arc \
        work/SoulvizierClassic/Database/uber_soul_tags.txt \
        work/SoulvizierClassic/Resources/mod_authored_tags.txt
   ```
   `validate_tags` MUST print `RESULT: PASS`.

4. **BUILD Quests.arc:**
   ```
   py tools/build_quest_files.py
   ```
   It restores the clean SVAERA `Quests.arc`, adds the ported SV area questlines at
   the root, and self-verifies each round-trips byte-exact (all-OK / 0-MISMATCH).

5. **The whole mod at once** (steps 2-4 + assets + levels handling): run
   `scripts/bootstrap_working_mod.ps1` (NO `-LiteMode`). It runs the DB build, asset
   copy+strip, Text.arc build + `validate_tags` gate, and the quest build in order.

6. **DEPLOY** (backs up saves + prior deploy first):
   ```
   powershell -ExecutionPolicy Bypass -File scripts/deploy_to_custommaps.ps1
   ```
   Add `-SyncLevels` ONLY when you also intend to push a freshly-verified
   `local/Levels_merged.arc` (MODDING_PLAYBOOK Section 9). Content-only changes (DB /
   text / quests) do NOT need `-SyncLevels`.

7. **TEST in-game:** TQAE -> Play Custom Quest -> `SoulvizierClassic`, on a DEDICATED
   Custom Quest character (never a mainline one). Souls are 100% drop by default so
   they are easy to farm and inspect. **Test with FRESHLY DROPPED items** - TQ bakes
   item properties into the save at pickup, so an item picked up before your DB change
   will NOT reflect the change (Section 12).

What each verifier proves:
- `build_svc_database.py` log: which pass wired what, and the drop-rate mode.
- `validate_tags.py`: no mod name/desc tag is missing from `Text.arc` (no raw
  `tag...` text in-game).
- `build_quest_files.py`: every quest added to `Quests.arc` decompresses back to the
  exact authored bytes.

---

## 12. Content failure graveyard (do NOT repeat)

| What was tried | Why it failed | The fix / rule |
|----------------|---------------|----------------|
| Passing an explicit dtype to `set_field` on a cloned record | INT/FLOAT re-encoding silently zeroes the value; pet fails to spawn | On cloned/existing records call `set_field` with NO dtype (preserve the record's dtype); only pass dtype when authoring a new field on a bare record (`arz_patcher.py:221-258`) |
| `clone_record` to make a new soul | Drags source soul stats that corrupt saved items | Create souls bare with `_ensure_record`; set only intended fields (`create_uber_souls.py:614-619`) |
| Copying equipment/loot fields from Monster.tpl into a Pet.tpl record | Crashes the game (even changing an existing shared field's value) | Clone the pet from Lyia (valid Pet.tpl); copy ONLY animation + update-only skill fields; set equipment via `_set_pet_equipment` with hardcoded paths (`apply_svc_patches.py:303-317`) |
| Leaving `spawnObjectsTimeToLive` on a soul summon | Pet despawns after the TTL | Omit the field (clone from Lyia's permanent `summon_lyia.dbr`); never add a TTL (`apply_svc_patches.py:444-452`) |
| Soul name tag with no `{^F}` prefix | Soul name renders in default color, not the pink soul color | Prefix the Text.arc VALUE with `{^F}` (`create_uber_souls.py:575`) |
| Soul `bitmap` pointing at `Items\miscellaneous\{n,e,l}_soul.tex` | That path is not in `Items.arc`; icon shows as a grey box | Point `bitmap` at `SVItems\jewelry\soul_{n,e,l}_icon.tex`; `fix_soul_bitmaps` fixes strays at build end (`build_svc_database.py:1325-1358`) |
| A `.arz` name/desc tag missing from `Text.arc` (e.g. `tagSoulSVC9005/9006`) | Raw `tag...` string shows in-game | `validate_tags.py` gate fails the build; author the tag into the pipeline so it lands in `Text.arc` (`validate_tags.py`, gate at `bootstrap_working_mod.ps1:335-367`) |
| Building `Text.arc` without regenerating soul tags | `Text.arc` built against a stale soul roster (the orphan-tag bug) | Rebuild `.arz` + `Text.arc` together; the staleness guard warns (`build_text_arc.py:117-133`) and `validate_tags` catches it |
| Shipping with the 100% soul-drop TESTING override left on | Every soul drops at 100% (release balance ruined) | Set `SVC_RELEASE_DROPS=1` for release; default is 100% testing (`build_svc_database.py:1428-1443`) |
| Testing DB changes with an item already in the save | TQ baked the item's properties at pickup; the change does not show | Test with a FRESHLY DROPPED/created item on a fresh character (`CLAUDE.md` lessons) |
| Case-mismatched `.dbr` reference (PascalCase vs stored lowercase) | AE Custom Quest lookups are case-SENSITIVE; the reference silently fails | Match the stored case; the build rewrites refs to the exact stored path (`build_svc_database.py:837-873`) |
| Running `-LiteMode` | Strips `drx.arc`/`DRXtextures.arc` which hold the soul mesh `drx\meshes\n_soulmesh.msh` + DRX item/terrain assets | Keep DRX; crash mitigation is the 4GB LAA patch, not stripping art (`CLAUDE.md` release plan) |
| Adding a quest with a NEW name and no map QUESTS registration | Name is not in the map; quest never activates | Reuse an already-registered name (Quests.arc-only, no rebuild), or add the name to the map's QUESTS section + place triggers = a map rebuild (`build_quest_files.py:46-52`) |
| Using a quest teleport to enter a persistent area | Step state bakes into saves; the 200x OnLevelLoad idiom broke twice | Use engine-native cave-mouth/grid-seam entry; quests for logic only (`build_quest_files.py:37-44`; MODDING_PLAYBOOK Section 2c) |

---

## 13. Appendix: content file / dir map

Where things live (paths relative to repo root unless noted):

- **DB source (upstream):** `upstream/soulvizier_098i/Database/database.arz` (base SV),
  `upstream/soulvizier_0.9/Database/database.arz` (potion-rate reference),
  `upstream/soulvizier_041/Database/database.arz` (legacy skills). Base game:
  `<TQAE install>/Database/database.arz`. (All `upstream/` is gitignored.)
- **Built DB:** `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (+ sidecars
  `uber_soul_tags.txt`, `uber_souls_report.md`).
- **Built text:** `work/SoulvizierClassic/Resources/Text.arc` (single `modstrings.txt`,
  UTF-16LE) + `mod_authored_tags.txt` manifest beside it.
- **Built quests:** `work/SoulvizierClassic/Resources/Quests.arc` (SVAERA base + ported
  SV area quests at root). Upstream SV quests:
  `upstream/soulvizier_098i/Resources/XPack/Quests.arc`.
- **Item/soul icons:** `SVItems.arc` (`SVItems\jewelry\soul_*_icon.tex`). **Soul mesh:**
  `drx.arc` (`drx\meshes\n_soulmesh.msh`). **Pet/skill icons:** `DRXtextures.arc`.
- **Templates:** `<TQAE install>/Toolset/Templates.arc` (566 `.tpl`; resolved
  automatically, never placed in the mod).
- **Record namespaces:** souls `records\item\equipmentring\soul\...` (auto souls under
  `...\soul\svc_uber\`); pets `records\skills\soulskills\pets\...`; summon skills
  `records\skills\soulskills\...`; loot tables `records\item\loottables\...`;
  formulas `records\item\formulas\...`; artifacts/scrolls `records\item\artifacts\...`;
  monsters `records\creature\monster\...`; portal NPCs `records\quests\...`.
- **The content tools:** `tools/build_svc_database.py` (DB builder + all soul/enchant
  passes), `tools/apply_svc_patches.py` (extended souls/pets/loot/drop patches),
  `tools/create_uber_souls.py` (auto-soul generator; designs in
  `tools/uber_soul_designs.py`), `tools/build_text_arc.py` (Text.arc),
  `tools/validate_tags.py` (tag gate), `tools/build_quest_files.py` (Quests.arc),
  `tools/qst_format.py` (.qst reader/writer/spec), `tools/arz_patcher.py`
  (`ArzDatabase`), `tools/arc_patcher.py` (`ArcArchive`). NOTE:
  `tools/apply_sv_classic_patches.py` (underscore variant) is DEAD/orphaned - the live
  one is `apply_svc_patches.py`.

### 13.1 "I want to add X content" quick reference

| I want to add... | Section | Key mechanism |
|------------------|---------|---------------|
| A new equipment / weapon / armor / jewelry item | 3 | record + template + tags; `make_enchantable` for a relic slot |
| It to actually drop from a chest / formula pool | 4.1 | append `lootName{i}`/`lootWeight{i}` to a `LootItemTable_FixedWeight`/`LootMasterTable` |
| It to be sold by a merchant | 4.1a | append to the loot table the merchant's `market<Category>Table{N}` points at |
| A new soul that drops from a monster | 4.2, 5 | soul ring record + wire the monster's `lootFinger2Item1`+`chanceToEquipFinger2`+`dropItems` |
| A summonable pet for a soul | 6 | `Skill_SpawnPet` (no TTL) + `Pet` cloned from Lyia; `_set_pet_equipment` |
| A quest (ported) | 7.3 | copy the `.qst` byte-exact to `Quests.arc` root; no map rebuild if the name is registered |
| A quest (new) | 7.4 | `build_quest` + `make_*`; register the name + place triggers = map rebuild |
| A quest reward (item/gold/xp/skill/attr) | 8 | header `reward*` fields or in-step `Action_Give*` |
| A new display string / soul name | 9 | author the `tag=value` into the build; `{^F}` for magenta; `validate_tags` gate |
| An upgrade recipe | 10 | `ItemArtifactFormula` (`artifactName` + `reagent{n}BaseName`); loot it like an item |
| Make an item enchantable | 10 | `numRelicSlots=1` (or the `make_enchantable` pass) |

Then always: build the DB (Section 11 step 2) -> build Text.arc + `validate_tags`
(step 3) -> build Quests.arc (step 4) -> deploy (step 6) -> test with freshly-dropped
items on a dedicated Custom Quest character (step 7). For anything spatial (a new cave,
walkable area, or the map registration of a new quest name), cross to
`docs/MODDING_PLAYBOOK.md`.
