r"""mastery_unlock_alignment - BUILD45/b77 UNLOCK-ALIGNMENT FIX WAVE (round 1).

Implements the confirmed b74 unlock-alignment audit
(docs/reports/b74_unlock_alignment_audit.md + tools/unlock_alignment_audit.json).
Every mastery skill button whose real unlock gate (skillTier -> point threshold)
did NOT match the row it is DRAWN on is brought into alignment, so a skill sitting
on a high row really does cost more mastery points and vice-versa (Will's directive
2026-07-16). Registered LAST among the mastery-UI writers (after mastery_sv_alignment),
so this module is the ratified final writer on the fields it touches for masteries
1/2/3/4/7. Its verify() re-asserts every fix on the FINAL assembled arz.

MECHANISM LAW (proven in the audit, byte-level re-derived, zero corrections):
  effective_unlock = max(pointThreshold(skillTier), skillMasteryLevelRequired)
  pointThreshold(tier 1..7) = 1 / 4 / 10 / 16 / 24 / 32 / 40 ; skillTier is PRIMARY.
  row geometry: Y = 465 - 62*tier ; rows t1..t7 -> Y {403,341,279,217,155,93,31};
  columns X {128,228,328,428,528,628}.
  connectors = record-driven skillConnectionOn/Off parallel arrays on the family
  BASE (largest Y), one tile per spanned row bottom->top (Bottom / Middle* / Top,
  a Connect tile where a side branch attaches).
  modifier<->base binding = SkillTree slot ORDER only; this module NEVER touches a
  SkillTree record, so every binding is preserved by construction.

WILL'S GREENLIGHT (2026-07-16, verbatim): "Proceed with fixing the masteries as
appropriate." Sensible defaults chosen; every judgment call is a WILL-VETO line in
docs/reports/b77_unlock_alignment_fix.md for his DEV pass.

THE FIX LIST (see the report for the two ladder diagrams + the E decision):

A. SPIRIT (m7) Distortion-Wave GT FIX-ROWS. The Spirit Distortion-Wave modifier
   BUTTONS reference the SHARED xpack\skills\dream records (verified: skill28 ->
   ...dream\drxdistortionwave_chaoticresonance, skill29 -> ...psionicimmolation), so
   their skillTier is co-owned by the correctly-drawn Dream (m9) twins and CANNOT be
   changed (FIX-GATE would break Dream). The only correct fix is FIX-ROW: move the
   Spirit buttons to the tier's row (== the Dream twin's row):
     Chaotic Resonance skill28  y217(row4) -> y279(row3)  (tier3)
     Psionic Immolation skill29 y93 (row6) -> y155(row5)  (tier5)
   Those rows are held by Death Chill Aura's modifiers Ravages of Time (col3 row3)
   and Necrosis (col3 row5) - both aligned, both Spirit-only, both bar-less. Vacate
   them into col4's free row3/row5 (x328->x428, Y unchanged, tier/gate unchanged):
     Ravages of Time skill07  col3->col4 (row3, tier3)
     Necrosis        skill08  col3->col4 (row5, tier5)
   Result: Spirit col3 Distortion-Wave ladder base r1 / ChaoticRes r3 / PsionicImm r5
   now byte-matches Dream, so the SHARED base bar (drxdistortionwave, len5 r1->r5)
   renders correctly in BOTH masteries (it was mis-drawn in Spirit before). No
   connector edit needed (base bar already Dream-correct; DCA mods carry no bar).
   WILL-VETO: DCA mods relocated col3->col4 (still bar-less standalone, as before) to
   free the GT Distortion-Wave ladder; alternative = a fuller Spirit reflow grouping
   Death Chill Aura with its col2 base.

B. FIX-GATE leans (skillTier -> the DRAWN row; req normalized <= tier threshold):
     m2 Defense drx_summonphalanx  skillTier 7->5  (row5, unlock 40->24)
     m4 Storm   drxfrostnova       skillTier 6->5  (row5, unlock 32->24)
     m4 Storm   drx_lightningdash  skillTier 5->7  (row7, unlock 24->40)
   (m3 Earth drx_firenova 6->7 is done inside item D - reconciled, applied once.)

C. WARFARE (m1) col3 mini-restack (the scrambled grafted family). col3 also holds
   the ALIGNED Battle Standard family (base row3 + petmods row5/row6 with a len4 bar
   spanning rows 3-6), which is KEPT untouched. The grafted family is seated in the
   col3 cells outside that bar corridor:
     ClubSlam      skill26  row7 -> row1 ; skillTier 2->1 (unlock 1); bar -> adjacent
                            len2 [Bottom,Top] up to its Fissure modifier (this also
                            REPAIRS ClubSlam's broken 6-tile off-grid upward bar).
     ClubSlam_fissure skill27 row4 -> row2 ; skillTier 7->2 (unlock 4); adjacent above.
     Ancestral (Lasting Legacy) skill28 row2 -> row7 ; skillTier 7 kept (ultimate top).
   Hamstring is grafted into col4 (drawn inside Onslaught's full-height bar); there is
   NO clean col3 cell for it (row4 sits inside the Battle Standard bar corridor), so it
   is aligned IN col4 by FIX-ROW to its real-tier row:
     Hamstring     skill25  col4 row3 -> col4 row4 ; skillTier 4 kept (unlock 16).
   WILL-VETO: hamstring aligned within col4 (its Onslaught column) rather than moved to
   col3; ClubSlam/Fissure FIX-GATE 2->1 / 7->2 to seat the pair adjacently at the clear
   bottom of col3 (a basic club attack + its modifier, low unlock, is coherent).

D. EARTH (m3) col4 in-place re-tier + bar repair. col4 is ALREADY a filled row1..row7
   ladder; only the skillTiers drift + two bars overshoot. No button moves:
     Soften Metal          skill10 row2 skillTier 3->2 (unlock 4)
     Rupture (Flame Surge) skill26 row3 skillTier 1->3 (unlock 10)  [b70: restored @r3
                                                                     intentionally]
     Rupture Burning       skill27 row4 skillTier 3->4 (unlock 16)
     Rupture Flare         skill28 row5 skillTier 5 kept (unlock 24) [already aligned]
     Spontaneous Combustion skill23 row6 skillTier 5->6 (unlock 32)
     Fire Nova             skill25 row7 skillTier 6->7 (unlock 40)   [== item B FireNova]
   Bar repair: RingOfFlame (row1) len3->len2 [Bottom,Top] (mod SoftenMetal now adjacent
   at row2); Rupture (row3) len5->len3 [Bottom,Middle,Top] spanning row3->row5 (its mods
   Burning row4 + Flare row5) - both removals delete an overshoot that crossed the rows
   above. WILL-VETO: SoftenMetal re-tiered 3->2 (its SV098 GT tier3/row3 is occupied by
   the intentionally-restored Rupture base per the b70 note); Rupture re-tiered 1->3 to
   match its intentional row3 seat.

E. STORM (m4) broken button. skill25 (col1 row3) points skillName at
   records\skills\storm\drxspellbreaker_spellshock2.dbr, which does NOT exist. The only
   existing variant drxspellbreaker_spellshock IS a real castable skill - but it is
   ALREADY live as "Inversion" (m4 skill14, col4 row6), so repointing skill25 to it
   would DUPLICATE that button. DECISION: RETIRE skill25 cleanly - remove it from every
   mastery-4 panectrl.tabSkillButtons copy (ingameui + xpack + xpack3) so the engine
   never renders it; the button record is left orphaned (parked). No black-hole button
   remains. WILL-VETO: retired (not repointed) because the sole existing variant is
   already the live Inversion button.

GOLDEN: masteries 1/2/3/4/7 are NOT A7-frozen (the golden covers only Occult m5 +
Hunting m6). This module touches ONLY m1/m2/m3/m4/m7, so the A7 golden gate stays green
by construction. The permanent gate tools/gate_unlock_alignment.py enforces
skillTier==drawn-row + req<=threshold on every live button (13 SV-faithful
REQ-EXCEEDS-ROW waivers).

Contract: patches-registry module - MODULE_NAME + apply(db, tags) + verify(db, tags).
"""

