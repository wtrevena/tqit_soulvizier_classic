"""formula_names - B80 FORMULA NAME AUDIT (round 1).

Will's report (2026-07-16, verbatim): "Also Mythic Formula - Crystalline Mask
is the formula name for the formula which makes Galefury. the Mythic Formula
has the wrong name."

ROOT CAUSE (verified against the reference build, docs/reports/b80_formula_names.md
has the full evidence trail): `records\\drxitem\\supra\\recipes\\ar_hunter_helm_
formula.dbr` (the formula that crafts Galefury, `ar_hunter_helm.dbr`) has its
`description` field pointed at `tagRecipe_ar_caster_helm` - the SAME tag the
`ar_caster_helm_formula.dbr` pair (recipes\\ + zrecipes\\) legitimately uses for
the REAL Crystalline Mask formula ('^rMythic Formula - Cystalline Mask'; the SV-
authored spelling, not touched here). This predates the b66 wave entirely (b66
never added or touched ar_hunter_helm_formula.dbr) - it is inherited SV 0.98i/DRX
authoring debt, and SV 0.98i's OWN Text_EN.arc already ships the fix: a second,
correctly-worded, previously ORPHANED tag `tagRecipe_ar_helm_fix` = "^rMythic
Formula - Galefury" (byte-verified: `upstream/soulvizier_098i/Resources/
Text_EN.arc` xuniqueequipment.txt), sitting unused because no record's
`description` field was ever repointed to it.

FIX: repoint `ar_hunter_helm_formula.dbr`'s `description` field from the shared
donor tag to its own already-correct, already-shipped tag. Zero Text-pipeline
change needed (`tagRecipe_ar_helm_fix` flows into modstrings.txt automatically -
it is one of SV 0.98i's own xuniqueequipment.txt entries, not a mod-authored
tag). Per the standing preference (re-point over edit-a-shared-tag): the shared
`tagRecipe_ar_caster_helm` donor tag is left untouched (it is legitimately used
by BOTH ar_caster_helm_formula.dbr copies, recipes\\ + zrecipes\\, which craft
the real Crystalline Mask and must keep saying so).

GATE (verify(), runs post-finalization over the FINAL assembled db): every
`records\\drxitem\\supra\\*` ItemArtifactFormula's `description` tag, when
shared by 2+ formulas, must be shared ONLY by formulas that craft the SAME
`artifactName` (the recipes\\/zrecipes\\ twin pattern - legitimate). A shared
tag whose sharers craft DIFFERENT results is exactly this bug class (a donor
tag reused instead of a dedicated/correct one) and fails the build loud. This
is a pure db-field structural check (no Text.arc dependency, so it runs
reliably at DB-build verify() time) - scoped to `records\\drxitem\\supra\\`
(the DRX "supra"/uber-forge tier this bug class lives in) to avoid false
positives on unrelated base-game tag reuse (e.g. the base game's own tiered
lesser-experience-potion formulas legitimately share one generic tag across 12
different potion tiers; base-game `xtagFormulaDescription*` Arcane Formula
records outside `drxitem\\supra`). See docs/reports/b80_formula_names.md for the
full-catalog TEXT-based sweep (all 42 obtainable formulas' rendered names vs
their results') and the standalone `tools/validate_formula_names.py` gate that
runs it against the built Text.arc.

Negative test: tools/debug/negtest_formula_names.py.
"""

MODULE_NAME = "B80: formula name audit - Galefury mislabeled as Crystalline Mask"

_SUPRA_PREFIX = 'records\\drxitem\\supra\\'

_AR_HUNTER_HELM_FORMULA = r'records\drxitem\supra\recipes\ar_hunter_helm_formula.dbr'
_WRONG_TAG = 'tagRecipe_ar_caster_helm'    # the shared Crystalline Mask donor tag
_CORRECT_TAG = 'tagRecipe_ar_helm_fix'     # SV098i's own, already-correct, orphaned tag

# Waiver list for the verify() tag-sharing gate: (description tag) -> reason.
# A shared supra description tag is normally required to be shared ONLY by
# formulas crafting the identical artifactName (the recipes\/zrecipes\ twin
# pattern). Any FUTURE case where SV/design deliberately wants two DIFFERENT
# supra results to display the same recipe name would be waived here, with the
# reasoning documented - empty today (no such case exists in the current
# catalog; the one prior instance, ar_hunter_helm_formula, was the bug this
# module fixes, not a deliberate design choice - see docs/reports/
# b80_formula_names.md WILL-CONFIRM section, which is also empty: nothing else
# in the sweep needed a design call).
TAG_SHARING_WAIVERS = {}


