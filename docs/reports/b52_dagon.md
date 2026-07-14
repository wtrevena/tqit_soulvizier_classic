# b52 DAGON RCA (read-only; no fixes applied)

**Boss:** `records\test\boss_dagon_66.dbr` (Class=Monster, monsterClassification=Boss,
Monster.tpl, charLevel 50/65/80, mesh `Creatures\Monster\Ichthian\IchthianMage01.msh`).
Added as a rare champion (weight 2) to every ichthian spawn pool by
`_add_dagon_to_ichthian_pools` (apply_svc_patches.py:1447, called :16570); soul by
`_create_dagon_soul` (:2427, called :16579). Will hit it on the Megara Coast: name rendered as
the raw tag `tagD2boss03`, it **stood immobile** the whole fight, dropped **Dagon Soul**.

**Ground truth:** `scratchpad/baseline_build38.arz` (md5 `fcd5dcab…`, 51,007 records), base
game `database.arz` + `Text\Text_EN.arc`, `upstream/soulvizier_098i/Database/database.arz` +
`Resources/Text_EN.arc`, `work/SoulvizierClassic/Resources/Text.arc` (modstrings.txt). All
probes read-only. Worktree `.claude/worktrees/b52-dagon` @ `d11d3c0`.

---

## Headline verdict

