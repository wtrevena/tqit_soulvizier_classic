# Hunting (Mastery 6) - Improvement Suggestions for Will

> **Status: SUGGESTIONS ONLY. Nothing here is implemented, and nothing should be until you say so.**
> Hunting is golden-frozen (slot 6). Every change below that touches a real Hunting record needs your
> explicit sign-off **and** an `owner_approved_overrides` key in `tools/occult_hunting_golden.json`
> (the same mechanism the Flash Powder F5 rework used) or the build gate will reject it on purpose.
>
> **What I verified first (so you can trust the rest):** I re-proved, with my own probe against the
> newest built arz (`build36-content` wave, `SoulvizierClassic.arz`, 2026-07-11), that Hunting is
> **mechanically identical to amgoz1's SV 0.98i** - 150 Hunting records, and every single field that
> differs from SV is a C1 display-field injection (`sv: None -> the effective value`), i.e. **zero
> gameplay value changes, zero balance edits, zero grafts.** The anim-castability gate **passes** for
> Hunting (0 cast-abort skills - it is actually cleaner than Warfare/Earth/Storm/Spirit were before
> Wave 1). So this is a mature, complete, well-built tree. My job was to find where being frozen-at-SV
> has left small warts or made it lag the *tuned* siblings - not to "fix" a tree that mostly does not
> need it.
>
> **Bottom line up front:** Hunting does **not** lag on power - the 2026-07-09 audit uses it as the
> *secondary balance bar*, and nothing in the mod is above it. What it has are (a) three genuine
> **SV-inherited warts** worth cleaning, (b) one **numeric gap** (mana) that is real but is also a
> deliberate amgoz1 design choice, and (c) an **additive** opportunity if you want Hunting to *gain*
> something rather than just be tidied. I recommend doing the three cleanups, treating the mana item as
> a pure feel call, and only pursuing additive content if you actively want it.

---

## 1. Recommendations first - the ranked list

Each item: what to change (field-level, so it is implementable later), why, expected feel, risk, size,
and an amgoz1-voice check. Ordered by value-per-risk (do the top ones first).

