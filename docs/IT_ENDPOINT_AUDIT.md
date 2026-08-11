# Immortal-Throne Endpoint Audit — does SV Classic's playable arc end at IT?

> **Question (Will, load-bearing for difficulty design):** SV 0.98i's balance assumes the
> campaign ends at the END OF IMMORTAL THRONE (Act 4, Hades) in Normal/Epic/Legendary.
> TQAE's DLC acts (Ragnarok=xpack2, Atlantis=xpack3, Eternal-Embers-era xpack4) must NOT
> extend the playable arc. Verify (static) that our mod ends at IT's end and difficulty
> progression pivots there.
>
> **Scope:** READ-ONLY static audit of the DEPLOYED artifacts
> (`work/SoulvizierClassic/Resources/{Levels.arc,Quests.arc}` + built
> `Database/SoulvizierClassic.arz`), cross-checked against the pristine vanilla TQAE base
> (`<game>/Resources/{Levels,Quests}.arc`) and the SVAERA reference
> (`reference_mods/SVAERA_customquest/...`). Produced 2026-07-07. House style: no em dashes.
>
> ⚠️ **AMENDMENT 2026-08-10 (R-210, branch `fix/portal-atlantis-cap`) - two corrections to this
> audit's scope.** (1) This audit covered LEVELS, QUESTS and scaling, but never the **act-selection
> UI**: the portal window's page list is a single database record and the mod was shipping the BASE
> game's copy, so a DLC owner saw Ragnarok / Atlantis / Eternal-Embers tabs. Now capped, see
> `PORTAL_PAGE_DLC_CAP.md`. (2) The Q3 statement that "Atlantis is optional side content" understates
> it: Atlantis branches from **Rhodes, mid-Immortal-Throne**, not post-Hades, so neither IT cap ever
> covered it, and the Rhodes -> Gadir -> Atlantis boat chain is measurably live in our map
> (`x3mq_AtlantisAdventure.qst` at registry idx 211 of 255; Marinos spawner + boatman both placed in
> `Rhodes_CityFinal_01`). Tracked as `BL-PORTALCAP-DEBT-1`.

---

## VERDICT

**PASS, with one design caveat that is inherent to the platform, not a mod defect.**

The mod adds **zero** DLC-act content of its own. Every Ragnarok/Atlantis/EE level and DLC
quest present in our map is inherited **byte-for-byte from the vanilla TQAE base map** (the
DLC level set is set-identical vanilla==ours; the DLC quest-identity set is a strict subset
of vanilla's, minus two dev-only stubs). The four SV area questlines and the completion
trigger are the ordinary IT-era main chain. The database leaks **no** DLC monster / level /
difficulty-scaling records into the Act 1-4 arc.

The **caveat** (unchanged from vanilla, and unavoidable for a Custom Quest built on the full
`world01.map`): the vanilla Act-4-Hades -> Act-5-Ragnarok transition machinery is present and
registered inside the load window (it is base-game content we inherit). It is **gated by DLC
ownership**: a player who does NOT own the Ragnarok/Atlantis/EE DLC has no Corinth/Asgard
NPCs, levels, or the "Persephone after Hades" portal-unlock, so their arc ends at Hades
exactly as SV 0.98i's balance assumes. A player who DOES own the DLC can continue past Hades
into the expansions, exactly as they could in vanilla TQAE. The mod does not, and as a
content-only Custom Quest largely cannot, hard-block a DLC owner from walking into Ragnarok.
If Will wants a hard cap at IT for DLC owners too, that is a deliberate map/quest change
(see FIX OPTIONS), not a bug to repair.

---

## Q1. WORLD: DLC levels present? reachable? added by us?

**Present: yes (inherited). Added by us: none. Rewired by us: none.**

Deployed `world01.map` LEVELS(0x01) section = **2282** entries. Vanilla = 2235, SVAERA = 2235.

| | Ragnarok(xpack2) lv | Atlantis(xpack3) lv | Eternal-Embers(xpack4) lv | total DLC (xpack2/3/4) |
|---|---|---|---|---|
| VANILLA base | 290 | 258 | 726 | **1271** |
| SVAERA ref   | 290 | 258 | 726 | 1271 |
| OURS         | 290 | 258 | 726 | **1271** |

- The DLC (`xpack[234]`) level set is **byte-identical vanilla == ours** (symmetric set diff
  = 0). We neither added nor dropped nor renamed a single DLC level.
- The **46 levels we added** over vanilla are ALL Soulvizier area interiors
  (`levels\world\xbloodcave\*`, `uberdungeon\*`, `bossarena\*`, `greece\minidungeons\
  spartacryptlevel2`, `egypt\minidungeons\coldtombs`, `olympus\gardenofmerchants`, ocean
  extensions). **DLC-namespaced among the 46 added: 0.**
- Reachability: the DLC acts are reachable in exactly the vanilla way (see Q2/Q3), which is
  **DLC-ownership-gated**. No SV-added portal, quest binding, or level-stitch points INTO any
  DLC level (we only added walk-links / mouths for the blood cave and the SV interiors).
- Asset suppression signal: the mod ships **empty 2048-byte DLC-stub `.arc`s** for
  `Resources/XPack2`, `XPack3`, `XPack4` (Dialog/Music/Scenery/Sounds all gutted;
  `bootstrap_working_mod.ps1:119-268`, `CONTENT_PLAYBOOK.md:108-111`). This strips the DLC
  regions' scenery/dialog/sound assets from the mod payload (the DLC world levels still index,
  but their art/dialog is not shipped by the mod; a DLC owner gets them from the base game).

