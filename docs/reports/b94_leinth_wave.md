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
build-level fact out of the builds this wave produced.

**MERGE NOTE (for the integrator).** This branch is based on `main` @ `8c3445c`, which was `main`'s
HEAD when the wave started and whose build IS the brief's stated ground truth (`1c27d5fa`). While
the wave ran, `main` advanced to `770bc35` (the `fix/debt-gate` + `fix/debt-mixed` debt-clearance
merges). Every diff and hash in this report is therefore stated against `8c3445c`, which is the
correct baseline for judging what this wave changed. The overlap with the newer `main` is three
files, all append-shaped and trivially resolvable:

| file | this wave | newer `main` |
|---|---|---|
| `docs/BACKLOG.md` | prepends the BUILD55-DEV gate record + 6 debt entries | prepends its own gate records + debt entries |
| `docs/WILL_RULINGS.md` | appends a NEW section (decade 70-79) at the end | edits/appends in the existing sections |
| `tools/patches/__init__.py` | appends `leinth_wave` + `uber_apex_orb` before `visuals` | appends `coldworm_buffs` + `uber_quest_markers` before `visuals` |

No source file this wave authored or edited collides with anything on the newer `main`, and the
REGISTRY modules are provably disjoint (no other module names a `bloodwitch` record, and only
`toxeus_souls_100` co-writes the two champion records, on a DIFFERENT field). A rebuild after the
merge picks up both waves.

---

## 1. PART A - ONE apex drop calibre for all three blood-cave bosses (R-72 + R-75)

> ⭐ **ROUND 2 SUPERSEDES ROUND 1 HERE.** Round 1 implemented the design pass's orb plan: move the
> two champions up to Leinth's volume, leave Leinth alone. Will's decision of 2026-07-27, captured
> **verbatim**, overrides that scope:
>
> > "increase the tier of the items dropped by leinth's orb to match the tier dropped by the
> > champions' orb and give that to both toxeus variants and also to leinth"
>
> So the deliverable is ONE apex drop combining BOTH sides' strengths, given to ALL THREE monsters.
> **Leinth is included and upgraded**, not left behind and not nerfed. Ledgered as **R-75**;
> R-72's analysis stands and its scope decision is marked superseded-in-part.
> Everything in this section describes the SHIPPED round-2 state.

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

**THE COUNTER-AXIS - and in round 2 this is not a caveat, it is half the deliverable.** orb04
rolls the HIGHER item tier, on three separate levers:

| tier lever | LEINTH (before) | ORB04 (the champions) |
|---|---|---|
| loot tables | Act-3 band `63-65` mastertables + `03_act3_arcaneformulae` | xpack Act-4 statics `static_*_l01c` + `03_act4_relics` + `03_act4_arcaneformulae` |
| `levelEquationFile` | `c03` = `((avgPlayerLevel*1)/2.05)-12` (normal)<br>`e_c03` = `((avgPlayerLevel*1)/2.01)-23` (epic)<br>`l_c02` = `1*1` (legendary) | `containerlevelequation_all` = `1*1` on **all three** |
| `goldGeneratorLevel` | 30 / 50 / 64 | 47 / 69 / 88 |

The level-equation row is the one that is easy to miss and matters most: on Normal and Epic,
Leinth's chest **divides the player's level** before rolling, so her items were held down to the
Act-3 band by construction. Her Legendary chest was already on the uncapped `1*1`. Corroboration
that `1*1` is the uncapped top-band form and not "item level 1": **all twelve** `l_*`
(legendary-band) equations in the database are `1*1`, and `containerlevelequation_all` is used by
**366** containers including every one of our own SVC boss hoards (Charon/Dorus/Ephialtes/
Obsidian/Tantalus), the DRX hidden blood-cave chests and the base-game hero chests.

So before round 2: orb04's individual items were higher item-level, Leinth's were lower-tier but
~3.25x more numerous and ~2x more unique-weighted. **Each side won a different axis, which is
exactly why Will's instruction is to combine them rather than pick one.**

**Whole-kill context, so the champions are not misrepresented:** they have ELEVEN live equipment
slots (~9.68 expected equipment items including their 100% souls per R-48, the Devourer's
guaranteed `crimsonverdict` and a guaranteed Misc4); Leinth has TWO (`chanceToEquipHead` 100 ->
`lenithsveil`, `chanceToEquipFinger2` 66 -> her soul) = 1.66. Totals ~15.4 vs ~20.2 per kill. So
Leinth still out-rewards them overall, and the entire gap lives in the orb/chest. That is exactly
the thing the report pointed at.

### The two constraints that shaped the fix

