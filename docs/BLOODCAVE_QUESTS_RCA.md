# BLOOD-CAVE QUESTS RCA - Widow Letter no-show + the exploding-wall secret area

> Read-only root-cause analysis of two blood-cave quest problems, traced end-to-end
> from the Soulvizier 0.98i (SV) upstream through the built DB / `Quests.arc` into the
> DEPLOYED merged map (`work/SoulvizierClassic/Resources/Levels.arc`, the stable
> build17-family copy). Produced 2026-07-06. Companions: `docs/DROPPED_CONTENT_AUDIT.md`
> (byte-level dropped-entity audit), `docs/SV_AREAS_AUDIT.md`, `docs/CONTENT_PLAYBOOK.md`
> (records/quests/rewards), `docs/MODDING_PLAYBOOK.md` (levels/navmesh/portals),
> `CLAUDE.md` (status). No em dashes by house style.
>
> METHOD NOTE: all "DEPLOYED map" claims below are parses of
> `work/SoulvizierClassic/Resources/Levels.arc` (the deploy target the brief pinned as
> stable, since `build_quest_files.py` + `local/Levels_merged.arc` are mid-edit by a
> concurrent workflow). Upstream = `upstream/soulvizier_098i/Resources/` (Levels.arc +
> XPack/Quests.arc). DB = `work/SoulvizierClassic/Database/SoulvizierClassic.arz`.
> Quest bodies were parsed with `tools/qst_format.py`; level `0x05`/`0x14`/`0x0b`
> sections with the repo's `merge_levels_binary` + `build_section_surgery` +
> `rec02_format` parsers (validated: the SV-side parser reproduces the
> `DROPPED_CONTENT_AUDIT` sentinel coords byte-for-byte).

---

## TL;DR (both root causes)

**Q1 - Widow Letter never appears.** The letter is NOT a monster drop or a loot
container. It is spawned by a QUEST ACTION: `widowletter.qst` step "Letter Control"
runs `Action_SpawnEntityAtLocation(finalletter.dbr, location_letterdrop.dbr)` gated
only by `Condition_OnLevelLoad AND NOT OwnsToken(SQWL_PickedUpLetter)`. There is **NO
circular dependency** - the letter spawn does NOT depend on `widow_ling` or any other
dropped entity (that dependency only exists two steps later, for the chest/reward).
Every ingredient the letter needs RESOLVES in the deployed build: `location_letterdrop`
(a `QuestLocation`) IS placed in `drxFirstxistion_connection` at world (5691.5, 1.0,
3308.6) and that point is **ON the walkable navmesh** (0.10u from a walkable cell);
`finalletter` (an `ItemEquipment`/Parchment, pickable, has a mesh) exists;
`widowletter.qst` is present in `Quests.arc` and registered in the map QUESTS section.
So the letter mechanism is data-complete and uses a proven vanilla idiom (11 base/SV
quests use the same `OnLevelLoad`+`SpawnEntityAtLocation` pattern). The residual reason
Will saw no letter is therefore NOT a missing entity - it is the **runtime firing of
that spawn trigger** (the `Condition_OnLevelLoad` + cross-region
`Action_SpawnEntityAtLocation` timing/activation), which only an in-game test can
finally confirm. The SEPARATE, definite data breakage is that the rest of the questline
(chest + widow + the buff reward) is dead in build17 because `widow_ling`,
`trg_foundzhidan`, and `location_treasurechest` were DROPPED from the shared level
`roadtotown03a` (the concurrent WAVE-E `INJECT_SPECS` work restores them but is
uncommitted and not yet in the deployed map).

**Q2 - The exploding-wall secret area.** This is the blood-cave WATERFALL/SANCTUARY
secret chain driven by `open_bloodcave_portal.qst`, and it is **fully intact and
walkable in the deployed build17** - not dropped, not un-navmeshed. Mechanism: kill the
`q_highpriest_lone` proxy (spawns bloodwitch disciples + blood-demon champions = the
"blood creatures") -> the quest `Action_UnlockFixedItem`s the "wall"
(`babtpl_waterfallroom_secretdoor` + `waterblocker`, both `FixedItemDoor`) -> entering
`trg_open_waterdoor` `Action_OpenDynGridEntrance`s the portal `xprtl_bc2et_01`
(`GridEntranceDynamic`, its `0x14` binding to `new_secretdoor_transitionhallway`
RESOLVES) -> the secret hallway -> the **mega chest** `proxy_hidden_bloodcave_chest`
whose `hidden_bloodcave_chest_0{1,2,3}` gives `supra_special.dbr` = **25 Supra crafting
formulae** (verified: 25 recipe entries). There is **no character-buff reward in this
questline** - the "character buff" Will remembers is the WIDOW LETTER reward (a
permanent `Skill_Passive`, e.g. `characterLifeRegen`), a different blood-cave questline.
Every secret-area entity is placed, every record resolves, and every one of these
levels carries a REAL `0x0b` navmesh. So Q2 needs NO restoration; it needs an in-game
walk/kill test to confirm the quest-gated portal opens.

