# b55 - ENSLAVER PET FX: black-rig the soul-summoned Enslaver (BL-ENSLAVER-PET-FX)

Branch `feat/enslaver-pet-fx` (worktree, from main HEAD `f816ca6`). DB/registry lane.
No heavy build - dry-run replay vs the build40 GOLDEN arz `b33c5a44`
(`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, 55,351,206 B).

## Will's order (2026-07-14, verbatim)
> "toxeus the murderer enslaver of souls has green glow not black like we said ...
> this is when i summon him from his soul."

Clarification (same day):
> "his poison effect is still green, it is not the custom black one we wanted to
> make for him."

Target = the SOUL-SUMMONED Enslaver (the friendly pet the Enslaver soul calls
forth) + the marauders that pet raises. The ENCOUNTER monster and the Devourer of
Blood are out of scope (see below).

## Root-cause analysis (from the GOLDEN build40 arz `b33c5a44`)

### b38's encounter fix LANDED - verified in the golden arz
The encounter monster `um_toxeus_enslaver_99` in the golden arz carries the b38
all-black rig, confirmed field-by-field:
- `mesh = Creatures\Monster\Skeleton\RevenantPoison.msh`
- `baseTexture = Creatures\Monster\Skeleton\NewSkeleton_Charcoal.tex` (black)
- `charFxPakRunningNames = ...\buff_self\svc_enslaver_darksmoke_charfxpak.dbr`
  (the black-smoke shroud, recoloured to `343_dark_smoke` -> `SVEffects/ambient/dark_smoke.pfx`)
- NO `initialSkillName` (b38 deleted the green `toxeus_envenomweapon` weapon glow)
- NO `buffSelfSkillName`, NO `deathEffect`
- kit (`toxeus_attackskill`, `netherstrike`, `toxeus_bladestorm`, chain
  `phantomstrike`->`toxeus_distortreality`, `lifedrain`, `flashpowder`,
  `lethalstrike`) RCA'd for FX: **none is green** (nether/shadow `.pfx`, dream
  `.pfx`, chaos beam, thrown knives). So the encounter is genuinely black -
  matching Will's "not the pet, the summon" localisation.

**The b38 fix operated ONLY on the fought monster record.** The soul-summon pet is
a separate record it never touched. That is the coverage gap.

### The pet chain, and where the green comes from
Full soul chain (all in the golden arz):

```
enslaver soul item (records\item\equipmentring\soul\...\enslaver_soul_{n,e,l})
  -> itemSkillName = SUMMON_ENSLAVER_SKILL (records\skills\soulskills\summon_toxeus_enslaver.dbr)
       -> spawnObjects = [ toxeus_enslaver_1 , _2 , _3 ]          (the 3 friendly PET records)
            -> pet specialAttackSkillName = svc_enslaver_petmarauders   (friendly pet-of-pet summon)
                 -> spawnObjects = [ enslaver_marauder_1 , _2 , _3 ]     (the raised marauder PETs)
```

The 6 pet records (`toxeus_enslaver_1..3`, `enslaver_marauder_1..3`) are built by
`_build_boss_summon` (apply_svc_patches.py), which - per the crash-safe pet
contract - **clones the Lyia Leafsong pet** (a Maenad poison/nature caster) for a
valid `Pet.tpl` baseline, then copies mesh/skin/anim + a NARROW set of skill-slot
refs from the source monster (`_SKILL_PREFIXES = skillName / attackSkill /
specialAttack / buffSelf / initialSkill`).

The Lyia base (`lyialeafsong_1.dbr`) carries these GREEN fields, and because the
SOURCE monster (`um_toxeus_enslaver_99` / `um_enslaver_marauder_99`) does **not**
define them, `_update_existing_fields` never overwrites them - so they survive on
the pet as residue:

| pet field | green value | what it renders |
|---|---|---|
| `buffSelfSkillName` | `stealth\envenomweapon.dbr` | **Skill_BuffSelfToggled: `skillWeaponTintGreen = 1.0` (Red/Blue 0.25) + `charFxPakSelfNames -> 343_weapon_poisoncharfxpak -> 343_Weapon_PoisonFX` + `weaponEnchantment=poisonweaponenchantment`.** The pet auto-casts it (always on) = a GREEN weapon-poison glow + green poison particles + poison DoT. **This is Will's "poison effect is still green"** - the same green profile as the `toxeus_envenomweapon` b38 deleted off the boss. |
| `buffSelf2SkillName` | `nature\heartofoak.dbr` | green FeralSpirit nature aura |
| `healSkillName` | `nature\regrowth_lyia.dbr` | green Regrowth heal FX (on self-heal) |
| `deathEffect` | `effects\nature\343_natureswrath_low_fx.dbr` | green nature death burst (the RECORD is MISSING in our arz, so it renders nothing today, but it is wrong residue + a dangling ref) |
| *(marauder pets only)* `specialAttackSkillName` + `skillName8` | `nature\sylvannymph_petskill_nature'swrath.dbr` | green nature'swrath AoE projectile (`343_NaturesWrath` FXPak) |
| *(marauder pets only)* `baseTexture` | `SVTextures/creatures/maenad/maenad_lyia.tex` | the WRONG Maenad skin painted over the ShadowStalker demon mesh |

And crucially the pet was **MISSING `charFxPakRunningNames` entirely** -
`charFxPakRunningNames` is not in `_SKILL_PREFIXES`, so the builder never copies the
boss's black-smoke shroud onto the pet. Net visual: a black skeleton emitting a
GREEN poison-weapon glow + green nature FX, with no black smoke.

The marauder pet also inherited Lyia's ranged `attackSkillName =
maenadsummon_attack_default` (a plain `arrowdefault01` projectile - **not green**;
`Default_Arrow` trail, `FireBlast` impact). That is a behaviour quirk (the melee
shadow marauder shoots arrows) but NOT a green-FX defect, so it is out of this
fix's scope and left as-is (noted for a future pet-behaviour pass).

## The fix (`tools/patches/enslaver_pet_fx.py`, new registry module, pos 12/14)

PET FX fields only. No clones, no new records, no textures authored. Reuses b38's
own `svc_enslaver_darksmoke_charfxpak` and the `drxshadowcloakrunning_fx_pak` the
marauder MONSTER already wears. Per the PET SAFETY LAWS: only animation/skill/FX
fields are touched; no equipment/loot field is copied Monster.tpl->Pet.tpl; no
explicit dtype on `set_field`; the shroud is copied VERBATIM from the source
monster's own `TypedField` (dtype + values) so the pet's field is byte-identical to
the monster it mirrors.

For each of the 6 Enslaver-family pets:
1. **STRIP the green Lyia residue** (marker-matched - only the known-green value is
   removed, never a legit field): `buffSelfSkillName`(envenom), `buffSelf2SkillName`
   (heartofoak), `healSkillName`(regrowth), `deathEffect`(natureswrath); and on the
   marauder pets `specialAttackSkillName`(sylvannymph) + the dormant kit slot
   `skillName8`(+`skillLevel8`) + `baseTexture`(maenad, -> ShadowStalker mesh
   default = exactly what the marauder MONSTER renders). Field-absence parity (the
   deleted key is simply not re-emitted by `write_arz`, matching the source).
2. **INHERIT the source monster's shroud**: copy the source's
   `charFxPakRunningNames` TypedField onto the pet -> enslaver pets <-
   `svc_enslaver_darksmoke` (b38 black smoke), marauder pets <- `drxshadowcloak`
   (the shadow cloak the monster already wears). `charFxPakRunningNames`-on-a-pet is
   the proven-safe route (the marauder monster + Vashkarr use it).

The enslaver soul-pet's `specialAttackSkillName` is NOT stripped: it is the friendly
pet-of-pet marauder summon (`svc_enslaver_petmarauders`, wired in `_create_enslaver`
step 5), which matches no green marker.

`verify(db)` (run_registry_verifies, post-finalization) asserts, over every
Enslaver-family pet that exists: zero green residue (FX fields + kit slots) AND the
correct source shroud in `charFxPakRunningNames`. Fail-loud (negative-tested).

## Sibling sweep (monster-vs-pet FX divergence across the whole roster)

Enumerated all 222 records under `records\skills\soulskills\pets\`. **82 carry the
same systemic Lyia green residue** (envenom/heartofoak/regrowth/natureswrath) - it
is an artifact of EVERY `_build_boss_summon` pet whose source lacks the field, not
Enslaver-specific.

The brief's precise same-class criterion is "a monster we RETINTED with a dedicated
custom FX shroud whose PET still wears the old rig". Checking each boss-summon
source's `charFxPakRunningNames`: **exactly two source monsters carry a custom
shroud, and both are the Enslaver family** - `um_toxeus_enslaver_99`
(svc_enslaver_darksmoke) and `um_enslaver_marauder_99` (drxshadowcloak). Every other
boss-summon source (xeiwang, broodmother, voranthys, narok, vort, longnu,
eaterofdays, boneash, ...) has **no custom shroud**, so its green pet residue does
not contradict a deliberate non-green identity.

- **FIXED (this round): the 2 same-class families = 6 pets** (toxeus_enslaver_1..3 +
  enslaver_marauder_1..3).
- **EXCLUDED: the Devourer of Blood `bloodtoxeus_1..3`** (crimson RevenantPoison).
  It is in the 82 but its green poison is INTENTIONAL and STAYS (Will 2026-07-14,
  and the brief). The module never touches it (proven byte-identical in the replay).
- **FLAGGED for Will (not fixed here): the broader ~76 pets** with the systemic Lyia
  green (+ the same maenad SOUND paks / maenadmerc AI controllers / dead maenad loot
  that are audio/behaviour, not visual green). Mass-repainting every summon pet is a
  design call, not a bug fix, and the Devourer proves some greens are wanted - so it
  should not be swept in this crash-history pet round without Will's decision.

## ITEM vs PET record (so Will's retest is set up right)

The summon FX rides entirely on the **PET records** (`toxeus_enslaver_1..3`,
`enslaver_marauder_1..3`). When the soul's granted skill fires, the engine resolves
`spawnObjects` against the CURRENT DB and instantiates the pet record live. TQ bakes
ITEM properties at pickup, but the soul ITEM only bakes `itemSkillName /
itemSkillLevel / augments` - none of which change here; the skill->pet resolution is
live. **Therefore the fix reaches Will's EXISTING Enslaver soul item.** He does NOT
need a freshly-dropped soul - only a full Steam/TQ restart so the game loads the new
arz (per the standing "restart before every test" rule). Summon the Enslaver from
his existing soul: the pet should be a black skeleton with black smoke and no green
poison, and the marauders it raises should be dark shadow demons (not green,
maenad-skinned).

## Verification (no heavy build; dry-run replay vs golden `b33c5a44`)

`scratchpad/replay_enslaver_pet_fx.py` (load golden -> run the module's `apply()` ->
diff + `verify()`). Faithful because the pet FX fields touched are NOT altered by
the build's finalization phase (which only touches soul equipmentring itemSkillName
+ cyclops de-filler + tag renames), so the golden arz's pet FX == what the module
sees at run_registry step 2.

```
apply modified EXACTLY the 6 Enslaver-family pets (scope proof: db._modified == the 6)
each pet: 0 green-FX residue after fix; charFxPakRunningNames == its source shroud
  toxeus_enslaver_1..3     - REMOVE buffSelf/buffSelf2/heal/death ; + svc_enslaver_darksmoke
  enslaver_marauder_1..3   - REMOVE buffSelf/buffSelf2/heal/death/specialAttack(sylvannymph)
                             /skillName8/skillLevel8/baseTexture(maenad) ; + drxshadowcloak
module verify() PASSED on the fixed db
Devourer bloodtoxeus_1 NOT modified + fields BYTE-IDENTICAL (green intended, excluded)
```

Negative tests (each MUST fail the module's verify):
```
[replant envenomweapon on toxeus_enslaver_1]   verify FAILED LOUD  OK
[clear the marauder pet's black shroud]        verify FAILED LOUD  OK
[wrong shroud value on toxeus_enslaver_2]       verify FAILED LOUD  OK
[replant green kit slot skillName8=sylvannymph] verify FAILED LOUD  OK
```

Contracts + gates (over a written fixed arz = golden + module, 6 records modified):
- **summons contract** (`tools/contracts/contracts_summons.py`) golden vs fixed:
  exit 0 both; violation output BYTE-IDENTICAL -> **0 new violations**.
- **PET-STAT-MIRROR / PET-GEAR-PARITY / PET-SKILL-KIT (222 pets swept) /
  soul-summon-identity** all PASS on the fixed arz (FX edits touch no stat/gear/
  spawn-skill).
- `py_compile` clean (no SyntaxWarning); `tools/patches/_check_registry.py` OK
  (**14 modules**, order `e64bc6e6...`).

## Files changed
- `tools/patches/enslaver_pet_fx.py` - NEW registry module (apply + fail-loud verify).
- `tools/patches/__init__.py` - REGISTRY += `enslaver_pet_fx` (pos 12, before `visuals`).
- `docs/BACKLOG.md` - B55 entry.
- `docs/reports/b55_enslaver_pet_fx.md` - this report.
- Scratchpad harnesses (analysis only, not shipped): `probe_enslaver_fx.py`,
  `probe_green_sources.py`, `sibling_sweep.py`, `probe_refs.py`,
  `probe_marauder_kit.py`, `replay_enslaver_pet_fx.py`, `make_fixed_arz.py`,
  `run_pet_gates.py`.

## What Will will see (after a Steam restart; existing soul is fine)
- Summon the Enslaver from his soul: a **black** skeleton lord wreathed in black
  smoke, **no green poison glow**.
- The marauders he raises: **dark shadow demons** (shadow-cloak shroud), no green,
  no maenad skin.
- The Devourer of Blood is unchanged (still its intentional crimson/green).
