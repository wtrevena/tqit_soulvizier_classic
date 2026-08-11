# docs/ INDEX - Soulvizier Classic

> **The doc map.** A brand-new agent reads in this order:
> **`CLAUDE.md`** (orientation + status board) → **`docs/README.md`** (this file) →
> **`docs/HANDOFF_LIVE_STATE.md`** (current deploy state) → then `docs/BACKLOG.md` (open work)
> and `docs/PLAYBOOK.md` (how-to) as needed.
>
> **Trust levels** (every entry is tagged):
> - **LIVE** - keep current; reflects the present state of the mod. Trust it, and update it as things change.
> - **RECIPE** - stable how-to / durable reverse-engineering reference. Trust the method; specific
>   numbers may drift, so verify sizes/hashes on disk before quoting.
> - **ARCHIVE** - historical (a point-in-time log, plan, RCA snapshot, or superseded doc). Useful for
>   "how did we get here / how did we fix X", but DO NOT trust for current state.
>
> "Last commit" = the file's most recent git commit date. Ground-truth artifact sizes/MD5s live in
> `HANDOFF_LIVE_STATE.md` §3 (re-verified 2026-07-08). Last updated: 2026-07-08.
> NOTE: the 2026-07-08 documentation-consolidation pass created `README.md` and `ARCHIVE_2026-07.md`
> and edited several LIVE/RECIPE docs (`CLAUDE.md`, `HANDOFF_LIVE_STATE.md`, `BACKLOG.md`,
> `PLAYBOOK.md`, `STEAM_RELEASE.md`, `MULTIPLAYER_COMPAT.md`, `SHARE_AND_PLAY.md`, `CUT_CONTENT.md`);
> those edits are UNCOMMITTED at time of writing, so a row's "Last commit" cell can predate its
> current content.

---

## LIVE - current state (read/keep these current)

| Doc | Role | Last commit | Trust |
|---|---|---|---|
| `../CLAUDE.md` | Orientation + status board; entry point (points here + to HANDOFF). | 2026-07-07 | LIVE |
| `README.md` (this) | The doc index + read order + trust legend. | new (uncommitted) | LIVE |
| `HANDOFF_LIVE_STATE.md` | The single current-state board: what/where, build27 sizes+MD5s, deploy asymmetry, standing rules. | 2026-07-08 | LIVE |
| `BACKLOG.md` | The single bug/queue board (live-test findings + standing queue + Workshop feedback triage). | 2026-07-08 | LIVE |
| `CUT_CONTENT.md` | Declared-unreachable-by-design areas (so the map contract suite does not flag them). | 2026-07-08 | LIVE |

## RECIPE - how-to manuals & release procedures

| Doc | Role | Last commit | Trust |
|---|---|---|---|
| `PLAYBOOK.md` | How to add/change ANYTHING (souls, pets, monsters, portals, entities, fountains, map areas, quests) + build/deploy/Workshop commands + gates. The current consolidated manual. | 2026-07-08 | RECIPE |
| `AREA_WIRING_RECIPE.md` | The distilled map how-to (navmesh + entrance) from the 17-attempt wall campaign. | 2026-07-06 | RECIPE |
| `MODDING_PLAYBOOK.md` | Engine internals + modding manual (map format, navmesh pipeline, failure graveyard). Predecessor to PLAYBOOK; deeper on internals. | 2026-07-07 | RECIPE |
| `CONTENT_PLAYBOOK.md` | Content-authoring how-to (souls/items/enchanting/DB pipeline). Predecessor detail. | 2026-07-05 | RECIPE |
| `STEAM_RELEASE.md` | The Steam Workshop publish procedure for Will to run (item 3759792705, PUBLIC). | 2026-07-07 (edited this pass) | RECIPE |
| `SHARE_AND_PLAY.md` | The no-Steam co-op path: build the CustomMaps zip, install, host/join MP. | 2026-07-07 | RECIPE |
| `MULTIPLAYER_COMPAT.md` | MP compatibility: the `RunEquation` spawn fix, determinism, and the byte-identity requirement. | 2026-07-07 (edited this pass) | RECIPE |

## RECIPE - durable reverse-engineering references (engine behavior)

| Doc | Role | Last commit | Trust |
|---|---|---|---|
| `DYNGRID_GATE_RCA.md` | What gates GridEntranceDynamic portal visibility/openness - full RCA + the born-open fix. | 2026-07-07 | RECIPE |
| `CROSS_LEVEL_STITCH_RE.md` | How TQAE stitches adjacent levels for seamless walking (the tile-lattice alignment rule). | 2026-07-05 | RECIPE |
| `NAVMESH_COVERAGE_FIX.md` | The xPTS → BC_initialpathway wall: index-footprint gap root cause + fix. | 2026-07-05 | RECIPE |
| `NAVMESH_OVERCOVERAGE_RCA.md` | Walk-through-rocks RCA (obstacle-polygon carving). | 2026-07-06 | RECIPE |
| `QUEST_STATE_INJECT.md` | Quest save-state format spec, the ~256-entry load window, and why registration injection is a no-op. | 2026-07-07 | RECIPE |
| `BLOODCAVE_QUESTS_RCA.md` | Widow-letter no-show + the exploding-wall secret area RCA. | 2026-07-06 | RECIPE |
| `CAVE_ENTRY_CHAIN_TRACE.md` | Complete surface→cave entry chain trace (byte + Engine.dll disassembly). | 2026-07-05 | RECIPE |

