# b53 - Boss-orb "Charon's Essence" RCA (Dagon drop)

**Status:** RCA COMPLETE - read-only, NO fix applied. Verdict + surgical fix plan below.
**Branch:** `feat/b53-orb-essence` (base `d11d3c0`, build38a).
**Ground truth:** `scratchpad/baseline_build38.arz` (== DEV/Steam arz `6631f252` Will plays);
base-game `database.arz`; upstream `soulvizier_098i/Database/database.arz`; deployed Workshop
`Text.arc` (`2af4ce38`, item 3759792705) + base `Text_EN.arc`.

---

## The report (Will, 2026-07-13)

Dagon (`records\test\boss_dagon_66`) dropped an item named **"Charon's Essence"**. Will: "it
should not say Charons Essence it should just use the typical name which is magical orb or
mystical orb or something." = the boss orb Dagon drops should use the generic/typical orb, not a
bespoke boss-named "X's Essence".

---

## 1) What "Charon's Essence" is (item + tag)

**Tag:** `xtagChest18 = Charon's Essence`
- A **base-game** tag (present in the stock `Text_EN.arc`) and re-emitted verbatim in the mod's
  deployed `Text.arc`. NOT a mod-authored name. Siblings in the same family:
  `xtagChest17 = Hades' Essence`, `tagEndChest01 = Typhon's Essence`, `tagEndChest02 = Mystical Orb`.

**Item record(s) carrying that name** (all base-game, `Class = FixedItemContainer`, mesh
`Items\Containers\typhonorb_chest02.msh`):
```
records\xpack\item\containers\bosschest02_charon_01.dbr        description=xtagChest18  (normal)
records\xpack\item\containers\bosschest02_charon_02.dbr        description=xtagChest18  (epic)
records\xpack\item\containers\bosschest02_charon_03.dbr        description=xtagChest18  (legendary)
records\xpack\item\containers\bosschest02_charonrepeat_01..03  description=xtagChest18  (repeat)
```
These FixedItemContainers ARE the openable "boss chest orb" the player sees on the ground - its
hover/pick-up name resolves to **"Charon's Essence"**. This is the base-game **act-2 Charon boss
chest** (the ferryman boss reward orb). It is a shared SV-original/base-game DESIGN record - do
NOT rename it.

