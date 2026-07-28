# b91 - COLD WORM BUFFS LANE (R-39), branch `fix/debt-mixed`

Will's ruling (docs/WILL_RULINGS.md R-39, 2026-07-16), verbatim:

> Cold Worm needs ~3x characterLife and +20% armor (`defensiveProtection`) ON TOP of the
> already-queued kit (burrow/frost skills that actually cast), a massive total-speed boost,
> the exclamation-marker mechanism extended to all placed ubers, and the 3-tier soul +
> loot-triple fix + roster drop-slot sweep - ships as ONE lane, not piecemeal.

**Status: 5 of the 6 sub-items SHIPPED + build-verified. 1 sub-item (the exclamation-point map
marker) is BLOCKED and is NOT claimed as done** - see section 7.

---

## 0. The stranded worktree: there were no partials

R-39 and the BACKLOG both say "worktree `coldworm-markers` has partials". That is **not true of
this checkout**. `.claude/worktrees/coldworm-markers` sits on `feat/coldworm-uber-markers` at
`75110bd`, which `git merge-base --is-ancestor 75110bd main` proves is an **ancestor of `main`**:
zero commits ahead, a clean tree, and no untracked files. `git diff main...feat/coldworm-uber-markers`
is empty. So nothing was recovered because nothing was ever committed there; the lane was started
and abandoned before any work landed. This lane was therefore built from ground truth, not resumed.

---

## 1. RCA: why the kit never cast (the real defect)

`records\test\boss_coldworm50.dbr` is an SV-0.98i-inherited leftover of an older "D2" conversion.
Its ENTIRE skill kit pointed at a record namespace that **ships nowhere**:

```
records\skills\boss skills\d2custom\coldworm_{shockwave, shockwave_sec, dropceiling,
    poisongas, layegg, summonbug, summonbugs, initial}.dbr
Records\Game\D2GlobalProperties_{Normal01, Epic_Boss, Legendary_Boss}.dbr
Records\Game\D2Boss_ConversionImmunity.dbr
```

Verified absent (case-insensitively) from **all three** possible sources:

| source | coldworm skill records | `d2custom` namespace |
|---|---|---|
| the built mod arz (`local/baseline_build47.arz`, 51,085 records) | 0 | 0 |
| `upstream/soulvizier_098i/Database/database.arz` (51,186 records) | 0 (only the monster) | 0 |
| base game `database.arz` (74,013 records) | 0 | 0 |

A roster-wide scan of the full **active** slot surface (`attackSkillName`, `initialSkillName`,
`dyingSkillName`, `specialAttackSkillName`, `specialAttack2..5SkillName`) ranks Cold Worm as the
single worst record in the entire database:

```
MONSTERS WHOSE **ENTIRE** ACTIVE SKILL KIT IS DANGLING: 83
   8/ 8 dead  records\test\boss_coldworm50.dbr     <-- worst in the DB
   2/ 2 dead  records\creature\monster\skeleton\quest\as_frostmagi_07.dbr
   2/ 2 dead  records\skills\...\alastor_skeletonpriest_10.dbr
   ... (every other entry is 1/1 or 2/2)
```

Consequences, all three real: Cold Worm **casts nothing**; it has **no difficulty-scaling
globals** (skillName10/11/12 dead); and it is **player-CONVERTIBLE** (its conversion-immunity
passive is dead - the same defect class `boss_skill_fix` fixed for the `um_*_99` apex bosses).

This is fixed at the record layer (BL-103 fix-upstream): every dead slot is repointed at a donor
that **exists**, not patched around.

---

## 2. Donor discipline (the `boss_skill_fix` precedent)

Cold Worm rides the CryptWorm rig (`Creatures\Monster\CryptWorm\CryptWorm01.msh`,
`characterRacialProfile = Insectoid`). Its identity donor is **`um_coldcreep_29`** - "Cold Creep",
the COLD CryptWorm-rig hero - plus the native `am_devourer_*` line. Every skill is (a) present in
the db and (b) already carried by a CryptWorm-rig monster or the nearest-tier insectoid boss, and
every LEVEL is copied verbatim from that donor. No blanket constants, no invented numbers.

