# ENTRANCES POLISH LOG - Workstreams A (entrances) + B (blood-cave polish)

> Running checkpoint log for the max-effort implementer wave that (A) restores the
> maze03 / Garden / Secret-Place entrances the SV-areas campaign SKIPPED as
> "ungateable offline", and (B) polishes the blood-cave entrance region per Will's
> asks (smoke atmosphere, exploding sprites, move the respawn fountain+caravan away
> from spawn-camping swarms). Written continuously so nothing is lost.
>
> Baseline: build23 (commit `04f2cd1`). `local/Levels_merged.arc` = 688,687,165 B.
> ALL 15 SV-area interior navmeshes are real + gated; only ENTRANCES are missing.
> Python: `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`
> (`PYTHONIOENCODING=utf-8`).
>
> Accepted pattern (from the brief, overriding the campaign's SKIP): implement each
> item with EVERY offline gate achievable, ship flagged WALK-TEST-PENDING, Will walks
> it. Maximize offline confidence; do not demand impossible proofs. Skip-not-break per
> item, with evidence.
>
> Companion docs: `SV_AREAS_CAMPAIGN_LOG.md` (the SKIP analyses + measured facts),
> `SV_AREAS_CAMPAIGN_PLAN.md`, `AREA_WIRING_RECIPE.md`, `DROPPED_CONTENT_AUDIT.md`
> (exact SV-local coords for every dropped entity - the exemplar source for B).

---

## Gates (per item, verbatim from the brief)

For EVERY shipped item:
- entity present in rebuilt map at intended coords
- byte-shape mirroring its exemplar (native or SV)
- landing/placement on-mesh (navlib vs current donors / AE baked mesh)
- 0x14 bindings resolve to merged-world GUIDs
- distances proven for B2/B3 (list every spawn proxy + distance)
- no collateral (only intended blobs+sections change vs build23)
- full map re-parse 0 malformed
- blood-cave + all 15 new-area navmeshes byte-identical
- entrance_landing + verify_merged still PASS
- state exactly what Will must walk-test

CONSTRAINTS: map tooling only (build_section_surgery INJECT_SPECS + helpers,
svaera_plus_portals). No DB scripts, no navmesh generation/donors, no Quests.arc
content change. No deploy, no commit, no Workshop.

---

## RECON PHASE - measured facts (build23 merged map + SV upstream)

Recon scripts (read-only): `tools/debug/recon_hv01_region.py`, `recon_hv01_mesh.py`,
`recon_greece_occultist.py`, `recon_border04_mesh.py`, `find_delphi.py`.

### Region topology (the "cave-mouth region")
Two DISTINCT shared levels, both v0x11 in the merge, both with REAL navmeshes:
- **HiddenValley01** (`levels/world/orient/silkroad/hiddenvalley01.lvl`): corner
  (-134,-120,2174). Mesh largest comp = 111,758 cells, world X[-122,9] Z[2183,2318].
  Holds the **respawn fountain** (`respawntempleorient01`, flags=1, UID `feeb4bc6...`)
  @ world (-84.7,-104.4,2188.9) = local (49.26,15.63,14.95), and the **caravan**
  (`caravan_silkroad`) @ world (-78.7,-104.4,2188.9) = local (55.30,15.60,14.90), 6u E.
- **HiddenValleyBorder04** (`.../hiddenvalleyborder04.lvl`): corner (-134,-104,2302).
  Mesh largest comp = 26,379 cells, world X[-112,-74] Z[2287,2340]. Holds the
  **"occultist" merchant scene**: `Merchant_HiddenValley_General` @ (-98.3,-102.4,2326.3)
  [0.00u on-mesh] + `merchant_hades_merchantwagon01` @ (-97.8,-102.4,2328.5) + Horse02 +
  `silkroad_villager1`.

**Key geometry:** HV01 (Z up to 2318) abuts Border04 (Z from 2287) - they overlap
Z[2287,2318]. The occultist is at Border04 Z~2326, just NORTH of HV01's north edge. So
"the occultist's side of the area" = the NORTH (+Z) end of HV01, adjacent to the Border04
merchant scene. The player walks NORTH out of HV01 into Border04 to reach the occultist.

**RECONCILIATION with the brief's "occultist is in the HV01 cave-mouth region":** confirmed
in spirit. The occultist = the Hades-merchant scene in Border04 (the level directly north
of HV01's cave mouth), which SV originally DRESSED with occult atmosphere
(`occultistaura_fx01` sits at Border04-local (41.01,1.51,21.99), 0.06u from
Merchant_HiddenValley_General @ (41.02,1.60,22.05) - literally the occultist aura ON the
merchant). The merge dropped all that occult dressing, so in-game the merchant currently
shows without the occult aura. B1 restores it.

### B3 - the spawn-camping swarm (the fountain problem), CONFIRMED
4 hostile spawn proxies in HV01 (Silk Road neanderthal beastman pack + an encounter proxy):
| proxy | world | d_fountain | d_caravan |
|-------|-------|-----------:|----------:|
| `proxies orient\area002 - silkroad\ag_beastman_neanderthal_02t` | (-82.9,-104.3,2197.8) | **9.1u** | **9.9u** |
| `proxies orient\area002 - silkroad\ag_beastman_neanderthal_02n` | (-59.1,-106.4,2199.7) | 27.8u | 22.3u |
| `proxies orient\area002 - silkroad\ag_beastman_neanderthal_03t` | (-112.3,-103.1,2199.6) | 29.5u | 35.2u |
| `creature\encounters\proxies\encact3` | (-101.2,-103.8,2216.6) | 32.2u | 35.7u |

The nearest is 9.1u from the fountain / 9.9u from the caravan = the spawn-camp Will reports.
HV01 mesh has a large SAFE zone at the NORTH end (Z~2314-2317): 748 on-mesh cells with
>=25u clearance from every hostile, best spots ~100u clearance, +128u dZ toward the
occultist. That is exactly "move the fountain to the occultist side, away from the swarms."

### B1 - the occult atmosphere donor (SV upstream, byte-exact exemplars)
SV HiddenValleyBorder04 (v0x0e) placed the occult scene the merge dropped (all SV-LOCAL,
Border04 corner (-134,-104,2302), NOT grid-shifted so local==merged-local):
`pit_fx01`@(26.98,0.38,24.94); `fog_occult_fx01`@(26.64,1.48,24.83)+(36.90,1.62,23.88);
`occultistaura_fx01`@(41.01,1.51,21.99); `10mlight_dyn_purple`@(47.03,6.51,29.58)+(41.09,6.51,12.38);
`10mlight_dyn_red`@(47.31,6.62,29.64)+(41.14,6.56,12.40); `5mlight_stat_blue`@(32.35,6.06,24.50)+(35.65,7.14,24.22);
`mc_hades_woodpyre01`@(27.65,0.94,25.31); `mc_hades_anouranfirepit02`@(27.35,1.59,25.04);
`totem`@(40.24,1.62,12.34)+(46.46,1.62,29.55);
`fx_disciple_aura_eyechantment01`@(38.68,4.96,29.89)+`_02`@(38.92,4.92,29.63).
SV HiddenValley01 (v0x0e) surface atmosphere (totems + coloured lights) also dropped -
coords in DROPPED_CONTENT_AUDIT WAVE A + recon output.
ALL these records RESOLVE in the built arz (Class: pit/fog/aura/disciple=EffectEntity,
totem/woodpyre=Decoration, firepit=Tile, lights=base-game). Re-injectable, no aggro.

### B2 - the WORKING Greece pit-sprite exemplar (byte-exact)
SV DelphiLowlands02 (`levels/world/greece/delphi/delphilowlands02.lvl`, v0x0e) is the
working "exploding sprites next to a volcano" scene. Sprite records (Class **Monster**):
`pitsprites\t1_lildude_01` x4, `t1_lildude_02` x2, `t1_pitspawner_01` x2 (the spawner,
Trap10, invisible), `t1_pitspawner_02` x1. Rotations are IDENTITY (except pitspawner_02 =
~0.09deg, negligible). Sprites cluster ~2-3u apart around each `pit_fx`.
**Merchant->sprite standoff in the WORKING Greece scene: nearest 10.8-11.6u** (measured:
merchantvendortable01 nearest sprite 11.3u; Merchant_Delphi_Quest 10.8u;
merchant_delphi_occulttent01 11.6u). This is the proven aggro-safe distance -> B2 must use
AT LEAST 11u standoff from the occultist merchant; brief says prefer more -> target >=15-20u.
All sprite records RESOLVE in the built arz (t1_lildude = Monster/lildude.msh;
t1_pitspawner = Monster/tagTrap10/invisible mesh).

### Baseline snapshots on disk
build23 = `local/Levels_merged.arc` (688,687,165 B). Rollback snapshots:
`local/Levels_merged_build22.arc` (685,652,028), `_wave1.arc` (686,012,299),
`.build21-baseline.arc`. Deployed `work/.../Levels.arc` == build23 (688,687,165, same file).

---

## A1 - maze03 -> Uber Dungeon + Boss Arena (measured facts)

Recon: `tools/debug/recon_maze03.py`.

- **SV Knossos Maze03** (`levels/world/greece/knossos/underground/maze03.lvl`, v0x0e,
  corner (-6740,0,-4201), GUID `cdef89ae...`): `portal_olympianarena1` at 0x05 idx 11,
  local (101.8381,1.0,144.5195) = world (-6638.2,1.0,-4056.5), flags=0, 56-byte record.
  Its **0x14 binding** (idx 11, 48 bytes):
  - mouth_uid = `58941143e04eb3c0d62dbd952143f05d`
  - exit_uid  = `6e513e901549b1d558db968c61bda66a`
  - **dest_guid = `dbc245c358434e0bb54760b234293cc5`**
- **AE Maze03 (merged, kept SVAERA)**: v0x0f, corner (-8076,0,-3943), SAME GUID
  `cdef89ae...`, 0x14 size 0, **real Editor-baked navmesh** (2,053,366-cell largest comp,
  world X[-7870,-7526] Z[-3833,-3380]), 447 instances.
- **corner delta AE-SV = (-1336,0,258)** (matches campaign).
- **crypt_floor1** (merged, v0x0e): GUID = **`dbc245c358434e0bb54760b234293cc5`** ==
  the SV 0x14 dest_guid EXACTLY. So the SV binding points to crypt_floor1 and crypt keeps
  its GUID in the merge -> **the 0x14 binding is directly reusable, NO GUID remap needed.**
  Landing `portal_olympianarena2` @ idx 192, world (-2438.1,10.0,-2450.1), on-mesh (Wave1).
- **boss_arena** (merged, v0x0e): GUID `6112638db5442534f7fb909aee415f7a`. Has
  `portal_olympianarena` @ idx 28 + 29, 2x 0x14 (48 B each). Its own DynGridEntrance chain.

**v0x0f 0x05 RECORD LAYOUT VERIFIED (the brief's flagged unknown):** base = **72 bytes**
(+16 if flags), IDENTICAL to v0x11 - NOT 56. Proof: walking all 447 AE-maze instances with
base=72 lands EXACTLY at data end (41222==41222, all string idx in range); base=56 desyncs
at instance 5. So the existing v11 inject path (`inject_into_0x05_v11`, base 72) is correct
for v0x0f. (Confirms the varwalk in `diag_bugs.walk_instances`: `base = 56 if v0e else 72`
already handles v0f correctly since v0f != 0x0e -> 72.)

**The placement problem:** SV-local direct in AE = world (-7974.2,1.0,-3798.5), which is
X=-7974 < AE mesh min X=-7870 -> OFF-MESH (campaign measured 169.5u off). AE maze is
re-authored geometry, so no faithful coordinate exists. Must pick an AE-mesh-on spot that
is a sensible labyrinth location -> next: analyze AE maze03's walkable layout + find where
the player enters, place the portal on-mesh + reachable.

---

## A1 - portal chain VERIFIED self-consistent (recon_portal_chain.py + place_maze03_portal.py)

- **`bossarena.qst`** (deployed Quests.arc, 2946 B): `Condition_OnLevelLoad` (isNot=false)
  -> `Action_ShowNpc(portal_olympianarena1.dbr)` + `Action_OpenDynGridEntrance(dynGridEntranceName=
  records/quests/portal_olympianarena1.dbr)` + `Action_UnlockFixedItem`. Opens the portal
  **BY RECORD NAME** - so an instance of `portal_olympianarena1.dbr` (GridEntranceDynamic)
  existing in the loaded level is all the quest needs. **NO Quests.arc change required** (as
  the plan predicted).
- **UID pairing correct:** SV maze03 portal exit_uid `6e513e90...` == crypt_floor1
  portal_olympianarena2 (GridExitOneWay) mouth_uid `6e513e90...` EXACTLY. The
  GridEntrance<->GridExit pair is intact. crypt landing 0x14 is byte-identical SV vs merged.
- **dest_guid** `dbc245c3...` == crypt_floor1 merged GUID -> entering the maze03 portal
  teleports to crypt_floor1 (Uber Dungeon), lands at portal_olympianarena2 (on-mesh, Wave1).
- DB records all resolve: portal_olympianarena1=GridEntranceDynamic (visible mesh),
  portal_olympianarena2=GridExitOneWay. boss_arena has 2x portal_olympianarena2 (idx 28/29,
  own DynGridEntrance chain, dest_guid=0 -> opened by its own logic; crypt->arena is a
  separate downstream link, not the maze03 entrance).

**PLACEMENT DECISION (A1):** SV placed portal_olympianarena1 0.3u from `doorframesecretos01`
(a Knossos SECRET-DOOR frame) in a decorated alcove at SV maze's WEST entrance (SV-local
~101,144), flanked by StatueMinoan pairs + braziers. AE TRIMMED that west alcove (SV-local
X=101 -> AE world X=-7974, 104u WEST of AE mesh min X=-7870 = OFF-MESH). BUT AE preserves
the Minotaur boss room INCLUDING `q07_minotaursecretosdoor` (a secret door!) @ AE-local
(289,150) world (-7787,-3793), on-mesh 0.14u. The faithful AE analogue of "the Olympian
portal at the secret door" = beside `q07_minotaursecretosdoor`. Chosen on-mesh cell (from
place_maze03_portal.py, openNbr 8/8, safe standoff): **AE-local (290.70, 1.20, 152.50)** =
world (-7785.3, 1.2, -3790.5): 3.0u from the secret door (mirrors SV's ~0.3u-from-secret-
door intent), 16.7u from the Minotaur boss proxy, 15.0u from the boss chest (so it is not
ON them), fully surrounded by walkable floor. This is on the AE Editor-baked navmesh, in
the boss room the player definitely reaches (Minotaur Lord fight = main Knossos quest), and
gated behind the secret door (reached after the boss). NOTE the player reaches the portal
AFTER the Minotaur fight - a sensible late-Knossos gate for an end-game Uber Dungeon.

**A1 rot:** SV portal used a specific facing; I will carry SV's EXACT rotation matrix from
its maze03 0x05 record so the injected record is byte-shape identical to SV's placement.

---

## INJECTION MACHINERY - two gaps found for A1 (must fix in tooling)

The deployed pipeline is `svaera_plus_portals.py`. For a SHARED AE level in INJECT_SPECS
it injects via `inject_into_0x05_v11` (base-72 records, correct for both v0x11 AND v0x0f).
The step-7 0x14-append (lines 583-654) appends a 0x14 entry per spec with `wants_0x14=True`
(or an `x14_payload`), keyed by the injected instance index (orig_instance_count + j), with
a hard collision assert.

- **GAP 1 (v0x0f skip):** line 552 `if blob_ver == 0x11:` else WARN+SKIP. maze03 is
  **v0x0f** -> injection would be SILENTLY SKIPPED. FIX: broaden the shared-level guard to
  accept 0x0f (its 0x05 records are base-72, byte-verified). `inject_into_0x05_v11` already
  walks base-72 so it works unchanged; only the version gate needs widening.
- **GAP 2 (0x14 append needs the section to exist):** the append loop only fires
  `if s['type'] == 0x14`. maze03 HAS a 0x14 section (size 0) -> the append WILL run and
  add my portal's 48-byte binding at instance index 447 (orig 447 instances -> my portal is
  index 447; collision-free since orig indices are 0..446). Confirmed maze03 sections =
  [0x5, 0x14(size0), 0x6, 0x9, 0xb, 0x17]. Good.