## Q2. COMPLETION TRIGGER + what the retained x2/x4 entries do

**Completion is the ordinary IT/Hades main chain; the retained DLC boundary entries are inert
NPC/controller quests that require physically standing in a DLC act to do anything.**

- The mod's `Quests.arc` carries the FULL base main chain (`quest 1` .. `quest 15`, the
  scripted-scene set, `init - set up all acts.qst`) plus the 5 SV additions. The IT/Hades
  finale + Act-4 completion resolve through the standard chain
  (`init - set up all acts.qst` wires the Hades-generals / after-Hades steps with
  `Action_CompleteQuestNow`; `quest 15 - save olympus from typhon.qst` uses
  `Condition_KillAllCreaturesFromProxy(BossProxy_20_Typhon_Titan)` ->
  `Action_BestowTriggerToken` -> `Action_CompleteQuestNow`). These are base-game IT-era
  identities, unchanged by us.
- **QUESTS(0x1b) registry = exactly 256 entries** (vanilla's proven-loading count). Boundary
  parity is byte-exact with vanilla:
  - idx 254 = `quests/x4_other_002_hcdungeon_control.qst`
  - idx 255 = `xpack2/Quests/x2_StartQuest.qst`
  - (SVAERA has 254 entries and ends at x2_StartQuest at idx 253; ours restores vanilla's
    256/parity while inserting the 4 SV primaries at idx 97-100.)
- The 5 SV area quests sit INSIDE the window: `sv_commonmechanics`(96),
  `open_bloodcave_portal`(97), `urder`(98), `widowletter`(99), `bossarena`(100). No duplicate
  basenames. None depends on a DLC act.
- **What the retained x2/x4 entries actually do in a world without their areas:** they are
  **inert**, not harmful.
  - `x2_StartQuest.qst` (idx 255): its triggers are `Condition_ConversationStart` with the
    Ragnarok rally/void NPCs (`x2_startquest_rally.dbr`, `x2_startquest_dvoid.dbr`) plus a
    `Condition_GotToken`. It only fires if the player is standing in Ragnarok's Corinth and
    talks to those NPCs. In an IT-bounded (or non-DLC) playthrough those NPCs are never
    reachable, so the quest never advances. It cannot supersede or move the IT completion
    point.
  - `x4_other_002_hcdungeon_control.qst` (idx 254) and the block of `x4_*` at idx 224-253 are
    EE controllers/side quests, all `OnLevelLoad`/`ConversationStart` scoped to xpack4 levels
    or NPCs that are never entered in the IT arc. `x2_MainQuestSanityCheck.qst` (idx 199) is a
    dev sanity controller. All are the vanilla identities at (or near) their vanilla indices.
  - **Nothing DLC-side supersedes the IT completion.** The DLC main chains that WOULD move the
    endpoint (Ragnarok "Burning Sword" / Surtr, Atlantis, EE) live in the base game's
    `XPack2/XPack3/XPack4` quest archives and only run if their acts are physically entered,
    which requires DLC ownership + the vanilla Hades->Corinth portal (Q3).

**DLC quest-identity parity (our map vs vanilla):** ours adds **0** DLC quest identities;
ours is missing only `x4_dev_001_deletebeforerelease` and `x4_dev_002_ratchet` (vanilla
dev-only stubs, harmless to drop). Net: our DLC registry is a strict subset of vanilla's.

## Q3. DIFFICULTY UNLOCK for Custom Quest characters

**Mechanism (authoritative, community-corroborated):** difficulty unlock in TQAE is
per-character and driven by campaign completion of the map you are playing. Beating the map on
Normal unlocks Epic for that character; Epic unlocks Legendary. A custom map is "its own map"
to the engine even when identical to vanilla, so its difficulty progression is bounded by that
map's own completion trigger. Which boss must die is **content-driven**:

- No Ragnarok DLC (or DLC unowned in this arc): killing **Hades** (Act 4 / IT end) completes
  the arc and unlocks the next difficulty. This is precisely SV 0.98i's assumption.
- Ragnarok DLC owned AND the Act 5 arc entered: the completion point moves to **Surtr**
  (Ragnarok's final boss). Atlantis is optional side content and never gates difficulty.

**Does OWNING Ragnarok change the unlock requirement inside our custom map?** It changes it the
same way it changes vanilla, and only if the DLC act is actually entered. The gate is the
vanilla **Hades -> Corinth portal**: `x4_other_001_control_expansionportals.qst` (registered
at idx 232 in our load window, inherited from vanilla) holds the whole DLC linkage web,
including the step **"IMMORTAL THRONE Portal to Eternal Embers / RESETTABLE: Portal From
Immortal Throne"** = `Condition_ConversationStart(persephone_hades.dbr)` ->
`Action_UnlockFixedItem`. That is the "talk to the lady after Hades dies, a portal opens"
transition. It requires the DLC's Persephone NPC + destination levels, which exist only for a
DLC owner. So:

- For a **non-DLC** player: the transition NPC/levels do not exist -> no portal -> arc ends at
  Hades -> Epic/Legendary unlock is the Hades kill. Matches design intent exactly.
- For a **DLC owner**: our map inherits vanilla's continue-past-Hades behavior verbatim (we
  changed nothing here) -> they CAN proceed into Ragnarok, and their difficulty completion
  then follows the vanilla Surtr rule. This is the design caveat in the VERDICT.

The mod is explicitly DLC-aware in one benign way that confirms it does not try to break DLC
owners: `build_svc_database.py:962 add_dlc_mastery_trees` adds the RuneMaster (Ragnarok) and
Neidan (Atlantis/EE) player masteries to the PC records so the mastery-select UI is not broken
for DLC owners (the target skill trees are not baked into the mod .arz; they resolve from the
base DB at runtime). This is a character-build convenience, orthogonal to act/monster scaling.

## Q4. SCALING SANITY (no DLC-act scaling leaks into our arc)

**Confirmed clean.** Built `SoulvizierClassic.arz` = 50,352 records. DLC-namespaced records
total **8, all** of which are the mod's OWN xpack3 skill-panel UI controllers
(`records\xpack3\ui\skills\mastery {1..8}\panectrl.dbr`, created by
`build_svc_database.py:721 fix_mastery_panel_buttons`). Zero `xpack2` / `xpack4` /
`x2_` / `x3_` / `x4_` / ragnarok / atlantis / asgard / jotunheim / muspelheim / scandia
records. No DLC monster records, no DLC level/proxy records, **no DLC scaling records**. The
only active character/monster scaling tables are base + IT
(`records\game\gameengine.dbr`, `records\xpack\game\gameengine.dbr`, the base/IT
`containerlevelequation` + hero/elite/boss/uber scaling). Probes for
`records\xpack{2,3,4}\game\gameengine.dbr` and DLC `levelequation` variants: **all absent.**

The mod's build/patch scripts touch DLC namespaces in exactly two functions, both skill-UI /
mastery, neither monster/level scaling:
- `build_svc_database.py:721 fix_mastery_panel_buttons` (skill-button panel overrides;
  lines 777, 783-786).
- `build_svc_database.py:962 add_dlc_mastery_trees` (adds RuneMaster/Neidan PC mastery
  string refs; lines 975-976; targets resolve from base DB, not baked).
`apply_svc_patches.py`, `wire_souls_to_monsters.py`, `create_uber_souls.py`: zero DLC
references. (Evidence gathered by the DB sub-audit; scratchpad-only scripts, no repo writes.)

---

## FIX OPTIONS (only if Will wants a hard IT cap for DLC owners too)

None of this is required to meet the stated design assumption for **non-DLC** play or for the
mod's own content; it only matters if the goal is to prevent a **DLC-owning** player from
continuing past Hades. In descending order of surgical-ness / lowest blast radius:

1. **Lane = map QUESTS + portal machinery (owner: svaera_plus_portals map tooling).** Neutralize
   the IT->DLC transition at its single choke point: the "Portal From Immortal Throne" step in
   `x4_other_001_control_expansionportals.qst` (Persephone-after-Hades -> UnlockFixedItem). Port
   that quest into the mod `Quests.arc` with that one trigger's action dropped (same surgical
   pattern already used for `open_bloodcave_portal` entry-NPC and `widowletter` spawn in
   `build_quest_files.py`). The quest identity is already registered at idx 232, so this is a
   `Quests.arc`-only change (no map rebuild). Net: even a DLC owner never gets the Corinth
   portal from Hades; the arc ends at Hades. VERIFY in-game with a DLC-owning character.
