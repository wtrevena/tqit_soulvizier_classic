r"""tools/patches/charon_rework.py - the Golden Bough forecourt uber, REWORKED.

WILL, VERBATIM (2026-08-11):

    "the charon uber boss we created needs to be re-worked, he is pretty much
     identical to the base game charon boss we cloned him off. maybe we can
     replace him with a different uber monster that is more unique"

He is right, and the artifact says so in one table. The shipped uber was NOT
"the same guy, bigger" - `um_charon_ferryman_99` (Charon01.msh, sc 1.7) already
rig-swapped to `um_charonform2_ferryman_99` (Charon02.msh, sc 1.2). The defect
is the KIT, byte-for-byte against the base bosses it was cloned from:

    | slot            | ours F1                 | boss_charon_43          |
    | skillName1      | charon_projectiletrigger| charon_projectiletrigger|
    | skillName4      | charon_selfbuff         | charon_selfbuff         |
    | skillName6      | charon_geyserform1      | charon_geyserform1      |
    | skillName7      | charon_summon           | charon_summon           |
    | specialAttack*  | identical               | identical               |

...and the same for form 2 vs `boss_charonform2_43`. The only authored deltas
were `characterLife`, four resist floats, `scale`, `actorHeight`, one aura and a
`deathEffect`. `apply_svc_patches._create_goldenbough_boss` says it out loud:
*"Keep Charon02's own kit verbatim"*. There was nothing to salvage.

================================================================================
WHAT SHIPS: AKREMON, THE GRASPING ROOT
================================================================================
`akremon` (ἀκρέμων) is the Greek word for a BOUGH. The thing the forecourt keeps
is the Golden Bough, and the thing that grows it is now the boss - which is a
tighter lore fit than the ferryman who merely stood next to it ever was.

Every hand that ever reached for the Bough is still at the shrine, grown through
and held fast, because the black tree those wrists are grown into is what the
forecourt actually keeps. Akremon does not ferry, does not bargain and does not
bleed. It takes the toll in arms. And when the trunk finally splits, the burning
heartwood that grows the boughs walks out of it to take yours.

Three beats, two bodies, the SAME proven `actorToSpawnOnDeath` link.

  BEAT 1 - THE GRASPING ROOT (phase 1, `Ascacophus02.msh`, PLANT, rs 1.35)
    * THE WOOD DOES NOT BLEED - the donor's native `ascacophus_bleeddamageimmunity`
      (Skill_Passive, `defensiveBleeding 100.0`) stays. The mod's marquee weapons
      are bleed spears; half this fight tells that build to sit down.
      HONEST: NOT a roster first - `um_helepolis_99` already carries the identical
      record. It is a first for a LIVING boss, and it is what makes beat 3 land.
    * ROOT-SNARE - `drx_earthbind` (Skill_AttackRadius, radius 22.0, cd 20).
    * THE THICKET - `quillwards` (Skill_DefensiveWall, cd 20, spawns
      `pets\quillvine_12` on a 10->30s TTL ladder). **ZERO other uber in the mod
      fields a Skill_DefensiveWall.** It grows cover between you and it. The
      immobile quilvine rig still appears in this fight - as the WALL, the one
      role where being rooted to the spot is the entire point (see CORRECTION 9).
    * QUILL VOLLEY - `razorquill_megaburst` (Skill_AttackProjectileFan): the
      reach that makes the snare a threat instead of a nap.
    * RETINUE FROM ITS OWN FAMILY (the R-125 bar, satisfied literally): the
      donor's native `hero_quillvines` (Skill_SpawnPet, petLimit 6, burst 3)
      keeps firing, untouched. HONEST, and corrected this round: those adds are
      STATIONARY too - `quillvine_01..06` all sit on `anm_quilvine.dbr`, the same
      locomotion-less table this lane bans for placed and summoned bodies, at
      `characterRunSpeed 0.0`. So BOTH of phase 1's plant-summon skills produce
      cover rather than chasers. That is the donor's native, unmutated base-game
      behaviour (vines being rooted is correct) and no crash law is touched - but
      "keeps firing" must not be read as "sends things after you". Both pet
      families count toward the add-density reading owed under BL-BOUGH-DEBT-2.

  BEAT 2 - THE SPLITTING (`svc_bough_splitting`)
    A clone of `lowhealth_berserkerrage01` (Skill_PassiveOnLifeBuffSelf,
    `lifeMonitorPercent 33.0`, `skillActiveDuration 12.0`, cd 5.0) - it fires
    ITSELF at 33% life with zero AI wiring. At the trigger the bark splits and
    the THORNS COME OUT: this lane moves the thorn coat onto the trigger record
    as `retaliationPierce`, so it is a phase-gated beat rather than a random cast
    (see CORRECTION 1). Precedent for the MECHANIC, corrected: see CORRECTION 7.
    WHAT IT GRANTS, IN FULL, BECAUSE THE DONOR'S OWN NUMBERS ARE NOT OURS
    (CORRECTION 14): retaliation pierce 180-260, an AUTHORED **+35% physical
    damage**, and DELIBERATELY **zero damage absorption and zero life regen** -
    the donor is `DefensiveMastery_Adrenaline` and ships 36% / 8-per-second at the
    wired level, which would have been a wall under this lane's own claim of exact
    Gaoler durability parity. Beat 2 costs the player TIME, never immunity.

  BEAT 3 - THE HEARTWOOD ABLAZE (phase 2, terminal, `emberoakmesh.msh`, PLANT,
    rs 1.45)
    The trunk bursts and the burning heartwood walks out of it, faster than the
    shell it came from. Slow physical/pierce zoning inverts into a fire kit that
    rides its donor's own records verbatim: `ringofflame` (a TOGGLED burning ring
    it simply wears - the fire reads on screen with zero FX authoring),
    `ringofflame_softenmetal`, `volcanicorb` + `volcanicorb_immolation` +
    `volcanicorb_fragmentation`, `drxheatshield`, `emberoak_stoneform`, plus
    `razorquill_nova` (Skill_AttackProjectileRing) and the thorn coat.
    **BLEED IMMUNITY DOES NOT CARRY**, and `defensiveLife` drops 60 -> 40, so the
    bleed/vitality build you shelved in beat 1 genuinely comes back for the kill.
    That is the whole shape of the fight in one sentence, and CORRECTION 10 is
    why it is now true rather than merely claimed.

  THE HANDBRIAR (Champion escort x2, `JungleCreep01.msh`, PLANT, rs 1.30)
    A ground-hugging whipping vine that can actually keep up: maximum silhouette
    contrast against a 2.8-scale trunk. That IS R-100 #18 ("they appear just like
    normal guys").

================================================================================
HOW IT SHIPS: ARZ-ONLY, IN PLACE, AT THE FROZEN RECORD PATHS
================================================================================
HARD CONSTRAINT from the order: the Golden Bough forecourt placement and its
spawn/proxy chain are REUSED. No map rebuild. `build_section_surgery.INJECT_SPECS`
places `q_goldenbough_lone` and `svc_charon_chest` BY NAME, so those names are
frozen. This module therefore REPLACES THE CONTENTS of the three monster records
the chain already names, rather than authoring new paths and repointing:

    um_charon_ferryman_99.dbr      <- xhero_strongbark_44   (the Grasping Root)
    um_charonform2_ferryman_99.dbr <- um_emberoak_42        (the Heartwood Ablaze)
    svc_charon_wraith_99.dbr       <- am_junglecreep_41     (the Handbriar)

MEASURED reason this is the ONLY safe shape (not a preference - three hard-coded
gates key on those exact basenames, and authoring new paths reds all three):

  1. `tools/verify_soul_drop_rates.py` EXPECT pins
     `um_charonform2_ferryman_99 -> ('PLACED', 33.0)`. A new terminal at a new
     path leaves the old record un-PLACED, so its klass flips and the spot test
     fails.
  2. `tools/build_svc_database.py:SOUL_RATE_ZERO_PINS` pins the chain HEAD
     `um_charon_ferryman_99` at 0.
  3. `tools/patches/uber_quest_drops.LEAKS[0]` and
     `tools/patches/red_uber_orbs.EXEMPT` both key on the pair by path.

Monster record paths are NOT baked into TQ saves (only ITEM paths are), so
replacing their contents is save-safe. The names now lie; that is registered as
BACKLOG debt for a future breaking build, exactly as the item paths are.

================================================================================
CORRECTIONS TO THE RATIFIED SPEC - each one measured on the LIVE arz
(work/SoulvizierClassic/Database/SoulvizierClassic.arz, 51,253 records, build83)
================================================================================
1. CAST SLOTS: the spec allocated FOUR new casts on phase 1 and there are only
   THREE free. Measured on `xhero_strongbark_44`: `specialAttackSkillName` =
   `hero_ascacophus_stumpstomp` (chance 30) and `specialAttack3SkillName` =
   `hero_quillvines` (chance 70) are OCCUPIED - both are the donor's own-family
   signature, which the R-125 bar forbids displacing. The engine caps at five
   slots, so exactly `2`, `4`, `5` are free.
   RESOLUTION: earthbind / quillwards / megaburst take the three cast slots, and
   `typhon_thornyaura` is NOT cast by phase 1 at all - its retaliation is folded
   into `svc_bough_splitting`, so the thorns arrive WITH the splitting instead of
   on a random 20s roll. Strictly better design; costs nothing. The thorn coat
   still ships as a real cast on the BLOOM (a free slot exists there).

2. SKILL SLOTS: the spec said phase 1's donor "occupies 1-6, 10, 11, 12". It also
   occupies **15** (`elementalresistance_10xlevel`) and **17** (`racial_plant`).
   The spec separately claimed the donor "does NOT carry racial_plant as a skill" -
   it does, at `skillName17`. Nothing breaks: `_svc_add_skill` takes the first
   EMPTY slot, so the additions land on 7/8/9/13/14/16.

3. `boss_conversionimmunity` IS resolvable - `records\skills\boss skills\
   boss_conversionimmunity.dbr` exists and both shipped Charon forms carry it.
   The spec told the implementer to probe and skip it. It ships.
   Real paths, measured: `boss_scaling` = `records\skills\monster skills\
   passive_buffs\boss_scaling.dbr`; `all_hpscaling_passive` =
   `records\xpack\skills\bossskills\all_hpscaling_passive.dbr`.

4. **THE TERMINAL KEEPS `bosschest02_charon`, AND THIS IS A HARD GATE, NOT TASTE.**
   The spec's lore reading wants the Charon-named orb gone (b53 did exactly that
   for Dagon). MEASURED: `tools/svc_orb_breadth.py` sets `MIN_PROXIES = 6` /
   `MIN_TABLES = 18` and `orb_loot_breadth.apply` RAISES below either floor. That
   scope is DERIVED as "every proxy an UBER names", and
   `um_charonform2_ferryman_99` is the only uber naming `bosschest02_charon` - so
   retargeting it drops the scope to 5 proxies / 15 tables and REDS THE BUILD, and
   would additionally orphan three tables that `orb_loot_breadth` + `orb_armor_rows`
   already widened (the BL-R181-DEBT-7 ownership gate). The donor
   `us_hellflower_37` carries no `treasureProxyName`, so this module SETS it
   explicitly. Registered as `BL-BOUGH-DEBT-4`: the encounter still drops an orb
   whose shared base-game display string reads "Charon's Essence", and retargeting
   it needs a coordinated floor re-measure in its own wave.

5. `offensiveTrapMin/Max` (the spec's "you start rooting what you hit") is carried
   by **ZERO** of the 2,095 soul records in the DB and by only 32 records DB-wide -
   it is not part of the soul template's shape. The field that IS
   (2,095 souls carry it) and that means the same thing is
   `offensiveSlowPhysicalMin` + `offensiveSlowPhysicalDurationMin`. That ships
   instead, with the amgoz1-tradition downside (negative `characterRunSpeed`,
   2,158 souls carry the field) intact.

5b. THE CENSUS TALLIES ARE RE-MEASURED, NOT COPIED. Round 2 re-ran the race
   census on the live artifact rather than trusting the spec: `um_*`/`svc_um_*`
   with `monsterClassification == Boss` = **53** records - Undead 18, Demon 14,
   Beastman 8, Insectoid 4, Magical 3, Animal 3, Beast 2, Device 1, **Plant 0**.
   That reproduces the ratified spec's numbers exactly on
   `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (build83, 51,253
   records). A round-2 vet pass reported 50 / Demon 12 / Beastman 7 off a
   different artifact; the conclusion is identical either way and the one number
   the design rests on - Plant = ZERO - holds in both readings. Also re-measured
   there: the Boss-uber `characterRunSpeed` band is min 0.35 / median 1.00 /
   max 4.00, which is the frame CORRECTION 9 uses.

6. b86 SOUL-RENAME ROW 7 STANDS - NO SUPERSEDE WAS NEEDED. Verified in
   `docs/SOUL_RENAME_PROPOSAL.md`: row 7 governs `tagSoulSVC9005` on
   `records\item\equipmentring\soul\svc_uber\boss_charon_soul_{n,e,l}.dbr`, the
   GENERATED soul of the BASE-GAME `boss_charon_{39,41,43}`. Our uber's soul is
   `...\svc_uber\ferryman_soul_{n,e,l}.dbr` on `tagSVCSoulFerryman`. Different
   record, different tag; they never collided. Our uber vacating the ferryman
   display namespace entirely STRENGTHENS row 7's primary. b86 ships row 7
   unchanged. (WILL_RULINGS R-231-C records this so it cannot be re-litigated.)

7. THE LIVE DEFECT NOBODY FILED: the shipped Champion escort
   `svc_charon_wraith_99` has `characterLife = [878.0, 300.0, 400.0]` - life FALLS
   from Normal to Epic. That is R-100 #18 as a measurable field. It dies with this
   wave and `verify()` carries a strictly-ascending gate so it cannot come back.
   AND THE BEAT-2 CITATION IS CORRECTED: round 1 cited "the pattern
   `um_vashkarr_99` already ships". Measured - `um_vashkarr_99` carries
   `lowhealth_berserkerrage01` at `skillLevel 0`, i.e. INACTIVE by the mod's own
   B-SOUL-PROC-1 lesson, so it proves nothing. The MECHANIC is fine and the real
   live precedent is `elder_um_boarmonstrous_16` (Champion, `skillLevel 5`) and
   `elder_am_boar_09` (`skillLevel 3`) on `lowhealth_boarberserkerrage01`; this
   lane wires `svc_bough_splitting` at level 10, inside its `skillMaxLevel 15`.

8. **"ORMENOS" WAS A NAME COLLISION AND IS DEAD.** The ratified spec named the
   boss Ormenos. Measured: `Ormenos` is ALREADY a boss in this database - the
   China Telkine, `boss_chinatelkine_ormenos_{38,41,44}.dbr`, with **59 records**
   carrying the name including `controller_ormenos`, six `ormenos_*` boss skills,
   three `ormenos_magmasprite_*` minions, `Ormenos_FireSpawn_FX` and its OWN soul
   at `records\item\equipmentring\soul\telkine\ormenos_soul_{n,e,l}.dbr`. Shipping
   a second, unrelated Ormenos with its own soul is exactly the duplicate-identity
   class Will keeps filing. The boss is now **AKREMON** (ἀκρέμων, Greek for
   "bough"): 0 record hits and 0 text-resource hits across the whole mod, and a
   tighter lore fit than Ormenos ever had, because the shrine's whole subject is
   a bough. `verify()` now carries a COLLISION GATE so no future rename can
   reintroduce a display name that an unrelated live monster family already owns.

9. **THE TERMINAL, THE ESCORTS AND THE SOUL PET WERE ALL IMMOBILE. DONORS SWAPPED.**
   Round 1 built phase 2 from `us_hellflower_37` and the escort from
   `am_quillvine_35`. Both ship `characterRunSpeed = 0.0`, and it is NOT tunable:
   their anim table `records\creature\monster\quilvine\anm\anm_quilvine.dbr`
   declares the `*RunAnimSpeed` scalars but binds **NO `unarmedRunAnim` and no
   `unarmedWalkAnim` clip at all** (measured; compare `anm_ascacophus02`,
   `anm_bogdweller` and `anm_junglecreep`, which all bind both). Raising runSpeed
   would ask the rig for an animation it does not bind - the B-SOUL-PROC-2 / D19
   class the crash laws forbid - and no new art is allowed. So the TERMINAL form,
   the form carrying all three guaranteed rewards, could not chase the player at
   all; the two "escorts" could not escort; and the soul's marquee permanent
   summon would never follow its owner. The encounter was very likely EASIER than
   the Charon it replaces, which is the opposite of the order.
   RESOLUTION - swap to donors that OWN a rig with locomotion, keeping Plant:
     * phase 2: `um_emberoak_42` (`DRX\meshes\emberoakmesh.msh`, `anm_bogdweller`,
       rs 1.0, Plant, Hero, live scale 1.90, `actorHeight` 1.0). Strictly better
       than the hellflower on every axis the design cared about: it is MOBILE, its
       fire kit is RICHER and native (`ringofflame` is a toggled burning ring it
       simply wears, plus two volcanicorb modifiers and `drxheatshield`), it keeps
       PLANT so the Plant=0 headline stands, its live scale 1.90 makes the 2.0 ask
       a 1.05x stretch instead of the hellflower's 1.33x, and its rotation leaves
       cast slots 4 and 5 free behind only ONE chance-100 slot instead of three -
       which is also the structural fix for the round-1 finding that the added
       casts would rarely fire.
     * escort: `am_junglecreep_41` (`JungleCreep01.msh`, `anm_junglecreep`, rs 1.0,
       Plant, 15 live carriers, live scale range 0.70..1.60 so the 1.55 ask is
       INSIDE proven range). It also carries NO soul loot at all, so the escort
       cannot leak one even before `_svc_clear_soul_loot` runs.
   HONEST COST: the terminal is no longer amgoz1's own SV hellflower. The
   immobile quilvine rig still appears in the fight, in the roles where being
   rooted is correct - the `quillwards` WALL pets and, corrected this round, the
   `hero_quillvines` RETINUE adds as well (`quillvine_01..06`, all on
   `anm_quilvine.dbr` at runSpeed 0.0). Round 2 disclosed only the wall pets.
   Nothing this lane places or summons sits on that table; both surviving
   quilvine roles are the donor's own untouched base-game behaviour.
   SPEEDS, all written explicitly and all inside the measured Boss-uber band
   (min 0.35, median 1.00, max 4.00): phase 1 **1.35** (rig-proven exactly -
   `credits_ringlesstree` ships 1.35 on Ascacophus02.msh), the terminal **1.45**
   (above this rig's only live carrier at 1.0; disclosed, cosmetic-only risk since
   the rig binds the clip), the Handbriar **1.30** (rig-proven exactly -
   `um_speckledjim_45` ships 1.30 on JungleCreep01.msh). The soul pet inherits the
   donor's 1.0, which is both the shipped oarsman's value and a clean pass of
   PET-STAT-MIRROR's `pet >= 0.90 x source`.
   The shipped Charon forms ran 2.8 and 4.0 - the two FASTEST bodies in the entire
   53-boss uber roster. This encounter deliberately does not chase that outlier.

10. **DURABILITY RE-CALIBRATED TO THE GAOLER, AND THE VITALITY WALL CUT.**
   Round 1 set life at "exact parity with the shipped Charon forms" - 28,000 +
   30,000 = **58,000 on Epic** - which was never itself calibrated against
   anything. `docs/reports/gaoler_variance_rca.md` is the reference frame this
   lane was told to use: Alkyoneus the Soul-Gaoler is **two forms totalling 35,000
   on Epic** plus a six-strong guard horde, and the RCA's verdict is hard-but-fair
   and killable ("no action warranted") after Will beat him on the second attempt.
   58,000 is 1.66x that, on an encounter that is now MOBILE in both phases. Ships
   at **13,000/17,000/22,000 + 14,000/18,000/24,000 = 27,000 / 35,000 / 46,000**
   against the Gaoler's 26,000 / 35,000 / 47,000 - an Epic total matched exactly.
   NO WALLS, and one real one is removed: round 1 shipped `defensiveLife 100` on
   BOTH forms, i.e. 100% VITALITY immunity end to end, which silently contradicted
   the design's own headline that the bleed/vitality build comes back in beat 3.
   Ships 60 on phase 1 and **40** on the terminal. Bleed immunity (phase 1 only,
   donor-native) stays, because that is the deliberate half-fight lever and it is
   WILL-DECISION 6; a lever the fight then hands back is not a wall.

--------------------------------------------------------------------------------
ROUND 3 - the vet found the two surfaces the player actually KEEPS. Both were
still Charon. Both are the same defect class as round 2's stale pet registration:
a SUPERSEDED WRITER'S OUTPUT SURVIVING UNDER THE NEW WRITER'S AT A FROZEN PATH.
--------------------------------------------------------------------------------
11. **THE SOUL WAS RE-LABELLED, NOT RE-THEMED.** MEASURED after apply() over the
   live build83 arz: the Epic tier still carried the shipped ferryman's
   `offensiveCold{Min,Max,Modifier}`, `offensiveSlowCold*`, `defensiveCold`,
   `offensiveLife{Min,Max}` (vitality), `offensiveLifeLeechMin`,
   `defensiveLifeLeech`, `offensiveFear{Min,Max}` and `offensivePercentCurrentLifeMin`
   - the last being **base Charon's own signature lever** (`charon_geyserform1`,
   24 roster carriers), which the ratified spec forbade on this soul BY NAME. The
   new fire/pierce block layered on top of all of it, roughly doubling the
   offensive load nobody balanced, on the one reward the player keeps forever.
   ROOT CAUSE: the soul PATH is frozen for save-compat, so `_create_soul` runs
   over a record `_create_goldenbough_boss` already wrote THIS RUN;
   `_ensure_record` no-ops on an existing record and `_set_soul_fields` only
   layers keys. FIX: `_strip_superseded_soul_stats` clears the superseded bonus-
   STAT block (offensive/defensive/retaliation/character/augmentSkill/itemSkill
   prefixes, minus exactly what the rebuild is about to write) before
   `_create_soul`; structural fields are never in reach, and `itemQualityTag` /
   `itemText` are re-applied afterwards by `run_registry_gates` finalization
   (`_apply_soul_tier_naming` / `_wire_soul_desc_itemtext`), which runs after every
   registry module. verify() now proves the OLD identity is ABSENT rather than only
   that the new one is present - round 2's gate read `itemNameTag` and nothing else.

12. **THE GRANTED SUMMON STILL WORE CHARON'S FACE.** `summon_charon_oarsman`
   shipped `SVTextures\skills\drownedspirit{up,down}.tex` - a DROWNED-GHOST glyph,
   and a Charon-specific one (only 3 records DB-wide reference `drownedspirit*`) -
   plus the Lyia-clone `maenadalertpak` cast sound, under the name "Graft the
   Burning Heartwood". R-125's player-surface law names the icon explicitly.
   FIXED AT THE SOURCE OF TRUTH: `_SUMMON_SKILL_ICON['summon_charon_oarsman']` in
   apply_svc_patches.py now maps `skill icons\soul\flamewave{up,down}.tex` - a fire
   glyph for a burning ember oak, with **0 references across every string field of
   all 51,253 records**, i.e. it collides with no other summon AND no other granted
   skill. That is strictly stronger than every established row in that table
   (`bloodbathup` shares with 3 live skills, `thunderorbup` with 4, `voidsnapup`
   with 1). Both halves PRESENT in the shipped DRXtextures.arc. `flamering{up,down}`
   was the tighter 1:1 with the pet's own `ringofflame` and IS proven to render, but
   it is worn by the Yaoguai soul's granted skill - a player holding both souls
   would see one glyph on two buttons, which is the duplicate-identity class Will
   keeps filing; it stays documented as the proven-render fallback
   (`BL-BOUGH-DEBT-10` covers the one-look confirmation).
   The hit sound is not written by `_build_boss_summon` at all, so this module sets
   it to the terminal donor's OWN `bogdwelleralertpak`, the `<family>alertpak`
   convention the already-fixed summons use. HONEST: `maenadalertpak` is a
   CLASS-wide residue (31 of the 52 soul summons in the DB carry it) that this lane
   did not create and does not fix beyond its own record - `BL-BOUGH-DEBT-9`.

13. **THE SCALER SWAP WAS BLIND.** Round 2 wrote `skillName12 = boss_scaling`
   unconditionally on both forms and declared `_SK_HERO_SCALING` without ever
   using it. Both boss donors do carry `hero_scaling` there, but the ESCORT donor
   `am_junglecreep_41` carries `globalproperties_legendary01` in the same slot, so
   one future donor swap would have destroyed a difficulty row with a green gate.
   `_swap_scaler` now ASSERTS the incumbent and verify() proves the end state.
   HONEST SCOPE: `globalproperties_*` rows carry only `characterBaseAttackSpeedTag`
   plus UI bitmaps - no stat or resistance scaling - and 8 of the 53 Boss-class
   ubers declare none at all, so the shipped shape (phase 1 normal01 + epic01;
   terminal none) sits inside the roster norm. Latent-trap fix, not a balance change.

--------------------------------------------------------------------------------
ROUND 4 - the vet found the numbers NOBODY AUTHORED. Every one of these is the
same defect class: A DONOR'S OWN PAYLOAD RIDING ALONG UNDER A CLAIM THAT DID NOT
MENTION IT. Round 3 fixed superseded WRITERS surviving; round 4 fixes INHERITED
VALUES surviving. Both make a document say something the artifact does not.
--------------------------------------------------------------------------------
14. **BEAT 2 WAS SILENTLY A 36% DAMAGE SHIELD, AND THE VET ONLY CAUGHT TWO OF
   THE THREE.** `svc_bough_splitting` was a VERBATIM clone of
   `lowhealth_berserkerrage01` (ActorName `DefensiveMastery_Adrenaline`), wired at
   `skillLevel 10`. MEASURED on the live arz, the donor carries THREE non-zero
   level arrays, all of which the clone inherited and none of which appeared in
   this module, in R-231, in the BACKLOG durability row or in `verify()`:

     damageAbsorptionPercent  [10,12,15,18,22,24,26,29,32,**36**,38,...,65]
     characterLifeRegen       [ 5, 5, 6, 6, 6, 7, 7, 7, 8, **8**, 8,...,11]
     offensivePhysicalModifier[15,20,25,30,35,40,45,50,55,**60**,65,...,110]

   Index 9 = the wired level 10. With `lifeMonitorPercent 33.0`,
   `skillActiveDuration 12.0` and `skillCooldownTime 5.0` it re-fires every 5s, so
   it is PERMANENTLY up for the whole last third of phase 1. That is 36% flat
   damage absorption + 8/s regen + **60% physical damage**, on the one encounter
   whose headline claim - repeated in this module, in R-231-E and in the BACKLOG
   player-surface checklist - is "Epic total 35,000, matching the Gaoler's 35,000
   EXACTLY". Phase 1's last 5,610 Epic HP actually cost ~56% more damage than that
   number stated. The vet caught absorption and regen; the +60% physical was still
   unmeasured after its report.
   RESOLUTION - the record is already being surgically edited, so AUTHOR ALL
   THREE instead of inheriting any of them, as FLAT 20-ROW ARRAYS so the wired
   level cannot mis-index whatever it is set to:
     * `damageAbsorptionPercent` -> 0.0. The durability claim is now true as
       written; a boss that also shrugs off a third of the damage is a WALL, and
       the order asked for a hard fight, not an unkillable one.
     * `characterLifeRegen` -> 0.0. A boss healing during its own last third is
       the "unkillable, then killable" shape the Gaoler RCA exists to avoid.
     * `offensivePhysicalModifier` -> **35.0, KEPT AND STATED**. Beat 2 has to DO
       something or it is a cosmetic bark-crack, and an enrage that hits harder is
       the correct half of an Adrenaline donor to keep - it costs the player time,
       not immunity. 35 is an authored number, not the donor's accidental 60, and
       it is asserted by `verify()`, disclosed in R-231-G and carried in the
       BACKLOG durability row so no future reader can call it undisclosed again.
   The retaliation thorns (CORRECTION 1) are unchanged.

15. **THE TERMINAL'S ORDINARY LOOT BAND REGRESSED A FULL ACT.** The re-clone from
   `um_emberoak_42` (a DRX act-2/3 creature) replaced the encounter's Hades-tier
   tables with the donor's own: Misc1 -> `n_03_unique_all` + an act-3
   `materials\jungleroot`; Misc2 -> `03_*_misc` + jungleroot again; Misc3 ->
   `relic_15-21/41-45/57-61` + `01/02/03_act2_arcaneformulae` + `03_*_misc`.
   MEASURED against the peer band on the very reference boss this lane calibrates
   durability against: `um_polisgaoler_unbound_99` runs `01/02/03_act4_relics` +
   `01/02/03_act4_arcaneformulae`. **Phase 1 of this same encounter was already
   correct** (`n_04_unique_all`, `04_*_misc`, act-4 relics + formulae - the
   strongbark donor's own), so the two halves of one boss were banded a full act
   apart and the LOW one was the form carrying the Golden Bough, the soul and the
   orb. RESOLUTION: the terminal's Misc1/2/3 are retargeted onto the act-4 band by
   NAMED CONSTANTS, and the two act-3 `jungleroot` crafting rows are muted (a
   jungle root is not a thing that falls off a burning tree at the Styx). The
   three GUARANTEED rewards were never affected and are unchanged.

16. **PHASE 1 WENT FROM DROPPING NOTHING TO A 75/13/1.6 ROLL. NOW IT IS A
   DECISION, NOT A SIDE EFFECT.** MEASURED: the shipped `um_charon_ferryman_99`
   had NO Misc loot at all. The re-clone inherited `xhero_strongbark_44`'s full
   table (Misc3 @75, Misc2 @13, Misc1 @1.6). That is defensible in isolation - the
   other transform shells all drop, and this roll is byte-for-byte the Mnemophage
   shell's shape - but it is an encounter-level loot INCREASE, on the exact
   encounter behind Will's R-100 #10 complaint (which R-108 answered by cutting
   three chests to one), shipping in the same window as b84 `fix/loot-volume-trim`.
   RULED: **MUTED**, back to the shipped Charon shell's own shape. The encounter's
   ordinary loot volume is therefore NOT raised by this wave in either direction
   that a trim lane would have to re-trim, and the terminal - the reward-bearing
   form, at the correct act-4 band per CORRECTION 15 - is where the payout lives.
   `_ORM_MUTE_MISC` names the decision so it can be reversed in one line.
   (Checked: no breadth module derives scope from a monster's `lootMisc*`
   pointers - `orb_loot_breadth` keys on `treasureProxyName` and b84's
   `svc_loot_volume` is container-scoped - so muting the CHANCE is sufficient and
   nothing is orphaned.)

17. **THE HANDBRIAR'S WHOLE ROTATION WAS BEETLE BILE.** `am_junglecreep_41`'s
   native kit is one cast: `beetlebile_vomitbile` (Skill_AttackProjectileBurst,
   chance 88, MediumRange, 5 poison projectiles). The donor was chosen for its RIG
   and its D19 mobility (CORRECTION 9), never for its kit - but the escort ships
   under docs calling it "a ground-hugging whipping vine ... maximum silhouette
   contrast", and a ranged beetle-bile spitter is neither. RESOLUTION: the
   declared slot and the cast both move to `quillvine_barb`
   (Skill_AttackProjectile, physical + `offensivePierceRatioMin 50`, 7 live
   carriers - and its carriers are `quillvine_01..06`, i.e. THE VERY BODIES the
   boss's own `quillwards` wall and `hero_quillvines` retinue put on the field).
   So the escorts now fire the same barb as the briar the boss grows, which is the
   R-125 own-family bar satisfied at the ENCOUNTER level rather than the donor
   level. Wired `[4, 5, 6]` per difficulty, inside the record's 6-entry array so
   it cannot mis-index. HONEST: this is also a NERF in raw output - the shipped
   escort's bile was 5 projectiles x 159/183/207 poison; this is one barb at
   245/263/300 physical - which is the right direction for an add beside a boss
   calibrated to the Gaoler.

18. **THE SOUL PET LOST ITS DIFFICULTY ROWS, AND `_swap_scaler`'s OWN DISCIPLINE
   WAS NOT APPLIED TO THE PETS IT WAS WRITTEN FOR.** CORRECTION 13 added
   assert-the-incumbent to the two BOSS forms. MEASURED after apply(): the three
   soul pets went `globalproperties_legendary01` -> `hero_scaling` at slot 12 and
   LOST `globalproperties_normal01` / `_epic01` at slots 10/11, inherited from the
   emberoak source through `_update_existing_fields`. Impact is nil by this
   module's own CORRECTION 13 measurement (those rows carry only
   `characterBaseAttackSpeedTag` plus UI bitmaps) and all three pet gates were
   green - but a monster's `hero_scaling` on a player's permanent pet is residue,
   and "we assert the incumbent now" was only half true. RESOLUTION:
   `_restore_pet_difficulty_rows` asserts `hero_scaling` IS the incumbent, swaps
   `globalproperties_normal01` in at that slot with the shipped `[1,0,0]` vector,
   and re-adds `_epic01` `[0,1,0]` + `_legendary01` `[0,0,1]`. End state = the
   SHIPPED pet shape, so this is a strict non-regression, and `verify()` proves it.
   Also fixed, in the monolith and for every lane: `_build_boss_summon`'s log line
   claimed the strip left "the source anm table now drives the body". It does not.
   The strip is SOURCE-FAITHFUL by design - it removes only the overrides the
   source does not declare - so the source's OWN weapon-row overrides survive, and
   on this donor some of them point at a foreign rig (`staffWalkAnim =
   Neanderthal_Run.anm` and ~50 siblings; unreachable at `loadout=None`, and
   class-wide: 16 of the 237 soulskill pets carry the same clip). The line now
   says what it did.

================================================================================
CRASH-LAW COMPLIANCE, ITEMISED
================================================================================
* FX via MONSTER-RECORD FIELDS ONLY (`spawnEffect` / `deathEffect`); all four
  targets verified `Class == EffectEntity` in the arz. This module authors NO
  `charFxPak*` anywhere, and `verify()` fails if any `Skill_SpawnPet` we reference
  grew `charFxPakSelfNames`. The one charFxPak in play
  (`Typhon_Thorn_CharFXPak`, inside the base `typhon_thornyaura` record) is
  referenced and never mutated.
* NO `clone_record` FOR SOULS - `_create_soul` / `_ensure_record` only. Monsters
  may clone (the `mnemophage_mindshroud` precedent).
* NO Monster.tpl -> Pet.tpl equipment copy - `_build_boss_summon` with
  `loadout=None` (correct: a flower equips nothing).
* PERMANENT PET TTL = `[]` - the Lyia baseline carries none; `verify()` asserts it.
* A9 RENDER CHAIN - every form clones the donor that OWNS its rig. NO cross-rig
  mesh swap and NO new art: each mesh/texture already has live carriers.
  Correction to the spec: `xhero_strongbark_44` declares **752** animation fields,
  not zero - which is exactly why cloning it wholesale is safe (the full anim
  table comes with the clone, so the B-SOUL-PROC-2 class cannot arise).
* SOUL-LEAK INVARIANT - both BOSS donors ship `chanceToEquipFinger2 = 33.0` with
  their OWN soul in `lootFinger2Item1` (`strongbark_soul_*`, `emberoak_soul_*`).
  A raw clone therefore inherits a FOREIGN soul drop (the R-42/R-106 class).
  `_svc_clear_soul_loot` runs on all three BEFORE `_create_soul` rewires the
  terminal. (The escort donor `am_junglecreep_41` carries no soul at all, so it is
  clean even before the clear - belt and braces, and `verify()` proves it.)
* D19 PET MOBILITY - every body this encounter places or summons must sit on an
  anim table that BINDS `unarmedRunAnim`, not merely declare a nonzero runSpeed.
  `verify()` asserts this per body. Round 1 shipped three permanently immobile
  permanent pets past a monolith assert whose guard was inverted on exactly that
  case; this wave fixes the assert upstream (`apply_svc_patches` D19 block) and
  states the invariant here too, because a gate that only lives in one place is
  one refactor away from not existing.

ORDERING: registered immediately AFTER `uber_quest_drops` and BEFORE every
breadth/derivation module (`chest_loot_breadth`, `armor_loot_breadth`,
`red_uber_orbs`, `orb_loot_breadth`, `orb_armor_rows`), so those derive their
scope from the FINAL records at apply() AND verify() time and cannot disagree.
`uber_quest_markers` (earlier) writes `DisplayAsQuestItem` on these records and
its verify() re-derives on the final db, so this module re-asserts that field
explicitly after the re-clone.

NAMES ARE THIS LANE'S INVENTION AND SHIP AS DEFAULTS FLAGGED FOR WILL VETO
(the standing creative-bar rule, R-125 precedent).
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]          # tools/
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import apply_svc_patches as asp                       # noqa: E402
from apply_svc_patches import (                       # noqa: E402
    DATA_TYPE_FLOAT, DATA_TYPE_INT, DATA_TYPE_STRING,
    _bmp, _build_boss_summon, _create_soul, _svc_add_skill,
    _svc_clear_soul_loot, _svc_guarantee_unique,
)

MODULE_NAME = ("Golden Bough uber rework (Will 2026-08-11): Charon out, "
               "Akremon the Grasping Root in - arz-only, frozen proxy chain")

S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

# ── FROZEN PATHS (the map places these by name; see the header) ──────────────
_CH = r'records\xpack\creatures\monster\bosses\02_charon'
_ORM = _CH + r'\um_charon_ferryman_99.dbr'          # LEGACY PATH: phase 1
_BLOOM = _CH + r'\um_charonform2_ferryman_99.dbr'   # LEGACY PATH: phase 2, terminal
_BRIAR = _CH + r'\svc_charon_wraith_99.dbr'         # LEGACY PATH: Champion escort

_POOL = r'records\drxmap\proxy\pools\q_goldenbough_lone.dbr'
_PROXY = r'records\drxmap\proxy\q_goldenbough_lone.dbr'
_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_goldenbough.dbr'
_YARD_PROXY = r'records\drxmap\proxy\q_yard_goldenbough.dbr'
_WORLD_CHEST = r'records\drxmap\proxy\svc_charon_chest.dbr'
_HOARD = [r'records\drxitem\container\svc_charonhoard_%s.dbr' % t
          for t in ('01', '02', '03')]

_AMULET = [r'records\item\equipmentamulet\svc_goldenbough_%s.dbr' % t
           for t in ('n', 'e', 'l')]
_SUMMON = r'records\skills\soulskills\summon_charon_oarsman.dbr'
_PETS = [r'records\skills\soulskills\pets\charon_oarsman_%d.dbr' % i
         for i in (1, 2, 3)]
_SOUL_BASENAME = 'ferryman'      # LEGACY PATH, frozen for save-compat (TQ bakes
                                 # item paths at pickup; renaming orphans looted souls)
_SOUL_TIERS = [r'records\item\equipmentring\soul\svc_uber\%s_soul_%s.dbr'
               % (_SOUL_BASENAME, t) for t in ('n', 'e', 'l')]
# CORRECTION 11: because the soul PATH is frozen, `_create_soul` layers onto a
# record the monolith already wrote this run. These are the field prefixes whose
# SUPERSEDED values have to be cleared first, or the ferryman's cold/vitality/
# life-leech identity keeps reading in the tooltip under the new fire/pierce one.
# Deliberately the bonus-STAT prefixes only - nothing structural is in reach.
# `itemSkill*` is in the set on purpose: it makes a stale `itemSkillAutoController`
# (the D19/D21 manual-cast law) structurally impossible to inherit.
_DEAD_SOUL_STAT_PREFIXES = ('offensive', 'defensive', 'retaliation', 'character',
                            'augmentSkill', 'itemSkill')
# The Charon identity, named field by field, so verify() can prove it is GONE
# rather than merely prove that the new stats are PRESENT (round 2 only did the
# latter - verify() read `itemNameTag` and nothing else on the tiers).
_DEAD_SOUL_FIELDS = (
    'offensiveColdMin', 'offensiveColdMax', 'offensiveColdModifier',
    'offensiveSlowColdMin', 'offensiveSlowColdDurationMin', 'defensiveCold',
    'offensiveLifeMin', 'offensiveLifeMax',            # vitality damage
    'offensiveLifeLeechMin', 'defensiveLifeLeech',
    'offensiveFearMin', 'offensiveFearMax',
    'offensivePercentCurrentLifeMin', 'offensivePercentCurrentLifeMax',
    'itemSkillAutoController',
)

# ── DONORS (each OWNS the rig its clone renders on - no cross-rig swap) ──────
# EVERY ONE IS D19-MOBILE: its `charAnimationTableName` BINDS `unarmedRunAnim`.
# That is a hard selection criterion, not a happy accident - see CORRECTION 9.
# The round-1 donors `us_hellflower_37` / `am_quillvine_35` are BANNED for any
# placed or summoned body in this encounter: `anm_quilvine.dbr` binds no
# locomotion clip at all, so anything built on it is a statue.
_D_ORM = r'records\xpack\creatures\monster\ascacophus\xhero_strongbark_44.dbr'
_D_BLOOM = r'records\creature\monster\bogdweller\um_emberoak_42.dbr'
_D_BRIAR = r'records\creature\monster\junglecreep\am_junglecreep_41.dbr'
_D_SPLIT = r'records\skills\monster skills\lowhealth_berserkerrage01.dbr'
# The immobile rig this lane REFUSES to place a body on. Named so `verify()` can
# say WHY when it reds, and so a future edit cannot quietly reintroduce it.
_BANNED_ANIM = r'records\creature\monster\quilvine\anm\anm_quilvine.dbr'

_SPLIT = r'records\skills\monster skills\lowhealth\svc_bough_splitting.dbr'

# ── SKILLS (Class verified in the arz; see the header table) ─────────────────
_SK_EARTHBIND = r'records\skills\nature\drx_earthbind.dbr'                 # Skill_AttackRadius r22 cd20
_SK_QUILLWARDS = r'records\skills\monster skills\summoning_pets\quillwards.dbr'  # Skill_DefensiveWall cd20
_SK_THORNYAURA = r'records\skills\boss skills\typhon_thornyaura.dbr'       # Skill_BuffSelfDuration 6.5s
_SK_MEGABURST = (r'records\skills\monster skills\attack_projectile'
                 r'\razorquill_megaburst.dbr')                             # Skill_AttackProjectileFan
_SK_NOVA = r'records\skills\monster skills\attack_radius\razorquill_nova.dbr'  # Skill_AttackProjectileRing
_SK_BOSS_SCALING = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
_SK_HERO_SCALING = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'
_SK_HPSCALING = r'records\xpack\skills\bossskills\all_hpscaling_passive.dbr'
_SK_CONVIMMUNE = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_SK_HEART_OF_OAK = r'records\skills\nature\drxheartofoak.dbr'              # Skill_BuffRadiusToggled
_SK_PLAGUE = r'records\skills\nature\drxplague.dbr'                        # Skill_AttackBuff
# CORRECTION 17 - the Handbriar's cast. Skill_AttackProjectile, physical +
# `offensivePierceRatioMin 50`; its 7 live carriers are `quillvine_01..06`, i.e.
# THE VERY BODIES the boss's own quillwards wall and hero_quillvines retinue put
# on the field. `_DEAD_BRIAR_SKILL` is the donor's native beetle-bile burst it
# replaces, named so verify() can prove it is gone rather than only that the barb
# is present.
_SK_QUILLBARB = r'records\xpack\skills\monsterskills\summoning\quillvine_barb.dbr'
_DEAD_BRIAR_SKILL = (r'records\skills\monster skills\attack_projectile'
                     r'\beetlebile_vomitbile.dbr')
_BRIAR_BARB_LEVEL = [4, 5, 6]     # inside the record's SIX-entry array; cannot mis-index
# CORRECTION 18 - the difficulty rows the soul pets are supposed to carry (the
# SHIPPED pet shape, restored). `hero_scaling` is the incumbent they inherited
# from the emberoak source and that a player's permanent pet has no business
# carrying; the swap asserts it before overwriting, exactly as `_swap_scaler`
# does on the two boss forms.
_SK_HERO_SCALING_PET_INCUMBENT = _SK_HERO_SCALING
_GP = r'records\skills\monster skills\globalproperties_%s01.dbr'
_PET_DIFFICULTY_ROWS = ((_GP % 'normal', [1, 0, 0]),
                        (_GP % 'epic', [0, 1, 0]),
                        (_GP % 'legendary', [0, 0, 1]))

# ── THE GRANTED SUMMON'S OWN PLAYER SURFACES (CORRECTION 12) ────────────────
# The summon skill is the thing on the player's SKILL BAR every time they cast
# the soul, so R-125's player-surface law names its icon explicitly. Round 2
# shipped it still wearing Charon's drowned-ghost glyph and the Lyia-clone
# Maenad cast sound under the name "Graft the Burning Heartwood".
#   ICON: retargeted at the SOURCE OF TRUTH - `_SUMMON_SKILL_ICON` in
#     apply_svc_patches.py, keyed 'summon_charon_oarsman' - so the monolith's own
#     earlier build of this skill is correct too and there is no second writer to
#     drift. `flamewave{up,down}` is a fire glyph with **0 references across every
#     string field of all 51,253 records** (no other summon AND no other granted
#     skill - stronger than every established row in that table, which all share
#     with a live skill), and both halves are PRESENT in the shipped
#     DRXtextures.arc under `skill icons/soul/`. Mirrored here ONLY so verify()
#     can prove the end state without importing a private table's semantics.
#   HIT SOUND: `_build_boss_summon` never writes it, so every boss summon it
#     builds inherits Lyia's Maenad pak (MEASURED: 31 of the 52 soul summons in
#     the DB carry `maenadalertpak` - a CLASS-wide residue, registered as
#     BL-BOUGH-DEBT-9, not invented by this lane). This lane fixes ITS OWN, using
#     the established `<family>alertpak` convention the fixed summons already use
#     (mummy/zombie/chimera/hydra): the terminal donor `um_emberoak_42` declares
#     `alertSound = ...\bogdwelleralertpak.dbr` on its own record.
_SUMMON_ICON = (r'DRXtextures\skill icons\soul\flamewaveup.tex',
                r'DRXtextures\skill icons\soul\flamewavedown.tex')
_SUMMON_HIT_SOUND = r'records\sounds\soundpak\monstersorient\bogdwelleralertpak.dbr'
_DEAD_ICON_TOKEN = 'drownedspirit'      # Charon's ghost glyph: 3 carriers DB-wide
_DEAD_SOUND_TOKEN = 'maenadalertpak'    # the Lyia-clone residue

# ── FX: monster-record fields ONLY. All four verified Class == EffectEntity ──
_FX = r'records\xpack\effects\particles\creature'
_FX_ORM_SPAWN = _FX + r'\ascacophus2_ambientfx.dbr'
_FX_ORM_DEATH = _FX + r'\ascacophus2_deathfx.dbr'      # the trunk bursting = the phase turn
_FX_BLOOM_SPAWN = _FX + r'\ascacophus_ambientfx.dbr'
_FX_BLOOM_DEATH = _FX + r'\ascacophus_deathfx.dbr'

_ORB = r'records\xpack\item\containers\proxies\bosschest02_charon.dbr'   # see CORRECTION 4

# ── MESHES (per-rig; each is its own donor's, so A9 is satisfied by construction)
_MESH_ORM = r'XPack\Creatures\Monster\Ascacophus\Ascacophus02.msh'
_MESH_BLOOM = r'DRX\meshes\emberoakmesh.msh'
_MESH_BRIAR = r'Creatures\Monster\JungleCreep\JungleCreep01.msh'
_SKIN_ORM = r'XPack\Creatures\Monster\Ascacophus\Ascacophus01B.tex'      # donor's own, 3 live carriers
# WILL-DECISION 3, shipped OFF: the DRX dead-trunk skin's only live baseTexture
# carrier is `um_deadtrunk_45`, which renders on `deadtrunk.msh` - a DIFFERENT
# mesh from Ascacophus02. Cross-mesh UV is the 343_dark_smoke / Vort-green trap,
# so this ships off behind a constant and needs a TESTHUB confirmation before any
# colour claim is made. (`um_deadtrunk_45` was also evaluated as an alternative
# phase-1 donor this round - Plant, D19-mobile at rs 1.10, and it owns the skin -
# and rejected only because `xhero_strongbark_44` brings `hero_quillvines`, the
# own-family retinue the R-125 bar wants, and the deadtrunk does not.)
_ORM_SKIN_ALT = r'DRXtextures\creatures\ascacophus\ascacophus_deadtrunk.tex'
_ORM_USE_SKIN_ALT = False

# ── THE NUMBERS ─────────────────────────────────────────────────────────────
_BAND = [48, 72, 100]
# DURABILITY, CALIBRATED - see CORRECTION 10. Round 1 justified its numbers as
# "exact parity with the shipped Charon forms", which was never itself calibrated
# against anything and landed at 58,000 on Epic. The reference frame this lane was
# told to use is docs/reports/gaoler_variance_rca.md: Alkyoneus the Soul-Gaoler is
# 15,000/20,000/27,000 + 11,000/15,000/20,000 = 26,000 / 35,000 / 47,000 across
# two forms, PLUS a six-strong guard horde, and the RCA's verdict on him is
# hard-but-fair and killable ("no action warranted", beaten on attempt two).
#
#   this encounter   27,000 / 35,000 / 46,000  (two forms + two Champions)
#   the Gaoler       26,000 / 35,000 / 47,000  (two forms + six guards)
#
# Epic matched exactly. NO WALLS, and this fight is deliberately gentler than the
# Gaoler on the two levers his RCA identified as the real ones: it has no 25%
# racial pet-damage reduction and no life-drain cascade. The wall in this fight is
# literal, made of quillvines, and has a cooldown.
_ORM_LIFE = [13000.0, 17000.0, 22000.0]
_BLOOM_LIFE = [14000.0, 18000.0, 24000.0]
# MOBILITY (CORRECTION 9). Written EXPLICITLY on all three bodies: two of the
# three donors sit at the roster's median 1.0 and the encounter needs to be able
# to close. Measured Boss-uber band on the live arz: min 0.35, median 1.00,
# max 4.00. The shipped Charon forms ran 2.8 and 4.0 - the two fastest bodies in
# the whole 53-boss roster - and this encounter deliberately does not chase that.
_ORM_SPEED = 1.35     # RIG-PROVEN: credits_ringlesstree ships 1.35 on Ascacophus02.msh
_BLOOM_SPEED = 1.45   # above this rig's only live carrier (1.0); disclosed, see BL-BOUGH-DEBT-5
_BRIAR_SPEED = 1.30   # RIG-PROVEN: um_speckledjim_45 ships 1.30 on JungleCreep01.msh
# WILL-DECISION 2: ship 2.8 / 2.0; TESTHUB yard sweep 3.1 and 3.4 before the
# canonical placement is blessed. Measured live scale ranges on the exact rigs:
# Ascacophus02.msh 1.15..1.80 (max = kaets.dbr, a Quest-class DRX crow hero);
# emberoakmesh.msh 1.90 on its single carrier, so the 2.0 ask is a 1.05x stretch
# (the round-1 hellflower would have been 1.33x); JungleCreep01.msh 0.70..1.60,
# so 1.55 is INSIDE proven range. Large scales DO work here (um_polisgaoler_99
# ships Gigantes02 at 3.5, um_vashkarr_99 at 3.0) so the residual risk is
# footprint/clearance, not the renderer - and only phase 1 carries it.
_ORM_SCALE = 2.8
_BLOOM_SCALE = 2.0
_BRIAR_SCALE = 1.55
# THE R-100 #18 FIX, and the anti-regression gate's reason to exist: the shipped
# escort was [878.0, 300.0, 400.0] - life FALLING from Normal to Epic. Sized off
# the live Champion-escort roster (svc_tantalus_famishedshade_90 = 4500/6500/9000,
# svc_obs_escort_bonehallow = 7671/9589/11507): two of these, not six.
_BRIAR_LIFE = [5000.0, 7000.0, 9500.0]

# ── BEAT 2's PAYLOAD, AUTHORED RATHER THAN INHERITED (CORRECTION 14) ─────────
# `lowhealth_berserkerrage01` is `DefensiveMastery_Adrenaline` and carries THREE
# non-zero level arrays. A verbatim clone wired at level 10 therefore shipped
# 36% flat damage absorption + 8/s life regen + 60% physical damage for the whole
# last third of phase 1, none of it stated anywhere - directly under this lane's
# repeated claim of EXACT Gaoler durability parity. All three are now written as
# FLAT 20-row arrays, so the value is level-index-proof and `verify()` can prove
# every row rather than just the one the current wiring happens to read.
_SPLIT_LEVEL = 10        # the wired skillLevel on phase 1 (donor skillMaxLevel 15)
_SPLIT_ROWS = 20         # the donor's array length; keep the shape, author the value
_SPLIT_ABSORB = 0.0      # was [10..65], idx9 = 36.0 -> a wall the claim did not mention
_SPLIT_REGEN = 0.0       # was [5..11],  idx9 =  8.0 -> a boss healing in its own last third
_SPLIT_PHYSMOD = 35.0    # was [15..110], idx9 = 60.0 -> KEPT, AUTHORED, DISCLOSED
# CORRECTION 19 (round-5 vet): round 4 authored all THREE of the donor's stat
# arrays and left its FACE. The record still shipped the player Defense-mastery
# Adrenaline buff aura (`Skill_Adrenaline_FX01` + `Buff07`) under a beat this
# round is NAMED after - "the bark comes apart and the thorns come out". Same
# donor-payload defect class as CORRECTION 14, on the visual dimension.
# Repointed onto the FX of the mechanic the beat actually grants: retaliation
# pierce = thorns. `Typhon_Thorn_CharFXPak` is the value `typhon_thornyaura`
# already ships in all three of its own FX fields, and this module already wires
# that skill onto the terminal - so the value is proven live in THIS build, and
# it is base-resolved exactly like the Adrenaline value it replaces (neither is
# present in the mod arz; measured). No new art asset, no new resolution class.
# NOT a crash-law surface: `svc_bough_splitting` is Skill_PassiveOnLifeBuffSelf,
# never a Skill_SpawnPet, and no monster record gains a charFxPak field.
_SPLIT_FX = r'Records\Effects\Boss Effects\Typhon_Thorn_CharFXPak.dbr'
_SPLIT_ACTOR_NAME = 'Akremon_TheSplitting'
_DEAD_SPLIT_FX_TOKENS = ('adrenaline', 'buff07')   # the donor's identity, gated out

# ── ORDINARY LOOT: the ACT-4 BAND this encounter's tier actually uses ────────
# CORRECTION 15. Measured peers at the same tier: `um_polisgaoler_unbound_99`
# (the very boss this lane calibrates durability against) runs
# `01/02/03_act4_relics` + `01/02/03_act4_arcaneformulae`, and PHASE 1 of this
# encounter already ran `n_04_unique_all` + `04_*_misc` + act-4 relics/formulae
# off the strongbark donor. Only the TERMINAL was a full act low, because the
# emberoak donor is a DRX act-2/3 creature.
_LT = r'records\item\loottables'
_XLT = r'records\xpack\item\loottables'
_ACT4_UNIQUE = [_LT + r'\raremisc\%s_04_unique_all.dbr' % t for t in ('n', 'e', 'l')]
_ACT4_MISC = [_LT + r'\raremisc\mastertables\04_%s_misc.dbr' % t for t in ('n', 'e', 'l')]
_ACT4_RELICS = [_XLT + r'\relics\0%d_act4_relics.dbr' % i for i in (1, 2, 3)]
_ACT4_FORMULAE = [_XLT + r'\arcaneformulae\0%d_act4_arcaneformulae.dbr' % i
                  for i in (1, 2, 3)]
# The terminal donor's own act-2/3 rows, retargeted onto the band above.
_BLOOM_LOOT_RETARGET = (('lootMisc1Item1', _ACT4_UNIQUE),
                        ('lootMisc2Item3', _ACT4_MISC),
                        ('lootMisc3Item1', _ACT4_RELICS),
                        ('lootMisc3Item2', _ACT4_FORMULAE),
                        ('lootMisc3Item3', _ACT4_MISC))
# ...and the two act-3 crafting rows that are simply wrong at the Styx. A jungle
# root does not fall off a burning tree in Hades; muted by WEIGHT, so nothing is
# orphaned and the row can be restored in one line.
_BLOOM_LOOT_MUTE_WEIGHTS = ('chanceToEquipMisc1Item5', 'chanceToEquipMisc2Item5')
# Any table basename matching one of these is BELOW this encounter's band. The
# gate reads the FINAL record, so a future donor swap that re-lowers the band
# reds instead of shipping quietly.
_UNDERBAND_TOKENS = ('_03_unique_all', '_02_unique_all', '_01_unique_all',
                     '03_n_misc', '03_e_misc', '03_l_misc',
                     '02_n_misc', '02_e_misc', '02_l_misc',
                     '_act1_', '_act2_', '_act3_',
                     'relic_15-21', 'relic_41-45', 'relic_57-61',
                     'jungleroot')
# CORRECTION 16, WILL-DECISION 7: the transform SHELL pays no ordinary Misc loot,
# which is the shipped Charon shell's own shape. Flip to False to restore the
# strongbark donor's 75/13/1.6 roll (Mnemophage-shell parity) in one line.
_ORM_MUTE_MISC = True
# ── CORRECTION 20 (round-5 vet P1): THE OTHER HALF OF THE SAME MUTE ──────────
# CORRECTION 16 measured and muted the SHELL and never looked at the TERMINAL,
# and CORRECTION 15 re-banded the terminal's TABLES without touching its CHANCES,
# which are the volume. MEASURED pre/post apply on the live build83 arz:
#
#   SHIPPED  um_charon_ferryman_99       chanceToEquipMisc1/2/3 = 0 / 0 / 0
#   SHIPPED  um_charonform2_ferryman_99  chanceToEquipMisc1/2/3 = 0 / 0 / 0  (+Misc4 100 = the Bough)
#   ROUND-4  um_charonform2_ferryman_99  chanceToEquipMisc1/2/3 = 1.6 / 100.0 / 75.0
#
# i.e. a GUARANTEED potion plus an act-4 misc roll every kill and a 75% relic /
# formula roll, inherited verbatim from the `um_emberoak_42` re-clone, never
# written or examined by this module - so the encounter's ordinary loot volume
# went 0 -> 176.6 while R-231-G #3 stated in writing that it did not move, on
# the exact promise the concurrent b84 `fix/loot-volume-trim` lane was handed.
#
# THE RULING (mute, not keep). 176.6 is defensible on peer parity - it is EXACTLY
# um_ephialtes_99 / um_mnemophage_99 / um_helepolis_99, against a 53-boss roster
# whose median is 4.5 - so this is not a correctness fix, it is a DECISION, and
# it is recorded as one. Muted because: (a) the SHIPPED encounter paid exactly
# zero, and this lane's whole discipline is zero balance drift so the vet's job
# stays identity rather than numbers; (b) it keeps the written coordination
# statement to b84 TRUE as issued instead of correcting a promise another
# in-flight lane is relying on; (c) the encounter's payout is DESIGNED as the
# guaranteed Golden Bough (Misc4 100%) + the dedicated hoard chest + the soul +
# the boss orb, and ordinary Misc rolls were never part of it. Misc4 is NOT
# touched. Flip to False to restore full donor parity in one line.
_BLOOM_MUTE_MISC = True
_MUTED_MISC_SLOTS = (1, 2, 3)          # Misc4 = the Golden Bough, never touched
# The retinue's inherited faucet, DISCLOSED rather than claimed away (round-5 vet
# P3). Phase 1 keeps `hero_quillvines` as its R-125 own-family retinue; MEASURED,
# its six spawns `records\xpack\skills\monsterskills\summoning\pets\quillvine_01
# ..06.dbr` each ship `dropItems 1` + `chanceToEquipMisc1 3.0` on the act-3 table
# `01_act3_vinygrowth.dbr`. Those are SHARED BASE-GAME records used by the stock
# ascacophus heroes, so mutating them is out of this lane's scope - but the claim
# "this wave does not raise the encounter's ordinary loot volume" is only true of
# the records this wave OWNS, and that is now how it is written. verify() reads
# these six and asserts the disclosed number so the hole cannot widen unseen.
_RETINUE_PETS = [r'records\xpack\skills\monsterskills\summoning\pets'
                 r'\quillvine_0%d.dbr' % i for i in range(1, 7)]
_RETINUE_PET_MISC1 = 3.0
_RETINUE_PET_TABLE = 'vinygrowth'

# ── MANA: the signature levers must not run dry (round-5 vet P2) ─────────────
# MEASURED post-apply, round 4: phase 1 carried `characterMana 3000` and
# `characterManaRegen 0.0`, both INHERITED from `xhero_strongbark_44` and never
# written, against a wired rotation costing 312.0 (drx_earthbind 172.0 +
# quillwards 140.0 at level 8; stumpstomp / hero_quillvines / razorquill_megaburst
# are free). 3000 / 312 = ~9.6 cycles, after which BOTH of the fight's signature
# levers are dead for the rest of the encounter and the headline claims ("ZERO
# other uber fields a Skill_DefensiveWall", "you cannot kite this fight") degrade
# to "for the first ten casts". The terminal was worse and the vet did not reach
# it: mana 1177 / regen 5.0 against a 417.0 rotation = ~2.8 cycles.
# ROSTER CONTEXT: 46 of 53 Boss ubers carry mana-costing casts and only 2 run
# regen <= 0. The calibration reference `um_polisgaoler_99` is 3000 + 2.0 against
# a 326 rotation; the Charon this replaces ran 8000 + 50.0.
# THE RULE, not a guess: pool = the Gaoler's 3000 on both forms, and regen sized
# so ONE full rotation is funded across the 20s cooldown that spaces it, i.e.
# regen >= rotation_cost / _MANA_CYCLE_SECONDS. verify() recomputes the rotation
# cost off the FINAL record at the FINAL wired levels and reds if a future skill
# or level retune outruns the pool, so this number can never silently rot.
# This is NOT a durability wall: mana regen adds zero effective HP, it only keeps
# the boss casting the things that make it this boss, and both numbers stay far
# under the shipped Charon's 8000 / 50.0.
_MANA_CYCLE_SECONDS = 20.0        # both signature casts are skillCooldownTime 20.0
_ORM_MANA = 3000.0                # the donor's own pool, = the Gaoler's
_ORM_MANA_REGEN = 16.0            # funds 312.0 / 20s = 15.6
_BLOOM_MANA = 3000.0              # raised from the inherited 1177 to phase-1 parity
_BLOOM_MANA_REGEN = 21.0          # funds 417.0 / 20s = 20.85

# ── THE CC / ELEMENTAL PROFILE, AUTHORED AND PINNED (round-5 vet P2) ─────────
# Round 4 changed the whole crowd-control profile silently. MEASURED, record
# block plus skill grants at the wired levels:
#
#   SHIPPED both forms  Stun 100  Freeze 100  Petrify 100  Trap 80  Cold 60 Fire 30
#   ROUND-4 phase 1     Stun  50  Freeze   0  Petrify 150  Trap  0  Cold -30 Fire -30
#   ROUND-4 terminal    Stun 300  Freeze   0  Petrify 100  Trap  0  Cold -30 Fire  70
#
# Two defects in one: freeze-lock became available on both forms where the
# shipped encounter was immune, and the TERMINAL simultaneously inherited a hard
# 300% STUN WALL off `hero_fire` on a wave whose CORRECTION 10 headline is
# "NO WALLS" and whose round-4 thesis is "a donor's own payload riding along
# under a claim that did not mention it". Nothing said so anywhere.
#
# THE FIX. (1) `hero_fire` is dropped from the terminal - it is a SHARED base
# record so it is never mutated, it is swapped out of its declared slot for
# `elementalresistance_10xlevel`, and the +40 fire it used to hand over is
# authored on the record instead. (2) An explicit CC floor is authored on BOTH
# forms so the profile is a decision, not a residue. (3) verify() recomputes the
# EFFECTIVE value (record + every skill grant at its wired level) and asserts it
# equals these targets, so the whole axis is pinned against any future donor,
# skill or level change.
# The values are deliberately RESISTANT, NOT IMMUNE: an uber that a Warfare
# player can perma-stun is not a fight, and a 100 wall is the shipped Charon's
# answer that this lane rejected. 75 / 60 / 60 leaves every CC build a real but
# non-trivial opening.
_CC_TARGET = {'defensiveStun': 75.0, 'defensiveFreeze': 60.0, 'defensiveTrap': 60.0}
# DISCLOSED, deliberate, and gated to the same table: Petrify lands at 150 on
# phase 1 and 100 on the terminal, entirely from `boss_conversionimmunity` (+100)
# and `ascacophus_bleeddamageimmunity` (+50) - both roster-standard uber skills,
# and conversion immunity is the thing that stops a player converting the boss.
# That one axis IS a wall, it is inherited roster-wide rather than authored here,
# and it is written down rather than discovered by the next vet.
_PETRIFY_EFFECTIVE = {'_ORM': 150.0, '_BLOOM': 100.0}
# ELEMENTAL, and the second half of the fight's build-swap shape. `racial_plant`
# hands both forms -30 cold and -30 fire. On phase 1 that is left ALONE and
# promoted from accident to design: the tree burns. On the terminal - which IS
# the fire - the record carries enough to land at +70 after the racial. So the
# player who brings fire to beat 1 has to bring something else to beat 3, which
# is the same inversion the bleed immunity already does in the other direction.
_ORM_FIRE_EFFECTIVE = -30.0       # record 0 + racial_plant -30. DELIBERATE weakness.
_ORM_COLD_EFFECTIVE = -30.0
_BLOOM_FIRE_RES = 100.0           # record 100 + racial -30 = +70 effective
_BLOOM_FIRE_EFFECTIVE = 70.0
_BLOOM_COLD_EFFECTIVE = -30.0
# MEASURED declared paths on the donors (slot 13 on the emberoak, slot 15 on the
# strongbark). The replacement is the strongbark's OWN elemental passive, so the
# terminal gains a skill this encounter already fields on its other form rather
# than an import: +10 elemental, no CC grant of any kind, Class Skill_Passive.
_DEAD_BLOOM_SKILL_FIRE = (r'records\skills\monster skills\passive_buffs\resists'
                          r'\hero_fire.dbr')
_SK_ELEMRESIST = (r'records\xpack\skills\monsterskills\passive'
                  r'\elementalresistance_10xlevel.dbr')
_SK_RACIAL_PLANT = (r'records\skills\monster skills\passive_buffs\resists'
                    r'\racial_plant.dbr')

# ── SOUL STAT BANDS: every authored number proved against its own peers ──────
# Round-5 vet P1, generalised. The reported defect was ONE field written with the
# wrong NAME; measuring the whole authored block the way the fix demanded found
# THREE numbers outside the live peer band, two of which nobody had reported.
# Scope = the 2,453 records under `records\item\equipmentring\soul`.
#
#   characterRunSpeed          -8 / -6 / -5   band [0.00, 1.28], 2,158 carriers,
#                                             ZERO negative. WRONG FIELD: this is
#                                             the creature LOCOMOTION scalar. The
#                                             item movement-percent field is
#                                             `characterRunSpeedModifier` (2,224
#                                             carriers, 155 negative, band
#                                             [-28.00, 45.00]) - and
#                                             `mnemophage_soul_{n,e,l}`, the mod's
#                                             own hand-designed uber soul and this
#                                             one's direct roster neighbour, ships
#                                             EXACTLY -8 / -6 / -5 there. So the
#                                             intended penalty did not exist AND a
#                                             negative absolute run speed shipped
#                                             on a permanently-equipped item.
#   offensiveSlowPhysicalMin   22 / 31 / 40   band [0.00, 8.00] - 5x the live max,
#                                             and only 3 of 2,095 carriers are
#                                             even non-zero.
#   offensiveSlowPhysicalDur.  3.0            band [0.00, 0.00] - EVERY one of the
#                                             2,095 carriers ships 0.0. The field
#                                             family is inert across the mod.
#
# So the "one weird stat" was writing into a dead field family at 5x its ceiling.
# The field the mod ACTUALLY uses for snare-on-hit is `offensiveSlowRunSpeed*`:
# 46 non-zero carriers, band [0.00, 79.00] with durations [0.00, 4.00], and the
# top of that list is exactly the hand-designed souls (thebloatedone 79.0 / 4.0s,
# meglograi 75.0 / 3.0s, camelbane 71.0 / 4.0s). That is literally "the ground
# takes hold of whatever you strike", it is in the same company this soul belongs
# in, and it is in band by construction.
_SOUL_SNARE = 58.0                       # legendary tier; peers run to 79.0
_SOUL_SNARE_DURATION = (2.0, 2.5, 3.0)   # peers use 2.0 - 4.0
_SOUL_RUNSPEED_PENALTY = {'n': -8.0, 'e': -6.0, 'l': -5.0}   # = mnemophage_soul_*
# The scope verify() measures the band over, and the fields it refuses to accept.
_SOUL_PEER_ROOT = r'records\item\equipmentring\soul'
# `characterRunSpeed` is the creature locomotion field; an ITEM must never carry
# it. `offensiveSlowPhysical*` is the dead family above. Both are gated by NAME
# so the class of defect cannot come back under a different number.
_BANNED_SOUL_FIELDS = ('characterRunSpeed', 'offensiveSlowPhysicalMin',
                       'offensiveSlowPhysicalMax',
                       'offensiveSlowPhysicalDurationMin',
                       'offensiveSlowPhysicalDurationMax')

# `actorHeight` is a per-RIG constant, inherited, NEVER invented (R-126, measured
# over 2,122 rigs). Ascacophus02 = 0.0 on all 4 live carriers; emberoakmesh.msh
# and JungleCreep01.msh = 1.0. This module NEVER writes the field; verify() proves
# it, and reads the value off each body's OWN DONOR rather than a hard-coded map,
# so a future donor swap cannot leave a stale constant behind.
_RIG_ACTOR_HEIGHT = {_ORM: 0.0, _BLOOM: 1.0, _BRIAR: 1.0}

# ── TAGS ────────────────────────────────────────────────────────────────────
# KEYS KEPT wherever a key already exists (nothing referenced is retired, so
# validate_tags cannot be handed an orphan); exactly ONE new key is minted, and
# it fixes a real defect: the two shipped forms SHARED one display tag, so the
# phase turn had no name change at all.
_TAG_ORM = 'tagSVCMonsterCharonFerryman'        # KEY KEPT, string rewritten
_TAG_BLOOM = 'tagSVCMonsterAkremonBlaze'        # MINTED (the two forms now differ)
_TAG_BRIAR = 'tagSVCMonsterCharonWraith'        # KEY KEPT, string rewritten
# CORRECTION 8: every display name this module mints is checked against the live
# record namespace by verify(). "Ormenos" - the ratified spec's choice - failed
# that check: it is the China Telkine, 59 records deep, with its own soul.
_NAME_TOKENS = ('akremon', 'handbriar')
_TAG_HOARD = 'tagSVCCharonHoard'                # KEY KEPT, string rewritten
_TAG_SOUL = 'tagSVCSoulFerryman'                # KEY KEPT (in _HAND_DESIGNED_SOUL_TAGS)
_TAG_SUMMON = 'tagSVCSummonCharonOarsman'       # KEY KEPT, string rewritten
_TAG_PET = 'tagSVCPetOarsman'                   # KEY KEPT, string rewritten
_TAG_AMULET = 'tagSVCitmGoldenBough'            # UNCHANGED
_TAG_AMULET_DESC = 'tagSVCitmGoldenBoughDESC'   # rewritten
# R-231-G #4 - the player surface nobody had flagged: the Helos/TESTHUB traveler
# NPC that SENDS the player to this forecourt is named through the tags pipeline
# and still read "Traveler: Golden Bough (Charon)" after three rounds. The string
# is retargeted at its source of truth (`HELOS_HUB_OUTBOUND` in the monolith); the
# KEY and the record path stay frozen, so the TESTHUB map's place-by-name still
# resolves and no map rebuild is implied. Mirrored here only so verify() can prove
# the end state without importing a private table.
_TAG_TRAVELER = 'tagSVCNpcTravCharon'

_REQUIRED_DONORS = (_D_ORM, _D_BLOOM, _D_BRIAR, _D_SPLIT)
_REQUIRED_SKILLS = ((_SK_EARTHBIND, _SK_QUILLWARDS, _SK_THORNYAURA, _SK_MEGABURST,
                     _SK_NOVA, _SK_BOSS_SCALING, _SK_HPSCALING, _SK_CONVIMMUNE,
                     _SK_HEART_OF_OAK, _SK_PLAGUE, _SK_QUILLBARB)
                    + tuple(p for p, _lv in _PET_DIFFICULTY_ROWS))
_REQUIRED_LOOT = tuple(_ACT4_UNIQUE + _ACT4_MISC + _ACT4_RELICS + _ACT4_FORMULAE)
_REQUIRED_FX = (_FX_ORM_SPAWN, _FX_ORM_DEATH, _FX_BLOOM_SPAWN, _FX_BLOOM_DEATH)

# Populated by apply(); read by verify() so the gate proves the ACTUAL writes.
_TOUCHED = set()


# ── helpers ─────────────────────────────────────────────────────────────────
def _n(s):
    return str(s).replace('/', '\\').strip().lower() if s else ''


def _one(db, rec, field):
    v = db.get_field_value(rec, field)
    return v[0] if isinstance(v, list) else v


def _replace_record(db, donor, dest):
    """clone donor -> dest, SAFELY, over an existing record.

    `ArzDatabase.clone_record` only deep-copies the decoded field map when the
    SOURCE is already in `_decoded_cache`; otherwise it rewires the raw blob and
    leaves any STALE `_decoded_cache[dest]` in place, so the very next
    `get_fields(dest)` would hand back the OLD record's fields and every write
    below would land on Charon. Forcing the source to decode first makes the
    deep-copy branch the only branch taken. Then prove it landed.
    """
    db.get_fields(donor)                      # guarantee source is cached
    db.clone_record(donor, dest)
    db._decoded_cache.pop(dest, None)         # belt AND braces: force a re-read
    got, want = _n(_one(db, dest, 'mesh')), _n(_one(db, donor, 'mesh'))
    if got != want:
        raise SystemExit(
            "charon_rework: clone of %s -> %s did not land (mesh %r, expected "
            "%r). The arz clone/cache seam moved; stop and re-measure."
            % (donor, dest, got, want))
    _TOUCHED.add(_n(dest))
    return dest


def _sf(db, rec, field, value, dtype=None):
    """set_field with the dtype-preservation law: NEVER pass an explicit dtype on
    a field the clone already carries (INT/FLOAT corruption silently zeroes it).
    An explicit dtype is passed ONLY when the field is genuinely absent."""
    if dtype is not None and db.get_field_value(rec, field) is None:
        db.set_field(rec, field, value, dtype)
    else:
        db.set_field(rec, field, value)
    _TOUCHED.add(_n(rec))


def _cast(db, rec, suffix, skill, chance, rng, delay, timeout):
    """Wire one AI cast slot. suffix '' = specialAttackSkillName (slot 1)."""
    _sf(db, rec, 'specialAttack%sSkillName' % suffix, skill, S)
    _sf(db, rec, 'specialAttack%sChance' % suffix, float(chance), F)
    _sf(db, rec, 'specialAttack%sRange' % suffix, rng, S)
    _sf(db, rec, 'specialAttack%sDelay' % suffix, float(delay), F)
    _sf(db, rec, 'specialAttack%sTimeout' % suffix, float(timeout), F)


def _swap_scaler(db, rec, slot=12):
    r"""CORRECTION 13 - hero_scaling -> boss_scaling, ASSERTED, never blind.

    Round 2 wrote `skillName12` unconditionally on both boss forms and never
    checked the incumbent, while declaring a `_SK_HERO_SCALING` constant it then
    referenced nowhere - the intent to verify the swap existed and was never
    implemented. MEASURED across the donors this lane has used: both current boss
    donors (`xhero_strongbark_44`, `um_emberoak_42`) carry `hero_scaling` at
    slot 12, but the ESCORT donor `am_junglecreep_41` carries
    `globalproperties_legendary01` in the same slot. One future donor swap would
    therefore have silently destroyed a difficulty row with a GREEN gate.

    HONEST SCOPE, so nobody reads this as a balance fix: `globalproperties_*` rows
    carry only `characterBaseAttackSpeedTag` plus UI bitmaps - no stat or
    resistance scaling - and 8 of the 53 Boss-class mod ubers declare none at all,
    so the shipped shape (phase 1: normal01 + epic01; terminal: none) is well
    inside the roster norm and the gameplay impact is nil. This is a latent-trap
    fix, not a numbers change.
    """
    field = 'skillName%d' % slot
    cur = _one(db, rec, field)
    if _n(cur) != _n(_SK_HERO_SCALING):
        raise SystemExit(
            "charon_rework: expected the donor's %s on %s to be hero_scaling "
            "(%s) before swapping in boss_scaling, but it is %r. Overwriting a "
            "slot blind is how a difficulty/globalproperties row gets destroyed "
            "with a green gate - re-measure the donor's slot map, then either "
            "move the scaler or use _svc_add_skill and strip hero_scaling "
            "explicitly." % (field, rec, _SK_HERO_SCALING, cur))
    _sf(db, rec, field, _SK_BOSS_SCALING)


def _swap_declared_skill(db, rec, incumbent, replacement, level, why):
    r"""CORRECTION 17/18 - replace a DECLARED `skillName*` entry, ASSERTED.

    The generalisation of `_swap_scaler`: find the slot that currently holds
    `incumbent`, prove it is there, then write `replacement` + its level into that
    exact slot. Never scans for a free slot and never overwrites blind, so a donor
    swap that moved the kit reds loudly instead of destroying a live row with a
    green gate. Returns the slot index.
    """
    for i in range(1, 25):
        if _n(_one(db, rec, 'skillName%d' % i)) == _n(incumbent):
            _sf(db, rec, 'skillName%d' % i, replacement)
            _sf(db, rec, 'skillLevel%d' % i, level)
            return i
    have = sorted(_n(_one(db, rec, 'skillName%d' % i)) or ''
                  for i in range(1, 25))
    raise SystemExit(
        "charon_rework: expected %s to declare %s so it could be replaced by %s "
        "(%s), but no skillName slot carries it. Declared: %s. The donor's kit "
        "moved - re-measure before writing anything into a slot."
        % (rec, incumbent, replacement, why, [h for h in have if h]))


def _flat(value, rows=_SPLIT_ROWS):
    """A level array whose every row is the same authored number.

    CORRECTION 14. The donor ships 20-row LEVEL ARRAYS; a clone wired at level N
    silently inherits row N-1. Writing the same value into every row keeps the
    record's shape (so nothing mis-indexes at any wired level, now or after a
    future retune) while making the number this module's, not the donor's.
    """
    return [float(value)] * int(rows)


def _restore_pet_difficulty_rows(db, pet):
    r"""CORRECTION 18 - the SHIPPED pet shape, restored, incumbent asserted.

    `_build_boss_summon` -> `_update_existing_fields` overwrites the Lyia
    baseline's skill slots from the SOURCE monster, so the three soul pets took
    the emberoak's `hero_scaling` at slot 12 and lost `globalproperties_normal01`
    / `_epic01` at 10/11 - rows the SHIPPED oarsman pets carried. Gameplay impact
    is nil (those rows hold only `characterBaseAttackSpeedTag` plus UI bitmaps,
    CORRECTION 13), but a monster's hero scaler on a player's permanent pet is
    residue, and `_swap_scaler`'s assert-the-incumbent discipline was written for
    exactly this and never applied here.
    """
    _swap_declared_skill(db, pet, _SK_HERO_SCALING_PET_INCUMBENT,
                         _PET_DIFFICULTY_ROWS[0][0], list(_PET_DIFFICULTY_ROWS[0][1]),
                         "a player's permanent pet must not carry a monster's "
                         "hero scaler; the shipped pets carried the three "
                         "globalproperties difficulty rows here")
    for path, lvl in _PET_DIFFICULTY_ROWS[1:]:
        if any(_n(_one(db, pet, 'skillName%d' % i)) == _n(path) for i in range(1, 25)):
            continue
        if not _svc_add_skill(db, pet, path, list(lvl)):
            raise SystemExit(
                "charon_rework: no free skillName slot on the soul pet %s for the "
                "difficulty row %s" % (pet, path))
    _TOUCHED.add(_n(pet))


def _strip_superseded_soul_stats(db, rec, keep):
    r"""CORRECTION 11 - the frozen-path retheme trap, and the fix.

    THE DEFECT, MEASURED after apply() over the live build83 arz: the shipped
    "Soul of the Unferried" stat block SURVIVED UNDERNEATH the new one. Epic tier
    still carried `offensiveCold{Min,Max,Modifier}`, `offensiveSlowCold*`,
    `defensiveCold`, `offensiveLife{Min,Max}` (vitality), `offensiveLifeLeechMin`,
    `defensiveLifeLeech`, `offensiveFear*` and - worst - `offensivePercentCurrentLifeMin`,
    which is the BASE CHARON'S OWN SIGNATURE LEVER (`charon_geyserform1`) and which
    the ratified spec explicitly forbade on this soul. The new fire/pierce stats
    layered ON TOP, so the reward the player keeps forever still read as the
    ferryman on an item called "Soul of the Grasping Root" dropped by a burning
    tree - i.e. the exact complaint that opened this wave, on the one surface a
    player never puts down.

    ROOT CAUSE, STRUCTURAL NOT TYPO: the soul path is FROZEN for save-compat
    (`_SOUL_BASENAME`), so `_create_soul` runs over a record the monolith's
    `_create_goldenbough_boss` already wrote EARLIER IN THE SAME RUN.
    `_create_soul` -> `_ensure_record` is a NO-OP when the record exists, and
    `_set_soul_fields` only ever LAYERS keys. Nothing clears a superseded block.
    Same defect class as the round-2 stale `_SUMMON_PET_BUILDS` registration: a
    superseded writer's output surviving under the new writer's at a frozen path.

    THE FIX, deliberately SURGICAL rather than a blanket wipe. Only the STAT block
    is removed - fields whose name starts with one of the bonus-stat prefixes and
    that this module is not itself about to write. Everything structural (Class,
    templateName, mesh, bitmap, itemLevel, itemNameTag, itemText, itemQualityTag,
    the drop sounds, the relic slot) is untouched, so nothing an earlier or later
    pass owns can be lost. This is the proven monolith idiom (the supra-weapon
    retheme clears exactly these prefixes "so its native element does not bleed
    into the retheme"), and `keep` is passed explicitly so the strip can never
    outrun what `_create_soul` is about to put back.

    Returns the sorted list of stripped field names, for the apply() log.
    """
    ff = db.get_fields(rec)
    if not ff:
        return []
    dead = [k for k in list(ff)
            if k.split('###')[0].startswith(_DEAD_SOUL_STAT_PREFIXES)
            and k.split('###')[0] not in keep]
    for k in dead:
        del ff[k]
    if dead:
        db._modified.add(rec)
        for _cb in db._mutation_listeners:      # keep the shared record index honest
            _cb(rec)
        _TOUCHED.add(_n(rec))
    return sorted(k.split('###')[0] for k in dead)


def _free_cast_slots(db, rec):
    """The cast slots with no SkillName. The engine caps at five: '', 2, 3, 4, 5."""
    out = []
    for sfx in ('', '2', '3', '4', '5'):
        v = _one(db, rec, 'specialAttack%sSkillName' % sfx)
        if not (isinstance(v, str) and v.strip()):
            out.append(sfx)
    return out


# ── apply ───────────────────────────────────────────────────────────────────
def apply(db, tags):
    _TOUCHED.clear()

    missing = [p for p in (_REQUIRED_DONORS + _REQUIRED_SKILLS + _REQUIRED_FX
                           + _REQUIRED_LOOT
                           + (_ORM, _BLOOM, _BRIAR, _POOL, _PROXY,
                              _YARD_POOL, _YARD_PROXY, _ORB))
               if not db.has_record(p)]
    if missing:
        raise SystemExit(
            "charon_rework: %d required record(s) absent from the DB - this "
            "module rewrites an EXISTING encounter in place, so a missing "
            "donor/skill/FX/anchor means the roster moved and the design must be "
            "re-measured, never silently degraded:\n  %s"
            % (len(missing), "\n  ".join(missing)))

    # ── BEAT 2 SKILL: the self-firing splitting, with the thorns folded in ───
    _replace_record(db, _D_SPLIT, _SPLIT)
    _sf(db, _SPLIT, 'FileDescription',
        'Akremon: THE SPLITTING - at 33% life the bark comes apart and the '
        'thorns come out (Skill_PassiveOnLifeBuffSelf, self-firing, no AI wiring)')
    _sf(db, _SPLIT, 'lifeMonitorPercent', 33.0)
    _sf(db, _SPLIT, 'skillActiveDuration', 12.0)
    _sf(db, _SPLIT, 'skillCooldownTime', 5.0)
    # CORRECTION 1: the thorn coat lives HERE, not on a random 20s cast roll.
    # Scalars (level-independent) so the wired skillLevel cannot mis-index.
    _sf(db, _SPLIT, 'retaliationPierceMin', 180.0)
    _sf(db, _SPLIT, 'retaliationPierceMax', 260.0)
    # CORRECTION 14: AUTHOR the donor's three inherited buff arrays instead of
    # riding them. Verbatim, wired at level 10, this record was shipping 36% flat
    # damage absorption + 8/s life regen + 60% physical damage for the entire last
    # third of phase 1 - permanently up (cd 5.0 < duration 12.0) and stated
    # NOWHERE, directly under this lane's claim of exact Gaoler durability parity.
    # Flat 20-row arrays: the shape survives, the number becomes ours, and no
    # future retune of `_SPLIT_LEVEL` can mis-index into a donor value again.
    _sf(db, _SPLIT, 'damageAbsorptionPercent', _flat(_SPLIT_ABSORB))
    _sf(db, _SPLIT, 'characterLifeRegen', _flat(_SPLIT_REGEN))
    _sf(db, _SPLIT, 'offensivePhysicalModifier', _flat(_SPLIT_PHYSMOD))
    # CORRECTION 19: ...and its FACE. Round 4 authored all three of the donor's
    # stat arrays and left `Skill_Adrenaline_FX01` + `Buff07` in place, so the
    # one beat this round is named after rendered the player Defence-mastery
    # Adrenaline buff aura. Repointed onto the FX of the mechanic the beat
    # actually grants - retaliation pierce, i.e. thorns.
    _sf(db, _SPLIT, 'skillActivatedAuraName', _SPLIT_FX, S)
    _sf(db, _SPLIT, 'targetFxPakName', _SPLIT_FX, S)
    # ...and the internal label, which is the last thing on the record still
    # reading `DefensiveMastery_Adrenaline`. Not a render path (the aura is named
    # explicitly by the two fields above, and the repoint is proven by measuring
    # the final record) and not player-facing, but it is the same donor identity
    # and this codebase authors `ActorName` freely (`build_svc_database` writes it
    # on NPCs; `validate_tags` lists it as a non-tag field), so there is no reason
    # to leave it.
    _sf(db, _SPLIT, 'ActorName', _SPLIT_ACTOR_NAME, S)

    # ── BEAT 1: AKREMON, THE GRASPING ROOT (phase 1, the placed head) ───────
    _replace_record(db, _D_ORM, _ORM)
    _sf(db, _ORM, 'monsterClassification', 'Boss')
    _sf(db, _ORM, 'description', _TAG_ORM)
    _sf(db, _ORM, 'charLevel', list(_BAND))
    _sf(db, _ORM, 'characterLife', list(_ORM_LIFE))
    _sf(db, _ORM, 'scale', _ORM_SCALE)
    _sf(db, _ORM, 'characterRunSpeed', _ORM_SPEED)      # CORRECTION 9
    # actorHeight DELIBERATELY NOT WRITTEN (R-126: per-rig constant, inherited).
    # CORRECTION 10: 60, not 100. `defensiveLife` is VITALITY resistance, and 100
    # on BOTH forms walled the mod's own marquee bleed/vitality line end to end
    # while the design claimed beat 3 hands it back. A tree resists poison and
    # shrugs off cuts; it is not a vitality boss.
    _sf(db, _ORM, 'defensiveLife', 60.0, F)
    _sf(db, _ORM, 'defensivePierce', 50.0, F)
    _sf(db, _ORM, 'defensivePhysical', 30.0, F)
    _sf(db, _ORM, 'defensivePoison', 60.0, F)
    # CORRECTION 22: the CC floor, AUTHORED. Round 4 changed this whole axis
    # silently - freeze-lock became available where the shipped encounter was
    # immune, because the donor simply carries none. Stun is written to 25 so
    # that the donor's OWN `ascacophus_bleeddamageimmunity` (+50, measured) lands
    # the effective value on the same 75 the terminal gets from its record alone.
    # verify() asserts the EFFECTIVE number, so this arithmetic cannot drift.
    _sf(db, _ORM, 'defensiveStun',
        _CC_TARGET['defensiveStun'] - 50.0, F)             # +50 from the donor passive
    _sf(db, _ORM, 'defensiveFreeze', _CC_TARGET['defensiveFreeze'], F)
    _sf(db, _ORM, 'defensiveTrap', _CC_TARGET['defensiveTrap'], F)
    # MANA (CORRECTION 23): written explicitly so the two signature levers cannot
    # run dry. The donor's inherited 3000 / 0.0 funded ~9.6 cycles of a 312-cost
    # rotation and then the snare and the wall were gone for the rest of the
    # fight. Pool = the Gaoler's; regen funds one full rotation per 20s cooldown.
    _sf(db, _ORM, 'characterMana', _ORM_MANA, F)
    _sf(db, _ORM, 'characterManaRegen', _ORM_MANA_REGEN, F)
    _sf(db, _ORM, 'actorToSpawnOnDeath', _BLOOM, S)
    _sf(db, _ORM, 'spawnEffect', _FX_ORM_SPAWN, S)
    _sf(db, _ORM, 'deathEffect', _FX_ORM_DEATH, S)
    if _ORM_USE_SKIN_ALT:
        _sf(db, _ORM, 'baseTexture', _ORM_SKIN_ALT)
    # SOUL-LEAK INVARIANT: the donor ships its OWN soul at 33% (R-42/R-106 class).
    _svc_clear_soul_loot(db, _ORM)
    _TOUCHED.add(_n(_ORM))
    # CORRECTION 16 / WILL-DECISION 7: the transform SHELL pays no ordinary Misc
    # loot. The shipped `um_charon_ferryman_99` had NONE; the strongbark re-clone
    # inherited a 75 / 13 / 1.6 roll, which is an undisclosed encounter-level loot
    # INCREASE on the exact encounter behind Will's R-100 #10 complaint, in the
    # same window as b84's loot-volume TRIM lane. Muted by chance so nothing is
    # orphaned (no breadth module derives scope from a monster's lootMisc rows).
    if _ORM_MUTE_MISC:
        for _slot in (1, 2, 3):
            _sf(db, _ORM, 'chanceToEquipMisc%d' % _slot, 0.0)
    # hero -> boss scaling (in place; do NOT add a second scaler)
    _swap_scaler(db, _ORM)
    for _sk, _lvl in ((_SK_EARTHBIND, 8), (_SK_QUILLWARDS, 8),
                      (_SK_MEGABURST, 8), (_SK_HPSCALING, 1),
                      (_SK_CONVIMMUNE, 1), (_SPLIT, _SPLIT_LEVEL)):
        if not _svc_add_skill(db, _ORM, _sk, _lvl):
            raise SystemExit("charon_rework: no free skillName slot on %s for %s"
                             % (_ORM, _sk))
    # CORRECTION 1: exactly three cast slots are free ('2', '4', '5'); slot 1
    # (stumpstomp) and slot 3 (hero_quillvines) are the donor's own-family
    # signature and the R-125 bar forbids displacing them.
    _free = _free_cast_slots(db, _ORM)
    for _want in ('2', '4', '5'):
        if _want not in _free:
            raise SystemExit(
                "charon_rework: cast slot %r on %s is NOT free (free: %r). The "
                "donor's rotation moved; re-measure before displacing anything - "
                "slots 1 and 3 are its own-family signature (R-125)."
                % (_want, _ORM, _free))
    # Round 1 wired the snare at chance 18 on a 20s skill cooldown, which is one
    # roll every twenty seconds on the fight's ONLY anti-kite lever - too thin to
    # support the design's own "you do not kite this fight". Raised; the skill's
    # own `skillCooldownTime 20.0` still does the real spacing, so this only
    # changes how reliably the boss reaches for it, not how often it lands.
    _cast(db, _ORM, '2', _SK_EARTHBIND, 40.0, 'MediumRange', 6.0, 4.0)
    _cast(db, _ORM, '4', _SK_QUILLWARDS, 30.0, 'ShortRange', 10.0, 6.0)
    _cast(db, _ORM, '5', _SK_MEGABURST, 35.0, 'LongRange', 6.0, 3.0)

    # ── BEAT 3: AKREMON, THE HEARTWOOD ABLAZE (phase 2, terminal) ───────────
    _replace_record(db, _D_BLOOM, _BLOOM)
    _sf(db, _BLOOM, 'monsterClassification', 'Boss')
    _sf(db, _BLOOM, 'description', _TAG_BLOOM)
    _sf(db, _BLOOM, 'charLevel', list(_BAND))
    _sf(db, _BLOOM, 'characterLife', list(_BLOOM_LIFE))
    _sf(db, _BLOOM, 'scale', _BLOOM_SCALE)
    _sf(db, _BLOOM, 'characterRunSpeed', _BLOOM_SPEED)   # CORRECTION 9: it can hunt now
    # BLEED IMMUNITY DELIBERATELY DOES NOT CARRY, AND VITALITY RESISTANCE DROPS
    # 60 -> 40. Together those are what actually hands the shelved bleed/vitality
    # build the kill, instead of the design merely saying so (CORRECTION 10).
    _sf(db, _BLOOM, 'defensiveLife', 40.0, F)
    _sf(db, _BLOOM, 'defensivePierce', 50.0, F)
    _sf(db, _BLOOM, 'defensivePhysical', 30.0, F)
    # CORRECTION 22: 100 on the record, NOT 60, because `hero_fire` is being
    # dropped below and its +40 has to come from somewhere deliberate. After
    # `racial_plant`'s -30 this lands at the authored +70 effective. Phase 1 is
    # left at its racial -30 ON PURPOSE: the tree burns, the fire does not, so
    # the build that trivialises beat 1 has to be put down for beat 3 - the same
    # inversion the bleed immunity runs in the other direction.
    _sf(db, _BLOOM, 'defensiveFire', _BLOOM_FIRE_RES, F)
    _sf(db, _BLOOM, 'defensiveStun', _CC_TARGET['defensiveStun'], F)
    _sf(db, _BLOOM, 'defensiveFreeze', _CC_TARGET['defensiveFreeze'], F)
    _sf(db, _BLOOM, 'defensiveTrap', _CC_TARGET['defensiveTrap'], F)
    _sf(db, _BLOOM, 'characterMana', _BLOOM_MANA, F)
    _sf(db, _BLOOM, 'characterManaRegen', _BLOOM_MANA_REGEN, F)
    # CORRECTION 22, THE WALL NOBODY AUTHORED: the emberoak donor declares
    # `hero_fire` at level 4, which grants `defensiveStun 300.0` as well as the
    # +40 fire - a hard stun wall on the terminal, on a wave whose CORRECTION 10
    # headline is "NO WALLS", inherited and undisclosed exactly like beat 2's
    # 36% absorption was. `hero_fire` is a SHARED base record (Class Skill_Passive,
    # other carriers across the roster) so it is never mutated; it is swapped out
    # of its own declared slot for the strongbark's `elementalresistance_10xlevel`
    # - the same passive this encounter already fields on phase 1, +10 elemental,
    # and no crowd-control grant of any kind.
    _swap_declared_skill(db, _BLOOM, _DEAD_BLOOM_SKILL_FIRE, _SK_ELEMRESIST, 1,
                         'hero_fire hands the terminal a 300%% stun wall this '
                         'lane never authored and its docs deny; the +40 fire it '
                         'also gave is now written on the record')
    _sf(db, _BLOOM, 'actorToSpawnOnDeath', '', S)          # terminal
    _sf(db, _BLOOM, 'spawnEffect', _FX_BLOOM_SPAWN, S)
    _sf(db, _BLOOM, 'deathEffect', _FX_BLOOM_DEATH, S)
    _sf(db, _BLOOM, 'treasureProxyName', _ORB, S)          # CORRECTION 4 (hard gate)
    # CORRECTION 15: the emberoak donor is a DRX ACT-2/3 creature, so the re-clone
    # dropped this form - the one carrying the Golden Bough, the soul and the orb -
    # a full act below its own phase 1 and below every Hades-tier peer. Retarget
    # onto the act-4 band by named constant, and mute the two act-3 jungleroot
    # crafting rows (a jungle root does not fall off a burning tree at the Styx).
    for _fld, _tiers in _BLOOM_LOOT_RETARGET:
        if db.get_field_value(_BLOOM, _fld) is None:
            raise SystemExit(
                "charon_rework: %s does not carry %s, so the act-4 retarget has "
                "nothing to land on. The terminal donor's loot shape moved - "
                "re-measure the band before shipping (CORRECTION 15)."
                % (_BLOOM, _fld))
        _sf(db, _BLOOM, _fld, list(_tiers))
    for _fld in _BLOOM_LOOT_MUTE_WEIGHTS:
        if db.get_field_value(_BLOOM, _fld) is not None:
            _sf(db, _BLOOM, _fld, 0)
    # CORRECTION 20: and now the CHANCES, which are the volume. The retarget
    # above fixed which TABLES the terminal reads and never touched how often it
    # reads them, so the encounter still went 0 -> 176.6 against a written
    # promise that it did not move. Muted to the shipped encounter's exact zero.
    # The act-4 retarget above is deliberately KEPT rather than deleted: it is
    # what a future un-mute lands on, and it keeps `_UNDERBAND_TOKENS` meaningful.
    # Misc4 - the guaranteed Golden Bough - is NOT in `_MUTED_MISC_SLOTS`.
    if _BLOOM_MUTE_MISC:
        for _slot in _MUTED_MISC_SLOTS:
            _sf(db, _BLOOM, 'chanceToEquipMisc%d' % _slot, 0.0)
    _svc_clear_soul_loot(db, _BLOOM)                       # before _create_soul rewires
    _swap_scaler(db, _BLOOM)
    for _sk, _lvl in ((_SK_NOVA, 8), (_SK_THORNYAURA, 8),
                      (_SK_HPSCALING, 1), (_SK_CONVIMMUNE, 1)):
        if not _svc_add_skill(db, _BLOOM, _sk, _lvl):
            raise SystemExit("charon_rework: no free skillName slot on %s for %s"
                             % (_BLOOM, _sk))
    _free = _free_cast_slots(db, _BLOOM)
    for _want in ('4', '5'):
        if _want not in _free:
            raise SystemExit(
                "charon_rework: cast slot %r on %s is NOT free (free: %r); SV's "
                "own firedart/volcanicorb/flamesurge rotation is kept verbatim "
                "and must not be displaced." % (_want, _BLOOM, _free))
    # Chances raised from round 1's 25/15. The round-1 donor put THREE chance-100
    # zero-delay casts ahead of these, so the two additions - the only things
    # differentiating phase 2 from a plain donor - were the least likely casts in
    # the fight. The emberoak donor fixes that structurally (its rotation is
    # 100/40/50 with real delays), and these numbers finish the job.
    _cast(db, _BLOOM, '4', _SK_NOVA, 50.0, 'ShortRange', 5.0, 3.0)
    _cast(db, _BLOOM, '5', _SK_THORNYAURA, 40.0, 'AnyRange', 12.0, 8.0)

    # ── THE HANDBRIAR (Champion escort x2) - the R-100 #18 fix ──────────────
    _replace_record(db, _D_BRIAR, _BRIAR)
    _sf(db, _BRIAR, 'monsterClassification', 'Champion', S)   # donor has NO such field
    _sf(db, _BRIAR, 'description', _TAG_BRIAR)
    _sf(db, _BRIAR, 'charLevel', list(_BAND))
    _sf(db, _BRIAR, 'characterLife', list(_BRIAR_LIFE))       # explicit ASCENDING
    _sf(db, _BRIAR, 'scale', _BRIAR_SCALE)
    _sf(db, _BRIAR, 'characterRunSpeed', _BRIAR_SPEED)        # an escort must escort
    _sf(db, _BRIAR, 'handHitDamageMin', 180.0)
    _sf(db, _BRIAR, 'handHitDamageMax', 240.0)
    _sf(db, _BRIAR, 'defensivePierce', 25.0, F)
    _sf(db, _BRIAR, 'defensiveBleeding', 50.0, F)
    _sf(db, _BRIAR, 'defensivePoison', 40.0, F)
    # R-125 minion law: a placed add can never become a loot faucet, can never
    # pay a soul (R-42/R-106) and can never enter the uber_quest_markers roster.
    _svc_clear_soul_loot(db, _BRIAR)
    _sf(db, _BRIAR, 'dropItems', 0)
    _sf(db, _BRIAR, 'chanceToEquipMisc1', 0.0)   # donor's act-3 relic table, muted
    _sf(db, _BRIAR, 'DisplayAsQuestItem', 0)
    if not _svc_add_skill(db, _BRIAR, _SK_HPSCALING, 1):
        raise SystemExit("charon_rework: no free skillName slot on %s" % _BRIAR)
    # CORRECTION 17: the donor's ENTIRE rotation was one cast - `beetlebile_vomitbile`,
    # a five-projectile POISON burst at MediumRange. The junglecreep was chosen for
    # its rig and its D19 mobility, never for its kit, and a ranged beetle-bile
    # spitter is not "a ground-hugging whipping vine". Swap the declared slot AND
    # the cast onto `quillvine_barb`, whose seven live carriers are `quillvine_01..06`
    # - literally the bodies the boss's own quillwards wall and hero_quillvines
    # retinue put on the field. The escorts now fire the same barb as the briar the
    # boss grows: the R-125 own-family bar satisfied at the ENCOUNTER level.
    _swap_declared_skill(db, _BRIAR, _DEAD_BRIAR_SKILL, _SK_QUILLBARB,
                         list(_BRIAR_BARB_LEVEL),
                         'an escort of a grasping-root boss fires briar barbs, '
                         'not beetle bile')
    _cast(db, _BRIAR, '', _SK_QUILLBARB, 70.0, 'ShortRange', 4.0, 2.0)

    # ── uber_quest_markers (registry index 43) writes DisplayAsQuestItem on
    #    these records and its verify() RE-DERIVES on the final db. The re-clone
    #    above reset the field to the donor's value, so re-assert it here.
    _sf(db, _ORM, 'DisplayAsQuestItem', 1)
    _sf(db, _BLOOM, 'DisplayAsQuestItem', 1)

    # ── THE PROXY CHAIN: REUSED, never rebuilt (arz-only; no map rebuild) ────
    for pool, desc in ((_POOL, 'Akremon, the Grasping Root (main) + 2 Handbriar '
                               'champion escorts'),
                       (_YARD_POOL, 'YARD: Akremon + 2 Handbriars @100% '
                                    '(TESTHUB-only, never uploaded)')):
        _sf(db, pool, 'FileDescription', desc)
        for f in ('name1', 'name2', 'name3'):
            _sf(db, pool, f, _ORM)
        for f in ('nameChampion1', 'nameChampion2'):
            _sf(db, pool, f, _BRIAR)
    for proxy in (_PROXY, _YARD_PROXY):
        _sf(db, proxy, 'mesh', _MESH_ORM)
        _sf(db, proxy, 'scale', _ORM_SCALE)

    for entry in asp._MOD_AUTHORED_SPAWN_PROXIES:
        if _n(entry.get('proxy')) == _n(_PROXY):
            entry['main_monster'] = _ORM
            entry['name'] = 'q_goldenbough_lone (Akremon + 2 Handbriar escorts)'
        elif _n(entry.get('proxy')) == _n(_YARD_PROXY):
            entry['main_monster'] = _ORM
            entry['name'] = 'q_yard_goldenbough (TESTHUB yard)'

    # ── REWARD 1: THE GOLDEN BOUGH, still guaranteed off the terminal ────────
    # `_svc_guarantee_unique` IGNORES its loot_name argument and writes
    # lootMisc{n}Item1 + chanceToEquipMisc{n}=100 straight onto the monster; the
    # `goldenbough_guaranteed.dbr` loot table the old call named DOES NOT EXIST
    # in the arz and never did. Pass None. The donor leaves Misc4 free, so this
    # lands on Misc4 exactly as the shipped encounter did.
    _svc_guarantee_unique(db, _BLOOM, list(_AMULET), None)
    _TOUCHED.add(_n(_BLOOM))

    # ── REWARD 2: THE HOARD - ONE chest. R-108 cut it 3 -> 1 in answer to Will's
    #    OWN R-100 #10 complaint about THIS boss ("the uber monster soul of the
    #    unferried also had three chests"). Chain frozen, loot band untouched
    #    (apply_svc_patches L16948 'svc_charonhoard' keys on the frozen prefix and
    #    needs no change - verify() proves that rather than assuming it).

    # ── REWARD 3: THE SOUL - {^F}Soul of the Gilded Root ─────────────────────
    def _stats(t):
        m = {'n': 0.55, 'e': 0.78, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)                                # noqa: E731
        return {
            **_bmp(t),
            # manual-cast summon grant: NO itemSkillAutoController (D19/D21 law)
            'itemSkillName': (S, _SUMMON),
            'itemSkillLevel': (I, {'n': 1, 'e': 2, 'l': 3}[t]),
            'augmentSkillName1': (S, _SK_HEART_OF_OAK),
            'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, {'n': 2, 'e': 3, 'l': 4}[t]),
            # RE-THEMED off the old cold/vitality soul onto fire + pierce. Note
            # the word RE-themed is only true because `_strip_superseded_soul_stats`
            # runs first (CORRECTION 11); round 2 made the same claim while the
            # ferryman's whole cold/vitality/life-leech block survived underneath.
            'offensiveFireMin': (F, r(64.0)), 'offensiveFireMax': (F, r(102.0)),
            'offensiveFireModifier': (F, r(20.0)),
            'offensivePierceMin': (F, r(48.0)), 'offensivePierceMax': (F, r(78.0)),
            'offensivePierceRatioMin': (F, r(18.0)),
            'retaliationPierceMin': (F, r(70.0)), 'retaliationPierceMax': (F, r(110.0)),
            # THE ONE WEIRD STAT (CORRECTION 5, REWRITTEN BY CORRECTION 21): the
            # boss's own signature as a player stat - the ground takes hold of
            # whatever you strike. Round 3 reached for `offensiveSlowPhysical*`
            # because 2,095 souls CARRY the field; measured this round, only 3 of
            # them carry it NON-ZERO, its whole live band is [0.00, 8.00] against
            # the 22/31/40 written here, and all 2,095 ship its DURATION at 0.0.
            # Carrying a field is not using it. The family the mod actually
            # snares with is `offensiveSlowRunSpeed*`: 46 non-zero carriers, band
            # [0.00, 79.00] with durations [0.00, 4.00], led by the hand-designed
            # souls this one belongs beside (thebloatedone 79.0/4.0s, meglograi
            # 75.0/3.0s, camelbane 71.0/4.0s). Same intent, real field, in band.
            'offensiveSlowRunSpeedMin': (F, r(_SOUL_SNARE)),
            'offensiveSlowRunSpeedDurationMin': (
                F, dict(zip('nel', _SOUL_SNARE_DURATION))[t]),
            # ...and the amgoz1 downside: the root takes a little hold of you as
            # well. CORRECTION 21: on `characterRunSpeedModifier`, the ITEM
            # movement-percent field (2,224 soul carriers, 155 of them negative),
            # NOT `characterRunSpeed`, which is the creature LOCOMOTION scalar
            # whose entire live soul band is [0.00, 1.28] with ZERO negatives.
            # Round 3 wrote the right three numbers into the wrong field, so the
            # penalty asserted in the module header, in R-231 and in the test
            # guide did not exist, and a negative absolute run speed shipped on a
            # permanently-equipped item instead. These are `mnemophage_soul_*`'s
            # exact values on the right field - the mod's own hand-designed uber
            # soul and this one's direct roster neighbour, measured.
            'characterRunSpeedModifier': (F, _SOUL_RUNSPEED_PENALTY[t]),
            'characterLife': (F, r(220.0)), 'characterLifeModifier': (F, r(15.0)),
            'characterDefensiveAbility': (F, r(80.0)),
            'defensiveBleeding': (F, r(35.0)),      # the wood's gift
            'defensiveFire': (F, r(30.0)), 'defensiveLife': (F, r(30.0)),
        }

    tiers = [{'diff': t, 'itemLevel': il, 'stats': _stats(t)}
             for t, il in (('n', 48), ('e', 72), ('l', 100))]
    # CORRECTION 11 - CLEAR THE SUPERSEDED FERRYMAN STAT BLOCK FIRST. The soul
    # path is frozen for save-compat, so `_create_soul` layers onto a record the
    # monolith wrote earlier in THIS run; `_ensure_record` no-ops on an existing
    # record and `_set_soul_fields` only ever adds keys. Without this, the whole
    # cold / vitality / life-leech / fear / offensivePercentCurrentLife identity
    # of "Soul of the Unferried" survives UNDERNEATH the new fire+pierce stats -
    # including base Charon's own signature lever, which the ratified spec
    # explicitly forbade on this soul. `keep` is the exact key set the rebuild is
    # about to write, so the strip can never outrun it.
    _keep = set(asp._SOUL_BOILERPLATE)
    for _t in tiers:
        _keep |= set(_t['stats'])
    _stripped = []
    for _t in tiers:
        _p = (r'records\item\equipmentring\soul\svc_uber\%s_soul_%s.dbr'
              % (_SOUL_BASENAME, _t['diff']))
        if db.has_record(_p):
            _stripped.append((_t['diff'], _strip_superseded_soul_stats(db, _p, _keep)))
    for _d, _fl in _stripped:
        if _fl:
            print("    soul tier %s: stripped %d superseded ferryman stat(s): %s"
                  % (_d, len(_fl), ', '.join(_fl)))
    soul_paths = _create_soul(db, _SOUL_BASENAME, _TAG_SOUL, tiers,
                              monster=_BLOOM, drop_rate=66.0)
    for p in soul_paths:
        db.set_field(p, 'FileDescription', 'Hades')
        db._modified.add(p)
        _TOUCHED.add(_n(p))
    # The chain HEAD names OUR soul at chance 0 (it never pays; the terminal
    # does). Strictly cleaner than the shipped shape, where the head named a
    # DIFFERENT soul at 0, and it keeps the record inside verify_soul_drop_rates'
    # index where SOUL_RATE_ZERO_PINS expects to find it at 0.0.
    _sf(db, _ORM, 'lootFinger2Item1', list(soul_paths))
    _sf(db, _ORM, 'chanceToEquipFinger2', 0.0)

    # ── THE SUMMON: same species as the dropper -> the F2 identity gate goes
    #    GREEN WITH NO EXEMPTION, so a sanctioned workaround is RETIRED rather
    #    than carried. The gate compares the SOURCE's mesh to the DROPPER's mesh;
    #    both are now DRX\meshes\emberoakmesh.msh.
    #
    #    THE STALE-REGISTRATION TRAP (round-1 P0, proven to red the full build).
    #    The monolith's `_create_goldenbough_boss` already built THESE EXACT pet
    #    paths from `charon_minion_30`, and `_SUMMON_PET_BUILDS` was a blind
    #    append cleared once per run. `run_registry_gates` runs AFTER every module
    #    and feeds the WHOLE list to the three pet gates, so the superseded pair
    #    was still judged: PET-STAT-MIRROR compared our newly-built pets against
    #    charon_minion_30 and failed, and the F2 identity gate failed next
    #    (charon_minion_30 wears CharonGhost.msh, our dropper does not) - which is
    #    exactly what `_SUMMON_IDENTITY_ALLOW['ferryman']` used to paper over.
    #    `_build_boss_summon` now supersedes by pet-path set upstream, which is
    #    the durable fix. This prune stays as the idempotent belt-and-braces so
    #    the module is correct even against an older monolith, and verify()
    #    asserts the END STATE rather than trusting either half.
    _pp = {_n(p) for p in _PETS}
    asp._SUMMON_PET_BUILDS[:] = [(s, p) for s, p in asp._SUMMON_PET_BUILDS
                                 if {_n(q) for q in p} != _pp]
    _build_boss_summon(
        db, _D_BLOOM, _PETS, _SUMMON, _TAG_SUMMON, _TAG_PET,
        char_level=list(_BAND), life=[5500.0, 8000.0, 11000.0],
        life_regen=[18.0, 36.0, 60.0], dmg_min=[42.0, 72.0, 108.0],
        dmg_max=[66.0, 110.0, 160.0], scale=1.4, loadout=None)
    for p in _PETS + [_SUMMON]:
        _TOUCHED.add(_n(p))
    # CORRECTION 18: restore the SHIPPED pet shape. `_update_existing_fields`
    # overwrote the Lyia baseline's skill slots from the emberoak SOURCE, so the
    # pets took a monster's `hero_scaling` and lost the three globalproperties
    # difficulty rows. Impact is nil (CORRECTION 13) but it is residue, and
    # `_swap_scaler`'s assert-the-incumbent discipline was written for exactly
    # this case and had never been applied to the pets.
    for p in _PETS:
        _restore_pet_difficulty_rows(db, p)
    # CORRECTION 24 (round-5 vet P3): R-126 stopped at the three MONSTER records
    # and never reached the three PETS the same wave rebuilds. `_build_boss_summon`
    # writes mesh and baseTexture but not `actorHeight`, so the pets kept the Lyia
    # baseline's 2.0 on `DRX\meshes\emberoakmesh.msh`, whose ONLY live carrier -
    # the donor itself - ships 1.0. Not a regression (the shipped oarsmen were
    # also 2.0, on CharonGhost.msh) and the impact is targeting / health-bar
    # anchoring rather than render, but the invariant this module is proudest of
    # had a blind spot on its own output. The value is READ OFF THE DONOR, never
    # invented, which is precisely what R-126 requires; verify() now covers all
    # six bodies instead of three.
    _pet_h = _one(db, _D_BLOOM, 'actorHeight')
    if _pet_h is None:
        raise SystemExit(
            "charon_rework: %s declares no actorHeight, so the soul pets have no "
            "rig constant to inherit (R-126 forbids inventing one). The terminal "
            "donor moved - re-measure before shipping." % _D_BLOOM)
    for p in _PETS:
        _sf(db, p, 'actorHeight', float(_pet_h), F)
    # CORRECTION 12 - THE GRANTED SKILL'S OWN PLAYER SURFACES.
    # The ICON is fixed at the source of truth (`_SUMMON_SKILL_ICON` in the
    # monolith), so `_build_boss_summon` above already stamped the flame-ring
    # glyph on this skill; verify() proves the end state either way.
    # The HIT SOUND is not written by `_build_boss_summon` at all, so the skill
    # kept Lyia's Maenad cast pak. Retargeted onto the terminal donor's OWN alert
    # pak - the `<family>alertpak` convention every already-fixed summon uses.
    if db.has_record(_SUMMON_HIT_SOUND):
        _sf(db, _SUMMON, 'skillHitSound', _SUMMON_HIT_SOUND)
    else:
        raise SystemExit(
            "charon_rework: %s does not resolve. It is the terminal donor "
            "um_emberoak_42's own declared alertSound and the replacement for the "
            "Lyia-clone Maenad cast pak on the granted summon; an unresolved "
            "sound ref is not an acceptable silent degrade." % _SUMMON_HIT_SOUND)
    # The source entry is DELETED in apply_svc_patches by this wave; this pop is
    # the idempotent belt-and-braces so a stale entry can never re-exempt us.
    asp._SUMMON_IDENTITY_ALLOW.pop('ferryman', None)

    # ── TAGS (arz + Text are a COUPLED deploy; validate_tags is a build gate) ─
    tags[_TAG_ORM] = '{^r}Akremon, the Grasping Root'
    tags[_TAG_BLOOM] = '{^r}Akremon, the Heartwood Ablaze'
    tags[_TAG_BRIAR] = '{^G}Handbriar'
    tags[_TAG_HOARD] = 'The Orchard of Hands'
    tags[_TAG_AMULET] = 'The Golden Bough'
    tags[_TAG_AMULET_DESC] = (
        'The tree grew it and would not let it go. Cut it while it still burned, '
        'and the wood it came off is still standing at the shrine with every hand '
        'that tried before yours grown into it.')
    tags[_TAG_SOUL] = '{^F}Soul of the Grasping Root'
    tags[_TAG_SOUL + 'DESC'] = (
        'It waited at the shrine for hands and it never had to wait long. Carry '
        'its soul and the ground takes hold of whatever you strike, and takes a '
        'little hold of you as well.')
    tags[_TAG_SUMMON] = 'Graft the Burning Heartwood'
    tags[_TAG_SUMMON + 'DESC'] = (
        'The heartwood is the part of the tree that is still hungry. Speak its '
        'soul and a burning cutting takes root beside you, stands up, and walks '
        'for you until something puts it out.')
    tags[_TAG_PET] = 'Burning Heartwood'

    print("  charon_rework: Charon is OUT of the Golden Bough forecourt. "
          "AKREMON, THE GRASPING ROOT [%s, rs %.2f] (Plant, Ascacophus02 @%.1f, "
          "bleed-immune, root-snare + the mod's ONLY Skill_DefensiveWall + quill "
          "fan, splits at 33%%) -> THE HEARTWOOD ABLAZE [%s, rs %.2f] (Plant, DRX "
          "emberoak @%.1f, ring of flame + volcanic orb + petal ring, NOT "
          "bleed-immune, vitality res 40) + 2 Handbriar champions [%s, ascending, "
          "rs %.2f, briar barbs not beetle bile]; Epic total %s vs the Gaoler's "
          "35,000 (gaoler_variance_rca) and beat 2 grants NO absorption and NO "
          "regen - only an authored +%.0f%% physical; every body D19-mobile; proxy "
          "chain REUSED (no map rebuild); Golden Bough Misc4 100%%, one hoard "
          "chest, soul re-identified; ordinary loot: terminal on the act-4 band, "
          "shell MUTED to the shipped shell's shape; "
          "_SUMMON_IDENTITY_ALLOW['ferryman'] RETIRED; %d record(s) written."
          % (_ORM_LIFE, _ORM_SPEED, _ORM_SCALE, _BLOOM_LIFE, _BLOOM_SPEED,
             _BLOOM_SCALE, _BRIAR_LIFE, _BRIAR_SPEED,
             f"{int(_ORM_LIFE[1] + _BLOOM_LIFE[1]):,}", _SPLIT_PHYSMOD,
             len(_TOUCHED)))


# ── verify: THE GATE (post-finalization, reads the FINAL assembled db) ──────
def verify(db, tags):
    problems = []

    def gv(rec, field):
        return _one(db, rec, field)

    # ONE lowercase index for the whole gate. The naive per-call
    # `any(... for n in db.record_names())` fallback is O(51k) on every miss and
    # turns a gate into a minute of wall clock inside the build.
    _names = {_n(n) for n in db.record_names()}

    def resolves(path):
        if not isinstance(path, str) or not path.strip():
            return False
        return db.has_record(path) or _n(path) in _names

    # ---- 1. THE PROXY CHAIN RESOLVES END TO END (the hard constraint) ------
    for proxy, pool, label in ((_PROXY, _POOL, 'canonical forecourt'),
                               (_YARD_PROXY, _YARD_POOL, 'TESTHUB yard')):
        if not db.has_record(proxy) or not db.has_record(pool):
            problems.append("%s: proxy/pool missing (%s / %s)" % (label, proxy, pool))
            continue
        if _n(gv(proxy, 'pool1')) != _n(pool):
            problems.append("%s: proxy pool1=%r, expected %s"
                            % (label, gv(proxy, 'pool1'), pool))
        for f in ('name1', 'name2', 'name3'):
            if _n(gv(pool, f)) != _n(_ORM):
                problems.append("%s: pool %s=%r, expected the reworked main "
                                "monster %s - the placed encounter would still "
                                "spawn the retired boss."
                                % (label, f, gv(pool, f), _ORM))
        for f in ('nameChampion1', 'nameChampion2'):
            if _n(gv(pool, f)) != _n(_BRIAR):
                problems.append("%s: pool %s=%r, expected %s"
                                % (label, f, gv(pool, f), _BRIAR))
        if _n(gv(proxy, 'mesh')) != _n(_MESH_ORM):
            problems.append("%s: proxy preview mesh=%r, expected %s (the world "
                            "preview would still show Charon)"
                            % (label, gv(proxy, 'mesh'), _MESH_ORM))
        if abs(float(gv(proxy, 'scale') or 0) - _ORM_SCALE) > 1e-4:
            problems.append("%s: proxy scale=%r, expected %s"
                            % (label, gv(proxy, 'scale'), _ORM_SCALE))
    if _n(gv(_ORM, 'actorToSpawnOnDeath')) != _n(_BLOOM):
        problems.append("phase link broken: %s actorToSpawnOnDeath=%r, expected %s"
                        % (_ORM, gv(_ORM, 'actorToSpawnOnDeath'), _BLOOM))
    if str(gv(_BLOOM, 'actorToSpawnOnDeath') or '').strip():
        problems.append("%s must be TERMINAL but actorToSpawnOnDeath=%r"
                        % (_BLOOM, gv(_BLOOM, 'actorToSpawnOnDeath')))

    # ---- 2. THE THREE GUARANTEED REWARDS ARE WIRED -------------------------
    slot = None
    for nsl in (3, 4, 5, 6):
        v = db.get_field_value(_BLOOM, 'lootMisc%dItem1' % nsl)
        v = v if isinstance(v, list) else ([v] if v else [])
        if [_n(x) for x in v] == [_n(a) for a in _AMULET]:
            slot = nsl
            break
    if slot is None:
        problems.append("THE GOLDEN BOUGH is NOT wired on %s: no lootMisc*Item1 "
                        "carries the 3 amulet tiers %s" % (_BLOOM, _AMULET))
    else:
        ch = float(gv(_BLOOM, 'chanceToEquipMisc%d' % slot) or 0)
        if abs(ch - 100.0) > 1e-4:
            problems.append("THE GOLDEN BOUGH is on Misc%d but chanceToEquipMisc%d"
                            "=%r, expected 100.0 (guaranteed)" % (slot, slot, ch))
        if int(gv(_BLOOM, 'dropItems') or 0) != 1:
            problems.append("%s dropItems != 1 - the guaranteed amulet cannot drop"
                            % _BLOOM)
    for a in _AMULET:
        if not resolves(a):
            problems.append("Golden Bough tier record missing: %s" % a)
    # the hoard: ONE chest (R-108 cut it 3 -> 1 for Will's own R-100 #10)
    for h in _HOARD:
        if not resolves(h):
            problems.append("hoard chain record missing: %s (the dedicated "
                            "Boss-locked hoard is a guaranteed reward)" % h)
    if not resolves(_WORLD_CHEST):
        problems.append("world-chest proxy missing: %s - build_section_surgery "
                        "places it BY NAME, so the frozen path must survive."
                        % _WORLD_CHEST)
    if not resolves(_ORB):
        problems.append("terminal orb %s does not resolve - the whole encounter "
                        "would drop no orb (red_uber_orbs shell exemption)." % _ORB)
    if _n(gv(_BLOOM, 'treasureProxyName')) != _n(_ORB):
        problems.append(
            "%s treasureProxyName=%r, expected %s. This is NOT cosmetic: "
            "svc_orb_breadth derives its scope as 'every proxy an UBER names' and "
            "enforces MIN_PROXIES=6 / MIN_TABLES=18; this record is the only uber "
            "naming that proxy, so dropping it reds orb_loot_breadth."
            % (_BLOOM, gv(_BLOOM, 'treasureProxyName'), _ORB))
    # the soul
    got = db.get_field_value(_BLOOM, 'lootFinger2Item1') or []
    got = got if isinstance(got, list) else [got]
    if [_n(x) for x in got] != [_n(s) for s in _SOUL_TIERS]:
        problems.append("%s soul loot=%r, expected the 3 frozen tiers %s"
                        % (_BLOOM, got, _SOUL_TIERS))
    if float(gv(_BLOOM, 'chanceToEquipFinger2') or 0) <= 0:
        problems.append("%s chanceToEquipFinger2=%r - the terminal must pay the "
                        "soul" % (_BLOOM, gv(_BLOOM, 'chanceToEquipFinger2')))
    if float(gv(_ORM, 'chanceToEquipFinger2') or 0) != 0.0:
        problems.append("%s chanceToEquipFinger2=%r - the chain HEAD must stay at "
                        "0 (build_svc_database.SOUL_RATE_ZERO_PINS; a paying head "
                        "makes one encounter drop two souls)"
                        % (_ORM, gv(_ORM, 'chanceToEquipFinger2')))
    if float(gv(_BRIAR, 'chanceToEquipFinger2') or 0) != 0.0:
        problems.append("%s chanceToEquipFinger2=%r - a Champion escort must never "
                        "pay a soul (R-42/R-106)"
                        % (_BRIAR, gv(_BRIAR, 'chanceToEquipFinger2')))
    for s in _SOUL_TIERS:
        if not resolves(s):
            problems.append("soul tier record missing: %s" % s)
        elif _n(gv(s, 'itemNameTag')) != _n(_TAG_SOUL):
            problems.append("soul %s itemNameTag=%r, expected %s"
                            % (s, gv(s, 'itemNameTag'), _TAG_SOUL))

    # ---- 2b. THE SOUL IS ACTUALLY RE-THEMED, NOT JUST RE-LABELLED ----------
    #
    # Round 2's gate read `itemNameTag` on the tiers and NOTHING ELSE, so the
    # entire shipped ferryman stat block survived underneath the new one and the
    # gate stayed green (CORRECTION 11). The soul is THE reward the player keeps
    # forever; a tooltip that still reads Cold Damage + Slow + Cold Resist +
    # Vitality + Life Leech + Fear + % Current Life on an item called "Soul of the
    # Grasping Root", dropped by a burning tree, fails Will's order on the one
    # surface he cannot put down. So prove the OLD identity is GONE, not merely
    # that the new one is present.
    for s in _SOUL_TIERS:
        if not resolves(s):
            continue
        survived = [f for f in _DEAD_SOUL_FIELDS if gv(s, f) is not None]
        if survived:
            problems.append(
                "SOUL RETHEME INCOMPLETE: %s still carries %d superseded field(s) "
                "from 'Soul of the Unferried': %s. The path is FROZEN for "
                "save-compat, so _create_soul layers onto the monolith's own "
                "earlier record (_ensure_record no-ops, _set_soul_fields only "
                "adds) - _strip_superseded_soul_stats must run first. "
                "offensivePercentCurrentLife in particular is base Charon's "
                "signature lever (charon_geyserform1, 24 roster carriers) and the "
                "ratified spec forbade it on this soul by name."
                % (s, len(survived), survived))
        # the new identity is present and the manual-cast law holds
        if gv(s, 'offensiveFireMin') is None or gv(s, 'offensivePierceMin') is None:
            problems.append("%s carries no fire+pierce offence - the re-theme did "
                            "not land at all" % s)
        if _n(gv(s, 'itemSkillName')) != _n(_SUMMON):
            problems.append("%s itemSkillName=%r, expected the reworked summon %s"
                            % (s, gv(s, 'itemSkillName'), _SUMMON))

    # ---- 2c. THE GRANTED SUMMON'S OWN PLAYER SURFACES (R-125 law #3) -------
    #
    # The summon skill sits on the player's SKILL BAR every cast. Round 2 shipped
    # it wearing Charon's drowned-ghost glyph (`drownedspirit*` - 3 carriers
    # DB-wide, all Charon-adjacent) and the Lyia-clone Maenad cast pak, under the
    # name "Graft the Burning Heartwood". On a wave whose entire premise is that
    # Charon stops being visible here, that is the wrong residue to ship.
    if resolves(_SUMMON):
        for fld, want in (('skillUpBitmapName', _SUMMON_ICON[0]),
                          ('skillDownBitmapName', _SUMMON_ICON[1])):
            got_i = gv(_SUMMON, fld)
            if _DEAD_ICON_TOKEN in _n(got_i):
                problems.append(
                    "%s %s=%r is still Charon's DROWNED-SPIRIT glyph. Retarget "
                    "_SUMMON_SKILL_ICON['summon_charon_oarsman'] in "
                    "apply_svc_patches.py - it is the source of truth and the "
                    "monolith stamps it BEFORE this module runs."
                    % (_SUMMON, fld, got_i))
            elif _n(got_i) != _n(want):
                problems.append("%s %s=%r, expected %s" % (_SUMMON, fld, got_i, want))
        snd = gv(_SUMMON, 'skillHitSound')
        if _DEAD_SOUND_TOKEN in _n(snd):
            problems.append(
                "%s skillHitSound=%r is the Lyia-clone Maenad pak. "
                "_build_boss_summon never writes this field, so it has to be set "
                "explicitly; use the summoned body's own family alert pak."
                % (_SUMMON, snd))
        elif _n(snd) != _n(_SUMMON_HIT_SOUND):
            problems.append("%s skillHitSound=%r, expected the terminal donor's "
                            "own alert pak %s" % (_SUMMON, snd, _SUMMON_HIT_SOUND))
        elif not resolves(snd):
            problems.append("%s skillHitSound=%r does not resolve" % (_SUMMON, snd))
        if _n(gv(_SUMMON, 'skillDisplayName')) != _n(_TAG_SUMMON):
            problems.append("%s skillDisplayName=%r, expected %s"
                            % (_SUMMON, gv(_SUMMON, 'skillDisplayName'), _TAG_SUMMON))

    # ---- 2d. THE SCALER SWAP LANDED, AND NO SECOND SCALER SURVIVES ---------
    #      CORRECTION 13: round 2 blind-overwrote skillName12 and declared a
    #      `_SK_HERO_SCALING` constant it never used. apply() now ASSERTS the
    #      incumbent before the swap; this proves the end state.
    for rec, label in ((_ORM, 'phase 1'), (_BLOOM, 'the terminal')):
        _sks = {_n(gv(rec, 'skillName%d' % i)) for i in range(1, 25)}
        if _n(_SK_BOSS_SCALING) not in _sks:
            problems.append("%s (%s) carries no boss_scaling - an uber must scale "
                            "as a Boss" % (rec, label))
        if _n(_SK_HERO_SCALING) in _sks:
            problems.append("%s (%s) still carries hero_scaling ALONGSIDE "
                            "boss_scaling - two scalers stack" % (rec, label))

    # ---- 2e. BEAT 2 CARRIES NO NUMBER THIS LANE DID NOT AUTHOR -------------
    #
    # CORRECTION 14. `svc_bough_splitting` clones `DefensiveMastery_Adrenaline`,
    # which ships THREE non-zero 20-row level arrays. Wired verbatim at level 10 it
    # was silently granting 36% flat damage absorption + 8/s life regen + 60%
    # physical damage, permanently up (cd 5.0 < duration 12.0) for the whole last
    # third of phase 1 - under this lane's own repeated claim of EXACT Gaoler
    # durability parity. Every row of all three is asserted, not just the row the
    # current wiring reads, so a future retune of `_SPLIT_LEVEL` cannot re-open it.
    if resolves(_SPLIT):
        for fld, want in (('damageAbsorptionPercent', _SPLIT_ABSORB),
                          ('characterLifeRegen', _SPLIT_REGEN),
                          ('offensivePhysicalModifier', _SPLIT_PHYSMOD)):
            v = db.get_field_value(_SPLIT, fld)
            v = v if isinstance(v, list) else ([] if v is None else [v])
            try:
                vals = [float(x or 0) for x in v]
            except (TypeError, ValueError):
                vals = []
            if len(vals) < _SPLIT_LEVEL:
                problems.append(
                    "BEAT 2: %s %s has %d row(s) but the skill is wired at level "
                    "%d - it would index past the end of its own array."
                    % (_SPLIT, fld, len(vals), _SPLIT_LEVEL))
            elif any(abs(x - want) > 1e-4 for x in vals):
                problems.append(
                    "BEAT 2 CARRIES AN UNAUTHORED DONOR BUFF: %s %s=%r, expected "
                    "every row = %s. This record is a clone of "
                    "lowhealth_berserkerrage01 (DefensiveMastery_Adrenaline); "
                    "verbatim at level %d it grants 36%% flat damage absorption + "
                    "8/s regen + 60%% physical damage for the whole last third of "
                    "phase 1, which makes the Gaoler-parity durability claim in "
                    "this module, in R-231 and in the BACKLOG measurably wrong. "
                    "Author the value or state the real number - do not inherit it."
                    % (_SPLIT, fld, vals[:12], want, _SPLIT_LEVEL))
        got_lvl = None
        for i in range(1, 25):
            if _n(gv(_ORM, 'skillName%d' % i)) == _n(_SPLIT):
                got_lvl = db.get_field_value(_ORM, 'skillLevel%d' % i)
                got_lvl = got_lvl[0] if isinstance(got_lvl, list) else got_lvl
                break
        if got_lvl is None:
            problems.append("%s does not declare the beat-2 trigger %s at all"
                            % (_ORM, _SPLIT))
        elif int(float(got_lvl)) != _SPLIT_LEVEL:
            problems.append("%s wires %s at skillLevel %r, expected %d "
                            "(_SPLIT_LEVEL - the gate above is sized to it)"
                            % (_ORM, _SPLIT, got_lvl, _SPLIT_LEVEL))

    # ---- 2f. ORDINARY LOOT: banded, and a decision rather than a side effect --
    #
    # CORRECTION 15/16. Two independent regressions, both invisible to every
    # existing gate (b84's svc_loot_volume is container-scoped; orb_loot_breadth
    # keys on treasureProxyName):
    #   * the TERMINAL - the form carrying the Golden Bough, the soul and the orb -
    #     inherited the DRX emberoak's ACT-2/3 tables, a full act below its own
    #     phase 1 and below every Hades-tier peer including the Gaoler this lane
    #     calibrates against;
    #   * the SHELL went from dropping NOTHING to a 75/13/1.6 roll.
    for _fld, _tiers in _BLOOM_LOOT_RETARGET:
        got_t = db.get_field_value(_BLOOM, _fld)
        got_t = got_t if isinstance(got_t, list) else ([got_t] if got_t else [])
        if [_n(x) for x in got_t] != [_n(t) for t in _tiers]:
            problems.append("TERMINAL LOOT BAND: %s %s=%r, expected the act-4 "
                            "band %s" % (_BLOOM, _fld, got_t, _tiers))
    for _rec, _lbl in ((_BLOOM, 'the terminal'), (_ORM, 'the shell')):
        for i in range(1, 9):
            for j in range(1, 9):
                v = db.get_field_value(_rec, 'lootMisc%dItem%d' % (i, j))
                for x in (v if isinstance(v, list) else [v]):
                    if not isinstance(x, str) or not x.strip():
                        continue
                    b = _n(x).rsplit('\\', 1)[-1]
                    hit = [t for t in _UNDERBAND_TOKENS if t in b]
                    if hit and float(gv(_rec, 'chanceToEquipMisc%d' % i) or 0) > 0 \
                            and float(gv(_rec, 'chanceToEquipMisc%dItem%d' % (i, j)) or 0) > 0:
                        problems.append(
                            "UNDER-BAND LOOT: %s (%s) lootMisc%dItem%d rolls %r, "
                            "which is act-1/2/3 tier. This is a Hades-tier uber; "
                            "its peers (incl. um_polisgaoler_unbound_99, the "
                            "durability reference) run the act-4 band, and phase 1 "
                            "of this same encounter already does. A donor swap "
                            "must not silently re-lower it."
                            % (_rec, _lbl, i, j, x))
    if _ORM_MUTE_MISC:
        for _slot in (1, 2, 3):
            ch = float(gv(_ORM, 'chanceToEquipMisc%d' % _slot) or 0)
            if ch > 0:
                problems.append(
                    "%s chanceToEquipMisc%d=%r but _ORM_MUTE_MISC is on. The "
                    "shipped Charon shell dropped NO ordinary Misc loot; the "
                    "strongbark re-clone inherits a 75/13/1.6 roll, which is an "
                    "encounter-level loot INCREASE on the encounter behind Will's "
                    "R-100 #10, shipping beside b84's loot-volume TRIM lane."
                    % (_ORM, _slot, ch))

    # ---- 2g. THE ESCORT LOOKS AND FIGHTS LIKE WHAT THE DOCS CALL IT ---------
    #      CORRECTION 17: the junglecreep donor's entire rotation was one
    #      five-projectile POISON burst (`beetlebile_vomitbile`) at MediumRange,
    #      under docs describing "a ground-hugging whipping vine ... maximum
    #      silhouette contrast". The donor was picked for its rig, not its kit.
    _b_slots = {_n(gv(_BRIAR, 'skillName%d' % i)) for i in range(1, 25)}
    _b_casts = {_n(gv(_BRIAR, 'specialAttack%sSkillName' % s))
                for s in ('', '2', '3', '4', '5')}
    if _n(_DEAD_BRIAR_SKILL) in (_b_slots | _b_casts):
        problems.append(
            "%s still carries the junglecreep donor's beetle-bile burst (%s). The "
            "escort ships as a briar beside a grasping-root boss; a ranged "
            "beetle-bile spitter is neither ground-hugging nor whipping, and the "
            "docs say it is both." % (_BRIAR, _DEAD_BRIAR_SKILL))
    if _n(_SK_QUILLBARB) not in _b_slots:
        problems.append("%s does not DECLARE %s - the barb cannot fire from a "
                        "cast slot alone" % (_BRIAR, _SK_QUILLBARB))
    if _n(_SK_QUILLBARB) not in _b_casts:
        problems.append("%s does not CAST %s - the escort would have no rotation "
                        "at all" % (_BRIAR, _SK_QUILLBARB))

    # ---- 2h. THE SOUL PETS KEEP THE SHIPPED DIFFICULTY-ROW SHAPE ------------
    #      CORRECTION 18: `_build_boss_summon` -> `_update_existing_fields`
    #      overwrote the Lyia baseline's slots from the emberoak SOURCE, so the
    #      pets took a monster's `hero_scaling` and lost all three
    #      `globalproperties_*01` rows the SHIPPED oarsman pets carried.
    for p in _PETS:
        if not resolves(p):
            continue
        rows = {}
        for i in range(1, 25):
            nm = _n(gv(p, 'skillName%d' % i))
            if nm:
                rows[nm] = db.get_field_value(p, 'skillLevel%d' % i)
        if _n(_SK_HERO_SCALING) in rows:
            problems.append(
                "%s carries a MONSTER's hero_scaling. A player's permanent pet "
                "inherited it from the emberoak source through "
                "_update_existing_fields; the shipped pets carried "
                "globalproperties_legendary01 in that slot." % p)
        for path, want_lvl in _PET_DIFFICULTY_ROWS:
            got_r = rows.get(_n(path))
            if got_r is None:
                problems.append(
                    "%s lost the difficulty row %s that the SHIPPED oarsman pets "
                    "carried (overwritten from the emberoak source)."
                    % (p, path.rsplit('\\', 1)[-1]))
                continue
            got_r = got_r if isinstance(got_r, list) else [got_r]
            if [int(float(x or 0)) for x in got_r[:3]] != list(want_lvl):
                problems.append("%s %s level=%r, expected the shipped vector %s"
                                % (p, path.rsplit('\\', 1)[-1], got_r, list(want_lvl)))

    # ---- 3. A9 RENDER CHAIN: no new art, no cross-rig swap -----------------
    for rec, donor, mesh in ((_ORM, _D_ORM, _MESH_ORM),
                             (_BLOOM, _D_BLOOM, _MESH_BLOOM),
                             (_BRIAR, _D_BRIAR, _MESH_BRIAR)):
        got_m = _n(gv(rec, 'mesh'))
        if got_m != _n(mesh):
            problems.append("A9: %s mesh=%r, expected its OWN donor's rig %s - a "
                            "cross-rig swap is the B-SOUL-PROC-2 defect class."
                            % (rec, gv(rec, 'mesh'), mesh))
        if got_m != _n(gv(donor, 'mesh')):
            problems.append("A9: %s no longer renders on the rig of its donor %s"
                            % (rec, donor))
        # SKIN: assert we ship the DONOR'S OWN texture. That is strictly stronger
        # than "this .tex has >= 2 carriers somewhere in the DB" (which a skin
        # borrowed from a DIFFERENT mesh would also pass - and cross-mesh UV is
        # exactly the 343_dark_smoke / Vort-green trap), and it is O(1) instead of
        # a 51k-record full decode inside a build gate.
        tex, dtex = gv(rec, 'baseTexture'), gv(donor, 'baseTexture')
        if _ORM_USE_SKIN_ALT and rec == _ORM:
            if _n(tex) != _n(_ORM_SKIN_ALT):
                problems.append("A9: %s skin=%r but _ORM_USE_SKIN_ALT is on"
                                % (rec, tex))
        elif _n(tex) != _n(dtex):
            problems.append(
                "A9: %s baseTexture=%r but its donor %s renders on %r. Ship the "
                "donor's OWN skin: a texture proven on a DIFFERENT mesh is the "
                "343_dark_smoke / Vort-green trap (R-125 player-surface law - a "
                "colour may only be claimed from an in-game-CONFIRMED asset)."
                % (rec, tex, donor, dtex))
        # R-126: actorHeight is a per-rig constant, INHERITED, never invented.
        # Read the expected value off this body's OWN DONOR rather than a
        # hard-coded map, so a donor swap (this lane did two) cannot leave a
        # stale constant silently passing. `_RIG_ACTOR_HEIGHT` stays as the
        # documented cross-check that the donors are still the rigs we think.
        want_h = gv(donor, 'actorHeight')
        want_h = float(want_h) if want_h is not None else _RIG_ACTOR_HEIGHT[rec]
        if abs(want_h - _RIG_ACTOR_HEIGHT[rec]) > 1e-4:
            problems.append(
                "R-126: donor %s now declares actorHeight=%s but this module "
                "documents %s for %s. The rig moved under us - re-measure before "
                "shipping, do NOT just update the constant."
                % (donor, want_h, _RIG_ACTOR_HEIGHT[rec], rec))
        got_h = gv(rec, 'actorHeight')
        if got_h is not None and abs(float(got_h) - want_h) > 1e-4:
            problems.append("R-126: %s actorHeight=%r, expected its donor's rig "
                            "constant %s (inherit, never write)"
                            % (rec, got_h, want_h))

    # ---- 4. CRASH LAWS -----------------------------------------------------
    for rec in (_ORM, _BLOOM, _BRIAR):
        if gv(rec, 'charFxPakSelfNames'):
            problems.append("CRASH LAW: %s carries charFxPakSelfNames=%r - FX go "
                            "through monster-record fields only"
                            % (rec, gv(rec, 'charFxPakSelfNames')))
        for fld in ('spawnEffect', 'deathEffect'):
            v = gv(rec, fld)
            if not v:
                continue
            if not resolves(v):
                problems.append("%s %s=%r does not resolve" % (rec, fld, v))
            elif _n(_one(db, v, 'Class')) != 'effectentity':
                problems.append("%s %s=%r is Class %r, expected EffectEntity"
                                % (rec, fld, v, _one(db, v, 'Class')))
        # every wired skill + cast resolves
        for i in range(1, 25):
            sk = gv(rec, 'skillName%d' % i)
            if isinstance(sk, str) and sk.strip() and not resolves(sk):
                problems.append("%s skillName%d=%r does not resolve (an authored "
                                "unresolved ref is a P1 on a clone)" % (rec, i, sk))
        for sfx in ('', '2', '3', '4', '5'):
            sk = gv(rec, 'specialAttack%sSkillName' % sfx)
            if isinstance(sk, str) and sk.strip() and not resolves(sk):
                problems.append("%s specialAttack%sSkillName=%r does not resolve"
                                % (rec, sfx, sk))
    # CRASH LAW: no charFxPakSelfNames on ANY Skill_SpawnPet this encounter can
    # reach - the boss kits, the escort, and the soul's own summon skill.
    reachable = {_n(_SUMMON)}
    for rec in (_ORM, _BLOOM, _BRIAR):
        for i in range(1, 25):
            v = gv(rec, 'skillName%d' % i)
            if isinstance(v, str) and v.strip():
                reachable.add(_n(v))
        for sfx in ('', '2', '3', '4', '5'):
            v = gv(rec, 'specialAttack%sSkillName' % sfx)
            if isinstance(v, str) and v.strip():
                reachable.add(_n(v))
    for sk in sorted(reachable):
        if not resolves(sk):
            continue
        if _n(_one(db, sk, 'Class')) == 'skill_spawnpet' and \
                _one(db, sk, 'charFxPakSelfNames'):
            problems.append("CRASH LAW: SpawnPet skill %s carries "
                            "charFxPakSelfNames - that is the shipped crash." % sk)
    # permanent pets: TTL must be empty
    for p in _PETS:
        if not resolves(p):
            problems.append("summon pet tier missing: %s" % p)
            continue
        ttl = db.get_field_value(p, 'spawnObjectsTimeToLive')
        if ttl not in (None, [], '') and any(
                float(x or 0) > 0 for x in (ttl if isinstance(ttl, list) else [ttl])):
            problems.append("PERMANENT PET LAW: %s spawnObjectsTimeToLive=%r, "
                            "expected empty" % (p, ttl))
    if 'ferryman' in asp._SUMMON_IDENTITY_ALLOW:
        problems.append(
            "_SUMMON_IDENTITY_ALLOW still carries 'ferryman'. The summon body is "
            "now the SAME species as the dropper (both DRX emberoak), so the F2 "
            "identity gate is green with no exemption - a retired workaround must "
            "not be carried.")

    # ---- 4b. THE SUMMON-PET REGISTRY NAMES EXACTLY ONE, CORRECT, SOURCE ----
    #      Round-1 P0: `_create_goldenbough_boss` builds these same pet paths from
    #      `charon_minion_30` earlier in the run, `_SUMMON_PET_BUILDS` was a blind
    #      append, and `run_registry_gates` judges the WHOLE list afterwards - so
    #      the superseded pair red-lined PET-STAT-MIRROR and then the F2 identity
    #      gate on a build this module's own verify() called green. Assert the END
    #      STATE here: the pets on disk can only have been built once, and it must
    #      be by us, from the terminal's donor.
    _pp = {_n(p) for p in _PETS}
    _pairs = [(s, p) for s, p in asp._SUMMON_PET_BUILDS if {_n(q) for q in p} == _pp]
    if len(_pairs) != 1:
        problems.append(
            "_SUMMON_PET_BUILDS has %d registration(s) for the soul pets %s, "
            "expected exactly 1. Every extra entry is a SUPERSEDED build that "
            "run_registry_gates will still judge - PET-STAT-MIRROR compares the "
            "live pets against a source that no longer wrote them, and the F2 "
            "soul-summon-identity gate compares meshes that no longer match. "
            "Sources currently registered: %s"
            % (len(_pairs), [p.rsplit('\\', 1)[-1] for p in _PETS],
               [s for s, _ in _pairs]))
    elif _n(_pairs[0][0]) != _n(_D_BLOOM):
        problems.append(
            "_SUMMON_PET_BUILDS registers the soul pets against %r, expected the "
            "terminal's own donor %s. The pet gates would judge the wrong source."
            % (_pairs[0][0], _D_BLOOM))

    # ---- 4c. D19: EVERY BODY THIS ENCOUNTER FIELDS CAN ACTUALLY MOVE -------
    #      Round-1 P1: the TERMINAL (the form carrying all three guaranteed
    #      rewards), both Champion escorts and the soul's permanent pet all
    #      shipped `characterRunSpeed 0.0` on `anm_quilvine`, a table that binds
    #      NO locomotion clip at all - so the reward-bearer could not chase, the
    #      escorts could not escort, and the marquee permanent summon could never
    #      follow its owner. A nonzero runSpeed is NOT sufficient evidence on its
    #      own; the rig has to bind the clip. Both halves are asserted.
    for rec, label in ((_ORM, 'phase 1'), (_BLOOM, 'the TERMINAL form'),
                       (_BRIAR, 'the Champion escort')) + tuple(
                           (p, 'the soul summon pet') for p in _PETS):
        if not resolves(rec):
            continue
        try:
            rs = float(gv(rec, 'characterRunSpeed') or 0)
        except (TypeError, ValueError):
            rs = 0.0
        if rs <= 0:
            problems.append(
                "D19 MOBILITY: %s (%s) has characterRunSpeed=%r. An immobile body "
                "cannot chase, escort or follow; the whole encounter degrades to a "
                "turret the player plinks from out of range." % (rec, label, rs))
        anim = db.get_field_value(rec, 'charAnimationTableName')
        a0 = anim[0] if isinstance(anim, list) and anim else anim
        if not (isinstance(a0, str) and a0.strip()):
            problems.append("D19 MOBILITY: %s (%s) declares no "
                            "charAnimationTableName" % (rec, label))
            continue
        if _n(a0) == _n(_BANNED_ANIM):
            problems.append(
                "D19 MOBILITY: %s (%s) sits on %s, which binds NO locomotion clip "
                "whatsoever - every body on that table is a statue regardless of "
                "characterRunSpeed. This lane bans it for placed and summoned "
                "bodies; it is legal ONLY for the quillwards wall pets, where "
                "being rooted is the point." % (rec, label, a0))
            continue
        if not resolves(a0):
            problems.append("D19 MOBILITY: %s (%s) anim table %r does not resolve"
                            % (rec, label, a0))
            continue
        _tf = db.get_fields(a0) or {}
        _runs = {k.split('###')[0] for k, tf in _tf.items()
                 if k.split('###')[0].endswith('RunAnim')
                 and tf.values and str(tf.values[0]).strip()}
        if 'unarmedRunAnim' not in _runs:
            problems.append(
                "D19 MOBILITY: %s (%s) is weaponless and its anim table %s binds "
                "no unarmedRunAnim (rows with locomotion: %s). Raising runSpeed "
                "would ask the rig for a clip it does not have - the "
                "B-SOUL-PROC-2 class." % (rec, label, a0, sorted(_runs) or 'NONE'))

    # ---- 4d. NO END-TO-END VITALITY WALL ----------------------------------
    #      The design's headline is that phase 1 benches the mod's marquee
    #      bleed/vitality line and phase 3 hands it back. `defensiveLife` is
    #      VITALITY resistance; round 1 shipped 100 on BOTH forms, which walls it
    #      for the entire fight and makes the headline false. The terminal must
    #      leave a real opening.
    _vl = float(gv(_BLOOM, 'defensiveLife') or 0)
    if _vl >= 100.0:
        problems.append(
            "%s defensiveLife=%r. That is 100%% VITALITY immunity on the TERMINAL "
            "form, so the bleed/vitality build benched by phase 1's bleed immunity "
            "never gets its kill - the fight's whole stated shape would be a lie, "
            "and 'no walls' would be false." % (_BLOOM, _vl))
    if float(gv(_BLOOM, 'defensiveBleeding') or 0) > 0:
        problems.append(
            "%s defensiveBleeding=%r - bleed immunity must NOT carry to the "
            "terminal; that is the reversal the whole fight is built on."
            % (_BLOOM, gv(_BLOOM, 'defensiveBleeding')))

    # ---- 5. THE ESCORT LIFE INVARIANT (the live defect this wave kills) ----
    #        R-100 #18 as a measurable field. Stated over EVERY mod-authored
    #        Champion escort, not just ours, because the roster grows.
    for name in db.record_names():
        base = _n(name).rsplit('\\', 1)[-1]
        if not (base.startswith('svc_') and base.endswith('.dbr')):
            continue
        if _n(_one(db, name, 'monsterClassification')) != 'champion':
            continue
        life = db.get_field_value(name, 'characterLife')
        if not isinstance(life, list) or len(life) < 3:
            continue
        vals = [float(x or 0) for x in life[:3]]
        if not (vals[0] < vals[1] < vals[2]):
            problems.append(
                "CHAMPION ESCORT LIFE NOT ASCENDING: %s characterLife=%r. Life "
                "must rise Normal -> Epic -> Legendary; the shipped Charon escort "
                "was [878, 300, 400] and read to Will as 'super weak ... just like "
                "normal guys' (R-100 #18)." % (name, life))

    # ---- 6. MARKERS + MINION LAW ------------------------------------------
    for rec, want in ((_ORM, 1), (_BLOOM, 1), (_BRIAR, 0)):
        got_v = gv(rec, 'DisplayAsQuestItem')
        if got_v is None or int(float(got_v)) != want:
            problems.append("%s DisplayAsQuestItem=%r, expected %d "
                            "(uber_quest_markers R-100 #7)" % (rec, got_v, want))
    if int(gv(_BRIAR, 'dropItems') or 0) != 0:
        problems.append("%s dropItems=%r - a placed add must not be a loot faucet "
                        "(R-125 minion law)" % (_BRIAR, gv(_BRIAR, 'dropItems')))
    if gv(_BRIAR, 'treasureProxyName'):
        problems.append("%s carries treasureProxyName=%r - escorts drop no chest"
                        % (_BRIAR, gv(_BRIAR, 'treasureProxyName')))

    # ---- 7. TAGS: every referenced display tag has a string ----------------
    for rec, tag in ((_ORM, _TAG_ORM), (_BLOOM, _TAG_BLOOM), (_BRIAR, _TAG_BRIAR)):
        if _n(gv(rec, 'description')) != _n(tag):
            problems.append("%s description=%r, expected %s"
                            % (rec, gv(rec, 'description'), tag))
        if not str(tags.get(tag, '')).strip():
            problems.append("tag %s has no string (arz + Text are a coupled "
                            "deploy; validate_tags is a build gate)" % tag)
    for tag in (_TAG_HOARD, _TAG_SOUL, _TAG_SOUL + 'DESC', _TAG_SUMMON,
                _TAG_SUMMON + 'DESC', _TAG_PET, _TAG_AMULET, _TAG_AMULET_DESC):
        if not str(tags.get(tag, '')).strip():
            problems.append("tag %s has no string" % tag)
    if 'charon' in str(tags.get(_TAG_ORM, '')).lower() or \
            'ferryman' in str(tags.get(_TAG_ORM, '')).lower():
        problems.append("the phase-1 display string %r still reads as Charon - "
                        "this wave exists because Will said the boss is "
                        "indistinguishable from the base Charon."
                        % tags.get(_TAG_ORM))
    if _n(tags.get(_TAG_ORM)) == _n(tags.get(_TAG_BLOOM)):
        problems.append("both forms share one display string - the phase turn "
                        "must read on screen (the shipped encounter's own defect)")
    # R-231-G #4: the traveler NPC that SENDS the player here is a player-facing
    # label owned by the monolith's HELOS_HUB_OUTBOUND table, and it still read
    # "Traveler: Golden Bough (Charon)" after three rounds. Asserted only when the
    # monolith has actually run (the standalone negtest starts with empty tags), so
    # this can never red a static harness while still holding in a real build.
    _trav = str(tags.get(_TAG_TRAVELER, ''))
    if _trav and 'charon' in _trav.lower():
        problems.append(
            "the traveler NPC that sends the player to this forecourt is still "
            "named %r (%s). It is a player-facing label, and this wave exists "
            "because Charon stops being what lives here. Retarget the string in "
            "HELOS_HUB_OUTBOUND - the record path and the tag KEY stay frozen, so "
            "no map rebuild is implied." % (_trav, _TAG_TRAVELER))

    # ---- 7b. NAME COLLISION: the boss's name is not already someone else's ---
    #
    # The ratified spec named this boss ORMENOS. `Ormenos` is the China Telkine -
    # `boss_chinatelkine_ormenos_{38,41,44}` plus `controller_ormenos`, six
    # `ormenos_*` boss skills, three `ormenos_magmasprite_*` minions,
    # `Ormenos_FireSpawn_FX` and its OWN soul at `soul\telkine\ormenos_soul_*`:
    # 59 records. Shipping a second, unrelated Ormenos with its own soul is the
    # duplicate-identity class Will keeps filing, so the name is now AKREMON and
    # this gate makes the mistake unrepeatable. It checks the NAME TOKEN against
    # the live record namespace, ignoring the records this module itself owns.
    _ours = {_n(x) for x in (_ORM, _BLOOM, _BRIAR, _SUMMON, _SPLIT)} \
        | {_n(x) for x in _PETS} | {_n(x) for x in _SOUL_TIERS}
    for token in _NAME_TOKENS:
        foreign = sorted(n for n in _names
                         if token in n and n not in _ours)[:6]
        if foreign:
            problems.append(
                "NAME COLLISION: this wave's display name contains %r, but %d "
                "record(s) it does not own already carry that token, e.g. %s. A "
                "second unrelated monster wearing an existing boss's name (with "
                "its own soul) is the duplicate-identity defect class - pick a "
                "name the database does not already use."
                % (token, len(foreign), foreign))
    for tag in (_TAG_ORM, _TAG_BLOOM, _TAG_BRIAR, _TAG_SOUL, _TAG_SUMMON, _TAG_PET):
        s = str(tags.get(tag, ''))
        if 'ormenos' in s.lower():
            problems.append(
                "tag %s = %r still says 'Ormenos', which is the China Telkine "
                "(boss_chinatelkine_ormenos_*, 59 records, own soul)." % (tag, s))

    # ---- 8. THE KIT IS NOT THE BASE BOSS'S KIT (Will's actual complaint) ---
    #
    # Stated precisely, because "zero shared skills" would be WRONG: boss_scaling,
    # all_hpscaling_passive, boss_conversionimmunity, armor_passive and the
    # globalproperties_* rows are universal Boss plumbing that every uber in the
    # mod carries. The complaint was never about plumbing - it was that the
    # SIGNATURE kit was byte-for-byte `boss_charon_43` / `boss_charonform2_43`.
    # So the invariant is: NO `charon_*` signature skill, in any skill slot or any
    # AI cast slot, on either form; and ZERO overlap in the cast ROTATION, which is
    # what a player actually sees the boss do.
    def _sig(rec):
        out = set()
        for i in range(1, 25):
            v = gv(rec, 'skillName%d' % i)
            if isinstance(v, str) and v.strip():
                out.add(_n(v))
        return out

    def _rotation(rec):
        out = set()
        for sfx in ('', '2', '3', '4', '5'):
            v = gv(rec, 'specialAttack%sSkillName' % sfx)
            if isinstance(v, str) and v.strip():
                out.add(_n(v))
        return out

    for rec in (_ORM, _BLOOM, _BRIAR):
        charon_sigs = sorted(p for p in (_sig(rec) | _rotation(rec))
                             if p.rsplit('\\', 1)[-1].startswith('charon_'))
        if charon_sigs:
            problems.append(
                "IDENTITY REGRESSION: %s still carries the base Charon signature "
                "skill(s) %s. Will's order (2026-08-11) was that this boss is "
                "'pretty much identical to the base game charon boss we cloned him "
                "off' - the signature kit is exactly what had to go."
                % (rec, charon_sigs))
    for rec, base in ((_ORM, _CH + r'\boss_charon_43.dbr'),
                      (_BLOOM, _CH + r'\boss_charonform2_43.dbr')):
        if not db.has_record(base):
            continue
        shared = sorted(_rotation(rec) & _rotation(base))
        if shared:
            problems.append(
                "IDENTITY REGRESSION: %s casts %d of the same ability/-ies as the "
                "base boss %s (%s). The AI cast rotation is what the player "
                "actually sees, so it must not overlap." % (rec, len(shared), base, shared))

    # ---- 9. DURABILITY STAYS INSIDE THE KILLABLE-UBER BAND -----------------
    #
    # Anchored on the LIVE Gaoler rather than a constant, so the band tracks the
    # roster instead of going stale. docs/reports/gaoler_variance_rca.md is the
    # named reference frame: two forms, 35,000 on Epic, six-strong guard horde,
    # verdict hard-but-fair and killable, "no action warranted". This encounter is
    # two forms + two Champions with no racial pet-damage reduction and no
    # life-drain cascade, so it must not out-tank him.
    _GAOLER = [r'records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr',
               r'records\xpack\creatures\monster\gigantes'
               r'\um_polisgaoler_unbound_99.dbr']

    def _epic(rec):
        v = db.get_field_value(rec, 'characterLife')
        v = v if isinstance(v, list) else [v]
        try:
            return float(v[1] if len(v) > 1 else v[0] or 0)
        except (TypeError, ValueError, IndexError):
            return 0.0

    if all(resolves(g) for g in _GAOLER):
        ref = sum(_epic(g) for g in _GAOLER)
        ours = _epic(_ORM) + _epic(_BLOOM)
        if ref > 0 and ours > ref * 1.15:
            problems.append(
                "DURABILITY: this encounter totals %.0f life on Epic across its "
                "two forms against the Gaoler's %.0f - %.2fx. The Gaoler is the "
                "ratified 'hard but fair, killable' reference (gaoler_variance_rca"
                ".md, no action warranted) and he brings SIX guards to our two. "
                "Anything materially above him is a wall, and the order asked for "
                "a hard fight, not an unkillable one." % (ours, ref, ours / ref))
        if ref > 0 and ours < ref * 0.55:
            problems.append(
                "DURABILITY: this encounter totals only %.0f life on Epic against "
                "the Gaoler's %.0f (%.2fx). Will's order was that the Golden Bough "
                "uber be a REAL uber; a pushover is its own kind of failure."
                % (ours, ref, ours / ref))
    for rec, life in ((_ORM, _ORM_LIFE), (_BLOOM, _BLOOM_LIFE)):
        got_l = db.get_field_value(rec, 'characterLife')
        got_l = got_l if isinstance(got_l, list) else [got_l]
        vals = [float(x or 0) for x in got_l[:3]]
        if len(vals) < 3 or not (vals[0] < vals[1] < vals[2]):
            problems.append("%s characterLife=%r must rise Normal -> Epic -> "
                            "Legendary" % (rec, got_l))

    if problems:
        raise SystemExit("charon_rework.verify FAILED:\n  " + "\n  ".join(problems))

    print("  charon_rework.verify: OK (proxy chain resolves to Akremon + 2 "
          "Handbriars on BOTH the forecourt and the TESTHUB yard; Golden Bough "
          "guaranteed on the terminal; hoard + world chest + orb intact; soul "
          "re-THEMED on the frozen tiers - 0 surviving ferryman cold/vitality/"
          "life-leech/fear/%-current-life fields, fire+pierce present, no stale "
          "itemSkillAutoController; the granted summon wears the flame-ring glyph "
          "and its own family's cast sound, not Charon's drowned spirit and not "
          "Lyia's Maenad; boss_scaling swapped in with hero_scaling gone; A9 clean "
          "on 3 own-rig clones with "
          "no invented actorHeight; 0 charFxPak, 0 dangling skill refs, permanent "
          "pets TTL-free; no 'ferryman' exemption; EXACTLY ONE summon-pet "
          "registration and it names the terminal's own donor; all 6 placed and "
          "summoned bodies D19-MOBILE on tables that bind unarmedRunAnim; no "
          "end-to-end vitality wall; no display-name collision with a live record "
          "family; Epic durability inside the Gaoler-anchored band AND beat 2 "
          "carrying 0 inherited absorption / 0 regen with only an authored "
          "physical modifier on every one of its 20 rows; ordinary loot banded - "
          "0 act-1/2/3 tables reachable on either form, terminal on act-4, shell "
          "muted; the escort fires briar barbs with 0 beetle-bile left; the 3 soul "
          "pets carry the shipped globalproperties difficulty vectors and 0 "
          "hero_scaling; every svc_* Champion escort has strictly ascending life; "
          "0 charon_* signature skills and 0 shared cast rotation vs "
          "boss_charon_43 / boss_charonform2_43)")
