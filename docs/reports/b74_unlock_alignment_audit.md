# b74 - Mastery Skill Unlock-Alignment Audit (build45)

**Directive (Will 2026-07-16):** "audit all the skills to see which skills have a real unlock number
of points in the tree required that is not aligned with where they are placed in the mastery
selection page (they are placed on a too high or too low row based on the number of points in the
tree needed to get the skill)."

**Lane:** READ-ONLY recon. No git, no code/pipeline changes. Pure-Python `arz_patcher` replay; no
game, no build. Outputs: this report + `tools/unlock_alignment_audit.json` (machine-readable full
sweep, every skill including aligned ones, so a fix lane can gate on it).

- **Subject:** build45 `work/SoulvizierClassic/Database/SoulvizierClassic.arz` (md5 **917d9047**d2281284f5fd5e9a163b9c5c).
- **Vanilla reference:** TQAE `Database/database.arz` (field calibration).
- **Cross-referenced ground truth:** `tools/sv_mastery_ground_truth.json` (SV098),
  `tools/sv_pre098i_occult_ground_truth.json` (SV 0.41/0.9), `docs/reports/sv_mastery_ground_truth.md`.

---

## 0. Headline

| metric | value |
|---|---|
| total skill-button records audited (all 9 masteries) | **239** |
| live (in `panectrl.tabSkillButtons`) / hidden | **239 / 0** |
| off-grid (Y not on the 7-row lattice) | **0** |
| **TIER-DRIFT mismatches (skillTier != drawn row)** | **14** (vanilla baseline: 0) |
| &nbsp;&nbsp;- deceptive-LATE (locked when the row implies available) | **6** |
| &nbsp;&nbsp;- benign-early (unlocks before the row implies) | **8** |
| REQ-EXCEEDS-ROW (secondary, by-construction, tier==row) | 13 (vanilla baseline: 14) |
| broken button (dangling skillName, no gate to read) | 1 |
| fully aligned | 211 |

The **14 TIER-DRIFT skills are the answer to the directive**: their real unlock gate is on a
different row than where the button is drawn. Vanilla has zero of these, so all 14 are mod-introduced.
The 13 REQ-EXCEEDS-ROW cases faithfully reproduce SV098/vanilla (11 of 13 match SV098's own
`skillMasteryLevelRequired` byte-for-byte) and are **not** mod defects.

---

## 1. FIELD CALIBRATION (make-or-break) - which field is the unlock gate?

**Proven gate:** `effective_unlock_points = max(pointThreshold(skillTier), skillMasteryLevelRequired)`,
where `pointThreshold(tier 1..7) = 1 / 4 / 10 / 16 / 24 / 32 / 40`.

**The primary field is `skillTier`, NOT `skillMasteryLevelRequired`.** Evidence, entirely from the
vanilla arz (trees aligned by construction), 180 displayed buttons across all 9 masteries:

| calibration test | result |
|---|---|
| `skillTier` == row implied by `bitmapPositionY` (Y=465-62*tier) | **142 / 142 tiered skills, 0 violations** |
| `skillMasteryLevelRequired` == threshold of the drawn row | equal **18**, below **109**, above **14**, absent 39 |

So `skillMasteryLevelRequired` does *not* track the row - it is below the row threshold for the
large majority. Two decisive vanilla records prove req-alone is not the gate:

- `battlestandard` : `skillTier=3` (10-pt row), `skillMasteryLevelRequired=0` - yet Battle Standard
  unlocks at 10 points, not immediately. The tier threshold binds.
- `ancestralhorn`  : `skillTier=6` (32-pt row), `skillMasteryLevelRequired=30` - yet the Warfare
  ultimate unlocks at 32, not 30. The tier threshold binds.

**`skillMasteryLevelRequired` is engine-read though (not vestigial):** the known b70 exemplar
`drxthrowingknife` was fixed by raising `skillMasteryLevelRequired` 5 -> 24 to match its tier-5 / row-5
(col6) placement. In build45 it is now fully consistent: `bitmapPositionY=155` (row5), `skillTier=5`,
`skillMasteryLevelRequired=24` - all three encodings agree at 24 points. So `req` acts as an
additional floor: `effective_gate = max(tier_threshold, req)`.

**Field semantics precisely:**
- `skillTier` = engine tier index 1..7 (points-in-mastery units via the fixed ladder 1/4/10/16/24/32/40).
  It is the row-unlock gate and, in a well-formed tree, equals the `bitmapPositionY` row.
- `skillMasteryLevelRequired` = a per-skill floor in points-in-mastery units. Usually <= the tier
  threshold (non-binding). When > the tier threshold it raises the effective gate above the drawn row.
