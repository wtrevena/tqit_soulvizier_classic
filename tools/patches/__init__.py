"""patches-registry: an ordered, multi-file content-module manifest for the
SoulvizierClassic DB build (build37 bootstrap).

WHY THIS EXISTS
---------------
`tools/apply_svc_patches.py` is a ~16k-line monolith. To let content waves own
DISJOINT modules and run in parallel, new content is being moved OUT of the
monolith into small sibling modules under this package. Round 1 (this bootstrap)
adds the seam and the coherency machinery; REGISTRY ships EMPTY so the build is
byte-identical to the pre-registry build (the identity proof, README S5).

THE MODULE CONTRACT (what content waves code against - see README.md)
---------------------------------------------------------------------
Every entry in REGISTRY is the base-name of a file `tools/patches/<name>.py`
that defines exactly:

    MODULE_NAME = "<human label>"          # non-empty str, for logs/gates
    def apply(db, tags):                    # required callable
        # mutate `db` (arz_patcher.ArzDatabase) and `tags` (dict) IN PLACE.
        ...

`db` and `tags` are the SAME objects the monolith uses: `db` is the in-memory
ArzDatabase that apply_all_extended_patches() just finished authoring; `tags`
is the dict apply_all_extended_patches() returned (build_text_arc later turns
it into Text.arc). A module adds/edits records via the same idioms the monolith
uses (`from apply_svc_patches import _ensure_record, ...`; `db.set_field(...)`;
`db.clone_record(...)`) and adds Text tags via `tags['tagKey'] = 'value'`.

EXECUTION ORDER (the load-bearing coherency requirement)
--------------------------------------------------------
build_svc_database.py runs, in this exact order:
    1. apply_all_extended_patches(db, ..., _defer_gates=True)   # monolith content
    2. run_registry(db, tags)                                   # THESE modules' apply(), in order
    3. apply_svc_patches.run_registry_gates(db, tags, ...)      # the whole gate battery
    4. run_registry_verifies(db, tags)                          # THESE modules' verify(), in order
So the monolith's entire fail-loud gate battery now runs over the FINAL
assembled db (monolith + every module). Nothing a module does escapes the gates.

A module's OPTIONAL verify(db, tags) hook (step 4) runs AFTER the gate battery's
FINALIZATION (the Ground Smash de-filler, the wave29 placeholder-tag renames, the
soul-naming standard, the MP-equation fix). So a roster/diversity check a module
MUST run over the FINAL assembled db belongs in verify(), NEVER in apply(): an
apply()-time gate (step 2) runs mid-registry, before step 3 clears the ordering
artifacts (cyclops de-filler; satyrmagi/satyrspiritcaller placeholder-tag rename),
and would fail loud on those transient artifacts - the build37 skill_quality
blocker. Modules with no verify() are simply skipped in step 4.

Public API: REGISTRY, run_registry(db, tags), run_registry_verifies(db, tags),
run_registry_gates lives in apply_svc_patches, registry_order_hash(names),
selfcheck().
"""
import hashlib
import importlib

# ── THE MANIFEST ────────────────────────────────────────────────────────────
# Ordered list of module base-names -> files tools/patches/<name>.py.
#
# ORDER MATTERS: modules run top-to-bottom. If two modules write the SAME
# record, the LATER one wins (legal registry semantics) but run_registry emits
# a loud COLLISION warning naming both (never silent).
#
# KEEP THIS EMPTY on `main` until content waves land their modules. An empty
# REGISTRY makes the whole build byte-identical to the pre-registry build
# (README S5 identity proof). Content waves append their own single line here
# (e.g. 'four_generals', 'toxeus_suite') in their own branch.
#
# NOTE: _smoke_example is the template/reference module. It is intentionally
# NOT registered (it stays a copy-me template); see README S6.
# ORDERING NOTE (four_generals, build37 merge UNION resolution): four_generals
# enriches the three EXISTING general souls (soul\machae\{dysnomion,makaria,
# trophonios}) with a light amgoz downside. skill_quality may also touch those
# souls, so four_generals MUST run BEFORE skill_quality: the S4b collision then
# resolves later-wins in the intended direction (skill_quality's skill-grant edits
# win; the four_generals downside sits on a defensive stat neither fully touches).
# 'visuals' stays LAST (DB precondition invariant, writes nothing).
REGISTRY = [
    'hunting_occult_ui',    # build37 backlog #35/#76: O/H mastery-screen UI (shapes/bitmaps)
    'mastery_ui_audit',     # build38: cross-mastery skill-tree UI fix (graft icons, Earth
                            # Rupture de-dup + reflow, Dream bg); disjoint from hunting_occult_ui
                            # (which owns mastery 1-8 backgrounds + O/H button shapes)
    'four_generals',        # build37: Hades' Generals upgrade (3 general souls); keep ahead of skill_quality
    'skill_quality',        # build37 backlog #31: granted-skill quality pass
    'toxeus_suite',         # build37 backlog #32: Toxeus Encounter Suite
    'diadochi',             # build37: the Helepolis, Taker of Cities (Fields of the Diadochi uber)
    'polis_vault',          # build37: Polis Daemonai Warden's Vault-Cage
    'neferkha',             # build37: Neferkha, the Rimebound Pharaoh (Cold Tombs Tier-1)
    'hunting_occult_improvements',  # build37: Will-approved H/O skill edits; runs late (was the
                                    # finalization-phase interim call) so it wins any collision
    'visuals',              # build37: DB precondition invariant (writes nothing) - keep LAST
]


