# b96 - Vashkarr, Eldest of the Ancients: spear-and-shield soul retune (R-72)

Branch `feat/vashkarr-soul`, tag `build57-dev`. **DB-ONLY lane** (coupled arz + Text pair).
**No map rebuild, no deploy** - the orchestrator merges this lane's arz with the other in-flight
lanes and deploys ONCE.

---

## 0. THE RULING

Will, 2026-07-27, verbatim:

> Vashkarr, Eldest of the Ancients soul should get +% pierce damage and =% penetration  since he is a spear and shield guy and the soul should give +% boost to movement not have a penalty for speed, this guy should be fast. also he needs to do more damage. we can have the penalty be something like -6-8% reduction in elemental damage or something like that

and, on field selection, verbatim:

> see spawn of chi soul for how to add +% penetration and pierce damage

Read as (the `=%` is a typo for `+%`): (a) add +% pierce damage and +% pierce PENETRATION;
(b) the movement-speed PENALTY becomes a movement-speed BONUS; (c) raise overall damage;
(d) add a -6% to -8% elemental-damage drawback in its place.

Appended to `docs/WILL_RULINGS.md` as **R-72**, status IMPLEMENTED.

> **Ledger note:** the Souls & items decade (R-40..R-49) was exhausted, and the file already
> carries two accidental duplicate numbers (R-13, R-43) that make those rulings ambiguous to
> cite. Rather than add a third collision this lane opened a fresh reserved overflow decade,
> **Souls & items 70-79**, documented in the ledger itself.

---

## 1. IDENTIFICATION (proven, not guessed)

Ground truth = the deployed `SoulvizierClassicDEV.arz` (51,085 records) plus the deployed
`Resources/Text.arc`.

**Text tags (deployed `modstrings.txt`), verbatim lines:**

```
tagSVCSoulVashkarr={^F}Vashkarr, Eldest of the Ancients Soul
tagSVCSoulVashkarrDESC=Torn from Vashkarr, Eldest of the Ancients, the last warlord of the dragonian race. It burns with the fury of an age the world has forgotten.
tagSVCMonsterVashkarr={^r}Vashkarr, Eldest of the Ancients
tagSVCMonsterVashkarrLance={^r}Ancient Lancer of the Deep
tagSVCMonsterVashkarrWarlock={^r}Ancient Warlock of the Deep
```

`tagSVCSoulVashkarr` resolves to **exactly the string Will named**, so the soul family is
identified by tag, not by guesswork. (Note `_create_vashkarr` also assigns this tag the value
`{^F}Soul of the Eldest`; the later F6 `_SOUL_NAME_STANDARD` pass overwrites it, and the
`{^F}Vashkarr, Eldest of the Ancients Soul` value above is what actually ships.)

**Records:**

| Role | Record | Notes |
|---|---|---|
| Soul, Normal | `records\item\equipmentring\soul\svc_uber\vashkarr_soul_n.dbr` | itemLevel 38, levelReq 33 |
| Soul, Epic | `records\item\equipmentring\soul\svc_uber\vashkarr_soul_e.dbr` | itemLevel 56, levelReq 51 |
| Soul, Legendary | `records\item\equipmentring\soul\svc_uber\vashkarr_soul_l.dbr` | itemLevel 71, levelReq 66 |
| Monster (the drop) | `records\creature\monster\dragonian\um_vashkarr_99.dbr` | `lootFinger2Item1` = the 3 tiers, `chanceToEquipFinger2` = 66.0 |
| Escort | `records\creature\monster\dragonian\svc_vashkarr_lance.dbr` | "Ancient Lancer of the Deep" |
| Escort | `records\creature\monster\dragonian\svc_vashkarr_warlock.dbr` | "Ancient Warlock of the Deep" |
| Fodder | `records\creature\monster\dragonian\svc_vashkarr_fodder.dbr` | |

**Difficulty variants:** there are **none**. A full record-name scan for `vashkarr` returns the
records above plus the proxy/pool/quest/skill records
(`q_vashkarr_lone`, `pools\q_vashkarr_lone`, `svc_area_return_vashkarr`,
`svc_helos_trav_vashkarr`, `svc_vashkarr_summonhorde`); the boss is a single `um_vashkarr_99`
record and difficulty scaling is carried by the three ITEM tiers, not by per-difficulty monster
records. Only the three soul records are in scope.

**Spear-and-shield premise confirmed at the source:** the boss record is built by cloning
`bm_deathlance_32` (AncientDragonian01), i.e. a lance-and-shield dragonian. Will's read of the
character is correct.

---

## 2. BEFORE STATE - every stat on all 3 tiers as it ships today

Read directly out of the deployed `SoulvizierClassicDEV.arz`. Zero-valued fields omitted
(each record carries 56 fields, 48 non-zero; the 8 omitted are all zero).

