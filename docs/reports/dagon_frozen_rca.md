# DAGON FROZEN - RCA + FIX (the maenad freeze class, second instance)

> **STATUS: FIXED + GATED.** `tools/patches/dagon_anim_rig.py`, registered after `thrown_anim_rig`.
> Dry-run verified with the REAL `apply`/`verify` against the shipped build83 (`44499f56`): PRE RED,
> POST GREEN, idempotent, **one** record modified, **21** fields written (all animation), kit and
> identity byte-unchanged. 15/15 negative tests pass; 42/42 `.anm` assets resolve. Static gates only
> - the Ship lane owns the heavy build, and in-game confirmation belongs to Will's test pass.

> **Will (2026-08-11):** *"Dagon, lord of the poisoned deep is frozen like the maened thrown
> object guys were"*
>
> He named the class correctly: the freeze lives on the **animation surface** and survives a correct
> fix to the kit/equipment surface. The mechanism inside that class turned out to be a different one
> from the maenads', and section 2 is the story of getting that wrong once.

**Ground truth:** `local/build83_run1_44499f56.arz` (the shipped build83, 51,253 records), base game
`database.arz` (74,013 records), `upstream/soulvizier_098i/Database/database.arz`, and the `.msh` /
`.anm` binaries inside the base game's `Resources\*.arc`. All probes read-only.

---

## 1. THE PRECEDENT (found first, then reused)

`02f1807` / `83d9fc2` / `adfda67` - **R-100 #15, the frozen thrown-wielders.**

Will's words then: *"they spawn and they cant move or attack or anything they are broken."*
The RCA's finding, restated as a law:

> A creature is a statue when, for the stance it is in, **neither its own record nor its
> `charAnimationTableName` supplies a usable `.anm`** for the movement + attack slots
> (`RunAnim`, `WalkAnim`, `AttackAnim1`).

Three properties of that precedent carry over exactly:

1. **The animation surface, not the equipment/kit surface, is the freeze.** `thrown_restore` had
   already fixed the maenads' equipment and they stayed frozen. Here `b52`'s `_fix_dagon_kit`
   already fixed Dagon's skills and he stayed frozen. Same shape, twice.
2. **The union law.** A slot is unbound only if *neither* surface supplies it. The record
   OVERRIDES the table, so a record-level clip shadows the table's.
3. **Static gates miss it** because the records resolve fine as records. What fails is downstream
   of the record: a reference into a namespace that was never shipped, or a clip that cannot drive
   the mesh it is bound to.

The maenads failed on the *first* of those. Dagon fails on the *second*, and the word "usable" in
the law above is doing work the original RCA never had to test.

---

## 2. THE WRONG VERDICT, AND THE RECORD THAT KILLED IT

This lane's first answer was: *`unarmedWalkAnim` is unbound on both surfaces, he equips nothing, so
he has no walk animation and stands - the R-100 #15 condition, met exactly.* Every fact in that
sentence is true. The conclusion is false, and **his own donor proves it.**

`records\test\boss_dagon_66.dbr` is a copy of `records\creature\monster\questbosses\boss_hydra_66.dbr`:

| measurement | result |
|---|---|
| fields shared by the two records | 1,043 (Dagon carries 1,065, the Hydra 1,044) |
| shared fields holding **identical values** | **977** |
| animation clips: same slots? | **yes**, all 13 |
| animation clips: same values? | **yes**, byte for byte |
| `boss_hydra_66.charAnimationTableName` | **absent** - it names no table at all |
| `boss_hydra_66` walk clip, any stance | **none** |
| does `boss_hydra_66` animate in the shipping game? | **yes** - it is the Act 1 Hydra quest boss |

So "no walk clip anywhere, plus no animation table" is a state the base game ships on a boss that
plays perfectly. It cannot be what freezes Dagon. **The one thing SV changed when it made Dagon out
of the Hydra is the `mesh`.**

That correction matters beyond this record: it is the same class of error this lane flagged in
b52's RCA (a true observation that was not the cause), and the fix would have shipped with a wrong
explanation attached to it had the vet not gone back to the bytes.

---

## 3. THE ACTUAL BROKEN CHAIN (measured)

