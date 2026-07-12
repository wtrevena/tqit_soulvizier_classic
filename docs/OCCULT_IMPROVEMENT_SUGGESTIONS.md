# Occult (Mastery 5) - Improvement Suggestions for Will

> **What this is.** A read-only analysis of the Occult tree as it currently ships (build36, the
> content/fix-wave worktree, incl. the landed Flash Powder rework), with candid per-skill grades,
> evidence-backed weak spots, and a ranked set of *optional* improvements you can approve (or not)
> later. **Nothing here is implemented.** Occult is your hand-tuned, golden-frozen tree; every
> suggestion is written to improve *around* the cores you love, never to nerf them.
>
> **Bottom line up front:** the Occult tree is genuinely strong and well-designed - it does not need
> rescuing the way Defense/Earth/Storm did. It is the **best-rounded mastery bar in the game**, it has
> the deepest CC/utility toolkit of any tree, and Smoke Screen + Breach + (now) Flash Powder are
> excellent. There is exactly **one structural weakness** worth acting on (no spell/elemental defense -
> it is an evasion-only tree that gets thin vs Act 4-5 casters), one **underperforming pick** (the
> added Darklings), and a couple of **quality-of-life** frictions (summon mana cost when paired with
> Hunting; Smoke Screen uptime). Everything else is "leave it alone."

---

## TL;DR - the ranked recommendations

| # | Suggestion | Size | Why it matters | Touches a loved core? |
|---|------------|:----:|----------------|:---------------------:|
| **S1** | Give the tree a small, shadow-themed **spell/elemental-defense layer** (fold onto the skipped **Shadow Link** aura, or add a new optional passive) | SMALL / BOLD | The one real late-game gap: Occult defends only by dodge/deflect, which do **nothing** vs spells | No (Shadow Link is the least-used skill) |
| **S2** | **Uplift Darklings** (the added summon) so it earns its slot next to Shadow Stalker | SMALL | It is the weakest real pick - fragile, low damage, dominated by Shadow Stalker | No (Darklings is an *added* skill, not original) |
| **S3** | Ease the **summon/caster mana pinch** (matters most with your Hunting pairing) | SMALL | Shadow Stalker 500 + Breach 130 + Darklings 346 mana on a 400-mana bar; Hunting adds 0 mana | Light touch only |
| **S4** | *Optional:* nudge **Smoke Screen uptime** (42% now) - only if it ever feels off | SMALL | 25s cloud / 60s cooldown; you love it as-is, so this is a "lever, not a recommendation" | Yes - proposed as no-op unless you ask |
| **S5** | *Optional:* fix two **tooltips** that hide real synergies (Nether Strike works with bows; dagger flags) | SMALL | Pure text accuracy, amgoz's own standard; no mechanical change | No |

Detail, field-level specifics, risk, and an amgoz1-voice check for each are in **section 3**.

---

## 1. The tree as it stands

