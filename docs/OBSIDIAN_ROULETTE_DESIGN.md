# OBSIDIAN HALLS TREASURE ROULETTE - approved design (2026-07-09)

> Design round 2 by the Obsidian design agent (source transcript: session task
> ad07cc8ed30623d82). WILL SIGNED OFF 2026-07-09 with these DECISIONS LOCKED:
> - chanceToRun = 25.0 per corner proxy
> - Voranthys summon-soul APPROVED: the ONE summon of the four souls, manual-cast
>   summon_voranthys via _build_boss_summon, SepulchralWyrm01 rig
> - ALL designer defaults accepted: mega-chest ornate hoard (locked=1,
>   LockedClassification=Boss, LockedRadius=50), 5-elite random warbands,
>   duplicate guardians acceptable, NO charm (section 5 = DROP stands),
>   Sarkoth soul grants pcsafe typhon_meteorstorm at levels 2/3/4
> - TRAIN: BUILD32 (with Mastery Wave 2; build31 is at capacity)
> - Map-side (4 INJECT_SPECS + the shared v0e branch) = map lane M10; the DB
>   records MUST land in the build32 arz FIRST (MAP-REF-1 ordering)
> - Gates: the design's full list + the NEW accessory-chain-resolves gate +
>   chest-lock-classification==Boss check + ondeath resolution; anim flag
>   DropProjectileTelekinesis on the liche rig = in-game confirm on Will's DEV pass
> - Souls drop at 66% via Finger2 (SVC_RELEASE_DROPS standard)


# OBSIDIAN HALLS TREASURE ROULETTE - design round 2 (for Will's sign-off)

Location CONFIRMED: the Act 3 Obsidian Halls, `levels/world/orient/typhonug/tombobs01.lvl` + `tombobs02.lvl`. Everything below re-verified against the built `.arz` (50,446 records) and the shipped canonical map this session.

## 1. THE EVENT MECHANISM - one proxy, one roll, whole ensemble (byte-proven)

The engine couples boss + warband + chest **natively, in a single record**. No paired-proxy desync problem exists at all:

- **`Proxy.tpl` carries BOTH monster pools AND container accessories.** DB-proven: **1,819 shipped proxies** carry `pool1` + `accessory1` together (e.g. `beast_hydradon_02n`: `pool1` = hydradon monster pool, `accessory1/Epic1/Legendary1` = bone-pile container accessory pools per difficulty). One proxy instance spawns its monsters AND its fixed items.
- **The chest chain (TutorialPotionChestProxy, fully decoded):** `Proxy` (`chanceToRun=100`) -> `accessory1` -> `ProxyAccessoryPool` (`fixedItemChance=100`, `fixedItemName1`) -> `FixedItemContainer`. The DRX golden chests in these very halls already ship this exact chain (`chest_goldenchest_normal_03` -> `poolchest_01/02/03` -> `goldenchest_01_normal/02_epic/03_legendary` per difficulty).
- **`chanceToRun` is THE roulette dial, and it is native to this exact region:** the halls' own trash proxies ship at `chanceToRun` 5 / 15 / 25 (`ug_undead_liche_01n/02n/03n`, `area007 - tomb`). Our mod already ships a working 50% (`q_bloodtoxeus_lone_50`, D7). It re-rolls each session, so the roulette re-shuffles every run.
- **THE KILLER DETAIL - chests lock until the guardian dies:** `FixedItemContainer` supports `locked=1` + `LockedClassification` + `LockedRadius`. The DRX golden legendary chest ships `LockedClassification=Boss, LockedRadius=50`; the blood-cave mega chest ships `Champion/60`. Our hoard chest is `locked=1, LockedClassification=Boss, LockedRadius=50`: it spawns WITH the ensemble but cannot be opened until the Boss-class guardian within 50u is dead. Guarded treasure, engine-native, zero quest logic.

**Per-corner ensemble record set (per corner: 1 proxy; shared: 1 pool + 3 chests + 3 accessory pools):**

