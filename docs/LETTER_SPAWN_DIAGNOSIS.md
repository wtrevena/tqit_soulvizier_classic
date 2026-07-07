# Widow Letter no-show - SAVE-STATE DIAGNOSIS (Will's character `_Toxeus`)

> 🚨 2026-07-06 LATE-NIGHT CORRECTION (read this first): the same-night follow-up
> investigation (`docs/QUEST_STATE_INJECT.md`) DISPROVED the per-character
> adoption-freeze mechanism this doc concludes with. The OBSERVATIONS below
> (quest untracked for `_Toxeus`, zero SQWL tokens, the timeline) all stand, but
> the CAUSE is WORLD-side, not save-side: the deployed map's QUESTS section =
> SVAERA's original 254 entries + 53 appended by our build, and the engine never
> loads ANY appended entry (`widowletter` sits at index 256; vanilla TQAE
> registers exactly 256; none of the 53 has ever produced state for ANY
> character). The engine DOES auto-adopt newly loadable quests on existing
> characters (proven: `x2Quest_AesirBrawlYlvaController` wrote fresh OnLevelLoad
> state on Will's 4.5-month-old character tonight), and `Condition_OnLevelLoad`
> DOES satisfy on revisited levels. Therefore:
> - FIX A below (fresh character) is WRONG and would NOT have produced the
>   letter either; do not act on it;
> - the real fix is map-side: rebuild the QUESTS registration list so the four
>   SV quests sit inside the engine's load window (see QUEST_STATE_INJECT.md
>   section 3). Once that lands, Will's EXISTING character gets the letter
>   automatically: no fresh start, no save surgery, no copy needed.
>
> Original (superseded in mechanism, accurate in observations) analysis follows.

> Read-only forensic diagnosis of WHY the widow-letter scroll does not appear in-game on
> the CURRENT deployed build, done by decoding Will's live per-character quest-save state.
> Companion to `docs/BLOODCAVE_QUESTS_RCA.md` (which proved the letter's DATA is complete
> and on-mesh, and narrowed the failure to "the runtime does not fire the spawn"). This
> doc identifies that runtime reason from the save files. Produced 2026-07-06. No em dashes.
>
> SCOPE NOTE: everything below is a parse of Will's actual save under
> `SaveData/User/_Toxeus/...` (READ ONLY, nothing written there) plus the deployed mod
> archives in `work/SoulvizierClassic/Resources/`. No game files were modified.

---

## VERDICT (one line)

**HYPOTHESIS 1 IS CONFIRMED - TRUE.** `widowletter.qst` was added to the mod's `Quests.arc`
on 2026-07-04, but Will's Custom-Quest character `_Toxeus` was created on 2026-02-21. The
whole widow-letter quest (and every other later-ported SV area quest: `urder`, `bossarena`,
`open_bloodcave_portal`) is **NOT TRACKED for this character at all**. Its step-0 letter
spawn, its `SQWL_*` tokens, the chest, the widow dialog, and the buff reward are ALL inert
for `_Toxeus`, and will stay inert no matter how many times he re-enters the blood cave.
They work only on a character created (or freshly re-initialized) AFTER the quest was added.

The letter's data being complete and on-mesh (per the RCA) is real but moot: the runtime
never runs `widowletter.qst`'s triggers for this character, so the `OnLevelLoad` spawn is
never evaluated.

---

## EVIDENCE

### E1 - The character's tracked-quest state contains ZERO Soulvizier area quests

Will's live per-character quest state lives in
`SaveData/User/_Toxeus/Levels_world_world01.map/Normal/` (the `_Toxeus` char is the one he
played tonight: `Player.chr` mtime 2026-07-06 20:38, level 37 Warrior, Custom-Quest map
`Levels_world_world01.map`). The engine stores quest state as:

- `Quest.myw` - the master list of quests the character is TRACKING (each entry = a 16-byte
  quest-identity MD5 stored as 4 `md5Chunk` u32s + `stepIdx`/`triggerIdx` progress).