**(1) `genericbossorb_04` is shared by TWENTY-ONE boss records** (Sarkoth, Vashkarr, Bloodcrow,
Voranthys, Broodmother, Enslaver, Gorrahk, Ilsevar, Dagon, Ephialtes, Mnemophage-core, Antaeus,
Polis Gaoler, Deep Thresher, Meglograi, bloodcrow_soul, Dorus, Tantalus, Hades Marshal,
Helepolis, Devourer). Editing it in place would silently buff twenty-one encounters and rewrite
the mod's whole endgame economy. Rejected, exactly as the brief required.

**(2) SOLE-OWNERSHIP OF LEINTH'S CHEST - VERIFIED, and this is the fact the brief asked me to
check and state.** The brief permitted upgrading `bosschestproxy_leinth` in place *if it is
referenced only by her*. Scanning **every field of all 51,085 records** (not just
`treasureProxyName` - a field-scoped scan would not be a proof) finds **EXACTLY THREE**
references, and all three are Leinth's own variants:

```
records\drxcreatures\bloodwitch\q_leinth_47.dbr   treasureProxyName
records\drxcreatures\bloodwitch\q_leinth_49.dbr   treasureProxyName
records\drxcreatures\bloodwitch\q_leinth_50.dbr   treasureProxyName
TOTAL references: 3  (distinct records: 3)
```

**She solely owns her chain, so the in-place upgrade is authorised and its blast radius is
provably zero.** `apply()` re-runs this same whole-database scan on the live db every build and
refuses to touch her chain if the referrer set is ever anything other than those three, so a
future record that starts consuming her chest cannot be silently swept into the upgrade.

That proof is also what makes in-place the *better* option than repointing her at the generic
orb: repointing would have destroyed her "Leinth's Essense" name and her chest mesh for zero
mechanical gain, and would have broken R-73's "her bespoke chest survives" assertion.

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

**8 CHANGED fields across 5 pre-existing records - and nothing else in 51,085:**

| record | field(s) | before -> after |
|---|---|---|
| `um_toxeus_enslaver_99` | `treasureProxyName` | `genericbossorb_04` -> `genericbossorb_05` |
| `um_bloodtoxeus_99` | `treasureProxyName` | `genericbossorb_04` -> `genericbossorb_05` |
| `bosschest_leinth_01_normal` | `tables` / `levelEquationFile` | `loottable_leinth_29-31` -> `svc_uberorb_apex_n01c` / `c03` -> `containerlevelequation_all` |
| `bosschest_leinth_02_epic` | `tables` / `levelEquationFile` | `loottable_leinth_49-51` -> `svc_uberorb_apex_e01c` / `e_c03` -> `containerlevelequation_all` |
| `bosschest_leinth_03_legendary` | `tables` / `levelEquationFile` | `loottable_leinth_63-65` -> `svc_uberorb_apex_l01c` / `l_c02` -> `containerlevelequation_all` |

Leinth's THREE MONSTER RECORDS ARE NOT TOUCHED. Her `treasureProxyName` still names her own
`bosschestproxy_leinth`, so R-73's "her bespoke chest survives" assertion in
`tools/patches/leinth_wave.py` stays green by construction rather than by coincidence.

### What Leinth deliberately KEEPS, and why

