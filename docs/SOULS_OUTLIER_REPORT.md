# Soulvizier Classic - Soul Outlier Analysis (read-only, understanding only)

**Question (Will):** *"I also want a comparison across souls and a comparison across masteries to find
outliers, are any particularly weak or strong (this is ok, I just want to understand the degree to
which this exists)."*

**This report covers the SOULS half.** It compares every soul ring on comparable value axes and
locates the strong/weak outliers, the family/rank patterns, and answers the load-bearing question:
**is the spread amgoz1's intended design, or a generator artifact?** No fixes are proposed. This is
a map of where the imbalance sits and how large it is.

**Source (newest built):** `.claude/worktrees/build36-content/local/build36c/Database/SoulvizierClassic.arz`
(md5 `759b2784`, built 2026-07-11 16:30, the content-wave build = fix wave + Lane A pet overhaul +
new-content souls). **amgoz1 baseline:** `upstream/soulvizier_098i/Database/database.arz` (SV 0.98i).
Read-only; probes at `scratchpad/outlier_probes/`.

---

## 1. TL;DR - the degree of imbalance

Measured at **Legendary** tier across **707 real soul rings** (5 wildcard/template records excluded):

| Axis (Legendary) | p10 | median | p90 | max | p90/p10 | Read |
|---|---:|---:|---:|---:|---:|---|
| **Composite value** | 94 | 219 | 494 | **1224** | **5.3x** | moderate-to-wide spread |
| Stat budget (positive) | 74 | 194 | 430 | 1118 | 5.8x | the dominant axis |
| Granted-skill / summon | 0 | 12 | 70 | 130 | - | present on ~half of souls |
| Downside (magnitude) | 0 | 0 | 63 | 341 | - | ~half of souls carry one |

**The imbalance is real and sizable, but it is overwhelmingly INTENDED amgoz1 design, not a generator
artifact.** Three numbers make the case:

1. **The spread is inherited.** amgoz1's own SV 0.98i souls already span **4.7x** (p90/p10) with a max
   of 798. The mod widens this only modestly to **5.3x** - and that widening is entirely the **96
   new mod-authored souls** (their internal spread is 6.7x), not a corruption of his originals.
2. **The weak tail is his, byte-for-byte.** The single weakest soul (Stonekeeper, net **-69**) has the
   **identical -69** in upstream. Behemoth (-37), Deathwalker (-8), Bonelord (23), Minkah (41),
   Cindercrow (39) - all match upstream exactly. The mod did not create the weak outliers.
3. **The port is faithful.** Across 611 inherited souls the median mod-vs-upstream value change is
   **0**, and only 4 of 701 souls are non-monotonic across tiers (N<E<L holds everywhere else). The
   generator did not scatter values.

**Where the mod DOES stretch the top:** 8 souls now exceed amgoz1's 798 ceiling - the **Toxeus family**
(SP Toxeus 1224, Toxeus 1096, Blood Toxeus 1055) plus the mod's marquee uber/act-boss souls (Hades
1034, Meglograi 901, SP Hades 895, Murderbunny 832, Ainex 816). These are **deliberate headliners**
(SP Toxeus is documented in `BOSS_SOULS_DESIGN.md` as "THE strongest soul in the game"), not accidents.

**The one genuinely structural gap:** **boss souls are categorically ~1.8-2.3x stronger than hero
souls, even at the same level** - and this is true in amgoz1's originals too. It is a design tier, not
a bug. Details in section 5.

---

## 2. Method (transparent, and stress-tested)

Each soul is a `ArmorJewelry_Ring` with three kinds of value, scored into a common **points** currency
(1 pt is calibrated to roughly the value of +1% single-element resistance):

- **Stat budget** - signed weighted sum of every bonus field (resists, attributes, flat/% damage,
  OA/DA, speeds, leech, on-hit CC, retaliation, racial...). Resists are capped at 80% (overcap waste);
  attack/cast/run speed and %life/%damage carry the heaviest weights, matching how TQ prices affixes.
  Negative modifiers subtract (this is the **downside** axis).
- **Granted skill / summon** - the `itemSkillName` proc, scored by kind and **castability-aware**
  (an auto-controller proc fires and scores full; a manual/uncertain one is discounted). Summon souls
  reuse the pet-roster method (DPS x count + effective HP), capped at 130 pt so one pet cannot
  dominate an item score.
- **Skill augments** - `+N to <skill>` handles (7 pt/level; mastery/all levels weighted higher).