- `QuestToken.myw` - the flat list of trigger TOKENS the character owns.
- 255 `*.que` files - per-quest runtime state (per-condition `isSatisfied`, per-trigger
  `hasFired`, `active`, a per-quest `crcFile` stamp of the `.qst` definition). Each `.que`
  file embeds the quest's resource path (e.g. `Triggers\Quests\...\SS_PreTegea_ArachnosCave.dbr`,
  `XPack/quests/xsq05_acolytespotion.qst`) inside its condition `comments`, so the tracked
  quests are directly identifiable.

Decoding all of it (parsers + full inventory in the session scratchpad):

- **`Quest.myw`: 124 trigger entries -> 62 distinct tracked quests. Extracting the embedded
  resource path from all 255 `.que` files yields 124 distinct quest identities. EVERY ONE is
  a stock base-game or Immortal-Throne (XPack) quest** - Egypt/Greece/Orient Journals, Main
  Quests, `xsq*`/`xq*`/scripted-scene quests. **NOT ONE Soulvizier custom quest is present.**
- Direct content search of all 255 `.que` files for the widow-letter questline and its
  siblings returned **0 hits** for every one of: `widowletter`, `widow_ling`, `SQWL`,
  `letterdrop`, `finalletter`, `foundzhidan`, `treasurechest`, `urder`, `bossarena`,
  `open_bloodcave`, `uberdungeon`, `drxmap`, `drxBC`. (The one apparent "widow" match is
  `Quests\Greece Journal - The Grieving Widow.qst` - the UNRELATED base-game grieving-widow
  side quest, which is registered because it is in the stock quest set.)
- **`QuestToken.myw`: 17 tokens, NONE in the `SQWL_*` family.** No `SQWL_PickedUpLetter`, no
  `SQWL_OpenedChest`, no `SQWL_TalkedToWidow`. So `widowletter.qst` has never bestowed a
  token on this character, consistent with it never having been tracked.

### E2 - The tokens the character DOES own prove the "added-later" cutoff exactly

`QuestToken.myw` DOES contain Soulvizier tokens: `SV_Forge_Free_Unlocked`,
`SV_Unique_Forge_Unlocked`, `SV_Unique_Forge_a0{1..6}_Locked`,
`SV_X2MQ07_MimerRewardFix_Previous`, plus base-game side-quest tokens (`JO3 - *`, `JO04 - *`,
`BossChest_Barmanu`). Tracing where those SV tokens are bestowed in the deployed `Quests.arc`:

| token | bestowing quest | in mod since |
|-------|-----------------|--------------|
| `SV_Forge_Free_Unlocked`, `SV_Unique_Forge_Unlocked` | `sv_commonmechanics.qst` | SVAERA base (present at char creation) |
| `SV_X2MQ07_MimerRewardFix_Previous` | `soundtyphonlaughingdistance.qst` | SVAERA base (present at char creation) |
| **`SQWL_PickedUpLetter`** | **`widowletter.qst`** | **added 2026-07-04 (NOT present at char creation)** |

So the SV quests that shipped in the SVAERA base `Quests.arc` (present since the character
was created) ARE tracked and DO grant their tokens; the SV quests ported in July are NOT.
The dividing line is exactly "was this quest in the mod's `Quests.arc` when the character
was created." This is the signature of hypothesis 1.

### E3 - The timeline: character predates the quest by ~4.5 months

- Oldest `.que` file mtime for `_Toxeus`: **2026-02-21 13:57** (the base-game quest batch
  written when the character was created and first played). Character is level 37, played
  across many sessions Feb -> Jul (mtimes span 2026-02-21 to 2026-07-06).
- `widowletter.qst` first entered the mod's `Quests.arc` in git commit `1175fc8`
  ("Content P0 fixes + SV area quest integration"), dated **2026-07-04 12:33**. The deployed
  `Quests.arc` carrying it is dated 2026-07-04 23:36 and is byte-identical in the
  `work/` staging copy and the live `CustomMaps/SoulvizierClassic/Resources/` deploy.
- The map (`Levels.arc`) that registers `widowletter.qst` in its QUESTS section is deployed
  (2026-07-06 19:38, identical work vs CustomMaps). Confirmed: the deployed map's QUESTS
  section DOES list `Quests/widowletter.qst` and `XPack/Quests/widowletter.qst` (307
  entries total). So the quest is registered in the WORLD but not in the CHARACTER.