---

## QUESTION 1 - THE WIDOW LETTER

### 1.1 MECHANISM (how SV does it)

`widowletter.qst` (upstream `XPack/Quests.arc`, 14,358 B, byte-exact ported into the
mod) is a 3-parallel-control-step quest ("Letter Control", "Chest Control", "Widow
Control"). Full parse: the letter is produced by a quest action, not by a monster/loot:

**Step 0 "Letter Control" - the letter drop (the only part that matters for "no letter"):**
```
Trigger "Spawn Letter"
  Condition_OnLevelLoad                      (no level param -> global)
  Condition_OwnsTriggerToken (isNot=1)  tokenName="SQWL_PickedUpLetter"
  Action_SpawnEntityAtLocation
     entity   = records/drxmap/quest/finalletter.dbr        (the letter item)
     location = records/drxmap/quest/location_letterdrop.dbr (a QuestLocation marker)
Trigger "Stop Letter Spawning"
  Condition_PickupItem  itemRecord = finalletter.dbr
  Action_BestowTriggerToken "SQWL_PickedUpLetter"  + Action_UpdateJournalEntry
```

So `location_letterdrop` is a **spawn-location proxy** (`Class = QuestLocation`), NOT a
loot container and NOT a monster. The letter appears purely because the quest, on level
load, spawns `finalletter` at wherever that `QuestLocation` is placed - as long as the
player has not yet picked one up. This is a standard TQ idiom (11 SV/base quests use
`Condition_OnLevelLoad` + `Action_SpawnEntityAtLocation`, e.g. `xsq02_childfallenill`,
`xsq03_beaconquest`, `xsq12_rescueleader`).

**Step 1 "Chest Control"** (needs the letter + entering `trg_foundzhidan`): spawns
`chest_goldenchest_normal_03` at `location_treasurechest`; the golden chest FixedItems
(`goldenchest_0{1,2,3}`) bestow `SQWL_OpenedChest`.

**Step 2 "Widow Control"** (needs `widow_ling` NPC): on `Condition_ConversationStart`
with `widow_ling` (holding the letter), grants the reward - `Action_FireSkill
(xsq05_potion_buff)` + 3x `Action_GiveSkillPoints` of the `Skill_Passive` rewards
`sqwl - widow letter reward 0{1,2,3}` - and completes the quest.

**Critical: the letter (step 0) has NO dependency on `widow_ling`, `trg_foundzhidan`, or
`location_treasurechest`.** The brief's suspected circular dependency (letter needs
something that itself needs a dropped entity) does NOT exist. The letter would spawn
even with the entire rest of the questline dead.

The letter's home level (where `location_letterdrop` sits) is the BLOOD CAVE
(`drxFirstxistion_connection`), while the widow NPC + chest are back in the Great Wall
surface level `roadtotown03a`. The questline is deliberately split across two zones:
find the dead man's letter in the blood cave, carry it out to the widow.

### 1.2 CURRENT STATE (deployed build17 evidence)

