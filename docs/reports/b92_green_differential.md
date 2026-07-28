# b92 - GREEN GLOW: differential diagnosis vs Will's control. ROOT CAUSE FOUND (5th attempt)

Branch `fix/green-diff` (worktree `.claude/worktrees/green-diff`), from `main` 8c3445c.
Ground truth throughout: the **deployed DEV arz** `1c27d5fa650b5c076696db4ad379672f`
(`CustomMaps/SoulvizierClassicDEV/Database/SoulvizierClassicDEV.arz`) - exactly what
Will is looking at - plus the shipped `.arc` set and the base-game
`Creatures.arc` / `Effects.arc` **read at the byte level**.

## Will's lead (2026-07-27, verbatim) - it was correct in every particular

> "i am pretty sure it is a skill or ability or something that is causing the green
> glow. i think this was inherited from the Toxeus the Murderer uber boss base monster
> that we created these monsters off of. If you compare the visuals to the secret
> passage toxeus the murderer who doesnt have the green glow, you may be able to find
> the difference"

The control was the whole game. Four prior rounds had no clean comparison and kept
guessing at assets.

---

## 1. THE ROSTER (every Toxeus variant in the deployed arz)

56 records match `toxeus`. The **monsters** are:

| # | record | display tag | skin | mesh | where placed | role |
|---|---|---|---|---|---|---|
| 1 | `records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr` | `tagMonsterName190` | `newskeleton_crimson.tex` | **RevenantStorm.msh** | **0 DB refs** - a fixed map placement; drops `sp_toxeus_soul_n` (**sp = secret passage**) | ⭐ **WILL'S CLEAN CONTROL** - the "dream like" secret-passage Toxeus (full Dream kit: LucidDream, DistortionWave, PhantomStrike, DistortionField), `Hero` |
| 2 | `records\creature\monster\skeleton\um_toxeus_21.dbr` | `tagMonsterName190` | `newskeleton_grean.tex` | RevenantPoison.msh | champion slot in **Greek area001** undead pools (+ Egypt/Orient); drops `toxeus_soul_n` | the generic **GREEN-POISON Greece** Toxeus the Murderer - green **BY DESIGN** (Will). `Boss` |
| 3 | `records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr` | `tagMonsterHemorrheus` | `newskeleton_crimson.tex` | RevenantPoison.msh | `egg_blooddragon` (chest guard) + `q_bloodtoxeus_lone` / `q_bloodtoxeus_ambush` | 🟢 **DEVOURER OF BLOOD** - green-afflicted |
| 4 | `records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr` | `tagSVCMonsterEnslaver` | `NewSkeleton_Charcoal.tex` | RevenantPoison.msh | `q_enslaver_warband`, `q_yard_enslaver` + 279 roaming pool refs | 🟢 **ENSLAVER OF SOULS** - green-afflicted |
| 5 | `records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr` | `tagSVCMonsterToxeusHunt` | - | ShadowStalker.msh | Legendary-only Endless Hunt pool | the roaming stalker - **not affected** |
| 6 | `records\xpack\creatures\monster\zzdev\z_toxeus.dbr` / `old_z_toxeus.dbr` | `tagMonsterName190` | crimson / grean | RevenantStorm / RevenantPoison | unreferenced dev leftovers | not shipped content |

Plus the **End of All Things** capstone, which exists only as pets
(`toxeus_eoat_1..3`, cloned from the Devourer pets) + `summon_toxeus_eoat` +
`soul_of_toxeus_endofallthings` + `svc_toxeus_eoat_formula`.

**Control resolution was not guessed.** `um_toxeus_99` has **zero** pool/proxy
references in the whole 51,085-record DB (so it is a fixed map placement, which is
what a secret-passage boss is), it drops the soul literally named
`sp_toxeus_soul_{n,e,l}`, and it is the only variant carrying the Dream-mastery kit
that makes it read "dream like". `um_toxeus_21` is a champion entry in
`proxies greek\area001\pools\undead\*` - the generic Greece spawn.

