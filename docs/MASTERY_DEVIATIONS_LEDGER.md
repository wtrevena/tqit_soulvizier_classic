# Mastery Deviations Ledger - Soulvizier Classic vs amgoz1 SV 0.98i core

> **Will's question (verbatim):** "describe all reassignments / deviations that we have
> made from the core masteries (what we changed and why across all masteries)."
>
> **Baseline / "core":** amgoz1's **Soulvizier 0.98i** (`upstream/soulvizier_098i/Database/database.arz`).
> **Target state:** the current build36 DB = `main @ 31a0bce` (Lane A pet/Rune-Golem + Lane B 18-skill
> SVAERA graft, both merged) **plus** the in-flight **fix wave** not yet on main:
> `feat/build36-fix-wave` = `182690e` (the **F1-F7** code, incl. the Flash Powder rework) **+** `5e2e30b`
> (gate-hardening on top). `feat/build36-content-wave` (real tip `5e6bfd6`) is a *superset* that merges
> `feat/build36-fix-wave` into two extra **C1-C7** content commits (`79de1d7` + `24a8ab8` = 4 uber
> bosses / Ereban relic / Dorus / uplift picks - boss/relic/loot content that touches **no** mastery
> record, verified). So all the mastery-relevant in-flight work (Flash Powder F5, Shadow Stalker D16b,
> the golden overrides) lives in `182690e` and is reachable from *both* branches.
> The built lane arz is `work/SoulvizierClassic/Database/SoulvizierClassic.arz`.
>
> **Method:** the mod is *generated*, not hand-authored - every deviation is a function in
> `tools/build_svc_database.py` / `tools/apply_svc_patches.py` run against the SV 0.98i arz at build
> time (three DLC upstream arzs + the base-game arz are also loaded for closure). So this ledger is
> compiled from (1) those build-script functions, (2) the git history that introduced each one, and
> (3) the two definitive audits `docs/MASTERY_AUDIT_2026-07-09.md` (the 11-agent scoring + boost plan
> Will approved) and `docs/SVAERA_MASTERY_COMPARISON.md` (the SVAERA-adoption proposal). Every claim
> below cites a record path + a commit so it is checkable.
>
> **Slot map (authoritative, from `records\xpack\creatures\pc\{male,female}pc01.dbr`):**
> 1 Warfare · 2 Defense · 3 Earth · 4 Storm · **5 Occult (FROZEN)** · **6 Hunting (FROZEN)** ·
> 7 Nature · 8 Spirit · 9 Quest-Reward (not a mastery) · 10 Dream · 11 RuneMaster (base DLC) ·
> 12 Neidan (base DLC). *(Note: UI panels 7/8 are swapped vs slots - Nature→panel 8, Spirit→panel 7 -
> matching SV 0.98i.)*

---

## 0) THE LAWS AND DESIGN RATIONALE (read first - they explain every choice below)

Four standing rules govern all mastery work; every per-tree entry honors them.

### L1 - NEVER REMOVE A SKILL OR TREE SLOT (`c344f94`, Will 2026-07-09, verbatim)
> "editing skills is probably preferred, but we can add new skills, i just dont want to arbitrarily
> delete things for cleanliness, i want to be very careful about preserving much of the original work
> and intent of the original devs."

Operational reading (from `docs/MASTERY_AUDIT_2026-07-09.md` header): (1) EDIT fields = preferred;
(2) ADD skills/slots = allowed; (3) REMOVE = **forbidden** without Will's per-item approval;
(4) re-enabling *disabled* original content is encouraged; (5) dangling-ref cleanup *inside* a record
is a field edit (allowed). **Consequence:** there are ZERO skill/slot removals anywhere in the mod.
Every "reworked" skill keeps its slot; every graft is appended at a new free slot.

### L2 - OCCULT + HUNTING ARE GOLDEN-FROZEN (`validate_mastery_golden.py`, gate A7, build29)
Occult (slot 5) and Hunting (slot 6) carry Will's manual hand-tuning and are **hard-excluded from all
systematic mastery work.** `tools/occult_hunting_golden.json` snapshots their complete observable
state (every UI record + panectrl override, every tree-slot skill record + one delegation hop, every
referenced Text tag with load-bearing definition order). Every build fail-loudly diffs against it;
**any** drift fails the build unless the exact drift key is listed in the golden's
`owner_approved_overrides` object with a justification - i.e. only after Will signs it off. This is the
mechanism that lets the other 9 trees be tuned freely while proving Occult/Hunting were never touched.

### L3 - PLAYER-SKILL ANIM CASTABILITY (hard-law #2 / `SkillManager::StartSkill` abort)
If a player skill's `skillSpecialAnimationName` names an animation token that is **not present in the
PC anim tables** (`records\creature\pc\anm\anm_malepc01.dbr` + `anm_femalepc.dbr`), the engine aborts
the cast. The SV→AE port both (a) grafted monster-only tokens onto player nukes and (b) dropped vanilla
weapon-rows from the PC tables - producing the six cast-abort / half-cast bugs fixed below. A
build-time gate (`validate_player_skill_anims.py`, the 4th DB invariant) now fails the build if any
castable tree skill names an unresolvable token.

### L4 - SVAERA = HYBRID-GRAFT, NEVER WHOLESALE (`docs/SVAERA_MASTERY_COMPARISON.md`, `11777ee`)
soa (SVAERA author) gave verbal permission to reuse his work (recorded `de1562a` / `docs/PERMISSIONS.md`).
**Wholesale adoption of SVAERA's trees was explicitly REJECTED** because on every *shared* skill our
Wave-1/Wave-2 work is equal-or-better, and swapping to SVAERA wholesale would actively regress us:
- it still ships the three cast-abort bugs we fixed (SVAERA's `drxmeteor` still carries `MeteorShower`,
  `drxthunderball` still `Ensnare`, Spirit Bonespire still `BoneSpire`);
- it would strand existing RuneMaster/Neidan characters (SVAERA re-paths those trees to `_drx_*` copies -
  swapping the tree pointer wipes invested points) - an L1 violation;