| Ingredient | State in deployed build | Evidence |
|-----------|--------------------------|----------|
| `widowletter.qst` in `Quests.arc` | PRESENT (14,358 B, at archive root `widowletter.qst`) | arc parse |
| quest registered in map QUESTS section | YES (`Quests/widowletter.qst` + `XPack/Quests/widowletter.qst`) | QUESTS(0x1b) dump |
| `finalletter.dbr` (letter item) | EXISTS, `ItemEquipment`/`Parchment.tpl`, `cannotPickUp=0`, mesh `XPack\Items\QuestItems\QI_InsurgencyScroll01.msh` | `.arz` |
| `location_letterdrop.dbr` (spawn marker) | EXISTS, `QuestLocation` | `.arz` |
| `location_letterdrop` PLACED in a level | YES - `drxFirstxistion_connection.lvl` 0x05, SV-local (32.459,10.005,17.593) -> world (5691.5,1.0,3308.6) | level 0x05 parse |
| letter spawn point walkable? | ON-MESH - nearest walkable navmesh cell 0.10u away; level's `0x0b` is REAL (112,303 B, 136,393 walkable cells) | `rec02_format` decode |
| `drxFirstxistion_connection` reachable | YES - 3rd room from the cave mouth (xPassageTransitionStart -> BC_initialpathway -> drxFirstxistion_connection), all REAL navmeshes; Will walked ~7 rooms deep, PAST this room | topology parse |
| reward records (`Skill_Passive` x3, `xsq05_potion_buff`) | ALL EXIST + resolve | `.arz` |
| `widow_ling` / `trg_foundzhidan` / `location_treasurechest` | **ABSENT from the deployed map (0 instances)** - dropped from shared `roadtotown03a` by the clean-base merge | level 0x05 scan (0 hits map-wide) |

So the LETTER SIDE is data-complete: marker placed on-mesh, item exists, quest present
and registered, no circular dependency. The CHEST + WIDOW + REWARD side is data-BROKEN:
the three `roadtotown03a` entities were dropped (`roadtotown03a` is a SHARED v0x11 level;
the merge kept SVAERA's version, which never had SV's widow entities - same failure
class as the Rebirth Fountain / Duister losses in `DROPPED_CONTENT_AUDIT`).

Note on build provenance: the widow `INJECT_SPECS` block (widow_ling/trg_foundzhidan/
location_treasurechest -> roadtotown03a) exists ONLY in the uncommitted working tree of
`tools/build_section_surgery.py` (the concurrent WAVE-A/E restoration). It is NOT in
HEAD and NOT in the deployed map. So in the build17 Will played, those three are
definitively absent.

### 1.3 ROOT CAUSE

Two distinct facts, do not conflate them:

1. **Why the CHEST + WIDOW + BUFF REWARD are dead (definite, data-level):** `widow_ling`,
   `trg_foundzhidan`, and `location_treasurechest` were DROPPED from the shared level
   `roadtotown03a` when the merge kept SVAERA's blob. Even if the letter spawns and is
   picked up, there is no volume to enter (`trg_foundzhidan`), no chest location
   (`location_treasurechest`), and no widow to talk to (`widow_ling`) - so the questline
   cannot progress past the letter and the buff reward can never be granted.

2. **Why the LETTER itself did not appear (most-likely, runtime-level):** the letter's
   data is complete and on-mesh, and the spawn idiom is proven in vanilla, so the letter
   NOT appearing is NOT a missing-entity problem. The remaining candidate is the
   RUNTIME firing of the step-0 spawn trigger:
   - `Condition_OnLevelLoad` carries no level parameter; it fires on level/region load.
     `Action_SpawnEntityAtLocation` can only place the entity if the target
     `QuestLocation` is resolvable at fire time. If the trigger fires on the FIRST region
     the player loads (HiddenValley01, character start) while the blood cave is not
     streamed, the spawn no-ops; it then depends on the trigger RE-firing when
     `drxFirstxistion_connection` streams in (its `isResettable=1` allows this, but
     whether OnLevelLoad re-evaluates per region-stream vs only per world/save-load is
     the exact engine behavior that is not statically determinable here).
   - A secondary possibility is quest ACTIVATION: the quest is registered and its step-0
     trigger is an OnLevelLoad self-activator, so it should run; but if the engine gates
     later steps' referenced-record resolution at quest-load and that had any effect on
     activation, it would suppress step 0 too. (No evidence this happens - TQ resolves
     quest record refs lazily at trigger-eval - but it is the only other lever.)

   This is the item the brief flagged as "only an in-game test can confirm."

The single most defensible statement: **there is no dropped/missing entity blocking the
letter drop; the letter's spawn point is placed and walkable; the failure is either (a)
Will genuinely walked through the room before/without the spawn firing, or (b) the
OnLevelLoad spawn did not re-fire in the blood-cave region.** The parts that are
DEFINITELY broken by dropped content are the downstream chest, widow, and buff reward.

### 1.4 RESTORATION SPEC

