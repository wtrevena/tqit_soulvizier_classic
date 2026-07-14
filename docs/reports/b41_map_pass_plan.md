# b41 MAP-PASS - complete on-mesh placement plan for the build37 DB-complete bosses

> **Trust level: DESIGN + SURVEY (sign-off-first).** Read-only recon + survey. NO placement edits
> and NO heavy build were performed. This plan hands a map-lane implementer everything needed to
> add the six accumulated map deltas in ONE consolidated wave. Produced 2026-07-13 on branch
> `feat/b41-map-pass` (worktree, off `da918c5`). House style: no em dashes.

## 0. Scope, ground truth, concurrency

Six accumulated map deltas whose DB records already ship (build37 content -> build38a-dev arz), but
which have NEVER been placed on the canonical map:

1. **Polis Daemonai Warden Cage** - Alkyoneus the Soul-Gaoler + horde + 5 majestic chests
2. **Menoetes, Marshal of the Dead** + 3 general honor-guard pairs
3. **The Helepolis** (Diadochi Siege Strider)
4. **Neferkha, the Rimebound Pharaoh** frost court (Cold Tombs Tier-1)
5. **Toxeus entrance ambush** proxy
6. **Garden-portal-NPC removal** from the first cave (Will's standing order)

**Ground truth used (read-only):**
- Canonical map: `local/Levels_merged.arc` (build36a, **md5 60a62880**, 688,682,781 B) - surveyed for
  every on-mesh coord below. Base-game host navmeshes are byte-identical base-vs-merged, so surveys hold.
- Record paths: `scratchpad/baseline_build38.arz` (build38a-dev DB, 51,007 records). Every map-placed
  record path was resolved here (Section 3).
- DB-complete modules: `tools/patches/{polis_vault,four_generals,diadochi,neferkha,toxeus_suite}.py`.
- Specs (predecessor session `fc31fa12`): `polis_cage_uberboss_spec.md`, `four_generals_upgrade_spec.md`,
  `diadochi_uberboss_spec.md`, `cold_tombs_finish_spec.md`, `toxeus_encounter_suite_spec.md`,
  `WILL_DECISIONS_2026-07-11.md`.

**Concurrency (2026-07-13):** other waves own MAIN + the build machine. This plan is survey/planning
ONLY. The canonical map build is DEFERRED to a later consolidated wave. Do NOT run
`svaera_plus_portals.py` / `build_svc_database.py` here.

**Placement-state finding:** NONE of these six are on the canonical map. The five `q_*_lone` boss
proxies and the guard/horde/sarcophagus/ambush proxies appear ONLY in `tools/patches/*.py` (the DB
modules) - never in `build_section_surgery.py` INJECT_SPECS or `svaera_plus_portals.py`. The build36
`UBERBOSS_SPECS` (build_section_surgery.py:969) placed a DIFFERENT five (Dorus, Tantalus, Charon,
Mnemophage, Ephialtes); these build37 five are the next tranche.

---

## 1. Global map laws honored by this plan

- **QUESTS 256-window parity (build22 law) is untouched.** Every placement below is a static `0x05`
  monster / chest / decoration / proxy instance. NONE adds a QUESTS(0x1b) registration or shifts the
  256 window. No quest is authored. (The generals' own quest xSQ27 is untouched - guards + marshal are
  SEPARATE proxies invisible to the quest's `Condition_KillAllCreaturesFromProxy`.)
- **Navmeshes byte-identical.** All deltas are `0x05` appends (or one optional `0x05` removal); no
  `0x0b`/`0x0a` geometry changes. Every host's navmesh is byte-unchanged; the merged-map 24/24
  navmesh gate stays green.
- **No walk-through teleports (TRAVEL LAW).** The only travel touched is item 6 (a REMOVAL).
- **Append-only, exemplar byte-shape.** Every injected proxy/monster uses the proven `q_leinth_lone`
  exemplar (`Q_LEINTH_EXEMPLAR_ROT`, flags=0, no `0x14`) - identical to the shipped roulette /
  broodnest / UBERBOSS placements. Chests (FixedItemContainer) inject flags=0 identity-rot, no `0x14`.
- **Records exist first (MAP-REF-1).** All record paths already resolve in build38a (Section 3), so the
  map lane places EXISTING paths - it authors no DB records.

### 1.1 CORRECTION - host blob versions + injection branch (verified this pass)

The `four_generals_upgrade_spec.md` claims the Area08_HadesPalace hosts are `v0x11 / 72-byte`. **This
is WRONG.** A direct blob-version read of the canonical map shows **every Area08_HadesPalace level is
`v0x0e` (base-56)**, exactly like the polis host. The correct injection branch for the Hades hosts is
the **base-56 `inject_into_sv_only_blob`** path (the same branch M4 Dorus + the roulette + broodnest
use), NOT `inject_into_0x05_v11`. `MOVE_SPECS` is unsupported on v0e (fail-loud) - all Hades deltas are
append-only.

| Host level | version | base | inject branch |
|---|---|---|---|
| `HadesPalace_Floor04_01` (Polis) | **v0x0e** | 56 | `inject_into_sv_only_blob` |
| `HadesPalace_Floor_03` (Menoetes) | **v0x0e** | 56 | `inject_into_sv_only_blob` |
| `HadesPalace_Crystal_03/Floor04_04/Crystal_04` (guards) | **v0x0e** | 56 | `inject_into_sv_only_blob` |
| `Elysian_Fields_03` (Helepolis) | **v0x11** | 72 | `inject_into_0x05_v11` |
| `ThebesOptTombA` (Neferkha) | **v0x0e** | 56 | `inject_into_sv_only_blob` |
| `drxFirstRoom` (Toxeus ambush) | **v0x0e** | 56 | `inject_into_sv_only_blob` (normal blood-cave fold) |

---

## 2. Record resolution (all paths resolve in baseline_build38.arz)

`scratchpad/b41_probe.py` resolved every map-placed record path + its backing monsters/pools/soul in
`baseline_build38.arz`: **TOTAL exact-miss = 0.** Highlights (full list in the harness):

| Boss | map-placed proxy/container paths | resolve? |
|---|---|---|
| Polis | `q_polisgaoler_lone`, `q_polis_{vindicator,lieutenant,limos,bloodwitch}`, `ss_warden_behemoth` (native), `svc_polisvault_chest_0{1..5}`, `q_yard_polisgaoler` | **12/12 OK** |
| Four-Generals | `q_hadesmarshal_lone`, `q_general_{a,b,c}_guardpair`, `q_yard_hadesmarshal` | **5/5 OK** |
| Diadochi | `q_diadochi_lone`, `q_yard_diadochi` | **2/2 OK** |
| Neferkha | `q_neferkha_lone`, `q_sarcophagus_{a,b,c,d}`, `q_yard_neferkha` | **6/6 OK** |
| Toxeus | `q_bloodtoxeus_ambush` (+ `q_bloodtoxeus_lone` pool source) | **2/2 OK** |
| Garden | `svc_helos_trav_garden`, `portal_master_helos` | **2/2 OK** |

Backing monsters (`um_polisgaoler_99`/`_unbound_99`, `svc_um_hadesmarshal_80`, `um_helepolis_99`,
`um_neferkha_99`, the four generals, the horde donors) and the four uber souls
(`svc_uber\{polisgaoler,hadesmarshal,diadochi,neferkha}_soul_l`) all resolve too.

---

## 3. PLACEMENT PLAN, per item

All coordinates are LEVEL-LOCAL (`world = local + grid_corner`). Clearance = fraction of a filled disc
at the proxy's `placementExtents` that is walkable, measured per tileset (Normal/Epic/Legendary) on the
host's own `0x0b`. `d` = nearest-walkable-cell distance (on-mesh when `d<=0.5u`). Surveys:
`scratchpad/b41_survey.py` + `b41_survey2.py` + `b41_discfind2.py` + `b41_survey3.py` vs
`local/Levels_merged.arc`.

### 3.1 POLIS DAEMONAI WARDEN CAGE  (Will's #1 priority - he is standing in it now)

**Target CONFIRMED: `HadesPalace_Floor04_01`** = the SW ground-floor chest cell of the Hades Palace
prison (region banner **"Polis Daemonai" / Prison of Souls**). Byte-verified in the spec: the cell
sits behind gate `z_wardenofsouls_gates` (`locked=1`, FileDescription *"Warden of Souls Gate -- Need
Key from Warden of Souls to Unlock"*) and today holds `z_wardenchestc_proxy` (the single "Majestic
Chest") + caged shades. This is exactly the barred, warden-key-locked cage Will cannot find the boss
in. Host key `xpack/levels/area08_hadespalace/hadespalace_floor04_01.lvl`, v0x0e, base-56,
corner (-1199, 1, -17307). Aggro-through-bars is native to this cell's neighbours (Will approved).

**12 instances** (guardian + 6 horde + 5 chests). DEFAULT keeps the old skeleton chest (6 chests
total, ZERO native edits; the exactly-5 removal of `z_wardenchestc_proxy` is gated on the
Warden-quest-safety check per spec 8.2). Floor Y = 3.2 (guardian) / 3.6 (rest).

| # | entity | record (`records\...`) | local (x, y, z) | survey clr N/E/L |
|---|---|---|---|---|
| 0 | GUARDIAN Alkyoneus | `drxmap\proxy\q_polisgaoler_lone.dbr` | **(72.1, 3.2, 37.1)** | 100/100/100 **OK** |
| H1 | Behemoth jailer | `xpack\quests\proxies\scripted\ss_warden_behemoth.dbr` | (66.0, 3.6, 37.5) * | 96/94/93 |
| H2 | Behemoth jailer | `ss_warden_behemoth.dbr` | (78.2, 3.6, 37.5) * | 87/86/81 |
| H3 | Limos hunger-daemon | `drxmap\proxy\q_polis_limos.dbr` | (67.1, 3.6, 41.5) | 100/100/99 **OK** |
| H4 | Melinoe blood-witch | `drxmap\proxy\q_polis_bloodwitch.dbr` | (77.1, 3.6, 41.5) | 92/88/83 |
| H5 | Gigantes Vindicator | `drxmap\proxy\q_polis_vindicator.dbr` | (66.4, 3.6, 36.2) * | 100/99/98 **OK** |
| H6 | Gigantes lieutenant | `drxmap\proxy\q_polis_lieutenant.dbr` | (77.5, 3.6, 36.2) * | 92/87/87 |
| C1 | Majestic chest | `drxitem\container\svc_polisvault_chest_01.dbr` | (65.2, 3.6, 32.6) * | 100/96/87 |
| C2 | Majestic chest | `svc_polisvault_chest_02.dbr` | (68.5, 3.6, 30.5) | 100/100/100 **OK** |
| C3 | Majestic chest (apex) | `svc_polisvault_chest_03.dbr` | (72.1, 3.6, 29.5) | 100/100/100 **OK** |
| C4 | Majestic chest | `svc_polisvault_chest_04.dbr` | (75.5, 3.6, 30.5) | 100/100/100 **OK** |
| C5 | Majestic chest | `svc_polisvault_chest_05.dbr` | (78.8, 3.6, 32.6) * | 100/100/100 **OK** |

`*` = **inward-nudge refinement** produced this pass (H1/H2/H5/H6/C1/C5 pulled ~1-1.5u toward cell
centre). The spec-primary coords (H1 65.1,38.1 / H2 79.1,38.1 / H5 65.6,35.5 / H6 78.6,35.5 / C1
64.5,33.1 / C5 79.5,33.1) are on-mesh (d=0) but read 46-90% clearance because the ~21x14u cell walls
clip the extents discs - exactly the "genuinely tight" flag in spec 2.4/8.4. The nudged coords above
improve them (H5 and C5 to 100%, C1 to 87-100%, H1 to ~94%). **H2/H4/H6 remain 81-92%** - the cell is
simply small; a scale-3.5 giant + 6 adds is deliberately crammed. This is the load-bearing in-game
clip pass (spec 8.4): accept it (a caged fight, minor wall overlap is cosmetic) OR shrink the horde to
4 (drop H2+H4). **Recommend: ship the nudged coords + do the in-game clip check.**

- **Injection:** all 12 append-only into Floor04_01's `0x05` via `inject_into_sv_only_blob` (base-56),
  flags=0, `Q_LEINTH_EXEMPLAR_ROT` for the proxies, identity-rot for the chests. No `0x14`. `0x05`
  count 75 -> 87 (keep-default 6-chest). Every other section (incl `0x0b`) byte-identical.
- **DB coupling / soul-orb / chest-lock:** all handled DB-side already (2-form guardian, orb+soul+
  Boss-lock ride the terminal `um_polisgaoler_unbound_99`). Map lane places EXISTING paths only.
- **Risks:** (a) confined-cell clearance (above); (b) first Area08_HadesPalace v0e injection - run the
  parse-back on Floor04_01 FIRST (0x05 grows, all else identical); (c) exactly-5 removal is gated on
  the quest-safety check - ship the 6-chest keep-default until green.

### 3.2 MENOETES, MARSHAL OF THE DEAD + 3 general honor-guard pairs

Will fought a general and saw no uber beside him. Two fixes: (a) Menoetes in the **central hall
`HadesPalace_Floor_03`** (WILL_DECISIONS binding; the traversal hall met mid-wing among the generals),
(b) two honor guards flanking each of the three generals in their own chambers.

**Menoetes** - `q_hadesmarshal_lone` (1 boss + 2 machae grandmaster-archer champion escorts).
Host `xpack/levels/area08_hadespalace/hadespalace_floor_03.lvl`, v0x0e, base-56, corner (-1491,-9,-16846).
The walkable hall is a north-south run at local x~155.7; both ends are 100%-clean open discs (ext 4.0):

| spot | local (x, y, z) | clr N/E/L | note |
|---|---|---|---|
| **PRIMARY** | **(155.7, ~11.5, 102.3)** | 100/100/100 **OK** | south end (toward Makaria/Trophonios) |
| ALT | (155.9, ~11.5, 168.5) | 100/100/100 **OK** | north end (toward Dysnomion) |

**Floor-Y for Menoetes is build-read** (nearest native was 14.9u away; ~11.5 is an estimate). The
implementer reads the exact `0x0b` cell Y at the chosen spot. Recommend PRIMARY; confirm it sits on the
player's traversal path through Floor_03 (trace the level's GridEntrance links or eyeball in-game).

**Guard pairs** - one `q_general_{a,b,c}_guardpair` proxy (each spawns 2 named champions at
placementExtents 5.0) placed ~6u beside each general's own `xsq27_namedhero` proxy. General coords read
from the canonical map this pass:

| general | host (v0x0e base56) | corner | general at local | GUARD PAIR at local | clr N/E/L |
|---|---|---|---|---|---|
| A Dysnomion | `...hadespalace_crystal_03.lvl` | (-1800,0,-15769) | (27.83, 27.0, 38.39) | **(27.83, 27.0, 44.39)** | 95/94/93 |
| B Makaria | `...hadespalace_floor04_04.lvl` | (-1474,0,-17087) | (62.39, 15.0, 40.26) | **(68.39, 15.0, 40.26)** | 100/100/100 **OK** |
| C Trophonios | `...hadespalace_crystal_04.lvl` | (-1302,0,-17793) | (66.46, 27.0, 55.98) | **(72.46, 27.0, 55.98)** | 100/100/100 **OK** |

Guard-pair Y = the general's own floor Y (A/C = 27, B = 15). Guard A's best flank (+6z) is 93-95% (the
chamber is tight to the -x side, which surveyed 22-26%; do NOT use -6x). B and C flanks are 100%.

- **Injection:** 4 appends (1 marshal + 3 guard pairs) across 4 v0e hosts, `inject_into_sv_only_blob`
  (base-56), flags=0, `Q_LEINTH_EXEMPLAR_ROT`, no `0x14`. Each host's `0x05` count = baseline + 1.
- **Quest-safety:** guards + marshal are SEPARATE proxies; xSQ27 tracks only the three
  `xsq27_namedhero` proxies (untouched). Killing the generals still completes the quest.
- **Risks:** (a) the version correction (Section 1.1) - these are v0e not v11; (b) confirm Menoetes'
  Floor_03 spot is on the traversal path; (c) Guard A at 93-95% (acceptable; a 2-champion pair, minor
  wall proximity). Yard: `q_yard_hadesmarshal` -> TESTHUB hub (Section 6 note).

### 3.3 THE HELEPOLIS (Diadochi Siege Strider)

Host **CONFIRMED `Elysian_Fields_03` (idx 776)**, `xpack/levels/area06_elysian/elysian_fields_03.lvl`,
v0x11, base-72, corner (-156,-48,-13871). The north Siege-Strider battlefield. Place the ONE
`q_diadochi_lone` proxy (1 Helepolis + 2 strider-guard champion escorts, scale 3.2, placementExtents 4.0).

| spot | local (x, y, z) | clr N/E/L | note |
|---|---|---|---|
| **PRIMARY** | **(20.7, ~1.0, 81.7)** | 100/100/100 **OK** | largest clean disc in the north field (~17.4u), room for the colossus |
| ALT-A north | (-2.7, ~1.0, 107.1) | 100/100/100 **OK** | furthest north |
| ALT-B strider line | (32.7, ~1.0, 82.9) | 100/100/100 **OK** | on the reenactment strider line |

- **Injection:** 1 append via `inject_into_0x05_v11` (base-72; the M7/M8 v11 branch), flags=0,
  `Q_LEINTH_EXEMPLAR_ROT`, no `0x14`. Floor Y ~1.0 (flat Elysium meadow; build-read; the diadochi
  module notes the map lane may dial `scale` 3.2 -> 3.0/2.8 if the giant clips on the re-survey).
- **Risks:** scale-3.2 clipping vs the reenactment striders/shrines (the ~17.4u disc has headroom; the
  in-game clip check confirms). No QUESTS/navmesh impact.

### 3.4 NEFERKHA, THE RIMEBOUND PHARAOH (Cold Tombs Tier-1)

The Cold-Tombs concept ships as a frost-court set-piece injected into an already-reachable Egypt
Valley-of-the-Kings tomb (broodmother pattern; NO new geometry/entrance). **Recommended host:
`ThebesOptTombA`** - a base-game optional Thebes/VoK tomb present in the merged map (v0x0e, base-56,
corner (-3614, 0, 5946)), with a 127 KB `0x0b` navmesh and a genuine open north chamber. Frame
calibration was 0.07u (excellent). Host key `xpack/levels/egypt/minidungeons/thebesopttomba.lvl`
(confirm exact index-cased fname at build).

Place `q_neferkha_lone` (boss + 2 frozen-guardian escorts) at the chamber centre + the 4
`q_sarcophagus_{a..d}` hatch proxies ringing it. Floor Y = 1.0.

| entity | record | local (x, y, z) | clr N/E/L |
|---|---|---|---|
| COURT (Neferkha + 2 escorts) | `drxmap\proxy\q_neferkha_lone.dbr` | **(32.0, 1.0, 85.0)** | 100/100/100 **OK** |
| sarcophagus A (W) | `drxmap\proxy\q_sarcophagus_a.dbr` | (25.0, 1.0, 85.0) | 100/100/100 **OK** |
| sarcophagus B (E) | `q_sarcophagus_b.dbr` | (39.0, 1.0, 85.0) | 88/91/88 |
| sarcophagus C (S) | `q_sarcophagus_c.dbr` | (32.0, 1.0, 79.0) | 88/85/83 |
| sarcophagus D (N) | `q_sarcophagus_d.dbr` | (32.0, 1.0, 91.0) | 100/100/100 **OK** |

Sarco B/E and C/S read 83-92% (chamber edge); nudge each ~1u inward (toward 32,85) or accept (they are
low-extent hatch spawners). Court + A + D are clean 100%.

- **Blue-light dressing (spec 6.6):** ADD `5mlight_dyn_blue` (base-game, ADV-verified) instances
  around the court (append-only; v0e forbids MOVE, so add rather than swap; optionally remove nearby
  native orange via `remove_0x05_instances_by_dbr`). Confirm the blue-light record resolves (render gate).
- **Injection:** 5 appends via `inject_into_sv_only_blob` (base-56), flags=0, `Q_LEINTH_EXEMPLAR_ROT`,
  no `0x14`. Plus the blue-light appends.
- **Risks (flag to Will):** (a) **confirm `ThebesOptTombA` is reachable** in the merged map (base-game
  optional tomb via a `CryptEntrance` POI - very likely, but verify the entrance streams); if not,
  `QueenTombA` (305 KB `0x0a`, bigger) is the alternate host. (b) the module wants **>=40u from native
  monster encounters** - the west end of the north chamber (25-32, 81-89) is ~35u from the east-room
  natives; survey the actual MONSTER proxies at build and shift west/south if a native encounter is
  within 40u. (c) the tomb is Act-2 (before Hades) - no IT-cap conflict.

### 3.5 TOXEUS ENTRANCE AMBUSH

Place `q_bloodtoxeus_ambush` (chanceToRun=15; reuses `_BT_POOL` = 1 Blood-Toxeus + 2 blood-demon adds)
in the blood-cave first room. Host `levels/world/xbloodcave/drxFirstRoom.lvl`, v0x0e, base-56,
corner (5499, 0, 3051) (grid-shifted; injected via the normal blood-cave INJECT_SPECS fold +
`inject_into_sv_only_blob`, the same path as the `drxfirstxistion_connection` Enslaver warband).

| spot | local (x, y, z) | clr N/E/L | note |
|---|---|---|---|
| **PRIMARY** | **(100.0, 1.0, 50.0)** | 100/100/100 **OK** | clean, main component (746,928 cells) |
| alts (all 100%) | (200.5,1.0,59.1) / (202.9,1.0,26.9) / (197.7,1.0,65.9) | 100/100/100 | far-side open discs |

- **Injection:** 1 append via `inject_into_sv_only_blob` (base-56), flags=0, `Q_LEINTH_EXEMPLAR_ROT`,
  no `0x14`. Floor Y = 1.0.
- **Risk (low):** confirm PRIMARY (100,50) is on the player's early path from the drxFirstRoom entrance
  (the spec leaves the exact coord to build time; a 15% ambush is low-stakes). If a spot nearer the
  entrance is wanted, any of the alts is 100%-clean.

### 3.6 GARDEN-PORTAL-NPC REMOVAL from the first cave

**Empirical finding (authoritative, this pass):** the canonical map (`Levels_merged.arc` md5 60a62880)
has **NO Garden / portal / traveler NPC in the first-cave chain**. A full `0x05` dump of
`Random09A`, `BC_initialpathway`, `drxFirstRoom`, `drxFirstxistion_connection`, and `HiddenValley01`
found only: native `silkroad_villager4`, NpcWanderPoints, the respawn shrine, `caravan_silkroad`, the
widow `finalletter`/`location_letterdrop`, and monster proxies. A map-wide scan for `trav_/portal_/
garden/boat/master` returned only native boatmen, soul-collectors, `portal_master_helos` (at Helos),
`portal_master_olympus` (Rhodes herald), and GardenofMerchants interior records - **zero Garden NPC in
any cave.** The A1 HV01 walk-through Garden door + swirl + return were already removed 2026-07-12
(`build_section_surgery.py`).

**So item 6 is already satisfied on the canonical/Steam map** - there is nothing left to remove.

**Stranding check (CLEARED):** canonical Garden access = `portal_master_helos` (records\quests\
portal_master_helos.dbr) at Helos `StartingFarmland06D` local (76.5, 0.6, 189.5), whose boat-dialog
lists **"Garden of Merchants"** (-> world 1173,-39,-4001, the caravan_rhodes hub). Removing any
first-cave residual does NOT strand the Garden.

**What Will most likely means + action:** the only "first-cave" traveler is the **TESTHUB-only**
`svc_testhub_master` injected into `Random09A` (SVC_TEST_HUB=1 path in `svaera_plus_portals.py`), whose
5-destination menu includes Garden of Merchants. If Will wants the Garden option gone from that
first-cave hub, drop the Garden destination from the Random09A hub (a `build_quest_files.py` dialog +
`build_section_surgery.py` hub-spec change, TESTHUB-only). The Helos hub `svc_helos_trav_garden`
(TESTHUB) + the canonical `portal_master_helos` both keep the Garden reachable.

**Recommendation:** flag to Will for confirmation - the canonical first cave is already clean, so the
order appears met by the 2026-07-12 removal. If a residual is meant, the removal mechanism is
`remove_0x05_instances_by_dbr(blob, <dbr>, <level_key>)` (build_section_surgery.py) targeting the
specific dbr in the specific first-cave blob.

---

## 4. INJECT_SPECS-ready sketch (for the deferred map wave)

New `B41_SPECS` dict merged into `INJECT_SPECS` collision-guarded (the UBERBOSS/BROODNEST precedent,
build_section_surgery.py:1958-1983). Coords LEVEL-LOCAL; `EXEMPLAR = Q_LEINTH_EXEMPLAR_ROT`.

```python
B41_SPECS = {
  # --- POLIS (v0e base56) : 12 appends, keep-default 6-chest ---
  'xpack/levels/area08_hadespalace/hadespalace_floor04_01.lvl': [
    (b'records\\drxmap\\proxy\\q_polisgaoler_lone.dbr',            72.1, 3.2, 37.1, {'rot': EXEMPLAR}),
    (b'records\\xpack\\quests\\proxies\\scripted\\ss_warden_behemoth.dbr', 66.0, 3.6, 37.5, {'rot': EXEMPLAR}),
    (b'records\\xpack\\quests\\proxies\\scripted\\ss_warden_behemoth.dbr', 78.2, 3.6, 37.5, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_polis_limos.dbr',                 67.1, 3.6, 41.5, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_polis_bloodwitch.dbr',            77.1, 3.6, 41.5, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_polis_vindicator.dbr',            66.4, 3.6, 36.2, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_polis_lieutenant.dbr',            77.5, 3.6, 36.2, {'rot': EXEMPLAR}),
    (b'records\\drxitem\\container\\svc_polisvault_chest_01.dbr',  65.2, 3.6, 32.6, {'rot': EXEMPLAR}),
    (b'records\\drxitem\\container\\svc_polisvault_chest_02.dbr',  68.5, 3.6, 30.5, {'rot': EXEMPLAR}),
    (b'records\\drxitem\\container\\svc_polisvault_chest_03.dbr',  72.1, 3.6, 29.5, {'rot': EXEMPLAR}),
    (b'records\\drxitem\\container\\svc_polisvault_chest_04.dbr',  75.5, 3.6, 30.5, {'rot': EXEMPLAR}),
    (b'records\\drxitem\\container\\svc_polisvault_chest_05.dbr',  78.8, 3.6, 32.6, {'rot': EXEMPLAR}),
  ],
  # --- MENOETES + GUARDS (v0e base56) ---  (Menoetes Y build-read from the 0x0b cell)
  'xpack/levels/area08_hadespalace/hadespalace_floor_03.lvl': [
    (b'records\\drxmap\\proxy\\q_hadesmarshal_lone.dbr',           155.7, 11.5, 102.3, {'rot': EXEMPLAR})],
  'xpack/levels/area08_hadespalace/hadespalace_crystal_03.lvl': [
    (b'records\\drxmap\\proxy\\q_general_a_guardpair.dbr',          27.83, 27.0, 44.39, {'rot': EXEMPLAR})],
  'xpack/levels/area08_hadespalace/hadespalace_floor04_04.lvl': [
    (b'records\\drxmap\\proxy\\q_general_b_guardpair.dbr',          68.39, 15.0, 40.26, {'rot': EXEMPLAR})],
  'xpack/levels/area08_hadespalace/hadespalace_crystal_04.lvl': [
    (b'records\\drxmap\\proxy\\q_general_c_guardpair.dbr',          72.46, 27.0, 55.98, {'rot': EXEMPLAR})],
  # --- HELEPOLIS (v0x11 base72) ---
  'xpack/levels/area06_elysian/elysian_fields_03.lvl': [
    (b'records\\drxmap\\proxy\\q_diadochi_lone.dbr',                20.7, 1.0, 81.7, {'rot': EXEMPLAR})],
  # --- NEFERKHA (v0e base56) + blue lights (add-only) ---
  'xpack/levels/egypt/minidungeons/thebesopttomba.lvl': [
    (b'records\\drxmap\\proxy\\q_neferkha_lone.dbr',               32.0, 1.0, 85.0, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_sarcophagus_a.dbr',              25.0, 1.0, 85.0, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_sarcophagus_b.dbr',              39.0, 1.0, 85.0, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_sarcophagus_c.dbr',              32.0, 1.0, 79.0, {'rot': EXEMPLAR}),
    (b'records\\drxmap\\proxy\\q_sarcophagus_d.dbr',              32.0, 1.0, 91.0, {'rot': EXEMPLAR}),
  ],
  # --- TOXEUS ambush (v0e base56, blood-cave fold) ---
  'levels/world/xbloodcave/drxfirstroom.lvl': [
    (b'records\\drxmap\\proxy\\q_bloodtoxeus_ambush.dbr',         100.0, 1.0, 50.0, {'rot': EXEMPLAR})],
}
```

TESTHUB yard proxies (`q_yard_polisgaoler`, `q_yard_hadesmarshal`, `q_yard_diadochi`,
`q_yard_neferkha`) belong in `build_hub_extra_specs()` (SVC_TEST_HUB=1), NOT the canonical fold - a
parallel TESTHUB-only task, out of the canonical map-pass scope.

---

## 5. Gates + deploy coupling (for the map wave)

- **Map parse-back per host:** `0x05` count = baseline + appended (Floor04_01 75->87; Floor_03/
  Crystal_03/Floor04_04/Crystal_04 each +1; Elysian_Fields_03 +1; ThebesOptTombA +5 (+ blue lights);
  drxFirstRoom +1); every appended instance flags=0 exemplar-rot; `0x14` VERBATIM; EVERY other section
  incl. `0x0b` byte-identical (append-only proof).
- **On-mesh re-verify** all coords on the BUILT map in all 3 tilesets (`survey_uberboss_spots.py`),
  main component #1; do the confined-cell in-game clip check for Polis (spec 8.4).
- **QUESTS parity:** world01.map QUESTS(0x1b) byte-identical (255/256), zero new registrations.
- **Navmesh:** merged 24/24 byte-identical; seam-lattice unchanged.
- **MAP-REF-1:** every placed dbr resolves in the arz (already true, Section 3) - re-assert at build.
- **Deploy coupling:** ships with the build38+ arz + Text (the boss records/souls/tags) as ONE
  canonical map wave. Restart Steam + hash-verify the deploy landed before Will tests (standing rule).
- **In-game:** Polis vault fight (guardian + horde + 5 chests, aggro-through-bars, Key opens gate);
  Menoetes met in Floor_03 + guards beside each general (xSQ27 still completes); Helepolis in the
  Elysium north field; Neferkha frost court in the tomb; Toxeus 15% ambush in drxFirstRoom.

---

## 6. Open questions for Will

1. **Polis horde density.** The ~21x14u cell yields 81-92% clearance on H2/H4/H6 even nudged (Section
   3.1). Ship all 7 bodies (accept minor wall overlap in a cage) OR drop to 5 (remove H2+H4)? Default =
   ship 7 with the in-game clip check.
2. **Polis chests: 6 (keep the old skeleton chest, zero native edits) vs 5** (remove
   `z_wardenchestc_proxy` after the Warden-quest-safety check). Default = 6.
3. **Menoetes location:** central hall `Floor_03` (WILL_DECISIONS default, used here) vs literally
   inside a general's chamber (adjacent `HadesPalace_General_01`, the spec's option i). Default = Floor_03.
4. **Neferkha host tomb:** `ThebesOptTombA` (used here) vs `QueenTombA` - contingent on the reachability
   confirm (Section 3.4 risk a). Default = ThebesOptTombA if its CryptEntrance streams.
5. **Garden NPC removal (Section 3.6):** the canonical first cave is ALREADY clean (nothing to remove).
   Confirm whether Will means the TESTHUB Random09A hub's Garden option (droppable, TESTHUB-only) or
   considers the order already met by the 2026-07-12 walk-through removal.

---

## Appendix - read-only harnesses (re-runnable)

All in `scratchpad/` (session 98075e9c), run with `PYTHONIOENCODING=utf-8 py <file>`:
- `b41_probe.py` - record resolution vs baseline_build38.arz + map-wide Garden-NPC scan + generals coords.
- `b41_firstcave.py` - first-cave chain interactive-entity dump (the Garden-NPC finding).
- `b41_survey.py` / `b41_survey2.py` / `b41_survey3.py` - on-mesh surveys (uses
  `tools/debug/survey_uberboss_spots.py`).
- `b41_discfind2.py` - fast open-disc finder (Floor_03 / ThebesOptTombA / drxFirstRoom).