| field | value kept | why |
|---|---|---|
| `mesh` / `scale` | `DRX\meshes\leinth_chest.msh` / 1.2 | her bespoke player-visible identity |
| `description` | `tagLeinthChest` = "Leinth's Essense" | same; and R-47 forbids AUTHORING new bespoke essences, not keeping hers |
| `goldGenerator` | `typhongoldgenerator` | it is **RICHER** than the champions' `bossgoldgenerator`: `(L^1.6)*48` vs `(L^1.6)*24`. Switching her to theirs would have been a **gold NERF**. She keeps hers AND inherits the higher `goldGeneratorLevel` from the shared table |
| `LockedClassification` | still absent | not an item-tier field, and inert while `locked = 0` (which every consumer, orb04's own chests included, carries). Adding an untested lock field to a boss chest is pure downside |

### RESULT - the calibre table (computed from the built arz, at 1 player)

| monster | expected items | expected uniques | gold level | level equation | item pool |
|---|---|---|---|---|---|
| **Enslaver of Souls** | 5.70 -> **21.16** (3.71x) | 0.174 -> **1.165** | 47/69/88 (kept) | uncapped (kept) | Act-4 (kept) |
| **Devourer of Blood** | 5.70 -> **21.16** (3.71x) | 0.174 -> **1.165** | 47/69/88 (kept) | uncapped (kept) | Act-4 (kept) |
| **Leinth** x3 variants | 18.51 -> **21.16** (1.14x) | 0.913/1.094 -> **1.165** | 30/50/64 -> **47/69/88** | `c03`/`e_c03`/`l_c02` -> **uncapped** | Act-3 63-65 -> **Act-4** |

At 6 players every figure scales by the same equation: 15.62 -> 57.96 for the champions,
50.72 -> 57.96 for Leinth.

**TABLE IDENTITY CHECK - the point of the whole exercise:** on each of the three difficulties all
FIVE monster records resolve to the SAME loot table.

```
normal     IDENTICAL  svc_uberorb_apex_n01c.dbr  <- Enslaver, Devourer, q_leinth_47/49/50
epic       IDENTICAL  svc_uberorb_apex_e01c.dbr  <- Enslaver, Devourer, q_leinth_47/49/50
legendary  IDENTICAL  svc_uberorb_apex_l01c.dbr  <- Enslaver, Devourer, q_leinth_47/49/50
```

**ONE HONEST DOWN-TICK, stated because it is the only one:** Leinth's unique *share* dips from
5.91% to 5.51% on Epic and Legendary (on Normal it RISES, 4.93% -> 5.51%). That is a ratio, not a
reward: because the drop is larger overall, her expected *count* of uniques goes UP on every
difficulty (1.094 -> 1.165 at 1P; 2.996 -> 3.192 at 6P), and they are now Act-4 uniques instead of
Act-3 uniques. She is up on absolute uniques, up on unique tier, up on items, up on gold, and up
on item level. There is no axis on which she is worse off.

**The no-nerf claim is COMPUTED, not asserted.** `apply()` refuses to move her at all unless the
apex table beats her original on all six loot-group chances, both spawn multipliers and
`goldGeneratorLevel`, and `verify()` recomputes the same proof on the final merged arz. Measured,
identical on all three difficulties:

```
g1 12.5->13.0 OK | g2 25.0->32.0 OK | g3 0.0->10.0 OK
g4 100.0->100.0 OK | g5 25.0->32.0 OK | g6 12.5->13.0 OK
```

Her three original loot tables (`loottable_leinth_{29-31,49-51,63-65}`) are deliberately LEFT IN
THE DATABASE, byte-unchanged. Nothing of hers is retired (retirement protocol), and they are what
the gate reads as the live no-nerf reference.

### R-48 is untouched and untouchable here

Souls are Finger2 EQUIPMENT (`lootFinger2Item1` + `chanceToEquipFinger2`); orbs are
`treasureProxyName`. Independent mechanisms. apply() still snapshots both soul fields on both
champions before and after and fails loud if either moved.

---

## 2. PART B - Leinth, the Blood Witch (R-73)

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

## 3. PART C - the post-kill exit to the occultist merchant (R-74)

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
| `tools/patches/uber_apex_orb.py::apply` | Leinth's chest chain gaining ANY referrer other than her 3 variants (whole-db sole-ownership re-proof); the apex table failing the no-nerf proof against her originals; orb04 chain moved; consumers changed by anything other than the 2 champions; R-48 soul wiring moved; her originals edited; her proxy/pools/monster records moved; her chests changing any field other than the 2 intended | (in-apply, fail-loud) |
| `tools/patches/uber_apex_orb.py::verify` | not exactly 2 orb05 carriers; broken orb05 chain on any difficulty; any of the 4 knobs below Leinth's originals; orb04 stripped of its other consumers; R-48 below 100; **any Leinth chest not on the shared apex table + level equation**; **her mesh / "Leinth's Essense" tag / richer gold generator lost**; **a Leinth variant repointed off her own proxy**; **the computed no-nerf proof failing on any of the 6 loot groups x 3 difficulties** | `tools/debug/negtest_uber_apex_orb.py` (**16 subtests**, 6 of them the Leinth half) |
| `tools/patches/leinth_wave.py::apply` | any loot/drop field on the 3 variants moved; a kit slot or cast mechanism already occupied | (in-apply, fail-loud) |
| `tools/patches/leinth_wave.py::verify` | any stat target moved; poison weakness changed; a new skill at level 0 or unwired; a summon without a finite TTL or with a big petLimit; a drop field moved; she out-stats the Enslaver; she reaches uber charLevel | `tools/debug/negtest_leinth_wave.py` (12 subtests) |
| contract `QST-LEINTH-EXIT` (`tools/contracts/contracts_quests.py`) | any Leinth-death trigger missing part of the exit action set; exit actions pointing at the wrong NPC; the offer tag regressed; the primary back to one-shot; a missing per-variant fallback | `tools/contracts/tests_quests_negative.py::test_leinth_exit` (6 subtests) |
| `tools/build_quest_files.py::_promote_leinth_exit_fallbacks` | primary trigger missing/relabelled; wrong action set on the primary; fewer than 3 fallbacks; emitted bytes not round-tripping; any Leinth-death trigger without the full set | (in-build, fail-loud) |
| `tools/build_quest_files.py::main` | the pristine SVAERA base missing (would double-append the non-idempotent Q1/Q2/Q3/testhub steps onto an already-built arc) | new fail-loud guard added this wave |

**The gates are demonstrably live, not decorative.** `leinth_wave.verify` aborted a real build in
this wave (`R-73 VERIFY FAILED ... svc_leinth_sanguine_mire.dbr spawns a MISSING record r`). The
data was fine; the gate had caught a defect in the gate's OWN code - `get_field_value` returns the
SCALAR for a single-entry array, so iterating it walked the string's characters. Fixed by
normalising to a list before iterating. A second real abort came from
`mastery_sv_alignment.verify` (2 unresolved emblem textures) when an empty
`work/SoulvizierClassic/Resources` directory staged inside the worktree shadowed the main repo's
populated one for that module's ancestor-walking arc resolver; removed, and the build went green.
Neither failure ever reached an artifact: both aborted before the `.arz` was written.

---

## 4a. ROUND 2 BUILD, PROOFS AND DEPLOY (the shipped state)

`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, built from this branch. **Build exit 0** with the whole
fail-loud battery green.

| artifact | md5 | note |
|---|---|---|
| baseline `SoulvizierClassic.arz` (`main` build = the brief's ground truth) | `1c27d5fa650b5c076696db4ad379672f` | 51,085 records |
| **round-2 `SoulvizierClassic.arz`** | **`9f98e3e88bca20f96bacc2fd6bb87b63`** | 51,098 records, 55,429,716 B |
| round-1 arz (superseded) | `0d861748df91442ab860995cdea243eb` | kept for the diff trail |
| `uber_soul_tags.txt` (build-emitted) | `c89194fc6f3427cf25712ad8ee6af5fc` | **byte-identical to round 1** - PART A adds zero tags |
| `Text.arc` (rebuilt from that emitted file) | `ed31ec8407e59710d4ad28d5532e75ae` | **byte-identical to round 1 / to what is deployed** |
| `Quests.arc` (PART C, unchanged in round 2) | `35bfe3f39e8480408e3c22ea5473f796` | |
| `Levels.arc` BEFORE == AFTER (never touched) | `943d0ab9516d332db79bd7f9fd2d3ffe` | |

**COUPLING SATISFIED WITH A PROOF, NOT AN ASSUMPTION.** The arz+Text pair was rebuilt together;
because PART A authors no Text tag, the rebuilt `Text.arc` came out byte-identical to the deployed
one. That is a stronger result than "Text unchanged, probably fine": the file was actually
regenerated from the new build's own emitted tag stream and then hash-compared.

**RECORD DIFF (baseline -> round-2 build): INTENDED-ONLY, zero collateral.**
`ADDED 13 / REMOVED 0 / CHANGED 9` (22 differing records total).

* **ADDED 13** = the 10 orb05 chain records + the 3 Leinth cult skills. Nothing else.
* **CHANGED 9** = `um_toxeus_enslaver_99` (1 field), `um_bloodtoxeus_99` (1 field),
  `q_leinth_{47,49,50}` (17 fields each, PART B), `leinth_summon_uglies` (3 fields, PART B), and
  `bosschest_leinth_{01_normal,02_epic,03_legendary}` (**exactly 2 fields each**, PART A).
* **COLLATERAL SENTINEL** (scans the whole diff for any `mesh` / `skin` / `baseTexture` / `bitmap`
  / `fx` / `Effect` / `shroud` / `chanceToEquip` / `lootFinger` / `dropItems` / `treasureProxy`
  field): the ONLY hits are the two intended `treasureProxyName` writes. **Not one FX, mesh, skin,
  texture or soul-drop field moved anywhere in the roster.**

**GATES**

| gate | result |
|---|---|
| `uber_apex_orb.verify` on the final merged arz | **OK** |
| `leinth_wave.verify` on the final merged arz | **OK** |
| `negtest_uber_apex_orb.py` | **16/16** (was 10/10; +6 for the Leinth half) |
| `negtest_leinth_wave.py` | **12/12** |
| `tests_quests_negative.py` (incl. `QST-LEINTH-EXIT`) | **25/25** |
| `validate_tags` | **PASS**, 362/362 referenced mod tags resolve |
| patches-registry selfcheck | OK, 35 modules |

**CONTRACT SUITE - 56 contracts, 5 modules, and this wave adds ZERO violations at ANY severity.**
Run over the round-2 arz + round-2 Text + the deployed Quests + the deployed (unchanged) Levels +
the full deployed Resources dir:

| domain | contracts | P0 | P1 | P2 |
|---|---|---|---|---|
| map | 18 | 0 | 0 | 3 |
| quests | 9 | 0 | 0 | 2 |
| resources | 6 | 0 | 0 | 4815 |
| souls | 10 | 0 | 0 | 0 |
| summons | 13 | 0 | 0 | 112 |
| **TOTAL** | **56** | **0** | **0** | **4932** |

`GATE: PASS`. **The baseline comparison is the load-bearing part:** the IDENTICAL configuration
run against the BASELINE arz (`1c27d5fa`) + the pre-wave `Text.arc` (`fcca4927`) yields **exactly
`0 P0 / 0 P1 / 4932 P2`** as well. So the count is provably unchanged and this wave introduced
nothing.

> NOTE ON THE ROUND-1 "1252 resources P1" FIGURE: that number came from a run where the mod
> `Resources` directory was not reachable, so 1252 assets could not be resolved. Pointing
> `--resource-arc-dir` at the real deployed `Resources` folder resolves them and the P1 count is
> 0 on BOTH the baseline and this build. The pre-existing debt is P2-class, not P1.

### DEPLOYED to DEV

Coupled **arz + Text**; `Quests.arc` was already the b94 one from round 1 (PART C is unchanged in
round 2) and `Levels.arc` was never touched.

| deployed artifact | md5 | verdict |
|---|---|---|
| `Database/SoulvizierClassicDEV.arz` | `9f98e3e88bca20f96bacc2fd6bb87b63` | **== built** |
| `Resources/Text.arc` | `ed31ec8407e59710d4ad28d5532e75ae` | **== built** (coupled pair) |
| `Resources/Quests.arc` | `35bfe3f39e8480408e3c22ea5473f796` | **UNCHANGED** (== the pre-deploy backup) |
| `Resources/Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | **UNTOUCHED** (mtime still 2026-07-27 16:48, predating this wave) |

Backups taken before the deploy: `local/db_backups/SoulvizierClassicDEV_pre-b94r2_f3015aa3.arz`,
`local/db_backups/DEV_Text_pre-b94r2_ed31ec84.arc`,
`local/db_backups/DEV_Quests_pre-b94r2_35bfe3f3.arc`.

**DEPLOYED RE-PROBE** (gates re-run against the bytes actually on disk, not against the build):
`uber_apex_orb.verify` **OK** and `leinth_wave.verify` **OK** on the deployed `.arz`;
`validate_tags` **PASS** on the deployed arz + deployed Text; all six new Leinth skill tags read
back out of the deployed `Text.arc` with their real strings ("Crimson Tithe", "Choir of the
Bloodborn", "Sanguine Mire" + descriptions).

### ⚠️ TWO DEPLOY CAVEATS WILL MUST READ

**(1) TQ.exe WAS RUNNING at deploy time.** I am not permitted to kill TQ or Steam, so I could not
apply the standing restart-before-test rule myself. The write landed (hash-verified above), but
the running game still holds the OLD database in memory. **Will must fully quit TQ and Steam and
restart before testing anything in this wave.** Test the exit portal on a character/difficulty
whose boss room has NOT already been cleared.

**(2) THE `fix/green-diff` LANE'S DEV MESH WORK WAS REVERTED BY THIS DEPLOY, AGAIN.** The DEV arz
on disk beforehand (`f3015aa3`) was round 1's b94 build PLUS that parallel lane's mesh swap, which
has since iterated to `GoldenSkeleton01.msh` on **15** records:

```
um_toxeus_enslaver_99 / um_bloodtoxeus_99
q_bloodtoxeus_ambush / q_bloodtoxeus_lone / q_enslaver_warband / q_yard_enslaver
soulskills\pets\{bloodtoxeus,toxeus_enslaver,toxeus_eoat}_{1,2,3}
   deployed-before = Creatures\Monster\Skeleton\GoldenSkeleton01.msh
   main / this build = Creatures\Monster\Skeleton\RevenantPoison.msh
```

**This wave's code touches no mesh or FX field whatsoever** (the collateral sentinel above proves
it), but any arz built from `main` necessarily reverts those 15 fields, and mine did. I did NOT
hand-compose an arz that merges both lanes, because the brief requires `deployed == built` and the
repo's own law requires builds to regenerate deterministically from committed code; a stitched
artifact would satisfy neither. **The remedy is merge order, not a code change:** merge
`fix/green-diff` and `feat/leinth-wave` and rebuild once, and both lands together. One-file restore
of the pre-deploy DEV arz is `local/db_backups/SoulvizierClassicDEV_pre-b94r2_f3015aa3.arz`.

---

## 4b. ROUND 1 BUILD, PROOFS AND DEPLOY (historical - superseded by 4a)

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

> Round 2 CLOSED the first three. They are kept here, struck through, so the record shows how they
> were answered rather than silently vanishing.

1. ~~**ORB CALIBRE EXACTNESS.**~~ **ANSWERED by Will's 2026-07-27 decision.** Not "same volume on a
   better pool for the champions only" - ONE apex calibre combining Leinth's generosity with the
   champions' tier, given to all three. Implemented; see PART A.
2. ~~**R-47 AMENDMENT.**~~ **RESOLVED without needing one.** The new tier is still un-named,
   generic and shared, and Leinth's pre-existing bespoke essence is re-tiered rather than authored,
   so R-47's prohibition (on AUTHORING bespoke essences per boss) is never engaged. Ledgered as
   R-75 with the reconciliation spelled out. Editing `genericbossorb_04` in place stays rejected
   (21 bosses).
3. ~~**SHOULD LEINTH ALSO GET AN ORB?**~~ **ANSWERED: yes, she is included** - but by re-tiering
   her own chest rather than hanging a generic orb on her, which is strictly better for her
   (identity kept, richer gold generator kept, same item calibre as the champions). Sole-ownership
   was verified first, exactly as the brief required.
4. **THE TWO STAGED POISON RIGS.** `cerberus_acidpuddle_summon` / `cerberus_acidpuddle_attack` sit
   unused in her OWN folder. Rejected as off-identity (poison, on the one poison-weak boss). Use
   them anyway? **STILL OPEN.**
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

---

> ROUND 3 SUPERSEDES PARTS OF SECTIONS 2 AND 3 ABOVE. Everything in sections 0-4 describes
> rounds 1-2 and is kept as the decision trail; where round 3 contradicts it, ROUND 3 WINS.
> R-numbers: the b94 entries were renumbered +2 (R-70..R-73 -> R-72..R-76) when main landed
> its own R-70/R-71 in the 2026-07-28 ledger-hygiene pass. No ruling text changed.

## 5. ROUND 3 (2026-07-29) - WILL ANSWERED THE FOUR QUESTIONS: Leinth's honour guard, the staged poison rigs, the swarm kept, the no-kill exit (2026-07-29, branch `feat/leinth-wave`, tag `build60-dev`)

> ⭐⭐ **WILL ANSWERED THE FOUR DESIGN QUESTIONS ON 2026-07-27. Three of the four answers go AGAINST
> the implementer's recommendation. They are law; this round implements them, including the
> reversals.** Ledgered VERBATIM as **R-76**, which **SUPERSEDES R-73 IN PART**.
>
> | Q | Will, verbatim | what round 1 had recommended | what shipped |
> |---|---|---|---|
> | Q4 how much stronger | *"lets give her some guardians like amgoz1 gave hades"* | stat inflation (+60% life, resists) | an **HONOUR GUARD**; the modest stat work is kept, no uber-tier push |
> | Q6 staged poison rigs | *"Use them AND remove her poison weakness"* | REJECT as off-identity | **both rigs wired**, `defensivePoison` -15 -> **+15** |
> | Q7 the ugly swarm | *"Keep the swarm as-is"* | cut 4;6;8/16 -> 2;3;4/6 + TTL | **cut REVERTED IN FULL**; risk measured + flagged instead |
> | Q9 stranded character | add the no-kill fallback | (was the open residual) | **`Condition_OnLevelLoad` fallback**, no `Action_OpenDoor` |

### PART D (NEW) - THE HONOUR GUARD, mirrored from what amgoz1/DRX actually built

The real Hades guardians were traced in the shipped bytes BEFORE anything was designed:
`xq06_boss_hades_champions.dbr` (FileDescription "DRX") is a **separate proxy** from the boss proxy,
carrying the guard's own mesh (`gigantes01_quest.msh` @ 2.8), sharing the boss's difficulty/limit
files and `quest=1`, pointing at `xq06_boss_hades_champion_pool.dbr` (`spawnMin=spawnMax=1`,
`championMax=1`, `name1 = drxdishonorguard\anapaest_45`). A placement census over **all 2,282
levels** finds it placed exactly **TWICE**, both in `HadesPalace_Floor05_04.lvl`.

The literal mirror needs two new placements in `bossfight.lvl` (a Levels.arc rebuild). **Not taken**,
because this repo already ships the DB-side equivalent and **its donor is literally Leinth's own
pool**: `_svc_boss_pool`, "the 1-boss + 2-guaranteed-champion recipe (spawnMax=3 /
championChance=100 / championMin=Max=2 -> 3-2=1 guaranteed boss; the LAW)", shipping in `neferkha`,
`diadochi` and the Hades Marshal. Applied to `q_leinth_lone` in place. **Levels.arc BYTE-UNCHANGED.**