**A. Make the whole questline completable (fixes chest + widow + buff) - the concrete,
data-level fix.** Restore the 3 dropped SV entities into the shared level
`roadtotown03a` (v0x11 -> MUST use the append-only `0x14` path, per `MODDING_PLAYBOOK`
8.4 / the v0x11 crash history). This is already staged in the concurrent
`tools/build_section_surgery.py` working tree `INJECT_SPECS` and must be built +
deployed. Coords are SV-LOCAL and CORRECT (roadtotown03a is NOT grid-shifted; SV corner
== shipped corner (824,-125,221)):

```
INJECT_SPECS['levels/world/orient/greatwall/roadtotown03a.lvl'] = [
    ('records\\drxmap\\quest\\widow_ling.dbr',            66.5019, -63.3410, 50.1083),  # Npc (Condition_ConversationStart)
    ('records\\drxmap\\quest\\trg_foundzhidan.dbr',       77.0740, -63.8614, 61.6060),  # BoundingVolume (Condition_EnterVolume)
    ('records\\drxmap\\quest\\location_treasurechest.dbr',27.1969, -63.6251, 34.7034),  # QuestLocation (chest spawn)
]
```
All three records resolve in the built `.arz` (verified: widow_ling=Npc,
trg_foundzhidan=BoundingVolume, location_treasurechest=QuestLocation). No new DB work,
no navmesh work, no map GRID_SHIFT. Method: `INJECT_SPECS` append (append-only 0x14).
Risk LOW-MED (v0x11 target - use the append path, never `generate_default_0x14`
wholesale). This is `DROPPED_CONTENT_AUDIT` WAVE E and is the correct fix.

**B. For the letter-drop firing itself (only if an in-game test shows the letter still
does not spawn after A):** the data is already correct, so the levers are runtime, in
order of preference:
  1. First, TEST IN-GAME on a fresh Custom Quest character (no stale `SQWL_PickedUpLetter`
     token) - walk into `drxFirstxistion_connection` and look at world (5691.5,1.0,
     3308.6). The letter is a small scroll mesh with `DisplayAsQuestItem=0` (no quest
     glyph), easy to miss - confirm presence/absence deliberately.
  2. If it does not spawn: change the spawn trigger's gating so it fires reliably when
     the blood-cave region is present, e.g. re-scope `Condition_OnLevelLoad` by pairing
     it with a `Condition_EnterVolume` on a volume placed IN
     `drxFirstxistion_connection` (guarantees the location is streamed when the spawn
     fires), OR place the letter directly in the level `0x05` as a static pickup instead
     of a quest-spawn (drop the quest step, inject `finalletter` at (32.46,10.0,17.59)) -
     the simplest, most robust option, at the cost of the "spawns fresh each visit"
     behavior. Both are `INJECT_SPECS`/quest edits, LOW risk.

CONFIDENCE: HIGH that the letter's data is complete and on-mesh and that the chest/widow/
buff are dead due to the roadtotown03a drops. MEDIUM on the exact runtime reason the
letter did not visibly spawn (needs the in-game test in B.1).

---

## QUESTION 2 - THE EXPLODING-WALL SECRET AREA

### 2.1 MECHANISM (how SV wires wall -> passage -> secret area -> chest -> reward)

This is the blood-cave WATERFALL / SANCTUARY secret chain, driven by
`open_bloodcave_portal.qst` (upstream 19,362 B; ported with ONE unrelated trigger
neutralized - the Garden-of-Merchants "Duister" boat-dialog to the absent
`starting_storyteller.dbr`; the waterfall/secret content is byte-identical to upstream).
It is NOT the `urder`/"Secret Place" rogue-forest cluster and NOT the maze03 uber/boss
arena - those are separate SV areas (`SV_AREAS_AUDIT`). Exact records:

**The "wall" made of exploding blood creatures:**
- `records\drxmap\proxy\q_highpriest_lone.dbr` (`Proxy`) -> pool
  `records\drxmap\proxy\pools\q_highpriest_lone.dbr` spawns
  `c_disciple_miniboss` (bloodwitch disciples) x3 + `b_med_blooddemon_3{0,1,2}`
  (blood-demon champions). These are the "blood creatures" guarding the secret door.
  (The literal "exploding sprites" motif - `t1_pitspawner`/`t1_lildude` - is the
  DelphiLowlands Greece scene, `DROPPED_CONTENT_AUDIT` 5; Will may be blending the two
  blood/exploding encounters, but the blood-cave secret-door guard is the priest pool.)

