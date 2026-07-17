r"""mastery_sv_alignment - BUILD45 MASTERY SV-ALIGNMENT (b70 wave).

Fixes the residual Occult/Hunting/Earth mastery-tree defects Will enumerated from
his build43 screenshot PLUS everything the two machine-verified ground-truth
extractions prove wrong vs Soulvizier. This module is the LAST WRITER on every
field it touches (registered in REGISTRY after hunting_occult_ui, mastery_ui_audit,
mastery_bg_render, oh_pane_art), and its verify() re-asserts every fix on the
FINAL assembled arz.

AUTHORITY (read-only, both committed):
  tools/sv_mastery_ground_truth.json        (SV 0.98i, 51,186 records)
  tools/sv_pre098i_occult_ground_truth.json (SV 0.41 == 0.9, the Occult 4-skill lineage)
  docs/reports/sv_mastery_ground_truth.md    (incl. section 8 pre-098i correction)
MECHANISMS (proven there): shape = boolean isCircular on the ingameui skillNN.dbr
button (1=circle=augment/passive/proc, 0=square=actively-cast); connectors = 100%
record-driven skillConnectionOn/Off parallel string arrays (equal length; the bar
sits on the family BASE = largest Y and draws UPWARD; SkillBarBottom/Middle/Connect/Top
tiles; a `_right` variant rises up-and-right); row geometry Y=465-62*tier
(t1..t7 Y={403,341,279,217,155,93,31}), cols {128,228,328,428,528,628}; emblem:
masterybitmap.dbr must be BitmapUIAware (plural bitmapNames) or the pane's black
circular hole shows through as a black disc.

THE FIX LIST (each cites its authority; see docs/reports/b70_mastery_sv_alignment.md):

A. SHAPES (isCircular on the button record). These 4 also fixed UPSTREAM in
   hunting_occult_ui.py (BL-103 fix-upstream: Will's 2026-07-16 rulings supersede
   his 2026-07-12 shape law for these skills); this module RE-ASSERTS them as the
   ratified last writer and verify() proves the FINAL values:
     1. Poisonous Gas  (m5 skill13, drxpoisongasbomb)            -> CIRCLE (isCircular=1). SV098 GT anchor 4 + Will.
     2. Blade Fury     (m5 skill06, drxcalculatedstrike_luckyhit)-> SQUARE (isCircular=0). SV098 GT anchor 8 + Will.
     3. Smoke Screen   (m5 skill18, drxlaytrap_petmodifier_multishotbolttrap) -> SQUARE. SV098 GT (c1t3 square standalone).
     4. Eviscerate     (m6 skill18, drxtakedown_eviscerate)      -> SQUARE. WILL RULING 2026-07-16 verbatim.
   NB: the golden baseline FROZE the SV-correct shapes (PoisonGas circle, the other
   three square); hunting_occult_ui's 2026-07-12 law DRIFTED them (waived). Reverting
   to the golden value means these produce ZERO net golden drift.

B. EMBLEM CIRCLE x9 (the black disc top-right of every skill window): convert each
   mastery's masterybitmap.dbr BitmapSingle -> BitmapUIAware (bitmapNames=[tex,tex],
   bitmapPositionsX=[718,748], bitmapPositionsY=[31,31], drop the singular
   bitmapName/bitmapPositionX/Y). Mirrors the proven b60 pane conversion applied to
   the emblem slot it missed. SV098 GT emblem RCA (section 4). All 9 textures resolve.

C. OCCULT COLUMN-6 RESTACK (m5). Darklings + Dark Aperture were moved into column 6
   by the build45 wave (item C round 1), which already held Throwing Knife (t4) and
   Flurry (t6); that layout INTERLEAVED (Darklings' t3->t5 bar crossed Throwing
   Knife@t4; Throwing Knife's t4->t6 bar crossed Dark Aperture@t5).
   WILL RULING 2026-07-16 (verbatim): "lets have darklings be in the same lane as
   throwing knife, but we will have darklings unlock at 10, dark aperture unlock at
   16, and then above it we will have throwing knife at 24 and the augment to throwing
   knife at 32 so we wont have lines behind one another."
   FIX (C2 = this round): restack column 6 (X=628) as a clean bottom-to-top ladder -
     Darklings   t3 (y279, unlock 10) - STAYS
     Dark Aperture t4 (y217, unlock 16) - moves DOWN from t5 (y155)
     Throwing Knife t5 (y155, unlock 24) - moves UP  from t4 (y217)
     Flurry      t6 (y93,  unlock 32) - STAYS
   The two augment bars are now ADJACENT (1-tier), drawn as the vanilla Shadow-Stalker
   len2 [Bottom,Top] straight: Darklings->Dark Aperture spans t3->t4; Throwing Knife->
   Flurry spans t5->t6. ZERO crossings. Dark Aperture's stray inherited `_right` bar
   stays CLEARED (build45). GAMEPLAY (Will explicit): each moved skill's skillTier is
   set to its new row (Dark Aperture 5->4, Throwing Knife 4->5) AND its
   skillMasteryLevelRequired (the actual unlock gate) is set == the row threshold
   (Dark Aperture 24->16, Throwing Knife 5->24) so the real unlock matches Will's
   stated number under EVERY engine gate-semantics (see below). Darklings (tier 3,
   gate 10) + Flurry (tier 6, gate 32) already correct - verified, not written.
   TIER LAW (proven: skillTier == button row across all 27 col skills + 142 vanilla
   buttons): threshold ladder = tier {1:1,2:4,3:10,4:16,5:24,6:32,7:40}.
   GATE MECHANISM: skillTier is the effective unlock gate; skillMasteryLevelRequired
   is at most a max()-gate (proven: vanilla modifiers rainoffire_brimstone tier6/req15,
   dream_slowtime tier7/req16, nature_wildhunt tier7/req1 all sit FAR below their base
   tier - req cannot be the sole gate or a modifier would precede its base). Setting
   both fields == the target threshold makes the unlock unambiguous under skillTier-,
   max()-, or req-semantics alike. MECHANISM LAW: the SkillTree slot ORDER (the ONLY
   modifier<->base binding surface) is UNTOUCHED - Dark Aperture@27 still binds to
   Darklings@26, Flurry@10 still binds to Throwing Knife@9 (verify() proves both).

D. DARK INVIGORATION = TRUE MODIFIER OF SHADOW LINK (m5). WILL RULING 2026-07-16
   verbatim: "so how does dark invigoration work? I think it should augment shadow link."
   MECHANISM (proven from vanilla TQAE, see report item D + docstring below): the engine
   binds a Skill_Modifier to its base skill PURELY by the mastery SkillTree's numeric
   skillName{N} ORDERING - a modifier attaches to the nearest LOWER-indexed non-modifier
   skill. There is NO back-reference on the modifier record, the base record, or the UI
   button (proven: vanilla Heart of Frost / Static Charge carry zero reference to Storm
   Nimbus; the ONLY linking datum is StormSkillTree slot order Nimbus@8 -> HeartofFrost@9
   -> StaticCharge@10). CURRENT-BINDING FINDING: the LIVE occult tree
   (records\skills\stealth\drxstealthskilltree.dbr, referenced by malepc01/femalepc01
   skillTree5 = mastery 5) ALREADY orders drxbladehoning@6 (Shadow Link, Skill_BuffRadius-
   Toggled - a valid modifier base, exactly like vanilla BattleAwareness) -> drxopenwound@7
   (Dark Invigoration, Skill_Modifier) -> drxanatomy@8 (Shadow Lore, Skill_Modifier). So
   Dark Invigoration ALREADY binds to (augments) Shadow Link - its offensiveLifeMin flat
   vitality damage + bleeding fold into the character while Shadow Link's toggled aura is
   up, the SAME way Heart of Frost's cold modifier folds into Storm Nimbus. The build45
   "no gameplay relation exists" line was a VET ERROR: it checked record cross-references
   (skillDependancy/buffSkillName), which is NOT TQ's modifier-binding surface. This module
   now (a) ASSERTS that tree-order binding fail-loud in apply() (module = ratified guarantor;
   idempotent - the arz already satisfies it), and (b) re-asserts it at MECHANISM level in
   verify(). The build45 UI wire (Shadow Link straight bar UP through c3t3 to Dark
   Invigoration at c3t4, plus the c3-column stack Shadow Link t2 square base / Dark Invig
   t4 circle / Shadow Lore t6 circle) is KEPT unchanged - it now correctly DEPICTS a real
   augment, exactly mirroring the vanilla Storm Nimbus column (base square + modifier
   circles stacked, connected by a bar). Zero arz field change vs build45 (the augment was
   already present); no new golden override needed (mirroring Heart of Frost requires ONLY
   tree-order + UI - adding any record field would DEVIATE from the vanilla shape).

E. EARTH Soften Metal (m3): NO-OP. The task brief's literal target (c4t2) already
   holds in build44 (drxringofflame_softenmetal @ x428 y341 = c4t2). SV098's authoritative
   slot is c4 t3 (y279), but build44's c4t3 is occupied by build41's INTENTIONAL
   restored Flame Surge line (drxrupture, a build41-new addition - pre-098i GT
   broader_sweep m3), so the SV move is blocked by restored content and Soften Metal's
   c4t2 rest position is a necessary consequence, not a bug. Documented; not touched.

F. VERIFY-ONLY chains (no change; verify() re-asserts): Toxic Concoction (drx_scrap
   c1t4) straight len4 bar up through Poisonous Gas to Aphotic Ichor; Shadow Stalker
   (drx_summon_shadow_stalker c4t6) straight len2 bar to Channel. Both byte-correct in
   build44 per pre-098i GT.

G. ROSTER-WIDE audit: report-only. Per SV098 GT section 7b the ONLY shape/move
   deviations vs SV are items A-E; every other build44-vs-SV098 difference is an
   intentional build41 legacy-skill restoration (additions are NOT deviations). No
   further unambiguous non-golden GT mismatch found; ambiguous items are WILL-CONFIRM
   in the report, not changed.

GOLDEN: Occult (m5) + Hunting (m6) are A7-frozen (tools/occult_hunting_golden.json).
Every m5/m6 field this module drifts from the golden is sanctioned by an
owner_approved_overrides entry citing 'Will ruling 2026-07-16' or the ground-truth
file+key. Earth (m3) is not golden and needs no waiver (and this wave does not touch it).

Contract: patches-registry module - MODULE_NAME + apply(db, tags) + verify(db, tags).
"""

