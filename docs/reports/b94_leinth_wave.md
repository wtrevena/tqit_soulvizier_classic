# b94 LEINTH WAVE - champion orb calibre, Leinth buff + cult abilities, post-kill exit

> Branch `feat/leinth-wave`, tag `build55-dev`. Three independent parts, one wave.
> Ground truth = the deployed DEV artifacts (see PROVENANCE below). House style: no em dashes.
> Design law checked: `docs/WILL_RULINGS.md` (R-42 / R-47 / R-48 / R-26 / R-3 / R-30-32),
> `docs/amgoz1_design_voice.md`, the b76 chumbi-freeze density law, BL-103 fix-upstream.

---

## 0. PROVENANCE (read this before trusting any number below)

| artifact | md5 | note |
|---|---|---|
| repo `main` build (`SoulvizierClassic.arz`) | `1c27d5fa650b5c076696db4ad379672f` | matches the brief's stated ground truth exactly, so `main` IS the design pass's baseline |
| DEPLOYED DEV `SoulvizierClassicDEV.arz` (at wave start) | `5143ad1a44a9964c22578e00613f3e14` | **NOT built from `main`** - see the deploy-hazard section |
| DEPLOYED DEV `Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | matches the brief; **untouched by this wave** |
| DEPLOYED DEV `Quests.arc` (at wave start) | `5e664c7b190965fd69f6ff15d77d85e4` | matches the brief; PART C changes exactly one entry inside it |

Every record-level fact in this report was read out of the DEPLOYED arz, and every
build-level fact out of the two builds this wave produced.

---

## 1. PART A - champion orb CALIBRE parity (R-70)

### Finding (confirmed, and by a wide margin)

`treasureProxyName` is the ONLY field in all 51,085 records that ever references an orb
(43 references total). Neither side drops "an orb" in the same sense:

* **Leinth** -> `records\drxitem\container\bosschestproxy_leinth.dbr`, a BESPOKE DRX chest
  (in-game name `tagLeinthChest` = "Leinth's Essense", mesh `DRX\meshes\leinth_chest.msh`).
* **Both Toxeus champions** -> `genericbossorb_04`, the R-47 shared generic apex orb.

Both chains traced proxy -> ProxyAccessoryPool -> FixedItemContainer -> FixedItemLoot on all
three difficulties:

| raw knob (unambiguous, straight off the records) | LEINTH CHEST | ORB04 (champions) |
|---|---|---|
| `numSpawnMinEquation` | `(3+(1.6*P))*2.2` | `(3+(1.6*P))*0.9` |
| `numSpawnMaxEquation` | `(3+(1.6*P))*2.4` | `(3+(1.6*P))*1.3` |
| `loot4Chance` (accessory/relic/ring/formula group) | 100.0 | 12.7 |
| unique-entry `lootWeight` | 50 | 27 |
| `goldGenerator` / level | typhon @64 | boss @47/69/88 |

Modelled expected items at 1 player (labelled a MODEL because engine roll semantics cannot be
proven from data alone; the raw knobs above already settle the direction on their own):
**Leinth 18.5 vs orb04 5.7 = 3.25x**, unique share 4.1-7.0% vs 3.1-3.3%. Identical on all three
difficulties.

**HONEST COUNTER-AXIS (it cuts the other way, so it is stated):** orb04 rolls the HIGHER item
tier. Its tables are the xpack Act-4 statics `uberorb_default_{n,e,l}01c` at
`goldGeneratorLevel` 47/69/88 with `levelEquationFile = containerlevelequation_all` and
`LockedClassification = Boss`; Leinth's are the Act-3-band 63-65 tables at gold level 64 with no
LockedClassification. So orb04's individual items are higher item-level; Leinth's are lower-tier
but ~3.25x more numerous and ~2x more unique-weighted.

**Whole-kill context, so the champions are not misrepresented:** they have ELEVEN live equipment
slots (~9.68 expected equipment items including their 100% souls per R-48, the Devourer's
guaranteed `crimsonverdict` and a guaranteed Misc4); Leinth has TWO (`chanceToEquipHead` 100 ->
`lenithsveil`, `chanceToEquipFinger2` 66 -> her soul) = 1.66. Totals ~15.4 vs ~20.2 per kill. So
Leinth still out-rewards them overall, and the entire gap lives in the orb/chest. That is exactly
the thing the report pointed at.

### The constraint that shaped the fix

`genericbossorb_04` is shared by **TWENTY-ONE** boss records (Sarkoth, Vashkarr, Bloodcrow,
Voranthys, Broodmother, Enslaver, Gorrahk, Ilsevar, Dagon, Ephialtes, Mnemophage-core, Antaeus,
Polis Gaoler, Deep Thresher, Meglograi, bloodcrow_soul, Dorus, Tantalus, Hades Marshal,
Helepolis, Devourer). Editing it in place would silently buff twenty-one encounters and rewrite
the mod's whole endgame economy. Rejected.

### What shipped

10 NEW records, every one a clone of a proven shipping record, owned by
`tools/patches/uber_apex_orb.py`:

1. `records\item\containers\new\genericbossorb_05.dbr` (Proxy; same ChestBoss01 mesh, Proxy_Blue
   texture, chanceToRun 100, difficulty/limit equations) with the 3 accessory slots repointed.
2-4. `genericboss05_{normal,epic,legendary}_repeat.dbr` (ProxyAccessoryPool) -> the 3 new chests.
5-7. `genericboss05_chest_{normal,epic,legendary}.dbr` (FixedItemContainer). `levelEquationFile`,
   `goldGenerator`, `LockedClassification=Boss`, `lootClassification=Hero`, mesh
   `DRX\meshes\bossorbmesh.msh` and scale 0.7 are all KEPT, so the drop still LOOKS and
   level-scales like the apex orb players know. Only `tables` moved.
8-10. `records\item\loottables\svc\svc_uberorb_apex_{n,e,l}01c.dbr` - clones of the xpack Act-4
   statics with every table reference and every `goldGeneratorLevel` untouched and exactly FOUR
   knob edits, which ARE the calibre match: min mult `*0.9 -> *2.2`, max mult `*1.3 -> *2.4`,
   `loot4Chance 12.7 -> 100.0`, and every UNIQUE-entry `lootWeight 27 -> 50` (derived from the
   record itself by matching the `unique` namespace in `lootNNameM`, never by hard-coded slot
   numbers, so an upstream table reshuffle cannot silently move the edit onto a static entry).

2 CHANGED fields: `treasureProxyName` on `um_toxeus_enslaver_99` and `um_bloodtoxeus_99`.

**Result:** champion orb goes from ~5.7 to ~18.5 expected items at 1P (Leinth's figure) and from
~3.1% to ~5.7% unique share (Leinth's figure), while KEEPING its strictly better Act-4 item pool
and gold level 88. **Leinth's own chest is UNCHANGED** (explicit instruction, asserted in apply()).

### R-48 is untouched and untouchable here

Souls are Finger2 EQUIPMENT (`lootFinger2Item1` + `chanceToEquipFinger2`); orbs are
`treasureProxyName`. Independent mechanisms. apply() still snapshots both soul fields on both
champions before and after and fails loud if either moved.

---

## 2. PART B - Leinth, the Blood Witch (R-71)

### Why she melts today

Her two passive packages already cap her where it does not matter: skill14
`zpassive_resists_bleedvitleechconvert_x10plvl` @10 gives +100 bleed / +100 life / +100 convert /
+100 life-leech / +100 mana-leech, and skill15 `elementalresistance_10xlevel` @3 gives +30
elemental. Effective: bleed 100, life 160, convert 100, elemental 50, stun 100 - and **physical
10, pierce 20, poison -15**. Physical and pierce are the only damage that touches her, which is
exactly why a weapon build shreds her and a caster respects her.

### Stats (all three variants)

| field | q_leinth_47 | q_leinth_49 | q_leinth_50 |
|---|---|---|---|
| `characterLife` | 32,481 -> **52,000** | 35,703 -> **57,000** | 38,924 -> **62,000** |
| `defensivePhysical` | 10 -> **35** | 10 -> **35** | 10 -> **35** |
| `defensivePierce` | 20 -> **45** | 20 -> **45** | 20 -> **45** |
| `characterAttackSpeed` | 0.8 -> **1.0** | same | same |
| `characterRunSpeed` | 1.0 -> **1.15** | same | same |
| `characterLifeRegen` | 2 -> **10** | same | same |
| `skillLevel13` (geysers) | 1;4;7 -> **4;7;9** | same | same |
| `defensivePoison` | **-15 KEPT** | **-15 KEPT** | **-15 KEPT** |

Deliberately NOT touched: her poison weakness (amgoz1 identity + the fight's counter-play) and
her charLevel 47-76 (she is the cave's main-path terminal boss, not an uber). The gate asserts
both, and also asserts she never out-stats the Enslaver on resists or speed.

**DEVIATION from the design brief, stated:** the brief asked for geysers `4;7;10`.
`cerberus_crackfire` has `skillMaxLevel = 10` but its per-level arrays carry only NINE entries
(indices 0-8), so 10 would index out of range. Shipped `4;7;9`, which delivers the brief's actual
intent (poison 800/850/950 and the 5% current-life component ON at every difficulty, where Normal
previously had none).

### Three new abilities, and why three and not four

**This is an engine ceiling, not a cut.** Monster.tpl exposes exactly FIVE castable
`specialAttack` slots (census over all 51,085 records: 3164 / 1602 / 894 / 300 / 167 users, with
only 3 stray `specialAttack6` references). Leinth already used FOUR, all of them her own bespoke
DRX kit (`melinoe_bloodboil`, `leinth_summon_uglies`, `leinth_bloodall_02`, `leinth_heatseeker`).
So there was ONE free attack slot, plus the two other AI-driven cast mechanisms Monster.tpl
actually supports for these donor CLASSES: `buffSelfSkillName` (978 refs, 9 of them
SpawnPet/SpawnPetMonster including a Boss) and `dyingSkillName` (541 refs, 18 on Boss records).
`healSkillName` is Skill_GiveBonus-only, `buffOtherSkillName` is Skill_BuffOther-only and
`berserkSkillName` is BuffSelfDuration/BuffOther-only, so none of those can carry these donors.
A fourth ability would have had to DISPLACE one of her own bespoke DRX skills, which the
retirement protocol forbids without Will.

| ability | donor (all from her OWN `drxcreatures\bloodwitch` cult family) | kit slot | cast wiring |
|---|---|---|---|
| **CRIMSON TITHE** | `skills\disciple_bloodrain_bleedx50_vitx10.dbr` (Skill_AttackProjectileAreaEffect; `bloodofares_tearsofblood` projectile, radius 8, 8s active, **30s cooldown**, bleed to 1000, -25% total resistance, -50 defensive ability, 33% slow, 25 fumble, Crumple) | skillName9 @ 8;14;20 | `specialAttack5` @ 100 |
| **CHOIR OF THE BLOODBORN** | `skills\discipleboss_summon_melinoe.dbr` (Skill_SpawnPet -> `discipleboss_bladedancer`), cut from burst 6 / limit 18 to **burst 2;3;4 / limit 6 + 45s TTL** | skillName16 @ 1;2;3 | `buffSelfSkillName` |
| **SANGUINE MIRE** | her OWN `leinth_skills\leinth_summon_uglies.dbr` Skill_SpawnPet rig, `spawnObjects` repointed to the cult's `skills\seductress_bloodpuddle_monster.dbr`, burst 3 / limit 3 / **8s TTL** | skillName18 @ 1;2;3 | `dyingSkillName` |

Shape precedent for Sanguine Mire (`petBurstSpawn` 3 over a single-entry `spawnObjects`): a census
of every `Skill_SpawnPet*` record in the shipped arz finds **108** with `maxBurst > len(spawnObjects)`
against 91 equal and 155 with more, and the 108 include base boss skills
(`alastor_summonskeleton{warrior,archer}` 3/1, `sandwraithlord_summonsandwraiths` 4/1,
`yaoguai_summonshadowstalkers` 5/1). So a single-entry spawn list under a larger burst is an
established shipping shape, not an invention.

amgoz1 bar: zero new art, zero new FX, zero new sound, nothing generic. Crimson Tithe is the
single highest-value addition because the fight currently has NO telegraphed phase moment; its
30s cooldown is what paces it (her four existing specials all sit at chance 100, so the module
keeps that convention and lets the cooldown do the rate-limiting). Sanguine Mire is deliberately
short-lived so it reads as a death flourish and never blocks looting, and it fires at the one
moment the player has a reason to move anyway - her death is also when the exit portal opens.

Player-surface checklist: each new skill carries a real name + flavour tag
(`tagSVCLeinthCrimsonTithe` / `...ChoirBloodborn` / `...SanguineMire` plus `DESC`), added to the
build-emitted tag stream so `validate_tags` resolves them.

### The summon-density cut (b76 law)

`leinth_summon_uglies`: `petBurstSpawn` 4;6;8 -> 2;3;4, `petLimit` 16 -> 6, plus the finite
`spawnObjectsTimeToLive` (45s) the skill never had. 16 concurrent PERMANENT chaff pets is exactly
the density that froze the game in b76, and it is the least amgoz1-ish thing in her kit. The
skill is NOT removed and stays wired at `specialAttack2`.

### STAGED-BUT-REJECTED (flagged, not silently chosen)

DRX left `skills\leinth_skills\cerberus_acidpuddle_summon.dbr` and `cerberus_acidpuddle_attack.dbr`
wired to NOTHING inside her own folder, so they were plausibly her intended kit. They are POISON,
and she is the one boss in the mod with a -15 poison weakness. A poison-dealing, poison-weak witch
is thematically self-contradictory, so they were not used. **Will's call** (question 4 below).

### Nothing loot-side moved

`chanceToEquipHead` (her 100% `lenithsveil`), `chanceToEquipFinger2` (her 66% soul at the R-42
PLACED rate), every `loot*Item*` field and `treasureProxyName` are snapshotted before and after
apply() and the module fails loud if any of them moved.

---

## 3. PART C - the post-kill exit to the occultist merchant (R-72)

### The machinery was already built, placed and correctly aimed

* `records\drxmap\bloodcave\portals\vortexportal_exit.dbr` is **Class=Npc** (AIType generic,
  ActorName "Ioannes", description `tagLeinthExitPortal`, mesh
  `XPack\Items\shrines\teleport\credits_portal.msh` + the DRX `vortexportal01` texture). It LOOKS
  like a vortex and IS an NPC, which is exactly what our proven traveler/boat-dialog pattern
  needs. Its own FileDescription reads, verbatim, "Exits the player after the Leinth boss fight."
* PLACED exactly ONCE across all 2,282 levels: `bossfight.lvl` local (15.00, 3.26, 66.00) = world
  (3441, 3.26, 3178), 6.2u from Leinth's proxy, on-navmesh (0.14u, component #0).
* Text already resolves `tagLeinthExitPortal` = "Mystical Vortex" and `tagReturnFromLeinthBattle`
  = "Leave the Sanctuary of the Bloodborn?".
* The shipped `Action_BoatDialog` destination `(4294967206, 4294967193, 2321)` decodes signed to
  world **(-90, -103, 2321)** = inside `HiddenValleyBorder04`, **9.79u from the OCCULTIST
  MERCHANT** (`Merchant_HiddenValley_General`) outside the blood-cave entrance, on the SAME
  walkable component (#0, 26,379 cells) as the merchant and his wagon, and ~16u from the pit-sprite
  cluster so the player does not land in hostiles. The shipped destination ALREADY IS what Will
  asked for.

### The defect

Verified against the deployed `Quests.arc` bytes. In step "Boss Room Crystal Gate":

* trigger "Open door on Leinth defeat": `Condition_KillAllCreaturesFromProxy(q_leinth_lone)`,
  **isResettable=0**, carrying all four actions (OpenDoor + ShowNpc + UpdateNPCDialog +
  BoatDialog).
* triggers "Open Boss Trap Door Fallback" x3: `Condition_KillCreature(q_leinth_47/49/50)`,
  isResettable=1, carrying **`Action_OpenDoor` ALONE**.

That pool also carries `nameChampion1-3 = b_med_blooddemon_30/31/32`, so the proxy-wide condition
needs every creature the proxy produced dead. Whenever it does not satisfy (an unaccounted
champion demon, a character that did not have the quest tracked at kill time - the widow-letter
class of bug, same quest family - or the one-shot already latched) the player gets exactly the
reported symptom: **the boss door opens and no exit portal ever appears.**

### The fix

`tools/build_quest_files.py::_promote_leinth_exit_fallbacks`, run after
`_harden_guardian_door_unlocks`:

1. Copy the primary trigger's action block **VERBATIM out of the parsed tree** onto all three
   resettable fallbacks. Copying rather than re-authoring means the npc, the destination ints and
   the offer tag are byte-identical to the shipped primary **by construction**, with no
   hand-transcription risk.
2. Flip the primary's `isResettable` 0 -> 1 so a revisit re-arms it.

Double-firing is harmless (ShowNpc on an already-shown NPC and a second identical BoatDialog offer
are both no-ops), the same reasoning b48 used for the redundant door opens.

### Artifacts and scope

**Quests.arc ONLY. Levels.arc is BYTE-UNCHANGED** (nothing is placed; the NPC and the destination
already exist). No new quest entry is created, so the ~254-entry load window
(`docs/QUEST_STATE_INJECT.md`) is **NOT engaged** and the QUESTS section is unchanged. The
Levels+Quests coupling is satisfied trivially: the Levels artifact deployed alongside is the
byte-identical one already on disk (hash proof in the deploy section).

**CANONICAL, not TESTHUB-only.** `bossfight.lvl` is an SV-native level present in both map
variants; `vortexportal_exit` is an SV-NATIVE placement inside SV's own bossfight blob (NOT one of
our `INJECT_SPECS` / `build_hub_extra_specs` additions); `Quests.arc` is variant-independent. And
because the fix places nothing there is no TESTHUB-only risk at all. Workshop subscribers on
canonical get the identical fix.

**Warden "1 route : 1 NPC" law: not engaged.** All four triggers bind the SAME record to the SAME
tag and the SAME destination, the NPC is placed exactly once, and `bossfight.lvl` holds no other
NPC.

### PART C PROOF (entry-level blob diff + real-world negative)

```
ENTRY-LEVEL BLOB DIFF: 107 entries in, 107 out, 1 changed
   CHANGED open_bloodcave_portal.qst  23213 -> 25316 bytes
   byte-identical entries: 106

