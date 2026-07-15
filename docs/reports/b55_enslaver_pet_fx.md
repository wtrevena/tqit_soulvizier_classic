# b55 - ENSLAVER PET FX: black-rig the soul-summoned Enslaver (+ sibling sweep) (BL-ENSLAVER-PET-FX)

Branch `feat/enslaver-pet-fx` (worktree, from main HEAD `f816ca6`). DB/registry lane.
No heavy build - dry-run replay vs the build40 GOLDEN arz `b33c5a44`
(`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, 55,351,206 B).

> **b55r2 (2026-07-14)** corrects the r1 sibling sweep. r1 fixed 2 families / 6 pets
> and asserted "exactly two source monsters ... and no other" - that was FALSE: it
> missed the **Hades Marshal soul-summon** (a third same-class divergence). This round
> adds it (now **3 families / 9 pets**), corrects the claim from ground truth, and
> softens the overstated "charFxPakRunningNames proven-safe on a pet" wording.

## Will's order (2026-07-14, verbatim)
> "toxeus the murderer enslaver of souls has green glow not black like we said ...
> this is when i summon him from his soul."

Clarification (same day):
> "his poison effect is still green, it is not the custom black one we wanted to
> make for him."

Target = the SOUL-SUMMONED Enslaver (the friendly pet the Enslaver soul calls
forth) + the marauders that pet raises. The sibling sweep (required by the brief:
"fix any other divergence of the same class ... report count") adds the Hades
Marshal soul-pet. The ENCOUNTER monster and the Devourer of Blood are out of scope
(see below).

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
| `healSkillName` | `nature\regrowth_lyia.dbr` | green Regrowth heal FX (`regrowth01` + `regrowth_fxpak01`) |
| `deathEffect` | `effects\nature\343_natureswrath_low_fx.dbr` | green nature death burst (the RECORD is MISSING in our arz, so it renders nothing today, but it is wrong residue + a dangling ref) |
| *(marauder pets only)* `specialAttackSkillName` + `skillName8` | `nature\sylvannymph_petskill_nature'swrath.dbr` | green nature'swrath AoE projectile (`343_NaturesWrath` FXPak) |
| *(marauder pets only)* `baseTexture` | `SVTextures/creatures/maenad/maenad_lyia.tex` | the WRONG Maenad skin painted over the ShadowStalker demon mesh |

And crucially the pet was **MISSING `charFxPakRunningNames` entirely** -
`charFxPakRunningNames` is not in `_SKILL_PREFIXES`, so the builder never copies the
boss's black-smoke shroud onto the pet. Net visual: a black skeleton emitting a
GREEN poison-weapon glow + green nature FX, with no black smoke.

### The Hades Marshal pet chain (b55r2 - the missed sibling)
Same shape, different soul (built by the `four_generals` registry module):

```
hadesmarshal soul item (records\item\equipmentring\soul\svc_uber\hadesmarshal_soul_{n,e,l})
  -> itemSkillName = summon_hadesmarshal
       -> spawnObjects = [ hadesmarshal_1 , _2 , _3 ]   <- built from svc_um_hadesmarshal_80
```

`svc_um_hadesmarshal_80` (Menoetes, Marshal of the Dead) is one of the FIVE
shroud-carrying monsters: it wears a dedicated dark
`records\xpack\effects\boss effects\hades2_shadowcloud_charfxpak.dbr` shadow-cloud.
Its 3 soul pets carry the IDENTICAL green Lyia residue (`envenomweapon`,
`heartofoak`, `regrowth_lyia`, `deathEffect=343_natureswrath`, `baseTexture=maenad_lyia`
over the `MachaeHero01.msh` mesh) and are MISSING the shroud. Its combat kit
(`hero_hadesbolt`, `hero_slowspiritbolt_ring`, `gigantes_groundbreaker`, `lifedrain`,
`svc_marshal_summonarchers`, passives) was RCA'd field-by-field for FX: **none is
green** (spirit/hades projectiles, physical ground wave, chaos lifedrain). So the
existing `_GREEN_MARKERS` cover its every green field with **no new marker needed**;
its `skillName8 = gigantes_groundbreaker` is NOT green (unlike the marauder's
green `skillName8`), so nothing dark is stripped by mistake.

## The fix (`tools/patches/enslaver_pet_fx.py`, registry module, pos 13/14)

PET FX fields only, on **9 PET records**. No clones, no new records, no textures
authored. Reuses each source monster's OWN existing shroud: b38's
`svc_enslaver_darksmoke_charfxpak` (Enslaver), the `drxshadowcloakrunning_fx_pak`
the marauder MONSTER already wears, and the `hades2_shadowcloud_charfxpak` the
Hades Marshal MONSTER already wears. Per the PET SAFETY LAWS: only animation/skill/FX
fields are touched; no equipment/loot field is copied Monster.tpl->Pet.tpl; no
explicit dtype on `set_field`; the shroud is copied VERBATIM from the source
monster's own `TypedField` (dtype + values) so the pet's field is byte-identical to
the monster it mirrors.

For each of the 9 pets:
1. **STRIP the green Lyia residue** (marker-matched - only the known-green value is
   removed, never a legit field): `buffSelfSkillName`(envenom), `buffSelf2SkillName`
   (heartofoak), `healSkillName`(regrowth), `deathEffect`(natureswrath); and where
   present `specialAttackSkillName`(sylvannymph) + the dormant kit slot
   `skillName8`(+`skillLevel8`, marauder only) + `baseTexture`(maenad). Stripping
   `baseTexture=maenad` on the marauder + Hades-Marshal pets falls the ShadowStalker /
   MachaeHero01 mesh back to its OWN default skin (both source monsters define no
   baseTexture). The enslaver soul-pet's baseTexture is already the boss's
   `NewSkeleton_Charcoal` (marker does not match), so it is untouched.
2. **INHERIT the source monster's shroud**: copy the source's
   `charFxPakRunningNames` TypedField onto the pet -> each pet ends up with EXACTLY
   its own source monster's shroud (enslaver <- svc_enslaver_darksmoke, marauder <-
   drxshadowcloak, Hades Marshal <- hades2_shadowcloud).

