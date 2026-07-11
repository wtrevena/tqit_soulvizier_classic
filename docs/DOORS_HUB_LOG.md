# DOORS + TEST HUB + BUILD24/25 FEEDBACK - implementer log (max effort)

> Continuous checkpoint log. Built ON build25 (commit `a70fc6d`, deployed
> `local/Levels_merged.arc` = 688,685,020 B, md5 `c9c8c12aea9f8012c2bb73b5e9a418a1`).
> Reuses the Sparta machinery verbatim (INJECT_SPECS + x14_payload + MOVE_SPECS +
> inject_into_sv_only_blob + inject_rec02_into_blob). Python:
> `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`
> (`PYTHONIOENCODING=utf-8`). Measure everything; C1 is a byte-scan diagnosis, no guessing.
>
> Companion docs: `SPARTA_CORRECTIONS_LOG.md` (the DynGridEntrance+GridExitOneWay+48B-0x14
> portal-pair machinery I mirror), `ENTRANCES_POLISH_LOG.md` (B3 fountain move history + the
> maze03 A1 machinery), `SV_AREAS_CAMPAIGN_LOG.md` (interior navmesh banking; Garden/Secret
> interiors already meshed), `DROPPED_CONTENT_AUDIT.md` (SV exemplar coords), `MODDING_PLAYBOOK.md`.

---

## SCOPE (from the brief)

- **A - TWO MORE INVENTED DOORS** (mirror Sparta exactly, same bossarena.qst record-name open):
  - A1 GARDEN OF MERCHANTS: portal pair from an Orient-side host near the blood-cave/HV01 region
    (prefer HVBorder04 / caravan scene, >=15u from everything) <-> GardenofMerchants donor landing;
    reciprocal return. Unlocks caravan_rhodes Super-Caravan region.
  - A2 SECRET PLACE: portal pair into darkforestenter (the 11-level cluster entry) from a hidden
    host (my pick + rationale; document exact location for Will).
- **B - TEST HUB** (SVC_TEST_HUB=1 env-flag; flag-OFF build BYTE-IDENTICAL to flag-ON minus hub
  entities - prove it). Portal pairs INSIDE THE BLOOD CAVE (Random09A interior near the mouth,
  on-mesh, away from combat/swarm, >=10u spacing) to: (1) maze03 beside the Olympian Arena portal,
  (2) Rhodes secret-passage interior (murderbunny/reflect-statue area - identify exact level),
  (3) SpartaCryptLevel2 landing, (4) darkforestenter, (5) GardenofMerchants. One-way pairs with
  returns to the cave. BUILD AS SEPARATE ARTIFACT: local/Levels_merged_TESTHUB.arc (canonical
  local/Levels_merged.arc stays hub-free).
- **C - BUILD24/25 FEEDBACK FIXES:**
  - C1 RESPAWN POSITION: Will DISPROVED activation-caching. Byte-scan ENTIRE merged map for the
    OLD fountain position (build18-era coords) as float triplets AND any structure keyed by UID
    feeb4bc6ce4e08c0e279b3824244aeeb (SD/0x18, GROUPS payloads, 0x09/0x06). Cross-check a NATIVE
    working respawn shrine. Move EVERY old-coord occurrence to the new position. GATE: zero
    structures retain old coords; fountain structure set matches a native shrine's shape.
  - C2 SPRITE SPAWN VISUAL: add a purple occult pyre/volcano visual anchor AT the sprite spawner
    position (the purple-flame wagon-side occult art); sprite coords unchanged.
  - C3 CARAVAN LAYOUT: wagon on the RIGHT-HAND side of the driver NPC (standard game camera);
    verify + swap if not (in-place moves, position bytes only).
  - C4 SMOKE COVERAGE, BOTH REGIONS: diff SV's FULL atmosphere vs shipped for (a) EVERY
    entrance-section level (HV01 + all borders + approach), (b) the Delphi occultist region
    (DelphiLowlands04), (c) the region-wide env params (SD/0x18 or 0x09 env records). Restore the
    complete SV extent at both regions.

CONSTRAINTS: map tooling only. No DB scripts, donors, Quests.arc. Stale fix_mc_output/hybrid_merge
untouched. No deploy/commit/Workshop. Skip-not-break per item with evidence.

---

## BASELINE (measured)

- `local/Levels_merged.arc` = 688,685,020 B, md5 `c9c8c12aea9f8012c2bb73b5e9a418a1` = build25 (a70fc6d).
- Snapshot for collateral diffs: `local/Levels_merged.build25-baseline.arc` (byte-copy).
- Machinery confirmed present: INJECT_SPECS (23 entries) + MOVE_SPECS (Horse02+villager1) +
  x14_payload path in both AE (step-6/7) and SV-only (inject_into_sv_only_blob) + move_0x05_instances
  + inject_rec02_into_blob(pre_positioned=True). SVC_INTERIOR_PORTALS=1 env flag exists (a model for
  SVC_TEST_HUB gating at INJECT_SPECS build time).

---

## RECON PHASE - measured facts

Recon scripts (read-only): `tools/debug/recon_doors_hub.py`, `tools/debug/recon_c1_bytescan.py`.

### GUIDs (merged-world, for all door destinations)
| Level | merged corner | merged GUID |
|-------|---------------|-------------|
| GardenofMerchants | (1043,0,-4074) | `15f9d3d7214d56d42a2ac6abd6114d78` |
| DarkForestEnter | (-2420,0,-5820) | `1397c8e754491051bcd1be9cc4dd092f` |
| SpartaCryptLevel2 | (-5644,0,-1451) | `797c78594040cba419340c990e6903c4` |
| CataCube02_FloorLast (Sparta HOST) | (-6612,0,-3218) | `817574a8674093619ebf6581db63274c` |
| maze03 | (-8076,0,-3943) | `cdef89ae834a4adf1214609306708c02` |
| Random09A (blood-cave doorway) | (5979,18,3243) | `d840e7ae4a42c504453f13a47940bc55` |
| HVBorder04 | (-134,-104,2302) | `4a5358aded4ae8de9bb76b8e778f2f32` |
| murderbossroom (Rhodes murderbunny) | (-3592,0,-5955) | `2817751af24828502c9d7ea5f0a5c6ab` |
| crypt_floor1 (Uber, A1 existing) | (-2578,0,-2682) | `dbc245c358434e0bb54760b234293cc5` |