MODULE_NAME = ("BUILD45 mastery SV-alignment (Occult/Hunting shapes + emblem x9 + "
               "col6 restack [Darklings/DarkAp/ThrowKnife/Flurry, adjacent bars] + "
               "Dark Invigoration TRUE-augments Shadow Link)")

# ---------------------------------------------------------------------------
# dtype ids (mirror arz_patcher.DATA_TYPE_*): 0 = INT, 2 = STRING, 3 = BOOL.
_DT_INT = 0
_DT_STR = 2
_DT_BOOL = 3

_UI = "records\\ingameui\\player skills\\mastery %d\\"          # masteries 1-8
_DREAM = "records\\xpack\\ui\\skills\\mastery 9\\"              # Dream / mastery 9
_UIAWARE_TPL = r"database\Templates\InGameUI\BitmapUIAware.tpl"

# --- A. shape presets (isCircular + the 3 border bitmaps kept consistent). ----
_SQUARE = (
    ("isCircular", 0, _DT_BOOL),
    ("bitmapNameUp", r"InGameUI\SkillButtonBorder01.tex", _DT_STR),
    ("bitmapNameDown", r"InGameUI\SkillButtonBorderDown01.tex", _DT_STR),
    ("bitmapNameInFocus", r"InGameUI\SkillButtonBorderOver01.tex", _DT_STR),
)
_CIRCLE = (
    ("isCircular", 1, _DT_BOOL),
    ("bitmapNameUp", r"InGameUI\SkillButtonBorderRound01.tex", _DT_STR),
    ("bitmapNameDown", r"InGameUI\SkillButtonBorderRoundDown01.tex", _DT_STR),
    ("bitmapNameInFocus", r"InGameUI\SkillButtonBorderRoundOver01.tex", _DT_STR),
)

