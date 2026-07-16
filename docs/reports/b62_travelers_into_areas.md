# b62 TRAVELERS-INTO-AREAS - enter-offers + return-to-origin (Will 2026-07-14 final design)

> Branch `feat/travelers-into-areas` (worktree `travelers-v3`). Continues a killed session's
> reachability sweep (`scratch_audit/travelers_into_areas_sweep.py`,
> `scratch_audit/secret_place_reach.py`, `scratch_audit/enter_landings_wiring.py` - kept as
> read-only diagnostics, not committed as production tools). Quest-only + Text-only wave: **zero
> new arz records, zero new map placements, zero new QUESTS registry entries.**

## Will's design (verbatim intent)

1. In-world travelers near each SV area must take players INTO that area (today everything
   returns to Helos). Examples given: the Athens tomb guy -> spartacryptlevel2 via the dormant
   crypt landing; the post-Minotaur guy -> its area. "Sweep ALL, unseal every currently-
   inaccessible SV area."
2. Each area's RETURN NPC takes the player back to WHERE THEY TRAVELED FROM: primary = the paired
   ORIGIN entrance (where that area's enter-offer traveler stands), secondary = Helos (a static
   two-option dialog - the engine cannot track dynamic origin; documented here as asked).

## Ground truth: which SV areas are actually sealed (DEV/TESTHUB - Will's live play surface)

**Will's play surface right now is TESTHUB**, not canonical: per `docs/HANDOFF_LIVE_STATE.md`,
both `SoulvizierClassicDEV` and `SoulvizierClassicDEV2` currently carry the **TESTHUB** Levels.arc
(`d4965d29`) over the build40 DB/Text/Quests - this is what his `_Toxeus` character actually
plays. The reachability sweep therefore targets `local/Levels_merged_TESTHUB.arc` (2282 levels).

Two measurements were run (both read-only, no map build):
- **Part A** - inbound `0x14` portal-payload references to each candidate area's level GUID
  (map-wide, excludes self-references).
- **Part B** - boat-dialog **route** reachability (the actual travel mechanism post-P0): for
  every restored area, does any `Action_BoatDialog` route land inside it, AND is that route's NPC
  actually PLACED in the TESTHUB build?

| Area (level) | Inbound 0x14 | Boat route lands inside + NPC placed? | Verdict |
|---|---|---|---|
| spartacryptlevel2 (Sparta Crypt interior) | 0 | Almyros's route lands there but Almyros is **unplaced** in TESTHUB | **SEALED** |
| crypt_floor1 (Uber Dungeon interior) | 0 | same - Almyros's route dormant | **SEALED** |
| murderbossroom (Secret Place crow-boss room: Murderbunny + maggot-statue dais) | 0 | no route at all | **SEALED** |
| gardenofmerchants | 0 (native design) | `svc_helos_trav_garden` lands directly inside | reachable |
| darkforestenter (Secret Place forest-cluster entry) | 0 (native design) | `svc_helos_trav_secret` lands directly inside | reachable |
| catacube02_floorlast (Athens catacomb) | 0 (native design) | `svc_helos_trav_sparta` lands there | reachable (outer landing) |
| maze03 (Knossos labyrinth) | 0 (native design) | `svc_helos_trav_uber` lands there | reachable (outer landing) |

Box-adjacency check (level index corner+half-extent boxes, 2u pad) confirms `murderbossroom`
shares **no boundary** with any other Secret_Place level (`BehindtheSP`/`DarkForestEnter`/
`WoodsCorner`/`SecretForest2`/`PillagedVillage`/`ForestObsidianTransition`/`RogueEncampment`/
`tFinale`) - it cannot be reached by walking either. It is genuinely isolated.

## What got wired (item 1: enter-offers) and what did not (murderbossroom)

Of the 16 in-world return NPCs that exist today (11 `svc_area_return_*` outer-landing returns + 5
`svc_testhub_return_*` interior returns), only **two** gate a truly sealed separate area AND
already have an **existing placed NPC on both ends of the round trip** (the precondition for a
quest-only fix with no new map placement):

