# b73 - Toxeus Champions Kit Wave (round 1)

> Registry module `tools/patches/toxeus_champion_kits.py` (apply + verify). Gives the ENCOUNTER
> Toxeus champions the player FIGHTS - the Blood/Devourer of Blood (`um_bloodtoxeus_99`) and the
> Enslaver of Souls (`um_toxeus_enslaver_99`) - the Tears of Blood ability (Will 2026-07-16) plus
> signature identity kits, all built from EXISTING DB skills retuned + re-selected for castability
> and colour. No pets, no souls, no pools, no map (the parallel `feat/toxeus-undivided` PET lane owns
> those). Reference arz = build45 `SoulvizierClassic.arz` (md5 917d9047), read-only.

Will's rulings (verbatim, 2026-07-16):
- "the blood toxeus should have the Tears of Blood ability granted by the Arcane Formula - Blood of Ares"
- "The toxeus devourer of blood should have maybe a 10 second cool down on a weaker version of this ability"
- "we also need to think of some good unique abilities to give to toxeus the murderer, enslaver of souls
  since right now his abilities are pretty generic. he needs some good skills and so does the devourer."

---

## 0. GROUND TRUTH that shapes the design (read first)

**The corridor "Blood Toxeus" and the deep "Devourer of Blood" are ONE record - and share ONE pool.**
Recon of build45 (`champ_topo.py`) proves:

| Placement | Proxy | Pool | Monster |
|---|---|---|---|
| Corridor entrance ambush (~33%) | `q_bloodtoxeus_ambush` | `pools\q_bloodtoxeus_lone` | `um_bloodtoxeus_99` (main) |
| Deep secret-hallway boss (100%) | `q_bloodtoxeus_lone` | `pools\q_bloodtoxeus_lone` | `um_bloodtoxeus_99` (main) |
| Egg-chest guardian | `egg_blooddragon_pack` | `pools\egg_blooddragon` | `um_bloodtoxeus_99` (champion) |

