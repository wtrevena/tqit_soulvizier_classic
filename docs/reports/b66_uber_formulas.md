# B66 - Uber Formula Expansion (round 2): 14 orphan weapons + non-weapon gap analysis

> Implements BACKLOG "QUEUED FEATURE: NEW-UBER-FORMULAS-FROM-ORPHANS" Part 1 (the 14
> curated weapons) and the Part 2 non-weapon survey/gap/wiring analysis Will asked for
> alongside it. Ground truth: build41 baseline `work/SoulvizierClassic/Database/
> SoulvizierClassic.arz` (md5 `eb8bc37775540f872003f873abf8e8be`), cross-checked against
> `upstream/soulvizier_098i|0.9|041/Database/database.arz` and the base game
> `database.arz`. Module: `tools/patches/uber_orphan_weapons.py` (registered in
> `tools/patches/__init__.py` REGISTRY, right before `visuals`). Donor data for the 3
> base-game-only orphans: `tools/patches/data/b66_orphan_donor_fields.json`.
>
> **Design-voice note:** the standing directive (2026-07-11, `feedback-amgoz1-creative-
> bar.md`) says to cite `amgoz1_design_voice.md` in every content brief. That file does
> **not exist anywhere in this repo** as of this wave (confirmed: `find . -iname
> "*amgoz1*"` and `*design_voice*` return nothing but an unrelated dye-skin `.dbr`). Names
> below follow the voice as documented secondhand in CLAUDE.md/BACKLOG.md ("monster/myth-
> identity-driven, flavorful, never generic filler") - **flagging this gap so a future
> wave creates the actual reference doc.**

## ROUND 2 CHANGELOG (independent adversarial vet of round 1, commit `d754359`)

Round 1's vet verdict was **NO-GO** on one HIGH (a false band-compliance claim), with one
MEDIUM and three LOW/nit findings. The implementation itself was called "functionally
excellent" - every fix below is a targeted correction, not a rework. Re-verified via the
same real dry-run replay harness against the same build41 baseline (still 21 new + 9
modified records, both gate-battery checks green, `verify()` green - see Verification).

1. **HIGH fixed - Ten Suns' Wrath was ~2.3x its bow sibling and the tier's single highest-
   damage weapon.** RETUNED (not left for a live design call, since this is a
   straightforward band-compliance fix with zero loss of identity): physical capped to
   145-160 (was 340-390) - now **exactly ties** its only bow sibling Stormbringer
   (`wep_bow.dbr`, 145-160) rather than exceeding it; flat pierce cut to a modest 40-60
   accent (was a tier-topping 220-300 FLAT); fire raised to 60-90 (+70%) to carry the
   "Ten Suns"/sun-god identity as the elemental-caster component - this is Phoenix's own
   already-vetted fire block verbatim, so it's a proven-safe number, not a new invention.
   Measured post-fix (all 27 supra weapons, sorted by physical max): Ten Suns' Wrath now
   sits at 160, tied with the bow/sword-class ceiling, nowhere near the tier's actual top
   (Last Word thrown 360, Omega/wep_club 315, Doom Herald 310). **The "none exceed the
   strongest sibling" claim below is now true, not aspirational.**
2. **MEDIUM fixed - donor combat stats weren't cleared before the retune, so orphan
   riders bled through uncontrolled.** `uber_orphan_weapons.py` now clears every
   `offensive*`/`retaliation*`/`characterDexterity`/`characterStrength`/
   `characterIntelligence`/`characterLife*`/`characterOffensiveAbility`/
   `characterAttackSpeedModifier` field on the built result BEFORE applying overrides
   (`_clear_inherited_combat_stats`, mirroring N5's `_add_supra_thrown_weapons` exactly),
   for all 14 weapons regardless of build path (clone or donor-JSON). This removes every
   round-1-flagged stray rider (Erysichthon's negative `characterLifeRegen`, Furies'/
   Scylla's stray `characterStrength`, Charybdis' stray `characterOffensiveAbility`, Doom
   Herald's stray Str/Dex/Int, Furies' undocumented total-speed slow) - verified gone by
   direct field probe post-fix. The 2 riders that legitimately depended on an inherited
   `offensiveGlobalChance` (Aquimae's dual life/mana-leach slows, Furies' bleed/poison
   slows) now set it explicitly (`100.0`, matching what was previously inherited by
   coincidence) instead of relying on the donor happening to carry it.
3. **LOW fixed - the donor JSON's "verbatim" claim was inaccurate for Di Jun's Pride.**
   `b66_orphan_donor_fields.json`'s `dijunspride` entry is now genuinely byte-verbatim
   against the real base-game `unique_houyi_bow.dbr` (restored `basicProjectileName` to
   the base `ArrowDefault01`, `offensivePhysicalModifier` to the base `55.0`, removed an
   extra `baseTexture` field the snapshot never should have carried). The intentional
   sun-projectile retheme is now an explicit, documented override in the module instead of
   a silent donor-snapshot drift.
4. **LOW fixed - Heartpierce/Ripulsar exceeded the documented supra sword ceiling.**
   Both trimmed to `offensivePhysicalMax=160` (was 175/165 respectively) - matches
   `wep_sword.dbr`'s own ceiling exactly.
5. **LOW/nit fixed - Munderizer/Sword Fish's `hidePrefixName`/`hideSuffixName` were 0/0**
   while the other 12 (and every existing supra weapon) use 1/1. Aligned to 1/1 - no
   design reason found for a fixed-name Legendary to show a rolled affix.
6. **`verify()` hardened** with 3 new round-2 regression guards: a physical-max band cap
   on the 3 retuned weapons, a non-zero `offensiveGlobalChance` check on Aquimae/Furies,
   and a `hidePrefixName`/`hideSuffixName`==1 check on all 14 - so any future edit that
   reintroduces one of these defects fails the build loud.

---

## Part 1 - the 14 weapons

### What "supra" means here (the proven template cloned)

The DRX "supra" tier: `records\drxitem\supra\*`, Legendary class, level-requirement 65,
crafted at the Enchanter from a Mythic/Arcane Formula + 3 reagents + 10,000,000 gold. SVC
already extended this exact way once (N5, build32): 3 thrown weapons
(`svc_wep_sanguineorbit/lastword/charonstoll`) cloned from base-game roh uniques, retuned,
and wired into `supra.dbr` + `supra_special.dbr`. This wave clones that same shape for the
14 backlog candidates.

### Where each orphan's record actually lives (verified fresh, not assumed)

The curation report's paths were re-resolved against **5 independent sources** (build41
baseline BUILT, base game database.arz, and all 3 upstream SV arzs) to determine whether
each orphan is reachable from a registry module's `db` at all:

| Candidate | Lives in | Consequence for this module |
|---|---|---|
| Ripulsar, Aquimae, Helona, Phoenix, Erysichthon's Hunger, Scylla, Charybdis, The Furies, Heartpierce, Doom Herald, The Munderizer | **BUILT** (present in `db` at registry time - SV/DRX-authored) | `db.clone_record(orphan, dest)` - every rendering field (bumpTexture/castsShadows/actorRadius/...) copied verbatim, zero risk of a missed field |
| Hati, Sword Fish, Di Jun's Pride | **BASE only** (base game database.arz; NOT in `db` - `base_db` is loaded+freed entirely inside `build_svc_database._run_prefix`, long before `run_registry` runs) | Full field set (628/624/631 fields) captured **read-only** from the live base arz, bundled as `tools/patches/data/b66_orphan_donor_fields.json`, reconstructed via `_ensure_record` + per-field `set_field` (same "copy every donor field, then override identity stats" shape N5 used with `base_db` directly) |

This is why the module needs the bundled JSON at all - it is the only way a registry
module (which structurally cannot touch `base_db`) can faithfully reproduce a base-game-
only donor's complete, render-safe field set.

### Formula shells: what "24 orphaned zrecipes" actually breaks down to

The `zrecipes\` folder holds 27 `ItemArtifactFormula` duplicates. Verified breakdown:
**13 already spoken for** (10 classic-weapon dups whose `recipes\` twin is the obtainable
original, + the 3 already-wired `svc_thrown_*`) + **14 non-weapon dups** (armor/jewelry/
artifact - see Part 2). Of the 10 classic-weapon shells, this wave's 14 candidates span 6
weapon classes needing **7 formula slots per class** in some cases and only 1 spare shell
existed - so **7 of 14 reuse a spare shell** (repointed in place) and **7 are freshly
authored** (cloned from a live `recipes\` formula of the same class, not from a shell):

| Class | Candidates needing a formula | Spare shells available | Reused (repointed) | Freshly authored |
|---|---|---|---|---|
| Sword | Ripulsar, Aquimae, Heartpierce (3) | `wep_sword`, `wep_dagger` (2) | Ripulsar->`wep_sword`, Aquimae->`wep_dagger` | Heartpierce->`svc_sword_heartpierce_formula` (cloned from live `recipes\wep_sword_formula`) |
| Axe | Phoenix, Erysichthon's Hunger, Scylla, Charybdis, The Furies (5) | `wep_axe` (1) | Phoenix->`wep_axe` | 4 fresh (`svc_axe_{erysichthon,scylla,charybdis,furies}_formula`, all cloned from live `recipes\wep_axe_formula`) |
| Mace | Sword Fish, Doom Herald (2) | `wep_club` (1) | Sword Fish->`wep_club` | Doom Herald->`svc_mace_doomherald_formula` (cloned from live `recipes\wep_club_formula`) |
| Staff | Helona, The Munderizer (2) | `staff_dream`, `staff_ele`, `staff_vit` (3, 1 spare left unused) | Helona->`staff_dream`, Munderizer->`staff_vit` | none |
| Thrown | Hati (1) | 0 (the only 3 thrown shells are the LIVE svc_thrown_* - not free) | none | Hati->`svc_thrown_hati_formula` (cloned from the live `zrecipes\svc_thrown_charonstoll_formula`, same SVC thrown convention) |
| Bow | Ten Suns' Wrath (1) | `wep_bow` (1) | Ten Suns' Wrath->`wep_bow` | none |

Repointing a shell **never touches its live `recipes\` twin** (a different record path;
e.g. `zrecipes\wep_axe_formula.dbr` is repointed for Phoenix while `recipes\wep_axe_
formula.dbr` keeps crafting Darkflame Devourer, untouched). All 14 are added to both
`supra.dbr` and `supra_special.dbr` at the next free `lootNameN` slot, weight 100 -
matching the 3 `svc_thrown_*` precedent exactly (verified in the dry-run: both tables now
carry every one of the 14 in addition to their pre-existing 27/28 members).

`artifactCreationCost` is normalized to **10,000,000** (`itemCost` 500,000) on all 14 -
matching the live `recipes\` tier and the already-shipped `svc_thrown_*` cost, **not** the
zrecipes shells' legacy 65,000,000 (that price was specific to the never-obtainable
orphaned duplicates and is not carried forward).

### The stat band (derived from the 13 existing supra ubers, per class)

Read directly off the shipped build41 arz (not estimated):

| Class | Reference supra(s) | Physical band (min-max, modifier%) | Signature extras |
|---|---|---|---|
| Sword | Shrike, Crystal Tear of Nyx | 110-160, 50-55% | pierce ratio 20-30, bleed/poison/disruption |
| Axe | Darkflame Devourer | 200-230, 45% | elemental 50-70 (+70% mod), leech 15, %curLife 10 |
| Mace | Omega | 292-315, 100% (10% chance) | cold 45, disruption 3-5, leech 20, big DA/OA debuffs |
| Staff | Scepter of Kronos, Soul Seekkor, Staff of Cosmos | base life/elemental 55-244 | mana regen, INT 45-120 |
| Bow | Stormbringer | 145-160, 50% | elemental 60 (+200% mod), pierce ratio 35 |
| Thrown | Sanguine Orbit, Last Word, Charon's Toll | 180-360, 20-30% | leech/bleed/stun/manaburn |
| Spear | Blood Whisper | 245-265, 25% | pierce mod 45/ratio 50, bleed 400 |
| Shield | Agathodaemon | 290, 50% | DA/OA 200 (+15% mod), life 350 |

All 14 candidates land inside their class's band (documented per-weapon in the module's
`overrides` dicts); none exceed the strongest existing sibling in that class. **(Round 2
correction: this claim was false for Ten Suns' Wrath and imprecise for Heartpierce/
Ripulsar in round 1 - all 3 were retuned/trimmed to make it true; see the ROUND 2
CHANGELOG above. Verified directly, not asserted: ranking all 27 supra weapons by
`offensivePhysicalMax` post-fix puts Ten Suns' Wrath at 160 - tied with the bow/sword
ceiling, nowhere near the tier's actual top of 360.)**

### Identity preserved (the "keep its identity skills/procs" mandate)

4 of the 14 carried a genuine granted skill/augment on the orphan - **all 4 kept, verbatim
path, level raised to supra weight**:

| Weapon | Kept mechanic |
|---|---|
| **Helona's Ascension** | `itemSkillName` = `helona_summon` (grants the summon - this is the entire point of the pick) |
| **Phoenix Ascendant** | `itemSkillName` = `heatshield` (the live granted skill the curation report called out) |
| **Ripulsar** | `augmentSkillName1` = Dream-mastery `drxpsionictouch`, level 2 -> 4 |
| **The Unholy Heartpiercer** (Heartpierce) | `augmentSkillName1` = `drxanatomy`, level 1 -> 3 |
| **Sword Fish** | `augmentSkillName1` = `concussiveblow`, level 1 -> 3 |
| **The Doomcaller's Maul** (Doom Herald) | `augmentSkillName1` = `drxconcussiveblow`, level 2 -> 4 |
| **Hati** | native bonus-vs-large-prey proc (`offensiveTotalDamageModifier` 200 @ 33% chance) kept unmodified |

`verify()` spot-checks the two `itemSkillName` cases fail-loud if either is lost.

### Reagents (2 Legendary + 1 Rare; 1 Legendary + 1 Epic + 1 Rare for the thrown pick)

Drawn from the SAME reagent pool the 13 existing formulas already use for that weapon
class - proven-resolving (they are LIVE reagents in shipped formulas today) and
thematically matched:

| Weapon | Reagent 1 (L) | Reagent 2 (L/Epic) | Reagent 3 (R) |
|---|---|---|---|
| Ripulsar | Mindrazor | Griefmaker | Sabertooth |
| Aquimae | Stymphalian Talon | Plissken | Deathweaver's Legtip |
| The Unholy Heartpiercer | Mindrazor | Stymphalian Talon | Sabertooth |
| Helona's Ascension | Praxidikae | Sakur-Aba | Scepter of the Liche King |
| The Munderizer | Rod of the Ancients | Riddle of the Sphinx | Staff of the Magi |
| Phoenix Ascendant | Pyrophoric Lop | Shai'tan | Head Hunter's Axe |
| Erysichthon's Undying Hunger | Pyrophoric Lop | Shai'tan | Head Hunter's Axe |
| Scylla Unbound | Pyrophoric Lop | Shai'tan | Head Hunter's Axe |
| Charybdis Unchained | Pyrophoric Lop | Shai'tan | Head Hunter's Axe |
| Wrath of the Furies | Pyrophoric Lop | Shai'tan | Head Hunter's Axe |
| Sword Fish | Sapros the Corrupter | Demeter's Sorrow | Animus |
| The Doomcaller's Maul | Sapros the Corrupter | Demeter's Sorrow | Animus |
| Hati | Touch of Nyx (L) | The Crow (Epic) | Demonic Rippers |
| Ten Suns' Wrath | Helios' Fury | Khamsin | Brigand's Bow |

**On the 5 axes sharing one reagent trio:** intentional, not an oversight - TQ's own
economy commonly reuses a class's most popular Legendary reagents across a themed
family (reduces reagent-hunting friction for a player collecting the whole set), and it is
literally the only proven-resolving 2L+1R axe trio available without inventing a new
reagent choice. Documented here for Will's veto if he'd rather diversify (would need
picking additional Legendary/Rare axes and independently re-verifying their
classification/resolution - deferred to keep this round's risk surface small).

**Ten Suns' Wrath's `dropSoundWater` fix:** Di Jun's Pride's own base-game record carries
a dead `dropSoundWater` ref (`Records\Sounds\SoundPak\ItemsWaterMdDropPak.dbr` - resolves
nowhere in BUILT or BASE, a pre-existing vanilla data slip on an item nothing has ever
dropped). Not propagated: repointed to the resolving
`records\sounds\soundpak\items\watersmdroppak.dbr` instead - same category as the 2
already-documented supra dead-ref fixes (`_SUPRA_DEAD_REF_FIXES` in apply_svc_patches.py),
cosmetically inert either way, fixed here since the correct value was already at hand.

**Round 2 correction - the donor JSON is now genuinely verbatim.** Round 1's
`b66_orphan_donor_fields.json` `dijunspride` entry silently differed from the real base
`unique_houyi_bow.dbr` on 3 fields while the module/report described the snapshot as
"verbatim": `basicProjectileName` had already been rethemed to the sun-projectile,
`offensivePhysicalModifier` had been zeroed (55.0 -> 0.0), and an extra empty-ish
`baseTexture` field was present that the base record doesn't carry. The JSON is now fixed
to hold the true base values (verified against a fresh read of the base game
`database.arz`), and the sun-projectile retheme is applied as an explicit, documented
`overrides['basicProjectileName']` in the module instead - same visible in-game result,
now honestly attributed.

---

## WILL VETO - every naming call (ship-as-default; flag to change)

Per the backlog's "twin caveat": 9 of the 14 orphans have a live droppable item sharing
their exact display name somewhere in the base game today. The orphan RECORD is still
safely unreferenced (nothing points to it), but the backlog calls for a rename or
"ascended" framing on the twin-affected picks. **NO new art** was authored for any of
these (efficiency law) - naming is the only creative surface touched.

| # | Weapon (shipped name) | Twins | Orphan's original name | Naming call |
|--:|---|:--:|---|---|
| 1 | Ripulsar | 0 | Ripulsar | **unchanged** - fully free identity |
| 2 | Aquimae | 0 | Aquimae | **unchanged** - fully free identity |
| 3 | Helona's Ascension | 1 | Helona | **renamed** ("Ascension" nods to the summon it grants) |
| 4 | Hati | 0 | Hati | **unchanged** - fully free identity |
| 5 | Sword Fish | 0 | Sword Fish | **unchanged** - the joke stands, deliberately |
| 6 | Phoenix Ascendant | 1 | Phoenix | **renamed** ("Ascendant" = minimal delta, keeps recognizability) |
| 7 | Erysichthon's Undying Hunger | 1 | Erysichthon's Hunger | **renamed** (escalates the curse to eternal/mythic scale) |
| 8 | Scylla Unbound | 1 | Scylla | **renamed** (paired framing with Charybdis Unchained) |
| 9 | Charybdis Unchained | 1 | Charybdis | **renamed** (paired framing with Scylla Unbound) |
| 10 | Wrath of the Furies | 1 | The Furies | **renamed** (name -> title, avoids exact collision) |
| 11 | The Unholy Heartpiercer | 1 | Heartpierce (`zzz_unholykatana`) | **renamed** |
| 12 | The Doomcaller's Maul | 1 | Doom Herald (`zzz_bamfhammer`) | **renamed** |
| 13 | The Munderizer | 0 | The Munderizer | **unchanged** - the insider joke stays exact |
| 14 | Ten Suns' Wrath | **2** | Di Jun's Pride | **fully renamed** (heaviest twin conflict; ties to the Houyi/ten-suns myth the bow mesh (`houyibow`) already depicts, without reusing either live twin's name) |

**Also flagging:** the curation report described The Munderizer as having "its own magenta
`^f` name". No such tag was ever found (checked the shipped Text.arc, the base game
Text_EN.arc, AND upstream sv098i's own Text_EN.arc - `tagEggMunderizer` resolves to
**nothing anywhere**; it would have shown as a raw tag key in-game had it ever been
reachable). No manual color prefix was applied here - `{^F}` is reserved for soul tags per
the standing color-discipline law, and none of the 13 existing supra weapons use a manual
color prefix (rarity-based coloring is automatic). If Will specifically wants Munderizer's
tag styled magenta to honor that description, it's a one-line change
(`tags['tagSVCwpnMunderizer'] = '{^F}The Munderizer'`) - left as default-off pending his
call.

---

## Part 2 - non-weapon uber-tier survey

### (a) What already exists (swept `records\drxitem\supra\*` + every `ItemArtifactFormula`
by result-class in the build41 baseline)

**Surprise finding: the non-weapon supra tier is not a gap - it already exists in full,
and it is ALREADY WIRED and obtainable.** All 25 `recipes\` formulas (10 weapon + **15
non-weapon**) are listed as `lootNameN` in supra.dbr; supra_special.dbr carries the same 25
plus `artifact_mortoksskull` (28 total incl. the 3 svc_thrown). Verified directly off the
tables' own `lootNameN` fields, not inferred:

| Slot (TQ's own item-class taxonomy) | Existing supra piece(s) | Wired? |
|---|---|:--:|
| ArmorJewelry_Amulet | neck_caster, neck_melee | YES (both tables) |
| ArmorJewelry_Ring | ring_caster, ring_melee | YES (both tables) |
| ArmorProtective_Forearm | ar_caster_arms, ar_melee_arms | YES (both tables) |
| ArmorProtective_Head | ar_caster_helm, **ar_hunter_helm**, ar_melee_helm | YES (both tables) |
| ArmorProtective_LowerBody | ar_caster_legs, ar_melee_legs | YES (both tables) |
| ArmorProtective_UpperBody | ar_caster_torso, ar_melee_torso | YES (both tables) |
| WeaponArmor_Shield | wep_shield (Agathodaemon) | YES (both tables) |
| ItemArtifact (its own dedicated slot) | artifact_plus2 (both tables), artifact_mortoksskull (supra_special only) | YES |

16 non-weapon pieces total, all fully-built real items (not stubs - each carries a
complete stat block, mesh, bitmap; several have their own skill/FX rig, e.g.
`hunter_helm_galefury` a togglable buff, `caster_helm_warpshield` a buff-radius proc,
`artifact_plus2` an attack-radius skill). **This was previously undocumented** - worth
surfacing to Will on its own: the "uber craft tier" he asked about already covers 7 of 8
non-weapon equip slots end to end.

### (b) The one genuine gap: `ArmorJewelry_Bracelet`

TQ's complete non-weapon equip-slot taxonomy (swept from the base game's own `Class`
values) is exactly 8: Amulet, Ring, **Bracelet**, Forearm, Head, LowerBody, UpperBody,
Shield. Bracelet is the only one with **zero** supra presence anywhere in
`drxitem\supra\*`.

**Why no orphan exists to curate:** every `ArmorJewelry_Bracelet`-class record in the
effective game (BUILT + BASE, exhaustively enumerated) is a generic `default\braceletXX.
dbr` procedural-affix base shell - empty `itemNameTag`, empty `itemClassification`, no
lore, no distinctive mesh (36 near-identical `braceletX##.dbr` entries + `braceletgold` +
`crocmanbracelet`). **Titan Quest (base game + every xpack) has no named/unique bracelet
at all** - bracelets are always assembled at runtime from magical-affix pools onto a
generic base, unlike rings/amulets/shields which do get discrete named uniques. This
matches the orphan audit's own JUNK classification criterion exactly ("no resolvable
display name AND zero base damage/identity").

