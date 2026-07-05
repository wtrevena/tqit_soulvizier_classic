# DROPPED CONTENT AUDIT - Soulvizier-only entities lost by the merge

> Byte-level audit of every classic-Soulvizier (SV 0.98i) entity DROPPED from the
> shipped Soulvizier Classic map because the merge kept SVAERA's version of each
> shared level. Produced 2026-07-05 against the DEPLOYED map. Companions:
> `docs/SV_AREAS_AUDIT.md` (the 16 SV-only AREAS + their entrances),
> `docs/MODDING_PLAYBOOK.md` (mechanisms), `docs/CONTENT_PLAYBOOK.md` (records/DB),
> `CLAUDE.md` (status). No em dashes by house style.

---

## 0. Root cause (confirmed at the byte level)

The deployed merge (`tools/svaera_plus_portals.py`, the pipeline that writes the
shipped `Levels.arc`) uses the "clean base" strategy: it keeps SVAERA's blob for
EVERY shared level and only appends the SV-only levels (plus one in-place swap of
`Random09A` for the blood-cave walk-in). Proven directly:

- Of **957 levels shared** by SV and the shipped map (present in both by fname), the
  shipped blob is **byte-identical to SVAERA's for 956**. The ONLY shared level the
  merge modifies is `levels/world/orient/underground/random09a.lvl` (the blood-cave
  doorway swap). (Script: `ship_vs_ae.py`.)
- The alternate `perform_section_surgery` drxmap-merge path (in
  `build_section_surgery.py` / `hybrid_merge.py`) that WOULD splice SV's `0x05` into
  SVAERA's blob is NOT the deployed pipeline. So the drxmap merge described in the old
  `README.md` item 14 is NOT in the shipped map.

Consequence: **everything SV 0.98i added to a shared level - NPCs, merchants,
shrines/fountains, quest trigger volumes/proxies, decorations, and effect/atmosphere
emitters - is dropped wherever SVAERA's version of that shared level lacks it.** This
is the same failure class as the already-known Duister NPC, Widow Letter, and Rebirth
Fountain losses.

### Method + parser validation (why the numbers are trustworthy)

For each shared level we take SV's PLACED `0x05` instances and subtract the shipped
level's `0x05` string table. A record SV places whose path is absent from the shipped
level's string table is definitely not placed there = DROPPED. Using the string table
as the shipped-side test is deliberately conservative (a path absent from the table
cannot be referenced by any instance), and it sidesteps the harder v0x11 record parse.