Occult (internally the DRX "Stealth" tree, `records\skills\stealth\drxstealthskilltree.dbr`) is a
27-slot renamed-and-retooled version of the classic Rogue mastery: an **assassin / poisoner / shadow
summoner** built on **pierce + poison + bleed + vitality** damage, with an unusually deep control kit.
It is frozen to SV 0.98i - a build-vs-SV field diff finds **the only value change in the whole tree is
Flash Powder** (everything else is byte-identical to amgoz's DRX tree, which *is* your golden bar).

**How to read the grade column:**
- **AUTO** = almost every Occult build takes it; a pillar of the tree.
- **SOLID** = a strong, build-defining pick within its line (poison / melee / thrower / summoner).
- **SITUATIONAL** = good only in a specific build or as a filler point.
- **DEAD** = rarely worth a point. *(There are essentially none - a credit to the design.)*

### Per-skill table

Mana/cooldown shown at the skill's top level. "Ult" = `skillUltimateLevel` (the hard cap with +skills).

| Slot | Skill (display) | Line / role | Max/Ult | Mana | CD | What it does | Castability | Grade |
|:---:|---|---|:---:|:---:|:---:|---|---|:---:|
| 1 | **Occult Mastery** | mastery bar | -/40 | - | - | Life 1200, Mana 400, Str 62 / **Dex 100** / Int 60, **+21% DA, +21% OA, +20% dodge** at L40 | passive | **AUTO** |
| 2 | **Envenom Weapon** | poison (toggle) | 12/16 | 50 reserve | - | Coats weapon w/ poison 2.4-39 (min) over 6s; works on **all weapons incl. bow/staff** | any weapon | **SOLID** |
| 3 | **Nightshade** | poison mod | 8/12 | 25 reserve | - | Adds -10..50% slow (5s) to Envenom | - | SOLID |
| 4 | **Mandrake** | poison mod | 8/12 | 0.5/s | - | Adds 12-56% chance to confuse (1.8-6.5s) + fumble 15-70% | - | SOLID |
| 5 | **Toxin Distillation** | poison capstone | 12/16 | - | - | **+35..350% poison damage** to everything | passive | SOLID |
| 6 | **Shadow Link** | aura (toggle) | 12/16 | life-drain | - | 3u aura: **+1..18 mana regen**, +1.2-9.2 life-leech, +26-200% pierce ratio, slow-life - **at cost of -5..-50 vitality resist + 1-12 life/s** | any weapon | **SITUATIONAL** |
| 7 | **Dark Invigoration** | bleed/life | 8/12 | - | - | +3-42 flat life dmg + bleeding on **all weapons** | passive | SOLID |
| 8 | **Shadow Lore** | bleed/life mod | 8/12 | 1-12 life/s | - | **+33-100% life dmg, +66-200% bleeding**, +15-50 vitality resist; costs life/s | passive | SOLID |
| 9 | **Throwing Knife** | thrower | 12/16 | 18-33 | 6 | Piercing throw 17-113 + bleed 19-138 (3s); **scales with your weapon** (`projectileUsesAllDamage`) | ranged, no weapon req | SOLID |
| 10 | **Flurry of Knives** | thrower mod | 6/10 | 5-10 | - | **+1..8 projectiles** + pierce mod on Throwing Knife | - | SOLID |
| 11 | **Calculated Strike** | melee (charge) | 8/12 | 14-100 | **6->1** | Spammable charged hit: +45-100 OA, +75-130% run, fumble 15-55%, pierce+bleed, fear | Sword/Axe/Spear | **AUTO** (melee) |
| 12 | **Blade Fury** | melee proc | 8/12 | 9-20 | 6 | Chance-on-hit cleave (1-4 targets, 90 deg): +phys/pierce mod | Sword/Axe | SOLID |
| 13 | **Nether Strike** | melee (blink) | 12/16 | 55-92 | 14 | Blink gap-closer, **+225-600% phys, +225-450% pierce**, fear; run 500% | **all melee + Bow** | **SOLID** |
| 14 | **Dark Vapors** | melee mod | 8/12 | 15 | - | **+60-445% life/bleed/slow-life** on Nether Strike + 3s stun | - | SOLID |
| 15 | **Flash Powder** *(reworked)* | AoE control | 8/12 | 53-86 | **6** | Self-centered blast r4.8-11.4: **blinds melee (fumble 30-85%) AND ranged (projectile fumble 30-85%, 8s)**, confuse 30-85%, **pierce dmg 40-260** | no weapon req | **SOLID** |
| 16 | **Toxic Concoction** | thrower (bomb) | 8/12 | 52-82 | 8 | Lobbed bomb, pierce 26-92 + bleed 22-88, 6-16 shrapnel fragments | no weapon req | SOLID |
| 17 | **Poisonous Gas** | bomb mod | 8/12 | 12-42 | - | Adds poison 22-84 (6s) + -20-42% slow to the bomb | - | SOLID |
| 18 | **Aphotic Ichor** | bomb mod | 12/16 | 76-148 | - | Adds **-15-45% enemy resist AND -15-45% enemy damage** (8s) + slow-life to the bomb | - | **SOLID** (strong debuff) |
| 19 | **Breach** | AoE nuke | 12/16 | 55-130 | **9.75->6** | Ranged vitality bomb 12-65 + **48-93% life-leech**, lingering pool 6-9s, ragdoll-pull | ThunderClap (staff-safe) | **AUTO** |
| 20 | **Shadow Grasp** | Breach mod | 12/16 | 1-16 | - | Adds **guaranteed AoE petrify 2-3.75s + immobilize + life-DoT 32-226** to Breach | - | **AUTO** (w/ Breach) |
| 21 | **Agility** | passive | 6/10 | - | - | **+22-100% cast speed**, +5-25% deflect projectile, +5-25 DA | passive | **AUTO** |
| 22 | **Blade Mastery** | passive (DW) | 8/12 | - | - | Dual-wield: +5-25% atk speed, +11-90 DA, +5-25% dodge, +5-25 OA | dual-wield only | SOLID |
| 23 | **Smoke Screen** | control zone | 8/12 | 27-103 | 60 | Throws a smoke device (25s): 20u zone of **-54% enemy OA, -60% enemy DA, -42% slow, up to -100% ranged accuracy** | no weapon req | **AUTO** |
| 24 | **Shadow Stalker** | summon (bruiser) | 16/20 | 139-500 | 60 | 1 permanent demon: **2210 life / 386-492 dmg** at top tier, full tiered kit | - | **AUTO** (summoner) |
| 25 | **Channel (Greater Power)** | Stalker unlock | -/16 | - | - | Unlocks the Stalker's 5-tier kit: Shadow Strike / Rush / Plague / Sprites / Bolts | passive | **AUTO** (w/ 24) |
| 26 | **Darklings** *(added)* | summon (swarm) | 16/20 | 80-346 | 30 | Up to 3 **fragile** shadow demons (678 life at 20) that **explode on death**; immune to poison/vitality | no weapon req | **SITUATIONAL** |
| 27 | **Dark Aperture** *(added)* | Darklings mod | 8/12 | - | -CD | -5.4..-17.4s cooldown + -12-40 mana on Darklings (small conversion-resist cost) | - | SITUATIONAL |

### What the shape of the table tells you

- **Almost no dead points.** For a 27-slot tree that is remarkable. The only genuinely soft picks are
  Shadow Link (slot 6) and the added Darklings pair (26-27). That density is why the tree "feels good."
- **Three partly-siloed damage identities** live in one tree: a **physical/pierce melee** assassin
  (Calculated Strike -> Blade Fury -> Nether Strike -> Dark Vapors + Blade Mastery), a **poison/bleed
  DoT** engine (Envenom -> Nightshade -> Mandrake -> Toxin Distillation + the bomb line), and a
  **vitality/summoner caster** (Breach + Shadow Grasp, Flash Powder, Smoke Screen, Shadow Stalker,
  Darklings). Any one build lights up ~2/3 of the tree and leaves the rest as "not my build" - that is
  breadth, not a defect, but it is why a given character sees some skills as skippable.
- **The control toolkit is the tree's signature and is excellent:** blind (Flash Powder melee+ranged,
  Smoke Screen ranged, Calculated Strike, Mandrake), confuse (Flash Powder, Mandrake), **petrify**
  (Shadow Grasp), immobilize (Shadow Grasp), slow (Nightshade, Poisonous Gas, Smoke Screen, Aphotic
  Ichor, Shadow Grasp), stun (Dark Vapors), fear (Calculated/Nether Strike), and **-45% enemy
  resist/-45% enemy damage** (Aphotic Ichor). This is exactly amgoz's stated Occult identity:
  *"manipulating hordes of enemies and striking from the shadows."*