| slot | new skill | level | donor the level came from |
|---|---|---|---|
| skillName1 / `dyingSkillName` | `ondeath_cryptworms` | [3] | `am_devourer_27` skillName1 |
| skillName2 | `coldcreep_frostslow` | [4,6,8] | `um_coldcreep_29` skillName1 |
| skillName3 / `specialAttack` | `drxfreezingblast` | [3,4,5] | `um_coldcreep_29` skillName3 |
| skillName4 / `specialAttack2` | `iceblasts` | [2,4,6] | `um_coldcreep_29` skillName4 |
| skillName5 / `specialAttack3` | `giantkarkinos_flightofthekondor` (**the BURROW**) | [1] | `um_deeptresher_47` skillName3 (`skillMaxLevel`=1) |
| skillName6 / `specialAttack4` | `cryptworm_megapoisonball` | [3] | `am_devourer_27` skillName3 |
| skillName7 | `retaliation_1coldperlevelx100levels` | [40,55,70] | `um_coldcreep_29` skillName5 |
| skillName8 | `armor_passive` | **[72,209,432]** | its own levels x1.2 (R-39 armor, S3) |
| skillName9 | `racial_insectoid` | [1] | universal insectoid level |
| skillName10/11/12 | `globalproperties_{normal,epic,legendary}01` | [1,0,0]/[0,1,0]/[0,0,1] | the vanilla difficulty convention |
| skillName13 | `physdmg_meleeonly` | [1,2,3] | `am_devourer_27` skillName7 |
| skillName14 | `boss_conversionimmunity` | [1,2,3] | its own kept levels (`skillMaxLevel`=3) |
| skillName15 / `attackSkillName` | `meleeattack_+5physicalperlvlx100` | [8,16,24] | `boss_scarabaeus_27` (nearest insectoid boss) |
| skillName16 / `initialSkillName` | `enchantment_cold` | [10,12,14] | `um_coldpaw_29` skillName4 |
| skillName17 / `specialAttack5` | `arachne_close_poisoncloud` | [14,17,20] | `um_sajaki_44` skillName3 |

The special-attack **tuning** (chance/delay/timeout/range) is likewise copied off the donor that
natively drives that skill in that slot - except `specialAttack5`, where amgoz1's **own** SV
slot-5 tuning (25% / 6s / 2s / LongRange) is preserved because the ROLE is preserved: that slot
was `coldworm_poisongas` and is now a real poison cloud.

Result, to the amgoz1 bar: **a burrowing frost worm that still spits poison**, on a boss literally
named Cold Worm whose kit was previously poison-only and entirely dead.

`attackSkillName` and `initialSkillName` were repointed rather than blanked: **zero** monsters in
the database carry an empty string in either field, so blanking is not a precedented state.

---

## 3. "+20% armor (`defensiveProtection`)" - the layer question, settled by evidence

Will named the field `defensiveProtection`. Applying it literally to the record would have been a
no-op, and the reason is measurable:

* **`defensiveProtection` non-zero carriers among Monster-class records: 0.**
* **`defensiveProtectionModifier` non-zero carriers among Monster-class records: 0.**

Monster armor in this game is delivered **exclusively** by the `armor_passive` skill, and that
skill's `defensiveProtection` array is exactly **linear**:

```
records\skills\monster skills\defense\armor_passive.dbr
  defensiveProtection = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0] ...(800 entries)
  skillMaxLevel       = [1000]
```

so **`armor_passive` level N grants exactly N `defensiveProtection`**. Cold Worm's level
`[60, 174, 360]` therefore *is* its `defensiveProtection`, and +20% is
`[72, 209, 432]`. This is Will's field, at the only layer where the number does anything -
not a re-interpretation of the ruling.

## 3b. "3x characterLife" and "massive total-speed boost"