2. **Lane = map LEVELS/SD.** Drop the DLC world levels from the LEVELS index (heavier, risks the
   SD/GROUPS regressions already tracked in CAVE_GRAFT_COMPLETENESS_AUDIT GAP-1; not recommended
   over option 1).
3. **Do nothing (current state).** Ship as-is: correct for non-DLC players (the majority target
   for a "Classic" back-port) and identical-to-vanilla for DLC owners. Document the caveat.

**Recommendation:** option 1 if a hard cap is wanted; otherwise option 3 is a legitimate ship
state and the difficulty balance holds for the non-DLC audience the mod targets.

---

## Evidence artifacts (read-only; scratchpad, not committed)

- `scratchpad/verify_arc_end.py` — parses deployed world01.map QUESTS+LEVELS + Quests.arc.
- `scratchpad/compare_three_maps.py` — vanilla vs SVAERA vs ours (quest/level counts, DLC
  level counts, boundary parity, level-set diff).
- `scratchpad/dlc_parity.py` — DLC quest-identity parity + SV-quest presence.
- DB sub-audit — DLC-record enumeration in the built `.arz` + build-script DLC touch points.

Boundary facts reproduced: QUESTS=256, idx 254/255 = `x4_other_002_hcdungeon_control` +
`x2_StartQuest` (vanilla byte-parity); SV quests at idx 96-100; DLC level set identical to
vanilla (sym-diff 0); 46 added levels all SV interiors (0 DLC); 8 DLC DB records all mod UI.