- **The mastery bar is the best-rounded of all 12 trees** (see next section) - a hidden pillar.

---

## 2. Evidence: where Occult sits vs its siblings

### 2.1 The mastery bar is a strength, not a weakness

Attribute grants at full base investment (mastery level 40), measured from the built DB:

| Tree | Life | Mana | Str | Dex | Int | DA mod | OA mod | Dodge |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Warfare | 1600 | 0 | 80 | 80 | 0 | - | - | - |
| Defense | 2000 | 0 | 80 | 60 | 0 | - | - | - |
| Earth | 1120 | 480 | 0 | 60 | 120 | - | - | - |
| Storm | 900 | 880 | 0 | 40 | 120 | - | - | - |
| **Occult** | **1200** | **400** | **62** | **100** | **60** | **+21%** | **+21%** | **+20%** |
| Hunting | 1300 | 0 | 70 | 100 | 0 | - | - | - |
| Nature | 800 | 640 | 0 | 60 | 100 | - | - | - |
| Spirit | 800 | 320 | 0 | 60 | 120 | - | - | - |
| Dream | 1400 | 320 | 80 | 0 | 70 | - | - | - |

**Occult is the only mastery in the game whose bar grants Defensive Ability, Offensive Ability, and
Dodge on top of all three core attributes.** Everyone else's bar is life + one or two stats. That makes
Occult uniquely self-sufficient: it hits harder (OA), gets hit less (DA + dodge), and can build toward
melee, ranged, poison, *or* caster because it feeds Str/Dex/Int all at once. Life 1200 is mid-pack
(a hybrid, not a tank); Mana 400 is respectable but see 2.3.