| field | NORMAL | EPIC | LEGENDARY |
|---|---|---|---|
| `itemLevel` / `levelRequirement` | 38 / 33 | 56 / 51 | 71 / 66 |
| `itemNameTag` | `tagSVCSoulVashkarr` | same | same |
| `itemText` | `tagSVCSoulVashkarrDESC` | same | same |
| `bitmap` | `SVItems\jewelry\soul_n_icon.tex` | `...soul_e_icon.tex` | `...soul_l_icon.tex` |
| `mesh` | `drx\meshes\n_soulmesh.msh` | same | same |
| `Class` / `templateName` | `ArmorJewelry_Ring` / `Jewelry_Ring.tpl` | same | same |
| `itemClassification` | `Magical` | `Magical` | `Magical` |
| `itemCostName` | `records/game/itemcost_soul.dbr` | same | same |
| `numRelicSlots` | 1 | 1 | 1 |
| `augmentSkillName1` | `drxfireenchantment` | same | same |
| `augmentSkillLevel1` | 3 | 4 | 5 |
| `augmentSkillName2` | `drxonslaught` | same | same |
| `augmentSkillLevel2` | 3 | 4 | 5 |
| `characterLife` | 210.0 | 287.0 | 350.0 |
| `characterLifeModifier` | 6.0 | 8.2 | 10.0 |
| `characterStrength` | 18.0 | 24.6 | 30.0 |
| `characterStrengthModifier` | 4.8 | 6.6 | 8.0 |
| `characterOffensiveAbility` | 54.0 | 73.8 | 90.0 |
| `characterDefensiveAbility` | 36.0 | 49.2 | 60.0 |
| `characterAttackSpeedModifier` | 9.6 | 13.1 | 16.0 |
| **`characterRunSpeedModifier`** | **-8.0** | **-8.0** | **-8.0** |
| `offensivePhysicalMin` | 36.0 | 49.2 | 60.0 |
| `offensivePhysicalMax` | 57.0 | 77.9 | 95.0 |
| `offensivePhysicalModifier` | 21.0 | 28.7 | 35.0 |
| `offensiveFireMin` | 30.0 | 41.0 | 50.0 |
| `offensiveFireMax` | 48.0 | 65.6 | 80.0 |
| `offensiveFireModifier` | 18.0 | 24.6 | 30.0 |
| `offensiveSlowBleedingMin` | 72.0 | 98.4 | 120.0 |
| `offensiveSlowBleedingDurationMin` | 3.0 | 3.0 | 3.0 |
| `offensiveLifeLeechMin` | 15.0 | 20.5 | 25.0 |
| `offensiveFearMin` | 1.5 | 2.0 | 2.5 |
| `defensivePhysical` | 30.0 | 45.0 | 60.0 |
| `defensiveProtection` | 150.0 | 260.0 | 400.0 |
| `defensiveBleeding` | 18.0 | 24.6 | 30.0 |
| `defensiveFire` | 15.0 | 20.5 | 25.0 |
| `defensiveLife` | 12.0 | 16.4 | 20.0 |
| `defensiveReflect` | 6.0 | 9.0 | 12.0 |
| **pierce fields** | **ABSENT (all zero)** | **ABSENT** | **ABSENT** |
| **`offensiveElementalModifier`** | **0.0 (absent)** | **0.0** | **0.0** |

### Will's premise is CONFIRMED

**Field:** `characterRunSpeedModifier`. **Value:** `-8.0` (FLOAT) on **all three tiers**.
In game this reads as **"-8% Movement Speed"**, i.e. a straight penalty on every tier.

**Where it comes from:** `apply_svc_patches._apply_b7_eldest_soul_rebalance` (the "A8/B7" pass),
line `db.set_field(rec, 'characterRunSpeedModifier', -8.0, DATA_TYPE_FLOAT)  # amgoz downside`,
applied to both the `vashkarr` and `gorrahk` soul families. Its docstring records the intent:
*"add an amgoz character-through-tradeoff downside (-8% run speed: the Eldest is ancient and
heavy)"*. Critically **this pass runs AFTER `_create_vashkarr`**, so it is the last writer on
that field - which is exactly why the fix has to touch it and not only the tier stats.

**Pierce:** no pierce field of any kind is present. **Elemental:** `offensiveElementalModifier`
is absent/zero. So (a) and (d) are genuinely new effects, not edits.

---

## 3. FIELD CHOICES - every field mirrored from a shipped donor

### 3.1 Pierce damage + penetration: the donor Will named

Resolved **Spawn of Chi** by its Text tag: `tagSoulName541={^F}Spawn of Chi Soul`, carried by
`records\item\equipmentring\soul\raptor\spawnofchi_soul_{n,e,l}.dbr` (monster
`records\creature\monster\raptor\um_spawnofchi_37.dbr`). Its full non-zero field set contains
**exactly two** pierce fields, quoted verbatim from the deployed arz:

| Spawn of Chi field | dtype | n | e | l |
|---|---|---|---|---|
| `offensivePierceModifier` | 1 (FLOAT) | **30.0** | **42.0** | **58.0** |
| `offensivePierceRatioModifier` | 1 (FLOAT) | **40.0** | **54.0** | **62.0** |

(For completeness, the rest of Spawn of Chi's payload: `itemSkillName` Trance of Empathy @4/6/8,
augments Herbalism + Wolf Maul, `characterDodgePercent` 10/13/13, `characterDeflectProjectile`
10/12/14, `characterLifeRegen` 8/9.43/11.79, `defensiveFire` 15/21/29,
`offensivePercentCurrentLife` 12-16/16-19/21-25 @15% chance, `offensiveSlowBleedingModifier`
34/47/69. No other pierce or penetration field appears.)

