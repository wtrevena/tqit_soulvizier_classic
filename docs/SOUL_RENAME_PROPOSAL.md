# SOUL RENAME PROPOSAL - `BL-R201-DEBT-1` (40 cross-family duplicate display names)

> **STATUS: PROPOSAL. NOTHING IS IMPLEMENTED. NO GAME DATA WAS TOUCHED BY THE LANE THAT WROTE THIS.**
> This document exists to be **ratified line-by-line or wholesale by Will**. Until a row is approved,
> nothing changes. Renaming souls is explicitly a Will decision, not an agent call
> (`docs/BACKLOG.md` `BL-R201-DEBT-1`).

**Measured on:** `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (build83, 51,253 records) with
display strings resolved through `work/SoulvizierClassic/Resources/Text.arc` (4,507 tags), using the
**exact** canonical-family filter the shipped R-201 gate uses
(`apply_svc_patches._soul_family_key` / `_iter_soul_tier_records`).
Reproduced the vet's finding exactly: **2,191 canonical soul tier records / 740 families / 698 distinct
display names / 40 display names shared by more than one family.**

## Verdict counts

| verdict | groups | what it is |
|---|---:|---|
| **RENAME PROPOSED** (mod soul vs SV soul) | **5** | rows 7, 12, 14, 19, 38 |
| **KEEP-AS-IS** (SV vs SV, amgoz1's own duplication) | **35** | everything else |
| of which: twin is SV's dead `soul\test\` folder | 29 | twin has **ZERO** external referents, so it can never reach a player's bag |
| of which: SV `_n` double-authored sibling | 4 | rows 4, 10, 15, 40 |
| of which: SV typo-path twin | 1 | row 37 (`orythroneus` / `oythroneus`) |
| of which: two distinct SV monsters sharing one tag | 2 | row 11 (`alcestis` / `soulcarver`), row 32 (`maenadscout` / `maenadvanguard`) |

Rows 11 and 32 are the pre-existing quirks the R-201 gate record already registered. Row 32 is counted
once, in the `soul\test\` bucket, and also carries the live two-monster share.

## THE RULE this proposal applies

1. **SV originals NEVER change.** Law #2 (never override amgoz1). Also R-49a, verbatim: no name-drift
   rename, *including* obvious SV misspellings ("The Etheral One Soul"). SV keeps its string in every
   row below without exception.
2. **Mod soul vs SV soul: the MOD soul is renamed.** All 5 rename rows are this case.
3. **Mod vs mod: rename the lesser / newer one.** **Zero rows hit this case** (no two `svc_uber\`
   families share a display name).
4. **Both SV originals: KEEP-AS-IS.** SV's own duplication, not ours. 35 rows.
5. Every proposed name keeps the **`{^F}` magenta prefix** and must read correctly with the R-201 tier
   prefix in front of it ("Epic \<name\>", "Legendary \<name\>"), because `itemQualityTag` renders as a
   PREFIX and all three tiers share one `itemNameTag`.

**Two naming registers are in play, both already shipped, and each row offers one of each so Will can
pick per row:**
* **`{^F}<Titled Monster> Soul`** - the F6 standard for generated souls. Titled monsters keep their
  full display form, e.g. the shipped `Kallixenia ~ Liche Queen Soul`, `Tomb Guardian ~ Hound of Anubis
  Soul`, `Ice Raptor ~ Brood Mother Soul`. **Needs no gate exemption.**
* **`{^F}Soul of the <X>`** - the evocative marquee register for hand-designed souls, e.g. the shipped
  `Soul of the Insatiable`, `Soul of the Unferried`, `Soul of the Coin-Drowned`, `Soul of Anapaest the
  Dishonored`. **Requires the tag in `_HAND_DESIGNED_SOUL_TAGS`** (and removal from
  `_SOUL_NAME_STANDARD`), exactly the Anapaest (A9) and Drowned-King (b47) precedent.

---

# RATIFICATION TABLE A - THE 5 RENAMES (mod soul renamed, SV soul untouched)

Ratify a row by picking **PRIMARY** or **ALTERNATE**, or by writing your own string in the margin.

| # | Current shared name | Souls involved (provenance / tag / dropper) | PROPOSED (primary) | ALTERNATE | One-line lore justification |
|---:|---|---|---|---|---|
| **7** | `Charon Soul` | **SV, KEEPS NAME:** `soul\charon\charon_soul_{n,e,l}` - `tagSoulName193`; dropped by `boss_charonform2_{39,41,43}` @25%; grants `charon_buffself`.<br>**MOD, RENAMED:** `soul\svc_uber\boss_charon_soul_{n,e,l}` - `tagSoulSVC9005`, **generated** (`create_uber_souls`); dropped by `boss_charon_{39,41,43}` @66%; grants `talos_flamethrower` + `drxvolcanicorb` + `drxringofflame`. | `{^F}Charon ~ Ferryman of the Styx Soul` | `{^F}Soul of the Ferryman's Flame` | Will's own double-soul ruling (c) keeps BOTH Charon drops on purpose as a two-form reward; two deliberate rewards must read as two. The mod soul is the FIRST form and carries his fire kit; the SV soul is the form-2 drop. |
| **12** | `General Yrrt'ik Soul` | **SV, KEEPS NAME:** `soul\formicid\generalyrrtik_soul_{n,e,l}` - `tagSoulName453`; dropped by `xhero_generalyrrtik_43`.<br>**MOD, RENAMED:** `soul\svc_uber\rainbowbright_soul_{n,e,l}` - `tagSVCSoulRainbowbright`, **hand-authored**; dropped by `drxcreatures\crowheroes\rainbowbright.dbr` (Quest, 33%); grants `battlestandard` + `drxbattlerage` + `drxrally`. | `{^F}Soul of Rainbowbright the Standard-Bearer` | `{^F}Hive Standard-Bearer Soul` | A different monster entirely: the DRX crow-hero who rallies the insectoid host under his battle standard, not SV's formicid general. **The primary string is already authored in the repo** (`apply_svc_patches.py` L18883, with a matching DESC); it is only being flattened by the F6 table. |
| **14** | `Ice Mandible Soul` | **SV, KEEPS NAME:** `soul\antlion\frostmandible_soul_{n,e,l}` - `tagSoulName387`; **no monster drops it** (crafting-formula reagent only).<br>**MOD, RENAMED:** `soul\svc_uber\frost_soul_{n,e,l}` - `tagSVCSoulHCFrost`, **mod handcraft** (`_DEWIRED_HANDCRAFT['frost']`); dropped by `antlion\um_frost_32.dbr` (Hero, 33%); grants `chillingair` + `drxcoldaura` + `drxdeathchillaura`. | `{^F}Frostmaw Soul` | `{^F}Soul of the Killing Frost` | The uber antlion's frozen jaws, and three stacked cold auras: it is a walking pall of frost, not SV's Ice Mandible. Ours is the only one of the pair that any monster actually drops. |
| **19** | `Kallixenia ~ Liche Queen Soul` | **SV, KEEPS NAME:** `soul\abyssalliche\kallixenia_soul_{n,e,l}` - `tagSoulName234`; dropped by `xsq02_lichequeen_36` (the real Lich Queen); grants `lichequeen_soulstrike` + `drxwraithlordsummons`.<br>**MOD, RENAMED:** `soul\svc_uber\kallixenia_soul_{n,e,l}` - `tagSVCSoulKallixenia`, **hand-authored**; wired to `drxcreatures\xurder\d2npc\01_akara.dbr`, whose own description tag reads **"Akara"**. ⚠️ **Its drop roll is ALREADY DETACHED** by `tools/patches/soul_identity.py` (`chanceToEquipFinger2` -> 0), so it is currently unobtainable. | `{^F}Soul of the Pale Diadem` | `{^F}Akara ~ Seeress of the Sightless Eye Soul` | A second lich-queen soul that is not the Lich Queen's. The **primary is name-only** and safe whatever you decide about the wire. The **alternate is only correct if you also re-point the soul to Akara's own identity** - that re-point is the separate open decision in `docs/reports/b97_soul_identity_audit.md` sec 8 and this document does NOT resolve it. |
| **38** | `Plague Feast Soul` | **SV, KEEPS NAME:** `soul\carrionbird\plaguefeast_soul_{n,e,l}` - `tagSoulName135`; dropped by `u_plaguefeast_13`; grants `drxplague`.<br>**MOD, RENAMED:** `soul\svc_uber\nomnom_soul_{n,e,l}` - `tagSVCSoulNomnom`, **hand-authored**; dropped by `drxcreatures\crowheroes\nomnom.dbr` (Quest, 33%); grants `arachne_venomspray` + `drxenvenomweapon` + `drxplague`. | `{^F}Soul of Nomnom` | `{^F}Carrion Glutton Soul` | A different monster: the DRX crow-hero glutton who spits venom, not SV's carrion bird. **The primary string is already authored in the repo** (`apply_svc_patches.py` L18891, with a matching DESC) and matches the shipped DRX joke-hero register (`yerk yerk Soul`, `Team Jabarto Soul`, `Murder Bunny Soul`). |

