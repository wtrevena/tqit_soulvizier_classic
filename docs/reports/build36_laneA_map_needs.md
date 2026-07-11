# build36 Lane A - MAP-WAVE NEEDS (DB side landed; map/quests side pending)

> Trust: HANDOFF (a coordinated handoff to the map + quests lanes). Lane A (DB) is
> `feat/build36-lane-a`. These two features have their **records in the arz** now;
> the map lane (`tools/build_section_surgery.py` + `tools/svaera_plus_portals.py`)
> and the quests lane (`tools/build_quest_files.py`) must place/trigger them.
> No em dashes. Coords are LOCAL to each host level unless marked WORLD.

---

## A5 - PROPONTIS SUPER BOSS: "Dorus, the Drowned King" (place ONE proxy)

**What the arz now has** (built by `apply_svc_patches._create_propontis_superboss`,
runs after `_create_obsidian_roulette`; register in `_MOD_AUTHORED_SPAWN_PROXIES`
proven by the spawn-eligibility gate):

- boss `records\xpack\creatures\monster\lostsoul\um_dorus_99.dbr` (Boss, band
  [41,57,71], HP [13500,18500,24000], scale 1.6, royalty rig
  `xSQ06_Royalty_NonQuest.msh`, ThunderClap/Thunderball + raise-court summon).
