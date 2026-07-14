# B54 / B-SMOKE-1 Occult-Atmosphere RCA (2026-07-14)

**Agent:** OCCULT-ATMOSPHERE RCA (read-only forensics). **Scope (Will 2026-07-14, verbatim):**
"its not smoke on all merchant areas, just on the two added occultist merchant areas" =
EXACTLY 5 levels, nothing else:
- **(A) Greece occultist merchant area** = `hiddenvalley01` + `hiddenvalleyborder04`
- **(B) Delphi occultist region** = `delphilowlands02` + `delphilowlands03` + `delphilowlands04`

`gardenofmerchants` and every other level are OUT of scope (no injection anywhere Will did not flag).

---

## VERDICT (lead with the not-done vs done)

**There is NO remaining occult-smoke DATA defect in the shipped map.** Every SV occult
atmosphere entity is PRESENT at SV-exact coordinates, every FX record is byte-identical to
SV, every `.pfx` particle file is present and byte-identical to the known-good DRX/SVAERA
reference, and every texture those `.pfx` reference resolves. This is verified from THREE
independent artifacts: the SV 0.98i source, our canonical build40 (`work/`), **and the LIVE
Steam Workshop map Will actually plays**.

**Both data levers the 2026-07-08 note queued are moot:**
- **Lever (a) map-side "still-dropped SV Delphi entities":** REFUTED. The entities it named
  (`t1_pitspawner_01` x2, `t1_pitspawner_02`, `t1_lildude` x6, `soundobject_cageglow`, the
  Delphi `fog_occult_fx01`/`pit_fx`) are ALL PRESENT in the shipped map. The SVAERA base
  drops them, but the SV->SVAERA object merge restores them (no INJECT_SPECS needed).
- **Lever (b) DB-side "FX emission weakened vs SV":** REFUTED. `fog_occult_fx01`,
  `pit_fx01`, `pit_fx02`, `bugcloud_smallfx`, `occultistaura_fx01`, `cage_binding_fx01`, and
  both disciple auras are BYTE-IDENTICAL deployed-vs-SV (0 fields drifted).

Per the 2026-07-08 note's own stated fallback: *"If both come back SV-faithful, the residual
gap is engine-era rendering, not data."* Both came back SV-faithful. **B-SMOKE-1 is a
rendering/perception issue, not a content gap - the map fix list for smoke is EMPTY.**

The **only** in-scope atmosphere entity that is genuinely dropped is `blooddemon_medium01`
(the caged blood-demon NPC in delphilowlands04) - a Monster prop, **not a smoke emitter**.

---

## Artifacts (ground truth, hashes)

| Artifact | Path | md5 / note |
|---|---|---|
| SV 0.98i (DRX-integrated) Levels | `upstream/soulvizier_098i/Resources/Levels.arc` | v0x0e source; Delphi occult native |
| SVAERA base Levels | `reference_mods/SVAERA_customquest/Resources/Levels.arc` | the merge base |
| **build40 canonical** Levels | `work/SoulvizierClassic/Resources/Levels.arc` | `9981085b…` (== `local/Levels_merged.arc`) |
| **LIVE Workshop** Levels | `…/workshop/content/475150/3759792705/…/Levels.arc` | `60a62880…` (what Will plays) |
| build40 arz | `work/SoulvizierClassic/Database/SoulvizierClassic.arz` | `b33c5a44…` |
| SV arz | `upstream/soulvizier_098i/Database/database.arz` | FX source-of-truth |
| Deployed DRXeffects.arc | `work/SoulvizierClassic/Resources/DRXeffects.arc` | occult `.pfx` host |

Concurrency honored: NO heavy build run. All checks = read-only arc/arz reads + blob diffs
against COPIES of the deployed artifacts. Harness in `tools/debug/` (atmos_rca_lib.py +
atmos_classify.py + full_entity_diff.py + fx_diff.py + fx_probe.py + pfx_locate.py +
asset_resolve.py + pfx_bytecmp.py + delphi_3way.py + instance_bytes.py).

---

## 1. Atmosphere classification (SV vs build40, coord-matched within 0.6u)

is_atmo = inclusive superset (fog*/smoke*/*aura*/pit_fx*/*light*dyn/simple/stat*/totem/
firepit/pyre/cage*/pitspawner/lildude/vitstaff/soundobject*/bugcloud*/disciple/demon/…).