# (slot, button, preset, expected skill record tail, human label). Fail-loud if the
# button's skillName no longer targets the expected skill (upstream reshuffle guard).
_SHAPE_FIXES = (
    (5, "skill13", _CIRCLE, "drxpoisongasbomb.dbr", "Poisonous Gas"),
    (5, "skill06", _SQUARE, "drxcalculatedstrike_luckyhit.dbr", "Blade Fury"),
    (5, "skill18", _SQUARE, "drxlaytrap_petmodifier_multishotbolttrap.dbr", "Smoke Screen"),
    (6, "skill18", _SQUARE, "drxtakedown_eviscerate.dbr", "Eviscerate"),
)

# --- B. emblem masterybitmap.dbr per mastery (all 9). --------------------------
_EMBLEM_DIRS = [(_UI % n, "m%d" % n) for n in range(1, 9)] + [(_DREAM, "m9")]
_EMBLEM_POS_X = [718, 748]
_EMBLEM_POS_Y = [31, 31]

# --- C2. Occult column-6 restack (Will ruling 2026-07-16). ---------------------
_DARK_COL_X = 628          # column 6 (the shared Darklings/Throwing-Knife lane)
_ROW_Y = {1: 403, 2: 341, 3: 279, 4: 217, 5: 155, 6: 93, 7: 31}   # Y = 465 - 62*tier
_TIER_THRESHOLD = {1: 1, 2: 4, 3: 10, 4: 16, 5: 24, 6: 32, 7: 40}  # mastery pts / tier

_DARKLINGS_BTN = "skill25"          # drxdarklings              (base,   t3 y279)
_DARKAP_BTN = "skill26"             # drxdarklings_darkaperture (augment, t4 y217 NEW)
_THROWKNIFE_BTN = "skill10"         # drxthrowingknife          (base,   t5 y155 NEW)
_FLURRY_BTN = "skill11"             # drxthrowingknife_flurryofknives (augment, t6 y93)
_DARKLINGS_SKILL = "records\\skills\\stealth\\drxdarklings.dbr"
_DARKAP_SKILL = "records\\skills\\stealth\\drxdarklings_darkaperture.dbr"
_THROWKNIFE_SKILL = "records\\skills\\stealth\\drxthrowingknife.dbr"
_FLURRY_SKILL = "records\\skills\\stealth\\drxthrowingknife_flurryofknives.dbr"

# Final col-6 ladder: (button, skill path, expected skillName tail, tier, label).
_COL6_STACK = (
    (_DARKLINGS_BTN, _DARKLINGS_SKILL, "drxdarklings.dbr", 3, "Darklings"),
    (_DARKAP_BTN, _DARKAP_SKILL, "drxdarklings_darkaperture.dbr", 4, "Dark Aperture"),
    (_THROWKNIFE_BTN, _THROWKNIFE_SKILL, "drxthrowingknife.dbr", 5, "Throwing Knife"),
    (_FLURRY_BTN, _FLURRY_SKILL, "drxthrowingknife_flurryofknives.dbr", 6, "Flurry"),
)
# The two skills that MOVE get an explicit gate write (== new-tier threshold) so the
# real unlock matches Will's number regardless of engine gate-semantics (skillMastery
# LevelRequired keyed by skill tail -> target threshold).
_GATE_WRITE = {
    "drxdarklings_darkaperture.dbr": (4, 16),   # tier 4, unlock 16
    "drxthrowingknife.dbr": (5, 24),            # tier 5, unlock 24
}
# The augment base that OWNS each adjacent straight bar (base is the larger-Y row).
_BAR_OWNERS = (_DARKLINGS_SKILL, _THROWKNIFE_SKILL)
# Modifier -> base bindings that MUST survive the restack (SkillTree tree-order).
_BIND_PAIRS = (
    ("drxdarklings_darkaperture.dbr", "drxdarklings.dbr", "Dark Aperture", "Darklings"),
    ("drxthrowingknife_flurryofknives.dbr", "drxthrowingknife.dbr", "Flurry", "Throwing Knife"),
)

