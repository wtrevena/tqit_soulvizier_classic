# PORTAL PAGE / ACT-SELECTION DLC CAP - RCA, audit, fix, gate

> **Trust level: LIVE.** Branch `fix/portal-atlantis-cap`, 2026-08-10. House style: no em dashes.
>
> **Will (verbatim, 2026-08-10):** "in the portal page i see atlantis which should be disabled in
> this mod"
>
> **Standing ruling this enforces (Will, 2026-07-10, BACKLOG):** "lets not make atlantis or anything
> past immortal throne reachable for now and we will fine tune immortal throne then if we want to
> add in the other areas later then we can."

---

## 1. WHERE THE PORTAL PAGE LIST COMES FROM

The in-game portal window (activate any rebirth fountain / teleport) is driven by **one database
record**:

```
records\ingameui\teleportmap\teleportmap.dbr
    templateName = database\Templates\InGameUI\WorldlMapWindow.tpl
```

Each **act page** on that window is a field triple on that single record:

| page | tab button | page art | destination list |
|---|---|---|---|
| Greece | `GreeceButton` | `GreeceMapImage` | `GreeceZoneList` (7 zones) |
| Egypt | `EgyptButton` | `EgyptMapImage` | `EgyptZoneList` (7 zones) |
| Orient | `OrientButton` | `OrientMapImage` | `OrientZoneList` (8 zones) |
| Immortal Throne | `HadesButton` | `HadesImage` (+ `OlympusMapImage`) | `HadesZoneList` (Olympus + 8 Hades zones) |
| **Ragnarok** | `ScandiaButton` (`x2tagMNorth`) | `ScandiaMapImage` | `ScandiaZoneList` (8) |
| **Atlantis** | `AtlantisButton` (`x3tagQAct06`) | `AtlantisMapImage` | `AtlantisZoneList` (6) |
| **Eternal Embers** | `ChinaButton` (`x4tagMChina`) | `ChinaMapImage` | `ChinaZoneList` (10) |

The `WorldlMapWindow.tpl` toolset template declares all 21 page variables with
`defaultValue = ""`, so a page whose fields are absent simply does not exist. Retail proof that
absence is a legal shipped configuration: `records\ingameui\mini map\world\worldmap.dbr` uses the
SAME template and carries `templateName` and nothing else.

## 2. RCA - why our mod shows the DLC pages

1. **SV 0.98i ships its own IT-era `teleportmap.dbr`** (44 `records\ingameui\teleportmap\*` records
   total) with exactly the four base pages and no DLC fields. That is the shape we want.
2. **`build_svc_database.strip_ui_overrides()` deletes it.** The strip removes EVERY
   `records\ingameui\*` / `records\xpack\ui\*` record except the mastery skill trees, because SV's
   TQIT-era UI records break AE's modern UI (click-through on mastery selection, missing portrait,
   transparent text). Measured on the shipped build76 arz: **0** `teleportmap` records, **0**
   `mini map\world` records.
3. **With no mod override, the record resolves from the BASE game `.arz`** - and the base TQAE
   record carries all seven pages. A player who owns the DLCs therefore sees Ragnarok, Atlantis and
   Eternal Embers tabs on the portal page. Exactly what Will reported.

The same mechanism hits a second act-selection surface: **the quest log**.
`records\ingameui\player quests\questwindow.dbr` (base) carries `questLocationButton5/6/7` +
`questMapBitmap5/6/7` pointing at the `XPack2` / `XPack3` / `XPack4` quest-log tabs. SV 0.98i's own
copy of that record stops at 4. Same strip, same fall-through, three extra DLC act tabs.

## 3. AUDIT - every DLC-act entry a fully-DLC'd player sees