**Gap: the character existed ~4.5 months before the quest existed.** When `_Toxeus` was
created and streamed through its regions (including, per the RCA, walking ~7 rooms deep past
`drxFirstxistion_connection`), `widowletter.qst` did not exist to be initialized, and the
engine has not retroactively added it.

### E4 - Tonight's session added nothing; the state is frozen

`Quest.myw` and `QuestToken.myw` from tonight's live save (20:24) are **byte-identical** to
the pre-session `Backup/` copies (18:57). Playing tonight on the current build did not add
the widow-letter quest (or any SV area quest) to the character's tracked set. This directly
matches Will's report ("the letter is NOT there" on the build that restored the widow
entities): restoring `widow_ling`/`trg_foundzhidan`/`location_treasurechest` in the level
cannot help, because the quest that would spawn/advance around them is not running for him.

---

## WHY THIS HAPPENS (mechanism)

Titan Quest tracks quest state PER CHARACTER, not globally. A quest becomes "tracked" for a
character when the engine first activates it for that character during play, at which point a
`.que` file and a `Quest.myw` entry (keyed by the quest's identity hash + a `crcFile` stamp
of the `.qst`) are created. The map's QUESTS section is the world-side registry of which
quest files exist; it is the CHARACTER-side `Quest.myw`/`.que` set that governs what actually
runs. A character only ever holds the quests that were activatable when it played through the
relevant content. Community guidance corroborates the model: fixing a missing quest means
re-triggering it via its quest-giver, or deleting `Quest.myw` to force a fresh re-scan - i.e.
the engine does NOT silently back-fill newly-added quests into an existing character's log.
(`Condition_OnLevelLoad` re-fires per region-load only for quests that are already tracked
and active for the character; for a quest the character does not track, there is nothing to
fire.)

