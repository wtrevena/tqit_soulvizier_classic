# b40 - ENSLAVER FX (all-black) + LOOT

Branch `feat/b40-enslaver-fx-loot` (base da918c5 = build38a-dev). DB/registry lane, no heavy
build (dry-run replay against a copy of `scratchpad/baseline_build38.arz`, arz md5 `fcd5dcab`).
Module: `tools/patches/enslaver_fx_loot.py` (new registry entry, after `toxeus_suite`).

## Will's order (2026-07-13, with a pink-circled screenshot of the Enslaver + his demons)
1. (a) the demons he SUMMONS are GREEN -> make them BLACK
2. (b) the Enslaver himself has BOTH green AND black smoke -> make it ALL black
3. (c) give the Enslaver really GOOD ITEMS, tiered across Normal/Epic/Legendary
4. (d) give the summoned demons GOOD WEAPONS too

Scope: `um_toxeus_enslaver_99` (roaming boss) + `um_enslaver_marauder_99` (his HOSTILE
summoned marauder). The **Devourer** (`um_bloodtoxeus_99`) crimson is a SEPARATE record and
is preserved untouched (TOXEUS LORE LAW).

---

## FX ROOT-CAUSE ANALYSIS (proven from the arz + DXT-sampled shipped textures)

Every FX field on both records was enumerated (`tools/debug/b40_probe_enslaver_fx.py`), every
referenced skill/pak chased, and the referenced `.tex`/`.pfx` colour-sampled from the shipped
`Resources` (`tools/debug/b40_tex_bright.py`, DDS `DDSR` decode).

### The b38 dark-smoke was correct but INCOMPLETE
b38 added `charFxPakRunningNames = svc_enslaver_darksmoke_charfxpak` (-> `343_dark_smoke`) on the
boss. That field renders **only while the character is RUNNING**. When the boss stands still there
is no shroud, so any residual green shows. It is also on the boss ONLY, not the marauders.

### BOSS `um_toxeus_enslaver_99` - body is already black; the green is the demons + idle gap
- `mesh = RevenantPoison.msh` is **StandardSkinned (NO glow shader)**; `baseTexture =
  NewSkeleton_Charcoal.tex` (resolves, dark). So the boss BODY is black. There is **no
  green-producing FX on the boss's own record** (kit skills all clean; `initialSkillName` was
  already deleted in b36; the `character_speedall` aura's `343_AlacrityAuraFX.dbr` record is
  **absent from the arz** -> renders nothing).
- The green Will sees on/around the boss is (1) the ever-present swarm of GREEN marauders he
  summons at 70% cast, and (2) the idle gap the running-gated b38 smoke leaves.

### MARAUDER `um_enslaver_marauder_99` - TWO confirmed green sources
1. `charFxPakRunningNames = drxshadowcloakrunning_fx_pak` -> a lightning/bolt weapon-energy trail;
   its `lightning_missile01b.tex` has **PURE-GREEN texels (8,252,0)**.
2. `ShadowStalker.msh` uses the **StandardBlendedGlowSkinned** shader with glow map
   `ShadowStalker01Glow.tex`, whose bright emissive spots are **green-cyan (0,184,176)**. The
   marauder set NO `baseTexture`, so it renders the default skin + this green glow.

### Why the Devourer (same-family) reads crimson and stays untouched
`um_bloodtoxeus_99` is on the SAME RevenantPoison rig but reads crimson because it wears a crimson
skin AND runs a PERSISTENT self-aura: `initialSkillName = bloodtoxeus_envenomweapon` (a
`Skill_BuffSelfToggled` with `charFxPakSelfNames = charfxpak_leinth_aura`, auto-cast on spawn,
always on). That is the proven pattern this fix reuses (in black).

