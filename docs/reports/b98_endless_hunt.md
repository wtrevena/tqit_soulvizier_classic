# b98 - THE ENDLESS HUNT (2026-07-28, branch `feat/endless-hunt`, ROUND 2, tag `build61-dev`)

DB-ONLY lane. **NOT DEPLOYED** (five content branches are staged for one merged deploy).
TAG NOTE: briefed as `build59-dev`, but that tag was already claimed by the parallel
`fix/soul-identity` lane (b97 round 2, `e3f7c32`); a tag in use is never reassigned, so round 1 took
`build60-dev` and this round-2 commit takes `build61-dev`.

Ground truth: deployed arz md5 `9f98e3e88bca20f96bacc2fd6bb87b63` (51,098 records),
`Levels.arc` md5 `943d0ab9516d332db79bd7f9fd2d3ffe`, plus the engine's own `Toolset/Templates.arc`.
Both re-hashed at the end of round 2 and **unchanged** (no deploy).

| artifact | path | md5 |
| --- | --- | --- |
| arz | `.claude/worktrees/endless-hunt/work/SoulvizierClassic/Database/SoulvizierClassic.arz` | `6be6fb0a5507ca4f6988405e7a64add8` (51,104 records) |
| Text (COUPLED) | `.claude/worktrees/endless-hunt/work/text/Text.arc` | `c0f22186550484b932e26dacc12c6a9a` |
| Levels / Quests | untouched | n/a |

(Round 1 shipped arz `c366b4108be547b4a4acb181d1b0675c` / Text `ce4653d30f304a88e837b20e166639fc`;
both are SUPERSEDED by the pair above.)

The pair is COUPLED: the arz references the new `tagSVCwpnRunbreaker` **and the seven new
`tagSVCHunt*` skill tags**, so shipping the arz without this Text.arc puts raw tag strings in a
player's hands.

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
- EMPIRICAL: across every controller record in the DB, `MaxPursuitDistance` and `PursuitTime` are
  array-valued ZERO times (the COUNT of controller records varies with the denominator, see 11.5;
  ZERO does not). The only controller field ever array-valued anywhere is `LeadChance` - which proves
  controllers CAN carry the [normal,epic,legendary] triple and that these two do not.
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
value), 100000 is carried by `controller_hydra` / `controller_terracotta` / `controller_typhonminion`
among others, `NeverRoam` is widely carried, ForgiveRate 0.2 is Aktaios. (Round 1 quoted carrier
COUNTS of 21 / 107 / 504 here; those numbers depend on the denominator and are corrected in 11.5.
The named per-record precedents above are what is load-bearing, and they are unchanged.) Aktaios's
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

**Castability (the Ephialtes lesson).** Every new skill declares NO `skillSpecialAnimationName`,
the same law `toxeus_champion_kits` already ships for these champions. Gated fail-loud.
⚠️ **Round 1 got the rest of this paragraph wrong and it cost him 40% of his cast budget. See
section 11.**

**Reported, not silently claimed:** the skill replaced at `specialAttack3`, `netherstrike`, declares
`skillSpecialAnimationName='LethalStrike'` which he does not bind. That slot was very likely dead
already, so this is a repair as well as a differentiation.

**Also gated:** a SAMENESS check that fails the build if every one of his cast slots is an Enslaver
cast slot again.

**His soul grants his own mark (round 2).** `toxeus_hunt_soul_{n,e,l}` used to grant
`soulskills\toxeus_flashpowder.dbr` - the skill this section retires. All three tiers now grant
`svc_hunt_quarrysmark` at itemSkillLevel 1/2/3. See section 11.

**Will's other observation is confirmed by the data:** "it wasnt a skeleton, it was a demon" -
`characterRacialProfile = Demon`. That is a data fact.

