# b97 - SOUL-vs-MONSTER IDENTITY AUDIT (round 2)

**Will (2026-07-27, verbatim):** *"we also need to do an audit of the hero monsters vs the souls
that they drop since i can see that some of the heroes are dropping the wrong souls or souls for
other boss monsters i think"*

**Verdict: Will is right, and the audit found the exact mechanism.** **22** records drop a soul
that belongs, by name, to a *different named creature that also drops it*. Every one is now
detached, at the correct layer, behind a permanent gate.

- Branch `fix/soul-identity`, tag `build59-dev` (round 1 shipped as `build58-dev`).
- Audit tool (reproducible over any `.arz`): `tools/audit_soul_identity.py`.
- Fix + gate: `tools/patches/soul_identity.py` (patches-registry module).
- Full **926-row** table: [`b97_soul_identity_table.md`](b97_soul_identity_table.md).

---

## 0. WHAT CHANGED IN ROUND 2 (read this first)

Round 1 was correct in everything it did and **incomplete in what it looked at**. The vet caught it,
and the gap contained a real, live mismatch of exactly the class Will reported. Four defects, all
now fixed and all now locked by a test:

| # | Defect (round 1) | Consequence | Fix |
|---|---|---|---|
| **D1** | Both the audit and the shipped gate were scoped by a path predicate requiring `\creature\` or `\creatures\` (`_is_creature`). | **97 live soul carriers were never judged** - all 25 of `records\drxcreatures\` (shipping DRX/Urder content), `records\test\`, `records\item\equipmentring\soul\test\`, the pet trees and the quest proxies. The 850-row table contained **zero** drxcreatures rows, and the "roster-wide, list-free, any future content module fails the build" claim was false for anything authored outside `\creature(s)\`. | `_is_soul_carrier(db, name)` - the roster is now **every record**, minus pets and quest spawn proxies, each excluded with a proof that excluding fails safe. |
| **D2** | Hiding in that gap: `records\drxcreatures\xurder\d2npc\01_akara.dbr` displays **"Akara"**, is `Quest`-classified, and dropped **"Kallixenia ~ Liche Queen Soul"** at 66% - while the real `Kallixenia ~ Liche Queen` (`xsq02_lichequeen_36`) drops an identically-named soul at the same 66%. The wire is **ours**: `apply_svc_patches._create_kallixenia_soul`. Three more (`soul\test\us_lysiaspellbreaker_15{,_e,_l}`, displaying "Nenea Sharpclaw") were hidden the same way. | 4 real mismatches shipped through the "roster-wide" gate. | Detached by the same rule. **18 -> 22.** |
| **D3** | Carriers were grouped by the soul **.dbr filename** family (`_soul_family`, basename only) - repeating *inside the gate* the very filename-is-identity mistake the gate exists to punish. It **merged** two genuinely different items that share a basename (`soul\abyssalliche\kallixenia_*` = SV's Liche Queen soul, `soul\svc_uber\kallixenia_*` = ours) and would **split** two items that share a name. | The ORPHAN GUARD could be fooled: zeroing a carrier could take a real item dark while the guard saw the *other* item's owner and passed. | Grouping key is now the soul's **display name** (`name_key`). A new **ITEM-DETACH GUARD** fails the build if any soul ITEM record loses its last live carrier without a reviewed waiver. |
| **D4** | `apply()` runs inside `run_registry()`, which is **before** `run_registry_gates()` calls `_apply_soul_naming_standard()` - the documented *"final authoritative override of the `tags` dict"*. `verify()` runs **after** it. So `apply()` judged identity against names that are **not the ones the player sees**, and could disagree with its own `verify()`. It did: `tagSVCSoulKallixenia` is `{^F}Soul of Kallixenia` at apply() time and `{^F}Kallixenia ~ Liche Queen Soul` in the shipped `Text.arc`. | Latent build-breaker + wrong verdicts on any F6-renamed soul. | `_display_tags()` now applies the same `_SOUL_NAME_STANDARD` override, so both passes judge the shipped text. |
| **D5** | ARCHETYPE vs NAME-DRIFT was split by a **row count** (exactly 1 unmatched carrier -> NAME-DRIFT). | Three archetype rows were filed as "by design, just spelled differently": **Cynisca, Princess of Sparta**, **Corpse Wake**, **Meritamen the Shadowcaller** - and §3 RC-3 cited Meritamen as a confirmed clone-inheritance case while §5b filed it as by design. Conversely the true 1:1 drift (Wither Mound <-> Speckled Jim) was labelled SHARED-ARCHETYPE. | The split is now **data-derived**: does a record that owns the soul's name exist, carrying the same soul item, gated dead? All three are relabelled ARCHETYPE-SHARED; Wither Mound is relabelled NAME-DRIFT. |

Two extra round-1 nits are also fixed: `audit_soul_identity.py` and the negative test hard-defaulted
to `<repo>/upstream/...` (gitignored, **absent in a fresh worktree**, so neither tool would run) -
they now use shared resolvers; and `--markdown out.md` leaked its value into the positional list, so
the flag crashed the tool on an `ArcArchive` assert.

**PETS ARE DELIBERATELY NOT CARRIERS** (the vet asked for this to be decided explicitly). A pet is
spawned by the player or by a monster skill and yields no loot to the player; its `lootFinger2Item*`
fields are inherited clone noise. Counting them is not merely useless, it is *harmful*: the 0.5%
monster-scroll pet `item\miscellaneous\monsterscrolls\pets\maenad_sorceress_20.dbr` displays
"Maenad ~ Sorceress", which would crown a **player summon** the rightful owner of the Maenad
Sorceress Soul and convict the real 50% Boss that legitimately drops it (Meritamen the
Shadowcaller). Verified: widening the scope to *everything* produces exactly that conviction.
Excluding a record can only ever **remove** a conviction (an excluded owner turns its whole name
group into the untouched no-owner case), so the exclusion fails safe by construction. `T7` in the
negative test locks it. Quest spawn proxies and loot pools (`\proxies\`) are excluded for the same
reason - they are not creatures, they mirror the boss they spawn. **`records\test\` and
`records\item\equipmentring\soul\test\` monsters DO count**: they are Monster records with live
rolls, and judging them is free (the only convictions there are the Nenea/Lysia trio, whose soul
stays live on the real Lysia Spellbreaker).

---

## 1. Scope audited

Ground truth = the deployed arz
`.../CustomMaps/SoulvizierClassicDEV/Database/SoulvizierClassicDEV.arz` (read-only), cross-checked
against this lane's own build, **SV 0.98i** upstream, and the **TQAE base game** database. Display
names come from SV 0.98i's `Text_EN.arc` **unioned with the shipped mod `Text.arc`** - i.e. the text
the player actually reads.

| Quantity | Count |
|---|---|
| Records in the arz | 51,085 |
| Records carrying soul loot (`lootFinger2Item1`) | 1,278 |
| **Records with a LIVE soul drop (`chanceToEquipFinger2` > 0), ROSTER-WIDE** | **929** |
| ... of which pets / quest proxies (not carriers, see §0) | 3 / 2 |
| **JUDGED live soul carriers** | **926** |
| ... of which Hero / Boss / Quest / Common | 626 / 174 / 121 / 5 |
| ... of which outside round 1's `\creature(s)\` scope | **97** (drxcreatures 25, `soul\test\` 51, `records\test\` 4, pets 10, skills 5, proxies 2) |
| **Distinct soul NAMES actually dropped** | **615** |
| Distinct monster display names dropping a soul | 628 |
| Carriers skipped as unjudgeable (name does not resolve -> never convicted) | 9 |

Every difficulty variant and every rank is included; the count is records, not creatures, which is
why 926 records map to 628 named creatures (normal/epic/legendary variants of one boss are separate
records). The 9 unjudgeable are the SV `soul\test\swift_*` dummies (no `description` tag at all)
plus `records\test\boss_coldworm50`/`boss_dagon_66`; an unknown identity is never convicted.

**The same roster reproduces on this lane's own build:** 926 live carriers pre-fix, **904** after the
22 detachments (926 - 22 = 904, exact).

## 2. Classification

Over the **pre-fix** ground-truth arz (the state Will is playing):

| Verdict | Rows | Meaning |
|---|---|---|
| **MATCH** | **878** | The soul's identity is the monster's identity. |
| **MISMATCH** | **22** | Drops a soul whose named owner is a *different* creature that also drops it. **The bug.** |
| ARCHETYPE-SHARED | 14 | No live carrier owns the name, **and** a record that does own it exists carrying the same soul but gated dead (rank-gated Common/Champion). Soul named for a monster *type*. By design. |
| NAME-DRIFT | 12 | No live carrier owns the name and **no record anywhere** carries it: the soul is its carrier's soul under a different spelling, or a mod-authored marquee name. Not identity theft. |

Over the **fixed** build the same table is MATCH 878 / **MISMATCH 0** / ARCHETYPE-SHARED 14 /
NAME-DRIFT 12 across 904 live rows.

Identity is compared on **display text** (`description` tag -> Text), never on the `.dbr` filename.
That distinction *is* the finding - see §3.

---

## 3. Root causes (grouped, so the fix is systemic)

### RC-1 - The `.dbr` filename is not an identity. The base game reuses one hero filename across several named heroes.

TQ ships hero records as `hero_<name>_<level>.dbr`, and the numbered siblings are **different
heroes**, distinguished only by their own `description` tag. Verified directly in the TQAE base
`database.arz`:

| Record | Base-game `description` | Resolves to |
|---|---|---|
| `ratman\hero_wheedletongue_39.dbr` | `tagMonsterName1203` | Wheedletongue the Magnificent |
| `ratman\hero_wheedletongue_41.dbr` | `tagMonsterName1206` | **Fesil the Quick** |
| `ratman\hero_wheedletongue_43.dbr` | `tagMonsterName1209` | **Sinnet Patchfur** |
| `scorpos\hero_kaaltspeartail_30.dbr` | `tagMonsterName1214` | **Errak Bonecarver** |
| `scorpos\hero_kaaltspeartail_33.dbr` | `tagMonsterName1215` | **Sartt Soulrender** |
| `neanderthal\hero_grom_31.dbr` | `tagMonsterName1204` | **Korat Bearkin** |
| `djinn\hero_adarathelovely_43.dbr` | `tagMonsterName1136` | **Raghd Bloatworm** |

`build_svc_database.wire_souls_to_monsters` matches souls to monsters by **filename**
(`_monster_clean_name` -> `hero_wheedletongue`), so all three ratman records qualify for the
Wheedletongue soul. amgoz1's SV 0.98i data made the same filename-shaped assumption upstream and
pre-attached the donor soul to the whole family.

**Why the existing F1 gate never caught it:** `_verify_no_fuzzy_cross_wire` scores the soul name
against the monster's *filename* - the very axis that is wrong (`'wheedletongue'` **is** a substring
of `'hero_wheedletongue'`, so it "qualifies") - and additionally whitelists every pairing SV 0.98i
authored. The 2026-07-05 yeti fix closed the **rank** dimension (419 records); this is the
**identity** dimension it explicitly did not cover.

### RC-2 - Our build ACTIVATED pairings SV shipped dead.

This is why Will is seeing it *now*. Provenance, measured per record against SV 0.98i:

| SV 0.98i state | Records | What our build did |
|---|---|---|
| loot ref present, `chanceToEquipFinger2 = 0.0` (**dead**) | **8** of 18 | `wire_souls_to_monsters`'s "already had souls" branch set 25/50 -> **latent upstream mis-pairing became a live drop** |
| loot ref present, `chance = 5.0` (amgoz shipped it live) | **9** of 18 | raised 5 -> 50, turning a 1-in-20 upstream wart into a coin flip |
| no pairing in SV **or** base at all | **1** of 18 (`um_rocksting_29`) | **our own** fuzzy filename wire created it |

Measured by `scratchpad/prov_split.py` against `upstream/soulvizier_098i` + the TQAE base arz. Note
the 7 base-game `hero_*` records carry **no** Finger2 soul loot in the base game at all - every
pairing is SV-authored or ours.

So the wrong souls are *upstream data*, but the visibility is *ours*: the mod's centerpiece feature
(activate every Hero/Boss/Quest soul drop) turned amgoz's dead mis-pairings on without ever asking
whether the soul's identity matched the monster's.

### RC-3 - SV/mod clones kept the donor's soul after the description changed (the predicted clone-inheritance class).

`um_inkeyes_45` / `um_inkeyes2_45` display **"Blood-Eyes"** but carry `wheedletongue_soul_{n,e,l}`;
`um_phagia_44` is a `human\` record displaying **"Meritamen the Shadowcaller"** carrying the maenad
sorceress soul; `us_poisonsiren_14` is a `gorgon\` record displaying **"Thelxiepeia Venomlip"**
carrying **Aquardia the Coral Queen**'s soul (a cross-family inheritance). Same signature, different
donor: the clone kept `lootFinger2Item*` while the identity was rewritten.

---

## 4. THE 18 MISMATCHES (the deliverable list)

All are now `chanceToEquipFinger2 = 0`. `lootFinger2Item1` is deliberately left intact (detach the
roll, keep the data - the A4 Aphiastas-zero / R-45 tombguardian shape), so the change is reviewable
and reversible. **Every one of these souls remains obtainable from its rightful owner**, proven
mechanically in `apply()` (ORPHAN GUARD).

### RC-1 group - base-game hero-filename reuse (7)

| Monster (what the player sees) | Was dropping | Rightful owner (keeps it) | Record |
|---|---|---|---|
| Fesil the Quick | Wheedletongue the Magnificent Soul | Wheedletongue the Magnificent | `ratman\hero_wheedletongue_41.dbr` |
| Sinnet Patchfur | Wheedletongue the Magnificent Soul | Wheedletongue the Magnificent | `ratman\hero_wheedletongue_43.dbr` |
| Errak Bonecarver | Kaalt Speartail Soul | Kaalt Speartail | `scorpos\hero_kaaltspeartail_30.dbr` |
| Sartt Soulrender | Kaalt Speartail Soul | Kaalt Speartail | `scorpos\hero_kaaltspeartail_33.dbr` |
| Korat Bearkin | Grom Soul | Grom | `neanderthal\hero_grom_31.dbr` |
| Raghd Bloatworm | Adara the Lovely Soul | Adara the Lovely | `djinn\hero_adarathelovely_43.dbr` |
| Prince Ch'kik't the Horrible | Z'kar Flamespinner Soul | Z'kar Flamespinner | `tropicalarachnos\hero_princech'kik't_37.dbr` |

### RC-3 group - clone kept the donor's soul (10)

| Monster | Was dropping | Rightful owner (keeps it) | Record |
|---|---|---|---|
| Blood-Eyes | Wheedletongue the Magnificent Soul | Wheedletongue the Magnificent | `ratman\um_inkeyes_45.dbr` |
| Blood-Eyes | Wheedletongue the Magnificent Soul | Wheedletongue the Magnificent | `ratman\um_inkeyes2_45.dbr` |
| Wahr'Ner Shadowpaw | Nephi'tek the Lasher Soul | Nephi'tek the Lasher | `shadowstalker\um_wahr_33.dbr` |
| Nazur the Shrouded | Nephi'tek the Lasher Soul | Nephi'tek the Lasher | `shadowstalker\us_nazur_34.dbr` |
| Masai-yin the Grovekeeper | Syrinx of the Tainted Meadow Soul | Syrinx of the Tainted Meadow | `naiad\ur_masai_43.dbr` |
| Xuannu the Twilight Matron | Syrinx of the Tainted Meadow Soul | Syrinx of the Tainted Meadow | `naiad\ur_uber_45.dbr` |
| Morbi | Venemurax Soul | Venemurax | `limos\um_morbi_17.dbr` |
| Mormo | Storm Crow Soul | Storm Crow | `carrionbird\us_mormo_16.dbr` |
| Daechalcos | Scarabaeus Soul | Scarabaeus the Desert King | `antlion\us_frostscarab_35.dbr` |
| Thelxiepeia Venomlip | Aquardia the Coral Queen Soul | Aquardia, the Coral Queen | `gorgon\us_poisonsiren_14.dbr` |

### RC-2 group - our own fuzzy filename wire (1)

| Monster | Was dropping | Rightful owner (keeps it) | Record |
|---|---|---|---|
| Colossal Scorpion | Rocksting Soul | Rock Sting (`um_rocksting_30`) | `scorpion\um_rocksting_29.dbr` |

### RC-4 group - ROUND 2: the 4 the `\creature(s)\` scope predicate hid

| Monster | Cls | Was dropping | Rightful owner (keeps it) | Record |
|---|---|---|---|---|
| **Akara** | Quest 66% | **Kallixenia ~ Liche Queen Soul** | Kallixenia ~ Liche Queen (`xsq02_lichequeen_36`) | `drxcreatures\xurder\d2npc\01_akara.dbr` |
| Nenea Sharpclaw | Hero 2% | Lysia Spellbreaker Soul | Lysia Spellbreaker | `item\equipmentring\soul\test\us_lysiaspellbreaker_15.dbr` |
| Nenea Sharpclaw | Hero 2% | Lysia Spellbreaker Soul | Lysia Spellbreaker | `...\us_lysiaspellbreaker_15_e.dbr` |
| Nenea Sharpclaw | Hero 2% | Lysia Spellbreaker Soul | Lysia Spellbreaker | `...\us_lysiaspellbreaker_15_l.dbr` |

**RC-4 root cause = OUR OWN AUTHORING, not upstream.** `apply_svc_patches._create_kallixenia_soul`
(line ~7186) hard-codes `MONSTER = records\drxcreatures\xurder\d2npc\01_akara.dbr` and calls
`_create_soul(..., 'tagSVCSoulKallixenia', ..., 66.0)`. The function's own docstring says
*"Kallixenia (01_akara) - lich-queen caster"*, so the author believed that record **was** Kallixenia -
but its `description` tag is DRX's `tagD2NPCakara` = **"Akara"**, and it was never changed. Meanwhile
the base game's real Kallixenia carries `soul\abyssalliche\kallixenia_soul_*` (`tagSoulName234`,
same displayed name) at the same 66%. Two identically-named souls, two different creatures, one of
them called Akara. That is Will's report verbatim. A pointer comment now sits at the authoring site.

The Nenea/Lysia trio is SV's own copy-paste: three legacy `soul\test\` monster records carrying
Lysia Spellbreaker's soul under a pasted "Nenea Sharpclaw" description tag.

**Why round 1's F1 gate AND round 1's own gate both missed all four:** F1 scores against the
filename and runs at `build_svc_database.py:3512`, long before `apply_all_extended_patches` (:3854)
authors the mod's soul wires; round 1's gate ran late enough but only looked inside `\creature(s)\`.

---

## 5. NOT bugs - left untouched, and why (no whitelist needed)

The rule below is structured so these are preserved **by construction**, not by a hand-list.

> **ROUND-2 RELABELLING.** The split below is no longer decided by a row count. For every soul name
> with no live identity-owning carrier, the audit asks the DATA: *does a record that owns this name
> exist, carrying this same soul item, gated dead?* Yes -> ARCHETYPE-SHARED (the soul is a monster
> **type**, and the archetype's own Common/Champion records are exactly those gated-dead owners).
> No -> NAME-DRIFT. This moves **Cynisca, Corpse Wake and Meritamen** out of "name drift" (they are
> archetype souls on named heroes, which §3 RC-3 already said about Meritamen - §3 and §5b
> contradicted each other in round 1) and moves **Wither Mound <-> Speckled Jim** into it (a true
> 1:1 rename: no "Speckled Jim" exists anywhere in the roster).

### 5a. ARCHETYPE-SHARED (14 rows, 5 soul names) - the soul is a monster *type*, not a hero

| Soul | Live carriers (named uniques) | The gated-dead owner that proves it is an archetype |
|---|---|---|
| Satyr Fire Magi Soul | Aniketos the Sacrificer x5, Phlegraeus Flame Chanter | `Dark Satyr ~ Fire Magi` / `Satyr ~ Storm Mage` @ 0.0 |
| Sandwraith Soul | Sandspirit ~ Dustwarrior x2, Royal Advisor Hemetre x2, Djenebti the Dust-Drinker | `Sandwraith` @ 0.0 |
| **Awakened Dead Soldier Soul** | **Cynisca, Princess of Sparta** | `Awakened Dead ~ Soldier` @ 0.0 |
| **Diseased Vulture Soul** | **Corpse Wake** | `Diseased Vulture` @ 0.0 |
| **Maenad Sorceress Soul** | **Meritamen the Shadowcaller** (Boss, 50%) | `Maenad ~ Sorceress` @ 0.0 |

The archetype's own Common/Champion records carry the loot ref but are gated dead by the 2026-07-05
yeti rank-fix, so **no carrier owns the name** and the named uniques are the only way to obtain the
soul. Zeroing these would make the soul **unobtainable** - the opposite of a fix. (Meritamen is also
the record that proves pets must not be carriers: the `Maenad ~ Sorceress` monster-scroll **pet** is
live at 0.5%, and counting it would convict this Boss. See §0.)

### 5b. NAME-DRIFT / mod-themed marquee (12 rows) - sole carrier, no identity stolen

`Wither Mound` <-> Speckled Jim Soul (x2), `Clazomenaeus the Unstoppable` <-> Crowboar Soul,
`Shriekbrood the Collector` <-> Grimshell Soul, `Skull Spine` <-> Spinebone Soul, `Vile Crawl` <->
Vilerotter Soul, `The Ethereal One` <-> "The Etheral One Soul" *[sic - a spelling typo in the SV
soul tag]*, `Kir4` <-> Kir Trap Soul, `Aegobolus` <-> Soul of the Blood Shaman, plus the
mod-authored marquee names `Alkyoneus, the Hoard Unbound` <-> Soul of the Gaoler, `Tantalus, the
Hunger Unbound` <-> Soul of the Insatiable, `The Helepolis, Taker of Cities` <-> Ash of the Funeral
Games. You kill that creature, you get that creature's soul - it is just spelled differently.
Renaming any of them is a **text/design** call (amgoz1 creative bar), so they are listed for Will in
§8, not changed.

### 5c. Souls that share a display NAME across two distinct items (found in round 2, not a bug here)

Grouping by display name surfaced four names carried by **two different soul item families**:

| Display name | Item families |
|---|---|
| `{^F}Kallixenia ~ Liche Queen Soul` | `abyssalliche\kallixenia` (SV) + `svc_uber\kallixenia` (ours) - **this one WAS a mismatch**, see RC-4 |
| `{^F}Charon Soul` | `charon\charon` + `svc_uber\boss_charon` |
| `{^F}General Yrrt'ik Soul` | `formicid\generalyrrtik` + `svc_uber\rainbowbright` |
| `{^F}Plague Feast Soul` | `carrionbird\plaguefeast` + `svc_uber\nomnom` |