Key constraint: `charFxPakSelfNames` is **zero-precedent on Monster records** (0 of 51007) - so we
do NOT add it to the monster (that field family was a build28 loadability suspect); we use the
base-game/Devourer route (a buff skill in the monster's kit).

---

## THE FIX (`tools/patches/enslaver_fx_loot.py`)

### FX - all black
- **`svc_enslaver_darkaura`** = `clone_record(bloodtoxeus_envenomweapon)` with
  `charFxPakSelfNames` repointed to the b38 dark-smoke pak. The donor is a pure-FX
  `Skill_BuffSelfToggled` (every offensive/defensive stat 0, no `weaponEnchantment`), so the clone
  is just a persistent black-smoke self-aura. Registered in `_BOSS_KIT_CLONES` (clone-shape gate).
- **Boss**: `initialSkillName = svc_enslaver_darkaura` + appended to a free kit slot -> the black
  smoke is now ALWAYS on (idle + moving). The b38 running smoke is kept.
- **Marauder**: `charFxPakRunningNames` green shadowcloak **-> the dark-smoke pak** (kills the
  green weapon-energy trail); `baseTexture` **-> `SVTextures\creatures\shadowstalker\wahr.tex`**
  (SV 0.98i's own dark, non-green shadowstalker skin: base 17,11,54 + paired `wahrglow` 19,2,57,
  greenest +4 -> not green); same persistent dark aura auto-cast.

The marauder skin swap is how the emissive green glow is addressed - an emissive glow shows THROUGH
smoke, so masking alone cannot kill it. The mod's own **Endless Hunt** already recolours this exact
mesh via `baseTexture` (`shadowstalker_iceheart`), so `baseTexture`-driven recolour is the
established pattern.

### LOOT (c) - guaranteed tiered unique hoard
The boss already drops the apex boss-orb chest (`treasureProxyName genericbossorb_04`) + its soul
(Finger2 @66%) + potions/relics/amulet (`lootMisc1-3`). Added a GUARANTEED signature drop the
mod-standard way (per-tier `LootItemTable_FixedWeight` -> a free `lootMisc` slot, pointing at
mastertable POOLS so the engine rolls a properly-affixed unique at kill-time - **no hand-placed
fixed item that "bakes badly"**):
- `svc_enslaver_hoard_{n,e,l}` = 7 unique mastertable pools each (unique 1H weapon + amulet + ring
  + torso/head/arms/legs unique) -> the boss's FREE `lootMisc4 @ 100%`.
- Tier quality scales automatically (`unique_1h_n01/e01/l01`, etc.).

### LOOT (d) - good marauder weapons
The marauder already equips `dyn_1h`/`unique_1h` mastertables but the unique weight was a token
`4/5004` (~0.08%). Rebalanced the wield choice to **2500/2500 (~50% unique)**. It is a **Monster**
(not a Pet) so normal equip fields are crash-safe. `dropItems` stays **0** - a transient summon
must never drop loot (infinite-summon exploit); "good weapons" = they WIELD good weapons.

---

## DRY-RUN VERIFICATION (`scratchpad/replay_enslaver_fx_loot.py`, no heavy build)

Load a copy of `baseline_build38.arz` -> run `apply()` + `verify()` -> enumerate before/after.

**FX before -> after**

| field | boss before | boss after | marauder before | marauder after |
|---|---|---|---|---|
| `initialSkillName` | (none) | `svc_enslaver_darkaura` | (none) | `svc_enslaver_darkaura` |
| `charFxPakRunningNames` | darksmoke (b38) | darksmoke | **shadowcloak (GREEN)** | **darksmoke** |
| `baseTexture` | charcoal | charcoal | (none/green glow) | **wahr (dark)** |
| aura `charFxPakSelfNames` | - | `-> 343_dark_smoke` | - | (same aura) |

**LOOT** - `lootMisc4` None -> `100%` -> `[hoard_n, hoard_e, hoard_l]`; all **21 unique pools
(7 x 3 tiers) RESOLVE**. Marauder `RightHandItem5` `4 -> 2500` (unique weight).

**CRASH-LAW proofs (all OK)**
- aura `Class = Skill_BuffSelfToggled` (NOT a SpawnPet class)
- `svc_enslaver_summonmarauders` (the SpawnPet skill) carries **no** `charFxPak*` field
- no `clone_record` on a soul (aura is a skill clone; loot tables via `_ensure_record`)
- no Monster.tpl -> Pet.tpl equipment copy (marauder is a Monster; weapon bump on its own record)
- Devourer `baseTexture` still `newskeleton_crimson.tex` (preserved)
- marauder `Class = Monster`, `dropItems = 0`

**A9 asset resolution (shipped Resources)** - `wahr.tex` RESOLVES; the dark-smoke pak ->
`343_dark_smoke` -> `SVEffects/ambient/dark_smoke.pfx` RESOLVES.

**Gates**: module `verify()` PASS; monolith `_verify_boss_kit_clone_shape` OK (aura clone keeps
donor shape); `_verify_boss_orbs` OK. Negative test (`scratchpad/negtest_enslaver_fx_loot.py`) -
the gate FAILS LOUD on each of 5 injected defects (non-vacuous). `py_compile` OK;
`tools/patches/_check_registry.py` OK (12 modules).

---

## FLAGGED FOR WILL'S IN-GAME CHECK (cannot be render-tested at build time)
1. **Marauder final colour.** The `wahr` skin + killed green trail + black aura should read as a
   dark shadow demon (blue-purple), definitively not green. IF the engine keeps the mesh's green
   emissive glow regardless of `baseTexture` (contrary to the Endless-Hunt precedent), the residual
   would be faint green glow spots - fallback is a one-line `baseTexture` revert (the shadowcloak
   ->smoke + aura fixes stand on their own). Confirm the marauders read dark/black.
2. **Boss idle shroud.** Confirm the persistent black aura removes any idle green and the boss reads
   solid black (his body was already charcoal; this closes the running-gated gap).
3. **Loot generosity.** `lootMisc4 @ 100%` = one guaranteed unique per kill on top of the orb + soul.
   He is a roaming rare (~once/act), so this is act-boss-tier. Dial `chanceToEquipMisc4` down if too
   generous.

## OUT OF SCOPE / FOLLOW-UP (documented, not done)
- The **friendly pet-of-pet marauders** (player's Enslaver-soul summon: `enslaver_marauder_1/2/3`)
  share the ShadowStalker rig and would also be green. They are Pet.tpl (crash-law sensitive) and
  built by the monolith BEFORE this registry module runs, so they are untouched here. If Will wants
  his summoned pack black too, mirror the marauder skin/FX onto those pet records (animation/FX
  fields only) in a monolith edit - a separate, carefully-gated change.

## Files
- `tools/patches/enslaver_fx_loot.py` (new module), `tools/patches/__init__.py` (REGISTRY += 1).
- `tools/debug/b40_probe_enslaver_fx.py`, `b40_probe_fx_resolution.py`, `b40_mesh_skin_probe.py`,
  `b40_boss_full.py`, `b40_aura_glow_probe.py`, `b40_tex_color.py`, `b40_texhdr.py`,
  `b40_tex_bright.py`, `b40_skin_scan.py`, `b40_skin_scan2.py`, `b40_loot_probe.py`,
  `b40_loot_slots.py`, `b40_aura_candidates.py` (read-only RCA probes).
- Scratchpad (analysis only, not shipped): `replay_enslaver_fx_loot.py`,
  `negtest_enslaver_fx_loot.py`.
