# b91 - DEBT CLEARANCE LANE: domain `db` (5 deferred backlog items)

**Branch** `fix/debt-db` (worktree `.claude/worktrees/debt-db`, base `main` @ `89d3e52` = post-b90/build49)
**Date** 2026-07-28
**Scope** DB only (`.arz` + `Text.arc`). NO map rebuild, NO deploy, NO Steam. `Levels.arc` /
`Quests.arc` untouched and hash-proven.

Five items were handed to this lane off the triage of Will's deferred backlog. **Three needed real
new code; two turned out to be ALREADY FIXED in the shipped arz and were closed with proof plus the
permanent gate they never had.** That distinction is called out per item rather than papered over.

| # | Item | Verdict |
|---|---|---|
| 1 | `B-FX-DANGLING-1` (~353 dangling Chris particle refs) | **FIXED** - new registry module, 353 slots stripped, base-parity proven |
| 2 | `BLOODHOUND-DYINGFX` (6 dangling `dyingFxPak`) | **ALREADY RESOLVED in the arz** - closed with proof + a new fail-loud invariant so it cannot return |
| 3 | `SOUL-EMBERTEETH-SUMMON` | **BUILT** - new registry module (3 pets + summon button + 3 soul tiers) |
| 4 | `LEGION-TERMINAL-50` (R-42 fold-in) | **FIXED UPSTREAM** in the shared soul-rate classifier; exactly 2 records move |
| 5 | `BL-ENSLAVER-SPAWNS` | **ALL 3 SUB-FIXES ALREADY SHIPPED** (1 by b49, 2 by ruling R-18, 3 by `_create_enslaver`) - verified, gated, closed; one honest open question left for Will |

---

## 1. B-FX-DANGLING-1 - 353 dangling `Chris\UnarmedProjectile_FX01` particle refs

### Ground truth (decoded against the UNION of the built arz + the stock TQAE `database.arz`)