**Composite = stat_positive - downside + augments + skill/summon.** Every axis is also reported
separately, because the composite is dominated by raw stat budget at the very top (e.g. SP Toxeus is
1118 stat of its 1224) while summon/proc value matters more in the mid-pack.

> **Reading the outlier tables (sections 4a/4b):** the **Comp** column is the weighted value-index
> above (in points). The stat figures in the **Why** column are the soul's **raw in-game values** - the
> numbers you would see on the item (e.g. SP Toxeus is `+20% attack speed`, not the 80 *points* that
> attack speed contributes to Comp; Hades grants `+193 DA`, worth ~96 pts). Only single-element resists
> (weight 1.0, e.g. `+80% fire res`) read the same in both; every weighted stat - speed / %life /
> %damage / attributes / OA / DA - is shown raw in Why and differs from its point contribution to Comp.
> The "downside ~N pts" figures are the model's downside *axis* (points), not a single game stat.

**Confidence check (the weights are subjective, so this matters):**
- Re-scoring under a deliberately different weight profile (attributes/speed up 1.5-1.6x, flat/DoT/CC
  down 0.6x, resist cap 110) gives a **Spearman rank correlation of 0.978**; the strong-15 list keeps
  **13/15** and the weak-15 keeps **13/15**.
- Doubling the summon/proc axis, doubling the downside penalty, or dropping skills entirely each keep
  **12-14 of the top-15**. The strong outliers are rock-solid; the exact ordering of the weak tail is
  a little fuzzier (near-zero souls reshuffle easily, so a doubled-downside or stats-only view keeps
  only 8-9/15 of the bottom membership), but the strong membership is stable.

So treat individual point values as +/- 15% and +/-1-2 ranks as noise; the tiers and outliers are robust.

**Rank labels** come from the built loot wiring (authoritative): a soul's dropper is the monster whose
`lootFinger2Item1` points at it with `chanceToEquipFinger2 > 0`, and that monster's
`monsterClassification` is the rank. Only Hero/Boss/Quest monsters drop souls by design. "unwired"
below = no standard finger2 dropper found in this build (not necessarily unobtainable; may drop via a
chest/quest or a not-yet-wired new-content monster).

---

## 3. The full distribution (Legendary composite)

```
comp bucket   count
 -100..  -1 :   3   ###
    0.. 99  :  83   ###############################################################
  100..199  : 231   ##############################################################################################################################################################   <- mode
  200..299  : 161   ###########################################################################################################
  300..399  : 110   ######################################################################
  400..499  :  52   #################################
  500..599  :  33   #####################
  600..699  :  17   ###########
  700..799  :   9   ######
  800..899  :   3   ##
  900..999  :   1   #
 1000..1099 :   3   ##
 1200..1299 :   1   #
```

A classic right-skewed loot curve: a dense body of "ordinary" souls at 100-300 (a bit over half the
roster), a smooth shoulder to ~500, and a thin ~30-soul elite tail stretching to 1224. There is **no
bimodal cliff** and **no cluster of broken zeros** - the shape itself argues for a designed budget
rather than a mis-generated mess. Tiers scale cleanly beneath this: median composite **N 135 -> E 176
-> L 219**, and the outlier cast is the *same at every tier* (Hades/Toxeus/Meglograi on top,
Stonekeeper/Behemoth on the bottom at N, E and L alike).

---

## 4. The outliers

### 4a. TOP 15 strongest (Legendary)