SV portal_olympianarena1 record: flags=0, **IDENTITY rotation** (rot bytes all identity),
local (101.838,1.0,144.520), 56-byte v0e record. So A1 byte-shape = flags=0 identity-rot
instance + the 48-byte 0x14 binding `58941143..` + `6e513e90..` + `dbc245c3..`.

---

## A2 - Garden of Merchants entrance: SKIP (genuinely blocked, evidence below)

The garden entrance is NOT a quest-driven warp and CANNOT be restored by record injection
within the constraints (no Quests.arc change; map tooling only):
- `imhere.dbr` + `seen_ocv2_trigger.dbr` are **BoundingVolume** records (orange spheres),
  NOT warps. `seen_ocv2_trigger` only grants a token: in `open_bloodcave_portal.qst` (already
  ported) `Condition_EnterVolume(seen_ocv2_trigger)` -> `Action_BestowTriggerToken(OCV2_Found)`
  -> later `Condition_OwnsTriggerToken(OCV2_Found)` -> `Action_ShowNpc(garden merchants)`. It
  REVEALS merchants; it does not move the player.
- **NO quest anywhere references `imhere.dbr`** - neither the deployed Quests.arc NOR SV's own
  upstream Quests.arc (54 quests scanned). And **no warp/teleport/MoveToLocation Action class
  exists in Quests.arc at all** (full Action_* enumeration: no move/warp/teleport).