BEFORE: 6 trigger(s) in step 'Boss Room Crystal Gate'
   Set door trap                Condition_OnLevelLoad               ['Action_OpenDoor']
   Trap Player                  Condition_EnterVolume               ['Action_CloseDoor']
   Open door on Leinth defeat   Condition_KillAllCreaturesFromProxy ['OpenDoor','ShowNpc','UpdateNPCDialog','BoatDialog'] isResettable=0
   Open Boss Trap Door Fallback Condition_KillCreature              ['Action_OpenDoor']
   Open Boss Trap Door Fallback Condition_KillCreature              ['Action_OpenDoor']
   Open Boss Trap Door Fallback Condition_KillCreature              ['Action_OpenDoor']

AFTER : 6 trigger(s) in step 'Boss Room Crystal Gate'
   Set door trap                Condition_OnLevelLoad               ['Action_OpenDoor']
   Trap Player                  Condition_EnterVolume               ['Action_CloseDoor']
   Open door on Leinth defeat   Condition_KillAllCreaturesFromProxy ['OpenDoor','ShowNpc','UpdateNPCDialog','BoatDialog'] isResettable=1
   Open Boss Trap Door Fallback Condition_KillCreature              ['OpenDoor','ShowNpc','UpdateNPCDialog','BoatDialog']
   Open Boss Trap Door Fallback Condition_KillCreature              ['OpenDoor','ShowNpc','UpdateNPCDialog','BoatDialog']
   Open Boss Trap Door Fallback Condition_KillCreature              ['OpenDoor','ShowNpc','UpdateNPCDialog','BoatDialog']