| # | Soul | Comp | Rank / Lvl | Why it is strong (raw in-game stats) |
|---|---|---:|---|---|
| 1 | **sp_toxeus** | 1224 | Hero / 80 | +20% attack / +16% total speed, +20% life, +85% phys dmg; Phantom Strike+6 / Distortion Wave+5; the documented "strongest soul in the game" |
| 2 | **toxeus** | 1096 | Boss / 62 | +18% total / +20% attack speed, +80% pierce-ratio, +15% life; Lethal Strike+8 / Battle Rage+7 / +1 mastery; flashpowder proc |
| 3 | **blood_toxeus** | 1055 | Boss / 100 | +20% attack / +16% total speed, +20% life; **summons the 26k-HP Devourer**; Open Wound+5 |
| 4 | **hades** | 1034 | Boss / 78 | +53% cast speed, +193 DA, +19% life; hades_star proc; Ternion+6 |
| 5 | **meglograi** | 901 | Boss / 74 | +62% cast speed, +106% life-drain, +78% vitality dmg; burst proc |
| 6 | **sp_hades** | 895 | unwired / 80 | +48% cast speed, +22% life; bloodboil proc; Death Chill+5 / Ternion+5 |
| 7 | **murderbunny** | 832 | unwired / 80 | +25% life, +22% attack speed, +100% phys dmg; Onslaught+6 (pure-upside joke boss) |
| 8 | **ainex** | 816 | Hero / 71 | +40% cast speed, +22% dodge, +22% deflect; spiritbolt proc |
| 9 | **nightmistress** | 748 | Quest / 72 | +71% current-life on hit, +82% mana-leech, execute kit |
| 10 | **broodmother** | 745 | Boss / 74 | +100% freeze res (overcaps 80), +14% life; **summons the 30k-HP Broodmother** |
| 11 | **zilla** | 719 | unwired / 73 | +22% attack / +16% total speed, +18% life; bladetwirl ring proc |
| 12 | **talos** | 719 | Boss / 75 | **+129% total damage**, +80% fire res; flamethrower proc (downside ~55 pts) |
| 13 | **vort** | 714 | Hero / 70 | +48% cast speed, +140 INT; **summons the 36k-HP Vort tank**; Thunderball+9/+8 |
| 14 | **cerberus** | 710 | Boss / 74 | +130% poison-duration, +115% slow-poison, +99% phys dmg; breathwave proc (downside ~46 pts) |
| 15 | **jiaco** | 710 | unwired / 73 | +24% attack speed, +22% dodge, +16% life; shadowsurge proc |

Pattern: the elite is **act-boss + uber (svc_uber) souls** carrying a triple stack of (1) a fat
speed/life/damage stat block, (2) a real proc or a marquee summon, and (3) strong skill augments. Ten
of the 15 are Boss/uber; the "Hero"-ranked ones (SP Toxeus, Ainex) are actually the mod's superbosses
that happen to be classed Hero.

### 4b. BOTTOM 15 weakest (Legendary)

| # | Soul | Comp | Rank / Lvl | Why it is weak (raw in-game stats; downside axis in pts) |
|---|---|---:|---|---|
| 1 | **stonekeeper** | -69 | Hero / 66 | **downside ~239 pts**: -38% attack speed, -18% run, -64% pierce dmg; +23% life cannot offset it |
| 2 | **behemoth** | -37 | Hero / 70 | **downside ~121 pts**: -26% dodge, -43 %-current-life-taken; thin upside |
| 3 | **deathwalker** | -8 | Hero / 59 | **downside ~74 pts**: -12% attack / -13% run speed; summons a weak 49-dps zombie |
| 4 | **rocksting** | 0 | Hero / 65 | **downside ~154 pts**: -36% cast speed, -23% run; boulder proc barely pays for it |
| 5 | **sentinel** | 4 | Hero / 68 | **downside ~276 pts** (the largest): -46% cast speed, -69 petrify/mana-leech res |
| 6 | **firebeetle** | 19 | unwired / 72 | trivial: tiny fire proc, -19% cold res, almost no stats |
| 7 | **bonelord** | 23 | Hero / 58 | **downside ~116 pts**: -29% attack speed; summons a 7-dps skeleton |
| 8 | **orthus** | 31 | unwired / 44 | filler: a little flat fire damage, nothing else |
| 9 | **crowboar** | 35 | Hero / 9 | intentionally tiny (level-9 novelty soul), 18-dps crow |
| 10 | **awakeneddeadarcher** | 36 | unwired / 44 | filler: minor pierce; summons a 6-dps skeleton archer |
| 11 | **plaguebird** | 37 | unwired / 72 | filler: minor pierce + a dab of poison |
| 12 | **cindercrow** | 39 | Hero / 56 | **downside ~56 pts**: -14% life offsets a modest fire kit |
| 13 | **exhumeddeadarcher** | 40 | unwired / 44 | filler: near-identical to the other dead-archer souls |
| 14 | **minkah** | 41 | Hero / 71 | **downside ~90 pts**: -30% cast speed; summons a **0-dps** pet |
| 15 | **birdofsorrow** | 47 | Hero / 53 | filler: a little dodge + pierce, -17% pierce res |

The weak tail is **two different things**, and neither is a generator bug:
- **Heavy-downside "curse" souls** (Stonekeeper, Sentinel, Rocksting, Behemoth, Bonelord, Deathwalker,
  Minkah): amgoz1's signature high-risk souls where the penalty is deliberately large. Their felt value
  depends on the build (a -attack-speed / +life soul can suit a caster/tank), but on a neutral budget
  they net near-zero. **All are inherited from SV 0.98i unchanged.**
- **Trivial low-level filler** (the dead-archer / carrion-bird / firebeetle / orthus souls): small
  Greece/early-act monster souls with a token stat line and a near-dead summon. Cheap by design.