### A1 GARDEN OF MERCHANTS door
- DEST GardenofMerchants: donor mesh 1,455,085 cells, **34 comps**. The caravan_rhodes
  (`records\drxmap\zgardenofmerchants\merchants\caravan_rhodes.dbr`) @ local (136.3,-36.1,79.1)
  world (1179.3,-36.1,-3994.9) is in **comp #1 (112,172 cells)** = the merchant-hub component (NOT
  the main comp #0 = 1.33M cells). teleportshrine_gom @ local (153.0,-40.5,86.2) = the SV rift-shrine
  EXIT once discovered. => The Garden door MUST land the player in comp #1 (near the caravan), where
  39,265 openNbr8 cells sit within 5-25u of the caravan. LANDING near caravan e.g. world
  (1176.1,-39.0,-3998.7) local (133.10,-39.00,75.30), 5u from caravan.
- HOST: HVBorder04 caravan scene (current build25 positions): merchant local (35.75,1.62,24.27),
  horse (26.00,1.62,17.00), driver-villager1 (25.50,1.62,22.50), wagon (23.00,1.62,20.00),
  occultistaura (41.01,1.51,21.99), pitspawner (50.70,1.80,34.30). Must place the Garden door
  >=15u from ALL of these. HVBorder04 mesh: recon pending for exact host cell.

### A2 SECRET PLACE door (darkforestenter entry)
- DEST darkforestenter: donor mesh 459,144 cells, 101 comps, main 320,225. Central openNbr8
  landing = world (-2396.1,2.0,-5789.5) local (23.90,2.00,30.50). darkforestenter IS the 11-level
  cluster's entry (SV_AREAS_CAMPAIGN Wave 3a: forest chain darkforestenter<->woodscorner<->
  secretforest2<->pillagedvillage, all internally connected + navmeshed).
- HOST: my pick + rationale = TBD (hidden Greece/Orient spot). See DESIGN.

### B TEST HUB
- Blood-cave Random09A interior: donor mesh 75,962 cells (main comp 75,411), world X[5920,6051]
  Z[3246,3344] = local X[-59,72] Z[3,101]. **107 instances = ALL set-dressing (stalagmites, roots,
  bones, boulders, lights, fog, sounds). ZERO combat/swarm proxies inside** (the beastman swarm is
  on the SURFACE in HiddenValley01, not in the cave). So the cave interior is safe for the hub. The
  player ARRIVES near the AE-Random09A entry (east side); the WEST tunnel leads deeper. 70,674
  openNbr8 cells in main comp = ample room for 5 entrance + 5 return portals at >=10u spacing.
- The Rhodes "murderbunny / reflect-statue" level = **XPack\Levels\Secret_Place\murderbossroom.lvl**
  (GUID 2817751a..); murderbunny @ local (54.00,3.00,34.00). Donor navmesh present (70,910 B).
- 5 hub DESTINATION landings (all on-mesh, computed):
  | Dest | GUID | landing local | note |
  |------|------|---------------|------|
  | maze03 | cdef89ae.. | (293.10,1.20,149.30) | 4.0u from A1 Olympian portal (beside it) |
  | murderbossroom | 2817751a.. | (52.90,3.00,28.10) | near murderbunny |
  | SpartaCryptLevel2 | 797c7859.. | (53.70,-1.60,38.30) | near the SC2 arena landing |
  | darkforestenter | 1397c8e7.. | (23.90,2.00,30.50) | central |
  | GardenofMerchants | 15f9d3d7.. | (133.10,-39.00,75.30) | comp #1 near caravan |
  - maze03 uses its AE Editor-baked 0x0b (in the blob, NOT a generated donor); its landing was
    measured against the blob mesh.

### C1 RESPAWN POSITION - **ROOT CAUSE PROVEN (byte-scan, no guessing)**
The fountain UID `feeb4bc6ce4e08c0e279b3824244aeeb` occurs in exactly **2 places** in the merged map:
1. **GROUPS(0x11) @ section-rel 31588** = the `respawnorient` shrine-group member for the fountain.
2. HiddenValley01 0x05 instance (the fountain itself, already MOVED to (35.70,17.60,143.10) in build24).

