# build36 LANE B report - SVAERA mastery-skill graft (18 skills) + Runemaster buffs

**Status: COMPLETE. All gates PASS.** Round 1 (predecessor made zero code
progress; implemented from scratch). Branch `feat/build36-lane-b`.

Artifacts (rebuilt this round, `work/SoulvizierClassic/`):
- `Database/SoulvizierClassic.arz` = 54,979,872 B, md5 `8731590586a404c2d3708188f05d41d6`
- `Resources/Text.arc` = 372,063 B, md5 `910dcef314497dc852419a3eb54ec137`
- `Database/uber_soul_tags.txt` = 205 tags (8 from this lane)

## 1. What shipped (additive-only)

**14 player-tree mastery skills**, each a new tree slot + a new mastery-panel UI
button, imported from the REAL SVAERA arz (`.../475150/2076433374/...`, soa's
verbal permission). Plus their recursive .dbr closure (7 records) = **21 SVAERA
records** total; **18 of them are gameplay "skills"** (14 player skills + a nymph
pet-skill + the Doppelganger pet + its aura + a pet conversion-immunity passive);
the other 3 are pure asset closure (2 Frost-Nova FX records + 1 Doppelganger anim
table).

| Mastery | Tree (skillNameN) | UI folder / cell | Skill (SVAERA record) | Anim |
|---|---|---|---|---|
| Warfare | drxwarfareskilltree 27/28/29 | ingameui M1 26/27/28 | Slam / Fissure / Lasting Legacy | Hew / - / - |
| Defense | drxdefensiveskilltree 26/27 | ingameui M2 25/26 | Perfect Block / Unyielding Phalanx | ShieldSkill02 / CallOfTheHunt |
| Earth | drxearthskilltree 26/27/28/29 | ingameui M3 25/26/27/28 | Fire Nova / Rupture / Burning Bolts / Flare | ThunderClap / - / - / - |
| Storm | drxstormskilltree 26/27 | ingameui M4 26/27 | Lightning Dash / Frost Nova | - / ThunderClap |
| Nature | drxnatureskilltree 26/27 | ingameui M8 25/26 | Earthbind / Sylvan Protection (nymph Rootwave petmod) | Colossus / - |
| Dream | drxdreamskilltree 26 | xpack M9 25 | Dream Image (Summon Doppelganger) | - |

Support closure records (no tree/UI slot): `drx_nymph_petskill_rootwave`,
`dreamcopypet` (+ `_petskill_aura`, `anm_dreamcopy`), `hero_conversionimmunity_pets`,
`storm_frostnova_fx`, `storm_frostnova_fxpak`.

**Runemaster buffs** (vanilla-path scalar edits, no tree-pointer swap):
`menhirwall` cd 22->18 + wall TTL 10->14; `mines` cd 9->8 + active duration 10->14.

New env kill-switch `SVC_GRAFT_SVAERA` (default ON).

## 2. Laws honored (verified against the shipped .arz bytes)

- **Additive only.** Every skill lands at the next FREE tree slot + a FREE UI grid
  cell (collision-checked against the live panels; build fails loud on any occupied
  slot). Existing characters keep every invested point.
- **No tree-pointer swap.** RuneMaster/Neidan trees keep their vanilla pointers
  (never repointed to SVAERA's `_drx_*`, which would strand invested points).
- **Occult (5) / Hunting (6) UNTOUCHED.** `validate_mastery_golden` PASS with no
  re-baseline; final-arz probe confirms their UI slot counts unchanged (M5=26, M6=24).
- **Anim safety.** Every non-empty `skillSpecialAnimationName` a grafted skill names
  already resolves in BOTH PC anim tables (Hew 7 rows, ShieldSkill02 3 incl sHanded,
  CallOfTheHunt 7, Colossus 8, ThunderClap 8). Graft #0 (build31/35) already restored
  the melee rows. The player-anim gate runs on the grafted trees and PASSES.
- **Closure / D5.** Every .dbr a grafted skill needs that does not resolve in the
  runtime model (mod UNION base) is imported from SVAERA, recursively, dtype-
  preserving. **Zero `_DRX` mesh/texture refs across the entire closure** (probed) -
  no invisible-pet risk. The Doppelganger is a `doppelganger.tpl` clone of the player
  mesh (shipped); its only `_DRX` refs are 6 fallback `.anm` run-fix clips (engine
  falls back to base cleanly). Summon Phalanx's 12 phalanx pets resolve in base xpack3.
- **drxrupture** carried the known SVAERA placeholder `sandbox\chris\unarmedprojectile_
  fx01.dbr` on two FX fields; cleared to '' (the freshly-authored record ships with
  no dangling ref).

## 3. ANIM-TOKEN AUDIT (per the brief)

build35 commit `4047b88` (+ build31 B6) already added the animation rows. Verified
every grafted skill's token resolves in the CURRENT tables (`anm_malepc01` +
`anm_femalepc`): Hew, ShieldSkill02, CallOfTheHunt, Colossus, ThunderClap all
present on the needed weapon rows (Slam needed the graft-#0 Hew melee rows -
present). No token had to be added by this lane. The player-anim gate confirms it
(46 anim-carrying tree skills checked, 0 violations; the 1 INFO is the pre-existing
Neidan `splash` modifier, not ours).

## 4. Rune Golem overlap check (read-only, per the brief)

