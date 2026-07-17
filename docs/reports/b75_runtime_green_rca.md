# b75 - RUNTIME-GREEN RCA + fix (round 1): the Enslaver's green is the SHROUD ASSET, not a DB field; class-wide Lyia-green strip; transitive skill-list gate

Branch `fix/runtime-green` (worktree, from main `33d25d6` = post-build45). DB lane
(`apply_svc_patches.py` + registry module `enslaver_pet_fx.py`). Ground truth: build45
LIVE-ON-DEV arz `917d9047` (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
read-only). Scratch build md5 `baa76edb` (idempotent - two independent builds byte-identical).

## Will's report (2026-07-16, verbatim - 3rd repeat of the green class = P1)
> "toxeus the devouerer still has a green glow around him. Can we steal the black smoke
> around his Enslaved Shadow Marauders and add that black smoke around him as well? I think
> his poison ability or some ability or something about him as a character is still rendering
> him green. It looks like his marauders also have a green aura around them, but around toxeus
> it looks more like green smoke than an aura."

Disambiguation: "his Enslaved Shadow Marauders" identifies the subject as the ENSLAVER-of-Souls
family (the Devourer has no marauders); Will conflated the two Toxeus bosses' names. The
Devourer + its lineage were ALSO swept (below) since Will named him.

## The two prior rounds (why we were "oscillating")
- **b55 (build41):** stripped every green FX FIELD from 9 pets (toxeus_enslaver_1-3,
  enslaver_marauder_1-3, hadesmarshal_1-3) and gave each the source monster's dark shroud.
  Record-level verify. Data-only, never confirmed in-game.
- **b71 (build44):** RCA'd the CHAIN (soul->skill->icon->pets->portrait), fixed the wrong
  summon icon + Lyia pet-bar portrait, added a chain gate. Concluded the pets are field-for-field
  identical to the confirmed-black encounter monster and carry ZERO green markers; guessed the
  residual green was save-state or an asset-level pfx tint, and (correctly) made no speculative
  FX change.

## b75 RCA - the last blind spot: fields -> chain -> RUNTIME asset
Three independent DB scans on build45 (`917d9047`) all came back GREEN-FREE for the Enslaver
boss + soul pets + marauders:
1. **FX fields** (b55): mesh `RevenantPoison.msh`, `baseTexture=NewSkeleton_Charcoal.tex`
   (resolves), shroud present; zero envenom/heartofoak/regrowth/natureswrath residue.
2. **Chain** (b71): soul->skill->spawnObjects->pets all on-identity.
3. **Transitive skill-list closure (b75, NEW):** every skill reachable from
   `toxeus_enslaver_1-3` + `enslaver_marauder_1-3` (attackSkill / all `skillName<N>` /
   `specialAttack*` / buff / heal / init, transitively decoded to buff/pak/tint/FX) - ZERO
   green-capable skills. The kit (netherstrike, toxeus_bladestorm, lifedrain=chaos,
   flashpowder, lethalstrike, character_speedall, passives) is nether/shadow/dream/chaos/
   physical - none green. Refutes Will's own "a skill is rendering him green" hypothesis for
   the Enslaver: the green is NOT any skill the pet casts.

So the green lives ONE LAYER BELOW the DB, in the **shroud ASSET**:

The boss `um_toxeus_enslaver_99` (and, via inheritance, the soul pets) wore
`charFxPakRunningNames = svc_enslaver_darksmoke_charfxpak` ->
`records\effects\custom\343_dark_smoke.dbr` -> `SVEffects/ambient/dark_smoke.pfx`. Decoding the
EffectEntity records ground-truth:

| shroud | EffectEntity | emitterType | boneList | in-game |
|---|---|---|---|---|
| svc_enslaver_darksmoke (Enslaver) | 343_dark_smoke | **absent (default)** | Bone_R_Weapon, Bone_L_Weapon | reads GREEN (Will x3) |
| drxshadowcloak (marauders) | drxshadowcloakrunning_fx | **Standard** | Bone_R_Weapon, Bone_L_Weapon | **BLACK (Will-confirmed)** |

