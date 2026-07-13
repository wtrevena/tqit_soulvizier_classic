"""hunting_occult_ui - Hunting/Occult mastery-screen UI fix (build37, backlog #35/#76).

Will's report: "on the skill selection screen the background image on both hunting
and occult is missing and some of the skills on the screen are circles when they
should be squares, some of them don't line up properly, etc."

Fixes two PROVEN, high-severity UI defects (see the implementable spec
scratchpad/specs/hunting_occult_ui_fix_spec.md). All edits are UI-leaf field
edits on `records\\ingameui\\player skills\\mastery {N}\\...`; NO skill VALUES
change (the golden freeze stays intact - the 5 drifting button + 4 background
golden-tracked field edits on masteries 5/6 are Will-authorized
owner_approved_overrides in tools/occult_hunting_golden.json, mirroring the F5
Flash Powder precedent; the 3 passive buttons re-assert the golden-baseline circle
and therefore need no waiver).

DEFECT 1 - missing background (ROOT CAUSE #2 in the spec, PROVEN by D5).
  Our DRX BitmapSingle records for EVERY mastery point `bitmapName` at
  `SkillsPanel\\skillbackgrounddiablo.tex` (and ...reallocation...), a texture SV
  0.98i shipped that our mod's packaging never included - it resolves in NO arc,
  so the pane renders black. Our xpack3 panectrl overrides win DLC priority and
  shadow the base game's working per-mastery backdrops, so the bug is latently
  UNIVERSAL (all 8 masteries), and Will happened to scrutinise it on O/H.
  FIX (Will's mandate - REPOINT route, extended to ALL 8 masteries): repoint each
  mastery's base + reallocation `bitmapName` to its own base-game backdrop
  `InGameUI\\Skills\\<Class>SkillBackground01.tex` / `...ReallocationBackground01`.
  All 16 target textures are D5-confirmed present in the base game's InGameUI.arc
  (loaded at runtime for every Custom Quest). Our slot->class order is the base
  game's own (1 Warfare, 2 Defense, 3 Earth, 4 Storm, 5 Stealth/Occult, 6 Hunting,
  7 Spirit, 8 Nature), so each slot gets its authoritative backdrop. Only masteries
  5/6 are golden-tracked (4 waived keys); 1-4,7,8 clear the identical latent bug
  with no waiver.

DEFECT 2 - button shapes per Will's SHAPE LAW (2026-07-12, verbatim): "circles
  are for passive buffs in the skill tree or passive abilities like % chance to
  activate or an extension / enhancement to a lower level skill; a square is an
  ability you have to CAST." So cast actives => SQUARE, passives / procs /
  modifiers => CIRCLE. This wave sets 8 O/H buttons; 5 drift from the golden
  baseline and are Will-authorized (waived): 2 cast actives squared
  (drxpoisongasbomb, drxspear_tempest - Will's explicit Tempest-is-a-square call)
  and 3 modifiers circled (drxcalculatedstrike_luckyhit,
  drxlaytrap_petmodifier_multishotbolttrap, drxtakedown_eviscerate). The other 3
  are STANDALONE PASSIVES (drx_dual_blade, drxherbalism, drxcorneredrage): an
  earlier wave squared them by base-game precedent, but under Will's law passives
  are CIRCLES, so this wave RE-ASSERTS their circle preset. That preset is
  IDENTICAL to the golden baseline, so the 3 passives produce ZERO drift and carry
  NO waiver (their now-vacuous waivers were removed from the golden). Each fix
  writes isCircular AND the 3 matching border bitmaps (square => SkillButtonBorder01
  family; circle => SkillButtonBorderRound01 family). All 6 textures D5-confirmed.

ALIGNMENT ("don't line up") is deliberately NOT touched this wave: every O/H
button is grid-valid + collision-free, and the perceived misalignment is chiefly
downstream of the shape bug (a main node wrongly drawn as an undersized circle).
Per Will's mandate, residual nudges wait for an in-game screenshot pass after he
tests; each would be a `bitmapPositionX/Y` edit + its own golden waiver.

Contract: patches-registry module - MODULE_NAME + apply(db, tags). Runs AFTER the
monolith (incl. fix_mastery_panel_buttons, which only rewrites panectrl button
LISTS - disjoint from these leaf records) and BEFORE the whole gate battery.
"""

# Contract field 1 - human label (build logs + collision gate).
MODULE_NAME = "Hunting/Occult mastery-screen UI fix (backgrounds + button shapes)"

# UI-record directory per mastery slot (lowercase, backslash convention - matches
# how ArzDatabase.record_names() stores these and how the A7 golden gate keys them).
_UI = "records\\ingameui\\player skills\\mastery %d\\"

# 5a - per-mastery-slot class name for the background repoint. Slot->class is the
# base game's own order (verified against the base database.arz + our built arz);
# each <Class>SkillBackground01.tex / <Class>SkillReallocationBackground01.tex is
# D5-confirmed present in base InGameUI.arc.
_MASTERY_CLASS = {
    1: "Warfare", 2: "Defense", 3: "Earth", 4: "Storm",
    5: "Stealth", 6: "Hunting", 7: "Spirit", 8: "Nature",
}