### 2.2 The one structural weak spot: no defense against spells

Occult's entire defensive identity is **evasion**: dodge (20% mastery + 25% Blade Mastery), deflect
projectile (25% from Agility - the tree's only source; the mastery bar grants none), and DA (21%
mastery + 90 Blade Mastery). In this engine:

- `characterDodgePercent` avoids **melee** attacks only.
- `characterDeflectProjectile` avoids **arrows/thrown projectiles** only.
- **Neither avoids spells.** And the tree carries **zero** `defensiveElementalResistance`, **zero**
  `defensiveAbsorption`, and **zero** flat/percent damage reduction anywhere.

Compare: Defense front-loads elemental resist on its mastery; Storm has an energy-shield line; even
Nature/Spirit hand out protection. Occult vs an Act 4 Hades spell-mob or an Act 5 caster is a
wet-paper glass cannon that survives on **raw 1200 life + whatever resists your gear rolls**. Some of
this is deliberate identity (an assassin *should* dodge, not armor up), but the **total absence of any
spell mitigation** is the tree's real late-game cliff. This is S1.

### 2.3 The mana pinch, especially with Hunting

Top-level mana costs stack up fast for a caster/summoner Occult: **Shadow Stalker 500**, Darklings 346,
Aphotic-Ichor bomb 148, Breach 130, Smoke Screen 103, Flash Powder 86 - against a **400-mana bar** and
75 of that reserved by Envenom+Nightshade if you run poison. The tree's only intrinsic mana sustain is
**Shadow Link** (+1-18 regen), which almost nobody takes because it is a tiny 3-unit aura that drains
your life and vitality resistance to run.

This bites hardest with your current **Hunting** pairing: Hunting is a pure-dex tree that grants **0
mana** from its bar. So an Occult+Hunting summoner/caster funds every expensive Occult active from
Occult's 400 + gear alone. (It is a non-issue for a pure weapon/poison Occult - those actives are cheap
- so this is a build-specific friction, not a universal one.) This is S3.

### 2.4 Occult + Hunting is otherwise a genuinely coherent pairing

The two trees dovetail: both are **Dex-primary** (Dex 100 each - 200 from bars alone), both flex
**bow + melee**, and both deal **pierce/bleed**. Hunting supplies precisely what Occult lacks -
**healing sustain (Herbalism - the potion/health-regen passive Occult has no equivalent of)**,
**mobility (Trail Blazing)**, **resist-shred (Study Prey)** that stacks with Aphotic Ichor's -45%,
and **a damage aura (Art of the Hunt)** - while Occult supplies
poison, the Breach/Flash Powder AoE, the deepest CC in the game, pets, **+100% cast speed (Agility)**,
and the all-rounder bar. Several Occult skills are *made* for a bow: **Envenom Weapon** and **Nether
Strike** both work with bows (poison arrows + a blink-shot), and **Throwing Knife scales off your
equipped weapon**. The only seam is mana (2.3). No change is needed here - it is called out so the
suggestions below respect it.

### 2.5 The Flash Powder rework (landed) is correct

Confirmed in the built DB: cd 15 -> 6, radius 4.8-11.4, and it now blinds **both** melee
(`offensiveFumbleMin` 30-85) and ranged (`offensiveProjectileFumbleMin` 30-85, 8s), confuses
(30-85%), and deals real pierce (40-260). This turned your "trash/unviable" skill into a legitimate
panic-button AoE control. No further change recommended - it is done and good.