### S1 - Strip the hidden charm-resistance penalty on Rapid Construction  ·  **SMALL**  ·  *recommended*
**Record:** `records\skills\hunting\drxmonsterlure_rapidconstruction.dbr` (Rapid Construction, the Lay
Trap cooldown modifier).
**Change:** remove/clear the `defensiveConvert` array. It is currently
`[-3.6, -5.4, -7.2, -8.8, -10.4, -12.0, -13.2, -14.4, -15.6, -17.0, -18.4, -19.8]` - **byte-for-byte
identical to the record's own `skillCooldownTime` ladder.** Keep `skillCooldownTime` and
`skillManaCostReduction` exactly as they are.
**Why:** this is the textbook "`defensiveConvert == skillCooldownTime` copy-paste artifact" that the
2026-07-09 audit called out as a systemic SV-port defect (section 4-C) and **already cleared on the
tuned Nature tree** (Accelerated Growth, Wave 2 - I re-proved its SV `defensiveConvert` ladder is
blanked in the built arz). It is genuinely systemic, not a one-off: Defense's Resilience
(`drxadrenaline_resilience`) *still* carries the identical `defensiveConvert == skillCooldownTime`
artifact in the current build. A negative
`defensiveConvert` silently lowers the player's **charm/conversion resistance**, so every point you put
into Rapid Construction quietly makes you *easier to charm* - up to **-19.8%** at max. It is pure
downside with zero intended payoff; amgoz clearly duplicated the cooldown array into the wrong field.
Hunting only still carries it because it was frozen before that sweep ran. I confirmed it is present in
SV 0.98i (inherited, not mod-introduced) and that the golden gate captures the field.
**Expected feel:** imperceptible in normal play except that you stop bleeding charm resistance - a
strict, invisible improvement. No damage, cooldown, or uptime changes.
**Risk:** none. Removing a penalty with no upside cannot regress anything; it matches the
already-shipped, already-approved fix pattern from the Nature tree.
**amgoz1 check:** PASS - this is faithfulness restoration, not a rebalance. amgoz's own changelog is a
wall of per-object bug fixes (voice doc V14); he would want this corrected. "Power without cost" is on
his never-ship list (V15/neg-#12), and this is *cost without power* - the same sin inverted.
**Golden handling:** needs one `owner_approved_overrides` entry for
`drxmonsterlure_rapidconstruction.defensiveConvert` + your sign-off.

### S2 - Fix the two skills both named "Eviscerate" (and their blank tooltips)  ·  **SMALL**  ·  *recommended*
**Records:** `records\skills\hunting\drxspear_tempest.dbr` and
`records\skills\hunting\drxtakedown_eviscerate.dbr`. **Both** currently set
`skillDisplayName = tagSkillName090` ("Eviscerate") and **both** have **no `skillBaseDescription`** -
so the mastery panel shows two adjacent nodes (grid 428,279 and 428,341) that are *both* labelled
"Eviscerate" with *blank* tooltip bodies.
**Change:** author a new name/description pair `tagTempestNAME` = "Tempest" (or "Spear Tempest") +
`tagTempestDESC`, and point `drxspear_tempest.skillDisplayName -> tagTempestNAME`,
`skillBaseDescription -> tagTempestDESC`. Give `drxtakedown_eviscerate` a real `skillBaseDescription`
(a short "a savage cleave that leaves deep bleeding wounds" line) so the remaining "Eviscerate" node
also has a tooltip.
**Why:** `drxspear_tempest` is the wide 300-degree, 12-target **fear + confusion + slow** spin (its own
record name is `..._tempest`, and its modifier higher in the same spear column is literally named **"Flayer"**
/`drxtempest_expose`); `drxtakedown_eviscerate` is the 3-target bleed cleave. Calling the CC spin
"Eviscerate" is a plain SV mislabel - I confirmed both point at `tagSkillName090` in SV 0.98i, so it is
inherited. Two identically-named, tooltip-less nodes is confusing exactly where a new Hunter is trying
to understand the spear line.
**Expected feel:** the spear column finally reads correctly - **Tempest** = the crowd-control spin,
**Flayer** = the modifier that turns it into a damage spin, **Eviscerate** = the single-target bleed
cleave. No mechanics change at all.
**Risk:** cosmetic only - display name + description text. No values touched.
**amgoz1 check:** PASS - names tracking the record/taxonomy is exactly his grammar (voice doc V8), and
fixing a mislabel is V14. The new "Tempest" text just needs to match the base-game register (V12): plain,
mythic, grounded - no jokes.
**Golden handling:** touches `skillDisplayName`/`skillBaseDescription` on two frozen tree records +
adds two tags -> needs `owner_approved_overrides` keys + a golden refresh + your sign-off.

### S3 - Rewrite the two garbled skill descriptions (Scatter Shot, Gouge)  ·  **SMALL**  ·  *recommended*
**Tags:** `tagSkillDescription171` (Scatter Shot Arrows) and `tagSkillDescription172` (Gouge), in
`Text.arc`.
**Current (wrong) text:**
- Scatter Shot Arrows -> *"The power of the Quillvine grove revitalizes those within and reduces the
  energy consumed by skill use."* (This describes an energy-cost aura, not a multi-arrow attack.)
- Gouge -> *"Increased barb growth causes Quillvines to fire multiple barbs on attack."* (Quillvine is a
  *monster*; Gouge is a bleeding weapon strike.)
**Change:** rewrite both to describe what the skills actually do. Scatter Shot fires a spread of
fragment arrows (`projectileFragmentsLaunchNumberMin`/`Max` ladders: 3-5 at rank 1, rising to 7-9 at
max) with bonus pierce + bleed; Gouge is a weapon strike with a heavy bleed proc
(`offensiveSlowBleedingMin` 16->125 over 3s) weighted into your left-click pool.
**Why:** these are SV authoring errors (the records point at the same tags in SV 0.98i). A player
reading the tooltip gets text that has nothing to do with the skill - the single most confusing kind of
tooltip. Marksmanship (169), Puncture Shot (170) and Volley (173) descriptions are all correct; only
these two are cross-wired.
**Expected feel:** tooltips finally describe the skills. Zero mechanics change.
**Risk:** cosmetic only.
**amgoz1 check:** PASS - V12 (register-matched prose) + V14 (per-object correctness). Keep it plain and
functional, the way his real reagent/skill lines read.
**Golden handling:** these tags are captured by the golden snapshot -> needs sign-off + a golden refresh
if you change the tag *values*.

### S4 - Optional: a modest mana pool on the Hunting mastery  ·  **MEDIUM**  ·  *feel call - your decision*
**Record:** `records\skills\hunting\drxhuntingmastery.dbr`. Today `characterMana = 0.0` (no mana ladder
at all).
**Change (if you want it):** add a `characterMana` 40-entry ladder in the ~4-5/level range, capping
around **160-200 at ML40** - well under Occult's 400, and **add no Intelligence** (keep Hunting pure
DEX/STR).
**Why this is the real numeric lag:** Hunting is the *only* mastery in the mod whose mastery bar grants
**zero** mana. Every tuned sibling now has a pool (Occult 400, Storm 880, Earth 480 after Wave 1, even
RuneMaster was fixed 0->400 because it was "the sole 0-mana INT mastery"). And Hunting's active rotation is
genuinely mana-hungry: Take Down 30->60, Eviscerate 41->86, Lay Trap 34->110, Tempest 33->66, Call of
the Hunt 45->67, Study Prey 35, Ensnare 15->41. A single-mastery or DEX/DEX Hunter leans hard on
+energy gear to keep that rotation running.
**The honest tension (why this is a feel call, not a bug fix):** in *vanilla* TQ **both** weapon-DEX
masteries - Hunting and Rogue - grant 0 mana; only the caster masteries do. amgoz1 then **deliberately**
gave his reworked Occult a 400 pool *plus* 60 Intelligence (making it a weapon+caster hybrid) while
leaving Hunting the pure-weapon tree, and he traded Hunting **+100 mastery HP** for it (Hunting 1300 vs
Occult 1200 at ML40). So the 0-mana is not an oversight - it is the deliberate "pure hunter vs
occult-hybrid" distinction, paid for in HP. Adding mana erodes that distinction.
**Expected feel:** noticeably smoother sustained casting for pure-Hunting builds; less reliance on
energy gear. Also nudges Hunting slightly away from its "lean, weapon-only" identity.
**Risk:** medium - it is a resource-identity change, not a bug fix. If you already think Hunting feels
good on mana (you said the tree "is good"), skip it. If you find the late-game active rotation
stuttering, the modest ladder is the measured version. **Recommendation: leave it unless you personally
feel mana-starved on your current character.**
**amgoz1 check:** MIXED - his own Occult precedent shows he is willing to fund a skill-heavy DEX tree
with mana, so a *small* pool is within his instincts; but he specifically chose *not* to for Hunting,
and traded it HP instead (V15, characterization-through-tradeoff). Keeping the grant small and INT-free
is what keeps it defensible.
**Golden handling:** edits a frozen mastery record -> `owner_approved_overrides` + refresh + sign-off.