# 5b - shape presets. isCircular drives the frame; the 3 border bitmaps are kept
# internally consistent with it (base-game convention, D5-confirmed textures).
_SQUARE = (
    ("isCircular", 0),
    ("bitmapNameUp", r"InGameUI\SkillButtonBorder01.tex"),
    ("bitmapNameDown", r"InGameUI\SkillButtonBorderDown01.tex"),
    ("bitmapNameInFocus", r"InGameUI\SkillButtonBorderOver01.tex"),
)
_CIRCLE = (
    ("isCircular", 1),
    ("bitmapNameUp", r"InGameUI\SkillButtonBorderRound01.tex"),
    ("bitmapNameDown", r"InGameUI\SkillButtonBorderRoundDown01.tex"),
    ("bitmapNameInFocus", r"InGameUI\SkillButtonBorderRoundOver01.tex"),
)

# The 8 O/H buttons, set per Will's SHAPE LAW (cast active => SQUARE; passive /
# proc / modifier => CIRCLE). (slot, button, preset, skill identity for logs).
# 2 SQUARE = cast actives (drxpoisongasbomb, drxspear_tempest - Will's explicit
# Tempest-is-a-square call); 6 CIRCLE = 3 modifiers (luckyhit, multishotbolttrap,
# takedown_eviscerate) + 3 standalone passives (drx_dual_blade, drxherbalism,
# drxcorneredrage). The 3 passives' CIRCLE preset is IDENTICAL to the golden
# baseline, so they produce ZERO drift and carry NO waiver (an earlier wave
# squared them by base-game precedent; Will's law reverts them to circle). The
# other 5 buttons drift from the golden and are Will-waived. m6 skill18
# (drxtakedown_eviscerate) pairs with the H/O improvements wave's Eviscerate
# RENAME: the renamed buff becomes correctly circular.
_SHAPE_FIXES = (
    (5, "skill13", _SQUARE, "drxpoisongasbomb"),                        # cast active (owns _shrapnel) -> SQUARE
    (5, "skill24", _CIRCLE, "drx_dual_blade"),                          # Skill_Passive -> CIRCLE (Will shape law; == golden baseline)
    (5, "skill06", _CIRCLE, "drxcalculatedstrike_luckyhit"),           # modifier of CalculatedStrike -> CIRCLE
    (5, "skill18", _CIRCLE, "drxlaytrap_petmodifier_multishotbolttrap"),  # pet-modifier of LayTrap -> CIRCLE
    (6, "skill09", _CIRCLE, "drxherbalism"),                           # Skill_Passive -> CIRCLE (Will shape law; == golden baseline)
    (6, "skill22", _SQUARE, "drxspear_tempest"),                       # cast active (owns tempest_expose) -> SQUARE (Will's explicit call)
    (6, "skill23", _CIRCLE, "drxcorneredrage"),                        # PassiveOnLifeBuffSelf -> CIRCLE (Will shape law; == golden baseline)
    (6, "skill18", _CIRCLE, "drxtakedown_eviscerate"),                # modifier of Takedown -> CIRCLE
)


def apply(db, tags):
    """Repoint all 8 mastery backgrounds + correct the 8 O/H button shapes.

    Fail-loud: if any target record or field is unexpectedly absent (an upstream
    structural change), abort the build with a clear message rather than silently
    no-op'ing the fix. `tags` is unused (this fix is record-only; no Text tags).
    """
    print("\n=== H/O UI fix: 8-mastery backgrounds + 8 O/H button shapes ===")

    def _require(rec, field):
        if not db.has_record(rec):
            raise SystemExit(
                "hunting_occult_ui: expected UI record missing: %s "
                "(upstream structure changed?)" % rec)
        if db.get_field_value(rec, field) is None:
            raise SystemExit(
                "hunting_occult_ui: record %s lacks expected field %s" % (rec, field))

    # 5a - background repoint (base + reallocation), all 8 masteries.
    bg_records = 0
    for slot in range(1, 9):
        cls = _MASTERY_CLASS[slot]
        base_rec = (_UI % slot) + "skillpanebasebitmap.dbr"
        real_rec = (_UI % slot) + "skillpanereallocationbitmap.dbr"
        base_tex = r"InGameUI\Skills\%sSkillBackground01.tex" % cls
        real_tex = r"InGameUI\Skills\%sSkillReallocationBackground01.tex" % cls
        _require(base_rec, "bitmapName")
        _require(real_rec, "bitmapName")
        db.set_field(base_rec, "bitmapName", base_tex)
        db.set_field(real_rec, "bitmapName", real_tex)
        bg_records += 2
        waived = " [golden-waived]" if slot in (5, 6) else ""
        print("  m%d %-8s background -> %s%s" % (slot, cls, base_tex, waived))
    print("  backgrounds repointed: %d records (masteries 1-8, base + realloc)"
          % bg_records)

    # 5b - button shapes: flip isCircular + swap the 3 border bitmaps to match.
    shapes = 0
    for slot, base, preset, ident in _SHAPE_FIXES:
        rec = (_UI % slot) + base + ".dbr"
        for field, _val in preset:
            _require(rec, field)
        for field, val in preset:
            db.set_field(rec, field, val)
        shape = "CIRCLE" if preset is _CIRCLE else "SQUARE"
        shapes += 1
        print("  m%d %-8s (%s) -> %s" % (slot, base, ident, shape))
    print("  button shapes set: %d (2 SQUARE cast-actives + 6 CIRCLE passives/procs/"
          "modifiers, Will's shape law); 5 drift-waived, 3 re-assert baseline circle"
          % shapes)
    print("=== H/O UI fix done: %d bg + %d shape records ==="
          % (bg_records, shapes))