This makes priority-2 (OnLevelLoad timing / revisit / fog-of-war) MOOT for `_Toxeus`: it
would only matter if the quest were tracked. It is not. (For completeness: the char has
walked the blood cave before, so even if the quest WERE tracked, the "spawns only on first
region load" sub-risk would be worth an in-game check - but that is a fresh-character
concern, not Will's.)

---

## WHAT UNLOCKS THE QUEST FOR AN EXISTING CHARACTER

This is the load-bearing question, because it changes the fix. Findings:

- **The engine will NOT auto-adopt `widowletter.qst` into `_Toxeus` on any number of normal
  loads/revisits.** There is no version-bump or Quests.arc re-scan that retroactively
  registers a brand-new quest into an existing character's `Quest.myw`. (If there were, E4
  would show the quest appearing after tonight's play; it does not.)
- **The clean, engine-legitimate way to make ALL the July-ported SV quests live is a
  character created AFTER the quests were added** (a fresh Custom-Quest character on the
  current build). That character's `Quest.myw` is initialized against the current
  `Quests.arc`, so `widowletter`/`urder`/`bossarena`/`open_bloodcave_portal` are all tracked
  and their `OnLevelLoad`/`EnterVolume` triggers fire normally.
- A save-surgery alternative (injecting the missing quest entries into `_Toxeus`'s
  `Quest.myw` + writing seed `.que` files) is theoretically possible given the format is now
  decoded, but it is out of scope here (this is a read-only diagnosis and we must not write
  to the save dir), it is fragile (must match the engine's identity-hash + `crcFile` exactly
  or the entry is ignored/re-derived), and it does not generalize to end users. It is NOT
  recommended as the ship fix.

---

## RECOMMENDED FIX

Two independent things are true and both should be acted on:

### FIX A (primary, ships the feature correctly): keep the quest-driven letter, and treat "existing character" as a KNOWN LIMITATION

The widow-letter questline (letter spawn -> pickup token -> carry to widow -> buff reward) is
data-complete once the WAVE-E `roadtotown03a` restoration (widow_ling / trg_foundzhidan /
location_treasurechest) is deployed. On a **fresh Custom-Quest character on the current
build**, the quest is tracked from creation, so:
- step-0 `OnLevelLoad` + `NOT OwnsToken(SQWL_PickedUpLetter)` spawns `finalletter` at
  `location_letterdrop` in `drxFirstxistion_connection` (on-mesh per the RCA),
- picking it up fires `Condition_PickupItem(finalletter)` -> `BestowTriggerToken
  SQWL_PickedUpLetter`,
- the widow/chest/buff steps then run off `trg_foundzhidan` / `widow_ling` / the golden
  chest.

Action: **verify the widow letter on a NEWLY CREATED Custom-Quest character**, not on
`_Toxeus`. Document (README / Workshop notes) that the July SV area questlines
(widow letter, urder, boss arena, blood-cave portal) require a character created on the
build that shipped them - existing pre-July saves will not see them. This is the correct,
low-risk, Steam-clean answer and it is the ONLY way ALL four ported questlines light up for a
player; it is not specific to the letter.

### FIX B (optional hardening, ONLY IF you want pre-existing saves like `_Toxeus` to get a letter): STATIC placement of `finalletter`

If Will specifically wants the letter to appear for his EXISTING `_Toxeus` character (whose
`widowletter.qst` will never run), the only mechanism that does not depend on the quest being
tracked is to place `finalletter` as a **static world item** at the letterdrop spot via
`INJECT_SPECS` into `drxFirstxistion_connection` (RCA local coords `(32.46, 10.0, 17.59)`).
The pickup-advances-quest trace resolves the two concerns:

- **Does a static pickup still advance the quest (on characters that DO track it)?** YES. The
  token is granted by `Condition_PickupItem(finalletter.dbr)` - a quest condition keyed on
  the ITEM RECORD, not on how the item entered the world. A statically-placed `finalletter`
  that a tracking character picks up satisfies `Condition_PickupItem` and bestows
  `SQWL_PickedUpLetter` normally, so the questline still progresses. (For `_Toxeus`, who does
  NOT track the quest, the pickup grants no token and just yields a letter item - which is
  exactly "the letter shows up" but the questline still cannot complete for him, because the
  downstream widow/chest steps are also untracked.)
- **Duplicate-letter risk on a FRESH character (static item + quest spawn both present)?**
  LOW but real: a tracking character would see the static `finalletter` AND the quest would
  spawn a second `finalletter` (until one is picked up and `SQWL_PickedUpLetter` is set).
  Picking up either satisfies `Condition_PickupItem` and stops further quest spawns, and the
  quest step `Action_RemoveItemFromInventory(finalletter)` at the widow removes one on turn-in
  - but the player could be left holding a duplicate scroll. If FIX B is used, prefer to
  ALSO neutralize the quest's step-0 "Spawn Letter" trigger (a byte-exact `qst_format.py`
  edit) so exactly one letter exists for everyone, at the cost of the "respawns fresh each
  visit" behavior. Net: static placement is the robust cross-character option but should
  REPLACE the quest spawn, not run alongside it.

### NOT recommended

- Re-scoping `OnLevelLoad` -> `EnterVolume` (RCA option B.2): does not help `_Toxeus` at all
  (still requires the quest to be tracked) and is unnecessary for fresh characters (the
  spawn point is already on-mesh). Skip it.
- Hand-editing `_Toxeus`'s `Quest.myw`/`.que` to inject the quest: fragile, non-generalizable,
  and outside a read-only diagnosis; do not ship this.

---

## BOTTOM LINE

- Hypothesis 1: **TRUE and proven.** `widowletter.qst` (added 2026-07-04) is not tracked for
  `_Toxeus` (created 2026-02-21); the entire questline is inert for that character.
- Root cause of "no letter": the quest's spawn trigger is never evaluated for this character
  because the quest is not in the character's `Quest.myw`, not because of any missing entity
  (the RCA already proved the letter data is complete and on-mesh).
- Fix: **test/ship on a fresh Custom-Quest character** (FIX A) - the only way all four July
  SV questlines work. If cross-save letter appearance is required, add a STATIC `finalletter`
  (FIX B), which correctly advances the quest for tracking characters via
  `Condition_PickupItem`, but should replace (not duplicate) the quest spawn.