MODULE_NAME = ("b77 mastery UNLOCK-ALIGNMENT (Spirit DW GT-rows + Warfare col3 restack "
               "+ Earth col4 re-tier + Defense/Storm gate leans + Storm broken-button retire)")

# --- dtype ids (mirror arz_patcher.DATA_TYPE_*): 0 = INT, 2 = STRING, 3 = BOOL. -----
_DT_INT = 0
_DT_STR = 2
_DT_BOOL = 3

_UI = "records\\ingameui\\player skills\\mastery %d\\"          # masteries 1-8

_ROW_Y = {1: 403, 2: 341, 3: 279, 4: 217, 5: 155, 6: 93, 7: 31}   # Y = 465 - 62*tier
_Y_ROW = {v: k for k, v in _ROW_Y.items()}
_TIER_THRESHOLD = {1: 1, 2: 4, 3: 10, 4: 16, 5: 24, 6: 32, 7: 40}
_COL_X = {1: 128, 2: 228, 3: 328, 4: 428, 5: 528, 6: 628}

# canonical connector tiles (full path form - matches the arz's stored values). -------
_BARROOT = "InGameUI\\Icons\\Skills\\SkillBars\\"
def _bar(tiles, on):
    suf = "On01.tex" if on else "Off01.tex"
    return [_BARROOT + "SkillBar" + t + suf for t in tiles]