* Her three variant `name` slots, weights and limits are **untouched** -> the single main is still a
  random `q_leinth_47/49/50`.
* `_svc_neutralize_pool_equation` is **mandatory, not cosmetic**: the inherited `proxypoolequation_02`
  scales the literal counts by 1.357 and floors them -> 4-2 = **TWO Leinths side by side**, the exact
  deterministic defect Will reported 2026-07-13. verify() fails if it ever returns.
* Guards (amgoz1 bar, zero new art/FX/sound, both from her OWN cult):
  `svc_leinth_guard_reaver` <- `d_reaver_42` ("Blood Reaver of the Sanctuary", no summons at all) and
  `svc_leinth_guard_disciple` <- `c_disciple_42` ("Voice of the Bloodborn"). Both at HER band
  `[47,62,74]`, Champion, scale 1.9, real Text names.
* The Disciple's inherited `disciple_summon_bloodbeast` is petLimit 4 with **NO TTL** (the b76
  defect), so the guard gets a **cloned** copy capped at 2 / 20s; the shared original is never
  written. The clone also drops the donor's 3 **dangling** loot refs so the wave adds zero new
  contract violations.
* **Deliberate exit-trigger interaction:** the guards ride in `q_leinth_lone`, the pool R-74's primary
  `Condition_KillAllCreaturesFromProxy` watches, so the primary now needs the whole guard dead. That
  is the right reading, and it is why R-74's three per-variant fallbacks plus the new no-kill
  fallback are load-bearing.