### (c) Wiring decision: SKIP this round (per the efficiency law)

Closing the Bracelet gap has no reuse-an-orphan path - it would require authoring an
entirely new bespoke item (mesh/icon choice + a from-scratch name/lore/stat identity),
which is new-art-adjacent creative authoring, not the "buff an orphan" pattern this wave
is scoped to. Per Will's efficiency law ("skip anything requiring heavy work... cap at
what is genuinely low-effort"), **no non-weapon winner is wired this round.**

**Worth adding later (for Will):** if he wants a supra Bracelet, the cheapest viable path
is reskinning an EXISTING supra jewelry piece's stat shape (e.g. a caster/melee split
mirroring the Ring/Amulet pattern already established) onto a generic bracelet mesh
(`default\braceletgold.dbr` is the cleanest-looking of the 36 shells) with a freshly
authored name/identity - still fresh creative content, just minimal art risk (reuses an
existing mesh). Flagged, not built, this round.

---

## Verification

**Round 2 re-verification** (same real harness, same build41 baseline arz, re-run after
every fix above):

- **Fast gates:** `py -m py_compile tools/patches/uber_orphan_weapons.py tools/patches/
  __init__.py` - PASS. `py tools/patches/_check_registry.py` - PASS (21 modules, order
  hash `479c97788384d28b5c16d0f391ed8914b72c6e14bfca3230b0d0e88c53d19ef8` - unchanged from
  round 1, since no module was added/removed/reordered).
