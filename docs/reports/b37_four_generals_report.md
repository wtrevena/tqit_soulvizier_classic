# build37 four_generals - HADES' GENERALS UPGRADE (registry module) - implementer report

Round 1 (salvage + finish + gate). Branch `feat/b37-four_generals`. Module owner scope:
`tools/patches/four_generals.py` + this report + probes only. The monolith
(`apply_svc_patches.py` / `build_svc_database.py`) was touched ONLY by the merged
`feat/patches-registry` seam, never by this wave.

Spec: `scratchpad/specs/four_generals_upgrade_spec.md` (DESIGN) + the binding
`WILL_DECISIONS_2026-07-11` FOUR GENERALS block.

## What shipped in the module

Package (c) BOTH, per Will's binding decision. All DB-side; the map lane owns the 0x05
placements (see MAP DELTAS). Everything is a registry module that runs AFTER the monolith
over the same `db`/`tags`, then the full gate battery runs over the assembled db.

1. **Archer muster (Will's ask)** - 3 `Skill_SpawnPetMonster` clones of
   `nehebkau_summonscorpions`, one per general, spawning the theme-matched Grandmaster
   Archer skin (`{ar,br,cr}_masterarcher_42`). petLimit 3, burst 3, **finite TTL 20**
   (quest-safety, spec 2.3 - nehebkau ships no TTL, we add one), cooldown ~20. Plus a
   bigger marshal muster (petLimit 5, all three skins).
2. **General ability upgrades (ADDITIVE, quest-safe spec 2.1)** applied to BOTH kit
   variants (`_45` and `_47`) of each general:
   - Dysnomion (a): muster on `skillName6` + the present-but-empty `specialAttack2`
     (in-place set of chance 0->35, range LongRange->AnyRange, per spec) + a `lifedrain`
     leech flourish on `skillName7`/`specialAttack3` (his kit was the thinnest).
   - Makaria (b): muster on `skillName9` + the clean-add `specialAttack3`.
   - Trophonios (c): muster on `skillName9` + `specialAttack4` (boss-proven slot) AND a
     redundant `specialAttack5` as the pre-wired autocast fallback (Will's QA-watch:
     sa4 must be confirmed firing in-game; petLimit 3 caps the total either way).
   NO path/classification/proxy/pool change; no field removed. The 3 quest proxies/pools
   are byte-untouched. Quest identity preserved.
3. **Menoetes, Marshal of the Dead** (the 4th general / uber) - clone of the machae Hero
   `xhero_aorg_45` -> Boss, L[50,66,80], HP **[26000,32000,40000]** (Will's binding value,
   above the generals' real build36 [20244,25305,30366] at every difficulty), scale 2.0,
   `MachaeHero01.msh` rig, Hades' black-smoke identity (initialSkillName shadow-cloud aura +
   `charFxPakRunningNames` shroud - the Enslaver B5 route), apex boss orb
   (`genericbossorb_04`), war-council kit (hadesbolt/spiritbolt-ring/groundbreaker/lifedrain
   + the archer muster on sa5) + boss immunities/scaling.
4. **6 honor-guard champions** (2 per general) - clones of the theme-matched machae warden
   Champion, laddered to [42,58,72], soul loot cleared (Champion = no soul, orb/soul law),
   named (amgoz V9 phonetics).
5. **Placements as SEPARATE proxies** (quest-invisible, spec 2.2): 3 guard-pair
   pools+proxies (spawnMin=Max=2, championChance=0 -> exactly the 2 named guards) + the
   marshal lone-boss pool+proxy (spawnMax=3/championChance=100/championMin=Max=2 = 1 boss +
   2 grandmaster-archer champion escorts, the boss-guarantee LAW) + a TESTHUB yard copy.
   `difficultyLimitsFile = limit_bloodtoxeus` ([1..110]) contains the L80 marshal. All
   registered in `mono._MOD_AUTHORED_SPAWN_PROXIES` so the spawn-eligibility gate covers them.
6. **Marshal's Command soul** - the house `_build_boss_summon` boss-soul (raise Menoetes at
   the bearer's side; source mesh == dropper mesh so the F2 summon-identity gate is
   native-clean; the hostile muster is auto-dropped from the friendly pet). Downside: a
   run-speed tax (amgoz V1 "weight of command"). Finger2 @ 66 (release rate). Hand-designed
   name `{^F}Marshal's Command` registered on the naming-gate whitelist.
7. **General-soul enrichment (spec 5.1)** - a light amgoz-V1 downside added in-place to each
   of the 3 EXISTING shipping general souls (`soul\machae\{dysnomion,makaria,trophonios}`),
   keeping name/skill/augments/drop-wiring intact:
   - dysnomion: `characterDefensiveAbility` -25/-35/-45 (base 0.0 -> additive).
   - makaria: `characterLife` -90/-130/-180 (base 0.0 -> additive).
   - trophonios: `characterMana` (energy) -40/-60/-80 - SEE THE FIX BELOW.

