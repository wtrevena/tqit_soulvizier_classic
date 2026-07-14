# Build-Speed RCA + Hotspot Report (read-only profiling, no full builds)

**Agent:** build-speed RCA. **Date:** 2026-07-14. **Base:** main `d8485fe`, worktree `feat/build-speed-infra`.
**Rule:** every optimization below MUST produce byte-identical output (same arz/Levels.arc md5). Each is a
PERF change only. Determinism (`PYTHONHASHSEED=0`), the QUESTS 256-window, and navmesh byte-identity are
preserved by every item here.

**Method:** read the build code paths + measured 3 targeted micro-probes on COPIES of existing artifacts
(no full `build_svc_database.py` / `svaera_plus_portals.py` run - build40 was building concurrently).
Probes committed at `docs/reports/build_speed_probes/` (reproducible, read-only). This report also folds in
+ verifies the prior DB-only scoping spec (`build_speed_infra_spec.md`); its DB findings hold, and this adds
the MAP-build analysis it did not cover.

---

## TL;DR - the three hotspots

| # | Hotspot | Where | Cost (measured/est) | Fix | Byte-risk |
|---|---|---|---|---|---|
| 1 | **arz serializer O(n²)** string-table concat | `arz_patcher.py:314-316` | **81.15 s MEASURED** / DB build | 3-line `bytearray` | **NONE - proven identical** |
| 2 | **DB re-does prefix + O(n²) helper rescans** every build | `build_svc_database.py` prefix + `apply_svc_patches.py` extended phase | ~77 s prefix (cacheable) + **~240 s** extended rescans (prior-spec measured) | snapshot cache + shared record index | low (md5-gated) |
| 3 | **Map re-merges + recompresses the full ~2 GB map** every build | `svaera_plus_portals.py:1701-1703` + `arc_patcher.py:166-175` | **59 s recompress MEASURED** (+~5 s load) | parallelize pack / incremental part-cache / reuse loaded base ARC | **NONE - proven identical** |