`343_dark_smoke` attaches to the WEAPON bones with **no `emitterType=Standard`**, so it never
envelops the body as a clean whole-body shroud the way `drxshadowcloak` (whole-actor,
`localOrientFix=1`) does; and the `dark_smoke.pfx` particle tint reads GREEN in-game (both pfx
use the same grey `343Smoke_01/02` textures, so the difference is the baked particle color - an
ASSET value, invisible to every DB scan). The mesh itself is innocent: `RevenantPoison.msh`
references only `NewSkeleton_White.tex` + a bump map (no baked green glow), and our charcoal
`baseTexture` override lands. This is exactly why b55 (fields) + b71 (chain) + the b75 transitive
skill scan all came back clean: **the green is an asset the DB merely points at, the last
blind spot after fields and chain.**

**Boss "green smoke" vs marauder "green aura" (both Will observations):**
- Boss = the `343_dark_smoke` shroud rendering green (weapon-bone, non-whole-body).
- Marauders = their own shroud is the PROVEN-black `drxshadowcloak`; their mesh (ShadowStalker)
  and full skill closure are green-free. Their apparent green "aura" is perceptual bleed from the
  boss's green smoke cloud they fight inside (no marauder DB/asset green source exists - the
  transitive gate confirms). The `character_speedall` alacrity aura the boss projects onto allies
  is a dead end: `343_AlacrityAuraFX.dbr` is MISSING from the arz (renders nothing).

## The fix

