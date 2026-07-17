# b77 - Mastery Skill Unlock-Alignment FIX WAVE (round 1, build45)

**Directive (Will 2026-07-16, verbatim greenlight):** "Proceed with fixing the masteries as
appropriate." Implement the confirmed b74 unlock-alignment audit with sensible defaults; every
judgment call is a **WILL-VETO** line below for his DEV pass.

**Authority:** `docs/reports/b74_unlock_alignment_audit.md` + `tools/unlock_alignment_audit.json`
(audit CONFIRMED by independent byte-level re-derivation, zero corrections) + the committed GT JSONs.
**Subject:** build45 `SoulvizierClassic.arz` md5 **917d9047**d2281284f5fd5e9a163b9c5c (read-only ref).
**This wave's built arz:** md5 **7718d584**1810034e73e7c1dfdc68788a (scratch determinism build).

**Mechanism law (proven, re-derived):** effective_unlock = max(pointThreshold(skillTier), req);
skillTier PRIMARY; thresholds 1/4/10/16/24/32/40; row geometry Y=465-62*tier -> rows t1..t7 Y
{403,341,279,217,155,93,31}; columns X {128,228,328,428,528,628}; connectors = record-driven
skillConnectionOn/Off on the family base; modifier<->base binding = SkillTree slot ORDER (this wave
NEVER touches a SkillTree record, so every binding is preserved by construction).

Implemented as the registry module `tools/patches/mastery_unlock_alignment.py` (apply + verify),
registered LAST among the mastery-UI writers (after `mastery_sv_alignment`, before `visuals`), plus
the permanent build gate `tools/gate_unlock_alignment.py` (wired into `build_svc_database.py` right
after the A7 golden guard).

---

## 1. Per-fix table (every changed skill: before row/gate -> after row/gate -> authority)

`gate` = effective unlock points. `row` = drawn row. Kind: **FIX-ROW** (move button to the tier's
row), **FIX-GATE** (re-tier to the drawn row), **retire**.

| # | mastery | skill (record) | before row / tier / gate | after row / tier / gate | kind | authority |
|---|---|---|---|---|---|---|
| A1 | m7 Spirit | drxdistortionwave_chaoticresonance (button skill28) | row4 / t3 / 10 | **row3** / t3 / 10 | FIX-ROW | b74 §3; Dream m9 twin row3/t3; shared skill record |
| A2 | m7 Spirit | drxdistortionwave_psionicimmolation (button skill29) | row6 / t5 / 24 | **row5** / t5 / 24 | FIX-ROW | b74 §3; Dream m9 twin row5/t5; shared skill record |
| A3 | m7 Spirit | drxdeathchillaura_ravagesoftime (button skill07) | col3 row3 / t3 / 10 | **col4** row3 / t3 / 10 | move (free cell) | vacate col3 r3 for A1 (WILL-VETO) |
| A4 | m7 Spirit | drxdeathchillaura_necrosis (button skill08) | col3 row5 / t5 / 24 | **col4** row5 / t5 / 24 | move (free cell) | vacate col3 r5 for A2 (WILL-VETO) |
| B1 | m2 Defense | drx_summonphalanx | row5 / t7 / 40 | row5 / **t5** / **24** | FIX-GATE | b74 §3 lean (align to drawn row5) |
| B2 | m4 Storm | drxfrostnova | row5 / t6 / 32 | row5 / **t5** / **24** | FIX-GATE | b74 §3 lean (align to drawn row5) |
| B3 | m4 Storm | drx_lightningdash | row7 / t5 / 24 | row7 / **t7** / **40** | FIX-GATE | b74 §3 lean (align to drawn row7) |
| C1 | m1 Warfare | drx_clubslam (button skill26) | col3 row7 / t2 / 4 | col3 **row1** / **t1** / **1** | FIX-ROW+GATE | b74 §3 col3 restack (WILL-VETO) |
| C2 | m1 Warfare | drx_clubslam_fissure (button skill27) | col3 row4 / t7 / 40 | col3 **row2** / **t2** / **4** | FIX-ROW+GATE | ClubSlam modifier, adjacent above (WILL-VETO) |
| C3 | m1 Warfare | drx_ancestralmod / Lasting Legacy (button skill28) | col3 row2 / t7 / 40 | col3 **row7** / t7 / 40 | FIX-ROW | ultimate to its real-tier top row |
| C4 | m1 Warfare | drxhamstring (button skill25) | col4 row3 / t4 / 16 | col4 **row4** / t4 / 16 | FIX-ROW | align in col4 to real tier4 (WILL-VETO) |
| D1 | m3 Earth | drxringofflame_softenmetal (button skill10) | row2 / t3 / 10 | row2 / **t2** / **4** | FIX-GATE | b74 §3; SV row3 blocked by restored Rupture (WILL-VETO) |
| D2 | m3 Earth | drxrupture (button skill26) | row3 / t1 / 1 | row3 / **t3** / **10** | FIX-GATE | b70 note: intentional Flame-Surge restoration @r3 (WILL-VETO) |
| D3 | m3 Earth | drxrupture_burning (button skill27) | row4 / t3 / 10 | row4 / **t4** / **16** | FIX-GATE | Rupture modifier, ladders col4 |
| D4 | m3 Earth | drxspontaneouscombustion (button skill23) | row6 / t5 / 24 | row6 / **t6** / **32** | FIX-GATE | b74 §3 (align to drawn row6) |
| D5 | m3 Earth | drx_firenova (button skill25) | row7 / t6 / 32 | row7 / **t7** / **40** | FIX-GATE | b74 §3B FireNova (Earth ultimate @top) |
| E  | m4 Storm | skill25 -> drxspellbreaker_spellshock2 (MISSING) | live col1 row3 | **retired** (delisted from 3 panectrls) | retire | b74 §6 broken button (see §4) |

