# b83 - THE DEVOURER'S BLACK POISON + THE RITE OF THE UNDIVIDED DROP

Branch `feat/black-poison` (merge of vetted `feat/toxeus-champions` + `feat/toxeus-undivided`,
merge commit `2f52507`). Ground truth: build45 arz md5 `917d9047` (read-only reference).
Will rulings 2026-07-16 (verbatim):

- **R-1 (black poison):** "we have wanted the devourer to have a literal black poison asset from
  the beginning and use that all along, idk what we hvae been doing, that is how we were going to
  replace the green poison effect that he had was make a black one and wire it in".
- **R-9 (Rite pool drop):** "let the Rite of the Undivided drop wherever else any supra / uber
  weapons formulas have a chance to drop".
- **R-13 (Rite boss-kill drop):** "also make it so if you kill either toxeus the devourer of blood
  of toxeus the enslaver of souls you also get the formula".

## ROUND 2 - vet resolution (the three findings)
- **HIGH (green survives on the summoned Devourer) - FIXED.** The soul-pets `bloodtoxeus_1/2/3` carry
  a LIVE `buffSelfSkillName = records\skills\stealth\envenomweapon.dbr` (base GREEN, tint
  (0.25,1.0,0.25)) that auto-fires on summon; round 1 rewired only `skillName3` and left it green.
  `_rewire_devourer` now also repoints the 3 pets' `buffSelfSkillName` -> `svc_black_poison`, and
  `black_poison.verify` now asserts `buffSelfSkillName` on all 3 pets (fails on crimson OR base-green).
  Round-2 changed-arz md5 `497073d1...`; diff vs round-1 = exactly those 3 fields, nothing else.
- **MEDIUM (343_dark_smoke provenance overstated) - FIXED.** The docstring/report no longer call the
  particle "proven/confirmed-dark"; it is stated as NOT colour-confirmed (rule 3), flagged BP-SMOKE-1,
  with the tint as the independent load-bearing black.
- **LOW (drop-weight "~2%" imprecise) - FIXED.** S4 now carries the decoded per-act supra weight table
  (1-5 by act/difficulty), not a flat 2.

---

## 1. THE EMPIRICAL TINT MODEL (field -> colour, proven from 394 tinted weapon buffs)

`skillWeaponTint{Red,Green,Blue}` are **additive emissive glow multipliers** on the weapon mesh.
Proven by scanning every record carrying a `skillWeaponTint*` field in the golden build45 arz
(`local/tint_scan.py`, 394 records):

| (R,G,B)            | count | example                        | reads as        |
|--------------------|-------|--------------------------------|-----------------|
| **(0.0,0.0,0.0)**  | 195   | alastor_circleofdecay          | **NO TINT** (off) |
| (1.0,0.1,0.0)      | 75    | seductress_conversionaura      | orange/fire     |
| (0.9,0.1,1.0)      | 32    | petskill_skelmfireeffect       | magenta         |
| (0.25,1.0,0.25)    | 30    | **base green envenom**         | GREEN           |
| (1.0,0.0,0.0)      | 27    | rustaurabuff                   | red             |
| (0.0,0.3,0.8)      | 2     | coldmastery_froststrike        | blue            |
| (0.4,0.0,0.8)      | (1)   | lightningmastery_stormstrike   | purple          |
| (1.0,0.25,0.25)    | 2     | **bloodtoxeus_envenomweapon**  | CRIMSON (Devourer) |
| (0.0,1.0,0.0)      | 1     | necrevivedebuff                | pure green      |
| **(0.1,0.1,0.1)**  | 1     | **hero_shadowenchantmentbuff** | **near-black / shadow** |

**Decisive conclusions:**

