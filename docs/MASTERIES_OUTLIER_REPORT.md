# Masteries Outlier Report, Soulvizier Classic

**For Will, read-only understanding. No fixes proposed.** This answers: *"a comparison across
masteries to find outliers, are any particularly weak or strong (this is ok, I just want to
understand the degree to which this exists)."*

**Source:** the newest built database, the **content-wave** arz
`.claude/worktrees/build36-content/local/build36c/Database/SoulvizierClassic.arz`
(md5 `759b2784`, built 2026-07-11 16:30, 50,840 records). It is a superset of the fix-wave arz
(`07de3349`) and I verified every mastery + key-skill record is byte/value-identical between the two,
so these numbers equal the post-fix-wave state. Base TQAE `database.arz` and amgoz1 **SV 0.98i** loaded
as fallbacks. Method reuses the pet-roster / mastery-audit approach: decode with `tools/arz_patcher.py`,
mod-first case-insensitive resolution, sample each ladder at L1 / skillMaxLevel / skillUltimateLevel,
parse the PC anim tables for castability. Probes: `.../scratchpad/outlier_probes/`.

---

## 1. The one-paragraph verdict (degree of imbalance)

**The 11 trees are in a fairly tight band, and the imbalance is MODERATE, not severe: roughly a 3 out
of 10.** After the fix wave, no tree is broken and no tree runs away with the game. The frozen
**Occult** tree is still the strongest overall (it is the designed benchmark, and by design nothing
exceeds it), with **Spirit, Warfare, Earth and Hunting** clustered right behind it. The clearest
*overall* laggards are the two base-DLC trees, **RuneMaster and Neidan**, which remain plain
vanilla-budget stat-sticks that top out at mastery level 40 with no deep combat-multiplier tail and the
thinnest skill synergy, though even they are now perfectly playable. Two trees look "weak" on the total
score only because they are deliberate **specialists**: **Defense** (a pure turtle, top defense but
bottom offense and pets) and **Nature** (a pure summoner, top pets but no personal damage or hard
crowd-control). The single genuine power *over-tune* is **Spirit's Necrosis**, a permanent -100% enemy
resistance debuff, and that one is inherited from amgoz1's original SV, not something our waves created.
The most important finding for "degree": the pre-fix audit found two trees flatly BELOW the bar and five
broken headline skills; **our fix wave has since closed almost all of that gap**, so the imbalance you
have today is mostly the *inherited* shape of the game (a strong hand-tuned bar, two untuned DLC trees,
one legacy over-tune) rather than anything the mod's own tuning broke.

**Top outliers at a glance:**
- **Strongest overall:** Occult (the bar), then Spirit / Warfare / Earth.
- **Weakest overall:** RuneMaster and Neidan (the vanilla DLC trees).
- **Biggest single-axis extremes:** Defense (defense/sustain, sky-high) and Spirit's Necrosis
  (-100% resist shred); at the low end, Nature (zero hard crowd-control) and Defense (near-zero pets).

---

## 2. How to read this (fairness caveats)

- **Damage is not one currency.** Weapon trees (Warfare, Defense, Occult, Hunting, and partly
  RuneMaster / Neidan) scale off your equipped weapon (a `+X% weapon` modifier); caster trees (Earth,
  Storm, Dream, Spirit) deal flat spell numbers. A single "DPS" figure across both is dishonest, so the
  damage axis blends: best spammable engine, best burst nuke, and execute (%current-life) damage.
- **The bar.** Occult (the reskinned Rogue/Stealth tree) is amgoz1's hand-tuned reference, frozen by the
  golden gate. Hunting is the secondary bar. The scoring treats "matches Occult's tree-total" as the top
  of the scale; the Will-approved `MASTERY_AUDIT_2026-07-09.md` established this and I reuse its rubric.
- **Ratings are a synthesis,** 1 (weakest) to 5 (strongest), combining my measured numbers with the
  audit's dimensional verdicts. Treat +/- 0.5 as noise. "Pets" is scored separately from "Damage" so a
  summoner is not double-counted.

---

## 3. Overall ranking (all seven axes)

Sum of six substantive axes (dead-skill is near-flat post-fix, shown separately). Higher = stronger.