* `Records\SandBox\Chris\UnarmedProjectile_FX01.dbr` exists **nowhere**: 0 hits across 92,311 union
  record names. The `records\sandbox\` namespace itself ships **536 other records**, so this is a
  genuinely missing sibling, not a missing namespace.
* **177 records** reference it, from `particleEffectName2` (177 slots) + `particleEffectName3`
  (176 slots) = **353 dangling slots** - exactly the "~353" the BACKLOG entry counts.
* Affected namespaces: `records\skills\monster skills` 62, `records\skills\skills` 48,
  `records\xpack\skills` 26, `records\skills\boss skills` 16, `records\skills\soulskills` 6,
  **`records\skills\earth` 6 (the player Earth mastery: `drxflamesurge` + `drxvolcanicorb`, live +
  scroll + backup copies)**, plus DRX creature/test records.

### Why STRIP, and why the attach points STAY

Of the 177 records, **69 also exist in the stock game DB**. In those 69:

| field | absent in base | carries the same dangling ref | carries something else |
|---|---|---|---|
| `particleEffectName2` | **69 / 69** | 0 | 0 |
| `particleEffectName3` | **68 / 68** | 0 | 0 |
| `particleEffectAttachPoint2` | 0 | - | **69 / 69 present** |
| `particleEffectAttachPoint3` | 0 | - | **68 / 68 present** |

So vanilla's shape for these exact records is *name slot absent, attach point present*. Deleting the
**name** field restores byte-shape parity with the game's own records; deleting the **attach point**
would DEVIATE from it. (731 orphaned attach-point slots exist across the arz, inherited straight from
the base game - an attach point with no name slot is simply what TQ ships.)

That also matches the house precedent: build30's F7a stripped `particleEffectName2/3` and nothing
else. **The BACKLOG's "strip the orphaned `particleEffectAttachPoint2/3`" sub-item is therefore closed
as REJECTED-BY-EVIDENCE, not silently dropped.**

A repoint was rejected too: it would invent an FX layer vanilla does not have, and an empty-string
ref is the B-TOXEUS-2 zero-precedent loader-abort class.

### F7a is superseded (BL-103 fix-upstream)

Round 1 of this lane asserted that the 3 `pcsafe` records F7a already fixed should NOT still carry the
ref, and **the build failed on that assert** - which turned out to be the useful finding: those 3
records are B-SOUL-PROC-2 `pcsafe` *clones*, and the clone step re-mints them from their
still-dangling PLAIN sources **after** F7a runs. F7a was a symptom patch the pipeline immediately
undid. The new sweep runs last, over the FINAL assembled db, and fixes the class at the source. F7a is
left in place as a documented harmless no-op and the re-mint count is printed every build.

### Implementation

New registry module **`tools/patches/fx_dangling_cleanup.py`**, registered second-to-last (immediately
before the write-nothing `visuals`) so it sweeps the final db and no later module can reintroduce the
class. `apply()` snapshots every record's emitted field-key set before and after its own writes and
`SystemExit`s unless the changed set is exactly the intended one.

Also finishes build30 **F3**: that fix repointed supra `wep_spear.dbr` to the base `RSpear14B.msh` and
stripped its DRX `baseTexture`, but left the sibling
`bumpTexture = DRXtextures\items\supra\skins\wep_spearbmp.tex` - the same DRX skin set on a mesh that
carries its own internal textures. Stripped here by the same mechanism.

---

## 2. BLOODHOUND-DYINGFX - ALREADY RESOLVED; now gated

Filed in the P0 crash block as "a real defect, NOT this crash", then orphaned. **Ground truth on the
current arz: there is nothing left to fix.**

All 6 summoned-bloodhound bodies already carry the exact repoint target the BACKLOG line names:

```
records\drxcreatures\bloodhound\b_bloodhound_33.dbr   dyingFxPak = ...\effects\fxpak_deathfx_burst.dbr
records\drxcreatures\bloodhound\b_bloodhound_34.dbr   (same)
records\drxcreatures\bloodhound\b_bloodhound_35.dbr   (same)
records\drxcreatures\bloodhound\c_bloodhound_40.dbr   (same)
records\drxcreatures\bloodhound\c_bloodhound_42.dbr   (same)
records\drxcreatures\bloodhound\c_bloodhound_44.dbr   (same)
```

and `records\drxcreatures\bloodhound\effects\fxpak_deathfx_burst.dbr` resolves. A roster-wide sweep
finds **0 dangling `dyingFxPak` refs anywhere in the arz**.

> Trap worth recording: a mod-arz-ONLY scan reports 7 false positives here (4
> `boss_daemonbull_yaoguai_*` + 3 `crowheroes\zilla*`). All 7 resolve in the base-game DB. **Any
> dangling-ref audit of this mod MUST resolve against the UNION of the mod arz and
> `<TQAE>\Database\database.arz`**, or it will chase ghosts.

Since a one-shot cleanup has nothing to clean, the lane ships the thing the debt actually lacked: a
**permanent invariant**. `fx_dangling_cleanup.verify()` fails the build loud if any record's
`dyingFxPak` stops resolving against that union, and separately re-asserts that exactly 6 bloodhound
bodies still point at the burst pak. Where the base DB is unavailable (scratch/determinism layouts) it
DOWNGRADES to a mod-only check with a loud note rather than skipping (cf. B-GATE-HARDEN-1).

---

## 3. SOUL-EMBERTEETH-SUMMON - built

Will, 2026-07-14, verbatim: **"emberteeth soul should let you summon him."**

### Ground truth before this lane

`records\creature\monster\orthrus\um_emberteeth.dbr`: `Hero`, `charLevel [18, 43, 58]` (the
lowest-level summon source in the roster), `characterLife [2355.2, 2944.0, 3532.8]`, race `Demon`,
description `tagNewHero12`, skin `brimstoneorthus01.tex` - a two-headed brimstone fire-hound. His kit:
`retaliation_1fireperlevelx100levels`, `orthus_firebreath`, `ondeath_fireorb`,
`emberteeth_meleeattack`, `physdmg_meleeonly`, `pillarofflame`, `armor_passive`. Soul drop
`chanceToEquipFinger2 = 50` (a RANDOM-pool roamer - untouched by this lane).

His souls `...\soul\orthus\emberteeth_soul_{n,e,l}.dbr` (`tagSoulName331`, itemLevel 18/42/59)
**granted no skill at all** - a pure fire-stat ring. So the feature was genuinely unbuilt, as the
triage said.

### What shipped

New registry module **`tools/patches/emberteeth_summon.py`**:

1. 3 permanent pets `records\skills\soulskills\pets\emberteeth_{1,2,3}.dbr` + manual-cast button
   `records\skills\soulskills\summon_emberteeth.dbr`, built through the shared
   `_build_boss_summon` pipeline with `source = um_emberteeth.dbr`. That gets, for free and by the
   proven path: his own mesh/texture/anim table/attack skill, his attribute + attack cadence, his
   skill kit, his race and voice/alert/death/stun paks (build log confirms
   `characterRacialProfile<-Demon`, `voxSound<-orthrusvoxpak`, `alertSound<-orthrusalertpak`,
   `deathSound1<-orthrusdeathpak`, `stunSound<-orthrusstunpak`, Maenad residue stripped), gear
   mirrored through the sanctioned `_set_pet_equipment` loot-table path (never Monster.tpl
   equipment/loot copies - the documented crash class), the D19 pet-mobility assert, permanence (no
   `spawnObjectsTimeToLive`, the Lyia Leafsong convention).
2. All 3 soul tiers wired via `_wire_summon_soul` at `itemSkillLevel` 1/2/3, so the epic soul spawns
   the epic-tier pet (R-43's companion check), with any inherited `itemSkillAutoController` stripped
   so it is a pet BUTTON and never an on-attack proc (the D21 Long Nu / R-44 crowboar law).
3. **Every pre-existing benefit kept.** `apply()` snapshots 16 fields per tier (fire offence, burn,
   retaliation, `defensiveFire`, name tag, level, icon, mesh) and `SystemExit`s if any of them moved.
   The soul name `tagSoulName331` is deliberately NOT renamed - Will asked for a summon, not a rename.

### Tier band - derived, not invented

`char_level` mirrors the source exactly. For life, the shipped player-facing boss-summon pets fall
into two clean life-per-charLevel clusters: flagship uber bosses at ~250-296/level (Mountainblade
11000/43, Xeiwang 12000/48) and lesser summons at ~119-167/level. Emberteeth is a mid-tier
`tagNewHero` Hero, so he takes the LOWER cluster: `[2400, 6000, 9500]` (~133/level rising to
~164/level) - strictly progressing, above his wild form at every tier, nowhere near the uber band.
Damage/regen scaled off Mountainblade's L43 numbers by the same charLevel ratio.

### Player-surface checklist (standing law 3)

| surface | state |
|---|---|
| soul name | `tagSoulName331` (existing, unchanged - no rename asked) |
| granted-skill name | new tag `tagSVCSummonEmberteeth` = "Summon Emberteeth" |
| granted-skill icon | `DRXtextures\skill icons\soul\summonchimera{up,down}.tex` - a fire-breathing multi-headed beast glyph, the closest on-identity match for a two-headed brimstone orthrus. **Arc-verified present** in the shipped `DRXtextures.arc`; **verified UNCLAIMED** by any other `_SUMMON_SKILL_ICON` entry (`apply()` fails loud on a collision - the b85 bwpriest lesson) |
| pet-bar portrait | neutral summon-proxy (no `chimera_party_*` art ships) - never the Lyia nymph. Same documented position as pygmalion / eaterofdays / xeiwang / mountainblade. **Registered as debt: a bespoke Emberteeth portrait is an art call (WILL-CONFIRM)** |
| race / sounds | inherited from his own record (b81 / R-11) - build-log confirmed above |
| drop | unchanged at 50% (RANDOM-pool roamer) |
| in-game colour | not claimed - his own `brimstoneorthus01.tex` is reused verbatim, nothing recoloured |

---

## 4. LEGION-TERMINAL-50 - the R-42 fold-in, fixed at the classifier

### The ruling

R-42, Will 2026-07-16 (post-build42), verbatim:

> "LEGION TERMINAL @66: fine for now. QUEUED: fold 'death-transform terminals of RANDOM chains
> inherit the 50 rate' into the NEXT SOULS PASS"

### Why it was a classifier bug, not a per-record tweak

A death-transform chain (`um_legion_28 -> _28a -> _28b -> _28c`) is ONE encounter: only the HEAD is
ever named by a spawn pool or a placement proxy; every later stage is spawned by the previous stage's
death (`actorToSpawnOnDeath`). `soul_spawn_provenance_sets()` scans pools and placements only, so every
non-head stage came back in NEITHER set and fell through `soul_drop_rate()`'s final *"not proven to
spawn randomly -> keep the PLACED release rate"* clause. Correct for a genuinely placed monster; wrong
for a transform stage, whose spawn provenance is definitionally its head's. Visible symptom: the
Legion terminal shipped at 66 while the Legion himself - the record the random pools actually name -
ships at 50.

### The fix

`tools/build_svc_database.py`: `soul_spawn_provenance_sets()` now closes BOTH membership sets forward
over the `actorToSpawnOnDeath` graph (`_soul_transform_edges` + `_propagate_transform_provenance`).

Fixing it **there** - the shared provenance source - is the b59 `boss_charon_39` lesson:
`_soul_release_rate()` routes through `soul_drop_rate()`, which routes through these sets, and so does
`create_uber_souls.py`. A per-record override or a call-site patch would be bypassable; closing the set
is not. Propagation is FORWARD-only and the two sets are closed independently, so a stage reachable
from a PLACED head keeps 66 (`placed_proxy_members` is checked before `random_pool_members`) - the
"never over-cut a placed encounter" invariant survives. Cycles terminate (visited set).

### Roster-wide impact - exactly 2 live movers

Simulated over all 51,085 records with the old vs new sets:

```
random members: 1810 -> 1821 (+11)
placed members:   55 ->   60 (+5)

