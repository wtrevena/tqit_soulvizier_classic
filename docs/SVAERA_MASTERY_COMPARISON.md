# SVAERA vs OURS - Mastery Adoption Proposal (2026-07-10)

> **SIGN-OFF-FIRST.** This is a proposal for Will. No production records were changed to write it.
> Scope: the 9 tunable masteries (Warfare, Defense, Earth, Storm, Nature, Spirit, Dream, Runemaster,
> Neidan). **Occult (slot 5) and Hunting (slot 6) are hard-excluded** (Will's golden-frozen hand-tuning,
> never compared for adoption). Laws honored throughout: never REMOVE a skill or tree slot; existing
> characters must keep working; player-skill anim-token safety (B1-B6 cast-abort class); Atlantis/xpack
> DLC content is legal because our mod already requires those DLCs for MP.
>
> Evidence base: direct `.arz` byte reads of our shipped DB, SVAERA's real DB, and vanilla AE, cross-checked
> against the four analysis lanes and the 2026-07-09 mastery audit. Artifacts read:
> - OURS: `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (also cross-checked vs the Workshop-shipped
>   copy `steamapps/workshop/content/475150/3759792705/...`; both give identical anim coverage).
> - SVAERA (real, 67.8 MB): `steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz`.
>   (Note: the `reference_mods/SVAERA_customquest/Database/*.arz` in-repo is a 2048-byte stub, NOT the real DB.)
> - Vanilla AE: `.../Titan Quest Anniversary Edition/Database/database.arz`.

---

## 1) DIRECT ANSWER to Will's question

**No, the masteries do not need further drastic improvement, and no, you should not adopt SVAERA wholesale.**
On every skill our mod shares with SVAERA, your shipped Wave 1 + Wave 2 work is equal to or better than soa's,
and adopting soa's trees wholesale would actively **regress** you: it would re-introduce the exact three cast-abort
bugs you just fixed (Earth Meteor `MeteorShower`, Storm Thunderball `Ensnare`, Spirit Bonespire `BoneSpire` are all
still LIVE in SVAERA, blanked in ours), undo your uptime/damage tuning, and for three trees it would either delete
player skills or strand existing characters (both forbidden). So SVAERA did **not** "already improve" the masteries
over yours; on shared content you are ahead.

**What SVAERA did do** is *keep* a thin layer of genuinely-new content that your back-port from pre-Atlantis SV 0.98i
dropped, plus one asset that is strictly better than ours: **its complete player-character animation tables**. This is
the real prize. Our animation tables are a lossy DRX merge that silently dropped weapon rows, which is *why* several of
your skills only half-cast; SVAERA's tables are a superset that restores them. On top of that, SVAERA retained roughly
a dozen additive Atlantis/DRX player skills our trees never wired in (Slam, Earthbind, Lightning Dash, Frost Nova, Fire
Nova, Rupture, Active Block, Summon Phalanx, Summon Doppelganger, Rune Golem). Every one of these is a pure ADDITION
that fills a gap the audit flagged, is character-safe (append at new tree slots, never renumber), and carries a tiny
port closure. **Verdict: 8 of 9 masteries = adopt specific additive pieces (HYBRID_GRAFT); 1 (Spirit) = keep ours.**
soa gave verbal permission to reuse his work (see section 6).

The single most important reconciliation this synthesis produced (two lanes disagreed, resolved against the bytes):
**our animation tables are NOT a superset of vanilla, they are a lossy merge that both added DRX tokens and dropped
vanilla weapon rows.** Measured directly in our shipped `.arz`, the melee token `Hew` is present on only 4 of 8 weapon
rows and is **missing on exactly the weapons a Warfare player uses (dual-wield, single-hand, spear)**. That means the
Warfare "Slam" skill (whose cast animation is `Hew`) would abort in our mod as-is, contradicting the lane that called
it "castable with every Warfare weapon" (that lane measured vanilla and wrongly assumed our table was a superset). The
fix is the same additive animation-row graft that unblocks Runemaster/Neidan, so it becomes graft #0, the shared
prerequisite (details in section 5).

---

## 2) VERDICT TABLE - all 9 masteries

| Mastery | Verdict | One-line rationale | Graft size (records to port) |
|---|---|---|---|
| **Warfare** (slot 1) | **HYBRID_GRAFT** | Ours = SVAERA tree + Wave-2 tuning; add the 3 dropped Atlantis skills (Slam + Fissure + Lasting Legacy). | 3 skill records + 3 new slots + ~4 tags. **Slam needs the shared anim rows (below).** |
| **Defense** (slot 2) | **HYBRID_GRAFT** | Ours wins every shared skill; add the 2 dropped Atlantis actives (Active Block, Summon Phalanx). Summon Phalanx fills the audit's worst Defense axis (zero pets). | 2 skill records + 2 slots; FX/pets/tags resolve in base xpack3. |
| **Earth** (slot 3) | **HYBRID_GRAFT** | Ours un-broke Meteor + retuned; add Fire Nova (AoE) + the Rupture line (spammable weapon/caster hybrid). | 4 skill records + 3 SV tags + 1 dangling-FX repoint. |
| **Storm** (slot 4) | **HYBRID_GRAFT** | Ours un-broke Thunderball; add Lightning Dash (the mobility the audit said Storm utterly lacks) + Frost Nova. | 2 skill records + 2 SV FX records + 1 SV tag. |
| **Nature** (slot 7) | **HYBRID_GRAFT** | Ours ahead + retuned; add Earthbind (fills the thin hard-CC axis, the SAFEST graft) + nymph Rootwave. | 3 records + 2 slots; all anim-safe (Colossus 8/8, pet anim). |
| **Spirit** (slot 8) | **KEEP_OURS** | Ours is strictly ahead: fixed B3, revived dead content, and ADDED 5 player skills SVAERA lacks. SVAERA's extras are functional duplicates; adopting = law violation (would delete our 5 skills + regress B3). | 0 recommended (optional Soul Vortex is low value, not recommended). |
| **Dream** (slot 10) | **HYBRID_GRAFT** | Ours revived MasterMind (dead in SVAERA) + out-tunes; add Summon Copy / Doppelganger (a real 3rd Dream pet, the audit's weak axis). | ~6 records + 2 tags + a difficulty-scaling remap. |
| **Runemaster** (slot 11) | **HYBRID_GRAFT** | Keep our vanilla-path tree (character-safe); add Rune Golem (durable elite pet) + the shared anim rows; optional number edits. | Anim rows + ~24 records (Rune Golem) + **a mesh extraction (D5 blocker)**. |
| **Neidan** (slot 12) | **HYBRID_GRAFT (anim-only)** | Our Wave 1+2 beats SVAERA on every Neidan record (SVAERA even nerfs mastery INT); the ONLY thing to adopt is the shared anim rows. | 0 new records (rides the shared anim-table graft). |
| **SHARED / graft #0** | **PREREQUISITE** | Complete our PC animation tables from SVAERA's superset: add the missing weapon rows for Ensnare/Hew/Crosscut/Barrage/ThunderClap. Unblocks existing broken skills AND several new grafts. | 2 record edits: `anm_malepc01.dbr` + `anm_femalepc.dbr` (additive rows only). |

Reconciled bottom line: two lanes independently concluded "Runemaster + Neidan are the ONLY adoption targets, SVAERA is
strictly behind on the 7 shared trees." That is true for *shared skill numbers/bugs* but WRONG as a whole: closure-count
inflation hid that Defense/Earth/Storm/Warfare/Nature/Dream each carry additive dropped player skills. The corrected
picture is 8 of 9 = additive graft.

---

## 3) PER-MASTERY DETAIL (validated against the bytes)

### Warfare - HYBRID_GRAFT
Our tree IS SVAERA's DRX tree plus Wave-2 tuning: Ancestral Horn cd 300->120 + TTL 30->45, War Wind cd 12->8 with a
stronger target/modifier ladder, Battle Standard uptime, and ours-only slots (Battle Standard glory pet-modifier +
Hamstring). SVAERA carries none of that. SVAERA's tree has 27 slots vs our 26 and holds **3 Atlantis (xpack3) skills our
back-port dropped**: `drx_clubslam` (Slam, `Skill_AttackWave`, anim `Hew`), `drx_clubslam_fissure` (modifier), and
`drx_ancestralmod` (Lasting Legacy, an Ancestral Horn modifier). All confirmed present in SVAERA and absent in ours.
**Anim reconciliation:** Slam's `skillSpecialAnimationName = 'Hew'`, and `Hew` in OUR tables is only 4/8 (rows
dualRanged/rangedOneHand/staff/unarmed), missing dHanded/sHanded/spear. A Warfare bruiser holds exactly those melee
weapons, so Slam aborts as-is. It is safe ONLY after graft #0 restores the Hew melee rows. Fissure and Lasting Legacy
are modifiers with no cast anim = safe.

### Defense - HYBRID_GRAFT
For shared skills ours is strictly better (our Shield Smash carries a +50% physical modifier SVAERA lacks; our Batter
ult modifier 55 vs SVAERA 25; SVAERA's Shield Smash is not broken, so the audit's "zeroed B4" was our own pre-Wave-1
regression, since fixed). SVAERA's tree wires 27 slots vs our 25 and the 2 extras are real additive Atlantis actives:
`drx_activeblock` (Active Block / Perfect Block, `Skill_BuffSelfInvulnerable`, anim `ShieldSkill02`) and
`drx_summonphalanx` (Summon Phalanx, `Skill_DefensiveGround`, anim `CallOfTheHunt`). Both confirmed. **Anim:**
`ShieldSkill02` is 3/8 in ours including `sHanded` (the sword+shield row), so Active Block casts with a shield equipped;
`CallOfTheHunt` is 7/8 in ours, fine. Summon Phalanx directly fills the audit's worst Defense dimension (zero pets); its
phalanx pets and FX resolve from base xpack3 (no art port).

### Earth - HYBRID_GRAFT
Adopting SVAERA regresses AND breaks the no-removal law: SVAERA's `drxmeteor` still ships `MeteorShower` (uncastable) and
cd 360 vs our fixed `''` + cd 60; SVAERA's tree does not wire our `drxstoneform_moltenrock` slot. But SVAERA's tree has
28 slots vs our 25 and the extras are 4 additive dropped skills: `drx_firenova` (Fire Nova, `Skill_AttackRadius`, anim
`ThunderClap`) and a full SV-authored Rupture line `drxrupture` (`Skill_AttackWeaponRangedSpread`, no cast anim) +
`drxrupture_burning` + `drxrupture_flare` (modifiers, no cast anim). All confirmed. **Anim:** `ThunderClap` is 7/8 in ours
(missing only dHanded), so Fire Nova casts with staff and every non-dual-wield weapon; the shared graft #0 adds the dHanded
ThunderClap row to cover dual-wield too. Hazard carried from the lane: `drxrupture` references the known dangling
`records\sandbox\chris\unarmedprojectile_fx01.dbr` placeholder (same one already on our Volcanic Orb/Flamesurge); repoint or
clear (cosmetic).

### Storm - HYBRID_GRAFT
Adopting SVAERA regresses (its `drxthunderball` still carries `Ensnare` = uncastable, reviving the dead Thunderball +
Concussive Blast) and violates no-removal (SVAERA's tree omits our `drxsquall_hail` slot). SVAERA's tree has 26 slots vs
our 25 and the 2 extras are the single most valuable adoption in the whole comparison: `drx_lightningdash` (Lightning
Dash, `Skill_WeaponPool_WarmUp`, **no cast anim = fully safe**, characterRunSpeedModifier 444) and `drxfrostnova`
(`Skill_AttackRadius`, anim `ThunderClap`, cold AoE + freeze). Both confirmed. Frost Nova needs its 2 SV-custom FX
records ported; Lightning Dash's FX resolve in base xpack3.

### Nature - HYBRID_GRAFT
Ours = SVAERA tree + Wave-2 tuning (Force of Nature cd 360->180, wolf FX fix, ours-only Treeskin + nymph wrath slots).
SVAERA kept the 2 Atlantis Nature skills our back-port swapped away: `drx_earthbind` (Earthbind, `Skill_AttackRadius`,
anim `Colossus`) + the nymph Rootwave pair (`drx_nymph_petmodifier_rootwave` + `drx_nymph_petskill_rootwave`, pet anim
`Overgrowth`). **Anim: Earthbind is the SAFEST possible graft: `Colossus` is 8/8 in ours (verified), universal on every
weapon, no graft #0 dependency.** Earthbind fills Nature's audited weakest dimension (thin hard-CC): a radius-22
root/immobilize AoE. Rootwave rides the nymph's own anim table (pet-safe; our nymph already references `Overgrowth`).

### Spirit - KEEP_OURS
Ours is strictly ahead on every axis and adopting SVAERA would break the no-removal law. Ours fixed B3 (Bonespire
`BoneSpire`->`''`, still broken in SVAERA), re-enabled dead `bonescourge_spiritbreath` and reworked it to a stronger
projectile-ring, tuned Ether Lord/Death Ward uptime, and **added two full player skills SVAERA lacks** (Sands of Sleep
hard-CC + Distortion Wave nuke) plus the Distortion/Chaotic/Psionic-Immolation chain. SVAERA's "extras" are functional
duplicates we already provide via repurposed records (SVAERA Acid Rain == our Circle-of-Power rework; SVAERA
Relentless Evil / Mortal Conduit == our Life-Drain reworks). The only optional graft is Atlantis `drx_soulvortex` (Soul
Vortex, no cast anim), but our Spirit tree is already 30 slots (grid-dense) and the audit flagged Spirit's AoE/resist axis
as already over-tuned, so it is **not recommended**. Do NOT graft SVAERA `drx_insidiousmiasma` (it duplicates our existing
Spirit Ward Miasma tag = two Miasmas).

### Dream - HYBRID_GRAFT
SVAERA is BEHIND: the Nightmare MasterMind pet aura is dead/unwired in SVAERA (its `nightmare_01` has no `skillName1`
slot at all), which ours revived in Wave 1; SVAERA's Phantom Strike carries the `PhantomStrike` abort token (0/8 in ours)
which ours blanked; and ours out-tunes SVAERA on Phantasm/Psionic Beam/Distortion Wave. The one additive delta worth
adopting is `drx_summoncopy` (Summon Copy / Doppelganger, `Skill_SpawnPet`, **no cast anim = safe**) + its pet chain
(`dreamcopypet` + aura + `doppelganger_reflect` + 2 pet passives). It is a genuine 3rd Dream pet (the audit's weak axis).
Port note: remap the copy-pet's difficulty-scaling `skillName10` to our single base `pet_difficultydamagescaling.dbr`
(matching how our Nightmare pet scales) rather than importing SVAERA's epic/leg 3-record chain. Do NOT port
`drx_psionictouch_staffbeammod` (anim `StaffBeam` = 0/8 in ours, and it conflicts with our short-range Psionic Touch rework).

### Runemaster - HYBRID_GRAFT
Both mods have a full DRX Runemaster tree, but **we ship the VANILLA tree (slot 11 -> `RuneMaster_SkillTree.dbr`) with
Wave 1+2 applied as overrides**, whereas SVAERA re-paths every skill to `_drx_*` copies. Wholesale adoption is
DISQUALIFIED: switching to SVAERA's `_drx` tree would strand every existing Runemaster character's invested mastery + skill
points (this is the asymmetry vs the 7 masteries where DRX was always shipped). And ours already wins the tree numbers
(mastery Life/Mana, Guardian-Stone uptime). The genuinely-new content is `_drx_runegolem` (Rune Golem pet) + optional
number buffs (mines/menhirwall) + a defensive mastery tail idea. **HARD HAZARD (D5 invisible pet):** the Rune Golem mesh
`_DRX_Meshes\Xpack2\Pets\runegolem01.msh` lives only in SVAERA's 430 MB `_DRX_Meshes.arc`, which we do not ship (zero
`runegolem` hits in our Resource arcs). Porting the record without extracting the mesh + textures into one of our shipped
mesh arcs yields an invisible pet; must run `validate_render_chain` before shipping. Recommend Rune Golem as its own
follow-up build (see section 5). Do NOT adopt SVAERA's `runecircle` change (it NERFS cd 9->12).

### Neidan - HYBRID_GRAFT (anim-only, effectively keep-ours)
SVAERA brings NO new Neidan skills (27 slots vs vanilla 28; it actually DROPPED `blessjinchan_new_buff`) and its numbers
are vanilla-equal or worse. Our Wave 1+2 dominates every Neidan record (mastery Life 1050 vs 900, Death Bomb chance 45 vs
33, Terracotta petLimit 3 vs 2, our Splash modifier is attached where SVAERA's is still a dead unattached modifier), and
SVAERA's `_drx_neidanmastery` REGRESSES a caster (nerfs INT per level, adds no combat tail). The ONLY SVAERA asset that
helps Neidan is the shared anim-table completion (graft #0): adding the Ensnare melee/spear rows makes Shen Pao and Smoke
Cloud fully castable, and the ThunderClap row helps Chi Realignment. No Neidan skill/pet/mastery record should be ported.

---

## 4) THE COOLEST SVAERA CONTENT WORTH ADOPTING (how it plays)

Ranked by "cool + fills a real gap." All are Atlantis/DRX-native, so they use stock art already reachable through DLC
our mod requires (the two exceptions with a real art dependency are called out).

1. **Storm - Lightning Dash** (`drx_lightningdash`). A lightning blink / gap-closer: +444% run-speed burst that also deals
   lightning damage on the dash. The audit named Storm's #1 gap as "ZERO mobility, no blink/charge," and Wave-1's fix was
   only a weak +10-15% aura rider. This is the on-identity answer Storm always deserved. **No cast animation = the safest
   real skill in the set.**
2. **Defense - Summon Phalanx** (`drx_summonphalanx`). Summons a squad of Spartan phalanx soldiers (base Atlantis pets,
   ~250-525 HP, 80s cd). Gives the pet-less turtle tank a real pet line - the audit's single worst Defense dimension.
3. **Runemaster - Rune Golem** (`_drx_runegolem`). A durable elite rune-construct pet, ~600 HP scaling to ~1950 across 20
   tiers, cd 15s, packing rune-weapon / retaliation / catalyst pet skills. Fills "Runemaster has no durable elite pet."
   Caveat: mesh not shipped, so this one needs a mesh/texture extraction or it is invisible (D5).
4. **Dream - Summon Doppelganger** (`drx_summoncopy`). Summons a Limos-skinned clone of YOU that casts your own Dream nukes
   (Psionic Touch + Psionic Burn + Distort Reality) and carries a damage-reflect passive. A genuine 3rd Dream pet (Dream's
   audited weak axis). cd 140s, ~10-27s life.
5. **Earth - Rupture line** (`drxrupture` + `drxrupture_burning` "Burning Bolts" + `drxrupture_flare`). A weapon-scaled
   ranged-spread earth attack with a fire-burn DoT (roughly +9->42/s over 4s at rank). A spammable weapon/caster hybrid the
   mono-fire Earth tree lacked. No cast anim = safe.
6. **Storm - Frost Nova** (`drxfrostnova`). A radius cold AoE, frostburn plus a ~1.8-2.9s freeze - hard CC Storm can layer
   on top of its petrify. Anim `ThunderClap` (safe on staff; graft #0 covers dual-wield).
7. **Earth - Fire Nova** (`drx_firenova`). A radius-20 fire AoE with a burn DoT (Atlantis nova). Anim `ThunderClap`.
8. **Nature - Earthbind** (`drx_earthbind`). A radius-22 root / immobilize AoE. Fills Nature's thin hard-CC hole and is the
   safest graft of all (anim `Colossus`, 8/8 universal, verified).
9. **Defense - Active Block** (`drx_activeblock`). A "Perfect Block": a ~2s invulnerability window plus a run-speed burst.
   Anim `ShieldSkill02` (casts with a shield equipped).
10. **Warfare - Slam + Fissure + Lasting Legacy** (`drx_clubslam` + `_fissure` + `drx_ancestralmod`). A cyclops-club
    ground-slam wave AoE, a fissure/cooldown modifier, and an Ancestral Horn modifier. Needs graft #0 (Hew melee rows).

**The unsung hero: SVAERA's complete PC animation tables.** Not a skill, but the highest-value adoption. Our
`anm_malepc01` / `anm_femalepc` are a lossy DRX merge (36 distinct tokens) vs SVAERA's superset (42). Grafting the missing
weapon rows back makes these already-shipped skills actually cast: Shen Pao, Smoke Cloud, Chi Realignment (Neidan), Arc
Attack, Exploding Strikes, Hail of Axes (Runemaster), and the new Slam. This is the piece that most directly improves the
play experience, and it is a character-safe additive edit to records we already override.

---

## 5) IMPLEMENTATION PLAN (recommended grafts)

### Ordering
0. **GRAFT #0 - anim-table completion (do first, it is a shared prerequisite).** Edit `records\creature\pc\anm\anm_malepc01.dbr`
   and `anm_femalepc.dbr` (both are already mod-authored overrides in our arz, so this is an EDIT, not a new record). ADD the
   missing paired `SpecialAnim` / `SpecialAnimRef` clip rows, copied verbatim from SVAERA's superset tables (which are the
   same clips as vanilla): Hew -> {dHanded, sHanded, spear}; Ensnare -> {dHanded, sHanded, spear}; Crosscut -> {sHanded,
   spear}; Barrage -> {dHanded}; ThunderClap -> {dHanded}. **ADD ROWS ONLY - never wholesale-swap the table**, because a
   swap would drop the one token OURS carries that SVAERA lacks (`Rest`, used by the Runemaster Rest skill; verified via the
   symmetric-difference read). Blast radius = every mastery, so gate hard: `validate_player_skill_anims.py` + an in-game cast
   test (the B-SOUL-PROC law is a runtime law) + the mandatory Fable-implement / Opus-vet loop.
1. **Anim-safe additive skills, lowest risk first** (append at fresh `skillName` slots on the relevant drx tree, never
   renumber existing slots; assign fresh grid UI coords so new icons do not overlap):
   - Nature Earthbind + nymph Rootwave (Colossus 8/8, pet anim - no #0 dependency).
   - Storm Lightning Dash, Earth Rupture line, Warfare Fissure/Lasting Legacy, Spirit Soul Vortex-if-ever (empty cast anim).
   - Defense Active Block + Summon Phalanx (ShieldSkill02 / CallOfTheHunt present in ours).
   - Earth Fire Nova + Storm Frost Nova (ThunderClap; staff-safe now, dual-wield covered by #0).
   - Warfare Slam (Hew - REQUIRES #0; sequence it after #0 lands and passes the cast test).
   - Dream Summon Copy chain (empty cast anim; remap the copy-pet difficulty scaling to our base record).
2. **Rune Golem - its own follow-up build.** Port `_drx_runegolem` + `runegolem_01..20` + the 3 pet skills as a new
   Runemaster slot, THEN extract `runegolem01.msh` + textures from SVAERA's 430 MB `_DRX_Meshes.arc` into one of our shipped
   mesh arcs and pass `validate_render_chain`. Do not ship it in the same build as the rest; it has a real art dependency and
   a D5 failure mode the others do not.
3. **Optional idea-grafts onto our vanilla-path Runemaster records** (character-safe EDITS, additive levels): mines
   smax/elemental ladder, menhirwall cd/TTL/smax, a DefensiveAbility+Dodge ML tail on OUR `runemaster_mastery` (keep our
   Life 1160 / Mana 400, do not import SVAERA's 800 / 250). Never adopt SVAERA's runecircle cd nerf or its lower Neidan INT.

### Hazards (and how each law is satisfied)
- **Anim tokens (reconciled against bytes):** Slam depends on #0; the ThunderClap novas want the dHanded row from #0 for
  dual-wield; Earthbind/Lightning-Dash/Rupture/Summon-Copy/Fissure/Lasting-Legacy need nothing. Every ported player skill
  must re-pass `validate_player_skill_anims.py` at build time AND an in-game cast test.
- **Existing characters:** every graft is additive (new slots, never renumber; and critically, never swap the Runemaster or
  Neidan tree pointer to SVAERA's `_drx` tree, which would strand invested points). Zero save-state impact.
- **No-removal law:** satisfied. The additive path preserves all original dev work; wholesale SVAERA adoption is precisely
  what would violate it (it would DELETE our Spirit Sands-of-Sleep/Distortion-Wave and regress B1/B2/B3).
- **Occult / Hunting untouched:** none of these grafts touch slots 5/6, their one-hop delegates, or their Text tags, so
  `validate_mastery_golden.py` stays green with no re-baseline (that gate is hard-scoped to Occult/Hunting only). This is the
  proof-of-non-interference for Will's frozen trees.
- **D5 invisible pet:** Rune Golem only (deferred to its own build with a mesh extraction + render-chain gate).
- **FX / Text tags:** most FX/sounds/pets resolve from base xpack3 (Atlantis, already required). A handful must be PORTED and
  added to `validate_tags`: SV-authored tags `tagRuptureNAME` / `tagBurningBoltsNAME` / `tagFlareNAME` (Earth),
  `tagSVAERSkillStorm001` (Storm Frost Nova), 2 Dream Doppelganger tags, plus the 2 Storm Frost Nova FX records. Verify
  Warfare Slam's `tagSlam_*` resolve in base Atlantis Text before assuming a port.

### Gates to run each build
`validate_player_skill_anims.py` (the fourth DB invariant, mandatory here), `validate_tags.py`, `validate_render_chain.py`
(Rune Golem + any touched pet), `validate_summon_pets.py`, `validate_mastery_golden.py` (must stay green = proves
Occult/Hunting untouched), `tools/contracts/run_contracts.py`, a deterministic 2x rebuild + `record_diff.py` vs the prior
arz, and the in-game cast/spawn test. Per the standing rule, commit + tag the build before any "please test."

### Roughly how big a build
- **Main graft build (everything except Rune Golem):** medium and DB-only. Approximately 22-24 skill/pet records + ~10 Text
  tags + the 2 anm-table edits + a couple of FX ports. No mesh work, no map coupling. This is a normal DB wave you can gate
  and ship like Wave 1+2.
- **Rune Golem build (separate):** ~24 records PLUS a mesh + texture extraction from a 430 MB arc and a `validate_render_chain`
  pass. Small record count, but the art step makes it the one heavier, higher-risk item; keep it out of the main wave.

---

## 6) PERMISSIONS NOTE

soa (author of SVAERA / Soulvizier AERA) gave **verbal permission** to reuse his work. Per Will (2026-07-10), quote: "he
said it was cool." When any of these grafts ship, **this permission must be captured in the credits / permissions record.**
`CLAUDE.md` already lists soa as an upstream author for credits + permissions, and `docs/STEAM_RELEASE.md` tracks the
"get written permission from amgoz1, soa, Dragonlord" release blocker. Recommendation: record the soa grant (date, scope,
"verbal - Will relayed 2026-07-10") in the permissions doc alongside the amgoz1/Dragonlord entries, and, because the Workshop
listing benefits from a durable paper trail, follow up for a written confirmation (forum PM / Discord message) to attach to
the release record. The grafts themselves are additive reuse of soa's SVAERA content on top of our tuned trees, which is
squarely within the "reuse his work" grant.

---

*Byte-level probes for this synthesis (throwaway, under the OS temp scratchpad): `anm_probe.py` (our per-weapon-row token
coverage), `svaera_probe.py` (SVAERA graft-source coverage + candidate existence + anim/class), `anm_diff.py` (token
symmetric difference). Lane dumps: `svaera_mastery_dumps/*.json` and `svaera_probe/*` under the same temp root.*
