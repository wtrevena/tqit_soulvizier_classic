r"""oh_pane_art - Occult (mastery 5) tree-pane BACKGROUND ART fix, round 1
(b67 wave, ships build43).

Will's directive (verbatim): "Go ahead and fix the occultist and hunting
mastery black-background fixes. You may need to go into SV files to find the
appropriate background image for the occult mastery skill selection page."

CONTEXT: the b60 wave (`mastery_bg_render.py`, shipped build42) fixed the
RENDER MECHANISM for all 9 live mastery panes (BitmapSingle -> the vanilla
BitmapUIAware widget the pane slot actually reads) - the panes stopped being
literally BLACK. But b60 was an explicit, documented "pure STRUCTURE upgrade"
that deliberately did NOT "second-guess the texture CHOICE the earlier waves
made" - so Occult (mastery 5, built on the base game's Rogue/Stealth UI slot)
was left pointing at the VANILLA `InGameUI\Skills\StealthSkillBackground01.tex`
backdrop: a tan/parchment stone tablet with no occult identity at all, because
that slot's stock art belongs to Rogue, not Occult.

SOURCE HUNT (this wave, decoded via `tools/tex_decode.py` against
`work/SoulvizierClassic/Resources/DRXtextures.arc`):

  - SV 0.98i's OWN `database.arz` (upstream/soulvizier_098i) was checked first:
    its `mastery 5\skillpanebasebitmap.dbr` still points at the dead
    `SkillsPanel\skillbackgrounddiablo.tex` (the same defect b37/b60 fixed in
    our build) - i.e. SV 0.98i itself never shipped a WORKING Occult tree-pane
    background either. There is no "restore the lost SV art" path for this
    specific slot; b60's base-game repoint is the only route that renders.
  - BUT `DRXtextures\masterybackdrops\` (1464-entry arc, D5-decoded) DOES carry
    a family of bespoke pane-art assets never fully wired:
      * `newstealthpanel01.tex` (175x175) - a witch portrait (pale skin, dark
        hood, occult rune/moon-circle) - ALREADY correctly wired as Occult's
        DECORATIVE `masterybitmap.dbr` art (the circle on the pane's right
        edge), in BOTH SV 0.98i's own database and ours. Confirms SV/DRX DID
        design a distinct Occult identity for this mastery slot.
      * `occultpanellarge.tex` (250x250) - the SAME witch portrait, larger -
        SV/DRX's bespoke SELECT-MASTERY-SCREEN preview asset (see
        `import_occult_select_mastery_art` in build_svc_database.py; a
        different record family, wired separately).
      * `standardskillbackground_joanna_ver_dark.tex` (919x540 - the EXACT
        tree-pane background class size) - a "Joanna" ("Joanna" = the DRX
        texture-artist credit baked into the filename) dark grey/teal stone
        tablet with a PURPLE accent square (bottom-right "selected tier" slot)
        and an empty round cutout (top-right) sized for the masterybitmap
        circle - i.e. a generic, mastery-agnostic ALTERNATE dark skin with no
        baked-in decorative content of its own (so it composites cleanly under
        the witch-portrait masterybitmap already drawn on top). Confirmed
        UNUSED anywhere in SV 0.98i's own database or ours (0 references) - an
        authored-but-never-wired DRX asset, exactly the "SV shipped bespoke art
        but never wired it" case Will's directive anticipated.
      * Also decoded and REJECTED as candidates: `stealthpanel02.tex` /
        `stealthpanelbig.tex` (226x226 - the wrong size class; both are the
        SAME vanilla Rogue-dagger-and-satyr artwork with an added lightning FX
        overlay, not occult-themed) and `drx_spiritskillbackground01.tex`
        (919x540 but bakes a GHOST figure into its own circle slot - a Dream/
        spectral-themed asset that would visually collide with the witch
        masterybitmap already drawn over the same circle; `spiritskillbackground
        01.tex` is a byte-for-byte copy of the base game's own Spirit
        backdrop, i.e. not occult-themed either).

  Verdict: `standardskillbackground_joanna_ver_dark.tex` is the most
  thematically-appropriate EXISTING texture for Occult's tree-pane background -
  dark, moody, with a purple accent that harmonizes with the witch portrait
  already on the pane. No new art authored; this is a pure re-pointing of a
  pre-existing, shipped-but-unused SV/DRX asset (docs/reports/b67_oh_pane_art.md
  has the full decode + rationale for Will's veto).

THE FIX (this module, mouse/keyboard mode ONLY - see residual below):
  `records\ingameui\player skills\mastery 5\skillpanebasebitmap.dbr` ::
  `bitmapNames[0]` (the mouse-mode texture the b60 BitmapUIAware slot reads)
  -> `DRXtextures\masterybackdrops\standardskillbackground_joanna_ver_dark.tex`.
  `bitmapNames[1]` (the `InGameUI\Controller\Skills\...` gamepad-mode sibling)
  is LEFT at the vanilla `StealthSkillBackground01.tex` controller texture:
  the DRX dark tablet is 919x540 (the mouse-mode canvas) but the base game's
  own controller-mode canvas for this slot is 980x540 (61px wider, to make
  room for button-prompt icons - D5-confirmed via `Controller\Skills\
  StealthSkillBackground01.tex`); no DRX/SV asset exists at that wider size,
  and this module never authors new art, so gamepad play keeps the vanilla
  tan backdrop (still renders correctly, just not reskinned) rather than
  clipping/gapping a too-narrow image into a too-wide canvas. Flagged as a
  residual for Will in docs/reports/b67_oh_pane_art.md.

NOT touched (documented choices, no bespoke asset exists for any of these):
  - Occult's REALLOCATION pane (`skillpanereallocationbitmap.dbr`): vanilla
    `StealthSkillReallocationBackground01.tex` (a blue magic-swirl motif that
    is THEME-INDEPENDENT across every base-game mastery - signals "reallocation
    mode", not mastery identity - so leaving it vanilla is correct, not a gap).
  - Occult's decorative `masterybitmap.dbr`: already correct (see above).
  - Occult's `masterybar.dbr` (mastery-level bar art): vanilla
    `InGameUI\Skills\StealthSkillBar01.tex`; DRX shipped no bespoke
    stealthbar/occultbar asset (0 hits swept across DRXtextures.arc).
  - Occult's select-mastery-screen BUTTON icon (Up/Down/Over/Disabled, 80x80):
    vanilla `StealthButton*01.tex`; DRX shipped no bespoke asset (0 hits).
  - Hunting (mastery 6) in its ENTIRETY: verified appropriate as-is (native,
    unchanged identity - Hunting was never reskinned by SV/DRX). Tree-pane
    background = base-game `HuntingSkillBackground01.tex`; decorative
    `masterybitmap.dbr` = base-game `HuntingPanel01.tex`; select-screen +
    mastery bar = base-game Hunting assets throughout. No defect found, no
    action taken - this module verifies (not fixes) Hunting.

Contract: patches-registry module - MODULE_NAME + apply(db, tags) + verify(db,
tags). MUST run AFTER `mastery_bg_render` (b60) - it upgrades the texture
CHOICE that wave's BitmapUIAware structure fix set, exactly mirroring how b60
itself was documented to run after `hunting_occult_ui`/`mastery_ui_audit`.
Occult (m5) is golden-tracked (A7); the resulting `bitmapNames` drift on
`skillpanebasebitmap.dbr` is a Will-authorized `owner_approved_overrides` entry
in `tools/occult_hunting_golden.json` citing this directive.
"""

