r"""mastery_bg_template - restore the mastery skill-tree BACKGROUND image (build40).

REPEAT-FILED P1 (Will, THIRD report): the mastery skill-tree screens render with a
pure-BLACK background (his Occult screenshot: black behind the purple skill web).
b37 hunting_occult_ui and b38 mastery_ui_audit BOTH claimed to fix this by
repointing the `bitmapName` field of each mastery's skillpanebasebitmap record to a
base-game backdrop texture - yet build38a-dev STILL renders black. That repoint is
the WRONG MECHANISM and is removed by this wave (see hunting_occult_ui / mastery_ui_
audit edits); this module fixes the TRUE cause.

TRUE ROOT CAUSE (proven; full evidence chain in docs/reports/b40_mastery_bg_rca.md):
  The AE engine renders the skill-pane backdrop (SkillPaneCtrl.skillPaneBaseBitmap /
  skillPaneBaseReallocationBitmap slots) from a `BitmapUIAware` record via its PLURAL
  `bitmapNames` array [keyboard-tex, controller-tex]. Every base-game mastery pane
  background is exactly that: template BitmapUIAware.tpl, bitmapNames =
  [InGameUI\Skills\<Class>SkillBackground01.tex, InGameUI\Controller\Skills\<...>].

  SV 0.98i (a TQ-ImmortalThrone-era mod, pre-BitmapUIAware) shipped these records as
  the OLDER `BitmapSingle` template with a SINGULAR `bitmapName` pointing at its own
  `SkillsPanel\skillbackgrounddiablo.tex` (a texture this mod never packaged). Our DB
  inherits the SV records verbatim -> ALL 9 masteries carry BitmapSingle backdrops.
  The AE skill-pane renderer does not display a BitmapSingle record in that slot, so
  the pane is BLACK regardless of what its bitmapName points at.

  DECISIVE PROOF the template (not the texture value) is the cause: build38a-dev's
  live DB already points these BitmapSingle records at the EXACT texture the working
  base game uses (InGameUI\Skills\WarfareSkillBackground01.tex - the b37/b38 repoint),
  and that texture PROVABLY resolves at runtime (it lives in base InGameUI.arc as
  skills/warfareskillbackground01.tex, and base InGameUI.arc IS in the custom-quest
  resource path - our mod ships no InGameUI.arc, yet in-game skill ICONS, which live
  ONLY in base InGameUI.arc, render fine). Same resolvable texture + BitmapSingle
  template => black; base uses the same texture + BitmapUIAware => renders. The
  differentiator is the template + field shape, which the value-repoint never touched.

THE FIX: convert each live mastery-pane background record from BitmapSingle to the
base-game BitmapUIAware shape - reproducing the WORKING base configuration exactly:
  templateName     = database\\Templates\\InGameUI\\BitmapUIAware.tpl
  FileDescription  = BitmapUIAware
  bitmapNames      = [InGameUI\\Skills\\<Class>SkillBackground01.tex,
                      InGameUI\\Controller\\Skills\\<Class>SkillBackground01.tex]
  bitmapPositionsX = [0, 0]
  bitmapPositionsY = [0, 0]
(the singular bitmapName / bitmapPositionX / bitmapPositionY fields are dropped, so
each record byte-matches the base-game record). Textures used are the base game's own
per-mastery backdrops, every one D-confirmed present in base InGameUI.arc (skills/ +
controller/skills/), so they resolve at runtime for a Custom Quest.

SCOPE (18 live records): masteries 1-8 (records\\ingameui\\player skills\\mastery N\\)
base + reallocation, and the Dream mastery (records\\xpack\\ui\\skills\\mastery 9\\;
base uses Nature's backdrop for Dream). The vestigial `records\\skills\\scroll skills\\
masteries\\earth\\...` records (an old TQ-IT scrollable-skill-list path, referenced by
no live panectrl) and the dated `mastery 9\\11-15-06\\...` backup records are left
untouched (dead; base ships the dated ones as BitmapSingle too). masterybitmap.dbr
(the class emblem) is a separate visual element Will did not report and is left as-is.

Masteries 5 (Occult) + 6 (Hunting) are GOLDEN-tracked (Will's hand-tuned trees). This
UI-defect fix reproduces the base-game working state and is Will-authorized (his THIRD
report demanding the background back); the golden drift keys are recorded as
owner_approved_overrides in tools/occult_hunting_golden.json (the F5 / b37-background
waiver precedent). NO skill VALUES change - background bitmap records only.

CONTRACT: patches-registry module - MODULE_NAME + apply(db, tags). Sole owner of the
mastery-pane background records (the b37/b38 background repoints are removed), so no
collision. Fail-loud if any target record is unexpectedly absent (upstream structure
changed). `tags` is unused (record-only; the textures are base-game art, not mod tags).
"""
from collections import OrderedDict