classifier verdicts that move: 9
  66 -> 50  Hero      arz=66.0  DROPS-A-SOUL   um_legion_28c.dbr
  66 -> 50  Hero      arz=66.0  DROPS-A-SOUL   um_possessedboar_spirit.dbr
  66 -> 50  Hero      arz= 0.0  (inert)        um_legion_28a.dbr
  66 -> 50  Hero      arz= 0.0  (inert)        um_legion_28b.dbr
  66 -> 50  Champion  arz= 0.0  (inert)        egypt_em_corruptedone_spawn_31.dbr
  66 -> 50  Champion  arz= 0.0  (inert)        egypt_bm_mummycaptainspawn_{22,25,28,31}.dbr
LIVE MOVERS: 2
```

The 7 inert ones carry no soul drop (`chanceToEquipFinger2 = 0`), so the verdict never reaches the
arz. The 2 live movers are exactly Will's case and its only sibling: both are terminals of chains
whose HEAD is a random-pool member, which is precisely the ruled class. `um_possessedboar_spirit` is
the surviving dropper that `double_soul_rulings` deliberately kept, so its rate must follow its chain.

Terminals of PLACED chains correctly do **not** move (`um_charonform2_ferryman_99`,
`um_polisgaoler_unbound_99`, `um_tantalus_unbound_99` stay 66) - and now for the right reason instead
of by classifier fall-through. The two R-48 100% carve-outs are untouched (`toxeus_souls_100` is the
final writer and both records are Boss-class, off this graph).

### Gate

`tools/verify_soul_drop_rates.py`:
* spot tests: `um_legion_28c` `(None, 66.0)` + an open Will-Q comment -> **`('RANDOM', 50.0)`**;
  new `um_possessedboar_spirit ('RANDOM', 50.0)`; new NEGATIVE-half assertions that
  `um_charonform2_ferryman_99` / `um_polisgaoler_unbound_99` / `um_tantalus_unbound_99` stay
  `('PLACED', 66.0)`.
* new **planted-regression negative test** "R-42 death-transform provenance closure": runs the
  classifier with the closure disabled and asserts the terminal falls back to 66 (so deleting
  `_propagate_transform_provenance` turns the gate red), plus a placed-chain never-over-cut case, a
  no-backward-flow case and a cycle-safety case.
* the two R-48 `_KNOWN_EXCEPTIONS` 100% entries are left exactly as they were.

---

## 5. BL-ENSLAVER-SPAWNS - all three sub-fixes already shipped; verified, gated, closed

The triage brief said sub-fixes (1) and (3) "were never reported closed". **The code says otherwise -
both shipped and the BACKLOG entry was simply never updated.** Reporting that honestly rather than
re-doing settled work:

### (1) DUPLICATE SPAWN - closed by b49, verified on the current arz

Verified against the b90 golden arz:

* **275** pool records name the Enslaver in a `name*`/`nameChampion*` slot.
* **273 of 273** roaming pools carry him at `weight = 1` **and `limit = 1`** - the per-slot MAX-count
  cap that makes "at most one Enslaver per pool per trigger" structural at any party size, regardless
  of `spawnMax` or draw-with-replacement.
* The other 2 are the whitelisted dedicated `q_enslaver_warband` / `q_yard_enslaver` set-piece pools
  (weight 100, multi-slot **by design**).
* Breadth is the b49 `undead`-family restrict (273 pools, was ~1224); `_EN_SWEEP_K = 600` puts the
  per-pool per-slot probability at `<= 1/24000`.
* The existing roaming-sweep gate already enforces weight/limit/probability/breadth/leak.

The residual case - two *independent proxies* placed near each other each rolling him - is **not
DB-expressible**: proxy placement lives in `Levels.arc`, and a proxy picks exactly ONE pool per
trigger (weightN on the proxy is a weighted pool CHOICE, proven in b38), so pool-reachability tells
you nothing about spatial adjacency. Its probability after b49 is ~1e-7 per adjacent pair.

**What was genuinely missing, and is now added** (`_verify_enslaver_roaming_sweep`, check 3c): `limitN`
caps a **slot**, not a **record**. If the Enslaver ever occupied TWO name slots of the same pool, each
would independently honour `limit=1` and the pool could still surface him twice in one trigger -
exactly Will's symptom, and invisible to every existing check (they all read a single `enl_idx`). The
new **adjacency assertion** requires each swept pool to name him **exactly once** across
`name1..18` + `nameChampion1..18`.

### (2) SPAWN RATE - closed by ruling

R-18: Will FORBADE a rate change on the roaming encounter frequency. Untouched. No action is the
correct action.

### (3) MARAUDER TANKINESS - already fixed in `_create_enslaver`, now gated

`apply_svc_patches._create_enslaver` already carries the fix, with Will's report quoted in the code:

```
# BL-ENSLAVER-SPAWNS (Will 2026-07-12): the marauders took ~0 damage in Epic. The
# near-immunity was this demon resist wall (defensiveLife 100 = FULL vitality
# immunity) AMPLIFIED by Epic/Legendary global scaling. ...
sf(M, 'defensiveLife',     40.0)   # was 100 (no longer vitality-immune)
sf(M, 'defensivePierce',   40.0)   # was 80
sf(M, 'defensivePhysical', 12.0)   # was 30
sf(M, 'characterLife', [10000.0, 14000.0, 18000.0])  # trimmed from 13k/18k/24k
```

DPS was deliberately left alone (`handHitDamage` 300/380). Confirmed present in the shipped arz.

**Roster measurement** (`um_enslaver_marauder_99`, Champion, `charLevel [40, 68, 100]`):

| tier | armor (`armor_passive` level) | vs Champion roster | characterLife | vs Champion roster |
|---|---|---|---|---|
| Normal | 78 | 78.9th pct (median 52) | 10000 | 99.2nd pct (median 582) |
| Epic | 226 | 78.5th pct (median 154, p90 246) | 14000 | **99.9th pct** (median 584, p90 2512) |
| Legendary | 468 | 91.6th pct (median 308, p90 462) | 18000 | 99.8th pct |

So his **armor ladder is level-appropriate and in-band** (compare `svc_vashkarr_lance` at
`charLevel 38/56/71` -> `75/204/405`); the outlier is **characterLife**, and it is the one axis the
fix already cut by 22-25%.

**What was genuinely missing, and is now added** (`_verify_enslaver_roaming_sweep`, check 0b): nothing
gated any of it, so a later wave could quietly restore the wall. The new gate sets **ceilings** on
`defensiveLife` / `defensivePierce` / `defensivePhysical` / `characterLife` **and floors** on
`handHitDamageMin/Max`, so the two halves of Will's ruling cannot drift apart: a future buff may not
re-wall him, and a future "rebalance" may not pay for a cut by gutting his threat instead.

### HONEST OPEN QUESTION FOR WILL (needs a fresh in-game read, not more code)

The fix above landed **after** Will's 2026-07-12 report and has never been confirmed in-game. At
14000 Epic life the marauder is still the 99.9th percentile of the Champion roster, and four spawn at
once, and they drop nothing. **Whether that is now "a killable elite" or still "a sponge" is a
playtest call, not a data call** - this lane deliberately did not invent a second cut on top of a fix
Will has not yet judged. Registered in the BACKLOG DEBT section; the ceilings above make any future
cut a one-line change.

---

## 6. BUILD + GATES

*(filled in from the wave-2 build; see the BUILD RECORD section appended below)*

## 7. DEBT REGISTER (standing law 4)

1. **69 OTHER dangling FX `.dbr` refs remain** (24 distinct missing targets), out of scope for
   B-FX-DANGLING-1 which names only the Chris ref. Measured this lane, by field:
   `particleEffectNames` 13, `targetFxPakName` 13, `particleEffectName1` 12, `skillBonusEffectName`
   10, `warmUpEffectName` 8, `radiusEffectName` 7, `charFxPakSelfNames` 2, plus singletons. Top
   targets: `records\skills\nature\renewalfx.dbr` (10), `records\effects\combat\skill_charge_strike01.dbr`
   (8), `records\effects\combat\skill_lethal_strike01.dbr` (6), `records\effects\petfx\ summonpet_wisp_fxpak.dbr`
   (6, note the stray leading space in the path), plus 4 `xxxrecords\...` typo-prefixed refs and one
   `# records\...` commented-out ref. These are NOT base-parity-provable as a single class the way the
   Chris slots were - each needs its own absent-vs-repoint call. **New BACKLOG item.**
2. **Emberteeth pet-bar portrait** is the neutral summon-proxy (no `chimera_party_*` art ships). A
   bespoke portrait is an art call - WILL-CONFIRM.
3. **Emberteeth in-game confirmation is launch-gated.** The summon, its icon, the pet's mobility on
   the orthrus rig and the 3-tier scaling can only be confirmed by Will on a fresh drop (TQ bakes item
   properties at pickup - test a FRESHLY dropped soul, not one already in a bag).
4. **Marauder tankiness re-read** - see the open question in section 5.
5. **`contracts_resources` pre-existing P1 volume** (b90 DEBT item 1) is unchanged by this lane and
   still needs its own triage lane.
