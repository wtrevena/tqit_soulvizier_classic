# b92 - GREEN GLOW: differential diagnosis vs Will's control. ROOT CAUSE FOUND (5th attempt)

> **ROUND 2 (2026-07-28).** Round 1's diagnosis was independently re-derived and upheld by the vet;
> its **remedy** was rejected (NO-GO) on three claims that were false against the bytes. This
> document is rewritten: the diagnosis stands, **the replacement mesh changed** from `Skeleton01.msh`
> to `GoldenSkeleton01.msh`, the scope grew from 12 to 15 records, the gate was narrowed so it
> encodes the BUG rather than an unratified art policy, the negative test is now a committed file,
> and every claim below was re-derived in round 2 from the shipped bytes. Round-1 claims that did
> not reproduce are named and corrected in section 9.

Branch `fix/green-diff` (worktree `.claude/worktrees/green-diff`), **rebased onto `main` 770bc35**
(round 1 was based on the then-current 8c3445c; `main` has since taken the debt-clearance lanes).

Ground truth throughout: the **pre-fix DEV arz** `1c27d5fa650b5c076696db4ad379672f` - exactly what
Will was looking at when he filed the bug - plus the shipped `.arc` set, the base-game
`Creatures.arc` / `Effects.arc` / `database.arz`, all **read at the byte level**.

> ⚠️ The rolling backup `local/DEV_arz_deployed_prev.arz` was **overwritten by a parallel lane** to
> `5143ad1a` during this work. The pre-fix ground truth is now pinned at
> **`local/b92_ground_truth_1c27d5fa.arz`** (md5 verified) and the negative test prefers that
> pinned name.

## Will's lead (2026-07-27, verbatim) - it was correct in every particular

> "i am pretty sure it is a skill or ability or something that is causing the green
> glow. i think this was inherited from the Toxeus the Murderer uber boss base monster
> that we created these monsters off of. If you compare the visuals to the secret
> passage toxeus the murderer who doesnt have the green glow, you may be able to find
> the difference"

The control was the whole game. Four prior rounds had no clean comparison and kept guessing at
assets. Will's instinct that the green was **inherited from the base monster** was exactly right; it
just was not a skill record.

---

## 1. THE ROSTER (every Toxeus variant in the ground-truth arz)

51,085 records; 56 match `toxeus`. The **monsters** are:

| # | record | display tag | skin | mesh | where placed | role |
|---|---|---|---|---|---|---|
| 1 | `records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr` | `tagMonsterName190` | `newskeleton_crimson.tex` | **RevenantStorm.msh** | **0 DB refs** - a fixed map placement; drops `sp_toxeus_soul_n` (**sp = secret passage**) | ⭐ **WILL'S CLEAN CONTROL** - the "dream like" secret-passage Toxeus (full Dream kit: LucidDream, DistortionWave, PhantomStrike, DistortionField), `Hero` |
| 2 | `records\creature\monster\skeleton\um_toxeus_21.dbr` | `tagMonsterName190` | `newskeleton_grean.tex` | RevenantPoison.msh | champion slot in **Greek area001** undead pools (+ Egypt/Orient); drops `toxeus_soul_n` | the generic **GREEN-POISON Greece** Toxeus the Murderer - green **BY DESIGN** (Will). `Boss` |
| 3 | `records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr` | `tagMonsterHemorrheus` | `newskeleton_crimson.tex` | RevenantPoison.msh | `egg_blooddragon` (chest guard) + `q_bloodtoxeus_lone` / `q_bloodtoxeus_ambush` | 🟢 **DEVOURER OF BLOOD** - green-afflicted |
| 4 | `records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr` | `tagSVCMonsterEnslaver` | `NewSkeleton_Charcoal.tex` | RevenantPoison.msh | `q_enslaver_warband`, `q_yard_enslaver` + roaming pool refs | 🟢 **ENSLAVER OF SOULS** - green-afflicted |
| 5 | `records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr` | `tagSVCMonsterToxeusHunt` | mesh default | ShadowStalker.msh | Legendary-only Endless Hunt pool | the roaming stalker - **not affected** |
| 6 | `records\xpack\creatures\monster\zzdev\z_toxeus.dbr` / `old_z_toxeus.dbr` | `tagMonsterName190` | crimson / grean | RevenantStorm / RevenantPoison | unreferenced dev leftovers | not shipped content |

