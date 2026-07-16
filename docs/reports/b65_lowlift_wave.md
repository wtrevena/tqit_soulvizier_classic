# b65 - Low-lift batch (round 1): 5 items, DB-only + one map placement

**Branch:** `feat/lowlift-wave` (shared worktree `.claude/worktrees/lowlift`, off `main` @ `c8883d6`)
**Baseline (golden):** build41 arz `eb8bc377` (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
51,023 records), CANON Levels `3f05c227` (`work/SoulvizierClassic/Resources/Levels.arc`).
**Commits (this branch, oldest -> newest):**
`907635e` (item 1), `afd762b` (item 2), `2791c38` + `231295d` (item 3, DB + map),
`c2e1dde` (item 4), `79ce459` (item 5).

All five items are DB-only (four new `tools/patches/` registry modules + two edited existing
modules) except item 3, which also has one map `INJECT_SPECS` addition. **Nothing built/deployed
this pass** - every item is verified via dry-run replay against the golden arz (and, for item 3's
map half, dry-run injection into a copy of the deployed level blob). All five ride the next
integration build.

---

## Item 1 - SVAERA 5-set re-link (`tools/patches/svaera_sets.py`)

**Git-blame gate (per the brief): NOT an intentional strip.** `git log --all -S itemSetName` and
`-S drxset0` over `tools/` turn up no commit that ever touched these 13 items or these 5 set
records. Ground-truthed directly against the arz sources: the 13 member items exist, byte-for-byte
structurally consistent, in **all three** upstream sources (`soulvizier_098i`/`_0.9`/`_041`) as
SV098i-original standalone uniques, and in every one the `itemSetName` field key is **absent**, not
merely empty - amgoz1's originals never had it. The 5 `drxset0{49,51,52,53,058}.dbr` grouping
records are **also** absent from all three upstream sources - SVAERA's own additive invention,
never grafted into our build. There was nothing to strip; proceeded with the verifier-corrected
recipe.