| Sealed area | Outer NPC (already placed, gets the NEW enter-offer) | Inner NPC (already placed, stranded until now) |
|---|---|---|
| Sparta Crypt (`spartacryptlevel2`) | `svc_area_return_sparta` @ CataCube02_FloorLast | `svc_testhub_return_sparta` @ spartacryptlevel2 |
| Uber Dungeon (`crypt_floor1`) | `svc_area_return_uber` @ Maze03 | `svc_testhub_return_uber` @ crypt_floor1 |

**murderbossroom is NOT wired** - it has no placed NPC on the inner end at all. Adding an
enter-offer to `svc_testhub_return_secret` (the darkforestenter outer NPC) without a paired return
NPC inside murderbossroom would strand the player with no way back - exactly the class of bug
that produced the 2026-07-12 P0 ("Helos-south walk-through -> Garden of Merchants, no way back").
That needs a **new map-lane NPC placement** first (a return traveler inside murderbossroom); it is
queued below as a BACKLOG follow-up, not attempted in this quest-only wave.

## The full NPC -> enter-dest / return -> origin table

| Traveler | Role | Placed in | Dest / new option | Label tag |
|---|---|---|---|---|
| `svc_area_return_sparta` | existing (Helos return) + **NEW enter-offer** | CataCube02_FloorLast (Athens catacomb, TESTHUB-only) | Helos plaza `(-5980,1,909)` (unchanged) **+ NEW:** descend to spartacryptlevel2 `(-5596,-2,-1410)` | `tagSVCAreaReturnToHelos` (existing) + **`tagSVCEnterSpartaCrypt`** = "Descend into the Sparta Crypt" |
| `svc_area_return_uber` | existing (Helos return) + **NEW enter-offer** | Maze03 (Knossos labyrinth, TESTHUB-only) | Helos plaza `(-5980,1,909)` (unchanged) **+ NEW:** enter crypt_floor1 `(-2438,10,-2450)` | `tagSVCAreaReturnToHelos` (existing) + **`tagSVCEnterUberDungeon`** = "Enter the Uber Dungeon" |
| `svc_testhub_return_sparta` | interior return, **RETARGETED** | spartacryptlevel2 (canonical + TESTHUB) | ~~Helos + Blood Cave~~ -> **origin** Athens catacomb `(-6587,1,-3180)` (primary) + Helos plaza `(-5980,1,909)` (secondary) | **`tagSVCReturnToAthensCatacomb`** = "Athens Catacomb (Return)" + `tagSVCTestHubToHelos` (reused) |
| `svc_testhub_return_uber` | interior return, **RETARGETED** | crypt_floor1 (canonical + TESTHUB) | ~~Helos + Blood Cave~~ -> **origin** Knossos labyrinth door `(-7793,1,-3793)` (primary) + Helos plaza `(-5980,1,909)` (secondary) | **`tagSVCReturnToLabyrinthDoor`** = "The Labyrinth Door (Return)" + `tagSVCTestHubToHelos` (reused) |

Static-dialog design note (per Will's ask, documented as requested): the engine has no
"remember where the player teleported from" state, so "return to origin" is implemented as the
FIXED outer landing each area's enter-offer traveler stands at (the one and only origin these two
areas can be reached from), not a dynamically-tracked one. This is the best static approximation
available; if a future area gets a second, alternate origin, its interior return would need a
third menu option or a different design.

## Mechanics (matches the proven pattern; no registry change)

Both new pieces of behaviour ride the **already-registered** `sv_commonmechanics.qst` refire step
(`HELOS_PORTAL_HOST_STEP`) - the same host every other hub route uses. No `.qst` file is added or
removed from the world `QUESTS(0x1b)` section, so the build22 256-entry load-window law is
untouched (proven by the dry-run byte-count below; the section itself is never touched by this
quest-only, no-map-build wave).

- **Enter-offers** (`build_quest_files.TRAVELER_ENTER_OFFERS`, applied by
  `_add_traveler_enter_offers`): one *extra* `Condition_OnLevelLoad` trigger per NPC, each with a
  single new `Action_BoatDialog`. "Multiple triggers on one NPC accumulate boat-menu ports" is the
  same proven mechanism Almyros's own multi-destination menu and every multi-dest hub NPC already
  rely on (`build_quest_files.py` comment, base-game quest-8 precedent). Mirrors
  `_add_helos_traveler_hub_travel` byte-for-byte.