### PART B' - both staged poison rigs live, weakness removed

All three records DRX staged in her own folder have **ZERO referrers** in the 51k-record db (exact-path
scan, not substring). **THE FREE WIN:** the "attack" rig is not a boss self-buff competing for a
scarce cast slot - it is the **puddle's own aura**, so wiring the SUMMON alone brings **both** of
Will's rigs live through ONE slot. Her summon is re-chained onto HER puddle and that puddle onto HER
aura (DRX aimed both at the xpack copies), leaving the xpack Cerberus chain byte-clean.

`defensivePoison` **-15 -> +15**: not invented, it is exactly her own cult heavy `d_reaver_42`'s
value. Removes the weakness without immunity (poison stays her softest resist by a wide margin, so
the counter-play survives). verify() fails on a negative value AND on immunity.

**Slot accounting.** Monster records expose five castable `specialAttack` slots (census
3164/1602/894/300/170; the only three `specialAttack6` users are `Pet.tpl` records from our own prior
wave). Her four bespoke DRX specials hold 1-4, so there is exactly ONE free slot and round 1 spent it
on the implementer's own Crimson Tithe. **Will's instruction outranks it:** `specialAttack5` -> the
acid rig; Crimson Tithe -> `dyingSkillName` (79 shipping records carry its class there).
`numAttackSlots` stays 4 - it is NOT a special-attack cap (46 shipping records run 4 with five wired).

