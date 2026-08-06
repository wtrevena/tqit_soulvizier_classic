# WILL'S TEST GUIDE - build40-dev bosses + SV areas (Helos traveler hub; deployed to DEV + DEV2 2026-07-14)

> ## NOW LIVE ON DEV + DEV2: build40-dev (2026-07-14) - see BUILD40 CHECKS below
> **BOTH `SoulvizierClassicDEV` and `SoulvizierClassicDEV2` now run build40-dev** - the TESTHUB map (full
> Helos traveler hub) over the build40 DB/Text/Quests (12 b40 content lanes b41-b53 + the warden P1 fix).
> **`SoulvizierClassicDEV2` is a fresh-char test surface** - start a BRAND-NEW Custom Quest character there
> for the placement/spawn checks so TQ save-baking does not hide them (your main DEV char has world state
> baked in). Deployed + md5-verified on disk (both entries): `Levels.arc` `d4965d29` (TESTHUB), `arz`
> `b33c5a44`, `Text.arc` `c910da65`, `Quests.arc` `37cf867f`. **Steam is build40 canonical** (shipped
> 2026-07-14; its map is the canonical `9981085b`, NOT this dev TESTHUB variant - the hub is never uploaded).
> **To load it: fully quit TQ if it is open, then start TQ fresh** (Steam was already running and was not
> restarted; the deploy landed while TQ was closed, so the files are current).

> Fastest test path: play the **DEV entry** (Custom Quest -> SoulvizierClassicDEV). Its TESTHUB
> map variant adds LOCAL-ONLY **traveler NPCs** (talk-to-travel, boat-dialog) - a **HELOS TRAVELER
> HUB** with one named person per test target (see the next section) plus the **monster test yard**
> in Hidden Valley where the custom bosses spawn at 100% for point-blank testing. The Steam build
> has none of that (canonical map only). Fully quit + restart TQ before testing so it loads the fresh
> files (Steam was already restarted today, so no Steam restart is needed).

