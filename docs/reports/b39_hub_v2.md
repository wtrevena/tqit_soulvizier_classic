# b39 - HELOS HUB v2 + ALL-BOSS-PORTALS (DEV/TESTHUB-only)

Branch `feat/b39-hub-v2` off `da918c5` (build38a-dev). DEV/TESTHUB-only content (SVC_TEST_HUB=1);
NEVER ships to Steam. NO heavy build run (all edits verified build-free). Canonical map/arz stay
byte-identical (the hub records are TESTHUB-only, proven by the gate).

## Will's two orders (2026-07-13)
- (i) The existing 11 Helos travelers teleported him straight to the destination interior / onto the
  boss. Instead, drop him **next to the in-game NPC/door he would use in game** to reach that area,
  so he can test those travel guys AND learn the geography.
- (ii) Add travelers to **all other new fixed-place bosses**, dropping him at the **area entrance amid
  regular mobs (not the boss horde)** so he can walk up, inspect, aggro.

Both reduce to one principle: **land at the natural in-game APPROACH POINT, amid regular mobs, never
on the boss.** Every landing was surveyed on-mesh in the main walkable component against the built
TESTHUB map (`tools/debug/survey_hub_v2_landings.py` + `survey_uberboss_spots.py`, vs
`local/Levels_merged_TESTHUB.arc` 841c56cd).

## Order (i): the 11 existing travelers
**KEPT (already at their natural approach, no boss to move off):** Garden of Merchants (merchant hub
+ rift-shrine), The Secret Place (forest-cluster entry), The Boss Arena (forecourt 90u off the arena
volume).

**RETARGETED (8)** - landing WORLD coord (boat-dialog) | rationale:
| Traveler | New landing (world) | Approach point |
|---|---|---|
| Sparta | (-6588, 1, -3180) | the Sparta-Crypt DOOR: deepest Athens catacomb (catacube02_floorlast, by stairs-down), amid beastmen |
| Uber (renamed "The Uber Dungeon") | (-7793, 1, -3793) | the Knossos->Uber DOOR: Minotaur's Labyrinth secret door (maze03) |
| Warband | (5699, 1, 3315) | blood-cave chamber at the regular demon pack (~35u off the Enslaver) |
| Dorus | (330, 1, -8380) | Medea tomb entrance (cryptentrance), ~82u off the boss |
| Tantalus | (-346, -12, -10131) | Styx swamp stairs entrance, ~36u off the boss |
| Charon | (-480, -12, -9591) | Styx Hades-city settlement (boatman + storyteller + rift), then walk E to the boss |
| Mnemophage | (169, -10, -11418) | Mnemosyne cave stairs-up entrance, ~20u off the boss ring |
| Ephialtes | (-1756, 3, -13198) | Dread Halls stairs-up entrance, ~130u off the deep-SW boss vault |

The Uber traveler NAME was corrected "The Obsidian Halls" -> "The Uber Dungeon" (crypt_floor1's true
identity; the boat-menu label was already "The Uber Dungeon"). crypt_floor1 and SpartaCryptLevel2
have NO placed boss (only regular mobs), so landing at the door teaches geography with nothing lost.
The 6 IT/warband returns were MOVED to sit a few u off each new landing; Uber + Sparta gained their
OWN distinct return records (they no longer land where the shared svc_testhub_return sits).