**This is the disambiguation Will was pointing at.** TQ has several pierce-shaped fields that are
easy to confuse; a database-wide census of every field whose name contains `pierc` or `penetrat`
returns 25 distinct fields with non-zero values. The two that matter here:

- `offensivePierceModifier` = **+X% Pierce Damage** (scales pierce damage you already deal).
- `offensivePierceRatioModifier` = **+X% Piercing** = the PENETRATION stat: pierce *ratio*
  converts a share of the hit's PHYSICAL damage into pierce, which bypasses armour absorption.

Mirroring both is what makes the pair work, and it compounds specifically well on Vashkarr
because he carries a large physical package for the ratio to convert.

**Roster corroboration:** 46 shipped soul records carry this exact pair, so it is amgoz1's own
established idiom, not an invention. Envelope on `offensivePierceModifier` runs from
`maenadtracker` 8/14/22 up to `hazur` 82/125/156; on `offensivePierceRatioModifier` from
`maenadscout` 6/12/20 up to `mordanokath` 50/65/79 and `toxeus_soul` 40/60/80.

### 3.2 Movement-speed BONUS (no donor named by Will, so one was found and cited)

Field: **`characterRunSpeedModifier`**, positive. Donors, all shipped soul rings in the same
slot, same dtype (FLOAT), quoted from the deployed arz:

| Donor record | n | e | l |
|---|---|---|---|
| `records\item\equipmentring\soul\vulture\sandbeak_soul_{n,e,l}.dbr` | 20.0 | 26.0 | 29.0 |
| `records\item\equipmentring\soul\satyr\rakanizeus_soul_{n,e,l}.dbr` | 45.0 | 45.0 | 45.0 (roster ceiling) |

`sandbeak` is the primary donor: it is the shipped soul that carries this field as a
**tier-scaled** value, which is the shape needed here. (`sandprowler_soul_e/l` = 25.0/29.0 and
`coldpaw_soul_e/l` = 24.0/31.0 corroborate the same band at Epic/Legendary; `rakanizeus` marks
the roster ceiling and is deliberately not matched.)

313 shipped soul records carry a positive value on this field, so the effect is unambiguously
live and this is the standard field for it. Non-soul corroboration:
`records\item\equipmentgreaves\u_l_hermes'talaria.dbr` = 40.0,
`records\item\equipmentgreaves\us_l_alexander'spanoply.dbr` = 30.0.

### 3.3 Percent ELEMENTAL damage reduction (no donor named by Will, so one was found and cited)

Field: **`offensiveElementalModifier`**, negative. Donor:

> `records\item\equipmentring\u_n_ringofzakalwe.dbr` (Epic ring, itemLevel 24) ships
> **`offensiveElementalModifier = -25.0`** alongside **`offensivePhysicalModifier = +25.0`** and
> `characterIntelligenceModifier = -10.0`.

This is the *only* item record in the database with a negative value on this field, and it is
close to a perfect donor: it is a **ring** (same slot, same `Jewelry_Ring.tpl` template, same
`ArmorJewelry_Ring` Class as a soul), and its design is literally the trade Will asked for -
give up elemental damage, gain physical. Liveness of the field is not in doubt: 193 records
carry a non-zero value on it (115 items, plus xpack/skills/drxitem), including 114 items with a
POSITIVE value (e.g. `thyia_soul_l` +182, `um_l_mindragerobe` +145), so the engine plainly reads
it; the sign is the only thing that changes.

`offensiveElementalModifier` is TQ's composite (fire + cold + lightning) percent-damage modifier,
so it renders as a single **"-X% Elemental Damage"** line rather than three separate penalties.
The per-element alternative was rejected: the database ships negative `offensiveFireModifier`
(6 souls: ikaie, coldtusk) but **no** negative cold or lightning modifier anywhere, so a
per-element drawback would have had to invent two of its three fields.

### 3.4 dtype preservation

All four fields are **FLOAT (dtype 1)** on their donors, and all four are written as `(F, value)`
tuples inside the `_vk_stats` tier dict, which is the exact idiom the surrounding 20 stat fields
already use. Per the documented corruption lesson, no explicit dtype is passed to `set_field` on
a cloned record: these souls are **not** clones - `_create_soul` builds them with bare
`_ensure_record` (the standing "never `clone_record` for souls" rule), and the tier-stats dict is
the sanctioned way to author their fields.

---

## 4. AFTER STATE - all 3 tiers

Changed and new fields only; every other field in the section-2 table is unchanged.