- No off-by-one: tier N's row is `Y = 465 - 62*N`; row t1..t7 -> Y {403,341,279,217,155,93,31}.

**Vanilla misalignments that calibrate expectations (as the directive asked to report):** 14 vanilla
skills have `skillMasteryLevelRequired` *above* their drawn-row threshold (e.g. `dualwieldtechnique_crosscut`
req24 on the 16-row; `ensnare_barbednetting` req24 on the 10-row; `plague_fatigue` req18 on the 10-row).
These are **modifier / leaf chain-slots** where the row shows chain topology (a modifier is drawn above
its parent) and `req` is the true gate. They are by-construction, present in vanilla, and are the
baseline against which build45's 13 REQ-EXCEEDS-ROW cases are judged benign. Vanilla has **0** cases of
`skillTier != drawn row` - that class is always a defect.

---

## 2. Geometry law + method

- Row from button `bitmapPositionY`: `Y = 465 - 62*tier`; rows t1..t7 -> Y {403,341,279,217,155,93,31};
  point thresholds **1 / 4 / 10 / 16 / 24 / 32 / 40**. Columns `bitmapPositionX` {128,228,328,428,528,628}.
- **Effective record set (last-writer per path):** m1-8 = `records\ingameui\player skills\mastery N\skillNN.dbr`;
  m9 = `records\xpack\ui\skills\mastery 9\skillNN.dbr`. build45 ships **no** `ingameui` m9 and **no**
  `xpack` m1-8 twins, so the effective set is unambiguous (verified).
- Every mastery's `panectrl.dbr::tabSkillButtons` lists exactly the Mastery button + all its `skillNN`
  records, so **all 239 skill buttons are live; 0 hidden/latent buttons** exist in build45.
- Per skill: button `bitmapPositionY` -> drawn row -> row threshold; skill record `skillTier` -> tier
  threshold; skill record `skillMasteryLevelRequired`; `effective_gate = max(tier_threshold, req)`.

---

## 3. TIER-DRIFT mismatches (14) - the directive's answer

`delta = pointThreshold(skillTier) - pointThreshold(drawn row)`. **LATE** (delta>0) = the skill's real
gate is higher than its row implies -> **player-visible deception** (button sits on a reachable shelf but
stays locked). **early** (delta<0) = unlocks before the row implies (benign, but still a visual lie).

```
m  mastery   skill_record                        row rthr tier gate delta class
1  Warfare   drx_ancestralmod                    2   4    7    40   +36  LATE*
1  Warfare   drx_clubslam_fissure                4   16   7    40   +24  LATE*
2  Defense   drx_summonphalanx                   5   24   7    40   +16  LATE*
4  Storm     drxfrostnova                        5   24   6    32   +8   LATE*
1  Warfare   drxhamstring                        3   10   4    16   +6   LATE*
3  Earth     drxringofflame_softenmetal          2   4    3    10   +6   LATE*
3  Earth     drxrupture_burning                  4   16   3    10   -6   early
7  Spirit    drxdistortionwave_chaoticresonance  4   16   3    10   -6   early
3  Earth     drxspontaneouscombustion            6   32   5    24   -8   early
3  Earth     drx_firenova                        7   40   6    32   -8   early
7  Spirit    drxdistortionwave_psionicimmolation 6   32   5    24   -8   early
3  Earth     drxrupture                          3   10   1    1    -9   early
4  Storm     drx_lightningdash                   7   40   5    24   -16  early
1  Warfare   drx_clubslam                        7   40   2    4    -36  early
```
`rthr` = drawn-row threshold; `gate` = effective unlock points = `max(tier_threshold, req)`.

### Grouped by mastery, with recommended resolution

**m1 Warfare - col3 (Battle Standard column) is scrambled + col4 (Onslaught chain):**

| skill (record) | drawn | real gate | deception | resolution |
|---|---|---|---|---|
| `drx_ancestralmod` | col3 row2 (4) | tier7 -> **40** | **LATE +36** (worst) | **WILL-DECISION.** Overlay skill, no GT. Drawn on the 4-pt shelf but locked to 40. Col3 (ancestralmod/clubslam/clubslam_fissure vs battlestandard family) is scrambled - needs holistic reflow. Align tier<->row; if it is meant to be an ultimate, move it to row7 (Y=31); else drop skillTier to 2. |
| `drx_clubslam_fissure` | col3 row4 (16) | tier7 -> **40** | **LATE +24** | **WILL-DECISION.** Modifier of `drx_clubslam`; tier7 gate at 40 but drawn at row4. Should sit one row above its base; reflow col3. |
| `drx_clubslam` | col3 row7 (40) | tier2 -> **4** | early -36 | **WILL-DECISION.** A basic-attack drawn at the very top (40-pt shelf) but unlocks at 4. Likely FIX-ROW down to row2 (Y=341) with its fissure modifier above; reflow col3. |
| `drxhamstring` | col4 row3 (10) | tier4 -> **16** | **LATE +6** | **WILL-DECISION.** Onslaught-chain overlay (onslaught t1, ignorepain t2, hamstring **t4** at row3, craven t5, ardor t7). Clean fix: set `skillTier=3` (FIX-GATE) so the column ladders 1,2,3,5,7 = rows; or FIX-ROW to row4 (Y=217, currently empty). |