| Rank | Mastery | Dmg (self) | Defense | CC/Util | Pets | Skill-pt value | Synergy | **Total /30** | Shape |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| 1 | **Occult** 🔒 | 5.0 | 3.0 | 4.0 | 4.5 | 4.5 | 5.0 | **26.0** | the bar: broad + layered |
| 2 | **Warfare** | 4.0 | 4.5 | 3.5 | 3.0 | 4.5 | 4.0 | **23.5** | sturdy front-loaded bruiser |
| 3 | **Spirit** | 4.0 | 2.0 | 3.5 | 5.0 | 3.5 | 5.0 | **23.0** | pet + DoT + shred powerhouse |
| 4 | **Earth** | 4.5 | 3.0 | 2.5 | 3.5 | 4.0 | 4.5 | **22.0** | post-fix fire-caster surge |
| 4 | **Hunting** 🔒 | 4.0 | 3.5 | 4.0 | 2.5 | 4.0 | 4.0 | **22.0** | efficient pierce/bleed ranger |
| 4 | **Dream** | 3.5 | 4.0 | 4.5 | 2.5 | 4.0 | 3.5 | **22.0** | CC + defense caster (three-way tie at 22.0) |
| 7 | **Storm** | 4.5 | 2.0 | 4.0 | 2.0 | 4.0 | 4.0 | **20.5** | glass-cannon storm caster |
| 7 | **Neidan** | 3.5 | 3.0 | 5.0 | 3.0 | 3.0 | 3.0 | **20.5** | alchemist CC specialist (capped) |
| 9 | **Nature** | 2.5 | 2.5 | 2.0 | 5.0 | 3.5 | 4.0 | **19.5** | pure summoner specialist |
| 9 | **RuneMaster** | 3.5 | 3.5 | 4.0 | 3.0 | 3.0 | 2.5 | **19.5** | capped rune-hybrid, thin synergy |
| 11 | **Defense** | 2.0 | 5.0 | 3.0 | 1.0 | 3.5 | 3.0 | **17.5** | pure turtle specialist |

**Spread: 17.5 to 26.0 (about 28%).** Read it as three groups: **Occult alone at the top** (the intended
ceiling), a **wide healthy middle** (Warfare, Spirit, Earth, Hunting, Dream, Storm, Neidan, ~20.5-23.5),
and a **specialist / laggard floor** (Nature, RuneMaster, Defense). Crucially, Nature and Defense are low
only because they pour everything into one axis; **RuneMaster is the one tree that is low without a
compensating peak**, which makes it the truest "plain / weak" outlier.

---

## 4. Per-axis ranked tables (the outliers live here)

### 4a. Damage throughput (personal rotation, pets excluded)
Best spammable engine + best burst + execute, at ML40 / gear-boosted ceiling.

| Rank | Tree | Headline | Key numbers (post-fix) |
|---|---|---|---|
| 1 | **Occult** 🔒 | Lethal Strike | **+600% phys +450% pierce** weapon one-button (cd14) + Calc Strike ~1s-cd spam + dual DoT paths |
| 2 | **Earth** | Meteor | **~2,600-3,300 dmg/hit** nuke (phys+fire at the +skills ceiling; more with fire/phys% gear), now castable, **cd 360 to 60**; Volcanic Orb **cd 4 to 1.5** spam; +20% cast speed |
| 2 | **Storm** | Chain Lightning | Lightning Bolt 380-683 + group-petrify chain; Thunderball **revived**; +60% cast speed front-loaded |
| 4 | **Warfare** | Onslaught+Battle Rage | near-free spam (0.5 mana, cd0) + Crushing Blow proc +265 flat; **+25% STR by ML40**; Doom Horn 24%-life execute |
| 4 | **Spirit** | Bonespire | **~2,000 nuke revived** (was cast-aborting) x7 projectiles; Necrosis -100% funnel doubles all vit damage |
| 4 | **Hunting** 🔒 | Marksmanship + Takedown | near-free pierce spam + **45% current-life execute** (Takedown, **spear-gated** - not on a bow/thrown build) + Study Prey -66% amp |
| 7 | **RuneMaster** | Seal of Fate | 1,300 elemental + **46% current-life execute** + Runic Mines (up to 30) + Maelstrom |
| 7 | **Neidan** | Death Bomb / Shen Pao | corpse-explosion AoE + Shen Pao **now castable**; Dragon's Breath staff-gated |
| 9 | **Dream** | Distort Reality | 831 flat + 20% execute + Phantom Strike +239%; no big weapon nuke |
| 10 | **Defense** | Heave / Shield Smash | Shield Smash damage **restored** [12-61]; Heave +355% mace + **new 5% execute**; still light + flat |
| 11 | **Nature** | (pets only) | no personal weapon/burst skill at all; damage routes through pets + Plague %-life tick |

