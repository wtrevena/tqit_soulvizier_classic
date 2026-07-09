# PLAYBOOK - How to add/change ANYTHING in Soulvizier Classic

> The complete build-and-deploy manual. Every recipe below is proven in production (build13–27).
> Read docs/HANDOFF_LIVE_STATE.md (live deploy state) + docs/BACKLOG.md (open issues) alongside this.
> This file answers "how do I add a soul / monster / map area / portal / fountain / etc."

---

## 0. ENVIRONMENT & GOLDEN RULES

- **Python:** `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`, always
  `PYTHONIOENCODING=utf-8`. (There is a `py` launcher too; use the full path in scripts.)
- **Never touch map.dat.** Steam-clean only - no DLL/exe patches ship (the 4GB LAA patch is a
  README instruction for players, not shipped).
- **Implement→vet loop is MANDATORY** for any non-trivial change: an independent implementer agent
  (Opus max) writes it, an independent vet agent (Opus max) reproduces every claim from raw bytes,
  re-run until the vet returns clean. Never ship self-vetted work. (Fable is exhausted - all Opus now.)
- **Commit + tag BEFORE every build you deploy.** Roll a backup before every deploy
  (local/*_deployed_prev.arc, local/db_backups/, local/save_backups/).
- **Five DB build invariants + map gates are fail-loud.** A build that trips one does NOT write/ship.
- **Deploy couplings:** ship together or not at all -
  - Levels.arc + Quests.arc when both changed (widow single-letter guarantee; quest neutralizations).
  - arz + Text.arc when tags changed.
  - **PORTAL born-open swap:** arz (60-byte record read) + BOTH maps (60-byte 0x14) - coupled,
    or the binary read misaligns. (See §7.)
- **TESTHUB is LOCAL-ONLY.** Never upload a `Levels_merged_TESTHUB.arc` to the Workshop. No co-op
  while it's deployed (byte-identity required for MP).

---

## 1. THE FILE MODEL (what lives where)

- `upstream/soulvizier_098i/` - pristine SV 0.98i source (Database/database.arz, Resources/*.arc,
  Quests). **The design authority / bible.** gitignored.
- `reference_mods/SVAERA_customquest/` - the SVAERA (AE port) base map we merge over. gitignored.
- `work/SoulvizierClassic/` - the STAGED mod (Database/SoulvizierClassic.arz, Resources/Levels.arc +
  Text.arc + Quests.arc + art .arc's, Maps/). This is what gets packaged. gitignored (regenerates).
- `local/` - big scratch: `Levels_merged.arc` (canonical map build), `Levels_merged_TESTHUB.arc`
  (hub variant), donor navmeshes in `editor_normalized/`, backups. gitignored.
- `tools/` - the entire build pipeline (Python). COMMITTED. The source of truth for all content.
- `scripts/` - PowerShell deploy/package/upload/bootstrap. COMMITTED.
- `docs/` - all knowledge. COMMITTED.
- **The mod is a Custom Quest total conversion:** loads via TQAE main menu → Custom Quest →
  SoulvizierClassic, with a dedicated Custom-Quest character (never load a normal char into it).

---

## 2. BUILD COMMANDS (the four artifacts)

### 2a. Database (`SoulvizierClassic.arz`) - souls, monsters, items, skills, masteries
```
py tools/build_svc_database.py \
  upstream/soulvizier_098i/Database/database.arz \
  upstream/soulvizier_0.9/Database/database.arz \
  upstream/soulvizier_041/Database/database.arz \
  work/SoulvizierClassic/Database/SoulvizierClassic.arz \
  "C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"
```
- Deterministic (same inputs → byte-identical arz; verify by md5). Prints invariant banners.
- Release drop rates (66% Hero/Quest, 25% Boss) are the DEFAULT. Testing 100% = env `SVC_TESTING_DROPS=1`.
- The actual content edits live in `tools/apply_svc_patches.py` (huge; the soul/monster/item/mastery
  wave functions) and `tools/build_svc_database.py` (wire_souls_to_monsters, the pipeline).
- **Fail-loud invariants (all must pass):** soul-leak (no non-Hero/Boss/Quest drops a soul),
  soul-augment (every augment/proc/item-skill ref resolves), supra-ref (craftable formula chains),
  tags (every referenced name/desc tag in Text.arc), spawn-eligibility (mod spawn pools spawn their
  boss with adds on N/E/L - added by the Toxeus fix).

### 2b. Text (`Text.arc`) - all display names/descriptions
```
py tools/build_text_arc.py \
  upstream/soulvizier_098i/Resources/Text_EN.arc \
  work/SoulvizierClassic/Resources/Text.arc \
  work/SoulvizierClassic/Database/uber_soul_tags.txt
```
- **The `work/SoulvizierClassic/Database/uber_soul_tags.txt` is the LIVE manifest** (written by the
  arz build). Root-level + `local/` copies are STALE DECOYS - never use them.
- After: `py tools/validate_tags.py <arz> <Text.arc> <uber_soul_tags.txt> <mod_authored_tags.txt>`
  must print `RESULT: PASS`. (The arz build already gates this internally.)

### 2c. Quests (`Quests.arc`)
```
py tools/build_quest_files.py
```
- = SVAERA's Quests.arc + the ported SV questlines (urder, widowletter, bossarena,
  open_bloodcave_portal) + neutralizations (widowletter's own letter-spawn removed since we place
  the letter statically; the two IT-cap quests - expansionportals + controlsbossdoors - with their
  post-Hades act portals removed).

### 2d. Map (`Levels.arc` / `Levels_merged.arc`)
```
py tools/gen_bc_navmeshes.py        # regenerate the 0x0b navmesh DONORS (only when navmesh changes)
py tools/svaera_plus_portals.py     # merge everything into local/Levels_merged.arc (canonical)
SVC_TEST_HUB=1 py tools/svaera_plus_portals.py   # writes local/Levels_merged_TESTHUB.arc instead
```
- `svaera_plus_portals.py` writes DIFFERENT output files by mode (canonical vs TESTHUB) - do NOT
  copy one over the other; run each mode and it writes its own file.
- Map merge applies: R09 blob swap (the SV blood-cave entrance), navmesh donor injection,
  INJECT_SPECS entity injection, the GRID_SHIFT relocation, born-open portal swaps, the respawn
  GROUPS position patch, the hub (in TESTHUB mode only).

---

## 3. DEPLOY & WORKSHOP

### Deploy locally (to the running game's CustomMaps folder)
`DEPLOY = "C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassic"`
1. Backup: `cp $DEPLOY/Resources/Levels.arc local/Levels_deployed_prev.arc` (and arz/Quests/Text as touched).
2. Copy the new artifact(s) into `$DEPLOY/…` AND into `work/SoulvizierClassic/…` (keep them in sync).
3. `cmp -s` to verify byte-identical.
4. **The game LOCKS Levels.arc while running.** If `cp` fails "Device or resource busy", the game is
   open - either wait, or arm a background poll that copies when it unlocks (until-loop, sleep 120).
5. For a TESTHUB test: deploy canonical to work/+Workshop, THEN overlay the TESTHUB map over the
   deployed Levels.arc locally (the arz/Quests/Text are the same shared coupled build).

### Push to Steam Workshop (item 3759792705, PUBLIC)
```
powershell -ExecutionPolicy Bypass -File scripts/package_workshop.ps1
powershell -ExecutionPolicy Bypass -File scripts/upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0
```
- steamcmd session is cached (no password prompt). `-Update` pushes a delta to the same item.
- **Always pass `-Visibility 0` on updates.** `0` public / `1` friends-only / `2` hidden / `3` unlisted.
  The script writes the visibility flag every run and DEFAULTS to `1`, so a bare `-Update` would flip
  the live public item to friends-only. Pass `0` to keep it public.
- **Single-wrapper layout (the 2026-07-08 fix, commit `1851203` / tag `workshop-wrapper-fix`).**
  `package_workshop.ps1` stages to `dist/workshop/content/SoulvizierClassic/{database,resources}` and
  `upload_workshop.ps1` points the vdf `contentfolder` at `dist/workshop/content` (whose only child is
  `SoulvizierClassic`). This makes the item root a SINGLE `SoulvizierClassic` mod. Shipping `database/`
  + `resources/` at the item root (the old wrapperless layout) made TQAE read them as two broken mods
  "database" and "resources" (the "two mods" bug). Do NOT revert the staging layout.
- **Built-in guards (both scripts fail loud, so you cannot ship a mistake):** the packager ABORTS if
  the packaged `Levels.arc` MD5 equals `local/Levels_merged_TESTHUB.arc` (the TESTHUB guard), asserts
  the content root has exactly one `SoulvizierClassic` child, wipes the stale wrapperless staging every
  run, and prints the packaged `Levels.arc` size + MD5. `upload_workshop.ps1` re-asserts the single
  wrapper before uploading. Still: ensure `work/` holds the CANONICAL map (not the hub) before packaging.
- steamcmd is at `C:\steamcmd\steamcmd.exe`. If it self-update-loops ("Failed to load steam.dll"),
  reinstall: back up the folder, download `https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip`,
  unzip, run `steamcmd +quit` once to bootstrap.

---

## 4. RECIPE: ADD / EDIT A SOUL

- **Souls are jewelry (ring-slot) items dropped by monsters** that grant summons/skills. Each soul =
  a 3-tier record set: `…_n.dbr` / `_e.dbr` / `_l.dbr` (normal/epic/legendary).
- **Taste hierarchy (LAW):** (a) if there's an explicit per-soul edit block in the build scripts,
  that's Will's intent - untouchable; (b) SV's ORIGINAL souls are the design bible - match their
  richness/structure; (c) more fun/powers welcome but thematically coherent.
- **Where:** `tools/apply_svc_patches.py` - soul creation uses `_create_soul()` /
  `_set_soul_fields()`. Wiring monster→soul uses `wire_souls_to_monsters` in build_svc_database.py.
- **HARD RULES (crash-proven, from CLAUDE.md):**
  - Use bare `_ensure_record` / `_create_soul` - NEVER `clone_record` for souls (brings stat values
    that corrupt saved items).
  - `{^F}` prefix on the soul name tag → pink/magenta text.
  - Icon path: `SVItems\jewelry\soul_{n,e,l}_icon.tex` (first path component = archive name).
  - Every augment/proc/item-skill path must RESOLVE (the soul-augment invariant blocks the build).
    Use VERIFIED real skill paths - see the `_SK_*` constant table (fixed in the augments-fix commit;
    e.g. Distortion Wave is `records\xpack\skills\dream\drxdistortionwave.dbr`, NOT `\skills\dream\…`).
  - All 3 tiers must exist and ladder (design uses 1×/1.4×/1.9× scaling as a baseline - but compare
    to SV originals; SV may ladder differently).
  - Name tags go in the tags dict → `uber_soul_tags.txt` → Text.arc. No generic/duplicate names.
- **If the soul GRANTS A SUMMON:** see §5 (pets). This is where B-SUMMON-1 bugs come from.

## 5. RECIPE: ADD / EDIT A PET / SUMMON (⚠️ crash-prone - read carefully)

- **Reference the WORKING pet: Lyia Leafsong** (permanent pet). Also base-game Boneash.
- **NEVER copy equipment/loot fields Monster.tpl → Pet.tpl** - even changing values of existing
  fields CRASHES the game. Only animation/skill fields are safe to copy.
- **Pet equipment** must use `_set_pet_equipment()` with HARDCODED item paths - not monster field
  copying. **If you skip this the pet spawns NAKED (B-SUMMON-1).**
- **Permanent pets:** set `spawnObjectsTimeToLive` to `[]` (empty).
- **dtype trap:** never pass an explicit dtype to `set_field()` on cloned records - INT/FLOAT
  corruption silently zeroes values (→ pet spawn failure).
- **mesh + charAnimationTable MUST be rig-compatible** - a body mesh needs its matching animation
  table, or the pet renders as a floating weapon / can't move (the Blade-Dancer bug). Derive the
  correct pairing from the SOURCE MONSTER (e.g. the Blood Cult High Priest's own mesh+anims) and
  from working exemplars.
- **The entity contract suite (HANDOFF §4b) exists to catch all of the above at build time - resume it.**

## 6. RECIPE: ADD A MONSTER / BOSS + its spawn

- Monster records are per-difficulty stat ARRAYS (`charLevel=[n,e,l]`, `characterLife=[…]`, etc.) -
  ALWAYS author all three tiers.
- **mesh + charAnimationTable consistency** (same rule as pets).
- **Spawning via a proxy (how bosses get placed):** a `Proxy` record (Class=Proxy) points at a
  `ProxyPool` record which lists `name1/2/3` (main monsters) + `nameChampion1/2/3` (adds).
  - **CHAMPION CROWD-OUT (the Toxeus bug):** `championChance` is the per-slot probability a slot is
    filled by a CHAMPION instead of a MAIN - champions REPLACE mains. Guaranteed mains =
    `spawnMax − championMax`. If that's ≤0 the boss NEVER spawns (you see only adds). Base-game boss
    pools use `championChance=0.1`. For "1 boss + N adds", set `spawnMax = 1+N`, `championMin=championMax=N`.
  - **difficultyLimitsFile** does NOT filter a too-high-level monster - it SCALES it down. To keep a
    boss at its authored level, give its proxy a no-cap limits file (clone herolimit_all, widen max).
  - The spawn-eligibility invariant now blocks builds where a mod pool can't spawn its boss.
- **Placing the proxy in the world:** inject the proxy ENTITY into a level's 0x05 via INJECT_SPECS
  (see §8). Mirror a working boss placement's byte-shape (e.g. bossfight's q_leinth_lone).
- **Boss FX/aura:** the ambient shroud is a separate FX/skill (B-TOXEUS-1 - we changed the body
  skin but not the green poison aura). Find and recolor the aura FX/skill.

## 7. RECIPE: ADD A PORTAL (cross-level teleport)

- **Two portal classes - this matters enormously:**
  - `GridEntranceDynamic` - born CLOSED + INVISIBLE, opened by a quest's `Action_OpenDynGridEntrance`.
    Fragile (the quest signal must reach every instance at runtime - it often doesn't → invisible
    portals, the build24-26 bug). **AVOID for always-open portals.**
  - `GridEntrance` (base) - **born OPEN + always visible, unconditionally, from raw map+DB bytes.**
    No quest dependency. THIS is what we use now (the born-open fix, build27).
  - `GridExitOneWay` - a landing/exit portal (the return side of a pair).
- **The 0x14 binding:** GridEntrance::Read consumes a 60-byte 0x14 (12-byte prefix
  `020000000000000001000000` + 48-byte binding = mouth_uid + exit_uid + dest_region_guid at
  offset 32). GridEntranceDynamic used 48 bytes. **So swapping class REQUIRES the 60-byte 0x14 -
  arz + map are byte-coupled, deploy together.**
- **Teleport linker** reads only: portal open-flag + connected-region-id + the paired landing found
  by exit_uid. NO 0x06 GridSystem descriptor needed (the Sparta-log "static needs 0x06" claim was
  DISPROVEN - that was a correlation with base cave mouths fronting 0x06 dungeons).
- **A portal PAIR:** an outbound `portal_olympianarena1` (GridEntrance, dest=target level GUID) +
  its landing in the target + a return `portal_olympianarena2` (GridExitOneWay) + return landing.
  mouth_uid/exit_uid must pair (entrance.exit_uid == landing.mouth_uid), globally unique, no cross-talk.
- **Where:** portal RECORD fields (Class/mesh/fx) in apply_svc_patches (`_make_portals_born_open_*`);
  portal PLACEMENT (coords + 0x14 payload) in tools/build_section_surgery.py INJECT_SPECS + the
  `_HUB_*` coord tables and the A1/A2/Sparta door specs.
- **KNOWN OPEN ISSUES (see BACKLOG):** portals render as ugly flat blue panels (need proper
  mesh/FX - B-PORTAL-1); placement can block the walkway (B-PORTAL-2); the return/dest portals
  and SV areas' OWN internal DynGridEntrance portals still need the born-open swap (B-PORTAL-3).
- **Gates:** gate_doors_hub.py (placement/collateral/crosstalk/hubidentity), entrance_landing_check,
  and the portal-openness invariant.

## 8. RECIPE: INJECT AN ENTITY (NPC / decoration / shrine / effect / proxy) into a level

- **Mechanism:** `INJECT_SPECS` in tools/build_quest_files.py (the spec dict) → consumed by
  tools/svaera_plus_portals.py step 7 → `inject_into_0x05_v11` / the v0e/v0f/v11 record builders in
  tools/build_section_surgery.py.
- **Spec shape:** `(record_path, local_x, local_y, local_z, {opts})` where opts can carry
  `rot` (rotation matrix), `flags`, `uniqueid`, `x14_payload`, `wants_0x14`.
- **Blob versions:** levels are v0e (56-byte records) / v0f (72-byte) / v11 (72-byte, 88 if flagged
  with a 16-byte UniqueId + 16-byte pad). The injector auto-detects; verify the target level's version.
- **Coords are LEVEL-LOCAL.** Convert world→local via the level's LEVELS-index corner. Cluster
  levels are GRID_SHIFTed; the corner accounts for it.
- **On-mesh:** the placement must land on the level's walkable 0x0b (parse it with navlib/the debug
  parsers). Keep clear of hostiles/friendlies as the case needs (≥25u from swarms for a fountain).
- **Byte-shape:** mirror a working native exemplar of the same class (flags/0x14 presence/rotation).
- **Use the LIVE step-7 path only** - the old `generate_default_0x14` path corrupted blobs; don't use it.

## 9. RECIPE: A RESPAWN FOUNTAIN (StrategicMovementRespawnShrine)

- The shrine is a plain 0x05 entity (`records\item\shrines\respawntempleorient01.dbr`) with
  `flags=1` + a 16-byte UniqueId + NO 0x14.
- **The respawn SYSTEM binds it via the GROUPS(0x11) section** - the `Shrine_Respawn_Orient` GROUPS
  record lists shrine UniqueIds as members. The shrine works iff BOTH the group lists its UID AND a
  0x05 entity carries that UID. (build18 shipped a flags=0/zero-UID entity → dangling → visible but
  dead.)
- **⚠️ The respawn POSITION is stored in the GROUPS member payload, NOT just the entity** - when you
  MOVE the fountain you must move BOTH (the C1 fix; `patch_respawn_group_position` in
  svaera_plus_portals). Every old-coord occurrence must be updated or the player respawns at the
  old spot. Verify against a native shrine's structure (GROUPS member pos == entity pos).

## 10. RECIPE: ADD A MAP AREA (navmesh + entrance) - the hard one

- Read docs/AREA_WIRING_RECIPE.md (the full distilled recipe from the 17-attempt wall campaign) +
  docs/SV_AREAS_CAMPAIGN_PLAN/_LOG. Summary:
  - **Navmesh:** SV levels ship `0x0a` (PathEngine) which TQAE can't read → invisible walls. Generate
    real `0x0b` (Detour dtTileCache) OFFLINE via `tools/gen_bc_navmeshes.py` (config-driven CLUSTERS
    registry) from the pristine 0x0a. Key steps: neighbor-aware rasterization, cross-tag area IDs,
    constant-Y-anchor alignment (anchored at the entrance-interfacing level), obstacle-polygon
    carving (SV rocks are baseObstacle polygons - carve them or you walk through rocks). Erode-then-
    carve + connectivity repair. Gates: verify_merged_bc_navmeshes, engine_corridor_full (reachability),
    seam_delta_check, overcoverage_check, entrance_landing_check.
  - **Entrance:** the AE host levels were re-authored so SV's original mouth records are gone. Either
    swap the whole level blob (blood cave's Random09A) or INVENT a portal (Sparta/Garden/Secret Place -
    a born-open GridEntrance pair per §7, hosted in a thematic base-game level).
- **Cut content:** an area with no navmesh source (Cold Tombs) or no possible entrance goes in
  docs/CUT_CONTENT.md (to be created) so the map contract suite doesn't flag it.

## 11. RECIPE: QUESTS (register / port / neutralize)

- **The QUESTS registry (in world01.map) loads only the first ~256 entries.** Quests past that
  boundary NEVER load for any character (the letter/widow bug). `build_ordered_quest_list` in
  svaera_plus_portals rebuilds it to exactly 256 vanilla-parity entries with mod quests INSIDE the
  window. Quest identity = md5("quests\<name>.qst"); .que filename = %08x×4 of the digest.
- **Existing characters DO auto-adopt newly-registered quests** (engine rebuilds quest state from
  live objects) - do NOT misdiagnose from the journal (controller/hidden quests never show a journal
  entry; story quests only show after their first visible step).
- **Port a quest:** extract from the SV/base upstream .qst, optionally remove specific actions
  (neutralization pattern - used for the widow letter spawn and the IT-cap act portals), via
  tools/build_quest_files.py. qst_format.py is a full RE'd reader/writer (round-trips byte-stable).
- **Deploy coupling:** if the map places a static entity the quest also spawns, remove the quest's
  spawn action AND ship both together (single-letter guarantee).

## 12. THE GATES (what protects each domain)

- **DB build invariants (in build_svc_database, fail-loud):** soul-leak, soul-augment, supra-ref,
  tags, spawn-eligibility. Validators: validate_tags.py, validate_soul_augments.py.
- **build29 additions (all fail-loud):**
  - **Castability (B-SOUL-PROC-2):** every soul-granted skill's special anim must be absent or
    universally PC-playable, and Enemy autocast controllers must carry autoTargetRadius (in-build
    invariant + validate_soul_augments + validate_summon_pets standalone re-checks).
  - **Boss-kit clone shape (B-TOXEUS-2):** a registered boss-kit clone must not add fields its
    donor lacks, must not blank a donor .dbr ref, and its refs must resolve
    (apply_svc_patches _verify_boss_kit_clone_shape).
  - **A9 render chain:** every soul-granted summon pet's mesh/texture/status icons + the summon
    skill's bar icons must resolve in the shipped arcs (tools/validate_render_chain.py,
    post-write; mod-authored pets FAIL, upstream WARN).
  - **A7 Occult/Hunting golden freeze:** the hand-tuned mastery state (records + tree + UI slots
    + Text tag definitions) must match tools/occult_hunting_golden.json; ANY drift requires
    Will's sign-off via owner_approved_overrides (tools/validate_mastery_golden.py, wired into
    the arz build [DB half] AND the Text build [full pair]).
- **Map gates (per wave):** verify_merged_bc_navmeshes, entrance_landing_check --check-merged,
  engine_corridor_full, cluster_seam_check, overcoverage_check, gate_doors_hub, portal-openness,
  blob re-parse (2282 levels to exact stream end).
- **TWO SUITES STILL TO BUILD (on hold, resumable):** entity contract suite (pets/summons/skills
  semantic completeness → commit-blocking, HANDOFF §4b, wf_87586bbf-b63) + map contract suite
  (portals/reachability/registries/UID/blob → gate every merge, task #30, wf_8da16855-efe).

## 13. RECURRING PITFALLS (learned the hard way)

- Env vars in compound bash commands may not propagate - `export` the flag on its own line
  (SVC_TEST_HUB build got this wrong once; verify output md5).
- The game locks Levels.arc while running - poll-until-unlock to deploy.
- Stale working-tree strays to NEVER commit: fix_mc_output.py, hybrid_merge.py, create_uber_souls.py,
  populate_svbake_records.py, setup_svbake_world.py, wrl_format.py, reconcile_seam_heights.py,
  docs/blood_cave_walkin_entrance_plan.md (parked/abandoned tracks). Stage files explicitly, never `git add -A`.
- The LIVE uber_soul_tags.txt is the `work/…/Database/` one; root+local copies are stale decoys.
- Determinism is your friend: rebuild twice, compare md5. A vet should reproduce the exact md5.
- Steam Cloud sync errors = quota, not corruption. Never accept cloud-over-local.
