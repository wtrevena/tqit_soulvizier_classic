# b95 - "Sargath Manbane" soul should summon him (R-51)

**Branch** `feat/sargath-soul` · **Ruling** R-51 (Will, 2026-07-27, verbatim):
> "backlog item sargath manbane soul should let you summon him"

**Precedent followed:** R-43 (b85) "the high priest soul should allow you to summon the high priest" -
same ruling class, same SECOND-BUILDER pattern, same shared chain gate.

> ## STATUS: CODE COMPLETE, **NOT BUILT / NOT GATED / NOT DEPLOYED**
> The lane stopped at the build+deploy step on purpose. The DEV deploy target was
> overwritten by a concurrent lane mid-session and the brief's ground-truth hash went
> stale, so building from `main` and deploying would have silently reverted another
> lane's shipped work. Full evidence in section 7. **Awaiting Will's sequencing decision.**

---

## 1. IDENTIFICATION (proven, not guessed)

The brief was right that "Sargath Manbane" appears nowhere in `docs/` or `tools/`. The reason is that
**the record name shares no token with the display name**, so no grep could ever have found it.

| | |
|---|---|
| Will's spelling | "Sargath Manbane" |
| **Shipped display string** | **"Sargoth Manbane"** |
| **Text tag** | **`tagMonsterName1138`** |
| **MONSTER record** | **`records\creature\monster\dragonian\hero_tarthon_na'arak_37.dbr`** |
| Classification / race | `Hero` / `Beastman` |
| charLevel | `[37, 54, 69]` |
| Body | `Creatures\Monster\Dragonian\Dragonian01.msh`, `MageB.tex`, `anm_dragonian`, scale 1.55 |
| Controller | `controller_noble01` |
| Kit | lightning mage: Lightning Ball, Thunderball + Concussive Blast, `dragonian_reflection`, lightning-bonus aura, `drxenergyshield_aoe`, `armor_passive`, `hero_scaling` |
| **SOUL family** | **`records\item\equipmentring\soul\dragonian\sargoth_soul_{n,e,l}.dbr`** (`tagSoulName297` = `{^F}Sargoth Manbane Soul`) |

### How it was proven (against the deployed DEV arz + shipped Text.arc, not from memory)

1. Searched the **shipped `Text.arc`** (`modstrings.txt`) for the display string and near-spellings.
   Exactly two hits: `tagMonsterName1138=Sargoth Manbane` and `tagSoulName297={^F}Sargoth Manbane Soul`.
2. Swept **every field of all 51,085 records** in the deployed arz for those two tags:
   - `tagMonsterName1138` -> **exactly one** record, as its `description`: `hero_tarthon_na'arak_37.dbr`.
   - `tagSoulName297` -> the 3 canonical soul tiers + 1 unreachable upstream duplicate (below).
3. Confirmed the pairing is real and droppable: the monster's
   `lootFinger2Item1` = the three `sargoth_soul_*` paths, `chanceToEquipFinger2 = 50.0`,
   `chanceToEquipFinger2Item1 = 100`, `dropItems = 1`.

### Difficulty variants

**There are none as separate records.** TQ stores per-difficulty values as arrays inside one record:
`charLevel = [37, 54, 69]` **is** normal/epic/legendary. The two neighbouring records in the same
family are *different named heroes*, not difficulty variants:

| record | tag | display name | its own soul |
|---|---|---|---|
| `hero_tarthon_na'arak_34` | `tagMonsterName1137` | Tarthon Na'Arak | `tarthon_soul_*` |
| **`hero_tarthon_na'arak_37`** | **`tagMonsterName1138`** | **Sargoth Manbane** | **`sargoth_soul_*`** |
| `hero_tarthon_na'arak_40` | `tagMonsterName1139` | Vort the Red | `vort_soul_*` |

### Placement in the world

Not a placed unique boss. He is the **`nameChampion7`** entry of **9 Orient (Act 3) dragonian spawn
pools** - a roaming Orient hero, which matches his soul's own `FileDescription = "Orient"`:

```
records\proxies orient\pools\beastman\dragonian_02_melee01.dbr   .._02_melee02   .._02_melee03
records\proxies orient\pools\beastman\dragonian_03_melee01.dbr   .._03_melee02   .._03_melee03
records\proxies orient\pools\beastman\dragonian_03_ranged01.dbr  .._03_ranged02  .._03_ranged03
```

---