The last three are **not** identity thefts (every carrier of each name legitimately owns it), so the
rule leaves them alone - but the player does see two different rings with the same name. Registered
as **BL-b97-DEBT-8** for the naming lane; not touched here (this lane authors 0 tags).

### 5d. Rulings honoured (checked before touching anything)

`docs/WILL_RULINGS.md` re-read for this wave. **Nothing ruled was overturned:**

- **R-48** (Enslaver + Devourer souls at 100%) - both are **sole carriers** of `enslaver_soul_` /
  `blood_toxeus_soul_`, so the rule never considers them. `soul_identity` is registered *after*
  `toxeus_souls_100` and its `verify()` re-reads the final db: both are still 100%.
- **R-43** (High Priest soul summons the High Priest), **R-45** (Tomb Guardian soul removed;
  `um_tombguardian_26` stays Common at 0.0), **R-42** (50/66/25 split), **R-44** (crowboar summon),
  bloodtip / gustleech, and the **legion double-soul chains** (`legion_soul_stages` +
  `double_soul_rulings`) - all untouched. This module writes exactly one field, only downward, only
  on the 22 records above; the 50/66/25/100 classifier is not modified. Re-verified on the round-2
  arz: Enslaver **100.0**, Devourer **100.0**, `um_tombguardian_26` **0.0** Common.

