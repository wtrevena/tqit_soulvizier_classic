# b85 - Blood Cult High Priest summon (R-43: "the high priest soul should allow you to summon the high priest")

> Branch `fix/soul-tiers` (extends on top of the vetted-GO b78 tip `50d4bdfc`, off `main` `33d25d6`,
> golden arz `917d9047`). Lane scope: the `bwpriest_*` pet/skill records + the b71 CHAIN gate roster
> entry ONLY. Did NOT touch `bwpriest_soul_{n,e,l}` (the RING records b78 already proved strictly
> tier-progressing), any other soul family, the map, or Quests/Levels.

## R-43 ruling (verbatim, docs/WILL_RULINGS.md main - not present on this branch's base; see
"Ledger note" at the end of this report)

> "the high priest soul should allow you to summon the high priest" + companion check "does the
> epic soul spawn the epic monster?"

## 1. Ground truth (the chain BEFORE this round)

The soul family `records\item\equipmentring\soul\svc_uber\bwpriest_soul_{n,e,l}.dbr` (name tag
`tagSVCSoulBWHighPriest`, "Blood Cult - High Priest Soul") drops from
`records\drxcreatures\bloodwitch\c_disciple_miniboss.dbr` - **the Blood Cult High Priest himself**,
confirmed from his own `description` tag `tagBWHighPriest`. Decoded from the golden arz (`917d9047`):