# canonical straight 3-tile bar (Bottom/Middle/Top) - the 2-tier span bar; retained
# for the item-D Shadow Link wire (c3 t2->t4).
_STRAIGHT_ON = [
    r"InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex",
    r"InGameUI\Icons\Skills\SkillBars\SkillBarMiddleOn01.tex",
    r"InGameUI\Icons\Skills\SkillBars\SkillBarTopOn01.tex",
]
_STRAIGHT_OFF = [
    r"InGameUI\Icons\Skills\SkillBars\SkillBarBottomOff01.tex",
    r"InGameUI\Icons\Skills\SkillBars\SkillBarMiddleOff01.tex",
    r"InGameUI\Icons\Skills\SkillBars\SkillBarTopOff01.tex",
]
# adjacent 1-tier straight bar (Bottom/Top, no Middle) - the col-6 augment bars.
# Byte-identical to the vanilla Shadow-Stalker->Channel len2 bar (probed live).
_STRAIGHT2_ON = [
    r"InGameUI\Icons\Skills\SkillBars\SkillBarBottomOn01.tex",
    r"InGameUI\Icons\Skills\SkillBars\SkillBarTopOn01.tex",
]
_STRAIGHT2_OFF = [
    r"InGameUI\Icons\Skills\SkillBars\SkillBarBottomOff01.tex",
    r"InGameUI\Icons\Skills\SkillBars\SkillBarTopOff01.tex",
]

# --- D. Shadow Link -> Dark Invigoration wire + TRUE modifier binding. ----------
_SHADOWLINK_SKILL = "records\\skills\\stealth\\drxbladehoning.dbr"
_DARKINVIG_SKILL = "records\\skills\\stealth\\drxopenwound.dbr"
# The LIVE occult (mastery 5) SkillTree - referenced by both PCs' skillTree5 field
# (records\xpack\creatures\pc\{male,female}pc01.dbr). This is the record whose numeric
# skillName{N} ORDER is the engine's modifier<->base binding surface. NB: a doubled-
# namespace TWIN exists at records\skills\skills\stealth\drxstealthskilltree.dbr but is
# referenced by NO PC/record (dead orphan) - editing it would be inert, so we assert on
# the LIVE tree only and merely NOTE the twin (no live/dead split: gameplay reads the LIVE
# one, and its @6->@7 order already binds Dark Invigoration to Shadow Link).
_OCCULT_SKILLTREE = "records\\skills\\stealth\\drxstealthskilltree.dbr"
_OCCULT_SKILLTREE_TWIN = "records\\skills\\skills\\stealth\\drxstealthskilltree.dbr"
_DARKINVIG_TAIL = "drxopenwound.dbr"
_SHADOWLINK_TAIL = "drxbladehoning.dbr"

# --- F. verify-only chains. ----------------------------------------------------
_TC_SKILL = "records\\skills\\stealth\\drx_scrap.dbr"                    # Toxic Concoction
_STALKER_SKILL = "records\\skills\\stealth\\drx_summon_shadow_stalker.dbr"  # Shadow Stalker


# ---------------------------------------------------------------------------
def _resolve(db, rec):
    """Case-insensitive record lookup; fail-loud if absent."""
    if db.has_record(rec):
        return rec
    low = rec.lower().replace('/', '\\')
    for n in db.record_names():
        if n.lower().replace('/', '\\') == low:
            return n
    raise SystemExit("mastery_sv_alignment: expected record missing: %s "
                     "(upstream structure changed?)" % rec)


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _drop_field(fields, name):
    for k in [k for k in fields if k.split('###')[0] == name]:
        del fields[k]


def _skillname_tail(db, rec):
    sn = _first(db.get_field_value(rec, "skillName"))
    return str(sn).replace('/', '\\').lower().rsplit('\\', 1)[-1] if sn else ""


def _class_of(db, rec):
    """Case-insensitive Class lookup for a skill record path; '' if unresolved."""
    low = str(rec).lower().replace('/', '\\')
    if db.has_record(rec):
        c = _first(db.get_field_value(rec, "Class"))
        return str(c) if c is not None else ""
    for n in db.record_names():
        if n.lower().replace('/', '\\') == low:
            c = _first(db.get_field_value(n, "Class"))
            return str(c) if c is not None else ""
    return ""


def _skilltree_pairs(db, tree_rec):
    """[(idx, skillName_value_str)] for the SkillTree, sorted by numeric skillName index.
    The engine reads these in numeric order; the arz stores them lexically."""
    rec = _resolve(db, tree_rec)
    fields = db.get_fields(rec)
    pairs = []
    for k in fields:
        base = k.split('###')[0]
        if base.lower().startswith("skillname") and base[9:].isdigit():
            sn = _first(db.get_field_value(rec, base))
            if sn and str(sn).strip():
                pairs.append((int(base[9:]), str(sn)))
    pairs.sort(key=lambda p: p[0])
    return pairs