**RETIREMENT, stated not silent (R-73 names both):** `svc_leinth_choir_bloodborn` and
`svc_leinth_sanguine_mire` are retired. Both were round-1 inventions on this unmerged branch, never
shipped to Will. The honour guard is his own answer to what Choir existed for; the acid puddle is the
authentic DRX rig for what Mire existed for.

### ⚠️ BL-b94-DEBT-9 (P1, WILL DECISION) - THE ENTITY BUDGET EXCEEDS THE b76 THRESHOLD

Will asked for the number and it is **measured, not estimated**:

| source | count | lifetime |
|---|---|---|
| Leinth | 1 | - |
| honour guards | 2 | permanent |
| `summoned_ugly` | 16 | **PERMANENT (no TTL)** - Will: keep as-is |
| `leinth_heatseeker_pet` | 10 | **PERMANENT (no TTL)** - her shipped DRX kit |
| acid puddles | 10 | 6s |
| guard bloodbeasts | 2 | 20s |
| **TOTAL** | **41 concurrent** | **26 of them PERMANENT** |

The b76 chumbi-freeze RCA measures the standalone offender `um_voranthys_99` at **25 PERMANENT**
summons (petLimit 9+8+8) and states that even standing alone that "degrades over a long fight".
**26 EXCEEDS it.** Nothing Will told me to keep was reduced; the only density lever pulled was
retiring two of the implementer's OWN round-1 skills. **This needs Will's call after a play test.**
The cheapest reductions if he wants one, in order: a finite TTL on `leinth_heatseeker` (10 permanent
pets, his DRX kit, never discussed), then the ugly `petLimit`.

