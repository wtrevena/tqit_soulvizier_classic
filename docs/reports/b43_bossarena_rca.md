# B43 — Boss Arena ("Olympian Arena") RCA (read-only diagnosis)

Branch: `feat/b43-bossarena` (worktree, off `da918c5`). Scope: diagnose why Will's Boss Arena
(reached via the Helos hub traveler, target "Boss arena") shows a vast bare icy/watery floor,
ONE green FX blob with faint ghostly figures mid-floor, and giant blurry gray untextured
planes/beams on approach. **NO fixes applied.** All evidence is from stable ground truth
(`local/Levels_merged.arc` canonical map, `baseline_build38.arz` DB + base-game `database.arz`,
the deployed DEV Resources arcs, `upstream/soulvizier_098i`, `reference_mods/SVAERA_customquest`,
base-game install). Probes: `scratchpad/probe_arena.py`, `probe_arena_pos.py`, `resolve_v2.py`,
`final_probe.py`.

## TL;DR verdict

**NOT "ported wrong."** The arena level blob is **byte-identical to SV 0.98i** in every gameplay
section — same 12 object types, same 30 placed instances, same grid corner. SVAERA never had this
level at all (it is an **SV-only** level carried whole), so there was **no SVAERA-drop** here.
**Missing dropped dress/props/monsters = 0.** Every mesh and texture referenced by every arena
entity and the whole boss chain **resolves** in the shipped base+mod arcs (**0 unresolved meshes,
0 unresolved textures**).

**The truth is "SV shipped a minimal, rough, partly-broken arena, and our faithful port carried the
roughness across (and already fixed one SV bug)."** What Will saw is explained by SV blockout
leftovers, not by our merge dropping content:

| Will saw | What it actually is | Class |
|---|---|---|
| green FX blob + faint ghostly figures, **mid-floor** | the boss encounter firing: the **visible spawn Proxy** `boss_satyrshaman.dbr` (it carries a `mesh` + the translucent `Creatures\Proxy01_Patrol.tex` marker at `maxTransparency 0.5`) at `location_bossarenacenter` (dead center), plus the **3** satyr-shaman minibosses it pools | SV visible-proxy / polish defect |
| giant blurry gray untextured planes/beams | the **portal objects** (`portal_olympianarena1/2`, Elysium portal mesh) textured with base **`System\...\flattexture01/flatbumptexture01`** placeholders — flat gray planes without an active portal shimmer | SV placeholder art |
| vast bare icy/watery floor | the intended **Olympus cloud-arena** aesthetic; the arena is genuinely **sparse** (no loot, no dressing) by SV's design | SV under-built |
| (also present, north edge) a lone standing figure | leftover static **`malepc01` (Class=Player)** mannequin — an SV blockout debug placeholder | SV leftover |

Fix class = **polish + content (amgoz1 bar)**, not restoration. See §6.

---

## 1. Where the arena lives

| Map | level index | fname | blob |
|---|---|---|---|
| MERGED (`local/Levels_merged.arc`, canonical) | idx **2279** | `Levels\World\BossArena\boss_arena.lvl` | 1,285,801 B, LVL v0x0e |
| SV 0.98i (`upstream/soulvizier_098i/Resources/Levels.arc`) | idx **1002** | same | 888,332 B, LVL v0x0e |
| SVAERA (`reference_mods/SVAERA_customquest/.../Levels.arc`) | **ABSENT** (0 hits) | — | — |