---

## 3. Ranked suggestions

Each is written so it *could* be implemented later as a field-level edit if you approve. Sizes:
**SMALL** = a few field edits on one/two records; **MEDIUM** = a coordinated set; **BOLD** = a new
skill/slot (allowed by the "never remove, may add" rule, but more work: new tags, icons, panel button,
and a golden-freeze override).

> Note on the freeze: Occult is gated by `validate_mastery_golden.py` / `occult_hunting_golden.json`.
> Any of these edits ships only after you sign it off, at which point the touched fields get an
> `owner_approved_overrides` entry (exactly like the Flash Powder rework did). None of this happens
> without your say-so.

---

### S1 - Close the spell-defense gap (the one real weakness)  ·  SMALL (preferred) or BOLD

**What.** Give Occult a modest, shadow-themed layer of spell/elemental mitigation. Two ways, pick one:

- **S1a (SMALL, recommended): fold it onto Shadow Link** (`drxbladehoningbuff.dbr`), the skill almost
  no one takes today. Add a ladder such as `defensiveElementalResistance` ~+3..12% (L1-16) and/or a
  small `defensiveLifeMax` (vitality-resist) bump, **while keeping - or slightly increasing - its
  existing life-drain cost** (`defensiveLife -5..-50`, `skillActiveLifeCost 1-12/s`). This does two
  jobs at once: it patches the spell-defense hole *and* it makes the tree's most-skipped skill worth a
  slot (also resolves S5 below). Field-level: edit `records\skills\stealth\drxbladehoningbuff.dbr`,
  add the `defensiveElementalResistance` array (len 16 to match `skillUltimateLevel`).
- **S1b (BOLD, alternative): a new optional passive** at a free slot (28), e.g. *"Umbral Ward"* /
  *"Shadowmeld"* - a small `defensiveAbsorptionModifier` or flat `defensiveElementalResistance` with a
  drawback (say -run speed or a life cost while active), themed as wrapping yourself in shadow. This is
  cleaner thematically (a dedicated defensive button) but costs new tags/icon/panel wiring and a bigger
  freeze override.

**Why.** Section 2.2 - dodge/deflect do nothing vs spells and the tree has no other mitigation; this is
the late-game cliff.

**Expected feel.** An Occult character stops evaporating the instant it meets a caster pack, without
becoming a tank. You *choose* to give up some life/resistance-elsewhere to buy spell survivability -
you stay squishy-by-choice, not squishy-by-omission.

**Risk.** Low for S1a (touches a rarely-used aura, not a loved core; bounded numbers). Medium for S1b
(new content surface). Keep the resist modest (single digits to low-teens %) so Occult never
out-tanks Defense.

**amgoz1-voice check.** Strong fit. amgoz's rule is *power is always paid for* (Colossus Form gets
slower; Stone Skin trades % for flat). Shadow Link already embodies exactly that trade (mana/leech for
a life drain), so adding resistance *there*, still paid for in life, is the most amgoz-authentic
possible home for this. S1b is also in-voice (a "system verb" defensive skill with a cost) but is a
bigger invention.

---

### S2 - Make Darklings earn its slot  ·  SMALL

**What.** Uplift the added Darklings summon so it is a real alternative to Shadow Stalker instead of a
strictly-worse pick. Levers (any subset), on the pet ladder
`records\skills\stealth\drxpet\drx_shadowdemon_01..20.dbr` and/or the boom skills:
- Raise the **death-explosion damage** (their actual payload - `drx_petskill_boom` /
  `drx_1stboom_chain_synergy`), since the demons are *designed* to die and explode.
- And/or a modest **life bump** (678 at tier 20 is low) so they survive long enough to reach a pack and
  detonate - keep them fragile, just not suicidal-on-arrival.
- And/or **+1 petLimit** at the very top tiers (currently 1->3) for a fuller swarm.

Keep their identity intact: glass-cannon, explosive, poison/vitality-immune, cheap-ish, short cooldown.