**Damage outliers:** Occult (burst) and Earth (post-fix, the biggest single jump in the whole mod) are
the high end; **Nature has literally no personal damage skill** and Defense is the slowest killer.

### 4b. Defense / sustain (mastery + tree, gear excluded)

| Rank | Tree | ML40 Life | Standout mitigation |
|---|---|:--:|---|
| 1 | **Defense** | **2000** | +10% phys + **+8% elem** res (front-loaded), Armor Handling, Rally heal, Colossus, taunt, block tail |
| 2 | **Warfare** | 1600 | Counter Attack, Ignore Pain +20% phys/pierce, Heart of War, dual-wield dodge |
| 3 | **Dream** | 1400 | +20% damage-absorb party aura, +30% DA, ~10% leech, 85% projectile reflect |
| 4 | **Hunting** 🔒 | 1300 | poison immunity, projectile deflect, Cornered Rage panic (near CC-immune) |
| 5 | **RuneMaster** | 1160 | Energy Armor (absorb to ~6900), Menhir Wall blockers |
| 6 | **Occult** 🔒 | 1200 | dodge 20% (only at ML41-72), life-leech engines; avoidance-based |
| 7 | **Earth** | 1120 | fire resist, Heat Shield retaliation, fear immunity |
| 8 | **Neidan** | 1050 | Aura of Tranquility, Melding Armor, potion trio |
| 9 | **Nature** | 800 | low HP but above-bar *active* heal/absorb (Regrowth, Heart of Oak, 40% Nature's Blessing) |
| 10 | **Storm** | 900 | Energy Shield flat absorb, Spellbreaker panic; no dodge/leech |
| 11 | **Spirit** | 800 | thin: Death Ward panic only, fights behind pets |

**Defense outliers:** **Defense is a runaway high outlier (2000 HP + layered mitigation).** Storm and
Spirit (800-900 HP, glass casters) are the low end. Post-fix the floor rose: Storm was buffed 680 to 900.

### 4c. Crowd-control / utility

| Rank | Tree | Hard-CC types | Mobility | Notable utility |
|---|---|---|---|---|
| 1 | **Neidan** | **5** (confuse/fear/freeze/petrify/stun) | Essence of Jade | 3 party auras, resist shred, potions |
| 2 | **Dream** | 4 (confuse/petrify/sleep/stun) | blink | mass sleep 6-13s x9, silence/dispel, 20% CDR |
| 3 | **Storm** | 3 (freeze/petrify/stun) | **Lightning Dash (grafted)** | group-petrify AoE nuke, Squall -43% all-resist |
| 3 | **RuneMaster** | 4 (confuse/fear/freeze/stun) | Arc Attack | Magic Maelstrom AoE lock, mines-field |
| 3 | **Occult** 🔒 | 3 (confuse/petrify/stun) | **blink** (Lethal Strike) | fumble/confusion heavy, Blade Honing aura |
| 6 | **Hunting** 🔒 | 2 (confuse/fear) | **best** (+28% run, +charge, +root) | 12-target Tempest, Study Prey team amp, 3 auras |
| 7 | **Warfare** | 1 (stun, but strong) | Ardor +25% run | War Horn/Chain AoE stun, **taunt** aggro-control, banner party-amp |
| 8 | **Spirit** | 2 (fear/sleep) | none | mass sleep + Death Chill -40% speed aura + shred |
| 9 | **Defense** | 1 (stun) | Shield Charge | fumble, taunt, Rally party heal |
| 10 | **Earth** | 1 (stun) | none (+12% passive run only) | 2 auras, -40% total-resist shred |
| 11 | **Nature** | **0 hard-CC** | none | soft slows + 1 root (Earthbind graft); 3 auras |

**CC outliers:** Neidan / Dream / Storm / RuneMaster are the high end (4-5 hard-CC types). **Nature is the
low outlier with zero hard crowd-control** (soft slows only). Earth and Defense also thin (1 type each).

### 4d. Pet power

| Rank | Tree | Types | Max bodies | Flagship pet (top-tier HP) | Notes |
|---|---|:--:|:--:|---|---|
| 1 | **Nature** | 5 | **17** | Treant 3,795 (temp) | wolves x5 + sprites x9 + nymph + briar + treant; +30% pet-dmg mastery |
| 2 | **Spirit** | 5 | 8 | Ether Lord 4,500 (temp) | 2 difficulty-scaled elites + bonefiend + 4 skeletons; **dead content revived** |
| 3 | **Occult** 🔒 | 3 | 5 | Shadow Stalker ~3,350 (perm) | elite caster + 3 darklings + bolt-trap: the reference pet package |
| 4 | **Earth** | 1 | 1 | Core Dweller **3,938 (permanent)** | one huge permanent diff-scaled golem (D17 buffed x1.75 life) |
| 5 | **RuneMaster** | 2-3 | 2-3 | Rune Golem ~1,950 (graft) | + Guardian zapstones + Menhir walls (blockers, no damage); golem wiring is a Lane-A detail |
| 6 | **Neidan** | 1 | 3 | Terracotta 1,225 (perm) | 3 tanky constructs; toads are gold-only props |
| 7 | **Warfare** | 1 | 5 | Spectral Soldier 1,200 (temp) | elite soldiers, uptime buffed 10% to **38%** |
| 8 | **Hunting** 🔒 | 1 | 5 | Bolt-trap 318 (~100% up) | disposable ranged turret swarm |
| 9 | **Storm** | 1 | 1 | Wisp 1,190 (perm) | single fragile totem that carries the +200% aura |
| 10 | **Dream** | 3 | 3 | Doppelganger 1,100 (temp) | Nightmare (MasterMind aura **revived**) + Phantasm + Dream Image graft |
| 11 | **Defense** | 1 | ~formation | Phalanx 525 (21% up) | went from **zero pets** to a minimal grafted formation |

**Pet outliers:** **Nature and Spirit are the high end** (broad, deep, difficulty-scaled). **Defense is
the low outlier** (essentially no pets, just a grafted phalanx). Earth is unusual: one single *permanent*
elite instead of a swarm.

### 4e. Skill-point value (per point on the strongest path, at practical caps)

| Tier | Trees | Why |
|---|---|---|
| **High** | **Warfare** (+25% STR by ML40), **Earth / Storm** (+20% / +60% cast speed by ML40), **Dream** (multipliers front-loaded to ~ML32), **Defense** (phys+elem res by ML40) | these deliver real combat multipliers at the level you actually reach |
| **Medium** | **Occult / Hunting** 🔒 (premium *skills* per point, but the mastery's %dodge/OA/DA/attack-speed are **back-loaded to ML41-72**), **Spirit / Nature** (INT/mana fuel + revived pet bonus) | strong skills, but the signature mastery multipliers arrive late or via pets |
| **Low(-ceiling)** | **RuneMaster / Neidan** | mastery **caps at level 40** with **no combat-multiplier tail at all**: every point is realized early but the ceiling is a plain stat-stick, so a dedicated player has nothing deep to invest into |

**Subtle finding:** the frozen bars (Occult / Hunting) are actually **back-loaded**, their signature
mastery percentages only accrue past ML40, which most players never reach. So at practical levels several
tuned trees (Warfare, Earth, Storm) get *more* per mastery point than the bars do. RuneMaster / Neidan
are the low outliers here: they are the only two masteries with no combat-multiplier ladder anywhere.

### 4f. Dead-skill count (castability + effect analysis)

**This axis is now essentially FLAT, which is the fix wave's headline achievement.** I scanned every
tree's attack skills against the PC animation tables and every summon / modifier for dead effects.

| Tree | Hard-dead (uncastable any weapon) | Weapon-gated / near-dead | Notes |
|---|:--:|---|---|
| Warfare, Defense, Earth, Storm, Occult, Nature, Spirit, Dream | **0** | 0 | all clean; every headline casts |
| **Hunting** 🔒 | 0 | **1** (Takedown) | spear-gated (takedown/tempest anim 1/8 = spear row only); alive for spear builds, off-weapon otherwise. Least restrictive of the three below - spear is a mainline Hunting weapon - and the bow/thrown Marksmanship engine is unrestricted, so this is a build choice, not dead content. |
| **RuneMaster** | 0 | **1** (Hail of Axes) | castable only when dual-wielding (barrage anim 2/8 = dual-melee or dual-thrown); damage is a flat non-scaling +100% |
| **Neidan** | 0 | **1** (Dragon's Breath) | staff-gated (flamesurge anim 1/8 rows); alive for staff builds, dead otherwise |

Pre-fix there were **five hard-broken skills** (Meteor, Thunderball, Bonespire cast-aborts; Shield Smash
zeroed; Nightmare MasterMind aura dead) plus disabled pet content. **All five are verified fixed** in this
arz, and the disabled Spirit (bonefiend Spirit Breath, Liche King skeleton summons), Dream (timefield
cleared, phantom-strike self-slow zeroed), Nature (charm-resist copy-paste cleared) and Neidan (Splash
modifier now attached) content is **revived**. The only residuals are the three weapon-gated slots above -
each alive for its intended weapon, none hard-dead. Minor cosmetic dead FX/sound references remain in
several trees but those are not dead *skills*.

### 4g. Synergy breadth (good pairings / modifier depth)

| Rank | Tree | Modifier slots | Synergy identity |
|---|---|:--:|---|
| 1 | **Occult** 🔒 | 12 | poison funnel (Toxin +350%) + bleed funnel (Anatomy +200%) + Blade Honing aura + pet synergy |
| 1 | **Spirit** | 14 | vitality funnel: Necrosis + Death Chill + Arcane Lore, Bonespire projectile/leech synergies |
| 3 | **Earth** | **15** | fire funnel: Meteor / Volcanic / Eruption + Molten Lava shred + Rupture line |
| 4 | **Nature** | 14 | summoner web: Overgrowth +60% pet dmg + Susceptibility -54% + per-pet modifiers |
| 4 | **Warfare** | 12 | Battle Rage + Crushing Blow, War Wind + Refinement + Lacerate, Slam + Fissure |
| 6 | **Storm** | 11 | lightning (Chain + Static Charge) + cold (Ice Shard + Torrent + Velocity) + Squall |
| 7 | **Hunting** 🔒 | 10 | pierce+bleed funnel: Study Prey + Art of Hunt + Cunning |
| 8 | **Defense** | 9 | weapon-pool procs + Rend/Triumph amp; Cleave bleed now coherent (base bleed added) |
| 9 | **Dream** | 8 | Lucid Dream amp + CC pairings |
| 10 | **Neidan** | 6 | potions + Consequences + Death Bomb chain |
| 11 | **RuneMaster** | 5 | fewest pairings; runic synergies are shallow |

**Synergy outliers:** Occult / Spirit / Earth (deep, coherent damage funnels) at the top; **RuneMaster is
the clear low outlier** (5 modifiers, shallowest web), with Neidan next.

---

## 5. The strongest trees, and why (with numbers)

- **Occult (the intended ceiling).** It is the only tree that is above a normal share on *four* axes at
  once: burst (Lethal Strike **+600% +450% weapon** one button), sustained DoT (Toxin **+350%** poison,
  Anatomy **+200%** bleed), a **5-body pet package** led by the ~3,350 HP Shadow Stalker elite caster, and
  the deepest synergy web (12 modifiers). Its only "weak" spots are middling raw HP (1200) and a
  back-loaded mastery. It is frozen precisely because it is the balance yardstick.
- **Spirit.** A genuine peer built the opposite way: the **biggest pet budget after Nature** (up to 8
  bodies, two difficulty-scaled 4,500 HP elites) plus a permanent **-100% enemy vitality/bleed/poison**
  aura (Necrosis) that doubles the whole tree's damage, plus its flagship **Bonespire ~2,000 nuke that the
  fix wave brought back from a dead cast**. Held back only by 800 HP and no personal defense.
- **Warfare.** The best-rounded tree: highest bruiser HP among offense trees (1600), the **only
  front-loaded offensive mastery** (+25% STR by ML40, so its points pay immediately), near-free rotation,
  above-bar AoE and stun/taunt control. No single peak, but no real hole either.
- **Earth (the biggest post-fix mover).** Pre-fix it was flatly BELOW (dead Meteor, throttled orb,
  mana-starved). Now: **Meteor ~2,600-3,300 base damage/hit, castable on a 60s cooldown** (was a dead 360s;
  the base skill tops out at phys 1,246-1,421 + fire 1,320-1,906 at the +skills ceiling, scaled further by
  fire/physical% gear), **Volcanic
  Orb spam at 1.5s** (was 4s), **+20% cast speed and 480 mana** on the mastery, a **-40% total-resist
  shred** (Molten Lava), and a single **permanent 3,938 HP Core Dweller**. It jumped from the bottom tier
  to the upper-middle.

---

## 6. The weakest trees, and why (with numbers)

- **RuneMaster (the truest overall laggard).** Its *skills* are competitive (Seal of Fate 1,300 +46%
  execute, up to 30 Runic Mines, Energy Armor), and the fix wave meaningfully helped it (**mastery Life
  800 to 1,160, mana 0 to 400**, Menhir/Mines/Guardian uptime up, Rune Golem grafted). But three
  structural things keep it last-equal: (1) the mastery **caps at level 40 with no combat-multiplier tail
  at all** (the only masteries like this are RuneMaster and Neidan), (2) the **fewest synergy modifiers (5)**,
  and (3) **Hail of Axes remains weapon-gated + flat-scaling**. It is fine to play, just plain.
- **Neidan.** Same capped-stat-stick structure (mastery Life buffed 900 to 1,050, still no
  multiplier tail, smax 40). It compensates with the **broadest hard-CC in the game (5 types)** and a
  potion/construct toolkit, so it scores higher than RuneMaster on utility, but **Dragon's Breath is still
  staff-gated** and its synergy web is thin (6 modifiers). A capable CC/support tree with a low ceiling.
- **Defense (weak only as a generalist).** It is **the #1 defense tree by a mile (2,000 HP + layered
  mitigation)** but trades away nearly all offense (slowest killer, flat/light damage even after the Shield
  Smash and Heave fixes) and **has almost no pets** (a grafted phalanx at 21% uptime, up from zero). Its
  low total score reflects extreme specialization, not brokenness: as a party turtle it is excellent.
- **Nature (weak only as a soloist).** **The #1 pet tree (5 lines, 17 bodies, +30% pet-damage mastery,
  a treant whose 705/hit exceeds the Shadow Stalker)**, but it has **no personal damage skill and zero
  hard crowd-control**. Everything runs through pets, so on the personal-damage and CC axes it is the
  floor. As a summoner it is top-tier.

---

## 7. Single-axis extremes (the sharpest outliers)

| Axis | High outlier | Low outlier | Gap |
|---|---|---|---|
| Defense/sustain | **Defense 2000 HP** + full mitigation | Spirit / Storm 800-900 HP | ~2.5x raw HP |
| Pet power | **Nature (17 bodies)**, Spirit (4,500 elite) | **Defense (~zero)** | categorical |
| Personal burst | **Occult** (+600/+450% wpn), **Earth** (~2.6-3.3k/hit Meteor) | **Nature** (no skill), Defense | categorical |
| Hard crowd-control | **Neidan (5 types)**, Dream (4) | **Nature (0)** | 5 vs 0 |
| Resist-shred amp | **Spirit -100% permanent** (Necrosis) | everyone else -40 to -66% windowed | the one over-tune |
| Skill-point ceiling | smax-72 tuned trees | **RuneMaster / Neidan** (smax-40, no tail) | structural |

---

## 8. Are the outliers amgoz1-inherited, or our-waves-created?

Cross-referenced against `docs/MASTERY_DEVIATIONS_LEDGER.md`.

**Inherited from amgoz1 SV 0.98i (and the base DLCs):**
- **The strong ceiling (Occult / Hunting).** amgoz1's hand-tuned frozen bars. They are the *reason* a bar
  exists; balanced against each other, protected by the golden gate.
- **The weak floor (RuneMaster / Neidan).** These are the vanilla Ragnarok and Eternal Embers trees. SV
  0.98i **predates both DLCs and never tuned them**, so their capped stat-stick shape is inherited. Our
  waves *buffed* them but kept them vanilla-pointer + smax-40 (deliberately, to avoid stranding existing
  characters).
- **Spirit's Necrosis -100% permanent shred.** An inherited SV over-tune (mitigated only by its small
  2.8-4.0 radius). Not created by us.
