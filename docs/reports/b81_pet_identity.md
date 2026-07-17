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