The enslaver soul-pet's `specialAttackSkillName` is NOT stripped: it is the friendly
pet-of-pet marauder summon (`svc_enslaver_petmarauders`, wired in `_create_enslaver`
step 5), which matches no green marker.

### Safety of the added shroud (honest scope - b55r2 MEDIUM correction)
Adding `charFxPakRunningNames` to a Pet.tpl record is **crash-safe**: it is a pure
string FX-path field (not the equipment/loot class that crashes a Pet.tpl); Pet.tpl
is a strict Character superset of Monster.tpl; the field is copied verbatim with no
explicit dtype. **But it is NOT a proven-on-a-pet render path**: across the entire
golden arz (51,029 records) **zero Pet.tpl records carry `charFxPakRunningNames`** -
only 5 MONSTER records do (the cited Vashkarr/marauder precedents are MONSTERS, not
pets). So whether the dark smoke actually RENDERS on a pet is confirmable only in
Will's in-game test. This does not gate the core fix: the pets end up **non-green
regardless** (the Enslaver pet keeps its charcoal skin; the marauder/Hades-Marshal
pets fall back to their mesh's dark default after the maenad strip), which already
satisfies "green not black" - the black smoke is the upgrade to confirm in-test.

`verify(db)` (run_registry_verifies, post-finalization) asserts, over every pet in
the three families that exists: zero green residue (FX fields + kit slots) AND the
correct source shroud in `charFxPakRunningNames`. Fail-loud (negative-tested both
directions).

## Sibling sweep (monster-vs-pet FX divergence across the whole roster) - CORRECTED

Ground-truth sweep of the golden arz (`scratchpad/b55r2_sweep.py`):

- **EXACTLY 5 records carry a custom `charFxPakRunningNames`, and all 5 are MONSTERs**
  (0 Pet records carry one). These 5 are the ENTIRE universe of "retinted-dark"
  monsters, so a same-class divergence can ONLY come from one of them.
- Of the 5, **EXACTLY 3 are `_build_boss_summon` soul sources** whose pets kept the
  green Lyia rig (the three families fixed here):

  | source monster | custom shroud | soul pets | status |
  |---|---|---|---|
  | `um_toxeus_enslaver_99` | svc_enslaver_darksmoke | toxeus_enslaver_1..3 | FIXED |
  | `um_enslaver_marauder_99` | drxshadowcloak | enslaver_marauder_1..3 | FIXED |
  | `svc_um_hadesmarshal_80` | hades2_shadowcloud | hadesmarshal_1..3 | **FIXED (b55r2)** |

- The other **2 shroud monsters have NO soul-summon pet**, so nothing diverges:
  - `um_vashkarr_99` (drxshadowcloak) - its soul is a STAT `_create_soul`, NOT a
    summon; its `svc_vashkarr_summonhorde` raises separate fodder, not a vashkarr
    pet. (Correctly excluded.)
  - `boss_satyrshaman_55` (ringofflame) - an arena APEX ("Aithon, the Ember-Crowned"),
    referenced only by the arena pool, no soul. (Correctly excluded.)

=> **3 same-class families / 9 pets.** (r1 asserted "exactly two ... and no other";
that was false - it missed the Hades Marshal. Corrected here, with the full 5-monster
enumeration as proof.)

### Not same-class (correctly excluded)
- **The Devourer of Blood `bloodtoxeus_1..3`** (crimson RevenantPoison) SHARES the
  RevenantPoison mesh with the Enslaver, but its source is `um_bloodtoxeus_99`
  (**NO custom shroud**) - it was never retinted, so it is not a same-class
  divergence, and its green poison is INTENTIONAL and STAYS (Will 2026-07-14). The
  module never touches it (proven byte-identical in the replay). A mesh-only linkage
  would wrongly group it under the Enslaver; the authoritative `_build_boss_summon`
  source disambiguates.
- **The broader systemic Lyia green.** 82 of 222 soul pets carry the 4-field buff
  residue (envenom/heartofoak/regrowth/natureswrath); 89 carry the module's full
  marker set. Subtracting the 9 same-class + 3 Devourer leaves **~77 pets** whose
  source was never retinted (their green is the systemic Lyia-clone artifact, not a
  contradiction of a deliberate dark identity). Mass-repainting every summon pet is a
  design call, not a bug fix (the Devourer proves some greens are wanted), so it is
  FLAGGED for Will, not swept in this crash-history pet round.

### Out-of-visual-scope residue on these pets (b55r2 LOW note)
Every one of these Lyia-clone pets still carries non-visual Maenad residue this fix
does not touch: `alertSound/deathSound1/rallySound/stunSound/voxSound` = Maenad
sound paks (a dark skeleton/machae emitting Maenad female screams),
`controllerAggressive/Defensive = controller_maenadmerc`, and dormant loot refs
(`lootFinger2Item1=maenadvanguard_soul_n`, `lootMisc2Item6=doll_maenad`; harmless as
`dropItems=0`). These are AUDIO/behaviour/loot, NOT the green VISUAL Will reported,
so leaving them is a defensible scoping call - noted for the same future systemic
pet-identity pass the ~77-pet Lyia residue is flagged for.

## ITEM vs PET record (so Will's retest is set up right)

The summon FX rides entirely on the **PET records** (`toxeus_enslaver_1..3`,
`enslaver_marauder_1..3`, `hadesmarshal_1..3`). When the soul's granted skill fires,
the engine resolves `spawnObjects` against the CURRENT DB and instantiates the pet
record live. TQ bakes ITEM properties at pickup, but the soul ITEM only bakes
`itemSkillName / itemSkillLevel / augments` - none of which change here; the
skill->pet resolution is live. **Therefore the fix reaches Will's EXISTING Enslaver
and Hades Marshal soul items.** He does NOT need a freshly-dropped soul - only a full
Steam/TQ restart so the game loads the new arz (per the standing "restart before
every test" rule). Summon the Enslaver (and the Hades Marshal) from the existing
soul: the pet should be a dark skeleton/machae with its source's dark shroud and no
green poison, and the marauders the Enslaver raises should be dark shadow demons.

## Verification (no heavy build; dry-run replay vs golden `b33c5a44`)

`scratchpad/b55r2_replay.py` (load golden -> run the module's `apply()` -> diff +
`verify()` + negatives + write/reload). Faithful because the pet FX fields touched
are NOT altered by the build's finalization phase (which only touches soul
equipmentring itemSkillName + cyclops de-filler + tag renames), so the golden arz's
pet FX == what the module sees at run_registry step 2. The golden arz predates the
module, so all 9 pets are in their green pre-fix state and the module fixes all 9.

```
[1] SCOPE  : apply modified EXACTLY the 9 family pets (db._modified == the 9)  PASS
[2] per-pet: 0 green-FX residue after fix; charFxPakRunningNames == its source shroud
      toxeus_enslaver_1..3     <- svc_enslaver_darksmoke_charfxpak     PASS
      enslaver_marauder_1..3   <- drxshadowcloakrunning_fx_pak         PASS
      hadesmarshal_1..3        <- hades2_shadowcloud_charfxpak         PASS
[3] module verify() PASSED on the fixed db
[4] Devourer bloodtoxeus_1..3 NOT modified + fields BYTE-IDENTICAL (green intended, excluded)
[6] write->reload round-trip: all 9 non-green + correct shroud persist (arz 55,350,877 B)
```

Negative tests - each MUST fail the module's verify (targeted at the NEW Hades
Marshal family to prove verify() genuinely covers it both directions):
```
[replant envenomweapon buffSelf on hadesmarshal_1]  verify FAILED LOUD  OK
[clear the inherited shroud on hadesmarshal_1]       verify FAILED LOUD  OK
[wrong shroud value on hadesmarshal_2]               verify FAILED LOUD  OK
[replant green kit slot skillName20=sylvannymph]     verify FAILED LOUD  OK
[replant maenad baseTexture on hadesmarshal_1]       verify FAILED LOUD  OK
```