| Level | corner match | SV atmo | PRESENT | DROPPED | MOVED | ADDED (build40 > SV) |
|---|---|---:|---:|---:|---:|---:|
| hiddenvalley01 | yes (0,0,64) | 27 | 27 | 0 | 0 | 3 (fog_occult + 2 lights, new-fountain B1) |
| hiddenvalleyborder04 | yes (255,255,32) | 16 | 16 | 0 | 0 | 8 (pit-sprite scene + firepit, B2/C2) |
| delphilowlands02 | yes (0,0,64) | 46 | 46 | 0 | 0 | 1 (10mlight_stat_green) |
| delphilowlands03 | yes (0,0,64) | 7 | 7 | 0 | 0 | 0 |
| delphilowlands04 | yes (0,0,64) | 25 | 24 | **1** | 0 | 1 (10mlight_dynnl_orange) |
| **TOTAL (5 in-scope)** | | **121** | **120** | **1** | **0** | **13** |

The identical classification holds against the **LIVE Workshop map** (`60a62880`): 120
present / 1 dropped / 13 added - Will's installed map carries the full atmosphere.

The single DROPPED atmosphere instance:
- `records\drxmap\dress\blooddemon_medium01.dbr` @ delphilowlands04 SV-local
  **(1.967, 10.062, 12.120)** flags=0 - the caged blood-demon NPC. NOT smoke.

## 2. Delphi provenance (3-way: SV / SVAERA base / build40) - resolves the B-SPRITE-1 myth

The 2026-07-08 B-SPRITE-1 comment claims *"SVAERA dropped Delphi's sprites entirely, so this
injected HVBorder04 pit is the ONLY sprite pit in the whole mod."* That is **half true and
now outdated**: SVAERA drops them, but the merge restores them into build40.

| entity | SV | SVAERA | build40 |
|---|---:|---:|---:|
| delphilowlands02 fog_occult_fx01 | 3 | **0** | **3** |
| delphilowlands02 pit_fx01 / pit_fx02 | 1 / 1 | 0 / 0 | 1 / 1 |
| delphilowlands02 t1_pitspawner_01 / _02 | 2 / 1 | 0 / 0 | 2 / 1 |
| delphilowlands02 t1_lildude_01 / _02 | 4 / 2 | 0 / 0 | 4 / 2 |
| delphilowlands02 soundobject_cageglow | 1 | 0 | 1 |
| delphilowlands02 bugcloud_smallfx | 1 | 0 | 1 |
| delphilowlands02 TOTAL occult | 18 | **0** | **18** |
| delphilowlands03 TOTAL occult (lildude/vitstaff/bugcloud) | 7 | **0** | **7** |
| delphilowlands04 TOTAL occult (fog/cage/tent/tomes) | 19 | **1** | **18** |

Mechanism: `svaera_plus_portals.py` / `build_section_surgery.py` merge SV's drxmap 0x05
objects into SVAERA's blob (file docstring line 5-6: "MERGE SV's drxmap object strings into
SVAERA's 0x05 section (append only)"). There is **no** `delphilowlands0*` key in INJECT_SPECS
(that dedicated lever was removed as v0x11-crash-prone, line 1794) - and it is unnecessary,
because the merge already carries the scene. **Every entity 2026-07-08 flagged as "still
dropped" is present.** The instances are real and valid: fog_occult_fx01 @ delphilowlands02
carries flags=0 + identity rotation (rotdet=1.0000) + SV-exact position in both SV and build40.

## 3. DB / FX dimension (deployed vs SV, field-by-field)

`tools/debug/fx_diff.py` - every occult FX EffectEntity record is **BYTE-IDENTICAL** deployed
vs SV (0 emission/scale/color/lifetime fields drifted):

| FX record (Class=EffectEntity, Effect.tpl) | DEP vs SV | effectFile (.pfx) |
|---|---|---|
| `drxmap\effects\fog_occult_fx01.dbr` | identical | DRXeffects\other\occultfog.pfx |
| `drxmap\effects\pit_fx01.dbr` | identical | DRXeffects\other\pitfx.pfx |
| `drxmap\effects\pit_fx02.dbr` | identical | DRXeffects\other\pitfx2.pfx |
| `xpack\…\environment\bugcloud_smallfx.dbr` | identical | XPack\…\bugcloud_small.pfx |
| `drxmap\effects\occultistaura_fx01.dbr` | identical | DRXeffects\other\occult_aura.pfx |
| `drxmap\effects\cage_binding_fx01.dbr` | identical | DRXeffects\other\cage_binding.pfx |
| `…bloodwitch\…\fx_disciple_aura_eyechantment01/02.dbr` | identical | …blooddemon\disciple_eye.pfx |