The GROUPS respawn-shrine member layout is **stride-44: `UID(16) + levelGUID(16) + position(3xf32,12)`**
(byte-proven: the levelGUID at UID+16 == HiddenValley01 GUID `ce93e328..`, and the position at UID+32).
Verified against NATIVE working shrines: BambooForest03 member pos (118.1,8.2,47.4) == its 0x05 local
coord (POS-MATCH), Connector01 member pos (48.9,-19.6,4.4) == its 0x05 (POS-MATCH). **The engine
respawns the player at the GROUPS-recorded position, which equals every native shrine's 0x05 position.**
- **OUR fountain's GROUPS member position = (49.263,15.634,14.950) = the OLD build18-era local coord**,
  NOT the moved (35.70,17.60,143.10). POS-MATCH=**False**. THIS is why Will respawns at the pre-move
  spot regardless of re-activation (activation-caching correctly disproven - the stale coord is in the
  world map's GROUPS section, baked at build time, not in the save).
- **THE FIX**: rewrite the 12 position bytes at GROUPS section-rel 31620 from (49.263,15.634,14.950)
  to (35.70,17.60,143.10). Surgical GROUPS edit. The 0x05 instance is already correct. GATE: after
  the fix, the fountain's GROUPS member pos == its 0x05 pos (native-shrine parity), and zero structures
  retain the old coords.
- Cross-checks done: SD(0x18) is byte-IDENTICAL SV-vs-shipped (116299 B) and contains NO old fountain
  coord -> SD is not involved. 0x09/0x06 in HV01 contain no old-coord triplet. The ONLY stale copy is
  the GROUPS member position.
- Native-shrine full structure set: a respawn shrine participates in = (a) its 0x05 instance
  (flags=1 + UniqueId), (b) exactly ONE GROUPS respawnorient member (UID+GUID+pos). 26
  respawntempleorient01 instances exist; all 25 natives have GROUPS pos == 0x05 pos.

### C2 SPRITE SPAWN VISUAL (purple occult pyre/volcano anchor)
The sprite spawner `t1_pitspawner_01` is at HVBorder04 local (50.70,1.80,34.30) and ALREADY co-located
with a `pit_fx01` (DRXeffects\other\pitfx.pfx = the purple occult pit flame effect). Will's C2 feedback
(build24/25) wants a SOLID "purple occult pyre/volcano-style visual anchor" there - the current pure-FX
`pit_fx01` alone is not enough of a visual. The wagon-side occult scene's solid pyre/volcano = the Hades
firepit `mc_hades_anouranfirepit02` (Class Tile, mesh MC_Hades_AnouranFirePit02.msh - the volcano/brazier
bowl) + `mc_hades_woodpyre01`. The Delphi "volcano" scene (DROPPED_CONTENT_AUDIT sec 5) is literally
`pit_fx + mc_hades_anouranfirepit`. **C2 FIX**: add `mc_hades_anouranfirepit02` (the firepit/volcano bowl)
AT the sprite-spawner spot (50.70,1.80,34.30); the existing pit_fx01 there provides the purple occult
flame -> together = the purple occult pyre/volcano. Sprite coords UNCHANGED (add-only, no sprite moves).
On-mesh: the spawner spot is 0.00u on-mesh (floorY -102.2). Optionally also add pit_fx01 emphasis (already
present). flags=0, no 0x14 (Tile Decoration).

### C3 CARAVAN LAYOUT (wagon vs driver camera-right) - RESOLVED
TQ camera convention (authoritative, TQ game guides + fandom): the default isometric camera has
**North (+Z) = top of screen**, so **screen-RIGHT = East = +X**. Current build25: driver-villager1 local
(25.50,1.62,22.50), wagon local (23.00,1.62,20.00) -> wagon dX vs driver = -2.50 = wagon is WEST =
screen-LEFT of the driver. **Will wants the wagon on the driver's RIGHT-HAND (screen-right = +X = East)
side -> the wagon is currently on the WRONG side.** C3 FIX: recompose the small caravan cluster so the
wagon sits EAST (+X, screen-right) of the driver, horse hitched in front (south/-Z) of the wagon, all
>=3.5u apart, merchant clickable (>=10u), on-mesh. In-place position-byte moves only (wagon via
INJECT_SPECS coord change; horse+driver via MOVE_SPECS). NOTE: TQ's camera is isometric-diagonal (N-up is
the guide simplification); the left/right call uses the dominant +X=screen-right axis. This is the one
C3 item to eyeball in the walk-test.

### A2 HOST DECISION - rhodes_secretvista_01 (rationale)
**Chosen host = `xpack/levels/area01_rhodes/rhodes_secretvista_01.lvl`** (v0x0f SHARED SVAERA level,
same base-72 inject path as maze03 + Sparta HOST). Rationale: (1) it is literally a "Rhodes Secret
Vista" - a scenic overlook = perfectly thematic for a hidden "Secret Place" door; (2) it is in the SAME
Rhodes region as the Secret Place cluster (secretvista corner (-216,0,-6070); darkforestenter corner
(-2420,0,-5820) - both IT Act 4 Rhodes); (3) it has a large 101,356-cell walkable mesh and ZERO hostile
proxies (peaceful); (4) SV's own Secret Place was entered from a Rhodes underground (scrabledeggs_floor06),
so a Rhodes host is faithful in spirit. HOST cell = a tucked-away east-edge nook: world (-77.5,18.4,-6036.9)
local (138.50,18.40,33.10), 17.8u from any decor (discoverable but not in the player's face). Return-landing
local (137.10,17.00,43.10). WILL walk-test location: reach the Rhodes Secret Vista overlook, look for the
Olympian portal at the east-edge nook.

### A1 HOST DECISION
HVBorder04 is DENSE with the occult scene (lights/sprites/totems/fog fill the north+central area; the only
>=15u-clear cells are at the south map edge). Better host = **HiddenValley01 NORTH, ~15-20u EAST of the
functional Super-Caravan** (caravan_silkroad @ world (-92.3,-102.2,2317.1), the moved Super-Caravan at
the HV01 north camp beside the moved fountain). Thematic match: the Garden of Merchants IS a merchant hub
holding caravan_rhodes (another Super-Caravan) - a "Garden of Merchants" portal beside the HV01
Super-Caravan is coherent, and it is squarely "near the caravan scene." HV01 mesh has 5245 openNbr8 cells
>=15u from fountain/caravan/hostiles within 28u of the caravan; candidate host world (-77.3,-102.8,2317.1)
local (56.70,17.20,143.10) = 15u E of the caravan, >=15u from all hostiles/fountain. (Final host cell +
>=15u-from-everything check in DESIGN.)

### C4 SMOKE COVERAGE - **25 dropped atmosphere instances measured** (SV vs shipped)
### (ROUND-1 undercounted HV01 as 6 -> 21; ROUND-2 vet found 4 more HV01 totem lights -> 10/25)
SD(0x18) is byte-IDENTICAL SV-vs-shipped -> the "region-wide env params (SD)" are ALREADY SV's
verbatim; the atmosphere is entirely 0x05 emitter entities. All target levels are v0x11 with SPARSE
0x14 -> the SAFE append-only INJECT_SPECS path (atmosphere = flags=0, no 0x14 appended).
**Entrance region:**
- HiddenValley01 (10 dropped): `totem` x2 @ (65,12,106),(65,12,98); **`10mlight_dyn_purple` x2 @
  (65.47,16.43,106.04),(65.34,16.19,98.03) + `10mlight_dyn_red` x2 @ (65.44,16.42,106.01),
  (65.40,16.30,98.04)** [the totem UNDER-LIGHTS, ROUND-2 fix - round-1's extract TARGETS omitted the
  dyn_purple/dyn_red substrings]; `15mlight_simple_purple` @ (45.06,29.08,102.42); `campfire01` @
  (38.72,15.01,89.66); `5mlight_dyn_orange` @ (38.89,15.43,90.28); `10mlight_simple_red` @
  (46.95,25.03,112.49). (HVBorder04 = fully SHIPPED by build24, no action.)
- Other silkroad borders (01,02,03,05, approach): NO dropped atmosphere (HV01 is the only surface
  entrance level with any).
**Greece occultist region (Delphi) - the "same regional smoke" Will remembers:**
- DelphiLowlands04 (occultist tent, 5 dropped): `merchant_delphi_occulttent01` @ (12.88,9.98,2.52);
  `fog_occult_fx01` x2 @ (19.34,10,2.12),(8.53,10,15.02); `10mlight_statnl_blue` @ (15.21,16.31,5.17);
  `5mlight_dyn_green` @ (14.88,11.31,4.74).
- DelphiLowlands02 (pit/volcano, 8 dropped): `fog_occult_fx01` x3, `pit_fx01`, `pit_fx02`,
  `mc_hades_anouranfirepitmd01`, `mc_hades_anouranfirepit03`, `bugcloud_smallfx`.
- DelphiLowlands03 (2 dropped): `bugcloud_smallfx` x2.
- CAUTION: a NAIVE v0x11 Delphi inject crashed the game historically (commit a674c49 = wholesale 0x14
  regen). The current pipeline's append-only 0x14 path (0x14 appended ONLY for wants_0x14 specs;
  atmosphere sets none) is the SAFE path - HVBorder04 already carries 16 build24-injected atmosphere
  entities via this exact path with no crash. So Delphi atmosphere restore is safe as long as no
  wholesale 0x14 regen runs (it does not for these keys).


