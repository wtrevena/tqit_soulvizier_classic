# b56 - Legion soul-stages: one soul per death-transform encounter

**Branch:** `feat/legion-soul-stages`  **Module:** `tools/patches/legion_soul_stages.py`
**Baseline (golden):** build40 arz `b33c5a447f3a8ca652c14f78d4ad1dd4`
(`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, 51,029 records).

## The bug (Will, 2026-07-14)

> "the hero monster legion is dropping souls at multiple stages of his life as he
> dies and gets bigger."

## RCA - the Legion stage chain

Legion is a **four-stage death-transform chain** linked by `actorToSpawnOnDeath`
(each stage on death spawns the next, bigger form):

```
um_legion_28  ->  um_legion_28a  ->  um_legion_28b  ->  um_legion_28c   (TERMINAL)
  Hero L14         Hero L14           Hero L14           Hero L14
  records\creature\monster\eurynomus\um_legion_28*.dbr
```

Every one of the four stages is its own monster record and **each carries the
identical soul drop**: `chanceToEquipFinger2 = 66.0` + `lootFinger2Item1 =
[legion_soul_n, _e, _l]`. So one Legion encounter yields up to **four copies of
`legion_soul`** (tag `tagSoulName527`). The three non-terminal stages point their
_n tier at the broken Dropbox `legion_soul_n (amgoz-qosmio's conflicted copy
2013-08-07).dbr`; only the terminal `um_legion_28c` uses the clean
`legion_soul_n.dbr`.

**Root cause:** `build_svc_database.wire_souls_to_monsters` wires a soul onto
every Hero/Boss/Quest-ranked monster independently and does not know the four
`um_legion_28*` records are one growing monster, so it arms all four. (These are
SV-original upstream records; the multi-arm is our wiring hitting each Hero
stage.) This contradicts the established uber-boss law - Tantalus /
Charon-the-Unferried / Mnemophage / Golden Bough all put the soul on the FINAL
form only and clear the inherited Finger2 soul on every non-terminal form.

## The fix

New registry module `tools/patches/legion_soul_stages.py` (after `boss_skill_fix`,
before the no-op `visuals`, which stays last). Algorithm, applied over the FINAL
assembled db:

> For each soul item dropped by 2+ stages where one stage is forward-reachable
> from another via `actorToSpawnOnDeath`, keep the drop on the **deepest
> (terminal-most)** stage and set `chanceToEquipFinger2 = 0` on every shallower
> stage (loot refs left intact and inert - the `_apply_aphiastas_finger2_zero`
> house pattern; dtype-safe, no explicit dtype on the existing FLOAT field).

This is **orphan-proof by construction**: a stage is zeroed only when the SAME
soul is still dropped by a deeper stage of its own chain, so the soul stays
obtainable exactly once.

**Legion result:** keep `um_legion_28c` (drops `legion_soul` @66 release / 100
testing); zero `um_legion_28`, `um_legion_28a`, `um_legion_28b`. One soul per
encounter, and the surviving drop uses the clean (non-conflicted-copy) soul path.

**Timing:** the module runs in `run_registry` (after all soul wiring:
`wire_souls_to_monsters` + `create_uber_souls` + `apply_all_extended_patches`)
and BEFORE the drop-rate forcer in `run_registry_gates`. The forcer only boosts
records with `chance > 0` (testing 100%) or leaves rates untouched (release
66/25), so a stage set to 0 stays 0 in BOTH build modes. `verify()` re-checks the
invariant in the post-finalization phase.

`verify(db, tags)` (fail-loud): asserts no death-transform chain drops the SAME
soul from more than one stage. Negative test (in the probe): re-arming
`um_legion_28b` to drop `legion_soul` trips `verify()` with `SystemExit`.

## Class sweep - every same-defect chain in the roster

Enumerated **every** `actorToSpawnOnDeath` chain with 2+ soul-bearing stages
(probe: `tools/patches/_probe_legion_soul_stages.py`). Seven chains carry >=2
soul drops. They split into two classes:

### (A) SAME soul dropped by multiple stages = the Legion defect - FIXED

| chain | stages dropping the soul | fix |
|---|---|---|
| **Legion** | `um_legion_28 / _28a / _28b / _28c` all drop `legion_soul` | keep `_28c`, zero the other 3 |

Legion is the **only** chain where one soul item is dropped by 2+ stages of a
single encounter. Fixed by this module.

### (B) DISTINCT souls per stage - NOT auto-fixed (design ruling required)

Six chains drop **two genuinely different souls** per encounter (head = an
`svc_uber` soul, terminal = a different base-path soul, with different granted
skills). Reducing these to one soul means deciding which of two real collectibles
is canonical and **orphaning the other** - the inverse defect this task guards
against, and for the base-game story bosses (Charon, Hades) a content change. So
they are **reported loud, not auto-zeroed**. Each is a candidate follow-up
pending Will's ruling:

| chain | head soul (skill) | terminal soul (skill) | recommendation |
|---|---|---|---|
| `um_possessedboar -> _spirit` | `possessedboar_soul` (thunderballnova) | `possesedboar_soul` (drxstormsurge) | terminal-only; retire svc_uber dup |
| `boss_hades_54 -> form2 -> form3_54` | `sp_hades_soul` (hades_star) | `hades_soul` (hades_star) | near-dup; terminal-only |
| `lillued -> lillued_big` | `lilluedchild_soul` (**empty husk, no grant**) | `lillued_soul` (summon_lillued) | terminal-only; child husk is worthless - safest to drop |
| `boss_charon_39 -> form2_39` | `boss_charon_soul` (talos_flamethrower) | `charon_soul` (charon_buffself) | terminal-only; retire svc_uber dup |
| `boss_charon_41 -> form2_41` | `boss_charon_soul` | `charon_soul` | same |
| `boss_charon_43 -> form2_43` | `boss_charon_soul` | `charon_soul` | same |

Note the parallel-difficulty variants (`boss_hadesform3_50/52/54` all drop
`hades_soul`; `boss_charon_39/41/43` all drop `boss_charon_soul`) are NOT one
chain - they are separate encounters at Normal/Epic/Legendary and are correctly
left alone (the module only reduces a soul dropped by two stages that are
forward-reachable from each other).

### Inverse defect (unobtainable soul)

**0 found.** No Hero/Boss/Quest death-transform head has a chain whose stages all
drop nothing. The Legion fix cannot create one (the terminal keeps the drop).

## Verification (dry-run replay vs golden `b33c5a44`, no heavy build)

- **Record-level diff:** exactly **3** records change - `um_legion_28 / _28a /
  _28b` `chanceToEquipFinger2` 66.0 -> 0.0. Terminal `um_legion_28c` unchanged
  (66, still drops `legion_soul`). All 6 distinct-soul chains byte-identical.
  Written arz = 51,029 records (0 added/removed).
- **`verify()`**: PASS (no chain drops the same soul from >1 stage).
- **Idempotent:** second `apply()` changes 0 records.
- **Negative test:** re-arming `um_legion_28b` -> `verify()` raises `SystemExit`.
- **`validate_soul_augments`**: golden PASS == post-apply PASS (2468 soul records,
  4938 skill refs, 1390 granted-skill souls, 0 dangling, 0 inactive).
- **contracts souls** (`run_contracts.py --only souls`): golden **0 P0/0 P1/0 P2**
  == post-apply **0 P0/0 P1/0 P2**, GATE PASS.
- **`py -m py_compile`** + **`_check_registry.py`**: OK (14 modules, order
  `fabf2d33cc81`).

## Integration notes

- One-line `REGISTRY` addition (`legion_soul_stages`, before `visuals`) - merges
  cleanly; other lanes touch different modules. New module file only; no edit to
  `apply_svc_patches.py` or `souls_quality.py` (avoids the souls-quality lane
  merge conflict per the brief).
- Rides the next integration build. In a full RELEASE build the arz record-diff
  vs build40 golden should be **exactly these 3 records** (each: Finger2 chance
  66 -> 0), 0 added/removed.