**fx_records_drifted = 0.**

## 4. Asset dimension (.pfx + textures present in shipped arcs)

- All 6 occult `.pfx` are present in `DRXeffects.arc`; `bugcloud_small.pfx` in base
  `Effects.arc`. (asset_resolve.py, robust logical-path resolution.)
- All 11 textures those `.pfx` reference resolve: base `Effects.arc`
  (343smoke_01/02, 343spark_01, 343_crescentbolt_01, ring01/02, water,
  lightning_missile01b, particletest) + `DRXeffects.arc` (cage_binding_arcanesymbols).
- **Byte-identity vs known-good references (pfx_bytecmp.py):** every occult `.pfx` in our
  DEPLOYED arc is byte-identical (same md5, same size) to BOTH our **LIVE Workshop** copy AND
  the **SVAERA** Workshop copy (a shipping DRX-integrated mod). The particle systems are the
  genuine DRX assets - NOT nerfed same-name stubs.

  | .pfx | DEPLOYED | LIVE_WS | SVAERA | verdict |
  |---|---|---|---|---|
  | occultfog.pfx | 62f77750d6 / 1880B | = | = | DEP==LIVE==SVAERA |
  | pitfx.pfx | 2c1a9bb63d / 5425B | = | = | DEP==LIVE==SVAERA |
  | pitfx2.pfx | 8b44d50f00 / 5425B | = | = | DEP==LIVE==SVAERA |
  | occult_aura.pfx | b0a78c75d1 / 2874B | = | = | DEP==LIVE==SVAERA |
  | cage_binding.pfx | eed8d0ad4d / 5075B | = | = | DEP==LIVE==SVAERA |
  | disciple_eye.pfx | c0bca156f4 / 2854B | = | = | DEP==LIVE==SVAERA |

---

## FIX LIST

### A. SMOKE (the reported bug) - **EMPTY. No data action.**
No occult smoke/fog emitter is dropped, no FX record is drifted, no `.pfx`/texture is missing,
in either build40 or the live Workshop map. Injecting more smoke where the data is already
SV-faithful would be scope creep against Will's tight framing and is a vet NO-GO by default.

### B. Non-smoke occult-scene completeness (OPTIONAL, pending Will - NOT smoke)
These SV occult-*scene* props (furniture / caged demon / tent dressing) are dropped by the
merge. They do NOT emit smoke, so they are NOT the reported bug, but they make the occultist
areas read as fuller occult scenes. **Do not auto-apply** - Delphi (v0x11) 0x05 injection was
historically crash-prone (INJECT_SPECS line 1794); any restore must use the proven step-6/7
`inject_into_0x05_v11` path, on-mesh-surveyed, and one of the aggro items (blooddemon) needs a
standoff check. Nearest existing INJECT_SPECS host key = **NONE for Delphi** (no delphilowlands*
key exists; this is greenfield and carries the v0x11 crash risk).

| entity (SV-exact local coord) | host level | class / note |
|---|---|---|
| `drxmap\dress\blooddemon_medium01.dbr` (1.967,10.062,12.120) | delphilowlands04 | Monster (aggro) - the caged blood-demon; its cage + cage_binding_fx + soundobject already ship |
| `drxmap\dress\qi_tomeofhealing01.dbr` (10.172,11.449,1.147) | delphilowlands04 | Decoration - occult tent tome |
| `drxmap\dress\scrolls.dbr` (11.348,9.325,1.253) | delphilowlands04 | Decoration - occult tent scrolls |
| `xpack\scenerymedit\…\merchantvendortable01.dbr` (65.987,10.005,124.426) | delphilowlands02 | Decoration - occultist merchant's vendor table |

(delphilowlands03 also drops SV bones/corpses/cliff scenery; delphilowlands02 drops
Hades-debris/corpses/rocks/trees; none are occult-scene-defining - see full_entity_diff.py.)

### C. If Will still sees NO smoke after confirming his install is current
1. **First, confirm his installed map is build40+** (per the "restart Steam before every test"
   rule): the smoke IS in the live Workshop `Levels.arc` (`60a62880`) - if Steam served a
   stale copy or he tested pre-build40, that alone explains it. Hash-verify the loaded arc.
2. If the map is current and smoke is still absent, the residual is **engine-era particle
   rendering** of the DRX occult fog on stock TQAE (possibly the 32-bit particle budget /
   draw-distance culling), NOT data. Diagnose in-game (does ANY `occultfog.pfx`/`pitfx.pfx`
   render at HVBorder04, where the same records are present) - a render probe, not a data edit.