**Wall -> passage (the destructible "wall" + the portal):**
```
open_bloodcave_portal.qst  Step 0 "BloodCave Doors and Portals":
  Trigger "Unlock Waterfall Door"
    Condition_KillAllCreaturesFromProxy  proxyRecord = q_highpriest_lone.dbr
    Action_UnlockFixedItem  babtpl_waterfallroom_secretdoor.dbr   (FixedItemDoor = the wall)
    Action_UnlockFixedItem  triggers/waterblocker.dbr             (FixedItemDoor)
  Trigger "Open Waterfall Door"
    Condition_EnterVolume   triggers/trg_open_waterdoor.dbr
    Action_OpenDynGridEntrance  portals/xprtl_bc2et_01.dbr        (GridEntranceDynamic)
    Action_OpenDynGridEntrance  portals/xprtl_bc2et_02.dbr        (GridExitOneWay)
  Trigger "Open Temple Exit Door"
    Condition_KillAllCreaturesFromProxy  proxyRecord = q_shaman_lone.dbr
    Action_UnlockFixedItem  bossroomentrancedress/hc_treasurydoor02_boss.dbr
  Trigger "Open Sanctuary Portal"
    Condition_EnterVolume   triggers/trg_open_sanctuaryportal.dbr
    Action_OpenDynGridEntrance  portals/xprtl_et2fn_01.dbr / _02.dbr
```

**Passage -> secret area (how the portal streams you across):** the DynGridEntrance
portal objects are pure-ART records (mesh only, no destination field - exactly like a
cave-mouth `GridEntrance`). The destination binding lives in the level's `0x14` metadata
(these SV levels carry `0x14` in the deployed map), 48-byte payload = [own mouth
UniqueId | reciprocal exit UniqueId | DESTINATION level GUID @ byte offset 32]:
- `xTempleTransitionHallway` rec[0] (`xprtl_bc2et_01`) `0x14` payload @32 =
  `new_secretdoor_transitionhallway`'s GUID -> **RESOLVES**.
- `yet_another_fucking_connector` rec[93] (`xprtl_et2fn_01`) `0x14` payload @32 =
  `drxBC3`'s GUID -> **RESOLVES**. The one-way exits (`xprtl_bc2et_02` in
  new_secretdoor, `xprtl_et2fn_02` in drxBC3) hold the reciprocal UniqueIds.

**Secret area -> chest -> reward:**
```
open_bloodcave_portal.qst  Step "Hidden Chest Control":
  Trigger "Open Chest" (x3, one per difficulty container)
    Condition_UseFixedItem  drxitem/container/hidden_bloodcave_chest_0{1,2,3}.dbr  (FixedItemContainer)
    Action_GiveItem  supra_special.dbr  (all 3 tiers)  + Action_UpdateJournalEntry "Esti's Chest"
```
- The mega chest is `records\drxitem\container\proxy_hidden_bloodcave_chest.dbr`
  (`Proxy`) placed in `drxBC2` (the waterfall room) at world (5284.1, 1.0, 3092.1); it
  proxies the `hidden_bloodcave_chest_0{1,2,3}` `FixedItemContainer`s.
- The reward is `records\xpack\item\loottables\arcaneformulae\supra_special.dbr`
  (`LootItemTable_FixedWeight`) = **exactly 25 Supra crafting formulae** (lootName1..25,
  weight 100 each: caster/melee armor pieces, all weapon types, artifact formulae). The
  chest also has its own `loottable_hidden_bloodcave_01.dbr` + a champion gold generator.

**Is the reward a buff?** NO. `open_bloodcave_portal.qst` has only 3 `Action_GiveItem`
(the supra formulae) and 0 buff/skill/attr actions. The **only "character buff" in the
blood-cave-family quests is the WIDOW LETTER reward** (Q1): `Action_FireSkill
(xsq05_potion_buff)` + `Action_GiveSkillPoints` of `Skill_Passive` records
(`sqwl - widow letter reward 0{1,2,3}`, e.g. `characterLifeRegen=1.0`, a permanent
passive). So Will's "mega chest AND a character buff" is two rewards from two different
blood-cave questlines: the mega chest = open_bloodcave (25 Supra formulae), the buff =
widow letter (permanent Skill_Passive). Neither is a shrine.

### 2.2 CURRENT STATE (deployed build17 evidence)

**Everything for Q2 is PRESENT and INTACT in the deployed map.** No dropped entity, no
dead stub. Placement + resolution + navmesh all verified:

| Entity / record | Class | Placed in (deployed) | world coord | Navmesh |
|-----------------|-------|----------------------|-------------|---------|
| `q_highpriest_lone` (guard proxy) | Proxy | drxBC2 | (5304.2,1.0,2994.2) | drxBC2 0x0b REAL 393,453 B |
| `babtpl_waterfallroom_secretdoor` (the wall) | FixedItemDoor | drxBC2 | (5288.4,0.2,2990.7) | " |
| `waterblocker` | FixedItemDoor | drxBC2 | (5287.8,1.0,2990.0) | " |
| `trg_open_waterdoor` (enter volume) | BoundingVolume | drxBC2 | (5287.2,1.0,2989.8) | " |
| `proxy_hidden_bloodcave_chest` (MEGA CHEST) | Proxy | drxBC2 | (5284.1,1.0,3092.1) | " |
| `xprtl_bc2et_01` (dyn portal in) | GridEntranceDynamic | xTempleTransitionHallway | (5235.0,1.0,2991.0) | 0x0b REAL 147,097 B; 0x14 -> new_secretdoor RESOLVES |
| `xprtl_bc2et_02` (one-way exit) | GridExitOneWay | new_secretdoor_transitionhallway | (5047.0,4.0,3467.0) | 0x0b REAL 140,584 B |
| `trg_open_sanctuaryportal` | BoundingVolume | yet_another_fucking_connector | (4583.1,4.0,3491.7) | 0x0b REAL 246,579 B |
| `xprtl_et2fn_01` (dyn portal) | GridEntranceDynamic | yet_another_fucking_connector | (4573.0,4.0,3491.0) | 0x14 -> drxBC3 RESOLVES |
| `xprtl_et2fn_02` (one-way exit) | GridExitOneWay | drxBC3 | (4411.0,2.0,3089.0) | 0x0b REAL 798,229 B |
| `q_shaman_lone` (temple-exit guard) | Proxy | yet_another_fucking_connector | (4617.0,4.0,3492.5) | " |
| `hc_treasurydoor02_boss` | FixedItemDoor | yet_another_fucking_connector | (4608.0,4.0,3491.0) | " |
| Leinth boss room: `q_leinth_lone`, `vortexportal_exit`, `door_bossroom_trap`, `trg_springtrap`, `trg_bossroom_close_door`, melinoe trap locations | Proxy/Npc/FixedItem/volumes | bossfight | ~(3480-3529, 3.x, 3165-3191) | 0x0b REAL 93,776 B |
| `hidden_bloodcave_chest_0{1,2,3}`, `supra_special`, reward records | FixedItemContainer / LootItemTable | DB | - | resolves in `.arz` |

The brief's specific check - **`new_secretdoor_transitionhallway` HAS a real navmesh
(140,584 B REC\x02) AND its entry mechanism exists** - is CONFIRMED: entry is the
`xprtl_bc2et_01` `GridEntranceDynamic` in `xTempleTransitionHallway` (which the player
reaches by walking; xTempleTransitionHallway's walkable band overlaps the drxBC2
waterfall-room region and abuts it at the x=5275 grid edge), whose `0x14` binding points
at `new_secretdoor_transitionhallway`'s GUID and resolves. The portal starts CLOSED
(dynamic) and is opened by the quest after killing the priest and entering
`trg_open_waterdoor`. This is exactly why the secret hallway "shares zero walkable floor
with the main chain" - it is GATED by a quest-opened portal, not by a navmesh gap.

Topology (world corners): the secret/sanctuary hallway row sits at Z~3425 stepping X by
120 (a full grid edge, so they grid-seam walk): yet_another_fucking_connector(4572) ->
drxBC_Connector2(4692) -> drxBC_finale_transitionconnector(4812) ->
new_secretdoor_transitionhallway(4932) -> Temple_entrance_clean(5052). The main cave
chain sits at Z~2955-3291. The two are joined by the two quest-opened DynGridEntrance
portal pairs (`xprtl_bc2et`: temple hallway <-> new_secretdoor; `xprtl_et2fn`:
yet_another <-> drxBC3), plus the drxBC_Finale->bossfight `0x06` link.

### 2.3 ROOT CAUSE

There is **no defect** in Q2's data. The exploding-wall secret area, its portal
plumbing, its mega chest, and its Supra-formulae reward are all present, resolvable, and
sitting on real navmeshes in the deployed build17. The reason Will "remembers it but is
not sure it is there" is that reaching it requires PLAYING the quest sequence, which has
not been tested:
1. walk deep enough to the waterfall room (drxBC2),
2. kill the `q_highpriest_lone` blood-creature guard (unlocks the secret door),
3. enter the `trg_open_waterdoor` volume (opens the `xprtl_bc2et` portal),
4. take the portal into the secret hallway and use the hidden chest.