**Headline correction to the task's premise:** the map-merge *core* is only **~2 min** (dominated by the 59 s
zlib recompress), NOT 15 min. The cited "~15 min map build" wall-clock is dominated by steps OUTSIDE the merge
(navmesh generation if re-run ~213 s, + the bootstrap's Text/Quests/resource-ARC packaging). So "incremental map
injection" is a real but *secondary* lever; the single biggest DB lever remains the O(n²) helper rescans, and the
single cheapest universal win is the 3-line serializer fix (which helps every arz/arc write).

---

## HOTSPOT 1 - arz serializer O(n²) string-table (the 3-line byte-identical fix)

**Location:** `tools/arz_patcher.py`, `ArzDatabase.write_arz`, lines 314-316:

```python
st_data = struct.pack('<i', len(self.strings))   # <-- immutable bytes
for s in self.strings:                            # 143 k strings
    st_data += write_lp_string(s)                 # each += copies the whole growing buffer -> O(n²)
```

`struct.pack` returns immutable `bytes`; each `+=` allocates a new object and copies the entire growing
buffer. For 143 k strings that is ~143 k copies of an ever-larger buffer = quadratic. (`data_block` and
`record_table` in the same function are already `bytearray` - only `st_data` is the immutable accumulator.)

**MEASURED** (probe 1, real 143,043-string table from `local/DEV_arz_deployed_prev.arz`, 7.6 MB table):

```
OLD (bytes +=):        81.150 s
NEW (bytearray):        0.050 s
IDENTICAL BYTES: True   speedup: 1632x   saved/build: 81.1 s
```

**Fix (3 lines, byte-identical):**
```python
st_data = bytearray(struct.pack('<i', len(self.strings)))
for s in self.strings:
    st_data += write_lp_string(s)
st_data = bytes(st_data)
```

**Risk: NONE.** Output bytes proven identical (`st_old == st_new` -> True). This is the safest possible change.
**Speedup: -81 s per DB build** (~23 % of the ~346 s DB build), and it also speeds every other `write_arz`
caller (deploy-delta, dry-run replays). Ship first.

> Note: the prior spec estimated the full `write_arz` O(n²) at ~114-144 s; on THIS arz (143 k strings) the
> string-table loop alone measured 81 s. The remainder of `write_arz` (~record recompress at zlib L6) is real
> work and stays. So the serializer fix collapses write from ~130 s -> ~30-50 s, not to zero.

---

## HOTSPOT 2 - DB build re-does the prefix + O(n²) extended-phase rescans

Code-confirmed the build's phase structure in `build_svc_database.main()`:
`from_arz(sv098/sv09/sv041/base)` @3223-3255 -> SVAERA graft @3320/3379 -> `del base_db` @3412 ->
`create_uber_souls` @3415 **(snapshot boundary)** -> `apply_all_extended_patches` @3482 **(the heavy phase)** ->
`write_arz` @3537 (Hotspot 1 lives here) -> reload-heavy gates @3545/3595.

### 2a. Cacheable prefix (the "db_cache_target")
Every build reloads the 4 upstream/base arzs (51 k SV records + the ~74 k-record base game DB) and re-runs the
deterministic prefix assembly through `create_uber_souls` (~77 s per the prior spec's phase probes) BEFORE any
build-specific work. That prefix is a pure function of the 5 input arz md5s + the prefix env flags
(`SVC_GRAFT_SVAERA`, `SVC_RESTORE_DROPPED_NPCS`) + the prefix source files.

**Cache design (endorsed from the prior spec, §2):** snapshot (pickle) the assembled `ArzDatabase` state at the
@3415/@3482 boundary, keyed by `sha256(hashseed + prefix-env-fingerprint + 5 arz md5s + prefix source hashes)`;
a HIT skips load+prefix (~77 s -> ~16 s snapshot load). **Byte-safety:** the prior spec's probe 06 proved a
pickle round-trip of the db state is md5-identical; the binding acceptance gate is a cold-vs-warm full-build md5
equality (`tools/verify_cache_determinism.py`). Two correctness must-dos the prior spec's critic already nailed
and that MUST be honored: (1) put the prefix env flags in the key (a `SVC_GRAFT_SVAERA` flip is otherwise a
silent WRONG HIT); (2) re-arm the provenance module globals `apply_svc_patches._SV098I_ALL_PATHS/_SOUL_PATHS`
on a HIT (they gate soul-record bytes, not just tags).

### 2b. The bigger DB lever - O(n²) helper rescans in the extended phase (code-confirmed)
The ~322 s extended phase is dominated (~240 s, prior-spec measured) by full-DB rescans in leaf helpers called
per-target inside small loops. **Confirmed by code shape:**
* `_add_monster_to_pools` (`apply_svc_patches.py:3602`): `for name in db.record_names(): fields = db.get_fields(name)`
  - a full 50 k-record × all-field scan, called ~40× across the placement passes.
* `_find_record` (`:3666`, substring `if sl in name.lower()`): full `record_names()` rescan + re-lowercase per
  call, called inside 50 k-record loops (e.g. `_verify_soul_itemskill_activation` @6591) = O(n²).
* ~a dozen more `for name in db.record_names(): db.get_fields(name)` full scans (1174, 1228, 1458, 1661, 3212,
  3739, 3866, 3928, 4130, 7772, 8447 ...).

**Fix:** a shared record index (built once, invalidated on mutation) in a common helper - the prior spec's §4.2.
**Two byte-safety traps (both real, honor them):** (i) the live `_find_record` is a **substring** search, so an
exact-match name dict does NOT accelerate it and would CHANGE results - the safe win is caching
`record_names()` + a parallel lowered list, preserving first-match order; (ii) index invalidation must be
**mutation-based**, not record-COUNT-based (`_add_monster_to_pools` mutates fields of existing records without
changing the count). Also note the **shadowed dual `_find_record`** (exact @294 + substring @3666): a module
split's `import *` would silently rebind callers - de-shadow first (prior spec §3.3 PR-0).

**Speedup (DB, prior-spec measured baseline):** serializer (-81 s) + helper index (-240 s) takes cold DB
~346 s -> ~90-110 s; + snapshot cache (-60 s prefix on a HIT) -> ~60-80 s incremental. The gates also reload the
55 MB arz + 63 MB base 4× (~86 s) - passing the in-memory db to the in-process validators reclaims ~45 s (§4.3).

---

## HOTSPOT 3 - map merge always re-merges + recompresses the full ~2 GB map

### What the map build actually does (code-confirmed, `svaera_plus_portals.main()`)
1. Load base SVAERA `Levels.arc` and decompress `world01.map` (@814-815); load SV map (@828-829).
2. Merge GROUPS/SD/QUESTS/BITMAPS + patch a few hundred `sv_only` + `ae_patched_blobs` levels (all the
   full-2282 loops @1468/1505/1540/1576 are `if lv_key in SPECS`-guarded - cheap dict lookups, blob work only
   for the 1-72 matched levels). Navmeshes are **read from cached donor files** (`local/editor_normalized/*.0b.bin`)
   and injected as byte ops - `gen_bc_navmeshes.py` is a SEPARATE ~213 s pre-step, NOT run here.
3. Rebuild the DATA section from scratch: concat ALL ~2282 level blobs into one `bytearray` (@1610-1632, O(n),
   fast) -> assemble the ~2 GB `world01.map` (@1669-1682).
4. **`ArcArchive.from_file(svaera_path)` AGAIN @1701** (a redundant 2nd full 688 MB read+parse; the base ARC is
   already loaded at @814) -> **`set_file('world/world01.map', result)` @1702 recompresses the ENTIRE ~2 GB map**
   into fresh 256 KB zlib-L6 parts (`arc_patcher.py:166-175`) -> `write()` 688 MB @1703.

### MEASURED map-pack cost (probe 2, streamed over ALL 7993 real parts of `local/Levels_merged.arc`)
```
world01.map: 7993 parts  ->  decompresses to 1998 MB (~2 GB; hence the code's many "under 2GB" asserts)
DECOMPRESS (load side):   1998 MB in  5.1 s  (388 MB/s)
RECOMPRESS L6 (set_file):  1998 MB in 59.0 s  (34 MB/s)   compressed out 657 MB (ratio 0.329)
BYTE-IDENTITY: recompress(decompress(part)) == original for ALL 7993/7993 parts (0 differ)
```

**So the map-merge core is ~2 min:** ~5 s load-decompress + ~5-10 s Python merge + the redundant 2nd base-ARC
read + **59 s recompress** + write. The recompress is the single dominant op. The full re-merge is *forced*
because the pipeline unconditionally rebuilds the whole DATA section and recompresses every 256 KB part on every
run - there is no reuse of the prior build's compressed parts.

### Incremental / parallel feasibility (the "incremental_map_feasible" question)
The probe's **DIFFERING=0** result is the key enabler: zlib L6 here is deterministic, so
`recompress(decompress(part)) == part` for every part. That makes BOTH of these **provably byte-identical**:

1. **Parallelize the pack (BEST safe map lever, recommended).** The 7993 parts are independent; compress them
   with a `multiprocessing.Pool` over the 256 KB chunks. **59 s -> ~10-12 s on 6-8 cores. Byte-identical**
   (deterministic zlib, same chunk boundaries). Small, self-contained change to `arc_patcher.set_file` (or a
   parallel variant used by the map build). Highest map ROI, lowest risk.
2. **Incremental part-cache (secondary).** Keep the previous `Levels.arc`; for each 256 KB decompressed part,
   look up its hash in the previous build's part set and reuse the cached compressed bytes on a hit (skip zlib).
   Byte-identical by the DIFFERING=0 proof. **BUT** limited by an offset-shift cascade: level blobs are
   variable-length and appended, so a size-CHANGING blob edit shifts every downstream byte -> every downstream
   256 KB part boundary moves -> those parts all miss the cache. It pays off for size-PRESERVING edits (in-place
   field tweaks) and edits near the map's end; an entity-injection wave (the common case) mostly misses.
   Moderate ROI, moderate complexity - do it only after #1 if the pack is still hot.
3. **Free win: reuse the already-loaded `ae_arc`** instead of the 2nd `ArcArchive.from_file(svaera_path)` @1701
   (`ae_arc.set_file(...); ae_arc.write(...)`). Saves one 688 MB read + 7993-part parse. Byte-identical (same
   base entries). ~a few seconds + less memory.

### The honest 15-min gap (out of merge scope, could not time under build40)
The merge core is ~2 min; the cited ~15 min is dominated by steps I could not run: **navmesh generation**
(`gen_bc_navmeshes.py`, ~213 s, only needed when SV geometry changes - its donors are already cached to disk, so
a content build should SKIP it) and the **bootstrap** (`bootstrap_working_mod.ps1`: DB build + Text.arc + Quests
+ copying/stripping the resource `.arc` set). The real 15-min levers are orchestration: (a) don't re-run navmesh
gen when the donor cache is fresh; (b) don't rebuild/re-copy unchanged resource ARCs each iteration. These are
bootstrap-script fixes, out of this profiling scope, but they - not the serializer - are where the map wall-clock
actually goes.

---

## Recommended landing order (each independently shippable + md5-gated; integrator merges post-build40)

1. **Hotspot 1 - serializer `bytearray`** (`arz_patcher.py`, 3 lines, -81 s, zero risk). Universal; ship first.
2. **Hotspot 3 #1 - parallel pack** (`arc_patcher.set_file`, -47 s map, byte-identical) + **#3 reuse base ARC**.
3. **Hotspot 2b - shared record index** (extended phase, -240 s, md5-gated + mutation-sound invalidation).
4. **Hotspot 2a - prefix snapshot cache** (-60 s incremental; env-fingerprint + provenance re-arm mandatory).
5. **Gate de-dup** (in-memory db to validators, -45 s) ; **Hotspot 3 #2 incremental part-cache** (only if pack
   still hot after parallelizing).

**Estimated result:** DB ~346 s -> ~90 s cold / ~70 s incremental; map-merge core ~120 s -> ~60-65 s
(parallel pack + base-ARC reuse). Every step carries an `md5(new) == golden` acceptance gate - a single
differing byte means the optimization is wrong.

## Byte-identity gates each fix must pass before the integrator merges (post-build40, one clean full build)
* Hotspot 1 & 3: cold rebuild -> `md5(arz)` and `md5(Levels.arc)` == the build40 golden md5s.
* Hotspot 2: `tools/verify_cache_determinism.py` cold-vs-warm md5 equality + env-flag negative tests +
  `uber_soul_tags.txt` identical.
* Parallel pack: assert the parallel-compressed `Levels.arc` is byte-for-byte the serial output (the probe's
  DIFFERING=0 is the standing proof this holds).

---

# IMPLEMENTATION (round 1) - 2026-07-14, worktree `feat/build-speed-infra`

All three optimizations from the RCA are implemented and EACH is proven byte-identical on COPIES of real
artifacts (no full build was run - build40 owned the machine). Determinism (`PYTHONHASHSEED=0`), the QUESTS
256-window, and navmesh byte-identity are untouched by every change. Reproducible harnesses live in
`docs/reports/build_speed_probes/`.

| # | Change | Files | Default | Byte-proof (md5) | Speedup (measured) | Commit |
|---|---|---|---|---|---|---|
| 1 | serializer O(n^2) -> `bytearray` | `arz_patcher.py` | ON (always) | full arz `6631f252...` OLD==NEW | write_arz **83.48s -> 0.31s** (267x) | `9089c15` |
| 2a | parallel ARC pack (threads) | `arc_patcher.py` | ON above 64 parts | parts digest `a4f574dc...` serial==parallel | 75MB/300 parts **1.82s -> 0.30s = 6.08x** (8 thr); full map ~49s -> ~8s | `6c79e39` |
| 2b | reuse loaded base ARC | `svaera_plus_portals.py` | ON (always) | arc `d8adb5b7...` reuse==fresh | -1x 688 MB read + one archive copy | `6c79e39` |
| 3 | DB prefix snapshot cache | `prefix_cache.py`, `build_svc_database.py` | **OFF** (opt-in) | static `a9631b7b...` + CONTINUE `33b9b45b...` cold==warm | ~77 s prefix skipped on a HIT + lower mem peak | `44d69de` |

### 1. Serializer (`arz_patcher.write_arz`, HOTSPOT 1) - SHIPPED, always on
`st_data` was an immutable-`bytes` accumulator (`st_data += write_lp_string(s)`) over 143k strings = O(n^2);
now a `bytearray` + `bytes()` at the end. **Proof** (`verify_serializer.py`, run against git-OLD `d8485fe`
and the worktree-NEW module on `local/DEV_arz_deployed_prev.arz`, 51007 records / 143043 strings): both write
`md5 6631f25219be1b8f9874c95af68755c7` (55,340,923 B); full `write_arz` **83.476 s -> 0.313 s**. Zero risk,
universal (every arz write - DB build, deploy-delta, dry-run replays).

### 2. Map pack (HOTSPOT 3) - SHIPPED, byte-identical
* **Parallel pack:** `set_file`/`add_file` now compress the 256KB parts through `_pack_parts()`, which uses a
  `ThreadPoolExecutor` above a 64-part threshold. `zlib.compress` **releases the GIL**, so threads give real
  multi-core parallelism with byte-identical output and NO Windows spawn / multi-GB pickle cost (the reason
  threads, not processes). `SVC_ARC_PARALLEL` = unset/auto (parallel, `min(cpu,8)` threads) | `0`/off (serial,
  byte-identical fallback) | `N`. Text.arc/Quests.arc are below threshold -> unchanged serial path. **Proof**
  (`verify_map_pack.py`, real world01.map data): serial and parallel part-digests both `a4f574dc62b6b9893ab874c9a09ba3be`,
  75 MB/300 parts 1.822 s -> 0.300 s = 6.08x (8 threads).
* **Reuse base ARC:** `svaera_plus_portals` reuses `ae_arc` (already loaded + only read at the top of `main()`)
  for the final `set_file`+`write` instead of a 2nd 688 MB `from_file`. **Proof** (`verify_map_pack.py` TEST B):
  reuse and fresh-load both write `md5 d8adb5b7cf23ae43bdb3843bd2dbca19`.

### 3. DB prefix snapshot cache (HOTSPOT 2a) - SHIPPED, byte-identical-gated; DEFAULT-ON since 2026-07-14
Caches the assembled prefix state (after `create_uber_souls`, before `apply_all_extended_patches`) keyed by
every prefix input (see `prefix_cache.py` docstring: hashseed + prefix ENV flags + 5 arz md5s [svaera
conditional on graft] + whole-`tools/` source fingerprint). The prefix was extracted VERBATIM into
`_run_prefix()` (a sibling-function move with ZERO reindentation; the moved block's sha was asserted identical
by the transform). `main()` gained a thin cache boundary. Shipped **default OFF**; the default was flipped to
**ON 2026-07-14** after the full-build gate went green on main @ `7c38c9e` (cold 209s and warm 134s both md5
`b33c5a447f3a8ca652c14f78d4ad1dd4` == build40 GOLDEN; tags identical; warm HIT log-proven; graft-flip negative
test forced a key MISS). Opt out with `SVC_PREFIX_CACHE=0`; `SVC_NO_CACHE=1` hard-disables.
**Proofs** (`verify_cache_roundtrip.py`, no full build):
* static: direct `a9631b7b8b1dd7fdf70d3caa2a48aa56` == restore (IDENTICAL).
* **CONTINUE-path** (the one a static probe cannot give): restored mid-state + identical further mutation
  writes `33b9b45bc0a794b4cc3dd04c904f3dee` == the never-pickled db (IDENTICAL).
* real `store()`/`load()` disk round-trip (atomic write + key verify): db-identical, side-outputs OK.
* key logic: 8/8 (env flags + input md5 + source fp all move the key; `SVC_RELEASE_DROPS` does NOT; svaera md5
  matters only when graft on).

The FINAL acceptance gate is `tools/verify_cache_determinism.py` (cold-vs-warm FULL-build md5 + tags + a
graft-flip negative test); it ran clean on main @ `7c38c9e` (2026-07-14) and the default is now ON (evidence
above and in `docs/BACKLOG.md` build-speed entry). **Honest hit-rate caveat:** the key includes the churny
`apply_svc_patches` (via the whole-`tools/` fingerprint - the sound choice absent the module split), so editing
DB content is a MISS; the cache HITs on prefix-invariant rebuilds and always removes the 4-DB memory
co-residence on a HIT. Widening the hit set needs the prior-spec module split (S3.6, out of this scope).

### Incremental map blob-injection - DESIGN ONLY (not shipped), and why
The RCA reframed the task's "incremental map injection": true per-blob incremental injection into a cached
merged map is byte-identical-PROVEN (RCA `probe_pack`: `recompress(decompress(part)) == part` for all
7993/7993 parts) but **limited by an offset-shift cascade** - level blobs are variable-length and appended, so
a size-CHANGING edit (entity injection, the common map wave) shifts every downstream byte -> every downstream
256KB part boundary moves -> those parts miss a part-cache. It pays off only for size-PRESERVING edits and
edits near the map's end. Rather than ship a cache that risks a differing byte on the common case, round 1
ships the **parallel pack** (always byte-identical, always helps: ~49s -> ~8s) + **base-ARC reuse**, which
capture the same wall-clock (the 59 s recompress was the dominant map-merge op) with zero byte-risk. A
size-preserving part-cache is documented in the RCA (Hotspot 3 #2) as an optional follow-up after the pack.
Note (RCA headline): the cited "~15 min map build" is dominated by navmesh generation (a separate ~213 s
cached pre-step, NOT re-run by the merge) + the bootstrap resource/Text/Quests packaging - orchestration
levers out of this serializer/pack scope.

### Reproduce (benchmark note)
All harnesses are read-only vs the repo (scratch outputs only), memory-light, and print their own md5s +
timings. Run with `PYTHONHASHSEED=0 PYTHONIOENCODING=utf-8`; arz/arc inputs live in the MAIN repo `local/`
(gitignored - not in the worktree), so pass absolute paths.
```
# 1. serializer: OLD vs NEW full-arz md5 (identical) + write time
py docs/reports/build_speed_probes/verify_serializer.py <git-old arz_patcher.py> <a.arz> <out.arz>
py docs/reports/build_speed_probes/verify_serializer.py tools/arz_patcher.py <a.arz> <out.arz>
# 2. map: parallel==serial (byte-identical) + speedup, and reuse==fresh
py docs/reports/build_speed_probes/verify_map_pack.py 300 <scratch_dir>
# 3. DB cache: static + CONTINUE-path + store/load + key-logic byte proofs
py docs/reports/build_speed_probes/verify_cache_roundtrip.py <a.arz> <scratch_dir>
# 3b. INTEGRATOR full-build acceptance gate (cold==warm md5); NOT under build40:
py tools/verify_cache_determinism.py <sv098.arz> <sv09.arz> <sv041.arz> <base.arz> <workdir>
```

### Integrator merge checklist (post-build40, one clean full build)
1. `py_compile` all changed files (done here). 2. Full cold build -> assert `md5(arz)` == the build40 golden
   arz md5 (serializer + parallel pack + base reuse are all byte-identical, so the golden must reproduce).
   3. Full map build -> assert `md5(Levels.arc)` == the build40 golden (parallel pack default-on; set
   `SVC_ARC_PARALLEL=0` to A/B the serial path if any doubt). 4. Run `verify_cache_determinism.py`; on PASS,
   flip the cache default to ON (change `enabled()` default or set `SVC_PREFIX_CACHE=1` in the build scripts).
