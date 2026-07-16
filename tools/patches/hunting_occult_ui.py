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

ALIGNMENT + CONNECTORS (the "don't line up" / "wrong arrows" follow-up, DONE
build40-r2 for the two golden trees, re-derived to Will's 2026-07-14 TIER +
CONNECTOR laws + the texture-decoded connection map):
  Occult (5) - de-interleave the crossed trees Will reported 2026-07-13: reunite
    the orphaned Lay Trap pet-branch (Multishot Bolt Trap) into Lay Trap's column,
    move Open Wound out of the Darklings->Darkaperture span so Darklings' bar
    reaches its own modifier, drop 3 spurious base/leaf connectors, and flip Lethal
    Strike's mis-pointed [R] side-connector to straight (it reaches its own Mortal
    Wound). See _OCCULT_MOVES + _OCCULT_HUNTING_CONN below.
  Hunting (6) - move Take Down's connector from the Eviscerate modifier onto the
    Take Down base (vanilla pattern) so Take Down->Eviscerate reads instead of the
    spurious Eviscerate->Tempest arrow.
Every one of those field edits is a Will-authorized owner_approved_overrides entry
in tools/occult_hunting_golden.json (see its _WILL_VETO_2026_07_14 section); UI
button bitmapPosition + visual skillConnectionOn only, NO skill VALUE change. The
2 residual findings (a Lay-Trap tier-3 collision + a summon->pet-modifier detector
false-positive) are tracked in tools/mastery_ui_waivers.json. Standing UI-on-device
rule: these still need Will's in-game screenshot before promote.

