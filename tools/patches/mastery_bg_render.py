r"""mastery_bg_render - mastery skill-pane BLACK BACKGROUND true render fix
(b60 wave, ships build42; Will 2026-07-14: "the mastery skill selection screens STILL have a
black background").

ROOT CAUSE (proven read-only against the DEPLOYED build40-dev arz md5 b33c5a44 +
the base-game database.arz + base InGameUI.arc; full evidence in
docs/reports/b60_mastery_bg_render.md):

  The b37 `hunting_occult_ui` + b38 `mastery_ui_audit` waves REPOINTED each
  mastery pane background's texture from the unresolvable `SkillsPanel\...diablo`
  to `InGameUI\Skills\<Class>SkillBackground01.tex` (which DOES resolve in the
  base InGameUI.arc the mod loads at runtime). That fixed the *texture path* but
  NOT the render: the panes stayed BLACK because the mod's pane-background
  records are the wrong WIDGET CLASS for the skill-pane slot.

    - VANILLA (renders): every mastery's `skillpanebasebitmap.dbr` /
      `skillpanereallocationbitmap.dbr` is a **BitmapUIAware.tpl** record whose
      bitmap lives in the PLURAL `bitmapNames` array = the mouse texture PLUS its
      `InGameUI\Controller\Skills\...` controller sibling (positions in
      `bitmapPositionsX/Y`). TQAE added controller support and made the pane
      background UI-aware; the `panectrl.dbr::skillPaneBaseBitmap` slot reads
      `bitmapNames`.
    - MOD (black): the SV 0.98i (TQ:Immortal-Throne era) DB merge OVERRODE those
      records with **BitmapSingle.tpl** records carrying a SINGULAR `bitmapName`.
      The b37/b38 fix set `bitmapName` on the BitmapSingle record - a field the
      UI-aware pane slot never reads. The texture resolves in the arc but the
      slot never requests it -> the pane draws nothing -> BLACK. (Proof it is the
      structure and not resolution: base InGameUI.arc IS loaded at runtime - the
      skill BUTTON borders `InGameUI\SkillButtonBorder01.tex` render, which is how
      Will can see the skill circles/squares over the black pane - and BitmapSingle
      itself renders fine for the small chrome numbers; but the base game is 100%
      consistent that the pane-background slot is BitmapUIAware, never BitmapSingle.)

  This is the same "record resolves statically but never renders at runtime"
  class as the graft-icon / boss-arena art families: valid file, wrong wiring.

THE FIX (this module): restore the EXACT vanilla structure for all 9 live player
masteries (1-8 under `records\ingameui\player skills\`, Dream/9 under
`records\xpack\ui\skills\`), for BOTH the base and the reallocation pane:

  templateName    -> database\Templates\InGameUI\BitmapUIAware.tpl
  FileDescription -> BitmapUIAware
  bitmapNames     -> [ <current mouse .tex>, <its InGameUI\Controller\Skills\ sibling> ]
  bitmapPositionsX/Y -> [0, 0]
  (the singular bitmapName / bitmapPositionX / bitmapPositionY are dropped)

The mouse texture is READ from whatever the earlier waves left on the record
(Warfare/Defense/.../Stealth for 5/Spirit for Dream-9), so this module is a pure
STRUCTURE upgrade layered on top of hunting_occult_ui + mastery_ui_audit - it does
not second-guess their texture choices, and it is idempotent. Every referenced
texture (mouse + controller) is verified to resolve by the build gate
`tools/gate_mastery_bg_render.py` (fail-loud) - a records-point-at-nothing pane
can never ship silently again.

PLUS the shared skill-window CHROME that every mastery pane composites and that
the same SV merge left pointing at the missing `SkillsPanel\...diablo` arc
(undo / undo-mastery buttons, gold + cost-per-point number backdrops): repointed
to their base-game `InGameUI\Skills\...01.tex` equivalents (all present in base
InGameUI.arc; templates unchanged - these slots legitimately read BitmapSingle /
ButtonStaticText).

NOT touched (documented in the report, deliberately out of scope):
  - `records\xpack\ui\skills\mastery 9\11-15-06\...` (an ArtManager auto-backup
    subfolder; 0 references - dead) and
  - `records\skills\scroll skills\masteries\earth\...` (a DRX dev-leftover mastery
    tree whose panectrl has 0 references - unreachable by any player).
  Both still carry the old `SkillsPanel\...diablo` refs but are unreachable, so
  repointing them is noise; the gate is scoped to the LIVE player masteries.

Contract: patches-registry module - MODULE_NAME + apply(db, tags) + verify(db, tags).
Registered AFTER hunting_occult_ui + mastery_ui_audit so it upgrades the structure
of whatever texture those set. Occult (m5) + Hunting (m6) are golden-tracked; the
resulting structural drift is Will-authorized (this render fix) via
owner_approved_overrides in tools/occult_hunting_golden.json.
"""