CONTRACT QST-LEINTH-EXIT:
  BEFORE (the shipped bytes): 4 violation(s)  <- REAL-WORLD NEGATIVE PROOF
     P1 Open door on Leinth defeat   :: the primary proxy trigger is one-shot (isResettable=0)
     P0 Open Boss Trap Door Fallback :: missing ShowNpc, UpdateNPCDialog, BoatDialog  (x3)
  AFTER : 0 violation(s)
```

The two other SV area questlines and every native SVAERA quest are byte-identical, and the
promotion is idempotent (a second `--promote-leinth-exit` run emits a byte-identical arc,
md5-verified).

**Typhon alternative, evaluated and rejected** (the brief's explicit fallback question): the
Typhon victory portal is `q15_typhontomb_portaltoolympus.dbr`, a FixedItemTeleport with locked=1 +
staticPortal=1 unlocked by `Action_UnlockFixedItem` and paired with a target SoundObject placed in
the destination level. Cloning it needs a new FixedItemTeleport, a new target SoundObject, a NEW
PLACEMENT in `bossfight.lvl` AND a NEW PLACEMENT in `HiddenValleyBorder04` - a two-blob Levels.arc
rebuild plus arz work, versus ZERO Levels change for the traveler route. It also re-enters the
map-portal firing-risk class this project deliberately left behind when it chose Model C
boat-dialog. The traveler pattern demonstrably CAN fire on a boss-death condition: it already does,
via `Condition_KillAllCreaturesFromProxy -> Action_ShowNpc + Action_BoatDialog`.

---

## 4. GATES SHIPPED WITH THIS WAVE (no new surface without a gate)

| gate | what it fails the build on | planted negative test |
|---|---|---|
| `tools/patches/uber_apex_orb.py::apply` | orb04 chain moved; consumers changed by anything other than the 2 champions; R-48 soul wiring moved; Leinth's chest tables moved | (in-apply, fail-loud) |
| `tools/patches/uber_apex_orb.py::verify` | not exactly 2 orb05 carriers; broken orb05 chain on any difficulty; any of the 4 knobs below Leinth's; orb04 stripped of its other consumers; R-48 below 100 | `tools/debug/negtest_uber_apex_orb.py` (10 subtests) |
| `tools/patches/leinth_wave.py::apply` | any loot/drop field on the 3 variants moved; a kit slot or cast mechanism already occupied | (in-apply, fail-loud) |
| `tools/patches/leinth_wave.py::verify` | any stat target moved; poison weakness changed; a new skill at level 0 or unwired; a summon without a finite TTL or with a big petLimit; a drop field moved; she out-stats the Enslaver; she reaches uber charLevel | `tools/debug/negtest_leinth_wave.py` (12 subtests) |
| contract `QST-LEINTH-EXIT` (`tools/contracts/contracts_quests.py`) | any Leinth-death trigger missing part of the exit action set; exit actions pointing at the wrong NPC; the offer tag regressed; the primary back to one-shot; a missing per-variant fallback | `tools/contracts/tests_quests_negative.py::test_leinth_exit` (6 subtests) |
| `tools/build_quest_files.py::_promote_leinth_exit_fallbacks` | primary trigger missing/relabelled; wrong action set on the primary; fewer than 3 fallbacks; emitted bytes not round-tripping; any Leinth-death trigger without the full set | (in-build, fail-loud) |
| `tools/build_quest_files.py::main` | the pristine SVAERA base missing (would double-append the non-idempotent Q1/Q2/Q3/testhub steps onto an already-built arc) | new fail-loud guard added this wave |

**The gates are demonstrably live, not decorative.** `leinth_wave.verify` aborted a real build in
this wave (`R-71 VERIFY FAILED ... svc_leinth_sanguine_mire.dbr spawns a MISSING record r`). The
data was fine; the gate had caught a defect in the gate's OWN code - `get_field_value` returns the
SCALAR for a single-entry array, so iterating it walked the string's characters. Fixed by
normalising to a list before iterating. A second real abort came from
`mastery_sv_alignment.verify` (2 unresolved emblem textures) when an empty
`work/SoulvizierClassic/Resources` directory staged inside the worktree shadowed the main repo's
populated one for that module's ancestor-walking arc resolver; removed, and the build went green.
Neither failure ever reached an artifact: both aborted before the `.arz` was written.

---

## 4b. BUILD, PROOFS AND DEPLOY

See the `BUILD55-DEV GATE RECORD` at the top of `docs/BACKLOG.md` for the full hash table, the
record diff, the contract results and the deployed-vs-built verification. Two facts belong here
because they change how the deploy must be read:

**Text pipeline control proof.** Rebuilding `Text.arc` from the BASELINE build's emitted
`uber_soul_tags.txt` reproduces the currently deployed `Text.arc` byte-for-byte
(`fcca49277b9d31ed451e4a6843898843`). So the Text half of the coupled pair is provably correct, and
any byte that moves in the new `Text.arc` comes only from this wave's six new Leinth skill tags.

**DEPLOY COLLISION with the in-flight `fix/green-diff` lane (read before trusting the DEV surface).**
The DEV `.arz` on disk at wave start (`5143ad1a...`) is NOT a build of `main` (`1c27d5fa...`). A
field-level record diff shows the delta is exactly **one field, `mesh`, on 12 records**:

```
um_toxeus_enslaver_99 / um_bloodtoxeus_99
q_bloodtoxeus_ambush / q_bloodtoxeus_lone / q_enslaver_warband / q_yard_enslaver
soulskills\pets\{bloodtoxeus,toxeus_enslaver}_{1,2,3}
   MAIN     = Creatures\Monster\Skeleton\RevenantPoison.msh
   DEPLOYED = Creatures\Monster\Skeleton\Skeleton01.msh