Contract: patches-registry module - MODULE_NAME + apply(db, tags). Runs AFTER the
monolith (incl. fix_mastery_panel_buttons, which only rewrites panectrl button
LISTS - disjoint from these leaf records) and BEFORE the whole gate battery. The
reflow writes bitmapPositionX/Y on records disjoint from mastery_ui_audit's Earth
(mastery 3) reflow and mastery_ui_vet's non-golden moves, so the layout fixes
compose without a write-fight.
"""

import os
import sys

# tools/ is the parent of tools/patches/ - reach the shared connector model + node math
# (same source of truth as mastery_ui_vet + gate_mastery_ui).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mastery_conn_model as CM  # noqa: E402
import audit_mastery_ui as A  # noqa: E402

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

# ── Occult (mastery 5) tree reflow + connector fixes (Will's 2026-07-13 crossed-tree
# report, re-derived to the 2026-07-14 TIER + CONNECTOR laws + the texture-decoded
# connection map). The connector bar draws UP to the NEAREST occupied cell above
# (straight = same column; DRX `_right` = column to the right). Golden tree: every
# field below is a Will-authorized owner_approved_overrides entry in
# tools/occult_hunting_golden.json (see the WILL VETO section there). UI-only:
# button `bitmapPositionX/Y` + the visual `skillConnectionOn/Off`; NO skill VALUE change.
# (The connector textures are chosen by mastery_conn_model, not hard-coded here.)
_COLX = {1: 128, 2: 228, 3: 328, 4: 428, 5: 528, 6: 628}
_ROWY = {1: 403, 2: 341, 3: 279, 4: 217, 5: 155, 6: 93, 7: 31}

# (ui slot file, expected skillName basename, column 1-6, tier row 1-7).
_OCCULT_MOVES = (
    # reunite the orphaned Lay Trap pet-branch into Lay Trap's column 4 (was col1,
    # OFFCOL). Lay Trap + this mod are both tier3, so it sits at row4 (TIER-waived);
    # Lay Trap's straight bar reaches it (nearest above).
    ("skill18", "drxlaytrap_petmodifier_multishotbolttrap", 4, 4),
    # Open Wound OUT of the Darklings span (it interleaved Darklings->Darkaperture and
    # stole Darklings' arrow); col5 row4 is tier-correct (tier4) and span-free.
    ("skill07", "drxopenwound", 5, 4),
)

# (mastery, ui slot file, expected skillName basename, action) - action 'drop' clears
# skillConnectionOn (a base with no modifier, or a leaf mod, must not draw a bar);
# 'straight' sets the same-column bar (flip a mis-pointed [R] side-connector, or move
# a bar from a modifier onto its base so the pair reads as a genuine augment).
_OCCULT_HUNTING_CONN = (
    (5, "skill21", "drx_scrap", 'drop'),                        # standalone, no modifier
    (5, "skill26", "drxdarklings_darkaperture", 'drop'),        # leaf mod; Darklings' bar reaches it
    (5, "skill17", "drxlaytrap_rapidconstruction", 'drop'),     # leaf mod; spurious [R]
    (5, "skill19", "drxlethalstrike", 'straight'),             # [R]->straight; reaches Mortal Wound
    (6, "skill17", "drxtakedown", 'straight'),                 # base gets the bar (vanilla pattern)
    (6, "skill18", "drxtakedown_eviscerate", 'drop'),          # modifier drops the spurious up-bar
)


def _first(v):
    return v[0] if isinstance(v, list) else v


def _assert_skill(db, rec, ident, expect):
    sn = _first(db.get_field_value(rec, "skillName")) or ""
    base = sn.rsplit("\\", 1)[-1].lower()
    if base.endswith(".dbr"):
        base = base[:-4]
    if base != expect.lower():
        raise SystemExit(
            "hunting_occult_ui: %s holds %r, expected %s - the golden Occult/Hunting "
            "layout drifted; reconcile the reflow before shipping" % (ident, sn, expect))
    return sn


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

    # 5c - Occult (mastery 5) tree reflow: de-interleave the crossed trees + reunite
    # the Lay Trap orphan (Will 07-13, re-derived to the TIER + CONNECTOR laws).
    moved = 0
    for slot_file, expect, col, tier in _OCCULT_MOVES:
        rec = (_UI % 5) + slot_file + ".dbr"
        _require(rec, "bitmapPositionX")
        _require(rec, "bitmapPositionY")
        _assert_skill(db, rec, "Occult %s" % slot_file, expect)
        db.set_field(rec, "bitmapPositionX", _COLX[col], 0)   # dtype 0 = INT (match existing)
        db.set_field(rec, "bitmapPositionY", _ROWY[tier], 0)
        moved += 1
        print("  reflow Occult %-8s (%-42s) -> col%d row%d" % (slot_file, expect, col, tier))

    # 5d - geometry-correct connector rebuild on Occult (5) + Hunting (6). Writes BOTH
    #      skillConnectionOn AND skillConnectionOff, always length-matched, spanning each
    #      touched family from base to top (mastery_conn_model.rebuild_into). Round-1 vet
    #      HIGH fix: 'drop' clears BOTH arrays (no stale dimmed bar); a moved member or a
    #      'straight' skill reshapes its whole family bar (no single-element under-draw).
    for mastery, slot_file, expect, action in _OCCULT_HUNTING_CONN:   # fail-loud assert
        rec = (_UI % mastery) + slot_file + ".dbr"
        _require(rec, "skillName")
        sn = _assert_skill(db, rec, "m%d %s" % (mastery, slot_file), expect)
        if not db.has_record(sn):
            raise SystemExit("hunting_occult_ui: skill record missing for %s (%s)"
                             % (slot_file, sn))
    wrap = A.DB.from_db(db)
    conns = 0
    for slot in (5, 6):
        moved_seeds = [e.lower() for _sf, e, _c, _t in _OCCULT_MOVES] if slot == 5 else []
        seeds = [e.lower() for m, sf, e, a in _OCCULT_HUNTING_CONN if m == slot and a != 'drop']
        drops = [e.lower() for m, sf, e, a in _OCCULT_HUNTING_CONN if m == slot and a == 'drop']
        changed = CM.rebuild_into(wrap, slot, seed_skills=moved_seeds + seeds, drops=drops, log=print)
        conns += len(changed)

    print("=== H/O UI fix done: %d bg + %d shape + %d Occult-reflow + %d connector-array "
          "writes ===" % (bg_records, shapes, moved, conns))