- it would delete our Spirit additions - an L1 violation.

So the adopted model is **additive HYBRID_GRAFT**: keep our tuned trees, and cherry-pick only SVAERA's
genuinely-*new* Atlantis/DRX player skills that our pre-Atlantis 0.98i back-port had dropped, appended
at fresh slots. That is exactly the build36 Lane B 18-skill graft + the Rune Golem (§ per-tree below).

---

## 1) CROSS-TREE MECHANICAL DEVIATIONS (apply to several/all trees; not tree-specific balance)

These four build-script passes touch many trees at once and are the substrate the per-tree balance
work sits on. They are deviations from the raw SV 0.98i *records* even though several are faithfulness
repairs.

| # | Pass (function) | What it changes | Why | Trees affected |
|---|---|---|---|---|
| C1 | `fix_broken_mastery_skills` (`build_svc_database.py`) | (a) Phase-1 sweeps **every** record and rewrites **every** case-mismatched `.dbr` reference in **any** field (not just `buffSkillName`/`petSkillName` - also sounds, FX, `propName`, `spawnObjects`, etc.) to the exact lowercase stored path; (b) Phase-2 copies display fields (`skillDisplayName`/`skillBaseDescription`/`skillUpBitmapName`/`skillDownBitmapName`/`skillConnectionOff`) from the delegated buff/pet child onto the parent stub. | TQIT did case-insensitive lookups + inherited display through delegation; AE Custom-Quest mods are case-sensitive and read display from the record itself, so SV's stubs render blank/dead without this. Injected display **equals** SV's chain-resolved effective display (faithful). **This is why even the frozen Occult/Hunting trees have non-value byte deltas vs raw SV.** | ALL mod trees (incl. Occult/Hunting) |
| C2 | `fix_mastery_panel_buttons` | rebuilds each ingameui panel's contiguous button list + the xpack/xpack3 overrides from folder contents. | makes newly-added tree slots actually render as clickable panel buttons (no engine auto-discovery). Re-run after every graft. | ALL panels 1-8 + Dream |
| C3 | `add_dlc_mastery_trees` | explicitly wires the Ragnarok **RuneMaster** + Atlantis **Neidan** tree refs into the PC records. | SV 0.98i predates both DLCs; with the DLCs installed the engine injects those masteries into the select UI but they load broken unless the PC records name them. | slots 11, 12 |
| C4 | `_port_pc_anim_tokens` + `_complete_pc_anim_melee_rows` (anim-table restoration) | restores dropped `(clip,ref)` rows to both PC anim tables. See L3 + §"ANIM" rows per tree. | un-breaks the six half-casting Neidan/RuneMaster/Warfare melee skills. | Warfare, Neidan, RuneMaster, Quest-Reward |

**Also (not a mastery, but same class):** `restore_rest_skill` re-adds the SV-0.4-era **Rest** skill to
the Quest-Reward tree (`questrewardskilltree.dbr` skillName22, level-1 auto-grant) that SV 0.98i dropped;
and C4 restored a `Taunt` row for that tree's `mp_taunt`. Documented here so the anim/`Rest` tokens are
accounted for; slot 9 is not a player mastery.

---

## 2) THE ANIM-TABLE COMPLETION WAVE (`4047b88`, GROUP 0) - the "granted/anim behavior changed" set

This is called out specifically in the brief. Two sub-passes, both inside
`apply_mastery_wave1_broken_fixes`, both ADD-ONLY edits to `anm_malepc01.dbr` + `anm_femalepc.dbr`:

- **B6 `_port_pc_anim_tokens` (Wave 1, `afb30a0`/`4002b17`):** the mod's overridden PC anim tables had
  dropped tokens that Neidan + RuneMaster actives name. Restores the `(clip,ref)` pairs for
  `Ensnare, Flamesurge, ThunderClap, Barrage, Crosscut, Hew` (+ `Taunt`, caught later by the gate on
  `mp_taunt`) row-matched from the base-game tables into **free indices ≤ 15 only** (the conservative
  cap: no base record populated a row above 15). Rows already full at 15/15 (the three *melee* rows
  dHanded/sHanded/spear) were skipped loudly.
