# WILL'S TEST GUIDE - build40-dev bosses + SV areas (Helos traveler hub; deployed to DEV + DEV2 2026-07-14)

> # 🦅 R-256 THERE IS SOMETHING AT THE END OF LOOKOUT CAVE NOW (2026-08-15)
>
> **✅ SHIPPED AS `build100` - LIVE ON YOUR DEV SURFACE *AND* ON STEAM (2026-08-16).** arz
> `6b89bb5d`, Text `1be898a0`, canonical map `08f3639e`, your DEV TESTHUB map `821ceaa9`;
> Workshop ManifestID `5905234666463375389`. **Full quit of TQ and a Steam restart first**, so
> the new database and the new map both load.
>
> **He is placed in the WORLD, not in the test hub** (`BL-R256-DEBT-3`, deliberate) - there is no
> yard proxy and no portal to him. You have to walk the cave.
>
> **Your order, verbatim:** "we should add a uber boss (a new unique one) at the end of lookout
> cave in the area outside the back of the cave that you get through after you walk through the
> whole cave, it is a dead end."
>
> ## How to walk there
>
> 1. **Act 2, Rhakotis.** Find the cave mouth in **Rhakotis03**, in the cliff face.
>    **Do NOT look for a "Lookout Cave" banner at the entrance - there isn't one, and an earlier
>    draft of this guide wrongly told you there would be.** I measured every one of the 2,282
>    levels: Rhakotis03 reads *City of Rhakotis / Rhakotis Slums / Rhakotis Library*, and the two
>    cave rooms carry no region at all. **"Lookout Cave" appears only when you come OUT the far
>    side** - Rhakotis05 is the single level in the entire world bound to that region. So the
>    banner is not how you find the cave; it is your confirmation that you found the right one.
> 2. **Walk the whole cave.** Two rooms, in and through.
> 3. **Come out the far side.** The banner flips to **Lookout Cave** and you step onto a cliff
>    terrace roughly 20 units above the desert. It is a genuine dead end - there is no path down
>    and no path on. You can only come out of the cave onto it, and walk back.
> 4. **He is about 17 units out from the mouth**, and he stands about 11 units to the near side of
>    the vanilla dune-raider camp (see the note below). You will see the nest before you see him:
>    animal bones, refuse piles and an urn dragged up out of the cave. That is deliberate. The
>    shelf is a larder, and the dressing is what he carried up.
>
> ## What you are fighting
>
> **{^r}Ushkaret, the Sky-Burial** - and the thing worth knowing is what he *is*: **the first
> Boss-rank BIRD in the game.** We checked every one of the 5,075 monster records; the vulture
> family has 9 commons, 5 champions and 5 heroes and has never had a boss. The only red uber on
> any flying body at all was a level-17 bat. The sky over Rhakotis is already full of his children
> (the vultures you have been killing all act); nothing was ever at the top of it.
>
> He wears a skin exactly one other creature in the database wears - the Corpsewake hero - so the
> corpsewakes read as his brood, and he is about **2.7x** the size of a normal vulture.
>
> **The fight has three beats:**
> - **He does not land.** He opens by raking a fan of quills across the shelf, and closing on him
>   costs you blood (he retaliates passively). No other uber in the mod opens this way.
> - **Then he stoops.** He folds and comes down on you as an area slam. **No red uber in this mod
>   has ever left melee range vertically** - this move exists on exactly three records in the whole
>   game, all of them the vanilla Charon, and Charon is not even in this mod any more (Akremon
>   replaced him). On the ground he bleeds you and drains you.
>   *(Tuning note, because it changed late: the stoop is set to the same power row vanilla's
>   weakest Charon uses, not a higher one - an earlier draft had it inheriting a level meant for a
>   different skill and hitting roughly 6x harder than intended on Normal. And his mana pool was
>   raised so he can actually keep using it; at the old value he could stoop twice and then stood
>   there. If the stoop feels rare or feels brutal, that pair of numbers is where to look.)*
> - **Then he calls the flock,** and when he dies the last quills scatter. **The flock is capped
>   and it expires** - never more than 6 of them at once, and each one fades after 20 seconds.
>   That is deliberate and it is because of *your* P0: the skeleton-dog / tomb-guardian freeze you
>   filed ("the infinite summon ... the game is frozen"). The body I built this summon from ships
>   with a cap but **no expiry at all**, which is exactly the bug you hit, so I added the expiry
>   and put a build gate on it. They are all plain commons - he never calls champions, so the
>   screen does not fill up.
>
> **Counterplay, so it is legible:** he leeches life from everything near him and he bleeds you
> hard, so **bleed resistance is the stat that matters**, and killing the two Cliffside Mourner
> champions out at the rim is better than fighting all three in the middle. He cannot be bled
> himself - he is the larder.
>
> ⚠️ **One thing to actually watch for, because it was broken until the last review and you are
> the one who would see it.** The leech aura is a custom one - a much wider, stronger version of
> the stock vampiric aura, and it is the whole idea behind his name. Until this round it was wired
> into a slot the engine does not read for that, so he would very likely have used the plain stock
> aura instead and none of the custom tuning would have reached you. It is now wired into the two
> channels that actually fire. **If it feels like he barely drains at all, or like he only drains
> when you are right on top of him rather than most of the terrace, tell me** - that is this exact
> bug coming back, and it is the difference between "the Larder" and "a big vulture".
>
> **Difficulty:** deliberately inside the band you already know. His health is 14,000 / 19,000 /
> 26,000 across the three difficulties, which sits between the Coin-Drowned King and Ephialtes.
> **Hard, but killable, and no wall.** If he feels like a wall, say so - that is a bug, not a
> design.
>
> ## What he drops
>
> - **The mystical orb**, like every other red uber (the Egypt-band one, same as Neferkha).
> - **ONE chest.** One. It stands on the shelf beside him and unlocks when he dies -
>   **The Larder of Ushkaret**. (That name is mine, not yours - tell me if you want it changed.)
>   It opens its own dedicated loot table, not a base-game one.
> - **{^F}Soul of the Sky-Burial** (66% drop, Normal / Epic / Legendary versions with those words
>   in front of the name, as they should be). The soul is a **manual summon button** - "Give It to
>   the Sky" - that raises **The Patient Wing**, a permanent bird of your own on his exact body. It
>   is not a Ground Smash filler and it is not an on-hit proc. The soul's own stats are bleed,
>   life-leech and pierce, and it carries a real cost: it opens your own hide, so you take more
>   pierce and bleeding damage while you wear it.
>
> ## ⚠️ One thing I have to be straight about
>
> The design I wrote said his aura should **eat the bleed** - that anything hemorrhaging on the
> shelf, including his own flock, would feed him. **The engine will not express that.** I measured
> the aura shape it would have to use, and there is no conditional-on-target-state channel in it at
> all. What actually ships is a **wide, strong life-leech aura** (its reach went from 8 to 14 units,
> so the whole shelf really is his plate) plus his bleed and his leech strike. The fight still reads
> "he feeds while you bleed" and bleed resist is still the counter - but it is a leech aura, not a
> bleed-conditional feed, and I would rather tell you that than let you find out.
>
> Two smaller ones: he does **not** sit still pretending to be a carcass until you walk in (I wanted
> that; a spawn proxy always produces a live monster, so there is no dormant state to use), and
> there is **no test-hub shortcut to him this wave** - you walk the cave.
>
> ## ⚠️ And one more: THE SHELF WAS ALREADY OCCUPIED, and I only found out on the second pass
>
> **The base game has always had a small encounter and a chest up there, and I did not know that
> when I wrote the first version of this page.** I went and read the actual base-game database. The
> record is `08_RhakotisLookout` and it is live, not scenery:
>
> - **1 to 3 sandvipers**, and a **55% chance of one champion** - usually a mounted marauder, with a
>   small chance of one of five named Egypt heroes (Ammet, Satef, Udje, Morloc, Hazur).
> - **A golden chest**, in Normal / Epic / Legendary versions. Vanilla's, not mine.
>
> **So when you clear that terrace you will find TWO chests: my Larder, and the base game's golden
> one that has been sitting there since 2006.** That is not a bug and it is not the three-chest
> problem you filed twice - that rule is about *me* stacking chests on one uber, and I still ship
> exactly one. **I chose to leave vanilla's content alone**, because you asked me to add a boss, not
> to delete anything, and ripping out base-game content is your call and not mine.
>
> They do not spawn on top of each other: his ring and theirs are about 11 units apart and do not
> touch. But they are close enough that the raiders will join in, which makes the fight a bit
> busier than the numbers above suggest. **If you want that camp gone so the dead end is his alone,
> say the word and I will clear it** - it is one line in the map lane. That is `BL-R256-DEBT-4`.
>
> **THE TEST:** walk the cave, come out the back. **PASS =** the banner reads Lookout Cave, a
> red-named giant vulture with two champion escorts is standing on the terrace, and when he dies he
> drops an orb, (usually) the soul, and **exactly one chest of mine - "The Larder of Ushkaret"**.
> (The plain golden chest next to it is vanilla's and was always there. Two chests total is the
> EXPECTED result, not a failure.) **FAIL =** empty terrace, two of HIM side by side, two of MY
> chests, a fight that feels like a wall, or **birds piling up until the game chugs** - that last
> one would mean the expiry I added is not firing, and I want to hear about it immediately.

> # 🖤 R-255 THE ENSLAVER'S SUMMONED PETS FINALLY SMOKE (2026-08-15) - READ THIS FIRST (it is LIVE)
>
> **✅ LIVE ON DEV *AND* STEAM AS `build99`** (arz `1113f2c69fc3f188b0b5bece340614f2`, 2026-08-15).
> Full quit TQ and restart Steam before testing.
>
> **Your report, verbatim, and this is the fourth time you have filed it:** "toxeus the murderer
> enslaver of souls summoned pets (when i summon them from their souls) still do not have the black
> smoke around them"
>
> **You were right all four times, and the last three fixes were real code that the game never
> read.** Monster skills live in numbered slots, and the template every monster and pet inherits
> declares slots **1 through 17 and nothing above them**. Across all 74,013 records in the base
> game, no monster and no pet has ever used a higher slot. The previous pass put the shroud in slot
> **19** on the wild Enslaver and slot **18** on all three summoned tiers, on a written-down belief
> that the template went to 23. It does not. 23 was just the highest slot this mod had already
> overflowed into, so that pass measured its own earlier mistake and read it as room to spare. Four
> fields were written and none of them were ever loaded. Everything built on top of them (the
> particle, the attach point, the always-on controllers) was correct and unreachable.
>
> **What it rides now:** the two always-on channels that template actually declares. One casts the
> buff **once at spawn**, so it is on from the first frame and never waits for combat AI. The other
> is the self-buff channel his own controller re-applies whenever possible. Both are ordinary skill
> fields, which is the only class this game's pet records tolerate without crashing.
>
> **The whole family is now checked, not just half of it.** The earlier check covered the boss and
> the three summoned tiers and never looked at the marauders he raises, nor at the marauders a
> SUMMONED Enslaver raises. Those were smoking by luck (their rig has the effect baked into the
> mesh) and a mesh swap could have taken it away silently at any time. The build now walks all eight
> family members and refuses to build unless each one carries the shroud either in its mesh or in
> both fields. On this build: four by mesh, four by fields.
>
> **THE TEST:** summon the Enslaver from **any tier** of his soul and **just stand there, out of
> combat**. **PASS = the black smoke is on him from the moment he appears, and on the marauders he
> raises.** FAIL = he appears clean, or he only smokes while running (that is the old running-only
> effect, which was always there and is untouched).
>
> **Your existing souls are enough.** This effect lives on the pet records, which the game resolves
> from the database at the moment the summon fires. It is not baked into the soul item when you pick
> it up, the way item stats are. So the Enslaver souls already sitting in your stash pick this up
> with no re-drop and no new character. A full restart to reload the database is all it needs.