The SV-side instance parser is the load-bearing one and is VALIDATED: SV `0x05`
records are `56 + (16 if flags@offset52 != 0 else 0)` bytes (the +16 is a UniqueId
GUID; this is the same relationship the merge's v0e->v11 converter documents). This
rule round-trips byte-exact on **1003 of 1003** SV levels (`verify_flagrule.py`); the
naive fixed-56 parser desynced on ~17% of levels and produced garbage string indices,
which is why an earlier draft over-counted. Sentinels reproduce exactly: the Rebirth
Fountain lands at HiddenValley01 local `(49.26,15.63,14.95)` == the brief's
`(49.3,15.6,14.9)`; widow_ling / trg_foundzhidan / location_treasurechest all land in
RoadToTown03A. (Scripts in the session scratchpad: `dca_lib.py`, `dca_parse.py`,
`enum2.py`, `report_meaningful.py`, `consolidate.py`, `atmosphere.py`, `occultist.py`,
`quest_entities.py`, `hunt_caravan.py`.)

---

## 1. Headline counts

**860 dropped placed entity instances across 154 shared levels** (327 distinct
`(level, record)` pairs; 219 distinct record paths). By bucket:

| Bucket | Instances | Distinct (level,rec) | Notes |
|--------|----------:|---------------------:|-------|
| Decoration / scenery | 750 | 248 | mostly base-game scenery + monster proxies SV placed and AE did not; low restore value except the `drxmap` dress |
| Effect / env emitter | 51 | 32 | **the atmosphere layer** (fog/pit/aura FX + coloured lights) - high value |
| Merchant | 24 | 24 | 21 = systematic SV alchemist merchants; 3 = the occult/hades merchants |
| NPC / creature | 16 | 6 | statues + uber proxies (base xpack); real SV NPCs are in the `drxmap` dress bucket below |
| Quest proxy / trigger | 12 | 11 | includes the 3 Widow-Letter volumes + GoM trigger |
| Portal / warp | 3 | 3 | `portal_olympianarena1` (uber+boss), `imhere` (GoM), typhon portal |
| Shrine / fountain | 3 | 3 | the Rebirth Fountain + two Hades respawn shrines |
| NPC (speaking) | 1 | 1 | `mystic_rhodes` |

**The genuinely SV-custom content is the 53 `drxmap`-namespace instances** (the rest is
largely SV-vs-AE base-scenery authoring drift). All 53 are the crown jewels and every
`drxmap` record RESOLVES in the built `.arz` (re-injectable). The `drxmap` drops
cluster into exactly four scenes:

1. **DelphiLowlands04** - the occultist tent scene (20 drops)
2. **DelphiLowlands02** - the pit-sprites / lava-pit scene (14 drops)
3. **HiddenValleyBorder04** - the cave-entrance "special area" dressing (7 drops)
4. **RoadToTown03A** - the Widow Letter questline (3 drops)
   (+ DelphiLowlands03 dress x5, startingfarmland06d `imhere` x1, HiddenValley01
   totems x2, scrabledeggs_floor06 secret-door x1.)

---

## 2. The shared-level dropped-entity table (meaningful buckets)

Decoration noise omitted; see `drops2.json` for the full 860. Coords are SV-LOCAL
(level-relative). `arz` = resolves in the built mod `.arz`; base-game records (e.g.
`records\lights\...`) show N but resolve at runtime via the stacked base DB
(`CONTENT_PLAYBOOK` 1.2), so all are re-injectable.

### 2.1 Merchants

The SV **"alchemist" merchants** are a systematic feature the merge dropped in 21
places (SVAERA has no `01_*_alchemist` at these spots):

| Record | Levels dropped from |
|--------|---------------------|
| `records\creature\npc\merchants\greece\01_greece_alchemist.dbr` | valley01, coastaltown01, athenscity03, delphicenter01, knossostownstarta, startingfarmland06d (6) |
| `...\greece\01_egypt_alchemist.dbr` | area006_abedju02, 256x256memphiscityarea, oasiscenter01, rhakotis02, thebes02 (5) |
| `...\greece\01_hades_alchemist.dbr` | rhodes_cityfinal_01, medea_medeagrove03, epirus_woods_01, styx_cryptug_stonetransitioniii01, elysian_fields_04 (5) |
| `...\greece\01_orient_alchemist.dbr` | hanginggardens04, hanginggardensexit01, changancity06, roadtotown03a, basecampforest02 (5) |

The **occult / hades scene merchants** (3, `drxmap`/hades):

| Record | Level | SV-local coord |
|--------|-------|----------------|
| `records\drxmap\dress\merchant_delphi_occulttent01.dbr` (the occultist tent - a Decoration) | delphilowlands04 | (12.88,9.98,2.52) |
| `records\xpack\sceneryhades\structure\merchant\merchant_hades_merchantwagon01.dbr` | hiddenvalleyborder04 | (36.23,1.62,26.54) |
| `records\xpack\scenerymedit\structure\merchant\merchantvendortable01.dbr` | delphilowlands02 | (65.99,10.00,124.43) |

### 2.2 Shrines / fountains

| Record | Level | SV-local coord | Note |
|--------|-------|----------------|------|
| `records\item\shrines\respawntempleorient01.dbr` (**the Rebirth Fountain**) | hiddenvalley01 | (49.26,15.63,14.95) | brief sentinel - confirmed |
| `records\xpack\item\shrines\respawn\respawn_hades_elysium.dbr` | olympusfinal02 | (456.06,23.0,943.36) | SV extra respawn |
| `records\xpack\item\shrines\respawn\respawn_towerofjudgement01.dbr` | judgment_towerug_floor00 | (81.09,3.0,22.41) | SV extra respawn |

### 2.3 Portals / warps

| Record | Level | SV-local coord | Serves |
|--------|-------|----------------|--------|
| `records\quests\portal_olympianarena1.dbr` (GridEntranceDynamic) | maze03 | (101.84,1.0,144.52) | **uber dungeon + boss arena entrance** |
| `records\drxmap\zgardenofmerchants\portmebiznitch\imhere.dbr` (BoundingVolume) | startingfarmland06d | (20.17,-2.45,188.52) | **Garden of Merchants warp** |
| `records\quests\questobjects\fixeditemtyphonportal.dbr` | hadespalace_floor05_04 | (-10.95,3.3,54.07) | Typhon portal object |

### 2.4 Quest proxies / trigger volumes

| Record | Level | SV-local coord | Quest |
|--------|-------|----------------|-------|
| `records\drxmap\quest\widow_ling.dbr` (Npc) | roadtotown03a | (66.5,-63.34,50.11) | **widowletter** |
| `records\drxmap\quest\trg_foundzhidan.dbr` | roadtotown03a | (77.07,-63.86,61.61) | **widowletter** |
| `records\drxmap\quest\location_treasurechest.dbr` | roadtotown03a | (27.2,-63.63,34.7) | **widowletter** |
| `records\drxmap\zgardenofmerchants\portmebiznitch\seen_ocv2_trigger.dbr` (BoundingVolume) | hiddenvalleyborder04 | (45.73,1.16,7.49) | GoM / open_bloodcave |
| `records\quests\volume_imhotepfix.dbr` | thebes02 | (29.87,5.21,79.54) | SV imhotep fix |
| `records\quests\volume_imhotepfixmemphis.dbr` | 256x256memphiscityarea | (171.11,3.0,176.75) | SV imhotep fix |
| `records\proxies boss\boss\minobossproxy_aniketos.dbr` | area002/connector04 | (85.79,36.16,113.25) | SV boss proxy |
| `records\drxcreatures\theregulator\theregulator_elproxy.dbr` (x8) + `_lproxy` (x1) | mantiocrefinale01, arachnosunderground01_floor0 (x2), athens01, knossoscity01, randombamboo01above | various | SV "regulator" trap-monster (Common, tagTrap10) - ambient, spread across base levels |

### 2.5 NPC / creature (real SV NPCs, mostly in `drxmap` dress)

| Record | Level | SV-local coord | What |
|--------|-------|----------------|------|
| `records\drxmap\pitsprites\t1_lildude_01/02.dbr` (Npc) + `t1_pitspawner_01/02.dbr` | delphilowlands02 | (55.33,10.32,114.49) etc | **the exploding pit-sprites** (see 5) |
| `records\drxmap\dress\t1_lildude_01/02/03.dbr` (Npc) | delphilowlands03/04 | (3.8,10.0,9.68) etc | sprite dress at the occult tent |
| `records\drxmap\dress\blooddemon_medium01.dbr` (Npc) | delphilowlands04 | (1.97,10.06,12.12) | the caged blood-demon |
| `records\drxmap\xurder\dng_bossroom_secretdoor.dbr` + `records\drxcreatures\crowheroes\jiaco.dbr` | scrabledeggs_floor06 | (10.93,-0.04,53.95) / (47.18,0.59,68.68) | SV secret-place hooks in the Rhodes underground |
| `records\xpack\creatures\npc\mystics\mystic_rhodes.dbr` | area002/valley04 | (125.79,25.83,51.92) | SV mystic NPC |
| base-game statues / `xq06_boss_hades_champions_uber` proxies | elysian_*, hadespalace_* | various | SV-placed base xpack content; low value |

---

## 3. Atmosphere / environment (Will's "dark cloud / smoke special area")

**Finding: the missing atmosphere is carried by `0x05` EMITTER ENTITIES, not by the
`0x09` or `SD` sections - so restoration is a plain entity re-inject, NOT deep section
surgery.** Proven:

- **SD (world-level lighting/atmosphere float params):** the shipped map's SD section
  is **byte-identical to SV's** (size 116299, first16 `020000000600...`; SVAERA's is
  227893). The merge uses SV's SD verbatim (`svaera_plus_portals.py` "Using SV SD").
  So SV's zonal lighting/atmosphere PARAMS are already shipped. No SD work needed.
