# b98 - THE ENDLESS HUNT (2026-07-28, branch `feat/endless-hunt`, tag `build60-dev`)

DB-ONLY lane. **NOT DEPLOYED** (five content branches are staged for one merged deploy).
TAG NOTE: briefed as `build59-dev`, but that tag was already claimed by the parallel
`fix/soul-identity` lane (b97 round 2, `e3f7c32`); a tag in use is never reassigned, so this lane
took the next free number.

Ground truth: deployed arz md5 `9f98e3e88bca20f96bacc2fd6bb87b63` (51,098 records),
`Levels.arc` md5 `943d0ab9516d332db79bd7f9fd2d3ffe`, plus the engine's own `Toolset/Templates.arc`.

| artifact | path | md5 |
| --- | --- | --- |
| arz | `.claude/worktrees/endless-hunt/work/SoulvizierClassic/Database/SoulvizierClassic.arz` | `c366b4108be547b4a4acb181d1b0675c` |
| Text (COUPLED) | `.claude/worktrees/endless-hunt/work/text/Text.arc` | `ce4653d30f304a88e837b20e166639fc` |
| Levels / Quests | untouched | n/a |

The pair is COUPLED: the arz references the new `tagSVCwpnRunbreaker`, so shipping the arz without
this Text.arc puts a raw tag string in a player's hands.

---

## 1. What Will asked for, and what shipped

| # | ask | ruling | status |
| --- | --- | --- | --- |
| 1 | his soul does not drop; and the EoAT formula should drop off him like the other two | R-81, R-82 | **DONE** |
| 2 | "yeah lets have the endless pursuit only be on legendary" | R-80 | **DONE** (fixed encounter only - see 6) |
| 3 | give him a spear; make the three champions look like three creatures | R-83 | **DONE for the Hunt**; the Enslaver/Devourer mesh half is NOT done (see 7) |
| 4 | "he doesnt really have any different or unique skills from ... the enslaver of souls" | R-84 | **DONE** |
| 5 | the Enslaver should have "the same black shroud smoke his summoned demons have" | R-85 | **DONE in data**; the in-game black CANNOT be claimed (see 7) |

---

## 2. Item 1 - the drops

**Why the soul did not drop: one field.** `chanceToEquipFinger2 = 25.0` on
`records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr`. Everything else about that drop was
already correct - `lootFinger2Item1` named the right `toxeus_hunt_soul_{n,e,l}` triple,
`chanceToEquipFinger2Item1` was already 100, `dropItems` was already 1, and all three soul records
existed with their name/description tags and icon. 25% means three kills in four pay nothing, which
is exactly what Will experienced.

Fixed by extending the R-48 owner module `tools/patches/toxeus_souls_100.py` from two targets to
three. Its `apply()` still proves roster-wide that ONLY the named records moved (now 3 of 3,629
creature records), and its `verify()` re-asserts 100 on the FINAL merged arz. Holds under
`SVC_RELEASE_DROPS=1`, which is what ships - it does not lean on `_force_100_pct_soul_drops`, the
testing-only forcer that never runs in a release build. `tools/verify_soul_drop_rates.py`'s waiver
for him moves 25.0 -> 100.0, and the R-80 endless variant gets a matching waiver.

**The Rite of the Undivided (R-82).** He had NO `Misc4` slot at all. He now mirrors the ENSLAVER
exactly: `chanceToEquipMisc4=100`, `chanceToEquipMisc4Item1=100`,
`lootMisc4Item1 = svc_rite_guaranteed` on all three tiers. The Enslaver's simple FixedWeight form
was used rather than the Devourer's master table, because the Hunt has no rant scroll to
co-schedule.

**The Legendary gate did not move - it was already in the right place.** `svc_toxeus_eoat_formula`
names `toxeus_soul_l` + `enslaver_soul_l` + `blood_toxeus_soul_l` by exact path, so the recipe
cannot be completed with normal- or epic-tier souls. R-8's "formula demands LEGENDARY tier" is
correctly wired in the shipped data and needed no change. Because the formula ITEM can now drop on
Normal and Epic, that recipe gate became load-bearing, so `toxeus_hunt_encounter.verify()` now
ASSERTS all three reagents stay `_l` records and fails the build otherwise.