def _modifier_binding_base(db, tree_rec, target_tail):
    """TQ modifier<->base binding = SkillTree numeric ORDER: a Skill_Modifier attaches to
    the nearest LOWER-indexed NON-modifier skill. Return the basename (lowercased) of the
    base that the modifier `target_tail` binds to in `tree_rec`, or None if target absent /
    no preceding base. This is the *mechanism-level* binding, not a field cross-reference."""
    last_base = None
    tgt = target_tail.lower()
    for _idx, sn in _skilltree_pairs(db, tree_rec):
        tail = sn.replace('/', '\\').lower().rsplit('\\', 1)[-1]
        if tail == tgt:
            return last_base
        if _class_of(db, sn) != "Skill_Modifier":
            last_base = tail
    return None


def _set_shape(db, slot, button, preset, expect_tail, label):
    rec = _resolve(db, (_UI % slot) + button + ".dbr")
    got = _skillname_tail(db, rec)
    if got != expect_tail.lower():
        raise SystemExit(
            "mastery_sv_alignment[A]: m%d %s skillName is %r, expected %r (%s) - "
            "button roster reshuffled upstream" % (slot, button, got, expect_tail, label))
    for field, val, dt in preset:
        if db.get_field_value(rec, field) is None:
            raise SystemExit("mastery_sv_alignment[A]: %s lacks field %s" % (rec, field))
        db.set_field(rec, field, val, dt)
    return rec


def _convert_emblem(db, dir_prefix):
    rec = _resolve(db, dir_prefix + "masterybitmap.dbr")
    cur = _first(db.get_field_value(rec, "bitmapName"))
    if cur and str(cur).strip():
        tex = str(cur).strip()
    else:
        # already converted (idempotent) - reuse bitmapNames[0]
        tex = _first(db.get_field_value(rec, "bitmapNames"))
        if not tex or not str(tex).strip():
            raise SystemExit("mastery_sv_alignment[B]: %s has no bitmapName/"
                             "bitmapNames to migrate" % rec)
        tex = str(tex).strip()
    db.set_field(rec, "templateName", _UIAWARE_TPL, _DT_STR)
    db.set_field(rec, "FileDescription", "BitmapUIAware", _DT_STR)
    db.set_field(rec, "bitmapNames", [tex, tex], _DT_STR)
    db.set_field(rec, "bitmapPositionsX", list(_EMBLEM_POS_X), _DT_INT)
    db.set_field(rec, "bitmapPositionsY", list(_EMBLEM_POS_Y), _DT_INT)
    fields = db.get_fields(rec)
    for f in ("bitmapName", "bitmapPositionX", "bitmapPositionY"):
        _drop_field(fields, f)
    return rec, tex