MODULE_NAME = ("Occult (mastery 5) tree-pane background art fix - vanilla "
               "Stealth backdrop -> bespoke DRX dark tablet (Hunting verified OK)")

_DT_STR = 2

_M5_BASE = r"records\ingameui\player skills\mastery 5\skillpanebasebitmap.dbr"
_M5_REALLOC = r"records\ingameui\player skills\mastery 5\skillpanereallocationbitmap.dbr"
_M6_BASE = r"records\ingameui\player skills\mastery 6\skillpanebasebitmap.dbr"
_M6_REALLOC = r"records\ingameui\player skills\mastery 6\skillpanereallocationbitmap.dbr"

_EXPECT_M5_BASE = [r"InGameUI\Skills\StealthSkillBackground01.tex",
                   r"InGameUI\Controller\Skills\StealthSkillBackground01.tex"]
_NEW_M5_BASE = [r"DRXtextures\masterybackdrops\standardskillbackground_joanna_ver_dark.tex",
               r"InGameUI\Controller\Skills\StealthSkillBackground01.tex"]

# Untouched siblings this module PROVES stay byte-identical (regression guard,
# see verify()) rather than merely leaving alone.
_EXPECT_M5_REALLOC = [r"InGameUI\Skills\StealthSkillReallocationBackground01.tex",
                      r"InGameUI\Controller\Skills\StealthSkillReallocationBackground01.tex"]
_EXPECT_M6_BASE = [r"InGameUI\Skills\HuntingSkillBackground01.tex",
                   r"InGameUI\Controller\Skills\HuntingSkillBackground01.tex"]
_EXPECT_M6_REALLOC = [r"InGameUI\Skills\HuntingSkillReallocationBackground01.tex",
                      r"InGameUI\Controller\Skills\HuntingSkillReallocationBackground01.tex"]


