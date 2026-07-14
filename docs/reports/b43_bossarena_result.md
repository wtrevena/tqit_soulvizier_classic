# B43 - Olympian Arena boss finish (RESULT)

Branch `feat/b43-bossarena` (worktree). Follows the read-only RCA
(`docs/reports/b43_bossarena_rca.md`, verdict: **NOT ported wrong; SV
under-built / never finished it**). This wave implements case (B) + the polish
(A): design + implement a worthy singular named Olympian arena boss, kill the
green blob, add the reward + dressing, strip the debug mannequin.

Commits: `f2c349a` (arz DB module) + `14c8d4e` (map). RCA anchor `cba1b18`.
Ground truth: `baseline_build38.arz` md5 **fcd5dcab** (my session snapshot; the
RCA's "6631f252" was the transient `work/` arz other waves are actively
rebuilding, now 10 min newer - I used the stable scratchpad snapshot per the
task, NOT `work/`). No heavy build this wave (per the concurrency rules); every
change is proven by dry-run replay into COPIES.

---

## ⚑ DESIGN - FLAGGED FOR WILL'S DEV-TOUR VETO (read this first)

The Olympian Arena's boss is now **"Aithon, the Ember-Crowned"** - a singular,
named, boss-scale **fire-satyr arena champion**, wreathed in a ring of volcanic
flame, flanked by 2 Ember Satyr Warden honor guard, dropping his own signature
soul.