- **GROUP 0 `_complete_pc_anim_melee_rows` (`4047b88`):** completes exactly those three skipped melee
  rows **above index 15** (proven engine-valid because SVAERA's own PC tables go to dHanded[23] etc.):
  `dHanded += Hew/Ensnare/Barrage/ThunderClap`; `sHanded += Hew/Ensnare/Crosscut`;
  `spear += Hew/Ensnare/Crosscut`. Byte-copied from the base game (clips are byte-identical to SVAERA's).
  ADD-ONLY, so indices 1-15 (and the mod's unique `Rest` token) survive byte-identical.

**Effect (the skills this unblocked):** the six half-/non-casting skills now cast with a **melee**
weapon equipped - RuneMaster **Arc Attack** (`Crosscut`), **Exploding Strikes** (`Hew`),
**Hail of Axes** (`Barrage`); Neidan **Shen Pao** + **Smoke Cloud** (`Ensnare`), **Chi Realignment**
(`ThunderClap`) - **and** it is the hard prerequisite for the grafted Warfare **Slam** (`Hew`).
Guard: `apply_svc_patches._pc_universal_special_anims` was bound at index ≤ 15 so the >15 melee rows
can't newly re-classify a token as "universal" and suppress soul-skill pcsafe cloning (no soul
regression under either engine behavior). Gates: `validate_player_skill_anims` PASS; det-2x byte-identical.

> Note the *distinct* sibling fix: the three cast-abort nukes **Meteor/Thunderball/Bonespire** were
> fixed by **blanking** their bad token to `''` (B1/B2/B3 below), not by adding a row - because their
> tokens (`MeteorShower`/`Ensnare`/`BoneSpire`) are monster-only and those skills are fine on the
> default cast anim.

---

## 3) PER-TREE LEDGERS

Legend for each tree: **(a) ADDED** = new tree slots · **(b) MODIFIED** = field edits / in-place
reassignments · **(c) ANIM/GRANTED** = cast-castability or granted-behavior changes · **(d) UI/PANEL**
· **(e) NON-CHANGES** = explicit preserved/rejected items.

---

### SLOT 1 - WARFARE  (`records\skills\warfare\drxwarfareskilltree.dbr`; UI panel 1)
Audit diagnosis: cleanest tree; only real deficit = pet uptime. *(MASTERY_AUDIT_2026-07-09 §1 #4.)*

**(a) ADDED (4 slots):**
- `drxhamstring.dbr` - **Hamstring**, slot 26 / UI skill25 (428,279). Legacy restore from SV 0.4.1
  (`restore_legacy_skills` Patch 11.D, `build_svc_database.py`): cloned from the 0.98i
  `drxonslaught_hamstring` shape, then 0.4.1 fields imported; `Skill_Modifier`,
  `skillDependancy → drxonslaught_ignorepain`. Tag `tagSkillName011` "Hamstring".
- `drx_clubslam.dbr` - **Slam**, slot 27 / UI M1 skill26 (328,31). SVAERA graft (`d10f04c`); a
  cyclops-club ground-slam line AoE (`Skill_AttackWave`, anim `Hew`). **Depends on GROUP 0** (§2).
- `drx_clubslam_fissure.dbr` - **Fissure**, slot 28 / UI skill27 (328,217, circular). Slam modifier.
- `drx_ancestralmod.dbr` - **Lasting Legacy**, slot 29 / UI skill28 (328,341, circular). Ancestral-Horn modifier.
- New SV tags authored via the data path: `tagSlam_NAME/DESC`, `tagSlam_FissureNAME/DESC`.

**(b) MODIFIED (Wave 2, `e57ca7e`):**
- `drxancestralhorn.dbr` - `skillCooldownTime` 300→120 + `skillCooldownReductionModifier` 300→120
  (kept in sync); `spawnObjectsTimeToLive` 30→45. *(pet uptime ~10%→~37%; the tree's one real deficit.)*
- `drxbattlestandard.dbr` - `spawnObjectsTimeToLive` tail 18..36 → 24..50. *(the only mobile team-amp/resist-shred, ~50%→higher uptime.)*
- `drxwarwind.dbr` - `skillCooldownTime` 12→8 + `skillCooldownReductionModifier` 12→8. *(optional "feel"; AoE already at bar.)*
- `spectralsoldier_01..20.dbr` (×20) - `lootForearmItem1` path fix (delete spurious `Armbands\`) to
  the existing lowercase `m_wraitharmband.dbr`. *(HYG: path repoint to an existing record - no
  Monster.tpl→Pet.tpl field copy, so no crash class.)*

**(c) ANIM/GRANTED:** Slam's `Hew` cast becomes valid on melee weapons only after GROUP 0 (§2);
Warfare's own `Exploding Strikes` (Hew) also rides that fix.
**(d) UI/PANEL:** +4 buttons (skill25-28), panel re-registered by C2.
**(e) NON-CHANGES:** no skill removed/renumbered; tree is otherwise the SVAERA DRX Warfare tree we
already shipped.

---

### SLOT 2 - DEFENSE  (`records\skills\defensive\drxdefensiveskilltree.dbr`; UI panel 2)
Audit diagnosis: **BELOW bar** (strong-end tank), zero pets, flat damage, shield opener zeroed. *(§1 #1.)*

**(a) ADDED (2 slots, SVAERA graft `d10f04c`):**
- `drx_activeblock.dbr` - **Perfect Block**, slot 26 / UI skill25 (428,31). ~2s invuln + run-speed
  burst (`Skill_BuffSelfInvulnerable`, anim `ShieldSkill02`, castable with a shield).
- `drx_summonphalanx.dbr` - **Unyielding Phalanx**, slot 27 / UI skill26 (428,155). Summons Spartan
  phalanx pets (`Skill_DefensiveGround`, anim `CallOfTheHunt`). **Fills the audit's worst Defense axis
  (zero pets).** Pets/FX resolve from base xpack3.

**(b) MODIFIED:**
- **[FIX B4]** `drxweaponpool_shieldsmash.dbr` (Wave 1, `afb30a0`) - port regression zeroed the damage.
  Restore `offensivePhysicalMin` 0 → `[12,18,25,31,37,43,49,55,59,61]`;
  add `offensivePhysicalModifier` 0 → `[20,24,28,32,36,40,44,47,49,50]` (len 10 = ult).
- **Wave-1 boosts (`abb3a69`):** `drxbatter` physMod ~3..25→6..55 + mana −6/lvl; `drxshieldcharge`
  +physMod 15..80 ladder; `drxheave` +1..5% current-life execute; `drxcolossusform` cd 360→180,
  speed malus −30→−15, absorb ~35→~50; `drxdefensivemastery` front-load `defensiveElementalResistance`
  ML1-40 to ~8%@ML40 (0.2/lvl, tail kept); `drxbatter_rendarmor` armor-shred ×160/6s; `drxheave_cleave`
  +30..120 base bleed/3s.
- **`drxrallybuff.dbr` (D11, build31 Group 3 `ed552ea`):** `skillCooldownTime` 45→30 (party heal-burst uptime).

**(c) ANIM/GRANTED:** none (Perfect Block / Summon Phalanx anims already resolve in ours).
**(d) UI/PANEL:** +2 buttons; panel re-registered.
**(e) NON-CHANGES:** on every shared skill ours already beats SVAERA (our Shield Smash +50% phys mod,
Batter ult 55 vs SVAERA 25) - so no SVAERA shared-skill adopted; nothing removed.

---

### SLOT 3 - EARTH  (`records\skills\earth\drxearthskilltree.dbr`; UI panel 3)
Audit diagnosis: **BELOW bar**; headline Meteor uncastable, ST throttled, mana-starved, zero mobility. *(§1 #2.)*

**(a) ADDED (4 slots, SVAERA graft `d10f04c`):**
- `drx_firenova.dbr` - **Fire Nova**, slot 26 / UI skill25 (428,31). Radius fire AoE + burn (`Skill_AttackRadius`, anim `ThunderClap`).
- `drxrupture.dbr` - **Rupture**, slot 27 / UI skill26 (428,93). Weapon-scaled ranged-spread earth attack (`Skill_AttackWeaponRangedSpread`, no cast anim).
- `drxrupture_burning.dbr` - **Burning Bolts**, slot 28 / UI skill27 (428,217, circular). Rupture modifier (tag `tagBurningBoltsNAME/DESC`).
- `drxrupture_flare.dbr` - **Flare**, slot 29 / UI skill28 (428,341, circular). Rupture modifier.
- Graft cleanup: cleared `drxrupture` two dangling `particleEffectName2/3` placeholder FX refs
  (`records\sandbox\chris\unarmedprojectile_fx01.dbr`) on import. Rupture/Flare *display* tags resolve
  to the mod's existing 0.98i text (NOT re-emitted - would trip the duplicate-tag gate).

**(b) MODIFIED:**
- **[FIX B1]** `drxmeteor.dbr` (Wave 1) - `skillSpecialAnimationName 'MeteorShower' → ''` (un-breaks the
  ~7,900-dmg ultimate; note `''` not `'0'`).
- **Wave-1 boosts (`abb3a69`):** `drxmeteor` cd 360→60; `drxvolcanicorb` cd 4→1.5; `drxearthmastery`
  mana ladder 8..320→12..480 + new `characterSpellCastSpeed` 0→+20%@ML40 + `characterRunSpeed`
  0→+12%@ML40; `drxeruption_moltenlava` add enemy total-resist shred 25..40%/3s (verified base field
  family); HYG: cleared SandBox `UnarmedProjectile_FX01` danglers on `drxvolcanicorb`/`drxflamesurge`
  + Wildfire soundpak danglers on `eruption_aeprojectile`.
- **Core Dweller pet overhaul (D17, build31 Group 3 `ed552ea`, `_apply_group3_tunes`; Will: "make the
  volcano guy much stronger"):** the Earth summon's pet bodies
  `records\skills\earth\pet\coredweller_01..20.dbr` (×20) - `characterLife` **×1.75** (781→1367 @ tier 1,
  scaling to ~3937 @ top tier), `handHitDamageMin`/`handHitDamageMax` **×1.6**, `characterStrength`
  **×1.25**, `characterLifeRegen` **×1.5**; the taunt skill-kit is left untouched (identity kept). Same
  GROUP 3 commit/function as Defense-D11 (Rally) and Occult-D16 (Shadow Stalker). Pet bodies reached via
  `spawnObjects` (not golden-tracked; Earth is not frozen anyway).

**(c) ANIM/GRANTED:** Fire Nova's `ThunderClap` is staff-safe already; GROUP 0's dHanded ThunderClap row covers dual-wield.
**(d) UI/PANEL:** +4 buttons; panel re-registered; F7 (`182690e`) added a Rupture tooltip DESC wiring.
**(e) NON-CHANGES:** SVAERA's `drxmeteor` (still `MeteorShower`, cd 360) explicitly NOT adopted - that's the wholesale-regression example.

---

### SLOT 4 - STORM  (`records\skills\storm\drxstormskilltree.dbr`; UI panel 4)
Audit diagnosis: **COMPARABLE but held back**; lowest HP, one fragile pet carries the headline aura,
Thunderball uncastable, no mobility. *(§1 #3.)*

**(a) ADDED (2 slots, SVAERA graft `d10f04c`):**
- `drx_lightningdash.dbr` - **Lightning Dash**, slot 26 / UI skill26 (428,31). Lightning blink / gap-closer
  (`Skill_WeaponPool_WarmUp`, +444% run-speed, **no cast anim = safest graft**). The audit's #1 Storm gap (zero mobility).
- `drxfrostnova.dbr` - **Frost Nova**, slot 27 / UI skill27 (428,155). Cold AoE + freeze (`Skill_AttackRadius`,
  anim `ThunderClap`); ports 2 SV-custom FX records; tag `tagSVAERSkillStorm001` "Frost Nova".

**(b) MODIFIED:**
- **[FIX B2]** `drxthunderball.dbr` (Wave 1) - `skillSpecialAnimationName 'Ensnare' → ''` (also revives its dependent `drxthunderball_concussiveblast`).
- **Wave-1 boosts (`abb3a69`):** `drxstormmastery` life slope 17→22.5/lvl (680→900@ML40); `stormwisp_01..20`
  life ~1.5× (ult 775→~1190, kept < Shadow Stalker 1440) + a **new pet-safe resist passive** (35%
  freeze/stun/fire/lightning/cold, cloned from `bonepet_passive_attributes` into a free pet slot on all
  20 tiers); `drxstormwisp_petskill_eyeofthestormbuff` +12% run-speed; HYG: `drxstormwispsummoning`
  `targetFxPakName` leading-space fix.
- **F5 render HYG (`182690e`, `apply_svc_patches.py`):** `sveffects\glacialorb_projectile_01.dbr` `mesh`
  `SVMesh\meshes\glacialorb01.msh` → base `Effects\Projectiles\ShardIce01.msh` (the SVMesh glacial-orb
  embedded a bad/invisible shader; shader-verified swap - cosmetic only, no stat/behavior change).

**(c) ANIM/GRANTED:** Frost Nova `ThunderClap` staff-safe; dual-wield covered by GROUP 0.
**(d) UI/PANEL:** +2 buttons; F7 (`182690e`) de-overlapped the Storm panel grid cells.
**(e) NON-CHANGES:** SVAERA's `drxthunderball` (still `Ensnare`) NOT adopted.

---

### SLOT 5 - OCCULT  🔒 GOLDEN-FROZEN  (`records\skills\stealth\drxstealthskilltree.dbr`; UI panel 5)
The Occult (renamed Rogue/Stealth) tree is Will's hand-tuned reference bar and is **excluded from all
systematic waves** by the golden-freeze gate (L2). Its differences from SV 0.98i are the pre-existing
hand-tuning (presumed intentional, never enumerated field-by-field, never reverted) plus these three
sanctioned exceptions. *(Independent check: a build-vs-SV098i field diff finds the whole stealth folder
matches the `upstream/soulvizier_098i` baseline with **no** wave-style value delta - the only real
changes are the 2 added Darkling slots + the three sanctioned exceptions below, everything else being
the universal C1 cosmetic pass; whatever hand-tuning exists is already baked into that baseline.)*
Frozen tree = **27 slots** (25 SV + the 2 Darklings below).

**(a) ADDED (2 slots - legacy restore, now baked into the golden baseline):**
- `drxdarklings.dbr` - **Darklings**, slot 26 / UI skill25 (328,279). `restore_legacy_skills` Patch 11.A
  (from SV 0.4.1): `Skill_AttackProjectileSpawnPet`, 20 shadow-demon pets + projectile. Tag `tagirregulardemonNAME`.
- `drxdarklings_darkaperture.dbr` - **Dark Aperture**, slot 27 / UI skill26 (328,155, circular). The
  Darklings modifier, renamed to avoid colliding with standalone Breach. New tags `tagDarkApertureNAME/DESC`.

**(b) MODIFIED - the ONLY authorized Occult content deviations, each Will-ordered:**
- **Flash Powder rework 🚧 IN FLIGHT (F5, `182690e`, `_apply_flashpowder_rework`):**
  `records\skills\stealth\drxflashpowder.dbr` - Will called it "trash/unviable." Changes:
  `skillCooldownTime` 15 → 6; add `offensivePierceMin` `[40..260]` / `offensivePierceMax` `[72..380]`
  (len-12 = its `skillUltimateLevel`); add `offensiveProjectileFumbleMin` `[30..85]` +
  `offensiveProjectileFumbleDurationMin` 8.0 (blinds ranged attackers - the Smoke-Screen gap).
  **Golden drift waived per-field:** the 5 keys are listed in `occult_hunting_golden.json`
  `owner_approved_overrides` (present on both in-flight branches) marked "Will-authorized … 2026-07-11 (F5)."
  This is *the* single deliberate flash-powder exception the brief flags.
- **Shadow Stalker pet overhaul (D16 build31 `ed552ea` + D16b F5-wave `182690e`, `_apply_group3_tunes`):**
  the Occult ultimate summon `drx_summon_shadow_stalker.dbr` (a real slot in the frozen tree) drives the
  pet bodies `records\skills\stealth\drxpet\drx_shadow_stalker_01..20.dbr`. **D16 (Will: "make him
  stronger, much stronger"):** replaced the suicide position-swap `skillName7` (`skill_shadowstrike`,
  teleports the squishy pet into packs) with a defensive `shadowstalker_distortionfield` veil; life
  500→2210 ladder (was flat 297), dmg 120-150→386-492 (was flat 83-98), str/dex ladders. **D16b (Will:
  "we lost the paralysis effect"):** restored hard CC as an AoE petrify/stun/confusion on the already-
  registered `skill_shadowzap` chain + resist floor. **These ride `owner_approved_overrides` conceptually
  but need no golden key** - the pet bodies are reached via `spawnObjects` (not a captured buff/pet hop),
  so they are outside the golden snapshot (verified: `skill_shadowzap` absent from the golden json).

**(c-d) ANIM / UI:** none beyond the above (the Darklings buttons predate and are inside the golden baseline).
**(e) NON-CHANGES (the point of the freeze):** every other Occult skill, value, tier, icon, position,
and Text tag is byte-frozen; `validate_mastery_golden` stays green and *proves* the 9-tree waves + grafts
never touched slot 5. No SVAERA graft, no Wave-1/Wave-2 tuning here.

---

### SLOT 6 - HUNTING  🔒 GOLDEN-FROZEN  (`records\skills\hunting\drxhuntingskilltree.dbr`; UI panel 6)
- **Zero *gameplay/mechanical* deviations from SV 0.98i.** The 2026-07-07 audit
  (`docs/MASTERY_AUDIT.md`) found *no* mechanical shipped-vs-SV differences across the full 52-node
  transitive skill graph; every icon/tag/ref resolves. An independent build-vs-SV098i field diff
  confirms **0 real value changes** in the whole Hunting folder - no balance edit, graft, or rework.
  (It is *not* literally byte-identical to SV: the universal cross-tree **C1** faithfulness pass touches
  every tree, so ~90 Hunting records get `.dbr`-reference case/separator normalization and a few stubs
  get display-field injection - neither changes a value, tier, or behavior.) Hunting is on the frozen
  list purely to *prevent* future drift (L2); the cleanest "core = ours" tree in the mod.

---

### SLOT 7 - NATURE  (`records\skills\nature\drxnatureskilltree.dbr`; UI panel 8)
Audit diagnosis: COMPARABLE summoner/sustain; below on personal burst/CC; Force-of-Nature 17% uptime +
a charm-resist copy-paste bug. *(§1 #5.)*

**(a) ADDED (2 slots, SVAERA graft `d10f04c`):**
- `drx_earthbind.dbr` - **Earthbind**, slot 26 / UI M8 skill25 (328,31). Radius-22 root/immobilize AoE
  (`Skill_AttackRadius`, anim `Colossus` = 8/8 universal, the **safest graft of all**, no GROUP 0
  dependency). Fills Nature's audited weakest axis (thin hard-CC).
- `drx_nymph_petmodifier_rootwave.dbr` - **Sylvan Protection**, slot 27 / UI skill26 (328,155, circular).
  Nymph Rootwave pet-modifier; its pet-skill `drx_nymph_petskill_rootwave` rides the closure (pet anim `Overgrowth`).

**(b) MODIFIED - includes 2 in-place *reassignments* (the truest "reassignment" per Will's word):**
- **Patch 11.B (`restore_legacy_skills`, from SV 0.4.1) - same record path, different skill identity:**
  - `drxsprite_summons.dbr`: **Elemental Flurry → Thorn Sprites** (icon `nature\spriteup.tex`, tag `tagThornSpritesNAME`).
  - `drxrenewal.dbr`: **Dissemination → Fabrical Tear** (icon `sprite_synergyup.tex`, tag
    `tagFabricalDischargeNAME`; **`skillUltimateLevel` 16→12**).
- **Wave-2 (`e57ca7e`):** `drxforceofnature` cd 360→180 + `skillCooldownReductionModifier` 360→180
  (deliberately 180 not 120 - see NON-CHANGES); `drxnaturemastery_petbonus` add
  `offensiveTotalDamageModifier` 0→+30% + `defensiveProtection` 0→160 (ML1-40); HYG: cleared the
  `defensiveConvert` charm-resist self-malus copy-paste on `drxregrowth_acceleratedgrowth` + `drxrenewal`;
  repoint `drxwolf_petskill_maul`→`Damage01`, `..._survivalinstinct`→`Buff07`, `sylvannymph` controller ×20.

**(c) ANIM/GRANTED:** Earthbind `Colossus` universal (no anim work needed).
**(d) UI/PANEL:** +2 buttons; the 11.B swaps kept their existing UI cells.
**(e) NON-CHANGES:** Force-of-Nature cd chosen at 180 (not the more-aggressive 120) specifically so
Nature's treant per-hits don't become continuously available and overshoot the frozen Occult pet bar
(explicit over-tune guard, MASTERY_AUDIT_2026-07-09 §4-F).

---

### SLOT 8 - SPIRIT  (`records\skills\spirit\drxspiritskilltree.dbr`; UI panel 7)
Audit diagnosis: COMPARABLE necro summoner/DoT/CC; flagship Bonespire cast-abort + dead pet content. *(§1 #6.)*
**This is the one tree marked KEEP_OURS in the SVAERA comparison** (ours is strictly ahead; no SVAERA graft).

**(a) ADDED (5 slots - legacy restore of Dream-mastery skills, Patch 11.C, `restore_legacy_skills`):**
Cross-grafted from Dream, at Spirit slots 26-30 / UI panel-7 skill25-29:
- `DRXSandsofSleep.dbr` - **Sands of Sleep** (26); `..._troubleddreams.dbr` - **Troubled Dreams** (27);
  `DRXDistortionWave.dbr` - **Distortion Wave** (28); `..._ChaoticResonance.dbr` - **Chaotic Resonance** (29);
  `..._PsionicImmolation.dbr` - **Psionic Immolation** (30). All icons/tags resolve. These are the "5
  player skills SVAERA lacks" that make wholesale-SVAERA an L1 violation for Spirit.

**(b) MODIFIED:**
- **[FIX B3]** `drxenslavespirit.dbr` (Bonespire, Wave 1) - `skillSpecialAnimationName ['BoneSpire'] → ['']` (cast-abort risk on the flagship ~2000 nuke).
- **Wave-2 (`e57ca7e`):** `drxoutsidersummons` cd 360→120 + TTL 30→60; `drxdeathward` cd 300→180;
  re-enabled the disabled `bonepet` spiritbreath (`'xxx'`-prefix stripped on 5 tiers; tiers 6-20 already
  enabled build31) + cleared the dangling `drxplaceholder` skillName2 (skillName6 no-op KEPT per L1);
  cleared `bonescourge_spiritbreath` dangling SandBox FX.
- **Liche King wraithlord re-enable (`apply_mastery_wave2_boosts`, `build_svc_database.py`; re-enable
  introduced GROUP 3 `c6bf6fd`):** the Spirit summon's pet ladder
  `records\skills\spirit\drxpet\wraithlord_01..20.dbr` (×20) had `skillName15`/`skillName16` un-prefixed
  (`xxxrecords\...` → `records\...`), **re-enabling** the DRX author's disabled
  `drx_lichskill_skellysummon2`/`3` skeleton summons on all 20 tiers (dead-content revival per L1; the
  build fails loudly if the two skellysummon target records are missing, so no dangling ref).

**(c) ANIM/GRANTED:** B3 blank restores Bonespire castability.
**(d) UI/PANEL:** +5 buttons (panel 7).
**(e) NON-CHANGES:** **KEEP_OURS** - the optional SVAERA `drx_soulvortex` was evaluated and **not**
grafted (Spirit already 30 slots + over-tuned AoE/resist axis); SVAERA `drx_insidiousmiasma` explicitly
rejected (duplicates our Spirit-Ward Miasma). No SVAERA graft on this tree at all.

---

### SLOT 10 - DREAM  (`records\xpack\skills\dream\drxdreamskilltree.dbr`; base xpack panel)
Audit diagnosis: COMPARABLE; best CC + highest HP; the Nightmare's +60% pet-damage aura "dead three ways." *(§1 #7.)*

**(a) ADDED (1 slot, SVAERA graft `d10f04c`):**
- `drx_summoncopy.dbr` - **Dream Image**, slot 26 / UI xpack-M9 skill25 (128,31). Summon Doppelganger -
  a Limos-skinned clone of you that casts your Dream nukes + a damage-reflect passive (`Skill_SpawnPet`,
  no cast anim). Its pet chain (`dreamcopypet` + aura + `doppelganger_reflect` + conversion-immunity
  passive = the 4 support records that make the "18") + a Doppelganger anim-table asset ride the closure;
  the copy-pet's difficulty-scaling was remapped to our base `pet_difficultydamagescaling.dbr`. Genuine
  3rd Dream pet (the audit's weak axis).

**(b) MODIFIED:**
- **[FIX B5]** `nightmare_01..20.dbr` (Wave 1) - MasterMind aura dead 3 ways: repoint `skillName1` to the
  resolving lowercase `nightmare_petskill_mastermind.dbr` + ramp `skillLevel1` 0 → `min(tier,12)` on all
  20 tiers. **[HYG]** normalized literal-`'0'` anim tokens to `''` on 2 passives
  (`drxluciddream_premonition`, `drxdistortionfield`) - inert but the documented anti-pattern.
- **Wave-2 (`e57ca7e`):** cleared the `nightmare` timefield self-buff ×20; `drxphantasm` cd 180→120 +
  TTL 15..25→15..30 + cleared its pet RingAll loot dangler ×20; `nightmare` psionicbeam
  offensivePhysical/LifeMin `[8..66]`; mana ladders `temporalrift` 10→16 / `spellbreaker` 10→12 /
  `spellshock` 10→12; **`phantomstrike` self-slow `[-11..-50]` zeroed** (field KEPT per L1).

**(c) ANIM/GRANTED:** Dream Image no cast anim; PhantomStrike's abort token handled by the zero + the
anim gate (its token was never added to the tables - deliberately, since only Neidan's unattached Splash names it).
**(d) UI/PANEL:** +1 button, registered directly in the xpack Dream panectrl (`_graft_register_dream_button`).
**(e) NON-CHANGES:** SVAERA `drx_psionictouch_staffbeammod` rejected (anim `StaffBeam` = 0/8 in ours + conflicts with our Psionic Touch rework).

---

### SLOT 11 - RUNEMASTER  (base DLC tree `Records\XPack2\skills\RuneMaster\RuneMaster_SkillTree.dbr`; xpack2 panel)
The mod ships the **vanilla** RuneMaster tree with our edits applied as overrides - deliberately NOT
SVAERA's `_drx_*` re-path (L4 character-safety). *(SVAERA comparison §Runemaster.)*

**(a) ADDED (1 major graft - Rune Golem, Lane A `19f9c60`, `_create_rune_golem`):**
- `records\xpack2\skills\runemaster\_drx_runegolem.dbr` (**Runic Golem** summon) + a 20-tier pet ladder
  `runegolem_01..20` + 7 pet-skills + 6 stat passives + AI controller = **35 records**, appended as UI
  **Skill23** (grid 628,217) and registered in the xpack2 **and** xpack3 Runemaster panectrl. A durable
  elite rune-construct pet (~600→1950 HP, cd 15). Ported from a committed faithful SVAERA snapshot; the
  **D5 invisible-pet hazard was resolved** by shipping the extracted mesh/textures in
  `assets/runegolem/_DRX_Meshes.arc` + `_DRX_Textures.arc` (proven by `validate_render_chain_golem.py`).
  SVAERA-only deps repointed to base: Menhir-Wall prereq → our vanilla `menhirwall`; cosmetic FX/sounds
  → base. 6 tags `x2tagNewSkillRunes001` etc.

**(b) MODIFIED:**
- **Wave-2 base→mod overrides (`e57ca7e`):** `runemaster_mastery` Life 800→1160 + **Mana 0→400** (it was
  the sole 0-mana INT mastery); `menhiraltar` (Guardian Stones) cd 240→120 + TTL 45→60.
- **Lane B vanilla-path buffs (`d10f04c`, `_apply_runemaster_buffs`):** `menhirwall` cd 22→18 + wall TTL
  10→14 (+40% uptime); `mines` cd 9→8 + active duration 10→14. *(Scalar edits on the vanilla-path
  records only - never the tree pointer, never SVAERA's `_drx` copies; non-overlapping with Wave-2 + the golem.)*

**(c) ANIM/GRANTED:** RuneMaster **Arc Attack** (`Crosscut`) / **Exploding Strikes** (`Hew`) / **Hail of
Axes** (`Barrage`) un-broken by the C4/GROUP-0 anim work (§2). Our unique `Rest` token (for the restored
Rest skill) preserved through all anim edits.
**(d) UI/PANEL:** +1 button (Skill23) in both xpack2/xpack3 panels.
**(e) NON-CHANGES:** tree POINTER kept vanilla (never swapped to SVAERA's `_drx` tree = would strand
characters); SVAERA's `runecircle` cd 9→12 **nerf** explicitly rejected.

---

### SLOT 12 - NEIDAN  (base DLC tree `records\XPack4\Skills\Neidan\neidanskilltree.dbr`; xpack4 panel)
SVAERA brings **no new Neidan skills** and even nerfs the mastery INT; the only worthwhile SVAERA asset
for Neidan is the shared anim rows. So Neidan = **anim-only adoption + our own tuning**. *(SVAERA comparison §Neidan.)*

**(a) ADDED:** none (0 new skills).
**(b) MODIFIED (Wave-2 base→mod overrides, `e57ca7e`):** `neidanmastery` Life 900→1050;
`terracotta_servant` petLimit `[1×9,2]` → `[1×7,2,2,3]`; `deathbomb` `skillCastChance` 33→45; `splash`
+`skillDependancy = shenpao` (attaches the previously dead unattached ML40 modifier).
**(c) ANIM/GRANTED:** Neidan **Shen Pao** + **Smoke Cloud** (`Ensnare`) and **Chi Realignment**
(`ThunderClap`) become fully castable via C4/GROUP-0 (§2) - the audit's #1 Neidan fix.
**(d) UI/PANEL:** none.
**(e) NON-CHANGES:** wholesale SVAERA Neidan rejected (its `_drx_neidanmastery` nerfs INT/lvl, adds no
combat tail); no Neidan skill/pet/mastery record ported from SVAERA.

---

## 4) EXECUTIVE SUMMARY (one page)

Counts are *tree slots added* / *distinct skill-records modified (field edits, in-place reassignments,
anim/ladder restores)* / *frozen-or-preserved*. "Modified" folds each 20-tier pet ladder as one logical record.

| Slot | Mastery | Added | Modified | Frozen | One-line rationale |
|---|---|:--:|:--:|:--:|---|
| 1 | **Warfare** | **4** | 4 | - | Cleanest tree; add the 3 dropped Atlantis skills (Slam/Fissure/Lasting Legacy) + legacy Hamstring; Wave-2 fixes only pet uptime. |
| 2 | **Defense** | **2** | 9 | - | BELOW bar: un-zero Shield Smash (B4), add burst/execute/DoT tunes + Rally uptime, and graft the pet line it lacked (Perfect Block + Summon Phalanx). |
| 3 | **Earth** | **4** | 7 | - | BELOW bar: un-break Meteor (B1) + fund the caster (mana/cast-speed/mobility) + Core Dweller pet ×1.75 life (D17) + graft Fire Nova & the Rupture line. |
| 4 | **Storm** | **2** | 5 | - | Un-break Thunderball (B2), firm the fragile wisp + HP, glacial-orb render fix, and graft the mobility+CC it utterly lacked (Lightning Dash + Frost Nova). |
| 5 | **Occult** 🔒 | 2\* | 2\*\* | **27** | GOLDEN-FROZEN hand-tuned bar. Only sanctioned deviations: legacy Darklings/Dark Aperture (baked into baseline) + Will-ordered Flash Powder rework (in-flight, 5 golden fields waived) + Shadow Stalker overhaul. |
| 6 | **Hunting** 🔒 | 0 | 0 | **25** | GOLDEN-FROZEN, gameplay-identical to SV 0.98i - zero mechanical deviations (only the universal C1 ref-case/display pass alters any bytes); frozen only to prevent future drift. |
| 7 | **Nature** | **2** | 7 | - | Reassign 2 skills to their SV-0.4.1 identities (Thorn Sprites / Fabrical Tear), Wave-2 uptime + pet-bonus, graft Earthbind + Sylvan Protection (hard-CC axis). |
| 8 | **Spirit** | **5** | 6 | - | **KEEP_OURS** (strictly ahead of SVAERA): un-break Bonespire (B3), revive dead content (bonepet spiritbreath + Liche King wraithlord skeleton summons ×20), and the 5 restored Dream cross-skills that make wholesale-SVAERA illegal. No SVAERA graft. |
| 10 | **Dream** | **1** | 8 | - | Revive the dead MasterMind aura (B5) + Wave-2 tunes; graft Summon Doppelganger as a real 3rd pet. |
| 11 | **RuneMaster** | **1** | 4 | ptr | Keep the VANILLA tree (character-safe), buff mastery Life/Mana + Menhir/Mines uptime, and graft the Rune Golem (mesh shipped). Tree pointer frozen vanilla. |
| 12 | **Neidan** | 0 | 4 | - | Anim-only adoption: our Wave-2 already beats SVAERA on every record; only fix is making Shen Pao/Smoke Cloud/Chi Realignment castable via the anim work. |

\* Occult "added" (Darklings/Dark Aperture) predate the freeze and are part of the golden baseline.
\*\* Occult "modified" = the two Will-ordered exceptions (Flash Powder + Shadow Stalker); everything else frozen.
"ptr" = RuneMaster tree pointer deliberately frozen to vanilla (non-adoption of SVAERA's `_drx` tree).

**Totals:** 23 new player-tree slots added across 8 trees (Warfare 4, Defense 2, Earth 4, Storm 2,
Nature 2, Spirit 5, Dream 1, RuneMaster 1, + Occult's 2 legacy) - the SVAERA graft contributes 14 of
those (Lane B) + the Rune Golem (Lane A); the rest are SV-0.4.1 legacy restores. **Zero removals**
anywhere (L1). Occult + Hunting proven untouched by the golden gate (L2). Every cast-abort/half-cast
bug (Meteor, Thunderball, Bonespire, Shield-Smash-zero, MasterMind-dead, + the 6 anim half-casts)
fixed. Wholesale SVAERA adoption rejected on all 12 trees; only additive hybrid grafts taken (L4).

## 5) COMMIT / SOURCE INDEX (for verification)
- `7770a40` - mastery audit + boost plan (Will approved both waves). `docs/MASTERY_AUDIT_2026-07-09.md`.
- `c344f94` - standing "NEVER REMOVE SKILLS" rule (L1).
- `afb30a0` + `4002b17` - Wave 1 broken fixes B1-B6 (`apply_mastery_wave1_broken_fixes`).
- `abb3a69` - Wave 1 boosts (Defense/Earth/Storm) (`apply_mastery_wave1_boosts`).
- `e57ca7e` - Wave 2 (Warfare/Nature/Spirit/Dream + RuneMaster/Neidan) (`apply_mastery_wave2_boosts`).
- `4047b88` - GROUP 0 PC-anim melee-row completion (`_complete_pc_anim_melee_rows`) + `_port_pc_anim_tokens`.
- `d10f04c` (merged `31a0bce`) - build36 Lane B: 18-skill SVAERA graft (`graft_svaera_mastery_skills`, `_GRAFT_SKILLS`) + Runemaster buffs (`_apply_runemaster_buffs`).
- `19f9c60` - build36 Lane A merge incl. Rune Golem (`_create_rune_golem`, `apply_svc_patches.py`).
- `182690e` - 🚧 IN FLIGHT (base commit of `feat/build36-fix-wave`, titled "build36 fix wave: F1-F7
  code"; also merged into `feat/build36-content-wave` via `5e6bfd6`): F5 Flash Powder rework
  (`_apply_flashpowder_rework`) + Shadow Stalker D16b + the `occult_hunting_golden.json` owner-approved
  overrides. `5e2e30b` = fix-wave gate hardening on top (fix-wave tip). `feat/build36-content-wave`'s own
  extra commits `79de1d7`/`24a8ab8` are non-mastery boss/relic/loot content (not in this ledger).
- `restore_legacy_skills` (Patch 11, `build_svc_database.py`; documented in `docs/MASTERY_AUDIT.md`) -
  Occult Darklings (11.A), Nature Thorn-Sprites/Fabrical-Tear reassignments (11.B), Spirit +5 Dream
  skills (11.C), Warfare Hamstring (11.D).
- `validate_mastery_golden.py` + `tools/occult_hunting_golden.json` - the L2 golden-freeze gate.
- `docs/SVAERA_MASTERY_COMPARISON.md` (`11777ee`) + `docs/PERMISSIONS.md` (`de1562a`) - the L4 hybrid-graft proposal + soa's reuse grant.
