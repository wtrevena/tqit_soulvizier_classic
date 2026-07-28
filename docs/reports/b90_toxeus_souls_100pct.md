# b90 - TOXEUS CHAMPION SOULS -> 100% DROP (R-48), round 1

**Branch** `feat/toxeus-souls-100` (worktree `.claude/worktrees/toxeus-souls-100`, base `main` @ `d1ec943` = build49)
**Date** 2026-07-27
**Scope** DB only (arz + Text). NO map rebuild; `Levels.arc` / `Quests.arc` untouched and hash-proven.

---

## 1. THE RULING

Will, 2026-07-27, verbatim:

> "increase the drop rate for the souls of toxeus the murderer, enslaver of souls and toxeus the
> murderer, devourer of blood to 100%"

Appended to `docs/WILL_RULINGS.md` as **R-48** (Souls & items section), status IMPLEMENTED b90.

### Ledger reconciliation (standing law 1)

| Ruling | Domain | Action taken |
|---|---|---|
| **R-42** "soul drop rates: random 50 / placed 66 / boss 25" | the whole roster | Marked **PARTIALLY SUPERSEDED by R-48 for these two records ONLY**. Every other record's rate stands and is proven unchanged in the record-diff (section 4). |
| **R-47** generic apex orb for custom Boss encounters | Blood Toxeus / Enslaver loot | Untouched - this lane changes only `chanceToEquipFinger2`, no `lootMisc*` / orb slot. |
| **R-5 / R-6 / R-7 / R-11 / R-12** Toxeus champion kits, black poison, identity | same two monster records | Untouched - no skill, mesh, texture, race, FX or pet field is written. |
| **R-13** [renumbered **R-19** on 2026-07-28 by the `fix/debt-docs` ledger-hygiene pass; the live R-13 is the Rite on-kill drop] "retire the one we are adding and just update the 15% one to 33%" | Blood-Toxeus SPAWN chance | **Not the same axis.** `chanceToRun` (33% corridor ambush spawn) is untouched; R-48 raises the SOUL DROP roll once the champion is actually killed. |
| Yeti Common/Champion lesson (CLAUDE.md) | `wire_souls_to_monsters` Hero/Boss/Quest gate | **Gate NOT modified.** Both champions are `monsterClassification=Boss`, so the gate never applied to them; no Common/Champion is re-enabled. Post-build proof: the testing-forcer survival check still reports **428 gated records stay 0**. |

No other ledger entry touches these two souls' drop rates.

---

## 2. RECON - what actually drops these souls

The drop is a plain equipped-ring roll on the monster record; there is **no pool or loot-table
indirection** for either champion (`lootFinger2Item1` names the three soul tiers directly).

| Champion | Monster record | Soul family | Class | Rate BEFORE | Set by |
|---|---|---|---|---|---|
| Toxeus the Murderer, **Enslaver of Souls** | `records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr` | `records\item\equipmentring\soul\svc_uber\enslaver_soul_{n,e,l}.dbr` | Boss | **66.0** | `apply_svc_patches._create_enslaver` -> `_create_soul(..., drop_rate=66.0)` -> routed through `_soul_release_rate()` -> PLACED_UBER 66 |
| Toxeus the Murderer, **Devourer of Blood** | `records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr` | `records\item\equipmentring\soul\svc_uber\blood_toxeus_soul_{n,e,l}.dbr` | Boss | **25.0** | `apply_svc_patches:10016` `_create_soul(db, 'blood_toxeus', ..., _BT_MONSTER, 25.0)` - 25 is not 66 so it passes the classifier straight through (module-owned superboss cap) |