3. **Only if Will explicitly wants the areas "smokier than SV"** does a data lever exist, and
   it is the established C2/C4 precedent (Will's own "pit_fx01 alone is not enough" feedback):
   add fog_occult_fx01 DENSITY emphasis in the Delphi occult scenes to match the enhanced
   HVBorder04 cave-entrance scene. This is emphasis-beyond-SV, in-scope to the two flagged
   areas, and must ride the proven v0x11 injector with on-mesh surveys.

---

## GATES
- levels_swept = 5 (the two occultist-merchant areas only; gardenofmerchants untouched)
- instances_sv_total = 121 (SV atmosphere instances across the 5 in-scope levels)
- dropped_count = 1 (blooddemon_medium01 NPC; **0 smoke emitters dropped**)
- moved_count = 0
- fx_records_drifted = 0 (all occult FX records byte-identical deployed vs SV)
- delphi_lever_ever_shipped = TRUE (the Delphi occult entities are present in build40 AND the
  live Workshop map, restored via the SV->SVAERA merge; the dedicated INJECT_SPECS lever was
  never added and is unnecessary)

---

## FIX (implementer round 1, 2026-07-14) - NO DATA CHANGE. Both levers refuted a SECOND time.

Per the mandatory implement->vet loop, a fresh implementer independently RE-VERIFIED the RCA's
three gate numbers from the DEPLOYED artifacts (not trusting the RCA prose) before deciding
whether to inject anything. The verdict is unchanged and now doubly-sourced: **there is no
occult-smoke DATA defect to fix.** No `SMOKE_SPECS` were added to `INJECT_SPECS`; no `tools/patches/`
module was added; `0x09`/`0x17` were not touched (refuted lever). **The map/DB fix list is EMPTY.**

### Independent re-verification (round 1), from deployed artifacts

Read-only, no heavy build (concurrency honored). Harness: `tools/debug/full_entity_diff.py`,
`fx_diff.py`, and a direct occult-emitter instance dump.

**1. Exhaustive per-level 0x05 drop diff, SV vs DEPLOYED build40** (`work/.../Levels.arc`,
`full_entity_diff.py build40`) - this is the SUPERSET check, every dbr, not just the is_atmo heuristic:

| Level | SV inst | present | dropped | dropped = smoke emitter? |
|---|---:|---:|---:|---|
| hiddenvalley01 | 205 | 204 | 1 | NO (`orienttownsetdresstablegroup` - a table) |
| hiddenvalleyborder04 | 51 | 50 | 1 | NO (`seen_ocv2_trigger` - a gardenofmerchants zone trigger) |
| delphilowlands02 | 110 | 87 | 23 | NO (hades-debris/corpses/rocks/trees/`merchantvendortable01`/vase) |
| delphilowlands03 | 40 | 32 | 8 | NO (bones/corpses/cliff scenery) |
| delphilowlands04 | 219 | 204 | 15 | NO (trees/`blooddemon_medium01`/`qi_tomeofhealing01`/`scrolls`/satyr-proxies/cliff + one FIRE fx, see below) |

**Occult smoke/fog emitters dropped across all 5 in-scope levels = 0.** `fog_occult_fx01`,
`pit_fx01`, `pit_fx02`, `occultistaura_fx01`, `cage_binding_fx01`, `bugcloud_smallfx` are ALL
present; `fog_occult_fx01` (+1 hiddenvalley01) and `pit_fx01` (+1 hiddenvalleyborder04) are even
in the ADDED column (the C2/C4 emphasis beyond SV). The ~48 non-smoke drops are scene dressing,
already covered by section B (OPTIONAL, do-not-auto-apply: Delphi 0x05 injection is greenfield +
v0x11-crash-prone, and restoring non-smoke props is scope creep against Will's "just the smoke").

**2. Same diff vs the LIVE Workshop map Will actually plays** (`3759792705/.../Levels.arc`,
`full_entity_diff.py live`): byte-for-behaviour identical present/dropped counts; the occult
emitters are present (fog + pit in the ADDED column). Will's installed map carries the smoke.

**3. Direct occult-emitter instance dump, DEPLOYED build40** - proves the emitters are not merely
present but ENABLED and correctly oriented (not silently disabled / zero-rotation degenerate):

| level | emitter instances | all flags=0 (enabled)? | all rotdet=1.0000 (identity)? |
|---|---:|---|---|
| hiddenvalley01 | 1 (fog) | YES | YES |
| hiddenvalleyborder04 | 5 (2 fog, 1 aura, 2 pit) | YES | YES |
| delphilowlands02 | 6 (3 fog, pit_fx01, pit_fx02, bugcloud) | YES | YES |
| delphilowlands03 | 2 (bugcloud) | YES | YES |
| delphilowlands04 | 3 (2 fog, cage_binding) | YES | YES |
| **total** | **17** | **17/17 enabled** | **17/17 identity** |

**4. FX field-drift, DEPLOYED arz vs SV arz** (`fx_diff.py`): all 8 occult FX EffectEntity
records (`fog_occult_fx01`, `pit_fx01`, `pit_fx02`, `bugcloud_smallfx`, `occultistaura_fx01`,
`cage_binding_fx01`, both disciple auras) are **BYTE-IDENTICAL DEP vs SV - 0 fields drifted.**
The DB-side lever (b) is refuted. Per the task rule, FX records that already match SV are NOT
touched.

### One thread the RCA's atmo heuristic did not name - checked and cleared

`full_entity_diff.py` (the superset) flags `records\skills\stealth\drxeffects\drx_bladehoning_running_fx.dbr`
dropped at delphilowlands04 (SV-local 14.160,10.121,6.250). The is_atmo heuristic missed it
(path `\drxeffects\` != the `\effects\` substring). Probed directly: it is an `EffectEntity`
whose `effectFile = DRXeffects\buttfire.pfx` - a **FIRE** particle, NOT the reported purple/black
occult smoke (that is `fog_occult_fx01` -> `occultfog.pfx`, present + byte-identical). Its DB
record resolves in the deployed arz. So it is a non-smoke fire prop, not the bug; restoring it
would be non-smoke scene emphasis + a greenfield Delphi 0x05 injection (crash risk) - out of scope.

### Why nothing was injected (this is the correct, DONE-means-DONE outcome, not a punt)

- MAP: no occult smoke emitter is dropped (0/17 missing, all enabled + oriented; fog even added).
  Injecting more `fog_occult_fx01` where the data is already SV-faithful is a FAKE-FIX (the entity
  is invisible-in-game for a NON-data reason, so a duplicate would not render either) + scope creep
  + a greenfield Delphi v0x11 injection with documented crash history. That is a vet NO-GO by
  default, and the brief forbids it.
- DB: 0 FX fields drifted; the brief says restore a field ONLY if drift was proven. None was.
- `0x09`/`0x17`: not touched (the 2026-07-08 refuted region-env lever; framing mismatch corrupts).

### The residual is NOT data - what to actually do next (no code lever without Will's go-ahead)

1. **Confirm install freshness first** (per "restart Steam before every test"): the smoke IS in
   the live Workshop `Levels.arc`. If Steam served a stale copy or Will tested a pre-build40
   subscribe, that alone explains "still not there." Restart Steam + hash-verify the loaded arc.
2. If current and still absent, the residual is **engine-era particle rendering** of the DRX
   occult fog on stock TQAE (particle budget / draw-distance culling), NOT content. The 6 `.pfx`
   are byte-identical to a shipping DRX mod (SVAERA) and our own live copy - they are the genuine
   assets. Diagnose in-game (does ANY `occultfog.pfx` render at HVBorder04, where identical records
   are present + enabled), a render probe - not a data edit.
3. **Only if Will explicitly wants the areas "smokier than SV"** does a data lever exist: fog
   DENSITY emphasis in the Delphi occult scenes via the proven v0x11 injector (the C2/C4 precedent).
   This is emphasis-beyond-SV and a deliberate scope expansion; it is NOT auto-applied.

### Deploy coupling

Nothing to deploy for the smoke bug (no artifact changed). This branch is docs-only (RCA report +
BACKLOG + read-only `tools/debug/` harness); it carries no map or arz delta and does not gate the
next build.

### Fix gates (round 1)

- instances_restored = 0 (0 dropped smoke emitters; fix list empty - re-verified from build40 + live)
- fx_fields_restored = 0 (0 FX fields drifted - all 8 records byte-identical)
- dry_run_diff = N/A - no injection performed (a redundant-smoke inject would be a fake-fix + vet NO-GO)
- dbr_resolution = all 6 occult-emitter records + `drx_bladehoning_running_fx` resolve in the deployed arz (0 new placements to resolve)
- py_compile = PASS (harness + build_section_surgery.py + patches/__init__.py)
- check_registry = PASS (`patches-registry selfcheck OK: 13 module(s)`, order b82195e9...; unchanged - no module added)