**m2 Defense - col4 (Battle Awareness column):**

| skill (record) | drawn | real gate | deception | resolution |
|---|---|---|---|---|
| `drx_summonphalanx` | col4 row5 (24) | tier7 -> **40** | **LATE +16** | **WILL-DECISION.** Overlay summon; col4 has focus(t4,row4), phalanx(**t7**,row5), ironwill(t6,row6), activeblock(t7,row7). Two t7 skills. Lean FIX-GATE `skillTier=5` (match row5, gate 24) unless phalanx is intended as an ultimate (then FIX-ROW to row7 - but row7 is taken by activeblock -> reflow). |

**m3 Earth - col4 is an over-packed merge of the Ring-of-Flame + Rupture families (4 drifts + 1 collision):**

| skill (record) | drawn | real gate | deception | resolution |
|---|---|---|---|---|
| `drxringofflame_softenmetal` | col4 row2 (4) | tier3 -> **10** | **LATE +6** | **FIX-ROW.** GT(SV098) row=3 and `skillTier=3` agree; `bitmapPositionY` drifted to row2. This is the documented "Earth Soften Metal MOVE (SV c4t3 -> build41 c4t2)" from `sv_mastery_ground_truth.md` sec 7a. Move to row3 (Y=279) - **but row3 is occupied by `drxrupture`**, so col4 needs a holistic reflow. |
| `drxrupture` | col4 row3 (10) | tier1 -> **1** | early -9 | **WILL-DECISION.** Overlay tier-1 base drawn two rows high. FIX-ROW to row1 (Y=403, taken by ringofflame) or FIX-GATE skillTier=3. Part of the col4 reflow. |
| `drxrupture_burning` | col4 row4 (16) | tier3 -> **10** | early -6 | **WILL-DECISION.** Rupture's burning modifier; tier3 but drawn row4. Reflow col4. |
| `drxspontaneouscombustion` | col4 row6 (32) | tier5 -> **24** | early -8 | **WILL-DECISION.** Overlay; FIX-GATE skillTier=6 (match row6) or FIX-ROW to row5 (taken). Reflow col4. |
| `drx_firenova` | col4 row7 (40) | tier6 -> **32** | early -8 | **WILL-DECISION.** Top-row ultimate drawn at row7 but `skillTier=6`. FIX-GATE skillTier=7 (match the top row / 40) is the natural fix for an ultimate. |

**m4 Storm - col4 (Spellbreaker column):**

| skill (record) | drawn | real gate | deception | resolution |
|---|---|---|---|---|
| `drxfrostnova` | col4 row5 (24) | tier6 -> **32** | **LATE +8** | **WILL-DECISION.** col4: spellbreaker(t3,row3), frostnova(**t6**,row5), spellshock(t6,row6), lightningdash(t5,row7). Lean FIX-GATE `skillTier=5` (match row5, gate 24). |
| `drx_lightningdash` | col4 row7 (40) | tier5 -> **24** | early -16 | **WILL-DECISION.** Drawn at the top (40) but `skillTier=5`. FIX-GATE skillTier=7 (ultimate) or FIX-ROW down. |

**m7 Spirit - col3 Distortion-Wave overlay COPIES drifted (the m9 originals are correct):**

The Distortion Wave family also lives in Dream (m9), where it is drawn correctly (`chaoticresonance`
row3/tier3, `psionicimmolation` row5/tier5). The Spirit copies were pushed one row down while keeping
their baked `skillTier`:

| skill (record) | drawn (m7) | m9 twin (correct) | real gate | resolution |
|---|---|---|---|---|
| `drxdistortionwave_chaoticresonance` | col3 row4 (16) | row3 | tier3 -> **10** | **FIX-ROW** to row3 (Y=279); GT+skillTier+m9-twin all say row3. Row3 is occupied by `drxdeathchillaura_ravagesoftime` -> reflow the Spirit col3 (two families interleaved). |
| `drxdistortionwave_psionicimmolation` | col3 row6 (32) | row5 | tier5 -> **24** | **FIX-ROW** to row5 (Y=155); occupied by `drxdeathchillaura_necrosis` -> same reflow. |