- Level DBR (zone/minimap) = `records/ingameui/teleportmap/zones/olympus/olympus.dbr` → labelled
  **"Olympian Arena"** on the minimap (matches Will's screenshot).
- Grid corner (world x,y,z) = **(-561, 0, -3642)**, identical SV↔merged. 0x05 positions below are
  LOCAL (add the corner for world coords).
- Decompiled editor sources `local/decompiled_sv/.../boss_arena.lvl` and
  `local/decompiled_merged/.../boss_arena.lvl` are **byte-identical** (md5
  `13f8e31f8d4febe5b1f1411d30df73e9`), corroborating the blob-level identity.

---

## 2. Full entity inventory (0x05) — MERGED and SV are identical

Both maps: **12 object types, 30 instances, 0 trailing bytes.** Per-class: DRESS/DECOR 21,
LIGHT 4, QUEST_OBJ 2, PORTAL 2, MONSTER 1. Every distinct record and count is identical between
MERGED and SV 0.98i:

| count | record | class | role |
|---:|---|---|---|
| 9 | `sceneryolympus\structure\city\olympusstoagiant01.dbr` | Decoration | giant stoa/colonnade (ring) |
| 6 | `sceneryolympus\structure\city\olympustholos01.dbr` | Decoration | round temple (ring) |
| 2 | `sceneryolympus\structure\city\olympusstoa04.dbr` | Decoration | stoa |
| 1 | `sceneryolympus\structure\arena\olympusarena01.dbr` | Tile | **arena floor** (center) |
| 1 | `sceneryolympus\structure\arena\arenatemple01.dbr` | Decoration | arena temple |
| 2 | `sceneryolympus\nature\cliff\cliff01.dbr` | Decoration | cliff |
| 3 | `lights\staticlights\15mlight_stat_blue.dbr` | EffectEntity | blue light |
| 1 | `lights\staticlights\25mlight_stat_red.dbr` | EffectEntity | red light (center, y≈32) |
| 1 | `creature\pc\malepc01.dbr` | **Player** | **static PC mannequin** (north, local (141.7,0,189)) |
| 2 | `quests\portal_olympianarena2.dbr` | GridExitOneWay | **return portals** (north edge) |
| 1 | `quests\volume_startolympianarena.dbr` | BoundingVolume | **EnterVolume trigger** (center, r=20) |
| 1 | `quests\location_bossarenacenter.dbr` | QuestLocation | **boss spawn marker** (center) |

Center cluster (dist ≤1.4 from floor-center local (132,130)): the arena floor tile (idx5), the
red light (idx2), the invisible trigger volume (idx9), the invisible spawn marker (idx27).
`malepc01` sits at the far NORTH (local Z≈189), next to the two return portals (Z≈166 / 198).
All 30 instances have **flags=0** (none tracked/unique). Other blob sections: 0x06 terrain
(330,343 B, real heightfield floor), 0x09 (88,651 B), 0x0b navmesh (474,110 B), 0x17 (390,207 B),
0x14 (112 B = **2** binding records on inst28+inst29, the two return portals).

---

## 3. DIFF — SV 0.98i vs our merge

**0x05 (placements): ZERO difference.** No dropped dress/props/monsters (unlike the SVAERA-drop
class we hit at Delphi). Nothing added either. This level was never in SVAERA, so the merge simply
appended SV's copy verbatim.

**Only two intentional divergences, both correct:**

1. **Navmesh (map):** SV blob carries a `0x0a` PTH mesh; MERGED carries a generated `0x0b` RLTD
   navmesh (474,110 B) with `0x0a` stripped. This is the correct **build23** navmesh port (this
   arena is one of the 15 SV-area interiors that got real navmeshes). Not a defect.
2. **Quest trigger (Quests.arc):** SV's `bossarena.qst` STEP-2 `Condition_EnterVolume` watches
   `records\quests\portal_olympianarena.dbr` — **which is placed NOWHERE in the level** (it is a
   `FixedItemTeleport` record, not the BoundingVolume). So in **raw SV the boss never spawns.**
   Our merge already fixes this: `tools/build_quest_files.py:1977 _fix_bossarena_entervolume`
   rewires the volumeRecord to `records\quests\volume_startolympianarena.dbr` — the r=20
   BoundingVolume actually placed at center (0x05 inst9). **Our port is more correct than SV's
   original.** (Verified by parsing both deployed-DEV and SV `bossarena.qst`.)

Interpretation: SV's arena was **authored but never wired/tested to completion** (a boss trigger
that points at an unplaced volume is a smoking gun that it was never play-tested).

---

## 4. Texture / mesh resolution — 0 unresolved

Resolution model (verified): a resource path's leading component names the `.arc` (XPack arcs mount
under `XPack\<name>`); the remainder is the entry path. A custom map resolves from mod Resources
first, then base Resources. Index built over deployed DEV Resources + base install Resources
(116,573 mount paths). Result for **every** arena entity + the full boss chain:

- **9 distinct meshes → all resolve. Every embedded `.tex` inside each mesh → all resolve.**
  The Olympus ring (stoa/tholos/stoa04/arena/temple/cliff) all resolve to **`SceneryOlympus.arc`
  [BASE]** with textures in `SceneryOlympus.arc` + `Effects.arc` (Olympus_Dark env map). `malepc01`
  → `Creatures.arc` [BASE]. The boss satyr mesh/skin (`SatyrShamanStarterBoss.msh`,
  `SatyrNEWDark01.tex`, `SatyrMage01*`) → `Creatures.arc` [BASE]. `cloud.tex` → `System.arc`.