Plus the **End of All Things** capstone, which exists only as pets (`toxeus_eoat_1..3`, **cloned from
the Devourer pets**) + `summon_toxeus_eoat` + `soul_of_toxeus_endofallthings` +
`svc_toxeus_eoat_formula`. 🟢 **Those three pets inherited the same green** - round 2 fixes them too
(section 5).

**Control resolution was not guessed.** `um_toxeus_99` has **zero** pool/proxy references in the
whole 51,085-record DB (so it is a fixed map placement, which is what a secret-passage boss is), it
drops the soul literally named `sp_toxeus_soul_{n,e,l}`, it is the only variant carrying the
Dream-mastery kit that makes it read "dream like", and the repo docs independently name it
"SP Toxeus" and group it with the Secret Passage bosses (`docs/BLOOD_TOXEUS_DESIGN.md:694,731`;
`docs/SOULS_COMPLETENESS_AUDIT.md:199-200`). `um_toxeus_21` is a champion entry in
`proxies greek\area001\pools\undead\*` - the generic Greece spawn.

---

## 2. THE DIFF - what the green pair carry that the clean control does not

Full field-level diff + one hop into every skill, buff, aura, pet, projectile, death FX, weapon
glow, shroud and texture; plus a transitive FX-asset closure per boss.

### 2a. Skill/ability sets (Will's first hypothesis - tested first, first-class)

Set difference of the complete skill/FX reference closure:

| shared by BOTH green bosses, absent from the control | also on the green-by-design Greece base? |
|---|---|
| `boss skills\boss_conversionimmunity.dbr` | no |
| `monster skills\attack_radius\toxeus_bladestorm.dbr` | yes |
| `spirit\lifedrain.dbr` | no |
| `stealth\lethalstrike_mortalwound.dbr` | yes |

None of these is a persistent glow: bladestorm/mortalwound are one-shot attacks, `lifedrain` is a
beam, `boss_conversionimmunity` is a passive with no FX. Decisive counter-evidence: **the Devourer
carries no `charFxPakRunningNames` shroud at all**, so no shroud/skill theory can explain a permanent
glow around him. Skills are NOT the mechanism.

### 2b. THE ANSWER - the `mesh` field

| | mesh | skin |
|---|---|---|
| ⭐ CONTROL `um_toxeus_99` | **`RevenantStorm.msh`** | crimson |
| GREEN BASE `um_toxeus_21` | **`RevenantPoison.msh`** | grean |
| 🟢 DEVOURER `um_bloodtoxeus_99` | **`RevenantPoison.msh`** (inherited) | crimson |
| 🟢 ENSLAVER `um_toxeus_enslaver_99` | **`RevenantPoison.msh`** (inherited) | charcoal |

**A TQ `.msh` file can carry an embedded entity-attachment script.** Read straight out of the shipped
`Creatures.arc` bytes, every Revenant mesh ends with:

```
CreateEntity
{
    attach = "Waist"
    entity = "Records\Effects\MonsterFX\Buffs\Revenant<Element>_FX.dbr"
}
```

`RevenantPoison.msh` therefore spawns a permanent particle effect on **every creature that wears it**.
The `EffectEntity` it names is **ABSENT from the mod arz** and resolves from the **base-game
database.arz**:

```
records\effects\monsterfx\buffs\revenantpoison_fx.dbr
    Class       = EffectEntity
    effectFile  = Effects\MonsterFX\Buffs\RevenantPoison.pfx
    boneList    = Bone_R_Weapon ; Bone_L_Weapon
```

The **entire** roster corroborates it: every *other* `RevenantPoison.msh` wearer in the shipped DB
also wears `newskeleton_grean.tex` (`cm_revenanttainted_16`, `um_nefesiris_30`, `um_rotbone_14`,
`um_toxeus_21`) - vanilla deliberately pairs that mesh with the green skin. Our Toxeus records are the
**only** wearers given a crimson / charcoal skin: the skin override landed, the mesh-baked effect did
not, so a green cloud sat on a red/black body.

> **HONEST RESIDUAL (round 2, `BL-b92-DEBT-6`).** The mesh block says `attach = "Waist"` but the
> EffectEntity carries `boneList = Bone_R_Weapon;Bone_L_Weapon`. Which wins is **not resolvable from
> bytes alone** - the green is either a body-wide waist cloud or particles on the two weapon bones.
> **Root cause and fix are unaffected** (removing the mesh removes the effect either way), but round
> 1's story that the Enslaver's marauders "look green because they are fighting inside the boss's
> cloud" is **NOT supported** and has been withdrawn. The marauders
> (`um_enslaver_marauder_99`, `enslaver_marauder_1..3`) wear
> `Creatures\Monster\ShadowStalker\ShadowStalker.msh`, whose own `CreateEntity` attaches
> `ShadowStalker_Smoke` (audited: not green) plus the Will-confirmed black `drxshadowcloak` shroud.
> If Will still sees green on the marauders after this build, that is a separate surface.