Swept every base-game record under `records\ingameui\` and `records\ui\` for a DLC namespace
(`xpack2|xpack3|xpack4|atlantis|scandia|china|x2tag|x3tag|x4tag`): **56 records**. Classified:

| class | count | act-selection surface? | action |
|---|---|---|---|
| `teleportmap.dbr` (the portal page itself) | 1 | **YES - 3 DLC pages** | CAPPED |
| `player quests\questwindow.dbr` (quest-log act tabs) | 1 | **YES - 3 DLC act tabs** | CAPPED |
| DLC tab button records (`atlantisbutton`, `scandiabutton`, `chinabutton`) | 3 | leaves, only reachable from the page list | moot once the page fields are gone |
| DLC teleport ZONE records (`zones\atlantis\*` 8, `zones\scandia\*` 8, `zones\china\*` 10) | 26 | leaves, only reachable from a `*ZoneList` | moot once the lists are gone |
| `teleportmap\teleportmapbackground.dbr` | 1 | NO - the window FRAME art, sourced from `XPack4\InGameUI\...` for every player including non-DLC owners | left untouched (base AE panel art, not an act entry) |
| `altcasinomerchantwindow\*` (orb-merchant buttons, incl. `scandianorb`, `x4tagOrb*` rollovers) | 24 | NO - a merchant window, not act selection | out of scope, noted |

**So: the complete set of DLC-act ENTRIES in the act-selection UI is 3 portal pages + 3 quest-log
tabs, all expressed as 15 fields on 2 records.** Nothing else in the UI namespace offers an act.

## 4. SEVERITY - Atlantis is genuinely travel-able, not a dead list entry

The portal page is the visible tip. Measured against the DEPLOYED artifacts (build76):

- `XPack3/Quests/x3mq_AtlantisAdventure.qst` is registered at **index 211** of the map's
  **255**-entry QUESTS(0x1b) window, i.e. INSIDE the load window (`quests` idx 253 and 254 are the
  vanilla boundary pair).
- `records\xpack3\quests\npc\speaking\x3mq_marinos_rhodes_spawner.dbr` (a `DLCActorSpawner`) IS
  placed in `XPack/Levels/Area01_Rhodes/Rhodes_CityFinal_01.lvl`, on the mandatory
  Olympus -> Rhodes -> Hades spine.
- `records\xpack3\creatures\npc\teleporters\rhodes_boatmantogadir.dbr` IS placed in the same level,
  and the onward `gadir_boatmantoatlantis` / `gadir_boatmantomalta` / `gadir_boatmantoafrica` are
  placed in `XPack3\Levels\Iberia\Gadir01B.lvl` / `Gadir01.lvl`.

**Verdict: for an Atlantis-DLC owner the Rhodes -> Gadir -> Atlantis boat chain is live in our map.
This is a REAL act leak, not cosmetic.** It was already recorded as a gap in
`docs/BROODMOTHER_NEST_DESIGN.md` §6b and PARKED under the 2026-07-10 ruling. A non-DLC player is
unaffected (no XPack3 levels/NPCs; the `DLCActorSpawner` never fires), which is why the two existing
IT caps never covered it: both of those are POST-HADES transitions, and Atlantis branches mid-IT
from Rhodes.

**This lane does NOT close the travel leak** (see the DEBT section). It closes the act-selection UI.

## 5. THE FIX - and why this layer actually takes effect

`tools/build_svc_database.py :: apply_dlc_act_ui_cap(db, base_db)`

For each of the two records: import the **BASE** record into the mod `.arz` byte-faithfully
(`_import_base_record_override`, the shared helper the A5 Act-5 fix also uses), then delete exactly
the DLC fields - 9 on `teleportmap.dbr`, 6 on `questwindow.dbr`. Field absence is the template's own
declared default, so the pages simply cease to exist. Record type is set to the base record's own
`.arz` record type for exact vanilla parity.

**Why this layer works, stated against the A5 lesson.** The A5 lesson is that identity is the FULL
registry path: a quest the map registers under `XPack3/Quests/...` resolves from the BASE GAME's own
`XPack3/Quests.arc`, so a mod copy dropped at the plain `Quests.arc` root is never consulted and the
fix ships inert. That trap is specific to **archive-hosted files keyed by md5 of the registry path**.
A `.dbr`'s identity IS its record path, and the mod `.arz` overrides the base `.arz` per record path.
This is the same mechanism the A5 fix uses to override `records\xpack2\quests\objects\
portal_hadesscandia.dbr`, which is runtime-confirmed live. Neither capped record is DLC-namespaced
anyway; both live at plain `records\ingameui\...`.

**The one way this fix could still ship inert is ORDERING**, and that is the real trap here: applied
before `strip_ui_overrides()` the cap would be deleted again and the mod would ship nothing. So:

- the call site is immediately AFTER `strip_ui_overrides(db)` (base_db is still alive there);
- the function asserts the ordering, failing loud if any un-stripped SV record still exists in the
  two capped namespaces;
- an in-memory gate runs immediately, and the artifact gate re-proves it on the WRITTEN `.arz`.

**Preserved exactly:** every non-DLC field, byte-faithful from base (names, dtypes, values), so the
four Immortal-Throne-era pages, all 30 legitimate zone destinations, AE's modern window layout, the
Olympus map image, `HadesImage` = `XPack\UI\TeleportMap\WorldMap05.tex` (plain `XPack` is Immortal
Throne and stays legal) and the quest log's four base act tabs are untouched.

## 6. THE GATE - `tools/gate_dlc_act_ui_cap.py`

Fail-loud, committed golden allow-list, wired into the DB build **twice**: in-memory the instant the
cap is applied, and on the written `.arz` beside the other artifact gates (after
`gate_unlock_alignment`).

| check | asserts |
|---|---|
| T1 | `teleportmap.dbr` is PRESENT in the mod `.arz` (it survived the strip - the anti-inert proof) |
| T2 | none of the 9 banned DLC page fields exist |
| T3 | the page-field set == the golden allow-list, exactly (catches a re-add AND a legit page lost) |
| T4 | no field VALUE names a DLC act namespace (`xpack[234]`, atlantis, scandia, china; plain `XPack` stays legal) |
| T5 | `questwindow.dbr` present, DLC act fields 5-7 absent, 1-4 exact, no DLC values |
| T6 | the DERIVED portal page list == `['Greece', 'Egypt', 'Orient', 'Hades']` - **ZERO DLC-act entries** |
| T7 | the mod overrides no other `records\ingameui\teleportmap\*` record |

`--negtest` plants three defects and requires the gate to RED on each: Atlantis put back, a
legitimate page (Greece) dropped, the Atlantis quest-log tab put back.

## 7. PROOF ON DISK (static, this lane - the Ship phase owns the real build)

Run against build76's shipped `work/SoulvizierClassic/Database/SoulvizierClassic.arz` plus the base
game `database.arz`:

1. **BEFORE:** the gate FAILS on the shipped arz - `T1 teleportmap.dbr is ABSENT`, `T5
   questwindow.dbr is ABSENT`. The reported bug reproduced as an artifact fact.
2. **APPLY:** the real `apply_dlc_act_ui_cap()` writes 2 record overrides
   (`-= 9` and `-= 6` DLC fields).
3. **AFTER:** the capped arz written to disk and gated as a FILE: **all 7 checks PASS**, portal pages
   = `['Greece', 'Egypt', 'Orient', 'Hades']`.
4. **NEGATIVE:** all 3 planted defects caught (RED).
5. **FIDELITY:** capped record == base record minus exactly the DLC fields, names/dtypes/values
   identical, record type identical. Record delta vs build76: **+2 records, 0 removed, 0 changed.**

## 8. DEBT (registered, not silently dropped)

- **`BL-PORTALCAP-DEBT-1` (P1, OPEN, real act leak):** the **Rhodes -> Gadir -> Atlantis boat chain**
  is still live for an Atlantis-DLC owner (evidence in §4). This lane removes the Atlantis PAGE, not
  the voyage. The A5-style one-field DB suppression is NOT available here: a census of the whole base
  DB found DLC gate fields (`RequireDLC`/`RequireNoDLC`) on **17 records only, all
  `FixedItemTeleport.tpl` / `FixedItemTyphonPortal.tpl`**, and there is no Atlantis DLC token at all
  (only `TQA2` and `TQX4`); the Marinos spawner is a `DLCActorSpawner` and the boatmen are plain
  `Npc.tpl`. The four candidate layers, in order of preference:
  1. override `records\xpack3\quests\npc\speaking\x3mq_marinos_rhodes_spawner.dbr` (and/or the boat
     NPC) in the mod `.arz` so the Rhodes end of the chain never materialises - arz-only, needs a
     spawner-record study first;
  2. ship a mod `Resources/XPack3/Quests.arc` carrying a neutralised `x3mq_AtlantisAdventure.qst`
     (the A5-sanctioned "override inside the matching mod XPack archive" layer) - blocked on proving
     mod-arc-vs-base-arc shadowing is per-ENTRY and not whole-archive, which the DLC stub archives
     suggest it is NOT;
  3. re-point map registry index 211 to a mod-root quest path - correct but needs a map rebuild;
  4. do nothing and accept a DLC owner can sail to a dead-ended Atlantis (its 16 Tartarus arena gates
     are already dead - `BROODMOTHER_NEST_DESIGN.md` §6c).
  **Recommend (1), as its own lane, with Will's sign-off on the layer.**
- **`BL-PORTALCAP-DEBT-2` (P2, LAUNCH-GATED):** not proven in-game. Everything above is a database
  and gate proof. Will opening a portal and seeing four tabs (Greece / Egypt / Orient / Immortal
  Throne) is the launch gate. The specific runtime risk being carried: the engine tolerating a
  `WorldlMapWindow` record with the DLC page fields absent. Evidence it does: the template declares
  every page variable with `defaultValue = ""`, and retail ships
  `records\ingameui\mini map\world\worldmap.dbr` on the same template with NO page fields at all.
- **`BL-PORTALCAP-DEBT-3` (P3, scope note):** the quest-log cap (`questwindow.dbr`) was not in Will's
  report. It is included because it is the same law, the same record shape and the same one-line
  removal, and because SV 0.98i's own copy of that record already stops at act 4. Flagged so a vet
  can challenge it independently of the portal page.