| field | NORMAL | EPIC | LEGENDARY | change |
|---|---|---|---|---|
| **`offensivePierceModifier`** | **40.0** | **58.0** | **78.0** | NEW (a) |
| **`offensivePierceRatioModifier`** | **35.0** | **50.0** | **65.0** | NEW (a) |
| **`characterRunSpeedModifier`** | **+12.0** | **+17.0** | **+22.0** | was -8 / -8 / -8 (b) |
| **`offensiveElementalModifier`** | **-8.0** | **-7.0** | **-6.0** | NEW (d) |
| `offensivePhysicalMin` | 46.8 | 64.0 | 78.0 | was 36.0 / 49.2 / 60.0 (c) |
| `offensivePhysicalMax` | 74.4 | 101.7 | 124.0 | was 57.0 / 77.9 / 95.0 (c) |
| `offensivePhysicalModifier` | 27.6 | 37.7 | 46.0 | was 21.0 / 28.7 / 35.0 (c) |
| `characterOffensiveAbility` | 66.0 | 90.2 | 110.0 | was 54.0 / 73.8 / 90.0 (c) |
| `characterAttackSpeedModifier` | 10.8 | 14.8 | 18.0 | was 9.6 / 13.1 / 16.0 (c) |
| `offensiveSlowBleedingMin` | 90.0 | 123.0 | 150.0 | was 72.0 / 98.4 / 120.0 (c) |
| `offensiveLifeLeechMin` | 18.0 | 24.6 | 30.0 | was 15.0 / 20.5 / 25.0 (c) |
| `offensiveFireMin` / `Max` / `Modifier` | 30 / 48 / 18 | 41 / 65.6 / 24.6 | 50 / 80 / 30 | **UNCHANGED (held flat on purpose)** |

The raised damage values follow the family's existing `m = 0.6 / 0.82 / 1.0` tier ramp from a
Legendary anchor, so the shape of the ladder is untouched; only the anchors moved. The four
ruling fields are set explicitly per tier instead (a steeper low end reads better on pierce, and
the drawback has to move in its own direction - see below).

### Value justification

- **Pierce damage 40/58/78.** Above Will's donor (Spawn of Chi 30/42/58) because the spear IS
  Vashkarr's identity where it is one of several things Chi does, and Vashkarr is an uber boss
  soul at a comparable itemLevel (38/56/71 vs 37/55/68). Well inside the shipped envelope: below
  `dayria` 50/73/89 at Normal and below `hazur` 82/125/156 throughout. `hazur` is a dedicated
  archer soul and should keep the ceiling - Vashkarr is a lancer, not a bowman.
- **Penetration 35/50/65.** Inside the shipped envelope and deliberately below the two
  ceiling-holders (`mordanokath` 50/65/79, `toxeus_soul` 40/60/80). Reads as "an ancient lance
  finds the gap in any armour" without making armour irrelevant.
- **Movement +12/+17/+22.** Reverses the sign of the old penalty and then some. Sits in the
  shipped mainstream top quartile (`najja_l` 22, `sandbeak_l` 29) rather than at the
  `rakanizeus` 45 outlier, so it reads clearly fast without turning a boss soul into a movement
  item.
- **Elemental -8/-7/-6.** Every tier inside Will's stated band. Direction explained below.

### Handling the drawback vs the `souls_quality` monotonicity gate (deliberate)

`souls_quality.verify()` enforces two things on every full-3-tier soul family:

1. `_monotonicity_violations` - `augmentSkillLevel1..4` and `itemSkillLevel` must be
   non-decreasing n <= e <= l when the skill NAME is identical across tiers. **Not touched by
   this lane:** the augments stay Fire Enchantment + Onslaught at 3/4/5, unchanged.
2. `_flat_tier_violations` (the b78 "Blood Cult High Priest" strict-progress law) - at least ONE
   power field must be **strictly greater** at each tier step. `_POWER_IGNORE` does not list
   `offensiveelementalmodifier` or `characterrunspeedmodifier`, so both of the new fields count
   as power fields.

A drawback that DEEPENS with rarity (say -6 / -7 / -8) would technically pass gate 2 - it only
needs one field strictly greater, and physical/pierce supply that easily - **but it would be a
real tier regression the gate cannot see**: the Legendary ring would be strictly worse than the
Epic on that axis.

So the penalty is deliberately made to **shrink** with rarity: **-8.0 / -7.0 / -6.0**. This:

- keeps every tier inside Will's named -6% to -8% band;
- makes the elemental field itself monotonically increasing (-8 < -7 < -6), so the higher tier is
  **not worse than the one below it on any power axis at all**;
- actively *helps* `_tier_progresses` rather than leaning on other fields to cover for it;
- needs **no `_FLAT_TIER_WAIVER` entry** (the waiver set stays empty, as the b78 sweep left it).

Flavour reading: the deeper you bind the Eldest, the better you carry the ember he lost.

---

## 5. CODE CHANGES

### 5.1 `tools/apply_svc_patches.py` - `_create_vashkarr._vk_stats`

The four ruling fields added/flipped and the damage anchors raised, with the field provenance and
the tier-shape reasoning recorded in the function comment.

### 5.2 `tools/apply_svc_patches.py` - `_apply_b7_eldest_soul_rebalance` (the load-bearing half)

This pass runs **after** `_create_vashkarr` and was the last writer on `characterRunSpeedModifier`.
Setting a positive value in `_vk_stats` alone would have been silently clobbered straight back to
`-8.0`. The `-8%` clause is now scoped to Gorrahk:

```python
RUNSPEED_DOWNSIDE = ('gorrahk',)   # R-72: NOT vashkarr (see the amendment above)
...
if base in RUNSPEED_DOWNSIDE:
    db.set_field(rec, 'characterRunSpeedModifier', -8.0, DATA_TYPE_FLOAT)  # amgoz downside
```