---

## 6. The fix - `tools/patches/soul_identity.py`

**THE RULE** (data-derived; no hand-list decides who loses a drop):

> For every soul **NAME** S (the text the player reads on the item), let CARRIERS(S) be the records
> with a live soul drop that reference an item displaying S.
> **If some carrier's display name identity-matches S, every other carrier whose display name does
> not match is an identity thief -> `chanceToEquipFinger2 = 0`.**
> **If no carrier identity-matches S, nothing is touched.**

The second clause is load-bearing: it is *why* §5a and §5b are safe without a whitelist, and it makes
orphaning a soul NAME structurally impossible.

**ROSTER** (`_is_soul_carrier`): every record in the database that holds live soul loot, minus
player/summon **pets** and quest **spawn proxies** - each justified in §0, each failing safe
(excluding a record can only remove a conviction, never add one). Round 1's `\creature(s)\` path
predicate is gone.

**GROUPING** (`name_key`): the soul's **display name**. Round 1 grouped by the .dbr basename, which
merged `soul\abyssalliche\kallixenia_*` with `soul\svc_uber\kallixenia_*` - two different items -
and would have split two items that share a name. `_soul_family()` survives for reporting only and
is now directory-qualified.

Layer choice (BL-103 fix-upstream): the rule depends on the **final** carrier set, which only exists
after every soul-wiring and drop-rate writer has run, so a patches-registry module is the correct
seam - not a hand-patch, and not a `wire_souls_to_monsters` edit that could only ever see half the
picture. Identity matching is done on display text; the `.dbr` filename - the axis that caused the
defect - is never consulted.