MODULE_NAME = ("Mastery pane BLACK-BACKGROUND render fix (BitmapSingle -> vanilla "
               "BitmapUIAware + controller sibling; + shared chrome repoint)")

# ---------------------------------------------------------------------------
_UI = "records\\ingameui\\player skills\\mastery %d\\"          # masteries 1-8
_DREAM = "records\\xpack\\ui\\skills\\mastery 9\\"              # Dream / mastery 9
_MB = "records\\ingameui\\player skills\\mastery base\\"        # shared chrome

_UIAWARE_TPL = r"database\Templates\InGameUI\BitmapUIAware.tpl"

# dtype ids (mirror arz_patcher.DATA_TYPE_*): 0 = INT, 2 = STRING.
_DT_INT = 0
_DT_STR = 2

# The 9 live pane records to restructure (base + reallocation each).
_PANE_DIRS = [_UI % n for n in range(1, 9)] + [_DREAM]
_PANE_LEAVES = ("skillpanebasebitmap.dbr", "skillpanereallocationbitmap.dbr")

# Shared chrome still pointing at the missing SkillsPanel arc -> base equivalents.
# (record, {field: base_tex}). Templates are LEFT unchanged (these slots read
# BitmapSingle / ButtonStaticText legitimately).
_CHROME = [
    (_MB + "undobutton.dbr", {
        "bitmapNameUp":       r"InGameUI\Skills\UndoBtnUp01.tex",
        "bitmapNameDown":     r"InGameUI\Skills\UndoBtnDown01.tex",
        "bitmapNameInFocus":  r"InGameUI\Skills\UndoBtnOver01.tex",
        "bitmapNameDisabled": r"InGameUI\Skills\UndoBtnDisabled01.tex",
    }),
    (_MB + "undomasteryselectionbutton.dbr", {
        "bitmapNameUp":       r"InGameUI\Skills\UndoMasteryBtnUp01.tex",
        "bitmapNameDown":     r"InGameUI\Skills\UndoMasteryBtnDown01.tex",
        "bitmapNameInFocus":  r"InGameUI\Skills\UndoMasteryBtnOver01.tex",
        "bitmapNameDisabled": r"InGameUI\Skills\UndoMasteryBtnDisabled01.tex",
    }),
    (_MB + "costperpointnumberbitmap.dbr",
     {"bitmapName": r"InGameUI\Skills\CostPerPoint01.tex"}),
    (_MB + "playergoldnumberbitmap.dbr",
     {"bitmapName": r"InGameUI\Skills\CurrentGold01.tex"}),
]


def _resolve(db, rec):
    """Case-insensitive record lookup; fail-loud if absent."""
    if db.has_record(rec):
        return rec
    low = rec.lower().replace('/', '\\')
    for n in db.record_names():
        if n.lower().replace('/', '\\') == low:
            return n
    raise SystemExit("mastery_bg_render: expected record missing: %s "
                     "(upstream structure changed?)" % rec)


def _first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _controller_sibling(tex):
    r"""InGameUI\Skills\WarfareSkillBackground01.tex ->
        InGameUI\Controller\Skills\WarfareSkillBackground01.tex
    (insert `Controller\` after the first path component = the arc name)."""
    parts = str(tex).replace('/', '\\').split('\\', 1)
    if len(parts) != 2:
        raise SystemExit("mastery_bg_render: pane texture has no sub-path: %r" % tex)
    return parts[0] + "\\Controller\\" + parts[1]


def _drop_field(fields, name):
    """Remove every ###-merged variant of `name` from the live fields dict."""
    for k in [k for k in fields if k.split('###')[0] == name]:
        del fields[k]