- **0x09 (per-level env grid):** near-identical SV vs SVAERA for every cave-region
  level (e.g. HiddenValley01 SV 4202 B vs AE 4210 B; the +8 is v0e->v11 padding). AE
  preserves the env grid. No 0x09 work needed.
- **0x06 (terrain):** identical or near-identical (AE preserves it).

What is missing is the **per-zone emitter entities** SV placed in `0x05` and the merge
dropped. These ARE the dark cloud / smoke / occult glow. The cave-entrance region
(HiddenValley01 + HiddenValleyBorder04, Orient Silk Road) dropped:

| Level | Dropped emitter/env entities (SV-local coords) |
|-------|-----------------------------------------------|
| **hiddenvalleyborder04** | `drxmap\effects\fog_occult_fx01` x2 (26.64,1.48,24.83),(36.9,1.62,23.88); `drxmap\effects\occultistaura_fx01` (41.01,1.51,21.99); `drxmap\effects\pit_fx01` (26.98,0.38,24.94); `xpack\effects\lights\dynamic\10mlight_dyn_purple` x2; `...10mlight_dyn_red` x2; `lights\staticlights\5mlight_stat_blue` x2; `xpack\sceneryhades\...anouranfirepit02` + `...woodpyre01`; `drxcreatures\bloodwitch\...fx_disciple_aura_eyechantment01/02` |
| **hiddenvalley01** | `xpack\effects\lights\dynamic\10mlight_dyn_purple` x2 + `...10mlight_dyn_red` x2 (65.4,16.x,~102/106); `xpack\effects\lights\simple\15mlight_simple_purple` (45.06,29.08,102.42) + `...10mlight_simple_red` (46.95,25.03,112.49); `lights\dynamiclights\5mlight_dyn_orange` + `sceneryorient\...campfire01` (~38.8,15,89.7); plus `drxmap\dress2\totem` x2 (65.0,12.0,106.0) |