def apply(db, tags):
    """Apply items A-D (E/F/G are no-op/verify-only/report-only). `tags` unused
    (all fixes are UI record fields; no Text tags)."""
    print("\n=== mastery_sv_alignment (b70): Occult/Hunting/emblem SV alignment ===")

    # ---- A. shapes (last-writer re-assert) ----
    for slot, button, preset, tail, label in _SHAPE_FIXES:
        rec = _set_shape(db, slot, button, preset, tail, label)
        shape = "CIRCLE" if preset is _CIRCLE else "SQUARE"
        print("  [A] m%d %-8s %-16s -> %s" % (slot, button, label, shape))

    # ---- B. emblem x9: BitmapSingle -> BitmapUIAware ----
    for dir_prefix, lbl in _EMBLEM_DIRS:
        rec, tex = _convert_emblem(db, dir_prefix)
        print("  [B] %s masterybitmap -> BitmapUIAware [%s x2 @718/748,31]"
              % (lbl, tex.rsplit('\\', 1)[-1]))

    # ---- C2. Occult column-6 restack (Will ruling 2026-07-16) ----
    # Bottom-to-top ladder: Darklings t3 / Dark Aperture t4 / Throwing Knife t5 /
    # Flurry t6, all X=628. Buttons carry the row (bitmapPositionY); skill records
    # carry the tier + gate. SkillTree slot order UNTOUCHED (binding preserved).
    for btn_const, skill_path, expect_tail, tier, label in _COL6_STACK:
        btn = _resolve(db, (_UI % 5) + btn_const + ".dbr")
        got = _skillname_tail(db, btn)
        if got != expect_tail:
            raise SystemExit("mastery_sv_alignment[C]: m5 %s targets %r, expected %s "
                             "(%s) - button roster reshuffled upstream"
                             % (btn_const, got, expect_tail, label))
        db.set_field(btn, "bitmapPositionX", _DARK_COL_X, _DT_INT)
        db.set_field(btn, "bitmapPositionY", _ROW_Y[tier], _DT_INT)
        # skillTier == row (TIER LAW). Write only where it changes (Dark Aperture,
        # Throwing Knife); assert the unchanged bases (Darklings, Flurry) fail-loud.
        sk = _resolve(db, skill_path)
        if expect_tail in _GATE_WRITE:
            wtier, wgate = _GATE_WRITE[expect_tail]
            if wtier != tier:
                raise SystemExit("mastery_sv_alignment[C]: gate-write tier mismatch for %s" % label)
            db.set_field(sk, "skillTier", tier, _DT_INT)
            db.set_field(sk, "skillMasteryLevelRequired", wgate, _DT_INT)
        else:
            cur = _first(db.get_field_value(sk, "skillTier"))
            if str(cur) != str(tier):
                raise SystemExit("mastery_sv_alignment[C]: %s skillTier=%s expected %d "
                                 "(unlock %d) - upstream drift"
                                 % (label, cur, tier, _TIER_THRESHOLD[tier]))
    # Adjacent augment bars (len2 [Bottom,Top]) on the two family BASES; Dark Aperture
    # stray `_right` bar stays CLEARED. Flurry (top of its chain) owns no bar.
    dk_skill = _resolve(db, _DARKLINGS_SKILL)
    tk_skill = _resolve(db, _THROWKNIFE_SKILL)
    da_skill = _resolve(db, _DARKAP_SKILL)
    for base in (dk_skill, tk_skill):
        db.set_field(base, "skillConnectionOn", list(_STRAIGHT2_ON), _DT_STR)
        db.set_field(base, "skillConnectionOff", list(_STRAIGHT2_OFF), _DT_STR)
    db.set_field(da_skill, "skillConnectionOn", [], _DT_STR)        # clear stray _right bar
    db.set_field(da_skill, "skillConnectionOff", [], _DT_STR)
    # GUARANTEE the modifier<->base bindings survive (SkillTree tree-order, untouched).
    for mod_tail, base_tail, mlabel, blabel in _BIND_PAIRS:
        bind = _modifier_binding_base(db, _OCCULT_SKILLTREE, mod_tail)
        if bind != base_tail:
            raise SystemExit(
                "mastery_sv_alignment[C]: %s (%s) no longer binds to %s (%s) in the LIVE "
                "occult SkillTree - nearest preceding non-modifier is %r. The restack must "
                "NOT reorder SkillTree slots." % (mlabel, mod_tail, blabel, base_tail, bind))
    print("  [C2] col6 restack: Darklings t3 / Dark Aperture t4 (unlock 16) / Throwing "
          "Knife t5 (unlock 24) / Flurry t6; adjacent len2 bars, ZERO crossings; "
          "bindings DarkAp->Darklings + Flurry->ThrowKnife preserved (tree untouched)")

    # ---- D. Dark Invigoration = TRUE modifier of Shadow Link ----
    # D1. GUARANTEE the gameplay binding (SkillTree tree-order). Fail-loud if an upstream
    #     reshuffle ever puts a non-modifier between Shadow Link and Dark Invigoration.
    #     This is the REAL augment (Will 2026-07-16); it is already satisfied in build44/45,
    #     so this is an idempotent, read-only assertion (zero arz change) - the module is
    #     merely the ratified GUARANTOR of the binding.
    bind = _modifier_binding_base(db, _OCCULT_SKILLTREE, _DARKINVIG_TAIL)
    if bind != _SHADOWLINK_TAIL:
        raise SystemExit(
            "mastery_sv_alignment[D]: Dark Invigoration (%s) does NOT bind to Shadow Link "
            "in the LIVE occult SkillTree %s - nearest preceding non-modifier is %r, expected "
            "%r. TQ binds a Skill_Modifier by tree-order; Will's ruling requires this. Re-order "
            "the tree so drxbladehoning is the nearest preceding non-modifier of drxopenwound."
            % (_DARKINVIG_TAIL, _OCCULT_SKILLTREE, bind, _SHADOWLINK_TAIL))
    # D2. UI wire (KEEP build45): Shadow Link straight bar UP through c3t3 to Dark
    #     Invigoration at c3t4 - now correctly depicting the real augment (mirrors the
    #     vanilla Storm Nimbus column: base square + modifier circles stacked + bar).
    sl_skill = _resolve(db, _SHADOWLINK_SKILL)
    db.set_field(sl_skill, "skillConnectionOn", list(_STRAIGHT_ON), _DT_STR)
    db.set_field(sl_skill, "skillConnectionOff", list(_STRAIGHT_OFF), _DT_STR)
    print("  [D] Dark Invigoration TRUE-augments Shadow Link: SkillTree tree-order binding "
          "confirmed (drxbladehoning -> drxopenwound), Shadow Link straight bar UP to c3t4 kept")

    print("  [E] Earth Soften Metal: NO-OP (build44 already c4t2; SV c4t3 blocked by "
          "build41 Flame Surge restoration - see report)")
    print("=== mastery_sv_alignment done: A(4 shapes) B(9 emblems) C(col6 restack) "
          "D(wire) ===")


# ---------------------------------------------------------------------------
def _list_of(db, rec, field):
    v = db.get_field_value(rec, field)
    if v is None:
        return None
    return v if isinstance(v, list) else [v]