---

## 3. Item 2 - the endless pursuit

**The mechanism, proven twice.** Leash is not a Monster field: all 4,600 Monster records carry zero
leash/aggro/chase/pursuit field. It lives on the CONTROLLER, and his
`controller_shadowstalker01_hidden` reads `MaxPursuitDistance=60` / `PursuitTime=20000` /
`RoamBehavior=Roam`. That is "you can kite him back and forth from where he spawns", field for
field.

Per-difficulty pursuit is **not expressible on one record**:
- EMPIRICAL: across all 504 controller-class records, `MaxPursuitDistance` and `PursuitTime` are
  array-valued ZERO times. The only controller field ever array-valued anywhere is `LeadChance`
  (112 carriers) - which proves controllers CAN carry the [normal,epic,legendary] triple and that
  these two do not.
- AUTHORITATIVE: the engine's own `Toolset/Templates.arc` declares both `class="variable"` in
  `templates/controllermonster.tpl`, while `LeadChance` is `class="array"`. `templates/monster.tpl`
  declares `controller` `class="variable"` too - one monster, one controller, all three difficulties.

A Legendary-gated buff or aura cannot do it either: skills move STATS, they cannot write controller
fields. (His `globalproperties_{normal,epic,legendary}01` slots ARE a real per-difficulty hook, but
they are `Skill_Passive` STAT records - they can make him tougher on Legendary, not make him follow
you.)

So it ships as a second monster record selected by the proxy's own `poolLegendary1` slot, which is a
shipped base-game pattern (29 proxies already resolve to different monsters per difficulty;
`ag_demon_djinnsprite_01t_ambush` is the exact ambush-vs-normal shape).

| record | what it is |
| --- | --- |
| `controllers\monster\controller_toxeus_hunt_endless.dbr` | a CLONE of his own ambush controller, overridden to MaxPursuitDistance 1000 / PursuitTime 100000 / NeverRoam / MinTimeBeforeRoam 0 / MaxTimeBeforeRoam 0 / ForgiveRate 0.2 |
| `creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr` | the Endless Hunt with EXACTLY ONE field changed: `controller` |
| `drxmap\proxy\pools\q_toxeus_hunt_lone_endless.dbr` | single-member Legendary pool |

Every value has a named shipped precedent: 1000 is `controller_aktaios` (the DB's highest monster
value), 100000 has 21 carriers including `controller_hydra` / `controller_terracotta` /
`controller_typhonminion`, `NeverRoam` has 107 carriers, ForgiveRate 0.2 is Aktaios. Aktaios's
`FleeWhenEnemyClose` was deliberately NOT copied - `FleeBehavior` stays `NeverFlee`, because a
hunter that flees is nonsense, and the gate fails the build if it changes.

**The shared donor was CLONED, never edited.** `controller_shadowstalker01_hidden` is used by 15
monsters, including the Enslaver's own marauders. Editing it in place would have made every
shadowstalker ambusher in the game relentless. The gate independently re-asserts the donor still
reads 60 / 20000.

**The doubled record cannot drift.** The variant is generated at build time as a clone-then-override
of the base, and `toxeus_hunt_endless.verify()` asserts base and variant differ in EXACTLY the
`controller` field and nothing else. Registry ORDER is what makes that hold: the module is last
among content modules, after every writer of the base record (`toxeus_hunt_encounter`,
`toxeus_champion_kits`, `boss_skill_fix`, `toxeus_souls_100` AND `uber_quest_markers`), so the clone
inherits the 100% soul rate and the `DisplayAsQuestItem` marker by construction. Verified in the
shipped arz: the variant carries `chanceToEquipFinger2 = 100.0` and `DisplayAsQuestItem = 1`.

**The gate the ruling forced us to invert.** The old module's `verify()` failed the build if `pool1`
or `poolEpic1` was non-empty ("Legendary-only gate broken, Normal would spawn him"). Implementing
Will's ruling reds that gate by construction, so it was flipped in the same commit: it now fails if
any of `pool1` / `poolEpic1` / `poolLegendary1` is EMPTY.

---

## 4. Item 3 - the spear, and the animation proof

