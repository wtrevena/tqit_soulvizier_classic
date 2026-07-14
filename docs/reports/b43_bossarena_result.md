# B43 - Olympian Arena boss finish (RESULT, round 2)

Branch `feat/b43-bossarena` (worktree). Round 2 = **fix ALL four prior-round vet
findings, then re-verify**. Round-1 shipped the Aithon boss + map dressing but the
adversarial vet found the encounter was **unreachable** (CRITICAL), plus 3 lesser
issues. This round fixes every one and re-proves the whole wave by dry-run.

RCA anchor `cba1b18` (`docs/reports/b43_bossarena_rca.md`). Ground truth: canonical
map `local/Levels_merged.arc` md5 **60a62880**; DB snapshot `baseline_build38.arz`
md5 **fcd5dcab**. **No heavy build** (blob parsing + dry-run inject into COPIES + DB
replay only, per the concurrency rules - other waves own main + the build machine).

---

## ⚑ DESIGN - STILL FLAGGED FOR WILL'S DEV-TOUR VETO (read first)

The Olympian Arena boss is **"Aithon, the Ember-Crowned"** - a singular named
boss-scale **fire-satyr arena champion** (scale 1.9, HP [42k,54k,66k], a fire/burn/
phys resist wall, a persistent ring-of-flame shroud) flanked by **2 Ember Satyr
Warden** honor guard, dropping his own signature `{^F}Aithon, the Ember-Crowned Soul`
(fire-nova erupt-on-hit + volcanic/fire-enchant augments + Beastman racial + the
amgoz downside). Built on SV's OWN bespoke arena fire kit (flame surge / volcanic orb
+ immolation/fragmentation / meteor / fire aura) + `controller_arenasatyrshaman` -
zero new/untested mechanics, fully offline-verifiable. **Now that round 2 makes the
arena reachable, this fight is LIVE - please veto/greenlight on the tour.**

Grander-donor upgrade pre-identified if you want it (one word round 3): **`um_clytius_44`**
(Clytius, a Gigante of the Gigantomachy - the battle *for Olympus*, myth-slain by fire;
a Hero already in the mod with `clytius.msh`). Swap = clone it, carry the SAME fire kit +
Aithon soul, repoint the pool; only unknown is whether the arena cast anims read clean on
the cyclops rig (a 30-second in-game look). Trivial dials also yours: 1+2 vs a lone apex;
HP band; the name.

---

## The four vet findings - ALL FIXED

### 1. [CRITICAL] Encounter was UNREACHABLE (isolated navmesh island) - FIXED

**Confirmed independently** on the canonical map (`survey_uberboss_spots.py boss_arena.lvl`):
the `boss_arena` 0x0b navmesh has **2 disconnected components** (engine climb model):
- **comp#1** = 1,381,391 cells, the low floor, **world y ~0**.
- **comp#2** = 92,026 cells, the raised **arena dais**, **world y ~27-31**, local x[93.9,169.7]
  z[97.5,168.1]. It has **no comp#1 floor under it** (single-height cells), i.e. a true 28u
  platform wall, not eroded ramp edges.

EVERY fight element sits on comp#2: the arena floor tile `olympusarena01`, the trigger
`volume_startolympianarena` (r=20 @ local 132,130, y27), the spawn `location_bossarenacenter`
(y27), the center light, and round-1's 6 dressing lights. **The Helos-traveler landing and the
in-arena return NPC were on comp#1** (local ~128-131,40) - so the player materialised on the low
floor 28u below the fight with no walkable path up. Nothing this wave placed was experienceable.

**FIX (vet option b - land + return ON the dais; the vet's own hypothesis that SV's entry was
directly onto the dais):**
- Outbound Helos-traveler landing retargeted **`world (-433,0,-3602)` -> `(-429,27,-3538)`**
  = local **(132,27,104)** on comp#2 (south dais), **26u S of the boss spawn**, **6u outside the
  r=20 trigger** (so `Condition_EnterVolume` fires on the short walk-in), 6.5u clear of the south
  dais edge. `build_quest_files.py` HELOS_HUB_TRAVEL + TESTHUB_MASTER_DESTS.
- In-arena return NPC (`svc_testhub_return`) retargeted **local (131,0,40) comp#1 -> (136,27,104)
  comp#2**, 4u E of the landing. `build_section_surgery.py` build_hub_extra_specs.
- `gate_build32_parseback.py` expected return coord updated to match.

**Survey proof** (canonical map, ext=3.0, all 3 tilesets): landing (132,104) = **comp#2/92026,
d=0.14, clr 100%**; return (136,104) = **comp#2/92026, d=0.14, clr 100%**. The whole loop
(land -> fight at center -> return NPC) is one connected component; landing y=27 snaps onto the
dais (the only mesh at that x,z). Chosen the SOUTH dais, not the vet's "near portal @130,166"
suggestion, because that portal is a GridExitOneWay (landing on it would teleport the player
straight back out) and the south gives a natural walk-in toward the boss.