Connector repairs (family bars, no button move): **drx_clubslam** len6 off-grid overshoot ->
adjacent len2 [Bottom,Top] up to Fissure; **drxringofflame** len3 -> len2 (Soften Metal now
adjacent at row2); **drxrupture** len5 -> len3 [Bottom,Middle,Top] spanning row3->row5 (mods Burning
r4 + Flare r5). Rupture Flare (m3 skill28) already aligned (t5/row5) - not written.

---

## 2. WILL-VETO ladder designs

### 2a. Warfare col3 (grafted family) - WILL-VETO

The Battle Standard family (base row3 + petmods row5/row6, a len4 bar spanning rows 3-6) is ALIGNED
and KEPT untouched. The grafted family is seated in col3 cells OUTSIDE that bar corridor:

```
col3 (X=328)                      col4 (X=428, Onslaught chain)
 row7  Lasting Legacy   t7  40      row7  Ardor            t7  40
 row6  Triumph (petmod)  -  (BattleStd)   (empty)
 row5  Glory  (petmod)   -  (BattleStd)   row5  Craven      t5  24
 row4  (empty; BattleStd bar passes here) row4  Hamstring   t4  16   <- moved up from row3
 row3  Battle Standard  t3  10  base      (empty)
 row2  Slam Fissure     t2  4   } adjacent row2  Ignore Pain t2  4
 row1  Club Slam        t1  1   } len2 bar row1  Onslaught   t1  1
```