_STRAIGHT2 = (["Bottom", "Top"])                 # adjacent (1-tier) modifier bar
_STRAIGHT3 = (["Bottom", "Middle", "Top"])       # 2-tier straight bar


# ---------------------------------------------------------------------------
def _resolve(db, rec):
    if db.has_record(rec):
        return rec
    low = rec.lower().replace('/', '\\')
    for n in db.record_names():
        if n.lower().replace('/', '\\') == low:
            return n
    raise SystemExit("mastery_unlock_alignment: expected record missing: %s "
                     "(upstream structure changed?)" % rec)


def _first(v):
    return (v[0] if v else None) if isinstance(v, list) else v


def _btn_tail(db, rec):
    sn = _first(db.get_field_value(rec, "skillName"))
    return str(sn).replace('/', '\\').lower().rsplit('\\', 1)[-1] if sn else ""


def _list_of(db, rec, field):
    v = db.get_field_value(rec, field)
    if v is None:
        return None
    return v if isinstance(v, list) else [v]


# --- fix tables --------------------------------------------------------------------
# BUTTON MOVES: (mastery, button, expect_skill_tail, target_col, target_row, label)
_MOVES = [
    # A. Spirit Distortion-Wave GT rows (buttons reference shared dream records) + the
    #    Death Chill Aura modifiers relocated to col4 to free row3/row5.
    (7, "skill28", "drxdistortionwave_chaoticresonance.dbr", 3, 3, "Spirit Chaotic Resonance -> row3 (Dream twin)"),
    (7, "skill29", "drxdistortionwave_psionicimmolation.dbr", 3, 5, "Spirit Psionic Immolation -> row5 (Dream twin)"),
    (7, "skill07", "drxdeathchillaura_ravagesoftime.dbr", 4, 3, "Spirit Ravages of Time col3->col4 row3"),
    (7, "skill08", "drxdeathchillaura_necrosis.dbr", 4, 5, "Spirit Necrosis col3->col4 row5"),
    # C. Warfare col3 grafted-family restack + hamstring aligned in col4.
    (1, "skill26", "drx_clubslam.dbr", 3, 1, "Warfare Club Slam -> col3 row1"),
    (1, "skill27", "drx_clubslam_fissure.dbr", 3, 2, "Warfare Slam Fissure -> col3 row2"),
    (1, "skill28", "drx_ancestralmod.dbr", 3, 7, "Warfare Lasting Legacy -> col3 row7"),
    (1, "skill25", "drxhamstring.dbr", 4, 4, "Warfare Hamstring col4 row3->row4"),
]

