# b97 - SOUL-vs-MONSTER IDENTITY AUDIT (round 1)

**Will (2026-07-27, verbatim):** *"we also need to do an audit of the hero monsters vs the souls
that they drop since i can see that some of the heroes are dropping the wrong souls or souls for
other boss monsters i think"*

**Verdict: Will is right, and the audit found the exact mechanism.** 18 creature records drop a
soul that belongs, by name, to a *different named creature that also drops it*. Every one is now
detached, at the correct layer, behind a permanent gate.

- Branch `fix/soul-identity`, tag `build58-dev`.
- Audit tool (reproducible over any `.arz`): `tools/audit_soul_identity.py`.
- Fix + gate: `tools/patches/soul_identity.py` (patches-registry module).
- Full 850-row table: [`b97_soul_identity_table.md`](b97_soul_identity_table.md).

---

## 1. Scope audited

Ground truth = the deployed arz
`.../CustomMaps/SoulvizierClassicDEV/Database/SoulvizierClassicDEV.arz` (read-only), cross-checked
against a baseline rebuild from `main`, **SV 0.98i** upstream, and the **TQAE base game** database.

| Quantity | Count |
|---|---|
| Records in the deployed arz | 51,085 |
| Creature records | 3,960 |
| Creature records carrying soul loot (`lootFinger2Item1`) | 1,278 |
| **Creature records with a LIVE soul drop (`chanceToEquipFinger2` > 0)** | **850** |
| ... of which Hero / Boss / Quest | 583 / 166 / 101 |
| **Distinct soul families actually dropped** | **591** |
| Distinct monster display names dropping a soul | 605 |
| Records that also exist in the TQAE base game | 412 |
| Monsters with an unresolvable display tag | 0 |

Every difficulty variant and every rank is included; the count is records, not creatures, which is
why 850 records map to 605 named creatures (normal/epic/legendary variants of one boss are separate
records).

## 2. Classification

| Verdict | Rows | Meaning |
|---|---|---|
| **MATCH** | **808** | The soul's identity is the monster's identity. |
| **MISMATCH** | **18** | Drops a soul whose named owner is a *different* creature that also drops it. **The bug.** |
| SHARED-ARCHETYPE | 13 | Soul named for a common monster *type*; no carrier owns the name. By design. |
| NAME-DRIFT | 11 | Sole live carrier, display name simply differs from its soul's. Not identity theft. |

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

---

## 5. NOT bugs - left untouched, and why (no whitelist needed)

The rule below is structured so these are preserved **by construction**, not by a hand-list.

### 5a. SHARED-ARCHETYPE (13 rows, 3 families) - the soul is a monster *type*, not a hero

`Satyr Fire Magi Soul` (Aniketos the Sacrificer x5, Phlegraeus Flame Chanter), `Sandwraith Soul`
(Sandspirit ~ Dustwarrior x2, Royal Advisor Hemetre x2, Djenebti the Dust-Drinker), `Speckled Jim
Soul` (Wither Mound x2). The archetype's own Common/Champion records carry the loot ref but are
gated dead by the yeti rank-fix, so **no carrier owns the name** and the family's named uniques are
the only way to obtain the soul. Zeroing these would make the soul **unobtainable** - the opposite
of a fix.

### 5b. NAME-DRIFT / mod-themed (11 rows) - sole carrier, no identity stolen

`Clazomenaeus the Unstoppable` <-> Crowboar Soul, `Shriekbrood the Collector` <-> Grimshell Soul,
`Skull Spine` <-> Spinebone Soul, `Vile Crawl` <-> Vilerotter Soul, `Corpse Wake` <-> Diseased
Vulture Soul, `Cynisca, Princess of Sparta` <-> Awakened Dead Soldier Soul, `Meritamen the
Shadowcaller` <-> Maenad Sorceress Soul, `The Ethereal One` <-> "The Etheral One Soul" *[sic - a
spelling typo in the SV soul tag]*, plus the mod-authored themed names `Alkyoneus, the Hoard
Unbound` <-> Soul of the Gaoler, `Tantalus, the Hunger Unbound` <-> Soul of the Insatiable, `The
Helepolis, Taker of Cities` <-> Ash of the Funeral Games. You kill that creature, you get that
creature's soul - it is just spelled differently. Renaming any of them is a **text/design** call
(amgoz1 creative bar), so they are listed for Will in §8, not changed.