---

## DESIGN (locked) - all coords + minted UIDs

Planner: `tools/debug/plan_doors_hub.py` (UIDs collision-checked vs 157,548 known map UIDs).
Every portal mirrors the A1/Sparta shape: entrance = `portal_olympianarena1.dbr` (GridEntranceDynamic),
0x14 = mouth+exit+dest(48B); landing = `portal_olympianarena2.dbr` (GridExitOneWay), 0x14 = exit+zeros(48B).
All opened globally by the EXISTING bossarena.qst (Condition_OnLevelLoad -> Action_OpenDynGridEntrance by
record name `portal_olympianarena1.dbr`) - NO Quests.arc change, NO 0x06, NO new records (same
constraint/price as Sparta: portals render with the Olympian-arena mesh; document for Will).

### A1 GARDEN OF MERCHANTS door (canonical + hub builds)
| # | record | level | local coord | 0x14 mouth+exit+dest |
|---|--------|-------|-------------|-----------------------|
| G1 | portal_olympianarena1 (entrance) | HiddenValley01 (v0x11 shared) | (46.70,15.80,127.90) | gM1 + gX1 + GoM GUID |
| G2 | portal_olympianarena2 (landing) | GardenofMerchants (v0x0e SV-only) | (130.30,-39.00,79.10) | gX1 + zeros |
| G3 | portal_olympianarena1 (return entrance) | GardenofMerchants (v0x0e SV-only) | (142.30,-39.00,79.10) | gM2 + gX2 + HV01 GUID |
| G4 | portal_olympianarena2 (return landing) | HiddenValley01 (v0x11 shared) | (56.90,17.60,138.10) | gX2 + zeros |
- gM1=`a8605b3120dc06df34ac0734e531052e` gX1=`f9f0d0051580d19a9680a9c62c617f23`
  gM2=`8f83a7e17a10749081b657243a7eb98b` gX2=`4aecb0aa270c1563687f67c52281d6cc`