# SKILL TIER/REQ WRITES: (skill_record, new_tier, new_req_or_None, label)
#   new_req_or_None = normalize skillMasteryLevelRequired (<= threshold); None = leave.
_TIER_WRITES = [
    # C. Warfare
    ("records\\skills\\warfare\\drx_clubslam.dbr", 1, None, "Club Slam tier 2->1"),
    ("records\\skills\\warfare\\drx_clubslam_fissure.dbr", 2, None, "Slam Fissure tier 7->2"),
    ("records\\skills\\warfare\\drx_ancestralmod.dbr", 7, None, "Lasting Legacy tier 7 (kept)"),
    ("records\\skills\\warfare\\drxhamstring.dbr", 4, None, "Hamstring tier 4 (kept)"),
    # B. Defense / Storm gate leans
    ("records\\skills\\defensive\\drx_summonphalanx.dbr", 5, None, "Summon Phalanx tier 7->5"),
    ("records\\skills\\storm\\drxfrostnova.dbr", 5, None, "Frost Nova tier 6->5"),
    ("records\\skills\\storm\\drx_lightningdash.dbr", 7, None, "Lightning Dash tier 5->7"),
    # D. Earth col4 in-place re-tier
    ("records\\skills\\earth\\drxringofflame_softenmetal.dbr", 2, None, "Soften Metal tier 3->2"),
    ("records\\skills\\earth\\drxrupture.dbr", 3, None, "Rupture tier 1->3"),
    ("records\\skills\\earth\\drxrupture_burning.dbr", 4, None, "Rupture Burning tier 3->4"),
    ("records\\skills\\earth\\drxspontaneouscombustion.dbr", 6, None, "Spontaneous Combustion tier 5->6"),
    ("records\\skills\\earth\\drx_firenova.dbr", 7, None, "Fire Nova tier 6->7"),
]

# CONNECTOR REWRITES: (base_skill_record, tiles, label)
_BAR_WRITES = [
    ("records\\skills\\warfare\\drx_clubslam.dbr", _STRAIGHT2, "Club Slam bar -> adjacent len2 (to Fissure)"),
    ("records\\skills\\earth\\drxringofflame.dbr", _STRAIGHT2, "Ring of Flame bar -> adjacent len2 (to Soften Metal)"),
    ("records\\skills\\earth\\drxrupture.dbr", _STRAIGHT3, "Rupture bar -> straight len3 row3->row5"),
]

# E. Storm broken button to retire from every panectrl copy.
_RETIRE_BTN = "skill25"
_RETIRE_PANECTRLS = [
    "records\\ingameui\\player skills\\mastery 4\\panectrl.dbr",
    "records\\xpack\\ui\\skills\\mastery 4\\panectrl.dbr",
    "records\\xpack3\\ui\\skills\\mastery 4\\panectrl.dbr",
]
_RETIRE_MISSING_SKILL = "drxspellbreaker_spellshock2.dbr"


def _set_button_pos(db, mastery, button, expect_tail, col, row, label):
    rec = _resolve(db, (_UI % mastery) + button + ".dbr")
    got = _btn_tail(db, rec)
    if got != expect_tail.lower():
        raise SystemExit("mastery_unlock_alignment[move]: m%d %s targets %r, expected %r "
                         "(%s) - button roster reshuffled upstream"
                         % (mastery, button, got, expect_tail, label))
    db.set_field(rec, "bitmapPositionX", _COL_X[col], _DT_INT)
    db.set_field(rec, "bitmapPositionY", _ROW_Y[row], _DT_INT)
    return rec