from arz_patcher import TypedField, DATA_TYPE_INT, DATA_TYPE_STRING

MODULE_NAME = "Mastery skill-tree background restore (BitmapSingle -> BitmapUIAware)"

# Slot -> base-game mastery class (base InGameUI\Skills\<Class>SkillBackground01.tex).
# Dream (xpack mastery 9) uses Nature's backdrop in the base game (verified).
_MASTERY_CLASS = {
    1: "Warfare", 2: "Defense", 3: "Earth", 4: "Storm",
    5: "Stealth", 6: "Hunting", 7: "Spirit", 8: "Nature",
    9: "Nature",   # Dream
}

_UI_1_8 = "records\\ingameui\\player skills\\mastery %d\\"
_UI_DREAM = "records\\xpack\\ui\\skills\\mastery 9\\"

# (slot, record-basename, which background: 'base' or 'realloc')
def _targets():
    out = []
    for slot in range(1, 9):
        out.append((slot, _UI_1_8 % slot + "skillpanebasebitmap.dbr", "base"))
        out.append((slot, _UI_1_8 % slot + "skillpanereallocationbitmap.dbr", "realloc"))
    out.append((9, _UI_DREAM + "skillpanebasebitmap.dbr", "base"))
    out.append((9, _UI_DREAM + "skillpanereallocationbitmap.dbr", "realloc"))
    return out


def _bg_texture(cls, kind):
    """Return (keyboard_tex, controller_tex) for a mastery class + kind."""
    suffix = "SkillBackground01" if kind == "base" else "SkillReallocationBackground01"
    kb = r"InGameUI\Skills\%s%s.tex" % (cls, suffix)
    ct = r"InGameUI\Controller\Skills\%s%s.tex" % (cls, suffix)
    return kb, ct


def apply(db, tags):
    """Convert the 18 live mastery-pane background records to the base-game
    BitmapUIAware shape. Idempotent + fail-loud on any missing target."""
    print("\n=== mastery_bg_template: restore mastery skill-tree backgrounds ===")

    def _resolve(rec):
        if db.has_record(rec):
            return rec
        low = rec.lower().replace('/', '\\')
        for n in db.record_names():
            if n.lower().replace('/', '\\') == low:
                return n
        raise SystemExit(
            "mastery_bg_template: expected record missing: %s "
            "(upstream structure changed?)" % rec)

    converted = 0
    for slot, rec_path, kind in _targets():
        rec = _resolve(rec_path)
        # Decode (populates the field cache) so we can replace the whole field set.
        if db.get_fields(rec) is None:
            raise SystemExit("mastery_bg_template: %s has no fields" % rec)
        cls = _MASTERY_CLASS[slot]
        kb, ct = _bg_texture(cls, kind)
        # Rebuild the record to EXACTLY the base-game BitmapUIAware field set/order.
        new = OrderedDict()
        new["templateName"] = TypedField(
            DATA_TYPE_STRING, ["database\\Templates\\InGameUI\\BitmapUIAware.tpl"])
        new["FileDescription"] = TypedField(DATA_TYPE_STRING, ["BitmapUIAware"])
        new["bitmapNames"] = TypedField(DATA_TYPE_STRING, [kb, ct])
        new["bitmapPositionsX"] = TypedField(DATA_TYPE_INT, [0, 0])
        new["bitmapPositionsY"] = TypedField(DATA_TYPE_INT, [0, 0])
        db._decoded_cache[rec] = new
        db._modified.add(rec)
        converted += 1
        tag = "Dream" if slot == 9 else "m%d %s" % (slot, cls)
        print("  %-14s %-12s -> BitmapUIAware  %s" % (tag, kind, kb))

    print("=== mastery_bg_template done: %d background records -> BitmapUIAware "
          "(masteries 1-8 + Dream, base + reallocation) ===" % converted)