- GoM GUID=`15f9d3d7214d56d42a2ac6abd6114d78` HV01 GUID=`ce93e328b14a5eba7ab5be8e623fa215`
- G1 host is 16u E of the HV01 Super-Caravan, >=15u from fountain/caravan/hostiles, on-mesh openNbr8.
  G2/G3 land in the Garden's CARAVAN COMPONENT (comp #1, 112,172 cells) 6u/near the caravan_rhodes so
  the player arrives IN the merchant hub (comp #0 = a different nook). G1<->G4 sep 14.4u; G2<->G3 12u.

### A2 SECRET PLACE door (canonical + hub builds)
| # | record | level | local coord | 0x14 mouth+exit+dest |
|---|--------|-------|-------------|-----------------------|
| S1 | portal_olympianarena1 (entrance) | rhodes_secretvista_01 (v0x0f shared) | (138.50,18.40,33.10) | sM1 + sX1 + DFE GUID |
| S2 | portal_olympianarena2 (landing) | darkforestenter (v0x0e SV-only) | (23.90,2.00,30.50) | sX1 + zeros |
| S3 | portal_olympianarena1 (return entrance) | darkforestenter (v0x0e SV-only) | (17.90,7.00,38.50) | sM2 + sX2 + SV01 GUID |
| S4 | portal_olympianarena2 (return landing) | rhodes_secretvista_01 (v0x0f shared) | (137.10,17.00,43.10) | sX2 + zeros |
- sM1=`bab0519fdc5f79a364f3b3eb492927ac` sX1=`f6474fb1f4ba46d01a4deefaebba1480`
  sM2=`46d2a8ba61db650f148f3944f56f4923` sX2=`c513d76bc21a59cacdc21296f99e0862`
- DFE GUID=`1397c8e754491051bcd1be9cc4dd092f` SV01 (rhodes_secretvista_01) GUID = to be read at build.
- S2 = central darkforestenter landing (the Secret Place forest-cluster entry); S3 return-entrance 8u away.

### TEST HUB (SVC_TEST_HUB=1, TESTHUB artifact ONLY)
Random09A blood-cave interior cluster (10 cells >=10u apart, entry/east region, all on-mesh openNbr8,
away from combat - the cave has NO combat proxies inside): entrance cells S0..S4 for the 5 outbound
portals, return-landing cells S5..S9 for the 5 returns. Each of the 5 destinations gets an entrance
(in the cave), a landing (in the dest), a return-entrance (in the dest), and a return-landing (in the cave).
Cave cells (local, HV01... no - Random09A corner (5979,18,3243)):
  S0(21.10,1.00,12.10) S1(21.10,1.00,22.10) S2(21.10,1.00,32.10) S3(21.10,1.00,42.10) S4(24.30,1.00,57.90)
  S5(29.10,1.00,48.10) S6(29.90,1.00,16.90) S7(29.90,1.00,26.90) S8(29.90,1.00,36.90) S9(34.30,1.00,57.50)
Destinations (landing local / return-entrance local / GUID):
| dest | landing | ret-entrance | GUID |
|------|---------|--------------|------|
| maze03 (v0x0f shared) | (290.70,1.20,148.50) | (292.50,1.20,156.30) | cdef89ae834a4adf1214609306708c02 |
| murderbossroom (v0x0e SV-only) | (52.90,3.00,28.10) | (52.90,3.00,39.90) | 2817751af24828502c9d7ea5f0a5c6ab |
| spartacryptlevel2 (v0x0e SV-only) | (42.90,-1.60,34.70) | (48.90,-1.60,40.70) | 797c78594040cba419340c990e6903c4 |
| darkforestenter (v0x0e SV-only) | (23.90,2.00,30.50) | (17.50,6.80,35.30) | 1397c8e754491051bcd1be9cc4dd092f |
| gardenofmerchants (v0x0e SV-only) | (130.30,-39.00,79.10) | (136.30,-39.00,73.10) | 15f9d3d7214d56d42a2ac6abd6114d78 |
Hub UIDs (per dest: in_mouth,in_exit,ret_mouth,ret_exit) - see plan_doors_hub.py output, all minted.
NOTE the hub maze03/darkforest/garden landings coincide with A1/A2/hub-shared dests; each hub pair uses
its OWN minted UIDs so there is NO cross-talk with A1/A2 or the 3 existing Sparta/A1 pairs.
CAUTION: SC2 already hosts the Sparta P2/P3 portals; the hub SC2 landing (42.90,-1.60,34.70) must be
>=10u from those (P2 @ 48.90,34.70 / P3 @ 50.30,26.70) - verify at gate. darkforestenter/garden host both
the A2/A1 landing AND the hub landing - distinct UIDs, verify spacing.

### C1 fix (respawn) - GROUPS surgery
Rewrite the 12 position bytes at GROUPS(0x11) section-rel 31620 from (49.263,15.634,14.950) to
(35.70,17.60,143.10). This is the ONLY stale copy. New tooling: a GROUPS-position patch keyed by the
fountain UID (find the member by UID, rewrite the pos triplet at UID+32). GATE: fountain GROUPS pos ==
its 0x05 pos (native-shrine parity); 0 old-coord triplets remain in the map.

### C2 fix (sprite pyre) - add mc_hades_anouranfirepit02 at the sprite spawner
INJECT_SPECS HVBorder04: add (MC_HADES_ANOURANFIREPIT02_DBR, 50.70, 1.80, 34.30) - the volcano/firepit
bowl at the sprite-spawner spot (existing pit_fx01 there = the purple occult flame). Sprites UNCHANGED.

### C3 fix (caravan) - wagon to driver's screen-right (+X/East) - FINAL COORDS
Recompose in the current west bench (clear of the occult camp props at X~27,Z~25): **driver
(22.70,1.62,19.90), wagon (26.70,1.62,19.90), horse (26.70,1.62,15.90)**. wagon 4u EAST (screen-right) of
driver; wagon d_merchant=10.0u (clickable); driver d_merchant=13.7u; min d_prop=4.9u; horse 4u S of wagon
(hitched front); all on-mesh <0.3u. Wagon moves via INJECT_SPECS coord change (it is an injected record);
driver+horse move via MOVE_SPECS (native records). All keep their existing rotations.
A2 rhodes_secretvista_01 GUID = `88b842ba1a4329176dc2a995c33eda29`.

### C4 fix (smoke) - restore 21 dropped atmosphere instances (SV-exact coords, safe INJECT_SPECS)
HiddenValley01 (+6): totem x2, 15mlight_simple_purple, campfire01, 5mlight_dyn_orange, 10mlight_simple_red.
DelphiLowlands04 (+5): merchant_delphi_occulttent01, fog_occult_fx01 x2, 10mlight_statnl_blue, 5mlight_dyn_green.
DelphiLowlands02 (+8): fog_occult_fx01 x3, pit_fx01, pit_fx02, mc_hades_anouranfirepitmd01,
  mc_hades_anouranfirepit03, bugcloud_smallfx.
DelphiLowlands03 (+2): bugcloud_smallfx x2.
All flags=0, no 0x14 (SV places none) -> the append-only path appends ZERO 0x14 (no crash risk).

---

## IMPLEMENTATION COMPLETE - GATE RESULTS (verbatim)

Artifacts:
- CANONICAL (flag OFF): `local/Levels_merged.arc` = 688,689,535 B (build25 was 688,685,020; +4,515 B for
  A1/A2 doors + C4 atmosphere + C1/C3). md5 `5bd233334a405151d3a80c78a4dcb2cf`.
- TEST HUB (flag ON): `local/Levels_merged_TESTHUB.arc` = 688,690,799 B (+1,264 B = the 20 hub portals).
  Built with `SVC_TEST_HUB=1`. LOCAL-ONLY (never Workshop).
- Baseline snapshot: `local/Levels_merged.build25-baseline.arc`.

Tooling changes (map tooling only):
- `tools/build_section_surgery.py`: A1/A2/hub portal DBR+UID+0x14 constants; C2/C4 atmosphere DBRs +
  SV-exact rotations; INJECT_SPECS entries (A1 HV01 G1/G4 + Garden G2/G3; A2 rhodes_secretvista_01
  S1/S4 + darkforestenter S2/S3; C4 HV01 + 3 Delphi levels; C2 firepit at HVBorder04 sprite spawner;
  C3 wagon coord); MOVE_SPECS (C3 horse+driver recompose); `build_hub_inject_specs()` +
  `merge_hub_into_inject_specs()` (the 20 hub portals, gated); `patch_respawn_group_position()` (C1).
- `tools/svaera_plus_portals.py`: SVC_TEST_HUB flag -> effective inject_specs + TESTHUB output name;
  C1 GROUPS fix after merged_groups; hub injection into the swapped Random09A blob; INJECT_SPECS ->
  inject_specs in the loops.
- NEW read-only recon/gate scripts under `tools/debug/`: recon_doors_hub.py, recon_c1_bytescan.py,
  extract_c4_atmosphere.py, plan_doors_hub.py, gate_doors_hub.py.
- Did NOT touch: DB scripts, donors, Quests.arc, fix_mc_output.py, hybrid_merge.py.

### GATES (all PASS)
- **COLLATERAL (canonical vs build25): PASS.** SD + QUESTS IDENTICAL; GROUPS changed (C1 fix, intended);
  EXACTLY 8 blobs changed, ALL intended (HV01, HVBorder04, GardenofMerchants, rhodes_secretvista_01,
  darkforestenter, DelphiLowlands02/03/04); 0 unexpected; **0 navmeshes (0x0b) changed**. maze03 + SC2 +
  crypt_floor1 + catacube02_floorlast BYTE-IDENTICAL to build25 (the 3 existing pairs untouched).
- **HUB IDENTITY: PASS.** GROUPS/SD/QUESTS/BITMAPS IDENTICAL canon vs hub; EXACTLY 6 blobs differ (the 6
  hub levels: Random09A +10 inst, maze03/murderbossroom/SC2/darkforestenter/gardenofmerchants +2 each);
  for each, the canonical instances are a BYTE-EXACT PREFIX of the hub instances (+ the appended hub
  portals). => flag-OFF is byte-identical to flag-ON minus the hub entities (proven).
- **PLACEMENT: PASS.** All 8 A1/A2 door portals at intended local coords, flags=0, identity rotation,
  0x14 bindings match exactly (mouth/exit/dest), on-mesh 0.00u. All 20 hub portals present with correct
  0x14. Hub landings + cave cells all on-mesh 0.00u.
- **C1 (respawn): PASS.** Fountain GROUPS respawn member pos (35.7,17.6,143.1) == its 0x05 instance pos
  (35.7,17.6,143.1) = native-shrine parity; **0 old-coord (49.26,15.63,14.95) triplets remain in the
  ENTIRE map**. Root cause byte-proven + fixed at the source (GROUPS member position, not the 0x05).
- **C3 (caravan): PASS.** wagon (26.70,19.90) is 4.0u EAST (screen-right, +X, N-up camera) of driver
  (22.70,19.90); wagon d_merchant=10.1u (clickable); horse 4u S (hitched front); on-mesh.
- **C4 (smoke): PASS.** All 25 dropped atmosphere record types present at SV-exact coords in the shipped
  blobs (10 HV01 [incl. the ROUND-2 2 purple + 2 red totem under-lights] + 5 DelphiLowlands04 + 8
  DelphiLowlands02 + 2 DelphiLowlands03), flags=0, SV rotations.
- **CROSSTALK: PASS.** 18 entrance mouths all DISTINCT; 17 landings each pair EXACTLY one entrance exit
  (2 pre-existing boss_arena landings excluded - unchanged from build25, own base chain); no cross-talk
  between any pairs incl. the 3 existing Sparta/A1 pairs.
- **Reachability: PASS.** A1 Garden G2/G3 + hub land/ret ALL in the caravan-hub comp #1 (112,172 cells,
  with caravan_rhodes). darkforest/SC2/murderbossroom/maze03 landings + returns in the LARGEST comp.
  A1 host G1/G4 (HV01) + A2 host S1/S4 (rhodes_secretvista_01) in their levels' LARGEST comp.
