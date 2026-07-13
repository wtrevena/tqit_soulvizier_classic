# b38 - ENSLAVER SPAWN V2 (BL-ENSLAVER-SPAWNS-V2)

Branch `feat/b38-enslaver-v2` (base d6ed889). DB/registry lane. No heavy build.
Report is the deliverable; the b38 integration wave consolidates BACKLOG entries.

## Will's order (2026-07-13, verbatim)
> "toxeus the murderer, enslaver of souls he is spawning like 2-3 of him at a time and
> just playing through act 1 to medusa i ran into him like 6 times. We need to drastically
> lower the spawn rate so we see him about once an act so divide the current spawn rate by
> 10 and then make it so he only spawns once max with a group of guys so you cant need to
> fight two or more of him at the same time."

Two requirements: **(1)** divide spawn rate by 10 (-> ~once per act); **(2)** never two or
more Enslavers at the same time. Target monster = `um_toxeus_enslaver_99` (the roaming
"Enslaver of Souls" black Skeleton Lord). The **Devourer** (`um_bloodtoxeus_99`), the
**static blood-cave warband**, and the **Endless Hunt** (`um_toxeus_hunt_99`, Hades stalker)
are OUT OF SCOPE and untouched.

## Root-cause analysis (enumerated from the SHIPPED build36a arz, md5 63ca7cf8)

The Enslaver reaches the world through the monolith's **roaming sweep**
(`_sweep_inject_roaming_rare`), which appends him as a plain weight-1 MAIN member to every
eligible hostile trash pool. Enumeration of the build36a arz (Will's live build):

| fact | build36a value |
|---|---|
| pools carrying the Enslaver | **1226** (greek 363, orient 292, egypt 224, hades 345, + 2 whitelisted drxmap yard/warband) |
| per-draw p_slot | 1/2401 (worst/most-common) .. 1/66001 |
| pools with spawnMax >= 3 (packs) | ~1050 |
| **Enslaver slots carrying a per-slot `limitN` cap** | **0 (the defect)** |

Mechanism findings (each PROVEN from the records, not assumed):

1. **Multi-pool proxies pick ONE pool, not all.** 1354 proxies list 2+ Enslaver pools, but the
   proxy's `weight1..N` are a *weighted pool CHOICE* (e.g. `ag_beastmen_satyr_02n`:
   weight1/2/3 = 20/30/50 -> 20%/30%/50% pick of pool1/2/3). So a single spawn point fires
   exactly ONE pool. Multi-pool proxies are therefore **not** a double source.
2. **Pool MAIN draws are independent WITH REPLACEMENT.** PROVEN: 170 vanilla pools spawn more
   mains than they have distinct name slots (e.g. `eurynomus_01_general01`: spawnMin=3, 2
   slots). So a single pack pool with spawnMax 3-8 CAN draw the same weight-1 member 2+ times
   in one trigger.
3. **The missing guard.** Vanilla NEVER lets a rare member duplicate in a pack: every rare
   hero sprinkled into a trash pool carries **`limitN = 1`** - a per-slot MAX-count cap
   (PROVEN by 2657 champion + 454 main vanilla slots; e.g. `as_venomancer_22` at weight 2 /
   `limit6 = 1` inside a spawnMax=3 jackalman pack; `spiderblackwidow01` at `limit1 = 1`).
   `limitN==1` correlates with LOW weight (median 4) = the rare-hero idiom. The build36a sweep
   added the Enslaver at weight 1 **with no `limitN`** -> the engine may draw him twice in one
   pack. **This is the structural bug behind "2-3 of him at a time."**
4. **"6 times to Medusa" is frequency-driven clustering.** At ~6 Enslavers per act spread over
   the map, two of them landing in the same on-screen field is a birthday-paradox event
   (~15-20% per act with ~50-75 fields) - which is the *dominant* "at a time" source; the
   per-trigger pack-double (finding 2/3) is the rarer, literally-overlapping case. Both are
   fixed below.

## The fix (monolith `tools/apply_svc_patches.py`, registry contract)

Two independent knobs, both in the sweep the registry contract already owns:

**(1) Frequency /10 vs build36a.** `_EN_SWEEP_K` 300 -> **600**. Will plays build36a (K=60);
the b37 lane's K=300 (5x) is UNSHIPPED, so "current" = build36a and the 10x is measured from
there: 60 -> 600. Per-draw p = 1/(K*W+1), so every pool's p scales by (60W+1)/(600W+1) ~=
**0.1000** (W = original main-weight-total). `_EN_SWEEP_CEIL` and `_EN_SWEEP_MAX_P` are
computed from K, so they follow to 24000 / (1/24000). The eligibility floor keys off ORIGINAL
W (not K), so **breadth is identical** (same 1224 pools) - the rate drops cleanly without
changing the roaming character.

**(2) Structural no-double.** When appending the Enslaver, also set `limit{slot} = 1`
(`_EN_SWEEP_SLOT_LIMIT`). This is the vanilla rare-hero cap: **at most ONE Enslaver spawns per
pool per trigger, structurally**, at any party size, regardless of spawnMax / mains /
replacement. Because a proxy fires exactly one pool (finding 1), the per-pool cap is also the
**per-spawn-point cap: no single spawn point can ever surface 2 Enslavers.**