## 2. BEFORE STATE - Will's premise CONFIRMED

All three tiers had **no `itemSkillName` at all**. The soul granted **no skill of any kind**, let alone
a summon - it was a pure stat + augment ring:

| field | n | e | l |
|---|---|---|---|
| `itemSkillName` | *(absent)* | *(absent)* | *(absent)* |
| `itemSkillLevel` | *(absent)* | *(absent)* | *(absent)* |
| `augmentSkillName1` | `soulskills\stafftraining` 5 | 6 | 7 |
| `augmentSkillName2` | `storm\drxthunderball_concussiveblast` 2 | 3 | 4 |
| `itemLevel` | 37 | 55 | 68 |

Plus lightning offense/resist, reflect 12, stun resist 30, STR/life. **So this is a genuine gap, not a
regression.**

### The closest precedent is his own sibling

**Vort the Red** (`hero_tarthon_na'arak_40`) - same family, same mesh, same anim table - **already
ships exactly this summon shape**, which is the template R-51 reproduces:

```
vort_soul_{n,e,l}: itemSkillName = summon_vort, itemSkillLevel = 1/2/3,
                   itemSkillAutoController = <absent>   (manual cast)
summon_vort:       manaCost [250,300,350], cooldown 180, no TTL,
                   petLimit 1, petBurstSpawn 1, skillMaxLevel 3
vort_1/2/3:        race Beastman, description tagMonsterName1139 ("Vort the Red")
```

---

## 3. THE FIX

New registry module **`tools/patches/sargoth_soul_summon.py`** (34th module; registry order hash
`59a36e8f076e6454b3dea354418178661f74312c85b3e573201a0d02f711a058`), registered late among content
modules so the source-mirroring builder reads the FINAL monster record.

1. **Pets + skill from his own rig** via `apply_svc_patches._build_boss_summon` - the same proven
   builder R-43 used. It clones the Lyia pet for a crash-safe `Pet.tpl` baseline, copies **only** anim
   + skill refs from `Monster.tpl` (never equipment/loot fields - the documented Pet.tpl crash law),
   and produces a permanent (no-TTL) manual-cast `Skill_SpawnPet`.
   - `records\skills\soulskills\pets\sargoth_{1,2,3}.dbr`
   - `records\skills\soulskills\summon_sargoth.dbr`
   - stat band anchored one notch below sibling Vort (he is one level band lower, same Hero rank):
     life 15000/22000/30000, regen 34/60/94, dmg 60-86 / 90-136 / 128-196, `charLevel [37,54,69]`,
     scale inherited (1.55).
2. **All three soul tiers wired**: `itemSkillName = summon_sargoth`, `itemSkillLevel = 1/2/3`, **no**
   `itemSkillAutoController` (manual cast - R-44 convention + the Lyia model + the Vort precedent).
   Existing augments and stats are left untouched.
3. **Identification asserts in `apply()`** - the module refuses to build if the monster is missing, if
   its `description` is not `tagMonsterName1138`, if the 3 tiers are not all present, if the monster
   does not drop that soul family, or if a tier's `itemNameTag` is not `tagSoulName297`. A
   mis-identification fails the build loud instead of silently building the wrong boss.

### The unreachable upstream duplicate

Upstream SV ships `sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07).dbr` (a Dropbox conflict
artifact). It is referenced by **nothing** - not the monster's loot, not any formula - so it can never
reach a player. The **shipped Vort family has the identical artifact and upstream wired the summon onto
it too**, so this module does the same, keeping the two sibling families the same shape. It is named
explicitly here so it appears as intended in any record-diff.

---

## 4. PLAYER-SURFACE CHECKLIST (CLAUDE.md law #3 - none deferred)