- **verify_merged_bc_navmeshes: 24/24 PASS** (canonical). **entrance_landing G2: PASS** (508 cells,
  dY +0.00u, donor + merged). **Full re-parse: 0 malformed / 0 bad magic across 2282 levels, BOTH
  artifacts.** All hub-level navmeshes (0x0b) BYTE-IDENTICAL canon vs hub (hub touched only 0x05/0x14).
- **3 existing pairs intact:** maze03/catacube02_floorlast/crypt_floor1/spartacryptlevel2 blobs
  byte-identical to build25 in the canonical build; A1 maze03 mouth + Sparta M1 UIDs resolve.

### THE PRICE (documented, same as Sparta) + WALK-TEST-PENDING
- All new portals render with the Olympian-arena portal mesh (same visual as the Uber Dungeon entrance)
  - the price of the no-Quests.arc constraint (bossarena.qst opens ONLY portal_olympianarena1 by name).
- No offline gate can confirm the GridEntranceDynamic teleport actually FIRES in-game (the quest-open +
  Grid-pair chain is the same unrehearsed mechanism A1/Sparta flagged; those are still walk-test-pending).

---

## WHAT WILL MUST WALK-TEST (per item; full TQ restart, Custom Quest char)

### A1 - GARDEN OF MERCHANTS door (canonical build; Orient, blood-cave entrance region)
- At the **HiddenValley01 NORTH camp** (the Silk Road cave-mouth area, by the moved respawn fountain +
  Super-Caravan), an **Olympian-arena portal** stands ~15u EAST of the Super-Caravan (world
  (-87.3,-104.2,2301.9)). WALK INTO IT.
- EXPECTED: teleports to the **Garden of Merchants**, landing right in the **merchant hub beside the
  caravan_rhodes Super-Caravan** (the previously-unreachable Super-Caravan region is now reachable). A
  **return portal** stands ~12u away in the Garden - walk into it to return to HV01 (landing ~14u from
  where you left). OFFLINE-VERIFIED: both portals on-mesh, in the caravan-hub walkable component,
  0x14 bindings resolve to the correct GUIDs with byte-exact mouth/exit pairing.

### A2 - SECRET PLACE door (canonical build; Rhodes, IT Act 4)
- At the **Rhodes Secret Vista** (the scenic overlook, `rhodes_secretvista_01`), look at the
  **tucked-away EAST-edge nook** (world (-77.5,18.4,-6036.9), local (138.5,33.1)) for an Olympian-arena
  portal. WALK INTO IT.
- EXPECTED: teleports to **darkforestenter** = the entry of the 11-level Secret Place forest cluster
  (forest chain + rogue camp + murder-boss room, all walkable + internally connected). A return portal
  stands ~8u away - walk into it to return to the Secret Vista. OFFLINE-VERIFIED: both portals on-mesh in
  the largest walkable comp, bindings resolve.

### B - TEST HUB (LOCAL-ONLY build `local/Levels_merged_TESTHUB.arc`; deploy this variant to CustomMaps
###     ONLY for testing - NEVER to Workshop; the canonical build has NO hub)
- Enter the **blood cave** (HiddenValley01 cave mouth -> west tunnel into Random09A). Near the cave
  entry/mouth (east side, before the deeper tunnels), **10 Olympian-arena portals** stand in two rows
  (5 outbound + 5 returns), >=10u apart, on-mesh, clear of any combat. Each outbound portal teleports to:
  (1) **maze03** (beside the existing Uber Dungeon portal in the Minotaur boss room),
  (2) **murderbossroom** (the Rhodes Murder Bunny / secret-passage room),
  (3) **SpartaCryptLevel2** (beside the invented Sparta crypt arena landing),
  (4) **darkforestenter** (the Secret Place forest entry),
  (5) **Garden of Merchants** (the merchant hub by the caravan).
  Each destination has a **return portal** back to the cave. So the hub lets you fast-hop to every
  invented/SV area for testing. OFFLINE-VERIFIED: all 20 portals on-mesh, in the largest/hub walkable
  comps, distinct UIDs (no cross-talk), byte-identity to the canonical build proven.