`records\test\boss_dagon_66.dbr` - `Class=Monster`, `monsterClassification=Boss`, spawn-referenced by
**23** ichthian pool records (`nameChampion*` in `records\proxies greek\area001\pools\beastmen\
icthian_*`).

```
mesh                   = Creatures\Monster\Ichthian\IchthianMage01.msh
charAnimationTableName = records\creature\monster\d2custom\anm\anm_dagon.dbr
```

**(a) Every clip he binds is authored for a different skeleton.** All 13 are
`Creatures\Monster\Hydra\ANM\Hydra_*.anm`, inherited from the donor above. Read out of
`Creatures.arc` and compared bone-name to bone-name against the meshes:

| pair | bones the clip drives that the mesh actually has |
|---|---|
| `IchthianMage01.msh` <- `Ichthian_Walk.anm` (his own rig) | 24 / 30 = **80%** |
| `IchthianMage01.msh` <- `Ichthian_Run.anm` | 22 / 30 = **73%** |
| `IchthianMage01.msh` <- `JackalMan_DieAlpha.anm` (what his 43 siblings use) | 20 / 30 = **67%** |
| `Hydra01.msh` <- `Hydra_Run.anm` (the donor's own pairing) | 69 / 101 = **68%** |
| **`IchthianMage01.msh` <- `Hydra_Run.anm` (what SV shipped)** | **8 / 101 = 8%** |

The Hydra clips drive a 101-bone rig built around three necks and three heads
(`Bone_MainNeck01..08`, `Bone_L_BkNeck01..07`, `Bone_L_Claw01..06`, `Bone_L_FrJaw` ...). The
IchthianMage01 mesh has 30 bones and none of that hierarchy; the eight names in common are generic
(`Bone_Root`, `Bone_Spine01`, `Bone_L_Femur`, `Bone_L_Shin` ...). Meanwhile every limb the ichthian
rig actually has - clavicles, forearms, wrists, weapon bones, fins, the horse bone - is driven by
nothing at all.

*(Method, stated so it can be checked: bone names are recovered by scanning the decompressed asset
for printable `Bone_*` strings. It is a lossy scan, and both sides of every comparison are measured
the same lossy way, so the ratios are comparable to each other and not to anything else. See section
6 for why this measurement is honest evidence for one record and a bad gate for the database.)*

**(b) The base game never pairs those two.** 54 base-game `Class=Monster` records carry
`IchthianMage01.msh`. Between their own clips and the tables they name they drive it with
**ichthian, jackalman, satyr, neanderthal, boarman, eurynomus** clips. **Hydra does not appear**, and
across all 51,253 records of build83 Dagon is the **only** record that pairs a Hydra clip with this
mesh.

**(c) The one surface that could have fixed it is a dangling reference.**
`d2custom\anm\anm_dagon.dbr` resolves in **NEITHER** the mod arz **NOR** the base game arz; there are
**0** `d2custom` records in either database. It contributes **0** clips. So there is no in-rig
fallback: the record's wrong-rig clips are the only animation the engine can reach, and per the union
law they would shadow the table's anyway.

That is the chain: **wrong rig, no fallback.** `unarmedWalkAnim` being unbound (and
`unarmedAttackAnim2/3`, `unarmedFidgetAnim1` with it) is a symptom of the same sloppy copy, not the
cause.

**Provenance - not ours.** SV 0.98i's own `database.arz` carries `boss_dagon_66` with the *identical*
dead table, the *identical* 13 Hydra clips and the *identical* Ichthian mesh. The record is a
frankenstein: an **Ichthian** mesh, a **Hydra** animation set, a **Harpy** `ActorName`, and a
**d2custom** table.

**Why b52 missed it.** The b52 RCA explicitly cleared the animation/movement surface - *"It is NOT a
movement/speed/mesh problem"* - on the strength of `characterRunSpeed = 1.1` and a behaviour-field
diff against a mobile same-mesh shaman. Both readings were true and both were irrelevant: the diff
compared AI/movement *fields*, and neither `charAnimationTableName` nor the clip slots are behaviour
fields. The kit fix (dead `d2custom` skills -> real ichthian skills) was correct and is kept; it was
simply not the freeze.

---

## 4. HIS SIGNATURE MOVE HAD NO ANIMATION EITHER

Separate from the freeze, found while checking the stance. The engine plays a skill's animation by
matching the skill record's `skillSpecialAnimationName` against the creature's
`<stance>SpecialAnimRef<N>` and playing the paired `<stance>SpecialAnim<N>`.

| his kit (b52) | `skillSpecialAnimationName` | had a ref slot? |
|---|---|---|
| `ichthian_tidalstrike` (**primary**, the WILL_DECISIONS signature move) | `TidalStrike` | **no** |
| `hydra_superbite` | `SuperBite` | yes |
| `nehebkau_poisongasbomb` | `PoisonBomb` | **no** |
| `ichthian_tidalorb`, `venomnova` | none (they use the generic attack anim) | n/a |

His four ref slots held `IceBreath / FireBreath / PoisonBreath / SuperBite` - Hydra leftovers again,
of which exactly one matches his kit. **Tidal Strike therefore fell through to the generic attack
animation.** This is not a freeze and never was a ship blocker - measured across the base game,
**1,202 of the 2,048** monsters whose kit demands a named animation have at least one demand that
neither their record nor their `charAnimationTableName` answers (59%), so the engine clearly
degrades gracefully, but on the mod's own uber it is worth fixing, and `anm_ichthian` already answers the
name `TidalStrike` in its spear stance, so the rig has a designated clip for it.

---

## 5. THE FIX

Module `tools/patches/dagon_anim_rig.py`, registered immediately after `thrown_anim_rig` (the other
half of the same failure class). **Animation fields only, one record, idempotent.**

**(1) Repoint the table** onto the one **43 of his 44 same-mesh siblings** already use:

```
records\creature\monster\d2custom\anm\anm_dagon.dbr        (dead)
  ->  records\creature\monster\ichthian\anm\anm_ichthian.dbr
```

It resolves, it is a clean `database\Templates\CharAnimationTable.tpl` (**not** the `Monster.tpl`
corruption SV inflicted on `ANM_Maenad`), and it binds **71 clips**, including all 12 `unarmed`
slots. **No clone is needed and no shared record is edited** - unlike the maenad fix, which had to
*modify* its tables and therefore had to clone them, this only *points at* one. The 43 existing
carriers are untouched.

**(2) Rebuild the stance in-rig, on BOTH surfaces** (the `adfda67` law: write identical values to the
record and the table so the engine gets the same animation whichever surface it reads):

| slot | was (Hydra rig, 8% bone match) | now (Ichthian rig, matches the mesh) |
|---|---|---|
| `unarmedWalkAnim` | UNBOUND | `Ichthian_Walk.anm` |
| `unarmedRunAnim` | `Hydra_Run.anm` | `Ichthian_Run.anm` |
| `unarmedAttackAnim1` | `Hydra_AttAlpha.anm` | `IchthianMage_Staff_AttAlpha.anm` |
| `unarmedAttackAnim2` | UNBOUND | `IchthianMage_Staff_AttBeta.anm` |
| `unarmedAttackAnim3` | UNBOUND | `IchthianMage_Staff_AttGamma.anm` |
| `unarmedAttackIdleAnim` | `Hydra_AttIdle.anm` | `IchthianMage_Staff_AttIdle.anm` |
| `unarmedSpellAttackAnim` | `Hydra_AttAlpha.anm` | `IchthianMage_Staff_Skill_CastProjectile.anm` |
| `unarmedBuffOtherAnim1` / `unarmedBuffSelfAnim1` | `Hydra_AttAlpha.anm` | `IchthianMage_Staff_Skill_BuffOther.anm` |
| `unarmedStunAnim` | `Hydra_Stun.anm` | `Ichthian_Stun.anm` |
| `unarmedFidgetAnim1` | UNBOUND | `Ichthian_Emote_AllAlpha.anm` |
| `unarmedDieAnim1` | `Hydra_DieAlpha.anm` | `JackalMan_DieAlpha.anm` (what the 43 siblings use; the base game drives this mesh with JackalMan clips, and `anm_ichthian` binds them for its whole dHanded stance) |
| `unarmedSpecialAnim1` | `Hydra_Skill_IceBreath.anm` | `IchthianMage_Staff_AttBeta.anm` |
| `unarmedSpecialAnim2` | `Hydra_Skill_FireBreath.anm` | `IchthianMage_Staff_Skill_BuffOther.anm` |
| `unarmedSpecialAnim3` | `Hydra_Skill_PoisonBreath.anm` | `IchthianMage_Staff_Skill_CastProjectile.anm` |
| `unarmedSpecialAnim4` | `Hydra_AttBeta.anm` | `IchthianMage_Staff_AttGamma.anm` |
| `unarmedLongIdleAnim` | `Hydra_Idle.anm` | `Ichthian_Emote_AllAlpha.anm` |

Measured against the table: **12 of the 17 are the byte-identical value `anm_ichthian` binds for the
same slot, 0 differ from it, and 5 are slots the table does not bind at all** (`unarmedDieAnim1`,
`unarmedLongIdleAnim`, `unarmedSpecialAnim2/3/4`). Those five are drawn from clips the table binds
elsewhere for this rig, so every value is proven in-rig and proven present as an asset.

**(3) Point the name-keyed refs at his actual kit:**

| slot | was | now | why |
|---|---|---|---|
| `unarmedSpecialAnimRef1` | `IceBreath` | `SkonerosBolt` | the table's own value for slot 1, so record and table agree (adfda67). Inert for his kit. |
| `unarmedSpecialAnimRef2` | `FireBreath` | **`TidalStrike`** | his signature move, paired with the clip `anm_ichthian` itself answers `TidalStrike` with (`spearSpecialAnim1` = `IchthianMage_Staff_Skill_BuffOther.anm`) |
| `unarmedSpecialAnimRef3` | `PoisonBreath` | **`PoisonBomb`** | `nehebkau_poisongasbomb`, paired with the cast clip |
| `unarmedSpecialAnimRef4` | `SuperBite` | `SuperBite` | already correct, kept |

**Identity preserved (measured, not asserted).** `description = tagSVCMonsterDagon`
("Dagon, Lord of the Poisoned Deep"), `specialAttackSkillName` = Tidal Strike, `skillName1..5`,
`characterRunSpeed`, `characterLife`, `mesh`, `monsterClassification`, his soul and its 66% drop: all
byte-unchanged. 21 fields written, every one an animation field, on one record.

**Crash laws honored:** no FX field on a monster record (animation clips are not FX), no `Pet.tpl`
equipment copy, no `clone_record`, no explicit `dtype`.

**Left alone, deliberately:** `ActorName = Greece_Creature_Monster_Harpy_HarpyCrag01` is a third
cross-rig leftover (42 of the 43 working same-mesh ichthians carry no `ActorName` at all). It is not
the freeze, it is byte-identical in SV 0.98i, and changing an actor binding has sound/actor
consequences this lane cannot measure. Filed `BL-DAGON-ACTORNAME-1`.

**What the fix does NOT prove.** That he walks. Static evidence establishes that his chain now
resolves to clips the shipping game drives this exact mesh with, on the table 43 working siblings
run on. Only Will's play pass can confirm the animation on screen.

---

## 6. THE GATE - what it closes, and what it honestly does not

### 6a. Per record (hard, always)

`_verify_dagon` encodes the mechanism on the record that had it:

- his table must be `anm_ichthian` and must resolve;
- **every clip he binds must come from a family the shipping game itself drives an `IchthianMage01`
  with** (`ichthian, jackalman, satyr, neanderthal, boarman, eurynomus` - the 54-record census of
  section 3b). This replaced a hardcoded `\hydra\` blacklist: negative test 5b plants a **Medusa**
  clip, which is proven on `medusa01.msh` and still wrong here, and the gate goes RED;
- all 17 unarmed slots bound on the record, agreeing with the table wherever the table binds them;
- **every named special in his KIT owns a ref slot** - read from the skill records at gate time
  (case-insensitively), so the invariant follows the kit rather than a hardcoded list;
- his b52 identity survives (name tag + Tidal Strike primary).

### 6b. DB-wide (the roster clause)

> **Every `Class=Monster` record with a `mesh` that NAMES a `charAnimationTableName` resolving in
> NEITHER the mod overlay NOR the base game arz must complete `RunAnim` + `WalkAnim` +
> `AttackAnim1` for at least one stance ON ITS OWN RECORD.**

HARD FAIL when the violator is spawn-referenced (the Dagon case), WARN when it is inert (the
`am_raptor_thunderlizard_33` case, so a pre-existing cut-content backlog can never block a build),
and the whole clause degrades to WARN when no base install is found (the `validate_tags` precedent).

**This closes the DANGLING-REFERENCE half of the class, not the cross-rig half.** It is what caught
Dagon from the outside and it would have caught him the moment SV wrote the dead table. It would
**not** catch a monster whose table resolves while its record overrides the critical slots with
clips for the wrong skeleton, because record clips win per field. That blind spot is registered as
**`BL-DAGON-CROSSRIG-DEBT-1`**.

Two weaker statements of the roster invariant were implemented and measured against build83 before
this one survived:

| candidate invariant | result on build83 |
|---|---|
| "bind Run/Walk/Attack1 for every stance you bind any clip for" | **1,399 violations** - mostly base monsters carrying a stray clip for a stance they never enter |
| "bind Run/Walk/Attack1 for the stance you fight in" | **60 spawn-referenced violations, every one correct base-game design**: rooted plants (quilvine, nightblossom, deathvine, hellflower), `Class=Monster` props (siege towers, crystal shards, `talos_decoration`, `manticore_bones`), flying bosses with no walk clip, non-combat quest NPCs with no attack clip |

Immobility is *authored* all over the base game, so a missing clip cannot be the signal. What
separates Dagon is that his reference **resolves from nothing**: a rooted quilvine names
`anm_quilvine`, which loads and deliberately binds no walk.

**Measured DB-wide on build83: exactly 2 findings** - Dagon (HARD, 23 pool referrers) and the inert
raptor (WARN). The gate scans the **mod overlay**, which is the right scope for a build gate. For the
record, the merged mod-plus-base view holds **7,112** `Class=Monster` records carrying a mesh and
**8** dead-table namers; the extra one is base-only
`records\xpack4\creatures\monster\test\soundtest\testsubject3.dbr` -> `anm_GorillaShaman.dbr`, which
completes four stances on its own record and is therefore not a violation. **The violation set is
identical either way.**

### 6c. Why there is no DB-wide cross-rig gate (three measurements, all negative)

Every natural generalisation of the per-record clause was implemented and measured. All three cry
wolf, and a gate that cries wolf is not a gate:

| candidate | measured on build83 | verdict |
|---|---|---|
| **bone overlap from the assets** (fail when a clip's bones are largely absent from the mesh) | proven base-game pairs sit as low as **10%** (`CryptWorm01.msh` <- `JackalMan_Walk.anm`, 21 records) and **18-24%** (`SepulchralWyrm01.msh` <- `arachnos` clips, which the **base game itself ships**), overlapping Dagon's 8-10% | no threshold separates them; the metric is sound for a single hand-checked record and useless as a discriminator |
| **cross-family screen** (mesh folder != clip folder) | **4,406** distinct (mesh, clip) pairs across **274** family combos; base monsters routinely borrow rigs (skeleton <- egypt_npc_male, ichthian <- jackalman/satyr, wraith <- mummy) | endemic by design, not a signal |
| **base-game provenance** (fail on a clip family the shipping game never pairs with this mesh) - the rule the per-record clause uses | **322** critical-slot hits DB-wide, dominated by inherited SV records that ship and play (naiad on maenad clips, mantid on male clips, maenad tables on `anims\*`) | correct for ONE mesh whose 54 base carriers were read by hand; unsafe as a blanket rule because SV's own art borrows rigs the base game never did, and this lane cannot verify 322 records in game |

So the honest position: **the cross-rig mechanism is gated per record, and the pattern above is the
one to copy onto the next custom monster.** DB-wide it is a debt, registered with these numbers, and
the offline sweep that produced them is how to re-check it.

`skeletaltyphon` is the control that keeps the roster clause honest: a *shipping base-game boss* that
carries a dead animation table in vanilla and animates perfectly, because its record binds all three
critical slots itself (with GiantTurtle clips, on a mesh the shipping game proves that rig for). A
naive "dead table = fail" gate would red the vanilla game; the union law separates it from Dagon
cleanly.

### 6d. Negative tests

`py tools/patches/dagon_anim_rig.py --negtest <arz>`, **15/15 PASS**, nothing leaked:

| # | planted defect | gate | expect |
|---|---|---|---|
| 1 | repoint the table back at `d2custom\anm\anm_dagon` | Dagon | **RED** (the shipped bug) |
| 2-4 | lose `unarmedWalkAnim` / `unarmedRunAnim` / `unarmedAttackAnim1` from the record | Dagon | **RED** |
| 5 | leave a `Hydra_*.anm` clip on the Ichthian-mesh record | Dagon | **RED** (the wrong rig) |
| 5b | bind a **Medusa** clip (proven on another mesh) | Dagon | **RED** (allowlist, not a hydra blacklist) |
| 5c | revert a ref slot to its Hydra leftover | Dagon | **RED** |
| 5d | no ref answers `TidalStrike` (the shipped state of the ref slots) | Dagon | **RED** (kit clause, on its own) |
| 6 | point the table at a `.msh` instead of a table `.dbr` | Dagon | **RED** |
| 7 | clobber the b52 Tidal Strike primary | Dagon | **RED** (identity guard) |
| 8 | dead table AND no complete stance on the record - **the statue state reached with no knowledge of Dagon** | roster | **RED** |
| 9 | promote the INERT frozen raptor into a live spawn pool | roster | **RED** (WARN escalates) |
| 10 | drop `unarmedFidgetAnim1` (non-critical) | roster | **stay GREEN** |
| 11 | base-game `skeletaltyphon` untouched (dead table + complete record) | roster | **stay GREEN** |
| 12 | rooted quilvine (authored immobility, table RESOLVES) | roster | **stay GREEN** |

**Assets: 42/42 resolve, 0 missing.** `tools/debug/probe_anm_asset_resolve.py` covers the whole
frozen class (`thrown_anim_rig` + `dagon_anim_rig`), printing the exact inner archive path each clip
matched; all the Ichthian/JackalMan clips are in base `Creatures.arc`.

---

## 7. FOUND IN PASSING, NOT FIXED HERE

- **`BL-DAGON-DEADSKILLS-1`** - the kit clause reads every skill slot, and **4 of them resolve
  nowhere**: `skillName6 = records\xpack\skills\dream\pet\pcloudpet_petskill_pcloud.dbr` and
  `skillName10/11/12 = Records\Game\D2GlobalProperties_{Normal01,Epic_Boss,Legendary_Boss}.dbr` -
  the same never-shipped D2 namespace b52 cleaned out of his primary kit. Inert, pre-existing SV
  residue, WARNed every build so a NEW name in that list reads as a regression. Not fixed here
  because this module writes animation fields only, which is what keeps its field set disjoint from
  `red_uber_orbs` on the same record.
- **`BL-DAGON-ACTORNAME-1`** - the Harpy `ActorName` (section 5).
- **`BL-DAGON-INERT-RAPTOR-1`** - `am_raptor_thunderlizard_33`, frozen by the dangling-table
  mechanism but spawn-referenced by nothing.
- **`BL-DAGON-CROSSRIG-DEBT-1`** - the DB-wide cross-rig blind spot (section 6c).

## 8. Probes (read-only, session scratchpad)

`p1_dagon_dump.py` (full record dump), `p2_chain.py` (chain resolution + same-mesh census),
`p3_sweep.py` (DB-wide dead-table sweep vs base), `p4_union.py` (record-surface union law),
`p5_gap.py` (Dagon vs the working ichthian union, clip by clip), `p6_table.py` (table template type
+ SV 0.98i provenance), `p7_final.py` (full table clip list, ActorName census, spawn-reference test),
`vet_probe.py` (the donor comparison + the merged sweep + the ref census), `p_rig.py` / `p_rig2.py`
(bone-name rig comparison out of `Creatures.arc`), `p_rig3.py` / `p_rig4.py` (cross-family pair
census + asset cost), `p_rig5.py` (stance-level placement of cross-family clips), `p_rig6.py`
(per-mesh base-game clip families - the 54-record census), `p_rig7.py` (the 322-hit provenance
sweep), `dryrun.py` (the real apply/verify against build83).
