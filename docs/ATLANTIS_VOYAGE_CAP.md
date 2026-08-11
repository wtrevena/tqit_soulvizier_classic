# ATLANTIS SEA-VOYAGE CAP - RCA, route audit, fix, gate

> **Trust level: LIVE.** Branch `fix/atlantis-voyage-cap`, 2026-08-10. House style: no em dashes.
>
> **Ruling this implements: R-211.** Sibling of R-210 (`docs/PORTAL_PAGE_DLC_CAP.md`), which removed
> the Atlantis PAGE and explicitly left the SHIP, as `BL-PORTALCAP-DEBT-1`:
> *"an Atlantis-DLC owner can still SAIL Rhodes -> Gadir -> Atlantis. The page is gone, the voyage is
> not."*
>
> **Standing ruling both enforce (Will, 2026-07-10):** "lets not make atlantis or anything past
> immortal throne reachable for now and we will fine tune immortal throne then if we want to add in
> the other areas later then we can."

---

## 1. WHY THE TWO EXISTING IT CAPS NEVER COVERED THIS

Both prior caps are **post-Hades** transitions:

| cap | transition | layer | status |
|---|---|---|---|
| A5 part 1 | Hades -> Ragnarok (`portal_hadesscandia.dbr`) | DB record, AND-unsatisfiable DLC gate | live |
| A5 part 2 | Hades -> Eternal Embers (`x4_other_immortalthrone_to_eternalembers_teleport_a.dbr`) | same | live |

**Atlantis is not post-Hades.** It branches from **RHODES**, mid-Immortal-Throne, on the mandatory
Olympus -> Rhodes -> Hades spine. So neither cap ever touched it, and it survived R-210 as well
(which capped the act-selection UI, not travel).

## 2. THE ROUTE, END TO END (measured on the deployed build78 artifacts)

```
xpack3_findmarinos.qst              map QUESTS idx 207   journal + MapUnlockAtlantis token; NO travel
    |  fires on Condition_GotToken('Olympus - Typhon Defeated')
    v
x3mq_Marinos_Rhodes                 ZERO static placements in world01.map (byte-verified)
    ^  enters the world ONLY via ...
x3mq_marinos_rhodes_spawner.dbr     DLCActorSpawner, dlcRequirement=DLC2, placed ONCE in
                                    XPack/Levels/Area01_Rhodes/Rhodes_CityFinal_01.lvl
    |  Condition_ConversationStart(x3mq_marinos_rhodes)
    v
x3mq_AtlantisAdventure.qst          map QUESTS idx 211 of the 255-entry load window (idx 253/254 are
  step "START QUEST: Second Talk    the vanilla boundary pair), so it LOADS
  Marinos"
    -> Action_BoatDialog(rhodes_boatmantogadir, tag x3tagtravelquestion1)   RHODES -> GADIR
    -> Action_BestowTriggerToken('MapUnlockAtlantis')
    v
  (in Gadir) Marinos_Gadir mission chain: Necropolis -> Malta -> Hesperides
    -> Action_BoatDialog(gadir_boatmantomalta,  x3tagtravelquestion3)
    -> Action_BoatDialog(gadir_boatmantoafrica, x3tagtravelquestion5)
  step "GO TO ATLANTIS: Sixth Talk Marinos"
    -> Action_BoatDialog(gadir_boatmantoatlantis, x3tagtravelquestion7)     GADIR -> ATLANTIS

XPack3TartarusPortal.qst            map QUESTS idx 205
  step "Gadir":   ConversationStart(senechaloftartarus_gadir)   -> UnlockFixedItem(portaltotartarus)
  step "Corinth": ConversationStart(senechaloftartarus_corinth) -> UnlockFixedItem(
                  portaltotartarusfromcorinth + portaltotartarus)
                  the Corinth Senechal is spawned by senechaloftartarus_corinth_spawner.dbr, the
                  ONLY other DLCActorSpawner in the entire base DB
xpack3teleporters.qst               map QUESTS idx 206   the RETURN boats only
                  (Malta/Africa/Atlantis -> Gadir), all Condition_OnLevelLoad
```

**The travel mechanism is `Action_BoatDialog`, i.e. exactly the TRAVEL LAW shape: an NPC you talk to,
who asks you to confirm.** The captains are plain `Npc.tpl` actors; the destination and the confirm
tag live in the quest action, not on the NPC. So "removing the Atlantis option" means stopping that
action from ever reaching a live captain.