The purple/red/blue dynamic lights + occult fog + aura + firepit are exactly the
"dark cloud / smoke to indicate a special area." **Restore method: re-inject these
`0x05` entities into the SVAERA blobs (the safe append path, Section 6); no SD/0x09
copy is required.** All `drxmap` emitter records resolve in the mod `.arz`; the
`records\lights\...` and `xpack\effects\...` records are base-game (resolve at runtime).

The same occult-fog / pit / firepit / coloured-light motif was dropped from the two
Delphi scenes (Section 5).

---

## 4. The caravan driver (Will: it "disappeared")

**Found: `records\drxmap\zgardenofmerchants\merchants\caravan_rhodes.dbr`
(Class `NpcCaravan`, the Super-Caravan storage NPC), placed in the SV-only level
`levels/world/olympus/gardenofmerchants.lvl` at SV-local (136.3,-36.1,79.1),
level corner (1043,0,-4074) => world (1179.3,-36.1,-3994.9). It resolves in the
built `.arz`.**

Diagnosis correction: the caravan did NOT move into the isolated blood cave. The
`GRID_SHIFT (7840,0,2030)` matches ONLY `xbloodcave` + `random09a`; the Garden of
Merchants is `olympus/gardenofmerchants`, which is NOT shifted (SV corner == shipped
corner == (1043,0,-4074); verified). The caravan is inside the Garden of Merchants at
its SV-original position, present and valid.

**Why it "disappeared": the Garden of Merchants is entrance-broken.** Per
`SV_AREAS_AUDIT.md` Section 5, GoM's inbound warp (`portmebiznitch`/`imhere`) was
placed in the SHARED levels `startingfarmland06d` (+ `hiddenvalleyborder04`), and this
audit confirms `imhere.dbr` (BoundingVolume) is DROPPED from startingfarmland06d and
its companion `seen_ocv2_trigger` is dropped from hiddenvalleyborder04. With the warp
gone the player can never enter GoM, so its caravan is unreachable even though it is
placed correctly inside.

