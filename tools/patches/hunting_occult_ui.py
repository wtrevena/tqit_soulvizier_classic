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

ALIGNMENT - OCCULT TREE REFLOW (build40, Will 2026-07-13). The deferred "don't
line up" follow-up above is now DONE for Occult (mastery 5). Will's report
(verbatim intent): the connector ARROWS still read wrong in some Occult skills
"because there is not enough horizontal space"; specifically in the THIRD column
(x=328) the bottom/middle/top skills read as one tree while the 2nd and 4th read
as a separate tree, so the dependency lines cross/confuse. He asked to MOVE the
offending skills to spread them out so the arrows read correctly.

  ROOT CAUSE (proven vs the LIVE build38a arz; full evidence in
  docs/reports/b40_occult_tree_rca.md): the skill panel is a FIXED 6-column
  (x=128,228,328,428,528,628) x 7-row (y=31,93,155,217,279,341,403) grid on ALL
  eight masteries - NO mastery uses x>628, so a literal "7th column on the right"
  is off-panel and impossible. A column reads as a clean tree ONLY when each
  dependency chain occupies a CONTIGUOUS vertical run (base at the bottom, higher
  y; upgrades stacking up) with UNRELATED chains separated by an empty row - the
  exact structure of the Will-accepted-clean column 6 (disarmtraps+dual_blade pair
  / empty row / throwingknife+flurry pair). Two Occult columns violate this:
    * col3 (x=328) INTERLEAVES three independent trees at alternating rows -
      Darklings (darklings->darkaperture) at rows 2&4, Open Wound (openwound->
      anatomy) at rows 3&5, plus standalone Blade Honing at row 1 - so the
      darklings arrow (2->4) and the openwound arrow (3->5) overlap and cross.
      This is Will's exact "2&4 vs 1-3-5" report.
    * col1 (x=128) has the same class of defect: the Flash Powder chain
      (flashpowder->poisongasbomb->shrapnel) is interleaved with standalone Scrap
      and with an ORPHANED Lay Trap pet-branch (multishotbolttrap) whose parent
      Lay Trap lives in col4 - so Scrap's straight up-connector currently points
      at the unrelated poisongasbomb and the trap sits divorced from its tree.

  FIX (position-only reflow; each moved skill is a bitmapPositionX/Y edit + its own
  golden waiver in tools/occult_hunting_golden.json - NO skill VALUE/effect/dep
  semantics touched, only the visual grid slot). De-interleave into contiguous,
  non-crossing runs, mirroring the proven col6 structure, and reunite the orphan:
    * col1 -> Flash Powder chain contiguous (flashpowder y403 base, poisongasbomb
      y279, shrapnel y155) + standalone Scrap isolated at the top (y31, empty row
      y93 below it); multishotbolttrap LEAVES col1 for col4.
    * col3 -> two clean base+child pairs like col6: Darklings (y403) + darkaperture
      (y341); empty divider row y279; Open Wound (y217, UNMOVED) + anatomy (y93,
      UNMOVED); standalone Blade Honing relocated to the top (y31). Open Wound and
      anatomy keep their exact cells, so only 3 col3 skills move.
    * col4 -> multishotbolttrap reunited into the Lay Trap column at the bottom
      (x428 y403), isolated by the empty row y341 below Lay Trap (y279); the Lay
      Trap main chain (laytrap/rapidconstruction/summon/greaterpower) is UNMOVED.
  Columns 2 (Envenom), 5 (Calculated Strike) and 6 (Disarm/Throwing Knife) already
  read clean (Will did not flag them) and are left byte-for-byte untouched -> zero
  drift, minimal risk. 8 skill buttons move (9 waiver keys: 7 y-only, multishot
  x+y). Consistent with the Earth col-428 reflow approach in mastery_ui_audit
  (UI-button records only; base is lower/high-y, modifiers stack up).