def _arc_resolver():
    """Build a b60-pattern arc resolver over the mod Resources + base game, if
    both are present on disk. Returns a resolve(ref)->bool callable, or None if
    the arcs are not available in this environment (then resolution is skipped
    and only the structural check runs)."""
    from pathlib import Path
    try:
        here = Path(__file__).resolve()
        # tools/patches/x.py -> repo root; walk UP so a linked git worktree still
        # finds the (gitignored, shared) main-repo work/SoulvizierClassic/Resources.
        mod_res = None
        for anc in here.parents:
            cand = anc / "work" / "SoulvizierClassic" / "Resources"
            if cand.is_dir():
                mod_res = cand
                break
        game = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                    r"\Titan Quest Anniversary Edition")
        if mod_res is None or not (game / "Resources").is_dir():
            return None
        # NOTE: do NOT mutate sys.path here. arc_patcher is already importable
        # (the build + validators keep tools/ on the path). Inserting the main-repo
        # tools/ ahead of the worktree's poisoned the build's later
        # `from validate_mastery_golden import validate` so it loaded the MAIN
        # repo's STALE golden instead of the worktree's -> false A7 gate FAIL.
        from arc_patcher import ArcArchive
    except Exception:
        return None
    xpack = {'xpack', 'xpack2', 'xpack3', 'xpack4'}
    cache = {}

    def names(folder, arc):
        if not Path(folder).is_dir():
            return None
        key = (str(folder).lower(), arc.lower())
        if key in cache:
            return cache[key]
        cand = Path(folder) / (arc + ".arc")
        if not cand.exists():
            hits = [p for p in Path(folder).glob("*.arc") if p.stem.lower() == arc.lower()]
            cand = hits[0] if hits else None
        nm = None
        if cand and cand.exists():
            try:
                a = ArcArchive.from_file(cand)
                nm = {e.name.lower().replace('\\', '/') for e in a.entries if e.name}
            except Exception:
                nm = None
        cache[key] = nm
        return nm

    def resolve(ref):
        parts = str(ref).replace('/', '\\').split('\\')
        if len(parts) < 2:
            return False
        p0 = parts[0].lower()
        if p0 in xpack and len(parts) >= 3:
            nm = names(game / "Resources" / parts[0], parts[1])
            inner = "/".join(parts[2:]).lower()
            return bool(nm) and inner in nm
        inner = "/".join(parts[1:]).lower()
        m = names(mod_res, parts[0])
        if m is not None and inner in m:
            return True
        b = names(game / "Resources", parts[0])
        return bool(b) and inner in b
    return resolve


