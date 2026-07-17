# b81 - PET IDENTITY PASS (round 1): race/distress-group/voice-pak alignment for every boss-summon pet

Branch `fix/runtime-green` (worktree, on top of `2a2139d` = the vetted-GO b75 shroud-swap +
Lyia-residue class-strip; extended, not reset). DB lane (`apply_svc_patches.py` +
`tools/patches/enslaver_pet_fx.py`). Ground truth: build45 LIVE-ON-DEV arz `917d9047`
(`C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
read-only). b75 branch scratch baseline `baa76edb` (2 independent builds, byte-identical,
confirmed at session start). This round's scratch build: `f639ba409562a334add231956637ac71`
(idempotent x2). Satisfies Will Ruling **R-11** (`docs/WILL_RULINGS.md`, main checkout,
not yet merged onto this branch - see Scope note at the end).

## Will's report (2026-07-16, verbatim)
> "It also says Toxeus the murderer, enslaver of souls is a beastman not a skeleton."

Third repeat-report against the SAME root class in one day: portrait (b71), then the Maenad
sound/controller residue the b71 vet enumerated but didn't fix, now RACE. Root cause named in
the brief and confirmed here: every boss-summon pet is a `_build_boss_summon` clone of Lyia
Leafsong; Lyia's own donor lineage is MAENAD (`characterRacialProfile=Beastman`), so every
un-overwritten identity field on every pet still reads Maenad - regardless of what the pet is
supposed to BE (a skeleton, a demon, a construct, an undead ghost...).

## 1. Ground-truth the race mechanism

`characterRacialProfile` is the race field (Monster.tpl/Pet.tpl), decoded off 8 real records
(6+ vanilla/SV monsters plus Lyia's own monster AND pet record):

| record | class | characterRacialProfile | distressCallGroup |
|---|---|---|---|
| `um_boneash_30.dbr` (skeleton Hero) | Monster | **Undead** | Skeleton |
| `um_kravmoloch_99.dbr` (skeleton Boss) | Monster | **Undead** | Skeleton |
| `am_soldier_02.dbr` (Satyr Common) | Monster | **Beastman** | Satyr |
| `am_marauder_05.dbr` (Centaur Common) | Monster | **Beastman** | (none) |
| `am_soldier_06.dbr` (Zombie Common) | Monster | **Undead** | (none) |
| `um_maevewaterguard.dbr` (Maenad Hero) | Monster | **Beastman** | Maenad |
| `um_lyialeafsong_18.dbr` (Lyia's own encounter monster) | Monster | **Beastman** | Maenad |
| `lyialeafsong_1.dbr` (Lyia's own PET record - the clone donor) | Pet | **Beastman** | Maenad |

This is the mechanism gear checks for "+damage vs Undead / vs Beastman / vs Demon" etc. and
for racial-resist interactions - it is not cosmetic. A dark skeleton lord reading `Beastman`
is eligible for the WRONG +damage buckets and immune to the RIGHT ones.

The Lyia PET record additionally carries `controllerAggressive/Defensive =
records\xpack\ai controllers\pet\controller_maenadmerc_{normal,defensive}.dbr` - this is the
**PET-BEHAVIOR AI controller** (a different field pair, and a different template contract,
from the source MONSTER's single `controller` field, which `_build_boss_summon` already
correctly repoints to `controller_skelly_aggressive.dbr`). See "AI controller: deliberately
NOT touched" below.

## 2. The fix (upstream, BL-103 - fixed at the builder, covers the whole class)

New `_align_pet_identity(db, path, source)` in `apply_svc_patches.py`, called from inside
`_build_boss_summon`'s per-pet loop (immediately after the b75 green-residue strip), for
**every** pet the helper builds - the same mechanism that already builds all 17 player-facing
boss summons + the 2 pet-of-pet sub-families (marauder, wyrmling), confirmed by
`_SUMMON_PET_BUILDS` at "19 summon families" in this build's PET-STAT-MIRROR/PET-GEAR-PARITY
gate output. `four_generals.py` (Hades Marshal) and `neferkha.py` call the SAME shared
`_build_boss_summon`, so the fix reaches them with no per-module change.

Source-faithful, field-by-field (mirrors `_strip_lyia_clone_green`'s philosophy, generalized
to a whole-field copy instead of a needle-match strip):
- **RACE** (`characterRacialProfile`): copied verbatim (TypedField dtype+values) from the
  pet's OWN source monster. Never hard-coded to one value - Meritamen's source is `Magical`,
  Pygmalion's is `Construct`, the Enslaver/Xeiwang/Neferkha/etc are `Undead`, the
  dragon-lich-rig bosses (Eater of Days, Long Nu, Broodmother, Voranthys, Wyrmling) are
  `Demon`.
- **distressCallGroup**: copied verbatim if the source defines it; **stripped** (field
  removed, not blanked) if the source does not define one at all (Mountainblade, Pygmalion,
  Sarpedon, Charon Oarsman, Hades Marshal, Neferkha) - a source with no distress-group means
  the pet should carry none either, never Lyia's leftover "Maenad".
- **SOUND/VOX paks** (alert/criticalHit/death/rally/rampage/stun/vox - the b55r2 vet's
  enumerated "AUDIO residue," + the paired *Chance/*Delay fields it also closes): each
  concrete field is aligned independently - if the source defines that EXACT field name, the
  pet's copy is overwritten verbatim (dtype+values); if the source does not define it at all,
  the pet's inherited Maenad value is **stripped**. This correctly produces, e.g., the
  Enslaver: `rallySoundChance`/`rampageSoundChance`/`rampageSoundDelay` copied over as `0.0`
  (the source explicitly disables rally/rampage) while the dangling `maenadrallypak`/
  `maenadrampagepak` PATHS are stripped outright (the source has no path for them at all).
- **Meritamen edge case (proves the source-faithful design, not a hard-coded exception):**
  her real source (`us_meritamen_34`, a sandspirit hero) itself carries
  `distressCallGroup=Maenad` (an SV-authorial choice, unrelated to Lyia). The pass correctly
  KEEPS "Maenad" on her pet because the SOURCE says so - not because a blanket "never Maenad"
  rule would have been wrong here. Race still corrects Beastman -> `Magical`.

### AI controller - deliberately NOT touched (documented per the brief)
`controllerAggressive`/`controllerDefensive` (= `controller_maenadmerc_normal`/`_defensive`
on every Lyia-clone pet) is **excluded** from `_is_pet_identity_field`. This is the
PET-BEHAVIOR controller (Pet.tpl AI logic: how a friendly pet fights/flees/holds), not a race
or identity surface - the source MONSTERs carry a completely different single `controller`
field with a MONSTER AI contract, already correctly repointed to
`controller_skelly_aggressive.dbr` by the existing `_build_boss_summon` code. A pet-controller
<-> monster-controller swap is not a like-for-like field copy (different field shape, different
template contract) and risks AI/behavior regressions (aggro range, flee thresholds, cast
logic) that are out of scope for an identity pass. Flagged here for a future dedicated
pet-AI-controller round if Will wants per-family pet behavior to diverge from the shared
`controller_maenadmerc` baseline every summon pet has always used.

### Loot residue - also NOT touched (out of scope, pet-field law)
`lootFinger2Item1`/`lootMisc2Item6` Maenad-flavored dormant loot refs (harmless,
`dropItems=0` on every pet) are equipment/loot-class fields - per the standing pet-field
safety law ("never equipment/loot Monster.tpl->Pet.tpl") and this task's explicit scope
(race/sound/distress only), left untouched.

## 3. Chain-gate extension (anti-oscillation, per gated family)

`tools/patches/enslaver_pet_fx.py` `_verify_chain` (the b71/b75 chain gate over the 3
formally-gated families: Enslaver soul-pet, Enslaved Marauder, Hades Marshal soul-pet) gets a
new leg, `_race_and_voice_problems(db, pet, source)`:
- pet `characterRacialProfile` must equal its OWN source's race;
- no alert/criticalHit/death/rally/rampage/stun/vox pak or `distressCallGroup` may still say
  "Maenad" **unless the source itself is Maenad** (source-faithful, mirrors the green sweep -
  a blanket "never Maenad" would be WRONG for a genuinely Maenad-sourced pet, none of which
  exist in the 3 gated families, but the check is written correctly rather than
  coincidentally).

`_CHAIN` entries gained `source`/`sub_source` keys (`_BOSS_MON`/`_MARAUDER_MON`/
`_HADESMARSHAL_MON`, already module constants) so the gate can compare each pet to its own
source. `verify()`'s docstring/print updated to name the new leg.

**Negative tests** (`scratchpad/negtest_gate.py`, extended), each MUST fail the gate:
- plant `characterRacialProfile=Beastman` on `toxeus_enslaver_1` (source is Undead) -> **FAILS**
- plant a Maenad `voxSound` on `enslaver_marauder_1` (source has no Maenad anything) -> **FAILS**
- (pre-existing b71/b75 negatives all still fail, unchanged)
- clean built arz -> **PASSES**

All 5 negative tests + the positive control ran GREEN on the real build45+b81 arz.

## 4. Per-family identity table (compact; before -> after)

**Before (every one of the 57 pets, uniformly):** `characterRacialProfile=Beastman`,
`distressCallGroup=Maenad`, alert/criticalHit/death/rally/rampage/stun/vox = Maenad paks
(the Lyia clone-donor residue).

**After** (generated straight from the fix's own source-lookup, one row per family):

| Family (pets) | Source monster | Race now | distressCallGroup now | Voice-pak family now |
|---|---|---|---|---|
| Devourer of Blood (3) | `um_bloodtoxeus_99.dbr` | Undead | Skeleton | skeletonvoxpax |
| Toxeus the Enslaver (3) | `um_toxeus_enslaver_99.dbr` | **Undead** | Skeleton | skeletonvoxpax |
| Enslaved Marauder (sub, 3) | `um_enslaver_marauder_99.dbr` | Demon | Skeleton | shadowstalkervoxpak |
| Xeiwang (3) | `um_xaiweng_48.dbr` | Undead | Skeleton | skeletonvoxpax |
| Mountainblade / Huo-ren (3) | `um_mountainblade_43.dbr` | Beastman* | STRIPPED (source: none) | dragonianshortvoxpak |
| Eater of Days (3) | `um_eaterofdays_45.dbr` | Demon | Skeleton | dragonlichvoxshortpak |
| Pygmalion (3) | `um_pygmalion_41.dbr` | Construct | STRIPPED (source: none) | automatoivoxpak |
| Sarpedon (3) | `um_sarpedon_41.dbr` | Beastman* | STRIPPED (source: none) | minotaurvoxpak |
| Long Nu (3) | `um_palai_47.dbr` | Demon | Skeleton | dragonlichvoxshortpak |
| Meritamen (3) | `us_meritamen_34.dbr` | **Magical** | Maenad† | sandspirit_voxpak |
| Broodmother (3) | `um_broodmother_99.dbr` | Demon | Skeleton | dragonlichvoxshortpak |
| Broodmother Wyrmling (sub, 3) | `um_sepulchralwyrm_common_31.dbr` | Demon | Skeleton | dragonlichvoxshortpak |
| Voranthys (3) | `um_sepulchralwyrm_31.dbr` | Demon | Skeleton | dragonlichvoxshortpak |
| Tantalus Shade (3) | `xhero_aberkios_43.dbr` | Undead | Skeleton | wraithvoxpak |
| Charon Oarsman (3) | `charon_minion_30.dbr` | Undead | STRIPPED (source: none) | ghostvoxpak |
| Mnemophage Phantasm (3) | `as_nightmare_43.dbr` | Demon | **Sprite** | epiales_vox |
| Kravmoloch Warden (3) | `um_gorrahk_99.dbr` | Undead | Skeleton | skeletonvoxpax |
| Hades Marshal (3) | `svc_um_hadesmarshal_80.dbr` | Demon | STRIPPED (source: none) | machae02_vox |
| Neferkha (3) | `um_neferkha_99.dbr` | Undead | STRIPPED (source: none) | mummyvoxpak |

`*` Mountainblade/Sarpedon's race already happened to read "Beastman" (their true source IS
Beastman) - the field is still overwritten (idempotent, byte-verified) to the source's own
value rather than left alone by coincidence; their sound/distress residue was still Maenad and
is fixed. `†` Meritamen keeps "Maenad" distress-group because her OWN source defines it
(source-faithful, see section 2) - not a miss.

19 families x 3 pets = **57 pets**, matching this build's "PET-STAT-MIRROR gate OK: 19 summon
families" / "PET-GEAR-PARITY gate OK: 19 summon families" output (the exact roster
`_SUMMON_PET_BUILDS` tracks) and the brief's "~54+ pets - the b75 roster" figure.

## 5. Verification

- **Full scratch DB build EXIT 0** (`local/build_b81.log`); all 26 registry verifies OK incl.
  `enslaver_pet_fx.verify` (b55 field + b71 chain + b75 transitive + **b81 race/voice** legs,
  all green); A7 Occult/Hunting golden freeze PASS (84 waived, 0 other, unchanged from b75);
  57 `aligned identity` log lines (exactly the 19 x 3 roster).
- **Idempotent**: two independent full builds -> arz md5
  `f639ba409562a334add231956637ac71` BOTH times.
- **Record-diff vs the b75 baseline scratch** (`local/scratch_rg2.arz`, `baa76edb`): **0
  ADDED / 0 REMOVED / 57 MODIFIED** - exactly this pass (race/distressCallGroup/sound-pak
  fields only, 9-14 fields per pet depending on how many the source itself defines), 0
  collateral, 0 shroud/portrait/green-FX/skill/equipment/loot field touched.
- **B-SUMMON-1** (`validate_summon_pets`): 279 soul summon chains, 253 pets checked, **STRICT
  failures: 0** (134 pre-existing upstream-proven WARNs, unrelated to this pass, unchanged).
- **Contracts** (souls/summons/resources) vs the b75 baseline: **IDENTICAL totals** - `TOTAL:
  11293 violations (0 P0, 576 P1, 10717 P2)` on BOTH => **0 new P0/P1/P2** (the sound-pak refs
  this pass writes are every one already-resolving on a live shipped MONSTER record - no new
  dangling ref is possible by construction, confirmed by the identical resources-contract
  count).
- **Negative tests**: 5/5 planted defects (green field, green transitive-skill, cleared
  shroud, **planted Beastman race**, **planted Maenad voxSound**) FAIL the gate as required;
  clean arz PASSES.
- **A7** (handcrafted hero souls): untouched - confirmed directly by the record-diff (all 57
  MODIFIED records are `records\skills\soulskills\pets\*`, zero A7 hero-soul paths touched).
- **Map/Quests/Text**: untouched (DB-only change; no build step for those artifacts was run
  this round since none of their inputs changed).

## 6. Scope note (WILL_RULINGS ledger)

The main checkout's working tree (a separate, concurrently-active session) has since added
`docs/WILL_RULINGS.md` (commit `5f139c3`, not yet on this branch) recording this exact task as
**R-11**: *"Toxeus the murderer, enslaver of souls is a beastman not a skeleton" - Enslaver
family race = skeleton/Undead; all boss-summon pets inherit race/sounds/distress from their
SOURCE monster.* This report satisfies R-11 in full (all 19 families, not just the Enslaver).
Per this worktree's standing instruction (work only in `fix/runtime-green`, no reset/pull),
the ledger file itself is not merged here; whoever integrates this branch should mark R-11
IMPLEMENTED with this commit's sha.

## Files changed
- `tools/apply_svc_patches.py` - new `_PET_IDENTITY_SCALAR_FIELDS` /
  `_PET_IDENTITY_SOUND_STEMS` / `_is_pet_identity_field` / `_align_pet_identity`; wired into
  `_build_boss_summon`'s per-pet loop (unconditional - runs for `protect_green=True` pets too,
  since race/voice identity is independent of the intentional-green concern).
- `tools/patches/enslaver_pet_fx.py` - `_CHAIN` entries gain `source`/`sub_source`; new
  `_race_and_voice_problems` + `_IDENTITY_VOICE_STEMS`; wired into `_verify_chain` for both
  main pets and sub-pets (against their OWN source); `verify()` docstring/print updated.
- `scratchpad/negtest_gate.py` (not committed, gitignored) - 2 new negative tests.
- `docs/reports/b81_pet_identity.md` - this report. `docs/BACKLOG.md` - B81 entry.

## What Will will see (after a full Steam restart; DISMISS + RE-SUMMON any already-summoned pet)
Every boss-summon pet's character-sheet race now matches its own identity: Toxeus the
Enslaver's skeleton pack (and every other skeleton-sourced summon - Xeiwang, Tantalus Shade,
Kravmoloch Warden, Charon Oarsman, Neferkha, the Devourer) reads **Undead**; the demon-rig
summons (Eater of Days, Long Nu, Broodmother + her wyrmlings, Voranthys, the Enslaved
Marauders, Hades Marshal, Mnemophage's phantasm) read **Demon**; Pygmalion reads
**Construct**; Meritamen reads **Magical**. +damage-vs-race gear and racial-resist
interactions now apply correctly. Every summon's alert/hit/death/stun/vox cry now matches its
own body instead of a Maenad woman's voice coming out of a skeleton or a machae. No visual
(mesh/skin/shroud/portrait/icon) or stat change - this is purely the race/audio identity
layer, verified byte-for-byte against the untouched b75 baseline.

---

# ROUND 2 (b81r2): the second Lyia-cloning lineage the round-1 vet caught

**VERDICT on round 1: NO-GO** (independently re-verified by a vet, all claims above about the
57 `_build_boss_summon` pets stood up byte-for-byte) - but the "What Will will see" claim above
that "**every** summon's ... vox cry now matches its own body" was **FALSE**. `_align_pet_identity`
was wired into `_build_boss_summon` only. A **second, older** Lyia-cloning summon-pet lineage
exists in `apply_svc_patches.py`: six standalone `_create_X_pet_skill` builders
(`_create_boneash_pet_skill`, `_create_pharaoh_guard_pet_skill`, `_create_bwpriest_pet_skill`,
`_create_lillued_pet_skill`, `_create_rakanizeus_pet_skill`) plus the generic
`_create_boss_summon_from_source` (`_A10_BOSS_SUMMONS` = Narok the Rockskin + Vort the Red) -
7 families / 21 pets - clone `lyialeafsong_{1,2,3}` exactly like `_build_boss_summon` does, but
`_align_pet_identity` was never called from any of them. Every one of the 21 pets still carried
Lyia's Maenad `distressCallGroup` + alert/criticalHit/death/rally/rampage/stun/vox sound paks
(race happened to already be hand-corrected by the original authors in all 7 cases, so only the
distress-group/sound layer was residue - the same class of bug, one layer down).

**Ground-truthed independently** (not assumed from the round-1 pattern): decoded each of the 7
families' own SOURCE monster (the record each builder already names for anim/skill copying) for
`characterRacialProfile` + `distressCallGroup` + the 7 sound-pak stems, confirming exactly what
each pet's post-fix state must be:

| Family (pets) | Source monster | Race (unchanged) | distressCallGroup (fixed) | Sound-pak family (fixed) |
|---|---|---|---|---|
| Boneash (3) | `um_boneash_30.dbr` | Undead | Skeleton | skeleton*pak |
| Narok the Rockskin (3) | `um_rockskin_42.dbr` | Beastman | STRIPPED (source: none) | dragonianshortvoxpak |
| Vort the Red (3) | `hero_tarthon_na'arak_40.dbr` | Beastman | STRIPPED (source: none) | dragonianshortvoxpak |
| Pharaoh's Honor Guard (3) | `boss_pharaohshonorguard1_31.dbr` | Construct | STRIPPED (source: none) | guardian*pak (egypt) |
| Blood Witch High Priest (3) | `discipleboss_bladedancer.dbr` | Demon | DuneRaider | melinoe_*pak |
| Lil'Lued the Elder Djinn (3) | `lillued_big.dbr` | Demon | Sprite | djinn*pak |
| Rakanizeus (3) | `um_rakanizeus_17.dbr` | Beastman | Satyr | satyr*pak |

**Fix (same mechanism, extended to the second builder, per the vet's remedy option (a)):** each
of the 7 functions now calls the SAME `_align_pet_identity(db, path, source)` from round 1,
immediately after its existing anim/skill copy, against the SAME source record it already names.
Zero new code paths; the proven-safe, already-vetted mechanism is simply reached from 7 more
call sites. `_create_boss_summon_from_source` (Narok/Vort) already had `source` in scope from its
existing anim/skill-copy call; the other 6 gained the call inside their existing
`if <source>_monster:` guard.

**Third category audited, not code-changed (per the vet's remedy option (a): "auditing
lyialeafsong/alethadarkclaw/phagia as legitimately Maenad"):** a full sweep of all 222 records
under `records\skills\soulskills\pets\` in the round-1 arz (not assumed from the vet's list -
independently re-derived) found 43 records still flagging `distressCallGroup=Maenad` or a Maenad
sound pak. After the 7-family/21-pet fix above, 22 remain, in 5 accounted-for buckets, NONE of
which is our own Lyia-clone bug:
- **`lyialeafsong_{1,2,3,18}` (4)** - Lyia herself, the clone DONOR. Correctly Maenad (nothing to
  fix; this is the source of the residue, not an instance of it).
- **`meritamen_{1,2,3}` (3)** - already handled correctly in round 1 (her real source
  `us_meritamen_34` itself defines `distressCallGroup=Maenad`; source-faithful, not a miss).
- **`alethadarkclaw_*` (7: `alethadarkclaw`, `_1`, `_2`, `_3`, `_e`, `_l`, `_n`)** - NOT built by
  any function in this file. Present verbatim in the raw upstream SV 0.98i database (confirmed
  by loading `upstream/soulvizier_098i/Database/database.arz` directly and finding the exact same
  record names) - genuine SV-authored content, not a Lyia-clone artifact of ours. Her own source
  monster is `records\creature\monster\maenad\um_alethadarkclaw.dbr` - she literally IS a Maenad
  (`characterRacialProfile=Beastman`, `distressCallGroup=Maenad`, every sound-pak stem =
  `maenad*.dbr`). Decoded field-by-field: her pet already matches the source byte-for-byte.
  LEGITIMATELY Maenad; correctly left untouched. Player-reachable (`alethadarkclaw_soul_{n,e,l}`
  under `\soul\maenad\` and `\soul\test\` grant `summon_aletha` -> spawns `alethadarkclaw_{1,2,3}`).
- **`helike_{1,2,3,46}` (4)** - also NOT built by any function in this file; also genuine upstream
  SV 0.98i content. Her source is `records\xpack\creatures\monster\empusa\xhero_helike_46.dbr`
  (Demon, with its OWN `empusa_alert/death/stun/vox` paks) - but the source monster ITSELF
  defines `distressCallGroup=Maenad` (an SV-authorial choice on the empusa, same shape as
  Meritamen's sandspirit source). New `_align_helike_identity(db)` (called once, standalone,
  from the same place `_fix_bloodhound_dyingfxpak` runs, since there is no shared builder to hook
  for upstream-native content) runs the SAME `_align_pet_identity` against `helike_1..3`: result
  is **0 fields changed** - Helike was ALREADY correctly sourced (SV 0.98i itself used the real
  empusa paks, not a Lyia clone, for this one) - confirmed, not fixed, and now permanently
  gated so a future regression here is caught. (`helike_46` is a 4th pet record referenced by
  nothing - orphaned, same as `phagia` below - left untouched.)
- **`phagia_{1,2,3,34}` (4)** - built upstream in SV 0.98i, but **orphaned**: a full sweep of
  every `itemSkillName` in the built .arz found zero live grants of `summon_phagia` (the only
  skill that would spawn these pets). The build36 F2 fix ("Meritamen the Shadowcaller", searched
  above in this same file) intentionally repoints the only souls that ever granted it
  (`phagia_soul_{n,e,l}`) to `summon_meritamen` instead (a documented SV name/summon
  conflation fix, not a regression). No player action can currently summon a Phagia pet. Left
  untouched (not deleted, per the RETIREMENT PROTOCOL - dead-but-present); registered as BACKLOG
  debt below rather than silently dropped.

**Chain-gate extension** (`tools/patches/enslaver_pet_fx.py`): new `_SECOND_BUILDER_ROSTER` (the
7 fixed families + Helike, 8 families / 24 pets total by their own source monster) and a new leg
in `verify()` that calls the SAME `_race_and_voice_problems` (round-1, unchanged) over every pet
in the roster - reusing proven code rather than duplicating gate logic. 2 new negative tests in
`scratchpad/negtest_gate.py` (plant Beastman race on `boneash_1`; plant Maenad voxSound on
`narok_1`) both FAIL the gate as required; all 5 round-1 negatives + the positive control still
pass unchanged (7/7 total).

**Verified** (independent full scratch build, `local/scratch_b81r2.arz`):
- Build EXIT 0; all 17 registry verifies OK incl. `enslaver_pet_fx.verify: ... second-lineage
  race/voice gate OK: 24 pets across 8 families, b81r2`; A7 golden PASS (84 waived, 0 other,
  unchanged).
- **Idempotent**: two independent full builds -> arz md5 `e77846c3a43cadbfc5af0720ce0fa8ef` BOTH
  times.
- **Record-diff vs the round-1 baseline** (`local/scratch_b81.arz`, `f639ba409562a334add231956637ac71`):
  **0 added / 0 removed / 21 modified** - exactly the 7 families x 3 pets, each modification
  confined to `distressCallGroup` + the sound-pak stems (`alertSound`/`criticalHitSound`/
  `deathSound1`/`rallySound`/`rampageSound*`/`stunSound`/`voxSound` + their `Chance`/`Delay`
  siblings) - `characterRacialProfile` unchanged on all 21 (it was already correct pre-existing,
  confirmed field-by-field in the diff: the field never appears in any of the 21 changed-field
  lists). 0 collateral on the 57 round-1 pets, 0 collateral anywhere else in the 51,057-record db.
- **B-SUMMON-1** (`validate_summon_pets.py`, run with base-game + upstream args for accurate
  rig-proven resolution): 279 soul summon chains, 253 pets checked, **STRICT failures: 0**
  (134 pre-existing upstream-proven WARNs, identical count to round 1, unrelated to this pass).
- **Contracts** (souls/summons/resources, `--only souls,summons,resources`): run identically
  against both the round-1 baseline and this round's build in this worktree (the worktree has no
  `Resources/` dir, so absolute counts run inflated/uncomparable to a live deploy - a pre-existing
  environmental gap, not introduced here) - **IDENTICAL totals both runs**: `TOTAL: 19168
  violations (96 P0, 7244 P1, 11828 P2)` => **0 new P0/P1/P2** from this pass.
- **Negative tests**: 7/7 (5 round-1 + 2 new) planted defects FAIL the gate; clean arz PASSES.
- Map/Quests/Text: untouched (DB-only change, same as round 1).

### Files changed (round 2, additive to the round-1 list above)
- `tools/apply_svc_patches.py` - `_create_boneash_pet_skill`, `_create_boss_summon_from_source`
  (Narok/Vort), `_create_pharaoh_guard_pet_skill`, `_create_bwpriest_pet_skill`,
  `_create_lillued_pet_skill`, `_create_rakanizeus_pet_skill` each gain one
  `_align_pet_identity(db, path, source)` call at their existing anim/skill-copy site; new
  `_align_helike_identity(db)` (standalone, upstream-native Helike) + one call site next to
  `_fix_bloodhound_dyingfxpak(db)`.
- `tools/patches/enslaver_pet_fx.py` - new `_SECOND_BUILDER_ROSTER` roster constant; `verify()`
  gains the second-lineage race/voice gate leg (reuses `_race_and_voice_problems` unchanged).
- `scratchpad/negtest_gate.py` (gitignored) - 2 new negative tests
  (`plant_beastman_race_second_lineage`, `plant_maenad_vox_second_lineage`).
- `docs/reports/b81_pet_identity.md` - this section. `docs/BACKLOG.md` - B81r2 entry.

### BACKLOG DEBT registered (per "NO NEW SURFACE WITHOUT A GATE + DEBT REGISTER")
- **Phagia orphan** - `phagia_{1,2,3,34}` pet records + `summon_phagia.dbr` are dead upstream SV
  content with zero live grant path (the only souls that ever granted it were intentionally
  repointed to Meritamen in build36). No player-visible symptom today (unreachable), so not
  fixed; if Will ever wants a standalone Phagia summon restored, it needs its OWN soul/grant
  wiring decision, not an identity-pass fix. Zero urgency.

### What Will will additionally see (after a full Steam restart; DISMISS + RE-SUMMON any active pet)
Boneash, Narok the Rockskin, Vort the Red, Pharaoh's Honor Guard, the Blood Witch High Priest,
Lil'Lued the Elder Djinn, and Rakanizeus - the 7 summon-the-boss souls built by the OLDER
standalone builders (distinct from the 19 `_build_boss_summon` families round 1 already fixed) -
now alert/crit/death/rally/vox in their OWN voice (a fire skeleton, two dragonians, a stone
guardian, a blade-dancer demon, a storm djinn, a satyr warlord) instead of every one of them
screaming in Lyia's Maenad-woman voice. Helike (an existing, correctly-sourced summon) is
unchanged in-game but now permanently gated. Aletha Darkclaw is unchanged (she is genuinely a
Maenad). No visual/stat change on any of the 8 families - purely the same race/audio identity
layer as round 1, now covering both Lyia-cloning lineages.