- **Dry-run replay** (fresh load of build41 baseline arz, md5 confirmed
  `eb8bc37775540f872003f873abf8e8be`, `patches.run_registry(db, tags,
  registry=['uber_orphan_weapons'])` - the REAL harness, not a hand-rolled call):
  **still exactly 21 new records + 9 existing records modified** (the 7 repointed shells +
  `supra.dbr` + `supra_special.dbr`) - **intended-only**, zero incidental diffs, unchanged
  shape from round 1 (round 2 only changed field VALUES on existing spec entries, not the
  record/formula roster). 28 tags added. S4a/S4b collision gates: clean (0 collisions).
- **verify() hook** (run via `run_registry_verifies`, the real post-finalization harness):
  all 14 results + 14 formulas resolve; every formula's `artifactName`/3 reagents are
  non-empty and correct; every formula is listed in BOTH `supra.dbr` and `supra_special.
  dbr`; every tag referenced is present in `tags`; both `itemSkillName`-preservation
  spot-checks (Helona, Phoenix) pass; **3 new round-2 guards** also pass: (a) physical-max
  band cap on Ten Suns' Wrath/Heartpierce/Ripulsar (all <=160), (b) non-zero
  `offensiveGlobalChance` on Aquimae/Furies post-clear, (c) `hidePrefixName`==
  `hideSuffixName`==1 on all 14. PASS.
