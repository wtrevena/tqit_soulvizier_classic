# b41 MAP-PASS (round 1) - RESULT: 5 build37 apex bosses placed on the canonical map

> **Trust level: IMPLEMENTED + DRY-RUN VERIFIED (no heavy build).** All placements wired into
> `tools/build_section_surgery.py` `B41_SPECS` -> `INJECT_SPECS`; verified by targeted dry-run
> injection into a COPY of the canonical map's blobs + independent on-mesh re-survey. The canonical
> map build + deploy is DEFERRED to a later consolidated wave (other waves own MAIN + the build
> machine, 2026-07-13). Branch `feat/b41-map-pass`. House style: no em dashes.

## 0. What shipped in this pass

23 static `0x05` placements across 8 host levels, wiring the 5 accumulated build37 DB-complete apex
bosses + their horde / chest / court set-pieces onto the CANONICAL map. This is the MAP lane placing
EXISTING DB record paths (it authors **no** DB records). Every entry is an append-only `0x05`
instance: it adds NO `QUESTS(0x1b)` registration, shifts NO 256-window slot, changes NO navmesh
(`0x0b`), and creates NO walk-through teleport. Byte-shape = the shipped UBERBOSS / BROODNEST /
ENSLAVER exemplar exactly (`flags=0`, `Q_LEINTH_EXEMPLAR_ROT`, no `0x14`).

| # | set-piece | host level (blob ver) | placements |
|---|---|---|---|
| 1 | Polis Daemonai warden cage | `hadespalace_floor04_01` (v0x0e) | 12 (guardian + 6 jailers + 5 chests) |
| 2 | Menoetes, Marshal of the Dead | `hadespalace_floor_03` (v0x0e) | 1 |
| 2b | 3 general honor-guard pairs | `crystal_03` / `floor04_04` / `crystal_04` (v0x0e) | 3 |
| 3 | The Helepolis (Diadochi) | `elysian_fields_03` (v0x11) | 1 |
| 4 | Neferkha frost court | `thebesopttomba` (v0x0e) | 5 (court + 4 sarcophagi) |
| 5 | Toxeus entrance ambush | `drxfirstroom` (v0x0e) | 1 |
| 6 | Garden-NPC removal | (first-cave chain) | **NO-OP** - nothing to remove (see 5) |

Records exist first (MAP-REF-1): `scratchpad/b41_probe.py` re-resolved all 47 map-placed + backing
paths in `baseline_build38.arz` (build38a-dev DB) this pass -> **exact-miss = 0**.

## 1. Placed coordinates (LEVEL-LOCAL; world = local + grid corner)

All coords are exactly as wired in `B41_SPECS`. Survey = `tools/debug/b41_resurvey.py` (committed) vs
`local/Levels_merged.arc` (build36a canonical, **md5 60a62880**), all 3 tilesets. Every placement is
**on-mesh (d <= 0.14u) in main component #1**. `clr` = worst of N/E/L. `*` = clearance < 95% (a tight
cell; still on-mesh comp#1 - the in-game clip check is the final gate, per polis spec 8.4).

### 1.1 POLIS DAEMONAI cage - `hadespalace_floor04_01` (v0x0e, corner -1199,1,-17307), 0x05 75 -> 87

| entity | record | local (x, y, z) | clr | on-mesh |
|---|---|---|---|---|
| GUARDIAN Alkyoneus | `drxmap\proxy\q_polisgaoler_lone` | (72.1, 3.2, 37.1) | 100% | comp#1 OK |
| H1 Behemoth jailer | `xpack\quests\proxies\scripted\ss_warden_behemoth` | (66.0, 3.6, 37.5) | 100% | comp#1 OK |
| H2 Behemoth jailer | `ss_warden_behemoth` | (78.2, 3.6, 37.5) | 89%* | comp#1 |
| H3 Limos daemon | `drxmap\proxy\q_polis_limos` | (67.1, 3.6, 41.5) | 93%* | comp#1 |
| H4 Melinoe witch | `drxmap\proxy\q_polis_bloodwitch` | (77.1, 3.6, 41.5) | 80%* | comp#1 |
| H5 Gigantes Vindicator | `drxmap\proxy\q_polis_vindicator` | (66.4, 3.6, 36.2) | 88%* | comp#1 |
| H6 Gigantes lieutenant | `drxmap\proxy\q_polis_lieutenant` | (77.5, 3.6, 36.2) | 83%* | comp#1 |
| C1 Majestic chest | `drxitem\container\svc_polisvault_chest_01` | (65.2, 3.6, 32.6) | 74%* | comp#1 |
| C2 Majestic chest | `svc_polisvault_chest_02` | (68.5, 3.6, 30.5) | 100% | comp#1 OK |
| C3 Majestic chest (apex) | `svc_polisvault_chest_03` | (72.1, 3.6, 29.5) | 100% | comp#1 OK |
| C4 Majestic chest | `svc_polisvault_chest_04` | (75.5, 3.6, 30.5) | 100% | comp#1 OK |
| C5 Majestic chest | `svc_polisvault_chest_05` | (78.8, 3.6, 32.6) | 89%* | comp#1 |