- **No wrong-shadowing:** every base texture resolves to the BASE arc (no mod arc masks them).
- **The two portal records** (`portal_olympianarena1` GridEntrance, `portal_olympianarena2`
  GridExitOneWay) use `XPack\SceneryHades\...\Elysium_from_TOJ_PortalObject_01.msh` →
  `SceneryHades.arc` [BASE], whose textures are **`XPack\system\textures\flattexture01.tex` +
  `flatbumptexture01.tex`** → `System.arc` [BASE]. These are **flat placeholder textures** — the
  portal object is meant to carry a scrolling portal shimmer; with a flat base and no active
  effect it reads as a **blank gray plane**.

**Conclusion:** the "giant gray untextured planes" are **NOT a missing-art / dropped-arc defect**
(everything the arena references is shipped and resolves). Leading explanation = the **portal
objects' flat placeholder textures** (2× return portals at the north edge where the traveler lands,
plus the quest-shown entrance portal). Everything else (marble Olympus structures, arena floor)
should render textured exactly as the mod's working Greek areas do (same base-arc tier,
`SceneryGreece`).

> ONE runtime caveat static analysis cannot fully close: whether the base `SceneryOlympus.arc`
> is actually mounted for this custom map at play time. It **should** be (base Resources always
> mount; Greek/Hades areas prove base scenery loads). In-game tiebreaker: if the ring columns show
> **marble** texture, base Olympus art is loading and the gray planes are only the portals; if the
> **whole ring** is gray, escalate to a resource-path/packaging check.

---

## 5. Encounter wiring — the boss IS wired; identity of the green blob + ghosts

`bossarena.qst` (deployed DEV, 2951 B) flow:

- **STEP 1** `Condition_OnLevelLoad` → `Action_ShowNpc` + `Action_OpenDynGridEntrance` +
  `Action_UnlockFixedItem`, all on `records/quests/portal_olympianarena1.dbr` (the GridEntrance —
  opened globally by name; this is the machinery the Sparta/hub doors also reuse).
- **STEP 2** `Condition_EnterVolume(volume_startolympianarena)` →
  `Action_SpawnEntityAtLocation(entity = records/proxies custom/bossarena/boss_satyrshaman.dbr,
  location = records/quests/location_bossarenacenter.dbr)` (delay 2.0s).

**Spawn chain (all records present in DB):**
`boss_satyrshaman.dbr` (Class **Proxy**, `pool1 → .../pools/satyr_shaman_01.dbr`) →
`satyr_shaman_01.dbr` (Class ProxyPool, `spawnMin=spawnMax=3`, `name1 = boss_satyrshaman_55.dbr`) →
**3×** `boss_satyrshaman_55.dbr` (Class Monster, "Satyr Shaman", boss music `GrkMiniBoss01`).

**The boss is a real, purpose-built fire/volcanic miniboss** (not filler): its skills are a bespoke
arena kit — `arena_flamesurge`, `arena_volcanicorb` (+ immolation/fragmentation modifiers),
`arena_meteor` (also its dying skill), and a `damage_arenafirebonus` fire aura, plus normal/epic/
legendary boss globals + conversion immunity. (Projectile FX use the `SandBox\Chris\
UnarmedProjectile_FX01` placeholder — cosmetic only.)

**What Will saw mid-floor (identified):**
- The **green FX blob** = the **spawn Proxy `boss_satyrshaman.dbr` rendering.** Unlike normal
  invisible spawners, this proxy carries `mesh = Creatures\monster\satyr\satyrmage01.msh`,
  `baseTexture = Creatures\Proxy01_Patrol.tex` (the standard TQ translucent proxy-**patrol marker**;
  confirmed present, a 2.8 KB DDS), `castsShadows = 1`, `maxTransparency = 0.5`, `scale = 1.3`. A
  visible proxy at 50% alpha textured with the patrol-marker = a **faint translucent (green-tinted)
  blob** sitting exactly at `location_bossarenacenter` (dead center = "mid-floor").