* Life: `[14000, 18000, 22000]` -> `[42000, 54000, 66000]` (exactly 3x).
* Speed: the **rig-proven** `um_coldcreep_29` profile is adopted wholesale, so every value is a
  real shipped value on the identical rig rather than a guess:

| field | before | after | why |
|---|---|---|---|
| `characterRunSpeed` | 0.75 | 1.8 | `um_coldcreep_29` |
| `characterAttackSpeed` | 0.8 | 1.5 | `um_coldcreep_29` |
| `characterSpellCastSpeed` | 1.0 | 1.1 | `um_coldcreep_29` |
| `walkSpeed` | 1.0 | 2.0 | `um_coldcreep_29` / `am_devourer_27` |
| `maxRotationSpeed` | **0.3** | 12.0 | `um_coldcreep_29`; at 0.3 the boss could barely turn |
| `minRotationSpeed` | **0.1** | 9.0 | `um_coldcreep_29` |
| 9 animation playback speeds | **0.15 - 0.4** | 1.0 | the whole CryptWorm family runs these at 1.0 |

The animation half matters as much as the movement half: Cold Worm played every anim it uses at
one-fifth speed, which is most of why it read as glacial - and raising movement without raising
the anims would have made it skate. Only the slots the live kit plays are touched; the emote/idle
slots (5-9) are left exactly as SV authored them.

---

## 4. NEW INVARIANT + GATE: an active skill slot must be *castable*, not merely wired

R-39's "skills that actually cast" is a class, not one record, so it ships with its own gate.

**The invariant.** For every active skill slot on a monster: the referenced skill must resolve,
AND if that skill declares a `skillSpecialAnimationName`, the caster must bind that ref name to a
non-empty animation via `unarmedSpecialAnimRef<i>` / `unarmedSpecialAnim<i>`. Otherwise the engine
has no playable animation for the skill and never starts it. This is the **monster-side twin of
B-SOUL-PROC-2** (the StartSkill anim abort that silently killed 29 soul-granted summons).

The invariant is load-bearing for this very lane. Two of the new skills carry an anim requirement:

* `iceblasts` needs `'Burst'`. Cold Worm bound no such ref, so this lane adds **slot 10** with the
  exact binding `um_coldcreep_29` uses for `'Burst'` on this same rig
  (`unarmedSpecialAnim10 = CryptWorm_Skill_Spit.anm`). Slot 10 is precedented: it is the DB-wide
  maximum on a Monster record (6 carriers), and Cold Worm already shipped `unarmedSpecialAnimSpeed10`.
* `giantkarkinos_flightofthekondor` needs `'Kondor'`. Rather than invent an 11th slot
  (unprecedented on any Monster record), the lane **repurposes ref4**: the anim stays
  `CryptWorm_AttGamma.anm` - the worm's own dive animation - and only the ref NAME changes
  `'Dive'` -> `'Kondor'`. A DB-wide scan finds **zero** skills bound to `'Dive'`, so ref4 was dead
  weight. The worm now burrows using its own dive animation.
* `arachne_close_poisoncloud` needs `'Spit'`, which Cold Worm already binds at ref1. The remaining
  new skills declare no animation requirement at all.

**The gate** lives in `coldworm_buffs.verify()` (registry step 4, over the FINAL merged db, after
the whole gate battery) and fails the build loud. **The planted negative test** proves it is not
vacuous:

```
$ py tools/patches/coldworm_buffs.py --negtest
coldworm_buffs _negtest:
  unbound-special-anim plant flagged : True
  dead-skill-reference plant flagged : True
  correctly-bound control is clean   : True ([])
  -> PASS
```

---

## 5. The 3-tier soul + loot triple: already correct, so nothing was rewritten

R-39 asks for a "3-tier soul + loot-triple fix". Ground truth on `main` says the fix already
landed in earlier waves, so this lane **asserts** it and writes nothing:

| tier | record | itemLevel | bitmap | itemSkillLevel | augments | defensiveCold |
|---|---|---|---|---|---|---|
| n | `boss_coldworm50_soul_n.dbr` | 30 | `soul_n_icon.tex` | 2 | 2 / 2 | 18 |
| e | `boss_coldworm50_soul_e.dbr` | 50 | `soul_e_icon.tex` | 4 | 3 / 3 | 30 |
| l | `boss_coldworm50_soul_l.dbr` | 65 | `soul_l_icon.tex` | 6 | 5 / 5 | 42 |

`lootFinger2Item1` is the proper difficulty-indexed `[n, e, l]` triple at
`chanceToEquipFinger2 = 66` (the PLACED_UBER rate, R-42) with `chanceToEquipFinger2Item1 = 100`
and `dropItems = 1`. The grant is the post-b29 `pcsafe\gargantuanyeti_iceblast` clone, and the
per-tier icons follow the b40 convention. Independently corroborated by b78's roster sweep
(775 tier families, **0 flat, 0 wrong-tier-loot**).

`verify()` now re-asserts every one of those facts so a later writer cannot silently regress them.

---

## 6. Roster drop-slot sweep - `tools/sweep_soul_drop_slots.py`

Shipped as a committed, read-only diagnostic. It checks that the four fields a soul drop needs all
agree on one slot (`loot<Slot>Item1`, `chanceToEquip<Slot>` > 0, `chanceToEquip<Slot>Item1` > 0,
`dropItems` == 1) and encodes the two **design** rules so they are not reported as bugs:

1. **Rank gating** - only Hero/Boss/Quest drop souls; the zeroes on Common/Champion carriers of
   inherited soul loot are the build13 yeti fix working (419 records), so they are excluded.
2. **Terminal-form gating** - a multi-form boss drops on its LAST form only. The sweep *follows*
   `actorToSpawnOnDeath` and only reports a gated dropper if no form in the chain pays out. This
   is mechanical, not a hand-maintained waiver list, so a genuinely broken chain still fails.
   Proof the rule is real: `um_tantalus_99` chance 0 -> `um_tantalus_unbound_99` chance 66;
   `um_charon_ferryman_99` chance 0 -> `um_charonform2_ferryman_99`; `um_polisgaoler_99` chance 0
   -> `um_polisgaoler_unbound_99`.

**Result on the b91 arz: 15 findings, 9 waived by a named ruling, 6 unwaived - none of them Cold
Worm, all of them pre-existing.** The unwaived six are a genuinely NEW defect class this sweep
surfaced, and they are **reported, not fixed** (see section 8: fixing them changes placed-content
drop behaviour, which defaults to WILL-VETO).

```
[P0-NO-DROPITEMS] Boss  q_leinth_47.dbr / _49 / _50   (Finger2)
      dropItems=0 explicitly, while 881/888 active soul droppers set it to 1 -
      every equipped item on this record, the soul included, is suppressed on death
[P0-NO-DROPITEMS] Hero  xhero_spinebreaker_42.dbr     (Finger2)
[P2-DROPITEMS-UNSET] Boss  boss_titan_typhon_45.dbr / boss_daemonbull_yaoguai_38.dbr
      dropItems is ABSENT (inherits the template default)
```

The `dropItems` distribution across the 888 ACTIVE soul droppers is what makes this a defect
signal and not a style: **881 set it to 1**, 5 set it to 0, 2 leave it absent. The two ABSENT
records are deliberately a lower severity because the Monster.tpl default is not established here.

