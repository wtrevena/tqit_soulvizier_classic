# b76 - CHUMBI VALLEY P0 FREEZE: RCA + fix (round 1)

**Branch** `fix/chumbi-lag` (from `main` @ 33d25d6 = post-build45).
**Will's P0 (2026-07-16, verbatim):** "in the chumbi valley in the dev environment there is so much
lag with the monsters you placed the game is unplayable i cant even move the game is like frozen i
think it is all the permian extinguishers and their abilities that are stopping the game especially
the infinite summon of the skeleton dog guys tomb guardian, i think the monster leading this whole
thing is the uber boss whos name has sepulcher in it." Plus four follow-ups (placement pileup =
co-primary; summon = co-primary; the widow quest chest; the fountain/occultist death loop).

**TWO co-primary defects, each independently freeze-capable — BOTH fixed:**
1. **PLACEMENT PILEUP** - the TESTHUB **Monster Test Yard**: 10 boss encounters stacked in ONE level
   (HiddenValley01 = the blood-cave surface = "Chumbi Valley"), around the Rebirth Fountain + occultist.
2. **UNBOUNDED SUMMONS** - the sepulcher boss `um_voranthys_99` fires three TTL-less summon skills
   (tomb guardians + skeletons) that accumulate/re-summon without bound.

---

## 1. GROUND TRUTH - what Will is running

DEV entry `SoulvizierClassicDEV/Resources/Levels.arc` md5 **`0c10343b4f8d378b83b13eafe520f5fe`**
(688,676,622 B, deployed 2026-07-16 02:05 - a fresh TESTHUB build newer than any documented one).
Census of `records\drxmap\proxy\*` placements across all 2282 levels
(`tools/debug/census_placements.py`): HiddenValley01 carries **10** custom boss proxies; every other
level carries 1-4. That is the pileup, and it is TESTHUB-ONLY (the canonical/Steam map places none of
these - each yard boss lives on its own distinct host level).

### The 10-boss yard (HiddenValley01, local coords)
| proxy | local (x,y,z) | pool (what it spawns) |
|---|---|---|
| q_yard_enslaver | (33,16,41) | Enslaver + marauders |
| q_yard_marauders | (71,14,31) | demon-strength marauders |
| q_vashkarr_lone | (101,-2,43) | Vashkarr + 2 champs |
| q_yard_dorus | (65,-10,63) | Drowned King Dorus + 2 royal guards |
| q_yard_obs_sarkoth | (63,10,97) | Sarkoth (blood-dragon) + whelps |
| q_yard_obs_gorrahk | (127,-2,93) | Gorrahk (cyclops) |
| q_yard_obs_voranthys | (157,0,111) | **um_voranthys_99 (the "sepulcher" boss)** |
| q_yard_broodmother | (107,1,123) | um_broodmother_99 + 2 **um_sepulchralwyrm_40** escorts |
| q_yard_obs_ilsevar | (71,0,129) | Ilsevar (phantom lich) |
| q_yard_wyrm | (55,18,157) | wyrm horde |

The Rebirth Fountain (respawn shrine) + occultist Hades-merchant are the legit HV01 residents; the
yard bosses were spaced ~30u around them, so a player who dies respawns AT the fountain into the aggro
radius of these bosses -> the **death loop** Will reported.

---

## 2. RCA - PILEUP (primary)

**Root cause: the Monster Test Yard (a deliberate TESTHUB-only QA cluster) grew unplayable.**
`tools/build_section_surgery.py :: build_hub_extra_specs()` appended a `HV01_LVL_KEY: [...]` block of
yard proxy placements, folded into `INJECT_SPECS` **only when `SVC_TEST_HUB=1`** by
`merge_hub_into_inject_specs`. Origin trace (git-blame + in-file comments):
- **build33** (comment @ line 2475 "MONSTER TEST YARD (build33, TESTHUB-only)"): 7 proxies so Will
  (mod author) could "fight+tune every new hostile monster from build31/32 in one place."
- **build35**: +broodmother apex (8->9). **build36 M1**: +Drowned King Dorus (9->10), RESPACED to min
  pairwise 32u because Will already said "pets too crowded."