The golem block lives in `apply_svc_patches.py` (lane A) and runs during my build
(88d2b03 has it). Overlap check: it only REFERENCES `menhirwall` as the Rune Golem's
prereq (`skillDependancy`) and never edits menhirwall's numbers; it appends the golem
at Runemaster UI slot23. My Runemaster buffs edit DIFFERENT records/fields
(`menhirwall` cd/TTL + `mines`), my graft does NOT touch the Runemaster tree/UI, and
my buff imports `menhirwall` BEFORE the golem references it (so the golem's dependency
resolves to my buffed override). **No double-apply, no slot collision.** The full
build ran the golem block AND my graft together and passed every in-build gate; the
final arz contains both (`_drx_runegolem` present, no conflict).

## 5. TAGS (data path, no build_text_arc.py edit)

The text pipeline is data-driven: `build_text_arc.py` reads
`work/.../uber_soul_tags.txt` (my `graft_tags` flow into it via `main()`). **8**
genuinely-new SV-authored tags were authored that way. The 8 base-Atlantis `x3tag*`
display tags resolve at runtime from base Text (no action). **4** tags
(`tagRuptureNAME/DESC`, `tagFlareNAME/DESC`) already ship in the mod's 0.98i text
(`xuniqueequipment.txt`) and are deliberately NOT re-emitted - re-adding
`tagRuptureDESC` tripped the duplicate-tag gate on the first Text build (0.98i "Staff
Only" vs SVAERA "Staff or Bow"); dropping the 4 is the fix. Full detail +
machine-readable manifest: `build36_laneB_tags_handoff.{md,json}`.

**Expected tags-gate delta: none (clean PASS).** Measured: `validate_tags` = "all 148
referenced mod tags present" + "all 205 authoritative tags present" -> PASS.

## 6. GATE RESULTS (one full DB rebuild + all gates)

| Gate | Result |
|---|---|
| Full DB rebuild (build_svc_database.py) | **PASS** (arz written, 54,979,872 B) |
| in-build: player-skill anim castability | **PASS** (46 checked, 0 viol) |
| in-build: container loot-slot shape | **PASS** |
| in-build: summon-pet chain (B-SUMMON-1) | **PASS** |
| in-build: render-chain (A9) | **PASS** |
| in-build: Occult/Hunting golden freeze (A7) | **PASS** |
| in-build: F2 summons contract | **PASS** |
| Text.arc build + duplicate-tag gate + A7 Text half | **PASS** (after the 4-tag fix) |
| validate_tags | **PASS** (all referenced + authoritative present) |
| validate_soul_augments | **PASS** |
| validate_mastery_golden | **PASS** |
| validate_player_skill_anims | **PASS** |
| validate_summon_pets | **PASS** |
| contracts suite (souls + summons) | **PASS** (0 P0, 0 P1, 112 P2 = pre-existing upstream monster debt, none mine) |

The 112 contract P2s are the standing upstream data debt (ported monsters with
unresolvable mesh/skill refs, e.g. `um_legion_28*`, `guardianstatue`, `01_charsi`);
none is a grafted record. They are the same P2 set every build carries.

## 7. Verification method

- Isolated self-test (`tools/debug/g1_graft_selftest.py`): ran the graft on the
  built work arz + real base + SVAERA, asserted every tree/UI/panel/tag/buff
  invariant + the player-anim gate + a write/reload round-trip. ALL PASS.
- Full build: the graft ran inside the real pipeline (after wave2, before the anim
  gate, before `del base_db`); the final arz was re-probed to confirm all 21 records,
  tree wiring, Runemaster buffs, cleared drxrupture ref, and untouched Occult/Hunting.

## 8. Files

- **Owned/edited:** `tools/build_svc_database.py` (the graft + Runemaster buffs +
  main() wiring + tag threading).
- **New (mine):** `tools/debug/g1_*.py` (recon probes + the self-test),
  `docs/reports/build36_laneB_report.md`, `docs/reports/build36_laneB_tags_handoff.{md,json}`.
- **Not touched:** `tools/apply_svc_patches.py`, `tools/build_text_arc.py`,
  `docs/BACKLOG.md` (lane A owns these).
- Upstream SV arzs + SV098i `Text_EN.arc` were re-extracted from `third_party/` into
  `upstream/` (gitignored) to enable the build; they had been cleared from disk.

## 9. Open items / notes for the vet

- **Determinism (2x rebuild -> md5 match) not run** (the brief caps the round at one
  full build). Recommend the vet does a deterministic 2x rebuild and confirms the arz
  md5 is stable (PYTHONHASHSEED=0 is pinned in-build).
- **In-game cast test outstanding** (the runtime B-SOUL-PROC law). The anim gate proves
  every grafted skill's cast anim resolves, but a real in-game cast/spawn test per the
  standing rule should confirm Slam/Active Block/Summon Phalanx/Fire Nova/Frost Nova/
  Earthbind cast and the Doppelganger/Phalanx pets spawn + render.
- **Rupture tooltip** reads "Staff Only" (0.98i text) though the SVAERA skill is
  Staff-or-Bow - cosmetic, not overridable via the data path (would need a
  build_text_arc.py change, out of lane scope).
- The `work/` arz + Text.arc were rebuilt in place (shared build output). Backup of the
  prior work arz saved to the session scratchpad (`work_arz_prebuild36B.arz`).