**Why a (named) satyr and not a Titan/Gigante.** SV's arena boss is its OWN
`boss_satyrshaman` on a **bespoke, hand-built fire kit** (arena_flamesurge /
volcanicorb + immolation + fragmentation / meteor / fire aura) + a bespoke
`controller_arenasatyrshaman` - amgoz's own SV content. The mesh is literally
`SatyrShamanStarterBoss.msh` (SV's placeholder "starter boss"). Elevating that
proven rig to a **named** apex is faithful to amgoz, fully in-rig (the fire kit
animates correctly - zero new/untested mechanics), and **fully offline-verifiable**
(done: all gates green). A rig-swap to a grander donor is the creative upgrade,
but it is **not** offline-verifiable (animation/assert risk, and you are playing),
so per the mandate's "prefer creative WHEN feasibility-vetted" it is held for your
in-game call, not shipped blind.

**If you want it grander (one word on the DEV tour and I do it round 2):** the
donor is pre-identified - **`um_clytius_44`** (Clytius, a Gigante of the
Gigantomachy - the battle *for Olympus* - myth-slain by fire; a Hero already in
the mod with its own `clytius.msh` + `clytius.tex`). The swap = clone it, carry
the SAME arena fire kit + the Aithon soul/reward onto it, repoint the pool. The
ONLY unknown is whether the arena cast/projectile skills animate cleanly on the
cyclops rig - a 30-second in-game look answers it. Other grander donors surveyed:
`um_emberoak_42` (ember treant), `am_colossusofkarnak_36` (Hephaestus-forged
automaton), `bm_eldercyclops`. **Say the word and I build whichever you pick.**

Also your call (trivial dials): lone apex vs the 1+2 honor-guard arena (currently
1+2); HP band [42k,54k,66k]; the name/epithet.

---

## What shipped (all verified by dry-run)

### DB - registry module `tools/patches/bossarena.py` (commit f2c349a)
Registered in `tools/patches/__init__.py` REGISTRY (12 modules; order hash
`525453c0...`). Disjoint: ref-scan proved `boss_satyrshaman_55` is referenced
ONLY by the arena pool, the pool ONLY by the proxy, the proxy by NO record (only
the untouched quest names it) - so every edit is "this arena's own restoration."

1. **Green blob killed.** The quest-spawned Proxy `boss_satyrshaman.dbr` (which
   rendered `satyrmage01.msh` + the translucent `Proxy01_Patrol.tex` marker at
   0.5 alpha, mid-floor) is made non-rendering: `maxTransparency 1.0`,
   `castsShadows 0`. Refs kept valid (no empty-ref abort). **Quest untouched** -
   it still spawns this proxy by name; the proxy still pools the encounter.
2. **The apex, in place.** `boss_satyrshaman_55` -> **Aithon, the Ember-Crowned**:
   name (`tagSVCMonsterAithon`), `maxTransparency 0.0` (kills the "faint ghostly
   boss" look - it was 0.5), `scale 1.9`, HP `[42k,54k,66k]`, a fire/burn/phys
   resist wall (`defensiveBurn 100` = he IS fire, cannot be burned), a persistent
   **ring-of-flame shroud** (`charFxPakRunningNames = [ringofflame_charfx]`, the
   proven Enslaver/Marshal CharFxPak route). The whole fire kit + controller +
   rich on-death loot (staff / caster armor / relics / heart / arcane formulae)
   are **left intact** = the boss-tier reward AT the center, on clear.
3. **Honor guard.** One new `ember_satyr_warden_55` (clone `am_champion_11`
   SatyrBrute, rebanded `[50,64,72]`, given the arena fire aura + flame-surge
   special, `defensiveFire/Burn`). Drops no soul (soul-leak law).
4. **The pool.** `satyr_shaman_01`: `spawnMax 3`, `championMin=championMax 2`,
   `name1 = the apex`, `nameChampion1 = the warden` -> **1 guaranteed apex + 2
   champion honor guard** (`spawnMax - championMax = 1`; asserted inline - NOT
   registered in the global spawn-eligibility gate because this quest boss
   intentionally scales to player level via `limit_quest` [Normal 29-36] which is
   BELOW his L55, so the gate's level<=window check would false-fail).
5. **The soul** (amgoz's signature trophy): **`{^F}Aithon, the Ember-Crowned Soul`**
   (`svc_uber\aithon_embercrown_soul_{n,e,l}`) - his own **fire-nova proc that
   ERUPTS when he is struck** (`firefragmentnova` + `flamefragmentnova_onattacked`
   controller = temperament-matched retaliation), **volcanic-orb + fire-enchant
   augments** (his real Earth/fire moves), **Beastman racial** (satyr - mastery
   over his own kind), a dense fire + ember-burn sheet, the **amgoz downside**
   (reckless arena brawler: `-characterDefensiveAbilityModifier`) + the identity
   resist (`defensiveBurn 100`). **No prose lore** (amgoz V5); `FileDescription =
   "Olympus"` (region). Drops **66%** off the apex; the shared `darksatyrshaman`
   soul stays on the 3 other satyrs that also drop it (untouched).

### Map - `build_section_surgery.py` + `svaera_plus_portals.py` (commit 14c8d4e)
Arena level ONLY. QUESTS section + every other level + all navmeshes untouched.

6. **Mannequin stripped.** New `REMOVE_ARENA_BLOCKOUT_SPECS` + an `M16` de-place
   block (mirrors M2/M6/M14) removes the SV Player-class debug mannequin
   `malepc01` (`boss_arena.lvl` inst 22, north edge, surveyed OFF-mesh / 0% clr =
   a careless blockout leftover). Asserts exactly 1 de-placement.
7. **Fire-glow dressing.** `INJECT_SPECS[boss_arena.lvl]` = a ring of **6 orange
   dynamic lights** (`5mlight_dyn_orange`, shipped/proven record) framing the
   central fight floor. Surveyed **on-mesh** on the fight component (comp#2) at
   r~14u around local (132,130): every point d<=0.14u / 100% clear on all 3
   tilesets. Pure light (no mesh / no collision / no 0x14) - never blocks the
   fight; pairs with Aithon's shroud (fire vs the cold arena floor).

---

## Verification (no heavy build; dry-run into COPIES)

- **py_compile**: `bossarena.py`, `build_section_surgery.py`,
  `svaera_plus_portals.py` all OK.
- **`_check_registry.py`**: OK, 12 modules, stable order hash.
- **DB replay** (module applied to a load of `baseline_build38.arz`): every field
  lands exactly (proxy invisible; apex renamed + shroud + HP + resist wall + kit
  intact + Finger2 66% -> Aithon soul; champion has no soul leak; pool 1 apex + 2
  champions, guaranteed_mains=1; all 3 soul tiers built with the full amgoz
  payload; all refs resolve; the 3 other satyrs still drop the shared soul).
- **DB gates** (monolith gate functions run over the replayed db): PASS -
  `_verify_no_unclassified_soul_leaks`, `_gate_common_soul_leaks`,
  `_verify_soul_augments_resolve`, `_verify_soul_itemskill_activation` (1390
  souls), `_apply_soul_naming_standard` + `_verify_soul_naming` (name preserved).
- **Map dry-run** (committed specs applied to a COPY of the `boss_arena` blob from
  `local/Levels_merged.arc`, in pipeline order inject-then-remove): 0x05 30->35
  instances, `malepc01` gone, 6 lights at the exact coords; **0x06 / 0x09 / 0x0b
  (NAVMESH) / 0x17 BYTE-IDENTICAL**; 0x14 reindexed (portals 28/29 -> 27/28); blob
  parses EXACT (LVL v0x0e). QUESTS 256-window untouched (no quest edits).

Evidence probes (session scratchpad): `b43_probe.py`, `b43_probe2.py`,
`b43_probe3.py`, `b43_probe4.py` (recon), `b43_replay.py` (DB replay),
`b43_gates.py` (gate battery), `b43_map_dryrun.py` (map surgery), plus the RCA's
`probe_arena*.py` / `final_probe.py`.

---

## OPEN ITEMS (surfaced, not dropped)

1. **[HIGH - reachability, verify in-game] The arena navmesh has TWO components.**
   The south hub landing (local ~128,40) is on comp#1 (1.38M cells); the central
   fight floor + boss spawn (local ~132,130) is on comp#2 (92k). If they are truly
   disconnected the player cannot walk from the landing to the boss and the whole
   encounter is unreachable. This is **PRE-EXISTING** (build23 navmesh gen of this
   SV area), NOT introduced here, and likely an erosion artifact of the low-apron/
   high-floor ramp (on-mesh cells exist 20u apart across the seam). **Needs a
   30-second in-game reach-test** (walk landing -> center); if it walls, it is a
   navmesh-lane re-stitch, not a content fix. Flagging because it gates everything.
2. **[HIGH - the gray planes, portal lane] The "giant gray untextured planes" Will
   saw are the return portals** (`portal_olympianarena2`, north edge, `flattexture01`
   placeholder). NOT fixed here (portal art is out of the boss lane). The decided
   fix is **B-PORTAL-1** (WILL_DECISIONS: co-locate the DRX swirl FX at flat portal
   panels). Recommend the visuals/portal lane apply B-PORTAL-1 to the 2 arena
   return portals (local (130,166) and (137,198)). Say the word and I fold it in.
3. **[MED - proxy invisibility fallback]** The green blob is killed by
   `maxTransparency 1.0` on the proxy. If any translucent marker still shows
   in-game, the ref-safe fallbacks are: repoint the proxy mesh to an invisible
   marker, or change the quest's `Action_SpawnEntityAtLocation` to spawn the pool
   directly. Confirm on the tour.
4. **[LOW - dressing polish, map lane] Physical Olympus braziers.** Round-1 dressing
   is light-only (safe, guaranteed-resolve, no theme clash). Physical fire props
   (donors identified: `hp_persephonebrazier01`, `hc_flamestatue01-03`, all resolve
   via SceneryUnderground) would enrich the frame but carry a small Hades-vs-Olympus
   theme-clash + exact-height risk - deferred to the map lane / your taste.
5. **[LOW - reward flourish] Bespoke signature relic.** The round-1 reward is the
   guaranteed named soul + the boss's rich on-death loot (already apex-tier). An
   "Aithon's Ember" tiered relic (donor `svc_flameguard`, the neferkha idiom) is a
   clean round-2 add if you want a named trophy item on top of the soul.

## Ban / law compliance
Worked only in the worktree (never touched main); no heavy build (blob parsing +
dry-run injection into copies + gate replay only); no git config mutation, no push;
SV DESIGN mutations confined to this arena's own boss chain (its own restoration);
no TQ/Steam interference; QUESTS 256-window + registry untouched; navmesh byte-
identity proven for the arena's 0x0b (and every other level untouched); every placed
light on-mesh; every referenced asset resolves; crash laws respected (no clone_record
soul - used `_create_soul`; no dtype on the champion clone; no Pet.tpl equipment; FX
via charFxPakRunningNames on the monster record, the proven route); no em dashes.