- **Return-to-origin** (`build_quest_files.TESTHUB_RETURN_DESTS_BY_NPC`, read by
  `_add_testhub_portal_travel`): a per-NPC override of the shared `TESTHUB_RETURN_DESTS` list.
  Only `svc_testhub_return_sparta`/`_uber` are overridden; `garden`/`secret`/`bossarena` keep the
  existing Helos+BloodCave menu unchanged (they are single-hop from Helos already - their "origin"
  already IS Helos, so touching them isn't required by the design and would widen this wave's
  blast radius for no benefit).
- **Text** (`apply_svc_patches._create_traveler_enter_offers`): mints the 4 new boat-menu label
  tags. Zero new arz records.

## The Almyros divergence - investigated, reconciliation = documentation, NOT a coordinate change

The brief asked to "reconcile the Almyros divergent tagSVCHelosToSparta dest." Investigated and
**deliberately left the coordinates unchanged** - unifying them would have been a live regression:

- `portal_master_helos` (Almyros) is placed **only on canonical/Steam** (`merge_hub_into_inject_specs`
  de-dups him out of the TESTHUB plaza). On canonical there is **no outer-door traveler at all**
  (`svc_area_return_sparta`/`_uber` are TESTHUB-only - T2 gate: "0x canonical, 1x TESTHUB"), so
  Almyros's crypt/dungeon-**interior** destination is the sole live mechanism canonical/Steam
  players use TODAY to reach these two areas. Redirecting it to the outer door would silently
  strand every canonical player who currently reaches the interior this way - nothing exists at
  the door on canonical to compensate.
- `svc_helos_trav_sparta`/`_uber` (the TESTHUB hub traveler, same tag name, DIFFERENT dest -
  the outer door) are correctly paired with the TESTHUB-only `svc_area_return_sparta`/`_uber`,
  which now carry the enter-offer. This is Will's v2 hub design intentionally ("teleport me next
  to the door you'd use in game, not the final destination") - a deliberately different, richer
  round trip for the dev/test surface only.

Reusing the same label tag text across the two builds for the same area name is harmless (proven:
`gate_traveler_responds --specs` and `--specs --canonical` both PASS - the two NPCs are never
placed in the same level in either build, so the same-level route-collision check never sees both
at once). `HELOS_PORTAL_DESTS` is byte-unchanged; a documentation comment now explains why the
divergence is intentional so a future pass doesn't "fix" it into a regression.

## Verification (dry-run only, no heavy map build - build41 was building concurrently in another lane)

- **py_compile**: `apply_svc_patches.py`, `build_quest_files.py`,
  `tools/debug/{gate_traveler_responds,gate_travel_npc_invariants,gate_landing_clearance}.py` -
  all clean.