Sibling `um_enslaver_marauder_99` (Champion) carries no soul loot and sits at 0 - unchanged.
The corridor ambush and the deep waterfall boss share the SAME `um_bloodtoxeus_99` record, so both
encounters get 100% (matches Will's wording, which names the champion, not one spawn site).

### The existing machinery, and why it could not carry the ruling

* `apply_svc_patches._force_100_pct_soul_drops` - the TESTING forcer. It runs **only** when the build
  is in testing mode (`SVC_TESTING_DROPS=1` / `SVC_RELEASE_DROPS=0`). The shipped build is RELEASE
  (`SVC_RELEASE_DROPS=1`), where it never runs. It also deliberately gates on `chance > 0` (the yeti
  Common/Champion fix) - correct, and left exactly as-is.
* `build_svc_database.wire_souls_to_monsters` + `soul_drop_rate()` - the Hero/Boss/Quest gate and
  the RANDOM-50 / PLACED-66 / BOSS-25 split. **Deliberately NOT modified**: it has no 100 branch and
  any edit there would move other records. R-48 is a two-record carve-out, so it is expressed as a
  carve-out.

---

## 3. IMPLEMENTATION

**New registry module `tools/patches/toxeus_souls_100.py`**, registered in `tools/patches/__init__.py`
**last among content modules** (immediately before `visuals`, which writes nothing), so it is the
ratified final registry writer of `chanceToEquipFinger2` on the two champions - after `toxeus_suite`,
`toxeus_champion_kits`, `black_poison`, `toxeus_endofallthings`, `legion_soul_stages` and
`double_soul_rulings`. Registry order hash `9bca0f20fd87c7dade8562c27914f73372e38aab13cb4c08dd93fba44d5624fe`
(33 modules); `tools/patches/_check_registry.py` OK.

`apply(db, tags)`:
1. Fails loud if either record is missing.
2. Fails loud if `lootFinger2Item1` is empty, is not souls-only, or does not carry the expected soul
   family (`enslaver_soul_` / `blood_toxeus_soul_`) - so a 100% roll can never guarantee an empty
   slot or a foreign reward.
3. Writes the standard soul-wiring triple with explicit dtypes:
   `chanceToEquipFinger2=100.0` (FLOAT), `chanceToEquipFinger2Item1=100` (INT), `dropItems=1` (INT).
4. **SCOPE PROOF (roster-wide, in-build):** snapshots `chanceToEquipFinger2` on every creature record
   before and after its own writes and `SystemExit`s unless the changed set is exactly the two
   targets. Build log: `scope proof: exactly 2/3629 creature records' chanceToEquipFinger2 changed`.

`verify(db, tags)` (step-4 hook, runs over the FINAL merged db after the whole gate battery incl. the
testing forcer): fails the build loud if either champion is not at exactly 100.0, has lost its soul
family, or has `dropItems != 1` / `chanceToEquipFinger2Item1 != 100`.

Deterministic (no wall-clock/random/hash-ordered iteration), idempotent (a re-run writes the same
three constants), and mode-independent (holds under `SVC_RELEASE_DROPS=1`, which is what ships).

**Gate ground-truth updated** - `tools/verify_soul_drop_rates.py`:
* `_KNOWN_EXCEPTIONS`: `um_bloodtoxeus_99` 25.0 -> **100.0**; new `um_toxeus_enslaver_99` -> **100.0**;
  both with the R-48 rationale. This covers BOTH the LAST-WRITER check and the intended-diff-vs-golden
  check.
* spot tests `EXPECT`: `um_toxeus_enslaver_99` ('PLACED', 66.0 -> **100.0**), `um_bloodtoxeus_99`
  (None, 25.0 -> **100.0**).
The shared classifier `soul_drop_rate()` is untouched, so it still says 66/25 and both records are
carried as documented, visible waivers rather than silently absorbed.

---

## 4. BUILD + RECORD-DIFF

Build: `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 py tools/build_svc_database.py <098i> <0.9> <041>
work/SoulvizierClassic/Database/SoulvizierClassic.arz <TQAE base>` - exit 0, every fail-loud gate green
(soul-leak, soul-augment, supra-ref, tags, spawn-eligibility, A7 golden 84 waived/0 other, A9
render-chain, b77 unlock-alignment, F2 summons contract).

Text: `py tools/build_text_arc.py <098i Text_EN.arc> work/.../Resources/Text.arc
work/SoulvizierClassic/Database/uber_soul_tags.txt` - built from the **BUILD-EMITTED** manifest
(md5 `49b6d85ba15236aa5df60f610e3a7bf0`, written by this same arz build), never a `local/` copy.

### Record-diff vs baseline `local/baseline_build47.arz` (md5 `5a3c016b...` = the arz that was staged in `work/` AND deployed on DEV)

```
ADDED   (0)
REMOVED (0)
CHANGED (2):
  records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr
      chanceToEquipFinger2:  (66.0,)  ->  (100.0,)
  records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr
      chanceToEquipFinger2:  (25.0,)  ->  (100.0,)
TOTAL DIFFERING RECORDS: 2
```

**2 records, 1 field each, 0 added, 0 removed.** Because the baseline was produced by an earlier run
of the same pipeline and the rebuild reproduces it exactly apart from these two fields, this diff
doubles as a determinism + provenance proof of the whole DB build.

### Hashes

| Artifact | md5 |
|---|---|
| `work/.../Database/SoulvizierClassic.arz` (NEW) | `c1a8fa2aee5e6eb88b641b28d7dc6ae4` |
| `work/.../Resources/Text.arc` (rebuilt, unchanged bytes - no tag changed) | `fcca49277b9d31ed451e4a6843898843` |
| `work/.../Database/uber_soul_tags.txt` (build-emitted) | `49b6d85ba15236aa5df60f610e3a7bf0` |
| baseline arz (`local/baseline_build47.arz`, pre-change) | `5a3c016baae8f136b8b801ea871b71ba` |

### NO-MAP proof - `Levels.arc` / `Quests.arc` byte-identical before vs after

| File | BEFORE | AFTER | verdict |
|---|---|---|---|
| `work/SoulvizierClassic/Resources/Levels.arc` | `17bed65ff9299a3398131025b4bfcfb3` | `17bed65ff9299a3398131025b4bfcfb3` | IDENTICAL |
| `work/SoulvizierClassic/Resources/Quests.arc` | `5e664c7b190965fd69f6ff15d77d85e4` | `5e664c7b190965fd69f6ff15d77d85e4` | IDENTICAL |

---

## 5. VERIFY BATTERY

| Gate | Result |
|---|---|
| `tools/validate_tags.py` (arz + Text.arc + uber_soul_tags + mod_authored_tags) | **PASS** - 356/356 referenced mod tags present, 417/417 authoritative tags present (2 pre-existing base/SV `tagNewMonster*` WARNs, non-blocking, unchanged) |
| `tools/verify_soul_drop_rates.py --gate` | **PASS** (exit 0). Spot tests: `um_toxeus_enslaver_99` arz=100.0 (want 100), `um_bloodtoxeus_99` arz=100.0 (want 100); every other named record unchanged (camelbane/morth/crowboar/xix/frost/junshan/grom/bloodwing 50, legion_28 0, legion_28c 66, vashkarr/broodmother/hadesmarshal/machae_45 66, tantalus 0, toxeus_hunt 25). Intended-diff-vs-golden (build40): 380 deltas, 380 intended/documented, **0 UNINTENDED**. Testing-forcer survival: 850 enabled -> 100, **428 gated stay 0**. Planted-stomp negative test CAUGHT. |
| Registry verify hooks (in-build, final merged arz) | **`[toxeus_souls_100] verify OK: both Toxeus champions at 100% soul drop with their soul families + dropItems intact`** (24 module verifies ran, all green) |
| `tools/patches/_check_registry.py` | **OK** - 33 modules |
| Contracts battery `--only souls,summons,resources` | **0 P0.** souls lane **0 P0 / 0 P1 / 0 P2**; summons lane **0 P0 / 0 P1** (112 P2). resources lane 1252 P1 / 3540 P2 - **100% PRE-EXISTING**: the identical command over the pre-change baseline arz yields the byte-identical violation set (4904 both, **0 only-in-built, 0 only-in-baseline**). See DEBT below. |

---

## 6. DEPLOY (DEV)

Target `C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV`.
Deployed the **coupled arz + Text pair only**. Pre-deploy backup:
`local/db_backups/SoulvizierClassicDEV_pre-b90_5a3c016b.arz`.

| DEV file | md5 after deploy | proof |
|---|---|---|
| `Database/SoulvizierClassicDEV.arz` | `c1a8fa2aee5e6eb88b641b28d7dc6ae4` | **== built arz** |
| `Resources/Text.arc` | `fcca49277b9d31ed451e4a6843898843` | **== built Text.arc** |
| `Resources/Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | **UNTOUCHED** (still the build49 map, as required) |
| `Resources/Quests.arc` | `5e664c7b190965fd69f6ff15d77d85e4` | **UNTOUCHED** |

In-arz re-probe of the DEPLOYED `SoulvizierClassicDEV.arz`:
`um_toxeus_enslaver_99` cls=Boss chance=**100.0** (3 enslaver soul tiers);
`um_bloodtoxeus_99` cls=Boss chance=**100.0** (3 blood_toxeus soul tiers);
`um_enslaver_marauder_99` cls=Champion chance=**0.0** (unchanged, no soul).

TQ was not running during the deploy (Steam client only). **Per the standing rule, Will must kill TQ +
Steam and restart before testing**, then verify the mod loads `SoulvizierClassicDEV`.

---

## 7. DEBT REGISTER (standing law 4)

1. **`contracts_resources` 1252 P1 (`C-RES-DBR-1` 768, `C-RES-ASSET-1` 484) - PRE-EXISTING, NOT this
   lane.** Byte-identical violation set on the pre-change baseline arz (0 delta). BACKLOG line ~1664
   records this lane at **0 P0 / 1 P1** at an earlier date, so it regressed by ~1251 P1 at some point
   BEFORE b90. Strong suspicion: environmental, not content - see item 2. **Needs its own triage lane.**
2. **`upstream/` and `reference_mods/` were EMPTY on this machine** (the three source archives are
   still in `third_party/`, and `CustomMaps\SoulvizierClassic` - the canonical, non-DEV deploy - is
   also gone). The DB build cannot run without `upstream/`, so this lane re-extracted **only the four
   files the build needs** from `third_party/` (098i `Database/database.arz` md5 `11773cdc…` +
   `Resources/Text_EN.arc` md5 `29505ac2…`; 0.9 `Database/database.arz` md5 `b31951df…`; 0.41
   `Database/database.arz` md5 `056d6f4e…`). Correctness is proven by the record-diff: the rebuild
   reproduced `baseline_build47.arz` exactly apart from the 2 intended fields, so these are provably
   the right inputs. **Someone should decide whether the full `upstream/` + `reference_mods/` +
   canonical `CustomMaps\SoulvizierClassic` trees get restored** (map/Workshop work will need them).
3. **In-game confirmation outstanding (launch-gated):** the 100% drop can only be confirmed by Will
   killing a Devourer and an Enslaver on DEV after a full Steam restart. Nothing in this lane can
   prove the in-game roll.
4. **Not in scope, flagged:** the `um_toxeus_hunt_99` Legendary Stalker (a third Toxeus champion) is
   still at 25%. Will's ruling names only the Enslaver and the Devourer, so it was deliberately left
   alone - raise a follow-up if he wants the Stalker at 100 too.