- `teleportshrine_gom` is a `StrategicMovementTeleportShrine` (a click-to-fast-travel rift
  shrine, the RETURN path once discovered), not a step-in warp.
- So SV's first-entry into the garden was map-geometry (a 0x06 GridSystem portal or terrain
  teleport on the shared `startingfarmland06d`), which the merge dropped when it kept AE's
  re-authored startingfarmland06d (v0x11, 26KB re-authored 0x14). Restoring it needs either
  (a) authoring a 0x06 GridSystem portal on AE's re-authored level (not-yet-built binding,
  same class the recipe flags as unbuilt), or (b) a quest warp action that does not exist and
  the brief forbids adding. Re-injecting the two BoundingVolumes alone is INERT.
- **PROPOSED ALTERNATIVE (out of scope here):** author a 0x14 GridEntranceDynamic on an
  SV-only level we control that binds to the garden GUID (like A1's maze03 portal), OR add a
  quest warp step - both require net-new tooling / Quests.arc content. The interior navmesh is
  banked (Wave 1) so the destination side is ready; only the entrance authoring is blocked.

## A3 - Secret Place entrance: SKIP (genuinely blocked, evidence + alternative below)

- SV `scrabledeggs_floor06` (v0x0e, GUID `4b75d427...`, corner (-1956,0,-6193)) linked to
  `behindthesp` via a **0x06 GridSystem portal pair**. The merge KEEPS AE's re-authored
  `scrabledeggs_floor06` (v0x11, GUID `63197cac...`, corner (-1917,0,-6421), 0x06 size 919 -
  a different layout) whose 0x06 does NOT reference behindthesp. `behindthesp` (v0x0e, GUID
  `82535f98...`, kept SV-only) reciprocally references SV's scrabledeggs GUID `4b75d427`,
  which is NOT the AE scrabledeggs GUID in the merge.
- Restoring needs: (a) author a 0x06 GridSystem portal descriptor on AE's re-authored
  scrabledeggs_floor06, (b) remap behindthesp's 0x06 to AE's scrabledeggs GUID. The 0x06
  GridSystem portal-pair binary format is NOT reverse-engineered/built in this project (only
  the 0x14 GridEntranceDynamic append was newly built, for A1). No tooling authors a 0x06
  pair, and the door placement on AE's re-authored geometry is ungateable offline.
- **PROPOSED ALTERNATIVE (out of scope here):** host the Secret Place mouth on an SV-only
  level we DO control (e.g. add a `portal`-style GridEntranceDynamic with a 0x14 binding to
  behindthesp's GUID onto a kept SV-only Rhodes level), using the A1 0x14-binding machinery
  now proven, rather than editing AE's scrabledeggs 0x06. The behindthesp interior navmesh
  (Wave 3a) is banked so the landing IS gateable once a host + mouth spot is chosen.

## IMPLEMENT / SKIP SUMMARY
| Item | Decision | Why |
|------|----------|-----|
| A1 maze03 -> Uber+Boss | **IMPLEMENT** | chain verified self-consistent; on-mesh spot chosen; needs v0x0f inject fix + portal spec |
| A2 Garden | SKIP (evidence) | no warp mechanism exists; needs 0x06 authoring or Quests.arc change |
| A3 Secret Place | SKIP (evidence) | needs 0x06 GridSystem pair authoring (not-yet-built); ungateable |
| B1 smoke/dark-cloud atmosphere | **IMPLEMENT** | re-inject SV occult FX/lights (measured exemplars, EffectEntity/no aggro) |
| B2 exploding sprites | **IMPLEMENT** | mirror Greece pitspawner+lildude (measured), >=15u standoff from occultist |
| B3 move fountain+caravan | **IMPLEMENT** | move to HV01 north (occultist side), >=25u from all 4 hostiles, keep UID |

---

## DESIGN DECISIONS (locked before implementation)

Planner: `tools/debug/plan_b_final.py` (all mutual constraints enforced simultaneously).

### B3 - MOVE fountain + caravan to the occultist side (HV01 north)
- **Fountain** `respawntempleorient01` (flags=1, UID `feeb4bc6ce4e08c0e279b3824244aeeb`
  KEPT - GROUPS binding is position-independent): move from HV01-local (49.26,15.63,14.95)
  world (-84.7,-104.4,2188.9) [9.1u from a beastman proxy] TO **HV01-local (35.70,17.60,
  143.10)** world (-98.3,-102.4,2317.1). New spot: 100.5u from every HV01 hostile (was 9.1u),
  9.2u from the occultist (Border04) = right at the occultist's doorstep, openNbr 8/8, on the
  largest walkable comp (reachable). MOVE not duplicate: change the existing INJECT_SPECS
  coord (the old position is removed automatically).
- **Caravan** `caravan_silkroad` (flags=0, +12B 0x14 (2,0,1)): move from HV01-local
  (55.30,15.60,14.90) TO **HV01-local (41.70,17.80,143.10)** world (-92.3,-102.2,2317.1).
  6.0u E of the new fountain, 100.9u from hostiles, openNbr 8/8. Keeps its native rot + 0x14.
- The 4 HV01 hostiles (unchanged, NOT touched): ag_beastman_neanderthal_02t/02n/03t + encact3.

### B2 - exploding sprites near the occultist (Border04), aggro-safe standoff
Mirror the WORKING Greece pit-sprite cluster (DelphiLowlands02): a `t1_pitspawner_01` (the
emitter) + a few `t1_lildude_01/02` around a `pit_fx01`, identity rotation (SV uses identity).
Placed on the FAR (north) side of the occultist so the player respawning at the fountain
(south) and walking to the merchant does NOT pass through them.
- **Cluster seed** = Border04-local (50.70,1.80,34.30) world (-83.3,-102.2,2336.3):
  **18.0u from the occultist** (Greece working standoff was 10.8-11.6u -> 18u >> that, safe),
  24.4u from the new fountain, 21.2u from the new caravan (both >= the brief's 20u), 16.4u
  from the wagon, openNbr 8/8. Cluster the sprites within ~3u of the seed, each re-verified
  on-mesh. Records = Class Monster (aggro) so the >=18u standoff is load-bearing; all resolve
  in the arz. AGGRO REASONING: DRX lildude aggro/leash is short (they are pit-bound exploders);
  the Greece scene proves ~11u is safe next to a talkable merchant, so 18u has a >6u margin,
  and the player's approach vector (from the south fountain) never crosses the sprite side.

### B1 - smoke / dark-cloud atmosphere over the entrance area (occultist + new fountain)
Restore SV's dropped occult atmosphere, SV-faithful, into TWO shared levels (all EffectEntity
/light/Decoration/Tile = NO aggro), at SV's exact local coords (byte-exact; these shared
levels are NOT grid-shifted so SV-local == merged-local):
- **HiddenValleyBorder04** (the occultist scene, all from SV's own Border04 0x05):
  `fog_occult_fx01` @ (26.64,1.48,24.83)+(36.90,1.62,23.88); `occultistaura_fx01` @
  (41.01,1.51,21.99) [on the merchant]; `pit_fx01` @ (26.98,0.38,24.94); `10mlight_dyn_purple`
  @ (47.03,6.51,29.58)+(41.09,6.51,12.38); `10mlight_dyn_red` @ (47.31,6.62,29.64)+(41.14,
  6.56,12.40); `5mlight_stat_blue` @ (32.35,6.06,24.50)+(35.65,7.14,24.22); `mc_hades_woodpyre01`
  @ (27.65,0.94,25.31); `mc_hades_anouranfirepit02` @ (27.35,1.59,25.04); `totem` @ (40.24,1.62,
  12.34)+(46.46,1.62,29.55); `fx_disciple_aura_eyechantment01` @ (38.68,4.96,29.89)+`_02` @
  (38.92,4.92,29.63). All flags=0, no 0x14 (SV places none). These land right on the occultist
  merchant scene = the "dark cloud / smoke special area".
- **Also a few emitters at the NEW fountain spot** so the moved respawn area reads as the
  atmospheric entrance too: add `10mlight_dyn_purple` + `fog_occult_fx01` near HV01-local
  (35.7,17.6,143.1) (the new fountain). (SV's original HV01 totems/lights were at local Z~98-106
  near the OLD interior, far from the new north spot; a couple of fresh emitters at the new
  fountain is the faithful intent - "atmosphere over the respawn portal".)

### A1 - maze03 portal (final coord)
Inject `portal_olympianarena1.dbr` (GridEntranceDynamic) into AE Maze03 at **AE-local
(290.70,1.20,152.50)** world (-7785.3,1.2,-3790.5), flags=0, IDENTITY rotation, + a 48-byte
0x14 binding (mouth `58941143..` + exit `6e513e90..` + dest `dbc245c3..`) at the injected
instance index. 3.0u from q07_minotaursecretosdoor, 16.7u from the Minotaur boss, on the AE
Editor-baked navmesh. Requires the v0x0f shared-level injection fix in svaera_plus_portals.

**A1 scope clarification (measured on the rebuilt map):** this patch restores the
maze03 -> **Uber Dungeon (crypt_floor1)** entrance. crypt_floor1 carries
`portal_olympianarena2` (the GridExitOneWay LANDING, idx 192, on-mesh 0.00u from Wave 1) +
`portal_uberdungeon_return` (return NPC, idx 247, already injected). There is NO direct
crypt->boss_arena portal in the map data; the Boss Arena is reached via the ported
`bossarena.qst` progression downstream. So the DIRECTLY restored + verified link is
maze03 -> Uber Dungeon; Boss Arena interior is walkable (Wave 1) + its quest is ported but
the crypt->arena hop is a downstream walk-test question.

---

## IMPLEMENTATION COMPLETE - all gates PASS (build: local/Levels_merged.arc 688,687,541 B)

Baseline snapshot for diffs: `local/Levels_merged.build23-baseline.arc` (byte-identical to
the deployed `work/.../Levels.arc`, md5 `50d7f77a...`). Rebuild log: `local/rebuild_polish.log`
(EXIT 0, 0 bad offsets, 0 bad magic). Tooling changes: `tools/svaera_plus_portals.py`
(v0x0f shared-level inject fix), `tools/build_section_surgery.py` (A1 portal + 0x14 binding,
B1 atmosphere records + SV rotations, B2 sprite records, B3 moved fountain/caravan coords +
HV01 emitters). Gate scripts: `tools/debug/gate_polish_collateral.py`,
`gate_polish_placement.py`, `gate_polish_byteparity.py` (+ the recon_*/plan_b_* scripts).

Injection log (all landed): roadtotown03a 3, hiddenvalley01 5, hiddenvalleyborder04 22,
**maze03 1 (v0x0f)**, crypt_floor1 1, drxfirstxistion 1, new_secretdoor 1. 0x14 appends:
caravan idx 206, **maze03 portal idx 447** (kept 0 orig + added 1).

### GATE RESULTS (verbatim)
- **Collateral (gate_polish_collateral.py): PASS.** QUESTS/GROUPS/SD/BITMAPS/DATA2 IDENTICAL;
  changed blobs = 3 (maze03 +172B, hiddenvalley01 +387B, hiddenvalleyborder04 +2353B) - ONLY
  the intended levels; 0 bad magic, 0 malformed across 2282 levels; **2261 0x0b navmeshes
  compared, 0 changed** (blood-cave + all 15 SV-area navmeshes byte-identical - this wave
  touches only 0x05/0x14).
- **Placement (gate_polish_placement.py): PASS.**
  - A1: portal present idx 447 at (290.70,1.20,152.50), flags=0, IDENTITY rot, **on-mesh
    0.00u**, 0x14 binding mouth/exit/dest exact, **dest_guid resolves to crypt_floor1**.
  - B3: fountain world (-98.3,-102.4,2317.1) flags=1 **UID feeb4bc6... UNCHANGED**, on-mesh
    0.00u, **100.5u** from nearest hostile (was 9.1u); caravan on-mesh 0.00u, 0x14=(2,0,1),
    100.9u from hostiles. HV01 hostiles (unchanged, 4): ag_beastman_neanderthal_02t/02n/03t +
    encact3.
  - B2: 4 sprite instances (pitspawner + 3 lildude), all **on-mesh 0.00u**, **18.0u from the
    occultist** (Greece working standoff 10.8u), **>=20.6u from fountain+caravan**.
  - B1: 11 atmosphere record types present (16 instances in Border04 + 3 at new fountain);
    occultistaura at SV-exact coord.
- **Byte-parity (gate_polish_byteparity.py): PASS.** Every B1/B2 record = v0x11 size 72,
  flags 0, rotation matching its NEAREST SV exemplar (rotated purple/pyre/totems carry SV's
  exact matrix; identity records stay identity), coord 0.0003-0.0006u from SV (float32 epsilon).
- **Blood-cave verify_merged_bc_navmeshes: 24/24 PASS** (0x0a stripped).
- **entrance_landing_check --check-merged: G2 PASS** (508 cells, dY +0.00u, donor + merged).
- **Reachability (gate_polish_reachability.py): PASS.**
  - Moved fountain + caravan are in HV01 component #0 (the largest, 111,758 cells) - the SAME
    component as the cave-mouth `SilkRdDngEntrance` (0.14u) - so a player entering HV01 can
    path to the fountain (the move did NOT strand it).
  - maze03 portal is in component #0 (largest, 2,053,366 cells) - the SAME component as the
    Minotaur boss (0.03u), the secret door, AND the one-way door - so the portal is in the
    walkable boss room the player reaches in the main Knossos quest, on the boss-fight
    navmesh + its exit path (genuinely reachable, not sealed).

### A1 crypt landing + return (verified on the rebuilt map)
crypt_floor1: `portal_olympianarena2` landing @ world (-2438.1,10.0,-2450.1) [GridExitOneWay,
on-mesh 0.00u from Wave 1] + `portal_uberdungeon_return` @ (-2438.0,10.0,-2467.0) [return NPC,
16.9u away]. boss_arena: 2x `portal_olympianarena2` (its own chain). No direct crypt->arena
map portal (that hop is quest/downstream).

---

## WHAT WILL MUST WALK-TEST (per shipped item)

Full TQ restart required (running game holds the map in RAM). All on a Custom Quest character.

### A1 - Uber Dungeon entrance (maze03, Knossos, Act 2)
- Reach the **Knossos underground Minotaur maze (Maze03)** in the main Greece questline and
  fight through to the **Minotaur Lord boss room**. After opening the `q07_minotaursecretosdoor`
  secret door / clearing the boss, look for the **Olympian Arena portal** (a visible portal
  object, `TJ_JudgementRoom_PortalObject`) standing ~3u from the secret door in the boss room,
  at world (-7785,-3790). WALK INTO IT.
- EXPECTED: the `bossarena.qst` OnLevelLoad opens the portal (Action_OpenDynGridEntrance by
  record name) and it teleports you to the **Uber Dungeon (crypt_floor1)**, landing at the
  Olympian Arena exit portal. Walk the crypt; the return NPC (`portal_uberdungeon_return`) is
  ~17u from the landing.
- WHAT IS OFFLINE-VERIFIED: the portal is present, on the AE baked navmesh, in the boss-room
  component, byte-shape = SV's record, and its 0x14 binding resolves to crypt_floor1's GUID
  (the GridEntrance<->GridExit UID pair is intact). WHAT NEEDS EYES: that the quest opens it
  in-game and the teleport fires (the GridEntranceDynamic + Action_OpenDynGridEntrance chain is
  unrehearsed in this mod - this is the one thing no offline gate can confirm). If the portal
  is visible but does not activate, the fallback is documented (the quest opens by record name,
  so re-check the quest's OnLevelLoad level binding). BOSS ARENA: reached via the ported
  bossarena.qst progression downstream of the Uber Dungeon, not a direct maze03 hop - note
  whether the Boss Arena becomes reachable from the Uber Dungeon.

### B3 - moved respawn fountain + caravan (blood-cave cave mouth, HiddenValley01)
- Enter HiddenValley01 (the Silk Road cave mouth). The **respawn fountain** and the
  **Super-Caravan** are now at the NORTH end of the area (world ~(-98,2317) and (-92,2317)),
  right by the connection to the occultist merchant area, ~100u from the beastman spawn packs.
- EXPECTED: dying/respawning no longer drops you into the beastman swarm (they are now ~100u
  south); the caravan is usable (Super-Caravan storage) next to the fountain. WHAT IS
  OFFLINE-VERIFIED: both are on-mesh (0.00u), in the cave-mouth walkable component (reachable),
  >=100u from every spawn proxy, and the fountain KEEPS its respawn-group UID (feeb4bc6...) so
  the respawn binding is intact. WHAT NEEDS EYES: that the respawn actually happens at the new
  spot and no OTHER swarm reaches it (only the 4 HV01 proxies were enumerated; watch for any
  mob that wanders up from the south or in from Border04).

### B1 - smoke / dark-cloud atmosphere (occultist + new fountain)
- At the occultist merchant scene (HiddenValleyBorder04, just north of the cave mouth) you
  should now see occult FOG + a purple/red/blue-lit glow + a firepit/pyre + cult totems + an
  aura on the merchant (the "dark cloud / smoke special area"). A couple of purple lights + fog
  should also sit at the new respawn-fountain spot.
- EXPECTED: purely visual (no gameplay effect). WHAT IS OFFLINE-VERIFIED: all 11 record types
  present at SV's exact coords, byte-shape = SV's placement (rotations included), all resolve in
  the arz. WHAT NEEDS EYES: that the FX render as intended (some DRX FX can look different from
  memory) and nothing floats oddly on AE's re-authored Border04 terrain (the occultistaura sits
  at SV's coord, 5.7u from where AE moved the merchant - confirm it still reads as "on" the
  occultist scene).

### B2 - exploding sprites near the occultist (HiddenValleyBorder04)
- North of the occultist merchant (~18u), a cluster of **exploding pit-sprites** (t1_lildude)
  + their spawner should appear, mirroring the Greece pit-sprite scene, near a pit FX.
- EXPECTED: the sprites explode/attack when you get close, BUT you can talk to the occultist
  merchant WITHOUT the sprites aggroing you (they are 18u away, > the Greece scene's proven-safe
  ~11u standoff, and on the far side of the merchant from the respawn fountain so your approach
  never crosses them). WHAT IS OFFLINE-VERIFIED: 4 sprite instances on-mesh, 18u from the
  merchant, >=20u from the fountain+caravan, byte-shape = the Greece Monster exemplar. WHAT
  NEEDS EYES (the load-bearing test): that the sprites genuinely do NOT aggro a player standing
  at the merchant. If they DO reach the merchant, the fix is to push the cluster further north
  (the standoff is a single coord change per sprite in INJECT_SPECS).

## SKIPPED (with evidence, per the brief's "skip if genuinely blocked")
- **A2 Garden of Merchants**: no warp mechanism exists to restore via record injection (no
  quest references imhere; no warp/teleport Action class in Quests.arc; the entrance was a
  0x06/terrain teleport on a re-authored AE level). Needs 0x06 authoring or a Quests.arc warp
  step (both out of the map-tooling-only scope). Interior navmesh already banked.
- **A3 Secret Place**: needs authoring a 0x06 GridSystem portal PAIR on AE's re-authored
  scrabledeggs_floor06 + remapping behindthesp's 0x06 GUID. The 0x06 GridSystem portal-pair
  binary format is not-yet-built tooling in this project (only the 0x14 GridEntranceDynamic
  append was newly built, for A1). Proposed alternative: host the mouth via a 0x14
  GridEntranceDynamic on a kept SV-only Rhodes level we control (the A1 machinery), documented.

## NOT DEPLOYED / NOT COMMITTED (per the brief)
The rebuilt map is `local/Levels_merged.arc` (688,687,606 B). Quests.arc UNCHANGED (A1 needs
none; A2/A3 skipped). No deploy, no commit, no Workshop - the main session owns those.
Baseline for rollback/diff: `local/Levels_merged.build23-baseline.arc`.