## Exactly what changes per rename row (so the wave is mechanical)

**No `.dbr` record is renamed, retired, or re-pointed. No SV tag is touched. Every rename is a
STRING change on a MOD-OWNED tag.** The three tier records keep pointing at the same `itemNameTag`,
so the R-201 tier prefix keeps working untouched.

| # | tag whose STRING changes | where the string is authored today | records that reference it (unchanged) | gate follow-up |
|---:|---|---|---|---|
| 7 | `tagSoulSVC9005` | generated in `tools/create_uber_souls.py` from the monster display (L597-604) | `svc_uber\boss_charon_soul_{n,e,l}.dbr` (3) | **PRIMARY:** add `'boss_charon': 'Charon ~ Ferryman of the Styx'` to `create_uber_souls.DISPLAY_NAME_OVERRIDES` (also corrects the record's `FileDescription`). No exemption needed. **ALTERNATE:** explicit `tags[...]` override + add to `_HAND_DESIGNED_SOUL_TAGS`. |
| 12 | `tagSVCSoulRainbowbright` | `apply_svc_patches.py` L18883 (evocative) then **overwritten** by `_SOUL_NAME_STANDARD` L9003 | `svc_uber\rainbowbright_soul_{n,e,l}.dbr` (3) | **PRIMARY:** DELETE the `_SOUL_NAME_STANDARD` entry and ADD the tag to `_HAND_DESIGNED_SOUL_TAGS` (Anapaest / Drowned-King precedent). The authored string then wins end-to-end. **ALTERNATE:** just change the `_SOUL_NAME_STANDARD` value. |
| 14 | `tagSVCSoulHCFrost` | built in `_apply_dewired_hero_handcraft` as `'{^F}%s Soul' % disp` from `_DEWIRED_HANDCRAFT['frost'][0]` = `'Ice Mandible'` | `svc_uber\frost_soul_{n,e,l}.dbr` (3) | **PRIMARY:** one-word edit, `'Ice Mandible'` -> `'Frostmaw'`, in `_DEWIRED_HANDCRAFT`. No exemption needed. **ALTERNATE:** explicit `tags[...]` override + `_HAND_DESIGNED_SOUL_TAGS` (the handcraft only emits the `<X> Soul` form). |
| 19 | `tagSVCSoulKallixenia` | `apply_svc_patches.py` L18827 then **overwritten** by `_SOUL_NAME_STANDARD` L8988 | `svc_uber\kallixenia_soul_{n,e,l}.dbr` (3) | **PRIMARY:** replace the `_SOUL_NAME_STANDARD` value and add to `_HAND_DESIGNED_SOUL_TAGS` (it is a `Soul of X` form). Update the DESC at L18828 to match. **ALTERNATE:** `_SOUL_NAME_STANDARD` value only, no exemption, **plus** the separate wire decision. |
| 38 | `tagSVCSoulNomnom` | `apply_svc_patches.py` L18891 (evocative) then **overwritten** by `_SOUL_NAME_STANDARD` L9000 | `svc_uber\nomnom_soul_{n,e,l}.dbr` (3) | **PRIMARY:** DELETE the `_SOUL_NAME_STANDARD` entry and ADD the tag to `_HAND_DESIGNED_SOUL_TAGS`. **ALTERNATE:** just change the `_SOUL_NAME_STANDARD` value. |

**Totals if all 5 PRIMARIES are ratified:** 5 tag STRINGS change, 0 records change, 0 SV tags touched,
0 records added or retired. `Text.arc` moves; `SoulvizierClassic.arz` moves only because
`uber_soul_tags.txt` is emitted by the DB build (see the implementation note).

---

# RATIFICATION TABLE B - THE 35 KEEP-AS-IS (SV vs SV)

Rule 4 applies to every row: both sides are amgoz1's, so **no string changes**. The `refs` column is
the count of external records (monsters, loot tables, crafting formulas) that reference that family's
tier records in the shipped arz; `mon` is how many of those are creature records.

| # | Shared display name | Families involved (all SV) | Shared tag | Why KEEP-AS-IS |
|---:|---|---|---|---|
| 1 | Aletha Darkclaw Soul | `maenad\alethadarkclaw` (refs 38, mon 6) + `test\alethadarkclaw` (refs **0**) | `tagSoulName321` | Twin is SV's dead `soul\test\` folder: zero referents, `e`/`l` only, unreachable in game. |
| 2 | Amynta Nimblebow Soul | `maenad\amynta` (38, mon 6) + `test\amynta` (**0**) | `tagSoulName322` | Same: dead `soul\test\` twin. |
| 3 | Ascacophus ~ Gate Keeper Soul | `ascacophus\gatekeeper` (27, mon 9) + `test\gatekeeper` (**0**) | `tagSoulName235` | Same: dead `soul\test\` twin. |
| 4 | Athenos the Nimble Soul | `furies\athenos` (21, mon 3) + `furies\athenos_n` (3, mon 0) | `tagSoulName173` | SV double-authoring: `athenos_n_soul` is a normal-tier sibling reachable only as a crafting reagent. amgoz1's data. |
| 5 | Bloodcrow Soul | `maenad\bloodcrow` (31, mon 6) + `test\bloodcrow` (**0**) | `tagSoulName112` | Same: dead `soul\test\` twin. |
| 6 | Bramblehorn Soul | `ascacophus\bramblethorn` (21, mon 3) + `test\bramblethorn` (**0**) | `tagSoulName401` | Same: dead `soul\test\` twin. |
| 8 | Deathtrunk Soul | `ascacophus\deadtrunk` (21, mon 3) + `test\deadtrunk` (**0**) | `tagSoulName185` | Same: dead `soul\test\` twin. |
| 9 | Dimanae the Intagliated Soul | `maenad\dimanae` (38, mon 6) + `test\dimanae` (**0**) | `tagSoulName438` | Same: dead `soul\test\` twin. |
| 10 | Diseased Vulture Soul | `vulture\diseasedvulture` (33, mon 24) + `vulture\diseasedvulture_n` (11, mon 1) | `tagSoulName84` | SV double-authoring; **both sides drop** (`vampiric_vulture_21` carries the `_n` sibling). amgoz1's data, and R-49a forbids the name-drift rename. |
| 11 | Empusa Soul Carver Soul | `empusa\alcestis` (18, mon 0) + `empusa\soulcarver` (36, mon 18) | `tagSoulName200` | Two DISTINCT SV monsters sharing one name tag. `alcestis` is reagent-only. Pre-registered quirk; SV's call, not ours. |
| 13 | High Priestess Vakiya Soul | `maenad\vakiya` (38, mon 6) + `test\vakiya` (**0**) | `tagSoulName190` | Same: dead `soul\test\` twin. |
| 15 | Infected Vulture Soul | `vulture\infectedvulture` (18, mon 9) + `vulture\infectedvulture_n` (10, mon 0) | `tagSoulName86` | SV double-authoring; `_n` sibling is reagent-only. |
| 16 | Ino Soul | `maenad\ino` (33, mon 9) + `test\ino` (**0**) | `tagSoulName69` | Same: dead `soul\test\` twin. |
| 17 | Inonia Strongheart Soul | `maenad\inoniastrongheart` (38, mon 6) + `test\inoniastrongheart` (**0**) | `tagSoulName165` | Same: dead `soul\test\` twin. |
| 18 | Isadora Sunspear Soul | `maenad\isadora` (38, mon 6) + `test\isadora` (**0**) | `tagSoulName256` | Same: dead `soul\test\` twin. |
| 20 | Kyra Shadowdancer Soul | `maenad\kyrashadowdancer` (38, mon 6) + `test\kyrashadowdancer` (**0**) | `tagSoulName323` | Same: dead `soul\test\` twin. |
| 21 | Laneira Flameheart Soul | `maenad\laneiraflameheart` (38, mon 6) + `test\laneiraflameheart` (**0**) | `tagSoulName171` | Same: dead `soul\test\` twin. |
| 22 | Linia Shieldbreaker Soul | `maenad\liniashieldbreaker` (38, mon 6) + `test\liniashieldbreaker` (**0**) | `tagSoulName324` | Same: dead `soul\test\` twin. |
| 23 | Lyia Leafsong Soul | `maenad\lyia` (44, mon 9) + `test\lyia` (**0**) | `tagSoulName156` | Same: dead `soul\test\` twin. (`maenad\lyia` is the repo's reference permanent-pet soul; do not disturb it.) |
| 24 | Lysia Spellbreaker Soul | `maenad\lysiaspellbreaker` (38, mon 6) + `test\lysiaspellbreaker` (**0**) | `tagSoulName326` | Same: dead `soul\test\` twin. |
| 25 | Maenad Alchemist Soul | `maenad\maenadalchemist` (28, mon 18) + `test\maenadalchemist` (**0**) | `tagSoulName68` | Same: dead `soul\test\` twin. |
| 26 | Maenad Huntress Soul | `maenad\maenadhuntress` (47, mon 24) + `test\maenadhuntress` (**0**) | `tagSoulName66` | Same: dead `soul\test\` twin. |
| 27 | Maenad Rogue Soul | `maenad\maenadrogue` (19, mon 9) + `test\maenadrogue` (**0**) | `tagSoulName72` | Same: dead `soul\test\` twin. |
| 28 | Maenad Shadowblade Soul | `maenad\maenadshadowblade` (19, mon 9) + `test\maenadshadowblade` (**0**) | `tagSoulName73` | Same: dead `soul\test\` twin. |
| 29 | Maenad Sorceress Soul | `maenad\maenadsorceress` (78, mon 51) + `test\maenadsorceress` (**0**) | `tagSoulName67` | Same: dead `soul\test\` twin. |
| 30 | Maenad Stalker Soul | `maenad\maenadstalker` (31, mon 18) + `test\maenadstalker` (**0**) | `tagSoulName65` | Same: dead `soul\test\` twin. |
| 31 | Maenad Tracker Soul | `maenad\maenadtracker` (19, mon 9) + `test\maenadtracker` (**0**) | `tagSoulName35` | Same: dead `soul\test\` twin. |
| 32 | Maenad Vanguard Soul | `maenad\maenadscout` (34, mon 15) + `maenad\maenadvanguard` (212, mon 69) + `test\maenadscout` (**0**) + `test\maenadvanguard` (**0**) | `tagSoulName34` | **Four** families on one tag. Two are live, distinct SV monsters (scout and vanguard) that genuinely read the same in the bag; this is the quirk the R-201 gate record already registered as SV data. Plus two dead `soul\test\` copies. |
| 33 | Maeve Waterguard Soul | `maenad\maevewaterguard` (39, mon 6) + `test\maevewaterguard` (**0**) | `tagSoulName44` | Same: dead `soul\test\` twin. |
| 34 | Menon, Prince of the Bow Soul | `skeleton\menon` (27, mon 9) + `test\menon` (**0**) | `tagSoulName225` | Same: dead `soul\test\` twin. |
| 35 | Nenea Sharpclaw Soul | `maenad\neneasharpclaw` (39, mon 6) + `test\neneasharpclaw` (**0**) | `tagSoulName123` | Same: dead `soul\test\` twin. |
| 36 | Nymea Swiftshot Soul | `maenad\nymeaswiftshot` (38, mon 6) + `test\nymeaswiftshot` (**0**) | `tagSoulName325` | Same: dead `soul\test\` twin. |
| 37 | Orythroneus the Plaguebringer Soul | `zombie\orythroneus` (15, mon 3) + `zombie\oythroneus` (9, mon 0) | `tagSoulName413` | SV's own misspelled typo twin (`oythroneus`), reagent-only. R-49a: no name-drift rename, misspellings included. |
| 39 | Strongbark Soul | `ascacophus\strongbark` (21, mon 3) + `test\strongbark` (**0**) | `tagSoulName402` | Same: dead `soul\test\` twin. |
| 40 | Vulture Lord Soul | `vulture\vulturelord` (18, mon 9) + `vulture\vulturelord_n` (10, mon 0) | `tagSoulName85` | SV double-authoring; `_n` sibling is reagent-only. |

### One honest caveat on Table B

The 29 `soul\test\` rows are **not a naming defect at all**: their twins have **zero external referents**,
so no monster drops them, no formula consumes them, and no player can ever hold one. They are SV
dead content. If you want them gone that is a **retirement** decision, which defaults to WILL-VETO under
the retirement protocol, and it belongs in its own lane with the dead-content audit, not in a rename
wave. This document does not propose retiring anything.

---

# IMPLEMENTATION NOTE (for whatever wave carries this once ratified)

1. **This is a TAG-STRING change only.** Ratified rows change 1 Text string each. No `.dbr` is renamed,
   retired, re-pointed or re-wired. The three tier records of each renamed soul keep the same
   `itemNameTag`, so R-201's `itemQualityTag` prefix keeps rendering "Epic \<name\>" / "Legendary
   \<name\>" with no extra work and the R-201 gate stays green by construction.
2. **arz + Text are COUPLED and must ship together.** The mod's tag strings are written to
   `work/SoulvizierClassic/Database/uber_soul_tags.txt` by `build_svc_database.py`, and
   `build_text_arc.py` reads that file to emit `Text.arc`. So a string change means a **full DB build
   followed by a Text build in the same wave**, and both artifacts ship together. Shipping `Text.arc`
   against a stale `uber_soul_tags.txt` is the exact shape of the historical `tagSoulSVC9005`/`9006`
   orphan bug, and `build_text_arc.py` has a staleness warning for it. Run `tools/validate_tags.py`
   as the authoritative gate.
3. **Gate obligations, per chosen register.**
   * A `{^F}<X> Soul` primary needs **no** exemption; the F6 gate passes it as-is.
   * A `{^F}Soul of <X>` name **must** be added to `_HAND_DESIGNED_SOUL_TAGS` **and** removed from
     `_SOUL_NAME_STANDARD`, or the F6 auto-transform flattens it back to `<X> Soul` **before** the gate
     ever sees it (the A9 amendment documents exactly this failure).
4. **Add the cross-family invariant, or this recurs.** The R-201 gate checks distinctness WITHIN a
   family only, which is why this debt existed. The wave that lands these renames should add a
   **C3 CROSS-FAMILY** clause to `_verify_soul_tier_naming`: no two canonical soul families whose
   records are externally referenced may render the same normal-tier name. Seed its waiver list with
   the ratified Table B rows only (the SV-vs-SV set), never with anything under `svc_uber\`, so the
   next soul we author cannot re-introduce the defect.
5. **Reproduce the measurement before and after.** The scan is deterministic: load the built arz,
   group by `_soul_family_key`, resolve `itemNameTag` through the built `Text.arc`, strip `{^..}`
   colour codes, and report display names held by more than one family. Expected after all 5 primaries
   land: **35** duplicate display names, all SV-vs-SV, **0** involving `svc_uber\`.
6. **This rides any wave.** It is arz + Text only, it touches no map, no quest, no navmesh, and no
   Levels artifact, so it can be folded into any future content or fix wave that already rebuilds the
   database. It does not need a lane of its own.
7. **Player-visible surfaces to verify in game** (player-surface checklist): the item name on all
   three tiers of each renamed soul, the soul's tooltip DESC where a row changes it (rows 12, 19, 38),
   and the caravan/stash rendering of a soul picked up on an older build (TQ bakes item data at pickup,
   so re-drop a fresh one before calling a rename missing).

---

**Open Will decisions this document deliberately does NOT resolve:**
* Row 19's wire: whether `d2npc\01_akara.dbr` gets its own soul identity or is re-pointed to the
  Kallixenia tag (`docs/reports/b97_soul_identity_audit.md` sec 8). The primary name for row 19 is
  safe either way.
* Retiring SV's 29 dead `soul\test\` soul families (retirement protocol, WILL-VETO by default).
* Row 11 and row 32: whether SV's own live two-monsters-one-name shares are worth breaking law #2 for.
  This proposal says no.