### S5 - If you want Hunting to *gain* something: add it, don't edit the cores  ·  **MEDIUM / BOLD**  ·  *only if you want new content*
Every tuned sibling gained 1-5 **new** skills at fresh slots (the SVAERA grafts + legacy restores);
Hunting gained nothing. There is also **no dropped legacy Hunting skill to restore** - I diffed SV 0.41
vs 0.98i and 0.98i is a superset (unlike Occult, which had Darklings to bring back). So if you want
Hunting to grow, it has to be **net-new content appended at a new tree slot** (slot 26+), never an edit
to the 25 frozen skills. That is the character-safe, freeze-safe, amgoz1-authentic path.
**The gap it should fill (see Weak Spots below):** a spear (melee) Hunter has **no self elemental
resistance** and a bleed-heavy damage profile that thins out against Act 3+ casters and
bleed-resistant late enemies. A new *defensive/utility* skill is the on-identity answer.
**Concrete shape (a starting point, not a spec):** a toggled hunter's-camouflage aura - modest flat
elemental resistance + reduced enemy detection *while you hold still / between attacks*, **reserving a
slice of mana** as its cost. That is an amgoz1 "system verb with a downside" (voice doc V7/V15), not a
stat stick, and it patches the exact survivability hole without buffing Hunting's already-benchmark
offense.
**Expected feel:** spear Hunters get a real defensive tool for the back half of the game; bow Hunters
(who already kite) get a smaller benefit. Hunting's offense is untouched.
**Risk:** BOLD - new content means new tags/FX/icon, a golden re-baseline for the *added* slot only, a
panel-button re-registration (`fix_mastery_panel_buttons`), and full QA. More work and more surface than
S1-S3.
**amgoz1 check:** PASS *if executed as a system verb with a cost* (V7 - his Occult skills are systems,
not bumps; V15 - power is paid for). FAIL if it becomes a free all-upside resist stick (neg-#3/#12).
**Golden handling:** additive slot -> regenerate the golden snapshot for the new slot in the same
change (do not add the slot without regenerating, or the gate false-positives).

### S6 - Direct self-resist on a core skill  ·  **BOLD**  ·  *flagged, NOT recommended*
The lazy way to close the survivability gap would be to bolt flat elemental resistance onto Wood Lore or
Herbalism, or to widen Study Prey's 3.0 radius / 5s duration. **I do not recommend this.** It edits
loved, frozen cores; it changes the glass-cannon risk profile you may like; and it is a stat bump, not a
system (fails the amgoz1 bar). If Act 3+ survivability ever genuinely bothers you on a spear build,
prefer S5 (additive) over touching a core. Listed only for completeness.

---

## 2. The tree as it stands (per-skill, with a candid grade)

25 slots, all verbatim SV 0.98i. Grades are mine: **auto-pick** (nearly every build wants it) /
**solid** (strong, build-defining for its lane) / **situational** (good in the right build/act) /
**dead** (skip). **There are no dead skills** - SV's Hunting is a tight tree. "Lane" = BOW / SPEAR /
BOTH, because Hunting is famously a two-weapon tree and most skills commit to one.

| # | Skill | Type / lane | Key numbers (max / ult) | Castable? | Grade |
|---|-------|-------------|--------------------------|-----------|-------|
| M | **Hunting Mastery** | Mastery | Life 1300, Dex 100, Str 70, RunSpeed +28%, **Mana 0**; +AtkSpeed/+PierceRatio tails at ML41+ | n/a | auto-pick |
| 1 | **Wood Lore** | Passive / BOTH | +Atk Speed 5->33%, +DA 13.5->45 (Bows/Spears) | n/a | solid |
| 2 | **Marksmanship** | LMB bow / BOW | +flat pierce 2->40, +pierce ratio 15->60%, mana 2 | yes | auto-pick (bow) |
| 3 | - Puncture Shot Arrows | Modifier / BOW | +pierce mod 18->45%, projectile pass-through 14->38% | - | solid (bow) |
| 4 | - Scatter Shot Arrows | Projectile mod / BOW | fires 3->9 arrows, +flat pierce, +bleed 9->54/3s | - | solid (bow AoE) |
| 5 | **Take Down** | Spear charge / SPEAR | +phys mod 26->75%, **+6->45% current-life execute**, +200% dash, fear; cd 8 | yes (TakeDown) | auto-pick (spear) |
| 6 | **Eviscerate** (`drxtakedown_eviscerate`) | Weapon attack / SPEAR | 3 targets/200deg, +phys 7->70%, +pierce 7->80, bleed 8->128/4s; cd 6 | yes (Tempest) | solid |
| 7 | **Tempest** (`drxspear_tempest`, *shown as "Eviscerate"*) | Weapon AoE / SPEAR | 12 targets/300deg, fear+confusion+slow, **-66% dmg** (CC, not a nuke); cd 10 | yes (BladeBlaze) | situational -> solid w/ Flayer |
| 8 | - Flayer (`drxtempest_expose`) | Modifier / SPEAR | +pierce mod 38->126%, +bleed mod 59->158%, +targets 1->3 | - | solid (makes Tempest hit) |
| 9 | **Volley** | WP attack / BOTH | rapid triple-strike (weapon dmg x3), chance-weight 7->36 | yes (TripleHit) | solid |
| 10 | **Gouge** | WP attack / BOTH | +pierce ratio 14->50%, bleed 16->125/3s, chance-weight 6->20 | yes (Puncture) | solid |
| 11 | **Study Prey** | Attack debuff aura | **-21->-66% enemy pierce & bleeding resist**, 3.0 radius, 5s; cd 8 | yes | auto-pick |
| 12 | - Flush Out | Modifier | **-14->-54% enemy elemental & trap resist**, +radius, +duration | - | solid |
| 13 | **Art of the Hunt** | Toggled aura, r15 | +pierce mod 12->115%, +bleed mod 15->60%, **racial vs Beast/Beastman 5->35%**; reserves **75% mana** | toggle | auto-pick |
| 14 | - Find Cover | Modifier | +projectile deflect 8->35%, +10% reserve | - | situational |
| 15 | - Trail Blazing | Modifier | +run speed 5->33%, +anti-slow 50->100%, +trap res; +50% reserve | - | solid |
| 16 | **Call of the Hunt** | Party buff, r15, temp | +Atk Speed 15->40%, small bleed, fear res; cd 180, dur 28->94s | yes | solid |
| 17 | - Exploit Weakness | Modifier | **+pierce mod 58->185%**, +bleed mod, racial +33% | - | auto-pick (huge dmg add) |
| 18 | **Lay Trap** (`drxmonsterlure`) | Turret pets | bolt traps, **petLimit 3->5, TTL 30s, cd 20** (-> ~0 w/ Rapid Construction); traps: pierce 8->122 + bleed | yes | auto-pick / solid |
| 19 | - Rapid Construction | Modifier | trap cd -3.6->-19.8s (near-instant), +mana cost reduction *(carries the S1 artifact)* | - | solid |
| 20 | - Improved Firing Mechanism | Pet modifier | +bolts/round 3->8, +pierce/bleed, +trap life | - | solid |
| 21 | **Ensnare** | Net projectile / CC | root/immobilize 2.5->10s, +flat pierce 15->75; cd 3 | yes | solid |
| 22 | - Barbed Netting | Modifier | **-28->-50% enemy OA & DA**, +bleed on the ensnared | - | solid |
| 23 | **Herbalism** | Passive | +life regen 3->8.4, +poison res 28->100%, +poison duration | n/a | situational |
| 24 | **Cornered** (`drxcorneredrage`) | Passive-on-low-life | +Atk Speed 25->60%, +OA 45->100, +DA 30->66, fear/stun res - **but -mana regen & -cast speed**; cd 180 | auto (trigger) | solid |

*(Slot numbers above are reading order, not the tree's internal `skillNameN` index. All 25 resolve,
all icons/tags resolve, and every animation token the tree's castable skills name (TakeDown, Tempest,
BladeBlaze, TripleHit, Puncture, plus Ensnare/CallOfTheHunt on the buff children) is present in the PC
anim tables - the build's `validate_player_skill_anims` gate passes, so nothing cast-aborts.)*

**Reading the tree:** Hunting is a weapon (bow *or* spear) pierce/bleed tree with an unusually complete
kit: best-in-mod single-target **execute** (Take Down 45% current-life), stacked **bleed** DoT,
double-barrelled **resist shred** (Study Prey pierce/bleed + Flush Out elemental/trap), ~100%-uptime
**turret pets**, two **party steroids** with a monster-family racial bonus, hard **CC** (Ensnare root +
Tempest fear/confuse), and a low-life **panic** button. That completeness is why the audit uses it as a
balance yardstick.

---

## 3. Weak spots (evidence-based)

Ordered strongest-evidence first. Note how few of these are about *power* - Hunting's power is fine.

1. **Hidden charm-resist penalty on Rapid Construction (real defect).** `defensiveConvert ==
   skillCooldownTime` (both `[-3.6 .. -19.8]`). The exact copy-paste class the 07-09 audit gated and
   cleared on Nature (Accelerated Growth); Defense's Resilience still carries it, and Hunting kept it
   because it was frozen first. Costs up to -19.8% charm
   resistance for investing in a cooldown modifier. -> **S1.**
2. **Two nodes both named "Eviscerate," both with blank tooltips.** `drxspear_tempest` (the CC spin)
   and `drxtakedown_eviscerate` (the bleed cleave) share `tagSkillName090` and neither has a
   description. SV-inherited. -> **S2.**
3. **Two skill descriptions describe the wrong skill.** Scatter Shot Arrows' tooltip is about a
   "Quillvine grove" energy aura; Gouge's is about "Quillvines firing barbs." SV authoring errors. ->
   **S3.**
4. **The mastery grants zero mana - the only 0-mana mastery left in the mod.** Real numeric lag vs the
   sibling bar (Occult 400, Storm 880, Earth 480). But it is deliberate amgoz1 design: vanilla had both
   DEX trees at 0, he funded only Occult (with INT), and traded Hunting +100 HP for it. -> **S4 (feel
   call).**
5. **No self elemental resistance; bleed-weighted damage.** The player's own mitigation is Life 1300 +
   DA (Wood Lore/Cornered) + projectile deflect (Find Cover) + poison res (Herbalism) - **no flat
   physical or elemental resist for self.** A **spear** (melee) Hunter therefore gets fragile against
   Act 3 Orient / Act 4 Hades casters, exactly where elemental damage spikes. And Hunting's DoT leans
   on **bleed**, which has coverage holes against some late-game constructs/undead - partly bought back
   by Study Prey's -66% bleed-resist shred, but only inside a 3.0-radius, 5s window. Bow builds sidestep
   most of this by kiting; spear builds eat it. This is the one genuine *design* gap, and it is arguably
   an intended glass-cannon trait. -> **S5 (additive) / S6 (flagged, not recommended).**
6. **No content growth since SV.** Every tuned sibling gained new skills; Hunting gained none, and there
   is no legacy-restore candidate (0.98i already supersets 0.41's Hunting folder). Not a power problem -
   just the reason any "give Hunting something" has to be net-new and additive. -> **S5.**

**How monsters actually threaten Hunting, by act (for context on #5):**
- **Act 1 Greece** - satyrs/boars/wolves/gorgons, mostly physical/pierce. Art of the Hunt's Beast/Beastman
  racial shines; trivial for Hunting.
- **Act 2 Egypt** - undead + insectoids + some casters. Herbalism's poison res helps; bleed still lands.
  Comfortable.
- **Act 3 Orient** - machae, demons, lightning/fire casters. Elemental threat rises and Hunting has no
  self elem-res; Study Prey/Flush Out keep offense strong, but a melee spear Hunter starts feeling
  squishy.
- **Act 4 Hades** - dense casters + high physical/elemental + undead legions. The worst case for a
  0-elem-res spear Hunter; the CC kit (Ensnare/Tempest) and Lay Trap turrets are your defense-by-control.
  Bow Hunting kites and is fine.
- **Act 5+ / Atlantis / higher difficulties** - the same pressure amplified; the survivability gap and
  bleed-coverage risk are most visible here.

---

## 4. Do-NOT-touch list (the loved / load-bearing cores)

These carry Hunting's identity and its benchmark strengths. Leave them exactly as amgoz1 shipped them
unless you have a specific reason and a QA plan.

- **Lay Trap + the bolt-trap pets + Rapid Construction's cooldown/Improved Firing Mechanism** - the
  ~100% pet uptime here is the *benchmark* the whole mod's pet-uptime tuning was measured against. (S1
  only removes the stray `defensiveConvert` penalty; it does **not** touch the cooldown or trap power.)
- **Take Down** - its 6->45% current-life execute is the best execute in the mod. Do not scale it.
- **Study Prey + Flush Out** - the -66% pierce/bleed + -54% elemental/trap shred is Hunting's answer to
  its own damage-coverage holes; it is load-bearing. Widening its radius/duration is tempting but is a
  core edit (that is S6, which I do not recommend).
- **Art of the Hunt (+ racial) and Call of the Hunt (+ Exploit Weakness)** - the party steroids and the
  Beast/Beastman racial are core to how Hunting plays and buffs a group.
- **Ensnare + Barbed Netting, and Tempest's fear/confuse** - the CC kit is the survivability answer for
  melee builds; keep the control values.
- **Cornered** - the low-life OA/Atk-Speed burst that pays for itself with -mana regen and -cast speed
  is textbook amgoz1 "power with a cost." Keep the downside; it is the point.
- **Marksmanship + Scatter/Puncture Shot** - the entire bow core.
- **Mastery HP (1300 @ ML40)** - it is deliberately +100 over Occult to pay for Hunting's 0 mana. If you
  ever add mana (S4), do **not** also cut the HP; the trade is the design.
- **Castability** - all Hunting anims pass the gate. Do not "clean up" any `skillSpecialAnimationName`.

**Out of scope for this document (Occult, not Hunting):** you rate **Smoke Screen** and **Breach**
highly and found **Flash Powder** trash - all three are **Occult (slot 5)** skills
(`records\skills\stealth\drxsmokescreenbuff.dbr`, `drxlaytrap.dbr` = Breach, `drxflashpowder.dbr`), owned
by the Occult analysis, not this one. Flagging them here only so they are explicitly on the protected
list and nobody touches them thinking they are Hunting. (Note the naming trap: Occult's "Breach" is
`drxlaytrap`, a *different* record from Hunting's "Lay Trap" `drxmonsterlure` - do not confuse the two.)

---

## 5. Summary table

| # | Suggestion | Size | Recommend? | Touches a frozen core? |
|---|------------|------|-----------|------------------------|
| S1 | Strip `defensiveConvert` artifact on Rapid Construction | SMALL | **Yes** | Yes (field edit; artifact removal) |
| S2 | Rename `drxspear_tempest` to "Tempest" + add both tooltips | SMALL | **Yes** | Yes (display/text only) |
| S3 | Rewrite garbled Scatter Shot + Gouge descriptions | SMALL | **Yes** | Text only |
| S4 | Modest mana pool on the mastery (0 -> ~160-200) | MEDIUM | Feel call - your decision | Yes (mastery field) |
| S5 | Additive new slot: hunter's-camouflage / self-resist utility | MEDIUM/BOLD | Only if you want new content | No (new slot; cores untouched) |
| S6 | Bolt self-resist onto a core skill | BOLD | **No** - use S5 instead | Yes (not recommended) |

**My recommendation:** do **S1-S3** (safe cleanups that make Hunting more correct without changing how
it plays), treat **S4** as a pure feel decision you make from your own character, and pursue **S5** only
if you actively want Hunting to gain a new toy. Skip **S6**. Every S1-S4/S6 item that touches a real
Hunting record must go through the `owner_approved_overrides` waiver + your explicit sign-off, exactly
like the Flash Powder rework - the freeze stays honest.

---

### Evidence appendix
- Built arz analyzed: `.claude/worktrees/build36-content/local/build36c/Database/SoulvizierClassic.arz`
  (build36 content wave, newest; superset of the fix wave). Cross-checked vs
  `upstream/soulvizier_098i/Database/database.arz` (SV bar), `upstream/soulvizier_041/...` (legacy
  check), and the base-game arz (vanilla mana check).
- Identity proof, roster, payloads, UI layout, and history probes:
  `scratchpad/ho_probes/probe_hunting.py` (+ `_hunting2/3/4`, `_vanilla_mana`, `_sv_history`), outputs
  `hunting_slots.json`, `hunting_full.json`, `hunting_identity_diffs.json`, `hunting_names_desc.txt`.
- Anim-castability: `tools/validate_player_skill_anims.py` on the built arz -> PASS (0 Hunting
  cast-aborts).
- Cross-refs: `docs/MASTERY_DEVIATIONS_LEDGER.md` (Slot 6), `docs/MASTERY_AUDIT.md` (Slot 6 = PASS,
  0 fixes), `docs/MASTERY_AUDIT_2026-07-09.md` (Hunting = secondary bar; the `defensiveConvert` gate is
  section 4-C), `scratchpad/specs/amgoz1_design_voice.md` (voice checks).