- The cluster kept growing one boss per content wave until 10 apex encounters (each a POOL of a boss +
  100% escorts, several of them summoners) share one small valley -> the freeze.

**Variant scope:** TESTHUB-ONLY. Canonical `INJECT_SPECS[HV01]` has 15 legit specs (plaza travelers +
returns), zero yard. The DEV map Will runs is the TESTHUB variant, which is why only DEV freezes.

**Every yard boss is ALREADY placed at its own canonical home** (the yard is a redundant QA copy):
Enslaver @ warband (drxfirstxistion_connection), Vashkarr @ FotA (random05a), Dorus @ Medea Tomb03,
Broodmother @ tombobs02, the 4 Obsidian @ their roulette/questbosses hosts. So the "space these out"
fix Will demands = REMOVE the redundant yard; the bosses are already dispersed canonically.

---

## 3. RCA - SUMMONS (co-primary): the sepulcher / tomb-guardian chain

Will's "uber boss whos name has sepulcher in it" = **`um_voranthys_99`**
(`records\creature\monster\questbosses\`), the apex Obsidian uber. Its signature is
`sepulchralwyrm_firebreath` ("sepulcher"). b39's `boss_skill_fix` module ENABLED its three previously
**dormant** (skillLevel-0, never-fired) summon specials - which is why the freeze is recent:

| skill voranthys fires | class | petLimit | **TTL** | spawns |
|---|---|---|---|---|
| `boss skills\aktaios_summontombguardians` | SpawnPetMonster | 9 (burst 2) | **NONE** | aktaios_tombguardian_21/24/27 = "the tomb guardians" |
| `boss skills\alastor_summonskeletonwarrior` | ProjectileSpawnPet | 8 | **NONE** | alastor_skeletonsoldier_07 = "the skeleton guys" |
| `boss skills\alastor_summonskeletonarcher` | ProjectileSpawnPet | 8 | **NONE** | alastor_skeletonarcher_07 |

One hop deeper, the base skeleton priest's `monster skills\summonpet_undeadmelee01` (petLimit 5, 3s
cooldown, **NO TTL**) spawns up to 5 permanent zombies/skeletons - the recursive tier.

**The defect:** each summon has a single-digit CONCURRENT cap (`petLimit`) but **NO
`spawnObjectsTimeToLive`**, so summoned minions are PERMANENT. With no TTL the boss re-summons on
cooldown the instant a minion dies to refill the cap; the fight never reaches steady state, and
dead-minion corpses + summon FX accumulate. Voranthys alone can hold ~25 permanent minions,
continuously refilled. Stacked x10 in the yard = hundreds of live entities + auras/FX = the freeze.

**VANILLA CONVENTION proves this is a REGRESSION, not design:** SV 0.98i's OWN variant of the identical
tomb-guardian skill, `records\skills\sv\shodema\aktaios_summontombguardians.dbr`, ships
`spawnObjectsTimeToLive = 5.0` (+ petLimit 3). This repo's own `four_generals` archer musters
deliberately add `spawnObjectsTimeToLive = 20.0` ("finite TTL (quest-safe)"). The `boss skills\` copies
these bosses actually fire simply lost the TTL.

"Permian Extinguisher" (Will's phrase) = the `dragonliche\permean_soul` monster family; its
`dragonliche_*` skills (freezingbreath/decomposition/buffetingwings, cooldown ~0.01s) are on voranthys
too and are heavy AoE-FX casters - a compounding FX-cost factor, not itself an unbounded summon.

---

## 4. ENTITY MATH (before / after)

- **Before (yard, standing):** 10 boss pools x (1 boss + ~2 @100% escorts) = ~30 baseline, PLUS each
  summoner's live pets: voranthys ~25, broodmother 6 broodlings + 2 sepulchralwyrm, sarkoth 5 whelps,
  the priest tier +5 each - a steady state well over 100 live entities, none despawning (no TTL),
  each with auras/combat FX. => frozen client.
- **After FIX 1 (unstack):** 0 yard entities in HiddenValley01; each boss fought at its own canonical
  home (1 boss + escorts + its own capped summons).
- **After FIX 2 (TTL restored):** voranthys' tomb guardians despawn after 5s and skeletons after 20s,
  so the fight reaches a bounded steady state and resolves - playable STANDING ALONE.

---

## 5. THE FIX

### FIX 1 (primary = UNSTACK) - map, `tools/build_section_surgery.py`
Removed the `HV01_LVL_KEY: [10 yard proxies]` block from `build_hub_extra_specs()`. The yard proxy
RECORDS stay in the shared arz (inert - nothing places them). Deterministic proof
(`merge_hub_into_inject_specs(INJECT_SPECS)` with `SVC_TEST_HUB=1`):
- `build_hub_extra_specs()` HV01 entries: **10 -> 0**.
- TESTHUB-merged HV01: 15 specs, **0 yard/vashkarr proxies** (== canonical HV01's 15 plaza/return NPCs).
- canonical `INJECT_SPECS[HV01]`: **15, unchanged** (was already yard-free).

So the rebuilt TESTHUB HiddenValley01 blob loses exactly the 10 yard 0x05 instances and nothing else
(the yard was an append-only TESTHUB layer; canonical is byte-untouched, and the append-only invariant
is the historically gate-proven `gate_hub_identity` property). The fountain + occultist are now clear
of hostiles -> death loop resolved.

> **Integration-gate residual (ship operator):** rebuild `local/Levels_merged_TESTHUB.arc` from this
> branch (`SVC_TEST_HUB=1 py tools/svaera_plus_portals.py`), blob-diff vs the current TESTHUB baseline
> = ONLY HiddenValley01's 0x05 sections change (the 10 removed instances), navmesh 0x0b byte-identical,
> `verify_merged_bc_navmeshes` 24/24, QUESTS 256-window byte-identical. Not run in-worktree: the map
> builder writes to hardcoded `<main-repo>\local\` (clobber hazard for parallel lanes); the spec-level
> proof above is decisive and the injection is deterministic + append-only.

### FIX 2 (co-primary = SUMMON CAPS) - DB, `tools/patches/summon_caps.py` (NEW registry module)
Additively restores the missing `spawnObjectsTimeToLive` on the four unbounded boss-summon skills of
the sepulcher/tomb-guardian chain (petLimit / spawnObjects / cooldown untouched):

| skill | TTL added | precedent |
|---|---|---|
| `boss skills\aktaios_summontombguardians` | **5.0s** | SV's own `sv\shodema\` variant |
| `boss skills\alastor_summonskeletonwarrior` | **20.0s** | four_generals quest-safe |
| `boss skills\alastor_summonskeletonarcher` | **20.0s** | four_generals quest-safe |
| `monster skills\summonpet_undeadmelee01` | **20.0s** | recursive skeleton-priest tier |

`petLimit` is left as-is: it is already a single-digit **hard concurrent cap** (9/8/8/5), vanilla-
shipped; the missing piece was the TTL (self-despawn), which is what stops the infinite re-summon /
accumulation. Module runs after `boss_skill_fix` (which enabled the specials), has `verify()`
(fail-loud if any target survives uncapped) + a standalone `--negtest` (plants an uncapped fast
summoner, asserts the sweep flags it, caps it, asserts it clears).

> **⚠️ WILL-VETO (tuning):** the TTL values (tomb guardians 5.0 = SV shodema; skeletons 20.0). The FIX
> is the PRESENCE of a finite TTL; bump/lower the seconds freely.
> **Honest scope note:** these skills are ALSO used by base Egypt-telkine **Aktaios** and base
> necromancer **Alastor**. Adding a TTL there is an intended, SV-aligned side effect (their minions
> now self-despawn, exactly as SV's shodema variant already does) - a mild improvement, never a
> difficulty cut (the boss re-summons on cooldown up to the same petLimit). The apex **pet FAMILIES**
> (aktaios_tombguardian_*, alastor_skeleton*) are NOT edited (a parallel lane owns boss-summon pet
> families); only the SKILL's TTL field is set.

### CHEST finding (folded into the unstack)
HiddenValley01 has **NO static custom chest** (census of `chest`/`widow`/`adventurer`/`loot` 0x05 refs
in HV01 = 0). The "Dead Adventurer's Chest" Will names is the **widowletter QUEST chest** - spawned by
the widowletter questline's OnLevelLoad action (quest-state-controlled; permanently sealed for players
who took the widow's buff), which legitimately lives at the blood-cave surface. The yard bosses had NO
reward container of their own; Will (reasonably) read the nearby quest chest as their reward. Removing
the yard resolves the false association: the bosses return to canonical homes that carry their own b42/
b43 non-quest-gated majestic chests (`svc_*_chest`), and the widow quest chest stays exactly where and
what it is (byte-untouched - the map lane never places it). **Container mini-sweep:** the placed-encounter
reward containers in `INJECT_SPECS` are all `records\drxmap\proxy\svc_*_chest.dbr` (b42/b43 majestic
chests) - none is a quest-controlled container. No other encounter reuses a quest chest.

---

## 6. VERIFICATION (this round)

**DB (`local/SoulvizierClassic_b76.arz`, md5 `7fb879ac9c346280cdaf3610e7d53dad`, 55,382,493 B):**
- Full scratch build `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1` -> **EXIT 0**; all 18 registry `verify()`
  hooks green incl. `summon_caps.verify` ("4 sepulcher-chain summon skills all carry a finite spawn-TTL").
- **Record-diff vs build45 reference `917d9047`: exactly 4 MODIFIED, 0 added/removed**, each a single
  `spawnObjectsTimeToLive` field added (5.0 / 20.0 / 20.0 / 20.0). Zero collateral.
- `summon_caps --negtest`: PASS (uncapped fast summoner flagged; capped one cleared).
- **summons contract** (`contracts_summons.py` vs base game): violation set **byte-identical** to the
  reference arz (652 lines, incl. 96 pre-existing whitelist-suppressed P0 = base/SV-inherited debt) ->
  **zero new/removed violations**; exit 0 (no unwhitelisted P0/P1).

**MAP (`tools/build_section_surgery.py`):** spec-level proof in §5 (yard 10->0, TESTHUB HV01 ==
canonical HV01); py_compile OK; registry selfcheck OK (27 modules, order
`fb5524e50881...`).

---

## 7. CLASS SWEEP (Will: "the last of its kind")

`summon_caps.sweep_uncapped()` (Skill_*SpawnPet* with cooldown <10s AND no petLimit AND no TTL = the
truly-unbounded pattern) over the build45 arz found **8** records, ALL base/dead/test, none a placed
freeze offender:
`telkine_projectilespawnpet` (x2 paths, base telkine), `oldnaturemastery_animalcompanion` (dead "old"
mastery), `01_skill_zombiemelee_swarm_a` + `_1sec_cd` (event summoning, ttl explicitly 0),
`copy (2) of drxregrowth` (dev-junk), `earth\test\stoneform_spawn_bait` (test record).

The genuine monster/boss-summon offenders in the sepulcher/placed-encounter chain are the **4 fixed
here** (petLimit present but no TTL). A broader first pass (any spawnObjects skill with no
petLimit/ttl/spawnMax) hit 119 records, but the large majority are **player-mastery** skills
(drxstoneform, drxbriarward, drxwolfsummons, quillvine walls, etc.) bounded by player/mastery caps -
not monster summoners.

**Round-2 items (documented, not done here):**
- Promote `summon_caps.sweep_uncapped` into a **build gate** in `tools/contracts/` (assert every
  monster-fired summon skill on a PLACED/spawnable boss has cap-or-TTL on the final arz; negative test =
  plant an uncapped fast summoner). Round-1 ships the sweep + negtest as a module method.
- Decide whether the base telkine `telkine_projectilespawnpet` / event zombie-swarm want caps (base
  content; likely fine - one-shot projectile/event summons).
- The stale build32-era debug script `tools/debug/gate_build32_parseback.py` still asserts the (now
  removed) HV01 yard placements - refresh or retire it (NOT in the active map gate battery).

---

## 8. FILES CHANGED
- `tools/build_section_surgery.py` - removed the HV01 Monster Test Yard block (FIX 1).
- `tools/patches/summon_caps.py` - NEW registry module (FIX 2).
- `tools/patches/__init__.py` - register `summon_caps` (after boss_skill_fix, before visuals).
- `tools/debug/census_placements.py`, `tools/debug/summon_probe.py` - NEW recon tools.
- `docs/reports/b76_chumbi_freeze_rca.md` - this report. `docs/BACKLOG.md` - b76 entry.