## AUDITS & DESIGN (reference; point-in-time but load-bearing)

| Doc | Role | Last commit | Trust |
|---|---|---|---|
| `MASTERY_AUDIT.md` | All 10 masteries + 2 DLC audit (0 port defects; protected Occult/Hunting trees). | 2026-07-07 | RECIPE |
| `UBER_WEAPONS_AUDIT.md` | DRX "supra" ultra-craftable set audit (Blood Whisper + Paragon verified). | 2026-07-07 | RECIPE |
| `CHEST_DROP_MATRIX.md` | Will's drop-breadth reference: what every mod chest can and cannot pay, per weapon class / armour slot / craft component, parsed from the shipped arz `16994072`. | 2026-08-10 | RECIPE |
| `IT_ENDPOINT_AUDIT.md` | Does the playable arc end at Immortal Throne? (the act-portal cap). | 2026-07-07 | RECIPE |
| `SOULS_COMPLETENESS_AUDIT.md` | Souls roster completeness audit + tag list. | 2026-07-06 | RECIPE |
| `BOSS_SOULS_DESIGN.md` | Boss-souls design doc (the ~60-soul roster, per-tier values). | 2026-07-06 | RECIPE |
| `BLOOD_TOXEUS_DESIGN.md` | Superboss/soul/set design spec (Hemorrheus → Toxeus the Murderer). NOTE: parked file with other-lane uncommitted edits - do not modify. | 2026-07-07 | RECIPE |
| `DROPPED_CONTENT_AUDIT.md` | SV-only entities lost by the merge (drives the dropped-visuals restoration). | 2026-07-05 | RECIPE |
| `SV_AREAS_AUDIT.md` | The remaining non-blood-cave SV levels audit. | 2026-07-05 | RECIPE |
| `skill_comparison.md` | Soulvizier skill archaeology v0.4.1 → v0.9 → v0.98i (design data). | 2026-03-01 | RECIPE |
| `upstream_inventory.md` | Pristine upstream SV 0.98i inventory. | 2026-03-01 | RECIPE |
| `reference_mods.md` | The reference mods used (SVAERA base, etc.). | 2026-03-01 | RECIPE |

## ARCHIVE - logs, plans, and superseded snapshots (do NOT trust for current state)

| Doc | Role | Last commit | Trust |
|---|---|---|---|
| `ARCHIVE_2026-07.md` | The consolidation archive: the prior HANDOFF verbatim (workflow IDs, task queue, entity-contract-suite spec, revert recipe). | new (uncommitted) | ARCHIVE |
| `DOORS_HUB_LOG.md` | Doors + test-hub + build24/25 implementer log. Parked file (other-lane edits) - do not modify. | 2026-07-07 | ARCHIVE |
| `SPARTA_CORRECTIONS_LOG.md` | Sparta Crypt L2 invented entrance + build23 screenshot-corrections log. | 2026-07-07 | ARCHIVE |
| `ENTRANCES_POLISH_LOG.md` | Entrances + blood-cave polish implementer log. | 2026-07-07 | ARCHIVE |
| `SV_AREAS_CAMPAIGN_LOG.md` | SV-areas navmesh generalization campaign log. | 2026-07-07 | ARCHIVE |
| `SV_AREAS_CAMPAIGN_PLAN.md` | SV-areas campaign plan (partly executed/superseded). | 2026-07-06 | ARCHIVE |
| `WALL_ATTEMPT_LEDGER.md` | The complete invisible-wall attempt ledger (17 attempts). | 2026-07-06 | ARCHIVE |
| `WALL_INVESTIGATION_STATE.md` | Invisible-wall investigation snapshot (2026-07-05 night). | 2026-07-05 | ARCHIVE |
| `CAVE_GRAFT_COMPLETENESS_AUDIT.md` | Cave-graft completeness audit (adversarial). | 2026-07-05 | ARCHIVE |
| `CAVE_INTERIOR_PORTALS.md` | Interior cave-mouth portals track. | 2026-07-05 | ARCHIVE |
| `CAVE_LEVEL_MERGE.md` | Blood-cave chain merge feasibility verdict. | 2026-07-05 | ARCHIVE |
| `LETTER_SPAWN_DIAGNOSIS.md` | Widow-letter no-show save-state diagnosis (superseded by the QUESTS load-window fix). | 2026-07-07 | ARCHIVE |
| `blood_cave_walkin_entrance_plan.md` | Walk-in entrance plan. Parked file - do not modify. | 2026-07-05 | ARCHIVE |
| `crash_analysis_report.md` | Early crash-log analysis (source of the `RunEquation` MP finding). | 2026-03-03 | ARCHIVE |
| `CHANGELOG.md` | Old changelog (stale). | 2026-03-01 | ARCHIVE |
| `system_check.md` | Early system-check report (stale). | 2026-03-01 | ARCHIVE |
| `uber_souls_report.md` | Early uber-soul report (superseded by SOULS_COMPLETENESS_AUDIT). | 2026-03-01 | ARCHIVE |
| `uber_soul_tags.txt` | Old uber-soul tag list. STALE DECOY - the live manifest is `work/SoulvizierClassic/Database/uber_soul_tags.txt`. | 2026-03-01 | ARCHIVE |

> Root-level `../README.md` and `../SOUL_AUDIT.md` are early (Feb-Mar 2026) and are ARCHIVE-grade -
> superseded by the docs above. The user's cross-session memory board
> (`tq-soulvizier-2026-07-resume.md`, outside this repo) is the other live index.