def registry_order_hash(names):
    """Stable content+ORDER hash of a manifest (S4a). Logged and asserted so a
    silent reordering or duplication of REGISTRY is caught at build time."""
    h = hashlib.sha256()
    for n in names:
        h.update(n.encode('utf-8'))
        h.update(b'\x00')
    return h.hexdigest()


class _TrackingModifiedSet(set):
    """Drop-in replacement for ArzDatabase._modified used ONLY while registry
    modules run.

    Why not a plain before/after set delta? `_modified` is a monotonic set:
    once module A adds record X, module B re-writing X is a set no-op, so a
    naive `after - before` for B would MISS the collision. This subclass logs
    EVERY `.add(name)` call against the currently-active module, so the
    collision gate (S4b) sees re-modifications. Only `.add` is instrumented;
    every other set operation (discard/remove/__contains__/iter) keeps stock
    set semantics, so downstream code (write_arz's `name in _modified`) is
    unaffected. After the registry runs, db._modified is restored to a plain
    set with identical membership.
    """

    def __init__(self, iterable=()):
        super().__init__(iterable)
        self._touch_log = []          # list[(module_name, record_name)]
        self._active_module = None    # set by run_registry around each apply()

    def add(self, item):
        if self._active_module is not None:
            self._touch_log.append((self._active_module, item))
        super().add(item)


def _load_module(name):
    """Import tools/patches/<name>.py and validate the module contract.
    Fail-loud (SystemExit) on any violation - a malformed module never ships."""
    try:
        mod = importlib.import_module('%s.%s' % (__name__, name))
    except Exception as e:
        raise SystemExit(
            "patches-registry: REGISTRY entry '%s' failed to import "
            "(tools/patches/%s.py): %r" % (name, name, e))
    module_name = getattr(mod, 'MODULE_NAME', None)
    apply_fn = getattr(mod, 'apply', None)
    if not isinstance(module_name, str) or not module_name.strip():
        raise SystemExit(
            "patches-registry: module '%s' must define a non-empty MODULE_NAME "
            "str (contract violation)" % name)
    if not callable(apply_fn):
        raise SystemExit(
            "patches-registry: module '%s' must define a callable "
            "apply(db, tags) (contract violation)" % name)
    return mod, module_name, apply_fn


def _collisions(per_module):
    """Given {module_name: set(items)} return {item: [modules...]} for every
    item claimed by 2+ modules, sorted for stable output."""
    owners = {}
    for module_name, items in per_module.items():
        for it in items:
            owners.setdefault(it, []).append(module_name)
    return {it: ms for it, ms in owners.items() if len(ms) >= 2}


def _warn_collisions(kind, per_module):
    coll = _collisions(per_module)
    if not coll:
        print("  collision gate (%s): none written by 2+ modules (clean)" % kind)
        return
    print("  WARNING collision gate (%s): %d %s written by 2+ modules "
          "(LATER module wins - legal registry semantics - but is never "
          "silent):" % (kind, len(coll), kind))
    for it in sorted(coll):
        print("    %s  <-  %s" % (it, ', '.join(coll[it])))