**Runbreaker**, a bespoke 3-tier signature weapon following the Devourer's Crimson Verdict /
Veinrender pattern exactly: `svc_{n,e,l}_runbreaker` + `runbreaker_guaranteed_{n,e,l}` FixedWeight
tables wired to `lootRightHandItem1` at 100%, so he both WIELDS and DROPS it. He previously carried
a random one-hander with no signature at all.

**The rig was proven before the item shipped.** His record ships
`spearAttackIdleAnim`, `spearBuffSelfAnim1`, `spearBuffOtherAnim1`, `spearSpellAttackAnim` and
`spearWalkAnim` - and is MISSING `spearAttackAnim1/2/3`, `spearRunAnim`, `spearDieAnim1` and
`spearStunAnim`. A spear without those means he walks with it and never swings.

The ShadowStalker rig ships no spear animation of its own (13 `.anm` files, 0 spear), so the attack
poses must be borrowed. Cross-rig spear animation is the base game's NORM, not an exception: 672
shipped records play a spear attack anim authored for a different rig, versus 247 same-rig. And this
mod already does it on the Toxeus family's own skeleton rig -
`records\skills\soulskills\pets\boneash_1.dbr` carries a complete Maenad-spear block on a
RevenantFire mesh.

The graft is deliberately minimal - only what the rig genuinely lacks is borrowed:

| slot | source | borrowed? |
| --- | --- | --- |
| `spearAttackAnim1/2/3` | `Maenad_Spear_Att{Alpha,Beta,Gamma}` | YES (boneash_1 precedent) |
| `spearRunAnim` | this record's own `sHandedRunAnim` | no |
| `spearDieAnim1` | this record's own `sHandedDieAnim1` | no |
| `spearStunAnim` | this record's own `sHandedStunAnim` | no |

The three self-sourced slots are read from the record at build time rather than hardcoded, so they
cannot desync from it. That leaves exactly THREE unproven-by-eye animations instead of eight, and
`verify()` asserts each of the three is referenced by at least one OTHER shipped record - a
provenance proof, not a guess that the file exists.

**Gate SPEAR-ANIM-1 (new content class ships its gate):** if a monster is guaranteed a
`WeaponHunting_Spear` in its RightHand slot, its rig must carry `spearAttackAnim1..3` plus run, walk,
idle, die and stun poses, each naming a non-empty `.anm`. Planted negative test included.

**A fix-upstream defect caught in passing (BL-103).** The supra spear donor still carries the
build30-F3 INVISIBLE-WEAPON DRX mesh at registry time - F3 (`_fix_wave30_render_and_refs`) repoints
it in `run_registry_gates`, AFTER every registry module, and it repoints exactly two records BY NAME.
A naive clone would therefore have shipped an invisible spear. Runbreaker sets the F3-corrected base
rig (`Items\EquipmentWeapon\Spear\Default\RSpear14B.msh`) explicitly, drops the DRX-only skin
(`baseTexture` + the leftover `bumpTexture` companion `fx_dangling_cleanup` strips from the donor),
and `verify()` asserts each tier's mesh equals the donor's FINAL post-F3 mesh so the two can never
diverge. This was found by the contract suite, not by inspection, and a fifth negative-test plant now
guards it.

### Player-surface checklist (R-83)
| surface | state |
| --- | --- |
| name | `tagSVCwpnRunbreaker` = "Runbreaker", one tag across all 3 tiers (the Veinrender convention). `validate_tags` PASS. |
| icon | shares the supra spear's `wep_spearUIBITMAP.tex` - the same convention Veinrender uses (it shares the base melinoe icon). A bespoke icon is registered as debt, not silently deferred. |
| mesh | base `RSpear14B.msh`, the Ares' Wrath legendary spear rig; resolves in the shipped arcs. |
| tiers | Rare 40/35, Epic 68/63, Legendary 95/90 - identical to Veinrender's ladder. |
| speed | `CharacterAttackSpeedAverage` + 0.25 (both inside the shipped spear envelope) to keep him the FAST champion; one-line WILL-VETO. |
| drop | guaranteed, RightHand @100%, the unique-1H alternative slot zeroed. |
| in-game look | **NOT CONFIRMED** - BL-b98-DEBT-1. |