### ⚠️ BL-b94-DEBT-10 (P2, WILL DECISION) - the exit vortex is now visible on entry

The `.qst` vocabulary has **no door-state condition**, so Will's literal "whenever the boss trap door
is already open" is not expressible. `Condition_OnLevelLoad` is the only mechanism that satisfies his
actual requirement (nobody stranded, including his own latched character). Cost: the vortex is visible
from the moment the player enters the Sanctuary rather than appearing when she dies. **If Will prefers
the reveal, deleting this ONE trigger restores it** and the three kill fallbacks still cover every
case except the already-latched character he asked to rescue. `Action_OpenDoor` is deliberately
stripped, so the boss door stays earned either way.

### ⚠️ BL-b94-DEBT-11 (P1, MERGE ORDER) - DEV collision with the unmerged `feat/sargath-soul` lane

The DEV arz on disk was **not** a build of `main`: it carried the unmerged `feat/sargath-soul` lane's
4 records (`summon_sargoth` + `sargoth_1/2/3`) plus 41 modified. Merging `main` into this branch
removed most of the collision (was 8 removed / 247 modified, now 4 removed / 41 modified), but the
sargath residual is another lane's **unmerged** work and a build from this branch necessarily reverts
it. Deployed anyway (DEV is the shared test surface and the wave is untestable otherwise), but the
pre-deploy state is backed up **byte-exact** and the action is fully reversible:
`local/db_backups/SoulvizierClassicDEV_pre-b94r3_f6cd8698.arz` (+ `DEV_Text_pre-b94r3_4162a3e0.arc`,
`DEV_Quests_pre-b94r3_35bfe3f3.arc`). **Remedy is merge order, not a hand-stitched arz** (which would
break deployed==built and deterministic regeneration). This is the third occurrence of this class
(see BL-b94-DEBT-7); it wants a standing rule, not another per-wave note.