Supporting changes: `build_svc_database.main()` loads SV 0.98i's `Text_EN.arc` into
`apply_svc_patches._SV098I_NAME_TAGS` (the same module-global hand-off the F6 soul-provenance sets
use), outside the prefix cache so a cached payload can never ship an empty table; and
`_display_tags()` now applies `_SOUL_NAME_STANDARD` so `apply()` judges the **same, final** names
`verify()` and the shipped `Text.arc` will carry (round-2 defect D4).

## 7. The gate (this must never regress)

1. **`verify()` - the permanent, LIST-FREE invariant.** Runs in registry step 4 over the FINAL merged
   db (after the whole gate battery *and* the testing drop-rate forcer): re-runs the rule and
   requires the answer to be **empty**. Any future clone, wire, or content module that hands a
   creature another named creature's soul **fails the build** - and, after round 2, that is true for
   **any record path**, not only `\creature(s)\`.
2. **REVIEW GATE in `apply()`.** The rule's verdict is asserted equal to `_REVIEWED` (the 22 rows
   classified here, each annotated with monster / stolen soul name / rightful owner). This is *not*
   the mechanism that decides who loses a drop - the rule is - it is the proof that the current
   data's verdict is the one a human reviewed. Content drift fails loud asking for review rather
   than silently zeroing a boss's soul. *(It already earned its keep: it is what stopped the first
   round-2 build when the pre-F6 tag table made Akara look clean.)*
3. **ORPHAN GUARD in `apply()`.** After zeroing, every affected soul **name** is re-checked to still
   have a **live matching carrier**; if not, the build aborts rather than make a soul unobtainable.
4. **ITEM-DETACH GUARD in `apply()` (new in round 2).** The orphan guard is about the NAME; this one
   is about the specific **item record**. Two distinct items can share one display name, so zeroing a
   thief can leave a real, authored item with no live carrier at all while the name still looks fine.
   Any such item must appear in `_ACCEPTED_ITEM_DETACH` with a written justification or the build
   **fails**. Exactly one waiver exists today (`svc_uber\kallixenia_soul_{n,e,l}` - see §8).
5. **Planted negative test** (`tools/contracts/tests_soul_identity_negative.py`, **21 assertions**):
   T1 clean db passes; **T2** re-arms the REAL Fesil-the-Quick mismatch and proves `verify()` fires;
   T3 a synthetic cross-wire fires; T4 the Satyr Fire Magi archetype is *not* flagged and keeps a
   live carrier; T5 filename is not identity; **T6 (new)** plants a thief on a real record
   **outside** `\creature(s)\` (`drxcreatures\...\01_akara.dbr`) and proves `verify()` fires - the
   permanent guard against re-narrowing the scope, the exact round-1 NO-GO; **T7 (new)** re-arms the
   monster-scroll **pet** and proves it convicts nobody new and leaves the real Boss alone.

**Whitelist:** the module ships with **no** whitelist for who loses a drop. Every by-design family in
§5 is preserved by clause 2 of the rule itself, which is strictly stronger than a hand-maintained
exception list (it cannot go stale, and it cannot be padded to silence a real bug). The two
review sets that do exist - `_REVIEWED` and `_ACCEPTED_ITEM_DETACH` - are *assertions*, not
permissions: they make the build fail when the verdict moves, they never cause a zero.

## 8. WILL DECISIONS (nothing below was changed)

1. **"Should have its own soul but none exists" (10 creatures).** Every RC-3 monster in §4 now drops
   nothing at all: Blood-Eyes, Wahr'Ner Shadowpaw, Nazur the Shrouded, Masai-yin the Grovekeeper,
   Xuannu the Twilight Matron, Morbi, Mormo, Daechalcos, Thelxiepeia Venomlip, plus the RC-1 heroes
   Fesil the Quick, Sinnet Patchfur, Errak Bonecarver, Sartt Soulrender, Korat Bearkin, Raghd
   Bloatworm, Prince Ch'kik't, Colossal Scorpion. **Creating a soul for any of them is new content**
   (amgoz1 creative bar applies), so none was invented. Two of them are notable: **Xuannu the
   Twilight Matron** is a *Boss*, and **Blood-Eyes** is a *Boss* placed in the ratman pool - the two
   most likely to be missed. Say the word and they get bespoke, monster-identity-driven souls.
2. **NAME-DRIFT renames (§5b).** Cosmetic only. Cheapest real win: `"The Etheral One Soul"` is a
   plain **misspelling** of The Ethereal One. Also candidates: Crowboar -> Clazomenaeus, Grimshell ->
   Shriekbrood, Spinebone -> Skull Spine, Vilerotter -> Vile Crawl. Text-only change; say which (or
   "all typos only").
3. **Iron Lore dev-dummy souls are shipping.** `xpack\creatures\monster\zzdev\` holds the original
   developers' test dummies (z_arthur, z_ben, z_chooch, z_cory, z_dave, z_david, z_frazier, z_josh,
   z_morgan, z_nate, z_parnell, z_scott, z_shawn, z_tom, z_~v~), all Quest-classified at **66% soul
   drop**, and our build authored real soul items for three of them
   (`soul\svc_uber\z_ben_soul_{n,e,l}.dbr`, `z_tom_soul_{n,e,l}.dbr`, plus a `~V~` soul). They are
   identity-*correct* (Ben drops "Ben Soul"), so the identity gate does not touch them, and they are
   almost certainly unreachable - but "Ben Soul" is in the shipped roster. Zeroing the drops or
   retiring the items are both **retirement-protocol** decisions (WILL-VETO by default), and the
   souls may sit in `svc_uber` formula chains, so nothing was touched. Recommend: zero the zzdev
   drops, leave the items.
4. **amgoz's Dropbox conflict duplicates.** `boss_gorgon_sstheno_22 (amgoz-qosmio's conflicted copy
   2013-08-07).dbr`, `copy of am_hero_29.dbr`, `um_speckledjim_45 (pcos modstridende kopi
   2014-09-10).dbr`, `um_cyniga_17 (pcos ...)`, `um_liophotia_18 (pcos ...)` and friends are
   compiled-in junk twins that also drop souls (66%). They are counted in the by-design buckets
   above, and one of them (`um_speckledjim_45 (pcos ...)`) is half the reason Speckled Jim reads as
   a 2-row family. Already a known separate data-hygiene ticket (the F1 gate excludes them
   explicitly); flagged again, still out of scope for an identity lane. **BL-b97-DEBT-9.**
5. **ROUND 2 - AKARA vs KALLIXENIA (the one that needs a real answer).** `01_akara.dbr` is now at
   `0.0`, so our bespoke `soul\svc_uber\kallixenia_soul_{n,e,l}` (a full 3-tier lich-queen caster
   soul: `lichequeen_soulstrike` proc, Death Chill + Ternion augments) has **no live carrier** and is
   currently unobtainable. Nothing was deleted - the item records and the loot ref are intact
   (retirement protocol), and the *name* "Kallixenia ~ Liche Queen Soul" is still obtainable from the
   real Kallixenia. Three ways out, pick one:
   - **(a) leave it** - Akara drops nothing, our bespoke soul stays shelved. *(shipped state)*
   - **(b) make Akara BE Kallixenia** - set `01_akara.dbr`'s `description` to `xtagxQuestMonster01`,
     the tag the sibling decoration `x01_akara.dbr` already uses and the identity our own code
     comment intends. One field. He then legitimately drops the bespoke soul. Cost: two creatures in
     the world share the name "Kallixenia ~ Liche Queen", and two differently-statted rings share
     one name (see §5c).
   - **(c) give Akara his own identity** - a bespoke "Akara" soul (new content, amgoz1 creative bar),
     and re-point the lich-queen soul at a lich-queen.
   **BL-b97-DEBT-7.**
6. **ROUND 2 - duplicate soul NAMES on distinct items (§5c).** Charon, General Yrrt'ik and Plague
   Feast each exist as two different rings with the same displayed name (one SV, one ours). Not an
   identity theft, but a player-visible collision. Text/design call. **BL-b97-DEBT-8.**
7. **ROUND 2 - `verify_soul_drop_rates.py` has the SAME `\creature(s)\` scope hole** this lane just
   closed in the identity gate. It is why the round-2 zeroes needed no new `_KNOWN_EXCEPTIONS`
   waivers (all four sit outside its roster). Widening it would pull every `drxcreatures` boss into
   the RANDOM/PLACED/BOSS classifier and is a wave of its own. **BL-b97-DEBT-10.**

## 9. Build + proofs (BUILD ONLY - not deployed)

`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, DB-only lane. **No map rebuild, no deploy** (concurrent lanes
are editing the arz; the orchestrator merges and deploys once).

