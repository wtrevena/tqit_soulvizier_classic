# E/L Boss Integrity Audit - every Epic/Legendary-gated boss/hero (base + SV)

> **UPDATE (round 2, 2026-07-14): FIX-1 (Aniketos) IMPLEMENTED + dry-run verified.** See
> section 9. `docs_broken=0` still holds; `merge_dropped` is now `restored=1, still_broken=0`.
> Map-side change only (`tools/build_section_surgery.py` `ANIKETOS_SPECS`), no DB-record touched,
> no heavy build run (per standing concurrency constraint) - the integrator's next real map build
> will carry this change; Will confirms in-game on a FRESH Epic DEV2 char per the save-baking
> caveat (section 6).

Read-only audit. NO fixes applied (round 1). Worktree `feat/el-boss-audit` @ `e993a33` (build40-dev).
Builds on b51 (Arachne's Shame proved intact); extends it to (a) the freshest **build40** arz,
(b) **base-game** E/L gates, and (c) the **map-placement-drop** dimension b51 did not cover.

## TL;DR / VERDICT

- **DB spawn-chain half is CLEAN.** Every Epic/Legendary-gated boss/hero in base + SV still
  spawns at runtime. Across the **full** E/L proxy universe (SV098: 811 proxies / 37 Boss-Hero-Quest
  E/L member-slots; BASE: 791 proxies / 264 such slots) **0 members were lost, zeroed, declassed, or
  crowded out** by our DB edits. This confirms b51's build38 result and extends it to build40 + base.
- **Map half surfaced exactly ONE genuine drop: Aniketos.** A guaranteed E/L satyr **Hero**
  (`minobossproxy_aniketos`) that SV 0.98i places in **Greece / Area002 / Connector04.LVL** is
  **absent from our deployed + canonical maps**. Its DB chain (proxy + pool + monster + name tag) is
  fully present in our mod arz - only the **map object placement** was lost when SVAERA ported that
  base level. This is the exact "an E/L boss SV/base placed that our map merge lost entirely" class
  the brief flagged, and the same incomplete-port pattern as the boss arena / SVAERA prop drops.
- **Arachne's Shame + Chromatic Liche re-confirmed PRESENT** (DB + on-mesh placement) in the current
  build40 maps - both ride on **base-native** level placements that SVAERA preserved. Only Aniketos
  used an **SV-created-and-injected** proxy placement, which is why only it was dropped.
- **No DB-record fix is warranted** (0 DB-broken). The single fix is a **map-side placement
  restoration** for Aniketos (recipe in section 7).

### Gates
| metric | value |
|---|---|
| el_bosses_total (distinct E/L-gated boss identities: 3 SV-authored + 84 base/DLC) | 87 |
| present (DB chain + map placement both intact) | 86 -> **87 after round-2 fix** |
| db_broken | 0 |
| merge_dropped (round 1) | 1 (Aniketos) |
| **restored (round 2)** | **1 (Aniketos)** |
| **still_broken (round 2)** | **0** |
| fix_list | 1 (Aniketos placement restore - map-side) - **IMPLEMENTED, see sec 9** |

> Placement-level counting: 108 source gate-placements (proxy x logical-boss) swept in the DB layer,
> all 108 spawn-intact under the runtime overlay.

---

## 0. Ground truth + the runtime OVERLAY model (the key correction)

| artifact | path | identity |
|---|---|---|
| our built DB (build40) | `scratchpad/golden/arz.golden` | md5 `b33c5a44...` (the build40 arz) |
| base game DB | `.../Titan Quest Anniversary Edition/Database/database.arz` | 74,013 records |
| SV098 (design bible) | `upstream/soulvizier_098i/Database/database.arz` | 51,186 records |
| our deployed map | `work/SoulvizierClassic/Resources/Levels.arc` | 2282 levels |
| our canonical map | `local/Levels_merged.arc` | 2282 levels (== deployed for gate placements) |
| SVAERA base map | `reference_mods/SVAERA_customquest/.../Levels.arc` | 2235 levels |
| SV098 map | `upstream/soulvizier_098i/Resources/Levels.arc` | 1004 levels |
| base map | `.../Titan Quest Anniversary Edition/Resources/Levels.arc` | 2235 levels |

**The mod arz is an OVERLAY, not a replacement.** GOLDEN (build40) has **51,029** records - close to
SV098's footprint, NOT base's 74,013. It contains **near-zero DLC** records (xpack2=39, xpack3=9,
xpack4=5) because SV 0.98i predates all three expansions (SV098 xpack2/3/4 = 0/0/0). At runtime the
Custom-Quest mod arz is layered over the base game arz, so any record the mod does NOT ship
(Talos/Manticore/Hydra proxies, all Ragnarok/Atlantis/Eternal-Embers content) **resolves from the base
game unmodified = intact by pass-through**. Effective record = `GOLDEN if present else BASE`. Every DB
verdict below uses this overlay model. (A naive "is the record in the mod arz" check wrongly flags 96
DLC gates as missing; they are simply base pass-throughs.)

**Our world is the FULL AE campaign.** The merged map is SVAERA-derived and spans Greece(247),
Egypt(217), Orient(243), **Ragnarok(288)**, **Atlantis(258)**, **Eternal Embers(726)**, Olympus/Babylon,
plus the SV blood-cave/uber/bossarena areas (30/1/1). So **every base + DLC E/L gate is in-scope and
reachable**; DLC gate placements are inherited from the base/SVAERA world and their DB resolves via the
overlay. Spot-verified placed in our world: `x4_sq_204_huoshen`, `x4_sq_206_shen`, `hero_monster_scorcheddead`,
`x2bonus_fafnir`, `x4_sq_402_demonicelemental`.

---

## 1. Master list of E/L-gated bosses (the enumeration)

An **E/L gate** = a proxy whose Epic/Legendary pool slots introduce a Boss/Hero/Quest member that no
Normal pool contributes (by logical identity). This is the Arachne mechanism: Normal spawns trash (or
nothing), Epic/Legendary spawns the boss. The **difficulty-scaling** pattern (same boss as `_80`/`_83`/
`_86` records across all three difficulties) is NOT a gate and is excluded.

| origin | count | notes |
|---|---|---|
| SV-authored true gates | **3** | Arachne's Shame, Aniketos, Chromatic Liche |
| BASE classic-region gates | **5** | Talos, Manticore, Dragon Liche, Hydra (`bossproxy_2N` wild-reappear), Boareater (Pre-Tegea) |
| BASE DLC gates | **~84 identities / 105 proxies** | Ragnarok(1: Fafnir) + Atlantis + Eternal Embers main/side-quest bosses + AE roaming heroes (`x4hero_*`) |

**Gate mechanisms observed:**
- **Pool-slot gating (dominant):** `pool1` = trash/empty, `poolEpic1`/`poolLegendary1..N` = a boss pool.
  Talos: `pool1`=soldiers, `poolEpic1`/`poolLegendary1`=`bosspool_21_talos`. Hydra: Normal+Epic empty,
  `poolLegendary1`=`bosspool_24_hydra` (**Legendary-only**). Arachne + Aniketos: **no `pool1` at all**,
  `poolEpic1`/`poolLegendary1`=guaranteed single-member boss pool.
- **Chance-in-Epic-pool:** Chromatic Liche is `name10 @ weight4` inside the Epic liche pool
  `e_liche_01_general01` (absent from the 9-member Normal pool `liche_01_general01`).
- **`difficultyLimitsFile` window:** every gate proxy carries one (`HeroLimit_All`, `Limit_AreaNNN`,
  `limit_quest`); none were found to clamp a classic gate out of Epic in our build.

### The 3 SV-authored gates (highest relevance - the mod's reason to exist)

| boss | monster record | gate proxy | mechanism | placed by SV098 in |
|---|---|---|---|---|
| **Arachne's Shame** (Boss, guaranteed) | `typhon\spiderblackwidow01` (tagBlackWidow) | `jg06_arachnospool - poisonspring c` | `poolEpic1`/`poolLegendary1..3` = `JG06_Arachnos_PoolB` (spawnMin=max=1) | `Greece/Area003/UG_ArachnosUnderground/ArachnosUnderground01_Floor0` (**base-native placement**) |
| **Aniketos** (Hero, guaranteed) | `satyr\qm_aniketos_9/10/11` (tagNewHero33, charLvl 9/37/55) | `minobossproxy_aniketos` | pool1=none, `poolEpic1`/`poolLegendary1` = `minobosspool_02_aniketos` (spawnMin=max=1) | `Greece/Area002/Connector04.LVL` (**SV-created injection**) |
| **Chromatic Liche** (Hero, chance) | `um_chromaticliche_44` | 6x `ug_undead_liche_0{1,2,3}{n,t}` | `poolEpic1`=`e_Liche_0N_General01` adds `um_chromaticliche_44 @ w4` | `Orient/TyphonUG/Tomb*` (**base-native placements**) |

---

## 2. Per-boss classification table

| boss / group | record(s) | E/L gate | DB verdict | MAP verdict | overall |
|---|---|---|---|---|---|
| **Arachne's Shame** | spiderblackwidow01 / poisonspring c | Epic+Leg guaranteed | PRESENT (overlay; chain 0-diff vs SV098 per b51 + re-verified build40) | PRESENT (poisonspring c in ArachnosUnderground01_Floor0 in BASE/SV098/CANON/DEPLOY) | **PRESENT** |
| **Chromatic Liche** | um_chromaticliche_44 / ug_undead_liche_* | Epic chance (w4) | PRESENT (member resolves Hero, w4, in `e_liche_*`) | PRESENT (liche proxies in 4+ Orient TyphonUG tombs in DEPLOY) | **PRESENT** |
| **Aniketos** | qm_aniketos_9/10/11 / minobossproxy_aniketos | Epic+Leg guaranteed | PRESENT (proxy+pool+monster all in mod arz; spawn-intact) | **DROPPED** (SV098 places it in Connector04; SVAERA + our map do NOT; both have the level) | **MERGE-DROPPED** |
| **Talos** (wild-reappear) | boss_talos_44/47/50 / bossproxy_21_talos | pool1=soldiers, Epic+Leg=bosspool | PRESENT (SV overrides boss+pool; still Boss, w10, spawnMin1) | PRESENT - direct-probed `Greece/Knossos/KnossosCity01` (identical in BASE + DEPLOY) | **PRESENT** |
| **Manticore** | boss_manticore_50/53/56 / bossproxy_22_manticore | pool1=scorpos, Epic+Leg=bosspool | PRESENT (SV override, still Boss) | PRESENT - `Egypt/MiniDungeons/MantiocreFinale01` (BASE + DEPLOY) | **PRESENT** |
| **Dragon Liche** | boss_dragonliche_57/60/63 / bossproxy_23_dragonliche | Epic+Leg=bosspool | PRESENT (SV override, still Boss) | PRESENT - `Orient/Underground/RandomBamboo01Above` (BASE + DEPLOY) | **PRESENT** |
| **Hydra** | boss_hydra_60/63/66 / bossproxy_25_hydra | **Legendary-only** (Normal+Epic empty) | PRESENT (SV override, still Boss) | PRESENT - `Greece/Athens/Area02_Athens01` (BASE + DEPLOY) | **PRESENT** |
| **Boareater** | um_boareater_40/42/44 / ss_pretegea_arachnos_melee d | pool3=dead boar, Epic=`qs_boarsnatcher` | PRESENT (base pass-through) | PRESENT - `Greece/Area003/PineForest04` + `Greece/MiniDungeons/SpartaOptCave03` (BASE + DEPLOY) | **PRESENT** |
| **Ragnarok - Fafnir** | fafnir_47/50/53 / x2bonus_fafnir | Legendary-only bonus boss | PRESENT (base overlay) | PRESENT (`XPack2\Levels\WildLands\Underground\FafnirsCave`) | **PRESENT** |
| **Eternal Embers main-quest bosses** (~29 proxies) | x4_mqjc/je* (Qiongqi, Sihai Longwang, Sun, Akhenaten, Zazamankh, terracotta...) | quest E/L difficulty stages | PRESENT (base overlay, 0-lost sweep) | PRESENT (placed in `XPack4/Levels/*`) | **PRESENT** |
| **Eternal Embers side-quest bosses** (~32 proxies) | x4_sq* (Ghost Pirate Captain, Fahai, Sanshou, Gorilla Shaman, Huoshen, Sun's Champion, Shen, Exhumed Medjai, Colossal Scorpion, Yaoguai, Demonic Elemental...) | quest E/L | PRESENT (base overlay) | PRESENT (`XPack4/Levels/*`) | **PRESENT** |
| **AE roaming heroes** (~43 `x4hero_*`) | scorcheddead, kemal, ganthere, sesketesh, xennu, narsas, shah, saixi, nemethika, broodgard, ardeth, nythri, ... | Legendary-only / random-inject | PRESENT (base overlay, 0-lost) | PRESENT-via-DB (AE random-hero injection, not fixed level placement - see note) | **PRESENT** |

Note on `x4hero_*`: these Eternal-Embers heroes use the AE **random-hero injection** proxy system
(`hero_monster_*` / `special_zz_random_at`), not fixed level-object placement, so map-blob presence is
not the right check for them; their DB chain is confirmed intact under the overlay (0-lost), and the
injection mechanism is inherited unchanged from base.

---

## 3. DB dimension - exhaustive, 0 broken (extends + confirms b51)

**Overlay sweep over every source gate-placement (SV098 + BASE):**
`108 gate-placements -> 108 PRESENT, 0 DB-BROKEN.` Each was walked in the effective `GOLDEN-over-BASE`
DB: the gated boss member still resolves in the proxy's Epic/Legendary pool as Boss/Hero/Quest with
`weight>0` and `spawnMin>=1`.

**The only chains our mod arz OVERRIDES (the real risk surface) - all non-breaking:**
GOLDEN ships its own version of 12 gate-chains (SV re-skins of the base wild-reappear bosses + the 3 SV
gates): `BossPool_21_Talos`+`boss_talos_44/47/50`, `BossPool_22_Manticore`+`boss_manticore_*`,
`BossPool_23_DragonLiche`+`boss_dragonliche_*`, `BossPool_24_Hydra`+`boss_hydra_*`,
`JG06_Arachnos_PoolB`+`spiderblackwidow01`, `minobosspool_02_aniketos`+`qm_aniketos_*`,
`e_Liche_0N_General01`+`um_chromaticliche_44`. Every one keeps `monsterClassification` Boss/Hero,
`spawnMin/Max`, `weight`, and pool membership that still yields the boss on E/L. (Arachne's chain was
byte-diffed 0-spawn-relevant-diffs by b51; re-verified here on build40.)

**Full-universe cross-check of b51's "809" sweep, on build40, under the overlay:**
- **SV098:** 811 E/L proxies; 21 carry a Boss/Hero/Quest E/L member; 37 member-slots -> **0 lost/declassed**.
- **BASE:** 791 E/L proxies; 138 carry a Boss/Hero/Quest E/L member; 264 member-slots -> **0 lost/declassed**.

This directly reproduces and confirms b51's build38 finding ("0 proxies lost a boss/hero/quest member")
on the current build40, and **extends it to the entire base-game E/L proxy set** (264 base member-slots,
0 lost) - the half b51 did not cover. The intentional global spawn ops (Enslaver x600 roaming sweep,
coldworm champion injection) only **ADD** roamers/champions to trash packs; they remove nothing.

---

## 4. MAP dimension - our merge dropped 0 vs SVAERA; 1 SV placement lost in the port

Placement was scanned by extracting every `records\...\*.dbr` reference from all level blobs of all 5
maps and intersecting with the gate-proxy set, then confirmed with direct byte-needle probes
(replicating b51's method) for the notable cases.

- **`SVAERA placed -> OUR_DEPLOY`: 0 dropped.** Our SVAERA-based merge preserved **100%** of the gate
  placements SVAERA carries (99/99). `OUR_CANON` == `OUR_DEPLOY` (0 difference).
- **`BASE placed -> OUR_DEPLOY`: only 2 absent, both DLC pass-through artifacts, none classic-region.**
  Every classic-region base gate placement is present.
- **`SV098 placed -> OUR_DEPLOY`: 1 absent = `minobossproxy_aniketos`.** The other 7 SV gate proxies
  (Arachne's `poisonspring c`; 6x `ug_undead_liche_*`) are present because they are **base-native**
  placements SVAERA preserved. Aniketos is the sole **SV-created injected** placement, and it was lost.
- **The 5 classic base gates were direct-probed identical in BASE and OUR_DEPLOY:** Talos
  (`Greece/Knossos/KnossosCity01`), Manticore (`Egypt/MiniDungeons/MantiocreFinale01`), Dragon Liche
  (`Orient/Underground/RandomBamboo01Above`), Hydra (`Greece/Athens/Area02_Athens01`), Boareater
  (`Greece/Area003/PineForest04` + `Greece/MiniDungeons/SpartaOptCave03`). All present, same levels.

> Method note: the bulk `records\...dbr` extraction produced **false negatives** for a few
> space/format-quirked proxy paths (Arachne's `poisonspring c`, `bossproxy_21_talos`,
> `bossproxy_23_dragonliche`, `bossproxy_25_hydra`). These were each re-checked with direct
> case-insensitive byte-needle probes (b51's method), which are authoritative; every one is in fact
> PRESENT. The cross-map **set-difference** conclusions (0 dropped vs SVAERA; Aniketos the lone SV
> drop) are unaffected because identically-encoded blobs match-or-miss uniformly across all maps.

**Aniketos, proven from the data (not from a save):**
- SV098 `Levels/World/Greece/Area002/Connector04.LVL` blob references `minobossproxy_aniketos` (1 level).
- The identical-named level exists in SVAERA and in our DEPLOY/CANON maps, but **neither references
  aniketos anywhere** (`aniketos` needle = 0 levels in SVAERA and in OUR_DEPLOY).
- Base has **no** `qm_aniketos` records and **no** aniketos placement - this is purely SV content.
- The DB chain IS in our mod arz: `minobossproxy_aniketos` (pool1=none, poolEpic1=poolLegendary1=
  `minobosspool_02_aniketos`), pool members `satyr\qm_aniketos_9/10/11` (Hero, charLvl 9/37/55,
  `description=tagNewHero33`), `difficultyLimitsFile=herolimit_all`. spawnMin=max=1 -> guaranteed one
  Aniketos on Epic + Legendary, none on Normal - the Arachne pattern exactly.

Conclusion: on Epic/Legendary the intended guaranteed Aniketos never spawns in our build, because the
SVAERA port of Connector04 did not carry SV's injected proxy object and our merge inherited the gap.

---

## 5. Cross-check vs b51 (reconciliation)

- b51 proved **Arachne's Shame** intact (DB + map) at build38; **re-confirmed here at build40** (chain
  overridden but spawn-identical; placement present in DEPLOY + CANON).
- b51 swept 809/811 SV098 E/L proxies and found 0 guaranteed hero pools broken; **reproduced on build40
  (0 lost) and extended to all 791 base E/L proxies (0 lost).**
- b51 did NOT classify **Aniketos** or **Chromatic Liche** (its filter was "strict single-member
  guaranteed pool"; Aniketos' pool has 3 difficulty records, Chromatic Liche is a chance member). This
  audit adds both: Chromatic Liche PRESENT, **Aniketos MERGE-DROPPED**.
- b51 did NOT cover the map-placement-drop dimension; this audit does, and it is where the one real
  defect lives.

---

## 6. SAVE-BAKING CAVEAT (must state)

TQ bakes per-visited-area monster spawns into the character save at first visit; non-resetting areas do
not re-roll. Will's `_Toxeus` explored at older build rates, so **absence on his save is NOT proof of a
real drop** - which is exactly why every finding here is proven from the **static data** (the spawn
chain in the arz and the object placement in the map), independent of any save. The one action item
(Aniketos) must be confirmed by Will on a **FRESH Epic DEV2 character** that has never entered Greece
Area002 Connector04 on Epic. Arachne's earlier "absence" was this save-baking artifact, not a defect
(b51); nothing in this audit contradicts that.

---

## 7. FIX LIST (ranked) - 1 item, map-side restoration only

**No DB-record fix is warranted (db_broken = 0).** The single genuine defect is a lost map placement.

### FIX-1 (only item) - restore Aniketos's guaranteed E/L placement in Greece Area002

- **Class:** MERGE-DROPPED (SVAERA-port drop of an SV-created injected placement). Restoring a
  genuinely dropped spawn is explicitly permitted (not an SV design mutation - the DB design records
  are untouched and already present).
- **Root cause:** our world uses SVAERA's base-native `Greece/Area002/Connector04.LVL`, which never
  carried SV098's injected `minobossproxy_aniketos` object. DB chain is present; only the placement is
  missing.
- **Recipe (map-side, no DB change):**
  1. Read SV098's `Connector04.LVL` blob (`upstream/soulvizier_098i/.../Levels.arc`); locate the placed
     `records\proxies boss\boss\minobossproxy_aniketos.dbr` object and capture its position/orientation
     (and any spawn group linkage) via `qst_format`/level-object tooling used by `build_section_surgery.py`.
  2. Inject that single object into our `Greece/Area002/Connector04.LVL` via
     `build_section_surgery.py` INJECT_SPECS (same mechanism that restored the widow letter / Tantalus /
     other SVAERA prop drops). Keep it on-mesh (Connector04 is a walkable base level; verify the SV
     coordinate lands inside our copy's navmesh, no grid-shift applies to base levels).
  3. **Dry-run replay:** inject into a COPY of the level blob, blob-diff to confirm only the object list
     changed and the navmesh (0x0b) is byte-identical; confirm the proxy path now resolves against the
     mod arz record. NO full map build (the integrator batches this into the next real build).
- **Verify:** Will on a FRESH Epic DEV2 char walks Greece Act 2 / Connector04 (restart Steam+TQ first,
  hash-verify the deploy landed) and confirms the Aniketos satyr hero spawns; then Legendary.
- **Open question for Will:** confirm the SV Aniketos guaranteed E/L encounter is wanted (its DB records
  were carried into the mod, implying yes; this only restores the map object SV originally placed).

---

## 8. Appendix - evidence artifacts (scratchpad, read-only probes)

- `elib.py` - shared arz loader + case-insensitive resolver + proxy->pool->monster walker.
- `el_enum.py` / `el_enum2.py` -> `el_master.json` / `el_truegates.json` - E/L proxy enumeration; true-gate
  (Arachne-class) vs difficulty-scaling separation.
- `el_dump.py` - per-proxy pool/member/classification dumps (Talos, Manticore, Hydra, Arachne, Aniketos, liche).
- `el_db2.py` -> `el_db2_result.json` - overlay `GOLDEN-over-BASE` DB sweep: 108/108 present, 0 broken,
  12 overridden chains verified. (`el_db.py` = the superseded replacement-semantics run kept for the record.)
- `el_809.py` - b51's 809-proxy sibling sweep reproduced on build40 + extended to base: SV098 0-lost, BASE 0-lost.
- `el_map.py` -> `el_map_result.json` + `el_map_analyze.py` - 5-map placement scan + set-difference fate analysis.
- `el_probe_arachne.py` - direct byte-needle placement probe (Arachne present; Aniketos absent; liche present).
- `el_scope.py` - our-world region histogram (full AE campaign) + Aniketos deep-dive + SVAERA placement check.
- `el_ani.py` - Aniketos identity (satyr Hero, qm_aniketos, tagNewHero33, guaranteed E/L pool) + base absence.
- `el_split.py` - base classic-region (5) vs DLC (105) gate split.

---

## 9. FIX IMPLEMENTED (round 2, 2026-07-14) - Aniketos placement restored

**Scope discipline:** ONLY the one merge-dropped item (Aniketos) was touched. Every PRESENT boss
from section 2 (Arachne's Shame, Chromatic Liche, Talos, Manticore, Dragon Liche, Hydra, Boareater,
all DLC gates) is byte-untouched - verified below (the change is confined to exactly one level
blob's 0x05 section).

### 9.1 Extraction (evidence, read-only)

Parsed SV098's own `Levels/World/Greece/Area002/Connector04.LVL` blob (v0x0e) 0x05 section directly
(`scratchpad/ani_extract.py`, byte-level, no tooling assumptions). Found exactly 1 aniketos
instance:

| field | value |
|---|---|
| dbr | `records\proxies boss\boss\minobossproxy_aniketos.dbr` |
| local position (x,y,z) | `(85.79340362548828, 36.15501403808594, 113.24531555175781)` |
| rotation (flat 3x3, SV-exact) | `(0.79155, 0, -0.61111, 0, 1, 0, 0.61111, 0, 0.79155)` (~-77.6deg yaw) |
| flags | `0` (no UniqueId block) |

**Grid-corner identity check (critical - determines whether the coordinate transposes directly):**
Connector04's `ints_raw` grid corner is **`(-6740, -23, -200)`, IDENTICAL** across SV098, SVAERA,
BASE, and both our maps (OUR_CANON/OUR_DEPLOY). The level is **not** in `svaera_plus_portals.GRID_SHIFT`
(unshifted, native AE level) - so SV098's local coordinate applies verbatim to our world's copy of
the level with no re-derivation or frame correction.

**Blob version:** SV098's copy is v0x0e (56-byte records); SVAERA/BASE/our world's copy is **v0x11**
(72-byte records, base=72) - matching the `inject_into_0x05_v11` path already proven by the build36
uberboss placements (Dorus/Tantalus/GoldenBough/Mnemophage/Ephialtes all route through the same
function on the same native-AE-v0x11 mechanism).

### 9.2 On-mesh survey (built map's own 0x0b, `tools/debug/survey_uberboss_spots.py`)

Point `local(85.79,113.25)` ext=3.5 on the deployed build40 `Connector04.lvl` navmesh:

```
N:d=0.10/clr=88%  E:d=0.10/clr=86%  L:d=0.10/clr=83%  comp#2/60617
```

On-mesh in all 3 tilesets (d=0.10u), good clearance (83-88%, in the same range as other shipped
uberboss spots e.g. Golden Bough's accepted 82%-Legendary forecourt). The one flag: it lands in
set-0 connected-component **rank 2** (60,617 cells), not rank 1 (148,438 cells) - the survey tool's
default gate treats rank!=1 as a "CHECK" (isolated-island risk).

**Investigated and cleared (`scratchpad/ani_comp_check.py`):** component #2 is NOT a tiny
unreachable island - it is the level's second-largest walkable region, and it is **already home to
a full native monster-camp cluster**: 6 native `MC_FortWal`/`MC_FortTor`/`MC_WeaponRack` instances
(base-game content, untouched by any of our edits) sit in this exact same component, 5-20u from the
Aniketos spot. A vanilla monster camp already thrives there, so the area is unambiguously reachable
in-game; the rank-2 read is an artifact of this survey's simplified height-adjacency component model
(elevation/ramp connectivity that the stock engine's real Detour navmesh polygons handle natively,
which this offline height-delta approximation doesn't fully capture - the same caveat noted for
other elevated outdoor sub-areas). Thematically fitting too: a lone satyr hero holed up near a
fortified monster encampment. **No coordinate nudge applied** - this is SV's own exact placement,
and there is no ground-truth reason to move it off SV's authored spot.

### 9.3 Implementation

`tools/build_section_surgery.py`: added `ANIKETOS_HOST_KEY`, `Q_ANIKETOS_PROXY_DBR`,
`Q_ANIKETOS_ROT`, `ANIKETOS_SPECS = {ANIKETOS_HOST_KEY: [(Q_ANIKETOS_PROXY_DBR, x, y, z, {'rot':
Q_ANIKETOS_ROT})]}`, merged into `INJECT_SPECS` with the same collision-guarded-assert pattern as
every other canonical boss fold (UBERBOSS_SPECS/B41_SPECS/BROODNEST_SPECS). Because Connector04
carries no `drxmap` content it is not an `sv_shared_drx` surgery pair; it is a plain native-AE host,
so it flows through `svaera_plus_portals.py`'s generic `ae_inject_keys` loop (the same v0x11 branch
already proven for the 5 build36 uberbosses) with **zero new wiring** required - the existing
build pipeline picks up the new `INJECT_SPECS` entry automatically on the next map build. No DB
record was created, modified, or touched (`minobossproxy_aniketos` + its pool + monster records
already exist in the mod arz, confirmed intact in round 1).

### 9.4 Verify (dry-run injection into a COPY of the blob, `scratchpad/ani_dryrun.py`)

Ran the exact production code path (`bss.inject_into_0x05_v11`) against a COPY of the real
Connector04.LVL blob pulled from BOTH the deployed (`work/SoulvizierClassic/Resources/Levels.arc`)
and canonical (`local/Levels_merged.arc`) maps - no file on disk was written.

| check | result |
|---|---|
| blob length delta | +128 B (55->56 strings table entry + 1 new 72-byte unflagged instance) |
| section 0x05 (objects) | CHANGED (expected) |
| section 0x06 (descriptors) | **byte-identical** |
| section 0x0b (navmesh/RLTD) | **byte-identical** |
| section 0x14 (metadata) | **byte-identical** |
| section 0x17 (region/env header) | **byte-identical** |
| 0x05 string count | 55 -> 56 (+1, the new dbr path) |
| 0x05 instance count | 212 -> 213 (+1) |
| new instance resolves to | `records\proxies boss\boss\minobossproxy_aniketos.dbr` at `(85.793,36.155,113.245)`, flags=0 |
| append-only proof | the ENTIRE new instance-block byte string starts with the old one verbatim, +72 trailing bytes (the one new unflagged v0x11 record) - **every native instance byte-unchanged** |
| result identical for OUR_DEPLOY and OUR_CANON | **yes** (same level, same fix) |

Confirms: only the ONE intended level's 0x05 section changes; navmesh, descriptors, region header,
and every other of the map's ~2282 level blobs are untouched; every pre-existing native instance in
Connector04 (including the 5 monster-camp scenery/proxy anchors used for the frame calibration) is
preserved byte-for-byte; the new instance is exactly the SV098-sourced Aniketos proxy at SV's exact
coordinate and orientation. QUESTS(0x1b) 256-window parity is untouched (this is a pure per-level
0x05 append; it does not reach the world-level QUESTS section at all).

### 9.5 Gates

- `py_compile tools/build_section_surgery.py`: PASS.
- `tools/patches/_check_registry.py`: PASS (`13 module(s)`, unaffected - map-only change).
- `python -c "import build_section_surgery"`: loads clean, `ANIKETOS_HOST_KEY in INJECT_SPECS` ==
  True, no assertion/collision error (confirms the collision-guard passed for real, not just in
  isolation).
- Containment: the injected proxy is the ONLY new object in Connector04, placed at SV's own
  in-bounds coordinate inside that level's own grid corner - no cross-level leakage possible (the
  spec dict key IS the host level).

### 9.6 Deploy note

Map-side content change, one level blob (`Connector04.lvl`), zero DB delta. Ships in the wave that
next runs `tools/svaera_plus_portals.py` (both canonical and TESTHUB variants pick it up
automatically via the shared `INJECT_SPECS` dict - no TESTHUB-only gating needed, this is shipped
content like the other uberbosses). Per the save-baking caveat (section 6), Will must confirm on a
**FRESH Epic DEV2 character** that has never entered Greece Area002 Connector04 on Epic - restart
Steam + TQ first, hash-verify the deploy landed, then walk to the fortified monster camp on the east
side of Connector04 (Greece Act 1, past Helos) and confirm Aniketos the satyr hero now spawns
guaranteed on Epic (and again on Legendary).