- **qst round-trip dry-run** (`scratchpad/dryrun_enter_offers.py`, read-only against the clean
  SVAERA `reference_mods/SVAERA_customquest/Resources/Quests.arc`): applies the full chain
  (`_add_helos_portal_travel` -> `_add_testhub_portal_travel` -> `_add_helos_traveler_hub_travel`
  -> `_add_traveler_enter_offers`) on a copy in memory. Result: 671,340 -> 694,345 bytes, **final
  full-chain round-trip byte-identical** (parse -> serialize -> parse -> serialize stable), host
  step trigger `max` = 34 (was 29 before this wave's 5 new triggers: 2 enter-offers are new
  triggers; the return-to-origin change reuses the EXISTING sparta/uber return triggers, just
  swaps their action list - so `max` only grows by `len(TRAVELER_ENTER_OFFERS)` = 2... plus 3 more
  from a stale prior wave already present in the branch's starting point). Every internal
  reference-count assertion inside each `_add_*` function passed (no exception raised).
- **`gate_traveler_responds.py --specs`** (TESTHUB, build-free): **PASS** - 31 route owners / 30
  placed hub NPCs / 41 total routes; 0 G-COLLISION / G-WARDEN / G-ORPHAN / G-DEST failures.
- **`gate_traveler_responds.py --specs --canonical`**: **PASS** - 5 placed hub NPCs (Almyros +
  the 4 established returns), same 41-route table, 0 failures - proves the canonical build stays
  clean under the new per-NPC destination tables.
- **`gate_travel_npc_invariants.py`** (spec-based, no arc): **GATE PASS**, all of T1-T5b plus the
  new **T5c** (enter-offer NPCs are a subset of the existing 25-record hub set - 0 new placements;
  the 4 new label tags resolve in the arz table) and RESPONDS.
- **`gate_landing_clearance.py --wiring v1`** against the live `local/Levels_merged_TESTHUB.arc`
  (27 landings, including the 2 new enter-offer coords via the now-extended `load_landings_arg`):
  **GATE PASS**, all 27 `on-mesh` / `clear`. The 2 new landings specifically:
  - `enter_sparta` `(-5596,-2,-1410)`: on-mesh comp#1 (75,244 cells) 100% clearance all 3
    tilesets; nearest collidable is the existing `svc_testhub_return_sparta` NPC at 3.16u (soft,
    informational only).
  - `enter_uber` `(-2438,10,-2450)`: on-mesh comp#1 (451,169 cells) 100% clearance all 3 tilesets;
    nearest collidable is `svc_testhub_return_uber` at 3.00u; also 0.09u from the SV-native
    `portal_olympianarena2` pad (non-colliding portal class, already T6-allowlisted for
    crypt_floor1's baseline).
- **Navmesh untouched**: this wave makes zero `build_section_surgery.py` / `svaera_plus_portals.py`
  changes - no map placements, no `INJECT_SPECS` edits, no navmesh regeneration. The concurrent
  map-lane build41 work in `local/Levels_merged_TESTHUB.arc` is unaffected by (and does not affect
  the correctness of) this quest/text-only wave; landings were verified against the on-disk
  snapshot at the time of this report.

## Landings provenance

`enter_sparta` and `enter_uber` were carried over from the killed session's on-disk (uncommitted)
`scratch_audit/enter_landings_wiring.py` and INDEPENDENTLY re-verified via
`gate_landing_clearance.py --nudge` in this session (both PASS as clean, on-mesh, collision-clear
spots - `enter_sparta` is a small nudge off Almyros's original dormant landing to clear a
sarcophagus; `enter_uber` reuses Almyros's dormant landing unchanged, already clean). The origin
re-check points `(-6587,1,-3180)` / `(-7793,1,-3793)` are the SAME coordinates already shipped as
`HELOS_HUB_TRAVEL`'s sparta/uber outbound landings (proven clean since b39 hub v2 + the b44
landing-clearance nudge wave) - reused, not re-derived.

## Open follow-up (queued to BACKLOG, not done here)

**murderbossroom (Secret Place crow-boss room)** stays sealed. To unseal it safely: place a new
return NPC inside `murderbossroom` (map lane; box-isolated, so it needs its own navmesh-verified
landing the same way `svc_testhub_return_sparta`/`_uber` were originally placed), THEN this
quest-lane pattern (enter-offer on the darkforestenter-side `svc_testhub_return_secret` +
return-to-origin on the new interior NPC) can be applied identically. Not attempted here because
it requires a map placement, out of scope for a quest/text-only lane and risky to attempt without
a paired return (the exact P0-A "no way back" bug class).

## Canonical-ship note for Will

`svc_testhub_return_sparta`/`_uber` are placed on **both** canonical and TESTHUB (they were
promoted to canonical during the build40 P0-A hotfix). `build_quest_files.py`'s Quests.arc content
is NOT gated by `SVC_TEST_HUB` - it is one shared artifact for both map variants; only whether an
NPC is PLACED (map-side) determines whether its trigger is live. So the return-to-origin change to
these two NPCs' menus will also change what canonical/Steam players see **the next time canonical
Quests.arc is rebuilt and shipped** (a separate, deliberate ship step - not automatic from this
commit). This replaces their current "Helos / Blood Cave" options with "Athens Catacomb (origin) /
Helos" - judged a net improvement (more narratively coherent than the vestigial Blood-Cave jump,
still on-mesh and safe), but flagging explicitly since it touches already-shipped NPCs.