| artifact | md5 |
|---|---|
| **ROUND-2 built arz (FOR THE ORCHESTRATOR)** `.claude/worktrees/soul-identity/work/b97r2/Database/SoulvizierClassic.arz` | **`41bc1d9e75df01ee538e2b25f8e0bb7f`** (55,424,077 B) |
| round-1 arz (commit `3785843`, superseded) | `fcc6fad38d9b8a0fd54a337e23e5ffa8` (55,424,089 B) |
| baseline arz (main `8c3445c`, pre-change) | `1c27d5fa650b5c076696db4ad379672f` (55,424,142 B) |
| `Text.arc` rebuilt from the build-emitted `uber_soul_tags.txt` | `fcca49277b9d31ed451e4a6843898843` - **byte-identical to round 1 and to baseline** (this lane authors 0 tags) |
| `uber_soul_tags.txt` | `49b6d85ba15236aa5df60f610e3a7bf0` - **byte-identical to round 1** |

- **RECORD-DIFF, round 2 vs round 1: 0 added, 0 removed, 4 modified** - exactly the 4 RC-4 records,
  one field each, `chanceToEquipFinger2` `66.0 -> 0.0` (Akara) and `2.0 -> 0.0` (the Lysia trio),
  **dtype 1 (FLOAT) preserved on both sides**. Nothing else in 51,085 records moved. Chained with
  round 1's proven diff vs `main` (0 added / 0 removed / 18 modified, same single field), the total
  delta vs baseline is **0 added, 0 removed, 22 modified, one field each**.
