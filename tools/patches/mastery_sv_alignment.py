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

C. OCCULT FAMILY PLACEMENT (m5): move Darklings (skill25/drxdarklings) + Dark
   Aperture (skill26/drxdarklings_darkaperture) OUT of column 3 (Shadow Link's
   column) into column 6 - the ONLY build44 m5 column with BOTH t3 (y279) and t5
   (y155) free (occupancy map in the report). Darklings base -> c6 t3, Dark Aperture
   augment -> c6 t5, preserving the canonical pre-098i base@t3 / augment@t5 pattern
   (Dark Aperture directly above Darklings, its req 24 == t5). Darklings keeps its
   canonical straight [Bottom,Middle,Top] bar (re-asserted); Dark Aperture's stray
   inherited `_right` bar is CLEARED (pre-098i GT flags it as an artifact topping on
   void). Pre-098i GT deviation table 8.5. RESIDUAL (flagged, WILL-CONFIRM): c6 t4
   holds the CANONICAL SV098 Throwing Knife (drxthrowingknife) - immovable without a
   golden waiver - so Darklings' bar passes BEHIND it as an empty-row (Middle)
   passthrough; a fully "t4 EMPTY" column needs a holistic m5 reflow (previously
   reverted) or Will's ruling to relocate Throwing Knife. UI fields only.

D. DARK INVIGORATION CONNECTOR (m5): Dark Invigoration (skill07/drxopenwound) stays
   at c3 t4 (y217, already correct). ADD a straight [Bottom,Middle,Top] bar to Shadow
   Link (skill09/drxbladehoning, c3 t2 y341) so its bar draws UP through the now-empty
   c3 t3 to Dark Invigoration at t4. WILL directive ("Dark Invigoration should be
   there connected ... at the 16 row mark"). WILL-INTENT wire, NOT ground truth (SV098
   col3 is bare). GAMEPLAY-RELATION FINDING (flagged): drxopenwound has NO
   skillDependancy/buffSkillName/modifier reference to drxbladehoning - the connector
   is purely VISUAL; no augment relation exists.

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
               "Darklings family move + Dark Invigoration wire)")

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

# --- C. Darklings family relocation (column 3 -> column 6). --------------------
_DARK_COL_X = 628          # column 6 (only build44 m5 column with t3+t5 both free)
_DARKLINGS_BTN = "skill25"          # drxdarklings   (base, t3 y279)
_DARKAP_BTN = "skill26"             # drxdarklings_darkaperture (augment, t5 y155)
_DARKLINGS_SKILL = "records\\skills\\stealth\\drxdarklings.dbr"
_DARKAP_SKILL = "records\\skills\\stealth\\drxdarklings_darkaperture.dbr"

# canonical straight 3-tile bar (Bottom/Middle/Top) - matches the golden drxdarklings
# and the pre-098i drxlaytrap family byte-for-byte.
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