**Range bands** widened for a two-handed reach weapon plus a long-range lance: short 0-4 / medium
4-8 / long 8-15 becomes short 0-5 / medium 5-12 / long 12-22.

---

## 5. Item 4 - a kit that is his own

Will's statement was literally true. Nine of his twelve skill slots were the SAME SKILL RECORD as
the Enslaver's (flashpowder, toxeus_bladestorm, netherstrike, lifedrain, character_speedall,
boss_conversionimmunity, hero_scaling, toxeus_passiveproperties, armor_passive); his only three
non-shared slots are the `globalproperties_{normal,epic,legendary}01` per-difficulty STAT hooks. He
had ZERO unique active abilities, and slot 2 was even the same skill at the same slot index.

The three cast slots that overlapped the Enslaver become his own, built from what he IS - a demon
that does not stop:

| slot | was | now | reads as |
| --- | --- | --- | --- |
| `specialAttack` @45% | flashpowder | **Quarry's Mark** (`svc_hunt_quarrysmark` + `_buff`, from Study Prey) - heavy run-speed slow + defensive-ability shred + bleed, MediumRange | he has your scent, and you cannot outrun him |
| `specialAttack3` @30% | netherstrike | **The Long Reach** (`svc_hunt_longreach`, from the DRX **stalker**-namespace shadow blast) - cold + pierce at LongRange | distance is not safety |
| `specialAttack4` @30% | lifedrain | **Run Them Down** (`svc_hunt_rundown`) - a close-range spear sweep, heavy bleed, ShortRange | when he closes, it ends |

`toxeus_bladestorm` - the Toxeus family signature verb - and every passive are KEPT. This edits three
slots; it never strips his kit. Each replacement reuses the retired skill's own `skillName` slot, so
the kit stays 12 slots with nothing orphaned at level 0. The retired skill RECORDS are shared and
were not touched.

**Castability (the Ephialtes lesson).** He binds ZERO `unarmedSpecialAnimRef` slots - and so do the
Enslaver and the Devourer. Every new skill therefore declares NO `skillSpecialAnimationName`, which
is the same law `toxeus_champion_kits` already ships for these champions. Gated fail-loud.

**Reported, not silently claimed:** the skill replaced at `specialAttack3`, `netherstrike`, declares
`skillSpecialAnimationName='LethalStrike'` which he does not bind. That slot was very likely dead
already, so this is a repair as well as a differentiation.

**Also gated:** a SAMENESS check that fails the build if every one of his cast slots is an Enslaver
cast slot again.

**Will's other observation is confirmed by the data:** "it wasnt a skeleton, it was a demon" -
`characterRacialProfile = Demon`. That is a data fact.

**A correction to the design brief, deliberately not actioned.** The brief called
`distressCallGroup='Skeleton'` on a Demon-race boss a clone leftover to fix. Ground truth says
otherwise: all 28 shipped ShadowStalker-mesh monsters are race=Demon AND group `Skeleton`, including
the Enslaver's own marauders - it is the base game's convention for this rig. There is also no
`Demon` group anywhere in the DB (19 groups exist; Demon is not one), so "fixing" it would invent a
group of one member and cut him out of the shadowstalker distress network. Left alone, census
recorded.

---

## 6. The "Hades-only" myth, and why Will met him in Rhodes on Epic

He has TWO spawn mechanisms and only ONE was ever difficulty-gated.

