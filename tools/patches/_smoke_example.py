"""_smoke_example - the patches-registry MODULE TEMPLATE (copy me).

This is the reference/no-op module that documents the contract every
patches-registry content module must satisfy. It is INTENTIONALLY NOT listed in
tools/patches/__init__.py REGISTRY - it stays a template. To create a real
content module:

    1. Copy this file to tools/patches/<your_module>.py
    2. Set MODULE_NAME to a short human label.
    3. Put your record/tag authoring in apply(db, tags).
    4. Append '<your_module>' to REGISTRY in tools/patches/__init__.py (your
       own branch; content waves own disjoint modules and one REGISTRY line).
    5. Run:  py tools/patches/_check_registry.py     (cheap contract check)

THE CONTRACT (enforced fail-loud by tools/patches/__init__.py:_load_module):

    MODULE_NAME : str          # non-empty; shown in build logs + collision gate
    def apply(db, tags): ...   # required callable; mutates db + tags IN PLACE

`db`   is arz_patcher.ArzDatabase - the SAME in-memory DB the monolith
       (apply_svc_patches.apply_all_extended_patches) just finished authoring.
       Read/write records with the monolith's own idioms:
           from apply_svc_patches import _ensure_record
           _ensure_record(db, path, template)        # create a bare record
           db.set_field(path, 'fieldName', value)    # int/float/str/bool or list
           db.get_field_value(path, 'fieldName')
           db.clone_record(src, dest)                # copy a record
           db.has_record(path) / db.record_names()
       Every write marks db._modified (directly or via set_field/clone_record),
       which the collision gate and write_arz key off. Do NOT reassign
       db._modified.

`tags` is a plain dict[str, str] of Text tags (tagKey -> displayed text). Add
       yours with `tags['tagSVCMyThing'] = 'My Thing'`. build_text_arc.py turns
       these into Text.arc; a tag your records reference but never add here will
       be caught by the build's text-tag invariant.

GUARANTEES you can rely on:
  * Your apply() runs AFTER all monolith content and AFTER earlier REGISTRY
    modules, and BEFORE the whole gate battery (apply_svc_patches.
    run_registry_gates) - so every monolith invariant (soul-leak, soul-augment,
    itemskill-activation, pet parity/gear/skill-kit, boss-kit clone-shape,
    spawn-eligibility, MP-equation, portal-openness, render-chain, golden,
    B-SUMMON-1, ...) validates YOUR records too. Write clean content and the
    gates will confirm it; write broken content and the build fails loud.
  * Later modules that write a record you also wrote WIN, but the build logs a
    loud COLLISION warning naming both modules. Keep modules disjoint.

Determinism: do not depend on wall-clock/random/hash-ordered iteration; the
build pins PYTHONHASHSEED=0 for reproducible .arz bytes. Sort any set you
iterate when the order affects what you write.
"""

# Contract field 1: a non-empty human label (shown in logs + the collision gate).
MODULE_NAME = "smoke example (no-op template)"


def apply(db, tags):
    """Contract field 2: the entry point. A REAL module mutates db + tags here.

    This template is a strict no-op: it must not change a single record or tag,
    so that even if it is (accidentally) registered, the build stays byte-
    identical. The asserts below prove it received the real objects.
    """
    # Trivial self-checks that the harness handed us the real db/tags objects.
    assert hasattr(db, "record_names") and hasattr(db, "set_field"), \
        "_smoke_example.apply: db is not an ArzDatabase"
    assert hasattr(db, "_modified"), \
        "_smoke_example.apply: db is missing the _modified tracker"
    assert isinstance(tags, dict), \
        "_smoke_example.apply: tags is not a dict"

    # A real module would do work here, e.g.:
    #     from apply_svc_patches import _ensure_record
    #     path = r"records\item\svc\example.dbr"
    #     _ensure_record(db, path, "database\\Templates\\Jewelry_Ring.tpl")
    #     db.set_field(path, "itemNameTag", "tagSVCExample")
    #     tags["tagSVCExample"] = "Example"
    #
    # This template deliberately does nothing (no db/tags mutation), so it is a
    # provable no-op template rather than shippable content.
    return
