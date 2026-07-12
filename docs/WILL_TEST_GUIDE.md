# WILL'S TEST GUIDE - build36 bosses + SV areas (2026-07-12)

> Fastest test path: play the **DEV entry** (Custom Quest -> SoulvizierClassicDEV). Its TESTHUB
> map variant adds LOCAL-ONLY portals at the blood-cave entrance to every test target, plus the
> **monster test yard** where the custom bosses spawn at 100% for point-blank testing. The Steam
> build has none of that (canonical map only). Kill TQ + restart Steam before testing (files lock).

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

## B. SV AREAS - what exists and how to get there

TESTED BY WILL: the blood cave complex (walkable end-to-end; widow quest, exploding-wall secret
area w/ mega chest, waterfall chamber, nest).

NOT YET TESTED (canonical entrances exist - see docs/DOORS_HUB_LOG.md for exact door spots):
1. **Uber Dungeon / Obsidian Halls** - the invented door in KNOSSOS (build24). The roulette +
   wardens live here.
2. **Sparta Crypt L2** - the invented door in the Athens-battlefield crypt (build25).
3. **Garden of Merchants** - portal pair; the entrance NPC currently stands in the FIRST CAVE on
   the way to the blood cave (⚠️ Will has ordered this NPC removed - test the area BEFORE the
   removal ships, or via TESTHUB after).
4. **Secret Place** - portal pair entrance (see DOORS_HUB_LOG). The crow-hero bosses (Murderbunny,
   Zilla, etc. - big souls) are placed in these interiors.
5. **Boss arena** (SV questline area inside the blood-cave complex questlines).

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
