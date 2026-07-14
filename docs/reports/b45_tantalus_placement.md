# b45 - Tantalus placement fix + containment audit

> **Bug (Will, 2026-07-13, verbatim):** "the den of tantalus monsters did not get placed inside of
> the den of tantalus, they got placed in the wrong location."
>
> **Verdict:** CONFIRMED and FIXED. The Tantalus encounter proxy was on-mesh in the correct host
> level but 28.1u from the den marker, tucked in the far SE corner of a large open level, out past
> the den mouth. Re-placed 10.2u from the den marker. Branch `feat/b45-tantalus`, commit for the
> map change: `d689d45`. NO heavy build (blob-parse + dry-run injection into copies + surveys only).

---

## 1. Ground truth established

- **Deployed DEV map Will played** = `.../CustomMaps/SoulvizierClassicDEV/Resources/Levels.arc`,
  **MD5 841c56cd** = byte-identical to `local/Levels_merged_TESTHUB.arc`. Canonical =
  `local/Levels_merged.arc` MD5 60a62880. Both were probed directly.
- **Den of Tantalus host** = blob **[755]** `XPack\Levels\Area04_Styx\Styx_SwampBorder_01.lvl`,
  v0x0f, grid corner (-396,0,-10209). This is the ONLY level whose 0x05 places the den POI
  `records\xpack\poi\hades\pj_denoftantalus.dbr` (local (26.0,-13.0,112.3) = world (-370,-13,-10097)).