Waived, each citing its ruling: the 7 Aphiastas keres records (A4 Aphiastas-zero - note the
records spell the family `um_afaistas` while the soul spells it `aphiastas`), the `um_legion_28*`
stages (b56 terminal-stage-only), `um_astralwing_35_illusion` (an illusion duplicate must not
duplicate its original's loot), the `records\skills\test\test_hero_*` harness records and the
`copy of ...` upstream junk (never placed).

The sweep is **not** wired into the build as a hard gate, precisely because it currently fails on
pre-existing content whose fix is Will's call. Wiring it in is the natural follow-up once he rules.

---

## 7. NOT DONE - the exclamation-point map marker (BLOCKED, honestly reported)

R-39's remaining clause is "the exclamation-marker mechanism extended to all placed ubers". This
lane did **not** deliver it, for two independent reasons:

1. **The referenced mechanism does not exist in this repo.** BACKLOG line 3628 cites
   "exclamation-point map marker per the b63 mechanism", but there is no `docs/reports/b63*`
   (the reports jump b62 -> b64), no commit implementing it, and no marker code in `tools/` or
   `scripts/`. The only `b63` string in the repo is the unrelated workflow id `wf_87586bbf-b63`.
   So there is no mechanism to "extend" - it would have to be designed from scratch.
2. **It is map-side, and map builds are blocked in this checkout.** The marker is not a DB-side
   monster property: a DB-wide scan finds `miniMapEntity` on **72 scenery/structure records and
   0 Monster records**, and the only other marker-ish fields belong to the quest-log UI
   (`records\xpack\quests\questlog ui\*`). Placing a marker therefore means editing level blobs in
   `Levels.arc`, which needs `SVC_SVAERA_ARC` / `SVC_SV_ARC` - unset here, with
   `reference_mods/` empty (BL-b89-DEBT-4 / BL-b90-DEBT-2).

Registered in the BACKLOG DEBT section. R-39 stays **PARTIAL** in the ledger, not IMPLEMENTED.

---

## 8. Scope, proofs, and what needs Will

**Record delta: exactly ONE record.**

```
$ py tools/record_diff.py local/baseline_build47.arz work/.../SoulvizierClassic.arz --summary
  ADDED   : 0
  REMOVED : 0
  MODIFIED: 3
  ~ records\test\boss_coldworm50.dbr                                  (70 field(s))  <- this lane
  ~ records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr  (1 field)      <- b90/R-48, already on main
  ~ records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr    (1 field)      <- b90/R-48, already on main
```

Every one of the 70 fields is in the intended classes: 3 stat, 6 speed, 9 anim-speed, 2 anim-ref,
17 skillName, 15 skillLevel, 3 active-slot, 20 special-attack tuning. Nothing else in the roster
moved.

**Build:** `SVC_RELEASE_DROPS=1 PYTHONHASHSEED=0`, exit 0, full gate battery green (soul-leak /
soul-augment / soul item-skill activation / boss-orb / boss-kit clone-shape / spawn-eligibility /
champion-cap / summons-contract / A7 golden / b77 unlock-alignment / container-loot / B80 formula
tags). arz md5 `461c54f95480f6c331f25ce7ab64c6f4`, 55,424,874 B.

**Determinism:** two independent full DB builds (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`) to
different output paths produced a **byte-identical** arz -
`461c54f95480f6c331f25ce7ab64c6f4` / 55,424,874 B both times.

**Tags:** the module adds none (`coldworm_buffs: modified 1 record(s), 0 tag(s)`), so the Text.arc
surface is unchanged and `validate_tags` has nothing new to check. Cold Worm's name/description
tags (`tagD2Boss004`, `tagSVCSoulColdWorm`) are untouched.

**Module verify (registry step 4, over the final merged db):**

```
coldworm_buffs verify OK: life [42000.0, 54000.0, 66000.0] (3x),
armor_passive [72, 209, 432] (+20%), speed profile applied,
8/8 active skill slots resolve with every required special animation bound,
3-tier soul + loot triple intact @66%
```

### Open, needs Will
1. **The 4 P0 + 2 P2 drop-slot findings above.** Setting `dropItems=1` on Leinth would also
   release her `lenithsveil` unique at 100%, and on Spinebreaker a rare-misc + parchment + potion
   table - real content changes, so they are flagged rather than made.
2. **In-game DEV verify on a fresh character** (TQ bakes item properties at pickup, and the burrow
   is the one cross-rig graft in the kit): does Cold Worm now cast freezing blast / ice blasts /
   the burrow / the poison cloud, and does the dive animation read correctly as a burrow?
3. **The exclamation marker** (section 7): design the mechanism, or drop the clause.