---

## 3. COLOUR PROVEN FROM THE ASSET BYTES, NOT THE NAME

Standing law (born from `343_dark_smoke`, which is NAMED dark and RENDERS green).

All four `Revenant*.pfx` are structurally identical - same two emitters (`Dark Clouds` /
`New Dark Clouds`), same textures (`Effects\Textures\Organism01.tex` + `Organism02.tex`), same
shaders (`ParticleCombine.ssh` / `ParticleAdditive.ssh`). Poison and Storm are the same byte length
(2061 B) and **differ in only 140 bytes**, which resolve into groups of four consecutive floats whose
exponent byte is identical across the files - i.e. colour keyframe tracks.

Round 2 re-derived these **independently** (own reader, offsets derived from the poison/storm byte
diff rather than hard-coded). Reading the *same* offsets in the sibling files is what validates the
channel assignment - frost must come out ice-blue and storm blue-violet, and they do:

| variant | R | G | B | renders |
|---|---|---|---|---|
| `RevenantFrost` | 0.534 / 0.520 | 0.824 / 0.844 | **0.9999 / 1.000** | ice blue ✔ |
| `RevenantStorm` (control) | 0.592 / 0.604 | **0.501 / 0.513** (lowest) | 0.695 / 0.722 | blue-violet ✔ |
| **`RevenantPoison`** | 0.534 / 0.520 | **1.000 / 0.974** | 0.591 / 0.637 | **GREEN `#88FF96`** ✔ |
| `RevenantFire01` | **1.000** | 0.518 | 0.007 | orange `#FF8401` ✔ |

`RevenantPoison` peaks the **green** channel at 1.0. **Three independent decoders** - the round-1
implementer, the vet, and this round (own ARZ/ARC/PFX readers, zero repo imports) - agree to three
decimals on every variant. **PROVEN-from-bytes.**

**Round 2 also closed the FIRE anchor**, which round 1 left open. `RevenantFire01.pfx` is a
different length (2005 B; emitter-1 float payload 473 vs 487) because it stores **one** keyframe
per channel where the others store two, so it does not line up on the same indices. Located by the
same structural signature rather than a hard-coded offset, its R/G/B sit at emitter-1 float indices
**41 / 50 / 59** (stride +9) and read **R 1.000 / G 0.518 / B 0.007 = `#FF8401`** - orange, R
dominant, B ~0, exactly as the name and its `newskeleton_crimson` skin predict, and matching the
vet's independently-decoded `#FF8401` to three decimals. **All four anchors now reproduce.**

The keyframe layout is understood rather than guessed: each channel is a block of
`[t0, value0, t1, value1]`, and for Poison/Storm/Frost the three blocks sit at emitter-1 float
indices **43 / 56 / 67**.

**Independent DB-side corroboration of the whole name->colour mapping** (no .pfx decode involved):
vanilla pairs each Revenant mesh with a matching-coloured skin - poison -> `newskeleton_grean.tex`,
frost -> `newskeleton_blue.tex`, storm -> `newskeleton_purple.tex`, fire -> `newskeleton_crimson.tex`.
Our Toxeus records are the only `RevenantPoison.msh` wearers given a crimson/charcoal skin: the skin
override landed, the mesh-baked FX did not, so a green cloud sat on a red/black body.

---

## 4. WHY THE FOUR PRIOR ROUNDS ALL FAILED

**Every prior fix operated on the database. The attachment is inside the MESH FILE.** No `.arz` scan
of any depth - fields, chain, or transitive skill closure - can see a `CreateEntity` block compiled
into a `.msh`.

- **b55** recoloured DB *emission fields* on 9 pets. Never touched `mesh`.
- **b71** walked the item->skill->icon->spawnObjects->pets chain and correctly proved it byte-identical.
  `mesh` was identical too - because it was uniformly *wrong*, so a drift-detector could never flag it.