```
q_obs_roulette_{a,b,c,d}.dbr          (Proxy, Proxy.tpl)
  chanceToRun        = 25.0                     <- the roulette (flag: Will picks)
  pool1              = pools\q_obs_warband.dbr  <- SHARED across all 4 corners
  accessory1         = svc_obsidianhoard_pool_01.dbr   (normal)
  accessoryEpic1     = svc_obsidianhoard_pool_02.dbr
  accessoryLegendary1= svc_obsidianhoard_pool_03.dbr
  difficultyEquationFile = records\proxies orient\difficulty_04.dbr
  difficultyLimitsFile   = records\proxies orient\limit_obsidianbosses.dbr  (no-cap clone, window [1..110])
  placementExtents   = 4.0

pools\q_obs_warband.dbr               (ProxyPool.tpl)  - THE SHARED ROULETTE POOL
  spawnMin = spawnMax = 6
  championChance = 100.0, championMin = championMax = 5     <- 6-5 = 1 main slot: the LAW holds
  name1..4      = the 4 guardians, weight 25 each           <- WHICH boss appears WHERE = random
  nameChampion1..6 = warband list, equal weights            <- composition random every spawn
```

Result per corner per run: 25% chance of [exactly 1 random guardian + exactly 5 randomly-composed escorts + 1 locked hoard chest]. Both the boss-guarantee accounting (`spawnMax - championMax >= 1`) and the escort recipe are the shipped `xsq22`/`xsq17` pattern from the BLOOD_TOXEUS doc.

**Honest limitations, flagged:** (a) corners roll independently, so one run CAN produce the same guardian at two corners (per-run exclusivity would need quest logic; recommend accepting - it reads as "the warden walks"); (b) `chanceToRun` is one value for all difficulties (native proxies live with this too).

**Warband ("star guys") list, all native to the region band:** `us_abyssalliche_flame/frost/plague_42` (Champions, L42/58/72), `um_permean_35` (DragonLich hero), golden-skeleton + dragonian elites, sepulchral wyrmsprites, fire sprites for the boom. 6 slots, equal weight, random mix per event.

**Per-corner chance - DECISION FOR WILL:** 25% per corner = ~1.0 events per full clear (4 corners), occasionally 0, occasionally a jackpot run of 2-3. 15% = rarer mystique, 35% = ~1.4/run. **Recommend 25%.**

## 2. THE FOUR GUARDIANS - wild kits (every record existence-verified this session)

Same derivation discipline as round 1 (derive from a native region monster so rig + anim table + kit stay compatible; D5-verified proxy meshes: `LicheKing02`, `GoldenSkeleton01`, `SepulchralWyrm01`, `revenantstorm` - all resolve, 0 bad shaders). Band: L **40/58/72**, between the champions (~1-2k HP) and Ormenos (27-31k). Same class for all: **Boss** (souls drop; chest lock keys off Boss classification).