- **Old placement (what Will played):** `q_tantalus_lone.dbr` at LOCAL **(54.0,-15.2,114.3)** =
  WORLD **(-342,-15.2,-10094.7)**, inst[71], flags=0. On-mesh (d=0.10u, clr 100% N/E/L, comp#1).
  Present at this exact spot in EVERY build since 2026-07-11 (R4-snapshot, canonical, TESTHUB, and
  the live deployed DEV map) - no build ever grossly misplaced it.

## 2. Root-cause analysis - what the mechanism was, and what it was NOT

The prime suspect handed to this lane was the b36 R3 coordinate-FRAME bug (grid-local vs world
confusion). It was investigated and **RULED OUT**, along with two other candidate mechanisms:

| Candidate mechanism | Verdict | Evidence |
|---|---|---|
| **R3/R4 coordinate-frame bug** (spec coord surveyed in the wrong frame) | **NOT the cause** | The R4 frame fix (+16 navmesh-origin offset) is CORRECT: native floor anchors at the den's west edge read 17-18u off in the RAW frame but ~2u in the corrected frame - only floor objects in the corrected frame. The boss at (54,114.3) is genuinely on the walkable floor at world (-342,...), d=0.10u, comp#1. Applying any frame correction does NOT move it onto the den marker. |
| **Wrong host-level key** | **NOT the cause** | The placement is in blob [755], the level that OWNS the pj_denoftantalus POI. Correct host. |
| **Grid-shift decoupling** (merge shifted the level away from the SD region banner) | **NOT the cause** | `svaera_plus_portals.GRID_SHIFT` contains only `xbloodcave` + `random09a`. Area04_Styx is unshifted; merged blob [755] corner == base-game corner (-396,0,-10209); merged 0x0b navmesh + 0x06/0x09/0x14/0x17 are byte-IDENTICAL to the base game (only 0x05 differs, by the one appended proxy). The level sits exactly where base-game TQ puts the den. |
| **BAD SPEC COORDINATE** (clearance optimized over proximity) | **CONFIRMED CAUSE** | The spec's own note: the POI marker sits in "a cramped rocky mouth (1u disc)" so it moved 28u EAST for a 9u clearance disc, ASSUMING that was "unambiguously in the Den of Tantalus." Will's in-game ground truth proves that assumption wrong: 28u east is the far SE corner of a large open level, out past the den mouth on the open Styx floor. |

### Why 28u east reads as "the wrong location"

The Den of Tantalus (blob [755]) is a **large open SwampBorder level**, not a tight interior. Three
reference points frame the den the player experiences:

- **POI marker** (den identity / banner source): local (26,112.3) = world (-370,-10097), at the
  WEST edge of the south chamber.
- **b39 hub-v2 den-entrance landing** (where the player ARRIVES when travelling to the den via the
  Helos hub): local (52,80) = world (-346,-10131). The b39 author's own comment already flagged the
  boss as "**~36u off Tantalus**."
- **Old boss spot:** local (54,114.3) = world (-342,-10094.7) - the SE corner, **28.1u from the
  marker and 34.4u from the landing**: the far corner from BOTH the den identity point and the
  player's arrival point. A void seam (local x~62-70) even splits the northern den, so the boss and
  the arrival point sit in different sub-chambers.

That is why the monsters read as "not in the den, wrong location": they landed in the open SE corner,
far from the marker and from where the player walks in.

## 3. The fix

**New placement: LOCAL (34.0, -13.4, 106.0) = WORLD (-362, -13.4, -10103).** The closest
full-clearance spot to the den marker.

| Property | Old (54,-15.2,114.3) | New (34,-13.4,106.0) |
|---|---|---|
| Distance to den POI marker | **28.1u** (wrong location) | **10.2u** (unambiguously in the den) |
| Distance to b39 arrival landing | 34.4u | 31.6u (clear of the landing, no collision) |
| On-mesh (d, N/E/L) | 0.10u | 0.14u |
| clr@3.5 N/E/L | 100/100/100 | 100/100/100 |
| clr@6 N/E/L (escort + hoard-chest room) | 100/100/100 | 97/97/97 |
| component | #1 (main) | #1 (main) |
| floor Y (navmesh-validated +/-0.2u) | -15.4 (sunken pool) | -13.4 (den-mouth floor) |
| nearest native monster/geyser proxy | ~12.8u | 9.0u (collision guard PASS, >6u) |

The encounter composition is preserved intact: this is ONE proxy (`q_tantalus_lone`, flags=0,
exemplar rot) that DB-side spawns the boss + 2 champion Famished-Shade escorts + the accessory hoard
chest, so moving the single proxy moves the whole encounter. Clear of the b39 den-entrance landing
(31.6u) and, since the hoard chest rides the proxy as a DB-side accessory (no separate map
placement), it spawns with the boss at the new spot - nothing to reconcile against a b42 chest coord.

### Files changed (commit d689d45)

- `tools/build_section_surgery.py` - `UBERBOSS_SPECS[TANTALUS_HOST_KEY]`: coord (54.0,-15.2,114.3)
  -> (34.0,-13.4,106.0) + RCA comment.
- `tools/debug/survey_uberboss_spots.py` - `BOSS_SPOTS` M5 entry updated so the map gate re-surveys
  the new spot (old spec-primary kept as a labelled retired reference).

## 4. Containment audit (curious-QA: every placed encounter)

For every authored encounter, confirmed the placed world coords fall INSIDE the intended named
area's level (correct host blob + on-mesh in all 3 tilesets + inside the walkable bbox). Ran against
the deployed TESTHUB map; b41 in-flight coords surveyed read-only against the canonical navmesh.

| Encounter | Intended host | In host? | on-mesh N/E/L | Verdict |
|---|---|---|---|---|
| **Tantalus** | styx_swampborder_01 [755] | YES | Y/Y/Y | on-mesh but 28u off den marker = **THE BUG (fixed)** |
| Dorus | medea_templeug_tomb01 [784] | YES | Y/Y/Y | contained |
| Charon/Golden Bough | styx_riveredge_01 [749] | YES | Y/Y/Y | contained |
| Mnemophage | judgment_templeug_mnemosyne01 [801] | YES | Y/Y/Y | contained |
| Ephialtes | judgment_stonecity_exit01 [931] | YES | Y/Y/Y | contained |
| Blood-Toxeus | bossfight.lvl [2256] | YES (via native `q_leinth_lone` proxy; DB remaps leinth->Toxeus) | Y/Y/Y | contained |
| Broodmother nest (+6 eggs) | tombobs02 [512] | YES | Y/Y/Y | contained |
| Obsidian roulette a,c | tombobs02 [512] | YES | Y/Y/Y | contained |
| Obsidian roulette b,d | tombobs01 [511] | YES (roulette deliberately spans both Obsidian levels) | Y/Y/Y | contained |
| Vashkarr | random05a [464] | YES | Y/Y/Y | contained |
| Enslaver warband | drxfirstxistion_connection [2247] | YES | Y/Y/Y | contained |
| Helos warden | startingfarmland06d [310] | YES | Y/Y/Y | contained |
| **b41 in-flight:** polisgaoler, hadesmarshal, generals a/b/c, diadochi, neferkha, bloodtoxeus_ambush | hadespalace/elysian/egypt/bloodcave hosts | YES (all 8) | Y/Y/Y, clr 100%, comp#1, in-bbox | contained (report to b41 lane: clean) |

**Result: Tantalus was the ONLY out-of-area placement.** Every other encounter - deployed and b41
in-flight - is properly contained. The Tantalus-class risk (on-mesh but semantically outside a small
named region inside a large open level) is unique to Tantalus; every other boss is in a dungeon
interior where the whole level IS the named area, so on-mesh + in-bbox is sufficient containment.

### Two minor, non-blocking notes (not containment failures, out of this lane's fix scope)

- **TESTHUB-only:** an extra `q_vashkarr_lone` test copy exists in `hiddenvalley01` (the SVC_TEST_HUB
  yard) and reads off-mesh there. It is a local test-yard artifact and does NOT ship (the canonical
  Vashkarr in random05a is on-mesh). Worth a yard-spot nudge in a TESTHUB pass.
- **Code hygiene:** `Q_BLOODTOXEUS_LONE_DBR` is defined in build_section_surgery.py but never wired
  into INJECT_SPECS (Blood-Toxeus ships via the native `q_leinth_lone` proxy). Harmless dead constant.

## 5. Verification gates (NO heavy build)

- **py_compile** (build_section_surgery.py + survey_uberboss_spots.py): PASS.
- **Survey gate** (`survey_uberboss_spots.py --bosses`, the same gate the other 5 bosses use): new
  spot local(34,106) -> N/E/L d=0.14u clr 100% comp#1 -> **OK**.
- **Dry-run injection into copies** (real `inject_into_0x05_v11` on the base-game blob [755]):
  - Harness reproduces the deployed build byte-for-byte: `inject(base_0x05, OLD) == deployed_0x05` -> True.
  - NEW vs OLD delta = **7 bytes, all inside the appended proxy's position field** (+40..+52); OLD
    (54,-15.2,114.3) -> NEW (34,-13.4,106.0). String table + all 71 native instances byte-identical.
- **Blob-diff / no-break gate:** base-game blob [755] vs deployed differ ONLY in 0x05; the **0x0b
  navmesh (275,312 B), 0x06, 0x09, 0x14, 0x17 are byte-IDENTICAL**. The change touches ONLY the
  `TANTALUS_HOST_KEY` entry, so ONLY blob [755] changes across the whole map; within it, only the
  proxy's position. The 71 native den instances (karkinos/anouran/6 geysers/Hades shrine/POI/
  watchtower/setdress) are byte-unchanged (append-only proof).
- **QUESTS 256-window parity:** UNTOUCHED. The change is a single 0x05 instance coordinate; the world
  QUESTS(0x1b) section is a separate world-level structure not reached by 0x05 injection.
- **Navmesh byte-identity for untouched levels:** holds - no other blob changes; blob [755]'s own
  0x0b is byte-identical (append-only to 0x05).
- **Collision guard:** nearest native monster/geyser proxy to the new spot = 9.0u (>6u) -> PASS.

## 6. Deploy note

Canonical-map content change (blob [755] only). Per the standing coupling, the Levels change ships in
the wave that also carries the Tantalus DB records (arz + Text). The placement is inert until both
the `q_tantalus_lone` proxy records and this map placement exist. RESTART STEAM before the in-game
retest (the den banner + boss position are the one-glance check: travel to the Den of Tantalus, the
boss + escorts should now stand ~10u from the den marker, in the den, not out in the SE corner).