The 6-body horde = 2 native Behemoth jailers (reuse `ss_warden_behemoth`, zero new record) + Limos +
Melinoe + Gigantes Vindicator + Gigantes lieutenant. The native `z_wardenchestc` (old skeleton chest)
is KEPT (zero native edits -> 6 chests total); the exactly-5 removal is a gated option NOT taken.
The confined ~21x14u cell is deliberately crammed (a scale-3.5 giant + 6 adds + 5 chests) - the 74-93%
clearances are the "genuinely tight" spots polis_cage_uberboss_spec 2.4/8.4 flags; every one is
on-mesh comp#1, not off-mesh and not an isolated island.

### 1.2 MENOETES + general guard-pairs (all v0x0e)

| entity | record | host | local (x, y, z) | clr | on-mesh |
|---|---|---|---|---|---|
| Menoetes, Marshal | `drxmap\proxy\q_hadesmarshal_lone` | `floor_03` (corner -1491,-9,-16846) | (155.7, 11.5, 102.3) | 100% | comp#1 OK |
| Guard pair A (Dysnomion) | `drxmap\proxy\q_general_a_guardpair` | `crystal_03` (-1800,0,-15769) | (27.83, 27.0, 44.39) | 93%* | comp#1 |
| Guard pair B (Makaria) | `drxmap\proxy\q_general_b_guardpair` | `floor04_04` (-1474,0,-17087) | (68.39, 15.0, 40.26) | 100% | comp#1 OK |
| Guard pair C (Trophonios) | `drxmap\proxy\q_general_c_guardpair` | `crystal_04` (-1302,0,-17793) | (72.46, 27.0, 55.98) | 100% | comp#1 OK |

Menoetes' Y=11.5 is native-confirmed to 0.01u (nearest native at 11.49). The guards are SEPARATE
proxies, invisible to xSQ27's `Condition_KillAllCreaturesFromProxy` (which tracks only the three
`xsq27_namedhero` proxies) -> killing the generals still completes the quest. Guard Y = the general's
own floor Y (A/C 27, B 15), read from the canonical map.

### 1.3 HELEPOLIS / NEFERKHA / TOXEUS

| entity | record | host (ver, corner) | local (x, y, z) | clr | on-mesh |
|---|---|---|---|---|---|
| Helepolis (Diadochi) | `drxmap\proxy\q_diadochi_lone` | `elysian_fields_03` (v0x11, -156,-48,-13871) | (20.7, **4.0**, 81.7) | 100% | comp#1 OK |
| Neferkha court | `drxmap\proxy\q_neferkha_lone` | `thebesopttomba` (v0x0e, -3614,0,5946) | (32.0, 1.0, 85.0) | 100% | comp#1 OK |
| sarcophagus A (W) | `drxmap\proxy\q_sarcophagus_a` | `thebesopttomba` | (25.0, 1.0, 85.0) | 100% | comp#1 OK |
| sarcophagus B (E) | `q_sarcophagus_b` | `thebesopttomba` | (39.0, 1.0, 85.0) | 88%* | comp#1 |
| sarcophagus C (S) | `q_sarcophagus_c` | `thebesopttomba` | (32.0, 1.0, 79.0) | 83%* | comp#1 |
| sarcophagus D (N) | `q_sarcophagus_d` | `thebesopttomba` | (32.0, 1.0, 91.0) | 100% | comp#1 OK |
| Toxeus ambush | `drxmap\proxy\q_bloodtoxeus_ambush` | `drxfirstroom` (v0x0e, 5499,0,3051) | (100.0, 1.0, 50.0) | 100% | comp#1 OK |