> # 💀 R-254 DYING COSTS HALF WHAT IT DID (2026-08-15)
>
> **✅ LIVE ON DEV *AND* STEAM AS `build98`** (arz `15dacc68c118f50900a5a7100225e2a8`, 2026-08-15).
> Full quit TQ and restart Steam before testing. The numbers below are what the build actually
> ships - every one of them was re-measured on the deployed DEV bytes, not on a plan.
>
> **Your report, verbatim:** "lets reduce the penalty for dying by another 50% from what it currently
> is at."
>
> **Done - and measured against what you are actually playing, not against the original game.** You
> were already on the -90% penalty from the last pass, so "another 50% from what it currently is at"
> was applied to THAT: **every death now costs exactly half what it costs you today.**
>
> | you are level | difficulty | it costs you today | it will cost |
> | --- | --- | --- | --- |
> | 55 | Legendary | 12,940 XP | **6,470 XP** |
> | 85 | Normal | 6,824 XP | **3,412 XP** |
> | 85 | Legendary | 47,765 XP | **23,883 XP** |
> | 100 | Legendary | 50,000 XP | **25,000 XP** |
>
> **The tombstone still gives back 100% of what you lost.** That was your earlier ruling ("lets make
> the tombstone xp recovery match the xp lost upon dying") and it is the part worth understanding:
> we built it as an **equality**, not as a fixed percentage, precisely so that a change like this one
> could not break it. The game hands your grave the amount it actually took from you, so when the
> penalty halved, the recovery halved with it **automatically - we did not touch the tombstone code
> at all.** Had we hardcoded "10%" back then, this change would have quietly turned dying-and-walking-
> back into a way to GAIN experience. It cannot.
>
> So at level 85 Legendary: you die and lose 23,883 XP, you walk back to your marker, you get 23,883
> XP back. Exactly, on every difficulty, at every level.
>
> **One thing to know:** the high-level cap moved too (50,000 -> 25,000). It had to. The penalty
> grows with the cube of your level, so above roughly level 87 on Legendary you were hitting a flat
> ceiling - and if we had halved the formula but left the ceiling alone, **you would have felt no
> change whatsoever** at exactly the levels you were complaining about. Both moved together.
>
> **THE TEST:** die on purpose at a level you know, note the XP you lose ->
> **PASS = it is half what you are used to.** Then walk back to the tombstone -> **PASS = you get
> back exactly the number you just lost, not half of it.** FAIL = the loss is unchanged (especially
> at high level), or the marker returns less than it took.

> # 🔥 R-253 THE BOSS ARENA NOW ALWAYS HAS ITS BOSS (2026-08-15)
>
> **Your report, verbatim:** "when i went to the boss arena this time there was no boss there. does
> he not spawn 100% of the time? the boss arena needs more work."
>
> **You were right, and it was worse than a random chance - it was three separate things, any one of
> which empties the arena:**
>
> 1. **The boss was spawned by a QUEST STEP, and a quest step only ever fires ONCE per character.**
>    Soulvizier built the arena fight as "walk into the middle -> quest spawns him". Titan Quest
>    saves that step as completed, forever. So the first visit had a boss and **every visit after it
>    was empty** - exactly your "this time".
> 2. **He also had a player-LEVEL window on him** (29-36 on Normal, 41-55 Epic, 60-75 Legendary,
>    inherited from the base game's generic quest-proxy). Outside that band: no boss, even on a
>    fresh character.
> 3. **He was configured as a quest-only spawner** (no spawn chance at all), unlike every boss we
>    place ourselves.
>
> **What changed:** Aithon is now placed in the arena the same way Tantalus, Ephialtes and the
> Devourer are - a real world placement standing on Soulvizier's own centre marker, with **no quest,
> no level window, and a 100% spawn**. The quest's old one-shot spawn is removed so you never get two
> sets of him. **He is there on every single visit, on any character, at any level.**
>
> **Two more things while we were in there (your "needs more work"):**
> - **The arena finally PAYS.** It had literally no loot and no chest in the whole level. Aithon now
>   guards an **Ember-Crowned Hoard** - a Boss-locked chest that unlocks when he dies (one chest, per
>   your "he should only have one" ruling). It keeps its **own** loot table, which guarantees a
>   unique weapon and a relic every time it rolls, rather than being repointed onto the shared
>   base-game boss table behind the five chests you called out that same day ("are you kidding me.
>   this is outrageous").
>   **BE CLEAR ABOUT WHAT THIS IS NOT.** It is not an un-nerfed chest and it is not more loot. It
>   ships at exactly the same trimmed volume as every other hoard chest in the mod - the loot-volume
>   trim covers this new table too. Measured at 1 player: it rolls about **1.1-1.2** times per open
>   against the base boss table's **6.9-7.8**, so it actually drops FEWER items overall. The one
>   thing it really buys you is that the guaranteed unique+relic slot fires on **every** roll
>   instead of 10% of them. So judge it as "does a dedicated boss hoard feel right", **not** as
>   "is this what an ungutted chest feels like" - that question belongs to the separate
>   chest-generosity wave, and if you want this chest carved out of the volume trim, say so and it
>   becomes a ruling.
> - **The ring burns.** The six lights we ringed the fight floor with last time had no fire under
>   them; now each one sits on a real flame, standing on the floor rather than hovering over it.
>
> **THE TEST:** travel to the **Boss Arena** from the Helos hub -> **PASS = Aithon, the Ember-Crowned
> plus his two Ember Satyr Wardens are standing in the middle, every time.** Then: **leave, come
> back, and check he is there AGAIN** (that is the actual bug). Kill him -> **PASS = a chest is there
> and opens.** FAIL = an empty arena on any visit, or two Aithons at once (tell me which).

> # 💰 R-251 THE UBER CHESTS PAY LIKE UBER CHESTS AGAIN (2026-08-14) - the chest fix, build95
>
> **✅ LIVE ON DEV *AND* STEAM as `build95` (arz `694fd88150b37d027dcf6b170c5e1bdb`).** arz-only:
> no map, no quest, no Text and no new item (all four sibling artifacts md5-proven byte-identical to
> build93). Closes `BL-W0814-2`, `-5`, `-7`, `-11` and `-13` - all five of your chest reports, with
> one fix. **Fully quit TQ and restart Steam before testing** (standing rule).
>
> **Your five reports, verbatim:** "are you kidding me. this is outrageous ... literally just dropped
> two items one thing of gold and incarnation of guan-yu's grace" (Propontis) / "same problem with the
> chest guarded by tantalus" / "aphoryteus (spelled wrong) dread hoard is a terrible chest, it got
> nerfed somewhere along the way and needs to drop more items" / "the obsidian hoard chests ... are
> still nerfed too much. if these share the same record as the chest - toxeus the murderer, devourer
> of blood hidden's chest we need to seperate those records" / "the gift box in the secret places need
> to increase the number of items dropped by 3x".
>
> **You were right that it was one thing.** It was not a tuning number - it was a WIRE. Back in b42 a
> finalization pass quietly repointed every uber chest at the BASE GAME's ordinary boss-chest loot
> ("the Cyclops chest"), and left each boss's own hand-tuned hoard table sitting there unreferenced.
> Measured on the build you played: **21 of 30 uber chests were opening a base-game table, and 18 of
> the 27 bespoke hoard tables had ZERO references anywhere in the database.** So the three waves of
> chest work you approved (every weapon class, armour parity, spear included) were being applied to
> records no chest actually opened - which is exactly why every one of these chests felt gutted, and
> why the gates all looked green.
>
> **Your obsidian/Devourer suspicion was also right, with one correction.** The chest in the **Great
> Hall of Propontis** is a clone of the **Obsidian Hoard** chest - it USED to share the Obsidian
> Hoard's loot record, and it is still LABELLED "Obsidian Hoard" in game (that label is a separate
> follow-up, `BL-R251-DEBT-2`). It never shared with the Devourer's stash - that one has been on its
> own records the whole time, and its R-247 revert is untouched here.
>
> **What changed this build:**
>
> 1. **Every uber/boss chest opens its OWN hoard table again** (Tantalus, Charon/Golden Bough,
>    Ephialtes's Dread-Hoard, Propontis/Dorus, the Obsidian hoards, the Mnemophage, the Helepolis, and
>    the three general-guard hoards). Each one is a SEPARATE record, so they can be tuned
>    independently from here on - and each carries its **guaranteed 100% unique + relic slot** back,
>    which the base-game table did not have.
> 2. **The Propontis chest got its own loot records** for the first time (it had none, which is why it
>    fell back on the Obsidian chest's).
> 3. **The uber hoards came back out of the R-240 volume trim.** That trim was for the polis-vault
>    cage farm you asked to cut back; it had swept the one-per-world uber chests along with it. They
>    are back at their authored volume, still BELOW the Devourer's stash so the blood-cave mega chest
>    stays the best chest in the mod. **The polis-vault cage is unchanged** - you asked for that trim
>    and it stands.
> 4. **The Secret Present gift box drops 3x the items**, exactly as asked. There are five of them
>    across the secret-place levels (Dark Forest entrance, Secret Forest, Pillaged Village), which is
>    why you saw them in more than one place.
> 5. **A second Obsidian bug turned up while checking the first, and is fixed here too.** The
>    **Epic and Legendary Obsidian Hoards were guaranteeing a NORMAL-tier (Essence) relic** - the
>    lowest tier, on the hardest difficulties. It is the same mistake you caught on 2026-08-08 in the
>    general-guard hoards; it had been left in the Obsidian chests' builder as well, and it stayed
>    invisible because the checker follows the chest wiring and those chests were pointed at the
>    base-game table. Fixing the wiring is what exposed it. Epic hoards now guarantee an
>    **Embodiment**, Legendary an **Incarnation**.
>
> **THE TEST:** open, on Legendary if you can:
>   * the **Great Hall of Propontis** chest (behind Kroisos the Coin-Drowned),
>   * the **Den of Tantalus** chest,
>   * **Ephialtes's Dread-Hoard** in the Dread Halls,
>   * an **Obsidian Hoard** in the Obsidian Halls,
>   * a **gift box** in a secret place.
>
> **PASS =** each uber chest pays a real handful - a guaranteed unique weapon and a tier-correct relic
> plus several more rolls - not "gold and one relic". The gift box should visibly pay about three
> times what it used to. On an **Obsidian Hoard specifically**, check the guaranteed relic's tier: on
> Legendary it must be an **Incarnation**, on Epic an **Embodiment**. An Essence there means item 5
> did not land. **FAIL =** any of them still pays 1-2 items; say which chest and on which difficulty
> and it is a one-line fix now that each has its own record.
>
> **Not in this change (on purpose):** the polis-vault cage chests, every Mystical Orb (those are the
> R-242 rates you already ruled on), and the Devourer's stash (already reverted in R-247). With the
> single exception of the Obsidian relic tier in item 5, nothing about WHAT the chests can pay
> changed - only whether the tuned table is the one that opens, and how many rolls it gets.


> ## 🆕 R-250 (2026-08-11): THE ENSLAVER OF SOULS NOW WEARS HIS DEMONS' BLACK SHROUD, ALL THE TIME
> **✅ LIVE ON DEV *AND* STEAM as `build93` (arz `db31414339f008792ea03aa8531f5002`).** arz-only:
> no map, no quest, no Text, no mesh and no texture change (all four sibling artifacts md5-proven
> byte-identical to build92). Closes `BL-W0814-1`, your third filing of this sentence.
> **Fully quit TQ and restart Steam before testing** (standing rule).
>
> **First, the name.** You wrote *"toxeus the murderer, devourer of souls"*. There is no Devourer of
> Souls - the mod has a **Devourer of BLOOD** and an **Enslaver of SOULS**. What decided it was your
> other clause, *"the same one that his demon summon guys have"*: the **Enslaver's** shadow marauders
> wear that black shroud (you confirmed it yourself - *"the demons that he summons have the proper
> black shroud"*), while the **Devourer's** minions are Blood Demons with red blood effects and no
> shroud to copy. So this went on the **ENSLAVER OF SOULS**. If you meant the other one, say so - it
> moves in one line.
>
> **Why you were right to file it a third time.** His demons' shroud is not a setting we could copy;
> it is **built into their model**, which is why they smoke constantly, even standing still. What he
> had instead was (a) smoke that only plays while he is RUNNING, and he is a caster who stands still,
> (b) a version that only switched on once a fight started, and (c) both of those came out of his
> **hands**, not from around him. On top of that, the fix that removed his green glow last week moved
> him onto a model with no built-in smoke at all - so he ended up with nothing. All three are fixed.
>
> **THE TEST - two places, because there are two of him:**
> 1. **The summon.** Summon the Enslaver and just **stand there, out of combat, doing nothing**. That
>    is the whole point of this fix: black smoke should be wrapping his body **immediately and
>    constantly**, not only once something attacks. Compare him side by side with his own Enslaved
>    Shadow Marauders - it should be the same smoke.
> 2. **The world boss.** Fight the Enslaver of Souls himself; same look, standing and moving.
>
> **It is literally their smoke, in their spot.** Not a lookalike: he now carries a copy of the demons'
> own effect entry, field for field, hung on the **same attach point their model uses** - which his
> skeleton turns out to have too, in the identical place. So standing side by side, he and a marauder
> should be wearing the same thing.
>
> **WHAT TO WATCH FOR, honestly flagged:** nobody has seen this in game - your eye is the only test
> that counts. The one thing worth reporting: is it **too thick / always-on annoying** now that it never
> switches off. That is a one-line change.
>
> **NOT CHANGED, on purpose - and one of them is a question for you:**
> - The **Devourer of Blood** has **no shroud either** (his only effect is two small black-poison puffs
>   on his hands). We did not touch him, because you did not ask and crimson is his design.
>   **Do you want him shrouded too, and in what colour?**
> - The **Endless Hunt** already has this smoke built into his model. Nothing to do.
> - **Toxeus, End of All Things** (the crafted supra pet) - still your call whether he gets his own look.

> # ⚔️ R-252 TOXEUS BOSS EQUIPMENT (2026-08-15) - the Hunt gets dressed, the Devourer drops the bow
>
> **✅ LIVE ON DEV *AND* STEAM as `build96` (arz `0bd0121f36e5ce7bd205c73e588016ae`).** arz-only:
> no map, no quest, no Text and no new item (all four sibling artifacts md5-proven byte-identical to
> build95). Closes `BL-W0814-3` and `-9`; **`BL-W0814-10` (the soul) is NOT closed** - see the
> STILL-OPEN block below. **Fully quit TQ and restart Steam before testing** (standing rule).
>
> **Your three reports, verbatim:** "toxeus the murderer the endless hunt is not wearing any equipment
> and i dont think he has a weapon" + "toxeus the murderer devourer of blood is using a bow which
> makes no sense" + "i killed toxeus the murderer devourer of blood and he did not drop his soul even
> though he should have 100% chance of dropping his soul."
>
> **What was actually wrong (measured in the shipped build, not guessed):**
>
> - **The bow was real.** In this engine the LEFT hand is the shield / two-handed-ranged slot. I
>   counted every base-game monster (all 5,556 of them): **805 carry a shield in the left hand and
>   exactly ZERO carry one in the right**; bows ride the left hand **514 times against 17** on the
>   right, and those 17 are all the same handful of hand-less things (rot piles, creeping slimes,
>   earth elementals) using the slot as a plain drop chute rather than as a hand - which is precisely
>   the mistake this fix removes from the Devourer.
>   The Devourer's left hand was pointed at a "high bleed gear" pool that had been picked by AFFIX
>   instead of by weapon type - and one of its three entries on Normal and on Legendary is a BOW. So
>   he equipped one and fought as an archer. The bows are now removed from that pool outright.
> - **And while I was in there I found something you did NOT report: he was often standing there with
>   NOTHING in his sword hand.** His weapon hand was pointed at his 4-piece Crimson Verdict set
>   table, and 3 of those 4 entries are ARMOUR - a helm, a cuirass, an armband. The engine cannot put
>   a helm in a hand, so **63% of Devourer spawns in the shipped build had an empty weapon hand.**
>   That is the same bug you filed against the Endless Hunt, on the boss you only mentioned the bow
>   for. Fixed: **his weapon hand now only ever rolls one-handed melee weapons, so he is armed 100%
>   of the time** - about **72%** of spawns it is his own **Vein Render**, the rest a bleed-affix axe
>   or a unique sword. His off hand holds a **shield about 86%** of the time; the other ~14% is the
>   Crimson Verdict set roll, which still DROPS the set piece for you but leaves that hand bare. So:
>   **always a weapon, usually a shield** - if you catch him without a shield once in a while that is
>   expected, and it means a set piece just dropped. If you ever see him with an empty WEAPON hand,
>   or a bow, that is a bug - tell me.
> - 🔴 **A NERF YOU DID NOT ASK FOR, AND I NEED YOU TO RULE ON IT.** Moving that set table out of his
>   sword hand is what fixes the empty hand, but it also makes the set **6.1x harder to farm**, and
>   that table is the **only** place those pieces drop in the entire game. Per kill of the Devourer:
>
>   | Crimson Verdict piece | before | now |
>   |---|---|---|
>   | helm | 21.0% | **3.4%** |
>   | cuirass | 21.0% | **3.4%** |
>   | armband | 21.0% | **3.4%** |
>   | Vein Render (the sword) | 21.0% | **72.5%** - and he actually wields it now |
>
>   The sword got much commoner; the three armour pieces got much rarer. **I did not "fix" this back
>   on my own, because every way to do it is a balance call on content you designed:** his only free
>   equipment slot is his head, and using it would mean he visibly wears the Crimson Verdict helm
>   about 1 spawn in 4 (that would actually give the BEST rate, 25% a piece, and costs nothing else);
>   the alternatives are hanging two of the three pieces on his chest/arm rolls (the helm still has
>   nowhere to go), or fattening the off-hand row and giving up most of the shield. **Tell me which
>   you want and it is a one-line change** (`BL-R252-DEBT-7`). If you would rather leave it as is,
>   say so and I will mark it ratified. Until then the build has a gate that refuses to let this
>   number move again without telling you.
> - **The Hunt really was naked - but he DID have his spear.** His record had no torso, legs or arm
>   equipment fields at all, and his ring/potion/relic/amulet slots were all switched off. His spear
>   was fine the whole time (right hand, 100%, the Runbreaker) - spears ride the right hand **493-to-0**
>   in the base game - so what you were seeing was a spearman in no armour. He now wears **torso,
>   greaves and armbands at 100%** from his own loot bracket, plus the ring / potion / relic / amulet
>   rolls his two brothers have. He stays **bare-headed on purpose** (so does the Enslaver and so does
>   the Devourer - that skull is deliberate) and carries no shield (his spear is two-handed).
> - **The soul: his 100% is genuinely still set.** I re-read the shipped bytes: the Devourer's soul
>   chance is 100%, the soul item exists, it is a proper ring, and there is exactly ONE Devourer
>   record in the game with every spawn pointing at it - so it is not a "wrong copy of the boss"
>   problem. The one thing that WAS wrong on his record and on nobody else's in the family is the
>   cross-wired hands above, which is the same system the soul is equipped through. That is now
>   clean. **I cannot prove from the files that this was the cause, so this one closes on your next
>   kill, not on my gate** (BL-R252-DEBT-1). If it still does not drop, tell me and I move the soul
>   onto the drop channel that provably works in-game (the same one that delivered your End of All
>   Things formula).
>
> **STILL OPEN - READ THIS FIRST.** Two of your three reports are fixed with proof in the files. The
> **soul is NOT one of them.** I could not find anything wrong with it, so there is nothing I can
> point at and call the fix. Your next kill is the test. If it still does not drop, say so and I move
> it onto the drop channel that provably works.
> **And one decision is yours, not mine:** the Crimson Verdict armour now drops 6.1x more slowly (the
> red block above). I left it that way deliberately rather than quietly picking a new number for a
> set you designed. Ratify it, or name which restoration you want, and it lands in one line.
>
> **THE TEST (fully quit TQ + restart Steam first):**
> 1. **Devourer of Blood** (blood cave, his stash / the parchment ambush): he must have a **melee
>    weapon in his weapon hand every single time - never a bow, never an empty hand**. A shield in
>    the off hand most of the time (roughly 6 spawns in 7); no shield now and then is expected and
>    means a Crimson Verdict set piece dropped instead. Kill him: **the thing I need to know is
>    whether his soul drops.** FAIL = a bow, an empty weapon hand, or still no soul.
> 2. **Toxeus the Murderer, the Endless Hunt:** he must be **wearing armour** (chest, legs, arms) and
>    still carrying his spear. FAIL = still naked, or the spear is gone.
> 3. **NEW at integration - the SUMMONED Hunt too.** Cast his soul and look at the pet: it must wear
>    the SAME armour the fought one wears. The build caught this on its own and refused to finish
>    until it was fixed: his three soul-pet records copy his gear at the moment they are BUILT, which
>    happens before the armour is written, so the pet was standing there naked while its source wore
>    a full kit - your own report, reproduced on the pet. FAIL = you summon him and he is bare.
> 4. Kill each of them a couple of times if you can - the armour and weapon rolls are per-spawn, so a
>    second look tells us whether it is consistent.

> # 🛠️ R-249 WARDEN FIX + ALMYROS TRIM (2026-08-14) - it amends the R-248 section below
>
> **Your ruling, verbatim:** "no steam should not have a traveler from helos to the secret place or the
> uber place. remove those from the steam build now. no we dont want to do the typhon-style fix, the
> current method we are using is getting much closer, we just need to fix the issue with the warden."
>
> **Two changes shipped this build:**
>
> 1. **ALMYROS is now GARDEN-ONLY (Steam).** Talk to **Almyros in the Helos plaza**: his menu offers
>    **ONLY "Garden of Merchants"** now - **"The Secret Place" and "The Uber Dungeon" are GONE** from
>    his menu, per your ruling. (Those two areas are still reachable other ways - see below.) This
>    change is Steam-only; the TESTHUB plaza launchers for Secret/Uber are unchanged on your DEV map.
>
> 2. **THE WARDEN DESCEND IS FIXED - and it is still the boat traveler, NOT a portal or a door.** Your
>    report was: you clicked the Warden, a "descend into the spartan crypt" popup came up, then the
>    question **vanished before you could click it**, and clicking him again did **nothing**. Root
>    cause: a 2-second delay on the NPC's "wake up" step let a late command **close the descend popup
>    you'd just opened** (you reach the Warden by teleport, so you click within those 2 seconds; the
>    uber-labyrinth traveler dodged it only because you WALK to him). The fix removes that delay
>    (sets it to 0, the base-game boatman value), so the popup can never be closed out from under you.
>    Nothing else about him changed - same name, same spot, same single "Descend into the Sparta
>    Crypt" option, same boat-traveler mechanism.
>
> ### ⚠️ CORRECTION (2026-08-14 night, `build94-dev`): YOUR DEV COPY DID NOT ACTUALLY HAVE THIS FIX UNTIL NOW
> **If you already tried the Warden click on DEV and it still auto-dismissed, that was not a failed fix -
> you were clicking the OLD build.** The Warden fix went to Steam with build92, but your DEV
> `Quests.arc` was never replaced, so it stayed on the pre-fix file (`1764c3a2`) - the exact one you
> were playing when you reported the bug. **That is fixed as of tonight: DEV now has the fixed quest
> file (`90d401f1`), and nothing else on DEV changed** (same map, same database, same everything else -
> md5-verified, 1 file of 62). **So please run the test below again on DEV, fresh.** Steam has been
> correct since build92 and did not move tonight. Sorry for the wasted click.
>
> ### ✅ STILL GOOD ON build97 (re-checked 2026-08-15, nothing deployed)
> Builds 95, 96 and 97 have landed on DEV since that correction, so your `Quests.arc` is no longer
> `90d401f1` - it is now `d9f8c316` (the build97 TESTHUB file). **The Warden fix is still in it.** We
> re-checked by reading your actual live DEV file rather than trusting the build: all 30 of the travel
> NPC "wake up" steps, the Warden's included, now open their menu instantly instead of after the 2
> second delay that was eating your click. Nothing was rebuilt or copied to do this check. **The test
> below is current and still worth running.**
>
> **THE HEADLINE TEST (Steam has had this since build92; DEV/TESTHUB has it as of tonight):** deepest Athens
> catacomb (`CataCube02_FloorLast`) -> click the **Warden of the Spartan Crypt** by the stairs-down ->
> **PASS = the "Descend into the Sparta Crypt" popup opens AND STAYS OPEN until you answer; clicking
> "yes" drops you into the crypt on the floor; clicking him again re-opens it.** Do it on an existing
> char AND a fresh Custom Quest char. FAIL = the popup still auto-dismisses, or he goes mute. Also
> re-test the **Labyrinth -> Uber Dungeon** traveler the same way (it shared the same latent timing).
>
> **Reachability check (Steam), now that Almyros dropped Secret + Uber:**
> - **Uber Dungeon:** still entered from the **Labyrinth of Knossos** - kill the Minotaur Lord, through
>   the secret door, click the pocket traveler -> "Enter the Uber Dungeon". (Same fix as the Warden.)
> - **Secret Place:** reached from the **Garden of Merchants** (Almyros's kept Garden route) via the
>   native shrine/rift network. ⚠️ If you find the Garden rift will NOT take you INTO the Secret Place
>   (only back out), tell me - there is a registered follow-up to add a dedicated Secret-Place entrance
>   traveler (BL-R249-DEBT-1); it could not be confirmed from the files alone.

# WILL'S TEST GUIDE (continued)

> # 🚢 R-248 PROVEN-MECHANISM TRAVEL (2026-08-14) - READ THE R-249 SECTION ABOVE FIRST; this section is otherwise current and SUPERSEDES the R-246 device section and every travel section below
>
> **Your ruling is implemented verbatim:** "why cant we just get the npc traveler to work as
> intended or the portals like the one that you use to travel after you kill typhon to get to
> rhodes... the traveler to take you to the garden of merchants works why cant we just use that
> design." The R-246 doors + rift shrines are GONE from both maps (they lagged and broke the
> game - that device class is permanently graveyarded). Travel is back to the TWO designs you
> named, both proven in our mod:
> - **THE BOAT-TRAVELER DESIGN** (the Almyros/Garden pattern): click a named traveler ->
>   travel menu -> pick a destination. The FIX under the hood: the old rig re-registered ~39
>   routes on EVERY level load (that churn is what corrupted the travel registry - wrong
>   labels, other rows firing, the mute Warden). The restored routes arm ONE-SHOT, exactly the
>   way the base game arms its Athens/Knossos/Egypt boatmen: registered once per character,
>   max 2-3 per step, never on a re-firing step. The corruption mechanism is structurally gone.
> - **THE FIXED-PORTAL DESIGN** (the post-Typhon -> Rhodes pattern): unchanged, untouched -
>   the Olympus summit portal + the Keryx herald both stay exactly as you know them.
>
> **CANONICAL (ships to Steam) - the routes:**
> 1. **Helos -> Garden:** Almyros's menu - GARDEN ONLY since R-249 (Secret + Uber removed; see the
>    R-249 section above). Uber is reached from the Labyrinth (route 2); Secret from the Garden rifts.
> 2. **Labyrinth -> Uber Dungeon:** the "Enter the Uber Dungeon" traveler in maze03's treasure
>    pocket (behind the Minotaur Lord's secret door, at the corrected R-245 spot) has his MENU
>    BACK - one route, into crypt_floor1.
> 3. **Uber Dungeon return:** the in-crypt return traveler - menu: "The Labyrinth Door
>    (Return)" (back to the maze03 pocket) or Helos.
> 4. **Catacombs -> Sparta Crypt (THE HEADLINE):** the Warden of the Spartan Crypt (deepest
>    Athens catacomb, by the stairs-down) has his DESCEND MENU BACK - one route, down into the
>    crypt. See the walk list: HIS CLICK IS THE WHOLE TEST.
> 5. **Sparta Crypt return:** the in-crypt return traveler - "Athens Catacomb (Return)" or Helos.
> 6. **Garden / Secret Place returns:** their in-area return travelers - Helos or Blood Cave.
>    (Garden/Secret ENTRY stays Almyros + the native shrines/portal-dudes, untouched.)
> 7. **Olympus -> Rhodes:** the portal you named. Untouched.
>
> **TESTHUB (your DEV map only, never Steam):** the 14 plaza travelers are BACK in the Helos
> plaza at their spread-out spots (>=4.1u apart; the east-field portal court is gone), one
> named person per area: Garden, Secret, Sparta(catacomb door), Uber(labyrinth door),
> BossArena, Warband, Dorus, Tantalus, Charon, Mnemophage, Ephialtes, Devourer, Vashkarr,
> Obsidian. Each boss area has its in-area "Helos (Return)" traveler again (devourer's is back
> at its proven spot). NOTE: the TESTHUB build arms 51 routes vs Steam's 26; it stays
> LOCAL-ONLY until a registry-capacity probe clears the bigger number - by design, not an
> accident.
>
> **YOUR WALK LIST (in priority order - the registry fix cannot be proven offline):**
> - (1) **THE WARDEN CLICK, existing character:** catacombs -> click the Warden -> his dialog
>   MUST open -> "Descend into the Sparta Crypt" -> you land in the crypt ON the floor. He was
>   the cross-binding victim; under one-shot arming his dialog should finally bind. This
>   single click is the best probe of the root-cause fix.
> - (2) **THE WARDEN CLICK, fresh character:** same test on a brand-new Custom Quest char
>   (isolates any stale registry state baked into old saves).
> - (3) **Labyrinth -> Uber + return:** kill the Minotaur Lord, through the secret door, click
>   the pocket traveler -> "Enter the Uber Dungeon" -> crypt; click the in-crypt return ->
>   "The Labyrinth Door (Return)" -> back at the pocket.
> - (4) **Garden + Secret returns:** enter via Almyros; the in-area return travelers offer
>   Helos + Blood Cave and both work.
> - (5) **TESTHUB plaza sweep (DEV only):** all 14 plaza travelers respond with the RIGHT
>   label and land at the RIGHT area; nothing yanks you while walking the plaza.
> - (6) **Label integrity everywhere:** every menu row does what its label says (the
>   corruption-era "labels were wrong too" class must be gone).
> - (7) After promote: items (1)-(4) + (6) again on the **Steam build** (TESTHUB never uploads).
>
> ## 🆕 UBER-LABYRINTH ENTRANCE (2026-08-13): THE UBER DUNGEON IS NOW ENTERED FROM THE LABYRINTH OF KNOSSOS (canonical/Steam) - AND THE GUY BEHIND THE DOOR WAS MOVED + FIXED
> ### ⚠️ R-248 RE-SUPERSESSION (2026-08-14): the R-246 device note that stood here is DEAD - the door is gone and the greeter's "Enter the Uber Dungeon" MENU IS BACK (one-shot armed). The spot and everything below survive exactly as written.
> **This is a CANONICAL/Steam change (it ships), Levels + Quests together** - no database, no text
> change. Per your three decisions: (1) the Uber Dungeon entrance goes in the Labyrinth of Knossos on
> the STEAM build (Almyros in Helos stays as a second route); (2) the traveler you found "literally
> right behind the door after you kill the minotaur" was MOVED farther along the pathway - 9u past
> the secret door, centered in the open treasure pocket, so you can see him and click him; (3) his
> menu no longer says "Helos (Return)" - it is a SINGLE option, **"Enter the Uber Dungeon"**. The
> move + menu fix apply to BOTH your DEV/TESTHUB map and canonical, so your play surface is fixed too.
>
> **WALK-TO TEST (the canonical path a Steam player takes):**
> 1. In the **Labyrinth of Knossos** (maze03), fight through to the **Minotaur Lord** and kill him.
> 2. Behind the fight, in the boss room's WEST wall, is the **secret door** (the quest door that
>    opens after the kill). Walk through it into the small treasure pocket.
> 3. The **entrance traveler** (`svc_area_return_uber`, named "Return Traveler" for now - naming is
>    flagged for you) stands **centered in the pocket, ~9u past the door**, in the open - NOT behind
>    the door frame. World spot **(-7796, 1, -3792)**. You should see him immediately and the click
>    should land.
> 4. Talk to him -> his menu has **EXACTLY ONE option: "Enter the Uber Dungeon"** (no "Helos
>    (Return)"). Pick it -> you land on-mesh inside **`crypt_floor1`** (the Uber Dungeon interior).
> 5. The in-crypt **return traveler** (`svc_testhub_return_uber`, at the landing) sends you back to
>    **the Labyrinth door** (primary, "The Labyrinth Door (Return)") or **Helos** (secondary).
> 6. Sanity: **Almyros in the Helos plaza** still offers **"The Uber Dungeon"** (plus Garden /
>    Secret Place) - the Helos route is KEPT as the second way in.
>
> **IN-GAME CONFIRMATION IS THE REMAINING GATE.** Proven byte-level (exactly one level blob changed:
> maze03 0x05 +1 instance; its navmesh byte-identical; the NPC's single route + awakening decoded in
> the built Quests.arc; landing-clearance + traveler-responds + travel-invariants + contracts all
> green) but NOT walked in-game by the implementer.
>
> ### 🆕 SAME WAVE (2026-08-13, R6 forensic hygiene - fixes the scrambled-teleport session):
> 1. **Uber Dungeon arrival moved off the portal prop.** Both routes into the Uber Dungeon (Almyros
>    AND the labyrinth traveler) now land you ~7u south of the alcove portal prop, in the open
>    chamber, **4u in front of the in-crypt return traveler** - you no longer materialize ON the
>    portal statue. Check: enter via either route -> you stand in the open with the return traveler
>    clearly clickable ahead.
> 2. **Helos plaza de-crowded (your TESTHUB map).** The 14 plaza travelers were 1.66u-apart twins;
>    now EVERY pair is >=4.1u apart, arranged around a central **landing court**: west arc =
>    Garden/Secret/Sparta/Uber (the 4 area entrances), east column = Warband/Devourer/Vashkarr,
>    north pair = Dorus/Tantalus, west yard (through the wall gap, by the villagers) =
>    Charon/Ephialtes/Obsidian, gate side = Mnemophage, front-east = Boss Arena. Hover tooltips
>    name each one. Check: click the Uber traveler - you should never grab Sparta by accident.
> 3. **Every "Helos (Return)" now lands you center-plaza, clear of ALL clickables** (>=6.3u from
>    every traveler/NPC, ~7u in front of Almyros) - no more arrival mis-clicks bouncing you to the
>    catacombs. Check: take any return -> you arrive on empty plaza ground facing Almyros.
> ## 🆕 R-247 (2026-08-13): AKREMON ENHANCED + LETHAEUS ESCALATED + THE HUNT IS A SKELETON - FIGHT CHECKS
> **arz + Text change** (branch feat/akremon-enhancement). Fully quit TQ + restart Steam first.
>
> **1. AKREMON (Golden Bough forecourt, the old Charon dock):**
> * Phase 2 (the Heartwood Ablaze) must now be BIGGER than phase 1 (2.9 vs 2.8) and much
>   tankier/harder-hitting - a real wall even for your Toxeus-farming character.
> * NEW casts to look for: **the Emberfall** (an orange Telkine bolt from the terminal) and
>   **the Styx Undertow** (a cold wave from phase 1 at range - the river answering the tree).
> * The orb he drops must now read **"Akremon's Essence"**, NOT "Charon's Essence" (veto the
>   name if you want a different one - it is one string).
> **2. LETHAEUS (the Mnemophage):** the second form (the core) must now be BIGGER than the
>   shell (3.1 vs 2.9) and clearly stronger - never again the shrunken half-health form.
> **3. THE ENDLESS HUNT (Hades Palace floor):**
> * He must be a pale GIANT SKELETON now (Undead), not the shadow demon - with his spear.
> * His summons must be SKELETAL HUNTSMEN with spears, not blood hounds.
> * His soul now SUMMONS him (manual cast, like the Enslaver soul); Normal/Epic/Legendary
>   souls summon visibly different tiers (", Ascendant" / ", Unbound" names, much stronger).
> * All Toxeus-family souls now give +1/+2/+3 to all skills by tier (EoAT soul +3).
> * The **Rite of the Undivided** formula from his kill now drops with a LEGENDARY (orange)
>   name so it cannot vanish under the loot pile again - it was always dropping, it was white.
> **4. THE DEVOURER'S STASH (blood cave, the hidden chest room) - R-247.7:**
> * The Majestic stash chest is UN-NERFED: back to the original-SV flood (~19 loot rolls per
>   open, vs the ~2 the trim left it). Every other chest in the game keeps the trimmed rates.
> * The Devourer must be guarding it - CHECK ON NORMAL specifically (that was your report; the
>   bytes always said 100% on every difficulty, so if Normal is STILL empty after this build,
>   say so - that fingers the one remaining suspect [the map instance] and the next lane ships
>   a dedicated guard spawner).
> **5. THE PARCHMENT SPOT (blood-cave entrance, by the tattered parchment) - R-247.7:**
> * The ENSLAVER no longer spawns there (his warband set-piece is dormant; where his
>   dependable fight should MOVE to is your call - flagged as a decision).
> * The DEVOURER still ambushes there at ~33% (1-in-3 entries), with his two blood-demon guys.
> **6. NOT touched, per your "make note of it":** the Enslaver's Epic difficulty. Measured for
>   the ledger: 45k life / 12 per-sec regen / 30% reflect at 33% chance / leech-immune (Undead).


> ## 🆕 build89 / R-170 SECOND FOLLOW-UP (2026-08-12): THE WARDEN OF THE SPARTAN CRYPT SHOULD TALK NOW - **TWO-PART CHECK, DO BOTH**
> **`Quests.arc` ONLY** - no database, no map, no text change. Your character, your saves and every
> item are untouched. **Fully quit TQ and restart Steam before testing** (standing rule) - a running
> game keeps the old `Quests.arc` in memory and you would be testing the build you already have.
>
> **Background in one line:** when you clicked the Warden, nothing happened - no dialog box, nothing.
> The earlier attempt (b63) moved WHICH quest slot he was registered in, which could never have
> changed his behaviour. The real defect was his ACTION LIST: an NPC you TELEPORT INTO is never
> "woken up", so the game draws him but he has no yellow icon and eats the click. Every remote
> traveler now gets the same wake-up pair the working Leinth exit vortex has always carried, put in
> FRONT of the travel offer.
>
> **PART 1 - THE FIX (this is the thing that was broken).**
> Go to the **Sparta catacombs** and find the **Warden of the Spartan Crypt** standing by the
> stairs-down (level `CataCube02_FloorLast`). **Click him.**
> - ✅ **PASS:** a menu opens with the single option **"Descend into the Sparta Crypt"**, and taking
>   it ports you into the crypt.
> - ❌ **FAIL:** still nothing on click. Say so plainly - the next lever is a physical GridEntrance
>   door (the same mechanism as the Knossos -> Uber Dungeon door), not another dialog tweak.
> - Note: he is **descend-only, by your own ruling** - there is deliberately NO "Helos (Return)"
>   option on him. One option is correct, not a bug.
>
> **PART 2 - THE REGRESSION CHECK (do not skip: the working ones were touched too).**
> The 14 **Helos plaza travelers** already worked, and this build changed their triggers as well
> (one uniform shape rather than two classes). So **click ONE plaza traveler in Helos and actually
> take its route.**
> - ✅ **PASS:** the menu opens exactly as before and it ports you where it always did.
> - ❌ **FAIL:** if a traveler that used to work has gone quiet, or a menu lost/gained an option,
>   that is a regression caused by this build - report it and it gets reverted, not patched over.
> - Free bonus while you are out there: click any **return NPC** in an SV area (the "back to Helos"
>   guy) - those are remote NPCs too and were mute for the same reason.
>
> **HONEST CAVEAT:** no remote traveler in this mod has ever been confirmed working in-game by
> anyone, including the vortex the fix is copied from. The evidence is strong (upstream-authentic
> mechanism, exact symptom match, a new gate that reproduces your bug against the currently-shipped
> file), but **you are the proof**. `BL-b88-DEBT-1` / `BL-b88-DEBT-2`.

> ## 🆕 R-240 + R-241 (2026-08-11): THE LOOT VOLUME TRIM - CHESTS AND ORBS BOTH COME DOWN ~10x
> **NOT BUILT YET** (branch `fix/loot-volume-trim`; this note is written with the lane so the check is
> ready when the build lands). arz-only - no map / quest / Text change on the canonical side.
> **Fully quit TQ and restart Steam before testing** (standing rule). Every number below is MEASURED
> against the shipped `build83` arz, not estimated.
>
> **Your two asks, and what each one did:**
>
> **1. "from the two chests, you get guaranteed 1 legendary item" (R-240).**
> The canonical Gaoler cage, both chests opened once, on Legendary difficulty: it paid **36.4**
> legendary-grade pieces and now pays **3.8** (Normal 43.7 -> 3.8, Epic 28.2 -> 2.7). It still pays at
> least one **99.6%** of the time on the optimistic reading, or **98.3%** if the engine truncates the
> spawn count to a whole number (Epic: 96.9% vs **94.0%**) - we do not yet know which it does, so both
> are gated and the pessimistic one is quoted alongside, because that is the number the gate actually
> holds (`BL-R240-DEBT-5`). Either way the guarantee survives the cut. Honest note: the mechanical floor
> is **2.74** per two-chest run, not 1.0 - six loot groups fire per spawn iteration and their chances
> already sum past 280%, so "literally one" needs a composition change, not a volume one. That is
> `BL-R240-DEBT-1`.
>
> **2. "you made the orbs way too good ... a chance to drop legendary items, but a low chance" (R-241).**
> **The number you asked for first: THREE guaranteed-legendary rows in the whole mod** - one per
> difficulty, all of them the same row on the three apex orb tables, and none of them a pure-legendary
> row. **They are all gone now (zero).**
> But the row count was not where the guarantee lived. Per ONE orb open on Legendary difficulty an orb
> paid **3.7 to 8.4 legendary items** with a **98-99.99%** chance of at least one. It now pays
> **0.70 to 0.85 - at most ONE legendary per open** - and the whole orb pays about **2 items** instead
> of 9 to 29.
>
> **WHAT TO DO:**
> - Kill a **Mystical Orb uber** a few times on Legendary and open the orbs. Expect roughly **two items**
>   out of each, and **at most one of them legendary** - that is the half of your ruling that landed
>   (8.4 legendary items per open became 0.85). Do NOT expect a legendary to feel rare yet: **a bit
>   over half of opens still contain one**, which is the half that did not land. See the box below -
>   it needs a decision from you, and the number there is the one to judge, not this bullet.
> - Run the **Gaoler cage** (the two canonical chests). Expect a **handful** of pieces, not a vendor's
>   stock, and still at least one legendary almost every run.
> - Anything you can still get, you could get before: **no pool lost an item and no weight moved.** The
>   spear variety, the armour parity and the class breadth from the last few builds are all intact - they
>   just arrive less often. If some class of item has stopped appearing entirely, that is a real bug.
>
> **⚠️ THE ONE THING I DID NOT FULLY FIX, AND IT NEEDS YOUR ANSWER BEFORE THIS SHIPS
> (`BL-R241-DEBT-1`).**
> You asked for two things about the orbs and I only delivered one. **Delivered:** no guaranteed
> legendary rows (3 -> 0) and 8.4 legendary items per open -> 0.85. **Not delivered:** "but a low
> chance". The chance of seeing at least one legendary from an orb is still **54-61%** on Legendary
> and **38-49%** on Epic. **That is more likely than not, so it is not a low chance, and I am not
> pretending it is.**
>
> The reason: about **40% of everything a Legendary-tier orb can pay IS legendary-grade**, because the
> last few builds deliberately weighted the unique weapon and armour pools that heavily to give you the
> class variety you asked for. So if the orb pays two items, one of them is often legendary. The volume
> lever is spent - the orbs are already at the floor where they would start coming up EMPTY - so
> dropping the rate further means changing WHAT is in the pools rather than how much, which re-opens
> the armour-parity work. That is a separate lane and your call:
> **(A)** accept it - you get ONE legendary instead of EIGHT, and roughly every other orb has one, or
> **(B)** I add an epic-grade sibling pool so an orb usually pays Epics with an occasional legendary.
>
> If you pick **(B)**, the ceiling the gate currently commits (`ORB_MAX_P_LEGENDARY` = 55%/68%) comes
> down in the same commit as the fix. It is set where it is to lock in the 90% cut already made, **not
> because 55-68% is a rate anyone chose.**
>
> **On the TESTHUB (DEV) side nothing gets poorer:** the four farm-duplicate cage chests are being moved
> onto their own records that keep the OLD, rich volume, so DEV farming stays fast while the Steam build
> trims. That needs the TESTHUB map rebuilt to take effect; until then the DEV cage trims with canonical
> (under-pays rather than over-pays, which is the safe direction).

> ## 🆕 R-211 (2026-08-11): ATLANTIS IS UNREACHABLE NOW, THE SHIP TOO (not just the portal page)
> **✅ LIVE ON DEV as `build82` (arz `09a0f51d`).** arz-only (no map / quest / Text change).
> **Fully quit TQ and restart Steam before testing** (standing rule).
>
> **Background in one line:** `build78` took Atlantis off the portal page, but an Atlantis-DLC owner
> could still SAIL there. This build closes that.
>
> **THE ONE-LINE TEST (needs the Atlantis DLC installed, otherwise there is nothing to see):**
> On a character that has **beaten Typhon**, walk around **Rhodes**.
>
> **What you should see:**
> 1. **No Marinos.** The Atlantis-quest NPC who used to appear in Rhodes City after Typhon is not there.
> 2. **No ship captain offering Gadir.** The boat NPC on the Rhodes dock that offered to sail west is
>    gone from the world and from the minimap.
> 3. **No Atlantis adventure in the quest log.** Nothing new appears under your active quests.
> 4. **The portal page still shows exactly FOUR act tabs** (Greece / Egypt / Orient / Immortal Throne),
>    and the Immortal Throne page still lists Olympus and all of Hades. This is the `build78` behaviour,
>    re-proved on this build so you can confirm nothing regressed.
>
> **What must still work (tell me if any of this broke):** everything else in Immortal Throne. Rhodes
> itself is unchanged as a place - you can still walk it, fight in it, use its portal and its shops. Only
> the two Atlantis-DLC travel NPCs are hidden. If you own the DLC, Rhodes should now look exactly the way
> it looks for a player who does not own it.
>
> **Not covered by this test:** if you already sailed to Gadir or Atlantis on an earlier build and have a
> character standing there, the RETURN boats were deliberately left working so you can sail back. That is
> intentional anti-strand behaviour, not a leak.


> ## 🆕 R-184/185/186 (2026-08-11): THE CRAFT CHAIN - FORMULAS ON NORMAL, EVERY REAGENT FARMABLE, THROWN LEGENDARIES DROP
> **✅ LIVE ON DEV as `build81` (arz `f1671207`).** arz-only (no map / quest / Text change).
> **Fully quit TQ and restart Steam before testing** (standing rule). Every number below is measured on
> the shipped build, not estimated.
>
> **THREE THINGS TO LOOK FOR, in the order they are quickest to check:**
>
> **1. Mythic Formulas can now appear on NORMAL - but legendary ITEMS still cannot.**
> Play a Normal-difficulty character and open mod chests (the Gaoler cage is the densest, but any of
> them works - this also applies to ordinary monster formula drops, not just chests). Mythic Formulas
> for the uber craftables are now possible: they sit at **~1.5% of a formula roll**, deliberately
> **rarer than the base game already makes them on Epic (2%) and Legendary (5%)**, so this is a "over a
> session you should see one or two", not "every chest". What you must **NOT** see on Normal is a
> legendary ITEM - that is unchanged and re-proved: the Normal weapon branch reaches **116 items, 0 of
> them Legendary**, and the new thrown table on Normal reaches **2 items, 0 Legendary**.
> *If a legendary item drops on Normal, that is a bug - tell me and I will treat it as P0.*
>
> **2. Farm Legendary and the reagents accumulate - no specific boss, no specific area.**
> All **42** uber craftables are now completable. Before this build, **seven** of them could not be
> finished at all by anyone playing this mod: Ananke's Canvas, Mortok's Skull, The All-Seeing Eye, and
> the four thrown ones (Charon's Toll, Hati, The Last Word, Sanguine Orbit) - the thrown four named
> **Ragnarok items this mod's database does not contain**, so their recipes were dead ends.
> Now: **61 of the 82 reagents drop from Legendary chests**, and every one of them is payable by **19
> of 19** legendary chest surfaces, so no single boss or area gates anything. The 22 that stay
> monster-specific are the **green / Monster Infrequent** items you exempted - and each one is now
> *proven* to have a live monster that drops it (one green had no live carrier at all; it is
> chest-placed instead).
>
> **3. The legendary thrown weapons drop.** They could not drop from anything before - there was no
> unique one-hand-ranged loot table in the whole database, so one was authored.
> Expect **about 1.3 thrown weapons per six-chest Gaoler cage run** on Legendary. Most of those are the
> ordinary DRX vit wand; the four craft-tier ones stay prizes at **~0.08 per run each**, which is
> roughly **five times rarer than any specific legendary spear**. That is deliberate: they are still
> meant to be crafted, and a chest handing you one should feel like luck.
> ⚠️ **This is the number I most want your eye on.** I built a version where the thrown class carried
> a full class's weight - it looked correct by every automated check, and it paid **1.3 of each craft
> weapon per run**, which would have made crafting them pointless. I rebuilt it. If it still feels too
> generous (or too stingy) in play, it is one constant and one line to change.
>
> **Where to go:** Prison of Souls / Hades Palace floor 4, kill Alkyoneus the Soul-Gaoler, open all 6
> cage chests, 2-3 runs. Same trip as the last three builds, so you can compare directly.

> ## 🆕 R-220 (2026-08-10): THE MYSTICAL ORBS NOW PAY EVERY CLASS TOO - SPEARS INCLUDED
> **✅ LIVE ON DEV AND ON STEAM as `build79` (arz `883a31e2`).** arz-only (no map/quest/Text change).
> **Fully quit TQ and restart Steam before testing** (standing rule). The numbers in the table below are
> measured on the shipped build, not estimated.
>
> **THE ONE-LINE TEST: kill any uber that drops a Mystical Orb, open it, and spears should now be in
> the pool - along with visibly more class variety.**
>
> **What was wrong.** R-180 fixed the CHESTS. The ORBS had the exact same defect and nobody had looked:
> every orb's weapon row named the 3-class `1h_all` master (axe / club / sword) plus bow and staff, and
> forgot **spear** - so **a spear of any quality was impossible out of 15 of the 18 orb loot tables, on
> every difficulty**. The only orb tier that was already fine is the Toxeus apex orb, purely by accident:
> its tables live in our own folder, so R-180's chest sweep happened to reach them.
>
> **What changed (measured on the built arz, not estimated).** Every orb tier now names the same
> aggregate weapon master the chests use, and its weapon row fires at **40%** (was 13/14%) with the
> shield row at **30%** (was 13/14%) - the values the Toxeus apex orb has had since build75, so the whole
> ladder now behaves the same way. Distinct reachable items per open:
>
> | orb tier (who drops it) | Normal | Epic | Legendary | spears |
> |---|---|---|---|---|
> | tier 1 - Mormo, Elephant Snatcher, Rakanizeus, Melalos, Calybe, Kaublasia, **Boar Snatcher** | 117 -> **195** | 72 -> **99** | 194 -> **260** | 0 -> **18 / 9 / 22** |
> | tier 2 - Grimshell, Phagia, Permean, um_frost, Neferkha | 101 -> **182** | 75 -> **102** | 138 -> **241** | 0 -> **18 / 9 / 22** |
> | tier 3 - Inkeyes, Palai, Xaiweng, the General's Guardians | 96 -> **180** | 71 -> **96** | 196 -> **262** | 0 -> **18 / 9 / 22** |
> | tier 4 - the custom apex roster (**Unbound Gaoler**, Tantalus Unbound, Mnemophage Core, Aithon, Dagon, Helepolis, Ephialtes, Kravmoloch, Sarkoth, Vashkarr, Ilsevar, Gorrahk, Voranthys, Broodmother, Drowned King, Hades Marshal, Bloodcrow...) | 99 -> **181** | 95 -> **116** | 258 -> **308** | 0 -> **18 / 9 / 22** |
> | tier 5 - the Toxeus roster | 181 | 116 | 308 | already fine (R-180) |
> | Charon's Essence - the Golden Bough terminal form (🆕 R-231: that form is now **Akremon, the Heartwood Ablaze**; the ORB keeps its shared base-game "Charon's Essence" display string, logged `BL-BOUGH-DEBT-4`) | 99 -> **181** | 95 -> **116** | 258 -> **308** | 0 -> **18 / 9 / 22** |
>
> **EASIEST CHECK - it is the SAME TRIP you are already doing for R-180.** In the **Prison of Souls**
> (Hades Palace floor 4), killing **Alkyoneus the Soul-Gaoler** finishes on his Unbound form, and the
> Unbound Gaoler drops a **tier-4 Mystical Orb**. So one run tests both waves: open the six cage chests
> (R-180) and the orb he drops (R-220). On Legendary the orb can now pay **308** distinct legendary
> items including **22 legendary spears**, where before it could pay 258 and **zero** spears.
>
> **Second check, low level:** the **Boar Snatcher** in Pine Forest / SpartaOptCave03 (the R-200 monster)
> drops a tier-1 orb - useful for confirming the Normal and Epic branches too.
>
> **What to look for:**
> 1. **Spears out of an orb at all** - that was impossible before, at every tier and difficulty.
> 2. **More than one thing per orb.** The weapon and shield rows used to fire ~1 open in 7; they now fire
>    ~1 in 2.5 and ~1 in 3.3, so an orb should feel less like "one item and some potions".
> 3. **Nothing got weaker.** The orb's spawn EQUATIONS, its gold, its relic row and the apex orb's
>    larger payout are byte-for-byte what they were - only the weapon and shield rows fire more often
>    (that is check 2, and it means MORE items, not fewer). If an orb feels *stingier* than before, that
>    is a bug, not the design; say so.
> 4. **Normal difficulty stays Normal.** No legendary gear should appear on Normal from any orb (the
>    mercenary scrolls and arcane formulae that already showed up there are base-game and unchanged).
>
> **One thing to veto if you want it.** Will asked for BREADTH and got it (check 1). Checks 2's higher
> drop rate was NOT asked for - it is the rate the Toxeus apex orb has had since build75, applied to the
> rest of the ladder for consistency, and it is half the change. Say the word and the classes stay while
> the drop rate goes back to what it is today; it is a one-line switch, not a rewrite.

> ## NEW R-210 (2026-08-10): ATLANTIS IS GONE FROM THE PORTAL PAGE
> **THE ONE-LINE TEST: open a portal (any rebirth fountain / teleport) and count the act tabs. You
> should see exactly FOUR - Greece, Egypt, Orient, Immortal Throne - and NO Atlantis, no Ragnarok, no
> Eternal Embers.** Then click each of the four and check the destination lists still look right
> (Olympus and all of Hades are still on the Immortal Throne page).
>
> **Second surface, same fix:** open the quest log. Its act tabs should also stop at Immortal Throne.
>
> **What was wrong.** The portal window's page list is ONE database record. Soulvizier ships an
> Immortal-Throne-era copy with the four base pages, but our user-interface cleanup pass deletes every
> such record (it has to - Soulvizier's old UI records break the modern mastery screens), so the mod
> shipped no copy at all and the BASE GAME's seven-page version took over. If you own the expansions,
> you got their tabs. Now the four base pages are imported back faithfully with the three expansion
> pages deleted, and a build gate fails loudly if any of them ever reappears.
>
> **If you see any tab other than those four, that is a real find** - the gate says there are zero.
>
> ⚠️ **STILL OPEN, be aware:** this removes the Atlantis PAGE, not the Atlantis VOYAGE. If you own the
> Atlantis DLC you can still sail Rhodes -> Gadir -> Atlantis by boat. That is a separate fix
> (`BL-PORTALCAP-DEBT-1`) and needs your call on how to block it.

> ## NEW R-201 (2026-08-10): OUR SOULS FINALLY HAVE EPIC AND LEGENDARY NAMES
> **✅ LIVE ON DEV AND ON STEAM (build77-ship, Workshop item 3759792705).** arz
> **`435cc485ee43e739b85d4221e6c9bb4b`**; the map, quests and Text did not move.
>
> **THE ONE-LINE TEST - two souls, three tiers each:**
> 1. **Soul of the Gaoler** (Alkyoneus the Soul-Gaoler, Prison of Souls / Hades Palace floor 4 - the same
>    boss as the chest-breadth test). Expect **"Soul of the Gaoler"** on normal, **"Epic Soul of the
>    Gaoler"** on Epic, **"Legendary Soul of the Gaoler"** on Legendary.
> 2. **Soul of the Insatiable** (Tantalus, `um_tantalus_99`, in the cave off the Stygian Marsh whose area
>    banner reads **"Den of Tantalus"**). Expect **"Soul of the Insatiable"** / **"Epic Soul of the
>    Insatiable"** / **"Legendary Soul of the Insatiable"**.
>
> All three tiers of both used to read the plain name. Same fix on the other 96 souls we made - Dagon, the
> Broodmother, the Blood Cult High Priest, the Waking Dread, all four Toxeus souls, every hand-crafted
> hero soul.
>
> ⚠️ **Use a FRESHLY DROPPED soul, not one already in your stash or caravan, if anything looks off.** The
> name is read from the database at display time so a stored soul should update too, but TQ bakes item
> data at pickup (standing lesson), and a stale stash item is the one way you could see "no change" on a
> build that is actually correct.
>
> ⚠️ **Do not use Charon Soul as your test.** Two different souls render that exact name - ours and
> Soulvizier's own - so it cannot tell you whether the fix landed. Same caution for General Yrrt'ik, Ice
> Mandible, Kallixenia and Plague Feast. That duplicate-name overlap is older than this fix and is logged
> as `BL-R201-DEBT-1`; renaming souls is your call, not ours.
>
> **What was wrong.** A soul does not carry three names: the three tier records share ONE name and the
> engine prefixes the tier word from a separate field (`itemQualityTag`). Every SV soul had it - all
> 641 of them, no exceptions - and not one of the 98 souls WE authored did, because every generator we
> wrote copies one field set to all three tiers and none of them ever set that field. So ours rendered
> the same string on normal, epic and legendary.
>
> **Nothing was renamed.** The tier word goes in FRONT of the existing name, so "Soul of the Gaoler"
> is still exactly "Soul of the Gaoler" on normal, and the SV originals were not touched at all.
>
> **If you see a soul that still reads the same on all three tiers, that is a real find** - the new
> build gate says there are zero left, and it fails the build if one appears.

> ## 🆕 R-181 (2026-08-10): ARMOUR NOW DROPS LIKE ARMOUR, AND NO ONE CLASS RUNS AWAY WITH THE RUN
> **✅ LIVE ON DEV AND ON STEAM as `build80` (arz `c5851a1a`).** This is your two follow-up reports on
> R-180: *"also what about the armor? i am not really seeing armor drops like shields, chest plates,
> helmets, etc."* and *"you overcorrected, that run 4 scorpions tail spears dropped"*. Both were REAL
> and both were measured, not guessed. arz-only again, so the map/quests/Text did not move.
> **Fully quit TQ and restart Steam before testing** (standing rule). Every number below is measured
> on the SHIPPED build, not predicted - the dry run and the build agree to the second decimal.
>
> **YOU WERE RIGHT ABOUT BOTH, AND HERE ARE THE NUMBERS.** R-180 proved a chest COULD pay every weapon
> class; it never checked how OFTEN. On the build you played, one cage run paid **58.5 legendary
> weapons against 12.4 armour pieces** - helms were 1.6% of everything that dropped - and **SPEAR alone
> was 24% of the run** when an even split across the eleven gear slots is 9.1%. At 17 spear drops a run
> over 22 distinct spears, **four copies of one spear was a 27% event**. Your run was the ordinary
> case, not bad luck.
>
> **WHAT CHANGED.** Every armour row now fires at the weapon row's own 40% (they were 33/31/30, and
> 32/32/30 on the orb chests), the
> legendary share inside each armour row went from roughly 10-19% of the row's weight to about half,
> and one new "armour master" pays all five worn slots evenly. On the weapon side, the one table that
> covers axe + mace + sword was carrying a single spear's weight, so each of those three classes got a
> third of a spear's chance; that is fixed, and the per-chest theme biases were softened. **Nothing was
> reduced** - your cage run goes from about 71 to about 109 legendary items; only the mix changes.
>
> | per cage run | you played | after |
> |---|---|---|
> | SPEAR share | 24.0% | 9.8% |
> | helm share | 1.6% | 8.7% |
> | torso share | 3.7% | 9.1% |
> | shield share | 7.1% | 10.8% |
> | weapons : armour | 4.73 : 1 | 1.22 : 1 |
> | armour pieces | 12.4 | 49.4 |
> | P(4 copies of ONE spear) | 27.0% | 6.3% |
> | P(4 Scorpion's Tails) | 2.07% | 0.45% |
> | P(4 copies of ANY one item) | 47.3% | **39.7%** |
>
> Every one of the eleven gear classes now lands between 7.8% and 10.8% of a run, against an even
> split of 9.1%. Before, the spread ran from 1.6% to 24.0%.
>
> **ONE THING I AM NOT GOING TO OVERSELL, because you would catch it anyway.** Four copies of a
> *spear* is now about 1 run in 16 instead of 1 in 4. But four copies of *something* is still a bit
> better than a coin flip - 39.7%, barely down from 47.3%. The reason is that I did not reduce
> anything: your run went from about 71 legendary items to about 109, and with more items on the floor
> some item will hit four copies fairly often just by volume. **If you want the total number of drops
> per chest brought down, say so and I will do it** - that is the one lever I deliberately did not
> pull, because cutting drops is exactly the kind of change you should get to approve.
>
> **HOW TO TEST IT (same cage as R-180 - Prison of Souls, Hades Palace floor 4, where Alkyoneus the
> Soul-Gaoler guards the Polybotes cage):**
> 1. Kill Alkyoneus (both forms) and open **all 6 chests**.
> 2. You should now see **helmets, chest plates, bracers, greaves and shields** in the pile, not just
>    weapons - expect roughly as much armour as weaponry.
> 3. No single weapon class should dominate. If one class is clearly running the run again, say which.
> 4. **Re-run 2-3 times.** Four copies of the same SPEAR should now be uncommon; four copies of some
>    item or other will still turn up, and that is expected (see the note above).
> 5. Boss hoards (Charon, Tantalus, the Diadochi, the guard pairs) and the blood-cave mega chest got
>    the identical treatment, so check one of those too if you are passing.
> 6. **NEW in this round - check a red-uber Mystical Orb chest** (the Boar Snatcher's, or any of the
>    red ubers from R-200, or Leinth's). Those were the WORST offenders in the whole mod and had been
>    missed: they were paying **0.07 helms per open** against 0.98 weapons. They now pay about **1.2
>    of every worn slot**. If an orb chest still looks weapon-only, that is a real find.
>
> **ADDED AFTER THE FACT (BL-R181-DEBT-7, round 3): the ORDINARY uber orbs too, and one honest
> warning. ✅ LIVE ON DEV **AND STEAM** as `build83` (arz `44499f56`)** - arz-only, no map / quest / Text change;
> fully quit TQ and restart Steam before testing. Item 6 above covers the red-uber and Leinth orbs. Fifteen more orb loot tables - the
> level-banded ones every ordinary uber drops, plus Charon's - had their armour owned by NOBODY and
> were running **3.4:1 to 8.5:1 weapons:armour with a worn slot as thin as 0.007 pieces per open**.
> They now pay **0.29 to 1.16 of the thinnest worn slot**, and total drops per orb went UP
> (7.9 -> 9.2, 9.3 -> 11.8, 13.7 -> 15.8 items per open). Nothing was reduced anywhere.
>
> ⚠️ **The warning, so you are not surprised:** on these fifteen the mix now runs **armour-heavy** -
> roughly 2 to 3.5 armour pieces per weapon (w:a 0.28-0.49). That is the exact ratio the Toxeus apex
> orb has been shipping since build75, so it is consistent rather than invented, but if orbs start
> feeling like an armour vending machine that is a REAL finding and worth saying - it is one constant
> to move back.
>
> **WHAT WAS DELIBERATELY LEFT ALONE, so you can rule it in or out:** armour that drops off MONSTERS is
> base-game wiring in this mod - of the ~1,500-1,850 records that carry each armour-drop chance, only
> 12 to 14 are ours (under 1%) - and no monster in the database drops a shield off its body at all
> (the field does not exist on a single record), so shields only ever come from chests and merchants.
> If you want armour off monsters too, that is a separate wave and it needs your call.

> ## 🆕 R-200 (2026-08-10): THE BOAR SNATCHER NOW DROPS A MYSTICAL ORB
> **✅ LIVE ON DEV (build76-dev) AND ON STEAM (build76-ship, Workshop item 3759792705).** `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` =
> **`16994072e1cb244af9f4d759309162cb`** (55,549,261 B), deployed + md5-verified 2026-08-10 while TQ was
> closed. arz-only; the map/quests/Text on DEV did not move. **Fully quit TQ and restart Steam before
> testing** (standing rule).
>
> **THE ONE-LINE TEST: kill the Boar Snatcher (the red legendary spider) and a Mystical Orb should drop.**
> Find him in **Greece - Pine Forest (Area003/PineForest04)** or the **Sparta optional cave
> (SpartaOptCave03)**; all three level variants (15/17/19) were wired, so any difficulty works.
>
> While you are there, 7 more red ubers that were silently orb-less now pay out too: **Neferkha**,
> **um_frost**, **Phagia (the lvl-44 twin)**, **Aithon** in the Olympian Arena, and **Kravmoloch**.
> If ANY red uber you kill still drops no orb, say so - the new class gate says there are zero left, so
> that would be a real find.

> ## 🆕 R-180 (2026-08-10): THE GAOLER-CAGE CHESTS NOW DROP DIFFERENT THINGS, AND LEGENDARY SPEARS ARE POSSIBLE
> **✅ NOW LIVE ON DEV - build75-dev.** `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` =
> **`3fb1f3ce8889e27de2491ab12814547d`** (55,539,324 B), deployed + md5-verified 2026-08-10 while TQ was
> closed. It is arz-only, so the 4 TESTHUB farm-duplicate chests get it too (they reference the same 2
> records as the canonical pair). **Fully quit TQ and restart Steam before testing** (standing rule).
> Steam: this arz is staged in the combined Workshop package alongside the b63 Warden fix; the Steam
> ship record for both lands with that push.
>
> **WHICH CHESTS TO OPEN:** the Polis Daemonai vault-cage in the **Prison of Souls** (Hades Palace floor 4)
> - where the Polybotes Soul drops and Alkyoneus the Soul-Gaoler guards the cage. **All 6 chests**
> (2 canonical placements + the 4 farm duplicates), on **3 separate runs**.
>
> **WHAT BREADTH TO EXPECT (measured on the built arz, not estimated):** each difficulty pool now offers
> **3 themed chests at 50/25/25** instead of 1, so the six physical chests stop mirroring each other -
> chest_01 rolls **martial** (spear + one-hand), **hunter** (bow + spear) or **warden** (shield + torso);
> chest_03 rolls **apex**, **adept** (staff) or **sovereign** (amulet + ring), each still with its
> guaranteed relic. The weapon row fires at **40%** (was 14%) and the shield row at **30%** (was 14%).
> Reachable distinct items per open: Legendary **258 -> 308**, Epic **90 -> 111**, Normal **99 -> 181**.
> **SPEARS EXPLICITLY: legendary spears go 0 -> 22 reachable** (Achilles' Spear, Ares' Wrath, Soulharvest,
> Peleus' Ashen Spear, Telamon's Boar Skewer, Onuris' Spear and the rest). Only 2 stay out by design:
> the Endless Hunt's Runbreaker (his own guaranteed drop) and the DRX supra craft-only spear.
>
> **What was wrong (both halves were real, not perception).** Every mod chest inherited one collapsed
> weapon row from the DRX donor: it named the 3-class `unique_1h` master plus bow and staff, and simply
> forgot **spear** - so a legendary spear was structurally impossible, in the cage AND in every boss
> hoard, while 24 legendary spears sat in the DB unreachable. And the only slot that reliably fired was
> the 100% guaranteed one, which always paid an axe/mace/sword, so every open looked the same.
>
> **What to check (Prison of Souls, Hades Palace floor 4 - where Polybotes stands and the Soul-Gaoler
> guards the cage):**
> 1. Kill **Alkyoneus the Soul-Gaoler** (both forms) so the cage unlocks, then open **all 6 chests**.
> 2. Expect **visible class variety between chests in the SAME run** - the chests now come in themes:
>    a martial/spear chest, a hunter (bow) chest, a warden (shield/armour) chest, an apex chest with a
>    guaranteed relic, a caster/staff chest and a jewellery chest. Each of the 6 physical chests rolls
>    its own theme when the area loads, so they should no longer read as six copies of one chest.
> 3. Expect **legendary spears to actually appear** across a few runs (22 of them are now reachable -
>    Achilles' Spear, Ares' Wrath, Soulharvest, Peleus' Ashen Spear, Telamon's Boar Skewer, Onuris'
>    Spear and the rest). Two are deliberately NOT in the pool: the Endless Hunt's Runbreaker (his own
>    guaranteed drop) and the DRX supra craft-only spear.
> 4. **Re-run the cage 2-3 times** and confirm the mix shifts between playthroughs, not just between
>    chests.
> 5. **Nothing should have got worse:** same number of items per chest, chest_03 still pays its
>    guaranteed relic at the same rate, and the difficulty tiers are unchanged (Essence on Normal,
>    Embodiment on Epic, Incarnation on Legendary).
> 6. The same breadth landed on **every other mod chest** (Charon / Tantalus / Mnemophage / Ephialtes /
>    Diadochi / the three general-guard pairs / Obsidian / the blood-cave mega chest), so spot-check one
>    boss hoard elsewhere if you get the chance.

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
> Sparta Crypt should be entered from the Athens CATACOMBS, not from Helos" - the **Warden of the
> Spartan Crypt now stands on the shipping map**, and **Almyros the Wayfarer in Helos NO LONGER lists
> "The Sparta Crypt"** (he still offers Garden of Merchants / The Secret Place / The Uber Dungeon).
>
> **PR-5 POLISH (2026-08-06):** the catacomb NPC is now named **"Warden of the Spartan Crypt"** (it used
> to read the generic "Return Traveler"), and his menu is **DESCEND ONLY** - the old "Helos (Return)"
> option is gone, so he offers a **single** boat choice.
>
> **WALK-TO TEST (fresh Custom Quest char recommended):**
> 1. Go into the **Athens catacombs** and work down to the **DEEPEST level** (CataCube02_FloorLast) -
>    the chamber with the **stairs-down**, amid the beastmen. World spot **(-6587, 1, -3180)**.
> 2. The **Warden of the Spartan Crypt** stands right by the stairs-down there (record
>    `svc_warden_sparta_crypt`). Confirm his name reads **"Warden of the Spartan Crypt"**, then talk to
>    him -> his boat menu has **EXACTLY ONE option: "Descend into the Sparta Crypt"** (no "Helos (Return)").
> 3. Pick it -> you teleport **on-mesh inside `spartacryptlevel2`** (the crypt interior). A **return
>    traveler stands there** (`svc_testhub_return_sparta`) and sends you back to **this catacomb door**
>    (primary) or **Helos** (secondary).
> 4. Sanity: talk to **Almyros in the Helos plaza** and confirm **"The Sparta Crypt" is GONE** from his
>    menu while Garden / Secret Place / Uber Dungeon remain.
>
> **IN-GAME CONFIRMATION IS THE REMAINING GATE.** This was proven byte-level (only the catacomb blob's
> 0x05 changed; navmesh byte-identical; the Warden owns exactly the one descend route; the landing
> passes gate_landing_clearance) but NOT walked in-game by the implementer (deploys are the
> orchestrator's). See BACKLOG PR-5 + WILL_RULINGS R-170 (+ its PR-5 POLISH amendment).
>
> ## 🔴 b63 (2026-08-10): YOU WALKED IT AND HE WAS MUTE - FIXED, RE-TEST THIS ONE
> Your report: "when I click on the guy who travels you to the spartan crypt (warden of the spartan
> crypt) nothing happens, no dialog box comes up, nothing." You were right, and it was **live on
> Steam** from 2026-08-06, where he is the **only** way into the Sparta Crypt.
>
> **What was wrong (two things).** (1) His one menu entry was generated by the single trigger class in
> the whole travel rig that had **never** been confirmed working in-game, and the PR-5 polish had
> accidentally made it his *only* menu source. It is now generated by the same proven code path as the
> travelers you use all the time. (2) He was standing on **exactly** the spot both Sparta teleports
> drop you on (0.00u), so an arriving player materialises inside him. He moved 6u, to
> **(-6587, 1, -3186)** - still right by the same stairs-down, just no longer on the landing pad.
>
> **His menu is UNCHANGED and still DESCEND ONLY** - one option, "Descend into the Sparta Crypt", no
> "Helos (Return)". That is still your ruling and it is now asserted by a gate directly.
>
> **⚠️ TEST ON LEGENDARY OR EPIC, not Normal.** Your `_Toxeus` Normal-difficulty quest state is still
> the stale pre-PR-5 shape and will only re-sync the next time you load it; Legendary and Epic already
> carry the current quest definition.
>
> **Re-test:** deepest Athens catacomb (CataCube02_FloorLast) -> find the **Warden of the Spartan
> Crypt** by the stairs-down -> click him -> **a dialog box should open with exactly one choice** ->
> pick it -> you land inside `spartacryptlevel2` -> the return traveler there brings you back.
> If he is STILL silent, say so and say **whether you walked in or teleported in** - that single
> detail decides the next fix (a door instead of a boat NPC).
>
> **SHIPPED 2026-08-10, tag `build75-ship`. It is on DEV AND on Steam.** DEV has `Levels.arc`
> `7a7ca9ac` + `Quests.arc` `607ec99c` (deployed together, and your arz/Text/Creatures were verified
> byte-unchanged by the deploy). Workshop item 3759792705 was updated and confirmed, so subscribers
> have it too - it had been broken for them since 6 August, and yours is the click that confirms it.
> **Quit TQ and Steam fully, restart Steam, then launch TQ** before testing (standing law).
>
> **The exact walk:** Play Custom Quest -> `SoulvizierClassicDEV` on **Legendary or Epic** -> deepest
> Athens catacomb (`CataCube02_FloorLast`) -> the **Warden of the Spartan Crypt** stands by the
> stairs-down (he has moved about 6 units off the teleport arrival spot, so if you teleport in you now
> land NEXT to him rather than inside him) -> **click him**.
> **PASS = a dialog box opens with EXACTLY ONE choice, "Descend into the Sparta Crypt".**
> Pick it -> you land inside `spartacryptlevel2` -> the return traveler there brings you back.
> **FAIL = still no dialog box.** That is still a useful result: say so plus walked-in vs teleported-in.
>
> Same session, the other half of this Steam update (chest loot, R-180): kill Alkyoneus the
> Soul-Gaoler and open all 6 vault-cage chests across about 3 runs - you should see legendary SPEARS
> become possible and the six chests stop mirroring each other.

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

## HELOS TRAVELER HUB v2 - ⚠️ SUPERSEDED BY R-246 NATIVE-DEVICE TRAVEL (2026-08-13, see the top section)

> **The boat-dialog hub below is RIPPED.** The 14 travelers are now NAMED MUTE MARKERS beside the
> east-field portal COURT (talking to them does nothing); travel is walk-in doors + click rift
> shrines; only Almyros keeps a talk menu. The "where each landing drops you" TABLES below are
> still accurate (the court reuses the same v2 area-entrance landings) - read them as the COURT's
> destination reference. The old per-area Return Travelers are replaced by return RIFT SHRINES.

The historical v2 description (mechanism superseded, landings current):

**v2 change (this is what you asked for):** each traveler now drops you at the **natural in-game
approach point** for its area - the **door / entrance / travel-NPC you would use in game**, standing
**amid the regular mobs**, NOT on top of the boss. So you can test the real in-game travel guys,
learn where everything is, and **walk in** to the boss yourself.

### Original 11 areas - where v2 now drops you

| Traveler NPC | Drops you at (v2) | What to walk to / test |
|---|---|---|
| **Traveler: Garden of Merchants** | the merchant hub by the caravan_rhodes Super-Caravan + the SV **rift-shrine** (teleportshrine_gom) that reaches the Garden in game | browse the merchants; the rift-shrine is the in-game way in |
| **Traveler: The Secret Place** | the darkforestenter **forest-cluster entry** | walk in; the crow-hero bosses (Murderbunny, Zilla) live in the interiors |
| **Traveler: The Sparta Crypt** | the **Sparta-Crypt DOOR** in the deepest Athens catacomb (CataCube02_FloorLast, by the stairs-down), amid catacomb beastmen | 🆕 PR-5 POLISH: the **Warden of the Spartan Crypt** (`svc_warden_sparta_crypt`) stands right there. His menu is DESCEND ONLY - a single "Descend into the Sparta Crypt" option that takes you straight into `spartacryptlevel2` (the interior itself), where its own return traveler sends you back to THIS catacomb door (primary) or Helos (secondary) |
| **Traveler: The Uber Dungeon** (was "Obsidian Halls") | the **Knossos->Uber DOOR** in the Minotaur's Labyrinth (maze03), at the Minotaur's secret door | the in-game Uber entrance; the base-game Minotaur Lord is ~24u east. 🆕 2026-08-13 UBER-LABYRINTH PROMOTION: the entrance NPC (`svc_area_return_uber`) is now CANONICAL (ships on Steam), was MOVED 9u past the secret door into the open treasure pocket (you reported him hidden right behind the door, unclickable), and his menu is a SINGLE option, **"Enter the Uber Dungeon"** - the old "Helos (Return)" row is GONE. It takes you into `crypt_floor1`, where its own return traveler sends you back to THIS door (primary) or Helos (secondary) |
| **Traveler: The Boss Arena** | the boss-arena forecourt (~90u south of the arena volume) | walk north into the Satyr-Shaman arena |
| **Traveler: Blood-Cave Warband** | the blood-cave connection chamber at the **regular demon pack** (~35u off the Enslaver horde) | walk up to the Enslaver warband (skeleton leader + 4 marauders) |
| **Traveler: Medea Tomb (Dorus)** | the tomb **entrance** (cryptentrance), amid the drowned court | walk ~82u to **Dorus, the Drowned King** + hoard |
| **Traveler: Den of Tantalus** | the Styx swamp-**stairs entrance**, amid anouran | walk ~36u to **Tantalus, the Insatiable** (2 forms) + hoard |
| **Traveler: Golden Bough (Akremon)** | the Styx **Hades-city settlement** (the boatman, storyteller + a Styx rift-shrine) | test the settlement NPCs; walk east to **Akremon, the Grasping Root** + the Golden Bough. 🆕 R-231: Charon is OUT of this forecourt entirely - the traveler NPC was renamed with him |
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
12. 🆕 **Akremon, the Grasping Root** - the Golden Bough forecourt (Styx river edge, Act 4).
    **REWORKED under R-231 (your 2026-08-11 order): Charon is GONE from this forecourt.** The
    same shrine, the same walk, an entirely different fight. A colossal black tree with every
    hand that ever reached for the Bough grown into it. TWO PHASES: phase 1 is **bleed-IMMUNE**
    (park the bleed spears), roots you in place, and grows a literal wall of quillvines between
    you and it - the only monster in the mod that builds terrain. At 33% life the bark splits, the
    thorns come out and it starts hitting **35% harder** - deliberately no damage shield and no
    self-heal, so it gets more dangerous without getting less killable. Kill it and **Akremon, the
    Heartwood Ablaze** walks out of the trunk:
    faster, on fire, and **NOT bleed-immune** - the build you shelved gets the kill. Two
    **Handbriar** champions whip alongside.
    **THE SECOND SWAP, and please poke at it:** the tree is **weak to fire and cold (-30 each)**
    and the thing that comes out of it **resists fire (+70)**. So burning phase 1 down should feel
    great and then stop working, the same way the bleed spears do in reverse. Both forms are
    **resistant but not immune** to stun/freeze/traps (75/60/60) - deliberately not the old
    Charon's flat 100 immunity, so your control skills should land *sometimes*. If either phase
    feels perma-lockable, or if the fire swap just reads as "phase 2 is annoying", say so.
    **35,000 on Epic across both forms, matched exactly to Alkyoneus the Soul-Gaoler** (the fight
    you beat on the second attempt) - so it should be hard, and it should die. Tell us if it is a
    wall; that is the number we most want checked.
    Drops **THE GOLDEN BOUGH** amulet (guaranteed), the **Soul of the Grasping Root** (grants
    "Graft the Burning Heartwood" - a permanent burning cutting that walks for you; the soul roots
    what you strike and costs you **8/6/5% movement speed** as the price), and the hoard chest,
    now labelled **"The Orchard of Hands"**. The names are our invention and are yours to veto.
    ⚠️ **Check the soul's tooltip specifically.** Through rounds 3 and 4 that movement penalty was
    written into the wrong field and **did not exist** while three documents said it did; round 5
    measured it against all 2,453 souls in the mod and moved it onto the field
    `mnemophage_soul_*` uses. It should now read as a real movement penalty on the item. If the
    tooltip shows nothing, the fix did not land.
    The boss drops **no ordinary junk loot** on either form - that is deliberate (it matches what
    the old Charon paid, and the payout is the Bough + the hoard + the soul + the orb). If that
    feels stingy for an uber, say so and it flips back on in one line.
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
   now ENTERABLE: at the Athens catacomb door, talk to the **Warden of the Spartan Crypt**
   (`svc_warden_sparta_crypt`) - his menu is DESCEND ONLY, one "Descend into the Sparta Crypt"
   option. Its own return traveler inside sends you back to this same catacomb door (primary) or
   Helos (secondary).
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