### 4c. The weakest summons specifically

A distinct sub-pattern worth naming: **five summon souls grant a truly dead (0-damage) pet.**
Soulfeeder, Hadronicus, Karnahk, Cliffrunner and Rainbowbright all summon a **0-damage** banner
(`drxbattlestandard` / `battlestandard` / `bonepet08` - no `attackSkillName`, no hand damage). They
score ~1 pt on the summon axis and are the true bottom of the summon roster (consistent with the
prior pet-roster ranking, where the battlestandards ranked last). *Djel is a near-miss, not a member:
its `flamesprite_3` does carry a live `flamesprite_meleeattack` (~21 dmg/hit), so it edges just above
this 0-damage floor - the value model under-credits it because it only reads ranged-skill damage or
`handHitDamage`, and skips melee `AttackInherent` skills; the prior pet-roster placed Djel at ~12 dps.
This blind spot only touches this near-dead tier, not any ranked outlier.*

---

## 5. Boss vs Hero - the categorical gap (answering Will's specific question)

| Rank (Legendary) | n | median | p10-p90 | CV (spread) |
|---|---:|---:|---:|---:|
| **Boss** | 71 | **495** | 300-655 | 0.38 (tight) |
| **Hero** | 460 | **213** | 97-398 | 0.56 (wide) |
| **Quest** | 52 | 202 | 132-372 | 0.57 |
| unwired | 124 | 161 | 59-522 | 0.82 (very wide) |

**Yes - boss souls are categorically above hero souls, by a lot.** The median boss soul (495) is
**2.3x** the median hero soul (213). And it is not just a level effect:

- **Level-controlled** (only souls at itemLevel 65-78, where both ranks live): Boss **499** vs Hero
  **275** = still **1.8x**.
- **Per-level efficiency** (composite / itemLevel): Boss **7.0** vs Hero **3.0** = **2.3x**.

Bosses are also far more **consistent** (CV 0.38 vs Hero's 0.56): almost every boss soul is a strong
soul, whereas hero souls fan out from -69 to 1224. That is the intended structure - a boss kill is
rarer and rewards a reliably premium soul; hero souls are the broad, noisy middle where amgoz1's
curses, filler, and gems all live.

The **unwired** group is the widest of all (CV 0.82) because it mixes two unlike things: the mod's
strong svc_uber uber souls (SP Hades 895, Murderbunny 832, Zilla 719, Jiaco 710, Gorgus 704) sitting
next to level-44 filler. See section 8 for the obtainability note this raises.

---

## 6. Family patterns

Soul strength tracks **where in the game the source monster lives** - a clean, intended gradient, not
a scatter.

| Strongest families (median comp) | | Weakest families (median comp) | |
|---|---:|---|---:|
| melinoe | 469 | vulture | 97 |
| sandwraith | 366 | harpy | 106 |
| machae | 360 | guardianstatue | 110 |
| lamia | 353 | carrionbird | 111 |
| keres | 346 | boar | 115 |
| dragonian | 343 | satyr | 132 |
| duneraider | 343 | (root/misc) | 148 |
| empusa | 332 | bat | 150 |

The strong families are all **late-game Immortal-Throne / Hades-act** monsters (melinoe, keres, machae,
lamia, empusa); the weak families are **early Greece-act** trash (vulture, harpy, boar, carrion-bird,
satyr). This is exactly what a level-scaled budget should produce. The one family that looks "weak"
for a non-level reason is **guardianstatue** (110), dragged down by Stonekeeper's -239 downside.

---

## 7. Intended design vs generator artifact (the headline finding)

I scored amgoz1's SV 0.98i souls with the identical model and compared.

| | souls | p90/p10 | CV | max |
|---|---:|---:|---:|---:|
| **amgoz1 (SV 0.98i)** | 611 | **4.7x** | 0.57 | 798 |
| **Mod - inherited souls** | 611 | 4.8x | 0.61 | 1096 |
| **Mod - new souls** | 96 | **6.7x** | 0.77 | 1224 |
| **Mod - all** | 707 | 5.3x | 0.65 | 1224 |

Reading:

- **The base spread is amgoz1's.** His own souls already span 4.7x with a heavy-downside weak tail. The
  inherited souls in the mod reproduce that almost exactly (4.8x). **The imbalance predates the mod.**
- **The port is faithful.** Median mod-vs-upstream change across 611 inherited souls is **0**; 554 are
  within +/-100 pt. The generator did **not** randomly widen the spread.
- **The mod stretches the TOP, deliberately.** 57 inherited souls were hand-boosted by >=100 pt - led by
  **Toxeus +592** (504->1096), Rakanizeus +485, Vort +457, Limos Lifeeater +454, Rockskin +366, Typhon
  +356. Some of these (Vort, Rakanizeus, Rockskin) are **summon souls whose gain is partly the Lane A
  pet overhaul** restoring their pet's kit - a real in-game power increase, correctly credited, not a
  scoring quirk. Others (Toxeus) are pure stat/augment hand-tuning.
- **The new souls skew strong.** The 96 mod-authored souls carry the widest internal spread (6.7x) and
  **29 of them exceed amgoz1's p90 (400)**; all 8 souls that breach his 798 ceiling are either
  mod-new svc_uber souls (SP Toxeus, Blood Toxeus, SP Hades, Murderbunny, Ainex) or the 3
  hand-boosted act-boss souls (Toxeus, Hades, Meglograi).

**Verdict:** the spread is **intended amgoz1 design, faithfully inherited, and amplified at the ceiling
by the mod's uber-boss content and Will's hand-tuning.** It is not a generator artifact. The only place
the *generator* itself could be said to contribute is that the 96 new souls were authored a notch
"hotter" than amgoz1's median envelope - a taste choice, not a defect.

---

## 8. Secondary observations (understanding only, no action implied)

1. **The downside/"curse" mechanic is an amgoz1 signature.** 49% of mod souls carry a stat penalty (52%
   upstream), heaviest on Boss (62%) and Hero (60%) souls. But the mod's **new** svc_uber souls almost
   never do (only 4% carry a downside) - so the new content is subtly more "pure upside" than amgoz1's
   originals. If the souls ever feel like they've drifted from his risk/reward flavor, this is the axis
   where it shows.
2. **Souls with a granted skill are worth more than pure-stat souls** (median: proc/attack 264, summon
   232, buff 212, pure-stat 180). The skill is genuine added value; ~38% of souls are pure-stat.
3. **Some of the mod's strongest souls have no standard dropper wired** (SP Hades 895, Murderbunny 832,
   Zilla 719, Jiaco 710, Gorgus 704, Kallixenia 638, and 6 more, all svc_uber, lvl 69-80). This is an
   **obtainability** observation, not a balance one: in this content-wave build they are not on a
   Hero/Boss/Quest finger2 drop, so either they drop by another mechanism (chest/quest) or their
   new-content monster is not yet wired. Worth a glance to confirm they are reachable.