| field | value |
|---|---|
| mesh | `DRX\meshes\disciple.msh` |
| baseTexture / bumpTexture | `disciple_miniboss.tex` / `disciple_minibossbmp.tex` |
| scale | 2.5 |
| characterRacialProfile | `God` |
| charAnimationTableName | `records\drxcreatures\bloodwitch\anm_seductress.dbr` |
| controller | `records\drxcreatures\bloodwitch\controller_disciple.dbr` |
| sounds | `snd_highpriest_voxpak` (voice), `snd_highpriest_alertpak` (alert) - his OWN dedicated packs |
| his real casts | `discipleboss_aura` (self-buff), `disciple_bloodstare` (specialAttack2, ranged blood-jet, **isPetDisplayable=1** on its own record), `disciple_bloodrain_bleedx50_vitx10` (specialAttack3, AOE, **isPetDisplayable=0** on its own record - the game's own "not for pets" flag), and `discipleboss_summon_melinoe.dbr` (his primary `specialAttackSkillName` - **his own signature summon**: `Class Skill_SpawnPet`, `petLimit 18`, `petBurstSpawn 6`, `spawnObjects` = 20x `discipleboss_bladedancer.dbr`) |

**The defect (pre-R-43 code):** the granted summon skill `summon_bwpriest.dbr` did NOT spawn the High
Priest. It spawned 3 tiers of a **Melinoe blade-dancer** built from `discipleboss_bladedancer.dbr`
(mesh `Melinoe01.msh`, race `Demon`) - which is not the High Priest's own body, it is the monster HE
casts as HIS OWN combat summon. Confirmed in the shipped flavor text (now rewritten, see \S4):
*"His soul, released, calls forth a Melinoe blade-dancer to fight at your side"* and the granted-skill
name *"Call the Blood Blade-Dancer"*. Will's ruling requires the High Priest himself.

## 2. Design (mirrors the b71 Enslaver "boss pet + tamed pet-of-pet" pattern exactly)

1. **`bwpriest_1/2/3`** = the High Priest **HIMSELF**, built via the shared `_build_boss_summon`
   pipeline (source `c_disciple_miniboss.dbr`): mesh/texture/anim-table/controller/gear/skill-kit
   auto-mirrored from his own record, D19 pet-mobility assert, b40 granted-skill icon, b71 pet-bar
   portrait.
2. **`bwpriest_attendant_1/2/3`** = the Melinoe blade-dancer HE casts in combat (source
   `discipleboss_bladedancer.dbr`), rebuilt as a **tamed, non-player-facing pet-of-pet**
   (`player_facing=False`, `isPetDisplayable=0`) - his real signature summon stays present (he still
   summons her), but capped to the **PROVEN pet-of-pet depth** established by the Enslaver/marauder
   family (`svc_enslaver_petmarauders.dbr`: petLimit 3-4, tiny burst, 0 mana cost) instead of the raw
   monster-scale swarm (`petLimit 18`, `petBurstSpawn 6`). This is the "note the depth implications,
   keep to proven depth" instruction: his real ability is honored, not amplified into an
   18-pet friendly swarm.
   - New tamed skill: `records\skills\soulskills\svc_bwpriest_summonmelinoe.dbr` (`Skill_SpawnPet`,
     `isPetDisplayable=0`, `petLimit=2`, `petBurstSpawn=1`, `skillCooldownTime=10.0`,
     `skillManaCost=0.0`, `spawnObjects` = the 3 tamed attendant pets) - a strictly SMALLER depth
     than the Enslaver's own proven `petLimit=3-4` envelope.
3. The raw `discipleboss_summon_melinoe.dbr` reference that `_build_boss_summon`'s
   `_update_existing_fields` copies verbatim onto `bwpriest_1/2/3`'s `specialAttackSkillName` (the
   SAME class of leak the Enslaver's marauder-summon repoint fixes) is swept and repointed to the
   tamed `svc_bwpriest_summonmelinoe.dbr` post-build (`_bwp_repoint_raw_refs`).
4. The source's own AOE (`disciple_bloodrain_bleedx50_vitx10`, flagged `isPetDisplayable=0` on its
   OWN record - the game's own "not for pets" marker) is swept off `bwpriest_1/2/3` after the
   kit-mirror places it (`_bwp_strip_skill_ref`) - never granted to a pet, honoring the source's own
   flag.
5. **Race + sounds** (R-11's general law: "boss-summon pets inherit race/sounds/distress from their
   SOURCE monster" - not auto-applied by `_build_boss_summon`, whose copy sets are skill/anim only):
   explicit post-set from each family's own source monster (`_bwp_mirror_identity`) - `God` for the
   Priest pets, `Demon` for the attendant pets; voice/alert/death/crit/stun/bodyfall/attack/impact
   sounds copied verbatim from each source.
6. **Green Lyia-clone residue** (`buffSelf2SkillName=heartofoak`, `healSkillName=regrowth_lyia`,
   `deathEffect=natureswrath` - the same class `enslaver_pet_fx.py` polices for the 3 "retinted-dark"
   families, present here because neither source monster defines those 3 fields so
   `_update_existing_fields` never overwrites the Lyia-clone default) is stripped explicitly
   (`_bwp_strip_green`) on both pet families.

## 3. Player-surface checklist (every item verified against the built arz/Text.arc)

| surface | before | after |
|---|---|---|
| soul item name | `{^F}Blood Cult - High Priest Soul` | unchanged (already correct) |
| soul item DESC | *"...calls forth a Melinoe blade-dancer to fight at your side"* | *"...calls the High Priest himself back from the dead to fight at your side, his bound Melinoe blade-dancer still answering his call"* |
| granted-skill (tooltip) name | "Call the Blood Blade-Dancer" | **"Summon the Blood Cult High Priest"** |
| granted-skill DESC | blade-dancer flavor | *"Call the Blood Cult High Priest himself back from beyond, staff and dark rites intact, to fight at your side."* |
| granted-skill icon | `bonefiendup/down` (DUPLICATE of kravmoloch's icon - a pre-existing identity collision) | `bloodbathup/down` - distinct, thematically fitting ("Blood Cult"), verified unclaimed by any other `_SUMMON_SKILL_ICON` entry, arc-resolves |
| pet-bar StatusIcon/StatusIconRed | `bonefiendup/down` (the SKILL-button texture, not a party-portrait asset - a latent mismatch) | `proxy_party_up/red` (neutral portrait; no bespoke `bloodbath_party_*` art ships, same convention as 10 other unmapped bosses) |
| pet mesh/texture/scale | Melinoe01.msh / bladedancer.tex / 1.4 | `disciple.msh` / `disciple_miniboss.tex` + `disciple_minibossbmp.tex` bump / 2.5 |
| race | `Demon` | `God` (matches the source monster) |
| sounds | Maenad voice/alert/death/crit/stun/bodyfall (Lyia-clone residue) | High Priest's own `snd_highpriest_voxpak`/`snd_highpriest_alertpak` + skeleton death/crit/stun/bodyfall (matches the source monster's own sound fields) |
| attendant pet identity | (did not exist as a separate surface) | `bwpriest_attendant_1/2/3`, `description=tagBWHighPriestAttendant` ("Blood-Bound Blade-Dancer"), distinct from the main pets |
| per-tier soul icons | `SVItems\jewelry\soul_{n,e,l}_icon.tex` via `_bmp()` | unchanged (already correct - soul RING records untouched) |

## 4. Text tags (new/changed, all verified resolving via `validate_tags.py`)

- `tagSVCSoulBWHighPriestDESC` - rewritten (item tooltip body).
- `tagSVCSummonBWHighPriest` - "Summon the Blood Cult High Priest" (was "Call the Blood Blade-Dancer").
- `tagSVCSummonBWHighPriestDESC` - rewritten (granted-skill tooltip body).
- `tagBWHighPriestAttendant` (NEW) - "Blood-Bound Blade-Dancer" (the attendant pet's `description` tag).
- `tagSVCSummonBWAttendant` (NEW) - "Call the Blood Blade-Dancer" (reuses the OLD skill-name text,
  now correctly describing the tamed sub-summon instead of the main soul).
- `tagSVCSummonBWAttendantDESC` (NEW).

## 5. Will's companion question: does the epic soul spawn the epic monster?

Answer: **yes.** `itemSkillLevel` on the soul selects the index into `summon_bwpriest.dbr`'s
`spawnObjects` array (`[bwpriest_1, bwpriest_2, bwpriest_3]`, unchanged paths/wiring - only the
CONTENT at those 3 paths changed this round). Decoded from the built arz (all 3 now share the
High-Priest identity; only the scaled stats differ):

| stat | Normal (`bwpriest_1`) | Epic (`bwpriest_2`) | Legendary (`bwpriest_3`) |
|---|---|---|---|
| charLevel | 39 | 56 | 71 |
| characterLife | 4800.0 | 6800.0 | 9000.0 |
| characterLifeRegen | 24.0 | 44.0 | 64.0 |
| handHitDamageMin / Max | 60.0 / 95.0 | 92.0 / 145.0 | 130.0 / 200.0 |
| skillLevel4 (his tamed attendant summon) | 18 | 19 | 20 |
| skillLevel8 (armor scaling) | 101 | 273 | 538 |

Every scaled field strictly increases Normal -> Epic -> Legendary; mesh/race/sounds/identity are
IDENTICAL across all 3 (same monster, just a stronger version of him) - the epic soul spawns the
epic-tier High Priest, exactly as the b78 strict-progress gate already proves for the RING side
(`souls_quality.verify` re-asserts "b78 Blood Cult High Priest gate" unchanged this round - the ring
records were not touched).

## 6. b71 chain-gate roster (item -> skill -> icon -> spawn -> pets -> portrait -> markers)

Added to `tools/patches/enslaver_pet_fx.py` `_CHAIN` (the anti-oscillation gate, run post-finalization
via `run_registry_verifies`):

```
{
    'label': 'Blood Cult High Priest',
    'souls': bwpriest_soul_{n,e,l},
    'skill': summon_bwpriest.dbr,
    'icon_stem': 'bloodbathup',
    'portrait_stem': 'proxy_party_up',
    'pets': bwpriest_{1,2,3},
    'sub_skill': svc_bwpriest_summonmelinoe.dbr,
    'sub_pets': bwpriest_attendant_{1,2,3},
}
```

This family was deliberately NOT added to `_FAMILIES` (the shroud-inherit fix-application list) -
that list's `verify()` unconditionally requires a matching `charFxPakRunningNames` shroud on every
member, and `c_disciple_miniboss` is not one of the 3 "retinted-dark" shroud monsters (adding it
there would false-positive-fail on "missing shroud"). `_CHAIN` has no such requirement and is the
correct, general identity/green-residue gate for this family.

## 7. Verification

- **py_compile**: `tools/apply_svc_patches.py` + `tools/patches/enslaver_pet_fx.py` - OK.
- **Full scratch build** (upstream SV098i/0.9/0.41 + base game, `local/scratch_r43/out/`) - **EXIT 0**.
  All 17 registry `verify()` hooks green, including:
  - `enslaver_pet_fx.verify` - OK ("chain icon+portrait on-identity across all 3 rostered families
    incl. R-43 Blood Cult High Priest").
  - `souls_quality.verify` - OK ("strictly progressing ... b78 Blood Cult High Priest gate").
- **Record-diff vs golden `917d9047`** (`tools/record_diff.py`): **intended-only** - 4 ADDED
  (`bwpriest_attendant_1/2/3.dbr`, `svc_bwpriest_summonmelinoe.dbr`), 4 MODIFIED
  (`bwpriest_1/2/3.dbr` 85 fields each, `summon_bwpriest.dbr` 2 fields: only the icon pair). **0
  REMOVED. `bwpriest_soul_{n,e,l}.dbr` (the RING records) do not appear in the diff at all - byte
  identical**, confirming the b78 strict-progress gate family is untouched.
- **`validate_summon_pets.py`** (B-SUMMON-1 render-chain / rig-pairing contract) - **PASS**, 0
  bwpriest warnings (mesh/anim-table pairing proven by the source monster itself; equipment
  loot-table-only per the strict mirror; every skill ref resolves).
- **`build_text_arc.py`** - Text.arc built clean; internal A7 Occult/Hunting golden-freeze gate
  **PASS (90 waived, 0 other)** - untouched by this lane (no mastery/skill-UI records touched).
- **`validate_tags.py`** - **RESULT: PASS**. "OK: all 349 referenced mod tags are present in
  Text.arc" (includes every new/changed bwpriest tag); "OK: all 409 authoritative tags are present".
  2 pre-existing unrelated WARNs (`tagNewMonster66`/`tagNewMonster46`, base/SV monster names,
  backlog, non-blocking, untouched by this lane).
- **`run_contracts.py --only souls,summons`** - **GATE: PASS**, 0 P0 / 0 P1 (112 P2, pre-existing
  "ported monster" roster-wide noise, 0 bwpriest hits).
- **Negative test** (`local/scratch_r43/negtest_r43.py`, calls `enslaver_pet_fx._verify_chain`
  directly against 4 in-memory variants of the built arz): baseline clean; planting the Lyia
  pet-bar portrait back on `bwpriest_1` -> **CAUGHT** (2 problems); planting the green
  `heartofoak` residue back on `bwpriest_2` -> **CAUGHT**; re-pointing `bwpriest_soul_n`'s granted
  skill back to `summon_lyia` -> **CAUGHT**. All 4 cases pass.
- **Idempotent**: two independent full scratch builds from the same source tree produced
  byte-identical output - arz md5 `47964fdd` (`47964fdda10c1c42840bb2f4dfd387e3`), both builds,
  55,392,545 bytes.

## 8. Files changed

- `tools/apply_svc_patches.py` - rewrote the "2.2 Blood Cult High Priest" section: new constants
  (`_BWP_*`), 4 new helpers (`_bwp_strip_green`, `_bwp_repoint_raw_refs`, `_bwp_strip_skill_ref`,
  `_bwp_mirror_identity`), rewrote `_create_bwpriest_pet_skill` to build both pet families via the
  shared `_build_boss_summon` pipeline; added `summon_bwpriest` to `_SUMMON_SKILL_ICON`; rewrote 3
  text tags + minted 3 new ones. `_create_bwpriest_soul` (the RING records) is UNCHANGED.
- `tools/patches/enslaver_pet_fx.py` - added the Blood Cult High Priest entry to `_CHAIN`; updated
  the `verify()` closing print to reflect the extended roster.
- `docs/reports/b85_highpriest_summon.md` - this report.
- `docs/BACKLOG.md` - R-43 / B85 entry (see below).

## 9. Ledger note (docs/WILL_RULINGS.md)

This branch's base (`fix/soul-tiers` off `main` `33d25d6`, the b78 tip) predates the ledger file's
creation on `main` (dated 2026-07-16, per the CLAUDE.md standing law); `docs/WILL_RULINGS.md` is
**not present on this branch**. Per the "no reset/pull" constraint on this lane, the ledger update
is NOT applied here (porting the file forward from `main` risks a stale fork that conflicts with
whatever else has landed on `main`'s copy since). **At merge/integration time, apply this status
line to `docs/WILL_RULINGS.md`:**

```
R-43 [2026-07-16] IMPLEMENTED b85 (this report) "the high priest soul should allow you to summon
the high priest" - bwpriest_1/2/3 = the High Priest himself (source c_disciple_miniboss); his real
signature summon (the Melinoe blade-dancer) survives as a tamed non-player-facing pet-of-pet
(bwpriest_attendant_1/2/3, proven Enslaver-marauder depth). Companion check (epic spawns epic)
verified: table in docs/reports/b85_highpriest_summon.md sec 5.
```

## 10. current_vs_new summary

**Before:** the soul's granted summon spawned a Melinoe blade-dancer (a Demon-race stand-in built
from the monster he himself casts in combat), never the High Priest's own body, identity, or voice.
**After:** the soul spawns the Blood Cult High Priest himself (his mesh/texture/scale/race/sounds/
kit, strictly tier-scaled), and his real signature blade-dancer summon survives as a tamed,
proven-depth pet-of-pet rather than being dropped or amplified into the raw 18-pet swarm.