def _restructure_pane(db, rec):
    """Convert a BitmapSingle pane record to the vanilla BitmapUIAware structure,
    preserving whatever mouse texture is currently set and adding its controller
    sibling. Fail-loud if the record lacks a resolvable singular bitmapName."""
    cur = _first(db.get_field_value(rec, "bitmapName"))
    if not cur or not str(cur).strip():
        raise SystemExit(
            "mastery_bg_render: %s has no singular bitmapName to migrate "
            "(did hunting_occult_ui / mastery_ui_audit run first?)" % rec)
    mouse = str(cur).strip()
    if not mouse.lower().startswith("ingameui\\") and not mouse.lower().startswith("ingameui/"):
        raise SystemExit(
            "mastery_bg_render: %s bitmapName %r is not an InGameUI\\ path; refuse "
            "to build a controller sibling for an unexpected arc (regression?)"
            % (rec, mouse))
    controller = _controller_sibling(mouse)

    # template + description -> BitmapUIAware
    db.set_field(rec, "templateName", _UIAWARE_TPL, _DT_STR)
    db.set_field(rec, "FileDescription", "BitmapUIAware", _DT_STR)
    # plural bitmap + positions (the fields the UI-aware pane slot actually reads)
    db.set_field(rec, "bitmapNames", [mouse, controller], _DT_STR)
    db.set_field(rec, "bitmapPositionsX", [0, 0], _DT_INT)
    db.set_field(rec, "bitmapPositionsY", [0, 0], _DT_INT)
    # drop the singular fields the UI-aware slot ignores (empty -> skipped on encode)
    fields = db.get_fields(rec)
    for f in ("bitmapName", "bitmapPositionX", "bitmapPositionY"):
        _drop_field(fields, f)
    return mouse, controller


def apply(db, tags):
    """Restructure all 9 live mastery pane backgrounds (base + reallocation) to
    the vanilla BitmapUIAware form, and repoint the shared SkillsPanel chrome.
    `tags` unused (record-only fix; every referenced texture is a base-game
    InGameUI asset that resolves at runtime and needs no Text tag)."""
    print("\n=== mastery_bg_render: mastery pane black-background render fix (b60 wave) ===")

    panes = 0
    for d in _PANE_DIRS:
        for leaf in _PANE_LEAVES:
            rec = _resolve(db, d + leaf)
            mouse, controller = _restructure_pane(db, rec)
            panes += 1
            print("  pane  %-58s -> BitmapUIAware [%s (+controller)]"
                  % (leaf + " @" + d.split("player skills\\")[-1].rstrip("\\"),
                     mouse.rsplit("\\", 1)[-1]))
    print("  pane records restructured BitmapSingle -> BitmapUIAware: %d "
          "(9 masteries x base+reallocation)" % panes)

    chrome = 0
    for rec_path, fieldmap in _CHROME:
        rec = _resolve(db, rec_path)
        for field, tex in fieldmap.items():
            if db.get_field_value(rec, field) is None:
                raise SystemExit("mastery_bg_render: %s lacks expected field %s "
                                 "(upstream structure changed?)" % (rec, field))
            db.set_field(rec, field, tex, _DT_STR)
        chrome += 1
        print("  chrome %-40s -> InGameUI\\Skills (%d field(s))"
              % (rec_path.rsplit("\\", 1)[-1], len(fieldmap)))
    print("  shared chrome records repointed SkillsPanel -> InGameUI: %d" % chrome)
    print("=== mastery_bg_render done: %d panes + %d chrome ===" % (panes, chrome))


def verify(db, tags):
    """Post-finalization guard (runs on the fully-assembled db): every live pane
    background is now BitmapUIAware with a non-empty bitmapNames, and no live
    mastery UI record still references the dead SkillsPanel arc. Fail-loud."""
    print("\n=== mastery_bg_render.verify: pane structure + no SkillsPanel refs ===")
    bad = []
    for d in _PANE_DIRS:
        for leaf in _PANE_LEAVES:
            rec = _resolve(db, d + leaf)
            tpl = str(_first(db.get_field_value(rec, "templateName")) or "")
            names = db.get_field_value(rec, "bitmapNames")
            if not tpl.lower().endswith("bitmapuiaware.tpl"):
                bad.append("%s :: templateName=%r (want BitmapUIAware)" % (rec, tpl))
            if not names or not str(_first(names) or "").strip():
                bad.append("%s :: bitmapNames empty/absent" % rec)
    # no LIVE mastery-pane / chrome record may still point at SkillsPanel
    live_prefixes = tuple(d.lower() for d in _PANE_DIRS) + (_MB.lower(),)
    for n in db.record_names():
        nl = n.lower().replace('/', '\\')
        if not nl.startswith(live_prefixes):
            continue
        for k, tf in (db.get_fields(n) or {}).items():
            for v in tf.values:
                if isinstance(v, str) and v.lower().startswith("skillspanel\\"):
                    bad.append("%s :: %s still -> %s (dead arc)"
                               % (n, k.split('###')[0], v))
    if bad:
        for b in bad:
            print("  FAIL:", b)
        raise SystemExit("mastery_bg_render.verify: %d pane/chrome defect(s) "
                         "survived finalization" % len(bad))
    print("  OK: 18 panes BitmapUIAware w/ bitmapNames; 0 live SkillsPanel refs")