**A correction to the design brief, deliberately not actioned.** The brief called
`distressCallGroup='Skeleton'` on a Demon-race boss a clone leftover to fix. Ground truth says
otherwise: it is the base game's convention for this rig, including on the Enslaver's own marauders.
Census, re-run in round 2 with the method stated so it reproduces (records whose `mesh` contains
'shadowstalker.msh' AND `Class`=='Monster', deployed arz): **30 records, ALL 30 race=Demon, 26 group
`Skeleton`, 4 group `Jackalman`** - and those 4 wear a different mesh path,
`Creatures\Monster\jackalman\shadowstalker.msh`. (Round 1 said "all 28 ... race=Demon AND group
Skeleton"; the race half was right, the group half was not exactly right.) There is no `Demon` group
anywhere in the DB (19 monster distress groups exist; Demon is not one), so "fixing" it would invent
a group of one member and cut him out of the shadowstalker distress network. Left alone, corrected
census recorded.

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

**All figures below are the ROUND 2 re-run** (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`, same inputs as
round 1 and as the `main` baseline).

| gate | result |
| --- | --- |
| DB build (`PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`) | **PASS**, exit 0 |
| patches-registry selfcheck | **OK**, 39 modules, order hash `14c27b6e835f` |
| every module `verify()` hook | **green** (30 hooks), incl. the rebuilt `toxeus_hunt_encounter.verify` |
| `validate_tags` | **PASS** - 365 mod-owned tags all resolve (was 358; +7 `tagSVCHunt*`), incl. `tagSVCwpnRunbreaker` |
| `verify_soul_drop_rates` | **PASS**, incl. its own planted-regression negative test |
| contract suite (5 domains) | **PASS - 0 P0 / 0 P1**, byte-for-byte the same verdict as the `main` baseline under identical inputs (both 0 P0 / 0 P1 / 4,759 P2) |
| record diff vs a freshly built `main` (a0276ab) baseline | ROUND 2: see the table below - **intended only** |
| planted negative tests | ROUND 2: **26/26 plants caught** across 3 new gates (was 16/16) |

### Contract-suite note for future lanes
Run it with `--resource-arc-dir` pointing at a Resources dir that actually holds the asset arcs, and
`--upstream-dir` at a populated upstream cache. Without them the suite reports **102 P0 / ~460 P1 on
`main` ITSELF** - pure environment artifacts (meshes "unresolvable" because no arcs were loaded, and
severity demotion because the provenance source could not load). Both numbers were reproduced on the
baseline before and after, which is how they were identified as environmental rather than a
regression. The one real finding the suite surfaced (the invisible-weapon spear mesh) was fixed, not
waived.

### Record diff detail (ROUND 2: 15 ADDED / 0 REMOVED / 7 MODIFIED, intended only)
ADDED (15, unchanged from round 1): `controller_toxeus_hunt_endless`, `um_toxeus_hunt_l_99`,
`q_toxeus_hunt_lone_endless`, `svc_{n,e,l}_runbreaker`, `runbreaker_guaranteed_{n,e,l}`,
`svc_hunt_quarrysmark`, `svc_hunt_quarrysmark_buff`, `svc_hunt_longreach`, `svc_hunt_rundown`,
`svc_enslaver_shroud`, `svc_enslaver_shroud_charfxpak`.

| modified record | fields | what |
| --- | --- | --- |
| `um_toxeus_hunt_99` | 35 | soul rate, Misc4 Rite, spear loot + the full spear anim block, range bands, 3 kit slots + 3 cast slots, **+ round 2:** `spearSpawnAnim`, `spear/unarmedSpecialAnimRef1` + `spear/unarmedSpecialAnim1` |
| `um_toxeus_enslaver_99` | 2 | the shroud in FREE slot 19 (`skillName19` / `skillLevel19`) |
| `q_toxeus_hunt_lone` (proxy) | 5 | the pool slots (gate off, Legendary repointed at the endless pool) |
| `q_toxeus_hunt_lone` (pool) | 1 | FileDescription |
| `toxeus_hunt_soul_n` | 2 | **round 2:** `itemSkillName` + `itemSkillLevel` |
| `toxeus_hunt_soul_e` | 2 | **round 2:** `itemSkillName` + `itemSkillLevel` |
| `toxeus_hunt_soul_l` | 2 | **round 2:** `itemSkillName` + `itemSkillLevel` |

No dtype flips, no collateral, nothing outside the Toxeus arc.

### Contract suite, per contract, vs the `main` (a0276ab) baseline
Every one of the 11 reporting contracts returns an **identical count**, so the pre-existing P1 total
(zero) and the P2 total (4,759) are provably unchanged by this lane:
`C-RES-ASSET-1` 1586, `C-RES-DBR-1` 2630, `C-RES-TAG-1` 332, `C-RES-TAGDEAD-1` 35, `C-RES-TPL-1` 57,
`MAP-NAV-4` 2, `MAP-PORTAL-1` 1, `MAP-PORTAL-3` 2, `MONSTER-MESH` 2, `MONSTER-SKILLS-LOOT` 110,
`QST-TAG-PLACEHOLDER` 2. All P2.

### Independent re-verification of the BUILT arz (not the module's own verify)
Read back out of the finished `.arz`, not asserted by the code that wrote it: bladestorm's `AoE360`
is bound with a real `.anm` on both the `spear` and `unarmed` rows and is the ONLY populated cast
slot that needs a special animation; all three souls grant `svc_hunt_quarrysmark` at 1/2/3 against
`skillMaxLevel` 3; all 13 stripped donor payload fields read ABSENT; all 8 skill display/description
tags read the mod-authored `tagSVCHunt*` values; the Legendary variant differs from the base in
**exactly** `controller` and inherits the new bindings and the 100% soul rate; and the built
`Text.arc` carries all 7 new tags with no "flash-burst" string anywhere.

### New gates shipped with the new content classes
| gate | what it forbids | negative test |
| --- | --- | --- |
| `toxeus_hunt_encounter.verify` | the Legendary-only gate coming back; a spear with no swing animation (now including the emerge pose); **ANY** populated cast slot whose special animation the caster cannot bind, on **any** row he can read, with the row derived from the weapon he is guaranteed; the EoAT recipe dropping its LEGENDARY reagents; the invisible-weapon DRX mesh; his soul granting the retired flashpowder, or granting a level its skill does not have; an inherited donor payload surviving a clone; a new skill still reading as its donor; the soul description still advertising the flash-burst; the AI being told to cast the lance beyond its own reach | `--negtest` **15/15** |
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
10. **The two monster-only new actives still carry their donors' icons and sounds** (round 2). Neither
    has a UI surface on a monster and no claim is made about how they sound, but Life Drain's cast
    and hit paks are the wrong audio identity for a cold spectral spear. BL-b98-DEBT-10.
11. **The AoE360 whirl pose has not been seen either** (round 2). Binding it makes bladestorm FIRE,
    which is the law it was breaking; whether a PC-rig whirl reads right on the ShadowStalker rig is
    the same cross-rig question as the swing poses. Folded into BL-b98-DEBT-1.

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

---

## 11. ROUND 2 - the adversarial vet's findings, and what changed

Round 1 (`2af3104`, tag `build60-dev`) was vetted **NO-GO on two issues**; the vet independently
rebuilt both this branch and `main`, re-ran all three negative-test suites, and upheld everything
else. Nothing from round 1 was reversed. This section is the delta.

### 11.1 BLOCKER - an uncastable skill in a rewritten cast slot, claimed as working

**What was wrong.** `toxeus_bladestorm` sits at `specialAttack2` @40% and declares
`skillSpecialAnimationName='AoE360'`. `um_toxeus_hunt_99` has **no `charAnimationTableName`** and
bound **zero `*SpecialAnimRef`** on any row, so under this repo's disassembly-proven hard law
(Game.dll `SkillManager::StartSkill` aborts a cast whose special animation the caster's table cannot
start; `docs/BACKLOG.md` B-SOUL-PROC-2, `docs/MASTERY_AUDIT_2026-07-09.md`, and the b91 coldworm
monster-side gate) that cast has never been able to fire, not in the shipped data and not after
round 1, whose report asserted the opposite ("toxeus_bladestorm ... and every passive are KEPT").

**The premise round 1 reasoned from was inverted.** Round 1 wrote that the Enslaver and the Devourer
"bind ZERO `unarmedSpecialAnimRef` slots" too. They do not need to: both carry

```
charAnimationTableName = records\creature\monster\skeleton\anm\anm_skeleton01.dbr
```

which binds `sHandedSpecialAnimRef1='AoE360'` and `sHandedSpecialAnimRef2='LethalStrike'`. So the
other two champions **can** cast bladestorm and netherstrike, and the Hunt was the only one who could
not, in exactly the domain of Will's complaint. Round 1's gate looped `for sk in _NEW_SKILLS`, so it
was structurally incapable of catching a defect in a slot the module kept.

**The fix: bind the animation rather than avoid it.** He has no animation table, so his inline
animation fields ARE his live table, which is where the binding goes:

| row | why this row | ref | animation | provenance |
| --- | --- | --- | --- | --- |
| `spear*` | the row the engine reads while he holds the R-83 spear (`chanceToEquipRightHand=100`, Item1 weight 100) | `AoE360` | `Creatures\PC\Female\ANM\FemalePC_Spear_Skill_Tempest.anm` | the **modal** shipped `spear`-row AoE360 binding: 11 of 23 carriers |
| `unarmed*` | the engine's universal fallback row, so the repair survives any later veto of the spear (BL-b98-DEBT-1/7) instead of dying with it | `AoE360` | `Creatures\PC\Male\ANM\MalePC_DW_Skill_AOE360.anm` | the modal shipped `unarmed`-row AoE360 binding: 5 carriers |

Neither path is hardcoded on trust: `_modal_row_binding()` re-derives the modal `(row, ref) -> .anm`
binding from the assembled db at build time and **fails the build** if the constant is no longer the
modal shipped choice. Precedent: `coldworm_buffs.py` writes ref + anim on exactly this shape.

**The gate is rebuilt, not patched.** `_castability_violations()` now walks **every** populated
active slot (`attackSkillName`, `initialSkillName`, `dyingSkillName`, `specialAttackSkillName`,
`specialAttack2..6SkillName`), resolves each skill, reads its `skillSpecialAnimationName`, and
requires the caster to bind that name on every row it can be reading. The wielded row is **derived**
from the `Class` of the item he is guaranteed in RightHand (`WeaponHunting_Spear -> spear`,
`WeaponMelee_* -> sHanded`, and so on), so the gate follows the weapon; an unmapped weapon Class is a
gate FAILURE, never a silent pass. This also retires round 1's other trap: its docstring and gate
text still said `unarmedSpecialAnimRef` after the record had just been given a spear, which is the
wrong row and a trap for the next lane.

**Honest limitation.** The AoE360 pose is a PC-rig animation on the ShadowStalker rig, the same
cross-rig class as R-83's borrowed swing poses. It makes the cast FIRE, which is the law. Whether the
whirl READS right is Will's eye, folded into BL-b98-DEBT-1.

### 11.2 BLOCKER - his soul still granted the skill this lane retired

`toxeus_hunt_soul_{n,e,l}` carried `itemSkillName = records\skills\soulskills\toxeus_flashpowder.dbr`,
the flagship of item 4's retirement. So the one player-facing artifact of his identity, now dropping
at 100% (R-81), handed out an ability he no longer has, and pointed at an over-shared filler (15 soul
records grant it in the deployed arz). The other two champion souls summon their champion; his was the
odd one out.

**Fix.** All three tiers grant `svc_hunt_quarrysmark`, the "become the Hunt" grant, at
`itemSkillLevel` n/e/l = **1/2/3**, which is the monolith's own established soul-tier convention and
also keeps the grant inside the skill's `skillMaxLevel` of 3. Soul and monster share ONE skill record,
so the player's mark and his mark can never diverge. **New invariant of the class:** a soul may never
grant a level its skill does not have.

**Fix-upstream (BL-103), three places, so nothing is left saying the old thing:**
- `toxeus_suite.py` `tagSVCSoulToxeusHuntDESC` no longer ends "and the flash-burst that opens the
  range"; it now reads "and his mark: what you wound, you keep". `verify()` fails the build if the
  flash-burst wording ever returns.
- `toxeus_suite.py` `_SOUL_PROC` carries an explicit pointer comment (the value is deliberately left
  at the shipped pre-state so the repointing module's "another writer owns this" guard still works).
- `skill_quality.ALLOW['toxeus_flashpowder.dbr']` drops `tagSVCSoulToxeusHunt` from its locked family
  roster: he left the family. That gate is subset-based, so a stale entry would NOT have failed the
  build, which is precisely why it had to be removed by hand. Removing it also makes the coupling
  fail-loud in the other direction: if the repoint ever regresses, he is outside the locked roster
  and the gate goes red.

### 11.3 MEDIUM - unreported inherited donor payloads

Cloning a record brings the donor's whole payload. Round 1 shipped the leftovers silently; each is now
stripped, with a gate and a planted negative.

| skill | inherited leftover | why it had to go |
| --- | --- | --- |
| `svc_hunt_longreach` | `offensivePetrifyMin = 2.0` | a 2-second **hard petrify** at 30% cast chance on a 5s cooldown at range 12-22, stacked on R-80's unleashable Legendary pursuit. Combat-defining, never designed, never disclosed. |
| `svc_hunt_longreach` | lifedrain's 16-entry `offensiveLifeLeechMin` / `offensiveLifeMin` | he is not a life-drainer; lifedrain is one of the three skills this lane retired from his kit. |
| `svc_hunt_rundown` | flash powder's 12-entry `offensiveConfusionChance`, `offensiveFumbleMin`, `offensiveProjectileFumbleMin` (+ their durations) | the blind/confuse package of the exact skill it replaces. |
| `svc_hunt_rundown` | flat `offensivePierceMin/Max` ladder | this skill authors its own physical ladder plus a pierce RATIO; the inherited flat ladder was an undisclosed third damage source. |
| `svc_hunt_rundown` | `radiusEffectName = 343_FlashPowder_FXPak01`, `particleEffectAttachPoint1 = Head`, `skillHitSound = secretninjapowdercastpak` | the literal audiovisual signature of Flash Powder. Stripped rather than repointed: 5 shipped monster `Skill_AttackRadius` records ship with no `radiusEffectName` at all, so absence is in-parity and needs no colour claim (process law #3). |

Two related fixes in the same pass:
- `svc_hunt_quarrysmark_buff` **keeps** the donor's physical/pierce resist shred (marked prey taking
  the spear harder IS this skill's identity) but on a **designed 3-entry ladder** (-25/-32/-40)
  instead of Study Prey's inherited 12-entry one, which `skillLevel [1,2,3]` was reading at its three
  weakest steps. `skillActiveDuration` also moved to 6.0 to match the three 6-second effect timers.
- `svc_hunt_longreach` `maxDistance` 18 -> 22, because the AI is told to cast it at LongRange up to
  22 and the far third of his own band was a dry cast. Gated: `maxDistance >= longRangeMax`.

### 11.4 MEDIUM - the player-surface checklist now covers the new skill class

Round 1's checklist covered Runbreaker only. "Quarry's Mark", "The Long Reach" and "Run Them Down"
existed **only** in `FileDescription`, a dev-only field, while `svc_hunt_quarrysmark_buff` is
`debufSkill=1` and therefore lands on the **player's status bar** reading `tagSkillName095` = "Study
Prey", with `tagSkillDescription095` describing pierce damage, which is not what it does.

| record | player-visible? | now reads |
| --- | --- | --- |
| `svc_hunt_quarrysmark` | YES, it is what his soul grants | `tagSVCHuntQuarrysMark` "Quarry's Mark" + its own description |
| `svc_hunt_quarrysmark_buff` | YES, `debufSkill=1`, the player's status bar | "Quarry's Mark" + a description written for the debuffed side |
| `svc_hunt_longreach` | no UI surface (monster-only active) | `tagSVCHuntLongReach` "The Long Reach" |
| `svc_hunt_rundown` | no UI surface (monster-only active) | `tagSVCHuntRunDown` "Run Them Down" |

Gated both ways: the record must name the mod-authored tag, and the tag must be present in the Text
set (a missing tag would show a raw tag string in game). `tagSVCLeinth*` and `tagSVCTempestNAME` are
the in-repo precedent for mod-authored skill tags.

**Disclosed, not fixed (BL-b98-DEBT-10):** the two monster-only actives still inherit their donors'
icons and sounds. `svc_hunt_longreach` keeps Life Drain's NegativeEnergyRay icons and its
`skillHitSound`/`skillSwipeSound` lifedrain paks (inherited from `zshadowblast`, an orphan DRX record
with zero other referencers, so nobody has heard it either). Neither has a UI surface on a monster,
and **no claim is made here about how they sound**. One-line repoint per field once a confirmed donor
is agreed.

### 11.5 LOW - `spearSpawnAnim`, and the census corrections

- **`spearSpawnAnim`** was the one animation slot the new spear row lacked. Both his `sHanded` and
  `unarmed` rows bind `ShadowStalker_Spawn.anm`; the spear row did not, and the spear row is now his
  ONLY row while he is a `ControllerMonsterHidden` ambusher (appearDistance 12.0), so his emerge pose
  had lost its binding. Now self-sourced from `sHandedSpawnAnim` like run/die/stun, and added to
  SPEAR-ANIM-1's required list with a planted negative.
- **The borrowed-pose debt is quantified** in BL-b98-DEBT-1: the Maenad swing poses track 26 bones
  including 4 tails, `ShadowStalker.msh` carries about 30 including HorseBone / Neck02 / Toe / Ear /
  Jaw and no tails, so 8 of his bones freeze during the swing and 4 tracks hit nothing, while the
  whole shoulder/forearm/wrist/Bone_R_Weapon chain IS tracked and 56 shipped TigerMan records play
  these same anims. He WILL swing. Two closer leads were checked and **rejected as precedent** because
  both are different meshes: `records\skills\stealth\drxpet\anm_shadowstalker.dbr` is the table of 42
  pets on `DRX\meshes\stalker.msh`, and `records\test\outsider_hero_*_46.dbr` wear
  `...\shadowstalker\daemon_outsider.msh` and point at an animation table that is not even present in
  the mod arz. Ranked fallbacks unchanged.
- **ShadowStalker census** corrected in section 5 and in R-84 (30 Monster records, all Demon, 26
  Skeleton and 4 Jackalman on a different mesh path). Decision unchanged.
- **Controller carrier counts** (`toxeus_hunt_endless` docstring): round 1 quoted 21 / 107 / 504, the
  vet counted 15 / 69 / 531, a mod-arz-only re-run gives 8 / 31 / 250. All three denominators are
  defensible and the conclusion is identical under all of them, so the docstring now states the
  method instead of a bare number and notes that each value written has a **named** shipped carrier
  verified by record rather than by count.

### 11.6 Not a defect, recorded so it is not mistaken for one

The vet flagged that the brief asked whether the EoAT formula drop "fires ONLY on Legendary". It does
not, and that is deliberate: `chanceToEquipMisc4 = 100` on all three tiers, exactly as the DEPLOYED
`um_toxeus_enslaver_99` already ships, which is what R-13 and R-82 say. The Legendary gate lives on
the **recipe** (`svc_toxeus_eoat_formula` reagents 1/2/3 are all `_l` souls) and `verify()` asserts it
fail-loud. See section 2.

### 11.7 What round 2 did NOT change

Every round-1 finding the vet upheld is untouched: the drop chain, the endless-pursuit variant and its
controller, the Runbreaker items and their F3 mesh correction, the ungated fixed encounter, the
Enslaver shroud, the ledger allocation, and the no-deploy discipline. The NOT-DONE list in section 9
is unchanged except that BL-b98-DEBT-10 joins it.
