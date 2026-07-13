"""READ-ONLY dry-run proof for tools/patches/damage_display.py.

Replays the module against a COPY of the live baseline arz and asserts the fix
is minimal + correct:
  1. apply() touches ONLY records\\xpack\\game\\gameengine.dbr.
  2. Exactly the 7 intended style fields are ADDED (dtype STRING), every other
     field byte-identical, no record added/removed.
  3. verify() passes.
  4. apply() is idempotent (a second run adds nothing).

Usage: py tools/patches/_probe_damage_display.py [baseline.arz]
Default baseline = the session scratchpad build36a canonical arz (md5 63ca7cf8).
Exit 0 = PASS (prints PASS lines); any assertion aborts with a clear message.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))          # tools/
sys.path.insert(0, str(HERE.parent))              # tools/patches/
from arz_patcher import ArzDatabase                # noqa: E402
import damage_display as MOD                        # noqa: E402

DEFAULT_BASELINE = Path(
    r"C:\Users\willi\AppData\Local\Temp\claude\C--Users-willi-repos"
    r"\98075e9c-011f-4120-9b92-ce6ca35146b2\scratchpad\baseline_build36.arz")

GE = MOD.GAMEENGINE
EXPECT = set(MOD.STYLE_FIELDS)


def field_snapshot(db, rec):
    """key(str) -> (dtype, tuple(values)) for every field on a record."""
    out = {}
    for key, tf in db.get_fields(rec).items():
        out[key.split('###')[0]] = (tf.dtype, tuple(tf.values))
    return out


def main():
    baseline = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BASELINE
    if not baseline.exists():
        raise SystemExit("baseline arz not found: %s" % baseline)

    db = ArzDatabase.from_arz(baseline)
    names_before = set(db.record_names())
    ge_before = field_snapshot(db, GE)
    assert not (EXPECT & set(ge_before)), \
        "PRECONDITION FAIL: baseline already has some target fields: %s" % (
            EXPECT & set(ge_before))
    assert db._modified == set(), "PRECONDITION FAIL: fresh db._modified non-empty"

    # --- run the fix ---
    tags = {}
    MOD.apply(db, tags)

    # 1. only the gameengine record was modified
    assert db._modified == {GE}, \
        "MINIMALITY FAIL: modified set = %s (expected only %s)" % (db._modified, GE)
    print("PASS 1: apply() modified ONLY %s" % GE)

    # 2a. no record added / removed
    names_after = set(db.record_names())
    assert names_after == names_before, "FAIL: record set changed (added/removed records)"
    print("PASS 2a: record set unchanged (%d records)" % len(names_after))

    # 2b. exactly the 7 fields added, everything else byte-identical
    ge_after = field_snapshot(db, GE)
    added = set(ge_after) - set(ge_before)
    removed = set(ge_before) - set(ge_after)
    assert added == EXPECT, "FAIL: added fields %s != expected %s" % (added, EXPECT)
    assert not removed, "FAIL: fields removed: %s" % removed
    for k, v in ge_before.items():
        assert ge_after[k] == v, "FAIL: pre-existing field %s changed: %r -> %r" % (
            k, v, ge_after[k])
    print("PASS 2b: exactly %d fields added, all pre-existing fields byte-identical"
          % len(added))

    # 2c. added fields are STRING dtype (2) pointing at the intended FontStyles
    tags_unused = tags  # tags dict must be untouched (no Text tags for this fix)
    assert tags_unused == {}, "FAIL: module wrote Text tags (should write none): %s" % tags_unused
    for f in sorted(EXPECT):
        dtype, vals = ge_after[f]
        assert dtype == 2, "FAIL: %s dtype=%s (want 2/STRING)" % (f, dtype)
        assert list(vals) == [MOD.STYLE_FIELDS[f]], \
            "FAIL: %s value=%r (want %r)" % (f, vals, MOD.STYLE_FIELDS[f])
        print("        %-24s dtype=STRING  ->  %s" % (f, vals[0]))
    print("PASS 2c: all added fields STRING dtype, correct FontStyle targets, 0 Text tags")

    # 3. verify() passes on the fixed db
    MOD.verify(db, tags)
    print("PASS 3: verify() OK")

    # 4. idempotency
    db._modified = set()
    MOD.apply(db, tags)
    assert db._modified == set(), \
        "IDEMPOTENCY FAIL: second apply() re-modified: %s" % db._modified
    print("PASS 4: apply() idempotent (second run modified nothing)")

    print("\nALL CHECKS PASS - fix is minimal (1 record, +7 STRING fields, 0 records, 0 tags)")


if __name__ == '__main__':
    main()