## Order (ii): 3 NEW travelers (map-placed bosses not covered by the 11)
| Traveler | Landing (world) | Boss + placement |
|---|---|---|
| Toxeus the Devourer | (5345, 1, 3010) | um_bloodtoxeus_99 (Devourer of Blood), egg_blooddragon_pack @ drxbc2 local (13,136); land in the main chamber ~92u off, walk NW |
| Vashkarr the Eldest | (-227, 1, 146) | q_vashkarr_lone @ random05a (Chang'an cave) local (24,32); land N end ~28u off |
| The Obsidian Halls | (-1827, -74, -462) | tombobs02 stairs-down entrance; covers the 4 roulette wardens (Sarkoth/Gorrahk/Voranthys/Ilsevar) + the Broodmother nest |

Each has a distinct return NPC a few u off its landing. This covers the brief's "Devourer/Hemorrheus
superboss", "wardens 5-9" (roulette 5-8 via Obsidian; Vashkarr = warden 9), and the broodmother.

## PENDING map placement (DB-only; cannot portal yet - documented, not fabricated)
polis_vault cage Guardian; Helepolis (Diadochi); Menoetes + 3 generals; Neferkha (Egypt). These b37
bosses exist in the DB but have no map placement in the current canonical/TESTHUB map, so no landing
spot exists. They get travelers once the b37 map pass places them.

## Wiring (proven 3-file TESTHUB pattern; ALL SVC_TEST_HUB-gated)
- **arz** `apply_svc_patches.py`: +3 outbound + 5 return records (distinct, warden-law single
  placement) cloned from the Knossos boatman; +6 Text tags; Uber name renamed. 14 outbound + 11
  returns; records INERT until the TESTHUB map places them.
- **quests** `build_quest_files.py`: `HELOS_HUB_TRAVEL` 17 -> 25 boat-dialog triggers (8 landings
  retargeted, 3 outbound + 5 returns added). Counter-based invariants auto-scale.
- **map** `build_section_surgery.py`: `HELOS_HUB_PLAZA_SPECS` 11 -> 14 (3 new Helos plaza spots,
  Z=186.2 row); `HELOS_HUB_RETURN_SPECS` 6 -> 11 (6 moved + 5 new). New host keys maze03 /
  catacube02_floorlast / drxbc2 are TESTHUB-only (canonical INJECT_SPECS untouched). drxbc2 flows
  through the normal (non-swap) fold.
- **gate** `gate_travel_npc_invariants.py`: hub-record count 17 -> 25.

## Gates (build-free, all PASS)
- `py_compile` all changed files: OK.
- `gate_travel_npc_invariants.py` (spec + canonical arc): T1 0 walk-throughs; T2 25 records,
  canonical=0 each / TESTHUB=1 each (WARDEN LAW); T3 masters retired; T4 Almyros x1 +
  svc_testhub_return x4 (P0 areas); T5 map==quests==arz (25 records) + 15 label tags resolve; T6
  canonical .arc byte-pure (authored walk-throughs=0, hub records 0 each). GATE PASS.
- Quest patch round-trip: full chain (_add_helos_portal_travel -> _add_testhub_portal_travel ->
  _add_helos_traveler_hub_travel) on the SVAERA base sv_commonmechanics.qst applies + round-trips +
  all 25 records present + Counter invariants pass, no exception.
- Map spec check: 25 distinct hub records; 0 in canonical; exactly 1 each in the TESTHUB fold.
- Landing survey: every outbound landing + return placement on-mesh in the main component (24 of 25
  at clr 100%; the devourer return is an accepted CHECK at 75% clr, still on-mesh comp#1).

## Deploy coupling (main session owns the build/deploy; TQ must be closed for the DEV map copy)
This is a coupled arz + Text + Quests + TESTHUB-Levels rebuild (the records ride the arz, the tags
ride Text, the triggers ride Quests, the placements ride the TESTHUB map; QUESTS 256-window parity
preserved). Rebuild all four with SVC_TEST_HUB=1, then run gate_travel_npc_invariants against BOTH
built arcs (T6 TESTHUB will then assert 1 each). Steam/canonical UNTOUCHED (TESTHUB is local-only).

## Files changed / commits (branch feat/b39-hub-v2)
- tools/debug/survey_hub_v2_landings.py (new recon tool) - `6c83a47`
- tools/apply_svc_patches.py (arz records + tags + rename) - `1e771c2` (+ call-site count fix in the gate/docs commit)
- tools/build_quest_files.py (quests: 25 triggers) - `0cc9fc9`
- tools/build_section_surgery.py (map: 14 plaza + 11 returns) - `cf5a0e4`
- tools/debug/gate_travel_npc_invariants.py (17->25) + docs/WILL_TEST_GUIDE.md (v2) + this report - gate/docs commit