> ## 🆕 PR-5 (2026-08-06): THE SPARTA CRYPT IS NOW ENTERED FROM THE ATHENS CATACOMBS (canonical/Steam)
> **This is a CANONICAL/Steam change (it ships), not a TESTHUB-only one.** Per Will's decision - "the
> Sparta Crypt should be entered from the Athens CATACOMBS, not from Helos" - a **catacomb entrance
> traveler now stands on the shipping map**, and **Almyros the Wayfarer in Helos NO LONGER lists "The
> Sparta Crypt"** (he still offers Garden of Merchants / The Secret Place / The Uber Dungeon).
>
> **WALK-TO TEST (fresh Custom Quest char recommended):**
> 1. Go into the **Athens catacombs** and work down to the **DEEPEST level** (CataCube02_FloorLast) -
>    the chamber with the **stairs-down**, amid the beastmen. World spot **(-6587, 1, -3180)**.
> 2. A **traveler NPC stands right by the stairs-down** there (record `svc_area_return_sparta`). Talk
>    to him -> his boat menu includes **"Descend into the Sparta Crypt"**.
> 3. Pick it -> you teleport **on-mesh inside `spartacryptlevel2`** (the crypt interior). A **return
>    traveler stands there** (`svc_testhub_return_sparta`) and sends you back to **this catacomb door**
>    (primary) or **Helos** (secondary).
> 4. Sanity: talk to **Almyros in the Helos plaza** and confirm **"The Sparta Crypt" is GONE** from his
>    menu while Garden / Secret Place / Uber Dungeon remain.
>
> **IN-GAME CONFIRMATION IS THE REMAINING GATE.** This was proven byte-level (only the catacomb blob's
> 0x05 changed; navmesh byte-identical; the landing passes gate_landing_clearance) but NOT walked
> in-game by the implementer (deploys are the orchestrator's). See BACKLOG PR-5 + WILL_RULINGS R-160.

## 🩸🩸 OCEAN-CHAMBER CRASH FIX - build49-dev on DEV (2026-07-27) - DO THIS ONE FIRST

**What changed:** your crash probe caught it twice, in the same place both times: the game died
loading the navmesh of `ocean_extension05`, a 240x240 chamber sitting right against `drxBC3` in the
deep ocean part of the cave. That chamber (and 7 others like it) shipped a **broken 148-byte
navmesh** - a container the engine reads past the end of, straight into the heap. Nothing to do with
memory pressure: one session died after 5 loads in 6 seconds, the other after 11 loads over 4
minutes, both at that one chamber, while 20+ other chambers loaded fine.

All 8 broken chambers now carry a proper (empty) navmesh in the shape the base game itself uses for
its scenery levels: `ocean_extension05`, `ocean_extensionx01/x03/x04/x05/x06/x07`, and `coldtombs`
(that last one is in Egypt - same landmine, different room). Only those 8 blobs changed; everything
else in the map is byte-identical to build48. DB/Text/Quests untouched.

**Restart first (standing law):** fully quit **TQ AND Steam**, restart Steam, then start TQ fresh.

1. **Load your `_Toxeus` save** (Custom Quest -> `SoulvizierClassicDEV`).
2. **Walk into the area that killed you** - the start of that deep section of the blood cave, through
   `drxBC3` / `drxBC_Finale` and out over the ocean-extension block. Before, this crashed to desktop.
   **Expected: no crash.**
3. **Keep walking around that block** (the ocean chambers ring the whole finale area) and give it a
   couple of minutes, since one of the two probe runs only died after ~4 minutes of play.
4. **Report:** (a) did the crash stop? (b) does the area still LOOK right (the ocean/backdrop
   scenery should be unchanged - it was never walkable floor)? (c) any new invisible wall anywhere in
   the finale area?

If it still dies there, say so immediately - the fallback is already picked (drop the navmesh section
from those 8 levels entirely, which is what the base game does for its own backdrop levels).

## 🩸 BLOOD-CAVE CRASH FIX - build48-dev on DEV (2026-07-17) - THE walk test (do this first)

**What changed:** the recurring blood-cave crash at the **first respawn fountain inside the cave**
(the mid-cave fountain, `new_secretdoor_transitionhallway` / `respawn_hadescave01`) is now fixed on
`SoulvizierClassicDEV` (fix A: that chamber's navmesh no longer waits on its neighbours to be loaded,
so it can't null-deref on a fresh spawn). Only that ONE chamber changed; nothing else in the map.
Deployed to `SoulvizierClassicDEV/Resources/Levels.arc` (md5 `c1e814e4`); DB/Text/Quests untouched.
This is the one thing static analysis cannot settle - it needs your run. Not on Steam yet
(walk-test-gated).

**Restart first (standing law):** fully quit **TQ AND Steam**, restart Steam, then start TQ fresh, so
it loads the new file (the running game holds the map in memory). Then, on **DEV**:

1. **Load your `_Toxeus` save that sits at the fountain** (Custom Quest -> SoulvizierClassicDEV). It
   loads at the mid-cave respawn fountain where it used to crash.
2. **Kill a Blood Cult Disciple** near the fountain. **Expected: NO crash** (before, this deterministically
   crashed to desktop). If it still crashes, stop and say so - that's fix A failing and we escalate.
3. **Walk the two seams and back** (this is the part only you can confirm - fix A could leave an
   invisible wall at a seam even though the crash is gone):
   - **WEST seam** -> toward `drxbc_finale_transitionconnector` (the connector chamber back toward the
     cave mouth). Walk across the seam and back. Does the player cross, or stop at an invisible wall?
   - **EAST seam** -> toward `temple_entrance_clean` (the temple side, deeper). Walk across and back.
     Same question.
4. **Report:** (a) did the Disciple-kill crash stop? (b) does the WEST seam still walk both ways?
   (c) does the EAST seam still walk both ways?

If the crash is gone AND both seams walk, we extend the same fix to the two remaining latent respawn
chambers (`drxBC3` deep in the cave, `RogueEncampment` in the Secret Place/Duister) and ship. If a
seam walls, we swap that chamber to a doorway-portal instead. (Detail: `docs/reports/b87_bloodcave_navok_rca.md` sec 10.)

## BUILD40 CHECKS (new this wave - both DEV entries are build40-dev, 2026-07-14)

build40-dev is live on **both** `SoulvizierClassicDEV` and `SoulvizierClassicDEV2`. Two of these want a
**FRESH Custom Quest character on DEV2** (TQ bakes world/spawn state into a save, so an existing char can
hide a placement fix). The two size-clip items ride the DB and can be checked on any character.

- **Ephialtes size-clip (EYEBALL - this is the Steam promote check).** Ephialtes, the Waking Dread was
  scaled UP to **2.7** (was 2.2). In the **Dread Halls terminal vault** (Judgment), confirm his body does
  NOT clip through the ceiling or walls and he still paths / can be meleed. This size shipped to Steam
  sight-unseen at your "ship everything" call - if he clips, say so and we drop his scale ~0.2 in build41.
- **Mnemophage size-clip (EYEBALL - this is the Steam promote check).** The Mnemophage shell was scaled UP
  to **2.9**. In the **Pools of Mnemosyne glyph ring** (Act 4 Judgment), confirm no ceiling/wall clip. Same
  drop-0.2 walk-back if it clips.
- **Aithon arena - reachable + fights (FRESH DEV2 char).** Get to the **Olympian Arena** (boss_arena). Last
  round the arena dais was an isolated navmesh island (you would land 28u BELOW the fight with no way up);
  that was FIXED this wave. Confirm you can **walk up onto the dais** to **Aithon, the Ember-Crowned** (a
  boss-scale fire-satyr champion, scale 1.9), the fight triggers, and his fire cast animations read clean.
  He drops the `{^F}Aithon, the Ember-Crowned Soul`. This fight was greenlit sight-unseen - veto or bless it.
- **Placement / spawn fixes (FRESH DEV2 char - dodge save-baking).** On a brand-new DEV2 char, spot-check the
  b41-b48 map work via the plaza travelers: the **5 apex-boss set-pieces** on the map, **Tantalus inside the
  Den of Tantalus** (b45), **Kroisos relocated to the Tomb of the Queens** (b47), the **boss/world chests**
  (Charon / Dorus / Ephialtes / Tantalus, b42), the **Uber-Dungeon minimap alignment + region label** (b46),
  and the **established-area returns** (Garden / Secret / Uber / Sparta) firing with a traveler that actually
  talks (b48 mute-traveler fix). Anything mis-placed, silent, or unreachable = report.

## BUILD38 CHECKS (new this wave - verify once a build38 DB is deployed)

These ride the DB/Text (not the map), so they apply on both DEV and, once shipped, Steam. Build38 is
merged in git but NOT yet built/deployed; do these after the next DB build lands on DEV.

- **Damage numbers.** Hit any monster with normal, elemental, and damage-over-time attacks and confirm
  FLOATING damage numbers appear (before build38 only critical hits showed a number). Healing numbers too.
- **Earth mastery layout.** Open the Earth skill tree: there should be exactly **ONE "Rupture"** (the
  staff line), the graft chain now reads "Flame Surge / Burning Bolts / Flame Arch / Fire Nova", and the
  Rupture chain should sit lower and read as a clean vertical chain (no interleaving, no floating icons).
- **Repointed icons + Dream background.** Spot-check the masteries whose graft skills had missing icons
  (Warfare Fissure, Defense Perfect Block, Earth Fire Nova / Burning Bolts / Flame Arch, Storm Frost Nova,
  Dream Image, Nature "Sylvan Protection"): every button now shows an icon AND a name. The **Dream** mastery
  screen should have a real background (not a black pane). Screenshots welcome.
- **Earth Fury cooldown.** The Anapaest / Gigantes Earth Fury soul skill should recharge in **5 seconds**
  (not 16). (Regression fix - it was 16s in build37-dev.)
- **Enslaver frequency.** Toxeus the Enslaver should now appear roughly **once per act** (was ~6), and you
  should **never see two of him in the same pack**. Report if you fight two side by side.
- **Language switch (optional).** If you read a non-English language: switch the game language and confirm
  vanilla menus/items localize (Soulvizier's own added content stays English by design). This is a HARD
  gate before any Steam push that changes Text.arc.

## HELOS TRAVELER HUB v2 (DEV / TESTHUB map only) - drops you at the AREA ENTRANCE, not the boss

In the **Helos starting-town plaza** (where you begin a Custom Quest char) stand **14 named
travelers** just south of the town-portal shrine. Each is a "talk-to-travel" NPC: **walk up, talk,
and a boat-dialog asks you to confirm the destination** - then it teleports you. This is the ONLY
travel mechanism (**if you are EVER teleported just by walking, that is a bug - report it**).

**v2 change (this is what you asked for):** each traveler now drops you at the **natural in-game
approach point** for its area - the **door / entrance / travel-NPC you would use in game**, standing
**amid the regular mobs**, NOT on top of the boss. So you can test the real in-game travel guys,
learn where everything is, and **walk in** to the boss yourself.

### Original 11 areas - where v2 now drops you

| Traveler NPC | Drops you at (v2) | What to walk to / test |
|---|---|---|
| **Traveler: Garden of Merchants** | the merchant hub by the caravan_rhodes Super-Caravan + the SV **rift-shrine** (teleportshrine_gom) that reaches the Garden in game | browse the merchants; the rift-shrine is the in-game way in |
| **Traveler: The Secret Place** | the darkforestenter **forest-cluster entry** | walk in; the crow-hero bosses (Murderbunny, Zilla) live in the interiors |
| **Traveler: The Sparta Crypt** | the **Sparta-Crypt DOOR** in the deepest Athens catacomb (CataCube02_FloorLast, by the stairs-down), amid catacomb beastmen | 🆕 the return traveler standing right there (`svc_area_return_sparta`) now has a SECOND option too: "Descend into the Sparta Crypt" - takes you straight into `spartacryptlevel2` (the interior itself), where its own return traveler now sends you back to THIS catacomb door (primary) or Helos (secondary) |
| **Traveler: The Uber Dungeon** (was "Obsidian Halls") | the **Knossos->Uber DOOR** in the Minotaur's Labyrinth (maze03), at the Minotaur's secret door | the in-game Uber entrance; the base-game Minotaur Lord is ~24u east. 🆕 the return traveler standing right there (`svc_area_return_uber`) now has a SECOND option too: "Enter the Uber Dungeon" - takes you straight into `crypt_floor1` (the interior itself), where its own return traveler now sends you back to THIS door (primary) or Helos (secondary) |
| **Traveler: The Boss Arena** | the boss-arena forecourt (~90u south of the arena volume) | walk north into the Satyr-Shaman arena |
| **Traveler: Blood-Cave Warband** | the blood-cave connection chamber at the **regular demon pack** (~35u off the Enslaver horde) | walk up to the Enslaver warband (skeleton leader + 4 marauders) |
| **Traveler: Medea Tomb (Dorus)** | the tomb **entrance** (cryptentrance), amid the drowned court | walk ~82u to **Dorus, the Drowned King** + hoard |
| **Traveler: Den of Tantalus** | the Styx swamp-**stairs entrance**, amid anouran | walk ~36u to **Tantalus, the Insatiable** (2 forms) + hoard |
| **Traveler: Golden Bough (Charon)** | the Styx **Hades-city settlement** (the boatman, storyteller + a Styx rift-shrine) | test the settlement NPCs; walk east to **Charon, the Unferried** + the Golden Bough |
| **Traveler: Pools of Mnemosyne** | the Mnemosyne cave **stairs-up entrance** | walk ~20u to **The Mnemophage** (boss-glyph ring) |
| **Traveler: Dread Halls (Ephialtes)** | the Dread Halls **stairs-up entrance** | walk ~130u SW to **Ephialtes, the Waking Dread** in the deep vault |

### NEW travelers (order ii) - map-placed bosses the original 11 did not cover

| Traveler NPC | Drops you at | Boss(es) to walk to |
|---|---|---|
| **Traveler: Toxeus the Devourer** | the drxbc2 blood-cave chamber, amid demon/hound/acolyte packs | walk NW to the waterfall corner where **Toxeus the Murderer, Devourer of Blood** rises (the crimson superboss) |
| **Traveler: Vashkarr the Eldest** | the Chang'an cave (random05a), north end | walk ~28u to **Vashkarr, Eldest of the Ancients** (all-black dragon warlord + 2 champions) |
| **Traveler: The Obsidian Halls** | the tombobs02 Obsidian-Halls **stairs-down entrance**, amid Obsidian undead/demons | walk the halls: the **4 roulette wardens** (Sarkoth / Gorrahk / Voranthys / Ilsevar) + the **Broodmother nest** (deep south chamber) |

### Not portal-able yet - PENDING MAP PLACEMENT (b37 map pass)

These bosses are built in the DB but are **not placed on the map yet**, so there is no spot to
portal to. They are listed here so nothing is silently missing; they get travelers once their map
placement lands:
- **The Polis Daemonai vault Guardian** (the caged Guardian + 5 majestic chests)
- **The Helepolis, Taker of Cities** (Fields of the Diadochi)
- **Menoetes, Marshal of the Dead** (+ the three Hades general upgrades)
- **Neferkha, the Rimebound Pharaoh** (Egypt tomb)

### Getting back

Each of the **11 boss/door areas above has its own distinct Return Traveler** placed a few steps
from where you land -> talk -> confirm -> back to the Helos plaza (distinct records, so each binds).
The three "kept" areas (**Garden / Secret Place / Boss Arena**) have no dedicated hub return - use
their in-game returns instead: the Garden/Secret **SV rift-shrines**, the Boss Arena's own arena
portal, or the **universal fallback: a TQ Town-Portal scroll returns you to town from ANY area**.

**Hub verification checklist:** (1) all 14 travelers present + individually clickable (no two
stacked); (2) each teleport lands you on solid ground (on-mesh) at the area **entrance**, NOT on the
boss; (3) you can walk from the entrance to the boss; (4) from each of the 11 boss/door areas the
Return Traveler brings you back to Helos; (5) NO walk-through teleports anywhere - travel only after
you talk + confirm.

## A. ALL NEW/CUSTOM BOSSES - where to find them (canonical path)

Blood cave complex (enter via the Silk Road cave in Hidden Valley, take the WEST tunnel):
1. **Toxeus the Murderer, Devourer of Blood** - beyond the secret waterfall chamber. Red boss;
   drops his soul + (new) the big boss orb. Crimson shroud.
2. **Toxeus the Murderer, Enslaver of Souls** (build36 rework) - black SKELETON leader with
   4 "Enslaved Shadow Marauder" demons at his side (deployed-demon strength) + summon waves; the
   warband stands in the first connection chamber (near the widow letter spot). He ALSO roams the
   cave as a rare. Orb on the skeleton; marauders drop nothing.
3. **The Broodmother of the Deep** - the nest apex set-piece deep in the cave (build35; build36
   adds her death crescendo: frost nova + corpse brood).
4. **Blood-Witch houndmaster disciples** (CRASH RETEST here) - the room after the first door /
   respawn portal: kill the hound-summoners repeatedly. Mitigation shipped; if TQ crashes, note
   the time and tell the assistant (deep dump analysis is staged).

Obsidian Halls (via the Knossos -> Uber Dungeon door) - the treasure roulette + its wardens, all
buffed in build36 (sizes, immunities, summons):
5. **Sarkoth the Glasswright** (3x, tanky, summons fire whelps), 6. **Gorrahk the Tombsplitter**,
7. **Voranthys the Sepulchral** (2.5x, real kit, cold breath), 8. **Ilsevar the Ashen Watch**
   (3x; his soul now grants the manual-cast AoE Life Drain Nova),
9. **Vashkarr, Eldest of the Ancients** (all-black shadow shroud, 3x, stun-immune, dragonfire
   breath + roar + 16-jet death nova). Also in the TESTHUB yard.

New build36 uber bosses (mainline Act 4, all with hoards/orbs/souls; also reachable via TESTHUB):
10. **Dorus, the Drowned King** - the Medea temple underground tomb (Act 4). Raises his drowned
    court; hold-and-drown combo; hoard chest.
11. **Tantalus, the Insatiable** - the Den of Tantalus (Styx marsh border, Act 4). TWO FORMS -
    kill him and "Tantalus, the Hunger Unbound" rises; shade waves accelerate as he weakens.
    Soul of the Insatiable (summons a Famished Shade; negative life regen downside) + hoard.
12. **Charon, the Unferried** - the Golden Bough forecourt (Styx river edge, Act 4). TWO PHASES,
    ~60k total; drowned-oarsman escorts; drops the Soul of the Unferried (raises an oarsman) +
    THE GOLDEN BOUGH amulet + the Ferryman's Toll hoard.
13. **The Mnemophage** - the Pools of Mnemosyne temple underground (Act 4 Judgment). Memory-
    drinking horror; shell-then-core; cooldown-reduction amulet + soul.
14. **Ephialtes, the Waking Dread** - the Dread Halls terminal vault, back corner (Judgment stone
    city). Fear engine; Mask of the Waking Dread + Dread Hoard + Soul of the Waking Dread
    (fear nova; mana-regen downside).

Coming in build37 (already built + vetted, shipping as small builds): The Helepolis, Taker of
Cities (Fields of the Diadochi); Menoetes, Marshal of the Dead (+ the three general upgrades);
the Polis Daemonai vault Guardian (5 majestic chests); Neferkha, the Rimebound Pharaoh (Egypt).

**QA-WATCH (build37, four_generals):** when you fight Hades' three generals, confirm **Trophonios's
archer-muster fires in-game** - he should periodically summon a small squad of crimson Machae
archers (his `specialAttack4`; a redundant `specialAttack5` autocast slot is pre-wired as the
fallback, and the muster is petLimit-3 / TTL-20 so it never swarms). If no archers ever appear
while Trophonios is engaged, flag it (the muster slot did not fire).

## B. SV AREAS - what exists and how to get there

TESTED BY WILL: the blood cave complex (walkable end-to-end; widow quest, exploding-wall secret
area w/ mega chest, waterfall chamber, nest).

NOT YET TESTED - reach all of these via the **HELOS TRAVELER HUB** above (DEV/TESTHUB map). The
invented walk-through doors that used to enter them were REMOVED 2026-07-12 (walk-through teleports
are banned; a walk-through to the Garden with no way back was a live Steam bug):
1. **Uber Dungeon / Obsidian Halls** (roulette + 4 wardens) - "Traveler: The Obsidian Halls".
   🆕 The interior itself (`crypt_floor1`) is now ENTERABLE: at the Knossos->Uber door, talk to
   the return traveler standing there (`svc_area_return_uber`) and pick "Enter the Uber Dungeon".
2. **Sparta Crypt L2** - "Traveler: The Sparta Crypt". 🆕 The crypt itself (`spartacryptlevel2`) is
   now ENTERABLE: at the Athens catacomb door, talk to the return traveler standing there
   (`svc_area_return_sparta`) and pick "Descend into the Sparta Crypt". Its own return traveler
   inside sends you back to this same catacomb door (primary) or Helos (secondary).
3. **Garden of Merchants** - "Traveler: Garden of Merchants". (The old first-cave portal NPC is on
   Will's removal list; the Garden is now reached via the hub, not that NPC.)
4. **Secret Place** - "Traveler: The Secret Place". The crow-hero bosses (Murderbunny, Zilla, etc. -
   big souls) are placed in these interiors.
5. **Boss arena** (SV questline area) - "Traveler: The Boss Arena".

NOT REACHABLE YET (no canonical entrance - the SV-areas campaign is the standing backlog item):
several deep SV interiors whose bosses/souls are wired but unreachable canonically (Blood-Witch
priest areas, parts of urder). The TESTHUB portals reach the test targets on DEV.

NOT BUILT: Cold Tombs (empty shell upstream; the Neferkha set-piece replaces it in build37).

## C. BUILD36 HEADLINE TEST MENU (beyond bosses)
- Summons: speed/stats/gear/skills all mirror the wild forms (Stygian Replicator's skills work;
  Xeiwang has NO gear - correct per the parity law).
- Meritamen the Shadowcaller soul summons MERITAMEN (who summons shadow stalkers for you).
- The white spider (Phantom Weaver) drops its OWN soul; Leveler/Stygasia/Tyrnaios soul floods gone.
- Ground Smash only on the 6 lore-true souls; Shadow Stalker petrifies packs (AoE) again.
- Flash Powder: real damage + ranged blind, 6s CD (Occult) / 10s (soul). Bloodcrow Flame Nova 4s;
  Makaria Venom Cloud 8s; Anapaest Earth Fury 5s. Soul of the Eldest physres now 30/45/60.
- Vort the Red IS RED (wild + summon). Soul descriptions render in-game now (114+ souls).
- Rune Golem: button on the Runemaster tree above Menhir Wall, summonable, renders.
- 18 new mastery skills across 6 trees (Slam, Lightning Dash, Doppelganger, Fire Nova, ...).
- Post-Hades: NO "Portal to the North" - a Victory Portal instead; USING IT SHOULD UNLOCK EPIC
  (the one engine-runtime unknown - please confirm). Your existing post-Hades char self-heals.
- Evocative soul names restored (e.g. "Soul of Anapaest the Dishonored").

## D. DEV BUILD vs STEAM BUILD
Same database, text, and quests (byte-identical). Differences:
- **DEV (SoulvizierClassicDEV)**: deployed directly by the assistant (instant, pre-Steam); may
  carry the TESTHUB map variant = local-only test portals at the blood-cave entrance + the
  monster yard; separate caravan/stash namespace (its own storage).
- **STEAM (Workshop item 3759792705)**: the public build; CANONICAL map only (TESTHUB is never
  uploaded); updates via packaged upload + Steam sync (restart Steam to pull).