## 2. Corrections found this pass (vs the design-plan sketch)

1. **Area08_HadesPalace hosts are `v0x0e` (base-56), NOT `v0x11`.** A direct blob-version read of the
   canonical map confirms every HadesPalace host + ThebesOptTombA + drxFirstRoom is `v0x0e` ->
   `inject_into_sv_only_blob` (base-56); only Elysian_Fields_03 is `v0x11` -> `inject_into_0x05_v11`
   (base-72). This corrects `four_generals_upgrade_spec.md`'s v0x11 claim. The svaera step-6 inject
   loop dispatches by ACTUAL blob version, so each host routes to the proven injector automatically.
2. **Neferkha host key = `levels/world/egypt/minidungeons/thebesopttomba.lvl`** (base-game Egypt path),
   NOT the plan sketch's `xpack/levels/egypt/...`. `INJECT_SPECS` uses EXACT-match keys, so the wrong
   key would have been a silent no-injection. The exact key was read from the map's level index.
3. **Helepolis Y = 4.0, NOT 1.0.** The Elysian meadow floor at (20.7,81.7) is `y=4.0` (navmesh height
   calibrated over 74 native instances + the nearest native both read 4.0; `scratchpad/b41_elysian_y.py`).
   At `y=1.0` the scale-3.2 colossus sinks ~3u below the meadow. Placed at 4.0.

## 3. Item 6 - Garden-NPC removal is a canonical NO-OP (nothing to remove)

A full first-cave `0x05` dump (`scratchpad/b41_firstcave.py`: `Random09A`, `BC_initialpathway`,
`drxFirstRoom`, `drxFirstxistion_connection`, `HiddenValley01`) finds **NO Garden / portal / traveler
NPC** - only native content (shrine ghost-casters, tropical spiders, the shrine-hades proxy, the widow
letter/letterdrop, NpcWanderPoints, `silkroad_villager4`, the respawn temple, `caravan_silkroad`). A
map-wide scan for `trav_/portal_/garden/boat/master` returns only native boatmen + `portal_master_helos`
(Helos) + `portal_master_olympus` (Rhodes) + the GardenofMerchants **interior** records - zero Garden
NPC in any cave. The A1 walk-through Garden door was already removed 2026-07-12.

**So item 6 is already satisfied on the canonical/Steam map.** No removal spec is added (inventing one
risks stranding the Garden). Canonical Garden access stays via `portal_master_helos` at Helos, whose
boat-dialog still lists "Garden of Merchants". **Flagged for Will (open question 5).**

## 4. Gates (no heavy build)

All run against `local/Levels_merged.arc` (md5 60a62880) via the project tooling.

### 4.1 Dry-run placement injection into a COPY of each host blob (`scratchpad/b41_dryrun.py`) - PASS

For each of the 8 hosts, the wired `INJECT_SPECS` was injected into a COPY of the host blob (v0e via
`inject_into_sv_only_blob`, v11 via `inject_into_0x05_v11`, the exact svaera step-6 dispatch), then
verified with `blob_diff.compare_blobs`:

```
host                         ver    0x05         sections-changed  reparse coords/flags0
hadespalace_floor04_01.lvl   v0x0e  75 -> 87 (+12)   ['0x05']        OK      OK
hadespalace_floor_03.lvl     v0x0e  262 -> 263 (+1)  ['0x05']        OK      OK
hadespalace_crystal_03.lvl   v0x0e  27 -> 28 (+1)    ['0x05']        OK      OK
hadespalace_floor04_04.lvl   v0x0e  58 -> 59 (+1)    ['0x05']        OK      OK
hadespalace_crystal_04.lvl   v0x0e  45 -> 46 (+1)    ['0x05']        OK      OK
elysian_fields_03.lvl        v0x11  277 -> 278 (+1)  ['0x05']        OK      OK
thebesopttomba.lvl           v0x0e  155 -> 160 (+5)  ['0x05']        OK      OK
drxfirstroom.lvl             v0x0e  2352 -> 2353 (+1)['0x05']        OK      OK
```

- **`changed=['0x05']` on every host** - the `0x0b` navmesh, the `0x14` metadata, and EVERY other
  section are byte-identical (append-only proof; navmesh integrity; no quest registration).
- **`reparse=True`** - each modified blob re-parses cleanly (section walk reaches the stream end).
- **`coords/flags0=OK`** - all 23 new tail instances read back at the EXACT wired local coords with
  `flags=0` (the exemplar byte-shape).