**(A) The roaming sweep - never gated, never Hades-confined.** He is a `nameN` member of 346
ProxyPools, 344 of them under `records\xpack\proxieshades\pools\`. 540 proxies reference those pools:

| area | proxies |
| --- | --- |
| area001 Rhodes | 70 |
| area002 Medea's Grove | 76 |
| area003 Epirus | 55 |
| area004 Styx | 78 |
| area005 Plains of Judgement | 79 |
| area006 Tower of Judgement | 49 |
| area007 Elysian Fields | 82 |
| area008 Hades Palace | 49 |

365 of those 540 define ONLY `poolN` - which resolves on all three difficulties - 174 define
`poolN` + `poolEpicN`, and ZERO define `poolLegendaryN`.

**The whole myth came from one comment.** `toxeus_suite.py`'s
`_LS_ALLOW_PREFIX = ('records\\xpack\\proxieshades',)` was annotated "Hades trash pools ONLY".
`records\xpack\proxieshades\` is the WHOLE Immortal Throne proxy namespace, and the base game filed
Rhodes inside it as area001. Every downstream claim ("narrowed to Hades", R-16's "Hades-confined",
BACKLOG's "hades-only sweep") inherited that error. Corrected in place under the retirement protocol
- wording only; the prefix itself is CORRECT and unchanged, and no record was renamed or deleted.

**Why Normal never showed him: rarity, not a gate.** His slot carries weight 1 against pool totals
of 36,001 to 660,001 (the natives are x600-scaled), so p_slot ranges from 1/36,001 to 1/660,001,
median about 1 in 66,667, with `limitN=1` capping him at one per pool per trigger. Meeting him once
on Epic and never on Normal is exactly what that distribution predicts. **He was eligible on Normal
the whole time** - the Rhodes Normal difficulty budget is about 33 x 4.5 = 148 at one player and he
costs 40.

**A shipped RCA that would mislead the next lane.** R-3/b91 rests part of its root cause on reading
`limit_area002`'s N[23-26] window as EXCLUDING charLevel [40,68,100]. `difficultyLimitsFile` records
contain only `minPlayerLevelEquation{Normal,Epic,Legendary}` and `maxPlayerLevelEquation{...}` - they
clamp the PLAYER level fed into `difficultyEquation`, they are not a monster-charLevel filter. Do not
reuse the b91 level-band reasoning for this monster; recommend a ledger reconciliation on R-3.

**(B) The fixed proxy** `records\drxmap\proxy\q_toxeus_hunt_lone.dbr` in
`hadespalace_floor04_04.lvl` WAS genuinely Legendary-only (`pool1=''`, `weight1=0`, `poolEpic1`
absent). R-80 removes that gate: pool1, poolEpic1 and poolLegendary1 now all name his pool.
`poolEpic1` is set EXPLICITLY rather than left to fall back on `pool1`, because "poolEpic1 absent" is
the Hydra gate idiom and reads as deliberate gating intent to the next maintainer. The MAP BYTES ARE
UNCHANGED - the placement was always difficulty-agnostic; only the DB pool slots decided.

---

## 7. Item 5 - the Enslaver's shroud, and what could NOT be claimed

**He already had the FX.** `um_toxeus_enslaver_99` carries
`charFxPakRunningNames = drxshadowcloakrunning_fx_pak` - the SAME pak, resolving to the SAME
EffectEntity (`DRXeffects\shadowcloakrunning.pfx`, boneList `Bone_R_Weapon;Bone_L_Weapon`), that his
marauders carry. Only 14 records in the whole 51,098-record DB carry that field and he is one of
them. So the ask was never "give him the FX"; it was "make the FX he already has actually show".

- **ELIMINATED from the asset bytes:** bone mismatch. `Bone_R_Weapon` and `Bone_L_Weapon` both exist
  on RevenantPoison.msh exactly as on ShadowStalker.msh. The first hypothesis was wrong and is
  reported as wrong rather than shipped. (Worth keeping: the WAIST attach point is named "Smoke02" on
  ShadowStalker but "Waist" on RevenantPoison, so a body-shroud FX targeting "Smoke02" would work on
  the marauders and silently do nothing on him.)
- **SURVIVING CAUSE:** `charFxPakRunningNames` renders ONLY while RUNNING. The marauders are melee
  chasers that run constantly; he is a caster (spell-cast speed 2.0, full armour, run 1.5) who stands
  and casts.

**The fix, on a shipped in-house pattern.** `charFxPakSelfNames` is the persistent channel and is a
SKILL field, never a Monster field (184 carriers, zero Monster-class), so the shipped way to put a
persistent FX on a monster's body is a self-buff SKILL - exactly what R-7 did for the Devourer.
`svc_enslaver_shroud` is a `Skill_BuffSelfToggled` cloned from `empusamerc_enchantment`, the ONE
zero-payload self-buff toggle in that namespace, so it carries NO combat payload at all; the donor's
purple weapon tint is zeroed to the inert (0,0,0) NO-TINT default (the b83 tint model: a zero channel
is OFF, not black, so it cannot recolour his weapon). His controller carries
`BuffSelfBehavior='WhenEnemyIsSeen'`, so it fires the moment the fight starts.

**No skill was dropped.** The design brief assumed all 12 of his slots were full and one would have
to be sacrificed under R-26's spirit. Ground truth: he uses `skillName1..18` and the Monster template
reaches at least 23 (`um_mnemophage_99` uses `skillName23`), so **slot 19 was free all along**. His
`charFxPakRunningNames` is kept, so he smokes harder when he moves and still matches his marauders.

**Colour discipline.** The only in-game-CONFIRMED black in this area is the shadowcloak smoke Will
has SEEN on the marauders and called "the black shroud smoke". That is the only asset used, and the
gate refuses any other. `343_dark_smoke` (the Devourer's shipped black poison particle) is explicitly
NOT confirmed - R-10 calls it "the green-rendering 343_dark_smoke" and `black_poison.py` flags it -
and `hades2_shadowcloud` is not confirmed either.

### ⚠️ THIS LANE DOES NOT CLAIM HE READS BLACK IN GAME
b92 proved from ASSET BYTES that `Creatures\Monster\Skeleton\RevenantPoison.msh` - the mesh he wears
in the DEPLOYED arz - ends with `CreateEntity { attach = "Waist"; entity = "...RevenantPoison_FX.dbr" }`
resolving to `Effects\MonsterFX\Buffs\RevenantPoison.pfx`, whose colour keyframes decode to
R 0.534 / G 1.000 / B 0.591 = GREEN, compiled into the mesh file and invisible to any `.arz` scan.
Black hand-smoke over a green waist aura will not read black.

That work belongs to the green-diff lane (b92, commit `60d7789`, reachable only from tag
`build53-dev`, **NOT deployed** - the deployed arz still reads `RevenantPoison.msh` on both
champions) and turns on Will's answer about giving each champion a DIFFERENT aura-free mesh. This
lane never touched that worktree. Registered as BL-b98-DEBT-2.

**Consequence for "make the three champions look different" (item 3, second half):** NOT DONE. The
Hunt is now clearly separated - ShadowStalker rig, cold/spectral iceheart skin, a two-handed spear
silhouette, widened reach and a wholly different kit. But the Enslaver and the Devourer still share
`RevenantPoison.msh`, differing only by texture and scale. Splitting them is the mesh decision above.

---

## 8. Verification

| gate | result |
| --- | --- |
| DB build (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`) | **PASS**, exit 0 |
| patches-registry selfcheck | **OK**, 39 modules |
| every module `verify()` hook | **green** (30 hooks) |
| `validate_tags` | **PASS** - 358 mod-owned tags all resolve, incl. `tagSVCwpnRunbreaker` |
| `verify_soul_drop_rates` | **PASS**, incl. its own planted-regression negative test |
| contract suite (5 domains) | **PASS - 0 P0 / 0 P1**, byte-for-byte the same verdict as the `main` baseline under identical inputs (both 0 P0 / 0 P1 / 4,759 P2) |
| record diff vs a freshly built `main` (a0276ab) baseline | 15 ADDED / 0 REMOVED / 4 MODIFIED - **intended only** |
| planted negative tests | **14/14 plants caught** across 3 new gates |