def _resolve(db, rec):
    if db.has_record(rec):
        return rec
    low = rec.lower().replace('/', '\\')
    for n in db.record_names():
        if n.lower().replace('/', '\\') == low:
            return n
    raise SystemExit("oh_pane_art: expected record missing: %s "
                     "(upstream structure changed?)" % rec)


def _names(db, rec):
    v = db.get_field_value(rec, "bitmapNames")
    if v is None:
        return None
    return list(v) if isinstance(v, list) else [v]


def _require_state(db, rec, expect, label):
    cur = _names(db, rec)
    if cur != expect:
        raise SystemExit(
            "oh_pane_art: %s (%s) bitmapNames drifted from the expected b60 "
            "state before this fix could run.\n      expected: %s\n      "
            "found   : %s\n      (did mastery_bg_render run first? did an "
            "unrelated wave touch this record?)" % (rec, label, expect, cur))


def apply(db, tags):
    """Repoint Occult's (mastery 5) tree-pane BACKGROUND mouse-mode texture to
    the bespoke DRX dark tablet; leave the controller sibling, the
    reallocation pane, and everything on Hunting (mastery 6) untouched.
    `tags` unused (record-only fix; the texture is a DRX asset already shipped
    in DRXtextures.arc - no Text tag needed)."""
    print("\n=== oh_pane_art: Occult tree-pane background art fix (b67 wave) ===")

    base = _resolve(db, _M5_BASE)
    _require_state(db, base, _EXPECT_M5_BASE, "Occult base pane, pre-fix")
    db.set_field(base, "bitmapNames", list(_NEW_M5_BASE), _DT_STR)
    print("  Occult skillpanebasebitmap.dbr :: bitmapNames[0] %s -> %s"
          % (_EXPECT_M5_BASE[0], _NEW_M5_BASE[0]))
    print("  Occult skillpanebasebitmap.dbr :: bitmapNames[1] (controller) "
          "unchanged: %s (no DRX asset at the 980x540 controller-canvas size; "
          "residual, flagged for Will)" % _NEW_M5_BASE[1])

    # Prove (not merely assert) every sibling this module deliberately leaves
    # alone is still exactly the b60-shipped vanilla state.
    for rec, expect, label in (
        (_M5_REALLOC, _EXPECT_M5_REALLOC, "Occult reallocation pane"),
        (_M6_BASE, _EXPECT_M6_BASE, "Hunting base pane"),
        (_M6_REALLOC, _EXPECT_M6_REALLOC, "Hunting reallocation pane"),
    ):
        r = _resolve(db, rec)
        _require_state(db, r, expect, label)
        print("  %-28s untouched (verified vanilla, no defect found): %s"
              % (label, expect[0]))

    print("=== oh_pane_art done: 1 texture repointed (Occult base, mouse-mode); "
          "3 siblings verified unchanged ===")


def verify(db, tags):
    """Post-finalization guard: Occult's base pane is still the new dark
    tablet + unchanged controller sibling; Occult's reallocation pane and all
    of Hunting are still exactly the b60-shipped vanilla state (no later
    module reverted or collided with this fix). Fail-loud."""
    print("\n=== oh_pane_art.verify: Occult art holds, Hunting untouched ===")
    bad = []
    checks = (
        (_M5_BASE, _NEW_M5_BASE, "Occult base pane (this fix)"),
        (_M5_REALLOC, _EXPECT_M5_REALLOC, "Occult reallocation pane"),
        (_M6_BASE, _EXPECT_M6_BASE, "Hunting base pane"),
        (_M6_REALLOC, _EXPECT_M6_REALLOC, "Hunting reallocation pane"),
    )
    for rec_path, expect, label in checks:
        rec = _resolve(db, rec_path)
        tpl = db.get_field_value(rec, "templateName")
        if isinstance(tpl, list):
            tpl = tpl[0] if tpl else ""
        if not str(tpl or "").lower().endswith("bitmapuiaware.tpl"):
            bad.append("%s (%s) :: templateName=%r (want BitmapUIAware)"
                       % (rec, label, tpl))
        cur = _names(db, rec)
        if cur != expect:
            bad.append("%s (%s) :: bitmapNames drifted\n      expected: %s\n"
                       "      found   : %s" % (rec, label, expect, cur))
    if bad:
        for b in bad:
            print("  FAIL:", b)
        raise SystemExit("oh_pane_art.verify: %d defect(s) survived "
                         "finalization" % len(bad))
    print("  OK: Occult base pane = dark DRX tablet (mouse) + vanilla "
          "controller sibling; Occult reallocation + all Hunting untouched")