```

That is unmistakably the parallel `fix/green-diff` lane's green-glow fix (RevenantPoison renders
green), deployed to DEV for its own QA and not yet merged to `main`. **This wave's code touches no
FX or mesh field whatsoever** (PART A moves only `treasureProxyName`; PART B moves only stats, skill
slots and cast wiring; PART C is Quests-only), but ANY `.arz` built from `main` necessarily reverts
those 12 mesh fields. The remedy is merge order, not a code change: merge `fix/green-diff` and
`feat/leinth-wave` and rebuild once, and both land together. Until then the pre-wave DEV `.arz` is
preserved verbatim at
`local/db_backups/SoulvizierClassicDEV_pre-b94_5143ad1a.arz` and restoring it is a single file copy.

---

## 5. OPEN WILL QUESTIONS (carried, not assumed)

1. **ORB CALIBRE EXACTNESS.** "Same calibre" is implemented as **same VOLUME on a BETTER item
   pool** (Leinth's four knobs laid on the champions' existing Act-4 tables at gold level 88). The
   alternative reading, strictly identical to Leinth, would DOWN-tier the champions to the Act-3
   63-65 band. Not recommended. Confirm the reading.
2. **R-47 AMENDMENT.** A new un-named generic tier `genericbossorb_05` shared by both champions
   keeps R-47's substance but adds a tier the ruling does not mention. The alternative (edit
   `genericbossorb_04` in place) silently buffs 21 bosses. Confirm the new tier.
3. **SHOULD LEINTH ALSO GET AN ORB?** She has no `genericbossorb` today: her bespoke DRX chest IS
   her orb, and it is literally named "Leinth's Essense". Left exactly as-is (the instruction was
   not to nerf her). Hang an orb on her as well, or leave it?
4. **THE TWO STAGED POISON RIGS.** `cerberus_acidpuddle_summon` / `cerberus_acidpuddle_attack` sit
   unused in her OWN folder. Rejected as off-identity (poison, on the one poison-weak boss). Use
   them anyway?
5. **HOW MUCH STRONGER.** Shipped ~1.6x life + physical 10->35 / pierce 20->45 + three abilities
   (roughly 2-2.5x time-to-kill for a physical build, ~1.6x for a caster). She was deliberately NOT
   pushed to uber tier. Right target?
6. **PORTAL ONE-WAY OR TWO-WAY?** The shipped offer is one-way to the occultist; the way back in is
   the normal walk-in cave route. Recommend leaving it one-way.
7. **RESIDUAL EXIT CASE.** A character who already killed Leinth while the one-shot was latched and
   who never kills her again is still stranded. Want a no-kill fallback as well (for example, show
   the portal on level load whenever the boss trap door is already open)?

---

## 6. RISKS AND HONEST RESIDUALS

1. **The exit root cause is INFERRED, not proven.** The shipped bytes prove the fallbacks lacked
   ShowNpc/BoatDialog and that the primary was a non-resettable proxy-wide condition over a pool
   that also carries champion blood demons. Which of those paths actually failed on Will's
   character cannot be proven from static data. The fix is designed to be robust to all of them.
   If the portal still fails after this, the remaining unknown is `Condition_ShowNpc`/`BoatDialog`
   binding semantics on an SV-only appended host level.
2. **Normal-band difficulty.** `characterLife` is a single value scaled per difficulty by the
   `globalproperties_{normal,epic,legendary}01` skills, so the +60% plus the physical/pierce change
   could make her disproportionately brutal in the level-47 Normal band. Time-to-kill cannot be
   measured statically. Verify Normal specifically in play, not just Legendary.
3. **Multiplayer.** The spawn equations are `(3+(1.6*numberOfPlayers))*k`, so raising `k` multiplies
   orb loot in MP too (at 6 players roughly 2.6x the 1-player figure). This is the SAME shape
   Leinth already ships, so it is not a new class of risk, but the champions should be eyeballed at
   6P before any Steam push. Related known hazard: SV's `RunEquation` MP spawn-scaling already
   fails to parse in AE.
4. **`genericbossorb_04` blast radius.** Avoided by construction, and the gate asserts orb04 plus
   all of its remaining consumers stay untouched, so a future refactor cannot reintroduce it.
5. **The parallel `fix/green-diff` lane** owns the Enslaver and Devourer FX and skill visuals. This
   wave touches only `treasureProxyName` on those two records (a drops field) plus entirely new
   container/loot records. Zero overlap with FX, `skillName*` or any visual field. See the deploy
   hazard below for the merge-order consequence.
6. **Mute-traveler regression class.** `tools/debug/gate_traveler_responds.py` deliberately EXCLUDES
   the base/SV boatmen, the vortex portal among them, so nothing gated this exit before. The new
   `QST-LEINTH-EXIT` contract now covers it. Extending `gate_traveler_responds.py` itself is
   registered as debt.
7. **ENVIRONMENT: a FULL `Quests.arc` rebuild is impossible on this machine.** Neither
   `reference_mods/SVAERA_customquest/Resources/Quests.arc` (the pristine base `main()` restores)
   nor `upstream/soulvizier_098i/Resources/XPack/Quests.arc` (the SV area-quest source) is present.
   PART C therefore shipped through the new `--promote-leinth-exit` surgical mode, which produces
   byte-for-byte what the full pipeline produces: the shipped entry is by construction
   `_harden_guardian_door_unlocks(_neutralize_bloodcave_entry_step(<upstream>))`, which is exactly
   the input the promotion asserts and refuses without. Proven idempotent (a second run emits a
   byte-identical arc). A new fail-loud guard in `main()` stops a full run from silently
   double-appending the non-idempotent Q1/Q2/Q3/testhub triggers onto an already-built arc.
   Registered as BL-b94-DEBT-6.
8. **DEPLOY COLLISION (the reason the deploy section below reads the way it does).** The DEV arz on
   disk at wave start (`5143ad1a...`) is NOT a build of `main` (`1c27d5fa...`, which is also the
   brief's stated ground truth). A record diff shows **12 records, 1 field each**, all in the Toxeus
   FX/identity family: `um_toxeus_enslaver_99`, `um_bloodtoxeus_99`, the six
   `skills\soulskills\pets\{bloodtoxeus,toxeus_enslaver}_{1,2,3}` soul pets and four
   `drxmap\proxy\q_*` proxies. That is another in-flight lane's work deployed for its own QA. Any
   arz built from `main` (including this one) necessarily reverts those 12 records. See the deploy
   section for the backup + restore path and the merge-order remedy.