def run_registry(db, tags, registry=None):
    """Run every REGISTRY module in manifest order over the shared db/tags,
    then the fail-loud coherency gates. Returns the list of executed names.

    Contract for each module: see this package's docstring / README.md.

    Called by build_svc_database.py AFTER
    apply_all_extended_patches(db, ..., _defer_gates=True) and BEFORE
    apply_svc_patches.run_registry_gates(db, tags, ...), so the monolith's gate
    battery validates the final assembled db (monolith + every module).

    Coherency gates:
      S4a registry-integrity - no duplicate entries; every entry runs exactly
          once, in manifest order (order hash logged + asserted).
      S4b module-collision WARN - after each module, log the records + tags it
          touched; if two modules write the SAME record (or tag), WARN naming
          both (later-wins is legal, but must be VISIBLE, never silent).

    With an EMPTY registry this does not touch db or db._modified at all, so the
    build is byte-identical to the pre-registry build (README S5 identity proof).
    """
    names = list(REGISTRY if registry is None else registry)
    order_hash = registry_order_hash(names)
    print("\n" + "=" * 70)
    print("=== patches-registry: %d module(s), order %s ==="
          % (len(names), order_hash[:12]))
    print("=" * 70)

    # S4a (pre): no duplicate manifest entries.
    if len(set(names)) != len(names):
        seen = set()
        dups = sorted({n for n in names if (n in seen) or seen.add(n)})
        raise SystemExit(
            "patches-registry integrity: REGISTRY has duplicate entries %s; "
            "each module must appear exactly once" % dups)

    if not names:
        print("  (registry empty - no content modules; identity-proof build)")
        print("=" * 70)
        return []

    # Instrument db._modified ONLY while modules run (see _TrackingModifiedSet).
    orig_modified = db._modified
    tracker = _TrackingModifiedSet(orig_modified)
    db._modified = tracker

    per_module_records = {}    # module_name -> set(record_name)
    per_module_tags = {}       # module_name -> set(tag_key)
    executed = []
    try:
        for idx, name in enumerate(names, 1):
            mod, module_name, apply_fn = _load_module(name)
            before_tags = dict(tags)
            mark = len(tracker._touch_log)
            print("\n--- [%d/%d] %s  (%s) ---" % (idx, len(names), name, module_name))
            tracker._active_module = name
            apply_fn(db, tags)
            tracker._active_module = None
            recs = {r for _m, r in tracker._touch_log[mark:]}
            tag_delta = {k for k in tags
                         if (k not in before_tags) or (tags[k] != before_tags[k])}
            per_module_records[name] = recs
            per_module_tags[name] = tag_delta
            print("    %s: modified %d record(s), %d tag(s)"
                  % (name, len(recs), len(tag_delta)))
            executed.append(name)
    finally:
        tracker._active_module = None
        # Restore a plain set with identical membership so all downstream
        # consumers (write_arz, the container-shape gate) see stock semantics.
        db._modified = set(tracker)

    # S4a (post): every entry ran exactly once, in manifest order.
    if executed != names:
        raise SystemExit(
            "patches-registry integrity: executed order %s != manifest order %s "
            "(a module must run exactly once, in order)" % (executed, names))
    if registry_order_hash(executed) != order_hash:
        raise SystemExit(
            "patches-registry integrity: post-run order hash mismatch "
            "(manifest mutated mid-run?)")

    # S4b: cross-module collisions (records AND tags).
    _warn_collisions("record(s)", per_module_records)
    _warn_collisions("tag(s)", per_module_tags)

    print("\n=== patches-registry: %d module(s) OK, order %s ==="
          % (len(executed), order_hash[:12]))
    print("=" * 70)
    return executed


def run_registry_verifies(db, tags, registry=None):
    """POST-FINALIZATION verify phase (step 4; see this package's EXECUTION ORDER).

    Call each REGISTRY module's OPTIONAL `verify(db, tags)` hook, in manifest
    order, AFTER apply_svc_patches.run_registry_gates has finalized the db (the
    Ground Smash de-filler, the wave29 placeholder-tag renames, the soul-naming
    standard, the MP-equation fix). A module puts here any roster/diversity/
    coherency check that MUST see the FINAL assembled db - a check that would
    trip on transient ordering artifacts if it ran at apply() time (step 2),
    mid-registry, before the finalization clears them.

    Fail-loud by construction: a module verify() raising SystemExit propagates
    and aborts the build (exactly like an apply()-time gate would). This is the
    ONLY thing that keeps the relocated gate live - a module that moves its gate
    out of apply() and into verify() is disabled UNLESS this phase runs, so
    build_svc_database.py MUST call it after run_registry_gates.

    Modules with no `verify` attribute (or a non-callable one) are skipped.
    Returns the list of module names whose verify() actually ran.
    """
    names = list(REGISTRY if registry is None else registry)
    print("\n" + "=" * 70)
    print("=== patches-registry: post-finalization verify() hooks ===")
    print("=" * 70)
    ran = []
    for name in names:
        mod, module_name, _apply_fn = _load_module(name)
        verify_fn = getattr(mod, 'verify', None)
        if not callable(verify_fn):
            continue
        print("  verify [%s] (%s) ..." % (name, module_name))
        verify_fn(db, tags)
        ran.append(name)
    if not ran:
        print("  (no registry module defines a verify() hook)")
    else:
        print("  verify hooks OK: %s" % ", ".join(ran))
    print("=" * 70)
    return ran


def selfcheck():
    """Cheap CI check (no DB build): validate that every REGISTRY module imports
    and satisfies the contract, and that the manifest has no duplicates. Prints
    the order hash. Returns 0 on success, raises SystemExit on any violation.

    Run it with: py tools/patches/_check_registry.py
    """
    names = list(REGISTRY)
    if len(set(names)) != len(names):
        raise SystemExit("patches-registry selfcheck FAIL: REGISTRY has "
                         "duplicate entries")
    for n in names:
        _load_module(n)   # fail-loud on any contract violation
    print("patches-registry selfcheck OK: %d module(s), order %s"
          % (len(names), registry_order_hash(names)))
    return 0