### Contract-suite note for future lanes
Run it with `--resource-arc-dir` pointing at a Resources dir that actually holds the asset arcs, and
`--upstream-dir` at a populated upstream cache. Without them the suite reports **102 P0 / ~460 P1 on
`main` ITSELF** - pure environment artifacts (meshes "unresolvable" because no arcs were loaded, and
severity demotion because the provenance source could not load). Both numbers were reproduced on the
baseline before and after, which is how they were identified as environmental rather than a
regression. The one real finding the suite surfaced (the invisible-weapon spear mesh) was fixed, not
waived.

### Record diff detail
ADDED (15): `controller_toxeus_hunt_endless`, `um_toxeus_hunt_l_99`, `q_toxeus_hunt_lone_endless`,
`svc_{n,e,l}_runbreaker`, `runbreaker_guaranteed_{n,e,l}`, `svc_hunt_quarrysmark`,
`svc_hunt_quarrysmark_buff`, `svc_hunt_longreach`, `svc_hunt_rundown`, `svc_enslaver_shroud`,
`svc_enslaver_shroud_charfxpak`.
MODIFIED (4): `um_toxeus_hunt_99` (30 fields - soul rate, Misc4 Rite, spear loot + anims, range
bands, 3 kit slots + 3 cast slots), `um_toxeus_enslaver_99` (2 - the shroud in free slot 19),
`q_toxeus_hunt_lone` proxy (5 - the pool slots), its pool (1 - FileDescription).

