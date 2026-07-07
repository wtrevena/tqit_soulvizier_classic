# QUEST SAVE-STATE: format spec, character copy, and why registration injection is a NO-OP

> Companion to `docs/LETTER_SPAWN_DIAGNOSIS.md` (updated the same night with the
> corrected verdict). Produced 2026-07-06 during the "surgical quest registration
> injection" task. Tool: `tools/quest_state_inject.py`. House style: no em dashes.
>
> HEADLINE: the per-character quest-save format is now fully decoded (identity
> hash cracked, Quest.myw round-trips byte-exact), a sandbox copy of Will's
> character exists (`_ToxeuQ`, ready to select in-game), BUT the investigation
> proved the widow-letter failure is NOT a save-state problem at all. The four
> July SV quests are never LOADED by the engine (world-side registration-slot
> defect in the map build). Save-side injection therefore cannot help, and,
> better, is not needed: the engine auto-adopts newly loadable quests for
> EXISTING characters. Will keeps his 24h character; no fresh start, no copy
> needed once the map is fixed.

---

## 1. FORMAT FINDINGS (all reverse-engineered + verified this session)

### 1.1 Quest identity = MD5 of the registration path

- Input string: `quests\<basename>.qst`, lowercase, backslash separator, UTF-8.
  (For quests the map registers under both `Quests/<name>` and
  `XPack/Quests/<name>`, the engine instantiates the `Quests/` form; verified
  via the doubled "grieving widow" registration, where only the `quests\`-form
  hash exists in the save.)
- The 16-byte MD5 digest is stored as four little-endian u32 `md5Chunk`
  values, and the per-quest state file is named
  `"%08x%08x%08x%08x.que" % (chunk0..chunk3)` (that format string is verbatim
  in Game.dll). Net effect: the filename is the hexdigest with each 4-byte
  group reversed.
- Engine internals (disassembled, TQAE `Engine.dll`): `GAME::Name` IS a 16-byte
  MD5 holder; `Name::Create(const char*)` = strlen + one-shot standard MD5
  (textbook IV `67452301/efcdab89/98badcfe/10325476`, standard padding), no
  case-folding inside; the path is normalized before Name creation.
- Validation: this scheme explains 252 of the 255 `.que` files of Will's
  `_Toxeus` character via the deployed map's QUESTS section (the 3 outliers
  date to 2026-03-10 and match a since-renamed March build's registrations),
  and reproduces identically across 5 custom-quest characters and the vanilla
  `SaveData/Main` characters (no per-character salt, no map/mod context in the
  hash).

Identities for the four ported SV quests (computed, verified-absent from every
save on the machine):

| quest | .que filename it would use |
|---|---|
| `quests\widowletter.qst` | `72453084ddabc2a1dac12333fa5fba2f.que` |
| `quests\urder.qst` | `a5b7f281bd30c323a93260683eb07ae4.que` |
| `quests\bossarena.qst` | `a732380c96f429a350479d6169edad5d.que` |
| `quests\open_bloodcave_portal.qst` | `cfc50d3bdc33fd14108d9ff292291daa.que` |

### 1.2 Quest.myw = armed-trigger scheduler (+ pending-rewards tail)

Layout (byte-exact round-trip verified against Will's live 18,570-byte file):

```
begin_block(0xB01DFACE)
  numberOfTriggers: u32 N
  N x {
    questName            (no inline value; followed by the hashed-name block)
    md5ChunkCount: u32 4
    4 x md5Chunk: u32    (the quest identity, LE dwords of the MD5)
    stepIdx: u32
    triggerIdx: u32
    target:              (usually u32 0; sometimes a u32 entity id, e.g. 42592;
                          occasionally a hashed-name block like questName)
  }
end_block(0xDEADC0DE)
begin_block                      <- 530-byte tail in Will's file
  numRewards: u32 M              (pending journal-reward entries, each keyed by
  ...                             a hashed questName + region/locationTag data)
end_block
```

Semantics: entries are ARMED trigger instances (e.g. the OnLevelLoad spawn
quests `xsq03_beaconquest` / `xsq12_rescueleader` each persist an armed
`(step 0, trigger 0)`; linear quests show armed runs like steps 2..10). It is
NOT the tracked-quest registry: quests can be live with zero entries here
(x2Quest_AesirBrawlYlvaController has a `.que` but no Quest.myw entry).

### 1.3 .que files = per-quest runtime state, created LAZILY

- Content: `crcFile` (a checksum stamp of the quest definition; not plain
  crc32/adler of the file bytes) + nested blocks mirroring the quest's
  step/trigger/condition/action tree with `active`, `hasFired`,
  `conditionCount`/`isSatisfied`, `actionCount`/`isPendingFire`, and condition
  `comments` strings (which embed the referenced `.dbr`/`.qst` paths; that is
  how the 255 files were identified).
- A `.que` appears only when a quest's state first differs from default, and
  is rewritten on save whenever the state is dirty (84 of the 255 were
  rewritten during tonight's session; all 84 are "volatile" quests such as
  controllers, teleporters and OnLevelLoad scripted scenes).
- ABSENCE of a `.que` = virgin state, NOT "quest not tracked". Therefore
  registering a quest for a character requires NO `.que` synthesis ever.

### 1.4 QuestToken.myw

Flat token list (plain-text names + fileReferenceCount), trivially parseable.
Will's character holds 17 tokens, none in the `SQWL_*` family.

### 1.5 Where the rest of "his exact state" lives (work item 2)

| state | file | notes |
|---|---|---|
| items, level 37, skills, money | `Player.chr` | tag-stream, `myPlayerName` = length-prefixed UTF-16 |
| waypoint (teleport) unlocks | `Player.chr` `versionCheckTeleportInfo` + `teleportUIDsSize` + N x `teleportUID` (16-byte UIDs) | 17 unlocked |
| respawn points | `Player.chr` `versionCheckRespawnInfo` + respawnUID list | |
| minimap markers | `Player.chr` `versionCheckMovementInfo` + markerUID list | |
| current spawn position on the map | `Levels_world_world01.map/Normal/map.dat` (`mapPath`, `modName`, `spawnCoords` 3x3 basis + position) | per map+difficulty |
| fog of war | `Levels_world_world01.map/Normal/fowData.arz` (ARC of per-level `.fow` bitmaps, plain names) | per map+difficulty |
| quest state | `Quest.myw`, `QuestToken.myw`, `*.que` | as above |

A WHOLE-FOLDER copy of `_Toxeus` therefore preserves everything: spawn point,
waypoints, fog, inventory, level, skills, quest progress. Nothing is keyed to
the folder name or character name except the display name itself.

---

## 2. THE DECISIVE FINDING: the save is not the gate; the map's quest list is

The injection premise ("the four quests are not in the character's tracked
set, so add them") was tested and DISPROVEN:

1. **The engine auto-adopts quests for existing characters.** Proof:
   `x2Quest_AesirBrawlYlvaController` (a Ragnarok controller with conditions
   `OnLevelLoad + OwnsToken + OwnsToken`) persisted `isSatisfied=1` on its
   OnLevelLoad condition in tonight's session on Will's 4.5-month-old
   character. `Condition_OnLevelLoad` satisfies on ANY level load, revisited
   or not, and partial condition state is persisted immediately. There is no
   per-character registration freeze. (This also retires the RCA's
   "OnLevelLoad may not re-fire on revisit" concern.)
2. **Widowletter's step-0 conditions were satisfiable tonight** (OnLevelLoad +
   NOT OwnsToken(SQWL_PickedUpLetter), and he owns no SQWL token). Had the
   quest been loaded, it would have fired, spawned the letter, and written
   state. Zero state was written on any of the 3 sessions since the quest
   shipped (verified by NTFS creation times: no new `.que` since 2026-03-10).
3. **The untracked set is EXACTLY the appended registration block.** The
   deployed map's QUESTS section = SVAERA's original 254 entries (byte-
   identical, same order) + 53 appended entries (indices 254..306: the four SV
   quests in both `Quests/` and `XPack/Quests/` forms, ~45 stale
   SV-upstream `XPack/Quests/*` duplicates, and 6 dead entries whose files do
   not exist anywhere: `imhotepfix`, `typhonportal`, `uberdungeon_entrance/
   return`, `bloodcave_entrance/return`). Every quest at index <= 253 behaves
   normally (e.g. `Quests/sv_commonmechanics.qst` at index 96, stored in the
   SAME mod Quests.arc the same way, was loaded and rewritten tonight). NOT
   ONE entry at index >= 254 has EVER produced any state for ANY character.
4. **Reference counts:** vanilla TQAE world01.map registers EXACTLY 256
   quests; SVAERA registers 254 (vanilla minus the two whose files SVAERA
   dropped: imhotepfix, typhonportal). The engine's `World`/`WorldFile` quest
   lists are plain std::vectors (no cap in the accessors; loader loop iterates
   GetNumQuestFiles() and does not abort on a failed entry), so the exact
   truncation mechanism was not pinned down statically. The empirical fact
   stands regardless: **entries appended past the original 254 never load;
   widowletter sits at index 256.**

Consequence for injection: adding Quest.myw armed-trigger entries (or synthetic
`.que` files) for a quest the engine never instantiates does nothing; the
engine rebuilds Quest.myw from live quest objects on every save, so foreign
entries are simply dropped. Injection is a NO-OP for this bug. (The tool still
implements it, correctly and round-trip-safe, for completeness/testing.)

## 3. THE ACTUAL FIX (map-side, owned by the map-tooling workflow)

Rebuild the QUESTS section so the four SV quests sit WITHIN the load window:

- Insert `Quests/open_bloodcave_portal.qst`, `Quests/urder.qst`,
  `Quests/widowletter.qst`, `Quests/bossarena.qst` INSIDE the first 254
  entries (safest interpretation of the boundary; e.g. right after
  `Quests/sv_commonmechanics.qst` at index 96).
- Drop the 53 appended entries: the `XPack/Quests/*` duplicates are dead
  weight, the 6 dead entries reference files that do not exist (they at
  minimum spam the `QuestRepository: Invalid Quest File` path), and the four
  SV quests get re-inserted lower as above.
- To stay within budget, 4 existing entries must yield their slots. Candidates
  with zero player impact: re-test whether the boundary is actually 256
  (vanilla's count) rather than 254; if 256, only cut the appended junk and
  reinsert the four so the list ends at <= 256. If 254, cut 4 provably
  unreachable entries (to be chosen by the map workflow with a reachability
  pass).
- After the fix, NO save-side work is needed: Will's existing `_Toxeus`
  adopts `widowletter` automatically on next load; step 0 fires (OnLevelLoad +
  no SQWL token) and the letter spawns at the on-mesh letterdrop marker in
  `drxFirstxistion_connection`. His items/level/skills/position/waypoints are
  untouched because his save is untouched.
- In-game verification order: letter spawn (blood cave, world (5691.5, 1.0,
  3308.6)) -> pickup grants `SQWL_PickedUpLetter` -> journal entry appears ->
  (with WAVE-E entities restored) chest + widow + buff chain.

## 4. THE SANDBOX COPY (delivered, ready to select in-game)

`SaveData/User/_ToxeuQ` exists now: a byte-verified full copy of `_Toxeus`
(271 files; only the two `Player.chr` name fields differ, same length:
`Toxeus` -> `ToxeuQ`, UTF-16, no structural change). Same items, level 37
Warrior, skills, spawn position, waypoints, fog of war, quest progress.
It shows up in the Custom Quest character list as `ToxeuQ`.

- REFRESH before testing (the copy captures the LAST SAVED state; if Will
  plays `_Toxeus` again, re-run):
  `python tools/quest_state_inject.py --copy`
  (idempotent: deletes and re-creates `_ToxeuQ` from the current `_Toxeus`,
  re-backs-up if the source changed, and byte-verifies the original after.)
- Optional (ineffective in-game until the map fix, see section 2):
  `python tools/quest_state_inject.py --copy --inject widowletter urder bossarena open_bloodcave_portal`

## 5. BACKUPS + ROLLBACK

- Full zips of the untouched original: `local/save_backups/_Toxeus_2026-07-06.zip`
  (+ `_1` refresh) with SHA-256 manifests alongside.
- Rollback = delete `_ToxeuQ` (the original was never written) or unzip the
  backup over an empty `SaveData/User/_Toxeus` if catastrophe strikes.
- The tool hard-fails if the source tree hash changes during any run and
  refuses same-folder operations.

## 6. OPEN ITEMS

1. The exact truncation mechanism (254 vs 256 boundary; where the loader
   stops) was not pinned statically. Cheapest decisive experiment: a build
   with widowletter inserted at a LOW index; if the letter then spawns for a
   fresh save-dir character AND for `_ToxeuQ`, the boundary story is confirmed
   in one shot.
2. The 3 unexplained `.que` files (created 2026-03-10 20:50, the corruption-
   event minute) match no current registration; almost certainly a March-era
   build's renamed registrations or external-tool artifacts. No action.
3. `docs/LETTER_SPAWN_DIAGNOSIS.md` section "WHY THIS HAPPENS" was corrected
   this session; the earlier per-character-freeze mechanism is retired.