### 5c. Rulings honoured (checked before touching anything)

`docs/WILL_RULINGS.md` re-read for this wave. **Nothing ruled was overturned:**

- **R-48** (Enslaver + Devourer souls at 100%) - both are **sole carriers** of `enslaver_soul_` /
  `blood_toxeus_soul_`, so the rule never considers them. `soul_identity` is registered *after*
  `toxeus_souls_100` and its `verify()` re-reads the final db: both are still 100%.
- **R-43** (High Priest soul summons the High Priest), **R-45** (Tomb Guardian soul removed;
  `um_tombguardian_26` stays Common at 0.0), **R-42** (50/66/25 split), **R-44** (crowboar summon),
  bloodtip / gustleech, and the **legion double-soul chains** (`legion_soul_stages` +
  `double_soul_rulings`) - all untouched. This module writes exactly one field, only downward, only
  on the 18 records above; the 50/66/25/100 classifier is not modified.

---

## 6. The fix - `tools/patches/soul_identity.py`

**THE RULE** (data-derived; no hand-list decides who loses a drop):

> For every soul family S, let CARRIERS(S) be the creature records with a live soul drop that
> reference S.
> **If some carrier's display name identity-matches S, every other carrier whose display name does
> not match is an identity thief -> `chanceToEquipFinger2 = 0`.**
> **If no carrier identity-matches S, nothing is touched.**

The second clause is load-bearing: it is *why* §5a and §5b are safe without a whitelist, and it makes
orphaning a soul structurally impossible.

Layer choice (BL-103 fix-upstream): the rule depends on the **final** carrier set, which only exists
after every soul-wiring and drop-rate writer has run, so a patches-registry module is the correct
seam - not a hand-patch, and not a `wire_souls_to_monsters` edit that could only ever see half the
picture. Identity matching is done on display text; the `.dbr` filename - the axis that caused the
defect - is never consulted.

Supporting change: `build_svc_database.main()` now loads SV 0.98i's `Text_EN.arc` into
`apply_svc_patches._SV098I_NAME_TAGS` (the same module-global hand-off the F6 soul-provenance sets
use), outside the prefix cache so a cached payload can never ship an empty table.

## 7. The gate (this must never regress)

1. **`verify()` - the permanent, LIST-FREE invariant.** Runs in registry step 4 over the FINAL merged
   db (after the whole gate battery *and* the testing drop-rate forcer): re-runs the rule and
   requires the answer to be **empty**. Any future clone, wire, or content module that hands a
   creature another named creature's soul **fails the build**.
2. **REVIEW GATE in `apply()`.** The rule's verdict is asserted equal to `_REVIEWED` (the 18 rows
   classified here, each annotated with monster / stolen soul / rightful owner). This is *not* the
   mechanism that decides who loses a drop - the rule is - it is the proof that the current data's
   verdict is the one a human reviewed. Content drift fails loud asking for review rather than
   silently zeroing a boss's soul.
3. **ORPHAN GUARD in `apply()`.** After zeroing, every affected family is re-checked to still have a
   **live matching carrier**; if not, the build aborts rather than make a soul unobtainable.
4. **Planted negative test** (`tools/contracts/tests_soul_identity_negative.py`): reproduces a real
   mismatch from today's data (Fesil the Quick -> Wheedletongue soul) by re-arming it on the fixed
   db, and asserts `verify()` raises. It also asserts the clean db passes, and that a
   SHARED-ARCHETYPE family (Satyr Fire Magi) is *not* flagged - so a future "tighten the rule" change
   that starts orphaning archetype souls fails the test.

**Whitelist:** the module ships with **no** whitelist. Every by-design family in §5 is preserved by
clause 2 of the rule itself, which is strictly stronger than a hand-maintained exception list (it
cannot go stale, and it cannot be padded to silence a real bug). If a future case ever needs one,
the correct move is to justify it in `_REVIEWED` with monster / soul / owner, which is already the
required shape.

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
   2014-09-10).dbr` and friends are compiled-in junk twins that also drop souls. Already a known
   separate data-hygiene ticket (the F1 gate excludes them explicitly); flagged again here, still
   out of scope.

## 9. Build + proofs (BUILD ONLY - not deployed)

`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, DB-only lane. **No map rebuild, no deploy** (concurrent lanes
are editing the arz; the orchestrator merges and deploys once).