4. **Tiers are well-behaved.** N/E/L scale monotonically (median 135/176/219); only 4 of 701 souls
   invert, and the outlier cast is identical at all three tiers. There is no tier-specific corruption.

---

## 9. One-page verdict

- **How much imbalance exists?** Moderate and by-design. Legendary souls span **5.3x** p90-to-p10; the
  strongest (SP Toxeus, 1224) is ~5.6x the median (219) and ~13x a 10th-percentile soul (94). That
  top-heavy shape is normal ARPG loot, not a defect.
- **Weakest outliers:** Stonekeeper (-69), Behemoth (-37), Deathwalker (-8), Rocksting (0), Sentinel
  (4) - all crippled by intentional amgoz1 downsides; plus a floor of trivial low-level filler
  (dead-archer/carrion souls) and 6 zero-damage summon souls (battlestandards/flamesprites).
- **Strongest outliers:** SP Toxeus (1224), Toxeus (1096), Blood Toxeus (1055), Hades (1034), Meglograi
  (901) - the Toxeus family and act/uber bosses, exactly the intended headliners.
- **Boss vs Hero:** a real, ~2x categorical gap that survives level-controlling, present in amgoz1's
  originals too. Bosses are uniformly premium (CV 0.38); heroes are the wide, noisy middle (CV 0.56).
- **Intended or artifact?** **Intended.** The 4.7x spread and the -69 weak tail are amgoz1's own,
  ported faithfully (median change 0). The mod widens to 5.3x purely by adding 96 hotter uber souls and
  hand-boosting ~57 marquee souls (Toxeus +592 leads). Nothing here reads as a build-script accident.

*Generated read-only from the built arz + SV 0.98i upstream. Probes and per-soul data:
`scratchpad/outlier_probes/` (`souls_values.json` = every soul's per-tier axis scores;
`analyze_souls.py` = the tables above; `soul_value.py` = the documented weight model). The value index
is a transparent heuristic; individual scores are +/-15%, the tiers and outliers are robust to weight
changes (Spearman 0.978).*
