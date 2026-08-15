r"""uber_hoard_generosity - R-251 (Will 2026-08-14): the uber/boss chests pay like ubers.

WILL, VERBATIM (2026-08-14), five reports in one play session - the full quotes and the
whole measurement live in `tools/svc_uber_hoards.py` and docs/WILL_RULINGS.md R-251:
  "are you kidding me. this is outrageous ... literally just dropped two items one thing
   of gold and incarnation of guan-yu's grace"        (Propontis, BL-W0814-11)
  "same problem with the chest guarded by tantalus"    (BL-W0814-13)
  "aphoryteus (spelled wrong) dread hoard is a terrible chest, it got nerfed somewhere
   along the way and needs to drop more items"         (Ephialtes, BL-W0814-5)
  "the obsidian hoard chests ... are still nerfed too much. if these share the same
   record as the chest - toxeus the murderer, devourer of blood hidden's chest we need
   to seperate those records"                          (BL-W0814-2)
  "the gift box in the secret places need to increase the number of items dropped by 3x"
                                                       (BL-W0814-7)

THIS MODULE IS DELIBERATELY SMALL, AND THAT IS THE POINT
---------------------------------------------------------
The shared cause is a WIRE, not a number, so it is fixed at the wire: the monolith's
finalization pass `_svc_wire_boss_hoard_chests` now points every uber hoard chest at its
own bespoke table instead of a base-game `boss_default_*`, and `svc_loot_volume.
_r251_exempt` takes the family out of R-240's trim so it keeps the volume the monolith
authors. Neither of those belongs in a registry module: one is the last writer of the
chests' `tables`, the other is a scope predicate the trim itself must consult.

What is left for a module is exactly ONE write and ONE gate:
  * apply()  - the Secret Present gift box, x3 item count, Will's literal number. It is
               the only DB write in R-251 that has no home elsewhere: `loottable_sp_0N`
               is an SV/DRX-original table no mod wave has ever owned.
  * verify() - the whole H1-H8 contract on the FINAL assembled db, so the wiring, the
               volume, the guaranteed row, the separation and the gift box are all
               proven together AFTER every other module and the monolith's finalization
               have had their say. An apply()-time check could not see the wiring at
               all: `_svc_wire_boss_hoard_chests` runs in step 3, after this step 2.

REGISTRY POSITION: after `loot_volume_trim` and `r247_bloodcave_rulings`, before the
no-op `visuals`. Load-bearing: apply() asserts the uber-hoard family came through the
trim UNTRIMMED, which is the live proof that the R-251 carve-out actually fired - and it
can only prove that once the trim has already run.

Negative test: py tools/patches/uber_hoard_generosity.py --negtest   (stub-db plants)
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import svc_loot_breadth as SLB          # noqa: E402
import svc_uber_hoards as SUH           # noqa: E402

MODULE_NAME = ("uber/boss chest generosity - every hoard chest opens its own table at "
               "uber volume, and the Secret Present box pays 3x (R-251)")

# The ONLY fields this module may move, on the ONLY records it may touch.
_ALLOWED_FIELDS = ('numSpawnMinEquation', 'numSpawnMaxEquation')


def _gv(db, rec, field, default=None):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        v = v[0] if v else None
    return default if v is None else v


def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    lk = SLB.Lookup(db)

    # ── PROOF THAT THE R-251 CARVE-OUT FIRED ─────────────────────────────────
    # `loot_volume_trim` has already run by now. If the carve-out were missing, the
    # uber-hoard family would be sitting at ~*0.22 and this module would be about to
    # gate a starved surface as if it were healthy. Fail loud instead: a silent pass
    # here is precisely how the family got nerfed twice without anyone noticing.
    trimmed = []
    for key, (real, _fam, _tier) in sorted(SUH.tables(db, lk).items()):
        mn = str(_gv(db, real, 'numSpawnMinEquation', ''))
        if mn != SUH.HOARD_MIN_EQ:
            trimmed.append('%s = %r' % (key.rsplit('\\', 1)[-1], mn))
    if trimmed:
        for t in trimmed[:12]:
            print("    - CARVE-OUT MISS: %s" % t)
        raise SystemExit(
            "[uber_hoard_generosity] %d uber/boss hoard table(s) no longer carry the "
            "authored volume %r by the time this module runs. Either `svc_loot_volume.`"
            "`_r251_exempt` stopped covering the family or a new writer appeared. R-240's "
            "trim was aimed at the polis-vault cage farm; sweeping the one-per-world uber "
            "hoards with it is the second half of what Will reported five times on "
            "2026-08-14." % (len(trimmed), SUH.HOARD_MIN_EQ))

    # ── BL-W0814-7: the Secret Present gift box, x3 ──────────────────────────
    # The chain, decoded from the shipped arz and the merged map: 5 world placements of
    # `proxyspawner_sp_chest` across DarkForestEnter / SecretForest2 / PillagedVillage
    # (which is why Will wrote "the secret places", plural) -> `poolspawner_sp` ->
    # `sp_chest_marker_deco` (tagSecretPresentSpawner) -> `proxy_sp_chest` ->
    # `pool_sp_0N` -> `sp_chest_0N` (tagSecretPresentBOX) -> `loottable_sp_0N`.
    # VOLUME ONLY. Composition is untouched: this is an SV/DRX-original table and its
    # members, weights and group chances are not this lane's to re-balance.
    before, changed = {}, []
    for path in SUH.GIFT_TABLES:
        real = lk.real(path)
        short = SLB._n(path).rsplit('\\', 1)[-1]
        if not real:
            raise SystemExit(
                "[uber_hoard_generosity] the Secret Present loot table %s is MISSING. "
                "BL-W0814-7 asks for 3x the items it drops; a missing table means the "
                "chain was renamed and this module would silently do nothing." % path)
        before[short] = {k.split('###')[0]: list(tf.values)
                         for k, tf in (db.get_fields(real) or {}).items()}
        mn = str(_gv(db, real, 'numSpawnMinEquation', ''))
        mx = str(_gv(db, real, 'numSpawnMaxEquation', ''))
        legal = ((SUH.GIFT_SV_MIN_EQ, SUH.GIFT_SV_MAX_EQ),      # a fresh build
                 (SUH.GIFT_MIN_EQ, SUH.GIFT_MAX_EQ))            # already applied
        if (mn, mx) not in legal:
            raise SystemExit(
                "[uber_hoard_generosity] %s carries numSpawn %r/%r, which is neither the "
                "SV original (%r/%r) nor this module's 3x (%r/%r). Another writer moved "
                "it; overwriting blind would hide that."
                % (short, mn, mx, SUH.GIFT_SV_MIN_EQ, SUH.GIFT_SV_MAX_EQ,
                   SUH.GIFT_MIN_EQ, SUH.GIFT_MAX_EQ))
        if (mn, mx) == (SUH.GIFT_MIN_EQ, SUH.GIFT_MAX_EQ):
            continue
        db.set_field(real, 'numSpawnMinEquation', SUH.GIFT_MIN_EQ)
        db.set_field(real, 'numSpawnMaxEquation', SUH.GIFT_MAX_EQ)
        db._modified.add(real)
        changed.append(short)

    # ── SCOPE PROOF: on the gift-box records, ONLY numSpawn moved ────────────
    illegal = []
    for path in SUH.GIFT_TABLES:
        real = lk.real(path)
        short = SLB._n(path).rsplit('\\', 1)[-1]
        now = {k.split('###')[0]: list(tf.values)
               for k, tf in (db.get_fields(real) or {}).items()}
        was = before.get(short, {})
        for field in sorted(set(was) | set(now)):
            if was.get(field, []) == now.get(field, []):
                continue
            if field not in _ALLOWED_FIELDS:
                illegal.append('%s.%s %r -> %r' % (short, field, was.get(field),
                                                   now.get(field)))
    if illegal:
        raise SystemExit(
            "[uber_hoard_generosity] SCOPE PROOF FAILED: %d field(s) outside "
            "numSpawnMin/MaxEquation moved on an SV-original Secret Present table: %s. "
            "Will asked for MORE ITEMS, not a different chest." % (len(illegal), illegal))

    print("    Secret Present box: %d table(s) taken to %s / %s (3x the SV original "
          "%s / %s); composition untouched."
          % (len(changed), SUH.GIFT_MIN_EQ, SUH.GIFT_MAX_EQ,
             SUH.GIFT_SV_MIN_EQ, SUH.GIFT_SV_MAX_EQ))
    print("    uber/boss hoard family: %d table(s) came through R-240 untrimmed at %s "
          "(the R-251 carve-out fired)." % (len(SUH.tables(db, lk)), SUH.HOARD_MIN_EQ))
    print("=== uber_hoard_generosity done ===\n")


def verify(db, tags):
    """The whole R-251 contract (H1-H8) on the FINAL db.

    Runs as a verify() and not at apply() time for a reason that is not stylistic: the
    WIRING half of R-251 lands in `run_registry_gates` (step 3), AFTER every registry
    apply() (step 2). A gate placed in apply() would be measuring the chests exactly one
    step before the pass that fixes them - which is a smaller version of the same
    mistake that let three breadth waves tune orphaned records."""
    lk = SLB.Lookup(db)
    report = {}
    problems = SUH.problems(db, lk, report=report)
    if problems:
        for p in problems[:20]:
            print("  GENEROSITY OFFENDER: %s" % p)
        raise SystemExit(
            "uber_hoard_generosity gate FAILED: %d finding(s). An uber/boss chest that "
            "does not open its own tuned table is what Will opened five times on "
            "2026-08-14 as 'two items, one thing of gold and incarnation of guan-yu's "
            "grace'." % len(problems))
    print("  " + SUH.pass_line(report))


# ─────────────────────────────────────────────────────────────────────────────
# NEGATIVE BATTERY (stub db). `py tools/patches/uber_hoard_generosity.py --negtest`
# A gate nobody has watched FAIL is a gate nobody should trust.
# ─────────────────────────────────────────────────────────────────────────────
def _negtest():
    sys.path.insert(0, str(_TOOLS / 'debug'))
    from negtest_uber_hoards import main as negmain
    return negmain([])


if __name__ == '__main__':
    if '--negtest' in sys.argv[1:]:
        sys.exit(_negtest())
    print(__doc__)