**Why.** Darklings (678 life, 43-71 hand dmg at tier 20) is dominated by Shadow Stalker (2210 life,
386-492 dmg) for the price of a comparable slot. As-is it is a SITUATIONAL/near-dead pick, which is a
shame because a *fragile explosive swarm* is a distinct, fun archetype next to the single bruiser.

**Expected feel.** A summoner Occult gets a real choice: one durable stalker, or a disposable pack of
shadow-bombs you throw into crowds. Both viable, different playstyles.

**Risk.** Low-medium (pet tuning; the boom already exists, so this is mostly number tuning). It is an
*added* skill, so it is the least "sacred" thing in the tree - the safest place to tune. Needs a
golden override key since it lives under the frozen tree, but it changes no original amgoz record.

**amgoz1-voice check.** Strong fit - amgoz's V6/V14: *every summon tier should be mechanically
meaningful*, and he iterated per-object to make summons pull their weight. Uplifting an
underperforming summon to a coherent role is squarely his standard.

---

### S3 - Ease the summon/caster mana pinch  ·  SMALL (optional)

**What.** Give caster/summoner Occult a little more mana headroom - pick the *least* invasive lever:
- **Trim the top of Shadow Stalker's mana curve** (`drx_summon_shadow_stalker.dbr`
  `skillManaCost` 139-500 -> e.g. 139-430). It is by far the single most expensive active in the tree.
- **Or** reduce the Envenom+Nightshade **reserve** (50+25=75) slightly, freeing standing pool.
- **Or** a small `characterManaRegen` bump on Shadow Link (ties into S1a; makes that skill the
  deliberate "sustain aura").

Only *one* of these is needed; do not stack them.

**Why.** Section 2.3 - the expensive actives (Shadow Stalker 500, Darklings 346, Breach 130) sit on a
400-mana bar, and your Hunting pairing adds 0 mana. A pure weapon/poison Occult never feels this, so
keep the change small and targeted at the summon/caster line.

**Expected feel.** You can actually re-summon and cast in a long fight without hard-stalling on mana,
without turning Occult into a mana-rich caster class.

**Risk.** Low. The caution is not to over-give - Occult should still *want* mana on gear; it is not
Earth/Storm.

**amgoz1-voice check.** Neutral-to-good. amgoz prices things deliberately; a *small* affordability
tune on the most expensive summon is reasonable, but he would resist making the class mana-carefree, so
keep it a trim, not a giveaway. Rank this **below S1/S2** - it is a comfort fix, not a gap fix.

---

### S4 - Smoke Screen uptime  ·  SMALL (optional, proposed as a no-op)

**What.** *If and only if* you ever feel Smoke Screen's downtime, the surgical levers are on
`records\skills\stealth\drxlaytrap_petmodifier_multishotbolttrap.dbr`: `skillCooldownTime` /
`skillCooldownReductionModifier` 60 -> ~45, **or** `spawnObjectsTimeToLive` 25 -> ~35. Either raises the
42% uptime (25s cloud / 60s cd) toward ~55-60%.

**Why.** It is currently your single best defensive-control button but is available under half the
time. Raising uptime would make the "smoke-controlled" playstyle you enjoy more continuous.

**Expected feel.** Smoke up more often; fewer naked windows.

**Risk.** Low mechanically - **but you have explicitly said you *like* Smoke Screen as it is.** So this
is filed as a *lever you can pull*, not a recommendation. Default: **leave it exactly as-is.** If
anything, the zone is already extremely strong (-54% OA / -60% DA / -100% ranged accuracy), so more
uptime could tip it from "great" to "trivializing," which is why I would not touch it unprompted.

**amgoz1-voice check.** amgoz balances strong effects with real downtime (auras/summons on long
cooldowns). The 42% uptime is likely *his* intentional tradeoff, so changing it deviates from his
tuning. Only pull this if play tells you to.

---

### S5 - Tooltip accuracy (two hidden synergies)  ·  SMALL (optional)

**What.** Two text-only fixes, no mechanics touched:
- **Nether Strike** (`drxlethalstrike.dbr`) is flagged usable with **Bow** (`Bow = 1`) but its
  description says *"All Melee Weapons."* It actually works as a blink-strike for **bow** builds too -
  a real gift for your Hunting pairing that the tooltip hides. Update the `^y(...)` weapon line to
  mention bow.
