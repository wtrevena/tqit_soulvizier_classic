"""B37 Hunting/Occult improvement wave (Will-approved 2026-07-12).

Patch-registry module. Contract: MODULE_NAME + apply(db, tags). Until the
patches registry (feat/patches-registry) lands, apply() is invoked directly
from apply_svc_patches.apply_all_extended_patches, right after the F5 Flash
Powder rework (the golden-waiver precedent this wave follows).

SCOPE (from docs/HUNTING_IMPROVEMENT_SUGGESTIONS.md + docs/OCCULT_IMPROVEMENT_
SUGGESTIONS.md, both checker-verified, and Will's verbatim approvals):

  H1  Rapid Construction: strip the copy-paste `defensiveConvert == skill
      CooldownTime` charm-resist penalty (S1). DB here; no tag.
  H2  The two skills both named "Eviscerate" (S2): drxtakedown_eviscerate (UI
      skill18, the CIRCLE-icon Takedown modifier per Will's shape law, isCircular=1)
      keeps "Eviscerate"; drxspear_tempest (UI skill22, the SQUARE-icon cast active
      per Will's shape law, isCircular=0) is renamed "Tempest". Both get the base
      descriptions they were missing. DB (skillDisplayName / skillBaseDescription
      repoint) here; the tag TEXT is authored in build_text_arc.py. The icon SHAPES
      are owned by the hunting_occult_ui module (the shape-law owner); this wave only
      renames + describes.
  H3  Descriptions: the two missing (H2) + the two inaccurate Hunting tooltips
      Scatter Shot (tagSkillDescription171) and Gouge (tagSkillDescription172),
      both cross-wired to a "Quillvine grove" in SV. TEXT in build_text_arc.py.
      (A full scan of every mastery-5/6 skill found NO other missing/blank/
      undefined description - only these.)
  H4  Hunting mastery: add a small mana ladder capping at 160 at ML40 (S4;
      Will: "small mana pool on the Hunting mastery, capping at 160"). No INT.
  H5  Darklings uplift (Occult S2; Will-approved): (a) raise the death-explosion
      blast damage, (b) count ladder reaching 4 at the top tier, (c) petrify-on-
      death duration scales up at high levels. The pet boom skills are NOT golden-
      tracked (verified: 0 hits in occult_hunting_golden.json) so (a)/(c) need no
      waiver; only drxdarklings.petLimit (b) is golden.
  H6  Tooltip synergies (Occult S5): Nether Strike works with Bow (the "^y(All
      Melee Weapons)" line hid it) - TEXT fix + teleport answer in the report.
      The "dagger flags" item is verified a NON-issue and left unchanged (see the
      _NOTE_DAGGER block below).

GOLDEN GATE: every Occult/Hunting record field/tag this wave changes gets an
`owner_approved_overrides` per-field waiver in tools/occult_hunting_golden.json
with justification "Will-authorized H/O improvement wave 2026-07-12" (the exact
drift keys are printed by validate_mastery_golden and added there). A mandatory
negative test proves the gate still fails loud on an un-waived mutation.

Every edit is fail-loud: the current value is asserted before it is changed, so
an upstream/build drift stops the build instead of silently mis-patching (same
discipline as _apply_flashpowder_rework)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arz_patcher import DATA_TYPE_STRING  # noqa: E402

MODULE_NAME = "hunting_occult_improvements"

# ── record paths ────────────────────────────────────────────────────────────
_RAPID = r'records\skills\hunting\drxmonsterlure_rapidconstruction.dbr'
_TEMPEST = r'records\skills\hunting\drxspear_tempest.dbr'           # SQUARE cast active (shape set by hunting_occult_ui)
_EVISCERATE = r'records\skills\hunting\drxtakedown_eviscerate.dbr'  # CIRCLE Takedown modifier (shape set by hunting_occult_ui)
_HUNT_MASTERY = r'records\skills\hunting\drxhuntingmastery.dbr'
_DARKLINGS = r'records\skills\stealth\drxdarklings.dbr'
_BOOM = r'records\skills\stealth\drxpet\drx_petskill_boom.dbr'
_BOOM_DISPLAY = r'records\skills\stealth\drxpet\drx_petskill_boom_display.dbr'

# ── new / repointed text tags (VALUES live in build_text_arc.OCCULT_FIX_TAGS) ─
_TEMPEST_NAME_TAG = 'tagSVCTempestNAME'
_TEMPEST_DESC_TAG = 'tagSVCTempestDESC'
_EVISCERATE_DESC_TAG = 'tagSVCEviscerateDESC'
_SHARED_EVISCERATE_TAG = 'tagSkillName090'   # stays on the SQUARE attack

# ── ladders ─────────────────────────────────────────────────────────────────
# H4: 4 mana/level, exactly 160 at ML40 (len 40, matches the other mastery bars).
_MANA_LADDER = [float(4 * i) for i in range(1, 41)]

# H5b: petLimit reaching 4 at the top tier (was ...,3,3,3,3,3,3,3 -> now 4 @ L16-20).
_PETLIMIT_LADDER = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 4, 4, 4, 4, 4]
_PETLIMIT_WAS = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3]

# H5a: the death-explosion burst (new physical) + boosted life-drain DoT (len 20).
_BOOM_PHYS_MIN = [40., 55., 70., 85., 100., 120., 140., 160., 180., 200.,
                  225., 250., 275., 300., 330., 360., 390., 430., 470., 520.]
_BOOM_PHYS_MAX = [70., 95., 120., 145., 170., 200., 230., 260., 290., 320.,
                  355., 390., 425., 460., 500., 540., 580., 635., 690., 760.]
_BOOM_SLOWLIFE = [30., 36., 42., 48., 54., 60., 66., 72., 80., 90.,
                  100., 112., 124., 136., 150., 164., 178., 215., 255., 310.]
_BOOM_SLOWLIFE_WAS = [19., 22., 25., 28., 31., 34., 37., 40., 43., 49.,
                      55., 60., 66., 72., 79., 84., 88., 112., 131., 166.]
# H5c: petrify duration scales at high levels (was flat 1.0). Low tiers ~1s, top 4s.
_BOOM_PETRIFY = [1.0, 1.0, 1.0, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6,
                 1.7, 1.9, 2.1, 2.3, 2.5, 2.7, 2.9, 3.2, 3.5, 4.0]


def _one(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if len(v) == 1 else v
    return v


def _need(db, rec, tag='H/O'):
    if not db.has_record(rec):
        raise SystemExit('B37 %s: missing record %s' % (tag, rec))


def _approx(a, b, eps=0.01):
    try:
        return abs(float(a) - float(b)) <= eps
    except (TypeError, ValueError):
        return False


# ── H1: Rapid Construction charm-resist artifact ────────────────────────────
def _fix_rapid_construction(db):
    """S1: defensiveConvert is a byte-identical copy of skillCooldownTime
    (both [-3.6..-19.8]); a negative defensiveConvert silently lowers the
    player's charm/conversion resistance (up to -19.8%) for investing in a
    cooldown modifier. Zero the array (encode-safe removal of the penalty);
    keep skillCooldownTime + skillManaCostReduction untouched. Pure cost-without-
    power removal (SV-inherited, cleared on the Nature tree already)."""
    _need(db, _RAPID, 'H1')
    dc = _one(db, _RAPID, 'defensiveConvert')
    cd = _one(db, _RAPID, 'skillCooldownTime')
    if not (isinstance(dc, list) and isinstance(cd, list) and dc == cd):
        raise SystemExit('B37 H1: drxmonsterlure_rapidconstruction defensiveConvert '
                         '(%r) is not the copy-paste of skillCooldownTime (%r) - '
                         'spec drift, refusing to guess' % (dc, cd))
    if not _approx(dc[-1], -19.8):
        raise SystemExit('B37 H1: unexpected defensiveConvert tail %r (want -19.8)' % dc[-1])
    db.set_field(_RAPID, 'defensiveConvert', [0.0] * len(dc))
    db._modified.add(_RAPID)
    print('  B37 H1: Rapid Construction defensiveConvert charm-resist penalty '
          '[-3.6..-19.8] -> zeroed (cooldown/mana untouched)')


# ── H2: the two "Eviscerate" nodes + their missing descriptions ─────────────
def _fix_eviscerate_dedup(db):
    """S2 + Will's square/circle detail (shapes owned by hunting_occult_ui, the shape-law
    owner). drxtakedown_eviscerate = the CIRCLE Takedown modifier (UI skill18 isCircular=1):
    keeps tagSkillName090 "Eviscerate", gains a real base description. drxspear_tempest = the
    SQUARE cast active (UI skill22 isCircular=0): renamed to "Tempest" (its own record name;
    its modifier one row up is already "Flayer"), gains a description that reads as the wide
    fear/confuse/slow control it is. Text-only intent; no mechanics."""
    S = DATA_TYPE_STRING
    _need(db, _TEMPEST, 'H2')
    _need(db, _EVISCERATE, 'H2')
    # both currently share tagSkillName090 and have NO skillBaseDescription
    for rec in (_TEMPEST, _EVISCERATE):
        dn = _one(db, rec, 'skillDisplayName')
        if dn != _SHARED_EVISCERATE_TAG:
            raise SystemExit('B37 H2: %s skillDisplayName=%r, expected %s (spec drift)'
                             % (rec, dn, _SHARED_EVISCERATE_TAG))
        bd = _one(db, rec, 'skillBaseDescription')
        if bd not in (None, '', 0, '0'):
            raise SystemExit('B37 H2: %s already has skillBaseDescription=%r '
                             '(spec drift)' % (rec, bd))
    # CIRCLE control spin -> "Tempest" + its description
    db.set_field(_TEMPEST, 'skillDisplayName', _TEMPEST_NAME_TAG, S)
    db.set_field(_TEMPEST, 'skillBaseDescription', _TEMPEST_DESC_TAG, S)
    db._modified.add(_TEMPEST)
    # SQUARE attack -> keep "Eviscerate" name, add its missing description
    db.set_field(_EVISCERATE, 'skillBaseDescription', _EVISCERATE_DESC_TAG, S)
    db._modified.add(_EVISCERATE)
    print('  B37 H2: drxspear_tempest (circle/buff-like) -> "Tempest" + desc; '
          'drxtakedown_eviscerate (square/attack) keeps "Eviscerate" + gains desc')


# ── H4: Hunting mastery mana ladder (cap 160) ───────────────────────────────
def _add_hunting_mana(db):
    """S4 (Will: "small mana pool on the Hunting mastery, capping at 160"). Add a
    40-entry characterMana ladder (4/level -> exactly 160 at ML40), well under
    Occult's 400, and add NO Intelligence (Hunting stays pure DEX/STR). The +100
    mastery HP that pays for 0-mana is deliberately LEFT intact per the doc."""
    _need(db, _HUNT_MASTERY, 'H4')
    cur = db.get_field_value(_HUNT_MASTERY, 'characterMana')
    curl = cur if isinstance(cur, list) else [cur]
    if not all(_approx(x, 0.0) for x in curl):
        raise SystemExit('B37 H4: drxhuntingmastery characterMana=%r, expected 0 '
                         '(spec drift)' % (cur,))
    intel = db.get_field_value(_HUNT_MASTERY, 'characterIntelligence')
    intell = intel if isinstance(intel, list) else [intel]
    if not all(_approx(x, 0.0) for x in intell):
        raise SystemExit('B37 H4: drxhuntingmastery characterIntelligence=%r, '
                         'expected 0 (must stay INT-free)' % (intel,))
    db.set_field(_HUNT_MASTERY, 'characterMana', list(_MANA_LADDER))
    db._modified.add(_HUNT_MASTERY)
    print('  B37 H4: Hunting mastery characterMana 0 -> ladder 4/level, cap %.0f '
          'at ML40 (no INT added; +100 mastery HP kept)' % _MANA_LADDER[-1])


# ── H5: Darklings uplift ─────────────────────────────────────────────────────
def _uplift_darklings(db):
    """Occult S2 (Will-approved). (a) raise the death-explosion blast damage
    (drx_petskill_boom, the real dyingSkill payload, which had only a life-drain
    DoT + no burst - add a physical burst + boost the DoT, and mirror it onto the
    display boom so the tooltip is honest); (b) petLimit reaches 4 at the top tier;
    (c) the petrify-on-death duration scales up at high tiers (was flat 1.0s ->
    up to 4.0s). Boom skills are not golden-tracked; only petLimit (drxdarklings)
    is golden. The chain-lightning synergy arcs the boom's damage, so raising the
    boom raises the chain automatically - no separate edit."""
    # (b) petLimit -> 4 at top (GOLDEN: waived)
    _need(db, _DARKLINGS, 'H5b')
    pl = db.get_field_value(_DARKLINGS, 'petLimit')
    if pl != _PETLIMIT_WAS:
        raise SystemExit('B37 H5b: drxdarklings petLimit=%r, expected %r (spec drift)'
                         % (pl, _PETLIMIT_WAS))
    db.set_field(_DARKLINGS, 'petLimit', list(_PETLIMIT_LADDER))
    db._modified.add(_DARKLINGS)

    # (a)+(c) the real death explosion + honest display mirror (NOT golden)
    _need(db, _BOOM, 'H5a')
    _need(db, _BOOM_DISPLAY, 'H5a')
    slow = db.get_field_value(_BOOM, 'offensiveSlowLifeMin')
    if slow != _BOOM_SLOWLIFE_WAS:
        raise SystemExit('B37 H5a: drx_petskill_boom offensiveSlowLifeMin=%r, '
                         'expected %r (spec drift)' % (slow, _BOOM_SLOWLIFE_WAS))
    pet = _one(db, _BOOM, 'offensivePetrifyMin')
    if not _approx(pet, 1.0):
        raise SystemExit('B37 H5c: drx_petskill_boom offensivePetrifyMin=%r, '
                         'expected 1.0 (spec drift)' % (pet,))
    for rec in (_BOOM, _BOOM_DISPLAY):
        db.set_field(rec, 'offensivePhysicalMin', list(_BOOM_PHYS_MIN))   # new burst
        db.set_field(rec, 'offensivePhysicalMax', list(_BOOM_PHYS_MAX))
        db.set_field(rec, 'offensiveSlowLifeMin', list(_BOOM_SLOWLIFE))   # boosted DoT
        db.set_field(rec, 'offensivePetrifyMin', list(_BOOM_PETRIFY))     # scaling petrify
        db._modified.add(rec)
    print('  B37 H5: Darklings - petLimit top %d->%d; death blast +physical '
          '%d-%d..%d-%d, life-drain +~1.6x, petrify 1.0s (flat) -> 1.0..4.0s by tier'
          % (_PETLIMIT_WAS[-1], _PETLIMIT_LADDER[-1], _BOOM_PHYS_MIN[0],
             _BOOM_PHYS_MAX[0], _BOOM_PHYS_MIN[-1], _BOOM_PHYS_MAX[-1]))


# ── H6: Nether Strike bow tooltip (TEXT in build_text_arc) + dagger note ────
# _NOTE_DAGGER: the doc's second "hidden synergy" (Calculated Strike / Blade Fury
# "dagger flags") is verified a NON-issue and intentionally NOT changed. Ground
# truth from the built arz: `Dagger=1` is set by ZERO skills mod-wide - TQAE has
# no separate Dagger skill weapon-requirement field; daggers satisfy the `Sword`
# flag, which BOTH drxcalculatedstrike (Sword/Axe/Spear) and its Blade Fury proc
# drxcalculatedstrike_luckyhit (Sword/Axe) already set. Their tooltips already
# read "^y(Sword/Dagger/Axe...)", so daggers already trigger them and the tooltip
# already advertises it - nothing is hidden and there is no flag to add. Nether
# Strike is the only genuinely hidden synergy (bow), fixed via TEXT. Full evidence
# is in the report; leaving accurate text unchanged avoids needless golden churn.


def apply(db, tags=None):
    """Registry entry point. Edits Occult/Hunting records in place. Text tags are
    authored in build_text_arc.OCCULT_FIX_TAGS (the golden-safe single-definition
    fix block); this function owns only the DB-side repoints/values."""
    print("\n=== B37: Hunting/Occult improvement wave (Will 2026-07-12) ===")
    _fix_rapid_construction(db)      # H1
    _fix_eviscerate_dedup(db)        # H2 (+ H3 missing descs)
    _add_hunting_mana(db)            # H4
    _uplift_darklings(db)            # H5
    # H3 inaccurate (Scatter Shot/Gouge) + H6 Nether Strike bow line are TEXT-only
    # (build_text_arc.OCCULT_FIX_TAGS); no DB edit here.
    print("=== B37 H/O wave: DB edits applied ===\n")