**Retirement-protocol check (standing law 2).** Nothing is deleted. The `-8%` downside is not
removed from the codebase, it is re-scoped; Gorrahk keeps it byte-identically. The rest of the
B7 pass (physres cap 30/45/60, flat armour 150/260/400, +25% HP) answers a **different** Will
decision about physical immunity and is untouched for both families. Vashkarr's fire package is
held flat rather than retired, so his dragonian heritage survives the retune. The ledger and the
wave reports were checked for design intent naming any of these fields before touching them.

**Debt found in passing:** the B7 pass is an **unledgered Will decision**. Its only record is the
verbatim quote in the docstring ("crazy on normal, 74% physical damage resistance? doesnt that
make you nearly unkillable by physical hits that arent piercing?"), never assigned an R-number.
R-72 documents the supersession by function name rather than inventing a number; the gap is
registered as debt below.

---

## 6. THE GATE (standing law 4: no new surface without a gate)

### 6.1 New contract `SOUL-IDENTITY-SHAPE` in `tools/contracts/contracts_souls.py`

A **declarative registry**, `SOUL_IDENTITY_SHAPES`, binds a ruling to an asserted field shape, so
future identity retunes register the same way instead of hand-rolling a checker:

```python
'vashkarr': {
    'ruling': 'R-72',
    'dir': r'records\item\equipmentring\soul\svc_uber',
    'fields': {
        'offensivePierceModifier':      {'min': 1.0,  'order': 'increasing', ...},
        'offensivePierceRatioModifier': {'min': 1.0,  'order': 'increasing', ...},
        'characterRunSpeedModifier':    {'min': 1.0,  'order': 'increasing', ...},
        'offensiveElementalModifier':   {'min': -8.0, 'max': -6.0,
                                         'order': 'non_decreasing', ...},
    },
},
```

`_c_identity_shape` runs against the **final built .arz**, so it catches a later pass clobbering
an earlier ruling back out. It asserts, per family:

- all three tiers exist;
- every mandated field is present and numeric on every tier;
- pierce damage, penetration and movement are **positive** (`min: 1.0` - a negative run speed,
  i.e. today's shipped state, fails on the bound);
- the elemental penalty is **within Will's -8..-6 band** on every tier;
- **tier ordering**: `increasing` (strict n < e < l) for the three bonuses, `non_decreasing`
  (never worse at a higher tier) for the drawback.

### 6.2 Planted negative tests in `tools/contracts/tests_souls_negative.py`

Case 11, **eight assertions**, all mutating the in-memory db only (nothing is written):

| # | planted state | expectation |
|---|---|---|
| 1 | the shipped R-72 shape, untouched | contract **silent** |
| **2** | **`characterRunSpeedModifier = -8.0` on all 3 tiers - i.e. EXACTLY today's shipped pre-R-72 state** | contract **FIRES** |
| 3 | the speed bonus restored | contract silent |
| 4 | `offensivePierceModifier = 0` on Epic (spear identity deleted) | contract FIRES |
| 5 | penetration inverted (Legendary set below Normal) | contract FIRES |
| 6 | elemental penalty pushed out of band (-25) | contract FIRES |
| 7 | elemental penalty **deepening** with rarity (-6/-7/-8): still inside the band on every tier, so **only** the `non_decreasing` ordering rule can catch it | contract FIRES |
| 8 | the elemental band restored | contract silent |

Assertion 2 is the negative test the brief asked for: it reproduces the current speed-penalty
state and that state fails the gate. Assertions 1/3/8 are the mirror halves that stop the contract
from being a checker that fires on everything.

A `_num()` helper tolerates an absent field when capturing originals, so pointing the suite at a
pre-R-72 arz reports rather than crashes.

---

## 7. PROOFS

Build command (both runs identical apart from the code change):

```
PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 py tools/build_svc_database.py \
  upstream/soulvizier_098i/Database/database.arz \
  upstream/soulvizier_0.9/Database/database.arz \
  upstream/soulvizier_041/Database/database.arz \
  <out>.arz \
  "<TQAE>/Database/database.arz"
```

`upstream/` was read from the MAIN repo tree (a worktree does not carry the gitignored sources).

### 7.1 Hashes

| artifact | md5 |
|---|---|
| **built arz (this lane)** | **`b88871f25e28791e6ffa00deea223af3`** |
| baseline arz (worktree main HEAD `8c3445c`, pre-change) | `1c27d5fa650b5c076696db4ad379672f` |
| built `Text.arc` (coupled pair) | `fcca49277b9d31ed451e4a6843898843` |
| `uber_soul_tags.txt` (build-emitted manifest) | `49b6d85ba15236aa5df60f610e3a7bf0` |
| `mod_authored_tags.txt` (Text-build-emitted) | `7836504539e3a4776b60a58c7cb1d0bb` |

**Built artifacts for the orchestrator to merge** (durable copies, outside the session scratchpad):

```
C:/Users/willi/repos/tqit_soulvizier_classic/local/lane_builds/b96_vashkarr_soul.arz            (55,424,191 B, md5 b88871f2...)
C:/Users/willi/repos/tqit_soulvizier_classic/local/lane_builds/b96_vashkarr_Text.arc            (88,699 B,     md5 fcca4927...)
C:/Users/willi/repos/tqit_soulvizier_classic/local/lane_builds/b96_vashkarr_uber_soul_tags.txt  (32,168 B,     md5 49b6d85b...)
```

**PROVENANCE / DETERMINISM PROOF.** The baseline rebuild came out at
`1c27d5fa650b5c076696db4ad379672f`, which is **byte-identical to the arz recorded as the b91 build**
in the BACKLOG gate record. So the pipeline reproduced the current main-HEAD artifact exactly before
a single field was touched, and every byte of difference below is attributable to this lane.

**Text.arc is byte-identical to the shipped one** (`fcca4927...`, the same md5 recorded for b90 and
b91): this lane changes no tag. The coupled pair is still rebuilt and shipped together per the
standing arz+Text coupling rule.

**NOT DEPLOYED.** Nothing was written to `CustomMaps\SoulvizierClassicDEV`. `Levels.arc` and
`Quests.arc` were never touched (no map tooling ran).

### 7.2 Record-diff vs baseline: the 3 intended records ONLY

```
ADDED   (0)
REMOVED (0)
CHANGED (3):
  records\item\equipmentring\soul\svc_uber\vashkarr_soul_n.dbr
      characterAttackSpeedModifier:  (9.6,)    ->  (10.8,)
      characterOffensiveAbility:     (54.0,)   ->  (66.0,)
      characterRunSpeedModifier:     (-8.0,)   ->  (12.0,)
      offensiveElementalModifier:    None      ->  (-8.0,)
      offensiveLifeLeechMin:         (15.0,)   ->  (18.0,)
      offensivePhysicalMax:          (57.0,)   ->  (74.4,)
      offensivePhysicalMin:          (36.0,)   ->  (46.8,)
      offensivePhysicalModifier:     (21.0,)   ->  (27.6,)
      offensivePierceModifier:       None      ->  (40.0,)
      offensivePierceRatioModifier:  None      ->  (35.0,)
      offensiveSlowBleedingMin:      (72.0,)   ->  (90.0,)
  records\item\equipmentring\soul\svc_uber\vashkarr_soul_e.dbr
      characterAttackSpeedModifier:  (13.1,)   ->  (14.8,)
      characterOffensiveAbility:     (73.8,)   ->  (90.2,)
      characterRunSpeedModifier:     (-8.0,)   ->  (17.0,)
      offensiveElementalModifier:    None      ->  (-7.0,)
      offensiveLifeLeechMin:         (20.5,)   ->  (24.6,)
      offensivePhysicalMax:          (77.9,)   ->  (101.7,)
      offensivePhysicalMin:          (49.2,)   ->  (64.0,)
      offensivePhysicalModifier:     (28.7,)   ->  (37.7,)
      offensivePierceModifier:       None      ->  (58.0,)
      offensivePierceRatioModifier:  None      ->  (50.0,)
      offensiveSlowBleedingMin:      (98.4,)   ->  (123.0,)
  records\item\equipmentring\soul\svc_uber\vashkarr_soul_l.dbr
      characterAttackSpeedModifier:  (16.0,)   ->  (18.0,)
      characterOffensiveAbility:     (90.0,)   ->  (110.0,)
      characterRunSpeedModifier:     (-8.0,)   ->  (22.0,)
      offensiveElementalModifier:    None      ->  (-6.0,)
      offensiveLifeLeechMin:         (25.0,)   ->  (30.0,)
      offensivePhysicalMax:          (95.0,)   ->  (124.0,)
      offensivePhysicalMin:          (60.0,)   ->  (78.0,)
      offensivePhysicalModifier:     (35.0,)   ->  (46.0,)
      offensivePierceModifier:       None      ->  (78.0,)
      offensivePierceRatioModifier:  None      ->  (65.0,)
      offensiveSlowBleedingMin:      (120.0,)  ->  (150.0,)

TOTAL DIFFERING RECORDS: 3
```

**Exactly the 3 named records, 11 fields each, 0 added, 0 removed.** In particular the
`gorrahk_soul_{n,e,l}` records do **not** appear, which is the positive proof that scoping the B7
run-speed clause left Gorrahk byte-identical. Re-probe of the built arz:

```
vashkarr  N: pierceMod=40.0(dt1)  pierceRatioMod=35.0(dt1)  runSpeed=12.0(dt1)  elemMod=-8.0(dt1)
vashkarr  E: pierceMod=58.0(dt1)  pierceRatioMod=50.0(dt1)  runSpeed=17.0(dt1)  elemMod=-7.0(dt1)
vashkarr  L: pierceMod=78.0(dt1)  pierceRatioMod=65.0(dt1)  runSpeed=22.0(dt1)  elemMod=-6.0(dt1)
gorrahk N/E/L: pierce absent, elemental absent, runSpeed=-8.0(dt1)   <- UNCHANGED
```

All four fields land at **dtype 1 (FLOAT)**, matching their donors exactly. No dtype corruption.

### 7.3 Verify battery

| Gate | Result |
|---|---|
| DB build | **exit 0**, every fail-loud invariant green. Soul-leak invariant OK (0 non-Hero/Boss/Quest creatures drop a soul); soul-augment, supra-ref, tags, spawn-eligibility, A9 render-chain, b77 unlock-alignment all green. |
| **`souls_quality.verify` (the monotonicity + tier-progress gate)** | **OK** - "roster tiers monotonic (n<=e<=l) AND strictly progressing (epic>normal, legendary>epic on some scaled field; b78 Blood Cult High Priest gate) across every soul family + per-tier svc_uber icons correct + roster-wide companion summons manual-cast + tombguardian soul retired". `_FLAT_TIER_WAIVER` still EMPTY. |
| Registry verify hooks (in-build, final merged arz) | **24 module verifies ran, 0 failures.** |
| `tools/patches/_check_registry.py` | **OK** - 33 modules, order hash `9bca0f20fd87c7da...` |
| A7 Occult/Hunting golden guard | **PASS** (90 waived owner-approved, **0 other**) |
| b77 unlock-alignment | **PASS** - every live button's skillTier == drawn row, 13/13 waivers in manifest |
| `tools/validate_tags.py` (arz + Text.arc + uber_soul_tags + mod_authored_tags + base Text_EN) | **PASS** (exit 0) - 356/356 referenced mod tags present, 417/417 authoritative tags present. 2 WARNs (`tagNewMonster66`, `tagNewMonster46`) are the documented pre-existing base/SV pair, non-blocking, unchanged. |
| Contracts `--only souls,summons` on the BUILT arz | **GATE PASS** - **0 P0 / 0 P1 / 112 P2**. souls lane **0/0/0**. |
| `tests_souls_negative.py` | **21/21 assertions PASS** (13 pre-existing + 8 new) |

### 7.4 Pre-existing violation count is provably unchanged

Same command, same Text/Resources, only the arz swapped:

| run | P0 | P1 | P2 | gate |
|---|---|---|---|---|
| **baseline** arz (pre-change) | 0 | **13** | 112 | FAIL |
| **built** arz (this lane) | 0 | **0** | 112 | **PASS** |

The 13 baseline P1 are **every one of them `SOUL-IDENTITY-SHAPE`, all on the three vashkarr
records**: 3x absent `offensivePierceModifier`, 3x absent `offensivePierceRatioModifier`, 3x absent
`offensiveElementalModifier`, 3x `characterRunSpeedModifier=-8.0 (must be >= 1.0)`, and 1x
`characterRunSpeedModifier n/e/l = [-8.0, -8.0, -8.0]` failing the increasing-order rule. **Every
other souls contract reports 0 P0 / 0 P1 / 0 P2 on that same baseline run**, and the summons P2
count is **112 in both runs**, so no pre-existing violation regressed and the P1 delta is
attributable in full to this lane's own new contract.

This doubles as the **real-world negative proof** demanded by the no-new-surface law: the contract
fails the pre-change artifact and passes the post-change one, independently of the planted
in-memory tests.

### 7.5 Negative-test output (verbatim tail)

```
=== contracts_souls NEGATIVE TESTS ===
  [PASS] SOUL-SKILL-REF-RESOLVES fires on dangling ref
  [PASS] SOUL-ITEMCOST-RESOLVES fires on dangling cost
  [PASS] SOUL-ICON-RESOLVES fires on missing icon
  [PASS] SOUL-ICON-RESOLVES fires on empty bitmap
  [PASS] SOUL-PROC-ACTIVATION fires on itemSkillLevel==0
  [PASS] SOUL-PROC-ACTIVATION silent after restore
  [PASS] SOUL-AUGMENT-LEVEL fires on augmentSkillLevel1==0
  [PASS] SOUL-NAME-RESOLVES fires on unresolved tag
  [PASS] SOUL-NAME-COLOR fires on non-{^F} name
  [PASS] SOUL-LEVEL-ONLY fires on nonzero stat requirement
  [PASS] SOUL-GRANT-USABILITY fires on non-grantable Class
  [PASS] SOUL-DROP-CLASSIFICATION fires on non-HBQ soul drop
  [PASS] SOUL-DROP-CLASSIFICATION silent at chance 0
  [PASS] SOUL-IDENTITY-SHAPE silent on the shipped R-72 shape
  [PASS] SOUL-IDENTITY-SHAPE fires on the pre-R-72 -8% speed PENALTY
  [PASS] SOUL-IDENTITY-SHAPE silent after the speed bonus is restored
  [PASS] SOUL-IDENTITY-SHAPE fires when pierce damage is zeroed
  [PASS] SOUL-IDENTITY-SHAPE fires on penetration tier INVERSION
  [PASS] SOUL-IDENTITY-SHAPE fires on out-of-band elemental penalty
  [PASS] SOUL-IDENTITY-SHAPE fires when the drawback DEEPENS with tier
  [PASS] SOUL-IDENTITY-SHAPE silent after the drawback band is restored

21/21 assertions PASS
```

The build-log line proving the second edit took effect:

```
A8/B7: Eldest+Gorrahk soul physres -> 30/45/60 + flat armor + HP (6 soul tier records; no longer
physical-immune); -8% run speed now GORRAHK-ONLY (R-72: Vashkarr carries a run-speed BONUS + a
-6..-8% elemental drawback instead)
```

---

## 8. IDENTITY CHECK (amgoz1 creative bar)

Does the result read as Vashkarr, or as stat soup?

The soul's centre of gravity **moved**, which is what stops this being a stat pile. Before, it was
a symmetrical physical+fire brick that also made you slow. After, it is a specific fighter:

- **A spear.** Pierce damage AND pierce ratio together are the mechanically correct rendering of a
  lance: the ratio converts his big physical hit into armour-bypassing pierce, so the two fields
  compound instead of sitting side by side. It is the same pairing amgoz1 used on 46 of his own
  souls, and the boss record is literally a `bm_deathlance_32` clone.
- **A shield.** The B7 half kept intact is exactly the shield half of the character: 30/45/60%
  physical resistance plus 150/260/400 flat armour, plus the existing `defensiveReflect` 6/9/12.
  Not touched, because it was already right.
- **Fast.** "This guy should be fast" is now literally true, and it is the single most visible
  reversal in the tooltip: a -8% penalty became a +12/+17/+22% bonus.
- **Weak to the elemental.** The cost is the one thing age would take from an ancient dragonian:
  **the flame**. His fire package is deliberately **held flat** while physical and pierce grow, so
  the -6..-8% elemental line is not an arbitrary tax bolted onto an unrelated build; it taxes the
  exact axis the retune is walking away from. Fire Enchantment stays as augment slot 1 (heritage
  preserved, nothing retired) and Onslaught in slot 2 is already the Warfare spear skill.

Net, in Will's own words, the soul "trades elemental power for speed and piercing lethality". The
lore string `tagSVCSoulVashkarrDESC` still fits without an edit: *"It burns with the fury of an age
the world has forgotten"* now reads as a fury that has outlasted its fire.

**Player-surface checklist (standing law 3).** This lane changes **stats only**. Name tag, desc
tag, icon (`soul_{n,e,l}_icon.tex`, per-tier and gate-verified), mesh, drop source
(`um_vashkarr_99` @ 66% Finger2), item classification, level requirement, relic slot and both
augment grants are all **unchanged and re-verified in the built arz**. No new player-visible
surface is created, so nothing is deferred.

---

## 9. DEBT REGISTER

Registered in `docs/BACKLOG.md` DEBT REGISTER as **BL-b96-DEBT-1..5** (standing law 4).

1. **BL-b96-DEBT-1 (P2, launch-gated):** not in-game confirmed. TQ bakes item properties at pickup,
   so **Will must test on a FRESHLY dropped soul** (kill `um_vashkarr_99` again, 66% drop) after the
   orchestrator's merged deploy and a full TQ + Steam restart. An already-held soul will not change.
2. **BL-b96-DEBT-2 (P2, unproven engine behaviour):** a NEGATIVE `offensiveElementalModifier` is
   carried by exactly one shipped item in the whole database. The field is unquestionably live
   (193 non-zero records), but that a negative composite elemental modifier renders and applies as
   "-X% Elemental Damage" rather than clamping at 0 is inferred from the donor, not observed.
   Fallback if the tooltip shows nothing: per-element negative `offensiveFireModifier` (precedent
   `ikaie_soul` / `coldtusk_soul`), at the cost of covering only fire.
3. **BL-b96-DEBT-3 (P2, unproven semantics):** the pierce-damage vs pierce-ratio (penetration)
   split follows Will's named donor and 46 shipped souls but has not been measured in game.
4. **BL-b96-DEBT-4 (P2, ledger gap found in passing):** `_apply_b7_eldest_soul_rebalance` implements
   an **unledgered** Will decision (quote lives only in its docstring, no R-number), so R-72 had to
   cite it by function name. A rulings-backfill lane should number it, and a sweep for other
   decisions living only in docstrings is likely worthwhile.
5. **BL-b96-DEBT-5 (P3, dead write):** `_create_vashkarr` sets `tagSVCSoulVashkarr` to
   `{^F}Soul of the Eldest`, which the later F6 `_SOUL_NAME_STANDARD` pass unconditionally
   overwrites with the shipped `{^F}Vashkarr, Eldest of the Ancients Soul`. Harmless today, but a
   silent ordering dependency: reordering the passes would rename the soul. Deliberately NOT touched
   here (out of scope, and touching it risks the name Will used).

---

## 10. HANDOFF TO THE ORCHESTRATOR

- **Do NOT deploy this arz on its own.** It was built from `main` + this lane only; deploying it
  would revert every other in-flight lane's edits. It is offered for the single merged deploy.
- Merge `feat/vashkarr-soul` (5 files: `tools/apply_svc_patches.py`,
  `tools/contracts/contracts_souls.py`, `tools/contracts/tests_souls_negative.py`,
  `docs/WILL_RULINGS.md`, `docs/BACKLOG.md`, plus this new report) and **rebuild** rather than
  merging the binary, since the arz cannot be merged.
- After the merged rebuild, the lane is re-verifiable in one command: contracts
  `--only souls` must report **0 P0 / 0 P1** with `SOUL-IDENTITY-SHAPE` silent. That contract is
  now the permanent guard that no later pass clobbers R-72 back out.
- Will's test instruction, per the standing restart rule: kill TQ **and** Steam, restart, confirm
  the deploy landed by hash, then kill Vashkarr in his cave and pick up a **newly dropped** soul.