- **The 300-360s pet-uptime throttle** across several trees is an inherited SV knob.

**Corrected or narrowed by our fix waves (this is why today's imbalance is smaller than the audit's):**
- **The two BELOW trees (Earth, Defense) and every broken headline** were caused by the SV-to-AE **port
  breakage** (monster anims on player nukes, a zeroed Shield Smash, a dead pet aura). **Our fix wave
  repaired all five**, lifting Earth from the bottom to the upper-middle and firming Defense.
- **Mastery buffs are ours:** Storm 680 to 900 HP, RuneMaster 800 to 1,160 HP + 0 to 400 mana, Neidan 900
  to 1,050, Earth mana + cast speed, Nature's +30% pet-damage bonus. These **shrank the mastery spread**.
- **The grafts are ours** (SVAERA hybrid + SV 0.4.1 legacy restores): Lightning Dash, Frost/Fire Nova,
  Perfect Block, Summon Phalanx, Rune Golem, Dream Image, Earthbind, Slam. They **added missing
  capabilities to the weak trees** (Storm's mobility, Defense's first pets, etc.).
- **Pet buffs are ours** (Core Dweller x1.75, Shadow Stalker overhaul, Storm Wisp x1.5), but each was
  **deliberately kept below the Occult Shadow Stalker bar**, so they raised the floor without creating a
  new high outlier.