- **WILL-VETO (C1/C2):** Club Slam FIX-GATE t2->t1 and Slam Fissure FIX-GATE t7->t2 to seat the
  base+modifier pair adjacently at the clear bottom of col3 (a basic club attack + its modifier at a
  low unlock is coherent, and this REPAIRS Club Slam's broken 6-tile off-grid upward bar). Alternative:
  keep t2/t7 and place them elsewhere - but col3 has no other clear adjacent pair of cells.
- **WILL-VETO (C4):** Hamstring is grafted into the Onslaught column (col4), which carries a
  full-height Onslaught bar; there is NO clean col3 cell for it (col3 row4 sits inside the Battle
  Standard bar corridor and would cross it). It is aligned IN col4 by FIX-ROW row3->row4 = its real
  tier4 (unlock 16). Alternative: FIX-GATE to t3 (audit's other option) keeps it at row3.

### 2b. Earth col4 (Ring-of-Flame + Rupture families) - WILL-VETO

col4 is ALREADY a filled row1..row7 ladder; only the tiers drifted + two bars overshot. NO buttons
move - this is an in-place re-tier + bar repair:

```
col4 (X=428)                         tier  gate
 row7  Fire Nova                      t7    40   (Earth ultimate)   [D5]
 row6  Spontaneous Combustion         t6    32                      [D4]
 row5  Rupture Flare      } Rupture    t5    24   (unchanged)
 row4  Rupture Burning    } family     t4    16                      [D3]
 row3  Rupture (Flame Surge, restored) t3   10                      [D2]
 row2  Soften Metal  } Ring of Flame   t2    4                       [D1]
 row1  Ring of Flame } family          t1    1    (req10 waiver)
```

- **WILL-VETO (D1):** Soften Metal re-tiered t3->t2. Its SV098 GT is t3/row3, but row3 is occupied
  by the intentionally-restored Rupture "Flame Surge" base (b70 note; a build41 legacy restoration).
  Seating Soften Metal at row2 (adjacent above Ring of Flame) is the only coherent alternative.
- **WILL-VETO (D2):** Rupture re-tiered t1->t3 to match its intentional row3 seat (Flame Surge
  restoration is design intent, not a bug).

---

## 3. The E decision (Storm broken button) - WILL-VETO

`records\ingameui\player skills\mastery 4\skill25.dbr` points `skillName` at
`records\skills\storm\drxspellbreaker_spellshock2.dbr`, which **does not exist**. The only existing
variant `drxspellbreaker_spellshock` IS a real castable skill - but it is **already live as
"Inversion"** (m4 skill14, col4 row6). Repointing skill25 to it would DUPLICATE the Inversion button.

**DECISION: RETIRE skill25.** Removed from all three mastery-4 `panectrl.tabSkillButtons` copies
(`ingameui` + `xpack` + `xpack3`) so the engine never renders it; the button record is left
orphaned (parked). No black-hole button remains. **WILL-VETO:** retired (not repointed) because the
sole existing variant is already the live Inversion button; if Will wants a distinct second
spellshock skill, that record must be authored first.

---

## 4. REQ-EXCEEDS-ROW waiver list (permanent gate)

13 SV-faithful secondary floors where tier==row but `skillMasteryLevelRequired` lifts the effective
gate above the row threshold (vanilla ships 14 of the same modifier / leaf chain-slot class; 11 of 13
match SV098's own req byte-for-byte). Each is waived in `tools/gate_unlock_alignment.py`:

| skill | m | row/thr | req | citation |
|---|---|---|---|---|
| drxdualwieldtechnique_crosscut | 1 | r4/16 | 24 | SV098 (audit §5) |
| drxwarwind (War Dance) | 1 | r2/4 | 15 | SV098 |
| drxwarwind_lacerate | 1 | r4/16 | 25 | SV098 |
| drxwarwind_refinement | 1 | r5/24 | 25 | overlay, no SV098 GT, +1 benign |
| drxbatter_rendarmor | 2 | r3/10 | 15 | SV098 |
| drxrally_defiance | 2 | r5/24 | 30 | SV098 |
| drxringofflame | 3 | r1/1 | 10 | SV098 |
| drxensnare_barbednetting | 6 | r3/10 | 24 | SV098 |
| drxherbalism | 6 | r2/4 | 5 | SV098 |
| drxweaponskill_gouge | 6 | r1/1 | 5 | SV098 |
| drxvisionofdeath | 7 | r1/1 | 5 | SV098 |
| drxsoulsiphontotem | 7 | r2/4 | 5 | overlay, no SV098 GT, +1 benign |
| drxplague_fatigue | 8 | r4/16 | 18 | SV098 |

The other 6 skills that exceeded their row threshold in build45 (hamstring, clubslam_fissure,
ancestralmod, summonphalanx, softenmetal, frostnova) were TIER-DRIFTS - fixed by this wave, no longer
over-gated.

---

## 5. Verification (all green)

| check | result |
|---|---|
| full scratch DB build | SUCCESS (arz 7718d584) |
| A7 golden guard (Occult m5 / Hunting m6) | **PASS** (84 waived, 0 other; wave touches only m1/2/3/4/7) |
| unlock-alignment gate (238 live buttons) | **PASS** (0 tier-drift, 0 req-over, 13/13 waivers hit) |
| negative test (plant drifted tier) | **PASS** (gate catches it) |
| mastery_sv_alignment.verify (DI mechanism, m5/m6 bindings) | green (build completed past registry verifies) |
| record-diff vs 917d9047 | **exactly this wave**: 22 records, 0 added/removed; only bitmapPositionX/Y, skillTier, skillConnectionOn/Off, tabSkillButtons (E). NO gameplay stat fields. NO skillMasteryLevelRequired changed (none exceeded threshold). |
| 9 live SkillTree records vs build45 | **slot-order identical** (modifier bindings intact by construction) |
| contracts souls/summons/resources | **no new P0/P1**: baseline 0 P0 / 576 P1 / 10717 P2 == this wave 0 P0 / 576 P1 / 10717 P2 (disjoint monster/soul record set) |
| validate_tags | **PASS** (wave adds no tag references) |
| idempotency (double apply) | **PASS** |

Note: the map contract is N/A - this is a DB-only wave (no Levels/Quests change).