Recommendation: **do not** move the caravan into the cave. Fix the GoM ENTRANCE
(restore the `imhere` warp - Section 6, WAVE 3), which makes the caravan reachable
along with the rest of the merchant hub. If a caravan/stash at the blood-cave surface
entrance is also wanted for convenience, inject a second `caravan_rhodes.dbr` into
HiddenValley01 near the fountain spot (see the optional spec in Section 6), but the
primary fix is the GoM warp.

---

## 5. The occultist merchant + exploding sprites + volcano (Will's Greece memory)

**All three found, in the Greece/Delphi "Crisaeos Falls" lowlands, and all dropped by
the merge.** This is the "occultist merchant in Greece we worked on a lot" - the
prior-work reference is in `README.md` items 14 + 17 ("occultist merchant, demon
sprites, pit sprites restored"; "NPC portal placed near the demon sprites in
DelphiLowlands04") and git commit `a674c49` ("Remove broken Delphi NPC injection ...
corrupts the v0x11 blob and crashes the game"). So the team previously restored this
scene via the drxmap section-merge, then a later merge strategy change (the clean-base
`svaera_plus_portals.py`) dropped it again, and a direct NPC injection into the v0x11
Delphi blob was found to CRASH the game (the v0x11-inject risk, `MODDING_PLAYBOOK` 8.4).

### The occultist tent scene - DelphiLowlands04 (20 drxmap drops)

- **Merchant:** `records\drxmap\dress\merchant_delphi_occulttent01.dbr` (a Decoration
  tent) at (12.88,9.98,2.52). The actual shop NPC beside it,
  `Records\Creature\NPC\Merchants\Greece\Merchant_Delphi_Quest.dbr` (3.8u away), is
  KEPT (it is in SVAERA). So the shop still works; the OCCULT DRESSING around it was
  stripped.
- **Exploding sprites (the "little dudes"):** `records\drxmap\dress\t1_lildude_01.dbr`
  x3, `t1_lildude_02.dbr`, `t1_lildude_03.dbr` (all Class `Npc`) around the tent.
- **Caged blood-demons:** `records\drxmap\dress\blooddemon_medium01.dbr` (Npc) +
  `cage_medium.dbr` x3 + `cage_small.dbr` x2 + `records\drxmap\effects\cage_binding_fx01.dbr`
  + `records\drxmap\sounds\soundobject_demoncagebindingloop.dbr`.
- **Occult atmosphere:** `records\drxmap\effects\fog_occult_fx01.dbr` x2; a green
  dynamic light (5mlight_dyn_green) + a blue nightlight; loot props `scrolls`,
  `qi_tomeofhealing01`, `vitstaff_01/05`.

### The pit-sprites / lava-pit scene - DelphiLowlands02 (14 drxmap drops)

This is the literal "exploding sprites next to a volcano":

- **Pit-sprites in their own namespace:** `records\drxmap\pitsprites\t1_lildude_01.dbr`
  x4, `t1_lildude_02.dbr` x2, **`t1_pitspawner_01.dbr` x2 + `t1_pitspawner_02.dbr`**
  (the spawner that emits the exploding sprites). All resolve in the `.arz`.
- **The "volcano" (lava pit):** `records\drxmap\effects\pit_fx01.dbr` +
  `pit_fx02.dbr` + the Hades lava firepits
  `xpack\sceneryhades\...mc_hades_anouranfirepit03.dbr` and `...anouranfirepitmd01.dbr`,
  wrapped in `drxmap\effects\fog_occult_fx01.dbr` x3 and a `bugcloud_smallfx` haze.

The exact same motif (pit_fx + occult fog + Hades firepit + coloured lights) was also
dropped at the cave entrance (hiddenvalleyborder04, Section 3), tying the Greece
occult-scene aesthetic to the blood-cave "special area" Will remembers.

**Prior-work reference confirmed:** yes, this is the scene worked on in earlier
sessions (the DelphiLowlands04 occultist tent + demon/pit sprites). It was restored
once (drxmap merge), lost again (merge strategy change), and a naive re-inject into
the v0x11 Delphi blob crashed - so the SAFE re-inject path (Section 6) must be used.

---

## 6. Restoration plan (prioritized, concrete)

### The injection mechanism + the v0x11 risk

The **safe** re-inject path is the `INJECT_SPECS` map in
`tools/build_section_surgery.py:121` consumed by `svaera_plus_portals.py`, which for a
v0x11 target level appends the new `0x05` records AND appends matching `0x14` metadata
entries for exactly the new instances via the step-7 append loop
(`svaera_plus_portals.py:396-428`) - it keeps the original `0x14` entries intact and
adds one default 20-byte payload per injected instance.

**The risk to avoid** (`build_section_surgery.py:122` history + commit `a674c49` +
`MODDING_PLAYBOOK` 8.4): the OLD path that REGENERATED the whole `0x14` from scratch
(`generate_default_0x14`, `build_section_surgery.py:551`) for a v0x11 Delphi level
corrupted the blob and crashed world streaming. **Do NOT regenerate 0x14 wholesale for
v0x11 levels;** use the append-only step-7 path. Every cave-region + Delphi target is
v0x11, so this is the operative constraint. (A safer-still option for some entrances is
the engine-native shared-level blob-patch used for Random09A - see WAVE 2/3.)

All target coords below are the SV-LOCAL coords proven in this audit (Sections 2-5);
they are correct because these shared levels are NOT grid-shifted (their corners match
between SV and the shipped map). Group order = Will's cave-entrance-first focus.

### WAVE A - Cave-entrance region (Will's focus) - effort S-M

The single highest-value quick win, since it is all `INJECT_SPECS` entity re-injects
into levels the player already reaches on the way to the blood cave.

| Target level (v0x11) | Inject (record, SV-local x,y,z) | Restores |
|----------------------|--------------------------------|----------|
| `hiddenvalley01` | `respawntempleorient01.dbr` @ (49.26,15.63,14.95) | **Rebirth Fountain** |
| `hiddenvalley01` | `10mlight_dyn_purple`/`_red` @ (65.47,16.43,106.04),(65.34,16.19,98.03) + `15mlight_simple_purple` @ (45.06,29.08,102.42) + `10mlight_simple_red` @ (46.95,25.03,112.49) + `5mlight_dyn_orange`+`campfire01` @ (~38.8,15,89.7) + `drxmap\dress2\totem` x2 @ (65.0,12.0,106.0) | cave-entrance glow/atmosphere |
| `hiddenvalleyborder04` | `drxmap\effects\fog_occult_fx01` @ (26.64,1.48,24.83),(36.9,1.62,23.88); `occultistaura_fx01` @ (41.01,1.51,21.99); `pit_fx01` @ (26.98,0.38,24.94); `10mlight_dyn_purple`/`_red` @ (47.0,6.5,29.6),(41.1,6.5,12.4); `5mlight_stat_blue` x2; `mc_hades_anouranfirepit02`+`woodpyre01` @ (~27.4,1.6,25); `fx_disciple_aura_eyechantment01/02`; `drxmap\dress2\totem` x2 | **the "dark cloud/smoke special area"** |
| `hiddenvalleyborder04` | `merchant_hades_merchantwagon01.dbr` @ (36.23,1.62,26.54) | the Hades merchant near the cave |

Method: `INJECT_SPECS` append (all v0x11 -> step-7 0x14-append path). Risk: LOW
(entity dress only, no blob-swap). Effort: **S-M**.

### WAVE B - Garden of Merchants entrance (unlocks the caravan) - effort M

`imhere.dbr` (BoundingVolume) was dropped from startingfarmland06d and its trigger
`seen_ocv2_trigger` from hiddenvalleyborder04; the GoM is otherwise placed correctly
with its caravan inside. Two options (this is the same decision as SV_AREAS_AUDIT
WAVE 3):

- **(preferred, engine-native)** re-inject the `portmebiznitch`/`imhere` warp record(s)
  into the SVAERA `startingfarmland06d` blob at (20.17,-2.45,188.52) wired to the GoM
  destination shrine (`teleportshrine_gom`, which survives inside GoM), the same
  blob-patch class as Random09A. Also restore `seen_ocv2_trigger` @ (45.73,1.16,7.49)
  in hiddenvalleyborder04 if the warp logic needs it.
- **(alternative)** an `INJECT_SPECS` entity re-inject of the two BoundingVolumes plus a
  small quest `Action_BoatDialog` to an on-mesh GoM cell (fragile per the playbook).

This makes the caravan-driver (`caravan_rhodes.dbr` @ world (1179.3,-36.1,-3994.9))
reachable. Effort: **M**. Depends on GoM having a navmesh (SV_AREAS_AUDIT WAVE 0).

Optional convenience: inject a second `caravan_rhodes.dbr` (NpcCaravan) into
HiddenValley01 near the fountain (e.g. local (47,15.6,17)) so a stash exists at the
blood-cave surface entrance even before GoM is wired. Low risk (`INJECT_SPECS`).

### WAVE C - The Greece occult scenes (the occultist merchant + sprites + volcano) - effort M

| Target level (v0x11) | Inject set | Restores |
|----------------------|-----------|----------|
| `delphilowlands04` | `merchant_delphi_occulttent01` @ (12.88,9.98,2.52); `t1_lildude_01` x3 @ (3.8,10,9.68)/(2.93,10,8.96)/(2.94,10,10.27); `t1_lildude_02` @ (1.47,11.88,10.67); `t1_lildude_03` @ (2.66,11.85,9.27); `blooddemon_medium01` @ (1.97,10.06,12.12); `cage_medium` x3 @ (1.82,10,12.08)...; `cage_small` x2; `cage_binding_fx01` @ (2.51,10.26,11.08); `soundobject_demoncagebindingloop` @ (2.19,10,10.9); `fog_occult_fx01` x2 @ (19.34,10,2.12)/(8.53,10,15.02); `5mlight_dyn_green` @ (14.88,11.31,4.74); `10mlight_statnl_blue` @ (15.21,16.31,5.17); props `scrolls`,`qi_tomeofhealing01`,`vitstaff_01/05` | **the occultist tent + caged demons + occult fog** |
| `delphilowlands02` | `pitsprites\t1_lildude_01` x4, `t1_lildude_02` x2, **`t1_pitspawner_01` x2 + `t1_pitspawner_02`** @ (~55,10.3,117); `pit_fx01` @ (79.45,10.29,122.03); `pit_fx02` @ (52.12,10.88,116.74); `mc_hades_anouranfirepit03`/`...md01`; `fog_occult_fx01` x3; `bugcloud_smallfx`; `merchantvendortable01` @ (65.99,10,124.43) | **the exploding pit-sprites next to the lava pit ("volcano")** |
| `delphilowlands03` | `t1_lildude_02` x2 @ (127.99,10,8.96),(127.39,10,10.09); `vitstaff_01` x3; `bugcloud_smallfx` x2 | sprite dressing continuation |

Method: `INJECT_SPECS` append (v0x11 -> step-7 0x14-append). **CRITICAL:** these are the
levels that crashed on a naive v0x11 inject (`a674c49`); use the append-only `0x14`
path, and validate no wholesale `0x14` regen runs for these keys. Effort: **M**.

### WAVE D - Uber dungeon + boss arena entrance (shared fix) - effort M

`portal_olympianarena1.dbr` (GridEntranceDynamic) was dropped from `maze03` (Knossos
underground). This is the SINGLE record that gates BOTH the uber dungeon
(`urder`/crypt_floor1) and the boss arena (`bossarena`/boss_arena) - restoring it in
maze03 fixes both. This is the engine-native shared-level blob-patch (re-inject the
record into maze03's `0x05` at (101.84,1.0,144.52) + APPEND its `0x14` GUID binding to
crypt_floor1), the same class as Random09A. Detail + the `0x14` binding math are in
`SV_AREAS_AUDIT.md` WAVE 2. Effort: **M** (blob-patch, Will decision). Also restore
the four maze03 green/red lights (dressing) via `INJECT_SPECS`.

### WAVE E - Widow Letter questline - effort S

Re-inject the 3 dropped Widow-Letter entities into `roadtotown03a` (v0x11):

| Record | SV-local coord |
|--------|----------------|
| `records\drxmap\quest\widow_ling.dbr` (Npc) | (66.5,-63.34,50.11) |
| `records\drxmap\quest\trg_foundzhidan.dbr` | (77.07,-63.86,61.61) |
| `records\drxmap\quest\location_treasurechest.dbr` | (27.2,-63.63,34.7) |

`widowletter.qst` is already in `Quests.arc` and its other entities
(`location_letterdrop`, the reward/dialog/finalletter records) are DB-resolved or
placed already, so this single `INJECT_SPECS` block makes the questline fireable.
Method: `INJECT_SPECS` append. Risk: LOW. Effort: **S**. (This plus the alchemist
merchant that also dropped from roadtotown03a can go in the same block.)

### WAVE F - Systematic alchemist merchants + regulator + misc - effort M (optional)

- Re-inject the 21 `01_*_alchemist` merchants into their 21 host levels (all v0x11 or
  v0x0f) via `INJECT_SPECS` (coords in `drops2.json`). Restores an SV convenience
  feature. Effort: **M** (bulk data entry; low risk each).
- Re-inject the `theregulator_elproxy`/`_lproxy` ambient trap-monster (9 spots) if the
  regulator encounters are wanted. Low value (Common trap), optional.
- The remaining ~700 base-scenery/monster-proxy decoration drops are SV-vs-AE authoring
  drift on shared base levels; treat as **do-not-restore** unless a specific spot looks
  wrong in-game (they are cosmetic and AE's dressing is already coherent).

### Per-quest dropped-entity summary (Item 4)

| Quest | Dropped entities (blocking) | Non-blocking (DB-resolved / already placed) |
|-------|-----------------------------|----------------------------------------------|
| **widowletter** | widow_ling, trg_foundzhidan, location_treasurechest (all roadtotown03a) | location_letterdrop placed; finalletter/rewards/dialog DB-only |
| **bossarena** | portal_olympianarena1 (maze03) - shared with uber | location_bossarenacenter placed; boss_satyrshaman/portal_olympianarena DB proxies |
| **urder** (secret place) | NONE dropped (all placements are in KEPT SV-only levels) - only the ENTRY into behindthesp is broken (SV_AREAS_AUDIT WAVE 1) | zilla01-03 are spawn proxies |
| **open_bloodcave_portal** | imhere (startingfarmland06d), seen_ocv2_trigger (hiddenvalleyborder04) | starting_storyteller placed (its Duister trigger was neutralized); all blood-cave interior triggers placed in kept SV-only levels |

### Effort roll-up

| Wave | Scope | Method | Risk | Effort |
|------|-------|--------|------|--------|
| A | Cave-entrance atmosphere + fountain + Hades merchant | INJECT_SPECS | LOW | S-M |
| B | Garden of Merchants entrance (unlock caravan) | shared blob-patch (pref) or quest | MED | M |
| C | Greece occult scenes (occultist merchant + sprites + volcano) | INJECT_SPECS (append-0x14 only) | MED (v0x11 crash history) | M |
| D | Uber + boss entrance (maze03 portal) | shared blob-patch + 0x14 GUID bind | MED | M |
| E | Widow Letter (3 entities) | INJECT_SPECS | LOW | S |
| F | Systematic alchemists + regulator + misc | INJECT_SPECS | LOW | M (bulk) |

**Single highest-value quick win:** WAVE A's HiddenValley01 + HiddenValleyBorder04
re-inject - it restores the Rebirth Fountain AND the exact "dark cloud / smoke special
area" atmosphere Will described, at the blood-cave entrance the player already walks
through, using only the SAFE `INJECT_SPECS` append path (no blob-swap, no crash risk),
with every record confirmed resolvable and every coord byte-verified.