## 3. ROUTE AUDIT - every remaining Atlantis access path, enumerated

| # | route | reachable how | status after this cap |
|---|---|---|---|
| 1 | **Rhodes -> Gadir** (the only IT -> XPack3 doorway) | Marinos-Rhodes conversation -> `Action_BoatDialog` | CLOSED twice (spawner dead, captain hidden) |
| 2 | **Gadir -> Atlantis** | Marinos-Gadir chain -> `Action_BoatDialog` | CLOSED twice (route 1 gone, captain hidden) |
| 3 | **Gadir -> Tartarus** | Senechal-Gadir conversation -> `Action_UnlockFixedItem` | CLOSED (route 1 gone + portal unsatisfiable) |
| 4 | **Corinth -> Tartarus** | Senechal-Corinth -> `Action_UnlockFixedItem` | CLOSED (spawner dead + portal unsatisfiable; Corinth was already unreachable behind the A5 cap) |
| 5 | portal page / rebirth-fountain Atlantis tab | `teleportmap.dbr` `AtlantisZoneList` | already CLOSED by R-210 (gate T6: pages == Greece/Egypt/Orient/Hades) |
| 6 | quest-log Atlantis act tab | `questwindow.dbr` buttons 5-7 | already CLOSED by R-210 (gate T5) |
| 7 | a fixed-item ACT PORTAL into Atlantis | - | **DOES NOT EXIST.** All **17** DLC-gated (`RequireDLC`/`RequireNoDLC`) records in the base DB are Ragnarok / Eternal-Embers act portals; not one names Atlantis, Gadir or Tartarus |
| 8 | a non-DLC quest opening an Atlantis route | - | **DOES NOT EXIST.** Base `Quests.arc`, `xpack/Quests.arc` and `XPack4/Quests.arc` contain **ZERO** references to any `records\xpack3\` record. The only cross-archive xpack3 references are five `XPack2` side quests (`x3sq01_thestatue` etc.) whose records live in Asgard / Jotunheim / Muspelheim, i.e. inside Ragnarok, not Atlantis |
| 9 | a level stitch / walk-in into an xpack3 level | - | **DOES NOT EXIST.** `IT_ENDPOINT_AUDIT.md` Q1: the DLC level set is byte-identical vanilla == ours (sym-diff 0) and none of our 46 added levels is DLC-namespaced; vanilla itself has no walk-in to Atlantis, only the boats |
| 10 | difficulty unlock | - | not a transit. Atlantis never gated difficulty even in vanilla (`IT_ENDPOINT_AUDIT.md` Q3) |

**So the complete set of live Atlantis-transit paths was routes 1-4, and all four are now closed at
every link.** Routes 7-10 are absence proofs, not fixes.

## 4. THE FIX - and why THIS layer provably takes effect

`tools/build_svc_database.py :: apply_atlantis_voyage_cap(db, base_db)`

### 4a. Why the quest layer is NOT available (the md5-full-registry-path trap)

The map registers all **20** XPack3 quests under the `XPack3/Quests/...` namespace (idx 203-222).
Per the A5 RCA, the per-quest save identity is `md5(lowercased FULL registry path)` and the file is
resolved through that same DLC namespace, which the engine reads from the base game's **uncapped**
`Resources\XPack3\Quests.arc`. A mod copy dropped at the plain `Quests.arc` root is **never
consulted**. That is precisely how the build33 IT cap shipped 100% inert. Shipping a mod
`Resources\XPack3\Quests.arc` instead is blocked on proving mod-arc-vs-base-arc shadowing is
per-ENTRY, which is unproven; re-pointing map registry idx 211 would work but costs a full
688 MB map rebuild. **Neither is bet on here.**

### 4b. The layer that IS proven

A `.dbr`'s identity **is** its record path, and the mod `.arz` overrides the base `.arz` per record
path. That is the same mechanism the A5 Act-5 fix uses on
`records\xpack2\quests\objects\portal_hadesscandia.dbr`, which is runtime-confirmed live, and the
same one R-210 used. All six records are imported from base byte-faithfully
(`_import_base_record_override`, the shared canonical helper) with the base record's own `.arz`
record type, then exactly the capped fields are changed.

**Ordering:** unlike R-210 this cap has no ordering trap. `strip_ui_overrides()` only touches
`records\ingameui\` and `records\xpack\ui\`; none of the six records is in that scope. The call site
sits immediately after `apply_dlc_act_ui_cap()` so the whole act-cap family reads as one block and
`base_db` is provably alive.

### 4c. The six overrides

| # | record | change | why this shape is safe |
|---|---|---|---|
| 1 | `x3mq_marinos_rhodes_spawner.dbr` | **delete** `actorToSpawn` | `DLCActorSpawner.tpl` declares `actorToSpawn` as `type = file_dbr`, `defaultValue = ""`. **Field absence IS the template's own declared default**, so the spawner has nothing to spawn. Same argument R-210 shipped on |
| 2 | `senechaloftartarus_corinth_spawner.dbr` | **delete** `actorToSpawn` | same |
| 3 | `rhodes_boatmantogadir.dbr` | `startVisible = 0`, `IncludeInMap = 0` | `startVisible=0` is a **retail-shipped configuration on 604 base-game records**. `IncludeInMap=0` is the A5 minimap-ghost lesson: never leave a live map icon on a suppressed object |
| 4 | `gadir_boatmantoatlantis.dbr` | `startVisible = 0`, `IncludeInMap = 0` | same |
| 5 | `portaltotartarus.dbr` | `+RequireDLC=TQA2`, `+RequireNoDLC=TQA2` | the **A5 idiom verbatim**: "owns TQA2 AND does not own TQA2" is unsatisfiable, so the `FixedItemTeleport` never spawns. Shipped precedent for the AND semantics: `endportal_hades_normal_epic.dbr` (`RequireDLC=TQX4` + `RequireNoDLC=TQA2`). Both Tartarus portals are the SAME class as the A5-suppressed `portal_hadesscandia.dbr` |
| 6 | `portaltotartarusfromcorinth.dbr` | same | same |

**`dlcRequirement` is deliberately LEFT ALONE** on both spawners. It is a **picklist** (`DLC1;DLC2`),
so an invented out-of-picklist token would be unproven engine behaviour, and deleting it could read
as "no DLC required" - the one edit that could make things *worse*. The gate asserts it is still
exactly `DLC2`.

**Nothing can undo the hidden captains.** Byte-verified across all five base quest archives
(`Quests.arc`, `xpack`, `XPack2`, `XPack3`, `XPack4`): **no `Action_ShowNpc` anywhere names any
boatman.** The only actions that ever name them are `Action_BoatDialog`. (`x3mq_AtlantisAdventure`
does contain `Action_ShowNpc`, but only for the Acrocatus NPCs, inside Atlantis.)

### 4d. No regression to legitimate IT-era travel

Both hidden captains are `records\xpack3\...`, i.e. Atlantis-DLC additions to an IT level. Immortal
Throne's own travel NPCs live under `records\xpack\...` and are untouched. A player who does not own
the Atlantis DLC already experiences Rhodes exactly this way; the cap makes a DLC owner's Rhodes
match. The four base portal pages, all 30 legitimate zone destinations and the whole IT arc are
untouched.

### 4e. What is deliberately NOT capped

`gadir_boatmantomalta`, `gadir_boatmantoafrica`, and every RETURN boatman
(`atlantis_/malta_/africa_boatmantogadir`) are left exactly as vanilla. They are interior to an act
that is now unreachable, so suppressing them buys no closure, and the return boats plus the
Greece/Egypt/Orient/Hades portal pages are the **anti-strand path** for any character that sailed on
an earlier build. Suppressing them is the one change that could strand a player.

## 5. THE GATE - `tools/gate_atlantis_voyage_cap.py`

Fail-loud, committed golden allow-list, wired into the DB build **twice**: in-memory the instant the
cap is applied, and on the **written `.arz`** beside the other artifact gates (after
`gate_dlc_act_ui_cap`).

| check | asserts |
|---|---|
| V1 | both DLCActorSpawner records are PRESENT in the mod `.arz` (the anti-inert proof), carry **no** `actorToSpawn`, and still have `dlcRequirement == DLC2` (suppress the spawn, never widen the DLC gate) |
| V2 | both boundary boat NPCs are PRESENT with `startVisible == 0` **and** `IncludeInMap == 0` |
| V3 | both Tartarus portals carry an AND-unsatisfiable DLC gate (`RequireDLC` and `RequireNoDLC` share a token) |
| V4 | the mod `.arz` overrides **no** `records\xpack3\` record outside the golden allow-list (this cap's 6 + the mastery skill-panel controllers) - the over-reach / collateral-damage check |
| V5 | the **DERIVED** list of resolvable Atlantis-transit routes is **EMPTY**: all 4 known routes closed at EVERY link |

Plus an in-build **FIDELITY assert** (inside the cap, where `base_db` is alive): every field we did
not set is byte-faithful to the base record, values and dtypes, so the cap can never be a silent
content edit.

`--negtest` plants four defects and requires the gate to RED on each: the Marinos spawner given its
`actorToSpawn` back; the Rhodes captain un-hidden; a Tartarus portal un-gated; and a **collateral**
xpack3 override planted (proving V4 fails on over-reach, not only on under-reach).

## 6. PROOF ON DISK (static, this lane - the Ship phase owns the real build)

Run against the shipped build78 `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
(md5 `f663846233295da3e8824bfa4d8925c8`, 55,551,546 B) plus the base game `database.arz`:

1. **BEFORE:** the gate **FAILS** on the shipped arz, 7 checks: all six records ABSENT and
   `V5 4 resolvable Atlantis-transit route(s) remain`. The leak reproduced as an artifact fact.
2. **APPLY:** the real `apply_atlantis_voyage_cap()` writes **6** record overrides; the FIDELITY
   assert passes.
3. **AFTER:** the capped arz written to disk and gated as a **FILE**: **all checks PASS**,
   `V5 resolvable Atlantis-transit routes = []`.
4. **NEGATIVE:** all 4 planted defects caught (RED), each naming exactly the routes it reopened.
5. **DELTA vs build78:** **ADDED 6 / REMOVED 0 / MODIFIED 0.** The six additions are exactly the six
   capped records. No other record in the database moved by one byte.

## 7. DEBT (registered, not silently dropped)

- **`BL-VOYAGECAP-DEBT-1` (P1, LAUNCH-GATED): NOT PROVEN IN-GAME.** Everything above is a database
  and gate proof. **Will's one-line test (needs an Atlantis-DLC owner): after beating Typhon, walk
  Rhodes - there is no Marinos, no ship captain offering Gadir, and the quest log offers no Atlantis
  adventure.** The specific runtime risks carried: (a) the engine tolerating a `DLCActorSpawner` with
  `actorToSpawn` absent - evidence it does: the template declares that field with
  `defaultValue = ""`, exactly the argument R-210 shipped on, and an editor-fresh spawner has the
  same shape; (b) a hidden `Npc` being non-conversable - evidence: `startVisible=0` ships on 604
  retail records and is the standard `Action_ShowNpc` gating idiom throughout TQ's own quests.