def verify(db, tags):
    """Post-finalization guard (runs on the fully-assembled db): re-assert EVERY
    fix on the final arz. Fail-loud. This is the make-or-break negative-test
    surface (a planted wrong value must fail here)."""
    print("\n=== mastery_sv_alignment.verify: re-assert every b70 fix ===")
    bad = []

    # A. shapes
    for slot, button, preset, tail, label in _SHAPE_FIXES:
        rec = _resolve(db, (_UI % slot) + button + ".dbr")
        want = 1 if preset is _CIRCLE else 0
        got = _first(db.get_field_value(rec, "isCircular"))
        if str(got) != str(want):
            bad.append("[A] %s (%s) isCircular=%s want %s" % (rec, label, got, want))
        up = str(_first(db.get_field_value(rec, "bitmapNameUp")) or "")
        round_up = "round" in up.lower()
        if (preset is _CIRCLE) != round_up:
            bad.append("[A] %s (%s) border %r inconsistent with shape" % (rec, label, up))

    # B. emblem x9: BitmapUIAware + non-empty bitmapNames (+ arc resolution if avail)
    resolve = _arc_resolver()
    n_res = 0
    for dir_prefix, lbl in _EMBLEM_DIRS:
        rec = _resolve(db, dir_prefix + "masterybitmap.dbr")
        tpl = str(_first(db.get_field_value(rec, "templateName")) or "")
        names = _list_of(db, rec, "bitmapNames")
        px = _list_of(db, rec, "bitmapPositionsX")
        if not tpl.lower().endswith("bitmapuiaware.tpl"):
            bad.append("[B] %s templateName=%r want BitmapUIAware" % (rec, tpl))
        if not names or not str(names[0]).strip():
            bad.append("[B] %s bitmapNames empty/absent (black disc)" % rec)
        elif len(names) < 2:
            bad.append("[B] %s bitmapNames has %d entries want 2" % (rec, len(names)))
        if px != _EMBLEM_POS_X:
            bad.append("[B] %s bitmapPositionsX=%s want %s" % (rec, px, _EMBLEM_POS_X))
        if names and resolve is not None:
            for t in names:
                if not resolve(t):
                    bad.append("[B] %s emblem tex UNRESOLVED in shipped arcs: %s" % (rec, t))
                else:
                    n_res += 1

    # C2. Column-6 restack: the full bottom-to-top ladder (positions + tiers + gates),
    #     adjacent len2 bars on the two bases, Dark Aperture bar cleared, and the
    #     modifier<->base bindings intact. This is the make-or-break negative surface:
    #     a planted crossing bar (len>2) or a misrowed skill fails right here.
    for btn_const, skill_path, expect_tail, tier, label in _COL6_STACK:
        btn = _resolve(db, (_UI % 5) + btn_const + ".dbr")
        gx = _first(db.get_field_value(btn, "bitmapPositionX"))
        gy = _first(db.get_field_value(btn, "bitmapPositionY"))
        if str(gx) != str(_DARK_COL_X):
            bad.append("[C] %s (%s) x=%s want %s" % (btn, label, gx, _DARK_COL_X))
        if str(gy) != str(_ROW_Y[tier]):
            bad.append("[C] %s (%s) y=%s want %s (t%d)" % (btn, label, gy, _ROW_Y[tier], tier))
        # TIER LAW: the skill's skillTier must equal the button's row tier.
        sk = _resolve(db, skill_path)
        st = _first(db.get_field_value(sk, "skillTier"))
        if str(st) != str(tier):
            bad.append("[C] %s skillTier=%s want %d (row t%d) - TIER-LAW break"
                       % (label, st, tier, tier))
        # Effective unlock gate (max of tier threshold and any explicit req) must equal
        # the tier threshold == Will's stated unlock number for that row.
        req = _first(db.get_field_value(sk, "skillMasteryLevelRequired"))
        try:
            reqn = int(req) if req is not None else 0
        except (TypeError, ValueError):
            reqn = 0
        eff = max(_TIER_THRESHOLD[tier], reqn)
        if eff != _TIER_THRESHOLD[tier]:
            bad.append("[C] %s effective unlock gate=%d want %d (req=%s over-gates the row)"
                       % (label, eff, _TIER_THRESHOLD[tier], req))
    # adjacent len2 [Bottom,Top] bars on Darklings + Throwing Knife (ZERO crossings).
    for base_path, blabel in ((_DARKLINGS_SKILL, "Darklings"), (_THROWKNIFE_SKILL, "Throwing Knife")):
        base = _resolve(db, base_path)
        if _list_of(db, base, "skillConnectionOn") != _STRAIGHT2_ON:
            bad.append("[C] %s skillConnectionOn not the adjacent len2 bar: %s"
                       % (blabel, _list_of(db, base, "skillConnectionOn")))
        if _list_of(db, base, "skillConnectionOff") != _STRAIGHT2_OFF:
            bad.append("[C] %s skillConnectionOff not the adjacent len2 bar" % blabel)
    da_skill = _resolve(db, _DARKAP_SKILL)
    if _list_of(db, da_skill, "skillConnectionOn") not in (None, []):
        bad.append("[C] Dark Aperture stray _right skillConnectionOn NOT cleared: %s"
                   % _list_of(db, da_skill, "skillConnectionOn"))
    if _list_of(db, da_skill, "skillConnectionOff") not in (None, []):
        bad.append("[C] Dark Aperture stray _right skillConnectionOff NOT cleared")
    # bindings survive the restack (SkillTree tree-order untouched).
    for mod_tail, base_tail, mlabel, blabel in _BIND_PAIRS:
        b = _modifier_binding_base(db, _OCCULT_SKILLTREE, mod_tail)
        if b != base_tail:
            bad.append("[C] %s tree-order binding base=%r want %r (SkillTree reordered?)"
                       % (mlabel, b, base_tail))

    # D. Dark Invigoration TRUE-augments Shadow Link. MECHANISM-LEVEL assert (not just
    #    field-present): walk the LIVE occult SkillTree and prove drxbladehoning is the
    #    nearest preceding non-modifier of drxopenwound (== the engine's modifier binding).
    dbind = _modifier_binding_base(db, _OCCULT_SKILLTREE, _DARKINVIG_TAIL)
    if dbind != _SHADOWLINK_TAIL:
        bad.append("[D] Dark Invigoration tree-order binding base=%r want %r (occult SkillTree "
                   "does NOT bind drxopenwound to Shadow Link)" % (dbind, _SHADOWLINK_TAIL))
    # D. UI wire (build45) still present + correctly depicting the augment
    sl = _resolve(db, _SHADOWLINK_SKILL)
    if _list_of(db, sl, "skillConnectionOn") != _STRAIGHT_ON:
        bad.append("[D] Shadow Link skillConnectionOn not the straight wire")
    if _list_of(db, sl, "skillConnectionOff") != _STRAIGHT_OFF:
        bad.append("[D] Shadow Link skillConnectionOff not the straight wire")

    # F. verify-only chains still intact (build44 correct; nothing should disturb them)
    tc = _resolve(db, _TC_SKILL)
    tc_on = _list_of(db, tc, "skillConnectionOn") or []
    if not (len(tc_on) == 4 and any("connect" in t.lower() for t in tc_on)):
        bad.append("[F] Toxic Concoction chain (drx_scrap) bar not the expected len4 "
                   "connect-straight: %s" % tc_on)
    st = _resolve(db, _STALKER_SKILL)
    st_on = _list_of(db, st, "skillConnectionOn") or []
    if len(st_on) != 2:
        bad.append("[F] Shadow Stalker bar not the expected len2 straight: %s" % st_on)

    if bad:
        for b in bad:
            print("  FAIL:", b)
        raise SystemExit("mastery_sv_alignment.verify: %d defect(s) survived "
                         "finalization" % len(bad))
    print("  OK: A(4 shapes) B(9 emblems, %d tex resolved%s) C(col6 restack: "
          "Darklings t3/DarkAp t4/ThrowKnife t5/Flurry t6 + adjacent bars + tiers + "
          "gates + bindings) D(Dark Invig TRUE-augments Shadow Link: tree-order + wire) "
          "F(TC + Stalker chains intact)"
          % (n_res, "" if resolve is not None else "; resolution SKIPPED - arcs absent"))