Contracts (over a written fixed arz = golden + module, 9 records modified), golden
vs fixed, normalized:
- **summons contract** (`tools/contracts/contracts_summons.py`): violation output
  BYTE-IDENTICAL (only wall-clock differs) - **652 viol (96 P0 / 0 P1 / 556 P2) on
  BOTH**, so **0 new violations**. (The 652 are pre-existing systemic pet issues in
  build40, out of this fix's scope; the summons contract does not test the FX fields
  this module edits.)
- **resources contract** (`contracts_resources.py`): BYTE-IDENTICAL -> **0 new
  violations**. Confirms the added `hades2_shadowcloud_charfxpak` shroud ref on the
  Hades Marshal pets RESOLVES (no new C-RES-DBR dangling ref).
- **souls contract** (`contracts_souls.py`): BYTE-IDENTICAL -> 0 new violations
  (FX edits touch no soul item / grant skill).
- `py_compile` clean (no SyntaxWarning); `tools/patches/_check_registry.py` OK
  (**14 modules**, order `e64bc6e6...` - unchanged; only a family entry was added
  inside the module, not the manifest).

## Files changed
- `tools/patches/enslaver_pet_fx.py` - add the Hades Marshal family to `_FAMILIES`
  (+ constants), correct the docstring's sweep claim, soften the shroud-safety
  wording. apply + fail-loud verify are unchanged in logic (generic over `_FAMILIES`).
- `docs/BACKLOG.md` - B55 entry (r2 update).
- `docs/reports/b55_enslaver_pet_fx.md` - this report.
- Scratchpad harnesses (analysis only, not shipped): `b55r2_sweep.py`,
  `b55r2_hades_kit.py`, `b55r2_counts.py`, `b55r2_replay.py`, `b55r2_make_fixed.py`.

## What Will will see (after a Steam restart; existing souls are fine)
- Summon the Enslaver from his soul: a **dark** skeleton lord (charcoal skin) wreathed
  in black smoke, **no green poison glow**.
- The marauders he raises: **dark shadow demons** (shadow-cloak shroud), no green,
  no maenad skin.
- Summon the Hades Marshal (Menoetes) from his soul: a **dark machae** in the hades
  shadow-cloud shroud, **no green poison glow**, no maenad skin.
- The Devourer of Blood is unchanged (still its intentional crimson/green).
- Retest note: the black-SMOKE shroud on a pet has no in-mod precedent (data-only
  confidence); please confirm in-game whether the dark smoke renders. Non-green is
  guaranteed either way.