- **Calculated Strike / Blade Fury** descriptions say *"Dagger"* is allowed; the records flag
  Sword/Axe(/Spear) and rely on daggers counting as swords. Worth a 30-second in-game check that a
  dagger actually triggers them; if it does, the text is fine, if not, add the flag.

**Why.** amgoz's own bar is *no soul/skill ships broken or with a wrong description* (V14). Accurate
tooltips are his standard, and #1 actively surfaces an Occult+Hunting combo you would enjoy.

**Expected feel.** No power change; you *discover* that Nether Strike is a bow skill.

**Risk.** Near-zero (text). Only caveat: editing a Text tag on a frozen skill still trips the golden
gate, so it needs the same sign-off ritual.

**amgoz1-voice check.** Perfect fit - this *is* his standard.

---

## 4. DO NOT TOUCH - the loved cores and load-bearing design

These are the things the analysis shows your builds lean on and/or that you have named as good. Leave
them frozen; improve *around* them.

- **Smoke Screen (slot 23)** - you rate it highly, and it is one of the best control abilities in the
  whole mod (20u zone, -54% enemy OA / -60% enemy DA / -42% slow / up to -100% ranged accuracy,
  non-dispelable). The *only* even-arguable change is uptime (S4), and that is proposed as a no-op.
  **Do not touch its effect, radius, or numbers.**
- **Breach (slot 19) + Shadow Grasp (slot 20)** - you rate Breach highly; together they are the tree's
  AoE + hard-CC centerpiece (vitality nuke + life-leech + guaranteed AoE petrify + immobilize + life
  DoT). **Leave entirely alone.** Any AoE-defense concern is handled elsewhere (S1), not here.
- **Flash Powder (slot 15)** - just reworked to your spec and confirmed good. **Done; no further edits.**
- **Occult Mastery bar (slot 1)** - the best-rounded bar in the game and the reason the class flexes
  into any build. Its DA/OA/dodge/tri-attribute spread is a signature. **Do not rebalance it.**
- **Agility (slot 21)** - +100% cast speed / +25% deflect / +25 DA for a cheap passive is a quiet
  pillar (it is what makes the caster and summoner lines feel responsive). **Leave it.**
- **The Calculated Strike -> Nether Strike melee line** and the **Envenom -> Toxin Distillation poison
  line** - both are complete, well-tuned amgoz chains. Not weak, not in need of help.
- **General rule:** honor the freeze. Occult is not a tree that needs buffing to reach the bar - it
  *is* the bar. The suggestions above are gap-fills and polish (S1 real, S2 worthwhile, S3-S5 optional),
  not a rebalance. When in doubt, do less.

---

## Appendix - how this was measured (reproducible, read-only)

- Built DB analyzed: `\.claude\worktrees\build36-content\local\build36c\Database\SoulvizierClassic.arz`
  (newest artifact; a superset that merges the fix-wave, so it carries the Flash Powder rework and the
  Shadow Stalker overhaul). Baseline: `upstream\soulvizier_098i\Database\database.arz`.
- Text tags resolved from the built `Resources\Text.arc` + upstream `Text_EN.arc`.
- Probe scripts (rerun with `PYTHONIOENCODING=utf-8 py <script>` from repo root) live in
  `...\scratchpad\ho_probes\`: `probe_occult.py` (roster), `probe_occult_detail.py` (per-slot fields),
  `probe_keyskills.py` (full non-zero fields + descriptions for every active), `probe_pets_mastery.py`
  (12-tree mastery-bar comparison + summon pet bodies), `probe_freeze_bolttrap.py` (built-vs-SV freeze
  diff + Smoke Screen internals), `probe_smoke_hunting.py` (Smoke Screen aura numbers + Hunting roster).
- Freeze verification: a field diff across all 25 shared stealth skills found the **only** value delta
  is Flash Powder (cd 15->6, pierce added) - confirming Occult == amgoz's SV 0.98i DRX stealth tree
  plus the two added Darkling slots and the Shadow Stalker pet overhaul, exactly as the deviations
  ledger states.