---

## 4. Off-grid buttons

**None.** All 239 live buttons sit on the 7-row lattice (Y in {403,341,279,217,155,93,31}). The
mastery-bar buttons sit off-grid at (29,459) by design and are not `skillNN` records (not counted).

---

## 5. REQ-EXCEEDS-ROW (secondary; by-construction, NOT actionable)

13 skills have `skillMasteryLevelRequired` above their drawn-row threshold while `skillTier` == the row
(so the tier/row agree; only the extra `req` floor lifts the effective gate). Vanilla has 14 of the
same class. **11 of 13 match SV098's own `req` byte-for-byte** (the `SV098gt` column) - they are
faithful reproductions of upstream design (modifier / leaf chain-slots), not mod defects.

```
m  mastery   skill_record                     row rthr req  +    mod    SV098gt
6  Hunting   drxensnare_barbednetting         3   10   24   +14  True   24
1  Warfare   drxwarwind (War Dance)           2   4    15   +11  False  15
1  Warfare   drxwarwind_lacerate              4   16   25   +9   True   25
3  Earth     drxringofflame                   1   1    10   +9   False  10
1  Warfare   drxdualwieldtechnique_crosscut   4   16   24   +8   False  24
2  Defense   drxrally_defiance                5   24   30   +6   True   30
2  Defense   drxbatter_rendarmor              3   10   15   +5   True   15
6  Hunting   drxweaponskill_gouge             1   1    5    +4   False  5
7  Spirit    drxvisionofdeath                 1   1    5    +4   False  5
8  Nature    drxplague_fatigue                4   16   18   +2   True   18
1  Warfare   drxwarwind_refinement            5   24   25   +1   True   (overlay)
6  Hunting   drxherbalism                     2   4    5    +1   False  5
7  Spirit    drxsoulsiphontotem               2   4    5    +1   False  (overlay)
```

Recommendation: **accept as upstream design** (matches SV098 + vanilla). If Will wants strict
"row shows the real gate" for the non-modifier ones (notably `drxwarwind`/War Dance +11 and
`drxringofflame`/Ring of Flame +9), lower `skillMasteryLevelRequired` to the row threshold - but this
changes long-standing SV balance, so it is a WILL-DECISION, not a bug fix. The two overlay cases
(`drxwarwind_refinement`, `drxsoulsiphontotem`) have no SV098 GT and only +1 delta - benign.

---

## 6. Broken button (data-integrity aside, not an alignment mismatch)

`records\ingameui\player skills\mastery 4\skill25.dbr` (Storm) points `skillName` at
`records\skills\storm\drxspellbreaker_spellshock2.dbr`, which **does not exist** in build45 (only the
non-"2" `drxspellbreaker_spellshock.dbr` exists). With no skill record there is no tier/req to read, so
it is outside the unlock-alignment mismatch counts, but it is a live button with a dangling skill and
should be repointed or removed.

---

## 7. Resolution summary for the fix lane

- **FIX-ROW (row is canonical - move `bitmapPositionY` to the tier's row):** 3 skills where GT and/or
  the m9 twin confirm the tier is canonical and the row drifted -
  `drxringofflame_softenmetal` (Earth, -> row3), `drxdistortionwave_chaoticresonance` (Spirit, -> row3),
  `drxdistortionwave_psionicimmolation` (Spirit, -> row5). Each lands on an occupied cell, so a small
  **holistic column reflow** is required (Earth col4, Spirit col3).
- **WILL-DECISION (overlay skills, no GT row):** the remaining 11 tier-drifts. For each, tier and row
  must be made equal; whether to move the button (FIX-ROW) or change the baked `skillTier`/`req`
  (FIX-GATE) depends on the intended unlock cost, which is Will's call. The 6 **deceptive-LATE** ones
  (`drx_ancestralmod` +36, `drx_clubslam_fissure` +24, `drx_summonphalanx` +16, `drxfrostnova` +8,
  `drxhamstring` +6, plus the FIX-ROW `drxringofflame_softenmetal` +6) are the priority - they are the
  ones that lie to the player as "available" while locked.
- **NO ACTION (by-construction):** the 13 REQ-EXCEEDS-ROW cases (match SV098/vanilla) and the 211
  aligned skills.
- **Separate defect:** repoint/remove the m4 `skill25` broken button.

Machine-readable full sweep (every skill, aligned included, with per-skill recommendation and
deception flag) for gating: **`tools/unlock_alignment_audit.json`**.