def _set_tier(db, skill, tier, req, label):
    rec = _resolve(db, skill)
    if db.get_field_value(rec, "skillTier") is None:
        raise SystemExit("mastery_unlock_alignment[tier]: %s has no skillTier field (%s)"
                         % (rec, label))
    db.set_field(rec, "skillTier", tier, _DT_INT)
    if req is not None:
        db.set_field(rec, "skillMasteryLevelRequired", req, _DT_INT)
    else:
        # normalize: if an existing req exceeds the new tier threshold, clamp it down so
        # the effective gate == the tier threshold (no silent over-gate on a fixed row).
        cur = _first(db.get_field_value(rec, "skillMasteryLevelRequired"))
        try:
            curn = int(cur) if cur is not None else 0
        except (TypeError, ValueError):
            curn = 0
        if curn > _TIER_THRESHOLD[tier]:
            db.set_field(rec, "skillMasteryLevelRequired", _TIER_THRESHOLD[tier], _DT_INT)
    return rec


def _set_bar(db, skill, tiles, label):
    rec = _resolve(db, skill)
    db.set_field(rec, "skillConnectionOn", _bar(tiles, True), _DT_STR)
    db.set_field(rec, "skillConnectionOff", _bar(tiles, False), _DT_STR)
    return rec


def _retire_button(db):
    """E: remove skill25 from every mastery-4 panectrl.tabSkillButtons list (idempotent)."""
    tail = ("\\mastery 4\\" + _RETIRE_BTN + ".dbr").lower()
    n_removed = 0
    for pc in _RETIRE_PANECTRLS:
        rec = None
        if db.has_record(pc):
            rec = pc
        else:
            low = pc.lower()
            for n in db.record_names():
                if n.lower() == low:
                    rec = n
                    break
        if rec is None:
            continue
        lst = _list_of(db, rec, "tabSkillButtons") or []
        kept = [e for e in lst if not str(e).lower().replace('/', '\\').endswith(tail)]
        if len(kept) != len(lst):
            db.set_field(rec, "tabSkillButtons", kept, _DT_STR)
            n_removed += (len(lst) - len(kept))
    return n_removed


def apply(db, tags):
    """Apply items A-E. `tags` unused (all fixes are DB record fields; no Text tags)."""
    print("\n=== mastery_unlock_alignment (b77): unlock-alignment fix wave ===")

    # A + C: button position moves (row/col). Guarded on skillName identity.
    for mastery, button, tail, col, row, label in _MOVES:
        _set_button_pos(db, mastery, button, tail, col, row, label)
        print("  [move] %s -> c%d r%d (y%d)" % (label, col, row, _ROW_Y[row]))

    # B + C + D: skill tier/req writes (the unlock gate).
    for skill, tier, req, label in _TIER_WRITES:
        _set_tier(db, skill, tier, req, label)
        print("  [tier] %s (unlock %d)" % (label, _TIER_THRESHOLD[tier]))

    # C + D: connector rewrites (repair overshoot / seat adjacent modifier bars).
    for skill, tiles, label in _BAR_WRITES:
        _set_bar(db, skill, tiles, label)
        print("  [bar]  %s" % label)

    # E: retire the Storm broken button.
    n = _retire_button(db)
    print("  [E] Storm skill25 (dangling %s) removed from %d panectrl slot(s)"
          % (_RETIRE_MISSING_SKILL, n))

    print("=== mastery_unlock_alignment done: A(Spirit DW rows) B(gate leans) "
          "C(Warfare col3) D(Earth col4) E(Storm retire) ===")