- the lone-boss proxy **`records\drxmap\proxy\q_dorus_lone.dbr`** (chanceToRun 100;
  pool1 = `pools\q_dorus_lone.dbr`; difficultyLimitsFile = `limit_obsidianbosses`
  [1..110]; placementExtents 4.0; accessory1/Epic1/Legendary1 = the Boss-locked
  Dorus's-Hoard chest chain). Pool = 1 guaranteed king + 2 royal-guard champion
  escorts (spawnMax=3 / championMin=Max=2, the boss-guarantee LAW).
- TESTHUB-only yard proxy `records\drxmap\proxy\q_yard_dorus.dbr` (+ pool).

**HOST LEVEL (byte-verified from the canonical map by the spec):**
`XPack\Levels\Area02_Medea\Undergrounds\Medea_TempleUG_Tomb01.lvl` (level index
[784], corner/world-origin ints_raw[6,7,8] = **(260, 0, -8522)**; base-game XPack
level, 0x05 = 243 instances, 0x0b navmesh 213,377 B). This is the innermost
Propontis tomb that holds the ENTIRE xSQ06 "Hidden Treasure of Dorus" quest and
King Dorus's questline shade.

**PLACEMENT (map lane - INJECT_SPECS append-only, the Obsidian `tombobs*` /
native-XPack-level 0x05-append branch; RE-SURVEY + nudge +/-2u on the built map):**

- PRIMARY spot (recommended): LOCAL **(52.0, 1.2, 60.0)** = WORLD **(312, 1.2, -8462)**.
  The largest clean open disc (~9u, all-3-tilesets 100% on-mesh, flat floor Y~1.2),
  in the great hall ON the approach between the north crypt entrance and the SW
  treasure vault, so the drowned king bars the way to his own hoard. ~37u from the
  questline Dorus shade (inst [37] at WORLD (276,-8472)) and clear of every xSQ06
  object.
- ALT-A (aggressive "sitting on the treasure"): LOCAL (26.0,1.2,52.0) = WORLD
  (286,-8470), vault mouth (~10u from the shade).
- Inject shape = the `q_leinth_lone` / Vashkarr / broodmother lone-boss tuple
  (flags=0 exemplar rotation, no 0x14): `(b'records\\drxmap\\proxy\\q_dorus_lone.dbr',
  52.0, 1.2, 60.0, {'rot': <q_leinth exemplar rot>})`.
- TESTHUB yard: `q_yard_dorus.dbr` in the HV01 monster yard (SVC_TEST_HUB-gated).

**xSQ06 NO-BREAK gate (append-only proof):** the 9 `xsq06_chest a/b/c` containers +
the 5 kingschest reward proxies + the King Dorus shade instance must be
byte-UNCHANGED in the rebuilt Tomb01 blob. The boss proxy is a NEW append; do not
overlap or displace any xSQ06 instance (full list in the spec's section 1c).

**Deploy coupling:** arz (records) + Text (new tags) ship together; the canonical
`Levels.arc` changes ONLY when the map lane injects the one proxy on Tomb01. The
placement is inert until BOTH the arz records and the map placement exist -> ship
them in the same wave. No Quests change (pure proxy placement).

**Map gates to run:** parse-back (Tomb01 0x05 count 243 -> 244, the appended proxy
flags=0 exemplar-rot, EVERY other section incl the 0x0b navmesh byte-identical);
on-mesh re-verify in all 3 tilesets; navmesh 24/24; groups-bindings; MAP-REF-1
(`run_contracts.py --only map` vs the new arz) 0 P0/P1; collision guard vs every
xSQ06 instance; det-2x both variants. First native-XPack-underground injection -
test the Tomb01 parse-back first (the Obsidian base-Orient precedent is byte-clean).

---

## A6 - WARDEN SPLIT-FIX (retire the double-placed hub master)

**Root cause (byte-proven, warden spec H1):** the single
`records\quests\svc_testhub_master.dbr` was PLACED in TWO levels (Helos /
StartingFarmland06D AND the blood cave / Random09A). `Action_BoatDialog` binds its
menu to ONE entity resolved from the record path, so the second placement spawned
mute-but-visible (yellow minimap dot, no dialog). Everything else (record shape,
trigger, canonical inertness) is byte-identical to the working Almyros NPC.

**What the arz now has** (Lane A DB side, `apply_svc_patches._create_testhub_portal_npcs`):
the TWO split master records, each cloned from the Knossos boatman, reusing the SAME
name/chat tags (NO Text change):
- `records\quests\svc_testhub_master_helos.dbr`
- `records\quests\svc_testhub_master_cave.dbr`

(The original `svc_testhub_master` record is KEPT for now so the current
build_quest_files trigger does not dangle; the map/quests wave RETIRES its placement
+ trigger. Record-diff for A6 = 2 ADDED.)

**QUESTS lane needs** (`tools/build_quest_files.py` `_add_testhub_portal_travel`, ~the
Helos-patch refire step in the always-loaded `sv_commonmechanics.qst`; NOT a Lane A
file):
- Emit **three** triggers instead of one: `svc_testhub_master_helos` (7 ports),
  `svc_testhub_master_cave` (7 ports), `svc_testhub_return` (2 ports). Bump the
  trigger `max` **+3** (was the existing count for the single master + return).
- Update the fail-loud ref-count asserts (each master NPC +7, return +2; the shared
  per-tag `Counter` deltas recompute, e.g. `tagSVCHelosToGarden` now +2 across the
  two masters). No leak onto `portal_master_helos` (Almyros untouched).
- Retire the OLD `svc_testhub_master` trigger (the 7 ports move to the two split
  records).

**MAP lane needs** (`tools/build_section_surgery.py` `build_hub_extra_specs`,
SVC_TEST_HUB-gated; NOT a Lane A file):
- Point the Helos placement (`HELOS_HOST_KEY` / startingfarmland06d, local
  ~(79.5,0.8,189.5)) at `svc_testhub_master_helos.dbr`, and the blood-cave placement
  (`R09_KEY` / random09a, local ~(32.0,1.0,45.0)) at `svc_testhub_master_cave.dbr`
  (two new DBR path constants). Coords unchanged. STOP placing `svc_testhub_master`.
- Cheap H5 insurance: nudge the Helos master farther from the canonical Almyros NPC
  (e.g. local ~(86,.,189), ~10u, still on-mesh) so clicks cannot be stolen.
- This is a TESTHUB-only map change; canonical `Levels.arc` stays byte-identical.

**Gates:** record-diff (2 ADDED vs the prior arz); validate_tags PASS (tags reused,
no new Text); contracts quests/souls/resources 0 P0/P1; `gate_testhub_portal_rig`
part B inertness = 0 canonical placements of BOTH split masters + return; parse-back
RIG section (each host = canonical + 1 flags=0 NPC, every other section incl 0x0b/
0x14 byte-identical); det-2x. Coupled deploy: arz + Quests + (unchanged) Text +
TESTHUB Levels.

**Cheap fallback if a full split is not wanted this wave (map-lane-only, no arz/
Quests change):** place `svc_testhub_master` ONCE (Helos only; keep its 7 ports incl
Blood Cave) and drop the Random09A placement. Loses only the area->area hop via the
cave mouth; Helos->anywhere + area->Helos/BloodCave (returns) remain. Guaranteed
correct if H1 holds.