- **Build exit 0**, every fail-loud invariant green: soul-leak (0 non-Hero/Boss/Quest drop a soul),
  soul-augment, soul item-skill activation (1388 souls), F1 cross-wire, F6 soul-naming,
  spawn-eligibility (44 proxies), boss-kit clone-shape, A7 Occult/Hunting golden (84 waived /
  0 other), b77 unlock-alignment (238 buttons, 13/13 waivers).
- **Registry:** `[33/34] soul_identity` -> `modified 22 record(s), 0 tag(s)`; **929 live carriers
  judged roster-wide across 616 soul names**, 18 names with no identity-owning carrier left untouched
  by construction, **9 carriers skipped as unjudgeable** (the SV `soul\test\swift_*` dummies and
  `records\test\boss_coldworm50`/`boss_dagon_66`, none of which has a `description` tag at all).
- **ITEM-DETACH GUARD** printed its 3 reviewed waivers (`svc_uber\kallixenia_soul_{n,e,l}`) and would
  have **failed the build** on any un-reviewed item going dark.
- **`[soul_identity] verify OK`** in step 4 over the FINAL merged db (`build_r2.log:1599`).
- **`validate_tags`: PASS** - all 356 referenced mod tags present in `Text.arc`; the 2 remaining
  WARNs are the pre-existing base/SV `tagNewMonster46/66` backlog items.