Contract: patches-registry module - MODULE_NAME + apply(db, tags). Runs AFTER the
monolith (incl. fix_mastery_panel_buttons, which only rewrites panectrl button
LISTS - disjoint from these leaf records) and BEFORE the whole gate battery. The
Occult reflow writes bitmapPositionX/Y on records disjoint from mastery_ui_audit's
Earth (mastery 3) reflow, so the two layout fixes compose without a write-fight.
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

# Occult (mastery 5) tree reflow (build40, Will 2026-07-13) - de-interleave the
# crossed connector trees in columns 1 & 3 and reunite the Lay Trap orphan. Each
# tuple = (slot file, expected skillName basename, new x, new y). We ASSERT the
# slot still holds the expected skill before moving it (fail-loud if the Occult
# layout drifted upstream). UI-button position ONLY; no skill VALUE changes. Every
# target cell is on-panel (x in the base 128..628 set, y in 31..403) and, together
# with the UNMOVED skills (openwound skill07 @328,217; anatomy skill08 @328,93; the
# Lay Trap main chain in col4; all of cols 2/5/6), collision-free. Slot->skill map
# verified against the build38a arz.
_OCCULT_REFLOW = (
    # col1 (x=128): Flash Powder chain contiguous + Scrap isolated at top.
    ("skill12", "drxflashpowder",                              128, 403),  # base   (was 128,341)
    ("skill13", "drxpoisongasbomb",                            128, 279),  # ->     (was 128,155)
    ("skill14", "drxpoisongasbomb_shrapnel",                   128, 155),  # ->     (was 128,31)
    ("skill21", "drx_scrap",                                   128,  31),  # lone   (was 128,217)
    # reunite the Lay Trap pet-branch into col4 (x=428), isolated at the bottom.
    ("skill18", "drxlaytrap_petmodifier_multishotbolttrap",    428, 403),  # (was 128,279 - orphaned in Flash Powder's col)
    # col3 (x=328): two clean base+child pairs (col6 pattern) + Blade Honing to top.
    ("skill25", "drxdarklings",                                328, 403),  # base   (was 328,279)
    ("skill26", "drxdarklings_darkaperture",                   328, 341),  # branch (was 328,155)
    ("skill09", "drxbladehoning",                              328,  31),  # lone   (was 328,341)
    # NOTE: openwound (skill07 @328,217) and anatomy (skill08 @328,93) are the
    # SECOND col3 pair and keep their exact cells (unmoved -> no drift).
)


def _first(v):
    return v[0] if isinstance(v, list) else v


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

    # 5c - Occult (mastery 5) tree reflow: de-interleave the crossed connector
    # trees in cols 1 & 3 and reunite the Lay Trap orphan (build40, Will 07-13).
    # UI-button positions only; fail-loud if a slot drifted from its expected skill.
    moved = 0
    for slot_file, expect, x, y in _OCCULT_REFLOW:
        rec = (_UI % 5) + slot_file + ".dbr"
        _require(rec, "bitmapPositionX")
        _require(rec, "bitmapPositionY")
        sn = _first(db.get_field_value(rec, "skillName")) or ""
        base = sn.rsplit("\\", 1)[-1].lower()
        if base.endswith(".dbr"):
            base = base[:-4]
        if base != expect.lower():
            raise SystemExit(
                "hunting_occult_ui: Occult %s holds %r, expected %s - layout "
                "drifted; reconcile the reflow before shipping" % (slot_file, sn, expect))
        db.set_field(rec, "bitmapPositionX", x, 0)   # dtype 0 = INT (match existing)
        db.set_field(rec, "bitmapPositionY", y, 0)
        moved += 1
        print("  reflow Occult %-8s (%-42s) -> (%d,%d)" % (slot_file, expect, x, y))
    print("  Occult tree reflow: %d buttons moved (cols 1 & 3 de-interleaved, Lay "
          "Trap orphan reunited to col4); cols 2/5/6 untouched" % moved)

    print("=== H/O UI fix done: %d bg + %d shape + %d Occult-reflow records ==="
          % (bg_records, shapes, moved))