- **`BL-VOYAGECAP-DEBT-2` (P3, scope note):** the two **Tartarus** portal suppressions were not
  strictly required - Tartarus is only reachable from Gadir (route 1, closed) or Corinth (already
  behind the A5 cap). They are included because Tartarus is an XPack3 area under the same standing
  ruling, because the idiom is the A5-proven one, and because defence in depth is cheap here.
  Flagged so a vet can challenge them independently of the voyage itself.
- **`BL-VOYAGECAP-DEBT-3` (P3, cosmetic):** an in-fiction refusal line from the Rhodes captain
  ("no ship sails west these days") was considered and **rejected for now**: the captain's dialog is
  a `.dbr` inside the base `Resources\XPack3\Dialog.arc`, so authoring one would depend on exactly
  the unproven mod-arc-vs-base-arc shadowing this lane refused to bet on. The captains are removed
  cleanly instead, which is the fallback Will's brief allowed.
- **Not a debt, stated for the record:** the 20 XPack3 quests stay registered in the map's QUESTS
  window. They are inert without their NPCs (every step is gated on a conversation, a pickup or a
  kill inside an unreachable act), exactly like the retained x2/x4 entries analysed in
  `IT_ENDPOINT_AUDIT.md` Q2. De-registering them is a map rebuild for zero behavioural gain.