**What shipped:** authored the 5 set records with SVAERA's exact per-piece set-bonus fields (field
name + dtype + value ported verbatim from the live SVAERA arz, `2076433374`), pointed
`setMembers` at our 13 items' exact stored paths, minted 5 fresh tags (`tagSetName049/051/052/
053/058`) following our own established non-xpack `drxset001-047` numbering convention (rather than
porting SVAERA's own unrelated tag keys `tagSetNameLE1/3/5/6`/`xtagArtifactDescription062`), and
re-linked `itemSetName` on the 13 items. No item/loot/map change (art already ships, items already
droppable).

**Verified:** dry-run replay vs golden - record-diff **+5 / 0 removed / 13 modified**
(`itemSetName` only); `verify()` PASS (round-trip back-link + tag resolution); idempotency (re-apply
raises `SystemExit`); negative test (corrupted back-link trips `verify()`). `py_compile` clean;
`_check_registry.py` OK.

---

## Item 2 - Two relics (`tools/patches/turtleshell_relics.py`)

**Ground-truthed "the magenta turtle shell custom relic" first.** It is the mod's proven Common-tier
`ItemCharm` recipe: base-game `records\item\animalrelics\{01,02,03}_act1_turtleshell.dbr` donor
(5-shard `completedRelicLevel`, own completion-bonus `LootRandomizerTable`, own FixedWeight loot
table). "Magenta" is the engine's `Class=ItemCharm`/`ItemRelic` tooltip-color convention, not a
`{^F}` text tag - confirmed absent on Turtle Shell, D10 Emberscale, and C5 Ereban Heartstone (the
two prior waves that already clone this exact shape).

**(a) Dionysus trickster archer -> "The Reveler's Ruse".** Wired onto the Satyr Archer family
(`records\creature\monster\satyr\ar_archer_{01..06}.dbr`, "Satyr ~ Skirmisher"/"Satyr ~ Veteran
Skirmisher" - satyrs are Dionysus's mythic revelers; the archer line is our system's own distinct
identity, proven by its dedicated `satyrarcher_soul_*`/`satyrveteranarcher_soul_*` family). Clones
the turtle-shell **item** donor directly (zero new art), bow-only, 5-shard attack-speed + %pierce
ladder, a 6-entry w1500 completion-bonus table (pierce/OA/dex/str/life/poison-resist via the
generic prefix affix, avoiding a theme collision with the existing base-game Dionysus'-Wineskin-
specific bonus record), wired at 7% on the verified-free `lootMisc4` slot on all 6 bodies.

**(b) Dune Fiend -> already satisfied, nothing authored.** Per the backlog's own conditional
("verify dune fiends don't already drop one" first): they do -
`records\creature\monster\antlion\em_dunefiend_{32,34}.dbr` already drop **Fiend Carapace**
(`records\item\animalrelics\{01,02,03}_act2_fiendcarapace.dbr`) at 12%. Ground-truthed present in
all 3 upstream sources, absent from the vanilla base-game `database.arz` - amgoz1's own SV098i-
original desert-terror relic, same turtle-shell shape. This module authors nothing for Dune Fiend;
`verify()`/`apply()` both assert the pre-existing wiring is still intact (a regression guard).

**Verified:** dry-run replay - record-diff **+9 / 0 removed / 6 modified** (the 6 archer bodies,
`lootMisc4` only); `verify()` PASS; idempotency; 2 negative tests (corrupted charm slot; simulated
Dune Fiend regression) both trip `verify()`.

Name flagged for Will veto (creative naming per the amgoz1 bar - see feedback-amgoz1-creative-bar.md,
re-distilled from first principles since `amgoz1_design_voice.md` is gone from the tree); ships as
default per the standing instruction.

---

## Item 3 - Legendary-only Toxeus stalker (B-TOXEUS-STALKER-1)

**DB (`tools/patches/toxeus_legendary_stalker.py`):** the proven Hydra pattern - `pool1` (Normal) +
`poolEpic1` (Epic) EMPTY, `poolLegendary1` = a single-member pool, so the proxy spawns ONLY on
Legendary. Ground-truthed against our own most recent live precedent
(`minobossproxy_aniketos`/`questbossproxy_celtheano` - "no `pool1` at all, `poolEpic1`/
`poolLegendary1` = a guaranteed single-member boss pool", build41's "Aniketos E/L restore"),
narrowed to Legendary-**only** by never setting `poolEpic1` at all (Aniketos sets it too, making it
Epic+Legendary). Deliberately NOT the inert `limit_legendary_only` `ProxyLimits` experiment
`toxeus_suite.py` documents as untested Option 2 (a `difficultyLimitsFile` window only ever *scales*
a monster's level, never *filters* whether the proxy resolves - see `docs/MULTIPLAYER_COMPAT.md`
M4.6 and the toxeus_suite docstring's own Option-1-vs-Option-2 framing).

Reuses the shipped Endless Hunt stalker (`records\creature\monster\shadowstalker\
um_toxeus_hunt_99.dbr` - ShadowStalker rig, Boss, charLevel `[40,68,100]`, already wired with its
own `{^F}` svc_uber soul at the Boss release rate) **verbatim** - no new monster clone, no new soul.
Clones the gate-proven `q_bloodtoxeus_lone` proxy donor (inheriting its no-cap `limit_bloodtoxeus`
`[1..110]` window), clears `pool1`, adds `poolLegendary1`/`weightLegendary1`, repoints the preview
mesh/scale to the Hunt's own silhouette. Registered in `apply_svc_patches._MOD_AUTHORED_SPAWN_
PROXIES`; the monolith's own `_verify_mod_spawn_proxies_eligible` gate re-run over the post-apply db
**passes with the new entry included** (17 proxies total).

**Map (`build_section_surgery.py`):** surveyed the deployed CANONICAL `Levels.arc`
(`tools/debug/survey_uberboss_spots.py`, md5 `3f05c227` == the recorded build41 CANON Levels md5)
and placed at `xpack/levels/area08_hadespalace/hadespalace_floor04_04.lvl` local `(38.0, 45.0)`,
Y=15.0 - the **least-crowded** Hades Palace floor (every other floor already carries its own
distinct set-piece: Menoetes in floor_03, the Polis Vault jailer horde in floor04_01, the other 2
generals' guard pairs in crystal_03/crystal_04). `clr=100%` on all three tilesets, reachable
component #1 (the main walkable mass, 76,499 cells - cross-calibrated against the shipped
`q_general_b_guardpair` spot, which the same tool/frame reads at `d=0.10u`), ~29u from the nearest
existing encounter, 7-17u from the nearest static set-dressing, 0 collision with any functional
entity (quest NPCs/gate objects cluster elsewhere on the floor). Appended to the existing
`B41_GUARDB_KEY` host list (never clobbers the general's guard pair).

Dry-run injection into a COPY of the deployed level blob (`inject_into_sv_only_blob`, the v0x0e
branch this level routes through): **+1 instance** (59 -> 60), landing at exactly local(38.0,45.0)
with the correct dbr, the `0x0b` navmesh section **byte-identical** before/after, every other
section (`0x06`/`0x17`/etc.) untouched.

---

## Item 4 - Double-soul rulings (`tools/patches/double_soul_rulings.py`)

Will's rulings, delegated to the standing recommendation (`docs/reports/b56_legion_soul_stages.md`
"distinct-soul chains" table) - documented as such.

**(a) Possessed Boar - FIX (terminal-only, typo-twin dup retired).** Ground-truthed: the
**terminal**'s soul (`soul\boar\possesedboar_soul`, granting `drxstormsurge`) is amgoz1's own
SV098i-original - present in all 3 upstream sources AND a reagent in 6 base-game enchanting
formulas (`lesserpotionoffortitude`/`lesserpotionofexperience`, all 3 tiers). The **head**'s soul
(`soul\svc_uber\possessedboar_soul`, correctly-spelled "svc_uber" = our own mod-generated-soul
territory, granting `thunderballnova`) is a build-introduced typo-twin duplicate. DETACH the head
(chance 66->0, loot refs cleared) then RETIRE the 3 now fully-unreferenced dup records (whole-db
scan confirmed zero other referents before retiring). Terminal untouched.

**(b) Lillued - FIX (terminal-only, empty-husk retired).** The head's soul (`lilluedchild_soul`)
grants literally nothing - `itemSkillName`/`augmentSkillName1`/`2` all unset on every tier, no Text
tag. DETACH + RETIRE the 3 husk records; the terminal's real soul (`lillued_soul`, `summon_lillued`
+ 2 storm augments) untouched.

**(c) Charon 39/41/43 + Hades 54 - UNTOUCHED**, per Will's explicit ruling (intentional multi-form
rewards on base-game story bosses). Ground-truthed the exact record paths (`boss_charonform2_<N>`
under `xpack\...\02_charon\`; the LIVE Hades head is `drxcreatures\bloodwitch\boss_hades_54`,
chaining into `xpack\...\05_hades\boss_hadesform2_54` -> `form3_54`). `verify()` asserts a literal
byte-identical snapshot of all 9 records taken at apply()-time.

**Class invariant:** `legion_soul_stages`'s `distinct_multi` roster is re-derived fresh from the
FINAL db every run (never hardcoded), so once the two heads' Finger2 chances are zeroed the roster
**shrinks 6 -> 4** automatically - the exact "roster shrinks" behaviour the round-1 brief calls for.

**Verified:** dry-run replay - record-diff **0 added / 6 removed / 2 modified**; `verify()` PASS;
`legion_soul_stages.verify()` stays green post-fix (roster 6->4 confirmed both via this module's own
check and a standalone re-derivation); idempotency; 3 negative tests (re-armed Possessed Boar head,
mutated Charon record, mutated Hades record) all trip `verify()`.

---

## Item 5 - Carrionlord skill_quality/souls_quality reconciliation

**Ground truth:** `skill_quality.py` REASSIGNs carrionlord's off-theme `toxeus_flashpowder` grant to
its own identity-true Summon Carrion Crow (Track B), and previously set the controller to
`ON_ATTACK`. `souls_quality.py` (registry pos 13, after skill_quality's pos 4) already treats
carrionlord as a mod-introduced on-attack controller on a permanent `Skill_SpawnPet` ring - the
exact class the D3 crow-reset-bug fix targets for the other 7 families
(crowboar/glittertail/koroush/nkac/komara/melalos/oythroneus) - and strips it again: a documented
but confusing "later-wins" cross-module collision (S4b WARN). Read the golden arz directly:
`itemSkillAutoController=None` on all 3 tiers today - **the final assembled db was already
correct**; only the intermediate state and the code's own honesty about it were not.

**Resolution:** carrionlord is a mod REASSIGN target, not one of the 18 amgoz1 SV-ORIGINAL
on-attack swarm souls (which SV098 itself ships with the controller and stay untouched) - there is
no upstream design to defer to, so the class-wide manual-cast convention applies cleanly, same as
its 7 siblings. `skill_quality.py` now sets `controller=None` directly at the REASSIGN site
(`tagSoulName49`) instead of `ON_ATTACK` - both modules agree at the source, no collision, no S4b
WARN. Updated `souls_quality.py`'s docstring + the `_SUMMON_CONTROLLER_WAIVER` comment to match
(carrionlord was never added to the waiver - confirmed a genuine bug, not a design exception).

**Verified:** re-ran `skill_quality.apply()` then `souls_quality.apply()` against the golden arz -
the 3 carrionlord soul records are **byte-identical** to their golden (already-final) state;
`souls_quality`'s roster-derived sweep finds nothing left to remove for this ring (harmless no-op,
confirming zero functional/output change); `souls_quality.verify()`'s roster-wide manual-cast law
still passes.

---

## Combined verification (all 4 DB-authoring modules together, REGISTRY order)

Ran `svaera_sets` -> `turtleshell_relics` -> `toxeus_legendary_stalker` -> `double_soul_rulings`
together against a single golden-arz load (item 5 is code-only, proven separately above; it needs
no combined record-diff).

- **Aggregate record-diff vs golden:** **+16 / -6 / ~21** (exactly the sum of the four items' own
  diffs - 5+9+2+0 added, 6 removed from item 4, 13+6+0+2 modified).
- **Every module's own `verify()`:** PASS.
- **Monolith spawn-eligibility gate** (`_verify_mod_spawn_proxies_eligible`) over the combined db:
  PASS (17 mod-authored spawn proxies).
- **`legion_soul_stages.verify()`** (independent re-check over the combined db): PASS, roster at 4.
- **New-tag completeness** (validate_tags-equivalent, in-memory): all 7 new tags
  (`tagSVCRevelersRuse`/`DESC`, `tagSetName049/051/052/053/058`) have non-empty text.
- **`validate_soul_augments` (souls contract):** written the combined db to a temp arz and ran the
  real validator against it - **exit 0, clean**.
- **`validate_summon_pets` (summons contract):** exit 1, but the `[BROKEN]` entry list is **byte-
  identical** to a baseline run of the same validator against the pristine, untouched golden arz
  (diffed the sorted header-line sets - zero difference). All 210 broken entries are pre-existing
  baseline noise (matches the repo's established "contracts GATE PASS, N pre-existing P2" pattern),
  completely unrelated to this wave's 4 modules - **zero new regressions**.

`py_compile` clean on every touched file; `_check_registry.py` OK (20 modules, order hash
`fc4c632fd31521e423c5e6c3763a5eb2f2db017a810bf71f7e22d85039cd1956` after items 1-4; item 5 does not
change REGISTRY membership).

---

## Gates summary

| gate | result |
|---|---|
| sets_relinked_or_stopped | RE-LINKED (not stopped - git-blame gate cleared, no intentional strip found) |
| relics | Reveler's Ruse authored; Dune Fiend confirmed already-satisfied (guard added, nothing new) |
| stalker_placed | DB (pool1/poolEpic1 empty, poolLegendary1 set) + map (INJECT_SPECS, dry-run injected, navmesh byte-identical) |
| double_souls | Possessed Boar + Lillued fixed terminal-only; Charon x3 + Hades UNTOUCHED (byte-identical snapshot) |
| carrionlord | RECONCILED - both modules now agree at the source (manual-cast), zero collision, byte-identical output |
| dry_run_diff | +16 / -6 / ~21 records (combined), all four modules' diffs individually re-verified |
| contracts | souls: PASS (exit 0); summons: pre-existing-only (zero new BROKEN entries vs golden baseline); spawn-eligibility: PASS; legion_soul_stages: PASS (roster 6->4) |

Not built/deployed this pass - rides the next integration build.