1. **(0,0,0) is the inert "no tint" default (195 records)** - a zero channel is OFF, not black.
   So the channels are **additive-only**: you cannot emit *black light*. **Literal-black IS
   UNREACHABLE via the tint channel** (exactly the case R-1's brief anticipated).
2. The green marker Will hates is `skillWeaponTintGreen=1.0` (base envenom (0.25,1.0,0.25)); the
   Devourer's round-1 crimson was (1.0,0.25,0.25).
3. The **darkest RENDERABLE non-zero tint in the whole DB is (0.1,0.1,0.1)**, shipped on the
   real, in-engine `hero_shadowenchantmentbuff` **shadow enchantment**. This is the near-black
   "shadow" register the engine actually draws, and it is a **direct engine emissive parameter
   (not a baked .pfx)**, so it renders dark/charcoal deterministically - never green, never crimson.

The "green poison effect" is two things on the base envenom: the green **tint** AND the green
weapon **charFxPak** (`343_weapon_poisoncharfxpak` -> `343_Weapon_PoisonFX`, attached to R/L Hand).
Both are green; both must be neutralized.

---

## 2. THE BLACK COMPOSITION (svc_black_poison)

New record `records\skills\monster skills\buff_self\svc_black_poison.dbr`, cloned from the
Devourer's own crimson `bloodtoxeus_envenomweapon` (his lineage, his-tier poison payload), then:

| field                              | crimson donor                | svc_black_poison            | why |
|------------------------------------|------------------------------|-----------------------------|-----|
| skillWeaponTintRed/Green/Blue      | 1.0 / 0.25 / 0.25            | **0.1 / 0.1 / 0.1**         | the shadow-enchant-proven darkest RENDERABLE tint (grounded near-black; kills green + crimson) |
| charFxPakSelfNames                 | charfxpak_leinth_aura (crimson) | **svc_black_poison_charfxpak** | black-smoke weapon drip (see below) |
| offensiveSlowPoisonMin / dur       | 90 / 5s                      | 90 / 5s (kept)              | his-tier poison, preserved |
| offensiveSlowTotalSpeedMin / dur   | 33 / 5s                      | kept                        | envenom slow, preserved |
| offensiveSlowLifeMin / dur         | -                            | **60 / 5s (added)**         | black vitality-decay DoT -> "poison/vitality" |

`svc_black_poison_charfxpak` (new, CharFxPak.tpl) mirrors the green weapon-poison pak's structure
(`particleEffectAttachPoints = ['R Hand','L Hand']`) but swaps the green `343_Weapon_PoisonFX`
particle for `343_dark_smoke` (`SVEffects/ambient/dark_smoke.pfx`), the same dark-smoke FX the
Enslaver ENCOUNTER rig uses (`svc_enslaver_darksmoke_charfxpak`). **This particle's real in-game
colour is NOT confirmed** - CLAUDE.md rule 3 names `343_dark_smoke` the "renders-green lesson" asset,
and the b55 source that introduced it hedges ("please confirm in-game whether the dark smoke
renders", data-only confidence). It is used here as the intended black-drip layer but its
black-vs-green render is an explicit Will in-game check (BP-SMOKE-1), NOT a proven claim. The
load-bearing black is the tint, which is independent (see below).

### How black is achieved (2 sentences)
Black is carried primarily by the weapon **tint set to (0.1,0.1,0.1)** - a direct engine emissive
parameter identical to the shipped `hero_shadowenchantmentbuff` shadow enchantment, empirically the
darkest renderable value (literal-black light is unreachable because the tint channels are
additive-only, proven by the 195 (0,0,0) "no-tint" records), so it draws a dark/charcoal glow that
is never green or crimson. On top of that a new weapon char-fx pak drips **`343_dark_smoke`** from
both hands (the same dark-smoke FX the Enslaver encounter uses; its render is NOT colour-confirmed, flagged BP-SMOKE-1) as the "black
poison" particle layer.

### PLAYER-SURFACE FLAG (rule 3, the 343_dark_smoke renders-green caution) - WILL IN-GAME CHECK
The **particle's** final black-vs-green render is a Will in-game colour check (CLAUDE.md rule 3 cites
a "343_dark_smoke renders-green lesson"). The **load-bearing black does NOT depend on the particle**:
if the smoke reads green in-game, the fix is a one-line pak swap (or clearing `charFxPakSelfNames`
-> tint-only black) and the (0.1,0.1,0.1) shadow-glow black still stands. Registered in the BACKLOG
DEBT section.

---

## 3. BEFORE / AFTER - the Devourer + EoAT poison surface

The Devourer poison surface carries TWO distinct envenom weapon-buffs: the crimson
`bloodtoxeus_envenomweapon` (skillName3 / initialSkillName) AND the base GREEN
`records\skills\stealth\envenomweapon.dbr` (tint (0.25,1.0,0.25)) that the soul-pets AUTO-fire via
`buffSelfSkillName` on summon. **Both** must go black or the summoned Devourer keeps glowing green.
Full surface (8 field rewires + the 6 EoAT-family flips downstream):

| record                                   | field(s)                    | before                      | after            |
|------------------------------------------|-----------------------------|-----------------------------|------------------|
| um_bloodtoxeus_99 (fought Devourer)      | initialSkillName, skillName3| bloodtoxeus_envenomweapon (crimson) | **svc_black_poison** |
| bloodtoxeus_1 / _2 / _3 (soul pets)      | skillName3                  | bloodtoxeus_envenomweapon (crimson) | **svc_black_poison** |
| bloodtoxeus_1 / _2 / _3 (soul pets)      | **buffSelfSkillName**       | **envenomweapon (base GREEN)** | **svc_black_poison** |
| toxeus_eoat_1 / _2 / _3 (EoAT pets)      | buffSelfSkillName           | bloodtoxeus_envenomweapon (crimson) | **svc_black_poison** |

> **ROUND-2 FIX (vet HIGH):** round 1 rewired only the pets' `skillName3` and left
> `buffSelfSkillName = envenomweapon` (base GREEN) live on `bloodtoxeus_1/2/3`, so the
> player-summonable Devourer soul-pet still auto-self-buffed a green weapon glow (tint (0.25,1.0,0.25))
> on summon - defeating R-1 on the summoned Devourer. `_rewire_devourer` now also repoints
> `buffSelfSkillName` (base green -> black) on all three soul-pets, and `black_poison.verify`
> asserts `buffSelfSkillName` on the three pets (fails on either crimson OR a surviving base-green
> `envenomweapon`), so the gate can no longer pass green.

His crimson **identity is untouched** (Will: "only the POISON goes black"): `newskeleton_crimson`
skin, `melinoe_bloodboil` nova, the leinth blood aura on his monster record - all preserved.

The EoAT module's `_BLACK_POISON` const now names `svc_black_poison`; its pet verify asserts the
buff **is** svc_black_poison (not crimson, not any envenom variant). The black_poison module is
registered **before** toxeus_endofallthings so the skill exists when EoAT references it and the
Devourer soul-pets are rewired before EoAT clones them.

**Gate safety:** the b55 `enslaver_pet_fx` green marker for `buffSelfSkillName` is the substring
`'envenom'` (excluded only for `'bloodtoxeus'`). The record is named `svc_black_poison` (no
`'envenom'` substring), so it is transparently clear of the green marker.

---

## 4. THE RITE DROP - formula-drop source table + wiring

### Where the supra/uber weapon formulas drop (ground truth)
The 24 supra weapon/armor formulas (`drxitem\supra\recipes\wep_*_formula`, `ar_*_formula`,
`ring/neck/staff_*_formula`) are pooled in **two `LootItemTable_FixedWeight` tables**, each entry
weight 100:

- `records\xpack\item\loottables\arcaneformulae\supra.dbr`
- `records\xpack\item\loottables\arcaneformulae\supra_special.dbr`

Those two pools are reached by the per-difficulty/per-act **`LootMasterTable`s**
`0X_actY_arcaneformulae.dbr`, where `supra.dbr` sits as the rarest child. Its **weight varies by
act/difficulty** (decoded from the golden arz, NOT a flat 2) - it is the low-weight rare tail
everywhere, climbing on later Legendary acts:

| parent LootMasterTable                | supra child weight |
|---------------------------------------|--------------------|
| `02_act1` / `02_act2` (Epic)          | **1** |
| `02_act3` / `02_act4` (Epic)          | **2** |
| `03_act1` (Legendary)                 | **2** |
| `03_act2` (Legendary)                 | **3** |
| `03_act3` (Legendary)                 | **4** |
| `03_act4` (Legendary)                 | **5** |
| `03_act4_arcaneformulae_sp` -> `supra_special.dbr` | **5** |

(These parents pool the supra child against a `..._table` of common formulas at much higher weight,
so the supra tier is the rare tail in every act - roughly 1-5% depending on act/difficulty.)
Monsters/chests reach these via their `lootMisc2Item2` = `[01/02/03_act1_arcaneformulae]` slots.
**The b66 `uber_orphan_weapons` module is the precedent: it wires every NEW supra weapon formula
into BOTH `supra.dbr` and `supra_special.dbr` at the next free `lootName` slot, weight 100.**

### R-9 implementation
The Rite formula item `records\drxitem\supra\recipes\svc_toxeus_eoat_formula.dbr` (built by the EoAT
module) is added to **BOTH `supra.dbr` and `supra_special.dbr`** at the next free `lootName` slot,
weight 100 (identical b66 mechanism + `_next_loot_slot` helper). It therefore drops **wherever any
supra weapon formula drops**, at that same rarest formula tier (the low-weight supra tail, ~1-5% by
act/difficulty per the table above) - and inside the pool it is one of 25 equal-weight entries. Runs
after `uber_orphan_weapons` so the two modules' appends do not collide.

### R-13 implementation (GUARANTEED on-kill on both bosses)
Boss-loot convention (decoded from the Devourer's own guaranteed drops): a named equip/Misc slot
with `chanceToEquip<Slot>=100` + `loot<Slot>Item1` -> a table that always yields the item (e.g. the
Devourer's `crimsonverdict_guaranteed` on RightHand, and the `toxeus_rant_perplayer` on Misc4).

- New `svc_rite_guaranteed.dbr` (FixedWeight, lootName1 = the Rite @ 100) = always the Rite.
- **Enslaver** (`um_toxeus_enslaver_99`): its Misc4 slot is FREE (Misc4 is a proven slot used by 29
  monsters) -> `chanceToEquipMisc4=100`, `lootMisc4Item1 = [svc_rite_guaranteed]x3`.
- **Devourer** (`um_bloodtoxeus_99`): Misc4 is occupied by the rant (`toxeus_rant_perplayer`, 100%).
  New `svc_devourer_misc4_master.dbr` (LootMasterTable) yields BOTH the rant (w100) AND
  `svc_rite_guaranteed` (w100) - a LootMasterTable rolls each child independently at
  weight-as-percent, so both always drop. The Devourer's `lootMisc4Item1` is repointed to it; **the
  rant is preserved verbatim inside it**.

**Soul drops untouched:** the Enslaver soul (Finger2 = enslaver_soul_n/e/l) and Devourer soul
(Finger2 = blood_toxeus_soul_n/e/l) slots are not modified (asserted in the EoAT verify).

### Where the Rite drops (1 sentence)
The Rite drops **wherever any supra weapon formula drops** (added to both the `supra.dbr` and
`supra_special.dbr` formula pools at the rarest supra tail, ~1-5% by act) AND is a **guaranteed 100% on-kill drop
on both Toxeus bosses** (Enslaver via a free Misc4 slot, Devourer via a rant+rite master table that
preserves his existing rant).

### WILL-VETO (balance tension, shipped per Will's plain reading)
R-13 mandates 100% on-kill. The Toxeus bosses are roaming rares (repeat-killable / farmable), so a
guaranteed apotheosis-formula drop is farmable (though crafting the EoAT soul still requires the 3
Legendary Toxeus souls). Shipped at 100% per R-13's plain reading; flagged WILL-VETO in the BACKLOG
DEBT section in case Will wants a first-kill-only or reduced-chance variant.

---

## 5. CROSS-BRANCH INTEGRATION FIX (first build of the merged champions+EoAT state)

The first DB build of the merged state crashed in the pre-existing gate
`_verify_soul_itemskill_activation` with `KeyError: 'records\skills\soulskills\pets\eoat_disciple_1.dbr'`
inside the shared record index (`_RecordIndex.find_first_substr`).

**Root cause (latent, exposed by the merge):** `_RecordIndex.name_lower` is an append-only cache
that is never pruned. `_sync_names` only repopulated it `if len(nl) != n`, but always set
`self.order = names`. When finalization deletes records and later modules add an equal number back,
the record count can COINCIDE with `len(nl)` while the name SET differs - the guard then skipped
adding the genuinely-new names (`eoat_disciple_*`) to `nl` while `order` already held them, so the
lookup KeyErrored.

**Fix (`tools/apply_svc_patches.py`, build-time lookup only - changes ZERO output records):**
reconcile every current name into `nl` unconditionally on a count change (cheap: `not in` skips
cached names), plus a self-healing `nl.get(name)` in `find_first_substr` so a missing name can never
KeyError. Documented here; verified by the clean re-build.

---

## 6. VERIFICATION

> **ROUND 2 (vet HIGH fix - the pets' green `buffSelfSkillName`):** rebuilt fresh with the extended
> `_rewire_devourer` (pet `buffSelfSkillName` base-green -> black) + extended `black_poison.verify`.
> New changed-arz md5 **`497073d10041a9d38e553a2ab708f206`** (`local/bp_changed_r2.arz`). Deltas below
> are updated for round 2; the round-1 figures (`32e0f2f7...`) are superseded.

- **Full scratch build on the merged branch** (round 2, with the HIGH fix): `local/bp_changed_r2.arz`
  md5 **`497073d10041a9d38e553a2ab708f206`**. All in-build invariants + the 29-module registry
  verifies GREEN, incl. the extended `black_poison.verify OK` ("Devourer fought-monster
  (initial+skillName3) + 3 soul pets (skillName3 crimson + buffSelfSkillName GREEN) all repointed to
  black; zero green/crimson tint OR envenom self-buff survives") and `toxeus_endofallthings.verify OK`;
  Occult/Hunting golden freeze guard `RESULT: PASS` (84 waived, 0 other).
- **Clean pre-change merged-state build** (content OFF, ridx infra fix ON): `local/bp_clean.arz` md5
  **`532003ecc70dfbcc3dadf9796cba1d81`**, golden guard PASS (unaffected by round 2 - the clean
  baseline is content-OFF, so my content-module edit does not change it; reused as-is).
- **Record-diff vs round-1 changed** (`local/diff_bp.py bp_changed.arz bp_changed_r2.arz`): **exactly
  3 CHANGED, 0 added/removed** = `bloodtoxeus_1/2/3` `buffSelfSkillName` `envenomweapon` (base green)
  -> `svc_black_poison`. Nothing else - the round-2 fix is surgically the HIGH and only the HIGH.
- **Record-diff vs CLEAN baseline** (`local/diff_bp.py bp_clean.arz bp_changed_r2.arz`): **exactly 17
  delta records, zero collateral** = 4 ADDED (svc_black_poison, svc_black_poison_charfxpak,
  svc_rite_guaranteed, svc_devourer_misc4_master) + 13 CHANGED (um_bloodtoxeus_99
  initialSkillName/skillName3/Misc4; **bloodtoxeus_1/2/3 skillName3 AND buffSelfSkillName** [round 2];
  toxeus_eoat_1/2/3 + eoat_disciple_1/2/3 buffSelfSkillName crimson-> svc_black_poison;
  um_toxeus_enslaver_99 Misc4; supra.dbr + supra_special.dbr Rite append). Nothing else.
- **Contracts** (`tools/contracts/run_contracts.py --only souls,summons,resources`): the round-2 build
  and the round-1 build give **identical totals** (19196 violations, 99 P0 / 7259 P1 / 11838 P2 - all
  pre-existing ported-monster mesh/skill false positives from not passing `--resource-arc-dir`).
  **ZERO new violations from this change**; none of the 4 new records NOR the 3 rewired pets is
  flagged. Map/Quests/Levels are **byte-untouched** (DB-only change), so the map contract is unaffected.
- **Negative test** (`local/negtest_bp.py bp_changed_r2.arz`): `black_poison.verify` PASSES on the
  built arz; planting a green tint (skillWeaponTintGreen=1.0) on svc_black_poison makes it correctly
  FAIL. **PLUS a targeted round-2 negative test** (the exact blind spot the vet found): planting the
  base-green `envenomweapon` back on `bloodtoxeus_1.buffSelfSkillName` makes `black_poison.verify`
  correctly FAIL ("bloodtoxeus_1.dbr.buffSelfSkillName still base GREEN envenom (the summoned-Devourer
  glow bug)"). The gate can no longer pass green on the pet self-buff. NEGTEST PASS.
- **Idempotent / deterministic**: a second full build of the round-2 changed state
  (`local/bp_changed_r2b.arz`) reproduces md5 `497073d1...` byte-for-byte; the modules use collision
  guards + an idempotent pool append (skip-if-listed) and no randomness. (Round 1's determinism was
  also independently reproduced byte-identical by the adversarial vet across 3 builds.)

## BACKLOG DEBT (open, registered at commit)
- **BP-SMOKE-1 (P2 visual, Will in-game check):** the `343_dark_smoke` weapon particle's final
  black-vs-green render must be confirmed on Will's screen (rule 3 caution). Tint-black is grounded
  and independent; one-line fallback documented.
- **BP-RITE-VETO (balance, WILL-VETO):** the Rite is a 100% on-kill drop on two farmable roaming-rare
  bosses. Confirm 100% (vs first-kill-only / reduced) is intended.