- The **faint ghostly figures (plural)** = the **3** `boss_satyrshaman_55` minibosses the pool
  spawns around that point (and/or the proxy's own satyr-mage mesh at 0.5 alpha). The invisible
  `volume_startolympianarena` (BoundingVolume, no mesh) and `location_bossarenacenter` (QuestLocation,
  no mesh) do **not** render — they are not the blob.

So the task's guess "spawn proxy firing with missing art" is close: it is the spawn proxy, but the
art is **present** — the proxy is simply left **visible with a placeholder marker texture** it was
never meant to show in-game. (A tell that the trigger volume is SV copy-paste: its FileDescription
still reads "Quest Update to Kill Charon.")

**Traversal:** the Helos hub traveler `svc_helos_trav_bossarena.dbr` lands the player at world
(-433,0,-3602) = local (128,0,40), the SOUTH apron ~90u short of the center volume; the player walks
NORTH toward the ring and crosses the r=20 center volume → the 2s-delayed spawn fires ahead of them.
Two `portal_olympianarena2` return portals sit at the north edge (0x14-bound, inst28/inst29). No
walk-through/teleport laws are violated.

---

## 6. Verdict + concrete fix plan (for a later fix wave — NOT applied here)

**Verdict: BOTH, weighted to "SV never finished it."** Nothing was ported wrong (0 dropped
entities, all art resolves, navmesh correct, and we already fixed SV's dead EnterVolume). The arena
is faithfully carried SV content that SV itself left **rough and under-built**: a functional but
bare fire-satyr miniboss pit with editor/blockout leftovers on show.

Enumerated defects (what a finished arena needs vs what exists), by fix class:

**A. Polish (kill the "broken" look) — highest ROI, map/DB only, no new mechanics**
1. **Hide the spawn proxy.** Make `records\proxies custom\bossarena\boss_satyrshaman.dbr` a
   non-rendering spawner: drop its `mesh` + `baseTexture` (or set it invisible/`maxTransparency 1`
   with no marker mesh) so no green blob renders. This is the direct cause of Will's "green FX
   blob." (DB change, registry-module contract.)
2. **Remove the `malepc01` static Player mannequin** (0x05 inst22, local (141.7,0,189)) via a
   `remove_0x05_instances_by_dbr`-style surgical strip (byte-clean, 1 instance + no 0x14). It is an
   SV blockout leftover, not gameplay.
3. **Portal render:** confirm in-game whether the two return portals + entrance portal show as gray
   planes; if so, give `portal_olympianarena1/2` a proper portal effect/shimmer (or a solid
   Olympus-appropriate mesh) instead of the `flattexture01` placeholder.

**B. Content (amgoz1 bar) — the arena deserves a real Olympian boss**
4. Replace "3× generic fire Satyr Shaman" with a **singular, named, monster-identity-driven
   Olympian arena boss** in amgoz1's SV 0.98i design voice (cite `amgoz1_design_voice.md`). The
   existing bespoke `arena_*` fire kit (meteor / volcanic orb / flame surge / fire aura) is a strong
   seed to build a proper Titan/Olympian boss on. Honor TOXEUS LORE LAW for naming.
5. **Add a reward:** the arena has **no loot and no chest** (verified: 0 chest/loot strings in the
   blob). A boss arena reached from the hub needs a boss-tier drop / reward chest at
   `location_bossarenacenter` on clear.
6. **Dress the bare floor** (Olympus braziers/statues/spectator dressing) so it is not visually
   empty — SV-faithful placement laws (0x05 via `build_section_surgery` INJECT_SPECS, on-mesh,
   flags=0, no walk-through).

**C. Verify (in-game, restart-Steam-first per standing rule)**
7. Confirm the ring Olympus structures render marble-textured (base-scenery-load tiebreaker, §4).
8. Confirm the encounter fires once from the hub landing and the boss is beatable, and that the
   proxy/mannequin no longer show.

All map placements stay 0x05-on-mesh; the QUESTS 256-window is untouched (bossarena.qst is already
registered — do not touch the registry); untouched levels stay navmesh-byte-identical; crash laws
(no clone_record, no dtype on clones, no Pet.tpl equipment, TTL=[], FX-on-monster) apply to any new
boss record.

---

## Evidence artifacts (scratchpad, reproducible)
- `probe_arena.py` — 3-map 0x05 inventory + section/navmesh diff (proves SV↔merged 0x05 identity;
  SVAERA absent).
- `probe_arena_pos.py` — per-instance local positions + parse of deployed-DEV & SV `bossarena.qst`.
- `resolve_v2.py` — full mesh/`.tex` resolution over base+mod arcs (0 unresolved).
- `final_probe.py` — malepc01/volume/location/pool records, satyr skill kit, arena 0x14 bindings,
  loot scan, hub-quest cross-refs.