- **`verify_soul_drop_rates --gate`: PASS** (exit 0). Testing-forcer survival **832 enabled -> 100,
  446 gated stay 0** - **identical to round 1**, because all four round-2 records sit outside that
  gate's own `\creature(s)\` roster (BL-b97-DEBT-10). Planted post-wire-stomp negative test still
  CAUGHT. R-48 spot-checks inside the gate: Enslaver `100.0`, Devourer `100.0`.
- **Contracts `--only souls,summons`** (with the real resource arcs + base game dir): **0 P0 / 0 P1 /
  112 P2, GATE PASS**, and the round-1 arz run through the identical invocation yields the
  **byte-identical violation set** (112 both, 0 only-in-r1, 0 only-in-r2), so the pre-existing P2s are
  provably untouched. *(Without `--resource-arc-dir` the same run reports 102 bogus P0 MONSTER-MESH
  violations - the BL-b97-DEBT-6 environment trap; always pass it.)*
- **Planted negative test:** `tests_soul_identity_negative.py` on the round-2 arz - **ALL 21
  ASSERTIONS HELD**, including the two new ones. Run against the **round-1** arz the same suite
  correctly **FAILS T1** and names Akara plus the Lysia trio, which is the machine-checked proof that
  round 1 shipped the gap.
- **Ruling spot-checks on the round-2 arz:** R-48 Enslaver `100.0` / Devourer `100.0`; R-45
  `um_tombguardian_26` `0.0` Common; the real Kallixenia `xsq02_lichequeen_36` still `66.0` with her
  `abyssalliche` soul intact; `01_akara` `0.0` with its `lootFinger2Item1` (3 refs) intact.