Three independent defects, all confirmed. **None is a regression we introduced** — Dagon is an
unfinished cut-content SV test boss (`boss_dagon_66`) that was promoted into live spawn pools
*without the finishing pass its twin Cold Worm received*. Cold Worm (`boss_coldworm50`, the
identical class of SV `records\test\` boss) got a stat-boost pass **and** a monster name; Dagon
got only "add to pools" + a soul. The map-side promotion + soul are correct; the monster record
itself was never made shippable.

| # | Defect | Root cause | Ours? |
|---|--------|-----------|-------|
| A | Name renders as raw `tagD2Boss033` | The monster name tag is defined **nowhere** (not mod, not base, not upstream). Cold Worm's identical case was fixed (`tagD2Boss004='Cold Worm'`); Dagon's was never added. | Omission (never authored) |
| B | Cannot move / immobile | His offensive kit is almost entirely **dead references** (`d2custom\dagon_*` skills never ported into the AE-merged DB). Only a mis-fit melee bite + passives resolve → the caster AI has no usable attack to drive engagement → it stands. | No — inherited broken from SV 0.98i upstream |
| C | The tag gate (`validate_tags`) stayed green | The gate only checks **mod-owned** tags; it assumes every other referenced tag "resolves from the base game" and never verifies that. `tagD2Boss033` resolves from nothing. | Gate blind spot |

---

## (A) NAME — resolves to the raw placeholder `tagD2Boss033`

**Mechanism (proven):** the monster's `description` field = `tagD2Boss033`. In-game the display
name is that tag's string; if the tag is undefined in every loaded Text source, TQ prints the raw
key (Will saw `tagD2boss03`, the on-screen truncation of `tagD2Boss033`).

**Tag resolution across all three Text sources (probe `dagon_text.py`):**

| Source | `tagD2Boss033` (Dagon) | `tagD2Boss004` (Cold Worm) |
|--------|------------------------|-----------------------------|
| MOD `work/…/Text.arc` (modstrings.txt) | **ABSENT** | `Cold Worm` |
| UPSTREAM SV 0.98i `Text_EN.arc` | **ABSENT** | ABSENT |
| BASE game `Text_EN.arc` | **ABSENT** | ABSENT |

So `tagD2Boss033` is defined **nowhere** — it is a never-named cut-content placeholder, *not* a
base tag the b38 language de-clobber dropped. (The de-clobber, `build_text_arc.py:291`, only drops
an SV tag when the **base game defines the identical key+value**; base has no `tagD2Boss033`, so
the de-clobber never touched it. It is not implicated.)

**Why Cold Worm is fine and Dagon is not** — `apply_svc_patches.py:16372`:
```python
# Monster name tag (Cold Worm's description tag was undefined)
tags['tagD2Boss004'] = 'Cold Worm'
```
Whoever finished Cold Worm knew these test-boss `description` tags are undefined and authored the
name into the mod text pipeline. The identical line for Dagon (`tags['tagD2Boss033'] = …`) was
never added. Dagon's SOUL was named (`tags['tagSVCSoulDagon']`, :16368) — the monster was not.

**Minor secondary:** `tagSVCSoulDagon` is defined twice with different values — `'{^F}Dagon Soul'`
(:8095, in a dict) and `'{^F}Soul of Dagon'` (:16368). First-wins picks one; harmless but worth
reconciling.

---

## (B) MOVEMENT — immobile because the offensive kit is dead references

**It is NOT a movement/speed/mesh problem.** Empirically:
- `characterRunSpeed = 1.1` (higher than the mobile shaman's 0.8), `walkSpeed`/rotation inherited.
- `handHitDamageMin/Max = 200/250` — a working natural melee attack exists.
- mesh `IchthianMage01.msh` is a real, animated ichthian rig used by 44 records including mobile
  champions/heroes (`elder_greece_as_shaman_12`, `um_vidja_43`, …).
- Behavior/AI field diff vs the mobile same-mesh shaman (`behavior_diff.py`): **no**
  stationary/leash/tether/wander/pursuit field differs — both inherit identical Monster.tpl AI
  defaults. The only real differences are stat values (Boss vs Champion) and the skill kit.

**The skill kit is the cause (probe `dagon_probe2.py`):**

| slot | skill | resolves in DB? |
|------|-------|-----------------|
| skillName1 / specialAttackSkillName (30%) | `d2custom\dagon_shadowstar_single` | **DEAD** |
| skillName2 / specialAttack3 (5%) | `d2custom\dagon_summonwater` | **DEAD** |
| skillName3 / specialAttack2 (10%) | `d2custom\dagon_tidalwave` | **DEAD** |
| skillName5 / specialAttack5 (30%) | `d2custom\dagon_mudstorm` | **DEAD** |
| skillName6 | `xpack…\pcloudpet_petskill_pcloud` | **DEAD** |
| skillName4 / specialAttack4 (45%) | `boss skills\hydra_superbite` | resolves (Skill_AttackWeapon, **melee**) |
| skillName10-12 | `D2GlobalProperties_Normal01/Epic_Boss/Legendary_Boss` | **DEAD** (no difficulty scaling) |
| skillName13 | `armor_passive` | resolves (Skill_Passive) |
| skillName14 | `D2Boss_ConversionImmunity` | **DEAD** |

His **primary** attack (`specialAttackSkillName` = shadowstar) is dead and **75% of the
special-attack chance budget** (shadowstar 30 + tidalwave 10 + summonwater 5 + mudstorm 30) points
at skills that do not exist. The `d2custom\dagon_*` and `D2GlobalProperties*` records are
D2/Diablo-namespace content that **SV 0.98i referenced but never shipped** — they are dead in the
upstream SV database too, and the SVAERA/AE merge never carried them.

**Why he stands still:** IchthianMage-rig creatures are *casters* — their engagement loop is
"acquire target → move to cast range → cast a projectile/AoE spell." Dagon's every castable
ranged skill is a dead reference, so the caster AI has nothing to cast and never completes the
engagement loop; his one working attack (`hydra_superbite`) is a melee bite wired as a low
secondary special on a caster rig (and he has `characterOffensiveAbility = 0`, i.e. never
finished). The mobile same-mesh shaman is the control: identical rig, but it owns **two resolving
projectile attacks** (`squall` = Skill_AttackProjectileAreaEffect, `ichthian_tidalorb` =
Skill_AttackProjectileBurst) and moves/casts normally. (The exact engine failure — AI-controller
init aborting on the dead primary skill vs. churning on failed casts — cannot be pinned without a
runtime probe, which is out of scope; the root cause and fix are identical either way.)

**We did not break it (proven):** upstream-vs-build38 field diff (`dagon_probe2.py` §2) shows the
monster record is byte-equivalent except cosmetic path-casing (`Records\Skills\…Hydra_SuperBite`
→ `records\skills\…hydra_superbite`) applied to all records by the merge. `skill_quality.py`
touches only the SOUL item (`tagSVCSoulDagon` → Tidal Strike proc, WILL intent), never the
monster. There is no `_boost_dagon_stats`. Git: the monster entered via `fef8870` "Add Dagon to
all 23 ichthian spawn pools…" — a pools-only change.

---

## (C) GATE — why `validate_tags` did not flag the unresolved monster name

`validate_tags.py` **does** collect the ref (`description ∈ TAG_FIELDS`, so it sees
`boss_dagon_66.description = tagD2Boss033`). It then discards it:

1. Line 245: `refs = {t: r for t, r in all_refs.items() if is_mod_owned(t)}` — only **mod-owned**
   tags are kept for the "must exist in Text.arc" check.
2. `is_mod_owned(tagD2Boss033)` = **False**: it is not in the `mod_authored_tags.txt` manifest
   (we never authored it) and does not match `MOD_TAG_PREFIXES` (which lists the EXACT
   `tagD2Boss004` but not `033`).
3. So it is dropped and never validated.

**The blind spot is the documented assumption itself** (`validate_tags.py:88-102`):
> `tagD2Boss004 … EXACT, not the tagD2Boss* prefix: the .arz also references base-game
> tagD2Boss033 (records\test\boss_dagon_66.dbr) which resolves from the base game and is absent
> from the mod Text.arc`

That comment is **factually wrong** — `tagD2Boss033` is absent from base `Text_EN.arc` too (table
in §A). The gate treats every non-mod-owned tag as "the base game will resolve it" and has **no
cross-check against base `Text_EN.arc`**, so a name tag that resolves in *neither* mod nor base
passes green. Any monster the mod promotes into spawn pools (Dagon, and structurally any future
`records\test\` boss) whose `description` is an undefined placeholder is invisible to the gate.

---

## FIX PLAN (for the implement wave — not applied here)

Registry contract + crash laws (no `clone_record`; no explicit dtype on cloned records; no
Pet.tpl equip copy; no FX fields on the monster record — only point `skillNameN` at existing skill
DBRs that carry their own FX) all hold for the plan below.

**A — name the monster.** In `apply_svc_patches.py`, beside line 16373, add
`tags['tagD2Boss033'] = '<Dagon name>'`. amgoz1 bar: a deep-sea / ichthian-lord identity to match
`_create_dagon_soul`'s "deep sea poison lord" (e.g. *"Dagon, Lord of the Deep"* / *"Dagon the
Tide-Drowned"* — final wording via the content brief). Add `tagD2Boss033` to the mod manifest so
it emits into modstrings.txt and the tag pipeline resolves it; verify with `validate_tags`.

**B — restore a functional, crash-safe kit** (honoring the WILL_DECISIONS "Dagon Tidal Strike"
intent, which today lives only on the soul). Repoint the dead `d2custom\dagon_*` slots at existing
resolving ichthian caster skills so his primary/special attacks work and the AI engages. Verified
present in build38:
- `records\skills\monster skills\attack_radius\ichthian_tidalstrike.dbr` (Skill_AttackProjectileAreaEffect) — his signature **Tidal Strike** [WILL]
- `records\skills\monster skills\attack_projectile\ichthian_tidalorb.dbr` (Skill_AttackProjectileBurst) — thematic water orb
- `records\skills\monster skills\attack_radius\squall.dbr` (Skill_AttackProjectileAreaEffect) — storm AoE (the working-shaman precedent)
- keep `hydra_superbite` (works) as the melee finisher.

Make `specialAttackSkillName` (the primary) a resolving skill (Tidal Strike). Also repoint the
dead scaling passives (`D2GlobalProperties_*`, `D2Boss_ConversionImmunity`) at their AE
equivalents so his stats scale across N/E/L and he is CC-appropriate, and drop the dead
`pcloudpet` skill slot. Give him non-zero `characterOffensiveAbility` (he is currently 0) so his
attacks land — mirror the finishing pass Cold Worm got in `_boost_coldworm_stats`. Do **not**
rebalance beyond making him a functional boss; **do not touch the soul drop** (it works: 66%,
grants Tidal Strike). A `_boost_dagon_stats` helper analogous to `_boost_coldworm_stats` is the
natural home.

**C — close the gate blind spot.** In `validate_tags.py`, additionally require that every
**monster `description`** tag referenced by the .arz resolves in **the mod Text.arc OR the base
`Text_EN.arc`** (the build already loads base Text_EN for the de-clobber, so the data is on hand).
This catches any promoted/new monster whose name tag resolves nowhere. Correct the false comment
at lines 88-102 (Dagon's tag does **not** resolve from the base game).

---

## Probes (read-only, in session scratchpad)
`dagon_probe.py` (base-vs-build38 record diff), `dagon_probe2.py` (skill/mesh resolution +
upstream diff + Cold Worm control), `dagon_text.py` (tag resolution across 3 Text sources),
`ichthian_cmp2.py` (working-shaman comparison + mesh users), `skill_exists.py` (dead vs real skill
existence), `behavior_diff.py` (AI/movement field diff vs mobile shaman).