---

## 2. THE DIFF - what the green pair carry that the clean control does not

Full field-level diff + one hop into every skill, buff, aura, pet, projectile, death
FX, weapon glow, shroud and texture. Transitive FX-asset closure per boss.

### 2a. Skill/ability sets (Will's first hypothesis - tested first, first-class)

Set difference of the complete skill/FX reference closure:

| shared by BOTH green bosses, absent from the control | also on the green-by-design Greece base? |
|---|---|
| `boss skills\boss_conversionimmunity.dbr` | no |
| `monster skills\attack_radius\toxeus_bladestorm.dbr` | yes |
| `spirit\lifedrain.dbr` | no |
| `stealth\lethalstrike_mortalwound.dbr` | yes |

None of these is a persistent glow: bladestorm/mortalwound are one-shot attacks,
`lifedrain` is a beam, `boss_conversionimmunity` is a passive with no FX. Decisive
counter-evidence: **the Devourer carries no `charFxPakRunningNames` shroud at all**,
so no shroud/skill theory can explain a permanent glow around him. Skills are NOT the
mechanism. (Will's instinct that something was *inherited from the base monster* was
right; it just wasn't a skill record.)

### 2b. THE ANSWER - the `mesh` field

| | mesh | skin |
|---|---|---|
| ⭐ CONTROL `um_toxeus_99` | **`RevenantStorm.msh`** | crimson |
| GREEN BASE `um_toxeus_21` | **`RevenantPoison.msh`** | grean |
| 🟢 DEVOURER `um_bloodtoxeus_99` | **`RevenantPoison.msh`** ← inherited | crimson |
| 🟢 ENSLAVER `um_toxeus_enslaver_99` | **`RevenantPoison.msh`** ← inherited | charcoal |

**A TQ `.msh` file can attach an entity to a bone.** Read straight out of the shipped
`Creatures.arc` bytes, every Revenant mesh ends with:

```
CreateEntity
{
    attach = "Waist"
    entity = "Records\Effects\MonsterFX\Buffs\Revenant<Element>_FX.dbr"
}
```

`RevenantPoison.msh` therefore hangs a **permanent particle aura off the Waist bone of
every creature that wears it** ->
`Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr` (an `EffectEntity`, resolved
from the base-game db) -> `Effects\MonsterFX\Buffs\RevenantPoison.pfx`.

The **entire** roster corroborates it: every *other* `RevenantPoison.msh` wearer in the
shipped DB also wears `newskeleton_grean.tex` (`cm_revenanttainted_16`,
`um_nefesiris_30`, `um_rotbone_14`, `um_toxeus_21`) - vanilla deliberately pairs that
mesh with the green skin. Our two bosses are the **only** wearers given a crimson /
charcoal skin: the skin override landed, the mesh-baked aura did not, so a green cloud
sat on a red/black body.

---

## 3. COLOUR PROVEN FROM THE ASSET BYTES, NOT THE NAME

Standing law (born from `343_dark_smoke`, which is NAMED dark and RENDERS green).

All four `Revenant*.pfx` are structurally identical - same emitter names
(`Dark Clouds` / `New Dark Clouds`), same textures
(`Effects\Textures\Organism01.tex` + `Organism02.tex`), same shaders
(`ParticleCombine.ssh` / `ParticleAdditive.ssh`). Poison and Storm are even the same
byte length (2061 B). **They differ ONLY in three numeric keyframe tracks.**

Decoding those three tracks as R/G/B reproduces all four known element colours
*simultaneously* - which is what validates the channel assignment (a self-checking
reader; fire/frost/storm are the sanity controls):

| variant | R | G | B | renders |
|---|---|---|---|---|
| `RevenantFire` | **1.000** | 0.518 | 0.007 | orange/red ✔ |
| `RevenantFrost` | 0.534 / 0.520 | 0.824 / 0.844 | **1.000** | ice blue ✔ |
| **`RevenantPoison`** | 0.534 / 0.520 | **1.000 / 0.974** | 0.591 / 0.637 | **GREEN** ✔ |
| `RevenantStorm` (control) | 0.592 / 0.604 | **0.501 / 0.513** (lowest) | 0.695 / 0.722 | blue-violet ✔ |

`RevenantPoison` peaks the **green** channel at 1.0 with red lowest. The control's
`RevenantStorm` puts green at its **lowest** channel. **PROVEN-from-bytes.**

Also checked and cleared from bytes: the mesh **material** block is byte-identical
across all four (same `specularColor` / `specularPower` / `fresnelAmount`), and all
four reference the same `NewSkeleton_White.tex` + `GoldenSkeleton01BMP.tex`. So the
mesh geometry/material is innocent - the aura is entirely the attached entity.

---

## 4. WHY THE FOUR PRIOR ROUNDS ALL FAILED

**Every prior fix operated on the database. The attachment is inside the MESH FILE.**
No `.arz` scan of any depth - fields, chain, or transitive skill closure - can see a
`CreateEntity` block compiled into a `.msh`.

- **b55** recoloured DB *emission fields* on 9 pets. Never touched `mesh`.
- **b71** walked the item->skill->icon->spawnObjects->pets chain and correctly proved it
  byte-identical. `mesh` was identical too - because it was uniformly *wrong*, so a
  drift-detector could never flag it.
- **b75** decoded `343_dark_smoke.pfx`, found it renders green, and swapped the
  Enslaver's `charFxPakRunningNames` to the proven-black `drxshadowcloak`. That was a
  **real fix to a real second surface** - it just wasn't this one. Two things prove it
  could never have worked: (a) the **Devourer has no `charFxPakRunningNames` at all**,
  so a shroud swap cannot explain his green; (b) b75's own transitive skill sweep came
  back green-free and it concluded "the green is an asset the DB merely points at" -
  right instinct, but it looked at the *shroud* asset the DB points at, not the *mesh*
  asset the DB points at. The mesh was one field further out and was never suspected;
  b75 even inspected `RevenantPoison.msh`, saw only `NewSkeleton_White.tex` + a bump
  map, and explicitly cleared it as "innocent" - it stopped at the texture strings and
  never read the trailing entity script.
- **b81** fixed pet identity/race - orthogonal.

Bonus: b75's unexplained "his marauders also have a green aura around them" now has a
mechanism. The marauders are `ShadowStalker.msh` with the proven-black `drxshadowcloak`
and zero green markers - they were fighting *inside* the boss's Waist-attached green
particle cloud. Removing the boss's aura removes theirs.

---

## 5. THE FIX

Repoint `mesh` to **`Creatures\Monster\Skeleton\Skeleton01.msh`** on the Devourer and
Enslaver families only. Chosen from a byte-level scan of every skeleton mesh in
`Creatures.arc` for `CreateEntity` blocks:

| candidate | shader + textures | CreateEntity |
|---|---|---|
| `RevenantPoison/Storm/Fire/Frost` | StandardSkinned + NewSkeleton_White | **yes** - coloured aura |
| `skeletonspirit01` | *StandardBlendedGlow* + SkeletonGlowing01 | no, but different shader/skin - rejected |
| `skeletonrumorboss` | - | yes (Boss Aura) - rejected |
| `goldenskeleton01` | StandardSkinned + *GoldenSkeleton01.tex* | no - viable, different base skin |
| ✅ **`skeleton01`** | **StandardSkinned + NewSkeleton_White + GoldenSkeleton01BMP** (identical to RevenantPoison) | **NO** |

`Skeleton01.msh` is the right drop-in: **same shader and same textures** so each boss's
`baseTexture` override keeps landing exactly as today; **closest geometry** of every
candidate (94.8% byte-identical body); it is the **canonical mesh for
`anm_skeleton01.dbr`**, the animation table both bosses already use; and **721 shipped
records** already wear it, many with a charcoal skin override.

Nothing green is left to render, and each boss's deliberate identity survives intact:
the Devourer keeps crimson + `svc_black_poison` (R-7), the Enslaver keeps charcoal +
the Will-confirmed BLACK `drxshadowcloak` smoke (R-10).

### Owner: registry module `tools/patches/toxeus_mesh_aura.py`

Registered after `toxeus_endofallthings` / `toxeus_souls_100`, before `visuals`, so it
is the ratified **final writer of `mesh`** on these records and the EoAT pets it clones
are provably unchanged. `apply()` refuses to run unless all 12 targets are on
`RevenantPoison` beforehand, and proves its own blast radius by snapshotting `mesh`
across every record in the DB before and after.

The two monolith sites that chose the green mesh
(`apply_svc_patches.py` Devourer visual block and `_EN_BOSS_MESH`) now carry
⚠️ comments pointing here, so nobody "restores the Athens mesh" and re-greens them.

### The 12 records (exactly the record-diff)

Devourer: `um_bloodtoxeus_99`, pets `bloodtoxeus_1..3`, proxies `q_bloodtoxeus_lone`,
`q_bloodtoxeus_ambush`.
Enslaver: `um_toxeus_enslaver_99`, pets `toxeus_enslaver_1..3`, proxies
`q_enslaver_warband`, `q_yard_enslaver`.

### Rulings checked (docs/WILL_RULINGS.md) - none regressed

R-5/R-6 (kits), R-7 (black poison - **reinforced**: the green that fought it is gone),
R-10 (Enslaver black shroud - untouched, `charFxPakRunningNames` not modified),
R-11/R-12 (skeleton identity - mesh stays in the same skeleton family, same anm table),
R-3/R-49 (chest spawn - proxies keep pool/limit/chance, only `mesh` moves),
R-48 (100% soul drop - untouched), R-8 (EoAT - deliberately untouched).

---

## 6. THE GATE (four recurrences = a machine check, not another report)

`toxeus_mesh_aura.verify()` runs in registry step 4 over the FINAL merged db and fails
the build loud, in **both** directions:
- any of the 12 targets on a mesh whose embedded `CreateEntity` attaches an aura, or on
  any unaudited mesh (an unknown mesh may carry its own aura);
- **and** `um_toxeus_21` no longer on `RevenantPoison` (Will's intentional green) or
  `um_toxeus_99` no longer on `RevenantStorm` (the control).

**Negative test** `scratchpad/negtest_b92.py` - **17/17 legs correct**:

| leg | expected | got |
|---|---|---|
| fixed scratch build | PASS | PASS |
| ⭐ **today's shipped DEV arz `1c27d5fa` as-is** | **FAIL** | **FAIL** |
| replant green mesh on each of the 12 targets | FAIL x12 | FAIL x12 |
| strip the aura from either PROTECTED record | FAIL x2 | FAIL x2 |
| unaudited mesh (`SkeletonSpirit01`) on the Devourer | FAIL | FAIL |

The second leg is the important one: **the gate reproduces and rejects exactly the state
Will is looking at right now.**

---

## 7. VERIFICATION

- Full coupled build **EXIT 0**, `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`. All in-build
  gates + **25/25 registry verify hooks** green (incl. `toxeus_mesh_aura`). A7
  Occult/Hunting golden freeze **PASS** (84 waived, 0 other). Unlock-alignment PASS.
- **Record-diff vs the deployed DEV arz: 0 ADDED, 0 REMOVED, 12 MODIFIED, 1 field each,
  all `mesh` RevenantPoison -> Skeleton01. Zero collateral.** No soul/skill/loot/pool/
  map/quest/text record touched.
- **Text.arc rebuilt byte-identical** to the deployed one (`fcca4927...`) - the change is
  DB-only, and the pair is coherent.
- **Contracts** (souls/summons/resources): **GATE PASS, 0 P0 / 0 P1 / 4905 P2** -
  *identical totals to the same run against the deployed arz* => **0 new violations**.
  `MONSTER-MESH` (mesh-resolves) reports only 2 pre-existing offenders, neither ours:
  `Skeleton01.msh` resolves.
- Deployed arz md5 stable across two reads.

## 8. DEPLOYED (DEV)

| artifact | md5 | state |
|---|---|---|
| `SoulvizierClassicDEV.arz` | `5143ad1a44a9964c22578e00613f3e14` | **NEW** (was `1c27d5fa650b5c076696db4ad379672f`) |
| `Text.arc` | `fcca49277b9d31ed451e4a6843898843` | unchanged (rebuild byte-identical) |
| `Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | ✅ **UNTOUCHED** (required) |
| `Quests.arc` | `5e664c7b190965fd69f6ff15d77d85e4` | ✅ **UNTOUCHED** (required) |

Rollback: `local/DEV_arz_deployed_prev.arz` + `local/DEV_Text_deployed_prev.arc`.

> NOTE: the `Text.arc` copy returned "Device or resource busy" - something (TQ or
> OneDrive) holds the file open. **Benign: the deployed bytes already equal the rebuild
> exactly**, so there is nothing to write. It is a reminder that the standing
> restart-Steam-before-every-test rule applies here.

## 9. WILL TEST INSTRUCTIONS

Kill TQ **and** Steam, restart both (standing rule - the running game holds mod files in
memory), then:
1. **Devourer of Blood** - blood cave, beside his hidden chest. Expect: a **crimson**
   skeleton with **no green cloud**.
2. **Enslaver of Souls** - expect a **charcoal/black** skeleton wearing the same black
   smoke his Enslaved Shadow Marauders wear, **no green** - and the marauders should now
   read black too (their apparent green was bleed from his cloud).
3. **Both soul summons** - DISMISS any currently-summoned pack and **RE-SUMMON** (a live
   pet keeps its old appearance).
4. Please confirm the two that must NOT change: the **Greece** Toxeus the Murderer is
   **still green** (intentional), and the **secret-passage** Toxeus is untouched.

## 10. REGISTERED DEBT (not fixed here - deliberately out of scope)

1. **`toxeus_eoat_1..3` (End of All Things pets) still wear `RevenantPoison.msh`** and
   therefore still carry the inherited green aura. They are cloned from the Devourer
   pets and owned by the `toxeus_endofallthings` lane (R-8 specifies an "ash-pale
   body", so green is wrong there too). One-line fix in that lane, or add the 3 records
   to `toxeus_mesh_aura.TARGETS`. **WILL-DECISION / lane owner.**
2. **Devourer soul pets still carry Lyia nature residue** - `buffSelf2SkillName=
   heartofoak`, `healSkillName=regrowth_lyia`, `deathEffect=343_natureswrath_low_fx`.
   b75 deliberately skipped the Devourer (`protect_green=True`, "Devourer green stays"
   2026-07-14); R-7 (2026-07-16) later asked for black poison and b83 replaced the
   envenom, but these three were never revisited. Two are functional (a heal and a
   health buff), so removing them is a **balance** call, not a visual one.
   **WILL-DECISION.**
3. **Other `343_dark_smoke` users** (Diadochi generals `svc_ashsmoke_charfxpak`,
   Helepolis) still ride the green-rendering pak flagged by b75/R-10 - unrelated to the
   mesh aura, still open.
4. The **F2 summons-contract** in-build gate self-skips when no `Resources` dir sits
   beside the build output; its fallback discovery pointed at an unrelated worktree.
   Cosmetic tooling debt - the contract was run standalone here and passed.
