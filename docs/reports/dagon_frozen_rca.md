# DAGON FROZEN - RCA + FIX (the maenad class, second instance)

> **Will (2026-08-11):** *"Dagon, lord of the poisoned deep is frozen like the maened thrown
> object guys were"*
>
> Will named the class correctly. This is the **same failure class** as the frozen thrown-wielders
> (R-100 #15), and the fix reuses that diagnostic frame verbatim.

**Ground truth:** `local/build83_run1_44499f56.arz` (the shipped build83, 51,253 records), base game
`database.arz` (74,013 records), upstream `upstream/soulvizier_098i/Database/database.arz`.
All probes read-only.

---

## 1. THE PRECEDENT (found first, then reused)

`02f1807` / `83d9fc2` / `adfda67` - **R-100 #15, the frozen thrown-wielders.**

Will's words then: *"they spawn and they cant move or attack or anything they are broken."*
The RCA's finding, restated as a law:

> A creature is a statue when, for the stance it is in, **neither its own record nor its
> `charAnimationTableName` supplies an `.anm`** for the movement + attack slots
> (`RunAnim`, `WalkAnim`, `AttackAnim1`).

Three properties of that precedent that carry over exactly:

1. **The animation surface, not the equipment/kit surface, is the freeze.** `thrown_restore` had
   already fixed the maenads' equipment and they stayed frozen. Here `b52`'s `_fix_dagon_kit`
   already fixed Dagon's skills and he stayed frozen. Same shape, twice.
2. **The union law.** A slot is unbound only if *neither* surface supplies it. The record
   OVERRIDES the table, so a record-level clip shadows the table's.
3. **Static gates miss it** because the records resolve fine as records - what fails is a
   *reference into a namespace that was never shipped*.

---

## 2. THE BROKEN CHAIN (measured)

`records\test\boss_dagon_66.dbr` - mesh `Creatures\Monster\Ichthian\IchthianMage01.msh`,
`Class=Monster`, `monsterClassification=Boss`, spawn-referenced by **23** ichthian pool records
(`nameChampion*` in `records\proxies greek\area001\pools\beastmen\icthian_*`).

```
charAnimationTableName = records\creature\monster\d2custom\anm\anm_dagon.dbr
```

| surface | state |
|---|---|
| the TABLE | `d2custom\anm\anm_dagon.dbr` resolves in **NEITHER** the mod arz **NOR** the base game arz. There are **0** `d2custom` records in the whole database. Contributes **0 clips**. |
| the RECORD | binds **13** `.anm` clips - **every one of them a `Creatures\Monster\Hydra\ANM\Hydra_*.anm`**, on a creature whose mesh is `IchthianMage01`. |
| **`unarmedWalkAnim`** | **unbound on BOTH surfaces.** |

Dagon equips nothing (`chanceToEquipRightHand = 0`, `chanceToEquipLeftHand = 0`), so his only
stance is **`unarmed`**. In that stance the engine finds:

| critical slot | record | table | result |
|---|---|---|---|
| `unarmedRunAnim` | `Hydra_Run.anm` (wrong rig) | - | cross-rig |
| `unarmedAttackAnim1` | `Hydra_AttAlpha.anm` (wrong rig) | - | cross-rig |
| **`unarmedWalkAnim`** | **absent** | **absent** | **UNBOUND -> statue** |

That is the R-100 #15 freeze condition, met exactly. He also cannot resolve `unarmedAttackAnim2`,
`unarmedAttackAnim3` or `unarmedFidgetAnim1` on any surface.

**Provenance - not ours.** SV 0.98i's own `database.arz` carries `boss_dagon_66` with the
*identical* dead table, the *identical* 13 Hydra clips and the *identical* missing
`unarmedWalkAnim`; and `d2custom\anm\anm_dagon.dbr` is absent from **SV's own database too**. This
is the same never-shipped `d2custom` namespace that made his skills dead references in b52 -
SV referenced a Diablo-namespace Dagon that it never built. The record is a frankenstein: an
**Ichthian** mesh, a **Hydra** animation set, a **Harpy** `ActorName`, and a **d2custom** table.

**Why b52 missed it.** The b52 RCA explicitly cleared the animation/movement surface - *"It is NOT
a movement/speed/mesh problem"* - on the strength of `characterRunSpeed = 1.1` and a behaviour-field
diff against a mobile same-mesh shaman. Both readings were true and both were irrelevant: the
diff compared AI/movement *fields*, and `charAnimationTableName` is not one of them. The kit fix
(dead `d2custom` skills -> real ichthian skills) was correct and is kept; it was simply not the
freeze.

---

## 3. WHY NO GATE CAUGHT IT - the same blind spot, twice

`thrown_anim_rig.scan_frozen_throwers` already states the freeze invariant DB-wide. It let Dagon
through on two counts:

1. **Scope.** It only examines monsters that *equip a thrown weapon*. Dagon equips nothing.
2. **The load-bearing assumption** (`table_binds`, verbatim):
   > *"Absent from the overlay -> pure base-game pass-through ... a pass-through table is healthy
   > by construction."*

   That is the **identical** assumption that hid Dagon's *name* in b52, where `validate_tags`
   assumed every non-mod-owned tag *"resolves from the base game"* and never checked. Both times
   the assumption was false for the same record, because `d2custom` resolves from **nothing**.

The generalized gate below closes it the same way b52 closed the tag gate: **cross-check against
the base game arz instead of assuming it.**

---

## 4. CLASS SWEEP - every custom monster, not just Dagon

Invariant swept over all **4,610** `Class=Monster` records in build83, resolving
`charAnimationTableName` against the mod overlay **and** the base game arz:

**7 records name an animation table that exists nowhere.** Applying the union law to each:

| record | table | record surface | spawn-referenced | verdict |
|---|---|---|---|---|
| `records\test\boss_dagon_66` (**Dagon**) | `d2custom\anm\anm_dagon` | 13 Hydra clips, **no WalkAnim** | **23 referrers** | **FROZEN - FIXED here** |
| `records\test\am_raptor_thunderlizard_33` | `raptor\anm\anm_gojiru` | **1** clip (`staffWalkAnim` only) | 0 | **structurally frozen but INERT** - never spawns; listed, not fixed |
| `records\test\bm_gruesomebonescarab_22` | `beetle\ANM\ANM_LightningBeetle` | 15 clips, Run+Walk+Attack1 all bound | 0 | healthy (record covers the stance) |
| `records\test\outsider_hero_caster_46` | `shadowstalker\anm\anm_shadowstalker` | 40 clips, Run+Walk+Attack1 on dHanded/bow/spear | 0 | healthy |
| `records\test\outsider_hero_melee_46` | same | same | 0 | healthy |
| `records\test\outsider_hero_poison_46` | same | same | 0 | healthy |
| `records\xpack\...\skeletaltyphon` | `XPack\...\ANM_SkeletalTyphon` | 15 clips, Run+Walk+Attack1 all bound | 0 (map-placed) | healthy - **and it is the control** |

**Skeletal Typhon is the proof the gate must not over-flag.** It is a *shipping base-game boss*
that carries a dead animation table in vanilla (byte-identical in base `database.arz`) and animates
perfectly, because its record binds all three critical slots itself. A naive "dead table = fail"
gate would red the vanilla game. The union law separates it from Dagon cleanly.

**Result: Dagon was the only spawn-referenced monster in the database whose animation chain
cannot resolve.** The maenad fix was indeed spot-only (thrown stances), but the sweep finds no
second live victim.

---

## 5. THE FIX

Module `tools/patches/dagon_anim_rig.py`, registered immediately after `thrown_anim_rig` (the
other half of the same failure class).

**(1) Repoint the table** onto the one **43 of his 44 same-mesh siblings** already use:

```
records\creature\monster\d2custom\anm\anm_dagon.dbr        (dead)
  ->  records\creature\monster\ichthian\anm\anm_ichthian.dbr
```

It resolves, it is a clean `database\Templates\CharAnimationTable.tpl` (**not** the `Monster.tpl`
corruption SV inflicted on `ANM_Maenad`), and it binds **71 clips**, including all 12 `unarmed`
slots. **No clone is needed and no shared record is edited** - unlike the maenad fix, which had to
*modify* its tables and therefore had to clone them. Here we only *read* the table by pointing at
it; the 43 existing carriers are untouched.

**(2) Restore the stance on BOTH surfaces** (the `adfda67` law: write identical values to the
record and the table so the engine gets the same animation whichever surface it reads). Every one
of the 13 cross-rig Hydra clips is repointed to the in-rig Ichthian clip the table binds, and the
four unbound slots are added:

| slot | was (Hydra, wrong rig) | now (Ichthian, matches the mesh) |
|---|---|---|
| **`unarmedWalkAnim`** | **UNBOUND - the freeze** | `Ichthian_Walk.anm` |
| `unarmedRunAnim` | `Hydra_Run.anm` | `Ichthian_Run.anm` |
| `unarmedAttackAnim1` | `Hydra_AttAlpha.anm` | `IchthianMage_Staff_AttAlpha.anm` |
| `unarmedAttackAnim2` | UNBOUND | `IchthianMage_Staff_AttBeta.anm` |
| `unarmedAttackAnim3` | UNBOUND | `IchthianMage_Staff_AttGamma.anm` |
| `unarmedAttackIdleAnim` | `Hydra_AttIdle.anm` | `IchthianMage_Staff_AttIdle.anm` |
| `unarmedSpellAttackAnim` | `Hydra_AttAlpha.anm` | `IchthianMage_Staff_Skill_CastProjectile.anm` |
| `unarmedBuffOtherAnim1` / `unarmedBuffSelfAnim1` | `Hydra_AttAlpha.anm` | `IchthianMage_Staff_Skill_BuffOther.anm` |
| `unarmedStunAnim` | `Hydra_Stun.anm` | `Ichthian_Stun.anm` |
| `unarmedFidgetAnim1` | UNBOUND | `Ichthian_Emote_AllAlpha.anm` |
| `unarmedDieAnim1` | `Hydra_DieAlpha.anm` | `JackalMan_DieAlpha.anm` (what the same-mesh siblings use; the ichthian rig is JackalMan-compatible - the table itself binds JackalMan clips for `dHanded`) |
| `unarmedSpecialAnim1` | `Hydra_Skill_IceBreath.anm` | `IchthianMage_Staff_AttBeta.anm` |
| `unarmedSpecialAnim2` | `Hydra_Skill_FireBreath.anm` | `IchthianMage_Staff_AttGamma.anm` |
| `unarmedSpecialAnim3` | `Hydra_Skill_PoisonBreath.anm` | `IchthianMage_Staff_Skill_CastProjectile.anm` |
| `unarmedSpecialAnim4` | `Hydra_AttBeta.anm` | `IchthianMage_Staff_AttAlpha.anm` |
| `unarmedLongIdleAnim` | `Hydra_Idle.anm` | `Ichthian_Emote_AllAlpha.anm` |

`SpecialAnim2/3/4` and `LongIdleAnim` are slots the table does not bind, so their values are chosen
from the clips the table *already* binds for the unarmed stance - proven in-rig and proven present.
He keeps 5 animated specials, one per skill in his b52 kit.

**Identity preserved.** Not one gameplay field is touched: his b52 kit (**Tidal Strike** primary,
Tidal Orb, Venom Nova, Super Bite, Poison Gas Bomb), his name tag `tagSVCMonsterDagon`
("Dagon, Lord of the Poisoned Deep"), `characterRunSpeed`, life, damage, his soul and its 66% drop
are all untouched. This module writes **animation fields only**.

**Crash laws honored:** no FX field on a monster record (animation clips are not FX), no
`Pet.tpl` equipment copy, no `clone_record`, no explicit `dtype`.

**Left alone, deliberately:** `ActorName = Greece_Creature_Monster_Harpy_HarpyCrag01` is a third
cross-rig leftover (42 of the 43 working same-mesh ichthians carry no `ActorName` at all). It is
not the freeze, it is byte-identical in SV 0.98i, and changing an actor binding has sound/actor
consequences this lane cannot measure. Filed as `BL-DAGON-ACTORNAME-1`, not fixed here.

---

## 6. THE GATE - a fail-loud playable-anim invariant for MONSTERS

`dagon_anim_rig.verify()` runs in the registry's verify pass and states the invariant over the
**whole roster**, not over Dagon:

> **Every spawn-referenced `Class=Monster` record must resolve, on the union of its own record and
> its `charAnimationTableName` (checked against the mod overlay AND the base game arz), an `.anm`
> for `RunAnim`, `WalkAnim` and `AttackAnim1` in the stance it enters.**

- **HARD FAIL** when a violator is **spawn-referenced** (named by another record - the Dagon case).
- **WARN** when it is inert (never spawned - the `am_raptor_thunderlizard_33` case), so a
  pre-existing cut-content backlog can never block a build.
- Base arz unavailable -> the DB-wide cross-check **degrades to WARN** with a message (build-safe,
  the `validate_tags` precedent), while the **targeted Dagon invariant stays hard** - his table must
  be `anm_ichthian`, all 16 unarmed slots must be bound, and **zero `Hydra\ANM` clips may remain on
  an Ichthian-mesh record**.

This extends the soul-side "every soul must resolve" invariant to wild monsters, which is what the
class was missing: `thrown_anim_rig` gated *thrown* stances only.

**Negative tests** (`py tools/patches/dagon_anim_rig.py --negtest`) - the defect is re-planted and
the gate must go RED:

| # | planted defect | expect |
|---|---|---|
| 1 | repoint the table back at `d2custom\anm\anm_dagon` | **RED** (the shipped bug) |
| 2 | delete `unarmedWalkAnim` from the record, table dead | **RED** (the exact statue state) |
| 3 | delete `unarmedRunAnim`, table dead | **RED** |
| 4 | delete `unarmedAttackAnim1`, table dead | **RED** |
| 5 | leave a `Hydra_*.anm` clip on the Ichthian-mesh record | **RED** (cross-rig clause) |
| 6 | point the table at a `.msh` instead of a `.dbr` table | **RED** |
| 7 | plant a NEW spawn-referenced monster on a nonexistent table with no record clips | **RED** (the invariant is roster-wide, not Dagon-shaped) |
| 8 | drop `unarmedFidgetAnim1` (non-critical slot) | **stay GREEN** |
| 9 | Skeletal Typhon untouched (dead table + complete record surface) | **stay GREEN** |

---

## 7. Probes (read-only, session scratchpad)
`p1_dagon_dump.py` (full record dump), `p2_chain.py` (chain resolution + same-mesh census),
`p3_sweep.py` (DB-wide dead-table sweep vs base), `p4_union.py` (record-surface union law),
`p5_gap.py` (Dagon vs the working ichthian union, clip by clip), `p6_table.py` (table template
type + SV 0.98i provenance), `p7_final.py` (full table clip list, ActorName census,
spawn-reference test).
