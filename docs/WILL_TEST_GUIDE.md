# WILL'S TEST GUIDE - build37-dev bosses + SV areas (Helos traveler hub; deployed to DEV 2026-07-13)

> ## NOW LIVE ON DEV: build37-dev (2026-07-13)
> The **SoulvizierClassicDEV** entry now runs **build37-dev** - the TESTHUB map with the full **Helos
> traveler hub** (17 talk-to-travel NPCs / returns) over the first full-registry database (the build36
> uber bosses PLUS the new registry bosses and the Occult/Hunting improvements). **Steam is untouched**
> (still build36a canonical - this hub is DEV-only and is never uploaded). Deployed + md5-verified on
> disk: `Levels.arc` `841c56cd`, `arz` `56d6db22`, `Text.arc` `8c7229db`, `Quests.arc` `838bdc3a`.
> **To load it: fully quit TQ if it is open, then start TQ fresh** (Steam was already restarted today,
> so no Steam restart is needed; the deploy landed while TQ was closed).

> Fastest test path: play the **DEV entry** (Custom Quest -> SoulvizierClassicDEV). Its TESTHUB
> map variant adds LOCAL-ONLY **traveler NPCs** (talk-to-travel, boat-dialog) - a **HELOS TRAVELER
> HUB** with one named person per test target (see the next section) plus the **monster test yard**
> in Hidden Valley where the custom bosses spawn at 100% for point-blank testing. The Steam build
> has none of that (canonical map only). Fully quit + restart TQ before testing so it loads the fresh
> files (Steam was already restarted today, so no Steam restart is needed).

## HELOS TRAVELER HUB (DEV / TESTHUB map only) - one traveler per area

In the **Helos starting-town plaza** (where you begin a Custom Quest char) stand **11 named
travelers**, arranged in two rows just south of the town-portal shrine. Each is a "talk-to-travel"
NPC: **walk up, talk, and a boat-dialog asks you to confirm the destination** - then it teleports
you. This is the ONLY travel mechanism (the old walk-through teleport doors were removed 2026-07-12;
**if you are EVER teleported just by walking, that is a bug - report it**).

Front row (established areas):

| Traveler NPC | Destination | What to verify on arrival |
|---|---|---|
| **Traveler: Garden of Merchants** | Garden of Merchants | land in the merchant hub by the caravan_rhodes Super-Caravan |
| **Traveler: The Secret Place** | darkforestenter (forest cluster) | the crow-hero bosses (Murderbunny, Zilla) live in these interiors |
| **Traveler: The Sparta Crypt** | SpartaCryptLevel2 | the invented Sparta crypt arena |
| **Traveler: The Obsidian Halls** | crypt_floor1 (Uber Dungeon) | the Obsidian Halls roulette (4 corners) + the 4 wardens |
| **Traveler: The Boss Arena** | boss_arena | the SV boss-arena (Satyr Shaman) questline area |
| **Traveler: Blood-Cave Warband** | drxfirstxistion_connection | the Enslaver warband set-piece (Toxeus Enslaver leader + marauders) |

Back row (the 5 new Immortal-Throne superbosses - build36):

| Traveler NPC | Destination | Boss to test |
|---|---|---|
| **Traveler: Medea Tomb (Dorus)** | Medea_TempleUG_Tomb01 | **Dorus, the Drowned King** (Propontis) + Hoard |
| **Traveler: Den of Tantalus** | Styx_SwampBorder_01 | **Tantalus, the Insatiable** + hoard |
| **Traveler: Golden Bough (Charon)** | Styx_RiverEdge_01 (forecourt) | **Charon, the Unferried** (2-phase) + hoard |
| **Traveler: Pools of Mnemosyne** | Judgment_TempleUG_Mnemosyne01 | **The Mnemophage** (2-phase) |
| **Traveler: Dread Halls (Ephialtes)** | Judgment_StoneCity_Exit01 | **Ephialtes, the Waking Dread** (fear nova) |

**Getting back:** every destination has a way back, but note one TESTHUB limitation on the older areas.
- The **6 NEW areas** (the 5 IT superbosses + the Blood-Cave Warband): each has its OWN **Return
  Traveler** record placed a few steps from where you land -> talk -> confirm -> back to the Helos
  plaza. These are distinct records, so every one binds and works.
- **Garden / Secret Place / Uber / Sparta / Boss Arena**: these 5 established areas currently SHARE a
  single `svc_testhub_return` record placed once in each. By the **WARDEN LAW** (only the FIRST
  placement of a given record binds; the engine leaves the duplicates MUTE), expect only ONE of these
  five return NPCs to actually respond - the others render but may do nothing. The Garden and Secret
  Place also keep their SV rift-shrines. **Universal fallback: a TQ Town-Portal scroll returns you to
  town from ANY area**, so use one if a return NPC is mute. Splitting these into one distinct return
  record per area (so all five bind) is deferred to the b37 map pass.

**Hub verification checklist:** (1) all 11 travelers are present + individually clickable (no two
stacked); (2) each teleport lands you standing on solid ground (on-mesh), not in a wall/void; (3)
from each of the 6 NEW boss areas the Return Traveler brings you back to Helos (the 5 established
areas share one return record, so only one binds - keep a TQ Town-Portal scroll as the universal
fallback); (4) NO walk-through teleports anywhere - travel only happens after you talk + confirm.

### Where the old walk-through doors were (removed 2026-07-12; reach these via the hub now)

Will asked for the exact door walk-to spots. These invented walk-through doors were deleted by the
P0 hotfix (a walk-through that yanked you to the Garden with no way back was a live Steam bug), so
walking to these spots now does nothing - use the hub travelers above. For the record:
- **Knossos -> Uber Dungeon door**: was in the **Minotaur's Labyrinth (maze03)**, beside the SV
  Olympian-arena portal, at **world (-7783, 1, -3794)** = maze03-local (293.1, 1.2, 149.3).
- **Athens -> Sparta Crypt door**: was in the **deepest Athens catacomb (CataCube02_FloorLast)**,
  near the **stairs-down** landmark, at **world (-6583, 1, -3177)** = local (29.1, 1.2, 41.3).

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
2. **Sparta Crypt L2** - "Traveler: The Sparta Crypt".
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