- **Direct field probe** (post-`apply()`, read back off the in-memory db - not asserted,
  measured): Ten Suns' Wrath = phys 145-160/+30%, pierce 40-60/ratio20, fire 60-90/+70%,
  `basicProjectileName`=the themed sun projectile (explicit override, not donor drift);
  Heartpierce/Ripulsar phys max = 160/160; Aquimae/Furies `offensiveGlobalChance`=100
  explicit; Erysichthon `characterLifeRegen`/Furies `characterStrength`+total-speed-slow/
  Scylla `characterStrength`/Charybdis `characterOffensiveAbility`/Doom Herald Str-Dex-Int
  all now `None` (cleared, no longer bleeding through) while every weapon's INTENDED
  `characterLife`/`characterDefensiveAbility`/`characterMana`/`characterOffensiveAbility`
  stat (the ones actually in `overrides`) is unaffected; Munderizer/Sword Fish
  `hidePrefixName`/`hideSuffixName`=1/1; Helona/Phoenix `itemSkillName` and Hati's
  bonus-vs-large-prey proc all still intact.
- **Tier-rank sanity check** (all 27 supra weapons, sorted by `offensivePhysicalMax`,
  measured post-fix): Last Word 360, Omega 315, Doom Herald 310, Sword Fish 300, Blood
  Whisper 265, Hati 260, Darkflame Devourer/Phoenix/Furies/Erysichthon 230, Scylla/
  Charybdis 225, Sanguine Orbit 215, Charon's Toll 210, **wep_sword/wep_bow/Ten Suns'
  Wrath/Ripulsar/Heartpierce/Aquimae all tied at 160**, wep_dagger 122. Ten Suns' Wrath is
  no longer the tier's outlier - it sits at the bow/sword floor, tied with its own sibling.