The only prior-known blood-cave un-walkable risk (the historic invisible wall) was the
navmesh problem, and these levels all carry REAL navmeshes in build17. The one quest
edit made to `open_bloodcave_portal.qst` (neutralizing the "Duister PortalDude" trigger)
is unrelated to the waterfall secret area (it was the Garden-of-Merchants entry).

### 2.4 RESTORATION SPEC

**None required for the data.** Q2 is complete. The actionable item is a VERIFICATION
plan, not a restoration:
- In-game (fresh Custom Quest character): reach drxBC2, kill the priest pool, confirm
  `babtpl_waterfallroom_secretdoor` unlocks, enter `trg_open_waterdoor`, confirm the
  `xprtl_bc2et_01` portal opens and streams into `new_secretdoor_transitionhallway`,
  then find + use `hidden_bloodcave_chest_01` and confirm the 25 Supra formulae drop.
- IF the in-game test shows the portal does NOT open or does NOT stream (the only
  residual uncertainty, which static analysis cannot settle): the levers are
  (1) confirm `open_bloodcave_portal.qst` is actually active in-game (it is registered +
  present; a `Condition_OnLevelLoad`/`EnterVolume` self-activator), and
  (2) confirm the DynGridEntrance `0x14` binding survives the streaming hand-off (the
  binding bytes resolve statically; the runtime portal open is quest-driven). No entity
  or navmesh work is anticipated.
- If Will specifically wants a CHARACTER BUFF behind this wall (as he remembers), note
  that is the WIDOW LETTER's `Skill_Passive` reward, gated on the Q1 restoration (WAVE E)
  - fixing Q1 restores that buff. The open_bloodcave hidden chest itself only gives the
  Supra formulae by design.

CONFIDENCE: HIGH that the secret area is data-complete and walkable in build17 (entities
placed, records resolve, `0x14` portal bindings resolve, navmeshes REAL). The single
thing only an in-game test can confirm is that the quest-gated DynGridEntrance actually
opens and streams the player across at runtime.

---

## APPENDIX - key coordinates + records (INJECT_SPECS-ready)

**Q1 letter (already correct, on-mesh, no change needed):**
`records\drxmap\quest\location_letterdrop.dbr` (QuestLocation) placed in
`levels/world/xbloodcave/drxfirstxistion_connection.lvl`, SV-local (32.459,10.005,
17.593), deployed world (5691.5,1.0,3308.6), navmesh REAL, point ON-MESH.

**Q1 fix (restore chest+widow+buff) - `INJECT_SPECS` append into the v0x11 shared level
`levels/world/orient/greatwall/roadtotown03a.lvl` (NOT grid-shifted; append-only 0x14):**
```
records\drxmap\quest\widow_ling.dbr             (66.5019, -63.3410, 50.1083)  # Npc
records\drxmap\quest\trg_foundzhidan.dbr        (77.0740, -63.8614, 61.6060)  # BoundingVolume
records\drxmap\quest\location_treasurechest.dbr (27.1969, -63.6251, 34.7034)  # QuestLocation
```
All resolve in the built `.arz`. (This is the concurrent WAVE-E `INJECT_SPECS` block,
currently uncommitted; it must be built + deployed to make the questline completable and
to deliver the buff reward.)

**Q2 (no change needed) - the secret-area chain, all placed + resolving in build17:**
wall = `records\drxmap\bloodcave\babtpl_waterfallroom_secretdoor.dbr` (drxBC2);
guard = `records\drxmap\proxy\q_highpriest_lone.dbr` (drxBC2);
portal in = `records\drxmap\bloodcave\portals\xprtl_bc2et_01.dbr` (xTempleTransitionHallway,
0x14 -> new_secretdoor_transitionhallway);
mega chest = `records\drxitem\container\proxy_hidden_bloodcave_chest.dbr` (drxBC2) ->
`hidden_bloodcave_chest_0{1,2,3}.dbr` -> `supra_special.dbr` (25 Supra formulae);
buff (widow letter, separate) = `records\quests\rewards\sqwl - widow letter reward 0{1,2,3}.dbr`
(Skill_Passive).