The corridor ambush and the deep waterfall boss point at the **same pool**, so they cannot be given
different Tears of Blood tiers without SPLITTING the corridor into a second monster + pool + repointing
the ambush (which would also touch `toxeus_suite`'s champion-cap gate and eligibility registry). The
record's own display name is **"Toxeus the Murderer, Devourer of Blood"** (`tagMonsterHemorrheus`), so
per Will's exact words the record that IS "the toxeus devourer of blood" gets the weaker 10s version.

**DECISION (round 1): give the shared `um_bloodtoxeus_99` ONE Tears of Blood - the weaker 10s
version - so both the corridor ambush AND the deep boss get the ability (Will: "the blood toxeus
should have the Tears of Blood ability"), at the Devourer's specified 10s cadence.** A separate
FULL-strength corridor version is deferred as **WILL-VETO #1** (recipe in §5) because it needs a
monster+pool split AND a full-strength blood-rain at the EARLY cave entrance risks the "unwinnable"
line the brief warns against (the ambush already spawns a L40 boss on Normal). Flagged for Will to
choose on DEV.

**Castability law honoured (the Ephialtes-nova / boss_skill_fix lesson).** Both champions ride the
`anm_skeleton01` skeleton rig (`RevenantPoison.msh`). Every skill added below has
`skillSpecialAnimationName = None` (a no-special-anim cast) OR is a passive/low-health trigger (no
cast anim at all), so every one is animatable on the skeleton rig. Proof table in §4.

**The 5-slot ceiling.** No monster in the whole DB uses more than `specialAttack5` (probed): the
Monster template caps AI cast slots at 5, and both champions already fill all 5. So new *cast*
abilities REPLACE the "generic" specials Will called out; new *passives* ride free skillName slots
(they auto-trigger, needing no cast slot). This is why the redesign is a swap, not an append.

---

## 1. TEARS OF BLOOD - the ability (decoded)

Chain (all base-AE records, present in build45):
- Artifact `records\xpack\item\artifacts\e_da_bloodofares.dbr` ("Blood of Ares") -> `itemSkillName =
  ...\artifactskills\e_da_bloodofares_tearsofblood.dbr`, autocast controller `...\autocast_items\
  e_da_bloodofares.dbr` = "5% Chance to Fire on Taking Any Damage" (triggerType HitByEnemy) - the
  RETALIATION framing Will referenced.
- Skill `e_da_bloodofares_tearsofblood` = **`Skill_AttackProjectileAreaEffect`**, `specialAnim=None`:
  "Tears of divine blood fall from the sky to do fire + bleeding dmg." Level-1 payload:
  `offensiveSlowFireMin/Max = 88/99` (2s fire DoT), `offensiveSlowBleedingMin = 975` (1s bleed),
  `projectileExplosionRadius = 8`, `skillActiveDuration = 8`, `skillCooldownTime = 120`.
- Monster-castable? YES. Same class + `anim=None` as `empusa_spirit_lifedrainnova` /
  `xsq27_machaegeneral_lifedrainnova`, which real monsters cast. No rig anim needed.

---

## 2. DEVOURER OF BLOOD (`um_bloodtoxeus_99`) - "he DEVOURS BLOOD"

Existing kit already covers a blood nova (`melinoe_bloodboil` @ specialAttack1), a bleeding bladestorm
(3), a life drain (`lifedrain` @ 4), and an exploding-sprite burst (5). What it LACKS is Tears of Blood
and a low-health phase. The one off-identity special is `flashpowder` (an assassin blink) at slot 2 -
so slot 2 is where Tears goes.

| Ability | Mechanic (source lineage) | Wiring | Why it fits |
|---|---|---|---|
| **Tears of Blood** (weak, 10s cd) | NEW `svc_devourer_tearsofblood` = clone of `e_da_bloodofares_tearsofblood` (Skill_AttackProjectileAreaEffect, no anim), damage cut + cd 120->10 + active 8->5 | `skillName16` @ [1,2,3]; **replaces `specialAttack2` (was flashpowder)** @ chance 35 | Will's ability; a recurring fiery-blood rain from the sky is pure "devourer", and drops the off-identity assassin blink |
| **Blood Frenzy** (low-health phase) | EXISTING `quak_bloodfrenzy` (Skill_PassiveOnLifeBuffSelf, no anim) referenced as-is: below 25% HP -> +30% attack speed + bleed & life-leech surge for 6s, crimson `quak_buffpak` FX | `skillName17` @ [4,8,12]; passive - NO cast slot | The brief's "frenzy phase at low health (attack speed + leech surge, crimson FX)", verbatim, from a blood-named record |

Existing `melinoe_bloodboil` (blood nova) + `lifedrain` (blood drain) are LEFT in place (they already
deliver the brief's "blood nova / blood-drain" candidates); the new work is Tears + Frenzy, matching
Will's "beyond the weaker Tears of Blood, 1-2 signatures".

### Tears-of-Blood weakening math (Devourer version)
`svc_devourer_tearsofblood` per-tier (N/E/L), giving the monster `skillLevel16 = [1,2,3]`:
```
offensiveSlowFireMin   = [50,  95, 160]   (base level-1 = 88)
offensiveSlowFireMax   = [60, 110, 185]   (base level-1 = 99)
offensiveSlowBleedingMin = [320, 520, 760] (base level-1 = 975)
skillCooldownTime = 10.0   (base 120.0)   skillActiveDuration = 5.0 (base 8.0)   radius = 8 (kept)
```
Per-cast damage is ~40-60% of the base artifact on Normal, rising to ~1.5-1.8x fire / ~78% bleed on
Legendary - still BELOW the Devourer's own `melinoe_bloodboil` nova (246-605 life + 148-328 bleed at
radius 8). The 120->10s cooldown is the trade: a lower-per-hit but recurring blood-rain, which reads
as a signature rather than a once-per-fight nuke. **Effective-DPS note for Will:** at a 35% cast roll
gated by the 10s cd, it fires roughly every 10-15s. If that feels too frequent, raise the cd or drop
the chance (WILL-VETO #2).

---

## 3. ENSLAVER OF SOULS (`um_toxeus_enslaver_99`) - "he ENSLAVES SOULS"

Will: his kit is "pretty generic." The generic cast slots were `netherstrike` (2), `bladestorm` (3),
`flashpowder` (4). His summon (`svc_enslaver_summonmarauders` @ 1 = raise the enslaved) and
`lethalstrike` (5 = the Murderer's finisher) are on-brand and KEPT. The 3 generic slots become the
enslavement identity:

| Ability | Mechanic (source lineage) | Wiring | Why it fits the ENSLAVER |
|---|---|---|---|
| **Raise Shadow Marauders** (kept) | EXISTING `svc_enslaver_summonmarauders` (Skill_SpawnPetMonster, Summon anim) | `specialAttack1` @ 70 (unchanged) | He raises the enslaved dead - his core verb |
| **Soul-Rip** | NEW `svc_enslaver_soulrip` = clone of `lifedrain` (Skill_AttackSpellChaos, no anim, Long range 18), boosted leech + %-current-life | `skillName16` @ [1,2,3]; **replaces `specialAttack2` (netherstrike)** @ 40 | The brief's "soul-rip (drains player health to heal himself)": a ranged soul-drain beam that heals him |
| **Chains of Servitude** | NEW `svc_enslaver_dominate` (+`_buff`) = clone of `heretic_curse` / `heretic_curse_buff` (Skill_AttackBuffRadius, no anim), tuned to short confusion + fumble + slow | `skillName17` @ [1,2,3]; **replaces `specialAttack3` (bladestorm)** @ 30 | The brief's "dominate/curse (fumble/slow = your body obeys him)": a radius curse; native dark debuff FX |
| **Unholy Dominion** | EXISTING `unholy_rally` (Skill_BuffRadius -> `unholy_rally_buff`, no anim): +28-85% phys, run speed, life regen to ALLIES in radius 10 | `skillName18` @ [1,2,3]; **replaces `specialAttack4` (flashpowder)** @ 30 | The brief's "marauder-empowering aura (his thralls surge when he casts)": the fight becomes about killing the master to weaken his thralls |
| **Lethal Strike** (kept) | EXISTING `lethalstrike` @ specialAttack5 (LethalStrike anim - already animates on his rig) | unchanged @ 35 | Toxeus THE MURDERER's melee finisher |

Net: raise thralls -> rip your soul to heal -> chain your body to his will -> empower his enslaved ->
finish with the Murderer's strike. A coherent "Enslaver of Souls" fight instead of four generic verbs.

### Enslaver ability tuning
```
svc_enslaver_soulrip (clone lifedrain):  offensiveLifeLeechMin=[200,260,340]  offensiveLifeMin=[90,140,210]
    offensiveLifeMax=[120,180,270]  offensivePercentCurrentLifeMin=[3,4,5]  skillCooldownTime=5  maxLevel=3
    (Long range 18 kept; he heals from the drain = "drinks your soul")
svc_enslaver_dominate_buff (clone heretic_curse_buff): SHORTENED from the donor's 3-8s/8s:
    offensiveConfusionChance=[30,35,40]  offensiveConfusionMin=2 Max=3  (2-3s loss of control)
    offensiveFumbleMin=[40,50,60] Dur=3   offensiveSlowRunSpeedMin=[30,35,40] Dur=3
    offensiveSlowAttackSpeedMin=[25,30,35] Dur=3   (dominate skill cd=12 so it cannot be spammed)
unholy_rally: referenced as-is (a shared record; NOT edited) - buffs his marauders, not the player.
```

---

## 4. CASTABILITY PROOF (per skill, on the anm_skeleton01 skeleton rig)

| Skill | Class | specialAnim | Castable? | Evidence |
|---|---|---|---|---|
| `svc_devourer_tearsofblood` | Skill_AttackProjectileAreaEffect | None (inherited) | YES | same class+anim=None as empusa/machae lifedrainnova cast by monsters |
| `quak_bloodfrenzy` | Skill_PassiveOnLifeBuffSelf | None | YES | passive low-health trigger, no cast anim |
| `svc_enslaver_soulrip` | Skill_AttackSpellChaos | None | YES | the Enslaver already carries base `lifedrain` (same class) |
| `svc_enslaver_dominate` | Skill_AttackBuffRadius | None | YES | heretic_curse is a monster-cast curse; no special anim |
| `unholy_rally` | Skill_BuffRadius | None | YES | a monster ally-buff; no special anim |
| kept: `lethalstrike` / `summonmarauders` | AttackWeapon / SpawnPetMonster | LethalStrike / Summon | YES | already cast by the Enslaver today (skeleton rig animates both) |

No new animation is required for any skill. This is the anti-Ephialtes guarantee: nothing was wired
that the rig cannot play.

---

## 5. WILL-VETO LIST (one line each - veto any on DEV)

1. **Corridor gets the SAME weak-10s Tears as the deep boss** (they share one record + one pool). To
   give the corridor a distinct FULL-strength Tears, split `um_bloodtoxeus_99` -> a corridor clone +
   its own pool + repoint `q_bloodtoxeus_ambush` + extend the champion-cap gate (round 2).
2. **Devourer Tears cadence** = 35% cast roll on a 10s cooldown (fires ~every 10-15s). Raise cd / drop
   chance if too frequent.
3. **Devourer loses `flashpowder`** (assassin blink) from its cast rotation to make room for Tears at
   the 5-slot cap; it stays in the skill list, just no longer auto-cast.
4. **Blood Frenzy** triggers below 25% HP: +30% attack speed + bleed/leech surge for 6s (a real
   sub-25% panic phase). Change the threshold or remove if it makes the last quarter too swingy.
5. **Enslaver Soul-Rip self-heal** (200-340% leech) makes him a "you must burst him" fight; lower the
   leech if he out-sustains DPS.
6. **Enslaver Chains of Servitude** briefly (2-3s) confuses + fumbles + slows the player at 30-40%
   chance on a 12s cd. Shorten/soften if the loss-of-control feels unfair.
7. **Enslaver loses `netherstrike`/`bladestorm`/`flashpowder`** from its cast rotation (replaced by
   Soul-Rip / Chains / Unholy Dominion); `summonmarauders` + `lethalstrike` kept.
8. **FX not recoloured** - abilities were SELECTED so their native FX already reads dark (enslave/curse/
   drain) or crimson (blood tears/frenzy); no `charFxPak` edit (avoids the b28 crash trap). Verify the
   in-game colour on DEV; if any reads green, that is a follow-up (not shipped here).

---

## 6. BALANCE (before/after; difficulty band preserved)

No HP, hand-damage, resist, scale, or loot field is touched on either champion. Only skill wiring +
new skill records change. Difficulty band is therefore preserved by construction; the deltas are:
- **Devourer**: +Tears of Blood recurring rain (moderate, below his own bloodboil) + a sub-25% frenzy
  phase. More dynamic, not a stat-check.
- **Enslaver**: trades 3 generic damage verbs for soul-drain-sustain + a short soft-CC + an ally-buff.
  Net threat rises modestly via sustain (Soul-Rip leech) but the fight is more counterable (burst him,
  and the marauder empowerment stops).

No loot / soul-drop / drop-rate field is touched (gated elsewhere per the brief). Pets, souls, and
pools are untouched (the chain gate stays green; `_verify_toxeus_champion_cap` is unaffected because
no pool is edited).

---

## 7. VERIFICATION (full scratch build, EXIT=0)

Scratch build = `local/scratch_b73/SoulvizierClassic.arz`, **md5 `0218d8127b8d8e0c8faa19498412315a`** (built
from main@33d25d6 + this module over build45 inputs; 27-module registry, all 18 verify hooks GREEN).

- **Module apply/verify GREEN.** `[toxeus_champion_kits].verify: OK (4 new skills castable [no special
  anim]; Devourer Tears@2 + Enslaver Soul-Rip@2/Chains@3/Dominion@4 wired @chance>0; all new kit skills
  level>=1; no level-0 special on either champion).` Modified 6 records, 0 tags.
- **Record-diff vs build45 (917d9047): CLEAN.** ADDED = exactly the 4 new skills
  (`svc_devourer_tearsofblood`, `svc_enslaver_soulrip`, `svc_enslaver_dominate`,
  `svc_enslaver_dominate_buff`); CHANGED = exactly the 2 champions (`um_bloodtoxeus_99`,
  `um_toxeus_enslaver_99`); REMOVED = 0. No collateral record touched.
- **Built wiring confirmed in the arz:** Devourer specials = bloodboil@90, **Tears@35** (was
  flashpowder), bladestorm@100, lifedrain@100, lildude@100; Blood Frenzy in `skillName17`. Enslaver
  specials = summon@70, **Soul-Rip@40** (was netherstrike), **Chains@30** (was bladestorm),
  **Unholy Dominion@30** (was flashpowder), lethalstrike@35. Tears cd=10/active=5/maxLvl=3, fire
  [50,95,160]/bleed [320,520,760], anim=None. Soul-Rip leech [200,260,340]/%life [3,4,5]/cd 5.
  Dominate cd=12; buff conf [30,35,40]/fumble [40,50,60]/slowRun [30,35,40].
- **`_verify_toxeus_champion_cap` (toxeus_suite Part D): GREEN** - `2 Blood-Toxeus pool(s) ... each
  surface <= 1 Toxeus at any party size 1-6` (no pool touched, invariant unaffected).
- **boss_skill_fix roster scan: GREEN** - `roster um_*_99 clean of level-0 specials` (every new special
  references a level>=1 kit skill).
- **Chain gate / souls / pets: UNTOUCHED-GREEN** - all other registry verify hooks pass; no soul/pet/pool
  record in the diff.
- **Contracts (souls + summons) on the scratch arz:** souls 0 viol. summons shows 96 P0 + 556 P2 - ALL
  pre-existing base/ported MONSTER-MESH / SUMMON-PET-MESH / MONSTER-SKILLS-LOOT records; **grep of the
  consolidated JSON for any of my 6 records = 0 hits**, i.e. this wave adds ZERO new violations (the
  record-diff proves the only records I touched are the 6, none of which appear in the violation set).
  Baseline (build45) summons run = same 96 P0 (identical pre-existing state). Map/quests contracts not
  run (no map/quest change this wave; the worktree has no `Levels_merged.arc` - owned by the map lane).
- **validate_tags:** no new Text tags minted (monster skills are not player-facing tooltips; the cloned
  skills keep their donors' resolving display tags), so the text-tag invariant is unaffected.
- **Negative test (`champ_negtest.py`): ALL PASS** - `verify()` passes on the clean build and correctly
  FAILS on all 4 planted regressions: Tears skillLevel->0 (level-0 special), Soul-Rip chance->0, Tears
  bad special-anim (castability), Chains special pointed at the wrong skill.
- **Idempotent:** apply() only creates collision-free NEW records + value-overrides on the 2 champions;
  re-running over an already-patched db is a no-op-equivalent (same writes). A7 (Occult/Hunting golden)
  untouched - no mastery record in the diff.