# --- D. Shadow Link -> Dark Invigoration wire. ---------------------------------
_SHADOWLINK_SKILL = "records\\skills\\stealth\\drxbladehoning.dbr"
_DARKINVIG_SKILL = "records\\skills\\stealth\\drxopenwound.dbr"

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

    # ---- C. Darklings family -> column 6 (base@t3, augment@t5) ----
    dk_btn = _resolve(db, (_UI % 5) + _DARKLINGS_BTN + ".dbr")
    da_btn = _resolve(db, (_UI % 5) + _DARKAP_BTN + ".dbr")
    if _skillname_tail(db, dk_btn) != "drxdarklings.dbr":
        raise SystemExit("mastery_sv_alignment[C]: m5 %s is not Darklings" % _DARKLINGS_BTN)
    if _skillname_tail(db, da_btn) != "drxdarklings_darkaperture.dbr":
        raise SystemExit("mastery_sv_alignment[C]: m5 %s is not Dark Aperture" % _DARKAP_BTN)
    db.set_field(dk_btn, "bitmapPositionX", _DARK_COL_X, _DT_INT)   # y (t3=279) unchanged
    db.set_field(da_btn, "bitmapPositionX", _DARK_COL_X, _DT_INT)   # y (t5=155) unchanged
    # Darklings straight bar (re-assert canonical B/M/T); Dark Aperture bar CLEARED.
    dk_skill = _resolve(db, _DARKLINGS_SKILL)
    da_skill = _resolve(db, _DARKAP_SKILL)
    db.set_field(dk_skill, "skillConnectionOn", list(_STRAIGHT_ON), _DT_STR)
    db.set_field(dk_skill, "skillConnectionOff", list(_STRAIGHT_OFF), _DT_STR)
    db.set_field(da_skill, "skillConnectionOn", [], _DT_STR)        # clear stray _right bar
    db.set_field(da_skill, "skillConnectionOff", [], _DT_STR)
    print("  [C] Darklings %s + Dark Aperture %s -> column 6 (x=628, t3/t5); "
          "Darklings straight bar re-asserted; Dark Aperture _right bar CLEARED"
          % (_DARKLINGS_BTN, _DARKAP_BTN))

    # ---- D. Shadow Link -> Dark Invigoration straight wire ----
    sl_skill = _resolve(db, _SHADOWLINK_SKILL)
    db.set_field(sl_skill, "skillConnectionOn", list(_STRAIGHT_ON), _DT_STR)
    db.set_field(sl_skill, "skillConnectionOff", list(_STRAIGHT_OFF), _DT_STR)
    print("  [D] Shadow Link (drxbladehoning c3t2) straight bar UP to Dark "
          "Invigoration (c3t4) - WILL-INTENT visual wire")

    print("  [E] Earth Soften Metal: NO-OP (build44 already c4t2; SV c4t3 blocked by "
          "build41 Flame Surge restoration - see report)")
    print("=== mastery_sv_alignment done: A(4 shapes) B(9 emblems) C(family move) "
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

    # C. Darklings family in column 6, canonical bar; Dark Aperture bar cleared
    dk_btn = _resolve(db, (_UI % 5) + _DARKLINGS_BTN + ".dbr")
    da_btn = _resolve(db, (_UI % 5) + _DARKAP_BTN + ".dbr")
    for btn, lbl, wy in ((dk_btn, "Darklings", 279), (da_btn, "Dark Aperture", 155)):
        gx = _first(db.get_field_value(btn, "bitmapPositionX"))
        gy = _first(db.get_field_value(btn, "bitmapPositionY"))
        if str(gx) != str(_DARK_COL_X):
            bad.append("[C] %s (%s) x=%s want %s" % (btn, lbl, gx, _DARK_COL_X))
        if str(gy) != str(wy):
            bad.append("[C] %s (%s) y=%s want %s" % (btn, lbl, gy, wy))
    dk_skill = _resolve(db, _DARKLINGS_SKILL)
    if _list_of(db, dk_skill, "skillConnectionOn") != _STRAIGHT_ON:
        bad.append("[C] Darklings skillConnectionOn not canonical straight bar")
    if _list_of(db, dk_skill, "skillConnectionOff") != _STRAIGHT_OFF:
        bad.append("[C] Darklings skillConnectionOff not canonical straight bar")
    da_skill = _resolve(db, _DARKAP_SKILL)
    if _list_of(db, da_skill, "skillConnectionOn") not in (None, []):
        bad.append("[C] Dark Aperture stray _right skillConnectionOn NOT cleared: %s"
                   % _list_of(db, da_skill, "skillConnectionOn"))
    if _list_of(db, da_skill, "skillConnectionOff") not in (None, []):
        bad.append("[C] Dark Aperture stray _right skillConnectionOff NOT cleared")

    # D. Shadow Link straight wire to Dark Invigoration
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
    print("  OK: A(4 shapes) B(9 emblems, %d tex resolved%s) C(family@col6 + bars) "
          "D(Shadow Link wire) F(TC + Stalker chains intact)"
          % (n_res, "" if resolve is not None else "; resolution SKIPPED - arcs absent"))