### ⚠️ BL-b94-DEBT-12 (P2, TOOLING) - worktree `work/.../Resources` shadows the main cache

`mastery_sv_alignment`'s ancestor-walking arc resolver stops at the FIRST
`work/SoulvizierClassic/Resources` it finds. A worktree that has staged only `Text.arc` there
shadows the main checkout's populated one and the build aborts on 2 "unresolved emblem texture"
FAILs. Worked around by moving the partial dir aside during the DB build. This bit round 1 too;
the resolver should require the dir to actually contain `.arc` files before accepting it.

### GATES (all green)

| gate | result |
|---|---|
| `leinth_wave.verify` on the final merged arz | **OK** |
| `uber_apex_orb.verify` on the final merged arz | **OK** |
| `tools/debug/negtest_leinth_wave.py` | **23/23** (was 12/12; +11 round-3 negatives) |
| `tools/debug/negtest_uber_apex_orb.py` | **16/16** |
| `tools/contracts/tests_quests_negative.py` | **31/31** (was 25/25; +6 for `QST-LEINTH-NOKILL`) |
| `validate_tags` | **PASS** |
| contracts battery (5 modules) | **0 P0 / 0 P1 / 4737 P2, GATE PASS** |
| both module verifies re-probed on the **DEPLOYED** bytes | **OK** |

**PROOF THE FIX IS REAL, NOT ASSERTED:** the new `QST-LEINTH-NOKILL` contract **fires P0 on the
PRE-WAVE bytes and is silent on the built bytes**. Run over the baseline with an identical config:
**1 P0 / 1252 P1 / 3658 P2**; over the pre-merge build: **0 P0 / 1252 P1 / 3658 P2**. The wave removes
exactly the one P0 it targets and adds **zero** violations at any severity (the 1252 resources P1s
were pre-existing and identical on both; `main`'s debt-wave has since cleared them, which is why the
post-merge number is 0 P1).

### PROOFS

| artifact | md5 | note |
|---|---|---|
| `SoulvizierClassic.arz` | `9cdb9ebaa0d277f5001b629a276a05d3` | post-merge build |
| `Text.arc` (from the BUILD-EMITTED `uber_soul_tags.txt` `ee0185f4f0340b0a1dfd33f61c619d0e`) | `6981d27903dc42a736f2a90c86c5903c` | coupled |
| `Quests.arc` | `bd0fb5f99d88fab74b81f27b7cb952b2` | PART C + the new no-kill fallback |
| `Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | **BEFORE == AFTER, never touched** |

**Record diff, round 3 delta only (vs round 2's deployed arz): 3 added / 2 removed / 7 modified,
every field intended, zero collateral.** Added = the 2 guards + the capped bloodbeast summon.
Removed = the 2 retired round-1 skills. Modified = the 3 variants (poison + slot moves), the 2 acid
records (re-chained + named), `leinth_summon_uglies` (**reverted to shipped**), and the pool (the
escort LAW).

### ⚠️ TESTING - RESTART STEAM AND TQ FIRST

TQ.exe was NOT running at deploy time, but Steam was (killing either is banned for this lane). The
write is hash-verified `deployed == built`, but per the standing rule **Will must fully restart Steam
and TQ before testing** or he is testing stale in-memory data.

---