### 2. [HIGH] "Giant gray untextured planes" left unaddressed - ADDRESSED (+ honest reframe)

Re-probed the actual records. The 2 **placed** return portals `portal_olympianarena2`
(GridExitOneWay) already ship **`invisibleInWorld=1`** - so they should NOT render, which
*weakens* the round-1/vet premise that the placed return portals are the gray planes. The ONE
portal that renders a mesh is **`portal_olympianarena1`** (GridEntrance, opened on level-load by
the quest, Elysium_from_TOJ mesh + `flattexture01`/`flatbumptexture01` flat placeholder, **no
invisibleInWorld**).

**FIX (DB, this arena's own portals, disjoint - 0 other DB refs):** hide BOTH portal meshes -
`invisibleInWorld=1` + `maxTransparency=1.0` + `castsShadows=0` - **without touching grid function**
(the quest's `Action_OpenDynGridEntrance` still runs; GridExitOneWay still teleports if walked
into). The player now travels via the hub + return NPC, so these SV portals are vestigial. This
kills the leading portal-based gray plane.

**Honest caveat (for the tour):** if gray planes PERSIST after this, the source is the Olympus
**structures** (stoa/tholos/arena tile) not resolving `SceneryOlympus.arc` at runtime - a
packaging question, not fixable by a record edit. **Unlikely**: the mod's other Olympus areas
(Helos plaza `olympusfinal02`, Garden of Merchants) render textured, and the RCA index found 0
unresolved art. **Will's 5-second tiebreaker: are the arena ring columns marble (art loads -> the
planes were only the portals, now hidden) or all gray (escalate to a resource-path/packaging
check)?**

### 3. [MED] Green-blob "fixed" overclaimed on a maxTransparency misdiagnosis - REDIAGNOSED

**The vet was right.** Base-DB proof: **1,003 base-game proxies carry the IDENTICAL config** as the
arena proxy (mesh `satyrmage01` + `baseTexture Proxy01_Patrol.tex` + `maxTransparency 0.5` + no
`invisibleInWorld`), and **none render as a blob** in normal play (the engine hides proxy meshes at
runtime). So the arena spawn-proxy is a bog-standard invisible spawner and is **NOT** Will's "green
FX blob" - round-1's core diagnosis was wrong.
- The proxy hardening is **kept as cheap defensive belt-and-braces** (now `invisibleInWorld=1` on
  top), but **no longer claimed as the fix**.
- **Reverted** the round-1 boss `maxTransparency 0.0` (it was never ghostly at the 0.5 template
  default, and 0.0 risked suppressing the `ambushDissolveTexture=cloud.tex` spawn-in fade - left at
  0.5 per the vet).
- **Leading true source, now mitigated:** an **OPEN Elysium grid-entrance glow** (portal_olympianarena1,
  opened on level-load) - hidden by fix #2. Secondary: the satyrs' 2s dissolve-in seen from afar,
  which round-1's unreachable-from-comp#1 state made a "ghost on a far platform"; option-b makes it
  a proper in-arena boss appearance.
- **Gate honesty:** `green_blob` is now **rediagnosed + mitigated (proxy hardened, Elysium glow
  hidden, encounter now fires in-arena), pending in-game confirmation** - NOT "killed."

### 4. [LOW] Report said "3 other satyrs" keep the shared soul - CORRECTED to 2

Replay confirms exactly **3** monsters drop `darksatyrshaman_soul` in build38
(`boss_satyrshaman_55` + `bs_shaman_10` + `bs_shaman_12`). After Aithon's Finger2 repoints to the
Aithon soul, **2** remain: `bs_shaman_10`, `bs_shaman_12`. Fixed in the module docstring + this
report. (Not orphaned; no functional impact.)

---

## What shipped (all verified by dry-run - see Verification)

**DB - `tools/patches/bossarena.py`** (registry module, 12 modules, order hash `525453c0`):
Aithon apex (name/scale/HP/resist wall/ring-of-flame shroud/kit+controller+loot intact,
Finger2 -> Aithon soul), Ember Satyr Warden champion (no soul leak), pool 1 apex + 2 champions,
the 3-tier Aithon soul, **proxy hardened invisible (defensive)**, **both Elysium portals hidden**,
**boss maxTransparency reverted to 0.5**, tags set. `maxTransparency 0.0` line removed.

**Map/Quest - `build_section_surgery.py` + `build_quest_files.py` + `gate_build32_parseback.py`:**
the reachability relocation (landing + return NPC onto comp#2) + round-1's map dressing (strip the
`malepc01` blockout mannequin + 6 orange fire-glow lights, unchanged). QUESTS 256-window + registry
untouched (only the x/y/z ints of an existing boat-dialog trigger change - no new quest registration).