**Gate.** `_verify_roaming_sweep` now FAILS LOUD unless every swept pool carries the Enslaver
at weight 1 **AND `limitN == 1`** AND p_slot <= 1/24000. Proven non-vacuous (negative test
below). The warband set-piece (`q_enslaver_warband`, exactly 1 leader + 4 marauders via
championMax) and the TESTHUB yard pool stay whitelisted and untouched; the roaming Enslaver
still raises his marauder warband in-fight (`svc_enslaver_summonmarauders`) - his "group of
guys" is unchanged.

## Dry-run verification (no heavy build; replay against a copy of build36a)

`scratchpad/replay_enslaver_v2.py`: load build36a arz -> **un-sweep** it (recover pre-sweep
pools: main weights /60 [exact, 0 non-divisible], drop the Enslaver slot) -> run the WORKTREE
`_sweep_inject_roaming_rare` + `_verify_roaming_sweep` -> enumerate.

```
un-swept 1224 pools; non-divisible-by-60 main weights: 0; residual enslaver: 0
V2 sweep touched 1224 pools (breadth preserved)
V2 _verify_roaming_sweep GATE PASSED
AFTER (V2): enslaver slots MISSING limit=1: 0
V2 per-draw p_slot: max 1/24001 (<= 1/24000 ceiling), min 1/660001
per-pool freq ratio V2/build36a: median/min/max = 0.1000 (exactly /10)
EXPOSURE-weighted system frequency ratio = 0.1000  (target 0.10)
region ratios (egypt/greek/orient/hades) = 0.1000 each
WORST-CASE per-trigger DOUBLE prob:  build36a 4.86e-06 (~1 in 205,886)  ->  V2 = 0 (structural)
Anchor: Will ~6 in Act1 -> V2 ~0.60 per Act 1 (his "6" was only to Medusa = partial Act 1,
        so a full act lands ~0.8-1.0 = "about once an act")
```

Negative test (`scratchpad/negtest_enslaver_gate.py`) - the gate MUST reject each defect:
```
[missing-limit=1]   gate correctly FAILED LOUD
[p_slot too common] gate correctly FAILED LOUD
RESULT: PASS (gate is non-vacuous)
```

Fast gates: `py_compile` OK; `tools/patches/_check_registry.py` OK (9 modules).

### Worst-case proof (never two at a time)
- **Same spawn point:** `limitN=1` caps the Enslaver at 1 per pool, and a proxy fires one pool
  -> **structurally 0** chance of 2 from one spawn point (was ~1/206k per trigger in build36a).
- **Two independent spawn points visible together:** the engine has **no global monster-count
  cap**, so this is not structurally zero for any roaming encounter. It scales with
  (encounters/act)^2, and the /10 frequency cut makes it ~100x rarer than build36a (from a
  ~15-20% per-act chance down to ~0.2% per act ~= once per several hundred acts) - i.e.
  effectively never. If Will wants a *hard* zero here, the only engine-supported route is to
  drop the roaming sweep entirely and deliver the Enslaver ONLY via a bounded set of dedicated
  warband proxies placed >=1 field apart by the map lane (each = exactly 1 leader). That is a
  design pivot (fixed set-pieces, loses "roam anywhere") and a map-lane dependency; flagged for
  Will's call, not done here.

## Coupling checked: the Endless Hunt stalker (toxeus_suite) is SAFE
`toxeus_suite._sweep_inject_legendary_stalker` reads `_LS_MAX_P = asp._EN_SWEEP_MAX_P`, now
1/24000. It runs AFTER the enslaver sweep, which inflates the (shared) Hades pools to
wtotal >= 24001 (600*W+1, W>=40); the stalker's inject floor (`wtotal >= 2399`) still passes
and its weight-1 append gives p <= 1/24002 <= 1/24000, so its own fail-loud gate still passes.
The stalker's eligible set is exactly the proxieshades subset of the enslaver's swept set
(identical filters), so it only ever touches enslaver-inflated pools. Verified: `toxeus_suite`
py_compiles; `_LS_MAX_P` resolves to 1/24000. **No stalker edit needed.**

### Follow-up (out of scope, flagged)
The **Endless Hunt** stalker has the *same* latent per-trigger-duplicate defect (swept into
Hades pools at weight 1 with no `limitN`). It is Hades-only, rarer, and UNSHIPPED (b37), and
Will did not report it, so it is left untouched here. Recommended one-line follow-up: add
`db.set_field(n, 'limit%d' % free, 1, I)` to `_sweep_inject_legendary_stalker` and assert it in
`_verify_legendary_stalker_sweep`, mirroring this fix.

## Files changed
- `tools/apply_svc_patches.py` - `_EN_SWEEP_K` 300->600, new `_EN_SWEEP_SLOT_LIMIT=1`;
  `_sweep_inject_roaming_rare` sets `limit{slot}=1`; `_verify_roaming_sweep` asserts it
  fail-loud; refreshed comments/docstrings (x60/1-in-12000 -> x600/1-in-24000 + limit=1).
- Scratchpad harnesses (analysis only, not shipped): `replay_enslaver_v2.py`,
  `negtest_enslaver_gate.py`, `enum_enslaver_baseline.py`, `enum_spawn_shapes.py`,
  `probe_limit_semantics.py`, `confirm_limit_template.py`.

## What Will will see
- The Enslaver appears about **once per act** (down from ~6), keeping his roaming character.
- **Never two on the same spawn** (structural). Two independent Enslavers close enough to fight
  together is now a once-in-hundreds-of-acts event (effectively never).
- He still leads his shadow-marauder warband when he appears.