Selector proxy (what a monster's `treasureProxyName` points at), `Class = Proxy`:
```
records\xpack\item\containers\proxies\bosschest02_charon.dbr
   accessory1         -> ...\accessory pools\bosschestpool02_charon_01.dbr  (normal)
   accessoryEpic1     -> ...\accessory pools\bosschestpool02_charon_02.dbr  (epic)
   accessoryLegendary1-> ...\accessory pools\bosschestpool02_charon_03.dbr  (legendary)
   mesh = Items\Containers\typhonorb_chest02.msh
```
The proxy has no name of its own; it spawns the difficulty-matched `bosschest02_charon_0N`
FixedItemContainer, whose `description = xtagChest18` is what displays "Charon's Essence".

## 2) Why DAGON drops it

`records\test\boss_dagon_66.dbr` (in the built `baseline_build38.arz`, i.e. the shipped state):
```
Class                 = Monster
monsterClassification = Boss
description           = tagD2Boss033          (Dagon's own name)
FileDescription       = drops Dagon relic
treasureProxyName     = records\xpack\item\containers\proxies\bosschest02_charon.dbr   <-- ROOT CAUSE
lootFinger2Item1      = ...\soul\svc_uber\dagon_soul_{n,e,l}.dbr   (Dagon soul, chanceToEquipFinger2=66)
lootMisc2Item3        = records\item\questitems\d2custom\cthulhu_dagon.dbr  (the Dagon relic)
```
Dagon's **`treasureProxyName` is the base-game Charon boss chest proxy**. On death Dagon spawns
Charon's boss chest -> "Charon's Essence".

**Provenance (why it's wired that way):**
- `boss_dagon_66` does **NOT** exist in base game (`has_dagon=False`).
- It **DOES** exist in **upstream Soulvizier 0.98i** (amgoz1) with
  `treasureProxyName = records\xpack\item\containers\proxies\bosschest02_charon.dbr`.
- So Dagon is an **upstream amgoz1 SV custom boss** (a Lovecraftian deep-one built on an Ichthian
  actor). amgoz1 authored Dagon **reusing the base-game act-2 Charon boss chest as a placeholder
  death drop**. Dagon is not Charon, so the name reads wrong.
- The mod inherits this verbatim. Mod code touches Dagon only to (a) add it as a rare champion in
  ichthian spawn pools (`_add_dagon_to_ichthian_pools`, apply_svc_patches.py:1447) and (b) create
  the Dagon soul (`_create_dagon_soul`, :2427). Neither sets `treasureProxyName`. The mod's
  boss-orb law (`_amend_boss_loot_orbs`, :10331; roster `_BOSS_ORB_TARGETS`, :10312) that wires the
  generic apex orb onto custom Boss-class bosses **never included Dagon**, so it kept amgoz1's
  Charon chest.

This is a **static authoring leftover**, NOT a runtime cross-wire and NOT a save-state artifact.

## 3) The family (how broad is the mis-drop?)

"X's Essence" is a **base-game/DRX act-boss chest naming system**. ~14 `bosschest*` selector
proxies exist (graeae / charon / cerberus / skeletaltyphon / hades + telkine/typhon/leinth/
blackwidow proxy variants); confirmed essence-named containers: Charon (`xtagChest18`), Hades
(`xtagChest17`), Typhon (`tagEndChest01`).

**Scope of the actual defect (scan of every monster in the shipped arz whose `treasureProxyName`
-> any `bosschest*` proxy): 30 monsters, of which only TWO are mod/custom content:**

| Monster | treasureProxyName | Verdict |
|---|---|---|
| `records\test\boss_dagon_66.dbr` | `...proxies\bosschest02_charon.dbr` | **BUG - the reported mis-drop** |
| `...02_charon\um_charonform2_ferryman_99.dbr` (mod Charon uber "Charon, the Unferried") | `...proxies\bosschest02_charon.dbr` | **CORRECT by design** - it IS Charon; explicitly excluded from the generic-orb law (apply_svc_patches.py:10308/10324 comment) |

The other 28 are base-game / DRX-native bosses (real act bosses, telkines, Typhon, Hades forms,
DRX Leinth/blackwidow) dropping their own correct essence. **So the shipped cross-wire is exactly
ONE boss: Dagon.** No other custom boss inherits a wrong-boss essence.

## 4) The generic orb target Will wants

The mod's established "typical" boss orb = **`records\item\containers\new\genericbossorb_04.dbr`**
(the `_APEX_ORB` / "boss-orb law", `Class = Proxy`, mesh `Items\Containers\ChestBoss01.msh`).
It is already the `treasureProxyName` of ~13 other custom Boss-class bosses (Blood Toxeus, the
Enslaver, Vashkarr, Broodmother, Dorus, Sarkoth, Gorrahk, Ilsevar, Voranthys, Tantalus,
Mnemophage-core, Ephialtes). It has **no bespoke name** (no `description` field; its accessory
pools are `ProxyAccessoryPool`, not named FixedItemContainers) - so bosses using it drop an
un-named generic apex orb, exactly the "typical" behavior Will wants (no "X's Essence").

(If Will ever wants a *visible* generic name instead of nameless, the base game already ships
`tagEndChest02 = Mystical Orb` - literally his "mystical orb". But matching the in-mod convention =
`genericbossorb_04`, and that is the recommended target.)

---

## VERDICT

Root cause = **Dagon's `treasureProxyName` = the base-game act-2 Charon boss chest proxy**
(`records\xpack\item\containers\proxies\bosschest02_charon.dbr`), inherited verbatim from upstream
amgoz1 SV 0.98i where Charon's chest was reused as Dagon's placeholder drop. That chest's
FixedItemContainer (`bosschest02_charon_0N`, `description = xtagChest18`) displays **"Charon's
Essence"**. The mod's generic boss-orb law never covered Dagon. It is the **only** custom boss
mis-wired this way (the Charon uber that also uses this proxy is correct-by-design).

## FIX PLAN (surgical, one field on one record)

**Retarget Dagon to the generic apex orb** by adding it to the existing boss-orb law roster:

- File: `tools/apply_svc_patches.py`, `_BOSS_ORB_TARGETS` (~line 10312), add:
  ```python
  (r'records\test\boss_dagon_66.dbr', _APEX_ORB),   # b53: was inherited Charon chest ("Charon's Essence")
  ```
  `_amend_boss_loot_orbs` (:10331) then sets `treasureProxyName -> genericbossorb_04`, and the
  existing fail-loud `_verify_boss_orbs` gate (:10484) auto-covers it (requires the new target's
  `treasureProxyName` to resolve).

**Why this and not a rename:**
- Do NOT rename `bosschest02_charon*` / `xtagChest18` - shared base-game DESIGN records, and the
  mod's Charon uber legitimately drops "Charon's Essence" from them. Renaming would corrupt Charon's
  correct drop and mutate an SV-original design record (banned).
- Retargeting only Dagon's one field is the minimal, in-family change; it makes Dagon match the
  ~13 other custom bosses.

**Preserved (must remain untouched by the fix):**
- Dagon **soul** drop (`chanceToEquipFinger2 = 66`, `lootFinger2Item1 = dagon_soul_{n,e,l}`) -
  independent of `treasureProxyName`.
- Dagon **relic** (`lootMisc2Item3 = cthulhu_dagon.dbr`) and all other `loot*`/`chanceToEquip*`
  fields - independent of `treasureProxyName`.
- Drop RATES and orb loot contents - unchanged (only the proxy identity/name changes).
- `um_charonform2_ferryman_99` (Charon uber) - leave on `bosschest02_charon` (correct).

**Registry / laws:** honors the boss-orb law + its fail-loud invariant; crash-safe (single string
field on a Monster record - Monster records are not clone-shape-gated, per the file's own note at
:10309); item-name change flows through the tags pipeline only insofar as the *new* proxy resolves
(genericbossorb_04 exists in the arz - verified). No Text/tag edit needed (the fix removes the
name, it doesn't add one).

**Verification for the fix agent:** dry-run replay `_amend_boss_loot_orbs` on a COPY of
`baseline_build38.arz`, then assert `boss_dagon_66.treasureProxyName == genericbossorb_04` and that
`bosschest02_charon*` + `um_charonform2_ferryman_99` are unchanged; run `_verify_boss_orbs` (must
print "Boss-orb invariant OK"); `validate_tags` PASS.

---

## Evidence / repro (read-only probes, in scratchpad)
- `b53_probe2.py` - Dagon + orb loot fields (shows `treasureProxyName = bosschest02_charon`).
- `b53_probe3.py` - full `genericbossorb_04` vs `bosschest02_charon` proxy chains.
- `b53_probe4.py` - Text scan: `xtagChest18 = Charon's Essence` (base + mod).
- `b53_probe5.py` - `xtagChest18` owner records + full essence family + all 30 bosschest droppers.
- `b53_probe6.py` - generic orb has no name; `tagEndChest02 = Mystical Orb`.
- `b53_prov.py` - provenance: Dagon absent in base game, present in SV 0.98i with the Charon proxy.