- Non-target level blobs are untouched (injection operates on extracted copies of the 8 target keys
  only; `data` is never mutated) -> only the 8 intended level blobs change.

### 4.2 QUESTS 256-window parity - PASS (untouched)

`QUESTS(0x1b)` = **255 entries** (the build22 law: 255 in the 256 load window), boundary idx254 =
`xpack2/Quests/x2_StartQuest.qst`, hash `7ad0f054b9f4b9a9`. The injection is `0x05`-only on level
blobs; the top-level QUESTS section byte range is NEVER written, and the code diff is `INJECT_SPECS`
additions only (it does not touch `build_ordered_quest_list`). QUESTS parity is preserved by
construction. No placement authors a quest - these are static monster/chest/proxy instances.

### 4.3 On-mesh re-survey (`tools/debug/b41_resurvey.py`) - PASS

All 23 placements on-mesh (d <= 0.14u) in main component #1 across all 3 tilesets. 13 read 100%
clearance; 10 read 74-93% (the tight Polis cage, tight Neferkha sarco edges, Guard-A) - EXPECTED and
documented, with the in-game clip check as the final gate on the built map.

### 4.4 py_compile - PASS

`tools/build_section_surgery.py` + `tools/debug/b41_resurvey.py` compile clean; `INJECT_SPECS` loads
with the 8 new hosts (23 placements), each spec `flags`-default (rot only), collision-guard green.

## 5. Deferred to the consolidated build wave + open questions for Will

**Deferred (out of this map-pass scope; NO heavy build here):**
- Build the canonical map (`svaera_plus_portals.py`) + re-run the project map gates on the BUILT map
  (`contracts_map`, `verify_merged_bc_navmeshes` 24/24, `tools/debug/b41_resurvey.py <built_map.arc>`),
  then the **in-game clip check** for the confined Polis cage (spec 8.4) + the diadochi scale-3.2 clip.
- The **TESTHUB yard proxies** (`q_yard_polisgaoler`, `q_yard_hadesmarshal`, `q_yard_diadochi`,
  `q_yard_neferkha`) are SVC_TEST_HUB-only and belong in `build_hub_extra_specs()`, NOT the canonical
  fold - a separate TESTHUB task.
- **Neferkha blue-light dressing** (spec 6.6, `5mlight_dyn_blue` add-only) was NOT placed - it is
  optional polish beyond the 5-proxy court and can ride a follow-up if Will wants the frost-blue read.

**Open questions for Will (defaults taken this pass):**
1. **Polis horde density** - shipped all 7 bodies (guardian + 6 adds); the cage is deliberately crammed
   (H2/H4/H6 at 80-93% clearance). Accept with the in-game clip check, or drop to 5 (remove H2+H4)?
2. **Polis chests: 6 (kept the native skeleton chest, zero native edits) vs 5** (remove
   `z_wardenchestc` after the Warden-quest-safety check). Default taken = **6**.
3. **Menoetes location** - placed in the central hall `Floor_03` (WILL_DECISIONS default). Alt = inside
   a general's chamber. Default taken = **Floor_03**.
4. **Neferkha host tomb** - placed in `ThebesOptTombA` (present in the map, v0x0e, 127 KB navmesh,
   91,387-cell main component). **Confirm its CryptEntrance streams the player in**; `QueenTombA` is the
   alternate host if not. Default taken = **ThebesOptTombA**.
5. **Garden-NPC removal (Section 3)** - the canonical first cave is ALREADY clean (nothing to remove).
   Confirm whether Will means the TESTHUB `Random09A` hub's Garden menu option (droppable, TESTHUB-only)
   or considers the order met by the 2026-07-12 walk-through removal.

## Appendix - re-runnable harnesses

Committed: `tools/debug/b41_resurvey.py <map.arc>` (on-mesh gate; default = canonical map).
Scratchpad (session `98075e9c`, `PYTHONIOENCODING=utf-8 py <file>`):
`b41_probe.py` (record resolution + Garden scan + generals coords), `b41_firstcave.py` (first-cave
Garden finding), `b41_resurvey_all.py` (full survey incl. alts), `b41_floory.py` + `b41_elysian_y.py`
(floor-Y grounding), `b41_dryrun.py` (dry-run injection + QUESTS/navmesh/blob-diff gates).