# ---------------------------------------------------------------------------
def verify(db, tags):
    """Post-finalization guard (runs on the fully-assembled db): re-assert EVERY fix.
    Make-or-break negative surface - a planted wrong tier/row/bar fails right here."""
    print("\n=== mastery_unlock_alignment.verify: re-assert every b77 fix ===")
    bad = []

    # A + C: button positions.
    for mastery, button, tail, col, row, label in _MOVES:
        rec = _resolve(db, (_UI % mastery) + button + ".dbr")
        got = _btn_tail(db, rec)
        if got != tail.lower():
            bad.append("[move] %s targets %r want %s" % (rec, got, tail))
            continue
        gx = _first(db.get_field_value(rec, "bitmapPositionX"))
        gy = _first(db.get_field_value(rec, "bitmapPositionY"))
        if str(gx) != str(_COL_X[col]):
            bad.append("[move] %s x=%s want %s (%s)" % (rec, gx, _COL_X[col], label))
        if str(gy) != str(_ROW_Y[row]):
            bad.append("[move] %s y=%s want %s r%d (%s)" % (rec, gy, _ROW_Y[row], row, label))

    # B + C + D: tiers == intended, and effective gate == the tier threshold.
    for skill, tier, req, label in _TIER_WRITES:
        rec = _resolve(db, skill)
        st = _first(db.get_field_value(rec, "skillTier"))
        if str(st) != str(tier):
            bad.append("[tier] %s skillTier=%s want %d" % (label, st, tier))
        rq = _first(db.get_field_value(rec, "skillMasteryLevelRequired"))
        try:
            rqn = int(rq) if rq is not None else 0
        except (TypeError, ValueError):
            rqn = 0
        if max(_TIER_THRESHOLD[tier], rqn) != _TIER_THRESHOLD[tier]:
            bad.append("[tier] %s effective gate=%d want %d (req=%s over-gates)"
                       % (label, max(_TIER_THRESHOLD[tier], rqn), _TIER_THRESHOLD[tier], rq))

    # cross-check: for every moved button whose skill carries a skillTier, tier == row.
    for mastery, button, tail, col, row, label in _MOVES:
        rec = _resolve(db, (_UI % mastery) + button + ".dbr")
        sn = _first(db.get_field_value(rec, "skillName"))
        if not sn:
            continue
        sk = _resolve(db, str(sn))
        st = _first(db.get_field_value(sk, "skillTier"))
        if st is not None and str(st) != str(row):
            bad.append("[align] %s drawn row%d but skillTier=%s (%s)"
                       % (rec, row, st, label))

    # C + D: connector bars.
    for skill, tiles, label in _BAR_WRITES:
        rec = _resolve(db, skill)
        on = _list_of(db, rec, "skillConnectionOn")
        if on != _bar(tiles, True):
            bad.append("[bar] %s skillConnectionOn=%s want %s"
                       % (label, on, _bar(tiles, True)))
        off = _list_of(db, rec, "skillConnectionOff")
        if off != _bar(tiles, False):
            bad.append("[bar] %s skillConnectionOff mismatch" % label)

    # E: skill25 gone from every mastery-4 panectrl; the record it pointed at is still
    #    absent (we did not conjure it). Also assert Inversion (the real variant) survives.
    tail = ("\\mastery 4\\" + _RETIRE_BTN + ".dbr").lower()
    for pc in _RETIRE_PANECTRLS:
        rec = None
        low = pc.lower()
        for n in db.record_names():
            if n.lower() == low:
                rec = n
                break
        if rec is None:
            continue
        lst = _list_of(db, rec, "tabSkillButtons") or []
        if any(str(e).lower().replace('/', '\\').endswith(tail) for e in lst):
            bad.append("[E] %s still lists the retired skill25 button" % rec)
    # the dangling target must remain non-existent (no accidental creation)
    if db.has_record("records\\skills\\storm\\" + _RETIRE_MISSING_SKILL):
        bad.append("[E] %s unexpectedly now EXISTS (was supposed to stay retired)"
                   % _RETIRE_MISSING_SKILL)
    # Inversion (the real spellshock variant) must still be a live button somewhere
    if not db.has_record("records\\skills\\storm\\drxspellbreaker_spellshock.dbr"):
        bad.append("[E] real Inversion skill drxspellbreaker_spellshock.dbr missing")

    if bad:
        for b in bad:
            print("  FAIL:", b)
        raise SystemExit("mastery_unlock_alignment.verify: %d defect(s) survived "
                         "finalization" % len(bad))
    print("  OK: A(Spirit DW rows + DCA relocate) B(3 gate leans) C(Warfare col3 restack "
          "+ hamstring) D(Earth col4 re-tier + 2 bar repairs) E(Storm skill25 retired)")