**Net attribution:** the imbalance you have now is **dominated by inherited structure** (a hand-tuned bar
as ceiling, two untuned DLC trees as floor, one legacy over-tune). **Our own tuning has been corrective,
it narrowed the spread and introduced no new runaway tree.** The only thing worth watching that is partly
ours is whether the revived Spirit pet content plus the buffed permanent pets (Earth's 3,938 Core Dweller,
Spirit's elites) drift the pet-heavy trees toward the intended pet ceiling, but each individual pet was
tuned to stay under Occult's Shadow Stalker.

---

## 9. One-page "degree of imbalance" verdict

- **Overall degree: MODERATE, about 3 out of 10, and shrinking.** Total scores run 17.5 to 26.0 out of 30
  (a ~28% spread). One tree sits alone at the top (Occult, by design), **seven** sit in a healthy 20.5-23.5
  middle, and the **three lowest** (Defense 17.5, Nature 19.5, RuneMaster 19.5) are two hyper-*specialists*
  plus the plainest *DLC* tree; the other plain DLC tree, **Neidan** (20.5), scores at the bottom edge of
  that middle band. **No tree is broken; no tree dominates.**
- **The strong end is intentional.** Occult is the frozen benchmark and, per the audit, nothing is above
  it on tree-total. Spirit, Warfare, Earth and Hunting are close behind by different routes (pets, bruiser
  durability, fire-caster burst, ranged efficiency).
- **The weak end is mostly inherited and mostly narrow.** RuneMaster and Neidan are the only trees weak
  *without* a compensating peak, and their weakness is the vanilla-DLC structure SV never tuned (capped
  masteries, thin synergy, one weapon-gated slot each), which our waves have already softened. Defense and
  Nature "score low" only because they are hyper-specialists that are best-in-class on their own axis.
- **Two things are genuine watch-items** (understanding only, not fix requests): (1) **Spirit's Necrosis**
  permanent -100% resist shred is the one true power over-tune, and it is amgoz1-inherited; (2) the
  **skill-point back-load inversion**, where the frozen bars reward ML41-72 investment most players never
  reach while the tuned trees front-load their multipliers, means the "bar" is softer at practical levels
  than its reputation suggests.
- **Bottom line for Will:** yes, weak/strong outliers exist, but the degree is mild and the shape is
  largely the game you inherited. Occult is the deliberate high; RuneMaster/Neidan are the inherited low;
  Defense and Nature are extreme-but-intended specialists; Spirit's Necrosis is the lone legacy over-tune.
  Your own waves have been the force *reducing* the imbalance, not causing it.

---

*Generated read-only from the content-wave arz (`759b2784`, = fix-wave `07de3349` on all mastery records).
Ratings synthesize measured record values with the Will-approved `MASTERY_AUDIT_2026-07-09.md` rubric.
Probe scripts: `.../scratchpad/outlier_probes/` (`01_discovery` .. `07_mastery_mults`).
Damage across weapon-scaled vs caster trees is not a single currency; treat +/- 0.5 rating and +/- 1 rank as noise.*