- **SARKOTH, THE GLASSWRIGHT** (caster, HP 4.5/7/10.5k) - derive `us_abyssalliche_flame_42`. Kit: **`ormenos_droptelekinesis`** (the halls' own final boss ripping obsidian slabs out of the dark - the signature), **`arena_meteor`** (`Skill_DropProjectileTelekinesis`, meteor-class), `volcanicorb`+`_fragmentation`+`_immolation`, `ringofflame`, `iceshard`+`squall` (frost-glass), `drxspellbreaker`, **ondeath `ondeath_frostnova`** (he shatters). Anim flag: `DropProjectileTelekinesis` on the liche rig needs the in-game check (it rides a cast anim, liches cast; verify).
- **GORRAHK, THE TOMBSPLITTER** (bruiser, HP 6.5/10/15k) - derive a golden-skeleton melee native. Kit: `bladestorm`, **`cyclops_groundsmash`** + **`cyclops_terrifyingroar`** (boss-class slam + roar), attack-damage/speed buffs, **ondeath `ondeath\skills\bladenova`** - the 16-knife death burst. You kill him, the room fills with knives.
- **VORANTHYS, THE SEPULCHRAL** (summon-storm, HP 5/8/12k) - derive `boss_dragonliche_57` (native Boss, same rig as the halls' wyrmsprites). Kit: `sepulchralwyrm_firebreath`, `dragonliche_freezingbreath` + `_decomposition` + `_buffetingwings`, **`alastor_summonskeletonarcher` + `_warrior` + `aktaios_summontombguardians`** (three stacked summon streams = a rising tide of dead), **ondeath `ondeath_spawnskeleton`** (`Skill_OnDeathSpawnActor`) + `ondeath_necronova` - killing him RAISES more.
- **ILSEVAR, THE ASHEN WATCH** (poltergeist duelist, HP 5.5/8.5/13k, L 42/60/74) - derive from the revenant family. Kit: **`phantomstrike`** (blink-attack, `Skill_AttackWeaponBlink`) + `kika_phantomstrike`, `distortionwave` (xpack path - the `skills\dream` twin DANGLES, round-1 law), `lifedrain`, `drxdeathchillaura`, `halimedes_terrifyingroar` (spectral scream), **ondeath `ondeath_detonate`**. He teleport-flickers around the corner pocket the whole fight.

## 3. SOULS - what amgoz1 would do (style decoded from 11 of his originals)

Decoded originals (`toxeus_soul_l`, `chimera`, `hydra`, `dragonliche`, `megalesios`, `alastor`, `minotaurlord`, `medusa`, `polyphemus`, `talos`, `typhon`) give the amgoz1 grammar:

1. **Name voice:** flat and iconic: `{^F}<Name> Soul` ("Toxeus the Murderer Soul", "Dragon Liche Soul", "Typhon Soul"). Not "Soul of X".
2. **The grant = the boss's SIGNATURE MOVE**, often a `soulskills\pcsafe\` port, at cheeky levels (Toxeus grants flashpowder at **level 14** on-attack; Typhon grants **his own meteor storm**, manual).
3. **Controllers:** procs get `onattack`/`onattacked`; spectacle casts are manual (ctrl=None).
4. **Exactly 2 skill augments** (player drx* mastery skills, thematic) and sometimes a whole `augmentMasteryName1` +1 (Toxeus grants +1 all of Stealth).
5. **Dense idiosyncratic stat sheets** with one weird signature stat (Dragon Liche: `offensiveFearMin=2`, `defensiveFreeze=100`, +7% XP; Toxeus: reflect 20, deflect 16, energy absorption 30).
6. **Summons only for the great beasts** (Chimera, Hydra); even Dragon Liche got a MOVE (galeforce).

The four souls, in that voice (all grants/augments are existence-verified shipped records):

- **`{^F}Sarkoth the Glasswright Soul`** - grant `soulskills\pcsafe\typhon_meteorstorm` (manual, lvl 2/3/4 n/e/l): the sky rains obsidian. FLAG: reuses the Typhon Soul's proc at lower levels with different augments; amgoz1 reuses grants (alastor+ilsevar-style lifedrain appears on several). Augments: `drxvolcanicorb` + `drxfireenchantment_stoneskin` (obsidian skin). Signature stat: `offensiveSlowTotalSpeed` retaliation ("cut by glass") + elemental %-mods.
- **`{^F}Gorrahk the Tombsplitter Soul`** - grant `soulskills\pcsafe\cyclops_groundsmash` (manual, the Polyphemus-soul donor) at 3/4/5. Augments: `drxconcussiveblow` + `drxonslaught`. Signature: `offensiveStunModifier` + retaliation physical + `characterDeflectProjectile`.
- **`{^F}Voranthys the Sepulchral Soul`** - **THE ONE SUMMON, explicitly flagged per Will's rule:** amgoz1's beast pattern (Chimera/Hydra = manual `summon_X` lvl 3) plus the mod's own summon standardization say this wyrm earns it. Manual-cast `summon_voranthys` via `_build_boss_summon`, pets on the render-verified `SepulchralWyrm01` rig, Lyia rules throughout. Fallback if declined: grant `dragonliche_freezingbreath`-flavored cold/vitality suite with `drxcoldaura`/`drxdeathchillaura` augments (the Dragon Liche Soul precedent).
- **`{^F}Ilsevar the Ashen Watch Soul`** - grant `skills\spirit\lifedrain` on-attack (the Alastor-soul donor, higher level). Augments: `xpack\skills\dream\drxphantomstrike` + `xpack\skills\dream\drxdistortionwave` (full xpack paths; the base-dream twins dangle). Signature stat: `offensiveFearMin=2` (the Dragon Liche weirdness, perfect on a ghost) + dodge/deflect suite.

Drop: 66% hand-crafted default (`SVC_RELEASE_DROPS` convention), `Finger2`, per-tier icons, `validate_tags` gated.

## 4. THE BIG CHEST - "Obsidian Hoard"

No "majestic" class exists in TQAE (0 records); the shipped big-chest tech is: DRX golden chests (wood mesh, scale 1.4, `LockedClassification=Boss`) and the blood-cave mega chest (`container_hpalace_chestlg01.msh`, the big ornate Hades-palace chest, +100% life/mana heal on open, boss-chest fanfare sound, champion gold generator). **Recommend: clone the mega-chest shape** - new `svc_obsidianhoard_0{1,2,3}` (FixedItemContainer): `hpalace_chestlg01` mesh at scale 1.4, `locked=1, LockedClassification=Boss, LockedRadius=50`, `goldGeneratorChance=100` (champion generator), new loot tables per tier: 1 guaranteed epic (N) / legendary-or-epic (E/L) roll from the orient boss tables + a high-roll random table, richer than a golden chest, below the blood-cave mega chest (that one stays the crown). Loot table shape donor: `loottable_hidden_bloodcave_0x` / `g_default_63-65`.

## 5. THE CHARM - recommend DROP

Chest + soul is already a double reward per event; the obsidian-shard fantasy lives better in Sarkoth's `droptelekinesis`. If Will wants it anyway: Emberscale-pattern 5-shard `ItemCharm` ("Obsidian Shard", turtle-shell donor trio, 7% `lootMisc` slot on all four guardians, completion bonus = pierce/bleed resist + `defensivePhysical`).

## 6. IMPLEMENTATION SKETCH + GATES

**DB lane (`apply_svc_patches.py`):** `_create_obsidian_roulette(db)` orchestrator: 4 guardian monsters (derive natives, wild kits, ondeath skills) -> 1 shared warband pool + 4 corner proxies (`chanceToRun=25`, accessory tiers, no-cap limits file) -> 3 hoard chests + 3 accessory pools + loot tables -> 4 souls (+ `summon_voranthys` pets if approved) -> tags into `uber_soul_tags.txt`.

**Map lane (unchanged from round 1):** 4 `INJECT_SPECS` entries at the surveyed corners (all on-mesh, calibration 23/23 + 36/36 floor markers):
- Corner A `tombobs02` local (50.4, 1.0, 143.6); Corner C `tombobs02` (200.4, 1.0, 97.6)
- Corner B `tombobs01` (220.8, 1.0, 89.6); Corner D `tombobs01` (90.8, 1.0, 45.6)
plus the **native-v0x0e injection branch extension** in `svaera_plus_portals.py` (route native v0e through `inject_into_sv_only_blob` into `ae_patched_blobs`; the injector is already native-safe; v0e stride = 56B + 16B UniqueId when flagged, proven byte-exact).

**Gates:** round-1 gates (tags, record resolution, spawn-eligibility `spawnMax-championMax>=1`, limit-window containment, 0x05 count+on-mesh round-trip, navmesh byte-identity) PLUS: accessory chain resolves end-to-end (proxy -> accessory pool -> container -> loot tables); chest `LockedClassification` == guardian classification (Boss); every ondeath skill resolves; in-game: run the halls repeatedly on a fresh char, confirm the ~25% roulette, boss-varies-by-corner, warband varies, chest locked until guardian dies, soul + hoard drop. MP spawn-scaling check (standing `RunEquation` caveat).

**Risks:** the halls are main-path (roulette keeps it spicy, not mandatory-hard: 75% of corners are empty per run); `DropProjectileTelekinesis` anim-fit on the liche rig needs in-game confirm; native-v0e injection is a new pipeline branch (test on one corner first); duplicates-across-corners possible (flagged).

**WILL DECISIONS:** (1) per-corner chance: 15 / **25** / 35%? (2) the four identities/names OK to rename freely; (3) **Voranthys summon-soul: approve or take the move-grant fallback?** (4) chest look: mega-chest ornate (recommended) vs golden-chest wood; loot aggressiveness; (5) duplicate-guardian-per-run acceptable? (recommended yes); (6) charm: drop (recommended) or fold in; (7) warband size 5 escorts OK? (8) Sarkoth's soul reusing Typhon's meteor-storm proc at lower levels: OK?

---

**Summary of what changed vs round 1:** always-on lone bosses became a 25%-per-corner roulette; the shared 4-boss pool randomizes WHO appears WHERE; each event ships a 5-escort random warband + a Boss-locked Obsidian Hoard chest, all under ONE `chanceToRun` roll on ONE proxy (1,819-proxy shipped precedent, TutorialPotionChestProxy chain decoded as the donor); kits went theatrical (meteor drops, 16-knife death burst, triple summon streams, blink-duelist ghost, ondeath effects all around); souls re-authored in amgoz1's decoded voice (signature-move grants incl. one flagged summon, 2 thematic augments, one weird signature stat each); corner coords, band math, D5 mesh proofs, and the native-v0e map-lane path carry over from round 1 unchanged.