---

## Verification (no heavy build; dry-run into COPIES)

- **py_compile** (bossarena.py, build_section_surgery.py, build_quest_files.py,
  gate_build32_parseback.py): **OK**. **`_check_registry.py`**: **OK** (12 modules, order `525453c0`).
- **DB replay** (module applied to a load of `baseline_build38.arz`): proxy `invisibleInWorld=1`
  + maxT 1.0 + shadows 0; portal1 + portal2 `invisibleInWorld=1` + maxT 1.0 + shadows 0 + mesh
  intact; **boss maxTransparency = 0.5 (reverted, not 0.0)**; boss description/scale 1.9/charFxPak
  ring-of-flame/HP[42k,54k,66k]/defensiveBurn 100/ambush cloud.tex intact; **boss Finger2 -> Aithon
  soul**; champion Champion + no Finger2 leak; pool spawnMax3/championMax2/name1=boss/nameChampion1=champ;
  3 Aithon soul tiers built; **exactly 2 other darksatyrshaman droppers remain**; all modified records
  re-encode cleanly (`write_arz` serialises from the modified cache).
- **DB soul-gate battery** (over the replayed db): **PASS** - `_verify_no_unclassified_soul_leaks`,
  `_gate_common_soul_leaks`, `_verify_soul_augments_resolve`, `_verify_soul_itemskill_activation`
  (1390 souls), `_verify_soul_naming`.
- **Map dry-run** (inject-then-remove into a COPY of the canonical `boss_arena` blob): 0x05
  **30 -> 37 -> 36** (6 lights + return NPC injected, mannequin de-placed); return NPC lands at
  exactly local **(136,27,104)**; 6 lights present; mannequin gone; **0x06 / 0x09 / 0x0b (NAVMESH) /
  0x17 BYTE-IDENTICAL**; blob parses to exact end (1,286,233 B).
- **Survey** (canonical 60a62880): landing (132,104) + return (136,104) both **comp#2/92026, clr 100%**;
  landing 26u from the r20 trigger center (outside).
- **Quest**: HELOS_HUB_TRAVEL + TESTHUB_MASTER_DESTS bossarena = `(-429,27,-3538)`; boat-dialog
  signed-int packing round-trips; 17 distinct traveler NPCs (warden law).
- **Portal disjointness**: 0 other DB records reference either portal (edit is contained).

Evidence probes (session scratchpad): `b43r2_probe.py`, `b43r2_probe2.py` (comp#2 footprint +
landing/return survey), `b43r2_db.py`, `b43r2_db2.py` (portal/proxy/volume records + the 1003-proxy
proof), `b43r2_soul.py` (dropper count), `b43r2_replay.py` (DB replay + gate battery),
`b43r2_mapdry.py` (map inject/remove + navmesh byte-identity).

---

## IN-GAME CHECKS for Will's DEV tour (restart Steam first)

1. **Reachability (the CRITICAL one):** Helos -> Boss arena traveler -> you now materialise **on the
   marble arena dais** (not a low floor below it); walk N a few steps -> Aithon + 2 wardens spawn;
   the fight is fully walkable; the return NPC is right beside the landing.
2. **Gray planes:** gone? If any remain, are the ring **columns marble** (art loads) or gray
   (packaging escalation)?
3. **Green blob:** gone with the Elysium portal hidden + the encounter firing in-arena?
4. **Boss feel / grander-donor call** (Aithon vs `um_clytius` Gigante); reward sufficiency.

## Residual / coordination notes
- The SV-native `portal_olympianarena2` GridExitOneWay on the dais is a vestigial bonus exit; its
  destination is engine-grid-resolved and may be inert - the **return NPC is the reliable exit**.
  Flagged for the tour.
- `build_quest_files.py` is co-owned with the Helos-hub lane; this wave changes only the bossarena
  landing tuple. `b44-landing-clearance`'s occupancy gate will pass (new landing is 100% clear).
- Physical Olympus braziers + a bespoke "Aithon's Ember" relic remain optional round-3 enrichment
  (round-1 open items 4-5), unchanged.

## Ban / law compliance
Worktree only (never touched main); no heavy build (blob parse + dry-run inject into copies + DB
replay); no git config mutation, no push; SV DESIGN mutations confined to this arena's own chain
(boss/champion/pool/soul/proxy/portals - all disjoint, this arena's restoration); no TQ/Steam
interference; QUESTS 256-window + registry untouched; navmesh byte-identity proven (arena 0x0b +
every other level); every placement on-mesh (survey); every referenced asset resolves; crash laws
respected (no clone_record soul, no dtype on the champion clone, no Pet.tpl equipment, FX via
charFxPakRunningNames on the monster); no em dashes.
