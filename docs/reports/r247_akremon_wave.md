# R-247 wave - Akremon enhanced, Lethaeus escalated, the Endless Hunt made whole
## Lane `feat/akremon-enhancement` (round 1) - content brief + audit table + decisions

**Creative bar:** this brief is held to `amgoz1_design_voice.md` (the standing
creative-bar reference per Will 2026-07-11: monster-identity-driven, evocative,
"crazy visually and gameplay-wise", never generic filler). Every kit choice
below is justified by the monster's IDENTITY, every name is in that voice, and
every asset claim is limited to in-game-confirmed material.

Ground truth: the shipped arz `a86afc15` (build90). Probes:
`tools/debug/r247_boss_form_audit.py`, `tools/debug/r247_hunt_chain_probe.py`.

---

## 1. AKREMON (R-247 rulings 1+2) - `tools/patches/charon_rework.py` amended

### Measured shipped state (the defect, in numbers)

| | phase 1 (Grasping Root) | terminal (Heartwood Ablaze) |
|---|---|---|
| scale / mesh | 2.8 / Ascacophus02 | **2.0** / emberoakmesh |
| life n/e/l | 13/17/22k | 14/18/24k |
| hand | 300-400 | **218.75-276.25** |

The FINAL form was visibly smaller and hit ~31% softer - exactly Will's "got way
smaller and turned into a different character completely who was much much
weaker". The R-231-E durability calibration (Gaoler parity, 35k Epic total) WAS
the state he ruled against.

### Shipped changes (justifications inline in the module)

* **Size:** terminal scale 2.0 -> **2.9** (strictly above phase 1's 2.8;
  = the Mnemophage-shell class; renderer band proven by Gigantes 3.5/3.8 +
  Vashkarr 3.0; actorRadius stays at the donor's 1.0 so the collision
  footprint class equals the 2.8 body Will already fought in that forecourt).