- **b75** decoded `343_dark_smoke.pfx`, found it renders green, and swapped the Enslaver's
  `charFxPakRunningNames` to the proven-black `drxshadowcloak`. That was a **real fix to a real second
  surface** - it just was not this one. Two things prove it could never have worked: (a) the
  **Devourer has no `charFxPakRunningNames` at all**, so a shroud swap cannot explain his green;
  (b) b75 **even opened `RevenantPoison.msh`**, read its texture strings (`NewSkeleton_White.tex` +
  a bump map) and explicitly cleared it as "innocent" - it stopped at the texture strings and never
  read the trailing entity script one field further out.
- **b81** fixed pet identity/race - orthogonal.

**THE LESSON, now a standing rule:** a `.msh` can carry its own FX attachment, so **"the DB is clean"
never proves a visual is clean.** Registered as `BL-b92-DEBT-7`: nothing in the build audits meshes
for `CreateEntity`; b92 read them by hand and its `AURA_MESHES` / `NO_EFFECT_MESHES` tables are the
seed for a real gate.

---

## 5. THE FIX - `Creatures\Monster\Skeleton\GoldenSkeleton01.msh`, 15 records

Round 1 chose `Skeleton01.msh`. The vet proved that choice unsound for LIVE creatures and it was
**abandoned**. Round 2 re-derived every candidate from the bytes:

| candidate | embedded `CreateEntity` | rig vs RevenantPoison (bone-name set) | live-creature precedent | verdict |
|---|---|---|---|---|
| `RevenantPoison` (today) | **yes - GREEN** | - | - | **the bug** |
| `RevenantStorm` | yes - blue-violet (not green) | **identical 24/24** | the control wears it | legal but adds a purple cloud to bosses ruled BLACK/crimson - **rejected on art, not safety** |
| `RevenantFire` / `RevenantFrost` | yes - orange / ice-blue | identical 24/24 | yes | wrong colour - rejected |
| `SkeletonSpirit01` | **no** | identical 24/24 | 5 wearers | *StandardBlendedGlowSkinned* would add a glow - rejected |
| `Skeleton01` (round 1's pick) | **no** | superset: all 24 **+8** finger/thumb/toe bones (32 unique / 92 refs vs 24 / 77); +6.4 KB | **203 of 205 mod wearers and 278 of 279 base wearers are `Class=Proxy`**; the sole live precedent is `z_nate.dbr`, an unreferenced zzdev dummy | **rejected - a proxy placeholder mesh** |
| ✅ **`GoldenSkeleton01`** | **no** | **identical 24/24, zero missing, zero extra** (76 `Bone_` refs vs 77 - that 1 delta IS the removed attach node); 362 B smaller than RevenantPoison (= the CreateEntity block + a texture-name delta) | **285 Monster + 22 Pet + 1 PetNonScaling + 121 Proxy** in the mod DB (332 Monster / 131 Proxy in base); **19 of those Pet-class wearers sit in `records\skills\soulskills\pets\`** - our exact class, folder and role, and the 121 Proxy wearers already cover our 4 proxy targets | ✅ **chosen** |

Additional reasons, all from bytes:

* **Canonical for `anm_skeleton01`**, the animation table all 15 targets use: **307** records in the
  mod DB and **299** in the base DB pair `GoldenSkeleton01.msh` with `anm_skeleton01` - far ahead of
  every other mesh. (`Skeleton01.msh`: **one**, the dev dummy. `RevenantPoison`: 26.)
* **Same shader** `Shaders\StandardSkinned.ssh` and **same bump** `GoldenSkeleton01BMP.tex` as
  RevenantPoison. Its default diffuse is `GoldenSkeleton01.tex` instead of `NewSkeleton_White.tex`,
  which **never renders** here: all 15 targets set `baseTexture` explicitly (crimson / charcoal /
  `proxyu_boss`).
* It satisfies **this repo's own pet rig contract** (`validate_summon_pets._collect_mesh_anim_families`,
  which requires a real Monster to have proven the mesh+anim family) with **285 proving Monsters**
  rather than one dev dummy.

Each boss's deliberate identity survives intact: the Devourer keeps crimson + `svc_black_poison`
(R-7), the Enslaver keeps charcoal + the Will-confirmed BLACK `drxshadowcloak` smoke (R-10).

### ⚠️ WILL-DECISION, surfaced rather than assumed

`apply_svc_patches.py` records Will's directive #2 for the Devourer as **"the GREEN Athens Toxeus,
but RED"**, with a note that the clone's `revenantstorm` was overridden "back to the Athens mesh".
This fix **moves him off that exact mesh**. That is unavoidable: the Athens mesh IS the green.
GoldenSkeleton01 keeps the identical rig, the same skeleton silhouette family and the crimson skin,
so he still reads as the Athens boss in red - but Will's real options are exactly three:

1. **(shipped)** no aura at all - `GoldenSkeleton01.msh`;
2. keep the literal Athens mesh and **accept the green**;
3. keep an aura but change its colour - `RevenantStorm.msh` (blue-violet), rig-identical.

That comment block is also **corrected**: it claims `revenantstorm.msh` is "a DIFFERENT rig from the
Athens boss". It is not - all four Revenant meshes **and** GoldenSkeleton01 share one 24-bone set.

### Scope - exactly 15 records (12 briefed + the 3 EoAT clones)

Devourer: `um_bloodtoxeus_99`, pets `bloodtoxeus_1..3`, proxies `q_bloodtoxeus_lone`,
`q_bloodtoxeus_ambush`.
Enslaver: `um_toxeus_enslaver_99`, pets `toxeus_enslaver_1..3`, proxies `q_enslaver_warband`,
`q_yard_enslaver`.
**End of All Things: pets `toxeus_eoat_1..3`.** Round 1 deferred these to another lane as debt.
Round 2 fixes them here: they are direct clones of the Devourer's pets, carry the identical inherited
green, and R-8 rules their body "ash-pale" - so green is wrong there too. It is the same one-field
operation on identical records, and shipping a third green Toxeus would be exactly the
"triaged into follow-up = NOT done" failure. **The EoAT ash-pale SKIN stays that lane's item**
(`BL-b92-DEBT-1`, narrowed to P2).

**NOT TOUCHED, deliberately:** `um_toxeus_21` (Greece, green by Will's design - `verify()` asserts he
still wears RevenantPoison), `um_toxeus_99` (the control - `verify()` asserts RevenantStorm), and
every vanilla RevenantPoison wearer (mummy guardians, `cm_revenanttainted_16`, `um_nefesiris_30`,
`um_rotbone_14`).

### Owner: registry module `tools/patches/toxeus_mesh_aura.py`

Registered after `toxeus_endofallthings` / `toxeus_souls_100`, before `visuals`, so it is the
ratified **final writer of `mesh`** on these records and the EoAT pets exist to be fixed. `apply()`
refuses to run unless all 15 targets are on `RevenantPoison` beforehand, and proves its own blast
radius by snapshotting `mesh` across every record in the DB before and after.

### Rulings checked (`docs/WILL_RULINGS.md`) - none regressed

R-5/R-6 (kits), R-7 (black poison - **reinforced**: the green that fought it is gone), R-10 (Enslaver
black shroud - untouched, `charFxPakRunningNames` not modified), R-11/R-12 (skeleton identity - the
mesh stays in the same skeleton family on the same anim table), R-3/R-49 (chest spawn - proxies keep
pool/limit/chance, only `mesh` moves), R-48 (100% soul drop - untouched), R-8 (EoAT - mesh fixed,
ash-pale skin left to that lane). New ruling recorded as **R-80** (see section 9 - round 1 filed it
as R-50, then as R-19; both collided, so it took the new Toxeus overflow decade 80-89).

---

## 6. THE GATE (four recurrences = a machine check, not another report)

`toxeus_mesh_aura.verify()` runs in registry step 4 over the FINAL merged db and fails the build
loud. Round 2 **narrowed** it, per the vet: it now encodes the **bug**, not an art policy.

It FAILS if:
- any of the 15 targets wears a mesh whose embedded `CreateEntity` spawns a **GREEN** effect;
- any target wears a mesh that has **never been byte-audited** (an unknown mesh may carry its own
  effect, so it must be read before it ships);
- `um_toxeus_21` leaves `RevenantPoison` (Will's intentional green) or `um_toxeus_99` leaves
  `RevenantStorm` (the control).

It **PASSES with a printed NOTE** if a target wears an audited **non-green** effect mesh
(Storm / Fire / Frost). Round 1's gate would have rejected those, which hard-coded an unratified
"no aura of any colour" policy as build law. Choosing boss art is Will's call, not the gate's.

**Negative test: `tools/test_toxeus_mesh_aura.py` - a COMMITTED file, 23/23 legs.** (Round 1 cited a
scratchpad script that did not exist in the tree; the vet could not reproduce it.) It drives the real
`verify()` over a shim on a real `.arz`:

| leg | expected | got |
|---|---|---|
| fixed scratch state | PASS | PASS |
| ⭐ **the pre-fix arz `1c27d5fa` as-is (15/15 targets still green)** | **FAIL** | **FAIL** |
| replant the green mesh on each of the 15 targets | FAIL x15 | FAIL x15 |
| unaudited mesh (`SkeletonRumorBoss`) on either boss | FAIL x2 | FAIL x2 |
| audited NON-green mesh (`RevenantStorm`, `SkeletonSpirit01`) | PASS x2 | PASS x2 |
| move either PROTECTED record off its ruled mesh | FAIL x2 | FAIL x2 |

The second leg is the important one: **the gate reproduces and rejects exactly the state Will filed
the bug against.** The leg's expectation is derived from the baseline's own bytes, so the test stays
meaningful whichever `.arz` it is pointed at:

```
py tools/test_toxeus_mesh_aura.py                       # pinned pre-fix arz -> 23/23, leg 2 FAILs
py tools/test_toxeus_mesh_aura.py --arz <deployed>      # post-fix arz       -> 23/23, leg 2 PASSes
```

---

## 7. VERIFICATION

- Full coupled build **EXIT 0** under `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1`. All in-build gates +
  **27/27 registry verify hooks** green (incl. `toxeus_mesh_aura`). A7 Occult/Hunting golden freeze
  **PASS** (84 waived DB / 90 waived text, 0 other). Unlock-alignment **PASS**. Contracts
  **GATE: PASS**, 0 P0 / 0 P1.
- **DETERMINISM: two independent full builds are byte-identical**, md5
  `3f92d8681157b2069e778fb3bfd5d366` (55,424,209 B).
- **RECORD-DIFF vs a `main`-only build of the same tree** (`7f8d04dfd0e8eecc4bb590a60d4a02c3`,
  built from a throwaway `770bc35` worktree so b92 is the *only* variable):
  **0 ADDED, 0 REMOVED, 15 MODIFIED, 1 field each, every one
  `mesh: RevenantPoison.msh -> GoldenSkeleton01.msh`. Zero collateral.** No soul / skill / loot /
  pool / map / quest / text record touched.
- **Text.arc rebuilt** to `fcca49277b9d31ed451e4a6843898843`; `toxeus_mesh_aura` adds **0 tags**, so
  the arz/Text coupling is satisfied trivially (no new, renamed or orphaned tag).
- Module `apply()` reported `modified 15 record(s), 0 tag(s)`; registry collision report shows the
  expected later-wins overlaps on the Toxeus records only.

---

## 8. DEPLOYED (DEV) - and a cross-lane hazard that changed how

**The DEV folder was occupied by another lane.** At 15:07 today a parallel lane deployed its own
integration build to `CustomMaps/SoulvizierClassicDEV`. Measured against a `main`-only build, that
artifact (`0d861748df91442ab860995cdea243eb`) carries **13 records and 28 field edits that are not on
`main`** - Leinth skills, `genericboss05` chests, uber-orb apex loot tables, and edits to
`um_sarkoth_99` / `um_vashkarr_99` / `um_neferkha_99` / `um_voranthys_99` / `um_broodmother_99`.

Copying this lane's own build over it would have **silently deleted another agent's live work**;
doing nothing would have left Will with no way to check the green. So b92 deployed
**non-destructively**: `tools/patch_deployed_arz.py` (new, committed) loads the artifact that is
actually deployed, runs `toxeus_mesh_aura`'s **own** `apply()` + `verify()` against it - so the
module's preconditions, blast-radius proof and gate all still run - prints the record-diff, and only
then writes atomically with a backup. Result = "exactly what was deployed, plus these 15 fields",
which is what a merge of the two lanes would have produced.

| artifact | md5 | state |
|---|---|---|
| `SoulvizierClassicDEV.arz` | `f3015aa3c3a75f6c14275f1ff0b602ac` | **NEW** - the other lane's `0d861748` **+ b92's 15 mesh fields, nothing else** |
| `Text.arc` | `ed31ec8407e59710d4ad28d5532e75ae` | ✅ **UNTOUCHED** (the other lane's; b92 adds 0 tags so the pair stays coherent) |
| `Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | ✅ **UNTOUCHED** - matches the required hash, verified before AND after |
| `Quests.arc` | `35bfe3f39e8480408e3c22ea5473f796` | ✅ **UNTOUCHED** - verified before AND after. ⚠️ **NOTE:** this already differed from the brief's expected `5e664c7b190965fd69f6ff15d77d85e4` **before b92 touched anything** - the other lane replaced it at 15:07. b92 did not change it. |

Proof of the sibling files: hashed immediately before and immediately after the write, identical.
The deployed file was re-read from disk afterwards and **passes the b92 gate (23/23)**.

Rollback: `local/DEV_arz_deployed_prev_b92r2.arz` (= `0d861748`, the exact pre-patch file).
Pre-fix ground truth pinned at `local/b92_ground_truth_1c27d5fa.arz`.

> ⚠️ **The canonical artifact is the branch build** (`3f92d868...`), fully reproducible from
> `fix/green-diff`. The deployed file is a reconciliation of two lanes and is **not** reproducible
> from any single branch. Whoever integrates should merge `fix/green-diff` and rebuild normally.
> If the other lane redeploys, b92's 15 fields go with it - re-run
> `py tools/patch_deployed_arz.py --module toxeus_mesh_aura --arz <deployed> --apply`, or just merge.

## 8b. ROUND-2 REMEDY RE-DERIVATION (the part the vet never saw)

The vet's NO-GO was on the REMEDY, not the diagnosis, and it landed while round 1 still proposed
`Skeleton01.msh`. The pick has since moved to `GoldenSkeleton01.msh`, so **that choice had never been
independently checked by anyone**. It has now been re-derived from the shipped bytes with a fresh
reader set (own ARZ / ARC / MSH / PFX decoders, zero repo imports). Result: the choice holds, and
**two of its supporting numbers were wrong and are corrected**.

| claim as round 2 wrote it | re-derived | verdict |
|---|---|---|
| GoldenSkeleton01 has no `CreateEntity` | confirmed - and all four `Revenant*.msh` DO have one, while `Skeleton01` / `SkeletonSpirit01` / `ShadowStalker` do not | ✅ |
| "identical **25**-bone rig" | **24**, not 25 | ❌ **corrected everywhere** |
| "zero missing, zero extra" vs RevenantPoison | confirmed - identical 24-name set | ✅ |
| canonical for `anm_skeleton01`: 307 mod / 299 base vs Skeleton01's 1 | confirmed exactly | ✅ |
| 285 Monster + 22 Pet + 1 PetNonScaling wearers (332 Monster base) | confirmed exactly | ✅ |
| Skeleton01 is a proxy mesh: 203/205 mod, 278/279 base `Class=Proxy` | confirmed exactly | ✅ |
| "**22** of those Pets are soul pets in `soulskills\pets\`" | **19** | ❌ **corrected everywhere** |
| same `StandardSkinned.ssh` + `GoldenSkeleton01BMP.tex` | confirmed | ✅ |

> ⚠️ **METHOD NOTE, and the reason the bone count was wrong.** Bone names must be extracted with a
> regex over the RAW mesh bytes (`Bone_[A-Za-z0-9_]+`). A printable-string-run scan - the obvious
> approach, and what produced the "25" - silently drops `Bone_Neck01` from GoldenSkeleton01,
> RevenantStorm, RevenantFrost and SkeletonSpirit01 because the name is not run-initial in those
> files, fabricating a phantom one-bone delta. The raw substring `bone_neck01` occurs **3x in every
> one of these meshes**. Heuristic-free counts: RevenantPoison **77** `Bone_` refs / **24** unique;
> GoldenSkeleton01 **76 / 24** (that single missing ref IS the removed `CreateEntity` attach node's
> `parent = "Bone_Waist"`); RevenantStorm **77 / 24**; **Skeleton01 92 / 32** - 8 extra
> finger/thumb/toe bones. This reproduces the vet's own 92-vs-77 `Bone_` and 5-vs-8 `Waist` counts
> exactly, which cross-validates both readers.

**A new fact in GoldenSkeleton01's favour that round 2 had missed:** it already has **121
`Class=Proxy` wearers** in the mod DB (131 in base). So it is not a creature-only mesh being forced
onto our 4 proxies - it is the mesh *both* roles already use, which is why all 15 records can share
one value instead of splitting the fix across two meshes.

**Independently re-verified on the DEPLOYED artifact** (`f3015aa3`, read with the fresh reader, not
the build tooling): 15/15 targets on `GoldenSkeleton01.msh`; `um_toxeus_21` still `revenantpoison.msh`
and `um_toxeus_99` still `revenantstorm.msh`; and the diff against its own pre-patch backup
(`0d861748`) is **exactly 15 field deltas, every one `mesh`, 0 records added, 0 removed**.

---

## 9. ROUND-1 CLAIMS THAT DID NOT REPRODUCE (corrected here)

The vet re-derived round 1 independently and upheld the roster, the diff, the colour, the
no-collateral proof and the gate. These are the claims that were **false against the bytes** and are
now corrected:

| round-1 claim | reality (re-derived in round 2) |
|---|---|
| `Skeleton01.msh` is "the canonical mesh for `anm_skeleton01`" | **False.** Exactly ONE record in the mod DB and one in the base DB pair them, and it is `zzdev\z_nate.dbr`, an unreferenced dev dummy. The canonical mesh is `GoldenSkeleton01.msh` (307 mod / 299 base). |
| "721 shipped records already wear it, many with a charcoal skin override" | **False.** 205 in the mod DB, 279 in base, and **zero** carry a charcoal skin override in either. |
| "closest geometry (94.8% byte-identical body)" | **Meaningless as a discriminator.** Sequence similarity is ~1.0 for every pair in this family. The real measure is the rig, and `Skeleton01`'s differs (+8 bones, +6.4 KB); `GoldenSkeleton01`'s is identical. |
| `RevenantStorm` dismissed in one table row as "coloured aura - yes" | It is **rig-identical and NOT green** (green is its lowest channel) and it is what the control wears. It was never evaluated on merit. Round 2 evaluates it, keeps it **legal under the gate**, and rejects it only on art (a purple cloud on bosses ruled black/crimson). |
| the marauders look green because they fight "inside the boss's Waist-attached cloud" | **Unsupported** - see the residual in section 2b. Withdrawn. |
| the ruling filed as **R-50** | **ID collision** with the 2026-07-16 Process meta-ruling R-50. Round 1 refiled it as **R-19** believing "R-18 was the max" - a stale read: the b84 backfill (now on main) had already taken R-14..R-19, and **R-19 is the parchment-retirement ruling**, so that was a SECOND collision. Now **R-80**, in the newly-allocated Toxeus overflow decade **80-89** (same precedent the b84 pass set for Souls with 70-79). Round 1 also edited the existing R-10 in an append-only file; that edit is **reverted** and the cross-reference moved into R-80. |
| negative test "`scratchpad/negtest_b92.py` (17/17)" | **Did not exist in the tree.** Replaced by the committed `tools/test_toxeus_mesh_aura.py` (23/23). |
| deployed to DEV **before** independent vet | Process inversion, acknowledged. Round 2 kept the pre-fix ground truth pinned in `local/` first, and deployed non-destructively (section 8). |

## 10. WILL TEST INSTRUCTIONS

Kill TQ **and** Steam, restart both (standing rule - the running game holds mod files in memory),
then load **SoulvizierClassicDEV**:

1. **Devourer of Blood** - blood cave, beside his hidden chest. Expect a **crimson skeleton with no
   green cloud**.
2. **Enslaver of Souls** - expect a **charcoal/black skeleton** wearing the same black smoke his
   Enslaved Shadow Marauders wear, **no green**.
3. **Both soul summons** - DISMISS any currently-summoned pack and **RE-SUMMON** (a live pet keeps
   its old appearance). Same for the **End of All Things** summon if you have the ring.
4. Please confirm the two that must NOT change: the **Greece** Toxeus the Murderer is **still green**
   (intentional), and the **secret-passage** Toxeus is untouched.
5. If the **marauders** still read green, say so - that is a separate surface and we have a clean
   differential method to run at it now (section 2b).
6. **One art call for you** (section 5): the Devourer is now on a rig-identical, aura-free skeleton
   rather than the literal Athens mesh, because the Athens mesh *is* the green. Happy with that, or
   do you want an aura back in a different colour?

## 11. REGISTERED DEBT

See `docs/BACKLOG.md` -> `BL-b92-DEBT-1..7`. Headlines: the EoAT **ash-pale skin** is still crimson
(other lane); the Devourer soul pets still carry Lyia nature residue (2 of the 3 are functional, so a
balance call); the other `343_dark_smoke` users are still on the green-rendering pak; the
waist-vs-weapon-bone anchor question; and the systemic one - **nothing in the build audits `.msh`
files for embedded `CreateEntity`**, which is the whole reason this bug survived four rounds.