| artifact | md5 |
|---|---|
| **built arz (FOR THE ORCHESTRATOR)** `<scratch>/final/Database/SoulvizierClassic.arz` | **`fcc6fad38d9b8a0fd54a337e23e5ffa8`** (55,424,089 B) |
| baseline arz (main `8c3445c`, pre-change) | `1c27d5fa650b5c076696db4ad379672f` (55,424,142 B) |
| `Text.arc` rebuilt from the build-emitted `uber_soul_tags.txt` | `fcca49277b9d31ed451e4a6843898843` - **byte-identical to baseline** (this lane authors 0 tags) |
| `uber_soul_tags.txt` | **byte-identical to baseline** |

- **RECORD-DIFF vs baseline: 0 added, 0 removed, 18 modified.** Every change is exactly one field,
  `chanceToEquipFinger2 -> 0.0`, on exactly the 18 records in §4. Nothing else in 51k records moved.
- **DETERMINISM:** two independent full builds (before and after widening the display-name table)
  produced the **same arz md5** `fcc6fad3`, confirming the tag change altered only which carriers are
  judgeable, never the output.
- **Build exit 0**, every fail-loud invariant green: soul-leak (0 non-Hero/Boss/Quest drop a soul),
  soul-augment, soul item-skill activation (1388 souls), F1 cross-wire, F2 soul-summon-identity (21
  families), F6 soul-naming, spawn-eligibility, boss-kit clone-shape, A7 Occult/Hunting golden
  (84 waived / 0 other), b77 unlock-alignment.
- **Registry:** `[33/34] soul_identity` -> `modified 18 record(s), 0 tag(s)`; order hash
  `86570c075c72a85ca5f63f018da7a0894371362e389b966c206df8752084253a` (34 modules). **0 carriers
  skipped as unjudgeable** in the final build.
- **`[soul_identity] verify OK`** in step 4 over the FINAL merged db.
- **`validate_tags`: PASS** (417/417 authoritative tags present).
- **`verify_soul_drop_rates --gate`: PASS** (exit 0). Testing-forcer survival **832 enabled -> 100,
  446 gated stay 0** (baseline 850/428 - exactly the 18 moved). All 18 carried as documented
  `_KNOWN_EXCEPTIONS` waivers. Planted post-wire-stomp negative test still CAUGHT.
- **Contracts `--only souls,summons`:** final **0 P0 / 0 P1 / 112 P2, GATE PASS** - and the baseline
  yields the **byte-identical violation set** (112 both, 0 only-in-final, 0 only-in-baseline), so the
  pre-existing P2s are provably untouched.
- **A9 render-chain:** `RESULT: PASS (22 upstream WARNs)` on the final build, and standalone on the
  baseline arz: **PASS, same 22**. (The gate SKIPS with no `Resources/` beside the output and FAILS
  spuriously with an EMPTY one - see BL-b97-DEBT-6; it was run against the real resource arcs.)
- **Planted negative test:** `tests_soul_identity_negative.py` on the final arz - **ALL 13 ASSERTIONS
  HELD** (T1 clean db passes; T2 re-arming the real Fesil-the-Quick mismatch makes `verify()` fire
  and name both the record and the rightful owner; T3 synthetic cross-wire fires; T4 the Satyr Fire
  Magi archetype family is NOT flagged and keeps a live carrier; T5 filename is not identity).
- **Ruling spot-checks on the final arz:** R-48 Enslaver `100.0` / Devourer `100.0`; R-45
  `um_tombguardian_26` `0.0`.

## 10. Debt register

- **B97-DEBT-1** - the 18 detached monsters have no soul of their own (§8 item 1). Awaiting Will.
- **B97-DEBT-2** - `wire_souls_to_monsters`'s NEW-wire matcher still keys on filename; the
  `soul_identity` gate now catches the consequence, but the matcher itself is unchanged (changing it
  would move records the F1 gate currently blesses, and is a separate wave).
- **B97-DEBT-3** - zzdev dev-dummy soul drops + items (§8 item 3). Awaiting Will.
- **B97-DEBT-4** - NAME-DRIFT text renames incl. the "Etheral" typo (§8 item 2). Awaiting Will.
