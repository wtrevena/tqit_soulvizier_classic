# Multiplayer Compatibility - Soulvizier Classic (TQAE)

> Audit + fixes for playing the mod in **TQAE multiplayer co-op** (Will + a friend).
> Scope of the original pass (M1-M3): **database (`.arz`) lane only**; the map/navmesh/quest lane was
> owned by a parallel workstream and NOT touched there. **§M4 (added 2026-07-14) extends this doc to
> the build37 Toxeus Encounter Suite (#32), which spans BOTH lanes.** Last updated: 2026-07-14
> (M4 added; arz hash/size below still reflect the build27 MP-fix pass, 2026-07-07/08).

> **⚠️ CURRENT ARZ (build27, verified on disk 2026-07-08):**
> `work/SoulvizierClassic/Database/SoulvizierClassic.arz` and the deployed
> `CustomMaps\SoulvizierClassic\Database\SoulvizierClassic.arz` are now
> **54,529,030 bytes, MD5 `7C6E209988F0CE815BAF35F058B6A0A8`, SHA-256
> `5014f1903aa4163adaeb8c35fd71ca8fe36db2a7293aa874932660619b600c8f`**.
> The `efbf2471…` SHA-256 / `54,526,916 B` figures throughout the determinism proofs below are the
> **earlier MP-fix-only baseline** (point-in-time, when this pass was written) and are **SUPERSEDED**:
> later content waves (the Blood Toxeus spawn fix, the born-open portal swap, mastery/supra repairs)
> landed on top and advanced the hash/size. The MP spawn-scaling fix analyzed here **remains in the
> standing build pipeline** (`apply_svc_patches.py`), so every conclusion below still holds - only the
> exact bytes moved. The build is still deterministic (rebuild twice, MD5 matches). The 8 missing
> `Text.arc` tags flagged in §M3.1 are still open, tracked as `B-TEXT-TAGS-1` in `docs/BACKLOG.md`.

## TL;DR

- **The one known MP risk (SV's `RunEquation` spawn-scaling formulas) is REAL, and it is now FIXED in the database.** SV's monster-pool spawn/champion equations divided by `numberOfPlayers`; the AE engine's proxy-spawn equation evaluator rejects `/` (it is a narrower code path than the item-equation evaluator), logs `RunEquation load failure`, and silently falls back to base-game spawn density. In multiplayer this meant **fewer monsters/champions than SV intends**. All 44 offending equation values were rewritten to a `/`-free form the AE evaluator accepts. The `.arz` is deployed (and re-verified byte-identical in round 2 - no redeploy needed).
- **Spawn-fit accuracy (corrected):** the `/`-free replacement is a least-squares quadratic; it is **not** exact at any player count. True relative error vs SV intent is **~2.6–4.4% at single-player (np=1)** and **~3.3–5.3% at np=2** (the worst point), monotone through the 6-player range. Because the engine floors pool budgets to integer counts and the replacement never reduces single-player spawns, the in-game effect is negligible (usually ≤1 spawn). Details + the deliberate decision *not* to pin np=1 (pinning would worsen the np=2 co-op case) are in §M1.3.
- **One launch-gated unknown:** the replacement uses `numberOfPlayers * numberOfPlayers`, a quadratic term with **zero precedent in the base game** (proven: 0 self-multiplies across all 74,013 base records). Its parseability in the *narrow* spawn evaluator is confirmed only by a single game launch (check the log for a spawn `RunEquation load failure`; §M1.5). A proven **linear fallback** (`SVC_MP_SPAWN_LINEAR=1`, structurally identical to a real base-game spawn eq) is ready if that check ever fails. The quadratic is strictly no-worse than the pre-fix parse-failure state, so it ships as default.
- **The mod is fully client-side Custom-Quest data** - no host-only logic in the database. It is safe for a friend to install and play, **provided both players have byte-identical mod files** (a hard TQAE MP requirement).
- **The `.arz` build is byte-for-byte deterministic** (three independent rebuilds produce an identical SHA-256, matching the deployed file), so "byte-identical" is easy to guarantee - and trivially guaranteed if Will and his friend share one zip (see `SHARE_AND_PLAY.md`).
- **What only live 2-player testing can confirm:** actual spawn density in co-op, the `np*np` parse check above, soul-summoned **pet** spawn/persistence under co-op lockstep, and that the injected quest/entity content (blood-cave portal, widow letter, fountain, caravan, Hemorrheus) neither desyncs nor crashes a joining client. These are enumerated in §M2.3.

---

## Risks found and their status

| # | Risk (from CLAUDE.md / audit) | Real? | Evidence | Status |
|---|-------------------------------|-------|----------|--------|
| R1 | SV `RunEquation` MP spawn-scaling formulas fail to parse in AE → fewer/no scaled spawns in MP | **YES** | `docs/crash_analysis_report.md` logs `RunEquation load failure`; operator-set anomaly (`tools/debug/mp_operator_audit.py`): base TQAE proxy-spawn equations use only `+ - *`, SV uniquely adds `/` | **FIXED** (DB) - see §M1 |
| R2 | Determinism: both players need byte-identical mod files or desync/crash | **YES (inherent TQAE rule)** | TQAE lockstep MP model | **Mitigated by process** - deterministic build + share-one-zip; see §M2 + `SHARE_AND_PLAY.md` |
| R3 | Host-only / SP-only injected content (proxies, quests, Hemorrheus, fountain/caravan/letter) that could crash/desync a client | **NO host-only logic found in DB**; map-lane content is standard TQ mechanics | Hemorrheus is a normal `Class=Proxy` placed monster (cloned from base-SV `q_leinth_lone`); its pool uses literal spawn/champion counts (not equations). Quest content uses standard quest tokens (per-character, MP-safe). | **No DB fix needed**; live 2-player smoke test still required (§M2) |
| R4 | Other MP-conditional equations (`numSpawnMaxEquation`, `goldAmountEquation`, `difficultyEquation`, `characterDifficultyEquation`) might also fail in AE | **NO** | `tools/debug/mp_scan_all_eq_tokens.py` - SV's `numSpawn*` equations use only `+ - *`; SV's gold/difficulty equations use `/` **only in the exact forms the base game also uses** (those evaluators support `/`) | **No fix needed** (verified) |

---

## GATE M1 - RunEquation / MP formula enumeration + classification + fix

### M1.1 Enumeration (every equation-bearing field in the built `.arz`)

Scanned all 50,352 records of `work/SoulvizierClassic/Database/SoulvizierClassic.arz` for every string field that holds an engine equation (`tools/debug/mp_scan_all_eq_tokens.py`, `tools/debug/mp_scan_equations.py`). The equation fields that reference `numberOfPlayers` (i.e. are MP-conditional) fall into these families:

| Field family | Purpose | MP token | Uses `/`? |
|---|---|---|---|
| `spawnMaxEquation`, `spawnMinEquation`, `championMaxEquation`, `championMinEquation` (in `...\proxypoolequation_*.dbr`) | Monster-pool spawn/champion budget scaling | `poolValue`, `numberOfPlayers` | **YES (SV)** |
| `numSpawnMaxEquation`, `numSpawnMinEquation` (MonsterPool records) | Direct per-pool spawn-count scaling | `numberOfPlayers` | No |
| `goldAmountEquation` (loot generators) | Gold reward scaling | `generatorLevel`, `numberOfPlayers` | Only where base game also does |
| `difficultyEquation`, `characterDifficultyEquation` | Difficulty/level scaling | `averagePlayerLevel`, `numberOfPlayers`, `characterLevel` | Only where base game also does |

### M1.2 Classification - which fail in AE, with evidence

**Root cause (pinned, evidence-based).** The tokens SV uses (`poolValue`, `numberOfPlayers`) are the *same* tokens the stock TQAE game uses in these exact fields - so "unknown tokens" is **not** the cause. The real cause is the **operator set of the proxy-spawn equation evaluator**:

```
tools/debug/mp_operator_audit.py  (SVC vs base TQAE database)

########## SPAWN/PROXY EQUATION FIELDS ONLY ##########
  BASE TQAE (spawn eq fields): operator totals {'*': 1238, '+': 1216, '-': 18}
      '/' NEVER used in BASE TQAE (spawn eq fields) equations.
  SVC (spawn eq fields):       operator totals {'-': 44, '+': 628, '*': 646, '/': 44}
      '/' appears in 44 equation values (examples):
        records\proxies egypt\proxypoolequation_01.dbr :: championMaxEquation =
          '((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))*2'
        records\proxies egypt\proxypoolequation_01.dbr :: spawnMaxEquation =
          '((poolValue * 2.3) - (poolValue / (0.4 +(numberOfPlayers * 0.6))))*2.7'

  ==== VERDICT ====
    BASE spawn-eq operators: ['*', '+', '-']
    SVC  spawn-eq operators: ['*', '+', '-', '/']
    Operators SVC uses in spawn eqs that BASE never does: ['/']
    >>> '/' is used ONLY by SVC spawn equations, never by base game.
    >>> This strongly implicates '/' as the RunEquation parse failure cause.
    SVC spawn-eq values containing '/': 44
```

Corroborating in-game evidence (`docs/crash_analysis_report.md`, "Key Finding: Proxy RunEquation Failures"):

```
Game logs show repeated `RunEquation load failure` for SV spawn formulas:
  poolValue (((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0)))))
These are SV's custom multiplayer scaling formulas that the AE engine can't parse.
They're benign warnings - the engine falls back to default pool values. These do
not cause crashes but may affect monster spawn density (likely spawning fewer
than intended).
```

Important nuance proven during this audit: `/` is **not** universally rejected by AE. The base game uses `/` **822 times** in *item* equations (`targetLevelEquation` etc.), and SV/base both use `/` in `goldAmountEquation`/`difficultyEquation`. It is specifically the **proxy-spawn** equation evaluator (`spawnMax/Min`, `championMax/Min`) that only ever sees `+ - *` in stock content and fails on `/`. That is why the fix is scoped to exactly those fields.

**Classification result:**

| Distinct SV spawn/champion equation | Verdict in AE | Why |
|---|---|---|
| `((poolValue * 2.3) - (poolValue / numberOfPlayers))` | **FAIL** | `/` in spawn evaluator |
| `((poolValue * 2.3) - (poolValue / (0.4 +(numberOfPlayers * 0.6))))*2.7` | **FAIL** | `/` in spawn evaluator |
| `((poolValue * 2.3) - (poolValue / numberOfPlayers))*2.7` | **FAIL** | `/` in spawn evaluator |
| `((poolValue * 2.3) - (poolValue / numberOfPlayers))*2` | **FAIL** | `/` in spawn evaluator |
| `((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))*2` | **FAIL** | `/` in spawn evaluator |
| `((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))` | **FAIL** | `/` in spawn evaluator |
| `(poolValue * 2.3) - (poolValue / numberOfPlayers)` | **FAIL** | `/` in spawn evaluator |
| `((poolValue * 2.3) - (poolValue / numberOfPlayers))*3` | **FAIL** | `/` in spawn evaluator |
| `1*1` | PASS | constant, `+ - *` only |
| `poolValue * 1` | PASS | `+ - *` only |
| all `numSpawnMax/MinEquation` values | PASS | `+ - *` only (SV already avoids `/` here) |

Failure impact is **MP-specific and benign**: in single-player (`numberOfPlayers = 1`) the parse-fail fallback and SV's intent nearly coincide, so single-player was barely affected in practice; in co-op the failing equation reverts the pool to base-game density, so SV's boosted MP spawns never appear. It does not crash and it is deterministic (both host and client evaluate the same records the same way), so it does not desync - it just under-delivers monsters in MP.

### M1.3 Fix applied

New database patch `_fix_mp_spawn_equations(db)` in `tools/apply_svc_patches.py`, called from `apply_all_extended_patches` (before the soul-drop pass), followed by a hard invariant check `_verify_no_slash_in_spawn_equations(db)` that fails the build if any spawn/champion equation still contains `/`.

Each failing equation is rewritten to a **`/`-free quadratic in `numberOfPlayers`** that approximates SV's intended spawn count across the valid 1–6 player range. Because SV's forms are `poolValue * (A − 1/f(np)) * k` with `f` linear in `np`, `poolValue` factors out; the players-scalar `g(np) = (A − 1/f(np))·k` is fit to `c0 + c1·np − c2·np²` (deterministic `numpy.polyfit` over np = 1..6, `tools/debug/mp_design_replacements.py`) and multiplied back by `poolValue`. The result uses only `+ − *` with a binary-subtraction term. Coefficients are baked into the patch so the build needs no numpy.

**Fidelity to SV's design - the TRUE measured per-player relative error** (independently re-derived: extract the pre-fix SV form and the post-fix replacement, pair per field, evaluate both with a real arithmetic evaluator at np = 1..6; `tools/debug/mp_quad_pinned.py`, `mp_fit_bakeoff.py`):

```
PRIMARY spawnMax form  ((poolValue*2.3) - (poolValue/(0.4+np*0.6)))*2.7 :
   SV g(np)   :  3.510  4.522  4.983  5.246  5.416  5.535     (p1..p6)
   fit g_hat  :  3.601  4.375  4.949  5.322  5.495  5.467
   rel err %  :  2.57   3.25   0.66   1.48   1.47   1.23      (max 3.25% at np=2)

pure '1/np' forms  ((poolValue*2.3) - (poolValue/np)) [*k] :
   rel err %  :  4.40   5.32   0.77   2.37   2.18   1.90      (max 5.32% at np=2)
```

**Correction to a prior overclaim.** An earlier draft of this doc stated the replacement is "exact at 1-2 players (the common co-op cases)" and that single-player is "unaffected." **That was not accurate.** The unconstrained least-squares `polyfit` is fit over np = 1..6, so it does **not** pass through SV's exact np = 1 value: single-player (np = 1) differs by **~2.57% (primary spawnMax form) to ~4.40% (pure `1/np` forms)**, and the worst point is **np = 2 at ~3.25% / ~5.32%** - not exact at either. The true errors are the table above.

**Why this is still the right fit (and why np = 1 is deliberately NOT pinned exact).** Materiality is negligible *and* the balanced fit is the best choice for the actual goal:
- The engine **floors** these pool budgets to integer counts, so the sub-integer error rarely changes the in-game count. Example (spawnMax, pool = 4): SV np = 1 → floor(4·3.51) = 14, replacement → floor(4·3.601) = 14 (identical); champion (pool = 4): SV → 5, replacement → 5. Across pool = 1..12 × np = 1..6 the replacement's floored count matches SV in the large majority of cells and **never REDUCES single-player spawns below SV** - so this is not a functional balance break.
- Pinning np = 1 exact **is** trivial (a constrained fit through SV's np = 1 value), and it was fully evaluated (`tools/debug/mp_fit_bakeoff.py`, `mp_quad_pinned.py`). It was **rejected on purpose** for two concrete reasons:
  1. **It degrades the primary co-op case.** Pinning np = 1 pushes the fit error onto **np = 2** - it rises from the current ~5.32% to ~6.6% (unweighted-pinned) and up to ~9.85% (monotone-pinned). np = 2 is exactly the **Will + one friend** case this whole fix is for, so pinning under-delivers the co-op pool by up to ~5 more monsters at high poolValue (measured with `tools/debug/mp_quad_pinned.py` + `mp_materiality.py`: over a pool = 2..10 sample the summed |np = 2 floored Δ| is ~50 for a pinned fit vs ~26 for the current fit) - to buy a single-player nicety that the integer floor makes almost invisible.
  2. **It introduces a non-monotonic integer artifact.** The pinned parabola turns over before np = 6, so a 6-player game would spawn *fewer* monsters than a 5-player game at many poolValues (SV's own curve is monotone-increasing). Forcing monotonicity back on top of the pin is what drives np = 2 all the way to ~9.85%.
  (For the record, the pinned fit does have a slightly lower *total* floored deviation across the full 1..6 grid - 248 vs 275 mismatched cells - because it wins at np ≥ 3; but total-over-all-party-sizes is the wrong objective here. The mod is played at np = 1 and np = 2, and the current fit is better at both the co-op case and monotonicity.)
  So the honest choice is: **keep the balanced fit and state its true errors** (this section), rather than pin np = 1 and degrade the case that matters.

All eight distinct failing forms fit within **≤ 5.32%** error. Example rewrites (live proxy pools):

```
records\proxies egypt\proxypoolequation_01.dbr
  spawnMaxEquation   BEFORE: ((poolValue * 2.3) - (poolValue / (0.4 +(numberOfPlayers * 0.6))))*2.7
                     AFTER : poolValue * (2.623966 + (1.076769 * numberOfPlayers) - (0.100485 * numberOfPlayers * numberOfPlayers))
  championMinEquation BEFORE: ((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0))))
                      AFTER : poolValue * (0.91 + (0.497143 * numberOfPlayers) - (0.05 * numberOfPlayers * numberOfPlayers))
```

**Defensive future-proofing:** any *unknown* `/`-bearing spawn equation (e.g. introduced by a future roster change) that does not match one of the eight known SV forms is rewritten to a safe `/`-free static fallback `poolValue * (1.9 + (0.15 * numberOfPlayers))` and logged loudly, so the mod can never re-ship a parse-failing spawn equation without the build shouting about it.

### M1.4a Structural-novelty caveat + LINEAR fallback (the `np*np` question)

The quadratic replacement multiplies `numberOfPlayers * numberOfPlayers` (a variable by itself). **This structure has ZERO precedent in the base game.** Surveyed independently:
- All **53 distinct base-game proxy-spawn equation forms** (`spawnMax/Min`, `championMax/Min`, `numSpawnMax/Min`; `tools/debug/mp_base_spawn_forms.py` over `database.arz`) use only operators `{+, −, *}`, max paren depth 2, and **every** `numberOfPlayers`-scaling form is strictly **linear** in `numberOfPlayers` (e.g. `(3+(1.6*numberOfPlayers))*1.7`). None self-multiply.
- Across the **entire** base game - **74,013 records / 16,519 equation values across 103 equation fields** (`tools/debug/mp_scan_selfmul.py`) - there are **0** occurrences of any variable-times-itself (`X*X`). (The base game expresses powers with the `^` operator, e.g. `((defenseAttrArmor * 2) ^ 2.05)`, but only in *item-cost / level / gold* equations - never in a spawn equation.)

So the operators `+ − *` are individually proven-good in the narrow proxy-spawn evaluator, but the **combination** `np*np` (a genuine quadratic term) is **not** something the base game ever feeds that evaluator. Its parseability in that specific code path is therefore **confirmed only by a live in-game check** (see M1.5). A sane arithmetic parser handles `np*np`, and the quadratic is strictly **no-worse** than the pre-fix `/`-parse-failure state (worst case it also falls back to base density, exactly like today; it cannot make MP worse than the unfixed build) - so it ships as the default.

**Escape hatch - `SVC_MP_SPAWN_LINEAR=1`.** The build accepts an environment flag that swaps the quadratic family for a **linear** family `poolValue * (c0 + c1*numberOfPlayers)`:
- This is **structurally identical to a real base-game spawn equation** - the base game ships `(poolValue * 1.6) * (0.53 +(0.2*numberOfPlayers))` which is exactly `poolValue*(0.848 + 0.32*np)`. **Zero novel structure**, guaranteed-parseable, monotone by construction, and **exact at np = 1**.
- Cost: higher mid-range error (np = 2 ≈ 11–16%), because a straight line cannot follow SV's concave saturating curve as well as a parabola.
- **Use it only if** a live game log ever shows a `RunEquation load failure` on a *spawn* equation after this fix (i.e. the narrow evaluator rejected `np*np`). Rebuild with `SVC_MP_SPAWN_LINEAR=1` and redeploy the arz; the flag is read in `_fix_mp_spawn_equations`. Both families were built + verified `/`-free and `np*np`-free-respectively (`tools/debug/mp_regression_snapshot.py` on each).

### M1.4 Proof the rebuilt `.arz` parses (no `/` remains)

```
=== Patch MP: Fix multiplayer spawn-scaling equations ===
  Rewrote 44 spawn/champion equation value(s) across 11 proxy record(s) to '/'-free AE-valid form
```
The build's post-fix assertion (`_verify_no_slash_in_spawn_equations`) did **not** raise → 0 offenders. Independent re-scan of the rebuilt `.arz` (`tools/debug/mp_regression_snapshot.py`):
```
spawn-eq values still containing '/': 0        (was 44 before the fix)
```
Live proxy-pool spot check (`tools/debug/mp_full_load_check.py`): all 5 live regional pools (egypt, greek, orient, xpack-creatures, xpack-proxieshades) now carry `/`-free equations; `slash=False` on every one.

### M1.5 The ONE launch-gated check (confirms `np*np` parses in the spawn evaluator)

The only thing a code/data audit cannot prove is that the narrow proxy-spawn evaluator accepts the `numberOfPlayers * numberOfPlayers` term (M1.4a). **This is confirmable with a single game launch - single-player is enough** (the equation is loaded regardless of player count):

1. Launch TQAE, Play Custom Quest → SoulvizierClassic, load into any area with monster spawns.
2. Check the game log (`<TQ docs>\Logs\` and the console) for **`RunEquation load failure`** referencing a **spawn/champion** equation.
   - **No such line** → the quadratic `np*np` parses fine → the fix is fully confirmed. (SV's *old* `/`-bearing lines will no longer appear because they were removed.)
   - **A spawn `RunEquation load failure` still appears** → the evaluator rejected `np*np`. Rebuild with `SVC_MP_SPAWN_LINEAR=1` (M1.4a) and redeploy the arz; re-launch and confirm the line is gone.

Until this launch check is done, the honest status of the `np*np` structure is **"removed the known-bad `/`; replacement parseability in the spawn path is high-confidence but unconfirmed, with a proven linear fallback ready."**

**M1: PASS** for the `/`-removal (proven, byte-verified) + fit correctness (measured); the `np*np` parse is the single launch-gated item above.

---

## GATE M2 - Determinism / client-side audit

### M2.1 Client-side-only confirmation

- The mod loads via **TQAE main menu → Custom Quest → SoulvizierClassic**. It is content-only data (`.arz` database + `.arc` resources + `world01.map`). There is no executable, no server component, and no Game.dll/Engine.dll dependency - enchanting and every mechanic are baked into the `.arz` (see CLAUDE.md "Enchanting … no Game.dll dependency").
- The build scripts add no per-machine state. The `.arz` writer (`tools/arz_patcher.py::write_arz`) iterates records in a stable insertion order (`OrderedDict`), preserves each record's source timestamp verbatim, and uses deterministic zlib level-6 compression and an append-only string table.
- **Injected entities are standard TQ mechanics, not host-only logic:**
  - **Hemorrheus (Blood Toxeus superboss):** a normal `Class=Proxy` placed monster proxy (`records\drxmap\proxy\q_bloodtoxeus_lone.dbr`) cloned from the existing base-SV donor proxy `q_leinth_lone`, pointing at a MonsterPool with **literal** `spawnMin/Max = 1` and `championChance/Min/Max = 100 / 1 / 2` (fixed integers, *not* equation-driven → immune to the R1 spawn-equation issue entirely). The monster (`um_bloodtoxeus_99.dbr`) is a plain `Class=Monster`, `monsterClassification=Boss`. TQ resolves placed proxies authoritatively on the host and replicates the spawned entities to clients - the mechanism every base-game boss uses.
  - **Fountain / caravan / widow letter / blood-cave portal:** owned by the map/quest lane (not modified here). They use standard TQ **quest tokens** (`OwnsToken` / `Condition_PickupItem`), which are per-character/party state that TQAE replicates in MP the same way it does for the base campaign. Nothing in these is a database-side host-only assumption.

### M2.2 Determinism proof (byte-identical builds)

> **SUPERSEDED HASH (see top banner):** the `efbf2471…` hash below was the MP-fix-only baseline and no
> longer matches the deployed arz. The current build27 deployed arz is `7C6E2099…` / SHA-256
> `5014f190…` / 54,529,030 B. The determinism *property* below still holds (rebuild twice, MD5 matches);
> only the specific bytes advanced as later content waves landed.

The `.arz` was rebuilt **independently, three times** (twice during the original pass, once during this round-2 re-verification), from the same sources, all producing the identical SHA-256 - and that hash **also matches the currently-deployed** `CustomMaps\SoulvizierClassic\Database\SoulvizierClassic.arz`:

```
build #1 sha256:  efbf24711ec542b4f8e4cb3d17d6a3e06bca9216f255ec46c2a603145cfc487d
build #2 sha256:  efbf24711ec542b4f8e4cb3d17d6a3e06bca9216f255ec46c2a603145cfc487d
build #3 sha256:  efbf24711ec542b4f8e4cb3d17d6a3e06bca9216f255ec46c2a603145cfc487d   (round-2 re-verify)
deployed  sha256: efbf24711ec542b4f8e4cb3d17d6a3e06bca9216f255ec46c2a603145cfc487d   (CustomMaps, matches)
DETERMINISTIC: byte-identical across independent builds AND == deployed
```

This byte-identity also proves the round-2 code changes (which added the opt-in `SVC_MP_SPAWN_LINEAR` fallback and corrected comments/docs) **did not alter the default shipped output** - the deployed arz is unchanged, so no redeploy is required. So even if Will and his friend each built the mod independently from the same sources, they would get identical database bytes. In practice they will **share one zip** (see `SHARE_AND_PLAY.md`), which makes byte-identity automatic.

### M2.3 Host-only entity risk that ONLY live 2-player testing can confirm

These are not database defects; they are runtime behaviors to smoke-test once in a real 2-player session:

1. **Blood-cave streaming/seam behavior for the joining client.** The custom relocated levels + navmeshes are a map-lane concern; confirm the *client* (not just the host) can walk the cave-mouth → west tunnel → blood cave and back without a desync or fall-through.
2. **Quest-token content on a client who did not start the quest.** Confirm the widow-letter pickup, the blood-cave portal quest, and any SV area questline advance correctly for a client, and that a client picking up a quest item does not desync the host's quest state. (Standard TQ quests replicate fine; this is belt-and-suspenders because these are freshly injected.)
3. **Hemorrheus + champion-add wave in co-op.** Confirm the boss and his blood-demon guards spawn once (not per-player) and that his loot (guaranteed Crimson Verdict piece + high-bleed drop) is granted correctly with 2 players present.
4. **Soul-summoned pet spawn/persistence in co-op.** The centerpiece souls summon pets: the arz has **1307 `Class=Pet` records** and several hundred `Skill_SpawnPet` summon skills (328 by `Class`, 435 counting by template; `tools/debug` scan of the built arz). Confirm that a client (not just the host) can summon soul pets, that the pets persist (per CLAUDE.md the permanent-pet fix removes `spawnObjectsTimeToLive`), and that both players' pets coexist without desync or a pet-count runaway. This is **inherited SV/SVAERA engine behavior, not a defect introduced by the DB build** - SVAERA already ships pets in MP with host-authoritative summons - but because souls are the mod's headline mechanic and pets are the highest-volume dynamic entity, it belongs on the live-test list. (No DB fix is expected here; this is a smoke-test-only unknown.)
5. **Spawn density sanity.** With the R1 fix in, confirm co-op areas now feel appropriately busier than single-player (the fix's intent), with no run-away spawn counts. (This is also where a spawn `RunEquation load failure` for the `np*np` term would surface - see M1.5.)

**M2: PASS** (client-side-only confirmed; deterministic build proven; residual live-test items enumerated).

---

## GATE M3 - `.arz` changed: validate + full load + regression

> **Round-2 note:** the round-2 code change (opt-in `SVC_MP_SPAWN_LINEAR` fallback + doc/comment fixes) leaves the **default** build byte-identical to the deployed arz (SHA `efbf2471…`, re-verified - see M3.4). So M3's gates below still describe the shipped arz exactly; nothing was re-deployed.

The `.arz` was rebuilt with the R1 fix (`SVC_RELEASE_DROPS` unset, matching the previously-deployed testing build, so the *only* intended delta is the spawn-equation fix).

### M3.1 `validate_tags`

Exact output against the deployed arz + `Text.arc` (independently reproduced 2026-07-07):
```
py tools/validate_tags.py <arz> work/.../Text.arc <uber_soul_tags.txt> <mod_authored_tags.txt>

  Loaded: 50352 records, 141530 strings
  Mod-tag manifest: mod_authored_tags.txt (117 mod-owned tags)
  OK: all 73 referenced mod tags are present in Text.arc     <-- gameplay gate PASSES
  Authoritative list: uber_soul_tags.txt (178 tags)
  FAIL: 171 authoritative tag(s) missing from Text.arc       <-- superset/wishlist cross-check
  RESULT: FAIL   (exit 1, driven by the authoritative cross-check, not the referenced-mod gate)
```

**Reconciling the 171 vs the real visible bug.** The tool runs two checks (see its docstring): (a) the **referenced-mod-tags gate** - every tag the `.arz` *actually references AND* the build manifest claims to author - which **PASSES** (`all 73 referenced mod tags present`); and (b) an **authoritative cross-check** of the 178-entry `uber_soul_tags.txt` list, of which **171 are absent** from the deployed `Text.arc`. The overall `RESULT: FAIL`/exit-1 comes from (b). The 171 is misleading as a "bug count": `uber_soul_tags.txt` is a *wishlist superset* of uber-soul tags, and the **large majority of the 171 are not referenced by the deployed arz at all** (no in-game effect - they never render).

**The real, user-visible subset (independently verified).** The genuinely-broken tags are the ones that are BOTH referenced by a deployed record AND missing from `Text.arc`. I enumerated these directly: **8 Blood Toxeus / Crimson Verdict tags**, each referenced by a shipped item/monster record but absent from the deployed `Text.arc`:

| Tag | Referenced by (deployed record) | In Text.arc? |
|---|---|---|
| `tagMonsterHemorrheus` | `...\skeleton\um_bloodtoxeus_99.dbr :: description` | MISSING |
| `tagSVCSetCrimsonVerdict` | `...\item\sets\svc_crimsonverdict.dbr :: setName` | MISSING |
| `tagSVCSoulHemorrhage` | `...\soul\svc_uber\blood_toxeus_soul_n.dbr :: itemNameTag` (×3 tiers) | MISSING |
| `tagSVCSoulHemorrhageDESC` | Hemorrhage soul description | MISSING |
| `tagSVCarmCrimsonVerdict` | `...\equipmentarmband\svc_*_crimsonverdict.dbr :: itemNameTag` (×3) | MISSING |
| `tagSVChlmCrimsonVerdict` | `...\equipmenthelm\svc_*_crimsonverdict.dbr :: itemNameTag` (×3) | MISSING |
| `tagSVCtorCrimsonVerdict` | `...\equipmentarmor\svc_*_crimsonverdict.dbr :: itemNameTag` (×3) | MISSING |
| `tagSVCwpnVeinRender` | `...\equipmentweapon\sword\svc_*_veinrender.dbr :: itemNameTag` (×3) | MISSING |

(These 8 escape the referenced-mod *gate* only because they postdate the `mod_authored_tags.txt` manifest - the manifest predates the Blood Toxeus wave, so the gate does not know it "owns" them. They are nonetheless authored-by-the-mod and referenced, so they are a real gap.)

**Status of this FAIL: pre-existing, out of MP/DB-spawn scope, and independent of my fix.** Confirmed three ways: (1) the **default round-2 rebuild is byte-identical to the deployed arz** (M3.4), and the validator reproduces the *identical* result against it; (2) all 8 visible-broken tags are **name/description** tags - none are spawn-equation content; (3) **my change adds/removes zero name/description tags** (it only edits equation strings), so the tag result is identical with and without the round-2 change. It is a known `build_text_arc.py` ↔ `build_svc_database.py` coupling gap (CLAUDE.md). **In-game effect:** Hemorrheus's name, the Crimson Verdict set name, its 4 set-piece item names, the Vein Render sword, and the Hemorrhage soul render as raw tag strings instead of proper names - a real, user-visible content bug that should be fixed **before a public Steam listing** (rebuild + redeploy `Text.arc`; see the pre-flight in `STEAM_RELEASE.md`). It is **not** an MP, determinism, or crash problem, so friends-only interim co-op is unaffected. A follow-up task (rebuild + redeploy `Text.arc`) is filed.

### M3.2 Full load (corruption check)

Decoded **every** record of the rebuilt `.arz` (`tools/debug/mp_full_load_check.py`):
```
decoded OK=50352 empty=0 bad=0 total=50352
```

### M3.3 Record-count delta explained + regression spot-checks

Baseline (pre-fix deployed `.arz`) vs rebuilt (post-fix), via `tools/debug/mp_regression_snapshot.py`:
```
                       BASELINE            POST-FIX
records:               50352               50352      (unchanged)
strings:               141525              141530     (+5: the 5 distinct new equation strings)
spawn-eq '/'-count:    44                  0          (the fix)
blood_toxeus/hemorrheus: present           present    (Jewelry_Ring.tpl, unchanged)
ainex_soul:            present             present    (empusasoulcarver_spiritbolt skill, unchanged)
lyia (ref pet):        present             present    (unchanged)
yeti am_yeti_27:       chanceToEquipFinger2=0.0       0.0   (gating intact)
yeti hulking_yeti_35:  0.0                 0.0        (gating intact)
yeti am_yetichampion_32: 0.0               0.0        (gating intact)
boss_gargantuanyeti_32: 100.0             100.0       (boss drops intact)
soul-ish item records: 2372                2372       (unchanged)
```
The **only** differences are `+5` strings (the new equation forms) and `44 → 0` on the spawn-equation `/` count. Every regression anchor (Hemorrheus, Ainex, souls, yeti soul-drop gating) is byte-stable. `.arz` size 54,527,198 → 54,526,916 bytes (−282, consistent with replacing the `/`-division strings and de-duplicating in the string table).

### M3.4 Round-2 re-verification (default build unchanged; linear fallback valid)

> **SUPERSEDED HASH (see top banner):** `efbf2471…` was the MP-fix-only baseline; the deployed arz is
> now build27 `7C6E2099…` (54,529,030 B). This block is a point-in-time record from the MP-fix pass.

Round 2 added the opt-in `SVC_MP_SPAWN_LINEAR` fallback and corrected the doc/comments; it did **not** change the default output. Verified:
```
DEFAULT rebuild (round-2 code) sha256:  efbf24711ec542b4f8e4cb3d17d6a3e06bca9216f255ec46c2a603145cfc487d
deployed CustomMaps arz        sha256:  efbf24711ec542b4f8e4cb3d17d6a3e06bca9216f255ec46c2a603145cfc487d   -> IDENTICAL
  default rebuild: full-load OK=50352 bad=0 ; spawn-eq '/'-count = 0 ; np*np present (quadratic, as intended)

LINEAR rebuild (SVC_MP_SPAWN_LINEAR=1): built OK, size 54,526,702 B
  full-load OK=50352 ; spawn-eq '/'-count = 0 ; spawn-eq np*np-count = 0 (pure linear, base-idiomatic)
  regression anchors (blood_toxeus, ainex, souls, yeti gating) all present/intact
```
So the shipped arz is unchanged (no redeploy needed) and the linear escape hatch is proven to build a valid, `/`-free, `np*np`-free arz if ever required.

**M3: PASS** (default build byte-identical to deployed + reproduced; validate_tags FAIL isolated as pre-existing/out-of-scope; full load 0 bad; delta fully explained; regressions intact; linear fallback validated).

---

## GATE M4 - Toxeus Encounter Suite (build37, backlog #32): 6-player checklist

> Added 2026-07-14 for the build37 Toxeus Encounter Suite (registry module
> `tools/patches/toxeus_suite.py`, Parts A-D). Unlike M1-M3 (`.arz` DB lane only), this section
> spans BOTH lanes: the ambush's placement is map-lane (`world01.map` in `Levels.arc`), the rant
> scroll + Endless Hunt + all pools are DB-lane. It is the whole-suite MP readiness checklist that
> M2.3 (which covers only the deep Hemorrheus boss, item 3) did not have. All three new surfaces are
> standard host-authoritative TQ mechanics; the hard MP requirement (byte-identical mod files, M2 +
> the Determinism statement below) applies to the suite unchanged.

### M4.1 The three suite surfaces + their party-size invariants

| Surface | Record(s) | Party-size behaviour | Proof status |
|---|---|---|---|
| **A** entrance ambush | `q_bloodtoxeus_ambush` (clone of `q_bloodtoxeus_lone`, `chanceToRun=33` - Will FINAL DESIGN 2026-07-14, retuned 15 -> 33) -> `_BT_POOL`; placed in `drxFirstRoom` local `(100,1,50)` (`B41_SPECS` item 5). The **ONLY** Blood-Toxeus chance in the entrance corridor (the never-wired ~50% parchment feature is retired). | **Exactly 1** Blood Toxeus + 2 blood-demon champion adds, at ANY party size | **STATIC-PROVEN** (M4.2); confirm live at np>=2 |
| **B** rant scroll | `svc_toxeus_rant` (Parchment) <- `toxeus_rant_item` (`LootItemTable_FixedWeight`) <- `toxeus_rant_perplayer` (`FixedItemLoot.tpl`, `numSpawn*Equation='numberOfPlayers*1'`); wired `um_bloodtoxeus_99` Misc4 @100% | **N copies for N players** (one per player) | equation **AE-parse-safe** (M4.3); monster-equip-slot per-player expansion **LAUNCH-GATED** (container fallback authored) |
| **C** Endless Hunt | `um_toxeus_hunt_99` (ShadowStalker rig) appended at weight 1 + per-slot `limit=1` into ~345 Hades trash pools | **At most 1** Hunt per Hades pool per spawn trigger, any party size | **STATIC-PROVEN** (per-slot `limit=1` + fail-loud sweep gate); confirm no co-op runaway |

> These A/B/C are the #32 SUITE surfaces. ONE ADJACENT Blood-Toxeus surface from the earlier M15
> feature (Will 2026-07-09) also spawns `um_bloodtoxeus_99` and so shares the single-Toxeus invariant:
> the **deep-chest Devourer** (`egg_blooddragon` champion @100, LIVE via the native `egg_blooddragon_pack`
> proxy), enumerated and neutralised in M4.2. The M15 **parchment** surface (`demon_01_cluster_toxeus50`
> champion @50) is **RETIRED** (Will FINAL DESIGN 2026-07-14 - it was never wired to the map; the monolith
> no longer authors it, nor its sibling `q_bloodtoxeus_lone_50`). So the corridor has EXACTLY ONE
> Blood-Toxeus chance: the ~33% ambush (A). See M4.7 note 5.

### M4.2 The single-Toxeus invariant (the double-spawn history, structurally closed)

The load-bearing MP property: **no Toxeus placement surfaces >1 Blood Toxeus at any party size 1-6.**
Ground truth (DB replay vs the built arz, verified 2026-07-14): after Will's FINAL DESIGN retired the
parchment pool, exactly **two** ProxyPools reference `um_bloodtoxeus_99`, and BOTH are neutralised so
their LITERAL spawn/champion counts hold at every player count (`proxyPoolEquation` empty = the engine
uses the literal `spawnMin/Max` + `championMin/Max` verbatim; `championMax` is then a hard integer cap,
never per-player-multiplied):

| Pool | Toxeus role | Placement | Literal Toxeus count |
|---|---|---|---|
| `q_bloodtoxeus_lone` (`_BT_POOL`) | 3 name slots (main) | the `drxFirstRoom` **ambush** proxy `q_bloodtoxeus_ambush` (`chanceToRun=33`, canonical, `B41_SPECS` item 5) | `spawnMax - championMax = 3 - 2 = 1` main + 2 blood-demon champions |
| `egg_blooddragon` | `nameChampion1` (champion @100) | the **deep-chest Devourer**, via the native `egg_blooddragon_pack` proxy in `drxBC2` (M15 in-place champion-join) | `championMax = 1` champion (+ 3 blood dragons) |

**FINAL DESIGN (2026-07-14, Will).** The derived parchment pool `demon_01_cluster_toxeus50` (formerly a
third row here, champion @50, never wired to the map) is **RETIRED** - the monolith no longer authors it
(nor its sibling `q_bloodtoxeus_lone_50`). The Part D gate is ROSTER-DERIVED, so the roster simply shrank
3 -> 2 with no gate code change; the DB replay confirms the gate stays GREEN on the two remaining pools
and still fails loud on a planted over-count.

**Round-2 history (2026-07-14, vet HIGH).** Before this final design there were THREE Toxeus pools, and
the two M15 pools (`egg_blooddragon` + the now-retired `demon_01_cluster_toxeus50`) both inherited the
base-game `proxyPoolEquation = proxypoolequation_02`, whose per-field floor `poolValue*(0.91 +
0.497143*np - 0.05*np^2)` takes `championMax=1` up to **2 at np in {4,5,6}** (`floor(1*2.099)=
floor(1*2.146)=floor(1*2.093)=2`) = **TWO Blood Toxeus side by side** in the deep-chest room for a
4-6-player party (`np<=3`, incl. Will's np<=2 co-op, was clean). `_apply_m15_toxeus_group_joins`
neutralises the equation on the (surviving) `egg_blooddragon` pool right where it authors the champion
join, so it holds its literal `championMax=1` at every party size (exactly 1 Devourer). The retired
parchment pool carried the same fix while it existed; removing the pool removes the concern entirely.

Enforced fail-loud, all re-verified after the fix:

- **Upper bound (<=1), ROSTER-DERIVED:** `toxeus_suite.py` Part D `_verify_toxeus_champion_cap` now
  derives EVERY pool referencing `um_bloodtoxeus_99` (name OR champion slot) straight from the arz and
  asserts, per pool, (i) `proxyPoolEquation` is neutralised (empty) and (ii) the literal max Toxeus
  count is `<= 1`. A future M-era pool that re-introduces the equation or an over-count fails the build
  LOUD. (Round-2: the prior gate proved this for `_BT_POOL` alone and MISSED the two M15 pools - that
  scoping gap is exactly what shipped the 4-6P double; it is now closed. A negative test confirms the
  new gate FAILS on the pre-fix arz and PASSES after neutralisation.)
- **Ambush lower bound (>=1):** `apply_svc_patches.py::_verify_mod_spawn_proxies_eligible` sub-checks A
  (champion crowd-out) + B (`limit_bloodtoxeus [1..110]` all-difficulty window) guarantee the ambush
  boss is not starved or scaled out; sub-check C fails the build if `_BT_POOL` retains the equation.

`chanceToRun=33` is a `Proxy.tpl` field rolled **once per instance** at level-load = a single ~33%
spawn-or-not roll, NOT a per-demon compounding roll. Net: a 6-player party sees the same 1 Toxeus per
surface as a solo player. (Will FINAL DESIGN 2026-07-14 retuned this 15 -> 33: it is now the SOLE
Blood-Toxeus chance in the corridor, so it deliberately sits above the original 10-25% single-ambush
guidance - that guidance assumed a second, parchment surface which is now retired. There is exactly ONE
roll, ~33%, with his entourage of 2 blood-demon adds inherent in `_BT_POOL`.)

### M4.3 Rant scroll per-player wiring - MP-safe path + the one launch-gated edge

The per-player count uses the **loot-table** `numSpawn` path, which is a DIFFERENT evaluator from the
proxy-spawn one that rejects `/` (M1.2). `toxeus_rant_perplayer` (`FixedItemLoot.tpl`) carries
`numSpawnMin/MaxEquation = 'numberOfPlayers*1'`:

- It is `/`-free and uses only `*`, with **no `np*np`** - so it does not even carry the M1.5
  quadratic-parse risk. SV's own `numSpawn*Equation` values all use `+ - *` and PASS (M1.1 / R4);
  this is the same operator class.
- `numSpawn*Equation` lives only on `FixedItemLoot.tpl` (DB-verified), which is why the outer table
  must be that template. The equation therefore parses in the item evaluator.

**LAUNCH-GATED edge (honest status):** whether a MONSTER **equip slot** (Misc4) honours the
sub-table's `numSpawn` per-player expansion is proven only for **containers**, not equip slots.
Live check at np=2: kill Blood Toxeus, confirm **2** copies of `{^r}The Murderer's Screed` drop (one
per player). If only 1 drops, flip to the documented fallback - a corpse/chest whose
`loottable = toxeus_rant_perplayer` (the SAME already-authored per-player table), spawned on
Blood-Toxeus death (a one-record + one-death-skill follow-up). Duplicates on repeat kills are
accepted (Will).

### M4.4 Endless Hunt in co-op

The roaming Hunt is appended at weight 1 into ~345 eligible Hades trash pools (per-slot probability
`<= 1/2400`), each appended slot carrying a per-slot `limit=1` **MAX-count cap**. This cap is the MP
safety: pool mains draw WITH REPLACEMENT, so without it a pack pool (`spawnMax>1`) could surface 2+
Hunts in ONE trigger (the "two-in-one-trigger" defect fixed for the Enslaver v2). With `limit=1` the
engine spawns **at most 1** Hunt per pool per spawn trigger, structurally, at any party size. A
fail-loud sweep gate (`_verify_legendary_stalker_sweep`) re-derives the touched set and proves 0
leaks into non-Hades / boss / quest / hero pools. Live check (co-op): the Hunt appears rarely in
Hades and never as a runaway pack.

### M4.5 Host-authoritative + determinism (unchanged from M2)

All three surfaces are standard host-authoritative TQ mechanics - placed proxies (ambush) and monster
loot/pool membership (scroll, Hunt) resolve on the host and replicate to clients, exactly like every
base-game boss and loot drop. **No host-only DB logic is added.** The M2 hard requirement stands: both
players need byte-identical mod files. Note the suite spans BOTH artifacts - the ambush placement is
in `Levels.arc` (`world01.map`), the scroll + Hunt + pools are in the `.arz` - so both must be
re-synced together after any rebuild (any rebuild advances the hash; see the Determinism statement).

### M4.6 Legendary-stalker feasibility VERDICT (mandate item c)

**A ROAMING + strictly-Legendary-only stalker as a pure data gate is NOT cleanly feasible, so it is
NOT shipped as such.** Roaming = appending the Hunt into many SHARED all-difficulty Hades trash pools,
and TQAE has **no per-appended-member difficulty filter**: `difficultyLimitsFile` scales a monster's
effective LEVEL toward a window, it does not suppress/filter the spawn. The shipped Endless Hunt
confines the Hunt to **Hades** (Act-4/endgame) pools, which reads in practice as "effectively
Legendary/endgame" - the honest closest approximation.

A TRUE data-only Legendary-only gate **does** exist for **FIXED** placements: the base-game **Hydra
pattern** (`pool1` empty + `poolLegendary1 = <boss pool>` spawns the boss on **Legendary only**;
`docs/reports/el_boss_audit.md`). So if Will wants a guaranteed Legendary-only Toxeus stalker, the
clean path is a FIXED-placement proxy using that PROVEN pattern (clone `q_bloodtoxeus_lone` ->
`q_toxeus_hunt_lone`, `pool1` empty, `poolLegendary1` = a single-member `um_toxeus_hunt_99` pool,
placed at one Hades/endgame spot) - trading "roaming but anywhere" for "findable but fixed." **This is
a Will design decision, not a defect.** The module's inert `limit_legendary_only` min-player-level
artifact is an UNPROVEN experiment (difficultyLimitsFile does not filter spawns) and must not be
relied on.

**WILL DECISION (2026-07-14): APPROVED, QUEUED (not scheduled).** Will greenlit a proper
Legendary-only Toxeus stalker via the PROVEN Hydra pattern (`pool1` empty + `poolLegendary1 =
<boss pool>`) as a distinct FIXED placement - NOT the inert `limit_legendary_only` experiment. It is
filed as a BACKLOG entry (approved-by-Will-2026-07-14, not scheduled) and is NOT built in this lane.
The already-shipped roaming Endless Hunt (Part C) stays as-is.

### M4.7 Launch-gated live checks (restart-Steam-before-test law) + creative-text veto

Per the RESTART-STEAM-BEFORE-TEST law, any test ping must kill TQ + Steam, restart, and hash-verify
the deploy landed BEFORE giving test instructions. Suite live checks:

1. **[np>=2]** Ambush spawns exactly 1 Toxeus + 2 adds (M4.2 static-proven; confirm live).
2. **[np=2]** Rant scroll drops 1 copy per player from Blood Toxeus's Misc4 (M4.3; else container fallback).
3. **[co-op]** Endless Hunt appears rarely in Hades, never a runaway pack (M4.4).
4. **[any]** The M1.5 `np*np` spawn-eq parse check (not suite-specific, but the standing launch check).
5. **[RESOLVED - parchment RETIRED, Will FINAL DESIGN 2026-07-14]** The M15 parchment feature (Will
   2026-07-09: "put toxeus devourer of blood there too with 50% spawn chance") was never wired to the map -
   the DB lane authored the derived pool+proxy `demon_01_cluster_toxeus50` but the MAP lane never injected
   the repoint (documented only as a prose comment at `build_section_surgery.py` `drxfirstxistion_
   connection`, now RETIRED). Asked whether the ambush 33% + a parchment 15%/50% could double-spawn Toxeus,
   Will's call: **"we need to retire the one we are adding and just update the 15% one to 33%."** So the
   monolith no longer authors `demon_01_cluster_toxeus50` (pool+proxy) or `q_bloodtoxeus_lone_50`; the
   parchment room keeps its plain `demon_01_cluster` (NO Toxeus); the sole corridor Toxeus is the single
   ~33% `drxFirstRoom` ambush. There is EXACTLY ONE Blood-Toxeus roll in the corridor - the double-encounter
   question is moot by design. (DB replay confirmed the three retired records are ABSENT and only the ambush
   `chanceToRun` field changed 15 -> 33.) **No map change** was made this lane.
6. **[amgoz1 CREATIVE-TEXT - RANT SCROLL CLEARED (Will 2026-07-14: "you are good to ship the rant
   scroll")]** The rant screed (`_RANT_TEXT`, ~180 words, Toxeus's voice, treats the original murderer as
   the blood-cult progenitor) and the scroll names (`{^r}The Murderer's Screed` / `A Parchment Slick with
   Blood`) **ship as-is** - Will's veto is satisfied. The ONLY remaining rant-scroll launch-gated item is
   the np=2 per-player Misc4 expansion live check (note 2 above; container fallback authored). *(Separate,
   still-pending:* the Part C Endless Hunt name/desc `{^r}Toxeus the Murderer, the Endless Hunt` + its
   `{^F}...Soul` remain under the standing amgoz1 sign-off; Will's 2026-07-14 clearance addressed the rant
   scroll only.) Full text is in `toxeus_suite.py` (`_RANT_TEXT`, the tag assignments) and
   `docs/reports/toxeus_suite_recon.md`.

**M4: PASS** (static invariants proven; DB replay verified 2026-07-14 after Will's FINAL DESIGN: `<= 1`
Blood Toxeus per pool at any party size 1-6 across the TWO Toxeus pools - ambush (`_BT_POOL`) + deep-chest
(`egg_blooddragon`) - each `proxyPoolEquation`-neutralised and covered by the roster-derived Part D gate
(gate GREEN on the shrunk 2-pool roster; still fails loud on a planted over-count and on the pre-fix
double); per-slot Hunt cap; `/`-free per-player scroll equation on the item evaluator. The corridor has
EXACTLY ONE Blood-Toxeus chance - the ~33% ambush - so the double-encounter question is moot by design;
the never-wired parchment feature (`demon_01_cluster_toxeus50` + `q_bloodtoxeus_lone_50`) is RETIRED.
Rant-scroll creative-text veto CLEARED (ships as-is); Legendary-only stalker APPROVED + QUEUED (Hydra
pattern, not built here). Residual live checks (ambush np>=2, scroll np=2 per-player, Hunt co-op,
np*np parse) enumerated under the restart-Steam law.)

---

## Determinism statement (what the friend needs)

**TQAE multiplayer requires every player to have byte-identical mod files or the session will desync or crash.** To guarantee that:

1. **The friend must install the exact same mod package Will has** - the entire `SoulvizierClassic` folder (`Database\SoulvizierClassic.arz`, `Resources\*.arc` including the 685 MB `Levels.arc`, and `Resources\Text.arc`). See `SHARE_AND_PLAY.md` for the shareable zip and install path.
2. **Share one zip, don't rebuild independently.** The simplest guarantee of byte-identity is: Will builds/deploys once, zips the deployed `SoulvizierClassic` folder, and the friend extracts that same zip. (The build is deterministic, so independent rebuilds would also match - but sharing the artifact removes all doubt.)
3. **Both must run the same base game version** (TQAE, same Steam build) - the mod overlays the base game's `database.arz`, so a base-game version mismatch is itself a desync source.
4. **Verify byte-identity if unsure:** compare the SHA-256 of the key files on both machines. Current expected database hash (build27, verified 2026-07-08): `5014f1903aa4163adaeb8c35fd71ca8fe36db2a7293aa874932660619b600c8f` (MD5 `7C6E209988F0CE815BAF35F058B6A0A8`, 54,529,030 B). (Any future arz rebuild changes this hash; both players must re-sync the new artifact.)
5. **Both must use a fresh, dedicated Custom-Quest character** (never a normal-campaign character; see CLAUDE.md). Character files themselves are per-player and do not need to match.

Files the friend needs, and why byte-identity matters per file:

| File | Size | Byte-identical required? |
|---|---|---|
| `Database\SoulvizierClassic.arz` | ~52 MB | **Yes** - item/skill/monster/spawn data; any mismatch desyncs |
| `Resources\Levels.arc` | ~685 MB | **Yes** - world geometry + navmeshes; mismatch = position/collision desync |
| `Resources\Text.arc` | ~0.4 MB | Recommended - cosmetic (names/descriptions); a mismatch is unlikely to desync but ship it anyway |
| `Resources\*.arc` (DRX, SV meshes/textures/sounds, Items, Quests, etc.) | ~1.1 GB total | **Yes** for anything with gameplay entities (Quests.arc, meshes referenced by collision); ship the whole set to be safe |

---

## Reproduce / re-verify

```
# Rebuild the arz (deterministic; a present-day rebuild = build27 sha256 5014f190...; default = quadratic MP-spawn fix):
py tools/build_svc_database.py \
  upstream/soulvizier_098i/Database/database.arz \
  upstream/soulvizier_0.9/Database/database.arz \
  upstream/soulvizier_041/Database/database.arz \
  work/SoulvizierClassic/Database/SoulvizierClassic.arz \
  "/c/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"

# Same, but emit the LINEAR fallback family (no np*np) -- only if the M1.5 launch
# check ever shows a spawn RunEquation failure:
SVC_MP_SPAWN_LINEAR=1 py tools/build_svc_database.py <same args>

# Audit + gate scripts (all under tools/debug/, read-only; the fit scripts are pure numpy):
py tools/debug/mp_operator_audit.py <arz> <base_tqae_arz>      # M1 root-cause (operator anomaly: '/')
py tools/debug/mp_base_spawn_forms.py <base_tqae_arz>          # M1.4a base spawn-eq forms: {+,-,*} only, all linear, 0 self-mul
py tools/debug/mp_scan_selfmul.py <base_tqae_arz>              # M1.4a 0 X*X across 74,013 base records (np*np has no precedent)
py tools/debug/mp_scan_all_eq_tokens.py <arz> <base_tqae_arz>  # M1 full token enumeration
py tools/debug/mp_eval_equations.py                            # M1 evaluate SV vs replacement at players 1-6
py tools/debug/mp_quad_pinned.py                               # M1.3 measured per-np error of the quadratic (proves the true 2.6-5.3%)
py tools/debug/mp_fit_bakeoff.py                               # M1.3 why np=1 is NOT pinned (pinning worsens np=2 co-op)
py tools/debug/mp_linear_design.py                             # M1.4a the linear-fallback coefficients
py tools/debug/mp_regression_snapshot.py <arz>                 # M3 regression snapshot (+ spawn '/' count)
py tools/debug/mp_full_load_check.py <arz>                     # M3 full-load corruption check

# Prove the default rebuild == deployed (byte-identity / determinism):
sha256sum work/SoulvizierClassic/Database/SoulvizierClassic.arz   # build27 -> 5014f1903aa4163adaeb8c35fd71ca8fe36db2a7293aa874932660619b600c8f
```