- **Audit reproduced independently of the build:** `py tools/audit_soul_identity.py <arz>` over the
  deployed ground-truth arz gives 926 judged carriers / 615 soul names / MATCH 878 / MISMATCH 22 /
  ARCHETYPE-SHARED 14 / NAME-DRIFT 12, and over this lane's built arz gives 904 / 615 / 878 / **0** /
  14 / 12. 926 - 22 = 904, exact.

## 10. Debt register

- **B97-DEBT-1** - the detached monsters have no soul of their own (§8 item 1). Awaiting Will.
- **B97-DEBT-2** - `wire_souls_to_monsters`'s NEW-wire matcher still keys on filename; the
  `soul_identity` gate now catches the consequence, but the matcher itself is unchanged (changing it
  would move records the F1 gate currently blesses, and is a separate wave).
- **B97-DEBT-3** - zzdev dev-dummy soul drops + items (§8 item 3). Awaiting Will.
- **B97-DEBT-4** - NAME-DRIFT text renames incl. the "Etheral" typo (§8 item 2). Awaiting Will.
- **B97-DEBT-7 (ROUND 2, WILL DECISION)** - Akara vs Kallixenia: our bespoke
  `soul\svc_uber\kallixenia_soul_{n,e,l}` is now carrier-less (reviewed waiver in
  `_ACCEPTED_ITEM_DETACH`). Options (a)/(b)/(c) in §8 item 5. Awaiting Will.
- **B97-DEBT-8 (ROUND 2)** - three soul NAMES are shared by two distinct item families (Charon,
  General Yrrt'ik, Plague Feast) - §5c. Text/design lane.
- **B97-DEBT-9 (ROUND 2)** - amgoz Dropbox conflict-copy creatures ship with live 66% soul drops and
  are counted in the by-design buckets (§8 item 4). Data-hygiene lane.
- **B97-DEBT-10 (ROUND 2)** - `tools/verify_soul_drop_rates.py::_is_creature` still has the
  `\creature(s)\`-only scope hole that this lane just closed in the identity gate, so every
  `records\drxcreatures\` boss is outside its roster. Widening it is a wave of its own.
- **B97-DEBT-11 (ROUND 2, P2)** - `tools/audit_soul_identity.py` resolves the SV `Text_EN.arc` via a
  best-effort `check_build_inputs` probe (it tries several function names because the resolver has no
  stable public API). Give `check_build_inputs` a documented `resolve(name)` entry point and delete
  the probe.