### 1. Enslaver shroud: dark_smoke -> drxshadowcloak (Will's verbatim ruling)
`_create_enslaver` now sets the boss `um_toxeus_enslaver_99` `charFxPakRunningNames` to the
marauders' **proven-black** `drxshadowcloakrunning_fx_pak` (emitterType=Standard, whole-body).
The soul pets `toxeus_enslaver_1-3` inherit it automatically (the b55 `enslaver_pet_fx` module
copies the SOURCE monster's shroud verbatim). The dead `svc_enslaver_darksmoke_charfxpak` clone
is no longer created (removed from the arz). This is literally "steal the black smoke around his
marauders and add that black smoke around him." `343_dark_smoke` is left untouched for the
`diadochi` lane which also uses it (**FLAGGED**: if Will confirms 343_dark_smoke reads green,
the Diadochi generals' `svc_ashsmoke_charfxpak` shroud has the same problem - out of this lane).

### 2. Class-wide Lyia-green strip, UPSTREAM in `_build_boss_summon` (anti-oscillation)
Every `_build_boss_summon` pet is a Lyia Leafsong clone; `_update_existing_fields` only
overwrites a field the SOURCE defines, so on a non-nature source the Lyia green FX fields survive
as residue (an always-on GREEN weapon-poison glow `buffSelfSkillName=envenomweapon`
[skillWeaponTintGreen=1.0 + 343_Weapon_PoisonFX], `buffSelf2=heartofoak`, `heal=regrowth_lyia`,
`deathEffect=natureswrath`, the Lyia default-ARROW `attackSkillName`, and the maenad skin). b55
fixed only 3 families; **b75 strips them for the WHOLE CLASS at the builder**, so this can't
oscillate again. New `_strip_lyia_clone_green(db, path, source)` is SOURCE-FAITHFUL (BL-103,
mirrors `_strip_foreign_anim_overrides`): a field is stripped ONLY when the source does not
itself reference an equivalent skill, so a genuinely nature/poison source keeps its intended
green. Safe (FX/skill/skin STRING fields only, never equipment/loot).

**Per-family removal (54 pets across 15 families, from the build log):**

| family | pets | stripped |
|---|---|---|
| xeiwang, eaterofdays, broodmother | 3 each | envenom, heartofoak, regrowth, natureswrath, arrow |
| broodmother_wyrmling, voranthys | 3 each | envenom, heartofoak, regrowth, natureswrath, maenad-skin |
| longnu | 3 | envenom, heartofoak, regrowth, natureswrath |
| mnemophage_phantasm | 3 | envenom, heartofoak, regrowth, natureswrath, arrow |
| charon_oarsman, kravmoloch_warden, tantalus_shade | 3 each | envenom, heartofoak, regrowth, natureswrath, arrow, maenad-skin |
| pygmalion, neferkha | 3 each | heartofoak, regrowth, natureswrath, arrow |
| meritamen | 3 | heartofoak, regrowth, natureswrath, arrow, maenad-skin |
| mountainblade, sarpedon | 3 each | heartofoak, regrowth, natureswrath |
| enslaver_marauder, hadesmarshal | 3 each | arrow only (b55 already stripped their green FX) |

**PROTECTED (Will 2026-07-14 "Devourer green stays" + parallel EoAT/undivided lane owns its
poison identity):** the Devourer of Blood `bloodtoxeus_1-3` is skipped entirely (`protect_green=True`
on its `_build_boss_summon` call) - byte-identical, keeps its green Lyia envenom rig. Named
skill: the Devourer's intended poison is source-defined `bloodtoxeus_envenomweapon`
(skillWeaponTintRed=1.0 = crimson) on `um_bloodtoxeus_99`; its PET's actual green is the Lyia
`stealth\envenomweapon` residue (skillWeaponTintGreen=1.0). The EoAT lane, reworking "the
Devourer's BLACK poison", should decide whether to repoint the pet from the Lyia green envenom to
a genuinely dark/black poison - flagged, not touched here.

### 3. Chain gate extended - transitive skill-list green sweep (anti-oscillation leg 3)
`enslaver_pet_fx.verify()` now also walks each gated pet's full skill/FX closure and fails loud on
any `skillWeaponTintGreen>0` or green nature/poison FX/skill/pak reference. Negative-tested:
planting `skillName13=envenomweapon` on a gated pet (a green skill the pet would CAST) makes the
gate fail - the leg the b55 field gate + b71 chain gate never reached.

## Verification (all green; scratch md5 `baa76edb`, idempotent x2)
- Full scratch DB build EXIT 0; all registry verifies + in-build gates green, incl.
  `enslaver_pet_fx.verify` (field + b71 chain + b75 transitive legs). A7 Occult/Hunting golden
  freeze PASS (84 waived, 0 other).
- **Record-diff vs build45 `917d9047`: exactly this fix** - 1 REMOVED (dead
  `svc_enslaver_darksmoke_charfxpak` clone) + 55 MODIFIED = `um_toxeus_enslaver_99` (shroud, 1
  field) + `toxeus_enslaver_1-3` (shroud, 1 field each) + `enslaver_marauder_1-3` +
  `hadesmarshal_1-3` (arrow strip, 1 field each) + 15 families' pets (green residue strip, 3-6
  fields each). **0 collateral, 0 soul-item/skill/map/quest/text records, Devourer absent (protected).**
- Negative tests (`scratchpad/negtest_gate.py`): plant envenom buffSelf (field gate) FAILS; plant
  envenom in a `skillName<N>` slot (TRANSITIVE gate) FAILS; clear the shroud FAILS; clean arz PASSES.
- B-SUMMON-1 (`validate_summon_pets`): PASS. Render-chain (`validate_render_chain`): PASS (254
  pets / 3004 art refs; the skill strips left NO dangling anims/casts; drxshadowcloak resolves).
- Contracts (souls/summons/resources) vs build45: **IDENTICAL totals** (0 P0 / 576 P1 / 10717 P2
  on BOTH) => **0 new P0/P1/P2**. validate_tags PASS. A7 untouched. Map/Quests/Text untouched
  (DB-only change).

## Will test instructions (after a full Steam restart)
Per the standing "restart before every test" + b55/b71 "summon FX rides on the live PET record"
notes, no fresh soul drop is needed - a restart to load the new arz is enough. Then, to be
certain the RENDER (not a stale already-summoned pack) is fresh: **DISMISS the current Enslaver
pack and RE-SUMMON it from the soul.** Expected: Toxeus the Enslaver (and his raised marauders)
wreathed in the SAME black smoke the hostile Enslaved Shadow Marauders wear, **no green**. Also
worth a glance: the ~15 other boss-summon souls (Pygmalion, Xeiwang, Charon, Sarpedon, Longnu,
Meritamen, Broodmother, Kravmoloch, Mnemophage, Mountainblade, Neferkha, Tantalus, Voranthys,
Eaterofdays) no longer emit the accidental green poison glow. The Devourer of Blood is unchanged
(still its intended green - a separate lane owns making it black).

## Files changed
- `tools/apply_svc_patches.py` - Enslaver boss shroud dark_smoke -> drxshadowcloak (+ dead
  darksmoke clone removed); new `_strip_lyia_clone_green` + `_source_references_needle` +
  `_LYIA_GREEN_RESIDUE`; `_build_boss_summon` gains `protect_green` and calls the strip; the
  Devourer call passes `protect_green=True`.
- `tools/patches/enslaver_pet_fx.py` - transitive skill-list green sweep (`_transitive_green_problems`)
  wired into `verify()`; docstrings updated for the drxshadowcloak shroud.
- `docs/reports/b75_runtime_green_rca.md` - this report. `docs/BACKLOG.md` - B75 entry.