### C1 - RESPAWN POSITION (canonical build; the build24/25 repeat bug - NOW ROOT-CAUSED + FIXED)
- Die/respawn anywhere bound to the HV01 Rebirth Fountain. EXPECTED: you now respawn at the **NEW north
  camp spot** (world (-98.3,-102.4,2317.1), by the Super-Caravan, ~100u from the beastman swarm), NOT the
  old pre-move spot. ROOT CAUSE (byte-proven): the respawn point lives in the world GROUPS section's
  shrine-member POSITION (not the 0x05 instance); build24 moved the 0x05 but left GROUPS stale. FIXED at
  the source. This is the load-bearing test - if you STILL spawn at the old spot, the GROUPS fix did not
  take (but the gate proves GROUPS pos == 0x05 pos + 0 old-coord triplets remain).

### C2 - SPRITE PYRE VISUAL (canonical build; HVBorder04 occultist scene)
- At the **exploding pit-sprites** north of the occultist merchant, there is now a **Hades firepit/volcano
  bowl** (mc_hades_anouranfirepit02) at the spawner spot, with the existing purple occult pit-flame FX =
  a purple occult pyre/volcano visual anchor. Sprites unchanged.

### C3 - CARAVAN LAYOUT (canonical build; HVBorder04)
- At the occultist merchant's caravan (west of the merchant), the **wagon now sits on the RIGHT-HAND side
  of the driver NPC** (screen-right, +X/East; N-up camera), horse hitched in front (south), merchant
  freely clickable. EYEBALL: confirm the wagon reads as camera-right of the driver (the one C3 walk-test
  item - TQ's camera is isometric-diagonal; the fix used +X=screen-right).

### C4 - SMOKE / ATMOSPHERE (canonical build; BOTH regions)
- **Entrance region (HiddenValley01 surface):** more occult atmosphere now - cult **totems** (each now
  under-lit by its SV **purple + red dynamic glow**) + a **campfire** + purple/red/orange coloured lights
  (10 SV emitters restored, on top of the Border04 occult scene).
- **Greece occultist region (Delphi):** the SAME regional smoke Will remembers is restored - the
  **occultist tent + occult fog + coloured lights** at DelphiLowlands04, and the **pit/volcano scene**
  (occult fog + lava firepits + pit FX + bug-cloud haze) at DelphiLowlands02/03. 21 SV emitters total,
  at SV-exact coords. Region-wide env params (SD) were already SV's verbatim (byte-identical), so no SD
  change was needed.

## SKIP/NOTE
- Nothing skipped: A1, A2, the full hub, and all of C1-C4 are IMPLEMENTED + gated. The only
  walk-test-pending uncertainty (shared with A1/Sparta) is whether the GridEntranceDynamic teleport
  fires in-game; every offline gate passes.

## DEPLOY GUIDANCE (main session owns deploy/commit) - ROUND-2 REBUILT ARTIFACTS
- CANONICAL `local/Levels_merged.arc` (**688,691,406 B, md5 `3f1b2e4d43a856f4df067f8f023da365`**) = the
  shippable build (A1/A2 doors + C1-C4 fixes incl. the round-2 HV01 totem under-lights, hub-free). Deploy
  to CustomMaps (`-SyncLevels`); Quests.arc UNCHANGED (no rebuild needed - bossarena.qst already opens
  portal_olympianarena1 by name). This is Workshop-safe.
- TEST HUB `local/Levels_merged_TESTHUB.arc` (**688,688,672 B, md5 `67090a9bdebe1ed5dd58ab912bacae2a`**) =
  LOCAL-ONLY testing variant. Deploy to CustomMaps only when Will wants to fast-hop the areas; NEVER
  upload to Workshop.
- NOT deployed/committed by this session. Baseline for rollback: `local/Levels_merged.build25-baseline.arc`.

---

## ROUND 2 - VET FIX (C4 HV01 totem under-lights) - IMPLEMENTED + RE-GATED

**Vet finding (minor, non-breaking):** C4's HV01 restoration was INCOMPLETE. SV's HiddenValley01 placed
4 dynamic mood-lights (2x `10mlight_dyn_purple` + 2x `10mlight_dyn_red`) as the occult UNDER-LIGHTING
for its 2 totems (~0.3-0.5u XZ / ~4u ABOVE each totem). Round-1 restored the 2 totems but NOT the 4
co-located dyn lights, because `tools/debug/extract_c4_atmosphere.py`'s HV01 TARGETS list omitted the
`10mlight_dyn_purple`/`10mlight_dyn_red` substrings (undercounted SV's HV01 atmosphere as 6, actually 10).
The 1 purple + 1 red already in CANON's HV01 were the SEPARATE B1 new-fountain emitters at local
~(33.5/38.0,145), ~50u from the totems. Pure-visual only (EffectEntity light, no aggro/0x14/mesh).

**Independent verification (`tools/debug/verify_c4_hv01_totemlights.py`, read-only):** confirmed against
pristine SV 0.98i - HV01 has EXACTLY 2 purple + 2 red, flags=0, IDENTITY rot, at:
- purple `(65.4732666015625, 16.431617736816406, 106.04359436035156)`, `(65.3399887084961, 16.19445037841797, 98.02886962890625)`
- red `(65.44312286376953, 16.418643951416016, 106.00531005859375)`, `(65.39828491210938, 16.303573608398438, 98.03968811035156)`
and CANON was MISSING all 4 (only the 2 B1 fountain lights present, ~50u away). Matches the vet exactly.

**Fix (map tooling only, same safe append path):** added the 4 records to HV01's INJECT_SPECS C4 block
(`tools/build_section_surgery.py`, right after the 2 totems) at SV's exact float32 coords, flags=0,
identity rot (no rot override - SV places them identity), no 0x14. Also corrected the recon
`extract_c4_atmosphere.py` TARGETS (added the 2 dyn-light substrings) and hardened `gate_doors_hub.py`
`gate_c4` (now checks the 2+2 totem under-lights at SV coords; HV01 C4 count 6 -> 10, total 21 -> 25).
Rebuilt BOTH artifacts (canonical + TESTHUB).

**RE-GATED (all PASS, both artifacts):**
- **Round1->Round2 blob diff (order-independent multiset):** EXACTLY 1 blob changed (HV01), EXACTLY +4
  records added (the 4 dyn lights at SV coords), 0 removed, 0 mutated - in BOTH artifacts. GROUPS/SD/
  QUESTS byte-identical round1->round2.
- **Collateral (canonical vs build25):** PASS - still 8 intended blobs, 0 unexpected, 0 navmeshes changed
  (HV01 696,275 -> 697,623 = +4 v0x11 light records). SD+QUESTS identical; GROUPS = C1 fix only.
- **Hub identity:** PASS - canonical is a byte-exact prefix of TESTHUB minus the hub instances (HV01 is
  not a hub level -> the 4 lights are byte-identical in both builds; 222 HV01 instances in each).
- **Byte-shape parity (`byteshape_check`):** the 4 new totem lights (idx 212-215) share the EXACT record
  shape of the B1 fountain purple/red exemplars (idx 207-208): flags=0, identity rot, NO 0x14.
- **C4:** PASS - HV01 now 2x purple + 2x red totem under-lights at SV coords (25 total: 10 HV01 + 15 Delphi).
- **Placement / C1 / C3 / crosstalk:** PASS (unchanged by this fix).
- **verify_merged_bc_navmeshes: 24/24 PASS** (both artifacts). **entrance_landing G2: PASS** (508 cells,
  dY +0.00u). **Full re-parse: 2282/2282 levels, 0 malformed** (both artifacts).

**New/edited files (round 2):** `tools/build_section_surgery.py` (4 INJECT_SPECS lines),
`tools/debug/extract_c4_atmosphere.py` (recon TARGETS), `tools/debug/gate_doors_hub.py` (gate_c4),
`tools/debug/verify_c4_hv01_totemlights.py` (NEW independent verification). Deploy targets unchanged
(canonical is Workshop-safe; TESTHUB is local-only).

---

## ROUND 3 - PORTAL OPENNESS FIX (born-open GridEntrance class swap) - IMPLEMENTED + GATED

**Problem (Will, TESTHUB, blood-cave first room):** NO hub portals visible; and per the round-1
DynGridEntrance RCA the portals were ALSO born CLOSED (inert) - both gated on bossarena.qst being
adopted per-character. Goal (wf_c0012e88-64a + brief): make the portals OPEN + VISIBLE from raw
data with NO quest dependency, for FRESH and PRE-EXISTING characters.

**Root cause + fix (disasm-proven, full evidence in docs/DYNGRID_GATE_RCA.md sec 5):** the ENTRANCE
record `portal_olympianarena1` was Class `GridEntranceDynamic`, whose activate method calls
`SetPortalIsOpen(0)` UNCONDITIONALLY at every spawn (Game.dll 0x101ae2f1) and hides its mesh unless
a quest fires. `SetPortalIsOpen` has EXACTLY 3 callers in Game.dll (all GridEntranceDynamic: Open/
Close/activate) and 0 in Engine.dll, so a static `GridEntrance` (the born-open cave-mouth class,
153 base-game precedents) NEVER self-closes and is always visible. The teleport reads ONLY the 0x14
binding (GetConnectedPortalId=[+0x2d8], GetConnectedRegionId=[+0x2e8]) - no 0x06, same pure-0x14
path A1/Sparta already use. **FIX = swap the entrance record to Class GridEntrance + reformat every
entrance's 0x14 from 48 -> 60 bytes (prepend the 12-byte (2,0,1) GridEntrance prefix).** Landing
`portal_olympianarena2` (GridExitOneWay) is already born-open - untouched (48-byte 0x14 kept).

**TWO coupled halves (must deploy together):**
- DB: `apply_svc_patches.py` `_make_portals_born_open_gridentrance` (Class/templateName/record_type
  -> GridEntrance, drop Dynamic-only fields, keep mesh) + fail-loud `_verify_portals_born_open`.
- MAP: `build_section_surgery.py` `GRIDENTRANCE_0x14_PREFIX` prepended to every entrance x14_payload
  in `_normalize_spec` (flows through both inject paths -> all entrances in BOTH artifacts 60-byte).

**Rebuilt (NOT deployed/committed - main session owns that + the coupled arz build):**
- `local/Levels_merged.arc` = 688,691,849 B, md5 `a1ba5db2f00ffa067a808753a2e1eac5` (7 entrances).
- `local/Levels_merged_TESTHUB.arc` = 688,687,885 B, md5 `96a9eb14c88e308e9f850515526c23e4` (17 entr).
- baselines: `local/Levels_merged*.build26-baseline.arc`. DB test build: scratchpad SVC_r2_test.arz.
- DB not restaged (the wf_30460e48-ca1 Toxeus-spawn loop also edits apply_svc_patches; the final
  arz build picks up BOTH fixes - main session runs `build_svc_database.py` once for the deploy).

**GATES (all PASS, both artifacts):** DB build 4 invariants + `_verify_portals_born_open` (exit 0);
`gate_portal_visibility.py` (arz born-open swap) PASS; `gate_portal_openness.py` PASS (canon 7/7 +
9 landings; TESTHUB 17/17 + 19 landings; pairing intact); `compare_gridentrance_0x14.py` = our
entrance 0x14 is BYTE-IDENTICAL in framing to the working native Silk Road cave mouth (60B, (2,0,1)
prefix); `gate_openness_collateral.py` + `gate_doors_hub.py` collateral = ONLY portal blobs changed
(+12B/entrance in 0x14 only), 0 navmeshes changed, QUESTS/GROUPS/SD identical; verify_merged_bc_
navmeshes 24/24; entrance_landing_check --check-merged PASS; gate_doors_hub placement/crosstalk/
hubidentity/c1/c3/c4 PASS; gate_sparta_placement A-workstream PASS with 60-byte entrances.

**DEPLOY (main session):** ship the freshly-built arz (via build_svc_database.py) + the two new
maps TOGETHER (60-byte 0x14 is byte-locked to the GridEntrance class; a mismatch misaligns the
read). Quests.arc needs NO change (bossarena.qst's OpenDynGridEntrance/ShowNpc become harmless
RTTI-filtered no-ops). Canonical map -> Workshop; TESTHUB -> Will's local CustomMaps only.