| # | Surface | Value | How it is verified |
|---|---|---|---|
| 1 | summon skill **name** | `tagSVCSummonSargoth` = "Summon Sargoth Manbane" | added to `tags` by the module; chain gate + `validate_tags` |
| 2 | summon skill **icon** | `DRXtextures\skill icons\soul\thunderorb{up,down}.tex` | **arc-verified present (up AND down)** in the shipped `DRXtextures.arc`; swept as **UNCLAIMED** by every other `_SUMMON_SKILL_ICON` entry; deliberately NOT sibling Vort's Thunderball icon so the two dragonian summons never read as one skill. Registered in the canonical `_SUMMON_SKILL_ICON` map, not hidden in the module. Chain gate asserts `icon_stem == thunderorbup` |
| 3 | pet-bar **portrait** | `proxy_party_up` / `proxy_party_red` (neutral) | swept **all 34** `*_party_up` portraits across every shipped arc: **no dragonian portrait exists**. Neutral proxy is the established convention for unmapped bosses (Hades Marshal; R-43's own High Priest). Load-bearing requirement met: **never the Lyia nymph** - chain gate asserts both `StatusIcon` and `StatusIconRed` |
| 4 | pet **name** | `description = tagMonsterName1138` -> "Sargoth Manbane" | module `verify()`; exactly the Vort precedent (`tagMonsterName1139`) |
| 5 | **race** | `Beastman`, from the source monster (R-11) | `_align_pet_identity` in the builder; module `verify()` compares pet race to source race; chain gate's b81 race/voice leg |
| 6 | **sounds** | distressCallGroup + alert/death/crit/stun/vox paks from the source | `_align_pet_identity`; chain gate's b81 voice leg (no Maenad residue unless the source is Maenad) |
| 7 | **not naked** | his own LeftHand staff (`staff_dyn_n/e/l03`); every slot he does not use zeroed | `_mirror_source_loadout(strict=True)`; the **PET-GEAR-PARITY** gate enforces it *both ways* |
| 8 | **not mute/inert** | lightning kit restored into AI-fireable slots | `_mirror_source_skill_kit`; the **PET-SKILL-KIT** gate |
| 9 | **mobile** | primary row `sHanded`; `anm_dragonian` defines `sHandedRunAnim` (and `staffRunAnim`) | the builder's **D19 pet-mobility assert** (fail-loud) - pre-checked against the deployed arz |

---

## 5. GATE

Per the brief, **no new one-off gate was invented.** R-51 is the same ruling class as R-43, so it was
added as a **leg of the existing shared chain gate**:

- **`tools/patches/enslaver_pet_fx.py` `_CHAIN`** - new `'Sargoth Manbane'` entry alongside Enslaver,
  Hades Marshal and R-43's Blood Cult High Priest. `_verify_chain` walks the whole chain on the FINAL
  assembled arz: **soul item -> granted skill -> skill icon -> spawnObjects -> pet records ->
  pet-bar portrait**, plus zero-green-residue and the b81 race/voice legs.
- **`tools/patches/_negtest_sargoth_chain.py`** - the planted negative test: breaks each link in turn
  (grant cleared; grant cross-wired to `summon_vort`; Lyia nymph icon planted; `spawnObjects`
  repointed at the Vort pets; Lyia party portrait planted; race flipped to Undead) and asserts the
  shared gate **fails on each**, then restores and asserts it passes again.
- **module `verify()`** covers the one leg the shared gate cannot see: that **all three tiers** grant
  the summon, manual-cast, with strict 1/2/3 progression (R-40).
- Inherited for free from the monolith battery (step 3), because a registry module's records are
  validated by every gate: **PET-STAT-MIRROR**, **PET-GEAR-PARITY**, **PET-SKILL-KIT**, **SUMMON-TTL-
  PERMANENT**, and notably **F2 SOUL-SUMMON-IDENTITY**, which independently re-proves the
  identification by asserting the summon source's mesh equals the mesh of the monster that drops the
  soul.

`py tools/patches/_check_registry.py` -> **OK, 34 modules**, order hash
`59a36e8f076e6454b3dea354418178661f74312c85b3e573201a0d02f711a058`.

---

## 6. FILES

| file | change |
|---|---|
| `tools/patches/sargoth_soul_summon.py` | **NEW** - the module (identification asserts, builder call, tier wiring, `verify()`) |
| `tools/patches/_negtest_sargoth_chain.py` | **NEW** - planted negative test for the new chain-gate leg |
| `tools/patches/__init__.py` | +1 `REGISTRY` line (+ rationale comment) |
| `tools/patches/enslaver_pet_fx.py` | +1 `_CHAIN` entry (Sargoth Manbane leg) |
| `tools/apply_svc_patches.py` | +1 `_SUMMON_SKILL_ICON` entry (`summon_sargoth` -> thunderorb) |
| `docs/WILL_RULINGS.md` | R-51 appended verbatim |
| `docs/reports/b95_sargath_soul_summon.md` | this report |

**No map tooling touched.** `Levels.arc` / `Quests.arc` are not inputs to or outputs of anything in
this lane, so they are byte-identical by construction.

---

## 7. ⚠️ WHY THIS DID NOT BUILD OR DEPLOY - concurrent-lane conflict

The brief pinned the ground truth as DEV arz md5 `1c27d5fa650b5c076696db4ad379672f`. That was correct
when this session started and it is what the identification and before-state work was performed
against. **It is no longer what is deployed.**

Measured facts (each re-read twice, stable):

| artifact | md5 | note |
|---|---|---|
| `work/SoulvizierClassic/Database/SoulvizierClassic.arz` | `1c27d5fa650b5c076696db4ad379672f` | mtime 2026-07-28 **09:30:03** - the brief's anchor |
| **deployed** `CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` | **`5143ad1a44a9964c22578e00613f3e14`** | mtime 2026-07-28 **13:55:19** - a *different* build, deployed ~4.5 h later |
| `.claude/worktrees/green-diff/work/.../SoulvizierClassic.arz` | **`5143ad1a44a9964c22578e00613f3e14`** | **provenance: the `fix/green-diff` lane** |

`fix/green-diff` HEAD is `60d7789` *"b92 GREEN GLOW root cause: the mesh attaches the aura (5th
attempt, solved)"*, committed **2026-07-28 14:00:05 - three minutes before this was discovered**. It is
**not merged into `main`** and it adds a new DB-affecting registry module
(`tools/patches/toxeus_mesh_aura.py`, +291 lines across 3 files).