def _get_field(db, rec, field):
    fields = db.get_fields(rec)
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == field:
            return tf.values[0] if tf.values else None
    return None


def apply(db, tags):
    print("\n=== Patch B80: formula name audit (Galefury) ===")
    if not db.has_record(_AR_HUNTER_HELM_FORMULA):
        raise SystemExit(
            f"B80 formula_names: expected record missing from db: "
            f"{_AR_HUNTER_HELM_FORMULA!r}")
    current = _get_field(db, _AR_HUNTER_HELM_FORMULA, 'description')
    if current == _CORRECT_TAG:
        print(f"  {_AR_HUNTER_HELM_FORMULA}: description already = "
              f"{_CORRECT_TAG!r} (idempotent no-op)")
        return
    if current != _WRONG_TAG:
        # Never blind-overwrite an unexpected value - only rewrite the exact
        # known-wrong string this module was written to repair.
        raise SystemExit(
            f"B80 formula_names: {_AR_HUNTER_HELM_FORMULA} description field "
            f"is {current!r}; expected the known-wrong {_WRONG_TAG!r} (or the "
            f"already-fixed {_CORRECT_TAG!r}). Refusing to overwrite an "
            f"unexpected value - update this module if the upstream state "
            f"legitimately changed.")
    db.set_field(_AR_HUNTER_HELM_FORMULA, 'description', _CORRECT_TAG)
    print(f"  {_AR_HUNTER_HELM_FORMULA}: description {_WRONG_TAG!r} -> "
          f"{_CORRECT_TAG!r}")
    print(f"  (tag already ships correctly in SV098i's own xuniqueequipment.txt: "
          f"{_CORRECT_TAG}='^rMythic Formula - Galefury' - was orphaned/unused "
          f"until this repoint; no Text-pipeline change needed)")


def _supra_formula_records(db):
    for rec in db.record_names():
        if not rec.replace('/', '\\').lower().startswith(_SUPRA_PREFIX.lower()):
            continue
        if _get_field(db, rec, 'Class') != 'ItemArtifactFormula':
            continue
        yield rec


def find_tag_sharing_offenders(db, waivers=None):
    """Return [(tag, [(record, artifactName), ...])] for every supra formula
    description tag shared by 2+ formulas whose artifactName values DIFFER,
    excluding any tag in `waivers`. Empty = gate PASS."""
    waivers = waivers if waivers is not None else TAG_SHARING_WAIVERS
    by_tag = {}
    for rec in _supra_formula_records(db):
        desc = _get_field(db, rec, 'description')
        artifact = _get_field(db, rec, 'artifactName')
        if desc:
            by_tag.setdefault(desc, []).append((rec, artifact))

    offenders = []
    for tag, entries in sorted(by_tag.items()):
        if len(entries) < 2 or tag in waivers:
            continue
        artifacts = {a for _r, a in entries}
        if len(artifacts) > 1:
            offenders.append((tag, entries))
    return offenders


def verify(db, tags):
    print("  [B80] supra formula-name tag-sharing gate ...")
    # Regression guard for the specific fix: the known-wrong value must be gone.
    current = _get_field(db, _AR_HUNTER_HELM_FORMULA, 'description')
    if current == _WRONG_TAG:
        raise SystemExit(
            f"B80 formula_names verify: {_AR_HUNTER_HELM_FORMULA} description "
            f"is still the wrong shared tag {_WRONG_TAG!r} (apply() should have "
            f"repointed it to {_CORRECT_TAG!r}) - fix did not stick.")

    offenders = find_tag_sharing_offenders(db)
    if offenders:
        for tag, entries in offenders:
            print(f"  FORMULA-NAME OFFENDER: description tag {tag!r} is shared "
                  f"by {len(entries)} formula(s) crafting "
                  f"{len({a for _r, a in entries})} DIFFERENT result(s):")
            for rec, artifact in entries:
                print(f"      {rec}  -> artifactName={artifact}")
        raise SystemExit(
            f"B80 formula_names verify FAILED: {len(offenders)} supra formula "
            f"description tag(s) shared across formulas crafting different "
            f"results (a donor tag reused instead of a dedicated/correct one - "
            f"exactly the Galefury/Crystalline-Mask bug class). See offenders "
            f"above; waive a genuinely SV-intended exception in "
            f"TAG_SHARING_WAIVERS with a documented reason.")
    print("  [B80] supra formula-name tag-sharing gate: PASS (no cross-result "
          "tag sharing)")