- **Resolves-in-arc** (the lesson from prior waves - resolution must be checked against
  BUILT-arz **union** BASE-arz, matching how the TQ engine actually overlays a mod over
  the stock database, not BUILT alone): every `mesh`/`bitmap`/`baseTexture`/`bumpTexture`/
  `weaponTrail`/`basicProjectileName`/`itemSkillName`/`augmentSkillName`/`itemCostName`/
  `artifactName`/3×`reagentBaseName`/`artifactBonusTableName`/`artifactFormulaBitmapName`/
  `dropSound*` reference from all 14 results + 14 formulas resolves. PASS (the initial
  BUILT-only pass over-flagged 8 refs that are legitimate base-game asset paths, resolved
  once BASE was unioned in - documented above, not a bug).
- **Supra dead-reference invariant** (`apply_svc_patches._verify_no_supra_dead_refs`, run
  directly against the post-apply db): 0 offenders. GREEN.
- **Container loot-shape gate** (`build_svc_database._validate_container_loot_shapes`, run
  directly against the post-apply db): PASS.
- **Negative test:** deleting the clone-source donor for Ripulsar and re-running `apply()`
  raises `SystemExit` with a clear message (fail-loud, not a silent skip). PASS (re-run
  round 2, unaffected by the clear-step change since the SystemExit fires before any
  clear/override runs).