**Consequence:** this branch is based on `main`, which contains neither `fix/green-diff` (b92) nor
`fix/devourer-chest` (b91) nor `feat/death-xp-penalty` (b93). Building from `main` + R-51 and deploying
the result to DEV would have **overwritten `5143ad1a` and silently reverted the green-glow fix another
agent shipped minutes earlier** - exactly the regression class the standing rules exist to prevent, and
on a worktree this brief explicitly forbids touching.

Two further hazards found while confirming this:

- **`work/` is shared mutable state.** At least four lanes (`green-diff`, `debt-db`, `debt-mixed`,
  `death-xp`) have their own `work/.../SoulvizierClassic.arz` at four different hashes, and the main
  checkout's `work/` is being written by whichever lane built last. A build from this lane into the
  shared staging dir could clobber a concurrent lane's artifacts.
- **A pre-existing backup-naming mismatch:** `local/db_backups/SoulvizierClassicDEV_pre-b93_1c27d5fa.arz`
  is *named* for hash `1c27d5fa` but its **contents hash to `5143ad1a`**. Worth a look - a rollback
  taken from that file would not restore what its name promises.

### What is needed to finish (all of it is mechanical once sequencing is decided)

1. **Will's call on integration order** - rebase `feat/sargath-soul` onto the branch that is actually
   deployed (`fix/green-diff`), or merge the in-flight lanes to `main` first, then rebase.
2. Baseline build + R-51 build **into an isolated output dir** (never the shared `work/`), record-diff
   intended-only, `validate_tags`, contracts battery vs a matching baseline, registry verifies.
3. Run `tools/patches/_negtest_sargoth_chain.py` against the new arz (it needs an arz built **with**
   this module; it cannot run until then).
4. Deploy the coupled arz + Text pair to DEV, md5-verify deployed == built, re-assert
   `Levels.arc`/`Quests.arc` untouched, tag, and add the BUILD GATE RECORD to `docs/BACKLOG.md`.

**Expected record-diff when it does build** (0 removed; every path named):

```
ADDED   (4):  records\skills\soulskills\summon_sargoth.dbr
              records\skills\soulskills\pets\sargoth_1.dbr
              records\skills\soulskills\pets\sargoth_2.dbr
              records\skills\soulskills\pets\sargoth_3.dbr
CHANGED (4):  records\item\equipmentring\soul\dragonian\sargoth_soul_n.dbr   (+itemSkillName, +itemSkillLevel 1)
              records\item\equipmentring\soul\dragonian\sargoth_soul_e.dbr   (+itemSkillName, +itemSkillLevel 2)
              records\item\equipmentring\soul\dragonian\sargoth_soul_l.dbr   (+itemSkillName, +itemSkillLevel 3)
              records\item\equipmentring\soul\dragonian\sargoth_soul_n (amgoz-qosmio's conflicted copy 2013-08-07).dbr
TEXT    (1):  tagSVCSummonSargoth = "Summon Sargoth Manbane"
```