### New gates shipped with the new content classes
| gate | what it forbids | negative test |
| --- | --- | --- |
| `toxeus_hunt_encounter.verify` | the Legendary-only gate coming back; a spear with no swing animation; a kit skill needing an unbindable special animation; the EoAT recipe dropping its LEGENDARY reagents; the invisible-weapon DRX mesh | `--negtest` 5/5 |
| `toxeus_hunt_endless.verify` | base/variant drift beyond `controller`; editing the 15-monster shared controller in place; Legendary losing the endless variant; Normal silently getting it; the hunter learning to flee | `--negtest` 5/5 |
| `enslaver_shroud.verify` | an unconfirmed colour asset; the shroud growing a combat payload; the donor's purple tint returning; the shroud falling out of his kit; his running FX being taken away; bone names used where attach-point names belong | `--negtest` 6/6 |

---

## 9. NOT DONE (the honest list)

1. **The Enslaver/Devourer mesh split** (item 3, second half). They still share `RevenantPoison.msh`.
   Blocked on the b92 mesh-green work in another lane plus Will's answer about a different aura-free
   mesh per champion. BL-b98-DEBT-2.
2. **"The Enslaver reads black in game"** - cannot be claimed while his mesh emits a green waist
   aura. The data change shipped; the visual claim did not. BL-b98-DEBT-2.
3. **Runbreaker's swing has not been seen.** Maenad-spear-on-ShadowStalker has no shipped instance.
   BL-b98-DEBT-1.
4. **The ROAMING Hunt is still kiteable on Legendary.** ProxyPool has no per-difficulty member list
   and the 345 pools are native and shared. Only the fixed encounter is endless. Structural, reported
   not hidden. BL-b98-DEBT-9.
5. **The roam RATE is untouched** (about 1 in 67,000 per roll). A rate change is WILL-VETO by the R-18
   precedent. BL-b98-DEBT-5.
6. **His empty drop slots are untouched.** Finger1 / Misc1 / Misc2 / Misc3 are wired at 0%, so his
   ring, potions, relic and amulet can never drop. WILL-VETO by the R-39 precedent. BL-b98-DEBT-6.
7. **The EoAT recipe reagents are unchanged.** Whether his soul should become one is Will's call, and
   a 4th slot must not be promised before checking the template. BL-b98-DEBT-4.
8. **Normal-difficulty balance is untouched.** BL-b98-DEBT-8.
9. **No in-game QA of any kind** - no deploy, no Steam, no launch. That is the merged-deploy lane's
   job.

## 10. Questions for Will (shortest form)

1. Endless pursuit at 1000 units / 100 seconds also means he cannot be outrun to a town portal on
   Legendary. Intended?
2. Should the Endless Hunt's legendary soul become a reagent of the End of All Things formula?
3. The roam is about 1 in 67,000 per spawn roll. Target: once a playthrough, once per act, or leave
   him a rumour?
4. Open his empty drop slots (ring / potions / relic / amulet) to Enslaver-comparable rates?
5. Spear: keep him FAST (shipped) or make him a slow, heavy reach-hunter?
6. Have you seen the Devourer's black poison read BLACK in game? Your answer decides whether
   `343_dark_smoke` can be reused anywhere - and whether the Devourer needs a fix.
7. Give each champion a DIFFERENT aura-free mesh, so removing the b92 mesh green also makes the three
   look less alike?
8. Normal-difficulty tuning: he is charLevel 40 / 16,000 HP / run 1.8 in a band that clamps the
   player to 29-33. Scale him down, or is a brutal ambush the point?
