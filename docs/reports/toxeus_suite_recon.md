# Toxeus Encounter Suite - Recon (BACKLOG #32)

> Read-only recon for the mandate at `docs/BACKLOG.md` line 2152 ("Toxeus encounter suite:
> 10-25% canonical entrance spawn, rant scroll (MP per-player), Legendary stalker feasibility,
> 6-player checklist (#32)"), Will greenlit 2026-07-14. Branch `feat/toxeus-encounter-suite`,
> base = main HEAD `5a52ef2`. No heavy build was run (another workflow owns builds); all claims
> are from source + docs + a cheap registry selfcheck. Ships in a later integration build.

---

## 0. HEADLINE (read this first)

> **⚠️ ROUND-2 UPDATE (2026-07-14): this recon MISSED a real 4-6-player double-spawn.** An adversarial
> vet of the shipped suite found that the deep-chest Devourer (`egg_blooddragon`) and the parchment
> (`demon_01_cluster_toxeus50`) - the two M15 Toxeus pools, NOT reached by the recon's `_BT_POOL`-only
> analysis in section 3 - both kept the base-game `proxyPoolEquation` (`proxypoolequation_02`), which
> floors `championMax=1` up to **2 at 4-6 players** = TWO Blood Toxeus in the deep-chest room for a
> 4-6-player party (`np<=3`, incl. Will's co-op, was clean). Round-2 FIX: `_apply_m15_toxeus_group_joins`
> now neutralises the equation on both pools, and `toxeus_suite.py` Part D `_verify_toxeus_champion_cap`
> is now ROSTER-DERIVED over EVERY `um_bloodtoxeus_99` pool (was `_BT_POOL`-only). So section 3's "no
> change recommended" and item 6.1's "single-Toxeus" checklist were both incomplete - corrected in
> `docs/MULTIPLAYER_COMPAT.md` §M4.2 and item 3 below. The rest of this recon (ambush mechanism, scroll,
> stalker verdict) stands.

**BACKLOG #32 is already built, registered, committed, and gate-GREEN on `main`.** The four
mandated parts (entrance ambush, rant scroll, Legendary-leaning stalker, 6-player readiness) all
ship as the registry module **`tools/patches/toxeus_suite.py`** (Parts A/B/C/D), registered at
`tools/patches/__init__.py:83`, first landed as commit `cbe5c7c` ("build37: Toxeus Encounter Suite
as registry module (backlog #32)") with four follow-ups (`711f385` gate-relocation, `630bb9b`
+ `2073fe6` per-slot-limit, `6d2f26e` b49 breadth cut). Its `verify()` hook is logged GREEN in the
build37/38/39/40 gate records (`docs/BACKLOG.md` lines 118, 173, 215, 244).

**The BACKLOG #32 ask-line (2152) is STALE** - it still reads as an open ask, but the work landed.
This is an INDEX-staleness case (the memory board warns about exactly this), not missing work.

**This is an EXTEND / VERIFY situation, not greenfield.** Do not duplicate the module. The genuinely
open items are small and enumerated in section 6:

1. **The suite-specific 6-player checklist is NOT in `docs/MULTIPLAYER_COMPAT.md`** (that doc is
   dated 2026-07-08 and predates build37; it covers the deep Hemorrheus boss but not the ambush,
   the rant scroll's per-player wiring, or the Endless Hunt). This is the one clear doc deliverable.
2. A handful of **launch-gated live verifications** (rant-scroll monster-equip per-player expansion;
   `netherstrike` anim on the table-less rig; the `np*np` MP spawn-eq parse) that only Will's
   in-game test can close.
3. A **design-coherence flag**: the entrance corridor actually rolls Blood Toxeus **twice** (50% at
   the parchment room + 15% at drxFirstRoom); confirm that is the intended aggregate.

The referenced design inputs (`scratchpad/specs/toxeus_encounter_suite_spec.md`,
`WILL_DECISIONS_2026-07-11.md`, `amgoz1_design_voice.md`) lived in gitignored `scratchpad/` and are
**gone** from the tree. The deciding text quoted below is reconstructed from the module's own inline
citations of Will + the committed design docs.

---

## 1. Ground-truth: what actually ships today

### 1.1 The module (Parts A-D)

`tools/patches/toxeus_suite.py` (`MODULE_NAME = 'toxeus_suite'`), registry slot 5 of 13. Every one
of its 18 `apply_svc_patches` (asp) dependencies resolves on current main (verified: 1 def-site each
for `_BT_MONSTER/_BT_PROXY/_BT_POOL/_EN_RIG_DONOR/_MOD_AUTHORED_SPAWN_PROXIES/_BT_DONOR_LIMIT/`
`_SS_FLASH_POWDER/_AC_ON_HIT/_EN_AUG_ANATOMY/_BT_AUG_OPENWOUND/_EN_SWEEP_K/_EN_SWEEP_CEIL/`
`_EN_SWEEP_SLOT_LIMIT/_EN_SWEEP_BAD_SUB/_EN_BOSS/_EN_SWEEP_MAX_P/_EN_SK_FLASHPOWDER/_EN_SK_NETHERSTRIKE`).

| Part | What it ships | Key records |
|---|---|---|
| **A** entrance ambush | clone `q_bloodtoxeus_lone` -> `q_bloodtoxeus_ambush` at `chanceToRun=15`; reuse `_BT_POOL`; register in `_MOD_AUTHORED_SPAWN_PROXIES` | `records\drxmap\proxy\q_bloodtoxeus_ambush.dbr` |
| **B** rant scroll | Parchment readable + 2 loot tables (per-player `numSpawn`) wired to Blood Toxeus Misc4 @100%; 3 tags | `svc_toxeus_rant.dbr`, `toxeus_rant_perplayer.dbr`, `toxeus_rant_item.dbr` |
| **C** Endless Hunt stalker | ShadowStalker-rig roaming Toxeus + granted-MOVE soul + Hades-only sweep + fail-loud sweep verify + inert Legendary-window experiment | `um_toxeus_hunt_99.dbr`, `toxeus_hunt` soul trio, `limit_legendary_only.dbr` |
| **D** 6-player readiness | fail-loud champion-count-cap invariant (<=1 Toxeus at any party size) + the per-player scroll | (gate only) |

The module correctly runs its gates in `verify()` (post-finalization), not `apply()` - the build37
gate-relocation law (`__init__.py` EXECUTION ORDER; commit `711f385`).

### 1.2 The map placement is CANONICAL, not TESTHUB

`tools/build_section_surgery.py:1261-1265` (`B41_SPECS` item 5) injects `q_bloodtoxeus_ambush.dbr`
into `levels/world/xbloodcave/drxfirstroom.lvl` at level-local `(100.0, 1.0, 50.0)`, identity rot,
flags=0, no `0x14`. `B41_SPECS` is folded into the canonical `INJECT_SPECS` unconditionally at
`build_section_surgery.py:2310-2312` ("Applies to BOTH map variants; canonical uses INJECT_SPECS
directly"). So the ambush is real shipped content, on-mesh (b41 survey: d<=0.14u, comp#1, y=1.0
native-confirmed), not gated behind `SVC_TEST_HUB`.

### 1.3 The canonical entrance = drxFirstRoom (confirmed)

`docs/blood_cave_walkin_entrance_plan.md` proves the engine-native walk-in chain (all `0x0a`
grid edges): `Random09A --west--> xPassageTransitionStart --> BC_initialpathway -->
drxFirstxistion_connection --> drxFirstRoom --> cave`. `drxFirstRoom` is the first real blood-cave
room after the transition passage = "at/near the canonical entrance". The ambush sits there.

### 1.4 Dry-run verification (no heavy build)

- `py tools/patches/_check_registry.py` -> `selfcheck OK: 13 module(s), order b82195e9...`, EXIT=0
  (imports `toxeus_suite`, validates the MODULE_NAME + apply() contract).
- `py -m py_compile` on `toxeus_suite.py`, `apply_svc_patches.py`, `build_section_surgery.py` -> OK.

---

## 2. GATE: ambush_subject

**Verdict: the ambush subject is BLOOD TOXEUS = `um_bloodtoxeus_99` = in-game
"Toxeus the Murderer, Devourer of Blood" (internal codename Hemorrheus / "Blood Toxeus").**
NOT the green Athens Toxeus (`um_toxeus_21`), NOT the SP super-Toxeus (`um_toxeus_99`), NOT the
Enslaver (a separate, later Toxeus-family roaming boss).

Deciding text (reconstructed - the WILL_DECISIONS file is gone):

- Module docstring, Part A: *"A lone Blood-Toxeus proxy at chanceToRun=15 (Will: 15% in
  drxFirstRoom), a clone of the gate-proven chest proxy q_bloodtoxeus_lone reusing its exact pool
  (_BT_POOL = 1 Toxeus + 2 blood-demon adds)."* (`toxeus_suite.py` Part A header.)
- `docs/BLOOD_TOXEUS_DESIGN.md:3` rename note: *"the boss now ships as 'Toxeus the Murderer, Devourer
  of Blood' ... his soul as '{^F}Devourer of Blood Soul'"* (Will 2026-07-07). This is the crimson
  cauldron-reforged superboss, deliberately the hardest Toxeus in the mod (L40/68/100, 13/18/24k HP).
- Record identity: `apply_svc_patches.py:9056` `_BT_MONSTER = ...\skeleton\um_bloodtoxeus_99.dbr`;
  `:9058` `_BT_PROXY = ...\q_bloodtoxeus_lone.dbr`; `:9059` `_BT_POOL`.

Why Blood Toxeus is the right subject: it is the mod's flagship Toxeus, it already has a
gate-proven single-main pool (`_BT_POOL`), and reusing that monster keeps ONE Toxeus roster
(the ambush Toxeus, the deep chest Hemorrheus, and the parchment Toxeus are all the same
`um_bloodtoxeus_99` record - so the rant scroll wired to its Misc4 drops from all of them). No new
monster, no new pool.

---

## 3. GATE: spawn_mechanism_rec

**Recommendation: KEEP the shipped mechanism - `chanceToRun` on a dedicated single-instance clone
proxy reusing the proven single-main pool. It is the correct, safe "chance-once" lever and is what
this exact lane's hard-won lessons point to.**

How a 10-25% chance-once spawn is expressed (the three candidates the mandate named):

| Mechanism | Verdict | Why |
|---|---|---|
| **Proxy `chanceToRun` field (SHIPPED)** | **RECOMMENDED** | `chanceToRun` is a Proxy.tpl field, rolled ONCE per proxy instance at level-load spawn resolution. `q_bloodtoxeus_ambush.chanceToRun=15.0` = a single clean ~15% roll for "spawn the pool or not". No equation, no per-difficulty scaling, no quest state. The donor `q_bloodtoxeus_lone` carries `chanceToRun=100.0` (`apply_svc_patches.py:9330`); the clone overrides value-only (dtype preserved). |
| Proxy-pool `spawnMax/champion` equation | **REJECT for the CHANCE** | Different lever: it controls the COUNT of mains/champions, not whether the encounter fires. This is exactly the `proxypoolequation_02` **double-spawn class** the mandate warns about (2-mains-at-1-player). It is the wrong tool for a probability. |
| Quest `OnLevelLoad` | **REJECT** | Trips the QUESTS-256-window law (`CLAUDE.md`, `docs/QUEST_STATE_INJECT.md`) and the fragile 200x-repeat idiom that already failed the blood-cave entrance twice. Adds per-character state for a stateless coin-flip. |

**The double-spawn trap is structurally gated (not just avoided).** `_verify_mod_spawn_proxies_eligible`
(`apply_svc_patches.py:15120-15157`) runs three sub-checks over EVERY entry in
`_MOD_AUTHORED_SPAWN_PROXIES` (which now includes `q_bloodtoxeus_ambush`, appended by the module):

- **(A) champion crowd-out** - fails if `spawnMax - championMax < 1` (boss never spawns; only adds).
- **(C) NO INHERITED SPAWN-COUNT EQUATION** - fails if the pool still carries `proxyPoolEquation`
  (the `proxypoolequation_02` re-scale that floors a 3/2 pool to 4/2 = 2 bosses at 1 player). The
  build is GREEN, so `_BT_POOL`'s equation IS neutralized (`_svc_neutralize_pool_equation`) and the
  literal `spawnMax=3, championMax=2` -> exactly **1** Toxeus main deterministically at any np.
- **(B) limit-window containment** - the ambush inherits `difficultyLimitsFile=limit_bloodtoxeus`
  with windows `[1..110]` on N/E/L (`apply_svc_patches.py:9305-9310`), so the L100 boss is not
  scaled down and spawns at authored level on **all three difficulties** (correct for an entrance
  ambush available from the first playthrough).

The module's Part D (`_verify_toxeus_champion_cap`) adds the matching UPPER bound: `_BT_POOL` yields
**exactly** 1 guaranteed Toxeus main, so no party size can surface >1 (championMax is never
per-player-multiplied). Lower bound (>=1) + upper bound (==1) together = "one Toxeus per encounter,
any party size" as a hard invariant.

Net: the ambush spawn is the proven-shape `q_<boss>_lone` template the lane's lessons demand,
multiply-gated against the exact double-spawn history. No change recommended.

---

## 4. GATE: scroll_mechanism

**The rant scroll ships (Part B) and its MP per-player wiring is AE-parse-safe; the ONE unproven
edge is monster-equip-slot per-player expansion, which is launch-gated with a documented fallback.**

Chain (all in `toxeus_suite.py` Part B):

1. **Readable item** `svc_toxeus_rant.dbr` = clone of the widow-letter Parchment chassis
   (`finalletter.dbr`), `itemClassification=Magical`, `itemText=tagSVCToxeusRantTEXT` (the screed),
   distinct `{^r}` name + on-ground label. Parchment.tpl drives the right-click "read".
2. **Inner table** `toxeus_rant_item.dbr` = `LootItemTable_FixedWeight`, single member -> the item @
   weight 100.
3. **Outer per-player table** `toxeus_rant_perplayer.dbr` = **`FixedItemLoot.tpl`** with
   `numSpawnMinEquation = numSpawnMaxEquation = 'numberOfPlayers*1'` -> `loot1 -> the inner table`.
4. **Wire**: `um_bloodtoxeus_99.chanceToEquipMisc4 = 100`, `lootMisc4Item1 = [T,T,T]` (all three
   difficulty columns), `dropItems=1`.

**MP evidence (why this is AE-safe, per `docs/MULTIPLAYER_COMPAT.md`):**

- The SV multiplayer risk is specifically SV's `/`-bearing **proxy-spawn** `RunEquation` formulas,
  which the narrow AE spawn evaluator rejects (`MULTIPLAYER_COMPAT.md` R1/M1.2). **This scroll does
  not use that path.** `numSpawn*Equation` is a LOOT-table field and `'numberOfPlayers*1'` is `/`-free,
  using only `*` - the same operator class the base game's own `numSpawn` equations use
  (`MULTIPLAYER_COMPAT.md` M1.1: "all `numSpawnMax/MinEquation` values PASS ... `+ - *` only"). No
  `np*np`, no `/`. So the equation itself parses.
- `numSpawn*Equation` lives ONLY on `FixedItemLoot.tpl` (DB-verified 311/311 such records per the
  module comment), which is why the outer table must be that template.

**The launch-gated unknown (honest status):** whether a MONSTER **equip slot** (Misc4) honors the
sub-table's `numSpawn` per-player expansion is proven only for **containers**, not equip slots. If
Will's 2-player test yields 1 copy instead of 2, the module documents the fallback inline: a
corpse/chest whose `loottable = toxeus_rant_perplayer` (the SAME already-container-ready table),
spawned on Blood-Toxeus death - a one-record + one-death-skill follow-up. The reusable per-player
table is already authored, so the fallback is cheap.

Duplicates on repeat kills are accepted (Will: "guaranteed one-per-player Misc4 @100%, duplicates on
repeat kills accepted" - module Part B header).

**amgoz1 gate:** the screed TEXT (`_RANT_TEXT`, ~180 words, Toxeus's voice, treats the original
murderer as the blood-cult progenitor) and the `{^r}The Murderer's Screed` name are CREATIVE CONTENT
and must go to Will for veto before ship (per the amgoz1 creative-bar + flag-creative-text rules).
Not reproduced here; see `toxeus_suite.py` `_RANT_TEXT`.

---

## 5. GATE: stalker_inputs

**Verdict: a ROAMING + strictly-Legendary-only stalker as a pure data gate is NOT cleanly feasible;
the shipped Hades-confinement is the honest closest approximation and is live. A FIXED-placement
Legendary-only stalker IS cleanly feasible (Hydra pattern) if Will would trade roaming for a fixed
spot - and if so, use that PROVEN pattern, not the module's inert min-player-level experiment.**

### 5.1 What shipped (the Endless Hunt)

`um_toxeus_hunt_99` on the ShadowStalker rig (`am_deathstalker` donor, distinct iceheart skin,
scale 1.9, Boss `[40,68,100]`, life 16/22/30k, pierce/pursuit kit), dropping its own granted-MOVE
soul (the flash-powder shadow-burst - the third real Toxeus-family build beside summon-Devourer and
summon-Enslaver). Roams **Hades trash pools ONLY** via a dedicated sweep
(`_sweep_inject_legendary_stalker`): appended at weight 1 into eligible `xpack\proxieshades` pools so
`p_slot <= 1/2400`, each appended slot carrying **`limit=1`** (a per-slot MAX-count cap) so a pack
pool with `spawnMax>1` cannot surface 2+ Hunts in one trigger (the "two-in-one-trigger" defect the
Enslaver v2 sweep fixed). A fail-loud verify (`_verify_legendary_stalker_sweep`) re-derives the
touched set and proves 0 non-Hades/boss/quest/hero leaks. BACKLOG build40 record: "345 additive
`um_toxeus_hunt_99` inserts at weight 1".

Because Hades = Act-4/endgame, "Hades-only" reads in practice as "effectively Legendary/endgame" -
the module's stated intent ("the honest closest thing to 'Legendary-only' TQAE supports").

### 5.2 The feasibility evidence (E/L audit)

The `feat/el-boss-audit` branch's `docs/reports/el_boss_audit.md` (not yet merged to main)
enumerates TQAE's real difficulty-gating mechanisms:

- **Pool-slot gating (dominant, PROVEN):** a proxy with `pool1` = trash/empty and
  `poolLegendary1..N` = a boss pool spawns the boss **only on Legendary**. Hydra is exactly this:
  "Normal+Epic empty, `poolLegendary1 = bosspool_24_hydra` (**Legendary-only**)". Arachne/Aniketos
  use `poolEpic1`/`poolLegendary1` with no `pool1`.
- **`difficultyLimitsFile` window:** scales a monster's effective LEVEL toward the window; it does
  NOT filter spawn (a below-window main is scaled, not suppressed - proven by the eligibility gate
  and by L>75 monsters spawning under max-75 limits). This is why the module's inert
  `limit_legendary_only` experiment (N/E window `[85..110]`, L `[1..110]`) is a WEAK, unproven gate:
  it bets that "player level below window min" = "dormant", which the engine does NOT demonstrably do.

**Reconciliation:** the module's "true data-only gate is not cleanly supported" verdict is correct
**for the ROAMING variant** - roaming = appending the Hunt into many SHARED all-difficulty trash
pools, and there is no per-appended-member difficulty filter, so you cannot make a roaming member
Legendary-only without editing every pool's Legendary slots. But a **FIXED** Legendary-only stalker
IS cleanly feasible via the Hydra `pool1`-empty/`poolLegendary1` pattern (a dedicated proxy + a
stalker pool, placed at a Hades/endgame spot). The grep for any existing "Legendary-only spawn"
helper in `apply_svc_patches.py` + `docs/*.md` returned nothing, confirming no such helper exists
yet - it would be new work.

### 5.3 If Will wants a TRUE Legendary-only stalker (option, not a blocker)

Recommended path = the PROVEN Hydra pattern, NOT the inert min-level experiment: clone
`q_bloodtoxeus_lone` -> `q_toxeus_hunt_lone` with `pool1` empty (or a trash filler) +
`poolLegendary1 = <a single-member um_toxeus_hunt_99 pool>`, `difficultyLimitsFile` = a `[1..110]`
no-cap file, placed at one Hades/endgame spot via `INJECT_SPECS`. That gives a guaranteed
Legendary-only appearance at a known location. The trade vs the shipped roaming Hunt: findable-but-
fixed instead of rare-but-anywhere. Keep the roaming Hades Hunt as the "apex hunter" flavor OR
replace it - Will's call. Either way, the module's inert `limit_legendary_only` artifact should be
treated as an unproven experiment, superseded by this proven pattern.

---

## 6. GATE: risks (open items, ranked)

1. **[DOC - the one clear deliverable] 6-player checklist missing from `docs/MULTIPLAYER_COMPAT.md`.**
   That doc (2026-07-08) covers the deep Hemorrheus boss (its §M2.3 item 3) but has NO section for
   the build37 suite: the entrance ambush, the rant scroll's per-player wiring, or the Endless Hunt.
   The mandate item (d) asks for a whole-suite 6-player checklist there. Draft contents to lift:
   (i) ambush spawns exactly 1 Toxeus + 2 adds at any party size (Part D invariant - static-proven;
   confirm live at np>=2); (ii) rant scroll drops N copies for N players (the launch-gated Misc4
   `numSpawn` edge - confirm 1 copy/player at np=2, else flip to the container fallback); (iii) the
   Endless Hunt spawns at most 1 per Hades pool per trigger at any party size (the per-slot `limit=1`
   cap - static-proven; confirm no runaway in co-op); (iv) all three are host-authoritative placed
   proxies / monster drops (standard TQ replication) with byte-identical mod files required.

2. **[LIVE - launch-gated verifications]** Only Will's in-game test can close: (a) rant-scroll
   monster-equip per-player expansion (Part B fallback ready); (b) `netherstrike`'s `LethalStrike`
   special anim resolving on the TABLE-LESS ShadowStalker rig (module ships it as a moderate-chance
   flavor blink; a silent no-op leaves the Hunt fully functional); (c) the `np*np` MP spawn-eq parse
   (`MULTIPLAYER_COMPAT.md` M1.5 - unrelated to the suite but the standing launch check;
   `SVC_MP_SPAWN_LINEAR=1` fallback ready). Per the RESTART-STEAM-BEFORE-TEST law, any test ping must
   kill TQ+Steam, restart, and hash-verify the deploy landed first.

3. **[CORRECTED round-2 2026-07-14 - see below] The entrance corridor rolls Blood Toxeus TWICE.**
   ~~Besides the 15% drxFirstRoom ambush, the adjacent parchment room `drxfirstxistion_connection`
   rolls Toxeus at 50% via `demon_01_cluster_toxeus50`... aggregate 50% + 15%.~~
   **CORRECTION (round-2 vet MEDIUM, ground-truth verified):** this was WRONG. The M15 parchment
   feature is an ORPHAN - the DB lane authored `demon_01_cluster_toxeus50` (proxy+pool) but the MAP
   lane NEVER injected the repoint of the parchment `demon_01_cluster` instance to it. The repoint is
   only a COMMENT at `build_section_surgery.py` `drxfirstxistion_connection` (the injection list holds
   just the finalletter + Enslaver-warband specs, no derived-proxy spec). So the parchment room still
   spawns the plain `demon_01_cluster` (NO Toxeus), and the ONLY entrance Toxeus is the single ~15%
   `drxFirstRoom` ambush - which cleanly matches the 10-25% mandate. The `demon_01_cluster_toxeus50`
   pool was ALSO carrying the un-neutralised `proxypoolequation_02` (the 4-6P double-spawn class); it
   is now equation-neutralised in round-2 (defense-in-depth) so it is MP-safe if/when the parchment
   repoint ships. FLAG TO WILL: ship the map repoint (make the 50% parchment Toxeus real) or retire
   the orphan `demon_01_cluster_toxeus50` (+ sibling orphan `q_bloodtoxeus_lone_50`).

4. **[STALE INDEX] `docs/BACKLOG.md:2152` lists #32 as open.** It shipped (gate-GREEN build37-40).
   The ask-line should be moved to a SHIPPED section with the residuals above, so #32 is not
   re-dispatched as greenfield again. (Low risk, but it caused this exact re-dispatch.)

5. **[KNOWN, BENIGN] Registry collision `um_toxeus_hunt_99` <- toxeus_suite + boss_skill_fix.**
   Logged in the build40 gate record (`BACKLOG.md:175`); later-wins is legal + visible (boss_skill_fix
   runs last to repair the Hunt's skill-usage wiring on the final record). No action unless the
   collision changes shape.

6. **[VERIFY] `q_bloodtoxeus_lone_50` may be an orphaned DB record.** `_create_blood_toxeus_proxy_50`
   (`apply_svc_patches.py:10051`) still builds the 50% parchment proxy, but the map M15 note
   (`build_section_surgery.py:1928-1942`) says its standalone placement was REMOVED in favor of the
   `demon_01_cluster_toxeus50` mechanism. If nothing places `q_bloodtoxeus_lone_50`, it is harmless
   dead weight - worth a cleanup pass, out of this suite's scope.

7. **[amgoz1 VETO GATE] Creative text needs Will's sign-off before ship:** the rant screed
   (`_RANT_TEXT`), the scroll names (`{^r}The Murderer's Screed` / `A Parchment Slick with Blood`),
   and the Hunt's name/desc (`{^r}Toxeus the Murderer, the Endless Hunt` / `{^F}...the Endless Hunt
   Soul`). All are held to the amgoz1 monster-identity-driven bar.

---

## 7. Bottom line for the integration build

The suite is DONE and gate-green; do not rebuild it. The integration lane's job is: (1) add the
6-player checklist to `MULTIPLAYER_COMPAT.md`; (2) run Will's launch-gated live checks with the
restart-Steam discipline; (3) get Will's veto on the creative text and a decision on the
double-entrance-roll coherence and whether he wants the proven fixed Legendary-only stalker in
addition to / instead of the roaming Hades Hunt; (4) tidy the stale BACKLOG #32 line + the possibly
orphaned `q_bloodtoxeus_lone_50`. All are small; none require touching the shipped `toxeus_suite.py`
logic.