## Ground-truth fix found + applied this round (the salvage delta)

The prior attempt's trophonios downside wrote a negative onto **`defensiveFire`**. Byte-probe
of the build36 arz proved that soul ALREADY carries a positive `defensiveFire` = **32/41/51**
(n/e/l) - its signature +fire-resist upside. `_setf` on a present field OVERWRITES, so the
prior code would have replaced +32 fire res with -8 (a ~40-point swing), gutting the soul's
upside instead of adding a light downside - a direct violation of spec 5.1 ("touch ONLY the
one ADDED downside field; keep the upsides intact"). No gate catches this (it is a semantic,
not structural, defect). FIX: the trophonios downside now rides **`characterMana`** (max
energy, base 0.0 on the record -> purely additive), the spec's own `-characterEnergy`
alternative, thematically "the oracle's fire runs hot and burns the bearer's own energy". The
+fire-res upside is preserved. dysnomion (`characterDefensiveAbility`=0) and makaria
(`characterLife`=0) were already clean additive writes - verified by the same probe.

## Quest safety (spec 2, byte-verified)

Quest `xSQ27` tracks the 3 generals via `Condition_KillAllCreaturesFromProxy` on the 3 proxy
records. This module's general edits are ADDITIVE field-writes on the MONSTER records only
(plus Dysnomion's in-place set of the two present-but-empty sa2 fields); it never changes a
record path, `monsterClassification`, a proxy, or a pool. Guards + the marshal are SEPARATE
proxies (invisible to the quest counters). Summoned archers are TTL+petLimit-bounded pets
(nehebkau precedent), not proxy creatures. NO Quests.arc change, no new QUESTS-registry entry.
The module's `_self_check` asserts each general stays Quest-class and keeps `chanceToEquipFinger2 > 0`.

## Collision note (skill_quality)

Per the manifest ordering note, four_generals must run BEFORE skill_quality. I read the
committed `feat/b37-skill_quality` module: it edits souls keyed by `tagSoulName*` and does NOT
touch `tagSoulName248/249/250` (the general souls), nor the `soul\machae\` path, nor
dysnomion/makaria/trophonios - so the two modules are DISJOINT on the general souls (no record
collision). At THIS build only `four_generals` is in REGISTRY, so no cross-module collision
runs at all. One shared-skill note: this module adds two `lifedrain` references (Dysnomion sa3
+ the marshal kit), nudging the tracked over-share WARN to `lifedrain.dbr=19`; that is a
tracked-not-failed quality WARN, and skill_quality's own lifedrain-split pass (WILL_DECISIONS
GRANTED-SKILL block) is the wave that reduces it. No action needed here.

## MAP DELTAS (for the map lane - this module only creates the DB proxy records)

The map lane injects these proxies as 0x05 instances (AE-native v11 branch, base AE
`Area08_HadesPalace` levels, NOT grid-shifted; survey on-mesh at implement):
- `records\drxmap\proxy\q_general_a_guardpair.dbr` -> `hadespalace_crystal_03.lvl` (flank Dysnomion)
- `records\drxmap\proxy\q_general_b_guardpair.dbr` -> `hadespalace_floor04_04.lvl` (flank Makaria)
- `records\drxmap\proxy\q_general_c_guardpair.dbr` -> `hadespalace_crystal_04.lvl` (flank Trophonios)
- `records\drxmap\proxy\q_hadesmarshal_lone.dbr` -> `hadespalace_floor_03.lvl` (the CENTRAL hall,
  Will's binding placement decision - the marshal met mid-wing among his generals)
- `records\drxmap\proxy\q_yard_hadesmarshal.dbr` -> TESTHUB yard (local-only, SVC_TEST_HUB)

## Deploy coupling

arz + Text ship together (new tags: marshal name/soul/desc/summon + 6 guard names; NO
general-soul tags - they already ship at tagSoulName248/249/250). The placements are inert
until the map lane injects them, so the map ships in the same build37 wave. No Quests.arc change.

## Gate results

Isolated in-memory test (`tools/patches/test_four_generals.py` over the build36 arz): ALL
GATES PASS (naming, boss-kit clone-shape, spawn-eligibility [22 proxies], soul-leak,
soul-augment, soul-itemskill-activation, F3 granted-skill diversity, PET-STAT-MIRROR,
PET-GEAR-PARITY, PET-SKILL-KIT [no hostile spawner on a friendly pet], F2 soul-summon-identity).

Full `build_svc_database.py` gate build (monolith + registry + full battery + post-write
A9/container/B-SUMMON-1/F2, Resources-populated so A9+F2 run): <FILLED AFTER BUILD>.

## Probes

`tools/patches/probe_four_generals.py` reproduces the ground-truth checks against the build36
arz. Ad-hoc soul-field probes (this round) confirmed the trophonios `defensiveFire`=32/41/51
finding and the additive-safety of the dysnomion/makaria downside fields.