* **Power** (re-anchored on the measured Toxeus band, the tier Will farms):
  phase 1 **20/27/36k** + hand authored 300-400; terminal **26/35/47k** + hand
  **380-500** (the Enslaver's own 350-500 class). Two-form total 46/62/83k =
  1.38x the apex Enslaver single form (32.5/45/60k); the terminal alone is the
  #2 single-form HP in the 50-boss roster. `verify()`'s band gate re-anchors on
  the LIVE Enslaver record, bounds [1.0x, 1.5x].
* **Kit - the activated innovation pass (ruling 2).** The b85 kit already
  merges Typhon (thorny aura) + the razorquill line + drx_earthbind; this wave
  adds the two donors Will NAMED, cloned never edited, anim BLANKED on both
  clones (b108 castability law - the donor clips LongBlast/TidalWave are
  foreign-rig), mana-neutral by construction:
  * **THE EMBERFALL** (`svc_akremon_emberfall` <- Telkine Ormenos's
    `ormenos_energyblast`): the Heartwood shakes and the cinders FALL - the
    Telkine's marquee slow-bolt refit with authored flat fire rows (260) on
    top of its heat-shimmer slows; its own projectile FX is an orange energy
    bolt, ember out of the box. Terminal cast slot 3, displacing the donor's
    GENERIC `meleeattack` filler (asserted incumbent, chance 45 @ Medium).
  * **THE STYX UNDERTOW** (`svc_akremon_styx_undertow` <- Charon's
    `charon_tidalwave`): the arena IS Charon's old dock - the drowned river
    answers the burning tree. Cold + life + 10% current-life wave with a 35%
    total-speed slow: the fight's SECOND anti-kite lever, stacking with
    drx_earthbind. Phase 1 long-range slot (35 @ Long), displacing
    razorquill_megaburst (the quill identity survives on the terminal's
    razorquill_nova + the quillvine wall/retinue, which remain the spine).
  * R-231's "no Charon kit" identity gate COMPOSES with R-247's "merge a
    Charon move": the gate keys on `charon_*` basenames and base-rotation
    overlap; the clones are `svc_akremon_*` records. Mechanic merged, record
    identity Akremon's own.
* **Orb rename** (closes `BL-BOUGH-DEBT-4`): the whole display chain
  (proxy -> 3 pools -> 3 FixedItemContainers whose `description` was the
  base-game `xtagChest18` = "Charon's Essence") CLONED verbatim to
  `svc_akremon_orb*`; exactly ONE field changed per container: `description`
  -> minted `tagSVCChestAkremon` = **"Akremon's Essence"** (the base game's
  own "X's Essence" family: Hades'/Charon's/Typhon's). The containers keep
  `tables -> boss_charon_{n,e,l}01b` byte-equal, so R-242 rates and every
  breadth widening are untouched BY CONSTRUCTION and gated (verify 9d). The
  shared base-game chain is untouched - base Charon keeps his essence.

---

## 2. LETHAEUS (ruling 3) - `tools/patches/r247_boss_forms.py`

Measured: shell 2.9 scale / 2.4 height / 14/19/25k / 262-284 -> core **1.8 /
1.8 / 7/9.5/12.5k / 262-284** = the audit's one BLATANT boss-tier offender.
Fix (scale+power only, kit asserted intact by sentinel gate):
core scale -> **3.1**, height -> **2.4** (the shell's own rig value on the same
Epiales01 mesh - restored, not invented), life -> **16/21/28k** (strictly above
the shell everywhere; the Gaoler-form-1 class), hand -> **300-330** (strictly
above the shell's; the core's menace is its dream-kit, not its swing).

---

## 3. THE ENDLESS HUNT (rulings 5+6) - `r247_boss_forms.py` + `devourer_kit.py`

* **5(a) skeleton identity:** b98 git-archaeology: the demon body (ShadowStalker
  mesh + inline foreign-rig anim rows + race Demon) was the b98 DESIGN, not a
  drift - R-247 supersedes it. Now: **SkeletonRumorBoss.msh** (the base game's
  own giant-skeleton boss mesh, distinct from the Enslaver's GrayBlack and the
  Devourer's Golden) + **NewSkeleton_White** (pale bone = his iceheart cold
  identity AND his own pack's skin; cross-pair inside the one skeleton texture
  family, the class the Devourer proves in-game) + **anm_skeleton01** (the
  family rig) + race **Undead** + actorHeight 2.0 (the rig constant, R-126).
  All 67 inline foreign-rig `.anm` rows cleared (the A9/Dagon-frozen class;
  the module counts and prints the exact number at apply time - 67 measured in
  the round-2 build, correcting round 1's "~100" estimate).
  The Legendary `_l` variant inherits everything at clone time (ordering gated).
* **5(b) summons:** blood hounds -> **Huntsmen of the Endless Hunt**
  (`svc_hunt_huntsman_99`, in `devourer_kit.py`, the summon's owner): cloned
  from the base game's skeletal spear hoplite (GoldenSkeleton01 +
  NewSkeleton_White + 100% spear equip chain + ambush controller - one proven
  package). Same fight numbers as the coursers Will already fought (3500/4800/
  6500, 180-240). Coursers stay BUILT, unreferenced (retirement protocol).
* **6(b) spear - VERIFIED, NOT FIXED:** the shipped chain was byte-correct
  (equip 100% -> runbreaker_guaranteed_{n,e,l} -> real Weapon_Spear records;
  inline spear stances bound). Will's softened "maybe he was using a spear and
  i couldnt see it" is the likely truth. After the rig swap the chain is
  re-proven on anm_skeleton01 (108 spear rows; 7 base-game spear-wielding
  hoplites); verify() gates the whole chain.
* **6(c) his soul summons him:** a BUILD (no summon/pets existed): pets
  `toxeus_hunt_1/2/3` (12000/18000/31500 life, 110-180/165-270/290-470 hand,
  skeleton identity + spear loadout inherited from the FIXED Hunt, permanent/
  TTL-free), `summon_toxeus_hunt` granted at itemSkillLevel 1/2/3; the on-hit
  autocast controller removed. Quarry's Mark stops being the wearer's granted
  skill (one grant per soul; the summon is the family contract) - FLAGGED.
* **6(a) formula:** drop wiring measured CORRECT (Misc4 @100 via
  svc_rite_guaranteed on both hunt records, all 3 difficulty rows - Will's
  kill DID roll it). Real defect = visibility: itemClassification 'Common'
  (white name, filter-hidden, buried under the boss-kill explosion) ->
  **'Legendary'** (proven on 7 base ItemArtifactFormula records). 100% chance
  KEPT; difficulty gate NOT added (the craft is self-gated: reagents are three
  LEGENDARY souls) - flagged as a one-constant decision.
* **6(d) tiers real + visible:** epic pets x1.5, legendary x1.75 (enslaver
  18->27k / 24->42k life etc.; the Legendary summon lands at the dropper's own
  Epic-form class, under the crafted EoAT apex pet's 82k), and per-tier
  display names: base / **", Ascendant"** / **", Unbound"** (the mod's own
  escalation vocabulary). EoAT = single supra soul, permanently tier-3,
  nothing to ladder. MOD-WIDE soul tiering = Will decision, NOT implemented.
* **6(e) +all-skills law:** augmentAllLevel **1/2/3** on enslaver + Devourer +
  Hunt soul tiers, **3** on the EoAT soul (INT; the svc_e_runbreaker-proven
  field). The original `skeleton\toxeus_soul_{n,e,l}` is NOT in the ruled
  roster and is untouched - flagged as a Will question.

---

## 4. THE CLASS-WIDE AUDIT TABLE (ruling 4)

Probe: `py tools/debug/r247_boss_form_audit.py <arz>` over shipped `a86afc15`
(66 actorToSpawnOnDeath chains + 50 Boss-class um_* ubers; Epic-life band:
min 1092 / p25 9000 / median 18000 / p75 20000 / max 45000).

### Boss-tier multi-form chains (the ruling's class)

| chain (form1 -> form2) | form1 | form2 | verdict |
|---|---|---|---|
| Akremon: um_charon_ferryman_99 -> um_charonform2_ferryman_99 | 2.8 / 13-22k / 300-400 | 2.0 / 14-24k / 219-276 | **FIXED (this lane)** - R-247.1 |
| Lethaeus: um_mnemophage_99 -> um_mnemophage_core_99 | 2.9/h2.4 / 14-25k | 1.8/h1.8 / 7-12.5k | **BLATANT -> FIXED (this lane)** - R-247.3 |
| um_polisgaoler_99 -> um_polisgaoler_unbound_99 | 3.5 / 15-27k | 3.8 / 11-20k | **FLAG (borderline, untouched)** - BIGGER but lower per-form HP; the Gaoler is the RCA'd hard-but-fair reference and the very pattern R-247.3 cites as GOOD (escalation reads through scale+kit; two-form total is the design) |
| um_tantalus_99 -> um_tantalus_unbound_99 | 2.2/h2.3 / 15-27k | 2.5/h2.5 / 9-16k | **FLAG (borderline, untouched)** - same Gaoler pattern |
| boss_hades_50/52/54 -> form2 -> form3 (base game) | 28-42k | f3 18-30k, +dmg | **FLAG-note, untouched** - base-game authored arc (form3 trades life for damage 440-680); base Hades is byte-frozen per double_soul_rulings |
| boss_hades_*_old chains | - | - | unplaced legacy records; frozen |
| um_legion_28 a->b->c | asc. | asc. | OK (soul-stage ladder ascends) |
| bastien 5-form chain | asc. | asc. | OK |

### Death-echo class (NOT forms - a base-game death-add mechanic; FLAG-note only)

`um_neferkha_99 -> as_ghosthero_32` (and the whole Egyptian
mummy/priest/hero family -> mummycaptainspawn/ghostcaster/ghosthero,
em_corruptedone -> corruptedone_spawn, hanifthecruel/um_asoris -> spawn,
spawner_medium -> larvae, tricksterdummy, um_possessedboar -> spirit,
mummymage -> ghost, lillued -> lillued_big, d_reaver/svc_leinth_guard ->
bloodharpy, z_arthur -> z_toxeus [dev records]): the "form 2" is a deliberate
weak echo/add that pops out of a corpse, base-game-authored, present across
dozens of trash/hero records. Retuning them would rewrite a base-game
mechanic mod-wide - flagged as a class, untouched, NOT the R-247.3 defect
(the boss does not TRANSFORM into a weaker final boss; it dies and leaks a
minion).

### Uber band spot-check (bosses Will names as the tier)

| uber | life n/e/l | hand | note |
|---|---|---|---|
| um_toxeus_enslaver_99 | 32.5/45/60k | 350-500 | the apex anchor |
| um_toxeus_hunt_99 (+_l) | 16/22/30k | 170-280 | identity fixed this lane |
| um_bloodtoxeus_99 (Devourer) | 13/18/24k | 60-120 (+kit) | in band |
| svc_um_hadesmarshal_80 | 26/32/40k | kit | top band |
| um_helepolis_99 | 24/32/42k | kit | top band |
| um_vashkarr_99 | 12/16.5/21k | 90-150 | mid band |
| Akremon (this lane) | 46/62/83k two-form total | 300-400 / 380-500 | re-anchored |
| Lethaeus (this lane) | 30/40/53k two-form total | 262-284 / 300-330 | re-anchored |

No OTHER blatant same-class offender exists in the boss tier: the audit's
remaining BLATANT rows are all the death-echo class above or unplaced legacy
(`boss_hades_*_old`).

---

## 4b. RULING 7 - CHESTS + DEVOURER SPAWNS (`tools/patches/r247_bloodcave_rulings.py`)

### 7(a) the stash revert - before / current / after (measured both arzs)

The nerf wave is **R-240 alone** (volume). R-242 measured NOT involved (chances sat at
the pre-R-242 40.0; relic row 21.2 == the SV original byte). Solo loot ITERATIONS =
numSpawn at numberOfPlayers=1 (bracket `(3+(1.8*nP))` = 4.8 solo):

| table (tier) | SV 0.98i original | shipped build90 (R-240) | AFTER this lane |
|---|---|---|---|
| loottable_hidden_bloodcave_01 (n) | `*3.8/*4.1` = 18.2-19.7 iter | `*0.323/*0.3485` = 1.55-1.67 | **SV verbatim `*3.8/*4.1`** |
| loottable_hidden_bloodcave_02 (e) | `*3.8/*4.1` = 18.2-19.7 | `*0.361/*0.3895` = 1.73-1.87 | **SV verbatim** |
| loottable_hidden_bloodcave_03 (l) | `*3.8/*4.1` = 18.2-19.7 | `*0.399/*0.4305` = 1.92-2.07 | **SV verbatim** |
| E[items]/open (chance sum 1.81 shipped, 1.13 SV) | ~21 (SV mix) | ~2.9-3.7 | **~34 (>= SV on every axis)** |

Composition (loot1/2/5/6 chances 40.0, widened weights, svc-unique member rows, relic
row 21.2) deliberately KEPT: each value >= its SV counterpart and they carry R-181's
distribution contract + the mod's uniques. The revert class was ENUMERATED by a
both-arz numSpawn sweep over all 51,298 records: **19 records differ; 15 are uber-ORB
tables (the R-242 class - kept trimmed, gated by the module's orb sentinels), 1 is the
richer-than-SV tutorial chest, and the 3 stash tables above are the ONLY SV-original
stash-chest tables the trim reached.** Mod-authored stash chests with NO SV original
(gaoler cage, polis vault, the 27 svc_*hoard chests) stay under R-240 - FLAGGED for
Will below (decision 9). Ledger: R-240 entry amended with the carve-out
(`svc_loot_volume.R247_STASH_EXEMPT` removes the 3 tables from trim scope + V1
ceiling); R-242 entry carries a measured not-involved note.

### 7(b) the stash guard on Normal - measured verdict + hardening

The shipped bytes are **difficulty-invariant and already guarantee him** under the
mod's RE'd + negative-tested model (spawn 4/4; champions = 3 blood dragons, min=max=3
@100; name1..3 = um_bloodtoxeus_99; equation neutralized; proxy limits [1..110] N/E/L;
mains = spawnMax - championMax = 1). Will's Normal absence is NOT derivable from any
decoded DB field. Shipped hardening: per-slot `limit1..3=1` + `weight1..3=150` - the
exact byte-shape class of the in-game-proven `_BT_POOL` (the ambush that DOES deliver
the Devourer). Residual channels (engine champion-budget runtime behaviour; a
per-difficulty flag on the map INSTANCE in the TESTHUB Levels Will plays) =
`BL-R247-DEBT-6`, escalation pre-designed (dedicated solo guard proxy, q_yard shape).
The closing proof is Will's Normal-difficulty look at the stash.

### 7(c) the parchment spot - root cause + fix

TWO set-pieces share `drxFirstxistion_connection`: the b79-relocated 33% Devourer
ambush (`q_bloodtoxeus_ambush` -> 1 Devourer + 2 blood demons - wired CORRECTLY) and
the A1/build36 **Enslaver warband** (`q_enslaver_warband`, chanceToRun 100, Enslaver +
4 marauders) ~26.6u away. Will meets the 100% warband next to the parchment and reads
it as the wrong Toxeus. The old "PARCHMENT REPOINT / championChance 50->33" queue items
are NOT the cause (the 50% pool was retired 2026-07-14, never wired; the ambush IS 33).
Fix: warband `chanceToRun 100 -> 0` (dormant; the chamber = exactly the ruled state).
R-18 collision (the warband was the Enslaver's "dependable placed beat") flagged:
relocation to a deeper pocket = `BL-R247-DEBT-7`, a Will map-lane decision. His other
spawns intact + gated: rare roam (R-18-frozen), egypt/orient undead-pool rares,
TESTHUB yard @100.

## 4c. RULING 8 - THE ENSLAVER ON EPIC (measured, NO change; ledger R-247.8)

Epic `um_toxeus_enslaver_99`: level 68, life 45,000, regen 12/s, hand 350-500;
reflect = 30% @ 33% chance (svc_toxeus_passiveproperties_monster - ALREADY the
R-103/R-107-reduced value, down from 100/33), defensivePercentCurrentLife 20,
defensivePhysical 40, dodge 15, deflect 33; race Undead = leech-immune, so Will's 50%
ADCTH works on the demon adds and never on the boss, and his two Normal-tier pets
cannot outpace 12/s regen. Recorded as an OPEN TUNING QUESTION with levers listed;
no stat moved (Will: "Maybe this difficulty setting is right, idk but make note of it").

## 5. WILL DECISIONS (implemented at recommended values, one constant each)

1. **Orb name** `tagSVCChestAkremon` = "Akremon's Essence" (base-game essence
   family). Veto = one string.
2. **Hunt texture** NewSkeleton_White on SkeletonRumorBoss (cross-pair;
   Devourer-class precedent). Fallback = NewSkeleton_Yellow (this mesh's own
   proven pairing). Veto = one constant.
3. **Huntsman summons** replace the blood hounds (coursers still built,
   unreferenced). Veto = one constant in devourer_kit.
4. **Quarry's Mark** superseded by the summon on the Hunt souls (one grant per
   soul). Alternative: keep Mark, no summon - that contradicts ruling 6(c).
5. **Formula stays 100% + ungated** (craft self-gated by 3 Legendary-soul
   reagents). Veto = classification/gate constants.
6. **Tier names** ", Ascendant"/", Unbound" + tier multipliers x1.5/x1.75.
7. **Mod-wide soul tiering** (every soul in the game) - NOT implemented;
   landscape: 2,095 soul records, generated souls are single-record with
   n/e/l item tiers already; a mod-wide pet-ladder pass is a full lane of its
   own. Will call.
8. **skeleton\toxeus_soul_{n,e,l}** (the original Toxeus soul, reagent 1 of
   the Rite): not in ruling 6(d)'s roster, so no +all-skills / no summon
   retune applied. Will call whether the law extends to it.
9. **Mod-authored stash chests** (gaoler cage, polis vault, 27 svc_*hoard
   chests): NO SV original exists, so "revert to original sv" is undefined for
   them - they stay under R-240's trim (the cage was R-240's own ratified
   exemplar). If Will wants THEM at pre-R-240 richness too, that is a one-set
   extension of `R247_STASH_EXEMPT` + a target-value ruling. FLAGGED.
10. **Warband relocation** (`BL-R247-DEBT-7`): the Enslaver's dependable placed
   beat (R-18) is vacant after 7(c); recommended fix = relocate the ONE
   `EN_WARBAND_SPEC` placement to a deeper blood-cave pocket (surveyed spot,
   map lane). Will picks the destination or vetoes the beat entirely.

## 6. DEBTS (registered in BACKLOG)

* BL-R247-DEBT-1: `svc_hunt_summoncoursers` record PATH still says "coursers"
  while spawning huntsmen (frozen name, same class as BL-BOUGH-DEBT-1).
* BL-R247-DEBT-2: courser + spew records built but unreferenced pending
  Will's huntsman veto window.
* BL-R247-DEBT-3: NewSkeleton_White on SkeletonRumorBoss + on the huntsman is
  a cross-mesh texture pair not yet SEEN in-game (Devourer-class precedent
  says it works; one look closes it).
* BL-R247-DEBT-4: the Akremon merged casts (Emberfall/Undertow) + new sizes
  are byte-proven castable/banded but not yet fought in-game.
* BL-R247-DEBT-5: hunt soul summon skill uses the neutral proxy icon/portrait
  (the sanctioned unmapped-boss fallback); bespoke art is a future call.
* BL-R247-DEBT-6: the Devourer's Normal-difficulty stash absence could NOT be
  reproduced from the DB bytes (config difficulty-invariant + model-guaranteed);
  hardened to the proven pool shape. If Will's Normal look still shows him
  absent, the residual channels are (i) engine champion-budget runtime
  behaviour, (ii) a per-difficulty flag on the map INSTANCE (TESTHUB Levels) -
  next lane runs the instance-flag probe + ships a dedicated solo guard proxy
  (q_yard shape, one new INJECT_SPECS entry).
* BL-R247-DEBT-7: the Enslaver warband set-piece is DORMANT (chanceToRun 0) at
  its only placement; R-18's "dependable placed beat" is vacant. Relocation to
  a deeper blood-cave pocket = one EN_WARBAND_SPEC change + surveyed spot +
  chanceToRun restore, map lane, WILL DECISION on the destination.