- **Text-tag manifest:** every `itemNameTag` and formula `description` tag the 14
  records/formulas reference is present in the `tags` dict the module returns (checked in
  `verify()`); a full `validate_tags.py` pass needs a real `Text.arc` build (heavy - out of
  scope this round per "NO heavy builds"), so this is the equivalent narrower invariant
  checked directly against the in-memory tag manifest.
- **NOT run this round** (heavy, per the brief): a full `build_svc_database.py` DB build,
  `build_text_arc.py` Text.arc build, or any map build. All verification above is
  dry-run/in-memory against the real build41 baseline arz and the real registry harness.

## Files touched

- `tools/patches/uber_orphan_weapons.py` (new registry module)
- `tools/patches/data/b66_orphan_donor_fields.json` (new - 3 base-game donor field
  snapshots, 628/624/631 fields each, captured read-only from the live base
  `database.arz`)
- `tools/patches/__init__.py` (REGISTRY: appended `uber_orphan_weapons` before `visuals`)
- `docs/reports/b66_uber_formulas.md` (this report)
- `docs/BACKLOG.md` (status update on the NEW-UBER-FORMULAS-FROM-ORPHANS entry)

## Handoff to round 3

Not built this round (out of scope / awaiting Will):
- The 8-axe Greek bench (Acheron's Touch, Axe of Tereus, Persephone's Caress, Torment,
  Shai'tan-the-orphan-bench-copy, Atropos' Assistant, Enkidu's Stand, Theogenes'
  Onslaught) - Will hasn't picked whether he wants a themed "Wrath of the Underworld"
  all-axe formula set from these.
- A fresh Spear or Shield uber authored from scratch (the report's "honest gaps" - no
  quality orphan exists for either; Blood Whisper already fills supra Spear).
- The supra Bracelet (Part 2c) - flagged, not built, per the efficiency law.
- Diversifying the 5-way shared axe reagent trio, if Will wants more variety than the
  proven-resolving reuse this round took.
